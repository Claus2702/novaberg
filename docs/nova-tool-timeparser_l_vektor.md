# 02_L_e — Lesson: Vektor-Modus Zeitparser

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Absolutes Parsing verliert Kontext bei Verschiebungen
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-tool-timeparser_l_vektor.md
**Ursprung:** nova-02-l-e.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 11 (24. März 2026, als P8 dokumentiert)
**Behoben:** Chat 14 (26. März 2026)
**Betrifft:** Zeitparser (`02_T_c`), TimelineManager (`02_M_e`)

---

## 1. Symptom

„Verschiebe den Zahnarzt auf Freitag" — der Termin lag am Donnerstag, 02.04.2026, um 14:00 Uhr. Nach der Verschiebung: Freitag, 27.03.2026, 00:00 Uhr. Zwei Fehler gleichzeitig:

1. **Uhrzeit verloren:** 00:00 statt 14:00 — der User wollte nur den Tag ändern, nicht die Uhrzeit
2. **Falscher Freitag:** 27.03. (nächster Freitag ab heute) statt 03.04. (Freitag nach dem bestehenden Termin)

---

## 2. Ursache

Der Zeitparser (`zeit_parsen()`) war für absolutes Parsing gebaut: Text rein, Datum raus. Er wusste nicht, dass er im Kontext einer Verschiebung aufgerufen wurde. Zwei blinde Flecken:

**Keine Komponentenerkennung:** „Freitag" enthält nur einen Tag, keine Uhrzeit. Aber `zeit_parsen()` liefert immer ein vollständiges `datetime` — mit 00:00 als Default. Der TimelineManager konnte nicht unterscheiden, ob der User „Freitag 00:00" meinte oder nur den Tag ohne Uhrzeitangabe.

**Falsche Referenz:** `zeit_parsen()` nutzte `datetime.now()` als Referenz. „Freitag" wurde als nächster Freitag ab *heute* interpretiert. Im Kontext einer Verschiebung meint der User aber den Freitag nach dem *bestehenden Termin*.

---

## 3. Lösung: Drei Konzepte

### 3.1 Komponentenerkennung (Tag/Uhrzeit)

Neue Funktion `zeit_parsen_vektor()` und Dataclass `ZeitVektor`. Nach der Normalisierung prüft der Parser, *welche* Komponenten im Text erkannt wurden:

- **Uhrzeit erkannt:** Ist nach der Normalisierung ein `HH:MM`-Pattern im String? (Die Normalisierung wandelt alle Formen — „15 Uhr", „halb drei", „dreiviertel acht" — in dieses Format um.)
- **Tag erkannt:** Steht im Text ein Wochentag, ein relatives Wort (heute/morgen) oder ein konkretes Datum?

Der TimelineManager kombiniert dann nur die erkannten Teile mit dem bestehenden Termin. Nicht erkannte Teile werden vom alten Termin übernommen.

### 3.2 Referenz-Modus (Präfix-Erkennung)

Die relative Präfixe („nächsten", „diesen", „letzten") bestimmen, von welchem Datum aus gerechnet wird:

| Präfix | Modus | Referenz |
|--------|-------|---------|
| „diesen Freitag" | `absolut` | heute |
| „Freitag" / „nächsten Freitag" | `relativ` | alter Termin |
| „letzten Freitag" | `relativ_rueckwaerts` | alter Termin, Vergangenheit bevorzugt |

Die Erkennung passiert auf dem fuzzy-korrigierten Text — **vor** Block 9 der Normalisierung, der die Präfixe entfernt. Die Information wird gemerkt, bevor sie weggeworfen wird.

### 3.3 Zwei-Phasen-Parsing im TimelineManager

1. **Phase 1:** `zeit_parsen_vektor(text)` mit Default-Referenz (jetzt) — erkennt Komponenten und Referenz-Modus
2. **TimelineManager** wählt die richtige Referenz basierend auf dem Modus
3. **Phase 2:** `zeit_parsen_vektor(text, referenz=alte_zeit)` mit korrekter Referenz
4. **Kombination:** Erkannte Teile mit altem Termin zusammenführen

---

## 4. Was wir daraus gelernt haben

### Kontext verändert die Semantik

„Freitag" bedeutet etwas anderes je nach Kontext. Beim Anlegen eines Termins ist „nächster Freitag ab heute" korrekt. Beim Verschieben eines bestehenden Termins meint der User „den Freitag nach dem Termin". Ein Parser, der seinen Aufrufkontext nicht kennt, kann das nicht unterscheiden.

Die Lösung ist nicht, den Parser schlauer zu machen — sondern ihm den Kontext mitzugeben. Der TimelineManager kennt den alten Termin und wählt die richtige Referenz. Der Parser bleibt dumm, aber konfigurierbar.

### Zwei Fehler, eine Ursache

Verlorene Uhrzeit und falscher Referenztag waren auf den ersten Blick unabhängig. Tatsächlich hatten sie dieselbe Wurzel: Der Parser lieferte ein absolutes Ergebnis ohne Metadaten darüber, *was* er erkannt hatte. Beides löste sich durch dieselbe Abstraktion — den `ZeitVektor`.

### Additive Architektur

`zeit_parsen()` blieb unverändert. Alle bestehenden Aufrufer (CREATE, Salienz-Pfad, alter Pfad) funktionieren weiter. Die neue `zeit_parsen_vektor()` ist eine Erweiterung, kein Ersatz. Nur der UPDATE-Block im TimelineManager wurde angepasst. Null Breaking Changes bei einem Bug-Fix, der zwei Dateien und ein neues Konzept einführt.

### „Diesen" vs. „nächsten" — regionale Unschärfe bewusst umgangen

Im Deutschen sind „diesen Freitag" und „nächsten Freitag" regional verschieden belegt. Statt dieses linguistische Rabbit Hole zu lösen, haben wir eine pragmatische Regel: „diesen" = ab heute (innerhalb der laufenden Woche), alles andere = ab dem bestehenden Termin. Das deckt 95% der Fälle ab. Wer einen Termin rückwärts verschieben will, nennt ein konkretes Datum — das ist zumutbar.

---

## 5. Dateien

| Datei | Änderung |
|-------|---------|
| `utils/zeitparser.py` | `ZeitVektor` Dataclass, `zeit_parsen_vektor()` mit Komponentenerkennung und Referenz-Modus |
| `plugins/timeline_manager/manager.py` | UPDATE-Block: Zwei-Phasen-Parsing, Vektor-Kombination mit altem Termin |

---

## 6. Validierung

```
Setup: Zahnarzt am Do 02.04.2026 14:00

"Verschiebe Zahnarzt auf Freitag"
→ Fr 03.04.2026 14:00 ✅ (relativ zum alten Termin, Uhrzeit behalten)

DB: event_time = 2026-04-03 12:00:00+00 (= 14:00 MEZ), aktiv = true
    alter Termin: aktiv = false (bi-temporal invalidiert)
```

---

→ Zeitparser-Technik: `02_T_c`, Abschnitt 10
→ Timeline-Modul: `02_M_e`, Abschnitt 3.1
→ Lesson Zeitparser-Evolution: `02_L_b`
→ Lesson Timezone: `02_L_a`
