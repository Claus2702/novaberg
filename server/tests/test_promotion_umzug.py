"""Tests: a KZG entry promoted into a new node moves there and leaves no hash behind.

The promotion agent left the KZG hash standing after a successful promotion.
Until its TTL ran out, the entry went into the promotion again and matched
the node it had become — measured on 2026-09-04: 95.2 % of 14,947
reinforcements carried `cosine = 1.0000`, one node reached `haeufigkeit` 92
from a single turn.

Only a new node takes the whole entry into the LZG. A hit on an active node
and a wake-up create no node: content, EI fields, magnets and creation time of
the entry arrive nowhere, so its hash stays until its TTL.

Driven through the real `_eintrag_verarbeiten`; Redis is a fake with real
hash semantics (a deleted key is gone for `exists` and `hget`). Embedding,
candidates, node writes, edges, the bridge and the back-channel are replaced.

  1. New node created -> the KZG key is deleted.
     Twin: `knoten_anlegen` returns None -> the key is still there.
  2. Deactivated node woken -> the key is still there, no DEL.
     Twin of the error path: the wake-up fails -> the key is still there.
  3. Active node hit -> the key is still there, no DEL.
  4. The key is deleted only after the back-channel has read `turn_id`.
  5. An exception before the end -> the key is still there.
  6. A Redis error on DEL is loud and does not tear the promotion.
  7. A key without the prefix `kzg:` is not deleted, even after a new node.

No skipUnless, no skipIf, no try/except around imports.
"""

import unittest
from unittest.mock import MagicMock, patch

import redis

from agents.synapsen_promotion.agent import SynapsenPromotionAgent

AGENT_MODULE: str = "agents.synapsen_promotion.agent"
KZG_KEY: str = "kzg:meister:nova:1789772063899"
FOREIGN_KEY: str = "sitzung:meister:nova:1789772063899"
TURN_ID: str = "turn-umzug-1"
MATCHED_NODE: int = 17
NEW_NODE: int = 4711


class FakeRedis:
    """Minimal Redis: one hash with real exists/hget/delete semantics."""

    def __init__(self, key: str) -> None:
        """Set up the hash of the entry under `key`."""
        self.hashes: dict[str, dict[str, str]] = {key: {
            "inhalt": "Der Nutzer beobachtet den Saturn und seine Ringe.",
            "character_id": "nova", "beobachter": "user", "salienz": "0.8",
            "erstellt_am": "1789772063.5", "turn_id": TURN_ID,
        }}
        self.deleted: list[str] = []
        self.delete_error: Exception | None = None

    def exists(self, key: str) -> int:
        """Report a key as existing for as long as its hash does."""
        return 1 if key in self.hashes else 0

    def hget(self, key: str, field: str) -> str | None:
        """Return one field of a hash, None when key or field is missing."""
        return self.hashes.get(key, {}).get(field)

    def delete(self, key: str) -> int:
        """Delete a hash and record the call."""
        if self.delete_error is not None:
            raise self.delete_error
        self.deleted.append(key)
        return 1 if self.hashes.pop(key, None) is not None else 0

    def set(self, key: str, value: str) -> bool:
        """Accept `hash_dirty` and ignore it."""
        return True


def _order(key: str) -> dict:
    return {
        "aufgabe": "lzg_promotion", "user_id": "meister",
        "key": key, "salienz": 0.8, "themen": "astronomie",
    }


