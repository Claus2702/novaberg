# Novaberg — Frames (Konzept)

**Absicht:** Nova löst eine Aussage in das Geflecht der Frames auf, die sie referenziert — Objekte, Personen, Orte, Vorgänge, Werkzeuge, Anweisungen und Anliegen mit ihren Slots —, prüft dieses Geflecht erst, wenn es akut wird, auf Vollständigkeit, Konsistenz zwischen den Frames und Plausibilität gegen Weltwissen, und lernt aus dem, was dieser Nutzer und seine Welt zeigen, ohne Schemas aufzuzwingen; Frames liefern die Slots, Skills verlangen sie.
**Stand:** 14. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Frames · Skills · Task-Orchestration · Cognitive Pipeline — im Bau als Lage-Konzept* 🟠 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md) · [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md) · [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md) · Messungen: keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-thinking-frames_k.md §5.3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md), `_b` ist [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md), `_e` ist [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md). Einen Teil `_m` gibt es nicht: Die Laborzahlen des Konzepts stehen im Stand-Block zwischen §4 und §5 und bleiben dort, weil ein Absatz nicht zerschnitten wird.

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle | `_k` |
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 · 2.4 · 2.5 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 | `_k`; der *Nachtrag 14.09.2026* aus §3.1 (Werkzeug-Frame) in `_b` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 · 4.5 | `_k` |
| Stand-Block zwischen §4 und §5 (*Stand 28.08.2026* …) | `_b` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 · 5.5 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 | `_t` |
| 7 · 7.1 · 7.2 · 7.3 | `_t` |
| 8 · 8.1 · 8.2 | `_k` |
| 9 · 9.1 · 9.2 · 9.3 | `_t`; der *Nachtrag 13.09.2026* aus §9.1 (ein Teil des Lagers steht) in `_b` |
| 10 · 10.1 · 10.2 · 10.3 · 10.4 · 10.5 · 10.6 · 10.7 | `_k` |
| 11 | `_k` |
| 12 · 12.1 · 12.3 | `_e` (Abschnitt C) |
| 12.2 | `_b` |
| 13 | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Quellen, Vorgänger-Stand) und bisherige Schlusszeile (*Stand 09.05.2026 …*) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, offene Punkte, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

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

> **Hinweis zur Aufteilung (19.09.2026):** Hier stand der *Nachtrag 14.09.2026* zum Werkzeug-Frame (die erste Form als Objekt-Merkmal in der Anmeldung eines Dienstes). Er steht in [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md), *Aus §3.1*.

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

> **Der Stand-Block zwischen §4 und §5 und die Abschnitte §5 bis §7 stehen nicht in dieser Datei.** Der Stand-Block (*Stand 28.08.2026* …, was in Konversationsfassung gebaut ist) steht in [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md); die iterative und rekursive Validierung (§5), die Plausibilitätsprüfung (§6) und die doppelte Bewegung aus LLM-Wissen und Frame-Lager (§7) stehen in [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md).

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

> **§9 steht nicht in dieser Datei.** Schema und Operationen des Frame-Lagers stehen in [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md).

## 10. Frames im Verhältnis zu existierenden Konzepten

### 10.1 Magneten-Convention

Magneten sind quer-thematische Achsen, die KZG/LZG-Einträge bündeln (Akteur, Thema, Zeit, Ort). Frame-Slots können Magneten **füttern**: aus dem Termin-Frame werden `wer → akteur_magnet`, `was → thema_magnet`, `wo → ort_magnet`, `wann → zeit_magnet`. Magneten sind die Speicher-Sicht, Frames die Verstehens-Sicht. Beide profitieren voneinander, sind aber nicht identisch.

### 10.2 Domain Language (Pattern)

Domain-Language-Vokabular (siehe `novaberg-pattern-domain-language.md`) liefert die sprachlichen Marker, mit denen das LLM Frame-Klassen erkennt. Termin-Frame wird durch *"Termin", "Treffen", "Verabredung"* aktiviert; Reifenwechsel-Frame durch *"Reifen wechseln", "Räder umstecken", "Saisonreifenwechsel"*. Domain Language ist das Vokabular, Frame ist die Struktur dahinter.

### 10.3 Substanz-Filter (Magneten-Convention §7)

Der Substanz-Filter trennt substantielles Wissen von dekorativem Smalltalk auf der Speicher-Ebene. Frame-Aktivierung trifft eine ähnliche Trennung auf der Verstehens-Ebene: nur akute Frames werden voll validiert. Beide Filter sind verwandt, leben aber an verschiedenen Stellen der Pipeline.

### 10.4 Entity Resolution (Pattern)

Entity Resolution gleicht *"der Zahnarzt"* mit *"Dr. Müller, Treuchtlingen"* ab. Das ist Slot-Belegung im Personen-Frame über bestehendes Knowledge-Graph-Wissen. Entity Resolution ist eine Mechanik, die der Frame-Auflöser nutzt — kein paralleler Mechanismus. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

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

> **§12 steht nicht in dieser Datei.** Die offenen konzeptionellen Fragen (§12.1) und die Risiken (§12.3) stehen in [`novaberg-thinking-frames_e.md`](novaberg-thinking-frames_e.md), Abschnitt C; die Implementierungs-Reihenfolge (§12.2) steht in [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md).

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
