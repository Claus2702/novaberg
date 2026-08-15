"""Die Riegelkette der Zustellung — wer entschieden hat, und womit.

Ein eigener Gedanke geht nicht hinaus, weil er gut ist. Sieben Riegel stehen
davor, und ihre Reihenfolge ist die Ordnung der Fragen, nicht Bequemlichkeit
(`novaberg-eigenzeit_k.md` §2.5):

    1 WOLLEN     Zuwendung >= Schwelle?              nein -> Ende, keine Suche
    2 FREQUENZ   Initiative: ist sie dran?           nein -> Ende
    3 RUHE       Cooldown aktiv? Burst erschoepft?   ja   -> Ende
    4 BEZUG      Gibt es eine Aeusserung des Menschen?
    5 THEMA      bester Eintrag >= Schwelle
    6 MODUS      Modus-Kompatibilitaet
    7 EMOTION    bei Stress nichts, bei negativem nur Zuwendung

**Der Rad-Riegel steht vor dem Themen-Riegel.** Will sie nicht zugehen,
braucht es keine Aehnlichkeitssuche ueber den Stapel — erst die Person, dann
der Gegenstand. Die Riegel 1 bis 4 sind Zahlenvergleiche auf Werten, die
ohnehin vorliegen; erst bei 5 entsteht ein Embedding.

**„Geblockt" ist keine Auskunft.** Wo mehrere Riegel blocken koennen, ist der
**Grund** selbst eine Messgroesse: An einem stillen Tag ist sonst nicht zu
unterscheiden, ob niemand zugehen wollte oder ob nichts gepasst hat — zwei
Befunde mit verschiedenen Konsequenzen. Daraus die beiden Regeln dieser Datei,
und die zweite ist die, die man vergisst:

  * **Der erste Blocker entscheidet, aber die billigen Riegel werden trotzdem
    alle gerechnet.** Wird nur der erste vermerkt, bekommen die spaeteren nie
    Daten — Riegel 1 verdeckt Riegel 2, und ihre Schwellen sind nicht mehr
    kalibrierbar. Sichtbar wird das nie, weil ein Riegel ohne Daten wie ein
    Riegel ohne Faelle aussieht.
  * **Ein nicht gerechneter Riegel wird als nicht gerechnet vermerkt.** Sein
    fehlender Wert darf nicht wie ein Durchlass aussehen — der Bauplan, der im
    Defektregister dieses Projekts sechsmal steht.

**Und blockiert ist nicht gleich blockiert.** Ein Riegel, der seine
Eingangsgroesse nicht lesen kann, hat nichts gemessen; er verweigert trotzdem
(`unbekannt ist nicht dasselbe wie in Ordnung`), aber sein Grund gehoert
getrennt gezaehlt. Sonst sieht ein kaputter Speicher aus wie eine distanzierte
Figur.
"""

import logging
from dataclasses import dataclass

from config import (
    GV_INITIATIVE_SCHWELLE,
    ZUWENDUNG_SCHWELLE,
    ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN,
)
from ei.initiative import initiative_bit
from memory.haltung import Haltungsstand

logger = logging.getLogger("ki_server.pixie.riegel")

# Der Kanon der Riegel, in der Reihenfolge, in der geprueft wird. Als
# geschlossene Menge, damit ein Name gegen sie **pruefbar** ist statt nur
# benutzbar: Ein unbekannter Riegelname waere sonst von einem fehlenden nicht
# zu unterscheiden.
RIEGEL_KANON: tuple[str, ...] = (
    "wollen", "frequenz", "ruhe", "bezug", "thema", "modus", "emotion",
)

# Die Gruende, mit denen Riegel 1 blocken kann — ebenfalls geschlossen.
# **Vier davon heissen „unbekannt", einer heisst „nein".** Nur der letzte ist
# eine Aussage ueber die Figur; die anderen sind Aussagen ueber den Speicher,
# und sie zusammenzuwerfen macht aus einem Ausfall eine Eigenschaft.
GRUND_KEIN_STAND:      str = "kein_stand"
GRUND_OHNE_RECHNUNG:   str = "stand_ohne_rechnung"
GRUND_ZU_ALT:          str = "stand_zu_alt"
GRUND_NAEHE_FEHLT:     str = "naehe_fehlt"
GRUND_UNTER_SCHWELLE:  str = "zuwendung_unter_schwelle"

