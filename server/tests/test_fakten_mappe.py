"""Zeugen für die Mappe einer Entität — `find_umgebung` und `memory/fakten_mappe.py`.

Was diese Datei zusichert:
  * **Beide Richtungen, bis zur Tiefe, mit Wert-Fakten:** Die Entität als
    Subjekt und als Objekt, der zweite Grad über die anderen Enden der
    Referenz-Fakten, der dritte erst mit `depth=3`.
  * **Nur das Paar, nur aktiv, nichts Ruhendes — auch nicht als Brücke:** Ein
    Fakt eines anderen Gegenübers, eines anderen Menschen, ein abgelöster und
    eine ruhende Kante fehlen, und über sie wird kein zweiter Grad erreicht.
  * **Kein Lesen schreibt:** `last_touched` bleibt in `fakten` und `entitaeten`.
  * **Gekürzt sagt sich selbst:** Kappung in Zeichen und Grenze der Zeilen
    ergeben `truncated`; *leer* ist nicht gekürzt; ein Ausfall ist eine
    Ausnahme, nie eine leere Mappe.
  * **Die Mappe importiert nur, was sie darf:** die Repositorien der Fakten
    und der Timeline, `config`, `utils.local_time` und die Standardbibliothek.

Die Graphen sind Literale dieser Datei, die Erwartungen von Hand bestimmt.
Die Suite läuft gegen eine Wegwerf-Datenbank aus den Schemadateien des Baums;
jedes Fixture bringt ein eigenes Paar mit und räumt in tearDown ab.

Kein skipUnless, kein skipIf: Fehlt eine Spalte, wird dieser Test rot.
"""

import ast
import sys
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.errors

import memory.fakten_mappe
from config import FAKTEN_MAPPE_MIN_STAERKE, POSTGRES_URL
from memory.fakten_mappe import Mappe, MappeEntry, cap_entries, load_mappe
from memory.repositories.fakten_repository import EntityNotFoundError, FaktenRepository, NewFact

# Ein Zeitpunkt weit vor jedem Lauf: Ein Lesen, das last_touched nachzieht,
# schiebt ihn sichtbar auf heute.
ALTER_ANKER: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
# Eine ID, die keine Entität trägt.
FEHLENDE_ENTITAET: int = 2_000_000_000
REPO_MODUL: str = "memory.repositories.fakten_repository"
MAPPE_MODUL: str = "memory.fakten_mappe"


class _GraphFixture(unittest.TestCase):
    """Ein eigenes Paar, ein zweites Gegenüber desselben Menschen, ein zweiter Mensch."""

    def setUp(self) -> None:
        kennung: str = uuid.uuid4().hex[:8]
        self.user = f"test-mappe-{kennung}"
        self.fremder = f"test-mappe-fremd-{kennung}"
        self.char = "nova-test"
        self.anderer = "andere-test"

    def tearDown(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                for user in (self.user, self.fremder):
                    cur.execute("DELETE FROM fakten WHERE user_id = %s", (user,))
                for user in (self.user, self.fremder):
                    cur.execute("DELETE FROM entitaeten WHERE user_id = %s", (user,))
            conn.commit()
        finally:
            conn.close()

    def _ausfuehren(self, sql: str, params: tuple) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
            conn.commit()
        finally:
            conn.close()

    def _entitaet(self, name: str, user: str | None = None) -> int:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO entitaeten (user_id, name) VALUES (%s, %s) RETURNING id",
                    (user or self.user, name),
                )
                entitaet_id: int = cur.fetchone()[0]
            conn.commit()
        finally:
            conn.close()
        return entitaet_id

    def _fakt(  # noqa: PLR0913 — ein Fakt der Tabelle, ein Argument je Feld
        self,
        subjekt: int,
        attribut: str,
        text: str,
        *,
        objekt: int | None = None,
        wert: str | None = None,
        staerke: float = 1.0,
        char: str | None = None,
        user: str | None = None,
    ) -> int:
        """Legt einen mehrwertigen Fakt an; eine Stärke unter 1 wird danach gesetzt."""
        neu = NewFact(fakt_text=text, herkunft="mensch", einwertig=False,
                      objekt_id=objekt, objekt_wert=wert)
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                fakt_id = FaktenRepository.insert(
                    cur, user or self.user, char or self.char, subjekt, attribut, neu,
                )
                cur.execute("UPDATE fakten SET staerke_decay = %s WHERE id = %s",
                            (staerke, fakt_id))
            conn.commit()
        finally:
            conn.close()
        return fakt_id

    def _mappe(self, start: int, depth: int = 2, max_chars: int = 10_000) -> Mappe:
        return load_mappe(POSTGRES_URL, self.user, self.char, start,
                          depth=depth, max_chars=max_chars)

    @staticmethod
    def _grade(mappe: Mappe) -> dict[int, int]:
        """Fakt-ID → Grad, so wie die Mappe sie trägt."""
        return {e.fact_id: e.degree for e in mappe.entries}


