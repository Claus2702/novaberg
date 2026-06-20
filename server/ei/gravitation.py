"""
Gravitationsberechnung — Ziele als Anziehungspunkte im semantischen Raum.

Reine Funktionen ohne I/O. Berechnet die Gravitationswirkung von Zielen
auf den aktuellen Turn über Embedding-Similarity × Motivation.

Wird verwendet von:
  - graph/nodes/enricher.py  (Phase 2 — Ziele laden + Gravitation berechnen)
  - graph/nodes/salience.py  (Phase 2 — Salienz-Boost)
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import redis

from config import (
    GRAVITATIONS_SCHWELLE,
    GRAVITATIONS_SALIENZ_FAKTOR,
    EMOTIONALE_GRAVITATIONS_SCHWELLE,
    EMOTIONALE_GRAVITATION_ZEIT_HALBWERT,
    EMOTIONALE_GRAVITATION_MAX_PRO_TURN,
    EMOTIONALE_GRAVITATION_FAKTOR_KZG,
    EMOTIONALE_GRAVITATION_FAKTOR_LZG,
    REDIS_URL,
)

logger = logging.getLogger("ki_server.ei.gravitation")


@dataclass
class ActivatedGoal:
    """Ein Ziel, dessen Gravitation über der Schwelle liegt.

    Attributes:
        ziel_id: Datenbank-ID des Ziels.
        ziel_typ: "langfristig" oder "mittelfristig".
        zielsatz: Der Zieltext.
        motivation: Motivationsstärke (0.0-1.0).
        emotion: Emotionale Valenz des Ziels.
        arousal: Emotionale Intensität.
        similarity: Cosine-Similarity zwischen Turn und Ziel.
        gravitation: similarity × motivation — der effektive Gravitationswert.
    """
    ziel_id:     int
    ziel_typ:    str
    zielsatz:    str
    motivation:  float
    emotion:     str
    arousal:     float
    similarity:  float
    gravitation: float


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Berechnet die Cosine Similarity zwischen zwei Vektoren.

    Args:
        vec_a: Erster Vektor.
        vec_b: Zweiter Vektor.

    Returns:
        Cosine Similarity als Float (0.0-1.0), oder 0.0 bei leeren Vektoren.
    """
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


def ziel_gravitation_berechnen(
    turn_embedding: list[float],
    ziele: list[dict],
) -> list[ActivatedGoal]:
    """Berechnet die Gravitationswirkung aller Ziele auf den aktuellen Turn.

    Für jedes Ziel: similarity = cosine(turn, ziel), gravitation = similarity × motivation.
    Über GRAVITATIONS_SCHWELLE → aktiviert.

    Args:
        turn_embedding: Embedding des aktuellen Turns (768-dim).
        ziele: Liste von Ziel-Dicts (aus ziele_aktive_laden).

    Returns:
        Liste der aktivierten Ziele, absteigend nach Gravitation sortiert.
    """
    if not turn_embedding:
        logger.debug("Gravitation: Kein Turn-Embedding — keine Berechnung")
        return []

    if not ziele:
        logger.debug("Gravitation: Keine aktiven Ziele")
        return []

    aktiviert: list[ActivatedGoal] = []

    for ziel in ziele:
        ziel_embedding: list[float] | None = ziel.get("embedding")

        if not ziel_embedding:
            logger.debug(
                f"Gravitation: Ziel id={ziel['id']} hat kein Embedding — übersprungen"
            )
            continue

        similarity:  float = _cosine_similarity(turn_embedding, ziel_embedding)
        motivation:  float = ziel.get("motivation", 0.5)
        gravitation: float = similarity * motivation

        if gravitation >= GRAVITATIONS_SCHWELLE:
            goal = ActivatedGoal(
                ziel_id=ziel["id"],
                ziel_typ=ziel.get("ziel_typ", "mittelfristig"),
                zielsatz=ziel.get("zielsatz", ""),
                motivation=motivation,
                emotion=ziel.get("emotion", ""),
                arousal=ziel.get("arousal", 0.5),
                similarity=round(similarity, 3),
                gravitation=round(gravitation, 3),
            )
            aktiviert.append(goal)

            logger.info(
                f"Gravitation: Ziel AKTIVIERT — id={ziel['id']}, "
                f"typ={goal.ziel_typ}, sim={goal.similarity:.3f}, "
                f"mot={motivation:.2f}, grav={goal.gravitation:.3f}, "
                f"'{goal.zielsatz[:50]}'"
            )
        else:
            logger.debug(
                f"Gravitation: Ziel id={ziel['id']} unter Schwelle — "
                f"sim={similarity:.3f}, mot={motivation:.2f}, "
                f"grav={gravitation:.3f} < {GRAVITATIONS_SCHWELLE}"
            )

    # Absteigend nach Gravitationsstärke sortieren.
    aktiviert.sort(key=lambda g: g.gravitation, reverse=True)

    if aktiviert:
        logger.info(
            f"Gravitation: {len(aktiviert)} Ziele aktiviert von {len(ziele)} — "
            f"stärkstes: grav={aktiviert[0].gravitation:.3f}, "
            f"'{aktiviert[0].zielsatz[:50]}'"
        )
    else:
        logger.debug(
            f"Gravitation: 0 Ziele aktiviert von {len(ziele)} "
            f"(Schwelle={GRAVITATIONS_SCHWELLE})"
        )

    return aktiviert