GRUENDE_UNBEKANNT: frozenset[str] = frozenset({
    GRUND_KEIN_STAND, GRUND_OHNE_RECHNUNG, GRUND_ZU_ALT, GRUND_NAEHE_FEHLT,
})

# Die Gruende von Riegel 2. Dieselbe Trennung, derselbe Grund: **einer heisst
# „nein", die uebrigen heissen „unbekannt".**
#
# Nur `GRUND_MENSCH_FUEHRT` ist eine Aussage ueber den Moment — der Mensch
# treibt gerade, also ist sie nicht dran. Die anderen sagen, dass niemand es
# weiss.
GRUND_MENSCH_FUEHRT:   str = "mensch_fuehrt"
GRUND_INITIATIVE_FEHLT: str = "initiative_fehlt"

GRUENDE_UNBEKANNT_FREQUENZ: frozenset[str] = frozenset({
    GRUND_KEIN_STAND, GRUND_ZU_ALT, GRUND_INITIATIVE_FEHLT,
})

# **Die Riegel, ohne die ein Urteil keines ist.** Eine Kette ohne sie hat
# nichts geprueft — und „nichts geprueft" darf nicht wie „nichts einzuwenden"
# aussehen. Ohne diese Menge waere eine **leere** Kette durchlaessig: Faellt
# eine Aufnahme aus (ein Name ausserhalb des Kanons wird gemeldet und
# verworfen), ginge jeder Gedanke hinaus, und kein Zeuge wuerde rot.
#
# **`frequenz` steht hier seit dem 15.08.2026, und zwar als Folge davon, dass
# die stuendliche Decke gefallen ist.** Solange sie stand, war ein nicht
# gerechneter Riegel 2 eine Luecke in den Daten; jetzt ist er das Fehlen der
# einzigen Begrenzung, die den Zeitpunkt noch beurteilt.
RIEGEL_PFLICHT: frozenset[str] = frozenset({"wollen", "frequenz"})


@dataclass(frozen=True)
class Riegel:
    """Das Ergebnis eines einzelnen Riegels.

    Attributes:
        name:         einer aus `RIEGEL_KANON`.
        gerechnet:    ob er ueberhaupt gelaufen ist.
        durchlaessig: ``True`` = durch, ``False`` = geblockt, ``None`` = nicht
            gerechnet. **Drei Zustaende, nicht zwei** — ein nicht gerechneter
            Riegel darf nicht wie ein Durchlass aussehen.
        wert:         die Zahl, an der er entschieden hat; ``None``, wenn er
            keine hatte.
        grund:        warum er geblockt hat; leer, wenn er durchliess.
    """

    name:         str
    gerechnet:    bool
    durchlaessig: bool | None
    wert:         float | None
    grund:        str


