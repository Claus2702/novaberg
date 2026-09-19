# Novaberg — Die Lage-Analyse (Konzept)

**Absicht:** Vor jeder Antwort erfasst das System je Turn, worum es geht, was der Nutzer vermutlich will und welche Objekte mit welchen gedeckten und offenen Eigenschaften im Spiel sind — fortgeschrieben über die Turns.
**Stand:** 19.09.2026
**Umsetzung:** `novaberg-featureliste.md` §6 — ⏫ *Frames · Skills · Task-Orchestration · Cognitive Pipeline — im Bau als Lage-Konzept* 🟠, dazu ↳ *Scheibe 12 A* bis *F* je 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) · [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md)
**Entschieden:** 21 · **Offen beim Meister:** 2 (Liste in [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md))

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

Seit dem 19.09.2026 ist das Konzept in drei Teilen: dieses Dokument (Absicht und Planung), [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) (Umsetzung und Ausarbeitung) und [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md) (Entscheidungen, offene Fragen, Befunde). Die Abschnittsnummern sind geblieben; ein Verweis der Form `novaberg-thinking-lage_k.md §4` löst sich über diese Tabelle auf.

| § | Abschnitt | Datei |
|---|---|---|
| Kopf | der bisherige Stands-Kopf (`**Stand:**`) | `_t`, *Bisheriger Kopf* |
| §1 | Anlass — die Messungen, die den Schnitt begründen | `_k` |
| §2 | Was die Konzepte bereitstellen | `_k` |
| §2a | Die wissenschaftliche Prüfung, dazu der Absatz *Eine Abweichung vom Pipeline-Konzept* | `_k` |
| §3 | Die Lage — das Artefakt, die vier Festlegungen | `_k`; die Nachträge zu Festlegung 1 (Formprüfung, 12./13.09.2026) in `_t` §3 |
| §3a | Der Kontext als Blase — das Zielbild | `_k` |
| §4 | Die Scheiben des Umbaus — Überschrift und Nachtrag | `_k` |
| §4 Scheibe 1–11 | je Scheibe Anlass, Bauweise, *was die Scheibe nicht tut*, `ZIEL` / `TEST` / `MESSUNG`, Reihenfolge | `_k`; *Gebaut*, Messung, Betrieb, zweite Kontrolle und Preis je Scheibe unter derselben Überschrift in `_t` §4 |
| §4 Scheibe 3, Nachträge | *der eigene Zug* (29.08.), *die Namen des Lesers* (29.08.) | `_t` §4 |
| §4 Scheibe 11 | Anlass, Absicht des Eigentümers, `ZIEL` / `TEST` / `MESSUNG` | `_k`; die drei Tabellen, Schreibweg, Bindung, Rückweg, Prompt-Regeln, Messungen in `_t` §4 |
| §4, zwischen Scheibe 5 und 6 | Der Gesprächskontext im Client | `_t` §4 |
| §4, zwischen Scheibe 9 und 10 | Die Betriebsmessung der Kette | `_t` §4 |
| §4 Scheibe 12 | Anlass, Entwurf (Teile A–F), Reihenfolge, *Das Kriterium der Zuordnung*, Vorbedingung | `_k` |
| §4 Scheibe 12 | Status-Zeile | `_t` §4 |
| §4 Scheibe 12 | Die Entscheidungen des Eigentümers (13. und 14.09.2026), im Wortlaut | `_e` |
| §4 Scheibe 12 | *Offen für den Bau* | `_e`; der erste Punkt (*Die Nähe*, samt *Zwei Schwellen und der geeichte Wortlaut*) in `_t` §4 |
| §4 Scheibe 12 | Teil C2, D2, *Die Zustimmung kommt an*, F und A Punkt 1, E2, E3, E1, D1, *Die Objektwahl der Lage*, C1, B, A — in der Reihenfolge des Originals | `_t` §4 |
| §4 Scheibe 12, Teil C2 | die Entscheidung über den Abstand (16.09.2026, 20:55 UTC) samt Rechnung | `_e` |
| §4 Scheibe 12, Teil E2 | die Entscheidung über die Wahrscheinlichkeit (18.09.2026) | `_e` |
| §5 | Was ausdrücklich nicht gebaut wird | `_k` |
| §6 | Verweise, Quellen der Prüfung | `_k` |
| Schlusszeile | *Stand 28.08.2026. Erstfassung …* | `_t`, *Bisheriger Kopf* |


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

## 4. Die drei Scheiben des Umbaus

> **Nachtrag 13.09.2026:** Die Überschrift stammt aus der Erstfassung vom 28.08.2026. Heute sind es **elf** Scheiben; Scheibe 11 steht am Ende dieses Abschnitts.

### Scheibe 1 — die Lage-Analyse

Der Knoten (Arbeitsname `lage`) läuft im CharacterGraph vor dem Gesprächsvektor, schreibt `state["lage"]` und die Protokollzeile. Verfasser und GV bekommen einen `[LAGE]`-Block.

| | |
|---|---|
| **ZIEL** | Jeder Turn trägt ein strukturiertes, **fortgeschriebenes** Verständnis (§3a): Bei *„bei uns steht ein Geburtstag an"* nennt die Lage das akute Objekt `geburtstag` mit gedecktem Anlass und den offenen Eigenschaften Wer/Wann/Geschenk — bei *„der Rasen wächst wie verrückt"* das latente Objekt ohne offene Eigenschaften. Nennt der Folgeturn das Wer, wandert die Eigenschaft von offen nach gedeckt, statt dass eine neue Lage entsteht. |
| **TEST** | Zeugen auf das Artefakt: Pflichtfelder immer belegt; akutes Objekt trägt offene Eigenschaften, latentes keine; die Fortschreibung deckt Eigenschaften aus Folgeturns; Parser-Ausfall ist laut (kein leeres `lage` ohne Log-Zeile). |
| **MESSUNG** | Laborlauf gegen den Knoten direkt (nicht über den vollen Pfad — Alltagssätze lösen im Produktivpfad echte Schreibungen aus): 10 feste Äußerungen, je erwartete Akutheit und Objektklasse, dazu die Dauer des Calls. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 1.*

### Scheibe 2 — das kurzfristige Ziel (gebaut am 28.08.2026)

`ziel_typ='kurzfristig'` in der bestehenden `ziele`-Tabelle. Entsteht, wenn Lagen derselben Session wiederholt auf ~~dasselbe Nutzerziel~~ **dasselbe akute Objekt** zeigen (*Kräuterbeet*); verfällt in Stunden statt Tagen. Läuft durch die bestehende Gravitation und erscheint damit ~~ohne weiteren Bau~~ im `[GEDANKEN]`-Block — **gemessen am 28.08.2026: nicht ohne Bau.** Der Zielsatz liegt zur Nutzeräußerung bei Kosinus 0,13–0,41 (Stärke 0,09–0,29 unter der Schwelle 0,40); die Gravitation hätte ihn nie aktiviert. Seither ist ein kurzfristiges Ziel per Bauart aktiviert, solange es lebt — sein Tor ist der Verfall, und es steht im `[GEDANKEN]`-Block vorn (`ei/gravitation.py`, `novaberg-thinking-drive_k.md` §5).


