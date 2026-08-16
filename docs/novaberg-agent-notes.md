# Novaberg — User-Agent: NotizenAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Modul NotizenAgent — Merkzettel, Listen, Snippets (konsolidiert)
**Stand:** 08. Mai 2026, Chat 80 (NOTIZEN-VOR-TURN-BEZUG — Inhalts-Auflösung, kleinste Wirkstufe)
**Pfad:** novaberg/docs/novaberg-agent-notes.md
**Quellen:** nova-02-m-f.md (Modul), nova-14-k.md (CRUD-Haertung), nova-15-k.md (Domain Language)

---

## 1. Aufgabe

Der NotizenAgent verwaltet Freiform-Inhalte: Einkaufslisten, ToDos, Merkzettel, Entwuerfe, Ideensammlungen. Alles, was der Nutzer explizit ablegen will und was nicht in das Fakten- oder Timeline-Schema passt. Das LLM versteht den Inhalt — die DB speichert nur Text. "Streich die Milch von der Einkaufsliste" wird vom LLM als neue Version der Liste generiert.

Der NotizenAgent war der erste migrierte Agent unter Epic 11 (Phase 2, Chat 22–23). Er ersetzte den frueheren NotizenManager (Plugin-System) und demonstrierte das volle Agent-Pattern: LangGraph-Subgraph, 5-Node-Architektur, pg_trgm-Suche, Resume-Flow fuer Rueckfragen.

---

## 2. Architektur: 6-Node-Subgraph

```
Validate → Resume? → Classify → Search → CRUD → Confirm
```

| Node | Datei | Aufgabe |
|------|-------|---------|
| `validieren` | `agent.py` | Pflichtfelder pruefen. Akzeptiert `"agent"` als Aktion (→ Classify-Node). |
| `resume` | `resume.py` | Resume-Flow bei Pending-Agent. Drei Pfade: Disambiguierung, Duplikat, Fallback. |
| `klassifizieren` | `klassifikation.py` | LLM-Call: Bestimmt action, target, target_typ. Container-vs-Inhalt-Regel. Session-Kontext fuer Rueckbezuege. |
| `suchen` | `suche.py` | Gewichtete Multi-Feld-Suche mit pg_trgm. |
| `ausfuehren` | `crud.py` | CRUD-Operation durchfuehren. LLM-Call fuer Create/Update. |
| `bestaetigen` | `bestaetigung.py` | Status setzen. Ueberschreibt `rueckfrage`/`fehler` nicht blind. |

**Routing-Logik (in agent.py):**

```
validieren
  ├─ fehler → END
  ├─ resume → resume → ...
  ├─ create/read/update/delete/append → direkt weiter (abwaertskompatibel)
  └─ agent → klassifizieren
                ├─ fehler → END
                ├─ create → ausfuehren → bestaetigen → END
                └─ read/update/delete → suchen → ausfuehren → bestaetigen → END
```

### File-Split-Konvention

| Datei | Inhalt | Zeilen |
|-------|--------|--------|
| `agent.py` | Klasse, Properties, build_graph(), Routing, _validieren | ~120 |
| `klassifikation.py` | Classify-Node (LLM-Prompt, Session-Kontext) | ~110 |
| `resume.py` | resume(), Disambiguierung, Duplikat-Aufloesung | ~145 |
| `suche.py` | suchen(), SUCH_GEWICHTE, Score-Gap | ~180 |
| `crud.py` | ausfuehren(), _create, _update, _delete, _append | ~270 |
| `bestaetigung.py` | bestaetigen() | ~20 |

Oeffentliche Node-Einstiegspunkte ohne Unterstrich (z.B. `resume()`), private Helfer mit Unterstrich (z.B. `_resume_disambiguierung()`). Node-Funktionen sind Standalone (kein `self`), nur `_validieren` bleibt als Methode auf der Klasse.

---

## 3. Classify-Node — Container vs. Inhalt

Seit Chat 60: `character_id` wird im Agent-Kontext (`state["kontext"]["character_id"]`) durchgereicht und an `session_turns_retrieve()` übergeben. Der Session-Key enthält die Charakter-Dimension.

