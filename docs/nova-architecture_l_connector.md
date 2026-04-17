# Lesson: Connector-Segregation — Modellunabhaengigkeit durch Textdateien

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Connector-Segregation
**Stand:** 15. April 2026, Chat 46
**Pfad:** novaberg/docs/nova-architecture_l_connector.md
**Kontext:** Migration von Mistral Small 3.2 auf Google Gemma 4 26B MoE

---

## 1. Ausgangssituation

Nova lief auf Mistral Small 3.2 (24B Dense). Google Gemma 4 26B MoE versprach deutliche Verbesserungen: 2.5x schneller (nur 3.8B aktive Parameter pro Token), doppeltes Kontextfenster (32768 statt 16384), explizite Optimierung fuer Agentic Workflows.

Problem: Ein Modellwechsel betrifft jeden Prompt in jedem Node. Prompts die fuer Mistral optimiert sind, funktionieren nicht zwingend fuer Gemma4 — anderes RLHF-Conditioning, andere JSON-Faehigkeiten, andere Thinking-Mechanismen. Ohne Segregation waeren Mistral-Prompts bei jedem Gemma4-Tuning ueberschrieben und unwiederbringlich verloren.

## 2. Loesung: Zwei Schichten

### Schicht 1 — Modell-Connector (config.py)

Ein Dict definiert Modell-Profile. Ein Env-Schalter waehlt das aktive Profil. Die bestehenden Variablen werden beim Start aufgeloest:

```python
OLLAMA_CONNECTORS = {
    "mistral": {"gpu_model": "mistral-small3.2-gpu", ...},
    "gemma4":  {"gpu_model": "gemma4-gpu", ...},
}
_connector = OLLAMA_CONNECTORS[OLLAMA_CONNECTOR]
OLLAMA_MODEL = _connector["gpu_model"]
```

Kein Node-Code aendert sich. Umschalten: `OLLAMA_CONNECTOR=mistral` in .env, Neustart.

### Schicht 2 — Prompt-Segregation (prompts/)

Statische Prompt-Bloecke als Textdateien. Default-Verzeichnis + Override-Verzeichnis pro Connector:

```
prompts/
  default/        ← 16 Bloecke (funktioniert mit jedem Modell)
  gemma4/         ← 7 Overrides (verschaerfte JSON-Regeln)
  mistral/        ← leer (nutzt Defaults)
```

Ein Loader liest beim Start alle Defaults, ueberschreibt mit Connector-Overrides. Dictionary auf `PROMPTS` in config.py. Nodes greifen ueber `PROMPTS["router.rules"]` zu.

## 3. Warum Textdateien statt YAML/JSON?

Die Diskussion in Chat 45 war kurz:

> "Ob das jetzt YAML ist oder JSON oder einfach ASCII-Text, das ist doch sekundaer."

Und genau so ist es. Ein Prompt ist ein String. Eine Textdatei enthaelt einen String. Kein Parser, kein Schema, kein Framework noetig. `open(datei).read().strip()` — fertig. Die Einfachheit ist das Feature.

## 4. Prinzip: Default + Override

Das Pattern ist bewusst analog zu CSS-Kaskadierung oder Linux-Konfiguration (/etc/default + /etc/override):

1. Default funktioniert immer (Baseline)
2. Override aendert nur was noetig ist (Delta)
3. Fehlendes Override = Default gilt

Das bedeutet: Ein neuer Connector braucht nur die Dateien die abweichen. Fuer Mistral null Dateien, fuer Gemma4 sieben. Wenn ein dritter Connector kommt (z.B. Llama 4), braucht er nur seine spezifischen Overrides.

## 5. Ergebnis

| Vorher | Nachher |
|--------|---------|
| Prompts als Python-Konstanten in 15+ Dateien | Prompts als Textdateien in einem Verzeichnis |
| Modellwechsel = Code-Aenderungen in jedem Node | Modellwechsel = 1 Env-Variable |
| Prompt-Tuning ueberschreibt Originale | Prompt-Tuning in separatem Override-Verzeichnis |
| Nicht i18n-faehig | Verzeichnisstruktur ist i18n-ready |

## 6. Anwendbarkeit

Das Pattern ist universell fuer jedes System das mit wechselnden LLM-Backends arbeitet. Die Kosten (Textdateien lesen, Dictionary fuellen) sind vernachlaessigbar. Der Gewinn (Modellunabhaengigkeit, verlustfreies Tuning, einfache Erweiterbarkeit) ist permanent.

---

→ Architektur: nova-architecture.md §2.1.1
→ Connector-Dict: config.py OLLAMA_CONNECTORS
→ Loader: server/prompt_loader.py
