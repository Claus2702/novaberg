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

Flood-Schutz — **seit dem 15.08.2026 ohne die stuendliche Decke**
(`novaberg-eigenzeit_k.md` §2.5). Was den Zeitpunkt beurteilt, sind jetzt die
Riegel; was die Wiederholung begrenzt, ist der Zaehler:

  - Riegel 2 (`frequenz`): Hat Nova gerade die Initiative? Sonst kein Impuls.
  - Burst-Limit: hoechstens `MAX_BURST` Impulse ohne Reaktion des Menschen.

Der Kopf nannte hier bis zum 15.08.2026 „Max 3" — `MAX_BURST` stand zu dem
Zeitpunkt bereits auf 2.
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
from ei.utils      import NEGATIVE_EMOTIONEN
from memory.haltung import haltung_lesen
from memory.pipeline_log import log_berechnung
from memory.session import session_turns_retrieve
from services.events import event_erzeugen
from services.model_services import model_service, EmbedRequest
from services.pixie.riegel import (
    Riegelkette,
    initiative_pruefen,
    zuwendung_pruefen,
)

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

# **Die stuendliche Decke ist am 15.08.2026 gefallen** — mit dem Bau von
# Riegel 2 (`novaberg-eigenzeit_k.md` §2.5). Sie war nie eine Aussage ueber den
# Gedanken, sondern ein Ersatz fuer ein Urteil, das es noch nicht gab; sie war
# ueberdies in die falsche Richtung geneigt, weil sie umso grosszuegiger wurde,
# je laenger niemand da war.
#
# **Was bleibt, ist der Burst-Zaehler** — und er ist etwas anderes als die
# Decke. Die Decke sagte *nicht jetzt*; der Zaehler sagt *nicht schon wieder,
# ohne dass jemand geantwortet hat*. Nach dem Wegfall der Uhr ist er das
# einzige, was verhindert, dass Nova in die Stille hineinredet.
#
# Diese Frist ist nicht seine Sperre, sondern sein **Gedaechtnis**: Nach ihr
# hat der Zaehler vergessen, wie viele Impulse ohne Antwort blieben. Geloescht
# wird er ohnehin bei jeder Aeusserung des Menschen.
BURST_TTL:            int   = 3600    # Wie lange der Burst-Zaehler sich erinnert

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
def _emotional_kompatibel(
    stack_aufgabe: str,
    user_emotion:  str,
) -> bool:
    """Prüft ob ein Impuls zur aktuellen User-Emotion passt.

    **Die Menge der negativen Emotionen kommt aus `ei.utils`, nicht von hier.**
    Bis zum 23.08.2026 stand daneben ein Literal mit vier Namen — eine echte
    Teilmenge der acht, die `EMOTION_SEKTOR_MAP` als negativ führt. `wut`,
    `verzweiflung` und `enttaeuschung` fielen deshalb auf den Schlusszweig
    *alle anderen Kombinationen: erlaubt*: Ein Recherche-Einwurf ging hinaus,
    während der Mensch wütend war — genau der Fall, den dieser Riegel
    verhindern soll. Zwei Mengen für einen Gegenstand sind der Defekt, nicht
    die kleinere Zahl (`novaberg-ei-plutchik.md`).

    **`stress` steht in den acht und wird trotzdem vorher geprüft.** Der
    Unterschied ist nicht die Gruppe, sondern die Strenge: Bei Stress ist
    *nichts* zulässig, bei den übrigen negativen die empathische Nachfrage.
    Die Reihenfolge trägt diese Unterscheidung — wer sie umdreht, lässt unter
    Stress das Nachfragen durch.

    Vorbedingung: `stack_aufgabe` und `user_emotion` sind Zeichenketten;
    eine leere oder unbekannte Emotion ist zulässig und bedeutet *keine
    Einschränkung aus dieser Richtung*.
    Nachbedingung: True heißt, der Eintrag darf den Filter passieren — nicht,
    dass er zugestellt wird; darüber entscheiden die Filter danach.

    Args:
        stack_aufgabe: Aufgabenname des Stapel-Eintrags, z.B. `nachfragen`.
        user_emotion:  Emotion des Menschen in diesem Turn.

    Returns:
        True, wenn der Eintrag emotional passt.
    """
    # ── Verarbeitung ────────────────────────────
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
# Burst-Ruecksetzung
# ─────────────────────────────────────────────
def shadow_burst_reset(redis_client: redis.Redis, user_id: str) -> None:
    """Loescht den Burst-Zaehler — der Mensch hat geantwortet.

    **Hiess bis zum 15.08.2026 `shadow_cooldown_reset` und loeschte zwei
    Schluessel.** Mit der stuendlichen Decke ist der Cooldown-Schluessel
    weggefallen; der Name ist mitgezogen, weil ein Bezeichner, der einen nicht
    mehr existierenden Gegenstand nennt, beim naechsten Leser eine Suche nach
    etwas ausloest, das es nicht gibt.

    Der Bestandsschluessel `shadow_cooldown:*` wird **nicht** aufgeraeumt: Er
    traegt eine Frist und verschwindet von selbst, und ein Loeschlauf ueber
    fremde Schluessel gehoert nicht in eine Zustellung.

    Args:
        redis_client: Verbindung.
        user_id:      Kennung des Menschen.
    """
    # ── Ausgabe ─────────────────────────────────
    redis_client.delete(f"shadow_burst_count:{user_id}")
    logger.debug("Delivery: Burst-Zaehler zurueckgesetzt fuer '%s'", user_id)


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
    redis_client.expire(key, BURST_TTL)


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
                # Der Stand, in dem der Gedanke gefasst wurde. Er **hebt**
                # Novas Zustand beim Einwurf, wenn er hoeher liegt — der Weg
                # zurueck in ihr Element (Bauteil B). Das Feld steht immer im
                # Payload, auch leer: `None` heisst unbekannt und darf nie zu
                # einer Zahl werden, und ein weggelassenes Feld waere von
                # einem Eintrag alter Bauart nicht zu unterscheiden.
                # Der Leser liegt in `graph/reiz.py` (`LEVEL_FELD`).
                "gedanke_arousal":  eintrag.get("arousal"),
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
def _riegelkette_pruefen(
    redis_client: redis.Redis,
    user_id:      str,
    trigger:      str,
) -> Riegelkette:
    """Rechnet die billigen Riegel und haelt das Ergebnis dauerhaft fest.

    **Riegel 1 steht vor der Suche, nicht dahinter.** Will sie nicht zugehen,
    kostet die Runde nichts — kein Embedding, kein Durchlauf ueber den Stapel.
    Das ist nicht Sparsamkeit, sondern die Ordnung der Fragen: erst die Person,
    dann der Gegenstand (`novaberg-eigenzeit_k.md` §2.5).

    **Der Eintrag entsteht auch dann, wenn geblockt wird** — er ist die
    eigentliche Messgroesse des Bauteils. An einem stillen Tag ist sonst nicht
    zu unterscheiden, ob niemand zugehen wollte oder ob nichts gepasst hat.

    **Der Umfang des Eintrags ist benannt, nicht stillschweigend:** Er beginnt
    am Trigger. Was davor abbricht — eine offene Rueckfrage, ein erschoepfter
    Burst, ein leerer Stapel —, erzeugt keinen Eintrag, weil diese Abbrueche
    vor der Kette liegen und ihre Umstellung das Verbrauchsverhalten des
    Momentums aendern wuerde. Das Feld `umfang` sagt es dem Leser, damit
    niemand die Verteilung fuer die ueber **alle** Zyklen haelt.

    Args:
        redis_client: Verbindung.
        user_id:      das Paar, fuer das zugestellt werden soll.
        trigger:      `momentum_low` oder `timeout` — steht im Eintrag, weil
            die beiden verschiedene Lagen sind.

    Vorbedingung: Ein Trigger ist gefallen, Burst und Cooldown sind passiert.
    Nachbedingung: Eine Kette, in der Riegel 1 gerechnet ist. Genau ein
        Protokolleintrag, auch bei einem Fehlschlag beim Schreiben.
    Fehlerfaelle: Ein Forensik-Schreibfehler darf die Zustellung nicht
        anhalten — gekapselt und gemeldet, wie in den Knoten des Graphen.

    Returns:
        Die Kette. `durchgelassen()` sagt, ob weitergegangen wird.
    """
    # ── Verarbeitung ────────────────────────────
    kette = Riegelkette()

    # **Ein Stand, zwei Riegel.** Beide lesen denselben Schluessel; er wird
    # einmal geholt, damit sie nicht ueber zwei Lesevorgaenge hinweg
    # verschiedene Staende beurteilen — zwischen zwei `hgetall` kann ein Turn
    # liegen, und dann entschiede die Kette ueber zwei Momente zugleich.
    stand = haltung_lesen(redis_client, user_id, ASSISTANT_USER_ID)
    jetzt: float = time.time()

    kette.aufnehmen(zuwendung_pruefen(stand, jetzt))

    # **Riegel 2 wird gerechnet, auch wenn Riegel 1 schon geblockt hat.** Die
    # billigen Riegel laufen alle — sonst verdeckt der erste den zweiten und
    # dessen Verteilung ist nie kalibrierbar (`novaberg-eigenzeit_k.md` §2.5).
    kette.aufnehmen(initiative_pruefen(stand, jetzt))

    # Riegel 3 ist an dieser Stelle notwendig passiert: Der Burst-Zaehler hat
    # die Runde schon vorher abgebrochen, wenn er zugeschlagen haette. Die
    # stuendliche Decke, die hier bis zum 15.08.2026 mitgemeint war, gibt es
    # nicht mehr.
    kette.gerechnet("ruhe", True, None)

    # ── Ausgabe-Verifikation ────────────────────
    inhalt: dict = {
        "schritt": "riegelkette",
        "trigger": trigger,
        "umfang":  "ab_trigger",
        **kette.als_protokoll(),
    }
    try:
        log_berechnung(
            turn_id = f"zv-{uuid.uuid4().hex}",
            node    = "zustellung",
            quelle  = "character",
            inhalt  = inhalt,
            user_id      = user_id,
            character_id = ASSISTANT_USER_ID,
        )
    except (redis.RedisError, ValueError, TypeError):
        # Nur die Fehler der Senke selbst. Ein Programmierfehler soll laut
        # sein — sonst ist er von einem ausgefallenen Speicher nicht mehr zu
        # unterscheiden.
        logger.exception(
            "Delivery: Riegel-Protokoll nicht geschrieben — die Zustellung "
            "laeuft weiter, die Reihe hat eine Luecke",
        )

    # **Hier steht ein Wort, das etwas entscheidet.** Eine unvollstaendige
    # Kette hat nichts geprueft; `durchgelassen()` antwortet darauf mit Nein,
    # und diese Zeile sagt, warum — sonst waere der Ausfall von einem
    # blockierenden Riegel nicht zu unterscheiden.
    if not kette.vollstaendig():
        logger.error(
            "Delivery: Riegelkette fuer '%s' unvollstaendig — es fehlen %s. "
            "Kein Einwurf; eine Kette ohne Pflicht-Riegel ist kein Urteil",
            user_id, kette.fehlende_pflicht(),
        )
        return kette

    logger.info("Delivery: Riegelkette fuer '%s' — %s", user_id, kette.kurzfassung())
    return kette


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

                # ── Riegel 1: will sie überhaupt zugehen? ──
                # **Vor dem LLM-Lock**, weil ein „sie will nicht" sonst erst
                # die GPU belegt, um danach nichts zu tun. Und vor der Suche,
                # weil die Ordnung der Fragen es so will: erst die Person,
                # dann der Gegenstand (novaberg-eigenzeit_k.md §2.5).
                if not _riegelkette_pruefen(redis_client, user_id, trigger).durchgelassen():
                    continue

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
                        # **Hier stand die stuendliche Decke.** Sie ist am
                        # 15.08.2026 gefallen; was den naechsten Zeitpunkt
                        # beurteilt, sind die Riegel. Der Burst-Zaehler steigt
                        # weiterhin — er zaehlt nicht die Zeit, sondern die
                        # Impulse ohne Antwort, und wird in
                        # `_delivery_ausfuehren` erhoeht.
                        logger.info(f"Delivery: Erfolgreich für '{user_id}' (trigger={trigger})")

                finally:
                    llm_lock.release()

        except asyncio.CancelledError:
            logger.info("Shadow Delivery Service beendet.")
            break

        except Exception as fehler:
            logger.exception(f"{type(fehler).__name__}: Delivery-Loop: Unerwarteter Fehler")
            await asyncio.sleep(PRÜF_INTERVALL)
