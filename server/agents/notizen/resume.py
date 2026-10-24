"""Resume-Nodes -- Loest User-Antworten auf Rueckfragen auf.

Zwei Szenarien: Disambiguierung (User waehlt einen Kandidaten)
und Duplikat-Aufloesung (aktualisieren oder neue anlegen).
"""

import json
import logging
import re
from collections.abc import Sequence

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.notizen.resume")

# Stamm einer Ablehnung, gesucht als Teilzeichenkette: *keinesfalls*,
# *mitnichten*, *lasst*, *abbrechen*, *ablehnen*, *ohne* lehnen so ab, ohne
# dass jede Form einzeln dasteht. Zu weit ist die sichere Richtung (*Klasse*
# traegt *lass*, *neue* traegt *ne*). Gesucht wird im Text ohne die
# Zustimmungswoerter (`CONSENT_WORDS`) — so trifft `"ne"` *gerne* und
# *meinetwegen* nicht.
REFUSAL_STEMS: tuple[str, ...] = (
    "nein", "ne", "nee", "nicht", "kein", "lass", "abbruch", "abbrech", "stopp", "stop",
)

# Zustimmung auf 'Notiz existiert nicht, soll ich anlegen?', gezaehlt als
# ganzes Wort: `"ja"` trifft *Jahr* nicht; die Formen (`jawohl`, `machs`
# ...) stehen deshalb einzeln da.
CONSENT_WORDS: tuple[str, ...] = (
    "ja", "jap", "jau", "jawohl", "klar", "klaro", "mach", "machs", "mache", "bitte",
    "okay", "ok", "gerne", "meinetwegen", "sure", "jep", "jepp", "jop", "jopp",
    "auf jeden", "logo", "passt",
)

# Kopie in den vier Ja/Nein-Deutungen (`direktiven`, `notizen`,
# `charakter_identitaet`, `dateien_wurzeln`), bewusst kein gemeinsames Modul.
# **Hier wird geschlossen angenommen:** Angelegt wird nur, wenn die Antwort
# aus nichts als Zustimmung besteht — jedes Wort steht in `CONSENT_WORDS`
# oder hier. Was zurueckhaelt, ablehnt oder aufschiebt, ist eine offene
# Klasse; *„Wie bitte?“* trug *bitte* und keinen Ablehnungsstamm und legte
# an. Die Zustimmung ist geschlossen, und ein Wort, das hier fehlt, kostet
# eine zweite Frage, nie eine Notiz gegen den Willen.
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


def _has_word(text: str, words: Sequence[str]) -> bool:
    r"""Prueft, ob der Text eines der Woerter **als ganzes Wort** enthaelt.

    Vorbedingung: `text` und `words` stehen in derselben Schreibung (der
    Aufrufer senkt beide); `words` ist nicht leer und traegt kein leeres
    Wort. Ein Eintrag darf mehrere Woerter tragen (*„auf jeden“*).
    Nachbedingung: True nur bei einem Treffer, vor und hinter dem kein
    Buchstabe und keine Ziffer steht — `"neu"` trifft *erneut* nicht, `"1"`
    trifft *11 Uhr* nicht, `"ja"` trifft *Jahr* nicht.
    Fehlerfaelle: eine leere Wortliste oder ein leeres Wort wirft
    `ValueError` — ein leeres Wort traefe an jeder Stelle.

    Die Grenze steht als Umgebung (`(?<!\w)`, `(?!\w)`) statt als `\b`:
    Fuer Woerter ist das dasselbe, und ein Notizname, der mit einem
    Satzzeichen endet, trifft so trotzdem.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not words or any(not word for word in words):
        msg: str = f"_has_word: leere Wortliste oder leeres Wort in {list(words)!r}"
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


def _has_stem(text: str, stems: Sequence[str]) -> bool:
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
        msg = f"_has_stem: leere Liste oder ungueltiger Stamm in {list(stems)!r}"
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


def _without_words(text: str, words: Sequence[str]) -> str:
    """Nimmt die Woerter **als ganze Woerter** aus dem Text; an ihrer Stelle bleibt Leerraum.

    Vorbedingung: `text` und `words` stehen in derselben Schreibung (der
    Aufrufer senkt beide); `words` ist nicht leer und traegt kein leeres
    Wort. Ein Eintrag darf mehrere Woerter tragen (*„auf jeden“*).
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


