"""Zeugen: Ein Lesevorgang belegt keine Schreibbehauptung.

Auf die Lesefrage *„Hab ich morgen was vor?“* las die Timeline eine
Terminzeile, und die Antwort sagte *„Hab's gerade fuer dich eingetragen“*.
Die Speicherpruefung meldete `gedeckt`, weil jeder abgeschlossene Dienst jede
Behauptung deckte. Jetzt deckt nur ein Dienst, der in diesem Turn geschrieben
hat; belegt wird das durch einen Schritt `verifiziert` gleich `True`.

Zeugen dieser Datei:
  * **Satz 2** — ein Leseergebnis der Timeline deckt *„eingetragen“* nicht;
    eine echte Schreibung deckt.
  * **Notizen** — ein Aktualisieren deckt, ein Auflisten nicht.
  * **Duplikat** — *„ist bereits eingetragen“* ist keine Schreibung dieses
    Turns; der Bestandsabgleich entscheidet, und beide Ausgaenge stehen hier.
  * **Nicht erkennbar** — ein Dienst, dessen Meldung nichts erkennen laesst,
    deckt wie bisher, mit genau einer Info-Zeile.
  * **Eintrag** — die dauerhafte Ablage nennt, wer geschrieben hat, getrennt
    von dem, der nur abgeschlossen hat.
  * **Struktur** — jede Schreibung von Timeline und Notizen meldet den Schritt.

Die Ergebnisse entstehen auf den echten Wegen der Dienste (`suchen`, `_create`,
`_update`); ersetzt sind nur Datenbank, Modell und Uhr. Die Beispiele sind
nachgebildet aus der Simulation an einem Pruef-Nutzer, nicht aus dem Bestand
eines Nutzers. Ohne Datenbank, Netz und Modell. Kein skipUnless, kein skipIf,
kein try/except um Importe.
"""

import ast
import logging
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from agents.base import AgentResult
from agents.notizen import crud as notes_crud
from agents.notizen import suche as notes_search
from agents.timeline import crud as timeline_crud
from agents.timeline import suche as timeline_search
from memory.repositories.timeline_repository import TimelineRepository
from utils.storage_claims import (
    ORDER_HEADER,
    WRITE_DONE,
    WRITE_NONE,
    WRITE_UNKNOWN,
    uncovered_claims,
    write_evidence,
)

BERLIN: ZoneInfo = ZoneInfo("Europe/Berlin")
#: Mittwoch; *morgen* ist Donnerstag, der 15.10.2026.
WEDNESDAY: datetime = datetime(2026, 10, 14, 9, 0, tzinfo=BERLIN)
TOMORROW_TEN: datetime = datetime(2026, 10, 15, 10, 0, tzinfo=BERLIN)
#: Die Antwort in Satz 2 der Simulation, nachgebildet.
SENTENCE_TWO: str = "Morgen um zehn steht Dr. Berger an. Hab's gerade für dich eingetragen."
#: Eine Behauptung, die Uhrzeit und Tag nennt — der Bestandsabgleich kann sie zuordnen.
CLAIM_AT_TEN: str = "Morgen um 10 Uhr ist notiert."
USER: str = "pruef-nutzer"
#: Die Figur des Paares — jeder Leser der Timeline liest nur im Paar.
CHARACTER: str = "nova"


def _row(moment: datetime, title: str) -> dict:
    """Eine Timeline-Zeile, wie das Repository sie liefert."""
    return {
        "id": 11, "user_id": USER, "event_time": moment, "title": title,
        "event_type": "termin", "precision": "minute", "details": "", "aktiv": True,
    }


def _as_result(name: str, produced: dict) -> AgentResult:
    """Das Ergebnis eines Dienstes, wie sein Dispatch es aus dem Agentenzustand baut."""
    return AgentResult(
        agent_name=name, ergebnis=produced.get("ergebnis"), status=produced["status"],
        fehler=produced.get("fehler"), schritte=produced.get("schritte", []),
    )


