# Novaberg — Die Lage-Analyse (Konzept)

**Absicht:** Vor jeder Antwort erfasst das System je Turn, worum es geht, was der Nutzer vermutlich will und welche Objekte mit welchen gedeckten und offenen Eigenschaften im Spiel sind — fortgeschrieben über die Turns.
**Stand:** 19.09.2026
**Umsetzung:** `novaberg-featureliste.md` §6 — ⏫ *Frames · Skills · Task-Orchestration · Cognitive Pipeline — im Bau als Lage-Konzept* 🟠, dazu ↳ *Scheibe 12 A* bis *F* je 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) · [`novaberg-thinking-lage_b.md`](novaberg-thinking-lage_b.md) · [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md) · [`novaberg-thinking-lage_m.md`](novaberg-thinking-lage_m.md)
**Entschieden:** 24 · **Offen beim Meister:** 4 (Liste in [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md))

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lage-Analyse — die erste gebaute Scheibe der Verstehens-Schicht
**Pfad:** novaberg/docs/novaberg-thinking-lage_k.md
**Typ:** Konzept (`_k`)
**Quellen:** `novaberg-thinking-frames_k.md` · `novaberg-thinking-cognitive-pipeline_k.md` · `novaberg-thinking-drive_k.md` (Herkunft jeweils dort) · Messungen vom 27./28.08.2026

**Verhältnis zu den Schwester-Dokumenten:** Dieses Dokument erfindet nichts neu. Es schneidet aus den drei Thinking-Konzepten die **erste baubare Scheibe** und legt fest, was davon jetzt entsteht und was ausdrücklich Konzept bleibt. Die Begriffe (Frame, Slot, Akutheit) sind dort definiert und werden hier benutzt, nicht wiederholt.

---

> **Herkunft der Beispiele:** Alle wörtlichen Gesprächsbeispiele in diesem
> Dokument (Geburtstag, Rasen, Kräuterbeet, das Gelb, die Themenkette
> Kino→Krieg) sind **synthetisch** — für dieses Konzept konstruiert, ohne
> Bezug zu einem echten Gespräch. Die Zahlen in §1 sind echte Messwerte;
> sie zitieren keinen Wortlaut.

## Wo die Abschnitte stehen — § → Datei

Seit dem 19.09.2026 ist das Konzept in fünf Teilen: dieses Dokument (Absicht), [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) (Ausarbeitung), [`novaberg-thinking-lage_b.md`](novaberg-thinking-lage_b.md) (Bauplan und Umstellung), [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md) (Diskussion und Ergänzungen) und [`novaberg-thinking-lage_m.md`](novaberg-thinking-lage_m.md) (Messungen). Die Abschnittsnummern sind geblieben; ein Verweis der Form `novaberg-thinking-lage_k.md §4` löst sich über diese Tabelle auf. Wo eine Scheibe auf mehrere Teile verteilt ist, steht ihre Überschrift in jedem davon.

