"""Zeugen für die zwei Routen der Fakten in `api/gedaechtnis.py`.

Was diese Datei zusichert:
  * **Die Liste trägt keine Fakten:** `GET /fakten/{user_id}` liefert je
    Entität genau `id`, `name` und `typ`, liest über
    `EntitaetenRepository.find_by_user` und zeigt keine Entität eines anderen
    Menschen.
  * **Die Mappe hat einen eigenen Pfad:** `GET /fakten/{user_id}/{entitaet_id}`
    antwortet 200 mit Einträgen, 200 mit einer leeren Mappe, 404 bei einer
    unbekannten oder fremden Entität, 500 bei einem Ausfall der Datenbank und
    422 ohne `character_id` — ein Ausfall ist nie eine leere Mappe.
  * **Nur die Herkunft entscheidet:** 422 nur aus der eigenen Prüfung der Route,
    404 nur bei `EntityNotFoundError`; ein ValueError oder LookupError aus dem
    Inneren der Mappe ist 500 mit einer Zeile auf ERROR.

Gefahren wird die Route über `TestClient`, also mit der Prüfung der Parameter
durch FastAPI; die Daten liegen in der Wegwerf-Datenbank der Suite, je Fixture
ein eigenes Paar, abgeräumt in tearDown.
"""

import dataclasses
import unittest
from collections.abc import Callable
from unittest.mock import patch

import psycopg2
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

import memory.fakten_mappe
from api.gedaechtnis import router
from config import POSTGRES_URL
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.repositories.fakten_repository import FaktenRepository, Surroundings
from tests.test_fakten_mappe import FEHLENDE_ENTITAET, MAPPE_MODUL, REPO_MODUL, _GraphFixture

ROUTE_MODUL: str = "api.gedaechtnis"


class _ApiFixture(_GraphFixture):
    """Das Paar aus `_GraphFixture`, dazu ein Client auf den Router."""

    def setUp(self) -> None:
        super().setUp()
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def _mappe_holen(self, entitaet: int, **params: object) -> Response:
        return self.client.get(f"/fakten/{self.user}/{entitaet}",
                               params={"character_id": self.char, **params})

    def _mit_veraenderten_zeilen(
        self, entitaet: int, aendern: Callable[[list[dict]], list[dict]],
    ) -> Response:
        """Holt die Mappe; die echten Zeilen des Repositorys gehen durch `aendern`."""
        echt = FaktenRepository.find_umgebung

        def lesen(*args: object, **kwargs: object) -> Surroundings:
            gelesen: Surroundings = echt(*args, **kwargs)
            return dataclasses.replace(gelesen, rows=tuple(aendern(list(gelesen.rows))))

        with patch(f"{MAPPE_MODUL}.FaktenRepository.find_umgebung", side_effect=lesen):
            return self._mappe_holen(entitaet)

    def _lena_mit_zwei_fakten(self) -> int:
        lena, kassel = self._entitaet("Lena"), self._entitaet("Kassel")
        self._fakt(lena, "wohnt_in", "Lena wohnt in Kassel", objekt=kassel)
        self._fakt(lena, "hobby", "Lena spielt Tennis", wert="Tennis", staerke=0.5)
        return lena


