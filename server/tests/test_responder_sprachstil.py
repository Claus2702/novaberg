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

    def test_ton_werkzeug_und_leitgedanke(self) -> None:
        block: str = _sprachstil_block(_state())

        self.assertIn("Ton: locker", block)
        self.assertIn("Impuls", block)          # Strategie-Langname
        self.assertIn("als Frage", block)       # Vehikel
        self.assertIn("Leitgedanke: Die Leichtigkeit halten", block)

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
