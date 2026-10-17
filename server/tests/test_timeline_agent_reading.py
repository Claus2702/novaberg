"""Zeugen: Der Leseast des Timeline-Agenten liest ueber den gemeinsamen Leseweg.

Eine Frage nach einem Zeitraum (*„Habe ich im November schon Termine?“*) las
ein Fenster von einem Tag: Aus *im November* wurde ein Tag im November, und
ein Termin am 06.11. fehlte. Nur *woche* und *monat* im Text weiteten das
Fenster, *am Wochenende* las Montag bis Sonntag.

Zeugen dieser Datei:
  * **Zeitraum** — `named_period` liest Monat, Monatsname, Woche und
    Wochenende als ganzen Zeitraum; ein Tag bleibt ein Tag.
  * **Leseast** — `suchen` liest mit `read_appointments`, die Zeilen sind die
    von `appointment_line`, ein Erinnerungs-Anker steht nicht darin.
  * **Schreibweg ohne Titel** — Aendern, Loeschen und Verschieben aus einem
    Zeitraum klaeren bei keinem, einem und mehreren Treffern: Die Klaerung
    nennt die gefundenen Termine und bittet um den Namen. Keine Antwort darauf
    schreibt, auch kein *„Ja“*. Ein Erinnerungs-Anker ist nie ein Kandidat.
  * **Auswahl** — keine Antwort auf eine Auswahl waehlt oder schreibt, mit
    oder ohne Titel; die Klaerung nennt die Kandidaten mit Datum und
    verspricht keinen Weg. Ein neuer Auftrag mit Titel geht den Weg mit
    Titel; mehrere Treffer gehen auch beim Verschieben in die Auswahl.
  * **Eine Quelle** — der Anker-Typ und das proaktive Fenster stehen je an
    einer Stelle.

Ohne Datenbank, Netz und Modell; die Beispiele sind synthetisch. Kein
skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import json
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from langgraph.graph import END

import config
from agents.timeline import magneten, resume, suche
from agents.timeline.agent import TimelineAgent
from memory import timeline_inventory, timeline_reading
from memory.timeline_inventory import ANCHOR_TYPE
from utils.zeitparser import named_period

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")
#: Der Tag der Frage *„Habe ich im November schon Termine?“*, ein Samstag.
SATURDAY: datetime = datetime(2026, 10, 17, 12, 0, tzinfo=BERLIN)
WEDNESDAY: datetime = datetime(2026, 10, 14, 10, 0, tzinfo=BERLIN)
ANCHOR_LITERAL: str = "erinnerungs_anker"
#: Die Zeile des Elternabends, gelesen am Samstag, 17.10.2026.
PARENTS_EVENING_LINE: str = "- Freitag, 06.11.2026, 19:00 Uhr — Elternabend (in 20 Tagen)"


def _row(row_id: int, moment: datetime, title: str, event_type: str = "termin") -> dict:
    """Eine Timeline-Zeile, wie das Repository sie liefert."""
    return {
        "id": row_id, "event_time": moment, "title": title, "event_type": event_type,
        "precision": "minute", "details": "", "aktiv": True,
    }


class _Timeline:
    """Doppel des Repositorys: liefert die Zeilen im Fenster und schreibt die Abfragen mit.

    Mit `honour_exclusion=False` liefert es auch ausgeschlossene Typen — so
    sieht ein Zeuge, ob der Leser dahinter einen Anker verwirft.
    """

    def __init__(self, rows: list[dict], honour_exclusion: bool = True) -> None:
        self.rows: list[dict] = rows
        self.honour_exclusion: bool = honour_exclusion
        self.ranges: list[tuple[datetime, datetime, tuple[str, ...]]] = []
        self.keywords: list[tuple[str, str, int, tuple[str, ...]]] = []

    def _visible(self, excluded: tuple[str, ...]) -> list[dict]:
        hidden: tuple[str, ...] = tuple(excluded) if self.honour_exclusion else ()
        return [r for r in self.rows if r["event_type"] not in hidden]

    def find_by_date_range(
        self, postgres_url: str, user_id: str, von: datetime, bis: datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        self.ranges.append((von, bis, tuple(exclude_event_types)))
        return [r for r in self._visible(exclude_event_types) if von <= r["event_time"] <= bis]

    def find_by_keyword(self, *args: object, **options: object) -> list[dict]:
        """Wie das Repository: URL, Nutzer, Wort, Richtung, Grenze, dann die Optionen."""
        keyword, direction, limit = str(args[2]), str(args[3]), int(args[4])
        excluded: tuple[str, ...] = tuple(options.get("exclude_event_types", ()))
        self.keywords.append((keyword, direction, limit, excluded))
        found: list[dict] = [
            r for r in self._visible(excluded) if keyword.lower() in r["title"].lower()
        ]
        return found[:limit]


def _state(action: str, zeitausdruck: str = "", target: str = "") -> dict:
    return {
        "parameter": {"action": action, "target": target, "zeitausdruck": zeitausdruck},
        "kontext": {"user_id": "pruefer"}, "aufgabe": "", "schritte": [],
    }


def _run(state: dict, timeline: _Timeline, now: datetime) -> dict:
    """Faehrt `suchen` gegen das Doppel, auf beiden Wegen zum Repository."""
    with patch("memory.timeline_reading.TimelineRepository", timeline), \
            patch("memory.repositories.timeline_repository.TimelineRepository", timeline), \
            patch("agents.timeline.suche.now_local", return_value=now):
        return suche.suchen(state)


#: Der Bestand der Frage nach dem November: der Elternabend, ein Anker am selben Tag, je ein
#: Termin knapp vor und knapp nach dem November, einer am Monatsende.
NOVEMBER_STOCK: list[dict] = [
    _row(1, datetime(2026, 10, 31, 18, 0, tzinfo=BERLIN), "Herbstfest"),
    _row(2, datetime(2026, 11, 6, 9, 0, tzinfo=BERLIN), "Anker Elternabend", ANCHOR_LITERAL),
    _row(3, datetime(2026, 11, 6, 19, 0, tzinfo=BERLIN), "Elternabend"),
    _row(4, datetime(2026, 11, 30, 20, 0, tzinfo=BERLIN), "Abschlussessen"),
    _row(5, datetime(2026, 12, 1, 17, 0, tzinfo=BERLIN), "Laternenlauf"),
]


class NovemberQuestionTest(unittest.TestCase):
    """*„Habe ich im November schon Termine?“* — der ganze November."""

    def test_in_november_names_the_parents_evening(self) -> None:
        timeline = _Timeline(NOVEMBER_STOCK)
        result: dict = _run(_state("read", "im November"), timeline, SATURDAY)

        self.assertEqual(result["status"], "abgeschlossen")
        self.assertEqual(
            result["ergebnis"].split("\n"),
            [
                "- Freitag, 06.11.2026, 19:00 Uhr — Elternabend (in 20 Tagen)",
                "- Montag, 30.11.2026, 20:00 Uhr — Abschlussessen (in 44 Tagen)",
            ],
        )
        self.assertEqual(
            timeline.ranges[0][:2],
            (datetime(2026, 11, 1, 0, 0, tzinfo=BERLIN),
             datetime(2026, 11, 30, 23, 59, 59, tzinfo=BERLIN)),
        )

    def test_twin_an_empty_november_names_the_window(self) -> None:
        """Leer heisst: der ganze November ist leer — und das steht so da."""
        stock: list[dict] = [NOVEMBER_STOCK[0], NOVEMBER_STOCK[4]]
        result: dict = _run(_state("read", "im November"), _Timeline(stock), SATURDAY)

        self.assertEqual(result["ergebnis"], "Keine Termine vom 01.11.2026 bis 30.11.2026.")


#: Eine Woche um das Wochenende: Freitag davor, Samstag, Sonntag, Montag danach.
WEEKEND_STOCK: list[dict] = [
    _row(1, datetime(2026, 10, 16, 18, 0, tzinfo=BERLIN), "Kino"),
    _row(2, datetime(2026, 10, 17, 10, 0, tzinfo=BERLIN), "Flohmarkt"),
    _row(3, datetime(2026, 10, 18, 11, 0, tzinfo=BERLIN), "Brunch"),
    _row(4, datetime(2026, 10, 19, 8, 0, tzinfo=BERLIN), "Zahnarzt"),
]


class WeekendTest(unittest.TestCase):
    """*am Wochenende* ist Samstag und Sonntag, nicht Montag bis Sonntag."""

    def test_weekend_reads_saturday_and_sunday(self) -> None:
        result: dict = _run(_state("read", "am Wochenende"), _Timeline(WEEKEND_STOCK), WEDNESDAY)

        self.assertEqual(
            result["ergebnis"].split("\n"),
            [
                "- Samstag, 17.10.2026, 10:00 Uhr — Flohmarkt (in 3 Tagen)",
                "- Sonntag, 18.10.2026, 11:00 Uhr — Brunch (in 4 Tagen)",
            ],
        )

    def test_weekend_period_is_saturday_to_sunday(self) -> None:
        self.assertEqual(
            named_period("am Wochenende", date(2026, 10, 14)),
            (date(2026, 10, 17), date(2026, 10, 18)),
        )

    def test_twin_this_week_is_monday_to_sunday(self) -> None:
        """Die Woche bleibt Montag bis Sonntag — nur das Wochenende ist kuerzer."""
        self.assertEqual(
            named_period("diese Woche", date(2026, 10, 14)),
            (date(2026, 10, 12), date(2026, 10, 18)),
        )


class SingleDayTest(unittest.TestCase):
    """Ein Ausdruck, der einen Tag nennt, liest einen Tag."""

    def test_tomorrow_is_one_day(self) -> None:
        window = suche.time_window("morgen", WEDNESDAY)

        self.assertEqual(
            (window.start, window.end),
            (datetime(2026, 10, 15, 0, 0, tzinfo=BERLIN),
             datetime(2026, 10, 15, 23, 59, 59, tzinfo=BERLIN)),
        )

    def test_on_friday_is_one_day(self) -> None:
        window = suche.time_window("am Freitag", WEDNESDAY)

        self.assertEqual(
            (window.start, window.end),
            (datetime(2026, 10, 16, 0, 0, tzinfo=BERLIN),
             datetime(2026, 10, 16, 23, 59, 59, tzinfo=BERLIN)),
        )

    def test_day_expressions_name_no_period(self) -> None:
        for text in ("morgen", "am Freitag", "am 17.10.", "6. November", "heute"):
            with self.subTest(text=text):
                self.assertIsNone(named_period(text, date(2026, 10, 14)))

    def test_twin_month_name_alone_names_a_period(self) -> None:
        """Derselbe Monat ohne Tageszahl ist ein Zeitraum — der Zwilling zu *6. November*."""
        self.assertEqual(
            named_period("November", date(2026, 10, 14)),
            (date(2026, 11, 1), date(2026, 11, 30)),
        )


class NamedPeriodTest(unittest.TestCase):
    """Monat, Monatsname und Woche, mit Richtung — gerechnet von Hand."""

    def _assert_period(self, text: str, today: date, first: date, last: date) -> None:
        self.assertEqual(named_period(text, today), (first, last), text)

    def test_past_month_name_is_this_years_past_month(self) -> None:
        """*im September*, gefragt im Oktober: der vergangene September, nicht der naechste."""
        self._assert_period("im September", date(2026, 10, 17), date(2026, 9, 1), date(2026, 9, 30))

    def test_next_with_past_month_name_is_next_year(self) -> None:
        self._assert_period(
            "nächsten September", date(2026, 10, 17), date(2027, 9, 1), date(2027, 9, 30),
        )

    def test_next_with_coming_month_name_stays_this_year(self) -> None:
        self._assert_period(
            "naechsten November", date(2026, 10, 17), date(2026, 11, 1), date(2026, 11, 30),
        )

    def test_last_with_coming_month_name_is_last_year(self) -> None:
        self._assert_period(
            "letzten November", date(2026, 10, 17), date(2025, 11, 1), date(2025, 11, 30),
        )

    def test_month_name_with_year(self) -> None:
        self._assert_period(
            "November 2027", date(2026, 10, 17), date(2027, 11, 1), date(2027, 11, 30),
        )

    def test_leap_february(self) -> None:
        self._assert_period("im Februar", date(2028, 1, 5), date(2028, 2, 1), date(2028, 2, 29))

    def test_maerz_with_and_without_umlaut(self) -> None:
        for text in ("im März", "im Maerz"):
            with self.subTest(text=text):
                self._assert_period(text, date(2026, 10, 17), date(2026, 3, 1), date(2026, 3, 31))

    def test_misspelled_month_name(self) -> None:
        self._assert_period("im Novmber", date(2026, 10, 17), date(2026, 11, 1), date(2026, 11, 30))

    def test_this_month(self) -> None:
        self._assert_period(
            "diesen Monat", date(2026, 10, 17), date(2026, 10, 1), date(2026, 10, 31),
        )

    def test_next_month_crosses_the_year(self) -> None:
        self._assert_period(
            "nächsten Monat", date(2026, 12, 10), date(2027, 1, 1), date(2027, 1, 31),
        )

    def test_next_week(self) -> None:
        self._assert_period(
            "nächste Woche", date(2026, 10, 17), date(2026, 10, 19), date(2026, 10, 25),
        )

    def test_in_two_weeks_is_that_week(self) -> None:
        self._assert_period(
            "in zwei Wochen", date(2026, 10, 14), date(2026, 10, 26), date(2026, 11, 1),
        )

    def test_unknown_word_names_no_period(self) -> None:
        for text in ("das Wochenende danach", "Wochen", "", "die naechsten zwei Wochen"):
            with self.subTest(text=text):
                self.assertIsNone(named_period(text, date(2026, 10, 14)))


class SharedReadingPathTest(unittest.TestCase):
    """Der Leseast liest mit `read_appointments` und schreibt die Zeilen von `appointment_line`."""

    def test_read_goes_through_read_appointments_and_drops_the_anchor(self) -> None:
        """Das Doppel liefert den Anker trotz Ausschluss — der Leser verwirft ihn laut."""
        timeline = _Timeline(NOVEMBER_STOCK[1:3], honour_exclusion=False)
        with patch(
            "memory.timeline_reading.read_appointments", wraps=timeline_reading.read_appointments,
        ) as shared, self.assertLogs("ki_server.memory.timeline_reading", level="ERROR"):
            result: dict = _run(_state("read", "im November"), timeline, SATURDAY)

        shared.assert_called_once()
        self.assertEqual(result["ergebnis"], PARENTS_EVENING_LINE)
        self.assertNotIn("Anker", result["ergebnis"])

    def test_keyword_read_uses_the_search_window(self) -> None:
        timeline = _Timeline(NOVEMBER_STOCK)
        result: dict = _run(_state("read", target="Elternabend"), timeline, SATURDAY)

        self.assertEqual(timeline.keywords, [("Elternabend", "both", 10, (ANCHOR_LITERAL,))])
        self.assertEqual(result["ergebnis"], PARENTS_EVENING_LINE)

    def test_overview_reads_the_proactive_window(self) -> None:
        """Drei Tage zurueck, vierzehn voraus — `proactive_window`, nicht eigene Werte."""
        timeline = _Timeline([])
        _run(_state("read"), timeline, SATURDAY)

        self.assertEqual(
            timeline.ranges,
            [(datetime(2026, 10, 14, 12, 0, tzinfo=BERLIN),
              datetime(2026, 10, 31, 12, 0, tzinfo=BERLIN), (ANCHOR_LITERAL,))],
        )

    def test_unreadable_time_says_nothing_was_read(self) -> None:
        """Ein unlesbarer Ausdruck ist kein leerer Zeitraum."""
        timeline = _Timeline(NOVEMBER_STOCK)
        with self.assertLogs("ki_server.agents.timeline.suche", level="ERROR"):
            result: dict = _run(_state("read", "xyzzy"), timeline, SATURDAY)

        self.assertTrue(
            result["ergebnis"].startswith("Den Zeitraum 'xyzzy' konnte ich nicht lesen"),
        )
        self.assertEqual(timeline.ranges, [])


#: Das Fenster des Novembers, wie `time_window` es baut.
NOVEMBER_WINDOW: tuple[datetime, datetime] = (
    datetime(2026, 11, 1, 0, 0, tzinfo=BERLIN),
    datetime(2026, 11, 30, 23, 59, 59, tzinfo=BERLIN),
)
#: Die Klaerungen zum November, gefragt am Samstag, 17.10.2026 — ohne, mit
#: einem und mit zwei Treffern.
NO_MATCH_QUESTION: str = (
    "Vom 01.11.2026 bis 30.11.2026 finde ich keinen Termin. "
    "Nenn mir den Termin, den ich löschen soll, mit seinem Namen."
)
PARENTS_EVENING_QUESTION: str = (
    "Vom 01.11.2026 bis 30.11.2026 habe ich diesen Termin gefunden: Freitag, "
    "06.11.2026, 19:00 Uhr — Elternabend (in 20 Tagen). "
    "Sag mir mit seinem Namen, ob ich ihn löschen soll."
)
TWO_MATCHES_QUESTION: str = (
    "Vom 01.11.2026 bis 30.11.2026 habe ich diese Termine gefunden:\n"
    f"{PARENTS_EVENING_LINE}\n"
    "- Montag, 30.11.2026, 20:00 Uhr — Abschlussessen (in 44 Tagen)\n"
    "Sag mir mit seinem Namen, welchen ich löschen soll."
)
#: Der Bestand je Klaerung: kein, ein und zwei Termine im November.
NO_MATCH_STOCK: list[dict] = [NOVEMBER_STOCK[0], NOVEMBER_STOCK[4]]
ONE_MATCH_STOCK: list[dict] = [NOVEMBER_STOCK[i] for i in (0, 2, 4)]


class WritePathTest(unittest.TestCase):
    """Aendern und Loeschen aus einem Zeitraum klaeren und schreiben nichts."""

    def _assert_nothing_written(self, state: dict, result: dict) -> None:
        """Klaerung ohne Termin: Der Graph endet nach `suchen`, `ausfuehren` laeuft nicht."""
        self.assertEqual(result["status"], "rueckfrage")
        self.assertTrue(result["parameter"]["clarification"])
        self.assertNotIn("termin", result["parameter"])
        self.assertEqual(TimelineAgent()._nach_suche({**state, **result}), END)

    def test_delete_in_november_without_match_asks_which(self) -> None:
        state: dict = _state("delete", "im November")
        result: dict = _run(state, _Timeline(NO_MATCH_STOCK), SATURDAY)

        self._assert_nothing_written(state, result)
        self.assertEqual(result["rueckfrage"], NO_MATCH_QUESTION)

    def test_delete_in_november_with_one_match_names_it_and_asks_for_the_name(self) -> None:
        state: dict = _state("delete", "im November")
        state["aufgabe"] = "Lösch meinen Termin im November"
        result: dict = _run(state, _Timeline(ONE_MATCH_STOCK), SATURDAY)

        self._assert_nothing_written(state, result)
        self.assertEqual(result["rueckfrage"], PARENTS_EVENING_QUESTION)
        self.assertNotIn("confirmation", result["parameter"])
        self.assertNotIn("original_aufgabe", result["parameter"])

    def test_delete_in_november_with_two_matches_lists_them(self) -> None:
        state: dict = _state("delete", "im November")
        result: dict = _run(state, _Timeline(NOVEMBER_STOCK), SATURDAY)

        self._assert_nothing_written(state, result)
        self.assertEqual(result["rueckfrage"], TWO_MATCHES_QUESTION)

    def test_this_month_with_one_coming_match_still_lists_both(self) -> None:
        """Der Vorzug des einzigen kommenden Termins gilt hier nicht: Er waehlte still."""
        stock: list[dict] = [
            _row(6, datetime(2026, 10, 5, 9, 0, tzinfo=BERLIN), "Friseur"),
            _row(7, datetime(2026, 10, 20, 9, 0, tzinfo=BERLIN), "Baumarkt"),
        ]
        state: dict = _state("update", "diesen Monat")
        result: dict = _run(state, _Timeline(stock), SATURDAY)

        self._assert_nothing_written(state, result)
        self.assertIn("Friseur", result["rueckfrage"])
        self.assertIn("Baumarkt", result["rueckfrage"])
        self.assertTrue(result["rueckfrage"].endswith("welchen ich ändern soll."))

    def test_update_by_period_never_offers_the_anchor(self) -> None:
        """Ein Anker allein im Monat ist kein Kandidat: die Klaerung aus null Treffern."""
        timeline = _Timeline([NOVEMBER_STOCK[1]])
        state: dict = _state("update", "im November")
        result: dict = _run(state, timeline, SATURDAY)

        self._assert_nothing_written(state, result)
        self.assertTrue(result["parameter"]["clarification"])
        self.assertEqual(timeline.ranges, [(*NOVEMBER_WINDOW, (ANCHOR_TYPE,))])

    def test_an_arriving_anchor_is_dropped_loudly(self) -> None:
        """Liefert die Abfrage den Anker trotz Ausschluss, bleibt nur der Termin."""
        timeline = _Timeline([NOVEMBER_STOCK[1], NOVEMBER_STOCK[2]], honour_exclusion=False)
        state: dict = _state("delete", "im November")
        with self.assertLogs("ki_server.memory.timeline_reading", level="ERROR"):
            result: dict = _run(state, timeline, SATURDAY)

        self.assertEqual(result["rueckfrage"], PARENTS_EVENING_QUESTION)

    def test_period_question_rejects_a_named_title(self) -> None:
        with self.assertRaises(ValueError):
            suche.period_question(_state("delete", "im November", "Zahnarzt"), SATURDAY)

    def test_twin_update_by_title_without_match_is_an_error(self) -> None:
        """Der Weg mit genanntem Titel bleibt: ohne Treffer `fehler`, keine Rueckfrage."""
        state: dict = _state("update", "im November", "Zahnarzt")
        result: dict = _run(state, _Timeline([]), SATURDAY)

        self.assertEqual(result["status"], "fehler")


#: Antworten auf die Klaerung: Zustimmung, Zustimmung mit dem Verb, ein
#: Datum, eine Wahl, eine Einschraenkung. Keine davon schreibt.
CLARIFICATION_ANSWERS: tuple[str, ...] = (
    "Ja", "Ja, verschieb ihn", "den am 30.11.", "den zweiten", "Ja, aber den Zahnarzt",
)


#: Antworten auf die Auswahl mit Titel: Titel mit Tag, eine Stelle, eine
#: Nummer. Keine davon waehlt.
SELECTION_ANSWERS: tuple[str, ...] = ("den Zahnarzt am 9.", "den zweiten", "Nummer 1")


def _new_order() -> dict:
    """*„Verschieb den Zahnarzt am 9. auf 11 Uhr“*, klassifiziert; der Zeitausdruck ist neu."""
    return {
        "aufgabe": "Verschieb den Zahnarzt am 9. auf 11 Uhr", "aufgabe_typ": "workflow",
        "agent_name": "timeline", "kontext": {"user_id": "pruefer"}, "schritte": [],
        "status": "laufend", "ergebnis": None, "rueckfrage": None, "fehler": None,
        "parameter": {"action": "reschedule", "target": "Zahnarzt", "zeitausdruck": "11 Uhr"},
    }


def _after_the_question(first: dict, asked: dict, answer: str) -> dict:
    """Der Zustand im Turn nach der Rueckfrage, wie `_handle_resume` ihn baut.

    `asked` ist die Ausgabe von `suchen`, eines Knotens: Sie traegt
    `parameter` nur, wenn der Knoten ihn aendert, bei der Auswahl mit Titel
    also nicht. Der Dispatch legt dann die Parameter des ersten Turns ins
    Pending, und so liest es auch dieser Zustand.
    """
    pending: dict = asked.get("parameter", first["parameter"])
    return {
        "aufgabe": answer, "aufgabe_typ": "workflow", "agent_name": "timeline",
        "kontext": first["kontext"], "schritte": [], "status": "laufend",
        "ergebnis": None, "rueckfrage": None, "fehler": None,
        "parameter": {
            **pending, "resume": True, "user_answer": answer,
            "original_rueckfrage": asked["rueckfrage"],
        },
    }


class ClarificationAnswerTest(unittest.TestCase):
    """Keine Antwort auf die Klaerung aus einem Zeitraum schreibt — auch kein *„Ja“*.

    Der erste Turn laeuft durch `suchen`, der zweite durch den ganzen Graphen
    des Agenten; `ausfuehren` ist durch einen Schreiber ersetzt, der jeden
    Aufruf festhaelt, das Repository durch ein Doppel, das jeden Zugriff
    festhaelt.
    """

    def setUp(self) -> None:
        self.repository = MagicMock()
        self.executed: list[dict] = []
        for p in (
            patch("memory.repositories.timeline_repository.TimelineRepository", self.repository),
            patch("agents.timeline.agent.ausfuehren", self._record),
        ):
            p.start()
            self.addCleanup(p.stop)

    def _record(self, state: dict) -> dict:
        """Haelt den Aufruf fest, statt zu schreiben."""
        self.executed.append(state)
        return {"status": "abgeschlossen", "ergebnis": "geschrieben"}

    def _assert_no_answer_writes(self, stock: list[dict]) -> None:
        """Faehrt jede Antwort auf die Klaerung zu `stock`, fuer Loeschen und Verschieben."""
        for action in ("delete", "reschedule"):
            first: dict = _state(action, "im November")
            first["aufgabe"] = "Mach was mit meinem Termin im November."
            asked: dict = _run(first, _Timeline(stock), SATURDAY)
            self.assertTrue(asked["parameter"]["clarification"])
            for answer in CLARIFICATION_ANSWERS:
                with self.subTest(action=action, answer=answer):
                    done: dict = TimelineAgent().invoke(_after_the_question(first, asked, answer))
                    self.assertEqual(done["status"], "abgeschlossen")
                    self.assertNotIn("termin", done["parameter"])
        self.assertEqual(self.executed, [])
        self.repository.find_by_id.assert_not_called()
        self.assertEqual(self.repository.method_calls, [])

    def test_no_answer_after_no_match_writes(self) -> None:
        self._assert_no_answer_writes(NO_MATCH_STOCK)

    def test_no_answer_after_one_match_writes(self) -> None:
        self._assert_no_answer_writes(ONE_MATCH_STOCK)

    def test_no_answer_after_two_matches_writes(self) -> None:
        self._assert_no_answer_writes(NOVEMBER_STOCK)

    def test_no_answer_after_a_selection_by_title_writes(self) -> None:
        """Die Auswahl mit Titel: Keine Antwort waehlt, die Klaerung nennt beide mit Datum.

        Sie verspricht keinen Weg, der nicht zum Ziel fuehrt: kein Auftrag mit
        Datum, denn der grenzt gleichnamige Termine nicht ein.
        """
        for action in ("update", "delete", "reschedule"):
            first: dict = _state(action, "", "Zahnarzt")
            first["aufgabe"] = "Mach was mit dem Zahnarzt."
            asked: dict = _run(first, _Timeline(DENTIST_STOCK), SATURDAY)
            self.assertEqual(json.loads(asked["rueckfrage"])["typ"], "disambiguierung")
            for answer in SELECTION_ANSWERS:
                with self.subTest(action=action, answer=answer):
                    done: dict = TimelineAgent().invoke(_after_the_question(first, asked, answer))
                    self.assertEqual(done["status"], "abgeschlossen")
                    self.assertNotIn("termin", done["parameter"])
                    self.assertIn("Zahnarzt am 02.10.2026 10:00", done["ergebnis"])
                    self.assertIn("Zahnarzt am 09.10.2026 10:00", done["ergebnis"])
                    self.assertIn("kann ich noch nicht wählen", done["ergebnis"])
                    self.assertNotIn("mit Titel und Datum", done["ergebnis"])
        self.assertEqual(self.executed, [])
        self.repository.find_by_id.assert_not_called()
        self.assertEqual(self.repository.method_calls, [])

    def test_twin_a_new_order_with_title_reaches_the_writer(self) -> None:
        """Derselbe Aufbau sieht ein Schreiben: ein neuer Auftrag mit Titel, ein Treffer."""
        self.repository.find_by_keyword.return_value = [DENTIST_STOCK[1]]
        TimelineAgent().invoke(_new_order())

        self.assertEqual(len(self.executed), 1)
        self.assertEqual(self.executed[0]["parameter"]["termin"], DENTIST_STOCK[1])

    def test_moving_by_title_with_two_matches_asks_which(self) -> None:
        """Verschieben mit Titel und zwei Treffern: die Auswahl, nicht still der erste."""
        self.repository.find_by_keyword.side_effect = _Timeline(DENTIST_STOCK).find_by_keyword
        asked: dict = TimelineAgent().invoke(_new_order())

        self.assertEqual(asked["status"], "rueckfrage")
        selection: dict = json.loads(asked["rueckfrage"])
        self.assertEqual(selection["typ"], "disambiguierung")
        self.assertEqual(selection["aktion"], "reschedule")
        self.assertEqual([c["id"] for c in selection["kandidaten"]], [8, 9])
        self.assertNotIn("termin", asked["parameter"])
        self.assertEqual(self.executed, [])

    def test_twin_moving_by_title_prefers_the_one_coming_match(self) -> None:
        """Derselbe Aufbau mit einem kommenden Zahnarzttermin: der wird verschoben."""
        coming: dict = _row(10, datetime.now(BERLIN) + timedelta(days=3), "Zahnarzt")
        stock: list[dict] = [DENTIST_STOCK[0], coming]
        self.repository.find_by_keyword.side_effect = _Timeline(stock).find_by_keyword
        TimelineAgent().invoke(_new_order())

        self.assertEqual(len(self.executed), 1)
        self.assertEqual(self.executed[0]["parameter"]["termin"]["id"], 10)

    # Rot, bis TIMELINE-TITEL-MEHRERE-TREFFER-OHNE-TAG gebaut ist: Der Weg mit
    # Titel grenzt mehrere Treffer nicht nach dem Tag des Termins ein. Die
    # Suche nach dem Titel liest den Zeitausdruck nicht, und beim Verschieben
    # ist er die neue Zeit. Beide Zahnarzttermine gehen in die Auswahl, und
    # verschoben wird keiner.
    @unittest.expectedFailure
    def test_a_new_order_with_title_and_date_moves_that_one(self) -> None:
        """*„Verschieb den Zahnarzt am 9. auf 11 Uhr“*, zwei Zahnarzttermine: der am 9."""
        self.repository.find_by_keyword.side_effect = _Timeline(DENTIST_STOCK).find_by_keyword
        TimelineAgent().invoke(_new_order())

        self.assertEqual(len(self.executed), 1)
        self.assertEqual(self.executed[0]["parameter"]["termin"]["id"], 9)


#: Zwei Zahnarzttermine in der Vergangenheit — der Vorzug des einzigen
#: kommenden Termins greift nicht, es kommt die Auswahl.
DENTIST_STOCK: list[dict] = [
    _row(8, datetime(2026, 10, 2, 10, 0, tzinfo=BERLIN), "Zahnarzt"),
    _row(9, datetime(2026, 10, 9, 10, 0, tzinfo=BERLIN), "Zahnarzt"),
]


def _old_selection(candidates: list[dict]) -> dict:
    """Der Zustand nach einer Auswahl ohne Titel, wie sie noch in Redis liegen kann."""
    first: dict = _state("delete", "im November")
    asked: dict = {
        "parameter": first["parameter"],
        "rueckfrage": json.dumps({
            "typ": "disambiguierung", "agent": "timeline", "aktion": "delete",
            "kandidaten": candidates,
        }, ensure_ascii=False),
    }
    return _after_the_question(first, asked, "den zweiten")


class ChoiceResumeTest(unittest.TestCase):
    """Eine Auswahl, die noch in Redis liegt, waehlt nicht und schreibt nicht."""

    def setUp(self) -> None:
        self.repository = MagicMock()
        p = patch("memory.repositories.timeline_repository.TimelineRepository", self.repository)
        p.start()
        self.addCleanup(p.stop)

    def test_a_choice_without_title_writes_nothing(self) -> None:
        """Die alte Auswahl aus *„im November“*: eine Klaerung mit beiden Terminen."""
        resumed: dict = resume.resume(_old_selection([
            {"id": 3, "title": "Elternabend", "datum": "06.11.2026 19:00", "typ": "termin"},
            {"id": 4, "title": "Abschlussessen", "datum": "30.11.2026 20:00", "typ": "termin"},
        ]))

        self.assertEqual(resumed["status"], "abgeschlossen")
        self.assertNotIn("parameter", resumed)
        self.assertIn("Elternabend am 06.11.2026 19:00", resumed["ergebnis"])
        self.assertIn("Abschlussessen am 30.11.2026 20:00", resumed["ergebnis"])
        self.repository.find_by_id.assert_not_called()

    def test_a_candidate_without_date_is_an_error(self) -> None:
        """Ein Kandidat ohne Datum laesst sich nicht nennen: `fehler`, laut, nichts gelesen."""
        with self.assertLogs("ki_server.agents.timeline.resume", level="ERROR"):
            resumed: dict = resume.resume(_old_selection([
                {"id": 3, "title": "Elternabend", "typ": "termin"},
            ]))

        self.assertEqual(resumed["status"], "fehler")
        self.assertNotIn("parameter", resumed)
        self.repository.find_by_id.assert_not_called()


def _anchor_literals(path: str) -> int:
    """Wie oft das Literal des Anker-Typs als Konstante im Quelltext steht."""
    tree: ast.Module = ast.parse(Path(path).read_text(encoding="utf-8"))
    return sum(
        1 for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and node.value == ANCHOR_LITERAL
    )


class OneSourceTest(unittest.TestCase):
    """Der Anker-Typ und das proaktive Fenster stehen je an einer Stelle."""

    def test_no_anchor_literal_in_suche_and_magneten(self) -> None:
        for module in (suche, magneten):
            with self.subTest(module=module.__name__):
                self.assertEqual(_anchor_literals(module.__file__), 0)

    def test_twin_the_source_carries_the_literal_once(self) -> None:
        """Die Zaehlung findet das Literal, wo es steht — sonst bewiese die Null nichts."""
        self.assertEqual(_anchor_literals(timeline_inventory.__file__), 1)

    def test_magneten_reads_the_anchor_type(self) -> None:
        self.assertEqual(magneten.EVENT_TYPES_ERINNERUNGS_ANKER, frozenset({ANCHOR_TYPE}))
        self.assertEqual(magneten.themen_aus_event_type(ANCHOR_TYPE), [])

    def test_overview_days_left_the_config(self) -> None:
        for name in ("TIMELINE_UEBERSICHT_TAGE_ZURUECK", "TIMELINE_UEBERSICHT_TAGE_VORAUS"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(config, name))

    def test_twin_the_search_limit_stays(self) -> None:
        self.assertTrue(hasattr(config, "TIMELINE_SUCHE_LIMIT"))


class TimeWindowGuardTest(unittest.TestCase):
    """`time_window` verwirft, was es nicht lesen darf."""

    def test_naive_now_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            suche.time_window("im November", datetime(2026, 10, 17, 12, 0))

    def test_empty_expression_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            suche.time_window("  ", SATURDAY)

    def test_twin_period_window_spans_whole_days(self) -> None:
        window = suche.time_window("im November", SATURDAY)

        self.assertEqual(window.end - window.start, timedelta(days=30) - timedelta(seconds=1))


if __name__ == "__main__":
    unittest.main()
