# Reducer-Umbau — Strukturierter memory_context

**Status:** Konzept
**Eröffnet:** Chat 74
**Bezug:** ENRICHER-DUP, Echo-Bug, RESP-DEAD, künftige Akten-Architektur (Backlog)

---

## 1. Motivation

Heute baut der Enricher den `memory_context` als **vorformatierten String** zusammen:

```
[KZG] themen (Salienz: 1.5): inhalt
[LZG/emotion] (Gewicht: 0.77, Arousal: 70%, ...): inhalt
[Charakter] hash-text
[Notiz] mehrzeiliger Block
...
```

Plugin-Manager liefern via `enrich()` ihre Beiträge ebenfalls als formatierte Strings. Das Format-Schema lebt verteilt: in `kzg_context_retrieve`, `lzg_context_retrieve`, im Enricher selbst und in jedem Plugin-Manager.

Der in Chat 74 gebaute Reducer hat versucht, **dieses String-Format zurückzuparsen**, um zu deduplizieren. Das hat sich in zwei Iterationen als brüchig erwiesen:

- Erste Version: `_zeile_zu_eintrag()` schnitt am ersten Doppelpunkt — Metadaten landeten als "Inhalt", Vergleiche waren wirkungslos.
- Zweiter Fix: Parser sucht `):` als Trenner — funktioniert für KZG/LZG, aber mehrzeilige Plugin-Blöcke (Notizen) werden zerlegt; "kardamon" und "hefe" wurden zu eigenständigen Einträgen ohne Präfix und Gewicht 0.0.

**Die Wurzel:** Ein Parser auf einem Pre-Format-String ist Inversionsarbeit. Strukturierte Daten existieren in den Memory-Modulen und Plugin-Managern bereits — sie werden nur **vorzeitig formatiert**, dann wieder zurückgeparst.

## 2. Ziel-Architektur

**Strukturierte Pipeline:**

```
Memory/Plugin liefert  →  Enricher sammelt        →  Reducer arbeitet  →  Formatter baut
strukturierte Entries     list[ContextEntry]         auf Liste            memory_context-String
                          state["memory_entries"]    dedupliziert         state["memory_context"]
```

Der Responder bleibt unverändert — er liest weiter `state["memory_context"]` als String. Die Schnittstelle nach hinten ist stabil; der Umbau ist nach vorn (Memory + Enricher) und im Reducer.

## 3. Datenstruktur

Neue TypedDict in `server/graph/context_entry.py`:

```python
ContextEntry = TypedDict("ContextEntry", {
    "quelle":   str,    # "kzg" | "lzg" | "charakter" | "summary" |
                        # "plugin_notiz" | "plugin_timeline" | "plugin_direktive" | ...
    "subtyp":   str,    # KZG/LZG-Dimension ("emotion", "kommunikation"); leer für andere
    "inhalt":   str,    # Reiner Text, ohne Format-Drumherum
    "gewicht":  float,  # Salienz oder effektives Gewicht; für Konflikt-Auflösung
    "meta":     dict,   # Quellen-spezifische Felder: beobachter, arousal, vektor,
                        # themen, dimension, erstellt_am, verstaerkt_am, ttl, ...
})
```

**Drei Eigenschaften, die der Parser-Pfusch nicht hatte:**

1. **Inhalt ist isoliert** — kein Format-Drumherum, kein Regex nötig.
2. **Gewicht ist explizit** — typisiert, nicht aus Strings extrahiert.
3. **Meta ist offen** — Quellen liefern, was sie haben; Formatter entscheidet, was er anzeigt.

## 4. Komponenten-Inventur

Was umgebaut wird:

