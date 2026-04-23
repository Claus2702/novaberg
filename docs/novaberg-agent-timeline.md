# Novaberg — User-Agent: TimelineAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** TimelineAgent (Termine, Ereignisse, Zeitachse)
**Stand:** 21. April 2026, Chat 60 (Session-Trennung: character_id im Kontext)
**Pfad:** novaberg/docs/novaberg-agent-timeline.md
**Quellen:** nova-02-m-e.md, nova-14-k.md, nova-15-k.md

---

## 1. Aufgabe

Der TimelineAgent verwaltet Novas Zeitachse -- Termine, Geburtstage, Deadlines, Jahrestage, Erinnerungen. Er unterstuetzt CRUD ueber den Agent-Pfad (Router erkennt Domaene, Agent klassifiziert Aktion), erkennt temporale Fakten aus der Salienz (implizit ueber den alten Pfad) und liefert zeitbezogenen Kontext ueber den Enricher-Hook im TimelineManager.

Alle Zeitoperationen nutzen den Zeitparser fuer natuerlichsprachliche deutsche Eingaben und das TimelineRepository fuer timezone-sichere Persistenz.

> **"Die Sekretaerin diagnostiziert nicht."** -- Der Router erkennt nur die Domaene, der Agent klassifiziert die Aktion. Der Router kennt weiterhin nur `management_action = "agent"`.

---

## 2. Architektur -- Subgraph

### 2.1 6-Node-Subgraph

```
Validate --> Resume? --> Classify --> Search --> CRUD --> Confirm
```

| Node | Datei | Aufgabe |
|------|-------|---------|
| `validieren` | `agent.py` | Pflichtfelder pruefen. Akzeptiert `"agent"` als Aktion (-> Classify-Node). |
| `resume` | `resume.py` | Resume-Flow bei Pending-Agent. Ein Pfad: Disambiguierung (Kandidat waehlen). |
| `klassifizieren` | `klassifikation.py` | LLM-Call: Bestimmt action, target, zeitausdruck, event_type, normalisiert. |
| `suchen` | `suche.py` | Drei Modi: Keyword, Zeitraum, Uebersicht (+/-14 Tage). |
| `ausfuehren` | `crud.py` | Create (Zeitparser ZeitVektor), Update (bi-temporal), Delete (Soft-Delete). |
| `bestaetigen` | `bestaetigung.py` | Status setzen. Ueberschreibt `rueckfrage`/`fehler` nicht blind. |

### 2.2 Routing-Logik

```
validieren
  +-- fehler --> END
  +-- resume --> resume --> ...
  +-- create --> ausfuehren --> bestaetigen --> END
  +-- read/update/delete --> suchen --> ausfuehren --> bestaetigen --> END
  +-- agent --> klassifizieren
                +-- fehler --> END
                +-- create --> ausfuehren --> bestaetigen --> END
                +-- read/update/delete --> suchen --> ausfuehren --> bestaetigen --> END
```

Vorklassifizierte Aktionen ueberspringen den Classify-Node (abwaertskompatibel).

Konvention: Oeffentliche Node-Einstiegspunkte ohne Unterstrich, private Helfer mit Unterstrich. Node-Funktionen sind Standalone (kein `self`).

---

## 3. Classify-Node

Seit Chat 60: `character_id` wird im Agent-Kontext (`state["kontext"]["character_id"]`) durchgereicht und an `session_turns_retrieve()` übergeben. Der Session-Key enthält die Charakter-Dimension.

Der Classify-Node extrahiert fuenf Felder per LLM:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `action` | create/read/reschedule/update/delete | "Verschieb den Zahnarzt" -> reschedule |
| `target` | Titel oder Beschreibung | "Zahnarzt" |
| `zeitausdruck` | Natuerlichsprachlich, WOERTLICH extrahiert | "auf Freitag" -> "Freitag" |
| `event_type` | termin/geburtstag/deadline/jahrestag/erinnerung | "termin" |
| `normalisiert` | Domain-Language-Uebersetzung | "reschedule: Termin auf Freitag verschieben" |

Zusaetzlich kann der Classify den Output `rejected` liefern (kein echter Termin-Auftrag, z.B. Rueckfrage oder Nennung ohne Anweisung) — der Agent bricht dann mit `status="rejected"` ab.

**Kernprinzip:** Der Zeitausdruck wird woertlich extrahiert, nicht geparst. "Donnerstag um 14 Uhr" bleibt "Donnerstag um 14 Uhr". Der Zeitparser in `crud.py` uebernimmt das deterministische Parsing. Saubere Trennung zwischen LLM-Verstaendnis und deterministischem Parsing.

