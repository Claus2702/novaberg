"""Resume-Node fuer CharakterIdentitaetAgent.

Verarbeitet die Antwort auf eine Pflicht-Rueckfrage (HITL-Gate aus db_validieren).

Phase 0: Standard ja/nein/unklar-Interpretation.
Phase 1 (geplant, Fachabteilungs-Epic): Differenzierte Interpretation pro
  rueckfrage_typ (widerspruch, ergaenzung, subtraktiv, konsolidierung).
"""

import logging
import re

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.charakter_identitaet.resume")


ABLEHNUNG = "abgelehnt"
BESTAETIGUNG = "bestaetigt"
UNKLAR = "unklar"

# Stamm einer Ablehnung, gesucht als Teilzeichenkette: *keinesfalls*,
# *mitnichten*, *lasst*, *abbrechen*, *ablehnen*, *ohne* lehnen so ab, ohne
# dass jede Form einzeln dasteht. Zu weit ist die sichere Richtung (*Klasse*
# traegt *lass*, *neue* traegt *ne*). Gesucht wird im Text ohne die
# Zustimmungswoerter (`CONSENT_WORDS`) — so trifft `"ne"` *gerne* und
# *meinetwegen* nicht.
REFUSAL_STEMS: tuple[str, ...] = (
    "nein", "ne", "nee", "nicht", "kein", "lass", "abbruch", "abbrech", "stopp", "stop",
)

# Zustimmung, gezaehlt als ganzes Wort: `"ja"` trifft *Jahr* nicht; die
# Formen (`jawohl`, `machs`, `klaro` ...) stehen deshalb einzeln da.
CONSENT_WORDS: tuple[str, ...] = (
    "ja", "jap", "jau", "jawohl", "jo", "jop", "jep", "jepp", "yes",
    "ok", "okay", "klar", "klaro", "bitte", "mach", "machs", "mache", "los",
    "gerne", "meinetwegen",
)

# Kopie in den vier Ja/Nein-Deutungen (`direktiven`, `notizen`,
# `charakter_identitaet`, `dateien_wurzeln`), bewusst kein gemeinsames Modul.
# **Hier wird geschlossen angenommen:** Bestaetigt hat nur, wer nichts als
# Zustimmung sagt — jedes Wort steht in `CONSENT_WORDS` oder hier. Was
# zurueckhaelt, ablehnt oder aufschiebt, ist eine offene Klasse;
# *„Wie bitte?“* trug *bitte* und keinen Ablehnungsstamm und bestaetigte —
# auf *„... loeschen (alle)“* deaktivierte das alle Anweisungen. Die
# Zustimmung ist geschlossen, und ein Wort, das hier fehlt, kostet eine
# zweite Frage, nie eine Aenderung der Identitaet.
# Die Regel der Menge: Artikel, Pronomen, das Hilfsverb *ist*, Partikeln, die
# nicht zoegern, und *danke*. Nie darin: ein Verb, ein Nomen, eine Zahl, ein
# Fragewort (*wie*, *was*), eine Partikel des Zoegerns (*na*, *nun*, *also*
# — *„na ja“* ist keine Zustimmung), ein Wort der Einschraenkung oder des
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
# steht — ASCII-Leerraum und die Satzzeichen, mit denen *„Ja!“* und
# *„Ja :)“* zustimmen. Jedes andere Zeichen macht die Antwort unklar: jedes
# Fragezeichen jeder Schrift (*„ja？“*, *„ja¿“*, *„ja ❓“*), jedes Emoji
# (*„ja 👎“*, *„ja 🤔“*), jedes Symbol. Eine Liste der Zeichen, die
# zurueckhalten, liesse wie jede Liste der Woerter das naechste durch; ein
# Zeichen, das hier fehlt, kostet eine zweite Frage. `?` steht nie darin.
DROPPED_SIGNS: frozenset[str] = frozenset(" \t\n\r\f\v.,!;:-()")

