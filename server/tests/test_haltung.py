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

import itertools
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
    speichen_spanne,
)

HALTUNG_LOGGER: str = "ki_server.ei.haltung"


class RechnungTest(unittest.TestCase):
    """Die Verknuepfung von Grundwert und Modifikation."""

    def test_die_neigung_geht_den_verbleibenden_weg(self) -> None:
        """glut/umfang: 0.70 Grundwert, dienst 1.0 traegt +0.20.

        Bis zum 08.08.2026 wurde addiert und ergab genau 1.00 — den Rand. Die
        Wegform normiert die Summe auf die Spanne der Groesse (+0.80) und geht
        diesen Anteil des verbleibenden Wegs: 0.70 + 0.375 * 0.30.

        **Die Modifikation bleibt die rohe Summe.** Sie ist die Messgroesse
        des Charakters und darf nicht durch die Normierung verschwinden — im
        Protokoll steht weiter, was das Rad beigetragen hat.
        """
        haltung = haltung_berechnen("glut", {"dienst": 1.0})
        self.assertIsNotNone(haltung)
        self.assertAlmostEqual(haltung.werte["umfang"].ergebnis, 0.82, places=6)
        self.assertAlmostEqual(haltung.werte["umfang"].grundwert, 0.70, places=6)
        self.assertAlmostEqual(haltung.werte["umfang"].modifikation, 0.20, places=6)
        self.assertEqual(haltung.werte["umfang"].art, "neigung")

    def test_halbe_auspraegung_geht_den_halben_weg(self) -> None:
        """Die Linearitaet ueberlebt die Wegform.

        Geprueft wird die Eigenschaft, nicht die Zahl: Die halbe Auspraegung
        legt genau die Haelfte der Strecke zurueck, die die volle zurueckgelegt
        haette. Eine Zahl allein wuerde auch dann bestehen, wenn die Form
        irgendwo geknickt waere.
        """
        voll  = haltung_berechnen("glut", {"dienst": 1.0}).werte["umfang"]
        halb  = haltung_berechnen("glut", {"dienst": 0.5}).werte["umfang"]
        grund = voll.grundwert

        self.assertAlmostEqual(halb.ergebnis - grund,
                               (voll.ergebnis - grund) / 2, places=9)

    def test_gegenlaeufige_speichen_verrechnen_sich(self) -> None:
        """glut/naehe: 0.90 + treue 0.20 + wohlwollen 0.10 - distanz 0.50."""
        haltung = haltung_berechnen(
            "glut", {"treue": 1.0, "wohlwollen": 1.0, "distanz": 1.0},
        )
        # Distanz uebersteuert die Naehe nicht, weil glut dort keine Grenze hat.
        # -0.20 auf der Abwaertsspanne (-1.20) sind -1/6 des Wegs nach unten:
        # 0.90 - 0.16667 * 0.90 = 0.75.
        self.assertAlmostEqual(haltung.werte["naehe"].modifikation, -0.20, places=6)
        self.assertAlmostEqual(haltung.werte["naehe"].ergebnis, 0.75, places=6)

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
        # Die Eingabe wird aus der Spanne gebaut, damit n genau 1 ist — dann
        # ist die **Form** sichtbar und der Test haengt nicht an einer Zahl der
        # Beitragstabelle. Die Erwartungen bleiben Literale.
        runter, hoch = speichen_spanne("umfang")

        self.assertAlmostEqual(_verrechnen(0.40, hoch, "grenze", "umfang"), 0.80, places=6)
        self.assertAlmostEqual(_verrechnen(0.40, runter, "grenze", "umfang"), 0.00, places=6)
        # Und null bleibt null, gleich wie gross die Summe ist.
        self.assertAlmostEqual(_verrechnen(0.00, 9.90, "grenze", "umfang"), 0.00, places=6)

    def test_neigung_und_uebersteuerung_gehen_den_weg(self) -> None:
        """Der Gegensatz zur Multiplikation, an denselben Zahlen.

        Bei vollem Weg nach oben (n = 1) geht ein Grundwert von 0.40 auf 1.00.
        Die Grenze kaeme mit derselben Eingabe auf 0.80 — der Unterschied
        zwischen "skaliert, was die Lage zulaesst" und "geht den Rest des Wegs".
        """
        _runter, hoch = speichen_spanne("umfang")

        self.assertAlmostEqual(
            _verrechnen(0.40, hoch, "neigung", "umfang"), 1.00, places=6)
        self.assertAlmostEqual(
            _verrechnen(0.40, hoch, "uebersteuerung", "umfang"), 1.00, places=6)

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
        # +0.40 auf der Aufwaertsspanne von `fragen` (+0.70): n = 0.5714, und
        # ein Grundwert von 0.00 hat den vollen Weg vor sich.
        self.assertAlmostEqual(wert.ergebnis, 0.571429, places=5)

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
    """Die Spanne kann nicht mehr verlassen werden — und wird nicht gekappt.

    **Diese Klasse sicherte bis zum 08.08.2026 das Gegenteil zu.** Sie hielt
    fest, dass `glut/waerme` auf 1.30 laeuft und `glut/draengen` auf -0.10, und
    das war richtig: Der Wert blieb stehen, damit die Messreihe ihn zaehlen
    konnte. Die Zusicherung hat ihren Zweck erfuellt — die Haeufigkeit wurde
    gezaehlt, und ueber die volle Charakterspanne gerechnet verliessen **62 von
    62** Zellen die Spanne.

    Damit war die Frage beantwortet und die Rechenform geaendert. Die
    Zusicherung dreht sich um: Nicht "der Ueberlauf bleibt sichtbar", sondern
    "er kann nicht entstehen". **Gekappt wird weiterhin nichts** — Kappen
    erzeugt genau die toten Enden, die der Raum nicht haben darf.
    """

    def test_die_warme_landschaft_bleibt_in_der_spanne(self) -> None:
        """glut/waerme lief mit diesem Rad auf 1.30."""
        haltung = haltung_berechnen("glut", {"treue": 1.0, "wohlwollen": 1.0})
        wert = haltung.werte["waerme"]

        self.assertFalse(wert.ausserhalb)
        self.assertLessEqual(wert.ergebnis, GROESSE_MAX)
        self.assertGreater(wert.ergebnis, wert.grundwert)

    def test_die_untere_spanne_haelt_ebenso(self) -> None:
        """glut/draengen lief mit einer einzigen Speiche auf -0.10."""
        haltung = haltung_berechnen("glut", {"treue": 1.0})
        wert = haltung.werte["draengen"]

        self.assertFalse(wert.ausserhalb)
        self.assertGreaterEqual(wert.ergebnis, GROESSE_MIN)
        self.assertLess(wert.ergebnis, wert.grundwert)

    def test_keine_zelle_verlaesst_die_spanne_an_den_enden(self) -> None:
        """Die Naht wird ueber die Enden gerechnet, nicht ueber die Mitte.

        Das ist die eigentliche Zusicherung, und sie ist vollstaendig statt
        gestichprobt: Bei festem Rad ist die Haltung eine reine Funktion der
        Landschaft, also sind vierzehn Landschaften mal zwei Enden der ganze
        Raum. Die alte Form fiel hier in 62 von 62 Zellen durch.

        Gefahren wird mit **allen** Speichen voll ausgepraegt — einmal so, wie
        die Tabelle sie fuehrt, und einmal ist das der staerkste Zug, den ein
        Charakter ueberhaupt ausueben kann.
        """
        volles_rad: dict = dict.fromkeys(SPEICHEN_BEITRAG, 1.0)

        for cluster in CLUSTER_GRUNDWERT:
            haltung = haltung_berechnen(cluster, volles_rad)
            self.assertIsNotNone(haltung, f"{cluster} lieferte keine Haltung")
            for groesse, wert in haltung.werte.items():
                with self.subTest(cluster=cluster, groesse=groesse):
                    self.assertGreaterEqual(wert.ergebnis, GROESSE_MIN)
                    self.assertLessEqual(wert.ergebnis, GROESSE_MAX)
                    self.assertFalse(wert.ausserhalb)

    def test_die_ordnung_der_landschaften_ueberlebt_jeden_charakter(self) -> None:
        """Kein totes Ende: Zwei Landschaften fallen unter keinem Rad zusammen.

        Das ist der Grund, warum nicht gekappt wird. Kappen macht aus zwei
        verschiedenen Lagen dieselbe Zahl, und der Raum verliert genau dort
        seine Aufloesung, wo der Charakter am staerksten zieht.

        Geprueft an der Groesse mit der breitesten Beitragsspanne und ueber
        alle Landschaftspaare, die sich in ihr unterscheiden.
        """
        volles_rad: dict = dict.fromkeys(SPEICHEN_BEITRAG, 1.0)
        leeres_rad: dict = {}

        for rad, name in ((volles_rad, "volles Rad"), (leeres_rad, "Nabe")):
            ergebnisse: dict = {
                cluster: haltung_berechnen(cluster, rad).werte["waerme"].ergebnis
                for cluster in CLUSTER_GRUNDWERT
            }
            for a, b in itertools.combinations(CLUSTER_GRUNDWERT, 2):
                grund_a = CLUSTER_GRUNDWERT[a]["waerme"]
                grund_b = CLUSTER_GRUNDWERT[b]["waerme"]
                if grund_a == grund_b or "waerme" in CLUSTER_GRENZE.get(a, ()) \
                        or "waerme" in CLUSTER_GRENZE.get(b, ()):
                    continue
                with self.subTest(rad=name, a=a, b=b):
                    self.assertEqual(
                        grund_a > grund_b, ergebnisse[a] > ergebnisse[b],
                        f"{a} und {b} haben ihre Ordnung verloren",
                    )

    def test_die_nabe_reproduziert_die_landschaft_exakt(self) -> None:
        """Die Gegenprobe der Rechenform: n = 0 gibt den Grundwert zurueck."""
        for cluster in CLUSTER_GRUNDWERT:
            haltung = haltung_berechnen(cluster, {})
            for groesse, wert in haltung.werte.items():
                with self.subTest(cluster=cluster, groesse=groesse):
                    self.assertAlmostEqual(
                        wert.ergebnis, CLUSTER_GRUNDWERT[cluster][groesse],
                        places=9,
                    )

    def test_der_rand_wird_erreicht_aber_nur_ganz_aussen(self) -> None:
        """Der Unterschied zwischen "geht den ganzen Weg" und "gekappt".

        `waerme` hat eine Aufwaertsspanne von +0.50, und `treue` (+0.10) plus
        `wohlwollen` (+0.40) sind **genau diese Spanne**. Ein solches Rad steht
        am aeussersten Rand dessen, was die Tabelle zulaesst — dass es 1.0
        erreicht, ist die Zusicherung und nicht ihre Verletzung: Der Rand ist
        erreichbar, sonst waere die obere Ecke ein totes Ende.

        **Gekappt waere es dann, wenn auch ein schwaecheres Rad dort landete.**
        Genau das prueft die zweite Haelfte: Bei halber Auspraegung liegt der
        Wert echt darunter, und zwar streng.
        """
        ganz  = haltung_berechnen("glut", {"treue": 1.0, "wohlwollen": 1.0})
        halb  = haltung_berechnen("glut", {"treue": 0.5, "wohlwollen": 0.5})

        self.assertAlmostEqual(ganz.werte["waerme"].ergebnis, GROESSE_MAX, places=9)
        self.assertLess(halb.werte["waerme"].ergebnis, GROESSE_MAX)
        self.assertGreater(halb.werte["waerme"].ergebnis,
                           halb.werte["waerme"].grundwert)

    def test_ein_wert_in_der_spanne_wird_nicht_markiert(self) -> None:
        """Der positive Zwilling — sonst markierte `ausserhalb` alles."""
        haltung = haltung_berechnen("foyer", {})
        for groesse in GROESSEN:
            with self.subTest(groesse=groesse):
                self.assertFalse(haltung.werte[groesse].ausserhalb)


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
