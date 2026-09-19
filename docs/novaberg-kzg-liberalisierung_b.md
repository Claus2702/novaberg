# Novaberg — KZG-Liberalisierung + Cluster-Promotion (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-kzg-liberalisierung_k.md`](novaberg-kzg-liberalisierung_k.md) · Ausarbeitung: [`novaberg-kzg-liberalisierung_t.md`](novaberg-kzg-liberalisierung_t.md) · Diskussion und Ergänzungen: [`novaberg-kzg-liberalisierung_e.md`](novaberg-kzg-liberalisierung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 5. Betroffene Dateien

| Datei | Änderung |
|-------|---------|
| config.py | Schwellwerte, TTL, Cap, Cluster-Konstanten, NODE_LLM_CONFIG |
| memory/kzg.py | Konstanten migriert, 3-Stufen-TTL, thematische Verstärkung |
| memory/__init__.py | Verwaiste Re-Exporte entfernt |
| agents/kzg/agent.py | Subgraph 5→4 Nodes |
| agents/kzg/speicher.py | Embedding-Erzeugung, thematische Verstärkung, sin^0.6 Cap |
| agents/kzg/aehnlichkeit.py | Gelöscht |
| agents/promotion/agent.py | 4-Phasen, 5 neue Methoden, 3 gelöscht, Kohärenzprüfung |
| prompts/default/salienz.aufgabe.txt | Bewertungsskala angepasst |

---

## 6. Evolutionspfad

Die Implementierung durchlief 10 Iterationen (A0→A→B→C→C1→D→D1→D2→D2-Fix) in einer Session. Wesentliche Kurskorrekturen: Themen-Clustering verworfen (kurze Strings unbrauchbar), Greedy-Zuordnung verworfen (Informationsverlust), Kohärenzprüfung ergänzt, Magnetismus-Kohärenz nachgereicht.

---
