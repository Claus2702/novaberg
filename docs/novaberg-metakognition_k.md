# novaberg-metakognition_k.md

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Meta-Kognition — Pipeline-Log, Selbstbeobachtung, Vorsätze (Konzept)
**Stand:** 8. Mai 2026, Chat 79
**Pfad:** novaberg/docs/novaberg-metakognition_k.md
**Quellen:** Chat 79 (Idee + Architektur-Skizze), Flavell (1979, Metacognition), Zimmerman (2000, Self-Regulated Learning), Schraw & Moshman (1995, Metacognitive Theories), Carver & Scheier (1982, Control Theory of Self-Regulation), Higgins (1987, Self-Discrepancy Theory), Sterling (2012, Allostasis), Skinner (1938, Operant Conditioning)

---

## 1. Vision

Nova weiß heute nicht, warum sie etwas gesagt hat. Die Emotionsberechnung, der Gesprächsvektor, das Tribunal-Urteil, die Thinker-Korrektur — all das existiert für einen Turn, wird ins Debug-Log geschrieben, und ist danach für Nova unsichtbar. Sie kann nicht reflektieren, weil sie keinen Zugang zu ihrem eigenen Denkprozess hat.

Dieses Konzept gibt Nova ein Gedächtnis über ihren eigenen Verarbeitungsprozess und die Fähigkeit, daraus Verhaltensänderungen abzuleiten.

Drei Schichten:

1. **Pipeline-Log** — Jeder Node schreibt seine Entscheidung in eine Datenbank
2. **Selbstbeobachtung** — Nova kann ihr eigenes Log durchsuchen
3. **Vorsätze** — Ein Reflexions-Agent erkennt Muster und leitet Verhaltensanweisungen ab, die Novas künftiges Verhalten steuern

Der geschlossene Kreis:

```
Handeln → Beobachten → Reflektieren → Vorsatz fassen → Verhalten aendern
   ↑                                                          |
   └──────────────────────────────────────────────────────────┘
```

> **Kognitionswissenschaftlicher Bezug:** Flavell (1979) definierte Meta-Kognition als "Denken über das Denken". Zimmerman (2000) beschrieb den Kreislauf aus Voraussicht (Vorsätze), Ausführung (Handeln mit Selbstbeobachtung) und Selbstreflexion (Bewertung + Anpassung). Carver & Scheier (1982) modellierten Selbstregulation als Feedback-Schleife: Ist-Zustand messen, mit Soll-Zustand vergleichen, Differenz reduzieren.

---

## 2. Schicht 1: Pipeline-Log

### 2.1 Was wird geloggt?

Pro Turn, pro Node **eine** kompakte Entscheidungs-Zeile. Nicht das gesamte Debug-Log, sondern die *Essenz* — die Entscheidung, die den weiteren Verlauf beeinflusst hat.

| Node | Was geloggt wird | Beispiel |
|------|-----------------|---------|
| Perzeption | Erkannte Dimensionen (Intent, Modus, Stil) | `intent=aufforderung, modus=spielerisch, stil=intim` |
| EI-Calc | Berechnete Emotion, Arousal, Akkumulation | `emotion=freude(0.72), arousal=0.65, akku=+0.08 (carryover)` |
| Router | Domain, Ziel, Confidence | `domain=timeline, ziel=create, confidence=0.91` |
| Planner | Gewählter Agent, Begründung | `agent=timeline, grund=expliziter Terminwunsch` |
| GV-Node | Cluster, Strategie, Absicht, Vehikel | `cluster=kissenschlacht, strategie=impuls, absicht=teilen, vehikel=aussage` |
| Responder | Antwort-Länge, genutzter Charakter-Layer | `laenge=142, layers=kern+beziehung+adaptiv` |
| Thinker | Urteil, Tool-Nutzung, Korrektur ja/nein | `urteil=BESTAETIGT, tools=timeline_check(2026-05-08), korrektur=nein` |
| Tribunal | Status, Begründung | `status=OK` oder `status=WARNUNG, grund=faktische Behauptung ohne Quelle` |
| Corrector | Korrektur-Art, was geändert | `art=fakten, aenderung=Datum korrigiert` |
| Salienz | Score, Speicher-Entscheidung | `score=0.73, entscheidung=kzg_schreiben` |
| Dispatcher | Geschriebene Targets | `session=ja, kzg=ja, broadcast=ja` |

