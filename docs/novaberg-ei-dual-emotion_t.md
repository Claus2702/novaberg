# Novaberg — Dual-Emotion Phase 2: Novas Emotionsstrang (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-ei-dual-emotion_k.md`](novaberg-ei-dual-emotion_k.md) · Bauplan und Umstellung: [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md) · Diskussion und Ergänzungen: [`novaberg-ei-dual-emotion_e.md`](novaberg-ei-dual-emotion_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 2. Der Kreislauf

```
Turn N:
  [Synchron — User wartet]
  Perzeption(User)     → Emotion, Arousal, Modus, Intent des Users
  Enricher(laden)      → Session, KZG, LZG, Hash laden (User + Nova)
  EI-Calc(User)        → Emotions-Verlauf, Vektor, Stil, Plausibilitäts-Gate
                          Nova-Emotion(N-1) laden → Decay + Empathie
                          → Nova-Emotion(N) berechnen → in State
  Router               → Routing-Entscheidungen (sieht jetzt volle Session + EI)
  [Planner → Agent]    → Bei Management-Aktion
  GV-Node              → Gesprächsvektor
  Responder            → Antwort generieren (mit Nova-Emotion als Kontext)
  Thinker              → Faktenprüfung
  Tribunal             → Qualitätskontrolle
  [Corrector]          → Bei Ablehnung

  [Antwort an User]

  [Asynchron — User wartet nicht]

  Nova (voller Pfad, ASSISTANT_USER_ID):
  Perzeption(Nova)     → Emotion, Arousal, Modus, Intent von Novas Antwort
  Enricher(Nova)       → Novas Session-Turns laden (ASSISTANT_USER_ID)
  EI-Calc(Nova)        → Nova-Emotions-Verlauf + Vektor berechnen
  Router(Nova)         → Prüft auf Commitments (Agent-Bedarf)
  [Planner → Agent]    → Bei Commitment (selten, z.B. "Ich erinnere dich morgen")
  Salienz(Nova)        → Nova-Antwort bewerten → pending_writes(Nova)
  Dispatcher(Nova)     → Schreibt unter ASSISTANT_USER_ID

  User (nur speichern, Daten liegen bereits im State):
  Salienz(User)        → User-Prompt bewerten → pending_writes(User)
  Dispatcher(User)     → Schreibt unter DEFAULT_USER_ID
```

---

## 3. Enricher-Split: Laden vs. Rechnen

### 3.1 Problem

Der Enricher ist ~1000 Zeilen und mischt zwei grundverschiedene Verantwortungen: Daten laden (I/O) und EI berechnen (reine Funktionen). Für Phase 2 müssen die EI-Berechnungen wiederverwendbar sein — einmal für den User (synchron), einmal für Nova (asynchron).

### 3.2 Split

**`ei/berechnung.py`** — ~600 Zeilen, reine Funktionen, null I/O:

| Funktion | Aufgabe |
|----------|---------|
| `_emotion_kanonisieren()` | Synonym-Auflösung |
| `_arousal_to_float()` | Legacy-Konvertierung |
| `_emotions_verlauf_berechnen()` | Gewichteter Verlauf mit Decay + Plutchik-Normalisierung |
| `_emotion_zu_gruppe()` | Sektor → Gruppe |
| `_dominante_gruppe()` | Dominante Gruppe einer Turn-Liste |
| `_emotions_vektor_bestimmen()` | 9 Richtungsvektoren |
| `_turn_features_bewerten()` | 13 Stilmerkmale pro Turn |
| `_hash_stil_extrahieren()` | Stil aus Charakter-Hash |
| `_sprach_stil_erkennen()` | Akkumuliertes Feature-Scoring |
| `_ei_arousal_berechnen()` | Gewichteter EI-Faktor |
| `_modus_plausibilitaet()` | Matrix-Lookup Modus |
| `_stil_plausibilitaet()` | Stil-Gegencheck |

