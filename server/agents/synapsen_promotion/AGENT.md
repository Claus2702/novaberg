# SynapsenPromotionAgent

Promotet KZG-Eintraege als eigenstaendige Knoten ins Synapsen-Netz (lzg_knoten)
und bildet Kanten zu verwandten Bestandsknoten (lzg_kanten). Ersetzt die
Cluster-Aggregat-Promotion, sobald SYNAPSEN_PROMOTION_AKTIV gesetzt ist.

- Keine LLM-Calls, keine Fakten-Extraktion (Magnet-Felder kommen aus P3)
- Embedding aus inhalt allein (K9), gewicht_roh = KZG-Salienz (K8)
- Match >= LZG_KNOTEN_MATCH_SCHWELLE -> Reinforcement + Trigger 2, sonst Neuanlage + Trigger 1 (K10)
- Schreibt hintergrund_log + pipeline_log auf jedem Event (K5)
- Queue VOLLSTAENDIG abarbeiten (KZG hat TTL!), KZG-Hash wird nicht geloescht
- Setzt hash_dirty nach Erfolg
- Periodisch: Prio 0.9, alle 5 min (wie promotion); dormant bei Flag=False
- context_user: user (Gedaechtnis des Meisters)
