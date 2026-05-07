"""
Shadow Agent — Shared Utility-Layer.

Der alte Plugin-basierte Background-Runner wurde entfernt (PIX-CLEAN); der
Pixie-Heartbeat dispatcht heute ueber `services.pixie.*` und `agents.*`.
Was hier bleibt, ist ein duenner Re-Export der einzigen extern genutzten
Funktion sowie die Submodule `utils` und `base_task` (letztere wird vom
verbleibenden Task `nova_gedaechtnis` gebraucht).
"""

from services.shadow_agent.utils import shadow_queue_push

__all__ = ["shadow_queue_push"]
