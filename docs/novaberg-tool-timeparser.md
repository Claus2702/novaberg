# Novaberg — Tool: Zeitparser

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Technik Zeitparser (Natürlichsprachliche Zeitauflösung)
**Stand:** 31. Juli 2026, Chat 120 (Zonen-Grenze, andauernde Dauern, Umlaut-Umschrift)
**Pfad:** novaberg/docs/novaberg-tool-timeparser.md
**Quellen:** nova-02-t-c.md
**Datei:** `utils/zeitparser.py`
**Tests:** 31 in `tests/test_zeit_richtung.py` (20) und `tests/test_zeit_umlaute.py` (11)

---

## 1. Aufgabe

Der Zeitparser löst natürlichsprachliche deutsche Zeitausdrücke in `datetime`-Objekte auf. Er ist die Brücke zwischen dem LLM (das den Zeitausdruck als String extrahiert) und der Datenbank (die ein exaktes Datum braucht).

> **Grundprinzip:** Das LLM extrahiert den Zeitausdruck als wörtlichen String — „am Donnerstag um 14 Uhr", „übermorgen früh", „dreiviertel acht". Python löst ihn deterministisch auf. Kein LLM rechnet Kalender.

→ Warum dieses Prinzip: novaberg-tool-timeparser_l_evolution.md

---

## 2. Dreistufige Architektur

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
    ├── Stufe 2: Normalisierung (12 Blöcke)
    │     "am Donnerstag um 14 Uhr" → "Donnerstag 14:00"
    │
    ├── Stufe 3: 3-Pfade-Parsing
    │     Pfad 1 (Direkt): ISO-Datum? → nein
    │     Pfad 2 (Split):  Uhrzeit raus, Datum separat → "Donnerstag" + 14:00 → ✅
    │     Pfad 3 (Fallback): dateparser komplett → (nicht nötig)
    │
    └── Stufe 4: Plausibilitäts-Check
          > 2 Jahre Vergangenheit? → verwerfen
          > 5 Jahre Zukunft? → verwerfen
          → 2026-03-27T14:00:00+01:00 ✅