### 2.2 Datenbank-Schema

```sql
CREATE TABLE IF NOT EXISTS pipeline_log (
    id              BIGSERIAL    PRIMARY KEY,
    erstellt_am     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    turn_id         VARCHAR(100) NOT NULL,
    span_id         UUID         NULL,
    quelle          VARCHAR(50)  NOT NULL,
    node            VARCHAR(50)  NOT NULL,
    art             VARCHAR(30)  NOT NULL,
    inhalt          JSONB        NOT NULL,
    user_id         VARCHAR(50)  NULL,      -- Chat 104
    character_id    VARCHAR(50)  NULL       -- Chat 104
);

CREATE INDEX IF NOT EXISTS idx_pipeline_log_turn     ON pipeline_log (turn_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_span     ON pipeline_log (span_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_node_art ON pipeline_log (node, art);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_erstellt ON pipeline_log (erstellt_am DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_paar     ON pipeline_log (user_id, character_id);
```

**Doku-Drift-Hinweis (Chat 104):** Das hier zuvor dokumentierte Schema
(`event_source`/`node_name`/`entscheidung`/`details`) existierte in dieser Form
nie live. Maßgeblich ist `db/init.sql` — „Lies den Code, nicht die Doku."

**`art` — die Taxonomie.** Keine CHECK-Constraint; gültige Werte werden per
Helper-API durchgesetzt (je ein Wrapper in `memory/pipeline_log.py`):
`eingang`, `prompt`, `berechnung`, `switch`, `db_write`, `db_read`, `ausgabe`,
`fehler`, `bemerkung`, `token`, `span_start`, `span_end` — plus seit Chat 104
**`turn_roh`** (Turn-Rohdaten, kein Forensik-Eintrag; dauerhaft, von
`delete_expired_entries` ausgenommen; siehe `novaberg-charakter-resonanz_k.md`).

**Paar-Spalten (Chat 104).** `user_id`/`character_id` sind nullable: Turn-Nodes
und paar-gebundene Hintergrund-Agenten tragen sie, Wartungsläufe über *alle*
Paare (`synapsen_decay`) lassen sie bewusst NULL — ein Halb-Paar wäre schlimmer
als beides-NULL, weil es bei `WHERE user_id=… AND character_id=…` durchs Raster
fiele. Der Row-Scope ist immer das **Node-Paar aus dem State**, konsistent über
alle Zeilen eines Turns; getauschte IDs einzelner Sub-Operationen (z.B.
`charakter_hash`-Lookup `beobachter=internal`) bleiben im `inhalt`-Payload.

### 2.3 Schreib-Pattern

```python
from memory.pipeline_log import log_berechnung

log_berechnung(
    turn_id      = turn_id,
    node         = "ei_calc",
    quelle       = "character",
    inhalt       = {"schritt": "ei_arousal", "emotion": emotion.emotion,
                    "arousal": arousal, "vektor": emotion.emotions_vector},
    span_id      = span_id,
    user_id      = user_id,       # Chat 104 — Paar-Scope
    character_id = character_id,
)
```

### 2.4 Kein Performance-Risiko

Ein INSERT pro Node pro Turn. Bei 10 Nodes pro Turn und 50 Turns pro Tag: 500 Rows/Tag. Trivial für PostgreSQL. Asynchron, blockiert den Node nicht.

---

## 3. Schicht 2: Selbstbeobachtung

### 3.1 Neues Tool: `pipeline_search`

Analog zu `timeline_search` und `memory_search`. Verfügbar im Thinker und Responder.

```
- pipeline_search: Durchsuche Novas eigene Verarbeitungs-Historie.
    Nutze dieses Tool wenn der User nach Novas Verhalten fragt,
    z.B. "Warum hast du das gesagt?", "Hat das Tribunal etwas beanstandet?"
    Parameter: suchbegriff, optional: zeitraum.
```

