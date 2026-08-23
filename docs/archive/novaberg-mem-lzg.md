# Novaberg — Gedächtnis: Langzeitgedächtnis (LZG)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul Langzeitgedächtnis
**Stand:** 12. Juli 2026, Chat 107 (Embedding-Migration: Modellwechsel auf nomic-embed-text-v2-moe, ivfflat-Indizes entfernt, Retrieval-Schwelle 0.40)
**Pfad:** novaberg/docs/archive/novaberg-mem-lzg.md
**Berichtigt am 23.08.2026:** Diese Zeile nannte den Ort **vor** dem Verschieben ins Archiv. Der `Stand` oben bleibt unveraendert — er sagt, wann der **Inhalt** zuletzt galt, und daran hat sich nichts geaendert.
**Quellen:** nova-02-m-c.md
**Datei:** ~~`memory/lzg.py`~~ — mit P9 aus dem Repositorium entfernt
**Status:** **Archiviert am 02.08.2026 (Synapsen P9).** Das beschriebene Modul und die Tabelle `langzeitgedaechtnis` existieren nicht mehr. Der Synapsen-Umbau hat das Langzeitgedächtnis auf `lzg_knoten` und `lzg_kanten` umgestellt: Jede Erinnerung bleibt ein eigener Knoten, Verbindungen leben als gerichtete Kanten mit eigenem Verfall. Das Dokument bleibt als Beleg, wie das Aggregat-Modell gebaut war — die Ablösung ist ohne es nicht nachvollziehbar.
**Nachfolger:** `novaberg-memory-synapsen_k.md` (Konzept), `novaberg-memory.md` (Modul)

---

> **Hinweis (Chat 88): Synapsen-Umbau im Gang.**
> Das hier beschriebene LZG-Modell mit aggregierten Einträgen wird durch ein assoziatives Netz-Modell ersetzt — siehe Konzept-Dokument `novaberg-memory-synapsen_k.md`. Statt verdichteten Aggregat-Einträgen behält jeder ehemalige KZG-Eintrag seine Identität als Knoten in `lzg_knoten`, Verbindungen leben in `lzg_kanten`. `emotions_vektor` kehrt im neuen Schema zurück (in Chat 83 entfernt, weil mit verdichteten Punkten inkompatibel — diese Begründung entfällt im Knoten-Modell). Tabellen `lzg_knoten`/`lzg_kanten` sind seit P2 (Chat 88) im Schema vorhanden, aber leer. Schreibpfad wechselt erst mit P4, Lesepfad mit P5. Bis dahin bleibt `langzeitgedaechtnis` produktiv und wird in diesem Dokument beschrieben.

> **Hinweis (Chat 107, 12.07.2026): Embedding-Migration EMBEDDING-CASING-BLIND.**
> Das Embedding-Modell ist auf **`nomic-embed-text-v2-moe`** gewechselt (weiterhin 768 Dimensionen). Alle Embedding-Spalten des Bestands wurden per `server/tools/reembed_all.py` neu gerechnet, die Gewichte der `lzg_knoten` zurückgesetzt und `lzg_kanten` komplett neu aufgebaut — Befund und Beweiskette in `novaberg-embedding-casing-blind_k.md`, der Reset-Bruch in `novaberg-memory-synapsen_k.md`. Neue Wartungs-/Migrationsfunktionen: `knoten_embedding_aktualisieren` und `knoten_gewichte_zuruecksetzen` in `memory/lzg_knoten.py`; `embedding_cosine_alle_aktualisieren`, `kanten_alle_loeschen` und `kanten_alle_neu_aufbauen` in `memory/lzg_kanten.py`. Für jedes Speicherziel existiert seitdem eine benannte `embed_text_bauen()`-Funktion im jeweiligen Modul — **eine** Formel, Live-Pfad und Migrationstool rufen dieselbe (→ `novaberg-convention-embedding.md`).

## 1. Aufgabe

Das LZG ist Novas permanenter Speicher — der Ort, an dem verdichtetes Wissen über Monate und Jahre lebt. Es liegt in PostgreSQL mit pgvector für semantische Suche. Einträge verblassen nach der Ebbinghaus-Kurve, werden bei Wiederholung verstärkt und bei Unterschreitung eines Schwellwerts als inaktiv markiert — nie gelöscht.

