"""Tests: Die Stil-Anweisung steht dort, wo sie gegen den Verlauf ankommt.

Ziel: Der Responder erhält die Angabe, wie er klingen soll, am Ende seiner
Nutzer-Nachricht — hinter dem Gesprächsverlauf und hinter dem aktuellen Prompt.

Hintergrund (Chat 114, gemessen): Alles über das WIE stand im System-Prompt,
unmittelbar vor der Generierung lag der Gesprächsverlauf. Ein Turn:

    Cluster=kissenschlacht · Strategie=Im · Vehikel=frage
    EI-Profil — Stil: locker | Modus: spielerisch
    Antwort: "Diese mathematische Eleganz, mit der du unsere Dynamik als
              Resonanzphänomen beschreibst … vor der thermischen Entropie
              zu schützen."

Jedes Registersignal sagte Kissenschlacht, die Sprache kam aus den rund
8.400 Tokens eigener Prosa im Verlauf — gegen 1.376 Zeichen Gesprächsvektor
im System-Prompt.

Zeugen: Die geforderte Reihenfolge (Verlauf → aktueller Prompt → Sprachstil)
stammt aus der Vorgabe, nicht aus dem Code. Die Cluster-Beschreibung wird
gegen die Tabelle in `ei/dreischicht.py` geprüft, die ihrerseits §5 des
Konzepts abbildet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.dreischicht import CLUSTER_BESCHREIBUNGEN
from graph.nodes.responder import _sprachstil_block
from graph.personality import Emotion, Personality

RESPONDER_LOGGER: str = "ki_server.responder"


def _state(cluster: str = "kissenschlacht", stil: str = "locker") -> dict:
    """Ein State, wie ihn der GV-Node und die Perzeption hinterlassen."""
    return {
        "gv_detail": {
            "cluster":   cluster,
            "strategie": "Im",
            "vehikel":   "frage",
            "impuls":    "Die Leichtigkeit halten, nicht erklaeren.",
        },
        "external": Personality(emotion=Emotion(language_style=stil)),
    }


class TestBlockInhalt(unittest.TestCase):
    """Der Block trägt die Landschaft, den Ton und den Leitgedanken."""

    def test_landschaft_kommt_aus_dem_cluster(self) -> None:
        block: str = _sprachstil_block(_state())

        self.assertIn("Kissenschlacht", block)
        self.assertIn(CLUSTER_BESCHREIBUNGEN["kissenschlacht"], block)

    def test_ton_und_werkzeug(self) -> None:
        """Was den Klang beschreibt, bleibt hier."""
        block: str = _sprachstil_block(_state())

        self.assertIn("Ton: locker", block)
        self.assertIn("Impuls", block)          # Strategie-Langname
        self.assertIn("als Frage", block)       # Vehikel

    def test_kein_leitgedanke_mehr(self) -> None:
        """Der Leitgedanke ist Inhalt und steht seit dem 31.07.2026 beim Verfasser.

        Dieser Block war die **zweite** Tuer: Der GV-Block war schon aus dem
        System-Prompt entfernt, und derselbe Text kam ueber den Sprachstil am
        Ende der Nutzer-Nachricht zurueck. Live beobachtet — der Responder gab
        den Leitgedanken daraufhin woertlich weiter.
        """
        block: str = _sprachstil_block(_state())

        self.assertNotIn("Leitgedanke", block)
        self.assertNotIn("Die Leichtigkeit halten", block)

    def test_fuehrt_hin_statt_zu_verbieten(self) -> None:
        """Die Formulierung ist Vorgabe: beschreiben, nicht untersagen."""
        block: str = _sprachstil_block(_state())

        self.assertIn("loese Dich erstmal von der Art und Weise", block)
        self.assertNotIn("nicht", block.split("Landschaft:")[0].replace(
            "kann in einer ganz anderen", ""))

    def test_ohne_angaben_kein_block(self) -> None:
        """Positiver Zwilling: Ein leerer Block darf nicht erfunden werden."""
        leer: dict = {"gv_detail": {}, "external": Personality()}

        with self.assertLogs(RESPONDER_LOGGER, level="INFO"):
            self.assertEqual(_sprachstil_block(leer), "")

    def test_ohne_cluster_trotzdem_der_ton(self) -> None:
        """Bei uebersprungenem GV-Node bleibt wenigstens das Register."""
        ohne_gv: dict = {
            "gv_detail": {},
            "external": Personality(emotion=Emotion(language_style="locker")),
        }

        block: str = _sprachstil_block(ohne_gv)

        self.assertIn("Ton: locker", block)
        self.assertNotIn("Landschaft:", block)


class TestLageVonGrobNachFein(unittest.TestCase):
    """Dieselbe Lage in drei Aufloesungen, von oben nach unten immer genauer.

    Entschieden am 08.08.2026: Die Landschaft geht in den Prompt, und zwar
    gestaffelt — die grobe Beschreibung oben, die genaue Situation unten, wo
    sie am dichtesten am Generierungspunkt steht.

    Landschaft (1 von 14), Sektor (1 von 64) und Achsen (die sechs Bits, aus
    denen beide gebaut sind) sind **nicht drei Angaben, sondern eine in drei
    Koernungen**. Deshalb prueft dieser Block nicht nur, dass sie da sind,
    sondern dass sie in dieser Reihenfolge stehen.
    """

    @staticmethod
    def _mit_lage() -> dict:
        zustand: dict = _state()
        zustand["gv_detail"].update({
            "sektor_name": "Kitzel",
            "achsen": {
                "energie": 1, "richtung_bin": 1, "naehe": 1,
                "valenz_bin": 1, "tiefe": 0, "initiative": 1,
                "initiative_roh": 0.21,
            },
        })
        return zustand

    def test_die_drei_stufen_stehen_von_grob_nach_fein(self) -> None:
        """Die Reihenfolge ist die Aussage, nicht nur die Anwesenheit."""
        block: str = _sprachstil_block(self._mit_lage())

        self.assertLess(block.index("Landschaft:"), block.index("Genauer:"))
        self.assertLess(block.index("Genauer:"),    block.index("Lage:"))

    def test_die_achsen_stehen_im_klartext(self) -> None:
        """Die feinste Stufe traegt Woerter, keine Bits."""
        block: str = _sprachstil_block(self._mit_lage())

        self.assertIn("viel Energie im Raum", block)
        self.assertIn("ihr steht euch nah", block)
        self.assertIn("flaches Gespraech", block)

    def test_eine_nicht_messbare_initiative_wird_nicht_behauptet(self) -> None:
        """Bit 1 ist bei fehlendem Mass ein Ausfall, keine Aussage.

        `achsen_berechnen` setzt es und meldet das laut. Wer es trotzdem als
        „du treibst" ausschreibt, macht aus dem Ausfall eine Behauptung —
        genau die Klasse, die `22_STILLE_FEHLER.md` §3 verbietet.
        """
        zustand: dict = self._mit_lage()
        zustand["gv_detail"]["achsen"]["initiative_roh"] = None

        block: str = _sprachstil_block(zustand)

        self.assertIn("Lage:", block)
        self.assertNotIn("du treibst", block)
        self.assertNotIn("der Mensch treibt", block)

    def test_der_sektor_wiederholt_die_landschaft_nicht(self) -> None:
        """10 der 64 Sektoren heissen wie ihre Landschaft.

        Dort waere die Zeile eine Wiederholung — sie kostet Kontext und
        traegt nichts.
        """
        zustand: dict = self._mit_lage()
        zustand["gv_detail"]["sektor_name"] = "Kissenschlacht"

        block: str = _sprachstil_block(zustand)

        self.assertIn("Landschaft: Kissenschlacht", block)
        self.assertNotIn("Genauer:", block)

    def test_ein_abweichender_sektor_steht_weiterhin_da(self) -> None:
        """Positiver Zwilling zur Unterdrueckung.

        Ohne ihn koennte die Zeile immer wegfallen und die Zusicherung
        darueber bliebe gruen.
        """
        block: str = _sprachstil_block(self._mit_lage())

        self.assertIn("Genauer: Kitzel", block)


class TestBlockPosition(unittest.TestCase):
    """Die Anweisung muss hinter dem Verlauf stehen, nicht davor.

    Das ist der eigentliche Eingriff: Im System-Prompt hat sie gegen den
    Verlauf verloren. Ein Test auf den Inhalt allein wuerde bestehen, auch
    wenn der Block wieder nach vorn wanderte.
    """

    def test_reihenfolge_verlauf_prompt_sprachstil(self) -> None:
        import inspect

        from graph.nodes import responder as modul

        quelle: str = inspect.getsource(modul.respond)
        pos_verlauf: int = quelle.find("[GESPRAECHSVERLAUF]")
        pos_prompt:  int = quelle.find("[AKTUELLER PROMPT]")
        pos_stil:    int = quelle.find("{sprachstil}")

        self.assertGreater(pos_verlauf, 0)
        self.assertGreater(pos_prompt, pos_verlauf)
        self.assertGreater(pos_stil, pos_prompt)

    def test_auch_ohne_verlauf_angehaengt(self) -> None:
        import inspect

        from graph.nodes import responder as modul

        quelle: str = inspect.getsource(modul.respond)
        self.assertIn("user_prompt + sprachstil", quelle)


if __name__ == "__main__":
    unittest.main()
