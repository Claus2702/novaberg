# Novaberg — Pixie-Agent: KZG-Agent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** KZG-Agent — LangGraph-Subgraph für Kurzzeitgedächtnis
**Stand:** 16. Mai 2026, Chat 88 (Synapsen P3 — neuer Node `magnete_aufloesen` zwischen `schwelle_pruefen` und `verdichten`, KZG-Subgraph jetzt 5 Nodes)
**Pfad:** novaberg/docs/novaberg-pixie-kzg.md
**Quellen:** nova-02-m-b.md (KZG-Agent-Abschnitte)

---

## 1. Aufgabe

Der KZG-Agent ist die Fachabteilung für Novas Kurzzeitgedächtnis. Er empfängt eingehende Turns über den Dispatcher, entscheidet WAS und WIE ins Gedächtnis fließt, verdichtet den User-Turn zu einem destillierten Kern, erzeugt das Embedding, schreibt einen eigenständigen Eintrag und befüllt Promotion- und Shadow-Queue. Seit Chat 64 wird parallel zum Schreiben die thematische Verstärkung verwandter Bestandseinträge ausgelöst.

Die Salienz bewertet OB etwas relevant ist — der KZG-Agent entscheidet WAS damit passiert. Trennung der Verantwortlichkeiten: Bewertung in der Salienz, Verdichtung im KZG-Agent, Extraktion im WissensAgent.

**Dateien:** `agents/kzg/agent.py`, `agents/kzg/magnete.py`, `agents/kzg/verdichtung.py`, `agents/kzg/speicher.py`, `agents/kzg/queues.py`, `agents/kzg/dispatch.py` (`agents/kzg/aehnlichkeit.py` in Chat 64 entfernt)

---

## 2. Subgraph-Überblick

Der KZG-Agent ist ein 5-Node-LangGraph-Subgraph:

```
Schwelle prüfen → Magnete auflösen → Verdichten → Speichern → Queues
```

| Node | Datei | Aufgabe |
|------|-------|---------|
| `schwelle_pruefen` | `agent.py` | Salienz-Score gegen `KZG_SALIENZ_MINIMUM`. Unter Schwelle → kein LLM-Call, kein Store. |
| `magnete_aufloesen` | `magnete.py` | Resolved Salience-Roh-Strings (`entitaeten_roh`, `zeitausdruck_roh`) zu `entitaet_ids` (via `EntityResolutionService`) und `timeline_id` (via `zeit_parsen_vektor` + `TimelineRepository`, ggf. Anlage eines `erinnerungs_anker`). Übernimmt eine im selben Turn vom TimelineAgent ins Clipboard geschriebene `timeline_id`, statt einen eigenen Anker anzulegen. |
| `verdichten` | `verdichtung.py` | LLM-Call: Erzeugt `kern` — konkreter Satz mit allen Namen, Orten, Zahlen. |
| `speichern` | `speicher.py` | Embedding erzeugen, eigenständigen Eintrag mit Magnet-Feldern schreiben, thematische Verstärkung verwandter Bestandseinträge in der Paar-Partition. TTL nach Salienz (7/14/30 Tage). Pipeline-Log-Eintrag nach erfolgreichem `hset` (Synapsen P1.1). |
| `queues_befuellen` | `queues.py` | Promotion-Queue + Shadow-Queue + Dirty-Flag. |

**Routing:**

```
schwelle_pruefen
  ├─ abgelehnt (Score < Schwelle) → END
  └─ angenommen → magnete_aufloesen → verdichten → speichern → queues_befuellen → END
```

`magnete_aufloesen` läuft bewusst VOR `verdichten` — defensiv: Resolver-Fehler verwerfen den teuren LLM-Call nicht, und bei Abbruch danach bleibt kein Waisenkind in der Timeline (Synapsen P3, siehe Code-Kommentar in `agent.py`).

