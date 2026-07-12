"""Migration langzeitgedaechtnis -> Synapsen-Netz (lzg_knoten/lzg_kanten).

Einmal-Migration der kuratierten Alt-Erinnerungen in das Synapsen-Modell.
Liest die Kuratierung aus lzg_migration_review (uebernehmen-Flag, inhalt_neu
fuer die Namens-Normalisierung) und die vollstaendigen Quellfelder aus
langzeitgedaechtnis. Schreibt jeden uebernommenen Eintrag als eigenstaendigen
lzg_knoten durch die echte Phase-B-Maschinerie und bildet Kanten zu den schon
migrierten Knoten.

Entscheidungen (Chat 98):
  - Embedding aus dem (ggf. normalisierten) inhalt allein, neu berechnet ueber
    den direkten Ollama-GPU-Client (2b, K9-konform). KEIN Worker noetig — eine
    Einmal-Migration hat keinen Server-Loop.
  - gewicht_roh = altes gewicht * 3 (Skalen-Anhebung; Alt-Skala ~0.27..1.70,
    neue gewicht_roh-Skala 0..10). Knoten starten praesent mit Luft nach oben.
  - Match-Schwelle als CLI-Parameter (Default 0.90), NICHT die Live-Konstante
    LZG_KNOTEN_MATCH_SCHWELLE — die Migration darf strenger sein als der
    Live-Pfad, ohne ihn zu veraendern.
  - entitaet_ids=[] und timeline_id=None: Alt-Eintraege tragen keine
    P3-Magnet-Felder. Es feuern nur Embedding- und Themen-Kantenschicht.

Dry-Run (Default): schreibt NICHTS. Die Match-Kaskade wird im Speicher
simuliert (Python-Cosine gegen die in dieser Sitzung schon "angelegten"
Knoten), damit die Vorschau ehrlich ist — im echten lzg_knoten stuende sonst
nichts, und jeder Eintrag meldete faelschlich NEU.

--commit: schreibt ueber knoten_anlegen / knoten_verstaerken und bildet Kanten
(Trigger 1 / Trigger 2), markiert lzg_migration_review.migriert + lzg_knoten_id.
Idempotent: ein erneuter Lauf ueberspringt bereits migrierte Eintraege.

Aufruf (im Server-Container, analog zu den bestehenden tools/migrate_*-Skripten):
    docker compose exec --workdir /app server python -m tools.migrate_lzg_synapsen
    docker compose exec --workdir /app server python -m tools.migrate_lzg_synapsen --schwelle 0.93
    docker compose exec --workdir /app server python -m tools.migrate_lzg_synapsen --commit
"""

import argparse
import logging
import sys

import numpy as np
import psycopg2
import psycopg2.extras

from config import POSTGRES_URL, ollama_gpu_client, EMBED_MODEL
from memory import lzg_knoten, lzg_kanten

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("migrate_lzg_synapsen")

# Migrations-Faktor: hebt die Alt-gewicht-Skala (~0.27..1.70) auf die neue
# gewicht_roh-Skala (0..10). Entscheidung Chat 98.
GEWICHT_FAKTOR: float = 3.0


# ─────────────────────────────────────────────
# Embedding (direkter Ollama-GPU-Client, ohne Worker)
# ─────────────────────────────────────────────

def embedding_berechnen(text: str) -> list[float]:
    """Berechnet das Embedding eines Textes ueber den direkten Ollama-Client.

    Nutzt denselben Endpunkt (OLLAMA_GPU_URL) und dasselbe Modell (EMBED_MODEL)
    wie der EmbedWorker im Live-Betrieb — identische Vektoren, kein Versatz.
    """
    antwort = ollama_gpu_client.embed(model=EMBED_MODEL, input=text)
    embeddings = antwort.get("embeddings")
    if not embeddings:
        raise RuntimeError(f"Ollama lieferte kein Embedding (Modell={EMBED_MODEL})")
    return list(embeddings[0])


def embedding_str_bauen(embedding: list[float]) -> str:
    """pgvector-Literal '[v1,v2,...]' — identisch zum Live-Schreibpfad."""
    return "[" + ",".join(str(x) for x in embedding) + "]"


# ─────────────────────────────────────────────
# Quelldaten laden
# ─────────────────────────────────────────────

