"""Zeugen ueber die Ladung eines Strangs: was ihn stark macht.

Ziel: Salienz, Valenz und Anzahl der Faeden ergeben zusammen, wie stark ein
Strang zieht — und die Praesenz sagt, ob er noch lebt.

Konzept §7.7 in der Fassung vom 02.09.2026. **Vorgabe des Eigentuemers:**
*„Salienz, Valenz, Anzahl Faeden. Das macht den Strang stark."* — und zur
Anzahl: *„Wenn ich viele emotionale Eindruecke (Faeden) habe, dann ist ein
Thema intensiv gepraegt. Es ist lebendig. Es ist praesent."*

**Die Fassung loest die des Konzepts ab**, die Anlaesse, Spitze und Spanne
nannte. Der Grund gegen Anlaesse dort war ein Messfehler — zwanzig Zeilen aus
einer Erhebung taeuschten eine Stichprobe von zwanzig vor. Hier ist es keine
Stichprobe: **Das Tor hat jeden Faden einzeln durchgelassen** (4 von 13
Pruefungen im Betrieb), und zwanzig Faeden sind zwanzig Erlebnisse.

**`mittel(|valenz|)`, nicht `|mittel(valenz)|`** — der Unterschied ist der
Kern und nicht die Schreibweise. Vorgabe: *„Wenn die sich aufheben wuerden,
wuerden viele Faeden eigentlich zu einer Nullung fuehren statt zu einer
Intensivierung der Praegung."*

**Sie wird nicht gespeichert**, wie die Richtung: `f_praesenz` macht sie
zeitabhaengig, und eine Spalte truege die Antwort von gestern.

Die Zusicherungen:

  1. **Die drei Eingaenge stehen additiv**, nicht multiplikativ — Regel (a) des
     Konzepts: keine Null aus einer Multiplikation.
  2. **Ambivalenz hebt sich nicht auf.** Zwei Freude- und zwei Trauerfaeden
     tragen die volle Valenz, nicht null.
  3. **Mehr Faeden sind mehr Ladung**, mit Saettigung: der zwanzigste traegt
     weniger als der zweite.
  4. **Ein stiller Strang verblasst** — und nicht bis auf null.
  5. **Der Bericht traegt die Teile, nicht nur die Summe.**
  6. **Faeden ohne Salienz zaehlen fuer das Mittel nicht mit und werden
     gemeldet** — ein Vorgabewert waere eine erfundene Messung.
  7. **Der Tageslauf ruft die Rechnung** und legt sie neben die Richtung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import (
    PRAEGUNG_ANZAHL_SAETTIGUNG,
    PRAEGUNG_PRAESENZ_BODEN,
    PRAEGUNG_W_ANZAHL,
    PRAEGUNG_W_SALIENZ,
    PRAEGUNG_W_VALENZ,
)
from memory.praegung import strang_staerke
from tests.test_praegung_strang import _Cursor, _mit_cursor

AGENT_MODUL: str = "agents.synapsen_decay.agent"


def _lauf(faden_zahl: int, mit_salienz: int, salienz_mittel: float,
          ohne_valenz: int = 0, tage_still: float = 0.0,
          emotion: str = "begeisterung") -> dict | None:
    """Faehrt die Rechnung mit einem vorgegebenen Aggregat.

    Zwei Abfragen: je Emotion eine Zeile, dann die Stille. `ohne_valenz` steht
    fuer Faeden aus Sektor 4 — sie tragen in `EMOTION_VALENZ` einen Betrag nahe
    null und senken das Mittel, statt gar nicht zu zaehlen.
    """
    gefaerbt = faden_zahl - ohne_valenz
    zeilen = []
    if gefaerbt:
        # `begeisterung` traegt |1,00| — so bleibt das Valenzmittel ohne
        # Sektor 4 genau 1,0 und die Rechnung ist von Hand nachvollziehbar.
        anteil_sal = min(mit_salienz, gefaerbt)
        zeilen.append((emotion, gefaerbt, anteil_sal,
                       salienz_mittel * mit_salienz if mit_salienz else 0.0))
    if ohne_valenz:
        rest_sal = max(0, mit_salienz - gefaerbt)
        zeilen.append(("verwundert", ohne_valenz, rest_sal, 0.0))
    cursor = _Cursor([zeilen, (tage_still,)])
    with _mit_cursor(cursor):
        return strang_staerke("postgresql://nachgebildet", 7)


class DieDreiEingaengeStehenNebeneinanderTest(unittest.TestCase):
    """Additiv, nicht multiplikativ — Regel (a) des Konzepts §10.0."""

    def test_ein_eingang_auf_null_loescht_die_staerke_nicht(self) -> None:
        """Genau das verbietet Regel (a): keine Null aus einer Multiplikation."""
        ergebnis = _lauf(faden_zahl=4, mit_salienz=0, salienz_mittel=0.0)

        self.assertGreater(
            ergebnis["staerke"], 0.0,
            "Ein Strang ohne eine einzige Salienz steht auf null — ein Faktor "
            "hat die ganze Groesse geloescht",
        )
        self.assertEqual(ergebnis["salienz_mittel"], 0.0)

    def test_die_summe_ist_die_gewichtete_summe_der_drei(self) -> None:
        ergebnis = _lauf(faden_zahl=4, mit_salienz=4, salienz_mittel=0.75)
        erwartet = (
            PRAEGUNG_W_SALIENZ * 0.75
            + PRAEGUNG_W_VALENZ * 1.0
            + PRAEGUNG_W_ANZAHL * (4 / (4 + PRAEGUNG_ANZAHL_SAETTIGUNG))
        )
        self.assertAlmostEqual(ergebnis["staerke"], erwartet, places=6)


class AmbivalenzHebtSichNichtAufTest(unittest.TestCase):
    """Der Kern der Vorgabe, und der Unterschied zu `|mittel(valenz)|`."""

    def test_gemischte_faeden_tragen_die_volle_valenz(self) -> None:
        """Zwei Freude, zwei Trauer: jeder Faden traegt |±1| = 1."""
        ergebnis = _lauf(faden_zahl=4, mit_salienz=4, salienz_mittel=0.8,
                         ohne_valenz=0)
        self.assertAlmostEqual(
            ergebnis["valenz_mittel"], 1.0, places=6,
            msg="Die Gegensaetze haben sich aufgehoben — viele Faeden fuehren "
                "damit zu einer Nullung statt zu einer Intensivierung",
        )

    def test_nur_ueberraschung_traegt_kaum_valenz(self) -> None:
        """Sektor 4 steht in der Tabelle nahe null, nicht auf null."""
        ergebnis = _lauf(faden_zahl=4, mit_salienz=4, salienz_mittel=0.8,
                         ohne_valenz=4)
        self.assertLess(ergebnis["valenz_mittel"], 0.2)

    def test_die_haelfte_aus_sektor_vier_senkt_das_mittel(self) -> None:
        voll   = _lauf(faden_zahl=4, mit_salienz=4, salienz_mittel=0.8)
        halb   = _lauf(faden_zahl=4, mit_salienz=4, salienz_mittel=0.8,
                       ohne_valenz=2)
        self.assertLess(halb["valenz_mittel"], voll["valenz_mittel"])
        self.assertGreater(halb["valenz_mittel"], 0.4)

    def test_die_tabelle_unterscheidet_die_staerke_der_faerbung(self) -> None:
        """`begeisterung` 1,00 gegen `neugierig` 0,35 — bis zum 02.09. gleich."""
        stark = _lauf(4, 4, 0.8, emotion="begeisterung")
        mild  = _lauf(4, 4, 0.8, emotion="neugierig")
        self.assertGreater(
            stark["valenz_mittel"], mild["valenz_mittel"],
            "Beide Faerbungen tragen dasselbe — die Groesse steht wieder auf "
            "einer Konstanten, wie vor der Tabelle in 97,05 % der Faelle",
        )


class MehrFaedenSindMehrLadungTest(unittest.TestCase):
    """Mit Saettigung: kein Deckel, aber ein abnehmender Zuwachs."""

    def test_mehr_faeden_heben_die_ladung(self) -> None:
        wenig = _lauf(faden_zahl=2, mit_salienz=2, salienz_mittel=0.8)
        viel  = _lauf(faden_zahl=20, mit_salienz=20, salienz_mittel=0.8)
        self.assertGreater(viel["staerke"], wenig["staerke"])

    def test_der_zuwachs_nimmt_ab(self) -> None:
        """Sonst uebernaehme die Anzahl allein die ganze Groesse."""
        werte = [
            _lauf(n, n, 0.8)["anzahl_term"] for n in (1, 2, 3, 4)
        ]
        zuwaechse = [b - a for a, b in zip(werte, werte[1:], strict=False)]
        self.assertTrue(
            all(b < a for a, b in zip(zuwaechse, zuwaechse[1:], strict=False)),
            f"Der Zuwachs faellt nicht monoton: {zuwaechse}",
        )

    def test_die_saettigung_erreicht_die_eins_nicht(self) -> None:
        self.assertLess(_lauf(1000, 1000, 0.8)["anzahl_term"], 1.0)


class EinStillerStrangVerblasstTest(unittest.TestCase):
    """Ohne Praesenz stuende ein Strang, der vor Jahren endete, dauerhaft hoch."""

    def test_stille_senkt_die_staerke(self) -> None:
        frisch = _lauf(4, 4, 0.8, tage_still=0.0)
        alt    = _lauf(4, 4, 0.8, tage_still=365.0)
        self.assertLess(alt["staerke"], frisch["staerke"])

    def test_er_faellt_nicht_unter_den_boden(self) -> None:
        """Ein Strang wird leiser, nicht abgeschaltet (§7.4)."""
        sehr_alt = _lauf(4, 4, 0.8, tage_still=100000.0)
        self.assertGreaterEqual(
            sehr_alt["praesenz"], PRAEGUNG_PRAESENZ_BODEN * 0.999,
            "Die Praesenz ist unter ihren Boden gefallen",
        )

    def test_ohne_stille_steht_die_praesenz_auf_eins(self) -> None:
        self.assertAlmostEqual(_lauf(4, 4, 0.8)["praesenz"], 1.0, places=6)


class DerBerichtTraegtDieTeileTest(unittest.TestCase):
    """Ohne sie ist nicht zu sehen, welcher Eingang die Zahl gemacht hat."""

    def test_alle_teile_stehen_im_ergebnis(self) -> None:
        ergebnis = _lauf(4, 3, 0.8, ohne_valenz=1, tage_still=5.0)
        for feld in ("staerke", "salienz_mittel", "valenz_mittel",
                     "anzahl_term", "praesenz", "faden_zahl",
                     "ohne_salienz", "tage_still"):
            self.assertIn(feld, ergebnis, f"'{feld}' fehlt im Bericht")

    def test_faeden_ohne_salienz_werden_gezaehlt(self) -> None:
        ergebnis = _lauf(faden_zahl=4, mit_salienz=1, salienz_mittel=0.9)
        self.assertEqual(
            ergebnis["ohne_salienz"], 3,
            "Drei Faeden ohne Salienz sind nicht als solche ausgewiesen — das "
            "Mittel saehe aus wie eines ueber alle vier",
        )

    def test_ein_strang_ohne_faeden_ergibt_nichts(self) -> None:
        self.assertIsNone(_lauf(faden_zahl=0, mit_salienz=0, salienz_mittel=0.0))

    def test_eine_unbrauchbare_kennung_faellt_aus(self) -> None:
        self.assertIsNone(strang_staerke("postgresql://nachgebildet", 0))


class DieVerdrahtungDerLadungTest(unittest.TestCase):
    """Vierter Fall derselben Klasse waere sie sonst."""

    def test_der_tageslauf_legt_die_ladung_neben_die_richtung(self) -> None:
        import importlib
        modul = importlib.import_module(AGENT_MODUL)

        straenge = [{"id": 5, "user_id": "u", "character_id": "c",
                     "sektor_histogramm": [3, 0, 0, 0, 0, 0, 0, 1]}]
        ladung = {"staerke": 0.42, "salienz_mittel": 0.75, "valenz_mittel": 1.0,
                  "anzahl_term": 0.5, "praesenz": 1.0, "faden_zahl": 4,
                  "ohne_salienz": 0, "tage_still": 0.0}
        with patch(f"{AGENT_MODUL}.db_manager") as datenbank, \
             patch(f"{AGENT_MODUL}.rad_messreihe.reihe_laden", return_value=[]), \
             patch(f"{AGENT_MODUL}.rad_messreihe.rad_zusammenfassen",
                   return_value=None), \
             patch(f"{AGENT_MODUL}.praegung.strang_staerke",
                   return_value=ladung) as gerufen, \
             patch(f"{AGENT_MODUL}.pipeline_log.log_berechnung") as protokoll:
            datenbank.select.return_value = straenge
            modul.SynapsenDecayAgent()._richtungen_protokollieren("r1")

        gerufen.assert_called_once()
        inhalt = protokoll.call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["ladung_staerke"], 0.42)
        self.assertIn(
            "ladung_salienz_mittel", inhalt,
            "Die Teile der Ladung stehen nicht in derselben Zeile wie die "
            "Summe — im Nachhinein waere nicht zu sehen, was sie gemacht hat",
        )
        self.assertEqual(
            inhalt["strang_id"], 5,
            "Richtung und Ladung stehen nicht in derselben Zeile",
        )


if __name__ == "__main__":
    unittest.main()
