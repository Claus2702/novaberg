# PromotionAgent

Promotet KZG-Eintraege ins Langzeitgedaechtnis. Zwei-Call-Promotion:
Call 1 klassifiziert (Fakt/Erinnerung, Entitaeten, Referenz/Interface).
Call 2 extrahiert Fakten-Tripel.

4 Qualitaetsfilter: Speaker (O5), Interface (O6), Objekt (O11), Tautologie (O12).
Entity Resolution + Edge Invalidation via FaktenManager.

- LLM: CPU-Modell (1-3 Calls pro Eintrag)
- Queue VOLLSTAENDIG abarbeiten (KZG hat TTL!)
- Setzt hash_dirty nach Erfolg
- Periodisch: Prio 0.9, alle 5 min
- context_user: user (Gedaechtnis des Meisters)
