"""WiedervorlageAgent — Prueft faellige Wiedervorlagen und erstellt Erinnerungen.

Scannt 4 Tabellen (Entitaeten, Fakten, Timeline, Notizen),
formuliert per LLM eine Erinnerung und legt sie auf den Shadow-Stack.
Migriert aus: services/shadow_agent/tasks/wiedervorlage.py
"""

import logging
from datetime import datetime, timedelta

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ASSISTANT_NAME,
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    POSTGRES_URL,
    PIXIE_WIEDERVORLAGE_PRIORITAET,
    PIXIE_WIEDERVORLAGE_INTERVALL_SEKUNDEN,
    PIXIE_WIEDERVORLAGE_SNOOZE_TAGE,
    redis_client,
    get_node_config,
)
from services.model_services import model_service, BackgroundRequest
from services.pixie.stack import stack_push
from memory.repositories import (
    EntitaetenRepository,
    FaktenRepository,
    TimelineRepository,
    NotizenRepository,
)

logger = logging.getLogger("ki_server.agents.wiedervorlage")

BUTLER_SYSTEM_PROMPT: str = f"""Du bist {ASSISTANT_NAME} — nicht im Gespräch mit einem Menschen,
sondern in deinem eigenen Denkprozess. Du bereitest eine kurze Erinnerung vor,
die du deinem Benutzer schicken möchtest.

Regeln:
- Formuliere eine freundliche, kurze Erinnerung (2-3 Sätze)
- Nenne den konkreten Inhalt — nicht nur "da war noch was"
- Sei hilfreich, nicht nervig
- Antworte auf Deutsch"""

TYP_LABEL: dict[str, str] = {
    "entitaeten": "eine Person/Sache",
    "fakten":     "ein Fakt",
    "timeline":   "ein Termin/Ereignis",
    "notizen":    "eine Notiz",
}


class WiedervorlageAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "wiedervorlage"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["wiedervorlage"]

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
            name="wiedervorlage",
            priority=PIXIE_WIEDERVORLAGE_PRIORITAET,
            interval=PIXIE_WIEDERVORLAGE_INTERVALL_SEKUNDEN,
            description="Prueft faellige Wiedervorlagen, erstellt Erinnerungen",
        )

    def build_graph(self):
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Prueft faellige Wiedervorlagen und erstellt Erinnerungen."""

        # Periodischer Pfad: dispatch.py setzt kontext={}, daher greift hier
        # strukturell der DEFAULT_USER_ID-Fallback. Multi-User-Wiedervorlage
        # braucht Scheduler-Umbau (Aufgaben pro User) — Backlog
        # WIEDERVORLAGE-MULTI-USER.
        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID

        # ── Faellige sammeln ─────────────────
        faellige: list[dict] = self._faellige_sammeln(user_id)

        if not faellige:
            logger.debug(f"WiedervorlageAgent: Keine faelligen Wiedervorlagen fuer {user_id}")
            state["ergebnis"] = {"verarbeitet": 0}
            state["status"] = "abgeschlossen"
            return state

        logger.info(f"WiedervorlageAgent: {len(faellige)} faellige Wiedervorlagen fuer {user_id}")

        verarbeitet: int = 0

        for eintrag in faellige:
            # ── LLM-Erinnerung formulieren ───
            nachfrage: str = self._nachfrage_formulieren(eintrag)

            # ── Auf Stack schreiben ──────────
            if nachfrage:
                try:
                    stack_push(
                        redis_client=redis_client,
                        user_id=user_id,
                        aufgabe="wiedervorlage",
                        thema=eintrag["titel"],
                        inhalt=nachfrage,
                    )
                except Exception as ex:
                    logger.error(f"WiedervorlageAgent: Stack-Push fehlgeschlagen — {ex}")

            # ── Wiedervorlage verschieben ────
            self._wiedervorlage_verschieben(eintrag)
            verarbeitet += 1

        logger.info(f"WiedervorlageAgent: {verarbeitet} Wiedervorlagen verarbeitet")

        state["ergebnis"] = {"verarbeitet": verarbeitet}
        state["status"] = "abgeschlossen"
        return state

    # ─────────────────────────────────────────
    # Faellige Wiedervorlagen aus allen Tabellen
    # ─────────────────────────────────────────

    @staticmethod
    def _faellige_sammeln(user_id: str) -> list[dict]:
        """Sammelt faellige Wiedervorlagen aus Entitaeten, Fakten, Timeline, Notizen."""

        faellige: list[dict] = []

        # Entitaeten
        try:
            for row in EntitaetenRepository.find_wiedervorlage_faellig(POSTGRES_URL, user_id):
                faellige.append({
                    "tabelle": "entitaeten",
                    "id":      row["id"],
                    "titel":   row.get("name", ""),
                    "details": row.get("zusammenfassung", "") or row.get("name", ""),
                })
        except Exception as fehler:
            logger.warning(f"WiedervorlageAgent: Entitaeten-Wiedervorlage fehlgeschlagen — {fehler}")

        # Fakten
        try:
            for row in FaktenRepository.find_wiedervorlage_faellig(POSTGRES_URL, user_id):
                faellige.append({
                    "tabelle": "fakten",
                    "id":      row["id"],
                    "titel":   row.get("attribut", ""),
                    "details": row.get("fakt_text", "") or row.get("attribut", ""),
                })
        except Exception as fehler:
            logger.warning(f"WiedervorlageAgent: Fakten-Wiedervorlage fehlgeschlagen — {fehler}")

        # Timeline
        try:
            for row in TimelineRepository.find_wiedervorlage_faellig(POSTGRES_URL, user_id):
                faellige.append({
                    "tabelle": "timeline",
                    "id":      row["id"],
                    "titel":   row.get("titel", ""),
                    "details": row.get("beschreibung", "") or row.get("titel", ""),
                })
        except Exception as fehler:
            logger.warning(f"WiedervorlageAgent: Timeline-Wiedervorlage fehlgeschlagen — {fehler}")

        # Notizen
        try:
            for row in NotizenRepository.find_wiedervorlage_faellig(POSTGRES_URL, user_id):
                faellige.append({
                    "tabelle": "notizen",
                    "id":      row["id"],
                    "titel":   row.get("name", ""),
                    "details": row.get("zusammenfassung", "") or row.get("name", ""),
                })
        except Exception as fehler:
            logger.warning(f"WiedervorlageAgent: Notizen-Wiedervorlage fehlgeschlagen — {fehler}")

        return faellige

    # ─────────────────────────────────────────
    # Nachfrage per LLM formulieren
    # ─────────────────────────────────────────

    @staticmethod
    def _nachfrage_formulieren(eintrag: dict) -> str:
        """Laesst das CPU-Modell eine kurze Erinnerung formulieren."""

        tabelle: str = eintrag["tabelle"]
        titel:   str = eintrag["titel"]
        details: str = eintrag["details"][:300]

        prompt: str = f"""Folgendes wurde zur Wiedervorlage markiert:

