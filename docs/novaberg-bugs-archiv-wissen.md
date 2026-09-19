# Novaberg — Bugs, Archiv: Wissen — Bibliothek, Dateien, Notizen, Timeline, Fakten

**Inhalt:** die abgeschlossenen Defekte dieses Gegenstands, 24 Eintraege, je mit `WIS` als Kategorie.
**Wegweiser:** [`novaberg-bugs-archiv.md`](novaberg-bugs-archiv.md) — Kopf, Formregel und die Kurzeintraege der alten Tabelle. **Findemittel ueber alle Bugs:** [`novaberg-bugs-index.md`](novaberg-bugs-index.md). **Offenes Register:** [`novaberg-bugs.md`](novaberg-bugs.md).

**Die Abschnittsueberschriften stammen aus dem ungeteilten Archiv** (geteilt am 19.09.2026) und sagen, *wann und wobei* ein Eintrag entstanden ist — nicht, welchen Gegenstand er hat. Den sagt die Datei, in der er steht.

---

## 19.08.2026, nachts — die Themenzeilen fehlten auf dem Verstärkungsweg

### `THEMENZEILEN-NUR-IM-INSERT-ZWEIG` — die Themenzeilen fehlten auf dem Verstärkungsweg

**Zustand:** ✅ behoben am 19.08.2026 · **Kategorie:** WIS · aus dem offenen Register übernommen am 19.09.2026, weil der Eintrag dort ohne Überschrift und schon geschlossen stand

**`THEMENZEILEN-NUR-IM-INSERT-ZWEIG`** — gefunden und im selben Zug behoben.

**Befund.** `AutonomousWissenRepository.speichern` hat zwei Zweige: Ein neuer Dateipfad wird angelegt, ein vorhandener **verstärkt** (`haeufigkeit` steigt, Gewichte wachsen). Die Themenzeilen nach Konvention 4 entstanden nur im Anlege-Zweig. Ein Eintrag mit dem Themenfeld `Alpha, Beta`, der später mit `Alpha, Gamma` verstärkt wird, behielt `Beta`.

**Warum das mehr ist als ein fehlendes Update:** Die Bibliothek hätte eine Ausarbeitung über ein Thema gefunden, das sie **nicht mehr behandelt** — ein Treffer, der auf einen Text zeigt, in dem das Gesuchte nicht steht. Das ist die Sorte Fehler, die als richtige Antwort aussieht.

**Reproduktionsweg.** Zweimal `speichern()` auf denselben `dateipfad`, beim zweiten Mal ein anderes Themenfeld; danach `SELECT thema FROM autonomous_wissen_thema WHERE wissen_id = …`.

**Wie er gefunden wurde — die Kette ist der eigentliche Eintrag.** Die Gegenprobe hebelte `themen_zerlegen` aus und sagte 12 rote Tests voraus; **gezählt wurden 9**. Die drei fehlenden waren die Live-Zusicherungen der Schema-Datei: Sie legen ihre Themenzeilen per direktem `INSERT` an und umgehen den Schreibpfad — **kein Zeuge prüfte, dass `speichern()` sie erzeugt**. Der daraufhin gebaute Zeuge fand den Defekt sofort.

> Weder die Suite (1985 grün) noch die Selbstprüfung des Bauenden hatten ihn. Die Abweichung *zwischen vorhergesagter und gezählter Zahl* hat ihn geliefert — nicht die Zahl selbst.

**Geschlossen, wenn** — bereits erfüllt: Beide Zweige ziehen die Themenzeilen nach, zwei Zeugen decken Anlegen und Verstärken ab, Suite `Ran 1987 tests — OK`.

---


## 25.08.2026 — eine Dauer in der Einzahl war ein Monatsname

#### ZEIT-EINZAHL-GREIFT-DANEBEN ✅ behoben
**Kategorie:** WIS

**Zustand:** **behoben am 25.08.2026.** Suite 2288 gruen / 0 uebersprungen, sieben neue Zeugen in `tests/test_zeit_dauer_einzahl.py`. Gegen Referenz 30.07.2026 nachgemessen: `in einem Tag` = `in 1 Tag` = **31.07.2026**, `in zwei Tagen` = 01.08.2026, `in einem Monat` = **30.08.2026** (vorwaerts). Alle dreizehn Faelle der Reihe rechnen richtig.

**Die Ursache war weder die Einzahl noch `dateparser`, sondern die eigene Fuzzy-Korrektur.** Sie zog `Tag` auf `Mai` und `Monat` auf `Montag` — beide auf Levenshtein-Distanz 2 und damit innerhalb von `max_distanz`. Danach parste `in einem Tag` als *im Mai* und `in einem Monat` als *am Montag*; die Ergebnisse 01.05.2027 und 01.07.2026 sind genau das, kein Rechenfehler.