def eintraege_laden() -> list[dict]:
    """Laedt die zu migrierenden Eintraege: Kuratierung aus lzg_migration_review,
    vollstaendige Quellfelder aus langzeitgedaechtnis (JOIN). Chronologisch nach
    kzg_erstellt_am, damit die Kantenbildung zeitlich plausibel waechst.
    """
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT r.id,
                       COALESCE(r.inhalt_neu, l.inhalt) AS text,
                       l.user_id, l.character_id, l.beobachter, l.dimension,
                       l.gedaechtnistyp, l.intentionen, l.gewicht, l.themen,
                       l.emotion, l.arousal, l.modus, l.sprach_stil,
                       l.beziehungs_dynamik, l.tone,
                       EXTRACT(EPOCH FROM COALESCE(l.kzg_erstellt_am, l.erstellt_am)) AS kzg_epoch
                FROM lzg_migration_review r
                JOIN langzeitgedaechtnis l ON l.id = r.id
                WHERE r.uebernehmen AND NOT r.migriert
                ORDER BY l.kzg_erstellt_am NULLS LAST, r.id
                """
            )
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def review_markieren(quell_id: int, knoten_id: int) -> None:
    """Markiert einen Review-Eintrag als migriert (idempotenter Wiederanlauf)."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE lzg_migration_review SET migriert = TRUE, lzg_knoten_id = %s WHERE id = %s",
                (knoten_id, quell_id),
            )
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Cosine (fuer die Dry-Run-Simulation im Speicher)
# ─────────────────────────────────────────────

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine-Similarity zweier Vektoren."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ─────────────────────────────────────────────
# Dry-Run: Match-Kaskade im Speicher simulieren
# ─────────────────────────────────────────────

def dry_run(eintraege: list[dict], schwelle: float) -> None:
    """Simuliert die Migration ohne DB-Schreibzugriff. Bettet jeden Text ein
    und prueft den Match gegen die in dieser Sitzung schon 'angelegten' Knoten
    (Python-Cosine) — eine ehrliche Vorschau der Merge-Entscheidungen.
    """
    logger.info("DRY-RUN (kein Schreibzugriff) — Schwelle=%.3f, %d Eintraege", schwelle, len(eintraege))
    simuliert: list[dict] = []  # {id, embedding (np.ndarray)}
    neu = 0
    merges = 0

    for e in eintraege:
        emb = np.asarray(embedding_berechnen(lzg_knoten.embed_text_bauen(e["text"])), dtype=np.float32)
        bester_id = None
        bester_cos = -1.0
        for s in simuliert:
            c = cosine(emb, s["embedding"])
            if c > bester_cos:
                bester_cos, bester_id = c, s["id"]

        roh = e["gewicht"] * GEWICHT_FAKTOR
        absolut = lzg_knoten.gewicht_absolut_berechnen(roh)

        if bester_id is not None and bester_cos >= schwelle:
            merges += 1
            logger.info(
                "[MATCH]  id=%s -> wuerde id=%s verstaerken (cosine=%.4f) | '%s'",
                e["id"], bester_id, bester_cos, e["text"][:50],
            )
        else:
            neu += 1
            simuliert.append({"id": e["id"], "embedding": emb})
            logger.info(
                "[NEU]    id=%s  roh=%.2f absolut=%.2f  top_cos=%.4f | '%s'",
                e["id"], roh, absolut, max(bester_cos, 0.0), e["text"][:50],
            )

    logger.info("─" * 60)
    logger.info("DRY-RUN Zusammenfassung bei Schwelle %.3f: %d neue Knoten, %d Merges",
                schwelle, neu, merges)
    logger.info("Kein Schreibzugriff erfolgt. Mit --commit ausfuehren, wenn die Liste passt.")


# ─────────────────────────────────────────────
# Commit: echter Schreibpfad ueber die Phase-B-Maschinerie
# ─────────────────────────────────────────────

