"""Die Recherche zu einer offenen Eigenschaft — Scheibe 8 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 8. Eine offene
Eigenschaft mit dem Wissenstraeger `nachschlagen` ist Weltwissen, das
speziell, aktuell oder zahlengenau ist — Nova muss es nicht im Kopf haben,
sie darf nachschlagen. Fuer die **erste** solche Eigenschaft eines akuten
Objekts, die das Gedaechtnis nicht deckt (Scheibe 6 nimmt gedeckte aus
`offen` heraus), laeuft **eine** Websuche je Turn; die Treffer stehen am
Objekt in `recherche`, und der `[SACHLAGE]`-Block gibt sie dem Verfasser.

**Dieselbe Suche wie im Thinker** (`tools/web/search.py`), kein Nachlesen
der Trefferseite — das bleibt dem Thinker. Ein Ausfall der Suche ist laut
und kostet den Turn nicht.

**Keine Suche zum eigenen Bestand des Nutzers.** Fragt er nach seinen
Terminen, Vorhaben oder Notizen, kennt das keine Websuche — ein Treffer
stuende trotzdem als »Nachgeschlagen zu …« im Block des Verfassers, neben
dem `[TERMINE]`-Block, und sahe aus wie ein Eintrag des Nutzers. Ob das
Modell der Eigenschaft `nachschlagen` gibt, entscheidet hier nicht: Die
Aeusserung selbst wird geprueft (`own_records_cue`), im Code und
deterministisch, und eine Recherche, die deshalb unterbleibt, steht im Log
(`withhold_research`).
"""

import logging
import re

from config import SACHLAGE_RECHERCHE_MAX_TREFFER
from tools.web.search import web_search_manager

logger = logging.getLogger("ki_server.sachlage.research")

