# Novaberg — Tool: Zeitparser

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Technik Zeitparser (Natürlichsprachliche Zeitauflösung)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/novaberg-tool-timeparser.md
**Quellen:** nova-02-t-c.md
**Datei:** `utils/zeitparser.py`
**Tests:** 47/47 bestanden

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

## 3. Stufe 1: Fuzzy-Korrektur

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
| „letzten", „vorigen" | `relativ_rueckwaerts` | `alter_termin["event_time"]` + `zukunft_bevorzugt=False` |

### 10.5 Zwei-Phasen-Parsing im TimelineManager

1. **Phase 1:** `zeit_parsen_vektor(text)` mit Default-Referenz (jetzt) → erkennt `referenz_modus` und Komponenten
2. **TimelineManager** wählt die richtige Referenz basierend auf `referenz_modus`
3. **Phase 2:** `zeit_parsen_vektor(text, referenz=alte_zeit)` mit korrekter Referenz
4. **Kombination:** Erkannte Teile (Tag/Uhrzeit) mit altem Termin zusammenführen

### 10.6 Dateien

| Datei | Änderung |
|-------|---------|
| `utils/zeitparser.py` | `ZeitVektor` Dataclass, `zeit_parsen_vektor()` |
| `plugins/timeline_manager/manager.py` | UPDATE-Block: Zwei-Phasen-Parsing, Vektor-Kombination |

→ Lesson: novaberg-tool-timeparser_l_vektor.md

---

→ Timeline (nutzt Zeitparser): novaberg-agent-timeline.md
→ Salienz (liefert Zeitausdruck): novaberg-node-salience.md
→ Lesson Zeitparser-Evolution: novaberg-tool-timeparser_l_evolution.md
→ Lesson Vektor-Modus: novaberg-tool-timeparser_l_vektor.md
→ Lesson Timezone: novaberg-tool-timeparser_l_timezone.md
