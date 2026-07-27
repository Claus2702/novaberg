"""Tests fuer das Charakter-Rad — Gewichtung der Nutzer-Salienz.

Ziel: Aus zwoelf Speichen-Auspraegungen entsteht ein Faktor zwischen 0.5 und
1.5, jederzeit von Hand nachrechenbar. Ein unvollstaendiges Rad ergibt keinen
halben Faktor, sondern gar keinen.

Herleitung und die drei Beispielcharaktere: novaberg-salienz-berechnung_k.md §5.
Die Zahlen hier sind gegen dieses Dokument geprueft — weichen sie ab, ist eines
von beiden falsch und beides gehoert angesehen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.charakter.destillation import (
    RAD_LEER,
    RAD_MAX,
    RAD_MIN,
    RAD_NABE,
    RAD_ZUG_HOCH,
    RAD_ZUG_RUNTER,
    charakter_rad_destillieren,
    nutzer_gewichtung_berechnen,
)

DESTILLATION_LOGGER: str = "ki_server.agents.charakter.destillation"


def _rad(hoch: dict | None = None, runter: dict | None = None) -> dict:
    """Baut ein vollstaendiges Rad; nicht genannte Speichen stehen auf 0.0."""
    return {
        "hoch":   {name: (hoch or {}).get(name, 0.0)   for name in RAD_ZUG_HOCH},
        "runter": {name: (runter or {}).get(name, 0.0) for name in RAD_ZUG_RUNTER},
    }


class RadGrenzenTest(unittest.TestCase):
    """Volle Auslenkung trifft die Grenzen exakt — die Kappung ist Sicherung."""

    def test_leeres_rad_ergibt_die_nabe(self):
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(RAD_LEER), RAD_NABE, places=9)

    def test_alle_zuwendungs_speichen_treffen_die_obergrenze_exakt(self):
        voll: dict = _rad(hoch={name: 1.0 for name in RAD_ZUG_HOCH})
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(voll), RAD_MAX, places=9)

    def test_alle_abwendungs_speichen_treffen_die_untergrenze_exakt(self):
        voll: dict = _rad(runter={name: 1.0 for name in RAD_ZUG_RUNTER})
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(voll), RAD_MIN, places=9)

    def test_die_zuege_summieren_sich_auf_die_dokumentierten_spannen(self):
        """Wer einen Zug aendert, muss die Spanne mitaendern — sonst trifft die
        volle Auslenkung die Grenze nicht mehr, und die Kappung wird zum
        Formteil statt zur Sicherung."""
        self.assertAlmostEqual(sum(RAD_ZUG_HOCH.values()),   RAD_MAX - RAD_NABE, places=9)
        self.assertAlmostEqual(sum(RAD_ZUG_RUNTER.values()), RAD_NABE - RAD_MIN, places=9)


class RadBeispieleTest(unittest.TestCase):
    """Die drei Charaktere aus dem Konzept, nachgerechnet."""

    def test_die_treu_ergebene(self):
        rad: dict = _rad(hoch={
            "treue": 1.0, "dienst": 1.0, "pflicht": 1.0,
            "aufmerksamkeit": 1.0, "wissbegier": 0.5, "wohlwollen": 1.0,
        })
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(rad), 1.46, places=4)

    def test_die_sachliche(self):
        rad: dict = _rad(
            hoch={"aufmerksamkeit": 0.5, "pflicht": 0.5},
            runter={"distanz": 0.5},
        )
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(rad), 0.98, places=4)

    def test_die_widerspenstige_mit_wissbegier(self):
        """Das Rad ist kein Schieberegler: Ihr Interesse zieht sie nach oben,
        obwohl sie ihn ablehnt."""
        rad: dict = _rad(
            hoch={"wissbegier": 1.0},
            runter={"widerspenstig": 1.0, "gleichgueltig": 1.0,
                    "selbstbezogen": 1.0, "langeweile": 0.5},
        )
        ohne_wissbegier: dict = _rad(
            runter={"widerspenstig": 1.0, "gleichgueltig": 1.0,
                    "selbstbezogen": 1.0, "langeweile": 0.5},
        )
        self.assertAlmostEqual(nutzer_gewichtung_berechnen(rad), 0.655, places=4)
        self.assertGreater(
            nutzer_gewichtung_berechnen(rad),
            nutzer_gewichtung_berechnen(ohne_wissbegier),
        )

    def test_zweimal_rechnen_liefert_bitgleich(self):
        """Reine Funktion — kein Akkumulator, keine Pfadabhaengigkeit."""
        rad: dict = _rad(hoch={"treue": 1.0, "wissbegier": 0.5}, runter={"distanz": 1.0})
        erst: float = nutzer_gewichtung_berechnen(rad)
        self.assertEqual(erst, nutzer_gewichtung_berechnen(rad))
        self.assertEqual(erst, nutzer_gewichtung_berechnen(json.loads(json.dumps(rad))))


class RadValidierungTest(unittest.TestCase):
    """Ein unvollstaendiges Rad ergibt keinen halben Faktor, sondern gar keinen."""

    def test_fehlende_speiche_wird_abgelehnt(self):
        rad: dict = _rad()
        del rad["hoch"]["treue"]
        with self.assertRaises(ValueError) as ctx:
            nutzer_gewichtung_berechnen(rad)
        self.assertIn("treue", str(ctx.exception))

    def test_unbekannte_speiche_wird_abgelehnt(self):
        rad: dict = _rad()
        rad["runter"]["erfunden"] = 1.0
        with self.assertRaises(ValueError) as ctx:
            nutzer_gewichtung_berechnen(rad)
        self.assertIn("erfunden", str(ctx.exception))

    def test_fehlende_seite_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            nutzer_gewichtung_berechnen({"hoch": {n: 0.0 for n in RAD_ZUG_HOCH}})

    def test_nicht_numerische_auspraegung_wird_abgelehnt(self):
        rad: dict = _rad()
        rad["hoch"]["treue"] = "viel"
        with self.assertRaises(ValueError):
            nutzer_gewichtung_berechnen(rad)

    def test_auspraegung_ausserhalb_null_bis_eins_wird_abgelehnt(self):
        rad: dict = _rad()
        rad["hoch"]["treue"] = 2.0
        with self.assertRaises(ValueError):
            nutzer_gewichtung_berechnen(rad)

    def test_kein_dict_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            nutzer_gewichtung_berechnen("kein Rad")


class RadDestillationTest(unittest.TestCase):
    """Der LLM-Weg: Was ankommt, wenn die Antwort nicht taugt."""

    @staticmethod
    def _antwort(text: str):
        return SimpleNamespace(text=text)

    def _destillieren(self, antwort_text: str, profil: str = "Ein Profiltext."):
        with patch(
            "agents.charakter.destillation.model_service.background.submit_sync",
            return_value=self._antwort(antwort_text),
        ):
            return charakter_rad_destillieren(profil, user_id="nova")

    def test_gueltige_antwort_liefert_rad_und_faktor(self):
        """Positiver Zwilling: Ohne ihn bestuenden alle Fehlerpfad-Tests auch
        dann, wenn die Funktion grundsaetzlich None liefert."""
        rad: dict = _rad(hoch={"treue": 1.0, "wohlwollen": 0.5})
        ergebnis = self._destillieren(json.dumps(rad))

        self.assertIsNotNone(ergebnis)
        erhalten, faktor = ergebnis
        self.assertEqual(erhalten, rad)
        self.assertAlmostEqual(faktor, RAD_NABE + 0.16 + 0.03, places=9)

    def test_kein_json_liefert_none_und_eine_fehlerzeile(self):
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as log:
            self.assertIsNone(self._destillieren("Das ist kein JSON."))
        self.assertIn("kein JSON", log.records[-1].getMessage())

    def test_unvollstaendiges_rad_liefert_none_und_eine_fehlerzeile(self):
        rad: dict = _rad()
        del rad["runter"]["distanz"]
        with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as log:
            self.assertIsNone(self._destillieren(json.dumps(rad)))
        self.assertIn("distanz", log.records[-1].getMessage())

    def test_leerer_profiltext_ruft_kein_llm(self):
        """Ohne Profil gibt es nichts zu bewerten — und keinen Grund, ein
        Modell zu fragen."""
        with patch(
            "agents.charakter.destillation.model_service.background.submit_sync",
        ) as ruf:
            with self.assertLogs(DESTILLATION_LOGGER, level="ERROR") as log:
                self.assertIsNone(charakter_rad_destillieren("   ", user_id="nova"))

        self.assertEqual(ruf.call_count, 0)
        self.assertIn("Profiltext leer", log.records[-1].getMessage())


if __name__ == "__main__":
    unittest.main()
