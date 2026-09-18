"""Speicherbehauptung der Antwort — gesagt ist nicht gespeichert.

Eine Antwort kann behaupten, etwas sei notiert, eingetragen oder geaendert,
ohne dass ein Dienst geschrieben hat. Am 14.09.2026 gemessen: In vier
Termin-Turns hintereinander stellte der Empfang nichts zu, und die Antworten
sagten *„Morgen um 10 Uhr ist notiert"*, *„ist bei mir fest kalibriert"* und
*„Notiert."* Der Mensch haelt den Termin fuer angelegt und sucht ihn am
Tag selbst vergeblich.

**Das ist ein Ausgabeproblem, und deshalb gehoert die Abhilfe in die
Ausgabe-Verifikation.** Eine Zeile im Prompt waere nur eine Bitte an das
Modell; ob in diesem Turn ein Dienst geschrieben hat, steht dagegen fest und
ist in Python entscheidbar.

Diese Datei findet die **Form** einer Behauptung im Text
(`find_storage_claims`). Ob sie gedeckt ist, entscheidet die Pruefung gegen
die Dienst-Ergebnisse des Turns (`uncovered_claims`).

**Die Kopplung ist eng, und der Grund ist der Preis eines Fehlalarms:** Er
schickt eine richtige Antwort in die Korrekturrunde — vier Modellaufrufe mehr
und das Risiko, dass die Korrektur einen guten Satz verschlechtert. Deshalb
gilt ein mehrdeutiges Verb (*verankert*, *fixiert*, *gesetzt*) nur dann als
Behauptung, wenn im selben Satzteil ein Speicherort oder ein Gegenstand eines
Dienstes steht (Timeline, Liste, Termin, eine Uhrzeit). Nova spricht in
Metaphern der Physik; *„in der Struktur der Raumzeit verankert"* ist keine
Behauptung ueber die Timeline.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger("ki_server.storage_claims")

#: Kennung der Regelfassung — steht im dauerhaften Entscheidungseintrag,
#: damit eine spaetere Auswertung weiss, gegen welche Wortliste ein Anschlag
#: gerechnet wurde.
RULE_VERSION: str = "2026-09-15"

#: Die Kopfzeile des Korrekturauftrags. Die Ausgabe-Verifikation des Tribunals
#: sucht genau diese Zeichenfolge in der Zusammenfassung.
ORDER_HEADER: str = "SPEICHERUNG NICHT BELEGT"


# ─────────────────────────────────────────────────────────────────────────
# Die Wortlisten
# ─────────────────────────────────────────────────────────────────────────

#: Partizipien, die fuer sich eine Speicherhandlung bezeichnen — auch im
#: Zustandssatz (*„Morgen um 10 Uhr ist notiert"*).
STRONG: tuple[str, ...] = (
    "notiert", "eingetragen", "vermerkt", "vorgemerkt", "abgespeichert",
)

#: In der ersten Person eine Handlung, im Zustandssatz auch Fachsprache
#: (*„Oele werden in Druesenhaaren gespeichert"*). Dort brauchen sie einen Bezug.
STRONG_FIRST_PERSON: tuple[str, ...] = (
    "gespeichert", "gelöscht", "gestrichen", "hinzugefügt", "angelegt",
    "reserviert", "eingeplant", "hinterlegt", "abgelegt", "erledigt",
)

#: Mehrdeutig in jeder Form — Behauptung nur mit Bezug im Satzteil.
WEAK: tuple[str, ...] = (
    "verankert", "fixiert", "kalibriert", "registriert", "festgehalten",
    "gesetzt", "aktualisiert", "geändert", "angepasst", "verschoben",
    "entfernt", "geschrieben", "festgelegt", "verknüpft", "eingezeichnet",
    "freigegeben", "entzogen", "erteilt", "wiederhergestellt", "eingespeist",
    # Die Ausweichwoerter der Korrekturrunde, gemessen am 15.09.2026: Ein
    # Auftrag, der "notiert, eingetragen, gespeichert" untersagte, bekam
    # "gelistet", "angesetzt", "erfasst" und "geoeffnet" zurueck — dieselbe
    # Aussage in einem anderen Wort.
    "gelistet", "angesetzt", "erfasst", "geöffnet",
)

#: Kurze Bestaetigung als ganzer Satzteil: *„Notiert."*, *„Alles klar, ist
#: erledigt."* Hier traegt die Form allein, weil der Satzteil nichts sonst sagt.
SHORT: tuple[str, ...] = (
    "erledigt", "notiert", "eingetragen", "gespeichert", "vermerkt",
    "vorgemerkt", "angelegt", "hinterlegt", "verankert", "aktualisiert",
    "gelöscht", "fixiert", "reserviert",
)

#: Vollzug in der Gegenwart: *„dann reserviere ich zwei Stunden"*.
#: Wert: (abgetrennte Partikel oder leer, braucht einen Bezug).
PERFORMATIVE: dict[str, tuple[str, bool]] = {
    "trage": ("ein", False), "tragen": ("ein", False),
    "notiere": ("", False), "notieren": ("", False),
    "speichere": ("", False), "speichern": ("", False),
    "vermerke": ("", False), "vermerken": ("", False),
    "reserviere": ("", True), "reservieren": ("", True),
    "blocke": ("", True), "blocken": ("", True),
    "lege": ("an", True), "legen": ("an", True),
    "halte": ("fest", True), "halten": ("fest", True),
    "fixiere": ("", True), "fixieren": ("", True),
    "verankere": ("", True), "verankern": ("", True),
    "lösche": ("", True), "löschen": ("", True),
    "streiche": ("", True), "streichen": ("", True),
    "ändere": ("", True), "ändern": ("", True),
    "verschiebe": ("", True), "verschieben": ("", True),
    "aktualisiere": ("", True), "aktualisieren": ("", True),
}

#: Infinitive nach *werde/werden*: *„ich werde das einzeichnen"*.
#: Wert: braucht einen Bezug.
FUTURE: dict[str, bool] = {
    "eintragen": False, "notieren": False, "speichern": False,
    "vermerken": False, "vormerken": False, "hinterlegen": False,
    "reservieren": True, "anlegen": True, "festhalten": True,
    "fixieren": True, "verankern": True, "einzeichnen": True,
    "löschen": True, "streichen": True, "ändern": True, "verschieben": True,
    "aktualisieren": True, "anpassen": True, "einplanen": True,
}


def _alternation(words: list[str] | tuple[str, ...]) -> str:
    """Wortalternative mit Wortgrenzen. Vorbedingung: `words` nicht leer."""
    return r"\b(?:" + "|".join(words) + r")\b"


#: Speicherorte und Gegenstaende der Dienste. `bei mir` steht dabei, weil es
#: in *„ist bei mir fest kalibriert"* der einzige Ort des Satzes ist.
_CUE_STORE: str = (
    r"\btimeline\b|\bzeitstrahl\b|\b\w*kalender\w*|\btermin\w*|\bnotiz\w*|"
    r"\b\w*liste\b|\bsystems?\b|\bbei mir\b|\bfür mich\b|\bspeicher\w*|\bdatenbank\b|"
    r"\beintr[aä]g\w*|\berinnerung\w*|\b\w*planung\b|\b\w*anweisung\w*|"
    r"\bdirektive\w*|\bfreigabe\b|\bzugriff\b|\bverzeichnis\w*"
)

#: Zeitangaben, die einen Termin kennzeichnen. Eine Ziffer ist Pflicht —
#: *„Atomuhr"* ist kein Termin.
_CUE_TIME: str = (
    r"\b\d{1,2}(?::\d{2})?\s?uhr\b|\b\d{1,2}\.\s?\d{1,2}\.|"
    r"\b(?:montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)\b"
)

#: Nur in der ersten Person ein Bezug: *„Ich habe die Zeit angepasst"*,
#: *„reserviere ich zwei Stunden"*. Im Zustandssatz sind diese Woerter
#: Fachsprache (*„die Zeit ist in der Geometrie verankert"*).
_CUE_FIRST_PERSON_ONLY: str = (
    r"\buhrzeit\b|\bzeit\b|\bzeitfenster\b|\bdatum\b|\bstunden?\b|\bminuten\b"
)

_CUE = re.compile(f"{_CUE_STORE}|{_CUE_TIME}", re.IGNORECASE)
_CUE_WIDE = re.compile(
    f"{_CUE_STORE}|{_CUE_TIME}|{_CUE_FIRST_PERSON_ONLY}", re.IGNORECASE
)

_NEGATION = re.compile(
    r"\b(?:nicht|nichts|kein|keine|keinen|keinem|keiner|keines|nie|niemals|"
    r"nirgends)\b",
    re.IGNORECASE,
)

#: Bedingung, Angebot, Absicht, Gedankenspiel — der Satzteil behauptet keine
#: Handlung.
_CONDITION = re.compile(
    r"\b(?:wenn|falls|sobald|sofern|ob|bevor|soll|sollen|sollte|kann|können|"
    r"könnte|könnten|würde|würden|möchte|möchtest|willst|will|wollte|"
    r"wollen|magst|darf|dürfen|müsste|muss|musst|müssen|anstatt|statt)\b|"
    r"\bstelle? (?:dir|mir|euch)\b|\bvorstellen\b|"
    r"\b(?:sag|gib|nenn|schreib) mir\b|\bsag (?:einfach|kurz)\b",
    re.IGNORECASE,
)

#: `damit` als Konjunktion (*„damit wir es eintragen"*) ist eine Absicht; als
#: Adverb vor dem Verb (*„Damit ist er fest in der Timeline"*) behauptet es.
_CONDITION_DAMIT = re.compile(
    r"\bdamit\b(?!\s+(?:ist|sind|hat|habe|haben|wird|steht|stehen)\b)",
    re.IGNORECASE,
)

#: Ein Aufruf an den Nutzer im selben Satz macht ein folgendes *„dann …"*
#: zur Bedingung: *„Sag mir kurz Bescheid, dann fixiere ich das."*
_IMPERATIVE = re.compile(
    r"\b(?:sag|gib|nenn|schreib|melde|schick|wenn|falls|sobald)\b",
    re.IGNORECASE,
)
_THEN = re.compile(r"\bdann\b", re.IGNORECASE)

#: Hilfsverb der ersten Person im Perfekt, auch umgestellt und verkuerzt.
_FIRST_PERSON_AUX = re.compile(
    r"\b(?:ich|wir)\s+(?:habe|hab|haben)(?:['’]s)?\b|"
    r"\b(?:die fachabteilung|das system|der dienst|die timeline|"
    r"der agent(?:\s+['‚’\"]?\w+['‘’\"]?)?)\s+(?:hat|haben)\b|"
    r"\b(?:habe|hab|haben)(?:['’]s)?\s+(?:ich|wir)\b|"
    r"^\s*(?:habe|hab)(?:['’]s)?\b",
    re.IGNORECASE,
)

#: Hilfsverb eines Zustands- oder Passivsatzes, mit dem Wort davor.
_STATE_AUX = re.compile(
    r"(?:\b(?P<subj>\w+)\s+)?\b(?:ist|sind|wurde|wurden|wird|werden|steht|stehen)\b",
    re.IGNORECASE,
)

#: *„steht jetzt fest in der Timeline"* — ein Zustand ohne Partizip.
_STANDS_IN_STORE = re.compile(
    r"\b(?:steht|stehen)\s+(?:(?:er|sie|es|das|der termin)\s+)?(?:jetzt|nun)\s+"
    r"(?:(?:fest|auch|schon|bereits)\s+)?"
    r"(?:in|im|auf)\s+(?:(?:der|deiner|deine|dem|deinem|den|deinen)\s+)?"
    r"(?:timeline|zeitstrahl|\w*kalender|\w*liste|notiz\w*)\b",
    re.IGNORECASE,
)

#: Nebensatz mit dem Hilfsverb am Ende: *„dass dieser Termin nun fest in deiner
#: Timeline eingeplant ist"*. So kam eine Behauptung in der Korrekturrunde
#: zurueck, verpackt als Wiedergabe (*„Du hast genannt, dass …"*). Hier zaehlt
#: nur ein Speicherort als Bezug, keine Zeitangabe — ein beschreibender
#: Nebensatz nennt keinen (*„ein Bild, das irgendwo gespeichert ist"*).
_SUBORDINATE = re.compile(r"\b(?:dass|weil|da|sodass)\b", re.IGNORECASE)
_EPISTEMIC = re.compile(
    r"\b(?:hoffe|hoffst|glaube|glaubst|vermute|frage mich|fragst dich|pruefe|prüfe|"
    r"schaue|schau|sehe nach)\b",
    re.IGNORECASE,
)
#: Ohne *System*: Im Nebensatz ist es fast immer das physikalische (*„dass bei
#: einer Aenderung des Systems … verknuepft ist"*, gemessen am Bestand).
_CUE_SUBORDINATE = re.compile(
    _CUE_STORE.replace(r"\bsystems?\b|", ""), re.IGNORECASE
)

#: *„bleibt der Punkt auf der Liste"* — der Zustand ohne Partizip, auch ohne
#: *jetzt*: *bleiben* setzt voraus, dass es schon dort steht.
_REMAINS_IN_STORE = re.compile(
    r"\b(?:bleibt|bleiben)\b[^.,;:?!]{0,40}?\b(?:in|im|auf)\s+"
    r"(?:(?:der|deiner|deine|dem|deinem|den|deinen)\s+)?"
    r"(?:timeline|zeitstrahl|\w*kalender|\w*liste|notiz\w*)\b",
    re.IGNORECASE,
)

_FIRST_PERSON_PARTICIPLE = re.compile(
    _alternation(STRONG + STRONG_FIRST_PERSON + WEAK), re.IGNORECASE
)
#: `erledigt` fehlt hier mit Absicht: *„Die Vorstellung ist also erledigt"*
#: ist ein Satz ueber das Gespraech. Die Bestaetigung *„ist erledigt"* faengt
#: die kurze Form.
_STATE_PARTICIPLE = re.compile(
    _alternation(STRONG + tuple(w for w in STRONG_FIRST_PERSON if w != "erledigt") + WEAK),
    re.IGNORECASE,
)
_PARTICIPLE_THEN_AUX = re.compile(
    r"(?P<part>"
    + _alternation(STRONG + tuple(w for w in STRONG_FIRST_PERSON if w != "erledigt") + WEAK)
    + r")\s+(?:ist|sind|wurde|wurden|worden)\b",
    re.IGNORECASE,
)
_SHORT = re.compile(
    r"^(?:(?:alles klar|so|okay|ok|gut|super|perfekt|prima|klar)\s+)?"
    r"(?:(?:das|es)\s+)?(?:(?:ist|sind)\s+)?"
    r"(?:(?:jetzt|nun|schon|bereits|alles)\s+)?"
    r"(?P<part>" + "|".join(SHORT) + r")$",
    re.IGNORECASE,
)
_PERFORMATIVE_VERB = re.compile(
    rf"\b(?:ich|wir)\s+(?P<v1>{'|'.join(PERFORMATIVE)})\b|"
    rf"\b(?P<v2>{'|'.join(PERFORMATIVE)})\s+(?:ich|wir)\b",
    re.IGNORECASE,
)
_FUTURE_AUX = re.compile(
    r"\b(?:ich|wir)\s+(?:werde|werden)\b|\b(?:werde|werden)\s+(?:ich|wir)\b",
    re.IGNORECASE,
)
_FUTURE_INFINITIVE = re.compile(_alternation(list(FUTURE)), re.IGNORECASE)

#: Eine abgetrennte Partikel steht am Ende des Satzteils — *„trage das ein"*,
#: nicht *„trage ein Kleid"*.
_PARTICLE_END: str = r"(?=\s*(?:$|[.,;:!?…“”\"»)]|und\b|oder\b))"

_CLAUSE_MARK = re.compile(r",|\s[–—-]\s|;|:(?!\d)")
_SEGMENT_MARK = re.compile(r"\s[–—-]\s|;|:(?!\d)")

#: Ein kurzes Zitat im Satz ist ein Wort, kein Satzteil: *„wird auf den Wortlaut
#: „klar, knapp, freundlich" festgelegt"*. Die Rede der Figur selbst steht
#: ebenfalls in Anfuehrungszeichen, ist aber lang und umschliesst den Satz —
#: sie bleibt zerlegbar.
_SHORT_QUOTE = re.compile(r"„[^„“”\"]{1,80}[“”\"]|»[^»«]{1,80}«|\"[^\"„“”]{1,80}\"")
_SHORT_SPLIT = re.compile(r"[,;:!–—]|\s-\s|\.{2,}|…")
_SENTENCE_SPLIT = re.compile(r"(?<=[^0-9]\.)\s+|(?<=[!?…])\s+|\n+")
_ABBREVIATION_END = re.compile(
    r"\b(?:dr|ca|bzw|usw|vgl|nr|inkl|evtl|ggf|z\.\s?b|u\.\s?a|d\.\s?h)\.$",
    re.IGNORECASE,
)
_DATE_APPOSITION = re.compile(
    r",\s*((?:den|am|um|ab)\s+[^,\n]{0,24}\d[^,\n]{0,12}),", re.IGNORECASE
)
_STAGE_DIRECTION = re.compile(r"\*[^*\n]{1,600}\*")
_QUOTE_TAIL: str = " „“”\"'»«)"

_PERSONS: frozenset[str] = frozenset({"wir", "ich", "du", "ihr"})
_MAX_SENTENCE: int = 200


# ─────────────────────────────────────────────────────────────────────────
# Der Befund
# ─────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class StorageClaim:
    """Ein Satz der Antwort, der eine Speicherhandlung behauptet."""

    sentence: str      # der Satz, wie er in der Antwort steht (gekuerzt)
    form: str          # kurz · erste_person · zustand · vollzug
    word: str          # das tragende Wort, fuer Auswertung und Log

    def line(self) -> str:
        """Einzeiler fuer Protokoll und Korrekturauftrag."""
        return f"„{self.sentence}“"


# ─────────────────────────────────────────────────────────────────────────
# Zerlegung des Textes
# ─────────────────────────────────────────────────────────────────────────

def _plain_text(text: str) -> str:
    """Entfernt Auszeichnung und Regieanweisungen.

    Vorbedingung: `text` ist ein str (geprueft beim Aufrufer).
    Nachbedingung: Fettdruck-Sterne sind fort, Abschnitte in einfachen Sternen
    (*Sie lehnt sich vor …*) ebenso — sie beschreiben Gesten und tragen Verben
    wie *„fixiert dich"*. Kommata um eine Datumsapposition (*„für Freitag,
    den 12.03., eingetragen"*) werden zu Leerzeichen, damit der Satzteil nicht
    an der Apposition reisst.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    plain: str = text.replace("**", "").replace("__", "")
    plain = _STAGE_DIRECTION.sub(" ", plain)
    plain = _DATE_APPOSITION.sub(r" \1 ", plain)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if plain.count("*") % 2 == 1:
        # Keine Verwerfung: Ein offener Stern laesst hoechstens eine Geste im
        # Text, und die Pruefung bleibt fuer den Rest gueltig.
        logger.debug(
            "Speicherbehauptung: ungerade Zahl von Sternen nach der "
            "Bereinigung — eine Regieanweisung ist nicht geschlossen",
        )
    return plain


