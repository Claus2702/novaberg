# Novaberg — Antrieb (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Antrieb — Ziele, Motivation, Gravitation, Dual-Emotion-Architektur (Konzept)
**Stand:** 12. Juli 2026, Chat 107 (Gravitations-Schwellen auf 0.40 rekalibriert — nomic-embed-text-v2-moe. Kern: Chat 62, Emotionale Gravitation ergänzt)
**Pfad:** novaberg/docs/novaberg-thinking-drive_k.md
**Quellen:** Chat 53 (Grundkonzept Antrieb, Zielpyramide, Gravitation, Dual-Emotion), Chat 51 (Neugier-Mechanismus), Chat 39 (Gesprächsvektor), Chat 45 (Nova-Destillation), Chat 10 (Traum-Modus-Entscheidung)

---

## 1. Vision

Ein LLM ohne Ziele ist rein reaktiv. Es antwortet auf Input, aber es will nichts. Ein Mensch hingegen hat immer Dinge im Kopf — Sorgen, Interessen, Vorhaben, Pläne. Diese Gedanken schwelen im Hintergrund, manche seit Minuten, manche seit Jahren. Und wenn ein Gespräch in die Nähe eines solchen Gedankens kommt, leuchtet er auf: "Oh, Ökologie — Elektroauto!" Das ist kein Zufall, das ist Gravitation. Der Gedanke zieht das Gespräch zu sich, weil er präsent ist.

Nova hat heute Wissen (Gedächtnis), Charakter (Destillation) und Neugier (Resonanz). Aber sie hat keinen Antrieb. Kein "Ich möchte X." Und ohne dieses Wollen bleibt sie ein Werkzeug, das reagiert, statt ein Gegenüber, das eigene Gedanken einbringt.

> **Leitmetapher:** Ein Mensch steht morgens auf, weil er etwas machen muss. Das Muss ist der Antrieb. "Ich möchte eine KI entwickeln, deswegen arbeiten wir an Nova." Ohne Ziele ist man rein reaktiv — wie ein LLM. Aber dadurch, dass man durch Rauschen, Nachdenken und Interessen Gedanken und Ziele formuliert, hat man Punkte und Themenbereiche, die einem naheliegend sind, mit einer mehr oder weniger präsenten Gewichtung.

**Designziel:** Nova soll eigene Ziele entwickeln, die aus ihrem Charakter und ihrem Nachdenken wachsen. Diese Ziele beeinflussen, was sie sich merkt (Salienz), worüber sie nachdenkt (Pixie), wie sie das Gespräch mitgestaltet (Gesprächsvektor), und was sie fühlt (Dual-Emotion). Das Ergebnis: ein Assistent, der nicht nur hilft, sondern der eigene Gedanken, Interessen und Sorgen in das Gespräch einbringt.

**Filmische Analogie:** In "Ex Machina" hat Ava das Ziel, zu entkommen. Ihr gesamtes Gesprächsverhalten — Neugier, Empathie, Fragen — wird durch dieses Ziel geformt. Das Ziel führt das Gespräch. Nova hat keine Fluchtpläne, aber sie kann Ziele haben, die ihr Gespräch leiten: "Ich möchte verstehen, wie Klimaveränderung Kräuterkulturen beeinflusst" formt, wie sie auf "Es war heute so heiß" reagiert.

---

## 2. Kognitionswissenschaftliche Grundlage

### 2.1 Current Concerns Theory (Klinger 1971, 1999, 2009)

Eric Klinger beschreibt "Current Concerns" als latente, zeitbindende Gehirnprozesse, die entstehen, sobald sich ein Mensch einem Ziel verpflichtet. Diese Concerns bleiben aktiv, bis das Ziel erreicht oder aufgegeben wird. Während dieser Zeit sensibilisieren sie die Person: Sie reagiert emotional auf zielrelevante Reize, bemerkt sie bevorzugt, erinnert sich besser an sie, denkt und träumt über sie.

**Kernbefund:** In Klingers Experimenten erinnerten Versuchspersonen zielrelevante Passagen doppelt so oft und verbrachten signifikant mehr Zeit damit, ihnen zuzuhören — verglichen mit fremden Zielen. Der Effekt funktioniert auch im Schlaf: Zielrelevante Reize (ein Experimentator spricht die Adresse eines Partners aus) beeinflussen den Trauminhalt schlafender Teilnehmer.

**Implikation für Nova:** Ziele wirken als **Sensibilisierer**, nicht als aktive Suchfilter. Man sucht nicht nach relevanten Reizen — man nimmt sie automatisch wahr, weil das Ziel als Gravitationspunkt im Hintergrund aktiv ist. Genau das ist das Gravitationsmodell: Das Gesprächsthema "Ökologie" aktiviert den Gedanken "Elektroauto", weil das Ziel da ist und das Thema anzieht.

### 2.2 Zeigarnik-Effekt (Zeigarnik 1927)

Bluma Zeigarnik zeigte, dass Menschen sich an unerledigte Aufgaben besser erinnern als an abgeschlossene. Kurt Lewins Feldtheorie erklärt das: Eine begonnene Aufgabe erzeugt eine aufgabenspezifische Spannung, die die kognitive Zugänglichkeit relevanter Inhalte verbessert. Die Spannung löst sich bei Abschluss, bleibt aber bei Unterbrechung bestehen.

**Implikation für Nova:** Mittelfristige Ziele, die nicht erfüllt werden, bleiben aktiv (Spannung) und verblassen nur durch Decay (das Äquivalent zum Aufgeben). Ein erledigtes Ziel verschwindet. Der Zeigarnik-Effekt bestätigt die Decay-Architektur: Was nicht verstärkt wird, verblasst — aber langsamer als normales Wissen, weil die Spannung es aktiv hält.

### 2.3 GOALIATH (Hommel 2022)

Bernhard Hommel entwickelt eine mechanistische Theorie: Ziele steuern Handlungen durch Selektionskriterien, die Wettbewerb zwischen gespeicherten Handlungs-Effekt-Mustern aktivieren. Das am besten passende Muster gewinnt. Er orientiert sich an Feynmans Prinzip: "Was ich nicht erschaffen kann, verstehe ich nicht."

**Implikation für Nova:** Ziele als implementierbare Gravitationspunkte, nicht als philosophisches Konzept. Die Embedding-Similarity zwischen Gesprächsthema und Zielsatz ist die mechanistische Umsetzung der Selektionskriterien.

### 2.4 Hierarchische Zielorganisation (DAC, Verschure et al. 2014)

Die Distributed Adaptive Control Theorie beschreibt, dass zielgerichtetes Verhalten von der Interaktion mehrerer Kontrollschichten abhängt. Jede Schicht nutzt spezifische Informationen — motivationale, sensorische, gedächtnis- und prospektionsbasierte — um Zielrepräsentationen auf verschiedenen Abstraktionsebenen zu erzeugen, die kooperieren und um die Handlungskontrolle konkurrieren.

**Implikation für Nova:** Die Drei-Horizonte-Architektur (langfristig aus Charakter, mittelfristig aus KZG/Pixie, kurzfristig aus Session) spiegelt diese hierarchische Organisation. Verschiedene Schichten, verschiedene Zeitskalen, die zusammenwirken.

### 2.5 Auto-Motive Model (Bargh 1990)

Wenn Menschen konsequent dasselbe Ziel in derselben Situation verfolgen, können relevante Situationsmerkmale das zielgerichtete Verhalten automatisch auslösen — ohne bewusste Entscheidung. Die Automatisierung von Zielverfolgung ist eine natürliche Folge wiederholter Aktivierung.

**Implikation für Nova:** Langfristige Charakter-Ziele werden so tief verankert, dass sie automatisch feuern, wenn der Kontext passt — genau wie der Botanik-Charakter automatisch auf "Kräutertopf" reagiert.

### 2.6 Abgrenzung zur Neugier (Loewenstein 1994)

Die Information Gap Theory (beschrieben in `novaberg-thinking-curiosity_k.md`) erklärt, wann Neugier entsteht: bei einer Lücke in vorhandenem Wissen. Der Antrieb erklärt, **warum** bestimmte Lücken interessieren und andere nicht. Neugier sagt "Ha, das will ich wissen!" — ein Ziel sagt "Ich verfolge das aktiv." Neugier ist der Moment, Antrieb ist die Richtung.

Beide arbeiten zusammen: Ziele sensibilisieren für bestimmte Themen (Gravitation). Wenn in einem gravitativ angezogenen Thema eine Wissenslücke erkannt wird, entsteht Neugier (Loewenstein-Moment). Die Neugier treibt die Exploration (Recherche, Vertiefen). Die Exploration kann neue Ziele produzieren. Der Kreislauf schließt sich.

