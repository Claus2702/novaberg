"""ZielDecayAgent — Motivations-Decay fuer mittelfristige Ziele.

Exponentieller Verfall basierend auf aktualisiert_am.
Langfristige Ziele sind ausgenommen. Deaktivierung unter Schwelle.

Kein LLM-Call. Reine Mathematik. Analog zum DecayAgent (LZG).
"""

import logging
import math
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ZIEL_DECAY_AKTIV,
    ZIEL_MITTELFRISTIG_DECAY_TAGE,
    PIXIE_DECAY_PRIORITAET,
    PIXIE_DECAY_INTERVALL_SEKUNDEN,
    POSTGRES_URL,
)
from memory.ziele import ziele_aktive_laden, ziel_motivation_anpassen, ziel_deaktivieren

logger = logging.getLogger("ki_server.agents.ziel_decay")

# Motivation unter diesem Wert → Ziel deaktivieren
ZIEL_DEAKTIVIERUNGS_SCHWELLE: float = 0.15


class ZielDecayAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "ziel_decay"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["ziel_decay"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    def periodic_task(self) -> PeriodicTask | None:
        """Registriert den taeglichen Lauf — oder gar nicht, wenn stillgelegt.

        Rueckgabe None => kein Zeitplan-Eintrag, der Agent taucht nicht als
        Heartbeat-Kandidat auf. Das ist das erste von zwei Gates (zweites in
        invoke). Muster wie synapsen_decay.
        """
        if not ZIEL_DECAY_AKTIV:
            logger.info(
                "ziel_decay stillgelegt (ZIEL_DECAY_AKTIV=false) — kein periodisches "
                "Scheduling, bis ZIEL-DECAY-FORMEL-KUMULATIV repariert ist"
            )
            return None

        return PeriodicTask(
            name="ziel_decay",
            priority=PIXIE_DECAY_PRIORITAET,
            interval=PIXIE_DECAY_INTERVALL_SEKUNDEN,
            description="Ziel-Decay: Mittelfristige Ziele mit verfallener Motivation deaktivieren",
        )

    def build_graph(self):
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Berechnet Motivations-Decay und deaktiviert verblasste Ziele.

        Zweites Gate: Auch ein direkt aufgerufener Lauf schreibt nichts, solange
        ZIEL_DECAY_AKTIV false ist. Ein Gate allein im Scheduling reichte nicht —
        der Router loest Agenten inzwischen auch ueber Namensgleichheit auf.
        """

        # ── Eingabe-Validierung ─────────────────────
        if not ZIEL_DECAY_AKTIV:
            logger.info(
                "ziel_decay invoke uebersprungen (ZIEL_DECAY_AKTIV=false) — "
                "die Formel schreibt sonst kumulativ verfallene Motivation zurueck"
            )
            state["ergebnis"] = {"aktiv": False, "deaktiviert": 0, "geprueft": 0}
            state["status"] = "abgeschlossen"
            return state

        ziele: list[dict] = ziele_aktive_laden(POSTGRES_URL, user_id="nova")

        if not ziele:
            logger.debug("ZielDecay: Keine aktiven Ziele")
            state["ergebnis"] = {"deaktiviert": 0, "geprueft": 0}
            state["status"] = "abgeschlossen"
            return state

        jetzt: datetime = datetime.now(timezone.utc)
        decay_rate: float = math.log(2) / ZIEL_MITTELFRISTIG_DECAY_TAGE

        deaktiviert: int = 0
        geprueft:    int = 0

        for ziel in ziele:
            # Langfristige Ziele sind vom Decay ausgenommen.
            if ziel["ziel_typ"] == "langfristig":
                continue

            geprueft += 1

            # Tage seit letzter Aktualisierung.
            aktualisiert: datetime = ziel.get("erstellt_am", jetzt)
            if aktualisiert.tzinfo is None:
                aktualisiert = aktualisiert.replace(tzinfo=timezone.utc)

            tage: float = max(0.0, (jetzt - aktualisiert).total_seconds() / 86400.0)

            # Exponentieller Verfall: motivation_neu = motivation × e^(-rate × tage)
            decay_faktor:   float = math.exp(-decay_rate * tage)
            motivation_alt: float = ziel["motivation"]
            motivation_neu: float = round(motivation_alt * decay_faktor, 3)

            if motivation_neu < ZIEL_DEAKTIVIERUNGS_SCHWELLE:
                ziel_deaktivieren(POSTGRES_URL, ziel["id"])
                deaktiviert += 1
                logger.info(
                    f"ZielDecay: id={ziel['id']} deaktiviert — "
                    f"motivation={motivation_alt:.2f} → {motivation_neu:.3f} "
                    f"(nach {tage:.0f} Tagen)"
                )
            elif abs(motivation_neu - motivation_alt) > 0.01:
                ziel_motivation_anpassen(POSTGRES_URL, ziel["id"], motivation_neu)
                logger.debug(
                    f"ZielDecay: id={ziel['id']} — "
                    f"motivation={motivation_alt:.2f} → {motivation_neu:.3f} "
                    f"({tage:.0f} Tage, Halbwert={ZIEL_MITTELFRISTIG_DECAY_TAGE}d)"
                )

        if deaktiviert:
            logger.info(f"ZielDecay: {deaktiviert} von {geprueft} mittelfristigen Zielen deaktiviert")
        else:
            logger.info(f"ZielDecay: Alle {geprueft} mittelfristigen Ziele noch aktiv")

        state["ergebnis"] = {"deaktiviert": deaktiviert, "geprueft": geprueft}
        state["status"] = "abgeschlossen"
        return state