**Die Mehrzahlformen waren nie betroffen, und daran lag die Fehldiagnose:** `Tagen` und `Monaten` sind lang genug, dass keine Korrektur greift. Der Defekt sah deshalb aus wie ein Einzahl-Problem und war eines der **Wortlaenge** — er traf jede Zahl, `in 2 Tag` ergab 2027-05-02. Die Vermutung des Befundes (*„vermutlich die Normalisierung der Einzahlform"*) traf die Wirkung und verfehlte die Ursache: Die Normalisierung reicht Dauern unveraendert durch, gemessen.

**Behoben** ueber `_ZEITEINHEITEN` in `_GESCHUETZTE_WOERTER` (`utils/zeitparser.py:182`) — der Mechanismus, den die Stufe fuer genau diesen Fall schon hatte. Geschuetzt sind alle sieben Einheiten in beiden Formen, auch die heute unauffaelligen.

**Was dabei offen bleibt und groesser ist als dieser Eintrag:** Ueber 57 gebraeuchliche Woerter gemessen werden **13** auf einen Monats- oder Wochentagsnamen gezogen. `Mittag` loest auf den **naechsten Montag** auf statt auf 12:00 desselben Tages, waehrend `mittags` korrekt rechnet; `morgen Mittag`, `heute Mittag` und `Freitag Mittag` parsen gar nicht. Steht in der Fundliste, nicht behoben — ein Fund wird nicht im Vorbeigehen repariert.

**Befund (2026-07-31).** **`in einem Tag` und `in 1 Tag` lösen auf den 01.05.2027 auf.** Die Mehrzahlform `in zwei Tagen` funktioniert. Gemessen gegen Referenz 30.07.2026. Ein Ausdruck, der um Monate danebengreift, ist schlimmer als einer, der gar nicht parst — er legt einen Anker an, und zwar einen plausibel aussehenden. Betrifft `utils/zeitparser.py`, vermutlich die Normalisierung der Einzahlform.

**Was fertig waere.** ~~`in einem Tag` loest auf denselben Tag auf wie `in 1 Tag` und `in zwei Tagen`.~~ **Erfuellt am 25.08.2026**, nachgemessen gegen die Referenz des Befundes.

**Prioritaet:** hoch.

---

## 25.08.2026 — der Versionsstempel frass die Leerzeile unter sich

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `VERSIONSSTEMPEL-FRISST-LEERZEILE` — jeder Eingriff des Rueckwegs nahm dem Kopf eine Zeile
**Kategorie:** WIS

**Zustand:** behoben am 25.08.2026 — `agents/wissen_rueckweg/einarbeitung.py:36` traegt ein waagerecht begrenztes Suchmuster, zwei Zeugen bewachen es, 136 Dateien im Bestand sind nachgezogen.

**Befund (25.08.2026), beim Sichten der autonomen Laeufe.** **Ein Suchmuster mit `\s*$` im Mehrzeilen-Modus verschluckt den Zeilenumbruch, den es zu begrenzen scheint.** `_VERSION_ZEILE` lautete `r"^\*\*Version:\*\*\s*(?P<wert>\S+)\s*$"` mit `re.M`. In Python schliesst `\s` den Umbruch ein, und `$` steht im Mehrzeilen-Modus auch vor einer leeren Zeile — der Treffer lautete damit `**Version:** 1.0\n` statt `**Version:** 1.0`. Die Ersetzung `f"**Version:** {neu}"` schreibt keinen Umbruch zurueck, also verlor der Kopf bei **jedem** Versionsstempel seine Leerzeile zur Trennlinie darunter.

**Gemessen ueber den Bestand (25.08.2026, 524 Wissensdateien unter `knowledge/autonomous/`):** Die Korrelation ist vollstaendig — **163 Dateien mit Version 1.0 trugen die Leerzeile, alle 136 mit Version > 1.0 trugen sie nicht.** 225 weitere fuehren kein Versionsfeld und sind unberuehrt. Alle 136 liegen im Verzeichnis **einer einzigen Figur** — der einzigen, deren Wissensdateien ueberhaupt Rueckweg-Einarbeitungen erhalten; die uebrigen 16 Figurenverzeichnisse tragen keinen Fall.

**Der Schaden bleibt beim zweiten Eingriff stehen.** Nach dem ersten Stempel steht keine Leerzeile mehr da, die `\s*` fressen koennte — deshalb fehlt genau eine, nicht eine je Version. Eine Datei bei Version 1.4 sieht aus wie eine bei 1.1.

**Warum es zwei Wochen lief:** `version_fortschreiben` hatte keinen eigenen Zeugen. In `tests/test_wissen_rueckweg.py` kam die Funktion nur als `patch.object(...)` vor — gemockt, nie gefahren. Ihr Rueckgabewert war in beiden Faellen `"1.1"`; der Unterschied stand allein in der Datei darunter, und die sah kein Test an.

**Geschlossen, wenn** ~~Der Versionsstempel fasst die Versionszeile an und sonst nichts, und der Bestand traegt die Zielform.~~ **Erfuellt am 25.08.2026**: Suchmuster auf `[^\S\n]*` umgestellt, `VersionsstempelTest` mit zwei Zeugen (Zielform, Zeichengleichheit des Rests), Suite 2281 gruen / 0 uebersprungen, Bestand 299 in Zielform / 0 abweichend.

---

## 20.08.2026 — aus der Klassifikation der Fundliste

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### `VERSCHWUNDEN-DURCH-FILTERWECHSEL` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `ecb2517` gehalten am 23.08.2026. Der Waechter fragt nicht mehr seine Buchfuehrung, sondern die Platte: `_liegt_noch_da()` in `agents/dateien_index/wandern.py` entscheidet je unbewerteter Bestandszeile, ob sie nach `verschwunden` oder nach `ausserhalb` geht.

**Der Befund war enger als der Defekt.** Er nannte den nicht betretenen Punkt-Ast; gemessen am 23.08.2026 an einem Lauf mit vorbereitetem Bestand (`labor/2026-08-23_waechter_verschwunden_klassen.py`) traf es **fuenf Klassen vorhandener Dateien** — Punkt-Ast, fremde Endung, ueber der Groessengrenze, leer, verborgene Einzeldatei. **Sechs Zeilen als verschwunden gemeldet, fuenf davon lagen da.**

**Der Umbau in Zahlen.** DDL: `verschwunden_am` → `grund_am` umbenannt, `grund TEXT CHECK (grund IN ('created','changed','deleted','excluded'))` hinzugefuegt; die 174 Bestandszeilen ohne Nachfuellen. Zeugen 32 → **43**; Gegenprobe **6 vorhergesagt, 6 gezaehlt**. Suite `Ran 2132 tests — OK, 0 uebersprungen`. Im Betrieb belegt: ein Lauf ueber `/docs` schrieb **29 `changed` und 1 `created`**, und eine Sonde gegen dieselbe Datenbank (`labor/2026-08-23_waechter_ausgang_db.py`) legte eine vorhandene Datei als `excluded` und eine fehlende als `deleted` still. Der Bestand vor dem Umbau ist mit `labor/2026-08-23_waechter_bestand_trocken.py` lesbar — der Waechter ueber die echten Wurzeln, ohne zu schreiben.

**Warum die Spalte und nicht ein NULL.** `verschwunden_am IS NULL` bei `aktiv = FALSE` haette die Unterscheidung auch getragen — aber nur die Tatsache, nicht den Grund, und der Wiedereintritt braucht ihn (siehe `DATEIINDEX-NEUANLAGE-ERBT-VORGAENGER`). `aktiv` bleibt daneben stehen: Es sagt, **ob** die Zeile gesucht wird, `grund` sagt **warum** sie ist, wie sie ist; fuenf Lesestellen filtern auf `aktiv` und keine davon will den Grund wissen.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. `speicher.py:138` setzt `verschwunden_am` weiter allein daraus, was der Lauf gesehen hat.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Eine Filteränderung erzeugt Zeilen, die als „verschwunden" markiert sind, obwohl die Datei dort liegt, wo sie lag.** Der Wächter leitet `verschwunden` daraus ab, was der Lauf **gesehen** hat: Was im Bestand steht und diesmal nicht gefunden wurde, wird stillgelegt (`aktiv = false`, `verschwunden_am`). Wird ein Filter enger — am 20.08.2026 der nicht mehr betretene Punkt-Ast —, trifft das auch Dateien, die unverändert vorhanden sind. **Gemessen** an einem Lauf mit vorbereitetem Bestand: Die Zeile zu `.obsidian/notiz.md` landet unter `verschwunden`, die Datei existiert. **Folgenlos in dieser Installation** (0 betroffene Zeilen, die sechs Dateien dort waren nie indiziert), aber die Bedeutung des Feldes ist damit zweideutig: *„die Datei ist fort"* und *„wir sehen nicht mehr hin"*. §5.5 begründet das Stillegen damit, dass die Frage *„wo war das noch"* eine sinnvolle Antwort bekommt — die lautet dann *„sie ist weg"* und ist falsch. Ein Zeuge hält das Verhalten fest; die Unterscheidung fehlt.

**Geschlossen, wenn** Der Waechter unterscheidet *die Datei ist fort* von *wir sehen nicht mehr hin*; eine Filteraenderung erzeugt keinen `verschwunden_am`.

</details>

---

### `DATEIINDEX-NEUANLAGE-ERBT-VORGAENGER` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gefunden und behoben am 23.08.2026, im selben Zug wie `VERSCHWUNDEN-DURCH-FILTERWECHSEL`. Der Eintrag steht, weil er erklaert, warum der UPSERT drei `CASE`-Zweige traegt.

**Befund (23.08.2026).** **Eine Neuanlage unter altem Pfad erbte drei Spalten ihres Vorgaengers.** `agent.py:255` rechnete `zu_tun = lauf.neu + lauf.geaendert` und verwarf damit das Etikett, das `wandern()` gerade vergeben hatte; beide Faelle nahmen denselben UPSERT. Dessen `DO UPDATE SET` frischte vierzehn Spalten auf und liess **`entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash`** stehen — die Graph-Verknuepfungen, den Zeitbezug und den Lernstand der geloeschten Datei. Erschwerend kam hinzu, dass eine stillgelegte Zeile mit vorhandener Datei ueberhaupt als *geaendert* galt: Der Fall *Grabstein mit anderem Hash* war nicht vorgesehen.

**Folgenlos zum Zeitpunkt des Befundes, und messbar so:** Ein `grep` ueber `agents/dateien_index/` und `agents/dateien/` fand fuer alle drei Spalten **keinen Schreiber** — dieselbe Beobachtung, die als `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` im Register steht. **Der erste Schreiber haette die Luecke scharf gemacht, und sie waere still gewesen:** Niemand sucht nach Beziehungen, die eine Datei zu Unrecht traegt.

**Die Behebung.** `_fall_bestimmen()` in `wandern.py` entscheidet den Wiedereintritt: `deleted` mit abweichendem Hash ist eine **Neuanlage**, gleicher Hash oder `excluded` sind Fortsetzung. `zeile_schreiben` raeumt die drei Spalten bei `created` und laesst sie bei `changed` stehen. Vier Zeugen halten die Faelle einzeln fest (`KetteTest`), darunter der Fall `grund IS NULL` — die 174 Bestandszeilen von vor der Spalte werden nicht zu Neuanlagen.

**Geschlossen, wenn** — erfuellt: Eine Zeile, die als `created` geschrieben wird, traegt in `entitaet_ids`, `timeline_id` und `zuletzt_gelernt_hash` nichts aus ihrem Vorleben. Im Betrieb geprueft: **0 Zeilen mit `grund = 'created'` und einem dieser drei Werte.**

---

### `ARCHIVDATEI-OHNE-ETIKETT` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben. Die Fundstelle traegt das Etikett `(archiviert)`, und zwar in **allen drei** Ausgabewegen — Enricher, lesender Dienst und Bibliothek. Die Regel steht an einer Stelle (`utils/etikett.py`), nicht in den beiden Bauern der Herkunftsangabe.

**Warum eine gemeinsame Stelle und nicht zwei Zeilen.** `agents/dateien_index/aufzeichnungen.py` (Enricher) und `agents/dateien/auskunft.py` (lesender Dienst) bauen dieselbe Angabe getrennt. Eine Regel, die an zwei Stellen getippt wird, laeuft auseinander, ohne dass etwas rot wird — und die Haelfte, die das Etikett verloere, ist genau die, die Widerrufenes als geltend ausgibt. Ein Zeuge haelt beide Wege einzeln fest.

**Geprueft wird das Verzeichnisglied**, nicht der Anfang (`startswith` fande `konzepte/archive/alt.md` nicht) und nicht der Teilstring (`"archive" in pfad` traefe `archivelogik_k.md`). Der Dateiname zaehlt nicht als Glied: `archive.md` ist ein Dokument ueber Archive.

**Gemessen im Betrieb** (`labor/2026-08-23_archivetikett_betrieb.py`), beide Wege aus `dateien_index` ueber alle 175 Indexzeilen: **6 etikettiert, 0 faelschlich, 0 Abweichungen.** Zeugen 15, Gegenprobe **6 vorhergesagt, 5 gezaehlt** — die Differenz ist ein Zaehlfehler der Vorhersage, nicht ein blinder Zeuge: In `ErkennungTest` pruefen zwei Zeugen den archivierten Fall, die uebrigen sind Gegenproben.

**Zwei Nachbesserungen aus einer Pruefung, die ein Kriterium anlegte statt die bekannten Stellen abzugehen.** Der Bau kannte zwei Ausgabewege; der Baum hat **drei** — `agents/wissen/auskunft.py` nennt dasselbe Wort *Fundstelle* vor demselben Publikum, liest aber aus `autonomous_wissen`. Heute ohne Wirkung (0 von 820 Zeilen unter einem Archivverzeichnis) und deshalb beim Pruefen entlang der Ausgabe unsichtbar. Verdrahtet. Zweitens fiel `Archiv/` durch: Die Erkennung pruefte auf die exakte englische Kleinschreibung — richtig fuer `/docs`, falsch fuer die Dateibaeume von Mensch und Figur. Seither wird kleingeschrieben verglichen, und `archiv` gilt neben `archive`; `archives` und `Archivierung` bleiben draussen.

**Der verschaerfende Teil lag ausserhalb des Codes und ist mitbehoben.** Drei der sechs Archivdateien nannten in ihrer Kopfzeile `Pfad:` weiterhin den Ort **vor** dem Verschieben — `novaberg-iteration-control_k.md`, `novaberg-mem-lzg.md`, `novaberg-pixie-decay.md`. Berichtigt. Eine vierte traegt gar keine `Pfad:`-Zeile; das ist keine falsche Angabe und bleibt.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. kein Etikett im Indexweg — `archive` kommt in `agents/dateien_index/` nicht vor.

**Befund (20.08.2026), aus der Fundliste uebernommen.** **Ein archiviertes Konzept sieht im Dateienindex aus wie ein geltendes.** Mit der Freigabe von `/docs` liegen 6 Dateien aus `docs/archive/` im selben Bestand wie die 154 geltenden. Getrennt sind sie allein durch den Pfadanteil `archive/`; die Indexzeile trägt kein Etikett, und der Enricher-Weg legt den Fundstellentext neben die geltende Doku, ohne den Unterschied zu benennen. **Verschärfend:** Nicht jede Archivdatei ist an ihrem Kopf erkennbar — `archive/novaberg-mem-lzg.md` nennt im Feld `Pfad:` weiterhin `novaberg/docs/novaberg-mem-lzg.md`, also den Ort vor dem Verschieben. Wer nur die Kopfzeilen liest, hält sie für aktuell.

**Geschlossen, wenn** Eine Indexzeile aus `docs/archive/` traegt ein Etikett, und der Fundstellentext nennt es.

</details>

---

### `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben — durch die **Statusmarke**, nicht durch einen Schreiber. Die Geschlossen-wenn-Zeile laesst beides zu, und die Messung entschied gegen den Schreiber.

**Warum kein Schreiber.** Der naheliegende Bau war, die je Datei erhobenen Stichwoerter gegen den Entitaetenbestand aufzuloesen. **Vor dem Bau gemessen** (`labor/2026-08-23_dateiindex_graphkanal.sql`, 175 Indexzeilen gegen die **690** Entitaeten, die der Aufloeser fuer dieses Paar sieht): Von **843** verschiedenen Stichwoertern treffen **10** eine bestehende Entitaet. 122 Dateien bekaemen eine Kante — **116 davon zu `Novaberg`, also 95,1 %.** Ohne sie bleiben **18 von 175**.

**Nicht die Zahl der Kanten entscheidet, sondern ihre Verteilung.** Eine Kante an zwei Dritteln des Bestands sortiert nicht; fuer eine Datei unter `/docs` ist *handelt von Novaberg* keine Auskunft. Der Rest ist ein langer Schwanz mit Pixie an 7 und Planner an 5 Dateien.

> **Zwei Berichtigungen an diesen Zahlen, aus einer Nachpruefung quer zum Bau.** Die erste Messung jointe **ohne `user_id`-Filter** und zaehlte drei Entitaeten fremder Kennungen mit; der reale Aufloeser filtert (`EntitaetenRepository.find_by_name`). Veroeffentlicht waren 13 / 124 / 21, berichtigt sind es **10 / 122 / 18**. Und der exakte Vergleich ist nur **eine von drei Stufen** des Aufloesers: Auf einer Wortgrenzen-Stufe steigen die Kanten ohne `Novaberg` auf 37, **der Novaberg-Anteil bleibt bei 91,4 %** — die Lockerung aendert die Ausbeute, nicht den Befund.
>
> **Ein zweiter Grund ist ersatzlos entfallen.** Die erste Fassung fuehrte an, die Aufloesung *lege an*, was sie nicht finde. Das ist eine Aussage ueber einen **Aufrufer**: `resolve_batch` schreibt nichts, angelegt wird in drei Zeilen des KZG-Pfads (`agents/kzg/magnete.py`). Ein Dateiweg laesst sie weg. Der Befund traegt allein ueber die Verteilung.

**`timeline_id` scheitert am Gegenstand**, nicht an der Ausbeute: Eine Datei hat keinen Ereigniszeitpunkt. Der Vorrang des Neueren steckt bereits in `geaendert_am`, und der Waechter haelt es aktuell.

**Wo die Marke steht:** `init.sql` an beiden Spalten mit der Messung, `novaberg-agent-dateien_k.md` §6.1a und die Spaltentabelle in §4 (⬜), Featureliste. **Der echte Graph-Kanal** — Entitaeten aus dem Dateiinhalt statt aus Stichwoertern, aufgeloest **ohne Anlegen** — steht als eigener Backlog-Eintrag.

<details><summary>Der Befund, wie er bis zum 23.08.2026 stand</summary>

**Zustand:** offen — gegen HEAD `00c16b6` gehalten am 20.08.2026. weder Schreiber noch Statusmarke gefunden.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **`dateien_index.entitaet_ids` und `.timeline_id` sind in 0 von 14 Zeilen belegt und haben keinen Schreiber.** Das Konzept beschreibt sie als *„der Graph-Kanal"* und als *„Eingang der Regel ‚das Neuere sticht'"* (`novaberg-agent-dateien_k.md`), im Produktivcode schreibt sie für **diese** Tabelle niemand. **Die naheliegende Zählung führt in die Irre:** Ein `grep` über den Baum findet 29 bzw. 27 Schreibstellen — sie betreffen alle andere Tabellen, in denen die Spalten gleich heißen. **Der Unterschied zu `zuletzt_gelernt_hash`:** Dessen fehlender Schreiber ist als ⚫ in der Featureliste und ⬜ im Konzept ausdrücklich vermerkt; für diese beiden fand sich keine Statusmarke, nur die Beschreibung dessen, was sie leisten sollen.

**Geschlossen, wenn** `entitaet_ids` und `timeline_id` haben entweder einen Schreiber oder eine Statusmarke, die sagt, dass sie keinen haben.

</details>

---

### `BIBLIOTHEK-FILTERT-ZWEISPALTIG` — behoben am 23.08.2026
**Kategorie:** WIS

**Zustand:** behoben. Jede Abfrage auf `autonomous_wissen`, die auf das Paar filtert, filtert dreispaltig. `Bibliotheksfrage` traegt `beobachter` als Pflichtfeld ohne Default, geprueft gegen den neuen `BEOBACHTER_KANON` (`config.py`); die Lesestellen nehmen `BIBLIOTHEK_BEOBACHTER` aus dem Repository statt eines Literals. Zeugen: `tests/test_bibliothek_partition.py` (5), Gegenprobe 1 vorhergesagt / 1 gezaehlt, Suite `Ran 2180 tests — OK`.

> **Der Befund nannte zwei Lesepfade, das Kriterium fand vier.** *Wer fragt `autonomous_wissen` mit `user_id = %s`?* — `AutonomousWissenRepository.suchen`, `AutonomousWissenRepository.zaehlen`, der Vorcheck im Enricher (`graph/nodes/enricher.py`) und die Kandidatenauswahl des Rueckwegs (`agents/wissen_rueckweg/zuordnung.py`). Die letzten beiden waeren bei einer Pruefung entlang der Aufzaehlung nie aufgefallen. Der Zeuge ist deshalb dasselbe Kriterium und keine Liste der vier.

> **Die Zeilenangabe des Befundes war veraltet** — die Datei liegt heute unter `memory/repositories/`, der Filter stand in `suchen` bei :541, nicht bei :65. Und die Bestandszahl ist gewachsen: **831 Zeilen** statt 274 — die 274 waren der Stand vom 19.08.2026 —, weiterhin **alle** mit `beobachter='assistant'`; der Filterwechsel entfernt heute 0 Zeilen. Messwerkzeug: `labor/2026-08-23_bibliothek_partition.sql`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Lesepfad der Bibliothek filtert das Paar zweispaltig, das Schema ist dreispaltig.** `AutonomousWissenRepository.suchen` und die Enricher-Quelle filtern auf `user_id` und `character_id`; `beobachter` steht in der Tabelle und wird beim Lesen **nicht** eingeschränkt. Heute ist das folgenlos und nachgezählt: **274 von 274** aktiven Wissenszeilen tragen `beobachter='assistant'`, weil allein die Hintergrund-Agenten schreiben. **Es fällt in dem Moment auf die Füße, in dem ein zweiter Schreiber dazukommt** — und der Ausfall wäre still: Fremde Zeilen erschienen als eigene Ausarbeitung, ohne dass irgendetwas anschlägt. Die Konvention führt für das Langzeitgedächtnis ausdrücklich drei Spalten.

**Geschlossen, wenn** Der Lesepfad filtert nach dem Paar-Schema, also dreispaltig.

---

### `BIBLIOTHEKSSCHWELLE-SORTIERT-FALSCH` — 0,40 sortiert gegen echte Fragen falsch herum
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. 19.08.2026 an 40 Fragen mit bekannter richtiger Antwort gegen 249 Ausarbeitungen kalibriert; `WISSEN_RETRIEVAL_SCHWELLE` steht auf 0.50, die Reihe steht in `server/config.py:478-499`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Die Bibliotheksschwelle 0,40 sortiert gegen echte Fragen genau falsch herum.** Acht Fragen als rohes Embedding gegen die 242 Ausarbeitungen des Paares `meister/nova`. Der sachlich **richtige** Treffer — Frage nach Sternentwicklung und Kernfusion, Datei mit dem wortgleichen Thema *„Sternentwicklung, astrophysikalische Prozesse, Kernfusion, Hydrostatische Balance"* — liegt bei **0,3054** und wird abgewiesen. Ein Fall **ohne** einschlägigen Treffer — Frage nach Resonanz als physikalischer Größe, bester Treffer *„Ehrlichkeit gegenüber der Informationslage"* — liegt bei **0,4700** und kommt durch. Die vollständige Reihe: 0,3054 · 0,4617 · 0,4700 · 0,3519 · 0,3147 · 0,3786 · 0,3402 · 0,2977. **Das ist nicht derselbe Befund wie der vom 17.08.**, sondern seine Kehrseite: Dort wurden **Korpuspaare** gemessen (35,6 % über 0,40, die Schwelle zu lasch), hier **Frage gegen Korpus** — und da ist dieselbe Zahl zu streng. Wer eine Schwelle an Paaren des Bestandes kalibriert, kalibriert sie für die falsche Richtung. Gehört zu `WIS-SCHWELLE-MESSEN`.

**Geschlossen, wenn** Die Schwelle ist an echten Fragen kalibriert statt uebernommen; belegt durch eine Messung mit bekannter richtiger Antwort.

---

### `VERWEISWEG-LEHNT-BESTEN-FALL-AB` — die falsche Frage am falschen Weg
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `00c16b6` gehalten am 20.08.2026. der Verweis-Weg hat eine eigene Frage — `prompts/default/verweis_zuordnung.task.txt` (*STEHT DER FUND DORT SCHON, IST DAS DIE BESTAETIGUNG*), gewaehlt in `agents/wissen_rueckweg/zuordnung.py:178`.

**Befund (19.08.2026), aus der Fundliste uebernommen.** **Der Verweis-Weg stellt die Frage des Einarbeitungs-Wegs und lehnt damit genau seinen besten Fall ab.** `prompts/default/rueckweg_zuordnung.task.txt` nennt als dritten Grund fuer `null`: *„Er steht dort erkennbar schon — eine Wiederholung ist kein Zuwachs"*. Fuer `wissen_rueckweg` (Schnitt) ist das richtig; fuer `wissen_verweis` (Verstaerkung) ist es **umgekehrt** — dass der Fund in der Datei schon steht, ist der staerkste Grund, ihre Zeile zu heben, und genau das beschreibt §4b.2. `[gemessen]` — 19.08.2026, 08:21 UTC, fuenfter echter Lauf: bester Kosinus **0,9226**, und das Modell lehnte ab mit *„exakte textliche Wiederholung der bereits in Datei [8974] enthaltenen Informationen … kein Wissenszuwachs"*. **Der gebaute Zweig kann seine eigene Wirkung so nicht erreichen:** Je besser die Zuordnung, desto sicherer die Ablehnung. Die Zuordnung muss die Auftragsart kennen.

**Geschlossen, wenn** Der Verweis-Weg stellt seine eigene Frage statt der des Einarbeitungs-Wegs.

---

## 20.08.2026 — die Blockkarte war halbiert und meldete es als gültiges Ergebnis

### `BLOCKKARTE-STILL-HALBIERT` — behoben am 20.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Zaunbilanz steht vor dem Parser (`server/tools/dateien/operationen.py:177`), und der Lauf ueber den echten Bestand liegt vor: 174 Dateien, **173 erhoben, 0 leer, 1 nicht erhoben** am 20.08.2026.

**Befund.** `struktur_analysieren` überspringt Überschriften innerhalb von Codeblöcken und
führt dafür einen Umschalter: Jede Zeile, auf die `^\s*(```|~~~)` passt, kippt ihn. Fällt ein
öffnender Zaun aus der Erkennung, kippt der Schalter einmal zu viel und **nie zurück** — ab
dieser Stelle gilt der Rest der Datei als Code. Genau das tut ein durchgestrichener
Codeblock: Die öffnende Zeile beginnt mit den beiden Tilden und passt nicht, die schließende
beginnt mit dem Zaun und passt.

**Reproduktion.** `novaberg-agent-dateien_k.md`, Zeile 72 und 78. Der Erkenner zählt **17**
Zäune — eine ungerade Zahl —, der letzte in Zeile 976 von 1236. Von **83** Überschriften der
Datei stehen **5** in der Karte, die letzte aus Zeile 68.

**Warum es zwei Tage unentdeckt blieb.** Das Ergebnis war keine Ausnahme, sondern eine
kürzere Liste, und eine kürzere Liste sieht aus wie eine kürzere Datei. Verstärkt wurde das
durch eine Zusicherung, die zwei Aussagen auf denselben Rückgabewert legte: *„nachgesehen,
die Datei hat keine Überschriften"* und *„ich konnte nicht nachsehen"* waren beide die leere
Liste — mit einem Docstring, der das ausdrücklich zum gültigen Ergebnis erklärte. Der
Aufrufer im Index schrieb daraufhin die Zeile *„keine Überschriften — die Datei ist ein
durchgehender Text"* in den Prompt: eine positive Aussage über eine Datei, die niemand
gelesen hatte.

**Abhilfe, zwei Hälften.** Der Erkenner rechnet die Zaunbilanz gegen und wirft
`StrukturDefektError`, wenn sie am Dateiende ungerade ist — das ist ohne Kenntnis des Inhalts
prüfbar. Und die Erkennerwahl hängt an einer Registry nach Dateiendung; fehlt ein Erkenner,
wirft `FormatOhneErkennerError`. Beide erben von `StrukturUnklarError`, und der Index bildet
sie auf `struktur = None` ab, gespeichert als SQL-NULL.

**Geschlossen, wenn** ein Lauf über den echten Bestand die drei Ausgänge getrennt ausweist.
Gemessen am 20.08.2026 über 174 Dateien: **173 erhoben, 0 leer, 1 nicht erhoben** — die eine
ist die Datei oben. Zeugen 4 neu, Gegenprobe zweimal je 1 vorhergesagt und 1 gezählt, Suite
**2004 grün**.

**Was der Defekt nicht ist.** Die Auszeichnung der Datei selbst bleibt gültiges Markdown; ein
durchgestrichener Codeblock ist eine erlaubte Schreibweise. Der Defekt sitzt im Erkenner,
nicht im Dokument.

---

## 20.08.2026 — vier Dateien fielen aus dem Indexlauf, und die Bilanz meldete keinen Fehler

### `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER` — behoben am 20.08.2026
**Kategorie:** WIS

**Zustand:** behoben — gegen HEAD `62560cf` gehalten am 21.08.2026. Die Bilanz traegt `gescheitert_gruende` je Wurzel mit Pfad und Grund (`server/agents/dateien_index/agent.py:340`), getrennt von `fehler`.

**Befund.** Der Erstlauf des Wächters über die neu freigegebene Wurzel `/docs` meldete `neu 160`, `indiziert 46`, `offen 110`, `fehler: []` und `status: abgeschlossen`. **Die drei Zahlen gehen nicht auf:** 46 + 110 = 156, nicht 160. Die fehlenden vier stehen ausschließlich im Log, als `Indizieren: Modellantwort fuer '…' unbrauchbar (JSONDecodeError)` — `novaberg-agent-dateien_k.md`, `novaberg-agent-notes.md`, `novaberg-ei-character-profiles_l.md`, `novaberg-gv-initiative_k.md`.

**Warum die Antworten unbrauchbar waren, steht als eigene Kennung daneben** (`JSON-FORMAT-NUR-ERBETEN`) — und die Trennung ist Absicht: Der eine Defekt erzeugt den Fehlschlag, dieser hier verschweigt ihn. Wäre nur der erste behoben, bliebe die Bilanz bei der nächsten unbrauchbaren Antwort genauso stumm.

**Der Mechanismus, in zwei Zeilen.** `erschliessen()` gibt bei unbrauchbarer Modellantwort `leer` zurück (`agents/dateien_index/indizieren.py`, `except (json.JSONDecodeError, …)`). Der Lauf verbraucht dafür sein Budget, schreibt aber keine Zeile. Und `fehler` in `agents/dateien_index/agent.py` sammelt ausschließlich **Ausnahmen je Wurzel** — ein Fehlschlag je Datei hat dort kein Fach.

**Warum das mehr ist als eine fehlende Zeile im Bericht.** Der Lauf trägt bereits `uebergangen_gruende` je Datei — die Bilanz kann also durchaus Auskunft über einzelne Dateien geben, und wer sie liest, darf annehmen, dass sie es vollständig tut. *„Übergangen, weil kein Text"* steht mit Pfad und Grund da; *„am Modell gescheitert"* steht nirgends. Damit sieht ein Lauf mit stillem Verlust genauso aus wie ein sauberer, der nur seine Obergrenze erreicht hat.

**Und der Wiederholversuch heilt es nicht — das ist der eigentliche Befund.** Über vier Läufe hinweg scheiterten dieselben Dateien: viermal je `novaberg-agent-dateien_k.md`, `novaberg-agent-notes.md`, `novaberg-ei-character-profiles_l.md`, `novaberg-gv-initiative_k.md`, dazu zweimal `novaberg-node-tribunal.md` — **18 Modellaufrufe ohne eine einzige Zeile.** Der Fehlschlag ist deterministisch und nicht zufällig; er hängt an diesen Dateien.

**Der Endstand ist deshalb der gefährlichste Teil.** Der letzte Lauf meldet `indiziert 20, offen 0, fehler: [], status: abgeschlossen` — die Sprache eines fertigen Laufs. Im Index stehen **155 von 160** Dateien. `offen: 0` heißt *„die Obergrenze hat nichts stehengelassen"* und nicht *„alles ist drin"*, und ohne die Differenz daneben ist der Unterschied nicht lesbar. Zu den fünf fehlenden gehört ausgerechnet `novaberg-agent-dateien_k.md` — das Konzeptdokument dieses Dienstes.

**Der schärfste Beleg ist der Lauf vom selben Tag, 07:12 UTC**, weil er in eine Zeile passt: `neu 5, geaendert 1` — sechs Dateien zu tun —, `indiziert 1`, `offen 0`, `fehler: []`, `status: abgeschlossen`. Fünf Fehlschläge, kein Wort darüber, und die Zahlen widersprechen sich, ohne dass etwas anschlägt.

**Reproduktionsweg.** `POST /admin/dateien/index` über eine Wurzel mit mehr Dateien als `DATEIEN_INDEX_MAX_PRO_LAUF`, dann in der Bilanz `neu` gegen `indiziert + offen` je Wurzel halten. Geht die Rechnung nicht auf, ist die Differenz die Zahl der verschwiegenen Fehlschläge. Am Ende einer Kette von Läufen dieselbe Probe gegen den Bestand: `SELECT count(*) FROM dateien_index WHERE wurzel_id = …` gegen die Zahl der Dateien mit indizierbarer Endung.

**Behoben.** Die Bilanz trägt je Wurzel `gescheitert` und `gescheitert_gruende` mit Pfad und Grund, nach dem Vorbild von `uebergangen_gruende`, und die Gesamtbilanz führt die Summe. **`gescheitert` steht neben `fehler`, nicht darin:** Jenes sammelt Ausnahmen je *Wurzel* — ein abgebrochener Lauf —, dieses zählt Dateien, die übergangen wurden, ohne dass etwas warf. Beides in einen Topf zu werfen machte aus einem stillen Verlust einen lauten Fehler und aus einem lauten Fehler eine Statistik.

**Der Riegel ist die Identität, nicht die Zeile.** Der Lauf rechnet `Kandidaten == indiziert + offen + gescheitert` nach und meldet als Fehler, wenn sie nicht aufgeht — *„eine Datei fällt zwischen die Fälle"*. Dazu eine eigene Fehlerzeile, sobald etwas scheitert: *„der Lauf ist trotz 'offen 0' nicht vollständig"*. Damit ist der Satz aus dem Befund im Code beantwortet: `offen: 0` heißt, die Obergrenze hat nichts stehengelassen, und nicht, dass alles drin ist.

**Ein Zeuge, und er prüft beides** — das Fach und die Rechnung: Eine Datei, deren Erschließung leer zurückkommt, erscheint mit Pfad unter `gescheitert_gruende`, und `neu == indiziert + offen + gescheitert` geht auf. Gegenprobe: das Fach ausgebaut → **1 vorhergesagt, 1 rot**. Suite **2000 grün**.

**Im Betrieb belegt:** Der Lauf vom 20.08.2026 meldet `indiziert 4, offen 0, gescheitert 0, fehler: []` — dieselbe Sprache wie zuvor, aber jetzt mit der Zahl, die den Unterschied trägt. Ein Lauf mit stillem Verlust ist von einem sauberen nicht mehr ununterscheidbar.

---

## Offene Bugs

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

### Neu gemessen am 09.08.2026 — die Ursache war eine andere, und die Hälfte ist behoben

**Der Befund oben beschreibt die Wirkung richtig und die Ursache falsch.** Nachgemessen am Code und an einem vollständigen Bogen:

- **Der Agent läuft nicht ab und löscht nichts.** `invoke` leerte die Queue schon immer in einer `while`-Schleife vollständig.
- **Die 300 s sind kein Fenster, sondern sein Takt** (`PIXIE_PROMOTION_INTERVALL_SEKUNDEN`).
- **Die Promotion ist nicht defekt — sie verhungert.** Sie tritt mit Prioritätsbasis **0,90** gegen die Aufträge an, die das Gespräch selbst erzeugt: nach Konrads Bogen lagen **63 Einträge mit Priorität 0,94 bis 1,00** in seiner Shadow-Queue. Dazu hält eine laufende `recherche` den einen Pixie-Platz minutenlang.

**Der Zeuge, Bogen konrad vom 09.08.2026:** 30 von 30 Turns, **0 Ausfälle**, 106 KZG-Einträge — und die Promotion kam in 28 Minuten **genau einmal** dran. **1 von 72 Aufträgen promotet, 71 warten, 1 LZG-Knoten entstanden.**

**Behoben ist der Verlust.** Der Auftrag wird nicht mehr per `lpop` entnommen, sondern per `LMOVE` in `queue:{paar}:arbeit` verschoben und erst nach grünem Ergebnis daraus entfernt; nach zwei Rückstellungen geht er auf den Fehlerstapel `queue:{paar}:gescheitert`. Nach dem Bogen waren Arbeitsliste, Fehlerstapel und Zählerhash **leer** — kein einziger Auftrag wurde verbraucht-und-verloren, keiner scheiterte.

**Dabei fiel eine zweite Hälfte des Defekts an, die niemand gesucht hatte:** Ein Lauf, in dem *jeder* Eintrag scheiterte, meldete `debug: „Queue leer — nichts zu tun"` — der Zweig unterschied nicht zwischen *nichts da* und *alles kaputt*, und die Zahl, die es unterscheidet, stand in derselben Funktion. Die Meldung nennt jetzt alle vier Größen auf `info`.