class Riegelkette:
    """Sammelt die Ergebnisse eines Zustellversuchs.

    Kein Dict im Aufrufer: Die Kette prueft ihre eigenen Namen gegen den Kanon
    und kennt die Reihenfolge, in der „der erste Blocker" bestimmt wird. Beides
    im Aufrufer haette bedeutet, es an jeder Stelle zu wiederholen.
    """

    def __init__(self) -> None:
        """Eine leere Kette."""
        self._riegel: dict[str, Riegel] = {}

    def _eintragen(self, riegel: Riegel) -> None:
        """Nimmt ein Ergebnis auf, wenn sein Name im Kanon steht.

        Vorbedingung: keine.
        Nachbedingung: Der Riegel steht in der Kette, oder der unbekannte Name
            ist gemeldet und **nichts** eingetragen — ein stillschweigend
            aufgenommener Fremdname erschiene in der Auswertung als Riegel.
        """
        # ── Eingabe-Validierung ─────────────────────
        if riegel.name not in RIEGEL_KANON:
            logger.error(
                "Riegelkette: %r steht nicht im Kanon %s — nicht eingetragen",
                riegel.name, list(RIEGEL_KANON),
            )
            return

        # ── Ausgabe ─────────────────────────────────
        self._riegel[riegel.name] = riegel

    def aufnehmen(self, riegel: Riegel) -> None:
        """Nimmt ein fertig gerechnetes Ergebnis auf.

        Fuer Riegel, die eine eigene Rechenfunktion haben — sie liefern den
        `Riegel` samt Grund, statt ihn beim Aufrufer wieder zusammenzusetzen.
        """
        self._eintragen(riegel)

    def gerechnet(
        self, name: str, durchlaessig: bool, wert: float | None, grund: str = "",
    ) -> None:
        """Vermerkt einen Riegel, der gelaufen ist."""
        self._eintragen(Riegel(name, True, durchlaessig, wert, grund))

    def nicht_gerechnet(self, name: str, grund: str) -> None:
        """Vermerkt einen Riegel, der **nicht** gelaufen ist, mit dem Warum."""
        self._eintragen(Riegel(name, False, None, None, grund))

    def entschieden_von(self) -> str:
        """Der erste blockierende Riegel in der Reihenfolge des Kanons.

        Returns:
            Sein Name, oder ``""``, wenn keiner geblockt hat. Nicht gerechnete
            Riegel entscheiden nie — sie haben nichts gesehen.
        """
        # ── Verarbeitung / Ausgabe ──────────────────
        for name in RIEGEL_KANON:
            riegel: Riegel | None = self._riegel.get(name)
            if riegel is not None and riegel.durchlaessig is False:
                return name
        return ""

    def vollstaendig(self) -> bool:
        """Ob jeder Pflicht-Riegel tatsaechlich gerechnet wurde.

        **Eine leere Kette ist kein Freibrief.** Ohne diese Pruefung waere
        `durchgelassen()` fuer eine Kette ohne einen einzigen Eintrag wahr —
        „nichts geprueft" saehe aus wie „nichts einzuwenden", und genau das
        ist die Klasse, gegen die `zuwendung_pruefen` selbst gebaut ist.

        Returns:
            True, wenn alle Riegel aus `RIEGEL_PFLICHT` gerechnet vorliegen.
        """
        # ── Ausgabe ─────────────────────────────────
        return all(
            (r := self._riegel.get(name)) is not None and r.gerechnet
            for name in RIEGEL_PFLICHT
        )

    def fehlende_pflicht(self) -> list[str]:
        """Welche Pflicht-Riegel fehlen — fuer die Meldung, die es benennt."""
        # ── Ausgabe ─────────────────────────────────
        return sorted(
            name for name in RIEGEL_PFLICHT
            if (r := self._riegel.get(name)) is None or not r.gerechnet
        )

    def durchgelassen(self) -> bool:
        """Ob die Kette vollstaendig ist **und** kein Riegel geblockt hat.

        Zwei Bedingungen, nicht eine: Ein Urteil ohne die Pflicht-Riegel ist
        keines. Eine unvollstaendige Kette laesst deshalb **nicht** durch.
        """
        # ── Ausgabe ─────────────────────────────────
        return self.vollstaendig() and self.entschieden_von() == ""

    def als_protokoll(self) -> dict:
        """Das JSON-taugliche Abbild fuer den Protokolleintrag.

        **Jeder Riegel des Kanons steht darin**, auch der nie beruehrte — als
        ``gerechnet: false`` mit Grund. Eine Auswertung soll die Verteilung der
        Entscheidungsgruende zaehlen koennen, ohne zu wissen, welche Riegel es
        zum Zeitpunkt des Eintrags schon gab.
        """
        # ── Ausgabe ─────────────────────────────────
        return {
            "entschieden_von": self.entschieden_von(),
            "durchgelassen":   self.durchgelassen(),
            # **Steht im Eintrag, nicht nur im Code.** Eine Auswertung soll
            # eine unvollstaendige Kette von einer durchgelassenen trennen
            # koennen, ohne sie an `durchgelassen: false` zu raten.
            "vollstaendig":    self.vollstaendig(),
            "fehlende_pflicht": self.fehlende_pflicht(),
            "riegel": {
                name: (
                    {
                        "gerechnet":    r.gerechnet,
                        "durchlaessig": r.durchlaessig,
                        "wert":         r.wert,
                        "grund":        r.grund,
                    }
                    if (r := self._riegel.get(name)) is not None
                    else {
                        "gerechnet":    False,
                        "durchlaessig": None,
                        "wert":         None,
                        "grund":        "nicht erreicht",
                    }
                )
                for name in RIEGEL_KANON
            },
        }

    def kurzfassung(self) -> str:
        """Eine Zeile fuer die Spur — lesbar ohne Umweg ueber die Datenbank."""
        # ── Ausgabe ─────────────────────────────────
        teile: list[str] = []
        for name in RIEGEL_KANON:
            riegel: Riegel | None = self._riegel.get(name)
            if riegel is None:
                continue
            if not riegel.gerechnet:
                teile.append(f"{name}=?")
                continue
            zeichen: str = "+" if riegel.durchlaessig else "-"
            wert:    str = "" if riegel.wert is None else f"{riegel.wert:.2f}"
            teile.append(f"{name}{zeichen}{wert}")
        entscheider: str = self.entschieden_von() or "keiner"
        return f"[{' '.join(teile)}] entschieden={entscheider}"


