"""Speicher — Neuer KZG-Eintrag + thematische Verstaerkung verwandter Eintraege.

Schreibt direkt in Redis. Nutzt redis_client aus config.
"""

import json
import logging
import math
import time

import numpy as np

from agents.base import AgentState
from config import (
    KZG_VERSTAERKUNG_DIVISOR,
    KZG_SALIENZ_HIGH,
    KZG_SALIENZ_MID,
    KZG_SALIENZ_CAP,
    KZG_SALIENZ_DAEMPFUNG_EXP,
    KZG_TTL_LOW_SEKUNDEN,
    KZG_TTL_MID_SEKUNDEN,
    KZG_TTL_HIGH_SEKUNDEN,
    redis_client,
)
from memory.kzg import _kzg_key
from memory.embedding import embedding_create
from memory.pipeline_log import log_db_zugriff

logger = logging.getLogger("ki_server.agents.kzg.speicher")


def speichern(state: AgentState) -> dict:
    """Speichert neuen KZG-Eintrag und verstärkt thematisch verwandte Einträge.

    Jeder Eintrag wird als eigenständiger Eintrag mit seinem scharfen Kern
    abgelegt. Danach werden alle Einträge mit thematischem Overlap verstärkt
    (Salienz-Boost + TTL-Auffrischung + Häufigkeitszähler).

    Die Verstärkung berührt nur Metadaten, nie den Inhalt. Jeder Kern bleibt
    exakt wie er beim Verdichten erzeugt wurde.
    """
    salienz_obj:  dict = state["parameter"].get("salienz_obj", {})
    kern:         str  = state["parameter"].get("kern", "")
    user_id:      str  = state["kontext"].get("user_id", "")
    character_id: str  = state["kontext"].get("character_id", "")
    beobachter:   str  = state["kontext"].get("beobachter", "user")
    turn_id:      str  = state["kontext"].get("turn_id", "")

    # Magnete aus dem magnete_aufloesen-Node (Synapsen P3).
    entitaet_ids: list[int]  = state["parameter"].get("entitaet_ids", []) or []
    timeline_id:  int | None = state["parameter"].get("timeline_id")

    salienz: float = salienz_obj.get("salienz", 0.0)

    valenz:     str = salienz_obj.get("emotionen", {}).get("valenz", "neutral")
    themen:     str = " ".join(salienz_obj.get("themen", []))
    embed_text: str = f"Thema: {themen}. Valenz: {valenz}. Aussage: {kern}"

    embed_client = state["kontext"].get("embed_client")
    embed_model:  str = state["kontext"].get("embed_model", "")

    embedding: list[float] = embedding_create(embed_text, embed_client, embed_model)

    ergebnis: dict = _neu_anlegen(
        redis_client, user_id, character_id, beobachter,
        salienz_obj, kern, embedding, salienz,
        entitaet_ids = entitaet_ids,
        timeline_id  = timeline_id,
        turn_id      = turn_id,
    )

    neue_themen: set[str] = set(
        t.strip().lower() for t in salienz_obj.get("themen", []) if t.strip()
    )
    verstaerkt_count: int = 0

    if neue_themen:
        verstaerkt_count = _thematisch_verstaerken(
            user_id, character_id, ergebnis.get("key", ""),
            neue_themen, salienz,
        )

    return {
        "parameter": {
            **state["parameter"],
            "embedding":           embedding,
            "speicher_status":     ergebnis["status"],
            "kzg_key":             ergebnis.get("key", ""),
            "kzg_themen_str":      ergebnis.get("themen_str", ""),
            "kzg_dimension":       ergebnis.get("dimension", ""),
            "neue_salienz":        salienz,
            "neue_haeufigkeit":    1,
            "verstaerkt_verwandt": verstaerkt_count,
        },
        "schritte": state["schritte"] + [
            {"node": "speichern", "ergebnis": ergebnis["status"],
             "verstaerkt_verwandt": verstaerkt_count}
        ],
    }


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