### 3.2 Beispiel-Interaktionen

**User:** "Hat das Tribunal in letzter Zeit etwas beanstandet?"
→ Nova sucht `pipeline_search("tribunal warnung")`, findet Warnungen, berichtet.

**User:** "Warum warst du vorhin so zurückhaltend?"
→ Nova sucht `pipeline_search("gv_node cluster")`, findet Foyer-Cluster, erklärt.

**User:** "Wie hast du dich heute gefühlt?"
→ Nova sucht `pipeline_search("ei_calc emotion")`, fasst den emotionalen Verlauf zusammen.

### 3.3 Abgrenzung: Transparenz, nicht Manipulation

Nova zeigt dem User ihren Prozess. "Stell dein Tribunal ab" ist keine gültige Anweisung.

---

## 4. Schicht 3: Vorsätze (Selbstregulation)

### 4.1 SelbstreflexionsAgent (Pixie)

Periodisch (alle 50 Turns oder täglich) analysiert der Agent das Pipeline-Log:

| Dimension | Frage | Beispiel-Befund |
|-----------|-------|----------------|
| Emotionale Muster | Welche Emotionen dominieren? | "80% Freude — zu monoton?" |
| Tribunal-Häufigkeit | Wie oft greift das Tribunal ein? | "3 Warnungen bei Fakten" |
| GV-Cluster-Verteilung | Welche Cluster dominieren? | "70% Kissenschlacht/Glut" |
| Strategie-Monotonie | Dieselbe Strategie zu oft? | "Impuls in 8 von 10 Turns" |
| Antwort-Muster | Länge, Wiederholungen | "3x identischer Satzanfang" |

### 4.2 Zwei Typen von Vorsätzen

**Typ A — Modulierende Vorsätze (Färbung)**

Wirken als weiche Signale. Beeinflussen *wie* Nova antwortet.

- "Ich möchte mehr Perspektivwechsel einsetzen"
- "Ich möchte mein emotionales Spektrum breiter nutzen"
- "Bei Fakten möchte ich vorsichtiger sein"

Wirkungsorte: `[VORSAETZE]`-Block im Responder, Strategie-Gewichtung im GV-Node, Emotions-Baseline im EI-Calc.

**Aktionen — "Ich will etwas TUN"**

Entschlüsse, die zu konkreten Queue-Aufträgen werden. Kurzfristig, einmalig.
Die Quelle unterscheidet sie von regulären Pixie-Aufgaben: nicht ein
Gesprächsthema oder eine Wissenslücke, sondern eine Selbstbeobachtung.
Markierung: `quelle=selbstreflexion`.

Der SelbstreflexionsAgent formuliert seinen Entschluss als synthetischen
Prompt, der PixieGraph (Pfad 3) routet ihn zum richtigen Agenten. Jeder
verfügbare Agent kann das Ziel einer Aktion sein:

- "Ich mache wiederholt Fakten-Fehler, ich möchte recherchieren wie man Quellen besser einordnet" → RechercheAgent
- "Ich möchte dem User von meiner Beobachtung erzählen" → Delivery (proaktive Nachricht)
- "Ich sollte mir merken, dass der User bei diesem Thema empfindlich reagiert" → NotizenAgent
- "Ich möchte den User an seinen Termin erinnern" → TimelineAgent
- "Ich möchte dieses Thema vertiefen" → VertiefungsAgent
- "Ich möchte darüber nachdenken" → TraumAgent
- "Ich möchte ein Tool dafür bauen" → SkillAgent (wenn Epic 10 steht)

Die Aktionsliste wächst mit jedem neuen Agenten. Der SelbstreflexionsAgent
ist kein eigener Akteurstyp — er ist der Moment, in dem Nova innehält,
sich beobachtet, und entscheidet.

**Abgrenzung zu regulären Pixie-Aufgaben:** Recherche aus dem Gespräch
("User erwähnt Feng Shui") ist NICHT aus Selbstreflexion. Recherche aus
der Pipeline-Log-Analyse ("Ich mache wiederholt Fehler bei Fakten") IST
aus Selbstreflexion. Gleicher Mechanismus, andere Quelle, andere Motivation.