class TheListCarriesNoFactsTest(_ApiFixture):
    """Die Liste — nur `id`, `name`, `typ`, nur dieser Mensch."""

    def test_only_id_name_and_type_of_the_own_entities(self) -> None:
        lena, kassel = self._entitaet("Lena"), self._entitaet("Kassel")
        fremd = self._entitaet("Lena", user=self.fremder)
        self._fakt(lena, "wohnt_in", "Lena wohnt in Kassel", objekt=kassel)
        antwort = self.client.get(f"/fakten/{self.user}")
        self.assertEqual(antwort.status_code, 200)
        entitaeten = antwort.json()["entitaeten"]
        self.assertEqual({e["id"] for e in entitaeten}, {lena, kassel})
        self.assertNotIn(fremd, {e["id"] for e in entitaeten})
        for eintrag in entitaeten:
            with self.subTest(id=eintrag["id"]):
                self.assertEqual(set(eintrag), {"id", "name", "typ"})
        self.assertEqual(antwort.json()["anzahl"], 2)

    def test_the_list_reads_through_the_repository(self) -> None:
        self._entitaet("Lena")
        with patch(f"{ROUTE_MODUL}.EntitaetenRepository.find_by_user",
                   wraps=EntitaetenRepository.find_by_user) as lesen:
            antwort = self.client.get(f"/fakten/{self.user}")
        self.assertEqual(antwort.status_code, 200)
        lesen.assert_called_once_with(POSTGRES_URL, self.user)

    def test_the_twin_a_human_without_entities_has_an_empty_list(self) -> None:
        antwort = self.client.get(f"/fakten/{self.user}")
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json(), {"entitaeten": [], "anzahl": 0})

    def test_a_database_error_is_500_not_an_empty_list(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch("memory.repositories.entitaeten_repository.psycopg2.connect",
                   side_effect=fehler), self.assertLogs("ki_server.gedaechtnis", "ERROR"):
            antwort = self.client.get(f"/fakten/{self.user}")
        self.assertEqual(antwort.status_code, 500)


class TheMappeHasItsOwnPathTest(_ApiFixture):
    """Die Mappe — 200, 200 leer, 404, 500, 422."""

    def test_200_with_the_entries_of_the_mappe(self) -> None:
        lena, kassel = self._entitaet("Lena"), self._entitaet("Kassel")
        wohnt = self._fakt(lena, "wohnt_in", "Lena wohnt in Kassel", objekt=kassel)
        hobby = self._fakt(lena, "hobby", "Lena spielt Tennis", wert="Tennis", staerke=0.5)
        antwort = self._mappe_holen(lena)
        self.assertEqual(antwort.status_code, 200)
        mappe = antwort.json()
        self.assertEqual((mappe["entity_id"], mappe["entity_name"]), (lena, "Lena"))
        self.assertEqual([e["fact_id"] for e in mappe["entries"]], [wohnt, hobby])
        self.assertEqual((mappe["truncated"], mappe["depth"]), (False, 2))

    def test_tiefe_reaches_the_mappe(self) -> None:
        lena, tom, berlin = self._entitaet("Lena"), self._entitaet("Tom"), self._entitaet("Berlin")
        bruder = self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=lena)
        self._fakt(tom, "wohnt_in", "Tom wohnt in Berlin", objekt=berlin)
        antwort = self._mappe_holen(lena, tiefe=1)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual([e["fact_id"] for e in antwort.json()["entries"]], [bruder])
        self.assertEqual(len(self._mappe_holen(lena, tiefe=2).json()["entries"]), 2)

    def test_200_with_an_empty_mappe(self) -> None:
        lena = self._entitaet("Lena")
        antwort = self._mappe_holen(lena)
        self.assertEqual(antwort.status_code, 200)
        mappe = antwort.json()
        self.assertEqual((mappe["entries"], mappe["truncated"], mappe["omitted"]), ([], False, 0))

    def test_404_for_an_unknown_entity(self) -> None:
        self.assertEqual(self._mappe_holen(FEHLENDE_ENTITAET).status_code, 404)

    def test_404_for_an_entity_of_another_human(self) -> None:
        fremd = self._entitaet("Lena", user=self.fremder)
        self.assertEqual(self._mappe_holen(fremd).status_code, 404)

    def test_500_for_a_database_error(self) -> None:
        lena = self._entitaet("Lena")
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch(f"{REPO_MODUL}.psycopg2.connect", side_effect=fehler), \
                self.assertLogs("ki_server.gedaechtnis", "ERROR"):
            antwort = self._mappe_holen(lena)
        self.assertEqual(antwort.status_code, 500)
        self.assertNotIn("entries", antwort.json())

    def test_422_without_character_id(self) -> None:
        lena = self._entitaet("Lena")
        antwort = self.client.get(f"/fakten/{self.user}/{lena}")
        self.assertEqual(antwort.status_code, 422)

    def test_422_for_a_depth_below_one(self) -> None:
        lena = self._entitaet("Lena")
        with patch(f"{ROUTE_MODUL}.load_mappe", wraps=memory.fakten_mappe.load_mappe) as laden:
            antwort = self._mappe_holen(lena, tiefe=0)
        self.assertEqual(antwort.status_code, 422)
        laden.assert_not_called()

    def test_422_for_an_entity_id_below_one(self) -> None:
        with patch(f"{ROUTE_MODUL}.load_mappe", wraps=memory.fakten_mappe.load_mappe) as laden:
            antwort = self._mappe_holen(0)
        self.assertEqual(antwort.status_code, 422)
        laden.assert_not_called()

    def test_the_twin_a_valid_depth_reaches_load_mappe(self) -> None:
        lena = self._entitaet("Lena")
        with patch(f"{ROUTE_MODUL}.load_mappe", wraps=memory.fakten_mappe.load_mappe) as laden:
            antwort = self._mappe_holen(lena, tiefe=1)
        self.assertEqual(antwort.status_code, 200)
        laden.assert_called_once_with(POSTGRES_URL, self.user, self.char, lena, depth=1)