def _thematisch_verstaerken(
    user_id:       str,
    character_id:  str,
    eigener_key:   str,
    neue_themen:   set[str],
    salienz:       float,
) -> int:
    """Verstärkt thematisch verwandte KZG-Einträge in der Paar-Partition.

    Verstärkungsschema (KZG):
    - salienz += eingehende_salienz / KZG_VERSTAERKUNG_DIVISOR
    - haeufigkeit += 1
    - TTL auf den höheren Wert aus (verbleibend, neu berechnet aus neuer Salienz)

    Nicht angerührt: inhalt, embedding, emotion, modus, arousal.
    Der scharfe Kern jedes Eintrags bleibt exakt erhalten.

    Returns:
        Anzahl verstärkter Einträge.
    """
    prefix: str = f"kzg:{user_id}:{character_id}:"
    keys: list = redis_client.keys(f"{prefix}*")
    verstaerkt: int = 0

    for key in keys:
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        if key == eigener_key:
            continue

        try:
            existing_themen_raw: str | None = redis_client.hget(key, "themen")
            if not existing_themen_raw:
                continue

            existing_themen: set[str] = set(
                t.strip().lower() for t in existing_themen_raw.split(",") if t.strip()
            )

            overlap: set[str] = neue_themen & existing_themen
            if not overlap:
                continue

            alte_salienz:     float = float(redis_client.hget(key, "salienz") or "0.0")
            alte_haeufigkeit: int   = int(float(redis_client.hget(key, "haeufigkeit") or "1"))

            raw_boost:        float = salienz / KZG_VERSTAERKUNG_DIVISOR
            boost:            float = _gedaempfter_boost(alte_salienz, raw_boost)
            neue_salienz:     float = alte_salienz + boost
            neue_haeufigkeit: int   = alte_haeufigkeit + 1

            redis_client.hset(key, mapping={
                "salienz":     str(neue_salienz),
                "haeufigkeit": str(neue_haeufigkeit),
            })

            if neue_salienz >= KZG_SALIENZ_HIGH:
                neuer_ttl: int = KZG_TTL_HIGH_SEKUNDEN
            elif neue_salienz >= KZG_SALIENZ_MID:
                neuer_ttl: int = KZG_TTL_MID_SEKUNDEN
            else:
                neuer_ttl: int = KZG_TTL_LOW_SEKUNDEN

            verbleibend: int = redis_client.ttl(key)
            if verbleibend < 0:
                verbleibend = 0
            effektiver_ttl: int = max(verbleibend, neuer_ttl)
            redis_client.expire(key, effektiver_ttl)

            verstaerkt += 1

            logger.info(
                f"KZG Verstärkung: {key} — "
                f"salienz {alte_salienz:.2f} → {neue_salienz:.2f} (+{boost:.2f}), "
                f"häufigkeit {alte_haeufigkeit} → {neue_haeufigkeit}, "
                f"TTL {effektiver_ttl}s, "
                f"overlap={overlap}"
            )

        except Exception as ex:
            logger.warning(f"KZG Verstärkung: Fehler bei {key}: {ex}")

    if verstaerkt > 0:
        logger.info(
            f"KZG Verstärkung: {verstaerkt} verwandte Einträge verstärkt "
            f"für {user_id}:{character_id}"
        )

    return verstaerkt


def _neu_anlegen(
    rc,
    user_id:      str,
    character_id: str,
    beobachter:   str,
    salienz_obj:  dict,
    kern:         str,
    embedding:    list[float],
    salienz:      float,
    entitaet_ids: list[int] | None = None,
    timeline_id:  int | None       = None,
    turn_id:      str              = "",
) -> dict:
    """Legt einen neuen KZG-Eintrag an.

    Magnet-Felder (Synapsen P3):
      entitaet_ids: kommagetrennter String im RediSearch-TagField. Leere
                    Liste -> leerer String "" (RediSearch tolerant).
      timeline_id:  Integer im RediSearch-NumericField. None -> Feld wird
                    aus dem mapping= ausgelassen, damit der Index-Update
                    nicht bricht.

    Pipeline-Log: nach erfolgreichem hset wird ein log_db_zugriff-Eintrag
    erzeugt (EVA-konform: Forensik nach Verarbeitung).
    """

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()
    timestamp:       float = time.time()

    key:        str = _kzg_key(user_id, character_id, str(int(timestamp * 1000)))
    themen_str: str = ", ".join(salienz_obj.get("themen", []))
    dimension:  str = salienz_obj.get("dimension", "kontext")

    entitaet_ids_str: str = ",".join(str(eid) for eid in (entitaet_ids or []))

    mapping: dict = {
        "user_id":            user_id,
        "character_id":       character_id,
        "beobachter":         beobachter,
        "themen":             themen_str,
        "inhalt":             kern,
        "salienz":            str(salienz),
        "haeufigkeit":        str(1),
        "gedaechtnistyp":     salienz_obj.get("gedaechtnistyp", "kurz"),
        "dimension":          dimension,
        "intentionen":        json.dumps(salienz_obj.get("intentionen", [])),
        "emotion":            salienz_obj.get("emotion", "neutral"),
        "modus":              salienz_obj.get("modus", ""),
        "arousal":            str(salienz_obj.get("arousal", 0.5)),
        "emotions_vektor":    salienz_obj.get("emotions_vektor", ""),
        "sprach_stil":        salienz_obj.get("sprach_stil", "neutral"),
        "beziehungs_dynamik": salienz_obj.get("beziehungs_dynamik", "neutral"),
        "tone":               salienz_obj.get("tone", "sachlich"),
        "erstellt_am":        str(timestamp),
        "entitaet_ids":       entitaet_ids_str,
        "embedding":          embedding_bytes,
    }
    if timeline_id is not None:
        mapping["timeline_id"] = str(timeline_id)

    rc.hset(key, mapping=mapping)

    if salienz >= KZG_SALIENZ_HIGH:
        ttl: int = KZG_TTL_HIGH_SEKUNDEN
    elif salienz >= KZG_SALIENZ_MID:
        ttl: int = KZG_TTL_MID_SEKUNDEN
    else:
        ttl: int = KZG_TTL_LOW_SEKUNDEN
    rc.expire(key, ttl)

    logger.info(
        f"KZG: Neuer Eintrag — salienz={salienz:.2f}, themen={themen_str}, "
        f"entitaet_ids={entitaet_ids or []}, timeline_id={timeline_id}, TTL={ttl}s"
    )

    # Pipeline-Log: schreibender DB-Zugriff (Synapsen §10.2).
    log_db_zugriff(
        turn_id = turn_id or "kzg-unbekannt",
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
        },
    )

    return {
        "status": "neu",
        "key": key,
        "themen_str": themen_str,
        "dimension": dimension,
    }
