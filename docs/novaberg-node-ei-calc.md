# Novaberg — Node: EI-Calc

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Node-Referenz EI-Calc (Emotionale Intelligenz — Berechnungsschicht)
**Stand:** 28. Juli 2026, Chat 114 (Raumzug als zweite Kraft neben der Empathie)
**Pfad:** novaberg/docs/novaberg-node-ei-calc.md
**Quellen:** Chat 58 (Konzept-Split), Chat 59 (Implementierung)
**Datei:** `graph/nodes/ei_calc.py`

---

## 1. Aufgabe

Der EI-Calc-Node ist die Berechnungsschicht der emotionalen Intelligenz. Er berechnet pro Aufruf **entweder** die User-EI (Pfad 1, HumanGraph) **oder** Novas Empathie-modulierten Emotionsstrang (Pfad 2, CharacterGraph). Welcher Block läuft, entscheidet `state["ei_calc_rolle"]`.

Eingangsdaten: die Session-Turns (`raw_turns`) und die Perzeptionsergebnisse aus der `Emotion`-Klasse (`state["external"].emotion` für den User-Pfad, `state["internal"].emotion` als Vorzustand für den Character-Pfad). Die Turn-Beschaffung unterscheidet sich je Graph: Im HumanGraph liefert sie der Enricher über `state["raw_turns"]` (er läuft davor); im CharacterGraph lädt `_ei_calc_character` sie **selbst** aus Redis (`session_turns_retrieve`, seit a5acc7d/Chat 105) — der Enricher läuft dort erst danach.

**Kein LLM-Call.** Ein Redis-Read (Session-Turns) auf der Character-Seite; sonst reine Python-Vektorarithmetik. Sub-100ms, deterministisch, reproduzierbar.

---

## Akkumulation und Glättung

### `inject_current: bool` Parameter

Funktionen `_emotions_verlauf_berechnen()` und `_emotions_vektor_bestimmen()` haben einen Parameter `inject_current`:

- **`True` (Default, User-Pfad):** Der aktuelle User-Turn wird als „virtueller Turn 0" in den Verlauf eingefügt, bevor der Decay rückwärts läuft. So zählt die frische User-Emotion voll.
- **`False` (Character-Pfad):** Novas aktuelle Emotion ist noch nicht perzipiert (das passiert erst am Ende des CharacterGraphs durch `perzeption_assistant`). Der Verlauf wird nur aus historischen Nova-Turns berechnet — die Empathie-Modulation ersetzt die Rolle des „aktuellen Turns".

### Drei biologische Mechanismen (seit Chat 61)

Die Akkumulation folgt drei biologisch motivierten Mechanismen:

1. **Aktueller Turn voll, Historie als Echo (15%):** Der neueste Turn (i=0) zählt mit seinem vollen Decay-Wert. Ältere Turns ziehen nur mit 15% ihres Decay-Werts ein. Modelliert **affective carryover** (Russell & Carroll 1999, Davidson 1998) — Emotionen hallen nach, übertönen aber nicht den aktuellen Zustand.

2. **Harter Cap bei 2.5:** Akkumulierte Rohwerte werden auf maximal 2.5 beschränkt. Verhindert unbegrenztes Aufstauen über viele wiederholte Turns.

3. **sin^0.5-Glättungskurve:** Der gekappte Rohwert wird auf den Anzeigebereich [0, 1] abgebildet über `sin(rohwert / MAXIMUM × π/2)^0.5`. Die Kurve ist steil unten (selbst kleine Andeutungen werden sichtbar: 0.1 → 0.25), sanft oben (einzelner starker Turn: 1.0 → 0.77, mehrere Turns bauen auf), mathematisch exakt 1.0 am Cap. Modelliert konversationelle Emotion — eine Emotion baut sich durch Wiederholung auf, statt sofort voll auszuschlagen.

Die Funktion ist in `server/ei/berechnung.py` als `_glaettung()` implementiert. Config-Parameter: `EMOTION_HISTORIEN_GEWICHT = 0.15`, `EMOTION_GLAETTUNGS_MAXIMUM = 2.5`.