def gravitationsterm_berechnen(aktivierte_ziele: list[ActivatedGoal]) -> float:
    """Berechnet den Salienz-Gravitationsterm aus aktivierten Zielen.

    Der Term ist die Summe aller Gravitationswerte, skaliert mit dem
    Salienz-Faktor. Er wird in Phase 2 auf die Basis-Salienz addiert.

    Args:
        aktivierte_ziele: Liste der aktivierten Ziele (aus ziel_gravitation_berechnen).

    Returns:
        Gravitationsterm als Float (kann > 1.0 sein, wird bei der Salienz gecapped).
    """
    if not aktivierte_ziele:
        return 0.0

    # Summe der Gravitationswerte × Salienz-Faktor.
    # Bei mehreren aktivierten Zielen verstärken sie sich.
    gesamt: float = sum(g.gravitation for g in aktivierte_ziele)
    term:   float = gesamt * GRAVITATIONS_SALIENZ_FAKTOR

    logger.debug(
        f"Gravitationsterm: {len(aktivierte_ziele)} Ziele, "
        f"summe={gesamt:.3f}, faktor={GRAVITATIONS_SALIENZ_FAKTOR}, "
        f"term={term:.3f}"
    )

    return round(term, 4)


# ─────────────────────────────────────────────
# Emotionale Gravitation (EI Phase 3)
# ─────────────────────────────────────────────

def emotionale_gravitation_scannen(
    turn_embedding: list[float],
    redis_client: redis.Redis,
    postgres_url: str,
    user_id: str,
    character_id: str,
) -> list[dict]:
    """Scannt KZG + LZG nach emotional aufgeladenen Erinnerungen.

    Berechnet die emotionale Gravitationskraft pro Eintrag:
    gravitation = similarity × gewicht × zeit_decay × quellen_faktor

    Nur Einträge über EMOTIONALE_GRAVITATIONS_SCHWELLE werden aktiviert.
    Maximal EMOTIONALE_GRAVITATION_MAX_PRO_TURN Einträge.

    Args:
        turn_embedding: Embedding des aktuellen Turns (768-dim).
        redis_client: Redis-Verbindung für KZG-Scan.
        postgres_url: PostgreSQL-URL für LZG-Scan.
        user_id: User-ID.
        character_id: Charakter-ID.

    Returns:
        Liste der aktivierten emotionalen Erinnerungen, absteigend nach Gravitation.
    """
    if not turn_embedding:
        return []

    kandidaten: list[dict] = []
    jetzt: datetime = datetime.now(timezone.utc)

    # ── KZG-Scan (Redis) ──
    kandidaten.extend(
        _kzg_emotionale_eintraege(turn_embedding, redis_client, user_id, character_id, jetzt)
    )

    # ── LZG-Scan (PostgreSQL) ──
    kandidaten.extend(
        _lzg_emotionale_eintraege(turn_embedding, postgres_url, user_id, character_id, jetzt)
    )

    # Sortieren nach Gravitation, Top-N
    kandidaten.sort(key=lambda k: k["gravitation"], reverse=True)
    aktiviert: list[dict] = kandidaten[:EMOTIONALE_GRAVITATION_MAX_PRO_TURN]

    if aktiviert:
        logger.info(
            f"Emotionale Gravitation: {len(aktiviert)} von {len(kandidaten)} "
            f"Kandidaten aktiviert"
        )

    return aktiviert


def _zeit_decay_faktor(erstellt: datetime, jetzt: datetime) -> float:
    """Berechnet den zeitlichen Decay-Faktor für emotionale Gravitation.

    Exponentieller Verfall mit EMOTIONALE_GRAVITATION_ZEIT_HALBWERT.

    Args:
        erstellt: Erstellungs-/Verstärkungszeitpunkt.
        jetzt: Aktuelle Zeit.

    Returns:
        Decay-Faktor zwischen 0.0 und 1.0.
    """
    if erstellt.tzinfo is None:
        erstellt = erstellt.replace(tzinfo=timezone.utc)

    tage: float = max(0.0, (jetzt - erstellt).total_seconds() / 86400.0)
    decay_rate: float = math.log(2) / EMOTIONALE_GRAVITATION_ZEIT_HALBWERT

    return math.exp(-decay_rate * tage)


