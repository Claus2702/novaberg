"""Der Aushang des Wurzeln-Dienstes — sein Zettel am schwarzen Brett.

Spezifikation: docs/novaberg-agent-dateien_k.md §8.2a ·
docs/novaberg-convention-nmcp.md §3.

**Der Zettel ist in der Sprache des Empfangs geschrieben, nicht in der des
Dienstes.** Er nennt Merkmale der Aeusserung ("bezieht sich auf ein
Verzeichnis als Ganzes") und keine Operationen ("wurzel_erstellen") — der
Empfang kennt die Fachsprache keiner Abteilung und darf sie nicht kennen,
sonst ist er wieder die zentrale Zuordnung (§3.2).

**Er nennt keinen anderen Dienst.** Die Negativfaelle sind Eigenschaften der
Aeusserung; ein Ausschlussrecht verwandelte im Fehlerfall eine
Fehlzustellung in eine ausgebliebene (§3.6b).

Kein `execute()` mit Wirkung — die fuenf Aktionen laufen ueber den
DateienWurzelnAgent.
"""

import logging

import redis

from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins.dateien_wurzeln")


class DateienWurzelnManager(BaseManager):
    """Traegt den Aushang; die Arbeit tut der gleichnamige Agent."""

    @property
    def ziel(self) -> str:
        """Der Name, unter dem Empfang und Agent diesen Dienst finden."""
        return "dateien_wurzeln"

    @property
    def immer_aktiv(self) -> bool:
        """Nur bei erkanntem Auftrag — eine Freigabe ist ein seltener Vorgang."""
        return False

    @property
    def router_intents(self) -> list[str]:
        """Keine Intent-Kuerzel — die Erkennung laeuft ueber den Aushang."""
        return []

    @property
    def router_prompt(self) -> str:
        """Der Zettel am schwarzen Brett — Merkmale der Aeusserung, keine Operationen."""
        return """
VERZEICHNIS-FREIGABE:
Setze management_action = "agent" wenn:
1. Der User ein Verzeichnis freigibt oder freigeben will:
   "Du darfst in ... nachsehen", "Schau mal in den Ordner ...",
   "Ich gebe dir ... frei", "Du hast ab jetzt Zugriff auf ..."
2. Der User eine Freigabe zuruecknimmt oder wieder aufnimmt:
   "Nimm das Verzeichnis wieder weg", "Da darfst du nicht mehr rein",
   "Gib ... wieder frei"
3. Der User fragt, worauf Nova Zugriff hat:
   "Worauf hast du Zugriff?", "Welche Verzeichnisse hast du?",
   "Wo darfst du nachsehen?"
4. Der User eine Freigabe umbenennt:
   "Nenn das ab jetzt meine Projektdoku"

Erkennungsmerkmal:
- Der Bezug geht auf ein VERZEICHNIS ALS GANZES — einen Ordner, einen Pfad,
  eine Ablage —, nicht auf eine einzelne Datei und nicht auf einen Inhalt.
- Ein Pfad im Text ist ein starkes Merkmal, aber nicht notwendig: Der User
  kann sein Verzeichnis auch beim Namen nennen ("meine Projektdoku").

NICHT triggern bei:
- Einer Frage nach dem INHALT ("was steht in der Roadmap", "such mal nach X")
- Der blossen Erwaehnung eines Ordners ohne Freigabeabsicht
  ("das liegt bei mir unter Projekte")
- Der Bitte, etwas ABZULEGEN oder zu schreiben

Bei Erkennung:
  management_action = "agent"
  management_target = "dateien_wurzeln"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Du darfst in /dokumente nachsehen"
- "Worauf hast du eigentlich Zugriff?"
- "Nimm die Freigabe auf die Projektdoku wieder weg"
- "Nenn den Ordner ab jetzt meine Projektdoku"
"""

    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> int:
        """Kein Schreibpfad hier — die fuenf Aktionen laufen ueber den Agenten.

        Vorbedingung: keine.
        Nachbedingung: 0, und das ist die vollstaendige Aussage: Dieser
        Manager traegt einen Aushang und keinen Vorgang. Eine Zahl groesser
        null waere ein zweiter Schreiber neben dem Agenten.
        """
        if writes:
            logger.error(
                "dateien_wurzeln: %d pending_writes erreicht den Manager, der "
                "keinen Schreibpfad hat — der Vorgang laeuft ueber den Agenten "
                "und ist hier verloren", len(writes),
            )
        return 0
