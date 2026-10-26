# Novaberg — User-Agent: DirektivenAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** DirektivenAgent (Verhaltensanweisungen, Arbeitsvertrag)
**Stand:** 26. Oktober 2026, 07:51 UTC (`date -u`; §3 und §6.1: die Deutung der Antwort im Betrieb über den echten Weg gemessen, `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` und `ZURUECKHALTUNG-GILT-ALS-ZUSTIMMUNG` geschlossen). Davor 24. Oktober 2026, 22:21 UTC (`date -u`; die Commit-Kennung nachgetragen — Code-Tree `f901e08` ist `e1e0724`, die Doku dazu `d2d6ec8`). Davor 24. Oktober 2026, 21:35 UTC (`date -u`; §3: die Deutung der Antwort ist geschlossen — nur eine Antwort aus Zustimmung führt aus, Wörter, Zeichen und Wortstellung; `WAIT_STEMS` und `_holds_back` entfallen; Code-Tree `f901e08`, Kennung wird nachgetragen, im Betrieb nicht gemessen). Davor 24. Oktober 2026, 16:50 UTC (`date -u`; §3 und §6.1: die Commit-Kennung des Knotens `read_answer` nachgetragen — Code-Tree `2457549` ist `6846120`). Davor 24. Oktober 2026, 14:20 UTC (`date -u`; §3, §6.1 und §10: ein Knoten `read_answer` deutet die Antwort auf jede Rückfrage, bevor etwas ausgeführt wird — Ablehnung zuerst, eine zurückhaltende Antwort ist unklar, eine Auswahlfrage führt nie aus; gebaut im Code-Tree `2457549`, Kennung wird nachgetragen, im Betrieb nicht gemessen, `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` offen bis dahin). Davor 18. Oktober 2026, 01:01 UTC (`date -u`; §3 und §6.1: die Antwort auf die Pflicht-Rückfrage wird nicht gedeutet, auch ein Nein führt aus — `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS`, am Code gelesen). Davor 17. Mai 2026, Chat 90 (PFAD2-PERZEPTION-FIX abgeschlossen, HumanGraph-Slimming Phase 4)
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

Der DirektivenAgent folgt dem etablierten NotizenAgent/TimelineAgent-Muster, erweitert um eine Validierungsphase mit Pflicht-Rueckfrage. Der LangGraph-Subgraph ~~(Entry-Point `validieren`)~~ → bis zum 24.10.2026 (Entry-Point `validieren`; seither mit dem Knoten `read_answer`, Vermerk unten):

```
validieren --+--> ausfuehren (bei resume=True)
             |
             +--> klassifizieren --> db_validieren --+
             |                                        |
             +-------------------> db_validieren -----+--> ausfuehren --> END
                                                      |
                                                      +--> END (Rueckfrage/Fehler)
```

`validieren` routet nach drei Kriterien: bei `resume=True` → ~~direkt `ausfuehren` (kein eigener Resume-Node wie beim CharakterIdentitaetAgent — der Direktiven-Agent rehydriert die Aktion aus Redis-Pending und spielt die Ausfuehrung sofort ab)~~ → `read_answer`, der die Antwort deutet (unten); bei bereits gueltiger `action` → `db_validieren`; sonst → `klassifizieren`. Verifikation und Confirm liegen inline in `ausfuehren` (kein eigener Node).

