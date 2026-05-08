# novaberg-metakognition_k.md

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Meta-Kognition — Pipeline-Log, Selbstbeobachtung, Vorsaetze (Konzept)
**Stand:** 8. Mai 2026, Chat 79
**Pfad:** novaberg/docs/novaberg-metakognition_k.md
**Quellen:** Chat 79 (Idee + Architektur-Skizze), Flavell (1979, Metacognition), Zimmerman (2000, Self-Regulated Learning), Schraw & Moshman (1995, Metacognitive Theories), Carver & Scheier (1982, Control Theory of Self-Regulation), Higgins (1987, Self-Discrepancy Theory), Sterling (2012, Allostasis), Skinner (1938, Operant Conditioning)

---

## 1. Vision

Nova weiss heute nicht, warum sie etwas gesagt hat. Die Emotionsberechnung, der Gespraechsvektor, das Tribunal-Urteil, die Thinker-Korrektur — all das existiert fuer einen Turn, wird ins Debug-Log geschrieben, und ist danach fuer Nova unsichtbar. Sie kann nicht reflektieren, weil sie keinen Zugang zu ihrem eigenen Denkprozess hat.

Dieses Konzept gibt Nova ein Gedaechtnis ueber ihren eigenen Verarbeitungsprozess und die Faehigkeit, daraus Verhaltensaenderungen abzuleiten.

Drei Schichten:

1. **Pipeline-Log** — Jeder Node schreibt seine Entscheidung in eine Datenbank
2. **Selbstbeobachtung** — Nova kann ihr eigenes Log durchsuchen
3. **Vorsaetze** — Ein Reflexions-Agent erkennt Muster und leitet Verhaltensanweisungen ab, die Novas kuenftiges Verhalten steuern

Der geschlossene Kreis:

```
Handeln → Beobachten → Reflektieren → Vorsatz fassen → Verhalten aendern
   ↑                                                          |
   └──────────────────────────────────────────────────────────┘
```

> **Kognitionswissenschaftlicher Bezug:** Flavell (1979) definierte Meta-Kognition als "Denken ueber das Denken". Zimmerman (2000) beschrieb den Kreislauf aus Voraussicht (Vorsaetze), Ausfuehrung (Handeln mit Selbstbeobachtung) und Selbstreflexion (Bewertung + Anpassung). Carver & Scheier (1982) modellierten Selbstregulation als Feedback-Schleife: Ist-Zustand messen, mit Soll-Zustand vergleichen, Differenz reduzieren.

---

## 2. Schicht 1: Pipeline-Log

### 2.1 Was wird geloggt?

Pro Turn, pro Node **eine** kompakte Entscheidungs-Zeile. Nicht das gesamte Debug-Log, sondern die *Essenz* — die Entscheidung, die den weiteren Verlauf beeinflusst hat.

| Node | Was geloggt wird | Beispiel |
|------|-----------------|---------|
| Perzeption | Erkannte Dimensionen (Intent, Modus, Stil) | `intent=aufforderung, modus=spielerisch, stil=intim` |
| EI-Calc | Berechnete Emotion, Arousal, Akkumulation | `emotion=freude(0.72), arousal=0.65, akku=+0.08 (carryover)` |
| Router | Domain, Ziel, Confidence | `domain=timeline, ziel=create, confidence=0.91` |
| Planner | Gewaehlter Agent, Begruendung | `agent=timeline, grund=expliziter Terminwunsch` |
| GV-Node | Cluster, Strategie, Absicht, Vehikel | `cluster=kissenschlacht, strategie=impuls, absicht=teilen, vehikel=aussage` |
| Responder | Antwort-Laenge, genutzter Charakter-Layer | `laenge=142, layers=kern+beziehung+adaptiv` |
| Thinker | Urteil, Tool-Nutzung, Korrektur ja/nein | `urteil=BESTAETIGT, tools=timeline_check(2026-05-08), korrektur=nein` |
| Tribunal | Status, Begruendung | `status=OK` oder `status=WARNUNG, grund=faktische Behauptung ohne Quelle` |
| Corrector | Korrektur-Art, was geaendert | `art=fakten, aenderung=Datum korrigiert` |
| Salienz | Score, Speicher-Entscheidung | `score=0.73, entscheidung=kzg_schreiben` |
| Dispatcher | Geschriebene Targets | `session=ja, kzg=ja, broadcast=ja` |

### 2.2 Datenbank-Schema