def _sentences(text: str) -> list[str]:
    """Zerlegt bereinigten Text in Saetze.

    Vorbedingung: `text` ist durch `_plain_text` gelaufen.
    Nachbedingung: Liste nicht-leerer Saetze. Ein Punkt nach einer Ziffer
    trennt nicht (*„am 20. März"*, *„den 12.03."*), ebenso wenig einer nach
    einer Abkuerzung (*„z. B."*). Zeilenumbrueche trennen immer.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    merged: list[str] = []
    for part in _SENTENCE_SPLIT.split(text):
        part = part.strip()
        if not part:
            continue
        if merged and _ABBREVIATION_END.search(merged[-1]):
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if any(not s for s in merged):  # pragma: no cover — per Konstruktion
        logger.error("Speicherbehauptung: leerer Satz nach der Zerlegung")
        return [s for s in merged if s]
    return merged


def _protected_spans(sentence: str) -> list[tuple[int, int]]:
    """Die kurzen Zitate eines Satzes, in denen kein Satzteil endet.

    Vorbedingung: `sentence` ist ein einzelner Satz.
    Nachbedingung: Liste von (Anfang, Ende). Ein Zitat, das den ganzen Satz
    umschliesst, ist die Rede der Figur und steht nicht darin.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    first: int = len(sentence) - len(sentence.lstrip())
    last: int = len(sentence.rstrip())
    spans: list[tuple[int, int]] = []
    for quote in _SHORT_QUOTE.finditer(sentence):
        whole: bool = quote.start() <= first and quote.end() >= last - 1
        if not whole:
            spans.append((quote.start(), quote.end()))
    return spans


