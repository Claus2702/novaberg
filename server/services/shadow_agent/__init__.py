"""
Shadow Agent — Shared Utility-Layer.

Der alte Plugin-basierte Background-Runner wurde entfernt (PIX-CLEAN); der
Pixie-Heartbeat dispatcht heute ueber `services.pixie.*` und `agents.*`.
Block 1 Cleanup-Sprint: auch `base_task` und der einzige verbliebene Task
`nova_gedaechtnis` wurden ersatzlos entfernt — beide hatten 0 Aufrufer.
Was hier bleibt, ist ein duenner Re-Export der einzigen extern genutzten
Funktion.
"""

from services.shadow_agent.utils import shadow_queue_push

__all__ = ["shadow_queue_push"]
