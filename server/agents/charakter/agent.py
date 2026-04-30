"""CharakterAgent — Destilliert 5 Charakter-Profile aus LZG+KZG.

Ein LLM-Call pro Profil pro User. Nur aktiv wenn hash_dirty gesetzt.
Migriert aus: services/shadow_agent/tasks/charakter_hash.py
"""

import logging

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    redis_client,
    ollama_gpu_client,
    EMBED_MODEL,
    POSTGRES_URL,
    ZIEL_MAX_LANGFRISTIG,
    PIXIE_CHARAKTER_PRIORITAET,
    PIXIE_CHARAKTER_INTERVALL_SEKUNDEN,
    PIXIE_CHARAKTER_LZG_LIMIT,
    PIXIE_CHARAKTER_KZG_LIMIT,
)
from tools.db_manager import db_manager
from agents.charakter.destillation import (
    kern_hash_destillieren,
    adaptive_hash_destillieren,
    intentions_profil_destillieren,
    emotions_profil_destillieren,
    beziehungsprofil_destillieren,
    langfristige_ziele_destillieren,
)
from memory.ziele import ziel_speichern, ziele_aktive_laden, ziel_deaktivieren
from memory.embedding import embedding_create

logger = logging.getLogger("ki_server.agents.charakter")


def _hget(rc, key: str, field: str, default: str = "") -> str:
    """Redis HGET mit Bytes-Decoding."""
    val = rc.hget(key, field)
    if val is None:
        return default
    return val.decode("utf-8") if isinstance(val, bytes) else val


class CharakterAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "charakter"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["charakter_hash"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    @property
    def identity_user(self) -> str:
        return ASSISTANT_USER_ID

    def periodic_task(self) -> PeriodicTask | None:
        return PeriodicTask(
            name="charakter_hash",
            priority=PIXIE_CHARAKTER_PRIORITAET,
            interval=PIXIE_CHARAKTER_INTERVALL_SEKUNDEN,
            description="5 Profile destillieren (bei hash_dirty)",
        )

    def build_graph(self):
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Destilliert 5 Charakter-Profile fuer alle dirty User."""

        paare: list[tuple[str, str]] = [
            (DEFAULT_USER_ID, ASSISTANT_USER_ID),
            (ASSISTANT_USER_ID, DEFAULT_USER_ID),
        ]
        gesamt_destilliert: int = 0

        for user_id, character_id in paare:
            # ── Dirty-Check ──────────────────────
            dirty = redis_client.get(f"hash_dirty:{user_id}:{character_id}")
            if not dirty:
                logger.debug(f"CharakterAgent: Kein hash_dirty fuer {user_id}:{character_id}")
                continue

            logger.info(f"CharakterAgent: Starte Destillation fuer {user_id}")

            # ── LZG-Eintraege laden ──────────────
            lzg_kern = self._lzg_kern_laden(user_id)
            lzg_intentionen = self._lzg_intentionen_laden(user_id)
            lzg_emotionen = self._lzg_emotionen_laden(user_id)

            # ── KZG-Eintraege laden ──────────────
            kzg_eintraege = self._kzg_laden(user_id)

            # ── 5 Profile destillieren ───────────
            ergebnis: dict = {
                "kern": "", "adaptiv": "",
                "intentions_profil": "", "emotions_profil": "",
                "beziehungsprofil": "",
            }

            try:
                ergebnis["kern"] = kern_hash_destillieren(lzg_kern, user_id=user_id)
            except Exception as ex:
                logger.error(f"CharakterAgent: Kern-Hash fehlgeschlagen fuer {user_id}: {ex}")

            try:
                ergebnis["adaptiv"] = adaptive_hash_destillieren(kzg_eintraege, user_id=user_id)
            except Exception as ex:
                logger.error(f"CharakterAgent: Adaptive-Hash fehlgeschlagen fuer {user_id}: {ex}")

            try:
                ergebnis["intentions_profil"] = intentions_profil_destillieren(lzg_intentionen, user_id=user_id)
            except Exception as ex:
                logger.error(f"CharakterAgent: Intentions-Profil fehlgeschlagen fuer {user_id}: {ex}")

            try:
                ergebnis["emotions_profil"] = emotions_profil_destillieren(lzg_emotionen)
            except Exception as ex:
                logger.error(f"CharakterAgent: Emotions-Profil fehlgeschlagen fuer {user_id}: {ex}")

            try:
                ergebnis["beziehungsprofil"] = beziehungsprofil_destillieren(kzg_eintraege, user_id=user_id)
            except Exception as ex:
                logger.error(f"CharakterAgent: Beziehungsprofil fehlgeschlagen fuer {user_id}: {ex}")

            # ── In PostgreSQL speichern ──────────
            hat_aenderungen: bool = any(v for v in ergebnis.values())

            if hat_aenderungen:
                try:
                    self._ergebnis_speichern(user_id, character_id, ergebnis)
                    redis_client.delete(f"hash_dirty:{user_id}:{character_id}")
                    gesamt_destilliert += 1
                    logger.info(f"CharakterAgent: {user_id} destilliert (5 Profile)")
                except Exception as ex:
                    logger.error(f"CharakterAgent: Speicherung fehlgeschlagen fuer {user_id}: {ex}")

                # ── Langfristige Ziele aus Kern-Hash destillieren ──
                # Nur für Novas eigenen Hash (ASSISTANT_USER_ID als user_id),
                # nicht für den User-Hash.
                if user_id == ASSISTANT_USER_ID and ergebnis["kern"]:
                    try:
                        neue_ziele: list[dict] = langfristige_ziele_destillieren(
                            ergebnis["kern"], user_id=ASSISTANT_USER_ID,
                        )

                        if neue_ziele:
                            # Alte langfristige Ziele deaktivieren
                            alte_ziele: list[dict] = ziele_aktive_laden(
                                POSTGRES_URL, user_id=ASSISTANT_USER_ID,
                            )
                            for altes in alte_ziele:
                                if altes["ziel_typ"] == "langfristig":
                                    ziel_deaktivieren(POSTGRES_URL, altes["id"])

                            # Neue Ziele speichern (mit Embedding)
                            for z in neue_ziele[:ZIEL_MAX_LANGFRISTIG]:
                                try:
                                    emb: list[float] = embedding_create(
                                        z["zielsatz"], ollama_gpu_client, EMBED_MODEL,
                                    )
                                except Exception:
                                    emb = None

                                ziel_speichern(
                                    postgres_url=POSTGRES_URL,
                                    user_id=ASSISTANT_USER_ID,
                                    ziel_typ="langfristig",
                                    zielsatz=z["zielsatz"],
                                    motivation=0.8,
                                    emotion=z.get("emotion", "neugierig"),
                                    arousal=z.get("arousal", 0.6),
                                    thema=z.get("thema", ""),
                                    embedding=emb,
                                )

                            logger.info(
                                f"CharakterAgent: {len(neue_ziele)} langfristige Ziele "
                                f"für {ASSISTANT_USER_ID} erneuert"
                            )

                    except Exception as ziel_fehler:
                        logger.warning(
                            f"CharakterAgent: Ziel-Destillation fehlgeschlagen — {ziel_fehler}"
                        )
            else:
                logger.info(f"CharakterAgent: Keine Aenderungen fuer {user_id}")

        state["ergebnis"] = {"destilliert": gesamt_destilliert}
        state["status"] = "abgeschlossen"
        return state

    # ─────────────────────────────────────────
    # Daten laden
    # ─────────────────────────────────────────

    def _lzg_kern_laden(self, user_id: str) -> list[dict]:
        """Laedt LZG-Eintraege fuer Kern-Hash (gewichtet nach Gewicht + Haeufigkeit)."""
        return db_manager.select(
            """
            SELECT dimension, inhalt, gewicht, haeufigkeit, verstaerkt_am
            FROM langzeitgedaechtnis
            WHERE user_id = %s AND aktiv = TRUE
            ORDER BY gewicht DESC, haeufigkeit DESC
            LIMIT %s
            """,
            (user_id, PIXIE_CHARAKTER_LZG_LIMIT),
        )

    def _lzg_intentionen_laden(self, user_id: str) -> list[dict]:
        """Laedt LZG-Eintraege mit Kommunikations-Signalen."""
        return db_manager.select(
            """
            SELECT intentionen, emotion, modus, sprach_stil, tone,
                   dimension, inhalt
            FROM langzeitgedaechtnis
            WHERE user_id = %s AND aktiv = TRUE
              AND (intentionen != '[]' OR emotion != '' OR sprach_stil != '')
            ORDER BY gewicht DESC
            LIMIT %s
            """,
            (user_id, PIXIE_CHARAKTER_LZG_LIMIT),
        )

    def _lzg_emotionen_laden(self, user_id: str) -> list[dict]:
        """Laedt LZG-Eintraege mit emotionalen Signalen."""
        return db_manager.select(
            """
            SELECT emotion, arousal, emotions_vektor,
                   dimension, inhalt, gewicht, verstaerkt_am
            FROM langzeitgedaechtnis
            WHERE user_id = %s AND aktiv = TRUE AND emotion != ''
            ORDER BY gewicht DESC
            LIMIT %s
            """,
            (user_id, PIXIE_CHARAKTER_LZG_LIMIT),
        )

    def _kzg_laden(self, user_id: str) -> list[dict]:
        """Laedt KZG-Eintraege aus Redis via SCAN."""
        eintraege: list[dict] = []

        for key in redis_client.scan_iter(match=f"kzg:{user_id}:*", count=100):
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            eintrag: dict = {
                "themen":             _hget(redis_client, key, "themen"),
                "inhalt":             _hget(redis_client, key, "inhalt"),
                "salienz":            _hget(redis_client, key, "salienz", "0"),
                "erstellt_am":        _hget(redis_client, key, "erstellt_am", "0"),
                "modus":              _hget(redis_client, key, "modus"),
                "emotion":            _hget(redis_client, key, "emotion"),
                "beziehungs_dynamik": _hget(redis_client, key, "beziehungs_dynamik"),
                "tone":               _hget(redis_client, key, "tone"),
            }
            eintraege.append(eintrag)

            if len(eintraege) >= PIXIE_CHARAKTER_KZG_LIMIT:
                break

        return eintraege

    # ─────────────────────────────────────────
    # Ergebnis speichern
    # ─────────────────────────────────────────

    @staticmethod
    def _ergebnis_speichern(user_id: str, character_id: str, ergebnis: dict) -> None:
        """Schreibt die 5 Profile per UPSERT in charakter_hash (Paar-Schema)."""
        db_manager.execute(
            """
            INSERT INTO charakter_hash
                (user_id, character_id, kern_hash, adaptive_hash, intentions_profil,
                 emotions_profil, beziehungsprofil,
                 kern_aktualisiert_am, adaptive_aktualisiert_am)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (user_id, character_id) DO UPDATE SET
                kern_hash = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.kern_hash END,
                adaptive_hash = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.adaptive_hash END,
                intentions_profil = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.intentions_profil END,
                emotions_profil = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.emotions_profil END,
                beziehungsprofil = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.beziehungsprofil END,
                kern_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.kern_aktualisiert_am END,
                adaptive_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.adaptive_aktualisiert_am END
            """,
            (
                user_id, character_id,
                ergebnis["kern"], ergebnis["adaptiv"],
                ergebnis["intentions_profil"], ergebnis["emotions_profil"],
                ergebnis["beziehungsprofil"],
                ergebnis["kern"], ergebnis["kern"],
                ergebnis["adaptiv"], ergebnis["adaptiv"],
                ergebnis["intentions_profil"], ergebnis["intentions_profil"],
                ergebnis["emotions_profil"], ergebnis["emotions_profil"],
                ergebnis["beziehungsprofil"], ergebnis["beziehungsprofil"],
                ergebnis["kern"],
                ergebnis["adaptiv"],
            ),
        )
