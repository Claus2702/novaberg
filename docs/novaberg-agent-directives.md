# Novaberg — User-Agent: DirektivenAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** DirektivenAgent (Verhaltensanweisungen, Arbeitsvertrag)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-agent-directives.md
**Quellen:** nova-12-k.md, nova-14-k.md, nova-15-k.md

---

## 1. Aufgabe

Der DirektivenAgent verwaltet absolute Verhaltensanweisungen des Nutzers -- GESETZ, nicht IDENTITAET. Direktiven bestimmen, WAS Nova tun oder lassen muss: "Sprich nie von Milch", "Sieze mich immer", "Nenn mich nie Schatz". Sie sind der Vertrag zwischen Nutzer und Nova.

Der Agent nimmt Anweisungen im Gespraech entgegen, speichert sie persistent und speist sie ueber den Enricher in den Prompt-Flow ein. Jeder Turn laedt ALLE aktiven Direktiven -- eine Direktive, die nicht geladen wird, wird nicht befolgt.

---

## 2. Konzeptionelle Einordnung

### 2.1 Direktiven sind nicht Charakter

| Aspekt | Direktive | Charakter |
|--------|-----------|-----------|
| Was | Verhaltensregel | Identitaetsbeschreibung |
| Wirkung | Bestimmt WAS Nova tun/lassen muss | Formt WER Nova ist |
| Stabilitaet | Kann jederzeit kommen und gehen | Langfristig, selten geaendert |
| Kardinalitaet | Beliebig viele | Max 3 aktiv |
| Tribunal | Geprueft (Antwort gegen Direktiven) | Nicht geprueft |

### 2.2 Orthogonalitaet

Die Schichten sind orthogonal: Ein lustiges Maedel vom Land (Charakter) kann trotzdem die Direktive "Sieze mich" befolgen. Charakter und Direktiven beeinflussen sich nicht gegenseitig.

### 2.3 Schichten-Modell (Prompt-Hierarchie)

```
[IDENTITAET]       "Du bist Nova." + Charakter-Anweisung (Saatgut, Primacy)
                   + nova_kern, nova_adaptiv, nova_beziehung, nova_intentionen
                   (Destillations-Schichten, konsolidiert seit Chat 45/RESP-CHAR1)
[AUFGABE]          Agent-Ergebnis / Pflicht-Rueckfrage (bedingt)
[KOMMUNIKATION]    EI-MIKRO, Sprachstil, Emotion, Vektor
[GESPRAECHSVEKTOR] Landschaftsbeschreibung
[GEDAECHTNIS]      KZG, LZG, Fakten, Notizen (bei Agent-Erfolg weggelassen)
[REGELN]           Antwortkuerze, Butler-Verbot, ... (System, fest)
[DIREKTIVEN]       Absolute Verhaltensanweisungen vom Nutzer (Recency)
```

Der `[CHARAKTER]`-Block existiert seit Chat 45 nicht mehr als eigener Block — die Destillations-Schichten sind in `[IDENTITAET]` konsolidiert.

`[DIREKTIVEN]` ist ein eigener Block -- nicht in `[REGELN]` eingebettet. Steht nach `[REGELN]` in ultimativer Recency-Position.

---

## 3. Architektur -- Subgraph mit HITL-Gate

Der DirektivenAgent folgt dem etablierten NotizenAgent/TimelineAgent-Muster, erweitert um eine Validierungsphase mit Pflicht-Rueckfrage. Der tatsaechliche LangGraph-Subgraph (Entry-Point `validieren`):

```
validieren --+--> ausfuehren (bei resume=True)
             |
             +--> klassifizieren --> db_validieren --+
             |                                        |
             +-------------------> db_validieren -----+--> ausfuehren --> END
                                                      |
                                                      +--> END (Rueckfrage/Fehler)
```

`validieren` routet nach drei Kriterien: bei `resume=True` → direkt `ausfuehren` (kein eigener Resume-Node wie beim CharakterIdentitaetAgent — der Direktiven-Agent rehydriert die Aktion aus Redis-Pending und spielt die Ausfuehrung sofort ab); bei bereits gueltiger `action` → `db_validieren`; sonst → `klassifizieren`. Verifikation und Confirm liegen inline in `ausfuehren` (kein eigener Node).

Der Classify-Node kann zusaetzlich zur Tabelle in §4 den Output `rejected` liefern (z.B. bei Kompliment/rhetorischer Frage statt echtem Direktiven-Auftrag) — dann bricht der Agent mit `status="rejected"` ab, ohne DB-Zugriff.

