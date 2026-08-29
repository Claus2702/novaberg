# Novaberg — Frames (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Frames — Universales kognitives Substrat (Konzept)
**Stand:** 29. August 2026 (§6 Plausibilität gebaut, offene Slots tragen ihren Wissensträger — Stand-Block vor §5). Davor 28. August 2026 (Konversationsfassung gebaut — Stand-Block vor §5). Davor 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-frames_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 80 (erste Konzeption als Slot-Erhebung pro Vorhaben), Chat 81 (universale Erweiterung — Frame als kognitives Substrat, Akutheit als Trigger, iterative Validierung, Plausibilitätsprüfung, Trennung zu Skills)

**Vorgänger-Stand:** Die Chat-80-Fassung dieses Dokuments definierte Frames eng als "Slot-Erhebung für Vorhaben" und beschrieb einen Pipeline-Pilot am Termin-Frame. Im Verlauf von Chat 81 wurde diese Definition als zu eng erkannt und durch die hier dokumentierte universale Sicht ersetzt. Die alte 4-Phasen-Implementierungsplanung wandert in das Folge-Dokument `novaberg-thinking-cognitive-pipeline_k.md`, weil Pipeline-Mechanik dort besser aufgehoben ist als im Substrat-Dokument.

---

## 1. Vision

Wenn Nova den Satz *"Ich bringe morgen das Auto zum Reifenwechseln"* hört, soll sie nicht nur einen Termin anlegen. Sie soll erkennen, dass mit diesem Satz ein ganzes Geflecht von Frames akut wird — das Auto-Frame mit seinem Standort, das Werkstatt-Frame mit seiner Erreichbarkeit, das Person-Frame mit dem aktuellen Aufenthaltsort des Sprechers, das Reifen-Frame mit der Frage, ob die Sommerreifen schon dabei sind. Wenn der Sprecher in Hamburg sitzt und das Auto in Wolferstadt steht, ist der Satz nicht ausführbar, und das soll Nova merken — bevor der Termin im Kalender steht und morgen zum stillen Fehlschlag führt.

Was hier geschieht, ist nicht Slot-Filling. Es ist **Verstehen** im starken Sinne — die Auflösung einer Aussage in das Geflecht von Wissensobjekten, das sie referenziert, und die Prüfung dieses Geflechts auf Vollständigkeit, Konsistenz und Plausibilität.

Das ist die kognitive Schwester zur emotionalen Wahrnehmung, die Novaberg bereits hat. Während die emotionale Pipeline antwortet auf *"Wie sagt der Nutzer das?"* (Tonfall, Intention, Beziehungsdynamik), antwortet die Frame-Schicht auf *"Was sagt der Nutzer, und passt das zusammen?"*. Sie ist heute der größte blinde Fleck im System — die Stelle, an der die Sachagenten (Notizen, Timeline, Fakten, Dateien) systematisch zu kurz greifen, weil ihnen die Verstehens-Schicht davor fehlt.

> **Leitmetapher:** Ein guter Butler hört nicht nur, was sein Herr sagt, sondern weiß, was zu einem Anliegen dazugehört — und merkt, wenn etwas nicht stimmt. *"Sehr wohl, Sir. Wenn ich darauf hinweisen darf — Ihr Wagen steht aktuell in Wolferstadt. Soll ich der Werkstatt vor Ort einen Termin geben oder die Überführung organisieren?"*

**Designziel:** Frames sind Novabergs kognitives Substrat. Jedes referenzierbare Etwas — Objekt, Vorgang, Person, Ort, Werkzeug, Anweisung — hat ein Frame, das beim Verstehen aktiv werden kann. Das Frame trägt die Slots, die zur vollständigen Erfassung dieses Etwas gehören, und die Constraints, an denen Plausibilität messbar wird.

---

## 2. Kognitionswissenschaftliche Grundlagen

Frames sind kein neues Konzept. Sie sind eine der ältesten und tragfähigsten Ideen der Kognitionswissenschaft, in mehreren parallelen Linien entstanden und bis heute aktiv beforscht.

### 2.1 Frame Semantics (Fillmore, 1976)

Charles Fillmore beschrieb in *"Frame Semantics and the Nature of Language"*, dass Wortbedeutung nicht aus isolierten Lexikoneinträgen entsteht, sondern aus **Frames** — schematischen Wissensstrukturen, die zu einem Begriff dazugehören. Wer das Wort *"verkaufen"* hört, aktiviert automatisch ein Handelsframe mit Verkäufer, Käufer, Ware und Geld. Auch wenn der Satz nur *"Anna hat verkauft"* lautet, sind die anderen Slots im Verstehen mitaktiviert — als offene Fragen.

**Implikation für Nova:** Wenn das LLM einen Begriff erkennt, hat es das zugehörige Frame implizit verfügbar. Wir müssen Frames nicht definieren, sondern nur abrufen.

### 2.2 Frame-Theorie der Wissensrepräsentation (Minsky, 1974)

Marvin Minsky verallgemeinerte das Konzept in *"A Framework for Representing Knowledge"* zur Kerntheorie der KI-Wissensrepräsentation. Bei ihm sind Frames Datenstrukturen für stereotype Situationen — ein Geburtstags-Frame, ein Restaurant-Besuchs-Frame, ein Auto-Frame. Jedes Frame hat **Slots** mit Defaults, **Bedingungen** für gültige Slot-Belegungen und **Verbindungen** zu anderen Frames. Verstehen heißt: das passende Frame finden, mit den verfügbaren Daten füllen, Defaults für Unbekanntes annehmen, Konflikte erkennen.

**Implikation für Nova:** Minskys Architektur — Slot, Default, Constraint, Frame-Verknüpfung — bildet auch heute noch die Mechanik, die wir bauen wollen. Modern ist nur, dass das Slot-Wissen nicht mehr im Code steht, sondern im LLM.

### 2.3 Scripts, Plans, Goals, Understanding (Schank & Abelson, 1977)

Schank und Abelson fügten dem statischen Frame eine zeitliche Dimension hinzu: das **Script**. Ein Script ist ein Frame für einen typischen Ablauf — Restaurant-Besuch (eintreten, hinsetzen, bestellen, essen, zahlen, gehen). Die einzelnen Schritte sind selbst Frames, das Script verkettet sie zu einer Sequenz mit kausalen Abhängigkeiten und Erwartungen.

**Implikation für Nova:** Vorgänge wie *"Reifenwechsel"* oder *"Einkauf"* sind Scripts — Frames mit zeitlicher Struktur. Skills (Dokument 3) werden auf dieser Schicht aufsetzen, sind aber selbst nicht das Frame, sondern eine Anweisung, wie ein Script sinnvoll abzuarbeiten ist.

### 2.4 Schema-Gedächtnis (Bartlett, 1932)

Frederic Bartlett zeigte schon vor knapp einem Jahrhundert, dass Erinnerungen nicht als pixelgenaue Reproduktionen gespeichert werden, sondern als **Schemata** — Gerüste, die beim Abrufen mit Details rekonstruiert werden. Wer eine Geschichte nacherzählt, füllt schematische Lücken mit Plausiblem aus dem eigenen Wissen.

