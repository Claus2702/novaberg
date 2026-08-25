"""Zeugen dafuer, dass der Eigentuemer gefragt und nicht geraten wird.

**Der Anlass ist eine Entscheidung, kein Defekt** (22.08.2026). Mit
`dateien_wurzeln.eigentum` bekam die Tabelle einen Vorgabewert `'nutzer'` —
richtig fuer Bestandszeilen, die niemand mehr befragen kann, und falsch fuer
den Gespraechsweg: Dort steht der Mensch daneben. Einen Wert zu schreiben,
den er nie genannt hat, hiesse seine Freigabe um eine Angabe zu ergaenzen,
die er nicht gemacht hat — und ein geratener Eigentuemer ist genau der
Fehler, gegen den die Spalte gebaut wurde.

**Die Antwort traegt einen Wert, kein Ja oder Nein**, und deshalb hat die
Frage einen eigenen Rueckweg. Der bestehende deutet Zustimmung und Ablehnung
(`_antwort_deuten`); er kann zwischen *deins*, *meins* und *beides* nicht
unterscheiden.

**Gelesen wird aus der Sicht des Antwortenden:** Die Figur fragt, der Mensch
antwortet — *„deins"* meint deshalb **ihres** (`figur`) und *„meins"* seines
(`nutzer`).
"""

import unittest

from agents.dateien_wurzeln import resume as resume_mod
from agents.dateien_wurzeln.crud import EIGENTUM_KANON


def _state(parameter: dict) -> dict:
    """Minimaler State fuer den Rueckweg."""
    return {
        "aufgabe": "egal", "aufgabe_typ": "workflow",
        "agent_name": "dateien_wurzeln",
        "kontext": {"user_id": "meister", "character_id": "nova"},
        "parameter": parameter, "schritte": [],
        "ergebnis": None, "status": "laufend",
        "rueckfrage": None, "fehler": None,
    }


class DerKanonIstGeschlossenTest(unittest.TestCase):
    """Drei Werte, deckungsgleich mit dem CHECK der Schemadatei."""

    def test_der_kanon_traegt_genau_die_drei(self) -> None:
        self.assertEqual(EIGENTUM_KANON, frozenset({"nutzer", "figur", "gemischt"}))


class DieAntwortWirdGedeutetTest(unittest.TestCase):
    """`_eigentum_deuten` — der Wert oder nichts."""

    def test_deins_meint_ihres(self) -> None:
        """Die Figur fragt, der Mensch antwortet."""
        for antwort in ("deins", "das ist deins", "deine Sachen", "gehoert dir"):
            with self.subTest(antwort=antwort):
                self.assertEqual(resume_mod._eigentum_deuten(antwort), "figur")

    def test_meins_meint_seines(self) -> None:
        for antwort in ("meins", "das ist mein Material", "gehoert mir"):
            with self.subTest(antwort=antwort):
                self.assertEqual(resume_mod._eigentum_deuten(antwort), "nutzer")

    def test_beides_meint_gemischt(self) -> None:
        for antwort in ("beides", "gemischt", "von uns beiden", "unser gemeinsames"):
            with self.subTest(antwort=antwort):
                self.assertEqual(resume_mod._eigentum_deuten(antwort), "gemischt")

    def test_beide_seiten_genannt_ist_unklar_und_keine_mischung(self) -> None:
        """*„meins, aber auch deins"* und *„nicht meins, sondern deins"*
        tragen dieselben zwei Treffer und meinen Verschiedenes.
        """
        self.assertEqual(resume_mod._eigentum_deuten("nicht meins, sondern deins"), "")

    def test_ohne_antwort_kein_wert(self) -> None:
        for antwort in ("", "   ", "hm", "weiss nicht"):
            with self.subTest(antwort=antwort):
                self.assertEqual(resume_mod._eigentum_deuten(antwort), "")

    def test_kein_teilwort_treffer(self) -> None:
        """»mein« steckt in »allgemein« und »gemeinsam«.

        Dieselbe Klasse wie am Tor: Dort wurde *„Ja, gerne."* als Ablehnung
        gelesen, weil `"ne"` in `"gerne"` steckt.
        """
        for satz in ("das ist allgemein bekannt", "wir haben das gemeinsam gemacht"):
            with self.subTest(satz=satz):
                self.assertEqual(resume_mod._eigentum_deuten(satz), "")


class DerRueckwegFuehrtNieOhneWertZurAusfuehrungTest(unittest.TestCase):
    """Dieselbe Zusicherung wie am Tor."""

    def _antworten(self, antwort: str) -> dict:
        return resume_mod.resume(_state({
            "action": "create", "pfad": "/x", "frage_art": "eigentum",
            "user_answer": antwort,
            "original_rueckfrage": "Wessen Material liegt dort?",
        }))

    def test_eine_deutbare_antwort_setzt_den_wert_und_laesst_laufen(self) -> None:
        ergebnis = self._antworten("deins")
        self.assertEqual(ergebnis["status"], "laufend")
        self.assertEqual(ergebnis["parameter"]["eigentum"], "figur")
        self.assertEqual(ergebnis["parameter"]["frage_art"], "")

    def test_eine_unklare_antwort_fragt_erneut(self) -> None:
        """Unklarheit fuehrt zur erneuten Frage, nie zur Ausfuehrung."""
        ergebnis = self._antworten("hm, schwer zu sagen")
        self.assertEqual(ergebnis["status"], "rueckfrage")
        self.assertNotIn("eigentum", ergebnis.get("parameter", {}))

    def test_eine_unklarheit_mit_ablehnungswort_beendet_den_vorgang(self) -> None:
        """**Ein Bestandsverhalten, festgehalten statt stillschweigend gedeutet.**.

        *„keine Ahnung"* traegt `keine` und wird von `_antwort_deuten` als
        Ablehnung gelesen — der Vorgang endet, statt dass erneut gefragt
        wird. Fuer das Tor ist das die sichere Seite (es wird nichts
        geschrieben); fuer eine Frage nach einem **Wert** ist es die falsche
        Antwort auf ein *ich weiss es nicht*. Der Fund steht in der
        Fundliste; dieser Zeuge haelt fest, was heute geschieht.
        """
        ergebnis = self._antworten("hm, keine Ahnung")
        self.assertEqual(ergebnis["status"], "dismissed")

    def test_eine_ablehnung_beendet_den_vorgang(self) -> None:
        """Wer »lass es« sagt, will keine Freigabe — nicht einen dritten Wert."""
        ergebnis = self._antworten("nein, lass es")
        self.assertEqual(ergebnis["status"], "dismissed")

    def test_kein_ausgang_fuehrt_ohne_wert_zur_ausfuehrung(self) -> None:
        """Der eigentliche Zeuge: 'laufend' nur mit gesetztem Wert."""
        for antwort in ("", "hm", "schwer zu sagen", "vielleicht", "nicht meins, sondern deins"):
            with self.subTest(antwort=antwort):
                ergebnis = self._antworten(antwort)
                if ergebnis["status"] == "laufend":
                    self.assertIn(
                        ergebnis["parameter"].get("eigentum"), EIGENTUM_KANON,
                        f"{antwort!r} laeuft ohne gueltigen Eigentuemer weiter",
                    )


if __name__ == "__main__":
    unittest.main()
