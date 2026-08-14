"""
Shadow Delivery Service — der Übergang von Pixies Fund zu Novas Gedanken.

Prüft periodisch ob Nova etwas einbringen kann:
  1. Momentum "low" nach einem Request → kurze Pause → Delivery
  2. Timeout (30s+ Inaktivität) → proaktive Nachricht

Wählt den thematisch passendsten Stack-Eintrag per Cosine Similarity und gibt
das Wissensstück in die beiden Graphen: Der AgentGraph lässt den Gedanken
entstehen, der CharacterGraph denkt ihn. Der Dienst formuliert selbst nichts
mehr — die Stimme kommt aus dem Responder, die Zustellung aus dem
Event-Consumer (`character_response`).

Keine Rückfallebene: Erreicht der Impuls den CharacterGraph nicht, bleibt der
Stack-Eintrag liegen und der nächste Zyklus versucht es erneut. Ein Gedanke,
der nicht gedacht wurde, wird nicht ausgesprochen.

Flood-Schutz:
  - Thematischer Cooldown: Anderes Thema → wartet auf User-Aktion
  - Burst-Limit: Max 3 aufeinanderfolgende Impulse ohne User-Reaktion
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime

import numpy as np
import redis

from config         import ASSISTANT_USER_ID, shutdown_event
from memory.session import session_turns_retrieve
from services.events import event_erzeugen
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.shadow_delivery")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
PRÜF_INTERVALL:       float = 5.0     # Sekunden zwischen Prüfungen
MOMENTUM_PAUSE:       float = 3.0     # Pause nach Momentum-Low bevor Delivery
INAKTIVITAET_GRENZE:  float = 30.0    # Sekunden ohne User-Aktion → Timeout-Trigger
# **Die Schwelle des Themen-Tors, und ihre Paarung gehoert zur Zahl.**
# Sie gilt fuer **Stapeltext gegen Nutzeraeusserung** — einen langen Fachtext
# gegen einen kurzen Zuruf. Gemessen am 14.08.2026 an etikettierten Paaren,
# bester Eintrag je Aeusserung: zum Thema 0,358 / 0,364 / 0,438, daneben
# Median 0,181 und Maximum 0,256. Beide Mengen trennen mit rund 0,10 Abstand.
#
# **Hoeher geht nicht:** Der beste je erreichte echte Treffer liegt bei 0,438;
# ab 0,45 kommt nichts mehr durch, auch das Passende nicht.
#
# ⚠ Die Zahl steht auf **drei** Aeusserungen — eine begruendete Setzung, kein
# belastbarer Messwert. Nach der naechsten Themenrunde nachmessen.
#
# Der Vorgaenger stand bei 0,40 auf der Paarung Langtext gegen Langtext und
# hat damit Textsortengleichheit gemessen (Median 0,557 im Bestand): 52 von 56
# Impulsen kamen durch. Eine Zahl ohne ihre Paarung ist keine Schwelle.
THEMEN_SCHWELLE: float = 0.30
MAX_BURST:            int   = 2       # Max aufeinanderfolgende Impulse
COOLDOWN_TTL:         int   = 3600    # Cooldown-Key TTL in Sekunden

# ─────────────────────────────────────────────
# Cosine Similarity
# ─────────────────────────────────────────────
_COMPATIBLE_MODES: dict[str, set] = {
    "fachgespraech":           {"lernmodus", "beratend", "berichtend"},
    "philosophischer_austausch": {"kreativ", "emotional"},
    "alltag":                  {"spielerisch", "emotional"},
    "arbeitsmodus":            {"beratend", "berichtend", "fachgespraech"},
    "emotional":               {"philosophischer_austausch", "alltag"},
    "spielerisch":             {"alltag", "kreativ"},
    "lernmodus":               {"fachgespraech", "beratend"},
    "kreativ":                 {"philosophischer_austausch", "spielerisch"},
    "beratend":                {"fachgespraech", "arbeitsmodus", "lernmodus"},
    "berichtend":              {"arbeitsmodus", "fachgespraech"},
}

def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Berechnet die Cosine Similarity zwischen zwei Vektoren."""
    if not vec_a or not vec_b:
        return 0.0

    a: np.ndarray = np.array(vec_a)
    b: np.ndarray = np.array(vec_b)

    dot:    float = np.dot(a, b)
    norm_a: float = np.linalg.norm(a)
    norm_b: float = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