| Komponente | Heute | Neu |
|---|---|---|
| `graph/state.py` | `memory_context: str` | + `memory_entries: list[ContextEntry]`, + `memory_context_raw: str` (Backup) |
| `graph/context_entry.py` | — | TypedDict-Definition (neue Datei) |
| `memory/kzg.py` | `kzg_context_retrieve() -> str` | `kzg_entries_retrieve() -> list[ContextEntry]` |
| `memory/lzg.py` | `lzg_context_retrieve() -> str` | `lzg_entries_retrieve() -> list[ContextEntry]` |
| `memory/charakter.py` | `charakter_hash_retrieve() -> str` | bleibt; Enricher wickelt das Ergebnis in einen Entry |
| Plugin-Basisklasse | `enrich(state, postgres_url) -> str` | `enrich_entries(state, postgres_url) -> list[ContextEntry]` |
| Alle Plugin-Manager | implementieren `enrich()` | implementieren `enrich_entries()` |
| `graph/nodes/enricher.py` | sammelt `context_parts: list[str]` | sammelt `entries: list[ContextEntry]`, schreibt `state["memory_entries"]` |
| `graph/nodes/reducer.py` | parst String, dedupliziert, schreibt String | liest Entries, dedupliziert, ruft Formatter auf |
| `graph/format/memory_context.py` | — | neue Datei: `format_memory_entries(entries) -> str`. Tool, kein Node. |

Was unverändert bleibt:

- **Responder:** liest weiter `state["memory_context"]`. Format-Konvention im Output-String bleibt identisch.
- **CharacterGraph + HumanGraph:** Knoten und Kanten unverändert.
- **Alle anderen Nodes:** Perzeption, Salienz, Router, Planner, Tribunal, Corrector, Dispatcher etc.
- **EI-Berechnung, GV-Node, Direktiven-Verarbeitung:** unberührt.

## 5. Plugin-Manager-Inventur (offen)

Vor Umbau-Beginn benötigt: Liste aller Manager mit `enrich()`-Hook. Heute aus dem Code direkt sichtbar:

- `fakten` (deaktiviert seit Chat 71)
- vermutlich: `notizen`, `timeline`, `direktiven`
- ggf. weitere

**Action vor STRUCT-3:** Inventur via `grep -r "def enrich" server/plugins/` und `server/managers/`. Liste in dieses Dokument aufnehmen.

## 6. Format-Vertrag (Output des Formatters)

Die Format-Konvention für den finalen `memory_context`-String bleibt **identisch zum heutigen Verhalten**, damit der Responder unverändert bleibt:

| Quelle | Format |
|---|---|
| `summary` | `═══ BISHERIGER GESPRÄCHSVERLAUF ═══\n{inhalt}` |
| `kzg` | `[KZG] {meta.themen} (Salienz: {gewicht}): {inhalt}` |
| `lzg` | `[LZG/{subtyp}] (Gewicht: {gewicht:.2f}, Arousal: {meta.arousal:.0%}, Beobachter: {meta.beobachter}, Vektor: {meta.vektor}): {inhalt}` |
| `charakter` | `[Charakter] {inhalt}` |
| `plugin_*` | `[{plugin-spezifisch}] {inhalt}` (mehrzeilig erlaubt) |

Der Formatter ist eine **reine Funktion** in `server/graph/format/memory_context.py`:

```python
def format_memory_entries(entries: list[ContextEntry]) -> str:
    """Baut den finalen memory_context-String fuer den Responder."""
```

Aufgerufen vom Reducer-Node nach der Dedup. Kein eigener Graph-Node — die Funktion trifft keine Entscheidungen, fasst nur zusammen. Das ist der **einzige** Ort, an dem Format-Schema-Wissen lebt. Dadurch:

- Format-Änderungen in Zukunft = ein Ort.
- Memory-Module und Plugin-Manager müssen nichts über Output-Format wissen.
- Reducer arbeitet nie auf Format, immer auf Daten.

## 7. Reducer-Funktionalität (auf strukturierten Daten)

