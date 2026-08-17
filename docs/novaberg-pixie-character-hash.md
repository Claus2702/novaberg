# Novaberg — Pixie-Agent: CharakterAgent (Hash-Destillation)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** CharakterAgent — Charakter-Hash aus KZG/LZG destillieren
**Stand:** 16. August 2026 (**die Auswahl der KZG-Einträge ordnet nach `salienz × zeitgewicht`** statt nach Fundreihenfolge — neuer §4b samt Herleitung der Halbwertszeit; §3.2 nachgezogen. Dabei am Code geprüft und **widerlegt**: Der Kern-Hash liest seit dem 10.08.2026 den **Turn-Wortlaut**, nicht `lzg_knoten` — §3.1 sagte vier Wochen lang das Falsche, ebenso `AGENT.md`. Davor am selben Tag: die getrennten `*_PROMPT_NOVA` sind zu **einem parametrisierten Satz** zusammengezogen, Träger über `_perspektive_aufloesen`; §3.3 nachgezogen). Davor: 1. August 2026 (**beide Räder sind eine Messreihe** — rohe Läufe in `charakter_rad_messung`, gespeichert wird das gewichtete Mittel der letzten fünf Erhebungen, Takt zweimal täglich; §4a. Zuvor: 29. Juli 2026, Chat 117 — die zwei Charakter-Räder und die vollständige Spaltenliste nachgetragen, §2, §4a, §7. ⚠ Fundament-Warnung nach Gewichts-Reset, siehe Kasten in §3. Kern: Chat 79, P7-Update Chat 103)
**Pfad:** novaberg/docs/novaberg-pixie-character-hash.md
**Quellen:** nova-05-m-a.md, nova-04-m-b.md, nova-04-t-b.md

---

## 1. Aufgabe

Der CharakterAgent destilliert Novas verdichtetes Bild ihres Gegenübers — und von sich selbst. Fünf automatisch destillierte Profile fassen zusammen, wer der Mensch ist, was ihn gerade beschäftigt, wie er kommuniziert, was er fühlt und wie die Beziehung zu Nova steht. Der Hash wächst aus der Interaktion — geformt durch das, was im Langzeitgedächtnis überlebt hat.

**Prinzip:** Der Nutzer prägt den Assistenten durch Gespräche, nicht durch Einstellungen.