# ─────────────────────────────────────────────
# Emotionale Kompatibilität prüfen
# ─────────────────────────────────────────────
NEGATIVE_EMOTIONEN: set = {"frustration", "aerger", "traurigkeit", "unsicherheit"}

def _emotional_kompatibel(
    stack_aufgabe: str,
    user_emotion:  str,
) -> bool:
    """Prüft ob ein Impuls zur aktuellen User-Emotion passt."""
    # Bei Stress: Grundsätzlich nichts einbringen
    if user_emotion == "stress":
        return False

    # Negative Emotionen: Nur empathische Nachfragen erlaubt
    if user_emotion in NEGATIVE_EMOTIONEN:
        return stack_aufgabe == "nachfragen"

    # Nachdenklich: Kein Humor
    if user_emotion == "nachdenklich" and stack_aufgabe == "humor":
        return False

    # Alle anderen Kombinationen: Erlaubt
    return True


def _modus_kompatibel(
    stack_modus:     str,
    gespraechs_modus: str,
) -> float:
    """
    Berechnet einen Kompatibilitäts-Score (0.0-1.0) zwischen
    Stack-Modus und aktuellem Gesprächsmodus.
    """
    if not stack_modus or not gespraechs_modus:
        return 0.5  # Unbekannt → neutral

    # Gleicher Modus = perfekt
    if stack_modus == gespraechs_modus:
        return 1.0

    # Kompatibilitäts-Gruppen

    kompatible: set = _COMPATIBLE_MODES.get(gespraechs_modus, set())

    if stack_modus in kompatible:
        return 0.7

    return 0.3  # Inkompatibel aber nicht verboten


# ─────────────────────────────────────────────
# Gesprächs-Embedding berechnen
# ─────────────────────────────────────────────
async def _gespraechs_embedding(
    redis_client:  redis.Redis,
    user_id:       str,
    character_id:  str = "",
) -> list[float]:
    """Berechnet ein Embedding aus den letzten Session-Turns."""
    turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id or ASSISTANT_USER_ID)

    if not turns:
        return []

    # **Nur die Aeusserungen des Menschen.** Ein Vektor aus allen Rollen misst,
    # ob ein Gedanke zu ihren **eigenen vorigen Gedanken** passt — und das tut
    # er immer: Jeder zugestellte Einwurf liegt danach selbst in der Session.
    # Je mehr zu einem Thema gesendet wurde, desto besser passte das naechste.
    #
    # **Und kein Zeitfenster.** Ein Fenster schneidet den Bezug ab, sobald
    # jemand eine Nacht schlaeft, und laesst danach alles ungefiltert durch —
    # also genau dort, wo die Nachricht liegen bleibt und am Morgen als erstes
    # gelesen wird. Der Bezug reicht bis zur letzten Aeusserung zurueck, gleich
    # wie lange sie her ist.
    aeusserungen: list[str] = [
        (t.get("inhalt") or "").strip() for t in turns
        if t.get("rolle") == "user" and (t.get("inhalt") or "").strip()
    ]

    if not aeusserungen:
        # Kein Bezugsvektor heisst: Dieses Tor entfaellt. Der Aufrufer
        # entscheidet, was daraus folgt — hier wird nichts erfunden.
        logger.info(
            "Delivery: keine Aeusserung des Menschen in der Session — kein "
            "Bezugsvektor fuer '%s', das Themen-Tor entfaellt", user_id,
        )
        return []

    kontext: str = " ".join(aeusserungen[-5:])

    embed_response = await model_service.embed.submit(EmbedRequest(text=kontext))
    embedding: list[float] = embed_response.embedding
    logger.debug(
        "Shadow-Delivery: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
        len(embedding),
        embed_response.duration_seconds,
    )
    return embedding


