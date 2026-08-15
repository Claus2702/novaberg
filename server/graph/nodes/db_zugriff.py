"""DB-Zugriffs-Node am Eingang des CharacterGraphs.

Laedt vier Quellen und befuellt die Personality-Klassen im State:

1. User-Werte aus dem Event-Payload in ``external.emotion``.
2. Persistierter Nova-State aus Redis in ``internal.emotion``.
3. Charakter-Hashes aus PostgreSQL (User-Hash in ``external.character``,
   Nova-Hash in ``internal.character``).
4. Charakter-Identitaeten und Direktiven aus PostgreSQL in
   ``internal.identities`` und ``internal.directives``.

Pixie-Sonderfall: bei ``event_source != "user"`` wird ``external`` mit
einer Kopie von ``internal`` initialisiert — Nova spricht mit sich
selbst, Empathie-Differenz ist null.

**Aufbau:** ``db_zugriff`` ist der Orchestrator und ruft je Quelle einen
Lader. Die **Reihenfolge der Lesevorgaenge ist Verhalten** — in dieser
Reihenfolge stehen sie im ``pipeline_log``, und dort werden sie ausgewertet.
Die Lader werden deshalb in der Schrittfolge gerufen und nicht nach Kanal
gruppiert, auch wenn Letzteres kuerzer aussaehe.

Konzept: docs/novaberg-path2-perzeption_k.md §4.2.
"""

import logging
import time
from dataclasses import dataclass, replace

from config import ASSISTANT_USER_ID, POSTGRES_URL, redis_client
from ei.eigenzeit import (
    KATEGORIE_NEUTRAL,
    arousal_daempfen,
    kategorien_gesprungen,
    verfall_faktor,
)
from ei.raum import raum_ziel_bestimmen
from memory.charakter import (
    charakter_hash_retrieve_dict,
    nova_charakter_hash_retrieve_dict,
)
from memory.pipeline_log import (
    log_berechnung,
    log_db_read,
    log_switch,
    span_end,
    span_start,
)
from tools.db_manager import db_manager

from graph.personality import (
    Character,
    Emotion,
    InternalPersonality,
    Personality,
    Raum,
)
from graph.state import ConversationState, reiz_herkunft

logger = logging.getLogger("ki_server.db_zugriff")

_NODE: str = "db_zugriff"

# Zuordnung Character-Feld → Hash-Spalte. Als Tabelle, weil sie zweimal
# gebraucht wird: fuer den Hash des Nutzers und fuer Novas eigenen. Zweimal
# hingeschrieben waere sie die Stelle, an der beide auseinanderlaufen.
_HASH_FELDER: dict[str, str] = {
    "core":         "kern",
    "adaptive":     "adaptiv",
    "relationship": "beziehungsprofil",
    "intentions":   "intentions_profil",
    "emotions":     "emotions_profil",
}


@dataclass(frozen=True)
class Protokollkopf:
    """Die fuenf Werte, die jeder Protokolleintrag dieses Knotens mitfuehrt.

    Zusammen gesetzt, zusammen weitergegeben — deshalb eine Klasse und nicht
    fuenf Parameter an jedem Lader
    (`novaberg-lesson_l_klassen-statt-flache-keys.md`). Ohne sie stand der
    Rumpf von ``log_db_read`` fuenfmal wortgleich im Node.
    """

    turn_id:      str
    quelle:       str
    span_id:      str
    user_id:      str
    character_id: str


def _lesevorgang(kopf: Protokollkopf, tabelle: str, **felder: object) -> None:
    """Protokolliert einen Lesevorgang im ``pipeline_log``.

    Vorbedingung: `kopf` stammt aus `db_zugriff`, `tabelle` benennt die Quelle.
    Nachbedingung: Ein Eintrag, dessen `inhalt` die Tabelle und die
    uebergebenen Felder traegt.
    Fehlerfaelle: Keine — `log_db_read` behandelt seine eigenen.
    """
    log_db_read(
        turn_id = kopf.turn_id,
        node    = _NODE,
        quelle  = kopf.quelle,
        inhalt  = {"tabelle": tabelle, **felder},
        span_id = kopf.span_id,
        user_id      = kopf.user_id,
        character_id = kopf.character_id,
    )