# **Die Frage ohne `?` wird an der Wortstellung erkannt:** Eine deutsche
# Ja/Nein-Frage stellt das finite Verb vor sein Subjekt (*„ist das ok“*,
# *„ist es ok“*), die Aussage stellt es dahinter (*„das ist ok“*). In der
# geschlossenen Menge ist die Wortstellung das einzige Merkmal, das eine
# Frage ohne `?` traegt; Fragewoerter kennt die Menge nicht. Eine Antwort mit
# einem Verb aus `ASKING_VERBS` und dahinter, im selben Satzteil, einem Wort
# aus `SUBJECT_WORDS` ist deshalb unklar.
# Fragend sind die Verben der Zustimmungs- und Fuellwoerter, die finit und
# kein Imperativ sind: hier nur *ist*. Nicht darin: der Imperativ der
# Zustimmung (*mach*, *machs*, *mache* — *„mach das“* stimmt zu, *„mach
# ich“* bleibt Selbstaussage) und die Formel *danke*.
ASKING_VERBS: frozenset[str] = frozenset({"ist"})
# Die Fuellwoerter, die Subjekt sein koennen — im Nominativ stehen koennen.
# Nicht darin: was nur Dativ, Akkusativ oder Genitiv ist (*den*, *dem*,
# *des*, *mich*, *mir*, *ihn*, *uns*, *diesen* ...).
SUBJECT_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "ein",
    "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "dies", "diese", "dieses", "dieser",
})
# Die Zeichen, an denen ein Satzteil endet: Ein Subjekt gehoert zum Satz
# seines Verbs, *„ist ok, mach das“* stimmt zu. `- ( )` und Leerraum trennen
# nicht — *„ist - das ok“* und *„ist (das) ok“* fragen. Ein Zeichen mehr
# hier liesse eine Frage als zwei Satzteile durch.
CLAUSE_SEPARATORS: frozenset[str] = frozenset(",.!;:")


def resume(state: AgentState) -> dict:
    """Resume-Node: User-Antwort auf Pflicht-Rueckfrage interpretieren.

    Returns:
      - status='abgeschlossen' → User hat abgelehnt, Aktion verworfen
      - status='rueckfrage'    → Antwort unklar, erneut fragen
      - status='laufend'       → User hat bestaetigt, weiter zu ausfuehren
    """
    user_answer = state["parameter"].get("user_answer", "")
    original_rueckfrage = state["parameter"].get("original_rueckfrage", "")
    rueckfrage_typ = state["parameter"].get("rueckfrage_typ", "standard")
    action = state["parameter"].get("action", "")

    logger.debug(
        f"resume: Einstieg -- action='{action}', typ='{rueckfrage_typ}', "
        f"user_answer='{user_answer[:80]}'"
    )

    interpretation = _antwort_interpretieren(rueckfrage_typ, user_answer)

    if interpretation == ABLEHNUNG:
        logger.info(f"resume: User lehnt ab -- action='{action}' verworfen")
        return {
            "status": "dismissed",
            "ergebnis": "Benutzer hat die Aktion abgelehnt. Keine Aenderung vorgenommen.",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "abgelehnt"}],
        }

    if interpretation == UNKLAR:
        logger.info("resume: Antwort unklar -- erneute Rueckfrage")
        return {
            "status": "rueckfrage",
            "rueckfrage": original_rueckfrage or "Soll ich die Aktion ausfuehren?",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unklar"}],
        }

    logger.info(f"resume: User bestaetigt -- action='{action}' wird ausgefuehrt")
    return {
        "parameter": {
            **state["parameter"],
            "resume": False,
        },
        "status": "laufend",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "bestaetigt"}],
    }


def _antwort_interpretieren(rueckfrage_typ: str, user_answer: str) -> str:
    """Klassifiziert die User-Antwort.

    Strategy-Hook fuer Phase 1: Hier spaeter Dispatch nach rueckfrage_typ
    ('widerspruch', 'ergaenzung', 'subtraktiv', 'konsolidierung').
    Phase 0 nutzt ausschliesslich den 'standard'-Pfad.
    """
    # Phase 1-Andockpunkt:
    # if rueckfrage_typ == "widerspruch": return _widerspruch_interpretieren(user_answer)
    return _standard_interpretieren(user_answer)