class AFailureInsideIsNot422Or404Test(_ApiFixture):
    """Ein ValueError oder LookupError aus dem Inneren ist ein Ausfall: 500 mit Logzeile.

    Nur die eigene Prüfung der Route ergibt 422, nur `EntityNotFoundError` 404.
    Die Fehler entstehen an den echten Zeilen des Repositorys, verändert erst
    zwischen Repository und Mappe.
    """

    def _pruefe_ausfall(self, antwort: Response) -> None:
        self.assertEqual(antwort.status_code, 500)
        self.assertNotIn("entries", antwort.json())

    def test_entries_out_of_order_are_500_with_a_log_line(self) -> None:
        lena = self._lena_mit_zwei_fakten()
        with self.assertLogs("ki_server.gedaechtnis", "ERROR"):
            antwort = self._mit_veraenderten_zeilen(lena, lambda zeilen: zeilen[::-1])
        self._pruefe_ausfall(antwort)

    def test_a_row_without_fakt_text_is_500_with_a_log_line(self) -> None:
        lena = self._lena_mit_zwei_fakten()

        def ohne_text(zeilen: list[dict]) -> list[dict]:
            return [{**zeilen[0], "fakt_text": ""}, *zeilen[1:]]

        with self.assertLogs("ki_server.gedaechtnis", "ERROR"):
            antwort = self._mit_veraenderten_zeilen(lena, ohne_text)
        self._pruefe_ausfall(antwort)

    def test_a_key_error_from_inside_is_500_not_404(self) -> None:
        # Ein KeyError ist ein LookupError. Die Prüfung der Spalten in der Mappe
        # macht aus einer fehlenden Spalte einen ValueError, deshalb steht der
        # Programmfehler hier für sich: Die Formung einer Zeile wirft ihn.
        lena = self._lena_mit_zwei_fakten()
        with patch(f"{MAPPE_MODUL}._entry_from_row", side_effect=KeyError("fakt_text")), \
                self.assertLogs("ki_server.gedaechtnis", "ERROR"):
            antwort = self._mappe_holen(lena)
        self._pruefe_ausfall(antwort)

    def test_the_twin_unchanged_rows_are_200(self) -> None:
        lena = self._lena_mit_zwei_fakten()
        antwort = self._mit_veraenderten_zeilen(lena, lambda zeilen: zeilen)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(len(antwort.json()["entries"]), 2)


if __name__ == "__main__":
    unittest.main()
