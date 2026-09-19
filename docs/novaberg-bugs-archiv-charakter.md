# Novaberg — Bugs, Archiv: Charakter — Profile, Räder, Haltung, Emotion, Destillation

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, 22 Eintraege, je mit `CHA` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 30.08.2026 — eine Schwelle, die nicht mehr ablehnt

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Zwei Eintraege aus derselben Messung, **beide am 30.08.2026 behoben**. Der erste ist ein
**Schwellwert auf einer Groesse, die ihren dokumentierten Wertebereich verlassen hat**; der zweite
ist der Grund, warum der erste so lange unbemerkt blieb — **es gab nichts zu zaehlen**.

### `PROFIL-SCHLUESSEL-MIT-LEERRAUM` — ein Leerzeichen kostet den Traeger dauerhaft
**Kategorie:** CHA

**Zustand:** behoben am 03.09.2026 ✅
**Symptom.** `[gemessen]` 03.09.2026, 21:21 UTC: Der Erstlauf der Qualitaetsprofile ueber 20
Traeger verlor **4**, und alle vier mit derselben Meldung — *„Schluesselsatz weicht vom Kanon
ab — fehlend ['ungewissheit'], unerwartet ['un gewissheit']"*. Das Modell setzt ein Leerzeichen
in einen Bezeichner, den es im Prompt woertlich vorgegeben bekommt, und zwar reproduzierbar an
derselben Stelle: viermal `ungewissheit`, nie eine andere Dimension.
**Wirkung.** Nicht ein verlorener Lauf, sondern ein **dauerhaft verlorener Traeger.** Die
Kandidatensuche nimmt, wer noch keine Kante traegt; ein an dieser Stelle gescheiterter Traeger
traegt keine und wird deshalb wieder gezogen — gegen dasselbe Modell, mit demselben Prompt,
bei Temperatur 0,0. Er faellt bei jedem Lauf erneut aus, und der Deckel von 20 Traegern je Lauf
fuellt sich mit Wiederholungen.
**Was ihn sichtbar machte.** Die Pruefung gegen den **Kanon** statt gegen eine Teilmenge: Sie
nennt beide Seiten, fehlend und unerwartet, und damit stand der Grund in der ersten Zeile. Eine
Teilmengen-Pruefung haette *„ungewissheit fehlt"* gemeldet und den Rest verschwiegen.
**Die Abhilfe raeumt nur Leerraum ab.** `_schluessel_entraeumen` zieht Leerraum in Schluesseln
zusammen, schreibt jede Berichtigung ins Log und verwirft, wenn dabei zwei Schluessel
kollidieren. Die Kanon-Pruefung darunter bleibt scharf — ein erfundener Name faellt weiterhin
durch, und ein Zeuge haelt genau das fest (`neu heit` → verworfen).
**Im Bestand belegt.** Die drei erneut gezogenen Traeger (4692, 3944, 1533) sind profiliert:
6 von 6, 0 gescheitert.
**Prioritaet:** mittel — der Verlust war still im Sinne der Wirkung, nicht der Meldung.

---

### `FALTUNG-OHNE-AUFRUFER` — die Beruehrung wird geschrieben und nie gelesen
**Kategorie:** CHA

**Zustand:** behoben am 01.09.2026 ✅
**Symptom.** `[gemessen]` 01.09.2026, 14:00 UTC: Die vierte Messreihe hat **4 Beruehrungen** in
`praegung_beruehrung` erzeugt (Naehen 0,682 · 0,684 · 0,739 · 0,682). `ausschlag_aktuell` aller
vier Faeden steht danach unveraendert auf `ausschlag_absolut` — 0,794 · 0,854 · 0,991 · 1,000.
Der Grund: `memory/praegung.py` → `ausschlag_aktuell_falten` hat **keinen Aufrufer im
Produktivcode**. `grep -rn "ausschlag_aktuell_falten" server/ --include=*.py` liefert ausserhalb
der Zeugen nur die Definition. Geschrieben wird `ausschlag_aktuell` genau einmal, beim Anlegen
des Fadens (Zeile 174).
**Wirkung.** Die Kette der Praegungsschicht ist **nicht** geschlossen, obwohl alle vier
Bauteile stehen und bezeugt sind (7 Zeugen, 18 Stuetzstellen gegen die Konzepttabelle). Der
Verfall findet nicht statt, die Auffuellung findet nicht statt: Ein Faden behaelt seinen
Eingangswert fuer immer — genau der Zustand, den Scheibe 2 beheben sollte.
**Dieselbe Klasse wie in Scheibe 1.** Dort war `beruehrung_anlegen()` gebaut, getestet und ohne
Aufrufer; der Befund steht seit dem 31.08.2026 in der Featureliste. **Der Nachfolgebauteil hat
den Fehler geerbt** — die Zeugen pruefen die Funktion, nicht ihre Verwendung, und eine gruene
Suite sagt darueber nichts.
**Was fertig waere.** `ausschlag_aktuell` wird bei jedem Lesen eines Fadens — oder in einem
periodischen Lauf — aus `entstanden_am`, `ausschlag_absolut` und der Beruehrungsliste neu
gefaltet, und ein Betriebsbeleg zeigt einen Faden, dessen `ausschlag_aktuell` von
`ausschlag_absolut` abweicht.
**Prioritaet:** hoch.

---

**Behoben am 01.09.2026, 15:05 UTC.** `memory/praegung.py` → `ausschlag_aktuell_nachfuehren`
liest `ausschlag_absolut`, `entstanden_am` und die vollstaendige Beruehrungsliste, faltet und
schreibt; `beruehrung_aus_reaktivierung` ruft sie fuer jeden getroffenen Faden. **Ausserhalb der
Transaktion, die die Beruehrung schreibt** — die Rechnung ist jederzeit wiederholbar, und ein
Fehler in ihr darf kein Ereignis mitnehmen.

`[gemessen]` im Betrieb, fuenfte Reihe: Faden 327 **0,793893 → 0,792117**, Faden 354
**1,000000 → 0,998756**. Der Unterschied ist klein, weil beide Faeden Stunden alt sind — bei
`PRAEGUNG_HALBSTRECKE` 60 Tage ist das die richtige Groessenordnung, und die Zeugen decken den
Bereich ab, den der Betrieb heute nicht erreicht.

**Neun Zeugen** in `tests/test_praegung_nachfuehrung.py`, davon drei auf die **Verwendung**
statt auf die Rechnung; zwei Gegenproben mit entferntem Aufrufer, **2 vorhergesagt und 2
gezaehlt**, dann **1 und 1**. Suite 2772 → **2781 gruen, 0 uebersprungen**.

**Beide Schreibwege falten.** Die zweite Kontrolle fragte nicht die eigene Liste ab, sondern
den Baum: *wer schreibt sonst noch in `praegung_beruehrung`?* `beruehrung_anlegen` tat es —
ohne Aufrufer im Produktivcode und ohne Nachfuehrung. Haette nur der gebaute Weg sie bekommen,
stuende derselbe Defekt an der anderen Tuer, sobald ihn jemand benutzt.

**Der Rest war benannt und ist am selben Tag geschlossen:** Der Verfall *zwischen* zwei
Beruehrungen erreichte die Spalte nicht — `FALTUNG-OHNE-PERIODISCHEN-LAUF`, seit 15:20 UTC
erledigt durch `alle_faeden_nachfuehren` als vierten Schritt im Tageslauf.

### `FADEN-EMBEDDING-VERDUENNT` — der Faden trug den Turn, nicht sein Segment
**Kategorie:** CHA

**Zustand:** behoben am 01.09.2026, am selben Tag gefunden. Zeugen: `tests/test_praegung_faden_schema.py`.

