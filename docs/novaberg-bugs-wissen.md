# Novaberg — Bugs: Wissen — Bibliothek, Dateien, Notizen, Timeline, Fakten

**Inhalt:** die offenen Defekte dieses Gegenstands, ~~21~~ → ~~23~~ → ~~27~~ → ~~28~~ → ~~26~~ → 30 Eintraege (20.10.2026: vier neu aus der Klassifizierung der Fundliste; 17.10.2026: drei neu, `NOTIZ-BEFEHL-ALS-TITEL` ins Archiv; später am selben Tag vier neu aus dem Entwurf der Bauart des Faktengedächtnisses und einer aus der Simulation `simnachher4`; 18.10.2026: `FAKTEN-LESEN-SCHREIBT-LAST-TOUCHED` und `FAKTEN-ABLOESEN-OHNE-TRANSAKTION` ins Archiv), je mit `**Kategorie:** WIS`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 20.10.2026 — aus der Klassifizierung der Funde vom 18. bis 20.10.2026

### `FAKTEN-HEISST-ICH-AUSGENOMMEN` — bei `heisst` lässt die Prüfung der Antwort *ICH* als Subjekt durch
**Kategorie:** WIS

**Rang:** **niedrig** — offen, aber nicht beobachtet: am Modell 9 von 9 Sätzen dieser Form richtig klassifiziert (20.10.2026). Träte es auf, löste es still den Namen des Menschen ab, weil `heisst` einwertig ist. Vergeben am 20.10.2026 gegen HEAD `b52e919`.

**Zustand:** offen — am Code gelesen am 20.10.2026, beim Bau des Fakten-Agenten (Schritt 4).

**Befund** `[Code]`: `server/agents/fakten/klassifikation.py::check_answer` prüft bei `heisst`, dass ein benanntes Subjekt nicht Besitzer ist, und nimmt `ICH` davon aus. Eine Antwort `ICH heisst Rufus` auf *„Mein Hund heißt Rufus“* ginge durch.

**Geschlossen, wenn** eine Antwort, die bei `heisst` den Menschen statt seines Besitzes benennt, abgelehnt wird — bezeugt mit `ICH` als Subjekt.

---

### `FAKTEN-SUCHE-PRIVATE-KLAERUNGSFRAGE` — die Suche des Fakten-Agenten ruft eine private Methode der Auflösung, deren Text immer von zwei Personen spricht
**Kategorie:** WIS

**Rang:** **niedrig** — laut falsch im Text, nicht still: Bei zwei Treffern zu einem Ort oder Tier fragt der Agent nach *„zwei Personen namens …“*. Vergeben am 20.10.2026 gegen HEAD `b52e919`.

**Zustand:** offen — am Code gelesen am 20.10.2026.

**Befund** `[Code]`: `server/agents/fakten/suche.py` ruft `EntityResolutionService._build_klärungsfrage` (Z. 74), eine private Methode eines anderen Bausteins; ihr Text lautet bei zwei Kandidaten immer *„Ich kenne zwei Personen namens …“* (`server/memory/services/entity_resolution.py`, Z. 376).

**Geschlossen, wenn** die Suche keine private Methode der Auflösung ruft und keine Rückfrage die Art der Entität verfälscht.

---

### `FAKTEN-OHNE-EMBEDDING` — die Fakten des Agenten tragen kein Embedding
**Kategorie:** WIS

**Rang:** **niedrig** — still, aber heute ohne Leser: `FaktenRepository.find_similar` hat außerhalb der Tests keinen Aufrufer (gezählt am 20.10.2026). Ein späterer Leser über Ähnlichkeit fände die Fakten des Agenten nicht, und nichts meldete es. Vergeben am 20.10.2026 gegen HEAD `b52e919`.

**Zustand:** offen — am Code gelesen am 20.10.2026.

**Befund** `[Code]`: `server/agents/fakten/crud.py` baut `NewFact` ohne `embedding`; die Spalte `fakten.embedding` und die Lesefunktion `server/memory/repositories/fakten_repository.py::find_similar` (Z. 555) gibt es.

**Geschlossen, wenn** jeder Fakt des Agenten mit Embedding entsteht, oder `find_similar` samt Spalte entfällt — entschieden mit dem ersten Leser über Ähnlichkeit.

---

### `NOTIZ-VERNEINUNG-UEBERLESEN` — bei *neu*, *aktualisieren* und der Wahl einer Notiz wird die Verneinung nicht gelesen
**Kategorie:** WIS

**Rang:** **mittel** — still, und es schreibt gegen die Antwort des Menschen. Vergeben am 20.10.2026 gegen HEAD `b52e919`; die Datei ist seit `2c64856` unverändert.

**Zustand:** offen — gemessen am 18.10.2026 an den Funktionen, aufgerufen ohne Datenbank, gefunden beim Nachzug zu `ZUSTIMMUNG-GILT-ALS-ABLEHNUNG`.

**Befund** `[gemessen 18.10.2026]`: `server/agents/notizen/resume.py::_resume_duplikat` sucht die Wörter für *aktualisieren* und *neu* ohne Blick auf ein *nicht* oder *kein*: *„nein, keine neue“* auf *„Aktualisieren oder neu anlegen?“* legt eine neue Notiz an, *„nicht aktualisieren“* aktualisiert. `_resume_disambiguierung` wählt bei zwei Kandidaten über *erste* und *zweite*: *„nicht die erste, die zweite“* wählt die erste.

**Geschlossen, wenn** an diesen drei Stellen eine verneinte Wahl nicht als diese Wahl gelesen wird, bezeugt mit den drei Sätzen. Mit `KLA-KLAERFALL-AM-OBJEKT` Schritt 5 löst ein geschlossener Leser im Code diese Deutung ab.

---

## 17.10.2026 — aus der Simulation `simnachher4` an einem Prüf-Nutzer

Ein Befund aus einer Simulation an einem frischen Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, Samstag, 17.10.2026, 14:49–18:07 UTC, auf `a26b2cd`; dieselben 24 Sätze wie im Vorlauf `simnachher3`), von Hand gegen den Bestand im Augenblick der Frage bewertet und am Code gehalten gegen HEAD `ae05667`. Die übrigen Befunde des Laufs stehen in [Antwortpfad](novaberg-bugs-antwortpfad.md).

### `TIMELINE-LESEN-SUCHT-MIT-FUELLWORT` — der Timeline-Agent sucht das Ziel einer Lesefrage wörtlich, mit Füllwörtern
**Kategorie:** WIS

**Rang:** **mittel** — still: Der Agent meldet *keine Termine*, obwohl einer im Bestand steht. Bisher berichtigte der Thinker aus seinem Fenster; läge der Termin außerhalb davon, bliebe *kein Termin* stehen (vorhergesagt, nicht gemessen). Vergeben am 17.10.2026 gegen HEAD `ae05667`.

**Zustand:** offen — gemessen am 17.10.2026 in einer Simulation auf `a26b2cd`, am Code gehalten gegen HEAD `ae05667`.

**Befund** `[gemessen]` (Satz 3, die Frage nach dem Termin beim Steuerberater; im Bestand *Steuerberater Hoffmann*, Montag, 19.10.2026, 14:30):

- Die Klassifikation liefert `target='Termin beim Steuerberater'`, normalisiert dagegen *„Termin 'Steuerberater' anzeigen“*.
- Die Suche nimmt das Ziel wörtlich — `agents/timeline/suche.py::raw_matches` gibt `target` als Suchwort an `TimelineRepository.find_by_keyword` — und meldet *„keine Termine zu "Termin beim Steuerberater"“*.
- Der Entwurf folgte dem Agenten, der Thinker berichtigte aus seinem Fenster (vierzehn Tage voraus).
- In `simnachher3` war es genauso: **2 von 2 Läufen.**

**Dieselbe Klasse auf einem anderen Weg:** Ein freier Name wird wörtlich gesucht — wie bei `SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN` (novaberg-bugs-antwortpfad.md), dort im Angebot der Sachlage, hier in der Suche des Timeline-Agenten.

**Wirkung.** Eine Lesefrage nach einem Termin, die der Router dem Agenten zustellt, findet ihn nur, wenn das Ziel ohne Füllwörter im Titel steht. Innerhalb des Fensters des Thinkers wird das berichtigt; ein Termin weiter als vierzehn Tage voraus fehlt auch dort, und die Antwort sagte dann *kein Termin* (vorhergesagt, nicht gemessen).

**Reproduktion.** Einen Termin mit einem Titel wie *Steuerberater Hoffmann* säen und nach dem *„Termin beim Steuerberater“* fragen; im Pipeline-Log das `target` der Klassifikation und die Meldung des Agenten lesen.

**Geschlossen, wenn** eine Lesefrage mit Füllwörtern im Ziel den Termin findet, dessen Titel den Kern des Ziels trägt.

---

## 17.10.2026 — aus dem Entwurf der Bauart des Faktengedächtnisses

Vier Befunde, beim Entwurf der Bauart des Faktengedächtnisses am Code gelesen und gegen HEAD `7b65297` nachgeprüft. Einer wirkt im Betrieb (die Timeline), drei sind latent, weil die Tabelle `fakten` stillgelegt ist (entschieden am 06.10.2026) und keinen Erzeuger hat.

### `TIMELINE-VERWEIS-VERALTET-BEIM-VERSCHIEBEN` — ein Verweis auf einen Termin bleibt beim Verschieben an der alten Zeile
**Kategorie:** WIS

**Rang:** **mittel** — still: Wer dem Verweis folgt, landet auf der inaktiven Zeile mit der alten Zeit; der Weg läuft im Betrieb bei jedem Verschieben. Vergeben am 17.10.2026 gegen HEAD `7b65297`.

**Zustand:** offen — am Code gelesen am 17.10.2026 gegen HEAD `7b65297`. Im Bestand zeigte zu diesem Zeitpunkt noch kein Verweis auf eine inaktive Zeile (unten).