---

## 2. Position im Graph

```
HumanGraph (Pfad 1, 5 Nodes):
perzeption → enricher → ▶ ei_calc ◀ → salience → dispatcher

CharacterGraph (Pfad 2, 17 Nodes):
db_zugriff → ▶ ei_calc ◀ → enricher → emotionale_gravitation → reducer → router → planner → agent_dispatch
          → gv_node → responder → thinker → tribunal → evaluate → corrector
          → perzeption_assistant → ei_calc_persist → salience → dispatcher
```

**HumanGraph:** Dritter Node, nach `perzeption → enricher`. Berechnet den User-Pfad.

**CharacterGraph:** Zweiter Node, nach `db_zugriff`. Berechnet den Character-Pfad.

**Reihenfolge-Logik (Phase 2, präzisiert Chat 105):** Im CharacterGraph läuft EI-Calc **vor** dem Enricher — bewusst (fe1bb5f): Der Enricher liest `nova_emotions_verlauf`, das EI-Calc erzeugt; die Erinnerungs-Auswahl (Spreading-Sektor-Faktor, `enricher.py` §8.4-Pfad) soll auf Novas empathie-modifizierter Lage stehen, nicht auf der des Vorturns. Die Abhängigkeit besteht damit in **beide** Richtungen: EI-Calc braucht Session-Turns, der Enricher braucht EI-Calc-Output. Aufgelöst wird sie, indem der Konsument selbst lädt — nicht durch Kantentausch.

**Konsequenz für raw_turns (seit a5acc7d):** Im CG liegt `state["raw_turns"]` zum EI-Calc-Zeitpunkt noch leer (create_state-Default). `_ei_calc_character` lädt die Session-Turns deshalb selbst aus Redis (`session_turns_retrieve`), mit EVA-Disziplin: Paar-Check (user_id/character_id vorhanden?), Redis-Read im try/except, bei Fehler `logger.error` mit Kontext und Weiterrechnen mit leerer Liste — der Turn stirbt nicht am fehlenden Emotionsverlauf, aber der Ausfall ist laut. Die geladene Liste bleibt **lokal**: `state["raw_turns"]` gehört weiterhin dem Enricher, kein zweiter Schreiber. `_ei_calc_user` (HG) liest unverändert aus `state["raw_turns"]`.

**Input:** State mit Perzeptionsergebnissen (Emotion, Arousal, Modus, Stil, Intent, Tone, Beziehungsdynamik) in den Personality-Klassen; Session-Turns je Graph wie oben (HG: `state["raw_turns"]` vom Enricher, CG: eigener Redis-Read).

**Output:** Pro Rolle entweder die User-Felder (`state["external"].emotion.emotions_vector`, `.mode`, `.language_style`, plus `state["emotions_verlauf"]`) oder die Nova-Felder (`state["internal"].emotion.emotions_vector`, plus `state["nova_emotions_verlauf"]`, `state["nova_emotion_konflikt"]`).

---

## 3. Zwei Berechnungsblöcke

### 3.1 User-EI (Kraft 1)

Die bisherigen Enricher-Berechnungen sind vollständig nach EI-Calc gewandert (Chat 59, AP2). Sechs Schritte, alle auf den User-Turns:

1. **Emotions-Verlauf** — `_emotions_verlauf_berechnen(raw_turns, current_emotion, current_arousal, rolle="user")`
   Logarithmischer Decay über alle User-Turns, Turn 0 aus Perzeption, sektorabhängige Normalisierung.

2. **Emotions-Vektor** — `stimmungsvektor_bestimmen(raw_turns, current_emotion, current_arousal, rolle="user")`. Die **Erregung wird mitgereicht**, seit der Intensitaetsanstieg an ihr gemessen wird; ohne sie faellt der eingespeiste Turn auf den Namens-Rueckfall. Neben `emotions_vector` wird `emotions_vector_quelle` gesetzt — die **Grundlage** der Richtung (`gemessen`, `gleichstand`, `zu_wenig_turns`), die als `richtung_quelle` in die Landschaftszeile reist.
   Einer der 9 Vektoren (absturz, spirale, stabilisierung, erholung, aufbluehen, eskalation, abkuehlung, einbruch, plateau).