# Der Traeger, der eine Suche verlangt — derselbe Wert wie in `sachlage.py`
# (dort TRAEGER_NACHSCHLAGEN; hier ohne Import, weil `sachlage.py` dieses
# Modul importiert und ein Kreis entstuende).
HOLDER_LOOKUP: str = "nachschlagen"
# Das Gewicht, das eine Luecke vorzieht — derselbe Wert wie in `sachlage.py`
# (dort KRITISCH), aus demselben Grund ohne Import.
CRITICAL: str = "kritisch"
# Wie viel eines Treffers das Artefakt traegt.
_CONTENT_MAX_CHARS: int = 400
# Ein Treffer muss die Sache nennen: mindestens ein Wort des Objektnamens ab
# dieser Laenge in Titel oder Text. `[gemessen]` 29.08.2026, 07:27 UTC: Die
# Suche zu »Neutronenstern-Rotation Rotationsfrequenz des schnellsten
# bekannten Pulsars« lieferte drei BeamNG-Mod-Seiten (BMW 318) — ohne Filter
# haette der Verfasser sie als Nachschlagewerk bekommen.
_MIN_TERM_CHARS: int = 5
# Eine Frage nach dem eigenen Bestand fragt nach dem Tun des Nutzers, nicht
# nach der Welt. Ein falsch Negatives kostet einen fremden Termin im Prompt,
# ein falsch Positives eine Websuche — die Regeln sind deshalb eher weit.
#
# Die erste Person als Handelnder: das Subjekt »ich«, »wir«. Ein »mir« als
# Empfaenger zaehlt nicht: »Kannst du mir sagen, wann die Termine der Liga
# sind?« fragt nach fremdem Wissen.
_SELF_ACTOR: re.Pattern = re.compile(r"\b(?:ich|wir)\b", re.IGNORECASE)
# Der Ort »bei mir« zaehlt nur in »was ist bei mir los«: »Wie wird das
# Wetter morgen bei uns?« ist Welt.
_SELF_PLACE: re.Pattern = re.compile(r"\bbei\s+(?:mir|uns)\b", re.IGNORECASE)
# Dazu der Besitz — aber nur neben einem Wort des Bestands: »mein Kalender«
# ja, »Liegt mein Hotel an der Kueste?« nicht.
_SELF_ANY: re.Pattern = re.compile(
    r"\b(?:ich|wir)\b|\bbei\s+(?:mir|uns)\b|\b(?:mein|unser)\w*", re.IGNORECASE,
)
# Woerter des Kalenders und der Notizen. `\w*termin` nimmt Zusammensetzungen
# (»Arzttermin«), die Endung schliesst »Terminator« aus.
_RECORD_WORD: re.Pattern = re.compile(
    r"\b(?:\w*termin(?:e|en|s)?|\w*kalender\w*|verabred\w*|notiz\w*|notiert\w*"
    r"|vorhab\w*|vorgenommen|eingetragen|plan|pläne)\b",
    re.IGNORECASE,
)
# Ein abgetrenntes Verbteil steht am Ende seines Satzteils: »Was steht
# diese Woche an?«, aber nicht »Liegt das Hotel an der Kueste?«.
_PART_END: str = r"(?=\s*(?:[,;.!?]|$))"
# »steht … an« fragt nach dem, was ansteht — fuer sich allein schon.
_PENDING: re.Pattern = re.compile(
    rf"\b(?:steht|stehen|liegt|liegen)\b[^,;.!?]*?\ban\b{_PART_END}|\bansteh\w*",
    re.IGNORECASE,
)
# »ist … los« nur mit »bei mir«: »Was ist in der Stadt los?« ist Welt.
_GOING_ON: re.Pattern = re.compile(
    rf"\b(?:ist|sind)\b[^,;.!?]*?\blos\b{_PART_END}", re.IGNORECASE,
)
# »habe … vor« nur mit erster Person: »Was haben die Parteien vor?« ist Welt.
_INTENT: re.Pattern = re.compile(
    rf"\b(?:habe|hab|haben)\b[^,;.!?]*?\bvor\b{_PART_END}", re.IGNORECASE,
)
# »wann« mit der ersten Person als Subjekt desselben Satzteils: »Wann muss
# ich zum Zahnarzt?« — nicht »Ich will wissen, wann das Planetarium oeffnet.«
_WHEN_SELF: re.Pattern = re.compile(r"\bwann\b[^,;.!?]*\b(?:ich|wir)\b", re.IGNORECASE)
# Ein Zeitbezug: Tag, Woche, Tageszeit, Uhrzeit, Datum.
_TIME_WORD: re.Pattern = re.compile(
    r"\b(?:heute\w*|\w*morgen\w*|gestern|vorgestern|\w*tag(?:e|en|es|s)?|\w*woche\w*"
    r"|\w*monat\w*|\w*abend\w*|nächst\w*|kommend\w*|uhr)\b|\b\d{1,2}\.\s?\d{1,2}\.",
    re.IGNORECASE,
)
# Fragewoerter am Anfang eines Satzteils.
_QUESTION_WORDS: frozenset[str] = frozenset({
    "was", "wann", "wo", "wohin", "woher", "wie", "wer", "wen", "wem", "wessen",
    "warum", "weshalb", "wieso", "woran", "worauf", "womit", "welche", "welcher",
    "welches", "welchen", "welchem",
})
# Ein Nebensatz mit diesen Woertern vorn fragt nicht nach dem eigenen Tag:
# »Wie wird das Wetter, wenn wir morgen wandern?« sucht das Wetter.
_SUBORDINATORS: frozenset[str] = frozenset({
    "wenn", "falls", "weil", "da", "dass", "als", "bevor", "nachdem", "während", "obwohl",
})
# Satz und Satzteil; der Punkt nach einer Zahl trennt nicht (»am 3.11. was«).
_SENTENCE: re.Pattern = re.compile(r"(?:\d+\.|[^.;!?])+[.;!?]*")
_CLAUSE: re.Pattern = re.compile(r"(?:\d+\.|[^,;.!?])+[,;.!?]*")


