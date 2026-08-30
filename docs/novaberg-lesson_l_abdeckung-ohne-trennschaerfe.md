# Novaberg — Lesson: Abdeckung ist kein Beleg für Trennschärfe

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Ein gefülltes Feld ist noch kein Schlüssel
**Stand:** 30. August 2026
**Pfad:** novaberg/docs/novaberg-lesson_l_abdeckung-ohne-trennschaerfe.md
**Typ:** Lesson (`_l`) — Archiv, wird nicht gekürzt
**Auslöser:** Suche nach einer Gruppierungsachse für die Qualitäts-Schicht; drei Felder geprüft, drei ausgeschieden
**Verwandt:** `novaberg-lesson_l_gelesen-ist-nicht-wirksam.md` · `novaberg-convention-magneten.md` · `novaberg-thinking-faszination_k.md` §5

---

## 1. Die Fehlerklasse

Ein Feld wird als Schlüssel oder Gruppierungsmerkmal verwendet. Geprüft wird, ob es gefüllt
ist. Nicht geprüft wird, ob seine Werte sich wiederholen.

> **Ein Zähler auf *„wie viele Zeilen haben einen Wert"* sieht nicht, ob es 8.000
> verschiedene Werte auf 12.000 Nennungen sind.**

Die Abdeckung misst, ob geschrieben wurde. Ein Schlüssel muss etwas anderes können: **zwei
Zeilen zusammenführen.** Das eine folgt aus dem anderen nicht.

---

## 2. Der Fund

Bei der Suche nach einer Gruppierungsachse für die Qualitäts-Schicht wurden drei Felder
geprüft. Alle drei fielen aus demselben Grund durch — und das am besten gefüllte war der
schärfste Fall.

**Alle Zahlen `[gemessen]` 30.08.2026 über 3.266 `lzg_knoten`.**

| Feld | Abdeckung | verschiedene Werte | Nutzungen je Wert |
|---|---:|---:|---:|
| `lzg_knoten.themen` | **84,7 %** | 8.097 auf 12.044 Nennungen | **1,49** |
| Sachlage-Eigenschaften | — | 139 auf 335 Nennungen | 2,41 |
| `prompt_topic` | hoch | Freitext, laufzeitungeprüft | — |

`themen` ist die am besten gefüllte der drei Magnetachsen — besser als `entitaet_ids`
(20,8 %) und `timeline_id` (4,4 %). **In jeder Abdeckungsprüfung glänzt es. Als
Gruppierungsschlüssel ist es wertlos.**

### 2.1 Die Zahl, die es entscheidet, ist nicht der Mittelwert

`1,49 Nutzungen je Wert` ist bereits ein schlechter Wert. Die Verteilung dahinter ist
schlechter, als der Mittelwert aussehen lässt:

| | Werte | Anteil |
|---|---:|---:|
| kommen **genau einmal** vor | 6.631 | **81,9 %** |
| kommen mehrfach vor | 1.466 | 18,1 % |

Der meistgenutzte Wert steht 99-mal — er allein hebt den Mittelwert spürbar, während vier
Fünftel des Vokabulars nichts gruppieren. **117 Werte sind länger als 60 Zeichen**: ganze
Sätze, teils mit unbalancierten Klammern.

> **Ein Mittelwert über eine Verteilung mit langem Schwanz beschreibt keinen einzigen ihrer
> Fälle.** Wer die Trennschärfe wissen will, zählt den Anteil der Einzelstücke.

---

## 3. Die Regel

**Wer ein Feld als Schlüssel verwenden will, zählt drei Zahlen, nicht eine:**

1. die **Abdeckung** — wie viele Zeilen tragen einen Wert,
2. die **Zahl verschiedener Werte** — und ihr Verhältnis zur Zahl der Nennungen,
3. den **Anteil der Werte, die genau einmal vorkommen**.

Erst die dritte sagt, ob das Feld gruppieren kann. Die erste allein sagt es nie.

**Und ein offenes Textfeld wird nie ein Schlüssel.** Dieselbe Sache bekommt drei
Schreibweisen, und keine Migration holt das zurück.

---

## 4. Die Kennzahl kann selbst zwei Populationen verdecken

Die Sachlage-Zeile oben trägt **2,41** — der beste Wert der drei. Er entsteht aus zwei
Feldern mit gegensätzlicher Bauart, die in der Auswertung zusammengeworfen wurden:

| Teilmenge | Nennungen | verschieden | je Wert | was sie ist |
|---|---:|---:|---:|---|
| `gedeckt` | 230 | 75 | **3,07** | beantwortete Eigenschaften |
| `offen` | 105 | 87 | **1,21** | offene Wissenslücken |

**Die 3,07 sind der beste gemessene Wert im ganzen Vergleich; die 1,21 der zweitschlechteste.**
Ihr gemeinsamer Mittelwert 2,41 beschreibt keine von beiden — und hätte die eine brauchbare
Teilmenge mit der unbrauchbaren zusammen aussortiert.

> **Dieselbe Fehlerklasse eine Ebene höher:** Nicht nur ein Feld kann Abdeckung ohne
> Trennschärfe haben, sondern auch die Kennzahl, mit der man Felder vergleicht. **Wer
> aggregiert, prüft zuerst, ob er eine Population vor sich hat.**

---

## 5. Seitenbefund: die Themen-Kanten stehen auf schmalerer Grundlage

`[gemessen]` 30.08.2026 über 495.610 `lzg_kanten` — eine Kante kann mehrere Gründe tragen,
die Anteile summieren sich deshalb über 100 %:

| Verbindungsgrund | Kanten | Anteil |
|---|---:|---:|
| `embedding` | 465.350 | 93,9 % |
| `themen` | 36.706 | **7,4 %** |
| `timeline` | 6.652 | 1,3 % |
| `entitaet` | 3.078 | 0,6 % |

Bei 1,49 Nutzungen je Themenwert hängen diese 7,4 % **an der Minderheit der
Mehrfachnennungen** — an den 18,1 % des Vokabulars, die überhaupt zweimal vorkommen. Kein
Widerspruch, aber die Zahl beschreibt eine schmalere Grundlage, als sie vermuten lässt.

> **Berichtigt gegenüber dem ersten Entwurf:** Dort standen 10,9 % Themen-Kanten. Gemessen
> sind es 7,4 %. Der Schluss ändert sich nicht, die Zahl schon.

---

## 6. Wo die Klasse sonst noch sitzt

- **Eine Stichprobe über `ORDER BY random()` mit `setseed` ist nicht reproduzierbar, wenn
  der Bestand wächst.** Dieselbe Saat zog am 30.08.2026 vormittags 202 Themen-Nennungen und
  nachmittags 191 — der Korpus war um fünf Knoten gewachsen. Für eine Aussage über den
  Bestand ist die **Korpuszahl** zu nehmen, nicht die Stichprobe; die Stichprobe taugt für
  die Form der Werte, nicht für ihre Verteilung.
- **`prompt_topic`** trägt dieselbe Bauart und ist laufzeitungeprüft. Es steht als
  Modulator-Kandidat der Faszination ausdrücklich nicht zur Verfügung.
