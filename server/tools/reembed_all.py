"""Re-Embedding aller Vektor-Speicher nach dem Modellwechsel (A5, Chat 107).

Anlass: EMBEDDING-CASING-BLIND — saemtliche Bestandsvektoren stammen aus dem
casing-blinden nomic-embed-text v1 und sind semantisch wertlos. Dieses
Werkzeug erzeugt sie mit dem konfigurierten Modell (config.EMBED_MODEL,
seit A4: nomic-embed-text-v2-moe) neu.

Grundsaetze:
  - EINE Formel pro Speicherziel: das Tool ruft die embed_text_bauen()-
    Funktionen der Module auf (Commit 5d58b66) — es baut KEINEN eigenen Text.
  - Direkter Ollama-Client wie migrate_lzg_synapsen.py (K9-konform): ein
    Standalone-Skript hat keinen Server-Loop, der EmbedWorker laeuft nicht.
  - Dry-Run ist Default und schreibt NICHTS. --commit schreibt. Idempotent.

Drei Sicherheitsnetze (Pflicht, nicht abschaltbar):
  1. Casing-Eingangspruefung vor jedem Lauf (auch Dry-Run): liefert
     embed("Hund") == embed("Katze") bit-identisch, bricht das Tool ab —
     ein Re-Embedding gegen ein casing-blindes Modell schriebe den Schaden
     nur neu, und diesmal saehen die Vektoren "frisch" aus.
  2. Dimensionspruefung bei JEDEM erzeugten Vektor (len == 768, sonst Abbruch).
  3. Modell-Protokoll: config.EMBED_MODEL als erste und letzte Log-Zeile.

Selbstkontrolle nach --commit (Ziel lzg_knoten): drei Referenzpaare aus der
Chat-107-Kalibrierung werden direkt in der DB nachgerechnet
(1 - (a.embedding <=> b.embedding)); Abweichung > 0.01 wird laut gemeldet.

Ziele (--target, mehrfach; "all" = alle ausser legacy, reset, kanten_rebuild):
  lzg_knoten entitaeten fakten ziele delegation kzg shadow kanten
  reset kanten_rebuild legacy
  - Reihenfolge in "all": lzg_knoten -> ... -> kzg -> shadow -> kanten.
    kanten IMMER zuletzt (rechnet Cosines aus den frischen Knoten-Vektoren).
  - shadow wird GELOESCHT, nicht re-embedded (kurzlebig, kein Verlust).
  - reset (NICHT in "all" — bewusste Entscheidung, kein Automatismus):
    setzt alle Knoten-Gewichte auf den rekonstruierten Anlagezustand
    zurueck und loescht die Kanten. Anlass: 2910 Reinforcements (93 %)
    aus Skelett-Kollisionen — Zufallsgewichte, die ueber gewicht_absolut
    die Charakter-Destillation speisen.
  - kanten_rebuild (NICHT in "all"): baut das Kantennetz chronologisch
    neu auf. Zwingend NACH Re-Embedding UND Reset — kanten_staerke_
    berechnen liest gewicht_absolut, ein frueherer Aufbau wuerde die
    Zufallsgewichte in die Kanten einfrieren.
    Phase-B-Kette: lzg_knoten -> reset -> kanten_rebuild
    (kanten/Cosine-Refresh bleibt fuer Refresh-OHNE-Reset erhalten).
  - legacy (langzeitgedaechtnis) nur explizit — hat keinen Live-Aufrufer
    und KEINE embed_text_bauen-Formel; der Handler verweigert laut, statt
    eine Formel im Tool zu improvisieren (Entscheidung noetig).
  - Auch inaktive Zeilen werden re-embedded (reactivate_node kann sie
    wiederbeleben); leere Quelltexte werden uebersprungen UND gezaehlt.

Aufruf (im Server-Container bzw. mit POSTGRES_URL/REDIS_URL auf localhost):
    python -m tools.reembed_all                          # Dry-Run, all
    python -m tools.reembed_all --target kzg --target shadow
    python -m tools.reembed_all --commit                 # schreibt

Nach dem Commit-Lauf (Phase B): Container NEU ERZEUGEN (docker compose
up -d) — ein blosser Restart liest die Compose-Env nicht neu ein. Der
Neustart loest zugleich den _strategie_embeddings_cache (ei/dreischicht).
"""