def _zweig_protokollieren(kopf: Protokollkopf, wert: str, zweig: str) -> None:
    """Protokolliert, welchen Zweig der Pixie-Weiche der Lauf genommen hat.

    Vorbedingung: `zweig` ist der Name des genommenen Zweigs.
    Nachbedingung: Ein `log_switch`-Eintrag mit Bedingung, Wert und Zweig.
    Fehlerfaelle: Keine.
    """
    log_switch(
        turn_id = kopf.turn_id,
        node    = _NODE,
        quelle  = kopf.quelle,
        inhalt  = {"bedingung": "event_source", "wert": wert, "zweig": zweig},
        span_id = kopf.span_id,
        user_id      = kopf.user_id,
        character_id = kopf.character_id,
    )


def _raum_aus_labels(emotion: Emotion) -> Raum:
    """Leitet Novas Raum aus ihren Register-Labels ab.

    Nur fuer den Fall, dass in ``redis:nova_state`` noch keine Raumwerte
    stehen — Cold-Start oder der erste Turn nach Einfuehrung des Raums
    (Chat 114). Der Raum, in dem sie zuletzt gesprochen hat, ist der
    ehrlichere Startwert als ein erfundener Default.

    Vorbedingung: `emotion` traegt die Registerfelder aus der Perzeption.
    Nachbedingung: Beide Achsen liegen auf denselben Skalen wie im laufenden
    Betrieb, gerundet auf zwei Stellen.
    Fehlerfaelle: Keine — unbekannte Labels nehmen den Tabellen-Default,
    und `raum_ziel_bestimmen` benennt einen Modus ausserhalb des Kanons.
    """
    # ── Verarbeitung ────────────────────────────
    tiefe, naehe = raum_ziel_bestimmen(
        Personality(emotion=emotion), quelle="Cold-Start aus Labels",
    )

    # ── Ausgabe ─────────────────────────────────
    return Raum(tiefe=tiefe, naehe=naehe)


def _kopf_eroeffnen(
    turn_id: str, quelle: str, user_id: str, character_id: str,
) -> Protokollkopf:
    """Oeffnet die Protokoll-Spanne und bindet ihre Kennung an den Kopf.

    Vorbedingung: Die vier Werte stammen aus dem State.
    Nachbedingung: Ein Kopf mit der `span_id` der geoeffneten Spanne. Zu jeder
    geoeffneten Spanne gehoert ein `span_end` beim Aufrufer.
    Fehlerfaelle: Keine — `span_start` behandelt seine eigenen.
    """
    # ── Ausgabe ─────────────────────────────────
    return Protokollkopf(
        turn_id = turn_id,
        quelle  = quelle,
        span_id = span_start(
            turn_id = turn_id,
            node    = _NODE,
            quelle  = quelle,
            user_id      = user_id,
            character_id = character_id,
        ),
        user_id      = user_id,
        character_id = character_id,
    )


def _emotion_aus_payload(payload: dict) -> Emotion:
    """Baut die Emotion des Nutzers aus dem Event-Payload des HumanGraphs.

    Vorbedingung: `payload` ist ein Dict, auch ein leeres.
    Nachbedingung: Emotion mit den Werten des Payloads; fehlende Schluessel
    nehmen die dokumentierten Defaults der Datenklasse.
    Fehlerfaelle: Keine — bei Pixie-Events ist der Payload typischerweise leer,
    und `external` wird dann ohnehin durch die Kopie von `internal` ersetzt.
    """
    # ── Verarbeitung ────────────────────────────
    emotion: Emotion = Emotion(
        emotion              = payload.get("current_emotion",    "neutral"),
        arousal              = float(payload.get("current_arousal", 0.5)),
        emotions_vector      = payload.get("emotions_vektor",    ""),
        mode                 = payload.get("gespraechs_modus",   "alltag"),
        language_style       = payload.get("sprach_stil",        "neutral"),
        relationship_dynamic = payload.get("beziehungs_dynamik", "neutral"),
        tone                 = payload.get("tone",               "sachlich"),
        intent               = payload.get("intent",             "smalltalk"),
        prompt_topic         = payload.get("prompt_thema",       ""),
    )

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"db_zugriff Schritt 1 — external.emotion aus Payload: "
        f"emotion={emotion.emotion}, arousal={emotion.arousal}, "
        f"mode={emotion.mode}"
    )
    return emotion