**Implikation für Nova:** Die Rekonstruktion fehlender Slots aus Vor-Wissen ist kein Hack, sondern eine kognitive Grundoperation. *"Wo war der Zahnarzt? Wahrscheinlich Treuchtlingen, da warst du immer."* Bartletts Schemata legitimieren genau diesen Mechanismus.

### 2.5 Slot Filling als Disziplin

Die Dialog-Systeme der späten 1990er und frühen 2000er (DARPA Communicator, TRIPS, RavenClaw) basierten auf Slot-Filling. Der Nutzer hat ein Vorhaben, das System kennt die Slots, die das Vorhaben braucht, und fragt sie strukturiert ab. Damals starr und mit Decision-Trees gebaut, weil die Sprachverarbeitung roh war.

**Implikation für Nova:** Slot-Filling ist eine bewährte Disziplin, kein neues Experiment. Was neu ist: Die Schemas leben im LLM-Wissen, nicht im Code, und die Reihenfolge der Slot-Klärung ist nicht mehr starr.

---

## 3. Frames als universales Substrat

Im Chat-80-Stand dieses Dokuments waren Frames noch *"Slot-Erhebung für Vorhaben"*. Diese Definition ist zu eng. Frames sind das **universale kognitive Substrat** Novabergs. Was sie unterscheidet, ist nicht ihr Wesen, sondern ihre Slot-Zusammensetzung.

### 3.1 Die Frame-Klassen

Eine erste, nicht abschließende Aufzählung der Frame-Klassen, die in Novabergs kognitiver Pipeline auftreten:

**Objekt-Frames** beschreiben Dinge der Welt mit ihren Eigenschaften. *Auto:* Marke, Modell, Standort, Zustand, Halter. *Reifen:* Typ (Sommer/Winter), Größe, Lagerort, Restprofil. *Werkstatt:* Name, Ort, Spezialisierung, Öffnungszeiten.

**Personen-Frames** sind Sonderfall der Objekt-Frames mit eigenem Reichtum: Anna, Meister, der Zahnarzt. Slots: Name, aktueller Aufenthaltsort, Beziehung zum Sprecher, bevorzugter Anredestil, geteilte Vorgeschichte.

**Ort-Frames** beschreiben räumliche Referenzen: Wolferstadt, Hamburg, Treuchtlingen, der Baumarkt in Donauwörth. Slots: Erreichbarkeit, Distanz zu anderen Orten, Funktion (Wohnort, Arbeitsort, Reiseziel).

**Vorgang-Frames** (im Schank-Sinn: Scripts) beschreiben typische Abläufe: Reifenwechseln, Einkaufen, Reisen, Arzt-Besuch. Slots: Voraussetzungen, beteiligte Akteure, Ressourcen, Reihenfolge der Schritte, typisches Ergebnis.

**Werkzeug-Frames** beschreiben die Fähigkeiten der Plugins/Agents: NotizenAgent, TimelineAgent, FaktenAgent, web_search. Slots: Eingaben, Ausgaben, Vorbedingungen, typische Anwendungsfälle, Grenzen.

**Anweisung-Frames** sind eine Sonderkategorie, die in Skills materialisiert wird (siehe Dokument `novaberg-thinking-skills_k.md`): Für eine bestimmte Aufgaben-Klasse beschreibt das Frame, wie der Vorgang sinnvoll abzulaufen hat — welche Werkzeuge zu nutzen sind, welche Defaults zu setzen, welche Rückfragen wann angebracht sind. Das Anweisung-Frame ist aktiv pflegbar (Nova editiert es selbst), die anderen Frame-Klassen sind Beobachtungs-Erträge.

**Anliegen-Frames** beschreiben das, was der Nutzer in einem Turn will: einen Termin anlegen, eine Notiz ändern, eine Frage stellen. Sie sind das, was die Chat-80-Fassung "Vorhaben-Frames" nannte — heute eine Klasse unter mehreren.

Diese Liste ist offen. Mit jeder neuen Domäne (Dateien, Kalender-Synchronisation, externe Datenquellen) kommen neue Klassen hinzu. Der Mechanismus ist aber für alle gleich.

### 3.2 Was Frames nicht sind

Die Universalität der Frame-Sicht erfordert eine sorgfältige Abgrenzung gegen verwandte Konzepte:

**Frames sind keine Skills.** Skills sind Anweisung-Frames, materialisiert als editierbare Markdown-Dateien, die Vorgehen beschreiben. Frames im Allgemeinen sind kognitive Schablonen, die das Verstehen strukturieren. Frames liefern die Slots — Skills verlangen sie. Diese Trennung ist tragend (siehe §8).

**Frames sind keine Workflows.** Ein Workflow ist eine konkrete Ausführungssequenz — *erst dies, dann das, falls A: jenes*. Ein Vorgang-Frame beschreibt das stereotype Wissen über solch eine Sequenz, aber nicht die konkrete Ausführung. Workflows leben im Cognitive Loop (Dokument 2) und sind das Ergebnis der Frame-Aktivierung, nicht das Frame selbst.

**Frames sind keine Datenbank-Records.** Im Frame-Lager (§9) materialisieren wir Beobachtungen über Frames als Records, aber das Frame selbst ist eine kognitive Operation, keine Zeile in der Tabelle. Ein und dasselbe Frame kann in tausend Aktivierungen auftauchen, ohne dass das Lager eine entsprechende Anzahl Records pflegt — Aggregation und Decay sind eingebaut.

**Frames sind kein Code.** Wir definieren Frame-Klassen nicht in einer Schema-Datei. Das LLM kennt sie aus seinem Training. Was wir bauen, ist die Mechanik, mit der Frames im Verstehensvorgang aktiviert, validiert und gegen das eigene Wissen abgeglichen werden.

### 3.3 Frame-Verbindungen

Frames sind nicht isoliert. Sie referenzieren einander über Slots. Ein Termin-Frame hat einen `wer`-Slot, der ein Personen-Frame öffnet. Ein Vorgang-Frame *Reifenwechsel* hat Slots für *Auto* (Objekt-Frame), *Werkstatt* (Ort-Frame), *Termin* (Anliegen-Frame). Ein Werkzeug-Frame *NotizenAgent* hat Slots für die Werkzeug-Eingaben (Listen-Name, Items), die ihrerseits Frames sind.

Diese Verbindungen werden bei der iterativen Validierung (§5) wirksam: Wenn ein Frame akut wird, werden seine slot-referenzierten Frames mit-akut.

---

## 4. Akutheit als Trigger

Frames existieren latent. Das LLM trägt sie in seinem Wissen, das Frame-Lager hält Beobachtungen über sie, aber sie werden nicht geprüft, solange sie nicht akut werden. Diese Trennung ist nicht nur Performance-Frage — sie spiegelt nach, wie biologische Kognition arbeitet. Das Gehirn validiert nicht jede Aussage gegen alles, was es weiß. Es validiert das, was gerade zur Sache wird.

### 4.1 Latenz vs. Aktivierung

