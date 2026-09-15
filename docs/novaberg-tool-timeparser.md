# Novaberg — Tool: Zeitparser

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Technik Zeitparser (Natürlichsprachliche Zeitauflösung)
**Stand:** 15. September 2026 (die Stunde ohne „Uhr" ist eine Uhrzeit: §4 *Vor Block 0*, Block 0, Block 9b; drei Zeilen in §8 geschlossen, sieben benannt). Davor 14. September 2026 (§8: die Grenze *Einzelne Ziffer ohne Uhr* im Betrieb gemessen). Davor 31. Juli 2026 (Marker-Stufe: die Richtung wird in EINEM Durchlauf gelesen statt aus zwei Textzustaenden rekonstruiert; Pfad 1c fuer nackte Uhrzeiten; `_heute_lokal()` statt `date.today()`. Zuvor: Zonen-Grenze, andauernde Dauern, Umlaut-Umschrift)
**Pfad:** novaberg/docs/novaberg-tool-timeparser.md
**Quellen:** nova-02-t-c.md
**Datei:** `utils/zeitparser.py`
**Tests:** 105 — `tests/test_zeitparser_bare_hour.py` (35), `tests/test_zeit_richtung.py` (20), `tests/test_zeit_nackte_uhrzeit.py` (15), `tests/test_zeit_dateparser_riegel.py` (12), `tests/test_zeit_umlaute.py` (11), `tests/test_zeit_dauer_einzahl.py` (7), `tests/test_zeit_bezugsmoment.py` (5). Die Kopfzeile nannte bis zum 15.09.2026 nur vier Dateien mit 58; die beiden letzten fehlten darin
**Korpus:** `tests/korpus/zeitausdruecke.yaml`, 92 Faelle, gefahren ueber `tests/korpus_laeufer.py`

---

## 1. Aufgabe

Der Zeitparser löst natürlichsprachliche deutsche Zeitausdrücke in `datetime`-Objekte auf. Er ist die Brücke zwischen dem LLM (das den Zeitausdruck als String extrahiert) und der Datenbank (die ein exaktes Datum braucht).

> **Grundprinzip:** Das LLM extrahiert den Zeitausdruck als wörtlichen String — „am Donnerstag um 14 Uhr", „übermorgen früh", „dreiviertel acht". Python löst ihn deterministisch auf. Kein LLM rechnet Kalender.

→ Warum dieses Prinzip: novaberg-tool-timeparser_l_evolution.md

---

## 2. Vierstufige Architektur

```
User: "Trag ein: Zahnarzt am Donnerstag um 14 Uhr"
    │
    ▼
Salienz: temporal_fact.date = "am Donnerstag um 14 Uhr"
    │
    ▼
zeit_parsen("am Donnerstag um 14 Uhr")
    │
    ├── Stufe 1: Fuzzy-Korrektur
    │     "Donerstag" → "Donnerstag" (Levenshtein ≤ 2)
    │
    ├── Stufe 2: Marker-Extraktion  (neu, 31.07.2026)
    │     Richtung, Ankerart und Versatz in EINEN Befund;
    │     der Rumpf verliert nur, was dateparser verwirren würde
    │
    ├── Stufe 3: Normalisierung (12 Blöcke)
    │     "am Donnerstag um 14 Uhr" → "Donnerstag 14:00"
    │
    ├── Stufe 4: 4-Pfade-Parsing
    │     Pfad 1  (Direkt): ISO- oder DD.MM.YYYY-Datum? → nein
    │     Pfad 1c (Uhrzeit): nur HH:MM? → nein
    │     Pfad 2  (Split):  Uhrzeit raus, Datum separat → "Donnerstag" + 14:00 → ✅
    │     Pfad 3  (Fallback): dateparser komplett → (nicht nötig)
    │
    └── Stufe 5: Plausibilitäts-Check
          > 2 Jahre Vergangenheit? → verwerfen
          > 5 Jahre Zukunft? → verwerfen
          → 2026-03-27T14:00:00+01:00 ✅
```

---

## 2a. Stufe 2: Die Marker-Extraktion

**Ein Durchlauf, ein Ergebnis.** `_marker_extrahieren()` liest die Richtungsmarker und gibt zwei Dinge zurueck: den **Rumpf**, der weitergereicht wird, und einen **`MarkerBefund`** mit Richtung, Ankerart, Versatz, den gefundenen Woertern und den Kennungen der Regeln, die gegriffen haben.

**Warum es diese Stufe gibt.** Bis zum 31.07.2026 wurde die Richtung **zweimal** ermittelt, ueber zwei verschiedene Zustaende desselben Textes: Block 9 loeschte die Richtungswoerter waehrend der Normalisierung, und ein zweiter Regex-Durchlauf in `zeit_parsen_vektor` rekonstruierte die Richtung aus dem *korrigierten, nicht normalisierten* Text. Zwei Pipelines, die synchron bleiben mussten — und die es nicht taten.

**Die Regeln stehen als Daten, nicht als Regex-Kette.** Jede `MarkerRegel` traegt eine Kennung (`M-01` bis `M-09`), ein Muster, eine Richtung, eine Ankerart, einen Versatz und ein `entfernen`-Flag.

> **`richtung` und `entfernen` sind bewusst unabhaengig.** Ein Marker kann Richtung tragen und trotzdem im Rumpf bleiben muessen: `vor` versteht `dateparser` selbst, `seit` nicht. Wer beides in ein Flag legt, waehlt fuer jeden neuen Marker den falschen Kompromiss.

| Kennung | Trifft | Richtung | bleibt im Rumpf |
|---|---|---|---|
| `M-01` | „bereits/schon/erst" **+ nackte Dauer** | rueckwaerts | nein |
| `M-02` | „noch" + nackte Dauer | vorwaerts | nein |
| `M-03` | „seit" | rueckwaerts | nein |
| `M-04` | „vor" + nackte Dauer | rueckwaerts | **ja** |
| `M-05` | „uebernaechste…" | vorwaerts, +7 Tage | nein |
| `M-06` | „naechste…", „kommende…" | vorwaerts | nein |
| `M-07` | „letzte…", „vorige…", „vergangene…" | rueckwaerts | nein |
| `M-08` | „bereits/schon/erst/nur/bloss" ohne Dauer | **keine** | nein |
| `M-09` | „diese[nmrs]" | keine, Anker „jetzt" | **ja** |

**Die Reihenfolge ist Prioritaet:** Die erste Regel, die eine Richtung setzt, gewinnt. Alle passenden Regeln werden trotzdem angewandt, damit ihre Entfernung und ihr Versatz greifen.

> **Jede Regel prueft gegen einen Rumpf, den frueher gelaufene Regeln bereits veraendert haben.** Das ist tragend — es ist der Grund, warum „schon seit zwei Wochen" funktioniert: `M-03` nimmt „seit" heraus und setzt die Richtung, danach raeumt `M-08` das „schon" ab, ohne eine zweite Richtung zu behaupten. Wer eine Regel einfuegt, aendert damit die Bedingungen aller nachfolgenden.

**Die Praefixformen werden aus Staemmen erzeugt**, nicht daneben gepflegt. Bis zum 31.07.2026 standen sie als Literale in den Regexen und damit in einer dritten, handgefuehrten Liste; keine bekam ihre ASCII-Umschreibung abgeleitet, und „naechsten Montag" behielt sein Praefix. Die Dativendung `-m` ist aufgenommen — „seit letztem Jahr" ist gaengiges Deutsch, die alten Regexe kannten nur `[nrs]`.

---

## 3. Stufe 1: Umlaut-Umschrift und Fuzzy-Korrektur

### 3.0 Umlaut-Umschrift — vor allem anderen

Wer ohne Umlaute tippt, schreibt „maerz", „fuenf", „zwoelf". `dateparser` kennt nur die Umlautform und liefert für „15. Maerz" nichts, während es „15. März" versteht. Die Umschreibungen werden deshalb zurückübersetzt, **bevor** die Fuzzy-Korrektur läuft — sie soll ein bekanntes Wort sehen und kein unbekanntes, das sie auf Distanz 2 irgendwohin zieht.

**Die Zuordnung wird aus den Wortlisten abgeleitet, nicht daneben geführt.** Jedes Wort mit Umlaut in `_WOCHENTAGE`, `_MONATE`, `_RELATIVE`, `_ZAHLWOERTER` und `_GESCHUETZTE_WOERTER` bekommt automatisch seine Umschreibung als Schlüssel. Der Grund steht in §9: Eine zweite, von Hand gepflegte Liste war genau die Ursache des Fehlers, den diese Stufe behebt.

Heute ergibt das fünf Einträge: `maerz`, `uebermorgen`, `fuenf`, `zwoelf`, `frueh`.

> **Nur ganze Wörter, nur bei vollständiger Übereinstimmung.** Eine Ersetzung der bloßen Buchstabenfolge machte aus „heute" ein „heüte" und aus „neue" ein „neü". Die Tests dafür stehen gleichberechtigt neben denen für die Ersetzung.

### 3.1 Fuzzy-Korrektur

Levenshtein-Distanz gegen Wochentage, Monate und relative Zeitbegriffe. Maximale Distanz: 2.

| Eingabe | Korrektur | Distanz |
|---------|-----------|---------|
| „Frietag" | „Freitag" | 1 |
| „Donerstag" | „Donnerstag" | 1 |
| „Septmeber" | „September" | 2 |

**Schutzliste (`_GESCHUETZTE_WOERTER`):** Wörter, die der Fuzzy-Korrektur nicht unterzogen werden dürfen — weil sie fälschlich auf Zeitbegriffe matchen:

| Problem | Schutz |
|---------|--------|
| „morgens" → „morgen" | `morgens` geschützt (Tageszeit ≠ relatives Datum) |
| „acht" → „nachts" | `acht` geschützt (Zahl ≠ Tageszeit) |
| „halb", „viertel", „dreiviertel" | Geschützt (Bruchteile, keine Wochentage) |
| **„Tag" → „Mai", „Monat" → „Montag"** | **seit 25.08.2026 `_ZEITEINHEITEN` geschützt** — Einzahl und Mehrzahl aller sieben Einheiten |

> **Die Einzahlform einer Dauer-Einheit ist kurz genug, um auf einen Monatsnamen zu fallen.** `Tag` → `Mai` und `Monat` → `Montag` liegen beide auf Distanz 2 und damit innerhalb von `max_distanz`. Gemessen gegen Referenz 30.07.2026: `in einem Tag` ergab den **01.05.2027**, `in einem Monat` den **01.07.2026** — 29 Tage *rückwärts*, obwohl die Zukunft bevorzugt wird.
>
> **Die Mehrzahlformen waren nie betroffen, und daran lag es, dass es niemandem auffiel:** `Tagen` und `Monaten` sind lang genug, dass keine Korrektur greift. Der Defekt sah aus wie ein Einzahl-Problem (`ZEIT-EINZAHL-GREIFT-DANEBEN`) und war eines der **Wortlänge** — er traf jede Zahl, auch `in 2 Tag`.
>
> Geschützt sind deshalb **alle** sieben Einheiten in beiden Formen, auch die heute unauffälligen: Was eine Zeiteinheit benennt, ist nie ein verschriebener Monatsname, und die Regel soll nicht daran hängen, welche Distanz eine einzelne Form gerade hat.

**Die Schutzliste ist unvollständig, und das ist gemessen.** Über 57 gebräuchliche Wörter am 25.08.2026: **13 werden auf einen Monats- oder Wochentagsnamen gezogen** — darunter `mittag` → `montag`, `mail`/`main`/`mais`/`rat`/`rad` → `mai`, `apfel` → `april`, `dienst` → `dienstag`. Der Fall `Mittag` ist der teuerste: Er löst auf den **nächsten Montag** auf statt auf 12:00 Uhr desselben Tages, während `mittags` mit s korrekt rechnet. Steht in der Fundliste, nicht behoben.

---

## 4. Stufe 2: Normalisierung (12 Blöcke)

Die Normalisierung transformiert deutsche Zeitausdrücke in ein Format, das `dateparser` verarbeiten kann. Konzeptionell 12 Blöcke in fester Reihenfolge. Im Code (`_text_normalisieren()` in `utils/zeitparser.py`) sind die Blöcke 0–9 nummeriert (mit Sub-Blöcken 0b, 0c, 1b); „Halb" ist im Code als Sub-Regex innerhalb des Viertel-Blocks implementiert, nicht als eigener Block 5:

### Vor Block 0: Stunde vor Tageszeit

„3 nachmittags" → „15:00", **bevor** Block 0 die Tageszeit herausnimmt (`_read_hour_before_daypart`, seit 15.09.2026). Bis dahin tat das Block 3 — hinter der Extraktion, wo das Paar nicht mehr stand: Die „3" blieb allein zurück und wurde zum Tag des Monats (`3 15:00` → der 03.).

Nicht gelesen wird die Zahl hinter einem Doppelpunkt, einer Ziffer, einem Punkt oder „Uhr " — „15:00 nachmittags", „01.07. nachmittags", „3 Uhr **15** nachmittags" — und keine Zahl über 23.

### Block 0: Tageszeit extrahieren

Tageszeit-Wörter werden extrahiert und als Fallback-Uhrzeit gemerkt — nur eingefügt wenn am Ende keine Uhrzeit im String steht.

| Tageszeit | Fallback-Uhrzeit |
|-----------|-----------------|
| `früh` | 06:00 |
| `morgens` | 08:00 |
| `vormittags`, `vormittag` | 10:00 |
| `mittags` | 12:00 |
| `nachmittags`, `nachmittag` | 15:00 |
| `abends`, `Abend` | 18:00 |
| `nachts` | 22:00 |

**Die Einzahl steht neben der Mehrzahl, weil sie nach einem Tageswort die gesprochene Form ist** — „heute abend", „morgen nachmittag". `vormittag` und `nachmittag` kamen am 15.09.2026 dazu; bis dahin löste „morgen nachmittag um 3" zu nichts auf. **„nacht" fehlt mit Absicht:** „heute Nacht um 2" meint den Morgen des Folgetags, und diese Rechnung kann der Parser nicht; ohne Eintrag bleibt der Ausdruck unaufgelöst, statt still auf heute 02:00 zu fallen.

**Gemerkt wird seit dem 15.09.2026 auch das Wort, nicht nur seine Fallback-Uhrzeit.** Eine vorangestellte Tageszeit verschiebt die Stunde, die ihr folgt, wie eine nachgestellte — in Block 1, Block 2 und Block 9b. Bis dahin ging die Verschiebung mit dem herausgeschnittenen Wort verloren: „nachmittags um 3 Uhr" ergab 03:00, „heute abend um 8 Uhr" 08:00. Die Verschiebung selbst steht für die neuen Formen an einer Stelle, `_shift_hour_by_daypart`: **+12 bei einer Stunde unter 12 und einer Tageszeit ab Mittag, „12 nachts" → 0** — die Regel von Block 2.

### Block 0a: „am" entfernen

„am Donnerstag" → „Donnerstag". Das „am" verwirrt dateparser bei deutschen Ausdrücken.

### Block 0b: Relative Tage → ISO-Datum

| Ausdruck | Ergebnis (bei heute = 2026-03-25) |
|----------|----------------------------------|
| „heute" | 2026-03-25 |
| „morgen" | 2026-03-26 |
| „übermorgen" | 2026-03-27 |
| „gestern" | 2026-03-24 |
| „vorgestern" | 2026-03-23 |

Python berechnet das Datum — nicht das LLM. Deterministisch.

**Diese Wörter sind deiktisch: Sie hängen am heutigen Kalendertag, nicht an `referenz`.** Das ist der Unterschied zu relativen Dauern („in drei Tagen"), die gegen die übergebene Referenz rechnen. Der Unterschied ist beabsichtigt und hat einen konkreten Grund: Der Update-Pfad des TimelineManagers reicht als Referenz die Zeit des **bestehenden** Termins durch (§10.4). Würde „morgen" ihr folgen, verschöbe „verschieb ihn auf morgen" einen Termin im August auf den Tag nach jenem Termin statt auf den Tag nach heute.

~~**Gerechnet wird in der Ortszone**, mit `date.today()`.~~ → **Ueberholt, 31.07.2026:** Gerechnet wird mit `_heute_lokal()`. `date.today()` liest die **Systemzone**, nicht `TIMEZONE` aus der Konfiguration; im Behaelter ist keine `TZ` gesetzt, also UTC. Damit klaffte dieselbe Luecke weiter, die der Fix am Vortag schliessen sollte — gemessen fuer 2026-07-30 22:30 UTC: Block 0b sah den 30.07., die Referenz fuer Dauern den 31.07. Das folgt der Grenzregel aus `novaberg-tool-timeparser_l_timezone.md` §3: Das Repository ist die einzige Stelle, die UTC kennt; alles davor arbeitet lokal.

> **Beide Wege müssen dieselbe Uhr benutzen.** Die Referenz für Dauern wird deshalb in die Ortszone **gedreht**, nicht ihres Zonenvermerks beraubt (§5). Bis zum 31.07.2026 geschah das Zweite — damit lagen „übermorgen" und „in zwei Tagen" in den Stunden zwischen lokaler und UTC-Mitternacht **einen Tag auseinander**.

### Block 0c: Deutsches Datum ohne Jahr

„01.07." oder „15.04." → „01.07.2026" oder „15.04.2026". Aktuelles Jahr ergänzen.

### Block 1: Zahlwort-Uhrzeiten

„drei Uhr nachmittags" → „15:00". Zahlwörter (`_ZAHLWOERTER`: eins bis zwölf) werden aufgelöst, optionaler Tageszeit-Suffix addiert den 12-Stunden-Offset.

### Block 2: Numerische Uhrzeiten

„14 Uhr 30" → „14:30". „3 Uhr nachmittags" → „15:00".

### ~~Block 3: Standalone Tageszeit~~

~~„3 nachmittags" → „15:00" (Zahl + Tageszeit ohne „Uhr").~~

→ **Entfernt am 15.09.2026, ersetzt durch *Vor Block 0*.** Der Block stand hinter der Extraktion und bekam das Paar nur noch zu sehen, wenn der Ausdruck eine zweite Tageszeit trug.

### Block 4: Fränkisch/Süddeutsch

„dreiviertel acht" → „7:45". Die Zahl nach „dreiviertel" ist die nächste volle Stunde, ¾ davon ist 45 Minuten der vorherigen.

### Block 5: Halb

„halb drei" → „2:30".

### Block 6: Viertel vor/nach

„viertel vor acht" → „7:45". „viertel nach acht" → „8:15".

### Block 7: Viertel regional

„viertel acht" → „7:15" (norddeutsch: ¼ der Stunde = 15 Minuten der vorherigen).

### Block 8: Minuten vor/nach

„zehn vor acht" → „7:50". „fünf nach drei" → „3:05". Zahlwörter für Minuten und Stunden aufgelöst.

### Block 9: Reste für dateparser-Kompatibilität

~~„nächsten", „kommenden", „letzten", „vorigen", „übernächsten" → entfernen, aber „übernächst" wird als Flag gemerkt für +7 Tage Offset.~~

~~**Hinweis:** Die Präfixe werden für den Vektor-Modus (Abschnitt 10) **vor** diesem Block ausgelesen. Block 9 entfernt sie danach wie gehabt.~~

→ **Ueberholt, 31.07.2026.** Die Praefixe stehen hier nicht mehr. Sie hat die **Marker-Stufe** (§2a) gelesen und — soweit noetig — entfernt, bevor dieser Text entstand; der +7-Versatz steht im Befund statt in einem Flag.

Der Block traegt jetzt nur noch eine Regel: **„Woche" faellt, wenn ein Wochentag folgt.** In „naechste Woche Dienstag" ist es nach der Markerentfernung redundant, sonst nicht. Die Regel loeschte bis zum 31.07.2026 **jedes** „Woche " mit Folgetext und war damit fuer einen Kontext gebaut, aber kontextfrei wirksam — gemessen: „in einer Woche um 14 Uhr" wurde zu „in einer 14:00".

### Block 9b: Stunde nach „um" ohne „Uhr"

„übermorgen um 9" → „2026-03-27 9:00", „Donnerstag um 14" → „Donnerstag 14:00", „abends um 8" → „20:00" (`_read_hour_after_um`, im Code Block 8b, seit 15.09.2026). **Die Stunde wird gelesen wie mit „Uhr"** — „um 3" ist 03:00 wie „um 3 Uhr"; welche Tageshälfte ohne Tageszeit gemeint ist, entscheidet der Block nicht (§8, Zwölf-Stunden-Deutung).

**Der Fall im Betrieb, 14.09.2026:** Ein Terminauftrag aus Tageswort, „um" und nackter Stunde kam wörtlich an. Die Normalisierung ließ „um H" stehen, Pfad 3 bekam den Text und lieferte den Folgetag **zur aktuellen Uhrzeit**; ohne Tagesangabe wurde die Zahl zum Tag des Monats, auch neben einem Wochentag — „Donnerstag um 14" ergab den 14., in der Vergangenheit.

| Bleibt stehen | Warum |
|---|---|
| „um 10 Minuten", „um 10 Prozent", „um 3 Grad" | Hinter der Zahl steht eine Menge (`_QUANTITIES_AFTER_UM`) |
| „um 15. Mai", „um 15 Aug" | Hinter der Zahl steht ein Monat (`_MONTHS_AFTER_UM`) — die Zahl ist ein Tag |
| „um 10.30", „um 10:30" | Andere Form; Punkt oder Doppelpunkt mit Ziffer dahinter |
| „um 24", „um 25" | Keine Stunde der Spanne 0..23 |

Ein Satzpunkt direkt hinter der Stunde („um 10.") und ein „rum"/„herum" gehören zum Treffer. **Die Ersetzung zählt sich selbst nach**, mit einem anderen Muster als dem, das die Treffer fand: Das Ergebnis muss genau so viele `H:MM` mehr tragen, wie es Treffer gab — sonst `_HourReadingError`. Dieselbe Nachzählung gilt für *Vor Block 0*.

**Die Tageszeit eines Treffers wird über den Tabellenschlüssel aufgelöst, mit derselben Faltung, mit der das Muster traf** (`_daypart_key`). `re.IGNORECASE` lässt `ı` (U+0131) und `İ` (U+0130) ein `i` treffen, `ſ` (U+017F) ein `s`; `str.lower()` führt von dort nicht zum Schlüssel zurück. Bis zur zweiten Kontrolle am 15.09.2026 warf *„morgen um 3 nachmıttags"* deshalb `_HourReadingError` — die Ausnahme, die nur einen Programmfehler anzeigen soll.

### Block 10: Orphaned „um"

„um 14:00" → „14:00". Das „um" ist nach der Normalisierung überflüssig.

### Block 11: Tageszeit-Fallback

Wenn nach allen Transformationen keine Uhrzeit (`\d{1,2}:\d{2}`) im String steht, wird die in Block 0 gemerkte Fallback-Uhrzeit angehängt. „morgen früh" → „2026-03-26 06:00".

> **Fränkisch und Norddeutsch gleichberechtigt:** „dreiviertel acht" (7:45, fränkisch) und „viertel vor acht" (7:45, norddeutsch) werden beide korrekt erkannt. Kein Dialekt ist bevorzugt.

---

## 5. Stufe 4: 4-Pfade-Parsing

Vor den Pfaden wird die Referenz gesetzt. `dateparser` bekommt sie als `RELATIVE_BASE`, und dieses Feld muss naiv sein — ohne Zonenvermerk. Die Einstellung `TIMEZONE` sagt der Bibliothek zugleich, dass sie naive Zeiten als **Ortszeit** liest.

> **Die Referenz wird deshalb in die Ortszone gedreht, nicht ihres Vermerks beraubt.** Ein bloßes `.replace(tzinfo=None)` gäbe die UTC-Wanduhr als Ortszeit aus und verschöbe sie um den Zonenversatz — zwischen lokaler und UTC-Mitternacht über die Datumsgrenze hinweg. Genau so war es bis zum 31.07.2026, und „übermorgen" (Block 0b, Ortszeit) lag dann einen Tag neben „in zwei Tagen" (`RELATIVE_BASE`, UTC-Wanduhr).

Nach der Normalisierung versucht der Parser vier Pfade:

### Pfad 1 — Direkt-Parse

Regex-Match auf bekannte Formate:
- `YYYY-MM-DD HH:MM` → direkt als datetime
- `YYYY-MM-DD` → datetime mit 00:00
- `DD.MM.YYYY HH:MM` → datetime
- `DD.MM.YYYY` → datetime mit 00:00

Schnellster Pfad, kein dateparser nötig.

**Das Datum wird zusammengesetzt, nicht ueber `fromisoformat` gebaut.** Das Muster erlaubt eine **einstellige** Stunde, `datetime.fromisoformat` verlangt zwei. „morgen um 9 Uhr" normalisiert zu `2026-08-01 9:00` und riss damit bis zum 31.07.2026 eine unbehandelte `ValueError` bis zum Aufrufer hoch. Zweistellige Uhrzeiten kamen durch, einstellige stuerzten ab — deshalb sah es nie nach einem Muster aus.

### Pfad 1c — Nackte Uhrzeit

Besteht der normalisierte Ausdruck nur noch aus `HH:MM` — „halb drei", „um 15 Uhr", „morgens", „14 Uhr 30" —, wird der Tag **selbst gerechnet**: heute, wenn die Uhrzeit noch kommt, sonst der Nachbartag in der gefragten Richtung.

**Das ist ein Riegel gegen zwei Defekte in `dateparser` 1.4.1**, beide in `_correct_for_time_frame`, beide am 31.07.2026 instrumentiert gemessen:

| | Was |
|---|---|
| **A — der Uebertrag wird ueberschrieben** | Die Addition ist korrekt (`dateobj + timedelta(days=1)`, mit Uebertrag). Das direkt danach laufende `_correct_for_month` rechnet nicht, sondern **weist zu**: `replace(month=<Monat des Bezugsmoments>)`. Am Monatsletzten geht der Uebertrag damit verloren und der Tag 1 bleibt stehen — 31.07. + „02:30" ergibt den **01.07.** statt des 01.08. |
| **B — der Vergleich hinkt** | `self.now` ist naive Ortszeit, von `dateobj` wird der UTC-Versatz abgezogen. Jede Uhrzeit innerhalb der naechsten `utcoffset` Stunden gilt damit als vergangen und wandert auf morgen. Bei Europe/Berlin im Sommer liegt die Kante exakt bei Bezugszeit + 2h: „15:00", um 14:27 gesagt, ergibt **morgen**. |

**Defekt A trifft zwoelfmal im Jahr, dafuer mit 28 bis 31 Tagen Betrag; an Silvester ueberlebt das Jahr die Zuweisung und der Monat nicht — elf Monate, nicht zwoelf. Defekt B trifft jeden Tag** und beide Richtungen: Bei `past` bleibt ein Zeitpunkt in der Zukunft stehen. Der Plausibilitaets-Check (§6) faengt keinen von beiden, er verwirft erst ab zwei Jahren.

> **Der Riegel hat ein Ablaufdatum.** `tests/test_zeit_dateparser_riegel.py` prueft die Bibliothek direkt und haelt die heutigen Fehlwerte fest. Er ist gruen, solange die Defekte leben, und wird rot, sobald einer verschwindet — die Fehlermeldung sagt dann, was zu tun ist. Erst wenn **beide** weg sind, kann Pfad 1c entfallen.

### Pfad 2 — Split-Parse

Uhrzeit per Regex extrahieren (`\d{1,2}:\d{2}`), Rest als Datum-Teil an dateparser übergeben. Ergebnis kombinieren.

**Warum?** dateparser hat Schwierigkeiten mit kombinierten Ausdrücken wie „Donnerstag 14:00". Getrennt funktioniert beides zuverlässig.

### Pfad 3 — Fallback

Gesamter normalisierter String an `dateparser.parse()` mit deutschen Spracheinstellungen:
- `PREFER_DATES_FROM: "future"` (bei Mehrdeutigkeit Zukunft bevorzugen)
- `DATE_ORDER: "DMY"` (deutsch: Tag.Monat.Jahr)
- `TIMEZONE: "Europe/Berlin"`

**Letzter Fallback:** Wenn der normalisierte Text scheitert, wird der original korrigierte (aber nicht normalisierte) Text versucht — für den Fall, dass die Normalisierung dateparser verwirrt hat.

---

## 6. Stufe 5: Plausibilitäts-Check

| Prüfung | Schwellwert | Aktion |
|---------|-------------|--------|
| Vergangenheit | > 2 Jahre | Verwerfen + Warning-Log |
| Zukunft | > 5 Jahre | Verwerfen + Warning-Log |

Verhindert, dass halluzinierte oder falsch berechnete Daten in die Timeline gelangen.

> **Die Spanne ist weit, und das hat einen Preis.** Ein Ergebnis, das einen Monat in der Vergangenheit liegt, laeuft ohne ein Wort durch — genau so blieben die beiden `dateparser`-Defekte aus §5 unbemerkt. Der Check faengt die Halluzination, nicht den Rechenfehler.

---

## 7. Parameter

### 7.1 `zeit_parsen()` — Absolutes Parsing

| Parameter | Beschreibung |
|-----------|-------------|
| `text` | Der Zeitausdruck als String |
| `referenz` | Referenzzeitpunkt (Default: jetzt UTC) |
| `zukunft_bevorzugt` | Bei Mehrdeutigkeit Zukunft wählen (Default: True) |

**Return:** `datetime` (timezone-aware, lokale Zeit) oder `None`.

> **Verhaltensaenderung seit v10:** `zeit_parsen()` wertet die **Richtung selbst aus**. Bis dahin tat das nur `zeit_parsen_vektor()`, und wer die einfache Funktion rief, bekam einen rueckwaerts gerichteten Ausdruck vorwaerts aufgeloest. Betroffen, ohne angefasst worden zu sein: `agents/kzg/magnete.py` und `agents/timeline/suche.py`. `zukunft_bevorzugt` bleibt der Wunsch des Aufrufers — ein erkannter Rueckwaertsmarker schlaegt ihn.

### 7.2 `zeit_parsen_vektor()` — Vektor-Parsing (P8)

| Parameter | Beschreibung |
|-----------|-------------|
| `text` | Der Zeitausdruck als String |
| `referenz` | Referenzzeitpunkt (Default: jetzt UTC) |
| `zukunft_bevorzugt` | Bei Mehrdeutigkeit Zukunft wählen (Default: True) |

**Return:** `ZeitVektor` Dataclass (siehe Abschnitt 10).

---

## 8. Bekannte Limitationen

| Limitation | Beschreibung | Status |
|-----------|-------------|--------|
| ~~Tageszeit VOR Uhrzeit~~ | ~~„nachmittags um 3 Uhr" → Offset geht verloren~~ | ✅ Behoben 15.09.2026 — die Tageszeit wird als Wort gemerkt (§4 Block 0), Korpus `REG-023` |
| ~~Einzelne Ziffer ohne „Uhr"~~ | ~~„nachmittags um 3" → als Tag interpretiert~~ — im Betrieb getroffen am 14.09.2026: Tageswort, „um" und nackte Stunde → Uhrzeit nicht erkannt, Termin um die aktuelle Uhrzeit mit Genauigkeit Tag; die Stunde ohne Tageswort → ein vergangener Tag; mit „früh" dazwischen → kein Datum | ✅ Behoben 15.09.2026 — §4 Block 9b, Korpus `REG-024`, `REG-026`, `REG-027` |
| „zwanzig vor vier" | `_ZAHLWOERTER` enthält nur 1–12, nicht „zwanzig" | Spätere Iteration |
| „in 2 Stunden" | Funktioniert nur über dateparser (keine Normalisierung) | Spätere Iteration |
| **Zwoelf-Stunden-Deutung** | „halb drei", um 14 Uhr gesagt, ergibt 2:30 des naechsten Tages statt 14:30 desselben. Die Normalisierung bildet das Zahlwort auf die Stunde ab, ohne die Tageshaelfte zu waehlen. **Gilt seit dem 15.09.2026 auch für „um 3"** — so gelesen wie „um 3 Uhr" | offen, Korpus `REG-006`/`REG-008` |
| ~~**„3 nachmittags"**~~ | ~~Die Tageszeit-Extraktion nimmt „nachmittags" heraus und merkt sich 15:00; die „3" bleibt stehen und wird als **Tag** gelesen. Ergebnis `3 15:00` → 03. des Monats~~ | ✅ Behoben 15.09.2026 — §4 *Vor Block 0*, Korpus `REG-011` |
| **Die Nacht verschiebt nicht** | „nachts um 11" und „11 Uhr nachts" ergeben 11:00 — `nachts` trägt den Versatz 0, richtig nur für die frühen Stunden. **Und die Mitternacht steht nur in zwei von drei Lesern:** „12 Uhr nachts" und „nachts um 12" → 00:00, „zwölf Uhr nachts" (Block 1) → 12:00 | offen, Fundliste 15.09.2026 |
| **Punkt als Trenner** | „übermorgen um 9.00 Uhr" → Block 2 liest „00 Uhr" als Stunde, der Text wird `9.0:00`, Pfad 3 liefert den Tag zur Sprechzeit. **Im Betrieb am 14.09.2026** die erste von drei Formulierungen desselben Termins | offen, Fundliste 15.09.2026 |
| **Stunde über 23, nackte Zahl** | „um 24", „um 25" und „Donnerstag 10" (ohne „um") werden weiter zum Tag des Monats | offen |
| **Tag des Monats ohne Zukunft** | „am 24." am 31.07. gesagt ergibt den 24.07.; ebenso „am 24. um 10" → 24.07. 10:00 | offen, Fundliste 15.09.2026 |
| **„und" wird „juni"** | Die Fuzzy-Korrektur (§3.1) zieht „und" auf Distanz 2 zum Monat: „um 10 und um 11" ergibt den 10. Juni, „morgen um 7 Uhr und um 9 Uhr" den 01.06. Ebenso „min" → „mai" | offen, Fundliste 25.08.2026 (Nachtrag) |
| **Ungültiger Kalendertag mit Uhrzeit** | „am 31.09. um 10", „30.02. um 9" → `ValueError` aus Pfad 1b, das Datum wird ungeprüft gebaut; mit „Uhr" schon vor dem 15.09.2026, seither auch ohne. Pfad 2 ebenso bei einer Minute über 59 | offen, Fundliste 15.09.2026 |
| **Leerzeichen hinter „Uhr"** | Block 2 nimmt es mit: „morgen um 1 Uhr Termin" → `1:00Termin` → kein Datum | offen, Fundliste 15.09.2026 |
| **Einzahl als Nomen** | „einen Vormittag", „jeden Vormittag" setzen `uhrzeit_erkannt` — wie „Abend" seit jeher. Das Datum bleibt leer; im Bestand 2 von 1494 Nutzereingaben | benannt |
| ~~Vektor-Modus~~ | ~~„Verschiebe auf Freitag" → Uhrzeit geht verloren~~ | ✅ Behoben (Chat 14, P8) |

**Die Zeilen mit Korpuskennung sind im Korpus als Faelle hinterlegt.** Eine bekannte Luecke, die niemand aufschreibt, wird irgendwann als neuer Bug wiederentdeckt. **Der Umkehrfall ist ungesichert:** Eine geschlossene Lücke (`ab_phase: null`) meldet der Läufer nicht — `ZON-009` besteht seit mindestens dem 15.09.2026 und steht weiter als unlösbar im Korpus (Fundliste 15.09.2026).

> **Die Zwoelf-Stunden-Deutung lag unter einem anderen Defekt.** Bis zum 31.07.2026 ergab „halb drei" den 1. des Monats (§5, Defekt A); dass zusaetzlich die **Stunde** falsch ist, wurde erst sichtbar, nachdem der Tag stimmte.

---

## 9. Evolution

| Version | Tests | Kernänderung |
|---------|-------|-------------|
| v1 | 20/26 | dateparser + Fuzzy-Korrektur |
| v2 | 22/26 | „am" entfernen, relative Tage als ISO |
| v3 | 40/47 | 3-Pfade-System (Direkt, Split, Fallback) |
| v4 | 47/47 | Tageszeit-Extraktion + Fallback statt Inline-Ersetzung |
| v5 | 47/47 | Schutzliste gegen falsche Fuzzy-Korrekturen |
| v6 | 47/47 | Vektor-Modus: `ZeitVektor` Dataclass, Referenz-Modus, Zwei-Phasen-Parsing (Chat 14) |
| v7 | — | Der erkannte Referenz-Modus steuert die Auflösung. Er wurde bis dahin berechnet, zurückgegeben und **nicht übergeben**; „letzte fünf Wochen" war als rückwärts erkannt und löste vorwärts auf. `seit` in die Richtungsliste (Chat 119) |
| v8 | 31 | Drei Befunde an einem Tag (Chat 120, siehe unten) |
| v9 | 31 | `_heute_lokal()` statt `date.today()` — Block 0b las die **System**zone, nicht `TIMEZONE`. Praefixe aus Staemmen erzeugt statt als Literale in den Regexen. „Woche" faellt nur noch vor einem Wochentag |
| v10 | 46 | **Marker-Stufe** (§2a): Die Richtung wird in einem Durchlauf gelesen statt aus zwei Textzustaenden rekonstruiert. `zeit_parsen()` wertet die Richtung jetzt selbst aus — das tat bis dahin nur `zeit_parsen_vektor()` |
| v11 | 58 | **Pfad 1c** fuer nackte Uhrzeiten, als Riegel gegen zwei `dateparser`-Defekte (§5). Pfad 1 setzt das ISO-Datum zusammen, statt es ueber `fromisoformat` zu bauen — eine einstellige Stunde stuerzte bis dahin ab |
| v12 | 105 | **Die Stunde ohne „Uhr" ist eine Uhrzeit** (15.09.2026): nach „um" (Block 9b), vor einer Tageszeit (*Vor Block 0*, ersetzt Block 3), und die vorangestellte Tageszeit verschiebt wie die nachgestellte. Anlass war der erste ausdrückliche Terminauftrag im Betrieb. Korpus 50 → 56 erfüllt |

**Die Tests sind mit v8 neu gezählt.** Die 47 der frühen Versionen stammen aus einer Suite, die es in dieser Form nicht mehr gibt.

**Seit v11 gibt es zwei Messgeraete, nicht eines.** Die 58 Tests pruefen den Parser gegen Zeugen; der **Korpus** (`tests/korpus/zeitausdruecke.yaml`, 89 Faelle) ist daneben eine Spezifikation: Jeder Fall traegt die Stufe, ab der er gruen sein muss, und der Laeufer unterscheidet „noch nicht gebaut" von „kaputtgemacht". Stand 31.07.2026: **49 erfuellt, 4 Regressionen, 31 offen, 5 dokumentierte Luecken.**

### Was v8 gefunden hat

Alle drei kamen aus einer einzigen Frage: ob der Parser Zahlwörter normalisiert. Er tut es nicht — die Wort-zu-Zahl-Tabelle dient nur Uhrzeit-Konstruktionen, Dauern versteht `dateparser` selbst.

1. **Zwei Uhren im selben Aufruf.** Die deiktischen Tageswörter rechneten lokal, die Referenz für Dauern kam als UTC-Wanduhr an. Zwischen den Mitternachten lagen „übermorgen" und „in zwei Tagen" einen Tag auseinander (§5).
2. **Jedes Datum im März fiel durch — verursacht von der Tippfehler-Korrektur.** `_MONATE` führte nur „maerz"; „März" galt damit als unbekannt, wurde auf Distanz 2 zur ASCII-Form gezogen, und `dateparser` liefert dafür nichts (§3.0).
3. **„bereits" und „schon" erreichten den Parser nie.** Die Salienz-Extraktion verwarf sie, weil ihre Beispiele keine Richtungspräposition trugen (§10.4).

**Die Reihenfolge war entscheidend.** Der Wortschatz des Parsers wurde erst erweitert, **nachdem** gemessen war, dass die Extraktion die Wörter überhaupt durchlässt — vorher wäre es Arbeit an einem Weg gewesen, den nichts befährt.

→ Vollständige Geschichte: novaberg-tool-timeparser_l_evolution.md

---

## 10. Vektor-Modus (P8)

### 10.1 Problem

`zeit_parsen("Freitag")` liefert ein absolutes Datum mit 00:00. Bei Timeline-Updates geht die Uhrzeit des bestehenden Termins verloren. Ebenso fehlt die Möglichkeit, nur die Uhrzeit zu ändern und den Tag beizubehalten. Zusätzlich wird bei „Verschiebe auf Freitag" der nächste Freitag ab *heute* gewählt, nicht ab dem bestehenden Termin.

### 10.2 Lösung: ZeitVektor

Neue Funktion `zeit_parsen_vektor()` und Dataclass `ZeitVektor`:

```python
@dataclass
class ZeitVektor:
    datum: Optional[datetime]
    tag_erkannt: bool        # Wochentag, relatives Wort oder konkretes Datum im Text
    uhrzeit_erkannt: bool    # HH:MM nach Normalisierung vorhanden
    referenz_modus: str      # "absolut" | "relativ" | "relativ_rueckwaerts"
```

`zeit_parsen_vektor()` ruft intern `zeit_parsen()` auf — keine Code-Duplikation. Alle bestehenden Aufrufer von `zeit_parsen()` funktionieren unverändert weiter.

### 10.3 Komponenten-Erkennung

| User sagt | tag_erkannt | uhrzeit_erkannt | Verhalten im TimelineManager |
|-----------|------------|----------------|------------------------------|
| „Freitag" | ✅ | ❌ | Tag → neu, Uhrzeit → vom alten Termin |
| „15 Uhr" | ❌ | ✅ | Tag → vom alten Termin, Uhrzeit → neu |
| „Freitag um 10 Uhr" | ✅ | ✅ | Komplett neu |
| „morgen früh" | ✅ | ✅ | Komplett neu („früh" = 06:00) |

**Uhrzeit-Erkennung:** Prüft ob nach der Normalisierung ein `HH:MM`-Pattern im String steht. Die Normalisierung wandelt alle Uhrzeitformen („15 Uhr", „halb drei", „dreiviertel acht") in dieses Format um — ein einzelner Regex-Check genügt.

**Tag-Erkennung:** Prüft ob im fuzzy-korrigierten Text ein Wochentag, ein relatives Wort (heute/morgen/übermorgen) oder ein konkretes Datum (DD.MM. oder YYYY-MM-DD) steht.

### 10.4 Referenz-Modus

Bei Timeline-Updates bestimmt der Referenz-Modus, von welchem Datum aus „Freitag" berechnet wird.

~~Die Präfix-Erkennung findet auf dem fuzzy-korrigierten Text statt — **vor** Block 9 der Normalisierung, der die Präfixe entfernt. Die Information wird gemerkt, bevor sie weggeworfen wird.~~ → **Ueberholt, 31.07.2026:** Es gibt keinen zweiten Durchlauf mehr. Die **Marker-Stufe** (§2a) liest die Richtung einmal, und `MarkerBefund.als_referenz_modus()` uebersetzt sie in dieses Feld. Die Tabelle unten beschreibt damit die Wirkung der Regeln `M-01` bis `M-09`, nicht mehr einen eigenen Regex-Pass.

| Präfix | referenz_modus | TimelineManager nutzt als Referenz |
|--------|---------------|-----------------------------------|
| „diesen" | `absolut` | `datetime.now()` (heute) |
| „nächsten", „kommenden", kein Präfix | `relativ` | `alter_termin["event_time"]` |
| „letzten", „vorigen", „vergangenen", „seit" | `relativ_rueckwaerts` | `alter_termin["event_time"]` + `zukunft_bevorzugt=False` |
| „bereits"/„schon" **+ nackte Dauer** | `relativ_rueckwaerts` | dito |

**`vor` steht bewusst nicht in der Liste.** Es kommt auch in Uhrzeiten vor („zehn vor acht"), und dort wäre eine Rückwärts-Auflösung falsch — gemessen: mit `vor` in der Liste löst „zehn vor acht" auf einen Zeitpunkt am selben Tag auf, der längst vorbei ist, statt auf den nächsten Termin. Rückwärts funktioniert es trotzdem, weil `dateparser` das Wort selbst versteht.

**„bereits" und „schon" nur vor einer nackten Dauer.** „Das dauert bereits zwei Wochen" meint den Beginn vor zwei Wochen. Aber beide Wörter sind häufiger Verstärkungspartikel als Richtungswort, und dann zeigen sie nach vorn. Eine Regel auf das bloße Wort löste „schon am Freitag" auf den vergangenen Freitag auf und „bereits nächsten Montag" auf den vergangenen Montag — aus Ausdrücken, die vorher gar nicht parsten, wurden damit welche, die falsch parsen. Deshalb muss unmittelbar eine Zahl und eine Zeiteinheit folgen.

> **Die Richtung muss ankommen, um wirken zu können.** Sie steht im Rohausdruck, den die Salienz-Extraktion bildet (`prompts/default/salienz.dimensionen.txt`). Bis zum 31.07.2026 verwarf diese Anweisung „bereits" und „schon" — ihre sechs Beispiele trugen keine Richtungspräposition, und das Modell normalisierte entsprechend. Der beste Wortschatz im Parser nützt nichts, wenn das Wort ihn nie erreicht.

### 10.5 Zwei-Phasen-Parsing im TimelineManager

1. **Phase 1:** `zeit_parsen_vektor(text)` mit Default-Referenz (jetzt) → erkennt `referenz_modus` und Komponenten
2. **TimelineManager** wählt die richtige Referenz basierend auf `referenz_modus`
3. **Phase 2:** `zeit_parsen_vektor(text, referenz=alte_zeit)` mit korrekter Referenz
4. **Kombination:** Erkannte Teile (Tag/Uhrzeit) mit altem Termin zusammenführen

### 10.6 Dateien

Wer den Parser benutzt, gemessen am 31.07.2026:

| Datei | Rolle |
|-------|-------|
| `utils/zeitparser.py` | Das Modul selbst — Umschrift, Fuzzy, zwölf Normalisierungsblöcke, drei Pfade, Richtung, Plausibilität |
| `agents/timeline/crud.py` | Anlegen und Verschieben. **Der einzige Aufrufer, der eine eigene Referenz übergibt** — die Zeit des bestehenden Termins |
| `agents/timeline/suche.py` | Terminsuche, über `zeit_parsen` |
| `agents/kzg/magnete.py` | Legt aus `zeitausdruck_roh` die Gedächtnis-Anker an. Hier entstand der Anker fünf Wochen in der Zukunft |

Davor liegt, was den Rohausdruck bildet — und was er weglässt, kann der Parser nicht wiederherstellen:

| Datei | Rolle |
|-------|-------|
| `prompts/default/salienz.dimensionen.txt` | Die Anweisung, die `zeitausdruck_roh` erzeugt |
| `graph/nodes/salience.py` | Setzt den Prompt zusammen, legt das Ergebnis in den State |

*(Der frühere Eintrag `plugins/timeline_manager/manager.py` ist überholt — die Datei importiert den Parser nicht mehr; der Update-Pfad liegt seit dem Agenten-Umbau in `agents/timeline/crud.py`.)*

→ Lesson: novaberg-tool-timeparser_l_vektor.md

---

→ Timeline (nutzt Zeitparser): novaberg-agent-timeline.md
→ Salienz (liefert Zeitausdruck): novaberg-node-salience.md
→ Lesson Zeitparser-Evolution: novaberg-tool-timeparser_l_evolution.md
→ Lesson Vektor-Modus: novaberg-tool-timeparser_l_vektor.md
→ Lesson Timezone: novaberg-tool-timeparser_l_timezone.md

---

## Eine Tür für die gesamte Zeitauflösung

Die Bibliothek `dateparser` wird ausschließlich aus `utils/zeitparser.py` gerufen (Grep über `server/`, Positivkontrolle auf `zeit_parsen` = vier Dateien). Damit liegt die gesamte Zeitauflösung an **einer** Tür — das ist heute ein Vorteil und zugleich der Grund, warum ein Defekt der Bibliothek jeden Aufrufer gleichzeitig trifft. Kein Befund, eine Eigenschaft, die bei der nächsten Fremddefekt-Frage bekannt sein sollte.