| | |
|---|---|
| **ZIEL** | Aus zwei Lagen mit demselben Nutzerziel innerhalb einer Session entsteht ein kurzfristiges Ziel; nach Ablauf seiner Frist ist es inaktiv. |
| **TEST** | Zeugen auf Entstehung (zweimal dasselbe Ziel → Eintrag), Nicht-Entstehung (einmal → kein Eintrag) und Verfall. |
| **MESSUNG** | Ein gestellter Sessionverlauf im Labor; danach `ziele`-Tabelle und Gravitations-Log. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 2 — samt der Messung *Warum das Objekt und nicht das Nutzerziel*.*

### Scheibe 3 — die Gesprächsführung aus der Lage

Die Rückfrage-Zeile des Verfassers (`ei/haltungssprache.py::_rueckfragenzeile`, seit 27.08. mit Menge und Art) bekommt ihren **Gegenstand**: die wichtigste offene Eigenschaft eines akuten Objekts, oder der nächste Schritt zum berührten Ziel. Fehlt beides, bleibt die heutige Art-Vorgabe der Rückfall. Ob Frage oder Aussage, bleibt Sache von GV-Vehikel und Haltung — die Lage liefert das Wohin, nicht das Wie.

| | |
|---|---|
| **ZIEL** | Die Rückfrage ist das Produkt aus Lage und Haltung: Auf *„bei uns steht ein Geburtstag an"* fragt Nova im zugewandten Gespräch nach Wer/Wann/Geschenk — nicht *„sollen wir tiefer eintauchen?"*. Bei distanzierter Haltung fragt sie **nicht**: Die Eigenschaften bleiben offen und füllen sich nur passiv. |
| **TEST** | Zeugen auf die Zeile: Bei akutem Objekt und fragender Haltung nennt sie dessen offene Eigenschaft; bei niedriger `fragen`-Haltung nennt sie trotz offener Eigenschaften keine — die Lage erzeugt keine Frage an der Haltung vorbei; ohne akutes Objekt steht die Art-Vorgabe wie heute. |
| **MESSUNG** | Die Schauspielerprobe-Anordnung vom 27.08.2026 (fester Prompt-Aufbau, T=0,0, Vergleichsarme mit/ohne Lage) über die 10 Äußerungen der Scheibe-1-Messung: Anteil der Schlussfragen, die eine offene Eigenschaft oder ein Ziel adressieren, vorher gegen nachher. |


**Reihenfolge ist Abhängigkeit:** 2 und 3 lesen nur, was 1 erzeugt. Nach Scheibe 1 wird gemessen, bevor 2 begonnen wird — trägt die Lage nicht, sind 2 und 3 gegenstandslos. **Gemessen am 28.08.2026 im Betrieb: sie trägt** (Betriebsmessung unter Scheibe 1).

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 3 — samt den Nachträgen *der eigene Zug* und *die Namen des Lesers* (29.08.2026).*

---

### Scheibe 4 — das Sachlage-Gedächtnis (entworfen und gebaut am 28.08.2026)

**Der Anlass sind Pixies Zustellungen.** Ein Impuls beruht auf einem Turn; wenn die Aussage im Chat landet, ist die Assoziation zum Auslöser oft schwer nachvollziehbar. Empathisch wäre ein **Übergang vom Kontext des aktuellen Turns zum Kontext des Auslösers** — dafür braucht es beide Enden, und das zweite existiert nicht: Die Sachlage wird heute je Paar **überschrieben** (Redis, Verfall 4 h); die `pipeline_log`-Zeile je Turn ist Forensik mit Vorhaltefrist, ohne Thema, ohne Embedding, nicht abfragbar. Geprüft am 28.08.2026: Der Impuls-Stack-Eintrag trägt Thema und Embedding, aber **keine `turn_id` seines Auslösers** — die Zuordnung ist nur implizit über Ähnlichkeit.

**Was schon trägt:** `turn_id` ist das Rückgrat, an dem alles Turnbasierte hängt — `turn_roh` (Wortlaut), `verbindung → lzg_knoten`, die Achsen-Protokolle, die Charakter-Destillation. Die Turns tragen das Emotionale, das *Wie*; die Sachlage trägt die Fakten. Eine je Turn persistierte Sachlage reiht sich mit einer Spalte ein.

**Der Bau, drei Teile:**

1. **Tabelle `sachlage_verlauf`** — je gerechnetem Turn eine Zeile: `turn_id`, Paar (`user_id`, `character_id`), **`thema`**, `gegenstand`, `nutzerziel`, `ausdrucksweise`, `objekte` (jsonb), **`embedding vector(768)`**, `erstellt_am`. Drei Festlegungen formen sie: Der Embedding-Text ist der `gegenstand`-Satz und aus der Zeile rekonstruierbar (`F-EMBED-1`); ein Vektor repräsentiert genau diesen einen Gegenstand (`F-EMBED-2`); und die Tabelle **verfällt nicht** — sie protokolliert ein Faktum, *die Sachlage dieses Turns war X* (`F-VERFALL-1`: was als Faktum protokolliert, bleibt). Geschrieben wird nur auf den drei rechnenden Wegen (frisch, fortgeschrieben, verfallen_neu) — übernommene Artefakte erzeugen keine Doppelzeile.
2. **`thema`** wird ein Pflichtfeld des Artefakts — derselbe LLM-Call liefert es mit, ein bis drei Worte. Es ist der Anzeigename der Blase (auch für den Kontext-Tab — seit dem 28.08.2026 abends gebaut: `client/ui/panels/sachlage_panel.py` »🫧 Gesprächskontext«, gespeist aus `GET /drive/kontext`) und das Findewort neben dem Vektor. **Und es benennt die Sache, nie den Wechsel** — seit dem Abend des 28.08.2026 als Prompt-Regel, weil der erste Betriebsturn nach dem Bau (Rettich → Neutronensterne) `thema='Themenwechsel'` und einen `gegenstand` über den Nutzer schrieb; aus den echten Turns nachgestellt **5/5** so, mit der Regel **5/5** »Neutronensterne« und ein Gegenstand, der die Sache nennt (`labor/2026-08-28_sachlage_thema_wechsel.py`). Der Vektor der Wechselzeile zeigte vorher halb auf das alte Thema — genau an der ersten Zeile jeder neuen Blase.
3. **Die Brücke:** Der Impuls-Eintrag bekommt bei seiner Entstehung die **`turn_id` seines Auslöser-Turns**. Bei der Zustellung lädt der Graph die Auslöser-Zeile aus `sachlage_verlauf`, und der Verfasser bekommt beide Blasen als `[SACHLAGE-BRÜCKE]` — *aktuell* und *damals* — mit dem Auftrag, den Übergang zu bauen statt unvermittelt einzuwerfen. Rückfall ohne harte `turn_id`: die ähnlichste Verlaufszeile per Embedding gegen das Impuls-Embedding, als Rückfall gekennzeichnet.