Typ: {TYP_LABEL.get(tabelle, tabelle)}
Titel: {titel}
Details: {details}

Formuliere eine kurze, freundliche Erinnerung für den Benutzer.
Nenne den konkreten Inhalt. Formuliere NUR die Erinnerung, kein weiterer Text."""

        try:
            node_cfg = get_node_config("wiedervorlage")
            # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
            # Sync invoke via Pixie/CharacterGraph asyncio.to_thread →
            # submit_sync. modus="sprache" — CPU-Sprachmodell, passend zur
            # Fliesstext-Erinnerung an den User.
            response = model_service.background.submit_sync(BackgroundRequest(
                messages          = [{"role": "user", "content": prompt}],
                modus             = "sprache",
                system            = BUTLER_SYSTEM_PROMPT,
                temperature       = node_cfg.get("temperature", 0.2),
                max_output_tokens = node_cfg.get("max_output_tokens"),
                caller            = "pixie/wiedervorlage",
            ))

            return response.text.strip()

        except Exception as fehler:
            logger.error(f"WiedervorlageAgent: LLM-Formulierung fehlgeschlagen — {fehler}")
            return ""

    # ─────────────────────────────────────────
    # Wiedervorlage verschieben (Snooze)
    # ─────────────────────────────────────────

    @staticmethod
    def _wiedervorlage_verschieben(eintrag: dict) -> None:
        """Verschiebt die Wiedervorlage um SNOOZE_TAGE Tage in die Zukunft."""

        tabelle:  str = eintrag["tabelle"]
        entry_id: int = eintrag["id"]
        neues_datum: datetime = datetime.now() + timedelta(days=PIXIE_WIEDERVORLAGE_SNOOZE_TAGE)

        try:
            if tabelle == "entitaeten":
                EntitaetenRepository.set_wiedervorlage(POSTGRES_URL, entry_id, neues_datum)
            elif tabelle == "fakten":
                FaktenRepository.set_wiedervorlage(POSTGRES_URL, entry_id, neues_datum)
            elif tabelle == "timeline":
                TimelineRepository.set_wiedervorlage(POSTGRES_URL, entry_id, neues_datum)
            elif tabelle == "notizen":
                NotizenRepository.set_wiedervorlage(POSTGRES_URL, entry_id, neues_datum)

            logger.debug(
                f"WiedervorlageAgent: Wiedervorlage {tabelle}#{entry_id} "
                f"verschoben auf {neues_datum.strftime('%Y-%m-%d')}"
            )

        except Exception as fehler:
            logger.warning(f"WiedervorlageAgent: Wiedervorlage verschieben fehlgeschlagen — {fehler}")
