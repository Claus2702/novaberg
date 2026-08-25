"""Formatierungshilfen fuer AgentResult-Listen.

Gemeinsam genutzt von Planner (task_block) und Thinker (Verarbeitungs-Block).
"""
import logging

logger = logging.getLogger(__name__)


def format_success_lines(results: list) -> str:
    r"""Baut die Listen-Zeilen fuer erfolgreiche AgentResults.

    Format: '- {bereich}: {ergebnis}' pro Zeile, gejoined per \n.
    Wird vom Planner (_build_task_success) und vom Thinker
    (_build_verarbeitungs_block) genutzt, damit das Format an einer
    einzigen Stelle lebt.

    **Der Name steht ohne das Wort "Agent" davor** (20.08.2026). Der Block
    landet im Prompt der Figur, und dort war *„Agent 'notizen'"* eine dritte
    Person neben ihr: In drei echten Antworten einer Sitzung sprach sie von
    *„der Fachabteilung"*, die etwas getan habe. Der Bereichsname bleibt —
    er unterscheidet die Zeilen, wenn mehrere Dienste gelaufen sind —, die
    Instanz verschwindet.
    """
    return "\n".join(
        f"- {r.agent_name}: {r.ergebnis}" for r in results
    )