class BothDirectionsInTheFirstDegreeTest(_GraphFixture):
    """Die Entität als Subjekt und als Objekt."""

    def test_subject_and_object_both_stand_in_the_first_degree(self) -> None:
        lena, tom, kassel = self._entitaet("Lena"), self._entitaet("Tom"), self._entitaet("Kassel")
        wohnt = self._fakt(lena, "wohnt_in", "Lena wohnt in Kassel", objekt=kassel)
        bruder = self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=lena)
        mappe = self._mappe(lena, depth=1)
        self.assertEqual(self._grade(mappe), {wohnt: 1, bruder: 1})
        self.assertEqual(mappe.entity_name, "Lena")
        eintrag = {e.fact_id: e for e in mappe.entries}[bruder]
        self.assertEqual((eintrag.subject_name, eintrag.object_name), ("Tom", "Lena"))

    def test_the_twin_a_fact_away_from_the_entity_is_not_in_the_first_degree(self) -> None:
        lena, tom, berlin = self._entitaet("Lena"), self._entitaet("Tom"), self._entitaet("Berlin")
        bruder = self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=lena)
        self._fakt(tom, "wohnt_in", "Tom wohnt in Berlin", objekt=berlin)
        self.assertEqual(self._grade(self._mappe(lena, depth=1)), {bruder: 1})


class ValueFactsInBothDegreesTest(_GraphFixture):
    """Ein Wert-Fakt im ersten und im zweiten Grad."""

    def test_value_facts_stand_in_the_first_and_the_second_degree(self) -> None:
        lena, tom = self._entitaet("Lena"), self._entitaet("Tom")
        beruf = self._fakt(lena, "beruf", "Lena ist Aerztin", wert="Aerztin")
        bruder = self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=lena)
        alter = self._fakt(tom, "alter", "Tom ist 35", wert="35")
        mappe = self._mappe(lena, depth=2)
        self.assertEqual(self._grade(mappe), {beruf: 1, bruder: 1, alter: 2})
        eintrag = {e.fact_id: e for e in mappe.entries}[alter]
        self.assertEqual((eintrag.object_id, eintrag.object_value), (None, "35"))

    def test_the_twin_a_value_fact_does_not_open_a_further_degree(self) -> None:
        lena, kassel = self._entitaet("Lena"), self._entitaet("Kassel")
        beruf = self._fakt(lena, "beruf", "Lena ist Aerztin", wert="Aerztin")
        # Kassel trägt keinen Fakt mit Lena: Der Wert "Aerztin" ist kein Ende,
        # über das ein zweiter Grad erreicht würde.
        self._fakt(kassel, "einwohner", "Kassel hat 200000 Einwohner", wert="200000")
        self.assertEqual(self._grade(self._mappe(lena, depth=2)), {beruf: 1})


class TheDepthIsHeldTest(_GraphFixture):
    """`depth=2` liefert den zweiten Grad und nicht den dritten."""

    def setUp(self) -> None:
        super().setUp()
        self.lena = self._entitaet("Lena")
        tom, berlin, land = self._entitaet("Tom"), self._entitaet("Berlin"), self._entitaet("DE")
        self.eins = self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=self.lena)
        self.zwei = self._fakt(tom, "wohnt_in", "Tom wohnt in Berlin", objekt=berlin)
        self.drei = self._fakt(berlin, "liegt_in", "Berlin liegt in DE", objekt=land)

    def test_depth_two_stops_before_the_third_degree(self) -> None:
        self.assertEqual(self._grade(self._mappe(self.lena, depth=2)), {self.eins: 1, self.zwei: 2})

    def test_depth_three_reaches_the_third_degree(self) -> None:
        self.assertEqual(
            self._grade(self._mappe(self.lena, depth=3)),
            {self.eins: 1, self.zwei: 2, self.drei: 3},
        )

    def test_depth_one_has_only_the_first_degree(self) -> None:
        self.assertEqual(self._grade(self._mappe(self.lena, depth=1)), {self.eins: 1})


