# Novaberg — Memory-Kern: Synapsen-Modell

**Absicht:** Novas Langzeitgedächtnis ist ein assoziatives Netz — jede promotete Erinnerung bleibt ein eigener Knoten mit Stärke, Verfall und Reaktivierung, Kanten sind abgeleitete Assoziationen über Entität, Zeit, Thema und Embedding, der Abruf geht von Embedding-Ankern entlang der Kanten, und verstärkt wird nur, was eine Antwort tatsächlich verwendet.
**Stand:** 18. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Synapsen-Modell* 🟠 · *Zwei-Call-Promotion* 🟢 · *Ebbinghaus-Decay + Soft-Delete* 🟢 · *Halbreaktivierung* 🟠 · *KZG-Magnetfelder* 🔴 · *Pipeline-Log* 🔴 · *Wahrnehmungs-Gravitation* 🟠 · *Langzeitgedächtnis alt* 🟢 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) · [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) · [`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md) · [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md)
**Entschieden:** 2 · **Offen beim Meister:** 0 (Liste in [`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-memory-synapsen_k.md §7` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md), `_b` ist [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md), `_e` ist [`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md), `_m` ist [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md).

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 · 2.6 · 2.7 | `_k` |
| 3 · 3.1 · 3.2 | `_k` |
| 4 · 4.1 · 4.1b · 4.1a · 4.2 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 | `_t` |
| 6 | `_t` |
| 7 · 7.1 · 7.2 · 7.3 · 7.4 · 7.5 · 7.6 · 7.6.1 · 7.6.2 · 7.6.3 · 7.7 · 7.8 · 7.9 · 7.9.1 · 7.9.2 · 7.10 | `_t` |
| 7.1a | `_t` (mit Hinweisen); die Unterabschnitte *Was heute stattdessen gilt, und was es anrichtet* und *Die Folge für die Zähler* und der `[gemessen]`-Absatz *gegen den echten Bestand* aus *Die Schwelle* in `_m` |
| 7.11 | `_e` |
| 8 · 8.1 · 8.2 · 8.2.1 · 8.2.2 · 8.2.3 · 8.3 · 8.3.1 · 8.3.2 · 8.3.3 · 8.4 · 8.4.1 · 8.4.2 · 8.4.3 · 8.4.4 · 8.5 · 8.5.1 · 8.5.2 · 8.5.3 · 8.5.4 · 8.6 | `_t` |
| 8.5.5 | `_b` |
| 8.5.6 | `_m` |
| 9 · 9.1 · 9.2 · 9.3 · 9.4 · 9.5 | `_t`; der Hinweis *Bruch in der Gewichts-Historie* vom Kopf von §9 in `_m` |
| 10 · 10.1 · 10.2 · 10.3 · 10.4 · 10.5 · 10.6 | `_t` |
| 11 · 11.1 · 11.2 · 11.3 · 11.4 | `_b` |
| 12 · 12.1 · 12.2 · 12.3 · 12.4 | `_b` |
| 13 · 13.1 · 13.2 · 13.3 · 13.4 · 13.5 · 13.6 · 13.7 · 13.8 · 13.9 · 13.10 · 13.11 · 13.12 | `_b` |
| 14 · 14.1 · 14.2 · 14.3 · 14.4 | `_k` |
| 15 | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Messung vom 02.08.2026, Pfad, Vorgänger-Konzepte) | `_m` |
| bisherige Schlusszeile (*Konzept-Stand …*) | `_e` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Vision

Novas Langzeitgedächtnis ist heute eine Aggregat-Schicht: einzelne KZG-Einträge werden in Cluster zusammengefasst, zu einem destillierten LZG-Eintrag verdichtet und ihre Quellen anschließend gelöscht. Diese Architektur folgt einer Buchhaltungs-Metapher — viele Einzelposten kollabieren zu einem Saldo.

