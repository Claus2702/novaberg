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


def _standard_interpretieren(user_answer: str) -> str:
    """Standard-Deutung ja/nein/unklar — Ablehnung ueber Staemme, Zustimmung ueber Woerter.

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
    Die Zustimmung zaehlt nur ganze Woerter (`"ja"` trifft *Jahr* nicht).
    """
    # ── Eingabe-Validierung ─────────────────────
    text: str = user_answer.lower().strip()
    if not text:
        return UNKLAR

    # ── Verarbeitung ────────────────────────────
    refused: bool = _has_stem(_without_words(text, CONSENT_WORDS), REFUSAL_STEMS)
    confirmed: bool = _has_word(text, CONSENT_WORDS)

    # ── Ausgabe-Verifikation ────────────────────
    if refused:
        return ABLEHNUNG
    if confirmed:
        return BESTAETIGUNG
    return UNKLAR