# ─────────────────────────────────────────────
# Besten Stack-Eintrag finden (semantisch)
# ─────────────────────────────────────────────
def _besten_eintrag_finden(
    redis_client:      redis.Redis,
    user_id:           str,
    gespraechs_vector: list[float],
    user_emotion:      str = "neutral",
    gespraechs_modus:  str = "",
) -> tuple[dict | None, int]:
    """
    Durchsucht den Stack nach dem thematisch und emotional passendsten Eintrag.
    Gibt (eintrag, index) zurück oder (None, -1) wenn nichts passt.
    """
    raw_list: list = redis_client.lrange(f"shadow_stack:{user_id}", 0, -1)

    if not raw_list:
        return None, -1

    bester_eintrag: dict | None = None
    bester_index:   int         = -1
    bester_score:   float       = 0.0

    for idx, raw in enumerate(raw_list):
        try:
            eintrag: dict = json.loads(raw)
        except json.JSONDecodeError:
            continue

        # Filter 1: Emotionale Kompatibilität (harter Filter)
        stack_aufgabe: str = eintrag.get("aufgabe", "")

        if not _emotional_kompatibel(stack_aufgabe, user_emotion):
            logger.debug(
                f"Delivery: '{eintrag.get('thema', '')[:30]}' emotional inkompatibel "
                f"(aufgabe={stack_aufgabe}, user_emotion={user_emotion})"
            )
            continue

        # Filter 2: Thematische Similarity
        embedding: list[float] = eintrag.get("embedding", [])

        if not embedding:
            # **Ein Ausfall darf nicht wie ein Treffer aussehen.** Vorher galt
            # ein Eintrag ohne Embedding als exakt auf der Schwelle liegend und
            # passierte damit — ein fehlender Wert wurde zum bestandenen Test.
            logger.error(
                "Delivery: Stapel-Eintrag ohne Embedding abgelehnt "
                "(thema='%s') — nicht pruefbar ist nicht dasselbe wie passend",
                eintrag.get("thema", "")[:40],
            )
            continue

        thema_sim: float = _cosine_similarity(gespraechs_vector, embedding)

        if thema_sim < THEMEN_SCHWELLE:
            continue

        # Filter 3: Modus-Kompatibilität (weicher Score)
        stack_modus: str   = eintrag.get("modus", "")
        modus_score: float = _modus_kompatibel(stack_modus, gespraechs_modus)

        # Gewichteter Gesamt-Score: 70% Thema + 30% Modus
        gesamt_score: float = (thema_sim * 0.7) + (modus_score * 0.3)

        if gesamt_score > bester_score:
            bester_score   = gesamt_score
            bester_eintrag = eintrag
            bester_index   = idx

    if bester_eintrag is None:
        logger.debug("Delivery: Kein kompatibler Eintrag gefunden")
        return None, -1

    logger.info(
        f"Delivery: Bester Match '{bester_eintrag.get('thema', '')[:40]}' "
        f"(score={bester_score:.2f}, idx={bester_index})"
    )

    return bester_eintrag, bester_index


# ─────────────────────────────────────────────
# Stack-Eintrag per Index entfernen
# ─────────────────────────────────────────────
def _stack_eintrag_entfernen(
    redis_client: redis.Redis,
    user_id:      str,
    index:        int,
) -> None:
    """Entfernt einen spezifischen Eintrag per Index vom Stack."""
    stack_key: str = f"shadow_stack:{user_id}"
    tombstone: str = "__REMOVED__"

    # Markieren + Aufräumen (Redis hat kein LREMOVE by index)
    redis_client.lset(stack_key, index, tombstone)
    redis_client.lrem(stack_key, 1, tombstone)

    logger.debug(f"Delivery: Stack-Eintrag {index} entfernt.")


# ─────────────────────────────────────────────
# Stack-Eintrag nach Ähnlichkeit entfernen
# ─────────────────────────────────────────────
def _stack_aehnliche_entfernen(
    redis_client:    redis.Redis,
    user_id:         str,
    referenz_vector: list[float],
    # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.65 im
    # casing-blinden Raum (Grundrauschen 0.74 — räumte fast alles ab; im
    # neuen Raum hätte 0.65 nie gegriffen).
    threshold:       float = 0.60,
) -> None:
    """Entfernt Stack-Einträge die dem gerade gesendeten zu ähnlich sind."""
    if not referenz_vector:
        return

    stack_key: str = f"shadow_stack:{user_id}"
    raw_list:  list = redis_client.lrange(stack_key, 0, -1)

    entfernt: int = 0

    for raw in raw_list:
        try:
            eintrag:   dict         = json.loads(raw)
            embedding: list[float]  = eintrag.get("embedding", [])

            if embedding and _cosine_similarity(referenz_vector, embedding) >= threshold:
                redis_client.lrem(stack_key, 1, raw)
                entfernt += 1
                logger.info(
                    f"Delivery: Duplikat entfernt — '{eintrag.get('thema', '')[:40]}'"
                )
        except json.JSONDecodeError:
            continue

    if entfernt:
        logger.info(f"Delivery: {entfernt} ähnliche Einträge bereinigt.")


