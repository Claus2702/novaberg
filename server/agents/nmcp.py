"""NMCP — Anmeldung, Handshake und Kompatibilitaetspruefung eines Fachdienstes.

Die Registrierung tut zwei Dinge: Sie stellt die **Naht** her und prueft die
**Kompatibilitaet**. Danach ist der Aufruf trivial — Auftrag hinein, Antwort
heraus.

Der Grund fuer diese Aufteilung ist nicht Bequemlichkeit, sondern Schutz: Zur
Laufzeit kann niemand mehr nein sagen, ohne das Gespraech anzuhalten. Ein
Aufrufer mitten im Turn hat nur die Wahl zwischen weitermachen und scheitern.
Wer eine Pruefung dorthin verlegt, hat sie faktisch abgeschafft.

Regelwerk: docs/novaberg-convention-nmcp.md §3 bis §5.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field

from agents.base import (
    GRAPH_KANON,
    QUOTEN_KANON,
    STATUS_KANON,
    ZUSTELLART_KANON,
    BaseAgent,
    Bedarf,
    Zusage,
)

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# Der Katalog der Zusagen — was der Empfang verbindlich anbieten kann
# ══════════════════════════════════════════════════════════════════════

#: Die Fundstellen, die der Empfang zusagen kann. Jede traegt ihre vier
#: Teile. Die Bedeutung ist der Teil, den kein Typpruefer ersetzt:
#: `timeline_id` kann den angelegten oder den gefundenen Eintrag tragen.
#:
#: Abgeleitet aus den Clipboard-Schluesseln in graph/state.py. Ein
#: Schluessel, der hier nicht steht, kann nicht zugesagt werden — auch
#: wenn er im Zustandstyp existiert. Das ist Absicht: Der Katalog ist die
#: Zusage, nicht der Zustandstyp.
ZUSAGEN: dict[str, Zusage] = {
    "timeline_id": Zusage(
        schluessel="timeline_id",
        typ="int | None",
        bedeutung=(
            "ID des im SELBEN Durchlauf angelegten Timeline-Eintrags. "
            "NICHT die ID eines gefundenen oder gesuchten Eintrags."
        ),
        lebensdauer="ein Durchlauf",
    ),
    "session_turn_kern": Zusage(
        schluessel="session_turn_kern",
        typ="str",
        bedeutung=(
            "Verdichteter Kern des laufenden Turns, erzeugt vom "
            "KZG-Schreibpfad. Leer, wenn keine Verdichtung lief."
        ),
        lebensdauer="ein Durchlauf",
        verbraucher_art="knoten",   # Dispatcher-Knoten, kein Agent
    ),
    "lzg_resonanz": Zusage(
        schluessel="lzg_resonanz",
        typ="dict | None",
        bedeutung=(
            "Assoziative Spreading-Resonanz aus dem Erinnerungsgraphen: "
            "anker_anzahl, sprung_tiefe, cluster, nova_sektor, erinnerungen."
        ),
        lebensdauer="ein Durchlauf",
        verbraucher_art="knoten",   # Reducer und Gespraechsvektor, keine Agenten
    ),
}


# ══════════════════════════════════════════════════════════════════════
# Befunde
# ══════════════════════════════════════════════════════════════════════

#: Die drei Grade der Ablehnung. Ein einziger Grad waere in beide
#: Richtungen falsch: Ein fehlender Negativfall macht einen Dienst nicht
#: arbeitsunfaehig, eine geratene Naht schon.
GRAD_KANON: frozenset[str] = frozenset(
    {"vollstaendig", "gemeldet", "eingeschraenkt", "verweigert"}
)

#: Rangfolge der Grade — hoeher schlaegt niedriger, wenn mehrere Befunde
#: zusammenkommen.
_GRAD_RANG: dict[str, int] = {
    "vollstaendig": 0,
    "gemeldet": 1,
    "eingeschraenkt": 2,
    "verweigert": 3,
}


@dataclass
class Mangel:
    """Ein einzelner Befund der Kompatibilitaetspruefung."""

    regel: str      # Kurzname der verletzten Regel, z.B. "naht"
    grad: str       # GRAD_KANON
    text: str       # Was fehlt, in einem Satz


@dataclass
class Anmeldebefund:
    """Das Ergebnis der Registrierung eines Dienstes.

    `eingebunden` ist die einzige Frage, die den Betrieb betrifft; die
    uebrigen Felder erklaeren sie. `zweifel_erlaubt` traegt die
    Einschraenkung aus dem fehlenden vierten Ausgang.
    """

    name: str
    grad: str                        # GRAD_KANON — der schwerste Mangel
    eingebunden: bool
    zweifel_erlaubt: bool            # Darf dieser Dienst Zweifelsfaelle bekommen?
    signatur: str                    # Naht-Signatur ueber alle Zusagen
    maengel: list[Mangel] = field(default_factory=list)

    def zeile(self) -> str:
        """Einzeilige Fassung fuer das Startprotokoll."""
        zustand = "eingebunden" if self.eingebunden else "NICHT eingebunden"
        zusatz = "" if self.zweifel_erlaubt else ", ohne Zweifelsfaelle"
        return (
            f"{self.name}: {self.grad} — {zustand}{zusatz}, "
            f"{len(self.maengel)} Mangel/Maengel, Naht {self.signatur[:12]}"
        )


# ══════════════════════════════════════════════════════════════════════
# Die Naht-Signatur
# ══════════════════════════════════════════════════════════════════════

def naht_signatur(bedarfe: list[Bedarf]) -> str:
    """Bildet die Signatur ueber die zugesagten Fundstellen eines Dienstes.

    Vorbedingung: `bedarfe` ist eine Liste von Bedarf-Objekten; unbekannte
    Schluessel sind zulaessig und gehen als solche ein.

    Nachbedingung: 64 Hex-Zeichen. Gleiche Bedarfe ergeben gleiche
    Signatur, unabhaengig von der Reihenfolge.

    Der Zweck ist nicht Sicherheit, sondern Verfall-Erkennung. Der
    haeufigste Verfall ist nicht Nachlaessigkeit des Dienstes, sondern
    eine berechtigte Aenderung auf der anderen Seite der Naht: Ein
    Schluessel behaelt seinen Namen und aendert seine Bedeutung. Das sieht
    kein Typpruefer und bemerkt kein Test.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not isinstance(bedarfe, list):
        logger.error(
            "Naht-Signatur: bedarfe ist %s statt list — Signatur nicht bildbar",
            type(bedarfe).__name__,
        )
        raise TypeError(f"bedarfe muss list sein, ist {type(bedarfe).__name__}")

    # ── Verarbeitung ─────────────────────────────────────────────────
    teile: list[str] = []
    for b in sorted(bedarfe, key=lambda x: x.schluessel):
        zusage = ZUSAGEN.get(b.schluessel)
        if zusage is None:
            teile.append(f"{b.schluessel}|OHNE-ZUSAGE")
            continue
        teile.append(
            f"{zusage.schluessel}|{zusage.typ}|{zusage.bedeutung}|{zusage.lebensdauer}"
        )

    signatur = hashlib.sha256("\n".join(teile).encode("utf-8")).hexdigest()

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if len(signatur) != 64:
        logger.error(
            "Naht-Signatur: Laenge %d statt 64 — Signatur unbrauchbar", len(signatur)
        )
        raise ValueError(f"Signatur hat Laenge {len(signatur)}, erwartet 64")

    return signatur


