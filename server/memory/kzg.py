"""
Kurzzeitgedächtnis — Redis Stack mit Vektorsuche.
TTL-basiert, Promotion ins LZG bei Schwellwert.
"""

import json
import logging
import time

from typing import Optional

import numpy as np
import redis

from config                                import ASSISTANT_USER_ID, KZG_VERSTAERKUNG_DIVISOR
from services.shadow_agent                 import shadow_queue_push

from redis.commands.search.field           import TextField, NumericField, VectorField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query           import Query

logger = logging.getLogger("ki_server.memory.kzg")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
EMBEDDING_DIM:        int   = 768
SIMILARITY_THRESHOLD: float = 0.85
PROMOTION_THRESHOLD:  float = 0.8
TTL_LOW:              int   = 604800     # 7 Tage
TTL_HIGH:             int   = 2592000    # 30 Tage
SALIENZ_LOW:          float = 0.5
SALIENZ_HIGH:         float = 0.7
KZG_INDEX_NAME:       str   = "idx:kzg"
KZG_PREFIX:           str   = "kzg:"


# ─────────────────────────────────────────────
# Intention → Shadow-Aufgabe Mapping
# ─────────────────────────────────────────────
_INTENTION_AUFGABE_MAP: dict[str, str] = {
    "emotionaler_ausdruck": "nachfragen",
    "information_teilen":   "vertiefen",
    "recherche_vertiefen":  "recherche",
    "reflexion":            "recherche",
    "gemeinsam_eruieren":   "recherche",
    "hilferuf":             "nachfragen",
    "information_erfragen": "recherche",
    "feedback_geben":       "",
    "feedback_erfragen":    "",
    "smalltalk":            "",
    "bestätigung":          "",
    "abschluss":            "",
    "anweisung":            "",
    "planung":              "",
    "humor":                "",
    "widerspruch":          "",
}


def _aufgabe_aus_intention(intentionen: list) -> str:
    """Leitet die Shadow-Aufgabe aus der primären Intention ab."""

    if not intentionen:
        return "recherche"

    aufgabe: str = _INTENTION_AUFGABE_MAP.get(intentionen[0], "recherche")

    return aufgabe if aufgabe else ""


# ─────────────────────────────────────────────
# Index-Erstellung (einmalig beim Start)
# ─────────────────────────────────────────────
def kzg_index_create(redis_client: redis.Redis) -> None:
    """Erstellt den RediSearch-Index für KZG-Einträge falls nicht vorhanden."""

    try:
        redis_client.ft(KZG_INDEX_NAME).info()
        logger.info("KZG-Index existiert bereits.")
        return
    except Exception:
        pass

    schema = (
        TagField("user_id"),
        TextField("themen"),
        TextField("inhalt"),
        NumericField("salienz"),
        NumericField("haeufigkeit"),
        TextField("gedaechtnistyp"),
        TextField("dimension"),
        NumericField("erstellt_am"),
        VectorField(
            "embedding",
            "FLAT",
            {
                "TYPE":            "FLOAT32",
                "DIM":             EMBEDDING_DIM,
                "DISTANCE_METRIC": "COSINE",
            },
        ),
    )

    definition = IndexDefinition(
        prefix=[KZG_PREFIX],
        index_type=IndexType.HASH,
    )

    redis_client.ft(KZG_INDEX_NAME).create_index(
        fields=schema,
        definition=definition,
    )

    logger.info("KZG-Index erstellt.")


# ─────────────────────────────────────────────
# Ähnlichen Eintrag suchen
# ─────────────────────────────────────────────
def kzg_similar_find(
    redis_client: redis.Redis,
    user_id:      str,
    embedding:    list[float],
    top_k:        int = 1
) -> Optional[dict]:
    """Sucht den ähnlichsten KZG-Eintrag per Vektorsuche."""

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()

    query = (
        Query(f"(@user_id:{{{user_id}}})=>[KNN {top_k} @embedding $vec AS score]")
        .sort_by("score")
        .return_fields("themen", "inhalt", "salienz", "haeufigkeit",
                       "gedaechtnistyp", "dimension", "score")
        .dialect(2)
    )

    try:
        results = redis_client.ft(KZG_INDEX_NAME).search(
            query,
            query_params={"vec": embedding_bytes},
        )

        if results.total == 0:
            return None

        treffer    = results.docs[0]
        score:      float = float(treffer.score)
        similarity: float = 1.0 - (score / 2.0)

        if similarity < SIMILARITY_THRESHOLD:
            logger.info(f"KZG: Kein ähnlicher Eintrag (beste Similarity: {similarity:.3f})")
            return None

        logger.info(f"KZG: Ähnlicher Eintrag gefunden (Similarity: {similarity:.3f})")

        return {
            "key":            treffer.id,
            "themen":         treffer.themen,
            "inhalt":         treffer.inhalt,
            "salienz":        float(treffer.salienz),
            "haeufigkeit":    int(float(treffer.haeufigkeit)),
            "gedaechtnistyp": treffer.gedaechtnistyp,
            "dimension":      treffer.dimension,
            "similarity":     similarity,
        }

    except Exception as fehler:
        logger.error(f"KZG-Suche fehlgeschlagen: {fehler}")
        return None