**`graph/nodes/enricher.py`** — ~400 Zeilen, nur Daten laden:

| Block | Aufgabe |
|-------|---------|
| Session-Turns aus Redis | `session_turns_retrieve()`, Shadow-Filter |
| Plugin-Hooks | `manager.enrich()` Loop |
| Charakter-Anweisungen + Direktiven | PostgreSQL SELECT |
| KZG/LZG Suche | Embedding erzeugen, Vektor-Suche |
| Charakter-Hash (User + Nova) | `charakter_hash_retrieve_dict()` |

### 3.3 EI-Calc als eigener Node

**Neuer Node:** `graph/nodes/ei_calc.py`

Importiert die Funktionen aus `ei/berechnung.py`, ruft sie mit den geladenen Daten aus dem State auf, schreibt die Ergebnisse zurück in den State.

**Kein LLM-Call.** Reine Python-Berechnung, deterministisch, < 100ms.

**Position im Graph:** Nach Enricher(laden), vor Router. Damit sieht der Router die vollständigen EI-Ergebnisse und kann bessere Routing-Entscheidungen treffen (löst ROUTE-MISS1).

**Dual-Modus:** Im synchronen Pfad berechnet EI-Calc die User-EI UND lädt Novas Emotions-Historie für die Nova-Emotion(N)-Berechnung (Decay + Empathie). Im asynchronen Pfad berechnet derselbe Node Novas EI aus der frischen Perzeption.

---

## 4. Nova-Emotion: Quellen und Berechnung

Pro Turn wirken zwei Kräfte auf Novas Position im 8-dimensionalen Plutchik-Raum (Phase 3 fügt die dritte hinzu):

### 4.1 Vorheriger Zustand × Decay

Novas Emotionsvektor tendiert zur Neutralität zurück, wenn nichts ihn verstärkt. Dieselbe Decay-Mechanik wie beim User — `_emotions_verlauf_berechnen()` auf Novas Turn-Historie.

### 4.2 Nutzer-Vektor × α (Asymmetrische Empathie)

Die Emotion des Users wirkt als Kraft auf Novas Position. Der Empathie-Faktor α hängt von der Sektor-Distanz im Plutchik-Oktagon ab:

| Sektor-Distanz | α-Bereich | Beispiel |
|----------------|-----------|---------|
| 0–1 (benachbart) | 0.1–0.2 | Beide freudig → Bestätigung |
| 2 (nah-diagonal) | 0.3–0.4 | Nova neugierig, User überrascht → leichte Modulation |
| 3–4 (gegenüber) | 0.7–0.9 | Nova freudig, User traurig → Empathie überschreibt |

Die Sektor-Distanzmatrix existiert bereits (`EMOTION_SEKTOR_DISTANZ` in `config.py`).

> **Abgrenzung zum Raumzug (Chat 114) — das Vorzeichen kehrt sich um.** Novas Register hat seit Chat 114 dieselbe Bauart: ein eigener Zustand, der vom Nutzer angezogen wird (`ei/raum.py`, Konzept in `novaberg-gv-strategie_k.md` §3.4). Die Formel ist dieselbe Gestalt, die Abhängigkeit von der Distanz aber die **entgegengesetzte**.
>
> | | Emotion | Register |
> |---|---|---|
> | Große Distanz | zieht **stärker** — Empathie überschreibt | zieht **nicht** stärker |
> | Richtung | symmetrisch | hinauf (System 1 → System 2) langsamer als hinab |
> | Faktor aus | Sektor-Distanz im Plutchik-Oktagon | fester Zug × Charakterfaktor |
>
> Der Grund ist inhaltlich: Ein Gegenüber, das emotional weit weg steht, zieht mich mit — das ist Mitgefühl. Ein Gegenüber, das das Register wechselt, zieht mich nicht schneller, weil das gedankliche Umstellen Zeit kostet, egal wie weit der Sprung ist.
>
> **Wer die α-Tabelle oben fürs Register abschreibt, baut das Gegenteil dessen, was entschieden wurde.**

