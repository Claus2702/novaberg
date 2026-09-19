# Novaberg — Pixie-Agent: VertiefungsAgent (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-pixie-deepdive_k.md`](novaberg-pixie-deepdive_k.md) · Diskussion und Ergänzungen: [`novaberg-pixie-deepdive_e.md`](novaberg-pixie-deepdive_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 2. Status

**Konzept, nicht implementiert.** Aktuell existiert der alte Task `vertiefen` unter `services/shadow_agent/tasks/`, der aber vom Scheduler nicht mehr aufgerufen wird. Die Migration zum eigenständigen Agenten steht aus.

**Trigger:** Queue-basiert (`aufgabe: vertiefen`), NICHT periodisch. Wird durch den KZG-Agent ausgelöst bei:
- Intention `information_teilen` mit Salienz >= 0.7
- Verstärkung mit Häufigkeit >= 3 und Salienz >= 0.7

---

## 4. Geplante Architektur

Der VertiefungsAgent teilt Infrastruktur mit dem RechercheAgent. Suche, Bewertung und Destillation werden importiert — mit eigenen Prompts. Nur die Kontext-Assembly und die Lagebeurteilung sind eigenständig.

```python
# agents/vertiefung/agent.py
from agents.recherche.suche import suche_und_fetch
from agents.recherche.bewertung import bewerten       # gleiche Struktur, anderer Prompt
from agents.recherche.destillation import destillieren  # Mistral, gleiche Struktur
```

Die Lagebeurteilung des VertiefungsAgenten fragt spezifischer: Wo hat Nova nur Oberfläche? Wo fehlen Mechanismen, Zusammenhänge, Gegenargumente?

**Dual-Modell-Routing:** Identisch zum RechercheAgent — Qwen3-32B (`PIXIE_ANALYSE_MODEL`) für Analyse, `SHADOW_MODEL` (aktiv: Gemma 4) für Sprache.

**Geplante Dateien:**

| Datei | Beschreibung |
|-------|-------------|
| `agents/vertiefung/agent.py` | Eigene Lagebeurteilung, shared Infrastruktur |
| `agents/vertiefung/AGENT.md` | Agent-Dokumentation |

---