Eine **latente** Frame-Aktivierung passiert, wenn ein Begriff erwähnt wird, ohne dass eine Validierung gefordert ist. *"Reifen sind teuer geworden."* aktiviert das Reifen-Frame im Sinne von "das Wort ist verstanden", löst aber keine Slot-Prüfung aus. Es gibt kein Vorhaben, keine Referenz auf eine konkrete Sache, keine zeitliche Nähe.

Eine **akute** Aktivierung passiert, wenn das Frame zur Sache wird. *"Ich brauche neue Reifen für mein Auto, am Wochenende will ich sie wechseln lassen."* — jetzt ist das Frame nicht nur erwähnt, sondern Gegenstand eines konkreten Vorhabens mit zeitlichem Horizont. Slot-Prüfung wird sinnvoll: *Welches Auto? Wo? Welche Werkstatt? Sind die Reifen schon vorhanden?*

### 4.2 Aktivierungs-Quellen

Vier Quellen lösen Akutheit aus, oft gemeinsam:

**Zeitliche Nähe.** *"morgen", "heute", "gleich", "in zwei Stunden"* — explizite zeitliche Verankerung. Ein Vorgang in der Zukunft, der zeitlich greifbar ist, wird akut. *"An Ostern wechsle ich wieder Reifen"* im November ist nicht akut. Im März wird es das.

**Konversationelle Verankerung.** Explizite Referenz auf eine konkrete Sache, nicht beiläufige Erwähnung. *"Mein Auto"* mit besitzanzeigendem Pronomen, *"der Termin"* mit definitem Artikel, Verben des Vorhabens (*"ich plane", "ich bringe", "ich gehe"*). Das ist die Schiene, die im Chat-80-Stand als "Interface vs. Referenz" beschrieben war — bleibt gültig, ist aber nicht die einzige Quelle.

**Situative Aktivierung.** Externe Trigger ohne Sprecherinitiative. Das Frame-Lager merkt: *"Termin Reifenwechsel morgen 10 Uhr"* — bei Tagesbeginn wird das Termin-Frame akut, auch wenn der Sprecher es heute morgen noch nicht erwähnt hat. Das ist die Stelle, an der proaktive Erinnerungen ihren Platz haben.

**Vorbedingungs-Kette.** Ein Slot eines bereits akuten Frames öffnet ein anderes Frame. Termin-Frame akut → Auto-Frame akut (weil Slot `objekt`) → Standort-Slot des Autos akut → Person-Frame akut (weil Sprecher als Akteur). Cascading activation in der klassischen Kognitionswissenschaft.

### 4.3 Smalltalk und Beiläufigkeit

Was nicht akut wird, wird nicht geprüft. Das ist nicht Schwäche, das ist Schutz vor Übergriffigkeit. *"Reifen sind teuer geworden"* ist eine Bemerkung, kein Vorhaben. Wer auf jede Bemerkung mit Slot-Prüfung reagiert, wird unerträglich. Nova muss zwischen Smalltalk und Anliegen unterscheiden, und Frames sind dabei das Filterkriterium.

Diese Disziplin lebt im Classify-Schritt der Cognitive Pipeline (Dokument 2). Sie nutzt die linguistischen Marker aus §4.4 plus den Akutheits-Test: *"Liegt hier eine konkrete Aufgabe oder ein konkreter Sachverhalt vor, der jetzt oder in absehbarer Zeit bearbeitet werden muss?"* Wenn nein — keine Frame-Aktivierung jenseits der latenten.

### 4.4 Linguistische Marker für Akutheit

Aus dem Chat-80-Stand übernommen, im Universal-Kontext leicht erweitert. Diese Liste ist heuristisch — das LLM trifft die Entscheidung, die Liste hilft beim Prompt-Design:

| Marker-Typ | Akut | Latent |
|---|---|---|
| Zeitlich | *morgen, heute, am Freitag, in zwei Wochen* | *irgendwann, mal, wenn ich Zeit habe* |
| Pronomen | *mein, unser, das (definit)* | *ein, irgendein, sowas wie* |
| Verben | *gehe, plane, bringe, will, muss* | *könnte, wäre schön, mag* |
| Subjektnähe | *ich, wir, du* | *man, jemand, die Leute* |

Mehrere Marker zusammen ergeben höhere Akutheits-Wahrscheinlichkeit. *"Ich plane morgen das Auto zur Werkstatt zu bringen"* hat alle vier — eindeutig akut.

### 4.5 Verhältnis zur Chat-80-Fassung "Interface vs. Referenz"

Die alte Unterscheidung war binär: ein Wort ist entweder Interface oder Referenz, ein Frame entsteht oder es entsteht keins. Das war zu starr. *"Ich kaufe morgen Fleisch"* ist nicht Frame-erzeugend (Interface), *"ich gehe morgen einkaufen und besorge Fleisch"* schon (Referenz) — aber die Grenze ist weicher, als der binäre Schnitt suggeriert.

Akutheit ist die feinere Mechanik. Sie ist gradiert, nicht binär. Ein Frame kann *halb akut* sein — erwähnt, aber zeitlich noch fern, wie *"an Ostern Reifen wechseln"* im November. Solche Frames werden im Lager registriert, aber nicht voll validiert. Wenn sie zeitlich näher rücken, gewinnen sie an Akutheit, und die Validierung beginnt.

Die alten Beispiele aus dem Chat-80-Stand (*Anna ist nett heute* vs. *Anna wohnt in München*) bleiben gültig, sind jetzt aber Spezialfälle des Akutheits-Konzepts: Ersteres ist eine flüchtige Eindrucks-Aussage ohne Akutheit, Letzteres ist eine Welt-Aussage mit niedriger akuter Validierungs-Notwendigkeit (kein Vorhaben), aber hoher Frame-Lager-Relevanz (Personen-Frame `Anna` bekommt einen Slot `wohnort` belegt).

---

**Stand 28.08.2026:** Die Konversationsfassung ist gebaut — der Sachlage-Knoten (`novaberg-thinking-lage_k.md` §3) erhebt je Turn Objekte mit Frame-Klasse (§3.1), Akutheit (§4, latent ohne offene Slots: §4.3 als Prüfung im Code) und gedeckten/offenen Slots aus dem Turn und aus Novas Antworten. **Ohne Frame-Lager (§7, §9)**: Die typischen Eigenschaften einer Sache erfindet das Modell je Turn neu — »Geburtstag« bekam einmal `wer`, einmal `Anlass`. Validierung (§5) und Plausibilität (§6) sind nicht gebaut. **Seit dem 28.08.2026, spät, werden offene Slots gegen den Bestand gehalten** (Frame-Auflöser in der Konversationsfassung, `novaberg-thinking-lage_k.md` §4 Scheibe 6): ein eigener Call prüft je akutem Objekt, ob ein Eintrag aus KZG, LZG, Bibliothek, Aufzeichnungen oder Kalender eine offene Eigenschaft beantwortet — gedeckt mit Quelle, sonst offen; im Labor 5/5 richtig und 0/5 falsch. Ohne Frame-Lager bleibt die Lücken-Menge selbst je Turn erfunden. **Seit dem 29.08.2026 ist auch §6 in der Konversationsfassung gebaut** (Scheibe 7): Behauptungen des Nutzers über die akute Sache werden gegen Weltwissen geprüft, in den vier Stufen aus §6.2; Labor 0/12 Fehlalarme, 18/18 nicht-plausible gemeldet, die Stufe im Mittel eine zu hoch. §5 (Cross-Frame) bleibt offen. **Seit dem 29.08.2026, vormittags, trägt jeder offene Slot seinen Wissensträger** (Scheibe 8: `nutzer` / `welt` / `nachschlagen`) — die Lückenbehandlung aus dem Pipeline-Konzept §4.6 in der Konversationsfassung: nur eine `nutzer`-Lücke wird gefragt, die anderen beantwortet Nova, notfalls mit einer Websuche.