Der Classify-Node loest AGT7: Der Router konnte "Streich die Bananen von der Obstliste" nicht von "Streich die Obstliste" unterscheiden. Der Agent kann das — per LLM mit einer expliziten Regel:

**Praeposition (von/aus/auf/zu)** → Inhalt-Operation → `update`
- "Streich die Milch VON der Liste" → update
- "Setz Kaese AUF die Liste" → update

**Ohne Praeposition + direktes Objekt** → Container-Operation → `delete`
- "Streich die Einkaufsliste" → delete
- "Loesch die Obstliste" → delete

### 9 Aktionen (erweiterte Taxonomie, Chat 42)

| Aktion | Bedeutung | Beispiele |
|--------|-----------|-----------|
| `create` | Neue Notiz anlegen | "Erstelle eine Einkaufsliste" |
| `read` | Notiz anzeigen | "Was steht auf der Einkaufsliste?" |
| `update` | Generische Aenderung | "Aendere die Einkaufsliste: nur Obst" |
| `append` | Text anhaengen (ohne LLM-Neugenerierung) | "Haeng an die Notiz dran: ..." |
| `add_content` | Inhalt hinzufuegen (semantisch via LLM) | "Fuege Milch zur Einkaufsliste hinzu" |
| `remove_content` | Inhalt entfernen | "Streich Shampoo von der Liste" |
| `clear_content` | Alle Inhalte leeren | "Leere die Einkaufsliste" |
| `rename` | Notiz umbenennen | "Nenn die Liste 'Samstags-Einkauf'" |
| `delete` | Notiz komplett loeschen | "Loesch die Einkaufsliste" |

Zusaetzlich akzeptiert die Input-Validierung den Platzhalter `agent` (Router-Routing vor Klassifikation). Der Classify-Node kennt die 9 Aktionen, die Input-Validierung alle 9 + `agent`.

### Domain Language — [FACHSPRACHE]-Block (Chat 43, Epic 15)

Der Classify-Node normalisiert den User-Prompt in die Fachsprache des Notizen-Systems. Neues Feld `normalisiert` im JSON-Output:

| User sagt | Normalisiert |
|-----------|-------------|
| "Hau die Bananen raus" | "remove_content: Bananen aus Notiz 'Einkaufsliste' entfernen" |
| "Setz Kuemmel drauf" | "add_content: Kuemmel zu Notiz 'Einkaufsliste' hinzufuegen" |
| "Notiere dir: Durch diese hohle Gasse..." | "create: Neue Notiz anlegen mit Inhalt: Durch diese hohle Gasse..." |
| "Hau die Scheiße raus" | "remove_content: Bananen von Notiz 'Einkaufsliste' entfernen" |
| "Schmeiss noch Milch drauf" | "add_content: Milch zu Notiz 'Einkaufsliste' hinzufuegen" |
| "Mach ne neue Liste fuer den Baumarkt" | "create: Neue Notiz 'Baumarkt' mit Typ 'einkauf' anlegen" |
| "Leg sie bitte an" *(nach Listen-Turn)* | "create: Neue Notiz mit Inhalt: Halloumi, Feta, Paneer" |
| "Schreib das auf" *(nach Aufzählungs-Turn)* | "create: Neue Notiz mit Inhalt: Bohrer, Dübel, Schrauben" |

Die CRUD nutzt `normalisiert` als primaere Anweisung, den Originaltext (`aufgabe`) als Inhaltsquelle. Trennung: Normalisierung steuert die Aktion, Originaltext liefert den woertlichen Inhalt.

```python
DOMAIN_LANGUAGE = {
    "aktionen": {
        "create": "Neuen Eintrag anlegen",
        "read": "Bestehenden Eintrag anzeigen",
        "update": "Bestehenden Eintrag inhaltlich aendern",
        "delete": "Eintrag deaktivieren (Soft-Delete)",
        "add_content": "Inhalt zu bestehendem Eintrag hinzufuegen",
        "remove_content": "Inhalt aus bestehendem Eintrag entfernen",
        "clear_content": "Gesamten Inhalt eines Eintrags leeren",
        "rename": "Titel eines Eintrags aendern",
    },
    "entitaeten": ["Notiz", "Liste", "Merkzettel", "Entwurf"],
    "format": "{action}: {beschreibung} (betrifft {entitaet} '{name}')",
}
```

