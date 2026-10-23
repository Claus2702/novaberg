"""Tests: Das Clipboard traegt die ID der Zeile, die der TimelineAgent geschrieben hat.

Die Zusage `timeline_id` im Katalog: die ID des im selben Durchlauf angelegten
Eintrags, nicht die eines gefundenen. `_build_return` las sie aus dem letzten
Schritt, und der ist nach jeder Ausfuehrung der Schritt von `bestaetigen` — ohne
ID. Das Clipboard blieb leer, und die KZG legte neben dem Termin einen eigenen
Erinnerungs-Anker an.

Der Graph des Agenten laeuft echt; gedoppelt ist nur das Repository
(`insert`, `find_by_keyword`, `find_by_date_range`) und die Lese-Verifikation
nach dem Schreiben.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from agents import AgentRegistry
from agents.base import AgentResult
from agents.timeline import dispatch
from agents.timeline.agent import TimelineAgent
from agents.timeline.dispatch import _written_row_id, dispatch_timeline
from utils.zeitparser import ZeitVektor

TZ = ZoneInfo("Europe/Berlin")
REPO = "memory.repositories.timeline_repository.TimelineRepository"
NEUE_ID = 42
FREMDE_ID = 7
TERMIN_VEKTOR = ZeitVektor(
    datum=datetime(2031, 12, 15, 10, 0, tzinfo=TZ), tag_erkannt=True,
    uhrzeit_erkannt=True, referenz_modus="absolut",
)


def _state(action: str = "create") -> dict:
    return {
        "user_id": "pruefer",
        "character_id": "nova",
        "management_action": action,
        "management_target": "Zahnarzt",
        "user_prompt": "Trag mir am 15.12.2031 um 10 Uhr den Zahnarzt ein",
        "agent_results": [],
    }


def _lauf(am_tag: list[dict]) -> tuple[dict, list]:
    """`dispatch_timeline` mit dem echten Graphen; `am_tag` ist der Bestand dieses Tages.

    Der Zeitparser ist gedoppelt: `dispatch_timeline` gibt dem Agenten keinen
    `zeitausdruck`, also bekommen Suche und Anlegen den ganzen Satz, und ob der
    Parser ihn aufloest, haengt an seiner Fuzzy-Korrektur (aus *mir* wird *maerz*).
    Beide rufen `zeit_parsen_vektor` erst in der Funktion aus `utils.zeitparser`
    ab; ein Doppel dort trifft die Suche (`find_duplicates`) und das Anlegen
    (`_create`) und gibt ihnen denselben festen Tag.
    """
    with patch.object(AgentRegistry, "finden", return_value=TimelineAgent()), \
         patch("utils.zeitparser.zeit_parsen_vektor", return_value=TERMIN_VEKTOR), \
         patch(f"{REPO}.find_by_keyword", return_value=[]), \
         patch(f"{REPO}.find_by_date_range", return_value=am_tag), \
         patch(f"{REPO}.insert", return_value=NEUE_ID) as schreiben, \
         patch("agents.timeline.crud._verifizieren_termin", return_value=True):
        return dispatch_timeline(_state()), schreiben.call_args_list


def _ergebnis(schritte: list[dict], status: str = "abgeschlossen") -> dict:
    result = AgentResult(
        agent_name="timeline", ergebnis="x", status=status, schritte=schritte,
        fehler="x" if status == "fehler" else None,
    )
    return dispatch._build_return({"agent_results": []}, result)


class AnlegenTest(unittest.TestCase):
    """Der echte Graph, von `dispatch_timeline` bis zum Rueckgabewert."""

    def test_angelegter_termin_steht_im_clipboard(self) -> None:
        """Der Fall des Bugs: abgeschlossen, und `timeline_id` ist die geschriebene Zeile."""
        rueck, schreibungen = _lauf([])
        self.assertEqual(len(schreibungen), 1, "der Graph hat nicht geschrieben")
        self.assertEqual(rueck["agent_results"][-1].status, "abgeschlossen")
        self.assertEqual(rueck["timeline_id"], NEUE_ID)

    def test_zwilling_duplikat_setzt_nichts(self) -> None:
        """Die Suche findet denselben Termin: nichts geschrieben, kein Clipboard.

        `find_duplicates` zaehlt eine Zeile nur, wenn sie aktiv ist, ihr Typ nicht
        in `NOT_APPOINTMENTS` steht (der Typ `termin` steht nicht darin) und ihr
        Titel ein tragendes Wort mit dem Ziel teilt (`Zahnarzt`); den Tag liefert
        der Zeitparser, die Zeile kommt aus `find_by_date_range`.
        """
        gefunden = {
            "id": FREMDE_ID, "title": "Zahnarzt", "event_type": "termin", "aktiv": True,
            "event_time": datetime(2031, 12, 15, 10, 0, tzinfo=TZ), "precision": "minute",
        }
        rueck, schreibungen = _lauf([gefunden])
        self.assertEqual(schreibungen, [], "ein Duplikat darf nichts schreiben")
        ergebnis = rueck["agent_results"][-1]
        self.assertEqual(ergebnis.status, "abgeschlossen")
        self.assertIn("bereits eingetragen", ergebnis.ergebnis, "kein Duplikat erkannt")
        self.assertNotIn("timeline_id", rueck)


class SchrittWahlTest(unittest.TestCase):
    """Die Auswahl des Schritts, gegen Schrittfolgen aus den Knoten des Graphen."""

    BESTAETIGT = {"node": "bestaetigen", "ergebnis": "ok"}

    def test_gefundene_zeile_im_suchschritt_kommt_nicht_ins_clipboard(self) -> None:
        """Zwilling zum Anlegen: eine `id` im Schritt der Suche ist die einer gefundenen Zeile.

        Feindliche Handfolge: der echte Duplikat-Schritt von `suchen` traegt keine
        ID; sie steht hier, damit eine Auswahl, die jede ID nimmt, auffaellt.
        """
        rueck = _ergebnis([
            {"node": "suchen", "ergebnis": "duplikat", "id": FREMDE_ID, "termin_id": FREMDE_ID},
            self.BESTAETIGT,
        ])
        self.assertNotIn("timeline_id", rueck)

    def test_loeschen_setzt_nichts(self) -> None:
        """Der Schritt des Loeschens traegt `termin_id` der abgelegten Zeile.

        So schreibt ihn `crud._delete`: `ergebnis` `geloescht`, mit `termin_id`.
        """
        rueck = _ergebnis([
            {"node": "ausfuehren", "ergebnis": "geloescht", "termin_id": FREMDE_ID,
             "verifiziert": True},
            self.BESTAETIGT,
        ])
        self.assertNotIn("timeline_id", rueck)

    def test_verschieben_setzt_die_neue_zeile(self) -> None:
        """Die neue Zeile ist im selben Durchlauf geschrieben; die alte ist abgelegt."""
        rueck = _ergebnis([
            {"node": "ausfuehren", "ergebnis": "verschoben",
             "alter_id": FREMDE_ID, "neuer_id": NEUE_ID, "verifiziert": True},
            self.BESTAETIGT,
        ])
        self.assertEqual(rueck["timeline_id"], NEUE_ID)

    def test_nicht_abgeschlossener_ausgang_setzt_nichts(self) -> None:
        """Auch ein schreibender Schritt zaehlt nicht, wenn die Verifikation den Ausgang kippte."""
        schritte = [
            {"node": "ausfuehren", "ergebnis": "erstellt", "termin_id": NEUE_ID},
            self.BESTAETIGT,
        ]
        self.assertNotIn("timeline_id", _ergebnis(schritte, status="fehler"))

    def test_schreibender_schritt_ohne_ganze_id_ergibt_none(self) -> None:
        for kaputt in (None, "42", True, 4.2):
            with self.subTest(wert=kaputt), self.assertLogs(dispatch.logger, "ERROR"):
                schritte = [{"node": "ausfuehren", "ergebnis": "erstellt", "termin_id": kaputt}]
                self.assertIsNone(_written_row_id(schritte))

    def test_ohne_schreibenden_schritt_ist_none_und_still(self) -> None:
        """Zwilling: Lesen und Abbruch sind kein Fehler und werden nicht gemeldet."""
        with self.assertNoLogs(dispatch.logger, "ERROR"):
            self.assertIsNone(_written_row_id([{"node": "suchen", "ergebnis": "duplikat"}]))

    def test_schrittfolge_ohne_liste_wirft(self) -> None:
        with self.assertRaises(TypeError):
            _written_row_id(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