```

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

---

## 4. Stufe 2: Normalisierung (12 Blöcke)

Die Normalisierung transformiert deutsche Zeitausdrücke in ein Format, das `dateparser` verarbeiten kann. Konzeptionell 12 Blöcke in fester Reihenfolge. Im Code (`_text_normalisieren()` in `utils/zeitparser.py`) sind die Blöcke 0–9 nummeriert (mit Sub-Blöcken 0b, 0c, 1b); „Halb" ist im Code als Sub-Regex innerhalb des Viertel-Blocks implementiert, nicht als eigener Block 5:

### Block 0: Tageszeit extrahieren

Tageszeit-Wörter werden extrahiert und als Fallback-Uhrzeit gemerkt — nur eingefügt wenn am Ende keine Uhrzeit im String steht.

| Tageszeit | Fallback-Uhrzeit |
|-----------|-----------------|
| `früh` | 06:00 |
| `morgens` | 08:00 |
| `vormittags` | 10:00 |
| `mittags` | 12:00 |
| `nachmittags` | 15:00 |
| `abends` | 18:00 |
| `nachts` | 22:00 |

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

**Gerechnet wird in der Ortszone**, mit `date.today()`. Das folgt der Grenzregel aus `novaberg-tool-timeparser_l_timezone.md` §3: Das Repository ist die einzige Stelle, die UTC kennt; alles davor arbeitet lokal.

> **Beide Wege müssen dieselbe Uhr benutzen.** Die Referenz für Dauern wird deshalb in die Ortszone **gedreht**, nicht ihres Zonenvermerks beraubt (§5). Bis zum 31.07.2026 geschah das Zweite — damit lagen „übermorgen" und „in zwei Tagen" in den Stunden zwischen lokaler und UTC-Mitternacht **einen Tag auseinander**.

### Block 0c: Deutsches Datum ohne Jahr

„01.07." oder „15.04." → „01.07.2026" oder „15.04.2026". Aktuelles Jahr ergänzen.

### Block 1: Zahlwort-Uhrzeiten

„drei Uhr nachmittags" → „15:00". Zahlwörter (`_ZAHLWOERTER`: eins bis zwölf) werden aufgelöst, optionaler Tageszeit-Suffix addiert den 12-Stunden-Offset.

### Block 2: Numerische Uhrzeiten

„14 Uhr 30" → „14:30". „3 Uhr nachmittags" → „15:00".

### Block 3: Standalone Tageszeit

„3 nachmittags" → „15:00" (Zahl + Tageszeit ohne „Uhr").

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

### Block 9: Relative Präfixe

„nächsten", „kommenden", „letzten", „vorigen", „übernächsten" → entfernen, aber „übernächst" wird als Flag gemerkt für +7 Tage Offset.

**Hinweis:** Die Präfixe werden für den Vektor-Modus (Abschnitt 10) **vor** diesem Block ausgelesen. Block 9 entfernt sie danach wie gehabt.

### Block 10: Orphaned „um"

„um 14:00" → „14:00". Das „um" ist nach der Normalisierung überflüssig.

### Block 11: Tageszeit-Fallback

Wenn nach allen Transformationen keine Uhrzeit (`\d{1,2}:\d{2}`) im String steht, wird die in Block 0 gemerkte Fallback-Uhrzeit angehängt. „morgen früh" → „2026-03-26 06:00".

> **Fränkisch und Norddeutsch gleichberechtigt:** „dreiviertel acht" (7:45, fränkisch) und „viertel vor acht" (7:45, norddeutsch) werden beide korrekt erkannt. Kein Dialekt ist bevorzugt.

---

## 5. Stufe 3: 3-Pfade-Parsing

Vor den Pfaden wird die Referenz gesetzt. `dateparser` bekommt sie als `RELATIVE_BASE`, und dieses Feld muss naiv sein — ohne Zonenvermerk. Die Einstellung `TIMEZONE` sagt der Bibliothek zugleich, dass sie naive Zeiten als **Ortszeit** liest.

> **Die Referenz wird deshalb in die Ortszone gedreht, nicht ihres Vermerks beraubt.** Ein bloßes `.replace(tzinfo=None)` gäbe die UTC-Wanduhr als Ortszeit aus und verschöbe sie um den Zonenversatz — zwischen lokaler und UTC-Mitternacht über die Datumsgrenze hinweg. Genau so war es bis zum 31.07.2026, und „übermorgen" (Block 0b, Ortszeit) lag dann einen Tag neben „in zwei Tagen" (`RELATIVE_BASE`, UTC-Wanduhr).

Nach der Normalisierung versucht der Parser drei Pfade:

### Pfad 1 — Direkt-Parse

Regex-Match auf bekannte Formate:
- `YYYY-MM-DD HH:MM` → direkt als datetime
- `YYYY-MM-DD` → datetime mit 00:00
- `DD.MM.YYYY HH:MM` → datetime
- `DD.MM.YYYY` → datetime mit 00:00

Schnellster Pfad, kein dateparser nötig.

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

## 6. Stufe 4: Plausibilitäts-Check

| Prüfung | Schwellwert | Aktion |
|---------|-------------|--------|
| Vergangenheit | > 2 Jahre | Verwerfen + Warning-Log |
| Zukunft | > 5 Jahre | Verwerfen + Warning-Log |

Verhindert, dass halluzinierte oder falsch berechnete Daten in die Timeline gelangen.

---

## 7. Parameter

### 7.1 `zeit_parsen()` — Absolutes Parsing

| Parameter | Beschreibung |
|-----------|-------------|
| `text` | Der Zeitausdruck als String |
| `referenz` | Referenzzeitpunkt (Default: jetzt UTC) |
| `zukunft_bevorzugt` | Bei Mehrdeutigkeit Zukunft wählen (Default: True) |

**Return:** `datetime` (timezone-aware, lokale Zeit) oder `None`.

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
| Tageszeit VOR Uhrzeit | „nachmittags um 3 Uhr" → Offset geht verloren | Spätere Iteration |
| Einzelne Ziffer ohne „Uhr" | „nachmittags um 3" → als Tag interpretiert | Spätere Iteration |
| „zwanzig vor vier" | `_ZAHLWOERTER` enthält nur 1–12, nicht „zwanzig" | Spätere Iteration |
| „in 2 Stunden" | Funktioniert nur über dateparser (keine Normalisierung) | Spätere Iteration |
| ~~Vektor-Modus~~ | ~~„Verschiebe auf Freitag" → Uhrzeit geht verloren~~ | ✅ Behoben (Chat 14, P8) |

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

**Die Tests sind mit v8 neu gezählt.** Die 47 der frühen Versionen stammen aus einer Suite, die es in dieser Form nicht mehr gibt; heute sind es 31 in zwei Dateien, die je einen Gegenstand haben — Richtung und Umlaute.

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

Bei Timeline-Updates bestimmt der Referenz-Modus, von welchem Datum aus „Freitag" berechnet wird. Die Präfix-Erkennung findet auf dem fuzzy-korrigierten Text statt — **vor** Block 9 der Normalisierung, der die Präfixe entfernt. Die Information wird gemerkt, bevor sie weggeworfen wird.

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