Classify-Output (erweitert):

```json
{
    "action": "update",
    "target": "Einkaufsliste",
    "target_typ": "inhalt",
    "konfidenz": "hoch",
    "normalisiert": "remove_content: Bananen von Notiz 'Einkaufsliste' entfernen"
}
```

Primacy/Recency-Reihenfolge im Classify-Prompt: [IDENTITAET] → [AUFGABE] → [FACHSPRACHE] → [REGELN].

### Inhalts-Auflösung aus Vor-Turns (seit Chat 80)

Der Classify-Node erhält über `session_turns_retrieve(user_id, character_id)` die letzten 5 Vor-Turn-Paare als `[KONTEXT]`-Block. Bis Chat 80 war die Nutzung dieses Verlaufs explizit auf Target-Auflösung beschränkt — der Prompt verbot Inhalts-Auflösung.

Seit Chat 80 darf der Classify-Node den Verlauf für **Target-Auflösung und Inhalts-Auflösung** nutzen. Bezugs-Anweisungen wie *"Leg sie bitte an"* nach einem Listen-Turn werden aufgelöst, indem der Klassifikator den vollständigen Vor-Turn-Inhalt in das `normalisiert`-Feld extrahiert.

**Beispiel:**

- Vor-Turn: *"Halloumi, Feta, Paneer kommen mir in den Sinn"*
- Aktueller Prompt: *"Leg sie bitte als Notiz an"*
- Klassifikator-Output: `normalisiert = "create: Neue Notiz mit Inhalt: Halloumi, Feta, Paneer"`

**Logging:** DEBUG-Log nach jedem LLM-Call mit `normalisiert`-Feld. INFO-Log mit Heuristik *"Inhalts-Auflösung erkannt: aufgabe={N} Zeichen, normalisiert={M} Zeichen"* wenn `normalisiert` deutlich länger ist als `aufgabe`.

**Reichweite:** Diese Wirkstufe deckt **einen Vor-Turn-Sprung** in **CREATE-Aktionen** ab. Mehrschrittige Rekonstruktion über mehrere Turns oder Bezugsauflösung in UPDATE/RENAME-Pfaden ist **nicht** abgedeckt — siehe Bugs NOTIZEN-KONTEXT-REKONSTRUKTION und NOTIZEN-UPDATE-TARGET-LEER. Die strukturelle Lösung ist das Frame-Konzept (`novaberg-thinking-frames_k.md`) Phase 1b.

---

## 4. Suche — pg_trgm gewichtete Multi-Feld-Suche

### SUCH_GEWICHTE (suche.py)

| target_typ | w_name | w_text | w_themen |
|---|---|---|---|
| `titel` | 2.0 | 1.0 | 1.0 |
| `inhalt` | 1.0 | 2.0 | 0.5 |
| `thema` | 1.0 | 1.0 | 2.0 |

### SQL-Kern

```sql
SELECT id, name, typ, text, themen,
  (similarity(name, query) * w_name +
   similarity(text, query) * w_text +
   MAX(similarity(thema, query)) * w_themen) AS score
FROM notizen
WHERE aktiv = TRUE AND (similarity(name, q) > 0.15 OR similarity(text, q) > 0.15 OR ...)
ORDER BY score DESC
LIMIT 10
```

**Post-Filter:** Ergebnisse mit `score < 0.3` werden nach dem SQL-Query verworfen. Der WHERE-Clause nutzt einen niedrigeren Schwellenwert (0.15) pro Feld, um Kandidaten nicht vorzeitig auszuschliessen. Der kombinierte Score muss aber >= 0.3 sein.

### Score-Gap-Disambiguierung

Nach der Suche wird die Kandidaten-Liste auf die Gewinner-Gruppe reduziert:
1. Berechne `avg = Durchschnitt aller Scores`
2. Gehe die sortierte Liste durch, finde den ersten Gap >= avg
3. Alles oberhalb der Trennlinie = Gewinner-Gruppe
4. Count=1 → klarer Gewinner, direkt weiter
5. Count>1 → Disambiguierung, aber nur mit der reduzierten Menge

