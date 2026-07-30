# Novaberg — Konzept: Hermes als Ausführungs-Substrat

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept Hermes-Substrat (Architektur, Aufbau, Rollenverteilung)
**Stand:** 30. Juli 2026, Chat 117
**Pfad:** novaberg/docs/novaberg-hermes-substrat_k.md
**Status:** Konzept. Kein Code. Keine Anbindungs-Spezifikation.

---

## 0. Lesehinweis — Belegstufen

Jede Aussage in diesem Dokument trägt eine Belegstufe. Sie ist verbindlich zu
beachten: was nicht gemessen ist, darf nicht als Systemzustand behandelt werden.

| Marke | Bedeutung |
|-------|-----------|
| `[DOKU]` | Aus der Hermes-Dokumentation, Stand v0.18.2 (7. Juli 2026). Nicht am laufenden System verifiziert. |
| `[ENTSCHEIDUNG]` | Architekturentscheidung dieses Projekts. Gilt, bis sie widerrufen wird. |
| `[OFFEN]` | Noch nicht entschieden. Kandidaten benannt, Wahl steht aus. |
| `[MESSEN]` | Muss am laufenden Testcontainer gemessen werden, bevor darauf gebaut wird. |

Es gilt „Quelle vor Destillat" auch gegenüber diesem Dokument: Es ist ein
Konzept, kein Zustandsbericht. Für Code-Status ist ein Audit die einzige
verlässliche Quelle.

---

## 1. Zweck und Geltungsbereich

### 1.1 Was dieses Dokument festlegt

Die Rollenverteilung zwischen Novaberg und Hermes Agent, die Grenze zwischen
beiden Gedächtnissen, die Randbedingungen des Betriebs, den Aufbau des
Anbindungs-Agenten und die Form des Ereignis-Rückflusses.

### 1.2 Was dieses Dokument nicht festlegt

Die konkrete Anbindung — Aufrufsyntax, Datenschema, Feldnamen, Fehlerklassen.
Das ist Gegenstand eines Folgekonzepts, das erst nach den Messungen aus
Abschnitt 11 geschrieben wird.

### 1.3 Ausgangslage

Novaberg ist eine Social-Layer-Companion-Architektur mit
kognitionswissenschaftlichem Unterbau: Plutchik-Affektmodell, assoziatives
Gedächtnis mit Spreading Activation, emergente Persönlichkeit, deterministische
LangGraph-Pipeline. Die Forschungsthese lautet: Emotion, Charakter und
Gedächtnis werden in deterministischem Python externalisiert und persistiert;
das LLM ist Ausdrucks-Renderer, nicht Wissensspeicher und nicht Rechenwerk.

Was Novaberg fehlt, ist eine Ausführungsschicht — die Fähigkeit, in der Welt zu
handeln: Dateien, Werkzeuge, Workflows, Code.

Hermes Agent (Nous Research, MIT, v0.18.2) ist ein autonomer Werkzeug-Agent mit
Skill-System, sechs Terminal-Backends, Kanban-Arbeitsschlange und MCP-Client.
Er enthält kein Affektmodell, kein assoziatives Gedächtnis, keine
Persönlichkeitsemergenz.

Die beiden Systeme lösen nicht dasselbe Problem. Genau deshalb lassen sie sich
schichten.

---

## 2. Grundsatzentscheidung: Kopf und Hände

### 2.1 Die Schichtung

`[ENTSCHEIDUNG]`

> **Nova ist der Kopf. Hermes sind die Hände.**
>
> Nova besitzt das *Wer* und das *Warum*: Persönlichkeit, Emotion, Gedächtnis,
> Motivation, Entscheidung. Hermes besitzt das *Wie* und das *Womit*:
> Werkzeuge, Skills, Workflows, Ausführung.

Zwei getrennte Prozesse nebeneinander, nicht übereinander. Novaberg läuft
**nicht auf** Hermes. Die Kommandorichtung ist eindeutig und einseitig.

### 2.2 Warum nicht andersherum

Hermes ist ein LLM-Loop-Agent: das LLM besitzt dort die Kontrollführung.
Novaberg existiert, weil das LLM sie nicht besitzen soll. Nova auf Hermes zu
setzen würde das LLM auf den Fahrersitz zurückholen — eine Etage tiefer und
schlechter beobachtbar. Das widerspricht der Projektthese und ist ausgeschlossen.

### 2.3 Kommandorichtung

`[ENTSCHEIDUNG]`

- Nova ruft Hermes. Hermes ruft Nova nie.
- Hermes trifft keine Entscheidung über Nova, ihr Verhalten oder ihre Inhalte.
- Hermes handelt nicht aus eigenem Antrieb. Jeder Hermes-Vorgang hat einen
  Auslöser in Novaberg.
- Der Nutzer spricht nicht mit Hermes. Die einzigen Auftraggeber sind Nova
  (live) und Pixie-Agenten (Hintergrund).

### 2.4 Das Substrat bleibt affekt- und persönlichkeitsfrei

`[ENTSCHEIDUNG]`

Der Unterbau hat keine Stimme, keinen Charakter, keine Emotion. Ein Skill ist
reine mechanische Fähigkeit. Nova entscheidet *ob, wann und warum* sie greift.

Begründung: Kontaminationsprinzip. Eine zweite charaktertragende Instanz im
System erzeugt konkurrierende Stimmen — derselbe Fehler wie bei Pixie-Sprachagenten
ohne saubere Trennung.