import argparse
import logging
import sys

import numpy as np
import psycopg2
import psycopg2.extras
import redis as redis_lib

from config import POSTGRES_URL, REDIS_URL, ollama_gpu_client, EMBED_MODEL
from memory import lzg_knoten, lzg_kanten
from memory.utils import embedding_zu_pgvector_str
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.repositories.fakten_repository import FaktenRepository
from memory.ziele import embed_text_bauen as ziel_embed_text_bauen
from agents.delegation.akte import embed_text_bauen as delegation_embed_text_bauen
from agents.kzg.speicher import embed_text_bauen as kzg_embed_text_bauen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("reembed_all")

EXPECTED_DIM: int = 768
PROGRESS_INTERVALL: int = 25

# Referenzpaare der Selbstkontrolle: (knoten_a, knoten_b, erwartete Cosine).
# Werte aus der Chat-107-Kalibrierungsmessung mit v2-moe an genau diesen Knoten.
KONTROLL_PAARE: list[tuple[int, int, float]] = [
    (102, 103, 0.9135),   # "Lumi stirbt bald" / "... nicht mehr lange leben"
    (47, 83, 0.7876),     # zwei VERSCHIEDENE Zahnarzttermine
    (150, 151, 0.9254),   # Paraphrase (lobt/mag die Tiefe, die Worte, ...)
]
KONTROLL_TOLERANZ: float = 0.01

ZIEL_REIHENFOLGE: list[str] = [
    "lzg_knoten", "entitaeten", "fakten", "ziele",
    "delegation", "kzg", "legacy", "shadow",
    "reset", "kanten", "kanten_rebuild",
]
# reset und kanten_rebuild laufen NICHT in "all" mit — der Gewichts-Reset ist
# eine bewusste Entscheidung, kein Automatismus; der Rebuild gehoert zwingend
# HINTER den Reset (kanten_staerke_berechnen liest gewicht_absolut — ein
# Rebuild vor dem Reset wuerde die Zufallsgewichte in die Kanten einfrieren).
ALL_ZIELE: list[str] = [z for z in ZIEL_REIHENFOLGE if z not in ("legacy", "reset", "kanten_rebuild")]

# Beispielknoten fuer die Reset-Vorschau: die drei bekannten Kollisions-Opfer
# (108: 179x "exquisit und blumig", 121: 121x OXTR-Frage, 167: 61x "Der Nutzer
# heisst Claus").
RESET_BEISPIEL_IDS: list[int] = [108, 121, 167]

# Redis ohne Auto-Decode: HGET auf Embedding-Bytes wuerde sonst
# UnicodeDecodeError werfen (Muster aus migrate_kzg_keys.py).
raw_redis: redis_lib.Redis = redis_lib.from_url(REDIS_URL, decode_responses=False)


# ─────────────────────────────────────────────
# Embedding (direkter Ollama-GPU-Client, ohne Worker) + Sicherheitsnetze
# ─────────────────────────────────────────────

