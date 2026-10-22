"""Zeugen für den Fakt eines Ereignisses: er verweist auf dessen Timeline-Zeile.

Was diese Datei zusichert:
  * **Mit eingetragenem Ereignis** trägt der Kandidat in der Nachricht an das
    Modell die Marke `EREIGNIS EINGETRAGEN`, und der Fakt steht mit
    `timeline_id` der Zeile in `fakten`.
  * **Ohne Ereignis** (P4) keine Marke und `timeline_id` NULL.
  * **Gescheitertes Eintragen** (`{kandidat: None}`): kein Fakt, das Tripel
    ist `verworfen:ereignis_fehlt`, laut im Log.

Die Abbildung kommt, wie der Dispatcher sie legt, unter `daten["ereignisse"]`.
Das Modell antwortet aus einem festen Ausgang; die Kandidaten des Turns sind
ersetzt, der Eintrag `log_db_write` wird abgefangen. Die Datenbank ist die
Wegwerf-Datenbank der Suite; jedes Fixture bringt ein eigenes Paar mit und
räumt in tearDown ab.
"""

import unittest
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras

from agents import discover_agents
from agents.fakten import dispatch as fakten_dispatch_mod
from config import POSTGRES_URL
from memory.repositories.timeline_repository import TimelineRepository
from plugins import discover_managers

VEKTOR: list[float] = [1.0] + [0.0] * 767
_AEUSSERUNG: str = "Ilva ist übrigens nach Ostheim gezogen"
_MARKE: str = "EREIGNIS EINGETRAGEN"


def _ausfuehren(sql: str, params: tuple) -> list[dict]:
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            zeilen: list[dict] = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return zeilen
    finally:
        conn.close()


def _auftrag(ereignisse: dict | None) -> dict:
    """Ein Fakten-Auftrag; `ereignisse` wie vom Dispatcher, None ohne den Schlüssel."""
    daten: dict = {"turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.80,
                   "user_intentionen": ["mitteilen"], "abgelegt": True}
    if ereignisse is not None:
        daten["ereignisse"] = ereignisse
    return {"ziel": "fakten", "aktion": "pruefen", "daten": daten}


class FactOfAnEventTest(unittest.TestCase):
    """Gegen die Datenbank: Abbildung → Marke → Tripel → Fakt mit `timeline_id`."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def setUp(self) -> None:
        self.user: str = f"test-fakt-tl-{uuid.uuid4().hex[:8]}"
        self.char: str = "nova-test"
        self.modell = MagicMock()
        self.modell.chat.submit_sync.return_value.parsed = {
            "dauerhafte_aussage": True, "grund": "Probe", "tripel": [
                {"kandidat": 1, "subjekt": "Ilva", "beziehung": "wohnt_in", "objekt": "Ostheim"},
            ]}
        einbettung = MagicMock()
        einbettung.embed.submit_sync.return_value.embedding = VEKTOR
        einbettung.embed.submit_sync.return_value.duration_seconds = 0.0
        for ziel, ersatz in (("agents.fakten.klassifikation.model_service", self.modell),
                             ("memory.services.entity_resolution.model_service", einbettung)):
            p = patch(ziel, ersatz)
            p.start()
            self.addCleanup(p.stop)
        _ausfuehren("INSERT INTO entitaeten (user_id, name, typ) VALUES (%s, 'Ilva', 'person')",
                    (self.user,))

    def tearDown(self) -> None:
        _ausfuehren("DELETE FROM fakten WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM timeline WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _ereignis_zeile(self) -> int:
        return TimelineRepository.insert(
            POSTGRES_URL, self.user, self.char, datetime(2026, 11, 1), "ereignis",
            "Umzug nach Ostheim", details="Ilva", precision="month",
        )

    def _laufen(self, ereignisse: dict | None) -> dict:
        """Der Inhalt des einen Eintrags `log_db_write`."""
        zustand: dict = {"user_id": self.user, "character_id": self.char,
                         "turn_id": "probe-turn", "user_prompt": _AEUSSERUNG}
        kandidat: dict = {"id": 1, "objekt_id": 1, "objekt": "Ilva", "klasse": "person",
                          "entitaet_id": None, "entitaet_bindung": None,
                          "eigenschaft": "Wohnort", "wert": "Ostheim", "sprecher": "nutzer"}
        with patch.object(fakten_dispatch_mod, "turn_candidates", return_value=[kandidat]), \
             patch.object(fakten_dispatch_mod, "log_db_write") as eintrag:
            fakten_dispatch_mod.process_fact_orders(zustand, [_auftrag(ereignisse)], POSTGRES_URL)
        eintrag.assert_called_once()
        return eintrag.call_args.kwargs["inhalt"]

    def _nachricht(self) -> str:
        self.assertEqual(self.modell.chat.submit_sync.call_count, 1)
        return self.modell.chat.submit_sync.call_args.args[0].messages[0]["content"]

    def _fakten(self) -> list[dict]:
        return _ausfuehren("SELECT attribut, timeline_id FROM fakten WHERE user_id = %s",
                           (self.user,))

    def test_an_entered_event_marks_the_candidate_and_the_fact_points_to_it(self) -> None:
        zeile = self._ereignis_zeile()
        inhalt = self._laufen({1: zeile})
        self.assertIn(f"Wert: Ostheim | {_MARKE}", self._nachricht())
        self.assertEqual(self._fakten(), [{"attribut": "wohnt_in", "timeline_id": zeile}])
        self.assertEqual([(t["ausgang"], t["timeline_id"]) for t in inhalt["tripel"]],
                         [("angelegt", zeile)])

    def test_the_twin_without_an_event_no_mark_and_no_reference(self) -> None:
        inhalt = self._laufen(None)
        self.assertNotIn(_MARKE, self._nachricht())
        self.assertEqual(self._fakten(), [{"attribut": "wohnt_in", "timeline_id": None}])
        self.assertNotIn("timeline_id", inhalt["tripel"][0])

    def test_a_failed_event_writes_no_fact(self) -> None:
        with self.assertLogs("ki_server.agents.fakten.klassifikation", level="ERROR") as protokoll:
            inhalt = self._laufen({1: None})
        self.assertIn("sein Ereignis fehlt", "\n".join(protokoll.output))
        self.assertNotIn(_MARKE, self._nachricht())
        self.assertEqual(self._fakten(), [])
        self.assertEqual([t["ausgang"] for t in inhalt["tripel"]], ["verworfen:ereignis_fehlt"])


if __name__ == "__main__":
    unittest.main()
