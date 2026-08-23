# Lesson: Connector-Segregation — Modellunabhaengigkeit durch Textdateien

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Connector-Segregation
**Stand:** 23. August 2026 (die Prompt-Segregation hat eine Modellebene bekommen — der Gespraechspfad haengt am GPU-Modell, nicht am Connector; davor: 15. April 2026, Chat 46)
**Pfad:** novaberg/docs/novaberg-architecture_l_connector.md
**Kontext:** Migration von Mistral Small 3.2 auf Google Gemma 4 26B MoE

---

## 1. Ausgangssituation

Novaberg lief auf Mistral Small 3.2 (24B Dense). Google Gemma 4 26B MoE versprach deutliche Verbesserungen: 2.5x schneller (nur 3.8B aktive Parameter pro Token), doppeltes Kontextfenster (32768 statt 16384), explizite Optimierung fuer Agentic Workflows.

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

Statische Prompt-Bloecke als Textdateien. Default-Verzeichnis + Override-Verzeichnisse:

```
prompts/
  default/        ← 91 Bloecke (funktioniert mit jedem Modell)
  gemma4-gpu/     ← 7 Overrides (verschaerfte JSON-Regeln)
```

Ein Loader liest beim Start alle Defaults und ueberschreibt sie. Dictionary auf `PROMPTS` in config.py. Nodes greifen ueber `PROMPTS["router.rules"]` zu.

> **Die Segregation nach Connector war für Gesprächs-Blöcke die falsche Größe, und das ist am 23.08.2026 gemessen worden.** Der Gesprächspfad hängt am **GPU-Modell**; zwei der drei Connectoren fahren dort dasselbe (`gemma4` und `qwen36` beide `gemma4-gpu`). Die sieben Overrides lagen deshalb unter dem aktiven Connector `qwen36` still, während Gemma4 antwortete — im Betriebslog als *„Keine Overrides fuer Connector 'qwen36'"* nachlesbar, und diese Null sah aus wie *nichts zu tun*.
>
> **Seither drei Ebenen:** `default` → `{gpu_model}` → `{connector}`. Der Connector bleibt die letzte, weil er der **engere** Schlüssel ist: Zwei Connectoren teilen sich ein Modell, kein Modell einen Connector. Für Hintergrund-Blöcke ist er weiterhin die richtige Ebene — dort unterscheiden sich die Connectoren wirklich (`cpu_model`).
>
> **Das Prinzip aus §4 trägt unverändert**, es hatte nur eine Ebene zu wenig. Ein Verzeichnis `mistral/` hat es übrigens nie gegeben; die Zeile stand hier, weil sie zur Symmetrie passte.

## 2a. Was von den Overrides trägt — gemessen statt vermutet

Die sieben Gemma4-Blöcke stammen vom April 2026 und tun zwei verschiedene Dinge. Am 23.08.2026 direkt gegen Ollama gemessen, drei Tribunal-Blöcke × 12 Läufe je Fassung, `think=False`, temperature 0.2 (`labor/2026-08-23_prompt_overrides_wirkung.py`):

| | Override | Default |
|---|---|---|
| **mit** `format="json"` | 36/36 gültiges JSON | **36/36** |
| **ohne** `format` — die Kontrolle | 36/36 | **0/36** |

**Die Kontrolle ist der Teil, der die Messung trägt.** Ohne sie hieße „kein Unterschied" auch: „die Sonde sieht nichts". Mit ihr steht fest, dass die sechs Formatzeilen genau das leisten, wofür sie gebaut wurden — und dass `format="json"` dasselbe strukturell erzwingt.

**Sie bleiben trotzdem.** Eine Redundanz, die im Fehlerfall trägt, ist keine: Käme ein Aufrufer ohne `expect_json` hinzu, ist der Unterschied 36 zu 0.

**Die Thinking-Zeile ist entfernt.** *„Halte deine internen Ueberlegungen unter 100 Tokens"* stand in 7 von 7 Overrides und 0 von 91 Defaults. Sie stammt aus einer Zeit, in der `think` kein Feld der Anfrage war — die Klasse entstand erst am **20.05.2026**, fünf Wochen später. Heute setzen alle verbrauchenden Knoten `think=False`, und Ollama liefert dann kein Denkfeld; im Betriebslog kommt `<think` in **0 von 31** Dateien vor.

Ihre gemessene Wirkung traf deshalb den **sichtbaren** Text: Vor dem Entfernen war der Override in **3 von 3** Blöcken kürzer als der Default, danach in **1 von 3**. Der Vorzeichenwechsel ist die Aussage, nicht der Mittelwert — die Default-Fassung schwankte zwischen zwei Läufen bei unverändertem Prompt selbst um 7 %, und das ist die Rauschgrenze.

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

→ Architektur: novaberg-architecture.md §2.1.1
→ Connector-Dict: config.py OLLAMA_CONNECTORS
→ Loader: server/prompt_loader.py
