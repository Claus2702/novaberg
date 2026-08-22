"""Datumspruefung der Antwort — der Wochentag muss zum Datum passen.

Ein Sprachmodell kann eine Zeitangabe erfinden, obwohl sein Prompt die richtige
zweimal trug. Am 17.08.2026 gemessen: Der Agent meldete
`"eingetragen fuer 19.08.2026 14:00"`, der Szenenblock nannte
`"Monday, 17.08.2026"`, und die Antwort lautete *„Mittwoch, 20.08., 14:00 Uhr"*.
Der 20.08.2026 ist ein Donnerstag.

**Das ist kein Datenproblem, sondern ein Ausgabeproblem** — die Eingabe war
richtig. Deshalb gehoert die Abhilfe in die Ausgabe-Verifikation und nicht in
einen besseren Prompt.

Der Kern ist eine Pruefung, die keine Bezugsdaten braucht: Nennt ein Text einen
Wochentag unmittelbar vor einem Datum, dann muessen beide zusammenpassen. Der
Widerspruch ist im Text selbst enthalten und deterministisch feststellbar — ganz
unabhaengig davon, was gespeichert wurde.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

logger = logging.getLogger("ki_server.datum_pruefung")

#: Wochentagsnamen auf ihre Nummer nach `date.weekday()` (Montag = 0).
#: Sonnabend steht neben Samstag, weil beide im Gebrauch sind.
WOCHENTAGE: dict[str, int] = {
    "montag": 0, "dienstag": 1, "mittwoch": 2, "donnerstag": 3,
    "freitag": 4, "samstag": 5, "sonnabend": 5, "sonntag": 6,
}

#: Nummer zurueck auf den Namen — fuer die Meldung, die den richtigen nennt.
NAMEN: tuple[str, ...] = (
    "Montag", "Dienstag", "Mittwoch", "Donnerstag",
    "Freitag", "Samstag", "Sonntag",
)

#: Wochentag, dann hoechstens ein kurzes Bindeglied, dann ein Datum.
#:
#: Die Kopplung ist absichtlich **eng** (bis zu zwoelf Zeichen zwischen
#: beiden, keine Satzzeichen ausser Komma und Punkt): Eine weite Kopplung
#: verbindet einen Wochentag mit einem Datum aus einer anderen Aussage
#: desselben Satzes und meldet einen Widerspruch, den es nicht gibt. Ein
#: Fehlalarm hier ist teuer, weil er eine richtige Antwort in die
#: Korrekturschleife schickt.
_PAAR = re.compile(
    r"\b(?P<tag>" + "|".join(WOCHENTAGE) + r")\b"
    r"(?P<brueck>[,\s]{0,4}(?:den|dem|der)?[,\s]{0,4})"
    r"(?P<d>\d{1,2})\.\s?(?P<m>\d{1,2})\.(?:\s?(?P<j>\d{4}))?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Widerspruch:
    """Ein Wochentag, der nicht zu seinem Datum passt."""

    genannt: str        # der Wochentag im Text
    datum: date         # das Datum im Text
    richtig: str        # der Wochentag, den dieses Datum wirklich hat
    fundstelle: str     # der Wortlaut, damit die Meldung auffindbar bleibt

    def satz(self) -> str:
        """Einzeiler fuer Protokoll und Korrekturauftrag."""
        return (
            f"'{self.fundstelle}': Der {self.datum.strftime('%d.%m.%Y')} ist ein "
            f"{self.richtig}, nicht {self.genannt.capitalize()}"
        )


def _jahr_ergaenzen(tag: int, monat: int, heute: date) -> date | None:
    """Ergaenzt ein fehlendes Jahr durch das naechstliegende.

    Vorbedingung: `tag` und `monat` sind Zahlen aus dem Text; sie koennen
    unmoeglich sein (32.13.) und ergeben dann None.

    Nachbedingung: das Datum mit dem Jahr, dessen Abstand zu `heute` am
    kleinsten ist — geprueft werden Vorjahr, laufendes Jahr und Folgejahr.
    Ein Datum ohne Jahr meint fast immer das naechstliegende; das Jahr
    stumpf auf `heute.year` zu setzen brach ueber den Jahreswechsel.
    """
    kandidaten: list[date] = []
    for jahr in (heute.year - 1, heute.year, heute.year + 1):
        try:
            kandidaten.append(date(jahr, monat, tag))
        except ValueError:
            continue
    if not kandidaten:
        return None
    return min(kandidaten, key=lambda d: abs((d - heute).days))


def widersprueche_finden(text: str, heute: date) -> list[Widerspruch]:
    """Findet Wochentag-Datum-Paare im Text, die nicht zusammenpassen.

    Vorbedingung: `text` ist die fertige Antwort, `heute` das Datum des
    Turns. Beides wird geprueft; bei defekter Eingabe wird gemeldet und eine
    leere Liste zurueckgegeben — eine Pruefung darf den Antwortpfad nicht
    anhalten.

    Nachbedingung: Liste der Widersprueche, jeder mit dem genannten und dem
    richtigen Wochentag. Leere Liste heisst: kein Paar gefunden ODER alle
    Paare stimmen. Die beiden Faelle werden im Log unterschieden, weil
    "nichts gefunden" und "alles richtig" verschiedene Aussagen sind.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not isinstance(text, str):
        logger.error(
            "Datumspruefung: text ist %s statt str — keine Pruefung",
            type(text).__name__,
        )
        return []
    if not isinstance(heute, date):
        logger.error(
            "Datumspruefung: heute ist %s statt date — keine Pruefung",
            type(heute).__name__,
        )
        return []
    if not text.strip():
        return []

    # ── Verarbeitung ─────────────────────────────────────────────────
    gefunden: list[Widerspruch] = []
    paare = 0
    for m in _PAAR.finditer(text):
        tag_name = m.group("tag").lower()
        try:
            d, mo = int(m.group("d")), int(m.group("m"))
        except ValueError:      # pragma: no cover — Muster erlaubt nur Ziffern
            continue

        if m.group("j"):
            try:
                datum = date(int(m.group("j")), mo, d)
            except ValueError:
                logger.info(
                    "Datumspruefung: '%s' ist kein gueltiges Datum — uebergangen",
                    m.group(0).strip(),
                )
                continue
        else:
            gefunden_datum = _jahr_ergaenzen(d, mo, heute)
            if gefunden_datum is None:
                logger.info(
                    "Datumspruefung: '%s' ergibt in keinem Jahr ein Datum — "
                    "uebergangen", m.group(0).strip(),
                )
                continue
            datum = gefunden_datum

        paare += 1
        if datum.weekday() != WOCHENTAGE[tag_name]:
            gefunden.append(Widerspruch(
                genannt=tag_name,
                datum=datum,
                richtig=NAMEN[datum.weekday()],
                fundstelle=m.group(0).strip(),
            ))

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if paare == 0:
        logger.debug("Datumspruefung: kein Wochentag-Datum-Paar im Text")
    elif not gefunden:
        logger.debug("Datumspruefung: %d Paar(e) geprueft, alle stimmen", paare)
    else:
        logger.error(
            "Datumspruefung: %d von %d Wochentag-Datum-Paar(en) widersprechen "
            "sich — %s",
            len(gefunden), paare, "; ".join(w.satz() for w in gefunden),
        )

    if len(gefunden) > paare:
        logger.error(
            "Datumspruefung: %d Widersprueche bei %d Paaren — die Zaehlung "
            "ist unmoeglich, Ergebnis verworfen", len(gefunden), paare,
        )
        return []

    return gefunden


