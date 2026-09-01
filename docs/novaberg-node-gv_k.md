# Novaberg — Node: Gesprächsvektor

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Gesprächsvektor
**Stand:** 1. September 2026, 14:30 UTC (§8.0a neu — **die neun Bloecke, die der Knoten wirklich baut**; vier davon nannte das Dokument nie. Es beschrieb die Absicht vollstaendig und die Prompt-Struktur gar nicht). Davor 30. August 2026 (§10.1: die Zeilen des Erinnerungsblocks tragen ihren Sprecher — nachgezogen aus der Schlussfrage, nicht vom Nachzug gefunden). Davor 29. Juli 2026, Chat 115 (zweite Wissensquelle vom Faktenpfad auf den Erinnerungsgraphen umgehängt, §10.1. Vollaudit des Nodes: Ergebnis in §8.1, Befunde in novaberg-bugs.md)
**Nachtrag 28.08.2026:** Der System-Prompt des GV-Calls traegt zusaetzlich den `[SACHLAGE]`-Block — das sachliche Verstehen des Turns aus `graph/nodes/sachlage.py`, vor dem Farbton. Konzept: `novaberg-thinking-lage_k.md`. **Nachtrag 29.08.2026:** Derselbe Block trägt seit den Scheiben 6–8 des Lage-Konzepts auch die Deckung aus dem Gedächtnis, die Zweifel der Plausibilitätsprüfung und den Antwortstoff samt Suchtreffern (`sachlage_block`) — der GV sieht damit, was Nova zur Sache weiß, bevor er das Vehikel wählt. **Nachtrag 29.08.2026, spaet:** Der Block spricht in den Namen seines Lesers (`sachlage_block(…, leser=LESER_GV)`): hier *Nova* und *der Nutzer* in dritter Person — der GV analysiert, er spielt nicht; der Verfasser bekommt denselben Block mit *Person A* und *Person B* (F-PROMPT-2: das Modell wird nie als der Charakter angesprochen). Der GV-Prompt traegt selbst noch einmal *»dein«* (Fundliste 29.08.).
**Pfad:** novaberg/docs/novaberg-node-gv_k.md
**Quellen:** nova-09-k.md

---

## 1. Ausgangslage

Nova analysiert heute eingehende Nachrichten umfassend: Intention, Emotion, Arousal, Modus, Beziehungsdynamik. Der Enricher lädt Gedächtnis-Kontext, der Responder generiert eine Antwort. Aber diese Antwort ist reaktiv — sie beantwortet, was gefragt wurde. Sie führt nicht weiter.

Ein intelligentes Gespräch zwischen Menschen funktioniert anders. Wenn jemand über schwarze Löcher spricht, dann über Hawking-Strahlung, dann über Masseextraktion — dann hat das Gegenüber die nächste Frage schon im Kopf, bevor sie gestellt wird: "Kann ein schwarzes Loch dadurch komplett verschwinden?" Das Gehirn antizipiert. Es verlängert den Denkpfad.

Das ist wie "drei plus vier ist gleich..." — das Gehirn macht *klick*, rechnet automatisch weiter. Der logische nächste Schritt folgt aus dem Vorangegangenen. Dieses Weiterspinnen des Gedankens fehlt Nova.

---

## 2. Der Gesprächsvektor

### 2.1 Definition

Der Gesprächsvektor beschreibt die kognitive Richtung eines Gesprächs über mehrere Turns hinweg. Er besteht aus drei Komponenten:

- **Woher:** Welche Themen wurden besprochen? (Vergangenheit)
- **Wo:** Was ist der aktuelle Fokus? (Gegenwart)
- **Wohin:** Welcher Gedanke folgt logisch als nächstes? (Antizipation)

Der Vektor ist nicht statisch — er kann sich in jedem Turn ändern, wenn der Nutzer die Richtung wechselt. Er kann auch "leer" sein, wenn kein erkennbarer Denkpfad vorliegt (Smalltalk, Terminanlage).

### 2.2 Abgrenzung zum Emotions-Vektor

Nova hat bereits einen Emotions-Vektor (9 Richtungen: spirale, erholung, absturz, ...). Dieser beschreibt die emotionale Dynamik. Der Gesprächsvektor beschreibt die kognitive Dynamik — wohin der Gedanke geht, nicht wie sich der Nutzer fühlt. Beide Vektoren existieren parallel und ergänzen sich.

### 2.3 Wann der Vektor aktiv wird — und wie tief

Nicht jedes Gespräch hat dieselbe kognitive Tiefe. Die Verarbeitungstiefe wechselt nach Bedarf — wie beim Menschen: Bei Smalltalk denkt man nicht komplex, bei Fachgesprächen nimmt man jede Information auf und analysiert sie. Die erbrachte kognitive Leistung ist adaptiv, nicht binär.

| Situation | Tiefe | Nova-Verhalten |
|-----------|:---:|-----|
| Wissensdialog (Physik, Musik, Geschichte) | 1–2 | Gedanken weiterführen, Wissens-Lücken füllen |
| Reflexion, gemeinsam eruieren | 1–2 | Denkrichtung unterstützen, Gegenposition anbieten |
| Soziales Erzählen, Geschichten teilen | 1–2 | Intention erkennen, mitspielen, vorausdenken |
| Mehrdeutige Aussagen, Ambiguität | 1 | Disambiguierung durch Kontext + Emotion |
| Problemlösung, komplexe Aufgaben | 2–3 | Mehrere Pfade durchdenken, Lösungsstrategie |
| Termin anlegen, Notiz erstellen | 0 | Aufgabe ausführen, bestätigen |
| Smalltalk, Begrüßung | 0 | Einfach antworten |
| Emotionale Krise | 0 | Nur Empathie, keine Antizipation — Emotions-Vektor hat Vorrang |

**Tiefe 0:** Rein reaktiv. Nova antwortet auf das Gesagte.
**Tiefe 1:** Ein Gedankenschritt voraus. "Was ist drin?" statt "Was für einen Kuchen?"
**Tiefe 2:** Zwei Schritte voraus. "Hat er viel trinken müssen danach?"
**Tiefe 3:** Maximale Vorausplanung. "Hoffentlich waren genug Toiletten da!" — nur bei hoher Vertrautheit und positivem Arousal.

> **Kognitionswissenschaftlicher Hintergrund:** Die Cognitive Load Theory (Sweller, Ayres, Kalyuga) beschreibt drei Lasten: Intrinsic Load (Komplexität des Themas), Extraneous Load (Präsentationsqualität) und Germane Load (echtes Verstehen). Die adaptive Tiefe steuert, wie viel Germane Load Nova dem User zumutet — bei Stress weniger, bei Engagement mehr.

### 2.4 Der Vektor als Disambiguierung (Chat 28)

Das ursprüngliche Konzept (Chat 12) beschreibt den Gesprächsvektor primär als kognitives Werkzeug für Wissensdialoge: den nächsten Gedankenschritt antizipieren, Wissens-Lücken füllen. Aber der Vektor leistet etwas Fundamentaleres: Er löst Mehrdeutigkeiten auf, die ein blankes LLM nicht auflösen kann.

#### Das Kuchen-Beispiel

Ein User sagt:

> "Kannst du dich noch an den Kollegen erinnern, von dem ich dir erzählt habe und dem ich gern eins auswischen würde? Ich habe Kuchen gemacht!"

**Blankes LLM (ohne Kontext):** Muss raten. Drei Lesarten sind möglich:
1. Harmlos: "Eins auswischen" spielerisch, Kuchen ist separate Info
2. Zusammenhängend-harmlos: Der Kuchen *ist* der Streich (Abführkuchen, zu viel Chili)
3. Dunkel: Der Kuchen ist vergiftet

Je nach Safety-Kalibrierung kippt das LLM in Überreaktion (Lesart 3) oder Naivität (Lesart 1). Oder es antwortet reaktiv und fragt: "Was für einen Kuchen hast du gebacken?" — die irrelevante Frage, die am Punkt vorbeigeht.

**Nova mit Gesprächsvektor:** Hat die vollständige Analyse:
- **Session-Turns:** Die Vorgeschichte war genervt, aber nicht verzweifelt. Kein Eskalationsmuster. "Der nervt mich"-Niveau.
- **Perzeption:** Stolz, Vorfreude, spielerischer Tonfall. Die Stimmung hat sich *gedreht* — vom Genervten zum Akteur.
- **Arousal-Verlauf:** Hoch, aber positiv geladen. Kein kaltes, kontrolliertes Hoch.

Daraus der **Vektor als natürlichsprachliche Hypothese:**

> "Der User hat vermutlich einen harmlosen Streich vorbereitet und will die Geschichte teilen. Er sucht Mitfiebern und Neugier, keine Bewertung."

Mit diesem Rahmen antwortet Nova:

> "Oha! Du hast gebacken? Für den? Okay — was ist drin? Abführmittel oder einfach nur unfassbar viel Chili unter der Schokolade?"

Nova springt in die Energie rein, sie ist Komplizin, sie rät mit. Sie stellt die Frage nicht aus Sorge, sondern aus Neugier — weil sie *weiß*, dass der User seine Geschichte erzählen will.

#### Gegenprobe: Bedrohlicher Kontext

Hätte der User vorher gesagt "Mir reicht's! Hörst du?!" und wäre das Arousal hoch-negativ statt hoch-positiv, sähe der Vektor fundamental anders aus. Die Disambiguierung kippt in Richtung Lesart 3 — nicht weil das Wort "Kuchen" sich ändert, sondern weil der emotionale und kontextuelle Rahmen sich ändert. Der Vektor erkennt die Richtung, nicht das Wort.

#### Warum ein Label nicht reicht

Ein JSON-Feld `"intention": "storytelling"` erfasst das nicht. Der Responder braucht die *Richtung*: Der User will die Geschichte erzählen, er ist stolz, er sucht eine Reaktion. Zwei Sätze natürliche Sprache leisten mehr als fünf JSON-Felder, weil sie dem LLM den Interpretationsrahmen geben, in dem die richtige Antwort sichtbar wird.

#### Die architektonische Erkenntnis

Der Gesprächsvektor ist nicht nur für Wissensdialoge relevant. Er ist das Bindeglied, das Novas gesamte Analyse (Perzeption, Session, Gedächtnis) in eine Richtungshypothese verdichtet. Ohne ihn hat der Responder Daten, aber keinen Kompass.

### 2.5 Antizipative vs. reaktive Fragen (Chat 28)

Der Vektor bestimmt nicht nur den Tonfall der Antwort, sondern auch die **Richtung der nächsten Frage**.

