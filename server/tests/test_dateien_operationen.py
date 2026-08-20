"""Tests für die Leseschicht des Dateizugriffs (`tools/dateien/operationen.py`).

Ziel: Nova kann eine Datei navigieren, ohne sie ganz zu laden — Karte, Block,
Fenster, Fundstelle —, und jeder Zugriff bleibt innerhalb einer ausdrücklich
genannten Wurzel.

Die vier Zusicherungen, die hier geprüft werden:

  1. **Die Wurzel begrenzt.** Ein Pfad, der nach der Auflösung außerhalb
     liegt, wird abgewiesen — auch über `..` und über eine symbolische
     Verknüpfung. Die Auflösung geschieht vor der Prüfung.
  2. **Überschriften in Codeblöcken sind keine Überschriften.** Sonst trägt
     die Karte Blockgrenzen, die im Text nicht existieren.
  3. **Eine Datei ohne Blockstruktur liefert eine leere Karte**, keinen
     erfundenen Ein-Block. Das ist der Normalfall im Bestand: gemessen am
     17.08.2026 tragen 223 von 223 Wissensdateien keine `##`-Überschrift.
  4. **Ein mehrdeutiger Header ist ein Fehler, kein Griff zum ersten
     Treffer.** Sonst liefert derselbe Aufruf morgen einen anderen Block.
  5. **Eine Karte, die nicht erhoben werden konnte, ist keine leere Karte.**
     Ein Format ohne Erkenner und eine Datei mit unschlüssiger Auszeichnung
     werfen — sonst sagt der Index über eine ungelesene Datei aus, sie sei
     ein durchgehender Text. Gemessen am 20.08.2026 an einer echten Datei:
     ein einzelner durchgestrichener Codezaun ließ von 83 Überschriften 5
     übrig, und nichts daran sah nach einem Fehler aus.

Die Zeugen:

  * Die Randfälle laufen gegen **angelegte** Dateien in einem eigenen
    Verzeichnis — nur so sind Codezaun, Mehrdeutigkeit und die leere Datei
    gezielt herstellbar.
  * Zusätzlich fährt ein Zeuge den **echten Bestand** (`knowledge/`), weil
    eine Nachbildung genau die Eigenschaft nicht hat, die den Bau ausgelöst
    hat: dass dort keine Blöcke stehen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.dateien.operationen import (
    BLOCK_LIMIT,
    GREP_LIMIT,
    FormatOhneErkennerError,
    StrukturDefektError,
    block_lesen,
    datei_grep,
    datei_suchen,
    metadaten_lesen,
    pfad_pruefen,
    struktur_analysieren,
    zeilen_lesen,
)

MIT_BLOECKEN: str = """# Titel der Datei

**Erstellt:** 04.08.2026
**Modus:** recherche

---

## Erster Block

Ein Satz im ersten Block.
Noch ein Satz.

### Unterblock

Text im Unterblock.

## Zweiter Block

Ein Satz im zweiten Block.
"""

MIT_CODEZAUN: str = """# Titel

## Echter Block

Hier folgt Beispielcode:

```markdown
## Das ist KEINE Ueberschrift
# Das auch nicht
```

Nach dem Zaun geht es weiter.

## Zweiter echter Block

Ende.
"""

OHNE_BLOECKE: str = """# Bewusstsein, Entropie, aesthetische Erfahrung

**Erstellt:** 04.08.2026
**Recherchiert fuer:** meister
**Modus:** recherche

---

Ein Absatz Fliesstext ohne jede Unterteilung.

Noch ein Absatz. So sehen die Wissensdateien im Bestand aus.
"""

ZWEIMAL_GLEICH: str = """# Titel

## Anmerkungen

Erster Vorkommen.

## Anmerkungen

Zweites Vorkommen.
"""


DEFEKTER_ZAUN: str = """# Titel

## Erster echter Block

Ein Satz.

~~```
veralteter Code
```~~

## Zweiter echter Block

Noch ein Satz.

### Ein Unterblock

Und noch einer.
"""

FREMDFORMAT_RST: str = """Titel der Datei
===============

Ein Absatz.

Ein Abschnitt
-------------

