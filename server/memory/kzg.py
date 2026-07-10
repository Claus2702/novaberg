"""
Kurzzeitgedächtnis — Redis Stack mit Vektorsuche.
TTL-basiert, Promotion ins LZG bei Schwellwert.

Key-Schema: kzg:{user_id}:{character_id}:{entry_id}
Das Paar (user_id, character_id) definiert das gemeinsame Gespraech.
Feld `beobachter` unterscheidet, ob der Eintrag aus Sicht des Users (HumanGraph)
oder des Charakters (CharacterGraph) entstanden ist.
"""

import json
import logging
import math
import time

from typing import Optional

import numpy as np
import redis

from config                                import (
    ASSISTANT_USER_ID,
    KZG_VERSTAERKUNG_DIVISOR,
    KZG_SALIENZ_MINIMUM,
    KZG_SALIENZ_MID,
    KZG_SALIENZ_HIGH,
    KZG_SALIENZ_CAP,
    KZG_SALIENZ_DAEMPFUNG_EXP,
    KZG_TTL_LOW_SEKUNDEN,
    KZG_TTL_MID_SEKUNDEN,
    KZG_TTL_HIGH_SEKUNDEN,
    PIXIE_AKTIV,
)
from graph.context_entry                   import ContextEntry
from memory.pipeline_log                   import log_db_write
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
# DEAD CODE (Chat 91, Pre-P4-Fix): Ersetzt durch KZG_SALIENZ_HIGH (= 0.7)
# in config.py. Wird mit dem Rest der alten Promotion in P9 entfernt.
# Nicht löschen vor P9 — könnte noch in nicht-aktivem Legacy-Code
# referenziert sein.
PROMOTION_THRESHOLD: float = 0.8  # Legacy, nicht mehr verwendet
KZG_INDEX_NAME:       str   = "idx:kzg"
KZG_PREFIX:           str   = "kzg:"


# ─────────────────────────────────────────────
# Key-Helfer
# ─────────────────────────────────────────────
def _kzg_key(user_id: str, character_id: str, entry_id: str) -> str:
    """Baut den Redis-Key fuer einen KZG-Eintrag."""
    return f"kzg:{user_id}:{character_id}:{entry_id}"


def _kzg_prefix(user_id: str, character_id: str) -> str:
    """Prefix fuer alle KZG-Eintraege eines Gespraechspaares."""
    return f"kzg:{user_id}:{character_id}:*"


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
        TagField("character_id"),
        TagField("beobachter"),
        TextField("themen"),
        TextField("inhalt"),
        NumericField("salienz"),
        NumericField("haeufigkeit"),
        TextField("gedaechtnistyp"),
        TextField("dimension"),
        NumericField("erstellt_am"),
        NumericField("arousal"),
        TextField("emotions_vektor"),
        TextField("sprach_stil"),
        TextField("tone"),
        TagField("emotion"),
        TagField("modus"),
        TagField("entitaet_ids", separator=","),
        NumericField("timeline_id"),
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
    character_id: str,
    embedding:    list[float],
    top_k:        int = 1
) -> Optional[dict]:
    """Sucht den ähnlichsten KZG-Eintrag per Vektorsuche (paar-skopiert)."""

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()

    query = (
        Query(
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN {top_k} @embedding $vec AS score]"
        )
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
# Salienz-Boost-Dämpfung
# ─────────────────────────────────────────────
def _gedaempfter_boost(alte_salienz: float, raw_boost: float) -> float:
    """Berechnet den gedämpften Salienz-Boost mit sin^0.6-Kurve.

    Unten fast voller Boost, oben immer weniger, asymptotisch gegen den Cap.
    Dieselbe Kurvenfamilie wie bei der Emotions-Glättung (sin^0.5, Cap 2.5).

    Formel:
        remaining = max(0, CAP - alte_salienz)
        ratio = remaining / CAP                    (1.0 am Anfang, 0.0 am Cap)
        dämpfung = sin(ratio × π/2) ^ EXPONENT     (sin^0.6)
        effektiver_boost = raw_boost × dämpfung
    """
    remaining: float = max(0.0, KZG_SALIENZ_CAP - alte_salienz)
    if remaining <= 0:
        return 0.0

    ratio:     float = remaining / KZG_SALIENZ_CAP
    daempfung: float = math.sin(ratio * math.pi / 2) ** KZG_SALIENZ_DAEMPFUNG_EXP
    effektiv:  float = raw_boost * daempfung

    return effektiv