def embedding_berechnen(text: str) -> list[float]:
    """Berechnet ein Embedding ueber den direkten Ollama-Client.

    Selber Endpunkt (OLLAMA_GPU_URL) und selbes Modell (config.EMBED_MODEL)
    wie der EmbedWorker im Live-Betrieb — identische Vektoren, kein Versatz.
    Vorbedingung: text nicht-leer (stellen die embed_text_bauen()-Bauer
    sicher). Nachbedingung: Vektor mit exakt EXPECTED_DIM Komponenten.
    Fehlerfaelle: leere Ollama-Antwort oder falsche Dimension -> RuntimeError
    (Abbruch des Laufs — Sicherheitsnetz 2, im Repo existiert sonst kein
    einziger Dimensions-Check).
    """
    # ── Verarbeitung ────────────────────────────
    antwort = ollama_gpu_client.embed(model=EMBED_MODEL, input=text)
    embeddings = antwort.get("embeddings")

    # ── Ausgabe-Verifikation ────────────────────
    if not embeddings:
        raise RuntimeError(f"Ollama lieferte kein Embedding (Modell={EMBED_MODEL})")
    embedding: list[float] = list(embeddings[0])
    if len(embedding) != EXPECTED_DIM:
        raise RuntimeError(
            f"Dimensionspruefung fehlgeschlagen: {len(embedding)} statt {EXPECTED_DIM} "
            f"Komponenten (Modell={EMBED_MODEL}) — Abbruch, bevor ein falsch "
            f"dimensionierter Vektor geschrieben wird"
        )
    return embedding


def casing_pruefung() -> None:
    """Sicherheitsnetz 1 — Casing-Eingangspruefung, nicht abschaltbar.

    Embeddet "Hund" und "Katze" ueber den regulaeren Pfad. Sind die
    Vektoren bit-identisch, ist das konfigurierte Modell casing-blind
    (der EMBEDDING-CASING-BLIND-Defekt) und der Lauf bricht sofort ab.
    Laeuft vor jedem Lauf, auch im Dry-Run.
    """
    # ── Verarbeitung ────────────────────────────
    hund: list[float] = embedding_berechnen("Hund")
    katze: list[float] = embedding_berechnen("Katze")

    # ── Ausgabe-Verifikation ────────────────────
    if hund == katze:
        logger.critical(
            "CASING-PRUEFUNG FEHLGESCHLAGEN: embed('Hund') und embed('Katze') sind "
            "bit-identisch — das Modell '%s' ist casing-blind. Ein Re-Embedding "
            "wuerde den Schaden nur neu schreiben. ABBRUCH.",
            EMBED_MODEL,
        )
        raise SystemExit(1)
    logger.info("Casing-Pruefung bestanden: embed('Hund') != embed('Katze') (Modell=%s)", EMBED_MODEL)


# ─────────────────────────────────────────────
# Generischer Postgres-Lauf
# ─────────────────────────────────────────────

def _rows_laden(select_sql: str) -> list[dict]:
    """Laedt alle Zeilen eines Ziel-SELECTs als Dict-Liste (RealDictCursor)."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(select_sql)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def _pg_ziel_verarbeiten(
    ziel: str,
    rows: list[dict],
    text_bauen,
    schreiben,
    commit: bool,
) -> dict:
    """Gemeinsamer Ablauf aller Postgres-Ziele.

    text_bauen(row) -> str | None  (None = Quelltext leer -> ueberspringen)
    schreiben(row_id, embedding)   -> bool (nur bei --commit aufgerufen)
    Liefert die Statistik {gelesen, embedded, geschrieben, uebersprungen}.
    """
    # ── Eingabe-Validierung ─────────────────────
    stats: dict = {"gelesen": len(rows), "embedded": 0, "geschrieben": 0, "uebersprungen": 0}
    logger.info("[%s] %d Zeilen gelesen", ziel, len(rows))

    # ── Verarbeitung ────────────────────────────
    beispiele: int = 0
    for i, row in enumerate(rows, start=1):
        text = text_bauen(row)
        if text is None:
            stats["uebersprungen"] += 1
            logger.error("[%s] id=%s: Quelltext leer — uebersprungen (Vektor bleibt alt!)", ziel, row["id"])
            continue

        if not commit:
            if beispiele < 3:
                logger.info("[%s] Beispiel id=%s: '%.70s...'", ziel, row["id"], text)
                beispiele += 1
            continue

        embedding: list[float] = embedding_berechnen(text)
        stats["embedded"] += 1
        if schreiben(row["id"], embedding):
            stats["geschrieben"] += 1
        else:
            raise RuntimeError(f"[{ziel}] Schreiben fuer id={row['id']} fehlgeschlagen — Abbruch")

        if i % PROGRESS_INTERVALL == 0:
            logger.info("[%s] Fortschritt: %d/%d", ziel, i, len(rows))

    # ── Ausgabe ─────────────────────────────────
    return stats


def _pg_update(sql: str, embedding: list[float], row_id: int) -> bool:
    """Parameterisiertes Embedding-UPDATE mit rowcount-Verifikation."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (embedding_zu_pgvector_str(embedding), row_id))
            rowcount: int = cur.rowcount
        conn.commit()
        if rowcount != 1:
            logger.error("UPDATE traf %d Zeilen fuer id=%s (erwartet 1)", rowcount, row_id)
        return rowcount == 1
    except psycopg2.Error as exc:
        conn.rollback()
        logger.exception("%s: UPDATE fehlgeschlagen id=%s", type(exc).__name__, row_id)
        return False
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Ziel-Handler
# ─────────────────────────────────────────────

