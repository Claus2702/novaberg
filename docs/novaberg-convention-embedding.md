# Novaberg — Embedding-Konventionen

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Verbindliche Konventionen für Embedding-Texte, Embedding-Modelle und die Grenze zwischen Vektor und strukturierten Feldern
**Stand:** 16. August 2026 (gegen den Code geprüft: Konvention 1 und 3 eingelöst, Konvention 2 zur Hälfte; ein siebter Speicher in den Geltungsbereich aufgenommen). Davor: 12. Juli 2026, Chat 107
**Pfad:** novaberg/docs/novaberg-convention-embedding.md
**Typ:** Convention
**Anlass:** EMBEDDING-CASING-BLIND (Befund und Beweiskette: `novaberg-embedding-casing-blind_k.md`), Migration 12.07.2026

---

## 1. Motivation

Chat 107 hat drei Fehlerklassen rund um Embeddings aufgedeckt, die alle dieselbe Wurzel haben: Der Vektor wurde behandelt wie eine Nebensache seines Textes — dabei ist er ein persistiertes Artefakt mit eigenen Konsistenz-Anforderungen.

- Bei `delegations_akten` fehlte die `zusammenfassung` im Schema, bei `entitaeten` existierten **drei** verschiedene Embed-Formeln für dieselbe Spalte (ENTITAET-EMBED-DREIFACH): Ein Re-Embedding hätte einen zweiten Mischraum erzeugt — nicht altes gegen neues Modell, sondern alte Formel gegen neue Formel.
- Das Embedding-Modell selbst war vier Monate lang defekt (`embed("Hund") == embed("Katze")` bit-identisch), ohne dass irgendein Bauteil einen Fehler meldete.
- `valenz` stand im KZG-Embed-Text und hat den Vektorraum verschoben statt geschärft.

Daraus folgen drei verbindliche Konventionen.

---

## 2. Konvention 1: Ein Embedding-Text MUSS aus dem persistierten Zustand rekonstruierbar sein

Sonst ist der Vektor eine **Einbahnstraße**: nie wieder erzeugbar, nie prüfbar, nie migrierbar.

**Konkret heißt das:**

- Jedes Feld, das in den Embed-Text eingeht, ist im selben Datensatz (Hash, Zeile) persistiert.
- Pro Speicherziel existiert **eine** benannte `embed_text_bauen()`-Funktion im jeweiligen Modul (`memory/lzg_knoten.py`, `agents/kzg/speicher.py`, `memory/ziele.py`, `memory/repositories/entitaeten_repository.py`, `memory/repositories/fakten_repository.py`, `agents/delegation/akte.py`, `services/wissensspeicher.py`). Live-Pfad **und** Migrations-/Wartungstools rufen dieselbe Funktion. Dann *kann* es keine zwei Formeln mehr geben.
- **Die Aufzählung ist ein Pflichtteil und wird nachgezogen.** Sie ist immer kürzer als die Wirklichkeit: `services/wissensspeicher.py` ist nach dieser Konvention entstanden und stand vier Wochen nicht darin — mit der Folge, dass sein Speicher aus dem Wartungswerkzeug fiel, ohne dass etwas anschlug.
- Wer ein neues Embedding-Feld einführt, schreibt zuerst die `embed_text_bauen()`-Funktion und stellt sicher, dass ihre Eingaben persistiert sind — nicht umgekehrt.

**Prüffrage im Review:** „Kann `reembed_all.py` diesen Vektor aus der Datenbank/Redis allein neu erzeugen?" Wenn nein, ist der Schreibpfad defekt, nicht das Tool.

---

## 3. Konvention 2: Casing-Eingangsprüfung für jedes Embedding-Modell

**Bevor ein Embedding-Modell produktiv geht (und als tägliches Vitalzeichen):**

```
embed("Hund") == embed("Katze")  bit-identisch  →  durchgefallen
```

Der Fehler hinter EMBEDDING-CASING-BLIND saß **nicht im Modell**, sondern in der GGUF-Konvertierung: Großgeschriebene Wörter kollabierten zu `[UNK]`-Ketten, deutsche Substantive verschwanden aus jedem Vektor. Das kann jedem Modell wieder passieren — bei jedem Pull, jeder Quantisierung, jedem Konverter-Update. Das Modell liefert dabei weiterhin 768 saubere Floats; kein Bauteil meldet einen Fehler.

Ergänzend zur Identitätsprüfung: bekannte Paraphrasen-Paare und Fremd-Paare aus der Kalibrierung nachmessen (`sim(paraphrase) > sim(fremd)`), Referenzwerte nach jedem Re-Embedding neu erheben. Siehe VITALZEICHEN (Backlog) — die Embedding-Probe hätte den Defekt an jedem einzelnen Tag der vier Monate in einer Sekunde gefunden.

