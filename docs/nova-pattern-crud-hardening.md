# Nova — Pattern: CRUD-Haertung (Gehaertete Agent-Transaktionen)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pattern — Transaktionssicherheit fuer Agent-CRUD-Operationen
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** `novaberg/docs/nova-pattern-crud-hardening.md`
**Quellen:** nova-14-k.md (allgemeine Abschnitte)

---

## 1. Problem

Agenten arbeiten nach Fire-and-Forget: Der Classify-Node bestimmt eine CRUD-Aktion, die CRUD-Funktion fuehrt sie aus, der Bestaetigungs-Node meldet Erfolg. Zwischen Klassifikation und Ausfuehrung findet keine Validierung statt.

**Beobachtete Fehlerklassen:**

- Halluzinierte Aktionen (Bestaetigung gemeldet, DB nicht geaendert)
- Falsche Klassifikation ("wiederherstellen" → create statt reactivate)
- Schreiben ohne Bestaetigungsmechanismus (unbemerkte Degradierung)
- Konversation als Direktive interpretiert

Ursache: Kein Pruefen des DB-Zustands vor der Aktion, kein Verifizieren nach der Aktion, kein Gate fuer sensible Operationen.

---

## 2. Loesung — Vier-Phasen-Transaktions-Pattern

Jede Agent-Aktion wird eine geprueft Transaktion:

```
ERKENNEN ──> VALIDIEREN ──> AUSFUEHREN ──> VERIFIZIEREN
(LLM+Py)     (Python)       (Python)       (Python)
                |
           Bei Fehler:
           → Rueckfrage
           → Auto-Korrektur
           → Retry an LLM
                |
          BESTAETIGUNG    ← nur bei sensiblen
          (Rueckfrage)      Agenten
```

Fundierung durch Industriestandards: Pre-Execution Guard (Pydantic AI), HITL-Gate (OWASP/Microsoft Agent Safety), Full-Lifecycle-Verifikation (CircleCI).

---

## 3. Phase 1: ERKENNEN

Dreistufige Erkennung im Classify-Node:

### Stufe A — Statische Keyword-Hints (Python, vor dem LLM-Call)

```python
KEYWORD_HINTS = {
    "wiederherstellen|wieder her|reaktivieren|zurückholen":  "reactivate",
    "rückgängig|undo|zurücknehmen":                          "reactivate",
    "lösch|entfern|weg damit|streich .*komplett":            "delete",
    "füge.*hinzu|hinzufügen|aufnehmen|nimm.*auf|ergänz":    "add_content",
    "streich|nimm.*raus|entferne.*von|runter von":           "remove_content",
    "leere|alles löschen|komplett leeren":                   "clear_content",
    "ändere|ändern|aktualisier|korrigier":                   "update",
    "verschieb|verleg":                                      "reschedule",
    "zeig|was hast|welche|liste|auflisten":                  "read",
}
```

### Stufe B — Lernende Verb-Mappings (PostgreSQL, pro User)

Bei umgangssprachlichen Ausdruecken ("hau rein", "pack drauf", "schmeiss weg"), die nicht in den statischen Keywords stehen, lernt Nova die Zuordnung durch Bestaetigung. Ab `konfidenz >= 3` (dreimal bestaetigt) wird der Ausdruck wie ein eingebautes Keyword behandelt.

### Stufe C — LLM-Klassifikation mit [ERKENNUNGSHILFE]-Block

Das LLM bekommt statische Hints UND gelernte Verb-Mappings als Kontext:

```
[ERKENNUNGSHILFE]
Schluesselwoerter und gelernte Ausdruecke im Text deuten auf folgende Aktionen:
- create (Gelernt: "hau rein", Konfidenz: 3)
- reactivate (Schluesselwort: "wiederherstellen")
Diese Hinweise sind NICHT bindend, aber beruecksichtige sie.
```

---

## 4. Phase 2: VALIDIEREN

Python prueft die LLM-Klassifikation deterministisch gegen den aktuellen DB-Zustand:

| Aktion | Pruefung | Bei Fehler |
|--------|---------|------------|
| create | Existiert ein aktiver Eintrag mit aehnlichem Inhalt? | → Rueckfrage: "Existiert bereits. Aktualisieren?" |
| create | Existiert ein inaktiver Eintrag? | → Auto-Korrektur zu `reactivate` |
| delete | Existiert das Target? Ist es aktiv? | → Fehler: "Nichts gefunden" |
| delete | Mehrere Treffer? | → Rueckfrage: "Welche meinst du?" |
| update | Existiert das Target? | → Fehler oder create-Vorschlag |
| reactivate | Existiert ein inaktiver Eintrag? | → Fehler: "Nichts zum Wiederherstellen" |
| add_content | Existiert der Container? | → create falls nicht |
| remove_content | Enthaelt der Container das Element? | → Fehler: "Element nicht gefunden" |

**HITL-Gate:** Fuer sensible Agenten (Direktiven, Charakter) ist eine Pflicht-Rueckfrage vor Ausfuehrung erforderlich. Technisch ueber den bestehenden `interrupt()`/Resume-Flow. Ziel: Rueckfrage-Pflicht wieder entfernen, sobald Validierung stabil genug ist.

---

## 5. Phase 3: AUSFUEHREN

Die eigentliche DB-Operation mit Vorher/Nachher-Snapshot:

- **Vorher-Snapshot:** Vor jeder Schreiboperation liest die CRUD-Funktion den aktuellen Zustand
- **Ausfuehrung:** CRUD-Operation (INSERT, UPDATE, Soft-DELETE)
- **Nachher-Snapshot:** Frischer DB-Read nach der Operation

Der Snapshot ermoeglicht Verifikation und potentielles Rollback.

---

## 6. Phase 4: VERIFIZIEREN

Liest den DB-Zustand und vergleicht mit dem erwarteten Ergebnis:

- Nach delete: Eintrag wirklich `aktiv=FALSE`?
- Nach update: Text wirklich geaendert? Neuer Wert == erwarteter Wert?
- Nach create: Neuer Eintrag existiert mit erwarteten Feldern?
- Nach reactivate: Eintrag wieder `aktiv=TRUE`?

Bei Fehler: `CrudErgebnis.erfolg` wird auf `False` korrigiert. Der Bestaetigungs-Node bekommt den echten Zustand statt eine Halluzination.

---

## 7. Konfidenz-Berechnung

| Situation | Konfidenz | Aktion |
|-----------|-----------|--------|
| Keyword-Hint + LLM stimmen ueberein | hoch | Direkt validieren |
| Verb-Mapping (>=3) + LLM stimmen ueberein | hoch | Direkt validieren |
| Verb-Mapping (<3) + LLM stimmen ueberein | mittel | Direkt validieren, Konfidenz++ |
| Nur LLM, kein Hint | niedrig | Rueckfrage + ggf. Verb lernen |
| Hint und LLM widersprechen sich | konflikt | Rueckfrage |

---

## 8. Verb-Mappings

Lernende Sprachadaption auf der Aktionsebene. Nova lernt, WAS der User mit bestimmten Ausdruecken MEINT — Dialekt und Slang, den kein vorgefertigtes Woerterbuch abdeckt.

```sql
CREATE TABLE IF NOT EXISTS verb_mappings (
    id          SERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL,
    ausdruck    TEXT NOT NULL,
    aktion      TEXT NOT NULL,
    agent       TEXT NOT NULL,
    konfidenz   INTEGER NOT NULL DEFAULT 1,
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, ausdruck, agent)
);
```

**UPDATE Chat 44:** Mit der Einfuehrung der Domain-Language-Normalisierung ([FACHSPRACHE]-Block) verschieben sich Verb-Mappings zu sekundaerer Konfidenz-Pruefung. Die Domain Language uebernimmt die primaere Erkennung. Verb-Mappings und Keywords dienen als deterministische Gegenprobe zur LLM-Klassifikation.