~~**Offen ist der Engpass.**~~ → **am selben Tag geschlossen** (siehe unten, zwei Spuren). 71 wartende Aufträge sind jetzt **sichtbar** statt still gelöscht — auswertbar ist der Gedächtnisstand deshalb noch nicht. Das ist `PIXIE-EIN-SLOT-BLOCKIERT-ALLES`, und die Reihe ist bis dahin nicht fahrbar: Siebzehn weitere Bögen ergäben siebzehn Personas mit je etwa einem Knoten.

**Was der Eintrag über Bug-Einträge zeigt.** Er benannte die Wirkung präzise und die Ursache plausibel — und die plausible Ursache hätte zu einem Umbau geführt, der nichts behoben hätte (ein Fenster, das es nicht gibt, zum Leerlaufen zu bringen). **Vor der Umsetzung eines Eintrags wird nicht seine Abhilfe gebaut, sondern seine Ursache nachgemessen.**

### ✅ Behoben am 09.08.2026 — zwei Spuren statt einer Schlange

Die Promotion konkurrierte um denselben Platz wie die Recherche, obwohl sie einen anderen Worker braucht. Der Hintergrund läuft seitdem in **zwei Spuren**: `llm` für alles mit Sprachmodell und Websuche, `cpu` für Rechnung und Einbettung, je mit eigenem Job, eigener Sperre und `max_instances=1`. Die Lastart steht am Agenten und wird **erzwungen** — ein `cpu`-Agent, der das Sprachmodell ruft, scheitert laut, statt seine Spur zu verstopfen.

