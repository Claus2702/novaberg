"""Shadow Agent — Shared Utilities."""

import json
import logging
from datetime import datetime

import redis

from config import PIXIE_AKTIV

logger = logging.getLogger("ki_server.shadow")


# ─────────────────────────────────────────────
# Queue befüllen (wird vom Hauptgraph aufgerufen)
# ─────────────────────────────────────────────
def shadow_queue_push(
    redis_client: redis.Redis,
    user_id:      str,
    aufgabe:      str,
    thema:        str,
    kontext:      str = "",
    prioritaet:   float = 0.0,
    intentionen:  list = None,
    emotion:      str  = "",
    modus:        str  = "",
) -> None:
    """Legt einen Auftrag in die Shadow-Queue."""
    if not PIXIE_AKTIV:
        logger.debug("shadow_agent.utils: shadow_queue_push uebersprungen (PIXIE_AKTIV=False)")
        return

    eintrag: dict = {
        "aufgabe":     aufgabe,
        "user_id":     user_id,
        "thema":       thema,
        "kontext":     kontext,
        "prioritaet":  prioritaet,
        "intentionen": intentionen or [],
        "emotion":     emotion,
        "modus":       modus,
        "erstellt":    datetime.now().isoformat(),
    }

    redis_client.rpush(
        f"shadow_queue:{user_id}",
        json.dumps(eintrag, ensure_ascii=False),
    )

    logger.info(f"Shadow-Queue: '{aufgabe}' für '{user_id}' — {thema[:60]}")


# ─────────────────────────────────────────────
# Promotions-Queue befüllen (idempotent je KZG-Key)
# ─────────────────────────────────────────────
def promotion_queue_push(
    redis_client: redis.Redis,
    user_id:      str,
    key:          str,
    salienz:      float,
    themen:       str = "",
    dimension:    str = "",
) -> bool:
    """Reiht einen KZG-Key zur LZG-Promotion ein — nur, wenn er nicht schon liegt.

    Bis Chat 111 schrieben drei Stellen ohne jede Pruefung; derselbe Key konnte
    mehrfach in der Queue stehen. Eine Dublette kann nachweislich nichts
    beitragen: Der SynapsenPromotionAgent liest die Salienz **frisch aus dem
    Hash** statt aus dem Auftrag (agents/synapsen_promotion/agent.py:236-240),
    der erste Auftrag holt einen gestiegenen Wert also ohnehin ab.

    Vorbedingung: user_id und key sind nicht leer.
    Nachbedingung: In `queue:{user_id}` liegt genau ein lzg_promotion-Auftrag
        fuer diesen Key. Rueckgabe True, wenn dieser Aufruf ihn angelegt hat.
    Fehlerfaelle: leere Pflichtfelder — laut abgelehnt, kein Push. Ein
        unlesbarer Fremdeintrag in der Queue blockiert die Pruefung nicht,
        wird aber benannt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not key:
        logger.error(
            f"promotion_queue_push: Pflichtfeld leer — user_id='{user_id}', "
            f"key='{key}' — nicht eingereiht"
        )
        return False

    if not PIXIE_AKTIV:
        logger.debug("shadow_agent.utils: promotion_queue_push uebersprungen (PIXIE_AKTIV=False)")
        return False

    # ── Verarbeitung: liegt der Key schon? ──────
    queue_key: str = f"queue:{user_id}"

    for roh in redis_client.lrange(queue_key, 0, -1):
        try:
            vorhanden: dict = json.loads(roh)
        except (json.JSONDecodeError, TypeError) as fehler:
            # Kein stiller Uebersprung: Ein unlesbarer Eintrag gehoert
            # benannt. Er darf die Pruefung aber nicht abbrechen, sonst
            # blockiert ein fremder Datensatz jede Promotion.
            logger.warning(
                f"promotion_queue_push: unlesbarer Queue-Eintrag in {queue_key} "
                f"({type(fehler).__name__}) — bei der Dublettenpruefung uebergangen"
            )
            continue

        if vorhanden.get("aufgabe") == "lzg_promotion" and vorhanden.get("key") == key:
            logger.debug(
                f"Promotions-Queue: '{key}' liegt bereits — nicht erneut eingereiht"
            )
            return False

    redis_client.rpush(queue_key, json.dumps({
        "aufgabe":   "lzg_promotion",
        "user_id":   user_id,
        "key":       key,
        "salienz":   salienz,
        "themen":    themen,
        "dimension": dimension,
    }))

    # ── Ausgabe ─────────────────────────────────
    logger.info(f"Promotions-Queue: '{key}' eingereiht (salienz={salienz:.2f})")
    return True
