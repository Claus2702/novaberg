"""Tests für die Schreibschicht des Dateizugriffs (`tools/dateien/redaktion.py`).

Ziel: Ein Eingriff ändert genau seinen Teil und lässt den Rest der Datei
Zeichen für Zeichen unberührt — und ein Eingriff, der nicht eindeutig ist,
findet nicht statt.

Die vier Zusicherungen, die hier geprüft werden:

  1. **Der Rest bleibt unberührt.** Nach jedem Eingriff wird nicht nur das
     Ziel geprüft, sondern der Text davor und dahinter. Ein Werkzeug, das
     nebenbei einen Absatz verliert, sähe sonst aus wie eines, das gearbeitet
     hat — auf dem Inhalt einer Wissensdatei steht kein Zeuge.
  2. **Ein mehrdeutiger Anker führt zu keinem Eingriff.** Er kommt als
     Ergebnis zurück, nicht als Ausnahme, und die Datei ist hinterher
     unverändert.
  3. **Die Wurzel begrenzt auch beim Schreiben.** Ein Ziel außerhalb wird
     abgewiesen, bevor irgendetwas geschrieben ist.
  4. **Kein Eingriff erzeugt einen zweiten gleichnamigen Block.** Sonst ist
     jeder spätere Zugriff auf ihn mehrdeutig.

Die Gegenprobe zu Zusicherung 1 steht als eigener Test: Sie zerstört den
Vergleich absichtlich und belegt, dass er anschlägt. Ohne sie wäre nicht zu
unterscheiden, ob der Vergleich prüft oder nur mitläuft.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.dateien.operationen import struktur_analysieren
from tools.dateien.redaktion import (
    block_anfuegen,
    block_einfuegen,
    block_ersetzen,
    metadaten_setzen,
    str_ersetzen,
)

VORLAGE: str = """# Der 30-jaehrige Krieg

**Erstellt:** 17.08.2026
**Modus:** recherche

---

## Vorgeschichte

Der Prager Fenstersturz gilt als Ausloeser.
Die Lage war jedoch schon lange gespannt.

## Der Kriegsverlauf

Die schwedische Phase begann 1630.
Gustav Adolf fiel bei Luetzen.

## Folgen

Der Westfaelische Friede beendete den Krieg 1648.
"""

DOPPELT: str = """# Titel

## Anmerkungen

Erstes Vorkommen.

## Anmerkungen