**Der Beleg, derselbe Bogen wie der Nachweis des Defekts:**

| | vorher | nachher |
|---|---|---|
| Turns | 30/30, 0 Ausfälle | 30/30, 0 Ausfälle, 0 Zeitabläufe |
| Promotionen | **1** | **200** |
| LZG-Knoten | **1** | **55** |
| wartend am Ende | **71** | **3** |
| Arbeitsliste / Fehlerstapel | leer | leer |

Über neun Messpunkte während des Laufs blieb die Warteschlange zwischen 0 und 4 — sie schwankte im Takt, statt zu wachsen.

**Ein Rest bleibt, klein und systematisch:** Die drei am Ende sind der Schwanz zwischen dem letzten Takt und dem Zurückschalten auf das produktive Paar. Ab da bedient der Heartbeat die Persona nicht mehr, und diese drei werden nie promotet. Das trifft jede Persona in zufälliger Höhe. **Die Abhilfe gehört ins Messrig, nicht hierher:** Es wartet vor dem Zurückschalten, bis die Queue leer ist — was erst jetzt baubar ist, weil Warten gegen Verhungern nicht half.

~~**Band A** (Rangordnung in `novaberg-backlog.md`, Reihe 1). Hoch für jede Messreihe, die Arme vergleicht. Ohne die Abhilfe trägt jeder gepaarte Vergleich auf diesem Korpus einen unbeobachteten Störfaktor.~~