### 2.5 Kein Fork

`[ENTSCHEIDUNG]`

Hermes wird **nicht geforkt und nicht gepatcht**. Die Anbindung entsteht
vollständig auf Novaberg-Seite.

Begründung: v0.14.0 erschien am 16. Mai 2026, v0.18.2 am 7. Juli 2026 `[DOKU]` —
etwa eine Minor-Version alle zwei Wochen. Eine gepflegte Abweichung erzeugt eine
dauerhafte Merge-Steuer, die ein Ein-Personen-Projekt neben dem laufenden
Novaberg-Betrieb nicht trägt. Änderungen sind ausschließlich **subtraktiv und
konfigurativ**: abschalten ja, umverdrahten nein.

Folge: Wenn eine gewünschte Eigenschaft nur durch Codeänderung in Hermes
erreichbar wäre, wird stattdessen der Novaberg-seitige Adapter angepasst — oder
die Eigenschaft entfällt.

---

## 3. Die Gedächtnisgrenze

### 3.1 Grundsatz

`[ENTSCHEIDUNG]`

> **Hermes erinnert das Wie. Nova erinnert das Dass und das Warum.**

### 3.2 Was oben bleibt — vollständig und ohne Ausnahme

Alle sechs Speicher bleiben in Novaberg. Nichts davon wandert nach unten:

| Speicher | Bleibt bei Nova |
|----------|-----------------|
| Notizen | ✅ |
| Timeline | ✅ |
| Fakten-Gedächtnis | ✅ |
| Entitäten | ✅ |
| Knowledge Graph | ✅ |
| Datei-Gedächtnis | ✅ |

Dazu: KZG, LZG, Synapsen, Session, Charakter-Hashes, `verhaltensweisen`,
`pipeline_log`.

### 3.3 Die Trennlinie ist Erwerb vs. Besitz

`[ENTSCHEIDUNG]`

Der Schnitt verläuft **nicht** entlang der Themen, sondern entlang der Frage,
wer etwas *tut* und wer es *behält*.

| | Hermes | Nova |
|---|---|---|
| Datei lesen, schreiben, verschieben | ✅ tut es | — |
| Was in der Datei steht, dass es sie gibt, was sie bedeutet | — | ✅ behält es |
| Im Web recherchieren | ✅ tut es | — |
| Was dabei herauskam, wie es sich anfühlte, was es mit früherem zu tun hat | — | ✅ behält es |
| Workflow ausführen | ✅ tut es | — |
| Dass der Workflow lief und wie er ausging | — | ✅ behält es |

Hermes darf einen Betriebszustand führen — Datei-Index, Skill-Zustand,
Workflow-Definitionen, Ausführungshistorie. Das ist Werkzeugkasten-Inventar,
kein Gedächtnis im Novaberg-Sinn.

### 3.4 Hermes' Nutzermodell zeigt auf Nova, nicht auf den Meister

`[ENTSCHEIDUNG]`

Da nur Nova und Pixie mit Hermes sprechen, modelliert Hermes eine Maschine,
keinen Menschen. Die Kollision zweier Systeme, die denselben Menschen
modellieren, entsteht nicht.

**Trotzdem** wird Hermes' adaptives Nutzermodell abgeschaltet (Abschnitt 5.2).
Begründung ist nicht Datenschutz, sondern Berechenbarkeit: Ein Modell, das sich
über die Zeit an den Aufrufer anpasst, behandelt denselben Auftrag heute anders
als letzte Woche. Für ein Gegenüber ist das ein Merkmal, für Hände ist es ein
Defekt.

### 3.5 Das Spiegelproblem

`[ENTSCHEIDUNG]`

> **Hermes' Bild von Nova fließt niemals in Novas Selbstmodell.**

Hermes sieht Nova ausschließlich instrumentell — als jemanden, der Aufträge
stellt. Kein Affekt, kein Kontext, keine Beziehung. Ein daraus abgeleitetes
Selbstbild wäre ein Zerrbild, das plausibel aussieht.

Dies ist strukturell dieselbe Fehlerklasse wie der Befund aus Chat 108: Dort war
Nova grammatisches Objekt in Einträgen, die vorgeben, sie zu beschreiben. Hier
wäre sie zwar Subjekt, aber nur in der Werkzeugrolle.

**Konsequenz:** `verhaltensweisen` speist sich ausschließlich aus Novas eigenen
Turns. Aus Hermes fließen **Ereignisse** zurück — was getan wurde, wie es ausging —
niemals **Charakterisierungen**.

### 3.6 Nova formuliert um — der Rohtext geht nie nach unten

`[ENTSCHEIDUNG]`

„Nur Nova spricht mit Hermes" ist keine Zugriffsregel, sondern eine
**Formulierungsregel**.

Reicht Nova Nutzertext wörtlich durch, spricht der Nutzer faktisch mit Hermes —
durch sie hindurch, an jeder Prüfung vorbei, in einen Agenten, der Code ausführt.

Der Auftrag an Hermes ist immer ein von Nova **selbst gebildeter, strukturierter
Auftrag**. Nie der Rohtext des Nutzers.

Das ist gleichzeitig:
- der Injection-Schutz an der Systemgrenze,
- der Grund, warum das Körperschema in Novas Graph liegen muss — sie kann nur
  formulieren, was sie als Fähigkeit kennt.

