"""Zeugen: Themen als Lueckenkandidaten — die Luecke beim Nutzer (`F-GV-2`).

Ziel: In den `[WISSENSLUECKEN]`-Block geht ein **Thema** aus Novas Bestand nahe am
Turn, das der Nutzer im Bestand des Paares nie beruehrt hat und das im Gespraech
nicht gefallen ist — kein Gedaechtnissatz. `[gemessen 12.09.2026, 15 Betriebsturns]`
Vorher waren 56 von 83 Luecken Vermerke ueber Novas eigene Aeusserungen
(*„Nova hat gefragt, ob …"*), und die Charakter-Resonanz trennte nach Sprecher
(+0,302 auf Saetzen). Auf Themen liegt der Abstand bei +0,009.

**Die Zeugen, die das Ziel festhalten:**
  * Ein vom Nutzer beruehrtes Thema kommt nicht in die Liste — auch nicht, wenn es
    in einem Nova-Knoten steht.
  * Die Resonanz entsteht aus dem Themenvektor: Zwei Themen desselben Knotens
    mit verschiedener Kern-Naehe werden verschieden gefiltert.
  * Der Stapel bettet jedes Thema nur einmal ein.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import asyncio
import math
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import ei.gap_topics as gap_topics
from config import GV_CHARAKTER_RESONANZ_SCHWELLE
from ei.gap_topics import (
    UserTopics,
    embed_topics,
    load_user_topics,
    split_topics,
    topic_stems,
    touched_by_user,
)
from ei.wissensluecken import _topic_candidates, wissensluecken_finden
from services.model_services.embed_worker import EmbedWorker
from services.model_services.types import EmbedBatchRequest, EmbedBatchResponse, EmbedRequest

TURN: list[float] = [1.0] + [0.0] * 7
KERN: list[float] = [0.0, 0.0, 1.0] + [0.0] * 5


def vektor(naehe_turn: float, naehe_kern: float) -> list[float]:
    """Ein Einheitsvektor mit festgelegtem Cosinus zum Turn (Achse 0) und zum Kern (Achse 2)."""
    rest = 1.0 - naehe_turn ** 2 - naehe_kern ** 2
    return [naehe_turn, math.sqrt(max(rest, 0.0)), naehe_kern] + [0.0] * 5


def knoten(themen, quelle: str = "lzg", similarity: float = 0.6, rang: float = 0.8) -> dict:
    return {"konzept": "Nova hat etwas erklaert", "similarity": similarity, "gewicht": 5.0,
            "gewicht_rang": rang, "gap_arousal": 0.3, "quelle": quelle, "themen": themen}


def zustand(**mehr) -> dict:
    basis = {"user_prompt": "Wie entsteht das Magnetfeld eines Neutronensterns?",
             "user_id": "mensch", "character_id": "figur", "prompt_embedding": TURN,
             "internal": None, "session_turns": [], "turn_id": "t-themen", "aktivierte_ziele": []}
    basis.update(mehr)
    return basis


class DieThemenWerdenZerlegt(unittest.TestCase):
    """`split_topics` — Array im LZG, Zeichenkette im KZG."""

    def test_liste_bleibt_liste(self) -> None:
        self.assertEqual(split_topics(["Quarkmaterie", " Dynamo-Effekt "]), ["Quarkmaterie", "Dynamo-Effekt"])

    def test_zeichenkette_wird_am_komma_getrennt(self) -> None:
        self.assertEqual(split_topics("Axionen, Nachweismethoden"), ["Axionen", "Nachweismethoden"])

    def test_leeres_und_none(self) -> None:
        self.assertEqual(split_topics(None), [])
        self.assertEqual(split_topics(""), [])
        self.assertEqual(split_topics([" ", ""]), [])

    def test_wiederholung_ohne_gross_klein(self) -> None:
        self.assertEqual(split_topics(["Entropie", "entropie", "Zeit"]), ["Entropie", "Zeit"])

    def test_ein_anderer_typ_ist_laut(self) -> None:
        with patch.object(gap_topics, "logger") as log:
            self.assertEqual(split_topics(42), [])
        self.assertTrue(log.error.called)


class BeruehrtIstEineAnnaeherung(unittest.TestCase):
    """`touched_by_user` — woertlich oder ueberwiegend bekannte Wortstaemme."""

    def setUp(self) -> None:
        themen = {"neutronensterne", "krustenbeben"}
        staemme: set[str] = set()
        for t in themen:
            staemme |= topic_stems(t)
        self.nutzer = UserTopics(themen, staemme)

    def test_woertlich_ohne_gross_klein(self) -> None:
        self.assertTrue(touched_by_user("Neutronensterne", self.nutzer))

    def test_ueberwiegend_bekannte_staemme(self) -> None:
        """*Neutronenstern Kruste*: beide Staemme (*neutron*, *kruste*) hat er schon."""
        self.assertTrue(touched_by_user("Neutronenstern Krustenbruch", self.nutzer))

    def test_ein_neues_wort_von_zweien_reicht_nicht(self) -> None:
        self.assertFalse(touched_by_user("Neutronenstern Magnetfeld", self.nutzer))

    def test_fremdes_thema_ist_nicht_beruehrt(self) -> None:
        self.assertFalse(touched_by_user("Flusserhaltung beim Sternkollaps", self.nutzer))

    def test_kurzwort_nur_woertlich(self) -> None:
        self.assertFalse(touched_by_user("Eis", self.nutzer))


class DerNutzerbestandWirdGeladen(unittest.TestCase):
    """`load_user_topics` — beide Speicher, blaetternd, zwischengehalten."""

    def setUp(self) -> None:
        gap_topics._user_cache.clear()

    def tearDown(self) -> None:
        gap_topics._user_cache.clear()

    def test_lzg_und_kzg_ueber_zwei_seiten(self) -> None:
        seiten = [[3, "kzg:a", ["themen", "Axionen, Kruste"], "kzg:b", ["themen", "Gamma"]],
                  [3, "kzg:c", ["themen", "Magnetare"]]]
        with patch.object(gap_topics.db_manager, "select", return_value=[{"themen": ["Entropie"]}]), \
             patch.object(gap_topics.redis_client, "execute_command", side_effect=seiten) as redis, \
             patch.object(gap_topics, "_KZG_PAGE", 2):
            bestand = load_user_topics("mensch", "figur")
        self.assertEqual(bestand.topics, {"entropie", "axionen", "kruste", "gamma", "magnetare"})
        self.assertEqual(redis.call_count, 2)
        self.assertIn("@beobachter:{user}", redis.call_args_list[0].args[2])

    def test_die_lzg_abfrage_liest_nur_nutzer_knoten(self) -> None:
        with patch.object(gap_topics.db_manager, "select", return_value=[]) as db, \
             patch.object(gap_topics.redis_client, "execute_command", return_value=[0]):
            load_user_topics("mensch", "figur")
        self.assertIn("beobachter = 'user'", db.call_args.args[0])

    def test_zwischengehalten(self) -> None:
        with patch.object(gap_topics, "_load_user_topics", return_value=UserTopics(set(), set())) as laden:
            load_user_topics("mensch", "figur")
            load_user_topics("mensch", "figur")
        self.assertEqual(laden.call_count, 1)

    def test_unvollstaendiges_paar(self) -> None:
        with self.assertRaises(ValueError):
            load_user_topics("mensch", "")


class ThemenvektorenImStapel(unittest.TestCase):
    """`embed_topics` — ein Aufruf fuer das Neue, nichts fuer das Bekannte."""

    def setUp(self) -> None:
        gap_topics._embed_cache.clear()

    def tearDown(self) -> None:
        gap_topics._embed_cache.clear()

    @staticmethod
    def antwort(request: EmbedBatchRequest, timeout: float = 60.0) -> EmbedBatchResponse:
        return EmbedBatchResponse(embeddings=[[float(len(t)), 1.0] for t in request.texts],
                                  model_name="m", duration_seconds=0.0, request_id="r")

    def test_ein_stapel_fuer_alle_neuen(self) -> None:
        with patch.object(gap_topics.model_service.embed, "submit_sync", side_effect=self.antwort) as aufruf:
            vektoren = embed_topics(["Gamma", "Quarkmaterie"])
        self.assertEqual(aufruf.call_count, 1)
        self.assertEqual(vektoren["Quarkmaterie"], [12.0, 1.0])

    def test_bekannte_kosten_keinen_aufruf(self) -> None:
        with patch.object(gap_topics.model_service.embed, "submit_sync", side_effect=self.antwort) as aufruf:
            embed_topics(["Gamma"])
            embed_topics(["Gamma"])
            embed_topics(["Gamma", "Axion"])
        self.assertEqual(aufruf.call_count, 2)
        self.assertEqual(aufruf.call_args.args[0].texts, ["Axion"])

    def test_der_speicher_haelt_seine_groesse(self) -> None:
        with patch.object(gap_topics.model_service.embed, "submit_sync", side_effect=self.antwort), \
             patch.object(gap_topics, "EMBED_CACHE_SIZE", 2):
            embed_topics(["A1xx", "B22xx", "C333xx"])
        self.assertEqual(list(gap_topics._embed_cache), ["B22xx", "C333xx"])

    def test_leeres_thema_ist_ein_aufruffehler(self) -> None:
        with self.assertRaises(ValueError):
            embed_topics(["Gamma", " "])


class DieLueckeBeimNutzer(unittest.TestCase):
    """`_topic_candidates` — beruehrt, erwaehnt, doppelt."""

    def rufen(self, nodes, nutzer=None, **mehr):
        nutzer = nutzer if nutzer is not None else UserTopics(set(), set())
        with patch("ei.wissensluecken.load_user_topics", return_value=nutzer), \
             patch("ei.wissensluecken.log_berechnung") as spur:
            ergebnis = _topic_candidates(nodes, zustand(**mehr))
        return ergebnis, spur

    def test_ein_beruehrtes_thema_faellt_heraus(self) -> None:
        nutzer = UserTopics({"quarkmaterie"}, topic_stems("quarkmaterie"))
        ergebnis, _ = self.rufen([knoten(["Quarkmaterie", "Flusserhaltung beim Sternkollaps"])], nutzer)
        self.assertEqual([k["konzept"] for k in ergebnis], ["Flusserhaltung beim Sternkollaps"])

    def test_ein_erwaehntes_thema_faellt_heraus(self) -> None:
        ergebnis, _ = self.rufen([knoten(["Dynamo-Effekt im Kern", "Quarkmaterie"])],
                                 session_turns=[{"inhalt": "Wir sprachen ueber den Dynamo-Effekt im Kern"}])
        self.assertEqual([k["konzept"] for k in ergebnis], ["Quarkmaterie"])

    def test_das_echo_des_laufenden_reizes_faellt_heraus(self) -> None:
        """Der Reiz selbst gehoert zum Gespraech — 12.09.2026 kam die eigene Frage als Luecke zurueck."""
        ergebnis, _ = self.rufen([knoten(["Staerke des Magnetfelds im Vergleich zur Erde", "Quarkmaterie"])],
                                 user_prompt="Wie stark ist das Magnetfeld im Vergleich zur Erde?")
        self.assertEqual([k["konzept"] for k in ergebnis], ["Quarkmaterie"])

    def test_das_thema_ist_der_kandidat_nicht_der_satz(self) -> None:
        ergebnis, _ = self.rufen([knoten(["Quarkmaterie"])])
        self.assertEqual(ergebnis[0]["konzept"], "Quarkmaterie")
        self.assertEqual(ergebnis[0]["knoten"], "Nova hat etwas erklaert")

    def test_doppelt_bleibt_das_staerkere(self) -> None:
        ergebnis, _ = self.rufen([knoten(["Quarkmaterie"], "lzg", similarity=0.3),
                                  knoten("Quarkmaterie", "kzg", similarity=0.7)])
        self.assertEqual(len(ergebnis), 1)
        self.assertEqual(ergebnis[0]["quelle"], "kzg")

    def test_die_zaehlung_steht_in_der_spur(self) -> None:
        nutzer = UserTopics({"quarkmaterie"}, topic_stems("quarkmaterie"))
        _, spur = self.rufen([knoten(["Quarkmaterie", "Gamma-Kohaerenz"]), knoten([])], nutzer)
        inhalt = spur.call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["schritt"], "gv4_themen")
        self.assertEqual((inhalt["knoten"], inhalt["ohne_themen"], inhalt["themen"],
                          inhalt["beruehrt"], inhalt["kandidaten"]), (2, 1, 2, 1, 1))

    def test_ohne_nutzerbestand_keine_luecke_und_ein_fehler(self) -> None:
        with patch("ei.wissensluecken.load_user_topics", side_effect=RuntimeError("db weg")), \
             patch("ei.wissensluecken.logger") as log:
            self.assertEqual(_topic_candidates([knoten(["Quarkmaterie"])], zustand()), [])
        self.assertTrue(log.error.called)


class DieResonanzKommtVomThema(unittest.TestCase):
    """Durch `wissensluecken_finden`: Naehe und Resonanz aus dem Themenvektor."""

    def finden(self, themen_vektoren: dict[str, list[float]], nodes: list[dict]) -> list[dict]:
        internal = SimpleNamespace(emotion=SimpleNamespace(mode="alltag", relationship_dynamic="neutral"),
                                   character=SimpleNamespace(core="ein Kern"))
        kern_antwort = SimpleNamespace(embedding=KERN)
        with patch("ei.wissensluecken.lzg_kandidaten_suchen", return_value=nodes), \
             patch("ei.wissensluecken.kzg_kandidaten_suchen", return_value=[]), \
             patch("ei.wissensluecken.load_weight_distributions", return_value={"lzg": [5.0], "kzg": [0.5]}), \
             patch("ei.wissensluecken.load_user_topics", return_value=UserTopics(set(), set())), \
             patch("ei.wissensluecken.embed_topics",
                   side_effect=lambda t: {x: themen_vektoren[x] for x in t}), \
             patch("ei.wissensluecken.model_service.embed.submit_sync", return_value=kern_antwort), \
             patch("ei.wissensluecken.log_berechnung"):
            return wissensluecken_finden(zustand(internal=internal), aufnahmebereitschaft=1.0)

    def test_zwei_themen_desselben_knotens_werden_verschieden_gefiltert(self) -> None:
        nah, fern = GV_CHARAKTER_RESONANZ_SCHWELLE + 0.3, GV_CHARAKTER_RESONANZ_SCHWELLE - 0.1
        ergebnis = self.finden({"Gamma-Kohaerenz": vektor(0.6, nah), "Kaffee": vektor(0.6, fern)},
                               [{**knoten(["Gamma-Kohaerenz", "Kaffee"]), "gewicht": 5.0}])
        self.assertEqual([k["konzept"] for k in ergebnis], ["Gamma-Kohaerenz"])
        self.assertAlmostEqual(ergebnis[0]["charakter_resonanz"], nah)

    def test_die_naehe_ist_die_des_themas(self) -> None:
        ergebnis = self.finden({"Gamma-Kohaerenz": vektor(0.55, 0.5)},
                               [{**knoten(["Gamma-Kohaerenz"], similarity=0.25), "gewicht": 5.0}])
        self.assertAlmostEqual(ergebnis[0]["similarity"], 0.55)

    def test_ohne_themenvektoren_keine_luecken_und_ein_fehler(self) -> None:
        with patch("ei.wissensluecken.lzg_kandidaten_suchen", return_value=[knoten(["Gamma"])]), \
             patch("ei.wissensluecken.kzg_kandidaten_suchen", return_value=[]), \
             patch("ei.wissensluecken.load_weight_distributions", return_value={"lzg": [5.0], "kzg": [0.5]}), \
             patch("ei.wissensluecken.load_user_topics", return_value=UserTopics(set(), set())), \
             patch("ei.wissensluecken.embed_topics", side_effect=RuntimeError("gpu weg")), \
             patch("ei.wissensluecken.log_berechnung"), \
             patch("ei.wissensluecken.logger") as log:
            self.assertEqual(wissensluecken_finden(zustand(), aufnahmebereitschaft=1.0), [])
        self.assertTrue(log.error.called)


class DerEmbedWorkerKannStapeln(unittest.TestCase):
    """`EmbedWorker._call_model` mit `EmbedBatchRequest` — ein Aufruf, ein Vektor je Text."""

    def worker(self, antwort: dict) -> tuple[EmbedWorker, MagicMock]:
        w = EmbedWorker()
        w._client = MagicMock()
        w._client.embed.return_value = antwort
        return w, w._client

    def test_ein_aufruf_mit_der_ganzen_liste(self) -> None:
        w, client = self.worker({"embeddings": [[1.0, 0.0], [0.0, 1.0]]})
        antwort = asyncio.run(w._call_model(EmbedBatchRequest(texts=["a", "b"])))
        self.assertEqual(antwort.embeddings, [[1.0, 0.0], [0.0, 1.0]])
        self.assertEqual(client.embed.call_args.kwargs["input"], ["a", "b"])

    def test_falsche_anzahl_ist_ein_fehler(self) -> None:
        w, _ = self.worker({"embeddings": [[1.0, 0.0]]})
        with self.assertRaises(RuntimeError):
            asyncio.run(w._call_model(EmbedBatchRequest(texts=["a", "b"])))

    def test_leerer_text_im_stapel(self) -> None:
        w, client = self.worker({"embeddings": []})
        with self.assertRaises(ValueError):
            asyncio.run(w._call_model(EmbedBatchRequest(texts=["a", ""])))
        self.assertFalse(client.embed.called)

    def test_der_einzelweg_bleibt(self) -> None:
        w, client = self.worker({"embeddings": [[0.5, 0.5]]})
        antwort = asyncio.run(w._call_model(EmbedRequest(text="a")))
        self.assertEqual(antwort.embedding, [0.5, 0.5])
        self.assertEqual(client.embed.call_args.kwargs["input"], "a")


if __name__ == "__main__":
    unittest.main()
