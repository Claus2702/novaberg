"""Tests fuer das Etikett einer Fundstelle (`utils/etikett.py`).

Ziel: Eine archivierte Datei sieht in der Ausgabe nicht aus wie eine
geltende. Der Index haelt beide gleich gut — der Unterschied muss an der
Fundstelle stehen, sonst zitiert die Figur ein widerrufenes Konzept in
derselben Form wie ein gueltiges.

Die Zusicherungen:

  1. **Das Verzeichnisglied entscheidet, nicht der Anfang und nicht der
     Teilstring.** `archive/x.md` und `konzepte/archive/x.md` tragen das
     Etikett, `archivelogik_k.md` und `archive.md` nicht.
  2. **Beide Ausgabewege tragen es.** Der Enricher-Weg
     (`aufzeichnungen._fundstelle_bauen`) und der lesende Dienst
     (`auskunft.fundstelle`) bauen ihre Herkunftsangabe getrennt; eine
     Regel an zwei Stellen laeuft auseinander.
  3. **Eine geltende Datei bekommt keinen Zusatz.** Der leere Text ist
     eine Aussage.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents.dateien.auskunft import fundstelle
from agents.dateien_index.aufzeichnungen import _fundstelle_bauen
from agents.wissen.auskunft import auskunft_bauen
from utils.etikett import (
    ETIKETT_ARCHIVIERT,
    etikett,
    ist_archiviert,
    mit_etikett,
)


class ErkennungTest(unittest.TestCase):
    """Welcher Pfad gilt als archiviert — und welcher nur so aussieht."""

    def test_oberste_ebene_wird_erkannt(self) -> None:
        """Der Fall, der im Bestand vorkommt: `docs/archive/`."""
        self.assertTrue(ist_archiviert("archive/novaberg-mem-lzg.md"))

    def test_tiefere_ebene_wird_erkannt(self) -> None:
        """Ein `startswith` fande diesen Fall nicht."""
        self.assertTrue(ist_archiviert("konzepte/archive/alt.md"))

    def test_geltende_datei_traegt_nichts(self) -> None:
        """Die Gegenprobe — sonst etikettierte der Riegel alles."""
        self.assertFalse(ist_archiviert("novaberg-agent-dateien_k.md"))
        self.assertEqual(etikett("novaberg-agent-dateien_k.md"), "")

    def test_namensteil_ist_kein_verzeichnis(self) -> None:
        """`archivelogik_k.md` handelt von Archiven, es liegt in keinem.

        Ein `"archive" in pfad` traefe hier — deshalb wird zerlegt.
        """
        self.assertFalse(ist_archiviert("archivelogik_k.md"))
        self.assertFalse(ist_archiviert("konzepte/archivierung_k.md"))

    def test_die_schreibung_entscheidet_nicht(self) -> None:
        """`Archiv/` ist dasselbe Verzeichnis wie `archive/`.

        Der Bestand entscheidet sonst, was ein Etikett bekommt: `/docs`
        folgt der englischen Konvention des Repositoriums, die beiden
        anderen Freigaben sind Dateibaeume von Menschen und Figuren.
        """
        for pfad in ("Archive/a.md", "ARCHIVE/a.md", "Archiv/a.md",
                     "archiv/a.md", "docs/Archiv/x/y.md"):
            with self.subTest(pfad=pfad):
                self.assertTrue(ist_archiviert(pfad))

    def test_aehnliche_namen_bleiben_draussen(self) -> None:
        """Die Gegenprobe zur Lockerung — sie darf nicht alles einsammeln."""
        for pfad in ("archives/a.md", "archivar/a.md", "arch/a.md",
                     "arch ive/a.md", "Archivierung/a.md"):
            with self.subTest(pfad=pfad):
                self.assertFalse(ist_archiviert(pfad))

    def test_die_datei_selbst_zaehlt_nicht_als_glied(self) -> None:
        """`archive.md` ist ein Dokument, kein Verzeichnis."""
        self.assertFalse(ist_archiviert("archive.md"))
        self.assertFalse(ist_archiviert("docs/archive.md"))

    def test_leerer_pfad_gilt_als_nicht_archiviert_und_meldet(self) -> None:
        """Kein stiller Uebersprung: Der Fall wird laut."""
        with self.assertLogs("ki_server.utils.etikett", "ERROR"):
            self.assertFalse(ist_archiviert("   "))


class AnhaengenTest(unittest.TestCase):
    """Wie das Etikett an eine fertige Herkunftsangabe kommt."""

    def test_archivierte_fundstelle_traegt_die_marke(self) -> None:
        """Das Etikett steht am Ort, nicht im Thema."""
        self.assertEqual(
            mit_etikett("/docs/archive/alt.md", "archive/alt.md"),
            f"/docs/archive/alt.md ({ETIKETT_ARCHIVIERT})",
        )

    def test_geltende_fundstelle_bleibt_unveraendert(self) -> None:
        """Kein Zusatz heisst: die Datei gilt."""
        self.assertEqual(
            mit_etikett("/docs/neu.md", "neu.md"), "/docs/neu.md",
        )

    def test_leere_fundstelle_wird_gemeldet(self) -> None:
        """Es gibt nichts zu etikettieren, und das wird gesagt."""
        with self.assertLogs("ki_server.utils.etikett", "ERROR"):
            self.assertEqual(mit_etikett("", "archive/alt.md"), "")


class BeideWegeTest(unittest.TestCase):
    """Die eigentliche Zusicherung: **beide** Ausgabewege tragen es.

    Der Enricher-Weg und der lesende Dienst bauen ihre Herkunftsangabe
    getrennt. Ein Zeuge, der nur einen prueft, laesst die Haelfte offen,
    die das Etikett verliert — und genau die gibt Widerrufenes als geltend
    aus.
    """

    def test_enricher_weg_traegt_das_etikett(self) -> None:
        """`aufzeichnungen._fundstelle_bauen`."""
        gebaut: str = _fundstelle_bauen("Doku", "/docs", "archive/alt.md")
        self.assertIn(ETIKETT_ARCHIVIERT, gebaut)
        self.assertIn("archive/alt.md", gebaut)

    def test_lesender_dienst_traegt_das_etikett(self) -> None:
        """`auskunft.fundstelle`."""
        gebaut: str = fundstelle({"pfad": "archive/alt.md", "wurzel": "/docs"})
        self.assertIn(ETIKETT_ARCHIVIERT, gebaut)
        self.assertIn("archive/alt.md", gebaut)

    def test_bibliotheksweg_traegt_das_etikett(self) -> None:
        """`agents/wissen/auskunft.auskunft_bauen` — der dritte Ausgang.

        Er war beim Bau nicht gefunden: Er nennt dasselbe Wort *Fundstelle*
        vor demselben Publikum, liest aber aus `autonomous_wissen` statt aus
        `dateien_index`. Gefunden von einer Nachpruefung, die nach dem
        **Kriterium** suchte statt nach den bekannten Stellen.
        """
        from dataclasses import dataclass

        @dataclass
        class _Zeile:
            thema: str = "Ein Thema"
            zusammenfassung: str = "Ein Auszug"
            dateipfad: str = "/knowledge/archive/alt.md"
            cosine: float = 0.5
            haeufigkeit: int = 1

        text: str = auskunft_bauen([_Zeile()])
        self.assertIn(ETIKETT_ARCHIVIERT, text)

    def test_beide_wege_lassen_geltendes_in_ruhe(self) -> None:
        """Die Gegenprobe an derselben Achse."""
        self.assertNotIn(
            ETIKETT_ARCHIVIERT, _fundstelle_bauen("Doku", "/docs", "neu.md"),
        )
        self.assertNotIn(
            ETIKETT_ARCHIVIERT,
            fundstelle({"pfad": "neu.md", "wurzel": "/docs"}),
        )


if __name__ == "__main__":
    unittest.main()
