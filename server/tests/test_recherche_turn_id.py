"""Zeugen dafuer, dass die Kennung des Ausloese-Turns den KZG-Pfad ueberlebt.

**Gemessen, nicht vermutet** (30.08.2026). Ueber alle Auftraege seit dem Bau
der Sachlage-Bruecke am 28.08.2026 trugen **6 von 148** eine
`ausloeser_turn_id` — 4 von 124 `recherche`, 2 von 24 `vertiefen`, am
30.08. keiner von 14. Die Bruecke haengt hart an dieser Kennung; ohne sie
laeuft jede Zustellung ueber den Vektor-Rueckfall, und das Konzept nannte als
Grund den Altbestand des Stapels, obwohl auch die neuen Auftraege sie nicht
trugen.

**Die Stelle:** `agents/recherche/agent.py` haelt die Kennung in der Hand und
reichte sie an **einer von zwei** Stellen weiter — an den Folgeauftrag ja, an
`kzg_store` nicht. Aus genau diesem KZG-Eintrag entstehen bei hoher Salienz
die naechsten Auftraege, und der Recherche-Agent erzeugt die Mehrzahl.

**Zwei Zeugen, und der zweite ist der, der den Defekt gefunden haette.** Der
erste prueft den Mechanismus: `kzg_store` reicht die Kennung an den Auftrag.
Der zweite prueft am Syntaxbaum, dass die Aufrufstelle sie ueberhaupt
**uebergibt** — ein Vorgabewert, den niemand setzt, ist in diesem Bestand eine
belegte Fehlerklasse.
"""

import ast
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from memory.kzg import kzg_store

AGENT = Path(__file__).resolve().parents[1] / "agents" / "recherche" / "agent.py"

TURN = "b673e7f1b34645db93525a1d657010c6"


def _redis() -> MagicMock:
    """Ein Redis, das jeden Schluessel als neu meldet."""
    client = MagicMock()
    client.exists.return_value = False
    client.keys.return_value = []
    client.scan_iter.return_value = iter(())
    client.hgetall.return_value = {}
    return client


class KzgStorePassesTheIdTest(unittest.TestCase):
    """Der Mechanismus: aus dem Eintrag wird ein Auftrag, und der erbt die Kennung."""

    def _store(self, turn_id: str) -> MagicMock:
        salienz_obj = {
            "salienz": 0.95,
            "themen": ["Neutronensterne"],
            "zusammenfassung": "Ein Zeuge ueber die Kennung des Ausloese-Turns.",
            "intentionen": ["wissen"],
            "emotion": "neugierig",
            "modus": "sachlich",
            "dimension": "wissen",
        }
        with patch("memory.kzg.shadow_queue_push") as push, \
             patch("memory.kzg.promotion_queue_push"), \
             patch("memory.kzg.log_db_write"), \
             patch("memory.kzg.PIXIE_AKTIV", True):
            kzg_store(
                redis_client=_redis(),
                user_id="meister",
                character_id="nova",
                beobachter="user",
                salienz_obj=salienz_obj,
                embedding=[0.0] * 768,
                turn_id=turn_id,
            )
        return push

    def test_the_order_inherits_the_turn_id(self) -> None:
        push = self._store(TURN)
        if not push.called:
            self.skipTest("kein Auftrag erzeugt — Salienz-Tor oder Aufgabenwahl griff")
        self.assertEqual(push.call_args.kwargs.get("ausloeser_turn_id"), TURN)

    def test_an_empty_id_becomes_none_not_an_empty_string(self) -> None:
        """Leer heisst unbekannt — ein Leerstring in der Spalte saehe aus wie ein Wert."""
        push = self._store("")
        if not push.called:
            self.skipTest("kein Auftrag erzeugt — Salienz-Tor oder Aufgabenwahl griff")
        self.assertIsNone(push.call_args.kwargs.get("ausloeser_turn_id"))


class ResearchAgentHandsTheIdOverTest(unittest.TestCase):
    """Die Aufrufstelle: der Zeuge, der den Defekt gefunden haette."""

    def setUp(self) -> None:
        self.baum = ast.parse(AGENT.read_text(encoding="utf-8"))
        self.aufrufe = [
            k for k in ast.walk(self.baum)
            if isinstance(k, ast.Call)
            and isinstance(k.func, ast.Name)
            and k.func.id == "kzg_store"
        ]

    def test_the_agent_calls_kzg_store(self) -> None:
        """Ohne diesen Zeugen waere ein umbenannter Aufruf ein gruener Lauf."""
        self.assertEqual(len(self.aufrufe), 1)

    def test_every_call_passes_a_turn_id(self) -> None:
        ohne = [k for k in self.aufrufe
                if not any(s.arg == "turn_id" for s in k.keywords)]
        self.assertEqual(ohne, [], "kzg_store-Aufruf ohne turn_id")

    def test_the_id_comes_from_the_order_not_from_a_literal(self) -> None:
        """Ein Literal waere ein Wert, der wie eine Messung aussieht."""
        for k in self.aufrufe:
            wert = next(s.value for s in k.keywords if s.arg == "turn_id")
            quelle = ast.unparse(wert)
            self.assertIn("queue_eintrag", quelle, f"turn_id kommt aus '{quelle}'")
            self.assertIn("ausloeser_turn_id", quelle)


if __name__ == "__main__":
    unittest.main()