Phänomenologisch ist das fragwürdig. Menschliches Gedächtnis aggregiert nicht. Es vernetzt. Einzelne Episoden bleiben unterscheidbar, ihre Beziehungen zueinander werden gestärkt oder verblassen. „Anna" und „Geburtstag" und „Familie" sind nicht ein Eintrag, sondern drei Knoten mit Kanten zwischen sich. Eine neue Erinnerung an Annas Geburtstag aktiviert alle drei, und die Verbindung zwischen ihnen wird gestärkt.

Das Synapsen-Modell ersetzt die Aggregat-Schicht durch ein **assoziatives Netz**: Jeder ehemalige KZG-Eintrag wird als eigenständiger LZG-Knoten persistiert. Cluster sind keine eigenen Einträge mehr, sondern emergente Muster — Mengen von Knoten, deren Kanten stark genug sind, um sie als zusammengehörig erscheinen zu lassen. Verbindungen entstehen, wachsen mit Co-Aktivierung, verblassen mit Vernachlässigung, können getrennt werden ohne dass die Knoten verloren gehen.

Der ursprüngliche Auslöser des Clusterings — das Charakter-Hash-Profil aus einer überschaubaren Menge von LZG-Einträgen destillieren zu können — entfällt damit nicht. Die Destillation arbeitet künftig auf einer großen Knotenmenge, selektiert aber gezielt nach Knoten-Gewicht und Kanten-Stärke. Eine starke Verbindung zwischen „Anna" und „Vertrauen" mit hohem Knoten-Gewicht hat mehr Charakter-Aussage als hundert schwach verbundene Episoden. Dadurch wird die Aufgabe einfacher, nicht schwerer.

Das Modell ist phänomenologisch näher dran, strukturell sauberer, und macht Novas Gedächtnis sowohl reversibel als auch nachvollziehbar.

---

## 2. Leitprinzipien

### 2.1 Knoten erhalten, Aggregate vermeiden

Jeder vom Salienz-Knoten ins KZG geschriebene und später promotete Eintrag wird zu einem eigenständigen LZG-Knoten. Es gibt keine Verdichtung mehr auf Speicher-Ebene. Wenn ein destillierter Text gebraucht wird — etwa für den Enricher-Kontext oder das Charakter-Hash-Profil — entsteht er zur Abfragezeit aus selektierten Knoten plus ihren Kanten. Die Selektion gewichtet nach Knoten-Gewicht und Kanten-Stärke, nicht über Vollständigkeit.

### 2.2 Kanten typisieren, nicht nur zählen

Eine Verbindung zwischen zwei Knoten ist mehr als eine Zahl. Sie trägt eine Stärke, eine Schichten-Charakterisierung (wodurch ist diese Verbindung zustande gekommen — Entität, Timeline, Themen, Embedding?), und Metadaten aus ihrem Entstehungs-Moment (Cosine zum Bildungszeitpunkt, Anzahl der greifenden Schichten). Damit ist nicht nur abfragbar, *dass* zwei Erinnerungen verbunden sind, sondern auch *wie* und *warum*. Die Stärke selbst wird aus den aktuellen Knoten-Stärken und den eingefrorenen Schicht-Werten berechnet — sie folgt dem Leben der Knoten.

### 2.3 Erinnerung im Knoten, Assoziation in der Kante

Das Synapsen-Modell trennt zwei Substanzen scharf voneinander: Der Knoten trägt die Erinnerung — Inhalt, Embedding, Emotion, Themen, Entität-Referenzen, Timeline-Bezug. Er hat ein eigenes Leben mit Stärke, Aktivierung, Decay, Reaktivierung. Die Kante trägt die Assoziation — sie ist die strukturelle Spur dessen, dass zwei Erinnerungen über eine geteilte Schicht zusammengefunden haben. Sie hat keine eigene Substanz.

Daraus folgt: Die Kante kennt keinen eigenen Decay, keine eigene Verstärkung, keine eigene Aktivierungs-Häufigkeit. Sie ist ein abgeleiteter Cache der Knoten-Stärken-Konstellation und der bei Bildung eingefrorenen Schicht-Werte. Verfällt ein Knoten, verfallen seine Kanten implizit mit ihm. Verstärkt sich ein Knoten, werden seine Kanten neu berechnet. Eine alte Erinnerung an eine längst verblasste Verbindung lebt im Netz weiter durch den Knoten, der sie trug — aber die Verbindung selbst hat kein eigenständiges Gedächtnis, das hinter dem Knoten zurückbliebe.