def ziel_lzg_knoten(commit: bool) -> dict:
    """lzg_knoten.embedding — Formel: memory/lzg_knoten.py::embed_text_bauen."""
    rows = _rows_laden("SELECT id, inhalt FROM lzg_knoten ORDER BY id")
    return _pg_ziel_verarbeiten(
        "lzg_knoten", rows,
        lambda r: lzg_knoten.embed_text_bauen(r["inhalt"]) if (r["inhalt"] or "").strip() else None,
        lambda rid, emb: lzg_knoten.knoten_embedding_aktualisieren(
            POSTGRES_URL, rid, embedding_zu_pgvector_str(emb)
        ),
        commit,
    )


def ziel_entitaeten(commit: bool) -> dict:
    """entitaeten.embedding — Formel: EntitaetenRepository.embed_text_bauen."""
    rows = _rows_laden("SELECT id, name, zusammenfassung FROM entitaeten ORDER BY id")

    def schreiben(rid: int, emb: list[float]) -> bool:
        EntitaetenRepository.update_embedding(POSTGRES_URL, rid, emb)
        return True

    return _pg_ziel_verarbeiten(
        "entitaeten", rows,
        lambda r: EntitaetenRepository.embed_text_bauen(r["name"], r["zusammenfassung"])
        if (r["name"] or "").strip() else None,
        schreiben,
        commit,
    )


def ziel_fakten(commit: bool) -> dict:
    """fakten.embedding — Formel: FaktenRepository.embed_text_bauen."""
    rows = _rows_laden("SELECT id, fakt_text FROM fakten ORDER BY id")
    return _pg_ziel_verarbeiten(
        "fakten", rows,
        lambda r: FaktenRepository.embed_text_bauen(r["fakt_text"])
        if (r["fakt_text"] or "").strip() else None,
        lambda rid, emb: _pg_update("UPDATE fakten SET embedding = %s::vector WHERE id = %s", emb, rid),
        commit,
    )


def ziel_ziele(commit: bool) -> dict:
    """ziele.embedding — Formel: memory/ziele.py::embed_text_bauen."""
    rows = _rows_laden("SELECT id, zielsatz FROM ziele ORDER BY id")
    return _pg_ziel_verarbeiten(
        "ziele", rows,
        lambda r: ziel_embed_text_bauen(r["zielsatz"]) if (r["zielsatz"] or "").strip() else None,
        lambda rid, emb: _pg_update("UPDATE ziele SET embedding = %s::vector WHERE id = %s", emb, rid),
        commit,
    )