# ══════════════════════════════════════════════════════════════════════
# Die Kompatibilitaetspruefung
# ══════════════════════════════════════════════════════════════════════

def _naht_pruefen(agent: BaseAgent) -> list[Mangel]:
    """Prueft jeden Bedarf gegen den Katalog der Zusagen.

    Vorbedingung: keine. Nachbedingung: je unerfuellbarem Bedarf ein
    Mangel vom Grad "verweigert" — ein Dienst, dessen Bedarf niemand
    erfuellt, kann nicht arbeiten.
    """
    maengel: list[Mangel] = []
    for b in agent.bedarf:
        zusage = ZUSAGEN.get(b.schluessel)
        if zusage is None:
            maengel.append(Mangel(
                regel="naht",
                grad="verweigert",
                text=(
                    f"Bedarf '{b.schluessel}' hat keine Zusage — "
                    f"der Empfang kann ihn nicht anbieten"
                ),
            ))
            continue
        if zusage.typ != b.typ:
            maengel.append(Mangel(
                regel="naht",
                grad="verweigert",
                text=(
                    f"Bedarf '{b.schluessel}': Typ '{b.typ}' erwartet, "
                    f"zugesagt ist '{zusage.typ}'"
                ),
            ))
    return maengel


def _aushang_pruefen(agent: BaseAgent) -> list[Mangel]:
    """Prueft Aushang, Negativfaelle und Sprachbedingung.

    Vorbedingung: keine. Nachbedingung: Maengel vom Grad "gemeldet" —
    ein ungenauer Aushang macht einen Dienst nicht arbeitsunfaehig, und
    seine Ungenauigkeit faellt dem Quotenabgleich auf.
    """
    maengel: list[Mangel] = []

    if agent.zustellart not in ZUSTELLART_KANON:
        return [Mangel(
            regel="zustellart",
            grad="verweigert",
            text=f"unbekannte Zustellart '{agent.zustellart}'",
        )]

    # Ein Dienst, der nicht ueber den Empfang laeuft, wird nicht gewaehlt.
    # Von ihm einen Aushang zu verlangen ist eine Forderung ohne
    # Gegenstand — gemessen am 17.08.2026: 8 von 14 Diensten laufen ueber
    # Zeitplan oder Queue, und die Pruefung meldete allen einen Mangel.
    if agent.zustellart != "empfang":
        return maengel

    if not agent.aushang.strip():
        maengel.append(Mangel(
            regel="aushang",
            grad="gemeldet",
            text="kein Aushang deklariert — der Empfang hat kein Erkennungsmerkmal",
        ))

    if not agent.negativfaelle:
        maengel.append(Mangel(
            regel="negativfall",
            grad="gemeldet",
            text=(
                "keine Negativfaelle deklariert — Fehlrouting scheitert an "
                "oberflaechlicher Aehnlichkeit, nicht an fehlender Faehigkeit"
            ),
        ))

    # Sprachbedingung: der Aushang darf die Fachsprache des Dienstes nicht
    # benutzen. Heuristisch geprueft gegen die eigenen Faehigkeitsnamen —
    # das sind per Definition Begriffe des Anbieters.
    text = agent.aushang.lower()
    treffer = [f for f in agent.faehigkeiten if f.lower() in text]
    if treffer:
        maengel.append(Mangel(
            regel="sprache",
            grad="gemeldet",
            text=(
                f"Aushang nennt eigene Fachbegriffe {treffer} — der Empfang "
                f"kennt die Fachsprache keiner Abteilung"
            ),
        ))

    maengel.extend(_ausschluss_pruefen(agent))
    return maengel


