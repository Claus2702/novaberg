# Novaberg — Frames (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden. Absicht und Kopfblock: [`novaberg-thinking-frames_k.md`](novaberg-thinking-frames_k.md) · Ausarbeitung: [`novaberg-thinking-frames_t.md`](novaberg-thinking-frames_t.md) · Bauplan und Umstellung: [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## A. Entschieden

Keine. Das Konzept führt keine Entscheidung mit Urheber und Datum.

**Genannt, aber nicht gezählt:**

- `_t` §5.5: Die Frage nach dem Reaktions-Zeitpunkt *„wird in der Implementierungs-Phase pragmatisch entschieden“* — eine offene Frage, keine Entscheidung (Abschnitt C).
- §12.1 unten, *Frame-Lager-Initialbefüllung*: *„Empfehlung: leer starten“* — eine Empfehlung ohne Urheber.
- §12.1 unten, *Frame-Klasse-Hierarchie*: *„Pragmatisch: vorerst flach“* — eine Vorgabe für den Bau ohne Urheber.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage, die eine Entscheidung verlangt.

---

## C. Offen ohne Frage

Punkte, die das Konzept selbst als offen führt:

- §12.1 unten: Reaktions-Zeitpunkt bei Konflikten, Konflikt-Klassifikation, Akutheit als skalarer Wert, Frame-Klasse-Hierarchie, Initialbefüllung des Lagers, Plausibilitäts-Implementierung.
- `_t` §5.4 und §5.5: die Klassifikation der Konflikt-Schwere und der Reaktions-Zeitpunkt als *offene Designfragen* (dieselben wie in §12.1).
- `_k` §10.5: die Verbindung zu Drive und Neugier, *„in der Implementierung später aufzubauen“*.
- `_b`, *Stand-Block zwischen §4 und §5*: *„§5 (Cross-Frame) bleibt offen.“* `_b`, *Aus §9.1*: Lernmechanik (§7.3) und Operationen (§9.2) bleiben Konzept.

Der Abschnitt §12 des ungeteilten Konzepts folgt, ohne §12.2.

## 12. Offene Punkte und nächste Schritte

### 12.1 Offene konzeptionelle Fragen

**Reaktions-Zeitpunkt bei Konflikten** (§5.5). Sofortige Plausibilitäts-Reaktion oder aufgeschobene Reaktion zum Akutheits-Zeitpunkt? Vorerst: konflikt-klassen-abhängig, Entscheidung pragmatisch in der Implementierung.

**Konflikt-Klassifikation** (§5.4). Wann ist ein Konflikt hart blockierend, wann Frage wert? Vermutlich Heuristik aus Konsens-Häufigkeit im Lager. Genauer Algorithmus offen.

**Akutheits-Schwelle als skalarer Wert?** Akutheit ist hier qualitativ beschrieben (latent, halb-akut, akut). Ob das in der Implementierung eine binäre, dreistufige oder kontinuierliche Variable wird, ist offen.

**Frame-Klasse-Hierarchie.** Sollen Frames in Klassen-Hierarchien stehen? *Termin* als Oberklasse, *Zahnarzt-Termin* und *Werkstatt-Termin* als Spezialisierungen mit zusätzlichen Slots? Pragmatisch: vorerst flach, spätere Hierarchisierung möglich.

**Frame-Lager-Initialbefüllung.** Startet das Lager leer und füllt sich durch Beobachtung, oder gibt es einen Seed mit häufigen Frame-Klassen (Termin, Person, Ort)? Empfehlung: leer starten, Seed wäre vorzeitige Optimierung.

**Plausibilitäts-Implementierung.** LLM-Call pro akutem Frame, oder Sammel-Call mit allen aktiven Frames? Performance-Frage, in der Implementierung zu klären.

> **§12.2 steht nicht in dieser Datei.** Die Implementierungs-Reihenfolge steht in [`novaberg-thinking-frames_b.md`](novaberg-thinking-frames_b.md), *Aus §12*.