**Kontextschutz:** "Analysiere NUR den aktuellen Prompt. Verlauf dient AUSSCHLIESSLICH fuer Rueckbezuege."

### [FACHSPRACHE]-Block

| User sagt | Normalisiert |
|-----------|-------------|
| "Hau mir Montag nen Zahnarzt rein" | "create: Termin 'Zahnarzt' am Montag anlegen (Typ: termin)" |
| "Verschieb das auf Freitag" | "reschedule: Termin auf Freitag verschieben" |

Die Domain Language ist die primaere Quelle fuer das Verstaendnis umgangssprachlicher Ausdruecke. Keywords und Verb-Mappings dienen als unabhaengige Gegenprobe fuer die Konfidenz-Berechnung.

---

## 4. Suche -- 3 Modi

### 4.1 Keyword-Suche (target vorhanden)

`TimelineRepository.find_by_keyword()` mit ILIKE und aktiv-Filter. Bei update/delete: Disambiguierung wenn mehrere Treffer.

**Smart-Disambiguierung:** Wenn mehrere Treffer, aber genau einer davon in der Zukunft liegt -> klarer Gewinner, keine Rueckfrage noetig (future-only winner).

### 4.2 Zeitraum-Suche (zeitausdruck vorhanden)

Zeitparser parst den Ausdruck -> `find_by_date_range()`. Erweiterte Zeitraeume: "morgen" -> Tag (00:00-23:59), "naechste Woche" -> Mo-So, "naechsten Monat" -> 1. bis letzter Tag.

### 4.3 Uebersicht (weder target noch zeitausdruck)

Anstehende Termine: heute -3 bis +14 Tage. Fuer "Was steht an?" ohne konkreten Zeitbezug.

### 4.4 Duplikat-Pruefung bei Create

Validierung prueft vor dem Anlegen, ob ein aktiver Eintrag mit aehnlichem Inhalt existiert. Bei Treffer: Rueckfrage "Existiert bereits. Aktualisieren?"

---

## 5. CRUD-Operationen

### 5.1 Create

1. Classify-Node liefert title + zeitausdruck + event_type
2. `zeit_parsen_vektor(zeitausdruck)` -> Datum berechnen (ZeitVektor)
3. Fallback: gesamten Prompt parsen wenn Zeitausdruck nicht parsbar
4. `TimelineRepository.insert()` mit precision (minute/day)
5. Verifikation nach Write: DB-Read, Ergebnis gegen Erwartung pruefen

### 5.2 Update / Reschedule (bi-temporal)

**Update = Invalidieren + Neu Anlegen.** Kein in-place UPDATE. Konsistent mit dem Fakten-System. Historie bleibt erhalten.

`reschedule` ist seit Chat 42 eine eigene Aktion (statt update+zeitausdruck). Bei reschedule wird der ZeitVektor fuer die Kombination von altem und neuem Zeitpunkt verwendet.

### 5.3 Delete (Invalidieren)

Soft-Delete: `aktiv = FALSE` ueber `TimelineRepository.invalidate()`. Kein Hard-Delete. Verifikation: Eintrag wirklich `aktiv=FALSE`?

---

## 6. ZeitVektor

`zeit_parsen_vektor()` liefert drei Steuerungsfelder:

| Feld | Werte | Beschreibung |
|------|-------|-------------|
| `tag_erkannt` | Boolean | Wurde ein Tag im Zeitausdruck erkannt? |
| `uhrzeit_erkannt` | Boolean | Wurde eine Uhrzeit erkannt? |
| `referenz_modus` | absolut / relativ / relativ_rueckwaerts | Wie ist der Zeitbezug zu interpretieren? |

### 6.1 Zwei-Phasen-Parsing

1. **Phase 1:** `zeit_parsen_vektor(zeitausdruck)` mit Default-Referenz (jetzt) -> erkennt `referenz_modus`
2. **Referenz waehlen:** `absolut` -> heute, `relativ` -> alter Termin, `relativ_rueckwaerts` -> alter Termin + Vergangenheit bevorzugt
3. **Phase 2:** `zeit_parsen_vektor(zeitausdruck, referenz=richtige_referenz)` mit korrekter Referenz
4. **Kombination:** Erkannte Teile (Tag/Uhrzeit) mit altem Termin zusammenfuehren

### 6.2 Kombination: neuer Tag + alte Uhrzeit (oder umgekehrt)

| User sagt | tag_erkannt | uhrzeit_erkannt | Ergebnis |
|-----------|------------|----------------|----------|
| "Freitag" | ja | nein | Tag -> neu, Uhrzeit -> vom alten Termin |
| "15 Uhr" | nein | ja | Tag -> vom alten Termin, Uhrzeit -> neu |
| "Freitag um 10 Uhr" | ja | ja | Komplett neu |