class AnotherPairIsMissingAlsoAsABridgeTest(_GraphFixture):
    """Ein anderes Gegenüber, ein anderer Mensch, auch im zweiten Grad."""

    def test_another_character_and_another_human_are_missing(self) -> None:
        lena, paul, rom = self._entitaet("Lena"), self._entitaet("Paul"), self._entitaet("Rom")
        tom = self._entitaet("Tom")
        # Die Brücke Lena–Paul gehört einem anderen Gegenüber; Paul–Rom dem
        # eigenen Paar. Über die fremde Brücke darf Rom nicht erreicht werden.
        self._fakt(lena, "kennt", "Lena kennt Paul", objekt=paul, char=self.anderer)
        self._fakt(paul, "wohnt_in", "Paul wohnt in Rom", objekt=rom)
        # Ein Fakt eines anderen Menschen an derselben Entität.
        self._fakt(lena, "kennt", "Lena kennt Tom", objekt=tom, user=self.fremder)
        # Der Zwilling: das eigene Paar ist da.
        eigen = self._fakt(lena, "beruf", "Lena ist Aerztin", wert="Aerztin")
        self.assertEqual(self._grade(self._mappe(lena, depth=3)), {eigen: 1})

    def test_the_twin_the_same_bridge_in_the_own_pair_is_crossed(self) -> None:
        lena, paul, rom = self._entitaet("Lena"), self._entitaet("Paul"), self._entitaet("Rom")
        kennt = self._fakt(lena, "kennt", "Lena kennt Paul", objekt=paul)
        wohnt = self._fakt(paul, "wohnt_in", "Paul wohnt in Rom", objekt=rom)
        self.assertEqual(self._grade(self._mappe(lena, depth=2)), {kennt: 1, wohnt: 2})

    def test_an_entity_of_another_human_in_an_own_fact_is_a_failure(self) -> None:
        lena, fremd = self._entitaet("Lena"), self._entitaet("Max", user=self.fremder)
        self._fakt(lena, "kennt", "Lena kennt Max", objekt=fremd)
        with self.assertRaisesRegex(RuntimeError, "Namen vollständig: False"):
            self._mappe(lena)


class ASupersededFactIsMissingTest(_GraphFixture):
    """Ein abgelöster Fakt fehlt, auch als Brücke; sein Nachfolger ist da."""

    def test_the_superseded_fact_and_its_bridge_are_missing(self) -> None:
        lena, kassel, hamburg = (self._entitaet("Lena"), self._entitaet("Kassel"),
                                 self._entitaet("Hamburg"))
        alt = self._fakt(lena, "wohnt_in", "Lena wohnt in Kassel", objekt=kassel)
        self._ausfuehren("UPDATE fakten SET aktiv = FALSE, t_invalid = NOW() WHERE id = %s",
                         (alt,))
        neu = self._fakt(lena, "wohnt_in", "Lena wohnt in Hamburg", objekt=hamburg)
        self._fakt(kassel, "liegt_in", "Kassel liegt in Hessen", wert="Hessen")
        hafen = self._fakt(hamburg, "hat", "Hamburg hat einen Hafen", wert="Hafen")
        self.assertEqual(self._grade(self._mappe(lena, depth=2)), {neu: 1, hafen: 2})


class ARestingEdgeIsMissingTest(_GraphFixture):
    """Eine ruhende Kante fehlt, auch als Brücke; knapp darüber ist sie da."""

    def test_the_threshold_is_the_one_these_witnesses_assume(self) -> None:
        # Die Zeugen unten stehen mit Literalen knapp unter und über 0,1.
        self.assertEqual(FAKTEN_MAPPE_MIN_STAERKE, 0.1)

    def test_below_the_threshold_is_missing_just_above_stands(self) -> None:
        lena, eva, wien = self._entitaet("Lena"), self._entitaet("Eva"), self._entitaet("Wien")
        self._fakt(lena, "hobby", "Lena spielt Schach", wert="Schach", staerke=0.09)
        tennis = self._fakt(lena, "hobby", "Lena spielt Tennis", wert="Tennis", staerke=0.11)
        self._fakt(lena, "kennt", "Lena kennt Eva", objekt=eva, staerke=0.05)
        self._fakt(eva, "wohnt_in", "Eva wohnt in Wien", objekt=wien)
        self.assertEqual(self._grade(self._mappe(lena, depth=2)), {tennis: 1})


