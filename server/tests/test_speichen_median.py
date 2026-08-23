"""Zeugen ueber den Median je Speiche — der zweite Wert neben dem Rad.

Ziel: `F-RAD-2` speichert das Rad des **Median-Laufs**, und das ist richtig —
ein gemitteltes Rad erzeugte Auspraegungen, die kein Lauf vergeben hat, und
`Rad x Zuege = Faktor` waere nicht mehr von Hand nachrechenbar.

**Der Preis war nicht benannt:** Der Median-Lauf wird ueber den **Faktor**
gewaehlt, nicht je Speiche. Eine einzelne Speiche kann darin einen Wert tragen,
den die Mehrheit ihrer eigenen Laeufe nicht stuetzt — und nichts sagte es dem
Leser. Gemessen am 19.08.2026 ueber drei Laeufe: beim Initiative-Rad **5 von
10** Speichen, beim Zuwendungsrad **0 von 12**.

Die Zusicherungen:

  1. **Der Median je Speiche ist der Median je Speiche** — an einem Fall mit
     bekannter richtiger Antwort, nicht an einem, den die Funktion selbst
     erzeugt hat.
  2. **Die Abweichungsliste nennt genau die Speichen ohne Mehrheit.** Ohne sie
     sagt das Feld, *dass* es einen zweiten Wert gibt, aber nicht, *wo*.
  3. **Der gemessene Fall vom 19.08.2026 wird wiedererkannt.** `behutsamkeit`
     0,60 gegen Median 0,40, `gespraechsdistanz` 0,10 gegen Median 0,20.
  4. **Einigkeit ergibt eine leere Liste.** Sonst waere Zusicherung 2 auch von
     einer Funktion erfuellt, die immer alles meldet.
  5. **Der Median ueber die leere Menge ist kein Wert, sondern ein Fehler.**
     Ein leeres Feld saehe aus wie Einigkeit.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import textwrap
import unittest

from agents.charakter.destillation import (
    flache_reihe_als_raeder,
    speichen_ohne_mehrheit,
    speichenweise_mediane,
)


def _rad(hoch: dict[str, float], runter: dict[str, float]) -> dict:
    """Ein Rad in der Gestalt, die die Erhebung liefert."""
    return {"hoch": dict(hoch), "runter": dict(runter)}


class MedianJeSpeicheTest(unittest.TestCase):
    """Zusicherung 1 — die Rechnung selbst."""

    def test_drei_laeufe_ergeben_den_mittleren_wert(self) -> None:
        """Die Antwort steht im Test, nicht in der Funktion.

        `folgsamkeit` 0,2 / 0,8 / 0,4 hat den Median 0,4 — sortiert 0,2 0,4 0,8,
        der mittlere. Waere die Funktion ein Mittelwert, stuende hier 0,4667.
        """
        erhebungen: list[dict] = [
            _rad({"folgsamkeit": 0.2}, {"eigensinn": 0.9}),
            _rad({"folgsamkeit": 0.8}, {"eigensinn": 0.1}),
            _rad({"folgsamkeit": 0.4}, {"eigensinn": 0.5}),
        ]
        mediane = speichenweise_mediane(erhebungen)
        self.assertEqual(0.4, mediane["hoch"]["folgsamkeit"])
        self.assertEqual(0.5, mediane["runter"]["eigensinn"])

    def test_bei_gerader_anzahl_der_untere_der_beiden_mittleren(self) -> None:
        """Dieselbe Wahl wie bei der Auswahl des Median-Laufs.

        0,2 / 0,4 / 0,6 / 0,8 — die beiden mittleren sind 0,4 und 0,6, genommen
        wird 0,4. Ein Mittelwert stuende bei 0,5 und waere ein Wert, den kein
        Lauf vergeben hat: genau das, was `F-RAD-2` ausschliesst.
        """
        erhebungen: list[dict] = [
            _rad({"treue": wert}, {}) for wert in (0.2, 0.4, 0.6, 0.8)
        ]
        self.assertEqual(0.4, speichenweise_mediane(erhebungen)["hoch"]["treue"])

    def test_ein_einziger_lauf_ist_sein_eigener_median(self) -> None:
        """Der Randfall, bei dem die Frage keine ist."""
        mediane = speichenweise_mediane([_rad({"pflicht": 0.7}, {})])
        self.assertEqual(0.7, mediane["hoch"]["pflicht"])

    def test_der_median_ueber_nichts_ist_ein_fehler(self) -> None:
        """Zusicherung 5 — ein leeres Feld saehe aus wie Einigkeit."""
        with self.assertRaises(ValueError):
            speichenweise_mediane([])

    def test_raeder_ohne_speichen_sind_ein_fehler(self) -> None:
        """Drei leere Raeder sind keine drei einigen Raeder."""
        with self.assertRaises(ValueError) as fall:
            speichenweise_mediane([_rad({}, {}), _rad({}, {})])
        self.assertIn("keine einzige Speiche", str(fall.exception))


class AbweichungTest(unittest.TestCase):
    """Zusicherungen 2 bis 4 — wo die beiden Werte auseinanderliegen."""

    def test_der_gemessene_fall_vom_19_08_wird_wiedererkannt(self) -> None:
        """Der Eichfall: zwei Speichen, deren Wert keine Mehrheit hat.

        `behutsamkeit` steht im gespeicherten Rad auf 0,60, waehrend zwei von
        drei Laeufen 0,40 sagten; `gespraechsdistanz` auf 0,10 bei Median 0,20.
        Das gespeicherte Rad ist hier der dritte Lauf — der Median-Lauf wurde
        ueber den **Versatz** gewaehlt, nicht je Speiche.
        """
        laeufe: list[dict] = [
            _rad({"behutsamkeit": 0.40}, {"gespraechsdistanz": 0.20}),
            _rad({"behutsamkeit": 0.40}, {"gespraechsdistanz": 0.20}),
            _rad({"behutsamkeit": 0.60}, {"gespraechsdistanz": 0.10}),
        ]
        gespeichert: dict = laeufe[2]

        mediane = speichenweise_mediane(laeufe)
        self.assertEqual(0.40, mediane["hoch"]["behutsamkeit"])
        self.assertEqual(0.20, mediane["runter"]["gespraechsdistanz"])

        self.assertEqual(
            ["hoch.behutsamkeit", "runter.gespraechsdistanz"],
            speichen_ohne_mehrheit(gespeichert, mediane),
        )

    def test_einigkeit_ergibt_eine_leere_liste(self) -> None:
        """Zusicherung 4 — die Gegenprobe zur Meldung.

        Der Fall des Zuwendungsrads vom 19.08.2026: 0 von 12 Speichen ohne
        Mehrheit, weil die stark ziehenden zeichengleich sind.
        """
        laeufe: list[dict] = [
            _rad({"treue": 0.8}, {"distanz": 0.1}),
            _rad({"treue": 0.8}, {"distanz": 0.1}),
            _rad({"treue": 0.8}, {"distanz": 0.1}),
        ]
        mediane = speichenweise_mediane(laeufe)
        self.assertEqual([], speichen_ohne_mehrheit(laeufe[0], mediane))

    def test_eine_speiche_ohne_median_gilt_nicht_als_abweichung(self) -> None:
        """Was nicht erhoben wurde, ist keine Abweichung, sondern eine Luecke.

        Sie hier zu melden machte die Liste unlesbar — und die Luecke selbst
        gehoert in `laeufe`, nicht in die Abweichungsliste.
        """
        mediane = {"hoch": {"treue": 0.5}, "runter": {}}
        self.assertEqual([], speichen_ohne_mehrheit(_rad({}, {}), mediane))


class MetadatenUeberlebenDieStabilisierungTest(unittest.TestCase):
    """Der Weg des Feldes bis in die gespeicherte Struktur.

    **Ein Feld zu berechnen ist nicht dasselbe, wie es abzulegen.** Beide
    Stabilisierungspfade bauten das Rad bis zum 23.08.2026 als **aufgezaehltes
    Literal** neu — `speichen_median` und `speichen_ohne_mehrheit` standen
    nicht darin und erreichten die Spalte nie. Gefunden hat es die zweite
    Kontrolle, nicht die Zeugen oben: Die pruefen die Rechnung, nicht ihren
    Weg.

    **Am Bestand gemessen, wie alt die Klasse ist:** 20 von 24 destillierten
    Zuwendungs-Raedern trugen nur `hoch` und `runter` — dort fielen schon
    `laeufe` und `streuung` heraus, lange vor diesem Feld. Die Aufzaehlung
    verliert lautlos, was sie nicht kennt, und beim naechsten Metadatum
    wieder. Deshalb pruefen diese Zeugen die **Bauart** und nicht die zwei
    Feldnamen von heute.
    """

    def _quelle(self, name: str) -> str:
        """Der Quelltext einer der beiden Stabilisierungsfunktionen."""
        from agents.charakter.agent import CharakterAgent

        return inspect.getsource(getattr(CharakterAgent, name))

    def _rad_neu_zuweisungen(self, quelle: str) -> list[ast.AST]:
        """Die Zuweisungen an `rad_neu` in dieser Funktion."""
        baum = ast.parse(textwrap.dedent(quelle))
        treffer: list[ast.AST] = []
        for knoten in ast.walk(baum):
            ziele = []
            if isinstance(knoten, ast.Assign):
                ziele = knoten.targets
            elif isinstance(knoten, ast.AnnAssign):
                ziele = [knoten.target]
            for ziel in ziele:
                if isinstance(ziel, ast.Name) and ziel.id == "rad_neu":
                    treffer.append(knoten)
        return treffer

    def test_beide_pfade_schreiben_das_rad_fort_statt_es_aufzuzaehlen(self) -> None:
        """`dict(rad_frisch)` statt eines Literals mit festen Schluesseln.

        Der Zeuge fragt die **Grammatik** und nicht die gemeinte Menge: Ein
        Test auf die zwei Feldnamen waere beim dritten Metadatum wieder gruen
        und wieder falsch.
        """
        for name in (
            "_rad_ueber_reihe_stabilisieren",
            "_initiative_ueber_reihe_stabilisieren",
        ):
            with self.subTest(funktion=name):
                zuweisungen = self._rad_neu_zuweisungen(self._quelle(name))
                self.assertTrue(zuweisungen, f"{name} weist `rad_neu` nicht zu")

                erste = zuweisungen[0]
                self.assertNotIsInstance(
                    getattr(erste, "value", None), ast.Dict,
                    f"{name} baut `rad_neu` als Literal — jedes Metadatum, das "
                    f"dort nicht aufgezaehlt ist, faellt weg",
                )

    def test_beide_speichenfelder_werden_ueber_die_reihe_neu_gerechnet(self) -> None:
        """Sie beschreiben das Rad, das gespeichert wird — nicht das frische.

        **Die Falle, die der erste Bau am 23.08.2026 selbst gestellt hatte:**
        `speichen_median` und `speichen_ohne_mehrheit` reisten als Metadaten
        der frischen Erhebung mit. Nach der Stabilisierung kommen die
        gespeicherten Speichen aber aus dem Mittel ueber die **Reihe** — die
        Liste haette einen Median aus drei Laeufen gegen eine Speiche aus
        allen Erhebungen gehalten. Zwei Groessen, ein Vergleich, keine
        Aussage.

        Der Zeuge fragt die Grammatik: Stehen nach der Zuweisung von `rad_neu`
        noch Zuweisungen an die beiden Felder? Ein Test auf ihre Werte
        pruefte, ob heute richtig gerechnet wird — nicht, ob ueberhaupt neu
        gerechnet wird.
        """
        for name in (
            "_rad_ueber_reihe_stabilisieren",
            "_initiative_ueber_reihe_stabilisieren",
        ):
            with self.subTest(funktion=name):
                quelle: str = self._quelle(name)
                for feld in ("speichen_median", "speichen_ohne_mehrheit"):
                    self.assertIn(
                        f'rad_neu["{feld}"]', quelle,
                        f"{name} rechnet `{feld}` nicht neu — es traegt dann "
                        f"die Fassung der frischen Erhebung weiter, waehrend "
                        f"die gespeicherten Speichen aus der Reihe kommen",
                    )

    def test_die_fortschreibung_traegt_jedes_metadatum(self) -> None:
        """Die Wirkung: ein erfundenes Feld ueberlebt die Umformung.

        Er nennt bewusst **kein** echtes Feld. Waere er auf `speichen_median`
        geschrieben, pruefte er die zwei Namen von heute und nicht die Bauart,
        die auch das naechste traegt.
        """
        rad_frisch: dict = {
            "hoch":   {"treue": 0.8},
            "runter": {"distanz": 0.2},
            "laeufe": [0.9, 1.0],
            "speichen_median": {"hoch": {"treue": 0.7}, "runter": {}},
            "ein_feld_das_es_morgen_gibt": 42,
        }
        flach: dict = {"treue": 0.6, "distanz": 0.4}

        # Dieselbe Umformung, die beide Pfade seit dem 23.08.2026 benutzen.
        rad_neu: dict = dict(rad_frisch)
        rad_neu["hoch"]   = {n: flach[n] for n in rad_frisch["hoch"]}
        rad_neu["runter"] = {n: flach[n] for n in rad_frisch["runter"]}

        self.assertEqual(0.6, rad_neu["hoch"]["treue"])
        self.assertEqual({"hoch": {"treue": 0.7}, "runter": {}}, rad_neu["speichen_median"])
        self.assertEqual(42, rad_neu["ein_feld_das_es_morgen_gibt"])
        self.assertEqual([0.9, 1.0], rad_neu["laeufe"])


class FlacheReiheTest(unittest.TestCase):
    """Zwei Gestalten fuer denselben Gegenstand.

    Die Destillation fuehrt ein Rad zweistufig, der Speicher legt es flach ab.
    Ein Verbraucher, der nur eine kennt, bekommt von der anderen **null**
    Speichen — und null sieht aus wie Einigkeit, nicht wie ein Lesefehler.
    Genau so meldete ein Messwerkzeug am 23.08.2026 einen Anteil von 0,0 %
    ueber 95 Erhebungen.
    """

    def test_die_flache_messung_wird_nach_dem_muster_zerlegt(self) -> None:
        """Welche Speiche wohin gehoert, sagt das Rad und keine zweite Liste."""
        muster: dict = _rad({"treue": 0.0, "dienst": 0.0}, {"distanz": 0.0})
        reihe: list[dict] = [
            {"treue": 0.8, "dienst": 0.6, "distanz": 0.2},
            {"treue": 0.4, "dienst": 0.6, "distanz": 0.4},
        ]

        raeder = flache_reihe_als_raeder(reihe, muster)

        self.assertEqual(2, len(raeder))
        self.assertEqual({"treue": 0.8, "dienst": 0.6}, raeder[0]["hoch"])
        self.assertEqual({"distanz": 0.2}, raeder[0]["runter"])

    def test_eine_fehlende_speiche_wird_nicht_erfunden(self) -> None:
        """Sie fehlt im Ergebnis, statt mit einem Vorgabewert aufzutauchen."""
        muster: dict = _rad({"treue": 0.0, "dienst": 0.0}, {})
        raeder = flache_reihe_als_raeder([{"treue": 0.5}], muster)
        self.assertEqual({"treue": 0.5}, raeder[0]["hoch"])
        self.assertNotIn("dienst", raeder[0]["hoch"])

    def test_ein_muster_ohne_seiten_ist_ein_fehler(self) -> None:
        """Sonst waere jedes Ergebnis leer — und leer sieht aus wie Einigkeit."""
        with self.assertRaises(ValueError) as fall:
            flache_reihe_als_raeder([{"treue": 0.5}], {})
        self.assertIn("Einigkeit", str(fall.exception))

    def test_der_median_ueber_die_gehobene_reihe_rechnet(self) -> None:
        """Die beiden Funktionen greifen ineinander — das ist der Weg im Code."""
        muster: dict = _rad({"treue": 0.0}, {"distanz": 0.0})
        reihe: list[dict] = [
            {"treue": 0.2, "distanz": 0.9},
            {"treue": 0.8, "distanz": 0.1},
            {"treue": 0.4, "distanz": 0.5},
        ]
        mediane = speichenweise_mediane(flache_reihe_als_raeder(reihe, muster))
        self.assertEqual(0.4, mediane["hoch"]["treue"])
        self.assertEqual(0.5, mediane["runter"]["distanz"])


if __name__ == "__main__":
    unittest.main()
