"""Zeugen ueber den Praegungszug: wie stark eine Praegung diesen Reiz anhebt.

Ziel: Ein Reiz, der einem Annaeherungs-Strang thematisch nahe liegt, erzeugt
einen Zug ueber 1,0; ein Reiz, der nur zu einem Vermeidungs-Strang passt, laesst
ihn bei genau 1,0. Konzept §10.3.

    praegungszug = 1.0 + PRAEGUNG_ZUG_HUB · max_j( sim_j · gewicht_j · ladung_j )
                   ueber die Straenge desselben Paares

**Verstaerkt nur, daempft nie.** Kein Tor, keine Null — der Grund steht im
Konzept: Ein multiplikatives Tor auf einer Aehnlichkeit hebt die noetige Naehe
unbemerkt an; bei der Ziel-Gravitation ergab Tor 0,40 in allen zwoelf
betrachteten Laeufen `gravitationsterm = 0.0`.

**Die Richtung ist der Torfaktor, nicht die Valenz.** Ein negativer Strang
zieht — *Machtlosigkeit → Macht* ist Annaeherung, Kriegsgeschichte kommt als
Awe-Dyade herein. Vorgabe des Eigentuemers (03.09.2026):

    „Was unter Vermeidung faellt, ist genau das, was wir nicht als Faszination
     wollen. Wir wollen deswegen auch keine Praegung dafuer. Das heisst, wir
     filtern es einfach raus."

`unbestimmt` ist dagegen keine Vermeidung, sondern **Unkenntnis** — ein junges
Paar hat noch kein vollstaendiges Rad — und wiegt `PRAEGUNG_ZUG_UNBESTIMMT`.

Die Zusicherungen:

  1. **Vermeidung traegt nichts bei** — der Zug bleibt bei genau 1,0.
  2. **Annaeherung zieht**, und die Zahl ist von Hand nachrechenbar.
  3. **`unbestimmt` zaehlt halb** — nicht null und nicht voll.
  4. **Nie unter 1,0**, auch bei negativer Kosinusnaehe.
  5. **Nie ueber die Spanne**, durch Konstruktion und ohne Kappung (`F-NAHT-1`).
  6. **Das Maximum, keine Summe** — zwei Straenge ziehen nicht doppelt.
  7. **Die Suche bricht ab, sobald kein Strang mehr gewinnen kann** — exakt,
     nicht genaehert.
  8. **Die Abfrage selbst** sortiert absteigend und grenzt auf das Paar ein.
     Ein Zeuge gegen eine nachgebildete Verbindung ersetzt den Cursor und prueft
     die Rechnung damit auf den Zahlen, die er selbst hineingibt — die Abfrage
     sieht er nicht.
  9. **Der Node ruft die Rechnung** und schreibt sie ins Protokoll — die
     Verdrahtung, nicht die Funktion.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import (
    PRAEGUNG_ZUG_HUB,
    PRAEGUNG_ZUG_SPANNE_OBEN,
    PRAEGUNG_ZUG_UNBESTIMMT,
)
from memory.praegung import praegungszug
from tests.test_praegung_strang import _Cursor, _mit_cursor

NODE_MODUL: str = "graph.nodes.praegung"

#: Ein Histogramm, das Regel 3 auf Annaeherung stellt (dominant positiv).
POSITIV:  list[int] = [3, 0, 0, 0, 0, 0, 0, 0]
#: Negativ dominant, ohne Neugier und ohne Awe-Dyade — hier entscheidet Regel 4.
NEGATIV:  list[int] = [0, 0, 0, 0, 3, 0, 0, 0]

#: Das Konfrontationsmass eines schuetzenden Charakters: Regel 4 → Vermeidung.
SCHUETZEND: float = -0.7


def _lauf(zeilen: list[tuple], ladung: float = 0.5,
          konfrontation: float | None = 0.5) -> tuple[dict | None, _Cursor, list]:
    """Faehrt den Zug gegen eine vorgegebene Strangliste.

    `zeilen` sind `(strang_id, histogramm, naehe)` in der Reihenfolge, in der
    die Abfrage sie liefert — also nach Naehe absteigend.
    """
    cursor = _Cursor([zeilen])
    gerufen: list[int] = []

    def staerke(_url: str, strang_id: int) -> dict:
        gerufen.append(strang_id)
        return {"staerke": ladung}

    with _mit_cursor(cursor), patch("memory.praegung.strang_staerke", staerke):
        ergebnis = praegungszug(
            "postgresql://nachgebildet",
            user_id       = "meister",
            character_id  = "nova",
            reiz_vektor   = [0.1] * 768,
            konfrontation = konfrontation,
        )
    return ergebnis, cursor, gerufen


class DieRichtungIstDasTorTest(unittest.TestCase):
    """Zusicherung 1 bis 3 — wer beitraegt, und mit welchem Gewicht."""

    def test_ein_vermeidungsstrang_traegt_nichts_bei(self) -> None:
        """Genau das, was wir nicht als Faszination wollen."""
        ergebnis, _, gerufen = _lauf(
            [(7, NEGATIV, 0.9)], konfrontation=SCHUETZEND,
        )

        self.assertEqual(
            ergebnis["zug"], 1.0,
            "Ein Strang, von dem Nova wegwill, hebt die Faszination — die "
            "Richtung ist dann kein Tor mehr",
        )
        self.assertEqual(ergebnis["richtung"], None)
        self.assertEqual(
            gerufen, [],
            "Die Ladung eines Vermeidungsstrangs wurde gerechnet, obwohl er "
            "ohnehin nicht beitraegt",
        )

    def test_ein_annaeherungsstrang_zieht_und_die_zahl_ist_nachrechenbar(self) -> None:
        ergebnis, _, _ = _lauf([(7, POSITIV, 0.8)], ladung=0.5)

        self.assertAlmostEqual(
            ergebnis["zug"], 1.0 + PRAEGUNG_ZUG_HUB * 0.8 * 0.5, places=9,
        )
        self.assertEqual(ergebnis["richtung"], "annaeherung")
        self.assertEqual(ergebnis["strang_id"], 7)

    def test_unbestimmt_zaehlt_halb_und_nicht_null(self) -> None:
        """Unkenntnis ist keine Vermeidung — jedes junge Paar hat kein Rad."""
        ohne_rad, _, _ = _lauf([(7, NEGATIV, 0.8)], ladung=0.5, konfrontation=None)
        voll, _, _     = _lauf([(7, POSITIV, 0.8)], ladung=0.5)

        self.assertEqual(ohne_rad["richtung"], "unbestimmt")
        self.assertAlmostEqual(ohne_rad["gewicht"], PRAEGUNG_ZUG_UNBESTIMMT, places=9)
        self.assertAlmostEqual(
            ohne_rad["produkt"], voll["produkt"] * PRAEGUNG_ZUG_UNBESTIMMT, places=9,
            msg="Ein Strang ohne feststellbare Richtung zieht wie einer mit "
                "belegter — oder gar nicht",
        )
        self.assertGreater(ohne_rad["zug"], 1.0)


class DerZugVerstaerktNurTest(unittest.TestCase):
    """Zusicherung 4 und 5 — die beiden Enden der Spanne."""

    def test_eine_negative_naehe_senkt_den_zug_nicht(self) -> None:
        """Ein fernes Thema laesst die Faszination in Ruhe, es senkt sie nicht.

        **Getragen wird das vom Abbruch, nicht von einer Klammer.** `bestes`
        startet bei 0,0, und `sim <= bestes` schliesst jede negative Naehe aus,
        bevor sie gewichtet wird. Eine zusaetzliche `max(0.0, …)` war genau
        deshalb toter Code (Gegenprobe 03.09.2026) — der Zeuge prueft deshalb
        **beides**: die Zahl und dass gar nicht erst gerechnet wurde.
        """
        ergebnis, _, gerufen = _lauf([(7, POSITIV, -0.4)], ladung=1.0)

        self.assertEqual(
            ergebnis["zug"], 1.0,
            "Eine negative Kosinusnaehe zieht ins Minus — der Zug daempft",
        )
        self.assertEqual(ergebnis["gerechnet"], 0)
        self.assertEqual(gerufen, [], "Ein ferner Strang wurde gewichtet")

    def test_ohne_strang_steht_der_zug_auf_eins_mit_grund(self) -> None:
        ergebnis, _, _ = _lauf([])

        self.assertEqual(ergebnis["zug"], 1.0)
        self.assertEqual(
            ergebnis["grund"], "kein Strang",
            "Ein Zug von 1,0 ohne Grund ist von 'kein Strang', 'keine Naehe' "
            "und 'lauter Vermeidung' nicht zu unterscheiden",
        )

    def test_das_obere_ende_ist_genau_die_spanne(self) -> None:
        """Durch Konstruktion, nicht durch Kappung (`F-NAHT-1`)."""
        ergebnis, _, _ = _lauf([(7, POSITIV, 1.0)], ladung=1.0)

        self.assertAlmostEqual(ergebnis["zug"], 1.0 + PRAEGUNG_ZUG_HUB, places=9)
        self.assertAlmostEqual(ergebnis["zug"], PRAEGUNG_ZUG_SPANNE_OBEN, places=9)

    def test_der_hub_ist_aus_der_spanne_abgeleitet_nicht_gesetzt(self) -> None:
        """`F-NAHT-1`: der Abbildungsfaktor wandert mit seiner Quelle mit.

        Ohne diesen Zeugen kann der Hub von der Spanne wegdriften, die er
        benennt — und dann heisst die Konstante `SPANNE_OBEN`, ohne das obere
        Ende zu sein. Die uebrigen Zeugen faenden das nicht: Sie rechnen selbst
        mit `PRAEGUNG_ZUG_HUB` und bleiben bei jedem Wert gruen (Gegenprobe
        03.09.2026).
        """
        self.assertAlmostEqual(
            PRAEGUNG_ZUG_HUB, PRAEGUNG_ZUG_SPANNE_OBEN - 1.0, places=9,
        )


class DasMaximumIstKeineSummeTest(unittest.TestCase):
    """Zusicherung 6 und 7 — es zieht einer, und die Suche weiss wann Schluss ist."""

    def test_zwei_straenge_ziehen_nicht_doppelt(self) -> None:
        ergebnis, _, _ = _lauf(
            [(7, POSITIV, 0.9), (8, POSITIV, 0.8)], ladung=0.5,
        )

        self.assertAlmostEqual(
            ergebnis["zug"], 1.0 + PRAEGUNG_ZUG_HUB * 0.9 * 0.5, places=9,
            msg="Die Straenge sind addiert worden — der Zug ist ein Maximum",
        )
        self.assertEqual(ergebnis["strang_id"], 7)

    def test_die_suche_bricht_ab_sobald_keiner_mehr_gewinnen_kann(self) -> None:
        """`gewicht · ladung` liegt auf [0,1] — ein Strang mit kleinerer Naehe
        als das beste Produkt kann das Maximum nicht mehr heben. Der Abbruch ist
        exakt und keine Naeherung."""
        ergebnis, _, gerufen = _lauf(
            [(7, POSITIV, 0.9), (8, POSITIV, 0.4), (9, POSITIV, 0.2)],
            ladung=1.0,
        )

        self.assertEqual(
            gerufen, [7],
            "Die Ladung ferner Straenge wird gerechnet, obwohl das Maximum "
            "schon feststeht",
        )
        self.assertEqual(ergebnis["gerechnet"], 1)
        self.assertEqual(ergebnis["betrachtet"], 3)

    def test_ein_naeherer_strang_wird_nicht_uebersprungen(self) -> None:
        """Die Gegenprobe zum Abbruch: Bei kleiner Ladung reicht die Naehe des
        ersten nicht, und der zweite muss noch gerechnet werden."""
        _, _, gerufen = _lauf(
            [(7, POSITIV, 0.9), (8, POSITIV, 0.8)], ladung=0.1,
        )

        self.assertEqual(
            gerufen, [7, 8],
            "Der Abbruch hat einen Strang uebersprungen, der noch haette "
            "gewinnen koennen",
        )


class DieAbfrageSelbstTest(unittest.TestCase):
    """Zusicherung 8 — was der nachgebildete Cursor sonst verdeckt.

    Der Abbruch aus Zusicherung 7 ist nur richtig, wenn die Zeilen **absteigend
    nach Naehe** kommen; und ein Strang eines fremden Paares duerfte gar nicht
    erst in der Liste stehen. Beides steht in der Abfrage und in keinem
    Rueckgabewert.
    """

    def test_die_zeilen_kommen_absteigend_nach_naehe(self) -> None:
        _, cursor, _ = _lauf([(7, POSITIV, 0.9)])
        sql = cursor.befehle[0][0]

        self.assertIn("ORDER BY naehe DESC", sql)

    def test_die_abfrage_grenzt_auf_das_paar_und_den_beobachter_ein(self) -> None:
        _, cursor, _ = _lauf([(7, POSITIV, 0.9)])
        sql, args = cursor.befehle[0]

        self.assertIn("user_id = %s AND character_id = %s AND beobachter = %s", sql)
        self.assertEqual(
            args[1:], ("meister", "nova", "assistant"),
            "Der Zug liest Straenge eines fremden Paares oder eines fremden "
            "Schreibers",
        )


class DerNodeRuftDenZugTest(unittest.TestCase):
    """Zusicherung 9 — die Verdrahtung, nicht die Funktion.

    Ein Zeuge auf `praegungszug` allein bliebe gruen, wenn der Node ihn nie
    ruft (`novaberg-lesson_l_zeuge-prueft-die-funktion-nicht-ihre-verwendung.md`).
    """

    ZUSTAND: dict = {
        "user_id": "meister", "character_id": "nova", "turn_id": "t-zug",
        "prompt_embedding": [0.2] * 768,
    }

    def test_der_node_rechnet_den_zug_und_protokolliert_ihn(self) -> None:
        from graph.nodes.praegung import _zug_protokollieren
        geschrieben: list[dict] = []

        with patch(f"{NODE_MODUL}.praegungszug",
                   return_value={"zug": 1.24, "strang_id": 7}) as zug, \
             patch(f"{NODE_MODUL}._konfrontation_des_paares", return_value=0.5), \
             patch(f"{NODE_MODUL}.log_berechnung",
                   side_effect=lambda **kw: geschrieben.append(kw)):
            _zug_protokollieren(dict(self.ZUSTAND), "meister", "nova")

        self.assertEqual(zug.call_count, 1, "Der Node rechnet den Zug nicht")
        self.assertEqual(len(geschrieben), 1)
        inhalt = geschrieben[0]["inhalt"]
        self.assertEqual(inhalt["schritt"], "praegung_zug")
        self.assertEqual(inhalt["zug"], 1.24)

    def test_ohne_reizvektor_steht_kein_zug_da_sondern_ein_grund(self) -> None:
        """„Kein Reiz" ist nicht „kein Strang" — ein Zug von 1,0 verwechselte beides."""
        from graph.nodes.praegung import _zug_protokollieren
        geschrieben: list[dict] = []

        ohne = dict(self.ZUSTAND) | {"prompt_embedding": []}
        with patch(f"{NODE_MODUL}.praegungszug") as zug, \
             patch(f"{NODE_MODUL}.log_berechnung",
                   side_effect=lambda **kw: geschrieben.append(kw)):
            _zug_protokollieren(ohne, "meister", "nova")

        self.assertEqual(zug.call_count, 0)
        inhalt = geschrieben[0]["inhalt"]
        self.assertIsNone(inhalt["zug"])
        self.assertEqual(inhalt["grund"], "kein prompt_embedding")

    def test_das_turn_tor_ruft_den_zug_auch_bei_ablehnung(self) -> None:
        """Ein Turn kann eine Praegung anziehen, ohne selbst eine zu hinterlassen."""
        from graph.nodes import praegung as node
        gerufen: list[tuple] = []

        with patch(f"{NODE_MODUL}._zug_protokollieren",
                   side_effect=lambda *a: gerufen.append(a)), \
             patch(f"{NODE_MODUL}.log_berechnung"):
            node.praegung_pruefen({
                "user_id": "meister", "character_id": "nova",
                "turn_id": "t-zug-tor",
                # Unter der Torschwelle: kein Faden, und trotzdem ein Zug.
                "pending_writes": [
                    {"daten": {"salienz_obj": {"salienz": 0.01,
                                               "emotion": "neugierig"}}},
                ],
                "nova_emotions_verlauf": [{"emotion": "neugierig", "gewicht": 0.01}],
            })

        self.assertEqual(
            len(gerufen), 1,
            "Der Zug haengt am Tor — er gilt aber fuer jeden Turn, nicht nur "
            "fuer die, die einen Faden hinterlassen",
        )


if __name__ == "__main__":
    unittest.main()
