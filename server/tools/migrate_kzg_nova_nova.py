#!/usr/bin/env python3
"""Einmalige Migration: kzg:nova:nova:* → kzg:nova:meister:*.

Novas Selbst-Erkenntnisse lagen vor Chat 71 unter dem falschen
Gegenueber-Key (nova statt meister). Dieses Skript verschiebt sie
und setzt beobachter=assistant.

Aufruf:
    python3 -m tools.migrate_kzg_nova_nova          (Dry-Run)
    python3 -m tools.migrate_kzg_nova_nova --commit  (Ausfuehren)
"""

import logging
import sys

from config import redis_client

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("migrate_kzg_nova_nova")

QUELL_PATTERN: str = "kzg:nova:nova:*"
ZIEL_PREFIX:   str = "kzg:nova:meister:"


def migrieren(commit: bool = False) -> None:
    """Migriert alle Keys von kzg:nova:nova:* nach kzg:nova:meister:*."""
    keys: list[str] = []
    for key in redis_client.scan_iter(match=QUELL_PATTERN, count=100):
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        keys.append(key)

    logger.info(f"Gefunden: {len(keys)} Keys unter {QUELL_PATTERN}")

    if not keys:
        logger.info("Nichts zu migrieren.")
        return

    migriert: int = 0
    fehler:   int = 0

    for alter_key in keys:
        # ID aus dem alten Key extrahieren: kzg:nova:nova:1777409300971 → 1777409300971
        teile: list[str] = alter_key.split(":")
        if len(teile) != 4:
            logger.warning(f"  Unerwartetes Key-Format: {alter_key} — uebersprungen")
            fehler += 1
            continue

        entry_id:  str = teile[3]
        neuer_key: str = f"{ZIEL_PREFIX}{entry_id}"

        # Pruefen ob Ziel-Key bereits existiert
        if redis_client.exists(neuer_key):
            logger.warning(f"  Ziel existiert bereits: {neuer_key} — uebersprungen")
            fehler += 1
            continue

        # TTL auslesen (Sekunden, -1 = kein Ablauf, -2 = existiert nicht)
        ttl: int = redis_client.ttl(alter_key)

        # Raw-Bytes: redis_client hat decode_responses=False,
        # aber hgetall kann bei einigen Redis-Versionen intern decodieren.
        # Sicher: DUMP/RESTORE statt feldweise Kopie.
        try:
            dump_data: bytes = redis_client.dump(alter_key)
        except Exception as ex:
            logger.warning(f"  DUMP fehlgeschlagen: {alter_key} — {ex}")
            fehler += 1
            continue

        if not dump_data:
            logger.warning(f"  Leerer DUMP: {alter_key} — uebersprungen")
            fehler += 1
            continue

        # Inhalt-Preview im Dry-Run (sicheres Decoding)
        try:
            inhalt_raw = redis_client.hget(alter_key, "inhalt")
            inhalt: str = inhalt_raw.decode("utf-8", errors="replace")[:60] if inhalt_raw else ""
        except Exception:
            inhalt = "(nicht lesbar)"

        if commit:
            # RESTORE kopiert den kompletten Hash inkl. binaerer Felder
            redis_client.restore(neuer_key, ttl * 1000 if ttl > 0 else 0, dump_data)

            # beobachter nachtraeglich setzen (ueberschreibt vorhandenes Feld)
            redis_client.hset(neuer_key, "beobachter", "assistant")

            # Alten Key loeschen
            redis_client.delete(alter_key)

            logger.info(f"  ✅ {alter_key} → {neuer_key} (TTL={ttl}s)")
        else:
            logger.info(f"  🔍 {alter_key} → {neuer_key} (TTL={ttl}s)")

        migriert += 1

    logger.info(f"\n{'COMMIT' if commit else 'DRY-RUN'}: {migriert} migriert, {fehler} uebersprungen")

    if commit and migriert > 0:
        # hash_dirty setzen damit CharakterAgent die neuen Daten einliest
        redis_client.set("hash_dirty:nova:meister", "1")
        logger.info("hash_dirty:nova:meister gesetzt")


if __name__ == "__main__":
    ist_commit: bool = "--commit" in sys.argv
    if not ist_commit:
        logger.info("=== DRY-RUN (ohne --commit) ===\n")
    else:
        logger.info("=== COMMIT-MODUS ===\n")
    migrieren(commit=ist_commit)