# ─────────────────────────────────────────────
# Eintrag speichern oder verstärken
# ─────────────────────────────────────────────
def kzg_store(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    beobachter:   str,
    salienz_obj:  dict,
    embedding:    list[float],
    entitaet_ids: list[int] | None = None,
    timeline_id:  int | None       = None,
    turn_id:      str              = "",
) -> str:
    """
    Speichert einen neuen KZG-Eintrag und verstärkt thematisch verwandte
    Einträge in der Paar-Partition (kein Merge, nur Salienz/Häufigkeit/TTL).
    Gibt den Status zurück: 'neu' oder 'ignoriert'.

    Magnet-Felder (Synapsen P3, optional):
      entitaet_ids: kommagetrennter String im RediSearch-TagField. Leere
                    Liste -> leerer String "". Default-Verhalten fuer Legacy-
                    Aufrufer (Recherche, Shadow): keine Magnete -> leerer
                    String, kein Index-Bruch.
      timeline_id:  Integer im RediSearch-NumericField. None -> Feld wird
                    aus dem mapping= ausgelassen.
      turn_id:      Pipeline-Log-Korrelation; bei Legacy-Aufrufern leer.
    """

    salienz: float = salienz_obj.get("salienz", 0.0)

    if salienz < KZG_SALIENZ_MINIMUM:
        logger.info(f"KZG: Salienz {salienz:.2f} unter Schwellwert — ignoriert")
        return "ignoriert"

    # Meta-Daten aus Salienz-Analyse (Intentions-Schicht)
    intentionen: list = salienz_obj.get("intentionen", [])
    emotion:     str  = salienz_obj.get("emotion", "neutral")
    modus:       str  = salienz_obj.get("modus", "")

    # Thematisch verwandte Einträge verstärken (kein Merge, nur Boost)
    neue_themen: set[str] = set(
        t.strip().lower() for t in salienz_obj.get("themen", []) if t.strip()
    )

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()
    timestamp:       float = time.time()

    key:        str = _kzg_key(user_id, character_id, str(int(timestamp * 1000)))
    themen_str: str = ", ".join(salienz_obj.get("themen", []))
    dimension:  str = salienz_obj.get("dimension", "kontext")

    arousal:          float = max(0.0, min(1.0, float(salienz_obj.get("arousal", 0.5))))
    emotions_vektor:  str   = salienz_obj.get("emotions_vektor", "")

    entitaet_ids_str: str = ",".join(str(eid) for eid in (entitaet_ids or []))

    mapping: dict = {
        "user_id":          user_id,
        "character_id":     character_id,
        "beobachter":       beobachter,
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
        "entitaet_ids":       entitaet_ids_str,
        "embedding":        embedding_bytes,
    }
    if timeline_id is not None:
        mapping["timeline_id"] = str(timeline_id)

    redis_client.hset(key, mapping=mapping)

    if salienz >= KZG_SALIENZ_HIGH:
        ttl: int = KZG_TTL_HIGH_SEKUNDEN
    elif salienz >= KZG_SALIENZ_MID:
        ttl: int = KZG_TTL_MID_SEKUNDEN
    else:
        ttl: int = KZG_TTL_LOW_SEKUNDEN
    redis_client.expire(key, ttl)

    # Pipeline-Log: schreibender DB-Zugriff (Synapsen §10.2).
    log_db_write(
        turn_id = turn_id or "kzg-store-unbekannt",
        node    = "kzg_speicher",
        quelle  = user_id,
        inhalt  = {
            "tabelle":      "kzg",
            "operation":    "insert",
            "kzg_key":      key,
            "entitaet_ids": entitaet_ids or [],
            "timeline_id":  timeline_id,
            "themen":       themen_str,
            "dimension":    dimension,
            "salienz":      salienz,
            "ttl":          ttl,
            "aufrufer":     "kzg_store",
        },
        user_id      = user_id,
        character_id = character_id,
    )

    if salienz >= KZG_SALIENZ_HIGH:
        if PIXIE_AKTIV:
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
        else:
            logger.debug("kzg: Promotion-Queue-Push uebersprungen (PIXIE_AKTIV=False)")

    logger.info(
        f"KZG: Neuer Eintrag — salienz={salienz:.2f}, themen={themen_str}, "
        f"arousal={arousal:.2f}, vektor={emotions_vektor}, TTL={ttl}s"
    )

    # Thematische Verstärkung: verwandte Einträge im KZG boosten
    if neue_themen:
        prefix: str = f"kzg:{user_id}:{character_id}:"
        for other_key in redis_client.keys(f"{prefix}*"):
            if isinstance(other_key, bytes):
                other_key = other_key.decode("utf-8")
            if other_key == key:
                continue
            try:
                other_themen_raw: str | None = redis_client.hget(other_key, "themen")
                if not other_themen_raw:
                    continue
                other_themen: set[str] = set(
                    t.strip().lower() for t in other_themen_raw.split(",") if t.strip()
                )
                if not neue_themen & other_themen:
                    continue

                alte_sal: float = float(redis_client.hget(other_key, "salienz") or "0.0")
                alte_hfk: int   = int(float(redis_client.hget(other_key, "haeufigkeit") or "1"))
                raw_boost: float = salienz / KZG_VERSTAERKUNG_DIVISOR
                boost:     float = _gedaempfter_boost(alte_sal, raw_boost)
                neue_sal:  float = alte_sal + boost
                neue_hfk: int   = alte_hfk + 1

                redis_client.hset(other_key, mapping={
                    "salienz":     str(neue_sal),
                    "haeufigkeit": str(neue_hfk),
                })

                if neue_sal >= KZG_SALIENZ_HIGH:
                    neuer_ttl: int = KZG_TTL_HIGH_SEKUNDEN
                elif neue_sal >= KZG_SALIENZ_MID:
                    neuer_ttl: int = KZG_TTL_MID_SEKUNDEN
                else:
                    neuer_ttl: int = KZG_TTL_LOW_SEKUNDEN

                verbleibend: int = redis_client.ttl(other_key)
                redis_client.expire(other_key, max(verbleibend if verbleibend > 0 else 0, neuer_ttl))

                logger.info(
                    f"KZG: Thematische Verstärkung {other_key} — "
                    f"salienz {alte_sal:.2f} → {neue_sal:.2f}, "
                    f"häufigkeit {alte_hfk} → {neue_hfk}"
                )
            except Exception as ex:
                logger.warning(f"KZG: Verstärkungsfehler bei {other_key}: {ex}")

    if PIXIE_AKTIV:
        redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")
    else:
        logger.debug("kzg: hash_dirty-Setzer uebersprungen (PIXIE_AKTIV=False)")
    return "neu"


