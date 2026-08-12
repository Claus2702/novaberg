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
    UEBERSTEUERUNG_AB,
    UEBERSTEUERUNG_SPEICHEN,
    _verrechnen,
    haltung_berechnen,
    speichen_spanne,
    uebersteuerungs_zug,
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
        """glut/naehe: 0.90 + treue 0.20 + wohlwollen 0.10 - distanz 0.25.

        **Die Distanz steht hier unter der Schwelle, und das ist der Punkt.**
        Bis zum 11.08.2026 lief dieser Test mit `distanz = 1.0` und pruefte
        damit unbemerkt zwei Dinge in einem: das Verrechnen gegenlaeufiger
        Speichen und die Abwesenheit einer Uebersteuerung. Seit die
        Uebersteuerung auch in Neigungszellen zieht, wuerde die volle
        Auspraegung das Ergebnis auf 0.0 klemmen und das Verrechnen gar
        nicht mehr zeigen. Halb ausgepraegt bleibt allein die Verrechnung
        uebrig — die Uebersteuerung hat ihren eigenen Test.
        """
        haltung = haltung_berechnen(
            "glut", {"treue": 1.0, "wohlwollen": 1.0, "distanz": 0.5},
        )
        wert = haltung.werte["naehe"]
        # +0.05 auf der Aufwaertsspanne (+0.50) sind ein Zehntel des Wegs
        # nach oben: 0.90 + 0.1 * (1 - 0.90) = 0.91.
        self.assertEqual(wert.art, "neigung")
        self.assertAlmostEqual(wert.modifikation, 0.05, places=6)
        self.assertAlmostEqual(wert.ergebnis, 0.91, places=6)

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

    def test_die_neigung_geht_den_weg(self) -> None:
        """Der Gegensatz zur Multiplikation, an denselben Zahlen.

        Bei vollem Weg nach oben (n = 1) geht ein Grundwert von 0.40 auf 1.00.
        Die Grenze kaeme mit derselben Eingabe auf 0.80 — der Unterschied
        zwischen "skaliert, was die Lage zulaesst" und "geht den Rest des Wegs".

        Die zweite Zusicherung dieses Tests galt bis zum 11.08.2026 der
        Rechenart "uebersteuerung" und ist entfallen: Die Uebersteuerung ist
        keine Rechenart mehr, sondern ein Zug nach der Rechnung.
        """
        _runter, hoch = speichen_spanne("umfang")

        self.assertAlmostEqual(
            _verrechnen(0.40, hoch, "neigung", "umfang"), 1.00, places=6)

    def test_eine_grenze_ohne_ausloeser_haelt(self) -> None:
        """gewitter/fragen bleibt null, solange keine Uebersteuerung greift."""
        haltung = haltung_berechnen("gewitter", {"aufmerksamkeit": 1.0})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "grenze")
        self.assertAlmostEqual(wert.ergebnis, 0.00, places=6)


