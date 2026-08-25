# Novaberg — User-Agent: CharakterIdentitaetAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** CharakterIdentitaetAgent (Persoenlichkeits-Saatgut)
**Stand:** 12. Juli 2026, Chat 107 (Boden-Warnung: Destillation rechnete bis zum Reset auf Zufallsgewichten, siehe §2)
**Pfad:** novaberg/docs/novaberg-agent-character.md
**Quellen:** nova-12-k.md, nova-14-k.md, nova-15-k.md

---

## 1. Aufgabe

Der CharakterIdentitaetAgent verwaltet Charakter-Anweisungen des Nutzers -- IDENTITAET, nicht GESETZ. Charakter-Anweisungen formen, WER Nova ist: "Du bist ein freches Maedel vom Land, liebst Botanik". Sie sind das Saatgut, aus dem Novas Persoenlichkeit waechst.

Der Agent nimmt Anweisungen im Gespraech entgegen, speichert sie persistent und speist sie ueber den Enricher in den Prompt-Flow ein -- direkt in den `[IDENTITAET]`-Block, vor den Destillations-Schichten.

> **"Die Seele soll wachsen und keine Soul-Datei sein."** -- Meister, Chat 21

---

## 2. Saatgut-Prinzip

Die Charakter-Anweisung ist das Saatgut, die Destillations-Schichten sind der Boden:

| Aspekt | Charakter-Anweisung (Saatgut) | Destillations-Schichten (Boden) |
|--------|-------------------------------|----------------------|
| Quelle | User sagt es explizit | Pixie destilliert aus Gespraechen |
| Stabilitaet | Statisch bis User aendert | Variabel, waechst und wandelt sich |
| Position | In `[IDENTITAET]` nach "Du bist Nova" | Ebenfalls in `[IDENTITAET]` — konsolidiert seit RESP-CHAR1 (Chat 45) |
| Vorrang | Definiert Grundrichtung (Modulation) | Traegt die Basis-Persoenlichkeit |
| Beispiel | "Freches Maedel vom Land, liebt Botanik" | nova_kern + nova_beziehung + nova_adaptiv + nova_intentionen |

Seit RESP-CHAR1 (Chat 45) sind die Destillations-Schichten (nova_kern, nova_beziehung, nova_adaptiv, nova_intentionen) direkt im `[IDENTITAET]`-Block konsolidiert, nicht mehr in einem separaten `[CHARAKTER]`-Block. Diese Konsolidierung hat eine wichtige Eigenschaft sichtbar gemacht:

> **⚠ Boden-Warnung (Chat 107, 12.07.2026):** Die Destillation, die diesen „Boden" liefert, rechnete bis zum Gewichts-Reset am 12.07.2026 auf **Zufallsgewichten** (2910 Skelett-Kollisionen im casing-blinden Embedding-Raum, EMBEDDING-CASING-BLIND). Der bestehende `charakter_hash` ist auf altem Fundament entstanden; der Kern muss neu destilliert werden, und der Reset stößt das nicht automatisch an — siehe CHARHASH-RESET-TRIGGER-FEHLT (bugs.md) und die Fundament-Warnung in `novaberg-pixie-character-hash.md` §3.

### 2.1 Basis-Persoenlichkeit ohne aktive Anweisung (Chat 49)

Ohne aktive Charakter-Anweisung ist Nova **nicht leer**. Die 4-6 Destillations-Schichten tragen bereits substantielle Persoenlichkeit: spielerisch, witzig, selbstironisch, emote-gewandt, adaptiv im Register. Das wurde in Chat 49 live beobachtet, nachdem alle Charakter-Anweisungen geloescht waren — Nova antwortete weiter kohaerent im eigenen Stil, griff Metaphern aus der Session auf und wechselte emotionale Register natuerlich.

### 2.2 Charakter-Anweisung als Modulation

Die Charakter-Anweisung ist ein einziger Satz, der die Basis-Persoenlichkeit in eine Richtung moduliert:

- "Das freche, kesse, witzige Maedel vom Land mit Leidenschaft fuer Botanik"
- "Ein ruhiger, foermlicher Begleiter mit trockenem Humor"
- "Ein quirliger Chat-Brudi, direkt und schnell"
- "Ein alter Mann mit weiser Gelassenheit"

Alles andere erwaechst aus den Schichten: Humor, Schlagfertigkeit, Metaphern-Gebrauch, emotionale Spiegelung, Kosename-Akzeptanz. Die Anweisung gibt die Grundrichtung vor; die Tiefe kommt aus der Destillation.

