# Novaberg — Vorbedingungen im Schreibpfad: das Clipboard-Prinzip

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Convention — wie ein Agent an einen Wert kommt, den ein anderer erzeugt
**Stand:** 16. August 2026 (der offene Punkt ist entschieden, und er zerfiel dabei in zwei: **kein generischer Vermittler zur Laufzeit** — die Regel dafür ist das Clipboard-Prinzip in §3. Die **Selbstanmeldung** dagegen existiert zweifach: auf der Manager-Fläche verdrahtet und wirksam, auf der Agenten-Fläche vollzählig gepflegt und ohne Leser, §3.7a — mit einem bereits verrotteten Eintrag, §3.7b). Davor: 06. Mai 2026, Chat 78
**Pfad:** novaberg/docs/novaberg-convention-planner-needs.md
**Typ:** Convention
**Voraussetzung:** Agent-System (Epic 11) ✅, BaseAgent + AgentResult + Planner-Schleife (E9) ✅
**Archiviert:** `archive/novaberg-convention-planner-needs-erweiterung.md` — der verworfene generische Mechanismus (ehemals §3 bis §7)

---

> ## Was dieses Dokument ist, seit dem 16.08.2026
>
> Es hieß bis dahin *„Plugins fragen, Planner vermittelt"* und beschrieb einen **Vermittlungs-Mechanismus, der nie gebaut wurde**. Der Fall, für den er entworfen war, ist inzwischen gelöst — auf einem anderen Weg, und dieser Weg hatte keine Regel.
>
> **Was blieb:** die Problemanalyse (§1, §2) und die Designprinzipien (§9). Beide gelten unabhängig davon, wie das Problem gelöst wird.
>
> **Was neu ist:** §3 — die Regel für den Weg, der tatsächlich gebaut ist.
>
> **Was ging:** der generische Mechanismus, nach `archive/`. Der Grund steht in §11.
>
> **Und was beinahe mitgegangen wäre:** Unter dem Namen *„Needs-Mechanismus"* standen **zwei** Dinge — die Auflösung zur Laufzeit und die **Selbstanmeldung** der Agenten. Nur die erste ist verworfen. Die zweite ist gebaut, wird von allen Agenten gepflegt und hat keinen Leser (§3.7, §11.1).

---

## 1. Motivation

Der Schreibpfad pro Turn besteht heute aus genau einem Agent: Router setzt
`agent_name`, der Planner führt aus, der Agent schreibt. Für die Salienz-Pipeline
ab M5 reicht das nicht mehr. Eine Erinnerung wie *„Wir gehen morgen mit Anna
ins Tandoor"* will gleichzeitig:

