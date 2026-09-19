# Novaberg — Tool: Datei-Operationen (Konzept)

**Absicht:** Nova liest und bearbeitet Dateien mit deterministischen Werkzeugen, die keinen Modellaufruf enthalten: erst die Karte, dann der Block, dann die Fundstelle — und sie schreibt chirurgisch, ohne den Rest der Datei zu berühren; was sie in ihren eigenen Wissensdateien ändert, bleibt als gepaarte Versionsmarke im Dokument nachvollziehbar.
**Stand:** 20. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Dateien — Schreibwerkzeug* 🟢 · *Dateien — Leseschicht* 🔴 · *Dateien — Schreibschicht* 🟢 · *Dateien — Versionierung im Dokument* 🟢 · *Dateien — Auftragsform `DATEI: {json}`* 🟠 · *Ankertreue des Schreibmodells* 🟢 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-tool-dateien_t.md`](novaberg-tool-dateien_t.md) · Bauplan und Umstellung (`_b`): keiner · [`novaberg-tool-dateien_e.md`](novaberg-tool-dateien_e.md) · [`novaberg-tool-dateien_m.md`](novaberg-tool-dateien_m.md)
**Entschieden:** 0 · **Offen beim Meister:** 3 (Liste in [`novaberg-tool-dateien_e.md`](novaberg-tool-dateien_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-tool-dateien_k.md §3.4` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-tool-dateien_t.md`](novaberg-tool-dateien_t.md), `_e` ist [`novaberg-tool-dateien_e.md`](novaberg-tool-dateien_e.md), `_m` ist [`novaberg-tool-dateien_m.md`](novaberg-tool-dateien_m.md).

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle | `_k` |
| 1 · 2 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 | `_t` |
| 3.4 · 3.4.1 · 3.4.2 · 3.4.3 · 3.4.4 · 3.4.5 · 3.4.6 | `_t` |
| 3.4.7 | `_e` |
| 4 · 5 · 6 | `_t` |
| 7 (mit *Erkenntnisse aus den Quellen*) · *Verwandte Dokumente* | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, *Bauzustand am 18.08.2026* mit der Messung der Ankertreue, Pfad, Quellen) | `_m` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Aufgabe

> **Die Prämisse dieses Abschnitts gilt nur noch für den Gesprächspfad.** Gemessen am laufenden System am 04.08.2026, 21:02 UTC, Connector `qwen36`: Der GPU-Pfad (`gemma4-gpu`, Gespräch) steht bei **32768**, der CPU- und der Analyse-Pfad (`qwen36-cpu`, Hintergrund) bei **262144** — dem Achtfachen.
>
> Für die Hintergrund-Agenten — Recherche, Vertiefung, Traum, Nachfragen — ist der fraktale Zoom damit **nicht mehr erzwungen**: Eine vollständige Wissen-Datei von wenigen Kilobyte passt mühelos in den Prompt. Er bleibt trotzdem sinnvoll, wo Token Geld und Zeit kosten oder wo ein gezielter Block genauer ist als eine ganze Datei; er ist nur keine Notwendigkeit mehr, sondern eine Wahl.
>
> **Für den Gesprächspfad bleibt der Abschnitt unverändert gültig.** Dort ist die Grenze real, und der Enricher liest gegen dieselben 32768 wie zuvor.
>
> Der Text unten bleibt als Herkunft stehen (`40_DOKU_GRUNDSAETZE`: markieren, nicht löschen).

Novas Kontext hat 32768 Tokens. System-Prompt, Charakter, Session, Gedaechtnis belegen einen erheblichen Teil davon. Grosse Dateien koennen nicht vollstaendig in den Prompt geladen werden. Trotzdem muss Nova bestehende Dateien lesen, verstehen, gezielt durchsuchen und chirurgisch bearbeiten koennen.

`tools/dateien/` stellt dafuer eine Sammlung deterministischer Python-Funktionen bereit. Kein LLM in den Tools — der Agent denkt (LLM), das Tool fuehrt aus (Python). Exakt das Prinzip "Berechnung in Python, nicht im LLM."

---

## 2. Kernprinzip — Fraktaler Zoom (Mandelbrot-Navigation)

Wie bei der Mandelbrotmenge: Jeder Zoom-Schritt zeigt mehr Detail in einem kleineren Bereich. Kein Schritt braucht das Gesamtbild. Das LLM entscheidet nach jedem Schritt, ob es tiefer zoomen muss oder genug Kontext hat.

```
Level 0: Verzeichnis scannen
          → "3 Dateien zu 'blockchain'" (~20 Tokens)

