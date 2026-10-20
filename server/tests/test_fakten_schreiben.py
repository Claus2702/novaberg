"""Zeugen für den Schreibweg eines Fakts: `schreiben` und die Auflösung über den Namen.

Was diese Datei zusichert:
  * **Eine einwertige Beziehung wird abgelöst**: genau ein aktiver Wert, der alte
    bleibt mit `t_invalid` in der Historie.
  * **Derselbe Wert schreibt nichts**, er zieht nur `last_touched` nach — gegen
    jeden aktiven Wert, nicht nur den jüngsten.
  * **Eine mehrwertige Beziehung fügt hinzu**: zwei Haustiere bleiben beide aktiv.
  * **Eine Schreibung gilt ganz oder gar nicht**: Scheitert das Anlegen nach dem
    Invalidieren, ist nach dem Rollback der alte Wert aktiv und keine Zeile neu.
  * **Die Auflösung über den Namen bindet keinen ähnlichen Namen** (*Lena* nicht
    an *Lea*) und **wirft einen Fehler der Suche**, statt null Treffer zu melden.

Die Suite läuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums.
Jedes Fixture bringt ein eigenes Paar mit und räumt in tearDown ab. Kein
Zeuge ruft ein Modell: Das Embedding wird ersetzt, wo der Bestand es erreichen
könnte.
"""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras

from config import POSTGRES_URL
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.repositories.fakten_repository import (
    FaktenRepository,
    NewFact,
    Schreibung,
)
from memory.services.entity_resolution import EntityResolutionService

# Ein Zeitpunkt weit vor jedem Lauf: Ein Schreiben, das last_touched nachzieht,
# schiebt ihn sichtbar auf heute.
ALTER_ANKER: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
VEKTOR: list[float] = [1.0] + [0.0] * 767


def _neu(
    text: str,
    wert: str | None = None,
    einwertig: bool = True,
    herkunft: str = "mensch",
    objekt_id: int | None = None,
) -> NewFact:
    return NewFact(
        fakt_text=text, herkunft=herkunft, einwertig=einwertig,
        objekt_id=objekt_id, objekt_wert=wert,
    )


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


