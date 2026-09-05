# Novaberg — Lesson: Eine behobene Fehlerklasse steht an ihrer zweiten Stelle weiter

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Wer den gefundenen Fall repariert, hat die Klasse nicht behoben
**Stand:** 5. September 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_zweite-fundstelle-nach-behebung.md
**Typ:** Lesson (L)
**Auslöser:** `FADEN-EMBEDDING-VERDUENNT` — behoben am 01.09.2026, dieselbe Klasse zwanzig Zeilen tiefer bis zum 05.09.2026
**Verwandt:** `novaberg-lesson_l_pattern-vor-namen-suche.md` · `novaberg-lesson_l_groesse-am-falschen-ort.md`

---

## 1. Der Vorfall

Am 01.09.2026 wurde `FADEN-EMBEDDING-VERDUENNT` behoben: Der Prägungsfaden trug den Vektor des
**ganzen Turns**, während Salienz und Emotion desselben Fadens aus dem **stärksten Segment** kamen —
ausgewählt mit der ausdrücklichen Begründung, ein Mittel verdünne den einschneidenden Satz.

Die Behebung war sauber. `_faden_embedding()` bettet seither den Segmenttext ein, der Rückfall wird
protokolliert, ein Zeuge hält es. Der Eintrag zog ins Archiv und trug dort sogar die allgemeine
Fassung des Fehlers:

> *„Wo eine Begründung für **eine** von mehreren Eigenschaften desselben Objekts formuliert wird,
> gilt sie meist für alle — und die übrigen werden nicht mitgezogen."*

**Vier Tage später stand genau das im selben Modul.** Der **Prägungszug** las weiterhin
`state["prompt_embedding"]`. Ein Turn über zwei Themen bekommt einen Vektor zwischen beiden und
liegt danach keinem der zugehörigen Stränge nahe — die Nähe eines Mittelwerts ist keine Nähe.

Die Begründung, warum das falsch ist, stand seit dem 01.09. **zwanzig Zeilen über der Stelle, die
sie ignorierte.**

---

## 2. Warum es niemand fand

**Nicht aus Nachlässigkeit, sondern weil die Prüfungen anderswo hinsehen.**

- **Die Zeugen des Fadens** waren grün — der Faden war ja repariert.
- **Die Zeugen des Zugs** waren grün — er rechnete korrekt auf dem Vektor, den er bekam.
- **Die Gegenprobe** traf nur, was eine Zusicherung schon behauptet — und keine behauptete etwas über die Herkunft des Vektors.
- **Der Bug-Eintrag** war geschlossen und im Archiv. Was geschlossen ist, wird nicht durchsucht.

Gefunden hat es eine **Frage des Eigentümers**: *„Wenn mehrere Sätze mit verschiedenen Themen
kommen, wie wollen wir dann die Nähe zum Strang ausrechnen?"*

---

## 3. Das Prinzip

> **Wer einen Defekt behebt, sucht die zweite Stelle derselben Klasse — im selben Modul zuerst.**

Der Suchbegriff ist nicht der Defektname und nicht die reparierte Funktion, sondern **die Quelle des
falschen Werts**. Hier: ein Grep auf `prompt_embedding` über die Datei, in der gerade repariert
wurde. Er hätte die zweite Stelle in Sekunden gezeigt.

**Das ist derselbe Gedanke wie `pattern-vor-namen-suche`, an einem anderen Zeitpunkt.** Dort geht es
um den *Audit vor* dem Umbau: Muster suchen statt Namen. Hier um den Moment *nach* der Behebung —
und der ist gefährlicher, weil das Erfolgserlebnis die Suche beendet.

---

## 4. Die Konsequenz

**Bei jeder Behebung ein Grep auf die Quelle des falschen Werts**, mindestens über die geänderte
Datei, besser über das Modul. Die drei Zahlen gehören in den Bericht: Fundstellen, behandelte, mit
Grund verworfene.

**Und der Bug-Eintrag trägt die Reichweite der Behebung.** *„Behoben"* ohne Angabe, **wo gesucht
wurde**, liest sich wie *„die Klasse ist erledigt"* — und genau so ist dieser Eintrag vier Tage lang
gelesen worden.

---

## 5. Der Preis

Vier Tage, in denen der Prägungszug auf verdünnten Vektoren rechnete — und damit jede Zahl, die aus
ihm folgte. Der Schaden blieb klein, weil der Zug in dieser Zeit keinen Leser hatte; hätte er einen
gehabt, wäre die Faszination auf einer Größe kalibriert worden, die systematisch zu niedrig lag.

**Der Gegenaufwand ist ein Grep.**

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht
diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Defektregister: `novaberg-bugs-archiv.md`, `FADEN-EMBEDDING-VERDUENNT` (dort als `[2×]`)
→ Moduldokument: `novaberg-node-praegung.md` §6c
