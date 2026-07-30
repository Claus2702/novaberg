"""
Drive-Endpunkte — Observability fuer Novas Antrieb.

Liefert Lese-Zugriff auf Ziele und kurzfristige Drive-Daten:
* Lang- und mittelfristige Ziele aus PostgreSQL (`ziele`-Tabelle).
* Kurzfristige Daten (Gespraechsvektor, aktivierte Ziele,
  Gravitationsterm) aus Redis — werden vom Dispatcher nach jedem Turn
  geschrieben.

Reine Datenabfrage, kein LLM-Call, keine Graph-Ausfuehrung.
"""

import json
import logging
from collections import Counter

import numpy as np

from fastapi           import APIRouter
from fastapi.responses import JSONResponse

import psycopg2

from config import (
    redis_client,
    POSTGRES_URL,
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    GRAVITATIONS_SCHWELLE,
    GRAVITATIONS_SALIENZ_FAKTOR,
    ZIEL_MITTELFRISTIG_DECAY_TAGE,
    ZIEL_MAX_LANGFRISTIG,
    ZIEL_MAX_MITTELFRISTIG,
)
from ei.gravitation import _cosine_similarity
from memory.session import session_turns_retrieve
from memory.ziele   import ziele_aktive_laden

logger = logging.getLogger("ki_server.drive")

router = APIRouter(prefix="/drive", tags=["Drive"])


def short_term_redis_key(user_id: str, character_id: str) -> str:
    """Redis-Key-Pattern fuer kurzfristige Drive-Daten."""
    return f"drive:short_term:{user_id}:{character_id}"


def _goal_row_to_dict(row: tuple) -> dict:
    """Mappt eine Zeile der ziele-Tabelle auf das API-Format mit englischen Keys."""
    created_at = row[6]
    updated_at = row[7]
    return {
        "id":         row[0],
        "goal_text":  row[1],
        "motivation": float(row[2]) if row[2] is not None else 0.0,
        "emotion":    row[3] or "",
        "arousal":    float(row[4]) if row[4] is not None else 0.0,
        "active":     bool(row[5]),
        "created_at": created_at.isoformat() if created_at else "",
        "updated_at": updated_at.isoformat() if updated_at else "",
    }


def _short_term_load(user_id: str, character_id: str) -> dict | None:
    """Liest kurzfristige Drive-Daten aus Redis. Gibt None zurueck wenn leer."""
    key: str = short_term_redis_key(user_id, character_id)
    raw: str | None = redis_client.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as fehler:
        logger.warning(f"Drive: Kurzfristig-Daten unter '{key}' nicht parsebar — {fehler}")
        return None


@router.get("/gv_detail")
def GvDetailLesen(user_id: str = DEFAULT_USER_ID, character_id: str = ASSISTANT_USER_ID):
    """Liefert das letzte vom Dispatcher persistierte GV-Detail.

    Key: gv:detail:{user_id}:{character_id}. Wird vom GV-Panel beim
    Oeffnen aufgerufen, damit ein Stand sichtbar ist, bevor der naechste
    Turn ueber WebSocket frische Daten liefert.
    """
    key: str = f"gv:detail:{user_id}:{character_id}"
    raw: str | None = redis_client.get(key)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as fehler:
        logger.warning(f"Drive/GvDetail: '{key}' nicht parsebar — {fehler}")
        return {}


