# Novaberg — Konvention: Abgeleitete Werte

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Verbindliche Konvention für Werte, die aus anderen Werten berechnet werden
**Stand:** 27. Juli 2026, Chat 111
**Pfad:** novaberg/docs/novaberg-convention-abgeleitete-werte.md
**Typ:** Convention
**Anlass:** `KZG-SALIENZ-SKALENBRUCH`, `ZIEL-DECAY-FORMEL-KUMULATIV` — dieselbe Bauart, zwei Fundorte
**Erste Anwendung:** `novaberg-kzg-salienz_k.md`

---

## 1. Die Fehlerklasse

Ein System speichert eine Zahl, die aus anderen Zahlen entsteht. Zwei Bauarten sind möglich, und nur eine ist tragfähig.

**Akkumulator (untauglich):**

```
neu = f(alt, zuwachs)
speichere neu in dasselbe Feld, aus dem alt gelesen wurde
```

**Reine Funktion (verbindlich):**

```
wert = f(eingabe_1, eingabe_2, …)
wobei keine Eingabe je aus wert berechnet wurde
```

Der Unterschied wird erst sichtbar, wenn etwas schiefgeht — und dann ist es zu spät, weil die Historie nicht mehr existiert.

## 2. Was der Akkumulator kostet

**Er ist nicht idempotent.** Läuft die Berechnung zweimal, steht ein anderer Wert da. Ein doppelt zugestelltes Event, ein Retry, ein zweimal verarbeiteter Queue-Eintrag — jeder verfälscht dauerhaft.

**Er ist pfadabhängig.** Zwei Einträge mit derselben Vorgeschichte können verschiedene Werte tragen, je nachdem, in welcher Reihenfolge die Verstärkungen kamen. Der Wert beschreibt dann nicht mehr die Sache, sondern die Historie ihrer Verarbeitung.

**Er ist nicht nachrechenbar.** Ist der Wert einmal falsch, gibt es keinen Weg zurück. Die Eingaben, aus denen er entstand, sind überschrieben. Eine Migration kann ihn nicht reparieren, nur ersetzen — und dafür fehlt die Grundlage.

**Er verbirgt Skalenfehler.** Genau das ist in `KZG-SALIENZ-SKALENBRUCH` passiert: Eine Dämpfungsformel war auf einen Wertebereich kalibriert, den die Eingangsgröße nie hatte. Weil der gedämpfte Zuwachs in dasselbe Feld zurückfloss, wuchs der Wert über seine eigene Skala hinaus, ohne dass eine einzige Prüfung anschlug. 68 % eines Korpus von 775 Einträgen standen am Ende über dem dokumentierten Maximum.

## 3. Die Regeln

**(1) Speichere die Eingaben, nicht nur das Ergebnis.**

Jede Größe, aus der sich ein Wert berechnet, ist ein eigenes Feld. Das Ergebnis darf zusätzlich gespeichert werden — nie stattdessen.

**(2) Eine Eingabe wird nie aus dem Ergebnis berechnet.**

Das ist die eigentliche Regel. Ein Zähler, der hochgezählt wird (`haeufigkeit + 1`), ist eine zulässige Eingabe: Er hängt nicht vom Ergebnis ab. Ein Gewicht, das aus dem alten Gewicht entsteht, ist es nicht.

**(3) Das Ergebnis ist jederzeit von Grund auf nachrechenbar.**

Prüfkriterium: Lässt sich der Wert aus den gespeicherten Feldern neu berechnen, ohne den bisherigen Wert zu kennen? Wenn nein, ist es ein Akkumulator.

**(4) Zweimal rechnen ändert nichts.**

Die Berechnung ist idempotent. Ein Wiederholungslauf über den gesamten Bestand ist ein zulässiger Wartungsvorgang, kein Datenverlust.

**(5) Eine Formkurve ist eine Umbenennung, kein Rechenschritt.**

Wird ein Wert durch eine monotone Kurve geschickt — Dämpfung, Sättigung, Normalisierung —, ändert das keine Reihenfolge und keinen Zeitpunkt, nur die Beschriftung. Daraus folgt zweierlei:

- Die Kurve wird **genau einmal** angewandt, beim Lesen oder beim Schreiben, nie an beiden Stellen.
- **Zuwächse greifen vor der Kurve an**, am Anker. Ein Zuwachs auf den gekrümmten Wert bedeutet an jeder Stelle der Skala etwas anderes.

**(6) Schwellwerte stehen auf der Skala, die tatsächlich gespeichert ist.**

Wird eine Kurve angewandt, müssen alle Tore durch dieselbe Kurve abgebildet werden. Ein Schwellwert auf der Rohskala und ein zweiter auf der gekrümmten Skala sind zwei Skalen im selben System — der Zustand, den `KZG-SALIENZ-KONSUMENTEN-DISSENS` beschreibt.

**(7) Jede so entstandene Konstante nennt ihr Roh-Äquivalent im Kommentar.**

`KZG_SALIENZ_MINIMUM = 0.6738` ist für sich unlesbar. Dass die Zahl „das Modell bewertete mit 0.3" bedeutet, steht nirgends im Wert. Ohne den Kommentar ist die Konstante beim nächsten Lesen wieder eine offene Frage.

## 4. Der Bestand, ehrlich eingeordnet

Diese Konvention beschreibt einen Zielzustand, den heute kein Modul vollständig erfüllt.

| Ort | Bauart | Bewertung |
|---|---|---|
| `memory/lzg_knoten.py` — `gewicht_absolut` | reine Funktion von `gewicht_roh` | Regel (3) erfüllt |
| `memory/lzg_knoten.py` — `gewicht_roh` | Akkumulator (`+= BOOST`) | Regel (2) verletzt |
| `memory/lzg_knoten.py` — `gewicht_decay` | reine Funktion aus `gewicht_absolut` und `verstaerkt_am` | erfüllt |
| `memory/kzg.py`, `agents/kzg/speicher.py` — `salienz` | Akkumulator mit Skalenfehler | `KZG-SALIENZ-SKALENBRUCH` |
| Ziel-Decay | Akkumulator | `ZIEL-DECAY-FORMEL-KUMULATIV` |

Das LZG-Gewicht ist damit **halb** konform: Die Kurve ist sauber, der Anker darunter nicht. Es taugt als Vorbild für die Formkurve und ausdrücklich **nicht** als Vorbild für den Anker.

Der KZG-Salienz-Neubau ist der erste vollständig konforme Fall: `salienz` wird aus einem unveränderlichen Eingangswert und einem Zähler berechnet, von denen keiner je aus `salienz` entstanden ist.

## 5. Prüffragen für neuen Code

Vor jedem Feld, das eine berechnete Zahl hält:

1. Aus welchen gespeicherten Feldern entsteht der Wert?
2. Ist eines davon selbst aus diesem Wert entstanden? → Bauart ändern.
3. Kann ich den Wert für den gesamten Bestand neu berechnen? → Wenn nein, fehlt ein Feld.
4. Was passiert bei doppelter Ausführung?
5. Wenn eine Kurve im Spiel ist: Auf welcher Skala steht der gespeicherte Wert, und stehen alle Schwellwerte auf derselben?

**Zusammenhang:** `novaberg-kzg-salienz_k.md` (erste Anwendung) · `KZG-SALIENZ-SKALENBRUCH` · `ZIEL-DECAY-FORMEL-KUMULATIV` · `KZG-SALIENZ-KONSUMENTEN-DISSENS` · `novaberg-mem-lzg.md` (Ebbinghaus-Decay)