Level 1: Struktur analysieren
          → "5 Bloecke: ## Konsens (Z.8-35), ## Smart Contracts (Z.36-60), ..."
            (~50 Tokens)

Level 2: Zielblock lesen
          → Inhalt von ## Smart Contracts (~200 Tokens)

Level 2b: Block zu gross → Haeppchenweise lesen
          → Zeilen 0-200 von 412, rest: 212 (~200 Tokens)

Level 3: Innerhalb des Blocks suchen (grep)
          → Zeilen mit "Security" (~30 Tokens)

Edit:     Block erweitern, ersetzen, oder str_replace innerhalb
          → Chirurgischer Eingriff, Rest der Datei unberuehrt
```

Jeder Schritt verbraucht nur so viele Tokens wie noetig, um die naechste Entscheidung zu treffen.

**Referenz:** Claude Codes autoDream-Service arbeitet identisch — "Don't exhaustively read transcripts. Look only for things you already suspect matter." (Quelle: Claude Code Leak-Analyse, github.com/Piebald-AI/claude-code-system-prompts)

---

## 7. Referenzen und Quellen

| Quelle | Relevanz | Fundort |
|--------|----------|---------|
| **SWE-agent** (Princeton/Stanford, NeurIPS 2024) | `str_replace_editor` mit `view_range`, empirisch validiert | github.com/SWE-agent/SWE-agent |
| **Claude Code** (Leak 2026-03-31) | `FileEditTool`, `FileReadTool`, 40+ Agent-Tools | github.com/Piebald-AI/claude-code-system-prompts |
| **Aider** (Paul Gauthier) | 5 Edit-Formate, Leaderboard, Architect-Mode | aider.chat/docs/more/edit-formats.html |
| **OpenAI Codex CLI** | `apply_patch.py`, GPT-4.1 auf Patch-Format trainiert | Prompt Cookbook (April 2025) |
| **Fabian Hertwig** | Umfassender Vergleich aller Edit-Ansaetze | fabianhertwig.com/blog/coding-assistants-file-edits/ |
| **Letta/MemGPT** (UC Berkeley) | `core_memory_replace/append` — Paradigma "LLM verwaltet eigenes Gedaechtnis" | github.com/letta-ai/letta, docs.letta.com |

### Erkenntnisse aus den Quellen

- **SWE-agent:** "Das effektivste Edit-Tool ist str_replace. Bei Nicht-Eindeutigkeit: range-Parameter oder mehr Kontext."
- **Aider:** "whole ist einfach aber teuer, diff ist effizient aber fehleranfällig. Verschiedene LLMs brauchen verschiedene Formate."
- **SWE-agent Deep Dive:** "Nicht die menschliche Shell wiederverwenden. cat, sed, grep -rn sind schlechte Agent-Tools. Agent-gerechte Befehle mit begrenztem, strukturiertem Output bauen."
- **Augment Code:** "Fuer SWE-bench waren Embedding-Tools nicht der Engpass — grep und find reichten."
- **Novas fuenfter Weg:** Block-basierte Navigation mit Markdown-Headings als natuerliche Grenzen ist semantisch eindeutiger als Code-Zeilen. `str_replace_in_block` begrenzt den Suchraum auf einen Block und reduziert Eindeutigkeitsprobleme massiv.

---

Verwandte Dokumente:
- Autonomes Wissen: `novaberg-autonomous-wissen_k.md`
- Pixie-Plugin-Architektur: `novaberg-pixie-plugin_k.md`
- Web-Infrastruktur: `novaberg-tool-web.md`