### ✅ Nachgemessen am 16.08.2026 — die Abhilfe hält nach sieben Tagen

**Der Beleg vom 09.08. stammt aus dem Bogen, an dem gebaut wurde.** Das ist der gebaute Weg; diese Prüfung geht quer dazu — sie fragt den **Bestand** statt den Zeugen, sieben Tage und einen laufenden Produktivbetrieb später.

| Paar | KZG-Schlüssel | LZG-Knoten | Verhältnis |
|---|---|---|---|
| `konrad` | 88 | **69** | 0,78 |
| `mehmet` | 98 | 59 | 0,60 |
| `sarah` | 92 | 51 | 0,55 |
| `leon` | 89 | 50 | 0,56 |
| `hartmut` | 95 | 48 | 0,51 |
| `meister` (produktiv) | 2203 | 2005 | 0,91 |

**Das Symptom ist damit widerlegt, nicht nur die Ursache.** Der Eintrag beschrieb *„völlig verschiedene Mengen an Langzeitwissen bei gleich langen Bögen"* und belegte es mit `konrad`: ein einziger Knoten. Konrad trägt heute **69**, und die fünf Personas liegen zwischen 48 und 69 — eine Spanne, die zur Spanne ihrer KZG-Stände passt (88 bis 98).

**Dazu der Betrieb statt der Suite:** Über zwei Stunden am 16.08.2026 gewann die Promotion **22-mal** die CPU-Spur und meldete dabei durchgehend `Queue leer — nichts zu tun`; in Redis existieren weder `queue:meister` noch `queue:meister:arbeit`, und eine leere Liste löscht sich dort selbst. **Rückstand null.**

**Was den Ausschlag gab, war nicht die Abhilfe an diesem Eintrag, sondern die Zwei-Spuren-Trennung.** Die Promotion braucht keinen Sprachmodell-Platz; seit sie auf der `cpu`-Spur läuft, konkurriert sie nicht mehr mit einer Recherche. Der benannte Rest — die letzten Aufträge einer Persona nach dem Zurückschalten — bleibt bestehen und ist unverändert klein.

---

### Zeitauflösung (Chat 119)

#### ZEIT-RUECKWAERTS-WIRD-ZUKUNFT — ein rückwärts gerichteter Zeitausdruck erzeugt einen Anker in der Zukunft ✅ Gelöst Chat 120
**Kategorie:** WIS

**(b) gelöst am 30.07.2026.** `zeit_parsen_vektor` reicht `referenz_modus` jetzt in die Auflösung durch; er wurde bis dahin berechnet, zurückgegeben und nicht übergeben. `seit` steht in der Richtungsprüfung und wird — wie `vergangene` — in der Normalisierung entfernt, weil es die Richtung trägt und nicht die Dauer; blieb es stehen, kannte `dateparser` den Ausdruck nicht und lieferte gar nichts.

Alle sieben Zeilen der Tabelle unten stimmen seitdem: `seit fünf Wochen`, `letzte fünf Wochen` und `vergangene fünf Wochen` ergeben −35 Tage, die Vorwärtsformen bleiben unverändert.

**`vor` steht bewusst NICHT in der Richtungsliste**, und der Unterschied ist gemessen: Mit `vor` darin löst „zehn vor acht" gegen eine Referenz um 17:10 auf **30.07. 07:50** auf — heute, längst vorbei — statt auf den nächsten Termin am Folgetag.

**(a) am 31.07.2026 neu gemessen — und der Befund trifft für `seit` nicht mehr zu.** Fünf Sätze durch die echte Extraktion, jeder einmal mit und einmal ohne Lagebild:

| Satz | `zeitausdruck_roh` |
|---|---|
| „**Seit** fünf Wochen sind keine zehn Millimeter Regen gefallen." | `'Seit fuenf Wochen'` — erhalten |
| „**Vor** zwei Wochen war das noch anders." | `'Vor zwei Wochen'` — erhalten |
| „Das Problem dauert **bereits** zwei Wochen." | `'zwei Wochen'` — **verworfen** |
| „Wir haben **schon** drei Tage nichts gehört." | `'drei Tage'` — **verworfen** |

