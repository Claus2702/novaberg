"""
Session-Verwaltung — Reset und Kontext-Abruf.
"""

from fastapi import APIRouter

from config       import redis_client, ASSISTANT_USER_ID
from memory.session import session_reset, session_turns_retrieve
from memory.session import _session_key

router = APIRouter()


@router.post("/session/reset/{user_id}")
def SessionZuruecksetzen(user_id: str, character_id: str = ASSISTANT_USER_ID):
    """Gesprächs-Session eines Paares zurücksetzen."""
    session_reset(redis_client, user_id, character_id)
    return {"status": "ok", "nachricht": f"Session für '{user_id}:{character_id}' zurückgesetzt."}


@router.get("/session/kontext/{user_id}")
def SessionKontextAbrufen(
    user_id: str,
    character_id: str = ASSISTANT_USER_ID,
    beobachter: str | None = None,
):
    """Aktuellen Session-Kontext eines Paares abrufen.

    Bei gesetztem ``beobachter`` (``user``/``assistant``) werden nur Turns
    der passenden Rolle zurueckgegeben; die Zusammenfassung bleibt ungefiltert.
    """
    summary_key: str = _session_key(user_id, character_id, "summary")
    summary:     str = redis_client.get(summary_key) or ""

    turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)

    if beobachter:
        turns = [t for t in turns if t.get("rolle") == beobachter]

    return {
        "zusammenfassung": summary,
        "turns":           turns,
        "anzahl_turns":    len(turns),
    }