| | |
|---|---|
| **ZIEL** | Eine Zustellung nennt hörbar, woran sie anknüpft: Der Verfasser sieht die Auslöser-Sachlage neben der aktuellen und baut den Übergang. Nebenziel: `SELECT … FROM sachlage_verlauf ORDER BY embedding <=> $1` findet zu einem Thema die Turns, in denen es Gegenstand war. |
| **TEST** | Zeugen auf: Schreibweg nur bei gerechneten Artefakten · Embedding-Text = `gegenstand` (rekonstruierbar) · Brücke nur mit beiden Enden, Rückfall gekennzeichnet · Impuls-Eintrag trägt die Auslöser-`turn_id`. |
| **MESSUNG** | Ein gestellter Verlauf im Labor: Impuls aus Turn A, Zustellung in Lage B — der Verfasser-Prompt trägt beide Blasen; dazu die Trefferprobe der Embedding-Suche über zehn persistierte Lagen. |

> **DDL:** `sachlage_verlauf` ist eine neue Tabelle (additiv) und wird nach `F-DDL-1` **vor dem Bau angekündigt**; sie wirkt erst nach Neustart des Dienstes. Ablageort nach `F-SCHEMA-1` in der zuständigen `init.sql`. **Angekündigt, freigegeben und angelegt am 28.08.2026** — dazu eine zweite, im Entwurf nicht genannte Spalte: `shadow_auftrag.ausloeser_turn_id`. Ohne sie hätte der Stapel-Eintrag die `turn_id` seines Auslösers nie bekommen können, denn der Auftrag ist das erste Glied der Kette (Auftrag → Stapel → Ereignis → Brücke), und er hatte keine Spalte dafür. **Kein Verfall, weil Turns auch keinen haben** — so entschieden bei der Freigabe.

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 4.*

---


### Scheibe 5 — die Wiederaufnahme (entworfen am 28.08.2026, abends)

**Der Anlass ist ein Satz mit zwei Sachen:** *„Nochmal zurück zur Gravitationslinse bei Schwarzen Löchern: kann man die Brechung des Lichts als Grundlage für die Bestimmung der Masse hernehmen? Ach, und nimm die Zitrone auf die Einkaufsliste, die sind alle."* Gemessen gegen den Knoten (drei Läufe, `labor/2026-08-28_sachlage_zwei_themen.py`): Die zwei Sachen liegen heute schon als **zwei Objekte in einer Blase** — `thema`/`gegenstand` tragen die Hauptsache, die Einkaufsliste steht als Objekt der Klasse *anliegen* daneben (akut 1/3, latent 2/3). Die „Notiz im Artefakt", die §3a für zwei unvereinbare Gegenstände verspricht, **ist damit das zweite Objekt** — kein eigenes Feld. Was fehlt, ist das *„nochmal zurück"*: Die Fortschreibung liest nur die aktuelle Redis-Blase (Pulsare); dass die Gravitationslinse vor zwei Blasen schon Gegenstand war, sieht sie nicht — gedeckt/offen jener Blase sind weg, obwohl `sachlage_verlauf` sie seit Scheibe 4 trägt, und der Objektname fiel dreimal anders aus, weil kein Vorgänger da ist, an dem die Wörtlich-Regel greift.

**Der Bau, schmal:** Vor dem Sachlage-Call sucht der Knoten auf dem rechnenden Weg in `sachlage_verlauf` die ähnlichste Zeile des Paares zum Reiz — mit dem Prompt-Embedding, das der Enricher ohnehin gerechnet hat — **unter Ausschluss des aktuellen Themas** (sonst fände er die eigene Blase). Liegt sie über `SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS`, bekommt der Prompt sie als *frühere Sachlage zu einer ähnlichen Sache* mit der Anweisung: Kehrt der Turn zu ihr zurück, führe **sie** fort — Objektname wörtlich, gedeckte Eigenschaften bleiben gedeckt; sonst ignoriere sie. Das Artefakt trägt `wiederaufnahme` (turn_id, thema, kosinus) oder `null`; der `[SACHLAGE]`-Block bekommt eine Zeile *„Der Nutzer kommt auf … zurück (zuletzt vor …)"*, damit der Verfasser den Anschluss hörbar machen kann. **Kein Stapel im Sinne von Grosz & Sidner** — keine zwei lebenden Blasen, kein Push/Pop. Die Wiederaufnahme holt eine Blase aus dem Faktum zurück; ob daraus ein Stapel wird, entscheidet der Betrieb.

| | |
|---|---|
| **ZIEL** | Kehrt ein Turn zu einer Sache zurück, die eine frühere Blase dieses Paares war, führt die Sachlage jene Blase fort — Objektname wörtlich, gedeckte Eigenschaften bleiben gedeckt — statt bei null zu beginnen; ein Turn ohne solche Blase bekommt keine. |
| **TEST** | Zeugen: die Suche läuft nur auf dem rechnenden Weg, mit dem Prompt-Embedding, unter Ausschluss des aktuellen Themas; ohne Treffer keine Sektion und `wiederaufnahme: null`; mit Treffer trägt der gerenderte Prompt die frühere Blase und die Regel, das Artefakt die Kennung; fällt der Vektor aus, läuft der Turn ohne Suche und sagt es; das Repository überspringt Zeilen des ausgeschlossenen Themas (live). |
| **MESSUNG** | Labor gegen Knoten und Repository mit einem Laborpaar: drei persistierte Blasen (Gravitationslinse, Pulsare, Rettich), vorige Blase Pulsare, dann der Zwei-Sachen-Satz — Treffer auf die Gravitationslinsen-Zeile mit Kosinus, und der Objektname des Artefakts ist der der alten Blase, ihre gedeckten Eigenschaften stehen wieder; dazu ein fremder Satz ohne Treffer. Die Schwelle wird an den Kosinuswerten dieser Reihe gesetzt, nicht geraten. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 5 — und der Abschnitt *Der Gesprächskontext im Client*.*

### Scheibe 6 — der Frame-Auflöser, Konversationsfassung (entworfen am 28.08.2026, spät)

**Der Anlass:** Scheibe 3 fragt nach der wichtigsten offenen Eigenschaft eines akuten Objekts — auch dann, wenn Nova die Antwort längst hat. Die Sachlage weiß nur, was der **Turn** deckt (§3, Festlegung 4); was das Gedächtnis deckt, sieht sie nicht. Das ist Schritt 4.3 des Pipeline-Konzepts: Lücken gegen Wissensquellen halten, je aufgelöstem Slot die Quelle vermerken.

**Der Bestand, gemessen am 28.08.2026, 22:32 UTC, für das Paar:** Der Fakten-Graph des Konzepts (Quelle 1) trägt **0 Zeilen** und `find_similar` hat keinen Aufrufer; `notizen` 1 Zeile, `timeline` 40 (39 Erinnerungs-Anker, ein Termin); ein Frame-Lager gibt es nicht. **Novas Wissen liegt woanders:** `autonomous_wissen` **1012** Zeilen (475 `echte_tiefe`, alle mit Vektor), `lzg_knoten` 2910 — und beides fließt **schon je Turn** in den State: Der Enricher sucht KZG, LZG, Bibliothek und Aufzeichnungen mit dem Suchvektor des Turns und legt sie als `memory_entries` (19 im letzten Betriebsturn) und `aufzeichnungen` (3) ab, bevor die Sachlage rechnet. Der Auflöser braucht keine zweite Suche und keinen zweiten Call — er braucht den Pool im Prompt und ein Urteil.

