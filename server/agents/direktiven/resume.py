"""Deutung der Antwort auf eine Rueckfrage der Direktiven -- das Tor vor dem Schreiben.

Der Dienst fragt vor jeder Schreiboperation nach (`crud.validieren_gegen_db`).
Kommt die Antwort mit `resume` zurueck, liest dieser Knoten sie, bevor etwas
ausgefuehrt wird:

  - **Ablehnung** (zuerst geprueft, sie gewinnt): nichts wird ausgefuehrt,
    der Lauf endet mit einem Satz, dass nichts geaendert wurde.
  - **Zustimmung**, nur wenn die Antwort aus nichts als Zustimmung besteht
    (`_consists_of_consent`): der Lauf geht weiter zu `ausfuehren`, mit der
    Aktion, nach der gefragt wurde.
  - **unklar**, alles andere: dieselbe Frage noch einmal; den Pending-Zustand
    erneuert `dispatch._handle_resume`. Unklar ist damit jede Antwort, die
    etwas zurueckhaelt, aufschiebt oder ein unbekanntes Wort traegt
    (*„Ja? :)“*, *„Sekündchen, bitte“*, *„ja, aber erst morgen“*).

Eine Auswahlfrage (*„Welche soll ich ...?“*) ist keine Ja/Nein-Frage: Eine
Ablehnung beendet sie, jede andere Antwort stellt sie erneut -- keine Antwort
fuehrt dort etwas aus, weil die Wahl aus der Antwort nicht gelesen wird.
"""

import logging
import re
from collections.abc import Sequence

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.direktiven.resume")

# Kopie aus `agents/notizen/resume.py` (dort mit den Faellen, an denen die
# Deutung schon falsch lag); bewusst kein gemeinsames Modul.
# Stamm einer Ablehnung, gesucht als Teilzeichenkette: *keinesfalls*,
# *mitnichten*, *lasst*, *abbrechen*, *ablehnen*, *ohne* lehnen so ab, ohne
# dass jede Form einzeln dasteht. Zu weit ist die sichere Richtung. Gesucht
# wird im Text ohne die Zustimmungswoerter (`CONSENT_WORDS`) -- so trifft
# `"ne"` *gerne* und *meinetwegen* nicht.
REFUSAL_STEMS: tuple[str, ...] = (
    "nein", "ne", "nee", "nicht", "kein", "lass", "abbruch", "abbrech", "stopp", "stop",
)

# Kopie aus `agents/notizen/resume.py`. Zustimmung, gezaehlt als ganzes Wort:
# `"ja"` trifft *Jahr* nicht; die Formen (`jawohl`, `machs` ...) stehen
# deshalb einzeln da.
CONSENT_WORDS: tuple[str, ...] = (
    "ja", "jap", "jau", "jawohl", "klar", "klaro", "mach", "machs", "mache", "bitte",
    "okay", "ok", "gerne", "meinetwegen", "sure", "jep", "jepp", "jop", "jopp",
    "auf jeden", "logo", "passt",
)

# Kopie in den vier Ja/Nein-Deutungen (`direktiven`, `notizen`,
# `charakter_identitaet`, `dateien_wurzeln`), bewusst kein gemeinsames Modul.
# **Hier wird geschlossen angenommen:** Zugestimmt hat nur, wer nichts als
# Zustimmung sagt -- jedes Wort steht in `CONSENT_WORDS` oder hier. Was
# zurueckhaelt, ablehnt oder aufschiebt, ist eine offene Klasse; jede Liste
# davon liess die naechste Form durch (*„Sekündchen, bitte“*, *„wait, ok“*,
# *„ja, aber erst morgen“* loeschten). Die Zustimmung ist geschlossen, und ein
# Wort, das hier fehlt, kostet eine zweite Frage, nie eine Ausfuehrung.
# Die Regel der Menge: Artikel, Pronomen, das Hilfsverb *ist*, Partikeln, die
# nicht zoegern, und *danke*. Nie darin: ein Verb, ein Nomen, eine Zahl, ein
# Fragewort (*wie*, *was*), eine Partikel des Zoegerns (*na*, *nun*, *also*
# -- *„na ja“* ist keine Zustimmung), ein Wort der Einschraenkung oder des
# Aufschubs (*aber*, *sondern*, *statt*, *erst*, *nur*, *noch*, *lieber*,
# *spaeter*, *morgen*) oder ein Wort mit einem Stamm aus `REFUSAL_STEMS`.
# Abgeloest wird diese Deutung mit den Klaerfaellen (`KLA-KLAERFALL-AM-OBJEKT`,
# Schritte 5 und 6).
FILLER_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "den", "dem", "des", "ein",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "mich", "dich", "sich", "uns", "euch",
    "mir", "dir", "ihm", "ihn", "man",
    "dies", "diese", "dieses", "diesen", "dieser", "diesem",
    "ist",
    "mal", "doch", "ruhig", "sehr",
    "danke",
})