def ziel_delegation(commit: bool) -> dict:
    """delegations_akten.themen_embedding — Formel: akte.py::embed_text_bauen.

    139 Altakten haben zusammenfassung leer (nie gespeichert, Commit ce0efc8)
    — der Bauer faellt dann auf die Themen allein zurueck; nur wenn BEIDE
    Felder leer sind, wird uebersprungen.
    """
    rows = _rows_laden("SELECT id, themen, zusammenfassung FROM delegations_akten ORDER BY id")

    def text_bauen(r: dict):
        themen = (r["themen"] or "").strip()
        zusammenfassung = (r["zusammenfassung"] or "").strip()
        if not themen and not zusammenfassung:
            return None
        return delegation_embed_text_bauen(r["themen"] or "", r["zusammenfassung"] or "")

    return _pg_ziel_verarbeiten(
        "delegation", rows, text_bauen,
        lambda rid, emb: _pg_update(
            "UPDATE delegations_akten SET themen_embedding = %s::vector WHERE id = %s", emb, rid
        ),
        commit,
    )


def ziel_kzg(commit: bool) -> dict:
    """KZG-Hashes in Redis — Formel: agents/kzg/speicher.py::embed_text_bauen.

    Heikelster Pfad: rohe float32-Bytes, raw_redis ohne decode (Muster aus
    migrate_kzg_keys.py). hset auf das einzelne embedding-Feld laesst TTL
    und alle anderen Felder unberuehrt.
    """
    stats: dict = {"gelesen": 0, "embedded": 0, "geschrieben": 0, "uebersprungen": 0}
    beispiele: int = 0

    for key_bytes in raw_redis.scan_iter(match="kzg:*", count=200):
        stats["gelesen"] += 1
        key: str = key_bytes.decode("utf-8")
        themen: str = (raw_redis.hget(key_bytes, "themen") or b"").decode("utf-8")
        inhalt: str = (raw_redis.hget(key_bytes, "inhalt") or b"").decode("utf-8")

        if not inhalt.strip():
            stats["uebersprungen"] += 1
            logger.error("[kzg] %s: inhalt leer — uebersprungen (Alt-Vektor ohne Quelltext, verfaellt per TTL)", key)
            continue

        text: str = kzg_embed_text_bauen(themen, inhalt)

        if not commit:
            if beispiele < 3:
                logger.info("[kzg] Beispiel %s: '%.70s...'", key, text)
                beispiele += 1
            continue

        embedding: list[float] = embedding_berechnen(text)
        stats["embedded"] += 1
        raw_redis.hset(key_bytes, "embedding", np.asarray(embedding, dtype=np.float32).tobytes())
        stats["geschrieben"] += 1

        if stats["gelesen"] % PROGRESS_INTERVALL == 0:
            logger.info("[kzg] Fortschritt: %d Hashes", stats["gelesen"])

    logger.info("[kzg] %d Hashes gelesen", stats["gelesen"])
    return stats


def ziel_shadow(commit: bool) -> dict:
    """Shadow-Stacks — werden GELOESCHT, nicht re-embedded (kurzlebig)."""
    stats: dict = {"gelesen": 0, "embedded": 0, "geschrieben": 0, "uebersprungen": 0}
    keys: list = list(raw_redis.scan_iter(match="shadow_stack:*", count=100))
    stats["gelesen"] = len(keys)
    for key in keys:
        eintraege: int = raw_redis.llen(key)
        if commit:
            raw_redis.delete(key)
            stats["geschrieben"] += 1
            logger.info("[shadow] %s geloescht (%d Eintraege)", key.decode("utf-8"), eintraege)
        else:
            logger.info("[shadow] %s wuerde geloescht (%d Eintraege)", key.decode("utf-8"), eintraege)
    return stats


