"""
CharakterIdentitaet-Manager — Vom Nutzer definierte Grundidentitaet von Nova.

Stellt Router-Prompt fuer die Erkennung von Identitaetszuweisungen bereit.
Kein execute() noetig — CRUD laeuft ueber den CharakterIdentitaetAgent.
"""

import logging

import redis

from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins.charakter_identitaet")


class CharakterIdentitaetManager(BaseManager):

    @property
    def ziel(self) -> str:
        return "charakter_identitaet"

    @property
    def immer_aktiv(self) -> bool:
        return False

    @property
    def router_intents(self) -> list[str]:
        return []

    @property
    def router_prompt(self) -> str:
        return """
CHARAKTER-IDENTITAET-ERKENNUNG:
Setze management_action = "agent" wenn:
1. Der User Nova eine Persoenlichkeit oder Identitaet zuweist:
   "Du bist ab jetzt...", "Sei mehr...", "Ich moechte dass du..."
   "Stell dir vor du waerst...", "Dein Charakter ist..."
2. Der User den Charakter aendern oder zuruecksetzen will:
   "Sei wieder normal", "Vergiss den Charakter", "Weniger frech"
3. Der User fragt, welchen Charakter Nova hat:
   "Was bist du fuer ein Typ?", "Wie wuerdest du dich beschreiben?"

NICHT triggern bei:
- Emotionalen Ausdruecken ("Du bist toll!") — das ist Feedback, kein Charakter
- Einmaligen Rollenspielen ("Antworte mal als Pirat") — das ist kein dauerhafter Charakter

Bei Erkennung:
  management_action = "agent"
  management_target = "charakter_identitaet"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Du bist ab jetzt ein freches Maedel vom Land"
- "Sei mehr wie ein Kumpel und weniger foermlich"
- "Vergiss den Charakter, sei wieder normal"
- "Was bist du eigentlich fuer ein Typ?"
"""

    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> int:
        """Kein execute noetig — CRUD laeuft ueber den Agent."""
        return 0