class _UserFixture(unittest.TestCase):
    """Ein eigener Mensch und eine Figur; tearDown räumt Fakten und Entitäten ab."""

    def setUp(self) -> None:
        self.user = f"test-schreib-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"

    def tearDown(self) -> None:
        _ausfuehren("DELETE FROM fakten WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _entitaet(self, name: str, typ: str = "person") -> int:
        return _ausfuehren(
            "INSERT INTO entitaeten (user_id, name, typ) VALUES (%s, %s, %s) RETURNING id",
            (self.user, name, typ),
        )[0]["id"]

    def _fakten(self) -> list[dict]:
        return _ausfuehren(
            "SELECT * FROM fakten WHERE user_id = %s ORDER BY id", (self.user,),
        )

    def _entitaeten(self) -> list[dict]:
        return _ausfuehren(
            "SELECT id, name, typ FROM entitaeten WHERE user_id = %s ORDER BY id", (self.user,),
        )


class WritingAFactTest(_UserFixture):
    """`schreiben`: identisch, angelegt oder abgelöst — in einer Transaktion."""

    def setUp(self) -> None:
        super().setUp()
        self.subjekt = self._entitaet("Michael")

    def _schreiben(self, attribut: str, neu: NewFact) -> Schreibung:
        return FaktenRepository.schreiben(
            POSTGRES_URL, self.user, self.char, self.subjekt, attribut, neu,
        )

    def test_kassel_is_replaced_by_hamburg(self) -> None:
        kassel = self._schreiben("wohnt_in", _neu("Michael wohnt in Kassel", "Kassel"))
        hamburg = self._schreiben("wohnt_in", _neu("Michael wohnt in Hamburg", "Hamburg"))
        self.assertEqual(kassel.art, "angelegt")
        self.assertEqual(hamburg.art, "abgeloest")
        zeilen = {z["id"]: z for z in self._fakten()}
        self.assertEqual(sorted(zeilen), [kassel.fakt_id, hamburg.fakt_id])
        self.assertEqual([i for i, z in zeilen.items() if z["aktiv"]], [hamburg.fakt_id])
        self.assertIsNotNone(zeilen[kassel.fakt_id]["t_invalid"])
        self.assertIsNone(zeilen[hamburg.fakt_id]["t_invalid"])
        self.assertEqual(
            (zeilen[hamburg.fakt_id]["herkunft"], zeilen[hamburg.fakt_id]["character_id"]),
            ("mensch", self.char),
        )

    def test_the_same_value_writes_no_row_and_touches_it(self) -> None:
        kassel = self._schreiben("wohnt_in", _neu("Michael wohnt in Kassel", "Kassel"))
        _ausfuehren(
            "UPDATE fakten SET last_touched = %s WHERE id = %s", (ALTER_ANKER, kassel.fakt_id),
        )
        wieder = self._schreiben("wohnt_in", _neu("Michael wohnt in kassel", " kassel "))
        self.assertEqual(wieder, Schreibung(fakt_id=kassel.fakt_id, art="identisch"))
        zeilen = self._fakten()
        self.assertEqual([(z["id"], z["aktiv"]) for z in zeilen], [(kassel.fakt_id, True)])
        self.assertGreater(zeilen[0]["last_touched"], ALTER_ANKER)

    def test_two_pets_both_stay_active(self) -> None:
        bello = self._schreiben("hat_haustier", _neu("Michael hat Bello", "Bello", False))
        rex = self._schreiben("hat_haustier", _neu("Michael hat Rex", "Rex", False))
        self.assertEqual((bello.art, rex.art), ("angelegt", "angelegt"))
        self.assertEqual(
            [(z["objekt_wert"], z["aktiv"]) for z in self._fakten()],
            [("Bello", True), ("Rex", True)],
        )

    def test_the_second_dog_is_identical_though_not_the_youngest(self) -> None:
        self._schreiben("hat_haustier", _neu("Michael hat Bello", "Bello", False))
        rex = self._schreiben("hat_haustier", _neu("Michael hat Rex", "Rex", False))
        self._schreiben("hat_haustier", _neu("Michael hat Fiffi", "Fiffi", False))
        wieder = self._schreiben("hat_haustier", _neu("Michael hat Rex", "Rex", False))
        self.assertEqual(wieder, Schreibung(fakt_id=rex.fakt_id, art="identisch"))
        self.assertEqual(
            [z["objekt_wert"] for z in self._fakten() if z["aktiv"]], ["Bello", "Rex", "Fiffi"],
        )

    def test_the_same_object_entity_is_identical_and_another_is_added(self) -> None:
        lena = self._entitaet("Lena")
        anna = self._entitaet("Anna")
        erste = self._schreiben("kennt", _neu("Michael kennt Lena", None, False, objekt_id=lena))
        wieder = self._schreiben("kennt", _neu("Michael kennt Lena", None, False, objekt_id=lena))
        anders = self._schreiben("kennt", _neu("Michael kennt Anna", None, False, objekt_id=anna))
        self.assertEqual(wieder, Schreibung(fakt_id=erste.fakt_id, art="identisch"))
        self.assertEqual(anders.art, "angelegt")
        self.assertEqual([z["objekt_id"] for z in self._fakten()], [lena, anna])

    def test_a_failed_insert_keeps_kassel_active(self) -> None:
        kassel = self._schreiben("wohnt_in", _neu("Michael wohnt in Kassel", "Kassel"))
        # Die Herkunft prüft `insert` — nach dem Invalidieren von Kassel.
        with self.assertRaises(ValueError):
            self._schreiben(
                "wohnt_in", _neu("Michael wohnt in Hamburg", "Hamburg", herkunft="altbestand"),
            )
        self.assertEqual(
            [(z["id"], z["aktiv"], z["t_invalid"]) for z in self._fakten()],
            [(kassel.fakt_id, True, None)],
        )

    def test_both_object_and_value_are_refused_without_a_row(self) -> None:
        lena = self._entitaet("Lena")
        with self.assertRaises(ValueError):
            self._schreiben("kennt", _neu("Michael kennt Lena", "Lena", False, objekt_id=lena))
        self.assertEqual(self._fakten(), [])

    def test_an_unknown_kind_of_writing_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            Schreibung(fakt_id=1, art="ueberschrieben")
        self.assertEqual(Schreibung(fakt_id=1, art="abgeloest").art, "abgeloest")


class ResolvingByNameTest(_UserFixture):
    """`resolve_by_name`: nur der Name, kein Rückfall, kein verschluckter Fehler."""

    def setUp(self) -> None:
        super().setUp()
        # Lea trägt denselben Vektor, den das ersetzte Modell für jeden Namen
        # liefert: Ein Embedding-Rückfall fände sie für "Lena" mit Ähnlichkeit 1,
        # und die Namensprüfung des Bestands ließe sie durch (gleicher Anfang,
        # ein Zeichen Unterschied).
        self.lea = EntitaetenRepository.insert(
            POSTGRES_URL, self.user, "Lea", typ="person", embedding=VEKTOR,
        )
        modell = MagicMock()
        modell.embed.submit_sync.return_value.embedding = VEKTOR
        modell.embed.submit_sync.return_value.duration_seconds = 0.0
        ersatz = patch("memory.services.entity_resolution.model_service", modell)
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def test_lena_is_not_bound_to_lea(self) -> None:
        self.assertEqual(
            EntityResolutionService.resolve_by_name(POSTGRES_URL, self.user, "Lena"), [],
        )

    def test_lea_is_found_by_her_name_in_any_case(self) -> None:
        treffer = EntityResolutionService.resolve_by_name(POSTGRES_URL, self.user, " lea ")
        self.assertEqual([(t["id"], t["name"]) for t in treffer], [(self.lea, "Lea")])

    def test_two_entities_of_one_name_are_both_returned(self) -> None:
        zweite = self._entitaet("Lea")
        treffer = EntityResolutionService.resolve_by_name(POSTGRES_URL, self.user, "Lea")
        self.assertEqual(sorted(t["id"] for t in treffer), [self.lea, zweite])

    def test_a_database_error_is_raised_and_creates_nothing(self) -> None:
        vorher = self._entitaeten()
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch.object(EntitaetenRepository, "find_by_name", side_effect=fehler):
            with self.assertRaises(psycopg2.OperationalError):
                EntityResolutionService.resolve_by_name(POSTGRES_URL, self.user, "Lena")
        self.assertEqual(self._entitaeten(), vorher)

    def test_ich_is_the_human(self) -> None:
        mensch = self._entitaet("Sam", typ="user")
        treffer = EntityResolutionService.resolve_by_name(POSTGRES_URL, self.user, "ich")
        self.assertEqual([t["id"] for t in treffer], [mensch])

    def test_ich_without_a_human_raises_and_creates_nothing(self) -> None:
        vorher = self._entitaeten()
        with self.assertRaises(LookupError):
            EntityResolutionService.resolve_by_name(POSTGRES_URL, self.user, "ICH")
        self.assertEqual(self._entitaeten(), vorher)


if __name__ == "__main__":
    unittest.main()