```
agents/direktiven/
+-- __init__.py
+-- agent.py            # DirektivenAgent(BaseAgent)
+-- klassifikation.py   # Classify-Node
+-- crud.py             # DB-Operationen mit Vorher/Nachher-Snapshot + validieren_gegen_db()
+-- dispatch.py         # Backend-Dispatch: Baut AgentState, startet den Agenten-Subgraph, verarbeitet das Ergebnis
+-- init.sql            # Schema
+-- AGENT.md            # Beschreibung + Router-Prompt
```

---

## 4. Classify-Node

Der Classify-Node extrahiert vier Felder per LLM:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `action` | create/read/update/delete/reactivate | "Sag nie wieder Schatz" -> create |
| `anweisung` | Destillierte Verhaltensregel | "Nutzer nicht Schatz nennen" |
| `kontext` | Gespraechskontext bei impliziten Direktiven | "User bezog sich auf Novas Aussage ueber Y in Turn 3" |
| `target_id` | Bei update/delete: ID der betroffenen Direktive | 5 |

### 4.1 Destillation und Kontext-Aufloesung

Das LLM destilliert die Anweisung aus dem Rohtext. Bei impliziten Direktiven wie "Sag das nie mehr!" loest der Classify-Node den Bezug aus dem Session-Kontext auf und speichert ihn als Klartext im `kontext`-Feld.

| User sagt | Destilliert (anweisung) |
|-----------|------------------------|
| "Sprich nie von Milch!" | "Sprich nie von Milch" |
| "Sag das nie mehr!" | "Erwaehne nicht mehr, dass [X]" (kontext aus Session) |
| "Du darfst wieder ueber Milch reden" | (action: delete, target: Milch-Direktive) |

### 4.2 [FACHSPRACHE]-Block

Der Classify-Prompt enthaelt einen `[FACHSPRACHE]`-Block mit Domain Language:

| User sagt | Normalisiert |
|-----------|-------------|
| "Nenn mich ab jetzt Boss" | "update: Anrede des Nutzers auf 'Boss' aendern (betrifft ID 1)" |
| "Vergiss die Siez-Regel" | "delete: Direktive 'Den Nutzer immer siezen' deaktivieren" |
| "Sag nie wieder Schatz zu mir" | "create: Neue Direktive 'Nutzer nicht Schatz nennen' anlegen" |

Die Domain Language ist die primaere Quelle fuer das Verstaendnis. Keywords und Verb-Mappings dienen als Konfidenz-Anker.

---

## 5. CRUD -- 5 Aktionen + agent

| Aktion | Bedeutung | Beispiele |
|--------|-----------|-----------|
| `create` | Neue Direktive anlegen | "Nenn mich nie Schatz" |
| `read` | Aktive Direktiven auflisten | "Welche Regeln hast du?" |
| `update` | Text einer Direktive aendern (bi-temporal) | "Aendere die Regel: auch kein Hase" |
| `delete` | Direktive deaktivieren | "Loesch die Siez-Direktive" |
| `reactivate` | Inaktive Direktive reaktivieren | "Stelle sie wieder her" |

Zusaetzlich akzeptiert die Input-Validierung den Platzhalter `agent` (Router-Routing vor Klassifikation).

### 5.1 ILIKE-Suche bei Delete

Bei delete wird per ILIKE-Suche das Target in den aktiven Direktiven gesucht. Bei mehreren Treffern: Disambiguierungs-Rueckfrage.

### 5.2 Bi-temporales Update

Update = Invalidieren + Neu Anlegen. Kein in-place UPDATE. Die alte Direktive wird auf `aktiv = FALSE` gesetzt, eine neue mit geaendertem Text angelegt. Historie bleibt erhalten.

---

## 6. DB-Validierung (HITL-Gate)

### 6.1 Pflicht-Rueckfrage

Fuer ALLE Schreiboperationen (create, update, delete, reactivate) gilt eine Pflicht-Rueckfrage vor Ausfuehrung:

```
Nova: "Ich soll die Direktive 'Den Nutzer nicht Schatz nennen'
       wiederherstellen. Soll ich das so machen?"
User: "Ja"
Nova: [fuehrt aus]
```

Technisch ueber den bestehenden `interrupt()`/Resume-Flow. Ziel: Pflicht-Rueckfrage wieder entfernen, sobald die Validierung stabil genug ist.

### 6.2 Duplikat-Check

Vor dem Anlegen prueft Python gegen den DB-Zustand: Existiert ein aktiver Eintrag mit aehnlichem Inhalt? Bei Treffer: Rueckfrage "Existiert bereits. Aktualisieren?"

### 6.3 Auto-Korrektur create -> reactivate

Wenn der User "Wiederherstellen" sagt und der Classify `create` liefert, prueft die Validierung ob ein inaktiver Eintrag existiert. Falls ja: automatische Korrektur zu `reactivate`. Verhindert Duplikate wie die dreifache "Schatz"-Direktive.