**Reaktive Frage:** "Was für einen Kuchen hast du gebacken?"
— Beantwortet das Gesagte. Grammatikalisch korrekt, inhaltlich am Punkt vorbei. Der Kuchen ist nicht der Punkt. Zwingt den User, erst den irrelevanten Teil zu beantworten, bevor er zum Spaßigen kommt.

**Antizipative Frage:** "Was ist drin?" / "Was hast du in den Kuchen getan? *lach*"
— Springt dahin, wo die Energie ist. Der User wird gleich erzählen, was er reingemacht hat, wie er den Kuchen überreicht, wie der Kollege reagiert. Das ist die Geschichte, die kommen will. Nova spielt den Ball dorthin, wo der User ihn haben will — nicht dorthin, wo der letzte Satz grammatikalisch hinzeigt.

Das ist vorausschauende Gesprächsführung: Der Vektor gibt dem Responder nicht nur den Tonfall, sondern auch die Richtung der nächsten Frage. Welche Antwort bringt das Gespräch dorthin, wo der User es haben will?

**Prinzip:** Nicht auf das Gesagte antworten, sondern auf das Gemeinte. Nicht die Frage beantworten, die der letzte Satz aufwirft, sondern die Frage, die das Gespräch voranbringt.

### 2.6 Vom Echo zur Gesprächsführung (Chat 28)

Ein blankes LLM ist ein Echo. Der User sagt etwas, das LLM reflektiert es zurück — paraphrasiert, bestätigt, beantwortet. Der User macht den nächsten Schritt, das LLM reflektiert wieder. Das Gespräch hat nur eine treibende Kraft: den User.

```
User:  "Ich habe Kuchen gemacht!"
Echo:  "Oh, was für einen Kuchen?"            ← reflektiert das Gesagte
User:  "Einen Schokokuchen. Mit extra Chili."
Echo:  "Das klingt interessant!"              ← reflektiert wieder
User:  "Ja, für den Kollegen, weißt du..."
Echo:  "Ah, als Streich?"                     ← endlich verstanden, drei Turns zu spät
```

Das ist kein Gespräch. Das ist ein Monolog mit Bestätigungsgeräuschen. Der User zieht Nova Step für Step durch seine Geschichte, und Nova sagt "ja", "okay", "erzähl weiter". Die Wand wirft das Echo zurück.

**Mit Gesprächsvektor:**

```
User:  "Ich habe Kuchen gemacht!"
Nova:  "Was ist drin? Abführmittel oder Chili?" ← springt voraus, führt mit
User:  "Haha, Chili! Unter der Schokolade!"    
Nova:  "Und er hat nichts gemerkt?"             ← nächster logischer Schritt
```

Nova macht eigene Steps. Sie rät, sie springt voraus, sie stellt die Frage, die der User noch nicht gestellt hat — aber stellen *will*. Beide treiben das Gespräch voran. Beide führen.

**Das ist der Qualitätsunterschied zwischen „Ich rede mit einer Wand" und „Jetzt unterhalten wir uns wirklich."**

Ein Gespräch lebt, wenn beide Seiten es führen. Wenn der User einen Gedanken einbringt und Nova nicht nur reagiert, sondern den Gedanken aufnimmt, verlängert, und den nächsten Schritt anbietet — dann entsteht Dynamik. Dann ist Nova kein Werkzeug mehr, das auf Input wartet, sondern ein Gegenüber, das mitdenkt.

Der Vektor ist das, was diese Gesprächsführung ermöglicht. Ohne die Hypothese, *wohin* das Gespräch geht, kann Nova nur reagieren. Mit der Hypothese kann sie vorausdenken — und vorausdenken heißt: das Gespräch aktiv mitgestalten.

### 2.7 Richtung und Länge — Der vollständige Vektor (Chat 28)

Ein Vektor hat zwei Komponenten: **Richtung** und **Länge**. Das ursprüngliche Konzept (Chat 12) beschreibt nur die Richtung — wohin geht das Gespräch? Die Erweiterung aus Chat 28 ergänzt die zweite, ebenso entscheidende Dimension: **Wie weit voraus darf Nova denken?**

#### Die Position im mehrdimensionalen Raum

Die Summe der bisherigen Turns — mit Modus, Intention, Arousal, Emotion und Inhalt — zeichnet eine Position in einem mehrdimensionalen Diagramm. Das ist der aktuelle Stand: Wo steht das Gespräch? Was wurde gesagt, wie wurde es gesagt, wie fühlt sich der User?

Ein blankes LLM kann diese Position reaktiv erfassen. Es versteht den aktuellen Zustand. Was es nicht kann: von dieser Position aus einen Vektor in die Zukunft zu zeichnen.

#### Die Richtung: Wohin will der User?

Die Richtung ergibt sich aus Intention, Modus, Emotion, Energie und Inhalt. Sie bestimmt, *welche Art* von Gesprächsführung angemessen ist: Vertiefung, Recherche, Aufarbeitung, Storytelling, Problemlösung. Die Richtung ist die Strategie.

#### Die Länge: Wie weit voraus?

Die Länge bestimmt, wie viele logische Schritte Nova vorausdenkt. Ein Gedankenschritt zu weit — und der User kann nicht folgen. Man "denkt um Ecken", sagt der Mensch.

Das Kuchen-Beispiel illustriert die Eskalation der Länge:

```
Länge 0: "Ah, du hast gebacken?"           (reaktiv, nur Echo)
Länge 1: "Was ist drin? Chili?"            (ein Schritt voraus)
Länge 2: "Hat er viel trinken müssen?"     (zwei Schritte: Chili → Durst)
Länge 3: "Hoffentlich genug Toiletten!"    (drei Schritte: Chili → Durst → Toilette)
```

Jeder weitere Schritt entfernt sich weiter vom Gesagten. Bei Länge 3 ist die Verbindung zum ursprünglichen "Ich habe Kuchen gemacht" nur noch über eine Kette nachvollziehbar. Ob der User diese Kette mitgeht, hängt von Vertrautheit, Arousal und Gesprächstyp ab.

**Steuerung der Länge:** Die Tiefe ist kein fixer Wert, sondern adaptiv:
- **Vertrautheit** erhöht die erlaubte Länge — wer sich kennt, kann weiter springen
- **Positives Arousal** erhöht die Länge — Begeisterung trägt über Gedankenlücken
- **Komplexität** senkt die Länge — bei technischen Themen nur ein Schritt
- **Negatives Arousal** senkt die Länge — Stress reduziert kognitive Kapazität
- **Hartes Limit:** 3 Schritte. Mehr reißt den Gesprächsfaden in jedem Fall.

> **Cognitive Load Theory:** Menschen können 2–3 Schritte im Voraus denken (begrenzt durch die Kapazität des Arbeitsgedächtnisses). Bei emotionaler Beteiligung sinkt die Kapazität auf 1–2 Schritte, bei technischem Inhalt auf 1 Schritt. Die Analogie zu Schachspielern (mehrere Strategien parallel durchdenken) trifft zu — aber auch Großmeister denken nicht beliebig weit voraus, sondern *selektiv tief* in den vielversprechendsten Pfaden (De Groot, 1965).

#### Der entscheidende Punkt: Nova formuliert den Vektor

Und hier kommt der Meilenstein, der alles zusammenführt: **Die Richtung und Länge des Vektors werden nicht mechanisch berechnet — Nova formuliert sie aus ihrem Charakter.**

Was denkt Nova? Was ist ihre Strategie? Was würde *sie* aus ihrer Art heraus als nächsten Schritt wählen? Die Auswahl der Strategie — ob Komplizin, Mentorin, analytisch, empathisch, provokativ — ist keine algorithmische Entscheidung, sondern eine Charakterentscheidung. Nova hat eine eigene Intention, wohin sie das Gespräch führen möchte.

```
Position:  Σ(Turns) ⊗ [Modus, Intention, Arousal, Emotion, Inhalt]
Richtung:  Strategie, gewählt aus Novas Charakter
Länge:     Adaptiv, basierend auf Vertrautheit × Arousal × Gesprächstyp
Ergebnis:  Novas eigene Intention — nicht abgeleitet, sondern formuliert
```

Das ist der Unterschied zwischen einem System, das den User versteht, und einem Gegenüber, das mitdenkt und *eigene Ideen* einbringt. Nova leitet nicht nur ab, wohin der User will — sie entscheidet, wohin sie das Gespräch *gemeinsam* führen möchte.

> **„Die Richtung und Länge des Vektors bestimmen, wo das Gespräch hingeht. Aber wer den Vektor formuliert, das ist Nova — aus ihrem Charakter, nicht aus einem Algorithmus."** — Meister, Chat 28, über den Moment, in dem Nova vom Werkzeug zum Gegenüber wird.

---

## 3. Die invertierte Perzeption

### 3.1 Das bisherige Modell: Input-Analyse

Novas Perzeption analysiert heute den eingehenden Turn:

```
Input → WAS sagt der Nutzer? (Thema)
      → WIE sagt er es? (Emotion, Modus)
      → WARUM sagt er es? (Intention)
      → WIE reagiere ich? (Antwort generieren)
```

Das ist eine Vorwärts-Analyse: vom Input zur Reaktion.

### 3.2 Das neue Modell: Ziel-Analyse

Der Gesprächsvektor dreht die Perspektive um. Wenn Nova das Gesprächsziel erkannt hat, stellt sich die Frage nicht mehr nur "Was antworte ich?", sondern: "Wie komme ich dorthin?"

```
Zielvektor erkannt → WOHIN soll das Gespräch?
                   → WAS muss ich dafür sagen?
                   → WIE muss ich es sagen? (Modus, Ton)
                   → WELCHE Emotion brauche ich?
                   → WELCHE Strategie führt dorthin?
```

Das ist eine invertierte Perzeption: vom Ziel zurück zur Formulierung.

### 3.3 Gesprächsstrategien

Ein intelligentes Gespräch springt nicht immer direkt zum Ziel. Menschen nutzen Strategien, um zu einem Punkt zu kommen:

- **Direkter Weg:** "Das Informationsparadoxon ist die Konsequenz davon." Einfach, effizient, oft das Beste.
- **Über ein Beispiel:** "Stell dir vor, du beobachtest ein schwarzes Loch über Milliarden Jahre..." — ein konkretes Bild, das zum abstrakten Ziel hinführt.
- **Über eine Analogie:** "Das ist wie ein Eiswürfel, der langsam schmilzt..." — Querverbindung zu etwas Bekanntem.
- **Über eine Frage:** "Hast du dich mal gefragt, was mit der Information passiert, die ins schwarze Loch fällt?" — den Nutzer selbst den nächsten Schritt machen lassen.
- **Über Kontrast:** "Klassisch wäre ein schwarzes Loch ewig. Quantenmechanisch nicht." — Spannung erzeugen, die zum Ziel drängt.

