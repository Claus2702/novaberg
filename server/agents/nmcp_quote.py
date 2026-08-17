"""Quotenabgleich — der laufende Zeuge der Anmeldung.

Der Dienst nennt bei der Anmeldung eine geschaetzte Quote, der Empfang zaehlt
die Zustellungen, der Abgleich meldet. Der tragende Grund ist nicht die Zahl,
sondern die Widerlegbarkeit: **Die Quote gibt jedem Aushang einen Leser, der
ihm widersprechen kann.**

Ohne sie ist eine Anmeldung eine Behauptung, die nicht falsch sein kann — und
genau daran verrotten Deklarationen unbemerkt: Es gibt keinen Lauf, der sie
prueft, und keinen Fehler, den sie ausloest.

Regelwerk: docs/novaberg-convention-nmcp.md §4.4 bis §4.9.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from agents.base import GRAPH_KANON, QUOTEN_KANON

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# Schwellen und Stichprobe
# ══════════════════════════════════════════════════════════════════════

#: Warnschwelle als Verhaeltnis gemessen/geschaetzt — eine
#: Viertel-Abweichung in beide Richtungen.
#:
#: Als Verhaeltnis und nicht als Prozentpunkt-Differenz: Eine Differenz
#: beurteilt dieselbe Verwechslung zweier Nachbarstufen je nach Richtung
#: verschieden (von 25 auf 50 sind +100 %, von 50 auf 25 sind -50 %).
WARNUNG_UNTEN: float = 0.75
WARNUNG_OBEN: float = 1.0 / 0.75          # 1.333…

#: Fehlerschwelle — eine halbe Abweichung in beide Richtungen.
FEHLER_UNTEN: float = 0.5
FEHLER_OBEN: float = 2.0

#: Mindest-Stichprobe, gerechnet und nicht gesetzt. Verlangt ist, dass das
#: 95-%-Intervall der Messung die Nachbarstufe ausschliesst. Im
#: unguenstigsten Fall (geschaetzt 50 %, groesste Streuung) braucht die
#: halbe Abweichung 16 Durchlaeufe, die Viertel-Abweichung 62. Beide Werte
#: liegen bewusst darueber: Je groesser die behauptete Abweichung, desto
#: weniger Durchlaeufe braucht es, um ihrer sicher zu sein.
MINDEST_FEHLER: int = 30
MINDEST_WARNUNG: int = 100

#: Halbe Breite eines Quoten-Bandes in Prozentpunkten. Jede Stufe der
#: Skala ist ein Band, kein Punkt.
BAND_HALB: float = 12.5

#: Laenge des rollenden Fensters, in Aeusserungen je Graph. Ueber
#: Durchlaeufe und nicht ueber einen Kalenderzeitraum: Ein Zeitfenster
#: gibt in einer stillen Woche einen Fehlalarm und in einer geschwaetzigen
#: ein Gefuehl von Sicherheit.
FENSTER: int = 500

#: Toleranz beim Vergleich der Verhaeltnisse. Die Schwellen sind
#: einschliessend gemeint, und 100/75 ist nicht bitgleich mit 1/0.75 — ohne
#: Toleranz entschiede die Gleitkommadarstellung ueber das Urteil am
#: Grenzfall.
TOLERANZ: float = 1e-9

#: Die drei Urteile des Abgleichs.
URTEIL_KANON: frozenset[str] = frozenset(
    {"keine_aussage", "stimmt", "warnung", "fehler"}
)


@dataclass
class Zaehlerstand:
    """Zustellungen und Bearbeitungen eines Dienstes in einem Graphen.

    Zwei Zaehler, weil zwischen Entscheidung und Ausfuehrung etwas
    verlorengehen kann. Die Quote vergleicht gegen `zugestellt`; die
    Differenz zu `bearbeitet` ist ein eigener Befund und hat mit dem
    Aushang nichts zu tun. Wer nur `bearbeitet` zaehlt, liest einen
    Pipeline-Defekt als Routing-Problem.
    """

    zugestellt: int = 0
    bearbeitet: int = 0
    abgelehnt: int = 0


@dataclass
class Abgleich:
    """Das Ergebnis eines Quotenabgleichs fuer einen Dienst in einem Graphen."""

    name: str
    graph: str
    geschaetzt: int
    gemessen: float           # Prozent
    stichprobe: int
    urteil: str               # URTEIL_KANON
    diagnose: str
    ablehnungsquote: float    # Anteil der Ablehnungen an den Bearbeitungen

    def zeile(self) -> str:
        """Einzeilige Fassung fuer das Protokoll."""
        return (
            f"{self.name}/{self.graph}: geschaetzt {self.geschaetzt} %, "
            f"gemessen {self.gemessen:.1f} % (n={self.stichprobe}) "
            f"→ {self.urteil} — {self.diagnose}"
        )


class QuotenRegister:
    """Fuehrt die Zaehler je Dienst und Graph und rechnet den Abgleich.

    Der Zaehler sitzt im Empfang, nicht in der Pruefstrecke: Er zaehlt,
    was tatsaechlich zugestellt wurde, und das weiss nur der Empfang.
    """

    def __init__(self) -> None:
        """Legt ein leeres Register an."""
        self._stand: dict[tuple[str, str], Zaehlerstand] = {}
        self._turns: dict[str, int] = {g: 0 for g in GRAPH_KANON}

    def turn_zaehlen(self, graph: str) -> None:
        """Zaehlt eine Aeusserung, die den Empfang erreicht hat.

        Vorbedingung: `graph` liegt in GRAPH_KANON — der Nenner ist je
        Graph getrennt, weil die Impulsrate des Hintergrunds keinem
        Fachdienst gehoert.

        Nachbedingung: Der Nenner des Graphen ist um eins hoeher.
        """
        # ── Eingabe-Validierung ──────────────────────────────────────
        if graph not in GRAPH_KANON:
            logger.error(
                "Quotenzaehler: unbekannter Graph '%s', Kanon ist %s — "
                "Turn nicht gezaehlt",
                graph, sorted(GRAPH_KANON),
            )
            return

        self._turns[graph] += 1

    def zustellung_zaehlen(self, name: str, graph: str) -> None:
        """Zaehlt eine Zustellung an einen Dienst.

        Vorbedingung: `graph` liegt in GRAPH_KANON, `name` ist nicht leer.
        Nachbedingung: `zugestellt` des Paares ist um eins hoeher.
        """
        # ── Eingabe-Validierung ──────────────────────────────────────
        if graph not in GRAPH_KANON:
            logger.error(
                "Quotenzaehler: Zustellung an '%s' mit unbekanntem Graph "
                "'%s' — nicht gezaehlt", name, graph,
            )
            return
        if not name:
            logger.error("Quotenzaehler: Zustellung ohne Dienstnamen — nicht gezaehlt")
            return

        self._stand.setdefault((name, graph), Zaehlerstand()).zugestellt += 1

    def bearbeitung_zaehlen(self, name: str, graph: str, status: str) -> None:
        """Zaehlt eine abgeschlossene Bearbeitung samt Ausgang.

        Vorbedingung: `graph` liegt in GRAPH_KANON.
        Nachbedingung: `bearbeitet` ist um eins hoeher; bei status
        "abgelehnt" zusaetzlich `abgelehnt`.
        """
        # ── Eingabe-Validierung ──────────────────────────────────────
        if graph not in GRAPH_KANON:
            logger.error(
                "Quotenzaehler: Bearbeitung von '%s' mit unbekanntem Graph "
                "'%s' — nicht gezaehlt", name, graph,
            )
            return

        stand = self._stand.setdefault((name, graph), Zaehlerstand())
        stand.bearbeitet += 1
        if status == "abgelehnt":
            stand.abgelehnt += 1

    def stand(self, name: str, graph: str) -> Zaehlerstand:
        """Gibt den Zaehlerstand eines Paares zurueck.

        Vorbedingung: keine. Nachbedingung: ein Zaehlerstand, notfalls ein
        leerer — ein unbekanntes Paar hat null Zustellungen und ist damit
        selbst eine Auskunft.
        """
        return self._stand.get((name, graph), Zaehlerstand())

    def turns(self, graph: str) -> int:
        """Gibt den Nenner eines Graphen zurueck.

        Vorbedingung: keine. Nachbedingung: nicht-negative Zahl.
        """
        return self._turns.get(graph, 0)

    def abgleichen(self, name: str, graph: str, geschaetzt: int) -> Abgleich:
        """Haelt die gemessene Quote gegen die geschaetzte.

        Vorbedingung: `geschaetzt` liegt in QUOTEN_KANON, `graph` in
        GRAPH_KANON.

        Nachbedingung: Ein Abgleich, dessen `urteil` in URTEIL_KANON
        liegt. Unterhalb der Mindest-Stichprobe lautet es
        "keine_aussage" — und das ist ein sichtbarer Zustand, nicht
        Schweigen. Ein Dienst, der monatelang darunter bleibt, hat damit
        selbst einen Befund.
        """
        # ── Eingabe-Validierung ──────────────────────────────────────
        if graph not in GRAPH_KANON:
            logger.error(
                "Quotenabgleich '%s': unbekannter Graph '%s'", name, graph
            )
            raise ValueError(f"Unbekannter Graph: {graph!r}")
        if geschaetzt not in QUOTEN_KANON:
            logger.error(
                "Quotenabgleich '%s': geschaetzt %r nicht im Kanon %s",
                name, geschaetzt, sorted(QUOTEN_KANON),
            )
            raise ValueError(f"Quote {geschaetzt!r} nicht im Kanon")

        # ── Verarbeitung ─────────────────────────────────────────────
        stand = self.stand(name, graph)
        n = self._turns.get(graph, 0)
        gemessen = (stand.zugestellt / n * 100.0) if n else 0.0
        ablehnungsquote = (
            stand.abgelehnt / stand.bearbeitet if stand.bearbeitet else 0.0
        )

        urteil, diagnose = self._urteilen(
            geschaetzt, gemessen, n, stand, ablehnungsquote
        )

        abgleich = Abgleich(
            name=name,
            graph=graph,
            geschaetzt=geschaetzt,
            gemessen=gemessen,
            stichprobe=n,
            urteil=urteil,
            diagnose=diagnose,
            ablehnungsquote=ablehnungsquote,
        )

        # ── Ausgabe-Verifikation ─────────────────────────────────────
        if abgleich.urteil not in URTEIL_KANON:
            logger.error(
                "Quotenabgleich '%s': Urteil '%s' nicht im Kanon",
                name, abgleich.urteil,
            )
            raise ValueError(f"Unbekanntes Urteil: {abgleich.urteil!r}")
        if not (0.0 <= abgleich.gemessen <= 100.0):
            logger.error(
                "Quotenabgleich '%s': gemessen %.2f %% ausserhalb 0–100 — "
                "%d Zustellungen bei %d Turns",
                name, abgleich.gemessen, stand.zugestellt, n,
            )
            raise ValueError(f"Gemessene Quote {abgleich.gemessen} ausserhalb 0–100")

        if urteil == "fehler":
            logger.error("Quotenabgleich: %s", abgleich.zeile())
        elif urteil == "warnung":
            logger.warning("Quotenabgleich: %s", abgleich.zeile())
        else:
            logger.info("Quotenabgleich: %s", abgleich.zeile())

        return abgleich

    @staticmethod
    def _urteilen(
        geschaetzt: int,
        gemessen: float,
        n: int,
        stand: Zaehlerstand,
        ablehnungsquote: float,
    ) -> tuple[str, str]:
        """Faellt das Urteil und benennt die Diagnose.

        Vorbedingung: `geschaetzt` liegt in QUOTEN_KANON, geprueft beim
        Aufrufer. Nachbedingung: Paar aus Urteil (URTEIL_KANON) und einem
        Diagnosesatz, der die Richtung benennt.
        """
        if n < MINDEST_FEHLER:
            return (
                "keine_aussage",
                f"Stichprobe {n} unter {MINDEST_FEHLER} — eine Quote ueber "
                f"so wenige Durchlaeufe ist keine Quote",
            )

        # Bei 0 % gelten absolute Schranken: ein Verhaeltnis zu null ist
        # nicht bildbar. Das Band endet bei einer halben Stufe.
        if geschaetzt == 0:
            if gemessen >= 2 * BAND_HALB:
                return (
                    "fehler",
                    f"als Ausnahme angemeldet, kommt aber in {gemessen:.1f} % "
                    f"der Faelle vor — der Aushang ist zu breit",
                )
            if gemessen >= BAND_HALB:
                if n < MINDEST_WARNUNG:
                    return (
                        "keine_aussage",
                        f"ueber dem Band, Stichprobe {n} aber unter "
                        f"{MINDEST_WARNUNG}",
                    )
                return (
                    "warnung",
                    f"als Ausnahme angemeldet, liegt mit {gemessen:.1f} % "
                    f"ueber dem Band",
                )
            return ("stimmt", QuotenRegister._null_diagnose(stand, ablehnungsquote))

        verhaeltnis = gemessen / geschaetzt

        # Die Grenzen sind EINSCHLIESSEND: "Abweichung um die Haelfte" heisst,
        # dass genau der Faktor 2 schon ein Fehler ist, nicht erst mehr. Ohne
        # den Toleranzwert faellt der Grenzfall der Gleitkommadarstellung zum
        # Opfer — 100/75 und 1/0.75 sind nicht bitgleich.
        if (verhaeltnis <= FEHLER_UNTEN + TOLERANZ
                or verhaeltnis >= FEHLER_OBEN - TOLERANZ):
            return ("fehler", QuotenRegister._richtung(
                verhaeltnis, gemessen, stand, ablehnungsquote
            ))

        if (verhaeltnis <= WARNUNG_UNTEN + TOLERANZ
                or verhaeltnis >= WARNUNG_OBEN - TOLERANZ):
            if n < MINDEST_WARNUNG:
                return (
                    "keine_aussage",
                    f"Viertel-Abweichung erkennbar, Stichprobe {n} aber unter "
                    f"{MINDEST_WARNUNG} — das Intervall schliesst die "
                    f"Nachbarstufe nicht aus",
                )
            return ("warnung", QuotenRegister._richtung(
                verhaeltnis, gemessen, stand, ablehnungsquote
            ))

        # Die Quote trifft. Damit wird die zweite Frage interessant: Wird
        # richtig zugestellt und trotzdem viel abgelehnt? Dann trifft der
        # Aushang und die Grenzangabe fehlt.
        if stand.bearbeitet >= MINDEST_FEHLER and ablehnungsquote >= 0.5:
            return (
                "warnung",
                f"Quote trifft, aber {ablehnungsquote * 100:.0f} % der "
                f"Auftraege werden abgelehnt — der Aushang trifft, die "
                f"Grenzangabe fehlt",
            )

        return ("stimmt", "Zustellquote im Band der Schaetzung")

    @staticmethod
    def _richtung(
        verhaeltnis: float,
        gemessen: float,
        stand: Zaehlerstand,
        ablehnungsquote: float,
    ) -> str:
        """Benennt, wo bei einer Abweichung zu suchen ist.

        Vorbedingung: keine. Nachbedingung: ein Diagnosesatz.
        """
        if stand.zugestellt == 0:
            return (
                "null Zustellungen bei positiver Schaetzung — der Dienst ist "
                "unerreichbar: keine Naht, kein ansprechender Aushang, oder "
                "die Anmeldung ist verrottet"
            )
        if verhaeltnis < 1.0:
            return (
                f"wird uebersehen (gemessen {gemessen:.1f} %) — Aushang zu eng, "
                f"ein Negativfall zu breit, oder ein Nachbardienst faengt ab. "
                f"Das ist die teure, unsichtbare Richtung"
            )
        return (
            f"wird behelligt (gemessen {gemessen:.1f} %) — Aushang zu breit "
            f"oder Negativfaelle fehlen"
        )

    @staticmethod
    def _null_diagnose(stand: Zaehlerstand, ablehnungsquote: float) -> str:
        """Diagnose fuer den konsistenten Null-Fall.

        Vorbedingung: keine. Nachbedingung: ein Diagnosesatz. Null
        geschaetzt und null gemessen ist konsistent **und trotzdem ein
        Befund**: unbrauchbarer Aushang oder unnoetiger Dienst sehen
        gleich aus, und beides muss man wissen.
        """
        if stand.zugestellt == 0:
            return (
                "als Ausnahme angemeldet und nie zugestellt — konsistent, "
                "aber unentschieden: unbrauchbarer Aushang oder unnoetiger "
                "Dienst sehen gleich aus"
            )
        if ablehnungsquote >= 0.5:
            return (
                f"selten zugestellt und {ablehnungsquote * 100:.0f} % davon "
                f"abgelehnt — die Grenzangabe fehlt"
            )
        return "als Ausnahme angemeldet, Zustellungen im Band"


#: Das Register des laufenden Prozesses. Ein Modul-Singleton, weil der
#: Empfang genau einer ist.
REGISTER = QuotenRegister()
