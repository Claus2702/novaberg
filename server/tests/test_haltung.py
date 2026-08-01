"""Tests: Aus Landschaft und Zuwendungsrad folgen fuenf Verhaltensgroessen.

Ziel: Dieselbe Landschaft ergibt bei verschiedenen Raedern verschiedene Werte,
eine Grenze haelt unter jedem Charakter, und ein Ueberlauf wird gemeldet statt
gekappt.

Zeugen dieser Datei:
  * **Die erwarteten Werte sind von Hand gerechnet** und stehen als Literale.
    Sie stammen aus den Tabellen des Konzepts, nicht aus einem Lauf der
    Funktion — sonst verglichen sich zwei Ableitungen derselben Quelle.
  * **Die Rechenart wird an ihrer Wirkung geprueft, nicht am Feld.** Dass eine
    Zelle "grenze" heisst, sagt nichts; geprueft wird, dass ein Grundwert von
    null unter jeder Modifikation null bleibt.
  * **`_verrechnen` wird einzeln geprueft**, weil alle sechs Grenzen im
    Bestand den Grundwert 0.00 tragen. Ueber `haltung_berechnen` allein waere
    die Multiplikation von "immer null" nicht zu unterscheiden — der Test saehe
    gruen aus und pruefte nichts.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.dreischicht import CLUSTER_BESCHREIBUNGEN, CLUSTER_FRAGEN
from ei.haltung import (
    CLUSTER_GRENZE,
    CLUSTER_GRUNDWERT,
    GROESSE_MAX,
    GROESSE_MIN,
    GROESSEN,
    SPEICHEN_BEITRAG,
    SPEICHEN_UEBERSTEUERUNG,
    UEBERSTEUERUNG_AB,
    _verrechnen,
    haltung_berechnen,
)

HALTUNG_LOGGER: str = "ki_server.ei.haltung"


class RechnungTest(unittest.TestCase):
    """Die Verknuepfung von Grundwert und Modifikation."""

    def test_neigung_addiert(self) -> None:
        """glut/umfang: 0.70 Grundwert, wissbegier 1.0 traegt +0.30."""
        haltung = haltung_berechnen("glut", {"wissbegier": 1.0})
        self.assertIsNotNone(haltung)
        self.assertAlmostEqual(haltung.werte["umfang"].ergebnis, 1.00, places=6)
        self.assertAlmostEqual(haltung.werte["umfang"].grundwert, 0.70, places=6)
        self.assertAlmostEqual(haltung.werte["umfang"].modifikation, 0.30, places=6)
        self.assertEqual(haltung.werte["umfang"].art, "neigung")

    def test_halbe_auspraegung_wirkt_halb(self) -> None:
        """Wissbegier 0.5 traegt +0.15 statt +0.30 auf glut/umfang."""
        haltung = haltung_berechnen("glut", {"wissbegier": 0.5})
        self.assertAlmostEqual(haltung.werte["umfang"].ergebnis, 0.85, places=6)

    def test_gegenlaeufige_speichen_verrechnen_sich(self) -> None:
        """glut/naehe: 0.90 + treue 0.20 + wohlwollen 0.10 - distanz 0.50."""
        haltung = haltung_berechnen(
            "glut", {"treue": 1.0, "wohlwollen": 1.0, "distanz": 1.0},
        )
        # Distanz uebersteuert die Naehe nicht, weil glut dort keine Grenze hat.
        self.assertAlmostEqual(haltung.werte["naehe"].modifikation, -0.20, places=6)
        self.assertAlmostEqual(haltung.werte["naehe"].ergebnis, 0.70, places=6)

    def test_leeres_rad_laesst_die_grundwerte_stehen(self) -> None:
        """Ohne Charakter bleibt die Landschaft, was sie ist."""
        haltung = haltung_berechnen("foyer", {})
        for groesse in GROESSEN:
            with self.subTest(groesse=groesse):
                wert = haltung.werte[groesse]
                self.assertAlmostEqual(wert.modifikation, 0.0, places=6)
                self.assertAlmostEqual(
                    wert.ergebnis, CLUSTER_GRUNDWERT["foyer"][groesse], places=6,
                )

    def test_die_reihenfolge_der_speichen_entscheidet_nichts(self) -> None:
        """Erst summieren, dann verrechnen — sonst waere das Rad geordnet.

        Der positive Zwilling zur Reihenfolge-Zusicherung im Charakter-Rad:
        Dort ist die Reihenfolge tragend, hier darf sie es nicht sein.
        """
        vorwaerts = haltung_berechnen(
            "bier", {"treue": 1.0, "distanz": 0.5, "wohlwollen": 1.0},
        )
        rueckwaerts = haltung_berechnen(
            "bier", {"wohlwollen": 1.0, "distanz": 0.5, "treue": 1.0},
        )
        for groesse in GROESSEN:
            with self.subTest(groesse=groesse):
                self.assertAlmostEqual(
                    vorwaerts.werte[groesse].ergebnis,
                    rueckwaerts.werte[groesse].ergebnis,
                    places=9,
                )


class GrenzeTest(unittest.TestCase):
    """Eine Grenze skaliert, sie verschiebt nicht."""

    def test_null_bleibt_null_unter_jeder_modifikation(self) -> None:
        """regen/draengen steht auf 0.00 und ist eine Grenze.

        dienst traegt +0.30 auf draengen. Additiv ergaebe das 0.30 — die Lage
        sagt aber, dass hier nicht gedraengt wird.
        """
        haltung = haltung_berechnen("regen", {"dienst": 1.0})
        wert = haltung.werte["draengen"]
        self.assertEqual(wert.art, "grenze")
        self.assertAlmostEqual(wert.modifikation, 0.30, places=6)
        self.assertAlmostEqual(wert.ergebnis, 0.00, places=6)

    def test_die_grenze_multipliziert_wirklich(self) -> None:
        """Mit einem Grundwert groesser null ist die Bauart sichtbar.

        Ohne diese Zusicherung waere die Multiplikation ungeprueft: Alle sechs
        Grenzen im Bestand tragen 0.00, und dort liefert jede Rechnung null.
        """
        self.assertAlmostEqual(_verrechnen(0.40, 0.50, "grenze"), 0.60, places=6)
        self.assertAlmostEqual(_verrechnen(0.40, -0.50, "grenze"), 0.20, places=6)
        self.assertAlmostEqual(_verrechnen(0.00, 9.90, "grenze"), 0.00, places=6)

    def test_neigung_und_uebersteuerung_addieren(self) -> None:
        """Der Gegensatz zur Multiplikation, an denselben Zahlen."""
        self.assertAlmostEqual(_verrechnen(0.40, 0.50, "neigung"), 0.90, places=6)
        self.assertAlmostEqual(
            _verrechnen(0.40, 0.50, "uebersteuerung"), 0.90, places=6,
        )

    def test_eine_grenze_ohne_ausloeser_haelt(self) -> None:
        """gewitter/fragen bleibt null, solange keine Uebersteuerung greift."""
        haltung = haltung_berechnen("gewitter", {"aufmerksamkeit": 1.0})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "grenze")
        self.assertAlmostEqual(wert.ergebnis, 0.00, places=6)


class UebersteuerungTest(unittest.TestCase):
    """Der Charakter darf die Lage ueberschreiben — markiert."""

    def test_volle_wissbegier_durchbricht_das_fragenverbot(self) -> None:
        """gewitter/fragen ist eine Grenze bei 0.00; wissbegier traegt +0.40."""
        haltung = haltung_berechnen("gewitter", {"wissbegier": 1.0})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "uebersteuerung")
        self.assertEqual(wert.ausloeser, "wissbegier")
        self.assertAlmostEqual(wert.ergebnis, 0.40, places=6)

    def test_halbe_wissbegier_durchbricht_sie_nicht(self) -> None:
        """Genau unter der Schwelle: Der Beitrag wirkt als Neigung.

        Gegen eine Grenze mit Grundwert null heisst das: gar nicht. Ohne diese
        Zusicherung waere `UEBERSTEUERUNG_AB` wirkungslos und niemand saehe es.
        """
        haltung = haltung_berechnen("gewitter", {"wissbegier": 0.5})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "grenze")
        self.assertEqual(wert.ausloeser, "")
        self.assertAlmostEqual(wert.ergebnis, 0.00, places=6)

    def test_die_schwelle_liegt_bei_voller_auspraegung(self) -> None:
        """Knapp darunter greift sie nicht, genau darauf greift sie."""
        knapp = haltung_berechnen("gewitter", {"wissbegier": UEBERSTEUERUNG_AB - 0.01})
        genau = haltung_berechnen("gewitter", {"wissbegier": UEBERSTEUERUNG_AB})
        self.assertEqual(knapp.werte["fragen"].art, "grenze")
        self.assertEqual(genau.werte["fragen"].art, "uebersteuerung")

    def test_eine_uebersteuerung_wirkt_nur_in_ihrer_groesse(self) -> None:
        """Wissbegier uebersteuert Fragen, nicht Draengen.

        Der positive Zwilling: Ohne ihn koennte die Uebersteuerung jede Grenze
        des Clusters aufheben, und der Test darueber bliebe trotzdem gruen.
        """
        haltung = haltung_berechnen("paradox", {"wissbegier": 1.0})
        self.assertEqual(haltung.werte["fragen"].art, "uebersteuerung")
        self.assertEqual(haltung.werte["draengen"].art, "grenze")

    def test_ohne_grenze_gibt_es_nichts_zu_uebersteuern(self) -> None:
        """glut/fragen ist eine Neigung — wissbegier addiert dort nur."""
        haltung = haltung_berechnen("glut", {"wissbegier": 1.0})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "neigung")
        self.assertEqual(wert.ausloeser, "")
        self.assertAlmostEqual(wert.ergebnis, 0.70, places=6)


class SpanneTest(unittest.TestCase):
    """Ein Ueberlauf wird gemeldet und markiert, nicht gekappt."""

    def test_waerme_laeuft_ueber_und_wird_markiert(self) -> None:
        """glut/waerme: 0.80 + treue 0.10 + wohlwollen 0.40 = 1.30.

        Der bekannte offene Punkt des Konzepts. Der Wert bleibt stehen, damit
        die Messreihe ihn zaehlen kann.
        """
        haltung = haltung_berechnen("glut", {"treue": 1.0, "wohlwollen": 1.0})
        wert = haltung.werte["waerme"]
        self.assertAlmostEqual(wert.ergebnis, 1.30, places=6)
        self.assertTrue(wert.ausserhalb)
        self.assertGreater(wert.ergebnis, GROESSE_MAX)

    def test_ein_ueberlauf_wird_gemeldet(self) -> None:
        """Stumm waere er von einem richtigen Wert nicht zu unterscheiden."""
        with self.assertLogs(HALTUNG_LOGGER, level="WARNING") as protokoll:
            haltung_berechnen("glut", {"treue": 1.0, "wohlwollen": 1.0})
        self.assertTrue(
            any("waerme" in zeile and "ausserhalb" in zeile for zeile in protokoll.output),
            f"keine Meldung zum Ueberlauf: {protokoll.output}",
        )

    def test_draengen_laeuft_unter_null(self) -> None:
        """glut/draengen: 0.20 Grundwert, treue 1.0 traegt -0.30.

        Die untere Spanne bricht genauso wie die obere, und schon bei einer
        einzigen voll ausgepraegten Speiche. Beim Entwurf war nur der Ueberlauf
        benannt — dieser Fall kam erst beim Bauen zum Vorschein.
        """
        haltung = haltung_berechnen("glut", {"treue": 1.0})
        wert = haltung.werte["draengen"]
        self.assertAlmostEqual(wert.ergebnis, -0.10, places=6)
        self.assertTrue(wert.ausserhalb)
        self.assertLess(wert.ergebnis, GROESSE_MIN)

    def test_ein_wert_in_der_spanne_wird_nicht_markiert(self) -> None:
        """Der positive Zwilling — sonst markierte `ausserhalb` alles."""
        haltung = haltung_berechnen("foyer", {})
        for groesse in GROESSEN:
            with self.subTest(groesse=groesse):
                self.assertFalse(haltung.werte[groesse].ausserhalb)

    def test_nichts_wird_gekappt(self) -> None:
        """Das Ergebnis traegt den gerechneten Wert, nicht die Obergrenze."""
        haltung = haltung_berechnen("glut", {"treue": 1.0, "wohlwollen": 1.0})
        self.assertNotAlmostEqual(
            haltung.werte["waerme"].ergebnis, GROESSE_MAX, places=6,
        )


class VorbedingungTest(unittest.TestCase):
    """Verletzte Vorbedingungen werden laut abgelehnt, nicht stillschweigend."""

    def test_unbekannter_cluster_wird_abgelehnt(self) -> None:
        """Eine Landschaft, die es nicht gibt, liefert keine stille Null."""
        with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
            self.assertIsNone(haltung_berechnen("nichtvorhanden", {}))

    def test_unbekannte_speiche_wird_abgelehnt(self) -> None:
        """Ein Tippfehler im Speichennamen waere sonst ein fehlender Beitrag."""
        with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
            self.assertIsNone(haltung_berechnen("glut", {"tapferkeit": 1.0}))

    def test_auspraegung_ueber_eins_wird_abgelehnt(self) -> None:
        """Ueber der Spanne: Der Beitrag wuerde ueberproportional wirken."""
        with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
            self.assertIsNone(haltung_berechnen("glut", {"treue": 1.5}))

    def test_negative_auspraegung_wird_abgelehnt(self) -> None:
        """Unter der Spanne: Das Vorzeichen des Beitrags kehrte sich um."""
        with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
            self.assertIsNone(haltung_berechnen("glut", {"treue": -0.5}))

    def test_wahrheitswert_ist_keine_auspraegung(self) -> None:
        """`True` ist in Python eine Eins und schluepft durch jede Zahlpruefung."""
        with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
            self.assertIsNone(haltung_berechnen("glut", {"treue": True}))

    def test_zeichenkette_ist_keine_auspraegung(self) -> None:
        """Eine Zahl als Text multipliziert sich in Python zu Text."""
        with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
            self.assertIsNone(haltung_berechnen("glut", {"treue": "1.0"}))

    def test_die_raender_der_spanne_sind_zulaessig(self) -> None:
        """Der Zwilling zu den vier Ablehnungen: 0.0 und 1.0 gehen durch."""
        self.assertIsNotNone(haltung_berechnen("glut", {"treue": 0.0}))
        self.assertIsNotNone(haltung_berechnen("glut", {"treue": 1.0}))


class TabellenTest(unittest.TestCase):
    """Die Tabellen sind vollstaendig und stimmen mit dem Bestand ueberein."""

    def test_jede_landschaft_des_bestands_hat_grundwerte(self) -> None:
        """Ein fehlender Cluster liefert sonst erst im Betrieb eine Ablehnung."""
        self.assertEqual(
            sorted(CLUSTER_GRUNDWERT), sorted(CLUSTER_BESCHREIBUNGEN),
        )

    def test_die_fragenspalte_folgt_dem_bestand(self) -> None:
        """Wo CLUSTER_FRAGEN "Keine" sagt, steht hier null und eine Grenze.

        Die Spalte ist aus dem Bestand uebersetzt, nicht gesetzt. Wer dort
        etwas aendert, muss es hier merken.
        """
        for cluster, text in CLUSTER_FRAGEN.items():
            if text.lower().startswith("keine"):
                with self.subTest(cluster=cluster):
                    self.assertEqual(CLUSTER_GRUNDWERT[cluster]["fragen"], 0.0)
                    self.assertIn("fragen", CLUSTER_GRENZE.get(cluster, frozenset()))

    def test_jede_landschaft_traegt_jede_groesse(self) -> None:
        """Eine fehlende Groesse liefert erst im Betrieb einen Schluesselfehler."""
        for cluster, werte in CLUSTER_GRUNDWERT.items():
            with self.subTest(cluster=cluster):
                self.assertEqual(sorted(werte), sorted(GROESSEN))

    def test_grundwerte_liegen_in_der_spanne(self) -> None:
        """Ein Grundwert ausserhalb macht jedes Ergebnis darauf unbrauchbar."""
        for cluster, werte in CLUSTER_GRUNDWERT.items():
            for groesse, wert in werte.items():
                with self.subTest(cluster=cluster, groesse=groesse):
                    self.assertGreaterEqual(wert, GROESSE_MIN)
                    self.assertLessEqual(wert, GROESSE_MAX)

    def test_jeder_beitrag_nennt_eine_bekannte_groesse(self) -> None:
        """Ein Tippfehler im Groessennamen bliebe sonst wirkungslos und stumm."""
        for speiche, beitraege in SPEICHEN_BEITRAG.items():
            for groesse in beitraege:
                with self.subTest(speiche=speiche, groesse=groesse):
                    self.assertIn(groesse, GROESSEN)

    def test_jede_speiche_des_rades_hat_einen_eintrag(self) -> None:
        """Die zwoelf Speichen der Zuwendung, wie die Destillation sie kennt."""
        from agents.charakter.destillation import RAD_ZUG_HOCH, RAD_ZUG_RUNTER

        self.assertEqual(
            sorted(SPEICHEN_BEITRAG),
            sorted(list(RAD_ZUG_HOCH) + list(RAD_ZUG_RUNTER)),
        )

    def test_jede_uebersteuerung_gehoert_zu_einer_bekannten_speiche(self) -> None:
        """Eine Uebersteuerung ohne Speiche koennte nie ausgeloest werden."""
        for speiche, groessen in SPEICHEN_UEBERSTEUERUNG.items():
            with self.subTest(speiche=speiche):
                self.assertIn(speiche, SPEICHEN_BEITRAG)
                for groesse in groessen:
                    self.assertIn(groesse, GROESSEN)

    def test_jede_grenze_gehoert_zu_einer_bekannten_landschaft(self) -> None:
        """Eine Grenze an einer unbekannten Landschaft wirkt nirgends."""
        for cluster, groessen in CLUSTER_GRENZE.items():
            with self.subTest(cluster=cluster):
                self.assertIn(cluster, CLUSTER_GRUNDWERT)
                for groesse in groessen:
                    self.assertIn(groesse, GROESSEN)


class KurzfassungTest(unittest.TestCase):
    """Die Zeile fuer die Spur sagt, was nur sie sagen kann."""

    def test_die_kurzfassung_nennt_jede_groesse(self) -> None:
        """Was in der Zeile fehlt, sieht in der Spur aus wie nicht gerechnet."""
        haltung = haltung_berechnen("glut", {})
        zeile: str = haltung.kurzfassung()
        for groesse in GROESSEN:
            with self.subTest(groesse=groesse):
                self.assertIn(groesse, zeile)

    def test_eine_uebersteuerung_steht_in_der_zeile(self) -> None:
        """Ein durchbrochenes Verbot muss in der Spur zu sehen sein."""
        haltung = haltung_berechnen("gewitter", {"wissbegier": 1.0})
        zeile: str = haltung.kurzfassung()
        self.assertIn("UEBERSTEUERT", zeile)
        self.assertIn("wissbegier", zeile)

    def test_ohne_uebersteuerung_steht_sie_nicht_da(self) -> None:
        """Der Zwilling — sonst meldete jede Zeile eine Uebersteuerung."""
        haltung = haltung_berechnen("glut", {})
        self.assertNotIn("UEBERSTEUERT", haltung.kurzfassung())


if __name__ == "__main__":
    unittest.main()
