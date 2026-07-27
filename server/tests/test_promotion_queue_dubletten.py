"""Tests fuer die Dublettenpruefung beim Einreihen zur LZG-Promotion.

Ziel: In `queue:{user_id}` liegt je KZG-Key hoechstens ein lzg_promotion-
Auftrag. Ein zweiter Aufruf fuer denselben Key schreibt nichts.

Hintergrund: Drei Stellen schrieben ohne jede Pruefung — der frisch angelegte
Eintrag, der verstaerkte Nachbar und der Bestandspfad. Eine Dublette kann
nachweislich nichts beitragen, weil der SynapsenPromotionAgent die Salienz
frisch aus dem Hash liest und nicht aus dem Auftrag; der erste Auftrag holt
einen gestiegenen Wert ohnehin ab.

Redis ist hier ein Fake mit echter Listen-Semantik statt eines MagicMock:
Geprueft wird, was am Ende in der Liste steht, nicht welche Methoden gerufen
wurden. Ein MagicMock wuerde die Dublettenpruefung selbst nicht ausueben.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import patch

from services.shadow_agent.utils import promotion_queue_push

UTILS_LOGGER: str = "ki_server.shadow"


class FakeRedis:
    """Minimal-Redis mit den drei Listen-Operationen, die der Helfer nutzt."""

    def __init__(self, vorbelegung: list[str] | None = None):
        self.listen: dict[str, list[str]] = {}
        if vorbelegung:
            self.listen["queue:meister"] = list(vorbelegung)

    def lrange(self, key: str, start: int, stop: int) -> list[str]:
        eintraege: list[str] = self.listen.get(key, [])
        return eintraege if stop == -1 else eintraege[start:stop + 1]

    def rpush(self, key: str, wert: str) -> int:
        self.listen.setdefault(key, []).append(wert)
        return len(self.listen[key])

    def roh(self, key: str = "queue:meister") -> list[str]:
        """Alle Eintraege unverarbeitet — auch die absichtlich unlesbaren."""
        return self.listen.get(key, [])

    def eintraege(self, key: str = "queue:meister") -> list[dict]:
        """Nur die lesbaren Eintraege. Unlesbare gehoeren zum Testaufbau und
        werden hier uebergangen — sonst scheitert der Helfer statt der
        geprueften Funktion."""
        lesbar: list[dict] = []
        for roh in self.listen.get(key, []):
            try:
                lesbar.append(json.loads(roh))
            except (json.JSONDecodeError, TypeError):
                continue
        return lesbar


def _push(redis, key: str, salienz: float = 0.8) -> bool:
    with patch("services.shadow_agent.utils.PIXIE_AKTIV", True):
        return promotion_queue_push(redis, "meister", key, salienz, "Thema", "kontext")


class DublettenTest(unittest.TestCase):
    """Je Key hoechstens ein Auftrag."""

    def test_erster_aufruf_reiht_ein(self):
        redis = FakeRedis()
        self.assertTrue(_push(redis, "kzg:test:1"))

        eintraege: list[dict] = redis.eintraege()
        self.assertEqual(len(eintraege), 1)
        self.assertEqual(eintraege[0]["aufgabe"], "lzg_promotion")
        self.assertEqual(eintraege[0]["key"],     "kzg:test:1")

    def test_zweiter_aufruf_fuer_denselben_key_schreibt_nichts(self):
        redis = FakeRedis()
        _push(redis, "kzg:test:1")
        self.assertFalse(_push(redis, "kzg:test:1", salienz=0.95))

        self.assertEqual(len(redis.eintraege()), 1)
        # Der bestehende Auftrag behaelt seine Salienz — richtig so: Der Agent
        # liest sie ohnehin frisch aus dem Hash.
        self.assertEqual(redis.eintraege()[0]["salienz"], 0.8)

    def test_verschiedene_keys_kommen_beide_durch(self):
        """Positiver Zwilling: die Pruefung darf nicht alles blockieren."""
        redis = FakeRedis()
        self.assertTrue(_push(redis, "kzg:test:1"))
        self.assertTrue(_push(redis, "kzg:test:2"))

        self.assertEqual([e["key"] for e in redis.eintraege()],
                         ["kzg:test:1", "kzg:test:2"])

    def test_fremde_auftragsart_mit_gleichem_key_blockiert_nicht(self):
        """Nur lzg_promotion zaehlt — ein anderer Auftrag ist kein Duplikat."""
        fremd: str = json.dumps({"aufgabe": "recherche", "key": "kzg:test:1"})
        redis = FakeRedis([fremd])

        self.assertTrue(_push(redis, "kzg:test:1"))
        self.assertEqual(len(redis.eintraege()), 2)


class RobustheitTest(unittest.TestCase):
    """Was der Helfer aushalten muss, ohne die Promotion zu blockieren."""

    def test_unlesbarer_fremdeintrag_wird_benannt_und_uebergangen(self):
        redis = FakeRedis(["das ist kein json"])

        with self.assertLogs(UTILS_LOGGER, level="WARNING") as log:
            self.assertTrue(_push(redis, "kzg:test:1"))

        # Zwei Rohzeilen: der unlesbare Fremdeintrag und der neue Auftrag.
        self.assertEqual(len(redis.roh()), 2)
        lesbar: list[dict] = redis.eintraege()
        self.assertEqual(len(lesbar), 1)
        self.assertEqual(lesbar[0]["key"], "kzg:test:1")

        unlesbar = [r for r in log.records if "unlesbarer Queue-Eintrag" in r.getMessage()]
        self.assertEqual(len(unlesbar), 1)

    def test_leerer_key_wird_laut_abgelehnt(self):
        redis = FakeRedis()

        with self.assertLogs(UTILS_LOGGER, level="ERROR") as log:
            self.assertFalse(_push(redis, ""))

        self.assertEqual(redis.eintraege(), [])
        self.assertIn("Pflichtfeld leer", log.records[0].getMessage())

    def test_ohne_pixie_wird_nichts_eingereiht(self):
        redis = FakeRedis()
        with patch("services.shadow_agent.utils.PIXIE_AKTIV", False):
            self.assertFalse(
                promotion_queue_push(redis, "meister", "kzg:test:1", 0.8)
            )
        self.assertEqual(redis.eintraege(), [])


if __name__ == "__main__":
    unittest.main()