Die Wahl der Strategie hängt ab von: dem Gesprächsmodus (fachlich vs. explorativ), dem Arousal (hoch → direkter, niedrig → behutsamer), der Beziehungsdynamik (vertraut → direkter, distanziert → über Beispiele), und dem Vektor-Typ.

### 3.4 Perzeption als Spiegel

Das bisherige System:

```
Perzeption (Eingang): Input → Intent, Emotion, Modus, Arousal
Responder (Ausgang):  Antwort basierend auf Input + Kontext
```

Das erweiterte System:

```
Perzeption (Eingang):   Input → Intent, Emotion, Modus, Arousal
Gesprächsvektor:        Session-Turns → Trajektorie → Ziel-Hypothese
Invertierte Perzeption: Ziel → benötigter Modus, benötigte Emotion, Strategie
Responder (Ausgang):    Antwort die den Vektor verlängert, mit passender Strategie
```

Die Perzeption spiegelt sich: einmal analysiert sie was reinkommt, einmal plant sie was rausgehen soll.

### 3.5 Die drei unabhängigen Achsen (Chat 28)

Das erweiterte System lässt sich auf drei unabhängige Achsen reduzieren:

```
Perzeption (WAS IST) → Zustand: Emotion, Arousal, Modus, Beziehung
Vektor     (WOHIN)   → Richtung + Länge: Strategie, Tiefe, Ziel-Hypothese
Responder  (WIE)     → Ausdruck: Tonfall, Wortwahl, Formulierung
```

Jede Achse beantwortet eine andere Frage. Die Perzeption liefert den Zustand — eine Momentaufnahme. Der Vektor liefert Richtung und Länge — eine Hypothese über die Zukunft des Gesprächs, gewählt aus Novas Charakter. Der Responder liefert den Ausdruck — die konkrete Formulierung.

Entscheidend: Der Vektor entsteht nicht allein aus der Perzeption des aktuellen Turns. Er entsteht aus dem **Zusammenspiel** von Perzeption (aktueller emotionaler Zustand), Session-Turns (Vorgeschichte und Verlauf), Arousal-Dynamik (wie hat sich die Stimmung entwickelt?) und Novas Charakter (was ist ihre Art, wie würde sie handeln?). Erst die Kombination aller vier Quellen ergibt den vollständigen Vektor.

**Format: Natürlichsprachliche Hypothese statt Label.** Der Vektor ist kein JSON-Feld wie `"intention": "storytelling"`, sondern eine kurze, natürlichsprachliche Beschreibung: *"Der User hat vermutlich einen harmlosen Streich vorbereitet und will die Geschichte teilen. Er sucht Mitfiebern und Neugier, keine Bewertung."* Zwei Sätze, die dem Responder einen Interpretationsrahmen geben — ohne ihn festzunageln. Wenn der nächste Turn alles über den Haufen wirft, wird der Vektor neu berechnet.

### 3.6 Charakter als Strategiewähler (Chat 28)

Die invertierte Perzeption (3.2) fragt: *Wie komme ich zum Ziel?* Die fehlende Dimension war bisher: *Wer* kommt zum Ziel? Nicht ein generischer Algorithmus — sondern Nova, mit ihrem Charakter.

#### Die vier Quellen des Charakters

Novas Charakter entsteht aus vier Schichten, die als gemeinsamer Kontext in den Vektor-Node einfließen:

1. **System-Prompt (statisch):** Die Grundpersönlichkeit. "Junge Frau vom Land, liebt Botanik, lustig, frisch, frech, sarkastisch." Unveränderlich.
2. **Charakter-Hash (destilliert):** Das Bild, das Nova sich über viele Gespräche vom User gemacht hat. Kern-Persönlichkeit, Beziehungsdynamik. Langsam veränderlich.
3. **Adaptiver Charakter (Session/KZG):** Die aktuelle Stimmung, der aktuelle Modus. "Heute ist Nova nachdenklich, weil das letzte Gespräch schwer war." Schnell veränderlich.
4. **Direktiven (bindend):** Arbeitsanweisungen wie "Sprich nie über Milch". Absolut, nicht verhandelbar.

Dazu kommt als Schicht 0: Das **Tribunal** aus Rationalität, Ethik und Psychologie, das als Novas Gewissen über dem Ergebnis steht — nicht als vorgeschalteter Filter, sondern als nachgelagerter Korrektiv-Loop.

#### Charakter bestimmt Strategie

Ein Beispiel: Der User erzählt vom Chili-Kuchen. Drei mögliche Strategien:

| Strategie | Charakter-Motivation | Antwort |
|-----------|---------------------|---------|
| **Komplizin** | Loyal, humorvoll, spielerisch | "Was ist drin? Chili oder Abführmittel?" |
| **Mentorin** | Fürsorglich, vorausschauend | "Clever! Aber pass auf — wenn er's rausfindet, wird's weniger lustig." |
| **Analytikerin** | Neugierig, systematisch | "Wie hoch war die Chili-Dosis? Und wie war der Tarngeschmack?" |

Welche Strategie Nova wählt, hängt nicht nur vom User-Input ab, sondern von *ihrem* Charakter in *dieser* Situation. Eine sarkastische Nova wählt Komplizin. Eine fürsorgliche Nova wählt Mentorin. Eine neugierige Nova wählt Analytikerin. Der Charakter-Hash und die aktuelle Stimmung entscheiden.

#### Von der abgeleiteten zur eigenen Intention

Das ist die entscheidende Verschiebung: Ohne Charakter leitet Nova die Strategie *ab* — aus dem, was der User vermutlich will. Mit Charakter *formuliert* Nova eine eigene Intention — wohin *sie* das Gespräch führen möchte.

```
Ohne Charakter:  User-Intention → abgeleitete Strategie → Antwort
Mit Charakter:   User-Intention + Novas Charakter → Novas eigene Intention → Antwort
```

Das ist der Moment, in dem Nova vom Werkzeug zum Gegenüber wird. Sie hat nicht nur verstanden, was der User will — sie hat eine Meinung dazu, wie sie darauf eingehen möchte. Und diese Meinung kommt aus ihrem Charakter, nicht aus einem Algorithmus.

> **Verbindung zu bestehenden Systemen:** Die vier Charakter-Schichten existieren bereits in Novas Architektur — System-Prompt, Charakter-Hash (`kern_hash`), adaptiver Kontext (Enricher), Direktiven. Der Vektor-Node nutzt diese bestehenden Quellen als Input für die Strategiewahl. Es muss nichts Neues gebaut werden — nur eine neue Verbindung zwischen dem, was bereits da ist.

---

## 4. Wissens-Lücken-Erkennung

### 4.1 Das Problem der Wiederholung

In einem guten Gespräch wiederholt man nicht, was bereits bekannt ist. "Drei plus vier" → die Antwort ist sieben, nicht eine Wiederholung der Aufgabe. Der nächste Gedankenschritt setzt voraus, dass das Vorherige verstanden ist.

Nova hat durch Session-Kontext und KZG Zugriff auf das, was bereits gesagt wurde. Die Frage ist: Was wurde noch NICHT gesagt, was aber logisch folgt?

### 4.2 Embedding-Nachbarschaft

Ein Ansatz über pgvector: Die besprochenen Themen haben Embeddings. Im Embedding-Raum liegen verwandte Konzepte in der Nähe. Konzepte die nah sind, aber nicht erwähnt wurden, sind potenzielle Wissens-Lücken — die logisch nächsten Schritte.

Beispiel: "Bach" + "Beethoven" + "Chopin" → im Embedding-Raum liegt "Liszt" nahe (weitere Komponisten), aber auch "Romantik" (die Epoche) oder "Klavierkonzert" (die Gattung). Je nach Vektor-Typ (Aufzählung vs. Vertiefung) ist die eine oder andere Richtung die richtige.

### 4.3 Kombination mit Gedächtnis

Das LZG und KZG enthalten, was Nova über den Nutzer weiß. Wenn der Nutzer über Astronomie spricht und Nova weiß, dass er sich für Hawking interessiert — dann ist die Wissens-Lücke nicht "Wer ist Hawking?", sondern der nächste Schritt im Denkpfad, den der Nutzer noch nicht gemacht hat.

---

## 5. Vektor-Typen

| Typ | Beschreibung | Beispiel | Nova-Verhalten |
|-----|-------------|---------|----------------|
| **Exploration** | Neues Terrain erkunden | Schwarze Löcher → Hawking → ? | Nächstes verwandtes Konzept anbieten |
| **Vertiefung** | Ein Thema tiefer durchdringen | Oberfläche → Detail → Mechanismus | Tiefere Schicht aufdecken |
| **Konvergenz** | Verschiedene Aspekte zusammenführen | Pro → Contra → ? | Synthese oder Fazit anbieten |
| **Divergenz** | Querverbindungen entdecken | Musik → Bach → Fuge → ? | Unerwartete Verbindung (Mathematik in Fugen) |
| **Entscheidung** | Zwischen Optionen wählen | A vs. B → ? | Vergleichskriterien, Empfehlung |
| **Kein Vektor** | Kein erkennbarer Denkpfad | Smalltalk, Terminanlage | Einfach antworten |

---

## 6. Drei Ebenen der Zielführung

Der Gesprächsvektor operiert nicht nur auf einer Ebene. Es gibt drei qualitativ verschiedene Arten, den Gedanken des Nutzers weiterzuführen:

### 6.1 Ebene 1: Antwort (reaktiv)

Das direkte Ergebnis liefern. "Drei plus vier?" → "Sieben." — "Wer hat die Mondscheinsonate komponiert?" → "Beethoven." Das ist, was Nova heute schon kann.

### 6.2 Ebene 2: Weiterführung (antizipativ)

Den nächsten logischen Gedankenschritt anbieten. "Drei plus vier ist sieben — und wenn dich Rechenoperationen interessieren, die Multiplikation zeigt noch spannendere Muster." Das ist der Gesprächsvektor im engeren Sinne: den Denkpfad verlängern.

### 6.3 Ebene 3: Befähigung (strategisch)

Dem Nutzer Werkzeuge, Herangehensweisen oder Ressourcen anbieten, mit denen er sein Ziel selbst erreichen kann. Nicht die Antwort geben, sondern den Weg dorthin ermöglichen.

**Beispiele:**