# ─────────────────────────────────────────────
# Eintrag speichern oder verstärken
# ─────────────────────────────────────────────
def kzg_store(
    redis_client: redis.Redis,
    user_id:      str,
    salienz_obj:  dict,
    embedding:    list[float]
) -> str:
    """
    Speichert einen neuen KZG-Eintrag oder verstärkt einen existierenden.
    Gibt den Status zurück: 'neu', 'verstaerkt' oder 'ignoriert'.
    """

    salienz: float = salienz_obj.get("salienz", 0.0)

    if salienz < SALIENZ_LOW:
        logger.info(f"KZG: Salienz {salienz:.2f} unter Schwellwert — ignoriert")
        return "ignoriert"

    # Meta-Daten aus Salienz-Analyse (Intentions-Schicht)
    intentionen: list = salienz_obj.get("intentionen", [])
    emotion:     str  = salienz_obj.get("emotion", "neutral")
    modus:       str  = salienz_obj.get("modus", "")

    existing: Optional[dict] = kzg_similar_find(redis_client, user_id, embedding)

    # Themen-Overlap prüfen wenn Treffer
    if existing:
        neue_themen:     set = set(t.strip().lower() for t in salienz_obj.get("themen", []))
        existing_themen: set = set(t.strip().lower() for t in existing["themen"].split(","))

        if not neue_themen & existing_themen:
            logger.info(
                f"KZG: Embedding ähnlich, aber Themen disjunkt — neuer Eintrag "
                f"(neu={neue_themen}, existierend={existing_themen})"
            )
            existing = None

    if existing:
        neue_salienz:     float = existing["salienz"] + (salienz / KZG_VERSTAERKUNG_DIVISOR)
        neue_haeufigkeit: int   = existing["haeufigkeit"] + 1

        # Arousal: Durchschnitt aus altem und neuem Wert
        alter_arousal: float = float(redis_client.hget(existing["key"], "arousal") or "0.5")
        neuer_arousal: float = float(salienz_obj.get("arousal", 0.5))
        gemittelter_arousal: float = round((alter_arousal + neuer_arousal) / 2, 2)

        # Vektor: neuester überschreibt
        neuer_vektor: str = salienz_obj.get("emotions_vektor", "")

        update_mapping: dict = {
            "salienz":     str(neue_salienz),
            "haeufigkeit": str(neue_haeufigkeit),
            "arousal":     str(gemittelter_arousal),
        }
        if neuer_vektor:
            update_mapping["emotions_vektor"] = neuer_vektor

        neuer_stil:   str = salienz_obj.get("sprach_stil", "")
        neue_dynamik: str = salienz_obj.get("beziehungs_dynamik", "")
        neuer_tone:   str = salienz_obj.get("tone", "")
        if neuer_stil:
            update_mapping["sprach_stil"] = neuer_stil
        if neue_dynamik:
            update_mapping["beziehungs_dynamik"] = neue_dynamik
        if neuer_tone:
            update_mapping["tone"] = neuer_tone

        redis_client.hset(existing["key"], mapping=update_mapping)

        ttl: int = TTL_HIGH if neue_salienz >= SALIENZ_HIGH else TTL_LOW
        redis_client.expire(existing["key"], ttl)

        logger.info(
            f"KZG: Verstärkt — salienz {existing['salienz']:.2f} → {neue_salienz:.2f}, "
            f"häufigkeit {neue_haeufigkeit}, TTL {ttl}s"
        )

        if neue_salienz >= PROMOTION_THRESHOLD:
            logger.info(f"KZG: Salienz {neue_salienz:.2f} ≥ {PROMOTION_THRESHOLD} — Promotion vorgemerkt")
            redis_client.rpush(
                f"queue:{user_id}",
                json.dumps({
                    "aufgabe":   "lzg_promotion",
                    "key":       existing["key"],
                    "salienz":   neue_salienz,
                    "themen":    existing["themen"],
                    "dimension": existing["dimension"],
                }),
            )

        if neue_haeufigkeit >= 3 and neue_salienz >= SALIENZ_HIGH and user_id != ASSISTANT_USER_ID:
            shadow_queue_push(
                redis_client = redis_client,
                user_id      = user_id,
                aufgabe      = "vertiefen",
                thema        = existing["themen"],
                kontext      = existing.get("inhalt", ""),
                intentionen  = intentionen,
                emotion      = emotion,
                modus        = modus,
            )

        redis_client.set(f"hash_dirty:{user_id}", "1")
        return "verstaerkt"

    else:
        embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()
        timestamp:       float = time.time()

        key:        str = f"{KZG_PREFIX}{user_id}:{int(timestamp * 1000)}"
        themen_str: str = ", ".join(salienz_obj.get("themen", []))
        dimension:  str = salienz_obj.get("dimension", "kontext")

        arousal:          float = salienz_obj.get("arousal", 0.5)
        emotions_vektor:  str   = salienz_obj.get("emotions_vektor", "")

        redis_client.hset(key, mapping={
            "user_id":          user_id,
            "themen":           themen_str,
            "inhalt":           salienz_obj.get("zusammenfassung", salienz_obj.get("begruendung", "")),
            "salienz":          str(salienz),
            "haeufigkeit":      str(1),
            "gedaechtnistyp":   salienz_obj.get("gedaechtnistyp", "kurz"),
            "dimension":        dimension,
            "intentionen":      json.dumps(intentionen),
            "emotion":          emotion,
            "modus":            modus,
            "arousal":          str(arousal),
            "emotions_vektor":    emotions_vektor,
            "sprach_stil":        salienz_obj.get("sprach_stil", "neutral"),
            "beziehungs_dynamik": salienz_obj.get("beziehungs_dynamik", "neutral"),
            "tone":               salienz_obj.get("tone", "sachlich"),
            "erstellt_am":        str(timestamp),
            "embedding":        embedding_bytes,
        })

        ttl: int = TTL_HIGH if salienz >= SALIENZ_HIGH else TTL_LOW
        redis_client.expire(key, ttl)

        if salienz >= SALIENZ_HIGH:
            redis_client.rpush(
                f"queue:{user_id}",
                json.dumps({
                    "aufgabe":   "lzg_promotion",
                    "key":       key,
                    "salienz":   salienz,
                    "themen":    themen_str,
                    "dimension": dimension,
                }),
            )

            aufgabe: str = _aufgabe_aus_intention(intentionen)

            if aufgabe and user_id != ASSISTANT_USER_ID:
                shadow_queue_push(
                    redis_client = redis_client,
                    user_id      = user_id,
                    aufgabe      = aufgabe,
                    thema        = themen_str,
                    kontext      = salienz_obj.get("zusammenfassung", ""),
                    intentionen  = intentionen,
                    emotion      = emotion,
                    modus        = modus,
                )

        logger.info(
            f"KZG: Neuer Eintrag — salienz={salienz:.2f}, themen={themen_str}, "
            f"arousal={arousal:.2f}, vektor={emotions_vektor}, TTL={ttl}s"
        )
        redis_client.set(f"hash_dirty:{user_id}", "1")

        return "neu"


# ─────────────────────────────────────────────
# Kontext abrufen für Enricher
# ─────────────────────────────────────────────
def kzg_context_retrieve(
    redis_client: redis.Redis,
    user_id:      str,
    embedding:    list[float],
    top_k:        int = 10
) -> str:
    """Holt die relevantesten KZG-Einträge als Kontext-String."""

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()

    query = (
        Query(f"(@user_id:{{{user_id}}})=>[KNN {top_k} @embedding $vec AS score]")
        .sort_by("score")
        .return_fields("themen", "inhalt", "salienz", "score")
        .dialect(2)
    )

    try:
        results = redis_client.ft(KZG_INDEX_NAME).search(
            query,
            query_params={"vec": embedding_bytes},
        )

        if results.total == 0:
            return ""

        context_parts: list[str] = []
        for doc in results.docs:
            similarity: float = 1.0 - (float(doc.score) / 2.0)
            if similarity >= 0.5:
                context_parts.append(
                    f"[KZG] {doc.themen} (Salienz: {doc.salienz}): {doc.inhalt}"
                )

        return "\n".join(context_parts)

    except Exception as fehler:
        logger.error(f"KZG-Kontextabruf fehlgeschlagen: {fehler}")
        return ""