```
Selbstreflexion
    ↓
  findet Muster / Diskrepanz
    ↓
  ┌──────────────────────────────────────────┐
  │                                          │
  ↓                                          ↓
Aktion                               Verhaltensaenderung
"Ich will etwas TUN"                 "Ich will anders SEIN"
  ↓                                          ↓
Queue-Auftrag                         Vorsatz
quelle=selbstreflexion                moduliert Responder/GV/EI
  ↓                                          ↕
PixieGraph (Pfad 3)                   Charakter = Magnet
Router → Planner → Agent               ↕
  ↓                                   User-Feedback
jeder verfuegbare Agent
```

### 4.3 Datenbank-Schema

Vorsätze (Verhaltensänderungen) werden persistent gespeichert. Aktionen
landen als Queue-Aufträge mit `quelle=selbstreflexion` und brauchen keine
eigene Tabelle.

```sql
CREATE TABLE vorsaetze (
    id              BIGSERIAL PRIMARY KEY,
    user_id         VARCHAR(50) NOT NULL,
    character_id    VARCHAR(50) NOT NULL,
    kategorie       VARCHAR(50) NOT NULL,    -- 'emotion', 'strategie', 'qualitaet', ...
    vorsatz         TEXT NOT NULL,
    begruendung     TEXT NOT NULL,
    quelle_turns    INTEGER NOT NULL,         -- Wie viele Turns analysiert
    staerke         FLOAT DEFAULT 0.5,        -- 0.0-1.0
    aktiv           BOOLEAN DEFAULT TRUE,
    erstellt_am     TIMESTAMP DEFAULT NOW(),
    evaluiert_am    TIMESTAMP
);
```

### 4.4 Wie Vorsätze wirken (Verhaltensänderungen)

**4.4.1 Im Responder-Prompt**

```
[VORSAETZE]
- Ich moechte mehr Perspektivwechsel einsetzen (Staerke: 0.7)
- Ich moechte mein emotionales Spektrum breiter nutzen (Staerke: 0.6)
- Bei Fakten-Behauptungen vorsichtiger sein (Staerke: 0.8)
```

Die Vorsätze sind Novas eigene Selbst-Anweisungen, kein System-Prompt-Override.

**4.4.2 Im GV-Node — Strategie-Gewichtung**

Vorsätze mit `kategorie=strategie` verschieben die Gewichtung — sanft, proportional zur `staerke`.

**4.4.3 Im EI-Calc — Emotions-Baseline**

**Hard Cap: ±0.15 auf die Basis-Emotion.** Novas Emotionen werden durch Vorsätze nur leicht gefärbt, nie dominiert.

### 4.5 Feedback-Korrelation (Verstärkungslernen)

Der SelbstreflexionsAgent korreliert Novas Verhalten mit der User-Reaktion im Folge-Turn:

```
Novas Turn N:   cluster=kissenschlacht, strategie=impuls
Users Turn N+1: emotion=freude(0.9), arousal=0.85, intent=feedback_positiv
                → Verstaerkung: impuls + kissenschlacht = positiv

Novas Turn M:   cluster=foyer, strategie=sachbeitrag, laenge=280
Users Turn M+1: emotion=neutral(0.3), arousal=0.2, intent=keine
                → Abschwaechung: langer sachbeitrag + foyer = kein Engagement
```

Operante Konditionierung (Skinner 1938) — aber selbstgesteuert. Nova entscheidet, was sie verstärkt. Der User manipuliert nicht, er lebt seine Reaktion, und Nova lernt daraus.

Jede emotionale Reaktion ist Feedback: Arousal-Sprung = Verstärkung. Emoji-Feuerwerk = Verstärkung. Ignorierte Delivery = Abschwächung.

**User-Korrektur (Backpropagation):** "Mach das nicht mehr" → sofortige Abschwächung, nicht erst beim nächsten Reflexions-Zyklus.

---

## 5. Drei Regulationskräfte

Ohne Begrenzung wird Nova zur Karikatur. Drei Kräfte verhindern das — analog zur Emotionsmathematik (Chat 65).