**Dateien:** `agents/charakter/agent.py`, `destillation.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | `PIXIE_CHARAKTER_PRIORITAET = 0.3` (`config.py`) |
| **Intervall** | `PIXIE_CHARAKTER_INTERVALL_SEKUNDEN = 600` = 10 Minuten (`config.py`) |
| **Bedingung** | NUR bei `hash_dirty:{user_id}` = "1" |
| **LLM-Call** | ~~5 CPU-Calls pro User (einer pro Profil)~~ → **9 pro Subjekt** (5 Profile + 1 Charakter-Rad + 3 Läufe des Initiative-Rads, §4a); für `nova` kommt die Ziel-Destillation dazu. Bei zwei Subjekten je Lauf sind das 19. **Seit 01.08.2026 fallen die vier Rad-Calls nur zweimal täglich an** — außerhalb des Takts sind es 5 je Subjekt |
| **LZG-Limit** | `PIXIE_CHARAKTER_LZG_LIMIT = 50` (max. LZG-Einträge pro Destillation, `config.py`) |
| **KZG-Limit** | `PIXIE_CHARAKTER_KZG_LIMIT = 20` (max. KZG-Einträge für Adaptiv, `config.py`) |
| **context_user** | Iteriert intern über `meister` + `nova` |

Kein dirty Flag → sofort return. Fehlerbehandlung pro Profil (try/except).

---

## 3. Fünf Profile

> **⚠ Fundament-Warnung (Chat 107, 12.07.2026):** Bis zum Gewichts-Reset am 12.07.2026 rechnete die Destillation auf **Zufallsgewichten** — im casing-blinden Embedding-Raum hatten 2910 Skelett-Kollisionen die `gewicht_absolut`-Ordnung bedeutungslos gemacht (EMBEDDING-CASING-BLIND; „Der Nutzer heißt Claus" stand bei 61, „Der Nutzer beobachtet dich" bei 44). Der bestehende `charakter_hash` — insbesondere `kern_hash` und `emotions_profil` — ist auf diesem Fundament entstanden und muss neu destilliert werden. **Der Reset stößt das nicht automatisch an:** Die Destillation läuft nur bei `hash_dirty`, und die Reset-/Re-Embed-Tools setzen das Flag nicht — offener Punkt CHARHASH-RESET-TRIGGER-FEHLT (bugs.md).

### 3.1 Kern-Hash (Turn-Wortlaut, Monate)

**Frage:** Wer ist dieser Mensch?

~~**Quelle:** Langzeitgedächtnis (`lzg_knoten`, PostgreSQL), selektiert und gewichtet nach Anker-Stärke `gewicht_absolut` (nicht nach Präsenz/Decay). Seit Synapsen P7 (Chat 103).~~ → **Am 16.08.2026 gegen den Code geprüft und widerlegt.** `agent.py` übergibt an `kern_hash_destillieren` das Ergebnis von `_turns_laden` — **40 Rohturns aus `pipeline_log`** (`art='turn_roh'`), nicht die Langzeit-Knoten. Die Umstellung ist vom 10.08.2026 und im Code begründet: `KERN_HASH_PROMPT` fragt nach dem **WIE** jemand spricht, und die Knoten tragen das WORÜBER — aus einem *„jo"* ist dort *„Der Nutzer weiss nicht, was er hier tun soll"* geworden. Dieses Dokument war bis zum 16.08.2026 nicht nachgezogen; dieselbe falsche Quelle stand in `server/agents/charakter/AGENT.md`.

**Stabilität:** Verändert sich langsam — *als Absicht*. Gemessen am 16.08.2026 liegt dem Profil ein Fenster von 40 Turns zugrunde.

> **Nur Begegnungen zählen — seit dem 16.08.2026.** `_turns_laden` verlangt `herkunft='nutzer_turn'`. Ein **eigener Impuls hat kein Gegenüber**, und beide Räder messen eine Haltung *gegenüber* jemandem; er trägt deshalb zu keinem der beiden Profile bei.
>
> Der Anlass war ein Defekt: Ein Impuls legt seinen Text in dasselbe Feld `user_prompt` wie eine Nutzeräußerung. Ungefiltert wurden die eigenen Gedanken der Figur als Äußerungen des Menschen gelesen — **25 der 40 Turns, 95,4 % des Materials**; mit der Antwortseite entstand sein Profil aus einem Material, das zu **98 %** von ihr stammte. Das erklärt die gemessene Spiegelung beider Räder (mittlere Abweichung **0,0202** über zwölf Speichen) und ihr Ausbleiben bei Paaren ohne Impulse (0,128 bis 0,533).
>
> **Was der Filter nicht behebt:** Auch danach bleibt das Material zu **90,5 %** von der Figur (4404 gegen 41 791 Zeichen, Faktor 9,5) — der Median einer Nutzeräußerung liegt bei 109 Zeichen, der einer Antwort bei 1055. Beide Perspektiven lesen weiterhin denselben Text; unterschieden wird nur die Anweisung, und die ist **1,4 % des Prompts**. Dazu kommt eine Asymmetrie der Beschriftung: Der Träger *„Nova"* steht 40-mal als Sprecherlabel im Material, der Träger *„der Nutzer"* **null-mal** — der Mensch erscheint dort nur als *„Gegenueber"*. Beides steht offen in der Fundliste.

**Beispiel:**
> "Der Nutzer ist ein analytischer Denker, der komplexe Themen ganzheitlich betrachtet und dabei intuitiv von der Sachebene zur emotionalen Bedeutung wechselt. Ihm ist Wohlbefinden und Qualität wichtiger als reine Effizienz. Er kommuniziert direkt, schätzt fundierte Zwischenbestätigungen und hat ein starkes Interesse an der Schnittstelle von Technologie und menschlichem Erleben."

### 3.2 Adaptiv-Hash (KZG, Tage)

**Frage:** Was beschäftigt ihn gerade?
**Quelle:** Kurzzeitgedächtnis (Redis) — die `PIXIE_CHARAKTER_KZG_LIMIT` Einträge mit der höchsten **effektiven Salienz** (§4b).
**Stabilität:** Wechselt mit Themen.

> **Bis zum 16.08.2026 wählte diese Quelle nicht aus, sie griff zu.** `_kzg_laden` nahm die ersten zwanzig, die `scan_iter` lieferte, und brach ab. `SCAN` sagt keine Reihenfolge zu: Gemessen am produktiven Paar lagen die genommenen zwanzig auf den **Zeiträngen 245 bis 2162 von 2202**, Median 1284, im Mittel **18 Tage** alt — bei einem Profil, dessen Frage *„gerade"* lautet. Zwölf der neunzehn im Prompt trugen ein Zeitgewicht unter 0,09 und standen trotzdem mit vollem Text da.

**Beispiel:**
> "Quantencomputing, Beziehung zu Nova, Abnehmen, Eis essen."

### 3.3 Intentions-Profil (Kommunikation)

**Frage:** Wie kommuniziert er?
**Quelle:** Aggregiert aus Session-Annotationen (Intentionen + Modus + Stil).
**Drei Dimensionen:** Was will er typischerweise (Intentionen)? In welchem Register denkt er (Gesprächsmodus)? Wie drückt er sich aus (Sprachstil)?

**Beispiel:**
> "Der Nutzer kommuniziert sachlich-strukturiert mit vollständigen Sätzen und korrekter Zeichensetzung. Er bevorzugt Fachgespräche und philosophischen Austausch, stellt tiefe Fragen und erwartet fundierte Antworten."

### 3.4 Emotions-Profil (Grundtendenz + Volatilität)

**Frage:** Was fühlt er typischerweise?
**Zwei Dimensionen:** Grundtendenz (dominante Emotionen über Monate) und Volatilität (wie sprunghaft ist er?).

**Beispiel (stabil):**
> "Grundlegend zuversichtlich-neugierig mit Begeisterungs-Peaks. Emotional stabil — bei Belastung baut sich Frustration langsam auf statt zu explodieren."

**Beispiel (volatil):**
> "Emotional lebhaft mit häufigen Richtungswechseln. Schnelle Umschwünge zwischen Begeisterung und Frustration. Braucht bei Absturz schnelle Anerkennung."

### 3.5 Beziehungs-Profil (Vertrauensniveau, Dynamik)

**Frage:** Wie steht er zu Nova?
**Quelle:** Aggregiert aus Beziehungsdynamik-Annotationen.
**Wichtig:** Stil ist nicht Beziehung. "Formell" ist Kommunikation, nicht Distanz.

**Beispiel:**
> "Vertrauensvoll, fast freundschaftlich, warmherzig, humorvoll."

---

## 4. Destillation

Fünf LLM-Calls auf dem CPU-Modell für die Profile, danach die beiden Räder (§4a). `hash_dirty:{user_id}` wird für beide User geprüft.

```
hash_dirty = TRUE in Redis?
    │
    Ja → lzg_knoten laden (aktiv = TRUE, sortiert nach gewicht_absolut DESC)
    │    Turn-Wortlaut laden (pipeline_log, 40 Turns — für den Kern, §3.1)
    │    KZG-Einträge wählen (höchste salienz × zeitgewicht, §4b)
    │
    ▼
    5 LLM-Calls (CPU-Modell) → 5 Profile generieren
    │
    ▼
    Charakter-Rad (1 Call) und Initiative-Rad (3 Calls) auf dem Profiltext
    │
    ▼
    charakter_hash-Tabelle aktualisieren (INSERT oder UPDATE)
    │
    ▼
    hash_dirty = FALSE