def _emotion_aus_nova_state(roh: dict) -> Emotion:
    """Baut Novas Emotion aus dem persistierten Redis-Hash.

    Vorbedingung: `roh` ist der Hash aus ``redis:nova_state``, auch ein leerer.
    Nachbedingung: Bei leerem Hash die Standard-Emotion (Cold-Start), sonst die
    persistierten Werte; `arousal` ist eine Zahl.
    Fehlerfaelle: Ein nicht zahlbares `arousal` nimmt 0.5. Der Rueckfall gilt
    genau diesem Feld — der uebrige Stand bleibt erhalten.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not roh:
        return Emotion()

    try:
        arousal: float = float(roh.get("arousal", 0.5))
    except (ValueError, TypeError):
        arousal = 0.5

    # ── Ausgabe ─────────────────────────────────
    return Emotion(
        emotion              = roh.get("emotion",              "neutral"),
        arousal              = arousal,
        emotions_vector      = roh.get("emotions_vector",      ""),
        mode                 = roh.get("mode",                 "alltag"),
        language_style       = roh.get("language_style",       "neutral"),
        relationship_dynamic = roh.get("relationship_dynamic", "neutral"),
        tone                 = roh.get("tone",                 "sachlich"),
        intent               = roh.get("intent",               "smalltalk"),
        prompt_topic         = roh.get("prompt_topic",         ""),
    )


def _raum_aus_nova_state(roh: dict, emotion: Emotion) -> tuple[Raum, bool]:
    """Holt Novas Raum aus dem Hash oder leitet ihn aus den Labels ab.

    Vorbedingung: `roh` ist der Hash, `emotion` die daraus gebaute Emotion.
    Nachbedingung: (Raum, geladen). Das zweite Feld sagt, ob der Raum aus dem
    Hash stammt oder abgeleitet wurde, und wandert in die Log-Zeile.
    Fehlerfaelle: Unlesbare Raumwerte sind ein **Defekt** und werden laut
    gemeldet; danach gilt derselbe Rueckfall wie bei fehlenden Werten.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "raum_tiefe" not in roh or "raum_naehe" not in roh:
        return _raum_aus_labels(emotion), False

    # ── Verarbeitung ────────────────────────────
    try:
        geladen = Raum(
            tiefe = float(roh["raum_tiefe"]),
            naehe = float(roh["raum_naehe"]),
        )
    except (ValueError, TypeError) as fehler:
        logger.exception(
            "%s: db_zugriff: Raumwerte in redis:nova_state unlesbar — "
            "aus den Register-Labels abgeleitet",
            type(fehler).__name__,
        )
        return _raum_aus_labels(emotion), False

    # ── Ausgabe ─────────────────────────────────
    return geladen, True