def _ausschluss_pruefen(agent: BaseAgent) -> list[Mangel]:
    """Prueft, ob ein Negativfall einen anderen Dienst benennt.

    Ein Zettel darf keinen anderen Dienst ausschliessen. Zwei Gruende, und
    der zweite ist der schwerere: Ein Plugin kann seinen Nachbarn nicht
    kennen — und selbst mit diesem Wissen waere das Ausschlussrecht Gift,
    weil es im Fehlerfall den **korrekten** Dienst mit ausschloesse. Aus
    dem billigen sichtbaren Fehler wuerde der teure unsichtbare.

    Vorbedingung: keine. Nachbedingung: je Treffer ein Mangel vom Grad
    "verweigert".

    **Die Pruefung ist heuristisch, und ihre Grenze ist gemessen.** Am
    17.08.2026 meldete eine Teilzeichenfolgen-Suche `charakter_identitaet`
    als Verstoss, weil dessen Negativfall "kein dauerhafter Charakter"
    den Namen des Dienstes `charakter` enthaelt. **Agentennamen sind
    Domaenenwoerter** — deshalb wird auf Wortgrenzen geprueft und die
    eigene Namensfamilie ausgenommen. Was danach bleibt, findet nur der
    Review.
    """
    from agents import AgentRegistry  # lokal: Zyklus Registry <-> nmcp

    eigen = agent.name.lower()
    fremde = {
        n.lower() for n in AgentRegistry.alle()
        if n.lower() != eigen
        # Namensfamilie ausnehmen: 'charakter' und 'charakter_identitaet'
        # sind dieselbe Domaene, kein fremder Dienst.
        and n.lower() not in eigen and eigen not in n.lower()
    }

    maengel: list[Mangel] = []
    for nf in agent.negativfaelle:
        worte = {
            w.strip(".,:;!?()\"'—").lower() for w in nf.replace("_", " ").split()
        }
        genannt = sorted(
            n for n in fremde
            if set(n.split("_")) <= worte or n in worte
        )
        if genannt:
            maengel.append(Mangel(
                regel="ausschluss",
                grad="verweigert",
                text=(
                    f"Negativfall nennt fremde Dienste {genannt} — ein Zettel "
                    f"darf keinen anderen Dienst ausschliessen: Im Fehlerfall "
                    f"schloesse er den korrekten Dienst mit aus"
                ),
            ))
    return maengel