### 12.3 Risiken

**Über-Validierung.** Wenn jeder Turn rekursiv mehrere Frames öffnet, droht Latenz-Explosion. Pragmatisch: harte Tiefenbegrenzung (2-3 Ebenen), Akutheits-Filter als Gatekeeper.

**Halluzinierte Slots.** Das LLM erfindet Slots, die nicht im Lager sind. Gegenmaßnahme: das Lager kennt die typische Slot-Menge pro Klasse, ungewöhnliche Slots werden markiert, nicht still übernommen.

**Lager-Pollution.** Schlecht erhobene Frames verschmutzen den Konsens. Gegenmaßnahme: Decay, Häufigkeits-Untergrenze für Default-Wert-Übernahme.

**Vehicle-Lärm.** Plausibilitäts-Hinweise klingen schnell besserwisserisch, wenn sie nicht über die Vehicle-Schicht laufen. Gegenmaßnahme: Frame-System liefert nur strukturelle Information, Responder formt aus.

---

## D. Diskussion und verworfene Varianten

Abgelöste Fassungen und verworfene Wege stehen an ihrer Stelle, mit Grund:

- Abschnitt F, *Vorgänger-Stand* — die frühere Fassung (Frames eng als Slot-Erhebung für Vorhaben, ein Pipeline-Pilot am Termin-Frame) ist als zu eng erkannt und durch die universale Sicht ersetzt; ihre Implementierungsplanung ist in das Pipeline-Konzept ausgelagert.
- `_k` §3 — die Definition *„Slot-Erhebung für Vorhaben“*: *„Diese Definition ist zu eng.“*
- `_k` §3.2 — die Abgrenzungen: Frames sind keine Skills, keine Workflows, keine Datenbank-Records, kein Code.
- `_k` §4.5 — die binäre Unterscheidung *Interface vs. Referenz*: *„Das war zu starr“*, ersetzt durch gradierte Akutheit.
- `_t` §5.1 — die flache Slot-Erhebung der früheren Fassung, die den Cross-Frame-Konflikt nicht entdeckt.
- `_t` §5.5 — Variante A (sofortige Reaktion) gegen Variante B (aufgeschobene Reaktion); die Tendenz ist konflikt-klassen-abhängig, offen.
- `_t` §6.1 — hartcodierte Plausibilitäts-Constraints, verworfen als *„Albtraum-Pfad“*.
- `_t` §7.1 — hardcoded Schemas gegen LLM-Wissen und Frame-Lager, mit Vergleichstabelle.
- §12.1 oben — ein Seed für das Frame-Lager, verworfen als *„vorzeitige Optimierung“*.
- `_b`, *Aus §9.1* — der gebaute Teil des Lagers weicht vom Schema in `_t` §9.1 ab: Verankerung an `entitaeten` statt Präfix-String, Slots als Zeilen statt JSONB, kein Decay, keine `haeufigkeit`.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder gegen eine Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B6 stammen aus der Sichtung, B7 bis B9 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_b`, *Stand-Block zwischen §4 und §5* | *„Validierung (§5) und Plausibilität (§6) sind nicht gebaut“*; im selben Block *„Seit dem 29.08.2026 ist auch §6 in der Konversationsfassung gebaut“* | `[gelesen 19.09.2026]` |
| **B2** | `_b`, *Aus §3.1* | Der Nachtrag schließt mit *„Nicht gebaut.“*; laut `novaberg-thinking-lage_k.md` ist C1 (das Objekt-Merkmal der Anmeldung) seit dem 16.09.2026 gebaut | `[gelesen 19.09.2026]` |
| **B3** | Abschnitt F, bisherige Schlusszeile | Sie nennt den Stand 09.05.2026; der bisherige Kopf trägt den Stand 14.09.2026, dazu die Nachträge in §3.1 und §9.1 und den Stand-Block | `[gelesen 19.09.2026]` |
| **B4** | `_b`, *Aus §12* (§12.2) | Phase 0 (M2.5b, TIMELINE-PAIR-MIGRATION, NOTIZEN-PAIR-MISSING, FAKTEN-PAIR-IGNORED) *„weiterhin gilt“* — nicht mit dem heutigen Stand abgeglichen | `[gelesen 19.09.2026]` |
| **B5** | `_t` §5.5 | Der Absatz ist in der Ich-Form geschrieben (*„Mein Bauchgefühl, das ich aber nicht hartcoden möchte“*); wessen Tendenz das ist, sagt das Konzept nicht | `[gelesen 19.09.2026]` |
| **B6** | `_k` §13, *Folge-Dokumente (in Arbeit)* | Ob beide Dokumente noch *in Arbeit* sind, ist nicht geprüft; beide Dateien liegen am 19.09.2026 in `docs/` | `[gelesen 19.09.2026]` |
| **B7** | `_t` §5.4, letzter Absatz | *„eine offene Designfrage (siehe §11)“*; §11 sind die Designprinzipien (`_k`), die Frage steht in §12.1 (Abschnitt C) | `[gelesen 19.09.2026]` |
| **B8** | `_k` §2.3, §3.2, §4.3, §8.2 | Verweise auf *„Dokument 2“* und *„Dokument 3“* ohne Dateinamen; die Zählung steht nirgends im Konzept. Aus dem Zusammenhang gemeint sind das Pipeline- und das Skills-Konzept (§13) | `[gelesen 19.09.2026]` |
| **B9** | Abschnitt F, *Vorgänger-Stand* | *„Die alte 4-Phasen-Implementierungsplanung wandert in das Folge-Dokument“*; der Phasen-Plan dort (`novaberg-thinking-cognitive-pipeline_k.md` §11) hat drei Phasen, A bis C | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen — bisheriger Kopf und Schluss

### Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts mit dem Absatz *Vorgänger-Stand*, ungekürzt. Er trägt keinen Messwert und steht deshalb hier und nicht in einem Teil `_m`.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Frames — Universales kognitives Substrat (Konzept)
**Stand:** 14. September 2026, 19:52 UTC (Nachtrag in §3.1: das Werkzeug-Frame als Objekt-Merkmal der Anmeldung, entworfen in Scheibe 12). Davor 13. September 2026, 15:11 UTC (Nachtrag in §9.1: ein Teil des Frame-Lagers steht als Eigenschaftsgedächtnis der Sachlage, Scheibe 11). Davor 29. August 2026, mittags (§6 Plausibilität gebaut, offene Slots tragen ihren Wissensträger, gedeckte ihren Sprecher — Stand-Block vor §5). Davor 28. August 2026 (Konversationsfassung gebaut — Stand-Block vor §5). Davor 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-frames_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 80 (erste Konzeption als Slot-Erhebung pro Vorhaben), Chat 81 (universale Erweiterung — Frame als kognitives Substrat, Akutheit als Trigger, iterative Validierung, Plausibilitätsprüfung, Trennung zu Skills)

**Vorgänger-Stand:** Die Chat-80-Fassung dieses Dokuments definierte Frames eng als "Slot-Erhebung für Vorhaben" und beschrieb einen Pipeline-Pilot am Termin-Frame. Im Verlauf von Chat 81 wurde diese Definition als zu eng erkannt und durch die hier dokumentierte universale Sicht ersetzt. Die alte 4-Phasen-Implementierungsplanung wandert in das Folge-Dokument `novaberg-thinking-cognitive-pipeline_k.md`, weil Pipeline-Mechanik dort besser aufgehoben ist als im Substrat-Dokument.

### Bisheriger Schluss

Die Schlusszeile des ungeteilten Konzepts, ungekürzt.

*Stand 09.05.2026 — Chat 81. Universalisierung der Frame-Sicht aus dem Chat-80-Vorgängerstand. Akutheit, iterative Validierung, Plausibilitätsprüfung, Frame-vs-Skill-Trennung. Phasen-Plan ausgelagert in das Cognitive-Pipeline-Dokument.*