3. **EI-Arousal** — `_ei_arousal_berechnen(current_arousal, beziehungs_dynamik, intent, tone)`
   Gewichteter Kombinationsfaktor (Dynamik 0.40, Intent 0.35, Tone 0.25) verstärkt/dämpft den Roh-Arousal.

4. **Modus-Plausibilität** — `_modus_plausibilitaet(current_emotion, ei_arousal, perzeption_modus)`
   Matrix-Lookup korrigiert den Perzeption-Modus. Negative Emotion + hoher EI-Arousal → `emotional` erzwungen. Neutrale Emotion → `emotional` blockiert.

5. **Sprachstil-Erkennung** — `_sprach_stil_erkennen(raw_turns, charakter_hash, rolle="user")`
   Per-Turn Feature-Scoring über 13 Merkmale. `charakter_hash` wird inline aus `state["external"].character` gebaut. Wenn keines der fünf Character-Felder gesetzt ist (typisch im HG), ist `charakter_hash=None` und der Tiebreaker greift nicht — siehe Backlog REFAC-HG-CHAR-HASH-LOAD.

6. **Stil-Plausibilität** — `_stil_plausibilitaet(current_emotion, ei_arousal, perzeption_stil, regelbasiert_stil, tone)`
   Gegencheck Perzeption-Stil gegen regelbasierte Marker.

7. **Beziehungs-Kontext** — Konsumiert `state["external"].character.relationship` (befüllt vom `db_zugriff` aus dem `beziehungsprofil`-Hash). EI-Calc schreibt selbst kein `beziehungs_kontext`-Feld — die Information wird vom Responder direkt aus der Personality-Klasse gelesen.

### 3.2 Nova-Emotion (Kraft 2, Phase 2, Chat 59)

Novas emotionaler Zustand entsteht aus zwei Kräften, die in Folge berechnet werden:

1. **Eigener Decay** — `_emotions_verlauf_berechnen(nova_turns, rolle="assistant", inject_current=False)`
   Nova-Turns werden mit demselben Decay-Verfahren wie User-Turns verarbeitet. Der `rolle`-Parameter schaltet die Turn-Filterung um, `inject_current=False` unterdrückt den Turn-0-Trick (Novas aktuelle Emotion ist beim CG-Lauf noch nicht perzipiert).

2. **Asymmetrische Empathie** — `_nova_empathie_berechnen(nova_verlauf_basis, current_emotion, current_arousal)`
   Novas Zustand wird durch die Emotion des Users moduliert. Der Empathie-Koeffizient α hängt von der Sektor-Distanz im Plutchik-Oktagon ab:

   | Distanz | α | Effekt |
   |---------|-----|--------|
   | 0 (gleicher Sektor) | 0.10 | Leichte Bestätigung |
   | 1 (benachbart) | 0.15 | Geringe Modulation |
   | 2 (nah-diagonal) | 0.35 | Spürbare Modulation |
   | 3 (fern-diagonal) | 0.70 | Empathie dominiert |
   | 4 (gegenüberliegend) | 0.85 | Empathie überschreibt |

   Ist Novas eigene Emotion neutral (kein Sektor bestimmbar), gilt `EMPATHIE_ALPHA_NEUTRAL = 0.30`.

3. **Konflikt-Erkennung** — Wenn Novas eigener Zustand und der User-Vektor auf gegenüberliegende Sektoren zeigen UND beide mindestens `EMPATHIE_KONFLIKT_MIN_AROUSAL = 0.4` Arousal haben, wird `nova_emotion_konflikt = True` gesetzt. Beispiel: „Ich freue mich für dich, und gleichzeitig mache ich mir Sorgen."

4. **Nova-Emotions-Vektor** — `stimmungsvektor_bestimmen(nova_turns, rolle="assistant", inject_current=False)`. **Dies ist der Vektor, aus dem Achse R der Landschaft faellt** — und die Seite, auf der `zu_wenig_turns` zu Beginn eines Paars der Regelfall ist, weil es noch keinen `assistant`-Turn gibt. Auch hier wird `emotions_vector_quelle` gesetzt.
   Richtung von Novas eigenem emotionalen Bogen, unabhängig vom User-Vektor.