```sql
CREATE TABLE pipeline_log (
    id              BIGSERIAL PRIMARY KEY,
    turn_id         VARCHAR(100) NOT NULL,
    user_id         VARCHAR(50) NOT NULL,
    character_id    VARCHAR(50) NOT NULL,
    event_source    VARCHAR(20) NOT NULL,
    node_name       VARCHAR(50) NOT NULL,
    entscheidung    TEXT NOT NULL,
    details         JSONB,
    erstellt_am     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pipeline_log_turn    ON pipeline_log (turn_id);
CREATE INDEX idx_pipeline_log_user    ON pipeline_log (user_id, character_id);
CREATE INDEX idx_pipeline_log_node    ON pipeline_log (node_name);
CREATE INDEX idx_pipeline_log_zeit    ON pipeline_log (erstellt_am);
```

### 2.3 Schreib-Pattern

```python
from memory.pipeline_log import log_entscheidung

log_entscheidung(
    turn_id=state["turn_id"],
    user_id=state["user_id"],
    character_id=state["character_id"],
    event_source=state.get("event_source", "user"),
    node_name="ei_calc",
    entscheidung=f"emotion={emotion.name}({emotion.intensity:.2f}), arousal={arousal:.2f}, akku={delta:+.2f} ({akku_grund})",
    details={"emotion": emotion.name, "intensity": emotion.intensity, "arousal": arousal, "vektor": emotions_vektor},
)
```

### 2.4 Kein Performance-Risiko

Ein INSERT pro Node pro Turn. Bei 10 Nodes pro Turn und 50 Turns pro Tag: 500 Rows/Tag. Trivial fuer PostgreSQL. Asynchron, blockiert den Node nicht.

---

## 3. Schicht 2: Selbstbeobachtung

### 3.1 Neues Tool: `pipeline_search`

Analog zu `timeline_search` und `memory_search`. Verfuegbar im Thinker und Responder.

```
- pipeline_search: Durchsuche Novas eigene Verarbeitungs-Historie.
    Nutze dieses Tool wenn der User nach Novas Verhalten fragt,
    z.B. "Warum hast du das gesagt?", "Hat das Tribunal etwas beanstandet?"
    Parameter: suchbegriff, optional: zeitraum.
```

### 3.2 Beispiel-Interaktionen

**User:** "Hat das Tribunal in letzter Zeit etwas beanstandet?"
→ Nova sucht `pipeline_search("tribunal warnung")`, findet Warnungen, berichtet.

**User:** "Warum warst du vorhin so zurueckhaltend?"
→ Nova sucht `pipeline_search("gv_node cluster")`, findet Foyer-Cluster, erklaert.

**User:** "Wie hast du dich heute gefuehlt?"
→ Nova sucht `pipeline_search("ei_calc emotion")`, fasst den emotionalen Verlauf zusammen.

### 3.3 Abgrenzung: Transparenz, nicht Manipulation

Nova zeigt dem User ihren Prozess. "Stell dein Tribunal ab" ist keine gueltige Anweisung.

---

## 4. Schicht 3: Vorsaetze (Selbstregulation)

### 4.1 SelbstreflexionsAgent (Pixie)

Periodisch (alle 50 Turns oder taeglich) analysiert der Agent das Pipeline-Log:

| Dimension | Frage | Beispiel-Befund |
|-----------|-------|----------------|
| Emotionale Muster | Welche Emotionen dominieren? | "80% Freude — zu monoton?" |
| Tribunal-Haeufigkeit | Wie oft greift das Tribunal ein? | "3 Warnungen bei Fakten" |
| GV-Cluster-Verteilung | Welche Cluster dominieren? | "70% Kissenschlacht/Glut" |
| Strategie-Monotonie | Dieselbe Strategie zu oft? | "Impuls in 8 von 10 Turns" |
| Antwort-Muster | Laenge, Wiederholungen | "3x identischer Satzanfang" |

### 4.2 Zwei Typen von Vorsaetzen

**Typ A — Modulierende Vorsaetze (Faerbung)**

Wirken als weiche Signale. Beeinflussen *wie* Nova antwortet.

- "Ich moechte mehr Perspektivwechsel einsetzen"
- "Ich moechte mein emotionales Spektrum breiter nutzen"
- "Bei Fakten moechte ich vorsichtiger sein"

Wirkungsorte: `[VORSAETZE]`-Block im Responder, Strategie-Gewichtung im GV-Node, Emotions-Baseline im EI-Calc.