# Das Apostroph faellt ohne Luecke weg (*mach's* ist *machs*).
_APOSTROPHES: str = "['’‘`´]"

# **Auch die Zeichen werden geschlossen angenommen:** Ausser Buchstaben,
# Ziffern und dem Apostroph darf in einer Zustimmung nur stehen, was hier
# steht -- ASCII-Leerraum und die Satzzeichen, mit denen *„Ja!“* und
# *„Ja :)“* zustimmen. Jedes andere Zeichen macht die Antwort unklar: jedes
# Fragezeichen jeder Schrift (*„ja？“*, *„ja¿“*, *„ja ❓“*), jedes Emoji
# (*„ja 👎“*, *„ja 🤔“*), jedes Symbol. Eine Liste der Zeichen, die
# zurueckhalten, liesse wie jede Liste der Woerter das naechste durch; ein
# Zeichen, das hier fehlt, kostet eine zweite Frage. `?` steht nie darin.
DROPPED_SIGNS: frozenset[str] = frozenset(" \t\n\r\f\v.,!;:-()")

# **Die Frage ohne `?` wird an der Wortstellung erkannt:** Eine deutsche
# Ja/Nein-Frage stellt das finite Verb vor sein Subjekt (*„ist das ok“*,
# *„passt es“*), die Aussage stellt es dahinter (*„das ist ok“*, *„es
# passt“*). In der geschlossenen Menge ist die Wortstellung das einzige
# Merkmal, das eine Frage ohne `?` traegt; Fragewoerter kennt die Menge nicht.
# Eine Antwort mit einem Verb aus `ASKING_VERBS` und dahinter, im selben
# Satzteil, einem Wort aus `SUBJECT_WORDS` ist deshalb unklar.
# Fragend sind die Verben der Zustimmungs- und Fuellwoerter, die finit und
# kein Imperativ sind: *ist*, *passt*. Nicht darin: der Imperativ der
# Zustimmung (*mach*, *machs*, *mache* -- *„mach das“* stimmt zu, *„mach
# ich“* bleibt Selbstaussage) und die Formel *danke*.
ASKING_VERBS: frozenset[str] = frozenset({"ist", "passt"})
# Die Fuellwoerter, die Subjekt sein koennen -- im Nominativ stehen koennen.
# Nicht darin: was nur Dativ, Akkusativ oder Genitiv ist (*den*, *dem*,
# *des*, *mich*, *mir*, *ihn*, *uns*, *diesen* ...).
SUBJECT_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "ein",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "dies", "diese", "dieses", "dieser",
})
# Die Zeichen, an denen ein Satzteil endet: Ein Subjekt gehoert zum Satz
# seines Verbs, *„passt, mach das“* stimmt zu. `- ( )` und Leerraum trennen
# nicht -- *„ist - das ok“* und *„ist (das) ok“* fragen. Ein Zeichen mehr
# hier liesse eine Frage als zwei Satzteile durch.
CLAUSE_SEPARATORS: frozenset[str] = frozenset(",.!;:")

# Die drei Ja/Nein-Fragen aus `crud.validieren_gegen_db`, erkannt am Wortlaut,
# den der Mensch gesehen hat: Pflicht-Rueckfrage, Duplikat, Auto-Korrektur.
YES_NO_PREFIXES: tuple[str, ...] = ("Soll ich das ausfuehren? ",)
YES_NO_SUFFIXES: tuple[str, ...] = (
    "Trotzdem anlegen?",
    "Soll ich die wiederherstellen statt eine neue anzulegen?",
)
# Die Auswahlfragen aus `crud.validieren_gegen_db`, `crud._delete` und
# `crud._reactivate`.
CHOICE_SUFFIXES: tuple[str, ...] = (
    "Welche soll ich wiederherstellen?",
    "Welche soll ich entfernen?",
)