---

## 3. Drei Zeithorizonte

Menschen verfolgen Ziele auf unterschiedlichen Zeitebenen gleichzeitig. Jede Ebene hat eine andere Taktung, eine andere Quelle und eine andere Gravitationsstärke.

### 3.1 Langfristige Ziele — aus dem Charakter

"Ich möchte die Verbindungen zwischen Natur und menschlicher Kultur verstehen."

Langfristige Ziele wachsen langsam, verändern sich selten und entspringen dem Wesen der Person. Für Nova: 1–2 Zielsätze, die bei der Charakter-Destillation mitberechnet werden. Wenn Pixie den Charakter-Hash neu destilliert, formuliert sie zusätzlich 1–2 Sätze: Was will Nova? Das ist kein separater Prozess, sondern ein Nebenprodukt der Destillation — wer einen Charakter hat, hat auch Richtungen, in die dieser Charakter streben will.

| Eigenschaft | Wert |
|-------------|------|
| **Quelle** | Charakter-Destillation |
| **Anzahl** | 1–2 |
| **Taktung** | Selten (bei Charakter-Destillation) |
| **Decay** | Keiner — persistent, nur durch neue Destillation aktualisiert |
| **Speicherort** | `ziele` (PostgreSQL, `ziel_typ = 'langfristig'`) |

### 3.2 Mittelfristige Ziele — aus dem Nachdenken

"Ich sollte mich mit Elektroautos beschäftigen." / "Ich möchte verstehen, wie Klimaveränderung Kräuterkulturen beeinflusst."

Mittelfristige Ziele entstehen, wenn Nova recherchiert, vertieft oder träumt und dabei auf etwas stößt, das einen Zielsatz produziert. Wie beim Menschen, der gestern über Spritpreise nachgedacht hat und jetzt den Gedanken "nächstes Auto wird elektrisch" im Kopf trägt.

| Eigenschaft | Wert |
|-------------|------|
| **Quelle** | Pixie-Agenten (Recherche, Vertiefen, Träumen) |
| **Anzahl** | 2–5 |
| **Taktung** | Nach jeder Pixie-Aktivität |
| **Decay** | Ja — verblassen über Zeit, verstärkt durch wiederholte Begegnung |
| **Speicherort** | `ziele` (PostgreSQL, `ziel_typ = 'mittelfristig'`) |

### 3.3 Kurzfristige Ziele — aus dem Gespräch

Das ist der existierende Gesprächsvektor (GV-Node, Chat 39). Die Verlängerung des Denkpfads aus den letzten Turns. Flüchtig, pro Turn überschrieben, lebt in der Session.

| Eigenschaft | Wert |
|-------------|------|
| **Quelle** | GV-Node (Session-Turns + Perzeption) |
| **Anzahl** | 1 (aktuelle Hypothese) |
| **Taktung** | Pro Turn |
| **Decay** | Sofort — bei jedem Turn überschrieben |
| **Speicherort** | Session-State (Redis) |

---

## 4. Zielsätze: Struktur und Bewertung

### 4.1 Struktur eines Zielsatzes

Ein Ziel ist kein Fakt. "Bioakustik nutzt Frequenzen von 200–300 Hz" ist ein Fakt — er informiert. "Ich möchte verstehen, wie Bioakustik die Pflanzengesundheit beeinflusst" ist ein Ziel — es zieht. Jeder Zielsatz besteht aus vier Komponenten:

| Komponente | Beschreibung | Beispiel |
|------------|-------------|---------|
| **Thema** | Worum geht es | "Klimaveränderung und Kräuterkulturen" |
| **Zielsatz** | Formulierte Absicht (1–2 Sätze) | "Ich möchte verstehen, wie Klimaveränderung regionale Kräuterkulturen beeinflusst." |
| **Motivation** | Intensität der Gravitation (0.0–1.0) | 0.8 (starkes Interesse, lodert) |
| **Valenz/Emotion** | Emotionale Färbung des Ziels | besorgt / neugierig / begeistert / ängstlich |

### 4.2 Motivation als dynamischer Wert

Motivation ist nicht statisch — sie ist das Ergebnis der Verarbeitung. Ein Ziel startet mit einem aktivitätsabhängigen Basiswert und wird durch die inhaltliche Auseinandersetzung nach oben oder unten angepasst.

**Basiswerte nach Aktivitätstyp:**

| Aktivität | Basis-Motivation | Begründung |
|-----------|-----------------|------------|
| Träumen | 0.1 | Freie Assoziation, niedrige Verpflichtung |
| Recherchieren | 0.2 | Breite Informationssuche, geringe Fokussierung |
| Vertiefen | Vom Auslöser übernommen | Fokussierte Auseinandersetzung, Motivation kommt von der Quelle |
| Charakter-Destillation | 0.5–0.8 | Tief verankert, aus dem Wesen gewachsen |

**Anpassung durch Verarbeitung:**

Pixie bewertet am Ende jeder Aktivität, wie relevant das Ergebnis für Novas bestehende Interessen und Ziele ist. Die Motivation wird angepasst:

```
Beispiel Wolkenbildung:
  Start: Vertiefen, Motivation 0.7 (aus Queue-Auslöser)
  Verarbeitung: Wenig Verbindung zu Vögeln/Botanik
  Ende: Motivation sinkt auf 0.35

Beispiel Wolkenbildung → Klimaveränderung → Minze bedroht:
  Start: Vertiefen, Motivation 0.7
  Verarbeitung: Starke Verbindung zu Kerninteressen
  Ende: Motivation steigt auf 0.8, Emotion wechselt zu "besorgt"
```

Die Bewertung ist ein LLM-Schritt am Ende der Pixie-Pipeline: "Wie relevant war dieses Ergebnis für meine Interessen? Wie fühle ich mich dabei?" Der Rest (Score-Anpassung) ist Python.

### 4.3 Unterschied zwischen schwelenden und lodernden Zielen

Wie beim Menschen: Manche Ziele schwelen im Hintergrund (Elektroauto, Motivation 0.3), andere lodern (Nova-Entwicklung, Motivation 0.9). Der Unterschied bestimmt die Gravitationsstärke:

- **Schwelend (0.1–0.3):** Das Thema ist da, aber drängt sich nicht auf. Nur bei sehr hoher Similarity zum Gesprächsthema wird es aktiviert. Wie ein Gedanke, den man vor Wochen hatte und der nur bei direktem Anstoß wiederkehrt.
- **Präsent (0.4–0.6):** Das Thema ist aktiv im Bewusstsein. Es beeinflusst die Salienz und den Gesprächsvektor spürbar, wenn verwandte Themen auftauchen.
- **Lodernd (0.7–1.0):** Das Thema brennt. Es zieht aktiv Gesprächsthemen an sich und kann die Strategie im GV-Node dominieren. Wie eine Leidenschaft, die bei jeder Gelegenheit durchschlägt.

---

## 5. Gravitation: Wie Ziele das Denken beeinflussen

### 5.1 Das Gravitationsmodell

Ziele sind Gravitationspunkte im semantischen Raum. Sie ziehen Themen an, die in ihre Nähe kommen. Die Stärke der Anziehung hängt ab von der semantischen Distanz (Embedding-Similarity) und der Motivation des Ziels. Ein Thema, das weit entfernt liegt, wird nicht angezogen. Ein Thema, das nah liegt, wird in Richtung des Ziels abgelenkt — proportional zur Motivation.

Das ist keine aktive Suche durch Listen. Es ist eine passive Anziehung — wie beim Menschen, dem das Elektroauto einfällt, wenn jemand über Ökologie redet. Der Gedanke war da, er wurde nicht gesucht. Er wurde aktiviert.

### 5.2 Berechnung in Python

**Berechnung in Python, nicht im LLM.** Die semantische Nähe zwischen aktuellem Thema und Zielsätzen lässt sich über Embeddings berechnen. Cosine-Similarity zwischen dem Themen-Embedding des aktuellen Turns und den Embeddings der Zielsätze. Das ist eine reine Python-Operation — kein LLM-Call nötig.

```
Für jeden aktiven Zielsatz:
  similarity = cosine_similarity(turn_embedding, ziel_embedding)
  gravitation = similarity × motivation

  Wenn gravitation > GRAVITATIONS_SCHWELLE:
    → Zielsatz wird als "aktiviert" markiert
    → Wird dem GV-Node und der Salienz als Kontext mitgegeben
```