class NoReadWritesTest(_GraphFixture):
    """`last_touched` bleibt in `fakten` und in `entitaeten`."""

    def _anker(self) -> dict[tuple[str, int], datetime]:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 'f', id, last_touched FROM fakten WHERE user_id = %s "
                            "UNION ALL SELECT 'e', id, last_touched FROM entitaeten "
                            "WHERE user_id = %s", (self.user, self.user))
                return {(r[0], r[1]): r[2] for r in cur.fetchall()}
        finally:
            conn.close()

    def test_last_touched_is_unchanged_after_reading(self) -> None:
        lena, tom = self._entitaet("Lena"), self._entitaet("Tom")
        self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=lena)
        self._fakt(tom, "alter", "Tom ist 35", wert="35")
        for tabelle in ("fakten", "entitaeten"):
            self._ausfuehren(f"UPDATE {tabelle} SET last_touched = %s WHERE user_id = %s",
                             (ALTER_ANKER, self.user))
        vorher = self._anker()
        mappe = self._mappe(lena, depth=2)
        # Die Mappe hat wirklich gelesen — sonst wäre ein unverändertes
        # last_touched kein Befund.
        self.assertEqual(len(mappe.entries), 2)
        self.assertEqual(set(vorher.values()), {ALTER_ANKER})
        self.assertEqual(len(vorher), 4)
        self.assertEqual(self._anker(), vorher)


class TheRowLimitTruncatesTest(_GraphFixture):
    """Die Grenze der Zeilen ergibt `truncated`, in der Ordnung der Stärke."""

    def setUp(self) -> None:
        super().setUp()
        self.lena = self._entitaet("Lena")
        self.stark = self._fakt(self.lena, "hobby", "Lena spielt Tennis", wert="Tennis",
                                staerke=0.9)
        self.mittel = self._fakt(self.lena, "hobby", "Lena spielt Schach", wert="Schach",
                                 staerke=0.6)
        self.schwach = self._fakt(self.lena, "hobby", "Lena malt", wert="Malen", staerke=0.3)

    def _mit_grenze(self, grenze: int) -> Mappe:
        with patch(f"{MAPPE_MODUL}.FAKTEN_MAPPE_MAX_ZEILEN_JE_GRAD", grenze):
            return self._mappe(self.lena, depth=1)

    def test_the_limit_cuts_the_weakest_and_says_so(self) -> None:
        mappe = self._mit_grenze(2)
        self.assertEqual([e.fact_id for e in mappe.entries], [self.stark, self.mittel])
        self.assertTrue(mappe.truncated)
        self.assertEqual(mappe.omitted, 0)

    def test_the_twin_a_limit_above_the_count_cuts_nothing(self) -> None:
        mappe = self._mit_grenze(3)
        self.assertEqual([e.fact_id for e in mappe.entries],
                         [self.stark, self.mittel, self.schwach])
        self.assertFalse(mappe.truncated)

    def test_the_repository_reports_the_limit(self) -> None:
        umgebung = FaktenRepository.find_umgebung(
            POSTGRES_URL, self.user, self.char, self.lena,
            depth=1, min_strength=0.1, max_rows=2,
        )
        self.assertTrue(umgebung.row_limit_hit)
        self.assertEqual([z["id"] for z in umgebung.rows], [self.stark, self.mittel])


class AnUnknownOrForeignEntityIsALookupErrorTest(_GraphFixture):
    """Eine unbekannte oder fremde Entität ergibt `EntityNotFoundError`, einen `LookupError`."""

    def test_an_unknown_entity(self) -> None:
        with self.assertRaises(EntityNotFoundError):
            self._mappe(FEHLENDE_ENTITAET)

    def test_an_entity_of_another_human(self) -> None:
        fremd = self._entitaet("Lena", user=self.fremder)
        with self.assertRaises(EntityNotFoundError):
            self._mappe(fremd)

    def test_the_twin_an_own_entity_is_found(self) -> None:
        lena = self._entitaet("Lena")
        self.assertEqual(self._mappe(lena).entity_name, "Lena")


def _eintrag(fact_id: int, text: str, degree: int = 1, strength: float = 1.0) -> MappeEntry:
    return MappeEntry(
        fact_id=fact_id, degree=degree, subject_id=1, subject_name="Lena",
        relation="hobby", object_id=None, object_name=None, object_value="x",
        text=text, origin="mensch", strength=strength,
    )