| § | Abschnitt | Datei |
|---|---|---|
| Kopf | der bisherige Stands-Kopf (`**Stand:**`) | `_m`, *Bisheriger Kopf* |
| §1 | Anlass — die Messungen, die den Schnitt begründen | `_k` |
| §2 | Was die Konzepte bereitstellen | `_k` |
| §2a | Die wissenschaftliche Prüfung, dazu der Absatz *Eine Abweichung vom Pipeline-Konzept* | `_k` |
| §3 | Die Lage — das Artefakt, die vier Festlegungen | `_k`; die Nachträge zu Festlegung 1 (Formprüfung, 12./13.09.2026) in `_t` §3 |
| §3a | Der Kontext als Blase — das Zielbild | `_k` |
| §4 | Die Scheiben des Umbaus — Überschrift und Nachtrag | `_b` |
| §4 Scheibe 1 · 2 · 3 · 4 · 6 · 7 · 8 · 9 · 10 | je Scheibe Anlass, Bauweise, *was die Scheibe nicht tut*, `ZIEL` / `TEST` / `MESSUNG`, Reihenfolge; dazu *Gebaut*, Zeugen, zweite Kontrolle und Preis | `_b`; Messung, Betrieb und Bestand je Scheibe unter derselben Überschrift in `_m` §4 |
| §4 Scheibe 3, Nachträge | *der eigene Zug* (29.08.), *die Namen des Lesers* (29.08.) | `_b` |
| §4 Scheibe 5 | Anlass, Bauweise, `ZIEL` / `TEST` / `MESSUNG` | `_b`; der Bauabsatz (*Gebaut*, Messung, Betriebsbeleg in einem Absatz) in `_m` §4 |
| §4, zwischen Scheibe 5 und 6 | Der Gesprächskontext im Client | `_b` |
| §4, zwischen Scheibe 9 und 10 | Die Betriebsmessung der Kette | `_m` §4 |
| §4 Scheibe 11 | Anlass, `ZIEL` / `TEST` / `MESSUNG`, Zeugen und Gegenproben, zweite Kontrolle, *Preis und Offenes* | `_b` |
| §4 Scheibe 11 | *Die Absicht des Eigentümers* | `_k`, *Aus §4* |
| §4 Scheibe 11 | die drei Tabellen, Schreibweg, Bindung, Zeitanker, Rückweg, Prompt-Regeln | `_t` §4 |
| §4 Scheibe 11 | Messungen: Labor Arm A und B, Betrieb, Bestand, Wechsel der Wert-Regel | `_m` §4 |
| §4 Scheibe 12 | Status-Zeile, Anlass, Entwurf (Teile A–F), Reihenfolge, Vorbedingung | `_b` |
| §4 Scheibe 12 | *Das Kriterium der Zuordnung* | `_k`, *Aus §4* |
| §4 Scheibe 12 | Die Entscheidungen des Eigentümers (13. und 14.09.2026), im Wortlaut | `_e`, D |
| §4 Scheibe 12 | *Offen für den Bau* | `_e`, D; der erste Punkt (*Die Nähe*, samt *Zwei Schwellen und der geeichte Wortlaut*) in `_m` §4 |
| §4 Scheibe 12 | Teil C2, D2, *Die Zustimmung kommt an*, F und A Punkt 1, E2 samt Nachträgen, E3, E1, D1, *Die Objektwahl der Lage*, C1, B, A — Bauberichte, Zeugen, zweite Kontrolle, Offenes, in der Reihenfolge des Originals | `_b`; die Messungen je Teil unter derselben Überschrift in `_m` §4 |
| §4 Scheibe 12, Teil C2 | die Entscheidung über den Abstand (16.09.2026, 20:55 UTC) samt Rechnung | `_e`, D |
| §4 Scheibe 12, Teil E2 | die Entscheidung über die Wahrscheinlichkeit (18.09.2026) | `_e`, D |
| §4 Scheibe 12 | die Entscheidungen vom 19.09.2026 | `_e`, D |
| §5 | Was ausdrücklich nicht gebaut wird | `_k` |
| §6 | Verweise, Quellen der Prüfung | `_k` |
| Schlusszeile | *Stand 28.08.2026. Erstfassung …* | `_e`, F |
| — | Register der Entscheidungen, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung | `_e`, A, B, C, E |

## 1. Anlass — die Messungen, die den Schnitt begründen

Alle vier vom 27./28.08.2026, alle am Produktivsystem:

