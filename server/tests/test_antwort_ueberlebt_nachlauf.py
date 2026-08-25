"""Tests: Eine freigegebene Antwort ueberlebt einen Fehler im Nachlauf.

**Das Problem, im Betrieb belegt am 25.08.2026:** Nova formulierte eine
Antwort (379 Zeichen), Thinker und Tribunal gaben sie frei — und siebzehn
Sekunden spaeter riss ein `TypeError` in der Salienz den Graphen. Der Nutzer
sah **nichts**: keine Antwort, keine Meldung, und die Eingabe wurde
freigegeben, als waere der Turn erledigt. Kennung:
`AUSLIEFERUNG-HINTER-DEM-NACHLAUF`.

Nach der Freigabe (`evaluate -> output`) folgen vier Knoten, die den Text
nicht mehr aendern: Perzeption, EI-Persistenz, Salienz, Dispatcher. **Ein
Fehler dort darf keine fertige Antwort kosten.**

Die Zusicherungen hier:

  1. **Der Zwischenstand ueberlebt die Ausnahme.** `_graph_streamen` fuehrt
     ohnehin einen `letzter_state` mit; er ging bisher nur verloren, weil die
     Ausnahme die Funktion verliess, bevor jemand ihn las.
  2. **Der Fehler bleibt laut.** Gerettet wird die Antwort, nicht der Fehler —
     er wird weiterhin mit Traceback protokolliert
     (`17_NEBENLAEUFIGKEIT/keine-stillen-uebersprunge.md`).
  3. **Der Lauf ist als unvollstaendig erkennbar.** Wer den Stand bekommt,
     muss wissen, dass er kein Abschluss ist.
  4. **Ohne Antwort kein stiller Ausfall.** Ein Turn, der scheitert, darf
     nicht aussehen wie einer, der erledigt ist.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.event_consumer import _graph_streamen

USER: str = "meister"
FIGUR: str = "nova"


class _Graph:
    """Ein CharacterGraph-Doppel, das nach N Knoten scheitert."""

    def __init__(self, knoten: list[tuple[str, dict]], scheitert_nach: int | None = None) -> None:
        self._knoten = knoten
        self._scheitert_nach = scheitert_nach

    def stream(self, _state: dict):
        for i, (name, zustand) in enumerate(self._knoten):
            if self._scheitert_nach is not None and i == self._scheitert_nach:
                raise TypeError("unsupported operand type(s) for +: 'int' and 'NoneType'")
            yield {name: zustand}


#: Der Verlauf eines echten Turns, gekuerzt auf das, worauf es ankommt.
VERLAUF: list = [
    ("responder", {"response": "Die fertige Antwort.", "user_id": USER}),
    ("thinker",   {"response": "Die fertige Antwort.", "user_id": USER}),
    ("tribunal",  {"response": "Die fertige Antwort.", "user_id": USER}),
    ("evaluate",  {"response": "Die fertige Antwort.", "user_id": USER}),
    # ── ab hier Nachlauf: aendert den Text nicht mehr ──
    ("perzeption_assistant", {"response": "Die fertige Antwort.", "user_id": USER}),
    ("salience",  {"response": "Die fertige Antwort.", "user_id": USER, "salienz": 0.7}),
    ("dispatcher", {"response": "Die fertige Antwort.", "user_id": USER, "fertig": True}),
]


class DerZwischenstandUeberlebtDenFehler(unittest.TestCase):
    """Reisst der Nachlauf, bleibt die freigegebene Antwort erhalten."""

    def setUp(self) -> None:
        self.loop = MagicMock()
        self._patch = patch("services.event_consumer.broadcast_threadsafe")
        self._patch.start()
        self.addCleanup(self._patch.stop)

    def _fahren(self, scheitert_nach: int | None) -> dict:
        graph = _Graph(VERLAUF, scheitert_nach=scheitert_nach)
        return _graph_streamen(graph, {"user_id": USER}, self.loop, USER, FIGUR)

    def test_fehler_in_der_salienz_kostet_die_antwort_nicht(self) -> None:
        """Der Fall aus dem Betrieb: Abbruch im sechsten Knoten."""
        ergebnis = self._fahren(scheitert_nach=5)

        self.assertEqual(
            "Die fertige Antwort.", ergebnis.get("response"),
            "die freigegebene Antwort ist beim Abbruch verlorengegangen",
        )

    def test_der_unvollstaendige_lauf_ist_erkennbar(self) -> None:
        """Wer den Stand bekommt, muss wissen, dass er kein Abschluss ist."""
        ergebnis = self._fahren(scheitert_nach=5)

        self.assertTrue(
            ergebnis.get("lauf_unvollstaendig"),
            "ein abgebrochener Lauf ist nicht von einem abgeschlossenen zu unterscheiden",
        )
        self.assertIn("TypeError", str(ergebnis.get("lauf_fehler", "")))

    def test_der_vollstaendige_lauf_traegt_die_marke_nicht(self) -> None:
        """Die Gegenprobe — sonst waere die Marke immer da und saegte nichts."""
        ergebnis = self._fahren(scheitert_nach=None)

        self.assertEqual("Die fertige Antwort.", ergebnis.get("response"))
        self.assertFalse(ergebnis.get("lauf_unvollstaendig"))
        self.assertTrue(ergebnis.get("fertig"), "der letzte Knoten fehlt im Ergebnis")

    def test_der_fehler_wird_protokolliert(self) -> None:
        """Gerettet wird die Antwort, nicht der Fehler."""
        with self.assertLogs("ki_server.event_consumer", level="ERROR") as protokoll:
            self._fahren(scheitert_nach=5)
        zeilen = "\n".join(protokoll.output)
        self.assertIn("TypeError", zeilen)
        self.assertIn("Traceback", zeilen, "der Traceback fehlt")

    def test_abbruch_vor_der_freigabe_rettet_nichts(self) -> None:
        """Vor dem Responder gibt es keine Antwort — und das ist richtig so.

        **Der Riegel gegen die naheliegende Ueberdehnung:** Wer jeden
        Zwischenstand sendet, sendet irgendwann eine Antwort, die Thinker und
        Tribunal nie gesehen haben.
        """
        graph = _Graph(VERLAUF, scheitert_nach=0)
        ergebnis = _graph_streamen(graph, {"user_id": USER}, self.loop, USER, FIGUR)

        self.assertFalse(ergebnis.get("response"))
        self.assertTrue(ergebnis.get("lauf_unvollstaendig"))


if __name__ == "__main__":
    unittest.main()