def ziel_reset(commit: bool) -> dict:
    """Gewichts-Reset + Kanten-Loeschung (Migrations-Reset, Phase B Schritt 2).

    Rechnet den Anlagezustand ueber die ECHTE Initialisierungslogik zurueck
    (memory/lzg_knoten.py::knoten_gewichte_zuruecksetzen — dieselbe
    gewicht_absolut_berechnen wie knoten_anlegen, Boost aus der config).
    Bricht den GESAMTEN Lauf ab, wenn die Rekonstruktion bei irgendeinem
    Knoten initial_roh <= 0 ergaebe. Loescht bei --commit alle lzg_kanten
    (Neuaufbau: --target kanten_rebuild).
    """
    stats: dict = {"gelesen": 0, "embedded": 0, "geschrieben": 0, "uebersprungen": 0}

    ergebnis: dict = lzg_knoten.knoten_gewichte_zuruecksetzen(
        POSTGRES_URL, commit=commit, beispiel_ids=RESET_BEISPIEL_IDS,
    )
    stats["gelesen"] = ergebnis["knoten"]
    stats["geschrieben"] = ergebnis["geschrieben"]

    if ergebnis["error"]:
        raise SystemExit(1)  # Verletzungen bereits einzeln als error geloggt

    for b in ergebnis["beispiele"]:
        logger.info(
            "[reset] Knoten %s VORHER: roh=%.3f absolut=%.3f decay=%.3f haeufigkeit=%d verstaerkt_am=%s",
            b["id"], b["vorher"]["roh"], b["vorher"]["absolut"], b["vorher"]["decay"],
            b["vorher"]["haeufigkeit"], b["vorher"]["verstaerkt_am"],
        )
        logger.info(
            "[reset] Knoten %s NACHHER: roh=%.3f absolut=%.3f decay=%.3f haeufigkeit=%d verstaerkt_am=%s",
            b["id"], b["nachher"]["roh"], b["nachher"]["absolut"], b["nachher"]["decay"],
            b["nachher"]["haeufigkeit"], b["nachher"]["verstaerkt_am"],
        )

    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM lzg_kanten")
            kanten_anzahl: int = cur.fetchone()[0]
    finally:
        conn.close()

    if commit:
        geloescht: int = lzg_kanten.kanten_alle_loeschen(POSTGRES_URL)
        if geloescht < 0:
            raise SystemExit(1)
        logger.info("[reset] %d Kanten geloescht — Neuaufbau via --target kanten_rebuild", geloescht)
    else:
        logger.info("[reset] %d Kanten wuerden geloescht (Neuaufbau via --target kanten_rebuild)", kanten_anzahl)
    return stats