**Der Bau, schmal:** Auf dem rechnenden Weg baut `graph/nodes/sachlage_resolver.py::memory_offer` aus dem Pool des Turns ein **nummeriertes Angebot** (G1 … Gn): `memory_entries` der Quellen `kzg`, `lzg`, `plugin_wissen` nach Gewicht, die `aufzeichnungen`, dazu Kalendereinträge zu den akuten Objektnamen der **vorigen** Blase (`TimelineRepository.find_by_keyword`, beide Richtungen) — gekappt auf `SACHLAGE_BESTAND_MAX_EINTRAEGE`, je Eintrag gekürzt. Der Sachlage-Prompt bekommt das Angebot als Sektion *„Was Novas Gedächtnis dazu hält"* und je Objekt ein Feld `aus_gedaechtnis`: *Eigenschaft → {Eintrag, was er dazu sagt}*. `apply_memory_coverage` hält die Antwort gegen das Angebot: Eine Referenz, die nicht angeboten war, wird verworfen und geloggt; eine gültige wandert von `offen` nach `gedeckt`, und das Objekt trägt sie in `quellen` (Quelle, Herkunft, Eintrag). Ohne Angebot ist der Prompt **zeichengleich** mit dem heutigen. Der `[SACHLAGE]`-Block nennt dem Verfasser, was Nova dazu schon weiß und woher; `question_target` überspringt es von selbst, weil es nicht mehr offen ist.

**Was der Auflöser nicht tut:** keine Suche je offener Eigenschaft (der Pool ist mit dem Reiz des Turns gesucht, nicht mit der Lücke — die gezielte Suche ist die Vollfassung und ein Preis dieser Scheibe), keine Notizen (der einzige Leser mit Treffersemantik schreibt `last_touched`, und der Bestand ist eine Zeile), keine Fakten (leer, kein Aufrufer), kein Frame-Lager, keine Kritikalität der Lücken, keine Plausibilität. Der Impuls-Weg bietet nichts an.

| | |
|---|---|
| **ZIEL** | Eine offene Eigenschaft eines akuten Objekts, die Novas Gedächtnis dieses Turns schon beantwortet, steht im Artefakt als gedeckt **mit ihrer Quelle** — und ist damit kein Rückfrage-Gegenstand mehr, sondern Wissen für den Verfasser. Eine Eigenschaft, die der Bestand nicht beantwortet, bleibt offen: Ein thematisch naher Eintrag, der die Frage nicht beantwortet, deckt nichts. |
| **TEST** | Zeugen: das Angebot nimmt KZG, LZG, Bibliothek und Aufzeichnungen, nicht Charakter und Verlauf, kappt und nummeriert; Kalender nur zu akuten Objekten der vorigen Blase; eine gültige Referenz wandert offen → gedeckt mit Quelle, eine nicht angebotene wird verworfen und geloggt und die Eigenschaft bleibt offen, ein latentes Objekt bekommt keine; ohne Angebot ist der gerenderte Prompt frei von Sektion und Feld; mit Angebot trägt er beides; `question_target` übergeht die gedeckte; der Block nennt Deckung und Herkunft; der Impuls-Weg bietet nichts an; der Knoten reicht das Angebot des Zustands an den Call (Verdrahtung). |
| **MESSUNG** | Labor, zwei Arme × 5 Läufe, die Pulsar-Anordnung vom Abend (vorige Blase mit zwei offenen Eigenschaften): **Arm A** Angebot mit einem Eintrag, der genau eine der beiden beantwortet — erwartet: sie gedeckt mit G-Quelle, die andere offen; **Arm B** Angebot mit thematisch nahen Einträgen, die keine beantwortet — erwartet: keine Deckung aus dem Gedächtnis (die Fehlerrate erster Art ist die Zahl, die zählt). Dazu die zehn Äußerungen der Scheibe 1 ohne Angebot: Artefakte wie zuvor. **Betrieb:** zwei Wissenschaftsturns zu einer Sache mit Bibliotheksbestand (Neutronensterne: drei Einträge) — `pipeline_log` mit `quellen`, die Log-Zeile des Auflösers, die Dauer des Calls gegen 2,7–4,2 s. Das Maß der Scheibe über die nächsten Betriebsturns: *wie oft war eine offene Eigenschaft im Bestand schon gedeckt.* |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 6.*

### Scheibe 7 — die Plausibilitätsprüfung gegen Weltwissen (entworfen am 29.08.2026)

**Der Anlass:** Schritt 4.5 des Pipeline-Konzepts, Frames §6: *„Mein Elefant ist gestern hergeflogen"* — Nova soll nicht stumm zustimmen. Die Sachlage deckt heute jede Behauptung des Nutzers als Eigenschaft, ohne zu fragen, ob sie stimmen kann; Scheibe 6 holt dazu, was das Gedächtnis weiß — ob die Behauptung *möglich* ist, prüft niemand vor dem Verfasser. **Abgegrenzt gegen den Sykophanz-Sprint:** Dort widerspricht der Nutzer einem Wert, den Nova genannt hat (`graph/einwand.py`, B1 — das Urteil im Kopfblock des Verfassers; B4 zählt den Ausbau). Hier behauptet der Nutzer etwas über die Sache, und die Frage ist, ob die Welt das hergibt — keine Einwandslage, kein Gedächtniswert, nur Weltwissen. **Schritt 4.4 (Cross-Frame) bleibt Konzept:** Er braucht Slots über mehrere Frames aus Fakten oder Lager, und `fakten` trägt 0 Zeilen.

**Der Bau, schmal:** Nach dem Auflöser ruft `_derive` auf dem rechnenden Weg einen zweiten kleinen Call (`graph/nodes/sachlage_plausibility.py::assess_plausibility`, Knoten-Konfiguration `sachlage_plausibilitaet`, T = 0) — nur wenn die Sachlage ein akutes Objekt trägt. Eingabe: die Äußerung des Nutzers und die akuten Objekte mit ihren gedeckten Eigenschaften als Kontext; Auftrag: *Enthält die Äußerung eine Sachbehauptung, die dem Weltwissen widerspricht?* Ausgabe je Objekt eine Liste von Befunden `{behauptung, stufe, grund}` mit den vier Stufen aus Frames §6.2 (`plausibel`, `frage_wert`, `konflikt`, `unmoeglich`); der Code behält nur die drei über `plausibel` (`objekt["plausibilitaet"]`, sonst leere Liste), verwirft unbekannte Stufen laut, und der `[SACHLAGE]`-Block trägt je Befund *»Zweifel (Stufe): Behauptung — Grund«*. **Die Form der Reaktion bleibt Sache von Haltung und Vehikel** (Frames §6.3) — die Lage sagt nur, dass und warum. Reaktionszeitpunkt: sofort (Frames §5.5, Variante A) — eine aufgeschobene Reaktion wäre eine Pixie-Sache. Ohne akutes Objekt kein Call; der Sachlage-Prompt bleibt zeichengleich.

**Was die Scheibe nicht tut:** keine Prüfung von Novas eigenen Antworten (das ist der Thinker), keine Prüfung gegen das Gedächtnis (Scheibe 6), keine Konflikt-Schwellwerte über Frames hinweg (§12.1), kein Frame-Lager als Verteilung (§6.4).