def _has_word(text: str, words: tuple[str, ...]) -> bool:
    """Prueft, ob der Text eines der Woerter **als ganzes Wort** enthaelt.

    Vorbedingung: `text` ist kleingeschrieben; `words` ist nicht leer und
    traegt kein leeres Wort.
    Nachbedingung: True nur bei einem Treffer, vor und hinter dem kein
    Buchstabe und keine Ziffer steht.
    Fehlerfaelle: eine leere Wortliste oder ein leeres Wort wirft
    `ValueError` — ein leeres Wort traefe an jeder Stelle.

    **Ein Teilzeichenketten-Vergleich taugt hier nicht:** `"ne"` steckt in
    `"gerne"`, `"meinetwegen"` und `"keine"`, `"ja"` in `"jahr"`. Eine
    Zustimmung wurde so zur Ablehnung und ein beliebiges Wort zur Zustimmung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words or any(not word for word in words):
        msg: str = f"_has_word: leere Wortliste oder leeres Wort in {words!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    hit: bool = any(
        re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) for word in words
    )

    # ── Ausgabe-Verifikation ────────────────────
    # Ein Treffer an Wortgrenzen ist immer auch einer als Teilzeichenkette;
    # gilt das nicht, ist das Muster falsch gebaut.
    if hit and not any(word in text for word in words):
        msg = f"_has_word: Worttreffer ohne Teilzeichenkette in {text!r}"
        raise RuntimeError(msg)
    return hit


def _has_stem(text: str, stems: tuple[str, ...]) -> bool:
    """Prueft, ob einer der Staemme irgendwo im Text steht, auch mitten im Wort.

    Vorbedingung: `text` ist kleingeschrieben; `stems` ist nicht leer und
    traegt nur kleingeschriebene, nicht leere Staemme.
    Nachbedingung: True, sobald ein Stamm als Teilzeichenkette vorkommt —
    `"kein"` trifft *keinesfalls*, `"nicht"` trifft *mitnichten*.
    Fehlerfaelle: ein Text mit Grossbuchstaben, eine leere Liste oder ein
    leerer oder grossgeschriebener Stamm wirft `ValueError` — ein leerer
    Stamm traefe jede Antwort, ein grossgeschriebener keine.
    """
    # ── Eingabe-Validierung ─────────────────────
    if text != text.lower():
        msg: str = f"_has_stem: Text nicht kleingeschrieben: {text!r}"
        raise ValueError(msg)
    if not stems or any(not stem or stem != stem.lower() for stem in stems):
        msg = f"_has_stem: leere Liste oder ungueltiger Stamm in {stems!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    hit: bool = any(stem in text for stem in stems)

    # ── Ausgabe-Verifikation ────────────────────
    # Ein Treffer braucht einen Text, der mindestens so lang ist wie der
    # kuerzeste Stamm; sonst ist der Vergleich falsch gebaut.
    if hit and len(text) < min(len(stem) for stem in stems):
        msg = f"_has_stem: Treffer in zu kurzem Text {text!r}"
        raise RuntimeError(msg)
    return hit


def _without_words(text: str, words: tuple[str, ...]) -> str:
    """Nimmt die Woerter **als ganze Woerter** aus dem Text; an ihrer Stelle bleibt Leerraum.

    Vorbedingung: `text` ist kleingeschrieben; `words` ist nicht leer und
    traegt kein leeres Wort.
    Nachbedingung: Der Rest traegt keines der Woerter mehr als ganzes Wort;
    alles andere steht unveraendert da. Neben einem ganzen Wort steht kein
    Buchstabe; so waechst kein Rest mit einem anderen zu einem neuen Wort.
    Fehlerfaelle: eine leere Wortliste oder ein leeres Wort wirft
    `ValueError` — ein leeres Wort traefe an jeder Stelle.

    So sucht die Ablehnung ihre Staemme nicht in der Zustimmung selbst:
    `"ne"` steckt in *gerne* und *meinetwegen*, in *ablehnen* und *ohne*
    lehnt es ab.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words or any(not word for word in words):
        msg: str = f"_without_words: leere Wortliste oder leeres Wort in {words!r}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    alternatives: str = "|".join(re.escape(word) for word in words)
    rest: str = re.sub(rf"(?<!\w)(?:{alternatives})(?!\w)", " ", text)

    # ── Ausgabe-Verifikation ────────────────────
    if _has_word(rest, words):
        msg = f"_without_words: Rest {rest!r} traegt noch ein Wort aus {words!r}"
        raise RuntimeError(msg)
    return rest


