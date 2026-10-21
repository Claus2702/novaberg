"""Zeugen: Ein Ausfall der Auflösung legt nichts still an.

Was diese Datei zusichert:
  * **`resolve_batch` wirft einen Fehler der Suche**, statt ihn als *kein
    Treffer* weiterzugeben — für die Namenssuche, das Embedding der Suche und
    `find_similar`. Eine leere Liste heißt nur noch: Die Suche lief und fand
    nichts (`ist_neu`).
  * **`create_new_entity` legt auch ohne Embedding an**: Die Zeile steht mit
    `embedding IS NULL`, und der Ausfall ist als `error` mit der ID gemeldet.
  * **Der Magnet-Knoten fängt je Name**: Ein Ausfall kostet nur den Namen, an
    dem er auftritt — keine ID, keine Entität, eine Zeile `error`, ein Eintrag
    `fehler` —, die übrigen Namen werden aufgelöst, und der Schritt, der den
    Eintrag des Kurzzeitgedächtnisses schreibt, bekommt ihre IDs.
  * **Der Magnet-Knoten löst nur über den Namen auf**: Ein Name, der einer
    bestehenden Entität nur ähnelt, wird eine neue Entität, auch wenn der
    Embedding-Rückfall die ähnliche fände; *ICH* ohne Entität des Menschen
    fällt aus, statt eine Entität *ICH* anzulegen.

Die Suite läuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums.
Jedes Fixture bringt einen eigenen Menschen mit und räumt in tearDown ab. Kein
Zeuge ruft ein Modell, keiner berührt Redis: Das Embedding, der Redis-Klient
und der Eintrag ins Pipeline-Log werden ersetzt.
"""

import unittest
import uuid
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras

from agents.kzg import magnete
from config import POSTGRES_URL
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.services.entity_resolution import EntityResolutionService, ResolutionResult

VEKTOR: list[float] = [1.0] + [0.0] * 767
LOGGER_AUFLOESUNG: str = "ki_server.memory.services.entity_resolution"
LOGGER_MAGNETE: str = "ki_server.agents.kzg.magnete"
ECHTE_NAMENSSUCHE = EntitaetenRepository.find_by_name


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


def _redis_ohne_agent_state() -> MagicMock:
    klient = MagicMock()
    klient.keys.return_value = []
    return klient