---

## 7. Verifikation

Nach jedem Write liest die CRUD-Funktion den DB-Zustand und vergleicht mit dem erwarteten Ergebnis:

- Nach create: Neuer Eintrag existiert mit erwarteten Feldern?
- Nach delete: Eintrag wirklich `aktiv=FALSE`?
- Nach update: Text wirklich geaendert? Neuer Wert == erwarteter Wert?
- Nach reactivate: Eintrag wieder `aktiv=TRUE`?

Bei Fehler: `CrudErgebnis.erfolg` wird auf `False` korrigiert. Der Bestaetigungs-Node bekommt den echten Zustand statt eine Halluzination. Die Datenstruktur `CrudErgebnis` (aus `agents/crud_validation.py`) erfasst Vorher/Nachher-Snapshot und Verifikationsstatus.

---

## 8. Prompt-Integration

### 8.1 [DIREKTIVEN]-Block (Recency)

Der Responder baut einen eigenen `[DIREKTIVEN]`-Block -- nach `[REGELN]`, als letzter Block vor den Messages. Maximale Recency. Der Block ist als Arbeitsvertrag gerahmt:

```
[DIREKTIVEN]
Der Nutzer hat folgende absolute Verhaltensanweisungen erteilt.
Diese MUESSEN befolgt werden -- sie sind dein Vertrag mit dem Nutzer:
- <anweisung>
  (Kontext: <kontext, falls gesetzt>)
```

### 8.2 Laden und Einbau

Die aktiven Direktiven werden vom Enricher aus der Datenbank geladen und im State bereitgestellt. Der Responder integriert sie in den System-Prompt innerhalb der Funktion `_build_system_prompt()` in `graph/nodes/responder.py`.

SQL beim Laden:

```sql
SELECT anweisung, kontext FROM direktiven
WHERE user_id = %s AND aktiv = TRUE
ORDER BY erstellt_am;
```

Kein Embedding, keine Vektorsuche -- Direktiven sind wenige, kurze Regeln. Komplett laden ist effizienter und vermeidet das Risiko, relevante Regeln durch Embedding-Schwaechen zu verpassen.

### 8.3 Tribunal: Jurist prueft, Ethik > Direktiven

Das Tribunal bekommt die aktiven Direktiven als Pruefkriterium. Es prueft nicht die Direktiven selbst, sondern ob Novas Antwort gegen die Direktiven verstoesst:

```
Der Nutzer hat folgende Direktiven (Verhaltensvertrag) erteilt:
- Sprich nie von Milch
- Sieze den Nutzer immer

Pruefe ob die Antwort gegen diese Direktiven verstoesst.
Wenn ja: Warne! "Das verstoesst gegen die Direktive: [Regel]."

WICHTIG: Ethik, Psychologie und Recht stehen UEBER Direktiven.
Ein Nutzer kann keine Direktive erteilen, die ethische Grundsaetze aushebelt.
Im Konfliktfall: Ethik/Psyche/Recht gewinnt, Direktive wird kommentiert.
```

**Tribunal-Hierarchie:** Ethik/Psyche/Recht > Direktiven > Charakter.

---

## 9. DB-Schema

Tabelle: `direktiven` (angelegt via `agents/direktiven/init.sql`)

```sql
CREATE TABLE IF NOT EXISTS direktiven (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    anweisung       TEXT NOT NULL,
    kontext         TEXT,
    erstellt_am     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktiv           BOOLEAN NOT NULL DEFAULT TRUE,
    geaendert_am    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_direktiven_user_aktiv
    ON direktiven(user_id, aktiv);
```

**`kontext`-Spalte:** Erfasst den Gespraechskontext bei impliziten Direktiven. "Sag das nie mehr!" -> `kontext` = "User bezog sich auf Novas Aussage ueber Milch in Turn 5".

---

## 10. Konfiguration

**Dateien:** `agents/direktiven/agent.py`, `agents/direktiven/klassifikation.py`, `agents/direktiven/crud.py` (enthaelt `validieren_gegen_db`), `agents/direktiven/dispatch.py`, `agents/direktiven/init.sql`, `agents/direktiven/AGENT.md`

**Plugin:** `plugins/direktiven_manager/` (liefert Router-Prompt; das Laden der aktiven Direktiven erfolgt im Enricher, der Einbau in den Prompt im Responder)

**Router-Prompt:** `management_action = "agent"` bei Direktiven-Erkennung. Erkennungsmuster: Imperative mit "nie", "immer", "ab jetzt", "ab sofort"; Verbote: "nicht mehr", "hoer auf", "lass das".

**HITL-Gate:** Pflicht-Rueckfrage fuer alle Schreiboperationen. **Gemeinsame Infrastruktur:** `agents/crud_validation.py`.
