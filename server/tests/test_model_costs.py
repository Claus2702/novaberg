"""Zeugen fuer die Kostenrechnung eines Modellaufrufs.

**Warum die Kennung ein Feld des Requests ist und keine Kontextvariable**
`[gemessen 06.09.2026]`: Die Worker-Schleife wird beim Serverstart **einmal**
als Task gestartet und traegt den Kontext dieses Zeitpunkts. Eine Probe mit
demselben Aufbau — Schleife als Task, danach `set()` beim Aufrufer — zeigte:
Der Aufrufer sah `turn-4711`, die Schleife sah den Vorgabewert. Der Wert muss
also **mit dem Auftrag reisen** und wird erst im Worker gesetzt, wo
`asyncio.to_thread` ihn in den Provider-Thread kopiert.

**Warum er zurueckgenommen wird:** Ein einziger Task ueber die ganze
Laufzeit heisst, dass ein gesetzter Wert stehen bleibt. Ohne `reset` buchte
der naechste Aufruf ohne eigenen Turn auf den vorigen — eine Rechnung, die
lautlos falsch waere.
"""

import asyncio
import unittest
from contextvars import copy_context

from config import (
    OPENROUTER_PRICE_INPUT_PER_M,
    OPENROUTER_PRICE_OUTPUT_PER_M,
)
from services.model_costs import (
    BACKGROUND_TURN,
    CURRENT_TURN,
    cost_usd,
)


class KostenrechnungTest(unittest.TestCase):
    """Die Rechnung selbst."""

    def test_ausgabe_wiegt_schwerer_als_eingabe(self) -> None:
        """Der ganze Grund, warum die Summe `token_total` nicht genuegt.

        Rot, sobald jemand beide Richtungen gleich bepreist — dann waere die
        Trennung im Provider ueberfluessig und die Rechnung falsch.
        """
        self.assertGreater(
            OPENROUTER_PRICE_OUTPUT_PER_M, OPENROUTER_PRICE_INPUT_PER_M,
            "Wenn Ausgabe nicht teurer ist, traegt die Begruendung des Moduls nicht",
        )
        self.assertGreater(cost_usd(0, 1000), cost_usd(1000, 0))

    def test_die_rechnung_ist_die_erwartete(self) -> None:
        """Eine Million Token kostet genau den Listenpreis."""
        self.assertAlmostEqual(
            cost_usd(1_000_000, 0), OPENROUTER_PRICE_INPUT_PER_M, places=9,
        )
        self.assertAlmostEqual(
            cost_usd(0, 1_000_000), OPENROUTER_PRICE_OUTPUT_PER_M, places=9,
        )

    def test_ein_kaputter_zaehlerstand_senkt_die_tagessumme_nicht(self) -> None:
        """Negative Werte werden geklemmt, nicht durchgereicht."""
        self.assertEqual(cost_usd(-5, -5), 0.0)
        self.assertEqual(cost_usd(0, 0), 0.0)


class TurnKennungTest(unittest.IsolatedAsyncioTestCase):
    """Wie die Kennung reist — und wie sie wieder verschwindet."""

    def test_ohne_turn_gilt_der_hintergrund(self) -> None:
        """Leer ist kein gueltiger Wert: `_log_eintrag` meldete ihn als Defekt."""
        self.assertEqual(copy_context().run(CURRENT_TURN.get), BACKGROUND_TURN)
        self.assertTrue(BACKGROUND_TURN)

    async def test_eine_schleife_traegt_den_turn_des_aufrufers_nicht(self) -> None:
        """Die Messung, die das Feld im Request begruendet — als Zeuge.

        Rot, falls Python das Verhalten je aendert: Dann waere die
        Kontextvariable allein tragfaehig und das Feld im Request
        ueberfluessig.
        """
        gesehen: list[str] = []
        queue: asyncio.Queue = asyncio.Queue()

        async def schleife() -> None:
            while True:
                auftrag = await queue.get()
                if auftrag is None:
                    return
                gesehen.append(CURRENT_TURN.get())
                auftrag.set_result(True)

        task = asyncio.create_task(schleife())
        await asyncio.sleep(0)

        CURRENT_TURN.set("turn-4711")
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        await queue.put(fut)
        await fut
        await queue.put(None)
        await task

        self.assertEqual(
            gesehen, [BACKGROUND_TURN],
            "Die Schleife sieht den Turn des Aufrufers — dann waere das Feld "
            "im Request ueberfluessig und die Begruendung des Moduls falsch",
        )

    async def test_der_thread_sieht_den_turn_des_workers(self) -> None:
        """`asyncio.to_thread` kopiert den Kontext — darauf ruht der Bau."""
        marke = CURRENT_TURN.set("turn-im-worker")
        try:
            gesehen: str = await asyncio.to_thread(CURRENT_TURN.get)
        finally:
            CURRENT_TURN.reset(marke)

        self.assertEqual(gesehen, "turn-im-worker")
        self.assertEqual(CURRENT_TURN.get(), BACKGROUND_TURN)


if __name__ == "__main__":
    unittest.main()