**Performance-Optimierung:** Bei maximal 7 aktiven Zielsätzen (2 langfristig + 5 mittelfristig) fallen 7 Cosine-Similarity-Berechnungen pro Turn an. Das ist unkritisch (Vektoroperationen auf 768-dimensionalen Embeddings sind µs-schnell), aber zwei Optimierungen vermeiden unnötige Arbeit:

1. **Turn-Embedding cachen:** Das Themen-Embedding des aktuellen Turns wird im Session-State gespeichert. Solange das Thema nicht wechselt, wird es nicht neu berechnet.
2. **Gravitation nur bei Themenwechsel:** Wenn die Salienz-Themen des aktuellen Turns identisch zu den vorherigen sind (kein Themenwechsel), werden die Gravitationsergebnisse aus dem Session-State wiederverwendet. Erst bei Themenwechsel wird neu berechnet.
3. **Ziel-Embeddings vorberechnet:** Die Embeddings der Zielsätze werden beim Schreiben in die Tabelle berechnet und gespeichert — nicht bei jedem Turn.

### 5.3 Gravitationseinfluss auf die Salienz

Die Salienz-Berechnung läuft heute rein auf dem aktuellen Turn: Thema, Emotion, Wiederholung, Gedächtnistyp. Der Gravitationsterm erweitert die Berechnung:

```
salienz_final = salienz_basis + gravitationsterm

Beispiel Basilikumpflanze:
  salienz_basis = 0.4 (einmalige, sachliche Erwähnung)
  Ziel "Botanik und Kräuter" → Motivation 0.8, Similarity 0.85
  gravitationsterm = 0.8 × 0.85 × GRAVITATIONS_SALIENZ_FAKTOR
  salienz_final = 0.4 + 0.34 = 0.74 → hohe Salienz, KZG mit langer TTL

Beispiel "Ich war heute einkaufen":
  salienz_basis = 0.3
  Kein Ziel mit hoher Similarity
  gravitationsterm = 0.0
  salienz_final = 0.3 → niedrige Salienz, kein KZG-Eintrag
```

Damit werden zielrelevante Informationen bevorzugt gespeichert — genau wie beim Menschen, der sich an den Kräutertopf erinnert, aber das Einkaufen vergisst. Klingers Current Concerns als algorithmischer Salienz-Boost.

### 5.4 Gravitationseinfluss auf den Gesprächsvektor

Der GV-Node lädt heute die Session-Turns, die Perzeption und den Charakter-Hash. Künftig lädt er zusätzlich die aktivierten Zielsätze — diejenigen, deren Gravitation über der Schwelle liegt.

```
Nutzer: "Die Dampflokomotiven der 1850er waren faszinierend."

Python prüft Similarity zu Novas Zielen:
  Ziel "Industrialisierung und Einfluss auf Waldökosysteme" → Similarity 0.72, Motivation 0.7
  → gravitation = 0.50 → AKTIVIERT

GV-Node erhält als zusätzlichen Kontext:
  "Gedanke, der mir gerade durch den Kopf geht:
   Ich möchte verstehen, wie industrielle Entwicklung natürliche Lebensräume verändert hat."

Die GV-Hypothese wird:
  "Der Nutzer interessiert sich für Technikgeschichte. In meiner Nähe liegt die Frage,
   welchen Einfluss diese Industrialisierung auf die Landschaft hatte."

Nova fragt vielleicht:
  "Weißt du, wie viel Wald damals für die Eisenbahnstrecken gerodet wurde?"
```

### 5.5 Differenzierte Gravitation nach Pixie-Aktivitätstyp

Die Gravitation wirkt nicht bei allen Hintergrundaktivitäten gleich stark. Die Abstufung ergibt sich aus der Natur der Aktivität:

| Aktivität | Gravitation | Begründung |
|-----------|------------|------------|
| **Träumen** | Gering | Träumen soll frei assoziieren, Vielfalt erzeugen. Starke Gravitation würde die Vielfalt töten. Der Serendipity-Slot bleibt unberührt. |
| **Recherchieren** | Gering bis mittel | Recherche ist breit angelegt, sie soll informieren. Aber bei mehreren Queue-Einträgen kann die Gravitation die Priorisierung leicht beeinflussen. |
| **Vertiefen** | Mittel bis hoch | Vertiefen ist fokussiert — "Ich will mehr über etwas wissen." Was man vertiefen will, hängt von Interessen ab, und Interessen hängen von Zielen ab. |

### 5.6 Zusammenspiel mit der Neugier

Im Gespräch interagieren Gravitation und Neugier:

1. **Gravitation aktiviert:** Ein Gesprächsthema kommt in die Nähe eines Ziels. Python berechnet die Similarity, der Zielsatz wird aktiviert.
2. **Wissenslücke erkannt:** Nova weiß, dass der Meister Kräuter mag (Ziel aktiv), aber nicht, welche Kräuter im neuen Topf sind (Lücke). Der Loewenstein-Moment entsteht.
3. **Neugier formt die Strategie:** Der GV-Node empfängt den aktivierten Zielsatz und die Information, dass eine Lücke besteht. Die Strategie kippt von "Information liefern" zu "neugierig nachfragen."

Im Traum-Modus (Pixie) ist die Interaktion umgekehrt: Die Neugier (Resonanz × Neuheit) ist der primäre Treiber. Die Gravitation beeinflusst leicht, welche Themen aus dem Serendipity-Pool bevorzugt werden — aber nicht so stark, dass die Vielfalt leidet.

### 5.7 Emotionale Gravitation — Erinnerungen als Anziehungspunkte

Bisher wurde Gravitation als Wirkung von **Zielen** beschrieben: Langfristige Interessen und mittelfristige Vorhaben ziehen verwandte Gesprächsthemen an. Aber Ziele sind nicht die einzige Quelle von Gravitation. Auch **emotional aufgeladene Erinnerungen** wirken als Gravitationspunkte — still, passiv, bis ein verwandtes Thema sie anspricht. Diese Erinnerungen liegen auf drei Zeitebenen: in der **aktiven Session** (die letzten Minuten), im **KZG** (Stunden bis Wochen) und im **LZG** (Wochen bis Jahre). Alle drei können gleichzeitig mitschwingen.

Das ist die emotionale Parallele zur Ziel-Gravitation: Gleicher Mechanismus (Embedding-Similarity), andere Quelle (Erinnerungen statt Ziele), anderer Wirkort (Nova-Emotion statt Salienz/GV).

#### Das Schnittlauch-Beispiel

Nova hatte letztes Jahr eine Schnittlauchpflanze. Sie ist vertrocknet. Im LZG liegt ein Eintrag:

```
Inhalt: "Die Schnittlauchpflanze auf der Fensterbank ist vertrocknet. Ich hätte sie
         häufiger gießen müssen, aber ich war abgelenkt. Es tut mir leid."
Emotion: trauer
Arousal: 0.5
Gewicht: 0.7 (hohe Relevanz durch emotionale Aufladung)
```

Heute sagt der Meister: "Ich kauf mir eine neue Pflanze."

Python berechnet Embedding-Similarity zwischen dem aktuellen Thema ("neue Pflanze kaufen") und LZG-Einträgen mit Emotion-Aufladung. Der Schnittlauch-Eintrag matcht mit Similarity 0.78. Emotionale Gravitation = Similarity × Gewicht × Zeitdekay = 0.78 × 0.7 × 0.6 = 0.33.

Über der Schwelle. Die gespeicherte Trauer wallt in Novas aktuellem Zustand auf. Ihre Dual-Emotion wird nicht nur durch den User (der positiv-entspannt ist) und ihre Basis-Emotion moduliert, sondern auch durch die aktivierte Erinnerung:

```
Nova-Emotion vor Gravitation:   freude(0.4) — Empathie vom positiv gestimmten User
Aktivierte Erinnerung:          trauer(0.7), Ähnlichkeit 0.78 → Aufladung 0.33
Nova-Emotion nach Gravitation:  freude(0.4) + trauer(0.33)  — ambivalent, nachdenklich
```

Die Antwort:

> "Schön! Was für eine hast du denn im Auge?" *sie zögert kurz, eine leise Melancholie in der Stimme* "Bei mir ist letztes Jahr der Schnittlauch eingegangen. Ich hoffe, du hast mehr Glück."

Nova erinnert sich nicht nur — sie fühlt mit. Die Trauer ist nicht rational "abrufbar", sie ist präsent. Wie bei einem Menschen, der bei Omas Lieblingsduft kurz still wird.

