"""Zeugen ueber den Emotions-Riegel der Zustellung und seinen Kanon.

Ziel: `_emotional_kompatibel` entscheidet, ob ein Impuls hinausgeht, waehrend
der Mensch etwas fuehlt. Bis zum 23.08.2026 stand die Menge der negativen
Emotionen **zweimal** — acht abgeleitet in `ei/utils.py`, vier als Literal in
`services/shadow_delivery.py`. Die zweite war eine echte Teilmenge, und der
Riegel benutzte sie: `wut`, `verzweiflung` und `enttaeuschung` fielen auf den
Schlusszweig *alle anderen Kombinationen: erlaubt*.

Die Zusicherungen:

  1. **Jede negative Emotion laesst nur die Nachfrage durch.** Der Zeuge zaehlt
     nicht vier Namen auf, sondern laeuft ueber `NEGATIVE_EMOTIONEN` — eine
     spaeter ergaenzte Emotion ist damit sofort mitgeprueft und nicht erst,
     wenn jemand die Liste hier nachzieht.
  2. **Stress laesst gar nichts durch**, auch keine Nachfrage. Er steht in den
     acht und wird trotzdem vorher geprueft; die Reihenfolge traegt den
     Unterschied.
  3. **Positive Emotionen sperren nicht.** Sonst waere die Zusicherung 1 auch
     mit einem Riegel erfuellt, der alles sperrt.
  4. **`NEGATIVE_EMOTIONEN` ist im Produktivbaum einmal definiert.** Die
     Behebung war das Entfernen eines Literals; ohne diesen Zeugen kehrt es
     beim naechsten Mal zurueck, ohne dass ein Werkzeug es meldet. Ruffs
     `F811` sieht nur dieselbe Datei, und der bestehende Struktur-Zeuge
     (`test_config_struktur.py`) ebenfalls — dieser Fall lag ueber zwei
     Module verteilt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import os
import unittest
from pathlib import Path

from ei.utils import NEGATIVE_EMOTIONEN, POSITIVE_EMOTIONEN
from services.shadow_delivery import _emotional_kompatibel

#: Die Wurzel des Produktivbaums; `tests/` steht nicht darin.
SERVER: Path = Path(__file__).resolve().parent.parent

#: Die einzige Aufgabe, die ein Impuls unter einer negativen Emotion tragen
#: darf. Steht hier als Name und nicht als Zeichenkette im Test, damit eine
#: Umbenennung an einer Stelle auffaellt.
EMPATHISCHE_AUFGABE: str = "nachfragen"

#: Ein Gegenbeispiel — eine Aufgabe, die unter einer negativen Emotion nicht
#: hinausgehen darf.
SACHLICHE_AUFGABE: str = "recherche"


def _definitionsorte(name: str) -> list[str]:
    """Nennt jede Modulebenen-Zuweisung dieses Namens im Produktivbaum.

    Vorbedingung: `name` ist ein Bezeichner.
    Nachbedingung: Liste aus `pfad:zeile`, leer wenn der Name nirgends auf
    Modulebene zugewiesen wird. Ein Import zaehlt nicht — er bindet den Namen,
    erklaert ihn aber nicht, und genau das ist die gewuenschte Bauart.
    """
    orte: list[str] = []
    for pfad in sorted(SERVER.rglob("*.py")):
        text: str = str(pfad)
        if "__pycache__" in text or f"{os.sep}tests{os.sep}" in text:
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8"))
        for knoten in baum.body:
            if isinstance(knoten, ast.Assign):
                ziele: list[ast.expr] = list(knoten.targets)
            elif isinstance(knoten, ast.AnnAssign):
                ziele = [knoten.target]
            else:
                continue
            for ziel in ziele:
                if isinstance(ziel, ast.Name) and ziel.id == name:
                    orte.append(f"{pfad.relative_to(SERVER)}:{knoten.lineno}")
    return orte


class EmotionsriegelTest(unittest.TestCase):
    """Was der Riegel bei welcher Emotion durchlaesst."""

    def test_jede_negative_emotion_laesst_nur_die_nachfrage_durch(self) -> None:
        """Der Fall, den das Literal mit vier Namen durchliess.

        Vor dem 23.08.2026 rot fuer `wut`, `verzweiflung`, `enttaeuschung`:
        Sie standen nicht in der lokalen Fassung und fielen auf *erlaubt*.
        """
        self.assertGreaterEqual(
            len(NEGATIVE_EMOTIONEN), 8,
            "Der Kanon muss die negativen Emotionen wirklich fuehren",
        )
        durchgelassen: list[str] = [
            emotion for emotion in sorted(NEGATIVE_EMOTIONEN)
            if _emotional_kompatibel(SACHLICHE_AUFGABE, emotion)
        ]
        self.assertEqual(
            durchgelassen, [],
            f"Sachlicher Impuls trotz negativer Emotion zugelassen: {durchgelassen}",
        )

    def test_die_nachfrage_darf_bei_negativer_emotion_hinaus(self) -> None:
        """Sonst waere Zusicherung 1 auch von einem Riegel erfuellt, der sperrt.

        Ausgenommen ist `stress`: Dort ist auch die Nachfrage zu viel, und das
        ist der Gegenstand des naechsten Zeugen.
        """
        gesperrt: list[str] = [
            emotion for emotion in sorted(NEGATIVE_EMOTIONEN)
            if emotion != "stress"
            and not _emotional_kompatibel(EMPATHISCHE_AUFGABE, emotion)
        ]
        self.assertEqual(
            gesperrt, [],
            f"Empathische Nachfrage gesperrt bei: {gesperrt}",
        )

    def test_stress_laesst_auch_die_nachfrage_nicht_durch(self) -> None:
        """Die Reihenfolge im Riegel traegt diese Unterscheidung.

        `stress` steht in `NEGATIVE_EMOTIONEN`. Wer die Stress-Pruefung hinter
        die Kanon-Pruefung schoebe, liesse die Nachfrage durch — der Zeuge wird
        genau dann rot.
        """
        self.assertIn("stress", NEGATIVE_EMOTIONEN)
        self.assertFalse(_emotional_kompatibel(EMPATHISCHE_AUFGABE, "stress"))
        self.assertFalse(_emotional_kompatibel(SACHLICHE_AUFGABE, "stress"))

    def test_positive_emotion_sperrt_nicht(self) -> None:
        """Die Gegenprobe zur Sperre: Bei guter Lage geht der Impuls hinaus."""
        gesperrt: list[str] = [
            emotion for emotion in sorted(POSITIVE_EMOTIONEN)
            if not _emotional_kompatibel(SACHLICHE_AUFGABE, emotion)
        ]
        self.assertEqual(
            gesperrt, [],
            f"Impuls trotz positiver Emotion gesperrt: {gesperrt}",
        )


class KanonquelleTest(unittest.TestCase):
    """Der Zeuge gegen die Rueckkehr des Literals."""

    def test_negative_emotionen_ist_einmal_definiert(self) -> None:
        """Zwei Mengen fuer einen Gegenstand sind der Defekt, nicht die Zahl.

        Vor dem 23.08.2026 zwei Orte: `ei/utils.py` (abgeleitet, acht) und
        `services/shadow_delivery.py` (Literal, vier).
        """
        orte: list[str] = _definitionsorte("NEGATIVE_EMOTIONEN")
        self.assertEqual(
            len(orte), 1,
            f"`NEGATIVE_EMOTIONEN` an {len(orte)} Stellen definiert: {orte}",
        )
        self.assertTrue(
            orte[0].startswith("ei/utils.py"),
            f"Der Kanon gehoert nach `ei/utils.py`, steht aber in {orte[0]}",
        )

    def test_positive_emotionen_ist_einmal_definiert(self) -> None:
        """Dieselbe Zusicherung fuer die Gegenmenge.

        Sie steht hier, weil der Defekt nicht an *negativ* hing, sondern an der
        Bauart: Ein Verbraucher schreibt sich die Menge hin, statt sie zu holen.
        """
        orte: list[str] = _definitionsorte("POSITIVE_EMOTIONEN")
        self.assertEqual(
            len(orte), 1,
            f"`POSITIVE_EMOTIONEN` an {len(orte)} Stellen definiert: {orte}",
        )


if __name__ == "__main__":
    unittest.main()
