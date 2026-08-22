"""Zeugen dafuer, dass der Kern-Prompt keinen Deckel mehr traegt.

**Gemessen, nicht gewaehlt** (11.08.2026). `KERN_HASH_PROMPT` verlangte bis
dahin »ein kompaktes Persoenlichkeitsprofil in 2-5 Saetzen« — eine Vorgabe
aus der Zeit knapper Kontextfenster. Die Gegenprobe fuhr dasselbe Material
zweimal, einmal mit Deckel und einmal ohne, ueber die ganze Kette (Kern
destillieren, dann Rad daraus lesen), drei Laeufe je Fassung und zwei
Personen:

    Fassung          Kern-Zeichen    Faktor    Spanne
    gedeckelt                 667    0.9433    0.2510      (Mehmet)
    offen                    3288    0.9197    0.0630
    gedeckelt                 734    0.8090    0.1040      (Sarah, n=3)
    offen                    2545    0.7940    0.0040      (Sarah, n=2)

**Die Spanne faellt um das Vierfache, der Faktor bleibt** (-0.024). Der
Deckel kauft nichts und kostet Verlaesslichkeit. Zum Vergleich: Das
Eigenrauschen des Rades auf **fester** Quelle liegt bei 0.061 bis 0.080 —
die offene Destillation legt also nichts obendrauf, die gedeckelte das
Vierfache davon.

**Und der Text traegt den Menschen statt eines Urteils ueber ihn.** Der
gedeckelte schreibt »Sein Grundmuster ist pragmatisch-resilient«, der offene
zitiert im Wortlaut. Genau das verlangt derselbe Prompt zwei Absaetze hoeher:
nicht WORUEBER, sondern WIE.

**Zwei harte Grenzen sitzen oberhalb des Prompts**, und ohne sie waere das
Streichen des Deckels ein stiller Ausfall statt einer Aenderung: die Frist
des Aufrufs und der Token-Deckel des Knotens. Ein offener Prompt unter einer
zu knappen Frist liefert **gar nichts**, unter einem zu knappen Token-Deckel
einen mitten im Wort abgeschnittenen Text. Beide Zeugen stehen unten.
"""

import unittest

from agents.charakter.destillation import KERN_HASH_PROMPT, _perspektive_aufloesen
from config import ASSISTANT_USER_ID, get_node_config


class KernOhneDeckelTest(unittest.TestCase):
    """Der Prompt selbst."""

    def test_der_deckel_ist_weg(self) -> None:
        """Rot, sobald »kompakt« oder eine Satzzahl zurueckkehrt."""
        self.assertNotIn("kompaktes", KERN_HASH_PROMPT)
        self.assertNotIn("2-5 Saetzen", KERN_HASH_PROMPT)
        self.assertNotIn("2-5 Sätzen", KERN_HASH_PROMPT)

    def test_der_raum_ist_ausdruecklich_erlaubt(self) -> None:
        """Das Weglassen des Deckels reicht nicht — der Raum wird verlangt.

        Ein Prompt, der nur nicht mehr »kompakt« sagt, laesst dem Modell
        seine Gewohnheit. Die gemessene Fassung sagt ausdruecklich, dass
        nicht verdichtet werden soll, und nennt den Grund: die Wendungen,
        den Ton, das Beilaeufige.
        """
        self.assertIn("Nimm dir den Raum", KERN_HASH_PROMPT)
        self.assertIn("Verdichte nicht", KERN_HASH_PROMPT)

    def test_der_traeger_steht_weiterhin_zweimal_im_offenen_teil(self) -> None:
        """Der Prompt bleibt fuer beide Perspektiven formatierbar.

        `_perspektive_aufloesen` setzt `traeger` je nach Subjekt auf einen
        Eigennamen oder auf »der Nutzer«. Ein Platzhalter, der beim Umbau
        verlorenginge, faellt sonst erst im Lauf auf.

        **Die Formen kommen seit dem 22.08.2026 aus der Funktion selbst**,
        nicht aus einer hier getippten Liste. Eine neu eingesetzte Form
        faellt sonst nicht hier auf, sondern im Destillationslauf.
        """
        gefuellt = KERN_HASH_PROMPT.format(
            eintraege="…", **_perspektive_aufloesen(ASSISTANT_USER_ID),
        )
        self.assertIn("Wesen Novas", gefuellt)
        self.assertNotIn("{traeger}", gefuellt)


class GrenzenUeberDemPromptTest(unittest.TestCase):
    """Frist und Token-Deckel — ohne sie ist der offene Prompt ein Ausfall."""

    def test_der_token_deckel_traegt_den_offenen_text(self) -> None:
        """3288 Zeichen Text plus das Denken des Modells passen nicht in 2048.

        Gemessen: 2310 Token allein fuer das Denken eines Profil-Aufrufs
        (09.08.2026). Der alte Deckel haette den Text abgeschnitten, und ein
        abgeschnittenes Profil sieht aus wie ein Modell, das aufgehoert hat
        zu denken — kein Fehler, keine Meldung.
        """
        self.assertGreaterEqual(
            get_node_config("charakter_hash")["max_output_tokens"], 4096,
            "Der Token-Deckel liegt unter dem gemessenen Bedarf des offenen "
            "Prompts — der Profiltext wird abgeschnitten",
        )

    def test_die_frist_traegt_den_offenen_aufruf(self) -> None:
        """300 s waeren ein Abbruch, kein Profil.

        Gemessen: rund 18 Minuten fuer Kern und Rad zusammen, bei einem
        einzelnen Rad-Aufruf von rund 8 Minuten. Die Frist steht an der
        Aufrufstelle und nicht am Worker, weil `MODEL_BACKGROUND_TIMEOUT_S`
        fuer jeden Hintergrund-Aufrufer gilt und die Recherche eine andere
        Zahl braucht als die Destillation.
        """
        self.assertGreaterEqual(
            get_node_config("charakter_hash")["timeout_s"], 900,
            "Die Frist des Profil-Aufrufs liegt unter dem gemessenen Bedarf "
            "— der Aufruf bricht ab und schreibt kein Profil",
        )


if __name__ == "__main__":
    unittest.main()