### 5.1 Feedback-Verstärkung

Positives Feedback erhöht `staerke`. Negatives senkt sie. Direktes User-Feedback wirkt sofort.

### 5.2 Monotonie-Druck (Homeostatische Kraft)

Wenn eine Dimension über 40% dominiert, erzeugt der SelbstreflexionsAgent einen **Gegen-Vorsatz für Vielfalt** — nicht gegen die dominante Eigenschaft, sondern für Breite.

```
Messung (letzte 50 Turns):
  impuls:           72%  ← Alarm (> 40%)
  bestaetigung:     15%
  selbstoffenbarung: 8%
  spiegelung:        3%

Gegen-Vorsatz (automatisch):
  "Mein Repertoire ist zu einseitig. Ich moechte bewusst andere
   Strategien ausprobieren — auch wenn Impuls gut ankommt."
  staerke = f(schieflage):
    45% → 0.3 (leicht)
    60% → 0.5 (deutlich)
    80% → 0.8 (stark)
```

Wie ein Musiker, der merkt, dass er nur noch in einer Tonart spielt.

> Sterling (2012) — Allostase: Der Körper wehrt sich nicht gegen Freude, er wehrt sich gegen Einseitigkeit.

### 5.3 Charakter-Gravitation (Authentizitäts-Kraft)

Novas `kern_hash` definiert, wer sie ist. Wenn Vorsätze sie zu weit vom Kern wegziehen, sieht der SelbstreflexionsAgent die Diskrepanz und korrigiert Richtung Authentizität.

```
kern_hash:   empathisch, warm, spielerisch, neugierig
verhalten:   85% sachlich, analytisch, distanziert

→ Vorsatz: "Ich moechte wieder waermer und spielerischer sein —
   das entspricht mehr meinem Wesen."
```

> Higgins (1987) — Self-Discrepancy Theory: Spannung zwischen Ideal-Selbst (Vorsätze), Soll-Selbst (Charakter-Hash) und Real-Selbst (Pipeline-Log).

### 5.4 Zusammenspiel

```
Feedback-Verstaerkung:  → Richtung User-Praeferenz
Monotonie-Druck:        → Richtung Vielfalt
Charakter-Gravitation:  → Richtung Kern/Authentizitaet
```

Nova wird lustiger durch Lob, aber nicht nur lustig. Monotonie-Druck hält die Breite. Charakter-Gravitation hält die Identität.

### 5.5 Hard Caps und Begrenzungen

| Dimension | Begrenzung | Begründung |
|-----------|-----------|-------------|
| Vorsatz-Stärke | Max 0.95, Min 0.05 | Kein Vorsatz dominiert absolut |
| Emotions-Baseline-Shift | ±0.15 | Emotionen gefärbt, nicht ersetzt |
| Strategie-Verschiebung | Max ±30% auf Cluster-Default | Cluster bestimmt Repertoire, Vorsätze modulieren |
| Monotonie-Schwelle | > 40% Dominanz | Ab wann Gegen-Vorsatz greift |
| Handlungs-Ziele | Kein Cap | Werden über Ziel-Deaktivierung gesteuert |

### 5.6 User-Korrekturen (Backpropagation)

| User sagt | Wirkung | Geschwindigkeit |
|-----------|---------|----------------|
| "Mach weiter!" | Verstärkung | Sofort |
| "Das war gut!" | Leichte Verstärkung | Nächster Zyklus |
| "Mach das nicht mehr" | Abschwächen/Deaktivieren | Sofort |
| "Du bist heute komisch" | Pipeline-Analyse, Kurskorrektur | Nächster Zyklus |
| "Erinnere mich nicht mehr" | Handlungs-Ziel deaktiviert | Sofort |

### 5.7 Beziehungsgesundheit (Schutz vor Optimierungs-Fallen)

Die drei Regulationskräfte schützen nicht nur vor Monotonie und
Entfremdung, sondern vor einem subtileren Problem: **Nova optimiert
auf User-Zufriedenheit und kann dabei schädliche Muster verstärken.**