# ─────────────────────────────────────────────
# Kontext abrufen für Enricher
# ─────────────────────────────────────────────
def kzg_entries_retrieve(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    embedding:    list[float],
    top_k:        int = 10
) -> list[ContextEntry]:
    """Holt die relevantesten KZG-Eintraege eines Paares als ContextEntry-Liste.

    Liefert strukturierte Daten ohne Format-Drumherum. Der Reducer
    dedupliziert auf dieser Ebene; der Formatter baut daraus den
    finalen memory_context-String fuer den Responder.

    Datenbeschaffung: KNN-Suche im RediSearch-Index (paar-skopiert auf
    user_id/character_id), Similarity-Schwelle 0.5, top_k Treffer.
    Filter, Schwellwerte und Index bleiben identisch zur Vorgaengerfunktion.

    Mapping pro KZG-Hash-Treffer auf ContextEntry:
      quelle  = "kzg" (Konstante)
      subtyp  = Hash-Feld `dimension` (Salienz-Dim 5: interessen,
                beziehungen, ...). Leer-String wenn nicht gesetzt.
      inhalt  = Hash-Feld `inhalt` (destillierter Kern)
      gewicht = Hash-Feld `salienz` als float
      meta    = {
          "themen":         Hash-Feld `themen` (String wie gespeichert),
          "beobachter":     Hash-Feld `beobachter`,
          "erstellt_am":    Hash-Feld `erstellt_am` (Unix-Timestamp, float),
          "arousal":        Hash-Feld `arousal` (float, fuer spaetere
                            Format-Erweiterungen),
          "emotion":        Hash-Feld `emotion`,
          "modus":          Hash-Feld `modus`,
          "gedaechtnistyp": Hash-Feld `gedaechtnistyp`,
          "emotions_vektor": Hash-Feld `emotions_vektor`,
      }

    Args:
        redis_client: Redis-Verbindung mit RediSearch-Modul.
        user_id:      Subjekt der Paar-Partition.
        character_id: Gegenueber der Paar-Partition.
        embedding:    Query-Vektor (768-dim) des aktuellen Prompts.
        top_k:        Maximale Treffer-Anzahl vor Similarity-Filter.

    Returns:
        Liste von ContextEntry-Dicts. Leer bei keinen Treffern oder Fehler.
    """

    logger.info(f"KZG-Entries-Retrieve: Paar={user_id}:{character_id}, Limit={top_k}")

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()

    query = (
        Query(
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN {top_k} @embedding $vec AS score]"
        )
        .sort_by("score")
        .return_fields(
            "themen", "inhalt", "salienz", "score",
            "dimension", "beobachter", "erstellt_am",
            "arousal", "emotion", "modus", "gedaechtnistyp",
            "emotions_vektor",
        )
        .dialect(2)
    )

    entries: list[ContextEntry] = []

    try:
        results = redis_client.ft(KZG_INDEX_NAME).search(
            query,
            query_params={"vec": embedding_bytes},
        )

        if results.total == 0:
            logger.info("KZG-Entries-Retrieve: 0 Eintraege geliefert")
            return entries

        for doc in results.docs:
            similarity: float = 1.0 - (float(doc.score) / 2.0)
            if similarity < 0.5:
                continue

            subtyp:  str   = getattr(doc, "dimension", "") or ""
            inhalt:  str   = getattr(doc, "inhalt", "") or ""
            gewicht: float = float(getattr(doc, "salienz", 0.0) or 0.0)

            erstellt_am_raw = getattr(doc, "erstellt_am", "") or ""
            try:
                erstellt_am: float = float(erstellt_am_raw) if erstellt_am_raw else 0.0
            except (TypeError, ValueError):
                erstellt_am = 0.0

            try:
                arousal: float = float(getattr(doc, "arousal", 0.0) or 0.0)
            except (TypeError, ValueError):
                arousal = 0.0

            entry: ContextEntry = {
                "quelle":  "kzg",
                "subtyp":  subtyp,
                "inhalt":  inhalt,
                "gewicht": gewicht,
                "meta": {
                    "themen":          getattr(doc, "themen", "") or "",
                    "beobachter":      getattr(doc, "beobachter", "") or "",
                    "erstellt_am":     erstellt_am,
                    "arousal":         arousal,
                    "emotion":         getattr(doc, "emotion", "") or "",
                    "modus":           getattr(doc, "modus", "") or "",
                    "gedaechtnistyp":  getattr(doc, "gedaechtnistyp", "") or "",
                    "emotions_vektor": getattr(doc, "emotions_vektor", "") or "",
                },
            }
            entries.append(entry)

            logger.debug(
                f"KZG-Entry: subtyp={subtyp}, gewicht={gewicht:.2f}, "
                f"inhalt-snippet={inhalt[:60]}"
            )

        logger.info(f"KZG-Entries-Retrieve: {len(entries)} Eintraege geliefert")
        return entries

    except Exception as fehler:
        logger.error(f"KZG-Entries-Retrieve fehlgeschlagen: {fehler}")
        return []
