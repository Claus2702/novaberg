# NachfragenAgent

Legt bei erkanntem Druck einen Zuwendungs-Reiz auf den Shadow-Stack. Er bringt Zuwendung, keinen Inhalt — als einziger Modus, den die Zustellung in negativen Phasen durchlässt.

## Trigger

- Queue-Auftrag `aufgabe: nachfragen`, erzeugt aus Intention `hilferuf` oder aus dem Emotionsvektor-Pfad des Routers (`absturz`, `spirale`, `einbruch`).

## Ablauf

1. Jüngsten annotierten User-Turn aus der Session lesen — der Druck wird **frisch** gelesen, nicht dem Auftrag entnommen.
2. Vektor gegen den Kanon prüfen, dann gegen die Druck-Teilmenge.
3. Kein Druck → kein Stapel-Eintrag, Audit `erledigt` mit Grund.
4. Druck → Lage und Anlass deterministisch zum Reiz verdichten (`ei/farbton.py::lage_beschreiben`).
5. Reiz → Shadow-Stack (`stack_push`, `aufgabe="nachfragen"`).

## Besonderheiten

- **Kein Modellaufruf.** Der Farbton spricht bereits im Zielregister; ein Hintergrundaufruf kostet hier 35–38 s am einzigen seriellen Platz.
- **Kein KZG-, Bibliotheks- oder Ziel-Schreiben** — es entsteht kein Wissen, nur ein Reiz aus bereits gespeicherten Größen.
- **`aufgabe="nachfragen"` ist Pflicht:** Die Zustellung vergleicht genau diese Zeichenkette und lässt bei negativen Emotionen nur sie durch.
- **Der Agent schweigt nicht selbst.** Über das *Ob* entscheidet die Zustellung, über die Form der CharacterGraph.
- „Kein Druck mehr" ist `erledigt`, nicht `fehler` — der häufigste Ausgang bei einem alten Auftrag.