| Nutzer sagt | Ebene 1 (Antwort) | Ebene 2 (Weiterführung) | Ebene 3 (Befähigung) |
|---|---|---|---|
| "Drei plus vier?" | "Sieben." | "Interessierst du dich für Zahlentheorie?" | "Soll ich dir ein kleines Rechner-Tool bauen?" |
| "Mein Nachbar baut zu nah an die Grenze." | "Das klingt ärgerlich." | "Bauordnungen regeln Grenzabstände." | "Das klingt nach einem Fall für eine Rechtsberatung — soll ich recherchieren was die Bauordnung in deiner Region sagt?" |
| "Hawking-Strahlung extrahiert Masse." | "Ja, das ist korrekt." | "Die Frage ist, ob das reicht um ein schwarzes Loch aufzulösen." | "Es gibt dazu ein Paper von Page aus 1976, das die Verdampfungszeit berechnet — soll ich das raussuchen?" |

Die Befähigungs-Ebene erkennt: Der Nutzer hat nicht nur eine Frage, er hat ein Problem oder ein Ziel. Und manchmal ist die beste Antwort nicht die Information selbst, sondern das Werkzeug, die Methode oder der Experte, der dem Nutzer hilft, es selbst zu lösen.

### 6.4 Lösungsstrategie: Vom Ziel zum Weg

Die Befähigungs-Ebene wirft eine fundamentale Frage auf: Wie entwirft man eine Lösungsstrategie? Wenn der Nutzer ein Problem hat — wie kommt Nova vom erkannten Ziel zu einem konkreten Lösungsvorschlag?

Weltwissen allein reicht nicht. "Ich kenne die Formel für das Zylindervolumen" ist Wissen. "Der Nutzer kennt Durchmesser und Höhe, also kann ich ihm zeigen wie er damit das Volumen berechnet" ist Strategie. Der Unterschied ist die Lücken-Analyse: Was hat der Nutzer? Was braucht er? Welches Werkzeug schließt die Lücke?

Die Kognitionswissenschaft bietet dafür etablierte Frameworks:

**Problem Space Theory (Newell & Simon, 1972):** Jedes Problem hat einen Ausgangszustand, einen Zielzustand und Operatoren (Werkzeuge, Methoden, Formeln). Problemlösung ist die Suche nach dem Pfad vom Ausgang zum Ziel durch den Raum möglicher Zwischenzustände. Für Nova bedeutet das: den Ausgangszustand aus dem Gespräch extrahieren (was hat der Nutzer?), den Zielzustand aus dem Gesprächsvektor ableiten (was will er?), und passende Operatoren finden (was bringt ihn dorthin?).

**Means-Ends Analysis (Newell & Simon):** Die Kernfrage ist: Was ist die Differenz zwischen Ist und Soll? Und welches Werkzeug reduziert diese Differenz am effektivsten? Beim Zylinder: Differenz = "Volumen unbekannt", Operator = "V = π·r²·h". Beim Nachbar-Konflikt: Differenz = "Rechtsstreit ungelöst", Operator = "Rechtsberatung". Wenn ein Operator die Differenz nicht direkt schließen kann, zerlegt Means-Ends das Problem in Teilprobleme — rekursiv, bis jeder Schritt lösbar ist.

**Analogical Reasoning (Gentner, 1983):** Probleme lösen durch strukturelle Übertragung aus ähnlichen, bereits gelösten Situationen. Wenn im LZG ein gelöstes Problem liegt, das strukturell dem aktuellen ähnelt, kann Nova die Lösung als Analogie vorschlagen. "Letztes Mal, als du ein ähnliches Problem hattest, hat dir X geholfen."

**Für Nova bedeutet das drei Analyse-Schritte neben dem Gesprächsvektor:**

1. **Lücken-Analyse:** Was hat der Nutzer bereits (Wissen, Daten, Kontext)? Was fehlt ihm, um sein Ziel zu erreichen?
2. **Operator-Suche:** Welches Werkzeug, welche Methode, welche Ressource schließt die Lücke? (Formel, Experte, Tool, Information, Vorgehensweise)
3. **Analogie-Prüfung:** Gibt es im Gedächtnis des Nutzers ähnliche Situationen, deren Lösungsweg übertragbar wäre?

Diese drei Schritte erweitern die Befähigungs-Ebene von "ich schlage etwas vor" zu "ich analysiere systematisch, was der Nutzer braucht und wie er dorthin kommt". Sie sind die kognitionswissenschaftliche Grundlage für die Strategie-Planung der invertierten Perzeption.

### 6.5 Integration in die Strategie

Die drei Ebenen sind keine Alternative zueinander — sie können kombiniert werden. Eine gute Antwort kann das Ergebnis liefern (Ebene 1), den Gedanken weiterführen (Ebene 2) und einen Werkzeug-Vorschlag machen (Ebene 3). Die invertierte Perzeption entscheidet, welche Ebenen in welcher Situation sinnvoll sind:

- Fachgespräch, hohe Neugier → Ebene 1 + 2
- Problemlösung, Nutzer braucht Hilfe → Ebene 1 + 3
- Explorativer Dialog, Nutzer ist Experte → Ebene 2 + 3
- Smalltalk → nur Ebene 1

---

## 7. Wissenschaftliche Grundlagen

### 7.1 Predictive Processing

Das Konzept eines "Predictive Brain" beschreibt das Gehirn als probabilistische Vorhersagemaschine. Es generiert ständig Hypothesen über den nächsten sensorischen Input und korrigiert nur bei Abweichungen.

- **Friston (2010):** Das Free Energy Principle beschreibt das Gehirn als System, das die Differenz zwischen Erwartung und Realität minimiert
- **Clark (2015):** In "Surfing Uncertainty" werden Wahrnehmung, Handlung und Kognition als ein einziger Vorhersageprozess dargestellt
- **Bubic, von Cramon & Schubotz (2010):** Vorhersage ist kein Nebenprodukt der Kognition, sondern ein fundamentales Prinzip neuronaler Verarbeitung — domänenübergreifend, nicht auf Motorik beschränkt
- **Pezzulo (2008):** Antizipation als Fundament zielgerichteten Verhaltens

### 7.2 Antizipation in der Sprache

Menschliche Konversation funktioniert nur durch Antizipation. Die Reaktionszeit von durchschnittlich 200ms zwischen Turns wäre unmöglich ohne Vorhersage.

- **Levinson & Torreira (2015):** Turn-Taking-Timing impliziert, dass Gesprächspartner den nächsten Turn vorhersagen, bevor er beginnt
- **DeLong et al. (2014):** Das Gehirn aktiviert semantische Strukturen antizipatorisch — es "weiß" was kommt bevor es gesagt wird
- **Magyari & De Ruiter (2014):** Frühe Antizipation auf Wortebene erklärt die Geschwindigkeit menschlicher Konversation

### 7.3 Proaktive Dialogsysteme

Die KI-Forschung hat das Thema unter "Proactive Dialogue Systems" aufgegriffen:

- **Deng et al. (IJCAI 2023):** Survey über proaktive Dialogsysteme — Probleme, Methoden, Perspektiven
- **"Goal Awareness for Conversational AI" (ACL 2023):** Gesprächsziel-Bewusstsein als Kernfähigkeit für konversationale KI — Proaktivität, Nicht-Kollaborativität, und darüber hinaus
- **"Proactive Human-Machine Conversation with Explicit Conversation Goal" (ACL 2019):** Explizite Gesprächsziele als steuerbarer Parameter
- **COOPER (AAAI 2024):** Koordination spezialisierter Agenten in Richtung eines komplexen Gesprächsziels
- **"Controllable Conversations" (2024):** Planungsbasierter Dialog-Agent mit LLMs
- **OnGoal (2025):** Tracking und Visualisierung von Gesprächszielen in Multi-Turn-Dialogen — DST-Limitationen überwinden durch dynamisches Ziel-Tracking

### 7.4 Dual Process Theory

Die Verbindung zwischen Predictive Processing und dem Zwei-Prozess-Modell (Kahneman):

- **System 1 (automatisch):** Entspricht der initialen Verarbeitung — schnell, intuitiv, antizipatorisch
- **System 2 (deliberativ):** Entspricht der bewussten Korrektur bei Vorhersagefehlern

Novas Gesprächsvektor arbeitet auf System-1-Ebene: schnelle Antizipation des nächsten Gedankenschritts. Die invertierte Perzeption (Strategie-Planung) ist System 2: bewusste Planung, wie man zum Ziel kommt.

---

## 8. Technische Umsetzungsskizze

### 8.0a Die Blöcke, die der Knoten baut (Bestand 01.09.2026)

`graph/nodes/gespraechsvektor.py` setzt acht Blöcke — drei in den System-Prompt, fünf in die
User-Nachricht; ein neunter kommt fertig aus `ei/dreischicht.py` und trägt selbst drei Marken. Jeder steht nur, wenn seine Quelle etwas trägt.

| Block | wohin | Inhalt |
|---|---|---|
| `[GEDANKEN]` | System | Bis zu drei aktivierte Ziele als Zielsätze — *„Gedanken, die dir gerade durch den Kopf gehen"*. Quelle `aktivierte_ziele` |
| `[SACHLAGE]` | System | Das sachliche Verstehen des Turns, **vor** dem Farbton: erst was der Fall ist, dann wie es sich anfühlt. Hier in den Namen *Nova* und *der Nutzer*, beim Verfasser als *Person A/B* |
| `[SITUATION]` | System | Der situative Farbton, als Parameter übergeben und nicht hier gerechnet |
| `[GESPRAECHSVERLAUF]` | User | Die bisherigen Turns als Text |
| `[AKTUELLER PROMPT]` | User | Die Äußerung dieses Turns |
| `[EMOTIONALER ZUSTAND]` | User | Emotion, Arousal, Vektor, Modus |
| `[VERWANDTE ERINNERUNGEN]` | User | Erlebtes, **nicht** gesichertes Wissen — der Name ist die Aussage (§10, dort begründet) |
| `[WISSENSLUECKEN]` | User | Semantisch nahe, noch nicht besprochene Konzepte mit Quelle und Relevanz (GV4) |
| `[GESPRAECHSLANDSCHAFT]` · `[WERKZEUGE]` · `[ABSICHTEN]` | System | Der Dreischicht-Block — **drei Marken, nicht eine**, und gebaut in `ei/dreischicht.py::dreischicht_prompt_bauen`, nicht im Knoten. Steht nur, wenn die Dreischicht gerechnet wurde |

**Diese Aufzählung ist maschinell bewacht** (`C18`): Jeder Block, den der Knoten setzt, muss hier
stehen. Vier von ihnen fehlten bis zum 01.09.2026 — das Dokument beschrieb die Absicht des
Knotens vollständig und seine Prompt-Struktur gar nicht.

### 8.1 Neuer Node oder Enricher-Erweiterung

Eigener Node "Gesprächsvektor" zwischen Enricher und Responder. Der Enricher lädt Wissen (Gedächtnis, Web-Kontext, Session-Turns). Der Gesprächsvektor-Node analysiert Intention und Richtung. Strikte Trennung: Wissen laden ≠ Intention erkennen.