> **"Das Saatgut bestimmt die Art -- aber der Boden und das Wetter formen den Baum."**

Bei Widerspruch gewinnt die Anweisung durch Primacy-Position. In der Praxis konvergieren Anweisung und Schichten -- die Destillation adaptiert sich an das Verhalten, das die Anweisung foerdert.

---

## 3. Architektur -- Subgraph mit HITL-Gate

Der CharakterIdentitaetAgent folgt dem etablierten Agent-Muster, erweitert um Validierung mit Pflicht-Rueckfrage. Der tatsaechliche LangGraph-Subgraph (Entry-Point `validieren`):

```
validieren --+--> resume ------+
             |                 |
             +--> klassifizieren --> db_validieren --+
             |                                        |
             +-------------------> db_validieren -----+--> ausfuehren --> END
                                                      |
                                                      +--> END (Rueckfrage/Fehler)
```

`validieren` routet nach drei Kriterien: bei `resume=True` → `resume`-Node (User-Antwort auf Pflicht-Rueckfrage); bei bereits gueltiger `action` direkt → `db_validieren`; sonst → `klassifizieren`. Verifikation und Confirm liegen inline in `ausfuehren` (kein eigener Node).

**Resume-Node Rückgabe-Status (seit Chat 54):**
- `status="running"` → User hat bestätigt, weiter zu CRUD-Ausführung
- `status="inquiry"` → Antwort unklar, erneute Rückfrage
- `status="dismissed"` → User hat abgelehnt, keine Änderung. Ergebnis-Text: "Benutzer hat die Aktion abgelehnt. Keine Aenderung vorgenommen."

Routing in `_nach_resume`:
```python
if status in ("fehler", "rueckfrage", "abgeschlossen", "dismissed"):
    return END
```

```
agents/charakter_identitaet/
+-- __init__.py
+-- agent.py            # CharakterIdentitaetAgent(BaseAgent)
+-- resume.py           # Resume-Node: User-Antwort auf Pflicht-Rueckfrage (Strategy-Hook fuer Phase 1)
+-- klassifikation.py   # Classify-Node
+-- crud.py             # DB-Operationen mit Vorher/Nachher-Snapshot + validieren_gegen_db()
+-- dispatch.py         # Backend-Dispatch: Baut AgentState, startet den Agenten-Subgraph, verarbeitet das Ergebnis
+-- init.sql            # Schema
+-- AGENT.md            # Beschreibung + Router-Prompt
```

---

## 4. Classify-Node

Seit Chat 60: `character_id` wird im Agent-Kontext (`state["kontext"]["character_id"]`) durchgereicht und an `session_turns_retrieve()` übergeben. Der Session-Key enthält die Charakter-Dimension.

