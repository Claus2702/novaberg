"""Zeuge: das gelesene Material steht mit Kennung im Protokoll, nicht nur als Zahl.

Ziel: Wer spaeter fragt, ob Nova eine Erinnerung hergenommen hat, findet beide
Haelften — die Antwort in der `turn_roh`-Zeile des Dispatchers und die gelesenen
Knoten in der `switch`-Zeile des Enrichers.

**Der Anlass steht im Bestand.** `[gemessen]` 04.09.2026: 1296 Enricher-Zeilen
tragen `lzg_resonanz_count`, 851 davon mit Erinnerungen — und **keine einzige
sagt, welche**. Damit war die Schwelle aus `novaberg-memory-synapsen_k.md`
§7.1a an echten Turns nicht kalibrierbar.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

ENRICHER_MODUL: str = "graph.nodes.enricher"


class DieResonanzTraegtIhreKennungenTest(unittest.TestCase):
    """Die Protokollzeile nennt die Knoten, nicht nur ihre Anzahl."""

    RESONANZ: dict = {
        "anker_anzahl": 3,
        "sprung_tiefe": 1,
        "cluster":      "sachlich",
        "nova_sektor":  "neugierig",
        "erinnerungen": [
            {"knoten_id": 4711, "inhalt": "a", "schale": 0},
            {"knoten_id": 4712, "inhalt": "b", "schale": 1},
        ],
    }

    def _zeile(self, resonanz: dict | None) -> dict:
        """Baut die Protokollzeile so, wie der Enricher sie schreibt."""
        erinnerungen: list = (resonanz or {}).get("erinnerungen", [])
        return {
            "lzg_resonanz_count": len(erinnerungen),
            "lzg_resonanz_ids":   [e.get("knoten_id") for e in erinnerungen],
        }

    def test_die_kennungen_stehen_neben_der_zahl(self) -> None:
        """Beide Felder, und sie sagen dasselbe.

        Die Zahl bleibt, weil Bestandsleser sie auswerten; die Kennungen
        kommen daneben. Ein Feld, das die Zahl ersetzt haette, waere ein
        stiller Bruch fuer jeden, der heute zaehlt.
        """
        zeile: dict = self._zeile(self.RESONANZ)
        self.assertEqual(2, zeile["lzg_resonanz_count"])
        self.assertEqual([4711, 4712], zeile["lzg_resonanz_ids"])

    def test_zahl_und_kennungen_gehen_auf(self) -> None:
        """Eine Laenge, die von der Zahl abweicht, waere ein halber Eintrag."""
        zeile: dict = self._zeile(self.RESONANZ)
        self.assertEqual(
            zeile["lzg_resonanz_count"], len(zeile["lzg_resonanz_ids"]),
            "Zahl und Kennungsliste widersprechen einander",
        )

    def test_ohne_resonanz_bleibt_die_liste_leer(self) -> None:
        """Leer heisst *nichts gelesen* — und nicht *nicht protokolliert*."""
        zeile: dict = self._zeile(None)
        self.assertEqual(0, zeile["lzg_resonanz_count"])
        self.assertEqual([], zeile["lzg_resonanz_ids"])

    def test_der_enricher_schreibt_das_feld(self) -> None:
        """Die Verdrahtung: Steht das Feld auch im Quelltext des Knotens?

        Ein Zeuge auf die Form der Zeile allein pruefte eine Rechnung, die
        dieser Test selbst anstellt. Rot wird er erst, wenn das Feld im
        Erzeuger fehlt — das ist die Frage, die zaehlt.
        """
        import inspect

        from graph.nodes import enricher

        quelle: str = inspect.getsource(enricher)
        self.assertIn(
            "lzg_resonanz_ids", quelle,
            "Der Enricher schreibt die Kennungen nicht — die Protokollzeile "
            "traegt weiterhin nur eine Zahl",
        )

    def test_die_kennungen_stehen_bei_der_zahl(self) -> None:
        """Beide Felder in **derselben** Zeile, sonst sind sie nicht paarbar.

        Stuenden sie in zwei Zeilen, muesste ein Leser sie ueber `turn_id`
        und Zeitstempel zusammenfuehren — und bei zwei Enricher-Laeufen im
        selben Turn ginge das schief.
        """
        import inspect

        from graph.nodes import enricher

        quelle: str = inspect.getsource(enricher)
        i_zahl: int = quelle.index('"lzg_resonanz_count"')
        i_ids:  int = quelle.index('"lzg_resonanz_ids"')
        zwischen: str = quelle[i_zahl:i_ids]
        self.assertNotIn(
            "log_switch(", zwischen,
            "Zwischen Zahl und Kennungen liegt ein weiterer Protokollaufruf — "
            "sie stehen nicht in derselben Zeile",
        )


if __name__ == "__main__":
    unittest.main()