class _ReadingTimeline:
    """Doppel des Repositorys fuer den Leseweg: liefert die Zeilen im Fenster."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows: list[dict] = rows

    def find_by_date_range(  # noqa: PLR0913, PLR0917 — dieselbe Unterschrift wie das Repository
        self, postgres_url: str, user_id: str, character_id: str, von: datetime, bis: datetime,
        exclude_event_types: tuple[str, ...] = (),
    ) -> list[dict]:
        return [r for r in self.rows if von <= r["event_time"] <= bis]


def _timeline_read() -> AgentResult:
    """*„Hab ich morgen was vor?“* — der Leseweg der Timeline mit einem Termin morgen um zehn."""
    state: dict = {
        "parameter": {"action": "read", "target": "", "zeitausdruck": "morgen"},
        "kontext": {"user_id": USER, "character_id": CHARACTER},
        "aufgabe": "Hab ich morgen was vor?", "schritte": [],
    }
    reading = _ReadingTimeline([_row(TOMORROW_TEN, "Dr. Berger")])
    with patch("memory.timeline_reading.TimelineRepository", reading), \
            patch("agents.timeline.suche.now_local", return_value=WEDNESDAY):
        return _as_result("timeline", timeline_search.suchen(state))


def _timeline_create() -> AgentResult:
    """Ein Termin wird angelegt, die Verifikation bestaetigt ihn."""
    state: dict = {
        "aufgabe": "Trag das Fußballtraining ein",
        "kontext": {"user_id": USER, "character_id": CHARACTER},
        "parameter": {"action": "create", "target": "Fußballtraining",
                      "zeitausdruck": "24.10.2026 18:00", "event_type": "termin"},
        "schritte": [],
    }
    with patch.object(TimelineRepository, "insert", return_value=4711), \
            patch.object(timeline_crud, "_verifizieren_termin", return_value=True):
        return _as_result("timeline", timeline_crud._create(state))


def _timeline_duplicate() -> AgentResult:
    """Ein Anlegen, dessen Termin schon dasteht: die Timeline meldet *„bereits eingetragen“*."""
    existing: dict = _row(datetime(2027, 11, 17, 10, 0, tzinfo=BERLIN), "Probetraining")
    state: dict = {
        "parameter": {"action": "create", "target": "Probetraining",
                      "zeitausdruck": "17.11.2027 10 Uhr"},
        "kontext": {"user_id": USER, "character_id": CHARACTER},
        "aufgabe": "Trag das Probetraining ein", "schritte": [],
    }
    with patch.object(TimelineRepository, "find_by_keyword", return_value=[existing]), \
            patch.object(TimelineRepository, "find_by_date_range", return_value=[existing]):
        return _as_result("timeline", timeline_search.suchen(state))


def _notes_update() -> AgentResult:
    """Die Einkaufsliste wird aktualisiert, die Verifikation bestaetigt es."""
    state: dict = {
        "aufgabe": "Setz Milch auf die Einkaufsliste",
        "parameter": {
            "action": "update",
            "notiz": {"id": 7, "name": "Einkaufsliste", "text": "Brot"},
        },
        "schritte": [],
    }
    model = MagicMock()
    model.chat.submit_sync.return_value = SimpleNamespace(text="Brot\nMilch")
    with patch("services.model_services.model_service", model), \
            patch("memory.repositories.notizen_repository.NotizenRepository.update"), \
            patch.object(notes_crud, "_zusammenfassung_generieren", return_value="Brot, Milch"), \
            patch.object(notes_crud, "_verifizieren_notiz", return_value=True):
        return _as_result("notizen", notes_crud._update(state))


def _notes_listing() -> AgentResult:
    """*„Was hab ich an Notizen?“* — der Leseweg der Notizen listet auf."""
    state: dict = {
        "parameter": {"action": "read", "target": ""}, "kontext": {"user_id": USER},
        "aufgabe": "Was hab ich an Notizen?", "schritte": [],
    }
    listing: list[dict] = [
        {"id": 7, "name": "Einkaufsliste", "typ": "liste", "zusammenfassung": "Brot"},
    ]
    with patch("memory.repositories.notizen_repository.NotizenRepository.find_by_user",
               return_value=listing):
        return _as_result("notizen", notes_search.suchen(state))


class SentenceTwoTest(unittest.TestCase):
    """Satz 2: Die Timeline hat nur gelesen, die Antwort sagt *„eingetragen“*."""

    def test_read_does_not_cover_the_claim(self) -> None:
        read: AgentResult = _timeline_read()
        self.assertEqual(read.status, "abgeschlossen")
        self.assertIn("Dr. Berger", read.ergebnis)

        check = uncovered_claims(SENTENCE_TWO, [read])

        self.assertEqual([c.word for c in check.claims], ["eingetragen"])
        self.assertEqual(write_evidence(read), WRITE_NONE)
        self.assertEqual(check.completed, ("timeline",))
        self.assertEqual(check.written, ())
        self.assertTrue(check.uncovered)
        self.assertEqual(check.result, "nicht_belegt")

    def test_twin_real_write_covers(self) -> None:
        created: AgentResult = _timeline_create()
        self.assertEqual(created.status, "abgeschlossen")
        self.assertTrue(created.ergebnis.startswith("Termin 'Fußballtraining' eingetragen fuer "))

        check = uncovered_claims(CLAIM_AT_TEN, [created])

        self.assertEqual(write_evidence(created), WRITE_DONE)
        self.assertEqual(check.written, ("timeline",))
        self.assertFalse(check.uncovered)
        self.assertEqual(check.result, "gedeckt")

    def test_write_beside_a_read_covers(self) -> None:
        """Liest ein Dienst und schreibt ein anderer, deckt der schreibende."""
        check = uncovered_claims(CLAIM_AT_TEN, [_timeline_read(), _notes_update()])
        self.assertEqual(check.completed, ("timeline", "notizen"))
        self.assertEqual(check.written, ("notizen",))
        self.assertFalse(check.uncovered)


class NotesTest(unittest.TestCase):
    """Notizen: Aktualisieren deckt, Auflisten nicht."""

    def test_updated_note_covers(self) -> None:
        updated: AgentResult = _notes_update()
        self.assertEqual(updated.status, "abgeschlossen")
        self.assertTrue(updated.ergebnis.startswith("Notiz 'Einkaufsliste' aktualisiert"))

        check = uncovered_claims("Notiert.", [updated])

        self.assertEqual(check.written, ("notizen",))
        self.assertFalse(check.uncovered)

    def test_twin_listing_does_not_cover(self) -> None:
        listing: AgentResult = _notes_listing()
        self.assertEqual(listing.status, "abgeschlossen")
        self.assertIn("Einkaufsliste", listing.ergebnis)

        check = uncovered_claims("Notiert.", [listing])

        self.assertEqual(write_evidence(listing), WRITE_NONE)
        self.assertEqual(check.completed, ("notizen",))
        self.assertTrue(check.uncovered)


class _Inventory:
    """Die Attrappe des Lesezugriffs im Bestandsabgleich: filtert nach dem Zeitraum."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows: list[dict] = rows
        self.calls: list[tuple] = []

    def __call__(
        self, url: str, user_id: str, character_id: str, start: datetime, end: datetime,
    ) -> list:
        self.calls.append((user_id, start, end))
        return [r for r in self.rows if start <= r["event_time"] <= end]


