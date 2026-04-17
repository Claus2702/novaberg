# Nova — Pixie-Agent: VertiefungsAgent (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** VertiefungsAgent — Konzept (noch nicht implementiert)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-pixie-deepdive.md
**Quellen:** nova-05-k-b.md (VertiefungsAgent-Abschnitte)

---

## 1. Aufgabe

Der VertiefungsAgent vertieft bestehendes Wissen basierend auf KZG-Einträgen. Während der RechercheAgent breite Überblicke verschafft, füllt der VertiefungsAgent spezifische Lücken in Novas vorhandenem Wissen — tief, nicht breit.

---

## 2. Status

**Konzept, nicht implementiert.** Aktuell existiert der alte Task `vertiefen` unter `services/shadow_agent/tasks/`, der aber vom Scheduler nicht mehr aufgerufen wird. Die Migration zum eigenständigen Agenten steht aus.

**Trigger:** Queue-basiert (`aufgabe: vertiefen`), NICHT periodisch. Wird durch den KZG-Agent ausgelöst bei:
- Intention `information_teilen` mit Salienz >= 0.7
- Verstärkung mit Häufigkeit >= 3 und Salienz >= 0.7

---

## 3. Abgrenzung zum RechercheAgent

| Aspekt | RechercheAgent | VertiefungsAgent |
|--------|---------------|-----------------|
| **Ziel** | Breiter Überblick | Lücken in Novas Wissen füllen |
| **Kontext** | Session + Queue | Session + Queue + **LZG/KZG-Vorwissen (gewichtet)** |
| **Lagebeurteilung** | "Was weiß Nova? Was fehlt?" | "Was weiß Nova GUT? Wo sind TIEFE Lücken?" |
| **Planung** | "Verschaffe Überblick — verschiedene Facetten" | "Fülle spezifische Lücken — tief, nicht breit" |
| **Bewertung** | 3 Prüfungen (Standard) | 3 Prüfungen + **Prüfung 4: Tiefe** |
| **Destillation** | "Das Wichtigste zum Thema" | "Nur das Neue, was Nova noch nicht wusste" |

**Vertiefung = bestehendes Wissen vertiefen. Recherche = neues Wissen suchen.**

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

**Dual-Modell-Routing:** Identisch zum RechercheAgent — Qwen3-32B für Analyse, Mistral Q5 für Sprache.

**Geplante Dateien:**

| Datei | Beschreibung |
|-------|-------------|
| `agents/vertiefung/agent.py` | Eigene Lagebeurteilung, shared Infrastruktur |
| `agents/vertiefung/AGENT.md` | Agent-Dokumentation |

---

Verwandte Dokumente:
- RechercheAgent (Shared Infrastruktur): `nova-pixie-research.md`
- KZG-Agent (Queue-Quelle): `nova-pixie-kzg.md`
- Pixie-Agenten-Übersicht: `nova-pixie.md`