def commit_run(eintraege: list[dict], schwelle: float) -> None:
    """Schreibt die Migration in lzg_knoten/lzg_kanten. Pro Eintrag: Embedding,
    Kandidaten laden, eigene Schwellen-Pruefung; bei Match knoten_verstaerken +
    Trigger 2, sonst knoten_anlegen + knoten_laden + Trigger 1. Idempotent.
    """
    logger.info("COMMIT — Schwelle=%.3f, %d Eintraege", schwelle, len(eintraege))
    neu = 0
    merges = 0
    fehler = 0

    for e in eintraege:
        try:
            emb = embedding_berechnen(lzg_knoten.embed_text_bauen(e["text"]))
            emb_str = embedding_str_bauen(emb)

            kandidaten = lzg_knoten.kandidaten_mit_cosine_laden(
                POSTGRES_URL, e["user_id"], e["character_id"], emb_str,
            )
            # Eigene Schwellen-Pruefung (nicht match_pruefen, das die
            # Live-Konstante nutzt): Kandidaten sind nach cosine DESC sortiert.
            top = kandidaten[0] if kandidaten else None
            ist_match = top is not None and top.get("cosine") is not None and top["cosine"] >= schwelle

            roh = e["gewicht"] * GEWICHT_FAKTOR

            if ist_match:
                lzg_knoten.knoten_verstaerken(POSTGRES_URL, top["id"])
                kanten_neu = lzg_kanten.kanten_neuberechnen_fuer_knoten(POSTGRES_URL, top["id"])
                review_markieren(e["id"], top["id"])
                merges += 1
                logger.info("[MATCH]  id=%s -> Knoten %s verstaerkt (cosine=%.4f, kanten_neu=%d)",
                            e["id"], top["id"], top["cosine"], kanten_neu)
            else:
                neue_id = lzg_knoten.knoten_anlegen(
                    POSTGRES_URL,
                    kzg_quell_key=f"migration:lzg:{e['id']}",
                    user_id=e["user_id"], character_id=e["character_id"],
                    beobachter=e["beobachter"], inhalt=e["text"], embedding_str=emb_str,
                    dimension=e["dimension"], gewicht_roh=roh, kzg_erstellt_am=float(e["kzg_epoch"]),
                    themen=e["themen"] or [], gedaechtnistyp=e["gedaechtnistyp"],
                    entitaet_ids=[], timeline_id=None,
                    emotion=e["emotion"] or "", arousal=e["arousal"] if e["arousal"] is not None else 0.5,
                    emotions_vektor="", intentionen=e["intentionen"] or "[]",
                    modus=e["modus"] or "", sprach_stil=e["sprach_stil"] or "",
                    beziehungs_dynamik=e["beziehungs_dynamik"] or "", tone=e["tone"] or "",
                )
                if neue_id is None:
                    fehler += 1
                    logger.error("[FEHLER] id=%s — knoten_anlegen lieferte None", e["id"])
                    continue
                neuer = lzg_knoten.knoten_laden(POSTGRES_URL, neue_id)
                paare = lzg_kanten.kanten_fuer_neuen_knoten_bilden(POSTGRES_URL, neuer, kandidaten) if neuer else 0
                review_markieren(e["id"], neue_id)
                neu += 1
                logger.info("[NEU]    id=%s -> Knoten %s (roh=%.2f, kanten_paare=%d)",
                            e["id"], neue_id, roh, paare)
        except Exception as ex:
            fehler += 1
            logger.error("[FEHLER] id=%s — %s", e["id"], ex, exc_info=True)

    logger.info("─" * 60)
    logger.info("COMMIT abgeschlossen: %d neue Knoten, %d Merges, %d Fehler", neu, merges, fehler)


# ─────────────────────────────────────────────
# Einstieg
# ─────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Migration langzeitgedaechtnis -> Synapsen-Netz")
    parser.add_argument("--commit", action="store_true",
                        help="Tatsaechlich schreiben (sonst Dry-Run)")
    # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.90 im
    # casing-blinden Raum. Bleibt strenger als die Live-Konstante
    # LZG_KNOTEN_MATCH_SCHWELLE (0.82), wie urspruenglich entschieden.
    parser.add_argument("--schwelle", type=float, default=0.85,
                        help="Match-Schwelle (Default 0.85). Cosine >= Schwelle -> Verstaerkung statt Neuanlage")
    args = parser.parse_args()

    eintraege = eintraege_laden()
    if not eintraege:
        logger.info("Keine offenen Eintraege (uebernehmen AND NOT migriert) — nichts zu tun.")
        return 0

    if args.commit:
        commit_run(eintraege, args.schwelle)
    else:
        dry_run(eintraege, args.schwelle)
    return 0


if __name__ == "__main__":
    sys.exit(main())