Dieses Prinzip unterscheidet das Synapsen-Modell von einem klassischen Knowledge Graph, wo Information auf den Kanten liegt (Tripel: Subjekt — Prädikat — Objekt) und Kanten als eigenständige Träger von Bedeutung gelten. Für das Erinnerungs-Gedächtnis ist die Eigen-Substanz der Kante nicht nur überflüssig, sondern phänomenologisch falsch — eine Assoziation ohne erinnerten Inhalt ist keine Erinnerung.

### 2.4 Mehrere Anker-Schichten strukturieren das Netz

Kanten entstehen in einer geordneten Folge von Schichten, jede mit eigenem Charakter:

- **Entitäts-Schicht:** Zwei Knoten, die mindestens eine Entität teilen, werden verbunden. Geteilte Entität ist der stärkste Anker — „Anna" verbindet alle Erinnerungen über Anna.
- **Timeline-Schicht:** Knoten mit Bezug zum selben oder einem nahen Datum bekommen eine Kante. „Annas Geburtstag" und „Rosas Geburtstag eine Woche später" sind über die Zeit-Nähe verbunden, ohne dass sie inhaltlich vermischt werden.
- **Themen-Schicht:** Geteilte Themen zwischen Knoten erzeugen Kanten. Geburtstag verbindet beide Geburtstagskinder über die thematische Schiene — eine eigene Verbindung, neben der Timeline-Verbindung und unabhängig von ihr.
- **Embedding-Schicht:** Für Knoten ohne harte Anker (Reflexionen, Stimmungen) bilden Kanten sich über Cosine-Similarity mit hohem Schwellwert.

Die Schichten schließen sich nicht aus — eine Kante kann mehrere Schichten gleichzeitig tragen, was sie stärker macht. Wenn Schichten wegfallen (Themen verblassen, Timeline-Bezug wird irrelevant), kann die Kante über die verbleibenden Schichten weiter bestehen oder eigenständig decayen. Das ergibt ein realistisches Bild assoziativer Verschiebung: Eine Verbindung kann sich im Charakter wandeln, ohne ganz zu verschwinden. **Entität schlägt Embedding.**

### 2.5 Gläsernheit als Architekturziel

Jede Pipeline-Entscheidung wird protokolliert: was wurde gesagt, was hat welcher Node daraus gemacht, welcher Gesprächsvektor wurde gewählt und warum, welche Emotion wurde gefühlt, was hat Nova zum Nachdenken oder Fragen veranlasst. Das Gesprächs- und Node-Log ist die unterste Schicht, auf der Debugging und spätere Selbstreflexion aufbauen.

Cluster-Bildungs-Entscheidungen sind nicht Teil des Logs — das LZG ist sein eigener Zeuge. Knoten werden nie hart gelöscht, sondern bei Decay-Unterschreitung auf `aktiv = FALSE` gesetzt und bleiben bei Bedarf reaktivierbar. Kanten haben keinen eigenen aktiv/inaktiv-Zustand, sondern folgen dem Schicksal ihrer Knoten — eine Kante zu einem inaktiven Knoten wird durch die Sortier-Gewichtung im Lesepfad automatisch ausgeblendet. Damit ist die Cluster-Geschichte zur Abfragezeit aus dem LZG selbst rekonstruierbar.

### 2.6 Pragmatismus bei Performance

PostgreSQL ist leistungsfähig. Eine große Knotenmenge plus eine quadratisch wachsende Kantenmenge sind in absehbarer Zeit kein Problem. Wenn wir später an Performance-Grenzen stoßen, denken wir über Caching, Parallelität, temporäre Optimierungs-Tabellen nach. Bis dahin bauen wir das System klar und korrekt — und vertrauen darauf, dass Mooresches Gesetz und PostgreSQL uns Zeit lassen, später zu optimieren, wenn es nötig ist.

### 2.7 Das Netz lebt

