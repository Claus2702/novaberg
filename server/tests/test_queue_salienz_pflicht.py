"""Tests: Ein Queue-Auftrag ohne Salienz entsteht gar nicht erst.

`shadow_queue_push` trug in seiner Signatur `prioritaet: float = 0.0`, und von
zwei Aufrufern uebergab genau einer den Wert:

    agents/kzg/queues.py   shadow_queue_push(… prioritaet=neue_salienz …)   uebergibt
    memory/kzg.py          shadow_queue_push(… kein prioritaet-Argument …)  uebergibt nicht

**Der Vorgabewert macht aus einem fehlenden Argument eine Zahl, die wie eine
gemessene aussieht.** Der Aufruf ist syntaktisch vollstaendig, an der
Aufrufstelle fehlt sichtbar nichts, und 0.0 ist ein gueltiger Salienzwert — er
unterschreitet nur jede Schwelle und sortiert den Auftrag an das Ende jeder
Rangfolge, ohne dass irgendwo eine Meldung entsteht.

Gemessen am 15.08.2026 um 13:52 UTC ueber 1036 Auftraege: **233 tragen 0.0, und
alle 233 sind `vertiefen`** — keine `recherche`, keine `nachfragen`. Beide
Pfade laufen unter derselben Bedingung und bilden dieselbe Intention auf
dieselbe Aufgabe ab; der einzige Unterschied ist das ausgelassene Argument.

Zeugen dieser Datei:
  * **Jeder Aufrufer uebergibt die Salienz.** Geprueft als Kriterium ueber den
    ganzen Baum, nicht als Aufzaehlung der beiden heute bekannten Stellen —
    sonst faellt der naechste Aufrufer durch dieselbe Luecke.
  * **Die Signatur traegt keinen Vorgabewert.** Ohne diesen zweiten Zeugen
    behebt der erste nur die Aufrufer von heute: Ein Vorgabewert bleibt eine
    Falle fuer jeden, der die Funktion spaeter benutzt.

Der Gegenstand ist `KANDIDATEN-PRIORITAET-STILLE-NULL` und zugleich die
Vorbedingung des Queue-Umzugs — das Schema aus `novaberg-queue-verfall_k.md`
erzwingt `salienz_absolut NOT NULL` ohne Vorgabewert.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import unittest
from pathlib import Path

from services.shadow_agent.utils import shadow_queue_push

# Die Serverwurzel — diese Datei liegt in `<wurzel>/tests/`.
SERVER_WURZEL: Path = Path(__file__).resolve().parent.parent

# Verzeichnisse, die kein Produktivcode sind und deshalb nicht mitzaehlen.
NICHT_PRODUKTIV: frozenset[str] = frozenset({"tests", "__pycache__"})


def _produktive_dateien() -> list[Path]:
    """Alle Python-Dateien des Servers ausserhalb der Testbaeume.

    **Ohne Leerpruefung, und das ist Absicht.** Findet der Scan nichts, ist der
    Zeuge blind — aber das gehoert als Zusicherung in den Test und nicht hier
    hinein, wo es eine Ausnahme waere, die niemand als rotes Ergebnis sieht.
    `test_kein_aufruf_ohne_prioritaet` prueft die Mindestzahl der Treffer.

    Vorbedingung: keine.
    Nachbedingung: Jeder Pfad liegt unter der Serverwurzel.
    """
    # ── Verarbeitung / Ausgabe ──────────────────
    return [
        pfad for pfad in SERVER_WURZEL.rglob("*.py")
        if not NICHT_PRODUKTIV & set(pfad.relative_to(SERVER_WURZEL).parts)
    ]


def _aufrufe_von(name: str) -> list[tuple[Path, int, ast.Call]]:
    """Findet jeden Aufruf der Funktion `name` im Produktivcode.

    Erfasst beide Schreibweisen — `name(...)` und `modul.name(...)` —, damit
    ein Aufrufer sich nicht durch einen qualifizierten Zugriff entzieht.

    Vorbedingung: keine — ein leerer Name liefert eine leere Liste, und die
    laesst den aufrufenden Zeugen an seiner Mindestzahl scheitern.
    Nachbedingung: Jeder Treffer traegt Datei, Zeile und den Aufrufknoten.
    """
    # ── Verarbeitung ────────────────────────────
    treffer: list[tuple[Path, int, ast.Call]] = []
    for pfad in _produktive_dateien():
        baum: ast.Module = ast.parse(pfad.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            ziel = knoten.func
            gerufen: str = (
                ziel.id if isinstance(ziel, ast.Name)
                else ziel.attr if isinstance(ziel, ast.Attribute)
                else ""
            )
            if gerufen == name:
                treffer.append((pfad, knoten.lineno, knoten))
    return treffer


class JederAufruferUebergibtDieSalienzTest(unittest.TestCase):
    """Kein Aufruf von `shadow_queue_push` laesst `prioritaet` aus."""

    def test_kein_aufruf_ohne_prioritaet(self) -> None:
        """Jeder Aufruf nennt `prioritaet` ausdruecklich."""
        aufrufe = _aufrufe_von("shadow_queue_push")

        self.assertGreaterEqual(
            len(aufrufe), 2,
            "Weniger als zwei Aufrufer gefunden — am 15.08.2026 waren es zwei "
            "(agents/kzg/queues.py, memory/kzg.py). Ein leerer oder zu kleiner "
            "Treffer heisst hier nicht 'alles sauber', sondern 'der Zeuge "
            "sucht falsch'.",
        )

        ohne: list[str] = [
            f"{pfad.relative_to(SERVER_WURZEL)}:{zeile}"
            for pfad, zeile, knoten in aufrufe
            if "prioritaet" not in {kw.arg for kw in knoten.keywords}
        ]

        self.assertEqual(
            ohne, [],
            f"Diese Aufrufe von shadow_queue_push uebergeben keine "
            f"`prioritaet` und erzeugen damit einen Auftrag, dessen Salienz "
            f"nie geschrieben wurde: {ohne}",
        )


class DieSignaturErzwingtDieSalienzTest(unittest.TestCase):
    """Ohne Vorgabewert kann das Argument nicht stillschweigend ausfallen."""

    def test_prioritaet_hat_keinen_vorgabewert(self) -> None:
        """`prioritaet` ist ein Pflichtargument."""
        parameter = inspect.signature(shadow_queue_push).parameters

        self.assertIn(
            "prioritaet", parameter,
            "Das Argument `prioritaet` fehlt in der Signatur — dann traegt der "
            "Auftrag seine Ausloese-Salienz ueberhaupt nicht mehr.",
        )
        self.assertIs(
            parameter["prioritaet"].default, inspect.Parameter.empty,
            f"`prioritaet` traegt den Vorgabewert "
            f"{parameter['prioritaet'].default!r}. Ein Vorgabewert macht aus "
            f"einem vergessenen Argument eine Zahl, die wie eine gemessene "
            f"aussieht — genau der Weg, auf dem 233 Auftraege eine 0.0 "
            f"bekamen.",
        )


if __name__ == "__main__":
    unittest.main()