class TheCapKeepsTheOrderTest(unittest.TestCase):
    """`cap_entries` hält die Ordnung und das Maximum; rein, ohne Datenbank."""

    # Je 10, 10, 10 und 2 Zeichen, in der Ordnung der Mappe.
    EINTRAEGE: tuple[MappeEntry, ...] = (
        _eintrag(4, "zehn Zeich", strength=0.9),
        _eintrag(3, "zehn Zeich", strength=0.5),
        _eintrag(9, "zehn Zeich", degree=2, strength=1.0),
        _eintrag(8, "zw", degree=2, strength=0.2),
    )

    def test_the_first_entry_that_does_not_fit_ends_the_mappe(self) -> None:
        kept, omitted = cap_entries(self.EINTRAEGE, 25)
        # Der vierte (2 Zeichen) passte noch, rückt aber nicht nach.
        self.assertEqual([e.fact_id for e in kept], [4, 3])
        self.assertEqual(omitted, 2)

    def test_the_twin_a_large_maximum_keeps_everything(self) -> None:
        kept, omitted = cap_entries(self.EINTRAEGE, 1000)
        self.assertEqual(kept, self.EINTRAEGE)
        self.assertEqual(omitted, 0)

    def test_entries_out_of_order_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Ordnung"):
            cap_entries(tuple(reversed(self.EINTRAEGE)), 1000)

    def test_an_invalid_maximum_is_rejected(self) -> None:
        for maximum in (0, True, 1.5):
            with self.subTest(maximum=maximum), self.assertRaises(ValueError):
                cap_entries(self.EINTRAEGE, maximum)


class TheCappedMappeSaysItIsTruncatedTest(_GraphFixture):
    """An der Mappe: gekappt heißt `truncated` und `omitted`."""

    def test_a_small_maximum_truncates(self) -> None:
        lena = self._entitaet("Lena")
        stark = self._fakt(lena, "hobby", "Lena spielt Tennis", wert="Tennis", staerke=0.9)
        self._fakt(lena, "hobby", "Lena spielt Schach", wert="Schach", staerke=0.6)
        mappe = self._mappe(lena, depth=1, max_chars=25)
        self.assertEqual([e.fact_id for e in mappe.entries], [stark])
        self.assertEqual((mappe.truncated, mappe.omitted, mappe.chars), (True, 1, 18))

    def test_the_twin_a_large_maximum_is_not_truncated(self) -> None:
        lena = self._entitaet("Lena")
        self._fakt(lena, "hobby", "Lena spielt Tennis", wert="Tennis", staerke=0.9)
        self._fakt(lena, "hobby", "Lena spielt Schach", wert="Schach", staerke=0.6)
        mappe = self._mappe(lena, depth=1, max_chars=1000)
        self.assertEqual((mappe.truncated, mappe.omitted, mappe.chars), (False, 0, 36))


class EmptyIsNotAFailureTest(_GraphFixture):
    """Ohne Fakten leer; ein Datenbankfehler ist eine Ausnahme."""

    def test_without_facts_the_mappe_is_empty_and_not_truncated(self) -> None:
        lena = self._entitaet("Lena")
        mappe = self._mappe(lena)
        self.assertEqual((mappe.entries, mappe.truncated, mappe.omitted, mappe.chars),
                         ((), False, 0, 0))

    def test_a_database_error_is_an_exception(self) -> None:
        lena = self._entitaet("Lena")
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch(f"{REPO_MODUL}.psycopg2.connect", side_effect=fehler) as verbinden, \
                self.assertRaises(psycopg2.OperationalError):
            self._mappe(lena)
        verbinden.assert_called_once_with(POSTGRES_URL)

    def test_a_failing_query_is_an_exception(self) -> None:
        conn = MagicMock()
        conn.cursor.return_value.fetchone.return_value = {"name": "Lena"}
        conn.cursor.return_value.execute.side_effect = [
            None, psycopg2.errors.UndefinedColumn("staerke_decay"),
        ]
        with patch(f"{REPO_MODUL}.psycopg2.connect", return_value=conn), \
                self.assertRaises(psycopg2.errors.UndefinedColumn):
            load_mappe("postgresql://attrappe", "u", "c", 7)
        conn.close.assert_called_once_with()


class AFactReachedTwiceStandsOnceTest(_GraphFixture):
    """Ein Fakt, der zweimal erreicht wird, steht einmal da, mit dem kleinsten Grad."""

    def test_a_triangle_gives_each_fact_once(self) -> None:
        lena, tom, berlin = self._entitaet("Lena"), self._entitaet("Tom"), self._entitaet("Berlin")
        bruder = self._fakt(tom, "ist_bruder_von", "Tom ist Bruder von Lena", objekt=lena)
        lebt = self._fakt(lena, "wohnt_in", "Lena wohnt in Berlin", objekt=berlin)
        # Von Tom und von Berlin aus erreichbar, beide Front des zweiten Grades.
        tom_berlin = self._fakt(tom, "wohnt_in", "Tom wohnt in Berlin", objekt=berlin)
        mappe = self._mappe(lena, depth=3)
        self.assertEqual(len(mappe.entries), 3)
        self.assertEqual(self._grade(mappe), {bruder: 1, lebt: 1, tom_berlin: 2})


