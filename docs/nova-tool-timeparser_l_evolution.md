# 02_L_b — Lesson: Zeitparser-Evolution

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Vom LLM-Halluzinator zum 47/47-Parser in 5 Iterationen
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-tool-timeparser_l_evolution.md
**Ursprung:** nova-02-l-b.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 10 (23. März 2026)
**Betrifft:** Timeline-System, Salienz-Prompt, Zeitparser (`02_T_c`)

---

## 1. Symptom

Der erste Versuch, Termine aus natürlicher Sprache zu extrahieren: Die Salienz erkannte „Zahnarzt am Donnerstag um 14 Uhr" als `temporal_fact` und schrieb `"date": "2024-06-13"` in die Timeline. Das Datum war komplett halluziniert — 2024 statt 2026, Juni statt März, der 13. statt Donnerstag.

---

## 2. Ursache: LLM rechnet nicht

Der Salienz-Prompt enthielt `"date": "YYYY-MM-DD"` als Platzhalter. Das LLM interpretierte das als Aufforderung, ein konkretes Datum zu berechnen — und halluzinierte. LLMs können keine Kalenderarithmetik: „nächsten Donnerstag" → welches Datum ist das? Das LLM rät.

---

## 3. Die fünf Iterationen

### v1 — dateparser + Fuzzy-Korrektur (20/26 Tests)

Erster Fix: `"date"` im Salienz-Prompt von `"YYYY-MM-DD"` auf wörtlichen Zeitausdruck geändert. Das LLM liefert jetzt `"am Donnerstag um 14 Uhr"` statt ein Datum. Python-basierter `dateparser` übernimmt die Konvertierung. Fuzzy-Korrektur für deutsche Eigenheiten.

**Probleme:** „am Montag" scheiterte (dateparser braucht das „am" nicht), relative Tage funktionierten nicht als ISO, DD.MM. ohne Jahr wurde falsch interpretiert.

### v2 — Bereinigung (22/26 Tests)

„am" vor Wochentagen entfernen, relative Tage direkt als ISO-Datum berechnen, DD.MM. ohne Jahr → aktuelles Jahr ergänzen.

### v3 — 3-Pfade-System (40/47 Tests)

Fundamentaler Umbau: Drei Parser-Pfade statt einem:

1. **Direkt-Parse:** Versuch den gesamten Ausdruck zu parsen
2. **Split-Parse:** Datum und Uhrzeit getrennt erkennen und kombinieren
3. **Fallback:** dateparser als letzter Versuch

47 Testfälle statt 26 — umfangreiche Abdeckung deutscher Zeitausdrücke.

### v4 — Tageszeit-Fix (47/47 Tests)

Problem: Tageszeit-Angaben („morgens", „nachmittags") als Inline-Ersetzung funktionierten nicht zuverlässig. Lösung: Extraktion + Fallback statt Inline-Ersetzung.

### v5 — Schutzliste (47/47 + stabil)

`_GESCHUETZTE_WOERTER` verhindert falsche Fuzzy-Korrekturen: „morgens" → „morgen" (falsch, Tageszeit ≠ relatives Datum), „acht" → „nachts" (falsch, Zahl ≠ Tageszeit).

**12 Normalisierungsblöcke,** fränkisch + norddeutsch gleichberechtigt: „dreiviertel acht" (7:45) und „viertel vor acht" (7:45) werden beide korrekt erkannt.

---

## 4. Was wir daraus gelernt haben

### Python ist deterministisch, LLMs sind es nicht

> **Kernprinzip:** Deterministische Operationen gehören in Python, nicht ins LLM. Das LLM liefert den natürlichsprachlichen Zeitausdruck (das kann es gut). Python berechnet das korrekte Datum (das kann Python besser). Die Kombination ist robuster als jeder Einzelansatz.

Das ist kein Zeitparser-spezifischer Befund. Es ist ein Architekturprinzip, das für alle berechenbaren Aufgaben gilt: Ebbinghaus-Decay, Emotions-Vektoren, Stilanalyse, Salienz-Schwellwerte.

### 5 Iterationen sind normal

Der Zeitparser ging durch 5 Versionen in einer Nacht. Jede Version löste neue Probleme und deckte neue Edge Cases auf. Das ist kein Zeichen schlechter Planung — es ist die Realität natürlichsprachlicher Verarbeitung. Deutsche Zeitausdrücke sind ausgesprochen vielfältig: „übermorgen früh", „am dritten Mai", „dreiviertel acht", „in zwei Wochen Dienstag". Kein erster Entwurf deckt alle Fälle ab.

### Tests als Treiber

Die Testfälle wuchsen von 26 auf 47. Jeder neue Testfall kam aus einem realen Fehler. Die Tests waren nicht nachgelagertes QA — sie waren der Motor der Entwicklung.

---

## 5. Bekannte Limitationen

Für eine spätere Iteration dokumentiert:

| Limitation | Beschreibung |
|-----------|-------------|
| Tageszeit VOR Uhrzeit | „nachmittags um 3 Uhr" → Offset geht verloren |
| Einzelne Ziffer ohne „Uhr" | „nachmittags um 3" → als Tag interpretiert |
| „zwanzig vor vier" | `_ZAHLWOERTER` enthält nur 1–12, nicht „zwanzig" |
| „in 2 Stunden" | Funktioniert nur über dateparser (keine Normalisierung) |
| ~~Vektor-Modus (P8)~~ | ~~„Verschiebe auf Freitag" → Uhrzeit geht verloren.~~ ✅ Behoben in Chat 14: `ZeitVektor` Dataclass + Referenz-Modus. → `02_T_c` Abschnitt 10, `02_L_e` |

---

→ Zeitparser-Technik: `02_T_c`
→ Salienz (liefert Zeitausdruck): `01_M_g`
→ Timeline-Modul: `02_M_e`
