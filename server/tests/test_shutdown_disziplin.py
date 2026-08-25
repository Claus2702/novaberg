"""Jede im Lifespan angelegte Hintergrundaufgabe wird beim Herunterfahren angefasst.

Strukturzeuge ueber den AST von `main.py`, nicht ueber einen Lauf: Der Lifespan
laesst sich nicht ohne Datenbank, Redis und Modelldienst fahren, und genau
deshalb ist hier noch nie jemand hingesehen. Bis zum 25.08.2026 fehlte
`prompt_task` — die Aufgabe hinter der Eingangs-Queue — als einzige von vieren
im Shutdown, und aufgefallen ist es nur, weil ihre Variable nirgends gelesen
wurde.

Der Zeuge prueft die Bauart, nicht den Ablauf: Wer eine Aufgabe anlegt, muss
ihren Namen im Shutdown-Zweig wieder nennen. Ein neuer `create_task` ohne
Gegenstueck macht ihn rot, ohne dass jemand daran denken muss.
"""
import ast
import unittest
from pathlib import Path

MAIN = Path(__file__).resolve().parent.parent / "main.py"


def _lifespan_knoten(baum: ast.Module) -> ast.AsyncFunctionDef:
    """Die Lifespan-Funktion, in der die Aufgaben entstehen und enden."""
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.AsyncFunctionDef) and knoten.name == "lifespan":
            return knoten
    raise AssertionError("main.py traegt keine async def lifespan")


class ShutdownDisziplinTest(unittest.TestCase):

    def setUp(self) -> None:
        self.baum = ast.parse(MAIN.read_text(encoding="utf-8"))
        self.lifespan = _lifespan_knoten(self.baum)

    def _angelegte_aufgaben(self) -> set[str]:
        """Namen, an die im Lifespan ein `asyncio.create_task(...)` gebunden wird."""
        namen: set[str] = set()
        for knoten in ast.walk(self.lifespan):
            ziele: list = []
            if isinstance(knoten, ast.Assign):
                ziele = knoten.targets
            elif isinstance(knoten, ast.AnnAssign):
                ziele = [knoten.target]
            else:
                continue
            wert = knoten.value
            if not isinstance(wert, ast.Call) or not isinstance(wert.func, ast.Attribute):
                continue
            if wert.func.attr != "create_task":
                continue
            namen |= {z.id for z in ziele if isinstance(z, ast.Name)}
        return namen

    def _angefasste_namen(self) -> set[str]:
        """Namen, auf denen im Lifespan `.cancel()` oder ein `await` steht."""
        angefasst: set[str] = set()
        for knoten in ast.walk(self.lifespan):
            if isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Attribute) \
                    and knoten.func.attr == "cancel" and isinstance(knoten.func.value, ast.Name):
                angefasst.add(knoten.func.value.id)
            elif isinstance(knoten, ast.Await):
                for k in ast.walk(knoten):
                    if isinstance(k, ast.Name):
                        angefasst.add(k.id)
        return angefasst

    def test_der_zeuge_findet_die_aufgaben_ueberhaupt(self) -> None:
        """Ohne diesen Zeugen waere eine leere Menge stille Zustimmung."""
        aufgaben = self._angelegte_aufgaben()
        self.assertGreaterEqual(
            len(aufgaben), 4,
            f"Nur {len(aufgaben)} Aufgaben erkannt ({sorted(aufgaben)}) — "
            "entweder ist main.py umgebaut oder der Zeuge sieht daneben",
        )

    def test_jede_angelegte_aufgabe_wird_beim_herunterfahren_angefasst(self) -> None:
        """Eine Aufgabe ohne Gegenstueck laeuft weiter, bis der Prozess stirbt."""
        offen = self._angelegte_aufgaben() - self._angefasste_namen()
        self.assertEqual(
            offen, set(),
            f"Im Lifespan angelegt, im Shutdown nie angefasst: {sorted(offen)}",
        )


if __name__ == "__main__":
    unittest.main()
