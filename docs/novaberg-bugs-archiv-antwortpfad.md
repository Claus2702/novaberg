# Novaberg — Bugs, Archiv: Antwortpfad — Gesprächsvektor, Responder, Verfasser, Prompts

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, 47 Eintraege, je mit `ANT` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 19.09.2026 — aus dem offenen Register übernommen

*Behoben am 10.09.2026, mit benanntem Rest; der Rest steht als Zeile in der Fundliste. Übernommen am 19.09.2026 beim Teilen des Registers nach Gegenstand.*

#### GV-FARBTON-SUBJEKTWECHSEL — der Farbton behauptet etwas über den Nutzer und misst Nova ⚠️
**Kategorie:** ANT

**Zustand:** ✅ **behoben am 10.09.2026 — mit benanntem Rest.** Die Absichtsfrage, auf die der Eintrag wartete, ist entschieden (Setzung des Eigentuemers, 10.09.2026): Der Farbton beschreibt **den Raum**, also wie sich beide aktiv zueinander verhalten — nicht eine Seite. `_farbe_intent` und `_farbe_dynamik` lesen seither `internal` **und** `external` und nennen beide Seiten; die Namen richten sich nach dem Leser — angesprochen wird nie der Charakter, sondern der Schauspieler ueber die Rolle. 22 Zeugen in `tests/test_farbton_raum.py`, drei Gegenproben (2, 8 und 3 vorhergesagt, alle drei so gezaehlt), Betriebsbeleg am 10.09.2026. **Auf einem Impuls-Turn bleibt die zweite Quelle ungelesen** — dort ist `external` eine Kopie von `internal`; 81 von 154 solchen Turns haetten sonst einen Paarsatz aus zweimal demselben Wert getragen.

**Der Rest, den die Abhilfe nicht deckt:** Der Eintrag nennt **vier** betroffene Farben. `_farbe_stil`, `_farbe_tone` und `_farbe_modus` sprechen bereits ueber den Raum (*„Der Ton ist sachlich"*, *„Das Gespraech ist fachlich"*) und behaupten nichts ueber den Nutzer — sie **messen** den Raum aber weiter aus einer Seite. Das ist keine Falschaussage mehr, sondern eine unvollstaendige Messung; die Zeile dazu steht in `novaberg-fundliste.md`.

**Was gemessen war, bevor es behoben wurde** `[10.09.2026, ueber 1348 Turns]`: **1164 (86,3 %)** trugen mindestens einen Satz ueber den Nutzer aus Novas Werten. Bei der Dynamik waren **419 von 826 (50,7 %)** gegen den am Nutzer gemessenen Wert falsch, beim Intent **292 von 904 (32,3 %)** — zusammen **711 falsche Aussagen** im Bestand. Haeufigster Einzelfall: **167-mal** *„Der Nutzer ist offen und vertraut"* bei gemessener `distanz`.

~~**Zustand:** offen — gegen HEAD `cc5aaae` gehalten am 25.08.2026, **unveraendert und am Code belegt**: `ei/farbton.py:198-202` liest `state.get("internal")`, also Novas Werte; `:72` formuliert daraus *„Der Nutzer haelt Abstand."* — genau der Satz aus dem Beleg. Das gilt fuer die ganze Tabelle: acht Saetze beginnen mit *„Der Nutzer"*.~~
**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel-hoch.**

**Symptom:** `farbton_berechnen` liest durchgehend `internal` (Nova), formuliert aber
Sätze über den Nutzer: *„Der Nutzer haelt Abstand."*, *„Der Nutzer ist offen und vertraut."*
Vier der acht Farben sind betroffen (`_farbe_intent`, `_farbe_dynamik`, `_farbe_stil`/`_farbe_tone`
und mittelbar `_farbe_modus`).

**Beleg (28.07.2026, 12:34:46):** Der `[SITUATION]`-Block trug *„Der Nutzer haelt Abstand."*,
während die Perzeption des Nutzers im selben Turn `dynamik=neutral` sagte. Die `distanz`
stammte aus `perzeption_assistant` auf **Novas eigene** Antwort des Vorturns — die Felder
`mode`, `language_style`, `relationship_dynamic`, `tone` und `intent` in `internal.emotion`
kommen aus `redis:nova_state` und beschreiben Novas letzte Äußerung, nicht den Nutzer.

**Auswirkung:** Das LLM bekommt eine Tatsachenbehauptung über den Nutzer, die auf einer
Messung an Nova beruht. Eine dichte Fachantwort Novas lässt den nächsten Turn glauben, der
Nutzer gehe auf Abstand. Konzept §10.1 nennt für `_farbe_dynamik` ausdrücklich das Beispiel
„Der Nutzer öffnet sich" — gemeint ist die Perzeption des Nutzers.

~~**Entscheidung nötig:** Welche der acht Farben Nova beschreiben sollen und welche den
Nutzer. Der Node liest beides und hat beide Quellen zur Hand.~~ → **Am 10.09.2026 entschieden, und die Antwort war keine der beiden angebotenen.** Der Eigentuemer: *„Der Raum sagt, wie sich beide aktiv zueinander verhalten. Nicht einer aktiv und der zweite passiv, sondern beide gemeinsam schaffen den Raum."* Die Frage bot Nova **oder** Nutzer an; die Antwort ist **beide**, und die Asymmetrie wird benannt statt verrechnet — *„Nova ist offen und zugewandt, der Nutzer haelt Abstand."* Ein Mittelwert haette geloescht, was der Block zeigen soll.

> **Der Sollzustand stand die ganze Zeit im Modul selbst.** `_farbe_dynamik` fragte im Docstring *„Wie nah sind wir uns?"* — beidseitig —, `_farbe_modus` trug die Regel *„Die Saetze beschreiben den Raum, nicht den Nutzer"*, und `lage_beschreiben` die Zusage *„Die Beschreibung adressiert niemanden"*. Drei Stellen nannten ihn, vier Zeilen dazwischen brachen ihn. **Was fehlte, war nicht die Regel, sondern die zweite Quelle.**

---

## 17.09.2026 — ein Paar ohne Ziele verlor jeden Turn

### `ENRICH-NULLTERM-IST-EINE-ZAHL` — der Nullwert hatte den falschen Typ ✅
**Kategorie:** ANT

**Zustand:** behoben am 17.09.2026, gefunden in der Betriebsmessung zu Scheibe 12 D.

**Symptom.** `graph/nodes/enricher.py::_compute_ziele_und_gravitation` gab im Zweig *keine aktiven Ziele* das Tupel `[], 0.0, 0.0` zurück; beide Aufrufer (`:499` HumanGraph, `:835` CharacterGraph) lesen dort `.normiert`. Jeder Turn eines Paares ohne aktive Ziele brach ab — `AttributeError: 'float' object has no attribute 'normiert'` —, die Antwort blieb leer. 20 Vorfälle im Serverlog, alle fünf Turns eines neuen Prüf-Nutzers.

**Warum es lange unsichtbar war.** Das eingespielte Paar des Betriebs trägt aktive Ziele und nimmt den Zweig nie. Getroffen wird, wer neu ist — und der bekommt dann gar keine Antwort.

**Behebung.** Der Nullwert kommt aus derselben Rechnung wie jeder andere Term (`gravitationsterm_berechnen([])`), der Rückgabetyp ist im Kopf der Funktion berichtigt. Zeuge: `tests/test_enricher_ohne_ziele.py` — er prüft den **Typ**, nicht den Wert. Suite 3890 grün, Gegenprobe 2 rot wie vorhergesagt.

**Die Regel dahinter:** *Ein Default darf nie aussehen wie ein echter Wert* — hier sah er sogar wie ein anderer Datentyp aus, und die Docstring der Funktion versprach bereits das Objekt.

---

---


## 16.09.2026 — das Zeitwort überstimmt den gewählten Dienst

Eine Kennung aus der Entscheidung vom selben Tag: **Welcher Dienst eine Merk-Bitte mit Zeitbezug bekommt, hängt am Gegenstand und nicht am Zeitwort.** Bis dahin war die Abweichung keine Verletzung, sondern eine offene Absichtsfrage (Fundliste 14.09.2026).

### `PLANNER-ZEITWORT-UEBERSTIMMT-DIENSTWAHL` — jede Zeitangabe schickt die Merk-Bitte an die Timeline
**Kategorie:** ANT

**Zustand:** ✅ behoben am 17.09.2026 (Scheibe 12 D1, `graph/nodes/planner.py::service_order_for`). ~~offen — gegen den Code nachgesehen am 16.09.2026.~~

**Symptom.** `graph/nodes/planner.py:399` wählt in Priorität 1 den Timeline-Dienst, sobald `needs_timeline` und `management_action` gesetzt sind; `management_target` wird dort nicht gelesen. `needs_timeline` setzt der Router bei jeder Zeitangabe. Der Aushang der Notizen nennt *„Merk dir, dass ich morgen Mehl brauche"* als sein eigenes Beispiel (`plugins/notizen_manager/manager.py:106`) — ein solcher Satz erreicht die Notizen nicht. `[gemessen 14.09.2026, Log]` Vier Zustellungen mit Zeitbezug, alle an `agent/timeline`, keine an die Notizen. Gefunden von der zweiten Kontrolle.

**Die Absicht steht seit dem 16.09.2026** (`novaberg-thinking-lage_k.md`, Scheibe 12, *Das Kriterium der Zuordnung*): Eine **Handlung oder ein Ereignis mit Zeitpunkt** gehört in die Timeline, eine **Sache oder ein Zustand mit Zeitbezug** in die Notizen. Das Beispiel im Notizen-Aushang ist danach richtig, die Wahl des Planners ist falsch.

**Wirkung.** Der Notizen-Dienst ist für jede Merk-Bitte mit Zeitbezug geschlossen, und die Klasse des Objekts spielt bei der Wahl keine Rolle. Beides trifft die Prüfungen dahinter: Der Bestandsabgleich des Riegels (Entscheidung 15.09.2026) sucht eine Behauptung im Speicher des Dienstes, den der Empfang gewählt hat — bei einer Notiz also in der falschen Tabelle.

**Was fertig wäre.** Die Wahl folgt der Klasse des Objekts statt dem Vorkommen einer Zeitangabe: Eine Merk-Bitte über eine Sache mit Zeitbezug erreicht die Notizen, eine über eine Handlung mit Zeitpunkt die Timeline — je Richtung bezeugt und in einem echten Lauf belegt.

**Der Weg ist entschieden und es ist der größere:** Scheibe 12 C und D — Objekt-Merkmal je Dienst, gerechnete Nähe, Zustellung mit Objektbezug. **Der kleine Weg ist geprüft und verworfen:** Priorität 1 nur greifen zu lassen, wenn kein anderer Dienst im Auftrag steht, würde diesen einen Fall abfangen und die Wahl weiter an einem Zeitwort-Flag hängen lassen.

**Priorität:** hoch — er hält einen der beiden Empfangsdienste für eine ganze Auftragsart geschlossen.

**Die Behebung (17.09.2026).** Priorität 1 ist entfernt. Der Router reicht das Urteil der Objekt-Nähe als `objekt_urteil` weiter; der Planner fragt zuerst die Dienste, deren Merkmal ein akutes Objekt erreicht (nach Nähe), dann den Treffer der übrigen Prioritäten — ein Treffer ohne eigenes Merkmal steht vorn. Nach `abgelehnt` oder `rejected` wird der nächste gefragt. **Gemessen** über 60 Äußerungen mit echtem Router und Planner, ohne Agenten (`labor/2026-09-17_planner_d1/`): 17 Aufträge; **Notizen-Fälle zuerst richtig 7 → 13 von 13**, Termine 4 → 4 von 4 — alle sechs geänderten Fälle Merk-Bitten mit Zeitangabe. Den Gewinn trägt vor allem das Entfernen der Priorität: Der Router-Treffer lag bei allen 13 Notizen schon richtig. Im Betrieb der 14 Tage davor hätte die neue Reihenfolge 0 von 11 Aufrufen einen anderen ersten Dienst gegeben. Zeugen: `tests/test_planner_objektwahl.py`.

---

## 13.09.2026 — die Form der Lage, eingeloest fuer jedes Feld

Ein Eintrag, **am Tag nach seinem Befund behoben** — der Blocker aus Band A. Die Abhilfe haengt an einer
Entscheidung des Eigentuemers ueber die Bedeutung eines Feldes, nicht an der Absturzstelle; und die Messung,
die sie bestaetigen sollte, fand zwei weitere Formen, die keine Pruefung vorher kannte.

### `LAGE-FORMPRUEFUNG-UNVOLLSTAENDIG` — die Formprüfung deckt die jüngeren Felder der Lage und nicht die zwei ältesten ⛔ Blocker
**Kategorie:** ANT

**Zustand:** ✅ **behoben am 13.09.2026** — gefunden am 12.09.2026 durch einen abgebrochenen Betriebsturn. `graph/nodes/sachlage_form.py::normalize_object_form` hält jedes Objektfeld, beim frischen Parse, beim Laden der vorigen Blase und im Lesepfad des Gesprächskontext-Tabs; Konzept nachgezogen in `novaberg-thinking-lage_k.md` §3 (Festlegung 1, Nachtrag).

**Symptom.** Ein Turn erreicht keine Antwort: `AttributeError: 'list' object has no attribute 'items'` in `sachlage_plausibility.py:87`. Das Modell lieferte `gedeckt` als **Liste**, die Lesestelle ruft `.items()`. Erster Fall im Serverlog, `[gemessen 12.09.2026, 18:55 UTC]`.

**Ursache.** `novaberg-thinking-lage_k.md` §3 Festlegung 1 verlangt einen Call mit erzwungenem JSON, der *„laut ausfällt statt still leer"*, und definiert im Artefakt `gedeckt` als **Zuordnung** (`{"anlass": "erwähnt im Turn"}`) und `offen` als **Liste**. `_validate_artifact` (`graph/nodes/sachlage.py`) prüft den Parse auf dict, fünf Pflichtfelder, `objekte` als Liste, jedes Objekt als dict mit `name`, hält die Smalltalk-Schranke — und normalisiert `traeger`, `kritikalitaet`, `sprecher`. **Für `gedeckt` und `offen` gibt es keinen Normalisierer.**

> **Die drei Felder mit Normalisierer stammen aus den Scheiben ~~7 bis 9~~ 8 bis 10** (~~am 29.08.2026 nachgebaut~~ → berichtigt am 13.09.2026: Träger Scheibe 8, Sprecher 9, Kritikalität 10). Die zwei ohne stehen seit **Scheibe 1** im Artefakt und werden von allen zehn Scheiben gelesen. Die Prüfung ist mit den jüngeren Feldern gewachsen und nie zu den ältesten zurückgekehrt — die Signatur schnellen Scheibenbaus: Jede Scheibe prüft, was sie selbst mitbringt; was schon da war, gilt als geprüft, weil es funktioniert hat.

**Wirkung — der Absturz ist der glückliche Fall.** Von sechs Lesern von `gedeckt` tragen **zwei** einen lokalen `isinstance(…, dict)`-Riegel (`sachlage.py:583`, `:635`), **vier** keinen: `sachlage_plausibility.py:86`, `sachlage_resolver.py:412`, `sachlage.py:1048`, `:1113`. Alle vier annotieren `gedeckt: dict` — eine Behauptung, keine Prüfung. Nur die erste ruft `.items()` und reißt den Turn ab; ~~**die drei anderen iterieren die Liste und laufen weiter**, vergleichen stringifizierte Dicts gegen Eigenschaftsnamen und erzeugen stillschweigend Unsinn.~~

> **Nachtrag 13.09.2026 — die Lesestellen waren unterschätzt** (Durchsicht vor dem Bau). `sachlage_resolver.py:412` (`gedeckt[offene] = …`) und `sachlage.py:1048/1056` (`gedeckt.get`) **werfen** bei einer nicht leeren Liste, statt weiterzulaufen. Ungenannt waren `sachlage_resolver.py:541` (`carry_sources`) und das Panel (`sachlage_panel.py:263`, `.items()`). Ungeprüft waren außerdem `quellen`, `plausibilitaet`, `recherche` (lieferte das Modell sie, blieben sie stehen), der Typ von `akut` (`"false"` galt als wahr), `name`, `klasse` und die Kopffelder; die vorige Blase aus Redis wurde nicht erneut geprüft.

`offen` wird durchgängig mit `or []` verteidigt, was eine Dict-Form **nicht** abfängt: `{"a": 1} or []` ist das Dict, die Iteration liefert Schlüssel. Betroffen ist auch `_normalize_holders` selbst, das `offen` so liest.

**Und Festlegung 3 verschärft es:** Das volle Artefakt geht je Turn ins `pipeline_log`. Eine falsche Form steht dort als gültige und trägt jede spätere Auswertung.

~~**Die Abhilfe folgt aus dem Hausmuster, nicht aus der Absturzstelle.** Die drei bestehenden Normalisierer haben dieselbe Form: `isinstance`-Prüfung, `logger.warning` mit dem gefundenen Typ, Feld verworfen, Objekt und Turn überleben — genau, was Festlegung 1 verlangt. Zwei weitere nach diesem Muster; danach können die sechs Lesestellen der Form trauen, die ihre Annotation schon behauptet, und die zwei lokalen Riegel werden überflüssig.~~ → **Die Abhilfe verwirft nicht, sie ordnet ein** — so folgt es aus der Entscheidung unten; verworfen wird nur, was keine Eigenschaft ist.

~~**Eine Absichtsfrage steht davor und liegt beim Eigentümer.** Was bedeutet `gedeckt` als Liste? Eine Liste gedeckter Eigenschaften **ohne** Begründung ist eine plausible Lesart des Feldnamens — das Modell hat nicht zufällig Unsinn geliefert. Soll sie zugelassen werden, ist der Normalisierer eine **Umformung** (Namen → `{name: ""}`); soll sie nicht, verwirft er wie die drei anderen.~~ → **Entschieden vom Eigentümer am 13.09.2026:** Eine Eigenschaft ist gedeckt, wenn sie einen Wert hat; **ohne Wert ist sie offen.** Nichts wird verworfen, was eine Aussage trägt. Eine Liste gedeckter Namen wird damit nicht zu `{name: ""}`, sondern zu offenen Eigenschaften.

**Was fertig wäre:** Beide Felder haben einen Normalisierer in `_validate_artifact`, je mit Zeugen für die richtige Form, die falsche Form und den Leerfall; die sechs Lesestellen sind gegen den Rückbau bezeugt; ein Betriebsturn mit akutem Objekt läuft durch.

**Priorität.** Hoch — er kostet Turns vollständig, und drei weitere Stellen erzeugen lautlos falsche Eingaben für Verfasser und Rückfrage.

**Klasse.** Dieselbe wie `EI-KANON-FEHLT`: Modellwerte ungeprüft in den State und in eine dauerhafte Quelle.

**Behebung (13.09.2026).** Ein eigenes Modul statt zweier weiterer Normalisierer, weil die Form aller Objektfelder zusammenhängt: `graph/nodes/sachlage_form.py`.

- **`normalize_object_form`**: `gedeckt` wird eine Zuordnung Text → Text mit Wert — ein Name ohne Wert wandert nach `offen`, eine Zahl wird Text, ein strukturierter Wert ist keiner; `offen` eine Liste ohne Dubletten und ohne Gedecktes — ein Wert unter `offen` wandert nach `gedeckt`; `akut` ein Wahrheitswert (`"false"` ist falsch, eine unlesbare Form latent); `klasse` im Kanon oder entfernt. Jede Abweichung wird laut benannt.
- **Die Felder des Servers** (`quellen`, `plausibilitaet`, `recherche`) werden aus dem frischen Parse entfernt; an der vorigen Blase bleiben sie, auf ihre Form gehalten. Die Prompt-Ansicht der vorigen Blase trägt alle drei nicht mehr (vorher fehlte nur `quellen`).
- **`_validate_artifact`** prüft die Kopffelder auf Text (eine Zahl wird Text, sonst verworfen) und ruft `_validate_objects`: Name nicht leer, Form, Zusammenführen, dann Träger, Kritikalität, Sprecher gegen die bereinigten Felder.
- **`sachlage_load`** hält die vorige Blase durch dieselbe Prüfung; ohne Objektliste oder mit unlesbarem Objekt beginnt die Sachlage laut frisch.
- **`api/drive.py::sachlage_lesen`** bringt die Objekte für den Gesprächskontext-Tab auf dieselbe Form.
- **Aus der Messung dazu:** Kanonwörter (`nutzer`, `nova`, `welt`, `nachschlagen`, `kritisch`, `unkritisch`) und die Vorlage `nutzer|nova` sind kein Wert; eine Angabe im Namen mit Sprecherwort im Wert wird geborgen (`"Temperatur: 2,725 Kelvin": "nutzer"` → `Temperatur` → `2,725 Kelvin`, Sprecher `nutzer`); gleichnamige Objekte werden zusammengeführt (`merge_same_name_objects`), und die Smalltalk-Schranke sitzt seither hinter dem Zusammenführen.