Knoten sind keine statischen Datensätze. Sie verfallen mit Zeit (Decay), werden bei Aktivierung verstärkt (Reinforcement), kippen bei Unterschreitung einer Schwelle in einen inaktiven Zustand (`aktiv = FALSE`), und können bei erneutem Anstoß reaktiviert werden. Nichts wird hart gelöscht. Kanten leben durch ihre Knoten: Sie werden bei jeder relevanten Knoten-Änderung neu berechnet, sie verschwinden nur, wenn ein Knoten hart gelöscht wird (Cascade). Das Netz ist ein lebendes Gewebe — formal eine Graph-Struktur mit zeitabhängigen Knoten-Gewichten, phänomenologisch ein assoziatives Gedächtnis. Diese Eigenschaft macht das Netz später auch visualisierbar als Force-Directed-Graph (Stil Obsidian) und damit zu einem direkten Diagnose-Werkzeug für Entwicklung und Selbstreflexion.

---

## 3. Scope-Definition

### 3.1 Was dieses Konzept umfasst

**Im Umbau-Scope:**

- KZG→LZG-Promotion mit Kantenbildung (großer Umbau in `agents/promotion/agent.py`)
- Neue Tabellen `lzg_knoten` und `lzg_kanten` auf grüner Wiese (parallel zum bestehenden `langzeitgedaechtnis`)
- Decay-Logik für Knoten (`pixie-decay`) — Kanten folgen indirekt, kein eigener Decay-Pfad
- Reinforcement-Logik für Knoten (Reaktivierung im Schreibpfad), Cache-Aktualisierung für Kanten als Folgewirkung
- Gesprächs- und Node-Log (`gespraechs_log`) als Forensik-Schicht — parallel mit aufzubauen
- Charakter-Hash-Destillation auf der neuen Netz-Topologie

**Außerhalb des Scopes (pausiert während des Umbaus):**

- HumanGraph und CharacterGraph bleiben unangetastet
- Salienz-Knoten und KZG-Schreibpfad bleiben wie sie sind
- Pixie-Plugins
- Alle Pixie-Agenten außer dem Promotion-Agent
- Metakognition-Konzept
- Skills-System
- Alle Erweiterungen, die auf dem Memory-Kern aufsetzen

### 3.2 Was dieses Konzept ausdrücklich nicht ist — der Ausblick auf das Faktengedächtnis

Das Synapsen-Modell ist ein **Erinnerungs-Gedächtnis**. Es trägt Inhalte, Emotionen, Erlebnisse, Stimmungen und ihre Assoziationen untereinander. Die Information liegt im Knoten, die Assoziation in der Kante. Knoten leben mit Stärke, Decay und Reaktivierung; Kanten sind abgeleitete Spuren ohne eigene Substanz (siehe Leitprinzip 2.3).

Daneben existiert eine zweite, fundamental andere Gedächtnis-Modalität, die im aktuellen System als pausierte Plugin-Familie schlummert und nach dem LZG-Kernumbau in den Kern angehoben werden wird: das **Faktengedächtnis**. Heute leben Timeline, Notizen, Fakten und Dateien als stillgelegte Plugins. Im Zielzustand werden Timeline und Fakten als Kern-Strukturen aufgewertet, die im Synapsen-Stil mit Knoten und Kanten arbeiten — aber mit umgekehrter Substanz-Verteilung. Notizen, Dateien, Skills und ähnliche Werkzeug-Plugins bleiben außerhalb des Kerns.

**Vergleich der beiden Gedächtnis-Modalitäten:**