---

## 5. Iterative und rekursive Validierung

Sobald ein Frame akut wird, beginnt die Validierung. Sie ist nicht flach, sondern öffnet rekursiv die Frames, die über Slots referenziert werden, und prüft das gesamte Geflecht auf Konsistenz.

### 5.1 Die Reifenwechsel-Diagnose

Konkretes Beispiel, das die Mechanik zeigt:

> *Sprecher in Hamburg sagt: "Ich bringe morgen das Auto zum Reifenwechseln."*

Akute Frames:

1. **Vorgang-Frame** *Reifenwechsel*. Slots: `objekt=Auto`, `zeit=morgen`, `ort=?`, `werkstatt=?`, `reifen_vorhanden=?`.
2. **Objekt-Frame** *Auto* (durch Slot `objekt` aktiviert). Slots: `marke=?`, `standort=?`, `halter=Sprecher`.
3. **Ort-Frame** *Werkstatt* (durch Slot `werkstatt` aktiviert). Slots: `name=?`, `ort=?`, `erreichbarkeit_vom_auto=?`.
4. **Personen-Frame** *Sprecher* (durch impliziten Akteur aktiviert). Slots: `aktueller_aufenthaltsort=?`, `verfügbar_morgen=?`.

Frame-Auflöser zieht aus dem Bestand:

- `Auto.standort` aus Fakten: *Wolferstadt* (Standard-Standort).
- `Sprecher.aktueller_aufenthaltsort` aus letzten Turns / Reisedaten: *Hamburg* (heute angekommen).
- `Werkstatt.name` aus Frame-Lager: häufig *Werkstatt Müller, Wolferstadt* in vorigen Reifenwechsel-Frames.

Plausibilitäts-Test über Frame-Grenzen hinweg:

- `Auto.standort = Wolferstadt`, aber `Werkstatt.ort = Wolferstadt` — passt.
- `Sprecher.aktueller_aufenthaltsort = Hamburg`, aber `Auto.standort = Wolferstadt` — **Konflikt**: Sprecher kann das Auto nicht ohne Weiteres morgen zur Werkstatt bringen.

Das ist nicht ein Slot-Fehler, sondern ein **Cross-Frame-Konflikt**. Eine flache Slot-Erhebung (wie der Chat-80-Stand sie vorsah) würde das nicht entdecken — sie sähe nur, dass `ort` und `werkstatt` rekonstruierbar sind, und liefe durch.

### 5.2 Validierung als rekursive Operation

Schematisch:

```
validiere(frame):
    für jeden slot in frame.slots:
        wenn slot referenziert ein anderes frame:
            sub_frame = aktiviere(slot.referenz)
            validiere(sub_frame)             # rekursiv
            cross_check(frame, sub_frame)    # Konflikte zwischen Frames
        wenn slot ist atomar:
            plausibility_check(slot.wert, slot.constraints)
    plausibility_check(frame als Ganzes)
```

Die Tiefe ist nicht unbegrenzt — pragmatisch reichen 2-3 Ebenen für die meisten Aktivierungen. Die Regel: *aktiv referenzierte* Sub-Frames werden validiert, *bloß genannte* nicht. Bei *"Reifenwechsel morgen"* ist das Reifen-Frame nur genannt, nicht aktiv referenziert — wir prüfen nicht, ob die Reifen ihrerseits einen Lagerort haben, der konsistent ist. Solange der Sprecher nicht *"die Reifen sind in Hamburg"* sagt, bleibt das Reifen-Frame in geringer Akutheit.

### 5.3 Cross-Frame-Konsistenz

Die wichtigste Klasse von Validierungs-Fehlern entsteht zwischen Frames, nicht innerhalb. Beispiele:

- *Sprecher-Standort* vs. *Termin-Ort* (Hamburg-Reifen-Beispiel).
- *Termin-Zeit* vs. *Reise-Zeitraum* (Termin in München während Urlaub auf Mallorca).
- *Anliegen* vs. *Werkzeug-Fähigkeit* (Bitte um Wetterbericht, Werkzeug `web_search` nicht aktiviert).
- *Vorgang-Voraussetzungen* vs. *Bestand* (Backe Kuchen — kein Mehl im Vorrat).

Cross-Frame-Validierung ist genau die Schicht, an der Nova heute systematisch schwach ist. Die einzelnen Agenten arbeiten lokal in ihrem Domänen-Frame, niemand prüft, ob die Frames untereinander passen.

### 5.4 Was bei Konflikt passiert

Konflikt bedeutet nicht zwingend Abbruch. Drei Reaktions-Klassen, je nach Schwere:

**Hart blockierend.** Die Aktion ist physisch oder logisch nicht ausführbar. Sprecher in Hamburg, Auto in Wolferstadt, Werkstatt in Wolferstadt, Reifenwechsel morgen 10 Uhr — das geht nicht. Frame-Auflöser meldet Konflikt zurück, Antwort fragt nach Auflösung: *"Du bist gerade in Hamburg — soll ich einen Termin für nach deiner Rückkehr suchen, oder wird der Wagen anders zur Werkstatt gebracht?"*

**Frage wert, nicht blockierend.** Ungewöhnliche Konstellation, die ein Default-Wert nicht abdecken würde. Reifenwechsel an einem Sonntag — die meisten Werkstätten sind zu, aber es gibt Ausnahmen. Frame-Auflöser meldet als Hinweis, die Antwort kann dezent darauf eingehen: *"Den Sonntag-Termin habe ich notiert — die meisten Werkstätten sind dann zu, ist deine Werkstatt offen?"*

**Plausibel, kein Konflikt.** Der Standardfall. Validierung läuft durch, das Frame ist konsistent, der Vorgang kann angelegt werden.

Die Klassifikation der Konflikt-Schwere ist eine **offene Designfrage** (siehe §11). Eine Heuristik wäre: hart blockierend, wenn ein Slot mit hoher Konsens-Häufigkeit klar widersprochen ist; Frage wert, wenn ein Default unsicher ist.

### 5.5 Reaktionszeitpunkt — Fragen oder Akut warten

Eine zweite offene Designfrage betrifft den Reaktions-*Zeitpunkt*. Gegeben, ein Konflikt ist erkannt — soll Nova sofort reagieren, oder zum Akutheits-Zeitpunkt?

Variante A: **Sofortige Plausibilitäts-Reaktion.** Sprecher sagt heute *"Ich bringe morgen das Auto zur Werkstatt"*, Nova merkt sofort den Standort-Konflikt und antwortet *"Aber du bist in Hamburg…"*. Vorteil: proaktive Beratung, Konflikt früh aufgelöst. Nachteil: kann übergriffig wirken, wenn der Sprecher gerade nur erzählen will.

