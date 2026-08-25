"""Tests für die Versionierung im Dokument (`tools/dateien/versionierung.py`).

Ziel: Was überschrieben wird, ist nicht weg — es steht mit Marke, Version und
Datum im Archivblock, und der Verlauf ist umkehrbar.

Die fünf Zusicherungen, die hier geprüft werden:

  1. **Jede Marke hat genau einen Eintrag und umgekehrt.** Das ist der
     einzige Detektor, den dieser Bereich hat; auf dem Inhalt einer
     Wissensdatei steht kein Zeuge. Geprüft wird beidseitig — und die
     Gegenprobe zerstört die Paarung absichtlich, damit belegt ist, dass die
     Prüfung anschlägt statt nur mitzulaufen.
  2. **Archiveinträge tragen selbst Marken.** Ein Absatz, der geändert und
     später gelöscht wurde, hält beide Vorgänge in einer Kette.
  3. **Die Position sagt, ob eine Fassung lebt.** Nach dem Löschen steht die
     Änderungsmarke nur noch im Archiv, nicht mehr im laufenden Text.
  4. **Ein Insert trägt keinen Rumpf, bekommt aber einen Eintrag.** Ohne ihn
     wäre ein fehlender Eintrag nicht mehr von einem erlaubten Fall zu
     unterscheiden — und die Invariante aus 1 wäre keine mehr.
  5. **Der Zähler läuft je Datei.** Sonst kollidieren zwei Marken im Archiv.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.dateien.versionierung import (
    ARCHIVBLOCK,
    LEBENDBLOCK,
    Fassung,
    absatz_aendern,
    absatz_einfuegen,
    absatz_loeschen,
    aktuell_lesen,
    marken_finden,
    paarung_pruefen,
    verlauf_lesen,
)

VORLAGE: str = """# Der 30-jaehrige Krieg

**Erstellt:** 17.08.2026

---

## Der Kriegsverlauf

Die schwedische Phase begann 1631.

Gustav Adolf fiel bei Luetzen.

## Folgen

