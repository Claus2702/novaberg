"""Task: Butler — prüft fällige Wiedervorlagen und schreibt Erinnerungen auf den Stack."""

import logging
import threading
from datetime import datetime, timedelta

import redis

from config                          import ASSISTANT_NAME, get_node_config
from services.shadow_agent.base_task import BaseTask
from services.shadow_agent.utils     import stack_push
from services.llm_provider           import get_background_provider
from memory.repositories             import (
    EntitaetenRepository,
    FaktenRepository,
    TimelineRepository,
    NotizenRepository,
)

logger = logging.getLogger("ki_server.shadow")

BUTLER_SYSTEM_PROMPT: str = f"""Du bist {ASSISTANT_NAME} — nicht im Gespräch mit einem Menschen,
sondern in deinem eigenen Denkprozess. Du bereitest eine kurze Erinnerung vor,
die du deinem Benutzer schicken möchtest.

Regeln:
- Formuliere eine freundliche, kurze Erinnerung (2-3 Sätze)
- Nenne den konkreten Inhalt — nicht nur "da war noch was"
- Sei hilfreich, nicht nervig
- Antworte auf Deutsch"""

SNOOZE_TAGE: int = 7


class WiedervorlageTask(BaseTask):
    """Butler-Task: Prüft fällige Wiedervorlagen über alle Tabellen."""

    TASK_NAME    = "wiedervorlage"
    BESCHREIBUNG = "Prüft fällige Wiedervorlagen und erstellt Erinnerungen"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = True
    PRIORITAET   = 20
    INTENTIONEN  = []
    EMOTION_BLACKLIST = ["stress"]

    def execute(
        self,
        auftrag:        dict,
        redis_client:   redis.Redis,
        embed_client,
        embed_model:    str,
        postgres_url:   str,
        user_id:        str,
        shutdown_event: threading.Event | None = None,
    ) -> dict | None:

        # Alle User-IDs ermitteln (aus Redis-Keys oder übergebener user_id)
        user_ids: list[str] = self._user_ids_ermitteln(redis_client, user_id)

        gesamt: int = 0

        for uid in user_ids:
            if shutdown_event and shutdown_event.is_set():
                logger.info("Butler: Shutdown — breche ab")
                return None

            faellige: list[dict] = self._faellige_sammeln(postgres_url, uid)

            if not faellige:
                continue

            logger.info(f"Butler: {len(faellige)} fällige Wiedervorlagen für '{uid}'")

            for eintrag in faellige:
                if shutdown_event and shutdown_event.is_set():
                    return None

                nachfrage: str = self._nachfrage_formulieren(eintrag)

                if nachfrage:
                    self._auf_stack_schreiben(
                        redis_client, embed_client, embed_model,
                        uid, eintrag, nachfrage,
                    )

                self._wiedervorlage_verschieben(postgres_url, eintrag)
                gesamt += 1

        if gesamt:
            logger.info(f"Butler: {gesamt} Wiedervorlagen verarbeitet")

        return None  # Ergebnisse gehen direkt auf den Stack, nicht über den Runner

    # ─────────────────────────────────────────────
    # User-IDs ermitteln
    # ─────────────────────────────────────────────
    @staticmethod
    def _user_ids_ermitteln(
        redis_client: redis.Redis,
        user_id:      str,
    ) -> list[str]:
        """Gibt eine Liste von User-IDs zurück die geprüft werden sollen."""

        if user_id:
            return [user_id]

        # Fallback: Alle bekannten User aus shadow_stack-Keys
        keys: list = redis_client.keys("shadow_stack:*")
        ids: set[str] = set()

        for key in keys:
            key_str: str = key if isinstance(key, str) else key.decode()
            parts = key_str.split(":")
            if len(parts) >= 2:
                ids.add(parts[1])

        return list(ids)

    # ─────────────────────────────────────────────
    # Fällige Wiedervorlagen aus allen Tabellen
    # ─────────────────────────────────────────────
    @staticmethod
    def _faellige_sammeln(
        postgres_url: str,
        user_id:      str,
    ) -> list[dict]:
        """Sammelt fällige Wiedervorlagen aus Entitäten, Fakten, Timeline, Notizen."""

        faellige: list[dict] = []

        # Entitäten
        try:
            for row in EntitaetenRepository.find_wiedervorlage_faellig(postgres_url, user_id):
                faellige.append({
                    "tabelle":  "entitaeten",
                    "id":       row["id"],
                    "titel":    row.get("name", ""),
                    "details":  row.get("zusammenfassung", "") or row.get("name", ""),
                })
        except Exception as fehler:
            logger.warning(f"Butler: Entitäten-Wiedervorlage fehlgeschlagen — {fehler}")

        # Fakten
        try:
            for row in FaktenRepository.find_wiedervorlage_faellig(postgres_url, user_id):
                faellige.append({
                    "tabelle":  "fakten",
                    "id":       row["id"],
                    "titel":    row.get("attribut", ""),
                    "details":  row.get("fakt_text", "") or row.get("attribut", ""),
                })
        except Exception as fehler:
            logger.warning(f"Butler: Fakten-Wiedervorlage fehlgeschlagen — {fehler}")

        # Timeline
        try:
            for row in TimelineRepository.find_wiedervorlage_faellig(postgres_url, user_id):
                faellige.append({
                    "tabelle":  "timeline",
                    "id":       row["id"],
                    "titel":    row.get("titel", ""),
                    "details":  row.get("beschreibung", "") or row.get("titel", ""),
                })
        except Exception as fehler:
            logger.warning(f"Butler: Timeline-Wiedervorlage fehlgeschlagen — {fehler}")

        # Notizen
        try:
            for row in NotizenRepository.find_wiedervorlage_faellig(postgres_url, user_id):
                faellige.append({
                    "tabelle":  "notizen",
                    "id":       row["id"],
                    "titel":    row.get("name", ""),
                    "details":  row.get("zusammenfassung", "") or row.get("name", ""),
                })
        except Exception as fehler:
            logger.warning(f"Butler: Notizen-Wiedervorlage fehlgeschlagen — {fehler}")

        return faellige

    # ─────────────────────────────────────────────
    # Nachfrage per LLM formulieren
    # ─────────────────────────────────────────────
    @staticmethod
    def _nachfrage_formulieren(eintrag: dict) -> str:
        """Lässt das CPU-Modell eine kurze Erinnerung formulieren."""

        tabelle: str = eintrag["tabelle"]
        titel:   str = eintrag["titel"]
        details: str = eintrag["details"][:300]

        typ_label: dict[str, str] = {
            "entitaeten": "eine Person/Sache",
            "fakten":     "ein Fakt",
            "timeline":   "ein Termin/Ereignis",
            "notizen":    "eine Notiz",
        }

        prompt: str = f"""Folgendes wurde zur Wiedervorlage markiert:

Typ: {typ_label.get(tabelle, tabelle)}
Titel: {titel}
Details: {details}

Formuliere eine kurze, freundliche Erinnerung für den Benutzer.
Nenne den konkreten Inhalt. Formuliere NUR die Erinnerung, kein weiterer Text."""

        try:
            node_cfg = get_node_config("wiedervorlage")
            provider = get_background_provider()
            antwort  = provider.chat(
                messages = [
                    {"role": "user", "content": prompt},
                ],
                system            = BUTLER_SYSTEM_PROMPT,
                temperature       = node_cfg.get("temperature", 0.2),
                max_output_tokens = node_cfg.get("max_output_tokens"),
                caller            = "pixie/wiedervorlage",
            )

            return antwort.content.strip()

        except Exception as fehler:
            logger.error(f"Butler: LLM-Formulierung fehlgeschlagen — {fehler}")
            return ""

    # ─────────────────────────────────────────────
    # Ergebnis auf den Shadow-Stack schreiben
    # ─────────────────────────────────────────────
    @staticmethod
    def _auf_stack_schreiben(
        redis_client:  redis.Redis,
        embed_client,
        embed_model:   str,
        user_id:       str,
        eintrag:       dict,
        nachfrage:     str,
    ) -> None:
        """Schreibt die formulierte Erinnerung auf den Shadow-Stack."""

        stack_push(
            redis_client  = redis_client,
            user_id       = user_id,
            aufgabe       = "wiedervorlage",
            thema         = eintrag["titel"],
            inhalt        = nachfrage,
            embed_client  = embed_client,
            embed_model   = embed_model,
        )

    # ─────────────────────────────────────────────
    # Wiedervorlage verschieben (Snooze +7 Tage)
    # ─────────────────────────────────────────────
    @staticmethod
    def _wiedervorlage_verschieben(
        postgres_url: str,
        eintrag:      dict,
    ) -> None:
        """Verschiebt die Wiedervorlage um SNOOZE_TAGE Tage in die Zukunft."""

        tabelle:  str = eintrag["tabelle"]
        entry_id: int = eintrag["id"]
        neues_datum: datetime = datetime.now() + timedelta(days=SNOOZE_TAGE)

        try:
            if tabelle == "entitaeten":
                EntitaetenRepository.set_wiedervorlage(postgres_url, entry_id, neues_datum)
            elif tabelle == "fakten":
                FaktenRepository.set_wiedervorlage(postgres_url, entry_id, neues_datum)
            elif tabelle == "timeline":
                TimelineRepository.set_wiedervorlage(postgres_url, entry_id, neues_datum)
            elif tabelle == "notizen":
                NotizenRepository.set_wiedervorlage(postgres_url, entry_id, neues_datum)

            logger.debug(
                f"Butler: Wiedervorlage {tabelle}#{entry_id} "
                f"verschoben auf {neues_datum.strftime('%Y-%m-%d')}"
            )

        except Exception as fehler:
            logger.warning(f"Butler: Wiedervorlage verschieben fehlgeschlagen — {fehler}")
