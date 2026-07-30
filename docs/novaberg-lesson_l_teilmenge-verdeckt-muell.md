# Novaberg — Lesson: Eine Teilmengen-Prüfung kann Müll nicht von Negativinformation trennen

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Wer nur gegen eine Teilmenge prüft, hält jeden unbekannten Wert für ein gültiges Nein
**Stand:** 30. Juli 2026, Chat 117
**Pfad:** novaberg/docs/novaberg-lesson_l_teilmenge-verdeckt-muell.md
**Auslöser:** `KALIBRIER-INTENTIONEN-UNGEPARST` — M1 der Initiative-Achse trug zwei Monate lang einen Konstantwert
**Verwandt:** `novaberg-lesson_l_default-wie-fehlschlag.md`, `novaberg-lesson_l_silent-skip.md`

---

## 1. Der Fall

Der Kalibrier-Korpus las das Feld `intentionen` aus dem KZG-Hash und splittete es an Kommas. Das Feld ist aber eine JSON-Liste, geschrieben mit `json.dumps`. Aus `["reflexion", "information_teilen"]` wurden damit zwei Bruchstücke, die die Syntax ihres Transportformats mittrugen: `["reflexion"` und `"information_teilen"]`.

`fuehrung_messen` prüft die gelesene Liste gegen `GV_INITIATIVE_FUEHREND` — fünf von sechzehn Intentionen. Ein Bruchstück mit Klammer trifft dort nie. Und weil die Liste dabei **nicht leer** war, galt M1 nicht als *fehlend*, sondern als *nicht führend*: ein harter Beitrag von −1.0 in jeden einzelnen Turn.

Gemessen am 30.07.2026: **0 von 144 Turns** trugen eine führende Intention. Nach dem Parsen: **40 von 99**.

Die Laufzeit war nie betroffen. Sie holt die Intentionen aus den Session-Turns, wo sie als echte Liste liegen. Betroffen war nur der Korpus — dessen Modul-Docstring zusagt, der Rohwert entstehe „wie zur Laufzeit". Zwei Monate lang entstand er ohne M1.

---

## 2. Die eigentliche Ursache: zwei Serialisierungen in einem Hash

Im selben Redis-Hash liegen beide Formen:

```
themen      = N-Frame-Modell, physikalische Unitarität, kognitive Aktualisierung, …
intentionen = ["reflexion", "information_teilen"]
```

`themen` wird mit `", ".join(...)` geschrieben, `intentionen` mit `json.dumps(...)`. **Sechs andere Lesestellen im Code splitten `themen` an Kommas — und sind korrekt.** Der Leser der Intentionen wurde nach dem Nachbarn gebaut und war für genau ein Feld falsch.

Es ist also kein Muster, sondern ein Einzelfall — aber einer, der jederzeit wieder entstehen kann, solange in einem Datensatz zwei Formate ohne Kennzeichnung nebeneinanderliegen.

---

## 3. Warum keine Prüfung ansprang

Die Intentionen kommen aus einer **geschlossenen Wertemenge** — sechzehn Namen. Ein Wert wie `["reflexion"` gehört ihr nicht an, und das ist maschinell in einer Zeile feststellbar.

Nur: **die Obermenge existiert nicht als Konstante.** `MODUS_KANON` und `EMOTION_KANON` gibt es, `INTENT_KANON` nicht. Die einzige verfügbare Mengenprüfung war die gegen `GV_INITIATIVE_FUEHREND`, also gegen eine Teilmenge — und ein Nichttreffer dort ist eine **gültige Aussage**: „keine führende Intention".

Damit waren zwei Sachverhalte auf dasselbe Ergebnis abgebildet:

| Sachverhalt | Prüfung gegen die Teilmenge | Prüfung gegen den Kanon |
|---|---|---|
| gültige, nicht führende Intention | kein Treffer | im Kanon → in Ordnung |
| Bruchstück eines Transportformats | kein Treffer | **nicht im Kanon → Defekt** |

Das unterscheidet diesen Fall von `default-wie-fehlschlag`. Dort fielen zwei Zustände auf **denselben Wert** (`[]`), und keine Ausgabeprüfung konnte sie trennen — der Informationsverlust lag vor jeder Validierung. Hier waren die Werte von Anfang an unterscheidbar. Es hat nur niemand hingesehen.

---

## 4. Die EVA-Sektion war vorhanden. Sie war leer.

Die alte Funktion, vollständig:

```python
    # ── Ausgabe-Verifikation ────────────────────
    return [teil.strip() for teil in roh.split(",") if teil.strip()]
```

Die Sektionsmarke stand da. Unter ihr stand ein `return`. **Die Form der Disziplin war erfüllt, die Substanz fehlte** — und weil die Marke da war, sah die Funktion bei jedem Lesen aus wie eine geprüfte.

Das ist die unangenehmste Zeile dieser Lesson: Eine Konvention, die durch eine Kommentarzeile erfüllbar ist, erzeugt genau diese Stelle. Ein leerer Abschnitt ist schlechter als kein Abschnitt, weil er die Prüfung vortäuscht.

---

## 5. Die Regel

> **Wird aus einer Teilmengen-Prüfung ein Wert abgeleitet, muss die Obermenge deklariert und geprüft sein.** Sonst ist ein unbekannter Wert von einem gültigen Nein nicht zu unterscheiden.

Konkret, in dieser Reihenfolge:

1. **Der Kanon existiert als Konstante.** Eine geschlossene Wertemenge ohne deklarierte Obermenge ist nicht validierbar.
2. **Zugehörigkeit zum Kanon wird an der Eingabegrenze geprüft**, nicht dort, wo der Wert benutzt wird. Ein Wert außerhalb des Kanons ist ein Defekt und wird geloggt — nicht als Negativinformation verrechnet.
3. **Ein leerer Wert und ein unbekannter Wert sind zwei Fälle.** Leer heißt „fehlend" und wird benannt. Unbekannt heißt „defekt" und wird laut gemeldet.
4. **Eine `Ausgabe-Verifikation`-Sektion, die nur ein `return` enthält, ist keine.** Das ist maschinell prüfbar und gehört in die Prüfstrecke.

---

## 6. Der Preis

Der Defekt hat nicht nur eine Messung verfälscht, er hat **zwei Befunde erzeugt, die keine waren** — und beide standen schon in der Chronik:

- **„98 % der Rohwerte sind negativ, und das ist eine Eigenschaft des Gesprächs."** Der Beleg dafür war, dass die Schiefe das Filtern des Korpus überlebte. Sie überlebte es, weil der Fehler in *jedem* Turn saß. Geparst sind es 57,6 %.
- **„Die Konstante `GV_INITIATIVE_SCHWELLE` beschreibt ihr eigenes Paar nicht mehr."** Sie erreichte κ 0,174. Geparst erreicht sie 0,320 gegen 0,383 der gesuchten Schwelle — und ist selbst die zweithäufigste über Zufallshalbierungen gefundene Schwelle.

Ein Defekt in der Eingabe erzeugt nicht falsche Zahlen, sondern **falsche Schlüsse mit Belegen**. Die Belege waren echt, die Rechnung war richtig, und die Aussage war trotzdem falsch. Das ist teurer als ein Absturz.

Was der Fix **nicht** verbessert hat: κ außerhalb der Stichprobe steht auf 0,260 gegen vorher 0,261. Der Defekt hat die Achse gestaucht, nicht ihr Signal verdeckt.
