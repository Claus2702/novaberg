# Novaberg — Node: Gesprächsvektor (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-node-gv_k.md`](novaberg-node-gv_k.md) · Bauplan und Umstellung: [`novaberg-node-gv_b.md`](novaberg-node-gv_b.md) · Diskussion und Ergänzungen: [`novaberg-node-gv_e.md`](novaberg-node-gv_e.md) · Messungen: [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 8. Technische Umsetzungsskizze

### 8.0a Die Blöcke, die der Knoten baut (Bestand 01.09.2026)

`graph/nodes/gespraechsvektor.py` setzt acht Blöcke — drei in den System-Prompt, fünf in die
User-Nachricht; ein neunter kommt fertig aus `ei/dreischicht.py` und trägt selbst drei Marken. Jeder steht nur, wenn seine Quelle etwas trägt.

| Block | wohin | Inhalt |
|---|---|---|
| `[GEDANKEN]` | System | Bis zu drei aktivierte Ziele als Zielsätze — *„Gedanken, die dir gerade durch den Kopf gehen"*. Quelle `aktivierte_ziele` |
| `[SACHLAGE]` | System | Das sachliche Verstehen des Turns, **vor** dem Farbton: erst was der Fall ist, dann wie es sich anfühlt. Hier in den Namen *Nova* und *der Nutzer*, beim Verfasser als *Person A/B* |
| `[SITUATION]` | System | Der situative Farbton, als Parameter übergeben und nicht hier gerechnet. **Seit dem 10.09.2026 beschreibt er den Raum aus beiden Seiten** — *Nova ist offen und zugewandt, der Nutzer haelt Abstand* statt einer Aussage ueber den Nutzer aus Novas Werten (Setzung des Eigentuemers, 10.09.2026). Hier in den Namen des GV, der analysiert; derselbe Farbton geht in den `[SZENE]`-Block des Responders und traegt dort die Anrede |
| `[GESPRAECHSVERLAUF]` | User | Die bisherigen Turns als Text |
| `[AKTUELLER PROMPT]` | User | Die Äußerung dieses Turns |
| `[EMOTIONALER ZUSTAND]` | User | Emotion, Arousal, Vektor, Modus |
| `[VERWANDTE ERINNERUNGEN]` | User | Erlebtes, **nicht** gesichertes Wissen — der Name ist die Aussage (§10, dort begründet) |
| `[WISSENSLUECKEN]` | User | ~~Semantisch nahe, noch nicht besprochene Konzepte~~ → seit 12.09.2026 **Themen** aus Novas Bestand nah am Gespräch, die der Nutzer nicht berührt hat — die Lücke beim Nutzer, mit Quelle und Relevanz (GV4, `novaberg-gv-strategie_k.md` A.0) |
| `[BITTE]` | User | seit 12.09.2026, wenn die Entscheidung *Bitte zuerst* steht — immer bei `intent = task`, bei `knowledge` als Pflicht, außer das Zuwendungsrad des Paares gibt der Neugier Anlass; nie auf einem Impuls. SPRUNG 1 erfuellt die Bitte, Luecken und offene Fragen duerfen danach anschliessen (`graph/reiz.py::request_first`, Eintrag `gv_detail['bitte_zuerst']`, `novaberg-gv-strategie_k.md` A.0) |
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

> **Hinweis:** Der Unterabschnitt *Ergebnis des Vollaudits* von §8.1 — 45 gemessene Läufe, die Verteilung der Sektoren und die offene Konzeptfrage zur Richtung bei `plateau` — steht in [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md), unter „Aus §8.1“.

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

## Aus §10 — Implementierungsreihenfolge

Die Einleitung von §10 mit der Tabelle der Schritte GV1 bis GV6 steht in [`novaberg-node-gv_b.md`](novaberg-node-gv_b.md), der Unterabschnitt *Die Decke ist nicht 3, sie ist modusabhängig …* (`[gemessen 12.09.2026]`) in [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md). Der Absatz *Architektur-Entscheidung*, der im ungeteilten Konzept hinter diesem Unterabschnitt stand, steht hier am Schluss von §10.1.

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

## GV3 — Invertierte Perzeption (Chat 71)

Der GV-Node formuliert zusätzlich zur Landschaftsbeschreibung eine **Strategie**
für Novas nächsten Gedankenschritt. Bedingung: Vektorlänge ≥ 2, kein Krisenmodus.

Die Strategie ist Teil des `[AUFGABE]`-Blocks (nicht separat), um Prompt-Widersprüche
zu vermeiden. Template in `gv.task.txt` mit `{strategie_block}`-Platzhalter.

> **Seit dem 10.09.2026 gibt es zwei Fassungen, und die Auswahl folgt dem Ausloeser.**
> Die Aufgabe fragt, was den Ausloeser beschaeftigt und welcher Gedanke bei ihm als
> naechstes kommt — der Knoten soll dessen Absicht erkennen und **weiterfuehren**; darauf
> beruht, dass Nova beteiligt wirkt statt nur zu antworten.
>
> | Fassung | wann | erste Frage |
> |---|---|---|
> | `gv.task.txt` | Nutzer-Turn, auch der Thinker-Retry | *Was beschaeftigt den Nutzer gerade?* |
> | `gv.task.impuls.txt` | `reiz_herkunft = eigener_impuls` | *Was beschaeftigt Nova gerade?* |
>
> **Der Grund ist derselbe wie beim Skip-Tor** (§10.1a): Auf einem Impuls-Turn gibt es
> keine Nutzer-Aeusserung, die weitergefuehrt werden koennte — der Faden ist Novas
> eigener. `[gemessen 10.09.2026]` **154 von 1350 Turns** tragen diese Herkunft (11,4 %).
> Die Impuls-Fassung nennt den Anstoss ausdruecklich; ohne diesen Satz waere die gedrehte
> Frage nur eine Umbenennung.

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

> **Seit dem 10.09.2026 ist beides ablesbar.** Die Zeile `strategie_tor` (`node='gespraechsvektor'`,
> `art='berechnung'`) trägt `max_laenge`, `min_laenge`, `strategie_aktiv`, `aufnahmebereitschaft`
> **und** die Zahl der gefundenen Lücken und offenen Fragen. Ohne die beiden Ergebnisse wäre
> *Tor zu* von *Tor offen, nichts gefunden* nicht zu trennen — zwei Fälle mit derselben leeren
> Antwort.
>
> *Die beiden `[gemessen 10.09.2026]`-Absätze, die hier folgten — was die erste Messung am Tor ergab und dass die Aufnahmebereitschaft dabei nie die Hürde ist —, stehen in [`novaberg-node-gv_m.md`](novaberg-node-gv_m.md), unter „Aus dem Anhang GV4“.*

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

**Die beiden Wissens-Sektionen gehören zusammen.** ~~Wissenslücken sagen, was Nova
zum Thema *nicht* weiß~~ → **seit dem 12.09.2026 zwei Listen** (`novaberg-gv-strategie_k.md`
Anhang A.0): die Lücke **beim Nutzer**, zu der Nova lenkt, und die Lücke **bei Nova**, aus
der sie nachfragt — der Satz hier und §4.3 dort hatten Verschiedenes behauptet. Verwandte
Erinnerungen sagen, was sie dazu schon erlebt hat —
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
