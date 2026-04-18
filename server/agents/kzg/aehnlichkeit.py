"""Aehnlichkeitssuche — Embedding + Redis-Vektorsuche + Themen-Overlap.

Nutzt die bestehende kzg_similar_find() aus memory/kzg.py
und erzeugt das Embedding ueber embedding_create().
"""

import logging

from agents.base import AgentState
from memory.embedding import embedding_create
from memory.kzg import kzg_similar_find
from config import redis_client

logger = logging.getLogger("ki_server.agents.kzg.aehnlichkeit")


def aehnlichkeit_pruefen(state: AgentState) -> dict:
    """Erzeugt Embedding fuer kern und sucht aehnlichen KZG-Eintrag."""

    kern:        str  = state["parameter"].get("kern", "")
    salienz_obj: dict = state["parameter"].get("salienz_obj", {})
    user_id:     str  = state["kontext"].get("user_id", "")

    # Embedding fuer Verdichtung erzeugen
    valenz:     str = salienz_obj.get("emotionen", {}).get("valenz", "neutral")
    themen:     str = " ".join(salienz_obj.get("themen", []))
    embed_text: str = f"Thema: {themen}. Valenz: {valenz}. Aussage: {kern}"

    embed_client = state["kontext"].get("embed_client")
    embed_model:  str = state["kontext"].get("embed_model", "")

    embedding: list[float] = embedding_create(embed_text, embed_client, embed_model)

    # Aehnlichen Eintrag suchen
    existing = kzg_similar_find(redis_client, user_id, embedding)

    # Themen-Overlap pruefen
    if existing:
        neue_themen:     set = set(t.strip().lower() for t in salienz_obj.get("themen", []))
        existing_themen: set = set(t.strip().lower() for t in existing["themen"].split(","))

        if not neue_themen & existing_themen:
            logger.info(
                f"KZG: Embedding aehnlich, aber Themen disjunkt — neuer Eintrag "
                f"(neu={neue_themen}, existierend={existing_themen})"
            )
            existing = None

    ergebnis: str = "verstaerken" if existing else "neu"
    logger.info(f"KZG-Aehnlichkeit: {ergebnis}")

    return {
        "parameter": {
            **state["parameter"],
            "embedding": embedding,
            "existing":  existing,
        },
        "schritte": state["schritte"] + [
            {"node": "aehnlichkeit", "ergebnis": ergebnis}
        ],
    }