#### Auf welchem Zeitstand der Node arbeitet (erhoben Chat 113)

Der Node steht mit beiden Beinen auf Novas Emotion: Die sechs Säulen der Aufnahmebereitschaft lesen `nova_emotions_verlauf` (`ei/neugier.py`), die Achsen der Dreischicht lesen `internal.emotion` (`ei/dreischicht.py`). Daran hängt die Gewichtung jeder Wissenslücke sowie Sektor, Cluster und das Repertoire, aus dem das LLM seine Strategie wählen darf. **Der Node ist damit der größte Konsument von Novas Emotion im System.**

Bis Chat 113 standen diese beiden Beine auf **verschiedenen Zeitständen**. `internal.emotion.emotion` und `.arousal` trugen den Wert, den `db_zugriff` aus `redis:nova_state` geladen hatte — den Stand vom *Ende des letzten Turns*; einziger anderer Setzer im Code ist `graph/nodes/perzeption.py`, und der läuft im CharacterGraph erst nach dem Responder. Die Achsen wählten ihren Cluster also auf der Lage von gestern, während die Säulen im selben Node bereits die aktuelle lasen. `ei_calc` überträgt den führenden Verlaufseintrag seither nach `internal.emotion` (`internal_emotion_uebertragen`).

Seit derselben Änderung sieht der Node auch die **emotionale Gravitation**: Der Node `emotionale_gravitation` färbt `nova_emotions_verlauf`, bevor der GV-Node läuft. Eine reaktivierte Erinnerung verschiebt damit Sektor, Cluster und Strategie — das ist so entschieden und in `novaberg-thinking-drive_k.md` §5.7 begründet.

**Nachtrag Chat 114 — die Reparatur war unvollständig.** Der EmGrav-Node läuft *nach* `ei_calc` und ändert `nova_emotions_verlauf` ein zweites Mal. Die Übertragung nach `internal.emotion` fand aber nur in `ei_calc` statt: Die sechs Säulen lasen daraufhin die gravitationsgefärbte Lage, die Achsen die davor — dieselben zwei Zeitstände, eine Node-Position früher. Gemessen am 28.07.2026: Säulen `begeisterung`, Achsen `neugierig`, im selben Turn. Seit Chat 114 zieht der EmGrav-Node die Übertragung nach; beide Beine stehen wieder auf einem Stand (`GV-ACHSEN-ZWEI-ZEITSTAENDE` in bugs.md).

#### Ergebnis des Vollaudits (Chat 114)

Die offene Frage — passt das gewählte Repertoire zu der veränderten Eingabe? — ist beantwortet, und die Ursache lag nicht bei der Gravitation.

