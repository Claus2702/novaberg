"""Der Rückweg — was im Gespräch entstand, wandert in die Wissensdateien.

**Zwei Auftragsarten, ein Agent.** Sie stehen hier und nicht in der
Agentenklasse, damit ein Auslöser sie benennen kann, ohne ihren Importbaum
mitzuladen — derselbe Grund, aus dem `synapsen_promotion` die Herkunftswahl
aus dem Helfer holt und nicht aus dem Agenten.

Spezifikation: `docs/novaberg-agent-dateien_k.md` §4b.1a.
"""

#: Weg 2, **das Überlebende**: Der Fund wird einer Datei zugeordnet und dort
#: eingearbeitet. Auslöser ist die gelungene Promotion ins Langzeitgedächtnis
#: — sie *ist* die Bewährungsprüfung.
AUFGABE_EINARBEITEN: str = "wissen_rueckweg"

#: Weg 3, **das Zugehörige**: Der Fund wird einer Datei zugeordnet, und die
#: Zeile dieser Datei wird **verstärkt** — kein Schnitt, kein zweiter Absatz.
#: Auslöser ist ein abgelegtes Recherche-Ergebnis.
#:
#: **Der Unterschied ist eine Absicht, keine Optimierung.** Das Ergebnis
#: behält seine eigene Datei — es ist die Ausarbeitung ihres Wissens und
#: steht für weitere Vertiefungen bereit. Denselben Inhalt zusätzlich in eine
#: bestehende Datei zu schneiden, legte ihn zweimal ab; was die verwandte
#: Datei braucht, ist nicht der Text, sondern das Gewicht.
AUFGABE_VERWEIS: str = "wissen_verweis"
