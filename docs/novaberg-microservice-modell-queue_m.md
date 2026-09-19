# Novaberg — Microservice-Modell-Queue (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-microservice-modell-queue_k.md`](novaberg-microservice-modell-queue_k.md) · Ausarbeitung: [`novaberg-microservice-modell-queue_t.md`](novaberg-microservice-modell-queue_t.md) · Bauplan und Umstellung: [`novaberg-microservice-modell-queue_b.md`](novaberg-microservice-modell-queue_b.md) · Diskussion und Ergänzungen: [`novaberg-microservice-modell-queue_e.md`](novaberg-microservice-modell-queue_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 9a. Der Vorgabewert ist die Frist der Aufrufer, nicht ihre Reserve (16.08.2026)

*„Der Fußtext unten“ ist die bisherige Schlusszeile des Konzepts; sie steht in [`novaberg-microservice-modell-queue_b.md`](novaberg-microservice-modell-queue_b.md), Abschnitt „Bisheriger Schluss“.*

Der Fußtext unten nennt das Ergebnis von Block 5 richtig: *„Worker-Instanz-Default per Konstruktor, **pro Call überschreibbar**"*. Der Mechanismus ist gebaut und funktioniert. **Gemessen wurde am 16.08.2026, wie oft er benutzt wird:**

```
Aufrufstellen von submit_sync im Baum        62
davon mit einer eigenen Frist                 1
```

**Damit ist der Vorgabewert keine Reserve, sondern die geltende Frist von 61 Aufrufstellen.** Das ist keine Nachlässigkeit der Aufrufer, sondern die Bauart: Wer nichts angibt, bekommt die Zahl, die für lauter verschiedene Aufgaben zugleich gesetzt ist. Ein Vorgabewert wird deshalb **nach der langsamsten Aufgabe bemessen, die ihn erbt** — oder die langsame Aufgabe nennt ihre eigene Frist.

Der Fall, an dem es sichtbar wurde: `recherche/zwischen` lag im Median bei **181 s** gegen die 300 s des `background`-Workers und riss sie in **12 %** der Läufe; die übrigen neun Aufrufstellen desselben Agenten lagen bei höchstens 89 s. Die beiden anderen Worker sind unauffällig — `chat` max 30,0 s und `embed` max 2,26 s gegen je 60 s, über 1303 Aufrufe null Überschreitungen.

**Und die Frist gehört mit einer Ausgabegrenze zusammen.** Eine Frist ohne Grenze begrenzt nichts, weil die Arbeit wächst, bis die Frist reißt; eine Grenze jenseits der Frist ist wirkungslos. Prüfbar ist ihr Verhältnis: Grenze geteilt durch den gemessenen Durchsatz muss deutlich unter der Frist liegen. Registriert als `F-FRIST-1`; die Herleitung am konkreten Fall steht in `novaberg-pixie-research.md` §7.

---

## 9b. Der erste fremde Rueckhalt — die Zusage von §1 gemessen (05.09.2026)

*Der Abschnitt ist überwiegend Messung und steht deshalb ganz hier. Er trägt auch den Bau des vierten Backend-Werts `openrouter` und die zwei Ergänzungen zu §3.5 (§3 steht in [`novaberg-microservice-modell-queue_k.md`](novaberg-microservice-modell-queue_k.md)).*

§1 schliesst mit einem Versprechen: *„Kuenftige Modell-Wechsel … sind Worker-interne
Konfiguration, keine projekt-weite Refactoring-Aktion."* Am 05.09.2026 wurde es zum
ersten Mal eingeloest, und zwar gegen ein Modell, das **nicht lokal laeuft**.

**Die Zahlen, an denen die Zusage haengt** — erhoben ueber `server/` ohne `tests/`:

| | |
|---|---:|
| Aufrufe von `model_service.chat.submit` | 35 |
| Aufrufe von `model_service.background.submit` | 16 |
| Dateien, die die Registry ansprechen | 63 |
| **Chat-Aufrufe an der Schicht vorbei** | **0** |