Formel: `gap >= avg` (nicht `>`). Validiert mit 20 Edge Cases.

### Fallback-Kette

Wenn die gewichtete Suche nach dem Min-Score-Filter (0.3) null Treffer liefert:
1. Exakter Name-Match (`find_by_stichwort`, ILIKE)
2. Volltext-Suche (`find_by_volltext`, tsvector)

### Rueckfrage bei nicht gefundener Notiz (Chat 43)

Bei `add_content` oder `remove_content` + Notiz nicht gefunden: Echte Rueckfrage statt Fehler. Der pending State bewahrt `original_aufgabe` (den rohen User-Prompt). Bei Bestaetigung setzt `_resume_nicht_gefunden()` die `aufgabe` auf den Originaltext zurueck — die CRUD extrahiert den Inhalt korrekt.

Vorher: "ja, bitte" als Notiz-Inhalt. Nachher: "Kuemmel" korrekt aus dem Originaltext extrahiert.

**Indexe:** `idx_notizen_user`, `idx_notizen_status`, `idx_notizen_themen`, `idx_notizen_entitaet_ids` (alle `db/init.sql`), dazu `idx_notizen_timeline_id` aus `agents/timeline/init.sql`.

> **Am 16.08.2026 berichtigt.** Hier standen ~~`idx_notizen_name_trgm` (Chat 23)~~ und ~~`idx_notizen_text_trgm` (Chat 24)~~ als GIN-Indexe. **Beide existieren nicht** — weder unter diesem noch unter einem ähnlichen Namen. Die Erweiterung `pg_trgm` ist in `db/init.sql` aktiviert, aber **auf `notizen` liegt kein einziger Trigramm-Index**; die fünf vorhandenen decken Besitzer, Status, Themen, Entitäten und den Timeline-Bezug ab. Wer sich auf unscharfe Namenssuche verlassen hat, hat sie nie gehabt.

---

## 5. CRUD-Operationen

### Create
1. `management_target` als Name (User-Wortlaut — Namens-Treue)
2. LLM extrahiert Typ, Text und Themen aus dem User-Prompt (JSON-Output)
3. Zusammenfassung generieren (Heuristik: erste 20 Woerter)
4. Duplikat-Check: Existiert eine Notiz mit gleichem Namen? → Rueckfrage. Bei Resume mit "neue anlegen": Duplikat-Check wird uebersprungen (`skip_duplikat_check`).
5. INSERT ueber `NotizenRepository`

Das `normalisiert`-Feld steuert die CRUD, der Originaltext (`aufgabe`) liefert den woertlichen Inhalt fuer die LLM-Extraktion.

### Read
Gewichtete Multi-Feld-Suche. Bei `read` reicht erster Treffer. Sonderfall: `read` ohne Target listet alle aktiven Notizen als kompakte Uebersicht (Name, Typ, Zusammenfassung).

### Update / add_content / remove_content
Das LLM generiert die neue Version. Der Agent laedt die aktuelle Notiz und gibt beides an das LLM:

```
System: Du bearbeitest eine Notiz. Fuehre die gewuenschte Aenderung durch.
        Antworte NUR mit dem neuen, vollstaendigen Notiz-Text.

User:   Aktuelle Notiz: Milch, Eier, Brot, Butter
        Aenderungswunsch: Streich die Milch
        Neuer Notiz-Inhalt:
```

→ LLM: "Eier, Brot, Butter"

Kein Diff, kein Regex — das LLM versteht natuerliche Sprache besser als jeder Parser.

### Delete (Soft-Delete)
`status = 'archiviert'` UND `aktiv = FALSE`. Kein Hard-Delete. Beide Felder werden synchron gesetzt (AGT-FIX5, Chat 22).

### clear_content (deterministisch)
Leert den Inhalt einer Notiz. Kein LLM-Call noetig — rein deterministische Operation.

### rename
Aendert den Titel einer bestehenden Notiz.