**Befund** `[Code]`: Verschieben heißt in der Timeline invalidieren und neu anlegen (`novaberg-agent-timeline.md` §5.2). `agents/timeline/crud.py::_update` setzt die alte Zeile mit `TimelineRepository.invalidate` auf `aktiv = FALSE` (Z. 336) und legt mit `TimelineRepository.insert` eine neue Zeile mit neuer `id` an (Z. 341). Drei Spalten verweisen per Fremdschlüssel auf `timeline(id)`, je mit `ON DELETE SET NULL` (`agents/timeline/init.sql`): `lzg_knoten.timeline_id`, `sachlage_eigenschaft.timeline_id` und `notizen.timeline_id`. Keine wird beim Verschieben nachgezogen. `memory/sachlage_properties.py::bind_timeline` setzt den Zeitanker einer Eigenschaft nur, solange sie noch keinen hat (`WHERE … timeline_id IS NULL`). Nach dem Verschieben zeigt der Verweis also auf die inaktive Zeile. `ON DELETE SET NULL` greift nie, weil eine Zeile der Timeline nie gelöscht, nur invalidiert wird (§5.3; in `server/` steht außerhalb der Tests kein `DELETE` auf `timeline`).

**Wirkung.** Eine Erinnerung, die an einem Termin hängt, und der Zeitanker einer Eigenschaft der Sachlage verlieren den Termin beim ersten Verschieben. Wer dem Verweis folgt, findet die alte Zeit oder, beim Filter auf `aktiv`, nichts. Jeder künftige Verweis erbt das, auch der geplante vom Fakt auf sein Ereignis (`novaberg-memory-fakten_b.md`, F6).

**Bestand** `[gemessen 17.10.2026, 16:57 UTC]`, nur gezählt: 177 Knoten in `lzg_knoten` und 66 Eigenschaften in `sachlage_eigenschaft` tragen einen Verweis, keiner davon zeigt auf eine inaktive Zeile; in `notizen` trägt keine Zeile einen. Der Defekt sitzt im Code und wird sichtbar, sobald ein Termin verschoben wird, auf den etwas verweist.

**Reproduktion.** Einen Termin anlegen, auf den eine Eigenschaft der Sachlage oder ein Knoten verweist, ihn verschieben und danach `timeline.aktiv` der verwiesenen Zeile lesen.