def _quote_pruefen(agent: BaseAgent) -> list[Mangel]:
    """Prueft die Quote gegen Kanon und Geltungsbereich.

    Vorbedingung: keine. Nachbedingung: Maengel vom Grad "gemeldet",
    ausser bei einem Wert ausserhalb des Kanons — der ist ein Defekt der
    Anmeldung selbst und damit "verweigert".
    """
    maengel: list[Mangel] = []
    quote = agent.quote

    # Ohne Zustellentscheidung gibt es nichts abzugleichen.
    if agent.zustellart != "empfang":
        return maengel

    if not quote:
        maengel.append(Mangel(
            regel="quote",
            grad="gemeldet",
            text=(
                "keine Quote deklariert — der Aushang ist damit eine "
                "Behauptung, die nicht falsch sein kann"
            ),
        ))
        return maengel

    for graph, wert in quote.items():
        if graph not in GRAPH_KANON:
            maengel.append(Mangel(
                regel="quote",
                grad="verweigert",
                text=f"Quote fuer unbekannten Graph '{graph}'",
            ))
        if wert not in QUOTEN_KANON:
            maengel.append(Mangel(
                regel="quote",
                grad="verweigert",
                text=(
                    f"Quote {wert} fuer '{graph}' nicht im Kanon "
                    f"{sorted(QUOTEN_KANON)} — jede Stufe ist ein Band, "
                    f"kein Punkt"
                ),
            ))

    # Eine Quote fuer einen Graphen, in dem der Dienst nicht laufen darf,
    # ist eine Angabe ohne Gegenstand.
    fremd = set(quote) - set(agent.graph_eignung)
    if fremd:
        maengel.append(Mangel(
            regel="quote",
            grad="gemeldet",
            text=(
                f"Quote fuer {sorted(fremd)} deklariert, aber graph_eignung "
                f"ist {agent.graph_eignung}"
            ),
        ))

    fehlend = set(agent.graph_eignung) - set(quote)
    if fehlend:
        maengel.append(Mangel(
            regel="quote",
            grad="gemeldet",
            text=f"keine Quote fuer {sorted(fehlend)}, obwohl dort zugelassen",
        ))

    return maengel


