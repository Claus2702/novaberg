# Novaberg — Referenz-Auflösung (REF-KASKADE)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Mehrschichtige Referenz-Auflösung vor dem Retrieval
**Stand:** 11. Juli 2026, Chat 106
**Pfad:** `novaberg/docs/novaberg-referenz-aufloesung_k.md`
**Status:** Konzept. Kein Code. Voraussetzungen offen (siehe §10).

---

## 1. Das Problem

Nova löst Rückbezüge aus dem Gesprächsverlauf nicht auf.

| Beleg | Prompt | Novas Verhalten |
|---|---|---|
| Matcha | 8 Turns über Matcha-Pulver, dann *„schauen wir nochmal nach dem Pulver"* | Fragt zurück: Kakao oder anderes? |
| Grillkäse | *„Die andere ist die mit dem Grillkäse"* | Klassifikator: `rejected` |
| Liste | *„Was steht auf der Liste?"* (Notiz heißt `Einkauf`) | Findet nichts |

Ein Mensch löst das ohne Nachdenken. Der rationale, semantische, thematische Bezug ist
vollständig vorhanden — er steht nur nicht **im Satz**, sondern **im Verlauf**.

### 1.1 Es sind zwei Wurzeln, nicht eine

Die drei Belege sehen gleich aus. Sie sind es nicht:

| Klasse | Beispiel | Wurzel |
|---|---|---|
| **Referenz** | „das Pulver" → „Matcha-Pulver" | Der Referent steht im Verlauf, nicht im Satz. |
| **Vokabular-Mismatch** | „Liste" → Notiz `Einkauf` | Der Referent steht in der **DB** unter anderem Namen. |

Beide zusammen ergeben den Liste-Fall: *welche* Liste (Referenz) **und** wie heißt sie
wirklich (Mismatch).

**Wichtig — der Mismatch löst sich womöglich von selbst:** Wenn die Kaskade *„die Liste"*
zu *„Einkaufsliste"* auflöst, findet die **bestehende** bidirektionale LIKE-Suche des
Notizen-Agenten (AGT-FIX4, Chat 22: *„Einkaufsliste" findet „Einkauf"*) die Notiz bereits.
Der Mismatch verschwindet, weil der aufgelöste Referent das Kompositum trägt.

Das gilt nur, wenn im Verlauf je „Einkaufsliste" fiel. Fiel dort nur „Notiz Einkauf" und
der User sagt „Liste", bleibt echter Vokabular-Mismatch → das ist L3 (Embedding) oder L5
(Rückfrage). Kein separater Sprint nötig, aber ein bewusst offener Fall.

---

## 2. Einordnung: das Feld heißt Conversational Query Rewriting

Das Problem ist seit ~2019 systematisch bearbeitet. **CQR** erzeugt aus dem Roh-Input eine
de-kontextualisierte Anfrage, indem es den Verlauf einbezieht und Koreferenzen, Ellipsen und
Themenwechsel auflöst. Datensätze/Benchmarks: **CANARD**, **QReCC**, **TopiOCQA**, **TREC CAsT**.

Drei Befunde aus der Literatur, die unser Design tragen:

1. **Der Schritt gehört VOR das Retrieval.** Ohne Rewriting bekommt die Vektordatenbank eine
   kontextfreie Anfrage und liefert irrelevante Dokumente. Über 60 % der konversationellen
   Folgefragen tragen unaufgelöste Koreferenzen.
2. **CANARDs Methode ist unsere L1:** Schlüsselwörter aus dem Kontext extrahieren, den
   referierenden Ausdruck ersetzen.
3. **Latenz zählt.** Der Schritt sitzt auf dem kritischen Pfad jeder Antwort. Ein kleines,
   schnelles Modell reicht — kein Frontier-Modell.

**Nicht übernommen:** `maverick-coref-de` (Uni Hamburg, KONVENS 2025). Technisch das beste
deutsche Koreferenz-System — aber **CC BY-NC-SA 4.0** (NonCommercial + ShareAlike).
Unvereinbar mit Apache 2.0. Weder Code lesen noch einbinden. Das Paper darf gelesen werden,
Ideen sind nicht schutzfähig. **Clean Room.**

Und selbst mit Lizenz löste es nur eine unserer vier Schichten: Dokument-Koreferenz kennt
unsere Datenbank nicht, kann kein Entitäts-Grounding, ist auf Fließtext trainiert statt auf
Dialog-Turns. Der Vokabular-Mismatch bliebe ungelöst.

---

## 3. Die Leitidee: Generatoren und Selektoren

Der naive Kaskaden-Entwurf lässt jede Schicht **unabhängig** versuchen und bei Misserfolg an
die nächste weiterreichen. Das ist falsch — es verschenkt die Arbeit der billigen Schichten.

**Richtig:** Billige Schichten sind **Kandidaten-Generatoren** (hohe Trefferquote, geringe
Präzision). Teure Schichten sind **Selektoren** (hohe Präzision auf einer *bereits
eingegrenzten* Menge).