class _Promotion:
    """One real `_eintrag_verarbeiten` over one KZG entry, everything around it replaced."""

    def __init__(self, match: dict | None, key: str = KZG_KEY) -> None:
        """Prepare the stand-ins; `match` is what `match_pruefen` returns."""
        self.key: str = key
        self.redis = FakeRedis(key)
        self.pipeline_log = MagicMock()
        self.audit = MagicMock()
        self.lzg_knoten = MagicMock()
        self.lzg_knoten.embed_text_bauen.return_value = "Saturn"
        self.lzg_knoten.kandidaten_mit_cosine_laden.return_value = []
        self.lzg_knoten.match_pruefen.return_value = match
        self.lzg_knoten.knoten_anlegen.return_value = NEW_NODE
        self.lzg_knoten.knoten_laden.return_value = None
        self.lzg_knoten.reactivate_node.return_value = {"decay_alt": 0.05, "decay_neu": 2.05}
        self.lzg_kanten = MagicMock()
        self.lzg_kanten.kanten_neuberechnen_fuer_knoten.return_value = 3
        self.model_service = MagicMock()
        self.model_service.embed.submit_sync.return_value = MagicMock(
            embedding=[0.1, 0.2, 0.3], duration_seconds=0.01,
        )
        # What the back-channel saw when it was called: its `turn_id`
        # argument and whether the hash still stood at that moment.
        self.back_channel: list[tuple[str, int]] = []

    def _back_channel(self, **kwargs: object) -> None:
        self.back_channel.append((str(kwargs["turn_id"]), self.redis.exists(self.key)))

    def run(self) -> "_Promotion":
        """Run the agent once on the entry."""
        agent = SynapsenPromotionAgent()
        with patch(f"{AGENT_MODULE}.redis_client", self.redis), \
             patch(f"{AGENT_MODULE}.pipeline_log", self.pipeline_log), \
             patch(f"{AGENT_MODULE}.write_audit", self.audit), \
             patch(f"{AGENT_MODULE}.lzg_knoten", self.lzg_knoten), \
             patch(f"{AGENT_MODULE}.lzg_kanten", self.lzg_kanten), \
             patch(f"{AGENT_MODULE}.model_service", self.model_service), \
             patch(f"{AGENT_MODULE}.PIXIE_AKTIV", False), \
             patch.object(agent, "_verbindung_lzg_id_nachtragen") as bridge, \
             patch.object(agent, "_rueckweg_einreihen", side_effect=self._back_channel):
            self.bridge: MagicMock = bridge
            agent._eintrag_verarbeiten(_order(self.key), "meister")
        return self

    def final_write(self) -> dict:
        """Return the content of the last `pipeline_log` write, the one that closes the run."""
        return self.pipeline_log.log_db_write.call_args_list[-1].kwargs["inhalt"]

    def audit_rows(self, status: str) -> list[str]:
        """Return the texts of every audit row with the given status."""
        return [c.args[3] for c in self.audit.call_args_list if c.args[2] == status]

    def error_reasons(self) -> list[str]:
        """Return the reasons of every `pipeline_log` error row."""
        return [c.kwargs["inhalt"]["grund"] for c in self.pipeline_log.log_fehler.call_args_list]


def _active_match() -> dict:
    return {"id": MATCHED_NODE, "aktiv": True, "cosine": 1.0}


def _inactive_match() -> dict:
    return {"id": MATCHED_NODE, "aktiv": False, "cosine": 0.91}


class NewNodeDeletesTest(unittest.TestCase):
    """A new node takes the whole entry; its KZG hash is gone afterwards."""

    def test_new_node_deletes_the_key(self) -> None:
        """Case 1: no match, a new node is created."""
        run = _Promotion(None).run()
        run.lzg_knoten.knoten_anlegen.assert_called_once()
        self.assertEqual(run.redis.exists(KZG_KEY), 0)
        self.assertEqual(run.redis.deleted, [KZG_KEY], "exactly the key of the order, once")
        done: list[str] = run.audit_rows("erledigt")
        self.assertEqual(len(done), 1, done)
        self.assertIn("kzg_geloescht=ja", done[0])
        self.assertEqual(run.error_reasons(), [])

    def test_deletion_comes_after_the_back_channel_read(self) -> None:
        """Case 4: the back-channel still reads `turn_id` from the hash."""
        run = _Promotion(None).run()
        run.lzg_knoten.knoten_anlegen.assert_called_once()
        self.assertEqual(run.back_channel, [(TURN_ID, 1)],
                         "back-channel called once, with the turn_id, while the hash stood")
        self.assertEqual(run.redis.exists(KZG_KEY), 0)