**Die Rückfragen haben keinen Gegenstand.** Über 84 Schlussfragen des produktiven Paares: 33 % beginnen als Angebot (*„Sollen wir …"*), 23 % zusätzlich mit „oder", neunzehn auf demselben Satzgerüst. Nach Halbierung der Fragen-Grundwerte und Mitlieferung der Frage-Art (beides 27.08.): weiterhin **2,2 Fragen je Turn, 100 % der Antworten enden mit einer Frage** — nur das Gerüst hat gewechselt (*„wie fühlt sich das für dich an?"* in 5 von 19 Turns). **Die Formvorgaben behandeln ein Symptom: Eine Frage ohne Ziel kann nur Floskel sein.**

**Niemand erhebt, was der Nutzer will.** Das Einzige, was existiert, ist das grobe `intent`-Label der Perzeption (`smalltalk`, `meta`, …). Der GV-Knoten rechnet Sprünge und Novas Absicht — die Frage *„worum geht es hier, was will er erreichen"* stellt kein Knoten.

**Der GV-Parse trägt seine eigenen Felder nicht.** Über 610 GV-Parses aus dem Serverlog: `Vehikel` leer in 75 %, `Absicht` leer in 66 %, `Strategie` leer in 66 %. Wer die Lage-Erhebung in diesen Parse legt, hängt sie an eine Kette, die meistens reißt.

**Die Landschaft entsteht aus Rückfallwerten.** Ein bloßer Zwei-Wort-Gruß nach 25 Stunden Pause landete in `kissenschlacht`: eine von sechs Achsen gemessen, drei auf Vorgabewerten, die sämtlich auf die warme Seite binarisieren. Die Raum-Neutralisierung (28.08.) mildert das; das Verstehen ersetzt sie nicht.

Dazu der Bestand laut Featureliste: *„Frames · Skills · Task-Orchestration · Cognitive Pipeline — ⚫ die Kernbezeichner fehlen sämtlich, kein Code."*

---

## 2. Was die Konzepte bereitstellen — die Kurzfassung

| Konzept | Was die Lage-Analyse daraus nimmt |
|---|---|
| **Frames** (`frames_k` §3–4) | Referenzobjekte *sind* Frames: Ein erwähnter Geburtstag trägt typische Eigenschaften (Wer, Wann, Feier, Geschenk), und die ungedeckten sind **mitaktivierte offene Fragen** (Fillmore). Die Slot-Schemata stehen im LLM-Wissen, nicht im Code. **Akutheit ist der Filter**: Was nicht akut ist, wird nicht beprobt — Schutz vor Übergriffigkeit (§4.3). |
| **Cognitive Pipeline** (`cognitive-pipeline_k` §1–4) | Die Diagnose („zwischen Router und Dispatch fehlt das Verstehen") und der Schritt **Akutheits-Klassifikation + Frame-Aktivierung** (§4.1–4.2). Die übrigen acht Schritte — Auflöser gegen den Bestand, Cross-Frame-Validierung, Plausibilität, Skills, Werkzeug-Orchestrierung — bleiben Konzept. |
| **Drive** (`drive_k` §3) | Drei Zielhorizonte. Langfristig und mittelfristig existieren (`ziele`-Tabelle, Gravitation, `[GEDANKEN]`-Block im GV). **Der kurzfristige Horizont ist als flüchtige GV-Hypothese definiert und hat keine persistente Form** — ein Sessionziel wie *„er baut ein Kräuterbeet auf"* kann heute nirgends stehen. |
| **Curiosity** (`curiosity_k`) | Die spätere Abnahmestelle: Ein wiederholt offener Slot ist eine Wissenslücke und damit Neugier-Trigger. In dieser Scheibe nur als Anschluss benannt. |

### 2a. Die wissenschaftliche Prüfung — 28.08.2026

**Die Annahmen dieses Dokuments sind im Projekt formuliert und danach gegen die Kognitionswissenschaft geprüft worden — die Schlüsse decken sich.** Alle vier Kernannahmen sind gedeckt; an zwei Stellen sagt die Forschung mehr, und beide sind in §3a eingearbeitet.

| Annahme | Deckung |
|---|---|
| Verstehen braucht ein Situationsmodell des Gesprächs | Lehrbuchstand seit van Dijk & Kintsch (1983). Das Event-Indexing-Modell (Zwaan, Langston & Graesser 1995) führt es auf **fünf Dimensionen**: Zeit, Raum, Akteur, Kausalität, **Intentionalität/Motivation** — nahezu die Felder des `lage`-Artefakts (§3). |
| Das Nutzerziel wird erschlossen; das Gesagte muss nicht der Grund sein | Sprechakttheorie und Grice; computational Allen & Perrault (1980): Verstehen **ist** Plan-Erkennung. Neurowissenschaftlich existiert dafür ein eigenes System — das Mentalizing-Netzwerk (medialer Präfrontalcortex, TPJ; Frith & Frith 2006), aktiv genau beim Deuten indirekter Äußerungen. |
| Referenzobjekte tragen typische Eigenschaften, die mitaktiviert werden | Über Fillmore/Minsky hinaus **gemessen**: Generalized Event Knowledge (Metusalem et al. 2012; McRae & Matsuki 2009) — Wörter aktivieren sofort Ereigniswissen samt Erwartungen an Beteiligte, nachweisbar im EEG (N400). |
| Antrieb ist im Gespräch verankert; die Frage dient dem Ziel | Klinger (Current Concerns): Ziel-Commitment sensibilisiert Wahrnehmung, Erinnern, Denken. Clark (1996): Gespräch ist Joint Action auf gemeinsame Ziele. Frageforschung (Rothe, Lake & Gureckis): Menschen fragen zielgerichtet; formalisierbar als **Expected Information Gain** — erwartete Unsicherheitsreduktion Richtung Ziel. Zugleich der Maßstab für Scheibe 3: Eine gute Rückfrage reduziert die Unsicherheit über eine offene Eigenschaft oder ein Ziel. |

**Die Einschränkung, die die Forschung mitgibt:** Absichtserkennung ist Inferenz, und selbst zielgerichtete Frager stellen selten die *optimale* Frage. Das Nutzerziel bleibt deshalb als **vermutet** gekennzeichnet — erschlossen aus Zeichen, Mustern und wahrgenommener Emotion, nie als Wissen behandelt.

---

**Eine Abweichung vom Pipeline-Konzept, und sie ist Absicht:** Das Konzept gattet den CognitiveGraph auf den **Management-Pfad** (Router: „Management oder Anliegen?"). Die Befunde aus §1 liegen aber im **Konversationspfad** — „ich habe eine neue Pflanze", „ein Geburtstag steht an" sind keine Agenten-Aufträge. Die erste Scheibe legt das Verstehen deshalb **vor den Gesprächsvektor**, wo es beiden Pfaden zur Verfügung steht. Der volle CognitiveGraph zwischen Router und Dispatch bleibt das Zielbild; diese Scheibe ist sein Eingangsschritt an anderer Stelle, nicht sein Ersatz.

---

## 3. Die Lage — das Artefakt

Je Turn ein strukturiertes Verständnis, **bevor** Gesprächsvektor und Verfasser arbeiten:

```
lage = {
  "gegenstand":     "worum es in diesem Turn geht, ein Satz",
  "nutzerziel":     "was der Nutzer damit erreichen will — das Gesagte
                     muss es nicht sein; gekennzeichnet als vermutet",
  "ausdrucksweise": "wie er es angeht (erzaehlend, prüfend, beilaeufig,
                     drängend, ...)",
  "objekte": [
    { "name":    "Geburtstag",
      "klasse":  "vorgang",          # Klassen aus frames_k §3.1
      "akut":    true,               # frames_k §4: latent | akut
      "gedeckt": {"anlass": "erwähnt im Turn"},
      "offen":   ["wer", "wann", "geschenk", "feier"] }
  ],
  "ziel_bezug":     "welches aktivierte Ziel (kurz-/mittel-/langfristig)
                     die Lage berührt, oder leer"
}
```

> **Nachtrag 13.09.2026 — der Wert in `gedeckt` ist die Angabe selbst.** Das Beispiel oben zeigt `{"anlass": "erwähnt im Turn"}` — eine Herkunft, keine Angabe. So hat es der Code nie gelesen: Der Sachlage-Prompt verlangt den Inhalt, der Auflöser schreibt ihn (Scheibe 6), Plausibilität und Verfasser-Block lesen ihn als Inhalt, und die Herkunft steht seit den Scheiben 6 und 9 in `quellen` und `sprecher`. **Entschieden vom Eigentümer am 13.09.2026:** Eine Eigenschaft ist *gedeckt*, wenn sie einen Wert hat — `gedeckt` ist eine Zuordnung Eigenschaft → Angabe (*»Rotationsperiode«: »33 Millisekunden«*). **Ohne Wert ist sie offen.** Einen Slot *»belegt, Inhalt unbekannt«* gibt es nicht. Das Beispiel bleibt als Erstfassung stehen; in heutiger Form hieße es etwa `{"anlass": "Geburtstag der Tochter"}`.
>
> **Das Artefakt ist seit den Scheiben 4–11 gewachsen**, ohne dass dieser Abschnitt nachgezogen wurde: `thema` (Pflichtfeld, Scheibe 4), `wiederaufnahme` (Scheibe 5), und je Objekt `quellen` (Scheibe 6), `plausibilitaet` (7), `traeger` und `recherche` (8), `sprecher` (9), `kritikalitaet` (10). `quellen`, `plausibilitaet` und `recherche` schreibt nur der Server — liefert das Modell sie, werden sie entfernt (Festlegung 1, Nachtrag). Scheibe 11 fügt dem Artefakt kein Feld hinzu: Sie legt `gedeckt` außerhalb der Blase ab.

**Vier Festlegungen, entschieden und begründet:**

1. **Eigener LLM-Call, nicht ein weiteres Feld im GV-Parse.** Der GV-Parse verliert heute zwei Drittel seiner eigenen Felder (§1). Ein eigener Call auf dem `analyse`-Backend hat einen eigenen Parser mit erzwungenem JSON (`expect_json`) und fällt laut aus statt still leer. Der Preis ist ein zusätzlicher Call je Turn; seine Dauer ist Teil der MESSUNG.

   *Die Nachträge zu Festlegung 1 — die Formprüfung (12. und 13.09.2026) — stehen in [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §3.*
2. **Die Akutheit entscheidet über die Tiefe, nicht über das Ob.** Gegenstand, Nutzerziel und Ausdrucksweise werden **immer** erhoben — auch Smalltalk hat eine Lage. Objekte werden nur bei Akutheit mit offenen Eigenschaften ausgewiesen (*„der Rasen wächst wie verrückt"* ist latent: Objekt erkannt, keine Slot-Fragen). Das ist die Smalltalk-Schranke aus `frames_k` §4.3 in der Konversationsfassung.
3. **Die Lage wird protokolliert wie die Haltung.** Eine `berechnung`-Zeile im `pipeline_log` je Turn, mit dem vollen Artefakt — sonst ist keine spätere Auswertung möglich, welche Nutzerziele das System vermutet hat und ob sie trafen.
4. **Kein Zugriff auf den Bestand in dieser Scheibe.** Der Frame-Auflöser (Slots aus Fakten, Timeline, Lager füllen) ist Schritt 4.3 des Pipeline-Konzepts ~~und braucht das Frame-Lager~~. Die Lage sagt nur, was der **Turn** deckt und was offen ist. Was das Gedächtnis davon deckt, ist die nächste Scheibe. → **Seit dem 28.08.2026, spät: Scheibe 6** — ohne Frame-Lager, gegen den Gedächtnis-Pool des Turns, in einem eigenen Call nach der Lage (§4).

---

## 3a. Der Kontext als Blase — das Zielbild hinter der Lage

**Der Kontext ist kein Turn-Artefakt, sondern ein lebendes Objekt über Turns.** Er entwickelt sich mit jedem Turn weiter und verschiebt sich fließend — ein Gespräch wandert von *Kino* zu *Film* zu *Schauspieler* zu *Mensch* zu *Beziehung* zu *sozialer Gesellschaft* zu *Instabilität* zu *Krieg*, ohne dass irgendwo ein harter Schnitt läge. Die Blase wabert: Ausrichtung, Gesprächsvektor und Ziele verschieben sich in ihr.

Das deckt sich mit der Event Segmentation Theory: Das Gehirn hält **ein** aktuelles Situationsmodell (Hippocampus, medialer PFC) und aktualisiert es fortlaufend; erst wo die Vorhersage bricht — Wechsel von Ort, Akteuren, **Zielen** — liegt eine Ereignisgrenze (Zacks; DuBrow & Davachi). Zwischen den Grenzen ist der Kontext Kontinuität, keine Folge unabhängiger Momentaufnahmen.

**Die Blase kann sich teilen.** Zwei Gesprächsstränge bestehen parallel, die Sprecher wechseln fliegend zwischen Thema 1 und 2; beide leben eine Weile, bis eine Blase schrumpft und eingeht und die andere sich weiterentwickelt. Auch das ist beschrieben: Grosz & Sidner (1986) führen den Diskurs als **Stapel von Segmenten**, jedes mit eigenem Zweck — Segmente werden unterbrochen, wiederaufgenommen oder aufgegeben.

**Was die Blase enthält:** den Text, die dahinterliegenden Informationen, die aktivierten Frames (§2), die Landschaft — und **Emotion**. Je nachdem, worüber gesprochen wird, zieht die Blase die aktuelle Emotion des Charakters (EI-Calc) in ihre Richtung: Wer abwechselnd über Lustiges und Bedrückendes spricht, dessen Emotion wird dorthin **gezogen, sie springt nicht** — eine Gravitation, dieselbe Bauart wie der bestehende Raumzug (`ei/raum.py`: *„Novas Raum springt nicht: Er wird gezogen"*). Die Trägheit der Emotion ist empirisch belegt (emotionale Inertie, Kuppens et al. 2010).

**Die Haltung reguliert die Füllung der Frames.** Ob offene Eigenschaften aktiv geklärt werden, entscheidet nicht die Lage — sie sagt nur, *was* offen ist. Wie aktiv die Lücken verfolgt werden, ist Sache der Haltung (`ei/haltung.py`: `fragen`, `naehe`, `draengen`):

- **Distanz und Desinteresse → passive Füllung.** Der Frame bleibt offen und füllt sich nur aus dem, was das Gegenüber von selbst sagt. Kein aktives Nachfragen; die Antworten der maximalen Distanz sind *„Aha!"*, *„Okay!"*, *„Ja und?"* — das Verstehen läuft weiter, die Klärung nicht.
- **Fachgespräch und Zuwendung → aktive Füllung.** Hier darf mehrfach nachgefragt werden, auch zur Rückversicherung des Verstandenen: *„Warte, Du meinst, dass das Gelb dem Ganzen erst die besondere Substanz gibt?"*

**Damit bekommt die Frage nach der Fragen-Menge ihren richtigen Ort.** Sie ist keine eigene Stellgröße, die man global halbiert oder verdoppelt — sie ist der sichtbare Ausdruck davon, wie aktiv die Haltung die offenen Eigenschaften der Blase verfolgt. Eine Vorgabe „eine Rückfrage" ohne Gegenstand erzeugt Floskeln (gemessen, §1); eine Haltung mit Gegenstand erzeugt die richtige Zahl von selbst: null bei Distanz, mehrere im Fachgespräch.

**Was daraus für die Scheiben folgt:**

- **Scheibe 1 schreibt die Lage fort, statt sie je Turn frisch zu erheben.** Der Lage-Call bekommt die vorige Lage als Eingang; der neue Turn aktualisiert sie — Drift statt Neuaufbau. *Ausdrücklich anders als beim Kern-Hash entschieden* (dort ist Fortschreibung abgelehnt, `novaberg-pixie-character-hash.md` §3.1a): Der Kern soll dauerhaft sein und aus rückverfolgbarem Material entstehen; die Lage soll genau den **Zustand zwischen den Turns** tragen — Kontinuität ist hier der Zweck, nicht der Fehler. Ihre Quelle bleibt klein und präsent (die Turns der Session), der Drift bleibt dadurch nachvollziehbar.
- **Teilung und Parallel-Stränge sind Zielbild, nicht Scheibe 1.** Die erste Scheibe führt **eine** Blase. Erkennt die Analyse zwei unvereinbare Gegenstände, notiert sie das im Artefakt, mehr nicht — **gemessen am 28.08.2026: die Notiz ist das zweite Objekt** (§4, Scheibe 5) — die Stapel-Mechanik ist eine eigene, spätere Scheibe; ihr erster Schritt, die Wiederaufnahme einer früheren Blase aus `sachlage_verlauf`, ist Scheibe 5.
- **Der emotionale Zug der Blase auf EI-Calc ist eine eigene, spätere Scheibe.** Er braucht die fortgeschriebene Lage als Quelle und gehört deshalb hinter Scheibe 1; die Bauart (Zug statt Sprung) steht mit dem Raumzug bereits im Haus.

---

## Aus §4 — was die Scheiben als Absicht festlegen

*Die Scheiben selbst — Anlass, Bauweise, `ZIEL` / `TEST` / `MESSUNG`, Reihenfolge und Bauberichte — stehen in [`novaberg-thinking-lage_b.md`](novaberg-thinking-lage_b.md) §4, ihre Messungen in [`novaberg-thinking-lage_m.md`](novaberg-thinking-lage_m.md) §4. Hier stehen die zwei Stellen aus §4, die eine Absicht des Eigentümers tragen; die Überschriften sind die der Scheiben.*

### Scheibe 11 — das Eigenschaftsgedächtnis (entworfen, gebaut und gemessen am 13.09.2026)

**Die Absicht des Eigentümers (13.09.2026), in drei Sätzen:** Je gerechnetem Turn werden die betroffenen Objekte des Gesprächskontexts **abgelegt** — so, wie Entitäten und Fakten persistiert werden. **Die Entität wird später gebunden:** erst festhalten, dann verbinden, sobald es eine Referenz gibt; die Zuordnung darf nach dem Dispatcher oder in einem späteren Turn entstehen. **Ein neuer Wert löst ab, statt zu überschreiben:** Der alte wird inaktiv, der neue steht daneben — wer erst den 1.7. und dann den 1.8. nennt, bleibt belegbar. Das ist die Bauart von `fakten` (`invalidate` setzt `aktiv = FALSE` und `t_invalid`; die Historie liefert aktive und inaktive Zeilen — vor dem Bau am Repository geprüft).

### Scheibe 12 — der Empfang liest die Lage (Entwurf, 14.09.2026)

#### Das Kriterium der Zuordnung — entschieden am 16.09.2026

**Teil C braucht eine Trennlinie zwischen den beiden Diensten, die heute beide „merk dir" annehmen.** Sie ist entschieden, im Wortlaut des Eigentümers:

> **„Aber etwas zu erledigendes wie ‚Morgen muss ich das Buch abgeben' passt eher in die Timeline. […] ‚Merke Dir, dass ich morgen Mehl brauche' ist nicht direkt etwas zu erledigendes. Es impliziert vielleicht, dass es etwas zu erledigendes geben könnte, nämlich das Einkaufen, aber der Gegenstand ist Mehl und brauchen. Das ist kein Termin, das ist eine Notiz mit Zeitbezug. Ein Buch abgeben ist eine Erledigung."**

| Der Gegenstand ist … | Dienst | Träger der Zeit |
|---|---|---|
| eine **Handlung oder ein Ereignis, das zu einer Zeit stattfindet** — Buch abgeben, Zahnarzt, Geburtstag, Feiertag, Frist | Timeline | `event_time`, bei Zeiträumen `event_ende` |
| eine **Sache oder ein Zustand mit Zeitbezug** — *morgen Mehl brauchen* | Notizen | `faellig_am`; soll erinnert werden, hängt die Notiz über `timeline_id` an einem Anker |

**Damit entscheidet das Verb, nicht das Zeitwort.** *„Morgen Mehl brauchen"* ist eine Notiz, *„morgen Mehl kaufen"* eine Erledigung und damit Timeline — dieselbe Sache, je nach dem, was der Mensch gesagt hat. Das ist beabsichtigt: Der Empfang deutet die Äußerung nicht um.

> **Ein Zeitwort-Flag kann diese Grenze nicht ziehen, und deshalb gehört sie zu Teil C.** Sie fragt nach der **Klasse des Objekts**, nicht nach dem Vorkommen einer Zeitangabe — genau die Frage, die das Objekt-Merkmal des Dienstes und die gerechnete Nähe beantworten sollen. Der heutige Weg über `needs_timeline` ist das Gegenteil davon und als Defekt erfasst (`PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL`).

---

## 5. Was ausdrücklich nicht gebaut wird

Aus `cognitive-pipeline_k` bleiben Konzept: ~~der Frame-**Auflöser** gegen den Bestand~~ (**seit dem 28.08.2026, spät, in der Konversationsfassung gebaut — Scheibe 6**; die gezielte Suche je offener Eigenschaft, Fakten und Notizen als Quellen ~~und die Kritikalität einer Lücke~~ bleiben Konzept; **die Kritikalität einer Lücke ist seit dem 30.08.2026 gebaut — Scheibe 10**), ~~das Frame-**Lager** samt Lernmechanik~~ → **seit dem 13.09.2026 steht ein Teil des Frame-Lagers in Konversationsfassung — Scheibe 11:** Objekte mit ihren Eigenschaftswerten und deren Historie je Paar, verankert an `entitaeten` statt an Klassennamen; **die Lernmechanik des Lagers (`frames_k` §7.3: Häufigkeit, Wert-Cluster, Recency- und Korrektur-Gewichtung, Schema-Aggregat je Klasse, Decay) bleibt Konzept**, **Cross-Frame-Validierung** (braucht Slots aus Fakten oder Lager), ~~**Plausibilitätsprüfung**~~ (**seit dem 29.08.2026 gebaut — Scheibe 7**; die Stufeneichung und die Konflikt-Schwellwerte bleiben offen), **Skills**, die Ablösung des Planners und die Werkzeug-Orchestrierung. ~~Ebenso bleibt liegen: die Formfrage der Rückfragen (2,2 je Turn) — sie wird nach Scheibe 3 neu gemessen und erst dann behandelt, falls sie dann noch besteht.~~ → **Gemessen am 29.08.2026 über 20 Turns** (§4, Betriebsmessung der Kette): **1,21 Fragezeichen je Antwort, 12 von 19 Antworten enden fragend** — gegen den Ausgangswert **2,2 Fragen je Turn bei 100 % fragenden Schlüssen**. Die Formfrage besteht in ihrer alten Schärfe **nicht mehr**; ob zwei Drittel fragende Schlüsse zu viel sind, ist eine Haltungsfrage und kein Befund. **Die Bedingung stand bis zum 30.08.2026 unverändert hier, während vier Absätze weiter oben ihre Messung stand** — im Labor blieb die Menge bei fragender Haltung 10/10, nur der Gegenstand änderte sich (§4). ~~Scheibe 4 bleibt Entwurf, bis die DDL angekündigt und freigegeben ist.~~ → **Nachtrag 13.09.2026:** Scheibe 4 ist seit dem 28.08.2026 gebaut (§4, DDL angekündigt, freigegeben, angelegt); der Satz stand seither unverändert hier. Cross-Frame-Validierung braucht Slots über mehrere Frames — mit Scheibe 11 gibt es gespeicherte Werte je Objekt, aber keinen Vergleich über Objekte hinweg; sie bleibt Konzept.

---

## 6. Verweise

- `novaberg-thinking-frames_k.md` — Substrat: Frame-Klassen, Akutheit, Slots
- `novaberg-thinking-cognitive-pipeline_k.md` — Zielbild der vollen Verstehens-Schicht
- `novaberg-thinking-drive_k.md` — Zielhorizonte, Gravitation
- `novaberg-thinking-curiosity_k.md` — Wissenslücken als spätere Abnahmestelle offener Slots
- `novaberg-haltungsraum_k.md` — Haltungsgrößen; die Rückfrage-Zeile, die Scheibe 3 erweitert

### Quellen der Prüfung (28.08.2026)

- van Dijk, T. A., & Kintsch, W. (1983). *Strategies of Discourse Comprehension.* Academic Press. Dazu van Dijk (1999): [Context Models in Discourse Processing](https://discourses.org/wp-content/uploads/2022/07/Teun-A.-van-Dijk-1999-Context-models-in-discourse-processing-in-Oostendorp-Goldman.pdf) — die Trennung Situationsmodell/Kontextmodell entspricht der Trennung Lage/Haltung.
- Zwaan, R. A., Langston, M. C., & Graesser, A. C. (1995). [The Construction of Situation Models in Narrative Comprehension: An Event-Indexing Model.](https://journals.sagepub.com/doi/10.1111/j.1467-9280.1995.tb00513.x) *Psychological Science*, 6(5). Dazu [Zwaan & Radvansky (1998)](https://sites.ualberta.ca/~dmiall/Cognitive/Readings/Zwaan_Radvansky_1998.pdf) und der Überblick [Zwaan (2025)](https://doi.org/10.1177/09637214251326812).
- Allen, J. F., & Perrault, C. R. (1980). [Analyzing Intention in Utterances.](https://nlp.stanford.edu/acvogel/allenperrault.pdf) *Artificial Intelligence*, 15(3), 143–178.
- Frith, C. D., & Frith, U. (2006). [The Neural Basis of Mentalizing.](https://www.cell.com/fulltext/S0896-6273%2806%2900344-8) *Neuron*, 50(4). Dazu [ToM und indirekte Kommunikation, Phil. Trans. R. Soc. B (2025)](https://royalsocietypublishing.org/rstb/article/380/1932/20230497/235137/Theory-of-Mind-and-the-brain-substrates-of-direct).
- Metusalem, R., Kutas, M., Urbach, T. P., Hare, M., McRae, K., & Elman, J. L. (2012). [Generalized event knowledge activation during online sentence comprehension.](https://pubmed.ncbi.nlm.nih.gov/22711976/) *Journal of Memory and Language*, 66. Dazu [McRae & Matsuki (2009)](https://compass.onlinelibrary.wiley.com/doi/10.1111/j.1749-818X.2009.00174.x).
- Klinger, E., & Cox, W. M. (2011). [Motivation and the Goal Theory of Current Concerns.](https://onlinelibrary.wiley.com/doi/10.1002/9780470979952.ch1) Dazu [Klinger (2013): Goal Commitments and the Content of Thoughts and Dreams.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3708449/)
- Clark, H. H. (1996). *Using Language.* Cambridge University Press — [Kap. 4: Common Ground](https://www.cambridge.org/core/books/abs/using-language/common-ground/7F9689E12F87250DCA81540FCBDE3720).
- Rothe, A., Lake, B. M., & Gureckis, T. M. (2018). [Asking goal-oriented questions and learning from answers.](https://nyuscholars.nyu.edu/en/publications/asking-goal-oriented-questions-and-learning-from-answers) Dazu [Coenen, Nelson & Gureckis (2019): Nine Open Challenges.](https://link.springer.com/article/10.3758/s13423-018-1470-5)
- DuBrow, S., & Davachi, L. [Events and Boundaries.](https://memory.psych.upenn.edu/mediawiki/images/e/e1/DuBrow_Final.pdf) Dazu [Hippocampal–mPFC Event Segmentation (2020/2022)](https://www.biorxiv.org/content/10.1101/2020.03.14.990002v4.full).
- Grosz, B. J., & Sidner, C. L. (1986). [Attention, Intentions, and the Structure of Discourse.](https://aclanthology.org/J86-3001/) *Computational Linguistics*, 12(3), 175–204 — die Stapel-Mechanik der geteilten Blase (§3a).
- Kuppens, P., Allen, N. B., & Sheeber, L. B. (2010). [Emotional Inertia and Psychological Maladjustment.](https://journals.sagepub.com/doi/10.1177/0956797610372634) *Psychological Science*, 21(7) — die Emotion springt nicht (§3a).

---