```
L0 Detektor    → gibt es überhaupt eine Referenz?         (Kostenbremse)
L1 Kompositum  → Kandidaten aus dem Verlauf               (Generator, µs)
L2 Entität     → Kandidaten aus Verlaufs-Entitäten + DB   (Generator, ms)
L3 Embedding   → rankt die Kandidaten aus L1+L2           (Selektor, ~10 ms)
L4 LLM         → entscheidet den Rest, Python verifiziert (Selektor, ~300 ms)
L5 Rückfrage   → Nova fragt SPEZIFISCH                    (ehrlicher Ausgang)
```

L3 sucht nicht selbst nach Referenten. L3 bekommt eine Liste und sortiert sie. Das macht die
teuren Schichten schnell *und* sicher: Sie können nichts erfinden, was L1/L2 nicht gesehen
haben.

**Ausnahme:** Findet L1+L2 **null** Kandidaten, darf L4 (LLM) einen aus dem Verlauf
vorschlagen — aber **nur** mit Turn-Beleg, den Python nachprüft (§7).

---

## 4. Der zentrale Defekt, den dieses Konzept vermeiden muss

> **Eine falsche Bindung ist schlimmer als gar keine.**

Bindet L1 *„die Liste"* an *„Preisliste"* aus Turn 3, geht ein **falsch aufgelöster, aber
syntaktisch perfekter** Prompt ins Retrieval. Nova antwortet dann selbstbewusst über die
falsche Sache — und **niemand merkt es**, weil kein Fehler geloggt wurde.

Das ist Halluzination *durch* Auflösung. Es ist der einzige Weg, wie dieser Sprint das System
schlechter machen kann als vorher.

Deshalb gilt, direkt aus `lesson_l_default-wie-fehlschlag`:

> **Ein Default darf nie wie ein Fehlschlag aussehen — und ein Fehlschlag nie wie ein Treffer.**

**Konsequenz:** Keine Schicht liefert einen Wert. Jede Schicht liefert einen **Zustand**:

| Zustand | Bedeutung | Folge |
|---|---|---|
| `GEFUNDEN` | Ein Kandidat über Schwelle **und** mit Abstand zum zweiten | Substitution, fertig |
| `UNSICHER` | Kandidaten da, aber keiner klar genug | **Eskalation** mit Kandidatenliste |
| `NICHTS` | Kein Kandidat über Schwelle | **Eskalation** ohne Kandidaten |

**Zwei fast gleich gute Kandidaten *sind* Unsicherheit.** Ein Schwellwert allein genügt
nicht — es braucht die **Marge** zum Zweitplatzierten. Ohne sie ist „UNSICHER" Geschmackssache.

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
`_ei_calc_character` seit `e54092d`. Keine Fernkopplung, kein Sonderweg, keine Kante zu drehen.
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

## 8. Der Weg dorthin — Messung vor Bau

Vier Schichten sind vier Wartungspfade und vier Drift-Quellen. Bevor wir sie bauen, wollen wir
wissen, **welche Schicht wie viel trägt.** Sonst bauen wir L1–L3 und stellen fest, dass in
90 % der Fälle doch L4 ran muss — dann wäre die Kaskade reiner Ballast.

### 8.1 Schritt 1 — Embedding-Diagnose (5 Minuten, kein Code, kein Risiko)

```python
# Cosinus-Ähnlichkeit mit dem LIVE-Modell
paare = [
    ("Liste",         "Notiz"),         # muss HOCH sein  — sonst ist L3 tot
    ("Einkaufsliste", "Notiz"),
    ("Matcha-Pulver", "Pulver"),        # muss HOCH sein
    ("Matcha-Pulver", "Kakaopulver"),   # muss NIEDRIGER sein als die Zeile darüber
    ("Liste",         "Fahrrad"),       # Kontrolle: muss NIEDRIG sein
]
```

**Abbruchkriterium:** Liegt `("Liste","Notiz")` nahe bei `("Liste","Fahrrad")`, ist das
Embedding für deutsche Semantik unbrauchbar. Dann ist L3 nicht der Sprint — dann ist der
Modellwechsel der Sprint.

**Ausweg, falls nötig:** BGE-M3 (MIT, 100+ Sprachen, dense **und** sparse in einem Modell —
bedient damit exakt unseren Notizen-Suchpfad) oder multilingual-e5-large (MIT). Beide auf
Ollama. **Aber:** Modellwechsel = **alles neu embedden** (KZG-Blobs in Redis, `lzg_knoten`,
`charakter_hash`). Eigener Migrations-Sprint. Nicht nebenbei.

### 8.2 Schritt 2 — Discovery-Audit

Läuft (Chat 106). Beantwortet: Wo wird das Embedding berechnet? Existiert der Entity-Layer
pro Turn (→ L2a)? Wo sind alle State-Init-Punkte?