def zuwendung_pruefen(
    stand: Haltungsstand | None,
    jetzt: float,
) -> Riegel:
    """Riegel 1 — ob sie ueberhaupt zugeht.

    Die Groesse ist die **Haltung**, nicht die Naehe-Achse der Landschaft: Die
    Achse beschreibt den Moment, gebraucht wird die Groesse, die Landschaft und
    Charakterrad verrechnet. Eine dauerhaft distanzierte Figur duerfte sonst
    einwerfen, sobald die Landschaft zufaellig warm ist.

    Args:
        stand: der zuletzt geschriebene Haltungsstand des Paares, oder ``None``.
        jetzt: Bezugszeit in Epochensekunden, fuer das Alter des Standes.

    Vorbedingung: keine.
    Nachbedingung: Ein gerechneter Riegel mit einem Grund aus der geschlossenen
        Menge oben. **Vier der fuenf Gruende heissen „unbekannt"** und werden
        getrennt gezaehlt: Ein Speicher, der nichts hergibt, darf in keiner
        Auswertung wie eine distanzierte Figur aussehen.
    Fehlerfaelle: Keiner fuehrt zum Durchlass. Ein Riegel, der seine
        Eingangsgroesse nicht lesen kann, verweigert — er ist sonst im Moment
        seiner groessten Nuetzlichkeit abgeschaltet.

    Returns:
        Das Ergebnis von Riegel 1.
    """
    # ── Eingabe-Validierung ─────────────────────
    if stand is None:
        return Riegel("wollen", True, False, None, GRUND_KEIN_STAND)

    if not stand.gerechnet:
        return Riegel("wollen", True, False, None, GRUND_OHNE_RECHNUNG)

    alter: float = stand.alter_sekunden(jetzt)
    if alter > ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN:
        logger.info(
            "Riegel wollen: Haltungsstand ist %.0f s alt (Grenze %.0f) — gilt "
            "als unbekannt, kein Einwurf",
            alter, ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN,
        )
        return Riegel("wollen", True, False, None, GRUND_ZU_ALT)

    naehe: float | None = stand.werte.get("naehe")
    if naehe is None:
        logger.error(
            "Riegel wollen: Haltungsstand aus Turn %r fuehrt keine Naehe "
            "(%s) — gilt als unbekannt, kein Einwurf",
            stand.turn_id, sorted(stand.werte),
        )
        return Riegel("wollen", True, False, None, GRUND_NAEHE_FEHLT)

    # ── Verarbeitung / Ausgabe ──────────────────
    if naehe < ZUWENDUNG_SCHWELLE:
        return Riegel("wollen", True, False, naehe, GRUND_UNTER_SCHWELLE)

    return Riegel("wollen", True, True, naehe, "")


