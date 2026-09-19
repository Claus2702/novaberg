# Novaberg — KZG-Salienz: Neubau als abgeleiteter Wert

**Absicht:** Die KZG-Salienz ist ein berechneter Wert auf der Skala 0 bis 1 — eine reine Funktion aus der unveränderlichen Eingangsbewertung und der Zahl der Wiederholungen —, der Einprägsame und der Angesammelte enden am selben Tor ins Langzeitgedächtnis, und ein Eintrag, der einen neuen LZG-Knoten erzeugt hat, verlässt das Kurzzeitgedächtnis.
**Stand:** 29. Juli 2026 (am 19.09.2026 in Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *KZG-Salienz-Neubau* 🟠 · *`salience` — Salienz als Entscheider* 🔴 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md) · [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md) · [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md) · `novaberg-kzg-salienz_m.md` — keiner
**Entschieden:** 2 · **Offen beim Meister:** 0 (Liste in [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-kzg-salienz_k.md §3` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md), `_b` ist [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md), `_e` ist [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md).

| § | Datei |
|---|---|
| 1 · 2 | `_k` |
| 3 · 4 · 5 · 6 · 7 · 8 · 9 | `_t` |
| 10 (mit *Die Migration, wie sie stattgefunden hat*) | `_b` |
| 11 (Bauteile 0, 1a, 1b, 1, 2) | `_b`; aus Bauteil 1b die Unterabschnitte *Was Salienz für Novas Äußerung bedeutet*, *Das neue Feld*, *Das Charakter-Rad* und *Zusammenspiel mit der Kurve* in `_t`, der Unterabschnitt *Offen* in `_e` |
| 12 (mit der Zeile *Zusammenhang*) | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Voraussetzung, Ersetzt, Schließt, *Sollte schließen …*, Kasten *Diese Zeile war eine Absicht …*) | `_e` |
| Entschieden, Offen, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Befund

Die KZG-Salienz ist heute ein Akkumulator mit einer Dämpfung, die auf den falschen Wertebereich kalibriert ist.

```
remaining = max(0.0, CAP - alte_salienz)      # CAP = 10.0
ratio     = remaining / CAP
daempfung = sin(ratio * pi/2) ** 0.6
effektiv  = (salienz / 2.0) * daempfung
```

Die Größe lebt auf 0.0–1.0, die Kurve ist über 0–10 gespannt. Im gesamten Entscheidungsbereich dämpft sie um **unter 1 %** — bei `alte_salienz = 0.7` um 0.36 %. Der Docstring verspricht, eine „Salienz-Explosion" zu verhindern; gemessen verhindert er nichts.

**Wirkung, gemessen 26.07.2026 an der Partition `kzg:{user}:{char}:*` (775 Einträge):** 527 Einträge (68 %) stehen über dem dokumentierten Maximum 1.0, der Höchstwert bei 10.002. Der oberste Eimer der Verteilung ist dicker als die drei darunter — ein Stau an einer Wand, kein Verteilungsschwanz. Nur 7 von 775 liegen unter 0.5.

**Folge:** Sämtliche Tore sind für zwei Drittel des Korpus wirkungslos. In sieben aufeinanderfolgenden `dispatch_kzg`-Läufen eines echten Gesprächs gab es null Ablehnungen.

Zwei Verstärkungen genügen, um die Skala zu verlassen: Bei `haeufigkeit = 1` stehen runde Werte (0.7, 0.4), ab `haeufigkeit = 2` lange Nachkommastellen über 0.8, ab 3 über 1.0.

**Alle Zahlen dieses Abschnitts stammen aus der Zeit vor dem Reset vom 27.07.2026, 09:13 UTC** und sind nicht mehr reproduzierbar — die Partition ist leer. Sie bleiben als Begründung stehen, weil der Befund nicht auf ihnen ruht, sondern auf der Formel: Eine Dämpfung, die gegen einen Deckel von 10 rechnet, während die Größe bei 1 endet, ist unabhängig von jedem Bestand falsch. Die Zahlen belegen, dass der Fehler auch gewirkt hat.

## 2. Was die Salienz bedeuten soll

**Entschieden Chat 111.** Die Salienz ist das Tor zwischen Kurzzeit- und Langzeitgedächtnis. Sie bildet zwei Wege ab, auf denen etwas dauerhaft wird:

**Der Einprägsame.** Ein Erlebnis oder eine Einsicht kann so bedeutsam sein, dass sie sofort bleibt — ohne Wiederholung, beim ersten Mal. Das Modell bewertet das beim Anlegen.

**Der Angesammelte.** Etwas mittelmäßig Wichtiges wird dadurch bedeutsam, dass es wiederkommt. Sieben Wiederholungen ab der mittleren Bewertung reichen aus.

Beides endet am selben Tor. Was hindurchgeht, ist im Langzeitgedächtnis und entwickelt sich dort weiter — oder nicht.

Daraus folgt die Bauart: Der Eingangswert des Modells und die Zahl der Wiederholungen sind **zwei getrennte, gespeicherte Größen**. Die Salienz ist ihre reine Funktion.

> **§3 bis §11 stehen nicht in dieser Datei.** Formel, Felder, Konstanten, Weg zum Tor, Konsumenten, das zweite Bauteil und die Wirkung im LZG (§3–§9) stehen in [`novaberg-kzg-salienz_t.md`](novaberg-kzg-salienz_t.md), dazu die Formel für Novas Äußerung aus Bauteil 1b; Migration und die Bauteile mit `ZIEL` / `TEST` / `MESSUNG` samt Abnahmen (§10, §11) in [`novaberg-kzg-salienz_b.md`](novaberg-kzg-salienz_b.md); der bisherige Kopf und der offene Punkt aus Bauteil 1b in [`novaberg-kzg-salienz_e.md`](novaberg-kzg-salienz_e.md). Welche Datei welchen Abschnitt trägt, sagt die Tabelle oben.

## 12. Nicht enthalten

**Decay auf der KZG-Salienz** (`KZG-KEIN-DECAY`, Sprint-Teil c des ursprünglichen Zuschnitts). Der Bestand bewegt sich nach diesem Umbau nur noch aufwärts, aber er verlässt das KZG jetzt an zwei Stellen — durch Promotion und durch TTL. Ob darüber hinaus eine Abwärtsbewegung nötig ist, wird **nach** der Messung aus §11 entschieden, nicht vorher. Kommt sie, gehört sie als Alters-Term in dieselbe reine Funktion, nicht als Subtraktion auf ein gespeichertes Feld.

**Die Lebensdauer im LZG.** Rund 6,7 Jahre bis zur Deaktivierung ist länger, als die Vorstellung vom Langzeitgedächtnis nahelegt. Das ist ein eigener Befund und keine Aufgabe dieses Sprints.

**E7** (`novaberg-charakter-resonanz_k.md` §442) wird durch diesen Umbau nicht beantwortet, sondern **beantwortbar**. Die Frage, ob das LZG-Gate das richtige Gate für Novas Charakter ist, ist neu zu stellen, sobald die Skala hält.

**Zusammenhang:** `novaberg-convention-abgeleitete-werte.md` (Bauart) · `novaberg-mem-kzg.md` (TTL-Stufen, Auffrischung) · `novaberg-mem-lzg.md` (Decay, Vorbild der Kurve) · `novaberg-node-salience.md` (die Bewertung, die den Eingangswert liefert) · `novaberg-charakter-resonanz_k.md` §16, §E7