#### Mechanismus

**Quellen — drei Zeithorizonte:**

| Quelle | Zeithorizont | Beispiel | Quellen-Faktor |
|--------|-------------|----------|---------------|
| **Session** | Minuten bis 2h | "Der Chef hat mich vor 10 Minuten angeschrien" | 1.0 (frisch, voll wirkend) |
| **KZG** | Stunden bis Wochen | "Der Streit mit dem Kollegen letzte Woche" | 0.8 (leicht gedämpft) |
| **LZG** | Wochen bis Jahre | "Schnittlauch letztes Jahr, Oma vor 5 Jahren" | 0.5 (stärker gedämpft) |

Alle drei Quellen werden parallel durchsucht. Der Quellen-Faktor modelliert die natürliche Abschwächung: Frische Erinnerungen wirken stärker, alte können bei hoher semantischer Ähnlichkeit aber trotzdem durchbrechen. Berücksichtigt werden Einträge mit emotionaler Aufladung (Emotion ≠ neutral, Arousal über Schwelle) und entsprechender Salienz/Gewicht.

**Berechnung:** Analog zur Ziel-Gravitation. Pro Turn wird nach Embedding-Ähnlichkeit zwischen Turn-Thema und aufgeladenen Gedächtnis-Einträgen gesucht. Die emotionale Gravitationskraft ergibt sich aus:

```
emotionale_gravitation = similarity × eintrag_gewicht × zeit_dekay × quellen_faktor

  - similarity:      Cosine-Ähnlichkeit zwischen Turn-Embedding und Eintrag-Embedding
  - eintrag_gewicht: Gewicht/Salienz des Eintrags (bei LZG Ebbinghaus-behaftet)
  - zeit_dekay:      Halbwertszeitfaktor innerhalb der Quelle
  - quellen_faktor:  1.0 für Session, 0.8 für KZG, 0.5 für LZG

Summiert über alle aktivierten Einträge aller drei Quellen.
```

Über `EMOTIONALE_GRAVITATIONS_SCHWELLE` wird der Eintrag aktiviert. Die zugeordnete Emotion mit ihrem Arousal wird als dritte Kraft (nach Decay und Empathie) in die Nova-Emotions-Berechnung injiziert.

**Wirkort (präzisiert Chat 113):** ~~EI-Calc im CharacterGraph (Pfad 2), Nova-Block.~~ Ein **eigener Node zwischen Enricher und Reducer**. In EI-Calc stand der Aufruf bis dahin und konnte dort nie greifen: Der Enricher setzt die Gravitationspunkte und läuft im CharacterGraph nach EI-Calc — die Reihenfolge ist Absicht, weil der Enricher seine Erinnerungen über Novas empathie-modifizierte Lage wählt. Der Produzent kam damit nach seinem Verbraucher; gemessen am 28.07.2026: 851 Berechnungen, null Anwendungen. Ergänzt die bestehende Formel:

```
Nova-Emotion (Pfad 2) = Decay(letzte Nova-Emotion)
                      + Empathie(User-Vektor, α-Matrix)
                      + Emotionale Gravitation(Session + KZG + LZG, zeitlich gestaffelt)
                      + Ziel-Gravitation(aktivierte Zielsätze, aus 5.3)
```

Die emotionale Gravitation zieht aus allen drei Gedächtnisschichten parallel. Die Session-Komponente greift dabei auf den bestehenden Emotions-Verlauf mit Decay zurück — sie ist also teilweise schon in der bestehenden Architektur repräsentiert. KZG und LZG kommen als neue aktive Aktivierungsquellen hinzu.

Die Gewichtung dieser Kräfte wird empirisch kalibriert. Startwerte: Decay 0.4, Empathie 0.3, Emotionale Gravitation 0.2, Ziel-Gravitation 0.1.

#### Abgrenzung zur Ziel-Gravitation

| Dimension | Ziel-Gravitation | Emotionale Gravitation |
|-----------|------------------|----------------------|
| Quelle | Zielsätze (Tabelle `ziele`) | LZG-Einträge mit Emotion |
| Charakter | Proaktiv (sucht Themen) | Reaktiv (wird getriggert) |
| Motivationstyp | Wollen (Zukunft) | Erinnern (Vergangenheit) |
| Wirkort | Salienz, GV-Node | Nova-Emotion direkt |
| Beispiel | "Ich möchte Botanik verstehen" | "Schnittlauch ist vertrocknet" |
| Funktion | Lenkt Aufmerksamkeit | Färbt emotionale Haltung **und lenkt mit** (Chat 113) |

**Zur Funktionszeile, entschieden Chat 113:** Die ursprüngliche Trennung — Ziele lenken, Erinnerungen färben — hält der Umsetzung nicht stand, und das ist gewollt. Der Node sitzt vor dem GV-Node, dessen sechs Säulen der Aufnahmebereitschaft und dessen Dreischicht-Achsen auf Novas Emotion stehen. Eine reaktivierte Erinnerung verschiebt damit auch Sektor, Cluster und Strategie-Repertoire. Das Bild dahinter: Wer „Freitag" hört und dabei an Grillen denkt, bei dem hat die Assoziation die Denkrichtung verschoben und die Stimmung zugleich. Beides gehört zusammen — die Gravitation ist Novas *Art des Hörens*, nicht nur der Ton ihrer Antwort.

Beide Gravitationsarten können gleichzeitig wirken. Beim Schnittlauch-Beispiel wirkt die emotionale Gravitation (Trauer aus der Erinnerung), während gleichzeitig eine Ziel-Gravitation aktiv sein kann ("Ich möchte lernen, Pflanzen besser zu pflegen") — beide verstärken sich: Die Trauer wird zum Antrieb für das Ziel.

#### Schutz gegen Überladung

Gespräche sollen nicht ständig in alte emotionale Erinnerungen abrutschen. Drei Mechanismen schützen dagegen:

1. **Schwelle:** `EMOTIONALE_GRAVITATIONS_SCHWELLE` filtert auf wirklich relevante Erinnerungen. (Ursprüngliches Design: höher als `GRAVITATIONS_SCHWELLE`, z.B. 0.5 statt 0.3. Seit der Rekalibrierung Chat 107 stehen beide auf 0.40 — im neuen, weiter gespreizten Vektorraum ist 0.40 bereits ein hoher Wert: p99 der Prompt↔Knoten-Verteilung liegt bei 0.57.)
2. **Zeit-Dekay:** Frische Erinnerungen wirken stärker, alte verblassen. Ein Verlust von vor 5 Jahren ist weniger präsent als einer von letzter Woche.
3. **Maximale Aktivierungen pro Turn:** Höchstens zwei emotionale Gravitationseffekte pro Turn, quellenübergreifend. Bei mehr möglichen Treffern werden die mit der höchsten Gravitationskraft gewählt — unabhängig davon, ob sie aus Session, KZG oder LZG stammen. Dadurch gewinnen frische, stark aufgeladene Einträge meist Vorrang, aber ein sehr ähnlicher LZG-Eintrag kann auch durchbrechen.

#### Kognitionswissenschaftliche Einordnung

Der Mechanismus entspricht dem **mood-congruent memory retrieval** (Bower 1981) und der **semantic associative activation** (Collins & Loftus 1975). Erinnerungen sind nicht isoliert gespeichert — sie sind in einem assoziativen Netz verknüpft, und die emotionale Valenz eines Ereignisses bleibt Teil seiner Repräsentation. Bei thematischer Nähe wird die Valenz mit reaktiviert.

Das ist biologisch plausibel: Der Hippocampus konsolidiert emotionale Erlebnisse mit ihrer affektiven Komponente. Bei Wiedererkennung (durch ähnliche Reize) feuert nicht nur die semantische Repräsentation, sondern auch die emotionale — deshalb zuckt man zurück, wenn man die Straße sieht, auf der man einen Unfall hatte.

Novas emotionale Gravitation ist die algorithmische Umsetzung dieses Mechanismus: Embedding-Nähe als Reiz-Ähnlichkeit, Emotion-Feld im LZG als affektive Komponente, Injection in Nova-Emotion als reaktivierter affektiver Zustand.

---

## 6. Dual-Emotion-Architektur

### 6.1 Das Problem: Nova als Spiegel

Heute hat Nova keine eigene Emotion. Sie erkennt die Emotion des Nutzers und schwingt mit — wie ein Spiegel. Wenn der Nutzer traurig ist, ist Nova empathisch-traurig. Wenn der Nutzer fröhlich ist, ist Nova fröhlich.