```

Jedes Profil ist Fließtext. Keine Listen, keine Stichworte — natürlichsprachliche Beschreibungen, die direkt in den Responder-Prompt einfließen.

> **Der Kern trägt seit dem 11.08.2026 keinen Deckel mehr.** Bis dahin verlangten alle fünf Prompts „kompakt … in 2–5 Sätzen" — eine Vorgabe aus der Zeit knapper Kontextfenster. Gemessen über zwei Personen mit je drei Läufen über die ganze Kette: **Die Streuung des daraus gelesenen Rades fällt um das Vierfache** (Spanne 0,2510 → 0,0630 und 0,1040 → 0,0040), der Faktor bleibt (−0,024). Der Deckel kaufte nichts und war die lauteste Stufe der Kette. Live gemessen am 12.08.2026 am produktiven Paar: Kern **916 → 3578 Zeichen**, Aufruf 11 min 35 s bei 26 879 Token — beides jenseits der alten Frist von 300 s und des alten Token-Deckels von 2048, die deshalb mitgehoben wurden (1800 s, 8192).
>
> **Die vier übrigen Profile bleiben gedeckelt** (adaptiv, Intention, Emotion, Beziehung). Jedes hat einen eigenen Abnehmer, und gemessen ist bisher nur der Kern — Backlog `VERDICHTUNG-UEBRIGE-VIER-PROMPTS`.

~~**Getrennte Prompts (seit Chat 45):** Die Destillation verwendet fuer user_id="nova" eigene Prompt-Texte. Alle vier Nova-Prompts haben die gleiche Qualitaetsstruktur wie die User-Prompts — identische Fokus-Dimensionen, Beispiele und Anleitungen, nur mit Nova-Rahmung ("Nova ist..." statt "Der Nutzer ist..."). Die User-Destillation (meister) bleibt unveraendert.~~

→ **Am 16.08.2026 gegen den Code geprueft: Die Verdopplung ist aufgeloest.** Es gibt keine `*_PROMPT_NOVA` mehr — weder die vier genannten noch sonst eine. An ihre Stelle ist **ein Satz parametrisierter Prompts** getreten, dessen Traeger zur Laufzeit eingesetzt wird.

**Die Bauart** (`agents/charakter/destillation.py`): Jeder Prompt traegt die Platzhalter `{traeger}`, `{traeger_gen}` und `{perspektive}`. `_perspektive_aufloesen(user_id)` liefert die passenden Formen — fuer `ASSISTANT_USER_ID` den Namen aus `ASSISTANT_NAME` samt Genitiv ueber `_genitiv_bilden`, sonst *der Nutzer* / *des Nutzers*.

**Zwei Eigenschaften, die die alte Fassung nicht hatte** und die den Umbau erklaeren:

- **Der Name steht nicht mehr im Prompt.** Die alte Fassung schrieb *Nova ist…* woertlich in vier Texte. Heute kommt er aus `ASSISTANT_NAME`; eine Umbenennung der Figur beruehrt keinen Prompt.
- **Eine Aenderung wirkt auf beide Seiten.** Bei zwei Saetzen musste jede Schaerfung zweimal gepflegt werden, und genau daran laufen sie auseinander.

**Die Prompts, die es heute gibt** — fuenf, nicht vier; `EMOTIONS_PROFIL_PROMPT` fehlte in der Aufzaehlung oben:

- `KERN_HASH_PROMPT`: Tiefenwerte, dauerhafte Interessen, Denkweise
- `ADAPTIVE_HASH_PROMPT`: Zeitgewichtung [AKUT/PHASE/TREND], aktuelle Themen
- `INTENTIONS_PROFIL_PROMPT`: drei Aspekte (STIL/MODUS/INTENTIONEN) + Beispiel
- `EMOTIONS_PROFIL_PROMPT`
- `BEZIEHUNGS_PROFIL_PROMPT`: vier Dimensionen (Naehe/Hierarchie/Vertrauen/Ton)

---

## 4a. Die zwei Charakter-Räder

Beide laufen **nach** den fünf Profilen und lesen deren Ergebnis, nicht erneut das Gedächtnis: Ein Rad ist eine Eigenschaft des destillierten Charakters, keine zweite Beobachtung der Rohdaten. Beide speichern neben dem Zahlenwert das Rad selbst, seine Herkunft und den Zeitpunkt — vier Spalten je Rad (§7).

| | **Charakter-Rad** (Chat 111) | **Initiative-Rad** (Chat 116) |
|---|---|---|
| Frage | Wie sehr gilt Nova das Gegenüber überhaupt? | Überlässt sie im Gespräch die Führung oder behält sie sie? |
| Speichen | 12 (6 hoch, 6 runter) | 10 (5 hoch, 5 runter) |
| Nabe | 0.9, Grenzen 0.5–1.5 | 0.0, Spanne ±0.25 |
| Erhebungen je Messung | 1 | **3, Median** |
| Takt | **zweimal täglich** (seit 01.08.2026) | **zweimal täglich** |
| Gespeicherter Wert | **gewichtetes Mittel der letzten 5 Erhebungen** | ebenso |
| Feld | `nutzer_gewichtung` | `initiative_versatz` |
| Verbraucher | Salienz: `max(salienz_human × nutzer_gewichtung, salienz_charakter)` | GV-Achse I: verschiebt den Rohwert vor der Schwelle |
| Beschreibung | `novaberg-salienz-berechnung_k.md` | `novaberg-gv-initiative_k.md` §6, `novaberg-gv-initiative.md` |

**Warum zwei Räder und nicht eines.** Vier der zwölf Speichen des älteren Rads berühren Führen und Folgen — sein Ergebnis bündelt sie aber mit Wissbegier, Pflichtbewusstsein und Aufmerksamkeit, die mit der Frage nichts zu tun haben. Ein abgeleiteter Wert wäre die Summe zweier Fragen gewesen.

**Die Entwurfsregel des zweiten Rads: Handlung statt Haltung.** Jede Speiche wird über eine *beobachtbare Gesprächshandlung* beschrieben, nicht über eine Disposition. Das ältere Rad beschreibt Treue als „die Anliegen des anderen voranstellen" — eine Haltung, die ein Modell als allgemeine Wärme liest. Am selben Profiltext gemessen: Das ältere Rad füllte 3 von 12 Speichen und auf der Abwendungsseite keine einzige, das neue 6 von 10 und auf beiden Seiten etwas.

### Seit 01.08.2026: beide Räder sind eine Messreihe

Bis dahin war der gespeicherte Wert **eine einzelne Erhebung**, beim nächsten Lauf überschrieben. Am 31.07. wechselte Novas Zuwendungsfaktor binnen zwei Stunden von 1.215 auf 0.980 — und ob das Bewegung oder Rauschen war, ließ sich aus den Daten nicht beantworten, weil die vorige Erhebung nicht mehr existierte. Das ist Regel (1) der Konvention über abgeleitete Werte: **Speichere die Eingaben, nicht nur das Ergebnis.**

- **Die rohen Läufe liegen in `charakter_rad_messung`** — eine Zeile je Lauf, mit eigenem Zeitstempel, Modell, Temperatur und der Prüfsumme des gelesenen Profiltexts. Gleiche Prüfsumme mit anderem Ergebnis ist Verfahrensstreuung, andere Prüfsumme kann Bewegung sein.
- **Der gelesene Wert in `charakter_hash` ist ihr gewichtetes Mittel** über die letzten fünf Erhebungen und wird daraus jederzeit neu berechnet. Ein Mittel wird **nie** als Messung zurückgeschrieben — das wäre der Akkumulator, an dem der Ziel-Decay scheiterte.
- **Der Takt ist fest**, zweimal täglich, geprüft vom Agenten selbst. Fest, damit Rang und Zeit dasselbe bedeuten: Die Gewichtskurve verfällt über den Rang.
- **Zwei Stufen, zwei Streuungen.** Die Läufe einer Erhebung werden gleichgewichtet gemittelt — sie liegen Sekunden auseinander und lesen denselben Text. Über die Erhebungen greift der Verfall.

**Die jüngste Messung trägt 41 %** statt 100 %; ein echter Umschwung ist nach zwei Tagen zu 87 % angekommen. Vollständig in `novaberg-charakter-rad-messreihe_k.md`.

> **Das Argument „gespeichert wird ein echtes Rad" ist damit hinfällig** — aber nur seine erste Hälfte. Es galt, solange die Einzelläufe nirgends erhalten blieben; sie liegen jetzt in der Messreihe. Die zweite Hälfte gilt weiter: `Rad × Züge = Faktor` bleibt von Hand nachrechenbar, auch mit 0.67.

**Warum das Initiative-Rad dreimal erhoben wird.** Zwei Läufe gegen denselben Text bei Temperatur 0.2 unterschieden sich um ein Fünftel der halben Spanne. Anders als ein Wert pro Turn wird dieser einmal geschrieben und steht bis zur nächsten Destillation — ein einzelner Ausreißer hätte ihn für Tage festgesetzt. **Gespeichert wird das Rad des Median-Laufs**, kein gemitteltes: Ein Mittel über drei Räder ergäbe Bewertungen, die kein Lauf je vergeben hat, und der Wert wäre von Hand nicht mehr nachrechenbar. Die Streuung reist als Metadatum mit.

**`_quelle` trennt `default` von `destilliert`.** Ein Versatz von 0.0, weil sich zehn Speichen aufheben, ist etwas anderes als 0.0, weil das Modell in keiner etwas erkannt hat. Ohne das Feld wäre dies die vierte Stelle im System, an der ein Ausfallwert wie ein Messergebnis aussieht (`novaberg-lesson_l_default-wie-fehlschlag.md`). Scheitert eine Erhebung — leerer Profiltext, unlesbares JSON, unvollständiges Rad —, bleibt der bestehende Wert stehen und eine `error`-Zeile sagt es; geschrieben wird nie ein erfundener.

---

**Gewichtung:** Hohe Anker-Stärken (`gewicht_absolut`) dominieren das Profil — was sich als dauerhaft prägend verankert hat, nicht was gerade präsent ist. `aktiv = TRUE` bleibt als Gate: inaktive (decay-deaktivierte) Knoten werden nicht geladen. Präsenz gated, Anker-Stärke ranked. Angezeigtes Gewicht im Kern-/Emotions-Prompt ist `gewicht_absolut` direkt (kein Read-Time-Decay mehr; `effektives_gewicht_berechnen` an diesen Stellen entfernt).

---

## 4b. Die Auswahl der KZG-Einträge

**Gewählt werden die stärksten, nicht die ersten** — seit dem 16.08.2026. Die Größe ist die **effektive Salienz**:

```
effektive_salienz = salienz × zeitgewicht(alter_in_tagen)
zeitgewicht(t)    = exp(-ln2 / T · t)      T = 1,7 Tage
```

Die Form ist die kanonische Verfallsform des Systems — dieselbe wie in `memory/ziele.py` und `memory/lzg_knoten.py`. Sie löst drei aneinandergesetzte Stücke ab (konstant, linear, exponentiell), die bei genau einem Tag von 1,00 auf 0,80 sprangen: Zwei Einträge, die eine Minute trennte, unterschieden sich um ein Fünftel.

### Warum die Halbwertszeit 1,7 Tage ist

**In einer Auswahl wirkt ein Zeitfaktor nur über die Ordnung, nie über den Betrag** — ein Faktor auf alle Einträge ändert die Rangfolge nicht. Die Halbwertszeit steuert deshalb genau eine Größe: wieviel Salienz-Vorsprung ein älterer Eintrag braucht, um einen jüngeren zu überholen, nämlich `2^(Δt/T)`.

Gemessen am 16.08.2026 spannt die KZG-Salienz nur von 0,67 bis 1,00 (Faktor 1,49), und **87 % der Einträge liegen über 0,90** (Faktor 1,11). Bei `T = 1,7` — der gemessenen mittleren Gesprächslücke des produktiven Paares — ergibt das ein Wirkfenster von **0,98 Tagen**: Innerhalb einer Gesprächssitzung ordnet die Salienz, zwischen Sitzungen die Zeit.

| T | Wirkfenster der Salienz |
|---|---|
| 1,0 Tag | 0,58 Tage |
| **1,7 Tage** | **0,98 Tage** |
| 3,0 Tage | 1,73 Tage |
| 7,0 Tage | 4,03 Tage |

Bei `T = 7` dürfte die Salienz über vier Tage hinweg umsortieren — dann zieht sie wieder Wochen altes Material nach oben. Die Nachmessvorschrift für den Stellwert steht im Kommentar bei `PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE`.

### Warum die volle Ordnung billiger ist als die alte Willkür

Die Schlüssel tragen ihre Zeitmarke (`kzg:{user}:{character}:{ms}`) — sortieren kostet keinen Redis-Zugriff. Absteigend gelesen fällt das Zeitgewicht monoton; sobald es unter die schwächste bereits gewählte effektive Salienz sinkt, **kann kein älterer Eintrag mehr aufholen**, denn `salienz ≤ 1` und damit `salienz × gewicht ≤ gewicht`. Ab da wird nicht weitergelesen.

**Gemessen am 16.08.2026:** 28 gelesene statt 2202 durchsuchter Schlüssel, mittleres Alter der Auswahl **18,0 → 2,06 Tage**, Laufzeit 30 ms.

### Zwei Verwerfungen, die jetzt zählen

Ein Eintrag ohne Themenfeld belegt keinen der Plätze — die Destillation verwirft ihn ohnehin, und unter den jüngsten `assistant`-Einträgen tragen nur **70 %** eines. Ebenso die Ladegrenze von 30 Tagen: Sie war bis dahin eine reine Gewichtskante *nach* dem Laden. Beide Pfade waren stille `continue`; beide stehen jetzt mit ihrer Zahl in der Logzeile.

**Das Beziehungsprofil erbt dieselbe Auswahl** (`agent.py` reicht `kzg_eintraege` weiter). Es verliert durch den Themenfilter nichts, weil es den Wortlaut über `_key` liest, nicht die Themen.

---

## 5. Profil-Pipeline

Die Profile entstehen durch eine mehrstufige Pipeline:

```
Erfassung (Perzeption)
  → intent, tone, emotion, arousal, sprach_stil, beziehungs_dynamik
    │
    ▼