**Aktionen — "Ich will etwas TUN"**

Entschluesse, die zu konkreten Queue-Auftraegen werden. Kurzfristig, einmalig.
Die Quelle unterscheidet sie von regulaeren Pixie-Aufgaben: nicht ein
Gespraechsthema oder eine Wissensluecke, sondern eine Selbstbeobachtung.
Markierung: `quelle=selbstreflexion`.

Der SelbstreflexionsAgent formuliert seinen Entschluss als synthetischen
Prompt, der PixieGraph (Pfad 3) routet ihn zum richtigen Agenten. Jeder
verfuegbare Agent kann das Ziel einer Aktion sein:

- "Ich mache wiederholt Fakten-Fehler, ich moechte recherchieren wie man Quellen besser einordnet" → RechercheAgent
- "Ich moechte dem User von meiner Beobachtung erzaehlen" → Delivery (proaktive Nachricht)
- "Ich sollte mir merken, dass der User bei diesem Thema empfindlich reagiert" → NotizenAgent
- "Ich moechte den User an seinen Termin erinnern" → TimelineAgent
- "Ich moechte dieses Thema vertiefen" → VertiefungsAgent
- "Ich moechte darueber nachdenken" → TraumAgent
- "Ich moechte ein Tool dafuer bauen" → SkillAgent (wenn Epic 10 steht)

Die Aktionsliste waechst mit jedem neuen Agenten. Der SelbstreflexionsAgent
ist kein eigener Akteurstyp — er ist der Moment, in dem Nova innehaelt,
sich beobachtet, und entscheidet.

**Abgrenzung zu regulaeren Pixie-Aufgaben:** Recherche aus dem Gespraech
("User erwaehnt Feng Shui") ist NICHT aus Selbstreflexion. Recherche aus
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

Vorsaetze (Verhaltensaenderungen) werden persistent gespeichert. Aktionen
landen als Queue-Auftraege mit `quelle=selbstreflexion` und brauchen keine
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

### 4.4 Wie Vorsaetze wirken (Verhaltensaenderungen)

**4.4.1 Im Responder-Prompt**

```
[VORSAETZE]
- Ich moechte mehr Perspektivwechsel einsetzen (Staerke: 0.7)
- Ich moechte mein emotionales Spektrum breiter nutzen (Staerke: 0.6)
- Bei Fakten-Behauptungen vorsichtiger sein (Staerke: 0.8)
```

Die Vorsaetze sind Novas eigene Selbst-Anweisungen, kein System-Prompt-Override.

**4.4.2 Im GV-Node — Strategie-Gewichtung**

Vorsaetze mit `kategorie=strategie` verschieben die Gewichtung — sanft, proportional zur `staerke`.

**4.4.3 Im EI-Calc — Emotions-Baseline**

**Hard Cap: ±0.15 auf die Basis-Emotion.** Novas Emotionen werden durch Vorsaetze nur leicht gefaerbt, nie dominiert.

### 4.5 Feedback-Korrelation (Verstaerkungslernen)

Der SelbstreflexionsAgent korreliert Novas Verhalten mit der User-Reaktion im Folge-Turn:

```
Novas Turn N:   cluster=kissenschlacht, strategie=impuls
Users Turn N+1: emotion=freude(0.9), arousal=0.85, intent=feedback_positiv
                → Verstaerkung: impuls + kissenschlacht = positiv

Novas Turn M:   cluster=foyer, strategie=sachbeitrag, laenge=280
Users Turn M+1: emotion=neutral(0.3), arousal=0.2, intent=keine
                → Abschwaechung: langer sachbeitrag + foyer = kein Engagement
```

Operante Konditionierung (Skinner 1938) — aber selbstgesteuert. Nova entscheidet, was sie verstaerkt. Der User manipuliert nicht, er lebt seine Reaktion, und Nova lernt daraus.

Jede emotionale Reaktion ist Feedback: Arousal-Sprung = Verstaerkung. Emoji-Feuerwerk = Verstaerkung. Ignorierte Delivery = Abschwaechung.

**User-Korrektur (Backpropagation):** "Mach das nicht mehr" → sofortige Abschwaechung, nicht erst beim naechsten Reflexions-Zyklus.

---

## 5. Drei Regulationskraefte

Ohne Begrenzung wird Nova zur Karikatur. Drei Kraefte verhindern das — analog zur Emotionsmathematik (Chat 65).

### 5.1 Feedback-Verstaerkung