### append
Text an bestehende Notiz anhaengen — ohne die bestehende Version neu zu generieren.

---

## 6. CRUD-Haertung (Chat 42, Epic 14)

### Dreistufige Erkennung

**Stufe A — Statische Keyword-Hints (Python, vor dem LLM-Call):**

```python
KEYWORD_HINTS = {
    "fuege.*hinzu|hinzufuegen|aufnehmen|nimm.*auf|ergaenz":    "add_content",
    "streich|nimm.*raus|entferne.*von|runter von":              "remove_content",
    "leere|alles loeschen|komplett leeren":                     "clear_content",
    "loesch|entfern|weg damit|streich .*komplett":              "delete",
    "aendere|aendern|aktualisier|korrigier":                    "update",
    "zeig|was hast|welche|liste|auflisten":                     "read",
}
```

**Stufe B — Lernende Verb-Mappings (PostgreSQL, pro User):** Bei unbekanntem Verb (z.B. "hau rein") klassifiziert das LLM, bei niedriger Konfidenz wird rueckgefragt, bei Bestaetigung wird das Mapping gelernt. Ab `konfidenz >= 3` keine Rueckfrage mehr.

**Stufe C — LLM-Klassifikation:** Bekommt Keywords + Verb-Mappings als `[ERKENNUNGSHILFE]`-Block. Mit Chat 44 (Domain Language) verschiebt sich die primaere Erkennung auf den `[FACHSPRACHE]`-Block. Keywords und Verb-Mappings dienen als sekundaere Konfidenz-Pruefung.

### Konfidenz

| Situation | Konfidenz | Aktion |
|-----------|-----------|--------|
| Keyword-Hint + LLM stimmen ueberein | Hoch | Direkt validieren |
| Verb-Mapping (>=3) + LLM stimmen ueberein | Hoch | Direkt validieren |
| Verb-Mapping (<3) + LLM stimmen ueberein | Mittel | Direkt validieren, Konfidenz++ |
| Nur LLM, kein Hint | Niedrig | Rueckfrage + ggf. Verb lernen |
| Hint und LLM widersprechen sich | Konflikt | Rueckfrage |

### Verifikation (DB-Read nach Write)

Nach jeder Schreiboperation liest die CRUD den DB-Zustand und vergleicht mit dem erwarteten Ergebnis. Bei Fehler wird `CrudErgebnis.erfolg` auf `False` korrigiert — keine halluzinierte Bestaetigung.

### Keine Pflicht-Rueckfrage

NotizenAgent erfordert Rueckfrage nur bei niedriger Konfidenz oder Konflikt (anders als Direktiven/Charakter).

---

## 7. Resume-Flow

### 3 Pfade

| Pfad | Ausloeser | Aktion |
|------|----------|--------|
| Disambiguierung | Mehrere Treffer, User waehlt | Matching auf Kandidaten, gewaehlte Notiz verarbeiten |
| Duplikat | Notiz existiert bereits | User entscheidet: aktualisieren oder neu anlegen |
| nicht_gefunden | add_content/remove_content + Notiz fehlt | `original_aufgabe` bewahrt, bei "ja" wird Notiz angelegt mit korrektem Inhalt |

### Kette

1. Agent setzt `status=rueckfrage` + formuliert Rueckfrage-Text
2. Dispatch speichert `pending_agent:{user_id}` in Redis (TTL 300s)
3. Router erkennt im naechsten Turn den Pending-Agent → `management_action=resume`
4. Planner sieht `resume` → Schleifen-Schutz `_agent_bereits_gelaufen()` (Chat 106), dann `agent_name` aus Redis
5. Agent._resume bearbeitet die Antwort

**Terminierung bei Rueckfrage-auf-Rueckfrage (Chat 106):** Liefert `_resume` erneut
`status=rueckfrage` (Antwort unklar, kein Match), schreibt der Dispatch den Pending-Key
sofort wieder nach Redis — die Terminierung besorgt dann der Planner-Guard: Der Agent
lief in diesem Turn bereits, der Turn endet, der Responder stellt die neue Rueckfrage,
der Pending-Key wartet auf den naechsten echten User-Turn. Ohne den Guard rekursierte
genau dieser Fall bis Recursion-Limit 25 (AGENT-RUECKFRAGE-LOOP, gefixt `f1b3a27`).
Details: `novaberg-node-planner.md` §3.1.