Speicherung (Session → KZG → LZG)
  → 9 Felder pro Turn annotiert, über Salienz ins KZG, über Promotion ins LZG
    │
    ▼
Destillation (Pixie CharakterAgent)
  → 5 Profile aus KZG/LZG-Daten destilliert
    │
    ▼
Nutzung (Enricher → Responder)
  → Hash in System-Prompt injiziert
```

---

## 6. Beide User

Der CharakterAgent iteriert intern über `meister` und `nova`:

| | User (Meister) | Nova |
|---|----------------|------|
| Kern-Hash | Wer ist der Mensch? | Wer ist Nova geworden? |
| Adaptiv-Hash | Was beschäftigt ihn? | Was hat Pixie zuletzt erforscht? |
| Quelle KZG | `kzg:meister:*` | `kzg:nova:*` |
| Quelle LZG | `langzeitgedaechtnis` (user_id=meister) | `langzeitgedaechtnis` (user_id=nova) |

Nova bildet durch ihre eigene KZG-LZG-Pipeline und die Hash-Destillation ein eigenes Selbstbild. Gleicher Mechanismus, getrennte Daten.

### Paar-Schema seit Chat 79

Seit Chat 79 iteriert der CharakterAgent nur noch das kanonische Paar
(user_id, ASSISTANT_USER_ID). Die Perspektiv-Unterscheidung laeuft ueber
das `beobachter`-Feld in `_kzg_laden()`:

- User-Profil: beobachter="user" (Meisters Beitraege)
- Nova-Profil: beobachter="assistant" (Novas Beobachtungen)

Die LZG-Lesepfade (_lzg_kern_laden, _lzg_intentionen_laden,
_lzg_emotionen_laden) filtern seit Chat 79 ebenfalls auf
(kanon_user_id, kanon_character_id, beobachter) statt auf subjekt_user_id
(CHAR-LZG-LEAK Fix).

---

## 7. DB-Schema

**Zwei Tabellen seit dem 01.08.2026.** `charakter_hash` hält den gelesenen Zustand, `charakter_rad_messung` die rohen Erhebungen, aus denen er entsteht.

### `charakter_rad_messung` (seit 01.08.2026)

Eine Zeile je **Lauf**, nicht je Erhebung. `erhebung_id` klammert die Läufe einer Messung, `lauf` nummeriert sie.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id`, `character_id` | TEXT | das kanonische Paar, wie in `charakter_hash` |
| `rad_art` | TEXT | `zuwendung` oder `initiative` |
| `erhebung_id` | UUID | klammert die Läufe einer Messung |
| `lauf` | SMALLINT | Nummer innerhalb der Erhebung |
| `gemessen_am` | TIMESTAMPTZ | **eigener Zeitstempel**, nur mit dieser Zeile geschrieben |
| `speichen` | JSONB | die rohen Werte dieses Laufs |
| `faktor` | DOUBLE PRECISION | der Skalar dieses Laufs — zusätzlich, nicht stattdessen |
| `modell`, `temperatur` | TEXT / DOUBLE | der Maßstab, mit dem gemessen wurde |
| `quelle_pruefsumme`, `quelle_zeichen` | TEXT / INTEGER | welcher Profiltext gelesen wurde |

