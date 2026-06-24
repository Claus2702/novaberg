"""Throwaway-Verifikation: anker_retrieval mit den exakten Thinker-Parametern.

Ruft anker_retrieval(user_id="meister", character_id="nova", top_k=20,
min_similarity=0.0) gegen die Live-lzg_knoten auf und prueft das zurueck-
gegebene Dict-Format, das der Thinker-Faktencheck (_format_faktencheck_treffer)
konsumiert: Keys id + beobachter vorhanden, Cosine-absteigende Reihenfolge.

Embedding-Weg: direkter ollama_gpu_client.embed(model=EMBED_MODEL, ...) —
exakt derselbe Client + dasselbe Modell wie der EmbedWorker, den der Thinker
ueber model_service.embed nutzt (siehe embed_worker.py:36-37). Der Vektor ist
identisch; der Worker wird hier bewusst umgangen, weil ein Throwaway-Skript
keinen Server-Event-Loop hat (gleiche Entscheidung wie tools/migrate_*).

Aufruf im Server-Container (NICHT in der Sandbox):
    docker compose exec --workdir /app server python -m scripts.test_anker_retrieval
"""

import logging

from config            import POSTGRES_URL, EMBED_MODEL, ollama_gpu_client
from memory.lzg_knoten import anker_retrieval
from memory.utils      import embedding_zu_pgvector_str

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("test_anker_retrieval")

# Feste Test-Parameter — exakt die Thinker-Schnittstelle.
TEST_QUERY:     str   = "Wie heißt mein Lieblings-Pflänzchen?"
USER_ID:        str   = "meister"
CHARACTER_ID:   str   = "nova"
TOP_K:          int   = 20
MIN_SIMILARITY: float = 0.0


def embedding_berechnen(text: str) -> list[float]:
    """Berechnet das Embedding ueber den direkten Ollama-GPU-Client.

    Identischer Endpunkt und identisches Modell (EMBED_MODEL) wie der
    EmbedWorker im Live-Betrieb — der Vektor entspricht dem, den der Thinker
    ueber model_service.embed bekaeme.
    Fehlerfall: Ollama liefert keine Embeddings -> RuntimeError (fail loud).
    """
    antwort = ollama_gpu_client.embed(model=EMBED_MODEL, input=text)
    embeddings = antwort.get("embeddings")
    if not embeddings:
        raise RuntimeError(f"Ollama lieferte kein Embedding (Modell={EMBED_MODEL})")
    return list(embeddings[0])


def main() -> None:
    """Embedet die Test-Query, ruft anker_retrieval auf und verifiziert das Ergebnis."""

    # ── Eingabe: Embedding erzeugen (Thinker-Weg) ───────────────
    logger.info("Test-Query: %r", TEST_QUERY)
    embedding: list[float] = embedding_berechnen(TEST_QUERY)
    embedding_str: str = embedding_zu_pgvector_str(embedding)
    logger.info("Embedding erzeugt (Dim: %d, Modell: %s)", len(embedding), EMBED_MODEL)

    # ── Verarbeitung: anker_retrieval mit Thinker-Parametern ────
    logger.info(
        "anker_retrieval(user_id=%r, character_id=%r, top_k=%d, min_similarity=%.1f)",
        USER_ID, CHARACTER_ID, TOP_K, MIN_SIMILARITY,
    )
    treffer: list[dict] = anker_retrieval(
        POSTGRES_URL,
        USER_ID,
        CHARACTER_ID,
        embedding_str,
        top_k=TOP_K,
        min_similarity=MIN_SIMILARITY,
    )

    # ── Ausgabe: Treffer drucken (robust gegen leeres Ergebnis) ─
    print("\n" + "=" * 72)
    if not treffer:
        print("ERGEBNIS: 0 Treffer.")
        print(
            "Hinweis: Leeres Ergebnis kann korrekt sein (kein passender Knoten "
            "fuer das Paar meister/nova) oder auf eine leere lzg_knoten-Partition "
            "hindeuten — am Live-Schema gegenpruefen."
        )
        print("=" * 72)
        return

    for i, t in enumerate(treffer, start=1):
        cosine = t.get("cosine")
        cosine_txt = f"{cosine:.4f}" if cosine is not None else "None"
        inhalt = (t.get("inhalt") or "")[:60]
        print(
            f"[{i:2d}] id={t.get('id')} cosine={cosine_txt} "
            f"beobachter={t.get('beobachter')!r} dimension={t.get('dimension')!r}"
        )
        print(f"     inhalt[:60]: {inhalt!r}")

    # ── Verifikation: Trefferzahl, Pflicht-Keys, Sortierung ─────
    print("-" * 72)
    print(f"Trefferzahl: {len(treffer)}")

    keys_ok: bool = all(("id" in t and "beobachter" in t) for t in treffer)
    print(f"Alle Treffer tragen Keys id UND beobachter: {keys_ok}")
    if not keys_ok:
        fehlende = [
            t.get("id", "?")
            for t in treffer
            if not ("id" in t and "beobachter" in t)
        ]
        print(f"  -> Treffer ohne vollstaendige Keys (id-Anzeige): {fehlende}")

    cosines = [t.get("cosine") for t in treffer]
    sortiert_ok: bool = all(
        a is not None and b is not None and a >= b
        for a, b in zip(cosines, cosines[1:])
    )
    print(f"Reihenfolge cosine-absteigend: {sortiert_ok}")
    if not sortiert_ok:
        print(f"  -> Cosine-Folge: {[round(c, 4) if c is not None else None for c in cosines]}")

    print("=" * 72)


if __name__ == "__main__":
    main()
