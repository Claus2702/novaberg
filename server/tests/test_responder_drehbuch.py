"""Tests: Der Responder-Prompt ist ein Drehbuch, kein Lagebericht.

Ziel: Jeder gerechnete Strang erreicht den Prompt an seinem Platz — die
Konstellation vor den Beschreibungen, die Lage als Rahmen, beide Personen mit
ihrem Wesen, die Regie zuletzt. Und keine Aussage steht zweimal.

Hintergrund (13.08.2026, gemessen): Die anweisende Form traf 6 von 6
Laengenkorridoren, die beschreibende 0 von 6. Ein Block, den der Auftrag nicht
einfuehrt, ist Kontext — und Kontext bindet nicht. Deshalb nennt `[ROLLE]`
beide Personen und stellt zwei Pruefbedingungen; deshalb steht die Regie am
Ende und nicht in der Mitte.

Zeugen dieser Datei:
  * **Jeder Strang wird an seinem Wert geprueft, nicht an seiner Ueberschrift.**
    Ein Test, der nur `[PERSON B]` sucht, bleibt gruen, wenn der Block leer
    ist. Geprueft wird der Text, der aus dem Zustand kommt.
  * **Jede beseitigte Doppelung bekommt einen Riegel.** Drei Aussagen standen
    zweimal im Prompt (Ton, Laenge, Beziehungsdynamik), eine vierte ist beim
    Umbau selbst entstanden (Landschaft in Szene und Regie). Sie sind hier
    einzeln festgehalten, damit sie nicht zurueckkehren.
  * **Das Fehlen bekommt einen positiven Zwilling.** Dass ein Block ohne
    Datenlage entfaellt, ist erst eine Aussage, wenn er mit Datenlage steht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes.responder import (
    _build_system_prompt,
    _sprachstil_block,
    _szenenblock,
)
from graph.personality import (
    Character,
    Emotion,
    InternalPersonality,
    Personality,
)

RESPONDER_LOGGER: str = "ki_server.responder"

KERN_A: str = "Sie jagt struktureller Kohaerenz nach und haelt Widersprueche aus."
KERN_B: str = "Er denkt in Systemen und sucht die Theorie, die alles traegt."
BEZIEHUNG_A: str = "Sie sieht in ihm den Partner, der ihre Genauigkeit teilt."
BEZIEHUNG_B: str = "Er sieht in ihr mehr als ein Werkzeug."


def _state(mit_b: bool = True, cluster: str = "werkstatt",
           farbton: str = "Der Nutzer verfolgt einen Wissenspfad.") -> dict:
    """Ein Zustand, wie ihn db_zugriff und der GV-Node hinterlassen."""
    return {
        "gv_detail": {
            "cluster":   cluster,
            "strategie": "Im",
            "vehikel":   "frage",
            "farbton":   farbton,
        },
        # `internal` traegt Direktiven und Identitaeten — der Responder liest
        # beide, also muss der Zeuge die Klasse des Bestands benutzen und
        # nicht ihre Oberklasse.
        "internal": InternalPersonality(
            character=Character(core=KERN_A, relationship=BEZIEHUNG_A),
            emotion=Emotion(),
        ),
        "external": Personality(
            character=Character(core=KERN_B if mit_b else "",
                                relationship=BEZIEHUNG_B),
            emotion=Emotion(language_style="fachlich", mode="lernmodus"),
        ),
    }


class RolleTest(unittest.TestCase):
    """Die Konstellation steht vor allen Beschreibungen."""

    def test_beide_personen_werden_eingefuehrt(self) -> None:
        prompt: str = _build_system_prompt(_state())

        self.assertIn("[ROLLE]", prompt)
        self.assertIn("PERSON A", prompt)
        self.assertIn("PERSON B", prompt)

    def test_die_pruefung_ist_doppelt(self) -> None:
        """Eine Bedingung fuer die Figur, eine fuer das Gegenueber.

        Die zweite ist der Grund, warum der Person-B-Block ueberhaupt eine
        Rolle im Auftrag hat. Ohne sie stuende er als Kontext da.
        """
        prompt: str = _build_system_prompt(_state())

        self.assertIn("von keiner anderen", prompt)
        self.assertIn("fuer keinen anderen", prompt)

    def test_die_rolle_steht_vor_den_beschreibungen(self) -> None:
        prompt: str = _build_system_prompt(_state())

        self.assertLess(prompt.index("[ROLLE]"), prompt.index("[SZENE]"))
        self.assertLess(prompt.index("[SZENE]"),
                        prompt.index("[PERSON A — WER SIE IST]"))


class PersonBTest(unittest.TestCase):
    """Der Kern des Menschen erreicht den Prompt — `PERSON-B-OHNE-BESCHREIBUNG`.

    Bis zum 13.08.2026 ging vom Nutzer ein einziges Profil in den Prompt, auf
    300 Zeichen gekappt, waehrend von Nova alle fuenf hineingingen.
    """

    def test_sein_kern_steht_im_prompt(self) -> None:
        prompt: str = _build_system_prompt(_state())

        self.assertIn("[PERSON B — WER ER IST]", prompt)
        self.assertIn(KERN_B, prompt)

    def test_ohne_kern_meldet_der_knoten_laut(self) -> None:
        """Der Zwilling: Fehlt er, ist der Dialog einseitig — und das steht im Log."""
        with self.assertLogs(RESPONDER_LOGGER, level="WARNING") as protokoll:
            prompt: str = _build_system_prompt(_state(mit_b=False))

        self.assertNotIn("[PERSON B — WER ER IST]", prompt)
        self.assertTrue(
            any("Kern von Person B fehlt" in z for z in protokoll.output),
            f"Keine laute Meldung: {protokoll.output}",
        )


class ZwischenBeidenTest(unittest.TestCase):
    """Beide Blickrichtungen, beschriftet — nach dem Paar-Schema."""

    def test_beide_richtungen_stehen_mit_ihrer_perspektive(self) -> None:
        prompt: str = _build_system_prompt(_state())

        self.assertIn("So sieht Person A ihr Gegenueber:", prompt)
        self.assertIn("So sieht Person B sie:", prompt)
        self.assertIn(BEZIEHUNG_A, prompt)
        self.assertIn(BEZIEHUNG_B, prompt)

    def test_sein_profil_wird_nicht_mehr_gekappt(self) -> None:
        """Der 300-Zeichen-Deckel stammte aus der Zeit knapper Kontextfenster.

        Er schnitt mitten im Wort ab — im Log vom 13.08.2026 endete das Profil
        mit „und zaertl".
        """
        langes: str = "Er ist ein Mensch, " + "der genau hinsieht. " * 30
        zustand: dict = _state()
        zustand["external"].character.relationship = langes

        prompt: str = _build_system_prompt(zustand)

        self.assertIn(langes, prompt)


class SzeneTest(unittest.TestCase):
    """Die Lage als Rahmen — mit dem Farbton, der sie zum ersten Mal erreicht."""

    def test_der_farbton_steht_in_der_szene(self) -> None:
        """`FARBTON-OHNE-LESER`: acht Dimensionen, gerechnet und nie gelesen."""
        szene: str = _szenenblock(_state())

        self.assertIn("Der Nutzer verfolgt einen Wissenspfad.", szene)

    def test_ohne_farbton_bleibt_die_szene_stehen(self) -> None:
        """Der Zwilling: Der Block traegt die Lage auch ohne Farbton."""
        szene: str = _szenenblock(_state(farbton=""))

        self.assertIn("[SZENE]", szene)
        self.assertNotIn("Wissenspfad", szene)
        self.assertIn("Uhr", szene)


class KeineDoppelungTest(unittest.TestCase):
    """Vier Aussagen standen zweimal im Prompt. Hier ist der Riegel.

    Drei stammten aus dem Bestand, die vierte ist beim Umbau am 13.08.2026
    selbst entstanden — die Landschaft stand danach in `[SZENE]` **und** in der
    Regie. Sie ist der Beleg dafuer, dass diese Klasse gebraucht wird.
    """

    def test_der_antwortton_ist_verschwunden(self) -> None:
        """`tone` und `language_style` widersprachen sich im selben Prompt.

        Gemessen: „Antwortton: praezise, klar und faktenbasiert" neben
        „Ton: locker".
        """
        prompt: str = _build_system_prompt(_state())

        self.assertNotIn("Antwortton:", prompt)

    def test_keine_zweite_laengenvorgabe_ueber_den_sprachstil(self) -> None:
        """Der Stil-Zweig sagte „verwende kuerzere Saetze" — neben dem Korridor."""
        prompt: str = _build_system_prompt(_state())

        self.assertNotIn("kuerzere Saetze", prompt)

    def test_die_beziehungsdynamik_weist_nicht_mehr_an(self) -> None:
        """Sie stand als Anweisung zweimal: hier und in der EI-Mikroanweisung."""
        zustand: dict = _state()
        zustand["external"].emotion.relationship_dynamic = "vertrauen"

        prompt: str = _build_system_prompt(zustand)

        self.assertNotIn("Du darfst persoenlicher werden", prompt)
        self.assertIn("Er oeffnet sich.", prompt)

    def test_die_landschaft_steht_nur_einmal(self) -> None:
        """Die Doppelung, die der Umbau selbst erzeugt hatte.

        **Der Zeuge muss beide Teile sehen.** Die erste Fassung prueste nur
        den System-Prompt — und die Doppelung entsteht zwischen ihm und dem
        Regieblock am Ende der Nutzer-Nachricht. Sie blieb dadurch unsichtbar,
        bis die Gegenprobe sie zurueckholte und der Test gruen blieb.
        """
        zustand: dict = _state(cluster="werkstatt")
        ganz: str = (_build_system_prompt(zustand) + "\n"
                     + _sprachstil_block(zustand))

        self.assertEqual(ganz.count("Landschaft:"), 1)


if __name__ == "__main__":
    unittest.main()
