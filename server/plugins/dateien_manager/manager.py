"""Der Aushang des lesenden Dienstes — sein Zettel am schwarzen Brett.

Spezifikation: docs/novaberg-agent-dateien_k.md §8.1, §3.0c ·
docs/novaberg-convention-nmcp.md §3.

**Der Zettel ist in der Sprache des Empfangs geschrieben, nicht in der des
Dienstes.** Er nennt Merkmale der Aeusserung ("bezieht sich auf einen
abgelegten Text") und keine Operationen ("datei_grep") — der Empfang kennt die
Fachsprache keiner Abteilung und darf sie nicht kennen, sonst ist er wieder die
zentrale Zuordnung (§3.2).

**Er enthaelt sich ueber die Nachbarn** (§3.0c). *"Weisst du was ueber X"*
heisst "such in allem, was du hast" — heute drei Bestaende mit drei Zugaengen.
Dieser Zettel sagt, woran man erkennt, dass in **Unterlagen** etwas zu holen
ist, und sagt nichts darueber, ob stattdessen oder zusaetzlich das eigene
Wissen zu befragen waere. Der Empfang beurteilt jeden Zettel fuer sich und
stellt mehrfach zu; mehrere Treffer sind der Normalfall, nicht der Konflikt.

**Die Negativfaelle stehen nicht hier, sondern am Dienst.** Der Aggregator
setzt sie bei jedem Dienst an derselben Stelle in dieselbe Form
(`agents/nmcp.py`); sie zusaetzlich in diesen Text zu schreiben legte dem
Modell dieselbe Regel zweimal vor. Zwei Regeln, die dasselbe sagen, heben sich
in der Wirkung auf.

Kein `execute()` mit Wirkung — die Arbeit tut der gleichnamige Agent.
"""

import logging

import redis

from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins.dateien")


class DateienManager(BaseManager):
    """Traegt den Aushang; das Lesen tut der gleichnamige Agent."""

    @property
    def ziel(self) -> str:
        """Der Name, unter dem Empfang und Agent diesen Dienst finden."""
        return "dateien"

    @property
    def immer_aktiv(self) -> bool:
        """Nur bei erkanntem Auftrag — er wartet, er laeuft nicht mit."""
        return False

    @property
    def router_intents(self) -> list[str]:
        """Keine Intent-Kuerzel — die Erkennung laeuft ueber den Aushang."""
        return []

    @property
    def router_prompt(self) -> str:
        """Der Zettel am schwarzen Brett — Merkmale der Aeusserung.

        Nachbedingung: nichtleerer Text, der die beiden Management-Felder
        benennt. Ohne sie waere der Zettel eine Beschreibung ohne Wirkung.
        """
        return """
UNTERLAGEN LESEN:
Setze management_action = "agent" wenn:
1. Der User nach dem Inhalt eines abgelegten Textes fragt:
   "Was steht in ...?", "Lies mir den Abschnitt ueber ... vor",
   "Wie war das nochmal mit ... in den Unterlagen?"
2. Der User wissen will, WO etwas steht:
   "Steht das irgendwo?", "Such mal in den Unterlagen nach ...",
   "Welche Aufzeichnungen hast du zu ...?", "Was haben wir zu ...?"
3. Der User eine Fachfrage stellt, deren Antwort in einem abgelegten Text
   stehen koennte — ein Begriff, eine Zahl, ein Name, der nicht Allgemeinwissen
   ist: "Bei welcher Temperatur laeuft der Schruehbrand?"

Erkennungsmerkmal:
- Der Bezug geht auf einen ABGELEGTEN TEXT — ein Dokument, eine Datei, eine
  Stelle darin —, nicht auf eine Erinnerung an ein Gespraech.
- Entscheidend ist der Bezug, nicht die Satzform: Auch eine Frage ohne das Wort
  "Datei" passt, wenn ihre Antwort in einer Ablage stehen wuerde.
- Ein Fachbegriff, den ein Gespraech nicht hergibt, ist ein starkes Merkmal.

Bei Erkennung:
  management_action = "agent"
  management_target = "dateien"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Was steht in der Roadmap zum Waechter?"
- "Steht irgendwo, wie die Salienz gerechnet wird?"
- "Such mal in den Unterlagen nach dem Abschnitt ueber die Baender"
- "Welche Aufzeichnungen hast du zu Orchideen?"
"""

    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> int:
        """Kein Schreibpfad hier — und auch keiner im Agenten.

        Vorbedingung: keine.
        Nachbedingung: 0, und das ist die vollstaendige Aussage: Dieser Dienst
        liest. Eine Zahl groesser null waere ein Schreiber, den es in diesem
        Verbund nicht gibt.
        """
        if writes:
            logger.error(
                "dateien: %d pending_writes erreicht den Manager eines "
                "lesenden Dienstes — hier gibt es keinen Schreibpfad, und der "
                "Vorgang ist verloren", len(writes),
            )
        return 0