| Aspekt | Synapsen-LZG (dieses Konzept) | Faktengedächtnis (eigenes Konzept, später) |
|--------|-------------------------------|--------------------------------------------|
| **Was trägt der Knoten?** | Erinnerung — Inhalt, Embedding, Emotion, Themen, Bezüge | Entität — Person, Ort, Sache als Identifikator |
| **Was trägt die Kante?** | Assoziation — keine eigene Information | Relation — typisierte Beziehung (`ist_Schwester_von`, `mag`, `wohnt_in`) |
| **Wo lebt die Substanz?** | Im Knoten (Erlebnis, Emotion, Embedding) | In der Kante (Aussage, Beziehung) |
| **Knoten-Dynamik** | Stärke, Decay, Aktivierung, Reaktivierung | Statisch — Entität existiert oder existiert nicht |
| **Kanten-Dynamik** | Abgeleiteter Cache, kein Eigenleben | Eigene Stärke, eigenes Decay, eigene Aktivierung |
| **Suche** | Embedding-Anker + Spreading-Activation entlang Kanten | Entitäten-Lookup + Kanten-Traversierung |
| **Phänomenologie** | „Mir fällt ein...", „Ich erinnere mich...", Resonanz | „Ich weiß...", „Es ist so, dass...", Akte |
| **Charakter** | Episodisch — was wurde erlebt | Semantisch — was ist der Fall |

Die beiden Modalitäten sind über `entitaet_ids` und `timeline_id` verschränkt. Ein LZG-Knoten referenziert die Entitäten, die in ihm vorkommen; eine Entität im Faktengedächtnis erscheint in vielen LZG-Knoten als Referenz. Beide Systeme bleiben mechanisch getrennt, aber sie lesen einander.

**Sequenz im späteren Enricher** (nach Fertigstellung beider Kern-Systeme):

Der Enricher wird zum Orchestrator zweier Gedächtnis-Modalitäten. Eine User-Anfrage wie „Wann hat Anna Geburtstag?" durchläuft dann grob:

1. **Faktengedächtnis** liefert die Akte zu Anna — wer oder was ist das, welche Beziehungen sind bekannt, prägnante Fakten mit hoher Stärke.
2. **Synapsen-LZG** wird mit der Akte als Kontext-Anker konsultiert — welche Erinnerungen und Assoziationen sind mit Anna verbunden, welche emotionale Färbung, welche Resonanz?
3. **Responder** bekommt die kombinierte Sicht: faktische Antwort plus erinnernder Kontext. Nicht „Anna hat am 1. Juni Geburtstag" als nackte Auskunft, sondern eingebettet in das Bild dessen, *wer* Anna für den User ist.

Phänomenologisch genau so, wie ein Mensch über eine vertraute Person spricht: Fakten *und* Resonanz, nicht das eine ohne das andere. Reine Fakten wären ein Polizeibericht. Reine Resonanz wäre ein Gefühl ohne Anker.

Das Faktengedächtnis-Konzept entsteht als eigenes Konzeptpapier, sobald der LZG-Kern dieses Konzepts steht. Im aktuellen Konzept ist es nur Ausblick — keine Designentscheidungen, keine Schemata, keine Pixie-Logik für Fakten werden hier festgelegt.

---

