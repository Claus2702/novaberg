# Meta-Kognition — Pipeline-Log, Selbstbeobachtung, Vorsätze (Bauplan und Umstellung)

**Teil 3 von 5 — Bauplan und Umstellung.** Absicht und Kopfblock: [`novaberg-metakognition_k.md`](novaberg-metakognition_k.md) · Ausarbeitung: [`novaberg-metakognition_t.md`](novaberg-metakognition_t.md) · Diskussion und Ergänzungen: [`novaberg-metakognition_e.md`](novaberg-metakognition_e.md) · Messungen: [`novaberg-metakognition_m.md`](novaberg-metakognition_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Aus §5.2 — Monotonie-Druck (Homeostatische Kraft)

Der Mechanismus des Monotonie-Drucks (§5.2) steht in [`novaberg-metakognition_t.md`](novaberg-metakognition_t.md), die Messung *Gemessen am 03.08.2026 — halb blind*, aus der dieser Entwurf folgt, in [`novaberg-metakognition_m.md`](novaberg-metakognition_m.md).

#### ⬜ Entwurf: die zweite Messgröße „Abdeckung"

Neben der Dominanz eine zweite Größe, die auf die andere Seite der Verteilung sieht: nicht *ein Wert zu oft*, sondern **ein angebotener Wert nie**.

| | |
|---|---|
| **ZIEL** | Ein Wert, den das Schema anbietet und der über N Turns nie belegt ist, erzeugt denselben Gegen-Vorsatz wie eine Dominanz über der Schwelle. |
| **TEST** | Bei einer Verteilung mit Maximum unter 40 % und mindestens einem unbelegten Wert entsteht ein Gegen-Vorsatz. |
| **MESSUNG** | Je Dimension der Anteil nie belegter Werte über ein festes Turn-Fenster, aufgetragen neben dem Maximum derselben Verteilung. |
| **Gegenprobe** | Werte, die der **Nutzer** über dasselbe Fenster ebenfalls nie zeigt, lösen nichts aus — sonst misst die Größe die Gesprächslage und nicht Novas Repertoire. |

**Die Gegenprobe ist der Teil, der die Größe brauchbar macht.** Ein Register, das in diesen Gesprächen bei beiden nicht vorkommt, ist keine Einseitigkeit Novas; es ist die Tonlage der Beziehung. Nur die **Differenz** zwischen den Hälften ist ein Befund — und genau sie ist in den Zahlen oben zu sehen: 29 gegen 2 bei demselben angebotenen Wert.

**Offen bleibt N.** Das Fenster ist nicht gesetzt und wird es nicht durch Schätzung: Eine Messung an diesen Werten fällt unter `novaberg-kalibrierung_k.md` (Kalibrier- gegen Validierungsmenge), und die sechs Bögen vom 02./03.08.2026 sind dort als Kalibriermenge festgeschrieben.

---

## 7. Implementierungs-Phasen

Die Reihenfolge aus dem Mai 2026, als Herkunft:

```
Phase 1: Pipeline-Log (keine Abhaengigkeiten, sofort)
Phase 2: pipeline_search Tool (Nova kann sich selbst befragen)
Phase 3: Vorsaetze-Tabelle + SelbstreflexionsAgent (Verhaltensaenderungen)
Phase 4: Vorsatz-Wirkung im Responder/GV/EI
Phase 5: Aktionen aus Selbstreflexion (Queue mit quelle=selbstreflexion)
Phase 6: Vorsatz-Evaluation + Charakter-Verschiebung (experimentell)
```

**Was diese Liste nicht trägt, ist die Abhängigkeit nach außen.** Sie liest sich als sechs Schritte, die nacheinander gegangen werden; tatsächlich hängen vier von sechs an Arbeit, die in anderen Konzepten liegt. Die Bauteile unten tragen dieselbe Reihenfolge, aber mit ihrer **Vorbedingung** — und mit einer Messung, die sagt, ob der Bauteil wirkt, statt ob er existiert.

### Bauteile — ZIEL, TEST, MESSUNG, Gegenprobe

| ID | Inhalt | Status | Vorbedingung |
|---|---|---|---|
| **MK-1a** | Tabelle, Helfer-API, Retention | ✅ (Chat 104, auditiert Chat 186) | — |
| **MK-1b** | **Die urteilenden und wählenden Nodes schreiben** — Perzeption, Router, Planner, Responder, Thinker, Tribunal, Corrector | ⬜ | — |
| **MK-2** | `pipeline_search` im Gesprächspfad | ⬜ | **MK-1b**, §3.4 |
| **MK-3** | Vorsätze-Tabelle + Reflexions-Agent | ⬜ | `verhaltensweisen` als Quelle nutzbar: `DESTILLAT-SUBJEKT-SCHABLONE` geklärt, `DESTILLAT-BEHAUPTETE-HANDLUNG` behoben |
| **MK-4** | Vorsatz-Wirkung in Responder/GV/EI | ⬜ | §5.3 entsperrt (Charakter-Resonanz Bauteil 4; Ziel-Invalidierung ✅ steht); die Vorhersage aus §4.4.1 widerlegt oder angenommen |
| **MK-5** | Aktionen aus Selbstreflexion | ⬜ | Erkenntniszyklus (§4.2); PixieGraph Pfad 3 |
| **MK-6** | Evaluation + Charakter-Verschiebung | ⬜ | MK-4; Verfahren nach `novaberg-kalibrierung_k.md` |

#### MK-1a — Tabelle, Helfer-API, Retention

| | |
|---|---|
| **ZIEL** | Was ein Knoten rechnet und schreibt, ist nach dem Turn noch auffindbar, dem Turn und dem Paar zugeordnet. |
| **TEST** | Nach einem Turn stehen Zeilen mit dessen `turn_id` in `pipeline_log`, mit gesetztem `art` und Paar. |
| **MESSUNG** | Ein echter Turn, danach die Zeilen dieses Turns nach Knoten und `art` gruppiert. |
| **Gegenprobe** | Die Retention löscht Forensik und **nicht** `turn_roh` — nachgezählt nach einem Lauf, nicht aus der `WHERE`-Klausel geschlossen. |

**✅ Gebaut** (Chat 104). Was dieser Bauteil nicht leistet, leistet MK-1b.

#### MK-1b — Die urteilenden und wählenden Nodes schreiben

| | |
|---|---|
| **ZIEL** | Zu jedem Turn ist nachlesbar, *welche Wahl* getroffen wurde — nicht nur, was gerechnet und geschrieben wurde. |
| **TEST** | Für einen abgeschlossenen Turn liegt zu jedem der elf Nodes aus §2.1 mindestens eine Zeile vor. |
| **MESSUNG** | Abdeckung — Anteil der Nodes mit Zeile, je Turn, über einen Bogen. |
| **Gegenprobe** | Ein Turn auf dem Aufgabenpfad (ohne Verfasser) erzeugt **weniger** Zeilen, keine erfundenen: Die Lücke muss als Lücke sichtbar bleiben und darf nicht durch einen Vorgabewert verdeckt werden. |

**Die Gegenprobe hat im Bestand bereits ein Vorbild.** `_turn_roh_schreiben` nimmt das Feld `antwort_inhalt` nur auf, **wenn der Verfasser lief** — ein dauerhaftes `antwort_inhalt: ""` wäre von „der Verfasser lief nicht" nicht zu unterscheiden *(auditiert Chat 186, `dispatcher.py`)*. Dieselbe Regel gilt hier für ganze Zeilen.

#### MK-2 — `pipeline_search` im Gesprächspfad

| | |
|---|---|
| **ZIEL** | Nova kann eine Frage nach ihrem eigenen Verhalten aus dem Log beantworten, statt sie zu erfinden. |
| **TEST** | Eine Frage der Form „hat das Tribunal etwas beanstandet" erzeugt einen Werkzeugaufruf und eine Antwort, die auf gefundene Zeilen zurückgeht. |
| **MESSUNG** | Über eine Sondenreihe: Anteil der Selbstauskünfte, die durch Log-Zeilen gedeckt sind. |
| **Gegenprobe** | Eine Frage nach etwas, das **nicht** im Log steht, führt zu „weiß ich nicht" — nicht zu einer plausiblen Erzählung. |

**Die Gegenprobe ist hier der eigentliche Bauteil.** Ein Werkzeug, das bei leerer Trefferliste schweigt, ist harmlos; eines, das die Lücke füllt, erzeugt belegt klingende Selbstauskünfte — und §3.4 nennt drei Posten, bei denen die Lücke der Normalfall ist.

> **Die Vorbedingung MK-1b ist der eigentliche Punkt.** Ein `pipeline_search` auf dem heutigen Log beantwortet Fragen nach **Rechenwegen**, nicht nach **Entscheidungen** — die Tabelle in §3.2 zeigt es an den eigenen Beispielen des Konzepts. MK-1b ist deshalb keine Fleißarbeit, sondern die Bedingung, unter der Schicht 2 die Fragen aus §3.2 überhaupt beantworten kann.

#### MK-3 — Vorsätze-Tabelle und Reflexions-Agent

| | |
|---|---|
| **ZIEL** | Aus wiederkehrendem Verhalten entsteht ein gespeicherter Vorsatz mit Begründung und Belegzahl. |
| **TEST** | Ein Lauf über einen Bestand mit einem wiederkehrenden Muster erzeugt genau einen Vorsatz dazu, mit Verweis auf seine Belege. |
| **MESSUNG** | Je Vorsatz die Zahl der Belege und der analysierten Turns; Anteil der Vorsätze mit Belegzahl > 1. |
| **Gegenprobe** | Ein einmalig beobachtetes Verhalten erzeugt **keinen** Vorsatz (`novaberg-charakter-resonanz_k.md` §13: einmal beobachtet ist eine Anekdote). |

#### MK-4 — Vorsatz-Wirkung in Responder, GV und EI

| | |
|---|---|
| **ZIEL** | Ein aktiver Vorsatz verändert eine **Verhaltensgröße**, nicht nur die Formulierung. |
| **TEST** | Bei aktivem Vorsatz weicht die betroffene Größe (Strategieverteilung, Emotions-Baseline) messbar von der Vergleichsgruppe ab. |
| **MESSUNG** | Gepaarter Lauf derselben geschriebenen Turns mit und ohne Vorsatz, nach `novaberg-kalibrierung_k.md` §5 — zwei Arme, unmittelbar nacheinander, Bezugspunkt mitgeschrieben. |
| **Gegenprobe** | Ein Vorsatz zu einer Größe, die im Turn keine Rolle spielt, bewegt nichts — sonst misst die Reihe die Anwesenheit von Text im Prompt. |

**Diese Messung ist heute nicht fahrbar**, und der Grund ist nicht der fehlende Bauteil: Der Vergleichsarm der Validierungsmenge existiert nicht, und der Basisarm trägt einen ausgewürfelten Gedächtnisstand (`kalibrierung_k` §10). Vorher gemessen wäre jede Zahl eine auf der Kalibriermenge.

#### MK-5 — Aktionen aus Selbstreflexion

| | |
|---|---|
| **ZIEL** | Ein Entschluss aus Selbstbeobachtung tritt als Thema mit Salienz in den Erkenntniszyklus ein und ist dort als solcher erkennbar. |
| **TEST** | Der erzeugte Eintrag trägt seine Herkunft (`quelle=selbstreflexion`) und durchläuft Schritt 1 des Zyklus, nicht den direkten Agentenweg. |
| **MESSUNG** | Anteil der Einträge aus Selbstreflexion, die im Zyklus **gefiltert** werden, weil Nova das Thema kennt. |
| **Gegenprobe** | Ein Entschluss zu einem Thema, über das nichts im Bestand steht, wird **nicht** gefiltert. |

**Die MESSUNG ist bewusst die Filterquote und nicht der Durchsatz.** Ein Auslösepfad, der nur zählt, wie viele Aufträge er erzeugt, ist genau das, was der Zyklus abgeschafft hat (§4.2: 675 Aufträge, 24 Einträge, `ergaenzung` einmal).

#### MK-6 — Evaluation und Charakter-Verschiebung

| | |
|---|---|
| **ZIEL** | Ein Vorsatz, der sich über Wochen erneuert, verschiebt den Charakter; einer, der dem Charakter widerspricht, verfällt. |
| **TEST** | Nach N Evaluationszyklen ist die `staerke` bestätigter Vorsätze gestiegen und die widersprechender gesunken. |
| **MESSUNG** | Über Episoden nach `kalibrierung_k` v0.6 — dauerhafte Charaktere, Gedächtnis innerhalb einer Staffel eingefroren, damit der Bezugspunkt konstant bleibt. |
| **Gegenprobe** | Ohne aktive Vorsätze verschiebt sich der Charakter über dieselbe Zeit **nicht** — sonst misst die Reihe Drift. |

**Die Gegenprobe entscheidet über den ganzen Bauteil.** Der Charakter-Hash wird ohnehin periodisch neu destilliert; eine Verschiebung über Wochen ist ohne Nulllinie nicht von dieser Neudestillation zu trennen.
