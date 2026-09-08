"""Zeugen: Der Messschalter nimmt genau eine Zeile — die mit der Zahl.

Ziel: `UMFANGSREGLER-BINDET-NICHT` (Band A1) verlangt als Pruefform *„dieselbe
Turnreihe desselben Reizes mit und ohne Block"*. Der Schalter, der das
moeglich macht, ist selbst ein Messgeraet — und ein ungeprueftes Messgeraet
misst nichts.

**Was hier schiefgehen kann, und warum es niemand saehe.** Der Arm *ohne
Block* unterscheidet sich vom Arm *mit Block* um genau eine Prompt-Zeile.
Entfernt der Schalter die falsche Zeile — die Haltungswoerter etwa, oder die
Energie —, laeuft die Reihe sauber durch, liefert plausible Zahlen und
beantwortet eine andere Frage als die gestellte. Kein Turn scheitert, kein
Log meldet etwas, und das Ergebnis wandert als Beleg in den Backlog.

Zeugen dieser Datei:
  * **Die Nachbedingung von `regie_zeilen` wird gebunden.** Sie sagt: *„Die
    Reihenfolge ist fest: Umfang, Haltung, Energie — die Zahl zuerst, weil
    sie bindet."* Der Schalter verlaesst sich darauf; verschiebt jemand die
    Reihenfolge, muss ein Zeuge rot werden und nicht eine Messreihe still
    das Falsche vergleichen.
  * **Der Fehlerfall entfernt nichts.** Traegt die erste Zeile die Marke
    nicht, bleibt die Regie unveraendert — lieber ein Arm ohne Unterschied
    als zwei Arme, die sich in etwas anderem unterscheiden als geglaubt.
  * **Beide Seiten des Schluessels stehen auf demselben Wert.** Er ist in
    `api/admin.py` und `graph/nodes/responder.py` doppelt gefuehrt, weil ein
    gemeinsamer Ort die Schichtung durchbrechen wuerde. Ein Zeuge haelt sie
    zusammen — sonst schaltet die API einen Schluessel, den der Responder
    nicht liest, und die Reihe misst zweimal denselben Arm.
  * **Ein unerreichbarer Redis schaltet NICHT ab.** Der Ausfall eines
    Messschalters darf den Betrieb nicht ohne Laengenvorgabe laufen lassen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from api.admin import REGIE_AUS_SCHLUESSEL as SCHLUESSEL_API
from ei.haltung import GROESSEN
from ei.haltungssprache import regie_zeilen
from graph.nodes.responder import (
    REGIE_AUS_SCHLUESSEL as SCHLUESSEL_RESPONDER,
)
from graph.nodes.responder import (
    UMFANGSZEILE_MARKE,
    _ohne_umfangszeile,
    _umfangszeile_abgeschaltet,
)


def haltung_bauen():
    """Eine vollstaendige Haltung, wie `regie_zeilen` sie verlangt.

    Vorbedingung: keine.
    Nachbedingung: Eine `Haltung`, deren `umfang` in der mittleren Spanne
        liegt und deren uebrige Groessen auf ihrem Grundwert stehen — so
        spricht keine von ihnen, und die Regie hat zwei Zeilen.
    """
    from ei.haltung import Groessenwert, Haltung

    werte: dict = {
        name: Groessenwert(
            name=name, art="neigung", grundwert=0.5, modifikation=0.0,
            ergebnis=0.5, ausloeser="", ausserhalb=False,
        )
        for name in GROESSEN
    }
    return Haltung(cluster="werkstatt", werte=werte)


class DieUmfangszeileStehtVorn(unittest.TestCase):
    """Die Nachbedingung, auf die der Schalter sich stuetzt."""

    def test_erste_zeile_traegt_die_marke(self):
        """`regie_zeilen` liefert die Umfangszeile zuerst."""
        zeilen: list[str] = regie_zeilen(haltung_bauen(), 0.5, 200, ())

        self.assertTrue(
            zeilen[0].startswith(UMFANGSZEILE_MARKE),
            f"Die erste Regie-Zeile ist {zeilen[0]!r} und traegt die Marke "
            f"{UMFANGSZEILE_MARKE!r} nicht. Der Messschalter entfernt damit "
            "die falsche Zeile — und die Reihe zu A1 vergleicht zwei Arme, "
            "die sich in etwas anderem unterscheiden als der Laengenvorgabe.",
        )

    def test_die_zahl_steht_in_dieser_zeile(self):
        """Die Umfangszeile ist die einzige mit einem Zeichenkorridor."""
        zeilen: list[str] = regie_zeilen(haltung_bauen(), 0.5, 200, ())

        mit_zeichen: list[str] = [z for z in zeilen if "Zeichen" in z]
        self.assertEqual(
            mit_zeichen, [zeilen[0]],
            "Genau eine Regie-Zeile darf einen Zeichenkorridor tragen. "
            f"Gefunden: {mit_zeichen}",
        )


class DerSchalterNimmtGenauEine(unittest.TestCase):
    """Was `_ohne_umfangszeile` entfernt und was nicht."""

    def test_die_umfangszeile_faellt(self):
        """Die erste Zeile ist weg, die uebrigen stehen unveraendert."""
        regie: list[str] = regie_zeilen(haltung_bauen(), 0.5, 200, ())

        ohne: list[str] = _ohne_umfangszeile(regie)

        self.assertEqual(len(ohne), len(regie) - 1)
        self.assertEqual(ohne, regie[1:], "Der Rest muss unberuehrt bleiben")

    def test_die_energie_bleibt(self):
        """Der Arm ohne Block verliert die Zahl, nicht die halbe Regie."""
        regie: list[str] = regie_zeilen(haltung_bauen(), 0.5, 200, ())

        ohne: list[str] = _ohne_umfangszeile(regie)

        self.assertTrue(
            any(z.startswith("Energie:") for z in ohne),
            "Die Energie-Zeile gehoert nicht zum Umfangsregler und muss in "
            f"beiden Armen stehen. Uebrig: {ohne}",
        )

    def test_fremde_erste_zeile_wird_nicht_entfernt(self):
        """Traegt die erste Zeile die Marke nicht, faellt nichts."""
        fremd: list[str] = ["Energie: ruhig.", "Umfang: 60 bis 175 Zeichen."]

        ohne: list[str] = _ohne_umfangszeile(fremd)

        self.assertEqual(
            ohne, fremd,
            "Bei unerwarteter Reihenfolge darf NICHTS entfernt werden — ein "
            "stiller Griff in die falsche Zeile ist ein Messfehler, den "
            "niemand sieht.",
        )

    def test_leere_regie_ueberlebt(self):
        """Eine leere Liste ist kein Absturz."""
        self.assertEqual(_ohne_umfangszeile([]), [])


class DerSchluesselIstDerselbe(unittest.TestCase):
    """Die API schaltet, was der Responder liest."""

    def test_beide_seiten_gleich(self):
        """Doppelt gefuehrt, aber nicht auseinandergelaufen."""
        self.assertEqual(
            SCHLUESSEL_API, SCHLUESSEL_RESPONDER,
            "Die API schaltet einen Schluessel, den der Responder nicht "
            "liest — die Reihe zu A1 misst dann zweimal denselben Arm und "
            "meldet einen Unterschied von null.",
        )


class EinAusfallSchaltetNichtAb(unittest.TestCase):
    """Ein unerreichbarer Redis laesst die Vorgabe im Prompt."""

    def test_redis_fehler_gibt_false(self):
        """Der Betrieb laeuft nicht versehentlich ohne Laengenvorgabe."""
        with patch(
            "graph.nodes.responder.redis_client.exists",
            side_effect=ConnectionError("Redis weg"),
        ):
            self.assertFalse(
                _umfangszeile_abgeschaltet(),
                "Faellt der Messschalter aus, muss die Umfangszeile STEHEN "
                "bleiben. Ein Ausfall darf nicht wie ein gesetzter Schalter "
                "wirken.",
            )

    def test_gesetzter_schluessel_schaltet_ab(self):
        """Die Gegenprobe: steht der Schluessel, ist die Zeile weg."""
        with patch(
            "graph.nodes.responder.redis_client.exists", return_value=1,
        ):
            self.assertTrue(_umfangszeile_abgeschaltet())


class DieIstLaengeWirdBelegt(unittest.TestCase):
    """Die Ergebnisgroesse haengt nicht mehr am Dispatcher.

    `[gemessen 07.09.2026, 20:43 UTC]` Ein Turn erzeugte 1722 Zeichen; der
    `salienz`-Agent scheiterte danach an seinem eigenen JSON, und der
    Dispatcher meldete *„turn_roh uebersprungen — keine Nova-Antwort"*. Die
    Antwort existierte, ihre Laenge stand nirgends.
    """

    def test_zeile_traegt_die_zeichenzahl(self):
        """Der Beleg entsteht im Responder, nicht im Dispatcher."""
        from graph.nodes.responder import _ergebnislaenge_belegen

        state: dict = {
            "turn_id": "abc123", "response": "x" * 512, "token_total": 130,
            "user_id": "meister", "character_id": "nova",
        }

        with patch("graph.nodes.responder.log_berechnung") as schreiber:
            _ergebnislaenge_belegen(state)

        schreiber.assert_called_once()
        inhalt: dict = schreiber.call_args.kwargs["inhalt"]
        self.assertEqual(inhalt["schritt"], "ergebnis")
        self.assertEqual(
            inhalt["ist_zeichen"], 512,
            "Die Ist-Laenge muss die Zeichenzahl der Antwort sein — sie ist "
            "die Ergebnisgroesse jeder Laengenmessung.",
        )

    def test_ohne_turn_id_wird_nicht_geschrieben(self):
        """Eine Zeile ohne Turnbezug ist keiner Messung zuzuordnen."""
        from graph.nodes.responder import _ergebnislaenge_belegen

        with patch("graph.nodes.responder.log_berechnung") as schreiber:
            _ergebnislaenge_belegen({"response": "x" * 100})

        schreiber.assert_not_called()


if __name__ == "__main__":
    unittest.main()