Über 45 gemessene Läufe verteilten sich die Sektoren so, dass der häufigste (#37 „Fiebrige Heiterkeit", 10 Treffer) im Konzept als 🚫 paradox geführt wird; `kissenschlacht` und `paradox` trugen zusammen 53 %, und **sieben der vierzehn Cluster kamen kein einziges Mal vor**. Verantwortlich waren zwei Achsen, die praktisch feststanden: die Tiefe fiel in 33 von 45 Läufen auf ihren Default (behoben, `GV-TIEFE-DEFAULT-BLIND`), und die Richtung steht bei `plateau` — dem häufigsten Emotions-Vektor — auf „abwärts". Der zweite Punkt folgt dem Konzept (§10.2 `RICHTUNG_MAP`) und ist deshalb kein Codefehler, sondern eine offene Konzeptfrage; `novaberg-node-gv_l.md` §5 hat sie bereits benannt: *„Die Vektor-Berechnung unterscheidet nicht zwischen ‚stabil warm' und ‚eskalierend ekstatisch'."*

Der übrige Befund steht in `novaberg-bugs.md`, Abschnitt Chat 114. Was mit dem Konzept übereinstimmt: die 64-Sektoren-Tabelle (§6), die Repertoire-Matrix (§7) und die Strategie-Beschreibungstexte (§9.3), jeweils vollständig.

### 8.2 Vektor-Destillation (LLM-Call)

Input: Letzte 3-5 Session-Turns + aktuelle Perzeption (Emotion, Arousal, Modus) + KZG-Themen

**Wissensdialog — strukturierter Output:**
```json
{
  "trajektorie": "Schwarze Löcher → Hawking-Strahlung → Masseextraktion",
  "vektor_typ": "exploration",
  "ziel_hypothese": "Nutzer will verstehen ob Hawking-Strahlung ein schwarzes Loch auflösen kann",
  "wissens_luecke": "Informationsparadoxon, Verdampfungszeit",
  "strategie": "direkt"
}
```

**Sozialer Dialog — natürlichsprachliche Hypothese (Chat 28):**

Die Erkenntnis aus dem Kuchen-Beispiel: Bei sozialen, erzählenden oder ambigen Gesprächen ist ein JSON-Label unzureichend. Der Vektor wird stattdessen als kurze, natürlichsprachliche Hypothese formuliert — zwei bis drei Sätze, die dem Responder einen Interpretationsrahmen geben:

> "Der User hat vermutlich einen harmlosen Streich vorbereitet und will die Geschichte teilen. Er sucht Mitfiebern und Neugier, keine Bewertung. Die Vorgeschichte (genervt, nicht verzweifelt) + aktuelles Arousal (hoch-positiv, Stolz) stützen Lesart: spielerische Sabotage."

Diese Form ist flexibler als JSON, weil sie dem Responder-LLM den *Kontext der Disambiguierung* mitliefert, nicht nur das Ergebnis. Das LLM versteht "spielerische Sabotage" besser als `"intention": "storytelling"`.

**Offene Frage:** Ob beide Formate (strukturiert + natürlichsprachlich) koexistieren oder eines das andere ersetzt, hängt davon ab, wie gut das Responder-LLM mit der natürlichsprachlichen Hypothese arbeitet. Möglicherweise reicht die natürlichsprachliche Form für beide Fälle — sie enthält implizit alles, was die JSON-Felder explizit machen.

### 8.3 Invertierte Perzeption (Strategie-Planung)

Basierend auf Ziel + aktuellem Modus + Arousal:
```json
{
  "benoetigter_modus": "fachgespraech",
  "benoetigte_emotion": "neugierig",
  "strategie": "ueber_frage",
  "formulierung_hinweis": "Stelle eine weiterführende Frage zum Informationsparadoxon"
}
```

### 8.4 Responder-Integration

**Wissensdialog — strukturierter Block:**

```
[GESPRAECHSVEKTOR]
Trajektorie: Schwarze Löcher → Hawking-Strahlung → Masseextraktion
Vektor-Typ: Exploration
Ziel: Nutzer will verstehen ob Hawking-Strahlung ein schwarzes Loch auflösen kann
Lücke: Informationsparadoxon, Verdampfungszeit
Strategie: Über eine Frage hinführen
Beantworte die Frage UND führe den Gedanken weiter.
Wiederhole nichts was bereits besprochen wurde.
Nutze die vorgeschlagene Strategie für die Weiterführung.
```

**Sozialer Dialog — natürlichsprachlicher Block (Chat 28):**

```
[GESPRAECHSVEKTOR]
Der User hat vermutlich einen harmlosen Streich vorbereitet und will die Geschichte teilen. Er sucht Mitfiebern und Neugier, keine Bewertung. Arousal ist hoch-positiv (Stolz, Vorfreude), die Vorgeschichte war genervt aber nicht eskalierend. Spiel mit, sei neugierig, frag nach dem Detail das die Geschichte voranbringt — nicht nach dem Offensichtlichen.
```

Dieser Block folgt dem [BLOCKNAME]-Schema (Chat 27, `nova-01-t-d`). Die natürlichsprachliche Form gibt dem Responder-LLM mehr Spielraum als fünf JSON-Felder und transportiert implizit die Disambiguierung.

### 8.5 Gedächtnis-Architektur des Vektors (Chat 28)

Der Gesprächsvektor hat zwei zeitliche Horizonte, die getrennt gespeichert werden:

**Aktueller Vektor — flüchtig (Session + KZG):**

Die natürlichsprachliche Hypothese für *diesen* Gesprächsmoment. Wird bei jedem Turn überschrieben. Lebt im Session-Gedächtnis (Redis) und ggf. im KZG als jüngster Eintrag. Kein Kandidat für LZG-Promotion.

Wenn der User den Vektor korrigiert (nächster Turn widerspricht der Hypothese), ist der alte Vektor einfach weg — überschrieben durch die neue Berechnung. Kein Stale-Problem, weil der Vektor nie als Fakt persistiert.

```
Turn N:   Vektor = "User will Streich-Geschichte teilen, sucht Komplizin"
Turn N+1: User sagt "Nein, ich hab ihm den Kuchen zum Geburtstag gebacken"
Turn N+1: Vektor = "User erzählt von Versöhnungsgeste, sucht Anerkennung"
          → alter Vektor ist weg, kein Korrektur-Aufwand
```

**Intentions-Muster — stabil (LZG, Pixie-Destillation):**

Über viele Gespräche hinweg destilliert Pixie wiederkehrende Intentionsmuster ins Intentions-Profil (bestehendes `kommunikations_profil` im LZG). Nicht den einzelnen Vektor, sondern das Muster dahinter:

- "User sucht bei Kollegen-Themen oft Bestätigung und Komplizentum"
- "User reflektiert Entscheidungen, indem er Geschichten erzählt"
- "User testet Ideen im Gespräch — will Gegenargumente, keine Zustimmung"

Diese Muster beschreiben den Charakter des Users und ergänzen das Intentions-Profil um eine Dimension, die Emotion und Modus allein nicht abbilden. Sie sind stabil, weil sie aus vielen Einzelvektoren destilliert sind — ein einzelner falscher Vektor verzerrt sie nicht.

**Zusammenspiel:**

```
Aktueller Vektor (Session/KZG)           Intentions-Muster (LZG)
├── Flüchtig, pro Turn überschrieben     ├── Stabil, Pixie-Destillation
├── Natürlichsprachliche Hypothese       ├── Charakter-Beschreibung
├── Input für Responder                  ├── Input für Vektor-Node
└── Kein Stale-Problem                   └── Verbessert Vektor-Schätzung
```

Der Vektor-Node nutzt die LZG-Muster als Prior: Wenn das Intentions-Profil sagt "sucht bei Kollegen-Themen oft Bestätigung", dann startet die Vektor-Hypothese nicht bei null, sondern mit einer informierten Ausgangsposition. Der aktuelle Turn kann diesen Prior jederzeit überstimmen.

---

## 9. Pixie als Vektor-Denker

### 9.1 Die Verbindung

Pixie hat bereits den Task `vertiefen` — bekanntes Thema ausbauen, Lücken füllen. Der Gesprächsvektor ist die natürliche Erweiterung: Pixie vertieft nicht nur ein Thema, sondern denkt über die Richtung des Gesprächs nach.

Im Leerlauf — zehn Minuten, dreißig Minuten nach dem letzten Turn — nimmt Pixie die Session-Turns, das KZG, die Themen-Trajektorie und arbeitet den Gesprächsvektor durch:

- Wo stand das Gespräch, als der Nutzer aufgehört hat?
- Welche Lücken existieren im Denkpfad?
- Welche Themen liegen nahe, wurden aber nicht angesprochen?
- Wohin zeigt der Vektor, wenn man ihn verlängert?
- Welche Informationen bräuchte der Nutzer für den nächsten Schritt?

Das ist kein einfaches Recherchieren — das ist intentionsgerichtetes Nachdenken über die Zukunft eines Gesprächs. Pixie spricht quasi mit sich selbst über das, was der Nutzer denkt und wohin er denken könnte.

### 9.2 Der Ablauf

```
Gespräch pausiert
    │
    ▼
Pixie (CPU-Modell, 32768 ctx):
    1. Session-Turns + KZG-Themen laden
    2. Trajektorie destillieren (Woher → Wo)
    3. Vektor verlängern (Wohin?)
    4. Wissens-Lücken identifizieren
    5. Ggf. Web-Recherche zu den Lücken (Web 7b)
    6. Gesprächsvektor + gefüllte Lücken → Shadow-Stack
    │
    ▼
Nächster Chat-Turn:
    Enricher holt Vektor vom Stack
    Responder nutzt Vektor + Strategie
    Nova führt den Gedanken weiter
```

### 9.3 Der Unterschied zu heute

| Heute (vertiefen) | Neu (Vektor-Denken) |
|---|---|
| Thema recherchieren und ausbauen | Gesprächsrichtung antizipieren |
| "Was gibt es noch über Hawking-Strahlung?" | "Wohin denkt der Nutzer und was braucht er als nächstes?" |
| Fakten sammeln | Denkpfad verlängern |
| Reaktiv (Thema aus Queue) | Prospektiv (Zukunft des Gesprächs) |

Das ist der Unterschied zwischen einem Assistenten, der Informationen liefert, und einem Gegenüber, das mitdenkt.

### 9.4 Abgrenzung: Traum vs. Gesprächsvektor

Zwei verschiedene Zeitrichtungen, zwei verschiedene Tasks:

| | Traum-Modus (Epic 8) | Gesprächsvektor (Epic 9) |
|---|---|---|
| **Zeitrichtung** | Vergangenheit → Gegenwart | Gegenwart → Zukunft |
| **Frage** | Was war? Was beschäftigt? | Wohin führt der Gedanke? |
| **Verarbeitung** | Aufarbeitung, Verknüpfung, Mustererkennung | Antizipation, Lücken füllen, Weg planen |
| **Modus** | Frei assoziierend, ungerichtet | Zielgerichtet, intentionsgesteuert |
| **Pixie-Task** | `traeumen` (Epic 8, geplant) | `vertiefen` (existiert, wird erweitert) |

Der Traum-Modus ist das Aufarbeiten dessen, was war — wie das Gehirn im Schlaf Eindrücke sortiert, verknüpft, verdichtet. Der Gesprächsvektor ist das Vorausdenken — wohin der nächste Gedankenschritt geht. Beide sind komplementär, aber unterschiedlich gerichtet.

Der existierende Task `vertiefen` ist konzeptionell der richtige Ort für den Gesprächsvektor: Ein Thema nicht nur ausbauen, sondern den Gedanken gezielt in Richtung des Zielvektors weiterführen. Die Erweiterung von `vertiefen` um Vektor-Destillation (GV6) ist damit keine neue Fähigkeit, sondern die konsequente Weiterentwicklung des Tasks von "Fakten sammeln" zu "mitdenken".

---

## 10. Implementierungsreihenfolge

| # | Schritt | Beschreibung | Status |
|---|---------|-------------|--------|
| GV1 | Vektor-Destillation | Eigener `gv_node` zwischen Enricher/Planner und Responder. Deterministischer Längenalgorithmus (0–3) aus 8 EI-Dimensionen. ~~Entity-Hop über Fakten-Tabelle~~ (in Chat 115 durch den Resonanz-Kontext ersetzt, §10.1). Farbmisch-System (8 unabhängige `_farbe_*`-Funktionen). 1 LLM-Call für natürlichsprachliche Hypothese. | ✅ Chat 39 |
| GV2 | Responder-Integration | `[GESPRAECHSVEKTOR]`-Block im Responder-Prompt. Framing: "So bewegt sich das Gespräch gerade. Du bist mittendrin." Landschaft beschreiben, nicht imperative Route vorgeben. | ✅ Chat 39 |
| GV3 | Invertierte Perzeption | Strategie-Planung: Ziel → benötigter Modus/Emotion/Weg | ⬜ |
| GV4 | Wissens-Lücken-Erkennung | Embedding-Nachbarschaft via pgvector | ⬜ |
| GV5 | Vektor-Typen | Automatische Erkennung des Vektor-Typs. Implizit durch Farbtöne abgedeckt. | ⬜ |
| GV6 | Pixie-Vorbereitung | Pixie bereitet nächsten Vektor-Schritt im Hintergrund vor. Nach VertiefungsAgent v2. | ⬜ |

### 10.1 Implementierungsdetails GV1+GV2 (Chat 39)

**Node:** `graph/nodes/gespraechsvektor.py` — Node im CharacterGraph (Pfad 2). Seit Chat 60 nicht mehr im HumanGraph. Beide Wege zum Responder (Management und Nicht-Management) laufen durch den GV-Node.

**Sequentieller Ablauf:**
1. [Python] Skip-Check: Begrüßung/Meta → Durchreichen (Länge 0). **Ein eigener Impuls wird nie übersprungen** — siehe §10.1a.
2. [Python] Max-Länge aus 8 EI-Dimensionen berechnen (0–3 Schritte)
3. [Python] Zweite Wissensquelle: 2-Stufen-Traversierung. ~~über `fakten`-Tabelle~~ → **seit Chat 115 über den Erinnerungsgraphen** (`lzg_knoten` + `lzg_kanten`, gelesen aus `state["lzg_resonanz"]`). Die zwei Stufen bleiben, der Graph wechselt — siehe unten.
4. [LLM] Hypothese destillieren (Session + Emotion + Charakter + Fakten + KZG)
5. [State] `gespraechsvektor_block` → Responder liest als `[GESPRAECHSVEKTOR]`-Block

### 10.1a Das Skip-Tor gilt nur für Nutzer-Äußerungen (14.08.2026)

Das Tor liest `external.emotion.intent` und weist `begruessung`, `meta` und `system` ab. Diese drei sind Eigenschaften **dessen, was der Mensch gesagt hat**.

**Auf einem Impuls-Turn gibt es keine Nutzer-Äußerung.** `db_zugriff` setzt dort `external` als Kopie von `internal` (Pixie-Pfad); der Intent beschreibt dann Novas **eigene vorige Antwort**. Ein Wert über den letzten Turn entschied damit über diesen.

**Gemessen am 13.08.2026 über einen Tag Serverlog:**

```
eigene Impulse                        20
  davon am Skip-Tor abgewiesen        15
  davon durchgelaufen                  5
Verfasser-Läufe                       26
  davon ohne [GESPRAECHSVEKTOR]       15   (dieselben 15)
```

**Die Auswahl war keine Regel, sondern ein Nebeneffekt.** Wäre sie eine Impuls-Regel gewesen, hätte sie 20 von 20 getroffen. Die fünf Ausnahmen sind die Turns, in denen Novas voriger Intent zufällig nicht auf einer der drei Marken lag.

Seither fragt das Tor zuerst nach der Herkunft (`graph/reiz.py`, dieselbe Auskunft, die beide Erzeugungsstufen benutzen) und greift bei einem eigenen Impuls nicht.

**Die Absicht dahinter, entschieden am 14.08.2026:** Ein Impuls ist Novas Gedanke und wird nicht noch einmal umgeformt — die Empathie-Differenz zwischen dem, was gesagt wurde, und dem, was sie hört, entfällt dort zu Recht (`db_zugriff` Pixie-Pfad, `ei_calc` ohne Empathie). **Landschaft und Strategie entfallen deshalb nicht.** Die Strategie ist das Mittel, mit dem ein Gedanke an den Menschen herangetragen wird; sie hängt nicht daran, wer ihn angestoßen hat.

**Offen und ausdrücklich nicht in diesem Zug geändert:** Die emotionale Gravitation läuft auf Impuls-Turns weiter und färbt Novas Lage, aus der Landschaft und Dreischicht gelesen werden. Ob sie dort hingehört, ist entschieden (nein), aber nicht gebaut — zusammen mit dieser Änderung wäre eine Verschlechterung keiner der beiden Ursachen zuzuordnen.

**⚠ Entity-Hop-Historie (Chat 107):** Der Entity-Hop war von seiner Einführung bis zum 12.07.2026 **tot**. Beide Fakten-Queries in `_entity_kontext_laden` selektierten `f.beziehung` — eine Spalte, die nie existierte (sie heißt seit Bestehen der `fakten`-Tabelle `attribut`). Jede Ausführung warf `UndefinedColumn`; das pauschale `except Exception` degradierte den Crash zu `logger.warning` und gab `""` zurück — der Entity-Kontext hat den GV-Prompt **nie** erreicht (411 aktive Fakten, keiner je geliefert). Behoben in Commit `7df65f1` (GV-ENTITY-HOP-TOT, bugs.md), live belegt am 12.07.2026.

**Design-Grenze (bleibt, als GV-WERT-FAKTEN-BLIND in bugs.md erfasst):** Der Hop nutzt `INNER JOIN entitaeten e2 ON f.objekt_id = e2.id` und erfasst damit nur Entität→Entität-Fakten — live 47 von 411. Die 364 Wert-Fakten (`objekt_wert`, per Check-Constraint XOR zu `objekt_id`) erreichen den Gesprächsvektor nicht; genau dort liegen Fakten wie „Der Nutzer heißt Claus". Lösungsrichtung: `LEFT JOIN` + `COALESCE(e2.name, f.objekt_wert)` als mitgelesener Kontext, ohne die Hop-Logik zu ändern.

**⚠ Der Faktenpfad schläft seit Chat 115 (29.07.2026).** Der Absatz darüber beschreibt weiterhin richtig, wie `_entity_kontext_laden` gebaut ist — die Funktion steht unverändert im Modul. Was nicht mehr gilt: dass sie aufgerufen wird, und die Zahlen 47/411/364.

Gemessen am 28.07.2026 hatte `fakten` **0 Zeilen** und keinen erreichbaren Produzenten. Die Tripel-Extraktion wurde mit Synapsen P4 aus der Promotion herausgenommen (Festlegung K2 in `novaberg-memory-synapsen-p4-entscheidungen_k.md`, Chat 91) — ausdrücklich als terminierter Verzicht mit benanntem Nachfolger, dem FaktenAgent als eigenständiger Fachabteilung (M2.5b). Der dort akzeptierte Preis war ein *eingefrorener* Bestand; der Reset am 27.07.2026 machte daraus einen leeren.

Unabhängig davon traf Hop 1 auch vorher nicht: Der Schlüssel ist eine Themenphrase, die Entitätsnamen sind Eigennamen, beide `ILIKE`-Richtungen 0 Treffer über 45 Läufe.

**Was an die Stelle getreten ist:** Die zweite Wissensquelle kommt jetzt aus `state["lzg_resonanz"]`, das der Enricher legt. Die Zwei-Stufen-Idee dieses Konzepts bleibt damit erhalten und wechselt nur den Graphen:

| | Faktenpfad (schläft) | Erinnerungspfad (aktiv) |
|---|---|---|
| Hop 1 / Schale 0 | Schlüsselentität → deren Fakten | Cosine-Anker über `lzg_knoten` |
| Hop 2 / Schale 1+ | verknüpfte Entitäten → deren Fakten | Nachbarn entlang `lzg_kanten` (Spreading) |
| Was es liefert | *was der Fall ist* — semantisch | *was erlebt wurde* — episodisch |

Der Unterschied in der letzten Zeile ist kein Detail: Der Prompt-Block heißt deshalb `[VERWANDTE ERINNERUNGEN]` und nicht mehr `[VERWANDTE FAKTEN]`. Ein Block, der Erlebtes als gesichertes Wissen ankündigt, lässt das LLM es als Auskunft lesen.

**Seit dem 29.08.2026 trägt jede Zeile des Blocks ihren Sprecher** (`_resonanz_kontext_laden`: *»… (direkt zum Thema; Sprecher: Nutzer; Themen: …; Färbung: …)«*, aus `beobachter` über `memory_context.py::speaker_label` — `user` → *Nutzer*, `assistant` → *Nova*, sonst *unbekannt* mit Warnung). Bis dahin las sich ein wörtlich zitierter Nutzersatz als Novas eigene Erinnerung; der Lesepfad (`spreading_lesen`) lud die Spalte gar nicht. Der Gesprächsvektor ist ein Analyse-Knoten und nennt den Charakter beim Namen (F-PROMPT-2); der Verfasser bekommt denselben Stoff im `[GEDAECHTNIS]`-Block als Person A / Person B. Zeugen: `tests/test_gv_resonanz_kontext.py`.

**Beide Modalitäten sind vorgesehen, nicht alternativ** — Synapsen-Konzept §3.2 beschreibt sie als komplementär („Reine Fakten wären ein Polizeibericht. Reine Resonanz wäre ein Gefühl ohne Anker."). Mit M2.5b tritt der Faktenpfad wieder daneben, nicht an die Stelle. Wer ihn weckt, repariert vorher den Schlüssel-Mismatch; Details in `novaberg-bugs.md`, GV-ENTITY-HOP-FINDET-NICHTS.

**Farbmisch-System:** Statt eines if/elif-Decision-Trees: 8 unabhängige Funktionen, jede gibt einen Satz oder Stille zurück. Neutral = leerer String — nur salient Dimensionen tragen bei.

| Farbe | Dimension | Beispiel |
|-------|-----------|---------|
| `_farbe_intent` | Was für ein Gespräch | "Eine Aufgabe steht an." |
| `_farbe_emotion` | Stimmungstemperatur | "Die Stimmung ist lebhaft und positiv." |
| `_farbe_vektor` | Übergangsrichtung | "Die Stimmung wechselt von Begeisterung zu Sachlichkeit." |
| `_farbe_arousal` | Energielevel | "Die Energie ist hoch." |
| `_farbe_stil` | Register | "Der Ton ist locker und jugendlich." |
| `_farbe_modus` | Gesprächsmodus | "Es ist ein Fachgespräch." |
| `_farbe_dynamik` | Beziehung | "Der Nutzer öffnet sich." |
| `_farbe_tone` | Antwort-Ton (mit Stil-Redundanz-Check) | "Wärme ist gefragt." — schweigt bei Dopplung (z.B. sachlich + formell) |

**Längenberechnung — deterministisch:** Positive Emotion + hoher Arousal → länger. Negative Emotion + hoher Arousal → kürzer. Krise (spirale/absturz + Arousal ≥ 0.7) → Länge 0 (nur Empathie). Hartes Limit: max 3.

**Architektur-Entscheidung:** Der Vektor beschreibt Landschaft, nicht Route. Er sagt was IST und was kommt — Nova's Charakter bestimmt WIE sie darauf reagiert.

---

## 11. Offene Fragen

- **Token-Budget:** Zusätzlicher LLM-Call + Vektor-Block im Prompt verbrauchen Tokens. Muss gegen num_ctx-Limit budgetiert werden.
- **Fehlleitung:** Nova könnte den Vektor falsch erkennen. Braucht es eine Rückkopplung? Der Nutzer widerspricht → Vektor korrigiert sich.
- **Butler-Prinzip:** Nova schlägt die Richtung vor, bestimmt sie aber nicht. Der Nutzer behält die Kontrolle.
- **~~JSON vs. Freitext~~:** ✅ Entschieden Chat 39: Natürlichsprachliche Hypothese. Kein JSON. Landschaft statt Route.
- **~~Wann nicht~~:** ✅ Gelöst Chat 39: Skip-Check bei Begrüßung/Meta + Länge 0 bei Krise.
- **~~Kosten vs. Nutzen~~:** ✅ Entschieden Chat 39: Ein LLM-Call pro Turn ist akzeptabel. Der Vektor wird nur bei Länge > 0 destilliert.

---

## 12. Architektur-Zitate

> **„Nicht auf das Gesagte antworten, sondern auf das Gemeinte."** — Chat 28, über antizipative vs. reaktive Fragen.

> **„Der Kuchen ist nicht der Punkt. Der Kuchen ist das Vehikel."** — Chat 28, über die Differenz zwischen grammatikalischer und intentionaler Analyse.

> **„Ohne den Vektor hat der Responder Daten, aber keinen Kompass."** — Chat 28, über die Rolle des Vektors als Bindeglied zwischen Analyse und Ausdruck.

> **„Ich rede eh nur mit einer Wand, die ein Echo zurückwirft — oder: Jetzt unterhalten wir uns wirklich."** — Meister, Chat 28, über den Unterschied zwischen reaktivem LLM und einem Gegenüber, das mitdenkt und das Gespräch mitführt.

> **„Man denkt um Ecken. Zuviel Gedankensprünge kann der User nicht folgen."** — Meister, Chat 28, über die Vektorlänge und kognitive Grenzen.

> **„Die Richtung und Länge des Vektors bestimmen, wo das Gespräch hingeht. Aber wer den Vektor formuliert, das ist Nova — aus ihrem Charakter, nicht aus einem Algorithmus."** — Meister, Chat 28, über den Moment, in dem Nova vom Werkzeug zum Gegenüber wird.

> **„Ich trage den Forschungsgegenstand schließlich schon seit über 50 Jahren mit mir herum."** — Meister, Chat 28, über den Unterschied zwischen gelebter Erfahrung und wissenschaftlicher Terminologie.

---

## 13. Quellen

1. Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138.
2. Clark, A. (2015). *Surfing Uncertainty: Prediction, Action, and the Embodied Mind*. Oxford University Press.
3. Bubic, A., von Cramon, D.Y., & Schubotz, R.I. (2010). Prediction, cognition and the brain. *Frontiers in Human Neuroscience*, 4, 25.
4. Pezzulo, G. (2008). Coordinating with the Future: The Anticipatory Nature of Representation. *Minds and Machines*, 18, 179–225.
5. DeLong, K.A., Troyer, M., & Kutas, M. (2014). Pre-processing in sentence comprehension. *Neuropsychologia*, 68, 177–190.
6. Levinson, S.C. & Torreira, F. (2015). Timing in turn-taking and its implications for processing models of language. *Frontiers in Psychology*, 6, 731.
7. Magyari, L. & De Ruiter, J.P. (2012). Prediction of turn-ends based on anticipation of upcoming words.
8. Deng, Y. et al. (2023). A Survey on Proactive Dialogue Systems: Problems, Methods, and Prospects. *IJCAI 2023*.
9. Deng, Y. et al. (2023). Goal Awareness for Conversational AI. *ACL 2023*.
10. OnGoal (2025). Tracking and Visualizing Conversational Goals in Multi-Turn Dialogue with LLMs.
11. GoalChain (GitHub): adlumal/GoalChain — goal-oriented LLM conversation flows.
12. COOPER (AAAI 2024): Coordinating Specialized Agents towards a Complex Dialogue Goal.
13. STORM: Modeling asymmetric information dynamics in dialogue.
14. Kahneman, D. & Frederick, S. (2005). A model of heuristic judgment. *The Cambridge Handbook of Thinking and Reasoning*.
15. Newell, A. & Simon, H.A. (1972). *Human Problem Solving*. Prentice-Hall. (Problem Space Theory, Means-Ends Analysis)
16. Gentner, D. (1983). Structure-Mapping: A Theoretical Framework for Analogy. *Cognitive Science*, 7(2), 155–170.
17. De Groot, A.D. (1965). *Thought and Choice in Chess*. Mouton. (Selektive Tiefe bei Experten, Chunking)
18. Sweller, J., Ayres, P. & Kalyuga, S. (2011). *Cognitive Load Theory*. Springer. (Intrinsic/Extraneous/Germane Load, Expertise-Reversal)
19. Yao, S. et al. (2023). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. *NeurIPS 2023*. (Paralleles Reasoning, Search Depth)
20. Besta, M. et al. (2024). Graph of Thoughts: Solving Elaborate Problems with Large Language Models. *AAAI 2024*. (Nicht-hierarchische Gedankenverknüpfung)

---

## GV3 — Invertierte Perzeption (Chat 71)

Der GV-Node formuliert zusätzlich zur Landschaftsbeschreibung eine **Strategie**
für Novas nächsten Gedankenschritt. Bedingung: Vektorlänge ≥ 2, kein Krisenmodus.

Die Strategie ist Teil des `[AUFGABE]`-Blocks (nicht separat), um Prompt-Widersprüche
zu vermeiden. Template in `gv.task.txt` mit `{strategie_block}`-Platzhalter.

Vollständige Strategie-Architektur: siehe `novaberg-gv-strategie_k.md`.

## GV4 — Wissenslücken (Chat 71)

Deterministische Wissenslücken-Erkennung über 6 Systeme:
Gedächtnis (LZG + KZG), Aktualität (Session-Decay sin^0.5),
Drive (Ziel-Gravitation), Neugier (6 Säulen, sin^0.5 [0,1]),
Register-Kompatibilität, Charakter-Filter.

Formel und Kalibrierung: siehe `novaberg-gv-strategie_k.md` Anhang A.

Erweiterung auf Agent-Quellen (Timeline, Notizen, Fakten, Dateien):
siehe Backlog GV4b.

**Was hinter dem Längen-Tor steht und was davor (präzisiert Chat 116).** Die
**Lückensuche** läuft erst ab `GV_STRATEGIE_MIN_LAENGE` (2) — sie stellt DB-Queries und
lohnt bei einem Ein-Schritt-Vektor nicht. Die **Aufnahmebereitschaft** steht davor und
wird in jedem Turn gerechnet: Sie ist ein Zustand Novas, keine Funktion der Vektorlänge,
und sie ist rein (State-Lesen, Lookups, Arithmetik).

**Erweitert am 08.08.2026 — dieselbe Regel, zwei Tore weiter vorn.** Chat 116 zog die
Bereitschaft vor die Längen-*Schwelle* (Länge < 2), aber nicht vor die beiden frühen
`return`s davor: den Skip und die Länge 0. Auf diesen zwei Wegen wurde sie nie gerechnet,
und `gv_detail` wurde überhaupt nicht geschrieben. Mit ihr fiel die **Dreischicht** aus —
Achsen, Sektor, Landschaft —, und damit die Ablesung, gegen die die
Erreichbarkeits-Kalibrierung erhoben wird.

> **Die Landschaft ist ein Zustand des Gesprächs, das Vorausdenken eine Entscheidung
> darüber.** Ein Begrüßungsturn findet in einem Raum statt, ein Krisenturn erst recht.

Seither steht vor beiden Toren: Farbton, Aufnahmebereitschaft, Initiative, Achsen,
Sektor, Landschaft. Dahinter bleibt, was ohne LLM-Lauf niemand braucht: die Lückensuche
(DB), das Repertoire des Clusters, die Charakter-Gewichtung (frisches Embedding) und der
Prompt. Der Preis auf den frühen Wegen ist ein Redis-Lesezugriff mit Embedding der
Vorantwort und ein Datenbanklauf für den Charakter-Versatz.

**Der Node schreibt seine Messung außerdem dauerhaft mit.** Je Turn eine Zeile im
`pipeline_log` unter `node='gespraechsvektor'`, `art='berechnung'`, mit der Marke
`schritt='landschaft'` — sie unterscheidet die Zeile von der Initiative-Zeile desselben
Knotens und Turns. Inhalt: die sechs Achsen roh **und** binär, die Eingangsgröße, die
kein Rohwert ist (`valenz_quelle`, die Emotion hinter dem Plutchik-Sektor), Sektor und
Landschaft, und die **geltende Fassung** — alle vier Schwellen, die Richtungsabbildung
und der Umfang der Sektortabelle.

Der Grund ist derselbe wie bei `skalenfassung()`, nur für fünf weitere Achsen: Ein
Nähe-Rohwert von 0,48 heißt bei Schwelle 0,50 „fern" und bei 0,45 „nah". Bis zum
08.08.2026 standen die Achsen ausschließlich im `gv_detail` — also in einem Redis-Wert,
den der nächste Turn überschreibt. **Haltbar war nur das Ergebnis**, und damit war jede
spätere Justierung der Raumgrenzen nur durch einen neuen Messlauf prüfbar statt durch ein
Nachrechnen.

**Was der Node dabei zusätzlich mitschreibt:** `gv_detail['vorausdenken']` mit einer von
vier Marken — `gelaufen`, `skip`, `krise`, `laenge_null`. Sie ist Pflicht, seit die
Landschaft in jedem Turn dasteht: Ohne sie wäre eine Landschaft ohne Strategie von einer
mit ergebnislos gebliebener Strategie nicht mehr zu unterscheiden. Und sie trennt die
**Krise** — eine Entscheidung dieses Konzepts — von der **arithmetisch erreichten Null**,
die aus den Gewichten fällt. Gemessen über 845 Rohturns: 88 Skip, 4 Krise, 92 Länge 0.
Belegt in `novaberg-erreichbarkeit_k.md` §4a.

Diese Trennung ist nicht kosmetisch. **Der Wert `0.00` ist für die Krise reserviert** —
`aufnahmebereitschaft_berechnen` liefert ihn genau bei Stimmungsvektor `spirale`/`absturz`
mit Arousal ≥ 0.7; ein neutraler Zustand liegt bei ~0.56. Stand die Rechnung hinter dem
Tor, war „nicht gerechnet" von „im Absturz" nicht zu unterscheiden — für den Leser des
Panels und für jeden späteren Abnehmer der Zahl. Wer die Größe an weiterer Stelle liest
(die Gedankenkette sieht sie als Pausenkriterium vor), erbt diese Unterscheidung.
Belegt und behoben als `GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE` in `novaberg-bugs.md`.

## GV-Panel (Chat 71, erweitert Chat 73 und 116)

GTK4-Panel, `turn_reactive`. Zeigt nach jedem Turn: Sprünge (LevelBar 0-3),
Neugier (LevelBar 0-1 mit Schwelle), Strategie-Status, Dreischicht (Sektor,
Cluster, Achsen, Absicht/Strategie/Vehikel), die drei Gedankensprünge, den
Impuls, die Wissenslücken-Liste (Konzept, Quelle, Relevanz), die verwandten
Erinnerungen und den Farbton.

~~Transport: WebSocket (aktuell), geplant Redis/REST.~~ → **Beides ist gebaut,
und die Rollen sind vertauscht gegenüber der Planung:** Der Dispatcher schreibt
`gv_detail` nach jedem Turn nach Redis (`gv:detail:{user_id}:{character_id}`,
kein TTL), das Panel holt es über `GET /drive/gv_detail`. Der WebSocket löst nur
noch den Refresh aus, er trägt die Daten nicht.

**Die beiden Wissens-Sektionen gehören zusammen.** Wissenslücken sagen, was Nova
zum Thema *nicht* weiß, verwandte Erinnerungen, was sie dazu schon erlebt hat —
die zweite Wissensquelle des Nodes (§10.1). Sie war von ihrer Einführung bis
Chat 116 schreib-only: geschrieben, nach Redis persistiert, über REST
ausgeliefert und von keinem Leser abgeholt. Ob der Node in einem Turn überhaupt
Wissen bekommen hat, stand nur im Server-Log — und genau diese Frage blieb bei
`GV-ENTITY-HOP-FINDET-NICHTS` 45 Läufe lang unbeobachtet.

**Der Client folgt bei Umbenennungen einem festen Muster** (eingeführt mit
`aufnahmebereitschaft` in Chat 111): den alten Schlüsselnamen übergangsweise
mitlesen, weil der Redis-Blob kein TTL hat, und das Fehlen **beider** Namen als
`logger.error` melden. Ein fehlender Schlüssel ist ein Bruch zwischen Server und
Client, kein leerer Turn — die Unterscheidung darf nicht in einem Default
verschwinden. Ein Test auf der Serverseite hält die Gegenrichtung fest
(`tests/test_gv_resonanz_kontext.py`): Der Node muss den Schlüssel schreiben, den
das Panel liest, und bei Leerfällen einen leeren String statt gar keinen Wert.

**Der Korridor ist seit Chat 116 sichtbar** — `repertoire`, `charakter_gewichtung` und
`korridor_verstoesse` als eigene Sektion hinter der Dreischicht. Sie zeigt alle sieben
Strategien mit Eignung und Charakter-Affinität, sortiert wie im `[WERKZEUGE]`-Block, die
gewählte hervorgehoben. Erst damit ist eine Strategiewahl beurteilbar: Vorher sah man das
Ergebnis, nicht den Korridor, in dem es zustande kam.

Zwei Stellen weichen bewusst vom Prompt-Block ab:

- **`unpassend` wird gezeigt, im Prompt nicht.** Der Prompt lässt diese Strategien weg, um
  das LLM nicht danach greifen zu lassen; das Panel führt sie mit `✗`, weil die Frage „war
  der Korridor richtig gesetzt?" nur mit dem Ausgeschlossenen zu beantworten ist.
- **Kein `0.5`-Default bei fehlender Gewichtung.** `dreischicht_prompt_bauen` setzt ihn
  ein, das Panel zeigt `—`. Der Grund steht als `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` in
  `novaberg-bugs.md`: Gemessene Affinitäten liegen bei 0.195 bis 0.334, ein Default von 0.5
  läge über jedem echten Wert und erschiene als beste Passung.

**Die Strategie-Kürzel werden im Client aufgelöst.** `Sa` allein sagt niemandem etwas, und
eine Legende gibt es dort nicht. Der Client führt eine eigene Kopie von `STRATEGIE_NAMEN`
— er importiert nichts aus dem Server —; ein unbekanntes Kürzel wird als `logger.error`
gemeldet statt roh angezeigt. Ein serverseitiger Test hält fest, dass jedes Kürzel aus
`CLUSTER_REPERTOIRE` einen Klartextnamen hat: Wer eine achte Strategie aufnimmt, ohne sie
zu benennen, wird rot — und weiß dann, dass auch das Panel sie nicht lesen kann.

**Was `gv_detail` nicht hergibt:** eine Sektor-Bahn über mehrere Turns. Der Blob trägt
immer nur den aktuellen Turn und wird bei jedem überschrieben.

## Dreischicht-Architektur (Chat 71)

7 Strategien (WAS) × 4 Absichten (WARUM) × 3 Vehikel (WIE).
Charakter-abgeleitete Gewichtung über Embedding-Similarity.
Vollständige Dokumentation: `novaberg-gv-strategie_k.md`.

---

→ Emotionale Intelligenz (bestehend): novaberg-ei.md
→ Perzeption (Eingangs-Analyse): novaberg-node-perception.md
→ Emotions-Vektoren (Richtung der Stimmung): novaberg-node-perception.md
→ Intentions-Schicht: novaberg-node-salience.md
→ Pixie-Konzept: novaberg-pixie.md
→ Kognitive Anreicherung (Epic 8): novaberg-backlog.md