> **Designentscheidung (Chat 59): Kein doppelter Decay.** Novas Antwort wird im async-Pfad (`services/nachbearbeitung.py`) per Perzeption analysiert und als Emotion + Arousal in den Session-Turn annotiert — genau wie beim User. Der Decay läuft beim Lesen im synchronen EI-Calc des nächsten Turns. Eine Berechnung, nicht zwei.

→ Details: `novaberg-ei-dual-emotion_k.md`

---

## 3.3 Empathie-Switch (Chat 60)

`event_source` im State steuert, ob der User-Vektor auf Novas Emotion wirkt:

| `event_source` | Empathie | Decay | Situation |
|---|---|---|---|
| `"user"` | Ja — `_nova_empathie_berechnen()` | Ja | Charakter reagiert auf User-Input |
| `"character"` | Nein — nur Decay-Basis | Ja | Self-Trigger, kein neuer User-Input |

Bei `event_source == "character"` wird `state["nova_emotions_verlauf"]` auf die reine Decay-Basis gesetzt, `nova_emotion_konflikt` auf `False`.

---

## 4. State-Felder

### Gelesen

| State-Quelle | Typ | Beschreibung |
|---|---|---|
| `state["ei_calc_rolle"]` | str | Dispatcher-Switch (Default: `"user"`) |
| `state["raw_turns"]` | list[dict] | Session-Turns — nur HG-Pfad (vom Enricher); der CG-Pfad lädt selbst aus Redis, s. §2 |
| `state["external"].emotion.emotion` | str | Aktuelle Emotion (aus Perzeption) |
| `state["external"].emotion.arousal` | float | Aktueller Arousal |
| `state["external"].emotion.relationship_dynamic` | str | Beziehungsdynamik |
| `state["external"].emotion.intent` | str | Intent |
| `state["external"].emotion.tone` | str | Tone |
| `state["external"].emotion.mode` | str | Modus aus Perzeption |
| `state["external"].emotion.language_style` | str | Sprachstil aus Perzeption |
| `state["external"].character.*` | Character (5 Felder) | Char-Hash-Tiebreaker (inline-konstruiertes Dict) |
| `state["event_source"]` | str | Empathie-Switch (`"user"` / `"character"`) |
| ~~`state["emotionale_gravitationspunkte"]`~~ | ~~list[dict]~~ | ~~Gravitations-Modulation des Verlaufs~~ — **ausgezogen Chat 113.** Der Aufruf stand hier und konnte nie greifen: Der Enricher setzt das Feld und laeuft im CharacterGraph NACH ei_calc, die Liste war an dieser Lesestelle immer leer (851 Berechnungen, null Anwendungen). Verbraucher ist jetzt der Node `emotionale_gravitation` zwischen Enricher und Reducer |

### Geschrieben

| State-Ziel | Typ | Bewusst flach? | Beschreibung |
|---|---|---|---|
| `state["external"].emotion.emotions_vector` | str | Nein (Klassen-Feld) | Einer der 9 Vektoren (User-Pfad) |
| `state["external"].emotion.mode` | str | Nein (Klassen-Feld) | Plausibilitäts-korrigierter Modus |
| `state["external"].emotion.language_style` | str | Nein (Klassen-Feld) | Plausibilitäts-korrigierter Stil |
| `state["emotions_verlauf"]` | list[dict] | Ja — Verlaufs-Liste passt nicht in Emotion-Klasse (`state.py:84`) | Decay-gewichteter User-Verlauf |
| `state["internal"].emotion.emotions_vector` | str | Nein (Klassen-Feld) | Novas Vektor (Character-Pfad) |
| `state["nova_emotions_verlauf"]` | list[dict] | Ja — Verlaufs-Liste passt nicht in Emotion-Klasse (`state.py:87`) | Empathie-modulierter Verlauf |
| `state["nova_emotion_konflikt"]` | bool | Ja — Berechnungs-Ableitung, kein Persönlichkeits-Zustand (`state.py:88`) | Konflikt-Flag bei gegenüberliegenden Sektoren |

