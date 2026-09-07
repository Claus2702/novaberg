# Lesson: Connector-Segregation — Modellunabhaengigkeit durch Textdateien

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Connector-Segregation
**Stand:** 5. September 2026, 20:28 UTC (§7 neu — die Modellebene haengt seither am **antwortenden** Modell, nicht mehr am konfigurierten GPU-Modell, und ein Modellname mit Schraegstrich wird flach gemacht). Davor 23. August 2026 (die Prompt-Segregation hat eine Modellebene bekommen — ~~der Gespraechspfad haengt am GPU-Modell~~, siehe §7; davor: 15. April 2026)
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

## 7. Die Modellebene haengt am antwortenden Modell (05.09.2026)

**Der Satz im Kopf dieses Dokuments war eine Vereinfachung, die genau so lange trug, wie
jedes Backend ein lokales war.** Die Modellebene wurde mit `OLLAMA_MODEL` geschluesselt —
dem **konfigurierten** GPU-Modell des Connectors. Welches Modell tatsaechlich antwortet,
entscheidet aber `MODEL_WORKER_BACKENDS["chat"]`.

Solange dort ein Ollama-Backend stand, waren beide Werte gleich. Mit dem ersten fremden
Rueckhalt faellt das auseinander: Das neue Modell bekaeme die Bloecke unter
`prompts/gemma4-gpu/` — Regeln, die fuer ein anderes Modell geschrieben sind.

`config.antwortendes_chat_modell()` loest den Namen seither ueber `MODELL_NACH_BACKEND`
aus dem Backend auf. Bei `ollama_gpu` liefert es unveraendert `OLLAMA_MODEL`; ein Zeuge
haelt diese Gleichheit fest, damit ein Abschalten nicht wie eine Umstellung aussieht.

### Ein Modellname kann einen Schraegstrich tragen

Ein Fernmodell nennt den Anbieter mit: `deepseek/deepseek-v4-flash-0731`. Unveraendert in
den Pfad eingesetzt ergaebe das ein **verschachteltes** Verzeichnis, und das Zwischenglied
`prompts/deepseek/` waere eine Ebene, die niemand nachschlaegt. Der Lader macht den Namen
deshalb flach (`/` → `_`); gesucht wird unter
`prompts/deepseek_deepseek-v4-flash-0731/`.

**Gefunden hat das ein Zeuge, der seit dem 23.08.2026 steht** — *„ein Verzeichnis, das
keine Ebene je nachschlaegt, ist totes Material"*. Seine Menge der erreichbaren Namen kam
aus `OLLAMA_CONNECTORS` und damit **nur von der eigenen Maschine**; sie kennt jetzt auch
die Fernmodelle.

> **Die Ebene ersetzt einen Block, sie ergaenzt ihn nicht.** Wer einen Block ueberschreibt,
> um einen Absatz zu aendern, uebernimmt die Pflege aller uebrigen —
> `tests/test_prompt_override_deckung.py` haelt fest, dass jedes Absatz-Stichwort des
> Defaults im Override wiederkehrt.

---

→ Architektur: novaberg-architecture.md §2.1.1
→ Connector-Dict: config.py OLLAMA_CONNECTORS
→ Modell je Backend: config.py MODELL_NACH_BACKEND
→ Loader: server/prompt_loader.py

---

## 8. Was jeder Anbieter fuehrt — gemessen am 07.09.2026

**Der Kanon `OPENROUTER_GEFUEHRTE_PARAMETER` in `config.py` stand von Hand fuer *einen*
Anbieter da.** Er stammt aus `GET /models/{id}/endpoints`, und dieselbe Quelle beantwortet
die Frage fuer **alle** — `labor/werkzeug/anbieter_faehigkeiten.py` liest sie aus.

`[gemessen]` ueber **29 Anbieter** desselben Modells. Die Auskunft ist schaerfer als die
Preistabelle:

| Anbieter | in/M | out/M | cache/M | `repetition_penalty` |
|---|---:|---:|---:|---|
| DeepInfra | 0,060 | 0,180 | 0,015 | ja |
| CoreWeave | 0,130 | 0,280 | 0,070 | ja |
| Parasail | 0,140 | 0,280 | 0,050 | ja |
| **Baidu** | 0,140 | 0,280 | 0,028 | **nein** |