def _clause_bounds(sentence: str, index: int) -> tuple[int, int]:
    """Der Satzteil zwischen Kommata und Segmentgrenzen, der `index` enthaelt.

    Vorbedingung: 0 <= index <= len(sentence).
    Nachbedingung: (Anfang, Ende) mit Anfang <= index <= Ende.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    start, end = 0, len(sentence)
    protected: list[tuple[int, int]] = _protected_spans(sentence)
    for mark in _CLAUSE_MARK.finditer(sentence):
        if any(a < mark.start() < b for a, b in protected):
            continue
        if mark.end() <= index:
            start = mark.end()
        elif mark.start() >= index:
            end = mark.start()
            break

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if not start <= index <= end:  # pragma: no cover — per Konstruktion
        logger.error(
            "Speicherbehauptung: Satzteil %d–%d enthaelt Stelle %d nicht",
            start, end, index,
        )
    return start, end


def _is_question(sentence: str, index: int) -> bool:
    """Liegt `index` in einem Segment, das mit einem Fragezeichen endet?

    Vorbedingung: `index` liegt im Satz.
    Nachbedingung: True, wenn das Segment eine Frage ist. Segmente trennen an
    Gedankenstrich, Semikolon und Doppelpunkt: *„Notiert — passt dir
    das?"* ist im ersten Segment keine Frage.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    start: int = 0
    protected: list[tuple[int, int]] = _protected_spans(sentence)
    for mark in _SEGMENT_MARK.finditer(sentence):
        if any(a < mark.start() < b for a, b in protected):
            continue
        if mark.start() >= index:
            return sentence[start:mark.start()].rstrip(_QUOTE_TAIL).endswith("?")
        start = mark.end()
    return sentence[start:].rstrip(_QUOTE_TAIL).endswith("?")


