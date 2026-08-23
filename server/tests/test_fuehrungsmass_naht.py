"""Zeugen ueber die Naht zwischen GV-Knoten und Haltungsstand.

Ziel: Das Fuehrungsmass entsteht im Gespraechsvektor-Knoten und entscheidet
ausserhalb des Graphen — Riegel 2 der Impuls-Zustellung fragt damit, ob Nova
gerade die Initiative hat (`novaberg-eigenzeit_k.md` §2.5). Der Weg dorthin
fuehrt ueber den Haltungsstand.

**Der Defekt sass nicht in einem der beiden Bausteine, sondern zwischen ihnen.**
Bis zum 23.08.2026 legte der Erzeuger das Mass in `gv_detail["initiative"]` ab
und der Leser holte es von `state["initiative"]` — einem Schluessel, den
niemand setzt. Ueber den ganzen Baum gemessen: **ein** Schreiber, **ein**
Leser, zwei verschiedene Ebenen.

**Die Folge war Stillstand, und er ist auf den Tag datierbar.** Der Leser gab
auf jedem Turn `(None, "gv_ohne_lauf")` zurueck, Riegel 2 sperrte seit seinem
Bau am 15.08.2026 immer, und der letzte Impuls-Turn stammt vom **15.08.2026** —
dem Tag desselben Commits.

**Warum acht Tage lang nichts anschlug**, gehoert zur Sache: Der Riegel
schliesst bei Unbekanntem, und das ist richtig so. Ein dauerhaft geschlossener
Riegel sieht deshalb aus wie eine Figur, die gerade nicht zugehen will, und
`gv_ohne_lauf` ist ein vorgesehener Grund, keine Fehlermeldung. **Ein Ausfall,
der sich als gueltige Entscheidung tarnt, hat keinen Melder** — nur einen
Zeugen ueber die Naht.

Die Zusicherungen:

  1. **Was der Erzeuger ablegt, findet der Leser.** Nicht nachgebaut: der Zeuge
     ruft `_gv_detail_bauen` und schickt dessen Ausgabe durch
     `_initiative_aus_state`. Ein Zeuge, der das Dict selbst zusammenstellt,
     prueft seine eigene Vorstellung von der Naht und bleibt gruen, wenn eine
     Seite die Ebene wechselt.
  2. **Die drei Ausfaelle tragen drei Namen.** `gv_ohne_lauf` behauptete, der
     Knoten sei nicht gelaufen — und genau das hat die Untersuchung verzoegert,
     weil derselbe Stand `cluster` aus demselben `gv_detail` trug und das
     Gegenteil belegte.
  3. **Ein Ausfall liefert keine Zahl.** Wer bei fehlendem Mass eine einsetzte,
     gaebe dem Riegel eine Messung, die keine war.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.initiative import Fuehrung
from graph.nodes.gespraechsvektor import Lage, _gv_detail_bauen
from graph.nodes.haltung import _initiative_aus_state

#: Ein Fuehrungsmass, das durchkommen muss. Als Literal, damit es an jeder
#: Stelle wiedererkennbar ist und nicht aus dem Pruefobjekt abgeleitet wird.
MASS: float = 0.37


def _lage(fuehrung: Fuehrung) -> Lage:
    """Eine vollstaendige Lage, wie der Knoten sie vermisst.

    Die Werte neben dem Fuehrungsmass sind gleichgueltig und stehen trotzdem
    da: `_gv_detail_bauen` liest sie alle, und eine halb gefuellte Lage
    pruefte einen Weg, den es im Betrieb nicht gibt.
    """
    return Lage(
        achsen               = {"initiative": 1},
        sektor_index         = 1,
        sektor_name          = "freude",
        cluster              = "foyer",
        fuehrung             = fuehrung,
        versatz_quelle       = "rad",
        farbton              = "warm",
        aufnahmebereitschaft = 0.5,
    )


class DieNahtTraegtTest(unittest.TestCase):
    """Zusicherung 1 — vom echten Erzeuger zum echten Leser."""

    def test_das_gemessene_mass_erreicht_den_leser(self) -> None:
        """Der Fall, der seit dem 15.08.2026 nie eintrat."""
        detail: dict = _gv_detail_bauen(
            _lage(Fuehrung(wert=MASS, rohwert=MASS, versatz=0.0)),
            "gemessen", 0,
        )
        wert, grund = _initiative_aus_state({"gv_detail": detail})

        self.assertEqual(MASS, wert)
        self.assertEqual("", grund, "Ein gelieferter Wert traegt keinen Grund")

    def test_der_erzeuger_legt_es_wirklich_in_gv_detail(self) -> None:
        """Die andere Haelfte der Naht, eigens geprueft.

        Ohne sie waere Zusicherung 1 auch von zwei Seiten erfuellt, die sich
        auf **derselben falschen** Ebene treffen — und der naechste Leser, der
        `gv_detail` erwartet, faende wieder nichts.
        """
        detail: dict = _gv_detail_bauen(
            _lage(Fuehrung(wert=MASS, rohwert=MASS, versatz=0.0)),
            "gemessen", 0,
        )
        self.assertIn("initiative", detail)
        self.assertEqual(MASS, detail["initiative"]["wert"])

    def test_das_mass_auf_der_obersten_ebene_wird_nicht_gelesen(self) -> None:
        """Die Gegenprobe zur Naht: der alte Platz traegt nichts mehr.

        Sie steht hier, weil ein Leser, der **beide** Ebenen versucht, gruen
        waere und den Defekt trotzdem konservierte — die zweite Quelle
        verdeckte, dass die erste leer ist.
        """
        wert, grund = _initiative_aus_state({
            "initiative": {"wert": MASS},
            "gv_detail":  {"cluster": "foyer"},
        })
        self.assertIsNone(wert)
        self.assertEqual("fuehrung_fehlt_im_detail", grund)


class DreiAusfaelleDreiNamenTest(unittest.TestCase):
    """Zusicherungen 2 und 3 — was der Grund sagt, und was er nicht sagt."""

    def test_kein_gv_detail_heisst_der_knoten_lief_nicht(self) -> None:
        """Der einzige Fall, fuer den `gv_ohne_lauf` je gemeint war."""
        wert, grund = _initiative_aus_state({})
        self.assertIsNone(wert)
        self.assertEqual("gv_ohne_lauf", grund)

    def test_gv_detail_ohne_mass_heisst_er_lief_und_liess_es_aus(self) -> None:
        """Der Fall, den `gv_ohne_lauf` bis zum 23.08.2026 falsch benannte.

        Der Stand trug `cluster` aus demselben `gv_detail` und belegte damit,
        dass der Knoten gelaufen war — waehrend der Grund das Gegenteil sagte.
        Ein Grund, der die falsche Ursache nennt, schickt die Untersuchung an
        die falsche Stelle.
        """
        wert, grund = _initiative_aus_state({"gv_detail": {"cluster": "foyer"}})
        self.assertIsNone(wert)
        self.assertEqual("fuehrung_fehlt_im_detail", grund)
        self.assertNotEqual("gv_ohne_lauf", grund)

    def test_ein_mass_ohne_zahl_nennt_die_fehlenden_quellen(self) -> None:
        """Er rechnete und kam nicht durch — die dritte Lage."""
        detail: dict = _gv_detail_bauen(
            _lage(Fuehrung(wert=None, fehlend=["m2", "m1"])),
            "gemessen", 0,
        )
        wert, grund = _initiative_aus_state({"gv_detail": detail})

        self.assertIsNone(wert)
        self.assertIn("masse_fehlen", grund)
        self.assertIn("m1", grund)
        self.assertIn("m2", grund)

    def test_ein_mass_ohne_zahl_und_ohne_liste_heisst_ohne_wert(self) -> None:
        """Die vierte Lage, damit `masse_fehlen` nicht alles einsammelt."""
        detail: dict = _gv_detail_bauen(
            _lage(Fuehrung(wert=None, fehlend=[])), "gemessen", 0,
        )
        _, grund = _initiative_aus_state({"gv_detail": detail})
        self.assertEqual("ohne_wert", grund)

    def test_kein_ausfall_liefert_eine_zahl(self) -> None:
        """Zusicherung 3, ueber alle vier Ausfaelle auf einmal.

        Eine eingesetzte Zahl gaebe Riegel 2 eine Messung, die keine war — und
        weil der Riegel bei Unbekanntem schliesst, waere die Folge nicht
        Stillstand, sondern ein Einwurf ohne Grundlage.
        """
        ausfaelle: list[dict] = [
            {},
            {"gv_detail": {"cluster": "foyer"}},
            {"gv_detail": _gv_detail_bauen(
                _lage(Fuehrung(wert=None, fehlend=["m1"])), "gemessen", 0)},
            {"gv_detail": _gv_detail_bauen(
                _lage(Fuehrung(wert=None, fehlend=[])), "gemessen", 0)},
        ]
        for zustand in ausfaelle:
            with self.subTest(zustand=sorted(zustand)):
                wert, grund = _initiative_aus_state(zustand)
                self.assertIsNone(wert)
                self.assertNotEqual("", grund, "Ein Ausfall ohne Grund")


if __name__ == "__main__":
    unittest.main()