**Gegen *Was fertig wäre* gehalten:** Die Normalisierung sitzt nicht in `_validate_artifact` selbst, sondern im Formmodul, das es ruft. Richtige Form, falsche Form (Liste, Dict unter `offen`, einzelner Text, Nicht-Text) und Leerfall sind bezeugt. **Die Lesestellen sind am Fall vom 12.09. bezeugt** — Plausibilität, Auflöser samt `carry_sources` und Block laufen mit dem geprüften Artefakt aus einer `gedeckt`-Liste —, nicht jede der sechs einzeln gegen den Rückbau. Die zwei lokalen Riegel (`sachlage.py`, heute Zeilen 633 und 685) stehen weiter; sie sind überflüssig, nicht schädlich, und wurden nicht im Vorbeigehen entfernt. Ein Betriebsturn mit akutem Objekt läuft durch (Messung unten).

**Zeugen.** `tests/test_sachlage_form.py`: **29**, nach der zweiten Kontrolle **31** (Nachtrag unten) (24 beim Bau, 5 aus der Messung — Kanonwort, Kanon-Menge gegen die drei Kanons, Vorlage, Bergung aus dem Namen, Zusammenführen); dazu ein Zeuge der Wert-Regel im Prompt (`test_sachlage.py`). Rote Phase gegen eine leere Hülle **20 vorhergesagt, 20 rot**; die Zeugen der Nachbesserungen waren vor ihrem Fix rot (Kanonwort 1/1, Vorlage 1/1, Bergung 1/1, Zusammenführen samt wörtlichem Rückwegwert 3/3). Sachlage-Zeugen beim Bau 209 grün, Suite am Ende des Umbaus **3656 grün, 0 übersprungen** (nach der zweiten Kontrolle 3663); harte Wand sauber.

**Gegenproben.** Formaufruf in `_validate_objects` entfernt → **18 vorhergesagt, 18 rot** (17 neue und der Bestandszeuge `test_latentes_objekt_verliert_offene_eigenschaften`); Prüfung beim Laden entfernt → 1/1; Zusammenführen entfernt → **1 vorhergesagt, 3 rot** (die Smalltalk-Schranke liegt im Zusammenführen — die Kopplung war übersehen); Schranke im Zusammenführen entfernt → 2/2; Bergung, Vorlage je 1/1.

**Gemessen am 13.09.2026.** **Labor** (echter Sachlage-Knoten mit echtem Modell, Laborpaar, 3 Läufe mit Wiederaufnahme, 3 ohne, 4 im Nachlauf): **0 Abstürze**; die Regel *ohne Wert → offen* griff zweimal an echten Parses (*Entfernung zur Erde* ohne Wert), und der Lauf fand die zwei Formen, die jetzt Regeln sind — `"Entfernung zur Erde": "nachschlagen"` in `gedeckt` und zwei Objekte gleichen Namens. **Betrieb, 14:47–14:52 UTC:** zwei Wissenschaftsturns zum Crab-Pulsar über `/chat` liefen mit akutem Objekt durch, Sachlage gerechnet und abgelegt. **Wechselmessung am rohen Parse** (sechs Zweierfolgen synthetischer Wissenschaftsreize, ~~vier~~ **fünf** Durchgänge je Fassung): gedeckte Werte ohne Angabe **31 von 70 (44 %) → 6 von 61 (10 %)**, kein Kanonwort mehr, die sechs leeren ordnet die Form als offen ein. Details: `novaberg-thinking-lage_k.md` §4, Scheibe 11.

**Nachtrag 13.09.2026, 15:55 UTC — die zweite Kontrolle fand zwei Lücken in der Form, die kein Zeuge sah.** Geprüft nach dem Bau, mit einem Zugriff, den der Bau nicht benutzt hatte, bei grüner Suite:

- **Der Vergleichsschlüssel war nicht der der Datenbank.** `property_key` schrieb mit `lower`, `sachlage_properties.text_key` mit `casefold`. *»Weißer Zwerg«* und *»WEISSER ZWERG«* blieben in der Form zwei Objekte, und zwei Schreibweisen derselben Eigenschaft (*Größe*, *Grösse*) lösten einander in der Datenbank im selben Turn ab. Seither `casefold`; die Schlüssel in `gedeckt` und beim Zusammenführen werden darüber entdoppelt, die Ablage entdoppelt je Objekt.
- **Ein zweiter Schreiber nach `gedeckt` lief an der Wertprüfung vorbei.** Der Frame-Auflöser setzte seine Ansprüche nach der Form in `gedeckt` — ein Anspruch `nutzer` stand dort, obwohl die Form ihn verwirft. Seither ist der Wertprüfer öffentlich (`covered_value`) und hält jeden Anspruch; ohne Wert wird er verworfen, die Eigenschaft bleibt offen. **Die Formprüfung gilt damit für jeden Schreiber, nicht nur für den Parse.**

Dritter Befund derselben Kontrolle, nicht die Form: Ein gespeicherter Wert deckte eine fremde Eigenschaft wörtlich (Scheibe 11, `novaberg-thinking-lage_k.md` §4). Zeugen der Form nach der Kontrolle **31** (zwei zum ß); die Gegenprobe am `casefold`-Schlüssel ergab zuerst **0 rot bei 1 vorhergesagtem** — der Zeuge prüfte die falsche Richtung, weil *WEISSER* unter `lower` und `casefold` gleich wird —, umgedreht 1/1. Suite **3663 grün, 0 übersprungen**.

---

## 12.09.2026, spaet — eine offene Frage, die jede fremde Antwort verdaechtig machte

Ein Eintrag, **am Tag seines Befundes behoben**. Gefunden hat ihn keine Pruefung, sondern der
Eigentuemer: 16 Warnungen an Antworten, die inhaltlich stimmten.

### `ZUORDNUNG-ANDERER-ABSENDER-FREMD` — eine Antwort an einen anderen Absender gilt bei offener Frage als falsch zugeordnet
**Kategorie:** ANT

**Zustand:** ✅ **behoben am 12.09.2026**, am Tag seines Befundes. `client/ui/stream_handler.py`: Der Handler fuehrt neben der offenen Menge die Menge aller Kennungen, die er je bestaetigt bekam (`_gesendete_nachrichten`, gefuellt in der SSE-Bestaetigung). Nennt eine Antwort nur Kennungen, die nicht darin stehen, ist sie `unbeobachtet` — auch bei offener Frage — und laesst die offene Frage stehen.

**Symptom.** Der Desktop-Client zeigte **16-mal** *„Diese Antwort gehoert nicht zu deiner letzten Nachricht. Sie blieb unbeantwortet."* an Antworten, die jede zu ihrem Reiz passten.

**Ursache, am Server-Log gemessen.** Um 18:55:04 UTC nahm der Server eine Desktop-Nachricht an; ihr Turn brach um 18:55:29 ab (`AttributeError`, der Blocker `LAGE-FORMPRUEFUNG-UNVOLLSTAENDIG`) und stellte nichts zu. Ihre Kennung blieb im Client offen. Zwischen 20:58 und 21:44 UTC liefen **16 Turns ueber `POST /chat`** von einem anderen Absender; der Server stellt jede Antwort allen Clients des Nutzers zu, mit den Kennungen **ihres** Absenders. `_zuordnung_pruefen` kannte nur zwei Faelle bei offener Frage — *genannte Kennung ist offen* oder *alles andere* — und *alles andere* hiess `fremd`. **Die Absicht stand im Kanon seit dem 01.08.2026** (`unbeobachtet` = *Antwort auf einen anderen Client*, siehe `ANTWORT-OHNE-ZUORDNUNG`), der Code hielt sie nur ohne offene Frage.

**Was `fremd` bleibt.** Eine Antwort **ohne** Kennung bei offener Frage, und ein Nachzuegler zu einer **eigenen**, schon beantworteten Frage — beides ist hier nicht als passend nachweisbar.

**Zeugen.** `client/tests/test_stream_assignment.py`, 5 neue, davon 4 durch die beiden Eingaenge des Clients (SSE-Bestaetigung, WebSocket-Nachricht) statt durch gesetzte Mengen; einer faehrt den gemessenen Ablauf nach (eine offene Frage, 16 Antworten an einen anderen Absender). Client-Lauf **28 grün** (vorher 23), Server-Suite **3586 grün, 0 übersprungen**. **Gegenprobe zweifach:** neuer Zweig abgeschaltet — 3 vorhergesagt, 3 rot; Vermerk in der Bestaetigung entfernt — 1 vorhergesagt, 1 rot.

**Gemessen am 12.09.2026, 22:50–22:53 UTC** mit dem echten `StreamHandler` gegen den laufenden Server: Reiz A ueber `POST /chat`, Reiz B ueber den Handler. Die Antwort auf A traf ein, **waehrend B offen war** (aufgezeichnet) → `unbeobachtet`; die Antwort auf B → `passt`. **Dieselben aufgezeichneten Eingaenge durch den Handler aus HEAD:** A → `fremd`, B → `passt`. Pixie pausiert, keine Seiteneffekte (timeline, notizen, fakten, ziele, wissensluecken unveraendert).

**Nicht mit behoben:** Die Meldung `turn_gescheitert` traegt keine `nachrichten_ids`, und der Client raeumt bei ihr nichts ab — die Kennung einer gescheiterten Nachricht bleibt bis zum Neustart offen. Seit der Behebung kostet das keine falsche Warnung mehr; es steht in der Fundliste.

**Nachtrag 12.09.2026, 23:22 UTC — der Rest ist fuer den gemeldeten Ausfall behoben.** `event_consumer.py` legt `nachrichten_ids` in `turn_gescheitert`, `StreamHandler._release_failed` nimmt sie aus der offenen Menge; eine Ausfallmeldung, die nur fremde Kennungen nennt, laesst die eigene Frage stehen. Server-Zeuge `test_der_ausfall_nennt_die_nachrichten_des_turns` (vorher rot, KeyError), Client-Zeugen 30 grün, Gegenprobe am Client 1/1. **Nicht gemessen:** Ein echter Ausfall laesst sich nicht gezielt herstellen; der Beleg ist die naechste Zeile *„gescheiterter Turn — nicht mehr offen"* im Client-Log. Fuenf Wege ohne jede Meldung stehen in der Fundliste.

---

## 25.08.2026 — eine fertige Antwort wartete auf Felder, die niemand liest

#### `AUSLIEFERUNG-HINTER-DEM-NACHLAUF` — jeder Fehler nach dem Responder kostet die fertige Antwort ✅
**Kategorie:** ANT

**Zustand:** **behoben am 25.08.2026**, am Tag des Befundes. Suite **2312 gruen / 0 uebersprungen**, elf neue Zeugen in `tests/test_antwort_ueberlebt_nachlauf.py` und `tests/test_ausgabe_bei_freigabe.py`.

**In drei Stufen gebaut, und die ersten beiden wirken unabhaengig von der dritten:**

**1 — Der Zwischenstand ueberlebt die Ausnahme.** `_graph_streamen` fuehrte ohnehin einen `letzter_state` mit; er ging nur verloren, weil die Ausnahme die Funktion verliess, bevor jemand ihn las. Er liegt jetzt in einem Traeger, der die Ausnahme uebersteht, und kommt mit `lauf_unvollstaendig` und dem Fehlertext zurueck. **Gerettet wird die Antwort, nicht der Fehler** — der Traceback steht wie bisher.

**2 — Kein stiller Ausfall mehr.** Wo bisher nur eine Serverzeile stand, geht eine Meldung an den Client: Typ `turn_gescheitert`, mit eigenem Zweig im Client, damit ein Ausfall nicht als Aeusserung Novas erscheint. **Ein bestehender Zeuge musste dafuer umgedreht werden** — `test_ohne_antwort_wird_nichts_zugestellt` sicherte genau die Stille zu, um die es ging (`20_TESTS/zusicherung-umdrehen.md`).

**3 — Die Antwort geht bei der Freigabe raus, nicht am Ende.** Signal ist der erste Knoten nach der Weiche (`perzeption_assistant`): Die Freigabe faellt in einer Kante, und Kanten erscheinen nicht im Stream. Ueber `output` **und** `fallback` fuehrt der Weg dorthin — also genau auf den beiden Wegen, auf denen ausgegeben werden soll. **Der Nachlauf laeuft unveraendert weiter**, er schreibt Novas Zustand, die Salienz und das Gedaechtnis; nur wartet niemand mehr darauf.

**Was den Zuschnitt entschieden hat, war eine Messung am Client:** Von den acht Zustandsfeldern der Nutzlast liest er **sieben gar nicht**. Einzig `momentum` wird angezeigt (`client/ui/main_window.py:392`), und das steht schon vor dem Responder. Eine zweite Nachricht fuer ein Zustandsbild, das niemand liest, waere Aufwand ohne Wirkung gewesen.

**Zwei Riegel gegen die naheliegende Ueberdehnung**, beide bezeugt: Ein Abbruch **vor** der Freigabe stellt nichts zu — wer frueher sendet, sendet irgendwann einen Text, den Thinker und Tribunal nie gesehen haben. Und gesendet wird **genau einmal**; die vier Nachlaufknoten loesen keine vier Zustellungen aus.

**Dabei kam die Nachvollziehbarkeit dazu**, die der Auftraggeber verlangt hat und die `18_NACHVOLLZIEHBARKEIT.md` §3 laengst fordert:

- **Die Weiche nennt ihre Eingangsgroessen**, bevor sie entscheidet: `verdict`, `correction_round`, `max_corrections`.
- **Sie liest sie mit `.get()` statt `[...]`.** Ein fehlendes `tribunal_verdict` warf einen `KeyError` in einer **Kante** — der Graph erreichte END nicht, und nirgends stand, welcher Wert gefehlt hatte. Jetzt wird er benannt und der Lauf faellt auf den Rueckfall.
- **Die Nutzlast meldet ihre Feldbelegung:** wie viele der acht Felder gefuellt waren und welche leer.

**Symptom.** In `services/event_consumer.py` steht die Auslieferung **hinter** dem vollstaendigen Graphenlauf:

```python
try:
    result: dict = await asyncio.to_thread(_graph_streamen, ...)   # :606
except Exception as fehler:
    logger.exception(f"...: Event-Consumer: Graph-Fehler")
    return                       # ← ueberspringt die Sendestelle
finally:
    llm_lock.release()

# ── Antwort per WebSocket senden ──                                # :617 ff.
```

**Was nach dem Responder noch laeuft, ist Nachlaufarbeit:** Tribunal, Perzeption, EI-Berechnung, Salienz, KZG-Schreibung. Sie bewerten, was der Turn fuer das Gedaechtnis wert ist. **Mit der Antwort an den Nutzer hat davon nichts zu tun** — und trotzdem entscheidet jeder dieser Knoten darueber, ob sie ankommt.

**Am 25.08.2026 belegt:** Die Antwort war um 13:33:07 erzeugt und um 13:33:18 vom Tribunal angenommen. Der Abbruch kam um 13:33:24 aus der Salienz — **siebzehn Sekunden nach der fertigen Antwort und aus einem Knoten, der sie nicht mehr veraendert.** Der Nutzer sah nichts; das Log meldete korrekt *Turn beendet, die Eingabe ist wieder frei*.

**Die Klasse ist groesser als der Ausloeser.** `TOKENZAEHLUNG-REISST-DEN-GRAPHEN` ist ein Fehler, der behoben wird; diese Reihenfolge bleibt danach. **Solange die Auslieferung am Ende steht, ist jede kuenftige Ausnahme im Nachlauf eine verlorene Antwort** — und die Nachlaufknoten sind die, an denen am haeufigsten gebaut wird.

**Geschlossen, wenn** ~~Eine vom Tribunal angenommene Antwort erreicht den Nutzer unabhaengig davon, ob der Nachlauf durchlaeuft.~~ **Erfuellt am 25.08.2026** — dreifach: sie geht bei der Freigabe raus, sie ueberlebt einen Abbruch danach, und ein Ausfall meldet sich.

**Prioritaet:** hoch.

---

## 25.08.2026 — der Versionsstempel frass die Leerzeile unter sich

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### TELEGRAM-SHADOW-TYP-TOT — der Bot behandelt einen Nachrichtentyp, den der Server nie erzeugt ⚠️
**Kategorie:** ANT

**Entdeckt:** Chat 110, beim Rückbau der Shadow-Delivery.

**Klasse:** Toter Zweig nach Architekturwechsel. Severity **niedrig**.

**Symptom:** `telegram_bot/bot.py:137` verzweigt auf `elif typ == "shadow_delivery":`, dokumentiert im Modulkopf (`:6`, `:105`). Ein solcher Nachrichtentyp wird vom Server **nirgends** erzeugt — auch vor Chat 110 hieß der Broadcast `shadow_impuls`. Der Zweig war also nie erreichbar.

**Beleg:** `grep -rn "shadow_delivery" --include='*.py'` außerhalb des Delivery-Moduls selbst → nur Bot und Importe.

**Nebenwirkung des Umbaus, positiv:** Novas Impulse erreichen Telegram jetzt **zum ersten Mal** — sie laufen als regulärer `character_response`, den der Bot seit jeher behandelt.

**Zustand:** **gegenstandslos seit dem 24.08.2026** — der Telegram-Kanal ist abgeschaltet. Der tote Zweig steht unveraendert in `telegram_bot/bot.py`; er wird nur nicht mehr ausgefuehrt. **Nicht behoben, sondern ohne Gegenstand** — wer den Kanal zurueckholt, holt ihn mit. Davor: Offen — Zweig entfernen oder Kommentar korrigieren.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `RESPONDER-ERFINDET-DATUM` — ein erfundenes Datum in der Bestaetigung
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `635dbfd` gehalten am 22.08.2026. Die Abhilfe sitzt in der **Ausgabe-Verifikation**, nicht im Prompt: Der Widerspruch Wochentag↔Datum lief seit dem 20.08.2026 (`utils/datum_pruefung.py::widersprueche_finden`, gerufen in `graph/nodes/tribunal.py`), **die zweite Haelfte ist am 22.08.2026 dazugekommen** — `bestaetigung_pruefen` haelt die Datumsangaben der Antwort gegen die der erfolgreichen Dienstergebnisse. Beide heben das Urteil auf `warnung` und damit in die Korrekturrunde.