Noch ein Absatz.
"""


class LeseschichtTest(unittest.TestCase):
    """Randfälle gegen angelegte Dateien."""

    def setUp(self) -> None:
        """Legt ein Wurzelverzeichnis mit den Prüfdateien an."""
        self.wurzel = Path(tempfile.mkdtemp(prefix="dateien_test_"))
        self.mit      = self._schreiben("mit_bloecken.md", MIT_BLOECKEN)
        self.zaun     = self._schreiben("mit_codezaun.md", MIT_CODEZAUN)
        self.ohne     = self._schreiben("ohne_bloecke.md", OHNE_BLOECKE)
        self.doppelt  = self._schreiben("zweimal_gleich.md", ZWEIMAL_GLEICH)
        self.leer     = self._schreiben("leer.md", "")
        # Der echte Fall vom 20.08.2026: Ein durchgestrichener Codeblock. Das
        # OEFFNENDE Gegenstueck steht hinter den beiden Tilden und wird vom
        # Erkenner nicht gesehen, das schliessende beginnt mit dem Zaun und
        # wird gesehen — eine ungerade Bilanz.
        self.defekt   = self._schreiben("defekter_zaun.md", DEFEKTER_ZAUN)
        self.fremd    = self._schreiben("fremdformat.rst", FREMDFORMAT_RST)
        self.lang     = self._schreiben(
            "lang.md",
            "# Titel\n\n## Grosser Block\n\n"
            + "\n".join(f"Zeile {i}" for i in range(1, 501)),
        )

    def tearDown(self) -> None:
        """Räumt das Wurzelverzeichnis ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _schreiben(self, name: str, inhalt: str) -> Path:
        """Legt eine Prüfdatei an und gibt ihren Pfad zurück."""
        ziel: Path = self.wurzel / name
        ziel.write_text(inhalt, encoding="utf-8")
        return ziel

    # ── Zusicherung 1: die Wurzel begrenzt ──────────────────────

    def test_pfad_ausserhalb_der_wurzel_wird_abgewiesen(self) -> None:
        with self.assertRaises(ValueError) as fall:
            pfad_pruefen(self.mit, self.wurzel / "unterordner")
        self.assertIn("ausserhalb der Wurzel", str(fall.exception))

    def test_ausbruch_ueber_punkt_punkt_wird_abgewiesen(self) -> None:
        """`..` muss VOR der Prüfung aufgelöst werden, sonst greift sie nicht."""
        unterordner: Path = self.wurzel / "unten"
        unterordner.mkdir()
        ausbruch: Path = unterordner / ".." / "mit_bloecke_n.md"
        with self.assertRaises(ValueError):
            pfad_pruefen(ausbruch, unterordner)

    def test_symbolische_verknuepfung_nach_aussen_wird_abgewiesen(self) -> None:
        fremd: Path = Path(tempfile.mkdtemp(prefix="dateien_fremd_"))
        try:
            ziel: Path = fremd / "geheim.md"
            ziel.write_text("# Fremd\n", encoding="utf-8")
            verknuepfung: Path = self.wurzel / "zeiger.md"
            verknuepfung.symlink_to(ziel)
            with self.assertRaises(ValueError) as fall:
                pfad_pruefen(verknuepfung, self.wurzel)
            self.assertIn("ausserhalb der Wurzel", str(fall.exception))
        finally:
            shutil.rmtree(fremd, ignore_errors=True)

    def test_fehlende_datei_ist_ein_fehler_kein_leerergebnis(self) -> None:
        with self.assertRaises(ValueError) as fall:
            pfad_pruefen(self.wurzel / "gibtsnicht.md", self.wurzel)
        self.assertIn("keine lesbare Datei", str(fall.exception))

    # ── Zusicherung 2: Codezaun ─────────────────────────────────

    def test_ueberschrift_im_codezaun_zaehlt_nicht(self) -> None:
        bloecke = struktur_analysieren(self.zaun, self.wurzel)
        header = [b["header"] for b in bloecke]
        self.assertIn("## Echter Block", header)
        self.assertIn("## Zweiter echter Block", header)
        self.assertNotIn("## Das ist KEINE Ueberschrift", header)
        self.assertNotIn("# Das auch nicht", header)

    def test_gegenprobe_ohne_zaunerkennung_waeren_es_mehr(self) -> None:
        """Belegt, dass der Zaun wirklich etwas entfernt — sonst prüft der
        Test oben nichts."""
        roh = self.zaun.read_text(encoding="utf-8").splitlines()
        naiv = [z for z in roh if z.startswith("#")]
        bloecke = struktur_analysieren(self.zaun, self.wurzel)
        self.assertEqual(len(naiv), 5)
        self.assertEqual(len(bloecke), 3)

    # ── Zusicherung 2b: eine unschluessige Bilanz ist ein Fehler ─

    def test_ungerader_codezaun_scheitert_laut(self) -> None:
        """Der Fall, der am 20.08.2026 78 von 83 Blöcken verschluckt hat."""
        with self.assertRaises(StrukturDefektError) as fall:
            struktur_analysieren(self.defekt, self.wurzel)
        self.assertIn("ungerade", str(fall.exception))

    def test_gegenprobe_ohne_bilanzpruefung_kaeme_eine_halbe_karte(self) -> None:
        """Belegt, dass der Zeuge oben etwas fängt, was sonst durchginge.

        Ohne die Prüfung liefert derselbe Text eine Karte mit genau den
        Blöcken **vor** dem Zaun — hier zwei von vier. Das ist der Grund,
        warum die halbierte Karte nie auffiel: Sie ist syntaktisch gültig
        und sieht aus wie eine kurze Datei.
        """
        zeilen = self.defekt.read_text(encoding="utf-8").splitlines()
        vorhanden = [z for z in zeilen if z.startswith("#")]
        # Der Erkenner ohne Bilanzpruefung, nachgebaut:
        im_zaun, gefunden = False, []
        for zeile in zeilen:
            if zeile.lstrip().startswith(("```", "~~~")) and zeile.startswith(("```", "~~~")):
                im_zaun = not im_zaun
                continue
            if not im_zaun and zeile.startswith("#"):
                gefunden.append(zeile)
        self.assertEqual(len(vorhanden), 4)
        self.assertEqual(len(gefunden), 2)

    # ── Zusicherung 5: nicht erhoben ist nicht leer ─────────────

    def test_format_ohne_erkenner_scheitert_laut(self) -> None:
        """Eine .rst-Datei ist gegliedert — nur nicht mit Rautenzeichen."""
        with self.assertRaises(FormatOhneErkennerError) as fall:
            struktur_analysieren(self.fremd, self.wurzel)
        self.assertIn(".rst", str(fall.exception))

    def test_gegenprobe_fremdformat_haette_leere_karte_geliefert(self) -> None:
        """Belegt, was der Zeuge oben verhindert: die stille Falschaussage.

        Der Markdown-Erkenner findet in der .rst-Datei keine einzige
        Überschrift, obwohl sie zwei trägt. Ohne die Endungsprüfung wäre das
        Ergebnis eine leere Karte — also die Aussage *„durchgehender Text"*
        über eine gegliederte Datei.
        """
        zeilen = self.fremd.read_text(encoding="utf-8").splitlines()
        mit_raute = [z for z in zeilen if z.startswith("#")]
        unterstrichen = [
            z for z in zeilen if z and set(z) <= set("=-") and len(z) > 2
        ]
        self.assertEqual(mit_raute, [])
        self.assertEqual(len(unterstrichen), 2)

    # ── Zusicherung 3: keine Struktur ist ein Befund ────────────

    def test_datei_ohne_bloecke_liefert_nur_den_titel(self) -> None:
        bloecke = struktur_analysieren(self.ohne, self.wurzel)
        self.assertEqual(len(bloecke), 1)
        self.assertEqual(bloecke[0]["ebene"], 1)

    def test_leere_datei_liefert_leere_karte(self) -> None:
        self.assertEqual(struktur_analysieren(self.leer, self.wurzel), [])

    def test_zeilen_lesen_traegt_die_datei_ohne_struktur(self) -> None:
        ergebnis = zeilen_lesen(self.ohne, self.wurzel, 1, 5)
        self.assertEqual(ergebnis["gelesen_von"], 1)
        self.assertEqual(ergebnis["gelesen_bis"], 5)
        self.assertIn("Bewusstsein", ergebnis["inhalt"])

    def test_zeilen_lesen_ueber_das_dateiende_kappt_und_weist_es_aus(self) -> None:
        ergebnis = zeilen_lesen(self.ohne, self.wurzel, 1, 9999)
        self.assertEqual(ergebnis["gelesen_bis"], ergebnis["datei_zeilen"])
        self.assertEqual(ergebnis["rest"], 0)

    # ── Zusicherung 4: Mehrdeutigkeit ist ein Fehler ────────────

    def test_mehrdeutiger_header_scheitert_laut(self) -> None:
        with self.assertRaises(ValueError) as fall:
            block_lesen(self.doppelt, self.wurzel, "## Anmerkungen")
        self.assertIn("2-mal", str(fall.exception))

    def test_unbekannter_header_nennt_die_vorhandenen(self) -> None:
        with self.assertRaises(ValueError) as fall:
            block_lesen(self.mit, self.wurzel, "## Gibt Es Nicht")
        self.assertIn("Erster Block", str(fall.exception))

    # ── Blockgrenzen und Fenster ────────────────────────────────

    def test_block_endet_vor_der_naechsten_gleichrangigen_ueberschrift(self) -> None:
        bloecke = {b["header"]: b for b in struktur_analysieren(self.mit, self.wurzel)}
        erster = bloecke["## Erster Block"]
        zweiter = bloecke["## Zweiter Block"]
        self.assertLess(erster["ende"], zweiter["start"])

    def test_unterblock_liegt_im_elternblock(self) -> None:
        bloecke = {b["header"]: b for b in struktur_analysieren(self.mit, self.wurzel)}
        eltern = bloecke["## Erster Block"]
        kind = bloecke["### Unterblock"]
        self.assertGreater(kind["start"], eltern["start"])
        self.assertLessEqual(kind["ende"], eltern["ende"])

    def test_grosser_block_wird_gefenstert_und_meldet_den_rest(self) -> None:
        ergebnis = block_lesen(self.lang, self.wurzel, "## Grosser Block")
        self.assertEqual(ergebnis["gelesen_bis"] - ergebnis["gelesen_von"], BLOCK_LIMIT)
        self.assertGreater(ergebnis["rest"], 0)

    def test_zweites_fenster_setzt_am_rest_an(self) -> None:
        erstes = block_lesen(self.lang, self.wurzel, "## Grosser Block")
        zweites = block_lesen(
            self.lang, self.wurzel, "## Grosser Block", offset=erstes["gelesen_bis"],
        )
        self.assertEqual(zweites["gelesen_von"], BLOCK_LIMIT)
        self.assertNotEqual(erstes["inhalt"], zweites["inhalt"])

    def test_ungueltiges_fenster_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            block_lesen(self.mit, self.wurzel, "## Erster Block", limit=0)

    # ── Fundstelle ──────────────────────────────────────────────

    def test_grep_liefert_zeilennummern(self) -> None:
        ergebnis = datei_grep(self.mit, self.wurzel, "zweiten Block")
        self.assertEqual(ergebnis["anzahl"], 1)
        nummer, zeile = ergebnis["treffer"][0]
        self.assertIn("zweiten Block", zeile)
        roh = self.mit.read_text(encoding="utf-8").splitlines()
        self.assertEqual(roh[nummer - 1], zeile)

    def test_grep_kappt_und_weist_die_kappung_aus(self) -> None:
        ergebnis = datei_grep(self.lang, self.wurzel, "Zeile")
        self.assertTrue(ergebnis["gekappt"])
        self.assertEqual(len(ergebnis["treffer"]), GREP_LIMIT)
        self.assertGreater(ergebnis["anzahl"], GREP_LIMIT)

    def test_grep_mit_ungueltigem_muster_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            datei_grep(self.mit, self.wurzel, "[unvollstaendig", regex=True)

    # ── Metadaten und Suche ─────────────────────────────────────

    def test_metadaten_werden_nur_aus_dem_kopf_gelesen(self) -> None:
        felder = metadaten_lesen(self.mit, self.wurzel)
        self.assertEqual(felder["Erstellt"], "04.08.2026")
        self.assertEqual(felder["Modus"], "recherche")

    def test_datei_suchen_findet_nach_muster(self) -> None:
        treffer = datei_suchen(self.wurzel, self.wurzel, "*bloecke*.md")
        self.assertEqual(len(treffer), 2)
        self.assertTrue(all(t.endswith(".md") for t in treffer))

    def test_datei_suchen_trennt_aehnliche_namen(self) -> None:
        """Das Muster ist wörtlich, nicht ungefähr: `*_bloecke.md` trifft
        `ohne_bloecke.md` und gerade nicht `mit_bloecken.md`."""
        treffer = datei_suchen(self.wurzel, self.wurzel, "*_bloecke.md")
        self.assertEqual(len(treffer), 1)
        self.assertTrue(treffer[0].endswith("ohne_bloecke.md"))

    def test_datei_suchen_ausserhalb_der_wurzel_scheitert(self) -> None:
        with self.assertRaises(ValueError):
            datei_suchen(self.wurzel.parent, self.wurzel, "*.md")