def _candidate_keys(index: int, candidate: dict) -> list[str]:
    """Die Kennungen, ueber die ein Kandidat gewaehlt werden kann: Position und ID.

    Vorbedingung: `index` ist die Stelle des Kandidaten ab 0, `candidate` ein
    Kandidat der Disambiguierung.
    Nachbedingung: die Position ab 1 und, wenn vorhanden, die ID — beide als
    Text, keiner leer. **Eine fehlende ID zaehlt nicht mit:** Ihr leerer Text
    stand frueher in jeder Antwort und waehlte den ersten Kandidaten.
    Fehlerfaelle: ein negativer Index wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if index < 0:
        msg: str = f"_candidate_keys: Index {index} ist negativ"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    keys: list[str] = [str(index + 1)]
    if candidate.get("id") not in (None, ""):
        keys.append(str(candidate["id"]))

    # ── Ausgabe-Verifikation ────────────────────
    if any(not key for key in keys):
        msg = f"_candidate_keys: leere Kennung in {keys!r}"
        raise RuntimeError(msg)
    return keys


def resume(state: AgentState) -> dict:
    """Loest die User-Antwort auf eine Rueckfrage auf.

    Zwei Szenarien:
    1. Disambiguierung: User waehlt einen von mehreren Kandidaten
    2. Duplikat: User sagt 'aktualisieren' oder 'neue anlegen'
    """
    user_answer = state["parameter"].get("user_answer", "")
    rueckfrage = state["parameter"].get("original_rueckfrage", "")
    action = state["parameter"].get("action", "")

    logger.debug(f"resume: Einstieg -- action='{action}', user_answer='{user_answer[:80]}', "
                 f"rueckfrage='{rueckfrage[:80]}'")

    # Versuch: Disambiguierung-JSON parsen
    try:
        disamb = json.loads(rueckfrage)
        if disamb.get("typ") == "disambiguierung":
            return _resume_disambiguierung(state, disamb, user_answer)
        if disamb.get("typ") == "nicht_gefunden":
            return _resume_nicht_gefunden(state, disamb, user_answer)
    except (json.JSONDecodeError, TypeError):
        pass

    # Versuch: Duplikat-Rueckfrage ("aktualisieren oder neue anlegen?")
    if "aktualisier" in rueckfrage.lower() or "bereits eine" in rueckfrage.lower():
        return _resume_duplikat(state, user_answer)

    # Fallback: Konnte Rueckfrage-Typ nicht erkennen
    logger.warning(f"resume: Unbekannter Rueckfrage-Typ -- rueckfrage='{rueckfrage[:100]}'")
    return {
        "status": "fehler",
        "fehler": "Konnte die Rueckfrage-Antwort nicht zuordnen.",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unbekannt"}],
    }


def _resume_disambiguierung(state: AgentState, disamb: dict, user_answer: str) -> dict:
    """User hat einen Kandidaten aus der Disambiguierung gewaehlt."""
    kandidaten = disamb.get("kandidaten", [])
    action = disamb.get("aktion", state["parameter"].get("action", ""))

    logger.debug(f"_resume_disambiguierung: {len(kandidaten)} Kandidaten, action='{action}', "
                 f"user_answer='{user_answer}'")

    if not kandidaten:
        return {
            "status": "fehler",
            "fehler": "Keine Kandidaten in der Disambiguierung.",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "keine_kandidaten"}],
        }

    # Einfache Zuordnung: Nennt die User-Antwort einen Kandidaten-Namen als
    # ganzes Wort? Ein leerer Name traefe jede Antwort und zaehlt nicht.
    user_lower = user_answer.lower()
    match = None
    for k in kandidaten:
        name: str = k["name"].strip().lower()
        if name and _has_word(user_lower, (name,)):
            match = k
            logger.debug(f"_resume_disambiguierung: Match via Name -- '{k['name']}'")
            break

    # Fallback: Position oder ID als ganzes Wort ("Nummer 2", nicht "11 Uhr");
    # eine fehlende ID zaehlt nicht mit
    if not match:
        for i, k in enumerate(kandidaten):
            if _has_word(user_answer, _candidate_keys(i, k)):
                match = k
                logger.debug(f"_resume_disambiguierung: Match via Index/ID -- '{k['name']}'")
                break

    # Fallback: Wenn genau 2 Kandidaten und "erste"/"zweite" im Text
    if not match and len(kandidaten) == 2:
        if _has_word(user_lower, ("erste", "ersten", "obere", "oberen", "1")):
            match = kandidaten[0]
            logger.debug(f"_resume_disambiguierung: Match via 'erste' -- '{match['name']}'")
        elif _has_word(
            user_lower, ("zweite", "zweiten", "untere", "unteren", "2", "andere", "anderen"),
        ):
            match = kandidaten[1]
            logger.debug(f"_resume_disambiguierung: Match via 'zweite' -- '{match['name']}'")

    if not match:
        # User-Antwort zu ungenau fuer einfaches Matching
        logger.info("_resume_disambiguierung: Kein Match -- erneute Rueckfrage")
        return {
            "status": "rueckfrage",
            "rueckfrage": json.dumps({
                "typ": "disambiguierung",
                "agent": "notizen",
                "aktion": action,
                "kandidaten": kandidaten,
            }, ensure_ascii=False),
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "kein_match"}],
        }

    logger.info(
        f"_resume_disambiguierung: Kandidat gewaehlt -- id={match.get('id')}, "
        f"name='{match['name']}'"
    )

    return {
        "parameter": {
            **state["parameter"],
            "action": action,
            "notiz": match,
            "resume": False,  # Resume abgeschlossen
        },
        "status": "laufend",
        "schritte": state["schritte"]
        + [{"node": "resume", "ergebnis": f"gewaehlt: {match['name']}"}],
    }


def _resume_nicht_gefunden(state: AgentState, info: dict, user_answer: str) -> dict:
    """User hat auf 'Notiz existiert nicht, soll ich anlegen?' geantwortet.

    Die Ablehnung gewinnt; angelegt wird nur, wenn die Antwort aus nichts
    als Zustimmung besteht (`_consists_of_consent`, die geschlossene
    Annahme, fuer Woerter, Zeichen und die Wortstellung einer Frage). Alles
    andere -- *„Wie bitte?“*, *„ja？“*, *„ja 👎“*, *„Moment, bitte“*,
    *„ist das ok“*, *„passt es“*, *„ja, vergiss es“* -- stellt die Frage
    erneut.
    """
    user_lower = user_answer.lower()
    target = info.get("target", "")
    original_aufgabe = info.get("original_aufgabe", "")
    original_aktion = info.get("aktion", "add_content")

    logger.debug(f"_resume_nicht_gefunden: target='{target}', user_answer='{user_answer}', "
                 f"original_aufgabe='{original_aufgabe[:80]}'")

    # Die Ablehnung zuerst, und sie gewinnt, wenn beide Seiten treffen
    # ("nein, bitte nicht"): Eine faelschlich unterbliebene Notiz kostet eine
    # Nachfrage, eine faelschlich angelegte schreibt gegen den Willen des Menschen.
    # Die Zustimmung zaehlt nur ganze Woerter ("ja" trifft "Jahr" nicht). Die
    # Ablehnung sucht ihre Staemme dagegen auch mitten im Wort ("bitte
    # keinesfalls", "ok, ich lehne ab"), aber im Text ohne die Zustimmungswoerter:
    # "ne" steckt in "gerne" und "meinetwegen", jedes andere "ne" lehnt ab.
    if _has_stem(_without_words(user_lower, CONSENT_WORDS), REFUSAL_STEMS):
        logger.info("_resume_nicht_gefunden: User lehnt ab")
        return {
            "status": "abgeschlossen",
            "ergebnis": f"Okay, '{target}' wird nicht angelegt.",
            "schritte": state["schritte"] + [{
                "node": "resume",
                "ergebnis": "nicht_gefunden_abgelehnt",
            }],
        }

    # Geschlossen angenommen: Ein Zustimmungswort allein genuegt nicht, es
    # darf nichts danebenstehen als Fuellwoerter (Grund bei `FILLER_WORDS`).
    if _consists_of_consent(user_lower):
        logger.info(
            f"_resume_nicht_gefunden: User bestaetigt -- create '{target}' mit Originaltext"
        )
        return {
            "aufgabe": original_aufgabe,
            "parameter": {
                **state["parameter"],
                "action": "create",
                "resume": False,
            },
            "status": "laufend",
            "schritte": state["schritte"] + [{
                "node": "resume",
                "ergebnis": f"nicht_gefunden_bestaetigt: create '{target}'",
            }],
        }

    logger.info("_resume_nicht_gefunden: Antwort unklar -- erneute Rueckfrage")
    return {
        "status": "rueckfrage",
        "rueckfrage": json.dumps({
            "typ": "nicht_gefunden",
            "agent": "notizen",
            "aktion": original_aktion,
            "target": target,
            "original_aufgabe": original_aufgabe,
        }, ensure_ascii=False),
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unklar"}],
    }


def _resume_duplikat(state: AgentState, user_answer: str) -> dict:
    """User hat auf Duplikat-Rueckfrage geantwortet ('aktualisieren' oder 'neu')."""
    user_lower = user_answer.lower()

    logger.debug(f"_resume_duplikat: user_answer='{user_answer}'")

    # Ganze Woerter: "neu" trifft "erneut" nicht. Die Formen hinter dem Stamm
    # (aktualisieren, neuen ...) trafen frueher als Teilzeichenkette mit.
    update_words: tuple[str, ...] = (
        "aktualisier", "aktualisiere", "aktualisieren", "update", "updaten",
        "überschreib", "überschreibe", "überschreiben", "ersetze", "ersetzen", "ändere",
    )
    new_words: tuple[str, ...] = (
        "neu", "neue", "neuen", "neues", "zusätzlich", "zusätzliche", "zusätzlichen",
        "extra", "trotzdem", "separate", "separaten",
    )
    if _has_word(user_lower, update_words):
        logger.info("_resume_duplikat: User will aktualisieren")
        return {
            "parameter": {
                **state["parameter"],
                "action": "update",
                "resume": False,
            },
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "aktualisieren"}],
        }

    if _has_word(user_lower, new_words):
        logger.info("_resume_duplikat: User will neue Notiz")
        return {
            "parameter": {
                **state["parameter"],
                "action": "create",
                "skip_duplikat_check": True,
                "resume": False,
            },
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "neu_anlegen"}],
        }

    # Unklar -- erneute Rueckfrage
    logger.info("_resume_duplikat: Antwort unklar -- erneute Rueckfrage")
    name = state["parameter"].get("target", "Notiz")
    return {
        "status": "rueckfrage",
        "rueckfrage": (
            f"Es gibt bereits eine Notiz '{name}'. "
            "Soll ich sie aktualisieren oder eine ganz neue anlegen?"
        ),
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unklar"}],
    }
