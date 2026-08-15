"""Test: Der Gespraechsverlauf ueberdauert den Verfall des Zustands.

Zwei Zahlen an zwei Orten, jede fuer sich plausibel — genau die Konstellation,
in der sie auseinanderlaufen:

    SESSION_TTL                    memory/session.py    wie lange der Verlauf haelt
    EIGENZEIT_NULLPUNKT_SEKUNDEN   config.py            wann der Zustand in Ruhe ist

Bis zum 15.08.2026 lag die Frist bei zwei Stunden und die Kurve bei drei.
Dazwischen klaffte ein Fenster, in dem der **Verlauf vor dem Zustand**
verschwindet: Nova waere noch nicht zur Ruhe gekommen und haette schon
vergessen, worueber gesprochen wurde. Das ist dieselbe fremde Nova, die
`novaberg-eigenzeit_k.md` §2.2 vermeiden will — nur von der anderen Seite.

**Dieser Zeuge behauptet nicht, dass Bauteil A die Session braucht.** Er
braucht sie nicht: Zustand und Uhr liegen im `nova_state`, der keine Frist
kennt. Geprueft wird allein, dass die beiden Zeitraeume zueinander passen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import EIGENZEIT_NULLPUNKT_SEKUNDEN
from memory.session import SESSION_TTL


class DerVerlaufUeberlebtDenZustandTest(unittest.TestCase):
    """Erst ist die Ruhe erreicht, dann darf der Verlauf gehen."""

    def test_die_session_ueberdauert_die_kurve(self) -> None:
        """Die Frist ist die Untergrenze, nicht der Zielwert — laenger ist erlaubt."""
        self.assertGreaterEqual(SESSION_TTL, EIGENZEIT_NULLPUNKT_SEKUNDEN)


if __name__ == "__main__":
    unittest.main()
