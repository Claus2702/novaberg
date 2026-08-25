"""Tests: Der Adaptiv-Hash waehlt nach Staerke, nicht nach Fundreihenfolge.

Ziel: Ein Profil mit der Frage "Was beschaeftigt ihn gerade?" liest die
Eintraege mit dem hoechsten Produkt aus Salienz und Zeitgewicht — nicht die,
die Redis beim Durchlaufen zuerst ausspuckt.

Zeugen dieser Datei:
  * **Die Attrappe liefert bewusst in falscher Reihenfolge.** `scan_iter`
    gibt die Schluessel gemischt zurueck, aeltere zuerst. Genau das tut das
    echte SCAN: Es sagt keine Ordnung zu. Eine Attrappe, die schon sortiert
    liefert, koennte den Defekt nicht bilden — und was die Attrappe nicht
    bauen kann, prueft kein Test.
  * **Geprueft wird die Auswahl, nicht nur ihre Groesse.** Dass zwanzig
    Eintraege zurueckkommen, war auch vorher wahr. Die Zusicherung gilt
    ihrer Zusammensetzung und ihrer Reihenfolge.
  * **Die Kante bei einem Tag hat einen eigenen Zeugen.** Die abgeloeste
    Kurve sprang dort von 1.00 auf 0.80; zwei Eintraege, die eine Minute
    trennte, unterschieden sich um ein Fuenftel. Der Test faellt gegen die
    alte Kurve durch und ist damit die Gegenprobe zum Umbau.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import time
import unittest
from unittest.mock import patch

from agents.charakter.agent import CharakterAgent
from agents.charakter.destillation import (
    adaptive_hash_destillieren,
    alterszone,
    zeitgewicht,
)
from config import PIXIE_CHARAKTER_KZG_LIMIT

AGENT_LOGGER:        str = "ki_server.agents.charakter"
DESTILLATION_LOGGER: str = "ki_server.agents.charakter.destillation"

TAG: float = 86400.0

# **Einmal gelesen, dann festgehalten.** Der Schluessel eines Eintrags wird an
# zwei Stellen gebraucht — beim Aufbau des Bestandes und in der Zusicherung —
# und muss beidemal derselbe sein. Eine Uhr, die bei jedem Aufruf neu gelesen
# wird, liefert dazwischen eine getickte Millisekunde und damit zwei
# Schluessel fuer denselben Eintrag (`ZEUGE-ERWARTUNG-AUS-DER-UHR`).
SCHLUESSEL_BASIS: float = time.time()


class _Redis:
    """Redis-Attrappe: haelt Hashes und zaehlt die Feldzugriffe.

    `scan_iter` liefert **unsortiert** — in der Reihenfolge, in der die
    Eintraege angelegt wurden. Die Tests legen sie absichtlich mit den
    aeltesten zuerst an.
    """

    def __init__(self, hashes: dict[str, dict[str, str]]) -> None:
        self.hashes = hashes
        self.hget_aufrufe: int = 0

    def scan_iter(self, match: str = "", count: int = 0):
        praefix = match.rstrip("*")
        for key in self.hashes:
            if key.startswith(praefix):
                yield key

    def hget(self, key: str, field: str):
        self.hget_aufrufe += 1
        return self.hashes.get(key, {}).get(field)


def _eintrag(
    alter_tage:  float,
    salienz:     float,
    beobachter:  str = "user",
    themen:      str = "Thema",
) -> dict[str, str]:
    """Baut einen KZG-Hash, wie ihn der Schreibpfad ablegt."""
    return {
        "beobachter":         beobachter,
        "themen":             themen,
        "inhalt":             f"Inhalt {alter_tage:.2f}d",
        "salienz":            str(salienz),
        "erstellt_am":        str(time.time() - alter_tage * TAG),
        "modus":              "sachlich",
        "emotion":            "neutral",
        "beziehungs_dynamik": "vertraut",
        "tone":               "ruhig",
    }


def _schluessel(alter_tage: float) -> str:
    """Der Schluessel traegt seine Zeitmarke in Millisekunden.

    Die Marke ist **Identitaet, kein Alter**: Das Alter eines Eintrags liest
    die Destillation aus `erstellt_am` (`destillation.py`), den Schluessel
    benutzt sie nur zum Nachschlagen des Wortlauts. Deshalb rechnet er gegen
    die festgehaltene Basis, waehrend `_eintrag` die laufende Uhr liest —
    die Alterswerte der uebrigen Zeugen bleiben damit unveraendert.
    """
    return f"kzg:meister:nova:{int((SCHLUESSEL_BASIS - alter_tage * TAG) * 1000)}"


def _bestand(*paare: tuple[float, float]) -> dict[str, dict[str, str]]:
    return {_schluessel(alter): _eintrag(alter, salienz) for alter, salienz in paare}


class TestSchluesselIstStabil(unittest.TestCase):
    """Derselbe Eintrag bekommt denselben Schluessel, wann immer man fragt.

    Der Zeuge stellt den Fall deterministisch her, der die volle Suite in
    einem von vier Laeufen rot machte (`ZEUGE-ERWARTUNG-AUS-DER-UHR`): Der
    Erwartungswert entstand zweimal aus der Uhr, und dazwischen tickte eine
    Millisekunde. **Der betroffene Zeuge kann seine eigene Abhilfe nicht
    bewachen** — ob er rot wird, entscheidet die Laufzeit der Suite.
    """

    def test_zwei_aufrufe_liefern_denselben_schluessel(self) -> None:
        """Die Uhr rueckt zwischen den Aufrufen vor; der Schluessel nicht."""
        with patch("time.time", side_effect=[
            SCHLUESSEL_BASIS, SCHLUESSEL_BASIS + 0.001,
        ]):
            self.assertEqual(_schluessel(1.0), _schluessel(1.0))


class TestZeitgewicht(unittest.TestCase):
    """Die Kurve selbst — stetig, fallend, ohne Kante."""

    def test_halbwertszeit_halbiert(self) -> None:
        self.assertAlmostEqual(zeitgewicht(1.7), 0.5, places=6)

    def test_frisch_ist_eins(self) -> None:
        self.assertAlmostEqual(zeitgewicht(0.0), 1.0, places=9)

    def test_streng_fallend(self) -> None:
        werte = [zeitgewicht(t) for t in (0, 0.5, 1, 2, 5, 10, 30)]
        self.assertEqual(werte, sorted(werte, reverse=True))
        self.assertEqual(len(set(werte)), len(werte))

    def test_keine_kante_bei_einem_tag(self) -> None:
        """Die abgeloeste Kurve sprang hier von 1.00 auf 0.80.

        Der Zeuge ist die Gegenprobe zum Umbau: Gegen das Stueckwerk faellt er
        durch, weil dort eine Minute ein Fuenftel Gewicht kostete.
        """
        eine_minute = 1.0 / 1440
        davor  = zeitgewicht(1.0 - eine_minute)
        danach = zeitgewicht(1.0 + eine_minute)
        self.assertLess(
            (davor - danach) / davor, 0.01,
            "Zwei Eintraege, die eine Minute trennt, duerfen sich nicht "
            "um mehr als ein Prozent unterscheiden",
        )

    def test_zukunft_wird_geklemmt(self) -> None:
        with self.assertLogs(DESTILLATION_LOGGER, level="WARNING"):
            self.assertAlmostEqual(zeitgewicht(-5.0), 1.0, places=9)

    def test_halbwertszeit_null_faellt_laut_aus(self) -> None:
        with patch(
            "agents.charakter.destillation."
            "PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE", 0.0
        ):
            with self.assertRaises(ValueError):
                zeitgewicht(1.0)

    def test_zone_benennt_das_alter(self) -> None:
        self.assertEqual(alterszone(0.5), "AKUT")
        self.assertEqual(alterszone(3.0), "PHASE")
        self.assertEqual(alterszone(20.0), "TREND")


class TestAuswahl(unittest.TestCase):
    """`_kzg_laden` ordnet nach Staerke.

    `_kzg_laden` benutzt `self` nicht; die Methode wird deshalb ungebunden
    mit `None` aufgerufen, statt einen Agenten samt Datenbank zu bauen.
    """

    def _laden(self, bestand: dict, beobachter: str = "user") -> tuple[list[dict], _Redis]:
        attrappe = _Redis(bestand)
        with patch("agents.charakter.agent.redis_client", attrappe):
            with self.assertLogs(AGENT_LOGGER, level="INFO"):
                treffer = CharakterAgent._kzg_laden(
                    None, "meister", "nova", beobachter_filter=beobachter,
                )
        return treffer, attrappe

    def test_juenger_schlaegt_staerker(self) -> None:
        """Ein Tag alt mit Salienz 0.7 verdraengt zwanzig Tage alt mit 1.0."""
        bestand = _bestand((20.0, 1.0), (1.0, 0.7))
        treffer, _ = self._laden(bestand)

        self.assertEqual(len(treffer), 2)
        self.assertIn("1.00d", treffer[0]["inhalt"])
        self.assertIn("20.00d", treffer[1]["inhalt"])

    def test_die_staerksten_zwanzig_statt_der_ersten(self) -> None:
        """Fuenf junge muessen sich gegen fuenfundzwanzig alte durchsetzen.

        Die Attrappe legt die alten zuerst an — die abgeloeste Fassung haette
        genau diese zwanzig genommen und keinen einzigen jungen gesehen.
        """
        paare = [(20.0 + i * 0.01, 1.0) for i in range(25)]
        paare += [(1.0 + i * 0.01, 0.7) for i in range(5)]
        treffer, _ = self._laden(_bestand(*paare))
        jetzt = time.time()
        alter = [(jetzt - float(t["erstellt_am"])) / TAG for t in treffer]

        self.assertEqual(len(treffer), PIXIE_CHARAKTER_KZG_LIMIT)
        self.assertEqual(
            len([a for a in alter if a < 5.0]), 5,
            f"Alle fuenf jungen Eintraege gehoeren in die Auswahl: {alter}",
        )
        self.assertLess(
            alter[0], 5.0,
            "Der staerkste Eintrag ist einer der jungen",
        )

    def test_absteigend_nach_effektiver_salienz(self) -> None:
        treffer, _ = self._laden(_bestand((0.5, 0.9), (3.0, 1.0), (0.1, 0.5)))
        jetzt = time.time()
        werte = [
            float(t["salienz"]) * zeitgewicht((jetzt - float(t["erstellt_am"])) / TAG)
            for t in treffer
        ]
        self.assertEqual(werte, sorted(werte, reverse=True))

    def test_ladegrenze_haelt_alte_draussen(self) -> None:
        treffer, _ = self._laden(_bestand((45.0, 1.0), (2.0, 0.8)))
        self.assertEqual(len(treffer), 1)
        self.assertIn("2.00d", treffer[0]["inhalt"])

    def test_fremde_perspektive_bleibt_draussen(self) -> None:
        bestand = {
            _schluessel(1.0): _eintrag(1.0, 0.9, beobachter="user"),
            _schluessel(1.1): _eintrag(1.1, 1.0, beobachter="assistant"),
        }
        treffer, _ = self._laden(bestand, beobachter="user")
        self.assertEqual(len(treffer), 1)
        self.assertEqual(treffer[0]["_key"], _schluessel(1.0))

    def test_abbruch_liest_nicht_den_ganzen_bestand(self) -> None:
        """Der Beweis-Abbruch spart die Zugriffe, die nichts mehr aendern.

        Zwanzig frische Eintraege fuellen die Auswahl; die zweihundert alten
        dahinter koennen sie nicht mehr erreichen und werden nicht geladen.
        """
        paare = [(0.1 + i * 0.001, 1.0) for i in range(PIXIE_CHARAKTER_KZG_LIMIT)]
        paare += [(15.0 + i * 0.01, 1.0) for i in range(200)]
        treffer, attrappe = self._laden(_bestand(*paare))

        self.assertEqual(len(treffer), PIXIE_CHARAKTER_KZG_LIMIT)
        self.assertLess(
            attrappe.hget_aufrufe, 200,
            "Nach der Gewichtsschranke darf nicht weitergelesen werden",
        )

    def test_ohne_themen_belegt_keinen_platz(self) -> None:
        """Was die Destillation ohnehin verwirft, darf keinen Platz kosten.

        Gemessen am 16.08.2026: Unter den juengsten `assistant`-Eintraegen
        tragen nur 70 % ein Themenfeld. Ohne diesen Filter waehlt die Auswahl
        gerade die staerksten davon — und der Prompt bleibt halb leer.
        """
        bestand = {
            _schluessel(0.1): _eintrag(0.1, 1.0, themen=""),
            _schluessel(0.2): _eintrag(0.2, 1.0, themen="   "),
            _schluessel(3.0): _eintrag(3.0, 0.8, themen="Astronomie"),
        }
        treffer, _ = self._laden(bestand)

        self.assertEqual(len(treffer), 1)
        self.assertEqual(treffer[0]["themen"], "Astronomie")

    def test_unbekannte_perspektive_faellt_laut_aus(self) -> None:
        with patch("agents.charakter.agent.redis_client", _Redis({})):
            with self.assertRaises(ValueError):
                CharakterAgent._kzg_laden(
                    None, "meister", "nova", beobachter_filter="niemand",
                )

    def test_leerer_bestand_gibt_leer(self) -> None:
        treffer, _ = self._laden({})
        self.assertEqual(treffer, [])


class TestVerwurfWirdGezaehlt(unittest.TestCase):
    """Was nicht in den Prompt kommt, steht im Log."""

    def test_eintrag_ohne_themen_wird_gezaehlt(self) -> None:
        eintraege = [
            {"themen": "Astronomie", "inhalt": "a", "salienz": "0.9",
             "erstellt_am": str(time.time())},
            {"themen": "", "inhalt": "b", "salienz": "0.9",
             "erstellt_am": str(time.time())},
        ]
        with patch(
            "agents.charakter.destillation._llm_call", return_value="Profil"
        ):
            with self.assertLogs(DESTILLATION_LOGGER, level="INFO") as protokoll:
                ergebnis = adaptive_hash_destillieren(eintraege, user_id="meister")

        self.assertEqual(ergebnis, "Profil")
        self.assertTrue(
            any("1 ohne Themen verworfen" in zeile for zeile in protokoll.output),
            f"Der Verwurf muss gezaehlt werden: {protokoll.output}",
        )

    def test_nur_unbrauchbares_meldet_fehler(self) -> None:
        eintraege = [{"themen": "", "inhalt": "x", "salienz": "1",
                      "erstellt_am": str(time.time())}]
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR"):
            self.assertEqual(adaptive_hash_destillieren(eintraege), "")


if __name__ == "__main__":
    unittest.main()
