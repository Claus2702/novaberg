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

## 5. Konvention 4: Ein Vektor repräsentiert genau einen Gegenstand

Trägt ein Feld mehrere Gegenstände — mehrere Themen, mehrere Begriffe —, bekommt **jeder seinen eigenen Vektor in einer eigenen Zeile**. Nicht einen gemittelten für alle.

**Der Grund ist geometrisch und nicht Geschmackssache.** Ein Vektor über mehrere Gegenstände liegt in ihrem Schwerpunkt, und der Schwerpunkt von fünf unverwandten Begriffen ist keinem davon nah. Die Suche findet ihn dann weder über den einen noch über den anderen.

**Gemessen am 19.08.2026** an der Bibliothek (`autonomous_wissen`, 249 aktive Einträge, Ø 4,37 Themen je Feld). 40 Fragen nach **einem** Thema, die richtige Antwort ist je Frage bekannt:

| Ziel des Vergleichs | richtige Antwort auf Rang 1 | Kosinus (Median) |
|---|---|---|
| Destillat des Eintrags | **6 / 40 — 15 %** | **0,2821** |
| das ganze Themenfeld | 26 / 40 — 65 % | 0,4564 |
| **ein Vektor je Thema** | **31 / 40 — 78 %** | **0,7425** |

Die mittlere Zeile ist die aufschlussreichere: Ein Vektor über das ganze Themenfeld liegt mit 0,4564 **knapp** über der Abweisungsschwelle von 0,40 — bei jeder Umformulierung der Frage kippt er darunter. Ein Vektor je Thema hat Abstand.

### Die Probe hängt nicht am Trennzeichen

**Die Frage ist nicht, ob ein Komma vorkommt, sondern ob das Feld eine Aufzählung oder eine Aussage ist.**

| | Beispiel | Gegenstände |
|---|---|---|
| **Aufzählung** — je Glied ein Vektor | *„Mut, Vertrauen"* · *„Begegnung, Entropie, Informationsaustausch, Ontologie"* | mehrere |
| **Aussage** — ein Vektor | *„Nova hat erklärt, dass sie die Frage nicht auflösen wird"* | einer |

Beide tragen Kommas. Eine Kommazählung über sieben Vektorspalten meldete am 19.08.2026 `lzg_knoten.inhalt` mit **2315 von 2545** Feldern als Verdachtsfall — es sind Sätze, und es ist **kein** Verstoß. Wer das Zeichen zählt statt der Sache, bekommt eine Zahl, die dreimal zu hoch ist.

> **Vier Werte des Feldes ansehen kostet eine Minute und ist nicht ersetzbar.** Eine Aufzählung erkennt man daran, dass ihre Glieder nebeneinander stehen und keines vom anderen abhängt.

### Und sie hebt die Frage nach dem langen Text nicht auf

Wer mit einem **langen** Text sucht, braucht ein Ziel in seiner Größenordnung. Der Rückweg der Bibliothek fragt mit Ø 713 Zeichen (n=924); ein Themenvektor von Ø 23 Zeichen ist für ihn die umgekehrte Asymmetrie. **Ein Vektor je Thema ersetzt keinen Inhaltsvektor** — er ersetzt den gemittelten Themenvektor.

---

## 5a. Der Bestand — Zustandssätze

> **Dieser Abschnitt hieß bis zum 19.08.2026 §5.** Er trägt jetzt §5a, weil Konvention 4 vor ihn gehört — die Regeln stehen beieinander, der Bestand dahinter. Geprüft: Kein Dokument im Repositorium und keins daneben verwies auf `§5`; die vorhandenen Verweise nennen `§2` und `§2–§4` und sind unberührt.

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

- **19.08.2026** — **Konvention 4 neu: Ein Vektor repräsentiert genau einen Gegenstand.** Gemessen an der Bibliothek: Bei einer Frage nach *einem* Thema findet ein Vektor über das Destillat den eigenen Eintrag in 15 % der Fälle auf Rang 1 (Kosinus-Median 0,2821 — unterhalb der eigenen Schwelle), ein Vektor je Thema in 78 % (Median 0,7425). Dazu die Probe, die **nicht am Komma hängt**: Aufzählung oder Aussage. Der bisherige §5 (Bestand) trägt seither §5a; keine Verweise betroffen.

- **v0.2 — 16.08.2026:** Erstmals gegen den Code gehalten. **Konvention 1 und 3 sind eingelöst**, und zwar auch in ihren scharfen Teilen: Das Wartungswerkzeug importiert die Bauer, statt eigene Formeln zu führen, und die Begründung für den entfernten `valenz`-Token steht im Docstring. **Konvention 2 ist zur Hälfte gebaut** — die Prüfung vor einem Lauf steht, das tägliche Vitalzeichen fehlt, und das ist die Hälfte, die den ursprünglichen Defekt gefunden hätte. **Der Geltungsbereich war nicht nachgezogen:** `services/wissensspeicher.py` ist nach dieser Konvention entstanden, folgt ihrer Form und stand nicht in ihrer Aufzählung — mit der Folge, dass 390 Vektoren aus dem Re-Embedding-Werkzeug fielen, ohne dass etwas anschlug. Neu §5 mit dem Bestand, ausdrücklich als beschreibend markiert.
- **v0.1 — 12.07.2026, Chat 107:** Erstfassung aus drei Fehlerklassen mit derselben Wurzel — der Vektor als Nebensache seines Textes behandelt.