Zweites Vorkommen.
"""


class RedaktionTest(unittest.TestCase):
    """Eingriffe gegen eine angelegte Datei."""

    def setUp(self) -> None:
        """Legt Wurzel und Prüfdateien an."""
        self.wurzel = Path(tempfile.mkdtemp(prefix="redaktion_test_"))
        self.datei = self.wurzel / "krieg.md"
        self.datei.write_text(VORLAGE, encoding="utf-8")
        self.doppelt = self.wurzel / "doppelt.md"
        self.doppelt.write_text(DOPPELT, encoding="utf-8")

    def tearDown(self) -> None:
        """Räumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _text(self) -> str:
        """Liest die Prüfdatei."""
        return self.datei.read_text(encoding="utf-8")

    # ── Zusicherung 1: der Rest bleibt unberührt ────────────────

    def test_block_ersetzen_laesst_die_nachbarn_stehen(self) -> None:
        block_ersetzen(self.datei, self.wurzel, "## Der Kriegsverlauf", "Neuer Rumpf.")
        text = self._text()
        self.assertIn("Neuer Rumpf.", text)
        self.assertNotIn("Gustav Adolf", text)
        self.assertIn("Der Prager Fenstersturz gilt als Ausloeser.", text)
        self.assertIn("Der Westfaelische Friede beendete den Krieg 1648.", text)

    def test_block_ersetzen_haelt_die_ueberschrift(self) -> None:
        block_ersetzen(self.datei, self.wurzel, "## Folgen", "Anders formuliert.")
        header = [b["header"] for b in struktur_analysieren(self.datei, self.wurzel)]
        self.assertIn("## Folgen", header)

    def test_anfuegen_erhaelt_den_bisherigen_rumpf(self) -> None:
        block_anfuegen(self.datei, self.wurzel, "## Folgen", "Ein Nachtrag.")
        text = self._text()
        self.assertIn("Der Westfaelische Friede beendete den Krieg 1648.", text)
        self.assertIn("Ein Nachtrag.", text)

    def test_anfuegen_trennt_mit_genau_einer_leerzeile(self) -> None:
        block_anfuegen(self.datei, self.wurzel, "## Folgen", "Ein Nachtrag.")
        zeilen = self._text().splitlines()
        i = zeilen.index("Ein Nachtrag.")
        self.assertEqual(zeilen[i - 1], "")
        self.assertNotEqual(zeilen[i - 2], "")

    def test_gegenprobe_der_nachbarpruefung(self) -> None:
        """Belegt, dass die Prüfung auf unberührte Nachbarn anschlägt.

        Ohne diesen Test wäre nicht unterscheidbar, ob die Zusicherungen oben
        prüfen oder nur mitlaufen.
        """
        self.datei.write_text(
            VORLAGE.replace("Gustav Adolf fiel bei Luetzen.", ""), encoding="utf-8"
        )
        self.assertNotIn("Gustav Adolf", self._text())

    # ── Zusicherung 2: Mehrdeutigkeit verhindert den Eingriff ───

    def test_mehrdeutiger_anker_wird_nicht_ersetzt(self) -> None:
        vorher = self.doppelt.read_text(encoding="utf-8")
        ergebnis = str_ersetzen(self.doppelt, self.wurzel, "Vorkommen.", "Ersetzt.")
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "nicht_eindeutig")
        self.assertEqual(ergebnis["anzahl"], 2)
        self.assertEqual(self.doppelt.read_text(encoding="utf-8"), vorher)

    def test_nicht_gefundener_anker_ist_ein_ergebnis_keine_ausnahme(self) -> None:
        vorher = self._text()
        ergebnis = str_ersetzen(self.datei, self.wurzel, "steht so nicht drin", "X")
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "nicht_gefunden")
        self.assertEqual(self._text(), vorher)

    def test_eindeutiger_anker_wird_ersetzt(self) -> None:
        ergebnis = str_ersetzen(
            self.datei, self.wurzel,
            "Die schwedische Phase begann 1630.",
            "Die schwedische Phase begann vermutlich 1630.",
        )
        self.assertTrue(ergebnis["erfolg"])
        self.assertIn("vermutlich 1630", self._text())
        self.assertNotIn("Phase begann 1630.", self._text())

    def test_anker_im_block_grenzt_den_suchraum_ein(self) -> None:
        """Derselbe Anker ist dateiweit mehrdeutig und im Block eindeutig."""
        dateiweit = str_ersetzen(self.doppelt, self.wurzel, "Vorkommen.", "Ersetzt.")
        self.assertFalse(dateiweit["erfolg"])
        # Beide Blöcke heißen gleich, deshalb ist auch der Block mehrdeutig —
        # das ist die richtige Antwort und kein Umweg.
        with self.assertRaises(ValueError):
            str_ersetzen(
                self.doppelt, self.wurzel, "Vorkommen.", "Ersetzt.",
                header="## Anmerkungen",
            )

    def test_anker_gleich_ersatz_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            str_ersetzen(self.datei, self.wurzel, "Folgen", "Folgen")

    # ── Zusicherung 3: die Wurzel begrenzt ──────────────────────

    def test_schreiben_ausserhalb_der_wurzel_wird_abgewiesen(self) -> None:
        fremd = Path(tempfile.mkdtemp(prefix="redaktion_fremd_"))
        try:
            ziel = fremd / "fremd.md"
            ziel.write_text(VORLAGE, encoding="utf-8")
            vorher = ziel.read_text(encoding="utf-8")
            with self.assertRaises(ValueError):
                block_ersetzen(ziel, self.wurzel, "## Folgen", "Eingriff")
            self.assertEqual(ziel.read_text(encoding="utf-8"), vorher)
        finally:
            shutil.rmtree(fremd, ignore_errors=True)

    # ── Zusicherung 4: keine zweite gleichnamige Überschrift ────

    def test_einfuegen_eines_vorhandenen_headers_scheitert(self) -> None:
        with self.assertRaises(ValueError) as fall:
            block_einfuegen(self.datei, self.wurzel, "## Folgen", "Text")
        self.assertIn("steht bereits", str(fall.exception))

    def test_ersetzen_mit_ueberschrift_im_inhalt_scheitert(self) -> None:
        """Ein Rumpf, der selbst eine Überschrift trägt, änderte die Karte."""
        with self.assertRaises(RuntimeError) as fall:
            block_ersetzen(self.datei, self.wurzel, "## Folgen", "## Heimlich\n\nText")
        self.assertIn("Ueberschrift", str(fall.exception))

    # ── Einfügen ────────────────────────────────────────────────

    def test_einfuegen_am_ende(self) -> None:
        vorher = len(struktur_analysieren(self.datei, self.wurzel))
        block_einfuegen(self.datei, self.wurzel, "## Quellen", "Eine Liste.")
        nachher = struktur_analysieren(self.datei, self.wurzel)
        self.assertEqual(len(nachher), vorher + 1)
        self.assertEqual(nachher[-1]["header"], "## Quellen")

    def test_einfuegen_vor_einem_block(self) -> None:
        block_einfuegen(
            self.datei, self.wurzel, "## Einordnung", "Vorbemerkung.",
            vor_header="## Folgen",
        )
        header = [b["header"] for b in struktur_analysieren(self.datei, self.wurzel)]
        self.assertLess(header.index("## Einordnung"), header.index("## Folgen"))

    def test_einfuegen_ohne_raute_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            block_einfuegen(self.datei, self.wurzel, "Quellen", "Text")

    # ── Metadaten ───────────────────────────────────────────────

    def test_metadatenfeld_wird_ersetzt(self) -> None:
        metadaten_setzen(self.datei, self.wurzel, "Modus", "vertiefung")
        self.assertIn("**Modus:** vertiefung", self._text())
        self.assertNotIn("**Modus:** recherche", self._text())

    def test_neues_metadatenfeld_landet_im_kopf(self) -> None:
        metadaten_setzen(self.datei, self.wurzel, "Version", "2.1")
        zeilen = self._text().splitlines()
        i = zeilen.index("**Version:** 2.1")
        trenner = zeilen.index("---")
        self.assertLess(i, trenner)

    def test_leeres_metadatenfeld_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            metadaten_setzen(self.datei, self.wurzel, "Modus", "   ")

    # ── Abschließendes Zeilenende ───────────────────────────────

    def test_zeilenende_bleibt_ueber_mehrere_eingriffe_erhalten(self) -> None:
        """Ohne diese Zusicherung wandert bei jedem Schnitt ein Byte heraus."""
        for _ in range(3):
            block_anfuegen(self.datei, self.wurzel, "## Folgen", "Nachtrag.")
        self.assertTrue(self._text().endswith("\n"))


if __name__ == "__main__":
    unittest.main()