REFUSED_TEXT: str = "Gut, dann lasse ich es. An deinen Direktiven ist nichts geaendert."

_READINGS: frozenset[str] = frozenset({"refusal", "consent", "unclear"})
_STATUSES: frozenset[str] = frozenset({"laufend", "abgeschlossen", "rueckfrage", "fehler"})


def _has_word(text: str, words: Sequence[str]) -> bool:
    r"""Prueft, ob der Text eines der Woerter **als ganzes Wort** enthaelt.

    Vorbedingung: `text` und `words` stehen in derselben Schreibung (der
    Aufrufer senkt beide); `words` ist nicht leer und traegt kein leeres Wort.
    Nachbedingung: True nur bei einem Treffer, vor und hinter dem kein
    Buchstabe und keine Ziffer steht -- `"ja"` trifft *Jahr* nicht.
    Fehlerfaelle: eine leere Wortliste oder ein leeres Wort wirft
    `ValueError` -- ein leeres Wort traefe an jeder Stelle.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words or any(not word for word in words):
        msg: str = f"_has_word: leere Wortliste oder leeres Wort in {list(words)!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    hit: bool = any(re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) for word in words)

    # ── Ausgabe-Verifikation ────────────────────
    # Ein Treffer an Wortgrenzen ist immer auch einer als Teilzeichenkette.
    if hit and not any(word in text for word in words):
        msg = f"_has_word: Worttreffer ohne Teilzeichenkette in {text!r}"
        raise RuntimeError(msg)
    return hit


def _has_stem(text: str, stems: Sequence[str]) -> bool:
    """Prueft, ob einer der Staemme irgendwo im Text steht, auch mitten im Wort.

    Vorbedingung: `text` ist kleingeschrieben; `stems` ist nicht leer und
    traegt nur kleingeschriebene, nicht leere Staemme.
    Nachbedingung: True, sobald ein Stamm als Teilzeichenkette vorkommt --
    `"kein"` trifft *keinesfalls*.
    Fehlerfaelle: ein Text mit Grossbuchstaben, eine leere Liste oder ein
    leerer oder grossgeschriebener Stamm wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if text != text.lower():
        msg: str = f"_has_stem: Text nicht kleingeschrieben: {text!r}"
        raise ValueError(msg)
    if not stems or any(not stem or stem != stem.lower() for stem in stems):
        msg = f"_has_stem: leere Liste oder ungueltiger Stamm in {list(stems)!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    hit: bool = any(stem in text for stem in stems)

    # ── Ausgabe-Verifikation ────────────────────
    if hit and len(text) < min(len(stem) for stem in stems):
        msg = f"_has_stem: Treffer in zu kurzem Text {text!r}"
        raise RuntimeError(msg)
    return hit


