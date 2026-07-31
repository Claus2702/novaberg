"""Tests: Die Initiative-Schwelle wird gegen einen Zeugen kalibriert.

Ziel: Die Suche findet die Schwelle mit dem besten kappa, die beide Bits
offen laesst — und schreibt nichts, wenn die Grundlage zu duenn ist oder kein
Kandidat die Erreichbarkeit traegt.

Hintergrund (Chat 116/117): Die erste Fassung binarisierte am Median. Der
sichert Erreichbarkeit und erzwingt zugleich einen 50/50-Schnitt, den die
Wirklichkeit nicht hergibt — gemessen 65,1 % Uebereinstimmung und kappa 0,286
gegen 83,1 % und 0,482 bei -0.45. Der Median lag ausserdem in einem Loch der
Verteilung: zwischen -0.15 und +0.20 liegt kein einziger Rohwert.

Zeugen dieser Datei:
  * **Die kappa-Erwartungen sind von Hand gerechnet** und stehen als Literale
    im Test. Jede Tafel ist so gewaehlt, dass die Rechnung ohne Taschenrechner
    aufgeht — 0.4, 1.0, 0.0, -0.6 sind exakte Werte, keine gerundeten.
    Keine davon stammt aus `cohens_kappa`.
  * Die Formel selbst stammt aus Cohen (1960), nicht aus dem Pruefobjekt:
    po = (a+d)/n, pe = ((a+b)(a+c) + (c+d)(b+d))/n^2, kappa = (po-pe)/(1-pe).
  * Der Korpus der Nebenbedingungs-Tests ist **konstruiert**, nicht gemessen:
    Seine kappa-beste Schwelle ist per Bauart unzulaessig, und der Test prueft
    genau das mit, damit er nicht versehentlich nichts misst.
  * Die Erwartung "ein Ausfall sieht nicht aus wie eine Messung" stammt aus
    `novaberg-lesson_l_default-wie-fehlschlag.md`, nicht aus dem Code.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.kalibrierung.korpus import Turnpaar
from agents.kalibrierung.lauf import _positions_kontrolle_fahren
from agents.kalibrierung.zwischenstand import Reihenstand
from config import KALIBRIERUNG_MIN_MINDERHEIT, KALIBRIERUNG_MIN_TURNS
from ei.initiative import initiative_bit
from ei.kalibrierung import (
    Urteilspaar,
    Vierfeldertafel,
    cohens_kappa,
    positions_kontrolle,
    schwelle_pruefen,
    schwelle_suchen,
    stichprobe_indizes,
)


def _korpus_schief() -> list[Urteilspaar]:
    """Baut einen Korpus, dessen kappa-beste Schwelle unzulaessig ist.

    92 Turns, in denen der Nutzer fuehrt, mit Rohwerten von +0.10 aufwaerts;
    8 Turns, in denen er folgt, mit Rohwerten unter null. Eine Schwelle bei
    0.00 trennt sie **perfekt** — und laesst der Minderheit 8 %.

    Genau diese Lage ist der Grund fuer die Nebenbedingung: Ohne sie waere die
    beste Schwelle eine, die 92 % aller Turns auf ein Bit legt und damit die
    halbe Sektorentafel wieder schliesst.

    Vorbedingung: keine.
    Nachbedingung: 100 Paare, Rohwerte in [-0.90, +0.99].
    Fehlerfaelle: keine.

    Returns:
        Der Korpus.
    """
    # ── Verarbeitung ────────────────────────────
    paare: list[Urteilspaar] = []

    for i in range(92):
        # 0.10 bis 0.9991 in gleichmaessigen Schritten — damit jede Schwelle
        # im Raster eine vorhersagbare Zahl von Turns ueber sich hat.
        wert: float = 0.10 + i * 0.0098
        paare.append(Urteilspaar(f"fuehrt-{i}", round(wert, 4), True))

    for i in range(8):
        wert = -0.90 + i * 0.10
        paare.append(Urteilspaar(f"folgt-{i}", round(wert, 4), False))

    # ── Ausgabe ─────────────────────────────────
    return paare


def _korpus_trennbar(n: int = 80) -> list[Urteilspaar]:
    """Baut einen Korpus mit sauberer Trennung nahe -0.45 und offener Minderheit.

    Zwei Haufen: einer oberhalb der Trennstelle mit dem Urteil "fuehrt", einer
    unterhalb mit "folgt". Der Bit-0-Anteil liegt bei 70 %, die Minderheit bei
    30 % — die Nebenbedingung ist erfuellt, ohne dass der Test sie prueft.

    Vorbedingung: n >= 10.
    Nachbedingung: n Paare, davon 70 % mit `zeuge_fuehrt=True`.
    Fehlerfaelle: keine.

    Returns:
        Der Korpus.
    """
    # ── Verarbeitung ────────────────────────────
    fuehrend: int = int(n * 0.7)
    paare: list[Urteilspaar] = []

    for i in range(fuehrend):
        paare.append(Urteilspaar(f"f-{i}", round(-0.30 + i * 0.01, 4), True))

    for i in range(n - fuehrend):
        paare.append(Urteilspaar(f"g-{i}", round(-0.90 + i * 0.01, 4), False))

    # ── Ausgabe ─────────────────────────────────
    return paare


class TestCohensKappa(unittest.TestCase):
    """Vier Tafeln, vier von Hand gerechnete Ergebnisse."""

    def test_lehrbuchfall_ergibt_genau_null_komma_vier(self) -> None:
        # a=20 b=5 c=10 d=15, n=50
        # po = 35/50 = 0.7
        # pe = (25*30 + 25*20) / 2500 = 1250/2500 = 0.5
        # kappa = (0.7 - 0.5) / 0.5 = 0.4
        self.assertEqual(0.4, cohens_kappa(Vierfeldertafel(20, 5, 10, 15)))

    def test_vollstaendige_uebereinstimmung_ergibt_eins(self) -> None:
        # a=30 b=0 c=0 d=20, n=50
        # po = 1.0 ; pe = (30*30 + 20*20)/2500 = 0.52
        # kappa = 0.48/0.48 = 1.0
        self.assertEqual(1.0, cohens_kappa(Vierfeldertafel(30, 0, 0, 20)))

    def test_reiner_zufall_ergibt_null(self) -> None:
        # a=25 b=25 c=25 d=25, n=100
        # po = 0.5 ; pe = (50*50 + 50*50)/10000 = 0.5
        # kappa = 0.0
        self.assertEqual(0.0, cohens_kappa(Vierfeldertafel(25, 25, 25, 25)))

    def test_schlechter_als_zufall_wird_negativ(self) -> None:
        # a=5 b=20 c=20 d=5, n=50
        # po = 10/50 = 0.2 ; pe = (25*25 + 25*25)/2500 = 0.5
        # kappa = (0.2 - 0.5)/0.5 = -0.6
        self.assertEqual(-0.6, cohens_kappa(Vierfeldertafel(5, 20, 20, 5)))

    def test_leere_tafel_wird_laut_gemeldet(self) -> None:
        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            self.assertEqual(0.0, cohens_kappa(Vierfeldertafel()))
        self.assertIn("leere Tafel", "".join(log.output))

    def test_entartete_verteilung_meldet_undefiniertes_kappa(self) -> None:
        # Beide Lesarten legen alles auf dasselbe Bit: pe = 1.0.
        # Das ist keine perfekte Trennung, sondern eine Tafel ohne Varianz.
        with self.assertLogs("ki_server.ei.kalibrierung", level="WARNING") as log:
            self.assertEqual(0.0, cohens_kappa(Vierfeldertafel(50, 0, 0, 0)))
        self.assertIn("nicht definiert", "".join(log.output))


class TestBinarisierungIstEineQuelle(unittest.TestCase):
    """Kalibrierung und Laufzeit teilen die Regel, statt sie zu kopieren."""

    def test_schwelle_pruefen_binarisiert_wie_die_achse(self) -> None:
        # Die Tafel, die schwelle_pruefen zaehlt, muss dieselbe sein, die man
        # mit initiative_bit von Hand ausrechnet.
        paare: list[Urteilspaar] = _korpus_trennbar(80)
        kandidat = schwelle_pruefen(paare, -0.45)

        bit0_von_hand: int = sum(
            1 for p in paare if initiative_bit(p.rohwert, -0.45) == 0
        )
        self.assertEqual(
            round(bit0_von_hand / len(paare), 4), kandidat.bit0_anteil
        )


class TestSchwellensuche(unittest.TestCase):
    """Bestes kappa — aber nur unter denen, die beide Bits offen lassen."""

    def test_der_konstruierte_korpus_hat_eine_unzulaessige_kappa_spitze(self) -> None:
        # Absicherung des Tests gegen sich selbst: Waere die kappa-beste
        # Schwelle ohnehin zulaessig, pruefte der Test unten nichts.
        paare = _korpus_schief()
        alle = [schwelle_pruefen(paare, -1.0 + i * 0.05) for i in range(41)]
        beste_ohne_bedingung = max(alle, key=lambda k: k.kappa)

        self.assertFalse(beste_ohne_bedingung.zulaessig)
        self.assertLess(beste_ohne_bedingung.minderheit, KALIBRIERUNG_MIN_MINDERHEIT)

    def test_gewaehlt_wird_eine_zulaessige_schwelle(self) -> None:
        ergebnis = schwelle_suchen(_korpus_schief())

        self.assertIsNotNone(ergebnis.schwelle)
        gewaehlt = next(
            k for k in ergebnis.kandidaten if k.schwelle == ergebnis.schwelle
        )
        self.assertGreaterEqual(gewaehlt.minderheit, KALIBRIERUNG_MIN_MINDERHEIT)

    def test_die_kappa_spitze_wird_nicht_gewaehlt(self) -> None:
        # Der eigentliche Vertrag: Erreichbarkeit schlaegt kappa.
        ergebnis = schwelle_suchen(_korpus_schief())
        beste_ohne_bedingung = max(ergebnis.kandidaten, key=lambda k: k.kappa)

        self.assertNotEqual(beste_ohne_bedingung.schwelle, ergebnis.schwelle)

    def test_unter_den_zulaessigen_gewinnt_das_hoechste_kappa(self) -> None:
        ergebnis = schwelle_suchen(_korpus_schief())
        zulaessige = [k for k in ergebnis.kandidaten if k.zulaessig]

        self.assertEqual(max(k.kappa for k in zulaessige), ergebnis.kappa)

    def test_ohne_zulaessigen_kandidaten_wird_nichts_geschrieben(self) -> None:
        # Alle Rohwerte liegen zwischen zwei Rasterpunkten (0.50 und 0.55).
        # Jeder Kandidat erfasst damit entweder alle Turns oder keinen — es
        # gibt keine Schwelle, die beide Bits offen laesst. Das ist der Korpus
        # einer Nova, deren Turns sich praktisch nicht unterscheiden.
        paare = [
            Urteilspaar(f"t-{i}", round(0.51 + (i % 4) * 0.01, 4), True)
            for i in range(KALIBRIERUNG_MIN_TURNS + 5)
        ]
        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            ergebnis = schwelle_suchen(paare)

        self.assertIsNone(ergebnis.schwelle)
        self.assertIn("Minderheit", ergebnis.grund)
        self.assertIn("kein Kandidat", "".join(log.output))


class TestNebenbedingungGegenprobe(unittest.TestCase):
    """Die Gegenprobe trifft die Wirkung: ohne Bedingung kippt das Ergebnis."""

    def test_ohne_die_bedingung_gewinnt_die_randschwelle(self) -> None:
        # Das ist die Gegenprobe zu den Tests darueber, als Test formuliert:
        # Nimmt man die Nebenbedingung heraus, waehlt dieselbe Suche eine
        # Schwelle, die der Minderheit weniger als 15 % laesst. Wer die
        # Bedingung spaeter entfernt, macht damit die Tests oben rot.
        paare = _korpus_schief()

        with patch("ei.kalibrierung.KALIBRIERUNG_MIN_MINDERHEIT", 0.0):
            ohne = schwelle_suchen(paare)

        mit = schwelle_suchen(paare)

        self.assertNotEqual(mit.schwelle, ohne.schwelle)
        gewaehlt_ohne = next(
            k for k in ohne.kandidaten if k.schwelle == ohne.schwelle
        )
        self.assertLess(gewaehlt_ohne.minderheit, KALIBRIERUNG_MIN_MINDERHEIT)
        self.assertGreater(ohne.kappa, mit.kappa)


class TestFallzahl(unittest.TestCase):
    """Zu wenig Grundlage heisst: nicht schreiben, und es sagen."""

    def test_unter_der_mindestzahl_keine_schwelle(self) -> None:
        paare = _korpus_trennbar(KALIBRIERUNG_MIN_TURNS - 1)

        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            ergebnis = schwelle_suchen(paare)

        self.assertIsNone(ergebnis.schwelle)
        self.assertEqual(KALIBRIERUNG_MIN_TURNS - 1, ergebnis.n)
        self.assertIn("keine Kalibrierung", "".join(log.output))

    def test_ab_der_mindestzahl_wird_kalibriert(self) -> None:
        # Der positive Zwilling zur Negativ-Zusicherung darueber: Ohne ihn
        # bestuende der Test auch dann, wenn die Suche nie etwas liefert.
        ergebnis = schwelle_suchen(_korpus_trennbar(KALIBRIERUNG_MIN_TURNS))

        self.assertIsNotNone(ergebnis.schwelle)
        self.assertEqual(KALIBRIERUNG_MIN_TURNS, ergebnis.n)
        self.assertEqual("", ergebnis.grund)

    def test_rohwert_ausserhalb_des_bereichs_verwirft_den_lauf(self) -> None:
        paare = _korpus_trennbar(KALIBRIERUNG_MIN_TURNS)
        paare[3].rohwert = 1.7

        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            ergebnis = schwelle_suchen(paare)

        self.assertIsNone(ergebnis.schwelle)
        self.assertIn("ausserhalb", "".join(log.output))


class TestPositionsKontrolle(unittest.TestCase):
    """Ein Zeuge, der nur die Reihenfolge liest, faellt durch."""

    def test_gemessene_werte_aus_chat_116_bestehen(self) -> None:
        # Die Zahlen sind die gemessenen: 79,5 % gegen 36,1 %.
        bestanden, text = positions_kontrolle(0.795, 0.361)

        self.assertTrue(bestanden)
        self.assertIn("43", text)

    def test_umgekehrte_richtung_besteht_ebenfalls(self) -> None:
        # Gemessen am 29.07.2026 mit einem nachgebauten Zeugen: 20,0 % gegen
        # 90,0 %. Er unterscheidet die Sprecher staerker als der aus Chat 116
        # — nur andersherum. Ob er inhaltlich richtig liegt, sagt diese
        # Kontrolle nicht; dass er nicht positionsblind ist, sehr wohl.
        bestanden, text = positions_kontrolle(0.20, 0.90)

        self.assertTrue(bestanden)
        self.assertIn("70", text)

    def test_positionsblinder_zeuge_faellt_durch(self) -> None:
        # Beide Richtungen gleich: Das Modell sagt "der zweite fuehrt",
        # unabhaengig davon, wer der zweite ist.
        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            bestanden, _ = positions_kontrolle(0.80, 0.78)

        self.assertFalse(bestanden)
        self.assertIn("unterscheidet die Sprecher nicht", "".join(log.output))

    def test_anteil_ausserhalb_des_bereichs_faellt_durch(self) -> None:
        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR"):
            bestanden, text = positions_kontrolle(1.4, 0.3)

        self.assertFalse(bestanden)
        self.assertIn("ausserhalb", text)


class TestStichprobeStreut(unittest.TestCase):
    """Die Probe kommt aus dem ganzen Korpus, nicht aus seiner aeltesten Ecke.

    Zeuge dieser Klasse: Die Viertel-Erwartung stammt aus der Messung vom
    31.07.2026, nicht aus dem Pruefobjekt — ueber die 30 aeltesten von 127
    Turnpaaren urteilte der Zeuge zu 50,0 % "Nutzer fuehrt", ueber alle 127
    zu 65,4 %. Eine Auswahl, die nur den Anfang sieht, misst diese Ecke.
    """

    def test_jedes_viertel_des_korpus_ist_vertreten(self) -> None:
        """Die Probe erreicht jedes Viertel des Korpus."""
        # Die eigentliche Zusicherung. 127 und 30 sind die gemessenen Groessen
        # des Laufs vom 30.07.2026.
        indizes = stichprobe_indizes(127, 30)

        self.assertEqual(30, len(indizes))
        for viertel in range(4):
            unten, oben = viertel * 127 / 4, (viertel + 1) * 127 / 4
            treffer = [i for i in indizes if unten <= i < oben]
            self.assertTrue(
                treffer,
                f"Viertel {viertel + 1} ({unten:.0f}-{oben:.0f}) nicht vertreten",
            )

    def test_indizes_sind_aufsteigend_und_im_korpus(self) -> None:
        """Die Indizes sind aufsteigend, doppelungsfrei und im Korpus."""
        indizes = stichprobe_indizes(127, 30)

        self.assertEqual(sorted(set(indizes)), indizes)
        self.assertGreaterEqual(indizes[0], 0)
        self.assertLess(indizes[-1], 127)

    def test_gleiche_eingabe_gleiche_probe(self) -> None:
        """Zweimal gezogen ergibt dieselbe Probe."""
        # Deterministisch: Ein Wiederanlauf muss dieselbe Menge treffen, sonst
        # beschreibt das abgelegte Ergebnis eine andere Stichprobe.
        self.assertEqual(stichprobe_indizes(127, 30), stichprobe_indizes(127, 30))

    def test_probe_groesser_als_korpus_nimmt_alles(self) -> None:
        """Ist die Probe groesser als der Korpus, kommt alles hinein."""
        self.assertEqual(list(range(12)), stichprobe_indizes(12, 30))

    def test_probe_genau_so_gross_wie_korpus_nimmt_alles(self) -> None:
        """Probe genau so gross wie der Korpus: alles, ohne Luecke."""
        self.assertEqual(list(range(30)), stichprobe_indizes(30, 30))

    def test_knappe_probe_zieht_kein_paar_doppelt(self) -> None:
        """Bei Schritt knapp ueber 1 wird kein Paar zweimal gezogen."""
        # Schritt knapp ueber 1 — der Fall, in dem eine Rundung zwei Bloecke
        # auf dasselbe Paar legen wuerde.
        indizes = stichprobe_indizes(31, 30)

        self.assertEqual(30, len(indizes))
        self.assertEqual(30, len(set(indizes)))

    def test_einzelne_probe_nimmt_nicht_die_aelteste_zeile(self) -> None:
        """Eine Einzelprobe trifft die Mitte, nicht den Anfang."""
        # Randfall groesse = 1. Bei einem driftenden Korpus waere Index 0 die
        # schlechteste aller Einzelproben.
        self.assertEqual([63], stichprobe_indizes(127, 1))

    def test_leerer_korpus_wird_laut_gemeldet(self) -> None:
        """Ein leerer Korpus liefert nichts und wird laut gemeldet."""
        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            indizes = stichprobe_indizes(0, 30)

        self.assertEqual([], indizes)
        self.assertIn("leeren Korpus", "".join(log.output))

    def test_probengroesse_null_wird_laut_gemeldet(self) -> None:
        """Eine Probengroesse von null wird laut gemeldet."""
        with self.assertLogs("ki_server.ei.kalibrierung", level="ERROR") as log:
            indizes = stichprobe_indizes(127, 0)

        self.assertEqual([], indizes)
        self.assertIn("keine Probe", "".join(log.output))


class TestPositionsKontrolleZiehtGestreut(unittest.TestCase):
    """Der Aufrufer legt dem Zeugen die gestreute Probe vor, nicht das Praefix.

    **Diese Klasse prueft die Verdrahtung, nicht den Baustein.** Der Defekt
    sass nie in einer Rechenfunktion, sondern in `paare[:30]` — eine Auswahl
    mit sauberen Tests haette ihn nicht gefunden.

    Zeuge: die Turn-Kennungen, die der Zeuge tatsaechlich zu sehen bekam. Sie
    stammen aus der Attrappe, nicht aus dem Pruefobjekt.
    """

    def _paare(self, anzahl: int) -> list:
        """Baut einen Korpus, dessen Kennung die Position im Korpus traegt."""
        return [
            Turnpaar(
                turn_id     = f"turn-{i:03d}",
                user_prompt = f"Nutzer {i}",
                user_modus  = "sachlich",
                vor_antwort = f"Nova {i}",
                vor_modus   = "sachlich",
                intentionen = [],
            )
            for i in range(anzahl)
        ]

    def _gesehene_indizes(self) -> list[int]:
        """Faehrt die Kontrolle und gibt zurueck, welche Paare befragt wurden."""
        gesehen: list[int] = []

        def _zeuge(text_a: str, text_b: str) -> bool:
            # B = Nutzer traegt "Nutzer <i>", B = Nova traegt "Nova <i>".
            gesehen.append(int(text_b.split()[-1]))
            return True

        stand = Reihenstand(urteile={}, gescheitert=set(), aggregate={})

        with patch("agents.kalibrierung.lauf.zeuge_befragen", side_effect=_zeuge), \
             patch("agents.kalibrierung.lauf.aggregat_schreiben"):
            _positions_kontrolle_fahren(self._paare(127), "test-reihe", stand)

        return sorted(set(gesehen))

    def test_der_zeuge_sieht_paare_aus_jedem_viertel(self) -> None:
        """Der Zeuge bekommt Paare aus jedem Viertel vorgelegt."""
        gesehen = self._gesehene_indizes()

        self.assertEqual(30, len(gesehen))
        for viertel in range(4):
            unten, oben = viertel * 127 / 4, (viertel + 1) * 127 / 4
            self.assertTrue(
                [i for i in gesehen if unten <= i < oben],
                f"Viertel {viertel + 1} wurde dem Zeugen nie vorgelegt",
            )

    def test_der_zeuge_sieht_auch_das_juengste_drittel(self) -> None:
        """Der Zeuge sieht auch das juengste Drittel des Korpus."""
        # Die Zusicherung, die gegen `paare[:30]` rot wird: Bei 127 Paaren
        # endet ein Praefix von 30 bei Index 29 und erreicht das juengste
        # Drittel (ab 85) nie.
        gesehen = self._gesehene_indizes()

        self.assertTrue([i for i in gesehen if i >= 85])


if __name__ == "__main__":
    unittest.main()
