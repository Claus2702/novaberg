# Novaberg — Referenz-Auflösung (REF-KASKADE) (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-referenz-aufloesung_k.md`](novaberg-referenz-aufloesung_k.md) · Bauplan und Umstellung: [`novaberg-referenz-aufloesung_b.md`](novaberg-referenz-aufloesung_b.md) · Diskussion und Ergänzungen: [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen.

---

## 5. Datenstrukturen

Kein `dict` mit implizitem Schema (`lesson_l_klassen-statt-flache-keys`). Frozen Dataclasses.

```python
# server/graph/reference/types.py

class Status(Enum):
    """Ergebniszustand einer Auflösungsschicht."""
    GEFUNDEN = "gefunden"
    UNSICHER = "unsicher"
    NICHTS = "nichts"


@dataclass(frozen=True)
class Reference:
    """Eine im Prompt erkannte, auflösungsbeduerftige Bezugnahme."""
    text: str                    # "die Liste" — wie im Prompt
    head: str                    # "Liste" — lemmatisiert, Kopf-Substantiv
    kind: str                    # definite_nominal | pronoun | ellipsis | ordinal
    span: tuple[int, int]        # Zeichen-Offsets im user_prompt


@dataclass(frozen=True)
class Candidate:
    """Ein moeglicher Referent fuer eine Referenz."""
    text: str                    # "Einkaufsliste"
    source: str                  # turn | entity | db_object
    source_id: str               # Turn-Index oder DB-Primaerschluessel
    turn_distance: int           # 0 = letzter Turn (Rezenz)
    score: float                 # 0.0-1.0, schichtabhaengig berechnet
    layer: str                   # L1 | L2 | L3 | L4


@dataclass(frozen=True)
class Resolution:
    """Ergebnis EINER Schicht fuer EINE Referenz."""
    reference: Reference
    status: Status
    candidates: tuple[Candidate, ...]   # sortiert, bester zuerst
    layer: str
    reason: str                  # Klartext fuers Log — WARUM dieser Zustand
```

`reason` ist keine Kosmetik. Es ist die Zeile, an der man später sieht, warum die Kaskade
falsch lag. *Erst die Zeile, dann der Fix.*

---

## 6. Die Schichten

### L0 — Detektor (Python, µs)

**Aufgabe:** Feststellen, **ob** überhaupt etwas aufzulösen ist. Die Kostenbremse.

**Auslöser:**

| Art | Muster | Beispiel |
|---|---|---|
| `definite_nominal` | Bestimmter Artikel + Substantiv | „**die** Liste", „**dem** Pulver" |
| `pronoun` | Personal-/Demonstrativpronomen | „**es**", „**die** ist voll" |
| `ordinal` | Ordnungs-/Vergleichswort + Substantiv | „die **andere**", „die **erste**" |
| `ellipsis` | Satzfragment ohne Verb | „und jetzt die zweite" |
| `repetition` | Wiederholungsadverb | „**nochmal**", „**wieder**" |