> **Die Luecke war gemessen, nicht vermutet:** Derselbe Originalsatz **ohne** Wochentag (*„am 20.08. um 14 Uhr"*) ergab 0 Befunde — die erste Pruefung braucht das Paar.
>
> **Am Bestand belegt** (22.08.2026, `labor/2026-08-22_bestaetigung_bestand*`): 5 Turns, in denen ein Dienst ein Datum meldete, alle fuenf pruefbar — **1 Anschlag, und das ist genau der Fall vom 17.08.2026**; die vier anderen echten Terminbestaetigungen bleiben still. 16 Zeugen (`tests/test_datum_bestaetigung.py`), Gegenprobe 1 vorhergesagt / 1 gezaehlt, Suite `Ran 2083 tests — OK`.
>
> **Der Rest ist benannt und gehoert nicht zu diesem Eintrag:** Ob die Korrekturrunde die Antwort danach richtig macht, ist nicht nachgemessen. Belegt ist, dass der Auftrag im `tribunal_summary` steht — dort, wo der Corrector ihn liest. Und fuenf Faelle sind keine Rate: Die Aussage lautet *„an allem, was da ist, trennt sie richtig"*.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Der Responder erfindet das Datum in einer Termin-Bestaetigung.** Der Agent lieferte `"Termin 'Meeting mit dem Chef' eingetragen fuer 19.08.2026 14:00"`, die Tabelle traegt `19.08.2026 12:00 UTC` (= 14:00 lokal, Mittwoch) — beides richtig. Novas Antwort um 11:31 lautet *„Mittwoch, **20.08.**, 14:00 Uhr"*. **Der Satz widerspricht sich selbst:** Der 20.08.2026 ist ein Donnerstag. Die Zahl stand in keiner Eingabe des Responders; der Erfolgsblock trug das korrekte Datum. Folge in derselben Sitzung: Der Mensch sucht den Termin am falschen Tag, findet ihn nicht, und haelt den Schreibpfad fuer defekt — er war es nie. **Eine falsche Bestaetigung ist teurer als eine fehlende**, weil sie geglaubt wird.

**Geschlossen, wenn** Der Responder nennt in einer Bestaetigung nur Daten, die im Zustand stehen.

---

### `ROUTERPROMPT-ZWEIFEL-WIDERSPRUCH` — zwei Regeln, entgegengesetzt
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. der zweite Satz ist fort: *als passend* kommt im ganzen Serverbaum nicht mehr vor; ueber den Zweifel steht nur noch `prompts/default/router.task.txt:62`.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Zwei Regeln im Router-Prompt sprechen entgegengesetzt ueber den Zweifel.** `prompts/default/router.task.txt:62` sagt *„Im Zweifel: kein Dispatch."*; der `[AGENTEN]`-Block sagt seit dem 17.08.2026 *„Kannst du bei einem Aushang nicht klar entscheiden, gilt er als passend."* Der Guard steht im Prompt **vor** dem Brett. Beide Saetze sind je fuer sich begruendet — der Guard gegen den Dispatch auf blosse Themen-Erwaehnung, das Brett gegen die ausgebliebene Zustellung. **Die Ungleichbehandlung von Lesen und Schreiben ist die naheliegende Aufloesung und ausdruecklich nicht entschieden:** Ein ueberfluessiges Lesen endet in einer Auskunft, ein ausgebliebenes in einer Behauptung. Eine Aenderung am Guard wurde am 17.08.2026 gebaut und **wieder zurueckgebaut**, weil sie auf einer Fehldiagnose stand (ein Prompt-Schema im Log war als Router-Entscheidung gelesen worden) und keine Messung ihren Nutzen belegte.

**Geschlossen, wenn** Der Router-Prompt sagt ueber den Zweifel eine Sache.

---

### `VERFASSER-ORDNET-IMPULS-PERSON-B-ZU` — der eigene Gedanke wird dem Gegenueber zugeschrieben
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `383d7e1` gehalten am 22.08.2026. **Und zwar seit dem 14.08.2026, dem Tag des Befunds selbst** (`b8abd82`, `e755b84`): `graph/nodes/verfasser.py` haengt bei `reiz_ist_eigener_gedanke(state)` den Auftrag `verfasser.auftrag_ohne_reiz` an statt des Reizes; der Gedanke steht als Material im System-Prompt. Erkannt wird an `event_payload["reiz_herkunft"] == "eigener_impuls"` — **an der Herkunft, nicht an der Rolle**, also genau die Schlussbedingung. Zeugen: `tests/test_verfasser_herkunft.py`. Im Betrieb belegt: Der Auftragstext steht **33-mal** im Log.

> **Der Zustand vom 20.08.2026 war falsch, und wie er es wurde, ist der Ertrag dieses Eintrags.** Er nannte `verfasser.py:405` und schrieb *„haengt den Reiz weiter als `user`-Nachricht an"*. Auf Zeile 405 steht genau das — `messages.append({"role": "user", "content": reiz})`. **Es ist der `elif`-Zweig.** Die Bedingung, die diesen Fall ausschliesst, steht vier Zeilen darueber.
>
> **Eine Zeilennummer, die auf einen Zweig zeigt, ist ohne ihre Bedingung kein Befund** — sie sieht aus wie einer, und sie laesst sich zitieren. Der Eintrag stand danach acht Tage als offen, obwohl er am Tag seiner Entstehung geschlossen worden war.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Der Verfasser schreibt Novas eigenen Gedanken der Person B zu, solange er ihn in der Rolle des Gegenuebers bekommt.** Messturn `065a5d5f` um 19:15 UTC, ein Gedanke ueber Rotationskurven von Spiralgalaxien: *„PERSON B stellt die physikalische Beobachtung der flachen Rotationskurven … "* — Person B ist der Mensch, der in diesem Turn nichts gesagt hat. **Der Reiz-Platz war dabei bereits leer**; der Gedanke kam ueber den eigenen Kanal und wurde nur weiterhin als `user`-Nachricht angehaengt. Das ist der Beleg fuer die tragende Aussage des Konzepts — die Rollenzuweisung ist die Ursache, nicht die Formulierung — und zugleich die Messgrundlage fuer den Materialblock, der noch nicht gebaut ist.

**Geschlossen, wenn** Der Verfasser erkennt den eigenen Gedanken an seiner Herkunft, nicht an der Rolle.

---

### `FRAGEN-ZEILE-OHNE-BEDINGUNG` — eine Zeile, auf die nichts zeigt
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `387915f` gehalten am 22.08.2026. Die Zeile ist entfallen, und zwar aus demselben Grund wie im Responder am 13.08.2026: **Dieselbe Aussage kommt aus der Haltungsgroesse `fragen`, charakterabhaengig statt fuer jede Nova gleich.** Sie erreicht den Verfasser als Rueckfrage-Zeile des `[MASS]`-Blocks, seit dieser am 20.08.2026 dazukam. Die Tabelle `CLUSTER_FRAGEN` bleibt — der GV-Knoten braucht sie fuer die Strategiewahl, und die Haltungsgroesse ist aus ihr uebersetzt (`ei/haltung.py`). Drei Zeugen auf die **Abwesenheit** (`tests/test_verfasser_gv_block.py`), Gegenprobe 2 vorhergesagt / 2 gezaehlt, Suite `Ran 2090 tests — OK`.

> **Der Befund vom 14.08.2026 nannte sie Zierat. Seit dem 20.08.2026 war sie mehr als das**, und die Messung zeigt es: In **15** Verfasser-Prompts des Betriebslogs standen beide Angaben nebeneinander, und in **11 davon waren sie uneinig** — die rohe Zeile sagte *„Selten, behutsam"* oder *„Selten (jeder 3.-4. Turn)"*, waehrend die Vorgabe daneben *„eine Rueckfrage"* verlangte. Zwei Stimmen im selben Prompt, in drei Vierteln der Faelle gegenlaeufig (`labor/2026-08-22_fragenfrequenz_doppelt.py`).
>
> **Nicht gemessen ist, ob das Modell deshalb anders antwortete.** Belegt ist, dass beide Stimmen dastanden, nicht welche es befolgte.
>
> **Die Absichtsfrage des Eintrags — ob die Fragenfrequenz zum Inhalt gehoert — ist damit nicht neu entschieden worden.** Sie war am 13.08.2026 entschieden; der Verfasser wurde nur nie nachgezogen, weil sein `[MASS]`-Block erst eine Woche spaeter kam.

**Befund (14.08.2026), aus der Fundliste uebernommen.** **Die Zeile `Fragen:` im Verfasser-Block hat keine Bedingung, die auf sie zeigt.** Der Block trägt `CLUSTER_FRAGEN` der Landschaft (*„Mittel, neckisch, oft rhetorisch"*), aber keine der drei Prüfbedingungen des Auftrags verlangt etwas davon; das Vehikel aus der Dreischicht sagt bereits, ob gefragt wird. Ein Block, den der Auftrag nicht einführt, ist Zierat — und wird beim Messen fälschlich als wirkungslos verbucht, obwohl nur seine Einführung fehlt. Im Responder ist dieselbe Quelle am 13.08.2026 als Doppelung entfallen. **Nicht entfernt:** Ob die Fragenfrequenz zum Inhalt gehört, ist eine Entscheidung und keine Aufräumarbeit.

**Geschlossen, wenn** Die Zeile `Fragen:` hat eine Bedingung oder entfaellt.

---

### `NUTZERKERN-ERREICHT-RESPONDER-NICHT` — gerechnet und nicht zugestellt
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `graph/nodes/responder.py:316-334` setzt den Block `[PERSON B — WER ER IST]` aus `external.character.core`, dazu das Adaptive; sein Fehlen wird gemeldet.

**Befund (12.08.2026), aus der Fundliste uebernommen.** **Der Kern des Nutzers erreicht den Responder nicht.** Von Nova gehen alle fünf Profile in den Prompt (`core`, `adaptive`, `emotions`, `intentions`, `relationship`); vom Nutzer geht **eines** hinein, sein Beziehungsprofil. Sein Wesen, seine Denkart, seine Interessen kommen im Prompt nicht vor — auch nicht, seit die offene Destillation daraus 5295 Zeichen macht. Im Code steht keine Begründung für die Asymmetrie.

**Geschlossen, wenn** Der Kern des Nutzers erreicht den Responder.

---

### `BEZIEHUNGSPROFILE-UNBESCHRIFTET` — zwei Profile ohne Perspektivangabe
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `graph/nodes/responder.py:412-415` beschriftet beide nach dem Paar-Schema — *So sieht Person A ihr Gegenueber* / *So sieht Person B sie*.

**Befund (12.08.2026), aus der Fundliste uebernommen.** Die beiden Beziehungsprofile stehen **unbeschriftet** im Responder-Prompt. Novas trägt „So siehst du deinen Nutzer", das des Nutzers trägt „Langzeit-Beziehungsprofil" — ohne Angabe, aus wessen Sicht. Nach dem Paar-Schema ist es *seine* Sicht auf *sie*; im Prompt liest es sich wie eine Anweisung an sie.

**Geschlossen, wenn** Jedes Beziehungsprofil im Prompt nennt, aus wessen Sicht es geschrieben ist (Paar-Schema).

---

### `RESPONDER-ANWEISUNG-DOPPELT` — dieselbe Anweisung aus zwei Quellen
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. die zweite Quelle beschreibt statt anzuweisen (`graph/nodes/responder.py:532-547`); ein Zeuge haelt es (`tests/test_responder_drehbuch.py:203`).

**Befund (12.08.2026), aus der Fundliste uebernommen.** Eine Anweisung steht im Responder-Prompt **doppelt**: *„Der Nutzer öffnet sich. Du darfst persönlicher werden."* kommt einmal aus der EI-Mikroanweisung (`_ei_mikro_anweisung`, Zweig Beziehungsdynamik) und einmal als eigene Zeile „Beziehungsdynamik" weiter unten. Zwei Quellen, derselbe Satz, keine weiß von der anderen.

**Geschlossen, wenn** Jede Anweisung steht einmal im Responder-Prompt.

---

### `FARBTON-ERREICHT-RESPONDER-NICHT` — jeden Turn gerechnet, nie zugestellt
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `graph/nodes/responder.py:207,219` nimmt den Farbton aus `gv_detail` in die Szene.

**Befund (12.08.2026), aus der Fundliste uebernommen.** **Der Farbton wird in jedem Turn gerechnet und erreicht den Responder nicht.** `ei/farbton.py` mischt acht Dimensionen zu 2–5 Sätzen, die „dem LLM die emotionale und kognitive Landschaft beschreiben, ohne Handlungsanweisungen" (Docstring). Er geht als `[SITUATION]`-Block in den **Gesprächsvektor**-Prompt und ins Log; der Knoten, der die Antwort schreibt, sieht ihn nie. Dritter Kanal dieser Art nach der Haltung und den Speichen. Dazu: Sind alle acht Dimensionen unauffällig, bleibt ein einziger Satz übrig — dreimal hintereinander „Das Gespraech ist ruhig und ausgeglichen".

**Geschlossen, wenn** Der Farbton erreicht den Responder oder wird nicht mehr gerechnet.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Chat 138 — aus einem Tag Betrieb nach dem Umbau (14.08.2026)

#### RESUME-VERBRAUCHT-DEN-IMPULS — ein eigener Gedanke löscht die Rückfrage eines wartenden Agenten ✅ behoben (14.08.2026)
**Kategorie:** ANT

**Symptom.** Ein Agent stellt eine Rückfrage („Welche Notiz meinst du?"). Trifft innerhalb der fünf Minuten Wartezeit ein eigener Impuls ein, ist die Rückfrage danach weg — der Mensch bekommt keine Gelegenheit mehr zu antworten, und der Agent hat mit etwas gearbeitet, das niemand gesagt hat.

**Ursache.** Der Router setzt `management_action="resume"`, sobald ein `pending_agent:<kennung>`-Schlüssel existiert — **ohne die Herkunft des Reizes zu prüfen**. Ein Impuls-Turn läuft damit in `_handle_resume`, und dort wird der Wartezustand **vor** dem Agentenlauf gelöscht (ausdrücklich, gegen Endlosschleifen). Danach gibt es nichts mehr, worauf der Mensch antworten könnte.

**Die Fehlerwirkung hat sich am 14.08.2026 verschoben, nicht aufgelöst.** Vorher stand Novas Gedanke auf dem Reiz-Platz und wurde als Antwort des Menschen verarbeitet — eine falsche Antwort. Seit der Ablösung des Reiz-Platzes ist er dort leer, und der Agent bekommt eine **leere** Antwort. Beide Male ist die Rückfrage danach gelöscht. Der zweite Fall ist der bessere: Er erfindet keine Antwort. Er ist trotzdem ein Verlust, und er ist still — es gibt keine Meldung „Rückfrage von einem Impuls verbraucht".

**Warum es zählt.** Ein eigener Impuls **soll** handeln dürfen (entschieden am 14.08.2026, siehe `novaberg-backlog.md` → `IMPULS-LOEST-MANAGEMENT-AGENT-AUS`). Das ist etwas anderes, als in fremdem Namen zu antworten: Eine Rückfrage richtet sich an den Menschen, und ihre Beantwortung ist keine Handlung Novas, sondern eine an seiner Stelle.

**Reproduktion.** Einen Agenten in den Wartezustand bringen (eine mehrdeutige Notiz-Anfrage), dann innerhalb von 300 Sekunden einen Impuls zustellen lassen. `pending_agent:<kennung>` ist danach gelöscht, im Log steht `Resume-Flow — action='…', user_answer=''`.

**Nicht gemessen** ist, wie oft der Fall eintritt: Die Wartezeit beträgt 300 Sekunden, Impulse kommen etwa stündlich — das Fenster ist schmal, aber jeder Treffer kostet eine Rückfrage.

**Behoben am 14.08.2026, mit zwei Riegeln für zwei verschiedene Fragen.**

**Der Router entscheidet die Zuständigkeit:** Ein Reiz eigener Herkunft nimmt den Resume-Pfad nicht, der Wartezustand bleibt stehen, der Impuls nimmt seinen gewöhnlichen Weg. Das gilt unabhängig vom Zeitpunkt der Zustellung — auch ein Wiederholungsversuch trägt dieselbe Marke und käme ohne diesen Riegel auf demselben Weg herein.

**Die Zustellung entscheidet den Zeitpunkt:** Solange ein Agent wartet, wird kein Impuls zugestellt. Der Eintrag verfällt dabei nicht, er bleibt auf dem Stapel; die Wartezeit ist auf 300 Sekunden begrenzt. Die Prüfung steht **vor** dem Burst-Zähler, weil ein Zähler, der für einen unterdrückten Impuls hochliefe, die nächste Gelegenheit mit verbrauchte.

**Der zweite ersetzt den ersten nicht.** Wer nur den Zeitpunkt sichert, hat den Weg offen gelassen, auf dem ein Reiz eigener Herkunft ohne Zustellung ankommt.

Zeugen in `tests/test_impuls_und_rueckfrage.py`, beide Herkünfte je Riegel. Gegenprobe mit beiden Riegeln abgeschaltet: 4 rot. **Ein fünfter Zeuge war vorhergesagt und blieb grün** — er prüfte die nicht gelöschte Wartemarke, und gelöscht wird eine Schicht tiefer, wo der Router nie hinkommt. Er konnte nicht rot werden und ist ersetzt.

---

#### WEBSOCKET-OHNE-KEEPALIVE — die Verbindung stirbt im Leerlauf, und der Client merkt es nie ✅ behoben (15.08.2026)
**Kategorie:** ANT

**Symptom.** Der Client zeigt „denkt nach" und bekommt nie eine Antwort. Nachrichten des Nutzers gehen weiter ein und werden vollständig verarbeitet; die Antworten entstehen und werden gespeichert. Zugestellt wird nichts. Der Zustand hält an, bis der Client neu gestartet wird.

**Ursache.** Der Client ruft `run_forever(reconnect=…)` **ohne `ping_interval` und `ping_timeout`** auf; im ganzen Client gibt es kein Keepalive (`client/ui/stream_handler.py`). Eine im Leerlauf gestorbene Verbindung ist damit von einer stillen nicht zu unterscheiden: Der Server bekommt beim Senden einen Fehler und räumt die Verbindung weg, der Client bekommt nichts. `on_close` feuert nie, `run_forever` kehrt nie zurück — und die Wiederverbindungsschleife darum herum ist genau deshalb wirkungslos. Ihr eigener Kommentar sagt es: Sie fängt nur den Fall ab, *dass `run_forever` früh zurückkehrt*.

**Reproduktion.** Eine Verbindung aufbauen, sie ohne Verkehr liegen lassen, bis sie unterwegs abgeräumt wird, und dann eine Nachricht senden. Der Server meldet einmal `WebSocket-Send (threadsafe) fehlgeschlagen`, danach für jeden weiteren Turn `Kein WebSocket für '<Kennung>'`.

**Gemessen am 14.08.2026.** Zwei Verbindungen starben am selben Vormittag auf dieselbe Weise, 05:45:50 und 06:39:48, beide beim Senden nach einer Ruhephase — zwischen der letzten Zustellung und dem Bruch lagen 47 Minuten. Danach acht Stunden **kein einziger Handshake-Versuch**, obwohl der Client-Prozess durchgehend lief. In dieser Zeit entstanden zwei vollständige Antworten (730 und 261 Zeichen), die beide nur in der Session landeten.

**Ein zweiter Defekt daneben:** Die Meldung lautet `… fehlgeschlagen für '<Kennung>' (client=…): ` — nach dem Doppelpunkt steht nichts. Die Ausnahme wird protokolliert, ihr Text ist leer, ihr Typ wird nicht genannt. Zweimal an einem Tag, beide Male ohne rekonstruierbaren Grund.

**Nicht zu verwechseln mit `CLIENT-EINGABESPERRE-OHNE-RUECKWEG`** (Chat 124, behoben). Dort hing die Eingabesperre, hier fehlt der Kanal.

**Behoben am 15.08.2026 — und die Ursache oben ist dabei zur Hälfte widerlegt worden.**

Der Eintrag nennt als Ursache das fehlende Keepalive im Client und ordnet den leeren Fehlertext als „zweiten Defekt daneben" ein, *„ohne rekonstruierbaren Grund"*. Beides ist so nicht haltbar:

- **Der leere Text hat einen Grund.** Er stammt von `concurrent.futures.TimeoutError` — `str()` darauf ist die leere Zeichenkette. Die Meldung nennt jetzt den Ausnahmetyp, in beiden Broadcast-Funktionen und im Client.
- **Der Auslöser saß am Server, nicht am Client.** `broadcast_threadsafe` wartete mit `future.result(timeout=5.0)` auf eine Zustellung, die es in den Haupt-Loop eingestellt hatte, und wertete den Ablauf dieser Frist als Verbindungsfehler. Die Frist misst aber die Auslastung des Loops. Gemessen am 14.08.2026: Der Server verwarf die Verbindung um 22:24:24,992 — der Client protokollierte die **erfolgreiche** Zustellung derselben Nachricht um 22:24:25,015, 23 ms später. Dieselbe Abfolge um 21:19:56 und 22:02:43.
- **Ein Keepalive allein hätte diese Fälle nicht erfasst.** Der Server nahm die Verbindung aus der Liste, **ohne den Socket zu schließen**. Damit beantwortet die Protokollschicht weiterhin jeden Ping, während die Anwendung den Client nicht mehr kennt — für den Client ist die Leitung nach jedem Maßstab gesund, den er selbst anlegen kann. Am 14./15.08. blieb der Telegram-Client so **elfeinhalb Stunden** angeschlossen und stumm, obwohl er `ping_interval=30` fährt.

**Was gebaut wurde.** Serverseitig: Der Timeout wird eigens gefangen und verwirft nicht mehr; eine wirklich verworfene Verbindung wird geschlossen (`_socket_schliessen`); beide Meldungen nennen den Ausnahmetyp. Clientseitig: `run_forever` fährt `ping_interval=30`/`ping_timeout=10` (`WS_PING_INTERVAL`, `WS_PING_TIMEOUT` in `client/config.py`), und der Thread-Fehler wird mit Typ protokolliert. **Beide Hälften werden gebraucht** — die eine gegen die stumm abgeräumte Leitung, die andere gegen die wirklich gestorbene.

**Gegengemessen am 15.08.2026, 10:31:08 UTC:** `Antwort gesendet per WebSocket (588 Zeichen, 2 Clients)`, und eine Millisekunde später `[meister] Sende an Telegram: …`. Zuvor stand dort an diesem Tag durchgehend `1 Clients`.

**Nicht behoben:** `BROADCAST-VERSCHLUCKT-FEHLER` bleibt offen. `broadcast()` gibt dem Aufrufer weiterhin keinen Rückgabewert; die Zahl in „2 Clients" zählt die Verbindungen in der Liste, nicht die bestätigten Zustellungen.

**Geschlossen, wenn.** Der Client sendet ein Keepalive und erkennt eine halboffene Verbindung selbst; die Fehlermeldung nennt Typ und Text der Ausnahme. Offen bleibt dann noch, ob eine unzustellbare Antwort beim Wiederverbinden nachgereicht wird — das ist eine Entscheidung über das Zustellverhalten und kein Defekt.

---

### Chat 137 — aus dem Umbau des Responder-Prompts (13.08.2026)

#### VERFASSER-KENNT-DIE-QUELLE-NICHT — Novas eigener Impuls wird ihr als Nutzeräußerung zugeschrieben ✅ behoben (Chat 137)
**Kategorie:** ANT

**Symptom.** Nach einem eigenen Impuls antwortet Nova, als hätte der Nutzer gesagt, was sie selbst gedacht hat. Am 13.08.2026 im Betrieb beobachtet: *„Du hast das gerade nicht nur zitiert, du hast es als strukturellen Anker in den Raum geworfen."* — der zitierte Text stammte von ihr.

**Ursache.** Ein Pixie-Impuls reist als `user_prompt` durch den Graphen; dieselbe Stelle, an der sonst die Nutzereingabe steht. Der **Responder** unterscheidet das: `_reiz_ist_eigener_gedanke()` liest `event_payload["reiz_herkunft"]` und setzt den Block `[EIGENER GEDANKE]` — *„Was unten als Eingabe steht, hat dir niemand gesagt […] schreibe sie ihm nicht zu."* Der **Verfasser** hat diese Prüfung nicht: In `graph/nodes/verfasser.py` gibt es keinen Treffer für `reiz_herkunft`, `eigener_impuls` oder `event_payload`. Er liest den Impuls als Äußerung des Nutzers und schreibt den Inhalt entsprechend — belegt am selben Turn: *„**Du hast** hier die gesamte Architektur der Resonanz-Modellierung direkt in den Fokus gerückt."*

**Warum es zählt.** Der Responder hält sich an seinen Block — er dankt nicht und lobt nicht. Die Zuschreibung steckt trotzdem in der Antwort, weil sie schon im **Material** stand. Ein Schutz, der nur die zweite Stufe kennt, greift ins Leere, sobald die erste den Text schreibt. **Der Defekt ist mit der Trennung von Inhalt und Form entstanden:** Vorher formulierte der Responder selbst und hatte den Block; seit der Verfasser den Inhalt liefert, entscheidet eine Stufe über die Perspektive, die die Herkunft des Reizes nicht kennt.

**Reproduktion.** Einen Pixie-Impuls auslösen und den Verfasser-Prompt im Log ansehen: `[AKTUELLER PROMPT]` trägt Novas eigenen Text, und kein Block sagt, von wem er stammt.

**Geschlossen, wenn.** Der Verfasser dieselbe Unterscheidung trifft wie der Responder und sein Auftrag die Herkunft nennt.

**Wie groß es war — gemessen am 13.08.2026 über einen ganzen Tag.** Vierzehn Impulse, stündlich von 07:52 bis 20:59 UTC, alle mit `herkunft: eigener_impuls` in der Session gespeichert. **Dreizehn von vierzehn** begannen mit *„Du hast …"*, **fünf davon wortgleich** (*„Du hast den Anker geworfen. Indem du diesen Block …"*). Der Defekt war also nicht der Ausnahmefall, sondern der Regelfall — und die Information lag die ganze Zeit im Zustand.

**Behoben.** Die Prüfung liegt jetzt in `graph/reiz.py`, wo beide Stufen sie erreichen, statt privat im Responder. Der Verfasser bekommt einen `[HERKUNFT DES REIZES]`-Block in zwei Fassungen — bei eigenem Impuls mit dem wörtlichen Verbot der gemessenen Formulierung, beim Nutzer-Turn mit der Gegenaussage. Beide Fassungen sind nötig: Ein Prompt, der in jedem Fall denselben Satz trägt, bestünde einen Test, der nur eine Seite prüft. Sieben Zeugen in `tests/test_verfasser_herkunft.py`; Gegenprobe mit ignorierter Herkunft: 2 rot.

**Nachgetragen am 14.08.2026 — die Bedingung ist entfallen.** Der Defekt konnte entstehen, weil „der Nutzer" die einzige Adresse im Verfasser-Prompt war. Der Auftrag trägt seither die Konstellation aus Person A und Person B, und der Inhalt entsteht in **dritter Person**: „Du hast …" kann dort nicht mehr gebildet werden, weil es kein „du" gibt. Das Verbot bleibt trotzdem stehen und deckt jetzt auch die Zuschreibung in dritter Person — „Person B hat den Anker geworfen" wäre derselbe Fehler in neuer Kleidung.

**Was der Fix nicht behebt, und was daraus folgt.** Die fünf wortgleichen Anfänge stammen aus dem **Verlauf**, nicht aus der Herkunft: Jeder Impuls wird zum Verlauf, der nächste sieht zwanzig Turns eigener Prosa und schreibt die Wendung wieder. Der Verfasser-Prompt trug an diesem Tag 22.545 Zeichen Verlauf aus 18 eigenen Beiträgen gegen 1.195 Zeichen Auftrag. **Das ist ein eigener Gegenstand** und steht in der Fundliste. **Und die Klasse ist größer als dieser eine Fall:** Jeder Block, der den Responder gegen eine Verwechslung schützt, ist daraufhin zu prüfen, ob die erste Stufe ihn ebenfalls braucht.

---

### Leere Modellantwort (01.08.2026)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ANTWORT-OHNE-ZUORDNUNG — die nächste Antwort wird als Antwort auf die letzte Frage angezeigt ✅ **behoben am 01.08.2026 (Chat 124)**
**Kategorie:** ANT

**Behoben — die Zuordnung reist mit und wird geprüft.** Drei Stellen bilden die Kette: `api/chat.py → _bestaetigungs_nutzlast` gibt dem Client die `turn_id` seiner eigenen Nachricht, `services/event_consumer.py` legt die `turn_id` des Reizes in das `character_response`-Payload, und `client/ui/stream_handler.py → _zuordnung_pruefen` vergleicht beide.

**Die Kennung stammt aus dem Reiz, nicht aus dem Ergebnis-Zustand.** Beide liegen im selben Griffbereich, und der Zustand trägt dieselbe Kennung nur, solange sie unterwegs niemand überschreibt. Was der Client braucht, ist die Kennung **seiner Frage** — nicht die des Laufs, der geantwortet hat. Die Tests halten beide auf verschiedenen Werten, damit die falsche Quelle rot wird.

**Drei Ausgänge als deklarierter Kanon:** `passt` (die offene Frage ist beantwortet, die Kennung wird gelöscht), `fremd` (gehört zu einem anderen Reiz — die Antwort wird mit Vermerk angezeigt, die Frage bleibt offen), `unbeobachtet` (dieser Client hat keine offene Frage: Antwort auf einen anderen Client oder ein Nachzügler). **Eine Antwort ohne Kennung fällt bei offener Frage auf `fremd`** — „nicht nachweisbar" darf nicht aussehen wie „stimmt".

**Nachtrag 12.09.2026 — *Antwort auf einen anderen Client* galt nur ohne offene Frage.** War hier eine Frage offen, wurde jede Antwort an einen anderen Absender `fremd`. Behoben als `ZUORDNUNG-ANDERER-ABSENDER-FREMD` (oben in dieser Datei).

**Was ausdrücklich nicht geschieht:** Die Antwort wird nicht unterdrückt und die Eingabe nicht gesperrt. Der Inhalt ist echt, nur seine Stelle im Gespräch ist es nicht; ihn zu verschweigen wäre ein zweiter Verlust. Und ein **eigener Impuls** lässt die offene Frage stehen — er beantwortet sie nicht.

**Gemessen am 01.08.2026, 19:35 UTC** an einem echten Turn: Bestätigung und zugestellte Antwort trugen dieselbe `turn_id`. Gegenprobe zweifach — Zuordnung aus dem `character_response` entfernt: 5 rot; aus der Bestätigung entfernt: 3 rot.

**Was der Riegel nicht tut:** Er verhindert den Ausfall nicht. `RESPONDER-LEERE-ANTWORT-STILL` bleibt offen, und `RESPONDER-OHNE-INHALT-ANTWORTET-TROTZDEM` ebenso. Er macht die Folge sichtbar, statt sie zu einer falschen Aussage werden zu lassen.

Der ursprüngliche Befund:

**Die teuerste der drei Stufen, weil sie unsichtbar falsch ist.** Bleibt eine Antwort leer, hängt das Gespräch — und die Antwort des **nächsten** Turns wird beim Nutzer als Antwort auf seine unbeantwortete Nachricht angezeigt.

**Belegt am 01.08.2026:**

```
18:36:41  Haltungsraum — feuerwerk        ← die Nachricht des Nutzers
18:37:47  salienz: bewertungsobjekt_leer  ← Antwort leer, kein Rohturn
18:38:52  Haltungsraum — werkstatt        ← der naechste Turn beginnt
18:40:52  Rohturn, 4312 Zeichen Antwort   ← wird zugestellt
```

Der Nutzer sah eine flüssige, inhaltlich geschlossene Antwort — zu einem **Eigenimpuls über ein anderes Thema**. Seine eigene Frage war nie beantwortet worden.

**Ursache:** Die WebSocket-Zustellung trägt **keine Turn-Zuordnung**. Der Client kann nicht prüfen, zu welchem Reiz eine ankommende Antwort gehört, und ordnet sie der letzten Nachricht zu. Solange jeder Turn antwortet, stimmt das; sobald einer ausfällt, verschiebt sich alles um eins.

**Ein Hänger ist erkennbar. Eine falsch zugeordnete Antwort ist es nicht** — sie liest sich richtig, sie passt nur nicht zur Frage.

**Was zu tun ist:** Die Zustellung trägt die `turn_id` des Reizes, auf den sie antwortet. Der Client zeigt eine Antwort nur an der Stelle, zu der sie gehört, und macht eine unbeantwortete Nachricht als solche sichtbar. Additiv und ohne Verhaltensänderung — es macht prüfbar, was heute geraten wird.

**Priorität:** hoch. Der Verlust ist nicht der Turn, sondern das Vertrauen in jede Antwort nach einem Ausfall.

### Zeitparser und Chat-Endpunkt (Chat 120)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### CHAT-NAME-OHNE-ERZEUGER — beide Pfade des Chat-Endpunkts lesen eine Variable, die es nicht mehr gibt ✅ Gelöst Chat 120
**Kategorie:** ANT

**Gelöst am 31.07.2026.** Beide Pfade leiten den Wert wieder lokal aus dem State ab, den sie ohnehin halten.

**Entdeckt:** Chat 120, aus einem Bildschirmfoto des laufenden Betriebs — nicht aus einem Test.

**Symptom:** `Fehler: name 'letzter_external' is not defined` im Client, während Novas Antwort trotzdem ankam.

**Mechanismus:** Der Nutzlast-Aufbau wanderte am Vortag in eine gemeinsame Funktion, die ihre Ableitung selbst vornimmt. Die lokale Zuweisung ging mit — **zwei Leser blieben stehen, in jedem der beiden Pfade.** Vier Ausdrücke, zwei tote Namen.

Dass die Antwort trotzdem ankam, liegt an der Reihenfolge: Das Ereignis für den zweiten Graphen ist zu diesem Zeitpunkt schon geschrieben. Der `NameError` tötet nur das abschließende Statusereignis, und die Ausnahmebehandlung macht daraus einen roten Kasten. Deshalb wirkte es sporadisch.

**Reproduktionsweg:** Einen Turn über `/chat/stream` fahren und das Serverprotokoll lesen — `NameError: Stream-Fehler` mit Zeilenverweis. Gemessen am 30.07.2026, 22:30 UTC.

**Der eigentliche Befund ist nicht der Defekt, sondern dass er gemeldet war.** Die Linter-Regel für undefinierte Namen trug ihn seit dem Vortag. Acht ihrer neun Treffer waren diese beiden Abstürze, und sie gingen in 2253 geduldeten Treffern unter. **Daraus die zweite harte Regelfamilie** (`ruff-hart.toml`, F821): Eine Regel, die einen Absturz vor der Auslieferung findet, duldet keinen Bestand.

---

### Initiative-Achse (Chat 119)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### INITIATIVE-M1-OHNE-QUELLE — der State-Key, den M1 liest, hat keinen Erzeuger ✅ Gelöst Chat 119
**Kategorie:** ANT

**Gelöst am 30.07.2026.** Der erste Pfad erhebt die Intentionen im Salienz-Node und legt ihre Vereinigung über die Segmente in den State; sie reisen mit demselben Ereignis in den zweiten Pfad wie `salienz_human`. Der Enricher des CharacterGraph gibt dem Wert aus dem Ereignis Vorrang vor seiner Ableitung aus der Historie — ohne diesen Vorrang überschriebe er die Quelle sechs Nodes vor der Achse. **Live gemessen an zehn Turns: M1 kam in allen acht Achsenläufen an, kein `fehlend=['wollen']`.**

~~**Was der Fix nicht löst:**~~ **Am selben Tag nachgezogen.** Die Schwelle stammte aus einer Erhebung ohne M1 und trug über zehn Turns **8 von 8 mal Bit 0**, Minderheit 0 %. Neu erhoben über 127 Turnpaare: **−0.05**, κ 0,406, κ außerhalb der Stichprobe 0,358. Dieselben zehn Turns ergeben jetzt 6 zu 2, Minderheit 25,0 %.

*Der Befund unten bleibt vollständig stehen — er beschreibt, wie der Kanal aussah, und die Fehlerklasse gilt weiter.*

**Entdeckt:** Chat 119, beim Prüfen der Live-Wirkung der Dreiwertigkeit.

**Symptom:** `fuehrung_messen` meldet in jedem Turn `fehlend=['wollen']`. Die Achse rechnet damit `rohwert = bewegung` — M1 trägt live nichts bei, obwohl es die Hälfte der Rechnung sein soll.

**Mechanismus:** M1 liest `state["user_intentionen"]`. Die einzigen Schreiber dieses Schlüssels sind:

- `graph/base.py:125` und `graph/builder.py:94` — initialisieren auf `[]`
- `graph/nodes/enricher.py:239, 434` — setzen ihn aus `raw_turns`, also aus den **bisherigen Session-Turns**
- `graph/nodes/dispatcher.py:329` — schreibt den Session-Turn mit `state.get("user_intentionen", [])`
- `services/event_consumer.py:502` — reicht durch

Der Enricher liest aus den Session-Turns, der Dispatcher schreibt in die Session-Turns. **Ein geschlossener Kreis ohne Quelle:** Was nie hineinkommt, kann nie herauskommen. Die Perzeption erzeugt kein `user_intentionen`, sondern ein einzelnes `external.emotion.intent`; die Intentionsliste im KZG stammt aus `salienz_obj["intentionen"]` (`agents/kzg/speicher.py:326`, `memory/kzg.py:369`). **Zwei Erzeuger von Intentionen, und keiner bedient den Schlüssel, den die Achse liest.**

**Reproduktionsweg:** Einen Turn fahren und die Zeile `ki_server.ei.initiative: Initiative: …` lesen — sie trägt `fehlend=['wollen']` und **keine** Kanon-Verwerfung, die Liste ist also leer und nicht ungültig. Gegenprobe in Redis: `LRANGE session:<user>:<char>:turns 0 -1` zeigt auf `rolle='user'` das Feld `intentionen: []`, während `modus`, `emotion`, `arousal`, `tone` und `sprach_stil` gefüllt sind. Gemessen 30.07.2026 an drei Turns, 3 von 3.

**Alter:** mindestens seit dem Bautag der Achse. Das als „live belegt" geführte Beispiel in `novaberg-gv-initiative_k.md` §1 vom 29.07.2026 trägt `fehlend=['wollen']` bereits im abgedruckten Log — der Beleg für das Funktionieren der Achse enthält den Befund.

**Wirkung, die über die Achse hinausgeht:** Der Kalibrier-Korpus holt die Intentionen über `verbindung` aus dem KZG und hat M1 in 47,4 % der Turns. Sein Modul-Docstring sagt zu, der Rohwert entstehe „wie zur Laufzeit". **Korpus und Laufzeit rechnen verschiedene Größen**, und die Schwelle `GV_INITIATIVE_SCHWELLE` wurde auf Rohwerten *mit* M1 kalibriert und wird auf Rohwerte *ohne* M1 angewandt.

**Nicht entschieden:** ob `user_intentionen` aus dem Salienz-Objekt gespeist werden soll — derselben Quelle wie das KZG — oder ob die Achse direkt dorthin greift. Das ist eine Frage der Absicht und gehört in die Konzeption.

### Prompt & Antwortqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### STREAM1 — 'list' object has no attribute 'items' ✅ Gefixt Chat 39
**Kategorie:** ANT
**Entdeckt:** Chat 37, SSE-Stream
**Doppel-Bug:**
1. `event_generator()` crashte bei `chunk.items()` — LangGraph liefert nach Agent-Subgraph-Return manchmal Listen statt Dicts. Fix: `isinstance(chunk, dict)`-Guard.
2. SSE-Detail-Builder für `agent_dispatch` behandelte `agent_results` als Dict, ist aber `list[AgentResult]`. Fix: Iteration über Liste mit isinstance-Check für Dataclass vs. Dict.
**Reproduzierbar:** Ja — tritt auf wenn Agent-Dispatch-Pfad durchlaufen wird (NotizenAgent, TimelineAgent). Seit Chat 37 bekannt, in Chat 39 endgültig gefixt.

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### RESUME-REJECT — Pflicht-Rückfrage führt Aktion trotz "Nein" aus ✅ Gefixt Chat 50
**Kategorie:** ANT
**Entdeckt:** Chat 49, Telegram-Konversation (16.04.2026 20:06–20:07)
**Reproduziert:** Chat 49 dreimal — 20:07 ("Nein, ich muss das korrigieren"), 20:34 ("nein"), 20:46 ("Nein" nach "Vergiss den ganzen Charakter"). Jedes Mal mit Datenveränderung in der DB.
**Symptom:** Nach einer Pflicht-Rückfrage ("Soll ich das ausführen? Charakter-Anweisung ändern (ID X): ...") antwortet der User mit einer Ablehnung. Nova antwortet: "Die Aktualisierung ist erfolgt" oder "Die Anweisung wurde ausgeführt". DB-Beweis: Alte Anweisung wird deaktiviert, neue angelegt (oder bei Delete: alle deaktiviert).
**Reproduktion:**
1. Prompt auslösen der Pflicht-Rückfrage erzeugt (z. B. Charakter-Update, Charakter-Delete)
2. Nova fragt: "Soll ich das ausführen? ..."
3. User antwortet mit Ablehnung — egal ob "Nein", "Nein, ich muss das korrigieren" oder "nein" kleingeschrieben
4. Nova bestätigt Ausführung, DB-Eintrag verändert
**Analyse-Hypothesen:**
- **A)** Der Resume-Flow interpretiert JEDEN weiteren Prompt nach einer Pflicht-Rückfrage als Bestätigung, unabhängig vom Inhalt. Das Pending-Objekt in Redis wird beim Next-Turn aufgelöst statt geprüft. **Aktuelle Leithypothese.**
- **B)** Die Bestätigungs-Erkennung prüft nicht auf explizite Negationen ("Nein", "Abbrechen", "Stopp").
- **C)** Eine Kombination: Classify fängt "Nein..." als "neuer Auftrag" und löst Resume parallel aus, was zu einem Race zwischen Rejection und Execution führt.
**Schadensklasse:** **Kritisch** — Datenintegrität. Das System führt Aktionen aus, die der User explizit abgelehnt hat. Verwandt mit HALL2-Update (dort halluzinierte Bestätigung ohne Ausführung, hier echte Ausführung trotz Ablehnung).
**Lösungsansatz (offen):**
- Resume-Flow: Explizite Prüfung auf Negations-Pattern (Nein/Stopp/Abbrechen) BEVOR die Pending-Aktion ausgelöst wird
- Alternativ: Pflicht-Rückfrage nur bei klarer Bestätigung (Ja/OK/Bitte) auflösen, bei Unsicherheit erneut nachfragen
- Logs prüfen: Pending-Key-Handling im Resume-Pfad
**Prio:** **Hoch** — schwerwiegender als HALL2-Update (nicht nur Kommunikation sondern Datenverlust/-manipulation). Nächster Arbeitsschritt.
**Fix (Chat 50):** Neue Datei `agents/charakter_identitaet/resume.py` mit Strategy-Hook-Architektur (`_antwort_interpretieren(rueckfrage_typ, user_answer)`). `agent.py`: Resume-Node registriert, `_nach_validierung` routet bei `resume=True` zu "resume" statt "ausfuehren", neue `_nach_resume`-Methode. Vier Live-Tests bestanden. Phase-1-Andockpunkt vorbereitet.