# ─────────────────────────────────────────────
# Zeitlichen Kontext berechnen
# ─────────────────────────────────────────────
def _zeitlicher_kontext(erstellt: str) -> str:
    """Berechnet eine natürliche Zeitangabe aus dem Erstelldatum."""
    try:
        erstelldatum: datetime = datetime.fromisoformat(erstellt)
        differenz = datetime.now() - erstelldatum
        stunden: float = differenz.total_seconds() / 3600

        if stunden < 1:
            return "Dieses Thema kam gerade eben im Gespräch auf."
        elif stunden < 24:
            return "Dieses Thema kam heute im Gespräch auf."
        elif stunden < 48:
            return "Dieses Thema kam gestern im Gespräch auf."
        else:
            tage: int = int(differenz.days)
            return f"Dieses Thema kam vor {tage} Tagen im Gespräch auf."

    except (ValueError, TypeError):
        return "Dieses Thema kam kürzlich im Gespräch auf."


# ─────────────────────────────────────────────
# Cooldown-Verwaltung
# ─────────────────────────────────────────────
def _cooldown_aktiv(redis_client: redis.Redis, user_id: str) -> bool:
    """Prüft ob der thematische Cooldown aktiv ist."""
    return redis_client.exists(f"shadow_cooldown:{user_id}") == 1


def _cooldown_setzen(redis_client: redis.Redis, user_id: str) -> None:
    """Setzt den Cooldown — wird durch nächste User-Aktion gelöscht."""
    redis_client.set(f"shadow_cooldown:{user_id}", "1", ex=COOLDOWN_TTL)


def shadow_cooldown_reset(redis_client: redis.Redis, user_id: str) -> None:
    """
    Löscht Cooldown und Burst-Counter.
    Wird bei jeder User-Nachricht aufgerufen (aus dem Chat-Endpoint).
    """
    redis_client.delete(f"shadow_cooldown:{user_id}")
    redis_client.delete(f"shadow_burst_count:{user_id}")
    logger.debug(f"Delivery: Cooldown + Burst reset für '{user_id}'")


# ─────────────────────────────────────────────
# Burst-Verwaltung
# ─────────────────────────────────────────────
def _rueckfrage_offen(redis_client: redis.Redis, user_id: str) -> bool:
    """Prueft, ob ein Agent gerade auf eine Antwort des Menschen wartet.

    **Warum das eine Wartebedingung ist und kein Verbot.** Der Eintrag
    verfaellt nicht, er bleibt auf dem Stapel und kommt beim naechsten Zyklus
    wieder — und die Wartezeit eines Agenten ist auf fuenf Minuten begrenzt.
    Der Preis ist also ein aufgeschobener Gedanke, der Gewinn eine Frage, die
    ihre Antwort bekommt.

    Sie steht **vor** dem Burst-Zaehler, weil sie nichts kostet und weil ein
    Zaehler, der fuer einen unterdrueckten Impuls hochliefe, die naechste
    Gelegenheit mit verbrauchte.

    Diese Pruefung ersetzt den Riegel im Router nicht: Sie regelt den
    Zeitpunkt der Zustellung, er die Zustaendigkeit. Ein Reiz eigener Herkunft
    kann den Graphen auch auf anderem Weg erreichen — ein Wiederholungsversuch
    traegt dieselbe Marke.

    Vorbedingung: keine.
    Nachbedingung: True genau dann, wenn ein Wartezustand fuer dieses Paar
        existiert.
    Fehlerfaelle: Ein Redis-Fehler gilt als „keine Rueckfrage offen" und wird
        laut gemeldet — ein ausgefallener Speicher darf die Zustellung nicht
        dauerhaft stilllegen.

    Args:
        redis_client: Redis-Verbindung.
        user_id:      Kennung des Menschen.

    Returns:
        True, wenn ein Agent auf eine Antwort wartet.
    """
    # ── Verarbeitung ────────────────────────────
    try:
        offen: bool = redis_client.exists(f"pending_agent:{user_id}") == 1
    except Exception:
        logger.exception(
            "Delivery: Wartezustand nicht lesbar fuer '%s' — es wird "
            "zugestellt, als waere keine Rueckfrage offen", user_id,
        )
        return False

    # ── Ausgabe ─────────────────────────────────
    if offen:
        logger.info(
            "Delivery: Impuls zurueckgestellt fuer '%s' — ein Agent wartet auf "
            "eine Antwort, der Eintrag bleibt auf dem Stapel", user_id,
        )
    return offen


