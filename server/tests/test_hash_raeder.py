"""Tests: Der Hash-Endpunkt liefert die zwei Charakter-Raeder mit Herkunft.

Ziel: Ein Rad, das nicht gelesen werden konnte, erreicht die Anzeige als
**nicht lesbar** und nicht als Rad voller Nullen. Der Unterschied ist der
ganze Zweck der Herkunftsfelder (`novaberg-gv-initiative_k.md` §6.4): Ein
Versatz von 0.00, weil sich zehn Speichen aufheben, ist eine Messung; ein
Versatz von 0.00, weil das JSON kaputt war, ist ein Ausfall.

Warum an dieser Stelle geprueft wird: Genau hier lag
`KALIBRIER-INTENTIONEN-UNGEPARST`. Ein JSON-Feld wurde ungeparst
weitergereicht, sah am Ziel wie ein Wert aus und liess M1 zwei Monate als
Konstante laufen — mit gruener Suite, weil niemand die Eingangsgrenze
geprueft hat.

Zeugen dieser Datei:
  * **Die Speichennamen sind der Vertrag mit dem Client.** Das
    Charakter-Panel zeichnet zwoelf bzw. zehn Achsen und liest sie **nach
    Namen** aus dem JSON. Wird eine Speiche serverseitig umbenannt, zeigt
    das Diagramm still eine Null — kein Fehler, kein Log, ein plausibles
    Bild. `VertragMitDemClientTest` haelt die Namen deshalb woertlich fest.
    Wer eine Speiche umbenennt, macht diesen Test rot und weiss dann, dass
    `client/ui/panels/character_panel.py` mitwandern muss.
  * **Geprueft wird `lesbar`, nicht der Wert.** Der gerechnete Faktor ist
    in `test_charakter_rad.py` abgedeckt; hier geht es allein darum, ob die
    Anzeige Messung von Ausfall unterscheiden kann.
  * Die Zeitstempel sind fest gesetzt, damit `erhoben_am` eine pruefbare
    Zeichenkette ist und kein Fenster.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import datetime
import json
import unittest

from agents.charakter.destillation import (
    INITIATIVE_RAD_LEER,
    INITIATIVE_ZUG_HOCH,
    INITIATIVE_ZUG_RUNTER,
    RAD_LEER,
    RAD_ZUG_HOCH,
    RAD_ZUG_RUNTER,
)
from api.gedaechtnis import _hash_leer, _rad_aufbereiten

GEDAECHTNIS_LOGGER: str = "ki_server.gedaechtnis"

# Fester Zeitpunkt — ein `NOW()` im Test misst die Uhr, nicht den Code.
ERHOBEN: datetime.datetime = datetime.datetime(
    2026, 7, 30, 19, 59, 9, tzinfo=datetime.timezone.utc,
)


class LesbarkeitTest(unittest.TestCase):
    """`lesbar` trennt Messung, Ausfall und fehlende Zeile."""

    def test_vollstaendiges_rad_ist_lesbar(self) -> None:
        """Ein gelieferter Rad-Block traegt Wert, Herkunft und beide Seiten."""
        block: dict = _rad_aufbereiten(
            "zuwendung", json.dumps(RAD_LEER), 0.9, "destilliert", ERHOBEN,
        )
        self.assertTrue(block["lesbar"])
        self.assertEqual(block["quelle"], "destilliert")
        self.assertEqual(block["wert"], 0.9)
        self.assertEqual(block["rad"]["hoch"].keys(), RAD_ZUG_HOCH.keys())

    def test_leeres_rad_ist_eine_messung_und_kein_ausfall(self) -> None:
        """Alle Speichen auf 0.0 ist ein Ergebnis — `lesbar` bleibt wahr.

        Der Unterschied zum Ausfall steht in `quelle`, nicht in `lesbar`.
        """
        block: dict = _rad_aufbereiten(
            "zuwendung", json.dumps(RAD_LEER), 0.9, "destilliert", ERHOBEN,
        )
        self.assertTrue(block["lesbar"])
        self.assertTrue(all(v == 0.0 for v in block["rad"]["hoch"].values()))

    def test_kaputtes_json_wird_nicht_zum_leeren_rad(self) -> None:
        """Unlesbares JSON meldet sich als Ausfall, nicht als Rad ohne Auspraegung."""
        with self.assertLogs(GEDAECHTNIS_LOGGER, level="ERROR"):
            block: dict = _rad_aufbereiten(
                "zuwendung", "{kein json", 0.9, "destilliert", ERHOBEN,
            )
        self.assertFalse(block["lesbar"])
        self.assertEqual(block["rad"], {})
        # Der Wert bleibt erhalten: Er stammt aus einer eigenen Spalte und
        # ist nicht deshalb falsch, weil die Herleitung unlesbar wurde.
        self.assertEqual(block["wert"], 0.9)

    def test_leere_spalte_meldet_sich(self) -> None:
        """Eine leere Spalte ist keine Erhebung und sagt das auch."""
        with self.assertLogs(GEDAECHTNIS_LOGGER, level="WARNING"):
            block: dict = _rad_aufbereiten(
                "initiative", "", 0.0, "default", None,
            )
        self.assertFalse(block["lesbar"])
        self.assertEqual(block["erhoben_am"], "")

    def test_json_ohne_die_beiden_seiten_ist_nicht_lesbar(self) -> None:
        """Geparst heisst nicht brauchbar — 'hoch' und 'runter' muessen da sein."""
        with self.assertLogs(GEDAECHTNIS_LOGGER, level="ERROR"):
            block: dict = _rad_aufbereiten(
                "zuwendung", json.dumps({"speichen": []}), 1.2, "destilliert", ERHOBEN,
            )
        self.assertFalse(block["lesbar"])

    def test_json_das_kein_objekt_ist_ist_nicht_lesbar(self) -> None:
        """Eine Liste ist gueltiges JSON und trotzdem kein Rad."""
        with self.assertLogs(GEDAECHTNIS_LOGGER, level="ERROR"):
            block: dict = _rad_aufbereiten(
                "zuwendung", json.dumps([1, 2, 3]), 1.2, "destilliert", ERHOBEN,
            )
        self.assertFalse(block["lesbar"])

    def test_zeitstempel_wird_als_iso_gereicht(self) -> None:
        """Der Erhebungszeitpunkt reist als ISO-Zeichenkette, nicht als Objekt."""
        block: dict = _rad_aufbereiten(
            "zuwendung", json.dumps(RAD_LEER), 0.9, "destilliert", ERHOBEN,
        )
        self.assertEqual(block["erhoben_am"], "2026-07-30T19:59:09+00:00")

    def test_zusatzfelder_des_initiative_rades_ueberleben(self) -> None:
        """`laeufe` und `streuung` stehen im Rad und duerfen nicht wegfallen.

        Sie sind heute ohne Anzeige, aber sie sind die Streuung ueber
        mehrere Erhebungen — ein Verlust hier waere unbemerkt.
        """
        # Synthetische Laeufe. Echte Rad-Werte sind ein Charakterprofil und
        # gehoeren auch als Testdatum nicht ins oeffentliche Repositorium.
        rad: dict = dict(INITIATIVE_RAD_LEER)
        rad["laeufe"] = [-0.11, -0.09, -0.07]
        rad["streuung"] = 0.02

        block: dict = _rad_aufbereiten(
            "initiative", json.dumps(rad), -0.09, "destilliert", ERHOBEN,
        )
        self.assertTrue(block["lesbar"])
        self.assertEqual(block["rad"]["laeufe"], [-0.11, -0.09, -0.07])
        self.assertEqual(block["rad"]["streuung"], 0.02)


class LeereAntwortTest(unittest.TestCase):
    """Ein Paar ohne Zeile liefert beide Rad-Bloecke, beide als nicht lesbar."""

    def test_beide_raeder_sind_vorhanden_und_leer(self) -> None:
        """Der Client liest beide Schluessel unbedingt — sie fehlen nie."""
        antwort: dict = _hash_leer()
        for schluessel in ("zuwendung", "initiative"):
            self.assertIn(schluessel, antwort)
            self.assertFalse(antwort[schluessel]["lesbar"])
            self.assertIsNone(antwort[schluessel]["wert"])
            self.assertEqual(antwort[schluessel]["rad"], {})

    def test_die_fuenf_profile_bleiben_im_leeren_fall_erhalten(self) -> None:
        """Der Client liest sie unbedingt — ein fehlender Schluessel waere ein KeyError."""
        antwort: dict = _hash_leer()
        for schluessel in (
            "kern_hash", "adaptive_hash", "intentions_profil",
            "emotions_profil", "beziehungsprofil",
            "kern_aktualisiert", "adaptive_aktualisiert",
            "intentions_aktualisiert", "emotions_aktualisiert",
            "beziehung_aktualisiert",
        ):
            self.assertIn(schluessel, antwort)

    def test_die_beiden_bloecke_sind_getrennte_objekte(self) -> None:
        """Sonst faerbt eine Aenderung am einen Rad das andere mit ein."""
        antwort: dict = _hash_leer()
        antwort["zuwendung"]["wert"] = 1.11
        self.assertIsNone(antwort["initiative"]["wert"])


class VertragMitDemClientTest(unittest.TestCase):
    """Die Speichennamen, die das Charakter-Panel nach Namen aus dem JSON liest.

    Diese Listen sind eine **Kopie** der Definition in
    `client/ui/panels/character_panel.py`. Der Client liegt ausserhalb des
    Server-Abbilds und kann hier nicht importiert werden; ohne diesen Test
    gaebe es zwischen beiden Seiten gar keine Verbindung ausser der
    Hoffnung. Wird eine Speiche hier rot, ist nicht der Test falsch — dann
    ist der Client nachzuziehen.
    """

    ZUWENDUNG_HOCH: tuple[str, ...] = (
        "treue", "dienst", "pflicht", "aufmerksamkeit", "wissbegier", "wohlwollen",
    )
    ZUWENDUNG_RUNTER: tuple[str, ...] = (
        "widerspenstig", "gleichgueltig", "selbstbezogen",
        "langeweile", "distanz", "misstrauen",
    )
    INITIATIVE_HOCH: tuple[str, ...] = (
        "folgsamkeit", "anschlussfreude", "zurueckhaltung",
        "antwortende_rolle", "behutsamkeit",
    )
    INITIATIVE_RUNTER: tuple[str, ...] = (
        "lenkungsdrang", "eigensinn", "assoziationsdrang",
        "widerspruchsfreude", "gespraechsdistanz",
    )

    def test_zuwendung_hoch_heisst_wie_der_client_erwartet(self) -> None:
        """Die sechs Zuwendungs-Speichen, wie das Panel sie sucht."""
        self.assertEqual(tuple(RAD_ZUG_HOCH), self.ZUWENDUNG_HOCH)

    def test_zuwendung_runter_heisst_wie_der_client_erwartet(self) -> None:
        """Die sechs Abwendungs-Speichen, wie das Panel sie sucht."""
        self.assertEqual(tuple(RAD_ZUG_RUNTER), self.ZUWENDUNG_RUNTER)

    def test_initiative_hoch_heisst_wie_der_client_erwartet(self) -> None:
        """Die fuenf Speichen der Folgen-Seite, wie das Panel sie sucht."""
        self.assertEqual(tuple(INITIATIVE_ZUG_HOCH), self.INITIATIVE_HOCH)

    def test_initiative_runter_heisst_wie_der_client_erwartet(self) -> None:
        """Die fuenf Speichen der Fuehrungs-Seite, wie das Panel sie sucht."""
        self.assertEqual(tuple(INITIATIVE_ZUG_RUNTER), self.INITIATIVE_RUNTER)

    def test_das_panel_zeichnet_zwoelf_und_zehn_achsen(self) -> None:
        """Die Achsenzahl des Widgets kommt aus der Laenge dieser Listen."""
        self.assertEqual(
            len(self.ZUWENDUNG_HOCH) + len(self.ZUWENDUNG_RUNTER), 12,
        )
        self.assertEqual(
            len(self.INITIATIVE_HOCH) + len(self.INITIATIVE_RUNTER), 10,
        )

    def test_ein_ausgeliefertes_rad_traegt_jede_erwartete_speiche(self) -> None:
        """Die Verdrahtung: Was der Endpunkt liefert, muss der Client finden."""
        block: dict = _rad_aufbereiten(
            "zuwendung", json.dumps(RAD_LEER), 0.9, "destilliert", ERHOBEN,
        )
        for name in self.ZUWENDUNG_HOCH:
            self.assertIn(name, block["rad"]["hoch"])
        for name in self.ZUWENDUNG_RUNTER:
            self.assertIn(name, block["rad"]["runter"])


if __name__ == "__main__":
    unittest.main()