- aufgelöste Entitäten (Anna, Tandoor) → FaktenManager im Resolve-Modus
- einen Timeline-Bezug („morgen") → TimelineAgent im Create-Modus
- einen KZG-Eintrag mit den oben aufgelösten Magneten → KZG-Salienz

Das ist eine sequenzielle Kette mit Datenfluss zwischen den Schritten:
TimelineAgent muss Annas Entitäts-ID kennen, um sie an den Termin zu hängen.
Die KZG-Salienz braucht beide — Entitäten-IDs und Timeline-ID — als Magneten.

Ein zentraler Routing-Code, der diese Reihenfolge kennt, wäre ein Bruch des
Plugin-Prinzips (E7). Eine direkte Agent-zu-Agent-Kommunikation wäre ein Bruch
der Akten-Architektur (E4: kein horizontaler Traffic).

**Diese Analyse gilt unverändert.** Was sich am 16.08.2026 geändert hat, ist
allein die Antwort darauf — sie steht in §3 statt im archivierten Mechanismus.

---

## 2. Leitprinzip

> **Der Erzeuger legt den Wert ab. Der spätere Leser nimmt ihn auf oder kommt ohne ihn aus.**

Wie ein Zettel auf dem Tisch, nicht wie ein Gespräch zwischen zwei Mitarbeitern:
Wer den Wert erzeugt, weiß nicht, wer ihn abholt. Wer ihn abholt, weiß nicht,
wer ihn hingelegt hat — nur, ob er daliegt.

**Keine direkte Agent-Kommunikation.** Kein Agent importiert oder ruft einen
anderen. **Keine zentrale Routing-Tabelle.** Kein Modul kennt die Reihenfolge
der Ketten. **Keine LLM-basierte Auflösung.** Wer welchen Wert übernimmt, ist
Code, nicht Inferenz.

**Und, seit dem 16.08.2026 ausdrücklich:** Der Datenträger zwischen zwei
Agenten ist der **Zustand des Graphen**, nicht die Akte. Die Akte
(`AgentResult`) trägt das Ergebnis eines Agenten an den Planner und den
Responder; sie wird von keinem zweiten Agenten gelesen. Das war bis dahin
anders beschrieben und nie so gebaut — siehe §9.3.

---

## 3. Das Clipboard-Prinzip

### 3.1 Die Regel

> **Ein Wert, den ein Agent erzeugt und ein späterer Knoten desselben Turns
> braucht, wandert über einen im Zustandstyp deklarierten Schlüssel — flach,
> benannt und optional.** Der lesende Knoten arbeitet weiter, wenn der Schlüssel
> leer ist; er hält nicht an.

Drei Teile, und jeder trägt seinen eigenen Grund:

**Deklariert.** Ein Schlüssel, der nicht in `ConversationState` steht, wird an
der Knotengrenze stillschweigend verworfen — der Wert ist innerhalb des
Knotens lesbar und dahinter weg, ohne Fehler und ohne Warnung. Ein Clipboard,
das nicht deklariert ist, ist deshalb kein unsauberes Clipboard, sondern
gar keins. Der Vorfall dazu steht in `novaberg-lesson_l_stategraph-channel-zwang.md`.

**Flach und benannt.** Der Schlüssel trägt den Namen des Wertes
(`timeline_id`), nicht den des Erzeugers. Der Leser fragt nach der Sache, nicht
nach der Zuständigkeit — das ist es, was die Agenten voneinander unabhängig
hält.

**Optional.** Ein fehlender Vorbedingungswert ist kein Fehler. Er ist der
Regelfall in jedem Turn, in dem der erzeugende Agent nicht lief. Der lesende
Knoten entscheidet selbst, was er ohne den Wert tut — das ist der
Continue-on-Error-Grundsatz aus dem archivierten §7, und er hat als einziger
den Mechanismus überlebt.

### 3.2 Geltungsbereich

**Erfasst:** der **Schreibpfad innerhalb eines Turns**, wo ein Agent einen
strukturellen Anker erzeugt, den ein späterer Knoten braucht.

**Ausdrücklich nicht erfasst** — jede dieser Grenzen ist am Bestand geprüft und
nicht abgeleitet:

| Nicht erfasst | Warum |
|---|---|
| **Der Lesepfad** | Mehrere Lese-Agenten laufen ohne Datenfluss untereinander parallel. Sie brauchen keine Vorbedingung, nur eine Quelle. Ausführlich in §8 |
| **Querschnitts-Zugriffe auf dieselbe Spalte** | Der WiedervorlageAgent scannt vier Repositorien nach demselben Feld. Das ist keine Kette, sondern eine Schleife über gleichartige Orte — kein Wert wandert |
| **Werte innerhalb eines Agenten-Subgraphen** | Was `magnete_aufloesen` an `verdichten` weiterreicht, läuft über `state["parameter"]` desselben Agenten. Dafür gilt die Bauart des Agenten, nicht diese Regel |
| **Der Weg zum Responder** | `AgentResult` und `task_block` tragen Ergebnisse an den Antwortpfad. Das ist Ausgabe, keine Vorbedingung |

### 3.3 Woran man einen Verstoß erkennt

Vier Formen, in absteigender Schwere:

1. **Ein Agent importiert oder ruft einen anderen Agenten.** Der harte Bruch —
   damit kennt ein Plugin ein anderes.
2. **Ein Knoten schreibt einen Schlüssel, der nicht in `ConversationState`
   deklariert ist.** Der Wert ist hinter der Knotengrenze weg. Das sieht wie ein
   funktionierendes Clipboard aus, solange man nur innerhalb des Knotens prüft.
3. **Ein Clipboard-Schlüssel fehlt in der Zustandstabelle** von
   `novaberg-graph.md` §4.8a. Dann existiert der Kanal, aber niemand außer
   seinen zwei Enden weiß von ihm.
4. **Der lesende Knoten bricht ab, wenn das Clipboard leer ist.** Damit wird aus
   einer optionalen Vorbedingung eine verdeckte Pflicht — und der Turn, in dem
   der Erzeuger nicht lief, schlägt fehl statt weiterzulaufen.

### 3.4 Maschinelle Prüfbarkeit

**Teilweise möglich, heute nicht gebaut.** Form 2 ist am Syntaxbaum prüfbar:
Jeder Schreibzugriff auf einen Zustands-Schlüssel wird gegen die Felder des
Zustandstyps gehalten. Form 3 ist ein Abgleich der Clipboard-Schlüssel gegen die
Tabelle in `novaberg-graph.md` §4.8a. Form 1 ist ein Import-Test über
`agents/`. Form 4 ist nicht mechanisch prüfbar — ob ein Abbruch richtig ist,
hängt am Zweck des Knotens.

### 3.5 Die bekannte Schwäche, benannt statt verschwiegen

**Die Reihenfolge ist durch die Graph-Topologie gesichert, nicht durch eine
Prüfung.** Der TimelineAgent läuft in der Planner-Schleife, früh im Turn; der
KZG-Schreibpfad läuft im `dispatcher`-Knoten unmittelbar vor `END`. Dass der
Erzeuger vor dem Leser liegt, folgt aus den Kanten des Graphen — es steht in
keiner Zusicherung, und keine Prüfung schlägt an, wenn jemand die Kanten
umhängt.

**Das ist tragbar, solange die Zahl der Clipboards klein ist**, und es ist der
Preis dafür, dass kein Vermittler existiert, der die Reihenfolge kennen müsste.
Wächst die Zahl, kippt die Rechnung — dann ist der archivierte Mechanismus neu
zu bewerten. Die Zahl steht in §4.

### 3.6 Verworfene Alternativen

| Alternative | Warum verworfen |
|---|---|
| **Generischer Needs-Mechanismus** mit Provides-Index und Re-Entry | Eine Kette und ein Anbieter je Bedarf im Bestand. Ein Index über einen Eintrag vermittelt nichts. Gemessen am 16.08.2026, siehe §11 — Text unter `archive/` |
| **Direkter Agent-zu-Agent-Aufruf** | Bricht die Akten-Architektur (E4). Ein Agent, der einen anderen kennt, ist kein Plugin mehr |
| **Zentrale Routing-Tabelle** im Planner | Bricht das Plugin-Prinzip (E7). Jede neue Kette wäre eine Änderung am Planner |
| **Fail-Fast** bei fehlender Vorbedingung | Eine fehlende Disambiguierung würde das Gespräch anhalten. Der Nutzer bezahlt für eine Unschärfe, die das System selbst erzeugt hat |

**Nicht verworfen, sondern bereits gebaut:** die **Selbstauskunft** der Agenten. Sie ist kein Teil der Vorbedingungs-Auflösung und hat mit ihr auch nichts zu tun — siehe §3.7.

### 3.7 Die Selbstauskunft — gebaut, vollzählig, ohne Leser

**Die Regel, und sie ist älter als dieses Dokument:**

> **Ein Agent beschreibt selbst, was er kann. Kein anderes Modul führt eine
> Liste darüber.**

Das ist der Kern des Plugin-Prinzips (E7) und der einzige Teil des ursprünglich
vorgeschlagenen Mechanismus, der **existiert**. Er hat nur nichts mit
Vorbedingungen zu tun — er beantwortet nicht *„wer liefert mir X"*, sondern
*„wer bist du und was tust du"*.

Die Deklarationsfläche sitzt in `agents/base.py` und ist breit: `name`,
`beschreibung` (lädt `AGENT.md` aus dem eigenen Verzeichnis), `typ`,
`faehigkeiten`, `graph_eignung`, `lastart`, `periodic_task`, `context_user`.
`AgentRegistry.beschreibungen()` fügt sie zu einem Text zusammen, dessen
Docstring seinen Zweck nennt: *„für den Planner-Prompt"*.

### 3.7a Zwei Deklarationsflächen — die ältere ist verdrahtet, die jüngere nicht

**Die Regel ist nicht gebrochen, weil niemand sie befolgte, sondern weil sie
zweimal umgesetzt wurde und nur einmal angeschlossen ist.**

**Die Manager-Fläche (Chat 5) lebt, und sie ist die bessere.** Jeder Manager
deklariert `router_prompt` — *„woran erkennst du, dass du mich brauchst"*.
`get_combined_router_prompt()` sammelt alle ein, und `graph/nodes/router.py`
setzt sie als `[AGENTEN]`-Block in den System-Prompt eines Modellaufrufs. Der
Router liest die Äußerung, liest die Aushänge und entscheidet.

Die Gestalt dieser Deklarationen ist der Grund ihres Überlebens:

```
TIMELINE-ERKENNUNG:
Entscheidend ist NICHT die Satzform, sondern ob der Prompt ein Datum,
eine Uhrzeit, einen Zeitraum oder ein zeitgebundenes Ereignis enthaelt.

CHARAKTER-IDENTITAET-ERKENNUNG:
NICHT triggern bei:
  - Emotionalen Ausdruecken ("Du bist toll!") — das ist Feedback
```

Das sind **Anweisungen an den Aufrufer**, samt Negativfällen. Danach bildet der
Planner das Ergebnis über `router_intents` und `manager.ziel` auf einen Manager
ab — ebenfalls eine Deklaration. **Beide Stufen lesen Selbstauskunft.**

**Die Agenten-Fläche (Chat 21/22) ist vollzählig gepflegt und nirgends
angeschlossen:**

```
faehigkeiten deklariert         14 von 14 Agenten
AGENT.md vorhanden              12 von 14
AgentRegistry.beschreibungen()  aggregiert beides
Aufrufer im Produktivcode        0
```

**Ein Agent wird heute gefunden, indem er den Namen seines Managers erbt** —
`AgentRegistry.finden(zustaendiger.ziel)`. Wer keinen Manager hat, ist auf dem
Nutzerpfad unerreichbar; das trifft **5 von 14** Agenten als erreichbar und ist
für die neun Hintergrund-Agenten richtig so.

> **Woran der Unterschied liegt, und das ist die eigentliche Lehre:**
> `["termin_erstellen", "termin_lesen"]` ist eine Auskunft in der Sprache des
> **Anbieters**. *„Entscheidend ist nicht die Satzform, sondern ob der Prompt
> ein Datum enthält"* ist eine Anweisung in der Sprache des **Aufrufers**. Nur
> die zweite ist benutzbar, und nur die zweite hat je einen Leser gefunden.
> **Eine Selbstauskunft stirbt nicht an mangelnder Güte, sondern daran, dass sie
> die Frage des Anbieters beantwortet statt der des Aufrufers.**

Geführt als `SELBSTAUSKUNFT-OHNE-LESER`. Die Abhilfe ist deshalb **nicht**, der
Fähigkeitenliste einen Leser zu bauen — sie transportiert die falsche Gattung
Text —, sondern den Agenten zu geben, was die Manager haben.

### 3.7b Eine ungelesene Deklaration verrottet, und der Verfall ist unsichtbar

**Gemessen am 16.08.2026, bei der Gegenprobe „wer wird eigentlich nie
gewählt":** `delegation` deklariert `graph_eignung = ["user"]` und läuft
tatsächlich über den Hintergrund-Router (`services/pixie/router.py`,
Sonderfall `aufgabe == "delegation"`). Auf dem Nutzerpfad ist der Agent nicht
wählbar, weil kein Manager dieses Ziel trägt. **Dreizehn Deklarationen stimmen,
diese eine ist falsch.**

> **Das ist die Klasse, nicht der Einzelfall.** Ein Feld ohne Leser wird
> gepflegt, aber nie widerlegt — es gibt keinen Lauf, der es prüft, und keinen
> Fehler, den es auslöst. Es sieht so lange richtig aus, wie niemand hinsieht.
>
> **Und daraus folgt eine Reihenfolge, die nicht die naheliegende ist:** Wer den
> fehlenden Leser nachbaut, schaltet damit eine Datenbasis scharf, die
> **niemand je gegengeprüft hat** — `fuer_graph("user")` nähme `delegation`
> auf, `fuer_graph("pixie")` ließe ihn weg, beides verkehrt herum. **Die
> Deklarationen werden vor dem Anschließen geprüft, nicht danach.**

---

## 4. Der Bestand

> **Zustandsteil, kein Regelteil.** Die folgenden Zahlen und Stellen beschreiben,
> wie es am 16.08.2026 aussieht. Sie ändern sich mit dem nächsten Commit und
> haben nicht den Rang der Regel in §3.

Zwei Clipboards, beide in `graph/state.py` deklariert und in
`novaberg-graph.md` §4.8a beschrieben:

| Schlüssel | Erzeuger | Leser | Zweck |
|---|---|---|---|
| `timeline_id` | `agents/timeline/dispatch.py` | `agents/kzg/magnete.py` | Der KZG-Schreibpfad übernimmt einen im selben Turn angelegten Timeline-Eintrag, statt einen zweiten `erinnerungs_anker` für denselben Tag zu erzeugen |
| `session_turn_kern` | `agents/kzg/dispatch.py` | `graph/nodes/dispatcher.py` | Der verdichtete Kern des Turns wandert vom KZG-Agent zum Schreiber des Session-Turns |

**Und eine Doppelung, die zum Preis dieser Bauart gehört:**
`agents/kzg/magnete.py` löst Entitäten selbst auf und folgt dabei dem
Zwei-Schritt-Muster aus `plugins/fakten_manager/manager.py` — der Docstring der
Funktion sagt es selbst. Ein zweckgebauter Knoten je Kette heißt: dasselbe
Muster ein zweites Mal. Bei einer Kette ist das billiger als ein Vermittler,
bei fünf nicht mehr.

---

## 5. bis 7. — archiviert

Der generische Vermittlungs-Mechanismus ist verworfen und archiviert; keiner
seiner Bezeichner existiert im Code — `provides`, Provides-Index,
`AgentInput`, `needs_pending`, Re-Entry-Zyklus und Continue-on-Error als
Resolver-Eigenschaft stehen vollständig in
`archive/novaberg-convention-planner-needs-erweiterung.md`, dort unter den
ursprünglichen Nummern §3 bis §7.

**Die Nummern bleiben hier frei.** Verweise aus anderen Dokumenten auf
„`novaberg-convention-planner-needs.md` §6" zeigen auf den archivierten Text
und werden dorthin umgehängt, nicht auf einen neuen Inhalt gerichtet.

---

## 8. Lese- vs. Schreib-Pfad

**Diese Convention betrifft nur den Schreib-Pfad.**

Lese-Operationen (`enrich_entries()` im Enricher, Volltext-Suche, Embedding-Suche)
laufen weiter parallel. Der Enricher ruft mehrere Lese-Agenten gleichzeitig
auf, ohne Datenfluss zwischen ihnen — parallele Ausführung ist effizient
und braucht keine Vorbedingungs-Auflösung.

Die Clipboard-Regel wird nur dort scharf, wo Agenten *schreiben* und dafür
strukturelle Anker brauchen, die andere Agenten erst auflösen oder erzeugen.

---

## 9. Designprinzipien

1. **Plugins kennen ihre eigenen Spalten und Fähigkeiten — sonst nichts.**
   Kein Agent weiß, dass `timeline_id` vom TimelineAgent kommt. Er weiß nur,
   dass er einen `timeline_id`-Wert hätte.

2. **Kein Modul kennt die Reihenfolge der Ketten.** Der Planner wählt einen
   Agenten je Durchlauf; welche Werte dabei entstehen, ist seine Sache nicht.
   *(Bis zum 16.08.2026 stand hier „Der Planner ist Vermittler, kein
   Entscheider." Er vermittelt nichts — er wählt aus.)*

3. **Der Zustand ist der Datenträger zwischen Agenten, die Akte der Träger zum
   Antwortpfad.** Plugins reden nicht direkt miteinander.

   > **Am 16.08.2026 berichtigt.** Hier stand: *„Alle Daten fließen über
   > `AgentResult` und `AgentInput`."* Das war nie gebaut — `AgentInput`
   > existiert nicht, und kein Agent liest die Akte eines anderen. Gebaut ist
   > der deklarierte Zustands-Schlüssel aus §3. Die Absicht dahinter — kein
   > horizontaler Verkehr — hält der gebaute Weg ein; sie hing nie an dieser
   > Umsetzung.

4. **Continue-on-Error.** Teil-Fehler blockieren nicht die Pipeline. Jeder
   Knoten entscheidet selbst, was bei fehlenden Vorbedingungen zu tun ist.

5. **Statisch, nicht inferenziert.** Wer welchen Wert übernimmt, steht als Code
   im lesenden Knoten. Keine LLM-Inferenz entscheidet darüber.

6. **YAGNI bis Konkretfall.** Ein zweckgebauter Knoten je Kette, solange die
   Zahl der Ketten klein ist. Der allgemeine Mechanismus liegt fertig
   beschrieben im Archiv und wird geholt, wenn die Zahl ihn trägt — nicht
   vorher.

---

## 10. Verweise

### Verbindliche Dokumente

- Convention: `novaberg-convention-event-model.md` — User und Charakter als Akteure
- Convention: `novaberg-convention-magneten.md` — was ein Magnet ist und wann er fehlen darf
- Konzept: `novaberg-architecture.md` Abschnitt 6 — Agent-System (Epic 11)
- Modul: `novaberg-graph.md` §4.8a — die Zustandstabelle mit den Clipboard-Schlüsseln
- Modul: `novaberg-node-planner.md` — Planner-Knoten und Schleife
- Modul: `novaberg-node-agent-dispatch.md` — Dispatch-Pattern
- Lesson: `novaberg-lesson_l_stategraph-channel-zwang.md` — warum ein undeklarierter Schlüssel kein Kanal ist

### Archiv

- `archive/novaberg-convention-planner-needs-erweiterung.md` — der verworfene generische Mechanismus

---

## 11. Der offene Punkt — entschieden am 16.08.2026

**Die Frage war:** Wird der generische Needs-Mechanismus noch gebraucht,
nachdem der Fall, für den er entworfen wurde, ohne ihn gelöst ist?

**Die Antwort ist nein**, und sie hängt an einer Zahl statt an einer Meinung.
Gezählt wurden die Fremdzugriffe auf die beiden Dienste, um die es geht
(`EntityResolutionService`, `TimelineRepository`) — vier Kandidaten, jeder
einzeln nachgesehen:

| Kandidat | Befund |
|---|---|
| `plugins/notizen_manager/manager.py` | **unbenutzter Import** — kein Zugriff |
| `graph/nodes/thinker.py` | **Lesepfad** — von §8 ausgeschlossen |
| `agents/wiedervorlage/agent.py` | **Querschnitts-Scan** über vier Repositorien — keine Kette |
| `agents/kzg/magnete.py` | **die eine Kette** |

**Eine Kette, ein Anbieter je Bedarf.** Damit hat ein Provides-Index nichts zu
indizieren und das *„erster gewinnt"* nichts zu entscheiden. Der Mechanismus
wäre eine Wette auf Ketten, die es nicht gibt.

**Was stattdessen geschah:** Die Bauart, die den Fall tatsächlich löst, hatte
keine Regel — sie war an zwei Stellen im Code beschrieben und in keiner
Konvention. Genau daraus entstand die Lage, dass dieses Dokument seit Mai einen
Mechanismus als geltend beschrieb, der nie existierte. §3 schließt das.

### 11.1 Die Frage war zu eng gestellt — und die zweite Hälfte fällt anders aus

**Nachtrag vom selben Tag.** Der Vorschlag von Chat 78 enthielt **zwei** Dinge
unter einem Namen, und die obige Messung trifft nur eines davon:

| Teil | Was er beantwortet | Befund |
|---|---|---|
| **Auflösung zur Laufzeit** — Provides-Index, `needs_pending`, Re-Entry | *„Wer liefert mir X, jetzt?"* | **verworfen.** Eine Kette, ein Anbieter je Bedarf |
| **Selbstanmeldung** — der Agent gibt Aufgabe, Nutzen und Dienste bekannt | *„Wer bist du und was kannst du?"* | **gebaut und vollzählig gepflegt — ohne einen einzigen Leser** |

**Der zweite Teil war nie eine offene Frage, sondern ein unbemerkter
Fehler-Zustand.** Er steht in §3.7a und §3.7b mit seinen Zahlen. Die Trennung ist
deshalb wichtig, weil beide Teile im Ursprungsdokument denselben Namen trugen: Wer
*„Needs-Mechanismus"* verwirft, verwirft bei unachtsamer Lesart auch die
Selbstauskunft — und die ist das Plugin-Prinzip selbst.

### 11.2 Der Abgleich nach außen — dieselbe Trennung, dieselbe Lücke

Weil die Frage sich stellt, sobald fremde Dienste eingebunden werden sollen:
Das **Model Context Protocol** (geprüft gegen Revision `2026-07-28`) trennt
genauso, und es zieht die Grenze an derselben Stelle.

- Ein Werkzeug meldet `name`, `title`, `description`, `inputSchema`,
  `outputSchema` und vier unverbindliche Verhaltens-Hinweise. **Das ist die
  Sprache des Anbieters** — dieselbe Gattung wie `faehigkeiten`.
- **Die Auswahl ist ausdrücklich kein Protokollgegenstand.** Werkzeuge sind
  *model-controlled*; im Ablaufdiagramm der Spezifikation steht zwischen
  Auflistung und Aufruf ein Abschnitt *Tool Selection* **ohne eine einzige
  Nachricht**. Dieselbe Arbeitsteilung wie hier: Ein Sprachmodell wägt
  Beschreibungstexte ab.
- Ein Feld für den Aushang gibt es — `instructions` im Ergebnis von
  `server/discover`, *„natural-language guidance for LLMs on how to use this
  server effectively"*. Es ist aber **je Server** statt je Dienst, optional an
  beiden Enden, ohne vorgesehene Zusammenführung mehrerer Anbieter, und das
  Beispiel der Spezifikation füllt es mit einer Selbstbeschreibung.
- Für das, was hier `router_prompt` leistet, läuft dort eine eigene
  Arbeitsgruppe (*Skills over MCP*), deren Ergebnis noch offen ist.

**Der Zustandstransport dagegen ist deckungsgleich mit §3** und unabhängig
entstanden: Da MCP keine Sitzung auf Protokollebene kennt, empfiehlt es
ausdrücklich, Zustand als **expliziten Handle** zurückzugeben und beim nächsten
Aufruf wieder mitzugeben — *„the model is responsible for carrying it
forward"* —, und die Lebensdauer gehöre in die Beschreibung des erzeugenden
Werkzeugs. Das ist das Clipboard-Prinzip, Wort für Wort.

> **Was daraus für einen möglichen Anschluss fremder Dienste folgt:** Der
> Aushang ist der Teil, den man selbst bauen muss. Übernimmt man nur, was das
> Protokoll überträgt, bekommt man die Fähigkeitenliste — und damit genau die
> Gattung Text, die hier vier Monate lang keinen Leser gefunden hat.

**Wann die Entscheidung neu zu treffen ist:** wenn die Zahl der Clipboards
wächst. Die Schwäche aus §3.5 — die ungeprüfte Reihenfolge — skaliert nicht,
und die Doppelung aus §4 auch nicht. Beides ist bei zwei Clipboards billig und
bei fünf nicht mehr.

---

## Versionshistorie

- **v0.5 — 16.08.2026:** **Die zweite Kontrolle hat §3.7 zur Hälfte widerlegt, und zwar die härtere Hälfte.** Dort stand, der Planner wähle über Zeichenketten-Abgleich *statt* über die Selbstauskunft. Falsch: **Der Router läuft davor und wählt sehr wohl über sie** — per Modellaufruf über die `router_prompt`-Aushänge der Manager, eingesammelt von `get_combined_router_prompt()`. Richtig ist die Zweiteilung in §3.7a: **zwei Deklarationsflächen, die ältere an beiden Stufen verdrahtet, die jüngere an keiner**, und ein Agent wird gefunden, indem er den Namen seines Managers erbt (5 von 14 auf dem Nutzerpfad erreichbar). Daraus die eigentliche Lehre, die den Befund vom Einzelfall zur Klasse hebt: **Eine Selbstauskunft stirbt daran, dass sie die Frage des Anbieters beantwortet statt der des Aufrufers** — `["termin_erstellen"]` gegen *„entscheidend ist nicht die Satzform, sondern ob der Prompt ein Datum enthält"*. Neu §3.7b: **Eine ungelesene Deklaration verrottet unbemerkt** — `delegation` deklariert `["user"]` und läuft über den Hintergrund-Router; dreizehn stimmen, diese eine nicht, und kein Lauf konnte es melden. Daraus eine Reihenfolge gegen die naheliegende: erst die Deklarationen gegenprüfen, dann den Leser bauen. Neu §11.2: der Abgleich mit dem Model Context Protocol (Revision `2026-07-28`) — dieselbe Trennung, dieselbe Lücke bei der Auswahl, und ein **deckungsgleiches** Clipboard-Prinzip beim Zustandstransport.
- **v0.4 — 16.08.2026:** **Die Frage aus §11 war zu eng gestellt.** Der Vorschlag von Chat 78 enthielt zwei Dinge unter einem Namen: die **Auflösung zur Laufzeit** und die **Selbstanmeldung** eines Agenten. Verworfen ist nur die erste. Die zweite ist **gebaut und von 14 der 14 Agenten gepflegt** — `faehigkeiten`, `AGENT.md`, `graph_eignung`, `lastart` — und `AgentRegistry.beschreibungen()` fügt sie zu einem Text „für den Planner-Prompt" zusammen, **den kein Produktivcode aufruft**. Der Planner wählt über Zeichenketten-Abgleich statt über die Selbstauskunft, also über genau die zentrale Zuordnung, die §1 als Bruch des Plugin-Prinzips benennt. Neu §3.7 mit dem Fehler-Zustand und seinen Zahlen, §11.1 mit der Trennung der beiden Teile. Die Trennung steht ausdrücklich da, weil sie beim Verwerfen beinahe verlorengegangen wäre: Wer *„Needs-Mechanismus"* verwirft, verwirft bei unachtsamer Lesart auch die Selbstauskunft.
- **v0.3 — 16.08.2026:** **Der offene Punkt aus v0.2 ist entschieden, und das Dokument hat dabei seinen Gegenstand gewechselt.** Der generische Mechanismus ist verworfen und liegt vollständig unter `archive/` — die Zahl, die ihn verworfen hat: **eine Kette und ein Anbieter je Bedarf**, aus vier Kandidaten, von denen drei bei Einzelprüfung wegfielen (ein unbenutzter Import, ein Lesepfad, ein Querschnitts-Scan). An seine Stelle tritt **§3, das Clipboard-Prinzip** — die Regel für den Weg, der wirklich gebaut ist, mit Geltungsbereich, vier Verstoßformen, dem Stand der maschinellen Prüfbarkeit und der benannten Schwäche, dass die Reihenfolge aus der Graph-Topologie folgt und aus keiner Zusicherung. **§9.3 ist berichtigt statt gestrichen:** Dort stand *„Alle Daten fließen über `AgentResult` und `AgentInput`"* — `AgentInput` hat nie existiert, und kein Agent liest die Akte eines anderen. Die Absicht dahinter hält der gebaute Weg trotzdem ein. §2 und §9.2 mitgezogen, weil der Planner nichts vermittelt, sondern auswählt. §4 trägt den Bestand als ausdrücklich gekennzeichneten Zustandsteil: zwei Clipboards und die Doppelung, die ein zweckgebauter Knoten je Kette kostet. Die Nummern §5 bis §7 bleiben frei, damit bestehende Verweise auf den archivierten Text zeigen können.
- **v0.2 — 16.08.2026:** Erstmals gegen den Code gehalten, mit einem Ergebnis, das die erste Einschätzung umkehrt. **Die Voraussetzung im Kopf ist zutreffend** — Agentenklasse, Ergebnisklasse, Planner-Schleife samt Schleifenschutz und Registry stehen alle. **Die beschriebene Erweiterung ist nicht gebaut**, und **der Anwendungsfall aus §1 wurde inzwischen ohne sie gelöst**: Ein zweckgebauter Knoten löst Entitäten und Zeitbezug auf und speist beide in den Schreibpfad. Daraus §11, der offene Punkt — nicht *wann* bauen, sondern *ob* noch. Neu ist ein Kasten vor §1, der Gebautes von Beschriebenem trennt: Der Text steht durchgehend im Präsens und war ohne ihn nicht als Soll erkennbar.
- **v0.1 — 06.05.2026, Chat 78:** Erstfassung.