def _nova_zustand_laden(kopf: Protokollkopf, herkunft: str) -> tuple[Emotion, Raum]:
    """Laedt Novas persistierten Zustand aus Redis und protokolliert das Lesen.

    Der geladene Zustand ist der von damals; was jetzt gilt, haengt am
    Intervall seit der letzten Nutzeraeusserung. Der Verfall gehoert deshalb
    hierher und nicht in einen Hintergrundlauf — er wird von der Aeusserung
    ausgeloest, nicht von der Uhr (novaberg-eigenzeit_k.md §2.2).

    Args:
        kopf: traegt das Paar und die Turn-Kennung.
        herkunft: ``"nutzer_turn"`` oder ``"eigener_impuls"``.

    Vorbedingung: `kopf` traegt das Paar.
    Nachbedingung: (Emotion, Raum), die Emotion um das Intervall gesenkt.
    Der Lesevorgang steht im ``pipeline_log``, auch wenn der Hash leer war —
    ein Cold-Start ist eine Auskunft.
    Fehlerfaelle: Siehe `_emotion_aus_nova_state` und `_raum_aus_nova_state`;
    beide fallen feldweise zurueck und melden es.
    """
    # ── Verarbeitung ────────────────────────────
    key: str = f"nova_state:{kopf.user_id}:{kopf.character_id}"
    roh: dict = redis_client.hgetall(key) or {}
    _lesevorgang(kopf, "redis:nova_state", key=key, exists=bool(roh))

    emotion: Emotion = _emotion_aus_nova_state(roh)
    emotion = _zustand_verfallen(kopf, emotion, roh, herkunft)
    raum, geladen = _raum_aus_nova_state(roh, emotion)

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"db_zugriff Schritt 2 — internal.emotion aus Redis: "
        f"cold_start={not bool(roh)}, "
        f"emotion={emotion.emotion}, arousal={emotion.arousal}, "
        f"raum=({raum.tiefe:.2f}, {raum.naehe:.2f})"
        f"{'' if geladen else ' [aus Labels abgeleitet]'}"
    )
    return emotion, raum


def _pause_bestimmen(kopf: Protokollkopf, roh: dict) -> float | None:
    """Liest den Abstand zur letzten Nutzeraeusserung aus dem Zustand.

    Args:
        kopf: traegt das Paar und die Turn-Kennung.
        roh: der Hash aus ``redis:nova_state``.

    Returns:
        Sekunden seit der letzten Nutzeraeusserung, oder ``None``, wenn keine
        verzeichnet ist. **None heisst unbekannt und nicht „keine Pause"** —
        ein fehlender Zeitstempel darf nicht wie ein frischer wirken.
    """
    # ── Eingabe-Validierung ─────────────────────
    roh_zeit: str = str(roh.get("nutzer_zeit", "")).strip()
    if not roh_zeit:
        return None

    try:
        zuletzt: float = float(roh_zeit)
    except ValueError:
        logger.error(
            "%s: db_zugriff: nutzer_zeit in redis:nova_state unlesbar "
            "(%r) — kein Verfall angewandt",
            kopf.turn_id, roh_zeit,
        )
        return None

    # ── Verarbeitung / Ausgabe ──────────────────
    return time.time() - zuletzt