**Symptom.** `praegung_faden.embedding` kam aus `state["prompt_embedding"]` — dem Vektor des **ganzen Turns**. Salienz und Emotion desselben Fadens kamen aus dem **staerksten Segment**, ausgewaehlt mit der ausdruecklichen Begruendung: *„Ein Turn mit einem einzigen einschneidenden Satz ist einschneidend, auch wenn drei belanglose daneben stehen — ein Mittel verduennte ihn."*

**Genau dieses Mittel stand im Embedding.** Der Faden trug die Wucht und den Sektor eines Segments und den Vektor des Durchschnitts.

**Warum das ein Defekt ist und nicht eine Einstellung.** Ein Faden wird ueber Embedding-Naehe wiedergefunden — das ist der einzige Weg, auf dem eine Reaktivierung ihn auffrischt (Konzept §7.12). `[gemessen]` 01.09.2026 ueber 19.900 Knotenpaare trennt diese Naehe ohnehin nur schwach: ohne geteiltes Thema Median **0,355**, mit geteiltem **0,504**, die Verteilungen ueberlappen breit. **Auf einem verduennten Vektor ist die Trennung noch schwaecher** — und ein Faden, der durch Zufallsaehnlichkeit aufgefrischt wird, wird unsterblich (§7.4). Dieselbe Ausfallklasse, wegen der `EMGRAV-SCHWELLE-TOT` ueberhaupt Vorbedingung dieser Schicht wurde.

**Behebung.** `_faden_embedding()` bettet den Segmenttext ein. Faellt der Embed-Dienst aus, wird auf den Turn-Vektor zurueckgefallen — **und die Torzeile vermerkt es**: `embedding_quelle` traegt `segment`, `prompt` oder `keins`. Ohne dieses Feld waere ein grober Faden von einem scharfen nicht zu unterscheiden, und die Naehe-Schwelle stuende auf gemischtem Material.

**Die Klasse ist allgemeiner als der Fall.** Wo eine Begruendung fuer **eine** von mehreren Eigenschaften desselben Objekts formuliert wird, gilt sie meist fuer alle — und die uebrigen werden nicht mitgezogen. Hier lag die Begruendung im Docstring der Funktion, die das Segment waehlt; das Embedding wurde vierzig Zeilen weiter unten aus einer anderen Quelle geholt.

**Verwandt:** `novaberg-lesson_l_groesse-am-falschen-ort.md` — dort dieselbe Familie mit vertauschten Groessen statt vertauschten Quellen.