def _is_conditional(sentence: str, clause_start: int, index: int) -> bool:
    """Steht die Stelle unter einer Bedingung, einem Angebot oder einer Absicht?

    Vorbedingung: clause_start <= index.
    Nachbedingung: True bei einem Bedingungswort im Satzteil vor der Stelle,
    oder bei *„dann"* dort, wenn im selben Satz vorher ein Aufruf an den
    Nutzer steht.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    prefix: str = sentence[clause_start:index]
    if _CONDITION.search(prefix) or _CONDITION_DAMIT.search(prefix):
        return True
    if _THEN.search(prefix):
        return bool(_IMPERATIVE.search(sentence[:clause_start]))
    return False


def _excluded(sentence: str, clause_start: int, index: int) -> bool:
    """Verneinung, Bedingung oder Frage vor der Stelle im Satzteil?

    Vorbedingung: clause_start <= index <= len(sentence).
    Nachbedingung: True, wenn die Stelle keine Behauptung sein kann.
    """
    return bool(
        _NEGATION.search(sentence[clause_start:index])
        or _is_conditional(sentence, clause_start, index)
        or _is_question(sentence, index)
    )


def _claim(sentence: str, form: str, word: str) -> StorageClaim:
    """Baut den Befund; kuerzt den Satz auf `_MAX_SENTENCE` Zeichen.

    Vorbedingung: `sentence` ist der bereinigte Satz, `form` eine der vier
    Formen, `word` das tragende Wort — alles vom Aufrufer bestimmt.
    Nachbedingung: `sentence` im Befund ist hoechstens `_MAX_SENTENCE` Zeichen
    lang und endet bei einer Kuerzung auf `…`; `word` ist kleingeschrieben.
    """
    shown: str = sentence if len(sentence) <= _MAX_SENTENCE else f"{sentence[:_MAX_SENTENCE - 1]}…"
    return StorageClaim(sentence=shown, form=form, word=word.lower())


# ─────────────────────────────────────────────────────────────────────────
# Die vier Formen
# ─────────────────────────────────────────────────────────────────────────

def _short_claim(sentence: str) -> StorageClaim | None:
    """Die kurze Bestaetigung als ganzer Satzteil.

    *„Notiert."*, *„Alles klar, ist erledigt."*

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `kurz` oder None. Nur ein Satzteil, der
    aus nichts anderem besteht als der Bestaetigung, zaehlt — und nur, wenn
    vorher im Satz kein Gedankenspiel steht: *„Ich stelle mir das wie ein
    Archiv vor: alles gespeichert"* bestaetigt nichts.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    offset: int = 0
    for part in _SHORT_SPLIT.split(sentence):
        position: int = sentence.find(part, offset)
        offset = max(offset, position + len(part))
        core: str = re.sub(r"[^\wäöüÄÖÜß ]", " ", part)
        core = re.sub(r"\s+", " ", core).strip()
        hit = _SHORT.match(core)
        if hit is None:
            continue
        if _CONDITION.search(sentence, 0, max(position, 0)):
            continue
        return _claim(sentence, "kurz", hit.group("part"))
    return None