class _UserFixture(unittest.TestCase):
    """Ein eigener Mensch, ein ersetztes Embedding; tearDown räumt Entitäten ab."""

    def setUp(self) -> None:
        self.user = f"test-aufloesung-{uuid.uuid4().hex[:8]}"
        self.modell = MagicMock()
        self.modell.embed.submit_sync.return_value.embedding = VEKTOR
        self.modell.embed.submit_sync.return_value.duration_seconds = 0.0
        ersatz = patch("memory.services.entity_resolution.model_service", self.modell)
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def tearDown(self) -> None:
        _ausfuehren("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _entitaet(self, name: str, typ: str = "person") -> int:
        return _ausfuehren(
            "INSERT INTO entitaeten (user_id, name, typ) VALUES (%s, %s, %s) RETURNING id",
            (self.user, name, typ),
        )[0]["id"]

    def _entitaeten(self) -> list[dict]:
        return _ausfuehren(
            "SELECT id, name, typ, embedding IS NULL AS ohne_vektor FROM entitaeten "
            "WHERE user_id = %s ORDER BY id",
            (self.user,),
        )

    def _namen(self) -> list[str]:
        return [e["name"] for e in self._entitaeten()]


class ResolvingABatchTest(_UserFixture):
    """`resolve_batch`: Ein Ausfall der Suche geht durch, leer heißt nur *nichts gefunden*."""

    def _aufloesen(self, name: str) -> ResolutionResult:
        return EntityResolutionService.resolve_batch(
            [{"name": name, "typ": "person", "ist_referenz": True}],
            POSTGRES_URL, self.user, _redis_ohne_agent_state(),
        )

    def test_a_search_that_finds_nothing_is_new(self) -> None:
        ergebnis = self._aufloesen("Lena")
        self.assertEqual(len(ergebnis.aufgeloest), 1)
        self.assertTrue(ergebnis.aufgeloest[0].ist_neu)
        self.assertEqual(self.modell.embed.submit_sync.call_count, 1)

    def test_a_failing_name_search_raises_and_creates_nothing(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch.object(EntitaetenRepository, "find_by_name", side_effect=fehler):
            with self.assertRaises(psycopg2.OperationalError):
                self._aufloesen("Lena")
        self.assertEqual(self._entitaeten(), [])

    def test_a_failing_search_embedding_raises(self) -> None:
        self.modell.embed.submit_sync.side_effect = TimeoutError("Embedding antwortet nicht")
        with self.assertRaises(TimeoutError):
            self._aufloesen("Lena")
        self.assertEqual(self._entitaeten(), [])

    def test_a_failing_similarity_search_raises(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch.object(EntitaetenRepository, "find_similar", side_effect=fehler):
            with self.assertRaises(psycopg2.OperationalError):
                self._aufloesen("Lena")


class CreatingAnEntityTest(_UserFixture):
    """`create_new_entity`: legt an, auch ohne Vektor — und meldet das als Fehler."""

    def test_with_an_embedding_the_vector_is_set_and_nothing_is_an_error(self) -> None:
        with self.assertLogs(LOGGER_AUFLOESUNG, "INFO") as protokoll:
            neue_id = EntityResolutionService.create_new_entity(POSTGRES_URL, self.user, "Lena")
        self.assertEqual(
            [(e["id"], e["name"], e["ohne_vektor"]) for e in self._entitaeten()],
            [(neue_id, "Lena", False)],
        )
        self.assertEqual([r for r in protokoll.records if r.levelname == "ERROR"], [])

    def test_a_failing_embedding_still_creates_the_entity_and_logs_an_error(self) -> None:
        self.modell.embed.submit_sync.side_effect = TimeoutError("Embedding antwortet nicht")
        with self.assertLogs(LOGGER_AUFLOESUNG, "ERROR") as protokoll:
            neue_id = EntityResolutionService.create_new_entity(POSTGRES_URL, self.user, "Lena")
        self.assertEqual(
            [(e["id"], e["name"], e["ohne_vektor"]) for e in self._entitaeten()],
            [(neue_id, "Lena", True)],
        )
        self.assertEqual(len(protokoll.records), 1)
        self.assertIn(f"ID {neue_id}", protokoll.output[0])
        self.assertIn("TimeoutError", protokoll.output[0])


class _MagnetFixture(_UserFixture):
    """Pipeline-Log des Magnet-Knotens ersetzt; Ilva steht schon."""

    def setUp(self) -> None:
        super().setUp()
        self.ilva = self._entitaet("Ilva")
        self.log_fehler = MagicMock()
        abfang = patch("agents.kzg.magnete.log_fehler", self.log_fehler)
        abfang.start()
        self.addCleanup(abfang.stop)

    def _namenssuche_faellt_aus_fuer(self, ausfall: str) -> "unittest.mock._patch":
        def suche(postgres_url: str, user_id: str, name: str) -> list[dict]:
            if name == ausfall:
                raise psycopg2.OperationalError("Verbindung verloren")  # noqa: TRY003
            return ECHTE_NAMENSSUCHE(postgres_url, user_id, name)
        return patch.object(EntitaetenRepository, "find_by_name", side_effect=suche)

    def _lauf(self, namen: list[str]) -> tuple[dict, list[int] | None]:
        from agents.kzg import agent as kzg_agent

        gespeichert: list[list[int]] = []

        def verdichten(state: dict) -> dict:
            return {"status": "laufend"}

        def speichern(state: dict) -> dict:
            gespeichert.append(list(state["parameter"]["entitaet_ids"]))
            return {"status": "abgeschlossen"}

        def queues_befuellen(state: dict) -> dict:
            return {"status": "abgeschlossen"}

        zustand: dict = {
            "aufgabe": "kzg", "aufgabe_typ": "workflow", "agent_name": "kzg",
            "kontext": {"user_id": self.user, "turn_id": "t-laut"},
            "parameter": {"salienz_obj": {
                "salienz": 1.0, "entitaeten_roh": namen, "zeitausdruck_roh": "",
            }},
            "schritte": [], "ergebnis": None, "status": "laufend",
            "rueckfrage": None, "fehler": None,
        }
        with patch.object(kzg_agent, "verdichten", verdichten), \
             patch.object(kzg_agent, "speichern", speichern), \
             patch.object(kzg_agent, "queues_befuellen", queues_befuellen):
            ende: dict = kzg_agent.KzgAgent().invoke(zustand)
        schritt = [s for s in ende["schritte"] if s["node"] == "magnete_aufloesen"]
        self.assertEqual(len(schritt), 1)
        return schritt[0], gespeichert[0] if gespeichert else None

    def _ids_namens(self, name: str) -> list[int]:
        return [e["id"] for e in self._entitaeten() if e["name"] == name]


class ResolvingMagnetsTest(_MagnetFixture):
    """`_entitaeten_aufloesen`: Ein Ausfall kostet nur seinen Namen."""

    def test_without_a_failure_both_names_get_their_id(self) -> None:
        ids, ausgefallen = magnete._entitaeten_aufloesen(["Lena", "Ilva"], self.user, "t-laut")
        lena = [e["id"] for e in self._entitaeten() if e["name"] == "Lena"]
        self.assertEqual(len(lena), 1)
        self.assertEqual(ids, [lena[0], self.ilva])
        self.assertEqual(ausgefallen, [])
        self.log_fehler.assert_not_called()

    def test_a_failing_search_costs_only_its_name(self) -> None:
        with self._namenssuche_faellt_aus_fuer("Lena"), \
             self.assertLogs(LOGGER_MAGNETE, "ERROR") as protokoll:
            ids, ausgefallen = magnete._entitaeten_aufloesen(
                ["Lena", "Ilva"], self.user, "t-laut",
            )
        self.assertEqual(ids, [self.ilva])
        self.assertEqual(ausgefallen, ["Lena"])
        self.assertEqual(self._namen(), ["Ilva"])
        self.assertEqual(len(protokoll.records), 1)
        self.assertIn("'Lena'", protokoll.output[0])
        self.assertIn("suche", protokoll.output[0])
        self.log_fehler.assert_called_once()
        aufruf = self.log_fehler.call_args.kwargs
        self.assertEqual(
            (aufruf["turn_id"], aufruf["node"], aufruf["quelle"]),
            ("t-laut", "magnete_aufloesen", self.user),
        )
        self.assertEqual(
            (aufruf["inhalt"]["name"], aufruf["inhalt"]["stufe"]), ("Lena", "suche"),
        )
        self.assertIn("OperationalError", aufruf["inhalt"]["fehler"])

    def test_a_failing_insert_costs_only_its_name_at_the_stage_anlegen(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch.object(EntitaetenRepository, "insert", side_effect=fehler), \
             self.assertLogs(LOGGER_MAGNETE, "ERROR"):
            ids, ausgefallen = magnete._entitaeten_aufloesen(
                ["Lena", "Ilva"], self.user, "t-laut",
            )
        self.assertEqual((ids, ausgefallen), ([self.ilva], ["Lena"]))
        self.assertEqual(self.log_fehler.call_args.kwargs["inhalt"]["stufe"], "anlegen")


class MagnetNodeInTheSubgraphTest(_MagnetFixture):
    """Der Knoten im Subgraphen des KzgAgent: Der Ausfall erreicht den Speicher nicht."""

    def test_without_a_failure_the_store_gets_both_magnets(self) -> None:
        schritt, gespeichert = self._lauf(["Lena", "Ilva"])
        lena = [e["id"] for e in self._entitaeten() if e["name"] == "Lena"]
        self.assertEqual(gespeichert, lena + [self.ilva])
        self.assertEqual(len(lena), 1)
        self.assertEqual(schritt["ausgefallen"], [])

    def test_a_failing_search_reaches_the_store_with_the_other_magnet(self) -> None:
        with self._namenssuche_faellt_aus_fuer("Lena"):
            schritt, gespeichert = self._lauf(["Lena", "Ilva"])
        self.assertEqual(gespeichert, [self.ilva])
        self.assertEqual(schritt["ausgefallen"], ["Lena"])
        self.assertEqual(self._namen(), ["Ilva"])

    def test_a_failing_human_lookup_for_ich_is_named_in_the_step(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch.object(EntitaetenRepository, "find_by_type", side_effect=fehler):
            schritt, gespeichert = self._lauf(["ICH", "Ilva"])
        self.assertEqual(gespeichert, [self.ilva])
        self.assertEqual(schritt["ausgefallen"], ["ICH"])
        self.assertEqual(self._namen(), ["Ilva"])

    def test_the_human_resolves_for_ich(self) -> None:
        mensch = self._entitaet("Sam", typ="user")
        schritt, gespeichert = self._lauf(["ICH", "Ilva"])
        self.assertEqual(gespeichert, [mensch, self.ilva])
        self.assertEqual(schritt["ausgefallen"], [])


class MagnetsResolveOnlyByNameTest(_MagnetFixture):
    """Der Magnet-Pfad sucht nur über den Namen: kein Rückfall über Embeddings."""

    def setUp(self) -> None:
        super().setUp()
        # Lea trägt denselben Vektor, den das ersetzte Modell für jeden Namen
        # liefert: Ein Embedding-Rückfall fände sie für "Lena" mit Ähnlichkeit 1,
        # und die Namensprüfung des Rückfalls ließe sie durch (gleicher Anfang,
        # ein Zeichen Unterschied).
        self.lea = EntitaetenRepository.insert(
            POSTGRES_URL, self.user, "Lea", typ="person", embedding=VEKTOR,
        )

    def test_lena_becomes_a_new_entity_and_is_not_bound_to_lea(self) -> None:
        ids, ausgefallen = magnete._entitaeten_aufloesen(["Lena"], self.user, "t-laut")
        lena = self._ids_namens("Lena")
        self.assertEqual(len(lena), 1)
        self.assertNotEqual(lena[0], self.lea)
        self.assertEqual((ids, ausgefallen), (lena, []))

    def test_lea_is_bound_to_lea_and_nothing_is_created(self) -> None:
        ids, ausgefallen = magnete._entitaeten_aufloesen(["Lea"], self.user, "t-laut")
        self.assertEqual((ids, ausgefallen), ([self.lea], []))
        self.assertEqual(self._namen(), ["Ilva", "Lea"])

    def test_lena_through_the_subgraph_stores_the_new_entity(self) -> None:
        schritt, gespeichert = self._lauf(["Lena"])
        lena = self._ids_namens("Lena")
        self.assertEqual(len(lena), 1)
        self.assertNotEqual(lena[0], self.lea)
        self.assertEqual(gespeichert, lena)
        self.assertEqual(schritt["ausgefallen"], [])

    def test_lea_through_the_subgraph_stores_lea(self) -> None:
        schritt, gespeichert = self._lauf(["Lea"])
        self.assertEqual(gespeichert, [self.lea])
        self.assertEqual(self._namen(), ["Ilva", "Lea"])

    def test_the_magnet_path_does_not_call_the_similarity_search(self) -> None:
        with patch.object(EntitaetenRepository, "find_similar", return_value=[]) as aehnlich:
            magnete._entitaeten_aufloesen(["Lena"], self.user, "t-laut")
        aehnlich.assert_not_called()

    def test_resolve_batch_does_call_the_patched_similarity_search(self) -> None:
        with patch.object(EntitaetenRepository, "find_similar", return_value=[]) as aehnlich:
            EntityResolutionService.resolve_batch(
                [{"name": "Lena", "typ": "person", "ist_referenz": True}],
                POSTGRES_URL, self.user, _redis_ohne_agent_state(),
            )
        aehnlich.assert_called_once()

    def test_two_entities_of_one_name_give_no_magnet_and_create_nothing(self) -> None:
        self._entitaet("Lea")
        vorher = self._entitaeten()
        with self.assertLogs(LOGGER_MAGNETE, "INFO") as protokoll:
            ids, ausgefallen = magnete._entitaeten_aufloesen(["Lea"], self.user, "t-laut")
        self.assertEqual((ids, ausgefallen), ([], []))
        self.assertEqual(self._entitaeten(), vorher)
        self.assertTrue(any("mehrdeutig" in z for z in protokoll.output))
        self.assertEqual([r for r in protokoll.records if r.levelname == "ERROR"], [])
        self.log_fehler.assert_not_called()


class MagnetNamesAreNormalizedTest(_MagnetFixture):
    """Leere Namen werden übersprungen, *ICH* ohne Menschen fällt aus, Namen getrimmt."""

    def test_empty_names_are_skipped_without_a_failure(self) -> None:
        ids, ausgefallen = magnete._entitaeten_aufloesen(["", "  ", "Ilva"], self.user, "t-laut")
        self.assertEqual((ids, ausgefallen), ([self.ilva], []))
        self.assertEqual(self._namen(), ["Ilva"])
        self.log_fehler.assert_not_called()

    def test_a_name_alone_resolves_to_its_entity(self) -> None:
        ids, ausgefallen = magnete._entitaeten_aufloesen(["Ilva"], self.user, "t-laut")
        self.assertEqual((ids, ausgefallen), ([self.ilva], []))
        self.log_fehler.assert_not_called()

    def test_ich_without_a_human_fails_and_creates_no_entity_ich(self) -> None:
        with self.assertLogs(LOGGER_MAGNETE, "ERROR") as protokoll:
            ids, ausgefallen = magnete._entitaeten_aufloesen(
                ["ICH", "Ilva"], self.user, "t-laut",
            )
        self.assertEqual((ids, ausgefallen), ([self.ilva], ["ICH"]))
        self.assertEqual(self._namen(), ["Ilva"])
        self.assertEqual(len(protokoll.records), 1)
        aufruf = self.log_fehler.call_args.kwargs
        self.assertEqual(aufruf["inhalt"]["stufe"], "suche")
        self.assertIn("LookupError", aufruf["inhalt"]["fehler"])

    def test_a_padded_name_is_created_trimmed(self) -> None:
        ids, ausgefallen = magnete._entitaeten_aufloesen([" Lena "], self.user, "t-laut")
        lena = self._ids_namens("Lena")
        self.assertEqual(len(lena), 1)
        self.assertEqual((ids, ausgefallen), (lena, []))
        self.assertEqual(self._namen(), ["Ilva", "Lena"])

    def test_an_unpadded_name_is_created_as_is(self) -> None:
        ids, _ = magnete._entitaeten_aufloesen(["Lena"], self.user, "t-laut")
        self.assertEqual(ids, self._ids_namens("Lena"))
        self.assertEqual(self._namen(), ["Ilva", "Lena"])


if __name__ == "__main__":
    unittest.main()