Die Datei `memory/lzg.py` enthält zwei Funktionen: die Berechnung des effektiven Gewichts und den Kontext-Abruf für den Enricher. Die Schreiboperationen ins LZG laufen über den Pixie-Task `lzg_promotion` — das LZG wird nie direkt aus dem Chat-Graph beschrieben.

---

## 2. DB-Schema

Tabelle: `langzeitgedaechtnis`

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `id` | SERIAL | Primärschlüssel |
| `user_id` | VARCHAR(50) | User-Partition (`meister`, `nova`, …) |
| `character_id` | VARCHAR(50), DEFAULT `'nova'` | Charakter-Partition (Chat 62). Paar-Schema mit `user_id`. |
| `inhalt` | TEXT | Destillierter Inhalt (aus KZG-Promotion) |
| `dimension` | TEXT | kognition / emotion / werte / interessen / kommunikation / kontext |
| `gewicht` | DOUBLE | Basis-Gewicht (steigt bei Verstärkung, wird nie durch Decay reduziert) |
| `haeufigkeit` | INTEGER | Verstärkungszähler |
| `embedding` | VECTOR(768) | Embedding aus `EMBED_MODEL` (seit 12.07.2026 `nomic-embed-text-v2-moe`, Bestand re-embedded) |
| `arousal` | FLOAT | Energie-Intensität zum Zeitpunkt der Speicherung |
| `beobachter` | VARCHAR(20), DEFAULT `'user'` | `"user"` oder `"assistant"` (Chat 62). Bei Promotion aus dem KZG-Eintrag uebernommen. |
| `aktiv` | BOOLEAN | Soft-Delete Flag (Default: TRUE) |
| `verstaerkt_am` | TIMESTAMPTZ | Basis für Decay-Berechnung (Reset bei Verstärkung) |
| `created_at` | TIMESTAMPTZ | Erstellungszeitpunkt |
| `themen` | TEXT[] | Themen-Magnet aus dem KZG-Hash übernommen (Promotion, Chat 84). Cluster-Pfad: Vereinigung über Mitglieder. |
| `kzg_erstellt_am` | TIMESTAMPTZ | Original-Erstellungszeitpunkt der Erinnerung im KZG, getrennt vom DB-Default `erstellt_am` (Promotion-Zeitpunkt). |

**Hinweis (Chat 83):** `emotions_vektor` wurde aus dem LZG-Schema entfernt. Das Feld beschreibt eine Trajektorie über mehrere Turns (9 Bewegungs-Labels: `eskalation`, `plateau`, `absturz`, …). Eine LZG-Erinnerung ist ein verdichteter Punkt — eine Trajektorie hat dort keinen sinnvollen Anker. Im KZG, im Session-Turn-Format und im State-Feld lebt das Konzept weiter; dort hat es eine eindeutige Bedeutung pro Einzel-Erinnerung beziehungsweise pro Live-Verlauf.

**Hinweis (Chat 84):** Drei weitere Magnet-Spalten existieren im Schema, sind aber heute leer: `entitaet_ids INTEGER[]`, `timeline_id INTEGER FK timeline(id)`, `gedaechtnistyp VARCHAR(20)`. Befüllung wartet auf M5 (Salienz-Pfad-Erweiterung im KZG-Schreibpfad). Das vollständige Magnet-Modell ist in `novaberg-convention-magneten.md` §4 dokumentiert. Diese Schema-Beschreibung listet bewusst nur die heute befüllten Felder; der vollständige Schema-Refresh ist als eigener Backlog-Sprint vorgesehen (siehe `novaberg-backlog.md`).

**Indexes:**
- Partial Index `idx_lzg_aktiv` auf `(user_id, character_id) WHERE aktiv = TRUE` — alle Abfragen filtern auf Paar + aktive Einträge (Chat 62)
- **Kein Vektor-Index mehr** (seit 12.07.2026): Die ivfflat-Indizes auf `langzeitgedaechtnis` und `lzg_knoten` wurden entfernt (Commit `0fd54a1`) — ivfflat mit lists=100 bei ~300 Zeilen und probes=1 durchsuchte eine einzige Liste und lieferte Zufallstreffer statt Nearest Neighbors (IVFFLAT-RECALL-KOLLAPS, bugs.md). Bis ~10k Zeilen läuft die KNN-Suche exakt per Seq-Scan; erst danach wieder einen Index anlegen (dann lists ≈ rows/1000 und `ivfflat.probes` mitkalibrieren, siehe Kommentar in `db/init.sql`)

