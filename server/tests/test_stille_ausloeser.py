"""Der dritte Ausloeser der Zustellung: Stille.

Ziel: Eine abgelaufene Frist beendet Novas Eigeninitiative nicht mehr.

`last_activity` traegt eine TTL von zwei Stunden und wird nur vom Nutzer-Turn
gesetzt. War der Schluessel fort, ging die Zustellschleife jeden Zyklus in
`else: continue` — die Riegelkette wurde nicht einmal gefragt, und beendet hat
das ausschliesslich ein Nutzer-Turn. Gemessen ueber 214,5 h Betrieb: zwoelf
Luecken ueber einer Stunde, **zehn davon enden binnen zwei Minuten mit einer
Aeusserung des Menschen**; die beiden anderen sind exakt 1:00:33 und 1:00:17
lang und damit die Burst-TTL. Zusammen 126 von 214,5 Stunden.

**Warum die Zeugen den Quelltext lesen und nicht den Lauf.** Der Zweig sitzt
inline in einer `while True`-Schleife mit `await asyncio.sleep` am Kopf; eine
Runde davon isoliert zu fahren hiesse, die Schleife zu zerlegen — ein groesserer
Eingriff als der, den sie pruefen sollen. Der Verhaltensbeleg ist deshalb die
Messung am Betrieb, nicht dieser Zeuge. Was er leistet, ist das, was eine
Messung nicht leistet: Er wird rot, wenn jemand die Wand zurueckbaut.
"""

import inspect
import re
import unittest

import services.shadow_delivery as sd


def _schleifenquelle() -> str:
    """Der Quelltext der Zustellschleife, ohne den Rest des Moduls."""
    for name, wert in vars(sd).items():
        if name.startswith("shadow_delivery") and callable(wert):
            return inspect.getsource(wert)
    raise AssertionError(
        "Die Zustellschleife ist unter keinem Namen auffindbar, der mit "
        "'shadow_delivery' beginnt — der Zeuge prueft dann nichts."
    )


class DerStilleAusloeserStehtTest(unittest.TestCase):
    """Die Wand ist gefallen, und an ihrer Stelle steht ein Ausloeser."""

    def setUp(self) -> None:
        self.quelle: str = _schleifenquelle()

    def test_die_schleife_ist_auffindbar(self):
        """Ohne diesen Zeugen pruefen die uebrigen eine leere Zeichenkette."""
        self.assertIn("last_activity", self.quelle)
        self.assertIn("momentum", self.quelle)

    def test_der_ausloeser_stille_existiert(self):
        self.assertIn('trigger = "stille"', self.quelle)

    def test_der_else_zweig_bricht_nicht_mehr_sofort_ab(self):
        """Die Wand war genau `else:` gefolgt von `continue`.

        Der Zeuge trifft die Wand und nicht ihre Nachbarn: Gesucht wird ein
        `else:`, auf das **unmittelbar** ein `continue` folgt. Ein `continue`
        weiter unten im Zweig — etwa hinter der Sitzungspruefung — ist
        erwuenscht und darf nicht rot werden.
        """
        wand = re.search(r"\n\s*else:\s*\n\s*continue\b", self.quelle)
        self.assertIsNone(
            wand,
            "Ein `else:` bricht wieder unmittelbar ab — die Zwei-Stunden-Wand "
            "steht erneut.",
        )

    def test_stille_traegt_dieselbe_sitzungspruefung_wie_der_timeout(self):
        """Ein Einwurf in die leere Sitzung waere eine Begruessung.

        Beide Zweige duerfen nur feuern, wenn ein Gespraech existiert. Gezaehlt
        wird der Aufruf: Vor dem Umbau stand er einmal da, danach zweimal.
        """
        self.assertEqual(
            self.quelle.count("session_turns_retrieve("), 2,
            "Timeout und Stille brauchen je eine eigene Sitzungspruefung.",
        )

    def test_stille_verbraucht_ihren_ausloeser(self):
        """Ohne Verbrauch fragte die Schleife alle 5 s statt alle 30 s.

        Beide Zweige schreiben `last_activity` zurueck. Fehlt das im
        Stille-Zweig, entscheiden die Riegel sechsmal so oft, und ihre
        Verteilung ist mit der des Timeout-Zweigs nicht mehr vergleichbar.
        """
        self.assertEqual(
            self.quelle.count('f"last_activity:{user_id}"'), 3,
            "Erwartet: einmal Lesen, zweimal Zurueckschreiben (Timeout, Stille).",
        )


class DieUhrIstNichtDieAnwesenheitTest(unittest.TestCase):
    """Was die Wand geprueft hat, und was nicht."""

    def test_die_schleife_laeuft_nur_ueber_offene_verbindungen(self):
        """Anwesenheit prueft die Verbindung, nicht `last_activity`.

        Faellt dieser Zeuge, ist der Wegfall der Wand **nicht** mehr harmlos:
        Dann koennte ein Impuls an niemanden gehen.
        """
        quelle: str = _schleifenquelle()
        self.assertIn("websocket_map.keys()", quelle)


if __name__ == "__main__":
    unittest.main()