def _ausgaenge_pruefen(agent: BaseAgent) -> list[Mangel]:
    """Prueft die bedienten Ausgaenge, insbesondere den vierten.

    Vorbedingung: keine. Nachbedingung: fehlt "abgelehnt", ein Mangel vom
    Grad "eingeschraenkt" — der Dienst wird eingebunden, bekommt aber
    keine Zweifelsfaelle. Die Zustellung im Zweifel setzt voraus, dass
    die Fachabteilung ablehnen kann; ein Dienst ohne begruendete
    Ablehnung fuehrt aus, was ihn erreicht.
    """
    maengel: list[Mangel] = []

    unbekannt = set(agent.ausgaenge) - STATUS_KANON
    if unbekannt:
        maengel.append(Mangel(
            regel="ausgang",
            grad="verweigert",
            text=f"unbekannte Ausgaenge {sorted(unbekannt)}",
        ))

    if "abgeschlossen" not in agent.ausgaenge:
        maengel.append(Mangel(
            regel="ausgang",
            grad="verweigert",
            text="bedient 'abgeschlossen' nicht — kein Erfolgsfall",
        ))

    if "abgelehnt" not in agent.ausgaenge:
        maengel.append(Mangel(
            regel="ausgang",
            grad="eingeschraenkt",
            text=(
                "bedient den vierten Ausgang 'abgelehnt' nicht — bekommt "
                "keine Zweifelsfaelle, weil er sie ausfuehren statt "
                "beurteilen wuerde"
            ),
        ))

    return maengel