> ### `[2×]` — dieselbe Klasse stand im selben Modul noch an einer zweiten Stelle
>
> **Behoben am 05.09.2026, vier Tage nach diesem Eintrag.** Der **Praegungszug** las weiterhin
> `state["prompt_embedding"]` — denselben gemittelten Turn, aus demselben Grund falsch. Ein Turn
> ueber zwei Themen bekommt einen Vektor zwischen beiden und liegt danach **keinem** der
> zugehoerigen Straenge nahe; die Naehe eines Mittelwerts ist keine Naehe.
>
> **Die Begruendung stand seit dem 01.09. woertlich im selben Modul** — in `_faden_embedding`,
> zwanzig Zeilen ueber der Stelle, die sie ignorierte. Die Behebung hatte den **gefundenen Fall**
> repariert und nicht nach dem naechsten gesucht.
>
> **Gefunden hat es eine Frage des Eigentuemers** (*„wenn mehrere Saetze mit verschiedenen Themen
> kommen, wie wollen wir dann die Naehe ausrechnen?"*), kein Zeuge und keine Pruefung.
>
> **Die Klasse ist damit hochgestuft und die Konsequenz benannt:** Wer einen Defekt behebt, sucht
> die **zweite Stelle derselben Klasse — im selben Modul zuerst.** Ein Grep auf die Quelle, aus der
> der falsche Wert kam (`prompt_embedding`), haette sie in Sekunden gezeigt.

## 25.08.2026, nachmittags — zwei Defekte, die ein Linter-Treffer sichtbar gemacht hat

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

Beide standen jahrelang gruen und waren mit keinem Zeugen und keiner Messung zu finden:
Ihr Symptom ist die **Abwesenheit** einer Wirkung, und die sieht aus wie ein ruhiger Lauf.
Sichtbar wurden sie ueber `F841` — eine Variable, die zugewiesen und nie gelesen wird.

#### `VORHER-ZUSTAND-OHNE-SPUR` — sechsmal geladen, nie protokolliert ✅
**Kategorie:** CHA

**Zustand:** behoben am 25.08.2026, mit acht Zeugen.

**Symptom.** `agents/direktiven/crud.py` und `agents/charakter_identitaet/crud.py` lesen vor
jedem Schreibvorgang den bisherigen Datensatz — `vorher = _read_by_id(target_id)`, je
dreimal, unmittelbar vor `UPDATE ... SET aktiv = FALSE`. **Der Wert wurde in keiner der
sechs Stellen weiterverwendet.** Der `schritte`-Eintrag, in base.py ausdruecklich als
Audit-Trail deklariert, trug `id` und `verifiziert` und nicht den ersetzten Inhalt.

**Was das kostet.** Nach dem Soft-Delete ist die Zeile noch da, aber nicht mehr als *die
vorherige* erkennbar; bei `_update` liegt daneben die neue. Wer spaeter fragt, was ersetzt
wurde, hat keine Quelle. `18_NACHVOLLZIEHBARKEIT` verlangt die Eingangsgroessen einzeln —
hier war die Eingangsgroesse geladen und fallengelassen.

**Dass es sechsmal identisch in zwei Modulen steht, ist der eigentliche Befund:** keine
vergessene Zeile, sondern eine Absicht ohne Empfaenger.

**Abhilfe.** `_vorher_spur()` je Modul; der `schritte`-Eintrag traegt den ersetzten Inhalt.
Fehlt der Datensatz, steht dort `{"gelesen": False}` — ein leerer String saehe aus wie eine
leere Anweisung und waere ein Default, der wie ein Messwert aussieht.
`tests/test_vorher_spur.py`, **acht Zeugen**; Gegenprobe 4 vorhergesagt / 4 gezaehlt.

---

## 23.08.2026 — die Naht zwischen GV-Knoten und Haltungsstand

### `FUEHRUNGSMASS-AUF-FALSCHER-EBENE` — behoben am 23.08.2026
**Kategorie:** CHA

**Zustand:** behoben. `_initiative_aus_state` liest das Fuehrungsmass aus `state["gv_detail"]["initiative"]`, wo der Erzeuger es ablegt. Bis dahin las es `state["initiative"]` — einen Schluessel, den **niemand setzt**.

**Befund (23.08.2026).** **Der Defekt sass nicht in einem der beiden Bauteile, sondern zwischen ihnen.** Ueber den ganzen Baum gemessen: **ein** Schreiber (`_gv_detail_bauen`, `gespraechsvektor.py:1087`), **ein** Leser (`haltung.py:175`), zwei verschiedene Ebenen. Derselbe Knoten liest die Landschaft 130 Zeilen weiter richtig aus `gv_detail`.

**Die Folge ist der Stillstand des Impulswegs, und er ist auf den Tag datierbar.** Der Leser gab auf **jedem** Turn `(None, "gv_ohne_lauf")` zurueck; Riegel 2 der Zustellung behandelt ein fehlendes Fuehrungsmass als *unbekannt* und laesst dann keinen Einwurf durch. Riegel und Leser kamen im **selben Commit** (`5bd2ab4`, 15.08.2026) — und der letzte Impuls-Turn stammt vom **15.08.2026**. Der Riegel hat seit seinem Bau nie geoeffnet.

**Was er gekostet hat, ist eine Zahl.** Ueber 595 protokollierte Fuehrungsmasse lagen **217 (36,5 %)** bei oder unter `GV_INITIATIVE_SCHWELLE` = −0,05, also im Bereich *Nova fuehrt*. So oft haette der Riegel geoeffnet. Messwerkzeug: `labor/2026-08-23_fuehrungsmass_verteilung.sql`.

> **Warum acht Tage lang nichts anschlug, gehoert zum Befund.** Der Riegel schliesst bei Unbekanntem, und das ist richtig so (`novaberg-eigenzeit_k.md` §2.5: *„Der Ausfall oeffnete den Schalter, statt ihn zu schliessen"*). Ein dauerhaft geschlossener Riegel sieht deshalb aus wie eine Figur, die gerade nicht zugehen will — und `gv_ohne_lauf` ist ein vorgesehener Grund, keine Fehlermeldung. **Ein Ausfall, der sich als gueltige Entscheidung tarnt, hat keinen Melder.**

**Im Betrieb belegt am 23.08.2026:** Der Haltungsstand trug vor dem Eingriff `initiative` leer mit `initiative_grund=gv_ohne_lauf`, danach `initiative = 0.409` mit leerem Grund. Die Riegelzeile ging von `[wollen+0.55 frequenz- ruhe+]` auf `[wollen+0.49 frequenz-0.41 ruhe+]` — der Riegel entscheidet jetzt auf einer **Messung** statt auf Unbekanntem. Er sperrte dabei weiter, und zwar richtig: `initiative_bit` ist `0 if wert > schwelle else 1`, ein hoher Wert heisst *der Nutzer fuehrt*, und der Mensch hatte gerade geschrieben.

Zeugen: `tests/test_fuehrungsmass_naht.py` (8) — der Naht-Zeuge ruft den **echten** Erzeuger und schickt seine Ausgabe durch den **echten** Leser; ein Zeuge, der das Dict selbst zusammenstellt, prueft seine eigene Vorstellung von der Naht. Gegenprobe: 4 vorhergesagt, **5 gezaehlt**. Suite `Ran 2213 tests — OK`.

**Geschlossen, wenn** Der Haltungsstand traegt das Fuehrungsmass, das der GV-Knoten gerechnet hat.

---

### `GRUND-NENNT-FALSCHE-URSACHE` — behoben am 23.08.2026
**Kategorie:** CHA

**Zustand:** behoben. Drei Sachverhalte tragen drei Namen: `gv_ohne_lauf` (kein `gv_detail` — der Knoten lief wirklich nicht), `fuehrung_fehlt_im_detail` (er lief und liess das Mass aus), `masse_fehlen` / `ohne_wert` (er rechnete und kam nicht durch).

**Befund (23.08.2026).** **Der Grund behauptete, der GV-Knoten sei nicht gelaufen — und genau das hat die Untersuchung verzoegert.** Derselbe Haltungsstand trug `cluster=foyer`, und `cluster` kommt aus `gv_detail`: Der Knoten **war** gelaufen. Der Zweig griff aber, sobald `state["initiative"]` kein `dict` war, und das ist nicht dasselbe.

**Die Klasse ist allgemeiner als der Fall:** Ein Grundtext ist eine Aussage ueber die **Ursache**, nicht ueber die Stelle, an der der Code abbricht. Wer beides gleichsetzt, schickt jede spaetere Untersuchung an den falschen Ort — hier an den GV-Knoten, waehrend der Defekt im Leser sass.

Zeugen: `tests/test_fuehrungsmass_naht.py::DreiAusfaelleDreiNamenTest` (5), darunter der Fall, den `gv_ohne_lauf` bisher falsch benannte, und eine Zusicherung ueber alle vier Ausfaelle, dass keiner eine Zahl liefert.

**Geschlossen, wenn** Jeder Grund benennt die Lage, die ihn ausgeloest hat.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `PROFILPROMPT-OHNE-GESCHLECHT` — das Modell raet, im selben Lauf verschieden
**Kategorie:** CHA

**Zustand:** behoben — gegen HEAD `12a7c6a` gebaut am 22.08.2026. Das Genus der Figur steht in `ASSISTANT_GENUS` (`config.py`, Vorgabe `w`), `_perspektive_aufloesen` liefert daraus `pronomen`, `pronomen_dat`, `pronomen_akk` und `possessiv`, und **jeder der fuenf Prompts gibt die Pronomen ausdruecklich vor**. Zeuge: `tests/test_traegerformen.py::test_jeder_prompt_gibt_das_genus_vor`.

**Die Formen allein genuegen nicht, und das ist die Lehre des Eintrags.** Ein gefuellter Platzhalter richtet den **Prompt**-Text; das Modell schreibt aber seinen **eigenen** und raet dort weiter. Deshalb steht die Vorgabe als Satz im Prompt und nicht nur als Formensatz in der Funktion.

**Der Ort ist eine Entscheidung, kein Zufall.** Der Backlog-Eintrag `ASSISTENT-GESCHLECHT-PRONOMEN` verlangte *„ein Geschlechts-Attribut am Charakter"* — also in der Datenbank. Gelegt ist es in die Konfiguration, **dorthin, wo heute der Name steht**: Solange `ASSISTANT_NAME` global per env kommt, waere ein paarbezogenes Genus daneben die Inkonsistenz. Wandert der Name mit `ASSISTENT-NAME-LAUFZEIT` in die DB, wandert das Genus mit; der Rest steht dort.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Kein Profil-Prompt kennt das Geschlecht seines Traegers, und das Modell raet es — im selben Lauf verschieden.** `_perspektive_aufloesen` liefert drei Formen (`traeger`, `traeger_gen`, `perspektive`) und **kein Pronomen**. Die Prompts umgehen das, indem sie ueberall `{traeger}` wiederholen; sobald aber ein Satz ein Pronomen braucht, entscheidet das Modell. **Belegt am 18.08.2026** an einem Profil mit dem Traegernamen »Juno«: Der Kern-Hash fuehrt durchgehend »er/sein«, das im selben Lauf erzeugte Beziehungsprofil fuehrt im Schlusssatz das **saechliche** Pronomen — zwei Genera fuer denselben Traeger, ohne dass irgendetwas anschlaegt. Bei einem Namen ohne eindeutiges Genus ist das der Normalfall, nicht die Ausnahme. **Es trifft nicht nur die Ausgabe, sondern jede kuenftige Prompt-Zeile:** Ein Satz wie *„wo {traeger} beschreibt, was sie tut"* ist fuer einen maennlichen oder saechlichen Traeger falsch — die heutige Bauart zwingt jede Anweisung in die Wiederholung des Namens. **Was fertig waere:** ein Geschlecht je Charakter, daraus abgeleitet Nominativ, Genitiv, Dativ, Akkusativ und Possessivformen als Prompt-Parameter, wie `traeger_gen` es fuer den Genitiv bereits vormacht.

**Geschlossen, wenn** Jeder Profil-Prompt bekommt das Geschlecht seines Traegers als Datum, nicht als Vermutung.

---

### `SPEICHENWERT-NICHT-MEDIAN` — behoben am 23.08.2026
**Kategorie:** CHA

**Zustand:** behoben. Entschieden: **der Speichenmedian laeuft als zweites, nicht rechnendes Feld mit.** `F-RAD-2` bleibt unangetastet — das gespeicherte Rad ist weiter das des Median-Laufs, und Faktor wie Versatz werden allein daraus gerechnet. Daneben tragen beide Raeder `speichen_median` (der Median je Speiche ueber alle gelungenen Laeufe) und `speichen_ohne_mehrheit` (die Namen der Abweichungen); eine Logzeile nennt sie. Eine Quelle fuer beide Raeder: `speichenweise_mediane` und `speichen_ohne_mehrheit` in `agents/charakter/destillation.py`. Zeugen: `tests/test_speichen_median.py` (8), Gegenprobe 3 vorhergesagt / 3 gezaehlt, Suite `Ran 2196 tests — OK`.

> **Die Messung ueber den ganzen Bestand korrigiert den Befund.** Er stuetzte sich auf **drei** Laeufe vom 19.08.2026 und meldete Initiative 5 von 10, Zuwendung 0 von 12. Gegen alle 95 Erhebungen in `charakter_rad_messung` gerechnet: **Initiative 48 von 480 Speichen (10,0 %), Zuwendung 77 von 564 (13,7 %)** — das Zuwendungsrad ist **staerker** betroffen, nicht gar nicht. Die drei Laeufe waren nicht repraesentativ. Messwerkzeug: `labor/2026-08-23_speichen_ohne_mehrheit.py`.

> **Das Werkzeug meldete zuerst 0 Speichen bei 95 Erhebungen** — es las die zweistufige Gestalt `hoch`/`runter`, waehrend `charakter_rad_messung.speichen` **flach** liegt. Eine Null, die aussah wie Einigkeit. Der Helfer `_flach` kennt seither beide Gestalten.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der gespeicherte Speichenwert ist nicht der Median seiner Erhebungen — bei der Initiative gilt das für die Hälfte der Speichen.** `F-RAD-2` legt fest, dass das Rad des **Median-Laufs** gespeichert wird, und begründet das gut: Ein gemitteltes Rad erzeugte Ausprägungen, die kein Lauf vergeben hat, und `Rad × Züge = Faktor` wäre nicht mehr von Hand nachrechenbar. **Der Preis war nicht benannt:** Der Median-Lauf wird über den **Faktor** bestimmt, nicht je Speiche. Gemessen am 19.08.2026 über drei Läufe: Beim Initiative-Rad tragen **5 von 10** Speichen einen gespeicherten Wert, den der Median ihrer eigenen Läufe nicht stützt — `behutsamkeit` steht auf 0,60, während zwei von drei Läufen 0,40 sagten; `gespraechsdistanz` auf 0,10 bei Median 0,20. Beim Zuwendungsrad trat der Fall nicht ein (0 von 12), weil dort die stark ziehenden Speichen zeichengleich sind. **Die Festlegung bleibt richtig, die Anzeige ist es nicht:** Wer eine einzelne Speiche liest — im Client, in einer Auswertung, in einem Befund —, bekommt einen Wert ohne Mehrheit hinter sich, und nichts sagt es ihm. Zu entscheiden: ob neben dem Median-Lauf-Rad die speichenweisen Mediane als eigenes, nicht faktortragendes Feld mitlaufen.

**Geschlossen, wenn** Der gespeicherte Speichenwert ist der Median seiner Erhebungen — dieselbe Bauart, die fuer die Raeder gilt: mehrfach erheben, den mittleren Lauf speichern.

---

### `NEUER-NUTZER-OHNE-UMFANGSVORGABE` — gar keine Vorgabe beim ersten Turn
**Kategorie:** CHA

**Zustand:** behoben — gegen HEAD `880be4f` gehalten am 22.08.2026. Ein Paar ohne `charakter_hash`-Zeile bekommt das **neutrale Rad** statt `(None, 'fehlt')`: zwoelf Speichen auf 0.0, Herkunft `'neutral'` (`memory/charakter.py::_neutrales_rad`). Der Haltungsraum rechnet damit normal, und die Landschaft traegt den Turn allein.

> **Die Begruendung ist keine technische, und deshalb war es eine Entscheidung und kein Bau:** Ein Rad aus Nullen ist gegenueber einer Person, ueber die noch nichts erhoben wurde, die **anfaenglich vorurteilsfreie Haltung** — nicht ein fehlender Wert, sondern der richtige. Entschieden am 22.08.2026.
>
> **Am echten Ladepfad gegen die Produktivdatenbank gemessen:** eine unbekannte Kennung liefert `quelle=neutral`, 12 Speichen, und `haltung_berechnen` daraus `umfang: grundwert=0.9, modifikation=0.0, ergebnis=0.9` — alle fuenf Groessen belegt. Zum Vergleich dasselbe fuer ein eingespieltes Paar: `modifikation=0.127, ergebnis=0.925`. **Die Landschaft traegt, das Rad moduliert.**
>
> **Drei Herkuenfte statt zwei, und das ist der Preis des Baus:** `destilliert` (erhoben), `default` (erhoben, ohne Ergebnis), `neutral` (nie erhoben). Wer die letzten beiden gleich nennt, kann spaeter nicht mehr zaehlen, wie viele Paare ueberhaupt durch die Destillation gelaufen sind. **Ein Lesefehler bleibt `fehlt`** — sonst saehe er aus wie ein neues Paar, und genau diese Verwechslung verhindert die Unterscheidung seit ihrem Bau.
>
> Vier Zeugen, einer davon auf die Gegenrichtung; **ein bestehender Zeuge ist entfallen** (`test_fehlende_zeile_wird_abgelehnt`) — er hielt die alte Entscheidung fest und steht als Begruendung im Docstring seines Nachfolgers. Gegenprobe 3 vorhergesagt / 2 gezaehlt (der Eingriff nahm nur die Rueckgabe zurueck, nicht die Logstufe). Suite `Ran 2093 tests — OK`.
>
> **Nicht gemessen ist der Turn selbst.** Die Kette bis zur Haltung ist am echten Bestand belegt, der Beleg *„ein neuer Nutzer bekommt jetzt Regie"* braucht einen Lauf mit frischer Kennung.

**Befund (17.08.2026), aus der Fundliste uebernommen.** **Ein neuer Nutzer bekommt gar keine Umfangsvorgabe.** Der Haltungsraum meldet `Rad nicht ladbar (fehlt)` und der Responder daraufhin `Keine Haltung im Zustand — dieser Turn bekommt KEINE Umfangsvorgabe`. Gemessen an fünf frisch angelegten Kennungen: **9 von 9 Turns ohne Regie**, während dasselbe Fenster für das eingespielte Paar **10 von 10 mit** zeigt. Das Charakter-Rad entsteht erst über Destillation aus Bestand, den ein neuer Mensch noch nicht hat. **Die Lücke liegt damit genau in den ersten Gesprächen** — dort, wo sich ein erster Eindruck bildet. Der Ausfall ist laut protokolliert und nicht still; was fehlt, ist ein Anfangswert für den Fall ohne Rad.

**Geschlossen, wenn** Auch der erste Turn eines neuen Nutzers traegt eine Umfangsvorgabe.

---

### `KERNHASH-LIEST-TURNWORTLAUT` — Wortlaut statt Langzeitgedaechtnis
**Kategorie:** CHA

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `novaberg-pixie-character-hash.md:45` ist am 16.08.2026 nachgezogen — die alte Quellenangabe steht durchgestrichen daneben. Offen bleibt eine andere Frage: 40 von 444 Zeilen decken 2 von 20 Bestandstagen.

**Befund (16.08.2026), aus der Fundliste uebernommen.** **Der Kern-Hash liest den Turn-Wortlaut, nicht das Langzeitgedächtnis.** `agents/charakter/agent.py:168` übergibt an `kern_hash_destillieren` das Ergebnis von `_turns_laden` — 40 Rohturns aus `pipeline_log` (`art='turn_roh'`). `novaberg-pixie-character-hash.md` §3.1 führt als Quelle weiterhin `lzg_knoten`, *„selektiert und gewichtet nach Anker-Stärke `gewicht_absolut`"*. Der Code-Kommentar nennt die Umstellung samt Datum (10.08.2026) und Begründung; die Doku ist nicht nachgezogen. Gemessen am produktiven Paar: **444 `turn_roh`-Zeilen, davon 40 gelesen (9 %)**, und die decken **2 von 20** Bestandstagen ab — für ein Profil, dessen erklärter Gegenstand der dauerhafte Wesenskern ist und das laut §3.1 *„sich langsam verändert"*.

**Geschlossen, wenn** Der Kern-Hash liest die Quelle, die das Konzept ihm zuweist.

---

### `HALTUNGSSTAND-OHNE-LOGZEILE` — als entschieden geschlossen am 23.08.2026
**Kategorie:** CHA

**Zustand:** geschlossen, **nicht behoben** — und der Unterschied ist die Sache selbst. Der Befund verlangte nicht die Zeile, sondern dass die Entscheidung *benannt* wird statt stillschweigend zu gelten. Sie ist benannt, seit `7c64fe9` (15.08.2026) und damit **vor** der Aufnahme des Eintrags: Der Docstring von `_stand_schreiben` traegt sie unter der Ueberschrift *Zwei Speicher, zwei Gegenstaende* — die Zeile im `pipeline_log` traegt den **Verlauf** und ist die Grundlage der Nachkalibrierung, dieser Stand traegt den **Zustand** und beantwortet die Frage eines Dienstes ausserhalb des Graphen.

Nachgemessen am 23.08.2026: `graph/nodes/haltung.py` enthaelt weiterhin kein `log_db_write`. Der **Preis ist benannt und bleibt**: Die Haeufigkeit fehlgeschlagener Standschreibungen ist nicht aus der Reihe zaehlbar, sondern nur aus dem Dateilog. Wer das aendern will, baut keine zweite `db_write`-Zeile — die fuehrte dieselbe Zahl doppelt —, sondern eine eigene Art, die nicht als Messwert mitzaehlt.

**Befund (15.08.2026), aus der Fundliste uebernommen.** **Der Haltungsstand hat keine Zeile im `pipeline_log`.** `ei_calc_persist` schreibt für seinen Redis-Schreibvorgang ein `log_db_write`; der `haltungsraum`-Knoten tut das für den Stand nicht — die Berechnungszeile trägt die Werte, der Stand ist eine Kopie davon, und ein Fehlschlag meldet sich über `logger.exception` im Dateilog. **Die Häufigkeit fehlgeschlagener Schreibvorgänge ist damit nicht aus der Reihe zählbar**, sondern nur aus dem Log. Bewusst so gelassen, weil ein zweiter Eintrag je Turn dieselbe Zahl doppelt führte; die Entscheidung gehört benannt, nicht stillschweigend getroffen.

**Geschlossen, wenn** Der Haltungsstand schreibt seine Zeile wie jeder andere Knoten.

---

### `UEBERSTEUERUNG-AB-FUER-DREIERSKALA` — auf die alte Skala geeicht
**Kategorie:** CHA

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. `ei/haltung.py:284` steht auf 0.9 statt 1.0; `tests/test_rad_skala.py:52` haelt die Eichung.

**Befund (11.08.2026), aus der Fundliste uebernommen.** `UEBERSTEUERUNG_AB = 1.0` in `ei/haltung.py` ist für die Dreierskala geeicht und greift auf der feinen Skala nicht mehr. Über alle Zuwendungsrad-Läufe: grob 50 Läufe mit `distanz >= 1.0` in 27 (54 %) und `wissbegier >= 1.0` in 26 (52 %); fein 30 Läufe mit 1 (3 %) und 0 (0 %). Beide Übersteuerungen — die einzigen zwei Wege, auf denen eine Speiche die Grenze ihrer Landschaft durchbrechen kann — sind damit praktisch abgeschaltet, ohne Meldung und ohne roten Test. Die Schwelle verlangt eine Entscheidung, keinen Wert: Vorher feuerte sie auf dem Rundungsanschlag, den die feine Skala gerade beseitigt hat. **Auf Novas Verhalten wirkt es heute nicht** — die Haltung wird gerechnet, protokolliert und angezeigt, aber kein Prompt liest sie (Konzept-Status). Die Wirkung tritt in dem Moment ein, in dem §3 gebaut wird; bis dahin betrifft der Schaden die gemessenen und protokollierten Zahlen.

**Geschlossen, wenn** `UEBERSTEUERUNG_AB` ist auf die feine Skala geeicht.

---

### `PERSPEKTIVE-OHNE-DATIV` — kein Dativ fuer den generischen Nutzer
**Kategorie:** CHA

**Zustand:** behoben — gegen HEAD `12a7c6a` gebaut am 22.08.2026. `_perspektive_aufloesen` liefert alle vier Kasus (`traeger`, `traeger_gen`, `traeger_dat`, `traeger_akk`); kein Prompt setzt den Traeger mehr im falschen Kasus ein. Zeuge: `tests/test_traegerformen.py::test_kein_prompt_traegt_eine_falsche_form` — er haelt **beide** Perspektiven gegen neun gemessene Fehlformen und wird rot, sobald eine zurueckkehrt.

**Der Eintrag nannte vier Stellen, das Rendern fand neun.** Neben den vier »von«-Stellen standen im gerenderten Text auch *„Was verraet die ART der Kommunikation ueber **der Nutzer**"*, *„charakterisiert **der Nutzer**"*, *„welche Emotionen tragen **der Nutzer** langfristig"*, *„an dem man **der Nutzer** erkennt"* und *„was **der Nutzer** wichtig ist"* (Dativ). Vier der fuenf »von«-Stellen sind dabei nicht auf den Dativ gegangen, sondern auf das Genitivattribut — *„das dauerhafte Wesen des Nutzers"* statt *„von dem Nutzer"*, was fuer den Eigennamen dieselbe Zeile richtig macht (*„das dauerhafte Wesen Novas"*).

**Befund (11.08.2026), aus der Fundliste uebernommen.** `_perspektive_aufloesen` kennt für den generischen Nutzer nur Nominativ und Genitiv (`der Nutzer` / `des Nutzers`), kein Dativ. Vier der fünf Profil-Prompts setzen den Träger hinter „von" ein und lesen dadurch bei jedem menschlichen Paar „ein kompaktes Persönlichkeitsprofil von **der Nutzer**". Für die Assistentin tritt der Fall nicht auf, weil dort ein Eigenname steht.

**Geschlossen, wenn** `_perspektive_aufloesen` kennt alle Faelle, die die Prompts einsetzen.

---
## Behobene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in . Ueberschrift und Text stehen in jedem empfangenden Teil.

> Der eigene Text dieses Abschnitts steht im Wegweiser [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md).

### Chat 135 — beim Bau der Phasensteuerung (11.08.2026)

#### RAD-AELTER-ALS-PROFIL — das gespeicherte Rad gehörte zu einem Text, den es nicht mehr gab ✅ behoben
**Kategorie:** CHA

**Symptom.** Nach einem Bogen stand in `charakter_hash` ein Rad von 09:23 neben einem Beziehungsprofil von 10:00. Die Messzeile trug `quelle_zeichen = 373`, das Profil daneben hatte 1456.

**Ursache.** `RAD_MESSUNG_ABSTAND_STUNDEN = 12`. In einem Bogen von 40 Minuten wurde das Rad **einmal** erhoben; jeder spätere Destillationslauf fand `messung_faellig` = nicht fällig, erneuerte die Profile und ließ das Rad stehen. Der Zeitpunkt der einen Messung hing an der Auslastung des Modells, nicht am Gegenstand.

**Warum es zählt.** Das Rad ist die Eingangsgröße der Salienz **jedes** Nutzer-Beitrags, und es war an einen Text gebunden, der zu dieser Zeit ein Drittel seiner späteren Länge hatte. Die Prüfsumme in `charakter_rad_messung` hat den Fall die ganze Zeit festgehalten — gelesen hatte sie niemand.

**Behoben am 11.08.2026.** Eine Messreihe bestimmt den Zeitpunkt selbst: `MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION` legt die automatischen Auslöser still, `RAD_MESSUNG_ABSTAND_STUNDEN=0` hebt die Sperre für den Lauf auf, und der Bogenläufer stößt nach dem Schnitt und am Ende an. Belegt: Nach dem Umbau stimmen `profil_am` und `rad_am` beider Paare auf die Sekunde überein. Im Regelbetrieb bleiben die zwölf Stunden.

---

#### HASH-DIRTY-DRITTER-SETZER — die Stilllegung war unvollständig ✅ behoben
**Kategorie:** CHA

**Symptom.** Nach einer Phase mit stillgelegter Automatik stand `hash_dirty:sarah:nova` wieder gesetzt da. Die Vorbedingung des nächsten Laufs schlug an.

**Ursache.** Drei Stellen setzen das Flag — `memory/kzg.py`, `agents/kzg/queues.py` und **`agents/synapsen_promotion/agent.py`**. Nur die ersten beiden waren stillgelegt. Die Promotion läuft **nach** den Turns und schärfte die Destillation damit erneut, an einer Stelle, die niemand bestimmt hat.

**Warum es zählt.** Es untergräbt genau die Eigenschaft, für die der Schalter gebaut wurde: die Bestimmtheit des Zeitpunkts. Der Bogen sah dabei vollständig aus — beide Phasen lieferten Profil und Rad; nur die Vorbedingung des Folgelaufs machte es sichtbar.

**Behoben am 11.08.2026**, samt einem Zeugen, der die Setzer am Syntaxbaum **zählt** statt sie zu erinnern: Ein vierter bekommt ein rotes Licht, statt in Wochen eine unerklärliche Erhebung zu erzeugen.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Datenqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### CHAR-BEZ-STALE — Veraltetes Beziehungsprofil im Prompt (Chat 71) ✅ Behoben Chat 83
**Kategorie:** CHA
**Status:** ✅ Behoben Chat 83
**Symptom:** Der GV-Node und der Responder erhalten als `nova_beziehung`:
  "Nova sieht ihren Nutzer als eine rein sachliche und effizienzorientierte Instanz,
  mit der sie eine rein funktionale und professionelle Beziehung pflegt."
Das widerspricht dem tatsächlichen Beziehungsprofil in der DB (User-Perspektive):
  "Der Nutzer pflegt eine sehr vertraute und emotionale Beziehung zum Assistenten,
  die durch eine hohe Dynamik des Vertrauens und einen empathischen Ton geprägt ist."
**Ursache (Vermutung):** Der Enricher lädt möglicherweise das falsche Paar
  (user_id/character_id vertauscht) oder es existiert ein zweiter Hash-Eintrag
  mit veralteten Daten. Muss untersucht werden: Welcher Eintrag liefert das
  "rein sachliche" Profil?
**Auswirkung:** Schwer. Nova antwortet mechanisch und kurz trotz warmem Gespräch.
  GV3-Strategie und GV4-Wissenslücken können nicht gegen ein falsches Identitäts-
  profil in Primacy-Position ankämpfen.
**Debug:** `SELECT user_id, character_id, beziehungsprofil FROM charakter_hash;`
  um alle Einträge zu sehen.

**✅ Behoben Chat 83:**
Empirisch verifiziert per SQL-Abfrage gegen `charakter_hash`. Beide Beobachter-Sichten (`meister → nova` und `nova → meister`) zeigen jetzt vertraute, emotional warme Beziehungsprofile statt der ursprünglichen "rein sachlichen, effizienzorientierten Instanz". Wirkmechanismus: Chat-82-Backfill der 19 Default-EI-Profile (`Korrektur.py` mit Qwen3-32B) plus Chat-83-Cluster-Aggregations-Fix (M4 Teil 2) — beides zusammen liefert dem CharakterAgent jetzt verlässliche Quelldaten.

---

### Chat 72 — Dreischicht-Integration + GV-Refactoring (Folgebugs)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### CHAR-HASH-FILTER — `beobachter=assistant`-Einträge fließen in Charakter-Hash ✅
**Kategorie:** CHA

**Entdeckt:** Chat 72

**Symptom:** Der Charakter-Hash zieht beim Aufbau auch Einträge mit `beobachter=assistant` ein, statt nur User-Beobachtungen zu konsolidieren. Folge: Novas Selbstbeschreibungen mischen sich mit dem User-Beziehungsprofil.

**Lösungsansatz:** Filter `WHERE beobachter='user'` an den Hash-Aufbauschritten ergänzen (Charakter-Hash + Beziehungsprofil).

**Prio:** Mittel — verschiebt das Hash-Bild von "wie der User Nova sieht" zu einer gemischten Selbst-/Fremdwahrnehmung. Beobachten zusammen mit CHAR-BEZ-STALE.

**Behoben Chat 73:** Beobachter-Filter in `_kzg_laden()` + 20 Altdaten von `kzg:nova:nova:*` nach `kzg:nova:meister:*` migriert (DUMP/RESTORE).

---

*Aktualisiert Chat 72: Vier Fixes in Behoben-Tabelle (MODUS-LEER, VEKTOR-LEER, AROUSAL-330, ZIEL-LABEL-LEER). Vier neue offene Bugs aus Dreischicht-Integration: ECHO-BUG (Hoch, durch geplanten Reducer adressiert), PENDING-RELEVANZ, MODUS-KALIBRIERUNG, CHAR-HASH-FILTER. Beobachtungen: KZG-DEDUP/KZG-KERN-BLIND wurden in Chat 64 als gelöst markiert, in Chat 72 jedoch wieder beobachtet (dreifache Katze-bei-Lumi-Einträge mit steigender Salienz) — bei nächster Wiederholung re-evaluieren. ZEIT1 (gefixt Chat 41) zeigt unter Gemma4 wieder Symptome — Modell-Verhalten, nicht Regex-Regression.*

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### HASH-DIRTY-SETZER-DRIFT — fünf Setzer, drei verschiedene Bauarten ✅
**Kategorie:** CHA

**Zustand:** behoben — gegen HEAD `9bcd214` gemessen am 24.08.2026. **Der beschriebene Zustand existiert nicht mehr.** Von fünf Setzern sind drei übrig (`memory/kzg.py:546`, `agents/kzg/queues.py:135`, `agents/synapsen_promotion/agent.py:472`); `agents/promotion/agent.py` setzt das Flag an keiner Stelle mehr. **Alle drei stehen hinter einem `PIXIE_AKTIV`-Gate** — auch `queues.py`, dessen fehlendes Gate der Befund war: `queues_befuellen` kehrt bei `not PIXIE_AKTIV` schon in Zeile 43 zurück, und der Setzer steht in derselben Funktion.

> **Ein Rest bleibt, und er ist kleiner als der Befund:** Die Meldung beim Übersprung ist weiter uneinheitlich. `memory/kzg.py:539` schreibt eine `debug`-Zeile mit dem Grund, `queues.py` meldet nur das Kürzel `dirty_flag` in einer Sammelzeile, und `synapsen_promotion/agent.py:464` überspringt mit einem blanken `pass` — ohne jede Zeile. Das ist die Logspalte der Tabelle, nicht die Gate-Spalte.

**Entdeckt:** Chat 110, im selben Audit.

**Klasse:** Uneinheitlicher Schreibpfad. Severity **niedrig**, aber sie erklärt, warum das Flag schwer zu beobachten ist.

**Symptom:** Fünf Stellen setzen `hash_dirty`, in drei Bauarten:

| Ort | `PIXIE_AKTIV`-Gate | Log bei Übersprung |
|---|---|---|
| `memory/kzg.py:448` | ja | `debug` |
| `agents/promotion/agent.py:331` | ja | `debug` |
| `agents/promotion/agent.py:816` | ja | `debug` |
| `agents/synapsen_promotion/agent.py:351` | ja | **keins** |
| `agents/kzg/queues.py:111` | **keins** | — |

`queues.py:111` setzt das Flag also auch bei `PIXIE_AKTIV=False` und meldet es nur als Kürzel `dirty_flag` in einer Sammelzeile (`logger.info(f"KZG-Queues: {', '.join(aktionen)}")`), nicht als eigene Zeile mit dem Key.

**Reproduktion:** `grep -rn "hash_dirty" --include='*.py' server/ | grep -v test` — die fünf Setzer und ihre Umgebung vergleichen.

~~**Status:** Offen.~~ **Verwandt:** HASH-DIRTY-WAISENKEYS.

---

## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Charakter**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Wissen](novaberg-bugs-archiv-wissen.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### CRUD-REACTIVATE-STAMP — Reactivate setzt deaktiviert_am nicht auf NULL zurück
**Kategorie:** CHA

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. `charakter_anweisungen` traegt heute `id`, `user_id`, `anweisung`, `erstellt_am`, `aktiv` und `geaendert_am`; die Spalte `deaktiviert_am`, um die es geht, gibt es nicht. Die Invariante `aktiv=TRUE ⇒ deaktiviert_am IS NULL` hat damit keinen Traeger mehr. **Der Schwesterbefund `CRUD-REACTIVATE-COEXIST` steht dagegen weiter und ist am 25.08.2026 im Bestand belegt.**
**Entdeckt:** Chat 49, Test "Reactivate ID 8"
**Symptom:** Nach `reactivate` steht der Eintrag zwar auf `aktiv=TRUE`, aber `deaktiviert_am` behält den alten Zeitstempel. Invarianz-Verletzung wie bei CHAR-ID4-ORPHAN, nur in die andere Richtung: `aktiv=TRUE` mit `deaktiviert_am IS NOT NULL`.
**Reproduktion:** Charakter-Eintrag reaktivieren, danach in DB prüfen: ID hat `aktiv=t` und gefüllten `deaktiviert_am`.
**Ursache (vermutet):** Die Reactivate-Logik in `agents/charakter_identitaet/crud.py` macht nur `UPDATE ... SET aktiv=TRUE WHERE id=X`, ohne `deaktiviert_am = NULL` mitzusetzen.
**Lösungsansatz:** Ein zusätzliches `deaktiviert_am = NULL` im UPDATE. Trivial. Wird vermutlich beim Umbau im Zuge des Fachabteilungs-Agenten-Epics ohnehin mitgefixt.
**Prio:** Niedrig — funktional unkritisch, Daten-Integritätsproblem (bi-temporale Invariante verletzt). Für Analyse der Charakter-Historie störend.

---

#### CHAR-ID4-ORPHAN — Charakter-Eintrag mit gebrochener bi-temporaler Invariante
**Kategorie:** CHA

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. Die Tabelle `charakter_identitaet`, in der die verletzte Invariante gemessen wurde, existiert nicht mehr; der Agent schreibt heute nach `charakter_anweisungen`, und die kennt weder `deaktiviert_am` noch die bi-temporale Bauart. **Wer die Invariante zurueckholt, holt diesen Befund mit** — der Eintrag bleibt deshalb stehen.
**Entdeckt:** Chat 49, DB-Inspektion
**Symptom:** In `charakter_identitaet` existiert ID 4 mit `aktiv=f` und `deaktiviert_am IS NULL`. Die bi-temporale Invariante verlangt: `aktiv=f` ⇒ `deaktiviert_am IS NOT NULL`.
**Kontext:** ID 4 ("Ein junges, freches, lustiges Mädel vom Land... etwas Besonderes") wurde am 12.04.2026 angelegt und später deaktiviert, ohne dass der Zeitstempel gesetzt wurde.
**Ursache:** Unklar — vermutlich einmaliger Vorfall. Kandidaten:
- Ein Agent-Pfad setzt nur `aktiv=FALSE` ohne `deaktiviert_am`
- Direkter SQL-Eingriff in einer früheren Session (wie bei FAK-LECK-Workaround)
- Eine Race-Condition zwischen zwei parallel laufenden CRUD-Operationen
**Lösungsansatz:**
- Einmalig korrigieren: `UPDATE charakter_identitaet SET deaktiviert_am = <plausibler Zeitpunkt> WHERE id = 4;`
- Prüfen ob andere Einträge (auch in anderen Tabellen mit bi-temporalem Modell) dieselbe Anomalie haben
- DB-Constraint einziehen: `CHECK (aktiv = TRUE OR deaktiviert_am IS NOT NULL)`
**Prio:** Niedrig — isolierter Vorfall, kein aktueller Schaden. Hinweis auf mögliche CRUD-Schwäche an einer Stelle.

---

#### ZIELE-PAIR-MISSING — Ziele-Tabelle ohne `character_id` ✅
**Kategorie:** CHA

**Zustand:** behoben — am Schema nachgesehen am 25.08.2026. `ziele` traegt die Spalte `character_id`.

**Entdeckt:** Chat 80, im Zuge der character_id-Inventur nach M2.5a-Phase-2

**Klasse:** Schema-Lücke + offene Skopierungs-Frage, Severity Niedrig — heute kein Live-Problem, aber Foundation-Bug

**Symptom:** `ziele` hat `user_id` mit Default `'nova'` und kein `character_id`. Wirkt wie pro-User-global. 9 Bestandseinträge, alle unter `user_id='nova'`.

**Offene Frage:** Sind Ziele charakter-spezifisch (Nova hat andere Ziele als Aria hätte)? Drive-Konzept (`thinking-drive_k.md`) suggeriert ja — explizite Festlegung fehlt.

**Lösung:** Im Migrations-Konzept zusammen mit den anderen Paar-Lücken klären.

**Ausführliche Beschreibung und Eingruppierung:** novaberg-backlog.md → Bug ZIELE-PAIR-MISSING (Chat 80).

---

### Umgezogen am 12.09.2026 — aus dem offenen Register

Am selben Tag behoben; die Kennung bleibt, weil Verweise darauf zeigen.

### `MODUS-KREATIV-WIRD-NIE-VERGEBEN` — der einzige hebende Modus ist im Perzeptionsmodell tot ✅ behoben am 12.09.2026
**Kategorie:** CHA

**Zustand:** ✅ **behoben am 12.09.2026.** Beide Perzeptions-Prompts tragen eine Wertelegende fuer `modus` — zehn Werte mit Auswahlkriterium statt einer Aufzaehlung —, und der Kanon-Zug loest seit demselben Tag Uebersetzungen auf (`MODUS_SYNONYM_MAP`).

`[gemessen 12.09.2026]` Ueber dieselben drei Kreativ-Reize wie die Nulllinie, je zehnmal, durch `perceive` und damit durch die Produktion:

| Arm | `kreativ` als Modus |
|---|---:|
| Betriebs-Prompt 10.09.2026 | 1 von 30 |
| Versuchsarm mit Legende 10.09.2026 | 11 von 30 |
| **Betrieb seit 12.09.2026** | **30 von 30** |

**Die Gegenfrage ist mitgemessen, und ohne sie waere die Zahl wertlos:** Eine Legende, die zu allem `kreativ` sagt, erreichte dieselben 100 %. Ueber das Spektrum aller zehn Modi (30 Reize, drei je Modus) trifft der Betrieb **23 von 30** — **genau die Nulllinie** des 10.09.2026 — und vergibt **0 mal** `kreativ` falsch. Die Legende hebt den Wert, ohne ihn auszuweiten.

> **Was den Unterschied zum Versuchsarm macht, ist unbelegt.** Die heutige Legende traegt einen Satz, den der Versuchsarm vermutlich nicht hatte: die Frage, die `kreativ` von `philosophischer_austausch` scheidet — *soll am Ende etwas Neues dastehen oder etwas Bestehendes verstanden sein?* Dass dieser Satz die 11 auf 30 hebt, ist plausibel und **nicht gemessen**; der Wortlaut des damaligen Arms liegt nicht vor.

**Und die zweite Haelfte der Abhilfe hat keinen Eingang:** Die Uebersetzungsstufe griff in **0 von 30** Laeufen — das Modell antwortete durchgehend deutsch. Sie ist gebaut, bezeugt und im Betrieb ohne Eingabe. Der Anlass (9 von 30 `creative` im Versuchsarm) ist mit der anderen Legende entfallen; als Riegel bleibt sie, als Notwendigkeit ist sie unbelegt.

**Die Absichtsfrage ist entschieden** (Eigentuemer, 12.09.2026): *„kreativ darf vergeben werden."*

**Nicht behoben ist die andere Haelfte des Befundes:** `sprach_stil` hat weiterhin keine Wertelegende. Gemessen ist nur `modus`; die Luecke bleibt in diesem Eintrag benannt.

~~**Zustand:** offen — gemessen am 10.09.2026 ueber eine entworfene Reihe und den Bestand.~~

**Befund.** `GV_LAENGE_MODUS_DELTA` traegt zehn Modi, und **einer** hebt die Vektorlaenge: `kreativ` mit **+0,3**. Drei ziehen mit −0,3 (`fachgespraech`, `lernmodus`, `philosophischer_austausch`), zwei mit −0,2, vier tragen nichts. **`kreativ` wurde noch nie vergeben.**

| Quelle | `kreativ` |
|---|---:|
| Bestand, gewachsen | 0 von 1293 |
| Spektrum-Reihe, entworfen | 0 von 54 |
| **zusammen** | **0 von 1347** |

**Die Reihe hat gezielt darauf gezielt.** Fuenf Reize waren als Kreativ-Auftraege gebaut — *„Erfinde mir ein Wort fuer den Moment, in dem ein Gedanke kippt"*, *„Stell dir vor, Gedaechtnis waere ein Fluss statt eines Archivs"*, *„Was waere, wenn Zeit rueckwaerts floesse"*. **Alle fuenf wurden `philosophischer_austausch`**, also der Modus mit **−0,3** statt dem mit +0,3.

> **Der naheliegende Verdacht ist ausgeschlossen, und zwar zweifach.** Die Option **steht im Prompt**: `perzeption.task.txt` und `perzeption.assistant_task.txt` fuehren `kreativ` an neunter von zehn Stellen, und `MODUS_KANON` kennt ihn. Und das Modell **kann** einen leichten Modus waehlen: In derselben Reihe vergab es `spielerisch` **sechsmal**. Es waehlt `kreativ` nicht.

**Warum das mehr ist als ein fehlender Wert.** Die Laengenrechnung startet bei 1,0 und braucht netto **+0,5** fuer eine 2. Faellt der einzige hebende Modus aus, kann die Modus-Dimension nur noch bremsen oder schweigen — **neun von zehn Werten wirken einseitig**. Was die Laenge dann noch hebt, sind Emotion, Dynamik und Stil; der Raum selbst kann es nicht mehr.

**Was der Befund nicht ist.** Er sagt nichts darueber, ob `kreativ` *haeufig* sein sollte. Er sagt, dass eine Dimension mit zehn Werten faktisch mit neun arbeitet, und dass der fehlende der einzige mit positivem Vorzeichen ist.

**Nicht Teil dieses Befundes:** `fachgespraech` erschien in der Reihe ebenfalls nicht, obwohl zwei Reize darauf zielten — im **Bestand** kommt er aber mit 148 von 1293 (11,4 %) vor. Er ist nicht tot, nur in dieser Reihe nicht getroffen.

**Belege:** `labor/messreihen/2026-09-10_spektrum_ergebnis.md`, `..._erwartung.md` (vor dem Lauf abgelegt), `labor/werkzeug/gv_laenge_zerlegen.py`.

**Die Ursache ist am 10.09.2026 gemessen: die fehlende Wertelegende.** Der Prompt erklaert `intent`, `arousal`, `emotion` und `beziehungs_dynamik` **Wert fuer Wert**; `modus` und `sprach_stil` bekommen je einen Satz und keine einzige Werterklaerung. Zwei Arme gegen dasselbe Modell, dieselben drei Kreativ-Reize je zehnmal:

| Arm | `kreativ` als Modus |
|---|---:|
| Prompt des Betriebs | **1 von 30** (3,3 %) |
| mit Wertelegende | **11 von 30** (36,7 %) |

**Faktor 11.** Die Gesamtqualitaet aendert die Legende dabei **nicht** — ueber 30 Reize aller zehn Modi trifft der Betriebs-Prompt in **23 von 30** Faellen (76,7 %), der ergaenzte in 24. Das Modell verteilt gut; der Ausfall betrifft gezielt diesen einen Wert.

> **Und die Legende allein genuegt nicht.** Der ergaenzte Arm vergab zusaetzlich **9-mal `creative`** — den englischen `intent`-Wert in der Modus-Spalte. Der Kanon-Zug faengt ihn nicht (`'creative' → None`, `'kreativ' → 'kreativ'`): Er zieht Schreibvarianten, keine Uebersetzungen. **Das Wort steht in drei Dimensionen** (`intent: creative`, `tone: kreativ`, `modus: kreativ`), und das Modell verteilt es auf die beiden, die eine Legende haben.

**Geschlossen, wenn** entweder `kreativ` im Betrieb vergeben wird — oder entschieden ist, dass er es nicht soll, und die Tabelle einen anderen hebenden Wert traegt. **Beides ist vertretbar; der heutige Zustand ist keins von beidem.** Die Legende ist gemessen und **nicht gebaut**: Sie hebt den Wert, erzeugt aber `creative` als neuen Ausreisser, und ob der Modus haeufiger vergeben werden *soll*, ist eine Absichtsfrage.

**Nachtrag 12.09.2026 — der Ausfall kostet mehr als Spielraum: er kostet den dritten Schritt, und zwar fuer die Haelfte des Bestandes.** Der Befund oben sagt, dass die Modus-Dimension ohne `kreativ` nur noch bremsen oder schweigen kann. **Gemessen ist jetzt die Folge daraus**: In `fachgespraech`, `lernmodus` und `philosophischer_austausch` (Zuschlag −0,3) ist Laenge 3 bei **jeder** Faktorstellung ausgeschlossen — die beste Summe ist exakt 2,5, und `round` rundet zur geraden Zahl (`GV-LAENGE-RUNDUNG-ZUR-GERADEN`). Dort liegen **794 von 1434 Rohturns**.

> ~~**`kreativ` ist damit nicht ein hebender Wert unter mehreren, sondern der einzige, der diese drei Modi ueberhaupt ueber die Kante bringt.**~~ → **Am 12.09.2026 ist die Kante gefallen** (`GV-LAENGE-RUNDUNG-ZUR-GERADEN`, behoben): Die drei fachlichen Modi erreichen die 3 jetzt auch ohne `kreativ`, bei bester Stellung. **Der Befund dieses Eintrags bleibt unveraendert** — eine Dimension mit zehn Werten arbeitet faktisch mit neun, und der fehlende ist der einzige mit positivem Vorzeichen. **Was wegfaellt, ist nur seine Dringlichkeit aus dem fremden Grund:** Er war kurzzeitig der einzige Weg zum dritten Schritt in der Haelfte des Bestandes; das ist er nicht mehr.
>
> **Und die Absichtsfrage dieses Eintrags ist entschieden** (Eigentuemer, 12.09.2026): **`kreativ` darf vergeben werden.** Damit ist der zweite Ausgang des Abschnitts *Geschlossen, wenn* hinfaellig — die Tabelle bekommt keinen anderen hebenden Wert, sondern der Modus wird vergeben. Zu bauen ist die Wertelegende (gemessen 3,3 % → 36,7 %) **samt** dem Zug fuer das englische `creative`, das derselbe Lauf in 9 von 30 Faellen erzeugte und der Kanon-Zug nicht faengt.

`[gemessen]` Ueber eine 20-Turn-Reihe in genau diesen beiden Modi: In **8 von 20** Turns haette allein `modus = kreativ` die 3 erzeugt; `arousal = 1.0`, `dynamik = vertrauen` und `stil = locker` erzeugten sie in **keinem einzigen**. Die Reihe erreichte 3 nie.

**Was das fuer die Behebung heisst:** Die beiden Kennungen sind **zusammen** zu lesen und **getrennt** behebbar — wer nur die Legende baut, hebt die drei fachlichen Modi trotzdem nicht (2,5 bleibt 2); wer nur die Rundung behebt, gibt ihnen die 3 auch ohne `kreativ`. Welche der beiden zuerst, ist eine Absichtsfrage und keine Ableitung.

---