### 4.3 Ziel-Vektor × Similarity (Phase 3 — noch nicht)

Aktivierte Zielsätze injizieren Emotion. Kommt mit dem Antrieb-System (novaberg-thinking-drive_k.md §4.3). In Phase 2 hat Nova zwei Quellen, keine drei.

### 4.4 Konflikterkennung

Wenn Empathie-Vektor und Novas eigener Zustand in entgegengesetzte Richtungen zeigen (Cosine-Similarity < -0.3), wird ein `nova_emotion_konflikt`-Flag gesetzt. Der Responder kann den Konflikt aktiv ausdrücken: "Ich freue mich für dich, aber ich mache mir Sorgen."

---

## 5. Datentrennung

Strikte Partition über `user_id`:

| Daten | Partition | Beispiel |
|-------|-----------|---------|
| User-Emotionen | `DEFAULT_USER_ID` | "meister" |
| User-KZG/LZG | `DEFAULT_USER_ID` | "meister" |
| Nova-Emotionen | `ASSISTANT_USER_ID` | "nova" |
| Nova-KZG | `ASSISTANT_USER_ID` | "nova" |
| Nova-Charakter-Hash | `ASSISTANT_USER_ID` | "nova" |

**Umschalten auf Charlotte** → anderer `ASSISTANT_USER_ID` → komplett andere Emotionshistorie, anderes KZG, anderer Charakter. Dasselbe gilt umgekehrt: anderer User → anderer `DEFAULT_USER_ID`. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

**Innerhalb eines Turns** fließt alles durch den State — das ist das eine Momentum. User-Daten und Nova-Daten koexistieren im selben State-Dict, werden aber getrennt gespeichert.

---

## 6. Asynchroner Block — Details

> **⚠️ Veraltet (Chat 60).** Der hier beschriebene asynchrone Block wurde durch das Event-Modell ersetzt. Der CharacterGraph (Pfad 2) läuft als eigenständiger Graph, ausgelöst durch Events. Siehe `novaberg-convention-event-model.md`.

### 6.1 Perzeption(Nova)

Derselbe Perzeption-Node, aufgerufen mit Novas `response` statt `user_prompt`. Der Prompt wird minimal angepasst: "Analysiere die folgende Aussage der Assistentin" statt "Analysiere den Prompt des Nutzers."

Extrahiert: `nova_response_emotion`, `nova_response_arousal`, `nova_response_modus`, `nova_response_intent`, `nova_response_tone`, `nova_response_beziehungs_dynamik`.

### 6.2 Enricher(Nova)

Derselbe Enricher-Node, aber mit `ASSISTANT_USER_ID`. Lädt Novas eigene Session-Turns, ihr KZG, ihr LZG, ihren Charakter-Hash. Der User-Enricher lief synchron — jetzt läuft Novas Enricher asynchron auf ihrer eigenen Partition.

### 6.3 EI-Calc(Nova)

Gehört zur Perzeption — erst wahrnehmen, dann berechnen. Dieselben Funktionen wie EI-Calc(User), aber auf Novas Turn-Historie (`ASSISTANT_USER_ID`-Partition):

- `_emotions_verlauf_berechnen()` auf Novas Session-Turns
- `_emotions_vektor_bestimmen()` auf Novas Session-Turns
- Empathie-Berechnung: Novas neuer Vektor unter Einfluss des User-Vektors

Schreibt: `nova_emotions_verlauf` in den State; den Vektor nach `internal.emotion.emotions_vector` (Personality-Klasse — ein flacher State-Key `nova_emotions_vektor` existiert seit dem Personality-Umbau nicht mehr; der Responder liest seit Chat 106 direkt aus der Klasse, RESPONDER-VEKTOR-TOT).

### 6.4 Router(Nova)