### 6.3 Referenz-Modus

| Praefix | Referenz |
|---------|---------|
| "diesen Freitag" | heute (absolut) |
| "naechsten Freitag" / "Freitag" | alter Termin (relativ) |
| "letzten Freitag" | alter Termin, Vergangenheit bevorzugt |

---

## 7. CRUD-Haertung

Seit Chat 42 (Epic 14) gelten gehaertete Transaktionen fuer den TimelineAgent.

### 7.1 Erweiterte Taxonomie

`reschedule` ist eine eigene Aktion (statt generischem `update` mit Zeitausdruck).

| Aktion | Bedeutung | Beispiele |
|--------|-----------|-----------|
| `create` | Neuen Termin anlegen | "Morgen um 10 Zahnarzt" |
| `delete` | Termin loeschen | "Loesch den Zahnarzt" |
| `read` | Termine anzeigen | "Was steht morgen an?" |
| `reschedule` | Termin verschieben | "Verschieb den Zahnarzt auf Freitag" |
| `update` | Details aendern (nicht Zeit) | "Der Zahnarzt ist jetzt Dr. Mueller" |

### 7.2 Dreistufige Erkennung

1. **Stufe A -- Statische Keyword-Hints** (Python, vor dem LLM-Call): Regex-Erkennung liefert Hinweise
2. **Stufe B -- Lernende Verb-Mappings** (PostgreSQL, pro User): "Hau rein" -> create (ab Konfidenz >= 3 ohne Rueckfrage)
3. **Stufe C -- LLM-Klassifikation** mit `[ERKENNUNGSHILFE]`- und `[FACHSPRACHE]`-Block

### 7.3 Konfidenz

| Situation | Konfidenz | Aktion |
|-----------|-----------|--------|
| Keyword-Hint + LLM stimmen ueberein | Hoch | Direkt validieren |
| Verb-Mapping (>=3) + LLM stimmen ueberein | Hoch | Direkt validieren |
| Nur LLM, kein Hint | Niedrig | Rueckfrage |
| Hint und LLM widersprechen sich | Konflikt | Rueckfrage |

### 7.4 Verifikation nach Write

Nach jedem Write ein DB-Read. Ergebnis gegen Erwartung pruefen. Bei Fehler: `CrudErgebnis.erfolg` wird auf `False` korrigiert. Rueckfrage nur bei niedriger Konfidenz oder Konflikt.

---

## 8. Event-Typen

| Typ | Beispiele | Beschreibung |
|-----|-----------|-------------|
| `termin` | Arzttermin, Meeting, Verabredung | Standard-Typ |
| `geburtstag` | Geburtstage | Jaehrlich wiederkehrend |
| `deadline` | Abgabetermine, Fristen | Fristgebunden |
| `jahrestag` | Wiederkehrende jaehrliche Ereignisse | Jaehrlich wiederkehrend |
| `erinnerung` | Allgemeine Erinnerungen | Ohne festen Termin-Charakter |

Der Typ wird vom Classify-Node bestimmt -- nicht vom Nutzer explizit angegeben.

---

## 9. DB-Schema

Tabelle: `timeline` (angelegt via `agents/timeline/init.sql`)

```sql
CREATE TABLE IF NOT EXISTS timeline (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    event_time      TIMESTAMPTZ,
    event_type      VARCHAR(50),        -- termin, geburtstag, deadline, jahrestag, erinnerung
    title           VARCHAR(255),
    details         TEXT,
    recurring       BOOLEAN DEFAULT FALSE,
    precision       VARCHAR(10),        -- day oder minute
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
    last_touched    TIMESTAMPTZ,        -- Letzter Zugriff (Ebbinghaus)
    wiedervorlage_am TIMESTAMPTZ,       -- Naechster Pixie-Check
    entitaet_ids    INTEGER[]           -- Referenzierte Entitaeten
);
```

**Timezone-Konvention:** UTC in der DB, lokale Zeit (`Europe/Berlin`) in der Anzeige. Repository konvertiert.

---

## 10. Konfiguration

**Dateien:** `agents/timeline/agent.py`, `klassifikation.py`, `resume.py`, `suche.py`, `crud.py`, `bestaetigung.py`, `dispatch.py`, `AGENT.md`

**Plugin:** TimelineManager (Enricher-Hook fuer proaktiven Kontext: heute -3 bis +14 Tage)

**Router-Prompt:** `management_action = "agent"` bei Termin-Erkennung. Keine spezifische CRUD-Aktion.

**Resume-TTL:** 300s (Redis `pending_agent:{user_id}`). **Rueckfrage-Pflicht:** Nur bei niedriger Konfidenz oder Konflikt.
