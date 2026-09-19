# Novaberg — Die Charakter-Räder als Messreihe

**Absicht:** Das Zuwendungs- und das Initiative-Rad bilden Novas akuten Zustand ab und werden durch die Messungen der letzten Tage stabilisiert — jede Erhebung bleibt als rohe Zeile einer Messreihe erhalten, der gelesene Wert ist ein gewichtetes Mittel über die letzten fünf Erhebungen, eine einzelne Messung bewegt ihn nur zu 41 %, und das Mittel wird nie als Messung zurückgeschrieben.
**Stand:** 6. September 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Charakter-Räder als Messreihe* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-charakter-rad-messreihe_t.md`](novaberg-charakter-rad-messreihe_t.md) · [`novaberg-charakter-rad-messreihe_b.md`](novaberg-charakter-rad-messreihe_b.md) · [`novaberg-charakter-rad-messreihe_e.md`](novaberg-charakter-rad-messreihe_e.md) · [`novaberg-charakter-rad-messreihe_m.md`](novaberg-charakter-rad-messreihe_m.md)
**Entschieden:** 1 · **Offen beim Meister:** 1 (Liste in [`novaberg-charakter-rad-messreihe_e.md`](novaberg-charakter-rad-messreihe_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-charakter-rad-messreihe_k.md §4` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-charakter-rad-messreihe_t.md`](novaberg-charakter-rad-messreihe_t.md), `_b` ist [`novaberg-charakter-rad-messreihe_b.md`](novaberg-charakter-rad-messreihe_b.md), `_e` ist [`novaberg-charakter-rad-messreihe_e.md`](novaberg-charakter-rad-messreihe_e.md), `_m` ist [`novaberg-charakter-rad-messreihe_m.md`](novaberg-charakter-rad-messreihe_m.md).

| § | Datei |
|---|---|
| 1 · 2 | `_k` |
| 3 · 3a · 4 · 5 | `_t` |
| 6 | `_k` |
| 7 | `_b` |
| 8 | `_e` |
| Versionshistorie | `_e` |
| Was die Streuungsangabe misst — und was nicht | `_m` |
| bisheriger Kopf (Projekt, Dokument, Stand mit den Messwerten vom 26. und 27.08.2026, Pfad, Typ, Status, Voraussetzung, Betrifft) | `_m` |
| Entschieden, Offen beim Meister, Offen ohne Frage, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Die Beobachtung

Am 31.07.2026 wechselte Novas Zuwendungsrad innerhalb von zwei Stunden von einer leeren Abwendungsseite zu `distanz 1.0`. Der Faktor, den die Salienz-Formel bei **jedem** Turn liest, fiel von 1.215 auf 0.980. Dazwischen lagen zwanzig sachliche Frage-Antwort-Turns.

Die naheliegende Erklärung — das Modell würfelt — ist geprüft und **widerlegt**: Drei Erhebungen gegen dieselbe Eingabe bei Produktions-Temperatur ergaben elf von zwölf Speichen identisch, `distanz` stabil auf 1.0. Die Verfahrensstreuung des Faktors beträgt **0.08**, der beobachtete Sprung **0.235** — das Dreifache.

> **Die Zahl 0.08 ist eine Zustandsangabe und seit dem 26.08.2026 überholt.** Sie wurde bei Produktions-Temperatur **0.2** erhoben. Der Knoten `charakter_hash` steht seither auf **0.0**, und drei Rad-Läufe auf demselben Eingang liefern **1,2977 · 1,2977 · 1,2977** — Spanne **0,0000**. **Die Verfahrensstreuung ist nicht kleiner geworden, sie ist verschwunden.**
>
> **Der Schluss dieses Absatzes bleibt trotzdem richtig, und zwar stärker:** Wenn das Verfahren gar nicht streut, kann der Sprung von 0.235 erst recht nicht daher kommen. Überholt ist die Vergleichsgröße, nicht die Aussage.
>
> **An ihre Stelle tritt eine andere Streuung, eine Stufe früher.** Bei festgehaltenem Material bewegt allein die Neuziehung des **Kern-Hash** den Zuwendungsfaktor um **0,2908** (`RAD-MEDIAN-SCHUETZT-FALSCHE-QUELLE`, 26.08.2026). Auch diese Zahl stammt von **vor** dem Temperaturwechsel; ob sie bei 0.0 bleibt, ist **ungemessen** und die nächste Frage an diese Reihe.

**Der Sprung war also echt.** Und genau das ist das Problem: Zwanzig Turns gegen einen Bestand von rund tausend Kurzzeit-Einträgen haben eine Größe umgeworfen, die jeder Turn liest.

### Was strukturell dahintersteckt

Das Rad speichert heute **ausschließlich sein Ergebnis** — einen einzigen Zug, der beim nächsten Lauf überschrieben wird. Damit verletzt es Regel (1) der Konvention über abgeleitete Werte: *„Speichere die Eingaben, nicht nur das Ergebnis."*

Die Folge war am 31.07. praktisch zu besichtigen: Ob der Sprung Bewegung oder Rauschen war, ließ sich nicht aus den Daten beantworten. Die vorige Erhebung existierte nicht mehr; sie musste durch Nachstellen der Destillation rekonstruiert werden. Regel (3) — *„jederzeit von Grund auf nachrechenbar"* — ist für das Rad heute unerfüllbar.

---

## 2. Was gelten soll

> **Das Rad misst einen akuten Zustand, und es wird durch die Messungen der letzten Tage stabilisiert.**

Das ist eine Entscheidung, keine Beschreibung des Bestands. Sie beantwortet eine Frage, die bisher offen war: Ob das Rad eine dauerhafte Eigenschaft abbildet oder eine gegenwärtige Lage. Antwort: **die gegenwärtige Lage** — die dauerhafte Eigenschaft steht bereits im Kern-Hash.

Daraus folgt die Bauart:

```
alle 12 Stunden        eine Messung          → Zeile in der Messreihe (roh)
bei jedem Lesen        gewichtetes Mittel    → Wert in charakter_hash
                       über die letzten 5