### 8.3 Schritt 3 — SCHATTEN-Sprint (das Herzstück)

**Baue L0 + L1. Lass sie NICHTS verändern.** Sie schreiben nur ins Log:

```
REF/L0: Marker erkannt — text='die Liste' art=definite_nominal head='Liste'
REF/L1: 8 Turns durchsucht, Kandidaten: ['Einkaufsliste' (d=3, s=0.74)]
REF/L1: Status=GEFUNDEN — Kopf-Match, Marge 0.74 (kein Zweiter)
REF/SCHATTEN: würde ersetzen 'die Liste' -> 'Einkaufsliste'   [NICHT ANGEWENDET]
```

**Null Risiko.** Kein Verhaltenswechsel, kein Retrieval berührt, kein Prompt verändert.
Ein `SCHATTEN`-Flag in `config.py`, Default `true`.

Nach ein paar Tagen Alltagsbetrieb weißt du:

| Frage | Antwort aus dem Log |
|---|---|
| Wie oft feuert L0 überhaupt? | Die Kosten-Basis. Literatur sagt >60 % — stimmt das für **uns**? |
| Wie oft löst L1 allein? | Trägt die Python-Schicht — oder ist sie Deko? |
| Wo hätte L1 **falsch** gebunden? | Der Nachweis, dass die Marge nötig ist. |
| Welche Scores treten real auf? | **Die Schwellenwerte für L3 — gemessen statt geraten.** |

Das ist dieselbe Methode, die in Chat 105 den Kraft-1-Bug fand: **Erst die Zeile, dann der Fix.**
Fünf Minuten Diagnose-Log deckten sechzehn Chats blinde EI-Berechnung auf. Hier stehen ein paar
Tage Log gegen einen Sprint, der sonst auf Vermutungen gebaut wäre.

### 8.4 Schritt 4 — Scharfschalten, schichtweise

L1 scharf → messen → L2 → messen → L3 → messen → L4. **Eine Schicht pro Commit.**
Jede Schicht hat ein eigenes Flag. Jede kann einzeln abgeschaltet werden.

---

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

## 10. Offene Entscheidungen (vor Baubeginn zu klären)

| # | Frage | Blockiert |
|---|---|---|
| 1 | Ist `nomic-embed-text` für deutsche Semantik brauchbar? | **L3 komplett** |
| 2 | Existiert der Entity-Layer pro Turn? | L2a |
| 3 | Lemmatizer: spaCy (schwach bei Plural) oder `simplemma`/`HanTa`? | L0 |
| 4 | Läuft spaCy unter Python 3.12 im Container? | L0 |
| 5 | `n` = wie viele Turns rückwärts? (Vorschlag: 10, aus dem Schatten-Log kalibrieren) | L1–L4 |
| 6 | Kann die Rückfrage (L5) über den bestehenden Pfad? | L5 — **hängt am Loop-Fix Chat 106** |
| 7 | Wo genau wird das Prompt-Embedding berechnet? | Node-Position |

Fragen 2, 4 und 7 beantwortet Brudis Discovery-Audit. Frage 1 beantwortet die
Embedding-Messung. Fragen 3 und 5 beantwortet der Schatten-Lauf. Frage 6 beantwortet der
Live-Test des Loop-Fixes.

**Keine dieser Fragen wird geraten.**

---

## 11. Abgrenzung — was dieses Konzept NICHT löst

- **`PENDING-RELEVANZ`** — ob ein Prompt die Antwort auf eine **Rückfrage** ist, ist verwandt,
  aber nicht dasselbe. Eigener Eintrag, eigener Sprint.
- **`NOTIZ-BEFEHL-ALS-TITEL`** — der Klassifikator, der „Neue Notiz anlegen" als *Namen*
  speichert. Verwandte Wurzel (Meta-Befehl vs. Sach-Inhalt), aber ein anderer Node.
  ⚠ Er ist der **Auslöser** der Duplikate, die L5 überhaupt erst nötig machen.
- **Embedding-Migration** — falls Messung 8.1 negativ ausfällt: eigener Sprint, nicht hier.

---

## 12. Warum das ein eigener Beitrag ist

Die CQR-Literatur schreibt einen Prompt um. Sie hat keine Datenbank dahinter.

**Unsere L2 gleicht gegen tatsächlich existierende Objekte ab** — Notiz-Titel, Termine,
Direktiven. Ein Referent, der kein reales Objekt bezeichnet, wird verworfen statt geraten.
Das ist kein Nachbau von Maverick. Das ist **„Entität schlägt Embedding"**, angewandt auf die
Referenz-Auflösung — und es ist die These, die ein Paper trägt.

Dazu die Kaskade selbst: Generatoren billig, Selektoren teuer, jede Schicht mit drei
Zuständen, und ein LLM, das nur vorschlagen darf, während Python entscheidet.

**Nova soll nicht raten, was gemeint war. Sie soll es wissen — oder ehrlich fragen.**