class UebersteuerungTest(unittest.TestCase):
    """Der Charakter darf die Lage ueberschreiben — markiert."""

    def test_volle_wissbegier_durchbricht_das_fragenverbot(self) -> None:
        """gewitter/fragen ist eine Grenze bei 0.00; wissbegier traegt +0.40.

        **Volle Auspraegung heisst voller Anschlag** (11.08.2026). Die Grenze
        haelt weiter multiplikativ — 0.00 mal irgendetwas bleibt 0.00 —, und
        darauf legt sich der Zug: bei 1.0 ist er 1.0, das Fragenverbot ist
        ganz aufgehoben. Bis zu diesem Tag ergab derselbe Fall 0.571429,
        weil die Uebersteuerung die Rechenart tauschte statt zu ziehen.
        """
        haltung = haltung_berechnen("gewitter", {"wissbegier": 1.0})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "uebersteuerung")
        self.assertEqual(wert.ausloeser, "wissbegier")
        self.assertAlmostEqual(wert.ergebnis, 1.00, places=6)

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

    def test_genau_auf_der_schwelle_ist_noch_keine_uebersteuerung(self) -> None:
        """Erst darueber, und die Marke faellt mit der Wirkung zusammen.

        Genau auf der Schwelle ist der Zug null. Waere die Zelle trotzdem
        als »uebersteuerung« markiert, zaehlte die Messreihe eine
        Uebersteuerung, die nichts verschoben hat — und wie oft sie greift,
        ist eine Messgroesse des Konzepts (§2).
        """
        genau  = haltung_berechnen("gewitter", {"wissbegier": UEBERSTEUERUNG_AB})
        drueber = haltung_berechnen("gewitter", {"wissbegier": UEBERSTEUERUNG_AB + 0.01})
        self.assertEqual(genau.werte["fragen"].art, "grenze")
        self.assertEqual(genau.werte["fragen"].ausloeser, "")
        self.assertEqual(drueber.werte["fragen"].art, "uebersteuerung")

    def test_die_schwelle_liegt_im_bereich_der_gemessenen_werte(self) -> None:
        """0.94 ist ein Wert, den das Rad ohne Raster wirklich vergibt.

        **Der Zeuge fuer einen stillen Ausfall, zweimal.** Die Zusicherung
        ist nicht die Zahl, sondern ihre Herkunft. Mit dem alten
        `UEBERSTEUERUNG_AB = 1.0` ist dieser Test rot — und er waere der
        einzige gewesen: Alle uebrigen fuehren die Schwelle symbolisch und
        bleiben gruen, egal wo sie steht.

        Und er haelt die zweite Haelfte des Fundes fest: **Das Raster von
        gestern hat `distanz` heruntergerundet.** Ueber zwoelf gerasterte
        Laeufe stand sie zwoelfmal auf exakt 0.9; ohne Raster liegt sie bei
        0.93 bis 0.96 (`labor/ergebnis/raster_*`). Eine Schwelle, die auf
        dem Rasterwert steht, loest deshalb nie aus — der wahre Wert liegt
        darueber und war nur nicht darstellbar.

        Geprueft an einer Grenzzelle, weil dort der Unterschied zwischen
        »haelt« und »oeffnet sich« am schaerfsten ist.
        """
        haltung = haltung_berechnen("gewitter", {"wissbegier": 0.94})
        self.assertEqual(haltung.werte["fragen"].art, "uebersteuerung")
        self.assertAlmostEqual(haltung.werte["fragen"].ergebnis, 0.16, places=6)

    def test_der_zug_verteilt_sich_ueber_die_zeile_der_speiche(self) -> None:
        """Wissbegier zieht Fragen ganz und Draengen halb — beides Grenzen.

        `SPEICHEN_BEITRAG["wissbegier"]` traegt `fragen +0.40` und
        `draengen +0.20`; die staerkste Zelle der Zeile ist 0.40. Also
        bekommt `fragen` den vollen Zug und `draengen` die Haelfte.

        **Bis zum 11.08.2026 hiess dieser Test »eine Uebersteuerung wirkt nur
        in ihrer Groesse« und behauptete das Gegenteil.** Er war richtig fuer
        eine Bauart, in der eine zweite Tabelle je Speiche genau eine Groesse
        nannte. Seit der Zug durch die Beitragszeile fliesst, ist die
        Verteilung der Punkt: Eine Speiche wirkt dorthin, wohin sie ohnehin
        traegt, in ihren eigenen Verhaeltnissen.
        """
        haltung = haltung_berechnen("paradox", {"wissbegier": 1.0})
        # Beide Zellen sind in `paradox` Grenzen bei Grundwert 0.00; was
        # dasteht, ist allein der Zug.
        self.assertEqual(haltung.werte["fragen"].art, "uebersteuerung")
        self.assertAlmostEqual(haltung.werte["fragen"].ergebnis, 1.00, places=6)
        self.assertEqual(haltung.werte["draengen"].art, "uebersteuerung")
        self.assertAlmostEqual(haltung.werte["draengen"].ergebnis, 0.50, places=6)

    def test_bei_zwei_ausschlaegen_gewinnt_der_staerkere_zug(self) -> None:
        """Sie summieren sich nicht — der extremere Zustand bestimmt.

        `distanz` traegt auf `naehe` -0.50 bei einer staerksten Zelle von
        0.50, zieht dort also voll. `misstrauen` traegt -0.20 bei staerkster
        Zelle 0.40, zieht dort halb. Beide voll ausgepraegt ergibt dasselbe
        wie `distanz` allein.

        Summierten sie, stuende in `ausloeser` nur einer von zweien und die
        Zeile nennte eine Ursache, die ihre eigene Zahl nicht erklaert.
        """
        allein = haltung_berechnen("glut", {"distanz": 1.0})
        beide  = haltung_berechnen("glut", {"distanz": 1.0, "misstrauen": 1.0})
        self.assertEqual(beide.werte["naehe"].ausloeser, "distanz")
        self.assertAlmostEqual(
            beide.werte["naehe"].ergebnis - allein.werte["naehe"].ergebnis,
            0.0, places=6,
            msg="Der zweite Ausschlag hat zusaetzlich gezogen — sie summieren sich",
        )

    def test_distanz_zieht_die_ganze_zeile_und_nicht_nur_die_naehe(self) -> None:
        """Voller Rueckzug macht kurz, fern und kuehl — in einem Zug.

        Die Zeile `umfang -0.30 · naehe -0.50 · waerme -0.20` verteilt sich
        auf 0.6 / 1.0 / 0.4 des Zuges. In `glut` (nah und warm) bleibt davon
        eine Haltung uebrig und kein Nullvektor: die Waerme haelt als
        einzige stand.
        """
        werte = haltung_berechnen("glut", {"distanz": 1.0}).werte
        self.assertAlmostEqual(werte["naehe"].ergebnis,  0.000, places=3)
        self.assertAlmostEqual(werte["umfang"].ergebnis, 0.196, places=3)
        self.assertAlmostEqual(werte["waerme"].ergebnis, 0.416, places=3)
        for groesse in ("naehe", "umfang", "waerme"):
            self.assertEqual(werte[groesse].ausloeser, "distanz")

    def test_auch_ohne_grenze_zieht_die_uebersteuerung(self) -> None:
        """glut/fragen ist eine Neigung — und wird trotzdem uebersteuert.

        **Der Zeuge fuer den Fund vom 11.08.2026.** Bis dahin fragte der
        Aufrufer `_uebersteuerer` nur fuer Grenzzellen. `naehe` ist in
        keiner der vierzehn Landschaften eine Grenze, also war die
        Uebersteuerung `distanz -> naehe` seit ihrem Bau in 0 von 14 Faellen
        erreichbar — dieser Test hiess damals »ohne Grenze gibt es nichts zu
        uebersteuern« und hielt genau den Defekt fest.

        Das Konzept sagt das Gegenteil: »`distanz` uebersteuert die Naehe,
        gleich wie warm die Landschaft ist« (§2).
        """
        haltung = haltung_berechnen("glut", {"wissbegier": 1.0})
        wert = haltung.werte["fragen"]
        self.assertEqual(wert.art, "uebersteuerung")
        self.assertEqual(wert.ausloeser, "wissbegier")
        # Neigung 0.70, dazu der volle Zug 1.0 — geklemmt auf 1.00.
        self.assertAlmostEqual(wert.ergebnis, 1.00, places=6)

    def test_distanz_zieht_die_naehe_in_jeder_warmen_landschaft(self) -> None:
        """Der Fall, den es vor dem 11.08.2026 in keiner Landschaft gab.

        `naehe` ist nirgends eine Grenze; unter der alten Bauart konnte
        `distanz` deshalb nie uebersteuern, auch nicht bei voller
        Auspraegung. Geprueft ueber alle Landschaften mit warmer Naehe.
        """
        for cluster in ("beichte", "glut", "regen", "kissenschlacht"):
            with self.subTest(cluster=cluster):
                wert = haltung_berechnen(cluster, {"distanz": 1.0}).werte["naehe"]
                self.assertEqual(wert.art, "uebersteuerung")
                self.assertEqual(wert.ausloeser, "distanz")
                self.assertAlmostEqual(wert.ergebnis, 0.00, places=6)

    def test_der_zug_ist_graduell_und_nicht_binaer(self) -> None:
        """Die Kurve: lange flach, dann steil — und stetig an der Schwelle.

        **Die Begruendung ist keine Rechenbequemlichkeit:** Ein Wesen kennt
        selten nur 0 und 1. Ein Schwellenwert,
        der von 0 auf 1 springt, machte aus einer Zehntelstelle im
        Modellurteil einen Zustandswechsel im Verhalten — genau die Haerte,
        die das Rad mit der feinen Skala loswerden sollte.
        """
        self.assertAlmostEqual(uebersteuerungs_zug(0.70), 0.0000, places=6)
        self.assertAlmostEqual(uebersteuerungs_zug(UEBERSTEUERUNG_AB), 0.0, places=6)
        self.assertAlmostEqual(uebersteuerungs_zug(0.93), 0.0900, places=6)
        self.assertAlmostEqual(uebersteuerungs_zug(0.95), 0.2500, places=6)
        self.assertAlmostEqual(uebersteuerungs_zug(0.97), 0.4900, places=6)
        self.assertAlmostEqual(uebersteuerungs_zug(1.00), 1.0000, places=6)

        # Monoton, ohne Sprung: je hoeher die Auspraegung, desto staerker der
        # Zug. Ohne diese Zusicherung koennte ein Exponent unter 1 die Kurve
        # umdrehen, ohne dass ein Ankerwert es zeigt.
        werte = [uebersteuerungs_zug(x / 100) for x in range(80, 101)]
        self.assertEqual(werte, sorted(werte))

    def test_der_zug_lehnt_eine_auspraegung_ausserhalb_ab(self) -> None:
        """Eine Auspraegung ueber 1.0 ergaebe einen Zug ueber 1.0.

        Sie wird laut abgelehnt und nicht geklemmt: Das Rad ist an seiner
        Eingabegrenze zu pruefen, nicht hier stillschweigend zurechtgebogen.
        """
        with self.assertRaises(ValueError):
            uebersteuerungs_zug(1.01)
        with self.assertRaises(ValueError):
            uebersteuerungs_zug(-0.01)


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

    def test_bei_vollem_ausschlag_gibt_die_landschaft_auf(self) -> None:
        """Die eine gewollte Tuer — und sie steht genau auf 1.0.

        Das Gegenstueck zum Test darunter. Bei voller Auspraegung nimmt der
        Zug den ganzen verbleibenden Weg, und alle Landschaften fallen in
        derselben Groesse zusammen. **Das ist kein Verlust an Aufloesung,
        sondern die Aussage:** Wer ganz zugemacht hat, ist ueberall gleich
        zu, und die Lage traegt nichts mehr bei (Konzept §2 — »ein Charakter
        darf die Lage ueberschreiben«).

        Ohne diesen Test waere die Ausnahme im Test darunter eine stille
        Abschwaechung statt einer benannten Eigenschaft.
        """
        voll: dict = dict.fromkeys(SPEICHEN_BEITRAG, 1.0)
        waerme = {
            cluster: haltung_berechnen(cluster, voll).werte["waerme"].ergebnis
            for cluster in CLUSTER_GRUNDWERT
        }
        self.assertEqual(set(waerme.values()), {0.0})

    def test_die_ordnung_der_landschaften_ueberlebt_jeden_charakter(self) -> None:
        """Kein totes Ende: Zwei Landschaften fallen unter keinem Rad zusammen.

        Das ist der Grund, warum nicht gekappt wird. Kappen macht aus zwei
        verschiedenen Lagen dieselbe Zahl, und der Raum verliert genau dort
        seine Aufloesung, wo der Charakter am staerksten zieht.

        Geprueft an der Groesse mit der breitesten Beitragsspanne und ueber
        alle Landschaftspaare, die sich in ihr unterscheiden.

        **Bei 0.99 statt 1.0, seit dem 11.08.2026.** Der Zug schliesst die
        Tuer bei Auspraegung exakt 1.0 — dort ist der Charakter der Zustand
        und die Landschaft zaehlt nicht mehr; das ist Absicht und hat einen
        eigenen Test. Fuer jeden Wert darunter gilt die Zusicherung
        unveraendert, und genau das prueft dieser Fall: Ein Haar unter dem
        Anschlag traegt die Ordnung noch (0.0298 · 0.0265 · 0.0166 · 0.0066
        ueber `feuerwerk`, `bier`, `foyer`, `gewitter`).
        """
        volles_rad: dict = dict.fromkeys(SPEICHEN_BEITRAG, 0.99)
        leeres_rad: dict = {}

        for rad, name in ((volles_rad, "fast volles Rad"), (leeres_rad, "Nabe")):
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

    def test_jede_ziehberechtigte_speiche_hat_eine_zeile(self) -> None:
        """Eine Speiche ohne Beitragszeile koennte nie ziehen.

        Seit dem 11.08.2026 nennt `UEBERSTEUERUNG_SPEICHEN` nur noch, **wer**
        ziehen darf; **wohin** und **wie stark** steht in `SPEICHEN_BEITRAG`.
        Fehlte dort die Zeile, verschwaende der Zug lautlos — die Speiche
        stuende in der Liste und bewirkte nie etwas.
        """
        for speiche in sorted(UEBERSTEUERUNG_SPEICHEN):
            with self.subTest(speiche=speiche):
                self.assertIn(speiche, SPEICHEN_BEITRAG)
                self.assertTrue(
                    SPEICHEN_BEITRAG[speiche],
                    "Zeile ohne Beitrag — der Zug haette keine Richtung",
                )
                for groesse in SPEICHEN_BEITRAG[speiche]:
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
