"""Speicher — Neuer KZG-Eintrag oder Verstaerkung eines bestehenden.

Schreibt direkt in Redis. Nutzt redis_client aus config.
"""

import json
import logging
import time

import numpy as np

from agents.base import AgentState
from config import (
    KZG_VERSTAERKUNG_DIVISOR,
    KZG_SALIENZ_HIGH,
    KZG_TTL_LOW_SEKUNDEN,
    KZG_TTL_HIGH_SEKUNDEN,
    redis_client,
)

logger = logging.getLogger("ki_server.agents.kzg.speicher")

KZG_PREFIX: str = "kzg:"


def speichern(state: AgentState) -> dict:
    """Speichert neuen KZG-Eintrag oder verstaerkt bestehenden."""

    salienz_obj: dict        = state["parameter"].get("salienz_obj", {})
    kern:        str         = state["parameter"].get("kern", "")
    embedding:   list[float] = state["parameter"].get("embedding", [])
    existing:    dict | None = state["parameter"].get("existing")
    user_id:     str         = state["kontext"].get("user_id", "")

    salienz: float = salienz_obj.get("salienz", 0.0)

    if existing:
        ergebnis = _verstaerken(redis_client, existing, salienz_obj, salienz)
    else:
        ergebnis = _neu_anlegen(redis_client, user_id, salienz_obj, kern, embedding, salienz)

    return {
        "parameter": {
            **state["parameter"],
            "speicher_status":  ergebnis["status"],
            "kzg_key":          ergebnis.get("key", existing["key"] if existing else ""),
            "kzg_themen_str":   ergebnis.get("themen_str", ""),
            "kzg_dimension":    ergebnis.get("dimension", ""),
            "neue_salienz":     ergebnis.get("neue_salienz", salienz),
            "neue_haeufigkeit": ergebnis.get("neue_haeufigkeit", 1),
        },
        "schritte": state["schritte"] + [
            {"node": "speichern", "ergebnis": ergebnis["status"]}
        ],
    }


def _verstaerken(
    rc,
    existing:    dict,
    salienz_obj: dict,
    salienz:     float,
) -> dict:
    """Verstaerkt einen bestehenden KZG-Eintrag."""

    neue_salienz:     float = existing["salienz"] + (salienz / KZG_VERSTAERKUNG_DIVISOR)
    neue_haeufigkeit: int   = existing["haeufigkeit"] + 1

    alter_arousal:      float = float(rc.hget(existing["key"], "arousal") or "0.5")
    neuer_arousal:      float = float(salienz_obj.get("arousal", 0.5))
    gemittelter_arousal: float = round((alter_arousal + neuer_arousal) / 2, 2)

    update_mapping: dict = {
        "salienz":     str(neue_salienz),
        "haeufigkeit": str(neue_haeufigkeit),
        "arousal":     str(gemittelter_arousal),
    }

    neuer_vektor: str = salienz_obj.get("emotions_vektor", "")
    if neuer_vektor:
        update_mapping["emotions_vektor"] = neuer_vektor

    for feld in ("sprach_stil", "beziehungs_dynamik", "tone"):
        wert: str = salienz_obj.get(feld, "")
        if wert:
            update_mapping[feld] = wert

    rc.hset(existing["key"], mapping=update_mapping)

    ttl: int = KZG_TTL_HIGH_SEKUNDEN if neue_salienz >= KZG_SALIENZ_HIGH else KZG_TTL_LOW_SEKUNDEN
    rc.expire(existing["key"], ttl)

    logger.info(
        f"KZG: Verstaerkt — salienz {existing['salienz']:.2f} -> {neue_salienz:.2f}, "
        f"haeufigkeit {neue_haeufigkeit}, TTL {ttl}s"
    )

    return {
        "status": "verstaerkt",
        "neue_salienz": neue_salienz,
        "neue_haeufigkeit": neue_haeufigkeit,
    }


def _neu_anlegen(
    rc,
    user_id:     str,
    salienz_obj: dict,
    kern:        str,
    embedding:   list[float],
    salienz:     float,
) -> dict:
    """Legt einen neuen KZG-Eintrag an."""

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()
    timestamp:       float = time.time()

    key:        str = f"{KZG_PREFIX}{user_id}:{int(timestamp * 1000)}"
    themen_str: str = ", ".join(salienz_obj.get("themen", []))
    dimension:  str = salienz_obj.get("dimension", "kontext")

    rc.hset(key, mapping={
        "user_id":            user_id,
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
        "embedding":          embedding_bytes,
    })

    ttl: int = KZG_TTL_HIGH_SEKUNDEN if salienz >= KZG_SALIENZ_HIGH else KZG_TTL_LOW_SEKUNDEN
    rc.expire(key, ttl)

    logger.info(
        f"KZG: Neuer Eintrag — salienz={salienz:.2f}, themen={themen_str}, TTL={ttl}s"
    )

    return {
        "status": "neu",
        "key": key,
        "themen_str": themen_str,
        "dimension": dimension,
    }