def _burst_erlaubt(redis_client: redis.Redis, user_id: str) -> bool:
    """Prüft ob der Burst-Limit noch nicht erreicht ist."""
    count: str | None = redis_client.get(f"shadow_burst_count:{user_id}")

    if not count:
        return True

    return int(count) < MAX_BURST


def _burst_erhoehen(redis_client: redis.Redis, user_id: str) -> None:
    """Erhöht den Burst-Counter."""
    key: str = f"shadow_burst_count:{user_id}"

    redis_client.incr(key)
    redis_client.expire(key, COOLDOWN_TTL)


# ─────────────────────────────────────────────
# Delivery ausführen (eine einzelne Nachricht)
# ─────────────────────────────────────────────
async def _delivery_ausfuehren(
    redis_client:  redis.Redis,
    user_id:       str,
    websocket_map: dict,
    compiled_agent_graph = None,
    agent_graph          = None,
) -> bool:
    """Gibt einen Pixie-Impuls den Weg durch beide Graphen.

    1. Gespraechs-Embedding berechnen
    2. Besten Stack-Eintrag finden
    3. turn_id erzeugen — eine je CharacterGraph-Durchlauf
    4. AgentGraph: der Gedanke entsteht (Kontext, Bewertung, Ablage)
    5. Event feuern: der CharacterGraph denkt ihn — Emotion, Assoziation,
       Stimme. Der Responder spricht, der Dispatcher schreibt den Rohturn.
    6. Stack-Eintrag und Aehnliche entfernen

    Das Wissensstueck ist der Reiz, nicht ein daraus vorformulierter Satz.

    Keine Rueckfallebene: Erreicht der Impuls den CharacterGraph nicht, wird
    nichts gesendet und der Stack-Eintrag bleibt liegen. Eine zweite, seelenlose
    Zustellung waere kein Ersatz, sondern genau das, was dieser Umbau abgeschafft
    hat — ein Gedanke, der ausgesprochen wird, bevor er gedacht wurde.

    Vorbedingung: ein WebSocket fuer den User ist verbunden — sonst entstuende
    eine Antwort, die niemand empfaengt.
    Gibt True zurueck, wenn ein Impuls seinen Weg genommen hat.
    """
    # Gesprächskontext als Embedding
    gespraechs_vector: list[float] = await _gespraechs_embedding(
        redis_client, user_id, ASSISTANT_USER_ID,
    )

    if not gespraechs_vector:
        # **Hier steht eine offene Entscheidung, kein gebautes Verhalten.**
        # Das Konzept will, dass ohne Aeusserung des Menschen nur *dieses* Tor
        # entfaellt und die uebrigen bleiben. Wonach dann gewaehlt wird —
        # aeltester, juengster, salientester Eintrag —, ist unentschieden, und
        # es ist der **haeufigste** Fall: 39 von 56 Impulsen lagen am
        # 14.08.2026 in dieser Lage.
        #
        # Bis das entschieden ist, bleibt es beim bisherigen Verhalten: Es
        # wird nichts zugestellt. Das ist keine Wahl, sondern ihr Aufschub —
        # und es steht als `error` da, damit der Aufschub im Betrieb zaehlbar
        # ist statt unsichtbar zu bleiben.
        logger.error(
            "Delivery: kein Bezugsvektor fuer '%s' — keine Aeusserung des "
            "Menschen in der Session. Das Themen-Tor entfaellt, und wonach "
            "ohne Themenwert zu waehlen waere, ist unentschieden: nichts "
            "zugestellt", user_id,
        )
        return False

    # Aktuelle Emotion und Modus aus letzten Turns
    turns: list[dict] = session_turns_retrieve(redis_client, user_id, ASSISTANT_USER_ID)
    user_emotion:     str = "neutral"
    gespraechs_modus: str = ""

    for turn in reversed(turns):
        if turn.get("rolle") == "user" and turn.get("emotion"):
            user_emotion     = turn["emotion"]
            gespraechs_modus = turn.get("modus", "")
            break

    # Besten Eintrag finden (thematisch + emotional + modus)
    eintrag, index = _besten_eintrag_finden(
        redis_client, user_id, gespraechs_vector,
        user_emotion, gespraechs_modus,
    )

    if eintrag is None:
        return False

    # Das Wissensstueck selbst ist der Reiz — nicht ein daraus formulierter
    # Satz. Der AgentGraph laesst den Gedanken entstehen (Kontext, Bewertung,
    # Ablage), der CharacterGraph denkt ihn dann: Emotion, Assoziation, Stimme.
    # Vorher sprach die Delivery den Gedanken aus, bevor er gedacht war.
    wissensstueck: str = (eintrag.get("inhalt", "") or "").strip()
    if not wissensstueck:
        logger.error(
            f"Delivery: Stack-Eintrag ohne Inhalt — Impuls verworfen "
            f"(thema='{eintrag.get('thema', '')[:40]}', index={index})"
        )
        return False

    # Ohne Zuhoerer kein Impuls: der CharacterGraph wuerde eine Antwort
    # erzeugen, die niemand empfaengt. Bewusst wie bisher gehalten.
    if not websocket_map.get(user_id):
        logger.warning(f"Delivery: Kein WebSocket für '{user_id}' — Impuls verworfen")
        return False

    # Eine turn_id pro CharacterGraph-Durchlauf (Glossar §8). Sie entsteht
    # HIER, beim Ausloeser, und wird an beide Graphen gereicht — genau wie
    # api/chat.py sie fuer einen Nutzer-Turn erzeugt. Wer spaeter eine
    # Gedankenkette feuert, erzeugt eine eigene; nur der Thinker-Retry erbt.
    turn_id: str = uuid.uuid4().hex

    # AgentGraph: das Entstehen des Gedankens — Spiegel zum HumanGraph.
    logger.info(f"Delivery: AgentGraph-Check — compiled={compiled_agent_graph is not None}, instance={agent_graph is not None}")

    if compiled_agent_graph and agent_graph:
        try:
            logger.info(
                f"Delivery: AgentGraph — erzeuge State fuer user='{user_id}', "
                f"character='{ASSISTANT_USER_ID}', rolle='character', turn_id={turn_id}"
            )
            agent_state = agent_graph.create_state(
                user_prompt    = wissensstueck,
                user_id        = user_id,
                character_id   = ASSISTANT_USER_ID,
                ei_calc_rolle  = "character",
                turn_id        = turn_id,
            )
            logger.info(f"Delivery: AgentGraph — State erzeugt, starte invoke...")
            # ── Graph-Invoke async-isiert (Microservice-Welle Block 2 Phase 4, G6) ──
            # compiled_agent_graph.invoke ist ein kompletter sync LangGraph-
            # Durchlauf — die migrierten Worker-Calls darin (submit_sync) sind
            # genau dann KORREKT, wenn der Graph in einem Worker-Thread laeuft,
            # weil submit_sync aus dem Worker-Thread in den Worker-Loop bruckt.
            # asyncio.to_thread schiebt den ganzen invoke in den to_thread-Pool,
            # damit der Haupt-Loop nicht blockiert wird (async-Bruecken-Lesson).
            # Rueckgabewert wird wie zuvor verworfen — nur Seiteneffekte (Salienz,
            # pending_writes, Dispatcher-Writes) sind relevant.
            await asyncio.to_thread(compiled_agent_graph.invoke, agent_state)
            logger.info(f"Delivery: AgentGraph — Analyse abgeschlossen für '{eintrag.get('thema', '')[:40]}'")
        except Exception as agent_fehler:
            logger.error(f"Delivery: AgentGraph-Fehler — {type(agent_fehler).__name__}: {agent_fehler}", exc_info=True)
    else:
        logger.warning("Delivery: AgentGraph NICHT verfügbar — übersprungen")

    # ── Der Gedanke geht in den CharacterGraph ──────
    # Dieselbe Form wie api/chat.py fuer einen Nutzer-Turn: source unterscheidet
    # sich, der Weg nicht. Der Consumer laesst source="character" ohne Debounce
    # durch, faehrt den vollen Graphen und sendet die Antwort des Responders als
    # character_response an die Clients. Der Dispatcher schreibt dabei den
    # turn_roh — der erste vollstaendige Rohturn ohne Nutzer-Reiz.
    #
    # Das Payload traegt nur, was der Stack-Eintrag wirklich hat. Die uebrigen
    # EI-Dimensionen bleiben leer statt plausibel gefuellt: ein erfundener
    # Reiz-Zustand waere von einem gemessenen nicht mehr unterscheidbar.
    if not _impuls_in_den_charaktergraph(
        redis_client, user_id, turn_id, wissensstueck, eintrag,
    ):
        # Keine Rueckfallebene. Der Fehler ist bereits laut protokolliert; der
        # Stack-Eintrag bleibt liegen und wird beim naechsten Zyklus erneut
        # versucht. Nichts halb Gedachtes verlaesst das System.
        return False

    # Vom Stack entfernen (erst NACHDEM der Impuls seinen Weg genommen hat)
    _stack_eintrag_entfernen(redis_client, user_id, index)

    # Deduplizierung: Ähnliche Einträge gleich mit entfernen
    _stack_aehnliche_entfernen(
        redis_client, user_id,
        eintrag.get("embedding", []),
    )

    # Burst-Counter erhöhen
    _burst_erhoehen(redis_client, user_id)

    return True


