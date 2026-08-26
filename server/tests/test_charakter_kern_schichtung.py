"""Tests: Das Material des Kern-Hash ist ueber die Historie geschichtet.

Ziel: Der Kern-Hash liest nicht mehr die neuesten 40 Begegnungen, sondern
zeitlich gleichmaessig verteilte bis zu einem festen Zeichenbudget. Der
Anlass ist gemessen, nicht ueberlegt: Mit dem gleitenden Fenster beschrieb
der Kern das Themenband dieses Fensters und keine wiedererkennbare Person —
Novas sieben Kern-Profile aehnelten einander nicht staerker als die Profile
sieben verschiedener Menschen (Ueberdeckung 16,0 % gegen 16,3 %), und von
641 Inhaltswoertern stand eines in allen sieben (`KERNHASH-TRAEGT-KEINE-PERSON`,
25.08.2026).

Zeugen dieser Datei:
  * **Der Baustein und die Verdrahtung werden getrennt geprueft.** Eine
    richtige Auswahlfunktion, die niemand aufruft, ist derselbe Defekt wie
    gar keine. Der letzte Zeuge faehrt deshalb `_turns_laden` und sieht nach,
    **welche** Kennungen der zweite Lesevorgang anfordert.
  * **Ein Verbotszeuge steht nie allein.** Die Zusicherung *„es ist nicht das
    Fenster der neuesten"* steht nur neben einer Zusicherung, die belegt,
    dass ueberhaupt etwas gewaehlt wurde und dass die Enden getroffen sind.
  * **Das Budget wird an einer Historie geprueft, die es ueberschreitet.**
    Ein Zeuge, dessen Material unter dem Budget bleibt, prueft das Budget
    nicht — er prueft nur, dass nichts wegfaellt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.charakter.agent import CharakterAgent
from agents.charakter.destillation import geschichtet_waehlen

AGENT_LOGGER: str = "ki_server.agents.charakter"
DESTILLATION_LOGGER: str = "ki_server.agents.charakter.destillation"


class TestGeschichtetWaehlen(unittest.TestCase):
    """Die Auswahl selbst — gleichmaessig verteilt, im Budget, geordnet."""

    def test_historie_unter_budget_geht_vollstaendig_durch(self) -> None:
        """Passt alles hinein, wird nichts ausgewaehlt — es wird alles genommen."""
        laengen = [100] * 20

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=10_000)

        self.assertEqual(gewaehlt, list(range(20)))

    def test_budget_wird_gehalten(self) -> None:
        """Die Summe der gewaehlten Laengen ueberschreitet das Budget nicht."""
        laengen = [100] * 200

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=2_500)

        summe = sum(laengen[p] for p in gewaehlt)
        self.assertLessEqual(summe, 2_500)
        self.assertGreater(len(gewaehlt), 0, "Eine leere Auswahl waere ein Ausfall")

    def test_auswahl_trifft_beide_enden_der_historie(self) -> None:
        """Der aelteste Beitrag ist dabei — genau das konnte das Fenster nie."""
        laengen = [100] * 200

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=2_500)

        self.assertEqual(gewaehlt[0], 0, "Die aelteste Begegnung fehlt")
        self.assertGreater(
            gewaehlt[-1], len(laengen) * 3 // 4,
            "Die juengste Haelfte der Historie ist nicht vertreten",
        )

    def test_auswahl_ist_nicht_das_fenster_der_neuesten(self) -> None:
        """Der Verbotszeuge, und er steht neben zwei positiven Zusicherungen.

        Ohne die beiden waere er auch dann gruen, wenn gar nichts gewaehlt
        wuerde — eine leere Auswahl ist ebenfalls nicht das Fenster.
        """
        laengen = [100] * 200

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=2_500)

        fenster = list(range(200 - len(gewaehlt), 200))
        self.assertEqual(len(gewaehlt), 25)
        self.assertEqual(gewaehlt[0], 0)
        self.assertNotEqual(gewaehlt, fenster)

    def test_positionen_sind_aufsteigend_und_verschieden(self) -> None:
        """Doppelte Positionen wuerden denselben Turn zweimal ins Profil legen."""
        laengen = [7] * 97

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=100)

        self.assertEqual(gewaehlt, sorted(set(gewaehlt)))

    def test_ungleiche_laengen_werden_nach_zeichen_gedeckelt(self) -> None:
        """Das Budget zaehlt Zeichen, nicht Begegnungen.

        Eine Grenze in Begegnungen misst die falsche Groesse — im Bestand
        liegen sie zwischen 109 und ueber 1000 Zeichen.
        """
        laengen = [1000 if i % 2 else 10 for i in range(100)]

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=3_000)

        self.assertLessEqual(sum(laengen[p] for p in gewaehlt), 3_000)

    def test_nach_dem_kuerzen_wird_aufgefuellt(self) -> None:
        """Geprueft wird die Abbruchregel: eine mehr passt nicht mehr hinein.

        Die proportionale Kuerzung springt und landet unter dem, was noch
        hineinpasst; ungenutztes Budget ist weniger Material, also genau die
        Groesse, die der Umbau vergroessern sollte. Die Zusicherung lautet
        deshalb nicht *„es sind mindestens N"* — jede feste Zahl haenge an der
        Verteilung der Laengen —, sondern **eine Begegnung mehr wuerde das
        Budget reissen**.

        Der Zeuge wiederholt dafuer die Verteilungsformel. Das ist Absicht und
        seine Grenze: Er prueft die **Abbruchregel**, nicht die Verteilung —
        die pruefen `test_auswahl_trifft_beide_enden_der_historie` und
        `test_positionen_sind_aufsteigend_und_verschieden`.
        """
        laengen = [i + 1 for i in range(200)]
        budget = 2_000

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget)

        self.assertLessEqual(sum(laengen[p] for p in gewaehlt), budget)
        self.assertLess(len(gewaehlt), len(laengen), "Es passte nicht alles hinein")

        eine_mehr = len(gewaehlt) + 1
        positionen = [min(i * 200 // eine_mehr, 199) for i in range(eine_mehr)]
        self.assertGreater(
            sum(laengen[p] for p in positionen), budget,
            "Eine Begegnung mehr haette noch hineingepasst — es wurde nicht "
            "aufgefuellt",
        )

    def test_auffuellen_haelt_am_budget_an(self) -> None:
        """Das Auffuellen darf das Budget nicht ueberschreiten.

        Ohne diesen Zeugen waere der vorige auch dann gruen, wenn das
        Auffuellen einfach alles naehme.
        """
        laengen = [100] * 200

        with self.assertLogs(DESTILLATION_LOGGER, level="INFO"):
            gewaehlt = geschichtet_waehlen(laengen, budget=2_500)

        self.assertLessEqual(sum(laengen[p] for p in gewaehlt), 2_500)
        self.assertLess(len(gewaehlt), 200)

    def test_leere_historie_ergibt_leere_auswahl(self) -> None:
        self.assertEqual(geschichtet_waehlen([], budget=1_000), [])

    def test_budget_null_wird_gemeldet_und_nicht_geraten(self) -> None:
        """Kein stiller Default — ein unbrauchbares Budget ist ein Fehler."""
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
            gewaehlt = geschichtet_waehlen([100, 100], budget=0)

        self.assertEqual(gewaehlt, [])
        self.assertTrue(
            any("Budget 0" in z for z in protokoll.output),
            f"Der Wert gehoert in die Meldung, nicht nur das Feld: {protokoll.output}",
        )

    def test_negative_zeichenzahl_ist_ein_defekt_der_quelle(self) -> None:
        """Leer und unbrauchbar sind zwei Faelle, und nur einer ist harmlos."""
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
            gewaehlt = geschichtet_waehlen([100, -1, 100], budget=1_000)

        self.assertEqual(gewaehlt, [])
        self.assertTrue(
            any("negativ" in z for z in protokoll.output),
            f"Die Quelle ist defekt und das gehoert gesagt: {protokoll.output}",
        )

    def test_einzelne_zu_grosse_begegnung_wird_genommen_und_gemeldet(self) -> None:
        """Eine leere Auswahl bei vorhandenem Material waere ein stiller Ausfall."""
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as protokoll:
            gewaehlt = geschichtet_waehlen([5_000, 5_000], budget=100)

        self.assertEqual(len(gewaehlt), 1)
        self.assertTrue(
            any("ueberschreitet das Budget" in z for z in protokoll.output),
            f"Die Ueberschreitung gehoert ins Log: {protokoll.output}",
        )


class _Bank:
    """Datenbank-Attrappe fuer den zweistufigen Lesepfad.

    Sie merkt sich, welche Kennungen der zweite Schritt angefordert hat —
    daran und nur daran ist die Verdrahtung zu erkennen.
    """

    def __init__(self, turns: list[dict]) -> None:
        self.turns = turns
        self.angefordert: list[int] = []

    def select(self, sql: str, params: tuple = ()) -> list[dict]:
        if "count(*)" in sql:
            return [{"impulse": 0, "ohne_marke": 0}]
        if "length(inhalt" in sql:
            return [
                {"id": i, "zeichen": len(t["aeusserung"]) + len(t["antwort"])}
                for i, t in enumerate(self.turns)
            ]
        self.angefordert = list(params[0])
        return [self.turns[i] for i in self.angefordert]


class TestVerdrahtung(unittest.TestCase):
    """Die Auswahl wirkt nur, wenn `_turns_laden` sie auch benutzt.

    `_turns_laden` benutzt `self` nicht; die Methode wird ungebunden mit
    `None` aufgerufen, statt einen Agenten samt Datenbank zu bauen.
    """

    def test_turns_laden_zieht_ueber_die_ganze_historie(self) -> None:
        """Angefordert werden verteilte Kennungen, nicht die letzten N."""
        turns = [{"aeusserung": f"a{i}", "antwort": "x" * 96} for i in range(200)]
        bank = _Bank(turns)

        with patch("agents.charakter.agent.db_manager", bank):
            with self.assertLogs(AGENT_LOGGER, level="INFO"):
                treffer = CharakterAgent._turns_laden(None, "meister", budget=2_500)

        self.assertGreater(len(treffer), 0)
        self.assertEqual(bank.angefordert[0], 0, "Die aelteste Begegnung fehlt")
        self.assertGreater(
            bank.angefordert[-1], 150,
            "Die juengste Haelfte der Historie ist nicht vertreten",
        )
        self.assertNotEqual(
            bank.angefordert,
            list(range(200 - len(bank.angefordert), 200)),
            "Angefordert wurde das Fenster der neuesten Begegnungen",
        )

    def test_log_nennt_grundmenge_und_budget(self) -> None:
        """Ohne beide Zahlen ist eine schmale Auswahl nicht deutbar."""
        turns = [{"aeusserung": f"a{i}", "antwort": "x" * 96} for i in range(200)]
        bank = _Bank(turns)

        with patch("agents.charakter.agent.db_manager", bank):
            with self.assertLogs(AGENT_LOGGER, level="INFO") as protokoll:
                CharakterAgent._turns_laden(None, "meister", budget=2_500)

        self.assertTrue(
            any("von 200 Begegnungen der Historie" in z for z in protokoll.output),
            f"Die Grundmenge gehoert ins Log: {protokoll.output}",
        )
        self.assertTrue(
            any("Budget 2500 Zeichen" in z for z in protokoll.output),
            f"Das wirksame Budget gehoert ins Log: {protokoll.output}",
        )


if __name__ == "__main__":
    unittest.main()