> **Der genutzte Anbieter fuehrt keine der drei Sampling-Schrauben** — weder
> `repetition_penalty` noch `presence_penalty` noch `frequency_penalty`. Responder und
> Verfasser setzen zwei davon gegen Wiederholungen; sie gehen ins Leere. Der Kanon faengt
> das ab, damit sie nicht stumm verworfen werden — **aber die Wirkung fehlt trotzdem**, und
> das ist ein Grund zum Anbieterwechsel unabhaengig vom Preis.

**Der Preis war der laute Grund, nicht der einzige.** Am 07.09.2026 fiel der Rabatt weg:
konfiguriert $0.04998/$0.09996 je Million, lebend $0.14000/$0.28000 — **Faktor 2,80**.

## 9. Warum die Modellwahl an der **aktiven** Parameterzahl haengt

**`ollama show` nennt die Gesamtzahl, nicht die aktive** — und bei einem MoE entscheidet die
aktive ueber den Durchsatz. `[gemessen 07.09.2026]` auf der eigenen Maschine:

| Modell | Bauart | aktiv | Durchsatz |
|---|---|---:|---:|
| `gemma4-gpu` (GPU) | MoE 26B | 3,8 Mrd. | **96,4 tps** |
| `gemma4-a4b-gpu` (GPU) | MoE 26B | 4 Mrd. | **99,3 tps** |
| `qwen36-cpu` (CPU) | MoE 35B | 3 Mrd. | **18,3 tps** |

**Ein dense-Modell derselben Groessenordnung waere um ein Vielfaches langsamer.** Qwen 3.8
27B ist dense — 27 Mrd. aktiv, also rund neunmal die Rechenarbeit von 3 Mrd.; auf der CPU
hochgerechnet **rund 2 tps**, und ein `pixie/hash`-Lauf ginge von 22 s auf etwa 200 s. Die
MoE-Variante desselben Hauses (Flash-Next, 512 Experten, 10 aktiv) traegt die richtige
Bauart und **103 GB** — bei 61 GB Arbeitsspeicher ausser Reichweite.

> **Der Ort fuer ein klugeres und langsameres Modell ist `analyse_model`**, das der Connector
> ohnehin getrennt fuehrt. Die Destillation laeuft taeglich, nicht je Turn; dort sind 200 s
> belanglos — und dort sitzen die Defekte, die ein besseres Modell beheben wuerde
> (`PROFIL-VERALLGEMEINERT-EINZELBELEG`, unbelegte Zitate).

## 10. Der Prefix-Cache — gemessen, nicht konfiguriert

`llama.cpp` haelt den KV-Cache eines wiederkehrenden Prompt-Anfangs von selbst.
`[gemessen 07.09.2026]`, derselbe Prompt dreimal:

| | kalt | warm | Faktor |
|---|---:|---:|---:|
| GPU (1934 Token) | 787,7 ms | 88 ms | **8–9** |
| CPU (1915 Token) | 11,61 s | 0,09 s | **115** |

**Auf der CPU wiegt er das Vielfache**, weil dort das Lesen teuer ist — und genau dort laeuft
der Hintergrund. Auf `pixie/hash` hochgerechnet (5418 ein / 403 aus): **72,8 s** mit
entladenem Modell, **54,9 s** geladen mit kaltem Prompt, **22,3 s** warm.

**Zwei Stellschrauben sind unkonfiguriert:** `OLLAMA_KEEP_ALIVE` ist nicht gesetzt, es gilt
der Default von fuenf Minuten — **jeder Kaltstart kostet 17,9 s Ladezeit** auf der CPU.
`OLLAMA_KV_CACHE_TYPE` steht auf `f16`; `q8_0` halbiert den KV-Speicher bei kaum messbarem
Verlust. Der Cache selbst braucht keine Einstellung, sondern eine Eigenschaft der Prompts:
**das Stabile muss vorn stehen.**
