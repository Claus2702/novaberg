"""Die Zustellung meldet die Belegung der Nutzlast, die sie sendet.

Bis zum 25.08.2026 fuehrte die Log-Zeile eine eigene Belegungstabelle neben der
Nutzlast, und vier ihrer acht Eintraege prueften dieselbe Groesse:
`bool(zustand_internal)` sagt, ob das Traegerobjekt existiert — nicht, ob das
Feld darin belegt ist. Gemessen mit einer frisch angelegten
`InternalPersonality`: Die Zeile meldete **8 von 8**, waehrend
`nova_emotions_vektor` als leerer String beim Client ankam.

Der letzte Zeuge ist der wichtigste: Er haelt die Namensliste gegen die
Schluessel der gebauten Nutzlast. Ein Name, der dort nicht vorkommt, waere
unsichtbar falsch — er wuerde bei jedem Turn als leer gemeldet, und niemand
koennte den Unterschied zu einem echten Ausfall sehen.
"""
import json
import logging
import unittest

from graph.personality import InternalPersonality
from services.event_consumer import GEMESSENE_ZUSTANDSFELDER, _antwort_nutzlast_bauen

VOLLER_ZUSTAND: dict = {
    "response":              "Antworttext",
    "nova_emotions_verlauf": [{"emotion": "ruhig", "arousal": 0.4}],
    "user_intentionen":      ["frage"],
    "momentum":              "steigend",
    "gespraechsvektor":      "nah",
}


def _internal_mit_vektor(vektor: str) -> InternalPersonality:
    person = InternalPersonality()
    person.emotion.emotions_vector = vektor
    return person


class NutzlastBelegungTest(unittest.TestCase):
    """Was die Zeile meldet, ist an der Nutzlast gemessen."""

    def _bauen(self, zustand: dict) -> tuple[dict, str]:
        """Liefert die Nutzlast und die dabei protokollierte Zeile."""
        with self.assertLogs("ki_server.event_consumer", level=logging.INFO) as fang:
            nutzlast = json.loads(_antwort_nutzlast_bauen(zustand, "turn-1", {}, {}))
        zeilen = [z for z in fang.output if "Zustandsfeldern gefuellt" in z]
        self.assertEqual(len(zeilen), 1, "genau eine Belegungszeile erwartet")
        return nutzlast, zeilen[0]

    def test_ein_leeres_feld_wird_namentlich_gemeldet(self) -> None:
        """Der Fall, an dem die alte Fassung 8 von 8 meldete."""
        zustand = dict(VOLLER_ZUSTAND, internal=_internal_mit_vektor(""))
        nutzlast, zeile = self._bauen(zustand)
        self.assertEqual(nutzlast["nova_emotions_vektor"], "")
        self.assertIn("7 von 8", zeile)
        self.assertIn("leer: nova_emotions_vektor", zeile)

    def test_alles_belegt_meldet_acht_von_acht_ohne_leerliste(self) -> None:
        """Der gute Fall traegt keinen Anhang, sonst liest er sich wie ein Befund."""
        zustand = dict(VOLLER_ZUSTAND, internal=_internal_mit_vektor("spirale"))
        _, zeile = self._bauen(zustand)
        self.assertIn("8 von 8", zeile)
        self.assertNotIn("leer:", zeile)

    def test_ohne_traegerobjekt_fallen_vier_felder_gemeinsam(self) -> None:
        """Fehlt `internal`, sind es vier Ausfaelle — und alle vier werden genannt."""
        zustand = dict(VOLLER_ZUSTAND)
        _, zeile = self._bauen(zustand)
        self.assertIn("4 von 8", zeile)
        for feld in ("gespraechs_modus", "intent", "nova_emotions_vektor", "tone"):
            self.assertIn(feld, zeile)

    def test_jedes_gemessene_feld_gibt_es_in_der_nutzlast(self) -> None:
        """Ein Name ohne Gegenstueck waere bei jedem Turn als leer gemeldet."""
        zustand = dict(VOLLER_ZUSTAND, internal=_internal_mit_vektor("spirale"))
        nutzlast, _ = self._bauen(zustand)
        fehlend = [f for f in GEMESSENE_ZUSTANDSFELDER if f not in nutzlast]
        self.assertEqual(
            fehlend, [],
            f"in GEMESSENE_ZUSTANDSFELDER, aber nicht in der Nutzlast: {fehlend}",
        )

    def test_die_zeile_zaehlt_nicht_die_ganze_nutzlast(self) -> None:
        """Die Auswahl ist eine Auswahl — das steht hier, damit es nicht ueberrascht."""
        zustand = dict(VOLLER_ZUSTAND, internal=_internal_mit_vektor("spirale"))
        nutzlast, _ = self._bauen(zustand)
        self.assertGreater(len(nutzlast), len(GEMESSENE_ZUSTANDSFELDER))


if __name__ == "__main__":
    unittest.main()