**Stufe 1: Exakt-Dedup**
- Schlüssel: normalisiertes `inhalt`-Feld (lowercase, kollabierte Whitespaces).
- Bei Konflikt: behalte Eintrag mit höchstem `gewicht`. Gleichstand → erster Eintrag.

**Stufe 2: Substring-Dedup**
- Sortiere absteigend nach `len(inhalt)`.
- Verwerfe kürzere Einträge, die vollständig in längerem `inhalt` enthalten sind.
- Mindestlänge 10 Zeichen, sonst Falsch-Positiv-Risiko.
- Mehrzeilige Plugin-Blöcke werden als Einheit behandelt — ihr `inhalt` ist der ganze Block; Subteile (Listenpunkte) werden nicht zerlegt.

**Stufe 3 (optional, künftig):** Akten-aware
- Wenn Entries zur selben Entität gehören (z.B. `meta.entity_id`), als Akte gruppieren und gemeinsam akzeptieren/verwerfen. Setzt Akten-Architektur voraus (Backlog-Punkt: Akten-basiertes Retrieval).

**Logging:**
- Pro entferntem Eintrag eine INFO-Zeile mit `quelle`, `gewicht`, Inhalt-Snippet und Begründung.
- Anfangs-Diagnose: erste 5 Einträge als `[PARSE-N]` ausgeben (Quelle prüfen, nicht Parser).

## 8. Brudi-Prompt-Plan

Sequenziell. Big Bang innerhalb der Phasen, aber Phasen einzeln testbar.

### STRUCT-1 — Datenstruktur
- Neue Datei `server/graph/context_entry.py`: `ContextEntry` TypedDict.
- `server/graph/state.py`: `memory_entries: list[ContextEntry]`, `memory_context_raw: str` ergänzen.

### STRUCT-2 — Memory-Module
- `server/memory/kzg.py`: neue Funktion `kzg_entries_retrieve()` ergänzen, alte `kzg_context_retrieve()` **entfernen**.
- `server/memory/lzg.py`: analog, alte Funktion entfernen.
- Beide liefern `list[ContextEntry]`.

### STRUCT-3 — Plugin-Inventur und Basisklasse
- Inventur (s. Abschnitt 5).
- Basisklasse / Konvention für `enrich_entries(state, postgres_url) -> list[ContextEntry]` definieren.
- Alte `enrich()`-Methode aus der Basisklasse entfernen.

### STRUCT-4 — Plugin-Manager-Umbau
- Pro identifiziertem Manager: `enrich_entries()` implementieren, alte `enrich()` entfernen.
- Manager funktional, aber liefern strukturierte Entries statt Strings.

### STRUCT-5 — Enricher umbauen
- `server/graph/nodes/enricher.py`: sammelt `entries: list[ContextEntry]` statt `context_parts: list[str]`.
- Plugin-Hook-Aufruf: `manager.enrich_entries()`.
- KZG/LZG-Aufrufe: neue `*_entries_retrieve()`.
- Charakter-Hash und Session-Summary werden in Entries gewickelt.
- Schreibt `state["memory_entries"]`. Schreibt **kein** `memory_context` mehr — das macht der Reducer.

### STRUCT-6 — Reducer neu + Formatter
- Neue Datei `server/graph/format/memory_context.py`: `format_memory_entries(entries) -> str`. Reine Funktion, kein Node, kein State. Sortiert nach Reihenfolge (Abschnitt 9, R5) und baut den String nach Format-Vertrag (Abschnitt 6).
- `server/graph/nodes/reducer.py` komplett neu.
- Liest `state["memory_entries"]`.
- Dedupliziert (Stufe 1 + 2).
- Ruft `format_memory_entries()` auf, schreibt Ergebnis in `state["memory_context"]`.
- Sichert ungekürzte Roh-Liste in `state["memory_entries_raw"]` (Debug).