def lookup_target(artifact: dict) -> tuple[dict, str] | None:
    """Die nachzuschlagende Eigenschaft — die kritische zuerst.

    **Scheibe 10 (30.08.2026):** Es gibt eine Suche je Turn, und bis dahin
    entschied die Reihenfolge in `offen`, welche Luecke sie bekommt. Dieselbe
    Ueberlegung wie beim Rueckfrage-Gegenstand: Eine Luecke, ohne die die
    Antwort raten muesste, geht einer vor, die sie nur genauer macht. Zwei
    Durchgaenge, der erste sucht die kritische.

    Vorbedingung: `artifact` ist validiert (`traeger` und `kritikalitaet`
        normalisiert).
    Nachbedingung: (Objekt, Eigenschaft) oder None.
    """
    for nur_kritische in (True, False):
        for objekt in artifact.get("objekte") or []:
            if not isinstance(objekt, dict) or not objekt.get("akut"):
                continue
            traeger: dict = objekt.get("traeger") or {}
            gewichte: dict = objekt.get("kritikalitaet") or {}
            for eigenschaft in objekt.get("offen") or []:
                if traeger.get(str(eigenschaft)) != HOLDER_LOOKUP:
                    continue
                if nur_kritische and gewichte.get(str(eigenschaft)) != CRITICAL:
                    continue
                return objekt, str(eigenschaft)
    return None


def _is_question(clause: str) -> bool:
    """Ob ein Satzteil fragt: Fragezeichen, Fragewort vorn oder Verb vor »ich«.

    Vorbedingung: `clause` ist ein Satzteil aus `_CLAUSE`, als Text.
    Nachbedingung: False bei einem Nebensatz (`_SUBORDINATORS` vorn); sonst
        True bei »…?«, bei einem Fragewort unter den ersten zwei Woertern
        (»Und was …«) oder bei »ich«/»wir« als zweitem Wort (»Hab ich …«);
        sonst False — »Morgen hole ich …« berichtet.
    Fehlerfaelle: ein `clause`, das kein Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(clause, str):
        msg: str = f"_is_question: Satzteil ist kein Text ({type(clause).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    words: list[str] = re.findall(r"\w+", clause.lower())
    asks: bool = not (words and words[0] in _SUBORDINATORS) and (
        clause.rstrip().endswith("?")
        or any(w in _QUESTION_WORDS for w in words[:2])
        or (len(words) > 1 and words[1] in {"ich", "wir"})
    )

    # ── Ausgabe-Verifikation ────────────────────
    if asks and not clause.strip():
        msg = "_is_question: leerer Satzteil als Frage erkannt"
        raise RuntimeError(msg)
    return asks


def _sentence_cue(sentence: str) -> str | None:
    """Das Merkmal eines Satzes: Wort des Bestands, »steht … an«, »habe … vor«, »… los«.

    Vorbedingung: `sentence` ist ein Satz aus `_SENTENCE`, als Text.
    Nachbedingung: das Merkmal wie geschrieben, nicht leer — ein Wort des
        Bestands neben erster Person, »bei mir« oder Besitz; ein »steht …
        an« fuer sich; ein »habe … vor« neben »ich«/»wir«; ein »ist … los«
        neben »bei mir« —, oder None.
    Fehlerfaelle: ein `sentence`, das kein Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(sentence, str):
        msg: str = f"_sentence_cue: Satz ist kein Text ({type(sentence).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    found: re.Match | None = None
    record: re.Match | None = _RECORD_WORD.search(sentence)
    pending: re.Match | None = _PENDING.search(sentence)
    intent: re.Match | None = _INTENT.search(sentence)
    going_on: re.Match | None = _GOING_ON.search(sentence)
    if record is not None and _SELF_ANY.search(sentence) is not None:
        found = record
    elif pending is not None:
        found = pending
    elif intent is not None and _SELF_ACTOR.search(sentence) is not None:
        found = intent
    elif going_on is not None and _SELF_PLACE.search(sentence) is not None:
        found = going_on

    # ── Ausgabe-Verifikation ────────────────────
    if found is not None and not found.group(0).strip():
        msg = "_sentence_cue: leeres Merkmal trotz Treffer"
        raise RuntimeError(msg)
    return found.group(0).strip() if found is not None else None