> **Die Antwort wird dabei nicht gedeutet** — am Code gelesen am 18.10.2026, HEAD `ae05667`: `_nach_validierung` geht mit `resume` nach `ausfuehren` (`agent.py`, Z. 109–110), und `ausfuehren` liest `user_answer` nicht. **Auch ein Nein führt aus:** Wer *„Soll ich das ausfuehren? …“* verneint, löst die Aktion aus, nach der gefragt wurde. Offen als `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` (`novaberg-bugs-charakter.md`, Rang hoch; → geschlossen am 26.10.2026, Archiv `novaberg-bugs-archiv-charakter.md`).
>
> → **Seit dem Code-Tree `2457549` (24.10.2026, Kennung wird nachgetragen → committet als `6846120`; ~~im Betrieb nicht gemessen, `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` offen bis dahin~~ → im Betrieb gemessen am 26.10.2026 über den echten Weg, `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` geschlossen)** **deutet ein eigener Knoten die Antwort, bevor etwas ausgeführt wird:** `read_answer` (`agents/direktiven/resume.py`) steht zwischen `validieren` und `ausfuehren`; `_nach_deutung` geht nur bei `status` `laufend` — einer Zustimmung auf eine Ja/Nein-Frage — nach `ausfuehren`, sonst nach `END`.
>
> ```
> validieren --+--> read_answer (bei resume=True) --+--> ausfuehren --> END   (Zustimmung)
>              |                                    +--> END                  (Ablehnung, unklar, Auswahl, Fehler)
>              +--> klassifizieren / db_validieren wie oben
> ```
>
> **Die Deutung** (`_reading`), in dieser Reihenfolge:
>
> 1. **Ablehnung** zuerst, und sie gewinnt: ein Stamm aus `REFUSAL_STEMS` (`nein`, `ne`, `nee`, `nicht`, `kein`, `lass`, `abbruch`, `abbrech`, `stopp`, `stop`) als Teilzeichenkette, gesucht im Text **ohne** die Zustimmungswörter — *gerne* und *meinetwegen* stimmen zu, *„ja, aber lieber nicht“* lehnt ab. Ergebnis: `status` `abgeschlossen`, *„Gut, dann lasse ich es. An deinen Direktiven ist nichts geaendert.“*, Schritt `abgelehnt`, nichts ausgeführt.
> 2. ~~**Unklar**, wenn die Antwort etwas zurückhält (`_holds_back`): ein `?` an irgendeiner Stelle (*„Wie bitte?!“*, *„Ja? :)“*) oder ein Stamm des Wartens aus `WAIT_STEMS` (`wart`, `moment`, `augenblick`, `sekunde`, `halt`, auch mitten im Wort: *„Bitte warten“*, *„Sekunde, bitte“*). Absichtlich zu weit: *„Ja? Ja!“*, *„dann halt“*, *momentan* fragen ein zweites Mal.~~ → **Seit dem Code-Tree `f901e08` (24.10.2026, Kennung wird nachgetragen → committet als `e1e0724`, die Doku dazu als `d2d6ec8`; im Betrieb nicht gemessen) entfallen `WAIT_STEMS` und `_holds_back`:** Die Klasse dessen, was zurückhält, ablehnt oder aufschiebt, ist offen, und jede Liste davon ließ die nächste Form durch (*„Sekündchen, bitte“*, *„wait, ok“*, *„ja, aber erst morgen“* löschten). Die Zustimmung ist geschlossen, deshalb gilt die Annahme umgekehrt.
> 3. **Zustimmung** nur, wenn die Antwort **aus Zustimmung besteht** (`_consists_of_consent`): (a) mindestens ein Wort ist ein Zustimmungswort aus `CONSENT_WORDS` (als ganzes Wort, *ja* trifft *Jahr* nicht; darin auch *passt*); (b) **jedes** Wort ist ein Zustimmungswort oder ein Füllwort aus `FILLER_WORDS` — Artikel, Pronomen, das Hilfsverb *ist*, Partikeln, die nicht zögern (*mal, doch, ruhig, sehr*), und *danke*; nie ein Nomen, eine Zahl, ein Fragewort, ein Wort der Einschränkung oder des Aufschubs (*aber, sondern, statt, erst, nur, noch, lieber, später, morgen*) und nie *na*, *nun*, *also*; (c) **kein Zeichen** außer Buchstaben, Ziffern, Apostroph und den Zeichen aus `DROPPED_SIGNS` steht — ASCII-Leerraum und `. , ! ; : - ( )`; jedes Fragezeichen jeder Schrift (*„ja？“*, *„ja¿“*), jedes Emoji und jedes Symbol macht die Antwort unklar, ein ASCII-`?` ebenso; (d) die **Wortstellung** keine Frage ist: Ein Verb aus `ASKING_VERBS` (*ist*, *passt*) vor einem Wort aus `SUBJECT_WORDS` (*der, die, das, ein, ich, du, er, sie, es, wir, ihr, man, dies, diese, dieses, dieser*) im selben Satzteil macht die Antwort unklar (*„ist das ok“*, *„passt es“*), die Aussage stimmt zu (*„das ist ok“*, *„es passt“*); Satzteile enden nur an `, . ! ; :` (`CLAUSE_SEPARATORS`), *„ist - das ok“* und *„ist (das) ok“* fragen also; der Imperativ der Zustimmung fragt nicht (*„Ja, mach das“*). Dann wird die Aktion, nach der gefragt wurde, ausgeführt. **Sonst unklar:** dieselbe Frage noch einmal, `status` `rueckfrage`, Schritt `unklar`; `dispatch._handle_resume` erneuert den Pending-Zustand. Ein Wort, das die Mengen nicht kennen, kostet eine zweite Frage, nie eine Ausführung.
>
> Das gilt für alle drei Ja/Nein-Fragen (§6.1–§6.3). **Eine Auswahlfrage** (*„… Welche soll ich wiederherstellen?“*, *„… Welche soll ich entfernen?“*) **führt nie aus:** Eine Ablehnung beendet sie, jede andere Antwort stellt sie erneut (Schritt `auswahl_offen`), weil die Wahl aus der Antwort nicht gelesen wird. Die Art der Frage erkennt `_question_kind` am Wortlaut, den der Mensch gesehen hat (`parameter["original_rueckfrage"]`); eine Frage keiner bekannten Form ergibt `fehler`, laut im Log, und führt nichts aus. **Die Ausgabe-Verifikation** von `read_answer` prüft unabhängig vom gewählten Zweig: Weiter nach `ausfuehren` geht es nur ohne Ablehnungsstamm und mit einer Antwort, die aus nichts als Zustimmung besteht (`_consists_of_consent`), sonst `RuntimeError`.
>
> Die Wortlisten und Helfer (`_has_word`, `_has_stem`, `_without_words`) sind Kopien aus `agents/notizen/resume.py`, bewusst ohne gemeinsames Modul; ~~**die Zurückhaltung gibt es nur hier**~~ → seit `f901e08` tragen alle vier Ja/Nein-Dienste die geschlossene Annahme als Kopie (`novaberg-agent-notes.md` §7, `novaberg-agent-character.md`, `novaberg-agent-dateien_t.md`), bis `KLA-KLAERFALL-AM-OBJEKT` Schritte 5 und 6 sie ablösen. Zeugen: `tests/agents/direktiven/test_resume.py`, 35 Testmethoden, 18 über den Graphen; Server-Suite `Ran 5244 tests` grün. ~~Grenzen: Formen der Zurückhaltung, die kein Stamm trifft (*„Sekündchen, bitte“*, *„wait, ok“*, *„Ja, später“*, *„Wie bitte!“* ohne `?`), führen aus, ebenso eine Ablehnung ohne Stamm neben einer Zustimmung (*„ja, vergiss es“*, `ABLEHNUNG-OHNE-STAMM-BESTAETIGT`)~~ → seit `f901e08` unklar. **Zeugen der geschlossenen Annahme:** `ClosedConsentTest`, `ClosedSignsTest`, `RefusalFirstTest`, `ExcludedWordsTest`, `WordOrderTest` und `ClauseSeparatorsTest` in `tests/agents/direktiven/test_resume.py`, die Zeichen, die ausgeschlossenen Wörter, die fragenden Verben und die Trennzeichen je als eigenes Literal; Server-Suite `Ran 5394 tests` · `OK (expected failures=2)`. MESSUNG vor dem Commit: 305 ungezeigte Antworten, 0 Fehlausführungen. **Grenzen:** Der Preis sind Zustimmungen, die eine zweite Frage kosten (*„ja 👍“*, *„Ja…“*, *„ja – gerne“*, *„na klar“*, *„gut, ja“*, *„auf jeden Fall“*); *„mach ich das“* stimmt zu (mit *ich* gelesen eine Frage nach der Wortstellung), und die Frage nur durch Betonung (*„das ist ok“*, als Frage gemeint) bleibt Zustimmung (Fundliste, 24.10.2026). ~~Die Deutung bleibt im Betrieb ungemessen: `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` und `ZURUECKHALTUNG-GILT-ALS-ZUSTIMMUNG` sind offen bis dahin.~~ → Im Betrieb gemessen am 26.10.2026 über den echten Weg, an einem Prüf-Nutzer: Die Bitte zum Löschen einer Direktive erreicht die Pflicht-Rückfrage mit der richtigen Kennung, *„Wie bitte?“* und *„ist das ok“* erneuern sie, *„Nein“* löscht nicht, *„ja“* löscht; beide Kennungen sind geschlossen (Archiv, `novaberg-bugs-archiv-charakter.md`).