### STRUCT-7 — Verifikation
- Smoke-Test: Server starten, Konversation, Logs prüfen.
- Vergleich Vor/Nach: hat sich `memory_context` strukturell geändert? (Sollte nicht — Format-Vertrag.)
- Dedup-Quote messen: höher als beim String-Reducer? (Erwartet: ja, weil sauber.)

## 9. Risiken und Gegenmaßnahmen

**R1: Plugin-Manager bleibt vergessen.**
- Server bricht beim Aufruf, weil Methode fehlt.
- Gegenmaßnahme: STRUCT-3 macht harte Inventur (grep). Vor STRUCT-5 alle Manager bestätigt umgestellt. Beim Test direkt erkennbar.

**R2: Format-Vertrag im Formatter weicht subtil vom heutigen Output ab.**
- Responder bekommt minimal anderen String → Verhalten ändert sich.
- Gegenmaßnahme: STRUCT-7 macht String-Diff vor/nach. Bei Abweichung Format anpassen.

**R3: Mehrzeilige Plugin-Blöcke verlieren ihre innere Struktur.**
- Wenn ein Plugin heute mehrzeilige Strings liefert, muss der Manager-Umbau entscheiden: ein Entry mit mehrzeiligem `inhalt` oder mehrere Entries.
- Gegenmaßnahme: Default = ein Entry mit mehrzeiligem `inhalt`. Manager kann bei klarer Liste (z.B. Einkaufsliste) bewusst mehrere Entries liefern.

**R4: Reducer-Dedup-Verhalten ändert sich gegenüber heutigem String-Reducer.**
- Saubere Daten = mehr Treffer = mehr Entfernungen.
- Gegenmaßnahme: Akzeptiert. Logging zeigt was rausfliegt; bei Fehlfunden Schwellwerte (z.B. Mindestlänge) anpassen.

**R5: Kontext-Reihenfolge ändert sich.**
- Heute: Enricher hängt in einer bestimmten Reihenfolge an `context_parts` an.
- Neu: Reducer entscheidet Reihenfolge im Output-String.
- Gegenmaßnahme: Formatter sortiert nach fester Reihenfolge: `summary` zuerst, dann `charakter`, dann `kzg`/`lzg` nach `gewicht` absteigend, dann `plugin_*` in Registrierungs-Reihenfolge.

## 10. Was nicht in diesem Umbau steckt

Bewusst ausgeschlossen, im Backlog:

- **Akten-basiertes Retrieval** (Entitäten als kohärente Pakete) — eigenständige Erweiterung.
- **Assoziatives Retrieval** (Geflecht statt Liste) — eigenständig.
- **Embedding-basierte semantische Dedup** (Cosinus > 0.9) — Reducer-Erweiterung später.
- **Retrieval-Schwellwert-Tuning** (Anna im Katzen-Chat) — separat, betrifft KZG/LZG-Suche, nicht Reducer.
- **TOPOS-LOCK / "Aber sag mal"-Phrasenfixierung** — Responder-Thema, nicht Reducer.

## 11. Erfolgskriterien

Der Umbau gilt als abgeschlossen, wenn:

1. Alle Memory-Module und Plugin-Manager liefern `ContextEntry`-Listen.
2. Der Enricher sammelt nur strukturierte Daten; baut keinen String mehr.
3. Der Reducer arbeitet ausschließlich auf `memory_entries`; keine Regex auf String-Format.
4. Der Responder erhält einen `memory_context`-String, der formal dem heutigen entspricht.
5. Smoke-Test zeigt korrekte Verarbeitung von KZG, LZG, Charakter-Hash, Summary und mindestens zwei Plugin-Quellen.
6. Logging dokumentiert pro Eintrag Quelle, Gewicht und Dedup-Entscheidungen.

## 12. Nicht-Ziele

- Keine Verhaltensänderung im Responder.
- Keine Änderung an EI, GV, Tribunal, Salienz, Dispatcher.
- Keine neue Funktionalität — nur Aufräumen einer brüchigen Stelle.