Der Westfaelische Friede beendete den Krieg 1648.
"""


class VersionierungTest(unittest.TestCase):
    """Eingriffe gegen eine angelegte Datei."""

    def setUp(self) -> None:
        """Legt Wurzel und Prüfdatei an."""
        self.wurzel = Path(tempfile.mkdtemp(prefix="version_test_"))
        self.datei = self.wurzel / "krieg.md"
        self.datei.write_text(VORLAGE, encoding="utf-8")
        self.f22 = Fassung("2.2", "2026-08-16")
        self.f23 = Fassung("2.3", "2026-08-17")

    def tearDown(self) -> None:
        """Räumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _text(self) -> str:
        """Liest die Prüfdatei."""
        return self.datei.read_text(encoding="utf-8")

    def _laufend(self) -> str:
        """Nur der laufende Text, ohne Archivblock."""
        return self._text().split(ARCHIVBLOCK)[0]

    # ── Zusicherung 1: die Paarung ──────────────────────────────

    def test_aenderung_erzeugt_marke_und_eintrag(self) -> None:
        ergebnis = absatz_aendern(
            self.datei, self.wurzel,
            "Die schwedische Phase begann 1631.",
            "Die schwedische Phase begann 1630.",
            self.f22,
        )
        self.assertTrue(ergebnis["erfolg"])
        self.assertEqual(ergebnis["marke"], "[c1>]")
        self.assertIn("[c1>]", self._laufend())
        self.assertIn("[<c1_2.2_2026-08-16]", self._text())

    def test_paarung_ist_nach_dem_eingriff_vollstaendig(self) -> None:
        absatz_aendern(
            self.datei, self.wurzel,
            "Gustav Adolf fiel bei Luetzen.",
            "Gustav Adolf fiel vermutlich bei Luetzen.",
            self.f22,
        )
        bericht = paarung_pruefen(self.datei, self.wurzel)
        self.assertEqual(bericht["befunde"], [])
        self.assertEqual(bericht["marken"], 1)
        self.assertEqual(bericht["eintraege"], 1)

    def test_gegenprobe_marke_ohne_eintrag_wird_gefunden(self) -> None:
        """Zerstört die Paarung absichtlich — sonst prüft der Test oben nichts."""
        absatz_aendern(
            self.datei, self.wurzel,
            "Gustav Adolf fiel bei Luetzen.", "Anders.", self.f22,
        )
        verstuemmelt = self._text().replace("[<c1_2.2_2026-08-16]", "[<c9_2.2_2026-08-16]")
        self.datei.write_text(verstuemmelt, encoding="utf-8")
        bericht = paarung_pruefen(self.datei, self.wurzel)
        arten = {b["art"] for b in bericht["befunde"]}
        self.assertIn("marke_ohne_eintrag", arten)
        self.assertIn("eintrag_ohne_marke", arten)

    def test_gegenprobe_typwiderspruch_wird_gefunden(self) -> None:
        absatz_aendern(
            self.datei, self.wurzel,
            "Gustav Adolf fiel bei Luetzen.", "Anders.", self.f22,
        )
        verstuemmelt = self._text().replace("[<c1_", "[<d1_")
        self.datei.write_text(verstuemmelt, encoding="utf-8")
        bericht = paarung_pruefen(self.datei, self.wurzel)
        self.assertIn("typ_widerspruch", {b["art"] for b in bericht["befunde"]})

    def test_unberuehrte_datei_hat_keine_befunde(self) -> None:
        bericht = paarung_pruefen(self.datei, self.wurzel)
        self.assertEqual(bericht["befunde"], [])
        self.assertEqual(bericht["marken"], 0)

    # ── Zusicherung 2 und 3: die Kette ──────────────────────────

    def test_geaenderter_absatz_kann_geloescht_werden_und_haelt_beide_vorgaenge(self) -> None:
        absatz_aendern(
            self.datei, self.wurzel,
            "Die schwedische Phase begann 1631.",
            "Die schwedische Phase begann 1630.",
            self.f22,
        )
        geaendert = "Die schwedische Phase begann 1630. [c1>]"
        self.assertIn(geaendert, self._laufend())

        ergebnis = absatz_loeschen(self.datei, self.wurzel, geaendert, self.f23)
        self.assertTrue(ergebnis["erfolg"])

        # Zusicherung 3: die Aenderungsmarke lebt nicht mehr im Text …
        self.assertNotIn("[c1>]", self._laufend())
        self.assertIn("[d2>]", self._laufend())
        # … sondern im Rumpf des Loescheintrags — das ist die Kette.
        eintraege = {e["nummer"]: e for e in verlauf_lesen(self.datei, self.wurzel)}
        self.assertIn("[c1>]", eintraege[2]["rumpf"])
        self.assertEqual(eintraege[2]["typ"], "d")
        self.assertEqual(eintraege[1]["typ"], "c")

    def test_paarung_bleibt_ueber_die_kette_vollstaendig(self) -> None:
        absatz_aendern(
            self.datei, self.wurzel,
            "Die schwedische Phase begann 1631.", "Neu.", self.f22,
        )
        absatz_loeschen(self.datei, self.wurzel, "Neu. [c1>]", self.f23)
        self.assertEqual(paarung_pruefen(self.datei, self.wurzel)["befunde"], [])

    def test_juengster_eintrag_steht_oben(self) -> None:
        absatz_aendern(self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.", self.f22)
        absatz_aendern(self.datei, self.wurzel, "Der Westfaelische Friede beendete den Krieg 1648.", "B.", self.f23)
        eintraege = verlauf_lesen(self.datei, self.wurzel)
        self.assertEqual(eintraege[0]["nummer"], 2)
        self.assertEqual(eintraege[0]["version"], "2.3")

    # ── Zusicherung 4: Insert ohne Rumpf, aber mit Eintrag ──────

    def test_insert_erzeugt_eintrag_mit_leerem_rumpf(self) -> None:
        ergebnis = absatz_einfuegen(
            self.datei, self.wurzel, "Ein neuer Absatz.", self.f23,
        )
        self.assertTrue(ergebnis["erfolg"])
        self.assertIn("[i1>]", self._laufend())
        eintraege = verlauf_lesen(self.datei, self.wurzel)
        self.assertEqual(eintraege[0]["typ"], "i")
        self.assertEqual(eintraege[0]["rumpf"], "")
        self.assertEqual(paarung_pruefen(self.datei, self.wurzel)["befunde"], [])

    def test_insert_hinter_einem_vorbild(self) -> None:
        absatz_einfuegen(
            self.datei, self.wurzel, "Nachbemerkung.", self.f23,
            nach="Gustav Adolf fiel bei Luetzen.",
        )
        laufend = self._laufend()
        self.assertLess(
            laufend.index("Gustav Adolf"), laufend.index("Nachbemerkung."),
        )

    def test_insert_mit_unbekanntem_vorbild_ist_ein_ergebnis(self) -> None:
        vorher = self._text()
        ergebnis = absatz_einfuegen(
            self.datei, self.wurzel, "X", self.f23, nach="steht nicht drin",
        )
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "nicht_gefunden")
        self.assertEqual(self._text(), vorher)

    # ── Zusicherung 5: der Zähler läuft je Datei ────────────────

    def test_zaehler_laeuft_ueber_bloecke_hinweg(self) -> None:
        absatz_aendern(self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.", self.f22)
        absatz_aendern(
            self.datei, self.wurzel,
            "Der Westfaelische Friede beendete den Krieg 1648.", "B.", self.f23,
        )
        nummern = sorted(n for _, n in marken_finden(self._laufend()))
        self.assertEqual(nummern, [1, 2])
        self.assertEqual(paarung_pruefen(self.datei, self.wurzel)["befunde"], [])

    def test_drei_eingriffe_ergeben_drei_verschiedene_nummern(self) -> None:
        absatz_aendern(self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.", self.f22)
        absatz_loeschen(self.datei, self.wurzel, "A. [c1>]", self.f23)
        absatz_einfuegen(self.datei, self.wurzel, "Ganz neu.", self.f23)
        bericht = paarung_pruefen(self.datei, self.wurzel)
        self.assertEqual(bericht["befunde"], [])
        self.assertEqual(bericht["eintraege"], 3)

    # ── Randfälle ───────────────────────────────────────────────

    def test_mehrdeutiger_absatz_ist_ein_ergebnis_und_aendert_nichts(self) -> None:
        self.datei.write_text(
            "# T\n\nGleicher Satz.\n\nGleicher Satz.\n", encoding="utf-8",
        )
        vorher = self._text()
        ergebnis = absatz_aendern(
            self.datei, self.wurzel, "Gleicher Satz.", "Anders.", self.f22,
        )
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "nicht_eindeutig")
        self.assertEqual(self._text(), vorher)

    def test_leere_version_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            absatz_aendern(
                self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.",
                Fassung("  ", "2026-08-17"),
            )

    def test_unformatiertes_datum_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            absatz_aendern(
                self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.",
                Fassung("2.2", "17.08.2026"),
            )

    def test_leerzeile_vor_dem_archivblock(self) -> None:
        """Ohne sie liest ein Parser die Überschrift als Teil des Absatzes —
        dann wäre der Archivblock über die Karte nicht mehr auffindbar.
        """
        absatz_einfuegen(self.datei, self.wurzel, "Ein Zusatz.", self.f23)
        zeilen = self._text().splitlines()
        i = zeilen.index(ARCHIVBLOCK)
        self.assertEqual(zeilen[i - 1], "", "vor der Archivüberschrift fehlt die Leerzeile")
        self.assertNotEqual(zeilen[i - 2], "", "es sind zwei Leerzeilen statt einer")

    def test_archivblock_bleibt_ueber_die_karte_auffindbar(self) -> None:
        """Die Gegenprobe zur Leerzeile: der Block muss ein Block bleiben."""
        from tools.dateien.operationen import struktur_analysieren
        absatz_aendern(self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.", self.f22)
        header = [b["header"] for b in struktur_analysieren(self.datei, self.wurzel)]
        self.assertIn(ARCHIVBLOCK, header)

    def test_aktuell_lesen_liefert_den_text_ohne_historie(self) -> None:
        """Der Zugriff, den ein Leser fast immer will: was gilt, nicht was galt."""
        absatz_aendern(self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.", self.f22)
        lebend = aktuell_lesen(self.datei, self.wurzel)
        self.assertIn("A. [c1>]", lebend)
        self.assertNotIn(ARCHIVBLOCK, lebend)
        self.assertNotIn("Gustav Adolf", lebend)

    def test_aktuell_lesen_funktioniert_ohne_historie(self) -> None:
        """Eine unberührte Datei hat keinen Historienblock — der lebende Teil
        ist dann die ganze Datei.
        """
        lebend = aktuell_lesen(self.datei, self.wurzel)
        self.assertIn("Der Westfaelische Friede", lebend)

    def test_die_beiden_bloecke_sind_ein_paar(self) -> None:
        """AKTUELL und HISTORIE sagen beide, was der andere ist."""
        self.assertEqual(LEBENDBLOCK, "## AKTUELL")
        self.assertEqual(ARCHIVBLOCK, "## HISTORIE")

    def test_archiv_liegt_hinter_dem_laufenden_text(self) -> None:
        absatz_aendern(self.datei, self.wurzel, "Gustav Adolf fiel bei Luetzen.", "A.", self.f22)
        text = self._text()
        self.assertLess(text.index("## Folgen"), text.index(ARCHIVBLOCK))


if __name__ == "__main__":
    unittest.main()