Variante B: **Aufgeschobene Reaktion zum Akut-Zeitpunkt.** Heute geht der Eintrag durch, morgen früh meldet Nova *"Heute wäre Reifenwechsel — du bist in Hamburg, das passt nicht zusammen"*. Vorteil: weniger aufdringlich. Nachteil: Konflikte werden spät entdeckt, der Termin ist schon im Kalender, möglicherweise wurde was anderes verpasst.

Mein Bauchgefühl, das ich aber nicht hartcoden möchte: Variante A bei Konflikten, die die Durchführbarkeit **blockieren**; Variante B bei Slots, deren Lücke sich später noch schließen lässt. Konflikt-Klassen-abhängige Reaktion, keine globale Regel.

Diese Frage bleibt im Konzept offen und wird in der Implementierungs-Phase pragmatisch entschieden — vermutlich erst, wenn wir ein paar Live-Beispiele beisammen haben.

---

## 6. Plausibilitätsprüfung

Validierung über Slot-Vollständigkeit und Cross-Frame-Konsistenz hinaus gibt es noch eine dritte Operation: die **Plausibilitätsprüfung gegen Weltwissen**. Sie ist die Stelle, an der Frames Constraints tragen, die nicht aus den Daten der Nutzer-Konversation stammen, sondern aus dem allgemeinen Wissen über die Welt.

### 6.1 Konzept

Frames tragen implizit Constraints. Ein Elefant-Frame hat einen Slot *Fortbewegungsart* mit einem Wertebereich, der *gehen, laufen, schwimmen* enthält, aber nicht *fliegen*. Das LLM weiß das aus seinem Training. Wenn jemand sagt *"Mein Elefant ist gestern hergeflogen"*, soll Nova nicht stumm zustimmen, sondern markieren: *Plausibilitäts-Verletzung*.

Wir hardcoden diese Constraints **nicht**. Das wäre der Albtraum-Pfad — eine endlose Tabelle "was ist plausibel". Stattdessen lassen wir das LLM die Plausibilität prüfen, mit dem expliziten Auftrag, gegen sein Weltwissen zu validieren.

### 6.2 Abstufung

Plausibilität ist nicht binär. Vier Stufen, die in der Praxis auftreten:

**Plausibel.** Slot-Wert passt ins Frame, kein Konflikt. *Reifenwechsel im März* — typisch, kein Hinweis nötig.

**Frage wert.** Slot-Wert ist möglich, aber ungewöhnlich. *Reifenwechsel im Juli* — möglich (Reifenkauf, Wechsel auf Neuware), aber atypisch genug, dass eine Rückfrage angemessen wäre. *"Wechseln auf Sommerreifen oder ein Reifenkauf?"*

**Konflikt.** Slot-Wert widerspricht etablierter Erwartung. *Reifenwechsel im November in Mallorca, wo es keine Saisonreifen gibt.* Das ist ein erkennbarer Konflikt — Mallorca-Wissen + Reifensaison-Wissen.

**Unmöglich.** Slot-Wert verletzt grundlegende Welt-Constraints. *Mein Elefant ist hergeflogen.* Hier soll Nova nicht stumm bleiben.

### 6.3 Reaktionsformen

Wie auf jede Stufe reagiert wird, hängt vom Vehicle ab (Beziehungs-Schicht, siehe §10). Das Frame liefert nur den Plausibilitäts-Wert, der Responder formt daraus eine angemessene Antwort. *Plausibel* — keine Reaktion. *Frage wert* — sanfte Rückfrage. *Konflikt* — klärende Bemerkung. *Unmöglich* — direkte Markierung, mit der Möglichkeit, dass es Metapher oder Scherz ist (*"Du meinst sicher, der Elefant kam mit dem Flugzeug?"*).

Wichtig: Plausibilitätsprüfung ist nicht Besserwisserei. Sie ist die Stelle, an der Nova Verstehen demonstriert, indem sie nicht durchwinkt. Aber sie soll dezent sein, nicht belehrend. Die Vehicle-Schicht entscheidet die Form.

### 6.4 Plausibilität als Slot-Eigenschaft

Im Frame-Lager (§9) wird Plausibilität nicht als separates Schema gespeichert, sondern emerge implizit aus der Häufigkeit und Verteilung der beobachteten Slot-Werte. Wenn `Elefant.fortbewegung` in 1000 beobachteten Frames immer eines aus *gehen, laufen, schwimmen* war, wird *fliegen* zu einer Anomalie. Das LLM kann diese Verteilung im Lager nachschlagen — aber meistens reicht sein Trainings-Wissen.

---

## 7. Doppelte Bewegung — LLM-Wissen und Frame-Lager

Aus dem Chat-80-Stand übernommen, im Universal-Kontext etwas ausgeweitet. Frames werden nicht im Code definiert. Sie sind Weltwissen, das das LLM hat. Aber für Nova-spezifisches Lernen brauchen wir einen **zentralen Speicher**, der über das Generelle hinaus die Beobachtungen über *diesen* Nutzer und *seine* Welt sammelt.

### 7.1 Warum eleganter als hardcoded Schemas

| Vergleich | Hardcoded Schema | LLM-Wissen + Frame-Lager |
|---|---|---|
| Neue Frame-Klasse (z.B. *Werkstatt-Termin* spezifisch vs. *Termin* generell) | Code-Änderung nötig | Funktioniert sofort |
| Frame-Variante (z.B. *Geburtstags-Termin* mit zusätzlichem Slot *Geschenk*) | Schema-Erweiterung | Slot wird einfach mit erhoben |
| Domänen-spezifisches Wissen (z.B. *Zahnarzt = meist Zahnreinigung*) | Externer Knowledge Graph | Frame-Lager lernt aus Häufigkeit |
| Selbst-Korrektur (z.B. *Kunde hat doch keinen `wo`-Slot, war Default*) | Manueller Eingriff | Lager passt Konsens an |

### 7.2 Lager als Beobachtungs-Aggregat

Das Frame-Lager sammelt:

- **Welche Frame-Klassen haben wir gesehen?** (Termin, Einkauf, Reifenwechsel, Person *Anna*, Ort *Treuchtlingen*…)
- **Welche Slots werden bei Klasse X typischerweise belegt?** (Bei *Termin* meistens `wer/wo/wann/was`, manchmal `anlass`, selten `kosten`.)
- **Welche Werte tauchen häufig auf?** (Bei `wo` für *Zahnarzt-Termin* dieses Nutzers: *Treuchtlingen*.)
- **Welche Frame-Verbindungen treten auf?** (Reifenwechsel-Frame öffnet typisch Auto-Frame, das öffnet Standort-Frame.)

Das Lager ist nicht autoritativ. Es zwingt keine Schemas auf. Es **hilft** beim Frame-Auflöser (Defaults rekonstruieren) und beim Plausibilitäts-Test (Anomalien erkennen).

### 7.3 Lernende Eigenschaften

Fünf Lern-Mechanismen, die das Lager nicht statisch lassen:

**Häufigkeits-Aggregation.** Je öfter ein Slot belegt wird, desto mehr "gehört" er zur Frame-Klasse. Ein Termin-Frame mit `wo=null` in 90% der Fälle ist ein Hinweis, dass `wo` für diesen Nutzer nicht kritisch ist (vermutlich Telefontermine oder Routine-Treffen ohne Ortswechsel).

**Wert-Cluster.** Häufige Werte für einen Slot werden zur impliziten Default-Annahme. *Treuchtlingen* bei Zahnarzt-`wo` wird zum Erst-Vorschlag des Auflösers.

**Recency-Gewichtung.** Jüngere Beobachtungen wiegen mehr als ältere. Wenn *Treuchtlingen* in 12 von 14 Zahnarzt-Frames der letzten zwei Jahre vorkommt, aber die letzten drei Beobachtungen in *Donauwörth* waren, soll der Default sich anpassen. Mechanik: zeitlich gewichtete Häufigkeit (linear oder exponentiell), nicht reine Zählung. Das Lager folgt der Realität, ohne dass jemand explizit *"vergiss Treuchtlingen"* sagen muss.

**Korrektur-Gewichtung.** Wenn ein Default-Vorschlag des Auflösers vom Nutzer aktiv korrigiert wird (*"Nicht in Donauwörth, in Treuchtlingen"*), zählt das stärker als eine beiläufige Beobachtung. Korrekturen sind explizite Lehrmomente und sollen entsprechend gewichtet werden — pragmatisch fünf- bis zehnfach im Vergleich zur normalen Häufigkeit. Das macht das Lager schnell-lernend gegen Fehler, ohne dass es bei jeder beiläufigen Erwähnung zappelt.

**Schema-Aggregation.** Über die einzelnen Beobachtungen hinaus pflegt das Lager pro Frame-Klasse einen aggregierten **Schema-Zustand**: welche Slots sind typisch, welche optional, welche Defaults sind aktuell etabliert. Dieser Aggregat-Zustand wird beim Hot-Cache (siehe Cognitive-Pipeline-Dokument §4.11) direkt abgerufen, ohne dass für jede Frame-Aktivierung ein neuer LLM-Call das Slot-Inventar bestimmen muss.

**Decay.** Alte, selten reproduzierte Frame-Klassen verschwinden langsam. Das Schema lebt mit dem Nutzer.

---

## 8. Frames im Verhältnis zu Skills

Das ist die zentrale Pipeline-Trennung, die im Chat-80-Stand noch verschwommen war. Sie wurde in Chat 81 herausgearbeitet und ist tragend für die gesamte kognitive Architektur.

> **Frames liefern die Slots — Skills verlangen sie.**

Frames sind kognitive Schablonen, die das Verstehen einer Aussage strukturieren und mit Wissen verzahnen. Sie sagen, *was an Informationen vorhanden sein und gesammelt werden muss*. Skills sind Arbeitsanweisungen, die diese Informationen *konsumieren* und in Vorgehen übersetzen.

### 8.1 Beispiel zur Trennung

Anliegen-Frame *Wetterbericht*:

- Slots: `ort`, `zeit`, `tiefe` (kurz/ausführlich).
- Frame-Auflöser füllt Lücken: `ort` aus Standort-Fakten, `zeit=heute` als Default, `tiefe=kurz` als Default.
- Plausibilitäts-Test: `ort=Wolferstadt` mit `zeit=heute` plausibel.

Skill *Wetterbericht-Vorgehen* (siehe `novaberg-thinking-skills_k.md`):

- Nimmt `ort`, `zeit`, `tiefe` aus dem Frame.
- Anweisung: *Suche bei agrarwetter.org, wenn ländliche Region; sonst allgemeine Wettersuche. Wenn Termine an dem Tag in anderem Ort, prüfe dort auch. Liefere kurz, wenn nicht ausführlich gefordert.*
- Ruft `web_search` mit dem aus den Slots gebauten Query.

Frame ohne Skill funktioniert: das LLM würde aus den Slots eine plausible Wettersuche machen, vielleicht nicht optimal. Skill ohne Frame funktioniert nicht: ohne Slots fehlt das Material zum Anweisungs-Bezug. **Frames sind Vorbedingung für Skill-Anwendung.**

### 8.2 Konsequenz für die Reihenfolge

In der Cognitive Pipeline (Dokument 2) steht die Frame-Erhebung **vor** dem Skill-Lookup. Sequenz:

1. Aussage parsen, Frame-Klassen aktivieren (Anliegen, Objekte, Personen, Orte).
2. Frame-Auflöser füllt Slots, validiert Cross-Frame.
3. Mit dem aufgelösten Anliegen-Frame Skill-Lookup im Speicher.
4. Skill-Executor führt das Vorgehen aus, mit Slot-Werten als Input.
5. Werkzeug-Aufrufe (NotizenAgent, web_search…) mit Skill-Steuerung.
6. Reflexion über Ergebnis, ggf. Skill-Edit als Antwort auf Negativ-Feedback.

Dokument 2 detailliert diese Pipeline. Dieses Dokument hier endet bei Schritt 2.

---

## 9. Frame-Lager — Schema und Operationen

Aus dem Chat-80-Stand übernommen, leicht angepasst an die universale Sicht.

### 9.1 Schema (vorläufig)

```sql
CREATE TABLE frames (
    id              SERIAL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    character_id    TEXT NOT NULL,
    frame_klasse    TEXT NOT NULL,        -- 'anliegen_termin', 'objekt_auto',
                                          -- 'person_anna', 'ort_treuchtlingen',
                                          -- 'vorgang_reifenwechsel', ...
    slots           JSONB NOT NULL,       -- aufgelöste Slot-Belegungen
    quellen         JSONB,                -- pro Slot: prompt|rekonstruiert|default
    haeufigkeit     INTEGER DEFAULT 1,
    erstellt_am     TIMESTAMPTZ DEFAULT NOW(),
    zuletzt_gesehen TIMESTAMPTZ DEFAULT NOW(),
    timeline_id     INTEGER REFERENCES timeline(id) ON DELETE SET NULL,
    notiz_id        INTEGER REFERENCES notizen(id) ON DELETE SET NULL,
    aktiv           BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_frames_klasse      ON frames (user_id, character_id, frame_klasse);
CREATE INDEX idx_frames_zuletzt     ON frames (zuletzt_gesehen DESC);
CREATE INDEX idx_frames_slots_gin   ON frames USING GIN (slots);
```

Paar-skopiert über `(user_id, character_id)` analog zu LZG/Notizen/Timeline (Magneten-Convention §6). Querverweise zu Timeline/Notizen für Re-Identifikation, weil viele Anliegen-Frames dort materialisiert sind. Querverweise zu Knowledge-Graph-Entitäten ergänzbar (zukünftige Erweiterung).

**Hinweis zur Klassen-Konvention:** `frame_klasse` ist ein Präfix-strukturierter String. *anliegen_termin*, *objekt_auto*, *person_anna*, *ort_treuchtlingen* — das Präfix gibt die Frame-Kategorie, der Rest die spezifische Klasse. Das vereinfacht spätere Analysen: alle Anliegen-Frames per `WHERE frame_klasse LIKE 'anliegen_%'`.