@router.get("/goals")
def GoalsLesen():
    """Liefert alle Ziele und den aktuellen kurzfristigen Drive-Zustand.

    Lang- und mittelfristige Ziele kommen aus PostgreSQL (aktiv + inaktiv,
    sortiert nach `active DESC, motivation DESC`). Kurzfristige Daten
    kommen aus Redis (zuletzt geschriebener Snapshot vom Dispatcher).
    """
    long_term: list[dict] = []
    mid_term:  list[dict] = []

    try:
        conn   = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, zielsatz, motivation, emotion, arousal, aktiv,
                   erstellt_am, aktualisiert_am, ziel_typ
            FROM ziele
            WHERE user_id = %s
            ORDER BY ziel_typ, aktiv DESC, motivation DESC
            """,
            (ASSISTANT_USER_ID,),
        )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            ziel_typ: str  = row[8]
            entry:    dict = _goal_row_to_dict(row)
            if ziel_typ == "langfristig":
                long_term.append(entry)
            elif ziel_typ == "mittelfristig":
                mid_term.append(entry)

        logger.info(
            f"Drive/Goals: {len(long_term)} langfristig, "
            f"{len(mid_term)} mittelfristig geladen"
        )

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Drive/Goals: Datenbank-Fehler")
        return JSONResponse(
            status_code=503,
            content={"error": f"Ziele konnten nicht geladen werden: {fehler}"},
        )

    short_term: dict | None = _short_term_load(DEFAULT_USER_ID, ASSISTANT_USER_ID)

    return {
        "long_term":  long_term,
        "mid_term":   mid_term,
        "short_term": short_term,
        "config": {
            "gravity_threshold": GRAVITATIONS_SCHWELLE,
            "salience_factor":   GRAVITATIONS_SALIENZ_FAKTOR,
            "max_long_term":     ZIEL_MAX_LANGFRISTIG,
            "max_mid_term":      ZIEL_MAX_MITTELFRISTIG,
            "decay_days":        ZIEL_MITTELFRISTIG_DECAY_TAGE,
        },
    }


# ─────────────────────────────────────────────────────────────────────
# Gravitationsgraph (Chat 68 — Visualisierung)
# ─────────────────────────────────────────────────────────────────────
_GOAL_TYPE_MAP: dict[str, str] = {
    "langfristig":   "long_term",
    "mittelfristig": "mid_term",
}


# Force-Directed Layout — Konstanten
_FORCE_C_REPEL:    float = 0.01    # Coulomb-artige Abstossung
_FORCE_C_ATTRACT:  float = 0.05    # Federkraft (proportional zu similarity)
_FORCE_ITERATIONS: int   = 150
_FORCE_EPSILON:    float = 0.001
_FORCE_INITIAL_TEMP: float = 0.1
# Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.1 — im neuen
# Raum (Grundrauschen 0.16) laege 0.1 unter dem Rauschen, alles zoege sich an.
# Nur Visualisierung (GravityMap-Layout), keine Gedaechtnis-Entscheidung.
_FORCE_ATTRACT_THRESHOLD: float = 0.25


def _force_directed_layout(
    embeddings: list[list[float]],
    iterations: int = _FORCE_ITERATIONS,
    seed: int = 42,
) -> list[tuple[float, float]]:
    """Fruchterman-Reingold-aehnliches Force-Directed Layout in 2D.

    Berechnet 2D-Positionen fuer N Nodes basierend auf ihren Embedding-
    Aehnlichkeiten. Aehnliche Nodes ziehen sich an (Federkraft propor-
    tional zur Cosine-Similarity), alle Nodes stossen sich gegenseitig
    ab (Coulomb-artig, ~1/d²). Eine linear abnehmende Temperatur
    begrenzt die maximale Verschiebung pro Iteration und sorgt fuer
    Konvergenz.

    Determinismus: Gleiche Embeddings → gleiche Positionen (durch fixen
    Seed). Wenn ein neuer Turn dazukommt, verschieben sich die be-
    stehenden Nodes nur geringfuegig.

    Returns:
        Liste von (x, y)-Tupeln, normalisiert auf 0.05–0.95.
    """
    n: int = len(embeddings)
    if n == 0:
        return []
    if n == 1:
        return [(0.5, 0.5)]

    rng: np.random.Generator = np.random.default_rng(seed)
    pos: np.ndarray = rng.random((n, 2)).astype(np.float32)

    # Cosine-Similarity-Matrix (n × n) per Matrixmultiplikation.
    matrix:     np.ndarray = np.array(embeddings, dtype=np.float32)
    norms:      np.ndarray = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    normalized: np.ndarray = matrix / norms
    sim:        np.ndarray = normalized @ normalized.T  # (n, n)

    # Anziehungs-Maske: nur Paare mit Similarity ueber Schwelle.
    attract_mask: np.ndarray = (sim > _FORCE_ATTRACT_THRESHOLD).astype(np.float32)
    np.fill_diagonal(attract_mask, 0.0)

    for iteration in range(iterations):
        # Temperatur linear von _FORCE_INITIAL_TEMP gegen 0.
        temp: float = _FORCE_INITIAL_TEMP * (1.0 - iteration / iterations)

        # Paarweise Differenzvektoren delta[i, j] = pos[i] - pos[j]  (n, n, 2)
        delta: np.ndarray = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
        distance: np.ndarray = np.sqrt(np.sum(delta * delta, axis=2)) + _FORCE_EPSILON
        # Selbstreferenz nicht zaehlen.
        np.fill_diagonal(distance, _FORCE_EPSILON)

        direction: np.ndarray = delta / distance[:, :, np.newaxis]  # (n, n, 2)

        # Abstossung: ~1/d², nach aussen (in delta-Richtung).
        repel_mag: np.ndarray = _FORCE_C_REPEL / (distance ** 2)
        np.fill_diagonal(repel_mag, 0.0)
        repel_force: np.ndarray = direction * repel_mag[:, :, np.newaxis]

        # Anziehung: ~ similarity * distance, gegen die delta-Richtung.
        attract_mag: np.ndarray = (
            _FORCE_C_ATTRACT * sim * distance * attract_mask
        )
        attract_force: np.ndarray = -direction * attract_mag[:, :, np.newaxis]

        # Gesamtkraft pro Node: Summe ueber alle anderen.
        total: np.ndarray = (repel_force + attract_force).sum(axis=1)  # (n, 2)

        # Verschiebung auf temp begrenzen (max-Step).
        force_mag: np.ndarray = np.linalg.norm(total, axis=1, keepdims=True)
        force_mag = np.maximum(force_mag, _FORCE_EPSILON)
        capped: np.ndarray = total * np.minimum(1.0, temp / force_mag)

        pos = pos + capped

    # Auf 0.05–0.95 normieren (mit Rand fuer Labels).
    for dim in range(2):
        min_val: float = float(pos[:, dim].min())
        max_val: float = float(pos[:, dim].max())
        span:    float = max_val - min_val
        if span > 0:
            pos[:, dim] = 0.05 + 0.9 * (pos[:, dim] - min_val) / span
        else:
            pos[:, dim] = 0.5

    return [(float(x), float(y)) for x, y in pos]


def _content_preview(text: str, limit: int = 80) -> str:
    """Schneidet einen Turn-Inhalt fuer das Panel-Label auf eine Vorschau zu."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def _kurzlabel_aus_zielsatz(zielsatz: str) -> str:
    """Fallback-Label aus dem Zielsatz fuer Altbestand ohne thema."""
    text: str = (zielsatz or "").strip().rstrip(".… ")
    if not text:
        return ""
    lower: str = text.lower()
    for marker in ("über ", "wie ", "dass ", "warum "):
        pos: int = lower.find(marker)
        if pos >= 0:
            rest: str = text[pos + len(marker):].strip().rstrip(".… ")
            return " ".join(rest.split()[:4])
    words: list[str] = [w for w in text.split() if len(w) > 2]
    return " ".join(words[-3:]) if len(words) >= 3 else text[:30]


