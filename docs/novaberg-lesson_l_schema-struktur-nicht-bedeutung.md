# Novaberg — Lesson: Schema-Audit liest Struktur, nicht Bedeutung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Ein Schema zeigt die Struktur einer Tabelle, die Bedeutung lebt im Schreibpfad
**Stand:** 21. Juni 2026, Chat 99
**Pfad:** novaberg/docs/novaberg-lesson_l_schema-struktur-nicht-bedeutung.md
**Kategorie:** Architektur — Audit-Disziplin bei Schema-Migrationen
**Schwester-Lessons:** `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_code-vor-doku.md`
**Konzept-Bezug:** `novaberg-memory-synapsen_k.md` (§4.2 — Richtungssemantik der Kanten)
**Handbuch-Bezug:** `DEVELOPER_HANDBOOK.md` §1 EVA-Disziplin (Plausibilität vor Verarbeitung)

---

## 1. Der Vorfall

Der P5-Lesepfad-Umbau (Chat 99) brauchte ein klares Bild der Kanten-Tabelle `lzg_kanten`, bevor der Spreading-Lesepfad gegen sie gebaut werden konnte. Ein früher Schema-Audit lieferte eine saubere Antwort: aus dem `CREATE TABLE` — zwei symmetrisch benannte Spalten `knoten_a_id` und `knoten_b_id`, ein `UNIQUE (knoten_a_id, knoten_b_id)`, kein Richtungsfeld, je ein Index auf beiden Knoten-Spalten — las der Audit die Tabelle als **ungerichtet, keine Mirror-Normalisierung**. Die Ableitung war aus der Struktur heraus korrekt: nichts im Schema verbietet die Gegenkante, nichts kennzeichnet eine Quelle und ein Ziel.

Auf dieser Annahme baute der erste Entwurf der Traversierung: `WHERE knoten_a_id = X OR knoten_b_id = X`, der Nachbar je nach Match-Seite mal `knoten_a_id`, mal `knoten_b_id` — eine beidseitige, ungerichtete Suche.

Sie war falsch.

Eine Datenabfrage gegen die Live-DB zeigte zunächst etwas, das die Annahme zu stützen schien: zu jeder Zeile `(a=X, b=Y)` existierte eine Zeile `(a=Y, b=X)` — 198 von 198 Kanten hatten eine Gegenzeile. Das sah nach Spiegeln aus, also nach einem ungerichteten Modell, das beide Richtungen redundant ablegt. Eine zweite, genauere Abfrage brachte den Riss: die Gewichte der zwei Richtungen unterschieden sich. In 184 von 198 Gegenpaaren trug `gewicht_absolut` der Hin-Richtung einen anderen Wert als die Rück-Richtung — klein, oft im Promille-Bereich, aber real.

Erst der **Schreibpfad-Code** entschied die Frage. `memory/lzg_kanten.py` `_kante_upsert` ist im Docstring unmissverständlich: „Schreibt eine **gerichtete** Kante (A→B)." Pro Knotenpaar setzt `kanten_fuer_neuen_knoten_bilden` **zwei** getrennte Inserts ab — einen für A→B, einen für B→A — mit den zwei Werten eines einzigen `kanten_staerke_berechnen`-Aufrufs, der ein Tupel `(roh_ab, roh_ba)` liefert. Beide Werte sind am schwächeren Anker verankert, aber weil die Zieh-Faktoren `ZIEH_HOCH` und `ZIEH_RUNTER` verschieden sind, fallen die zwei Richtungen unterschiedlich aus. Die Tabelle ist **gerichtet**. Die zwei Zeilen sind keine Spiegel, sondern zwei Assoziationsrichtungen mit eigener Stärke.

## 2. Die Ursache

Der Schema-Audit war kein Fehler. Er hat exakt das gelesen, was im Schema stand — und das Schema trägt die Richtungssemantik nicht. `knoten_a_id`/`knoten_b_id` sind eine reine Positions-Konvention: dass die erste Spalte „Quelle" und die zweite „Ziel" bedeutet, ist eine Vereinbarung des Schreibpfads, kein Constraint. Ein `UNIQUE (a, b)` sperrt nur exakte Duplikate je Richtung, nicht die Gegenkante — strukturell sieht das aus wie ein ungerichtetes Modell, das zufällig beide Richtungen führt.

Die Bedeutung — *was eine Zeile ist* — lebte nicht im Schema, sondern im Code, der die Tabelle befüllt: in der Berechnung, die zwei asymmetrische Gewichte erzeugt, und in den zwei gerichteten Inserts. Ohne diesen Code ist die Frage „gerichtet oder gespiegelt?" aus Struktur **und** Daten allein nicht sicher zu beantworten. Die Daten waren sogar zweifach mehrdeutig: die bloße Existenz der Gegenzeile sah nach Spiegel aus, und die kleine Gewichts-Differenz konnte zweierlei sein — designte Asymmetrie oder numerisches Artefakt (etwa ein Decay-Zeitversatz zwischen zwei Schreibvorgängen). Nur die Berechnungs-Formel im Schreibpfad trennte die beiden Deutungen: ein einziger `kanten_staerke_berechnen`-Aufruf, ein konsistenter Snapshot, zwei bewusst verschiedene Richtungswerte — also Design, kein Artefakt.

Hätte der Lesepfad auf der Schema-Annahme „ungerichtet" weitergebaut, hätte Nova **rückwärts** assoziiert: die beidseitige Suche hätte eingehende Kanten als Ausgangspunkte mitgezogen, die Gegenzeile mit der jeweils anderen Stärke verwechselt, und die Vorgänger-Sperre hätte über eine Kanten-`id` versucht zu sperren, was im gerichteten Modell zwei verschiedene Zeilen sind. Aus „von Anna assoziiere ich Schokolade" wäre unbemerkt „von Schokolade assoziiere ich Anna" geworden — mit der falschen Stärke gewichtet.