| | |
|---|---|
| **ZIEL** | Behauptet der Nutzer über die akute Sache etwas, das dem Weltwissen widerspricht, trägt die Sachlage den Zweifel mit Stufe und Grund, und der Verfasser bekommt ihn — bei *»ein Neutronenstern von zwölf Sonnenmassen«* steht `unmoeglich` mit dem Grund (TOV-Grenze), bei einer plausiblen Behauptung steht nichts. Eine Frage des Nutzers ist keine Behauptung. |
| **TEST** | Zeugen: der Call läuft nur mit akutem Objekt; sein Prompt trägt Äußerung und Objekte, nicht das Angebot; nur Stufen über `plausibel` bleiben, unbekannte Stufen und Befunde ohne Behauptung werden verworfen und gesagt; jedes akute Objekt trägt `plausibilitaet` (auch leer); der Block nennt Stufe, Behauptung und Grund; Ausfall ist laut und leer; `_derive` ruft ihn nach dem Auflöser (Verdrahtung). |
| **MESSUNG** | Labor, zehn Wissenschaftsäußerungen mit akutem Objekt, je 3 Läufe: 4 plausible, 2 *frage wert*, 2 *Konflikt*, 2 *unmöglich* — die Zahl, die zählt, ist die Fehlalarmrate auf den plausiblen (Ziel 0/12), dann die Trefferrate auf *unmöglich* (Ziel 6/6); Dauer des Calls. **Betrieb:** ein Wissenschaftsturn mit einer unmöglichen Behauptung — Log-Zeile, `pipeline_log` mit `plausibilitaet`, der Block im Verfasser, Novas Antwort. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 7.*

### Scheibe 8 — der Wissensträger: Antwortstoff statt Rückfrage (entworfen am 29.08.2026)

**Der Anlass, gemessen:** Turn 07:04 UTC — *„Das muss ganz schön knallen bei einem Kollaps."* Die Sachlage las richtig (`nutzerziel`: eine Einschätzung zur Energieentladung *erhalten*; akutes Objekt »Kollaps« mit offener Eigenschaft »Energieentladung«), und Scheibe 3 machte genau diese Eigenschaft zum Rückfrage-Gegenstand: Nova fragte den Nutzer, wie das Knallen aussieht — obwohl er sie danach gefragt hatte. Scheibe 3 wurde an Alltagsframes entworfen (Geburtstag → wer/wann: nur der Nutzer weiß es). Im Wissensgespräch liegt das Wissen bei Nova, und eine offene Eigenschaft ist dann **Antwortstoff**, nicht Fragestoff. **Die Absicht:** Nova vervollständigt offene Eigenschaften aus ihrem Weltwissen — und wo das nicht reicht, darf sie nachschlagen; sie muss nicht alles wissen.

**Der Bau, schmal:** Jede offene Eigenschaft bekommt ihren **Träger** — im Sachlage-Call, weil *wer kann das wissen* Teil des Verstehens ist und nicht ein Urteil gegen etwas Äußeres (anders als Auflöser und Plausibilität): `nutzer` (nur der Nutzer kennt es: sein Vorhaben, seine Leute, seine Wahl), `welt` (allgemeines Wissen, aus dem Kopf zu beantworten), `nachschlagen` (Weltwissen, aber speziell, aktuell oder zahlengenau — eine Suche lohnt). `question_target` gibt nur noch `nutzer`-Eigenschaften als Rückfrage-Gegenstand; `answer_targets` liefert die `welt`- und `nachschlagen`-Eigenschaften, die das Gedächtnis nicht deckt (Scheibe 6), und der `[SACHLAGE]`-Block sagt dem Verfasser *»Der Nutzer will dazu wissen: … — beantworte es aus deinem Wissen«*. Für die erste `nachschlagen`-Eigenschaft ohne Deckung läuft **eine** Websuche je Turn (`tools/web/search.py`, dieselbe wie im Thinker; höchstens `SACHLAGE_RECHERCHE_MAX_TREFFER` Treffer), das Objekt trägt sie in `recherche`, der Block *»Nachgeschlagen zu …: …«*. Fehlt der Träger (alte Artefakte, Ausfall), gilt `nutzer` — das heutige Verhalten. Die Haltung bleibt der Regler der Rückfrage; der Antwortstoff geht an ihr vorbei, denn er ist keine Frage.

**Was die Scheibe nicht tut:** keine zweite Suche, kein Nachlesen der Trefferseite (`web_fetch` bleibt dem Thinker), keine Prüfung, ob die Antwort die Eigenschaft dann wirklich deckt (das sieht die Fortschreibung im nächsten Turn — *Deckung von beiden Seiten*), keine Änderung am Responder.

| | |
|---|---|
| **ZIEL** | Bei *„Das muss ganz schön knallen bei einem Kollaps"* fragt Nova nicht, wie das Knallen aussieht, sondern sagt es — aus ihrem Wissen, und bei einer Eigenschaft, die Nachschlagen verlangt, aus einer Suche; bei *„bei uns steht ein Geburtstag an"* fragt sie weiter nach dem Wer. |
| **TEST** | Zeugen: der Sachlage-Prompt trägt das Feld und die drei Werte; die Prüfung verwirft unbekannte Träger laut und lässt fehlende zu; `question_target` übergeht `welt` und `nachschlagen`; `answer_targets` liefert nur ungedeckte; die Suche läuft nur für `nachschlagen`, nur einmal, nur ohne Deckung, und ein Ausfall ist laut und leer; der Block nennt Antwortstoff und Rechercheergebnis; die Verdrahtung in `_derive`. |
| **MESSUNG** | Labor: die zehn Alltagsäußerungen der Scheibe 1 und fünf Wissenschaftsäußerungen, je 3 Läufe über `_derive` — der Träger je offener Eigenschaft (Alltag → `nutzer`, Wissenschaft → `welt`/`nachschlagen`; die Zahl, die zählt, ist *nutzer* an einer Wissensfrage und *welt* an einem Vorhaben), dazu die Artefakte gegen die Vorher-Form (offen/gedeckt unverändert?). **Betrieb:** der Kollaps-Turn erneut — kein Rückfrage-Gegenstand auf der Energieentladung, Antwortstoff-Zeile im Block, Novas Antwort sagt statt fragt; ein Turn mit `nachschlagen` und Suche im Log. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 8.*

### Scheibe 9 — der Sprecher: der Gedanke des Nutzers bleibt seiner (entworfen und gebaut am 29.08.2026, mittags)