`seit` und `vor` kommen durch, in beiden Varianten. Verworfen werden `bereits` und `schon`. **Die ursprüngliche Beobachtung — im Log stand `'fünf Wochen'` — ist damit nicht reproduzierbar**; sie bleibt oben stehen, weil sie den damaligen Stand festhält, taugt aber nicht mehr als Beleg.

**Behoben am 31.07.2026, an beiden Enden:** Die Anweisung nennt jetzt ausdrücklich, dass das Richtungswort zum Ausdruck gehört, und trägt vier Beispiele mit einem — sie hatte sechs, von denen keines eine Richtungspräposition enthielt. Danach überleben alle vier Wörter. Und der Parser deutet `bereits`/`schon` vor einer nackten Dauer als rückwärts; `bereits zwei Wochen` ergibt −14 Tage, `schon drei Tage` ergibt −3.

**Die Reihenfolge war der Punkt.** Der Wortschatz des Parsers wurde erst erweitert, nachdem gemessen war, dass die Extraktion die Wörter durchlässt. Vorher wäre es Arbeit an einem Weg gewesen, den nichts befährt — die Wörter hätten den Parser nie erreicht.

**Die Regel ist eng, und die Gegenprobe ist der Grund.** `bereits` und `schon` sind häufiger Verstärkungspartikel als Richtungswort. Eine Regel auf das bloße Wort löste `schon am Freitag` auf den vergangenen Freitag auf und `bereits nächsten Montag` auf den vergangenen Montag — aus Ausdrücken, die vorher gar nicht parsten, wurden welche, die falsch parsen. Deshalb muss unmittelbar eine Zahl und eine Zeiteinheit folgen.

**Was offen bleibt:** Die Extraktion ist über den Richtungsverlust hinaus unscharf — `zeitausdruck_roh` trug im Befund-Gespräch auch `'trockenen Sommer'` und `'Tageslicht'`. Das ist nicht gemessen und nicht angefasst.

**Entdeckt:** Chat 119, im Gedächtnis-Nachlauf eines Gesprächs.

**Symptom:** Der Satz „seit fünf Wochen sind keine zehn Millimeter Regen gefallen" (30.07.2026) erzeugte einen Timeline-Eintrag `erinnerungs_anker` auf den **03.09.2026** — fünf Wochen in die **Zukunft** statt in die Vergangenheit. Richtig wäre der 25.06.2026 gewesen.

**Zwei unabhängige Ursachen, die sich zusammensetzen:**

**(a) Die Extraktion verwirft das Richtungswort.** Der Salienz-Schritt legt den Rohausdruck in `zeitausdruck_roh` ab; gemessen am Log stand dort `'fünf Wochen'` — die Präposition `seit`, die allein die Richtung trägt, war schon weg. Was danach kommt, kann die Richtung nicht mehr kennen.

**(b) Der Parser wertet die Richtung nicht aus, auch wenn er sie erkennt.** `zeit_parsen_vektor` (`utils/zeitparser.py`) bestimmt `referenz_modus` über eine Präfix-Prüfung und ruft anschließend `zeit_parsen(text, referenz, zukunft_bevorzugt)` — **ohne den Modus zu übergeben**. Der Wert wird berechnet, im `ZeitVektor` zurückgegeben und steuert die Auflösung nicht.

**Reproduktionsweg**, gemessen am 30.07.2026 gegen Referenz 30.07.2026:

| Ausdruck | erkannter `referenz_modus` | aufgelöst |
|---|---|---|
| `fünf Wochen` | `relativ` | **03.09.2026 (+35 Tage)** |
| `seit fünf Wochen` | `relativ` | nicht geparst |
| `vor fünf Wochen` | `relativ` | 25.06.2026 (−35 Tage) ✓ |
| **`letzte fünf Wochen`** | **`relativ_rueckwaerts`** | **03.09.2026 (+35 Tage)** |
| `vergangene fünf Wochen` | `relativ_rueckwaerts` | nicht geparst |
| `seit drei Tagen` | `relativ` | nicht geparst |
| `vor drei Tagen` | `relativ` | 27.07.2026 (−3 Tage) ✓ |

Die vierte Zeile trägt den Kern: Die Richtung ist erkannt und wirkt nicht. Nur `vor` funktioniert, und zwar weil `dateparser` es selbst versteht — nicht durch das Zutun dieser Funktion.

**`seit` fehlt zusätzlich in beiden Listen:** weder in der Präfix-Prüfung des `referenz_modus` (`letzten?|vorigen?|vergangenen?`) noch im Wortschatz des Parsers. Ein nicht geparster Ausdruck ist dabei der harmlosere Fall — er trägt eine Warnung und legt keinen Anker an.

**Nicht die Ursache, aber im selben Feld gemessen:** `zeitausdruck_roh` trug im selben Gespräch auch `'trockenen Sommer'` und `'Tageslicht'` — Zeichenketten, die keine Zeitangaben sind. Die Extraktion ist über den Richtungsverlust hinaus unscharf.

**Wirkung:** Ein Anker in der Zukunft ist kein toter Eintrag. `erinnerungs_anker` trägt die Flags (False, False, False), ist also nicht bindend — aber er sitzt als Magnet im Gedächtnis und zieht Bezüge auf ein Datum, an dem nichts war. Zwei solche Einträge stehen seit dem 30.07.2026 live in der Timeline.

### Zeitparser und Fremdbibliothek (31.07.2026)

#### PARSER-EINSTELLIGE-STUNDE-STUERZT-AB — „morgen um 9 Uhr" wirft eine unbehandelte ValueError ✅ Gelöst 31.07.2026
**Kategorie:** WIS

**Gelöst am 31.07.2026.** Pfad 1 setzt das Datum aus seinen Teilen zusammen, so wie Pfad 1b es fuer `DD.MM.YYYY` immer schon tat.

**Entdeckt:** beim Schreiben der Tests fuer Pfad 1c — nicht gesucht, und der gesuchte Defekt war ein anderer.

**Symptom**, gemessen am Bestandsparser:

```
morgen um 9 Uhr   ->  ABSTURZ ValueError: Invalid isoformat string: '2026-08-01T9:00:00'
heute um 8 Uhr    ->  ABSTURZ ValueError: Invalid isoformat string: '2026-07-31T8:00:00'
morgen um 14 Uhr  ->  2026-08-01 14:00:00+02:00
```

**Mechanismus:** Das Muster von Pfad 1 erlaubt eine **einstellige** Stunde (`\d{1,2}:\d{2}`), `datetime.fromisoformat` verlangt zwei. Block 0b macht aus „morgen" ein ISO-Datum, die Uhrzeit-Bloecke aus „9 Uhr" ein `9:00` — und die Verkettung ergibt einen String, den `fromisoformat` ablehnt.

**Reichweite:** jeder Ausdruck mit deiktischem Tageswort **und** einstelliger Stunde. Das ist eine haeufige Sprechform. Zweistellige Uhrzeiten kamen durch, deshalb sah es nie nach einem Muster aus, sondern nach einem Einzelfall.

**Es war eine unbehandelte Ausnahme, kein falscher Wert** — sie verliess `zeit_parsen` und traf den Aufrufer.

---

### Zeitparser und Chat-Endpunkt (Chat 120)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### PARSER-MAERZ-FAELLT-DURCH — die Tippfehler-Korrektur zerstört den korrekt geschriebenen Monat ✅ Gelöst Chat 120
**Kategorie:** WIS

**Gelöst am 31.07.2026.** Die Monatsliste führt jetzt die Umlautform, und die ASCII-Umschreibungen werden vor der Fuzzy-Korrektur zurückübersetzt. Die Zuordnung wird aus den Wortlisten abgeleitet, nicht daneben geführt.

**Entdeckt:** Chat 120, beim Nachgehen einer Frage nach der Zahlwort-Normalisierung — nicht durch ein Audit.

**Symptom:** `zeit_parsen_vektor("15. März")` lieferte `None`. Jedes Datum im März fiel durch, also ein Zwölftel aller Datumsangaben.

**Mechanismus, und er ist die Pointe:** `_MONATE` trug nur `"maerz"`. Die Fuzzy-Korrektur fand ein korrekt geschriebenes „März" damit **nicht** als bekanntes Wort, suchte den nächsten Nachbarn und landete auf Distanz 2 bei der ASCII-Form — die `dateparser` nicht versteht. **Der Schritt, der Tippfehler reparieren soll, hat die richtige Schreibweise zerstört.**

**Reproduktionsweg**, gemessen am 31.07.2026:

| Aufruf | Ergebnis |
|---|---|
| `dateparser.parse("15. März", languages=["de"])` | 2026-03-15 |
| `dateparser.parse("15. Maerz", languages=["de"])` | **None** |
| `zeit_parsen_vektor("15. März")` — vor dem Fix | **None** |
| `_fuzzy_korrektur("15. März")` | `'15. Maerz'` |

Die dritte Zeile folgt aus der vierten: Was die Bibliothek versteht, machte unsere Vorstufe unverständlich.

**Ursache dahinter war Drift zwischen drei Listen:** Monate nur ASCII, Zahlwörter und Schutzwörter nur Umlaut, relative Tageswörter beides. Jede wird an anderer Stelle gelesen — deshalb fiel es nie auf.

**Wirkung:** Kein falscher Anker, sondern gar keiner. Der harmlose Ausfall, aber ein vollständiger für einen ganzen Monat.

---

#### PARSER-ZWEI-UHREN — deiktische Tagesworte und relative Dauern rechnen in verschiedenen Zonen ✅ Gelöst Chat 120
**Kategorie:** WIS

**Gelöst am 31.07.2026.** Die Referenz wird in die Ortszone gedreht, statt ihres Zonenvermerks beraubt zu werden.

**Entdeckt:** Chat 120, ausgelöst durch einen roten Test, der über Nacht rot geworden war.

**Symptom:** „übermorgen" und „in zwei Tagen" lieferten verschiedene Tage.

**Mechanismus:** `RELATIVE_BASE` muss naiv sein, und `settings["TIMEZONE"]` sagt der Bibliothek, dass sie naive Zeiten als **Ortszeit** liest. Übergeben wurde `referenz.replace(tzinfo=None)` — die UTC-Wanduhr, die damit als Ortszeit **umgedeutet** statt umgerechnet wurde. Block 0b rechnet dagegen mit `date.today()`, also lokal. Zwei Uhren in einem Aufruf.