```

**Die Messreihe ist die Eingabe, das Rad ist ihr Ergebnis.** Nicht umgekehrt.

### Die Regel, an der die Bauart kippen würde

**Das Mittel wird nie als Messung zurückgeschrieben.** Sonst mittelt jeder Lauf über Werte, die selbst schon Mittel waren — der Akkumulator aus Regel (2), an dem der Ziel-Decay gescheitert ist. Nach fünf Läufen wäre nicht mehr rekonstruierbar, was je gemessen wurde.

Sauber ist die Trennung:

- **Die Messreihe nimmt nur rohe Läufe auf.** Eine Erhebung, eine Zeile, unverändert.
- **Der gelesene Wert ist eine reine Funktion über die letzten N Zeilen**, bei jeder Berechnung neu gebildet.

Damit ist Regel (4) erfüllt: Die **Aggregation** ist idempotent. Das Anhängen einer Messung ist es nicht — das ist zulässig, es ist ein Ereignis wie ein Zähler, kein Rechenschritt auf dem Ergebnis.

> **§3 bis §5, §7, §8 und die Abschnitte nach §8 stehen nicht in dieser Datei.** Takt, Gewichtung und Datenmodell (§3 bis §5) stehen in [`novaberg-charakter-rad-messreihe_t.md`](novaberg-charakter-rad-messreihe_t.md), der Bauteil (§7) in [`novaberg-charakter-rad-messreihe_b.md`](novaberg-charakter-rad-messreihe_b.md), die offenen Punkte (§8) und die Versionshistorie in [`novaberg-charakter-rad-messreihe_e.md`](novaberg-charakter-rad-messreihe_e.md), der bisherige Kopf und der Abschnitt *Was die Streuungsangabe misst — und was nicht* in [`novaberg-charakter-rad-messreihe_m.md`](novaberg-charakter-rad-messreihe_m.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

---

## 6. Was ausdrücklich nicht enthalten ist

- **Keine Glättung des Profiltexts.** Geglättet wird das Rad, nicht seine Eingabe. Wer beides glättet, dämpft zweimal und weiß hinterher nicht, welche Dämpfung gewirkt hat.
- **Kein Rückschreiben des Mittels in die Messreihe** (§2).
- **Keine Änderung an der Rechnung des Faktors.** `nutzer_gewichtung_berechnen()` bleibt, was es ist; es bekommt nur ein anderes Rad übergeben.
- **Keine Änderung an der Rechnung des Initiative-Rades.** Es behält seine drei Läufe; neu ist, dass jeder davon als eigene Zeile in der Reihe liegt und der gespeicherte Wert aus den letzten Erhebungen folgt statt aus dem Median-Lauf allein.
- **Keine Entscheidung über die Zusammensetzung der Quelle.** Dass das Rad zur einen Hälfte aus dem zeitlosen Kern-Hash liest, bleibt offen (§8).
