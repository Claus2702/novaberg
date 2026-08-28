"""ZielDecayAgent — Motivations-Verfall fuer mittelfristige Ziele.

Exponentieller Verfall aus dem Anker `motivation_basis` und dem Zeitpunkt
`motivation_basis_am`. `motivation` ist das materialisierte Feld, das jede
Abfrage liest — einmal rechnen, hundertmal lesen, wie `gewicht_decay` im LZG.

Der Agent traegt keine Formel und keine Schleife: Die Fachlogik liegt in
memory/ziele.py, hier steht nur der Ausloeser plus Audit und Forensik.

Kein LLM-Call. Reine Mathematik. Analog zum SynapsenDecayAgent.
"""

import logging
import uuid

from agents.base import AgentState, BaseAgent, PeriodicTask
from config import (
    DEFAULT_USER_ID,
    PIXIE_DECAY_INTERVALL_SEKUNDEN,
    PIXIE_DECAY_PRIORITAET,
    POSTGRES_URL,
    ZIEL_DECAY_AKTIV,
    ZIEL_KURZFRISTIG_DECAY_STUNDEN,
    ZIEL_MITTELFRISTIG_DECAY_TAGE,
)
from memory import pipeline_log
from memory.ziele import ziel_decay_lauf
from tools.db_manager import db_manager

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
    def lastart(self) -> str:
        """Die CPU-Spur. Reine Rechnung ueber Bestandswerte, kein Modellaufruf."""
        return "cpu"

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


    @staticmethod
    def _audit_log(user_id: str, status: str, ergebnis: str) -> None:
        """Schreibt einen hintergrund_log-Eintrag (Audit-Pflicht).

        Failsafe: Bei DB-Fehler nur logger.critical, kein Retry — sonst droht
        Endlos-Rekursion bei kaputter Audit-Senke. Muster wie synapsen_decay.
        """
        try:
            db_manager.execute(
                """
                INSERT INTO hintergrund_log
                    (user_id, aufgabe, status, ergebnis, verarbeitet_am)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, "ziel_decay", status, ergebnis),
            )
        except Exception as ex:
            logger.critical(
                f"hintergrund_log-INSERT fehlgeschlagen: {ex} "
                f"(verlorener Audit-Eintrag: ziel_decay/{status}/{ergebnis[:100]})"
            )

    @staticmethod
    def _log_forensik(run_id: str, inhalt: dict) -> None:
        """Schreibt eine pipeline_log-Zeile (best-effort).

        Paar-los wie beim synapsen_decay: Ein Wartungslauf gehoert zu keinem
        Turn und zu keinem Paar. Ein Forensik-Schreibfehler darf den Lauf nicht
        killen — deshalb gekapselt mit logger.warning.
        """
        try:
            pipeline_log.log_berechnung(
                turn_id=run_id, node="ziel_decay", quelle="pixie", inhalt=inhalt
            )
        except Exception as ex:
            logger.warning(
                f"pipeline_log-Forensik nicht geschrieben ({inhalt.get('phase', '?')}): {ex}"
            )

    def invoke(self, state: AgentState) -> AgentState:
        """Loest den Verfallslauf ueber die mittel- und kurzfristigen Ziele aus.

        Ablauf (EVA):
          Eingabe      — Feature-Gate pruefen.
          Verarbeitung — ziel_decay_lauf() materialisiert `motivation` aus Anker
                         und Zeit und deaktiviert, was unter die Schwelle faellt.
          Ausgabe      — Ergebnis in state["ergebnis"], Status und Audit setzen.

        Zweites Gate: Auch ein direkt aufgerufener Lauf schreibt nichts, solange
        ZIEL_DECAY_AKTIV false ist. Ein Gate allein im Scheduling reichte nicht —
        der Router loest Agenten inzwischen auch ueber Namensgleichheit auf.

        Der Lauf ist idempotent. Wird er zweimal hintereinander ausgefuehrt,
        steht danach derselbe Wert wie nach dem ersten Mal.
        """
        # --- Eingabe (EVA): Feature-Gate ---
        if not ZIEL_DECAY_AKTIV:
            logger.info(
                "ziel_decay invoke uebersprungen (ZIEL_DECAY_AKTIV=false)"
            )
            state["ergebnis"] = {"aktiv": False, "verarbeitet": 0, "deaktiviert": 0}
            state["status"] = "abgeschlossen"
            return state

        run_id: str = f"ziel_decay:{uuid.uuid4()}"
        logger.info(f"Ziel-Decay-Lauf startet (run_id={run_id})")
        self._audit_log(DEFAULT_USER_ID, "gestartet", f"run_id={run_id}")
        self._log_forensik(run_id, {"phase": "start"})

        # --- Verarbeitung ---
        # Zwei Typen, zwei Halbwertszeiten (Scheibe 2 des Lage-Konzepts,
        # 28.08.2026): mittelfristig in Tagen, kurzfristig in Stunden. Ein
        # Lauf je Typ, weil die Allowlist im Lauf genau einen Typ nimmt.
        laeufe: list[dict] = [
            ziel_decay_lauf(
                POSTGRES_URL,
                ziel_typ                = "mittelfristig",
                deaktivierungs_schwelle = ZIEL_DEAKTIVIERUNGS_SCHWELLE,
                halbwertszeit_tage      = ZIEL_MITTELFRISTIG_DECAY_TAGE,
            ),
            ziel_decay_lauf(
                POSTGRES_URL,
                ziel_typ                = "kurzfristig",
                deaktivierungs_schwelle = ZIEL_DEAKTIVIERUNGS_SCHWELLE,
                halbwertszeit_tage      = ZIEL_KURZFRISTIG_DECAY_STUNDEN / 24.0,
            ),
        ]
        ergebnis: dict = {
            "verarbeitet": sum(l["verarbeitet"] for l in laeufe),
            "deaktiviert": sum(l["deaktiviert"] for l in laeufe),
            "ohne_anker":  sum(l["ohne_anker"] for l in laeufe),
            "error":       " | ".join(l["error"] for l in laeufe if l["error"]) or None,
        }

        # --- Ausgabe (EVA) ---
        state["ergebnis"] = ergebnis
        ende: dict = {
            "phase":       "ende",
            "verarbeitet": ergebnis["verarbeitet"],
            "deaktiviert": ergebnis["deaktiviert"],
            "ohne_anker":  ergebnis["ohne_anker"],
        }

        if ergebnis["error"]:
            state["status"] = "fehler"
            state["fehler"] = ergebnis["error"]
            ende["status"]  = "fehler"
            ende["fehler"]  = ergebnis["error"]
            self._log_forensik(run_id, ende)
            self._audit_log(DEFAULT_USER_ID, "fehler", ergebnis["error"])
            logger.error(f"Ziel-Decay-Lauf mit Fehler beendet (run_id={run_id})")
            return state

        state["status"] = "abgeschlossen"
        ende["status"]  = "abgeschlossen"
        self._log_forensik(run_id, ende)
        self._audit_log(
            DEFAULT_USER_ID,
            "erledigt",
            f"{ergebnis['verarbeitet']} verarbeitet, "
            f"{ergebnis['deaktiviert']} deaktiviert, "
            f"{ergebnis['ohne_anker']} ohne Anker",
        )
        logger.info(f"Ziel-Decay-Lauf abgeschlossen (run_id={run_id})")
        return state
