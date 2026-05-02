"""ContextEntry — strukturierter Eintrag im memory_entries-Pool.

Pre-format data structure used by Memory modules (KZG, LZG, Charakter,
Session-Summary) and Plugin Managers to deliver context contributions
to the Enricher. Replaces the old pre-formatted string approach where
format-knowledge was scattered across multiple modules.

Pipeline:
    Memory/Plugin liefert  -->  Enricher sammelt          -->  Reducer dedupliziert
    list[ContextEntry]          state["memory_entries"]        auf Liste
                                                                -->  Formatter baut String
                                                                     state["memory_context"]
"""

from typing import Any, TypedDict


class ContextEntry(TypedDict):
    """Strukturierter Eintrag im memory_entries-Pool.

    Liefert ein einzelnes Memory-Item (KZG-Treffer, LZG-Eintrag,
    Charakter-Hash, Session-Summary, Plugin-Beitrag) als typisierte
    Datenstruktur ohne Format-Drumherum. Der Reducer dedupliziert
    auf dieser Datenebene; der Formatter baut daraus den finalen
    memory_context-String fuer den Responder.

    Felder:
        quelle:  Quellen-Tag, steuert Formatter-Verhalten und
                 Reihenfolge im finalen String. Erlaubte Werte:
                   "summary"            — bisheriger Gespraechsverlauf
                   "charakter"          — Charakter-Hash
                   "kzg"                — Kurzzeitgedaechtnis-Treffer
                   "lzg"                — Langzeitgedaechtnis-Treffer
                   "plugin_notiz"       — Plugin: Notizen
                   "plugin_timeline"    — Plugin: Timeline
                   "plugin_direktive"   — Plugin: Direktiven
                   "plugin_*"           — weitere Plugins nach Konvention

        subtyp:  Bei KZG/LZG die Dimension ("emotion", "kommunikation",
                 "themen", ...). Leer-String bei Quellen ohne Subtyp.

        inhalt:  Reiner Text-Inhalt, ohne Format-Praefix, ohne
                 Metadaten-Klammern. Mehrzeilig erlaubt (z.B. ganze
                 Plugin-Bloecke werden als ein Eintrag mit
                 mehrzeiligem inhalt geliefert).

        gewicht: Effektives Gewicht (Salienz oder Eintrags-Gewicht).
                 Reducer nutzt es fuer Konflikt-Aufloesung (hoechstes
                 Gewicht gewinnt). Formatter nutzt es fuer Sortierung
                 von kzg/lzg-Eintraegen (absteigend).

        meta:    Quellen-spezifische Felder. Konvention pro quelle:
                   "summary"          — leer
                   "charakter"        — leer
                   "kzg"              — themen (list[str]), beobachter
                                        (str), erstellt_am (float)
                   "lzg"              — arousal (float 0..1), vektor
                                        (str), beobachter (str),
                                        dimension (str), erstellt_am
                                        (float), ttl (int|None)
                   "plugin_notiz"     — plugin-spezifisch (frei)
                   "plugin_timeline"  — plugin-spezifisch (frei)
                   "plugin_direktive" — plugin-spezifisch (frei)
                 Der Formatter liest nur, was er pro quelle kennt;
                 unbekannte Meta-Felder werden ignoriert (kein Fehler).
    """

    quelle: str
    subtyp: str
    inhalt: str
    gewicht: float
    meta: dict[str, Any]