Zusätzliche EI-Metadaten-Spalten (intentionen, emotion, modus, sprach_stil, beziehungs_dynamik, tone) werden bei der Promotion aus dem KZG-Eintrag übernommen und per `ALTER TABLE ADD COLUMN` hinzugefügt.

### 2.1 Paar-Schema (Chat 62)

Alle Queries (Retrieval, Verstaerkung, Decay, Charakter-Hash) filtern jetzt auf das Gespraechspaar:

```sql
WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
```

**Migration (bereits ausgefuehrt):** Bestehende Eintraege mit `user_id='nova'` (Novas Beobachtungen unter dem alten Ein-User-Schema) wurden zu `user_id='meister', character_id='nova', beobachter='assistant'` umgeschrieben. Eintraege mit `user_id='meister'` bekamen per DEFAULT `character_id='nova'` und `beobachter='user'`. Ergebnis: eine durchgaengige Paar-Partition `(meister, nova)` mit sauberer Beobachter-Zuordnung.

---

## 3. Effektives Gewicht: Die Ebbinghaus-Formel

Das gespeicherte `gewicht` dokumentiert die Verstärkungshistorie — es steigt bei jeder Wiederholung und wird nie reduziert. Das *effektive* Gewicht wird bei jedem Zugriff live berechnet:

```python
effektives_gewicht = gewicht × e^(-decay_rate × tage_seit_verstärkung)
```

**`tage_seit_verstärkung`** wird aus `verstaerkt_am` berechnet — dem Zeitpunkt der letzten Verstärkung, nicht der Erstellung. Jede Verstärkung setzt den Decay-Timer zurück.

**Beispielwerte bei `EBBINGHAUS_DECAY_RATE = 0.0015`:**

| Basis-Gewicht | 1 Monat | 6 Monate | 1 Jahr | 3 Jahre |
|---------------|---------|----------|--------|---------|
| 0.80 (einmalig) | 0.77 | 0.61 | 0.46 | 0.15 |
| 2.00 (3× verstärkt) | 1.91 | 1.52 | 1.16 | 0.38 |
| 4.80 (10× verstärkt) | 4.59 | 3.65 | 2.78 | 0.91 |
| 8.80 (Kern-Interesse) | 8.42 | 6.69 | 5.10 | 1.67 |

**Inaktivierung:** Wenn das effektive Gewicht unter `EBBINGHAUS_MIN_GEWICHT` (0.1) fällt, markiert der Pixie-Task `lzg_decay` den Eintrag als `aktiv = FALSE`. Nicht gelöscht — nur aus aktiven Abfragen ausgeschlossen.

**Hinweis (Synapsen P2):** Die hier beschriebenen Konstanten `EBBINGHAUS_DECAY_RATE` und `EBBINGHAUS_MIN_GEWICHT` steuern den Decay der legacy `langzeitgedaechtnis`-Tabelle. Die neue `lzg_knoten`-Tabelle trägt eigene Decay-Konstanten `LZG_KNOTEN_DECAY_RATE` (0.0015) und `LZG_KNOTEN_MIN_GEWICHT` (0.1) in `config.py`. Beide Konstanten-Familien existieren parallel, bis P9 die alte Tabelle entfernt.