**Reproduktionsweg**, Referenz 30.07.2026 22:30 UTC (= 31.07. 00:30 Ortszeit):

| Ausdruck | vor dem Fix | nach dem Fix |
|---|---|---|
| `übermorgen` | 2026-08-02 | 2026-08-02 |
| `in zwei Tagen` | **2026-08-01** | 2026-08-02 |

**Welche Seite recht hatte, folgt aus der Festlegung, nicht aus Geschmack:** Das Repository ist die einzige Stelle, die UTC kennt (`novaberg-tool-timeparser_l_timezone.md` §3). Vor dieser Grenze wird lokal gerechnet — die Tagesworte waren richtig, der Dauer-Pfad nicht.

**Alter:** Das Fenster ist die Zeitspanne zwischen lokaler und UTC-Mitternacht, im Sommer zwei Stunden täglich. Der Defekt bestand, seit die Referenz durchgereicht wird.

**Der Zeitparser ist die vierte Stelle**, die die Zonen-Umrechnung braucht, neben Schreiben, Lesen und Query-Range. Die Zentralisierung von damals hat ihn nicht erfasst, weil er kein Datenpfad ist, sondern ein Interpret — das Partial-Fix-Problem aus derselben Lesson.

---

### Prompt & Antwortqualität

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md), [Bauart](novaberg-bugs-archiv-bauart.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### ZEIT1 — Monat/Tag vertauscht bei Uhrzeit ✅ Gefixt Chat 41
**Kategorie:** WIS
**Entdeckt:** Chat 39, Claude API-Test (war als 5i bekannt, jetzt bestätigt)
**Symptom:** "morgen um 08:00 Uhr" → `2026-10-04T08:00:00` statt `2026-04-10T08:00:00`.
**Ursache:** Block 2 in `_text_normalisieren()` matchte "00" aus "08:00 Uhr" als Stunde.
**Fix (Chat 41):** Block 1b entfernt "Uhr" nach HH:MM. Block 2 Lookbehind `(?<!:)`. Zusätzlich ZEIT2 entdeckt und mitgefixt (Fuzzy: Montag→Sonntag).

---

### Agent-System (Epic 11, Chat 22–29)

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### AGENT-RUECKFRAGE-LOOP — Resume-Rückfrage rekursiert bis Recursion-Limit ✅ Behoben Chat 106
**Kategorie:** WIS

Bei einer Notiz-Disambiguierungs-Rückfrage (`_resume_duplikat`) führt eine
Antwort, die die Rückfrage nicht auflöst, zur Endlos-Rekursion: `resume`
liefert `status='rueckfrage'`, `dispatch_notizen` löscht den Pending-Key und
setzt ihn sofort neu, der `Planner` resumt **im selben Turn** erneut mit
derselben `user_answer` (`resume=True`), `_resume_duplikat` findet sie wieder
„unklar" → identische Rückfrage. ~60 Iterationen in ~230 ms bis
LangGraph `Recursion limit of 25 reached` → Graph-Crash, keine Antwort an den
User (über Telegram beobachtet).

Reproduktion Chat 103: Rückfrage „Es gibt bereits eine Notiz 'Neue Notiz
anlegen'…", User antwortet „Was steht in dieser Notiz?" (Gegenfrage statt
Wahl) → Loop → Crash.