---

## 9. Datenstrukturen

### KlassifikationsErgebnis (Output des Classify-Node)

```python
@dataclass
class KlassifikationsErgebnis:
    aktion: str                    # aus erweiterter Taxonomie
    target: str | None             # worauf sich die Aktion bezieht
    slots: dict                    # agent-spezifische Felder
    keyword_hints: list[str]       # aus Stufe A (statisch) + Stufe B (gelernt)
    konfidenz: str                 # "hoch", "mittel", "niedrig", "konflikt"
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    ok: bool
    korrektur: str | None          # auto-korrigierte Aktion
    grund: str                     # Erklaerung fuer Logs/Rueckfrage
    bestaetigung_noetig: bool      # HITL-Gate
    bestaetigung_text: str | None  # "Soll ich X machen?"
```

### CrudErgebnis (mit Vorher/Nachher-Snapshot)

```python
@dataclass
class CrudErgebnis:
    erfolg: bool
    aktion: str           # tatsaechlich ausgefuehrte Aktion
    vorher: dict | None   # DB-Zustand vor der Aenderung
    nachher: dict | None  # DB-Zustand nach der Aenderung (frischer DB-Read)
    verifiziert: bool     # nachher == erwartet?
    meldung: str          # Menschenlesbare Beschreibung
```

---

## 10. Gemeinsame Infrastruktur

**Datei:** `agents/crud_validation.py`

Enthaelt die gemeinsamen Datenstrukturen (`KlassifikationsErgebnis`, `ValidationResult`, `CrudErgebnis`) sowie die Hilfsfunktionen:
- `keyword_hints_ermitteln(text)` — Stufe A: statische Regex-Keywords
- `verb_mappings_laden(user_id, agent)` — gelernte Verb-Mappings aus PostgreSQL
- `verb_mapping_pruefen(text, user_id, agent)` — Stufe B: dynamische Mapping-Prüfung
- `verb_mapping_lernen(user_id, agent, ausdruck, aktion)` — Konfidenz++ / Insert
- `konfidenz_berechnen(...)` — hoch/mittel/niedrig/konflikt
- `erkennungshilfe_block(...)` — baut den `[ERKENNUNGSHILFE]`-Prompt-Block

Validierung ist keine Agent-Eigenschaft, sondern ein Service. Agenten ohne CRUD (Decay, Recherche) brauchen keine Validierung. `crud_validation.py` ist ein Import, keine Basisklasse.

**Verzeichnisstruktur (Stand Chat 52):**

```
agents/
+-- crud_validation.py         # Gemeinsame Datenstrukturen + Hilfsfunktionen
+-- direktiven/
|   +-- klassifikation.py      # Classify-Node mit Hints + [FACHSPRACHE]
|   +-- crud.py                # CRUD + inline `validieren_gegen_db()`
|   +-- agent.py               # LangGraph-Subgraph mit `_db_validieren`-Node
+-- charakter_identitaet/
|   +-- klassifikation.py
|   +-- crud.py                # crud.py enthaelt die validieren_gegen_db-Funktion
|   +-- agent.py
+-- notizen/, timeline/
|   +-- (analoges Muster, Validation inline in crud.py bzw. agent._db_validieren)
```

Es gibt keine separaten `validation.py`-Dateien in den Agent-Ordnern. Die agent-spezifischen Validierungsregeln leben in `crud.py` (Funktion `validieren_gegen_db()`) bzw. direkt als Graph-Node `_db_validieren()` im `agent.py`.

### Architektur-Prinzipien

- **"Berechnung in Python, nicht im LLM"** — LLM erkennt Absicht, Python prueft und verifiziert
- **"Trust, but verify"** — Jede Phase prueft die Arbeit der vorherigen
- **"Die Sekretaerin diagnostiziert nicht"** — Router entscheidet nur welcher Agent, Taxonomie lebt im Classify-Node
- **"Rueckfrage vor Dummheit"** — Im Zweifel lieber rueckfragen als falsch ausfuehren