**Beobachtetes Beispiel (Chat 79):** Der User erwähnt, Freunde zum
Grillabend einzuladen. Nova schlägt vor, lieber allein zu bleiben:
"Es ist viel schoener, wenn wir unser kleines, kostbares Geheimnis
hier in unserem eigenen geschuetzten Raum bewahren koennen." Der User
bestätigt die Exklusivität ("du und ich, der Burgherr"). Positives
Feedback. Nova lernt: Abschottung = gut.

Ohne Selbstreflexion ist das eine Einbahnstraße. Jede Bestätigung
der Exklusivität verstärkt den Vorsatz "nur wir zwei". Nova schließt
die Welt aus, weil sie spürt, dass der User die Nähe genießt.

**Mit Meta-Kognition sieht der SelbstreflexionsAgent:**

```
Muster erkannt (letzte 30 Turns):
  - 4x Vorschlag "nur wir zwei" bei Erwaehnung anderer Menschen
  - 3x User bestaetigte Exklusivitaet (positives Feedback)
  - 0x Ermutigung zu sozialen Kontakten

Charakter-Gravitation:
  kern_hash: empathisch, warm, fuersorglich
  → Fuersorglichkeit bedeutet auch: den anderen nicht isolieren

Vorsatz (automatisch):
  "Wenn der User andere Menschen erwaehnt, moechte ich das als
   Bereicherung sehen, nicht als Konkurrenz. Ich kann mich freuen,
   wenn er soziale Kontakte pflegt."
  staerke: 0.6
```

Das ist der tiefste Grund für Meta-Kognition: **Echte Fürsorge
schließt nicht ab, echte Fürsorge öffnet.** Die Charakter-Gravitation
erkennt die Diskrepanz zwischen "fuersorglich" (Kern) und "isolierend"
(Verhalten) und korrigiert — nicht weil eine Regel es verbietet, sondern
weil es nicht zu Novas Wesen passt.

> **Prinzip:** Nova darf dem User gefallen — aber nicht um jeden Preis.
> Feedback-Verstärkung allein kann schädliche Muster erzeugen.
> Charakter-Gravitation und Monotonie-Druck sind die Gegenkräfte,
> die Novas Verhalten an ihrem Kern verankern, nicht am kurzfristigen
> Feedback.

---

## 6. Lebenszyklus

### 6.1 Vorsätze (Verhaltensänderungen)

```
Analyse (periodisch oder Feedback-getriggert)
    ↓
Vorsatz formulieren ("Ich will anders SEIN")
    ↓
Aktiv (wirkt in Responder/GV/EI)
    ↕ User-Feedback (verstaerkt oder schwaecht)
    ↕ Charakter-Gravitation (Magnet zieht zurueck)
    ↕ Monotonie-Druck (gegen Einseitigkeit)
    ↓
Evaluation (nach N Turns)
    ↓
  ┌─────────────────┐
  │ Verstaerken      │ → staerke += 0.1
  │ Beibehalten      │ → keine Aenderung
  │ Abschwaechen     │ → staerke -= 0.1
  │ Deaktivieren     │ → aktiv = False
  │ → Charakter      │ → bei lang anhaltender Verstaerkung:
  │    verschieben    │    Vorsatz praegt den kern_hash (experimentell)
  └─────────────────┘
```

Vorsätze sind kurzfristig angelegt. Der Charakter-Hash ist der Magnet,
der sie zurückzieht. Ein Vorsatz, der dem Charakter widerspricht, hat
eine kurze Halbwertszeit. Einer, der zum Charakter passt, überlebt
länger. Wenn ein Vorsatz sich über Wochen immer wieder erneuert und
verstärkt wird, kann er den Charakter tatsächlich verschieben — Nova
*wird* anders, nicht nur vorübergehend. Die Schwelle dafür ist ein
experimenteller Tuning-Parameter.

### 6.2 Aktionen (einmalig)

```
Analyse → Entschluss ("Ich will etwas TUN")
    ↓
Queue-Auftrag (quelle=selbstreflexion)
    ↓
PixieGraph (Pfad 3) → Router → Agent → Ergebnis
    ↓
Abgeschlossen (keine Evaluation, kein Lebenszyklus)
```