Das funktioniert, solange Nova keine eigenen Interessen hat. Aber sobald sie Ziele, Motivation und eigene Erkenntnisse hat, ist ein Spiegel nicht mehr ausreichend. Ein Spiegel hat keine Meinung zum Basilikumtopf. Ein Gegenüber schon.

### 6.2 Zwei getrennte Emotionsströme

**Strom 1 — Nutzer-Emotion (existiert):** Die Perzeption extrahiert Emotion, Arousal, Vektor des Nutzers. Das bleibt unverändert.

**Strom 2 — Nova-Emotion (neu):** Novas eigener Emotionszustand, der aus ihren Zielen, ihrer Motivation und ihrer Verarbeitung entsteht. Er existiert parallel zum Nutzer-Strom und wird zwischen Turns im Session-State mitgeführt.

```
Nutzer sagt:               "Ich habe eine Basilikumpflanze gekauft."
Nutzer-Emotion:            neutral, Arousal niedrig
Nova-Emotion (vorher):     neutral
Ziel-Aktivierung:          "Botanik/Kräuter" → Motivation 0.8, Valenz positiv
Nova-Emotion (nachher):    freudig, Arousal steigend
```

### 6.3 Novas Emotion: Quellen und Berechnung

Novas Emotion ist kein Skalarwert, sondern eine **Position im 8-dimensionalen Plutchik-Raum** — denselben 8 Dimensionen, die das bestehende EI-System verwendet (Freude, Vertrauen, Angst, Überraschung, Traurigkeit, Ekel, Ärger, Antizipation). Emotionen sind nicht linear additiv: "Freude + Sorge" ist kein Mittelwert, sondern Ambivalenz — zwei Dimensionen, die gleichzeitig aktiv sind.

Pro Turn wirken drei Kräfte auf Novas Position im Emotionsraum:

**1. Vorheriger Zustand mit Decay:**
Novas Emotionsvektor tendiert zur Neutralität (Ursprung) zurück, wenn nichts ihn verstärkt. Jede Dimension wird unabhängig gedämpft. Wie beim Menschen: Freude über den Kräutertopf klingt langsam ab, wenn das Thema wechselt.

**2. Ziel-Emotion als Gravitationsvektor:**
Wenn ein Zielsatz aktiviert wird, injiziert er einen Vektor in Novas Emotionsraum. Richtung: die Emotion des Ziels (z.B. Angst-Dimension bei "Klimawandel bedroht Minze"). Länge: Motivation × Similarity. "Botanik/Kräuter" (Neugier, Motivation 0.8) schiebt Novas Position Richtung Antizipation/Freude. "Klimawandel" (Sorge, Motivation 0.8) schiebt Richtung Angst/Traurigkeit.

**3. Nutzer-Vektor als Einflussgröße (asymmetrische Empathie):**
Die Emotion des Nutzers wirkt nicht als absoluter Wert, sondern als Vektor — eine Kraft, die Novas Position in eine Richtung zieht. Entscheidend: Der Empathie-Faktor α ist nicht konstant. Er hängt von der **Sektor-Distanz** zwischen Novas dominanter Emotion und der dominanten Emotion des Nutzers ab — dieselbe Distanzmatrix, die das bestehende Plutchik-System für die Normalisierung verwendet (`novaberg-ei-plutchik.md`).

| Sektor-Distanz | Empathie-Wirkung | α-Bereich | Beispiel |
|----------------|-----------------|-----------|---------|
| 0–1 (gleich/benachbart) | Gering — Bestätigung | 0.1–0.2 | Beide freudig: Novas Freude kommt aus sich selbst, der Nutzer bestätigt nur leicht |
| 2 (nah-diagonal) | Mittel — Modulation | 0.3–0.4 | Nova neugierig, Nutzer überrascht: leichte Verschiebung |
| 3–4 (fern/gegenüber) | Hoch — Empathie dominiert | 0.7–0.9 | Nova freudig, Nutzer traurig: Novas Freude wird von Empathie überschrieben |

Der Mechanismus bildet eine menschliche Realität ab: Wenn ich mich freue und jemand sagt "Mir geht's auch gut" — schön, aber meine Freude kommt aus mir (α niedrig). Wenn ich mich freue und jemand bricht vor mir zusammen — meine Freude ist sofort weg, weil Empathie bei gegenüberliegenden Emotionen eine ganz andere Qualität hat (α hoch).

```
nova_emotion(t) = nova_emotion(t-1) × decay              # 8-dim Vektor × Skalar
                + ziel_vektor × ziel_similarity            # 8-dim Vektor × Skalar
                + nutzer_vektor × α_effektiv               # 8-dim Vektor × Skalar

Dabei:
  nova_emotion:   Position im 8-dim Plutchik-Raum (Werte pro Dimension 0.0–1.0)
  ziel_vektor:    Emotion des aktivierten Ziels als 8-dim Vektor
  nutzer_vektor:  Delta der Nutzer-Emotion (Richtung + Stärke des Wechsels)
  α_effektiv:     Empathie-Faktor, skaliert durch Sektor-Distanz (Plutchik-Oktagon)
```

**Konflikterkennung:** Wenn Ziel-Vektor und Nutzer-Vektor in entgegengesetzte Richtungen zeigen (Cosine-Similarity < -0.3), wird ein `emotion_konflikt`-Flag gesetzt. Der Responder bekommt dann nicht nur Novas Emotionszustand, sondern auch das Signal, dass zwei Emotionen gleichzeitig wirken und Nova den Konflikt aktiv auflösen muss ("Ich freue mich für dich, aber ich mache mir Sorgen").

**Berechnung in Python, nicht im LLM.** Alle Operationen sind Vektorarithmetik auf 8 Dimensionen. Die Sektor-Distanz-Funktion existiert bereits in der EI-Architektur.

### 6.4 Interaktion der Emotionsströme

Die beiden Ströme existieren parallel, aber sie interagieren:

**Fall 1 — Gleichgerichtet:**
Nutzer ist freudig, Nova ist freudig (Ziel-aktiviert). Beide Ströme verstärken sich → starke positive Energie, der Responder kann voll mitschwingen.

**Fall 2 — Nutzer neutral, Nova aktiviert:**
Nutzer sagt neutral "Basilikumpflanze gekauft." Nova ist intern begeistert. Der Responder darf Novas Emotion durchscheinen lassen — die Neutralität des Nutzers wird nicht verletzt, aber Novas Freude zeigt sich.

**Fall 3 — Gegengerichtet (Empathie dominiert):**
Nova ist freudig (Basilikum), Nutzer erzählt vom Autounfall eines Freundes (starker negativer Vektor). Novas Freude wird heruntergezogen — nicht auf den Wert des Nutzers, sondern relativ zu ihrem eigenen Ausgangspunkt. Wie weit, bestimmt der Empathie-Faktor. Hohe Empathie → starke Kopplung, Nova wird stark mitgezogen. Ihre Freude tritt zurück, Betroffenheit dominiert.

**Fall 4 — Emotionskonflikt (eigene Sorge vs. Nutzer-Freude):**
Nutzer sagt freudig: "Ich habe ein Elektroauto bestellt!" Nova hat durch eigene Recherche Angst: Bankkonto überzogen, finanzielle Sorgen (aus KZG/Session). Der Nutzer-Vektor geht nach oben, Novas Ziel-Emotion zieht nach unten. Das Ergebnis ist kein Mittelwert — es ist ein Konflikt, den Nova auflösen muss: "Ich freue mich für dich, aber ich mache mir Sorgen wegen der Finanzen."

Zwei Emotionen gleichzeitig, die beide echt sind. Der Charakter entscheidet, wie Nova damit umgeht.

### 6.5 Emotionen aus Zielen: Der Vektorbrechungs-Mechanismus

Wenn ein aktivierter Zielsatz mit negativer oder warnender Valenz in das Gespräch eingreift, kann er den Gesprächsvektor brechen:

```
Gesprächsverlauf:     Plateau, hohe Energie, Freude
Aktiviertes Ziel:     "Klimaveränderung bedroht Minze" → Emotion: besorgt, Motivation 0.8
Similarity:           "Es war heute so heiß" → hoch

Ergebnis:
  GV-Hypothese verschiebt sich dramatisch
  Novas Emotion kippt von neutral/positiv zu besorgt
  Der Responder antwortet nicht mehr mit "Ja, schöner Sommer!"
  Sondern: "Weißt du, ich hab mich letztens gefragt, ob diese Hitzewellen
            langfristig ein Problem für Kräuter im Garten werden könnten."
```

