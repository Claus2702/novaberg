"""Zeugen dafuer, dass der Block sagt, wessen Material er traegt.

**Der Anlass ist gemessen** (22.08.2026). Bis dahin kannte der Enricher-Weg
nur einen Block, und dessen erster Satz lautet *„Es sind fremde
Aufzeichnungen"*. Das stimmt fuer die Unterlagen des Menschen und ist fuer die
Recherchen, die der Hintergrundprozess der Figur selbst ablegt, die Anweisung,
eigenes Material einem anderen zuzuschreiben. Im Betrieb sah das so aus: Auf
die ausdrueckliche Korrektur *„Du recherchierst ja, nicht ich"* antwortete sie
*„die ganze Recherche war dein Werk, nicht meins. Ich habe nur beobachtet."*

**Die Angabe haengt an der Wurzel, nicht an der Datei** (§2.2): Eine Datei hat
keinen Eigentuemer, eine Freigabe schon. `Aufzeichnung.eigentum` erbt sie
ueber `wurzel_id`, wie das Paar.

**Warum die Bloecke verschieden heissen und der eine den anderen nicht
enthaelt:** `[EIGENE FUNDE]` statt `[EIGENE AUFZEICHNUNGEN]`. Der Bestand
zerteilt Prompts an `prompt.split("[AUFZEICHNUNGEN]")`; ein Blockname, der den
anderen als Teilzeichenkette traegt, laesst jede solche Pruefung an der
falschen Stelle schneiden, ohne rot zu werden.
"""

import unittest

import graph.nodes.verfasser as verf_mod
from agents.dateien_index.aufzeichnungen import Aufzeichnung


def _state(**felder) -> dict:
    """Minimaler State, wie der Enricher ihn dem Verfasser uebergibt."""
    basis: dict = {
        "user_id": "meister", "character_id": "nova",
        "memory_context": "", "aufzeichnungen": [],
    }
    basis.update(felder)
    return basis


def _treffer(eigentum: str = "nutzer", thema: str = "Ein Thema") -> Aufzeichnung:
    """Ein Treffer mit gesetzter Eigentumsangabe."""
    return Aufzeichnung(
        fundstelle=f"Ablage/{eigentum}.md", thema=thema,
        zusammenfassung="Ein Auszug.", kosinus=0.42, eigentum=eigentum,
    )


class EigentumWirdVererbtTest(unittest.TestCase):
    """Die Angabe kommt von der Wurzel bis zum Treffer durch."""

    def test_der_vorgabewert_ist_die_sichere_seite(self) -> None:
        """Ohne Angabe gilt fremd — nicht 'ihres'.

        Der teurere Fehler ist, dass sie Fremdes als eigenes ausgibt; eine
        Wurzel, deren Einstufung niemand entschieden hat, darf nicht auf der
        Seite der Figur landen.
        """
        treffer = Aufzeichnung(
            fundstelle="x.md", thema="t", zusammenfassung="z", kosinus=0.5,
        )
        self.assertEqual(treffer.eigentum, "nutzer")


class DerBlockNenntDenEigentuemerTest(unittest.TestCase):
    """Der Zeuge am Text, den das Modell liest."""

    def test_eigenes_material_kommt_als_ihre_arbeit_an(self) -> None:
        """Rot, sobald ein `figur`-Treffer im Fremd-Block landet."""
        block: str = verf_mod._aufzeichnungen_block(
            _state(aufzeichnungen=[_treffer("figur")])
        )
        self.assertIn("[EIGENE FUNDE]", block)
        self.assertNotIn("[AUFZEICHNUNGEN]", block)
        self.assertNotIn("fremde Aufzeichnungen", block)

    def test_fremdes_material_behaelt_seinen_block(self) -> None:
        """Die bestehende Zusicherung bleibt: Unterlagen sind fremd."""
        block: str = verf_mod._aufzeichnungen_block(
            _state(aufzeichnungen=[_treffer("nutzer")])
        )
        self.assertIn("[AUFZEICHNUNGEN]", block)
        self.assertNotIn("[EIGENE FUNDE]", block)
        self.assertIn("fremde Aufzeichnungen", block)

    def test_gemischtes_material_laeuft_in_den_fremdblock(self) -> None:
        """Eine Wurzel, bei der beides liegen kann, traegt keine Zusicherung."""
        block: str = verf_mod._aufzeichnungen_block(
            _state(aufzeichnungen=[_treffer("gemischt")])
        )
        self.assertIn("[AUFZEICHNUNGEN]", block)
        self.assertNotIn("[EIGENE FUNDE]", block)

    def test_beide_sorten_stehen_getrennt(self) -> None:
        """Der eigentliche Zweck: eine Liste unter einer Ueberschrift waere
        fuer die andere Haelfte eine falsche Aussage."""
        block: str = verf_mod._aufzeichnungen_block(_state(aufzeichnungen=[
            _treffer("figur",  thema="Was ich nachgelesen habe"),
            _treffer("nutzer", thema="Was in seinen Unterlagen steht"),
        ]))
        self.assertIn("[EIGENE FUNDE]", block)
        self.assertIn("[AUFZEICHNUNGEN]", block)

        eigen, fremd = block.split("[AUFZEICHNUNGEN]", 1)
        self.assertIn("Was ich nachgelesen habe", eigen)
        self.assertNotIn("Was in seinen Unterlagen steht", eigen)
        self.assertIn("Was in seinen Unterlagen steht", fremd)
        self.assertNotIn("Was ich nachgelesen habe", fremd)

    def test_der_eigenblock_traegt_die_herkunft_ueber_den_uebergang(self) -> None:
        """Ohne diesen Satz liegt beim naechsten Mal eine herkunftslose
        Aussage im Gedaechtnis (§1a.4) — auch bei eigenem Material."""
        block: str = verf_mod._aufzeichnungen_block(
            _state(aufzeichnungen=[_treffer("figur")])
        )
        self.assertIn("nachgesehen", block)
        self.assertIn("recherchiert", block)

    def test_ohne_treffer_kein_block(self) -> None:
        """Ein Turn ohne Dateibezug ist der Normalfall, kein Ausfall."""
        self.assertEqual("", verf_mod._aufzeichnungen_block(_state()))


if __name__ == "__main__":
    unittest.main()
