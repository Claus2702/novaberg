"""Deutung der Antwort auf eine Rueckfrage der Direktiven -- das Tor vor dem Schreiben.

Der Dienst fragt vor jeder Schreiboperation nach (`crud.validieren_gegen_db`).
Kommt die Antwort mit `resume` zurueck, liest dieser Knoten sie, bevor etwas
ausgefuehrt wird:

  - **Ablehnung** (zuerst geprueft, sie gewinnt): nichts wird ausgefuehrt,
    der Lauf endet mit einem Satz, dass nichts geaendert wurde.
  - **Zustimmung**: der Lauf geht weiter zu `ausfuehren`, mit der Aktion,
    nach der gefragt wurde.
  - **unklar**: dieselbe Frage noch einmal; den Pending-Zustand erneuert
    `dispatch._handle_resume`. Unklar ist auch eine Antwort, die etwas
    zurueckhaelt: ein `?` an irgendeiner Stelle oder ein Wort des Wartens
    (*„Ja? :)“*, *„Sekunde, bitte“*, *„Bitte warten“*).

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

# Hier weicht die Kopie von `agents/notizen/resume.py` ab: Ein Zustimmungswort
# in einer Antwort, die etwas zurueckhaelt, ist keine Zustimmung. Zurueck
# haelt ein `?` an irgendeiner Stelle (*„Wie bitte?!“*, *„Ja? :)“*) und ein
# Wort des Wartens, gesucht als Stamm wie die Ablehnung: `wart` trifft
# *warte*, *warten*, *wartet*, ohne dass jede Form einzeln dasteht. Eine
# solche Antwort ist unklar und kostet eine zweite Frage; als Zustimmung
# gelesen, loeschte sie. Zu weit ist die sichere Richtung: *„Ja? Ja!“*,
# *„dann halt“* und *momentan* fragen ein zweites Mal.
WAIT_STEMS: tuple[str, ...] = ("wart", "moment", "augenblick", "sekunde", "halt")

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


def _holds_back(lowered: str) -> bool:
    """Prueft, ob die Antwort zurueckfragt oder aufhaelt, statt zuzustimmen.

    Vorbedingung: `lowered` ist ein kleingeschriebener String (auch leer).
    Nachbedingung: True, wenn die Antwort an irgendeiner Stelle ein `?`
    traegt oder einen Stamm aus `WAIT_STEMS` enthaelt, auch mitten im Wort.
    Fehlerfaelle: ein Text mit Grossbuchstaben wirft `ValueError`. Steckt
    ein Stamm des Wartens nur in einem Zustimmungswort, widersprechen sich
    die Listen -- dieses Wort hielte jede Zustimmung auf, in der es steht --,
    und es wird `RuntimeError` geworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if lowered != lowered.lower():
        msg: str = f"_holds_back: Text nicht kleingeschrieben: {lowered!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    asks: bool = "?" in lowered
    waits: bool = _has_stem(lowered, WAIT_STEMS)

    # ── Ausgabe-Verifikation ────────────────────
    # Der Stamm muss auch ausserhalb der Zustimmungswoerter stehen; sonst
    # traegt ein Wort aus `CONSENT_WORDS` ihn, und die Listen sind defekt.
    if waits and not _has_stem(_without_words(lowered, CONSENT_WORDS), WAIT_STEMS):
        msg = f"_holds_back: Stamm des Wartens nur in einem Zustimmungswort: {lowered!r}"
        raise RuntimeError(msg)
    return asks or waits


def _reading(answer: str) -> str:
    """Deutet eine Antwort als Ablehnung, Zustimmung oder unklar.

    Vorbedingung: `answer` ist ein String (auch leer).
    Nachbedingung: genau einer von `"refusal"`, `"consent"`, `"unclear"`.
    Die Ablehnung wird zuerst geprueft und gewinnt, wenn beide Seiten
    treffen (*„nein, bitte nicht“*): Eine faelschlich unterbliebene Aenderung
    kostet eine Nachfrage, eine faelschlich ausgefuehrte schreibt gegen den
    Willen des Menschen. Die Ablehnung sucht Staemme im Text ohne die
    Zustimmungswoerter, die Zustimmung zaehlt nur ganze Woerter. Eine Antwort,
    die etwas zurueckhaelt (`_holds_back`: ein `?` an irgendeiner Stelle oder
    ein Stamm des Wartens), ist keine Zustimmung, sondern unklar
    (*„Wie bitte?!“*, *„Ja? :)“*, *„Bitte warten“*).
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
    elif _holds_back(lowered):
        reading = "unclear"
    elif _has_word(lowered, CONSENT_WORDS):
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
    # Weiter nach `ausfuehren` geht es nur mit einem Zustimmungswort, ohne
    # Ablehnungsstamm und ohne etwas, das zurueckhaelt (`?`, Stamm des
    # Wartens) -- unabhaengig davon, welcher Zweig oben gewaehlt hat.
    lowered: str = answer.lower()
    if result["status"] == "laufend" and (
        _has_stem(_without_words(lowered, CONSENT_WORDS), REFUSAL_STEMS)
        or _holds_back(lowered)
        or not _has_word(lowered, CONSENT_WORDS)
    ):
        msg: str = f"read_answer: Ausfuehrung ohne Zustimmung auf {answer[:80]!r}"
        raise RuntimeError(msg)
    if result["status"] not in _STATUSES:
        msg = f"read_answer: unbekannter Status {result['status']!r}"
        raise RuntimeError(msg)
    return result