def ziel_kanten_rebuild(commit: bool, reset_dabei: bool) -> dict:
    """Kanten-Neuaufbau nach Reset (Phase B Schritt 3, IMMER als letztes).

    Chronologisch ueber kzg_erstellt_am, echte Bausteine
    (kandidaten_mit_cosine_laden + kanten_fuer_neuen_knoten_bilden) —
    siehe memory/lzg_kanten.py::kanten_alle_neu_aufbauen.
    """
    if not reset_dabei:
        logger.warning(
            "[kanten_rebuild] reset ist NICHT Teil dieses Laufs — der Aufbau friert "
            "die AKTUELLEN gewicht_absolut-Werte in die Kantenstaerken ein. Nur "
            "sinnvoll, wenn der Reset bereits vorher gelaufen ist."
        )
    stats: dict = {"gelesen": 0, "embedded": 0, "geschrieben": 0, "uebersprungen": 0}
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM lzg_knoten WHERE aktiv = TRUE AND embedding IS NOT NULL")
            stats["gelesen"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM lzg_kanten")
            bestand: int = cur.fetchone()[0]
    finally:
        conn.close()

    if not commit:
        logger.info(
            "[kanten_rebuild] wuerde das Netz fuer %d aktive Knoten chronologisch neu "
            "aufbauen (aktueller Kanten-Bestand: %d)", stats["gelesen"], bestand,
        )
        return stats

    ergebnis: dict = lzg_kanten.kanten_alle_neu_aufbauen(POSTGRES_URL)
    if ergebnis["error"]:
        raise SystemExit(1)
    stats["geschrieben"] = ergebnis["paare"]
    return stats


def ziel_kanten(commit: bool, lzg_dabei: bool) -> dict:
    """lzg_kanten.embedding_cosine_initial — Refresh + Gewichts-Neuberechnung."""
    if not lzg_dabei:
        logger.warning(
            "[kanten] lzg_knoten ist NICHT Teil dieses Laufs — der Cosine-Refresh "
            "rechnet dann auf dem aktuellen Embedding-Bestand, nicht auf frisch "
            "re-embeddeten Knoten. Nur sinnvoll, wenn lzg_knoten bereits vorher lief."
        )
    stats: dict = {"gelesen": 0, "embedded": 0, "geschrieben": 0, "uebersprungen": 0}
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM lzg_kanten WHERE embedding_cosine_initial IS NOT NULL")
            stats["gelesen"] = cur.fetchone()[0]
    finally:
        conn.close()
    logger.info("[kanten] %d Kanten mit Initial-Cosine", stats["gelesen"])
    if commit:
        stats["geschrieben"] = lzg_kanten.embedding_cosine_alle_aktualisieren(POSTGRES_URL)
    return stats


def ziel_legacy(commit: bool) -> dict:
    """langzeitgedaechtnis — VERWEIGERT: keine embed_text_bauen-Formel.

    Der Legacy-Pfad ist bewusst kein Bauer-Ziel (Commit 5d58b66). Eine
    Formel hier im Tool nachzubauen waere genau der Fehler, den die
    Vereinheitlichung abschafft — melden, nicht improvisieren.
    """
    logger.error(
        "[legacy] langzeitgedaechtnis hat KEINE embed_text_bauen-Formel (bewusst "
        "kein Bauer-Ziel, Commit 5d58b66). Das Tool improvisiert keine Formel. "
        "Entscheidung noetig: Bauer anlegen oder Tabelle stilllegen "
        "(Backlog: Landmine in EMBEDDING-CASING-BLIND §6)."
    )
    raise SystemExit(1)


# ─────────────────────────────────────────────
# Selbstkontrolle (nach --commit mit Ziel lzg_knoten)
# ─────────────────────────────────────────────

def selbstkontrolle() -> bool:
    """Prueft die Referenzpaare direkt in der DB (nicht aus dem Speicher).

    Abweichung > KONTROLL_TOLERANZ -> logger.error (anderer Text embedded,
    anderes Modell benutzt, oder das UPDATE hat nicht gegriffen). Fehlende
    oder inaktive Referenzknoten -> Warnung, kein Abbruch.
    Liefert True, wenn alle prueffbaren Paare im Toleranzband liegen.
    """
    # ── Verarbeitung ────────────────────────────
    alles_ok: bool = True
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            for a_id, b_id, erwartet in KONTROLL_PAARE:
                cur.execute(
                    """
                    SELECT 1 - (a.embedding <=> b.embedding)
                    FROM lzg_knoten a, lzg_knoten b
                    WHERE a.id = %s AND b.id = %s
                      AND a.aktiv AND b.aktiv
                      AND a.embedding IS NOT NULL AND b.embedding IS NOT NULL
                    """,
                    (a_id, b_id),
                )
                row = cur.fetchone()
                if row is None:
                    logger.warning(
                        "Selbstkontrolle: Referenzpaar %d/%d nicht pruefbar (fehlt, inaktiv "
                        "oder ohne Embedding) — uebersprungen", a_id, b_id,
                    )
                    continue
                ist: float = float(row[0])
                abweichung: float = abs(ist - erwartet)
                if abweichung > KONTROLL_TOLERANZ:
                    alles_ok = False
                    logger.error(
                        "Selbstkontrolle FEHLGESCHLAGEN: Paar %d/%d — erwartet %.4f, "
                        "gemessen %.4f (Abweichung %.4f > %.2f). Anderer Text embedded, "
                        "anderes Modell benutzt, oder das UPDATE hat nicht gegriffen.",
                        a_id, b_id, erwartet, ist, abweichung, KONTROLL_TOLERANZ,
                    )
                else:
                    logger.info(
                        "Selbstkontrolle ok: Paar %d/%d — erwartet %.4f, gemessen %.4f",
                        a_id, b_id, erwartet, ist,
                    )
    finally:
        conn.close()

    # ── Ausgabe ─────────────────────────────────
    return alles_ok


# ─────────────────────────────────────────────
# Einstieg
# ─────────────────────────────────────────────

def main() -> int:
    """Kommandozeilen-Einstieg: Ziele aufloesen, Sicherheitsnetze, Lauf, Bilanz."""
    # ── Eingabe-Validierung ─────────────────────
    parser = argparse.ArgumentParser(description="Re-Embedding aller Vektor-Speicher (A5, Chat 107)")
    parser.add_argument("--target", action="append", choices=ZIEL_REIHENFOLGE + ["all"],
                        help="Ziel, mehrfach angebbar. Default: all (ohne legacy)")
    parser.add_argument("--commit", action="store_true", help="Tatsaechlich schreiben (sonst Dry-Run)")
    args = parser.parse_args()

    gewaehlt: list[str] = args.target or ["all"]
    ziele: list[str] = []
    for z in gewaehlt:
        ziele.extend(ALL_ZIELE if z == "all" else [z])
    # Kanonische Reihenfolge, Duplikate raus, kanten dadurch immer zuletzt.
    ziele = [z for z in ZIEL_REIHENFOLGE if z in ziele]

    logger.info("=" * 70)
    logger.info("MODELL: %s (config.EMBED_MODEL)", EMBED_MODEL)
    logger.info("Modus: %s | Ziele: %s", "COMMIT" if args.commit else "DRY-RUN", ", ".join(ziele))

    # ── Sicherheitsnetz 1 (immer, nicht abschaltbar) ──
    casing_pruefung()

    # ── Verarbeitung ────────────────────────────
    handler = {
        "lzg_knoten": lambda: ziel_lzg_knoten(args.commit),
        "entitaeten": lambda: ziel_entitaeten(args.commit),
        "fakten":     lambda: ziel_fakten(args.commit),
        "ziele":      lambda: ziel_ziele(args.commit),
        "delegation": lambda: ziel_delegation(args.commit),
        "kzg":        lambda: ziel_kzg(args.commit),
        "legacy":     lambda: ziel_legacy(args.commit),
        "shadow":     lambda: ziel_shadow(args.commit),
        "reset":      lambda: ziel_reset(args.commit),
        "kanten":     lambda: ziel_kanten(args.commit, lzg_dabei="lzg_knoten" in ziele),
        "kanten_rebuild": lambda: ziel_kanten_rebuild(args.commit, reset_dabei="reset" in ziele),
    }
    bilanz: dict[str, dict] = {}
    for ziel in ziele:
        logger.info("-" * 70)
        bilanz[ziel] = handler[ziel]()

    # ── Ausgabe: Zusammenfassung ────────────────
    logger.info("=" * 70)
    logger.info("ZUSAMMENFASSUNG (%s)", "COMMIT" if args.commit else "TROCKENLAUF — nichts geschrieben")
    logger.info("%-12s %9s %9s %12s %14s", "Ziel", "gelesen", "embedded", "geschrieben", "uebersprungen")
    for ziel, s in bilanz.items():
        logger.info("%-12s %9d %9d %12d %14d",
                    ziel, s["gelesen"], s["embedded"], s["geschrieben"], s["uebersprungen"])

    kontrolle_ok: bool = True
    if args.commit and "lzg_knoten" in ziele:
        logger.info("-" * 70)
        kontrolle_ok = selbstkontrolle()

    if args.commit:
        logger.info("-" * 70)
        logger.info(
            "NAECHSTE SCHRITTE (Phase B): Container NEU ERZEUGEN mit "
            "'docker compose up -d' — ein blosser Restart liest die geaenderte "
            "Compose-Env (EMBED_MODEL) NICHT neu ein. Der Neustart loest zugleich "
            "den _strategie_embeddings_cache in ei/dreischicht.py (Alt-Vektoren im "
            "Prozess-Speicher)."
        )
    logger.info("MODELL: %s (config.EMBED_MODEL)", EMBED_MODEL)
    return 0 if kontrolle_ok else 1


if __name__ == "__main__":
    sys.exit(main())
