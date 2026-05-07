"""Formatierungshilfen fuer AgentResult-Listen.

Gemeinsam genutzt von Planner (task_block) und Thinker (Verarbeitungs-Block).
"""
import logging

logger = logging.getLogger(__name__)


def format_success_lines(results: list) -> str:
    """Baut die Listen-Zeilen fuer erfolgreiche AgentResults.

    Format: '- Agent {name}: {ergebnis}' pro Zeile, gejoined per \\n.
    Wird vom Planner (_build_task_success) und vom Thinker
    (_build_verarbeitungs_block) genutzt, damit das Format an einer
    einzigen Stelle lebt.
    """
    return "\n".join(
        f"- Agent '{r.agent_name}': {r.ergebnis}" for r in results
    )