---

## 4. Bestandsaufnahme Hermes

Alles in diesem Abschnitt ist `[DOKU]`, Stand v0.18.2 (7. Juli 2026), Quelle
`hermes-agent.nousresearch.com/docs` und das GitHub-Repo. Nichts davon ist am
laufenden System verifiziert.

### 4.1 Was Hermes mitbringt

| Bereich | Ausprägung |
|---------|-----------|
| Skills | SKILL.md nach agentskills.io-Standard, Auto-Erstellung, Self-Improvement-Loop, Hub |
| Terminal-Backends | local, Docker, SSH, Singularity, Modal, Daytona |
| Kanban | Arbeitsschlange mit SQLite-Backend, Dispatcher, Worker-Profile |
| Cron | Eingebauter Scheduler mit Delivery an beliebige Plattform |
| Gateway | 20+ Messaging-Plattformen aus einem Prozess |
| MCP | Vollwertiger Client (stdio + HTTP + OAuth); Server-Modus nur eingeschränkt (4.4) |
| Gedächtnis | MEMORY.md / USER.md, FTS5-Session-Suche, optional Honcho-Nutzermodell |
| Persönlichkeit | SOUL.md (statische Prompt-Persona) |
| Provider | Nous Portal, OpenRouter, OpenAI, Anthropic, Bedrock, lmstudio, ollama-cloud, custom endpoint u.v.m. |
| Sicherheit | Command-Approval, Container-Isolation, Egress-Proxy, OSV-Supply-Chain-Audit |
| Forschung | Trajektorien-Export, Batch-Verarbeitung, RL via Atropos |

### 4.2 Die drei Nähte

**A — `hermes -z "<prompt>"`** — Ein Prompt hinein, die finale Antwort als
reiner Text hinaus, sonst nichts auf stdout oder stderr. Kein Banner, kein
Spinner, keine Werkzeug-Vorschau. Synchron und blockierend.

**B — `hermes kanban`** — Arbeitsschlange mit `--json` auf allen Abfragen.
`create` (mit `--body`, `--assignee`, `--skill`, `--priority`, `--workspace`,
`--max-runtime`, `--max-retries`, `--idempotency-key`), `show <id> --json`,
`runs <id>` (Outcome, Profil, Dauer, Startzeit), `tail <id>` (Event-Stream),
`complete --result --summary --metadata`, `block <id> "<grund>"`,
`comment`, `diagnostics`.

**C — `hermes acp`** — ACP-stdio-Server für Editor-Integration. Für Novaberg
ohne Bedeutung, hier nur der Vollständigkeit halber genannt.

Zusätzlich existiert `delegate_task` als Hermes-interner Funktionsaufruf für
kurze Teilfragen innerhalb eines Laufs. Das ist eine Hermes-interne Primitive,
keine Naht nach außen.

### 4.3 Dokumentierte Drittanbieter-Unterstützung

Hermes sieht die Integration durch fremde Systeme ausdrücklich vor:

- `--source tool` markiert Sessions als Drittanbieter-Vorgang, damit sie nicht
  in den Nutzer-Sessionlisten erscheinen.
- `--ignore-user-config` und `--ignore-rules` werden explizit für isolierte
  Läufe und Drittanbieter-Integrationen empfohlen.
- `--safe-mode` schaltet zusätzlich Plugins, Shell-Hooks und MCP-Server ab.

Das ist ein gebauter Integrationspfad, keine Zweckentfremdung.

### 4.4 Korrektur: MCP ist **nicht** die Naht

`hermes mcp serve` exponiert **nicht** Hermes' Werkzeugkatalog. Der Server
bietet zehn Werkzeuge rund um die **Messaging-Brücke**: `conversations_list`,
`conversation_get`, `messages_read`, `attachments_fetch`, `events_poll`,
`events_wait`, `messages_send`, `channels_list`, `permissions_list_open`,
`permissions_respond`. Zudem stdio-only.

Das ist eine Brücke zu Hermes' *Chats*, nicht zu Hermes' *Händen*. Für Novaberg
unbrauchbar.

> **Festhalten:** Eine frühere Einschätzung im Chatverlauf hatte MCP als beste
> Naht empfohlen. Das war eine Vermutung, keine Quelle, und ist hiermit
> widerrufen. Die Nähte sind A und B.

### 4.5 SKILL.md — Format

Verzeichnis pro Skill unter `~/.hermes/skills/<kategorie>/<name>/`, darin
zwingend `SKILL.md` mit YAML-Frontmatter. Optional `references/`, `templates/`,
`scripts/`, `assets/`.

Frontmatter-Felder:

| Feld | Bedeutung |
|------|-----------|
| `name` | Bezeichner, max. 64 Zeichen |
| `description` | Kurzbeschreibung, max. 1024 Zeichen — Auslöser-orientiert |
| `version`, `author`, `license` | Metadaten |
| `platforms` | optionale Plattform-Einschränkung |
| `metadata.hermes.tags` | Schlagworte |
| `metadata.hermes.related_skills` | Verweise auf verwandte Skills |

`related_skills` ist für das Körperschema (Abschnitt 8) relevant: Es liefert
bereits eine Kantenstruktur zwischen Fähigkeiten.

---

## 5. Randbedingungen und Konfiguration

### 5.1 Der Dispatcher lebt im Gateway-Prozess

