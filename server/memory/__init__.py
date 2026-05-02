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

# Embedding
from memory.embedding import embedding_create

# KZG
from memory.kzg import (
    kzg_index_create,
    kzg_similar_find,
    kzg_store,
    kzg_entries_retrieve,
    EMBEDDING_DIM,
    SIMILARITY_THRESHOLD,
    PROMOTION_THRESHOLD,
    KZG_INDEX_NAME,
    KZG_PREFIX,
)

# LZG
from memory.lzg import lzg_entries_retrieve

# Charakter-Hash
from memory.charakter import charakter_hash_retrieve

# Session
from memory.session import (
    session_turn_store,
    session_turn_mark_action,
    session_summarize_if_needed,
    session_turns_retrieve,
    session_context_build,
    session_reset,
    SESSION_MAX_TURNS,
    SESSION_TTL,
    SESSION_SUMMARIZE_AT,
)

# Repositories (M2-M6)
from memory.repositories import (
    EntitaetenRepository,
    FaktenRepository,
    TimelineRepository,
    NotizenRepository,
)
from memory.services import EntityResolutionService
