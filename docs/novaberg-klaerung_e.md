# Novaberg — Klärung: Abweichung und Lücke sind derselbe Vorgang (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-klaerung_k.md`](novaberg-klaerung_k.md) · Ausarbeitung: [`novaberg-klaerung_t.md`](novaberg-klaerung_t.md) · Bauplan und Umstellung: [`novaberg-klaerung_b.md`](novaberg-klaerung_b.md) · Messungen: [`novaberg-klaerung_m.md`](novaberg-klaerung_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine. Das Konzept führt keine Entscheidung; `_b` §4 sagt ausdrücklich *„Keines ist beschlossen.“*

---

## B. Offen beim Meister

**Vier** — die Punkte aus §8 (Abschnitt D unten). §8 nennt keinen Adressaten; gezählt sind sie, weil es offene Entwurfsentscheidungen sind und keine Messungen:

1. Wie viele Fragen zu viele sind — nur der stärkste Bedarf oder mehrere gebündelt.
2. Wo das Erwartungsschema liegt — eigene Tabelle, Feld an der Entität oder abgeleitet aus vorhandenen Tripeln.
3. Ob der Aufgabenpfad ein eigenes Urteil braucht — *„Das ist eine Entwurfsentscheidung.“*
4. Ob eine zurückgestellte Schreibung verfällt, und nach welcher Frist (dazu `_b` K4, *Preis*).

**Offen, ohne eine Entscheidung zu verlangen:**

