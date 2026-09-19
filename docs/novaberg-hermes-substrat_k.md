# Novaberg — Konzept: Hermes als Ausführungs-Substrat

**Absicht:** Nova handelt über einen externen Werkzeug-Agenten in der Welt — Nova ist der Kopf, Hermes sind die Hände: Hermes hat weder eigenes Gedächtnis noch eigenen Charakter, handelt nie aus eigenem Antrieb, bekommt nie den Rohtext des Nutzers, und jeder seiner Vorgänge fließt als Ereignis in Novas `pipeline_log` zurück.
**Stand:** 30. Juli 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Hermes-Substrat* ⚫ — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-hermes-substrat_t.md`](novaberg-hermes-substrat_t.md) · [`novaberg-hermes-substrat_b.md`](novaberg-hermes-substrat_b.md) · [`novaberg-hermes-substrat_e.md`](novaberg-hermes-substrat_e.md) · `novaberg-hermes-substrat_m.md` — keiner
**Entschieden:** 27 · **Offen beim Meister:** 0 (Liste in [`novaberg-hermes-substrat_e.md`](novaberg-hermes-substrat_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-hermes-substrat_k.md §3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-hermes-substrat_t.md`](novaberg-hermes-substrat_t.md), `_b` ist [`novaberg-hermes-substrat_b.md`](novaberg-hermes-substrat_b.md), `_e` ist [`novaberg-hermes-substrat_e.md`](novaberg-hermes-substrat_e.md).

| § | Datei |
|---|---|
| 0 | `_k` |
| 1 · 1.1 · 1.2 · 1.3 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 · 3.5 · 3.6 | `_k` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 · 5.5 · 5.6 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 | `_k` |
| 7 · 7.1 · 7.2 · 7.3 · 7.4 · 7.5 · 7.6 | `_t` |
| 8 · 8.1 · 8.2 · 8.3 · 8.4 | `_t` |
| 9 · 9.1 · 9.2 · 9.3 · 9.4 · 9.5 | `_t` |
| 10 · 10.1 · 10.2 · 10.3 | `_t` |
| 11 | `_b` |
| 12 | `_e` |
| 13 · 14 | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Status) und bisherige Schlusszeile (*Konzept erstellt …*) | `_e` |
| Entschieden, Offen, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

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

> **§4, §5 und §7 bis §12 stehen nicht in dieser Datei.** Bestandsaufnahme, Randbedingungen, die Naht HermesAgent, das Körperschema, der Ereignis-Rückfluss sowie Betrieb und Sicherheit (§4, §5, §7–§10) stehen in [`novaberg-hermes-substrat_t.md`](novaberg-hermes-substrat_t.md); die Messfragen der Phase 0 (§11) in [`novaberg-hermes-substrat_b.md`](novaberg-hermes-substrat_b.md); die offenen Entscheidungen H1–H8 (§12), der bisherige Kopf und die bisherige Schlusszeile in [`novaberg-hermes-substrat_e.md`](novaberg-hermes-substrat_e.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

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