def _aggregate_dominant_topics(
    user_turns: list[dict],
    limit: int = 8,
    min_count: int = 1,
) -> list[str]:
    """Aggregiert die haeufigsten Themen ueber alle Turns.

    Sortiert nach Haeufigkeit, gibt maximal ``limit`` einzigartige Themen
    zurueck. Themen werden case-preserving als erste gesehene Schreibweise
    zurueckgegeben.
    """
    counter: Counter[str] = Counter()
    first_seen: dict[str, str] = {}

    for turn in user_turns:
        themen = turn.get("themen") or []
        if not isinstance(themen, list):
            continue
        for thema in themen:
            if not isinstance(thema, str):
                continue
            schluessel: str = thema.strip().lower()
            if not schluessel:
                continue
            counter[schluessel] += 1
            if schluessel not in first_seen:
                first_seen[schluessel] = thema.strip()

    haeufigste: list[tuple[str, int]] = [
        (k, c) for k, c in counter.most_common() if c >= min_count
    ]
    return [first_seen[k] for k, _ in haeufigste[:limit]]


@router.get("/gravity_map")
def GravityMapLesen():
    """Liefert Turns + Ziele auf einer 2D-Ebene plus Gravitations-Connections.

    Datenfluss:
      1. Session-Turns aus Redis (Default-Perspektive: meister/nova).
      2. User-Turns mit Embedding filtern, Themen sammeln.
      3. Aktive Ziele aus PostgreSQL laden (mit Embedding).
      4. Alle Embeddings gemeinsam per Force-Directed Layout auf 2D legen
         (Aehnliches zieht sich an, alle Nodes stossen sich ab).
      5. Pro (Turn, Ziel) Cosine-Similarity berechnen — Connections nur ueber
         GRAVITATIONS_SCHWELLE.
      6. Dominante Themen ueber alle Turns aggregieren.

    Falls weniger als zwei User-Turns mit Embedding existieren, gibt es keine
    sinnvolle Projektion. Wir geben dann eine leere Turn-Liste zurueck und
    streuen die Ziele entlang der x-Achse mit y=0.5.
    """
    user_id:      str = DEFAULT_USER_ID
    character_id: str = ASSISTANT_USER_ID

    # ── 1+2. Session-Turns: User-Turns mit Embedding rausziehen ──
    turns_raw: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)

    user_turns: list[dict] = []
    for idx, turn in enumerate(turns_raw):
        if turn.get("rolle") != "user":
            continue

        embedding = turn.get("embedding")
        if not embedding:
            continue

        # Defensive: das Embedding kommt als list[float] aus JSON, sicherstellen.
        if not isinstance(embedding, list):
            continue

        themen_raw = turn.get("themen") or []
        themen: list[str] = [
            t.strip() for t in themen_raw
            if isinstance(t, str) and t.strip()
        ] if isinstance(themen_raw, list) else []

        user_turns.append({
            "turn_number":  idx + 1,
            "inhalt":       turn.get("inhalt", ""),
            "emotion":      turn.get("emotion", "neutral") or "neutral",
            "arousal":      float(turn.get("arousal", 0.5) or 0.5),
            "embedding":    [float(x) for x in embedding],
            "themen":       themen,
        })

    # ── 3. Aktive Ziele mit Embedding laden ──
    ziele_raw: list[dict] = ziele_aktive_laden(POSTGRES_URL, user_id=ASSISTANT_USER_ID)

    goals: list[dict] = []
    for ziel in ziele_raw:
        ziel_embedding = ziel.get("embedding")
        if not ziel_embedding:
            continue

        goals.append({
            "goal_text":   ziel.get("zielsatz", "") or "",
            "goal_type":   _GOAL_TYPE_MAP.get(
                ziel.get("ziel_typ", "") or "", "mid_term",
            ),
            "motivation":  float(ziel.get("motivation", 0.0) or 0.0),
            "emotion":     ziel.get("emotion", "") or "neutral",
            "theme_label": (ziel.get("thema") or "").strip()
                           or _kurzlabel_aus_zielsatz(ziel.get("zielsatz", "")),
            "embedding":   [float(x) for x in ziel_embedding],
        })

    logger.info(
        f"Drive/GravityMap: {len(user_turns)} User-Turns mit Embedding, "
        f"{len(goals)} Ziele mit Embedding"
    )

    dominant_topics: list[str] = _aggregate_dominant_topics(user_turns)

    # ── Sonderfall: nicht genug Turns fuer Force-Directed Layout ──
    if len(user_turns) < 2:
        # Ziele entlang x-Achse verteilen, y=0.5. Reihenfolge bleibt stabil.
        anzahl: int = len(goals)
        if anzahl == 0:
            spread_xs: list[float] = []
        elif anzahl == 1:
            spread_xs = [0.5]
        else:
            spread_xs = [0.05 + 0.9 * i / (anzahl - 1) for i in range(anzahl)]

        goals_response: list[dict] = []
        for goal, x in zip(goals, spread_xs):
            goals_response.append({
                "x":                    float(x),
                "y":                    0.5,
                "goal_text":            goal["goal_text"],
                "goal_type":            goal["goal_type"],
                "motivation":           goal["motivation"],
                "emotion":              goal["emotion"],
                "theme_label":          goal["theme_label"],
                # Ohne Connections kein Ereignishorizont.
                "event_horizon_radius": 0.0,
            })

        return {
            "turns":           [],
            "goals":           goals_response,
            "connections":     [],
            "dominant_topics": dominant_topics,
        }

    # ── 4. Force-Directed Layout fuer Turns + Ziele gemeinsam ──
    all_embeddings: list[list[float]] = (
        [t["embedding"] for t in user_turns]
        + [g["embedding"] for g in goals]
    )
    coords: list[tuple[float, float]] = _force_directed_layout(all_embeddings)

    n_turns: int = len(user_turns)
    turn_coords: list[tuple[float, float]] = coords[:n_turns]
    goal_coords: list[tuple[float, float]] = coords[n_turns:]

    turns_response: list[dict] = []
    for turn, (x, y) in zip(user_turns, turn_coords):
        turns_response.append({
            "x":               float(x),
            "y":               float(y),
            "turn_number":     turn["turn_number"],
            "content_preview": _content_preview(turn["inhalt"]),
            "emotion":         turn["emotion"],
            "arousal":         turn["arousal"],
            "topics":          turn["themen"],
        })

    goals_response: list[dict] = []
    for goal, (x, y) in zip(goals, goal_coords):
        goals_response.append({
            "x":                    float(x),
            "y":                    float(y),
            "goal_text":            goal["goal_text"],
            "goal_type":            goal["goal_type"],
            "motivation":           goal["motivation"],
            "emotion":              goal["emotion"],
            "theme_label":          goal["theme_label"],
            # Wird unten gesetzt (max. Distanz zu einem verbundenen Turn).
            "event_horizon_radius": 0.0,
        })

    # ── 5. Gravitations-Connections berechnen ──
    connections: list[dict] = []
    for turn_idx, turn in enumerate(user_turns):
        for goal_idx, goal in enumerate(goals):
            similarity: float = _cosine_similarity(turn["embedding"], goal["embedding"])
            gravity_strength: float = similarity * goal["motivation"]

            if similarity >= GRAVITATIONS_SCHWELLE:
                connections.append({
                    "turn_index":       turn_idx,
                    "goal_index":       goal_idx,
                    "similarity":       round(float(similarity), 3),
                    "gravity_strength": round(float(gravity_strength), 3),
                })

    # ── 6. Ereignishorizont pro Ziel: max. Abstand zum verbundenen Turn ──
    # Definition: alle Turn-Punkte innerhalb dieses Radius haben Connection
    # zu diesem Ziel. Ohne Connections bleibt der Radius bei 0.0.
    goal_max_dist: dict[int, float] = {}
    for conn in connections:
        t_idx: int = conn["turn_index"]
        g_idx: int = conn["goal_index"]
        tx, ty = turn_coords[t_idx]
        gx, gy = goal_coords[g_idx]
        dist: float = ((tx - gx) ** 2 + (ty - gy) ** 2) ** 0.5
        if dist > goal_max_dist.get(g_idx, 0.0):
            goal_max_dist[g_idx] = dist

    for idx, entry in enumerate(goals_response):
        entry["event_horizon_radius"] = round(goal_max_dist.get(idx, 0.0), 4)

    logger.info(
        f"Drive/GravityMap: {len(turns_response)} Turns, "
        f"{len(goals_response)} Ziele, {len(connections)} Connections, "
        f"{len(dominant_topics)} dominante Themen"
    )

    return {
        "turns":           turns_response,
        "goals":           goals_response,
        "connections":     connections,
        "dominant_topics": dominant_topics,
    }