---

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### THINK-MEM-LOOP — Thinker zykelt im memory_search-Tool ohne Konvergenz ✅ Behoben Chat 82
**Kategorie:** ANT

**Entdeckt:** Chat 75, Reducer-Umbau Smoke-Test (Faktencheck-Turn)
**Behoben:** Chat 82 (Per-Turn-Tool-Cache `ThinkerToolCache`, Stufe 1 + Stufe 2)

**Symptom:** Der Thinker ruft das `memory_search`-Tool 5× hintereinander mit derselben Query auf (`memory_search(Anna Geburtstag)`), bekommt 5× das identische Ergebnis (5 Treffer, 605 Zeichen Output) und verbraucht damit das gesamte 5-Iterationen-Limit (Thinker-Doku §3). Latenz dadurch ~25 Sekunden pro Turn. Nach Limit-Erreichung bleibt die Antwort unverändert — kein Faktencheck-Korrektur-Pfad.

**Ursache:** Fehlendes Abbruchkriterium im Thinker-ReAct-Loop. Tool-Outputs lebten ausschliesslich in der lokalen `messages`-Liste, ohne Wiederholungs-Erkennung. Identische Argumente erzeugten identische Tool-Calls, identische Treffer erzeugten identischen LLM-Reasoning-Output, der wieder denselben Tool-Call ausloeste.

