"""Zeugen ueber die Richtung eines Strangs: Annaeherung oder Vermeidung?

Ziel: Zu einem Strang und dem heutigen Charakter-Rad ist ablesbar, ob er Nova
anzieht oder wegdrueckt. Konzept §7.7.

**Die Richtung ist nicht die Valenz, und das ist der ganze Grund fuer diese
Achse.** Zwei negative Praegungen koennen entgegengesetzt zeigen:

    Machtlosigkeit → Macht        negativ,  Annaeherung,  speist Faszination
    Furcht vor der Dunkelheit     negativ,  Vermeidung,   speist sie nicht

Eine Valenzachse allein kann Kriegsgeschichte nicht von Dunkelheit
unterscheiden.

**Sie steht nicht im Bestand.** Ein Strang ist Bestand, das Rad ist Zustand —
es bewegte sich am 31.07.2026 binnen zwei Stunden um 100 %. Eine gespeicherte
Richtung waere die Antwort von gestern auf die Frage von heute.

Vorgabe des Eigentuemers (01.09.2026), aus der die vier Regeln folgen:

    „Auch Aerger und Ekel kann anziehen, aber ein normales Gemuet mit
     Selbsterhaltungsdrang, Pflichtbewusstsein und Verantwortungsgefuehl wird
     sich davor schuetzen wollen und eher vermeiden. Das wilde, furchtlose,
     chaotische, neugierige Wesen wird aber die Konfrontation nicht scheuen.
     Man muesste es am Haltungsrad festmachen. … Starke Neugier ist sicher ein
     Faktor, der immer zieht."

Die Zusicherungen:

  1. **Sektor 8 ueber der Schwelle zieht, ohne das Rad zu fragen** — auch bei
     einem durch und durch schuetzenden Charakter.
  2. **Furcht und Ueberraschung zusammen ziehen** (Awe-Dyade).
  3. **Derselbe Strang, zwei Charaktere, zwei Richtungen** — das ist die
     Aussage der ganzen Achse.
  4. **Ohne Rad kein Urteil**, sondern `unbestimmt`: Ein Vorgabewert waere eine
     Aussage ueber den Charakter, die niemand getroffen hat.
  5. **Das Mass braucht alle acht Speichen** — eines aus sechs saehe aus wie
     eines aus acht.
  6. **Die Reihenfolge der Regeln ist Teil der Aussage.**
  7. **Der Tageslauf ruft die Rechnung** und schreibt sie ins Protokoll.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import (
    PRAEGUNG_SEKTOR8_ZUG,
    PRAEGUNG_SPEICHEN_SCHUETZEND,
    PRAEGUNG_SPEICHEN_WILD,
)
from memory.praegung import konfrontationsmass, strang_richtung

AGENT_MODUL: str = "agents.synapsen_decay.agent"

#: Ein Rad, das jede Speiche auf denselben Wert setzt — die beiden Seiten
#: werden je Fall gesetzt, damit im Zeugen steht, worauf es ankommt.
def _rad(wild: float, schuetzend: float) -> dict[str, float]:
    return ({n: wild for n in PRAEGUNG_SPEICHEN_WILD}
            | {n: schuetzend for n in PRAEGUNG_SPEICHEN_SCHUETZEND})


WILDES_RAD:       dict[str, float] = _rad(0.9, 0.2)   # Mass +0,7
SCHUETZENDES_RAD: dict[str, float] = _rad(0.2, 0.9)   # Mass -0,7


def _histogramm(**sektoren: int) -> list[int]:
    """`_histogramm(s1=3, s8=1)` → [3,0,0,0,0,0,0,1]."""
    h = [0] * 8
    for name, anzahl in sektoren.items():
        h[int(name[1:]) - 1] = anzahl
    return h


class DasKonfrontationsmassTest(unittest.TestCase):
    """Vier wilde Speichen gegen vier schuetzende, aus beiden Raedern."""

    def test_das_wilde_rad_liegt_oben(self) -> None:
        self.assertAlmostEqual(konfrontationsmass(WILDES_RAD), 0.7, places=6)

    def test_das_schuetzende_rad_liegt_unten(self) -> None:
        self.assertAlmostEqual(konfrontationsmass(SCHUETZENDES_RAD), -0.7, places=6)

    def test_eine_fehlende_speiche_macht_das_mass_ungueltig(self) -> None:
        """Ein Mass aus sechs Speichen saehe aus wie eines aus acht."""
        unvollstaendig = dict(WILDES_RAD)
        del unvollstaendig["wissbegier"]
        self.assertIsNone(
            konfrontationsmass(unvollstaendig),
            "Das Mass ist aus den uebrigen Speichen gebildet worden — der "
            "Unterschied waere nirgends ablesbar",
        )

    def test_die_speichen_kommen_aus_beiden_raedern(self) -> None:
        """Wer nur eines liest, sieht die halbe Anlage."""
        namen = set(PRAEGUNG_SPEICHEN_WILD) | set(PRAEGUNG_SPEICHEN_SCHUETZEND)
        self.assertIn("wissbegier", namen, "Zuwendungs-Rad fehlt")
        self.assertIn("eigensinn", namen, "Initiative-Rad fehlt")
        self.assertEqual(len(namen), 8)


class NeugierZiehtImmerTest(unittest.TestCase):
    """Die erste Regel, und sie fragt das Rad nicht."""

    def test_sektor_acht_ueber_der_schwelle_zieht_auch_den_vorsichtigsten(self) -> None:
        # Genau auf der Schwelle: ein Faden Neugier unter vier, macht 0,25.
        richtung, grund = strang_richtung(
            _histogramm(s7=3, s8=1),
            konfrontationsmass(SCHUETZENDES_RAD),
        )
        self.assertEqual(
            richtung, "annaeherung",
            f"Ein Strang mit Neugier ueber {PRAEGUNG_SEKTOR8_ZUG} wurde "
            f"gemieden — die Vorgabe sagt, starke Neugier zieht immer ({grund})",
        )
        self.assertIn("Neugier", grund)

    def test_wenig_neugier_reicht_nicht(self) -> None:
        richtung, _ = strang_richtung(
            _histogramm(s7=99, s8=1), konfrontationsmass(SCHUETZENDES_RAD),
        )
        self.assertEqual(richtung, "vermeidung")


class DieAweDyadeZiehtTest(unittest.TestCase):
    """Der einzige Fall, den das Konzept selbst vorgibt."""

    def test_furcht_und_ueberraschung_zusammen_ziehen(self) -> None:
        richtung, grund = strang_richtung(
            _histogramm(s3=3, s4=2), konfrontationsmass(SCHUETZENDES_RAD),
        )
        self.assertEqual(richtung, "annaeherung", grund)
        self.assertIn("Awe", grund)

    def test_reine_furcht_ohne_ueberraschung_ist_keine_dyade(self) -> None:
        richtung, _ = strang_richtung(
            _histogramm(s3=5), konfrontationsmass(SCHUETZENDES_RAD),
        )
        self.assertEqual(
            richtung, "vermeidung",
            "Reine Furcht-Konzentration ist Vermeidung (§7.7)",
        )


class DerCharakterEntscheidetTest(unittest.TestCase):
    """Die Aussage der ganzen Achse in einem Zeugen."""

    NEGATIV: list[int] = _histogramm(s7=4)   # reiner Aerger

    def test_derselbe_strang_zwei_charaktere_zwei_richtungen(self) -> None:
        wild, grund_wild = strang_richtung(
            self.NEGATIV, konfrontationsmass(WILDES_RAD),
        )
        vorsichtig, grund_vorsichtig = strang_richtung(
            self.NEGATIV, konfrontationsmass(SCHUETZENDES_RAD),
        )

        self.assertEqual(wild, "annaeherung", grund_wild)
        self.assertEqual(vorsichtig, "vermeidung", grund_vorsichtig)

    def test_positiv_ueberwiegt_ohne_rad(self) -> None:
        richtung, _ = strang_richtung(_histogramm(s1=3, s5=1), None)
        self.assertEqual(richtung, "annaeherung")

    def test_ohne_rad_kein_urteil_ueber_einen_negativen_strang(self) -> None:
        richtung, grund = strang_richtung(self.NEGATIV, None)
        self.assertEqual(
            richtung, "unbestimmt",
            "Ein negativer Strang ohne Rad wurde beurteilt — ein Vorgabewert "
            "an dieser Stelle ist eine Aussage ueber den Charakter",
        )
        self.assertIn("kein Rad", grund)

    def test_ein_leerer_strang_ist_unbestimmt(self) -> None:
        self.assertEqual(strang_richtung([0] * 8, 0.5)[0], "unbestimmt")

    def test_der_grund_nennt_die_zahl_nicht_nur_die_regel(self) -> None:
        """11_EVA: Ohne sie ist nicht zu sehen, wie knapp es war."""
        _, grund = strang_richtung(self.NEGATIV, konfrontationsmass(WILDES_RAD))
        self.assertIn("0.7", grund.replace(",", "."))


class DieVerdrahtungDerRichtungTest(unittest.TestCase):
    """Ohne Aufrufer waere die Rechnung der vierte Fall derselben Woche."""

    def test_der_tageslauf_ruft_die_richtungen(self) -> None:
        import importlib
        import inspect

        modul = importlib.import_module(AGENT_MODUL)
        koerper: str = inspect.getsource(modul.SynapsenDecayAgent.invoke)
        self.assertIn(
            "_richtungen_protokollieren", koerper,
            "Die Richtung ist gebaut und wird von nichts gerufen — der Leser "
            "waere der Praegungszug, und der ist nicht gebaut",
        )

    def test_der_lauf_schreibt_je_strang_eine_zeile(self) -> None:
        import importlib
        modul = importlib.import_module(AGENT_MODUL)

        straenge = [
            {"id": 5, "user_id": "u", "character_id": "c",
             "sektor_histogramm": _histogramm(s1=3, s8=1)},
        ]
        with patch(f"{AGENT_MODUL}.db_manager") as datenbank, \
             patch(f"{AGENT_MODUL}.rad_messreihe.reihe_laden", return_value=[]), \
             patch(f"{AGENT_MODUL}.rad_messreihe.rad_zusammenfassen",
                   return_value=WILDES_RAD), \
             patch(f"{AGENT_MODUL}.pipeline_log.log_berechnung") as protokoll:
            datenbank.select.return_value = straenge
            gezaehlt = modul.SynapsenDecayAgent()._richtungen_protokollieren("r1")

        self.assertEqual(gezaehlt, 1)
        protokoll.assert_called_once()
        inhalt = protokoll.call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["schritt"], "strang_richtung")
        self.assertEqual(inhalt["strang_id"], 5)
        self.assertEqual(inhalt["richtung"], "annaeherung")
        self.assertIn(
            "grund", inhalt,
            "Ohne den Grund ist die Zeile eine Behauptung ohne Herleitung",
        )

    def test_das_rad_wird_je_paar_geladen_nicht_je_strang(self) -> None:
        import importlib
        modul = importlib.import_module(AGENT_MODUL)

        straenge = [
            {"id": i, "user_id": "u", "character_id": "c",
             "sektor_histogramm": _histogramm(s1=2)} for i in (1, 2, 3)
        ]
        with patch(f"{AGENT_MODUL}.db_manager") as datenbank, \
             patch(f"{AGENT_MODUL}.rad_messreihe.reihe_laden",
                   return_value=[]) as laden, \
             patch(f"{AGENT_MODUL}.rad_messreihe.rad_zusammenfassen",
                   return_value=WILDES_RAD), \
             patch(f"{AGENT_MODUL}.pipeline_log.log_berechnung"):
            datenbank.select.return_value = straenge
            modul.SynapsenDecayAgent()._richtungen_protokollieren("r1")

        self.assertEqual(
            laden.call_count, 2,
            "Das Rad wird je Strang geladen statt je Paar — dieselbe Abfrage "
            "dreimal, und bei zwei Raedern sechsmal",
        )


if __name__ == "__main__":
    unittest.main()