> ⚠ **Die Konvention verlangt zwei Dinge, und nur eines ist gebaut** (16.08.2026 geprüft). Die Identitätsprüfung **vor** einem Lauf steht: `tools/reembed_all.py` embeddet „Hund" und „Katze" über den regulären Pfad und bricht bei Bit-Gleichheit ab. Das **tägliche Vitalzeichen** gibt es nicht — kein periodischer Agent führt die Probe.
>
> **Und die fehlende Hälfte ist die, auf die es ankommt.** Der Satz oben sagt es selbst: Der Defekt lief vier Monate, und ein Re-Embedding-Lauf findet ihn erst, wenn ohnehin jemand migriert. Was ihn am Tag seines Entstehens gefunden hätte, ist die tägliche Probe.

---

## 4. Konvention 3: Was man exakt vergleichen kann, gehört nicht in einen Vektor

Metadaten (Valenz, Zeit, Ort, IDs, Flags) machen den Vektor **unschärfer, nicht schärfer**.

**Arbeitsteilung:**

- Der **Vektor** findet den Kandidatenraum (semantische Nähe).
- **Strukturierte Felder** entscheiden danach exakt (Filter, Ranking, Joins).

**Anlass:** `valenz` wurde aus dem KZG-Embed-Text entfernt. Bei 81 % „positiv" war es ein nahezu konstanter Token — er verschiebt den gesamten Raum in eine Richtung und kostet Trennschärfe genau dort, wo sie gebraucht wird. Wer nach Valenz filtern will, filtert auf das persistierte Feld, nicht auf ein einembeddetes Wort.

**Prüffrage im Review:** „Würde ich auf dieses Merkmal je exakt filtern oder sortieren wollen?" Wenn ja: strukturiertes Feld, nicht Embed-Text.

---

## 5. Der Bestand — Zustandssätze

> ⚠ **Dieser Abschnitt beschreibt, er legt nicht fest.** Er wird nachgezogen, wenn sich der Code ändert. Die Regeln stehen in §2 bis §4.

`[gemessen]` — 16. August 2026:

| Konvention | Zustand |
|---|---|
| **1** — eine `embed_text_bauen()` je Speicher | ✅ Alle sieben Module tragen genau eine. `tools/reembed_all.py` **importiert dieselben Funktionen**, statt eigene Formeln zu führen. |
| **2** — Casing-Prüfung | 🔶 vor dem Lauf gebaut, als tägliches Vitalzeichen nicht (→ `VITALZEICHEN`) |
| **3** — Metadaten nicht in den Vektor | ✅ `valenz` ist aus dem KZG-Embed-Text entfernt, mit Begründung im Docstring des Bauers |

**Eine offene Stelle:** `autonomous_wissen.themen_embedding` — **390 von 390 Zeilen belegt** — wird von `tools/reembed_all.py` nicht erfasst. Der Speicher folgt der Form von Konvention 1 (eigener benannter Bauer, aus `zusammenfassung` rekonstruierbar), aber die Prüffrage aus §2 ist für ihn mit **nein** zu beantworten. Bei einem Modellwechsel bliebe er im alten Vektorraum zurück, während die übrigen migrieren — ein zweiter Mischraum, also genau der Fall, aus dem diese Konvention entstanden ist. → `REEMBED-WISSENSSPEICHER`

---

## 6. Querverweise

```
→ novaberg-embedding-casing-blind_k.md — Befund, Beweiskette, Migrationsentscheidung
→ novaberg-memory-synapsen_k.md §9 — Gewichts-Reset 12.07.2026 (Bruch in der Historie)
→ novaberg-mem-kzg.md §6 — KZG-Embed-Formel (Thema/Aussage, ohne valenz)
→ novaberg-bugs.md — EMBEDDING-CASING-BLIND, IVFFLAT-RECALL-KOLLAPS, ENTITAET-EMBED-DREIFACH
→ novaberg-backlog.md — VITALZEICHEN (Embedding-/Retrieval-Proben), GESPRAECH-ARCHIV-LEER
```

---

## Versionshistorie

- **v0.2 — 16.08.2026:** Erstmals gegen den Code gehalten. **Konvention 1 und 3 sind eingelöst**, und zwar auch in ihren scharfen Teilen: Das Wartungswerkzeug importiert die Bauer, statt eigene Formeln zu führen, und die Begründung für den entfernten `valenz`-Token steht im Docstring. **Konvention 2 ist zur Hälfte gebaut** — die Prüfung vor einem Lauf steht, das tägliche Vitalzeichen fehlt, und das ist die Hälfte, die den ursprünglichen Defekt gefunden hätte. **Der Geltungsbereich war nicht nachgezogen:** `services/wissensspeicher.py` ist nach dieser Konvention entstanden, folgt ihrer Form und stand nicht in ihrer Aufzählung — mit der Folge, dass 390 Vektoren aus dem Re-Embedding-Werkzeug fielen, ohne dass etwas anschlug. Neu §5 mit dem Bestand, ausdrücklich als beschreibend markiert.
- **v0.1 — 12.07.2026, Chat 107:** Erstfassung aus drei Fehlerklassen mit derselben Wurzel — der Vektor als Nebensache seines Textes behandelt.