**Wichtig:** Dies war KEIN Reducer-Umbau-Bug. Pre-Umbau wäre derselbe Loop entstanden — er war nur unsichtbar, weil der alte `lzg_context_retrieve`-Aufruf einen Argument-Mismatch hatte und zur Laufzeit beim ersten Tool-Call gecrasht wäre. STRUCT-5c hat den latenten Bug en passant gefixt — und damit den Loop-Bug sichtbar gemacht.

**Lösung (Chat 82):** Defense-in-Depth Per-Turn-Cache, strikt lokal in `think()` instanziiert (keine Verschmutzung zwischen parallelen Graph-Laeufen mit unterschiedlichen Paaren moeglich, weil Lebensdauer = Lebensdauer von `think()`).

- **Stufe 1 (generisch, alle 5 Tools):** Argument-Cache in `_execute_tool_call`. Schluessel `f"{tool_name}::{json.dumps(args, sort_keys=True, default=str)}"`. Bei Treffer Hinweis-String zurueck statt Tool-Invocation.
- **Stufe 2 (nur `memory_search`):** Result-Hash ueber `(inhalt, subtyp, dimension, beobachter, vektor)` der entries-Liste. Effektives Gewicht und Arousal sind Decay-volatil bzw. Float-instabil und bewusst ausgeschlossen — sonst waere der Hash zwischen zwei identischen Anfragen wackelig.
- **Datenstruktur:** `OrderedDict` mit `MAX_GROESSE=20` und FIFO-Verdraengung via `popitem(last=False)`.
- **Code:** `novaberg/server/graph/nodes/thinker_cache.py` (neue Datei), Wiring in `novaberg/server/graph/nodes/thinker.py`.

### Classify & Router (Chat 48)

#### HALL2-Update — ~~Halluzinierte Bestätigung mit Datenverlust~~ ✅
**Kategorie:** ANT
**Gefixt:** Chat 54 — Architektur-Fix: Business-Logik aus dem Responder in den Planner verschoben. `_build_task_block()` erzeugt fertigen [AUFGABE]-Block im State (`task_block`). Responder konsumiert nur noch. REGELN-Guard: "Bestätige keine Aktion ohne Auftrag." Getestet: Router-Miss → Nova sagt ehrlich "kann ich nicht durchführen" statt zu halluzinieren.
**Entdeckt:** Chat 48, Live-Konversation
**Symptom:** "Ich hab den Ort direkt in den Termin eingetragen" — aber DB `details`-Feld leer, kein Agent-Dispatch im Log.
**Schadensfall:** HALL2 + ROUTE-MISS1 in Kombination:
1. Router: Miss → kein Agent
2. Responder: Halluziniert Erfolg aus dem Gesprächskontext
3. Salienz: Erkennt "Monheim" (Score 0.70), aber unter Promotion-Threshold (0.80)
4. KZG: Eintrag mit TTL 30 Tage, kein Fakt, keine Entität → verfällt
5. User denkt, Info ist gespeichert → falsches Vertrauen
**Lösungsansatz:** Regel im Responder-Prompt: "Bestätige keine Aktionen, die du nicht durchgeführt hast (kein AgentResult mit status='abgeschlossen' vorhanden)."
**Prio:** Hoch — schlimmste Variante: nicht nur falsche Info, sondern falsches Vertrauen.

---

### Responder & Stilqualität (Chat 49)

#### urllib3-RETRY — Automatischer HTTP-Retry erzeugt Doppel-Turns ✅
**Kategorie:** ANT
**Entdeckt:** Chat 61, 23. April 2026
**Symptom:** Wenn der Server lange auf die LLM-Antwort wartet (in Chat 61: 55 Sekunden Pfad 1 durch GPU-Druck), wird der gleiche User-Prompt zweimal in die Session geschrieben. Zwei User-Turns mit identischem Inhalt, Zeitstempel-Differenz exakt 55 Sekunden. Kein Fehler im Log.
**Ursache (Hypothese):** Die `requests`-Library (über urllib3) macht automatische Retries bei Connection-Reset oder ähnlichen Netzwerk-Events. Bei langen Verbindungen zum Docker-Server kann ein Connection-Wackler den Retry triggern — der Server sieht ihn als neuen Prompt.
**Lösungsansatz:** In `client/ui/stream_handler.py` einen HTTPAdapter mit `max_retries=0` konfigurieren:
```python
from requests.adapters import HTTPAdapter
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=0))
session.mount('https://', HTTPAdapter(max_retries=0))
```
Dann Requests über diese Session abwickeln statt direkt `requests.post()`.
**Prio:** Niedrig-Mittel — nur bei langsamen Responses auftretbar, aber erzeugt inkonsistente Session-Daten, wenn es auftritt.

**Verifiziert Chat 73:** Fix seit Chat 65 aktiv, 5 Tage ohne Doppel-Turn-Bericht.

---

### Chat 62 — Paar-Schema-Folgebugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Hintergrund](novaberg-bugs-archiv-hintergrund.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ROUTE-CHAR-NOTIZ — CharacterGraph-Router dispatched Konversation an NotizenAgent ✅
**Kategorie:** ANT
**Entdeckt:** Chat 62
**Symptom:** Der Router im CharacterGraph erkennt Konversation faelschlich als Notizen-Task ("Lumi Geschlecht" → `management_action=agent`, `management_target=notizen` → Dispatch → Fehler). Der Classify im NotizenAgent rejected korrekt ("kein Notiz-Auftrag"), aber der Umweg kostet einen LLM-Call und erzeugt eine Fehlermeldung im Gespraechsvektor.
**Verwandt:** ROUTE-MISS1 — dort False Negative (Router uebersieht Auftrag), hier False Positive (Router halluziniert Auftrag). Beide zeigen, dass der Router kurze kontextabhaengige Prompts nicht sauber klassifiziert.
**Loesungsansatz:** Router-Prompt haerten — kurze Zwei-Wort-Phrasen ohne Verb und ohne Objekt-Marker nicht als Notiz-Auftrag klassifizieren. Alternativ: Router bekommt die letzten Turns als Kontext und prueft, ob das Thema gerade im Gespraech ist.
**Prio:** Niedrig — kosmetisch und Performance, kein Datenverlust.
**Fix (Chat 65):** Zwei Maßnahmen: (1) Genereller Dispatch-Guard in `prompts/default/router.task.txt` — kein Dispatch ohne Kommando-Signal (Verb, Imperativ, Schlüsselwort). (2) Regel 2 in `plugins/notizen_manager/manager.py` verschärft — bloße Themen-Erwähnung ist kein Dispatch mehr, nur explizite Änderungsanweisungen.
**Status:** Behoben, Verifikation ausstehend. Bei erneutem Auftreten wieder öffnen.

---

### Chat 72 — Dreischicht-Integration + GV-Refactoring (Folgebugs)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Charakter](novaberg-bugs-archiv-charakter.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ECHO-BUG — Nova wiederholt User-Nachricht wörtlich bei langen Sessions ✅ Behoben Chat 81
**Kategorie:** ANT

**Entdeckt:** Chat 72, 01. Mai 2026
**Behoben:** Chat 81, 09. Mai 2026 (durch Reducer-Umbau Chat 75, STRUCT-1 bis STRUCT-6)

**Symptom:** Bei Sessions mit 11+ Turns wiederholt Nova die User-Nachricht wörtlich statt zu antworten.

**Ursache:** Kontext-Sättigung. Session-Turns + KZG/LZG-Rauschen + Charakter-Hash + GV-Vorschlag erschöpften den verfügbaren Kontext. Das Modell fiel in einen Kopier-Modus zurück.

**Lösung:** Reducer-Umbau in Chat 75 (STRUCT-1 bis STRUCT-6) hat den Memory-Context strukturiert dedupliziert und das Kontext-Volumen reduziert.

**Verifikation:** Live-Beobachtung im 38-Turn-Chat in Chat 81 — kein Kopier-Modus, kein Echo-Verhalten. Nova antwortet eigenständig auch in langen Sessions.

---

### Chat 106 — Doku-Code-Abgleich (Code-Funde)

#### RESPONDER-VEKTOR-TOT — Novas Emotions-Vektor erreicht den Responder-Prompt nie ✅ Behoben Chat 106
**Kategorie:** ANT

**Entdeckt:** Chat 106, systematischer Doku-Code-Abgleich (Fund über `novaberg-node-responder.md` §3/§5)

**Klasse:** Toter Lesepfad — State-Key ohne Schreiber nach dem Personality-Klassen-Umbau (Chat 105), Severity **Hoch** — kritischer Pfad, entwertet den NOVA-VERLAUF-LEER-Fix

**Symptom:** Die Vektor-Zeile im `[EIGENE_EMOTION]`-Block des Responder-System-Prompts erscheint nie. Der Responder liest `state.get("nova_emotions_vektor", "")` und rendert die Beschreibung nur, wenn der Wert gesetzt und in `EMOTIONS_VEKTOREN_NOVA` enthalten ist — aber kein Node im gesamten Server schreibt diesen State-Key. Der EI-Calc legt den Wert stattdessen in `internal.emotion.emotions_vector` ab; `graph/state.py` dokumentiert diese Wanderung sogar als Kommentar.

**Beleg (Datei:Funktion):**

