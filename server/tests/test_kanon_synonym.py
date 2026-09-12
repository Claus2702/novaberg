"""Tests: Der Kanon-Zug loest eine Uebersetzung auf — und nur eine erlaubte.

Ziel: `to_canonical` zieht seit dem 12.09.2026 eine dritte Stufe — Synonyme und
**Uebersetzungen**. Die beiden Stufen davor fangen Grossschreibung und Umlaute;
eine Uebersetzung ist keine Schreibvariante und fiel deshalb durch.

**Der Anlass ist gemessen** (10.09.2026): Eine Wertelegende im Perzeptions-Prompt
hebt den Modus `kreativ` von 3,3 % auf 36,7 % — und erzeugte in **9 von 30**
Laeufen das englische `creative`. Der Zug fing es nicht; `modus_pruefen` meldete
es, und die Laengen- und Tiefentabellen nahmen ihren Vorgabewert. **Die Legende
allein haette den Modus also gehoben und gleichzeitig einen neuen stillen
Vorgabewert erzeugt.**

Warum die Uebersetzung **nicht** in den Kanon gehoert: Ein englischer Wert im
Kanon passierte jede Pruefung und liefe in die Modus-Tabellen, wo er keinen
Eintrag hat — also in `GV_LAENGE_MODUS_DELTA.get(modus, 0.0)` und damit still in
den Zuschlag von `alltag`. Der Zug loest ihn stattdessen an der Grenze auf.

Zeuge: Die Erwartung stammt aus der Tabelle `MODUS_SYNONYM_MAP` und dem Kanon,
nicht aus dem Code, der sie liest.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from config import MODUS_KANON, MODUS_SYNONYM_MAP
from utils.canon import to_canonical


class UebersetzungWirdAufgeloestTest(unittest.TestCase):
    """Stufe 3 des Zugs — Synonyme und Uebersetzungen."""

    def test_creative_wird_kreativ(self) -> None:
        """Der gemessene Fall: 9 von 30 Laeufen lieferten `creative`."""
        self.assertEqual(
            "kreativ",
            to_canonical("creative", MODUS_KANON, "modus", "test",
                         synonyme=MODUS_SYNONYM_MAP),
        )

    def test_auch_mit_grossschreibung(self) -> None:
        """Stufe 2 und 3 greifen hintereinander, nicht alternativ."""
        self.assertEqual(
            "kreativ",
            to_canonical("Creative", MODUS_KANON, "modus", "test",
                         synonyme=MODUS_SYNONYM_MAP),
        )

    def test_jeder_eintrag_der_tabelle_zeigt_in_den_kanon(self) -> None:
        """Eine Uebersetzung auf einen Wert ausserhalb des Kanons waere wirkungslos.

        Der Zug gibt sie dann nicht zurueck — und der Eintrag sieht aus wie
        eine Abhilfe, die es nicht gibt.
        """
        for fremd, kanonisch in MODUS_SYNONYM_MAP.items():
            with self.subTest(synonym=fremd):
                self.assertIn(kanonisch, MODUS_KANON)

    def test_kein_eintrag_steht_selbst_im_kanon(self) -> None:
        """Ein Synonym, das schon kanonisch ist, wird von Stufe 1 gefangen.

        Es stuende dann wirkungslos in der Tabelle und taeuschte eine
        Uebersetzung vor, die nie stattfindet.
        """
        for fremd in MODUS_SYNONYM_MAP:
            with self.subTest(synonym=fremd):
                self.assertNotIn(fremd, MODUS_KANON)


class OhneTabelleBleibtEsBeimAltenTest(unittest.TestCase):
    """Die Aenderung ist additiv: ohne `synonyme` verhaelt sich der Zug wie vorher."""

    def test_ohne_tabelle_faellt_creative_durch(self) -> None:
        """Die Gegenprobe im Zeugen: derselbe Wert, kein Synonym-Argument."""
        self.assertIsNone(to_canonical("creative", MODUS_KANON, "modus", "test"))

    def test_ein_unbekannter_wert_bleibt_unbekannt(self) -> None:
        """Die Tabelle oeffnet keine Tuer fuer alles andere."""
        self.assertIsNone(
            to_canonical("erfindend", MODUS_KANON, "modus", "test",
                         synonyme=MODUS_SYNONYM_MAP),
        )

    def test_der_kanon_selbst_geht_unveraendert_durch(self) -> None:
        """Stufe 1 bleibt Stufe 1."""
        self.assertEqual(
            "kreativ",
            to_canonical("kreativ", MODUS_KANON, "modus", "test",
                         synonyme=MODUS_SYNONYM_MAP),
        )


if __name__ == "__main__":
    unittest.main()