def _without_words(text: str, words: Sequence[str]) -> str:
    """Nimmt die Woerter **als ganze Woerter** aus dem Text; an ihrer Stelle bleibt Leerraum.

    Vorbedingung: `text` und `words` stehen in derselben Schreibung; `words`
    ist nicht leer und traegt kein leeres Wort.
    Nachbedingung: Der Rest traegt keines der Woerter mehr als ganzes Wort;
    alles andere steht unveraendert da.
    Fehlerfaelle: eine leere Wortliste oder ein leeres Wort wirft `ValueError`.

    So sucht die Ablehnung ihre Staemme nicht in der Zustimmung selbst:
    `"ne"` steckt in *gerne* und *meinetwegen*.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words or any(not word for word in words):
        msg: str = f"_without_words: leere Wortliste oder leeres Wort in {list(words)!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    alternatives: str = "|".join(re.escape(word) for word in words)
    rest: str = re.sub(rf"(?<!\w)(?:{alternatives})(?!\w)", " ", text)

    # ── Ausgabe-Verifikation ────────────────────
    if _has_word(rest, words):
        msg = f"_without_words: Rest {rest!r} traegt noch ein Wort aus {list(words)!r}"
        raise RuntimeError(msg)
    return rest


def _asks_by_word_order(joined: str) -> bool:
    """Prueft, ob die Antwort durch ihre Wortstellung fragt -- finites Verb vor seinem Subjekt.

    Vorbedingung: `joined` ist kleingeschrieben, das Apostroph ist entfernt.
    Nachbedingung: True, wenn in einem Satzteil (getrennt an den Zeichen
    aus `CLAUSE_SEPARATORS`) ein Wort aus `ASKING_VERBS` steht und irgendwo
    dahinter ein Wort aus `SUBJECT_WORDS` -- *„ist das ok“*, *„passt es“*,
    *„passt dir das“*, *„ist - das ok“*. *„das ist ok“*, *„es passt“* und
    *„passt, mach das“* fragen nicht.
    Fehlerfaelle: ein Text mit Grossbuchstaben wirft `ValueError`. Steht ein
    fragendes Verb nicht unter den Zustimmungs- und Fuellwoertern, ein
    Subjekt nicht unter den Fuellwoertern oder ein Trennzeichen nicht unter
    `DROPPED_SIGNS`, kann es in keiner Zustimmung stehen -- die Listen
    widersprechen sich, es wird `RuntimeError` geworfen; ebenso bei leeren
    Trennzeichen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if joined != joined.lower():
        msg: str = f"_asks_by_word_order: Text nicht kleingeschrieben: {joined!r}"
        raise ValueError(msg)
    if not ASKING_VERBS <= set(CONSENT_WORDS) | FILLER_WORDS or not SUBJECT_WORDS <= FILLER_WORDS:
        msg = "_asks_by_word_order: fragendes Verb oder Subjekt ausserhalb der Zustimmung"
        raise RuntimeError(msg)
    if not CLAUSE_SEPARATORS or not CLAUSE_SEPARATORS <= DROPPED_SIGNS:
        msg = f"_asks_by_word_order: Trennzeichen ungueltig: {sorted(CLAUSE_SEPARATORS)!r}"
        raise RuntimeError(msg)

    # ── Verarbeitung ────────────────────────────
    separators: str = re.escape("".join(sorted(CLAUSE_SEPARATORS)))
    clauses: list[list[str]] = [
        re.findall(r"\w+", clause) for clause in re.split(rf"[{separators}]", joined)
    ]
    asks: bool = any(
        word in ASKING_VERBS and not SUBJECT_WORDS.isdisjoint(words[index + 1:])
        for words in clauses
        for index, word in enumerate(words)
    )

    # ── Ausgabe-Verifikation ────────────────────
    # Eine Frage nach der Wortstellung braucht ein fragendes Verb und ein
    # Subjekt, also mindestens zwei Woerter.
    words_of_answer: list[str] = re.findall(r"\w+", joined)
    if asks and (ASKING_VERBS.isdisjoint(words_of_answer) or len(words_of_answer) < 2):
        msg = f"_asks_by_word_order: Frage ohne fragendes Verb und Subjekt in {joined!r}"
        raise RuntimeError(msg)
    return asks