Der Node `aehnlichkeit_pruefen` und die Datei `aehnlichkeit.py` wurden in Chat 64 entfernt. Es gibt keine Embedding-basierte Schreibzeit-Deduplizierung mehr — jeder Turn landet als eigenständiger Eintrag.

---

## 3. Schwelle

Salienz-Filter am Eingang des Subgraphs:

```python
KZG_SALIENZ_MINIMUM = 0.3   # Chat 64: von 0.5 gesenkt

if salienz_score < KZG_SALIENZ_MINIMUM:
    return AgentResult(status="abgelehnt", ergebnis="Salienz unter Schwelle")
```

Unter der Schwelle wird kein LLM-Call ausgelöst, kein Embedding erzeugt, nichts gespeichert. Smalltalk-Turns behalten den rohen `inhalt` in der Session — ein destillierter `kern` für "Hallo" hat keinen Mehrwert. Die Senkung der Untergrenze von 0.5 auf 0.3 (Chat 64) lässt informative Alltagsaussagen ("Ich mag Schnittlauch") ins KZG; sie sterben durch TTL, wenn sie nicht thematisch verstärkt werden.

---

## 4. Verdichten

Der einzige LLM-Call im KZG-Agent. Erzeugt den `kern`:

- Konkreter Satz, kein Stichwort
- ALLE Namen, Orte, Zahlen, Beziehungen erhalten
- Inhalt, nicht Emotion ("Anna ist nach München gezogen", nicht "User ist traurig über Annas Umzug")
- Kurz — ein Satz, maximal zwei

**Input:** User-Prompt + Assistenten-Antwort (als Lagebild).
**Output:** Ein `kern`-String.

---

## 5. Speichern

**Eigenständiger Eintrag (immer):** Jeder Turn oberhalb der Salienz-Schwelle wird als neuer Eintrag in Redis abgelegt. Hash mit `inhalt` (kern), `themen`, `salienz`, `haeufigkeit` (1), `gedaechtnistyp`, `dimension`, `intentionen`, `emotion`, `modus`, `arousal`, `emotions_vektor`, `embedding`, `erstellt_am`. TTL nach Salienz-Stufe (siehe §7 Konfiguration und novaberg-mem-kzg.md §2a).

Seit Chat 64 entfällt die Schreibzeit-Deduplizierung. Jeder Kern bleibt exakt erhalten — Zusammenführung passiert erst bei der Cluster-Promotion ins LZG.

**Thematische Verstärkung (verwandte Bestandseinträge):** Direkt nach dem Schreiben durchsucht `_thematisch_verstaerken()` die gesamte Paar-Partition (`kzg:{user_id}:{character_id}:*`) nach Einträgen mit Themen-String-Overlap (case-insensitive, exakter Match auf den `themen`-Tags). Treffer bekommen einen gedämpften Salienz-Boost und TTL-Auffrischung — der `inhalt` und das `embedding` bleiben unangetastet.

```
boost_roh    = aktuelle_salienz / KZG_VERSTAERKUNG_DIVISOR
remaining    = max(0, KZG_SALIENZ_CAP - alte_salienz)
ratio        = remaining / KZG_SALIENZ_CAP
daempfung    = sin(ratio × π/2) ^ KZG_SALIENZ_DAEMPFUNG_EXP   # sin^0.6
boost        = boost_roh × daempfung
neue_salienz = alte_salienz + boost
neue_haeufigkeit = alte_haeufigkeit + 1
neuer_TTL    = max(verbleibend, TTL der neuen Salienz-Stufe)
```

`KZG_VERSTAERKUNG_DIVISOR = 2.0`, `KZG_SALIENZ_CAP = 10.0`, `KZG_SALIENZ_DAEMPFUNG_EXP = 0.6`. ~~Die sin^0.6-Kurve verhindert Salienz-Explosion bei häufig wiederkehrenden Themen~~ (selbe Kurvenfamilie wie Arousal-Glättung, Chat 61).