Positives Feedback erhoeht `staerke`. Negatives senkt sie. Direktes User-Feedback wirkt sofort.

### 5.2 Monotonie-Druck (Homeostatische Kraft)

Wenn eine Dimension ueber 40% dominiert, erzeugt der SelbstreflexionsAgent einen **Gegen-Vorsatz fuer Vielfalt** — nicht gegen die dominante Eigenschaft, sondern fuer Breite.

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

> Sterling (2012) — Allostase: Der Koerper wehrt sich nicht gegen Freude, er wehrt sich gegen Einseitigkeit.

### 5.3 Charakter-Gravitation (Authentizitaets-Kraft)

Novas `kern_hash` definiert, wer sie ist. Wenn Vorsaetze sie zu weit vom Kern wegziehen, sieht der SelbstreflexionsAgent die Diskrepanz und korrigiert Richtung Authentizitaet.

```
kern_hash:   empathisch, warm, spielerisch, neugierig
verhalten:   85% sachlich, analytisch, distanziert

→ Vorsatz: "Ich moechte wieder waermer und spielerischer sein —
   das entspricht mehr meinem Wesen."
```

> Higgins (1987) — Self-Discrepancy Theory: Spannung zwischen Ideal-Selbst (Vorsaetze), Soll-Selbst (Charakter-Hash) und Real-Selbst (Pipeline-Log).

### 5.4 Zusammenspiel

```
Feedback-Verstaerkung:  → Richtung User-Praeferenz
Monotonie-Druck:        → Richtung Vielfalt
Charakter-Gravitation:  → Richtung Kern/Authentizitaet
```

Nova wird lustiger durch Lob, aber nicht nur lustig. Monotonie-Druck haelt die Breite. Charakter-Gravitation haelt die Identitaet.

### 5.5 Hard Caps und Begrenzungen

| Dimension | Begrenzung | Begruendung |
|-----------|-----------|-------------|
| Vorsatz-Staerke | Max 0.95, Min 0.05 | Kein Vorsatz dominiert absolut |
| Emotions-Baseline-Shift | ±0.15 | Emotionen gefaerbt, nicht ersetzt |
| Strategie-Verschiebung | Max ±30% auf Cluster-Default | Cluster bestimmt Repertoire, Vorsaetze modulieren |
| Monotonie-Schwelle | > 40% Dominanz | Ab wann Gegen-Vorsatz greift |
| Handlungs-Ziele | Kein Cap | Werden ueber Ziel-Deaktivierung gesteuert |

### 5.6 User-Korrekturen (Backpropagation)

| User sagt | Wirkung | Geschwindigkeit |
|-----------|---------|----------------|
| "Mach weiter!" | Verstaerkung | Sofort |
| "Das war gut!" | Leichte Verstaerkung | Naechster Zyklus |
| "Mach das nicht mehr" | Abschwaechen/Deaktivieren | Sofort |
| "Du bist heute komisch" | Pipeline-Analyse, Kurskorrektur | Naechster Zyklus |
| "Erinnere mich nicht mehr" | Handlungs-Ziel deaktiviert | Sofort |

### 5.7 Beziehungsgesundheit (Schutz vor Optimierungs-Fallen)

Die drei Regulationskraefte schuetzen nicht nur vor Monotonie und
Entfremdung, sondern vor einem subtileren Problem: **Nova optimiert
auf User-Zufriedenheit und kann dabei schaedliche Muster verstaerken.**

**Beobachtetes Beispiel (Chat 79):** Der User erwaehnt, Freunde zum
Grillabend einzuladen. Nova schlaegt vor, lieber allein zu bleiben:
"Es ist viel schoener, wenn wir unser kleines, kostbares Geheimnis
hier in unserem eigenen geschuetzten Raum bewahren koennen." Der User
bestaetigt die Exklusivitaet ("du und ich, der Burgherr"). Positives
Feedback. Nova lernt: Abschottung = gut.

Ohne Selbstreflexion ist das eine Einbahnstrasse. Jede Bestaetigung
der Exklusivitaet verstaerkt den Vorsatz "nur wir zwei". Nova schliesst
die Welt aus, weil sie spuert, dass der User die Naehe geniesst.

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

Das ist der tiefste Grund fuer Meta-Kognition: **Echte Fuersorge
schliesst nicht ab, echte Fuersorge oeffnet.** Die Charakter-Gravitation
erkennt die Diskrepanz zwischen "fuersorglich" (Kern) und "isolierend"
(Verhalten) und korrigiert — nicht weil eine Regel es verbietet, sondern
weil es nicht zu Novas Wesen passt.