**Der Anlass, gemessen:** die Beobachtung vom Morgen — *Nova verliert das Gespür, wer was gesagt hat* — in ihrer zweiten Hälfte. Auf *»Das muss ganz schön knallen bei einem Kollaps«* (07:04 und 07:24 UTC) eröffnete Nova mit *»Das muss ja eine gewaltige energetische Entladung sein«*: der Satz des Nutzers als eigene Feststellung, kein Anschluss. Das Log zeigt, wo es passiert: Der Verfasser **kannte** den Sprecher — sein Kopfblock sagt *»PERSON B sagt, dass der Kollaps ein gewaltiges Ereignis sein müsse«* — und schrieb den Stoff trotzdem als *»Person A stellt fest, dass … eine gewaltige energetische Entladung«*; der Responder machte daraus Novas Rede. Der Verlaufsblock trägt Rollen, der Reiz kommt als Nachricht des Nutzers — was fehlte, war zweierlei: eine Führung, was Person A mit einem fremden Gedanken tut, und in der Lage die Auskunft, **wer eine gedeckte Eigenschaft gesagt hat** — denn Deckung kommt von beiden Seiten (Scheibe 8: *»Was Nova beantwortet hat, deckt die Eigenschaft«*), und im dritten Turn weiß niemand mehr, ob *716 Hz* vom Nutzer oder von Nova kam. Scheibe 8 fragte *wer kann es wissen* (der Träger der offenen Eigenschaft); diese Scheibe fragt *wer hat es gesagt* (der Sprecher der gedeckten).

**Der Bau, schmal:** Jede gedeckte Eigenschaft bekommt im Sachlage-Call ihren **Sprecher** — `nutzer` oder `nova` — als Feld `sprecher` neben `traeger`, mit derselben Regelzeile für den Fortführungsfall (*»JEDE Eigenschaft aus gedeckt … auch eine fortgeführte«* — das Modell kopiert die Form der vorigen Blase, Scheibe 8 hat es gemessen); `_normalize_speakers` hält ihn gegen den Kanon (unbekannte Werte und Schlüssel außerhalb von `gedeckt` fallen laut, fehlend bleibt fehlend), `carry_speakers` erbt aus der vorigen Blase. Der `[SACHLAGE]`-Block trägt je akutem Objekt bis zu drei Zeilen *»Der Nutzer hat zu … gesagt: … — …«* / *»Nova hat schon zu … gesagt: …«* (`speaker_lines`); eine Deckung aus dem Gedächtnis behält ihre Quellenzeile (Scheibe 6) statt eines Sprechers. Und der Herkunftsblock des Nutzer-Turns (`verfasser.fremder_reiz.txt`) **führt** jetzt wie die Impuls-Fassung (F-PROMPT-1): *Die letzte Nachricht der Folge hat PERSON B gesagt … ES IST SEIN GEDANKE — Person A greift ihn als seinen auf: stimmt zu, führt weiter, zweifelt; IHRE EIGENE FESTSTELLUNG BEGINNT DORT, WO SIE ETWAS HINZUFÜGT.* Die alte Fassung verwies auf `[AKTUELLER PROMPT]` — einen Block, den der Verfasser nie setzt. Der Kontext-Tab zeigt `↳nutzer` / `↳nova` hinter der gedeckten Eigenschaft. Ohne Sprecher (alte Artefakte) keine Zeile — das Verhalten vor der Scheibe.

**Was die Scheibe nicht tut:** keine Sprecher im `[GEDAECHTNIS]`-Block (dort verwirft `_format_kzg` das Feld `beobachter` beim Rendern, und die LZG-Resonanz lädt es gar nicht — Fundliste 29.08.), keine Änderung am Responder, kein Urteil über Zustimmung oder Zweifel (das bleibt Haltung und Plausibilität, Scheibe 7).

| | |
|---|---|
| **ZIEL** | Auf *»Das muss ganz schön knallen bei einem Kollaps«* nimmt Nova den Gedanken als den des Nutzers auf (*»Ja, das muss es — …«*) statt ihn als eigene Feststellung zu eröffnen; und im Folgeturn weiß die Lage, dass *716 Hz* Nova gesagt hat und *zwölf Sonnenmassen* der Nutzer. |
| **TEST** | Zeugen: der Sachlage-Prompt trägt das Feld und die zwei Werte; die Prüfung verwirft unbekannte Sprecher laut, lässt fehlende zu und übergeht Schlüssel außerhalb von `gedeckt`; fehlende Sprecher werden aus der vorigen Blase geerbt, und `_derive` ruft die Vererbung; der Block nennt Nutzer- und Nova-Zeilen nur bei akuten Objekten, höchstens drei, und eine Gedächtnis-Deckung behält ihre Quellenzeile; der Herkunftsblock des Nutzer-Turns führt, nennt den Ort des Reizes und trägt kein Verbot. |
| **MESSUNG** | Labor, zwei Arme wie in Scheibe 3: fünf Wissenschaftsäußerungen mit einer Behauptung des Nutzers × 2 Läufe, T = 0, Sachlage frisch über `_derive`, dann der echte Verfasser-Systemprompt — Arm A mit altem Herkunftsblock und Block ohne Sprecherzeilen, Arm B wie gebaut. Gezählt: nennt einer der ersten zwei Sätze des Stoffs Person B als den, der es gesagt hat (Zuschreibung), und stellt der erste Satz fest, ohne Person B zu nennen (Echo)? Dazu die Sprecher der frischen Artefakte und der Fortführungsfall (die Blase aus Redis ohne `sprecher` + ein Verlauf, in dem Nova den Rekordwert nannte + Folgeturn: trägt die Rekord-Eigenschaft `nova`?). **Betrieb:** der Kollaps-Satz über `/chat` — Sprecherzeile im Block, der Stoff nennt Person B, Novas Antwort greift auf. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 9 — und der Abschnitt *Die Betriebsmessung der Kette* (29.08.2026).*

---

### Scheibe 10 — das Gewicht einer Lücke (entworfen und gebaut am 30.08.2026)

**Der Befund.** Scheibe 8 gibt jeder offenen Eigenschaft ihren Träger — *wer kann das wissen*. Sie sagt nichts darüber, *was es kostet, wenn niemand es sagt*. Solange die erste `nutzer`-Eigenschaft den Rückfrage-Gegenstand bekam, entschied die Reihenfolge einer nach Wichtigkeit sortierten Liste darüber, ob Nova nach dem Tragenden oder nach dem Netten fragt — und Wichtigkeit ist nicht dasselbe wie *ohne diese Angabe muss die Antwort raten*. Dasselbe galt für die eine Websuche je Turn.

**ZIEL** Eine offene Eigenschaft, ohne die Novas Antwort raten müsste, ist als kritisch erhoben — und sie bekommt die Rückfrage und die Suche, auch wenn sie nicht vorne steht.

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 10 — dort auch `TEST` und `MESSUNG` dieser Scheibe.*

---

### Scheibe 11 — das Eigenschaftsgedächtnis (entworfen, gebaut und gemessen am 13.09.2026)

**Der Anlass.** Was die Sachlage über eine Sache weiß, lebte an zwei Orten, und keiner trägt über die Blase hinaus: in der Blase selbst (Redis, je Paar überschrieben, Verfall 4 h) und als JSON in der `objekte`-Spalte von `sachlage_verlauf` (Scheibe 4). Ein Objekt, über das an drei Abenden gesprochen wurde, steht dort in drei Zeilen, und seine gedeckten Eigenschaften liest niemand über Turns hinweg. Kehrt ein Gespräch ohne Wiederaufnahme (Scheibe 5) zu einer Sache zurück, beginnt sie bei null; korrigiert der Nutzer einen Wert, ist der alte mit der Blase verschwunden.