> **⚠ Widerlegt — die Kurve dämpft im Betriebsbereich nicht.** Sie rechnet gegen `KZG_SALIENZ_CAP = 10.0`, während `salienz` auf **0.0–1.0** lebt. Gemessene Dämpfung dort, wo die TTL- und Promotions-Entscheidungen fallen: 0.99933 bei Salienz 0.30, 0.99637 bei 0.70, 0.99259 bei 1.00 — **unter 1 %**. Faktisch die Identität; die Salienz wächst näherungsweise um Faktor 1.5 je Verstärkung und verlässt nach zwei Verstärkungen ihren Wertebereich. → Backlog **`KZG-SALIENZ-SKALENBRUCH`** (Ursache und Formel), **`KZG-SALIENZ-BOOST-OHNE-DECKEL`** (Korpusverteilung). Der Satz bleibt hier als das stehen, was er war: die Absicht des Entwurfs, nicht sein Verhalten.

Seit Chat 60: `dispatch_kzg()` ruft nicht mehr `session_turn_annotate()` direkt auf. Stattdessen schreibt er den `kern` in `state["session_turn_kern"]`. Der Dispatcher sammelt den Kern ein und schreibt den Session-Turn vollständig.

### Rückgabe an den Dispatcher

`dispatch_kzg(state, writes)` gibt ein Dict mit **drei Schlüsseln** zurück:

- **`kzg_verarbeitet`** — Anzahl der in diesem Lauf verarbeiteten Salienz-Segmente.
- **`kzg_neue_keys`** — Redis-Keys der neu angelegten Einträge, in Segment-Reihenfolge.
- **`kzg_verstaerkte_keys`** — Redis-Keys der thematisch verstärkten Nachbar-Einträge (§5), über alle Segmente des Laufs.

**Beide Rückgabepfade tragen dieselben drei Schlüssel.** Auch der Registry-Miss-Pfad — wenn der KzgAgent nicht in der Registry steht — liefert `kzg_verarbeitet: 0` plus zwei leere Listen statt eines verkürzten Dicts. Ein Aufrufer mit direktem Index-Zugriff läuft auf keinem Pfad in einen `KeyError`.

**Neuanlage und Verstärkung sind zwei getrennte Listen** und werden nicht zusammengeführt: Der neue Eintrag entsteht aus diesem Turn, der verstärkte Nachbar stammt aus einem früheren und bekommt hier nur Gewicht. Der Dispatcher nimmt beide entgegen und protokolliert sie, verwendet sie aber noch nicht.

**Kardinalität:** Die Listen enthalten die Keys **eines** Graph-Laufs — je Salienz-Segment ein Subgraph-Durchlauf. Pro Konversations-Turn läuft `dispatch_kzg()` zweimal (HumanGraph und CharacterGraph, unterschieden über `beobachter`), mit unabhängiger Segmentzahl je Lauf: Pfad 1 bewertet den Nutzer-Prompt, Pfad 2 Novas Antwort.

**Fehlender Key — `info` oder `warning`, und der Unterschied ist die Aussage:** Bleibt ein Segment ohne Key, weil es **regulär unter der Salienz-Schwelle abgelehnt** wurde (`status == "abgelehnt"`), steht eine `info`-Zeile im Log — Normalfall, **kein Defektsignal**. Fehlt der Key **ohne** diesen Status, steht eine `warning` mit `status` und `speicher_status` — **das** ist das Defektsignal. Ein verstärkter Eintrag ohne `key`-Feld ist ebenfalls `warning`. Wer die `info`-Zeilen für Fehler hält, sucht einen Defekt, der keiner ist.

---

## 6. Queues

### Shadow-Queue Push (bei Salienz >= 0.7)

Intention aus der Salienz wird auf eine Pixie-Aufgabe gemappt:

| Intention | Shadow-Aufgabe |
|-----------|---------------|
| `recherche_vertiefen`, `reflexion`, `gemeinsam_eruieren`, `information_erfragen` | `recherche` |
| `information_teilen` | `vertiefen` |
| `emotionaler_ausdruck`, `hilferuf` | `nachfragen` |
| `smalltalk`, `bestätigung`, `abschluss`, `humor`, ... | Keine Aufgabe |

Bei Verstärkung mit Häufigkeit >= 3 und Salienz >= 0.7 → `vertiefen`.

### Promotion-Queue Push (bei Salienz >= KZG_SALIENZ_HIGH)

Wenn Salienz eines Eintrags >= 0.7 → Promotion-Queue (`queue:{user_id}`). Pixie arbeitet diese Queue mit höchster Priorität ab. Der frühere Schwellwert `PROMOTION_THRESHOLD = 0.8` wurde in Chat 64 durch `KZG_SALIENZ_HIGH` abgelöst.

### Dirty-Flag

Jeder Schreibvorgang setzt `hash_dirty:{user_id}` auf `"1"`. Pixie prüft das Flag für Charakter-Hash-Destillation.

---

## 7. Nova-Guard

`user_id == "nova"` → keine Shadow-Queue-Einträge (Feedback-Loop-Schutz, O9b). Verhindert, dass Novas eigene KZG-Einträge Pixie-Aufgaben auslösen, die wiederum KZG-Einträge erzeugen würden.

---

## 8. Konfiguration

| Konstante | Wert | Pfad | Beschreibung |
|-----------|------|------|-------------|
| `KZG_SALIENZ_MINIMUM` | 0.3 | `config.py` | Agent-Eingangsfilter — Chat 64: von 0.5 gesenkt |
| `KZG_SALIENZ_MID` | 0.5 | `config.py` | Schwelle für mittlere TTL (14 Tage) — Chat 64 neu |
| `KZG_SALIENZ_HIGH` | 0.7 | `config.py` | Schwelle für hohe TTL + Promotion-/Shadow-Queue |
| `KZG_SALIENZ_CAP` | 10.0 | `config.py` | Asymptotischer Cap der thematischen Verstärkung — Chat 64 neu |
| `KZG_SALIENZ_DAEMPFUNG_EXP` | 0.6 | `config.py` | Exponent der sin-Dämpfungskurve — Chat 64 neu |
| `KZG_TTL_LOW_SEKUNDEN` | 604800 (7 Tage) | `config.py` | Salienz 0.3–0.5 |
| `KZG_TTL_MID_SEKUNDEN` | 1209600 (14 Tage) | `config.py` | Salienz 0.5–0.7 — Chat 64 neu |
| `KZG_TTL_HIGH_SEKUNDEN` | 2592000 (30 Tage) | `config.py` | Salienz >= 0.7 |
| `KZG_VERSTAERKUNG_DIVISOR` | 2.0 | `config.py` | Roh-Boost-Divisor (vor sin^0.6-Dämpfung) |
| `KZG_VERTIEFUNG_HAEUFIGKEIT` | 3 | `config.py` | Häufigkeits-Schwelle für `vertiefen`-Trigger |
| `EMBEDDING_DIM` | 768 | — | nomic-embed-text Dimensionen |

`SIMILARITY_THRESHOLD` und `PROMOTION_THRESHOLD` in `memory/kzg.py` existieren noch als Konstanten, werden aber von der KZG-Schreib-Pipeline nicht mehr genutzt. Der Promotion-Push gegen die Queue läuft jetzt über `KZG_SALIENZ_HIGH`.

---

Verwandte Dokumente:
- Pixie-Agenten-Übersicht: `novaberg-pixie.md`
- PromotionAgent (Promotion-Ziel): `novaberg-pixie-promotion.md`
- DecayAgent (Ebbinghaus): `novaberg-pixie-decay.md`
- CharakterAgent (Hash-Destillation): `novaberg-pixie-character-hash.md`
