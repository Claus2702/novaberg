"""DecayAgent — Ebbinghaus-Decay fuer LZG-Eintraege.

Berechnet das effektive Gewicht aller aktiven LZG-Eintraege
und deaktiviert Eintraege unter dem Schwellwert.

Kein LLM-Call. Reine Mathematik. Beide User (kein user_id-Filter).
Migriert aus: services/shadow_agent/tasks/lzg_decay.py
"""

import logging

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    EBBINGHAUS_MIN_GEWICHT,
    PIXIE_DECAY_PRIORITAET,
    PIXIE_DECAY_INTERVALL_SEKUNDEN,
)
from memory.lzg import effektives_gewicht_berechnen
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.decay")


class DecayAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "decay"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["lzg_decay"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    def periodic_task(self) -> PeriodicTask | None:
        return PeriodicTask(
            name="decay",
            priority=PIXIE_DECAY_PRIORITAET,
            interval=PIXIE_DECAY_INTERVALL_SEKUNDEN,
            description="Ebbinghaus-Decay: Verblasste LZG-Eintraege deaktivieren",
        )

    def build_graph(self):
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Berechnet effektives Gewicht und deaktiviert verblasste Eintraege."""

        rows: list[dict] = db_manager.select(
            "SELECT id, gewicht, verstaerkt_am FROM langzeitgedaechtnis WHERE aktiv = TRUE"
        )

        inaktiv_ids: list[int] = []

        for row in rows:
            eff: float = effektives_gewicht_berechnen(row["gewicht"], row["verstaerkt_am"])
            if eff < EBBINGHAUS_MIN_GEWICHT:
                inaktiv_ids.append(row["id"])

        if inaktiv_ids:
            db_manager.execute(
                "UPDATE langzeitgedaechtnis SET aktiv = FALSE WHERE id = ANY(%s)",
                (inaktiv_ids,),
            )
            logger.info(
                f"LZG-Decay: {len(inaktiv_ids)} Eintraege inaktiv markiert "
                f"(Schwellwert: {EBBINGHAUS_MIN_GEWICHT})"
            )
        else:
            logger.info(f"LZG-Decay: Alle {len(rows)} Eintraege noch aktiv.")

        state["ergebnis"] = {"deaktiviert": len(inaktiv_ids), "geprueft": len(rows)}
        state["status"] = "abgeschlossen"
        return state