def korrekturauftrag(widersprueche: list[Widerspruch]) -> str:
    """Formuliert den Auftrag, mit dem die Korrekturrunde arbeitet.

    Vorbedingung: `widersprueche` ist nicht leer — geprueft beim Aufrufer.
    Nachbedingung: nicht-leerer Text, der jeden Widerspruch nennt und den
    richtigen Wochentag mitgibt.

    Der Auftrag nennt den richtigen Wert, statt nur den Fehler zu ruegen:
    Ein Modell, das erfahren hat, dass etwas falsch ist, erfindet sonst den
    naechsten Wert.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not widersprueche:
        logger.error("Korrekturauftrag ohne Widerspruch angefordert — leer")
        return ""

    zeilen = [
        "ZEITANGABE FALSCH — Wochentag und Datum passen nicht zusammen:",
        *(f"  - {w.satz()}" for w in widersprueche),
        "Nenne die Zeitangabe erneut und richtig. Aendere sonst nichts.",
    ]
    return "\n".join(zeilen)


# ─────────────────────────────────────────────────────────────────────────
# Die Bestaetigung gegen das, was der Dienst wirklich eingetragen hat
# ─────────────────────────────────────────────────────────────────────────

#: Ein Datum ohne Wochentag davor. Deckt `19.08.2026`, `19.08.` und `19.8.`.
#:
#: Die Pruefung oben braucht das **Paar** aus Wochentag und Datum; nennt eine
#: Antwort ein erfundenes Datum ohne Wochentag, findet sie nichts. Gemessen am
#: 22.08.2026 am Originalfall: mit Wochentag 1 Befund, ohne 0.
_DATUM = re.compile(r"\b(?P<d>\d{1,2})\.\s?(?P<m>\d{1,2})\.(?:\s?(?P<j>\d{4}))?")


@dataclass(frozen=True)
class Abweichung:
    """Ein Datum in der Antwort, das in keiner Quelle des Turns steht."""

    genannt: date          # was die Antwort sagt
    belegt: tuple[date, ...]   # was die Dienste gemeldet haben

    def satz(self) -> str:
        """Einzeiler fuer Protokoll und Korrekturauftrag."""
        belegt = ", ".join(d.strftime("%d.%m.%Y") for d in self.belegt)
        return (
            f"Die Antwort nennt den {self.genannt.strftime('%d.%m.%Y')}; "
            f"eingetragen wurde {belegt}"
        )


def datumsangaben(text: str, heute: date) -> set[date]:
    """Alle Datumsangaben eines Textes, Jahr wo noetig ergaenzt.

    Vorbedingung: `text` ist beliebig, auch leer. `heute` traegt den Bezug
    fuer Angaben ohne Jahr.
    Nachbedingung: die Menge der erkannten Daten; unmoegliche Angaben
    (32.13.) fallen still heraus, weil sie kein Datum sind und keine
    Aussage ueber die Antwort erlauben.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    gefunden: set[date] = set()
    for treffer in _DATUM.finditer(text or ""):
        jahr = treffer.group("j")
        if jahr:
            try:
                gefunden.add(date(int(jahr), int(treffer.group("m")),
                                  int(treffer.group("d"))))
            except ValueError:
                continue
        else:
            datum = _jahr_ergaenzen(int(treffer.group("d")),
                                    int(treffer.group("m")), heute)
            if datum is not None:
                gefunden.add(datum)

    # ── Ausgabe ──────────────────────────────────────────────────────
    return gefunden