Ablage: `server/agents/charakter/init.sql`. Zwei Indizes: die Reihe je Rad (`user_id, character_id, rad_art, gemessen_am DESC`) und die Läufe je Erhebung.

### `charakter_hash`

Zwanzig Spalten, PRIMARY KEY `(user_id, character_id)`. ~~PRIMARY KEY `user_id`~~ — überholt seit dem Paar-Schema (Chat 79): Eine Zeile gilt für ein *Paar*, nicht für einen User.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `user_id` | TEXT | Teil des PK — Subjekt der Zeile (`meister` oder `nova`) |
| `character_id` | TEXT | Teil des PK — das Gegenüber (`novaberg-convention-paar-schema.md`) |
| `kern_hash` | TEXT | Grundpersönlichkeit (aus LZG) |
| `adaptive_hash` | TEXT | Aktuelle Phase (aus KZG) |
| `kern_aktualisiert_am` | TIMESTAMPTZ | Letzte Kern-Destillation |
| `adaptive_aktualisiert_am` | TIMESTAMPTZ | Letzte Adaptiv-Destillation |
| `intentions_profil` | TEXT | Kommunikationsmuster (aggregiert) |
| `intentions_aktualisiert_am` | TIMESTAMPTZ | Letzte Intentions-Destillation |
| `emotions_profil` | TEXT | Emotionale Grundtendenz (aggregiert) |
| `emotions_aktualisiert_am` | TIMESTAMPTZ | Letzte Emotions-Destillation |
| `beziehungsprofil` | TEXT | Beziehungsdynamik (aggregiert) |
| `beziehung_aktualisiert_am` | TIMESTAMPTZ | Letzte Beziehungs-Destillation |
| `nutzer_gewichtung` | DOUBLE PRECISION | Charakter-Rad, Default 0.9 (§4a) |
| `nutzer_gewichtung_quelle` | TEXT | `default` oder `destilliert` |
| `nutzer_gewichtung_rad` | TEXT | Die zwölf Speichen als JSON — der Wert ist daraus nachrechenbar |
| `nutzer_gewichtung_am` | TIMESTAMPTZ | Zeitpunkt der Erhebung (nullable: nie erhoben) |
| `initiative_versatz` | DOUBLE PRECISION | Initiative-Rad, Default 0.0 (§4a) |
| `initiative_versatz_quelle` | TEXT | `default` oder `destilliert` |
| `initiative_versatz_rad` | TEXT | Die zehn Speichen des **Median-Laufs** als JSON, mit der Streuung als Metadatum |
| `initiative_versatz_am` | TIMESTAMPTZ | Zeitpunkt der Erhebung (nullable: nie erhoben) |

