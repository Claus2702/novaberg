# Novaberg — Bugs: Wissen — Bibliothek, Dateien, Notizen, Timeline, Fakten

**Inhalt:** die offenen Defekte dieses Gegenstands, 21 Eintraege, je mit `**Kategorie:** WIS`.
**Wegweiser:** [`novaberg-bugs.md`](novaberg-bugs.md) — Kopf, Form eines Eintrags, Rangfolge, Verlauf. **Findemittel ueber alle Teile:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Archiv:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Register** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

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

**Zustand:** offen — gefunden am 01.09.2026 gegen HEAD `79aaaa6`, aus der Fundliste uebernommen.

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

#### NOTIZ-BEFEHL-ALS-TITEL — Meta-Befehl wird als Notiz-Name gespeichert ⬜ Chat 103
**Kategorie:** WIS

**Rang:** **mittel** — still. Durchsicht 05.10.2026, gegen HEAD `17bf86e`: gilt; der Prompt verlangt für `name` den exakten Wortlaut (`server/agents/notizen/crud.py:93-157`), die Fachsprache lehrt Normalisierungen ohne Namen.

**Zustand:** offen, **unbelegt** — am Bestand nachgesehen am 25.08.2026. Die Tabelle `notizen` traegt **eine** Zeile; die beiden Notizen, die den Befund belegten, gibt es nicht mehr. Der Klassifikator ist damit nicht geprueft, sondern nur der Beleg verfallen.

Der Notiz-Klassifikator speichert die Meta-Formulierung des Befehls als Name
(Spalte `name`, nicht `titel`) statt sie als Anweisung aufzulösen. Belegt
Chat 103: notizen `id 3` und `id 4` tragen den Namen „Neue Notiz anlegen"
(id 4 enthält den kompletten P1–P10-Migrationsplan als Inhalt), zwei weitere
„Neue Notiz". Folge: viele Namens-Duplikate → Disambiguierungs-Rückfragen →
Auslöser für AGENT-RUECKFRAGE-LOOP. Verwandt mit
REFERENZ-AUFLOESUNG-VOR-RETRIEVAL / NOTIZEN-VOR-TURN-BEZUG (anaphorische
Auflösung vor dem Retrieval fehlt). Fix-Richtung: Klassifikator muss
Meta-Befehle („neue Notiz anlegen", „das festhalten") vom Namens-Inhalt
trennen; Name aus dem Sach-Inhalt ableiten.

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