Derselbe Router-Node, prüft Novas Antwort auf Commitments. In den meisten Fällen: kein Agent-Bedarf → weiter zur Salienz. Im seltenen Fall, dass Nova ein Versprechen gemacht hat ("Ich erinnere dich morgen") → Planner → TimelineAgent/WiedervorlageAgent.

### 6.5 Salienz + Dispatcher

Zwei getrennte Pfade:

**Nova-Pfad (im selben async-Block):**
Salienz(Nova) → "Hat die Assistentin etwas gesagt, das sie sich merken sollte?" → `pending_writes` mit `user_id = ASSISTANT_USER_ID` → Dispatcher(Nova) schreibt unter `ASSISTANT_USER_ID`.

**User-Pfad (parallel oder sequentiell):**
Salienz(User) → "Hat der User etwas Wichtiges gesagt?" → `pending_writes` mit `user_id = DEFAULT_USER_ID` → Dispatcher(User) schreibt unter `DEFAULT_USER_ID`. Keine Enricher/EI-Calc nötig — die Daten liegen bereits im State vom synchronen Durchlauf.

### 6.6 Laufzeit-Schätzung

| Schritt | GPU-Calls | Geschätzte Zeit |
|---------|-----------|----------------|
| **Nova-Pfad:** | | |
| Perzeption(Nova) | 1 | ~1-2s |
| Enricher(Nova) | 0 (I/O) | <0.5s |
| EI-Calc(Nova) | 0 (Python) | <0.1s |
| Router(Nova) | 1 | ~1-2s |
| Salienz(Nova) | 1 | ~2-3s |
| Dispatcher(Nova) | 0 (Python) | <0.1s |
| **User-Pfad:** | | |
| Salienz(User) | 1 | ~2-3s |
| Dispatcher(User) | 0 (Python) | <0.1s |
| **Gesamt (ohne Agent)** | **4** | **~6-10s** |
| + Agent bei Commitment | +1-2 | ~9-15s |

Alles asynchron — der User sieht die Antwort sofort nach dem Tribunal.

---

## 7. Neue State-Felder

| Feld | Typ | Quelle | Beschreibung |
|------|-----|--------|-------------|
| `nova_response_emotion` | `str` | Perzeption(Nova) | Novas dominante Emotion in dieser Antwort |
| `nova_response_arousal` | `float` | Perzeption(Nova) | Novas Arousal in dieser Antwort |
| `nova_response_modus` | `str` | Perzeption(Nova) | Novas Kommunikationsregister |
| `nova_response_intent` | `str` | Perzeption(Nova) | Novas Kommunikationsabsicht |
| `nova_emotions_verlauf` | `list[dict]` | EI-Calc(Nova) | Gewichteter Verlauf mit Decay |
| `internal.emotion.emotions_vector` | `str` | EI-Calc(Nova) | Richtungsvektor (9 Werte) — Klassen-Feld, kein flacher Key (Chat 106) |
| `nova_emotion_konflikt` | `bool` | EI-Calc | Empathie vs. eigener Zustand |

---

> **Hinweis zur Aufteilung (19.09.2026):** §8 *Graph-Änderungen* steht in [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md).

---

## 9. Responder-Integration ✅

Der Responder bekommt Novas berechnete Emotion für den aktuellen Turn als zusätzlichen Kontext im `[EIGENE_EMOTION]`-Block:

```
[EIGENE_EMOTION]
Dein aktueller emotionaler Zustand: {nova_emotion_label}
Arousal: {nova_arousal}
Vektor: {nova_emotions_vektor}
```

Platziert zwischen [IDENTITAET] und [KOMMUNIKATION]. Die Emotion beeinflusst die Antwort, ohne sie zu diktieren — Nova kann fröhlich sein und trotzdem sachlich antworten, aber die Grundfärbung ändert sich.

**Status:** Implementiert. Der Block wird aus `nova_emotions_verlauf`, `nova_emotions_vektor` und `nova_emotion_konflikt` (State-Felder aus EI-Calc) zusammengebaut.

---