- `_k` §7: Wer zwei widersprüchliche Werte später zusammenführt, *„ist offen und gehört nicht hierher“*.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_b` K3 und Abschnitt F (v0.1) — eine Untergrenze der Bedeutung, die der Charakter nicht unterschreiten darf; verworfen noch am 04.08.2026, weil sie eine distanzierte Nova zum Nachfragen zwänge.
- `_b` K1, *Gegenargument* — ein vom Modell erzeugtes Schema ist selbst eine Behauptung; daher Gegenprobe und Notwendigkeitsmarke als eigenes Feld.
- `_m` §3.2 — die Annahme, der Salienz-Knoten schreibe Fakten; korrigiert am 04.08.2026.
- `_m` §3, Tabelle — *„niemand liest es“* (Urteil über eine Abweichung); widerlegt am 05.08.2026.
- `_b` K5, Kasten, und §5 — K5 als erstes Bauteil, abhängig von `SYK-B1`, und der Vergleich mit `SYK-B8`; zurückgestuft am 04.08.2026. Die Prüfung gehört in den Schreibpfad statt an das Verfasser-Urteil.
- `_k` §6 — die Gleichsetzung mit `novaberg-wissensluecken_k.md`; abgegrenzt (Thema über Wochen gegen Eigenschaft eines konkreten Objekts).

---

## D. Aus dem Konzept: §8

Der Abschnitt, in dem das Konzept seine offenen Punkte führt, ungekürzt.

## 8. Was offen ist

**Wie viele Fragen sind zu viele?** Ein Turn kann mehrere Bedarfe erzeugen. Ob nur der stärkste gestellt wird oder mehrere gebündelt, ist unentschieden — und es entscheidet, ob sich das Verhalten aufmerksam oder anstrengend anfühlt.

**Wo das Erwartungsschema liegt.** Eine eigene Tabelle, ein Feld an der Entität, oder abgeleitet aus vorhandenen Tripeln desselben Typs — die dritte Variante braucht keinen Modellaufruf, aber einen Bestand.

**Ob der Aufgabenpfad ein eigenes Urteil braucht.** Dort läuft der Verfasser nicht. Entweder bekommt er ein reduziertes Urteil, oder es wird ausdrücklich festgehalten, dass von dort ungeprüft geschrieben wird. Das ist eine Entwurfsentscheidung.

**Ob eine zurückgestellte Schreibung verfällt.** Und nach welcher Frist.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder eine Entscheidung einholen — das ist ein eigener Schritt. B1 bis B3 stammen aus der Sichtung, B4 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Versionshistorie* | Zwei Einträge tragen die Nummer „v0.2“ (05.08.2026 und 04.08.2026) | `[gelesen 19.09.2026]` |
| **B2** | `_b` K5 und §5 | K5 hängt an einem Backlog-Eintrag (`15e — FaktenAgent (Salienz-Pipeline)`), nicht an einem Konzept | `[gelesen 19.09.2026]` |
| **B3** | das ganze Konzept | Kein Bezug zum übergeordneten `novaberg-thinking-erkenntniszyklus_k.md`, der seinerseits auf §2.2 verweist und die Klärfrage als Weg in seinem Schritt 6 führt | `[gelesen 19.09.2026]` |
| **B4** | Abschnitt F, *Versionshistorie* v0.2 vom 05.08.2026 | Der Eintrag nennt die widerlegte Aussage *„in §4“*; sie steht in §3, Tabelle, Zeile *Urteil über eine Abweichung* ([`novaberg-klaerung_m.md`](novaberg-klaerung_m.md)) | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Der bisherige Kopf und die Versionshistorie des ungeteilten Konzepts, ungekürzt. Der Kopf trägt keinen Messwert und steht deshalb hier.

### Bisheriger Kopf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — wann ein Objektzustand geprüft wird, und wann daraus eine Frage folgt
**Stand:** 5. August 2026 (Erstfassung 4. August)
**Pfad:** novaberg/docs/novaberg-klaerung_k.md
**Typ:** Konzept (`_k`)
**Status:** ⬜ **nicht gebaut** — Grundsatz formuliert, Bestand belegt, Bauteile entworfen
**Betrifft:** Faktengedächtnis · Verfasser · Planner · Salienz · Perzeption · Dispatcher
**Verwandt:** `novaberg-sykophanz-eindaemmung_k.md` (B1 ist das erste Stück hiervon) · `novaberg-wissensluecken_k.md` (Themen-Neugier, **nicht** dasselbe)

---

## Versionshistorie

- **v0.2 — 05.08.2026:** Eine Aussage in §4 widerlegt: Das dreiwertige Urteil aus `SYK-B1` wird gelesen — seit dem 05.08. von der Vorzeichenprüfung. Für K2 ist es damit ein Anschluss und kein Neubau.
- **v0.2 — 04.08.2026:** **K5 zurückgestuft, nachdem zwei tragende Annahmen der Erstfassung nachgemessen und widerlegt wurden.** Erstens: Die Tabelle `fakten` hat null Zeilen, kein Aufrufer setzt `ziel = "fakten"` — der Triple-Store war in Betrieb und ist beim Umbau nicht mitgezogen worden (Backlog `15e`). Der beschriebene Zeichenketten-Vergleich ist damit nie eingetreten; er wird zum Defekt, sobald `15e` steht. Zweitens: Urteil und Schreibvorgang liegen **nicht** im selben Zustand — es sind zwei Graphen über denselben Turn, korreliert allein über `turn_id`, und der HumanGraph hat gar keinen Verfasser. Die Erstfassung hatte daraus geschlossen, K5 sei einfacher als `SYK-B8`; das Gegenteil stimmt, die Klammer fehlt genauso. **Daraus folgt aber auch etwas Besseres:** Die Prüfung gehört in den Schreibpfad statt an das Verfasser-Urteil, deckt dort beide Graphen und den Aufgabenpfad ab, und K5 hängt nicht mehr an `SYK-B1`.
- **v0.1 — 04.08.2026:** Erstfassung. Anlass war die Frage, wie das Faktengedächtnis Werte korrigiert und aktualisiert — und die Feststellung, dass der Aktualisierungspfad an einem reinen Zeichenkettenvergleich entscheidet und drei verschiedene Fälle gleich behandelt. Der Grundsatz selbst ist allgemeiner als der Anlass: **Abweichung und Lücke sind derselbe Vorgang**, beide heißen *erwartet ≠ vorhanden*, und beide enden in einer Frage. Neu gegenüber der bisherigen Fassung des Gedankens: die Trennung in **zwei** Tore — Notwendigkeit aus dem Objekt, Salienz aus dem Charakter —, ohne die aus Aufmerksamkeit ein Verhör wird.

  **Noch am selben Tag korrigiert (§2.1, K3):** Die erste Fassung gab der Bedeutung eine Untergrenze, die der Charakter nicht unterschreiten darf. Das ist falsch — es zwänge eine distanzierte Nova zum Nachfragen und machte den Charakter zur Fassade. Der Vorgang hat **vier** Stufen, und nur die letzte hängt am Charakter: Erkennen, nicht darauf bauen und nicht überschreiben sind still, gratis und unbedingt; nur das Fragen kostet einen Gesprächszug. Bei voller Distanz merkt Nova die Abweichung, baut nicht darauf, überschreibt den Fakt nicht — und sagt nichts. Sie ist nicht blind, sie ist wortkarg.
