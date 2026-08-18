"""Tests für die Hand (`tools/dateien/hand.py`) — Novas eigener Schreibweg.

Ziel: Sie kann einen Auftrag stellen, und was dabei schiefgeht, kommt als
Antwort zurück, die sie lesen und beantworten kann.

Die vier Zusicherungen, die hier geprüft werden:

  1. **Kein Fehlgriff wird zur Ausnahme.** Unbekannte Aktion, fehlendes Feld,
     Anker nicht gefunden, Pfad außerhalb der Zone — alles kommt mit
     `erfolg=False` und einem Hinweis zurück. Das ist die Bedingung dafür,
     dass ein zweiter Versuch möglich ist; eine Ausnahme beendet den Turn.
  2. **Die Zone begrenzt.** Ein Auftrag auf eine Datei außerhalb der Wurzel
     wird abgewiesen, und die Datei bleibt unverändert.
  3. **Der Auftragsleser überlebt echte Nutzlasten.** `alt` und `neu` tragen
     regelmäßig Anführungszeichen, Gedankenstriche, Zeilenumbrüche und
     geschweifte Klammern — ein naiver Klammerzähler zerschnitte genau die
     Aufträge, auf die es ankommt.
  4. **Jede Änderung über die Hand ist versioniert.** Nach dem Eingriff steht
     eine Marke im Text und ein Eintrag im Archiv.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.dateien.hand import (
    AKTIONEN,
    antwort_formulieren,
    auftrag_ausfuehren,
    auftrag_lesen,
)
from tools.dateien.versionierung import paarung_pruefen

VORLAGE: str = """# Quarks

**Erstellt:** 17.08.2026

---

## Aufbau

Quarks treten immer gebunden auf.

## Offene Fragen