def _clause_cue(clause: str) -> str | None:
    """Das Merkmal eines Satzteils: der Nutzer fragt nach seiner eigenen Zeit.

    Vorbedingung: `clause` ist ein Satzteil aus `_CLAUSE`, als Text.
    Nachbedingung: »wann … ich« wie geschrieben, oder bei einer Frage
        (`_is_question`) die erste Person als Handelnder und ein Zeitbezug
        als »ich … Wochenende«; sonst None. Nicht leer, wenn nicht None.
    Fehlerfaelle: ein `clause`, das kein Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(clause, str):
        msg: str = f"_clause_cue: Satzteil ist kein Text ({type(clause).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    cue: str | None = None
    when_self: re.Match | None = _WHEN_SELF.search(clause)
    actor: re.Match | None = _SELF_ACTOR.search(clause)
    time_word: re.Match | None = _TIME_WORD.search(clause)
    if when_self is not None:
        cue = when_self.group(0).strip()
    elif actor is not None and time_word is not None and _is_question(clause):
        cue = f"{actor.group(0)} … {time_word.group(0)}"

    # ── Ausgabe-Verifikation ────────────────────
    if cue is not None and not cue.strip():
        msg = "_clause_cue: leeres Merkmal trotz Treffer"
        raise RuntimeError(msg)
    return cue


def own_records_cue(utterance: str) -> str | None:
    """Das Merkmal, an dem die Aeusserung als Frage nach dem eigenen Bestand erkannt ist.

    Der eigene Bestand ist, was nur der Nutzer und sein Kalender kennen:
    Termine, Vorhaben, Notizen, sein eigener Tag. Erkannt wird er je Satz
    (`_sentence_cue`: Wort des Bestands mit erster Person oder Besitz,
    »steht … an«, »habe … vor« mit erster Person, »was ist bei mir los«) und
    je Satzteil
    (`_clause_cue`: »wann … ich«, oder eine Frage mit der ersten Person als
    Handelndem und einem Zeitbezug). Ein »mir« als Empfaenger, ein Besitz
    ohne Wort des Bestands und ein Bericht ohne Frage reichen nicht.

    Vorbedingung: `utterance` ist ein Text, auch leer.
    Nachbedingung: das erste gefundene Merkmal (nicht leer, wie in der
        Aeusserung geschrieben), oder None.
    Fehlerfaelle: ein `utterance`, das kein Text ist, wirft `TypeError` —
        ein Programmierfehler des Aufrufers.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(utterance, str):
        msg: str = f"own_records_cue: Aeusserung ist kein Text ({type(utterance).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    cue: str | None = None
    for sentence in _SENTENCE.findall(utterance):
        cue = _sentence_cue(sentence)
        clauses: list[str] = _CLAUSE.findall(sentence)
        for clause in clauses:
            cue = cue or _clause_cue(clause)
        if cue is not None:
            break

    # ── Ausgabe-Verifikation ────────────────────
    if cue is not None and not cue.strip():
        msg = "own_records_cue: leeres Merkmal trotz Treffer"
        raise RuntimeError(msg)
    return cue


