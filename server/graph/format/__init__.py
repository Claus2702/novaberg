"""Format-Tools — wandelt strukturierte Graph-Daten in Strings fuer
LLM-Konsumenten (Responder, Thinker-Tools).

Die Funktionen in diesem Paket sind das einzige Ort, an dem Format-
Schema-Wissen lebt. Memory-Module und Plugin-Manager liefern
strukturierte Daten; die Format-Funktionen hier bauen daraus die
String-Darstellung, die das LLM zu sehen bekommt.
"""

from graph.format.memory_context import format_memory_entries

__all__ = ["format_memory_entries"]