**Die Absicht des Eigentümers (13.09.2026), in drei Sätzen:** Je gerechnetem Turn werden die betroffenen Objekte des Gesprächskontexts **abgelegt** — so, wie Entitäten und Fakten persistiert werden. **Die Entität wird später gebunden:** erst festhalten, dann verbinden, sobald es eine Referenz gibt; die Zuordnung darf nach dem Dispatcher oder in einem späteren Turn entstehen. **Ein neuer Wert löst ab, statt zu überschreiben:** Der alte wird inaktiv, der neue steht daneben — wer erst den 1.7. und dann den 1.8. nennt, bleibt belegbar. Das ist die Bauart von `fakten` (`invalidate` setzt `aktiv = FALSE` und `t_invalid`; die Historie liefert aktive und inaktive Zeilen — vor dem Bau am Repository geprüft).

| | |
|---|---|
| **ZIEL** | Eine gedeckte Eigenschaft überlebt Blase und Turn: Sie steht dauerhaft am Objekt des Paares; ein neuer Wert löst den alten ab, ohne ihn zu löschen (*30 → 33 Millisekunden* mit inaktivem Vorgänger), derselbe Wert bestätigt; das Objekt findet seine Entität, sobald die Magnete eines seiner Turns sie nennen; und kehrt das Gespräch **ohne** Blase zur Sache zurück, bekommt der Auflöser den gespeicherten Wert angeboten und übernimmt ihn wörtlich. |
| **TEST** | ~~11 Zeugen live am Schema (`test_sachlage_properties_schema.py`: Tabellen, Löschverhalten, ein aktiver Wert je Eigenschaft von der Datenbank verweigert); 18 an Ablage und Bindung (`test_sachlage_memory.py`: neu / bestätigt / abgelöst, verschwunden → nichts, gleich / Enthaltensein ab vier / nie bei zwei Kandidaten, Satzzeichen, Zeitanker nur bei genau einem, Verdrahtung im Knoten nur mit Verlaufszeile); 10 am Rückweg (`test_sachlage_recall.py`: nur akute Objekte mit offenen Eigenschaften, nie eine gedeckte, Kappung, vor dem Pool, wörtlicher Wert, Verdrahtung in `_derive`)~~ → **berichtigt nach der zweiten Kontrolle** (die Zuordnung war falsch, und die Kappung war nicht bezeugt): **12** live am Schema und an der Ablage (`test_sachlage_properties_schema.py`: Tabellen, Löschverhalten, neu / bestätigt / abgelöst, eine verschwundene Eigenschaft bleibt aktiv, zwei Schreibweisen in einem Turn sind ein Wert, ein Objekt und eine Turn-Zeile je Turn, die Datenbank lässt einen aktiven Wert zu, spätere Bindung einmal); **18** an Namensregel und Bindung (`test_sachlage_memory.py`: gleich / Enthaltensein ab vier / nie bei zwei Kandidaten, Satzzeichen, Magnete aus KZG-Hash und LZG-Knoten, Ablage und Bindung samt Zeitanker, Verdrahtung im Knoten nur auf gerechneten Wegen, Rundlauf gegen Datenbank und Redis); **14** am Rückweg (`test_sachlage_recall.py`: nur akute Objekte mit offenen Eigenschaften, Kappung, ß im Namen, vor dem Pool, wörtlicher Wert nur an der eigenen Eigenschaft, Anspruch ohne Wert deckt nicht, Etikett, Wörtlich-Regel im Prompt, Verdrahtung in `_derive`); dazu die Zeugen der Formregeln (`test_sachlage_form.py`, 31) und der Wert-Regel im Prompt (`test_sachlage.py`). |
| **MESSUNG** | Labor gegen den echten Knoten mit echtem Modell, Laborpaar, Crab-Pulsar-Reihe: T1 Periode 30 ms, T2 Nachfrage, T3 Korrektur auf 33 ms, T4 Folgefrage, dann Blase gelöscht und T5 Rückkehr — Arm A mit, Arm B ohne Wiederaufnahme; Erwartung vor dem Lauf schriftlich. Betrieb: zwei Wissenschaftsturns über `/chat`. Dazu die Auszählung der gedeckten Werte im Bestand und eine Wechselmessung der Wert-Regel. |

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 11 — die drei Tabellen, Schreibweg, Bindung, Rückweg, Prompt-Regeln, Messungen, zweite Kontrolle, Preis und Offenes.*

### Scheibe 12 — der Empfang liest die Lage (Entwurf, 14.09.2026)