Der Classify-Node kann zusaetzlich zur Tabelle in §4 den Output `rejected` liefern (z.B. bei Kompliment/rhetorischer Frage statt echtem Direktiven-Auftrag) — dann bricht der Agent mit `status="rejected"` ab, ohne DB-Zugriff.

```
agents/direktiven/
+-- __init__.py
+-- agent.py            # DirektivenAgent(BaseAgent)
+-- klassifikation.py   # Classify-Node
+-- crud.py             # DB-Operationen mit Vorher/Nachher-Snapshot + validieren_gegen_db()
+-- resume.py           # seit 24.10.2026: read_answer, die Deutung der Antwort auf eine Rueckfrage
+-- dispatch.py         # Backend-Dispatch: Baut AgentState, startet den Agenten-Subgraph, verarbeitet das Ergebnis
+-- init.sql            # Schema
+-- AGENT.md            # Beschreibung + Router-Prompt
```

---

## 4. Classify-Node

Seit Chat 60: `character_id` wird im Agent-Kontext (`state["kontext"]["character_id"]`) durchgereicht und an `session_turns_retrieve()` übergeben. Der Session-Key enthält die Charakter-Dimension.

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

**Der ersetzte Inhalt steht seit dem 25.08.2026 in der Audit-Spur.** Der bisherige Datensatz wurde vor jedem Schreibvorgang gelesen und nie weiterverwendet — sechsmal dasselbe Muster ueber zwei Agenten, sichtbar geworden ueber einen `F841`-Treffer. Nach dem `UPDATE ... SET aktiv = FALSE` ist die Zeile noch da, aber nicht mehr als *die vorherige* erkennbar; bei einem Update liegt daneben die neue. `_previous_state_trace()` legt sie in den `schritte`-Eintrag. Fehlt der Datensatz, steht dort `{"gelesen": False}` statt eines leeren Strings, der wie eine leere Anweisung aussaehe (`VORHER-ZUSTAND-OHNE-SPUR`).

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