Die Massehierarchie ist ungeklaert.
"""


class AuftragLesenTest(unittest.TestCase):
    """Zusicherung 3 — der Leser überlebt echte Nutzlasten."""

    def test_einfacher_auftrag(self) -> None:
        auftrag = auftrag_lesen('DATEI: {"aktion": "karte", "pfad": "a.md"}')
        self.assertEqual(auftrag, {"aktion": "karte", "pfad": "a.md"})

    def test_auftrag_mit_anfuehrungszeichen_im_text(self) -> None:
        roh = json.dumps({
            "aktion": "aendern", "pfad": "a.md",
            "alt": 'Er sagte "so ist es" und ging.',
            "neu": 'Er sagte "so scheint es" und ging.',
            "version": "2.1",
        }, ensure_ascii=False)
        auftrag = auftrag_lesen(f"DATEI: {roh}")
        self.assertIsNotNone(auftrag)
        self.assertIn('"so ist es"', auftrag["alt"])

    def test_auftrag_mit_geschweifter_klammer_im_text(self) -> None:
        """Ein naiver Klammerzähler bräche genau hier."""
        roh = json.dumps({
            "aktion": "aendern", "pfad": "a.md",
            "alt": "Die Menge {a, b} ist endlich.",
            "neu": "Die Menge {a, b, c} ist endlich.",
            "version": "2.1",
        }, ensure_ascii=False)
        auftrag = auftrag_lesen(f"DATEI: {roh}")
        self.assertIsNotNone(auftrag)
        self.assertEqual(auftrag["alt"], "Die Menge {a, b} ist endlich.")

    def test_text_hinter_dem_objekt_stoert_nicht(self) -> None:
        auftrag = auftrag_lesen(
            'DATEI: {"aktion": "karte", "pfad": "a.md"}  — ich sehe mal nach.',
        )
        self.assertEqual(auftrag["aktion"], "karte")

    def test_zeile_ohne_marke_ist_kein_auftrag(self) -> None:
        self.assertIsNone(auftrag_lesen("Ich denke gerade nach."))

    def test_kaputtes_json_ist_kein_absturz(self) -> None:
        self.assertIsNone(auftrag_lesen('DATEI: {"aktion": "karte", '))

    def test_json_das_kein_objekt_ist(self) -> None:
        self.assertIsNone(auftrag_lesen('DATEI: ["karte"]'))


class HandTest(unittest.TestCase):
    """Ausführung gegen eine angelegte Zone."""

    def setUp(self) -> None:
        """Legt Wurzel und Prüfdatei an."""
        self.wurzel = Path(tempfile.mkdtemp(prefix="hand_test_"))
        self.datei = self.wurzel / "quarks.md"
        self.datei.write_text(VORLAGE, encoding="utf-8")

    def tearDown(self) -> None:
        """Räumt die Wurzel ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _tun(self, **auftrag: object) -> dict:
        """Führt einen Auftrag auf der Prüfdatei aus."""
        auftrag.setdefault("pfad", str(self.datei))
        return auftrag_ausfuehren(auftrag, self.wurzel)

    # ── Zusicherung 1: kein Fehlgriff wird zur Ausnahme ─────────

    def test_unbekannte_aktion_nennt_die_moeglichen(self) -> None:
        ergebnis = self._tun(aktion="radieren")
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "unbekannte_aktion")
        for name in AKTIONEN:
            self.assertIn(name, ergebnis["hinweis"])

    def test_fehlendes_feld_nennt_den_bestand(self) -> None:
        ergebnis = self._tun(aktion="aendern", alt="x", version="1.0")
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "feld_fehlt")
        self.assertIn("neu", ergebnis["hinweis"])

    def test_fehlende_version_beim_schreiben(self) -> None:
        ergebnis = self._tun(aktion="aendern", alt="x", neu="y")
        self.assertFalse(ergebnis["erfolg"])
        self.assertIn("version", ergebnis["hinweis"])

    def test_anker_nicht_gefunden_ist_beantwortbar(self) -> None:
        ergebnis = self._tun(
            aktion="aendern", alt="steht nicht drin", neu="x", version="2.1",
        )
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "nicht_gefunden")
        self.assertIn("zeichengenau", ergebnis["hinweis"].lower())

    def test_unbekannter_header_wird_abgewiesen_nicht_geworfen(self) -> None:
        ergebnis = self._tun(aktion="block", header="## Gibt Es Nicht")
        self.assertFalse(ergebnis["erfolg"])
        self.assertEqual(ergebnis["grund"], "abgewiesen")

    def test_jede_antwort_traegt_erfolg(self) -> None:
        for aktion in AKTIONEN:
            with self.subTest(aktion=aktion):
                self.assertIn("erfolg", self._tun(aktion=aktion, version="1.0"))

    # ── Zusicherung 2: die Zone begrenzt ────────────────────────

    def test_pfad_ausserhalb_der_zone_wird_abgewiesen(self) -> None:
        fremd = Path(tempfile.mkdtemp(prefix="hand_fremd_"))
        try:
            ziel = fremd / "fremd.md"
            ziel.write_text(VORLAGE, encoding="utf-8")
            ergebnis = auftrag_ausfuehren(
                {"aktion": "aendern", "pfad": str(ziel),
                 "alt": "Quarks treten immer gebunden auf.",
                 "neu": "Anders.", "version": "2.1"},
                self.wurzel,
            )
            self.assertFalse(ergebnis["erfolg"])
            self.assertEqual(ergebnis["grund"], "abgewiesen")
            self.assertEqual(ziel.read_text(encoding="utf-8"), VORLAGE)
        finally:
            shutil.rmtree(fremd, ignore_errors=True)

    # ── Zusicherung 4: die Hand versioniert ─────────────────────

    def test_aendern_hinterlaesst_marke_und_eintrag(self) -> None:
        ergebnis = self._tun(
            aktion="aendern",
            alt="Die Massehierarchie ist ungeklaert.",
            neu="Die Massehierarchie gilt als weitgehend ungeklaert.",
            version="2.1", datum="2026-08-17",
        )
        self.assertTrue(ergebnis["erfolg"])
        text = self.datei.read_text(encoding="utf-8")
        self.assertIn("[c1>]", text)
        self.assertIn("[<c1_2.1_2026-08-17]", text)
        self.assertEqual(paarung_pruefen(self.datei, self.wurzel)["befunde"], [])

    def test_loeschen_und_einfuegen_ueber_die_hand(self) -> None:
        self._tun(
            aktion="loeschen", absatz="Quarks treten immer gebunden auf.",
            version="2.1", datum="2026-08-17",
        )
        self._tun(
            aktion="einfuegen", absatz="Quarks sind bislang nur gebunden beobachtet.",
            version="2.2", datum="2026-08-17",
        )
        bericht = paarung_pruefen(self.datei, self.wurzel)
        self.assertEqual(bericht["befunde"], [])
        self.assertEqual(bericht["eintraege"], 2)

    # ── Lesen ───────────────────────────────────────────────────

    def test_karte_liefert_die_bloecke(self) -> None:
        ergebnis = self._tun(aktion="karte")
        self.assertTrue(ergebnis["erfolg"])
        header = [b["header"] for b in ergebnis["bloecke"]]
        self.assertIn("## Aufbau", header)

    def test_suchen_liefert_fundstellen(self) -> None:
        ergebnis = self._tun(aktion="suchen", begriff="Massehierarchie")
        self.assertTrue(ergebnis["erfolg"])
        self.assertEqual(ergebnis["anzahl"], 1)

    def test_verlauf_ist_vor_dem_ersten_eingriff_leer(self) -> None:
        ergebnis = self._tun(aktion="verlauf")
        self.assertTrue(ergebnis["erfolg"])
        self.assertEqual(ergebnis["eintraege"], [])

    # ── Die Antwort, die sie liest ──────────────────────────────

    def test_antwort_bei_fehlschlag_nennt_grund_und_hinweis(self) -> None:
        text = antwort_formulieren(self._tun(aktion="radieren"))
        self.assertIn("unbekannte_aktion", text)
        self.assertIn("karte", text)

    def test_antwort_bei_erfolg_ist_lesbares_json(self) -> None:
        text = antwort_formulieren(self._tun(aktion="karte"))
        self.assertTrue(text.startswith("Datei-Werkzeug: "))
        json.loads(text.split("Datei-Werkzeug: ", 1)[1])

    def test_antwort_ohne_erfolgsfeld_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            antwort_formulieren({"bloecke": []})


if __name__ == "__main__":
    unittest.main()
