"""Zeugen: die Kern-Naehe kommt aus den Suchen — nicht aus einer Zuweisung danach.

Ziel: Seit dem 12.09.2026 tragen die Kandidaten ihre eigene Naehe zum
Charakterkern, und sie entsteht **in** den beiden Suchen: im LZG als zweiter
Abstandsausdruck derselben Abfrage, im KZG aus dem mitgelieferten Vektor. Beides
kostet keinen weiteren Modellaufruf.

**Warum es diese Datei gibt.** Die Zeugen in `test_gv4_qualifikation.py` sehen nur
das Dict, das bei `_qualifizieren` ankommt — sie setzen `charakter_resonanz`
selbst. Wer den SQL-Ausdruck oder das `embedding` in der Redis-Rueckgabe
entfernte, liesse **jeden** davon gruen: Der Filter arbeitete dann wieder als
globaler Schalter, und zwar lautlos, weil `_resonanz_pruefbar` in dem Fall
sauber auf False faellt und das Log *„Resonanz nicht pruefbar"* sagt — eine
Meldung, die aussieht wie ein Cold-Start.

**Das ist die Verdrahtung, nicht der Baustein**
(`20_TESTS/verdrahtung.md`). Sie ist nur am Quelltext pruefbar, solange die
Suchen Datenbank und Redis brauchen; ein Zeuge, der beides nachbaut, pruefte die
Nachbildung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest

from ei import wissensluecken as wl


class DieLzgAbfrageRechnetDieKernNaehe(unittest.TestCase):
    """Der zweite Abstandsausdruck steht in derselben Abfrage."""

    def _quelle(self) -> str:
        return inspect.getsource(wl.lzg_kandidaten_suchen)

    def test_die_abfrage_traegt_einen_zweiten_abstand(self) -> None:
        self.assertIn("AS kern_naehe", self._quelle())

    def test_ohne_kern_bleibt_die_spalte_leer(self) -> None:
        """Kein Vorgabewert: NULL heisst `nicht anwendbar`, 0.0 hiesse `fern`."""
        self.assertIn("IS NULL THEN NULL", self._quelle())

    def test_der_wert_wird_nur_gesetzt_wenn_er_da_ist(self) -> None:
        """Ein fehlendes Feld ist die Auskunft — ein gesetztes 0.0 waere eine Luege."""
        self.assertIn('if kern_naehe is not None:', self._quelle())

    def test_der_kern_ist_ein_schluesselwort_argument(self) -> None:
        """Drei Stellungsargumente waren da; das vierte kam dazu."""
        unterschrift = inspect.signature(wl.lzg_kandidaten_suchen)
        self.assertIn("kern_embedding", unterschrift.parameters)
        self.assertIsNone(unterschrift.parameters["kern_embedding"].default)


class DieKzgSucheHoltDenVektorMit(unittest.TestCase):
    """Ohne `embedding` in der Rueckgabe gibt es nichts zu rechnen."""

    def _quelle(self) -> str:
        return inspect.getsource(wl.kzg_kandidaten_suchen)

    def test_die_rueckgabe_nennt_das_embedding(self) -> None:
        self.assertIn('"embedding"', self._quelle())

    def test_die_anzahl_der_rueckgabefelder_stimmt(self) -> None:
        """`RETURN 5` gegen fuenf genannte Felder — eine 4 liesse das letzte fallen.

        Der Zeuge ist nicht Kosmetik: RediSearch schneidet still ab.
        """
        quelle = self._quelle()
        self.assertIn('"RETURN", "5"', quelle)
        for feld in ("inhalt", "salienz", "arousal", "score", "embedding"):
            with self.subTest(feld=feld):
                self.assertIn(f'"{feld}"', quelle)

    def test_das_embedding_wird_nicht_als_text_gelesen(self) -> None:
        """Ein float32-Blob durch `decode("utf-8")` wirft oder liefert Muell."""
        quelle = self._quelle()
        self.assertIn('if k == "embedding":', quelle)

    def test_der_vektor_wird_aus_den_bytes_gebildet(self) -> None:
        self.assertIn("np.frombuffer(roh, dtype=np.float32)", self._quelle())

    def test_die_suche_nimmt_den_nicht_dekodierenden_client(self) -> None:
        """Der dekodierende Client macht aus der Suche einen leeren Speicher.

        `decode_responses=True` laesst redis-py die ganze Antwort als UTF-8
        lesen; ein float32-Blob bricht das mit
        `'utf-8' codec can't decode byte 0xd0`. Der Abbruch wird gefangen und
        als Warnung protokolliert — die Suche liefert dann **null Kandidaten,
        die aussehen wie ein leeres Kurzzeitgedaechtnis**.

        `[gemessen 12.09.2026]` Genau so ist es beim Bau passiert: Suite gruen,
        alle Zeugen gruen, und die KZG-Haelfte des Lueckenpfades tot. Gefunden
        hat es ein Lauf gegen den echten Bestand — 3544 Schluessel, 10
        Kandidaten ohne den Eingriff, 0 mit ihm.
        """
        self.assertIn("redis_client_bytes.execute_command", self._quelle())

    def test_der_dekodierende_client_kommt_hier_nicht_vor(self) -> None:
        """Die Gegenrichtung: ein Rueckbau auf `redis_client` faellt auf."""
        quelle = self._quelle()
        self.assertNotIn("redis_client.execute_command", quelle)


class DerKernEntstehtVorDenSuchen(unittest.TestCase):
    """Die Reihenfolge **ist** der Bauteil.

    Bis zum 12.09.2026 entstand das Kern-Embedding nach der Suche — und konnte
    deshalb nur mit dem Turn verglichen werden. Stuende es wieder dahinter,
    waere der Rueckbau vollzogen, ohne dass ein anderer Zeuge es merkte.
    """

    def test_das_kern_embedding_steht_vor_den_suchaufrufen(self) -> None:
        quelle = inspect.getsource(wl.wissensluecken_finden)
        kern  = quelle.index("kern_embedding: list[float] | None = None")
        suche = quelle.index("lzg_kandidaten_suchen(")
        self.assertLess(kern, suche)

    def test_beide_suchen_bekommen_ihn(self) -> None:
        quelle = inspect.getsource(wl.wissensluecken_finden)
        self.assertEqual(quelle.count("kern_embedding=kern_embedding"), 2)

    def test_die_verteilung_wird_protokolliert(self) -> None:
        """Ohne die Zeile waere die naechste Kalibrierung wieder ein Stellvertreter."""
        quelle = inspect.getsource(wl.wissensluecken_finden)
        self.assertIn('"schritt":   "gv4_kern_resonanz"', quelle)


if __name__ == "__main__":
    unittest.main()
