"""Tests: Der Farbton beschreibt den Raum, nicht eine der beiden Seiten.

**Die Absicht stammt nicht aus dem Code, sondern ist gesetzt** (10.09.2026):
Der Raum sagt, wie sich beide aktiv zueinander verhalten — nicht einer aktiv
und der andere passiv. Der `[SITUATION]`-Block soll dem Leser deshalb beide
Haltungen nennen, auch und gerade wenn sie auseinanderfallen.

Was vorher stand, und warum es kein Schoenheitsfehler war: Sieben der 33
Saetze nannten den Nutzer (*„Der Nutzer haelt Abstand"*), gespeist aus
`internal` — also **Novas** Register. `[gemessen 10.09.2026 ueber 1348 Turns]`
1164 (86,3 %) trugen mindestens einen solchen Satz; von den 826 Dynamik-Saetzen
waren **419 (50,7 %)** gegen den am Nutzer gemessenen Wert falsch. Der
haeufigste Einzelfall: 167-mal *„Der Nutzer ist offen und vertraut"* bei
gemessener `distanz`.

Zeuge: Die Erwartung stammt aus dem Modul selbst, nicht aus der Funktion, die
sie erfuellt. `_farbe_dynamik` trug seit jeher den Docstring *„Wie nah sind
wir uns?"* — beidseitig gefragt —, `_farbe_modus` die Regel *„Die Saetze
beschreiben den Raum, nicht den Nutzer"*, und `lage_beschreiben` die Zusage
*„Die Beschreibung adressiert niemanden"*. Drei Stellen, die den Sollzustand
schon nannten, waehrend vier Zeilen dazwischen ihn brachen.

Die Namen je Leser folgen `F-PROMPT-2`: Der Responder spricht den Schauspieler
als `du` an, der Verfasser kennt Person A und Person B, der GV analysiert und
darf den Charakter beim Namen nennen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.farbton import (
    LESER_GV,
    LESER_RESPONDER,
    LESER_VERFASSER,
    _farbe_dynamik,
    _farbe_intent,
    farbton_berechnen,
)
from graph.personality import Emotion, InternalPersonality, Personality


def _state(nova_dynamik: str = "neutral", nutzer_dynamik: str = "neutral",
           nova_intent: str = "smalltalk", nutzer_intent: str = "smalltalk",
           mit_external: bool = True) -> dict:
    """Ein Zustand mit beiden Seiten — oder nur mit Novas."""
    zustand: dict = {
        "internal": InternalPersonality(
            emotion=Emotion(relationship_dynamic=nova_dynamik,
                            intent=nova_intent),
        ),
    }
    if mit_external:
        zustand["external"] = Personality(
            emotion=Emotion(relationship_dynamic=nutzer_dynamik,
                            intent=nutzer_intent),
        )
    return zustand


class BeideSeitenStehenImSatz(unittest.TestCase):
    """Liegen zwei Werte vor, nennt der Satz zwei Seiten."""

    def test_abweichende_haltungen_nennen_beide(self) -> None:
        satz: str = _farbe_dynamik("vertrauen", "distanz", LESER_GV)
        self.assertIn("Nova", satz)
        self.assertIn("der Nutzer", satz)

    def test_der_gemessene_defekt_ist_rot(self) -> None:
        """167-mal stand hier die Haltung Novas als die des Nutzers."""
        satz: str = _farbe_dynamik("vertrauen", "distanz", LESER_GV)
        self.assertNotEqual(satz, "Der Nutzer ist offen und vertraut.")
        # Novas `vertrauen` darf nicht am Nutzer haengen.
        nutzer_teil: str = satz.split("der Nutzer", 1)[1]
        self.assertNotIn("zugewandt", nutzer_teil)
        self.assertIn("Abstand", nutzer_teil)

    def test_gleichstand_wird_ein_zustand_und_nicht_zwei_saetze(self) -> None:
        satz: str = _farbe_dynamik("vertrauen", "vertrauen", LESER_GV)
        self.assertEqual(satz, "Nova und der Nutzer sind offen und zugewandt.")

    def test_gleich_und_verschieden_sagen_nicht_dasselbe(self) -> None:
        self.assertNotEqual(
            _farbe_dynamik("vertrauen", "vertrauen", LESER_GV),
            _farbe_dynamik("vertrauen", "distanz", LESER_GV),
        )

    def test_schweigt_eine_seite_traegt_die_andere_ihren_namen(self) -> None:
        self.assertEqual(_farbe_dynamik("neutral", "distanz", LESER_GV),
                         "Der Nutzer haelt Abstand.")
        self.assertEqual(_farbe_dynamik("vertrauen", "neutral", LESER_GV),
                         "Nova ist offen und zugewandt.")

    def test_schweigen_beide_faellt_kein_satz(self) -> None:
        self.assertEqual(_farbe_dynamik("neutral", "neutral", LESER_GV), "")

    def test_intent_nennt_ebenfalls_beide(self) -> None:
        satz: str = _farbe_intent("knowledge", "personal", LESER_GV)
        self.assertIn("Nova verfolgt", satz)
        self.assertIn("der Nutzer bringt", satz)


class DieNamenGehoerenDemLeser(unittest.TestCase):
    """`F-PROMPT-2`: ein Block mit mehreren Lesern traegt die Namen je Leser."""

    def test_responder_spricht_den_schauspieler_an(self) -> None:
        satz: str = _farbe_dynamik("vertrauen", "distanz", LESER_RESPONDER)
        self.assertTrue(satz.startswith("Du bist"), satz)
        self.assertIn("der Nutzer haelt Abstand", satz)

    def test_responder_beugt_den_gleichstand_auf_ihr(self) -> None:
        self.assertEqual(_farbe_dynamik("distanz", "distanz", LESER_RESPONDER),
                         "Ihr haltet beide Abstand.")

    def test_gv_spricht_ueber_nova_nicht_zu_ihr(self) -> None:
        """Der Analysator spielt den Charakter nicht — kein `du`."""
        for a, b in (("vertrauen", "distanz"), ("vertrauen", "vertrauen"),
                     ("hilfesuchend", "angriff"), ("vertrauen", "neutral")):
            satz: str = _farbe_dynamik(a, b, LESER_GV)
            for anrede in ("Du ", "du ", "dein", "dir ", "dich "):
                self.assertNotIn(anrede, satz, f"{satz!r} traegt {anrede!r}")

    def test_verfasser_kennt_nur_person_a_und_b(self) -> None:
        satz: str = _farbe_dynamik("vertrauen", "distanz", LESER_VERFASSER)
        self.assertIn("Person A", satz)
        self.assertIn("Person B", satz)
        self.assertNotIn("Nova", satz)

    def test_einzelform_bleibt_singular(self) -> None:
        """`Nova sind` — der Fehler, den eine fehlende Tabellenform machte."""
        self.assertIn("Nova ist", _farbe_dynamik("vertrauen", "distanz",
                                                 LESER_GV))

    def test_unbekannter_leser_ist_ein_fehler_kein_rueckfall(self) -> None:
        with self.assertRaises(ValueError):
            _farbe_dynamik("vertrauen", "distanz", "psychologe")


class OhneZweiteSeiteWirdKeineErfunden(unittest.TestCase):
    """Hintergrundagenten haben keinen Turn — sie bekommen die Lage."""

    def test_fehlende_seite_formuliert_akteurslos(self) -> None:
        satz: str = _farbe_dynamik("distanz", None, LESER_GV)
        self.assertEqual(satz, "Abstand liegt im Raum.")
        self.assertNotIn("Nutzer", satz)
        self.assertNotIn("Nova", satz)

    def test_lage_beschreiben_adressiert_niemanden(self) -> None:
        """Die Zusage stand im Docstring, bevor der Code sie einloeste."""
        from ei.farbton import lage_beschreiben
        lage: str = lage_beschreiben(vektor="", emotion="neutral",
                                     arousal=0.5, dynamik="distanz")
        self.assertNotIn("Nutzer", lage)
        self.assertNotIn("Nova", lage)


class AufEinemImpulsGibtEsKeineZweiteMessung(unittest.TestCase):
    """`F-GV-1`: Auf einem Impuls-Turn ist `external` eine Kopie von `internal`.

    Der Wert steht da und ist keine Messung am Gegenueber — er beschreibt Novas
    vorige Antwort. Wer ihn als zweite Seite liest, laesst den Farbton
    *Nova und der Nutzer sind einander zugewandt* sagen und stuetzt das *beide*
    auf zweimal denselben Wert. `[gemessen 10.09.2026]` **81 von 154**
    Impuls-Turns (52,6 %) haetten diesen Paarsatz getragen.
    """

    def test_der_paarsatz_faellt_nicht_aus_einer_kopie(self) -> None:
        zustand: dict = _state(nova_dynamik="vertrauen",
                               nutzer_dynamik="vertrauen")
        zustand["event_payload"] = {"reiz_herkunft": "eigener_impuls"}

        farbton: str = farbton_berechnen(zustand)

        self.assertNotIn("Nova und der Nutzer", farbton)
        self.assertIn("Nova ist offen und zugewandt", farbton)

    def test_derselbe_zustand_ohne_impuls_traegt_den_paarsatz(self) -> None:
        """Der Zwilling: Ohne die Marke ist die Uebereinstimmung gemessen."""
        farbton: str = farbton_berechnen(
            _state(nova_dynamik="vertrauen", nutzer_dynamik="vertrauen")
        )

        self.assertIn("Nova und der Nutzer sind offen und zugewandt", farbton)

    def test_der_impuls_unterdrueckt_auch_den_intent_der_kopie(self) -> None:
        zustand: dict = _state(nova_intent="knowledge",
                               nutzer_intent="knowledge")
        zustand["event_payload"] = {"reiz_herkunft": "eigener_impuls"}

        farbton: str = farbton_berechnen(zustand)

        self.assertNotIn("Nova und der Nutzer", farbton)
        self.assertIn("Nova verfolgt einen Wissenspfad", farbton)

    def test_nicht_gemessen_ist_nicht_dasselbe_wie_keine_zweite_seite(self) -> None:
        """`NICHT_GEMESSEN` nennt Nova, `None` nennt niemanden."""
        zustand: dict = _state(nova_dynamik="distanz", nutzer_dynamik="distanz")
        zustand["event_payload"] = {"reiz_herkunft": "eigener_impuls"}

        mit_gegenueber: str = farbton_berechnen(zustand)
        ohne_gegenueber: str = farbton_berechnen(
            _state(nova_dynamik="distanz", mit_external=False)
        )

        self.assertIn("Nova haelt Abstand", mit_gegenueber)
        self.assertIn("Abstand liegt im Raum", ohne_gegenueber)
        self.assertNotIn("Nova", ohne_gegenueber)


class DerZustandIstVerdrahtet(unittest.TestCase):
    """Dass die Rechnung kann, ist die eine Frage — ob sie gerufen wird, die andere."""

    def test_farbton_liest_die_zweite_seite_aus_external(self) -> None:
        farbton: str = farbton_berechnen(
            _state(nova_dynamik="vertrauen", nutzer_dynamik="distanz")
        )
        self.assertIn("der Nutzer haelt Abstand", farbton)
        self.assertIn("Nova ist offen und zugewandt", farbton)

    def test_ohne_external_bleibt_der_farbton_akteurslos(self) -> None:
        farbton: str = farbton_berechnen(
            _state(nova_dynamik="distanz", mit_external=False)
        )
        self.assertIn("Abstand liegt im Raum", farbton)
        self.assertNotIn("Der Nutzer", farbton)

    def test_der_leser_reicht_bis_in_den_farbton_durch(self) -> None:
        farbton: str = farbton_berechnen(
            _state(nova_dynamik="vertrauen", nutzer_dynamik="distanz"),
            leser=LESER_RESPONDER,
        )
        self.assertIn("Du bist offen und zugewandt", farbton)


if __name__ == "__main__":
    unittest.main()