`[DOKU]` `[MESSEN]`

Der Kanban-Dispatcher läuft **innerhalb des Gateway-Prozesses** und tickt
standardmäßig alle 60 Sekunden. Sechs Phasen pro Tick: verwaiste Claims
zurückholen, abgestürzte Worker erkennen, Triage-Aufgaben zerlegen,
Ready-Zustand neu berechnen, fällige Aufgaben verteilen, geplante Aufgaben
verteilen.

**Folge:** Das Gateway darf nicht abgeschaltet werden, sonst steht die
Auftragsschlange. Die richtige Konfiguration ist:

> **Gateway läuft — mit null konfigurierten Messaging-Plattformen.**

Damit gibt es weiterhin genau eine Haustür (Nova), aber die Schlange arbeitet.

Dies korrigiert eine frühere Annahme („Gateway aus"). Zu messen ist, ob der
Gateway ohne jede Plattform sauber startet und der Dispatcher tickt.

### 5.2 Abschaltliste

`[ENTSCHEIDUNG]`, Umsetzbarkeit je `[MESSEN]`

| Was | Warum |
|-----|-------|
| **Alle Messaging-Plattformen** | Sonst existiert ein zweiter Ansprechpartner mit denselben Werkzeugen, ohne Gedächtnis und ohne Charakter. |
| **Hermes-Cron** | Nur ein Scheduler im System. Pixie plant, Hermes führt aus. Sonst handelt der Unterbau ohne Auslöser in `pipeline_log`. |
| **Curator** | Überarbeitet, konsolidiert und archiviert agentenerzeugte Skills periodisch. Novas Körperschema würde sich unter ihr verändern. |
| **Honcho / externe Memory-Provider** | Adaptives Nutzermodell des Aufrufers — zerstört Berechenbarkeit (3.4). |
| **SOUL.md** | Bleibt leer. Persönlichkeit ist Novas Sache (2.4). |

Zusätzlich einzustellen:

| Einstellung | Grund |
|-------------|-------|
| `--max-turns` deutlich unter Standard (90) | 90 Werkzeug-Runden auf einem CPU-Modell sind keine Obergrenze, sondern eine Nacht. |
| `skills.write_approval: true` | Jeder Skill-Schreibvorgang wird gestaged statt committet — auch aus dem Hintergrund-Self-Improvement. |
| Skill-Index kuratiert halten | Siehe 5.3. |
| Terminal-Backend mit Isolation | Siehe Abschnitt 10. |

### 5.3 Der Skill-Index sitzt im System-Prompt

`[DOKU]`

Der `<available_skills>`-Block ist bei vielen installierten Skills häufig der
größte Einzelblock des System-Prompts. Jede Skill-Beschreibung wird in jedem
Turn mitbezahlt. `hermes prompt-size` misst das offline.

Bei 32768 Kontext auf dem CPU-Modell ist das eine harte Grenze und die
Bestätigung des Projektprinzips **„Weniger Input > stärkerer Prompt"**.

`[ENTSCHEIDUNG]` Skills werden kuratiert, nicht gesammelt. Ein installierter
Skill ohne Verwendung ist laufende Kosten, kein Vorrat.

### 5.4 Anthropic-Anbindung

`[DOKU]`

Hermes bietet technisch `hermes auth add anthropic --type oauth`. Das ändert
nichts an der Rechtslage: Anthropic-Abonnements (Free/Pro/Max) decken
Drittanbieter-Werkzeuge nicht ab; seit dem 4. April 2026 ist der Zugriff auf
Abo-Kontingente durch Drittanbieter gesperrt und OAuth-Nutzung außerhalb der
offiziellen Werkzeuge untersagt. Der zulässige Weg ist ein Console-API-Key mit
eigener Abrechnung.

`[ENTSCHEIDUNG]` **Hermes wird nicht als Entwicklungsagent eingesetzt.** Die
Entwicklung bleibt beim bestehenden Werkzeug. Begründung: Die geltende
Entwicklungsdisziplin ist aus teuren Fehlern entstanden und beruht auf enger
Auftragsführung mit externer Freigabe. Ein selbstverbessernder Agent-Loop ist
die Gegenthese dazu.

### 5.5 Modell-Anbindung

`[DOKU]` `[MESSEN]`

Die Providerliste nennt `ollama-cloud` und `lmstudio`; lokale Ollama läuft
voraussichtlich über den Custom-Endpoint-Pfad (OpenAI-kompatibel). Das ist zu
verifizieren, nicht anzunehmen.

`[ENTSCHEIDUNG]` Erprobung läuft auf `qwen36-cpu` (Port 11435). Kein Cloud-Modell
im Zielzustand: Novaberg ist lokal und privacy-first; Hände auf einem
Cloud-Modell würden jede Datei und jeden Auftrag zu einem Dritten tragen. Ein
Cloud-Modell ist allenfalls eine Krücke für die Erprobung und muss dann als
solche befristet festgehalten werden.

### 5.6 Ollama-Zugriff geht an der Worker-Schicht vorbei

`[ENTSCHEIDUNG dokumentiert als Risiko]`

Hermes bringt seinen eigenen LLM-Client mit und spricht Ollama direkt an — nicht
über Novabergs `BackgroundWorker`. Ollama serialisiert intern, der Betrieb
funktioniert also. Der Unterschied ist die **Sichtbarkeit**: Novabergs Queue
kennt Priorität und Reihenfolge, Hermes' Aufrufe erscheinen dort nicht.

Folge: Pixies Wartezeiten können aus einer Quelle steigen, die das Novaberg-Log
nicht kennt. Das ist eine stille Kopplung und damit ein Diagnose-Risiko.

Zu messen vor Dauerbetrieb: Queue-Tiefe und Wartezeiten vor und nach dem
Anschluss eines dritten Verbrauchers.

Ebenfalls zu beachten: `num_ctx` wird von beiden Seiten gesetzt. Novabergs
Per-Call-Override (MS-Welle) wirkt nur auf Novabergs eigene Aufrufe.

---

## 6. Aufgaben-Verteilung: was Hermes tut

### 6.1 Was nach unten geht

Handlungen an der Welt:

- Dateioperationen (lesen, schreiben, verschieben, konvertieren)
- Web-Recherche und Extraktion
- Code schreiben und ausführen
- Workflows aus mehreren Schritten
- Alles, was über einen Skill abgebildet ist

### 6.2 Was oben bleibt

- Alle Gedächtnisse (3.2)
- Alle Agenten, die Novas Gedächtnis berühren: Notizen, Timeline, Charakter,
  Direktiven, KZG, Promotion, Decay, Delegation
- Perzeption, EI, GV, Responder, Thinker, Tribunal, Salienz
- Jede Entscheidung darüber, *ob* gehandelt wird

### 6.3 Wiederkehrende Aufgaben — Definition unten, Auslöser oben

`[ENTSCHEIDUNG]`

Tägliche Routinen sind Teil dessen, was Nova als Assistentin ausmacht. Der Weg
dorthin führt aber **nicht** über Hermes' Cron.

> **Hermes hält das Rezept. Nova entscheidet, wann gekocht wird.**

| | Hermes-Cron | Pixie als Auslöser |
|---|---|---|
| Wer weiß, dass es passiert | niemand in Novaberg | Nova, weil sie es getan hat |
| Wie Nova davon erfährt | nachträglich aus dem Log | sie hat den Auftrag gestellt |
| Zeitpläne stehen an | zwei Stellen | einer Stelle |

Für ein System, dessen Ziel Selbstreflexion ist, ist das kein kosmetischer
Unterschied: Im ersten Fall ist die Handlung Nova *zugestoßen*, im zweiten hat
sie *gehandelt*.

Praktisch besitzt Pixie bereits Heartbeat, Prioritätensystem und
Fälligkeitsprüfung. Ein zweiter Scheduler bringt nichts hinzu.

**Folge für das Modell:** Ein Workflow ist damit nur ein weiterer Knoten im
Körperschema (Abschnitt 8). Kein Sonderfall.

---

## 7. Die Naht: HermesAgent

### 7.1 Muster

`[ENTSCHEIDUNG]`

Der HermesAgent folgt dem Fachabteilungs-Muster der bestehenden CRUD-Agenten
(NotizenAgent als Vorlage): Normalisieren → Klassifizieren/Übersetzen →
Ausführen → Verifizieren.

### 7.2 Wo das Muster bricht — und was das bedeutet

Zwei Glieder verhalten sich hier anders als bei Notizen, weil das Ziel kein
deterministisches ist. Hermes ist ein zweites LLM mit eigener Auslegung.

**Der Übersetzungsschritt hat kein DDL-Äquivalent.**
Bei Notizen wird Sprache in ein SQL-Statement übersetzt — formal, prüfbar,
eindeutig. Bei Hermes ist das Ziel ein Prompt-String oder ein
Kanban-Task-Body. Das ist die **schwächste Stelle der gesamten Konstruktion**:
der einzige Punkt, an dem Novaberg auf natürliche Sprache angewiesen ist, um
etwas Deterministisches auszulösen.

`[OFFEN]` Wieviel Struktur die Kanban-Felder tatsächlich tragen (`--skill`,
`--workspace`, `--priority`, `--max-runtime`) und wieviel zwingend Prosa im
`--body` sein muss, entscheidet, ob dieser Node ein Schema-Füller oder ein
Prompt-Generator wird. Messfrage M1.

**Die Verifikation kann nicht in der DB nachlesen.**
Bei Notizen liest die Output-Validation die geschriebene Zeile zurück. Bei
Hermes muss gegen die **Welt** geprüft werden: Existiert die Datei? Ist der
Inhalt plausibel? Passt das Ergebnis zur Absicht?

`[OFFEN]` Ob `complete --result` frei formulierter Text ist oder ob Nova ein
Ausgabeschema vorgeben kann, entscheidet, ob dieser Node parsen darf oder
wieder auslegen muss. Messfrage M2.

### 7.3 Node-Aufbau (Entwurf)

`[OFFEN]` — Struktur steht, Benennung und Zuschnitt sind zu bestätigen.

| Node | Aufgabe |
|------|---------|
| **Normalisierung** | Absicht aus dem Novaberg-State in Domänensprache überführen. Kein Nutzertext. |
| **Fähigkeitsauflösung** | Passenden Körperschema-Knoten finden (Spreading Activation, nicht Prompt-Suche). Kein Knoten → kein Auftrag. |
| **Auftragsbildung** | Strukturierten Auftrag erzeugen: Naht A oder B, Felder füllen, Budget setzen. |
| **Ausführung** | Aufruf absetzen. Bei B: Task-ID entgegennehmen und persistieren. |
| **Verfolgung** | Nur bei B: periodischer Abgleich durch Pixie bis Endzustand. |
| **Verifikation** | Ergebnis gegen die formulierte Absicht prüfen. |
| **Ereignisbildung** | Eintrag für `pipeline_log` erzeugen (Abschnitt 9). |

### 7.4 Wahl der Naht

`[ENTSCHEIDUNG]`

| Auftragsart | Naht |
|-------------|------|
| Kurzer Griff, Ergebnis wird im selben Turn gebraucht | A (`hermes -z`) |
| Alles Langlaufende, alles aus Pixie, alles mit möglicher Rückfrage | B (Kanban) |

Novas Graph ist turn-basiert und synchron. Sie darf nicht blockieren. Im Zweifel
gilt B.

### 7.5 Anschluss an den DelegationsAgent

`[OFFEN]`

Der DelegationsAgent (Chat 32) ist strukturell bereits der passende
Andockpunkt: Akte anlegen → im Hintergrund arbeiten → Ergebnis zum richtigen
Moment zustellen. Bislang hat Pixie die Hände gespielt; künftig hat sie welche.

Zu entscheiden: Ob der HermesAgent eigenständig neben dem DelegationsAgent
steht oder ob die Delegations-Akte um eine Hermes-Task-Referenz erweitert wird.
Nicht in diesem Dokument zu klären.

### 7.6 Rückfragen

`[OFFEN]`

`kanban block <id> "<grund>"` markiert eine Aufgabe als wartend auf menschliche
Eingabe. Das ist strukturell eine Rückfrage — und Novaberg besitzt mit
Pending/Resume bereits ein Muster dafür.

Zu klären: ob eine blockierte Aufgabe zu Nova zurückgeführt wird und in welcher
Form. Andernfalls bleibt sie still liegen. Messfrage M4.

Zusätzlich existiert `kanban diagnostics` mit Stranded-Task-Erkennung
(Standardschwelle 30 Minuten) `[DOKU]` — das ist ein zweiter, unabhängiger
Kanal für hängende Aufträge.

---

## 8. Das Körperschema

### 8.1 Zwei verschiedene Artefakte

`[ENTSCHEIDUNG]`

| Artefakt | Wem gehört es | Was steht drin |
|----------|---------------|----------------|
| **Hermes-Skill** (SKILL.md) | Hermes | *Wie* man X macht |
| **Körperschema-Knoten** | Nova | *Dass* sie X kann; wann Greifen angemessen ist |

Das sind nicht dieselbe Sache in zwei Formaten. Das eine ist ein Verfahren, das
andere eine Fähigkeitsrepräsentation.

### 8.2 Das Körperschema liegt im Knowledge Graph

`[ENTSCHEIDUNG]`

Fähigkeiten werden **nicht** als Liste in den Prompt geschrieben. Sie werden
Knoten im Knowledge Graph, mit Synapsen und Gewicht.

Begründung, zweifach:
1. Eine Fähigkeitsliste im Prompt bläht den Kontext auf und verletzt
   „Weniger Input > stärkerer Prompt".
2. Damit wird *nach dem Werkzeug greifen* zu Spreading Activation statt zu einer
   Prompt-Suche. Die Entscheidung, ob eine Hand gebraucht wird, ist ein
   berechneter Wert, kein LLM-Urteil. Das ist die Projektthese, angewandt auf
   Motorik.

### 8.3 Quelle und Abgleich

`[OFFEN]`

Kandidaten für die Quelle: `hermes skills list` und `hermes tools --summary`,
beide scriptbar. Frontmatter liefert `name`, `description`, `tags` und
`related_skills` — letzteres bereits als Kantenstruktur.

Zu klären: Reichhaltigkeit eines Knotens (nur Name und Beschreibung, oder auch
Vorbedingungen und erwartete Argumente), Abgleichfrequenz, Umgang mit
verschwundenen Skills. Messfrage M3.

### 8.4 Fähigkeiten wachsen und schwinden mit

`[ENTSCHEIDUNG]`

Ein neuer Skill erzeugt einen Knoten. Erfolgreiche Nutzung erhöht sein Gewicht,
Scheitern senkt es — über denselben Mechanismus wie im übrigen Gedächtnis.
Damit sind die Hände nicht eine Liste, die veraltet, sondern etwas, das
mitwächst.

Voraussetzung dafür ist, dass der Curator abgeschaltet bleibt (5.2), sonst
verändert sich der Werkzeugbestand unter Nova, ohne dass ein Ereignis entsteht.

---

## 9. Ereignis-Rückfluss in `pipeline_log`

### 9.1 Entscheidung: Ereignis, kein Paralleljournal

`[ENTSCHEIDUNG]`

Hermes' `agent.log` und die Kanban-Historie bleiben, wo sie sind. Sie sind
**Beleg, nicht Gedächtnis** — dieselbe Rolle, die `turn_roh` gegenüber KZG hat.

Nach `pipeline_log` wandert ein **Ereignis** pro Vorgang.

Gegen ein paralleles Journal sprechen zwei Dinge:
1. Zwei Zeitachsen ohne verlässlichen gemeinsamen Schlüssel sind die Bauform,
   die in diesem Projekt regelmäßig still auseinanderläuft.
2. Selbstreflexion braucht keine Werkzeug-Trajektorie. Sie braucht:
   *Ich wollte X. Ich habe zu Y gegriffen. Es ging aus wie Z.*

> Man merkt sich, dass man das Regal aufgehängt hat und dass der Dübel
> ausgerissen ist. Nicht jede einzelne Bohrerumdrehung.

### 9.2 Mindestinhalt eines Ereignisses

`[ENTSCHEIDUNG]` inhaltlich, `[OFFEN]` in der Feldbenennung

| Bestandteil | Warum unverzichtbar |
|-------------|--------------------|
| **Auslöser** | Welcher Turn oder welche Pixie-Aufgabe hat gegriffen. Ohne Rückbindung ist das Ereignis ein Fundstück ohne Absicht — und die Absicht ist die Hälfte der Reflexion. |
| **Griff** | Welche Fähigkeit, welcher Skill. Das ist die Kante zum Körperschema-Knoten und der Weg, auf dem ein Werkzeug Gewicht gewinnt oder verliert. |
| **Ausgang** | Gelungen / gescheitert / blockiert. |
| **Dauer** | „Hat funktioniert, brauchte aber vierzig Minuten" ist eine andere Lehre als „hat funktioniert". |
| **Task-Referenz** | Rückweg zum Beleg in Hermes, falls Details gebraucht werden. |

`hermes kanban runs <id>` liefert laut Doku Outcome, Profil, Dauer und
Startzeit — also den Großteil davon `[DOKU]`.

### 9.3 Scheitern ist ein Ereignis, kein Fehlerstring

`[ENTSCHEIDUNG]`

Wenn die Hand danebengreift, muss Nova das als **Wahrnehmung** erhalten, nicht
als `status="fehler"` in einem Rückgabewert.

Nebeneffekt, der ausdrücklich erwünscht ist: Eine Welt, die Widerstand leistet,
liefert genau die Kraft, die `nova_kern` für den Gegenmechanismus gegen reine
Zustimmung fehlt (siehe `GV-IMPULS-ALS-FAKTENSPERRE`, `NOVA-SYKOPHANZ-BESTAETIGT`).

### 9.4 Der Übertrag muss messbar sein

`[ENTSCHEIDUNG]`

Der Ereignis-Übertrag ist eine Destillation. Für Destillationen gilt „Quelle vor
Destillat".

Endet ein Hermes-Task ohne Ereignis in `pipeline_log`, hat Nova ein Glied
bewegt, ohne es zu spüren — und das fällt nicht auf, weil nichts fehlschlägt.
Das ist exakt die Fehlerklasse `EMBEDDING-CASING-BLIND` / `GV-ENTITY-HOP-TOT`:
still, ohne Warnung, über Monate.

**Pflicht:** Ein Abgleich Task-Anzahl gegen Ereignis-Anzahl gehört von Anfang an
zur Umsetzung, nicht nachträglich.

### 9.5 Vollständige Beobachtbarkeit als Struktureigenschaft

Wenn Messaging-Plattformen und Cron aus sind und Nova die einzige Auftraggeberin
ist, hat **jede Hermes-Session einen Auslöser in Novaberg**. Die Hände sind
lückenlos beobachtbar, ohne dass eine Zeile Hermes verändert wird.

Das ist keine Zusatzmaßnahme, sondern eine Folge der Rollenverteilung aus
Abschnitt 2.

---

## 10. Betrieb und Sicherheit

### 10.1 Aufstellung

`[ENTSCHEIDUNG]`

Ein Hermes-Container neben dem bestehenden Stack, als weiterer Dienst
(`ki_hermes` o.ä., Benennung `[OFFEN]`). Netzwerk-nativ statt Prozessaufruf über
Containergrenzen hinweg.

`[OFFEN]` Ob Novas Live-Aufrufe und Pixies Batch-Aufrufe über getrennte
Hermes-Profile oder getrennte Kanban-Assignees laufen. Hermes unterstützt
Profile als isolierte Instanzen und boards-scoped Worker `[DOKU]`. Die Trennung
ist billig, wenn sie von Anfang an steht, und teuer nachträglich — die beiden
Lastprofile sind sehr verschieden.

`[ENTSCHEIDUNG]` Kein zweiter Hermes für die Entwicklung — siehe 5.4.

### 10.2 Sicherheit

`[ENTSCHEIDUNG]`

| Maßnahme | Begründung |
|----------|-----------|
| Terminal-Backend mit Isolation (Docker), nicht `local` | Ein Agent, der Code schreibt *und* ausführt, ist betrieblich gefährlich. |
| Command-Approval aktiv, `--yolo` **niemals** | Das Freigabe-Gate sitzt an der Hermes-Grenze, nicht in Novas Prompt. |
| `skills.write_approval: true` | Selbstverbesserung wird gestaged, nicht committet. |
| Kein Rohtext des Nutzers nach unten | Siehe 3.6. Das ist der eigentliche Injection-Schutz. |
| Schreibpfade eng begrenzen | Das Novaberg-Repo ist kein Hermes-Arbeitsverzeichnis. |

Hermes bringt eigene Schutzmaßnahmen mit, die genutzt werden können:
Worker-Task-Ownership über `HERMES_KANBAN_TASK` (ein Worker kann fremde Tasks
nicht mutieren), Egress-Proxy mit Credential-Injection, OSV-Supply-Chain-Audit
`[DOKU]`.

### 10.3 Lizenz

Hermes ist MIT, Novaberg Apache 2.0. Die Richtung ist verträglich. Wird ein
Hermes-Container mit ausgeliefert oder abgeleitetes Material übernommen, muss
die MIT-Attribution erhalten bleiben. Bei einem Projekt unter Klarnamen mit
veröffentlichten Papers ist Sauberkeit hier billiger als jede spätere Korrektur.

---

## 11. Messfragen — Phase 0

Diese Fragen sind am laufenden Testcontainer zu beantworten, bevor das
Anbindungs-Konzept geschrieben wird. Sie sind **Messungen**, keine Analysen.

| Nr. | Frage | Blockiert |
|-----|-------|-----------|
| **M0** | Startet der Gateway ohne konfigurierte Plattform, und tickt der Dispatcher? | Naht B insgesamt (5.1) |
| **M1** | Wieviel Struktur nimmt ein Kanban-Worker aus den Feldern auf, wieviel muss Prosa im `--body` sein? | Auftragsbildungs-Node (7.2) |
| **M2** | Ist `complete --result` strukturierbar? Kann ein Ausgabeschema vorgegeben werden? | Verifikations-Node (7.2) |
| **M3** | Welche Felder liefert `hermes skills list` maschinenlesbar? Reicht das für einen Körperschema-Knoten? | Körperschema (8.3) |
| **M4** | Wie erfährt ein Aufrufer von `block`? Nur durch Polling, oder gibt es einen Rückkanal? | Rückfragen (7.6) |
| **M5** | Läuft lokale Ollama über den Custom-Endpoint-Pfad? Welches Tool-Calling-Verhalten zeigt `qwen36-cpu`? | Modellwahl (5.5) |
| **M6** | Queue-Tiefe und Wartezeiten an Port 11435 vor und nach Anschluss des dritten Verbrauchers. | Dauerbetrieb (5.6) |

**Reihenfolge:** M0 und M5 zuerst — beide ohne LLM-Entscheidung prüfbar
beziehungsweise Voraussetzung für alles Weitere. M1–M4 danach. M6 erst im
Dauerbetrieb.

**Wichtig:** Ein schwaches Modell lässt Hermes kaputt aussehen. Tool-Calling ist
die Disziplin, an der billige Modelle zuerst brechen — oft still, mit halb
gefüllten Argumenten statt einer Fehlermeldung. Wird M5 vor M1–M4 nicht sauber
beantwortet, misst man das Modell und nicht Hermes, und kann die beiden
hinterher nicht auseinanderhalten.

---

## 12. Offene Entscheidungen

| Nr. | Entscheidung | Abhängig von |
|-----|--------------|-------------|
| H1 | Eigenständiger HermesAgent oder Erweiterung des DelegationsAgenten | M1, M2 |
| H2 | Node-Zuschnitt und Benennung des HermesAgenten | M1, M2 |
| H3 | Tabellen und Feldnamen für Task-Referenz und Ereignis | M2 |
| H4 | Profile- oder Assignee-Trennung Nova / Pixie | M0 |
| H5 | Reichhaltigkeit eines Körperschema-Knotens; Abgleichfrequenz | M3 |
| H6 | Behandlung blockierter Tasks (Anschluss an Pending/Resume) | M4 |
| H7 | Dienstname und Compose-Einbindung | — |
| H8 | Cloud-Modell zur Erprobung: ja/nein, und wenn ja, befristet festhalten | M5 |

---

## 13. Was dieses Dokument bewusst nicht tut

- Es legt **keine** Aufrufsyntax fest. Die Beispiele aus der Hermes-Doku sind
  Belegmaterial, keine Spezifikation.
- Es benennt **keine** Tabellen, Spalten oder Funktionsnamen als beschlossen.
- Es behauptet **nicht**, dass irgendetwas davon implementiert ist. Zum
  Zeitpunkt dieses Dokuments existiert kein Zeile Code zur Hermes-Anbindung.
- Es ersetzt **kein** Audit. Für Code-Status gilt weiterhin: Audit gegen
  benannte Dateipfade.

---

## 14. Referenzen

**Novaberg-intern:**
- `novaberg-metakognition_k.md` — `pipeline_log`, SelbstreflexionsAgent, Vorsätze
- `novaberg-thinking-skills_k.md` — Epic 10, Skill-System
- `novaberg-charakter-resonanz_k.md` — `verhaltensweisen`, Nova als Subjekt
- `novaberg-pixie.md` — Heartbeat, Scheduling, Agenten-Inventar
- `novaberg-agent-fachabteilung_k.md` — Semantik-Check und Output-Validation
- `novaberg-mem-knowledge-graph.md` — Knotenmodell für das Körperschema
- `novaberg-node-gv_k.md`, `novaberg-lesson_l_quelle-vor-destillat.md`

**Hermes (extern), Stand v0.18.2 / 7. Juli 2026:**
- Dokumentation: `hermes-agent.nousresearch.com/docs`
- Repo: `github.com/NousResearch/hermes-agent` (MIT)
- Skill-Standard: `agentskills.io`

---

*Konzept erstellt 30. Juli 2026, Chat 117. Grundlage: Hermes-Dokumentation
v0.18.2 und Novaberg-Projektdokumente. Nächster Schritt: Messungen M0/M5 am
Testcontainer, danach Anbindungs-Konzept.*
