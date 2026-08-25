"""Session-Verwaltung — Reset und Kontext-Abruf."""

from fastapi import APIRouter

from config import ASSISTANT_USER_ID, redis_client
from memory.session import _session_key, session_reset, session_turns_retrieve

router = APIRouter()


@router.post("/session/reset/{user_id}")
def session_zuruecksetzen(user_id: str, character_id: str = ASSISTANT_USER_ID):
    """Gesprächs-Session eines Paares zurücksetzen."""
    session_reset(redis_client, user_id, character_id)
    return {"status": "ok", "nachricht": f"Session für '{user_id}:{character_id}' zurückgesetzt."}


@router.get("/session/kontext/{user_id}")
def session_kontext_abrufen(
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