def bestaetigung_pruefen(
    antwort: str,
    quellen: list[str],
    heute: date,
) -> list[Abweichung]:
    """Prueft, ob die Antwort ein Datum bestaetigt, das kein Dienst nennt.

    **Der Fall** (`RESPONDER-ERFINDET-DATUM`, 17.08.2026): Der Dienst meldete
    `Termin 'Meeting mit dem Chef' eingetragen fuer 19.08.2026 14:00`, die
    Antwort nannte den 20.08. Der Mensch sucht am falschen Tag, findet nichts
    und haelt den Schreibpfad fuer defekt — er war es nie.

    **Die Bedingung ist absichtlich eng, und das ist der Kern dieser
    Funktion.** Gemeldet wird nur, wenn beides zutrifft:

      1. Eine Quelle nennt ein Datum — es gibt also etwas zu bestaetigen.
      2. Die Antwort nennt **keines** der Quelldaten, wohl aber ein anderes.

    Nennt die Antwort das richtige Datum und daneben ein zweites, ist das
    keine falsche Bestaetigung, sondern ein Satz ueber etwas anderes: *„Der
    Termin steht am 19.08. — der 25.08. waere mir lieber gewesen."* Eine
    Regel *„jedes Datum muss belegt sein"* schickte diesen Satz in die
    Korrekturschleife, und ein Fehlalarm ist hier teuer: Er korrigiert eine
    richtige Antwort.

    Vorbedingung: `quellen` sind die Ergebnistexte der Dienste dieses Turns.
    Eine leere Liste ist zulaessig und liefert nichts — kein Turn muss
    Dienste gerufen haben.
    Nachbedingung: je erfundenem Datum eine `Abweichung` mit dem belegten
    Wert daneben. Der Wert steht dabei, damit die Korrektur ihn nennen kann
    statt den naechsten zu erfinden.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not antwort or not quellen:
        return []

    belegt: set[date] = set()
    for quelle in quellen:
        belegt |= datumsangaben(quelle, heute)
    if not belegt:
        # Kein Dienst hat ein Datum gemeldet — es gibt nichts zu bestaetigen,
        # und jede Angabe der Antwort gehoert einem anderen Satz.
        return []

    # ── Verarbeitung ─────────────────────────────────────────────────
    genannt: set[date] = datumsangaben(antwort, heute)
    if belegt & genannt:
        # Das eingetragene Datum steht in der Antwort. Weitere Angaben
        # daneben sind kein Widerspruch (siehe Docstring).
        return []

    abweichungen: list[Abweichung] = [
        Abweichung(genannt=d, belegt=tuple(sorted(belegt)))
        for d in sorted(genannt)
    ]

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if abweichungen:
        logger.error(
            "Datumspruefung: Antwort bestaetigt %d Datum/Daten, das kein Dienst "
            "nennt — %s",
            len(abweichungen), "; ".join(a.satz() for a in abweichungen),
        )
    return abweichungen


def bestaetigungsauftrag(abweichungen: list[Abweichung]) -> str:
    """Der Korrekturauftrag zur falschen Bestaetigung.

    Vorbedingung: `abweichungen` ist nicht leer — geprueft beim Aufrufer.
    Nachbedingung: nicht-leerer Text, der jede Abweichung nennt und den
    belegten Wert mitgibt — aus demselben Grund wie oben: Ein Modell, das
    nur erfaehrt, dass etwas falsch war, erfindet den naechsten Wert.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not abweichungen:
        logger.error("Bestaetigungsauftrag ohne Abweichung angefordert — leer")
        return ""

    zeilen = [
        "ZEITANGABE FALSCH — die Bestaetigung nennt ein Datum, das kein Dienst "
        "eingetragen hat:",
        *(f"  - {a.satz()}" for a in abweichungen),
        "Nenne das eingetragene Datum. Aendere sonst nichts.",
    ]
    return "\n".join(zeilen)