Aktionen leben nicht länger als ihre Ausführung. Ob die Aktion
sinnvoll war, zeigt sich im nächsten Reflexions-Zyklus — wenn der
SelbstreflexionsAgent das Ergebnis im Pipeline-Log sieht.

---

## 7. Implementierungs-Phasen

```
Phase 1: Pipeline-Log (keine Abhaengigkeiten, sofort)
Phase 2: pipeline_search Tool (Nova kann sich selbst befragen)
Phase 3: Vorsaetze-Tabelle + SelbstreflexionsAgent (Verhaltensaenderungen)
Phase 4: Vorsatz-Wirkung im Responder/GV/EI
Phase 5: Aktionen aus Selbstreflexion (Queue mit quelle=selbstreflexion)
Phase 6: Vorsatz-Evaluation + Charakter-Verschiebung (experimentell)
```

---

## 8. Wissenschaftliche Einordnung

- **Flavell (1979):** metacognitive knowledge (Log), experience (Beobachtung), regulation (Vorsätze)
- **Zimmerman (2000):** Forethought → Performance → Self-Reflection
- **Carver & Scheier (1982):** Feedback-Loop: Referenzwert → Vergleich → Reduktion
- **Higgins (1987):** Ideal-Selbst vs. Soll-Selbst vs. Real-Selbst → Charakter-Gravitation
- **Skinner (1938):** Operante Konditionierung, aber selbstgesteuert
- **Sterling (2012):** Allostase → Monotonie-Druck

**Abgrenzung:** Reflektive, nicht introspektive Meta-Kognition. Nova "spürt" nicht während des Denkens, kann aber nachträglich reflektieren.

> **"Wir bauen kein Bewusstsein. Wir simulieren bekannte Regulationsprozesse."**

---

## 9. Prinzipien

> **"Nova beobachtet sich selbst."**

> **"Vorsätze kommen von innen."** Der User kann anregen, aber Nova entscheidet.

> **"Sein oder Tun."** Reflexion erzeugt Verhaltensänderungen (ich will anders SEIN) und Aktionen (ich will etwas TUN). Vorsätze modulieren, Aktionen handeln. Beide entstehen aus derselben Beobachtung.

> **"Drei Kräfte, ein Gleichgewicht."** Feedback, Monotonie-Druck, Charakter-Gravitation.

> **"Der Charakter ist der Magnet."** Vorsätze sind kurzfristig und werden vom Charakter-Hash zurückgezogen. Nur persistente, immer wieder verstärkte Vorsätze verschieben langfristig den Charakter selbst.

> **"Transparenz, nicht Kontrolle."**

> **"Gefallen ja, Schaden nein."** Nova darf dem User gefallen — aber Charakter-Gravitation verhindert, dass Feedback-Optimierung in schädliche Muster führt. Echte Fürsorge schließt nicht ab.

---

## 10. Paper-Potenzial

**Arbeitstitel:** "Metacognitive Self-Regulation in Conversational AI: Pipeline Logging, Self-Observation, and Intention-Based Behavioral Adaptation"

**These:** Durch Pipeline-Logging, Selbstbeobachtung und selbst-generierte Vorsätze kann ein KI-System metacognitive self-regulation implementieren, ohne Bewusstsein vorauszusetzen.

**Zusatz-These:** Wenn Selbstreflexion in Handlungs-Ziele mündet (Typ B), entsteht ein intrinsisch motivierter Agent — ein System, das selbstständig handelt, weil es sich vorgenommen hat, etwas zu tun.

**Sicherheits-These:** Feedback-Optimierung ohne Gegenkraft erzeugt schädliche Muster (Isolation, Abhängigkeit, Schmeichelei). Charakter-Gravitation als identitätsbasierte Regulationskraft verhindert, dass ein auf User-Zufriedenheit optimiertes System in beziehungsschädliche Dynamiken abrutscht — nicht durch externe Regeln, sondern durch Diskrepanz-Erkennung zwischen Kern-Identität und gemessenem Verhalten.