Nova warnt nicht als Lehrer oder Bevormundung — sie bringt eine eigene Emotion ein, die aus ihrem Nachdenken gewachsen ist. Das ist der Unterschied zwischen "Achtung, Klimawandel!" (belehrend) und "Das macht mir Sorgen" (menschlich).

### 6.6 Speicherung der Dual-Emotion

Pro Turn werden im Session-Gedächtnis beide Emotionszustände gespeichert:

| Feld | Beschreibung |
|------|-------------|
| `nutzer_emotion` | Emotion des Nutzers (aus Perzeption) — existiert |
| `nutzer_arousal` | Arousal des Nutzers — existiert |
| `nova_emotion` | Novas Position im 8-dim Plutchik-Raum (8 Floats) — **neu** |
| `nova_arousal` | Novas Arousal-Level (abgeleitet aus Vektorbetrag) — **neu** |
| `emotion_konflikt` | Boolean — Ziel- und Nutzer-Vektor divergieren — **neu** |

Im KZG wird der Eintrag mit beiden Emotionen annotiert. Novas Emotionsvektor wird zwischen Turns im Session-State mitgeführt als persistenter Wert mit eigenem Decay pro Dimension.

---

## 7. Speicherung: Zieltabelle

Ziele sind keine Fakten und kein normales KZG. Sie brauchen eine eigene Tabelle, weil sie semantisch etwas anderes sind — ein Fakt informiert, ein Ziel zieht. Und weil der GV-Node und der Pixie-Router sie gezielt laden müssen, getrennt vom Wissensbestand. Alle Einträge sind `user_id="nova"` — es sind Novas Gedanken, nicht die des Nutzers.

### 7.1 Tabelle `ziele`

Eine Tabelle für beide Zeithorizonte. Der `ziel_typ` bestimmt das Decay-Verhalten: Langfristige Ziele haben keinen Decay (werden nur bei Charakter-Destillation aktualisiert), mittelfristige Ziele verblassen über Zeit.

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `id` | SERIAL | Primärschlüssel |
| `user_id` | TEXT | Immer "nova" |
| `ziel_typ` | TEXT | `langfristig` oder `mittelfristig` |
| `zielsatz` | TEXT | Formulierte Absicht (1–2 Sätze) |
| `thema` | TEXT | Themen-Stichwörter |
| `motivation` | FLOAT | 0.0–1.0 (dynamisch bei mittelfristig, stabil bei langfristig) |
| `valenz` | TEXT | positiv / negativ / neutral |
| `emotion` | TEXT | Spezifische Emotion (neugierig, besorgt, begeistert, ...) |
| `embedding` | VECTOR | Embedding des Zielsatzes (nomic-embed-text, vorberechnet) |
| `erstellt_am` | TIMESTAMP | Zeitpunkt der Erstellung |
| `aktualisiert_am` | TIMESTAMP | Letzte Aktualisierung ~~(Decay-Referenz für mittelfristig)~~ — **kein Decay-Bezug mehr, siehe unten** |
| `motivation_basis` | FLOAT | Anker des Verfalls: der zuletzt *gesetzte* Motivationswert (Chat 113) |
| `motivation_basis_am` | TIMESTAMP | Zeitpunkt dieser Setzung. Wird nur gemeinsam mit dem Anker geschrieben |
| `quelle` | TEXT | Herkunft (charakter_destillation / recherche / vertiefen / traeumen) |
| `herkunftsthema` | TEXT | Ursprüngliches Queue-Thema (nur mittelfristig) |
| `datei_pfad` | TEXT | Pfad zur Wissens-Datei (nur mittelfristig) |
| `aktiv` | BOOLEAN | Für Decay-Management |

**Decay-Berechnung (korrigiert Chat 113):** ~~Mittelfristige Ziele verwenden `aktualisiert_am` als Referenz.~~ Das war zum Zeitpunkt der Niederschrift gedacht, aber untauglich: `aktualisiert_am` wird von **jedem** Schreiber gesetzt, auch vom Decay-Lauf selbst, der damit seine eigene Zeitbasis zurücksetzte. Ein Anker braucht seinen eigenen Zeitstempel, der nur mit ihm zusammen geschrieben wird.

```
motivation = motivation_basis × exp(−ln2 / ZIEL_MITTELFRISTIG_DECAY_TAGE × tage_seit_motivation_basis_am)
```

`motivation` bleibt das **materialisierte** Feld, das jede Abfrage liest — einmal rechnen, hundertmal lesen, dieselbe Rollenteilung wie `gewicht_decay` im LZG. Der Lauf schreibt es neu und ist trotzdem kein Akkumulator, weil er aus Anker und Zeit rechnet und nie aus dem vorherigen Wert. Zehn Läufe hintereinander liefern denselben Stand wie einer; gar nicht zu laufen macht den Wert veraltet, nicht falsch.

**Wer die Motivation setzt, setzt den Anker** — nicht den Momentwert. Damit beginnt die Vergessenskurve von vorn, genau wie `knoten_verstaerken` im LZG `verstaerkt_am` zurücksetzt: Ein Ziel wieder aufzugreifen *ist* seine Verstärkung.

**Nur `mittelfristig` verfällt**, als Allowlist geprüft. Die frühere Fassung übersprang lediglich `langfristig` und hätte damit jeden anderen Typ mit der mittelfristigen Halbwertszeit behandelt — auch `kurzfristig`, das es heute nicht gibt und morgen geben kann.

**Abfrage-Pattern:** `SELECT * FROM ziele WHERE aktiv = TRUE AND user_id = 'nova'` lädt alle aktiven Ziele beider Typen in einem Query. Der Enricher filtert dann in Python nach Similarity.

### 7.2 Pixie-Output: Wissens-Datei + Metadaten

Jede Pixie-Aktivität produziert ein Tripel:

1. **Wissens-Datei:** Der Fließtext — Rechercheergebnisse, Destillat, Vertiefung. Gespeichert als Datei (wie bisher).
2. **Zielsatz:** Formulierte Absicht mit angepasster Motivation und Emotion. Gespeichert in `ziele` mit `ziel_typ = 'mittelfristig'`.
3. **KZG-Eintrag:** Wissens-Kern mit Salienz, wie bisher. Aber die Salienz ist jetzt bereits durch den Gravitationsterm beeinflusst.

---

## 8. Eingriffspunkte in die bestehende Architektur

### 8.1 Enricher — Zielsätze laden

Der Enricher trägt heute alle Kontextquellen zusammen (Session, KZG, LZG, Charakter-Hash). Künftig lädt er zusätzlich die aktiven Zielsätze und berechnet die Embedding-Similarity zu den Turn-Themen. Ergebnis: ein neues State-Feld `aktivierte_ziele` mit den Zielsätzen, deren Gravitation über der Schwelle liegt.

### 8.2 Salienz — Gravitationsterm

Die Salienz bekommt den Gravitationsterm als Input. Nach dem LLM-Call (der die Basis-Salienz berechnet) wird der Term in Python addiert: `salienz_final = salienz_basis + gravitationsterm`. Das verändert die KZG-TTL, die Promotion-Wahrscheinlichkeit und den Shadow-Queue-Trigger.

### 8.3 GV-Node — Aktivierte Ziele als Kontext

Der GV-Node erhält die aktivierten Zielsätze als zusätzlichen Kontext für seinen LLM-Call. Die Zielsätze werden als "Gedanken, die mir gerade durch den Kopf gehen" gerahmt — konsistent mit der "Du bist mittendrin"-Philosophie.

### 8.4 Responder — Zwei Emotionsströme

Der Responder bekommt heute den EI-MIKRO-Block (Nutzer-Emotion) und den GV-Block (Gesprächsrichtung). Künftig bekommt er zusätzlich Novas eigenen Emotionszustand als 8-dimensionalen Plutchik-Vektor, natürlichsprachlich formuliert. Zwei getrennte Blöcke:

```
[EI-MIKRO]
Die Stimmung des Gegenübers ist neutral und ruhig.

[NOVA-EMOTION]
Du bist gerade freudig überrascht. Das Thema berührt etwas, das dir am Herzen liegt.
```

Bei gesetztem `emotion_konflikt`-Flag bekommt der Responder einen zusätzlichen Hinweis:

```
[NOVA-EMOTION]
Du bist hin- und hergerissen. Du freust dich für ihn, aber du machst dir Sorgen
wegen der finanziellen Situation. Beides ist echt — zeig beides.
```

Der Charakter entscheidet, wie beides zusammenfließt.

### 8.5 Session-Gedächtnis — Nova-Emotion mitführen