→ Vollständige Details: novaberg-pixie-decay.md — Ebbinghaus-Decay`

---

## 4. Kontext-Abruf (`lzg_entries_retrieve`)

Der Enricher ruft die relevantesten LZG-Einträge per pgvector-Similarity-Suche ab:

1. Embedding des User-Prompts als Suchvektor
2. `ORDER BY embedding <=> suchvektor` (Cosine Distance)
3. Nur `aktiv = TRUE` Einträge
4. Top-K (Default: 10)
5. Similarity-Filter: Nur Einträge mit Similarity ≥ 0.40 (kalibriert auf `nomic-embed-text-v2-moe`, Chat 107; vorher 0.5 im casing-blinden Raum)

**Hinweis (Chat 75):** Seit dem Reducer-Umbau (`novaberg-reducer-umbau_k.md`) liefert die Funktion eine Liste strukturierter `ContextEntry`-Dicts. Der unten gezeigte Format-String wird vom Formatter (`graph/format/memory_context.py`, `format_memory_entries()`) gebaut, nicht mehr von der Retrieve-Funktion selbst.

**Format pro Eintrag im Kontext (Formatter-Output):**

```
[LZG/interessen] (Gewicht: 2.15, Arousal: 70%, Vektor: aufbluehen): User ist begeistert von Astronomie und schwarzen Löchern
```

Das effektive Gewicht wird live berechnet — der Enricher sieht den aktuellen Wert, nicht den gespeicherten. Einträge mit niedrigem effektivem Gewicht tauchen zwar in der Suche auf (wenn semantisch relevant), liefern aber über das niedrige Gewicht ein Signal an den Responder: „Das ist alt und unbestätigt."

---

## 5. Schreibpfade

Das LZG wird nie direkt aus dem Chat-Graph beschrieben. Alle Schreiboperationen laufen über Pixie:

| Pfad | Task | Beschreibung |
|------|------|-------------|
| **Promotion** | `lzg_promotion` | KZG → LZG. Zwei-Call-Promotion (Klassifikation + Extraktion). Einziger Weg ins LZG. Seit Chat 84 (M3a) überträgt die Promotion `themen` und `kzg_erstellt_am` aus dem KZG-Hash. |
| **Verstärkung** | `lzg_promotion` | Bestehender LZG-Eintrag wird erneut angesprochen → `gewicht` steigt, `verstaerkt_am` wird zurückgesetzt. |
| **Decay** | `lzg_decay` | Berechnet effektives Gewicht für alle aktiven Einträge, markiert unter-Schwellwert als inaktiv. |
| **Charakter-Hash** | `charakter_hash` | Liest aktive LZG-Einträge (gewichtet nach effektivem Gewicht) und destilliert 4 Profile (kern_hash, adaptive_hash, beziehungsprofil, intentions_profil). |

---

## 6. Designentscheidungen

### Gewicht nie reduzieren

Das gespeicherte `gewicht` ist eine kumulative Historie: Jede Verstärkung addiert. Der Decay wird live berechnet, nie geschrieben. Das bedeutet: Wenn ein Eintrag nach 2 Jahren Inaktivität plötzlich wieder angesprochen wird, wird `verstaerkt_am` zurückgesetzt und der Decay startet neu — mit dem vollen kumulierten Gewicht. Langfristige Kern-Interessen (Gewicht 8.80 nach 20 Verstärkungen) überleben auch längere Pausen.

### Soft-Delete statt Hard-Delete

Inaktive Einträge bleiben in der Datenbank. `aktiv = FALSE` schließt sie aus Abfragen aus, aber sie existieren weiter. Gründe: Speicherplatz ist vernachlässigbar, Reaktivierung möglicherweise wertvoll, der Charakter-Hash könnte in Zukunft auch historische Einträge berücksichtigen.

### Kein direkter Schreibzugriff aus dem Graph

Die Trennung ist architektonisch erzwungen: Der Chat-Graph (HumanGraph) schreibt ins KZG. Pixie promotet ins LZG. Das verhindert, dass der Chat-Graph bei hoher Salienz direkt ins LZG schreibt und die Promotion-Logik (Klassifikation, Extraktion, Entity Resolution) umgeht.

---

## 7. Zusammenspiel

```
KZG (Redis)
    │ Salienz ≥ KZG_SALIENZ_HIGH → Promotion-Queue
    ▼
Pixie: lzg_promotion
    │ Zwei-Call-Promotion (Klassifikation + Extraktion)
    ▼
LZG (PostgreSQL)                 Pixie: lzg_decay
    │                                │
    │ ← Verstärkung bei             │ Effektives Gewicht < 0.1?
    │   Wiederholung                │ → aktiv = FALSE
    │                                │
    ▼                                ▼
Enricher                         Charakter-Hash
    │ lzg_entries_retrieve()         │ Destillation aus aktiven Einträgen
    │ Effektives Gewicht live        │ Gewichtet nach effektivem Gewicht
    ▼                                ▼
Responder                        Responder (als Persönlichkeit)
```

---

→ Gedächtnis-Konzept: novaberg-memory.md, Abschnitt 2.4
→ KZG (Eingangsstufe): novaberg-mem-kzg.md / novaberg-pixie-kzg.md
→ Ebbinghaus-Decay (Details): novaberg-pixie-decay.md
→ Zwei-Call-Promotion: novaberg-pixie-promotion.md
→ Charakter-Profile: novaberg-ei-character-profiles.md
→ Pixie-Tasks: novaberg-pixie.md