def _consists_of_consent(lowered: str) -> bool:
    """Prueft, ob die Antwort aus nichts als Zustimmung besteht -- die geschlossene Annahme.

    Vorbedingung: `lowered` ist ein kleingeschriebener String (auch leer);
    die Ablehnung prueft der Aufrufer vorher.
    Nachbedingung: True nur, wenn (a) jedes Zeichen ausser Buchstaben,
    Ziffern und Apostroph in `DROPPED_SIGNS` steht -- kein `?`, kein
    Fragezeichen einer anderen Schrift, kein Emoji, kein Symbol --, (b)
    mindestens ein Wort aus `CONSENT_WORDS` dasteht, (c) jedes andere Wort
    in `FILLER_WORDS` steht und (d) die Wortstellung nicht fragt
    (`_asks_by_word_order`: kein fragendes Verb vor einem Subjekt). Das
    Apostroph faellt ohne Luecke weg: *„Ja :)“*, *„Ja, bitte!“*,
    *„mach's“* und *„das ist ok“* stimmen zu, *„Wie bitte?“*, *„ja？“*,
    *„ja 👎“*, *„na ja“*, *„Moment, bitte“*, *„ist das ok“* und
    *„ok, ich überleg noch“* nicht.
    Fehlerfaelle: ein Text mit Grossbuchstaben wirft `ValueError`. Traegt
    eine Zustimmung ein `?` (dann traegt es `DROPPED_SIGNS`) oder ausserhalb
    der Zustimmungswoerter einen Ablehnungsstamm (dann steht er in einem
    Fuellwort) -- die Listen widersprechen sich --, wird `RuntimeError`
    geworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if lowered != lowered.lower():
        msg: str = f"_consists_of_consent: Text nicht kleingeschrieben: {lowered!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    joined: str = re.sub(_APOSTROPHES, "", lowered)
    rest: str = _without_words(joined, CONSENT_WORDS)
    consents: bool = (
        all(sign in DROPPED_SIGNS for sign in re.sub(r"\w", "", joined))
        and _has_word(joined, CONSENT_WORDS)
        and all(word in FILLER_WORDS for word in re.findall(r"\w+", rest))
        and not _asks_by_word_order(joined)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if consents and "?" in joined:
        msg = f"_consists_of_consent: `?` in einer Zustimmung: {lowered!r}"
        raise RuntimeError(msg)
    if consents and _has_stem(rest, REFUSAL_STEMS):
        msg = f"_consists_of_consent: Fuellwort mit Ablehnungsstamm in {lowered!r}"
        raise RuntimeError(msg)
    return consents


def _reading(answer: str) -> str:
    """Deutet eine Antwort als Ablehnung, Zustimmung oder unklar.

    Vorbedingung: `answer` ist ein String (auch leer).
    Nachbedingung: genau einer von `"refusal"`, `"consent"`, `"unclear"`.
    Die Ablehnung wird zuerst geprueft und gewinnt, wenn beide Seiten
    treffen (*„nein, bitte nicht“*): Eine faelschlich unterbliebene Aenderung
    kostet eine Nachfrage, eine faelschlich ausgefuehrte schreibt gegen den
    Willen des Menschen. Die Ablehnung sucht Staemme im Text ohne die
    Zustimmungswoerter. **Die Zustimmung wird geschlossen angenommen**
    (`_consists_of_consent`): nur eine Antwort aus Zustimmungs- und
    Fuellwoertern, ohne ein Zeichen ausserhalb von `DROPPED_SIGNS` (kein
    Fragezeichen, kein Emoji) und ohne die Wortstellung einer Frage (kein
    finites Verb vor seinem Subjekt). Alles andere ist unklar -- auch
    *„Wie bitte!“*, *„Sekündchen, bitte“*, *„wait, ok“*, *„ja？“*,
    *„ja 🤔“*, *„passt es“* und *„ja, vergiss es“*.
    Fehlerfaelle: kein String wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(answer, str):
        msg: str = f"_reading: Antwort ist {type(answer).__name__} statt str"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    lowered: str = answer.lower()
    reading: str = "unclear"
    if _has_stem(_without_words(lowered, CONSENT_WORDS), REFUSAL_STEMS):
        reading = "refusal"
    elif _consists_of_consent(lowered):
        reading = "consent"

    # ── Ausgabe-Verifikation ────────────────────
    if reading not in _READINGS:
        msg = f"_reading: unbekannte Deutung {reading!r}"
        raise RuntimeError(msg)
    return reading