def anmelden(agent: BaseAgent) -> Anmeldebefund:
    """Fuehrt den Handshake fuer einen Dienst durch und faellt das Urteil.

    Vorbedingung: `agent` ist eine BaseAgent-Instanz mit gueltigem Namen.

    Nachbedingung: Ein Anmeldebefund, dessen `grad` der schwerste
    gefundene Mangel ist. `eingebunden` ist genau dann falsch, wenn der
    Grad "verweigert" lautet. Die Ablehnung trifft **den Dienst und nicht
    das System** — ein fehlerhaft angemeldetes Plugin darf den Start
    nicht verhindern.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not isinstance(agent, BaseAgent):
        logger.error(
            "Anmeldung: Objekt ist %s statt BaseAgent — nicht anmeldbar",
            type(agent).__name__,
        )
        raise TypeError(f"agent muss BaseAgent sein, ist {type(agent).__name__}")

    if not agent.name or not agent.name.strip():
        logger.error("Anmeldung: Dienst ohne Namen — nicht anmeldbar")
        raise ValueError("Dienst ohne Namen")

    # ── Verarbeitung ─────────────────────────────────────────────────
    maengel: list[Mangel] = []
    maengel.extend(_naht_pruefen(agent))
    maengel.extend(_aushang_pruefen(agent))
    maengel.extend(_quote_pruefen(agent))
    maengel.extend(_ausgaenge_pruefen(agent))

    grad = "vollstaendig"
    for m in maengel:
        if _GRAD_RANG[m.grad] > _GRAD_RANG[grad]:
            grad = m.grad

    befund = Anmeldebefund(
        name=agent.name,
        grad=grad,
        eingebunden=(grad != "verweigert"),
        zweifel_erlaubt=("abgelehnt" in agent.ausgaenge and grad != "verweigert"),
        signatur=naht_signatur(agent.bedarf),
        maengel=maengel,
    )

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if befund.grad not in GRAD_KANON:
        logger.error(
            "Anmeldung '%s': Grad '%s' nicht im Kanon — Befund unbrauchbar",
            agent.name, befund.grad,
        )
        raise ValueError(f"Unbekannter Grad: {befund.grad!r}")

    if not befund.eingebunden:
        logger.error(
            "Dienst '%s' NICHT eingebunden — %s",
            agent.name,
            "; ".join(m.text for m in maengel if m.grad == "verweigert"),
        )
    elif not befund.zweifel_erlaubt:
        logger.warning(
            "Dienst '%s' eingebunden, aber ohne Zweifelsfaelle — vierter "
            "Ausgang fehlt", agent.name,
        )
    elif maengel:
        logger.info(
            "Dienst '%s' eingebunden mit %d Meldung(en): %s",
            agent.name, len(maengel), "; ".join(m.regel for m in maengel),
        )

    return befund


# ══════════════════════════════════════════════════════════════════════
# Das Gesamtbild — nur bei der Registrierung moeglich
# ══════════════════════════════════════════════════════════════════════

def gesamtbild_pruefen(agenten: dict[str, BaseAgent]) -> list[Mangel]:
    """Prueft die Menge aller Dienste — vier Fragen, die nur hier gehen.

    Zur Laufzeit sieht niemand alle Dienste zugleich. Bei der
    Registrierung sieht der Empfang sie alle, und das ist der einzige
    Moment, in dem Fragen ueber die Menge beantwortbar sind.

    Vorbedingung: `agenten` ist die vollstaendige Registry.

    Nachbedingung: ausschliesslich Maengel vom Grad "gemeldet". **Das
    Ergebnis geht an den Autor der Zettel, niemals in die
    Zustellentscheidung** — eine hier berechnete Rangfolge waere zur
    Laufzeit dieselbe zentrale Zuordnungstabelle, gegen die die ganze
    Bauart gerichtet ist.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not isinstance(agenten, dict):
        logger.error(
            "Gesamtbild: agenten ist %s statt dict", type(agenten).__name__
        )
        raise TypeError("agenten muss dict sein")

    maengel: list[Mangel] = []

    # 1) Quotensumme je Graph. Ueber 100 % ist der Normalfall — mehrere
    #    Dienste duerfen dieselbe Aeusserung beanspruchen. Auffaellig ist
    #    ein weit zu niedriger Wert (viele Aeusserungen erreichen
    #    niemanden) oder ein Vielfaches.
    for graph in sorted(GRAPH_KANON):
        empfang = [
            a for a in agenten.values()
            if graph in a.graph_eignung and a.zustellart == "empfang"
        ]
        summe = sum(a.quote.get(graph, 0) for a in empfang)
        beteiligt = len(empfang)
        if beteiligt == 0:
            continue
        if summe < 50:
            maengel.append(Mangel(
                regel="quotensumme",
                grad="gemeldet",
                text=(
                    f"Graph '{graph}': Quotensumme {summe} % ueber {beteiligt} "
                    f"Dienste — ein grosser Teil der Aeusserungen erreicht "
                    f"keinen Dienst"
                ),
            ))
        elif summe > 300:
            maengel.append(Mangel(
                regel="quotensumme",
                grad="gemeldet",
                text=(
                    f"Graph '{graph}': Quotensumme {summe} % — mehrfache "
                    f"Beanspruchung ist zulaessig, ein Vielfaches ist "
                    f"erklaerungsbeduerftig"
                ),
            ))

    # 2) Ueberlappende Aushaenge ohne Negativfall. Paarweiser Vergleich
    #    ueber die Merkmalswoerter — heuristisch, und das Ergebnis ist
    #    eine Meldung an den Menschen, der beide Zettel pflegt.
    namen = sorted(agenten)
    for i, a_name in enumerate(namen):
        for b_name in namen[i + 1:]:
            a, b = agenten[a_name], agenten[b_name]
            if not (a.aushang.strip() and b.aushang.strip()):
                continue
            gemeinsam = _merkmale(a.aushang) & _merkmale(b.aushang)
            if len(gemeinsam) < 3:
                continue
            if a.negativfaelle or b.negativfaelle:
                continue
            maengel.append(Mangel(
                regel="ueberlappung",
                grad="gemeldet",
                text=(
                    f"'{a_name}' und '{b_name}' teilen {len(gemeinsam)} "
                    f"Merkmalswoerter {sorted(gemeinsam)[:4]}, und keiner der "
                    f"beiden nennt einen Negativfall"
                ),
            ))

    # 3) Gleicher Bedarf, verschiedene Bedeutung.
    bedeutungen: dict[str, dict[str, list[str]]] = {}
    for name, a in agenten.items():
        for b in a.bedarf:
            bedeutungen.setdefault(b.schluessel, {}).setdefault(
                b.bedeutung, []
            ).append(name)
    for schluessel, gruppen in bedeutungen.items():
        if len(gruppen) > 1:
            maengel.append(Mangel(
                regel="bedeutung",
                grad="gemeldet",
                text=(
                    f"Bedarf '{schluessel}' wird von {sum(len(v) for v in gruppen.values())} "
                    f"Diensten in {len(gruppen)} verschiedenen Bedeutungen "
                    f"verlangt: {[v for v in gruppen.values()]}"
                ),
            ))

    # 4) Kanal ohne Gegenstueck: eine Zusage, die niemand anmeldet.
    angemeldet = {b.schluessel for a in agenten.values() for b in a.bedarf}
    # Nur agentenseitige Zusagen erwarten einen Agenten-Bedarf. Die
    # Clipboard-Regel gilt zwischen Stufen; ein Kanal Knoten-zu-Knoten hat
    # zu Recht keinen Anmelder, und ihn zu melden waere ein Fehlalarm.
    agentenseitig = {
        s for s, z in ZUSAGEN.items() if z.verbraucher_art == "agent"
    }
    tot = agentenseitig - angemeldet
    for schluessel in sorted(tot):
        maengel.append(Mangel(
            regel="toter_kanal",
            grad="gemeldet",
            text=(
                f"Zusage '{schluessel}' wird von keinem Dienst angemeldet — "
                f"ein Kanal ohne Verbraucher"
            ),
        ))

    logger.info(
        "Gesamtbild geprueft: %d Dienste, %d Meldung(en) an den Autor",
        len(agenten), len(maengel),
    )
    return maengel