- Leser (toter Pfad): `graph/nodes/responder.py` → `_build_system_prompt` (Lesestelle Z. 233, Render-Bedingung Z. 247–248)
- Schreiber (anderer Kanal): `graph/nodes/ei_calc.py` → `_ei_calc_character` (`internal.emotion.emotions_vector = nova_emotions_vektor`, Z. 255)
- Bestätigung der Wanderung: `graph/state.py:85` („nova_emotions_vektor wandert in internal.emotion.emotions_vector")
- Korrekt migrierter Vergleichspfad: `services/event_consumer.py:476` liest für die API-Response richtig aus `result_internal.emotion.emotions_vector`

**Auswirkung:** Nova bekommt die Richtung ihres eigenen emotionalen Bogens (plateau, eskalation, absturz, …) in keiner Antwortgenerierung zu sehen — betrifft jeden CharacterGraph-Turn. Der NOVA-VERLAUF-LEER-Fix (`2462d16`/`a5acc7d`/`4c409b3`, Roadmap) hat den Vektor erstmals beweglich gemacht; durch diesen Lesepfad-Bruch bleibt die Bewegung für die Antwortqualität unsichtbar. Fix bewusst offen — kommt nach eigenem Audit, nicht aus dem Doku-Abgleich.

**Behoben Chat 106 (Commit `f1b7f8e`):** Reiner Lesepfad-Fehler, Regression aus dem
Personality-Umbau — die Reihenfolge stimmte (`ei_calc` ist der zweite Node im
CharacterGraph, lange vor dem Responder; kein Chat-89-Muster). **Live bewiesen
11.7. 19:11:43:** `VEKTOR-TEST: flach=None | internal vorhanden=True |
vektor='eskalation'` — der Wert war da, eine Etage tiefer, als der Responder suchte.
Fix: Lesepfad umgebogen auf `internal.emotion.emotions_vector`, dazu jeder Ausfallweg
einzeln laut (internal/emotion fehlt → error; Vektor leer/Kaltstart → warning; Vektor
unbekannt → error — der dritte Zweig fängt EI-KANON-FEHLT an dieser Stelle ab). Der
Zustand „Zeile fehlt still" existiert nicht mehr. **Abnahme 11.7. 19:19:51:** Die
Vektor-Zeile stand erstmals im `[EIGENE_EMOTION]`-Block („Du bist in Hochstimmung. Die
Begeisterung steigt weiter.") — zwei verschiedene Vektoren im selben Prompt (Nova:
`eskalation`, User: `plateau`), die Konfliktzeile lebt. Die Dual-Emotion-Architektur hat
seit Chat 89 gerechnet und geschwiegen — ab heute spricht sie. Der Miss war 16 Chats
unsichtbar, weil der Block wie „Vektor absichtlich leer" aussah
(lesson_l_default-wie-fehlschlag in Reinform).

---

*Aktualisiert Chat 106: Doku-Code-Abgleich über 46 Dokumente (Bericht: `~/ki-assistent/doku-code-abweichungen-chat106.md`, außerhalb des Repos). Code-Fund RESPONDER-VEKTOR-TOT als Bug aufgenommen. PIPELINE-LOG-ART-DOKU-DRIFT → novaberg-backlog.md (Doku-Drift, kein Code-Defekt — der Code ist richtig, das Konzeptdokument falsch; ⚠ Sperrvermerk dort: vor CHARAKTER-RESONANZ Teil 2 klären). Die übrigen ~60 Befunde sind Doku-Drift und gehören in die Doku-Pflege, nicht hierher.*

---

### Chat 106 — Audit tote State-Keys

#### THINKER-SELFTRIGGER-KANALLOS — Self-Trigger-Wert am Node-Übergang still verworfen ✅ Behoben Chat 106
**Kategorie:** ANT

**Entdeckt:** Chat 106, Audit der flachen State-Keys nach dem Personality-Umbau
(Gegenprobe über alle Schreibstellen).

**Klasse:** Undeklarierter StateGraph-Channel — Wert soll transportiert werden, wird
verworfen. Der schlimmste der drei Tages-Bugs: **falsch beglaubigt**. Kraft 1 war still
kaputt, der Loop war laut kaputt — hier behauptete das Log aktiv das Gegenteil der
Wahrheit („Thinker: Doppel-Fehlschlag — Self-Trigger fuer Klaerung gesetzt"). Wer den
Pfad debuggt, sieht „gesetzt" und sucht den Fehler woanders; der Wachposten
THINKER-DOPPELFEHLSCHLAG-LIVE beobachtete wochenlang einen Pfad, der laut Log
funktioniert.

**Symptom:** Der Thinker schreibt `self_trigger`/`self_trigger_payload` in den State
(Doppel-Fehlschlag-Pfad), der Event-Consumer liest sie vom finalen Graph-Result — beide
Keys waren im `ConversationState`-TypedDict nicht deklariert. StateGraph rekonstruiert
den State pro Node aus den Channels; der Wert wurde an der ersten Node-Grenze
(Thinker → Tribunal) still verworfen und erreichte das Result nie. Der
Klärungs-Folge-Durchlauf (continue-Event) konnte nie feuern. Ironie: Der
`lzg_resonanz`-Kommentar in `state.py` dokumentiert exakt diesen Fehlermodus — drei
Zeilen weiter fehlten die beiden Keys.

**Live bewiesen 11.7. 18:35:22** (Zweig deterministisch erzwungen via temporärem
`_FORCE_DOPPELFEHLSCHLAG`; der erste Versuch traf den Erfolgspfad — die Messung war
korrekt, aber sie traf den Pfad daneben):

```
KANAL-TEST/Thinker: self_trigger im State gesetzt — vorhanden=True,  wert=True
KANAL-TEST (Tribunal):                              vorhanden=False, wert=None
```

Eine Millisekunde. Eine Node-Grenze. Wert weg. Nicht `False` — **nicht vorhanden**.

**Behoben Chat 106 (Commit `090ac07`):** Zwei Kanäle in `state.py` deklariert, zwei
Init-Punkte (`base.py`, `builder.py` — mehr gibt es nicht; `character_graph`/`agent_graph`
delegieren an `super()`, `human_graph` hat keinen Override). Dazu: Das Log sagt jetzt,
was es weiß („Self-Trigger im State gesetzt (self_trigger=True) — Auslieferung haengt am
Event-Consumer", auch in `node_annotations`); der Consumer loggt jede Ankunft, nicht nur
den Erfolgsfall; der `MAX_SELF_TRIGGERS`-Deckel greift nicht mehr heimlich. **Abnahme:**
`Event-Consumer: Self-Trigger im Result — vorhanden=True, wert=False` —
`vorhanden=True` beweist den Kanal, ohne den Fehlschlag provozieren zu müssen.

---

### Chat 106 — Tagesgeschäft (Befunde)

#### GV-STRATEGIE-VEHIKEL-LEER — leere Strategie/Vehikel ohne Log ✅ Behoben Chat 114
**Kategorie:** ANT

**Entdeckt:** Chat 106, Tagesgeschäft. **Prio mittel.**

**Symptom:** ~~Bei `Cluster=paradox`/`kissenschlacht`~~ liefert der GV-Node leere Strategie
und leeres Vehikel. ~~Kein Log — stiller Miss.~~

**Beide Einschränkungen widerlegt (Chat 114, GV-Vollaudit):** Der Verlust hängt **nicht am
Cluster** — er trat in jedem Cluster auf, in dem das LLM überhaupt eine Strategie nannte.
Und es gab sehr wohl eine Log-Zeile (`GV-Parse: Unbekannte Strategie '●'`); sie benannte
nur das Symptom, nicht die Ursache, und niemand las sie.

**Gemessene Ursache:** Der `[WERKZEUGE]`-Block stellte jeder Zeile eine Marker-Glyphe
voran (`● Sp (Spiegelung) — Affinitaet: 25%`). Das LLM antwortete formattreu
`STRATEGIE: ● Sp (Spiegelung) …`, und `gv_output_parsen` las mit `raw.split()[0]` die
**Glyphe** als Kürzel. Zweite Variante: Das LLM verwechselte die Stockwerke und
beantwortete die Absicht-Zeile mit einem Strategie-Kürzel (`ABSICHT: Sa`).

**Beleg:** 44 Injektionen über 18 h Container-Laufzeit — **17 mit leerer Strategie (39 %),
14 mit leerem Vehikel (32 %)**, 16 Parse-Warnungen. Zwei Live-Turns am 28.07.2026
(12:31:56 und 12:34:48) zeigen beide Varianten wörtlich.

**Auswirkung:** GV-Impuls ohne Strategie-Anteil, von außen unsichtbar. Der Responder
erhielt `Strategie=` und ließ die Zeile *„Deine Strategie: …"* im Prompt weg — das WAS
der Dreischicht fehlte in zwei von fünf Turns.

**Behebung (Chat 114):** Drei Teile in `ei/dreischicht.py`. (1) `_strategie_extrahieren`
und `_begriff_extrahieren` ziehen den Kanon-Begriff aus der Zeile statt des ersten Tokens
— Marker, Klammern, Umlaute und angehängte Begründungen sind toleriert. (2) `korridor_pruefen`
prüft die gewählte Strategie gegen das Repertoire des Clusters; was dort `unpassend` ist,
wird verworfen. (3) Der Marker steht jetzt **hinter** dem Kürzel, und der Block nennt das
erwartete Antwortformat. Verworfene Rohwerte tragen Feld, Wert und Grund und werden im
Node mit `logger.error` benannt sowie in `gv_detail["korridor_verstoesse"]` geführt — ein
Verlust ist damit nicht mehr von außen unsichtbar. Das Vehikel wird erstmals überhaupt
gegen seinen Kanon geprüft. Tests: `tests/test_gv_korridor.py` (16), Eingaben wörtlich aus
dem Messprotokoll. Live belegt 28.07.2026 13:03:50 — `Strategie=Sa` im Cluster
`schlachtfeld`, wo `Sa` Kernstrategie ist.

### Chat 107 — init.sql-Audit (Code-Fund)

#### GV-ENTITY-HOP-TOT — Entity-Kontext im Gesprächsvektor seit Einführung tot ✅ Behoben Chat 107
**Kategorie:** ANT

**Entdeckt:** Chat 107, init.sql-Audit (systematischer Abgleich aller SQL-Literale im Code gegen das in `db/init.sql` + `agents/*/init.sql` definierte Schema, Gegenprobe gegen die Live-DB).

**Klasse:** Schema-Mismatch hinter Silent Skip — Query gegen eine Spalte, die es nie gab, Fehler vier Monate lang als Warning degradiert. Severity **Hoch** — der GV-Node verlor eine seiner beiden eigenen Wissensquellen (Entity-Hops), ohne dass es je eine Fehlermeldung gab.

**Symptom:** Beide Fakten-Queries in `_entity_kontext_laden` selektierten `f.beziehung` aus `fakten` — die Spalte heißt in `db/init.sql` und live seit jeher `attribut`. Jede Ausführung warf `UndefinedColumn`; der umschließende `except Exception` stufte auf `logger.warning("GV-Entity-Hop fehlgeschlagen")` ab und lieferte `""`. 411 aktive Fakten, nie einer im Gesprächsvektor angekommen. Das Warning sah aus wie ein legitimer Leerfall (lesson_l_default-wie-fehlschlag, gleiche Klasse wie RESPONDER-VEKTOR-TOT).

**Beleg (Datei:Funktion):**

- Leser (beide Queries): `graph/nodes/gespraechsvektor.py` → `_entity_kontext_laden` (Hop 1 und Hop 2)
- Schema: `db/init.sql`, Tabelle `fakten` (`attribut`, kein `beziehung`; Live-DB deckungsgleich)
- Silent Skip: `except Exception` → `logger.warning` → `return ""`

**Auswirkung:** Der GV-Node bekam nie Entity-Kontext (Hop-1-/Hop-2-Faktenkanten) für die Hypothesen-Destillation — betrifft jeden Turn mit `management_target` oder `prompt_topic`.

**Behoben Chat 107 (Commit `7df65f1`):** `f.beziehung` → `f.attribut` in beiden Queries. Fehlerbehandlung nach dem Fail-loud-Muster des Dispatchers getrennt: `psycopg2.Error` → `logger.error` mit `exc_info` + `log_fehler`-Forensik (`grund=entity_hop_db_fehler`), Turn läuft ohne Entity-Kontext weiter; das pauschale `except Exception` ist weg — echte Python-Fehler krachen jetzt. Legitime Leerfälle (kein Schlüssel, keine Entitäten, 0 Fakten) loggen `info`/`debug` und liefern weiterhin `""`. Verbindung schließt im `finally` (leckte vorher im Fehlerfall). **Live bewiesen 12.7.** (echte Funktion, read-only gegen Live-DB): Schlüssel `Nova` (user `meister`) → 23 deduplizierte Faktenkanten statt `""`; Gegenprobe mit Fantasie-Schlüssel → `info`-Log + `""`. Design-Grenze dokumentiert, kein Bug: Der Hop erfasst nur Entität→Entität-Fakten (`objekt_id` gesetzt, live 47 von 411); Wert-Fakten (`objekt_wert`, 364) sind konstruktionsbedingt nicht hüpfbar.

---

### Chat 107 — Randbefund der Schwellwert-Kalibrierung (A3)

#### GV-RESONANZ-FALLBACK-LUEGT — erfundener Resonanz-Wert verkleidet „nicht anwendbar" als „passt hervorragend" ✅ Behoben Chat 107
**Kategorie:** ANT

**Entdeckt:** Chat 107, Randbefund bei A3 (Schwellwert-Kalibrierung) — aufgefallen, weil 0.5 im neuen Vektorraum ein HOHER Wert ist (p99 = 0.57). Ab dem Modellwechsel hätte der Fallback jeden Kandidaten durchgewinkt — **angelastet worden wäre es dem neuen Embedding.**

**Klasse:** Der Kern in einem Satz: **Ein Default, der wie ein voller ERFOLG aussieht.** Gegenrichtung zur Lesson „Ein Default darf nie wie ein Fehlschlag aussehen" (`lesson_l_default-wie-fehlschlag`) — und mindestens genauso gefährlich, weil er nicht auffällt. Severity **Mittel** (im alten Raum verhaltensneutral, ab A4 aktiv falsch).

**Symptom:** `ei/wissensluecken.py::wissensluecken_finden` setzte bei fehlendem Charakter-Kern (legitimer Cold-Start) UND bei fehlgeschlagenem Kern-Embedding (Infrastrukturdefekt) für jeden Kandidaten `charakter_resonanz = 0.5` — lautlos, über der 0.40-Schwelle, jeder Kandidat passierte. Der erfundene Wert hat nie etwas entschieden; er hat nur die Buchführung belogen und den Fehlerfall zum Erfolg umlackiert.

**Behoben Chat 107 (Commit `1e5ae70`):** `resonanz_pruefbar`-Flag statt Zahlen-Fallback — der Filter prüft die Resonanz-Bedingung nur, wenn das Flag steht. Zweig 1 (kein Kern, Cold-Start): `logger.warning` einmal pro Aufruf mit `user_id`, Kandidaten qualifizieren sich allein über die Relevanz. Zweig 2 (Kern da, Embedding scheitert): `logger.error` mit `exc_info`, Turn läuft weiter — der Defekt schreit, die LOG-TUERKLINGEL wird ihn fangen. Kein Verhaltenswechsel, ehrliche Verbuchung. Fallback 0.0 bewusst verworfen: hätte die Neugier beim frischen Paar bis zur ersten Destillation abgewürgt — ein Feature abwürgen, um eine Buchführung zu reparieren, wäre der falsche Tausch.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### `IMPULS-FAELLT-AUS-DEM-VERLAUF` — Nova schreibt ihren eigenen Vorschlag dem Nutzer zu ✅
**Kategorie:** ANT

**Zustand:** behoben — gebaut und gemessen am 24.08.2026. Der Sprecher kommt jetzt aus dem Feld `herkunft`, nicht aus der Position in der Liste. Zeugen `tests/test_verlauf_sprecher.py` (24), zwei Gegenproben (**9 vorhergesagt / 8 gezählt** an der Paarbildung, **4 vorhergesagt / 8 gezählt** an der Sprecherbezeichnung), Suite `Ran 2248 tests — OK`, 0 übersprungen.

> **Die Behebung erzeugte ihr eigenes Spiegelbild, und die zweite Kontrolle fand es.** `max_turns` hieß *Turn-Paare* und ein Impuls zählte nicht, weil er übersprungen wurde; danach zählte **jede Gruppe**. Der Impuls fiel nicht mehr aus dem Verlauf — er **verdrängte** dafür den Nutzer aus dem Fenster derer, die nur fünf Einheiten sehen, und acht der neun Aufrufer übergeben unverändert `5`. Bei **16 von 24** Zuständen der echten Session lagen weniger Nutzer-Turns im Fenster als vorher, bei einem **keiner mehr**: fünf aufeinanderfolgende Eigen-Impulse und kein Wort des Nutzers, gelesen von Perzeption, Router und sechs Klassifikations-Knoten. Berichtigt über `fenster_waehlen` — die Zahl zählt wieder Wortwechsel, Impulse dazwischen kommen mit; danach kein Zustand ohne Nutzer-Turn.

**Symptom, im Betrieb belegt am 24.08.2026.** Drei Turns in 41 Sekunden — die entscheidende Spanne ist die von **sieben**, zwischen Impuls und Nachfrage. Hier in ihrer Struktur — der Wortlaut trägt nichts zum Befund bei:

```
18:37:40  eigener_impuls   Nova   schlaegt aus eigenem Antrieb ein Vorhaben vor
18:37:47  nutzer_turn      User   fragt nach, worum es dabei gehe        (+7 s)
18:38:21  nutzer_turn      Nova   fragt zurueck, worauf DER NUTZER damit hinauswolle
```

**Nova schreibt den Vorschlag dem Nutzer zu.** Gemacht hatte ihn sie, sieben Sekunden vor seiner Nachfrage.

**Ursache — und sie liegt nicht dort, wo der Verdacht hinzeigt.** Nicht der tote Kontaminationsfilter (`KONTAMINATIONSFILTER-TOT`) hat den Impuls entfernt, sondern die **Paarbildung**: Beide Verlaufs-Renderer gruppierten `user` → `assistant` und übersprangen, was nicht hineinpasste.

```python
else:
    # Alleinstehender Assistant-Turn (z.B. Shadow) — ueberspringen
    i += 1
    continue
```

Ein Eigen-Impuls **ist** ein alleinstehender assistant-Turn. Er traf diesen Zweig in `memory/session.py::format_session_turns_numbered` **und** in einer wörtlichen Kopie derselben Logik in `graph/nodes/responder.py` — er erreichte keinen der beiden Verläufe.

**Gemessen, mit der echten Funktion über die echten Turns:**

| | |
|---|---|
| Turns im Verlauf | 24 |
| alleinstehende assistant-Turns (fielen aus) | **8** |
| Satz des Impulses im Verlauf wiederzufinden, vorher | **nein** |
| Satz des Impulses im Verlauf wiederzufinden, nachher | **ja** |
| Beiträge hinein / heraus, nachher | 8 / 8 |

**Die Daten waren die ganze Zeit vollständig.** Alle 24 Turns tragen `herkunft`, acht davon `eigener_impuls`. Das Feld existiert seit dem 30.07.2026 und wurde von keinem Renderer gelesen — der Sprecher wurde aus der Position **erschlossen**, obwohl er **mitgeschickt** wurde.

**Warum es nie auffiel.** Was übrig bleibt, liest sich vollständig:

```
[2] NOVA: <Frage aus dem vorigen Turn>
[3] USER: <Nachfrage>
```

Das ist ein sauberer Wortwechsel. Die Lücke ist nur daran zu erkennen, dass die Antwort auf eine Frage antwortet, die nicht dasteht.

**Die Abhilfe.** `verlauf_gruppieren` und `sprecher_bezeichnen` in `memory/session.py`; beide Renderer rufen sie, die Kopie im Responder ist fort. Ein Impuls steht als eigene Gruppe mit `NOVA (von sich aus)`. Eine Ausgabe-Verifikation zählt Beiträge gegen Turns und meldet, wenn der Verlauf eine Äußerung verliert — im Auslösepfad belegt, nicht nur gebaut.

**Alle sieben Renderer nennen den Sprecher aus dem Feld**, nicht nur die zwei, an denen es auffiel. Die zweite Kontrolle hat sie gesucht statt erinnert und fand drei, die zwar jeden Turn trugen, aber den Anlass verschwiegen — `memory/kontext.py::_turns_formatieren`, `enricher.py::_suchtext_bauen` und den `messages`-Aufbau des Verfassers. **Person-eindeutig, Anlass unbekannt.** Alle drei nachgezogen, gemessen über die echten Turns: **24/24 Inhalte, 8/8 Impulsmarken** in jedem.

> **Der Verfasser hat dafür seine Prompt-Form gewechselt.** Er reichte den Verlauf als Nachrichtenfolge durch — je Turn eine Chat-Nachricht —, und dort gibt es für den Anlass nur einen Platz: den Inhalt der `assistant`-Nachricht. **Genau dort darf er nicht stehen:** Das ist Iteration 1 aus `novaberg-pixie_l_kontamination.md`, und das Modell hat den Marker damals mitgeschrieben. Der Verlauf steht jetzt als benannter Textblock, wie beim Responder — der Anlass im Rahmen, nicht in Novas Mund. Der Preis ist benannt: kein natives Chat-Format mehr, und ein Rückschlag wäre daran zu erkennen, dass `(von sich aus)` in Novas Antworten auftaucht.

Beim **Zusammenfasser** wiegt es am schwersten — seine Ausgabe überdauert den Verlauf und wird später als Tatsache gelesen.

**Verwandt:** `KONTAMINATIONSFILTER-TOT` (derselbe Gegenstand, andere Ursache; durch diesen Befund entschieden) · `PFAD1-TIMEOUT-TURNVERLUST` (dort entstand das Feld `herkunft`, das hier fehlte, weil es niemand las).

---

#### KONTAMINATIONSFILTER-TOT — der Filter prüft auf einen Marker, den niemand setzt ✅
**Kategorie:** ANT

**Zustand:** behoben — am 24.08.2026 **entfernt statt repariert**, und die ausstehende Entscheidung ist damit getroffen. Von den drei Möglichkeiten des Befundes (streichen · auf `reiz_herkunft` umhängen · als bewusste Nicht-Filterung dokumentieren) ist die **erste** gewählt, aus einem Grund, den der Befund noch nicht kannte: **Der Impuls gehört in den Verlauf.**

> **Entschieden hat es ein zweiter Defekt am selben Gegenstand.** `IMPULS-FAELLT-AUS-DEM-VERLAUF` zeigte, was passiert, wenn ein Eigen-Impuls den Verlauf nicht erreicht — Nova schrieb einen Vorschlag, den sie selbst gemacht hatte, dem Nutzer zu. Ein Filter, der genau das absichtlich täte, hätte den behobenen Defekt wiederhergestellt, sobald jemand den Marker setzt.
>
> **Was der Filter verhindern wollte, war eine Verwechslung, kein Vorkommen.** Die verhindert jetzt der benannte Sprecher (`memory/session.py::sprecher_bezeichnen`) — ohne die Äußerung zu verlieren. Zeugen: `tests/test_verlauf_sprecher.py` (13), Suite `Ran 2237 tests — OK`.
>
> **Der Filter blieb dreizehn Tage stehen, weil er wie ein Schutz aussah.** Genau das ist die Klasse: Ein toter Schutzmechanismus ist teurer als keiner, weil wer ihn liest das Problem für gelöst hält.

**Entdeckt:** Chat 110, bei der Frage, ob der Impuls-Turn gefiltert werden muss.

**Klasse:** Toter Schutzmechanismus. Severity **mittel** — der Filter *scheint* zu schützen; wer ihn liest, hält das Problem für gelöst.

**Symptom:** `server/graph/nodes/enricher.py:448` filtert Session-Turns:

```python
if turn.get("kern") and turn["kern"].startswith("[Nova-Impuls]"):
```

Der Marker `[Nova-Impuls]` wird im gesamten Server **nirgends gesetzt** — die einzige Fundstelle ist diese Lesestelle. Der Filter greift damit nie. Er sitzt zudem nur in `_enrich_character`, nicht im HumanGraph.

**Beleg:** `grep -rn "Nova-Impuls" --include='*.py' server/` liefert genau einen Treffer: die Bedingung selbst.

**Herkunft:** Der Filter stammt aus der Zeit, als die Shadow-Delivery ihre Nachricht selbst formulierte und als Sonder-Turn ablegte. Seit Chat 110 spricht der Responder, und der Impuls-Turn ist ein regulärer Turn.

**Nicht entschieden:** Der Impuls-Turn steht jetzt **ungefiltert** im Kontext. Das ist vermutlich richtig — er trägt Novas eigene Stimme, nicht mehr eine fremdformulierte Zeile. Aber es ist nicht entschieden, und die Lesson aus Chat 7 beschreibt einen realen Vorfall mit kontaminiertem Kontext. Drei Möglichkeiten: streichen, auf `reiz_herkunft` umhängen, oder als bewusste Nicht-Filterung dokumentieren.

~~**Status:** Offen, Entscheidung ausstehend.~~ → entschieden und behoben am 24.08.2026, siehe Zustandszeile.

---

### Chat 114 (28.07.2026) — GV-Vollaudit

#### GV-TIEFE-DEFAULT-BLIND — die Tiefe-Achse maß überwiegend ihren eigenen Default ✅ Behoben Chat 114
**Kategorie:** ANT

**Klasse:** Default, der wie ein echter Wert aussieht. Severity **Hoch** — die Achse
entscheidet über Sektor und Cluster und damit über das gesamte Strategie-Repertoire.

**Symptom:** Die Perzeption darf zehn Gesprächsmodi liefern (`perzeption.task.txt`),
die vier Modus-Tabellen des GV-Pfads kannten fünf. Die fehlenden fünf —
`philosophischer_austausch`, `lernmodus`, `kreativ`, `beratend`, `berichtend` — fielen
auf den Default 0.3. Das ist derselbe Wert, den `alltag` legitim trägt: Aus dem Log war
ein echter Alltag von einer Vokabular-Lücke nicht zu unterscheiden.

**Beleg:** 33 von 45 Läufen mit `T=0(0.30)`, während Novas Live-Modus in Redis
`philosophischer_austausch` war. Betroffen waren fünf Stellen, nicht vier: `GV_TIEFE_MODUS`,
`GV_AUFNAHMEBEREITSCHAFT_MODUS`, `register_kompatibilitaet`, `_farbe_modus` und die
if/elif-Kette der Längenberechnung im Node.

**Auswirkung:** Ein philosophischer Austausch wurde als flaches Alltagsgespräch verrechnet.
Die tiefen Cluster waren praktisch unerreichbar — sieben der vierzehn kamen in 45 Läufen
kein einziges Mal vor.

**Behebung:** `MODUS_KANON` in `config.py` als Single Source of Truth (Handbuch §6). Alle
zehn Modi tragen in allen fünf Stellen einen eigenen Wert; die if/elif-Kette wurde zur
Tabelle `GV_LAENGE_MODUS_DELTA`, damit Vollständigkeit prüfbar ist. `modus_pruefen()` in
`ei/utils.py` meldet einen Modus außerhalb des Kanons mit seinem Namen. Die Achsen-Logzeile
nennt jetzt den Modus hinter dem Rohwert. Tests: `tests/test_modus_kanon.py` (14) — der
Zeuge ist die Prompt-Datei, nicht der Code, der sie erfüllen soll. Live belegt
28.07.2026 13:03:47: `T=1(0.90 philosophischer_austausch)`, erstmals aus einer Messung
statt aus dem Default.

#### GV-ACHSEN-ZWEI-ZEITSTAENDE — die beiden Beine des Nodes standen wieder auf verschiedenen Ständen ✅ Behoben Chat 114
**Kategorie:** ANT

**Klasse:** Ein Wert, dessen Uhr in einem Feld liegt, das jemand anders berührt — dieselbe
Fehlerklasse, die Chat 113 eine Node-Position früher geschlossen hat. Severity **Hoch**.

**Symptom:** `ei_calc` überträgt Novas dominante Emotion nach `internal.emotion`. Seit
Chat 113 läuft der EmGrav-Node **danach** und ändert `nova_emotions_verlauf` erneut. Die
sechs Säulen der Aufnahmebereitschaft lesen den Verlauf, die Dreischicht-Achsen lesen
`internal.emotion` — im selben Node, im selben Turn, auf zwei Ständen.

**Beleg (28.07.2026):**

```
12:31:49,832  internal.emotion aktualisiert — neugierig (a=0.50), gilt ab hier fuer den GV-Node
12:31:50,054  EmGrav-Node: neugierig(0.96) -> begeisterung(1.00)
12:31:52,354  GV4-Neugier: emotion='begeisterung' … A=1.25      ← sechs Saeulen
12:31:52,508  GV-Achsen: E=1(0.50) …                            ← internal.emotion
```

**Auswirkung:** Sektor, Cluster und Repertoire standen auf der Lage **vor** der
reaktivierten Erinnerung, während die Neugier die danach kannte. Die Log-Zeile
*„gilt ab hier für den GV-Node"* behauptete zusätzlich eine Geltung, die sie seit Chat 113
nicht mehr besaß — ein Log, das eine Entscheidung benennt, die es nicht getroffen hat.

**Behebung:** Der EmGrav-Node zieht `internal_emotion_uebertragen()` nach, wenn er den
Verlauf verändert hat; die Funktion nennt ihren Aufrufer in der Log-Zeile. Die
Achsen-Logzeile trägt die Emotion hinter dem Valenz-Bit, damit die Frage überhaupt
beobachtbar ist. Tests: `tests/test_gv_zeitstand.py` (6). Live belegt 28.07.2026 13:03:45 —
`EmGrav-Node (nachgezogen): internal.emotion gesetzt — begeisterung (a=1.00)`, gefolgt von
`GV-Achsen: E=1(1.00) … V=1(begeisterung)`.

#### GV-ENTITY-HOP-FINDET-NICHTS — 45 von 45 Läufen ohne einen einzigen Fakt ✅ Behoben Chat 115 (umgehängt, nicht repariert)
**Kategorie:** ANT

**Entdeckt:** Chat 114, GV-Vollaudit. **Prio hoch.** **Untersucht und geschlossen Chat 115.**

**Klasse:** Drei unabhängige Ursachen hintereinander, von denen die erste die beiden
anderen verdeckt. Der Leerfall sieht an jeder der drei Stellen legitim aus.

**Symptom:** Jeder Lauf endet mit `GV-Entity-Hop: keine Entitaeten zum Schluessel '…'`.
Über die gesamte Container-Laufzeit lieferte **kein einziger** Hop Fakten.

##### Warum der ursprüngliche Befund richtig und trotzdem zu kurz war

Der Chat-114-Eintrag nannte die `ILIKE`-Suche als Ursache und schlug vor, den Schlüssel zu
tokenisieren oder über das Embedding zu suchen. **Beides hätte keinen einzigen der 45 Läufe
verändert.** Die Untersuchung in Chat 115 fand drei Türen, die unabhängig voneinander
geschlossen sind; der Befund von Chat 114 beschreibt die oberste.

**Tür 1 — Hop 1 kann konstruktiv nicht treffen.** Der Schlüssel ist eine Themenphrase aus
`prompt_topic`, der Entitätsbestand besteht aus Eigennamen. Gemessen 28.07.2026 an 89 aktiven
Entitäten: 65 einwortig, Namenslänge im Schnitt 11 Zeichen, 83 von 89 kürzer als ein typischer
Schlüssel. Gegen zwei echte Schlüssel aus dem Log wurden **beide** Richtungen getestet —
`name ILIKE %schluessel%` (der heutige Code) und die Umkehrung `schluessel ILIKE %name%`:
je **0 Treffer**. Der Mismatch ist kategorial, nicht syntaktisch; kein Teilstring-Verfahren
verbindet eine Themenbeschreibung mit einem Eigennamen. Eine Tokenisierung hätte daran
nichts geändert.

**Tür 2 — der zweite `ILIKE`-Zweig ist durch die Daten tot.** Die Query prüft zusätzlich
`zusammenfassung ILIKE %schluessel%`. Gemessen: **88 von 89** Entitäten haben keine
Zusammenfassung, weil der einzige aktive Erzeuger (`agents/kzg/magnete.py`,
`_entitaeten_aufloesen` → `create_new_entity`) nur Name und Typ setzt. Nur die eine
`user`-Entität trägt eine. Auch eine Embedding-Suche über dieses Feld hätte kein Substrat.

**Tür 3 — auch ein perfekter Hop 1 liefert nichts.** Die `fakten`-Tabelle hat **0 Zeilen**
(gemessen 28.07.2026; nicht 0 aktive, 0 insgesamt) und keinen erreichbaren Produzenten.
Details unter *Warum die Tabelle leer ist*.

##### Warum die Tabelle leer ist — und warum das keine Panne war

Der einzige Extraktionspfad ist `FaktenManager.fakten_verarbeiten`, direkt aufgerufen nur von
`agents/promotion/agent.py`. Alle Auslöser dieses Agenten sind zu:

- Die Queue-Route `lzg_promotion` zeigt seit Commit `4dd6ac6` (24.05.2026) auf
  `synapsen_promotion` statt auf `promotion`.
- Die Aufgabe `fakten_extraktion` kommt repoweit **einmal** vor — in der Deklaration, die
  sie anmeldet. Niemand stellt je einen solchen Auftrag ein.
- Ein Schedule-Eintrag `pixie:schedule:promotion` existiert nicht (7 Einträge, keiner davon).
- Der zweite Eingang `FaktenManager.execute()` über `pending_writes` ist erreichbar, aber
  unbefüllt: Die Salienz legt ausschließlich `ziel="kzg"` an, der Notizen-Manager
  `ziel="notizen"`. `ziel="fakten"` erzeugt niemand.

**Das war eine bewusste Festlegung, keine Regression.** K2 in
`novaberg-memory-synapsen-p4-entscheidungen_k.md` (Chat 91):

> Pfad D.2 — Tripel-Extraktion entfällt komplett in P4. Kein Call 1, kein Call 2, kein
> FaktenManager-Aufruf im neuen Pixie-Agent. Funktionalitäts-Bruch zwischen P4 und M2.5b
> wird akzeptiert (keine neuen Tripel, keine Edge Invalidation, **eingefrorener
> Fakten-Bestand**). Spätere Architektur: FaktenAgent als eigenständige Fachabteilung
> (M2.5b), analog zu TimelineAgent.

**Was die Festlegung nicht vorsah:** Der akzeptierte Preis war ein *eingefrorener* Bestand —
keine neuen Fakten, aber die vorhandenen weiter lesbar. Das galt 64 Tage lang; Chat 107 zählte
am 12.07.2026 noch 411 aktive Fakten. Der Reset am 27.07.2026 hat diesen Bestand entfernt.
Aus *eingefroren* wurde *leer*, und das ist ein anderer Preis als der, der damals abgewogen
wurde. Kein Dokument hielt das fest, weil es niemand beschlossen hat.

##### Behoben Chat 115 — umgehängt statt repariert

Der GV-Node zieht seine zweite Wissensquelle jetzt aus `state["lzg_resonanz"]`, das der
Enricher legt (`_resonanz_kontext_laden` in `graph/nodes/gespraechsvektor.py`). Das ist
dieselbe Zwei-Stufen-Traversierung, die das Konzept für den Entity-Hop beschreibt, nur über
den Erinnerungs- statt den Faktengraphen: Schale 0 sind die Anker der Cosine-Suche über
`lzg_knoten`, Schale 1+ die Nachbarn entlang `lzg_kanten`. Dieser Graph wird laufend
befüllt — 296 Knoten, 13.538 Kanten (gemessen 28.07.2026).

**Warum keine eigene Abfrage:** Der GV-Node fragt bewusst nicht selbst die Datenbank. Zwei
Retrieval-Pfade mit zwei verschiedenen Ankern in einem Turn wären zwei Wahrheiten über
dasselbe Gespräch. Der Enricher läuft ohnehin vorher (`character_graph.py`:
enricher → … → gv_node).

**Der Prompt-Block heißt jetzt anders.** `[VERWANDTE FAKTEN]` versprach „bekanntes Wissen
über Personen, Orte und Vorlieben" — das war der Faktengraph. Die neue Quelle ist episodisch:
was erlebt wurde, nicht was der Fall ist. Der Block heißt `[VERWANDTE ERINNERUNGEN]` und sagt
das im Kopf. Ebenso umbenannt: das `gv_detail`-Feld `entity_hops` → `resonanz_kontext`.

**Was nicht behoben ist:** Der Faktenpfad selbst. `_entity_kontext_laden` liegt schlafend im
Modul, mit der Begründung und der Weckbedingung als Kommentarblock darüber. **Wer ihn
reaktiviert, repariert vorher Tür 1** — der Schlüssel-Mismatch bleibt auch mit vollen
Tabellen bestehen. Die Wiederbelebung des Faktengedächtnisses ist M2.5b (Backlog); ihre
Vorbedingung nach Synapsen-Konzept §3.2 ist ein stehender LZG-Kern. Stand 29.07.2026 ist
er das nicht: Die beiden Felder, über die §3.2 die zwei Gedächtnis-Modalitäten verschränkt,
sind zu 22 % (`entitaet_ids`, 65 von 296 Knoten) und zu 0,3 % (`timeline_id`, 1 von 296)
gefüllt. Das Faktengedächtnis müsste genau dort andocken.

**Tests:** `tests/test_gv_resonanz_kontext.py` (9). Darunter einer, der rot wird, wenn der
Faktenpfad wieder in den Node verdrahtet wird — sonst käme der Befund zurück, ohne dass
etwas rot wird. Gegenprobe zweifach: Schalen-Unterscheidung entfernt → rot; Aufruf auf
`_entity_kontext_laden` zurückgedreht → rot.

**Live belegt 29.07.2026, 05:35 UTC:** `GV-Resonanz: 3 Erinnerung(en) in den Prompt
(Cluster 'feuerwerk', Schalen: [0, 1, 1])` — ein Anker, zwei Nachbarn. `[VERWANDTE
ERINNERUNGEN]` im GV-Prompt vorhanden, `[VERWANDTE FAKTEN]` nicht mehr. Seiteneffekte im
Messfenster: 0 `timeline`, 0 `notizen`, 0 `fakten`.

#### GV-REGISTER-OHNE-ZUG — Novas Register wurde konserviert, aber nie zum Nutzer gezogen ✅ Behoben Chat 114
**Kategorie:** ANT

**Klasse:** Halb gebauter Mechanismus. Die konservierende Hälfte stand seit jeher, die
zweite Kraft fehlte. Severity **Hoch** — betrifft zwei der sechs Achsen und damit Cluster
und Repertoire jedes Turns.

**Symptom:** Die Nähe- und Tiefe-Achse lasen `internal.emotion.mode`, `.language_style`
und `.relationship_dynamic`. Diese Felder beschreiben **Novas letzte Äußerung**, gemessen
von der Assistant-Perzeption, über `redis:nova_state` in den nächsten Turn getragen — und
nichts zog daran. Die gemessenen Werte des Nutzers lagen im selben State und wurden nie
gelesen.

**Beleg (28.07.2026, Sequenz mit Themenwechsel vom Physikgespräch auf ein Alltagsthema):**

| Turn | Register des Nutzers | Register Novas | Cluster |
|---|---|---|---|
| 13:16 | `alltag` / `locker` | `philosophischer_austausch` / `fachlich` | Schlachtfeld |
| 13:27 | `alltag` / `locker` | `philosophischer_austausch` / `formell` | Foyer |

Der Nutzer wurde lockerer, Nova förmlicher — keine Verzögerung um einen Turn, sondern eine
**Divergenz**, die sich mit jedem Eigen-Impuls verstärkte. In beiden Clustern führt die
Matrix `So` (Selbstoffenbarung) als unpassend; die naheliegende menschliche Antwort war
strukturell ausgeschlossen. Eine ausdrückliche Kurskorrektur des Nutzers hatte keinen
Eingang ins System.

**Auswirkung:** Der Node bezog seine Landschaft aus einem Text, der nicht der letzte war.
Verstärkt durch die Rückkopplung über Eigen-Impulse: Novas eigener abstrakter Beitrag
wurde als `philosophischer_austausch` klassifiziert, und genau dieses Feld las der nächste
Turn.

**Behebung:** Novas Raum als eigener, persistierter Zustand (`graph/personality.py:Raum`,
`ei/raum.py`, Konzept §3.4). Zwei Zahlen statt Labels — Labels beschreiben je eine
Äußerung, der Raum ist der Zustand dazwischen. Der Zug ist proportional zum Abstand,
derselben Bauart wie die Empathie-Injektion der Emotion, aber mit umgekehrtem Vorzeichen
in der Distanz: Bei der Emotion zieht ein weit entfernter Nutzer stärker, beim Register
kostet die Umstellung. Hinauf 0.35, hinab 0.65 — beide aus einer Simulation aller
Modus-Übergänge gewählt, nicht gesetzt.

**Zwei Befunde aus dieser Simulation, die den Bau verändert haben:** Ein Ziel exakt auf der
Achsen-Schwelle (`kreativ` = 0.5, Nähe neutral/neutral = 0.5) ist bei proportionalem Zug
**nie** erreichbar — daher die Ankunftsregel. Und der Charakterfaktor, der den Zug
skalieren soll, ließ sich nicht aus der Cosine-Distanz zweier Pol-Texte gewinnen: Zwei
Kunstfiguren trennen sich sauber bei +0.24 und −0.22, der echte Charakter liegt bei +0.036
und wechselt das Vorzeichen je nach eingebettetem Textumfang. Er steht deshalb auf 1.0 und
ist als offener Punkt dokumentiert.

**Messung (28.07.2026, 14:28–14:30, drei Turns mit Wissenschaftsthemen):**

```
Raumzug: Tiefe 0.90 → 0.90 (Ziel 0.90) · Naehe 0.45 → 0.62
Raumzug: Tiefe 0.90 → 0.51 (Ziel 0.30) · Naehe 0.62 → 0.65
Raumzug: Tiefe 0.51 → 0.37 (Ziel 0.30) · Naehe 0.65 → 0.76
GV-Sektor: #13 'Bier' → Cluster 'bier'   ·   Repertoire: Im=passt, Be=kern
```

Dieselbe Ausgangslage hatte vorher Schlachtfeld und Foyer ergeben. Tests:
`tests/test_gv_raumzug.py` (16), darunter eine Wirksamkeitsprüfung, die Raum und Labels in
Widerspruch setzt — die erste Fassung der Datei belegte nur, dass der Zug rechnet, nicht
dass die Achsen ihn benutzen.

**Bleibt offen:** `GV-FARBTON-SUBJEKTWECHSEL`. Der Farbton liest weiterhin die Labels und
formuliert daraus Sätze über den Nutzer.

*Aufgenommen Chat 114 (GV-Vollaudit). Drei Befunde derselben Sitzung behoben
(GV-TIEFE-DEFAULT-BLIND, GV-ACHSEN-ZWEI-ZEITSTAENDE, GV-REGISTER-OHNE-ZUG), einer aus
Chat 106 geschlossen und in seiner Ursache korrigiert (GV-STRATEGIE-VEHIKEL-LEER).
Suite 296 → 349 Tests, grün, 0 übersprungen.*

#### GV-METADATEN-ERREICHEN-DIE-SPRACHE-NICHT — der Korridor stand richtig und wurde überschrieben ✅ Behoben Chat 114
**Kategorie:** ANT

**Klasse:** Prompt-Architektur. Eine korrekte Anweisung an der falschen Stelle. Severity
**Hoch** — sie entwertete die gesamte Registermechanik des Nodes.

**Symptom:** Alles über das WIE der Antwort stand im System-Prompt. Unmittelbar vor der
Generierung lag stattdessen der Gesprächsverlauf.

**Beleg (28.07.2026, 16:59:55):** Ein Turn mit `Cluster=kissenschlacht` („Spielerisch, nah,
lebendig. Leichtigkeit ist der Inhalt"), `Strategie=Im`, `Vehikel=frage`, EI-Profil
`Stil: locker | Modus: spielerisch` — also jedes Registersignal auf leicht. Die Antwort
begann mit *„Diese mathematische Eleganz, mit der du unsere Dynamik als Resonanzphänomen
beschreibst …"* und endete bei der thermischen Entropie. Das Wort „spielerisch" kam darin
vor — als Objekt eines abstrakten Satzes.

**Die Größenverhältnisse, gemessen im selben Turn:**

| Bestandteil | Größe |
|---|---|
| Session-Verlauf im Prompt | 21 Turns, 98.074 Bytes in Redis, ungekürzt |
| Gedächtnis-Kontext | 4.154 Zeichen |
| Identität | 1.268 Zeichen |
| Gesprächsvektor-Block | **1.376 Zeichen** |
| Responder-Eingang gesamt | **11.254 Tokens** |

Rund drei Viertel des Prompts sind Gesprächsverlauf, und dort stehen die eigenen Absätze
der Assistentin wörtlich. Der Registeranteil ist etwa drei Prozent — und stand vor der
Wand statt dahinter.

**Auswirkung:** Die Dreischicht konnte den Ton nicht setzen, egal wie richtig Cluster,
Strategie und Raum waren. Das erklärt, warum eine ausdrückliche Bitte des Nutzers um einen
leichteren Ton mehrere Turns lang folgenlos blieb: Der Verlauf trug seine eigene Sprache
weiter, und `SESSION_MAX_TURNS = 20` heißt, dass ein abstrakter Absatz erst nach rund zehn
Wortwechseln aus dem Prompt fällt.

**Behebung:** Neuer Block `[DEIN SPRACHSTIL]` (`prompts/default/responder.sprachstil.txt`),
angehängt ans **Ende** der Nutzer-Nachricht — hinter dem Verlauf und hinter dem aktuellen
Prompt. Er führt hin, statt zu verbieten: Der Verlauf sei in einer anderen Lage entstanden,
wichtig sei jetzt dieser Klang. Inhalt: Landschaft und Fragefrequenz aus dem Cluster (der
über Novas Raum trägheitsbehaftet nachzieht), der Ton aus `external` — dem Register des
aktuellen Nutzer-Turns, nicht aus alten Labels — sowie Werkzeug und Leitgedanke.
Rund 60 Tokens.

**Messung (28.07.2026, 17:57–17:58, zwei Turns):** Bei `Cluster=feuerwerk` und einem Prompt
**ohne** jeden Stilwunsch begann die Antwort mit *„… das ist ein wahnsinnig starkes Bild!
Es ist, als würde die Realität selbst kurz die Maske fallen lassen …"* — sie greift das
Bild des Nutzers auf, statt es zu übersetzen. Tests:
`tests/test_responder_sprachstil.py` (7), darunter eine Positionsprüfung: Verlauf →
aktueller Prompt → Sprachstil. Ein Inhaltstest allein bestünde auch, wenn der Block wieder
nach vorn wanderte.

**Einschränkung:** Zwei Turns. Die Wirkung auf den Ton lässt sich nicht im Unit-Test
sichern, nur live beobachten. Ob der Block auch über längere Strecken trägt, ist offen.

**Zusammenhang:** `GV-REGISTER-OHNE-ZUG` (die Metadaten stimmen seit derselben Sitzung —
Voraussetzung, nicht Wirkung) · `GV-IMPULS-ALS-FAKTENSPERRE` · Echo-Bug Chat 72,
Lösungsvorschlag (c) Verlaufs-Trimming — durch diesen Befund als der wirksamste der drei
belegt, weiterhin nicht gebaut.

---

### Chat 116 (29.07.2026) — GV-Panel

#### GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE — der Neugier-Balken meldete eine Krise, wenn nur der Vektor kurz war ✅ Behoben Chat 116
**Kategorie:** ANT

**Entdeckt:** Chat 116, am laufenden Client beobachtet: Der Neugier-Balken des GV-Panels
stand über viele Turns hinweg auf 0. **Prio mittel.**

**Klasse:** Ausfallwert, der wie eine Messung aussieht — und zwar wie die eine Messung, die
etwas Bestimmtes bedeutet. Dieselbe Klasse wie `GV-CHARAKTER-DEFAULT-UEBER-MESSBEREICH` und
`lesson_l_default-wie-fehlschlag`.

**Symptom:** `aufnahmebereitschaft` wurde mit `0.0` initialisiert und nur innerhalb von
`if strategie_aktiv:` überschrieben, also erst ab Vektorlänge ≥ `GV_STRATEGIE_MIN_LAENGE`
(2). Jeder kürzere Turn schrieb die `0.0` unverändert nach `gv_detail`, von dort nach Redis
und ins GV-Panel.

**Warum das nicht nur unschön ist:** `0.00` ist im Konzept **für die Krise reserviert** —
`aufnahmebereitschaft_berechnen` gibt genau dann 0 zurück, wenn Stimmungsvektor `spirale`
oder `absturz` bei Arousal ≥ 0.7 vorliegt. Ein neutraler Zustand liegt bei ~0.56. Der
Balken meldete also nicht „nicht gemessen", sondern „Nova ist im Absturz".

**Beleg (Server-Log, 28.07. 19:57 bis 29.07. 05:37 UTC, acht GV-Läufe):** vier mit Länge 2
→ gerechnete Werte 0.626, 0.626, 0.937, 0.824. Drei mit Länge 1 → nie gerechnet, `0.0`
ausgeliefert. Einer mit Länge 0 → der Node kehrt zurück, bevor `gv_detail` existiert. In
**der Hälfte der Läufe** trug das Panel den Krisenwert.

**Mitbetroffen:** `services/event_consumer.py` loggt dieselbe Zahl aus `gv_detail` in die
Turn-Zeile.

**Behoben:** Die Rechnung steht jetzt vor dem Tor, nicht dahinter. Begründung im Code: Die
Aufnahmebereitschaft ist ein **Zustand Novas** — sechs Säulen aus Emotion, Arousal,
Stimmungsrichtung, Modus, Dynamik und Stil — und keine Funktion der Vektorlänge. Sie ist
rein (State-Lesen, Tabellen-Lookups, Arithmetik; keine DB, kein LLM). Das Längen-Tor bleibt
unverändert dort, wo es hingehört: vor der teuren Wissenslücken-Suche, die weiterhin
`strategie_aktiv and aufnahmebereitschaft > 0` verlangt.

**Tests:** `tests/test_gv_aufnahmebereitschaft.py` (3). Der Erwartungswert stammt aus der
dokumentierten Semantik der Größe, nicht aus dem Rechenweg. Zwei davon prüfen beide
Richtungen des Tors — geschlossen bei Länge 1, offen bei gesenkter Schwelle —, weil eine
vorgezogene Messung das Tor mit hochziehen könnte und die Suche dann in jedem Turn liefe.

**Gegenprobe zweifach, jeweils gezielt:** alte Torstellung wiederhergestellt → die zwei
Messungs-Tests rot, der Tor-Zwilling grün. Tor aus der Suchbedingung entfernt → nur der
Tor-Test rot.

**Live belegt 29.07.2026, 06:21:49 UTC:** Turn mit `GV-Laenge: 1`,
`GV4-Neugier: 0.551 (roh=0.49, produkt=0.98, emotion='neugierig' sektor=8 dist=0)`, und im
Panel-Pfad `GET /drive/gv_detail` → `aufnahmebereitschaft=0.551`, `strategie_aktiv=False`,
`wissensluecken=0`. Vorher wäre an derselben Stelle `0.0` gestanden. Seiteneffekte über
beide Messturns: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nicht mitbehoben, in der Fundliste:** Bei Länge 0 und beim Skip kehrt der Node zurück,
**bevor** `gv_detail` gesetzt wird. Der Dispatcher persistiert dann nichts, der Redis-Key
hat kein TTL — das Panel zeigt danach den Stand des letzten *nicht* übersprungenen Turns,
ohne Kennzeichnung. Am 29.07.2026 um 06:20:41 live vorgeführt: Ein Turn mit `GV-Laenge: 0`
ließ den 45 Minuten alten Blob stehen.

#### GV-INITIATIVE-KIPPT-NIE — eine Achse, die über 15 Läufe denselben Wert trug ✅ Behoben Chat 116
**Kategorie:** ANT

**Entdeckt:** Chat 116, bei der Frage, ob die Repertoire-Verteilung etwas ausschließt. **Prio hoch** — die Achse ist ein Drittel des Sektor-Index.

**Klasse:** Ein Maß, dessen Schwelle außerhalb seines erreichbaren Wertebereichs liegt. Verwandt mit `GV4-BEREITSCHAFT-DEFAULT-WIE-KRISE` aus derselben Sitzung, aber eine Stufe tiefer: Dort wurde ein Wert nicht gerechnet, hier wurde er gerechnet und konnte nie etwas bedeuten.

**Symptom:** `initiative_berechnen` bildete das Verhältnis der durchschnittlichen Zeichenzahl von Nutzer- zu Nova-Turns über die letzten sechs Session-Turns; `achsen_berechnen` kippte bei `>= 1.5`.

**Beleg (Server-Log, 28.07. 19:57 bis 29.07. 07:52 UTC, 15 GV-Läufe):** I = 1 in **15 von 15**, Rohwerte 0.10 bis 1.00. Aus den Session-Turns desselben Paars: Nutzer **51 Zeichen** je Turn, Nova **433** — Verhältnis 0.12. Für die Schwelle müsste der Nutzer **649 Zeichen** je Turn schreiben, das **12,6-fache**, und das im Schnitt über sechs Turns. Der Quotient ist durch die Bauart beider Seiten nach oben gedeckelt: Eine Assistentin antwortet in Absätzen, ein Mensch tippt eine Zeile.

**Auswirkung:** Sektor-Index = `E*32 + R*16 + N*8 + V*4 + T*2 + I*1`. Ein festes Bit halbiert den Zustandsraum — **32 der 64 Sektoren waren nicht selten, sondern unerreichbar.**

**Drei Konzept-Widersprüche, alle am Code belegt:**

- `novaberg-gv-strategie_k.md` §3.1 nennt als Quelle `intentionen` + Turn-Muster. Gebaut war nur die Textlänge; dasselbe Dokument nennt seine Fassung an anderer Stelle „Heuristik v1".
- Die Wertebereichs-Tabelle desselben Dokuments führt die Größe mit **0.0 bis 1.0**. Die Schwelle lag bei **1.5**, also außerhalb. Wäre der Code auf den konzipierten Bereich normiert gewesen, hätte die Achse **konstruktionsbedingt** nie kippen können.
- `if avg_nova == 0: return 2.0` — 2.0 ≥ 1.5. **Eine leere Nova-Antwort war der zuverlässigste Weg zu „Nutzer führt".** Ein Ausfallwert auf einer regulären Achsenposition.

**Behoben Chat 116 — ersetzt, nicht kalibriert.** Eine Nachkalibrierung der Schwelle hätte die Achse nur launischer gemacht: Sie misst die falsche Größe. Wer ein Gespräch treibt, hängt nicht an der Zeichenzahl — eine kurze Frage kann stärker lenken als drei Absätze Antwort. Neu misst `ei/initiative.py` drei Formen von Führung (Wollen, Themensprung, Registerweg), jede auf ihr eigenes erhobenes Zentrum bezogen und je Dimension gewichtet. Herleitung, Messgrundlage und die verworfenen Alternativen: `novaberg-gv-initiative_k.md`.

**Tests:** `tests/test_gv_initiative.py` (12). **Gegenprobe:** die alte Achse zurückverdrahtet → vier rot, darunter `test_beide_bits_sind_erreichbar` mit `AssertionError: 1 == 1` — der Defekt reproduziert sich im Test.

**Live belegt 29.07.2026, 13:56 UTC:** Zwei Turns, der zweite mit Themenwechsel. `Initiative: wert=0.104 … [M1=— M2=0.729 M3=0.100] fehlend=['wollen']` → `I=0` → Sektor **#14 'Stilles Vertrauen'**, Cluster `glut`. **#14 gehört zu den 32 vorher unerreichbaren.** Seiteneffekte: 0 `timeline`, 0 `notizen`, 0 `fakten`.

**Nicht mitbehoben:** Der Charakter-Versatz steht auf 0.0 und ist nicht abgeleitet — dieselbe Lage wie `GV_RAUM_CHARAKTER_FAKTOR` nach Chat 114. Das Rad dafür ist entworfen (`novaberg-gv-initiative_k.md` §6), nicht gebaut. Ebenso fehlt das tote Band: Das Zentrum ist per Konstruktion der Median, also die dichteste Stelle der Verteilung — dort zittert das Bit am stärksten. Die Breite braucht eine eigene Messung.

---


## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Antwortpfad**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### EIGENER-GEDANKE-BEHAUPTET-SCHWEIGEN ✅ offen
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Der Block haengt an einem Tor: `graph/nodes/responder.py` haengt `[EIGENER GEDANKE]` nur an, wenn `reiz_ist_eigener_gedanke(state)` gilt. Ein Nutzer-Turn bekommt ihn nicht mehr, und der Thinker-Retry ebenfalls nicht — beide Faelle sind eigens bezeugt (`tests/test_responder_eigener_gedanke.py`).

**Befund (2026-07-31).** `[EIGENER GEDANKE]` behauptet „der Nutzer hat gerade nichts gesagt, auf das du antwortest", während der Prompt des Nutzers im selben Prompt darunter steht. Beobachtet an einem Turn mit vorhandener Nutzeräußerung.

**Was fertig waere.** Der Block erscheint nur, wenn der Nutzer tatsaechlich nichts gesagt hat.

**Prioritaet:** mittel.

#### CLIENT-OFFENE-FRAGE-UNSICHTBAR ✅ offen
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Die fehlende Anzeige ist gebaut: Trifft eine Antwort mit fremder Zuordnung ein, setzt `client/ui/main_window.py` sie als *unzugeordnete Antwort* ab, mit dem Vermerk, dass die letzte Nachricht unbeantwortet blieb. Der Riegel verhinderte die falsche Zuordnung schon vorher; **sichtbar** ist die fehlende Antwort seitdem.

**Befund (2026-08-01).** **Eine nie beantwortete Frage ist im Client als offen vermerkt, aber auf dem Bildschirm unsichtbar.** Nach einem ausgefallenen Turn bleibt ihre Kennung in der Menge der offenen Fragen stehen; die nächste Antwort schließt nur die Kennungen, die sie nennt. Der Riegel verhindert damit die **falsche** Zuordnung, macht die **fehlende** Antwort aber nicht sichtbar — der Nutzer sieht drei Fragen und zwei Antworten und kann nicht erkennen, welche ins Leere ging. Die Daten liegen vor, es fehlt die Anzeige.

**Nachtrag 31.07.2026, die Rate im Messbestand.** In **5 von 19** Turns einer Messreihe trägt der Rohturn **kein** `antwort_inhalt`, der Verfasser hat also nichts geliefert. Das Feld erscheint nur, wenn es belegt ist — die Unterscheidung „nicht gelaufen" gegen „leer" ist damit gewahrt, aber ein Viertel der Turns ohne fachlichen Inhalt ist eine eigene Zahl. Kein Agent war beteiligt, `task_context_cut` also nicht der naheliegende Grund.

**Was fertig waere.** Eine Frage, die als offen gefuehrt wird, ist auf dem Bildschirm auch als offen erkennbar — oder sie wird beim Ausfall geschlossen.

**Prioritaet:** mittel.

#### GV-DREISCHICHT-BLOCK-OHNE-AUFTRAG — Werkzeuge im Prompt, aber kein Auftrag, sie zu benutzen ✅
**Kategorie:** ANT

**Zustand:** behoben — gegen HEAD `b8e9543` nachgesehen am 25.08.2026. Der Block wird nicht mehr unbedingt gebaut: `graph/nodes/gespraechsvektor.py` haengt ihn nur an, wenn die Strategie aktiv **und** die Aufnahmebereitschaft groesser null ist. Werkzeuge ohne Auftrag stehen damit nicht mehr im Prompt.

**Entdeckt:** Chat 114, GV-Vollaudit. **Prio mittel.**

**Symptom:** Der Dreischicht-Block wird unbedingt gebaut und angehängt, auch wenn
`strategie_aktiv=False` (Vektorlänge < `GV_STRATEGIE_MIN_LAENGE`). Dann sieht das LLM
`[WERKZEUGE]` und `[ABSICHTEN]`, bekommt aber die Anweisung *„Beschreibe die LANDSCHAFT —
nicht die Route"* und kein Ausgabeformat, weil `gv.strategie` fehlt.

**Beleg:** Zwei Turns mit Länge 1 (28.07.2026, 12:34 und 13:03). Beide Male antwortete das
LLM trotzdem mit Absicht- und Strategie-Zeilen, aber ohne Vehikel — der Prompt fragt es
in diesem Zweig nicht.

**Auswirkung:** Widersprüchlicher Prompt. Entweder der Block gehört hinter dieselbe
Bedingung wie der Strategie-Auftrag, oder der Auftrag gehört zum Block.

### `TELEGRAM-NAMENSAUFLOESUNG-FAELLT-AUS` — zeitweise kein Name
**Kategorie:** ANT

**Zustand:** **gegenstandslos seit dem 24.08.2026** — der Telegram-Kanal ist abgeschaltet, der Behaelter `ki_telegram` gestoppt und entfernt. Der Befund ist damit **nicht behoben, sondern ohne Gegenstand**: `_nachricht_senden` faengt weiter jede Ausnahme und kehrt zurueck, aber der Pfad laeuft nicht mehr. **Wer den Kanal zurueckholt, holt diesen Defekt mit** — der Eintrag bleibt deshalb stehen statt geschlossen zu werden. Davor: offen, gegen HEAD `00c16b6` gehalten am 20.08.2026.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Die Namensauflösung im Telegram-Behälter fällt zeitweise aus.** `httpx.ConnectError: [Errno -3] Temporary failure in name resolution` beim Griff nach `api.telegram.org`, zweimal im beobachteten Fenster: 14.08. 23:06 und 15.08. 07:22 (dort vier Zeilen). Beim Abholen von Nachrichten ist das folgenlos — die Bibliothek wiederholt. **Ungeprüft ist der Sendepfad:** `_nachricht_senden` fängt jede Ausnahme, protokolliert sie und kehrt zurück; eine Nachricht, die in dieses Fenster fällt, wäre damit verloren, ohne dass jemand sie erneut zustellt. Beobachtet, nicht reproduziert.

**Geschlossen, wenn** Die Namensaufloesung im Telegram-Behaelter faellt laut aus statt still.

---

---

### Umgezogen am 12.09.2026 — aus dem offenen Register

Der Eintrag ist an diesem Tag behoben worden; die Kennung bleibt unveraendert,
weil Verweise darauf zeigen.

#### GV-LAENGE-RUNDUNG-ZUR-GERADEN — ein Viertel der Nullen entsteht aus Pythons Rundungsregel ✅ behoben am 12.09.2026
**Kategorie:** ANT

**Symptom.** Turns bekommen Vektorlänge 0 und damit kein Vorausdenken, obwohl die Rechnung 0,5 ergeben hat.

**Ursache.** `_vektor_laenge_berechnen()` in `graph/nodes/gespraechsvektor.py` schließt mit `round(laenge)`. Python rundet zur **geraden** Zahl: `round(0.5)` ist 0, nicht 1. Ein Grenzwert, der auf der Kante liegt, entscheidet damit nach einer Regel, die an keiner Stelle genannt ist.

**Warum es niemandem auffiel.** Eine 0 ist ein gültiges Ergebnis dieser Funktion — sie heißt „kein Vorausdenken". Von einer gerechneten 0 ist eine gerundete nicht zu unterscheiden, solange niemand die Summe **vor** der Rundung ansieht.

**Belegt.** Über 845 Rohturns wiedergegeben: 96 Turns erreichen Länge 0, bei **25 davon (26 %)** liegt die Summe vor der Rundung bei mindestens 0,5. Die häufigste Lage dieser Art ist `berichtend | neutral | distanz | fachlich` — 1,0 minus 0,5 für `distanz`, sonst kein Beitrag, also genau 0,5.

**Priorität.** Mittel. Seit `F-LAGE-1` kostet eine 0 nicht mehr die Landschafts-Ablesung, sondern nur noch das Vorausdenken. Die Kante bleibt trotzdem eine ungenannte Regel an einem Tor.

**Nachtrag 12.09.2026 — dieselbe Regel hat eine zweite Kante, und die obere ist die teurere.** Der Befund oben beschreibt `round(0.5) → 0`, also den Verlust eines Schrittes am unteren Ende. **Am oberen Ende verliert dieselbe Regel den dritten Schritt vollständig, und zwar für drei der zehn Modi dauerhaft.**

`[gemessen 12.09.2026]` Je Modus die günstigste Faktorstellung (positive Emotion, arousal 1.0, `vertrauen`, `locker`) durch `_vektor_laenge_berechnen`:

| Modus-Zuschlag | beste Summe | Länge | Modi |
|---|---:|---:|---|
| 0.0 und +0.3 | 2.8 / 3.1 | 3 | `alltag`, `spielerisch`, `berichtend`, `arbeitsmodus`, `kreativ` |
| −0.2 | 2.6 | 3 | `emotional`, `beratend` |
| **−0.3** | **2.5** | **2** | `fachgespraech`, `lernmodus`, `philosophischer_austausch` |

> **Zwei Zuschläge, die sich um ein Zehntel unterscheiden, trennen hier *erreichbar* von *unerreichbar*** — nicht weil 0,1 viel wäre, sondern weil die Rundungsregel genau zwischen ihnen liegt. In den drei Modi mit −0.3 liegen **794 von 1434 Rohturns (55,4 %)**.

**Der Gegenbeleg aus dem Bestand:** 116 der 1434 Turns tragen Länge 3 — **keiner** in einem dieser drei Modi, alle mit `vertrauen` **und** `locker`, Modi `spielerisch` (62), `alltag` (44), `emotional` (8), `arbeitsmodus` (2). Die Kante ist also nicht theoretisch: Sie ist die Trennlinie, an der der Bestand endet.

**Und sie greift ineinander mit `MODUS-KREATIV-WIRD-NIE-VERGEBEN`.** Über eine 20-Turn-Reihe in `lernmodus` und `philosophischer_austausch` gemessen: In **8 von 20** Turns hätte allein `modus = kreativ` die Länge 3 erzeugt, während arousal, Dynamik und Stil in **keinem einzigen** dafür reichten. Der eine Modus, der die drei fachlichen über die Kante heben könnte, ist der, den das Perzeptionsmodell noch nie vergeben hat. **Wer die Rundung behebt, hebt zugleich diesen Riegel** — und wer nur `kreativ` zum Leben bringt, lässt die Kante stehen.

**Zustand: ✅ behoben am 12.09.2026.** `_vektor_laenge_berechnen` schließt mit `math.floor(laenge + 0.5)`; eine Summe genau auf der halben Stufe bekommt den höheren Schritt.

**Die Absichtsfrage ist dabei entschieden** (Eigentümer, 12.09.2026): Der Mechanismus darf aktiv sein. Die Decke 2 in den drei fachlichen Modi war keine Setzung, sondern die Folge einer Rundungsregel — sie fällt.

`[vorher gerechnet und nachgemessen, je 1434 Rohturns]` Die Vorhersage traf auf den Turn:

| Länge | vorher | nachher |
|---|---:|---:|
| 0 | 123 | **80** |
| 1 | 786 | **829** |
| 2 | 409 | **384** |
| 3 | 116 | **141** |

**68 Turns (4,7 %) wechseln** — 43 von 0 auf 1, 25 von 2 auf 3 —, und es kippt ausschließlich an den Summen 0,50 und 2,50. **Die Quote des Strategie-Tors bleibt unverändert bei 36,6 %**, weil kein Wechsel die Schwelle 2 überschreitet: Der Eingriff gibt Schritte dazu, ohne das Tor zu verschieben.

**Die Gegenprobe traf vorhergesagt:** Zeile zurückgedreht, 4 von 20 Zeugen rot — vorhergesagt 4. Suite **3463 grün, 0 übersprungen** (davor 3454).

> **Ein bestehender Zeuge fiel, und er war der aufschlussreichste Teil des Baus.** `test_die_gerechnete_null_traegt_eine_landschaft` prüfte, dass eine *gerechnete* Null eine Landschaft trägt — und hatte als Vorlage die **häufigste** Nulllage des Bestandes gewählt: `berichtend | neutral | distanz | fachlich`, Summe genau 0,5. Das war keine gerechnete Null, sondern eine gerundete, und sie war häufig **wegen** dieses Defekts. Der Zeuge bezeugte also die Ursache seiner eigenen Vorlage. Er trägt jetzt eine echte negative Summe (−0,5), und daneben steht ein zweiter, der den Wechsel der alten Kante festhält.

---