Regression zu AGT-FIX3 (Chat 22, „Endlosschleife Planner ↔ Agent-Dispatch,
Recursion 25", gelöst via `bereits_gelaufen`-Dict): Der Schleifen-Schutz
greift für den Resume-Pfad nicht (mehr). Fix-Richtung: (1) Bei
`status='rueckfrage'` Turn beenden und auf echten nächsten User-Turn warten,
NICHT im selben Turn re-dispatchen; und/oder (2) `bereits_gelaufen`-Guard auf
den Resume-Pfad ausdehnen / Iterations-Budget im Resume. Ausgelöst durch
NOTIZ-BEFEHL-ALS-TITEL (Duplikate erzeugen die Disambiguierung überhaupt erst).

**Behoben Chat 106 (Commit `f1b3a27`):** Der Guard war nie kaputt — er wurde nur nie
gefragt. Der Resume-Pfad ist Priorität 0 im Planner und kehrte zurück, BEVOR der
`bereits_gelaufen`-Guard erreicht wurde; Chat 101 fuhr fünf Turns über den Agent-Pfad,
wo der Guard greift — die Stichprobe traf den Pfad daneben. Fix: Helfer
`_agent_bereits_gelaufen()` auf Modul-Ebene, aufgerufen an beiden Stellen (Resume-Zweig
VOR dem Setzen von `agent_name` + bestehender Epic-11-Block). Der Turn endet,
`_write_task_block` baut den inquiry-Block, der Pending-Key bleibt für den nächsten
echten User-Turn stehen. Damit sind beide Fix-Richtungen auf einmal erfüllt, und der Fix
wirkt für alle vier User-Agenten — der Guard sitzt zentral im Planner, nicht im Dispatch.
`iteration-control_k` bleibt geparkt (der Zyklus war strukturell, nicht quantitativ).
**Live bewiesen 11.7. 18:14:01** nach gezielter Provokation (Notiz-Duplikat → Rückfrage →
Gegenfrage statt Wahl): `Planner/Guard: results_im_turn=1, bereits_gelaufen=True` →
„Turn beenden, weiter zum Responder". Fünf Millisekunden, ein Durchlauf — vorher
60 Iterationen in 230 ms. Wichtig: Neun Live-Turns davor liefen sauber durch und bewiesen
nichts — alle neun nahmen den Agent-Pfad; der Loop braucht zwingend eine Rückfrage.

---

### Chat 110 (26.07.2026) — Impuls-Pfad, Gedächtnis-Duplikate und blinde Stellen

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

#### `RUECKWEG-SETZT-KOPIE-NEBEN-ORIGINAL` — der Fund stand schon da ✅
**Kategorie:** WIS

**Zustand:** behoben — gebaut und gemessen am 24.08.2026. `absatz_bestimmen` verlangt jetzt, dass ein Absatz mindestens **einen Satz** mitbringt, der noch nicht im Text steht (`_bringt_neues`); bringt er keinen, wird er als *steht schon da* behandelt. Zeugen `tests/test_rueckweg_dublette.py` (24), zwei Gegenproben (**6 vorhergesagt / 6 gezählt** am Riegel, **5 vorhergesagt / 2 gezählt** an der Schwelle), Suite `Ran 2272 tests — OK`, 0 übersprungen.

> **Die erste Fassung verglich auf Gleichheit und war damit zu schwach.** Sie fing **12 von 18** Doppelgängern; die übrigen sechs waren Umformulierungen desselben Satzes, und ein umgestelltes Wort genügte, um durchzukommen. **Bei zweien sagte die „neue" Fassung sogar weniger als die alte.**
>
> Verglichen wird jetzt über **Trigramm-Übereinstimmung**, Schwelle `AEHNLICH_GENUG = 0.65`. Die Zahl ist an den echten Fällen abgelesen: Über die 232 Einarbeitungen liegen 12 auf 1,00, sechs zwischen 0,65 und 0,95 (allesamt Umformulierungen ohne neuen Gehalt), dann sechs zwischen 0,50 und 0,65 (gemischt) und 208 darunter. **Ein sauberes Tal gibt es nicht** — bei 0,65 kippt das Urteil beim Lesen, und zwei Umformulierungen darunter laufen durch.
>
> **Die Schwelle liegt bewusst hoch, und der Grund ist die Asymmetrie der Kosten:** Ein durchgelassener Doppelgänger ist ein doppelter Absatz — sichtbar, zählbar, mit einem Werkzeug zurücknehmbar. Ein fälschlich abgewiesener Fund ist **fort**: `steht_schon_da` reiht nicht wieder ein, und niemand erfährt, was verloren ging. Ein Zeuge hält die Grenze ausdrücklich fest: Wer rund ein Drittel des Satzes weglässt, kommt durch.
>
> **Geeicht an `pg_trgm.similarity()`** — in dieser Datenbank vorhanden — über 60 echte Paare: größte Abweichung **0,083**, mittlere **0,025**, und **0 Paare mit abweichendem Urteil** an dieser Schwelle. Die Rechnung bleibt trotzdem im Code: Ein Datenbankaufruf für einen reinen Textvergleich fügt einen Ausfallpfad hinzu, der still wäre.
>
> Über die 232 echten Einarbeitungen: **18 gefangen, 214 durchgelassen** (vorher 12 / 220). Die gemessene Nähe steht bei jeder Abweisung im Log, damit die Schwelle aus dem Betrieb nachjustierbar bleibt statt aus der Erinnerung.

> **Und dann reicht auch die justierbare Zahl nicht — am 25.08.2026 nachgemessen und behoben.** Ein Nebensatz verschiebt die Übereinstimmung weiter, als eine Schwelle reicht: Im Bestand liegt ein echter Doppelgänger bei **0,452** und eine echte Ergänzung bei **0,622**. **Der Doppelgänger ist unähnlicher als der Fund**, und keine Schwelle kann das ordnen.
>
> Die Zahl löst deshalb jetzt die **Frage** aus statt sie zu beantworten. Drei Zonen: ab 0,65 Kopie ohne Aufruf (18 von 232), unter 0,35 eingearbeitet ohne Aufruf (195), dazwischen **ein Modellaufruf je Satz** (19 von 232, also 8 %). Der untere Rand liegt zehn Hundertstel unter dem schwächsten nachgewiesenen Doppelgänger.
>
> **Gefragt wird schmal.** `rueckweg_dublette.*` stellt eine Frage und schreibt nichts — im Unterschied zum Einarbeitungs-Aufruf, dem dieselbe Auskunft eine von vier Aufgaben ist und der mit *„schreibe einen Absatz"* konkurriert. Über die 19 Grenzfälle: **19 von 19 beantwortet**, 10 Fund / 9 Dublette, und das entscheidende Paar richtig herum — 0,622 → Fund, 0,452 → Dublette.
>
> **Ein ausgefallenes Urteil führt zur Einarbeitung, nicht zur Abweisung**, und der Unterschied steht als `error` im Log.

**Symptom.** Der Rückweg arbeitet Funde in bestehende Wissensdateien ein: Er spaltet einen Absatz hinter einem Anker und setzt den Fund in die Naht, mit Marke `[iN>]`. Schlägt das Modell als Fund einen Satz vor, **der schon dasteht**, landet die Kopie unmittelbar neben ihrem Original:

```
… Synapsenlast gesenkt und die regulatorische Stabilität erhöht wird. [i2>]
… Synapsenlast gesenkt und die regulatorische Stabilität erhöht wird.
```

**Der Aufruf hat für diesen Fall einen eigenen Ausgang** — `nach=None`, *steht schon da* — und benutzt ihn nicht zuverlässig. Geprüft wurde er nie.

**Gemessen am 24.08.2026 über 474 Wissensdateien:**

| | |
|---|---|
| wörtlich doppelte Absätze | **17** |
| unmittelbar wiederholte Sätze im selben Absatz | **7** |
| betroffene Dateien | **22** |
| davon in einem einzigen Durchgang entstanden | **5** |
| Einarbeitungen dieses Durchgangs | 232 |
| davon ohne einen neuen Satz | **12** |
| davon echte Funde | **220** |

> **Der Fehler ist still gegen die einzige Prüfung, die es gab.** `paarung_pruefen` wacht über die Invariante *eine Marke, ein Eintrag* — und die hält: Die Kopie bekommt ihre Marke, der Eintrag steht im Archiv, die Version wird fortgeschrieben. **Eine Invariante über die Buchführung sagt nichts über den Inhalt, den sie verbucht.** Nur wer den Absatz liest, sieht ihn doppelt.

**Zwei Formen, und die Marken entscheiden über die Behandlung.** Beim Satz im selben Absatz trägt nur eine Kopie die Marke — die überlebt. Beim doppelten Absatz an zwei Stellen tragen **beide** eine eigene Marke; dort fällt die zweite Fassung, aber ihre Marke wandert an die erste (`Text [i4>] [i5>]`), damit kein Archiveintrag verwaist.

**Der Bestand ist geräumt** (`labor/2026-08-24_dubletten_ruecknahme.py`): 23 Dateien, 7 Sätze und 18 Absätze zurückgenommen, danach **0 wörtliche Dubletten**.

> **Das Räumwerkzeug verglich ebenfalls exakt, und damit bleibt ein Rest.** Mit derselben Trigramm-Schwelle nachgemessen stehen im Bestand noch **29 Absatzpaare über 0,65**, bis hinauf zu 0,96 — in einer Datei drei fast gleiche Absätze. **Sie werden nicht automatisch zusammengefaltet:** Bei einer wörtlichen Kopie sagt die zweite Fassung nachweislich nichts Eigenes, bei 0,80 kann die Differenz der Inhalt sein. Das ist eine Entscheidung je Fall und keine Schwelle — geführt in der Fundliste. Gegengeprüft mit der Produktivfunktion `paarung_pruefen` über alle 474 Dateien: **474 heil, 0 Befunde.** Die Gegenprobe am Werkzeug — Markenrettung abgeschaltet — hätte 12 Dateien wegen gerissener Paarung übersprungen; der Riegel greift also nachweislich.

**Verwandt:** `KZG-SEGMENT-DUPLIKAT` und `PROMO-QUEUE-DUBLETTEN` (dieselbe Klasse an anderer Stelle: etwas entsteht zweimal, und die Buchführung darüber stimmt).

---

## Nachgeprueft am 25.08.2026 — geschlossen beim Durchgang durch die ungeprueften Eintraege

> **Geteilter Abschnitt.** Seine Eintraege liegen in mehreren Gegenstaenden; hier stehen die von **Wissen**, die uebrigen in [Gedächtnis](novaberg-bugs-archiv-gedaechtnis.md), [Hintergrund](novaberg-bugs-archiv-hintergrund.md), [Charakter](novaberg-bugs-archiv-charakter.md), [Antwortpfad](novaberg-bugs-archiv-antwortpfad.md). Ueberschrift und Text stehen in jedem empfangenden Teil.

**Diese 20 Eintraege standen als offen im Register und waren es nicht mehr.** Sie sind am 25.08.2026 einzeln gegen den Code und den Bestand gehalten worden; die Zustandszeile je Eintrag nennt, woran das erkennbar ist. Sie stammen aus derselben Pruefung, die den Schnitt zwischen Register und Archiv ausgeloest hat.

**Zwei Ausgaenge sind zu unterscheiden.** *Behoben* heisst: Die Abhilfe steht im Code. *Gegenstandslos* heisst: Der Befund ist nicht widerlegt, aber die Stelle, an der er galt, gibt es nicht mehr — wer sie zurueckholt, holt ihn mit.

---
#### FAK1 — Temporalität in Fakten
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen. Siehe `FAKTEN-RAUSCH`. Die Frage nach `permanent` gegen `situativ` bleibt offen, sobald der Speicher wieder befuellt wird.
**Lösung:** Klassifikation: `permanent` → Fakten-Tabelle, `situativ` → nur KZG.

---

#### D9 — Fakten-Deduplizierung
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen. Siehe `FAKTEN-RAUSCH`. Eine Deduplizierung ohne Bestand hat keinen Gegenstand.
**Lösung:** Embedding-basierter Ähnlichkeitscheck vor dem Schreiben.

---

#### FAK-LECK — Charakter-Anweisungen als User-Fakten extrahiert
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — `fakten` traegt 0 Zeilen, die Extraktion laeuft nicht. Siehe `FAKTEN-RAUSCH`. Der Befund ist nicht widerlegt: Eine Extraktion, die Anweisung an die Figur und Aussage ueber den Menschen nicht unterscheidet, wuerde dasselbe wieder tun.
**Entdeckt:** Chat 40
**Symptom:** "Du bist ein freches Mädel vom Land" wird als Fakt über den User extrahiert: `meister IST junges, freches, lustiges Mädel vom Land`, `meister LIEBT Botanik`.
**Ursache:** Die Fakten-Extraktion (Salienz/Pixie) kann nicht zwischen "Anweisung an Nova" und "Information über den User" unterscheiden.
**Workaround:** Manuell bereinigt (`aktiv = FALSE`).
**Prio:** Niedrig — tritt nur bei Charakter-Anweisungen auf, selten.

---

#### FAKTEN-RAUSCH — Fakten-Enrichment produziert massenhaft Rauschen Deaktiviert
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — nicht behoben, sondern ohne Gegenstand. Die Tabelle `fakten` traegt **0 Zeilen**, und der Anreicherungspfad, der das Rauschen erzeugte, ist stillgelegt. **Wer die Fakten-Anreicherung wieder einschaltet, holt diesen Befund mit** — der Eintrag bleibt deshalb stehen, zusammen mit `FAK-LECK`, `FAK1`, `D9` und `ENRICHER-DUP`, die alle denselben Gegenstand hatten.
**Entdeckt:** Chat 71
**Symptom:** Fakten-Enrichment produziert 130+ Einträge für User "meister", davon die meisten Rauschen: `VERWENDET_BELEIDIGUNG = Fotzen`, `HAT_VISITENKARTE = Code`, `BEHERRSCHT = Markdown`, `LEGT_AB = Schwarzweiß-Brille`, `HALTET_SICHER_UND_FEST = schwarzes Geschöpf`.
**Ursache:** Salienz-Agent extrahiert zu aggressiv Fakten aus Gesprächskontext, ohne Qualitätsfilter. Rollenspiel-Inhalte, einmalige Erwähnungen und metaphorische Sprache werden als Fakten gespeichert.
**Workaround:** Fakten-Enrichment im Enricher deaktiviert (Chat 71).
**Fix:** Fakten-Bereinigung (manuelle DB-Cleaning + Salienz-Prompt-Tuning für Fakten-Extraktion). Phase 4 (CRUD gerade ziehen).

---

#### ENRICHER-DUP — Fakten werden mehrfach in den Enricher-Kontext injiziert
**Kategorie:** WIS

**Zustand:** **gegenstandslos seit dem 25.08.2026** — die mehrfach eingespeisten Fakten kommen aus einer Tabelle, die heute 0 Zeilen traegt; der Weg ist stillgelegt. Siehe `FAKTEN-RAUSCH`.
**Entdeckt:** Chat 62, Beobachtung im memory_context-Log
**Symptom:** Einzelne Fakten (beobachtet: `HAT_FREUNDIN`) erscheinen 4–7 Mal hintereinander im destillierten Enricher-Kontext, der an den Responder geht. Der Kontext wird unnoetig aufgeblaeht, und das LLM kann den Fakt als besonders wichtig (weil haeufig genannt) fehldeuten.
**Ursache (vermutet):** Der Enricher holt Fakten aus mehreren Quellen (KZG, LZG, Knowledge Graph, evtl. Timeline) ohne nachgelagerte Dedup-Stufe. Bei ueberlappenden Retrieval-Treffern wandert derselbe Fakt mehrfach in die Liste.
**Loesungsansatz:** Deduplizierungs-Schritt im Enricher nach dem Sammeln — einfacher Set-Filter auf `subjekt+attribut+objekt`-Tripel oder Embedding-Aehnlichkeit.
**Status Chat 74:** Reducer-Erst-Iteration adressiert das Problem teilweise. Beobachtung im Live-Log: bei ~30 Einträgen werden 1-2 Duplikate pro Turn entfernt — also weniger als ursprünglich vermutet. Wichtige Erkenntnis: ENRICHER-DUP ist nicht das Hauptproblem des memory_context, sondern thematisch unpassende Einträge (Embedding-Schrott, Anna im Katzen-Chat). Reducer-Umbau wird beide Aspekte sauberer adressieren.
**Prio:** Beobachtung — noch kein bestaetigter Funktionsbruch, aber kontext- und qualitaetsrelevant. Bei naechstem Auftreten Details sammeln (welche Quellen liefern den Fakt?).

---