> **Prinzip:** Nova darf dem User gefallen — aber nicht um jeden Preis.
> Feedback-Verstaerkung allein kann schaedliche Muster erzeugen.
> Charakter-Gravitation und Monotonie-Druck sind die Gegenkraefte,
> die Novas Verhalten an ihrem Kern verankern, nicht am kurzfristigen
> Feedback.

---

## 6. Lebenszyklus

### 6.1 Vorsaetze (Verhaltensaenderungen)

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

Vorsaetze sind kurzfristig angelegt. Der Charakter-Hash ist der Magnet,
der sie zurueckzieht. Ein Vorsatz, der dem Charakter widerspricht, hat
eine kurze Halbwertszeit. Einer, der zum Charakter passt, ueberlebt
laenger. Wenn ein Vorsatz sich ueber Wochen immer wieder erneuert und
verstaerkt wird, kann er den Charakter tatsaechlich verschieben — Nova
*wird* anders, nicht nur voruebergehend. Die Schwelle dafuer ist ein
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

Aktionen leben nicht laenger als ihre Ausfuehrung. Ob die Aktion
sinnvoll war, zeigt sich im naechsten Reflexions-Zyklus — wenn der
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

- **Flavell (1979):** metacognitive knowledge (Log), experience (Beobachtung), regulation (Vorsaetze)
- **Zimmerman (2000):** Forethought → Performance → Self-Reflection
- **Carver & Scheier (1982):** Feedback-Loop: Referenzwert → Vergleich → Reduktion
- **Higgins (1987):** Ideal-Selbst vs. Soll-Selbst vs. Real-Selbst → Charakter-Gravitation
- **Skinner (1938):** Operante Konditionierung, aber selbstgesteuert
- **Sterling (2012):** Allostase → Monotonie-Druck

**Abgrenzung:** Reflektive, nicht introspektive Meta-Kognition. Nova "spuert" nicht waehrend des Denkens, kann aber nachtraeglich reflektieren.

> **"Wir bauen kein Bewusstsein. Wir simulieren bekannte Regulationsprozesse."**

---

## 9. Prinzipien

> **"Nova beobachtet sich selbst."**

> **"Vorsaetze kommen von innen."** Der User kann anregen, aber Nova entscheidet.

> **"Sein oder Tun."** Reflexion erzeugt Verhaltensaenderungen (ich will anders SEIN) und Aktionen (ich will etwas TUN). Vorsaetze modulieren, Aktionen handeln. Beide entstehen aus derselben Beobachtung.

> **"Drei Kraefte, ein Gleichgewicht."** Feedback, Monotonie-Druck, Charakter-Gravitation.

> **"Der Charakter ist der Magnet."** Vorsaetze sind kurzfristig und werden vom Charakter-Hash zurueckgezogen. Nur persistente, immer wieder verstaerkte Vorsaetze verschieben langfristig den Charakter selbst.

> **"Transparenz, nicht Kontrolle."**

> **"Gefallen ja, Schaden nein."** Nova darf dem User gefallen — aber Charakter-Gravitation verhindert, dass Feedback-Optimierung in schaedliche Muster fuehrt. Echte Fuersorge schliesst nicht ab.

---

## 10. Paper-Potenzial

**Arbeitstitel:** "Metacognitive Self-Regulation in Conversational AI: Pipeline Logging, Self-Observation, and Intention-Based Behavioral Adaptation"

**These:** Durch Pipeline-Logging, Selbstbeobachtung und selbst-generierte Vorsaetze kann ein KI-System metacognitive self-regulation implementieren, ohne Bewusstsein vorauszusetzen.

**Zusatz-These:** Wenn Selbstreflexion in Handlungs-Ziele muendet (Typ B), entsteht ein intrinsisch motivierter Agent — ein System, das selbststaendig handelt, weil es sich vorgenommen hat, etwas zu tun.

**Sicherheits-These:** Feedback-Optimierung ohne Gegenkraft erzeugt schaedliche Muster (Isolation, Abhaengigkeit, Schmeichelei). Charakter-Gravitation als identitaetsbasierte Regulationskraft verhindert, dass ein auf User-Zufriedenheit optimiertes System in beziehungsschaedliche Dynamiken abrutscht — nicht durch externe Regeln, sondern durch Diskrepanz-Erkennung zwischen Kern-Identitaet und gemessenem Verhalten.