def _kzg_emotionale_eintraege(
    turn_embedding: list[float],
    redis_client: redis.Redis,
    user_id: str,
    character_id: str,
    jetzt: datetime,
) -> list[dict]:
    """Scannt KZG-Einträge mit Emotion und berechnet Gravitation.

    Iteriert über alle KZG-Einträge des Paares, filtert auf vorhandene
    Emotion, berechnet Cosine-Similarity gegen Turn-Embedding.

    Embedding wird über einen separaten decode_responses=False-Client gelesen,
    da der Default-Client (decode_responses=True) den Float32-Blob korrumpiert.

    Args:
        turn_embedding: Embedding des aktuellen Turns.
        redis_client: Redis-Verbindung (decode_responses=True, für Text-Felder).
        user_id: User-ID.
        character_id: Charakter-ID.
        jetzt: Aktuelle Zeit für Decay.

    Returns:
        Liste von Kandidaten-Dicts über der Schwelle.
    """
    from memory.kzg import _kzg_prefix

    kandidaten: list[dict] = []
    prefix: str = _kzg_prefix(user_id, character_id)

    # Separater Raw-Client für die Embedding-Bytes
    raw_redis: redis.Redis = redis.from_url(REDIS_URL, decode_responses=False)

    for key in redis_client.scan_iter(match=prefix, count=100):
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        emotion: str = redis_client.hget(key, "emotion") or ""
        if not emotion or emotion == "neutral":
            continue

        # Embedding aus dem Raw-Client (Float32-Bytes)
        embedding_bytes = raw_redis.hget(key, "embedding")
        if not embedding_bytes:
            continue

        try:
            eintrag_embedding: list[float] = np.frombuffer(
                embedding_bytes, dtype=np.float32
            ).tolist()
        except (ValueError, TypeError):
            continue

        # Similarity berechnen
        similarity: float = _cosine_similarity(turn_embedding, eintrag_embedding)

        # Salienz als Gewicht
        salienz_raw: str = redis_client.hget(key, "salienz") or ""
        gewicht: float = 0.5
        if salienz_raw:
            try:
                gewicht = float(salienz_raw)
            except (ValueError, TypeError):
                pass

        # Arousal
        arousal_raw: str = redis_client.hget(key, "arousal") or ""
        arousal: float = 0.5
        if arousal_raw:
            try:
                arousal = float(arousal_raw)
            except (ValueError, TypeError):
                pass

        # Erstellt-Zeitpunkt für Decay (Unix-Timestamp-String, siehe kzg_store)
        erstellt_raw: str = redis_client.hget(key, "erstellt_am") or ""
        zeit_decay: float = 1.0
        if erstellt_raw:
            try:
                erstellt: datetime = datetime.fromtimestamp(
                    float(erstellt_raw), tz=timezone.utc,
                )
                zeit_decay = _zeit_decay_faktor(erstellt, jetzt)
            except (ValueError, TypeError):
                pass

        # Gravitation berechnen
        gravitation: float = similarity * gewicht * zeit_decay * EMOTIONALE_GRAVITATION_FAKTOR_KZG

        if gravitation >= EMOTIONALE_GRAVITATIONS_SCHWELLE:
            inhalt: str = redis_client.hget(key, "inhalt") or ""

            kandidaten.append({
                "emotion":     emotion,
                "arousal":     arousal,
                "similarity":  round(similarity, 3),
                "gewicht":     round(gewicht, 3),
                "zeit_decay":  round(zeit_decay, 3),
                "gravitation": round(gravitation, 3),
                "quelle":      "kzg",
                "inhalt":      inhalt[:100],
            })

            logger.debug(
                f"EmGrav KZG: {emotion}(a={arousal:.2f}), "
                f"sim={similarity:.3f}, grav={gravitation:.3f}, "
                f"'{inhalt[:40]}'"
            )

    return kandidaten


