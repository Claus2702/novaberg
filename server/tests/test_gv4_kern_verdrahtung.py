"""Zeugen: die Kern-Naehe entsteht auf dem Thema — nicht in den Suchen, nicht auf dem Satz.

**Geschichte dieser Datei, weil sie die Aussage traegt.** Bis zum 12.09.2026 (mittags)
war die Charakter-Resonanz fuer alle Kandidaten derselbe Wert: die Naehe des
**Turns** zum Kern — ein globaler Schalter. Die erste Abhilfe rechnete die Naehe
je Kandidat **in den Suchen**, als zweiten Abstandsausdruck ueber dem
Gedaechtnissatz. Diese Datei bezeugte genau das.

**Am selben Abend gemessen: Der Satz traegt den Sprecher.** Nova-Saetze lagen gegen
den Kern bei 0,44–0,53, Nutzer-Saetze bei 0,13–0,24; von 83 Luecken im Prompt
begannen 56 mit *„Nova …"*. Seit `F-GV-2` sind Kandidaten **Themen**, und die
Resonanz entsteht auf dem Thema — dort Median 0,209 gegen 0,200, kein Abstand mehr.

**Die Zusicherungen sind umgedreht, nicht geloescht** (`20_TESTS/zusicherung-umdrehen.md`):
Wo stand *„die Suche rechnet die Kern-Naehe"*, steht jetzt *„sie tut es nicht"*.
Ein Rueckbau auf die Satz-Resonanz macht diese Datei rot.

Die Suchen brauchen Datenbank und Redis; ihre Verdrahtung ist am Quelltext
pruefbar. Die Rechnung auf dem Thema ist zusaetzlich am Verhalten bezeugt, in
`test_gv4_themen.py`.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest

from ei import wissensluecken as wl


class DieLzgSucheLiefertKnotenAusNovasSicht(unittest.TestCase):
    """Die Abfrage holt Themen und keine Kern-Naehe."""

    def _quelle(self) -> str:
        return inspect.getsource(wl.lzg_kandidaten_suchen)

    def test_die_abfrage_rechnet_keine_kern_naehe_mehr(self) -> None:
        """Umgedreht: Stand hier `AS kern_naehe`, waere die Satz-Resonanz zurueck."""
        self.assertNotIn("AS kern_naehe", self._quelle())

    def test_die_suche_nimmt_keinen_kern_mehr(self) -> None:
        """Umgedreht: Der Kern war ein Schluesselwort-Argument; die Suche braucht ihn nicht."""
        self.assertNotIn("kern_embedding", inspect.signature(wl.lzg_kandidaten_suchen).parameters)

    def test_die_abfrage_holt_die_themen(self) -> None:
        self.assertIn("themen", self._quelle().split("FROM lzg_knoten")[0])

    def test_nur_knoten_aus_novas_sicht(self) -> None:
        """Themen der Nutzer-Knoten waeren nach Definition beruehrt."""
        self.assertIn("AND beobachter = 'assistant'", self._quelle())


class DieKzgSucheLiefertEintraegeAusNovasSicht(unittest.TestCase):
    """Ohne Vektor in der Rueckgabe, mit Themen und mit Sprecherfilter."""

    def _quelle(self) -> str:
        return inspect.getsource(wl.kzg_kandidaten_suchen)

    def test_die_rueckgabe_nennt_kein_embedding_mehr(self) -> None:
        """Umgedreht: Das `embedding` kam mit, um den Satz gegen den Kern zu messen."""
        self.assertNotIn('"embedding"', self._quelle())

    def test_die_anzahl_der_rueckgabefelder_stimmt(self) -> None:
        """`RETURN 5` gegen fuenf genannte Felder — RediSearch schneidet still ab."""
        quelle = self._quelle()
        self.assertIn('"RETURN", "5"', quelle)
        for feld in ("inhalt", "salienz", "arousal", "score", "themen"):
            with self.subTest(feld=feld):
                self.assertIn(f'"{feld}"', quelle)

    def test_nur_eintraege_aus_novas_sicht(self) -> None:
        self.assertIn("@beobachter:{{assistant}}", self._quelle())

    def test_die_suche_nimmt_keinen_kern_mehr(self) -> None:
        self.assertNotIn("kern_embedding", inspect.signature(wl.kzg_kandidaten_suchen).parameters)

    def test_die_suche_nimmt_den_nicht_dekodierenden_client(self) -> None:
        """Bleibt: 12.09.2026, 0 Kandidaten bei 3544 Schluesseln, weil ein Blob durch UTF-8 lief."""
        self.assertIn("redis_client_bytes.execute_command", self._quelle())

    def test_der_dekodierende_client_kommt_hier_nicht_vor(self) -> None:
        self.assertNotIn("redis_client.execute_command", self._quelle())


class DieResonanzEntstehtAufDemThema(unittest.TestCase):
    """In `wissensluecken_finden`, nach der Einbettung der Themen."""

    def _quelle(self) -> str:
        return inspect.getsource(wl.wissensluecken_finden)

    def test_der_kern_wird_mit_dem_themenvektor_verglichen(self) -> None:
        self.assertIn('k["charakter_resonanz"] = cosine_similarity(vektor, kern_embedding)', self._quelle())

    def test_der_vektor_ist_der_des_themas(self) -> None:
        quelle = self._quelle()
        self.assertIn('embed_topics([k["konzept"] for k in gefiltert])', quelle)
        self.assertIn('vektor: list[float] = vektoren[k["konzept"]]', quelle)

    def test_die_themen_entstehen_vor_der_einbettung(self) -> None:
        """Die Reihenfolge ist der Bauteil: erst Themen, dann ihre Vektoren, dann die Resonanz."""
        quelle = self._quelle()
        self.assertLess(quelle.index("_topic_candidates(alle_knoten, state)"),
                        quelle.index("embed_topics("))
        self.assertLess(quelle.index("embed_topics("),
                        quelle.index('k["charakter_resonanz"] = cosine_similarity'))

    def test_die_suchen_bekommen_keinen_kern(self) -> None:
        """Umgedreht: Frueher bekamen beide Suchen ihn."""
        self.assertEqual(self._quelle().count("kern_embedding=kern_embedding"), 0)

    def test_die_verteilung_wird_protokolliert(self) -> None:
        """Ohne die Zeile waere die naechste Kalibrierung wieder ein Stellvertreter."""
        self.assertIn('"schritt":   "gv4_kern_resonanz"', self._quelle())


if __name__ == "__main__":
    unittest.main()