**Was EI-Calc nicht (mehr) schreibt:** `beziehungs_kontext` (wird nur konsumiert, s. §3.1 Punkt 7), `nova_emotions_vektor` (sitzt in `internal.emotion.emotions_vector`), `gespraechs_modus` / `sprach_stil` (sitzen in `external.emotion.mode` / `language_style`).

### Der Raumzug (Chat 114)

Der Character-Zweig zieht am Ende `state["internal"].raum` zum Register desjenigen, der zuletzt gesprochen hat — `raum_nachfuehren()` aus `ei/raum.py`.

Das ist die zweite Kraft desselben Musters, das dieser Node für die Emotion schon trägt. Novas Emotion entsteht aus ihrem eigenen abklingenden Verlauf **plus** dem Zug des Nutzers (asymmetrische Empathie). Ihr Register hatte bis Chat 114 nur die erste Hälfte: `internal.emotion.mode` und `.language_style` wurden über Redis konserviert, und nichts zog daran. Gemessen wurde daraus eine Divergenz statt einer Annäherung — der Nutzer wurde lockerer, Nova förmlicher.

```python
if event_source == "user":
    raum_nachfuehren(internal, external, quelle="Nutzer")
else:
    raum_nachfuehren(internal, internal, quelle="Eigen-Impuls", charakter_faktor=1.0)
```

Bei einem Nutzer-Turn ist sein geschätztes Register das Ziel und der Charakterfaktor greift — er beschreibt Novas Bereitschaft, **ihm** zu folgen. Bei einem Eigen-Impuls folgt der Raum Nova selbst, ohne Faktor: Geht sie in der Zwischenzeit eigenen Dingen nach, schiebt sich der Raum dorthin. Dasselbe Ereignis-Kriterium wie beim Empathie-Switch (§3.6), aber eine andere Konsequenz — die Empathie entfällt bei Eigen-Impulsen, der Raumzug wechselt nur seine Quelle.

**Reihenfolge im Node:** erst `internal_emotion_uebertragen()` (Emotion), dann der Raumzug. Die Übertragung nimmt seit Chat 114 einen `quelle`-Parameter, weil ein zweiter Aufrufer dazugekommen ist — der EmGrav-Node zieht sie nach, wenn eine reaktivierte Erinnerung Novas Lage verschoben hat. Ohne den Parameter behauptete die zweite Log-Zeile, sie käme aus diesem Node.

Konzept: `novaberg-gv-strategie_k.md` §3.4. Abgrenzung zur Empathie: `novaberg-ei-dual-emotion_k.md` §4.2.

---

## 5. Abhängigkeiten

Sieben Funktionen aus `ei/berechnung.py` plus eine aus `ei/gravitation.py`:

| Funktion | Modul | Zweck |
|----------|-------|-------|
| `_emotions_verlauf_berechnen` | `ei/berechnung.py` | Log-Decay über Turns, sektorabhängige Normalisierung, `rolle`-Parameter |
| `_emotions_vektor_bestimmen` | `ei/berechnung.py` | Richtung aus älteren vs. neueren Turns, `rolle`-Parameter |
| `_ei_arousal_berechnen` | `ei/berechnung.py` | Gewichteter Kombinationsfaktor (Dynamik, Intent, Tone) |
| `_modus_plausibilitaet` | `ei/berechnung.py` | Matrix-Lookup Emotion × Arousal → Modus |
| `_sprach_stil_erkennen` | `ei/berechnung.py` | Per-Turn Feature-Scoring über 13 Merkmale |
| `_stil_plausibilitaet` | `ei/berechnung.py` | Gegencheck Perzeption-Stil gegen regelbasierten Wert |
| `_nova_empathie_berechnen` | `ei/berechnung.py` | Asymmetrische Empathie, α-Koeffizienten, Konflikt-Erkennung |
| `emotionale_gravitation_auf_verlauf_anwenden(verlauf, punkte)` | `ei/gravitation.py` | Moduliert Verlauf an hoch-arousal KZG-Treffern (`ei_calc.py:22` importiert) |