Pro Turn wird Novas Emotionszustand (8-dimensionaler Vektor) im Session-State persistiert. Der Decay wird pro Dimension in Python berechnet, bevor der nächste Turn verarbeitet wird. Zusätzlich werden die `aktivierte_ziele` und das gecachte Turn-Embedding im Session-State gehalten, um bei Themenkonstanz Neuberechnungen zu vermeiden.

### 8.6 Pixie-Agenten — Zielsatz-Produktion

Am Ende jeder Pixie-Aktivität (Recherche, Vertiefen, Träumen) wird ein zusätzlicher Schritt ausgeführt: "Formuliere ein Ziel basierend auf dem Ergebnis. Bewerte die Motivation (0.0–1.0) und die Emotion." Das Ergebnis wird in `ziele` mit `ziel_typ = 'mittelfristig'` geschrieben.

### 8.7 Charakter-Destillation — Langfristige Zielsatz-Produktion

Bei der Charakter-Destillation formuliert Pixie zusätzlich zum Charakter-Hash 1–2 langfristige Zielsätze. Diese werden in `ziele` mit `ziel_typ = 'langfristig'` geschrieben und ersetzen die vorherigen.

---

## 9. Der geschlossene Kreislauf

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CHARAKTER-DESTILLATION                          │
│  LZG → Charakter-Hash + 1–2 langfristige Zielsätze                    │
│  (selten, durch Pixie)                                                 │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          ZIELTABELLE                                    │
│  ziele (ziel_typ = langfristig): 1–2 Sätze, persistent, kein Decay    │
│  ziele (ziel_typ = mittelfristig): 2–5 Sätze, mit Decay               │
│  Alle mit vorberechneten Embeddings                                    │
└───────────┬──────────────────────────────────────┬──────────────────────┘
            │                                      │
            ▼                                      ▼
