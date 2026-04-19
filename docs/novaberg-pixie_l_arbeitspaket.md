# 05_L_d — Lesson: Enges Arbeitspaket — Was OpenClaw lehrt

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-pixie_l_arbeitspaket.md
**Ursprung:** nova-05-l-d.md
**Typ:** Lesson (L)
**Auslöser:** OpenClaw Agentic Workflow Analyse

---

## 1. Die Situation

Der RechercheAgent v1 hatte offene Prompts: "Erstelle einen Recherche-Plan", "Bewerte ob die Ergebnisse das Ziel abdecken", "Fasse zusammen was hilft." Das funktioniert mit Claude Sonnet (OpenClaw). Mit Mistral 24B (lokal) produzierte es generische Queries, schwache Bewertungen und Destillation ohne Charakter-Treue.

Die Analyse des OpenClaw-Ökosystems zeigte: nicht das Modell war das Problem, sondern die Prompts.

## 2. Die vier Prinzipien

### Prinzip 1: Enges Arbeitspaket

> Jeder LLM-Call bekommt exakt die Daten, die er braucht, in exakt dem Format, das er verarbeiten kann.

Nicht "plane die Recherche", sondern "Gegeben diese 3 bekannten Fakten und diese 2 Lücken, formuliere 2-3 spezifische Suchqueries." Das LLM trifft eine enge Entscheidung, kein offenes Brainstorming.

### Prinzip 2: Deterministische Orchestrierung

> Python entscheidet den Ablauf. Das LLM entscheidet innerhalb eines Schritts. Nie umgekehrt.

Die Schleife (Suche → Bewertung → ggf. nochmal) ist ein `for`-Loop in Python. Nicht das LLM entscheidet "mache ich weiter?" — der Code prüft `status == "luecken"` und iteriert.

### Prinzip 3: Strukturierte Artefakte

> Zwischen den Schritten fließen JSON/Dict-Strukturen, kein Fließtext.

Die Lagebeurteilung produziert ein Dict mit `vorwissen_zusammenfassung`, `wissensluecken`, `ausschluss`. Die Planung konsumiert dieses Dict direkt. Kein LLM muss Fließtext re-interpretieren.

### Prinzip 4: Kontext-Assembly als Engineering

> Vor dem ersten LLM-Call wird der gesamte verfügbare Kontext deterministisch aggregiert.

`kontext_paket_bauen()` ist Python-Code — kein LLM. Es liest KZG, LZG, Session, Charakter-Hash und baut ein strukturiertes Paket. Erst danach geht ein kompaktes, vorbereitetes Paket ans LLM.

## 3. Die Falle

OpenClaws ReAct-Loop wirkt wie Magie: das LLM plant, führt aus, bewertet, plant neu — in einer offenen Schleife. Der natürliche Impuls ist, das zu kopieren.

Aber der ReAct-Loop funktioniert nur mit einem Modell, das zuverlässig in einer offenen Schleife operieren kann (Claude Sonnet, GPT-4). Mit lokalen Modellen ist der zuverlässigere Weg: **deterministische Orchestrierung mit engen LLM-Schritten.**

> "Consider whether your orchestration layer needs to be an LLM at all. Sometimes the best agent architecture is one where the agents don't know they're being orchestrated." — OpenClaw Community

## 4. Übertragbarkeit

Das Muster gilt für jeden Pixie-Agenten:
- Kontext deterministisch aufbauen (Python)
- LLM nur für Sprachverarbeitung aufrufen (Klassifikation, Extraktion, Formulierung)
- Ergebnisse als strukturierte Artefakte weitergeben
- Ablaufsteuerung in Python, nicht im LLM

Es gilt auch für den User-Graph: der Router ist deterministisch, der Planner bekommt ein enges Arbeitspaket, der Responder bekommt nur die Daten die er braucht.

## 5. Verbindung zu bestehenden Prinzipien

- **"Weniger Input > stärkerer Prompt"** — Bestätigt. Die Lagebeurteilung reduziert den Kontext für alle Folge-Calls.
- **"Das LLM ist ein Sprachprozessor, kein Wissenspeicher"** — Bestätigt. Kontext-Assembly liefert das Wissen, das LLM verarbeitet es nur.
- **"Daten vollständig transportieren, Formatierung am Konsumenten"** — Bestätigt. JSON-Artefakte zwischen Steps.

---

*"If you can't describe what an agent does in one sentence, it's doing too much." — OpenClaw Best Practices*