Die verbliebenen Direktzugriffe auf einen Modell-Client sind die Statusabfrage
(`api/health.py` mit `list()`/`pull()`, kein Erzeugen) und die Embedding-Pfade, die nach
§4.2 ausdruecklich nicht Teil der Backend-Wahl sind. **Alle drei Graphen — Mensch,
Charakter, Agent — haengen damit an denselben drei Workern.** Der Wechsel des Modells
fuer das ganze System ist drei Umgebungsvariablen breit.

Gebaut wurde ein vierter Backend-Wert, `openrouter`, mit dem `OpenRouterProvider` als
Rueckhalt: das OpenAI-Chat-Protokoll ueber `httpx`, kein Anbieter-SDK, die Modell-ID
waehlt den Anbieter. Er setzt `expect_json` als `response_format` **durch** — §3.3 sagt,
Workarounds und Faehigkeiten des Modells gehoeren in den Worker, und dies ist der Fall,
in dem eine Faehigkeit statt eines Mangels dort ankommt.

### Der Worker kennt sein Modell — beim Fernzugang kennt er einen Marktplatz

§3.2 sagt: *„Der Worker ist die einzige Stelle im System, die das Modell hinter seiner
Queue beim Namen kennt."* Bei einem lokalen Modell ist der Name eindeutig. **Bei einem
Zugang wie diesem ist er es nicht:** Am 05.09.2026 lieferten **29 Anbieter** dieselbe
Modell-ID, mit Faktor 8,8 im Eingangspreis, vier Quantisierungen (fp4 bis bf16),
Kontextfenstern von 262.144 bis 1.310.720 — und vier von ihnen fuehren `response_format`
nicht, womit die Fessel aus §3.3 dort ausfiele.

> **Ein Modellname ist beim Fernzugang eine Ausschreibung, keine Wahl.** Wer nur die ID
> setzt, hat dem Zugang die Entscheidung ueberlassen, und zwar pro Aufruf. Zum Namen
> gehoeren deshalb Anbieter, Quantisierung und die Absage an den Rueckfall — sonst
> beschreibt der Worker ein Modell, das er nicht bestellt hat.

Daraus zwei Ergaenzungen zu §3.5 (*vollstaendiger Parameter-Satz wird transportiert*):
Der Satz gilt weiter — **aber ein transportierter Parameter ist noch kein wirksamer.**
Der gewaehlte Anbieter fuehrt `presence_penalty` und `repetition_penalty` nicht; beide
gehen mit und verfallen. Der Worker meldet das und entfernt sie nicht: Was gesendet wurde,
gehoert ins Protokoll, und die Entscheidung darueber liegt beim Anbieter.

### Was der Umbau ueber die Schicht gelernt hat

> **Die Schicht kapselt das Modell — sie kapselte den Prompt nicht.** §3.1 sagt, der
> Konsument kenne keinen Modellnamen. Das stimmte fuer den Aufruf und nicht fuer das
> Material: `PROMPTS` wurde beim Start mit `modell=OLLAMA_MODEL` geladen, also mit dem
> **konfigurierten** GPU-Modell — nicht mit dem, das der `chat`-Worker tatsaechlich
> fuehrt. Solange dort ein Ollama-Backend stand, war beides dasselbe und der Riss
> unsichtbar.
>
> **Beim ersten fremden Rueckhalt haette das neue Modell sieben Prompt-Bloecke bekommen,
> die fuer ein anderes geschrieben sind** — `prompts/gemma4-gpu/` mit Perzeption, Router,
> Salienz und Tribunal. Die Modellebene folgt seit dem 05.09.2026 dem Backend
> (`config.antwortendes_chat_modell()`).
>
> Die Lehre gilt ueber diesen Fall hinaus: **Eine Abstraktion, die den Aufrufpfad
> kapselt, kapselt damit noch nicht alles, was am Modell haengt.** Was nach Modellname
> geschluesselt ist, gehoert an dieselbe Quelle wie die Backend-Wahl — sonst zeigen zwei
> Wege auf zwei Modelle und stimmen nur zufaellig ueberein.