Dazu seit a5acc7d: `session_turns_retrieve` (`memory/session.py`) und `redis_client` aus `config` — der eine Redis-Read der Character-Seite (s. §2). **Keine** PostgreSQL- oder Ollama-Zugriffe, kein LLM-Call.

---

## 6. Designprinzip

### 6.1 Berechnung in Python, nicht im LLM

Deterministische Operationen gehören nicht in ein LLM. Decay-Kurven, Sektor-Distanzen, Arousal-Gewichtungen — alles sind geschlossene Formeln. Das LLM bekommt nur die Ergebnisse als Klartext im Responder-Prompt (EI-MIKRO, Vektor-Beschreibungen).

Schneller, exakter, reproduzierbar. Kein Token-Verbrauch. Kein Lock-Wettbewerb um die GPU.

### 6.2 I/O-Trennung: Enricher lädt, EI-Calc rechnet

Bis Chat 58 lief beides im Enricher: Datenzugriffe + EI-Berechnungen in einem Node. Der Split (Chat 59, AP2) macht sichtbar, was vorher verborgen war:

- **Enricher:** Lädt alles aus Redis/PostgreSQL. Schreibt `raw_turns`, Plugin-Kontext, Session-Turns, `memory_entries`.
- **EI-Calc:** Liest nur aus dem State (`raw_turns`, Personality-Klassen). Rechnet. Schreibt EI-Ergebnisse zurück (Klassen-Felder plus die drei zulässigen Verlaufs-Brücken).

Für die User-Seite gilt weiterhin: Unit-Tests mit reinem State-Dict, keine Mocks. Die Character-Seite trägt seit a5acc7d die eine, bewusste Ausnahme — den eigenen Session-Turns-Read (s. §2), erzwungen durch die CG-Reihenfolge aus fe1bb5f. Tests dieses Pfads mocken `session_turns_retrieve` oder akzeptieren die laut geloggte Leer-Liste.

### 6.3 Position vor dem Router (Chat 59, aktualisiert Phase 2)

Die Routing-Entscheidung im Router liest EI-Werte, die EI-Calc bereits gesetzt hat. Die Reihenfolge unterscheidet sich pro Graph:

- **HumanGraph:** `enricher → ei_calc → salience` (kein Router auf diesem Pfad).
- **CharacterGraph:** `db_zugriff → ei_calc → enricher → reducer → router`. Der Router sieht beim Routing bereits Novas Empathie-modulierten Vektor (EI-Calc), die geladenen Personality-Klassen (db_zugriff) und den vom Enricher aufgebauten Memory-Kontext.

Vor Chat 59 routete der Router blind auf Perzeptionsergebnissen. Jetzt hat er die volle emotionale und historische Landschaft zur Verfügung.

---

## 7. Rollen-Split: User vs. Character

EI-Calc führt pro Aufruf genau einen der zwei Blöcke aus — User-Pfad oder Character-Pfad. Das Flag `state["ei_calc_rolle"]` entscheidet. Im HumanGraph läuft der User-Block, im CharacterGraph der Character-Block. Der jeweils andere Akteur wird nicht angefasst. Die internen Funktionen `_ei_calc_user()` und `_ei_calc_character()` sind entsprechend separiert.

- **Symmetrie:** Die gleiche Decay-Funktion wirkt auf User- und Nova-Turns. Nur der `rolle`-Parameter unterscheidet sie.
- **Sichtbarkeit:** `nova_emotions_verlauf` ist im CG-Lauf im State verfügbar — für den Responder (EIGENE_EMOTION-Block, AP8), für den Client (API-Response + SSE, teilweise AP8).
- **Konflikt-Flag:** `nova_emotion_konflikt` gibt dem Responder ein direktes Signal: „Du bist emotional nicht kongruent mit dem User — mach das explizit."