class HitKeepsTest(unittest.TestCase):
    """A hit creates no node, so the entry has not moved; its hash stays.

    From the first build of 2026-10-23 until its correction the same day, both
    witnesses asserted the opposite: the hash was deleted after a wake-up and
    after a hit on an active node as well. Concept §7.2 ties step 4 to the
    creation of a node, and the deletion there lost the content of the entry.
    """

    def _assert_kept(self, run: _Promotion) -> None:
        run.lzg_knoten.knoten_anlegen.assert_not_called()
        self.assertEqual(run.redis.exists(KZG_KEY), 1)
        self.assertEqual(run.redis.deleted, [], "no DEL at all")
        done: list[str] = run.audit_rows("erledigt")
        self.assertEqual(len(done), 1, done)
        self.assertIn("kzg_geloescht=nein", done[0])
        self.assertEqual(run.error_reasons(), [], "keeping the hash is no error")

    def test_woken_node_keeps_the_key(self) -> None:
        """Case 2: a deactivated node is woken."""
        run = _Promotion(_inactive_match()).run()
        run.lzg_knoten.reactivate_node.assert_called_once()
        self._assert_kept(run)

    def test_hit_on_active_node_keeps_the_key(self) -> None:
        """Case 3: an active node is hit."""
        run = _Promotion(_active_match()).run()
        self._assert_kept(run)


class FailedPromotionKeepsTest(unittest.TestCase):
    """The twins: whatever did not move into a node keeps its hash."""

    def test_failed_node_write_keeps_the_key(self) -> None:
        """Twin of case 1: `knoten_anlegen` returns None."""
        promotion = _Promotion(None)
        promotion.lzg_knoten.knoten_anlegen.return_value = None
        run = promotion.run()
        self.assertEqual(run.redis.exists(KZG_KEY), 1)
        self.assertEqual(run.redis.deleted, [])
        self.assertEqual(len(run.audit_rows("fehler")), 1)

    def test_failed_wake_up_keeps_the_key(self) -> None:
        """Twin of case 2: `reactivate_node` returns None — nothing was woken."""
        promotion = _Promotion(_inactive_match())
        promotion.lzg_knoten.reactivate_node.return_value = None
        run = promotion.run()
        self.assertEqual(run.redis.exists(KZG_KEY), 1)
        self.assertEqual(run.redis.deleted, [])
        done: list[str] = run.audit_rows("erledigt")
        self.assertEqual(len(done), 1, done)
        self.assertIn("kzg_geloescht=nein", done[0])

    def test_exception_before_the_end_keeps_the_key(self) -> None:
        """An exception between match and end leaves the order for a retry."""
        promotion = _Promotion(None)
        promotion.lzg_knoten.knoten_anlegen.side_effect = RuntimeError("Datenbank weg")
        with self.assertRaises(RuntimeError):
            promotion.run()
        self.assertEqual(promotion.redis.exists(KZG_KEY), 1)
        self.assertEqual(promotion.redis.deleted, [])


class DeletionErrorTest(unittest.TestCase):
    """A refused or failed DEL is loud, and the promotion still ends as done."""

    def test_redis_error_is_logged_and_does_not_raise(self) -> None:
        """The hash stays, one error row names the step, the audit says `nein`."""
        promotion = _Promotion(None)
        promotion.redis.delete_error = redis.ConnectionError("Redis weg")
        run = promotion.run()
        self.assertEqual(run.redis.exists(KZG_KEY), 1)
        reasons: list[str] = run.error_reasons()
        self.assertEqual(len(reasons), 1, reasons)
        self.assertIn(KZG_KEY, reasons[0])
        self.assertEqual(
            run.pipeline_log.log_fehler.call_args.kwargs["inhalt"]["schritt"], "kzg_loeschen",
        )
        done: list[str] = run.audit_rows("erledigt")
        self.assertEqual(len(done), 1, done)
        self.assertIn("kzg_geloescht=nein", done[0])

    def test_key_without_kzg_prefix_is_not_deleted(self) -> None:
        """Case 7: after a new node, a foreign key in the order is refused.

        Twin on the accepting side: `test_new_node_deletes_the_key`.
        """
        run = _Promotion(None, key=FOREIGN_KEY).run()
        run.lzg_knoten.knoten_anlegen.assert_called_once()
        self.assertEqual(run.redis.exists(FOREIGN_KEY), 1)
        self.assertEqual(run.redis.deleted, [], "no DEL on a key outside the KZG")
        reasons: list[str] = run.error_reasons()
        self.assertEqual(len(reasons), 1, reasons)
        self.assertIn(FOREIGN_KEY, reasons[0])
        self.assertEqual(
            run.pipeline_log.log_fehler.call_args.kwargs["inhalt"]["schritt"], "kzg_loeschen",
        )
        done: list[str] = run.audit_rows("erledigt")
        self.assertEqual(len(done), 1, done)
        self.assertIn("kzg_geloescht=nein", done[0])


if __name__ == "__main__":
    unittest.main()