### 9.2 Operationen

```python
def frame_registrieren(klasse, slots, quellen, ...) -> int:
    """Legt Frame-Eintrag an. Erhöht Häufigkeit, falls ähnliches Frame existiert.
    Ähnlichkeit über Klasse + Slot-Schlüssel-Übereinstimmung."""

def frame_konsens_holen(klasse) -> dict | None:
    """Aggregiert Konsens für Frame-Klasse mit Recency-Gewichtung:
       - typische Slots (welche werden in >X% der Fälle belegt?)
       - typische Werte (Modus, häufigste Belegung, jüngere stärker gewichtet)
       - durchschnittliche Vollständigkeit
       Korrekturen (siehe frame_korrektur_registrieren) zählen mehrfach."""

def frame_schema_holen(klasse) -> dict | None:
    """Schnellzugriff auf den aggregierten Schema-Zustand pro Klasse:
       - slots_typisch: Liste der Slots, die in >X% der Fälle belegt sind
       - slots_optional: Liste der Slots, die selten, aber regelmäßig auftreten
       - defaults: Dict mit aktuell etablierten Default-Werten pro Slot
       - reife_stufe: 'cold', 'warm', 'hot' anhand Häufigkeit
       Wird vom Cognitive Loop (Pipeline §4.11) für die Cache-Hierarchie genutzt.
       Wenn nicht vorhanden oder nur 'cold': LLM-basierte Slot-Inventarisierung."""

def frame_aehnliche_finden(klasse, slots) -> list[dict]:
    """Findet Frames mit gleicher Klasse und teil-überlappenden Slots.
       Für Rekonstruktion: 'In früheren Zahnarzt-Frames war wo=Treuchtlingen'."""

def frame_korrektur_registrieren(klasse, slot, falscher_wert, korrekter_wert) -> None:
    """Verbucht eine vom Nutzer ausgesprochene Korrektur eines Default-Vorschlags.
       Erhöht das Gewicht des korrekten Werts deutlich (5-10× normale Häufigkeit),
       reduziert das Gewicht des falschen Werts. Triggert ggf. Default-Wechsel im
       Schema-Aggregat."""

def frame_decay() -> int:
    """Decay analog zu LZG: alte, selten gesehene Frames verlieren Gewicht.
       Salienz-inspirierte Decay-Funktion (siehe Memory-Decay-Konzept)."""
```

### 9.3 Verhältnis zum Knowledge Graph

Das Frame-Lager und der Knowledge Graph sind verschiedene Schichten:

| | Frame-Lager | Knowledge Graph |
|---|---|---|
| Granularität | Frame-Schemas mit Slot-Belegungen | Atomare Tripel `(S, P, O)` |
| Lebensdauer | Wachsend, decaybar | Bi-temporal (`valid_from`, `valid_to`) |
| Zweck | Schema-Konsens, Vor-Erfahrung, Plausibilitäts-Basis | Welt-Wissen für Anfragen |
| Schreibtrigger | Frame-Aktivierung im Cognitive Loop | Salienz, Planner, Agent-Push |

Zusammenspiel: Ein neuer Termin-Frame schreibt sowohl ins Frame-Lager (als Schema-Beleg und Quelle für künftige Plausibilitäts-Tests) als auch über den FaktenAgent-Push in den Knowledge Graph (als atomare Tripel).

---

## 10. Frames im Verhältnis zu existierenden Konzepten

### 10.1 Magneten-Convention

Magneten sind quer-thematische Achsen, die KZG/LZG-Einträge bündeln (Akteur, Thema, Zeit, Ort). Frame-Slots können Magneten **füttern**: aus dem Termin-Frame werden `wer → akteur_magnet`, `was → thema_magnet`, `wo → ort_magnet`, `wann → zeit_magnet`. Magneten sind die Speicher-Sicht, Frames die Verstehens-Sicht. Beide profitieren voneinander, sind aber nicht identisch.

### 10.2 Domain Language (Pattern)

Domain-Language-Vokabular (siehe `novaberg-pattern-domain-language.md`) liefert die sprachlichen Marker, mit denen das LLM Frame-Klassen erkennt. Termin-Frame wird durch *"Termin", "Treffen", "Verabredung"* aktiviert; Reifenwechsel-Frame durch *"Reifen wechseln", "Räder umstecken", "Saisonreifenwechsel"*. Domain Language ist das Vokabular, Frame ist die Struktur dahinter.

### 10.3 Substanz-Filter (Magneten-Convention §7)

Der Substanz-Filter trennt substantielles Wissen von dekorativem Smalltalk auf der Speicher-Ebene. Frame-Aktivierung trifft eine ähnliche Trennung auf der Verstehens-Ebene: nur akute Frames werden voll validiert. Beide Filter sind verwandt, leben aber an verschiedenen Stellen der Pipeline.

### 10.4 Entity Resolution (Pattern)

Entity Resolution gleicht *"der Zahnarzt"* mit *"Dr. Müller, Treuchtlingen"* ab. Das ist Slot-Belegung im Personen-Frame über bestehendes Knowledge-Graph-Wissen. Entity Resolution ist eine Mechanik, die der Frame-Auflöser nutzt — kein paralleler Mechanismus.

### 10.5 Drive und Neugier

Wenn ein Frame Slots offen lässt, die das Lager-Wissen als kritisch ausweist, kann das ein **Neugier-Trigger** sein: Nova fragt sich selbst (im Pixie-Reflexionslauf), warum der Slot fehlt, und ob Vor-Wissen über andere Quellen aktivierbar ist. Drive-Themen wachsen aus wiederholt unaufgelösten Slots in einer Domäne. Diese Verbindung ist konzeptionell, in der Implementierung später aufzubauen.

### 10.6 Vehicle als separate Beziehungs-Schicht

Vehicle ist die Sprach- und Beziehungsschicht: *wie* etwas gesagt wird, nicht *was*. Aus der Chat-80-Fassung übernommen und unverändert gültig. Frames sind Struktur, Vehicle ist Form. Der Frame-Auflöser meldet *"Konflikt: Sprecher in Hamburg, Auto in Wolferstadt"*; der Responder formt daraus *"Du bist gerade in Hamburg — magst du den Termin nach deiner Rückkehr legen, oder fährt jemand das Auto rüber?"*. Vehicle wohnt im Responder/Gesprächsraum, nicht im Frame-System.

### 10.7 Emotionale Pipeline

Frames sind die kognitive Schwester der emotionalen Pipeline. Beide laufen pro Turn, aber an verschiedenen Stellen. Die emotionale Pipeline verarbeitet *"wie sagt der Nutzer das"* (Tonfall, Intention, Dual-Emotion). Die Frame-Schicht verarbeitet *"was sagt der Nutzer, und passt das"*. Sie sind komplementär — ein Turn braucht beides — und greifen nicht in dieselben State-Felder ein. Konvergenz passiert im Responder, der beide Quellen für die Antwortformung nutzt.

---

## 11. Designprinzipien

Die Leitsätze, die in der Diskussion auftauchten und das Konzept tragen:

**Frames sind universales Substrat.** Objekt, Vorgang, Person, Ort, Werkzeug, Anweisung — alles ist Frame, unterschieden nur durch Slot-Zusammensetzung.

**Akutheit ist Trigger.** Latente Frames werden nicht geprüft. Prüfung beginnt bei Referenz, zeitlicher Nähe oder situativer Aktivierung.

**Validierung ist iterativ und rekursiv.** Slots öffnen Sub-Frames, Cross-Frame-Konflikte werden auf der zweiten und dritten Ebene gefunden — nicht in der flachen Slot-Sicht.

**Plausibilität gehört zum Frame.** Constraints gegen Weltwissen sind keine separate Schicht, sondern Eigenschaft der Frame-Klasse. Das LLM prüft, der Code orchestriert.

**Frames liefern Slots, Skills verlangen sie.** Saubere Trennung. Frames sind Verstehens-Schablonen, Skills sind Vorgehens-Anweisungen.

**Lager lernt, zwingt nicht.** Das Frame-Lager ist Konsens-Speicher, nicht Schema-Definition. Es hilft beim Auflöser und Plausibilitäts-Test, ohne Schemas aufzuoktroyieren.

**Latenz ist Schutz, nicht Mangel.** Nicht jeder Begriff aktiviert eine volle Frame-Validierung. Was nicht akut wird, wird nicht geprüft. Das hält Nova frei von Besserwisserei.

---

## 12. Offene Punkte und nächste Schritte

### 12.1 Offene konzeptionelle Fragen

**Reaktions-Zeitpunkt bei Konflikten** (§5.5). Sofortige Plausibilitäts-Reaktion oder aufgeschobene Reaktion zum Akutheits-Zeitpunkt? Vorerst: konflikt-klassen-abhängig, Entscheidung pragmatisch in der Implementierung.

**Konflikt-Klassifikation** (§5.4). Wann ist ein Konflikt hart blockierend, wann Frage wert? Vermutlich Heuristik aus Konsens-Häufigkeit im Lager. Genauer Algorithmus offen.

**Akutheits-Schwelle als skalarer Wert?** Akutheit ist hier qualitativ beschrieben (latent, halb-akut, akut). Ob das in der Implementierung eine binäre, dreistufige oder kontinuierliche Variable wird, ist offen.

**Frame-Klasse-Hierarchie.** Sollen Frames in Klassen-Hierarchien stehen? *Termin* als Oberklasse, *Zahnarzt-Termin* und *Werkstatt-Termin* als Spezialisierungen mit zusätzlichen Slots? Pragmatisch: vorerst flach, spätere Hierarchisierung möglich.

**Frame-Lager-Initialbefüllung.** Startet das Lager leer und füllt sich durch Beobachtung, oder gibt es einen Seed mit häufigen Frame-Klassen (Termin, Person, Ort)? Empfehlung: leer starten, Seed wäre vorzeitige Optimierung.

**Plausibilitäts-Implementierung.** LLM-Call pro akutem Frame, oder Sammel-Call mit allen aktiven Frames? Performance-Frage, in der Implementierung zu klären.

### 12.2 Implementierungs-Reihenfolge

Die Phasen-Planung wandert in das Folge-Dokument `novaberg-thinking-cognitive-pipeline_k.md`, weil Pipeline-Mechanik dort orchestriert wird. Hier nur die Markierung, dass die Frame-Schicht **vor** der Skill-Schicht implementiert werden muss — Skills brauchen Frames als Input.

Aus dem Chat-80-Stand bleibt der Hinweis, dass die Phase 0 (Vorbedingungen) weiterhin gilt:

- M2.5b — FaktenAgent als echter Agent statt Plugin
- TIMELINE-PAIR-MIGRATION
- NOTIZEN-PAIR-MISSING
- FAKTEN-PAIR-IGNORED

Diese Migrations-Themen sind unabhängig vom Frame-Konzept anzugehen — sie bereinigen das Paar-Schema und sind Voraussetzung für den FaktenAgent-Push in §9.3.

### 12.3 Risiken

**Über-Validierung.** Wenn jeder Turn rekursiv mehrere Frames öffnet, droht Latenz-Explosion. Pragmatisch: harte Tiefenbegrenzung (2-3 Ebenen), Akutheits-Filter als Gatekeeper.

**Halluzinierte Slots.** Das LLM erfindet Slots, die nicht im Lager sind. Gegenmaßnahme: das Lager kennt die typische Slot-Menge pro Klasse, ungewöhnliche Slots werden markiert, nicht still übernommen.

**Lager-Pollution.** Schlecht erhobene Frames verschmutzen den Konsens. Gegenmaßnahme: Decay, Häufigkeits-Untergrenze für Default-Wert-Übernahme.

**Vehicle-Lärm.** Plausibilitäts-Hinweise klingen schnell besserwisserisch, wenn sie nicht über die Vehicle-Schicht laufen. Gegenmaßnahme: Frame-System liefert nur strukturelle Information, Responder formt aus.

---

## 13. Verweise

### Verbindliche Dokumente

- `novaberg-architecture.md` — Architektur, in die Frames eingebettet werden
- `novaberg-convention-paar-schema.md` — Paar-Skopierung (`user_id`, `character_id`)
- `novaberg-convention-magneten.md` — Magneten als Bündelung-Schicht, von Frame-Slots gefüttert

### Folge-Dokumente (in Arbeit)

- `novaberg-thinking-cognitive-pipeline_k.md` — Cognitive Loop, Pipeline-Mechanik, Akutheits-Trigger als Schritt-Folge, Skill-Lookup-Position
- `novaberg-thinking-skills_k.md` — Skills als Anweisung-Frame, Lifecycle, Editor, Reflexion

### Verwandte Konzepte

- `novaberg-thinking-curiosity_k.md` — Neugier als Folge unaufgelöster Slots
- `novaberg-thinking-drive_k.md` — Drive-Themen aus Frame-Lager-Wachstum
- `novaberg-metakognition_k.md` — Selbstbeobachtung und Vorsätze, Reflexions-Trigger
- `novaberg-pattern-domain-language.md` — Vokabular für Frame-Aktivierung
- `novaberg-pattern-entity-resolution.md` — Slot-Belegung über Entity-Match

### Quellen

- Fillmore, C. J. (1976). *Frame Semantics and the Nature of Language.* Annals of the New York Academy of Sciences, 280, 20–32.
- Minsky, M. (1974). *A Framework for Representing Knowledge.* MIT-AI Laboratory Memo 306.
- Schank, R. C., & Abelson, R. P. (1977). *Scripts, Plans, Goals, and Understanding: An Inquiry into Human Knowledge Structures.* Lawrence Erlbaum.
- Bartlett, F. C. (1932). *Remembering: A Study in Experimental and Social Psychology.* Cambridge University Press.

---

*Stand 09.05.2026 — Chat 81. Universalisierung der Frame-Sicht aus dem Chat-80-Vorgängerstand. Akutheit, iterative Validierung, Plausibilitätsprüfung, Frame-vs-Skill-Trennung. Phasen-Plan ausgelagert in das Cognitive-Pipeline-Dokument.*
