# Novaberg — Die Gedankenkette: ein Gedanke über mehrere Turns (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-gedankenkette_k.md`](novaberg-gedankenkette_k.md) · Bauplan und Umstellung: [`novaberg-gedankenkette_b.md`](novaberg-gedankenkette_b.md) · Diskussion und Ergänzungen: [`novaberg-gedankenkette_e.md`](novaberg-gedankenkette_e.md) · Messungen: [`novaberg-gedankenkette_m.md`](novaberg-gedankenkette_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 3. Der Raum: das Embedding als Radius

Eine Kette bewegt sich in einer **Kugel um ihren Ausgangsvektor**. Was innerhalb liegt, gehört zum Gedanken; was außerhalb liegt, ist ein neuer.

```
kette_radius = 0.95        (Startwert, kalibrierbar)
```

Der Radius ist eng zu ziehen. Ein weiter Radius lässt sie abschweifen, bis das Thema beliebig wird; ein enger hält sie beim Gedanken.

### Die Zahl der Zustellungen misst den Radius

Das ist die Eigenschaft, die diesen Entwurf selbstkalibrierend macht: **Wie viele Zustellungen eine Kette hervorbringt, sagt, ob der Radius stimmt.**

| Zustellungen je Kette | Befund |
|---|---|
| 10 | Radius zu weit — sie schweift, das Thema trägt nicht so lange |
| **3** | gut |
| **4** | auch gut |
| 1 | Radius zu eng — sie kann nichts ergänzen |

Drei oder vier sind der erwartete Bereich, **aber keine Vorgabe.** Es kommt darauf an, was sie vermitteln will; eine Kette darf auch nach zweien fertig sein. Die Zahl ist ein Messwert über den Radius, keine Quote.

> **Hinweis zur Aufteilung (19.09.2026):** §4 bis §8 stehen in [`novaberg-gedankenkette_k.md`](novaberg-gedankenkette_k.md), §9 *Was heute im Weg steht* in [`novaberg-gedankenkette_b.md`](novaberg-gedankenkette_b.md).

## 10. Verhältnis zum Wissensspeicher

Eine Kette, die über Turns wächst, braucht einen Ort für das Gewachsene. Der Prompt ist er nicht — der wird nur damit gefüttert.

**Bei ihren eigenen Wissenslücken darf sie ihre Dateien beliebig ändern und erweitern.** Ausarbeitung und Reflexion einer Kette landen im Wissensspeicher und stehen dem nächsten Glied als Material zur Verfügung — und einer späteren Fortsetzung, auch Tage danach.

~~Das setzt Strang B voraus: Verzeichnis, Format, Mount außerhalb des Git-Roots. Ohne ihn kann eine Kette nur so weit tragen, wie ein Prompt reicht.~~ → **Steht seit Chat 128 (14.08.2026 nachgeprüft).**

Die Bibliothek ist gebaut und läuft in beide Richtungen:

| | Stand am 14.08.2026 |
|---|---|
| **Schreiben** | jede Recherche legt Bericht und Wissensdatei ab, dazu eine Metadatenzeile mit Themen-Embedding; ein Gate entscheidet, ob es Wissen wird oder nur ein Bericht |
| **Lesen** | der Wissens-Manager sucht in **jedem** Turn über das Themen-Embedding, Schwelle 0,40, und speist die Treffer als eigene Kontextquelle ein |
| **Bestand** | über dreitausend Zeilen, stündlich wachsend |

**Was eine Kette daraus gewinnt:** Sie muss das Gewachsene nicht im Prompt mitschleppen. Ausarbeitung und Reflexion liegen in der Bibliothek und werden gefunden, wenn das Thema wiederkommt — auch Tage später, auch ohne dass jemand die Kette fortsetzt.
