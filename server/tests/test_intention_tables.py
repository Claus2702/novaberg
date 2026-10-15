"""Tests fuer die beiden Intention-Aufgabe-Tabellen der KZG.

Ziel: Eine Bestaetigung des Nutzers ueber einer hohen Salienz erzeugt in beiden
Pfaden keinen Auftrag, und jede Intention des Kanons (`INTENT_KANON`) steht in
beiden Tabellen in der Schreibweise des Kanons.

Hintergrund: `memory/kzg.py` fuehrte `"bestätigung"` (mit Umlaut), der Kanon
`"bestaetigung"`. Beide Tabellen fallen bei einem unbekannten Schluessel auf den
Vorgabewert `recherche` — eine Bestaetigung haette einen Recherche-Auftrag
erzeugt statt keinen. Eine Tippabweichung faellt so nie laut auf; deshalb
vergleicht jeder Zeuge die Schluessel mit dem Kanon.

Die Tabelle in `agents/kzg/queues.py` wird per `ast` gelesen: Ein Import des
Pakets `agents` oeffnet beim Laden den Verbindungspool. Die Tabelle in
`memory/kzg.py` wird importiert — wie in den anderen Zeugen der KZG.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path

from config import INTENT_KANON
from memory import kzg as kzg_module

QUEUES_PATH: Path = Path(__file__).resolve().parent.parent / "agents" / "kzg" / "queues.py"


class TableSourceError(AssertionError):
    """Die Tabelle ist in der Quelldatei nicht als nichtleeres Literal zu lesen."""

    def __init__(self, path: Path, name: str, reason: str) -> None:
        super().__init__(f"{name} in {path}: {reason}")


def _table_from_source(path: Path, name: str) -> dict[str, str]:
    """Liest eine Tabelle auf Modulebene als Literal, ohne das Modul zu laden.

    Vorbedingung: `name` ist auf Modulebene mit einem Dict-Literal belegt.
    Nachbedingung: das Dict ist nicht leer.
    Fehlerfall: Datei oder Tabelle fehlt — der Zeuge scheitert laut.
    """
    # ── Eingabe-Validierung ──
    if not path.is_file():
        raise TableSourceError(path, name, "Quelldatei fehlt")

    # ── Verarbeitung ──
    tree: ast.Module = ast.parse(path.read_text(encoding="utf-8"))
    table: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == name:
            table = ast.literal_eval(node.value)

    # ── Ausgabe-Verifikation ──
    if not table:
        raise TableSourceError(path, name, "fehlt oder ist leer")
    return table


class TestIntentionTables(unittest.TestCase):
    """Beide Tabellen tragen genau die Intentionen des Kanons."""

    def test_canon_is_not_empty(self) -> None:
        """Positiver Zwilling: Ein leerer Kanon machte die Mengenvergleiche leer."""
        self.assertGreater(len(INTENT_KANON), 0)
        self.assertIn("bestaetigung", INTENT_KANON)

    def test_memory_table_has_exactly_the_canon_keys(self) -> None:
        keys: set[str] = set(kzg_module._INTENTION_AUFGABE_MAP)
        self.assertEqual(set(), INTENT_KANON - keys, "im Kanon, nicht in der Tabelle")
        self.assertEqual(set(), keys - INTENT_KANON, "in der Tabelle, nicht im Kanon")

    def test_queues_table_has_exactly_the_canon_keys(self) -> None:
        table: dict[str, str] = _table_from_source(QUEUES_PATH, "_INTENTION_AUFGABE_MAP")
        keys: set[str] = set(table)
        self.assertEqual(set(), INTENT_KANON - keys, "im Kanon, nicht in der Tabelle")
        self.assertEqual(set(), keys - INTENT_KANON, "in der Tabelle, nicht im Kanon")

    def test_confirmation_yields_no_task_in_memory(self) -> None:
        self.assertEqual("", kzg_module._aufgabe_aus_intention(["bestaetigung"]))

    def test_confirmation_yields_no_task_in_queues(self) -> None:
        table: dict[str, str] = _table_from_source(QUEUES_PATH, "_INTENTION_AUFGABE_MAP")
        self.assertEqual("", table["bestaetigung"])

    def test_unknown_intention_still_falls_back_to_recherche(self) -> None:
        """Zwilling: Der Vorgabewert bleibt, sonst prueft der Zeuge oben nichts."""
        self.assertEqual("recherche", kzg_module._aufgabe_aus_intention(["gibt_es_nicht"]))

    def test_both_tables_agree_on_the_tasks(self) -> None:
        table: dict[str, str] = _table_from_source(QUEUES_PATH, "_INTENTION_AUFGABE_MAP")
        self.assertEqual(kzg_module._INTENTION_AUFGABE_MAP, table)


if __name__ == "__main__":
    unittest.main()