def _impuls_in_den_charaktergraph(
    redis_client:  redis.Redis,
    user_id:       str,
    turn_id:       str,
    wissensstueck: str,
    eintrag:       dict,
) -> bool:
    """Feuert das Event, mit dem der CharacterGraph den Gedanken denkt.

    Der Pixie-Impuls ist ein Reiz wie ein Nutzer-Prompt, aber nicht auf
    demselben Platz: Er geht als `eigener_gedanke` ins Payload, der Consumer
    faehrt den vollen Graphen, der Responder gibt ihm eine Stimme, der
    Dispatcher schreibt den Rohturn. **Der Reiz-Platz bleibt leer** — was dort
    stuende, waere eine Aeusserung des Menschen, und es gab keine.

    Vorbedingung: turn_id und wissensstueck sind gesetzt.
    Nachbedingung: genau ein Event mit source="character" liegt in der Queue.
    Fehlerfaelle: leere Eingabe oder Redis-Fehler (error, False) — der
    Aufrufer faellt dann auf die nuechterne Zustellung zurueck. Die Funktion
    wirft nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turn_id or not wissensstueck:
        logger.error(
            f"Delivery: Impuls ohne turn_id oder Inhalt — nicht in den "
            f"CharacterGraph gegeben (turn_id='{turn_id}', laenge={len(wissensstueck)})"
        )
        return False

    # ── Verarbeitung ────────────────────────────
    try:
        event_id: str = event_erzeugen(
            redis_client = redis_client,
            user_id      = user_id,
            character_id = ASSISTANT_USER_ID,
            source       = "character",
            typ          = "message",
            payload      = {
                "turn_id":          turn_id,
                # Der Gedanke steht auf seinem eigenen Platz — und **nur**
                # dort. `user_prompt` fehlt im Payload, weil auf diesem Weg
                # niemand gesprochen hat; ein leeres Feld waere dieselbe
                # Aussage, ein gefuelltes eine Aeusserung, die es nicht gab.
                "eigener_gedanke":  wissensstueck,
                # Ausdruecklicher Herkunfts-Marker statt Ableitung aus
                # source="character": Der Thinker-Retry traegt dieselbe source,
                # ist aber ein Wiederholungsversuch auf eine NUTZER-Aeusserung.
                # Wer beides ueber source unterscheiden wollte, raete.
                "reiz_herkunft":    "eigener_impuls",
                "current_emotion":  eintrag.get("emotion", ""),
                "gespraechs_modus": eintrag.get("modus", ""),
                "prompt_thema":     eintrag.get("thema", ""),
                "impuls_aufgabe":   eintrag.get("aufgabe", ""),
            },
        )
    except Exception as ex:
        logger.error(
            f"Delivery: Event fuer den CharacterGraph fehlgeschlagen — "
            f"turn_id={turn_id}, thema='{eintrag.get('thema', '')[:40]}', fehler={ex}",
            exc_info=True,
        )
        return False

    # ── Ausgabe-Verifikation ────────────────────
    if not event_id:
        logger.error(
            f"Delivery: event_erzeugen lieferte keine event_id — turn_id={turn_id}"
        )
        return False

    logger.info(
        f"Delivery: Impuls in den CharacterGraph gegeben — turn_id={turn_id}, "
        f"event_id={event_id}, thema='{eintrag.get('thema', '')[:40]}', "
        f"{len(wissensstueck)} Zeichen"
    )
    return True


# ─────────────────────────────────────────────
# Haupt-Loop: Prüft periodisch alle User
# ─────────────────────────────────────────────
async def shadow_delivery_loop(
    redis_client:  redis.Redis,
    websocket_map: dict,
    llm_lock,
    compiled_agent_graph = None,
    agent_graph          = None,
) -> None:
    """
    Endlos-Loop, läuft als asyncio-Task.
    Prüft alle 5 Sekunden ob Delivery-Bedingungen erfüllt sind.
    """
    logger.info("Shadow Delivery Service gestartet.")

    while True:
        try:
            await asyncio.sleep(PRÜF_INTERVALL)

            if shutdown_event.is_set():
                logger.info("Shadow Delivery: Shutdown erkannt — beende Loop")
                break

            # Alle User mit aktiven WebSocket-Verbindungen prüfen
            for user_id in list(websocket_map.keys()):

                # ── Prüfung 0: Wartet ein Agent auf eine Antwort? ──
                if _rueckfrage_offen(redis_client, user_id):
                    continue

                # ── Prüfung 1: Burst-Limit ────────
                if not _burst_erlaubt(redis_client, user_id):
                    continue

                # ── Prüfung 2: Stack leer? ────────
                stack_laenge: int = redis_client.llen(f"shadow_stack:{user_id}")

                if stack_laenge == 0:
                    continue

                # ── Prüfung 3: Trigger ermitteln ──
                momentum: str | None = redis_client.get(f"momentum:{user_id}")
                last_raw: str | None = redis_client.get(f"last_activity:{user_id}")

                if isinstance(momentum, bytes):
                    momentum = momentum.decode()
                if isinstance(last_raw, bytes):
                    last_raw = last_raw.decode()

                trigger: str = ""

                # Trigger 1: Momentum low
                if momentum == "low":
                    # Cooldown prüfen
                    if _cooldown_aktiv(redis_client, user_id):
                        continue

                    trigger = "momentum_low"

                    # Momentum verbrauchen (nicht nochmal triggern)
                    redis_client.delete(f"momentum:{user_id}")

                    # Kurze Pause für natürliches Timing
                    await asyncio.sleep(MOMENTUM_PAUSE)

                # Trigger 2: Timeout (Inaktivität)
                elif last_raw:
                    try:
                        letzte_aktivitaet: float = float(last_raw)
                        inaktiv_seit:      float = time.time() - letzte_aktivitaet

                        if inaktiv_seit >= INAKTIVITAET_GRENZE:
                            # Nicht feuern wenn noch kein Gespräch läuft
                            turns: list = session_turns_retrieve(redis_client, user_id, ASSISTANT_USER_ID)
                            if not turns:
                                continue

                            # Cooldown prüfen
                            if _cooldown_aktiv(redis_client, user_id):
                                continue

                            trigger = "timeout"

                            # Timeout verbrauchen (last_activity aktualisieren)
                            redis_client.set(
                                f"last_activity:{user_id}",
                                str(time.time()),
                                ex=7200,
                            )

                    except (ValueError, TypeError):
                        continue
                else:
                    continue

                if not trigger:
                    continue

                logger.info(f"Delivery: Trigger '{trigger}' für '{user_id}'")

                # ── LLM-Lock prüfen (GPU-Modell nicht blockieren) ──
                acquired: bool = llm_lock.acquire(blocking=False)

                if not acquired:
                    logger.debug("Delivery: LLM belegt — verschiebe auf nächsten Zyklus")
                    continue

                try:
                    gesendet: bool = await _delivery_ausfuehren(
                        redis_client, user_id, websocket_map,
                        compiled_agent_graph, agent_graph,
                    )

                    if gesendet:
                        # Cooldown setzen — wird durch nächste User-Aktion gelöscht
                        _cooldown_setzen(redis_client, user_id)

                        # Prüfe ob thematische Fortsetzung möglich
                        # (nächster Zyklus wird das über Similarity entscheiden)
                        logger.info(f"Delivery: Erfolgreich für '{user_id}' (trigger={trigger})")

                finally:
                    llm_lock.release()

        except asyncio.CancelledError:
            logger.info("Shadow Delivery Service beendet.")
            break

        except Exception as fehler:
            logger.exception(f"{type(fehler).__name__}: Delivery-Loop: Unerwarteter Fehler")
            await asyncio.sleep(PRÜF_INTERVALL)
