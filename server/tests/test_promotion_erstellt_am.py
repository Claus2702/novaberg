"""Tests: an unreadable creation time does not become a node with an invented date.

The promotion agent read the KZG hash field `erstellt_am` and, when it was
missing or not a number, silently put *now* in its place: `ValueError` caught,
no log, no audit row. The node then carried an invented `kzg_erstellt_am`, and
the column is `NOT NULL`, so nothing downstream could tell it apart.

Four assertions, driven through the real `invoke` (queue -> work list ->
`_eintrag_verarbeiten`):

  1. Field missing: no node, one error row with the raw value and the key in
     `pipeline_log` and in the audit, and the entry leaves the work list.
  2. Field `"abc"`: the same.
  3. Field not finite (`"nan"`, `"inf"`): the same — `float()` accepts them,
     but neither is a point in time.
  4. Field valid: a node is created with exactly this point in time.

Redis is a fake with real list semantics, like in
`test_promotion_arbeitsliste.py`. Everything behind the node write (embedding,
candidates, edges, the back-channel) is replaced; asserted is what reaches
`knoten_anlegen` and what ends up in the lists.

No skipUnless, no skipIf, no try/except around imports.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from agents.base import AgentState
from agents.synapsen_promotion.agent import SynapsenPromotionAgent

AGENT_MODULE: str = "agents.synapsen_promotion.agent"
KZG_KEY: str = "kzg:meister:nova:1789772063899"
VALID_TIMESTAMP: str = "1789772063.5"

# The services write their own audit (NMCP §7). Without this stand-in every
# witness that calls `invoke` would write real rows into `hintergrund_log`.
_SERVICE_AUDIT = patch("agents.base.write_audit")


def setUpModule() -> None:
    """Keep the service audit out of the production table for this file."""
    _SERVICE_AUDIT.start()


def tearDownModule() -> None:
    """Release the stand-in."""
    _SERVICE_AUDIT.stop()


class FakeRedis:
    """Minimal Redis: the list operations of `invoke` plus one KZG hash."""

    def __init__(self, queue: list[str], kzg_hash: dict[str, str]) -> None:
        """Set up the queue of the pair and the KZG hash of the entry."""
        self.lists: dict[str, list[str]] = {"queue:meister": list(queue)}
        self.counters: dict[str, dict[str, int]] = {}
        self.kzg_hash: dict[str, str] = dict(kzg_hash)

    def lmove(self, source: str, target: str, where_from: str, where_to: str) -> str | None:
        """Move one entry atomically."""
        entries: list[str] = self.lists.get(source, [])
        if not entries:
            return None
        value: str = entries.pop(0) if where_from == "LEFT" else entries.pop()
        target_list: list[str] = self.lists.setdefault(target, [])
        if where_to == "LEFT":
            target_list.insert(0, value)
        else:
            target_list.append(value)
        return value

    def lrem(self, key: str, count: int, value: str) -> int:
        """Remove exactly one entry by value."""
        entries: list[str] = self.lists.get(key, [])
        if value in entries:
            entries.remove(value)
            return 1
        return 0

    def lindex(self, key: str, index: int) -> str | None:
        """Look at an entry without moving it."""
        entries: list[str] = self.lists.get(key, [])
        try:
            return entries[index]
        except IndexError:
            return None

    def hincrby(self, key: str, field: str, amount: int) -> int:
        """Count the retry counter up."""
        counter: dict[str, int] = self.counters.setdefault(key, {})
        counter[field] = counter.get(field, 0) + amount
        return counter[field]

    def hdel(self, key: str, field: str) -> int:
        """Delete a retry counter."""
        return 1 if self.counters.get(key, {}).pop(field, None) is not None else 0

    def exists(self, key: str) -> int:
        """Report the KZG entry as existing for as long as its hash does."""
        return 1 if key == KZG_KEY else 0

    def hget(self, key: str, field: str) -> str | None:
        """Return one field of the KZG hash, None when it is missing."""
        if key != KZG_KEY:
            return None
        return self.kzg_hash.get(field)

    def set(self, key: str, value: str) -> bool:
        """Accept `hash_dirty` and ignore it."""
        return True

    def entries(self, key: str) -> list[str]:
        """Return the content of a list, for the assertions."""
        return self.lists.get(key, [])


def _order() -> str:
    return json.dumps({
        "aufgabe": "lzg_promotion", "user_id": "meister",
        "key": KZG_KEY, "salienz": 0.9, "themen": "astronomie",
    })


def _kzg_hash(erstellt_am: str | None) -> dict[str, str]:
    kzg_hash: dict[str, str] = {
        "inhalt": "Der Nutzer beobachtet den Jupiter.",
        "character_id": "nova", "beobachter": "user", "salienz": "0.8",
    }
    if erstellt_am is not None:
        kzg_hash["erstellt_am"] = erstellt_am
    return kzg_hash


def _state() -> AgentState:
    return {
        "aufgabe": "Test", "aufgabe_typ": "workflow",
        "agent_name": "synapsen_promotion", "kontext": {"user_id": "meister"},
        "parameter": {}, "schritte": [], "ergebnis": None,
        "status": "laufend", "rueckfrage": None, "fehler": None,
    }


class _PromotionRun:
    """One real `invoke` over one queued order, everything behind the node write replaced."""

    def __init__(self, erstellt_am: str | None) -> None:
        """Run the agent once and keep what the assertions need."""
        self.redis = FakeRedis([_order()], _kzg_hash(erstellt_am))
        self.pipeline_log = MagicMock()
        self.audit = MagicMock()
        self.lzg_knoten = MagicMock()
        self.lzg_knoten.embed_text_bauen.return_value = "Der Nutzer beobachtet den Jupiter."
        self.lzg_knoten.kandidaten_mit_cosine_laden.return_value = []
        self.lzg_knoten.match_pruefen.return_value = None
        self.lzg_knoten.knoten_anlegen.return_value = 4711
        self.lzg_knoten.knoten_laden.return_value = None
        model_service = MagicMock()
        model_service.embed.submit_sync.return_value = MagicMock(
            embedding=[0.1, 0.2, 0.3], duration_seconds=0.01,
        )
        agent = SynapsenPromotionAgent()
        with patch(f"{AGENT_MODULE}.redis_client", self.redis), \
             patch(f"{AGENT_MODULE}.pipeline_log", self.pipeline_log), \
             patch(f"{AGENT_MODULE}.write_audit", self.audit), \
             patch(f"{AGENT_MODULE}.lzg_knoten", self.lzg_knoten), \
             patch(f"{AGENT_MODULE}.lzg_kanten", MagicMock()), \
             patch(f"{AGENT_MODULE}.model_service", model_service), \
             patch(f"{AGENT_MODULE}.PIXIE_AKTIV", False), \
             patch.object(agent, "_verbindung_lzg_id_nachtragen"), \
             patch.object(agent, "_rueckweg_einreihen"):
            self.result: dict = agent.invoke(_state())["ergebnis"]

    def error_reasons(self) -> list[str]:
        """Return the reasons of every `pipeline_log` error row."""
        return [c.kwargs["inhalt"]["grund"] for c in self.pipeline_log.log_fehler.call_args_list]

    def audit_errors(self) -> list[str]:
        """Return the texts of every audit row with status `fehler`."""
        return [c.args[3] for c in self.audit.call_args_list if c.args[2] == "fehler"]


class UnreadableCreationTimeTest(unittest.TestCase):
    """The witnesses for the defect: no node with an invented date."""

    def _assert_rejected(self, run: _PromotionRun, raw_value: str) -> None:
        self.lzg_knoten_not_called(run)
        reasons: list[str] = run.error_reasons()
        self.assertEqual(len(reasons), 1, reasons)
        self.assertIn(KZG_KEY, reasons[0])
        self.assertIn(raw_value, reasons[0])
        audit: list[str] = run.audit_errors()
        self.assertEqual(len(audit), 1, audit)
        self.assertIn(raw_value, audit[0])
        self.assertEqual(run.redis.entries("queue:meister"), [])
        self.assertEqual(run.redis.entries("queue:meister:arbeit"), [],
                         "a rejected entry must not be delivered again")

    def lzg_knoten_not_called(self, run: _PromotionRun) -> None:
        """Assert that no node is written and no embedding is spent on the entry."""
        run.lzg_knoten.knoten_anlegen.assert_not_called()
        run.lzg_knoten.kandidaten_mit_cosine_laden.assert_not_called()

    def test_missing_field_creates_no_node(self) -> None:
        """Case 1: `erstellt_am` is not in the hash."""
        self._assert_rejected(_PromotionRun(None), "''")

    def test_unreadable_value_creates_no_node(self) -> None:
        """Case 2: `erstellt_am` is `"abc"`."""
        self._assert_rejected(_PromotionRun("abc"), "'abc'")

    def test_value_that_is_not_finite_creates_no_node(self) -> None:
        """Case 3: `float()` reads `nan` and `inf`, neither is a point in time."""
        for raw in ("nan", "inf"):
            with self.subTest(raw=raw):
                self._assert_rejected(_PromotionRun(raw), f"'{raw}'")


class ReadableCreationTimeTest(unittest.TestCase):
    """The unchanged path: a readable value is taken as it is."""

    def test_valid_value_reaches_the_node(self) -> None:
        """Case 4: the node carries exactly the point in time from the hash."""
        run = _PromotionRun(VALID_TIMESTAMP)
        run.lzg_knoten.knoten_anlegen.assert_called_once()
        self.assertEqual(
            run.lzg_knoten.knoten_anlegen.call_args.kwargs["kzg_erstellt_am"],
            float(VALID_TIMESTAMP),
        )
        self.assertEqual(run.error_reasons(), [])
        self.assertEqual(run.redis.entries("queue:meister:arbeit"), [])


if __name__ == "__main__":
    unittest.main()