def initiative_pruefen(
    stand: Haltungsstand | None,
    jetzt: float,
) -> Riegel:
    """Riegel 2 — ob sie gerade dran ist.

    **Ein Schalter, kein Frequenzmass.** Hat Nova im letzten Turn die
    Initiative gehabt, darf ein Impuls kommen; hatte der Mensch sie, nicht.
    Mehr entscheidet er nicht — *was* und *wie viel* durchkommt, entscheiden
    die uebrigen Riegel. Entschieden am 15.08.2026, und die Entscheidung hat
    eine Messung im Ruecken: Ueber sechs Paare mit je mindestens zwanzig Turns
    spannen die Paar-Mediane des Fuehrungsmasses 0,318, waehrend ein einzelnes
    Paar im Mittel 1,436 durchlaeuft. **Es traegt keine Frequenz je Paar** —
    aber genau diese Schwankung im Paar ist das, was ein Schalter auf den
    Moment braucht.

    **Die Schwelle wird nicht neu gesetzt.** `ei/dreischicht.py` macht aus
    demselben Fuehrungsmass seit Langem ein Bit, mit `GV_INITIATIVE_SCHWELLE`
    gegen 83 unabhaengige Lesarten kalibriert. Bit 1 heisst *du treibst*. Eine
    zweite Schwelle daneben hiesse, dass zwei Stellen dasselbe Wort verschieden
    lesen — und die Fassung wandert (34 Zeilen des Bestandes stehen noch auf
    -0.45, 424 auf -0.05).

    **Und er liest den rohen Wert, nicht das Achsen-Bit.** Bei fehlendem Mass
    setzt `dreischicht.py` Bit 1 — *Nova fuehrt* — und meldet es laut. Fuer
    eine Achse, die immer ein Bit braucht, ist das vertretbar; fuer einen
    Riegel waere es die Umkehrung seiner Aufgabe: Der Ausfall oeffnete den
    Schalter, statt ihn zu schliessen. Hier gilt dieselbe Regel wie bei
    Riegel 1 — **unbekannt ist nicht dasselbe wie in Ordnung.**

    Args:
        stand: der zuletzt geschriebene Haltungsstand des Paares, oder ``None``.
        jetzt: Bezugszeit in Epochensekunden, fuer das Alter des Standes.

    Vorbedingung: keine.
    Nachbedingung: Ein gerechneter Riegel. **Nur ein Grund heisst „nein"**
        (`GRUND_MENSCH_FUEHRT`); die uebrigen heissen „unbekannt" und werden
        getrennt gezaehlt.
    Fehlerfaelle: Keiner fuehrt zum Durchlass.

    Returns:
        Das Ergebnis von Riegel 2.
    """
    # ── Eingabe-Validierung ─────────────────────
    if stand is None:
        return Riegel("frequenz", True, False, None, GRUND_KEIN_STAND)

    # **Kein `stand.gerechnet` an dieser Stelle.** Die Marke gilt der Haltung;
    # das Fuehrungsmass ist eine eigene Messung mit eigenem Ausfall. Wer hier
    # darauf pruefte, liesse Riegel 1 den Riegel 2 verdecken — und dessen
    # Verteilung waere nie wieder kalibrierbar.
    alter: float = stand.alter_sekunden(jetzt)
    if alter > ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN:
        logger.info(
            "Riegel frequenz: Haltungsstand ist %.0f s alt (Grenze %.0f) — wer "
            "gerade fuehrt, sagt er nicht mehr, kein Einwurf",
            alter, ZUWENDUNG_STAND_MAX_ALTER_SEKUNDEN,
        )
        return Riegel("frequenz", True, False, None, GRUND_ZU_ALT)

    if stand.initiative is None:
        logger.info(
            "Riegel frequenz: Stand aus Turn %r fuehrt kein Fuehrungsmass "
            "(%s) — gilt als unbekannt, kein Einwurf",
            stand.turn_id, stand.initiative_grund or "ohne Grund",
        )
        return Riegel("frequenz", True, False, None, GRUND_INITIATIVE_FEHLT)

    # ── Verarbeitung / Ausgabe ──────────────────
    # Bit 1 = „du treibst" = sie ist dran. Die Binarisierung steht in
    # `ei/initiative.py`, damit Laufzeit und Kalibrierlauf dieselbe Regel
    # benutzen — und dieser Riegel jetzt auch.
    if initiative_bit(stand.initiative, GV_INITIATIVE_SCHWELLE) != 1:
        return Riegel(
            "frequenz", True, False, stand.initiative, GRUND_MENSCH_FUEHRT,
        )

    return Riegel("frequenz", True, True, stand.initiative, "")