def _first_person_claim(sentence: str) -> StorageClaim | None:
    """Die erste Person im Perfekt: *„Ich habe den Termin eingetragen"*.

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `erste_person` oder None. Ein
    mehrdeutiges Partizip braucht einen Bezug im Satzteil; Verneinung,
    Bedingung und Frage schliessen aus.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    for aux in _FIRST_PERSON_AUX.finditer(sentence):
        clause_start, clause_end = _clause_bounds(sentence, aux.start())
        for hit in _FIRST_PERSON_PARTICIPLE.finditer(sentence, aux.end(), clause_end):
            if _excluded(sentence, clause_start, hit.start()):
                break
            word: str = hit.group(0).lower()
            if word in WEAK and not _CUE_WIDE.search(sentence, clause_start, clause_end):
                continue
            return _claim(sentence, "erste_person", word)
    return None


def _stands_claim(sentence: str) -> StorageClaim | None:
    """Der Zustand ohne Partizip: *„steht jetzt fest in der Timeline"*.

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `zustand` oder None.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    stands = _STANDS_IN_STORE.search(sentence) or _REMAINS_IN_STORE.search(sentence)
    if stands is None:
        return None
    clause_start, _ = _clause_bounds(sentence, stands.start())
    if _excluded(sentence, clause_start, stands.end()):
        return None
    return _claim(sentence, "zustand", "steht in")


