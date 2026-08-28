"""Zeugen: Die Rueckfrage hat eine Menge UND eine Art — beide erreichen ihren Leser.

**Zwei Defekte einer Sache, gefunden am 27.08.2026.**

*Die Menge war zu hoch.* Gemessen ueber 424 Turns mit protokollierter Haltung
liegt der Zuschlag des Charakter-Rades auf `fragen` bei rund **+0,38**, in
jeder Landschaft nahezu gleich. Er hob `werkstatt` auf 1,18 (ueber
`GROESSE_MAX`) und liess `glut` — Vorgabe *„Selten, jeder 3.-4. Turn"* — bei
0,70 landen. Der Grundwert ist deshalb halbiert; das Rad bleibt vorerst, wie
es ist.

*Die Art kam nie an.* `stoffzeilen` lieferte dem Verfasser ausschliesslich
die **Menge**. Die **Art** stand in `CLUSTER_FRAGEN`, lief aber nur in den
Strategie-Prompt des GV-Knotens — der Knoten, der die Frage schreibt, sah sie
nicht. Gemessen an 84 Schlussfragen des produktiven Paares:

    beginnt als Angebot ("Sollen wir …", "Willst du …")   28/84   33 %
    davon zusaetzlich mit "oder"                          19/84   23 %
    enthaelt "tiefer" / "eintauchen"                      10/84   12 %

Neunzehn Fragen auf demselben Satzgeruest. **Wer eine Menge bestellt und
sonst nichts, bekommt die Form, die zugleich die Vorschlagsvorgabe
erledigt** — und das ist immer dieselbe.

**Die Art haengt an der Landschaft, nicht am Vehikel** — und das ist die
Korrektur eines ersten Versuchs vom selben Tag. Der hing sie an
`vehikel == "frage"` im GV-Block des Verfassers. Gemessen ueber 610
GV-Parses aus dem Serverlog:

    Vehikel leer      456   75 %
    Vehikel=aussage   101   17 %
    Vehikel=frage      53    9 %

Dazu `Absicht` leer in 405 und `Strategie` leer in 400 Faellen. **Eine
Vorgabe, die in jedem elften Turn ankommt, ist keine.** Die Landschaft steht
in jedem Turn; die Zeile haengt deshalb dort.

Zeugen dieser Datei:
  * **Die Art wird an der erzeugten Zeile geprueft, nicht an der Tabelle.**
    Dass `CLUSTER_FRAGE_ART` einen Eintrag hat, sagt nichts darueber, ob er
    beim Verfasser ankommt — genau das war der Defekt.
  * **Die Gegenprobe steht daneben.** Wo die Landschaft keine Frage zulaesst,
    darf keine Art stehen — sonst waere es eine Vorgabe ohne Gegenstand.
  * **Das Nachhaken wird als erreichbar geprueft, nicht als vorhanden.**
    Ausdruecklich verlangt: Die Halbierung darf das Band nicht abschneiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.dreischicht import (
    CLUSTER_FRAGE_ART,
    CLUSTER_FRAGE_MENGE,
    CLUSTER_FRAGEN,
)
from ei.haltung import CLUSTER_GRUNDWERT, haltung_berechnen
from ei.haltungssprache import stoff_band, stoffzeilen

# Der gemessene Zuschlag des Rades auf `fragen`, Mittel ueber 424 Turns mit
# protokollierter Haltung (27.08.2026). Eine Messung, keine Setzung — und
# deshalb hier als Konstante mit Datum statt als Zahl im Testkoerper.
RAD_ZUSCHLAG: float = 0.38

# Ein Rad, das die Frage-Groesse anhebt: die beiden Speichen, die im Betrieb
# fast am Anschlag stehen (wissbegier 0.87, aufmerksamkeit 0.91).
RAD_FRAGEND: dict[str, float] = {"wissbegier": 0.87, "aufmerksamkeit": 0.91}


def _rueckfragenzeile(cluster: str) -> str:
    """Die zweite Stoffzeile — die, die der Verfasser als Rueckfrage liest."""
    haltung = haltung_berechnen(cluster, RAD_FRAGEND)
    return stoffzeilen(haltung, reiz_zeichen=120, intentionen=())[1]


class DieArtDerFrageErreichtDenVerfasserTest(unittest.TestCase):
    """Der Defekt: Die Art stand in der Tabelle und lief am Schreiber vorbei."""

    def test_die_art_steht_in_der_zeile(self) -> None:
        """Rot, sobald der Verfasser wieder nur die Menge bekommt."""
        self.assertIn("analytisch", _rueckfragenzeile("werkstatt"))

    def test_die_menge_steht_weiterhin_darin(self) -> None:
        """Die Art darf die Menge nicht verdraengen — beide werden gebraucht."""
        zeile: str = _rueckfragenzeile("werkstatt")

        self.assertTrue(zeile.startswith("Rueckfrage: "))
        self.assertIn("Rueckfrage, die nachhakt", zeile)

    def test_die_landschaft_entscheidet_die_art(self) -> None:
        """Eine feste Zeile fuer alle Landschaften waere im ersten Test gruen."""
        zeile: str = _rueckfragenzeile("kissenschlacht")

        self.assertIn("neckisch", zeile)
        self.assertNotIn("analytisch", zeile)

    def test_ohne_frage_keine_art(self) -> None:
        """Die Gegenprobe: Wo nicht gefragt wird, gibt es nichts zu praegen.

        `gewitter` fuehrt `fragen` als Grenze — das Rad kann sie nicht
        anheben. Eine Art-Angabe waere dort eine Vorgabe ohne Gegenstand.
        """
        zeile: str = _rueckfragenzeile("gewitter")

        self.assertEqual(zeile, "Rueckfrage: keine Rueckfrage.")

    def test_die_werkstattfrage_ist_ausdruecklich_kein_angebot(self) -> None:
        """Der gemessene Defekt beim Namen genannt.

        23 % der Schlussfragen waren Angebotsfragen mit Alternative. In der
        Werkstatt wird Fachwissen nachgefragt — die Vorgabe sagt das, statt
        es dem Modell zu ueberlassen.
        """
        self.assertIn("kein Angebot", _rueckfragenzeile("werkstatt"))


class DieMengeIstHalbiertUndDasNachhakenBleibtTest(unittest.TestCase):
    """Die Halbierung darf das obere Band nicht abschneiden."""

    def test_kein_grundwert_ueber_der_haelfte(self) -> None:
        """Rot, sobald ein Wert auf den alten Stand zurueckwandert."""
        hoechster: float = max(
            werte["fragen"] for werte in CLUSTER_GRUNDWERT.values())

        self.assertLessEqual(hoechster, 0.45)

    def test_das_nachhaken_bleibt_erreichbar(self) -> None:
        """Ausdruecklich verlangt: als Option offen, nicht abgeschnitten.

        Geprueft am Band, nicht an der Zahl — die Zahl allein sagt nicht, was
        der Verfasser daraus liest.
        """
        wert: float = CLUSTER_GRUNDWERT["werkstatt"]["fragen"] + RAD_ZUSCHLAG

        self.assertIn("nachhakt", stoff_band("fragen", wert))

    def test_die_grenzlandschaften_bleiben_bei_null(self) -> None:
        """Halbieren darf aus einer Grenze keine Neigung machen."""
        for cluster in ("nebel", "gewitter", "paradox"):
            with self.subTest(cluster=cluster):
                self.assertEqual(CLUSTER_GRUNDWERT[cluster]["fragen"], 0.0)


class DieTabellenBleibenDeckungsgleichTest(unittest.TestCase):
    """Menge, Art und Grundwert beschreiben dieselben vierzehn Landschaften."""

    def test_menge_und_art_decken_dieselben_landschaften(self) -> None:
        """Eine fehlende Art faellt sonst erst im Betrieb als Warnung auf."""
        self.assertEqual(set(CLUSTER_FRAGE_MENGE), set(CLUSTER_FRAGE_ART))

    def test_die_grundwerttabelle_kennt_dieselben(self) -> None:
        """Die beiden Tabellen sind von Hand gekoppelt (haltung.py §Grundwerte)."""
        self.assertEqual(set(CLUSTER_FRAGE_MENGE), set(CLUSTER_GRUNDWERT))

    def test_die_zusammengesetzte_zeile_traegt_beides(self) -> None:
        """`CLUSTER_FRAGEN` speist weiterhin den Strategie-Prompt des GV-Knotens."""
        self.assertEqual(CLUSTER_FRAGEN["werkstatt"],
                         "Mittel, analytisch — eine echte Sachfrage, kein Angebot")
        self.assertEqual(CLUSTER_FRAGEN["nebel"], "Keine")
        self.assertEqual(CLUSTER_FRAGEN["gewitter"],
                         "Keine — Spiegelung, keine Fragen")


class DieRueckfrageBekommtIhrenGegenstandTest(unittest.TestCase):
    """Scheibe 3 des Lage-Konzepts: Die Zeile nennt, wonach gefragt wird.

    Gemessen 27./28.08.2026: 2,2 Fragen je Turn, 100 % Frage-Enden, und die
    Antwort auf »Licht oder Wasser?« bestand aus vier Rueckfragen — eine
    Vorgabe ohne Gegenstand erzeugt Floskeln. **Die Haltung bleibt der
    Regler:** Wo sie keine Frage zulaesst, erzeugt auch ein Gegenstand keine.
    """

    GEGENSTAND: str = "Geburtstag — was dazu noch offen ist: wer"

    def _zeile(self, cluster: str, gegenstand: str | None) -> str:
        haltung = haltung_berechnen(cluster, RAD_FRAGEND)
        return stoffzeilen(haltung, reiz_zeichen=120, intentionen=(), gegenstand=gegenstand)[1]

    def test_mit_gegenstand_nennt_die_zeile_ihn_hinter_menge_und_art(self) -> None:
        zeile = self._zeile("werkstatt", self.GEGENSTAND)

        self.assertIn("Rueckfrage, die nachhakt", zeile)
        self.assertIn("analytisch", zeile)
        self.assertTrue(zeile.endswith(f"ihr Gegenstand: {self.GEGENSTAND}."), zeile)

    def test_die_haltung_bleibt_der_regler(self) -> None:
        """`gewitter` laesst keine Frage zu — der Gegenstand aendert daran nichts."""
        self.assertEqual(self._zeile("gewitter", self.GEGENSTAND), "Rueckfrage: keine Rueckfrage.")

    def test_ohne_gegenstand_steht_die_zeile_wie_bisher(self) -> None:
        self.assertEqual(self._zeile("werkstatt", None), _rueckfragenzeile("werkstatt"))
        self.assertNotIn("Gegenstand", self._zeile("werkstatt", None))