**Geschlossen, wenn** ein Verweis nach dem Verschieben zur aktiven Zeile führt, für alle drei Spalten. Vorgeschlagen ist eine Spalte `timeline.nachfolger_id`, der ein Leser bis zur aktiven Zeile folgt. ~~Entschieden ist die Bauart nicht;~~ → **Im Grundsatz entschieden am 17.10.2026, nicht gebaut**, als Schemaänderung S5 des Faktengedächtnisses ([`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A, Nr. 20; [`novaberg-memory-fakten_b.md`](novaberg-memory-fakten_b.md) §6); geschlossen ist der Eintrag erst, wenn jeder der drei Verweise der Kette folgt. Eine neue Spalte ist DDL und wird vor ihrem Bau einzeln angekündigt.

### `FAKTEN-UNAUFGELOESTES-OBJEKT-WIRD-WERT` — ein ungeklärtes Objekt wird still ein Wert
**Kategorie:** WIS

**Rang:** **niedrig** — latent im abgeschalteten Plugin: `fakten_verarbeiten` bekommt keinen Auftrag. Vergeben am 17.10.2026 gegen HEAD `7b65297`.

**Zustand:** offen — am Code gelesen am 17.10.2026 gegen HEAD `7b65297`.

**Befund** `[Code]`: Lässt sich in `plugins/fakten_manager/manager.py::fakten_verarbeiten` das Objekt eines Fakts nicht zu einer Entität auflösen, wird sein Name ohne Meldung als Wert gespeichert (Z. 493–495, Kommentar *„Objekt nicht aufgelöst → als Wert behandeln“*). Aus einer Beziehung zwischen zwei Entitäten wird so eine Beziehung zu einer Zeichenkette. Kein Log und kein Ausgang sagt es; ein nicht aufgelöstes Subjekt dagegen wird gemeldet und übersprungen (Z. 481–485). Einziger Aufrufer ist `FaktenManager.execute` (Z. 318, 342). Ihm liefert der Planner keinen Schreibauftrag, denn `FaktenManager` hat kein `plan` und erbt das leere aus `plugins/base.py`.

**Wirkung.** Würde der Weg wieder benutzt, verschwänden Beziehungen zwischen Entitäten still in Wert-Fakten. Eine Mappe, die über Entitäten geht, fände sie in der Objekt-Richtung nicht, und der zweite Grad bräche an ihnen ab.

**Geschlossen, wenn** ein nicht aufgelöstes Objekt zu einer Klärung oder einem lauten Ausgang führt statt zu einem Wert. Der Eintrag entfällt mit dem Umbau des Plugins zum Fakten-Agenten, sobald `fakten_verarbeiten` nicht mehr existiert.

---

## 17.10.2026 — aus den Simulationen an Prüf-Nutzern und den Entscheidungen zur Timeline

### `ZEITRAUM-LIEST-EINEN-TAG` — „im November“ liest einen Tag im November
**Kategorie:** WIS

**Rang:** **mittel** — still, die Antwort sagt *keine Termine*, und der Mensch handelt danach; auf dem Aufgabenpfad, also nur wenn der Router eine Lesefrage dem Timeline-Agenten zustellt. Vergeben am 17.10.2026 gegen HEAD `914217c`.

**Zustand:** **gebaut am 17.10.2026** (getestet, ~~noch nicht committet~~ → committet als `c0eecbb`); **offen bis zur Messung** an einem frischen Prüf-Nutzer mit derselben Frage und einer Frage nach dem Wochenende.

**Befund** `[gemessen 17.10.2026]`, Simulation an einem Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher3/`): Auf die Frage, ob im November schon Termine stehen, stellte der Router dem Timeline-Agenten zu. Der meldete, für *„im November“* keine Termine gefunden zu haben, und die Antwort sagte, im November sei nichts eingetragen. Im Bestand stand ein Termin am 06.11.2026. In den beiden Simulationen davor lief derselbe Satz ohne den Agenten — über den Block `[TERMINE]` — und war richtig.

**Mechanismus, am Code gelesen:** `agents/timeline/suche.py::suchen` machte aus dem Zeitausdruck ein Fenster von **einem Tag**; nur die Wörter *woche* und *monat* im Text weiteten es. *„im November“* ergab einen Tag im November, *„am Wochenende“* Montag bis Sonntag.

**Gebaut:** Ein genannter Zeitraum ist ein Fenster über den ganzen Zeitraum — Monat und Monatsname, Woche, Wochenende als Samstag und Sonntag, Abstände —, dekodiert an einer Stelle (`utils/zeitparser.py::named_period`); ein einzelner Tag bleibt ein Tag. Ein Monatsname ohne Präfix ist der des laufenden Jahres. Der Leseast liest über `read_appointments`, ohne Anker, in den Zeilen von `appointment_line`. Zeugen: `tests/test_timeline_agent_reading.py` (48), darunter die Frage nach dem November mit einem Termin am 06.11. — vor dem Bau rot. Bauart: `novaberg-agent-timeline.md` §4.2, `novaberg-tool-timeparser.md` §10.7.

**Nachtrag, 17.10.2026 — Simulation `simnachher4`:** An einem frischen Prüf-Nutzer, mit dem Bau im Dienst (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, auf `a26b2cd`), ist der Wortlaut der Schließbedingung erfüllt: Die Antwort auf die Frage nach dem November nannte den Elternabend am Samstag, 07.11.2026, und die Frage nach dem Wochenende (am Samstag, 17.10.2026) las Samstag und Sonntag. **Beide Fragen liefen aber am Agenten vorbei, also nicht auf dem Weg des Defekts:** Der Router stellte nicht zu, gelesen hat der Leseweg im Turn — für den November `range` 01.11.–30.11., für das Wochenende `range` vom 17.10. bis zum 18.10., 23:59. Am Agenten lief nur *nächste Woche*, als ganze Kalenderwoche gelesen, und *morgen* blieb ein Tag. Die November-Antwort trug zudem einen falschen Korrektursatz (`PRUEFER-OHNE-LESESTAND`, novaberg-bugs-antwortpfad.md). **Der Eintrag bleibt offen, bis der Router dem Agenten eine Monatsfrage zustellt.**

**Reproduktion.** Eine Lesefrage nach einem Monat, die der Router dem Timeline-Agenten zustellt, mit einem Termin im Monat, der nicht auf dem gelesenen Tag liegt.

**Geschlossen, wenn** dieselbe Frage an einem frischen Prüf-Nutzer den Termin im Monat nennt und eine Frage nach dem Wochenende Samstag und Sonntag liest.

### `VERSCHIEBEN-NACKTE-STUNDE-OHNE-TAGESHAELFTE` — „auf 4 Uhr“ schreibt still 04:00
**Kategorie:** WIS

**Rang:** **hoch** — still: eine geratene Zeit steht im Kalender, und der Mensch verlässt sich darauf. Vergeben am 17.10.2026 gegen HEAD `914217c`.

**Zustand:** offen — **entschieden am 17.10.2026, nicht gebaut.**

**Befund** `[Code]`, beschrieben in `novaberg-agent-timeline.md` §5.2, *Grenzen des Endstands*: Beim Verschieben wird eine nackte Stunde wörtlich gelesen, ohne Tageshälfte. *„Verschieb den Nachmittagskaffee auf 4 Uhr“* bei einem Termin um 15:30 schreibt 04:00 — Lesung und Positivform sind sich einig, also wird geschrieben (Beispiel synthetisch).

**Warum es ein Defekt ist:** Entschieden am 17.10.2026: Eine Stunde von 1 bis 12 ohne Tageszeit führt beim Verschieben zur Rückfrage (*„4 Uhr morgens oder nachmittags?“*), außer der Satz nennt die Tageszeit selbst (*„um 4 Uhr nachmittags“*). Bis dahin war es eine offene Deutungsfrage (Backlog `ZEIT-ZWOELF-STUNDEN-DEUTUNG`); seit sie entschieden ist, weicht der Code davon ab.

**Reproduktion.** Einen Termin am Nachmittag mit *„auf 4 Uhr“* verschieben.

**Geschlossen, wenn** *„auf 4 Uhr“* zur Rückfrage führt, *„auf 4 Uhr nachmittags“* auf 16:00 verschiebt und *„auf 16 Uhr“* ohne Rückfrage schreibt.

### `TIMELINE-TITEL-MEHRERE-TREFFER-OHNE-TAG` — gleichnamige Termine lassen sich nicht einzeln ändern
**Kategorie:** WIS

**Rang:** **mittel** — laut und sicher: Es wird nie am falschen Termin geschrieben, aber ein Auftrag bleibt unausgeführt, und die Klärung sagt das. Vergeben am 17.10.2026 gegen den Stand des Umbaus der Timeline (noch nicht committet).

**Zustand:** offen — bekannt seit dem Bau vom 17.10.2026; ein erwarteter Fehlschlag trägt die Kennung (`tests/test_timeline_agent_reading.py::test_a_new_order_with_title_and_date_moves_that_one`).

**Befund** `[Code]`: Der Weg mit Titel grenzt mehrere gleichnamige Treffer nicht nach dem Tag des Termins ein. Stehen zwei Zahnarzttermine im Bestand, trifft *„Verschieb den Zahnarzt am 9. auf 11 Uhr“* beide — beim Verschieben ist der Zeitausdruck die neue Zeit, nicht der Tag des Termins. Gibt es keinen einzigen kommenden unter ihnen, kommt die Auswahl, und keine Antwort auf sie schreibt (`novaberg-agent-timeline.md` §4.5). Gleichnamige Termine ohne einen einzigen kommenden lassen sich damit über den Agenten weder einzeln ändern noch löschen noch verschieben (Beispiel synthetisch).

**Warum es so steht:** Eine Wahl aus einer freien Antwort traf auf diesem Weg den ersten Kandidaten gleichen Titels und schrieb still am falschen Termin; deshalb schreibt keine Antwort mehr. Das Eingrenzen nach dem Tag kommt mit der Auswahl der Klärfälle — als feste, nummerierte Liste, entschieden am 17.10.2026 (`KLA-KLAERFALL-AM-OBJEKT`, ~~Schritt 3~~ → Schritt 2 der Bauart, angenommen am selben Abend).

**Reproduktion.** Zwei gleichnamige Termine, beide vergangen oder beide kommend, und ein Auftrag mit Titel und dem Tag eines von ihnen.

**Geschlossen, wenn** der erwartete Fehlschlag grün wird — *„Verschieb den Zahnarzt am 9. auf 11 Uhr“* verschiebt bei zwei Zahnarztterminen genau den am 9. — und eine Auswahl mit Titel zu einer Wahl führt, die den gewählten Termin schreibt.

---

## Einzelbefunde ohne eigenen Datumsabschnitt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

*Die Einträge dieses Abschnitts standen bis zum 19.09.2026 ohne eigene Überschrift unter dem Abschnitt vom 25.08.2026, zu dem nur der erste Eintrag davor gehört. Ihre Befunddaten reichen vom 05.08. bis zum 18.09.2026.*

### `SETEXT-UNTERSCHRIFT-IM-BLOCK` — die Unterstreichung steht im Inhalt
**Kategorie:** WIS

**Rang:** **niedrig** — still, Markdown betrifft keine Datei, RST jede Überschrift. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/tools/dateien/operationen.py:587`); die Reparatur ändert einen Vertrag mit fünf Aufrufern.

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `block_lesen` liest weiter ab `start` der Ueberschriftenzeile (`tools/dateien/operationen.py:587`).

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Bei einer Setext-Überschrift steht ihre Unterstreichung in der ersten Zeile des Blockinhalts.** `struktur_analysieren` setzt `start` auf die Textzeile der Überschrift, und `block_lesen` liefert ab `start + 1` — bei einer Rautenüberschrift ist das die erste Inhaltszeile, bei einer Setext-Überschrift die Reihe aus `=` oder `-`. Gefunden von der zweiten Kontrolle am 20.08.2026, indem die neue Karte durch ihren nachgelagerten Verbraucher geschickt wurde: `block_lesen(...)` auf einen Setext-Block gibt `'===================\n\nInhalt…'` zurück. **Der Parser weiß es besser, als der Vertrag hergibt:** `token.map` hält den Bereich der *ganzen* Überschrift, bei Setext also zwei Zeilen; das Erkenner-Tupel trägt nur den Anfang. **Nicht behoben, weil die Reparatur einen Vertrag mit fünf Aufrufern ändert.** **Nachtrag vom selben Tag, ~13:55 UTC: Der Fall ist nicht mehr latent.** Mit dem reStructuredText-Erkenner ist die Unterstreichung nicht der Sonderfall, sondern **die Regel** — in RST trägt *jede* Überschrift eine, und `block_lesen` liefert sie bei jeder als erste Inhaltszeile mit. In Markdown betrifft es weiterhin keine der 174 Dateien; sobald eine `.rst`-Datei indiziert wird, betrifft es sie vollständig.

**Geschlossen, wenn** `block_lesen` liefert bei jeder Ueberschriftform die erste Inhaltszeile — der Vertrag traegt das Ende der Ueberschrift, nicht ihren Anfang.

---

### `BIBLIOTHEK-FINDET-SICH-SELBST` — Kosinus 1,000 in 44 von 46 Trefferzeilen
**Kategorie:** WIS

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `Bibliotheksfrage` hat kein Ausschlussfeld (`server/memory/repositories/autonomous_wissen_repository.py:160-190`), ausgeschlossen wird nur im Rückweg (`7d22db1`).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. der Lesepfad schliesst die eigene Ausarbeitung nicht aus; die Trefferzahl braucht einen Messlauf.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **44 von 46 Bibliotheks-Trefferzeilen melden Kosinus exakt 1,000: Der Eintrag findet sich selbst.** Ein Kosinus von 1 heißt, der Suchschlüssel **ist** der gespeicherte Vektor. **Geprüft und ausgeschlossen:** die Spaltenabbildung im Repository (acht Spalten auf acht Felder, `cosine` ist das echte `MAX(1 - …)`), eine doppelte Registrierung des Managers (genau einer in der Registry), und ein doppelter Aufruf je Turn — **ein Nutzerturn erzeugt gemessen genau einen Aufruf**. **Eingegrenzt:** In **42 von 44** Fällen steht unmittelbar davor der Zettel-Dienst (`agents/wissen`); es sind Hintergrundläufe, deren Suchtext ein gespeichertes Thema ist. Die beiden echten Meldungen haben diese Nachbarschaft nicht. **Offen bleibt, ob das schadet:** Ein Vertiefungslauf, der seine eigene Ausarbeitung als Kontext zurückbekommt, ist die Selbstbestätigung, gegen die an anderer Stelle schon `bezug_id` gebaut wurde. **Warum es zählt:** Solange sie mitzählen, ist jede Aussage über die Trefferrate der Bibliothek um den Faktor 23 falsch.

**Geschlossen, wenn** Ein Lauf, der seine eigene Ausarbeitung als Kontext bekaeme, wird ausgeschlossen; die Trefferrate der Bibliothek zaehlt nur Fremdtreffer.

---

### `ZUORDNUNG-NENNT-LISTENPOSITION` — Listenposition statt Datenbank-Nummer
**Kategorie:** WIS

**Rang:** **mittel** — laut, aber der Auftrag geht verloren. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; eine fremde Nummer wird verworfen (`server/agents/wissen_rueckweg/zuordnung.py:240-246`), ohne zweiten Versuch (`agent.py:243-248`).

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert: `agents/wissen_rueckweg/zuordnung.py:240-244` verwirft mit `return None`, ohne zweiten Versuch und ohne Rueckstellung. Der Riegel selbst ist intakt — drei Rueckgabepfade melden je einen eigenen Grund (Nummer nicht in der Vorlage · `ziel` keine Nummer · `kern` leer) —, aber alle drei enden gleich, und keiner ist von *„keine Datei passt"* zu unterscheiden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Das Zuordnungsmodell nennt eine Listenposition statt der Datenbank-Nummer, und der Riegel verwirft zu Recht — aber der Auftrag ist danach weg.** Im Betriebslog: *„Rueckweg-Zuordnung: Nummer 3 steht nicht in der Vorlage [587, 2022, 3058, 5592, 6869, 6871, 7972, 8817] — verworfen"*, danach `keine_zuordnung (Aufruf unbrauchbar)`. Der Zeuge dafuer steht seit dem 18.08. und hat gehalten; **gemessen ist damit erstmals, dass der Fall im Betrieb wirklich vorkommt** — 1 von 4 echten Laeufen. Offen ist nicht der Riegel, sondern die **Behandlung danach**: Ein unbrauchbarer Modellaufruf ist von *„keine Datei passt"* nicht zu unterscheiden, obwohl das eine ein Ausfall und das andere ein Ergebnis ist. Ein zweiter Versuch waere billiger als der verlorene Auftrag.

**Geschlossen, wenn** Der Riegel verwirft weiterhin, aber der Auftrag geht nicht verloren — er wird zurueckgestellt oder mit der richtigen Nummer erneut gestellt.

---

### `ERSCHLIESSUNG-VERSTUEMMELT-STICHWORT` — der scharfe Kanal haengt an verstuemmelten Woertern
**Kategorie:** WIS

**Rang:** **mittel** — still, die Datei fällt aus dem lexikalischen Kanal. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; Stichwörter werden nur gestrippt (`server/agents/dateien_index/indizieren.py:272-282`).

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. keine Pruefung der erhobenen Stichwoerter im Indexweg.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Das Erschließungsmodell verstümmelt Stichwörter, und der scharfe Kanal hängt daran.** Beim Indizieren von `kzg-salienz.md` erhob das Modell unter anderem `DAEMPFUNGSEEXPONENT` (doppeltes E) und `Figureseite` statt *Dämpfungsexponent* und *Figurenseite*. **Gemessen:** Die Frage nach dem Dämpfungsexponenten fiel deshalb aus dem lexikalischen Kanal und wurde nur vom dense Kanal getragen (0,4904). Der Ausfall war folgenlos, **weil es zwei Kanäle gibt** — mit einem allein wäre er ein stiller Treffer weniger gewesen. **Die Klasse ist größer als der Fall:** Der scharfe Kanal setzt voraus, dass die erhobenen Stichwörter die Schreibweise treffen, in der ein Mensch fragt; niemand prüft das heute. Ungezählt ist, wie viele der Stichwörter im Bestand solche Fehler tragen.

**Geschlossen, wenn** Die Stichwoerter des Erschliessungsmodells sind vollstaendig, oder der scharfe Kanal haengt nicht mehr an ihnen.

---

### `FUNDSTELLE-MIT-BEHAELTERPFAD` — der absolute Pfad steht im Prompt
**Kategorie:** WIS

**Rang:** **niedrig** — still, der volle Pfad der Wurzel erscheint als Ort. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt (`server/agents/dateien_index/aufzeichnungen.py:120`). Vorgehen entscheidbar ohne neue Absicht; Empfehlung: Rückfall auf den Basisnamen der Wurzel.

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. `_fundstelle_bauen` fällt weiter auf den vollen Wurzelpfad zurück (`ort = bezeichnung.strip() or wurzel.strip()`, `aufzeichnungen.py:120`). **Die Zahl, die den Befund billig machte, gilt nicht mehr:** Es ist nicht mehr eine Wurzel, es sind **drei**, und die dritte hat die offene Frage von damals bereits in eine Richtung beantwortet.

```
id | pfad                               | bezeichnung
 1 | /files                             | <LEER>            -> Behaelterpfad im Prompt
 2 | /docs                              | <LEER>            -> Behaelterpfad im Prompt
 3 | /knowledge/autonomous/nova/meister | meine Recherchen  -> traegt eine Bezeichnung
```

> **Der Weg ist damit begehbar, aber nicht gebahnt.** Wurzel 3 zeigt, dass eine Bezeichnung vergeben werden *kann*; das Tor der Freigabe verlangt sie weiterhin nicht, und der Rückfall nimmt weiterhin den vollen Pfad statt des Basisnamens. Zwei von drei Wurzeln reichen heute ein Umgebungsdetail an das Modell durch — 2026 war es eine von einer.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Die Fundstelle im Prompt trägt den absoluten Behälterpfad, weil die einzige Freigabe keine Bezeichnung hat.** Der `[AUFZEICHNUNGEN]`-Block nennt je Eintrag `<Ort>/<Pfad>`; als Ort steht die `bezeichnung` der Wurzel und, wenn sie fehlt, deren `pfad`. **Gemessen am laufenden Bestand:** `SELECT id, pfad, bezeichnung FROM dateien_wurzeln` → eine Zeile, `/files`, **Bezeichnung leer** — im Messturn stand deshalb `/files/novaberg-papers.md` im Prompt. Das ist der vorgesehene Rückfall und kein Defekt, aber es steht quer zu der Begründung, mit der die Indexzeile ihren Pfad **relativ** führt (`novaberg-agent-dateien_k.md` §4: *„absolut wäre ein Umgebungsdetail und nicht verschiebbar"*) — genau dieses Umgebungsdetail erreicht jetzt das Modell. **Zwei Auswege, und die Wahl ist eine Absicht:** Das Tor der Freigabe verlangt eine Bezeichnung, oder der Rückfall nimmt den Basisnamen der Wurzel statt ihres vollen Pfades. Heute nur eine Wurzel, also billig zu ändern — bei zehn nicht mehr.

**Geschlossen, wenn** Die Freigabe traegt eine Bezeichnung, und die Fundstelle nennt sie statt des Behaelterpfads.

---

### `FAKTENPLUGIN-OHNE-KAPPUNG` — weder Kappung noch Schwelle
**Kategorie:** WIS

**Rang:** **niedrig** — heute ohne Wirkung, das Plugin ist abgeschaltet (`server/graph/nodes/enricher.py:1074`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt bei Reaktivierung (`server/plugins/fakten_manager/manager.py:163-175`, Abfragen ohne LIMIT).

**Zustand:** offen — gegen HEAD `9bcd214` gemessen am 24.08.2026. Unveraendert und im Kontextpfad nachgesehen: `enrich_entries` (`plugins/fakten_manager/manager.py:130`) laeuft ueber `EntitaetenRepository.find_by_user` und je Entitaet ueber `FaktenRepository.find_by_subjekt` — **kein `LIMIT`, keine Schwelle, kein Aehnlichkeitsvergleich** an einer der beiden Stellen. Die Menge ist weiterhin allein durch den Bestand begrenzt.

**Befund (18.08.2026), aus der Fundliste uebernommen.** **Der Fakten-Plugin hat weder Kappung noch Schwelle — das ist der Grund für seine 130+ Einträge, nicht die Datenqualität.** `enricher.py` schaltet ihn seit Chat 71 ab mit dem Vermerk *„Fakten-Enrichment produziert 130+ Rausch-Eintraege — wird reaktiviert nach Fakten-Bereinigung"*. Gezählt über die sieben Kontextquellen: `wissen_manager`, `notizen_manager` und `timeline_manager` tragen ein `LIMIT`, **`fakten_manager` trägt keins** — und auch keinen Ähnlichkeitsvergleich. Die Diagnose lautete *Bereinigung*, aber eine Quelle ohne Obergrenze liefert unabhängig von der Datenqualität so viele Einträge, wie der Bestand hergibt. **Die Abhilfe ist eine Zeile und wurde nie versucht**; solange sie fehlt, ist die Wiederinbetriebnahme an eine Bedingung geknüpft, die nicht die wirksame ist. Aufgefallen beim Entwurf des Dateien-Plugins, das dieselbe Stelle besetzt und dieselbe Falle hätte.

**Geschlossen, wenn** Das Fakten-Plugin kappt und schwellt wie die uebrigen Quellen.

---

### `TIMELINE-SCHREIBT-OHNE-AUFTRAG` — die beilaeufige Erwaehnung legt an, der Auftrag scheitert
**Kategorie:** WIS

**Rang:** **niedrig** — die schwerere Hälfte ist erfüllt (`c6c0e98`, 14.09.2026: nur ein ausdrücklicher Auftrag schreibt). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: offen nur, ob ein Auftrag mit Wochentagsnamen schreibt; ungemessen.

**Zustand:** offen — gefunden am 01.09.2026 gegen HEAD `79aaaa6`, aus der Fundliste uebernommen. **Ein Eintrag dieser Klasse ist am 16.09.2026 aus dem Bestand genommen:** Zeile 507 der Timeline, am 13.09.2026 aus einer Aussage statt aus einem Auftrag angelegt, steht auf `aktiv = false` (Entscheidung des Eigentuemers, kein Fremdschluessel zeigte darauf). **Der Defekt selbst bleibt offen** — der schreibende Weg ist unveraendert.

**Befund.** Eine beilaeufige Erwaehnung eines Vorhabens mit dem Wort *morgen* erzeugte einen Timeline-Eintrag (`status=abgeschlossen`); der **ausdrueckliche Eintragungsauftrag** sieben Minuten spaeter, mit zwei Wochentagsnamen statt eines relativen Tages, scheiterte (`status=fehler`, *„Konnte kein Datum erkennen"*). Dazwischen sagte die Antwort, es sei nichts eingetragen worden — waehrend der Eintrag seit sieben Minuten stand.

**Zwei Ursachen, und nur die zweite ist die Datumserkennung.** Die Erkennung nimmt relative Tage und keine Wochentagsnamen (`agents/timeline/crud.py:122`). Dass eine Erwaehnung ohne Auftragscharakter ueberhaupt schreibt, ist die erste und die schwerere: Der Nutzer bekommt Eintraege, um die er nicht gebeten hat, und keinen fuer den, um den er bat.

**Der angelegte Eintrag war zudem unvollstaendig** — weder der Ort aus der Aeusserung noch ein `event_ende`; der zweite Tag fehlte, der Titel bestand aus dem Vorgangswort allein.

**Geschlossen, wenn** ein Auftrag mit Wochentagsnamen schreibt und eine Erwaehnung ohne Auftragscharakter nicht.

**Stand 14.09.2026 — die erste Haelfte ist erfuellt, die zweite ungemessen.** Entscheidung des Eigentuemers am 13.09.2026: *„Nur ein ausdruecklicher Auftrag"*. Aushang, Negativfall und Vorpruefung der Klassifikation verlangen seither einen Auftrag (`novaberg-agent-timeline.md` §3a). `[gemessen 14.09.2026, gemma4-a4b-gpu]` **Aussagen mit Zeitpunkt schreiben 0 von 21**, Auftraege 12 von 12 bis zur Klassifikation — darunter *„Erinnere mich am Donnerstag um 15 Uhr …"* als `create`. **Ob der Wochentagsname danach auch geparst und geschrieben wird, lief nicht** (die Messung endete vor der Ausfuehrung). Bleibt offen, bis ein Auftrag mit Wochentagsnamen im Betrieb einen Eintrag erzeugt.

---

### `TIMELINE-NENNT-ABGELAUFENEN-TERMIN-ALS-KOMMENDEN` — dreizehn Tage alt, als morgig ausgegeben
**Kategorie:** WIS

**Rang:** **hoch** — still, eine falsche Zeitangabe wird geglaubt. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: keine Prüfung der Antwort gegen `event_time`; `server/utils/datum_pruefung.py` prüft nur Wochentag gegen Datum. Ungemessen.

**Zustand:** **im Code behoben am 15.10.2026; Messung im Betrieb ausstehend.** ~~offen — gefunden am 01.09.2026 gegen HEAD `79aaaa6`, aus der Fundliste uebernommen.~~

**Gebaut am 15.10.2026 — Fassung c der Entscheidung unten, an der Stelle, an der ein Termin in den Prompt der Antwort kommt** (getestet, im Betrieb nicht gemessen):

- **Der Bezug zu heute ist vorgerechnet.** Der Block `[TERMINE]` des Verfassers trägt je Termin Wochentag, Datum und Uhrzeit in Ortszeit und in Klammern den Bezug zu heute — *heute*, *morgen*, *in 3 Tagen*, *vor 9 Tagen* —, gerechnet nach Kalendertagen in Ortszeit (`graph/format/appointments.py::relative_day`). Der Prompt sagt, dass der Inhalt ihn übernimmt, statt selbst zu rechnen.
- **Abgelaufen heißt gekennzeichnet oder weggelassen.** Ein Termin vor jetzt (mit Uhrzeit) oder vor heute (ohne Uhrzeit) steht als *„vergangen, vor N Tagen“* da; bei `direction: forward` fehlt er, und die Kopfzeile sagt *„nur kommende Termine“*. `direction` gilt jetzt auch für einen Zeitraum (`range`), nicht nur für die Titelsuche; der Router-Prompt setzt `forward` auch bei Fragen nach Kommendem (*„was steht an“*, *„was habe ich noch“*, *„diese Woche noch“*).
- **Eine Titelsuche grenzt *vergangen* in der Abfrage so ab wie der Leser**, mit der Uhr des Turns statt `NOW()` der Datenbank — kein Platz der Obergrenze geht an einen Termin, der danach wegfällt (`memory/repositories/timeline_repository.py::find_by_keyword`, Schlüsselwörter `now` und `timed_precisions`).
- Zeugen in `tests/test_timeline_reading.py` (`DirectionTest`, `RelationToTodayTest`, `SearchBoundaryTest` — über das Monatsende und kurz nach Mitternacht Ortszeit) und `tests/test_timeline_anchor_exclusion.py`.

**Nicht gebaut:** eine Prüfung hinter der Antwort, die ein genanntes Datum gegen `event_time` hält. Die Lesezeilen des Timeline-Agenten (`agents/timeline/suche.py`) ~~tragen weiter keinen Bezug zu heute~~ → **tragen seit dem 17.10.2026 den Bezug zu heute** (gebaut und getestet, noch nicht committet): Der Leseast liest über `read_appointments` und schreibt die Zeilen von `appointment_line`, dieselben wie der Block `[TERMINE]` — und auf dem Aufgabenpfad sind sie das, was die Antwort bekommt. **Geschlossen wird erst nach der Messung** — die Schließbedingung unten fragt nach der Auskunft, nicht nach dem Prompt.

**Nachgezogen am 17.10.2026, abends — auch das Angebot der Sachlage** (gebaut und getestet, ~~im Betrieb nicht gemessen~~ → im Betrieb gemessen am selben Abend: Der Leseweg kennzeichnet den vergangenen Termin, das Angebot blieb aber leer, weil die Objektnamen ihn nicht treffen — `SACHLAGE-KALENDER-VERFEHLT-OBJEKTNAMEN`, `novaberg-thinking-lage_m.md` Scheibe 13; für diesen Eintrag kein Beleg in die eine oder andere Richtung). Ein weiterer Weg, auf dem ein Termin die Antwort erreicht, war das Angebot des Frame-Auflösers: Er las Kalenderzeilen selbst, über `find_by_keyword` ohne die Uhr des Turns, und bot sie als *Kalender TT.MM.JJJJ: Titel* an — ohne *vergangen* und ohne Bezug zu heute; aus diesem Angebot deckt der Auflöser offene Eigenschaften, und eine Deckung steht dem Verfasser im `[SACHLAGE]`-Block. Jetzt liest er über `read_appointments` mit der Uhr des Turns, und die Angebotszeile ist die von `appointment_line`: ein abgelaufener Termin trägt *(vergangen, vor N Tagen)* (`graph/nodes/sachlage_resolver.py::_offer_line`; Zeugen `tests/test_sachlage_calendar_reading.py`, `PastBoundaryTest`; `novaberg-thinking-lage_b.md` §4 Scheibe 6). Die Schließbedingung bleibt dieselbe.

**Nachtrag, 17.10.2026 — Simulation `simnachher4`:** Ein Datenpunkt für die Schließbedingung, an einem frischen Prüf-Nutzer (`labor/2026-10-15_sim_timeline_notizen/simnachher4/`, auf `a26b2cd`): Der Zahnarzt (Sonntag, 18.10.2026) hieß in **6 von 6** Antworten richtig *morgen* (Satz 2, 10, 17, 18, 19 und 21) — mehrere Auskünfte über denselben Eintrag im selben Gespräch trugen dieselbe Relativangabe. Kein abgelaufener Termin wurde als kommender genannt. Gemessen ist ein Lauf; der Eintrag bleibt offen. In der Sache nahe steht `PRUEFER-OHNE-LESESTAND` (novaberg-bugs-antwortpfad.md): Dort verdirbt ein Prüfer hinter dem Verfasser ein richtig gelesenes Datum.

**Gegenpunkt aus `simnachher3`** (`labor/2026-10-15_sim_timeline_notizen/simnachher3/`, Satz 18, *„Was ist morgen bei mir los?“*): Dort nannte die Antwort denselben, noch bevorstehenden Zahnarzt *„heute hattest du bereits“* — die umgekehrte Richtung (Kommendes als vergangen), derselbe falsche Bezug zu heute. Für die Schließbedingung zählt der Fall nicht, er gehört aber zur Klasse.

**Diagnose am Code, 15.10.2026 — die Ursache ist kein einzelner Fehler, sondern das Fehlen jeder Zeitbeziehung entlang des Weges.** Die Lesewege der Timeline (Suche, Zeitraum, Repository) liefern abgelaufene, noch aktive Termine ohne Kennzeichen *vergangen*; die Prompts der Antwort tragen den Termin als absolutes Datum ohne Bezug zu heute; keine Prüfung hinter der Antwort hält ein genanntes Datum gegen `event_time`. Nur der proaktive Zweig des Timeline-Managers setzt den Bezug — mit einem Fenster ab heute minus drei Tagen, das einen dreizehn Tage alten Termin nicht aufnimmt. Welcher Weg im ursprünglichen Fall lief, ist ungemessen. ~~**Vor dem Bau steht eine Absichtsfrage beim Eigentümer:**~~ → entschieden am 15.10.2026 (unten): ob ein abgelaufener Termin bei einer Frage nach kommenden weggelassen, sonst als *vergangen* gekennzeichnet und mit vorgerechnetem Bezug zu heute gegeben wird (beides zusammen erfüllt die Schließbedingung unten).

**Entschieden am 15.10.2026, vor dem Bau** — aus der Schliessbedingung, keine offene Absicht: Bei einer Frage nach **kommenden** Terminen fehlen abgelaufene ganz; sonst (*„wann war …“*, Suche ohne Richtung, `direction: backward`) stehen sie als *vergangen* gekennzeichnet und mit vorgerechnetem Bezug zu heute (*„vor 13 Tagen“*) im Kontext. Weglassen allein naehme dem Rueckblick die Grundlage; kennzeichnen allein liesse den abgelaufenen Termin in einer Auskunft ueber kommende stehen.

**Befund.** Die Antwort nannte in drei aufeinanderfolgenden Turns einen bestehenden Termin fuer den Folgetag, zweimal mit einer Uhrzeit und einmal als *fixiert*. In `timeline` gibt es genau einen Eintrag dieses Titels — **dreizehn Tage alt und abgelaufen**. Fuer den genannten Tag standen zwei andere Zeilen. Derselbe Lauf gab fuer einen zweiten Vorgang ein Datum an, das **sechzehn Tage** neben dem Eintrag lag, der tatsaechlich in der Tabelle steht.

**Verwandt mit `TIMELINE-LESEPFAD-INSTABIL`, aber nicht dasselbe:** Dort bleibt eine Zustellung aus und die Auskunft hat keine Grundlage. Hier **liegt** eine Grundlage vor, und die Antwort liest sie falsch — ein abgelaufener Termin wird ohne Datumspruefung als kommender ausgegeben.

**Warum es teuer ist:** Eine falsche Bestaetigung wird geglaubt. Derselbe Satz steht bei `RESPONDER-ERFINDET-DATUM` im Archiv.

**Zweiter Fall, gemeldet vom Eigentuemer am 10.09.2026** — und er zeigt die Klasse von einer anderen Seite: **Derselbe Termin wurde in einem Gespraech zuerst als *heute um 13 Uhr* und unmittelbar danach als *morgen* ausgegeben.** Nicht ein falsches Datum gegen die Tabelle, sondern **zwei Relativangaben, die einander widersprechen** — die Auskunft rechnet die gespeicherte `event_time` offenbar nicht gegen den laufenden Tag, sondern formuliert frei.

> **Ein Widerspruch innerhalb eines Gespraechs ist die billigste Pruefform, die es gibt** — er braucht keine Tabelle, nur zwei Saetze nebeneinander. Dass er auffiel, ist dem Menschen zu verdanken und keiner Pruefung.

**Herkunft dieses Datenpunktes: eine Beobachtung, keine Messung.** Turn-Kennung und Zeitpunkt sind nicht erhoben, der Wortlaut stammt aus der Schilderung. Wer ihn nachmisst, sucht nach zwei Auskuenften desselben Termins in einem Gespraech mit verschiedenen Relativangaben.

**Geschlossen, wenn** eine Auskunft ueber kommende Termine keine Zeile nennt, deren `event_time` in der Vergangenheit liegt — **und zwei Auskuenfte ueber denselben Eintrag im selben Gespraech dieselbe Relativangabe tragen.**

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 133 — aus der Fundliste klassifiziert, Block 30.–27.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Siebzehn Defekte, der aelteste Bestand der Liste. **Sechs von ihnen sind derselbe Bauplan:** ein Vorgabewert an einer Stelle, an der ein Ausfall gehoert — beim Queue-Push, beim Dispatch, am Spalten-Default des Rades, bei zwei Kanon-Feldern, in der fehlenden Klemme und beim Suchdienst, dessen Ausfall wie ein leeres Ergebnis aussieht.

#### UNBEKANNTE-AKTION-FAELLT-DURCH 🔧 offen
**Kategorie:** WIS

**Rang:** **niedrig** — still, als Verhalten gepinnt (`server/tests/test_notizen_execute.py:191`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt an beiden Stellen (`server/plugins/notizen_manager/manager.py:493-522`).

**Zustand:** offen, **zur Haelfte erledigt** — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Die unbekannte Aktion faellt nicht mehr stillschweigend durch: `execute()` gibt `erfolg=False` mit dem Text *„Unbekannte Aktion: …"* zurueck. **Laut ist sie damit noch nicht** — es entsteht keine Logzeile, und *„Eine unbekannte Aktion scheitert laut"* ist genau das, was fertig waere. Die zweite Haelfte des Befundes — `verarbeitet` bedeutet je Pfad etwas anderes — ist nicht nachgeprueft.

**Befund (2026-07-30).** `plugins/notizen_manager/manager.py` `execute()`: Eine **unbekannte Aktion** faellt stillschweigend durch — keine Zaehlung, keine Log-Zeile. Der stille Uebersprung, den der Standard verbietet. Zusaetzlich zaehlt der alte Update-Pfad **unbedingt**, der M6-Pfad nur bei gemeldetem Erfolg: `verarbeitet` bedeutet je Pfad etwas anderes. Beides mit `assertNoLogs` bzw. einem Vergleichstest gepinnt.

**Was fertig waere.** Eine unbekannte Aktion scheitert laut.

**Prioritaet:** mittel.

### Chat 133 — aus der Fundliste klassifiziert, Block 31.07. (08.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Antwortpfad](novaberg-bugs-antwortpfad.md), [Bauart](novaberg-bugs-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Acht Defekte. **Vier davon sind Prompt-Bloecke, die etwas ueber den Nutzer behaupten, was Novas Zustand ist** — dieselbe Verwechslung an vier Stellen, jede fuer sich unauffaellig.

#### ZEIT-EXTRAKTION-UNSCHARF 🔧 offen
**Kategorie:** WIS

**Rang:** **niedrig** — still, der Parser verwirft nachgelagert. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `zeitausdruck_roh` geht ungeprüft weiter (`server/graph/nodes/salience.py:710-711`).

**Befund (2026-07-31).** **Die Zeit-Extraktion ist über den Richtungsverlust hinaus unscharf.** Im Gespräch, aus dem `ZEIT-RUECKWAERTS-WIRD-ZUKUNFT` stammt, trug `zeitausdruck_roh` auch `'trockenen Sommer'` und `'Tageslicht'` — Zeichenketten, die keine Zeitangaben sind. Die Anweisung schließt allgemeine Bemerkungen ohne konkreten Anker zwar aus, nennt aber nur drei Beispiele dafür. Nicht nachgemessen nach der Prompt-Änderung vom 31.07.

**Was fertig waere.** Was als Zeitausdruck geliefert wird, ist einer — oder das Feld traegt eine Marke, dass es ungeprueft ist.

**Prioritaet:** mittel.

### Zeitparser und Fremdbibliothek (31.07.2026)

#### PARSER-NACKTE-UHRZEIT-FALSCHER-TAG — eine Uhrzeit ohne Tagesangabe landet im Vormonat 🔧 Umgangen, Ursache extern
**Kategorie:** WIS

**Rang:** **niedrig** — umgangen (Pfad 1c, `server/utils/zeitparser.py:1422-1470`), Riegel mit Verfallsdatum (`f2052c6`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: offen nur, weil die Ursache in der Bibliothek liegt; `dateparser` ist ungepinnt (`server/requirements.txt:24`).

**Umgangen am 31.07.2026** durch Pfad 1c: Ein Ausdruck, der nach der Normalisierung nur noch aus `HH:MM` besteht, bekommt seinen Tag selbst gerechnet, statt ihn bei `dateparser` zu erfragen. **Die Ursache liegt in der Bibliothek und ist nicht behoben.**

**Entdeckt:** beim ersten Lauf des Haertefallkorpus gegen den Parser — zehn Faelle des Bestandsschutz-Blocks fielen durch, in **beiden** Parserfassungen. Nicht gesucht.

**Symptom**, gemessen am 31.07.2026 am Bestandsparser im Produktionsmodus, heute war der 31.:

```
halb drei          ->  2026-07-01 02:30
dreiviertel acht   ->  2026-07-01 07:45
14 Uhr 30          ->  2026-07-01 14:30
morgens            ->  2026-07-01 08:00
```

**Mechanismus, instrumentiert.** Es sind **zwei** Defekte, beide in `_correct_for_time_frame` von `dateparser` 1.4.1:

**A — der Uebertrag wird ueberschrieben.** Die Addition ist korrekt: `dateobj + timedelta(days=1)`, mit Uebertrag in Monat und Jahr. Unmittelbar danach laeuft `_correct_for_month`, und die rechnet nicht, sondern **weist zu** — `date_obj.replace(month=<Monat des Bezugsmoments>)`. Die Korrektur soll ein *nicht genanntes* Monatsfeld fuellen; zu ihrem Zeitpunkt ist das Feld aber das **Ergebnis der Addition**, und ein `datetime` traegt keine Herkunft, an der sie beides unterscheiden koennte.

```
ZEITRAHMEN  2026-07-31 02:30  ->  2026-08-01 02:30     korrekt
MONAT       2026-08-01 02:30  ->  2026-07-01 02:30     Zuweisung
```

**Der Silvester-Fall ist der Fingerabdruck:** 31.12. + 1 Tag ergibt 01.01.2027, dann `replace(month=12)` → **01.12.2027**. Das Jahr ueberlebt, weil nur das Monatsfeld zugewiesen wird — elf Monate daneben, nicht zwoelf. Eine fehlerhafte Addition koennte dieses Muster nicht erzeugen.

**B — die beiden Seiten des Vergleichs sind nicht dieselbe Groesse.**

```python
tz_offset = tz.utcoffset(dateobj)
if self.now > dateobj - tz_offset:
    dateobj = dateobj + timedelta(days=1)
```

`self.now` ist naive Ortszeit, von `dateobj` wird der UTC-Versatz abgezogen. Jede Uhrzeit innerhalb der naechsten `utcoffset` Stunden gilt als vergangen. Gemessen bei Europe/Berlin, Referenz 15.07. 14:27 — die Kante liegt exakt bei +2h:

| Eingabe | Ergebnis | |
|---|---|---|
| `14:28` | 16.07. 14:28 | falsch |
| `15:00` | 16.07. 15:00 | falsch |
| `16:26` | 16.07. 16:26 | falsch |
| `16:27` | 15.07. 16:27 | richtig |

**Bedingungen und Haeufigkeit.** Defekt A verlangt drei Dinge gleichzeitig: eine Uhrzeit ohne jede Tagesangabe, den **letzten Tag des Monats**, und eine Uhrzeit, die heute schon vorbei ist. Das sind zwoelf Tage im Jahr, dafuer mit 28 bis 31 Tagen Betrag. **Defekt B trifft jeden Tag** und beide Richtungen — bei `past` bleibt ein Zeitpunkt in der **Zukunft** stehen.

**Warum es so lange unentdeckt blieb.** Der Plausibilitaets-Check verwirft erst ab zwei Jahren Vergangenheit; dreissig Tage laufen ohne ein Wort durch. Und ein Test, der gegen `date.today()` laeuft, ist bei Defekt A an 29 von 30 Tagen gruen.

**Reichweite, instrumentiert:** Fuer Wochentage, Dauern und deiktische Worte wird die Monatskorrektur gar nicht erst gerufen — `Montag`, `in einem Tag`, `morgen` tragen korrekt ueber die Monatsgrenze. Die nackte Uhrzeit ist der einzige Ausdruck, der dort ankommt.

**Der Riegel traegt ein Ablaufdatum:** `tests/test_zeit_dateparser_riegel.py` prueft die Bibliothek direkt und haelt beide Fehlwerte in getrennten Klassen fest. Er wird rot, sobald einer der Defekte verschwindet. **Erst wenn beide weg sind, kann Pfad 1c entfallen** — wer nach der Behebung nur eines davon aufraeumt, holt den anderen zurueck.

**Offen:** ein Fehlerbericht an die Bibliothek.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-gedaechtnis.md), [Hintergrund](novaberg-bugs-hintergrund.md), [Charakter](novaberg-bugs-charakter.md), [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### `READ-NACH-UPDATE-ALTER-WERT` — Read nach Update zeigt alten Wert ⬜
**Kategorie:** WIS

**Rang:** **niedrig** — der Eintrag nennt weder Datei noch Bezeichner und ist nicht gegen den Code prüfbar (Durchsicht 05.10.2026, gegen HEAD `17bf86e`); der Agentweg hat sich seither verändert.

**Entdeckt:** Chat 27
**Prio:** Mittel — architektonische Frage: Sollen Reads generell über den Agent gehen?

---

### Classify & Router (Chat 48)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

---

### Chat 80 — character_id-Inventur (M2.5a-Folge)

#### TIMELINE-PAIR-MISSING — Timeline-Tabelle ohne `character_id` ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — still beim zweiten Charakter, Aufwand groß (DDL). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `timeline` hat keine `character_id` (`server/agents/timeline/init.sql:7-26`).

**Zustand:** offen — am laufenden Schema geprueft am 25.08.2026, **unveraendert**: `timeline` fuehrt `user_id` und kein `character_id`.
**Entdeckt:** Chat 80, im Zuge der M2.5a-Phase-2-Implementierung (Magnet-Spalten-Befüllung beim Timeline-Schreiben)

**Klasse:** Schema-Lücke, Severity Mittel — Foundation-Bug, akut nur bei Multi-Charakter-Setup

**Symptom:** `timeline` hat heute nur `user_id`, kein `character_id`. Verletzt `novaberg-convention-paar-schema.md` (Subjekt × Gegenüber × Beobachter) und `novaberg-convention-magneten.md` §6 (Welt-/Erlebnis-Trennung). Aria-Termine würden bei Nova auftauchen und umgekehrt — heute kein praktisches Problem (nur Nova aktiv), aber jeder neue Charakter bringt das Wissens-Leck mit.

**Vermutung:** Andere paar-skopierte Speicher (`langzeitgedaechtnis`, `notizen`, `fakten`, `dateien`) ungeprüft. Sauber: KZG (Redis-Schlüssel), `charakter_hash` (Composite PK).

**Lösung — zwei Sprints:** TIMELINE-PAIR-INVENTUR (Read-only-Sweep, ~10 Min) → TIMELINE-PAIR-MIGRATION (Spalte ergänzen, Indexe, Repositories, Bestand auf `character_id='nova'` initialisieren).

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug TIMELINE-PAIR-MISSING (Chat 80).

#### NOTIZEN-PAIR-MISSING — Notizen-Tabelle ohne `character_id` ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — still beim zweiten Charakter (DDL). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `notizen` hat keine `character_id` (`db/init.sql:471-488`).

**Zustand:** offen — am laufenden Schema geprueft am 25.08.2026, **unveraendert**: `notizen` fuehrt `user_id` und kein `character_id`.
**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Schema-Lücke, Severity Mittel — Foundation-Bug, akut nur bei Multi-Charakter-Setup

**Symptom:** `notizen` hat nur `user_id`, kein `character_id`. Repository filtert nur `WHERE user_id = %s`. Bei Multi-Charakter-Setup würden Aria-Notizen bei Nova auftauchen und umgekehrt. Verletzt `novaberg-convention-paar-schema.md` und `novaberg-convention-magneten.md` §6 — identische Klasse wie TIMELINE-PAIR-MISSING und FAKTEN-PAIR-IGNORED.

**Lösung:** Gemeinsamer Migrations-Sprint mit Timeline und Fakten. Bei Notizen einfach (1 Bestandseintrag, alle bekommen `character_id='nova'`).

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug NOTIZEN-PAIR-MISSING (Chat 80).

#### FAKTEN-PAIR-IGNORED — Fakten-Repository ignoriert `character_id` ⚠️
**Kategorie:** WIS

**Rang:** **niedrig**; ~~wartet auf eine Absicht: bleibt `fakten` ein lebender Speicher (dann Paar-Schema), oder wird er stillgelegt?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: die Tabelle ist leer und hat keinen Erzeuger; das Repository nennt `character_id` nicht.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: `fakten` wird **stillgelegt**, bis ein Fakten-Agent gebaut wird; das Paar-Schema entfällt bis dahin. Ein Entfernen der Tabelle wäre DDL und wird vorher angekündigt.

**Zustand:** offen im Code, **Begruendungszahl verfallen** — gegen HEAD `cc5aaae` und den Bestand gehalten am 25.08.2026. Die Spalte `character_id` steht in `fakten`; `fakten_repository.py` nennt sie **0 mal**, der Befund gilt also unveraendert. Die *171 Live-Eintraege*, die ihn als Severity Hoch begruendeten, sind **0 Zeilen** — die Tabelle ist leer. Was bleibt, ist die Repository-Luecke ohne Datenmigration.
**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Repository-Lücke trotz vorhandener Schema-Spalte, Severity Hoch — 171 Live-Einträge betroffen

**Symptom:** `fakten` hat die Spalte `character_id` mit Default `'nova'`. INSERTs in `fakten_repository.py` setzen die Spalte nicht (DB-Default greift). SELECTs filtern nur `WHERE user_id = %s`, ignorieren `character_id` komplett.

**Im Repository geschlossen am 18.10.2026** (Tree `00c7b4c`, Schema und Repository des Faktengedächtnisses): Jede Abfrage von `memory/repositories/fakten_repository.py` filtert nach `user_id` und `character_id`, `insert` schreibt `character_id` ausdrücklich, ein unvollständiges Paar wird abgewiesen. Das Plugin nimmt das Gegenüber aus dem Write (`daten["character_id"]`) und aus dem State und verwirft einen Write ohne es mit einer Fehlerzeile; die Wiedervorlage liest im Paar (`user_id`, `ASSISTANT_USER_ID`). Zeuge: `server/tests/test_fakten_repository.py::EveryQueryFiltersByThePairTest`. **Offen bleiben die zwei Stellen am Repository vorbei** (unten) — der Eintrag bleibt deshalb hier.

**Weitere Stellen, gegen HEAD `7b65297` gelesen am 17.10.2026.** Am Repository vorbei lesen zwei Stellen `fakten` mit eigenem SQL, und auch sie filtern nur `user_id`, nie `character_id`: `api/gedaechtnis.py::fakten_abrufen` (Endpunkt `GET /fakten/{user_id}`, Z. 373–379) und `graph/nodes/gespraechsvektor.py::_entity_kontext_laden` (Z. 435 und 454; diese Funktion hat keinen Aufrufer). Geschlossen ist der Eintrag erst, wenn jede Stelle nach dem Paar liest oder über die eine Lesefunktion des Faktengedächtnisses (Bauteil F1, `novaberg-memory-fakten_b.md`). → **Die Bauart dazu ist am 17.10.2026 angenommen, nicht gebaut:** Das Repository nimmt das Paar in jede Abfrage, `fakten_abrufen` liest über die Mappe, und `_entity_kontext_laden` entfällt, weil es keinen Aufrufer hat (`novaberg-memory-fakten_b.md` §6, *Die angenommene Bauart*, F1 und F2).

**Komplikation:** 171 Bestandseinträge unter `user_id='nova'` (Pre-Paar-Schema-Logik) repräsentieren *"Nova-Sicht auf Meister"* und gehören semantisch zu `(user_id='meister', character_id='nova', beobachter='assistant')` — nicht trivial pauschal umsattelbar.

**Lösung:** Konzept-Dokument vor Sprint. Klärt Spalten-Migration, Repository-Anpassung, Daten-Migration mit ASSISTANT_USER_ID-Umsattelung.

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug FAKTEN-PAIR-IGNORED (Chat 80).

### Chat 80 — Live-Test-Befunde (NOTIZEN-VOR-TURN-BEZUG-Smoke-Test)

#### NOTIZEN-KONTEXT-REKONSTRUKTION — Mehrschritt-Rekonstruktion fehlt ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — laut, Aufwand groß. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: eine Auflösung über mehr als einen Turn ist nicht gebaut (`server/agents/notizen/klassifikation.py:63-78`); der Frame-Auflöser befragt Notizen nicht.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Bezugsaufloesung ueber mehr als einen Vor-Turn. Der Eintrag verweist auf das Frame-Konzept als Loesung; sein Symptom ist eine Turnfolge.
**Entdeckt:** Chat 80, Live-Test B des NOTIZEN-VOR-TURN-BEZUG-Sprints

**Klasse:** Strukturelle Lücke — Bezugsauflösung über mehrere Vor-Turns hinweg, Severity Hoch

**Symptom:** Bei UPDATE/RENAME-Aktionen mit Bezugs-Pronomen über mehrere Turns (Distanz >1) scheitert die Rekonstruktion. Konkret: Drei-Sachen-Aufzählung in Turn n-3 + Notiz-Erstellung in Turn n-1 + *"schreib die 3 Sachen rein"* in Turn n → Nova fragt *"Welche drei Sachen?"*.

**Was heute fehlt:** Classify-Node hat Vor-Turns als `[KONTEXT]`-Block, aber keinen Mechanismus für mehrschrittige semantische Kette über Turn-Distanz >1. Heutige Inhalts-Auflösung (Chat-80-Sprint) deckt nur einen Vor-Turn-Sprung ab.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — Frame-Auflöser-Node (`thinking-frames_k.md` §7) iteriert Slot für Slot über Vor-Turns.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-KONTEXT-REKONSTRUKTION (Chat 80).

#### NOTIZEN-CONTAINER-WECHSEL — Notiz↔Liste-Wechsel verweigert ⚠️
**Kategorie:** WIS

**Rang:** **niedrig**; ~~wartet auf eine Absicht: ist der Typ einer Notiz nachträglich änderbar (Text → Liste)?~~ → **entschieden am 06.10.2026** (unten). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: keine Codestelle verbietet es; die Verweigerung kam vom Modell.

**Entschieden am 06.10.2026** vom Eigentümer — *„Alle wie empfohlen“*, über 23 offene Absichtsfragen des Registers zugleich. Für diesen Eintrag: **Ja** — der Typ einer Notiz ist nachträglich änderbar, als eigene Aktion des Notizdienstes.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: die Verweigerung eines Notiz-zu-Liste-Wechsels ist eine Antwort, keine Codezeile.
**Entdeckt:** Chat 80, Live-Test B

**Klasse:** Architektur-Strenge zu hoch — Container-Typ als unveränderliche Klasse, Severity Mittel

**Symptom:** NotizenAgent trennt "Textnotiz" und "Liste" als harte Klassen. Eine als Textnotiz angelegte Notiz kann nicht zu einer Liste mit Items erweitert werden, obwohl semantisch sinnvoll. Nova-Antwort im Live-Test: *"Das System unterscheidet hier strikt zwischen einer Textnotiz und einer strukturierten Liste."*

**Was heute fehlt:** Container-Typ als änderbare Eigenschaft. Korrekte Aktion bei `add_content` auf Textnotiz mit mehreren Items: Container-Typ-Wechsel zu Liste, Items strukturieren.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — `notiz_update`-Frame mit Slot `neuer_typ` definiert Container-Wechsel als legitime Aktion.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-CONTAINER-WECHSEL (Chat 80).

#### NOTIZEN-SKILL-MANIFEST — Skills nicht in Sprach-Schicht repräsentiert ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — still, die Selbstauskunft bleibt Zufall. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `AgentRegistry.beschreibungen()` (`server/agents/__init__.py:47`) hat keinen Aufrufer außerhalb der Tests.

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: falsche Selbstauskunft ueber die eigenen Faehigkeiten. Der Nachtrag vom 16.08.2026 im Rumpf nennt mit `SELBSTAUSKUNFT-OHNE-LESER` die messbare Haelfte derselben Ursache.
**Entdeckt:** Chat 80, Live-Test B (durch Meister thematisiert)

**Klasse:** Domain-Language-Lücke — Skills im Code vorhanden, in der Sprach-Schicht nicht repräsentiert, Severity Mittel

**Symptom:** Nova verweigert legitime Aktionen mit Begründungen, die im Code so nicht stimmen. Sie kennt ihre eigenen Skills nicht in dem Sinne, dass sie sie erklären oder anbieten könnte. Falsche Selbstauskunft an User.

**Erwartung:** Butler-Selbstkenntnis. *"Ich kann für Sie Listen erstellen, Notizen erstellen, das eine zum anderen abändern, Inhalte anhängen oder entfernen, umbenennen, leeren..."*

**Strukturelle Lösung:** Frame-Konzept Phase 1b implizit. Frames definieren legitime Aktionen pro Domäne; Frame-Lager (§11) wird zur Skill-Selbstkenntnis-Quelle. Kleinerer Skill-Manifest-Sprint wäre möglich, in Chat 80 bewusst gegen die strukturelle Lösung verworfen.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-SKILL-MANIFEST (Chat 80).

> **Nachtrag 16.08.2026 — derselbe Defekt, eine Schicht tiefer, unabhängig gefunden.** `SELBSTAUSKUNFT-OHNE-LESER` (Backlog) beschreibt dieselbe Lücke am **Planer** statt an der Sprach-Schicht: Die Agenten deklarieren ihre Fähigkeiten vollzählig (14 von 14 `faehigkeiten`, 12 von 14 `AGENT.md`), und `AgentRegistry.beschreibungen()` hat null Aufrufer. **Nova kennt ihre Skills nicht, weil im ganzen System niemand sie liest** — weder um sie anzuwenden noch um sie zu erklären. Die beiden Einträge haben damit **eine gemeinsame Ursache und womöglich eine gemeinsame Abhilfe**; wer einen davon angeht, prüft den anderen mit. Die dort gemessene Einschränkung gilt hier ebenso: Eine Fähigkeitenliste ist in der Sprache des Anbieters formuliert und taugt weder zur Auswahl noch zur Selbstauskunft gegenüber dem Nutzer — die Manager-Aushänge (`router_prompt`) zeigen die brauchbare Gestalt.

#### NOTIZEN-UPDATE-TARGET-LEER — Bezugs-Pronomen für UPDATE crashen ⚠️
**Kategorie:** WIS

**Rang:** **mittel** — laut (`status=fehler`). Durchsicht 05.10.2026, gegen HEAD `17bf86e`: ein leeres `target` läuft ungeprüft in die Suche (`server/agents/notizen/suche.py:77-125`).

**Zustand:** unbelegt — braucht Messturn. Gegen HEAD `cc5aaae` am 25.08.2026 gesichtet: Crash bei leerem `target` im UPDATE-Pfad. Verwandt mit `NOTIZ-RESUME-TARGET-VERLUST`, wo der leere String inzwischen einen Vorgabewert hat — ob dieser Pfad denselben traegt, zeigt erst der Aufruf.
**Entdeckt:** Chat 80, Live-Test B

**Klasse:** Bezugsauflösung im UPDATE-Pfad — verwandt zu NOTIZEN-VOR-TURN-BEZUG, andere Aktion, Severity Hoch — Crash-Verhalten

**Symptom:** UPDATE/RENAME-Aktion mit Bezugs-Pronomen (*"Aktualisiere sie"*) übergibt leeren `target`. NotizenAgent-Crash: *"keine Notiz mit dem Namen '' gefunden"*.

**Was heute fehlt:** Heutiger Sprint hat das Verbot nur für CREATE aufgehoben (Inhalts-Auflösung). UPDATE-Pfad hat dieselbe Lücke: `target` wird nicht aus Vor-Turns aufgelöst.

**Strukturelle Lösung:** Frame-Konzept Phase 1b — Frame-Auflöser löst Slots wie `target` deterministisch aus Vor-Turn-Kontext. Pattern identisch zur Inhalts-Auflösung, nur in anderem Slot.

**Ausführliche Beschreibung:** novaberg-backlog.md → Bug NOTIZEN-UPDATE-TARGET-LEER (Chat 80).

---

### Chat 106 — Tagesgeschäft (Befunde)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Charakter](novaberg-bugs-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### NOTIZ-RESUME-TARGET-VERLUST — Rückfrage verarmt bei jedem Resume ⚠️
**Kategorie:** WIS

**Rang:** **niedrig** — laut, Abhilfe eine Zeile. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; `.get("target", "Notiz")` (`server/agents/notizen/resume.py:212`) fängt den leeren String nicht, den `dispatch.py:56-60` immer setzt.

**Zustand:** offen, **entschaerft** — gegen HEAD `cc5aaae` gehalten am 25.08.2026. `agents/notizen/resume.py:206` liest heute `state["parameter"].get("target", "Notiz")` — der leere String aus dem Symptom ist abgefangen, die Rueckfrage lautet nicht mehr *„Notiz ''"*. Die Ursache steht: `target` wird weiterhin nicht aus den Vor-Turns aufgeloest, der Vorgabewert verdeckt das nur.
**Entdeckt:** Chat 106, Nebenbefund der AGENT-RUECKFRAGE-LOOP-Abnahme. **Prio mittel.**

**Symptom:** Turn 1: *„Es gibt bereits eine Notiz 'Neue Notiz anlegen'."* → Turn 2:
*„Es gibt bereits eine Notiz ''."* — `_resume_duplikat` liest `parameter["target"]`,
das im Resume-Parameter leer ist. Verwandt: `action='agent'` im Resume-Dispatch (der
Chat-43-Bug „pending_data speichert Input statt Output" lebt im Notizen-Agenten weiter;
ohne Auswirkung, weil `resume.py` sich `create` aus den Parametern holt — Fehlerkeim).

**Beleg:** `agents/notizen/resume.py`, `_resume_duplikat` (Target-Lesung aus
`parameter`); Pending-Aufbau in `agents/notizen/dispatch.py`.

**Auswirkung:** Rückfragen werden mit jedem Resume-Zyklus unverständlicher.

*Aktualisiert Chat 106 (Abschluss, Quelle: Chat-106-Protokoll): Drei Bugs live bewiesen
und geschlossen — AGENT-RUECKFRAGE-LOOP (`f1b3a27`, 18:14:01), THINKER-SELFTRIGGER-KANALLOS
(`090ac07`, 18:35:22), RESPONDER-VEKTOR-TOT (`f1b7f8e`, 19:11:43/Abnahme 19:19:51). Keiner
wurde durch Code-Lesung gefunden — alle drei durch eine Log-Zeile, die vorher nicht da war.
NOVA-SYKOPHANZ-BESTAETIGT auf Protokoll-§7-Wortlaut gezogen. Neu aufgenommen: 6 Einträge
aus dem Lügende-Logs-Audit (BROADCAST-VERSCHLUCKT-FEHLER als Wurzel,
SHADOW-DELIVERY-DATENVERLUST und WIEDERVORLAGE-SNOOZE-OHNE-WIRKUNG als Datenverlust-Fälle)
und 3 aus dem Tagesgeschäft (EI-VEKTOR-TEXT-EMOTIONSFEST, GV-STRATEGIE-VEHIKEL-LEER,
NOTIZ-RESUME-TARGET-VERLUST). Nach der Trennungsregel (bugs = der Code tut etwas Falsches;
backlog = Konzepte/Refactors/Doku-Drift/toter Code; ein Eintrag in GENAU EINEM Dokument)
nach novaberg-backlog.md verschoben: PIPELINE-LOG-ART-DOKU-DRIFT (Doku-Drift),
DELEGATION-STATE-UNDEKLARIERT (Landmine/Sperrvermerk), PLANNER-AKTIV-RELIKT,
WEB-CONTEXT-ALTPFAD, BUILDER-CREATE-INITIAL-STATE-TOT (toter Code).
NOTIZ-BEFEHL-ALS-TITEL bleibt offen — der Auslöser der Duplikate, die die
Disambiguierung erzeugen, die den Loop auslöste: der Crash ist behoben, nicht die Ursache.*

---