def _situation_at_ten() -> dict:
    """Eine erfundene Lage: ein akutes Objekt am 17.11.2027 um 10 Uhr."""
    return {
        "herkunft": "frisch",
        "objekte": [{
            "name": "Sache", "klasse": "vorgang", "akut": True, "offen": [],
            "gedeckt": {"Tag": "17.11.2027", "Uhrzeit": "10 Uhr"},
        }],
    }


def _step(
    results: list, situation: dict | None, inventory: _Inventory,
) -> tuple[dict, list[str], dict]:
    """Ruft `_storage_claim_step` mit Urteil `ok`; liefert Zustand, Auftraege und Eintrag."""
    from graph.nodes import tribunal
    state: dict = {
        "turn_id": "zeuge", "user_id": USER, "character_id": CHARACTER,
        "response": CLAIM_AT_TEN, "agent_results": results,
        "correction_round": 0, "max_corrections": 2, "tribunal_verdict": "ok",
    }
    if situation is not None:
        state["sachlage"] = situation
    feedback: list[str] = []
    with patch.object(TimelineRepository, "find_by_date_range", side_effect=inventory), \
            patch.object(tribunal, "log_berechnung") as record:
        tribunal._storage_claim_step(state, feedback)
    return state, feedback, record.call_args.kwargs["inhalt"]


class DuplicateTest(unittest.TestCase):
    """*„ist bereits eingetragen“* — keine Schreibung dieses Turns; der Bestand entscheidet."""

    def test_duplicate_is_no_write(self) -> None:
        duplicate: AgentResult = _timeline_duplicate()
        self.assertEqual(duplicate.status, "abgeschlossen")
        self.assertIn("ist bereits eingetragen", duplicate.ergebnis)

        self.assertEqual(write_evidence(duplicate), WRITE_NONE)
        self.assertTrue(uncovered_claims(CLAIM_AT_TEN, [duplicate]).uncovered)

    def test_duplicate_found_in_inventory_is_a_repetition(self) -> None:
        """Steht der genannte Termin im Bestand, wiederholt die Antwort eine echte Schreibung."""
        moment = datetime(2027, 11, 17, 10, 0, tzinfo=BERLIN)
        inventory = _Inventory([_row(moment, "Probetraining")])
        state, feedback, entry = _step([_timeline_duplicate()], _situation_at_ten(), inventory)

        self.assertEqual(len(inventory.calls), 1)
        self.assertEqual(entry["bestandsabgleich"], "gefunden")
        self.assertEqual(state["tribunal_verdict"], "ok")
        self.assertEqual(feedback, [])
        self.assertEqual(entry["abgeschlossen"], ["timeline"])
        self.assertEqual(entry["geschrieben"], [])

    def test_twin_duplicate_without_situation_is_corrected(self) -> None:
        state, feedback, entry = _step([_timeline_duplicate()], None, _Inventory([]))

        self.assertEqual(entry["bestandsabgleich"], "kein_akutes_objekt_mit_zeit")
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))
        self.assertEqual(entry["ergebnis"], "nicht_belegt")


