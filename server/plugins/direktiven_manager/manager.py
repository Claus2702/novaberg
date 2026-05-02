"""
Direktiven-Manager — Absolute Verhaltensanweisungen des Nutzers an Nova.

Stellt Router-Prompt fuer die Erkennung von Direktiven bereit.
Kein execute() noetig — CRUD laeuft ueber den DirektivenAgent.
"""

import logging

import redis

from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins.direktiven")


class DirektivenManager(BaseManager):

    @property
    def ziel(self) -> str:
        return "direktiven"

    @property
    def immer_aktiv(self) -> bool:
        return False

    @property
    def router_intents(self) -> list[str]:
        return []

    @property
    def router_prompt(self) -> str:
        return """
DIREKTIVEN-ERKENNUNG:
Setze management_action = "agent" wenn:
1. Der User eine absolute Verhaltensregel aufstellt:
   "Sprich nie von...", "Sag das nie mehr!", "Erwaehne nie wieder..."
   "Du hast mich immer zu siezen!", "Nenn mich immer..."
   "Mach das ab jetzt immer so", "Hoer auf damit"
2. Der User eine bestehende Regel aendern oder aufheben will:
   "Du darfst wieder ueber X reden", "Das Siezen ist nicht mehr noetig"
   "Vergiss die Regel mit..."
3. Der User fragt, welche Regeln gelten:
   "Welche Regeln hast du?", "Was darfst du nicht?"

Erkennungsmuster:
- Imperative mit "nie", "immer", "ab jetzt", "ab sofort"
- Verbote: "nicht mehr", "hoer auf", "lass das"
- Der Gespraechskontext ist WICHTIG: "Sag das nie mehr!" braucht den Bezug

Bei Erkennung:
  management_action = "agent"
  management_target = "direktiven"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Sprich nie wieder von Milch!"
- "Sag das nie mehr!"
- "Du hast mich ab jetzt immer zu siezen"
- "Welche Regeln hast du?"
- "Du darfst wieder ueber Milch reden"
"""

    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
        embed_client=None,
        embed_model:  str = "",
    ) -> int:
        """Kein execute noetig — CRUD laeuft ueber den Agent."""
        return 0