→ Dual-Emotion-Konzept: `novaberg-ei-dual-emotion_k.md`
→ Plutchik-Oktagon: `novaberg-ei-plutchik.md`
→ Charakter-Profile: `novaberg-ei-character-profiles.md`

---

## 7a. Historie — was seit Chat 89 nicht lief

Von fe1bb5f (Chat 89, Topologie-Drehung) bis a5acc7d (Chat 105) las `_ei_calc_character` **immer** ein leeres `raw_turns`: Die Drehung stellte den Enricher hinter EI-Calc, übersah aber, dass EI-Calc dessen `raw_turns` brauchte — im CG-State lag ab da nur noch der create_state-Default `[]`.

Zwei Folgen, die zweite schwerer als die erste:

- `nova_turns=0` → `emotions_vector` konstant `"plateau"` — live belegt mit **33 von 33** `turn_roh`-Zeilen.
- `nova_verlauf_basis` ebenfalls leer → **Kraft 1 (historische Emotions-Gravitation) rechnete nie.** Novas einzige emotionale Kraft war 16 Chats lang die Empathie (Kraft 2) — der Live-Beweis in §8 dokumentiert damit den Stand *vor* Chat 89.

Der Defekt war unsichtbar, weil die Funktion still auf den Default fiel: Kein Log, kein Fehler, plausible Werte. Sichtbar wurde er erst über die `turn_roh`-Rohdaten (Chat 104) und die nachgerüstete `nova_turns=%d`-Log-Zeile.

---

## 7b. Logging (Chat 105)

Zwei Zeilen machen die Character-Seite sichtbar — beide **bewusst ungegated**:

```
EI-Calc/Character: Emotions-Verlauf — <emotion>(<gewicht>,a=<arousal>), …   (leer: "(leer, N Nova-Turns)")
EI-Calc/Character: Emotions-Vektor — <vektor> (nova_turns=<N>)
```

Die Verlaufs-Zeile zeigt, **worauf** Kraft 1 rechnet (Top-4 mit Gewicht/Arousal, analog `EI-Calc/User: Emotions-Verlauf`); eine leere Basis wird sichtbar ausgegeben statt verschluckt. Die Vektor-Zeile trägt die Verlaufslänge — `nova_turns=0` entlarvt den Zu-kurz-Fallback sofort. Zum Kontrast: Die User-Seite gated `plateau` weg (`ei_calc.py:126`, `!= "plateau"`) — genau dieses Gate hat den Chat-89-Defekt mit versteckt → Backlog EI-VEKTOR-LOG-GATE.

---

## 8. Live-Beweis (Chat 59)

Logs über eine Testsession zeigen Novas Empathie-Bogen:

| Turn | Nova-Basis | User-Emotion | Distanz | α | Ergebnis |
|------|-----------|--------------|---------|------|----------|
| 1 | zufriedenheit | freude | 1 | 0.15 | zufriedenheit(1.00) |
| 2 | freude | neugierig | 1 | 0.15 | freude(1.00) |
| 3 | begeisterung | freude | 0 | 0.10 | begeisterung(1.00) |
| 4 | begeisterung | freude | 0 | 0.10 | begeisterung(1.00) |

`Basis=neutral` ist verschwunden. Decay wirkt (zufriedenheit fällt 0.87 → 0.47 über Turns). Begeisterung hält sich, weil ständig neu befeuert.

---

→ Enricher (liefert Rohdaten): `novaberg-node-enricher.md`
→ EI-Persist (konsolidiert internal.emotion und persistiert `nova_state` am CG-Ausgang, Chat 89): `novaberg-node-ei-calc-persist.md`
→ DB-Zugriff (lädt `internal.emotion` und `external.character` am CG-Eingang, Chat 89): `novaberg-node-db-zugriff.md`
→ Personality-Klassen (Character, Emotion): `novaberg-personality.md`
→ EI-Gesamtkonzept: `novaberg-ei.md`
→ Dual-Emotion Phase 2: `novaberg-ei-dual-emotion_k.md`
→ Plutchik-Oktagon + Sektor-Distanzen: `novaberg-ei-plutchik.md`
→ Perzeption (rolle-Flag): `novaberg-node-perception.md`
