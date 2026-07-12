# Novaberg — Embedding-Konventionen

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Verbindliche Konventionen für Embedding-Texte, Embedding-Modelle und die Grenze zwischen Vektor und strukturierten Feldern
**Stand:** 12. Juli 2026, Chat 107
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
- Pro Speicherziel existiert **eine** benannte `embed_text_bauen()`-Funktion im jeweiligen Modul (`memory/lzg_knoten.py`, `agents/kzg/speicher.py`, `memory/ziele.py`, `memory/repositories/entitaeten_repository.py`, `memory/repositories/fakten_repository.py`, `agents/delegation/akte.py`). Live-Pfad **und** Migrations-/Wartungstools rufen dieselbe Funktion. Dann *kann* es keine zwei Formeln mehr geben.
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

---

## 4. Konvention 3: Was man exakt vergleichen kann, gehört nicht in einen Vektor

Metadaten (Valenz, Zeit, Ort, IDs, Flags) machen den Vektor **unschärfer, nicht schärfer**.

**Arbeitsteilung:**

- Der **Vektor** findet den Kandidatenraum (semantische Nähe).
- **Strukturierte Felder** entscheiden danach exakt (Filter, Ranking, Joins).

**Anlass:** `valenz` wurde aus dem KZG-Embed-Text entfernt. Bei 81 % „positiv" war es ein nahezu konstanter Token — er verschiebt den gesamten Raum in eine Richtung und kostet Trennschärfe genau dort, wo sie gebraucht wird. Wer nach Valenz filtern will, filtert auf das persistierte Feld, nicht auf ein einembeddetes Wort.

**Prüffrage im Review:** „Würde ich auf dieses Merkmal je exakt filtern oder sortieren wollen?" Wenn ja: strukturiertes Feld, nicht Embed-Text.

---

## 5. Querverweise

```
→ novaberg-embedding-casing-blind_k.md — Befund, Beweiskette, Migrationsentscheidung
→ novaberg-memory-synapsen_k.md §9 — Gewichts-Reset 12.07.2026 (Bruch in der Historie)
→ novaberg-mem-kzg.md §6 — KZG-Embed-Formel (Thema/Aussage, ohne valenz)
→ novaberg-bugs.md — EMBEDDING-CASING-BLIND, IVFFLAT-RECALL-KOLLAPS, ENTITAET-EMBED-DREIFACH
→ novaberg-backlog.md — VITALZEICHEN (Embedding-/Retrieval-Proben), GESPRAECH-ARCHIV-LEER
```