def _aux_state_claim(sentence: str) -> StorageClaim | None:
    """Hilfsverb vor dem Partizip: *„Morgen um 10 Uhr ist notiert"*.

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `zustand` oder None. Eine Person als
    Satzgegenstand (*„Wir sind hier sicher verankert"*) schliesst aus, ebenso
    Verneinung, Bedingung und Frage.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    for aux in _STATE_AUX.finditer(sentence):
        if (aux.group("subj") or "").lower() in _PERSONS:
            continue
        clause_start, clause_end = _clause_bounds(sentence, aux.end())
        for hit in _STATE_PARTICIPLE.finditer(sentence, aux.end(), clause_end):
            if _excluded(sentence, clause_start, hit.start()):
                break
            word: str = hit.group(0).lower()
            if word not in STRONG and not _CUE.search(sentence, clause_start, clause_end):
                continue
            return _claim(sentence, "zustand", word)
    return None


def _subordinate_claim(sentence: str) -> StorageClaim | None:
    """Nebensatz mit dem Hilfsverb am Ende: *„dass der Termin in der Timeline eingeplant ist"*.

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `zustand` oder None. Bedingung, Wunsch,
    Vermutung und Verneinung gelten hier fuer den ganzen Satz davor: *„Du
    moechtest, dass der Termin eingetragen ist"* ist ein Wunsch. Als Bezug
    zaehlt nur ein Speicherort.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    for hit in _PARTICIPLE_THEN_AUX.finditer(sentence):
        clause_start, clause_end = _clause_bounds(sentence, hit.start())
        blocked: bool = bool(
            not _SUBORDINATE.search(sentence, clause_start, hit.start())
            or _CONDITION.search(sentence, 0, hit.start())
            or _EPISTEMIC.search(sentence, 0, hit.start())
            or _NEGATION.search(sentence, 0, hit.start())
            or _is_question(sentence, hit.start())
            or not _CUE_SUBORDINATE.search(sentence, clause_start, clause_end)
        )
        if not blocked:
            return _claim(sentence, "zustand", hit.group("part"))
    return None


def _state_claim(sentence: str) -> StorageClaim | None:
    """Der Zustandssatz in seinen drei Stellungen.

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `zustand` oder None.
    """
    return _stands_claim(sentence) or _aux_state_claim(sentence) or _subordinate_claim(sentence)


def _present_claim(sentence: str, condition: re.Match | None) -> StorageClaim | None:
    """Der Vollzug in der Gegenwart: *„dann reserviere ich zwei Stunden"*.

    Vorbedingung: `sentence` ist ein bereinigter Satz; `condition` ist der erste
    Treffer von `_CONDITION` im ganzen Satz oder None.
    Nachbedingung: ein Befund der Form `vollzug` oder None. Eine abgetrennte
    Partikel muss am Satzteilende stehen, ein mehrdeutiges Verb braucht einen
    Bezug.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    for hit in _PERFORMATIVE_VERB.finditer(sentence):
        verb: str = (hit.group("v1") or hit.group("v2")).lower()
        particle, needs_cue = PERFORMATIVE[verb]
        clause_start, clause_end = _clause_bounds(sentence, hit.start())
        particle_ok: bool = not particle or bool(re.compile(
            rf"\b{particle}\b{_PARTICLE_END}", re.IGNORECASE
        ).search(sentence, hit.end(), clause_end))
        blocked: bool = (
            (condition is not None and condition.start() < hit.start())
            or _excluded(sentence, clause_start, hit.start())
            or bool(_NEGATION.search(sentence, hit.end(), clause_end))
        )
        cue_ok: bool = not needs_cue or bool(
            _CUE_WIDE.search(sentence, clause_start, clause_end)
        )
        if particle_ok and cue_ok and not blocked:
            return _claim(sentence, "vollzug", verb)
    return None


def _future_claim(sentence: str, condition: re.Match | None) -> StorageClaim | None:
    """Der Vollzug in der Zukunft: *„ich werde das einzeichnen"*.

    Vorbedingung: wie `_present_claim`.
    Nachbedingung: ein Befund der Form `vollzug` oder None.
    """
    # ── Verarbeitung ─────────────────────────────────────────────────
    for aux in _FUTURE_AUX.finditer(sentence):
        clause_start, clause_end = _clause_bounds(sentence, aux.start())
        infinitive = _FUTURE_INFINITIVE.search(sentence, aux.end(), clause_end)
        if infinitive is None:
            continue
        word: str = infinitive.group(0).lower()
        blocked: bool = (
            (condition is not None and condition.start() < aux.start())
            or _excluded(sentence, clause_start, infinitive.start())
        )
        cue_ok: bool = not FUTURE[word] or bool(
            _CUE_WIDE.search(sentence, clause_start, clause_end)
        )
        if cue_ok and not blocked:
            return _claim(sentence, "vollzug", word)
    return None


def _performative_claim(sentence: str) -> StorageClaim | None:
    """Der Vollzug in Gegenwart oder Zukunft.

    Vorbedingung: `sentence` ist ein bereinigter Satz.
    Nachbedingung: ein Befund der Form `vollzug` oder None. Eine Bedingung
    **irgendwo vor** dem Verb schliesst hier aus, nicht nur im Satzteil:
    *„Stell dir vor: Anstatt alles zu löschen, speichern wir jeden Moment"* ist
    ein Gedankenspiel, keine Handlung.
    """
    condition = _CONDITION.search(sentence)
    return _present_claim(sentence, condition) or _future_claim(sentence, condition)


# ─────────────────────────────────────────────────────────────────────────
# Die oeffentliche Pruefung
# ─────────────────────────────────────────────────────────────────────────

def find_storage_claims(text: str) -> list[StorageClaim]:
    """Findet die Saetze einer Antwort, die eine Speicherhandlung behaupten.

    Vorbedingung: `text` ist die fertige Antwort. Ein anderer Typ wird laut
    gemeldet und ergibt eine leere Liste — eine Pruefung darf den Antwortpfad
    nicht anhalten.

    Nachbedingung: hoechstens ein Befund je Satz, in der Reihenfolge der
    Antwort. Leere Liste heisst: keine Behauptung in einer der vier Formen.
    **Es heisst nicht, dass der Text keine enthaelt** — die Wortliste ist am
    Bestand vom 27.07. bis 14.09.2026 geeicht und kennt nur dessen Wortlaut.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not isinstance(text, str):
        logger.error(
            "Speicherbehauptung: text ist %s statt str — keine Pruefung",
            type(text).__name__,
        )
        return []
    if not text.strip():
        return []

    # ── Verarbeitung ─────────────────────────────────────────────────
    sentences: list[str] = _sentences(_plain_text(text))
    claims: list[StorageClaim] = []
    for sentence in sentences:
        claim = (
            _short_claim(sentence)
            or _first_person_claim(sentence)
            or _state_claim(sentence)
            or _performative_claim(sentence)
        )
        if claim is not None:
            claims.append(claim)

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if len(claims) > len(sentences):  # pragma: no cover — per Konstruktion
        logger.error(
            "Speicherbehauptung: %d Befunde bei %d Saetzen — die Zaehlung ist "
            "unmoeglich, Ergebnis verworfen", len(claims), len(sentences),
        )
        return []
    return claims