def _question_kind(question: str) -> str:
    """Bestimmt die Art der gestellten Rueckfrage an ihrem Wortlaut.

    Vorbedingung: `question` ist die Frage, die der Mensch gesehen hat
    (`parameter["original_rueckfrage"]`).
    Nachbedingung: `"yes_no"` fuer die drei Ja/Nein-Fragen, `"choice"` fuer
    eine Auswahlfrage, `""` fuer eine Frage, die keiner Form entspricht.
    Fehlerfaelle: kein String wirft `TypeError`. Eine unbekannte Frage ist
    kein Fehler dieser Funktion; der Aufrufer meldet sie und fuehrt nichts aus.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(question, str):
        msg: str = f"_question_kind: Frage ist {type(question).__name__} statt str"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    text: str = question.strip()
    kind: str = ""
    if text.startswith(YES_NO_PREFIXES) or text.endswith(YES_NO_SUFFIXES):
        kind = "yes_no"
    elif text.endswith(CHOICE_SUFFIXES):
        kind = "choice"

    # ── Ausgabe-Verifikation ────────────────────
    # Eine Frage darf nicht beide Formen tragen; sonst ist ihre Art geraten.
    if kind == "yes_no" and text.endswith(CHOICE_SUFFIXES):
        msg = f"_question_kind: Frage traegt Ja/Nein- und Auswahlform: {text[:120]!r}"
        raise RuntimeError(msg)
    return kind


def read_answer(state: AgentState) -> dict:
    """Deutet die Antwort auf die Rueckfrage, bevor etwas ausgefuehrt wird.

    Vorbedingung: `state["parameter"]` traegt `user_answer` (String) und
    `original_rueckfrage` (die gestellte Frage, nicht leer).
    Nachbedingung: Bei Ablehnung `status` `abgeschlossen` mit `REFUSED_TEXT`
    und dem Schritt `abgelehnt` -- nichts ausgefuehrt. Bei Zustimmung auf
    eine Ja/Nein-Frage `status` `laufend` und der Schritt `zugestimmt`; der
    Router geht nach `ausfuehren`. Sonst `status` `rueckfrage` mit derselben
    Frage (Schritt `unklar` oder `auswahl_offen`).
    Fehlerfaelle: fehlende Frage, eine Antwort, die kein String ist, oder
    eine Frage, die keiner bekannten Form entspricht, ergeben `status`
    `fehler` -- laut im Log, nichts ausgefuehrt.
    """
    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    answer: object = parameter.get("user_answer")
    question: object = parameter.get("original_rueckfrage")
    if not isinstance(answer, str) or not isinstance(question, str) or not question.strip():
        logger.error(
            "read_answer: Resume ohne Antwort oder Frage -- nichts ausgefuehrt "
            f"(user_answer={type(answer).__name__}, original_rueckfrage={question!r:.80})"
        )
        return {
            "status": "fehler",
            "fehler": "Rueckfrage oder Antwort fehlt -- nichts ausgefuehrt",
            "schritte": state["schritte"]
            + [{"node": "read_answer", "ergebnis": "fehler: eingabe"}],
        }
    kind: str = _question_kind(question)
    if not kind:
        logger.error(
            f"read_answer: Frage keiner bekannten Form -- nichts ausgefuehrt: {question[:120]!r}"
        )
        return {
            "status": "fehler",
            "fehler": "Rueckfrage nicht erkannt -- nichts ausgefuehrt",
            "schritte": state["schritte"]
            + [{"node": "read_answer", "ergebnis": "fehler: frage_unbekannt"}],
        }

    # ── Verarbeitung ────────────────────────────
    reading: str = _reading(answer)
    action: str = parameter.get("action", "")
    logger.info(f"read_answer: action='{action}', frage={kind}, deutung={reading}")
    if reading == "refusal":
        result: dict = {
            "status": "abgeschlossen",
            "ergebnis": REFUSED_TEXT,
            "schritte": state["schritte"]
            + [{"node": "read_answer", "ergebnis": "abgelehnt", "action": action}],
        }
    elif reading == "consent" and kind == "yes_no":
        result = {
            "status": "laufend",
            "schritte": state["schritte"]
            + [{"node": "read_answer", "ergebnis": "zugestimmt", "action": action}],
        }
    else:
        step: str = "unklar" if kind == "yes_no" else "auswahl_offen"
        result = {
            "status": "rueckfrage",
            "rueckfrage": question,
            "schritte": state["schritte"]
            + [{"node": "read_answer", "ergebnis": step, "action": action}],
        }

    # ── Ausgabe-Verifikation ────────────────────
    # Weiter nach `ausfuehren` geht es nur ohne Ablehnungsstamm und mit einer
    # Antwort, die aus nichts als Zustimmung besteht -- unabhaengig davon,
    # welcher Zweig oben gewaehlt hat.
    lowered: str = answer.lower()
    if result["status"] == "laufend" and (
        _has_stem(_without_words(lowered, CONSENT_WORDS), REFUSAL_STEMS)
        or not _consists_of_consent(lowered)
    ):
        msg: str = f"read_answer: Ausfuehrung ohne Zustimmung auf {answer[:80]!r}"
        raise RuntimeError(msg)
    if result["status"] not in _STATUSES:
        msg = f"read_answer: unbekannter Status {result['status']!r}"
        raise RuntimeError(msg)
    return result