*Die Status-Zeile dieser Scheibe steht in [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 12.*

**Der Anlass, gemessen.** Ein Termin mit Tag, Uhrzeit und Dauer entstand über mehrere Turns im Gesprächskontext — als akutes Objekt mit gedeckten Eigenschaften, im Eigenschaftsgedächtnis abgelegt (Scheibe 11). Angelegt wurde er nicht, und die Antworten sagten in 4 von 4 Turns, er sei *„notiert"* oder *„fest verankert"* (Fundliste 13. und 14.09.2026). Drei Stellen tragen das:

1. **Der Empfang liest die Lage nicht.** Die Sachlage läuft unmittelbar vor dem Router (`reducer → sachlage_node → router`), damit *„beide Pfade dasselbe Verstehen sehen"* — gelesen wird sie von Verfasser, Gesprächsvektor und Thinker, nicht von Router, Planner oder Agenten-Dispatch.
2. **Der Empfang sieht den Verlauf in 100 Zeichen je Beitrag** — ein Angebot am Ende einer Antwort erreicht ihn nicht, ein *„Gerne"* ist ohne das Angebot nicht zuordenbar (Fundliste 14.09.2026; `ROUTE-MISS1`, offen seit Chat 54).
3. **Kein Dienst meldet, mit welchen Objekten er umgehen kann.** Die Konvention verbietet es bisher sogar: Die Fähigkeitenliste *„wird nie zur Auswahl gelesen"* (`novaberg-convention-nmcp.md` §3.4).

*Die Entscheidungen des Eigentümers (13. und 14.09.2026), im Wortlaut, stehen in [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md), §4 Scheibe 12. Sie tragen diesen Entwurf.*

**Der Entwurf** — in der Bauart der bestehenden Scheiben, und so, dass der Empfang weiter jeden Zettel für sich beurteilt:

| Teil | Was entsteht | Woran es anschliesst |
|---|---|---|
| **A — die Wahrheit der Antwort** ✅ *gebaut 15.09.2026* | Nach dem Schreiben der Antwort prüft ein Riegel: Behauptet sie ein Speichern, Eintragen, Anlegen, Ändern oder Löschen, ohne dass in diesem Turn ein Dienst mit `abgeschlossen` zurückkam, ist das laut — und die Antwort wird neu geschrieben. Eine Prompt-Zeile allein wäre nur eine Bitte an das Modell. | Thinker/Tribunal/Korrektor-Schleife; `agent_results` des Turns |
| **B — der ganze Verlauf** ✅ *gebaut 16.09.2026* | Die Leser, die Zuordnung und Rückbezug leisten, bekommen die Beiträge ungekürzt; eine Kappung, wo sie bleibt, liegt am Ende und schneidet nicht das Ende ab. | `format_session_turns_numbered` und seine neun Aufrufer |
| **C — die Anmeldung trägt ein Objekt-Merkmal** 🟠 *C1 und C2 gebaut 16.09.2026: Deklaration, Vektor, Nähe im Schatten — noch liest niemand das Urteil* | Jeder Empfangsdienst beschreibt zusätzlich zur Äußerung das **Objekt**, das er bedient — in derselben Sprache, in der die Sachlage Objekte klassifiziert (Klasse, typische Eigenschaften). Die Timeline: *ein Ereignis mit Bezug zu einem Zeitpunkt oder Zeitraum*. Die Nähe zwischen Merkmal und akutem Objekt wird **gerechnet**, nicht erraten; nur ein Objekt mit Nähe über der Schwelle steht am Zettel des Dienstes. | `agents/nmcp.py::aushaenge_sammeln`, Embed-Worker; Konvention §3.2/§3.4 wird erweitert |
| **D — der Empfang liest die Lage** 🟠 *D1 und D2 gebaut 17.09.2026: der Planner fragt nach der Nähe, der Router liest die Lage, der Objektbezug reist zum Dienst — gemessen im Labor, im Betrieb noch kein Lauf* | Der Router bekommt einen `[LAGE]`-Block: die akuten Objekte mit Klasse und gedeckten Eigenschaften, je Objekt die Dienste, zu deren Merkmal es nahe ist. Zustellung, wenn der Nutzer um das Objekt bittet oder einem Angebot zustimmt; der **Objektbezug reist mit** — der Dienst bekommt die Eigenschaften des Objekts als Eingabe, nicht nur den Wortlaut *„Gerne"*. **Seit dem 16.09.2026 je Zettel für sich:** Das Objekt steht an jedem Dienst, dessen Untergrenze es erreicht; im Grenzfall bekommen es beide, und **die Ablehnung des einen hält den anderen nicht auf** (unten, *Teil C2*). | Router; `agent_dispatch`; Klassifikation des Dienstes |
| **E — das Angebot** 🟠 *E1 gebaut 17.09.2026: die Zustimmung braucht ein offenes Angebot; E3 gebaut 18.09.2026: das Nein am Objekt; E2 gebaut 18.09.2026: Nova bietet ~~ab Pflichtbewusstsein 0,9~~ → ab 0,33 mit steigender Wahrscheinlichkeit an (18.09.2026, 21:41 UTC), im Betrieb gemessen* | Ein akutes Objekt, zu dem ein Dienst nahe ist und das nicht abgelehnt ist, wird bei ausreichendem Pflichtbewusstsein zum **Rückfrage-Gegenstand der Art Angebot** (*„ob sie ihn anlegen soll"*). ~~Unter der Schwelle kein Angebot. **Für Notizen (17.09.2026) eine hohe Schwelle:** ein Angebot *»soll ich das notieren?«* nur ab Pflichtbewusstsein 0,9 — sonst wäre es aufdringlich.~~ → **Seit 18.09.2026, für Notizen und Timeline:** unter Pflichtbewusstsein 0,33 kein Angebot, darüber je Turn mit einer Wahrscheinlichkeit, die linear auf 100 % bei 1,0 steigt. Ein Nein setzt am Objekt die Eigenschaft *Speichern abgelehnt*; ein solches Objekt wird nicht wieder angeboten. | `sachlage.py::question_target_origin`, Haltung (`ei/haltung.py`, Speiche `pflicht`), Eigenschaftsgedächtnis |
| **F — die Fachabteilung prüft den Bestand** 🟠 *gebaut 18.09.2026 für die Timeline: Duplikat = selber Tag, ähnlicher Titel, kein Anker* | Ob das Objekt schon gespeichert ist, prüft der Dienst (Timeline: Duplikat-Prüfung vor dem Anlegen, `novaberg-agent-timeline.md` §4.4) und meldet es mit seinem Ausgang. | TimelineAgent |

**Reihenfolge:** A zuerst — unabhängig von allem anderen, und der Defekt tritt heute in jedem Termin-Turn auf. Dann B, weil C bis E ohne den ganzen Verlauf nicht messbar sind. C und D zusammen am Timeline-Dienst; E danach; ein Fakten-Dienst als zweiter Abnehmer, sobald es ihn in heutiger Bauart gibt (der vorhandene ist abgeschaltet und veraltet — M2.5b).

#### Das Kriterium der Zuordnung — entschieden am 16.09.2026

**Teil C braucht eine Trennlinie zwischen den beiden Diensten, die heute beide „merk dir" annehmen.** Sie ist entschieden, im Wortlaut des Eigentümers:

> **„Aber etwas zu erledigendes wie ‚Morgen muss ich das Buch abgeben' passt eher in die Timeline. […] ‚Merke Dir, dass ich morgen Mehl brauche' ist nicht direkt etwas zu erledigendes. Es impliziert vielleicht, dass es etwas zu erledigendes geben könnte, nämlich das Einkaufen, aber der Gegenstand ist Mehl und brauchen. Das ist kein Termin, das ist eine Notiz mit Zeitbezug. Ein Buch abgeben ist eine Erledigung."**

| Der Gegenstand ist … | Dienst | Träger der Zeit |
|---|---|---|
| eine **Handlung oder ein Ereignis, das zu einer Zeit stattfindet** — Buch abgeben, Zahnarzt, Geburtstag, Feiertag, Frist | Timeline | `event_time`, bei Zeiträumen `event_ende` |
| eine **Sache oder ein Zustand mit Zeitbezug** — *morgen Mehl brauchen* | Notizen | `faellig_am`; soll erinnert werden, hängt die Notiz über `timeline_id` an einem Anker |

**Damit entscheidet das Verb, nicht das Zeitwort.** *„Morgen Mehl brauchen"* ist eine Notiz, *„morgen Mehl kaufen"* eine Erledigung und damit Timeline — dieselbe Sache, je nach dem, was der Mensch gesagt hat. Das ist beabsichtigt: Der Empfang deutet die Äußerung nicht um.

> **Ein Zeitwort-Flag kann diese Grenze nicht ziehen, und deshalb gehört sie zu Teil C.** Sie fragt nach der **Klasse des Objekts**, nicht nach dem Vorkommen einer Zeitangabe — genau die Frage, die das Objekt-Merkmal des Dienstes und die gerechnete Nähe beantworten sollen. Der heutige Weg über `needs_timeline` ist das Gegenteil davon und als Defekt erfasst (`PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL`).

**Vorbedingung, gefunden am 13.09.2026:** Ein Zeitraum oder eine Dauer lässt sich heute nicht speichern — `event_ende` hat keinen Schreiber, und `update` kann nur verschieben (Fundliste). Für Zeiträume braucht Teil D diesen Schreiber.

*Offen für den Bau — die Nähe (gemessen und geeicht am 16.09.2026) in [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 12; die übrigen Punkte samt den Entscheidungen vom 15. und 16.09.2026 in [`novaberg-thinking-lage_e.md`](novaberg-thinking-lage_e.md), §4 Scheibe 12.*

*Bau und Messung dazu: [`novaberg-thinking-lage_t.md`](novaberg-thinking-lage_t.md) §4, Scheibe 12 — die gebauten Teile C2, D2, F, A, E2, E3, E1, D1, die Objektwahl, C1, B und A.*

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