def _merkmale(aushang: str) -> set[str]:
    """Zerlegt einen Aushang in bedeutungstragende Woerter.

    Vorbedingung: `aushang` ist Text. Nachbedingung: Menge kleingeschriebener
    Woerter ab vier Zeichen, ohne Funktionswoerter.
    """
    stopp = {
        "eine", "einen", "einem", "eines", "oder", "sind", "wird", "wenn",
        "nicht", "dass", "sich", "auch", "aber", "sondern", "diese", "dieser",
        "dieses", "welche", "welcher", "haben", "wurde", "ueber", "unter",
        "durch", "seine", "ihrer", "damit", "beim", "vom", "zum", "zur",
        "entscheidend", "satzform", "aeusserung", "aeusserungen", "prompt",
    }
    worte = {
        w.strip(".,:;!?()\"'").lower()
        for w in aushang.split()
    }
    return {w for w in worte if len(w) >= 4 and w not in stopp}


# ══════════════════════════════════════════════════════════════════════
# Das schwarze Brett — die Aushaenge, die der Empfang liest
# ══════════════════════════════════════════════════════════════════════

#: Ruecknahme der Zweifelsregel fuer einen Dienst ohne vierten Ausgang.
#: Wortlaut am Zettel und nicht als Rangfolge: Er sagt etwas ueber DIESEN
#: Dienst, nicht ueber sein Verhaeltnis zu einem anderen.
_OHNE_ZWEIFEL: str = (
    "BEI UNSICHERHEIT NICHT ZUSTELLEN: Dieser Dienst kann einen Auftrag "
    "nicht begruendet ablehnen. Stelle ihm nur zu, wenn der Aushang klar "
    "passt."
)


