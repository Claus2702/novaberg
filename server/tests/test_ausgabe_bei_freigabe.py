"""Tests: Die Antwort geht raus, sobald sie freigegeben ist — nicht am Ende.

**Der Zeitpunkt ist die Freigabe, nicht die Erzeugung.** Der Responder
formuliert, aber Thinker und Tribunal koennen sperren; erst wenn `evaluate`
auf `output` (oder `fallback`) entscheidet, steht der Text fest. Danach
folgen vier Knoten, die ihn nicht mehr aendern: Perzeption, EI-Persistenz,
Salienz, Dispatcher.

Bis zum 25.08.2026 wartete die Auslieferung auf **END** — also hinter diesen
vier. Am 25.08. um 13:33 kostete das eine fertige, vom Tribunal angenommene
Antwort: Ein `TypeError` in der Salienz riss den Graphen, und der Nutzer sah
nichts. Kennung: `AUSLIEFERUNG-HINTER-DEM-NACHLAUF`.

**Warum `perzeption_assistant` das Signal ist:** Die Freigabe faellt in einer
Kante (`_after_evaluate`), und Kanten erscheinen nicht im Stream. Der erste
Knoten *nach* der Freigabe ist `perzeption_assistant` — er wird sowohl ueber
`output` als auch ueber `fallback` erreicht, also genau auf den beiden Wegen,
auf denen eine Antwort ausgegeben werden soll. Erscheint er, ist entschieden.

Die Zusicherungen hier:

  1. **Freigegeben heisst gesendet** — beim ersten Knoten nach der Weiche.
  2. **Genau einmal.** Wer bei der Freigabe sendet, darf am Ende nicht noch
     einmal senden.
  3. **Nicht vor der Freigabe.** Ein Abbruch zwischen Responder und Tribunal
     stellt nichts zu — die Antwort hat die Pruefung nicht bestanden.
  4. **Der Nachlauf laeuft weiter.** Die vier Knoten danach tun ihre Arbeit;
     gesendet wird nur frueher.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from services.event_consumer import _graph_streamen

USER: str = "meister"
FIGUR: str = "nova"
ANTWORT: str = "Die freigegebene Antwort."


class _Graph:
    """Ein CharacterGraph-Doppel mit steuerbarem Abbruchpunkt."""

    def __init__(self, knoten: list, scheitert_bei: str | None = None):
        self._knoten = knoten
        self._scheitert_bei = scheitert_bei

    def stream(self, _state: dict):
        for name, zustand in self._knoten:
            if name == self._scheitert_bei:
                raise TypeError("unsupported operand type(s) for +: 'int' and 'NoneType'")
            yield {name: zustand}


def _verlauf(response: str = ANTWORT) -> list:
    zustand = {"response": response, "user_id": USER, "tribunal_verdict": "ok"}
    return [
        ("responder", zustand), ("thinker", zustand), ("tribunal", zustand),
        ("evaluate", zustand),
        ("perzeption_assistant", zustand),          # ← ab hier ist freigegeben
        ("ei_calc_persist", zustand), ("salience", zustand), ("dispatcher", zustand),
    ]


class BeiDerFreigabeWirdGesendet(unittest.TestCase):

    def setUp(self) -> None:
        self.loop = MagicMock()
        self.gesendet: list = []
        p = patch("services.event_consumer.broadcast_threadsafe",
                  side_effect=lambda u, nutzlast, *a, **k: self.gesendet.append(nutzlast))
        p.start()
        self.addCleanup(p.stop)

    def _fahren(self, scheitert_bei: str | None = None, response: str = ANTWORT) -> dict:
        graph = _Graph(_verlauf(response), scheitert_bei=scheitert_bei)
        return _graph_streamen(
            graph, {"user_id": USER}, self.loop, USER, FIGUR,
            bei_freigabe=self._melden,
        )

    def _melden(self, zustand: dict) -> None:
        self.gesendet.append(f"ANTWORT:{zustand.get('response', '')}")

    def _antworten(self) -> list:
        return [g for g in self.gesendet if isinstance(g, str) and g.startswith("ANTWORT:")]

    def test_die_antwort_geht_bei_der_freigabe_raus(self) -> None:
        """Nicht am Ende, sondern beim ersten Knoten nach der Weiche."""
        self._fahren()
        self.assertEqual([f"ANTWORT:{ANTWORT}"], self._antworten())

    def test_genau_einmal(self) -> None:
        """Vier Nachlaufknoten duerfen nicht vier Sendungen ausloesen."""
        self._fahren()
        self.assertEqual(1, len(self._antworten()))

    def test_ein_fehler_im_nachlauf_aendert_nichts_mehr(self) -> None:
        """Der Fall vom 25.08.2026: Abbruch in der Salienz, Antwort ist schon draussen."""
        self._fahren(scheitert_bei="salience")
        self.assertEqual([f"ANTWORT:{ANTWORT}"], self._antworten())

    def test_vor_der_freigabe_wird_nichts_gesendet(self) -> None:
        """Ein Abbruch im Tribunal stellt nichts zu — die Pruefung lief nicht durch.

        **Der Riegel gegen die naheliegende Ueberdehnung.** Wer frueher sendet,
        sendet irgendwann einen Text, den Thinker und Tribunal nie freigegeben
        haben.
        """
        self._fahren(scheitert_bei="tribunal")
        self.assertEqual([], self._antworten())

    def test_der_nachlauf_laeuft_weiter(self) -> None:
        """Gesendet wird frueher — gearbeitet wird unveraendert bis zum Ende."""
        ergebnis = self._fahren()
        self.assertFalse(ergebnis.get("lauf_unvollstaendig"))
        self.assertEqual(ANTWORT, ergebnis.get("response"))

    def test_ohne_antwort_meldet_die_freigabe_nichts(self) -> None:
        """Eine leere Antwort ist kein Sendegrund — dafuer gibt es die Ausfallmeldung."""
        self._fahren(response="")
        self.assertEqual([], self._antworten())


if __name__ == "__main__":
    unittest.main()