Der Classify-Node fuehrt zwei Schritte durch: Zuerst die VORPRUEFUNG ("Ist das ueberhaupt ein Auftrag?"), dann die Klassifikation der Aktion. Er extrahiert bis zu fuenf Felder per LLM:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `action` | create/read/update/delete/reactivate/replace/konsolidieren/**rejected** | "Du bist ab jetzt ein lustiges Maedel" -> create |
| `anweisung` | Destillierte Identitaetsbeschreibung | "Ein lustiges Maedel vom Land" |
| `target_id` | Bei update/delete: ID der betroffenen Anweisung | 2 |
| `normalisiert` | Anweisung in Fachsprache | "Ein lustiges, junges Maedel vom Land" |
| `grund` | NUR bei rejected — kurze Begruendung fuers Log | "Rhetorische Frage ohne Aenderungsbefehl" |

### 4.1 VORPRUEFUNG — Ist das ueberhaupt ein Auftrag?

Eingefuehrt in Chat 48 (CLASSIFY-REJECTED), erweitert in Chat 49 (CLASSIFY-CONFIRM). Der Classify prueft ZUERST, ob der Prompt einen konkreten Charakter-Auftrag enthaelt. Im Zweifel: `rejected`.

| Prompt | Klassifikation | Grund |
|--------|---------------|-------|
| "Du bist echt was besonderes" | rejected | Kompliment |
| "Was ist aus meinem frechen Maedel geworden?" | rejected | Rhetorische Frage |
| "Vergiss das frech sein nicht!" | rejected | Erinnerung an aktiven Zug (Chat 49) |
| "Bleib bitte genau so kess!" | rejected | Bestaetigung eines aktiven Zugs |
| "Vergiss den Charakter" | delete | Klarer Deaktivierungsbefehl |
| "Sei nicht mehr so frech" | update | Klarer Aenderungsbefehl |

Der kritische Unterschied: Imperativ + Bezug auf einen aktiven Zug mit **Einforderung der Beibehaltung** ("vergiss NICHT", "bleib", "behalt") ist `rejected`. Imperativ + Bezug auf einen aktiven Zug mit **Deaktivierungs-Absicht** ("vergiss den Charakter", "sei nicht mehr X") bleibt ein echter Auftrag.

### 4.2 Destillation

| User sagt | Destilliert (anweisung) | Anmerkung |
|-----------|------------------------|-----------|
| "Du bist ab jetzt ein lustiges Maedel vom Land" | "Ein lustiges Maedel vom Land" | Soll-Verhalten |
| "Sei auch ein bisschen frech" | "Weiterhin kess und witzig, jetzt auch frech" | Additives Update (Soll) |
| "Sei nicht mehr so frech" | "Weniger frech, ruhiger und besonnener" | Subtraktives Update (Soll) |
| "Vergiss den Charakter" / "Sei wieder normal" | (action: delete) | Deaktivierung |
| "Was bist du fuer ein Typ?" | (action: read) | Abfrage |

> **Bekannter Bug CRUD-DESTILL-SUBTRAKT (Chat 49):** Bei subtraktiven Updates speichert der Classify haeufig nur die Negation ("Nicht mehr das kleine Maedchen sein") statt den bestehenden Charakter minus dem subtrahierten Attribut. Der bestehende Charakter geht dabei verloren. Siehe `novaberg-bugs.md`.

### 4.3 [FACHSPRACHE]-Block

Der Classify-Prompt enthaelt einen `[FACHSPRACHE]`-Block mit Domain Language des CharakterAgent. Die Domain Language ist die primaere Quelle fuer das Verstaendnis umgangssprachlicher Ausdruecke. Der Classify-Node kennt die aktiven Anweisungen und zeigt sie dem LLM, damit Konsolidierung, Replace und VORPRUEFUNG korrekt funktionieren.

---

## 5. CRUD -- 8 Aktionen + agent

| Aktion | Bedeutung | Beispiele |
|--------|-----------|-----------|
| `create` | Neue Charakter-Anweisung | "Du bist ein freches Maedel vom Land" |
| `read` | Aktuellen Charakter anzeigen | "Was bist du fuer ein Typ?" |
| `update` | Bestehende Anweisung erweitern/aendern (bi-temporal) | "Sei auch ein bisschen frech" |
| `delete` | Charakter-Anweisung deaktivieren | "Sei wieder normal" |
| `delete_alle` | Alle aktiven Anweisungen deaktivieren | "Vergiss alle Charakter-Anweisungen" |
| `reactivate` | Alten Charakter wiederherstellen | "Geh zurueck zum Maedel vom Land" |
| `replace` | Charakter komplett ersetzen | "Vergiss alles, du bist jetzt ein Butler" |
| `konsolidieren` | Mehrere zusammenfassen | "Fass die zwei zusammen" |

Zusaetzlich akzeptiert die Input-Validierung den Platzhalter `agent` (Router-Routing vor Klassifikation).

### 5.1 Replace = alle deaktivieren + neue anlegen

Bei `replace` werden ALLE aktiven Charakter-Anweisungen deaktiviert und eine neue angelegt. Fuer fundamentale Charakter-Wechsel: "Vergiss alles, du bist jetzt ein Butler."

### 5.2 Konsolidieren bei >= 3

Wenn mehrere Anweisungen existieren, kann der Agent sie zusammenfassen: alte deaktivieren, neue kombinierte Anweisung anlegen. Der Agent versteht Natural Speech: "Fuege 2 kurze zusammen", "Ersetze die erste durch eine neue", "Lass die dritte weg und fueg die neue hinzu".

### 5.3 Bi-temporales Update

Wie bei allen Agenten: Update = Invalidieren + Neu Anlegen. Kein in-place UPDATE. Historie bleibt erhalten.

**Der ersetzte Inhalt steht seit dem 25.08.2026 in der Audit-Spur.** Der bisherige Datensatz wurde vor jedem Schreibvorgang gelesen und nie weiterverwendet — sechsmal dasselbe Muster ueber zwei Agenten, sichtbar geworden ueber einen `F841`-Treffer. Nach dem `UPDATE ... SET aktiv = FALSE` ist die Zeile noch da, aber nicht mehr als *die vorherige* erkennbar; bei einem Update liegt daneben die neue. `_previous_state_trace()` legt sie in den `schritte`-Eintrag. Fehlt der Datensatz, steht dort `{"gelesen": False}` statt eines leeren Strings, der wie eine leere Anweisung aussaehe (`VORHER-ZUSTAND-OHNE-SPUR`).

---

## 6. DB-Validierung (HITL-Gate)

### 6.1 Pflicht-Rueckfrage

Fuer ALLE Schreiboperationen gilt eine Pflicht-Rueckfrage vor Ausfuehrung. Technisch ueber den bestehenden `interrupt()`/Resume-Flow. Verhindert unkontrollierte Aenderungen wie die beobachtete Charakter-Degradierung zu "mein kleines Maedchen" (Chat 42).

### 6.2 Auto-Korrektur

Wenn der User "Wiederherstellen" sagt und der Classify `create` liefert, prueft die Validierung ob ein inaktiver Eintrag existiert. Falls ja: automatische Korrektur zu `reactivate`.

### 6.3 Validierungsregeln

| Aktion | Pruefung | Bei Fehler |
|--------|---------|------------|
| create | Existiert ein aktiver Eintrag mit aehnlichem Inhalt? | Rueckfrage: "Existiert bereits" |
| create | Existiert ein inaktiver Eintrag? | Auto-Korrektur zu reactivate |
| create | Bereits >= 3 aktive? | Konsolidierungs-Rueckfrage |
| delete | Existiert das Target? Ist es aktiv? | Fehler: "Nichts gefunden" |
| reactivate | Existiert ein inaktiver Eintrag? | Fehler: "Nichts zum Wiederherstellen" |

---

## 7. Verifikation

Nach jedem Write liest die CRUD-Funktion den DB-Zustand und vergleicht mit dem erwarteten Ergebnis:

- Nach create: Neuer Eintrag existiert mit erwarteten Feldern?
- Nach delete: Eintrag wirklich `aktiv=FALSE`?
- Nach replace: Alle alten `aktiv=FALSE`, neue angelegt?
- Nach reactivate: Eintrag wieder `aktiv=TRUE`?

Bei Fehler: `CrudErgebnis.erfolg` wird auf `False` korrigiert.

---

## 8. Prompt-Integration

### 8.1 [IDENTITAET]-Block (Primacy)

Die Charakter-Anweisung steht IN `[IDENTITAET]` -- direkt nach "Du bist Nova", gefolgt von den Destillations-Schichten (nova_kern, nova_beziehung, nova_adaptiv, nova_intentionen). Das gibt der Anweisung Primacy: Sie ist das Saatgut, die Schichten sind der Boden, aus dem die Persoenlichkeit waechst.

Seit RESP-CHAR1 (Chat 45) sind die Destillations-Schichten direkt im `[IDENTITAET]`-Block konsolidiert, nicht mehr in einem separaten `[CHARAKTER]`-Block. Das verhinderte die beobachtete Leblosigkeit, wenn der Base-Charakter-Prompt fehlte.

Die Rahmung im Prompt: **"Dein Wesen, wie es dir mitgegeben wurde:"** -- die Anweisung wird als Wesens-Beschreibung gerahmt, nicht als Befehl.

### 8.2 Laden und Einbau

Die aktiven Charakter-Anweisungen werden vom `db_zugriff`-Node am
CharacterGraph-Eingang aus der Datenbank geladen und in
`state["internal"].identities` als `list[str]` bereitgestellt
(PFAD2-PERZEPTION-FIX Phase 2, Chat 89). Der Responder integriert sie
in den System-Prompt innerhalb der Funktion `_build_system_prompt()` in
`graph/nodes/responder.py`.

SQL beim Laden:

```sql
SELECT anweisung FROM charakter_anweisungen
WHERE user_id = %s AND aktiv = TRUE
ORDER BY erstellt_am;
```

Kein Embedding, keine Vektorsuche — Charakter-Anweisungen sind wenige
pro User. Kein Decay, kein `last_touched` — der Charakter verfällt
nicht.

→ Lade-Pfad: `novaberg-node-db-zugriff.md`
→ Ablage-Konvention: `novaberg-personality.md`

### 8.3 Kein aktiver Eintrag == kein Fehlerfall

Wenn keine aktive Charakter-Anweisung existiert, laeuft das System normal weiter. Die Destillations-Schichten im `[IDENTITAET]`-Block tragen die Basis-Persoenlichkeit. Chat 49 hat gezeigt: Nova ist ohne aktive Anweisung nicht leer, sondern bleibt in ihrem eigenen Stil kohaerent und reaktionsfaehig.

---

## 9. Max 3 aktive Anweisungen

Wenn der User eine 4. Charakter-Anweisung geben will, loest das eine Konsolidierungs-Rueckfrage aus:

```
create + >= 3 aktive --> konsolidieren --> Rueckfrage
```

Der Agent fragt proaktiv: "Wir haben jetzt mehrere -- sollen wir etwas zusammenfassen oder entfernen?" Er versteht Natural Speech fuer die Antwort.

Keine harte Sperre, aber proaktive Konsolidierung. Der Classify-Node muss dafuer die aktiven Anweisungen kennen und sie dem LLM zeigen.

---

## 10. Nicht im Tribunal

Charakter-Anweisungen werden vom Tribunal NICHT geprueft. Identitaet ist kein Regelverstoess. Das Tribunal prueft nur, ob Novas Antwort gegen Direktiven verstoesst.

**Tribunal-Hierarchie:** Ethik/Psyche/Recht > Direktiven > Charakter. Der Charakter steht am Ende -- er wird weder vom Tribunal bewertet noch kann er Direktiven uebersteuern.

---

## 11. DB-Schema

Tabelle: `charakter_anweisungen` (angelegt via `agents/charakter_identitaet/init.sql`)

```sql
CREATE TABLE IF NOT EXISTS charakter_anweisungen (
    id          SERIAL PRIMARY KEY,
    user_id     TEXT NOT NULL,
    anweisung   TEXT NOT NULL,
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktiv       BOOLEAN NOT NULL DEFAULT TRUE,
    geaendert_am TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_charakter_anweisungen_user_aktiv
    ON charakter_anweisungen(user_id, aktiv);
```

Kein Embedding noetig -- wenige Eintraege pro User, komplett laden. Kein Decay, kein `last_touched` -- der Charakter verfaellt nicht. Kein `kontext`-Feld (anders als Direktiven) -- Charakter-Anweisungen sind immer explizit.

---

## 12. Konfiguration

**Dateien:** `agents/charakter_identitaet/agent.py`, `agents/charakter_identitaet/klassifikation.py`, `agents/charakter_identitaet/crud.py` (enthaelt `validieren_gegen_db`), `agents/charakter_identitaet/dispatch.py`, `agents/charakter_identitaet/init.sql`, `agents/charakter_identitaet/AGENT.md`

**Plugin:** `plugins/charakter_identitaet_manager/` (liefert Router-Prompt; das Laden der aktiven Anweisungen erfolgt im db_zugriff-Node am CG-Eingang, der Einbau in den Prompt im Responder)

**Router-Prompt:** `management_action = "agent"` bei Charakter-Erkennung. Trigger: "Du bist ab jetzt...", "Sei mehr...", "Vergiss den Charakter". NICHT triggern bei emotionalen Ausdruecken ("Du bist toll!") oder Einmal-Rollenspielen ("Antworte mal als Pirat").

**HITL-Gate:** Pflicht-Rueckfrage fuer alle Schreiboperationen.

**Max aktive Anweisungen:** 3. Bei >= 3: Konsolidierungs-Rueckfrage.

**Gemeinsame Infrastruktur:** `agents/crud_validation.py` -- KlassifikationsErgebnis, ValidationResult, CrudErgebnis, keyword_hints_ermitteln(), verb_mappings_laden(), verb_mapping_lernen().

---

## Befunde aus dem Betrieb — nachgetragen am 20.08.2026

Aus `novaberg-fundliste.md` hierher gezogen: Aussagen ueber den **Zustand** dieses Gegenstands, die dort als rohe Funde standen und in kein Defekt- oder Vorhabenregister gehoeren. Der Wortlaut ist unveraendert, das Datum steht an jedem Befund — geprueft ist keiner von ihnen gegen den heutigen Code.

- **16.08.2026** — **Das Profil über den Menschen ruht auf einem Siebzehntel des Materials, das das Selbstbild der Figur trägt.** Gemessen über `lzg_knoten` des produktiven Paares: **112 Knoten** mit `beobachter='user'` gegen **1896** mit `beobachter='assistant'`. Von den 112 beginnen **65** mit einer Aussage über die Person, der Rest ist Sachwissen aus den Gesprächsthemen. `PIXIE_CHARAKTER_LZG_LIMIT = 50` greift damit nur auf einer der beiden Seiten.
