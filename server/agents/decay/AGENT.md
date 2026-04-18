# DecayAgent

Periodischer Housekeeping-Agent. Berechnet das effektive Gewicht aller aktiven LZG-Eintraege
nach der Ebbinghaus-Formel und deaktiviert Eintraege unter dem Schwellwert.

- Kein LLM-Call
- Beide User (meister + nova)
- Periodisch: Prio 0.2, alle 24h