def aushaenge_sammeln(graph_typ: str) -> str:
    """Sammelt die Aushaenge aller Dienste am Empfang zu einem Brett.

    Vorbedingung: `graph_typ` liegt in GRAPH_KANON.

    Nachbedingung: Text mit einem Abschnitt je Dienst, oder leer, wenn kein
    Dienst fuer diesen Graphen einen Aushang hat. Jeder Abschnitt traegt den
    Aushang und — falls deklariert — die Negativfaelle als eigenen Block.

    **Der Aushang kommt vom Dienst, wo es einen gibt, und sonst vom
    Manager.** Beide Flaechen tragen im Bestand denselben Text: Der Dienst
    erbt ihn vom gleichnamigen Manager. Ihn zweimal auszugeben hiesse, dem
    Modell dieselbe Regel doppelt vorzulegen — und zwei Regeln, die
    dasselbe sagen, heben sich in der Wirkung auf. Deshalb gewinnt der
    Dienst, und der Manager kommt nur zum Zug, wenn kein Dienst seinen
    Namen traegt (im Bestand ist das `fakten`).

    **Die Negativfaelle sind der Zugewinn dieses Aggregators.** Auf der
    Manager-Flaeche stehen sie als Prosa mitten im Aushang und nur bei
    einigen; hier stehen sie bei jedem Dienst an derselben Stelle in
    derselben Form. Fehlrouting scheitert an oberflaechlicher Aehnlichkeit,
    nicht an fehlender Faehigkeit — und dagegen wirkt nur der Negativfall.

    Was NICHT hineinkommt: eine Rangfolge, ein Vorrang, ein Hinweis auf
    Ueberlappungen. Der Empfang beurteilt jeden Zettel fuer sich; ein
    Verhaeltnis zwischen zwei Zetteln waere die zentrale Zuordnungstabelle,
    gegen die die ganze Bauart gerichtet ist.
    """
    from plugins import get_registry

    from agents import AgentRegistry  # lokal: Zyklus Registry <-> nmcp

    # ── Eingabe-Validierung ──────────────────────────────────────────
    if graph_typ not in GRAPH_KANON:
        logger.error(
            "Aushaenge: unbekannter Graph '%s', Kanon ist %s — leeres Brett",
            graph_typ, sorted(GRAPH_KANON),
        )
        return ""

    # ── Verarbeitung ─────────────────────────────────────────────────
    agenten = AgentRegistry.alle()
    manager = get_registry()

    bloecke: list[str] = []

    for name, agent in sorted(agenten.items()):
        if agent.zustellart != "empfang":
            continue
        if graph_typ not in agent.graph_eignung:
            continue
        aushang = agent.aushang.strip()
        if not aushang:
            logger.warning(
                "Aushaenge: Dienst '%s' steht am Empfang und hat keinen "
                "Aushang — der Empfang hat kein Erkennungsmerkmal fuer ihn",
                name,
            )
            continue
        teile = [aushang]
        if agent.negativfaelle:
            teile.append(
                "NICHT zustellen bei:\n"
                + "\n".join(f"  - {f}" for f in agent.negativfaelle)
            )
        # Die Zustellung im Zweifel setzt den vierten Ausgang voraus: Sie ist
        # nur billig, weil die Fachabteilung ablehnen KANN. Ein Dienst ohne
        # begruendete Ablehnung fuehrt aus, was ihn erreicht — er beurteilt
        # es nicht. Deshalb wird die Zweifelsregel fuer ihn ausdruecklich
        # zurueckgenommen, am Zettel und nicht in einer Rangfolge.
        if "abgelehnt" not in agent.ausgaenge:
            teile.append(_OHNE_ZWEIFEL)
        bloecke.append("\n\n".join(teile))

    # Manager ohne gleichnamigen Dienst: ihr Aushang wuerde sonst entfallen.
    for ziel, m in sorted(manager.items()):
        if ziel in agenten:
            continue
        aushang = (m.router_prompt or "").strip()
        if aushang:
            # Ein Manager ohne Dienst hat keine vier Ausgaenge und kann
            # nicht begruendet ablehnen. Fuer ihn gilt die Zweifelsregel
            # deshalb nicht.
            bloecke.append(f"{aushang}\n\n{_OHNE_ZWEIFEL}")

    brett = "\n\n".join(bloecke)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if not brett:
        logger.error(
            "Aushaenge: leeres Brett fuer Graph '%s' — %d Dienste und %d "
            "Manager geprueft, keiner traegt einen Aushang. Der Empfang "
            "kann damit keinen Dienst waehlen",
            graph_typ, len(agenten), len(manager),
        )
        return ""

    logger.debug(
        "Aushaenge: %d Zettel fuer Graph '%s', %d Zeichen",
        len(bloecke), graph_typ, len(brett),
    )
    return brett