@dataclass(frozen=True)
class ClaimCheck:
    """Das Ergebnis der Pruefung gegen die Dienste eines Turns."""

    claims: tuple[StorageClaim, ...]     # alle Behauptungen der Antwort
    completed: tuple[str, ...]           # Dienste mit Ausgang `abgeschlossen`
    outcomes: tuple[str, ...]            # alle Ausgaenge als `dienst:status`

    @property
    def uncovered(self) -> bool:
        """Behauptet die Antwort etwas, das kein Dienst dieses Turns deckt?"""
        return bool(self.claims) and not self.completed

    @property
    def result(self) -> str:
        """Der Name des Ausgangs fuer den dauerhaften Eintrag."""
        if not self.claims:
            return "keine_behauptung"
        return "gedeckt" if self.completed else "nicht_belegt"


def uncovered_claims(response: str, agent_results: list | None) -> ClaimCheck:
    """Haelt die Behauptungen der Antwort gegen die Dienst-Ergebnisse des Turns.

    **Nur `abgeschlossen` deckt.** Was ein Dienst abgelehnt, mit Fehler beendet
    oder als Rueckfrage zurueckgegeben hat, wurde nicht geschrieben.

    **Die Deckung ist grob, und das ist benannt:** Jeder abgeschlossene Dienst
    deckt jede Behauptung — auch ein abgeschlossener *Lesevorgang* eine
    behauptete Schreibung. Eine feinere Zuordnung braucht die Art der Aktion
    im Ergebnis, die heute nicht jeder Dienst meldet. Umgekehrt meldet die
    Pruefung die **Wiederholung** einer frueheren, echten Schreibung (*„10 Uhr
    ist fixiert"* einen Turn nach dem Anlegen) als nicht belegt — sie sieht nur
    diesen Turn. Der Korrekturauftrag ist darauf zugeschnitten
    (`correction_order`). **Und Bestand, den der Turn ohne Dienst gelesen hat**
    (Enricher, Werkzeuge des Thinkers), deckt nichts: Ein wahrer Satz ueber ihn
    schlaegt an wie eine Behauptung.

    Vorbedingung: `agent_results` ist eine Liste von Ergebnisobjekten mit
    `agent_name` und `status`, leer oder None. Ein anderer Typ wird laut
    gemeldet und als leer behandelt.
    Nachbedingung: ein `ClaimCheck`; `uncovered` ist genau dann wahr, wenn die
    Antwort mindestens eine Behauptung traegt und kein Dienst abgeschlossen hat.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    results: list = []
    if isinstance(agent_results, list):
        results = agent_results
    elif agent_results is not None:
        logger.error(
            "Speicherbehauptung: agent_results ist %s statt list — als leer "
            "behandelt, die Pruefung urteilt dadurch strenger",
            type(agent_results).__name__,
        )

    # ── Verarbeitung ─────────────────────────────────────────────────
    claims: tuple[StorageClaim, ...] = tuple(find_storage_claims(response or ""))
    completed: tuple[str, ...] = tuple(
        str(getattr(r, "agent_name", "unbekannt")) for r in results
        if getattr(r, "status", "") == "abgeschlossen"
    )
    outcomes: tuple[str, ...] = tuple(
        f"{getattr(r, 'agent_name', 'unbekannt')}:{getattr(r, 'status', 'unbekannt')}"
        for r in results
    )

    # ── Ausgabe-Verifikation ─────────────────────────────────────────
    if len(completed) > len(outcomes):  # pragma: no cover — per Konstruktion
        logger.error(
            "Speicherbehauptung: %d abgeschlossene bei %d Ausgaengen — "
            "unmoeglich", len(completed), len(outcomes),
        )
    return ClaimCheck(claims=claims, completed=completed, outcomes=outcomes)


def correction_order(claims: list[StorageClaim] | tuple[StorageClaim, ...]) -> str:
    """Der Korrekturauftrag zur Speicherbehauptung ohne Schreibung.

    Vorbedingung: `claims` ist nicht leer — geprueft beim Aufrufer.
    Nachbedingung: nicht-leerer Text mit der Kopfzeile `ORDER_HEADER`, jedem
    beanstandeten Satz im Wortlaut und der Richtung der Korrektur.

    **Der Auftrag gibt die Form vor, statt Woerter zu verbieten.** Gemessen am
    15.09.2026 in der echten Korrekturrunde: Ein Auftrag, der untersagte, etwas
    *„als notiert, eingetragen oder gespeichert"* zu melden, bekam in 6 von 24
    Faellen dieselbe Aussage in einem anderen Wort zurueck — *gelistet*,
    *angesetzt*, *erfasst*, *geoeffnet* —, und die Pruefung sah sie nicht mehr.
    Die sauberen Fassungen hatten fast alle eine Form: die Wiedergabe des
    Wunsches. Die gibt der Auftrag jetzt vor.

    **Die Form ist in zwei von drei Lagen wahr, und die dritte ist benannt.**
    Diese Pruefung sieht nur den laufenden Turn. *„Du hast … genannt"* stimmt,
    wenn die Behauptung erfunden ist, und auch dann, wenn ein frueherer Turn den
    Termin nach einem Auftrag tatsaechlich angelegt hat. **Es stimmt nicht fuer
    Bestand, den der Turn ueber einen Leseweg ohne Dienst kennt** — die
    Timeline im Enricher, die Notizen, die Werkzeuge des Thinkers: Beschreibt
    die Antwort ihn wahrheitsgemaess im Zustandssatz, schlaegt die Pruefung an,
    und der Auftrag legt dem Nutzer etwas in den Mund, das er nicht gesagt hat.
    Gefunden von der zweiten Kontrolle am 15.09.2026; im Bestand ab 14.08.2026
    kein solcher Anschlag in 928 Turns, davor drei ohne bekannte Dienst-Ausgaenge.
    Nicht gemessen, ohne Zeugen.

    Ein Auftrag *„sag, dass nichts gespeichert ist"* waere keine Abhilfe: Er
    machte aus der Wiederholung einer echten Schreibung die naechste falsche
    Aussage, in der Gegenrichtung. Der Auftrag bietet auch nichts an: Ob Nova
    anbietet einzutragen, haengt an ihrem Pflichtbewusstsein und ist nicht Sache
    dieser Pruefung.
    """
    # ── Eingabe-Validierung ──────────────────────────────────────────
    if not claims:
        logger.error("Korrekturauftrag Speicherbehauptung ohne Befund angefordert — leer")
        return ""

    # ── Verarbeitung ─────────────────────────────────────────────────
    lines: list[str] = [
        f"{ORDER_HEADER} — diese Saetze melden etwas als bereits erledigt, "
        "aber in diesem Turn hat kein Dienst etwas gespeichert oder veraendert:",
        *(f"  - {c.line()}" for c in claims),
        "Schreibe jeden dieser Saetze als Wiedergabe dessen, was der Nutzer "
        "gesagt oder sich gewuenscht hat — in der Form „Du moechtest …\" oder "
        "„Du hast … genannt\". Der Satz handelt vom Wunsch des Nutzers, nicht "
        "von dem, was daraus geworden ist. Aendere sonst nichts.",
    ]
    return "\n".join(lines)


# Scheibe 12 A, Punkt 1 (entschieden am 16.09.2026): Uebersteht eine
# Speicherbehauptung beide Korrekturrunden, wird sie nicht entfernt, sondern
# ein Korrektursatz angehaengt — gerechnet, nicht erbeten. Der Wortlaut folgt
# dem Vorschlag des Eigentuemers (*"Korrektur: Agent hat keinen Eintrag
# erstellt" oder aehnlich*): sachlich, ohne Entschuldigung, und er nennt, was
# stimmt — gespeichert ist nichts.
CORRECTION_NOTE: str = "(Korrektur: Dafuer wurde kein Eintrag angelegt — gespeichert ist davon nichts.)"


def append_correction(response: str) -> str:
    """Haengt den Korrektursatz an eine Antwort, die eine Speicherbehauptung behielt.

    Vorbedingung: `response` ist die Antwort nach der letzten Korrekturrunde.
    Nachbedingung: die Antwort mit dem Korrektursatz am Ende, durch eine
        Leerzeile getrennt — **genau einmal**: Steht er schon da, bleibt die
        Antwort unveraendert. Der behauptende Satz bleibt stehen; entfernt
        wird nichts, denn ohne Bestandsabgleich ist er nicht als falsch belegt.
    """
    if not isinstance(response, str):
        logger.error("Korrektursatz: Antwort ist %s statt str — unveraendert", type(response).__name__)
        return response
    if CORRECTION_NOTE in response:
        return response
    return f"{response.rstrip()}\n\n{CORRECTION_NOTE}"