**Kein Auslöser:** unbestimmter Artikel („**eine** Liste" = neu), Eigennamen, vollständig
spezifizierte Komposita ohne Konkurrenz.

**Werkzeug:** spaCy `de_core_news_sm` (MIT, ~15 MB, CPU). Der Morphologizer liefert genau,
was wir brauchen: `DET` mit `Definite=Def` gefolgt von `NOUN`. Deterministisch.

⚠ **Bekannte Schwäche:** Der deutsche spaCy-Lemmatizer ist nachweislich unzuverlässig bei
Plural/Umlaut (*„Bäume" → „bäumen"*). **Wir brauchen den Lemmatizer nicht für den Kopf** —
CharSplit arbeitet auf der Oberflächenform. Für die Normalisierung des Kopfes reicht eine
Suffix-Regel oder alternativ `simplemma`/`HanTa` (beide MIT, leichtgewichtig).
**Offene Entscheidung, siehe §10.**

**Ausgang:** Kein Marker → `NICHTS`, Kaskade endet, **kein Aufwand**. Das ist der Gewinn.

---

### L1 — Kompositum-Kopf (Python, µs)

**Die Schicht, die den Matcha-Fall allein löst.**

Das Deutsche schenkt uns etwas, das andere Sprachen nicht haben: Das nackte Substantiv
*„Pulver"* ist der **Kopf** des Kompositums *„Matcha-Pulver"*. Ebenso *„Liste"* ⊂
*„Einkaufsliste"*.

**Werkzeug:** **CharSplit** (MIT, reines Python, N-Gramm-Statistik, kein NN).
Trainiert auf 1 Mio. deutschen Substantiven aus Wikipedia, ~95 % Genauigkeit bei der
Kopf-Erkennung auf dem GermaNet-Kompositum-Testset.

```python
>>> from charsplit import Splitter
>>> Splitter().split_compound("Einkaufsliste")
[(0.79, 'Einkaufs', 'Liste'), ...]   # Kopf = zweites Element
```

Ironie am Rande: CharSplit stammt aus dem Anhang von Tuggeners Dissertation
*„Incremental Coreference Resolution for German"* (Uni Zürich, 2016). Wir landen auf demselben
Feld — nur über eine MIT-Tür.

**Algorithmus:**

```
FÜR jedes Substantiv N der letzten n Turns:
    kopf = CharSplit.head(N)                    # "Einkaufsliste" -> "Liste"
    WENN kopf == referenz.head:
        Kandidat(text=N, source="turn", score=1.0, layer="L1")
    SONST WENN referenz.head == N:              # Identität, kein Kompositum
        Kandidat(text=N, source="turn", score=1.0, layer="L1")
```

**Rezenz-Gewichtung (deterministisch, Python — kein LLM):**

```
score_final = score_layer * exp(-LAMBDA_RECENCY * turn_distance)
```

Exponentieller Abfall, dieselbe Formel wie `synapsen_decay`. Der jüngste Referent gewinnt.
`LAMBDA_RECENCY` in `config.py`, Startwert aus dem Schatten-Lauf (§8), **nicht geraten**.

**Grenze:** L1 kann *„die andere"*, *„das nochmal"*, *„es"* nicht. Dafür ist L4 da.

---

### L2 — Entitäten (Python + DB, ms)

**Grundsatz: „Entität schlägt Embedding."**

Zwei Quellen:

**L2a — Verlaufs-Entitäten.** Die im Verlauf erkannten Entitäten (Entity-Layer).
⚠ **Existiert das pro Turn?** Das ist die offene Frage, an der L2 hängt. Brudis
Discovery-Audit (Chat 106, Teil B1) beantwortet sie. Falls **nein**: L2a entfällt im ersten
Wurf, L2b bleibt.

**L2b — DB-Objekte.** Abgleich gegen **tatsächlich existierende** Objektnamen:
Notiz-Titel, Timeline-Einträge, Direktiven-Namen. Kein Raten — der Referent muss ein
Objekt bezeichnen, das es **gibt**.

Das ist der Punkt, den kein Koreferenz-System der Welt hat: **Grounding gegen eine reale
Datenbank.** Maverick weiß nicht, dass es eine Notiz namens „Einkauf" gibt. Wir wissen es.

```
FÜR jeden Notiz-Titel T (aktiv=TRUE, user_id=X):
    kopf = CharSplit.head(T)
    WENN kopf == referenz.head:
        Kandidat(text=T, source="db_object", source_id=notiz.id, score=0.9)
```

---

### L3 — Embedding (~10 ms)

**Aufgabe:** Die Kandidaten aus L1+L2 **ranken** — nicht selbst suchen.

Genau hier greift der echte Vokabular-Mismatch: *„Liste"* ↔ *„Notiz"* ist **kein**
Kompositum-Verhältnis. Nur semantische Nähe kann das binden.

```
FÜR jeden Kandidaten K aus L1+L2 (oder, falls leer: Substantive der letzten n Turns):
    K.score = cosine(embed(referenz.head), embed(K.text)) * exp(-LAMBDA * K.turn_distance)
```

> ### ⚠ BLOCKER — L3 steht auf ungeprüftem Fundament
>
> `nomic-embed-text` berichtet seine MTEB-Werte auf der **englischen** Bestenliste. Die
> mehrsprachige Variante ist erst Nomic Embed v2. **Wir fahren womöglich ein
> englisch-optimiertes Embedding-Modell über einen vollständig deutschen Korpus.**
>
> Trifft das zu, ist das kein L3-Problem — es ist ein Problem der **Grundschicht** des
> gesamten semantischen Gedächtnisses: KZG-Ähnlichkeit, LZG-Resonanz, Spreading Activation,
> Charakter-Destillation. Alles rechnet auf diesen Vektoren.
>
> **Messung vor Bau** (§8.1). Ohne sie ist L3 Kaffeesatz.

---

### L4 — LLM (qwen36-cpu, `think=False`, ~300 ms)

**Aufgabe:** Was Python nicht kann — *„die andere"*, *„das nochmal"*, Ellipsen, Ironie.

**Modell:** `qwen36-cpu`, `think=False`. Der Literaturbefund ist eindeutig: Koreferenz-Auflösung
braucht kein Frontier-Modell, ein kleines schnelles reicht. Der Chat-Pfad (gemma4-gpu) bleibt
unangetastet — **Chat-Latenz ist geschützt** (Topologie-Prinzip).

> **Das LLM darf keinen Referenten erfinden. Es darf nur substituieren.**

```json
{
  "referenz": "die Liste",
  "referent": "Einkaufsliste",
  "quelle_turn": 4,
  "konfidenz": "hoch"
}
```

**Python verifiziert — zwingend:**

```python
if referent not in turns[quelle_turn].text:
    logger.error(
        "REF/L4: Halluzinierter Referent '%s' — steht nicht in Turn %d. Vorschlag verworfen.",
        referent, quelle_turn,
    )
    log_fehler(...)                    # forensisch
    return Resolution(status=Status.NICHTS, ...)   # weiter zu L5
```

Das LLM schlägt vor, **Python entscheidet**. *Berechnung in Python, nicht im LLM.*
*Lieber laut krachen — das ist ehrlich.*

---

### L5 — Rückfrage (kein Fehler, sondern das Ziel)

Wenn nach L4 nichts sicher ist, fragt Nova. **Aber spezifisch.**

| | |
|---|---|
| ❌ heute | *„Welches Pulver meinst du? Kakao oder ein anderes?"* |
| ✅ Ziel | *„Meinst du das Matcha-Pulver, über das wir gerade sprachen?"* |

Die erste Rückfrage ist die einer Maschine, die den Verlauf nicht gelesen hat. Die zweite ist
die eines Gegenübers, das nur sichergehen will. **Der Unterschied ist der ganze Punkt.**

Bei `UNSICHER` mit mehreren Kandidaten wird die Rückfrage zur **Disambiguierung** —
mit den echten Kandidaten, nicht mit erfundenen Alternativen:

> *„Die Einkaufsliste oder die Preisliste?"*

⚠ Diese Rückfrage geht über den bestehenden `rueckfrage`-Pfad. **Voraussetzung:** der
`AGENT-RUECKFRAGE-LOOP`-Fix aus Chat 106 muss live abgenommen sein. Sonst produziert L5
den Crash, den wir gerade repariert haben.

---

## 7. Einbau in den Graph

### 7.1 Wohin der Node gehört

**Zwingend:** nach der Perzeption, **vor** dem Retrieval.

Und hier läuft er in **exakt dieselbe Falle wie `_ei_calc_character` in Chat 89**: Der Enricher
ist der einzige Schreiber von `state["raw_turns"]` — und der Enricher macht auch das Retrieval.
Wer vor dem Enricher läuft, hat keine Session-Turns. Wer nach ihm läuft, kommt zu spät.

**Lösung = Option (b) aus Chat 105, wortgleich:**

> **Der Node, der rechnet, lädt seine Daten selbst.**

Der Referenz-Node holt die Session-Turns über `session_turns_retrieve` — wie
`_ei_calc_character` seit `a5acc7d`. Keine Fernkopplung, kein Sonderweg, keine Kante zu drehen.
Und „leer" heißt dann eindeutig *leer* und nicht *nie geladen*.

⚠ **Der Enricher hat kein `try/except` um Redis** (`ENRICHER-REDIS-UNGESCHUETZT`). Der neue
Node **muss** eins haben. Sonst crasht ein Redis-Ausfall den kritischen Pfad.

### 7.2 Neue State-Kanäle

**Clipboard-Prinzip: `user_prompt` wird NIE verändert.** Nur ergänzt.

```python
# graph/state.py — ConversationState
prompt_resolved: str                    # umgeschriebener Prompt (leer = keine Auflösung)
reference_resolutions: list[Resolution] # strukturiert, mit Zustand und Quelle
```

⚠ **`StateGraph(TypedDict)` — das TypedDict IST die Kanal-Definition.** Fehlt ein Feld, wirft
LangGraph den Wert **still** weg (`lesson_l_stategraph-channel-zwang`). Beide Felder müssen in
**allen** Init-Punkten vorbelegt werden — `create_state` (`base.py`), `builder.py`,
`human_graph.py`, `character_graph.py`. Brudis Audit (Teil D3) findet sie alle.

### 7.3 Wer liest was — die Trennung ist strikt

Direkt aus `pattern-domain-language`:

| Schicht | Feld | Konsumenten |
|---|---|---|
| **Rohdaten** | `user_prompt`, Emotion, Arousal | **Responder**, Salienz, EI |
| **Validierte Daten** | `prompt_resolved`, `reference_resolutions` | **Retrieval**, Agenten, CRUD |

> **Der Responder sieht `prompt_resolved` NIE.**

Sonst redet Nova dem User Worte in den Mund, die er nicht gesagt hat. Das wäre eine neue
Halluzinationsklasse — und zwar eine, die wir selbst gebaut hätten.

Konsument des umgeschriebenen Prompts ist das **Embedding** und die **Agenten**, sonst niemand.

---

> **Hinweis zur Aufteilung (19.09.2026):** §8 *Der Weg dorthin — Messung vor Bau* steht in [`novaberg-referenz-aufloesung_b.md`](novaberg-referenz-aufloesung_b.md).

## 9. Abhängigkeiten (alle MIT — Apache-2.0-kompatibel)

| Paket | Zweck | Lizenz | Größe | Risiko |
|---|---|---|---|---|
| `CharSplit` | Kompositum-Kopf (L1) | **MIT** | ~5 MB (ngram_probs.json) | keine — reines Python |
| `spaCy` + `de_core_news_sm` | POS/Morph (L0) | **MIT** | ~15 MB | ⚠ Python-3.12-Kompatibilität prüfen |
| *(Alternative)* `simplemma` / `HanTa` | Lemma ohne spaCy | **MIT** | klein | Fallback, falls spaCy zickt |

**Ausdrücklich NICHT:**

| Paket | Grund |
|---|---|
| `maverick-coref-de` | ⛔ **CC BY-NC-SA 4.0** — NonCommercial + ShareAlike. Nicht lesen, nicht einbinden. |
| `coreferee` | ⚠ MIT, kann Deutsch — aber getestet nur bis spaCy 3.5 / Python 3.11. Container läuft 3.12. **Nur wenn L1–L4 nachweislich nicht reichen.** YAGNI. |

---

> **Hinweis zur Aufteilung (19.09.2026):** §10 *Offene Entscheidungen* steht in [`novaberg-referenz-aufloesung_e.md`](novaberg-referenz-aufloesung_e.md), Abschnitt C.