def withhold_research(artifact: dict, cue: str) -> dict:
    """Die Recherche unterbleibt, weil der Turn nach dem eigenen Bestand fragt — laut.

    Das Artefakt sieht danach aus wie nach `research_open_property` ohne
    Ziel: Jedes akute Objekt traegt `recherche`, leer. Haette die Recherche
    eine Eigenschaft gesucht, sagt das Log welche und warum nicht.

    Vorbedingung: `artifact` ist validiert; `cue` ist das Merkmal aus
        `own_records_cue`, nicht leer.
    Nachbedingung: Jedes akute Objekt traegt `recherche == {}`; keine Suche
        lief. Gab es ein Ziel, steht eine INFO-Zeile »Sachlage-Recherche
        unterbleibt« mit Merkmal und Anfrage im Log.
    Fehlerfaelle: ein leeres `cue` wirft `ValueError` — ohne Merkmal gibt es
        keinen Grund, und eine grundlos unterlassene Suche waere still.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(cue, str) or not cue.strip():
        msg: str = f"withhold_research: kein Merkmal ({cue!r}) — ohne Grund unterbleibt nichts"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    acute: list[dict] = [
        o for o in artifact.get("objekte") or [] if isinstance(o, dict) and o.get("akut")
    ]
    for objekt in acute:
        objekt["recherche"] = {}
    target: tuple[dict, str] | None = lookup_target(artifact)
    if target is not None:
        target_object, target_property = target
        query: str = f"{target_object.get('name', '')} {target_property}".strip()
        logger.info(
            f"Sachlage-Recherche unterbleibt: Frage nach eigenem Bestand "
            f"(Merkmal '{cue[:40]}') — '{query[:60]}' nicht nachgeschlagen"
        )

    # ── Ausgabe-Verifikation ────────────────────
    if any(o.get("recherche") for o in acute):
        msg = "withhold_research: Recherche-Treffer trotz Unterlassung"
        raise RuntimeError(msg)
    return artifact


def _terms(text: str) -> set[str]:
    """Die Woerter eines Namens ab `_MIN_TERM_CHARS`, kleingeschrieben, ohne Bindestriche."""
    return {
        w for w in "".join(c if c.isalnum() else " " for c in text.lower()).split()
        if len(w) >= _MIN_TERM_CHARS
    }


def relevant_hits(objekt_name: str, treffer: list[dict]) -> list[dict]:
    """Die Treffer, die die Sache nennen — die anderen sind Rauschen der Suche.

    Vorbedingung: `treffer` roh aus der Suche (title, url, content).
    Nachbedingung: Nur Treffer, in deren Titel oder Text ein Wort des
        Objektnamens (ab `_MIN_TERM_CHARS`) vorkommt; hat der Name kein
        solches Wort, bleiben alle. Reihenfolge erhalten.
    """
    woerter: set[str] = _terms(objekt_name)
    if not woerter:
        return list(treffer)
    behalten: list[dict] = []
    for t in treffer:
        if not isinstance(t, dict):
            continue
        text: str = f"{t.get('title', '')} {t.get('content', '')}".lower()
        if any(w in text for w in woerter):
            behalten.append(t)
    return behalten


def research_open_property(artifact: dict) -> dict:
    """Eine Websuche fuer die erste offene Eigenschaft, die Nachschlagen verlangt.

    Vorbedingung: `artifact` ist validiert.
    Nachbedingung: Jedes akute Objekt traegt `recherche` (auch leer); hoechstens
        eines traegt Treffer, unter der gesuchten Eigenschaft, hoechstens
        `SACHLAGE_RECHERCHE_MAX_TREFFER`, jeder mit title, url, content. Die
        Suche steht im Log — mit Anfrage und Trefferzahl.
    Fehlerfaelle: Ein Ausfall der Suche ist eine Warnung, `recherche` bleibt
        leer, der Turn laeuft weiter.
    """
    # ── Eingabe-Validierung ─────────────────────
    for objekt in artifact.get("objekte") or []:
        if isinstance(objekt, dict) and objekt.get("akut"):
            objekt.setdefault("recherche", {})
    ziel: tuple[dict, str] | None = lookup_target(artifact)
    if ziel is None:
        return artifact
    objekt, eigenschaft = ziel

    # ── Verarbeitung ────────────────────────────
    anfrage: str = f"{objekt.get('name', '')} {eigenschaft}".strip()
    try:
        treffer: list[dict] = web_search_manager.suchen(
            anfrage, max_results=SACHLAGE_RECHERCHE_MAX_TREFFER,
        )
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.warning(
            f"Sachlage-Recherche: Suche zu '{anfrage[:60]}' ausgefallen "
            f"({type(fehler).__name__}: {fehler}) — ohne Treffer"
        )
        return artifact
    passend: list[dict] = relevant_hits(str(objekt.get("name", "")), treffer)
    gekuerzt: list[dict] = [
        {
            "title":   str(t.get("title", ""))[:120],
            "url":     str(t.get("url", "")),
            "content": str(t.get("content", ""))[:_CONTENT_MAX_CHARS],
        }
        for t in passend[:SACHLAGE_RECHERCHE_MAX_TREFFER]
        if t.get("content") or t.get("title")
    ]

    # ── Ausgabe-Verifikation ────────────────────
    objekt["recherche"] = {eigenschaft: gekuerzt}
    logger.info(
        f"Sachlage-Recherche: '{anfrage[:60]}' — {len(treffer)} Treffer, "
        f"{len(gekuerzt)} nennen die Sache"
        + (f", erster: {gekuerzt[0]['url']}" if gekuerzt else " (keiner — Rauschen verworfen)")
    )
    return artifact