def _asks_by_word_order(joined: str) -> bool:
    """Prueft, ob die Antwort durch ihre Wortstellung fragt — finites Verb vor seinem Subjekt.

    Vorbedingung: `joined` ist kleingeschrieben, das Apostroph ist entfernt.
    Nachbedingung: True, wenn in einem Satzteil (getrennt an den Zeichen
    aus `CLAUSE_SEPARATORS`) ein Wort aus `ASKING_VERBS` steht und irgendwo
    dahinter ein Wort aus `SUBJECT_WORDS` — *„ist das ok“*, *„ist es ok“*,
    *„ist mir das recht“*, *„ist - das ok“*. *„das ist ok“*, *„es ist ok“*
    und *„ist ok, mach das“* fragen nicht.
    Fehlerfaelle: ein Text mit Grossbuchstaben wirft `ValueError`. Steht ein
    fragendes Verb nicht unter den Zustimmungs- und Fuellwoertern, ein
    Subjekt nicht unter den Fuellwoertern oder ein Trennzeichen nicht unter
    `DROPPED_SIGNS`, kann es in keiner Zustimmung stehen — die Listen
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
    """Prueft, ob die Antwort aus nichts als Zustimmung besteht — die geschlossene Annahme.

    Vorbedingung: `lowered` ist ein kleingeschriebener String (auch leer);
    die Ablehnung prueft der Aufrufer vorher.
    Nachbedingung: True nur, wenn (a) jedes Zeichen ausser Buchstaben,
    Ziffern und Apostroph in `DROPPED_SIGNS` steht — kein `?`, kein
    Fragezeichen einer anderen Schrift, kein Emoji, kein Symbol —, (b)
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
    Fuellwort) — die Listen widersprechen sich —, wird `RuntimeError`
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


def _standard_interpretieren(user_answer: str) -> str:
    """Standard-Deutung ja/nein/unklar — Ablehnung ueber Staemme, Zustimmung geschlossen.

    Vorbedingung: `user_answer` ist der Wortlaut des Menschen; leer ist
    zulaessig und heisst UNKLAR.
    Nachbedingung: genau einer der Werte ABLEHNUNG, BESTAETIGUNG, UNKLAR.
    Fehlerfaelle: keine — eine Antwort ohne bekanntes Wort ist UNKLAR und
    fuehrt zur erneuten Frage, nie zur Ausfuehrung.

    **Die Ablehnung gewinnt, wenn beide Seiten treffen** (*„ja, aber lieber
    nicht“*): Eine faelschlich unterbliebene Aenderung kostet eine
    Nachfrage, eine faelschlich bestaetigte schreibt in die Identitaet.

    Die Ablehnung sucht die Staemme aus `REFUSAL_STEMS` auch mitten im Wort
    (*keinesfalls*, *nichts*, *ablehnen*, *ohne*); das ist weit, aber in der
    sicheren Richtung. Sie sucht im Text ohne die Zustimmungswoerter
    (`CONSENT_WORDS`), denn `"ne"` steckt in *gerne* und *meinetwegen*;
    jedes andere `"ne"` lehnt ab, auch der Artikel (*„ja, leg ne neue an“*).

    **Die Zustimmung wird geschlossen angenommen** (`_consists_of_consent`):
    Bestaetigt ist nur eine Antwort aus ganzen Woertern aus `CONSENT_WORDS`
    und `FILLER_WORDS` (`"ja"` trifft *Jahr* nicht), ohne ein Zeichen
    ausserhalb von `DROPPED_SIGNS` (kein Fragezeichen, kein Emoji) und ohne
    die Wortstellung einer Frage (kein finites Verb vor seinem Subjekt).
    Alles andere ist UNKLAR — *„Wie bitte?“*, *„ja？“*, *„ja 👎“*,
    *„Moment, bitte“*, *„ist das ok“*, *„ja, vergiss es“*, *„ok nö“*.
    """
    # ── Eingabe-Validierung ─────────────────────
    text: str = user_answer.lower().strip()
    if not text:
        return UNKLAR

    # ── Verarbeitung ────────────────────────────
    refused: bool = _has_stem(_without_words(text, CONSENT_WORDS), REFUSAL_STEMS)
    confirmed: bool = _consists_of_consent(text)

    # ── Ausgabe-Verifikation ────────────────────
    if refused:
        return ABLEHNUNG
    if confirmed:
        return BESTAETIGUNG
    return UNKLAR