## 3. Die Faustregeln

- **Schema sagt, WAS für Spalten existieren, nicht WAS sie bedeuten.** Bei mehrdeutiger Struktur — gespiegelte oder doppelte Zeilen, Positions-Konventionen wie „erste Spalte = Quelle", Soft-Delete-Flags, Typ-Marker — entscheidet der **Schreibpfad**, nicht das Schema, was eine Zeile semantisch ist.
- **Schreibpfad vor Lesepfad lesen.** Bevor man einen Konsumenten gegen eine Tabelle baut, liest man, wie die Tabelle **befüllt** wird. Der schreibende Code ist die Quelle der Wahrheit über die Bedeutung der Daten; der lesende Code, der auf einer Annahme darüber sitzt, vererbt jeden Irrtum der Annahme.
- **Daten allein reichen nicht.** Eine 0,1-%-Differenz zwischen zwei Zeilen kann „designte Asymmetrie" oder „numerisches Artefakt" sein. Ein Muster in den Daten (jede Zeile hat eine Gegenzeile) kann „Spiegel" oder „zwei Richtungen" sein. Nur die Berechnungs- und Insert-Logik im Schreibpfad unterscheidet die Fälle — eine Stichprobe der Werte beantwortet die Frage nicht.
- **Die Antwort gehört ins Schema-Dokument zurück.** War die Bedeutung nur im Code, ist das eine Doku-Lücke. Sobald der Schreibpfad die Frage geklärt hat, wird die Semantik (hier: „Kanten sind gerichtet, `knoten_a_id` = Quelle") explizit ins Schema-Konzept geschrieben, damit der nächste Audit sie nicht erneut erschließen muss.

## 4. Das Prinzip

### Bedeutung lebt im Schreibpfad, nicht in der Struktur

Ein Schema-Audit erfasst die **Form** einer Tabelle — Spalten, Typen, Constraints, Indizes — vollständig und korrekt. Es erfasst die **Bedeutung** nur dort, wo die Struktur sie erzwingt: ein `NOT NULL`, ein `CHECK`, ein `FOREIGN KEY` tragen Semantik im Schema. Alles, was nur Konvention ist — welche Spalte die Quelle ist, ob zwei Zeilen Spiegel oder Richtungen sind, ob ein `gewicht`-Wert frei wächst oder gedämpft ist — lebt im Code, der schreibt.

Wer einen Konsumenten gegen eine Tabelle baut, braucht beide Lesungen: das Schema für die Form und den Schreibpfad für die Bedeutung. Die erste Lesung kostet Minuten und liefert ein plausibles, oft falsches Bild. Die zweite kostet Minuten mehr und liefert das richtige. Im `lzg_kanten`-Fall war der Unterschied zwischen den beiden Lesungen der Unterschied zwischen „Nova assoziiert vorwärts" und „Nova assoziiert rückwärts" — kein Detail, sondern die Kern-Mechanik des Lesepfads.

## 5. Die Konsequenz

**Erstens:** Die Richtungssemantik der Kanten steht jetzt explizit im Schema-Konzept (`novaberg-memory-synapsen_k.md` §4.2): `knoten_a_id` = Quelle, `knoten_b_id` = Ziel, zwei Zeilen je Paar mit asymmetrischen Gewichten, Spreading folgt nur ausgehenden Kanten, Vorgänger-Sperre knoten-basiert. Der nächste Audit liest sie aus dem Konzept, nicht aus dem Code.

**Zweitens:** Der Lesepfad wurde korrigiert, bevor er live ging — die Traversierung folgt nur noch ausgehenden Kanten (`WHERE knoten_a_id = X`, Nachbar = `knoten_b_id`), die Vorgänger-Sperre sperrt den Vorgänger-**Knoten** als Rücksprung-Ziel statt eine Kanten-`id`. Der Irrtum hat eine Audit-Runde gekostet, aber keinen falschen Live-Zustand.

**Drittens:** Diese Lesson ist Archiv. Wer künftig eine Tabelle mit Positions-Konventionen oder gespiegelt wirkenden Zeilen vor sich hat, liest hier nach, warum die Daten-Stichprobe nicht genügt und der Schreibpfad die Bedeutung trägt.

## 6. Verwandtschaft

Diese Lesson reiht sich neben zwei ältere, die denselben Kern aus anderen Winkeln treffen:

- **`novaberg-lesson_l_pattern-vor-namen-suche.md`** — bei Audits das Aufruf-**Pattern** suchen, nicht nur den Wrapper-Namen. Dort ging es um das vollständige Erfassen einer Schicht über ihr Verhalten statt ihren Namen; hier um das Erfassen einer Tabelle über ihren Schreibpfad statt ihre Struktur. Beide Male trägt der oberflächliche Indikator (Name, Schema) nicht die ganze Wahrheit.
- **`novaberg-lesson_l_code-vor-doku.md`** — der Live-Code schlägt Doku und Erinnerung. Hier schlägt der Schreibpfad-Code die plausible Schema-Lesung. Dieselbe Hierarchie: was der Code *tut*, gilt; was Struktur, Doku oder Annahme *nahelegen*, ist nachrangig und muss am Code verifiziert werden.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_code-vor-doku.md`
→ Konzept-Dokument: `novaberg-memory-synapsen_k.md` (§4.2 — Richtungssemantik der Kanten)
→ Handbuch-Bezug: `DEVELOPER_HANDBOOK.md` §1 EVA-Disziplin