def _zustand_verfallen(
    kopf:     Protokollkopf,
    emotion:  Emotion,
    roh:      dict,
    herkunft: str,
) -> Emotion:
    """Senkt den geladenen Zustand um das Intervall seit der letzten Aeusserung.

    Gedaempft wird das Fluechtige: Erregung als Zahl, Emotion und die
    Kategorien durch Sprung auf ihren Neutralwert. Naehe, Tiefe und
    Beziehungsdynamik bleiben unberuehrt — sie tragen die Bindung, nicht die
    Energie (novaberg-eigenzeit_k.md §2.2).

    Args:
        kopf: traegt das Paar und die Turn-Kennung.
        emotion: der geladene Zustand.
        roh: der Hash aus ``redis:nova_state``.
        herkunft: ``"nutzer_turn"`` oder ``"eigener_impuls"``.

    Returns:
        Den gedaempften Zustand. Unveraendert auf einem Impuls-Turn, bei
        fehlendem Zeitstempel und bei Faktor 1,0.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Auf einem Impuls-Turn findet kein Verfall statt: Er ist keine Pause,
    # sondern Novas eigene Regung darin.
    if herkunft != "nutzer_turn":
        return emotion

    pause: float | None = _pause_bestimmen(kopf, roh)
    if pause is None:
        logger.info(
            "%s: db_zugriff: kein nutzer_zeit im Zustand — kein Verfall "
            "(erster Turn dieses Paares oder Zustand von vor Bauteil A)",
            kopf.turn_id,
        )
        return emotion

    # ── Verarbeitung ────────────────────────────
    faktor: float = verfall_faktor(pause)
    if faktor >= 1.0:
        return emotion

    vorher_arousal: float = emotion.arousal
    vorher_modus:   str   = emotion.mode

    emotion.arousal = arousal_daempfen(emotion.arousal, faktor)

    gesprungen: bool = kategorien_gesprungen(faktor)
    if gesprungen:
        emotion.emotion         = KATEGORIE_NEUTRAL["emotion"]
        emotion.mode            = KATEGORIE_NEUTRAL["mode"]
        emotion.language_style  = KATEGORIE_NEUTRAL["language_style"]
        emotion.tone            = KATEGORIE_NEUTRAL["tone"]
        emotion.emotions_vector = ""

    # ── Ausgabe-Verifikation ────────────────────
    log_berechnung(
        turn_id = kopf.turn_id,
        node    = "db_zugriff",
        quelle  = "character",
        inhalt  = {
            "schritt":          "eigenzeit_verfall",
            "pause_sekunden":   round(pause, 1),
            "faktor":           round(faktor, 4),
            "arousal_vorher":   round(vorher_arousal, 4),
            "arousal_nachher":  round(emotion.arousal, 4),
            "kategorien":       "gesprungen" if gesprungen else "gehalten",
            "modus_vorher":     vorher_modus,
            "modus_nachher":    emotion.mode,
        },
        user_id      = kopf.user_id,
        character_id = kopf.character_id,
    )
    logger.info(
        "%s: db_zugriff: Eigenzeit-Verfall — Pause %.0f s, Faktor %.2f, "
        "Erregung %.2f → %.2f, Kategorien %s",
        kopf.turn_id, pause, faktor, vorher_arousal, emotion.arousal,
        "gesprungen" if gesprungen else "gehalten",
    )
    return emotion


def _character_aus_hash(hash_dict: dict) -> Character:
    """Bildet einen Charakter-Hash auf die fuenf Character-Felder ab.

    Vorbedingung: `hash_dict` ist das Ergebnis einer Hash-Abfrage, auch leer.
    Nachbedingung: Character; fehlende Spalten ergeben leere Zeichenketten,
    nie None.
    Fehlerfaelle: Keine.
    """
    # ── Ausgabe ─────────────────────────────────
    return Character(**{
        feld: hash_dict.get(spalte, "") for feld, spalte in _HASH_FELDER.items()
    })


def _charaktere_laden(kopf: Protokollkopf) -> tuple[Character, Character]:
    """Laedt beide Charakter-Hashes aus PostgreSQL.

    Die Reihenfolge ist Verhalten: erst der Hash des Nutzers, dann Novas
    eigener. So stehen die beiden Lesevorgaenge im ``pipeline_log``.

    Vorbedingung: `kopf` traegt das Paar.
    Nachbedingung: (external, internal), beide Lesevorgaenge protokolliert.
    Fehlerfaelle: Keine — ein fehlender Treffer ergibt leere Felder, und dass
    er fehlte, steht in der Log-Zeile.
    """
    # ── Verarbeitung ────────────────────────────
    extern: dict = charakter_hash_retrieve_dict(
        POSTGRES_URL, kopf.user_id, kopf.character_id,
    )
    _lesevorgang(
        kopf, "charakter_hash",
        user_id      = kopf.user_id,
        character_id = kopf.character_id,
        rolle        = "external",
        hat_treffer  = bool(extern),
    )

    intern: dict = nova_charakter_hash_retrieve_dict(POSTGRES_URL, kopf.user_id)
    _lesevorgang(
        kopf, "charakter_hash",
        user_id      = ASSISTANT_USER_ID,
        character_id = kopf.user_id,
        rolle        = "internal",
        hat_treffer  = bool(intern),
    )

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"db_zugriff Schritt 3 — Hashes geladen: "
        f"external_treffer={bool(extern)}, internal_treffer={bool(intern)}"
    )
    return _character_aus_hash(extern), _character_aus_hash(intern)


def _identities_laden(kopf: Protokollkopf) -> list[str]:
    """Laedt Novas Charakter-Anweisungen aus PostgreSQL.

    Vorbedingung: `kopf` traegt die `user_id`.
    Nachbedingung: Liste der aktiven Anweisungen in Anlagereihenfolge; der
    Lesevorgang steht mit seiner Zahl im ``pipeline_log``.
    Fehlerfaelle: Scheitert die Abfrage, bleibt die Liste leer und der Node
    laeuft weiter — der Graph soll nicht im Eingangsknoten sterben.
    """
    # ── Verarbeitung ────────────────────────────
    anweisungen: list[str] = []
    try:
        zeilen = db_manager.select(
            "SELECT anweisung FROM charakter_anweisungen "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (kopf.user_id,),
        )
        anweisungen = [z["anweisung"] for z in zeilen] if zeilen else []
    except Exception as fehler:
        logger.warning(
            f"db_zugriff — Charakter-Anweisungen Laden fehlgeschlagen: {fehler}"
        )

    # ── Ausgabe-Verifikation ────────────────────
    _lesevorgang(
        kopf, "charakter_anweisungen",
        user_id = kopf.user_id, count = len(anweisungen),
    )
    return anweisungen


def _directives_laden(kopf: Protokollkopf) -> list[dict]:
    """Laedt die Direktiven aus PostgreSQL.

    Vorbedingung: `kopf` traegt die `user_id`.
    Nachbedingung: Liste von Dicts mit `anweisung` und `kontext`; ein fehlender
    Kontext ergibt eine leere Zeichenkette, nie None.
    Fehlerfaelle: Wie bei den Anweisungen — leere Liste, Warnung, weiter.
    """
    # ── Verarbeitung ────────────────────────────
    direktiven: list[dict] = []
    try:
        zeilen = db_manager.select(
            "SELECT anweisung, kontext FROM direktiven "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (kopf.user_id,),
        )
        direktiven = [
            {"anweisung": z["anweisung"], "kontext": z.get("kontext", "")}
            for z in zeilen
        ] if zeilen else []
    except Exception as fehler:
        logger.warning(f"db_zugriff — Direktiven Laden fehlgeschlagen: {fehler}")

    # ── Ausgabe-Verifikation ────────────────────
    _lesevorgang(
        kopf, "direktiven", user_id = kopf.user_id, count = len(direktiven),
    )
    return direktiven


def _external_bestimmen(
    kopf:         Protokollkopf,
    event_source: str,
    internal:     InternalPersonality,
    charakter:    Character,
    emotion:      Emotion,
) -> Personality:
    """Waehlt, wer ``external`` ist: der Nutzer oder Nova selbst.

    Pixie-Sonderfall: bei ``event_source != "user"`` spricht Nova mit sich
    selbst, die Empathie-Differenz ist null.

    **Die Kopie ist eine Kopie.** `replace` ohne Aenderung liefert ein neues
    Objekt mit denselben Werten. Eine Zuweisung ergaebe einen Alias, und eine
    spaetere Aenderung an `internal` schlueg dann auf `external` durch, ohne
    dass ein Gleichheitstest es saehe.

    Vorbedingung: `internal` ist fertig gebaut.
    Nachbedingung: Personality; der genommene Zweig steht im ``pipeline_log``.
    Fehlerfaelle: Keine.
    """
    # ── Verarbeitung ────────────────────────────
    if event_source != "user":
        _zweig_protokollieren(
            kopf, event_source, "pixie_pfad_external_aus_internal",
        )
        logger.info("db_zugriff — Pixie-Pfad: external = Kopie von internal")
        return Personality(
            character = replace(internal.character),
            emotion   = replace(internal.emotion),
        )

    # ── Ausgabe ─────────────────────────────────
    _zweig_protokollieren(kopf, event_source, "user_pfad")
    return Personality(character=charakter, emotion=emotion)


def db_zugriff(state: ConversationState) -> ConversationState:
    """Eingangsnode des CharacterGraphs.

    Laedt Identitaets-Daten und Zustands-Daten aus PostgreSQL und Redis
    und befuellt die Personality-Klassen ``external`` und ``internal``.

    Vorbedingung: ``user_id`` und ``character_id`` sind im State gesetzt.
    Nachbedingung: ``state["external"]`` und ``state["internal"]`` sind
    befuellt; bei ``event_source != "user"`` traegt ``external`` eine Kopie
    von ``internal``.
    Fehlerfaelle: leere ``user_id``/``character_id`` werden geloggt; der
    Node bricht nicht ab, sondern faehrt mit Defaults fort, damit der
    Graph nicht im Eingangsknoten stirbt.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id:      str  = state.get("user_id", "")
    character_id: str  = state.get("character_id", "")
    event_source: str  = state.get("event_source", "user")
    payload:      dict = state.get("event_payload", {}) or {}
    turn_id:      str  = state.get("turn_id", "unbekannt")
    quelle_log:   str  = state.get("ei_calc_rolle", "character")

    if not user_id or not character_id:
        logger.error(
            f"db_zugriff: Paar-Schluessel unvollstaendig — "
            f"user_id='{user_id}', character_id='{character_id}'"
        )

    kopf = _kopf_eroeffnen(turn_id, quelle_log, user_id, character_id)
    logger.info(
        f"db_zugriff start — paar={user_id}:{character_id}, "
        f"event_source={event_source}"
    )

    # ── Verarbeitung ────────────────────────────
    # Ein abgebrochener Pfad 1 liefert keine Perzeptionswerte, und
    # `_emotion_aus_payload` fuellt fehlende Schluessel mit den Defaults der
    # Datenklasse — `neutral`, 0.5, `alltag`. **Ohne diese Zeile waere ein
    # Zusammenbruch von einer ruhigen Nutzeraeusserung nicht zu
    # unterscheiden**, und der Turn liefe unauffaellig auf erfundenen Werten
    # weiter. Das Ereignis wird trotzdem verarbeitet: Eine Antwort auf
    # Defaults ist besser als keine (novaberg-bugs.md →
    # PFAD1-TIMEOUT-TURNVERLUST), aber sie ist als solche kenntlich.
    pfad1_ausfall: str = str(payload.get("pfad1_ausfall", ""))
    if pfad1_ausfall:
        logger.error(
            f"db_zugriff: Pfad 1 ist abgebrochen ({pfad1_ausfall}) — "
            f"external.emotion traegt die Defaults der Datenklasse und ist "
            f"KEINE Messung (turn_id={turn_id})"
        )

    external_emotion: Emotion = _emotion_aus_payload(payload)
    internal_emotion, internal_raum = _nova_zustand_laden(kopf, reiz_herkunft(state))
    external_character, internal_character = _charaktere_laden(kopf)
    identities: list[str]  = _identities_laden(kopf)
    directives: list[dict] = _directives_laden(kopf)

    internal = InternalPersonality(
        character  = internal_character,
        emotion    = internal_emotion,
        identities = identities,
        directives = directives,
        raum       = internal_raum,
    )

    # ── Ausgabe-Verifikation ────────────────────
    state["internal"] = internal
    state["external"] = _external_bestimmen(
        kopf, event_source, internal, external_character, external_emotion,
    )

    span_end(
        turn_id = kopf.turn_id,
        node    = _NODE,
        quelle  = kopf.quelle,
        span_id = kopf.span_id,
        user_id      = kopf.user_id,
        character_id = kopf.character_id,
    )
    logger.info("db_zugriff fertig — external und internal befuellt")
    return state