def _lzg_emotionale_eintraege(
    turn_embedding: list[float],
    postgres_url: str,
    user_id: str,
    character_id: str,
    jetzt: datetime,
) -> list[dict]:
    """Scannt LZG-Einträge mit Emotion und berechnet Gravitation.

    SQL-Query mit Embedding-Similarity und Emotion-Filter.

    Args:
        turn_embedding: Embedding des aktuellen Turns.
        postgres_url: PostgreSQL-URL.
        user_id: User-ID.
        character_id: Charakter-ID.
        jetzt: Aktuelle Zeit für Decay.

    Returns:
        Liste von Kandidaten-Dicts über der Schwelle.
    """
    import psycopg2

    embedding_str: str = "[" + ",".join(str(x) for x in turn_embedding) + "]"

    try:
        conn = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT inhalt, emotion, arousal, gewicht_decay, verstaerkt_am,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM lzg_knoten
            WHERE user_id = %s
              AND character_id = %s
              AND aktiv = TRUE
              AND embedding IS NOT NULL
              AND emotion != ''
              AND emotion != 'neutral'
            ORDER BY embedding <=> %s::vector
            LIMIT 10
        """, (embedding_str, user_id, character_id, embedding_str))

        rows = cursor.fetchall()
        conn.close()

    except Exception as fehler:
        logger.warning(f"EmGrav LZG-Scan fehlgeschlagen: {fehler}")
        return []

    kandidaten: list[dict] = []

    from memory.lzg import effektives_gewicht_berechnen

    for inhalt, emotion, arousal, gewicht, verstaerkt_am, similarity in rows:
        # Ebbinghaus-Decay aus lzg.py wiederverwenden
        eff_gewicht: float = effektives_gewicht_berechnen(gewicht, verstaerkt_am, jetzt)

        # Zeit-Decay für emotionale Gravitation (eigener, langsamerer Decay)
        zeit_decay: float = _zeit_decay_faktor(verstaerkt_am, jetzt)

        # Gravitation berechnen
        gravitation: float = similarity * eff_gewicht * zeit_decay * EMOTIONALE_GRAVITATION_FAKTOR_LZG

        if gravitation >= EMOTIONALE_GRAVITATIONS_SCHWELLE:
            kandidaten.append({
                "emotion":     emotion,
                "arousal":     arousal or 0.5,
                "similarity":  round(similarity, 3),
                "gewicht":     round(eff_gewicht, 3),
                "zeit_decay":  round(zeit_decay, 3),
                "gravitation": round(gravitation, 3),
                "quelle":      "lzg",
                "inhalt":      (inhalt or "")[:100],
            })

            logger.debug(
                f"EmGrav LZG: {emotion}(a={arousal:.2f}), "
                f"sim={similarity:.3f}, eff_gew={eff_gewicht:.3f}, "
                f"grav={gravitation:.3f}, '{(inhalt or '')[:40]}'"
            )

    return kandidaten


def emotionale_gravitation_auf_verlauf_anwenden(
    nova_verlauf: list[dict],
    gravitationspunkte: list[dict],
) -> list[dict]:
    """Injiziert emotionale Gravitation in Novas Emotions-Verlauf.

    Für jeden aktivierten Gravitationspunkt wird dessen Emotion
    mit einem Gewicht proportional zur Gravitationsstärke in den
    Verlauf injiziert — analoges Muster zur Empathie-Injektion
    in _nova_empathie_berechnen().

    Args:
        nova_verlauf: Novas aktueller Verlauf (nach Decay + Empathie).
        gravitationspunkte: Aktivierte emotionale Erinnerungen
                           (aus state["emotionale_gravitationspunkte"]).

    Returns:
        Modifizierter Verlauf mit injizierten Erinnerungs-Emotionen.
    """
    if not gravitationspunkte:
        return nova_verlauf

    modifiziert: list[dict] = list(nova_verlauf)

    for punkt in gravitationspunkte:
        emotion:     str   = punkt.get("emotion", "")
        arousal:     float = punkt.get("arousal", 0.5)
        gravitation: float = punkt.get("gravitation", 0.0)

        if not emotion or emotion == "neutral":
            continue

        # Gravitation als Injektions-Gewicht (skaliert: 0.3 → schwaches Echo,
        # 0.8 → starker Anklang). Gecapped auf 0.5 — Erinnerungen sollen
        # Novas Emotion färben, nicht überschreiben.
        injektions_gewicht: float = min(0.5, gravitation * 0.6)

        # Prüfen ob die Emotion schon in Novas Verlauf existiert
        gefunden: bool = False
        for eintrag in modifiziert:
            if eintrag["emotion"] == emotion:
                eintrag["gewicht"] = round(
                    min(1.0, eintrag["gewicht"] + injektions_gewicht), 2
                )
                eintrag["arousal"] = round(
                    min(1.0, max(eintrag.get("arousal", 0.0), arousal * gravitation)), 2
                )
                gefunden = True
                break

        if not gefunden:
            modifiziert.append({
                "emotion": emotion,
                "gewicht": round(injektions_gewicht, 2),
                "arousal": round(min(1.0, arousal * gravitation), 2),
            })

        logger.info(
            f"EmGrav Injektion: {emotion} (grav={gravitation:.3f}, "
            f"gewicht={injektions_gewicht:.3f}, quelle={punkt.get('quelle', '?')})"
        )

    # Neu sortieren
    modifiziert.sort(key=lambda e: e["gewicht"], reverse=True)

    return modifiziert