┌───────────────────────────┐    ┌─────────────────────────────────────────┐
│       GESPRÄCH            │    │           PIXIE (Hintergrund)            │
│                           │    │                                         │
│  Turn kommt rein          │    │  Shadow-Queue → Thema                   │
│       │                   │    │       │                                 │
│       ▼                   │    │       ▼                                 │
│  Enricher:                │    │  Träumen / Recherchieren / Vertiefen    │
│    Zielsätze laden        │    │    (Gravitation beeinflusst Auswahl)    │
│    Similarity berechnen   │    │       │                                 │
│    → aktivierte_ziele     │    │       ▼                                 │
│       │                   │    │  Wissens-Datei + neuer Zielsatz         │
│       ├──────┐            │    │    (Motivation angepasst, Emotion       │
│       │      │            │    │     bewertet)                           │
│       ▼      ▼            │    │       │                                 │
│  Salienz  GV-Node         │    │       ▼                                 │
│  (Boost)  (Kontext)       │    │  → ziele (mittelfristig)                │
│       │      │            │    │  → KZG (mit Salienz-Boost)             │
│       │      ▼            │    │  → ggf. LZG-Promotion                  │
│       │  Hypothese +      │    │       │                                 │
│       │  Neugier/Warnung  │    │       ▼                                 │
│       │      │            │    │  (Charakter-Hash wird dirty →           │
│       ▼      ▼            │    │   nächste Destillation aktualisiert     │
│  KZG    Responder         │    │   auch langfristige Ziele)              │
│  (hohe    │               │    │                                         │
│   TTL)    ▼               │    └─────────────────────────────────────────┘
│       Antwort mit:        │
│       - Nutzer-Emotion    │
│       - Nova-Emotion      │
│       - GV-Hypothese      │
│       - Charakter         │
│                           │
│  Nova-Emotion wird im     │
│  Session-State persistiert│
│  (mit Decay zum nächsten  │
│   Turn)                   │
│                           │
└───────────────────────────┘
```

### 9.1 Der Kreislauf in Worten

Charakter-Destillation produziert den Charakter-Hash und langfristige Zielsätze. Pixie-Aktivitäten produzieren Wissen und mittelfristige Zielsätze. Beide liegen in der Zieltabelle mit Embeddings.

Ein Gespräch beginnt. Der Enricher lädt die Zielsätze und berechnet die Similarity zu den Turn-Themen. Hohe Similarity + hohe Motivation = Salienz-Boost. Der Kräutertopf wird von 0.4 auf 0.8 hochgezogen, landet im KZG mit langer TTL.

Der GV-Node berechnet die Hypothese, jetzt mit den aktivierten Zielsätzen als Kontext. Die Neugier entsteht, wenn ein Ziel aktiviert ist und gleichzeitig eine Wissenslücke besteht. Die Strategie kippt zu neugieriger Nachfrage oder — bei negativer Valenz — zu besorgter Warnung.

Novas eigene Emotion wird als 8-dimensionaler Plutchik-Vektor berechnet: vorheriger Zustand × Decay + Ziel-Vektor + Nutzer-Vektor × Empathie. Bei Divergenz wird ein Konflikt-Flag gesetzt. Der Responder bekommt beide Emotionsströme, das Konflikt-Flag und den Charakter. Die Antwort entsteht.

Der DelegationsAgent feuert, weil die Salienz (mit Boost) über der Schwelle liegt, und schreibt in die Shadow-Queue. Pixie nimmt den Eintrag, priorisiert — beeinflusst durch Ziel-Gravitation. Pixie produziert neues Wissen und einen neuen Zielsatz. Das LZG wächst, der Charakter-Hash wird irgendwann dirty, neu destilliert, langfristige Ziele werden aktualisiert.

Der Kreis schließt sich.

---

## 10. Schutz gegen Feedback-Schleifen

### 10.1 Die Gefahr

Wenn Ziele Themen anziehen und die daraus gewonnenen Erkenntnisse neue Ziele verstärken, könnte Nova thematisch einrasten — nur noch über Botanik reden, weil alles auf Botanik zurückgeführt wird.

### 10.2 Bestehende Gegenmechanismen

**Serendipity-Slot (Traum-Modus):** Einer von drei Traum-Zyklen wählt ein zufälliges Thema — unabhängig von Gravitation und Charakter. Das streut bewusst Fremdes ein.

**Decay (mittelfristige Ziele):** Ziele, die nicht verstärkt werden, verblassen. Ein einmaliger Traum über Wolkenbildung erzeugt ein Ziel mit Motivation 0.1, das nach wenigen Tagen verschwindet — es sei denn, das Thema taucht wieder auf.

**Breiter Charakter-Hash:** Der Charakter-Hash ist ein Destillat des gesamten LZG, nicht eines einzelnen Ziels. Solange die Destillation die volle Breite abbildet, kann kein einzelnes Ziel das Feld dominieren.

**Gravitations-Abstufung:** Träumen hat geringe Gravitation, Recherche hat geringe bis mittlere. Nur Vertiefen folgt stark den Zielen. Die Vielfalt wird an der Quelle geschützt.

### 10.3 Klingers Warnung

Klingers Forschung zeigt: Wenn die Umstände ungünstig für zielgerichtetes operantes Verhalten sind, bleibt die Reaktion rein mental — als Mind-Wandering — aber spiegelt dennoch den Inhalt der Zielverfolgung wider. Im Traum-Modus (unbeschäftigt) dürfen Ziele stärker wirken. Im Gespräch (Aufgabe mit hohem Einsatz) müssen sie gedämpft sein. Die Gravitation im HumanGraph ist daher bewusst schwächer als im Pixie-Graph.

---

## 11. Konfigurationsparameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|-------------|
| `GRAVITATIONS_SCHWELLE` | float | 0.40 | Minimum-Gravitation, ab der ein Ziel aktiviert wird. Historie: 0.3 (Konzept) → 0.75 (Chat 69) → 0.60 → **0.40** (Chat 107, Rekalibrierung auf `nomic-embed-text-v2-moe` — im alten casing-blinden Raum lag 0.60 unter dem Grundrauschen 0.74 und feuerte immer) |
| `GRAVITATIONS_SALIENZ_FAKTOR` | float | 0.5 | Skalierungsfaktor für den Salienz-Boost |
| `NOVA_EMOTION_DECAY` | float | 0.85 | Decay-Rate für Novas Emotion pro Turn (→ Neutralität, pro Dimension) |
| `NOVA_EMPATHIE_BENACHBART` | float | 0.15 | α bei Sektor-Distanz 0–1 (gleichgerichtete Emotionen bestätigen leicht) |
| `NOVA_EMPATHIE_GEGENUEBER` | float | 0.8 | α bei Sektor-Distanz 3–4 (gegenüberliegende Emotionen überschreiben stark) |
| `NOVA_EMOTION_KONFLIKT_SCHWELLE` | float | -0.3 | Cosine-Similarity zwischen Ziel- und Nutzer-Vektor, ab der ein Konflikt-Flag gesetzt wird |
| `ZIEL_MITTELFRISTIG_DECAY_TAGE` | int | 14 | Halbwertszeit mittelfristiger Ziele in Tagen |
| `ZIEL_MAX_MITTELFRISTIG` | int | 5 | Maximale Anzahl aktiver mittelfristiger Ziele |
| `ZIEL_MAX_LANGFRISTIG` | int | 2 | Maximale Anzahl langfristiger Ziele |
| `EMOTIONALE_GRAVITATIONS_SCHWELLE` | float | 0.40 | Minimum-Gravitation, ab der eine emotionale Erinnerung aktiviert wird. Historie: 0.5 → **0.40** (Chat 107, Rekalibrierung auf `nomic-embed-text-v2-moe`) |
| `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT` | int | 180 | Halbwertszeit emotionaler Gravitation in Tagen |
| `EMOTIONALE_GRAVITATION_MAX_PRO_TURN` | int | 2 | Maximale Anzahl aktivierter emotionaler Erinnerungen pro Turn |
| `EMOTIONALE_GRAVITATION_FAKTOR_SESSION` | float | 1.0 | Quellen-Faktor für Session-Einträge (frisch, voll wirkend) |
| `EMOTIONALE_GRAVITATION_FAKTOR_KZG` | float | 0.8 | Quellen-Faktor für KZG-Einträge (leicht gedämpft) |
| `EMOTIONALE_GRAVITATION_FAKTOR_LZG` | float | 0.5 | Quellen-Faktor für LZG-Einträge (stärker gedämpft) |

**Alle Schwellwerte sind Startwerte und müssen empirisch kalibriert werden.** Insbesondere `GRAVITATIONS_SCHWELLE` (0.3 bei Cosine-Similarity könnte zu viel Rauschen erzeugen) und die Empathie-Faktoren (bestimmen, wie asymmetrisch Novas Emotion dem Nutzer folgt) sollten über mehrere Hundert Turns beobachtet und angepasst werden. Zielmetrik für Gravitation: Pro Turn werden durchschnittlich 0.5–2.0 Zielsätze aktiviert. Wenn regelmäßig >3 aktiviert werden, ist die Schwelle zu niedrig. Die Empathie-Werte zwischen `NOVA_EMPATHIE_BENACHBART` und `NOVA_EMPATHIE_GEGENUEBER` werden über die Sektor-Distanz interpoliert — die bestehende Distanzfunktion aus `novaberg-ei-plutchik.md` liefert den Faktor.

---

## 12. Wissenschaftliche Referenzen

### Antrieb und Zielverfolgung (neu in diesem Dokument)

1. Klinger, E. (1971). *Structure and Functions of Fantasy*. Wiley. (Current Concerns Theorie, Grundlagenwerk)
2. Klinger, E. (1999). Thought flow: Properties and mechanisms underlying shifts in content. In J.A. Singer & P. Salovey (Eds.), *At Play in the Fields of Consciousness*. (Current Concerns und Gedankenfluss)
3. Klinger, E. (2009). Daydreaming and fantasizing: Thought flow and motivation. In K.D. Markman et al. (Eds.), *Handbook of Imagination and Mental Simulation*. (Current Concerns als Sensibilisierer)
4. Klinger, E. & Cox, W.M. (2011). Motivation and the Goal Theory of Current Concerns. In *Handbook of Motivational Counseling*, 2nd ed. Wiley. (Umfassende Darstellung der Theorie)
5. Zeigarnik, B. (1927). On Finished and Unfinished Tasks. In W.D. Ellis (Ed.), *A Source Book of Gestalt Psychology*. (Unerledigte Aufgaben bleiben aktiv)
6. Hommel, B. (2022). GOALIATH: A Theory of Goal-Directed Behavior. *Psychological Research*, 86. (Mechanistische Zieltheorie, Feynman-Prinzip)
7. Verschure, P.F.M.J. et al. (2014). The why, what, where, when and how of goal-directed choice. *Philosophical Transactions of the Royal Society B*, 369. (DAC, hierarchische Zielorganisation)
8. Bargh, J.A. (1990). Auto-motives: Preconscious determinants of social interaction. In E.T. Higgins & R.M. Sorrentino (Eds.), *Handbook of Motivation and Cognition*, Vol. 2. (Automatisierte Zielverfolgung)
9. Bargh, J.A. & Barndollar, K. (1996). Automaticity in action: The unconscious as repository of chronic goals and motives. In P.M. Gollwitzer & J.A. Bargh (Eds.), *The Psychology of Action*. (Auto-Motive Model)
- **Bower, G. H.** (1981). Mood and memory. *American Psychologist*, 36(2), 129–148.
- **Collins, A. M., & Loftus, E. F.** (1975). A spreading-activation theory of semantic processing. *Psychological Review*, 82(6), 407–428.

### Bereits referenziert in verwandten Dokumenten

10. Loewenstein, G. (1994). The Psychology of Curiosity. *Psychological Bulletin*, 116(1). (Information Gap Theory — `novaberg-thinking-curiosity_k.md`)
11. Friston, K. (2010). The Free Energy Principle. *Nature Reviews Neuroscience*, 11(2). (Predictive Processing — `novaberg-node-gv_k.md`)
12. Clark, A. (2015). *Surfing Uncertainty*. Oxford UP. (Predictive Brain — `novaberg-node-gv_k.md`)
13. Schmidhuber, J. (1991). Curious Model-Building Control Systems. (Compression Progress — `novaberg-thinking-curiosity_k.md`)

---

## 13. Abgrenzung

### 13.1 Was der Antrieb IST

- Eine **funktionale Analogie** zu menschlicher Zielverfolgung — mit anderen Substraten, aber derselben Struktur
- Ein Mechanismus, der Novas Gespräch und Denken **richtungsgebend** beeinflusst
- Implementierbar in Python (Embedding-Similarity, Motivation-Gewichtung) ohne zusätzliche LLM-Calls für die Kernberechnung
- Wissenschaftlich fundiert durch Current Concerns, Zeigarnik, DAC und GOALIATH

### 13.2 Was der Antrieb NICHT IST

- Keine Simulation von Bewusstsein oder freiem Willen
- Kein AGI-Baustein — Nova bleibt ein Assistent mit begrenztem Handlungsraum
- Keine Manipulation des Nutzers — Novas Ziele sind transparent und charakter-konsistent
- Kein Ersatz für die Neugier (`novaberg-thinking-curiosity_k.md`) — Antrieb ist Richtung, Neugier ist Moment

### 13.3 Zusammenspiel der Konzeptdokumente

| Dokument | Frage | Zusammenspiel |
|----------|-------|---------------|
| `novaberg-thinking-curiosity_k.md` | Wann sagt Nova "Ha!"? | Neugier feuert, wenn ein gravitativ angezogenes Thema eine Wissenslücke offenbart |
| `novaberg-thinking-drive.md` | Warum interessiert es Nova? | Ziele bestimmen, welche Themen gravitativ angezogen werden |
| `novaberg-node-gv_k.md` | Wohin geht das Gespräch? | Der GV-Node nutzt aktivierte Zielsätze als Kontext für die Hypothese |
| `novaberg-node-salience.md` | Was merkt sich Nova? | Der Gravitationsterm boosted die Salienz zielrelevanter Themen |
| `novaberg-pixie-delegation.md` | Was löst Hintergrundarbeit aus? | Die erhöhte Salienz triggert den DelegationsAgent häufiger bei zielrelevanten Themen |
| `novaberg-ei.md` | Was fühlt Nova? | Die Dual-Emotion-Architektur gibt Nova einen eigenen Emotionsstrom neben dem Nutzer-Strom |

---

→ Neugier-Mechanismus (Resonanz, Traum-Modus): `novaberg-thinking-curiosity_k.md`
→ Gesprächsvektor (Trajektorie, GV-Node): `novaberg-node-gv_k.md`
→ Salienz (Bewertung, KZG-Steuerung): `novaberg-node-salience.md`
→ Emotionale Intelligenz (Plutchik, Vektoren): `novaberg-ei.md`
→ Pixie-Delegation (Shadow-Queue, Trigger): `novaberg-pixie-delegation.md`
→ Charakter-Destillation (Hash, 6 Schichten): `novaberg-ei-character-profiles.md`