class BestandTest(unittest.TestCase):
    """Ein Zeuge, der den echten Bestand fährt statt seiner Nachbildung.

    Die Eigenschaft, die den Bau ausgelöst hat — Wissensdateien ohne
    Blockstruktur —, ist in einer Nachbildung genau die, die man versehentlich
    wegbaut.
    """

    WURZEL = Path("/knowledge")

    def setUp(self) -> None:
        """Sucht eine echte Wissensdatei; ohne Bestand ist der Zeuge rot."""
        self.dateien = sorted((self.WURZEL / "autonomous").rglob("*_wissen.md"))
        self.assertTrue(
            self.dateien,
            f"Kein Bestand unter {self.WURZEL}/autonomous — der Zeuge kann "
            f"nicht prüfen, was er prüfen soll",
        )

    def test_neue_wissensdateien_tragen_bloecke(self) -> None:
        """Umgedreht am 18.08.2026 — die Zusicherung ist erfüllt.

        Bis dahin hielt dieser Zeuge den Befund fest: **223 von 223**
        Wissensdateien ohne `##`-Überschrift, während 461 von 462 übrigen
        Dateien welche trugen. Seit die Schreibvorlage einen Block erzwingt
        (`wissen_text_bauen`), gilt das Gegenteil für jede neu geschriebene
        Datei — belegt an 9 Dateien, die der Recherche-Pfad nach der
        Änderung selbst angelegt hat.

        **Der Zeuge ist nicht gelöscht, sondern umgedreht** (`20_TESTS` §4g):
        Er prüft jetzt, dass keine Datei mehr *ohne* Block entsteht. Die
        Altbestände bleiben blocklos und sind kein Fehler — sie stammen von
        vor der Änderung und werden nicht rückwirkend umgeschrieben.
        """
        mit_version = [
            p for p in self.dateien
            if "**Version:**" in p.read_text(encoding="utf-8")
        ]
        self.assertTrue(
            mit_version,
            "Keine einzige Wissensdatei trägt eine Versionszeile — die "
            "Schreibvorlage greift nicht mehr",
        )
        ohne_block = [
            p for p in mit_version
            if not any(b["ebene"] >= 2 for b in struktur_analysieren(p, self.WURZEL))
        ]
        self.assertEqual(
            ohne_block, [],
            f"{len(ohne_block)} von {len(mit_version)} neu geschriebenen "
            f"Wissensdateien haben keinen adressierbaren Block",
        )

    def test_karte_und_zeilenlesen_greifen_auf_echtem_bestand(self) -> None:
        probe = self.dateien[0]
        bloecke = struktur_analysieren(probe, self.WURZEL)
        self.assertGreaterEqual(len(bloecke), 1)
        ergebnis = zeilen_lesen(probe, self.WURZEL, 1, 3)
        self.assertTrue(ergebnis["inhalt"])
        self.assertGreater(ergebnis["datei_zeilen"], 0)


if __name__ == "__main__":
    unittest.main()