~~**Auf ein „Nein“ führt der Dienst ebenso aus** (am Code gelesen am 18.10.2026, §3): Die Rückfrage stellt er, ihre Antwort liest er nicht — `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS`, offen. Dasselbe gilt für *„… Trotzdem anlegen?“* (§6.2) und für die Frage nach dem Wiederherstellen (§6.3).~~ → **Seit dem Code-Tree `2457549` (24.10.2026, Kennung wird nachgetragen → committet als `6846120`; ~~im Betrieb nicht gemessen, `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` offen bis dahin~~ → im Betrieb gemessen am 26.10.2026 über den echten Weg, `DIREKTIVEN-FUEHRT-JEDE-ANTWORT-AUS` geschlossen)**: Auf alle drei Ja/Nein-Fragen führt nur eine Zustimmung aus; eine Ablehnung ändert nichts und sagt es, eine unklare oder zurückhaltende Antwort stellt dieselbe Frage erneut — auch auf *„… Trotzdem anlegen?“* (§6.2) und auf die Frage nach dem Wiederherstellen (§6.3), wo ein Nein auch keine neue anlegt (§3, *Die Deutung*). Die Rückfrage nennt bei `delete` und `update` ohne Kennung *„(ID None)“* (Fundliste, 24.10.2026).

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

~~Bei Fehler: `CrudErgebnis.erfolg` wird auf `False` korrigiert.~~ → **widerlegt am 16.09.2026, behoben am 18.09.2026:** `CrudErgebnis` hatte keinen einzigen Importeur, und der Dienst meldete trotz gescheiterter Verifikation `abgeschlossen` (`DIENST-MELDET-ABGESCHLOSSEN-OHNE-VERIFIKATION`). Seither laeuft jede verifizierende Rueckgabe durch `agents/write_outcome.py::verified_outcome`: nicht bestaetigt heisst Status `fehler` mit Begruendung und ohne Zusage. Die Datenstruktur `CrudErgebnis` (aus `agents/crud_validation.py`) erfasst Vorher/Nachher-Snapshot und Verifikationsstatus.

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

Die aktiven Direktiven werden vom `db_zugriff`-Node am
CharacterGraph-Eingang aus der Datenbank geladen und in
`state["internal"].directives` als `list[dict]` bereitgestellt
(PFAD2-PERZEPTION-FIX Phase 2, Chat 89). Der Responder integriert sie
in den System-Prompt innerhalb der Funktion `_build_system_prompt()` in
`graph/nodes/responder.py`.

SQL beim Laden:

```sql
SELECT anweisung, kontext FROM direktiven
WHERE user_id = %s AND aktiv = TRUE
ORDER BY erstellt_am;
```

Kein Embedding, keine Vektorsuche — Direktiven sind wenige, kurze
Regeln. Komplett laden ist effizienter und vermeidet das Risiko,
relevante Regeln durch Embedding-Schwächen zu verpassen.

→ Lade-Pfad: `novaberg-node-db-zugriff.md`
→ Ablage-Konvention: `novaberg-personality.md`

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

**Dateien:** `agents/direktiven/agent.py`, `agents/direktiven/klassifikation.py`, `agents/direktiven/crud.py` (enthaelt `validieren_gegen_db`), `agents/direktiven/resume.py` (seit 24.10.2026, `read_answer`), `agents/direktiven/dispatch.py`, `agents/direktiven/init.sql`, `agents/direktiven/AGENT.md`

**Plugin:** `plugins/direktiven_manager/` (liefert Router-Prompt; das Laden der aktiven Direktiven erfolgt im db_zugriff-Node am CG-Eingang, der Einbau in den Prompt im Responder)

**Router-Prompt:** `management_action = "agent"` bei Direktiven-Erkennung. Erkennungsmuster: Imperative mit "nie", "immer", "ab jetzt", "ab sofort"; Verbote: "nicht mehr", "hoer auf", "lass das".

**HITL-Gate:** Pflicht-Rueckfrage fuer alle Schreiboperationen. **Gemeinsame Infrastruktur:** `agents/crud_validation.py`.