### Rueckfrage-Szenarien

| Situation | Rueckfrage |
|-----------|----------|
| Create ohne Name oder Text | "Mir fehlt noch: Stichwort/Name der Notiz" |
| Create mit existierendem Namen | "Es gibt bereits eine Notiz 'X'. Aktualisieren oder neu anlegen?" |
| Delete/Update mit mehreren Treffern | "Ich habe mehrere Notizen gefunden: 'X', 'Y'. Welche meinst du?" |
| add_content/remove_content + Notiz nicht gefunden | "Einkaufsliste existiert nicht. Soll ich sie anlegen?" |

---

## 8. Notiz-Typen

| Typ | Beispiele |
|-----|-----------|
| `einkauf` | Einkaufslisten |
| `todo` | Aufgabenlisten |
| `merkliste` | Gesammelte Links, Referenzen |
| `notiz` | Allgemeine Merkzettel |
| `entwurf` | Textentwuerfe, Formulierungen |
| `idee` | Brainstorming, Konzepte |

Der Typ wird vom LLM beim Erstellen klassifiziert — nicht vom Nutzer explizit angegeben.

---

## 9. DB-Schema

Tabelle: `notizen` (angelegt via `db/init.sql`; eine eigene `agents/notizen/init.sql` existiert nicht)

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `id` | SERIAL | Primaerschluessel |
| `user_id` | VARCHAR(50) | Gedaechtnis-Partition |
| `name` | VARCHAR(255) | Stichwort / Kurzname |
| `typ` | VARCHAR(50) | einkauf, todo, merkliste, notiz, entwurf, idee |
| `text` | TEXT | Vollstaendiger Inhalt |
| `zusammenfassung` | TEXT | Erste 20 Woerter (Heuristik) |
| `themen` | TEXT[] | PostgreSQL-Array fuer Themen-Tags |
| `status` | VARCHAR(20) | `aktiv` oder `archiviert` |
| `aktiv` | BOOLEAN | Partial Index fuer Soft-Delete |
| `created_at` | TIMESTAMPTZ | Erstellungszeitpunkt |
| `updated_at` | TIMESTAMPTZ | Letzte Aenderung |

pg_trgm Extension: `CREATE EXTENSION IF NOT EXISTS pg_trgm` in `db/init.sql`.

---

## 10. Konfiguration

| Parameter | Wert | Beschreibung |
|-----------|------|-------------|
| NOTIZEN_SUCHE_MIN_SIMILARITY | 0.15 | WHERE-Schwellenwert pro Feld (pg_trgm) |
| NOTIZEN_SUCHE_MIN_SCORE | 0.3 | Post-Filter fuer kombinierten Score |
| Score-Gap-Formel | `gap >= avg` | Disambiguierungs-Schwelle |
| Redis Pending TTL | 300s | Timeout fuer Rueckfrage-Flow |
| Zusammenfassung | Erste 20 Woerter | Heuristik fuer Notiz-Zusammenfassung |
| Konfidenz-Lernschwelle | 3 | Ab 3 Bestaetigungen keine Rueckfrage |

---

## 11. Offene Punkte

**Offen — durch Live-Test in Chat 80 entdeckt, strukturelle Lösung im Frame-Konzept Phase 1b:**

- NOTIZEN-KONTEXT-REKONSTRUKTION — Mehrschritt-Rekonstruktion über mehrere Turns
- NOTIZEN-CONTAINER-WECHSEL — Notiz↔Liste-Wechsel als legitime Aktion
- NOTIZEN-SKILL-MANIFEST — Nova kennt eigene Fähigkeiten in Sprach-Schicht nicht
- NOTIZEN-UPDATE-TARGET-LEER — Bezugs-Pronomen im UPDATE-Pfad

Details siehe `novaberg-bugs.md` und `novaberg-backlog.md`. Lösungsraum: `novaberg-thinking-frames_k.md` §16.2 (Phase 1b).