class UnrecognizedTest(unittest.TestCase):
    """Ein Dienst, dessen Meldung nicht erkennen laesst, ob er schrieb, deckt wie bisher."""

    def test_other_service_covers_with_one_info_line(self) -> None:
        other = AgentResult(agent_name="wissen", ergebnis="ok", status="abgeschlossen",
                            schritte=[{"node": "einordnen", "ergebnis": "ok"}])
        with self.assertLogs("ki_server.storage_claims", level="INFO") as logs:
            check = uncovered_claims(CLAIM_AT_TEN, [other])

        self.assertEqual(write_evidence(other), WRITE_UNKNOWN)
        self.assertEqual(check.unrecognized, ("wissen",))
        self.assertFalse(check.uncovered)
        self.assertEqual(check.result, "gedeckt")
        self.assertEqual(len(logs.records), 1)
        self.assertEqual(logs.records[0].levelno, logging.INFO)
        self.assertIn("wissen", logs.records[0].getMessage())

    def test_timeline_without_trail_covers(self) -> None:
        """Auch ein Dienst, der Schreibungen meldet, laesst ohne Verlauf nichts erkennen."""
        bare = SimpleNamespace(agent_name="timeline", status="abgeschlossen")
        with self.assertLogs("ki_server.storage_claims", level="INFO") as logs:
            check = uncovered_claims(CLAIM_AT_TEN, [bare])
        self.assertEqual(check.unrecognized, ("timeline",))
        self.assertFalse(check.uncovered)
        self.assertEqual(len(logs.records), 1)

    def test_twin_without_claim_no_info_line(self) -> None:
        other = AgentResult(agent_name="wissen", ergebnis="ok", status="abgeschlossen")
        with self.assertNoLogs("ki_server.storage_claims", level="INFO"):
            check = uncovered_claims("Die Pulsare sind erstaunlich stabil.", [other])
        self.assertEqual(check.result, "keine_behauptung")


class RecordTest(unittest.TestCase):
    """Der dauerhafte Eintrag trennt die schreibenden von den abgeschlossenen Diensten."""

    def test_entry_names_writers_apart_from_completed(self) -> None:
        _, _, entry = _step([_timeline_read(), _notes_update()], None, _Inventory([]))
        self.assertEqual(entry["abgeschlossen"], ["timeline", "notizen"])
        self.assertEqual(entry["geschrieben"], ["notizen"])
        self.assertEqual(entry["nicht_erkennbar"], [])
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefragt")

    def test_read_alone_asks_the_inventory(self) -> None:
        """Bisher deckte der Lesevorgang, und der Bestand wurde nie gefragt."""
        inventory = _Inventory([])
        state, feedback, entry = _step([_timeline_read()], _situation_at_ten(), inventory)
        self.assertEqual(len(inventory.calls), 1)
        self.assertEqual(entry["bestandsabgleich"], "nicht_gefunden")
        self.assertEqual(entry["geschrieben"], [])
        self.assertEqual(state["tribunal_verdict"], "warnung")
        self.assertTrue(feedback[0].startswith(ORDER_HEADER))


class StructureTest(unittest.TestCase):
    """Jede Schreibung von Timeline und Notizen meldet den Schritt `verifiziert`.

    Darauf ruht die Einordnung: Fehlt der Schritt bei diesen Diensten, gilt der
    Turn als gelesen. Eine Erfolgsmeldung ohne ihn wuerde eine echte Schreibung
    korrigieren.
    """

    FILES: tuple[str, ...] = ("agents/timeline/crud.py", "agents/notizen/crud.py")

    @staticmethod
    def _is_success(node: ast.Dict) -> bool:
        status = next((v for k, v in zip(node.keys, node.values, strict=True)
                       if isinstance(k, ast.Constant) and k.value == "status"), None)
        return isinstance(status, ast.Constant) and status.value == "abgeschlossen"

    def test_every_success_reports_the_verified_step(self) -> None:
        root = Path(__file__).resolve().parent.parent
        reporting = silent = 0
        for name in self.FILES:
            tree = ast.parse((root / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict) and self._is_success(node):
                    if "'verifiziert'" in ast.dump(node):
                        reporting += 1
                    else:
                        silent += 1
        self.assertEqual(silent, 0)
        self.assertEqual(reporting, 9)   # 17.10.2026: Timeline 3, Notizen 6


if __name__ == "__main__":
    unittest.main()