> **§4 bis §13 stehen nicht in dieser Datei.** Die Ausarbeitung (§4–§10) steht in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md), Bauplan und Umstellung (§8.5.5, §11–§13) in [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md), die Messungen (der bisherige Kopf, Teile von §7.1a, §8.5.6, der Bruch-Hinweis aus §9) in [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md), die offenen Detail-Punkte §7.11 in [`novaberg-memory-synapsen_e.md`](novaberg-memory-synapsen_e.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

---

## 14. Wissenschaftliche Einordnung

Die Architektur des Synapsen-Modells ist aus phänomenologischer Beobachtung entstanden — aus der Frage, wie sich Erinnerung anfühlt, wie Assoziationen aufpoppen, wie Gefühle eine Erinnerung färben oder verblassen lassen. Sie ist nicht aus einer Theorie abgeleitet worden. Aber wenn man sie nachträglich gegen die Forschung der letzten Jahrzehnte aus Kognitionspsychologie, Neurowissenschaft, Konnektionismus und Knowledge-Engineering hält, zeigt sich: Das Konzept fügt sich in eine breite, bestätigende Tradition — mit gezielten, bewussten Differenzierungen, wo es sinnvoll erschien. Dieser Abschnitt dokumentiert diese Einordnung als Rückversicherung und als Anker für weitergehende Vertiefung.

### 14.1 Was die Forschung bestätigt

**Spreading Activation (Collins & Loftus 1975).** Das Fundament des Lesepfads. Allan Collins und Elizabeth Loftus formulierten 1975 in ihrem klassischen Artikel „A spreading-activation theory of semantic processing" (Psychological Review 82, 407–428) das bis heute prägende Modell semantischen Gedächtnisses: Konzepte sind als Knoten in einem Netzwerk repräsentiert, Beziehungen zwischen Konzepten als assoziative Pfade zwischen den Knoten. Wenn ein Teil des Netzwerks aktiviert wird, breitet sich Aktivierung entlang der Pfade zu verbundenen Bereichen aus, und die Stärke der sich ausbreitenden Aktivierung wird durch die Stärke der jeweiligen Verbindung bestimmt. Unser Punkt 8 (Lesepfad) ist eine direkte Übertragung dieses Modells: pgvector-Cosine-Treffer als Aktivierungs-Anker, Spreading-Activation entlang der LZG-Kanten mit cluster-abhängiger Sprung-Tiefe, gewichtete Sortierung des Aktivierungs-Pools. Auch die Idee, dass Typikalitäts-Effekte (gewichtete semantische Distanz) statt strenger Hierarchien das Gedächtnis organisieren, ist von Collins & Loftus übernommen.

**Hebbsche Plastizität (Hebb 1949).** Donald Hebb formulierte in „The Organization of Behavior" (Wiley 1949) das Grundprinzip neuronaler Verbindungsbildung, bis heute meist verkürzt als „neurons that fire together, wire together". Synaptische Verbindungen zwischen Neuronen stärken sich, wenn diese gemeinsam aktiviert werden — diese ko-aktivierte Verstärkung ist das neurobiologische Substrat assoziativen Lernens. Unser Schreibpfad (Punkt 7) ist eine softwareseitige Übertragung: Kanten entstehen, wenn beim Anlegen eines neuen Knotens die Schichten zu einem Kandidaten-Knoten greifen, also wenn neuer und alter Knoten *gemeinsam aktiviert werden* durch denselben externen Anstoß. Die Sperre gegen reines Lesen als Verstärkungs-Quelle (Leitprinzip 7.1, kein passives Wachsen) folgt ebenfalls Hebb: Ohne aktiven Anstoß keine synaptische Veränderung.

**Semantische Narrative Netzwerke und Edge-Weights als Cosine-Similarity.** Die jüngere Forschung zu naturalistischer Gedächtnis-Bildung (z.B. Lee et al., „Predicting memory from the network structure of naturalistic events", Nature Communications 2022) modelliert episodische Erinnerungen als Knoten in Netzwerken, deren Kanten-Gewichte aus der semantischen Ähnlichkeit der Knoten-Inhalte berechnet werden — über Embeddings wie Universal Sentence Encoder. Das deckt sich mit unserer Embedding-Schicht aus 7.3 und stützt die Designentscheidung, Cosine-Similarity als eine von vier Verbindungs-Schichten zu führen.

**Hybrid Vector + Graph als Architektur für LLM-Memory.** In der industriellen Praxis ringer LLM-Agenten (z.B. Zep, Memini, neuere Forschung zu agentenbasierten Memory-Systemen) hat sich die Kombination aus Vektor-Suche und Graph-Traversierung als robusteste Architektur etabliert: Vektor-Suche findet Anker-Knoten über breite semantische Ähnlichkeit, Graph-Traversierung erweitert von dort aus den Kontext über strukturelle Beziehungen. Unser Lesepfad-Aufbau aus 8.1 (Initial-Retrieval per pgvector) und 8.2 (Spreading-Activation entlang Kanten) folgt exakt diesem Muster.

### 14.2 Wo wir uns bewusst differenzieren

**Gerichtete statt bidirektionale Kanten.** Klassische Collins-Loftus-Modelle arbeiten mit bidirektionalen, ungerichteten Verbindungen. Wir haben gerichtete Kanten (A→B und B→A als zwei separate Datensätze mit eigenen Stärken), weil Assoziationen phänomenologisch asymmetrisch sind: „Anna erinnert mich an Schokolade" ist nicht symmetrisch zu „Schokolade erinnert mich an Anna". Diese Asymmetrie ist auch in neueren Knowledge-Graph-Implementierungen und Graph-Neural-Network-Architekturen Standard.

**Information im Knoten, Assoziation in der Kante.** Wir entscheiden uns explizit gegen das RDF-Triple-Modell, in dem Information *auf der Kante* liegt (Subjekt — Prädikat — Objekt). Im LZG ist der Knoten der semantische Träger, die Kante hat keine eigene Information. Das ist eine bewusste Designentscheidung, die das Erinnerungs-Gedächtnis vom Faktengedächtnis trennt (siehe 3.2). Für Erinnerungen ist die Eigen-Substanz der Kante phänomenologisch falsch — eine Assoziation ohne erinnerten Inhalt ist keine Erinnerung. Für Fakten ist die Eigen-Substanz der Kante phänomenologisch richtig — eine Beziehung *ist* die Information. Daher trennen wir die beiden Modalitäten architektonisch.

**Kante als abgeleiteter Cache, nicht als eigenständiger Träger.** Klassische konnektionistische Netze (Rumelhart & McClelland, McClelland & Rumelhart, „Parallel Distributed Processing", MIT Press 1986) modellieren Kanten-Stärken als eigenständig modulierbar — sie haben eigenes Lernen, eigenes Vergessen. Wir haben uns entschieden, die Kante an die Knoten zu binden: keine eigene Aktivierungs-Häufigkeit, kein eigenes Decay, kein eigenes Reinforcement (siehe Leitprinzip 2.3 und Punkt 7.9). Begründung: Im Erinnerungs-Gedächtnis ist die Assoziation nicht selbst eine Erinnerung, sondern eine strukturelle Konsequenz zweier Erinnerungen. Sie folgt deren Leben.

**Ein Graph für alles statt episodisch/semantisch getrennt.** Endel Tulving prägte 1972 die einflussreiche Trennung zwischen episodischem Gedächtnis (eigene Erlebnisse, zeitlich verortet) und semantischem Gedächtnis (Fakten, abstraktes Wissen). Spätere Modelle (z.B. HumemAI 2024) implementieren diese Trennung als zwei separate Graphen mit unterschiedlicher Mechanik. Wir gehen mittelfristig in dieselbe Richtung — Synapsen-LZG als episodisches System, Faktengedächtnis als semantisches System (siehe 3.2) —, halten sie aber konzeptionell sauberer auseinander: zwei eigenständige Gedächtnis-Modalitäten mit verschränkten Identifikatoren, nicht ein gemeinsames Modell mit Typ-Markierungen.

### 14.3 Was wir bewusst weglassen

**Multi-Timescale-Konsolidierung (Benna & Fusi 2016).** Marcus Benna und Stefano Fusi modellieren in „Computational principles of synaptic memory consolidation" (Nature Neuroscience 19, 1697–1706) Synapsen als gekoppelte schnelle und langsame Variablen, aus denen episodische Sensitivität, graduelle Konsolidierung und selektives Vergessen als Facetten eines einzigen Mechanismus hervorgehen. Aktuelle Memory-Architekturen für LLM-Agenten (z.B. Memini 2025) übernehmen dieses Modell. Wir lassen es bewusst weg, weil wir Konsolidierung über die Knoten-Dynamik abbilden (Decay, Reaktivierung, `aktiv`-Status) und die Kanten als abgeleiteter Cache fungieren. Eine spätere Erweiterung in Richtung Benna-Fusi wäre technisch denkbar, ist aber für die phänomenologischen Ziele nicht notwendig.

**Edge-Embeddings als Relations-Semantik.** Graph Neural Networks (z.B. R-GCN, CompGCN, jüngere Edge-Enhancement-Modelle) lernen für jede Kante einen Embedding-Vektor, der die Semantik der Beziehung trägt. Wir haben das nicht, weil unsere Kanten keine semantische Eigeninformation tragen sollen. Im späteren Faktengedächtnis können typisierte Relationen sehr wohl Embedding-Repräsentationen bekommen — das gehört dann ins separate Konzept.

**Spike-Timing-Dependent Plasticity (STDP).** Verfeinerung der Hebbschen Regel auf Millisekunden-Genauigkeit (Bi & Poo 1998). Für unser Software-Modell irrelevant, weil wir nicht in biologischer Zeit operieren — der externe Anstoß zur Kantenbildung ist ein diskretes Promotion-Ereignis, kein zeitlich nahe getaktetes Neuronen-Feuern.

### 14.4 Eigene Beiträge

Wo das Synapsen-Modell über die zitierte Forschung hinausgeht oder eigene Akzente setzt:

- **Schicht-Faktor und Tiefe-Faktor als zweistufige Wertigkeit** (Punkt 7.4). Statt einer einzigen Verbindungs-Stärke verwenden wir eine statische Schicht-Wertigkeit (welche Art von Verbindung ist wertvoll?) und einen dynamischen Tiefe-Faktor (wie tief greift sie im Einzelfall?). Die Trennung in zwei orthogonale Dimensionen ist in der zitierten Literatur nicht explizit so formuliert.
- **Asymmetrische Sinus-Geometrie für Kanten-Initial-Stärke** (Punkt 5.1). Die nach unten flachere und nach oben steilere Anhebung der schwächeren Knoten-Stärke ist eine eigene Wahl, die schwache Erinnerungen vor Erdrückung durch starke Partner schützt.
- **Cluster-abhängige Spreading-Tiefe** (Punkt 8.2.1). Die Sprung-Tiefe der Spreading-Activation wird aus Novas Gesprächsraum abgeleitet (`CLUSTER_ENRICHER_SPRUENGE`). „Fokussiertes Denken" bei Werkstatt-Modus, „freies Schweifen" bei Glut. Diese Verknüpfung von Gesprächs-Modus und Retrieval-Breite ist eine Eigenentwicklung aus dem GV-Konzept.
- **Plutchik-Sektor-Affinität als Sortier-Faktor** (Punkt 8.3.1). Erinnerungen mit ähnlicher emotionaler Färbung wie Novas aktueller Zustand werden im Lesepfad bevorzugt. Diese Brücke zwischen Affekt-Theorie (Plutchik 1980) und Spreading-Activation ist eine Eigenentwicklung.
- **Trennung Erinnerungs-Gedächtnis vs. Faktengedächtnis als zwei verschränkte Modalitäten** (Punkt 3.2). Tulvings episodisch/semantische Trennung wird hier nicht als interner Typ eines einzigen Systems modelliert, sondern als zwei mechanisch unabhängige Systeme mit verschränkten Identifikatoren. Die Substanz-Asymmetrie (Information im Knoten vs. Information in der Kante) ist die architektonische Begründung dafür.

---

## 15. Verwandte Dokumente

- `novaberg-kzg-liberalisierung_k.md` (Chat 64) — Vorgänger-Konzept, KZG-Liberalisierung und heutige Cluster-Promotion
- `novaberg-pixie-promotion.md` — heutige Promotion-Implementierung (wird durch den Umbau abgelöst)
- `novaberg-mem-lzg.md` — heutige LZG-Beschreibung (wird durch den Umbau abgelöst)
- `novaberg-mem-kzg.md` — KZG bleibt unverändert
- `novaberg-memory.md` — übergreifendes Memory-Konzept, insbesondere Kapitel 11.4 zur Cluster-Gravitations-Tabelle
- `novaberg-convention-magneten.md` — Entitäten und Timeline als Magnet-Felder
- `novaberg-gv-strategie_k.md` — Gesprächsvektor-Konzept, Cluster und Sprung-Geschwindigkeit
- `novaberg-pixie-character-hash.md` — Charakter-Hash-Destillation (Pixie-Pfad, außerhalb des LZG-Kerns)
- `novaberg-backlog.md` Epic „Memory-Promotion-Korrektur" (Chat 75) — M3b und M5 werden durch diesen Umbau anders gelöst oder ersetzt