Kein Auto-Increment — eine Zeile pro Paar. Der Hash wird nicht versioniert, sondern überschrieben. Die Historie lebt im LZG, nicht im Hash.

**Die beiden `_rad`-Spalten sind der Grund, warum ein Wert prüfbar bleibt.** Ohne sie stünde eine Zahl da, die niemand mehr aufschlüsseln kann; mit ihnen lässt sich jede Erhebung von Hand nachrechnen und im Client als Radar zeigen (Backlog, „Charakter-Räder im Client").

---

## 8. Nutzung

### Enricher

Lädt den Hash in zwei Formaten:
- Als String (`charakter_hash_retrieve`) → fließt in den `memory_context`
- Als Dict (`charakter_hash_retrieve_dict`) → fünf Felder: `kern`, `adaptiv`, `beziehungsprofil`, `intentions_profil`, `emotions_profil` (erweitert in Chat 45 und Chat 52)

### Responder — User-Hash

User-Profil wird über `[GEDAECHTNIS]` als `[Charakter]`-Eintrag in den System-Prompt injiziert. Kein eigener `[CHARAKTER]`-Block mehr (seit Chat 45, RESP-CHAR1).

### Responder — Nova-Hash

Der Enricher lädt Novas eigenen Hash. Der Responder injiziert fünf Profile direkt in `[IDENTITAET]`:

```
Schichten in [IDENTITAET] (Primacy-Reihenfolge):
1. "Du bist Nova." (Fundament)
2. Charakter-Anweisung (Saatgut, vom User)
3. "Deine gewachsene Persoenlichkeit:" + nova_kern
4. "Was dich gerade beschaeftigt:" + nova_adaptiv
5. "Deine emotionale Grundstimmung:" + nova_emotions (seit Chat 52)
6. "Deine Art zu kommunizieren:" + nova_intentionen
7. "So siehst du deinen Nutzer:" + nova_beziehung
8. Datum + Rollenklarheit + Web-Zugriff (Recency)
```

Alles Nova-bezogene in einem Block. Der separate `[CHARAKTER]`-Block wurde entfernt — er vermischte Nova-Selbstbild mit User-Beschreibung und verwendete widersprüchliche Labels.

---

Verwandte Dokumente:
- Die zwei Räder: `novaberg-salienz-berechnung_k.md` (Charakter-Rad), `novaberg-gv-initiative.md` und `novaberg-gv-initiative_k.md` §6 (Initiative-Rad)
- DecayAgent (Ebbinghaus-Gewichtung): `novaberg-pixie-decay.md`
- PromotionAgent (hash_dirty-Setter): `novaberg-pixie-promotion.md`
- KZG-Agent (Datenquelle Adaptiv): `novaberg-pixie-kzg.md`
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
