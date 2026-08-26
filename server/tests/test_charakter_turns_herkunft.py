"""Tests: Ein eigener Impuls gehört in kein Charakterprofil.

Ziel: Beide Charakter-Räder messen eine Haltung GEGENÜBER jemandem. Ein
Impuls hat kein Gegenüber — er trägt weder zum Profil des Menschen noch zum
Profil der Figur etwas bei.

Der Anlass ist gemessen, nicht überlegt: Ein Impuls legt seinen Text in
dasselbe Feld `user_prompt` wie eine Nutzeräußerung. Ungefiltert las
`_turns_laden` die eigenen Gedanken der Figur als Äußerungen des Menschen.
Am 16.08.2026 am produktiven Paar: von 40 gelesenen Turns **25 Impulse mit
95,4 % des Materials**, die tatsächlichen Äußerungen 1761 Zeichen (4,6 %).

Zeugen dieser Datei:
  * **Der Filter sitzt in SQL, also prüft ein Zeuge die abgesetzte Abfrage.**
    Eine Attrappe der Datenbank kann kein `WHERE` ausführen; sie kann nur
    bezeugen, dass die Einschränkung überhaupt gestellt wurde. Das ist eine
    schwächere Zusicherung als eine gefilterte Zeilenmenge, und sie steht
    hier ausdrücklich als solche — die Wirkung selbst belegt die Messung am
    echten Bestand, nicht dieser Test.
  * **Die Zahl der ausgenommenen Turns gehört ins Log.** Ohne sie ist
    "wenig Material" nicht von "viel Material, davon das meiste ausgenommen"
    zu unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.charakter.agent import CharakterAgent

AGENT_LOGGER: str = "ki_server.agents.charakter"


class _Bank:
    """Datenbank-Attrappe fuer den zweistufigen Lesepfad.

    Seit dem 26.08.2026 liest `_turns_laden` in zwei Schritten: erst Kennung
    und Zeichenzahl je Begegnung, dann den Wortlaut der ausgewaehlten. Die
    Attrappe bildet beide Schritte aus **derselben** Turn-Liste, damit ein
    Zeuge weiterhin nur Turns hinschreibt — und sie merkt sich, welche
    Kennungen der zweite Schritt angefordert hat.
    """

    def __init__(self, turns: list[dict], zaehlung: dict | None = None) -> None:
        self.turns = turns
        self.zaehlung = zaehlung or {"impulse": 0, "ohne_marke": 0}
        self.abfragen: list[str] = []
        self.angefordert: list[int] = []

    def select(self, sql: str, params: tuple = ()) -> list[dict]:
        self.abfragen.append(sql)
        if "count(*)" in sql:
            return [self.zaehlung]
        if "length(inhalt" in sql:
            return [
                {"id": i, "zeichen": len(t["aeusserung"]) + len(t["antwort"])}
                for i, t in enumerate(self.turns)
            ]
        self.angefordert = list(params[0])
        return [self.turns[i] for i in self.angefordert]


def _turn(aeusserung: str, antwort: str) -> dict:
    return {"aeusserung": aeusserung, "antwort": antwort}


class TestHerkunftsFilter(unittest.TestCase):
    """`_turns_laden` verlangt Begegnungen, nicht Turns.

    `_turns_laden` benutzt `self` nicht; die Methode wird ungebunden mit
    `None` aufgerufen, statt einen Agenten samt Datenbank zu bauen.
    """

    def _laden(self, bank: _Bank, level: str = "INFO"):
        with patch("agents.charakter.agent.db_manager", bank):
            with self.assertLogs(AGENT_LOGGER, level=level) as protokoll:
                treffer = CharakterAgent._turns_laden(None, "meister")
        return treffer, protokoll.output

    def test_abfrage_schraenkt_auf_begegnungen_ein(self) -> None:
        """Die Zusicherung gilt der Abfrage — die Attrappe filtert nicht selbst.

        Der Filter sitzt seit dem 26.08.2026 im **ersten** Schritt, der die
        Grundmenge bestimmt. Genau dort muss er stehen: Der zweite Schritt
        holt nur noch benannte Kennungen und kann nichts mehr ausschliessen,
        was der erste hereingelassen hat.
        """
        bank = _Bank([_turn("hi", "hallo")])
        self._laden(bank)

        grundmenge = [a for a in bank.abfragen if "length(inhalt" in a]
        self.assertEqual(len(grundmenge), 1)
        self.assertIn("herkunft", grundmenge[0])
        self.assertIn("nutzer_turn", grundmenge[0])

        wortlaut = [a for a in bank.abfragen if "id = ANY" in a]
        self.assertEqual(len(wortlaut), 1)
        self.assertNotIn("LIMIT", wortlaut[0],
                         "Der zweite Schritt waehlt nicht mehr aus, er holt nur")

    def test_impulse_werden_gezaehlt_und_gemeldet(self) -> None:
        bank = _Bank([_turn("hi", "hallo")], {"impulse": 25, "ohne_marke": 318})
        _, protokoll = self._laden(bank)

        self.assertTrue(
            any("25 Impulse ausgenommen" in z for z in protokoll),
            f"Die Zahl der Impulse gehoert ins Log: {protokoll}",
        )
        self.assertTrue(
            any("318 ohne Marke" in z for z in protokoll),
            f"Die unmarkierten Turns gehoeren ins Log: {protokoll}",
        )

    def test_leeres_ergebnis_meldet_fehler_mit_zahlen(self) -> None:
        """Kein Material ist ein Fehler, kein leises Nichts.

        Der Fall ist real: Nach dem Filter kann ein Paar, das nur Impulse
        erzeugt hat, ohne Begegnung dastehen. Dann darf kein leeres Profil
        entstehen, das wie ein Ergebnis aussieht.
        """
        bank = _Bank([], {"impulse": 84, "ohne_marke": 0})
        treffer, protokoll = self._laden(bank, level="ERROR")

        self.assertEqual(treffer, [])
        self.assertTrue(
            any("84 Impulse" in z for z in protokoll),
            f"Der Grund gehoert in die Fehlermeldung: {protokoll}",
        )

    def test_reihenfolge_aelteste_zuerst(self) -> None:
        """Die Nachbedingung ist unveraendert; der Weg dorthin nicht.

        Bis zum 26.08.2026 las die Abfrage absteigend und die Liste wurde
        umgedreht. Beide Schritte sortieren jetzt aufsteigend, und die
        Attrappe liefert in derselben Ordnung — die Zusicherung gilt weiter
        dem Ergebnis, nicht dem Umweg.
        """
        bank = _Bank([_turn("alt", "a"), _turn("mittel", "b"), _turn("neu", "c")])
        treffer, _ = self._laden(bank)

        self.assertEqual(
            [t["aeusserung"] for t in treffer], ["alt", "mittel", "neu"],
        )

    def test_leere_felder_fallen_heraus(self) -> None:
        bank = _Bank([_turn("", ""), _turn("da", "")])
        treffer, _ = self._laden(bank)

        self.assertEqual(len(treffer), 1)
        self.assertEqual(treffer[0]["aeusserung"], "da")


if __name__ == "__main__":
    unittest.main()
