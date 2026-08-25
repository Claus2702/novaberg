"""
Memory Package — Re-Exports.

Aufbau:
  embedding.py     — Vektor-Erzeugung
  kzg.py           — Kurzzeitgedächtnis (Redis Stack)
  lzg.py           — Langzeitgedächtnis (pgvector)
  charakter.py     — Charakter-Hash
  session.py       — Gesprächskontext
  repositories/    — CRUD-Zugriff auf Entitäten, Fakten, Timeline, Notizen
  services/        — Entity Resolution
"""

# KZG
# Charakter-Hash
from memory.charakter import charakter_hash_retrieve
from memory.kzg import (
    EMBEDDING_DIM,
    KZG_INDEX_NAME,
    KZG_PREFIX,
    PROMOTION_THRESHOLD,
    SIMILARITY_THRESHOLD,
    kzg_entries_retrieve,
    kzg_index_create,
    kzg_similar_find,
    kzg_store,
)

# Repositories (M2-M6)
from memory.repositories import (
    EntitaetenRepository,
    FaktenRepository,
    NotizenRepository,
    TimelineRepository,
)
from memory.services import EntityResolutionService

# Session
from memory.session import (
    SESSION_MAX_TURNS,
    SESSION_SUMMARIZE_AT,
    SESSION_TTL,
    session_context_build,
    session_reset,
    session_summarize_if_needed,
    session_turn_mark_action,
    session_turn_store,
    session_turns_retrieve,
)
