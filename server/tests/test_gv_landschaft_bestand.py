"""Tests: Die Landschaft hinterlaesst einen nachrechenbaren Bestand.

Ziel: Zu jedem Turn steht dauerhaft, aus welchen sechs Achsen seine Landschaft
entstanden ist und gegen welche Grenzen. Ohne das ist die Justierung der
Raumgrenzen (`novaberg-erreichbarkeit_k.md` B4) nicht fahrbar — ihre MESSUNG
ist „dieselbe Entscheidungsfolge vor und nach der Justierung ueber denselben
Bestand", also ein Nachrechnen ueber gespeicherte Eingangsgroessen, und ihre
Gegenprobe verlangt, dass unveraenderte Grenzen exakt dasselbe Ergebnis
liefern.

Hintergrund, gemessen am 08.08.2026: Eine Abfrage ueber **alle** Schluessel
aller `pipeline_log`-Eintraege nach `achse|naehe|tiefe|valenz|energie|richtung|
sektor` kam leer zurueck. Haltbar war nur das Ergebnis — der Cluster in der
`haltungsraum`-Zeile — und vom Weg dorthin genau ein Bit, die Initiative. Die
sechs Achsen standen ausschliesslich im `gv_detail` und damit in einem
Redis-Wert, den der naechste Turn ueberschreibt.

Die Folge war keine Doku-Luecke, sondern ein Preis: Jede Grenzvariante kostete
einen neuen Messlauf — eine Nacht —, in dem sich ausser den Grenzen auch alles
andere geaendert hatte.

Zeuge: Die Erwartung stammt aus `18_NACHVOLLZIEHBARKEIT.md` und aus dem
Praezedenzfall im Bestand — die Initiative schreibt seit Chat 116 Rohwert, Bit
und geltende Skalenfassung in **einer** Zeile, mit der ausdruecklichen
Begruendung, dass ein Rohwert ohne seinen Massstab nach der ersten
Kalibrierung nicht mehr auswertbar ist. Diese Tests uebertragen dieselbe
Forderung auf die uebrigen fuenf Achsen; sie leiten sie nicht aus dem Code ab,
der sie erfuellt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from ei.dreischicht import achsen_fassung
from graph.nodes import gespraechsvektor as gv_modul
from graph.personality import Emotion, Personality

# Was ein Nachrechnen der Grenzen braucht. Von Hand aus der Achsen-Definition
# in `novaberg-gv-strategie_k.md` §3.1 abgeleitet: Fuer jede der sechs Achsen
# muss ablesbar sein, WORAUS ihr Bit entstanden ist — sonst ist eine geaenderte
# Grenze am Bestand nicht nachvollziehbar.
EINGANGSGROESSEN: tuple = (
    "energie_roh",     # E  — Arousal
    "richtung",        # R  — Stimmungsvektor im Klartext
    "naehe_roh",       # N  — Novas Raum
    "valenz_quelle",   # V  — die Emotion, aus der der Plutchik-Sektor faellt
    "tiefe_roh",       # T  — Novas Raum
    "initiative_roh",  # I  — der gemessene Fuehrungswert
)
BITS: tuple = (
    "energie", "richtung_bin", "naehe", "valenz_bin", "tiefe", "initiative",
)


def _zeilen_sammeln(zustand: dict) -> list[dict]:
    """Faehrt den Node und faengt ab, was er ins `pipeline_log` schreiben will.

    Gefangen wird an `log_berechnung`, also an der Grenze zum Speicher — nicht
    an der Funktion, die den Inhalt baut. Ein Test, der den Erzeuger prueft,
    bliebe gruen, wenn der Aufruf wegfaellt.
    """
    zeilen: list[dict] = []

    def fangen(**felder: object) -> None:
        zeilen.append(felder)

    with patch.object(gv_modul, "_hypothese_destillieren",
                      return_value=("Hypothese", {})), \
         patch.object(gv_modul, "log_berechnung", side_effect=fangen):
        gv_modul.gespraechsvektor(zustand)

    return zeilen


def _landschaftszeile(zustand: dict) -> dict:
    """Die eine Zeile mit `schritt='landschaft'`."""
    treffer: list[dict] = [
        z for z in _zeilen_sammeln(zustand)
        if z.get("inhalt", {}).get("schritt") == "landschaft"
    ]
    if len(treffer) != 1:
        meldung: str = (
            f"erwartet: genau eine Landschaftszeile, bekommen: {len(treffer)}"
        )
        raise AssertionError(meldung)
    return treffer[0]


def _turn(**emotionsfelder: str | float) -> dict:
    return {
        "user_id":      "test_gv_bestand",
        "character_id": "test_gv_bestand",
        "turn_id":      "test-turn-bestand",
        "external":     Personality(emotion=Emotion(**emotionsfelder)),
    }


class DieAchsenWerdenHaltbarTest(unittest.TestCase):
    """Jede der sechs Achsen steht mit Bit UND Eingangsgroesse im Bestand."""

    def test_jedes_bit_steht_in_der_zeile(self) -> None:
        """Ohne die Bits ist die Sektorzuordnung nicht nachrechenbar."""
        achsen: dict = _landschaftszeile(_turn())["inhalt"]["achsen"]

        for schluessel in BITS:
            with self.subTest(achse=schluessel):
                self.assertIn(schluessel, achsen)

    def test_jede_achse_traegt_ihre_eingangsgroesse(self) -> None:
        """Ein Bit ohne seine Quelle ueberlebt keine Grenzverschiebung.

        Bei geaenderter Schwelle muss der Rohwert neu binarisiert werden
        koennen. Steht er nicht da, ist der Bestand fuer B4 wertlos — und die
        Valenz ist der Fall, an dem es zuerst auffiel: Sie hat keinen
        Rohwert, sondern faellt ueber den Plutchik-Sektor aus dem
        Emotionsnamen.
        """
        achsen: dict = _landschaftszeile(_turn())["inhalt"]["achsen"]

        for schluessel in EINGANGSGROESSEN:
            with self.subTest(groesse=schluessel):
                self.assertIn(schluessel, achsen)

    def test_das_ergebnis_steht_daneben(self) -> None:
        """Sektor und Landschaft, damit ein Replay sich selbst pruefen kann."""
        inhalt: dict = _landschaftszeile(_turn())["inhalt"]

        self.assertIn("sektor_index", inhalt)
        self.assertIn("sektor_name",  inhalt)
        self.assertIn("cluster",      inhalt)

    def test_der_index_passt_zu_den_bits(self) -> None:
        """Die Gegenprobe des Bestands gegen sich selbst.

        Aus den sechs gespeicherten Bits muss sich der gespeicherte Index
        ergeben. Faellt das auseinander, ist der Bestand nicht nachrechenbar,
        auch wenn beide Felder dastehen.
        """
        inhalt: dict = _landschaftszeile(_turn())["inhalt"]
        achsen: dict = inhalt["achsen"]

        erwartet: int = (
            achsen["energie"] * 32 + achsen["richtung_bin"] * 16
            + achsen["naehe"] * 8 + achsen["valenz_bin"] * 4
            + achsen["tiefe"] * 2 + achsen["initiative"] * 1
        )
        self.assertEqual(erwartet, inhalt["sektor_index"])


class DieGeltendeFassungReistMitTest(unittest.TestCase):
    """Ein Rohwert ohne seinen Massstab ist nach der ersten Justierung stumm."""

    def test_die_grenzen_stehen_in_der_zeile(self) -> None:
        """Sonst ist nicht trennbar, ob Novas Raum sich bewegt hat oder die Grenze."""
        fassung: dict = _landschaftszeile(_turn())["inhalt"]["fassung"]

        for schluessel in ("energie_schwelle", "naehe_schwelle",
                           "tiefe_schwelle", "initiative_schwelle"):
            with self.subTest(grenze=schluessel):
                self.assertIn(schluessel, fassung)

    def test_die_fassung_kommt_aus_einer_quelle(self) -> None:
        """Der Node setzt sie nicht selbst zusammen.

        Zwei Stellen, die dieselbe Fassung bilden, laufen auseinander — und
        zwar unbemerkt, weil beide plausibel aussehen.
        """
        fassung: dict = _landschaftszeile(_turn())["inhalt"]["fassung"]

        self.assertEqual(achsen_fassung(), fassung)

    def test_der_umfang_der_sektortabelle_steht_dabei(self) -> None:
        """Der Umfang der Sektortabelle gehoert zur Fassung.

        Eine geaenderte Zuordnung macht zwei Bestandsteile unvergleichbar,
        auch wenn jede Grenze gleich blieb.
        """
        fassung: dict = _landschaftszeile(_turn())["inhalt"]["fassung"]

        self.assertEqual(64, fassung["sektoren"])


class DerBestandHatKeinenBlindenFleckTest(unittest.TestCase):
    """Auch die Turns ohne Vorausdenken landen im Bestand.

    Ein Bestand, der sie auslaesst, haette genau den Fehler, den B1 am selben
    Tag beseitigt hat — und zwar in der Menge, die B2 als die interessante
    ausgewiesen hat: 82 von 164 Turns mit `distanz`.
    """

    def test_der_skip_schreibt_seine_landschaft_mit(self) -> None:
        """Begruessung und Meta gehoeren in den Bestand wie jeder Turn."""
        inhalt: dict = _landschaftszeile(_turn(intent="meta"))["inhalt"]

        self.assertTrue(inhalt["cluster"])

    def test_die_gerechnete_null_schreibt_ihre_landschaft_mit(self) -> None:
        """Der Weg, auf dem die Ablesung bis heute Vormittag ausfiel."""
        zustand: dict = _turn(
            mode="fachgespraech", relationship_dynamic="distanz",
        )
        inhalt: dict = _landschaftszeile(zustand)["inhalt"]

        self.assertTrue(inhalt["cluster"])

    def test_die_zeile_ist_von_der_initiative_zeile_unterscheidbar(self) -> None:
        """Beide stehen unter demselben Knoten und demselben Turn.

        Ohne die Marke `schritt` zaehlte jede Auswertung, die
        `node='gespraechsvektor'` und `art='berechnung'` filtert, ab heute das
        Doppelte — und es faellt nicht auf, weil beide Zeilen echt sind.
        """
        zeilen: list[dict] = _zeilen_sammeln(_turn())
        marken: list = [z.get("inhalt", {}).get("schritt", "") for z in zeilen]

        self.assertIn("landschaft", marken)
        self.assertEqual(1, marken.count("landschaft"))
        self.assertGreater(len(zeilen), 1)

    def test_ohne_turn_id_wird_nichts_geschrieben(self) -> None:
        """Eine Zeile ohne Turnbezug ist keiner Messung zuzuordnen."""
        zustand: dict = _turn()
        del zustand["turn_id"]

        marken: list = [
            z.get("inhalt", {}).get("schritt", "") for z in _zeilen_sammeln(zustand)
        ]
        self.assertNotIn("landschaft", marken)


if __name__ == "__main__":
    unittest.main()