class EveryRowIsVerifiedTest(unittest.TestCase):
    """`find_umgebung` weist eine Zeile ab, die ihre Abfrage nicht liefern dürfte.

    Die Attrappe der Verbindung liefert sie mit Absicht. Der Zwilling im selben
    Aufbau: eine Zeile des Paares geht durch.
    """

    def _zeile(self, **abweichung: object) -> dict:
        zeile: dict = {
            "id": 7, "user_id": "u", "character_id": "c", "aktiv": True,
            "subjekt_id": 3, "subjekt_name": "Lena", "attribut": "hobby",
            "objekt_id": None, "objekt_name": None, "objekt_wert": "Tennis",
            "fakt_text": "Lena spielt Tennis", "herkunft": "mensch", "staerke_decay": 0.5,
        }
        zeile.update(abweichung)
        return zeile

    def _lesen(self, zeile: dict) -> object:
        conn = MagicMock()
        conn.cursor.return_value.fetchone.return_value = {"name": "Lena"}
        conn.cursor.return_value.fetchall.return_value = [zeile]
        with patch(f"{REPO_MODUL}.psycopg2.connect", return_value=conn):
            ergebnis = FaktenRepository.find_umgebung(
                "postgresql://attrappe", "u", "c", 3,
                depth=1, min_strength=0.1, max_rows=10,
            )
        conn.set_session.assert_called_once_with(readonly=True)
        return ergebnis

    def test_a_row_of_another_character_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "character_id"):
            self._lesen(self._zeile(character_id="andere"))

    def test_a_row_away_from_the_front_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "berührt die Front: False"):
            self._lesen(self._zeile(subjekt_id=99))

    def test_a_resting_row_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Stärke 0.05"):
            self._lesen(self._zeile(staerke_decay=0.05))

    def test_the_twin_a_row_of_the_pair_passes(self) -> None:
        umgebung = self._lesen(self._zeile())
        self.assertEqual([z["id"] for z in umgebung.rows], [7])
        self.assertEqual(umgebung.rows[0]["grad"], 1)


def _verbotene_importe(quelltext: str) -> list[str]:
    """Nennt jeden Import außerhalb der erlaubten Module und der Standardbibliothek.

    Erlaubt sind die Repositorien, `config` und `utils.local_time`. Das
    Repository der Timeline und `utils.local_time` kamen mit dem Verweis eines
    Fakts auf ein Ereignis dazu: Die Mappe folgt ihm über `aktive_zeile` und
    nennt den Monat mit `month_label`.
    """
    erlaubt: set[str] = {
        "config", "memory.repositories.fakten_repository",
        "memory.repositories.timeline_repository", "utils.local_time",
    }
    gefunden: list[str] = []
    for knoten in ast.walk(ast.parse(quelltext)):
        if isinstance(knoten, ast.Import):
            gefunden.extend(a.name for a in knoten.names)
        elif isinstance(knoten, ast.ImportFrom):
            gefunden.append("." * knoten.level + (knoten.module or ""))
    return [
        name for name in gefunden
        if name not in erlaubt and name.split(".")[0] not in sys.stdlib_module_names
    ]


class TheMappeImportsOnlyWhatItMayTest(unittest.TestCase):
    """Die Wand prüft `memory/*.py` nicht; dieser Zeuge tut es."""

    def test_the_mappe_has_only_allowed_imports(self) -> None:
        quelle = Path(memory.fakten_mappe.__file__).read_text(encoding="utf-8")
        self.assertIn("memory.repositories.fakten_repository", quelle)
        self.assertEqual(_verbotene_importe(quelle), [])

    def test_the_twin_forbidden_imports_are_recognised(self) -> None:
        verstoss = ("from graph.nodes import planner\nimport psycopg2\n"
                    "from agents.fakten import crud\nfrom . import utils\n")
        self.assertEqual(_verbotene_importe(verstoss),
                         ["graph.nodes", "psycopg2", "agents.fakten", "."])


if __name__ == "__main__":
    unittest.main()
