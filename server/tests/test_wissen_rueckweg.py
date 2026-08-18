"""Tests für den Rückweg (`agents/wissen_rueckweg/`).

Ziel: Ein Fund, der die Promotion überlebt hat, landet **eingeordnet** in einer
vorhandenen Wissensdatei — oder nirgends, und zwar begründet.

Die Zusicherungen, die hier geprüft werden:

  1. **Keine passende Datei ist ein Ergebnis**, kein Fehlschlag — und der
     häufigere Ausgang. Eine erzwungene Zuordnung verschmutzt die Datei, die
     sie trifft.
  2. **Eine Nummer, die nicht in der Vorlage stand, wird verworfen statt
     geraten.** Die falsche Datei ist teurer als keine.
  3. **Der Anker wird vor dem Schreiben geprüft.** Ein mehrdeutiger Anker
     führt nie zu einem Schnitt an der ersten Fundstelle.
  4. **Steht der Fund schon da, wird nichts geschrieben** — eine Wiederholung
     ist kein Zuwachs.
  5. **Die Herkunft des Materials reist mit.** Ein Destillat darf sich nicht
     als Wortlaut ausgeben; im Zweifel gilt die vorsichtigere Lesart.
  6. **Die Version steigt vor dem Schnitt**, nicht danach.
  7. **Der Auslöser reisst die Promotion nicht.** Ein Fehlschlag beim
     Einreihen kostet eine Einarbeitung, kein Gedächtnis.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.wissen_rueckweg import einarbeitung, herkunft, zuordnung
from agents.wissen_rueckweg.agent import WissenRueckwegAgent
from services.pixie.router import _QUEUE_ROUTING

PAAR_USER: str = "meister"
PAAR_FIGUR: str = "nova"

#: Zwei Kandidaten, wie sie `kandidaten_laden` liefert.
KANDIDATEN: list[dict] = [
    {"id": 11, "dateipfad": "/knowledge/a.md", "thema": "Kakteen",
     "zusammenfassung": "Areolen, Dornen, Wuchsformen", "haeufigkeit": 1, "kosinus": 0.61},
    {"id": 12, "dateipfad": "/knowledge/b.md", "thema": "Orchideen",
     "zusammenfassung": "Velamen, Epiphyten", "haeufigkeit": 2, "kosinus": 0.44},
]


class VersionTest(unittest.TestCase):
    """Die zweite Stelle steigt je Eingriff — abgeleitet, nicht erfunden."""

    def test_zweite_stelle_steigt(self) -> None:
        """Aus den Beispielen des Konzepts: 2.2 wird 2.3."""
        self.assertEqual("1.1", einarbeitung.naechste_version("1.0"))
        self.assertEqual("2.3", einarbeitung.naechste_version("2.2"))
        self.assertEqual("1.10", einarbeitung.naechste_version("1.9"))

    def test_unbrauchbare_angabe_wird_gemeldet_und_markiert(self) -> None:
        """Eine gerissene Zählung verhindert den Eingriff nicht, versteckt sich aber auch nicht."""
        self.assertEqual("v1+1", einarbeitung.naechste_version("v1"))


class HerkunftTest(unittest.TestCase):
    """Ein Destillat darf sich nicht als Wortlaut ausgeben."""

    def test_marke_wird_gelesen(self) -> None:
        """Beide Werte des Kanons kommen unverändert zurück."""
        self.assertEqual(herkunft.QUELLE_ROH, herkunft.herkunft_lesen("rueckweg_roh"))
        self.assertEqual(
            herkunft.QUELLE_VERDICHTET, herkunft.herkunft_lesen("rueckweg_verdichtet"),
        )

    def test_unbekannte_marke_gilt_als_verdichtet(self) -> None:
        """Die vorsichtigere Lesart — sonst tarnt sich ein Destillat."""
        for wert in ("", "rueckweg", "irgendwas", None):
            self.assertEqual(herkunft.QUELLE_VERDICHTET, herkunft.herkunft_lesen(wert))

    def test_rohfassung_gewinnt_wenn_es_sie_gibt(self) -> None:
        """§4b.1b — die rohe Fassung ist die entschiedene."""
        with patch.object(herkunft, "rohfassung_holen", return_value="ÄUSSERUNG:\nx"):
            text, quelle = herkunft.material_waehlen("t1", "verdichtet", PAAR_USER, PAAR_FIGUR)
        self.assertEqual(herkunft.QUELLE_ROH, quelle)
        self.assertIn("ÄUSSERUNG", text)

    def test_ohne_rohfassung_faellt_er_erkennbar_zurueck(self) -> None:
        """Der Rückfall ist erlaubt — unmarkiert wäre er es nicht."""
        with patch.object(herkunft, "rohfassung_holen", return_value=""):
            text, quelle = herkunft.material_waehlen("", "verdichtet", PAAR_USER, PAAR_FIGUR)
        self.assertEqual(herkunft.QUELLE_VERDICHTET, quelle)
        self.assertEqual("verdichtet", text)

    def test_ohne_turn_id_keine_abfrage(self) -> None:
        """Ein leerer Turnbezug ist keine Suche wert."""
        self.assertEqual("", herkunft.rohfassung_holen("", PAAR_USER, PAAR_FIGUR))

    def test_unvollstaendiges_paar_holt_nichts(self) -> None:
        """Sonst käme fremdes Gesprächsmaterial in eine Wissensdatei."""
        self.assertEqual("", herkunft.rohfassung_holen("t1", PAAR_USER, ""))


class ZuordnungTest(unittest.TestCase):
    """Pflegbarkeit entscheidet, nicht Nähe — und null ist eine Antwort."""

    def _antwort(self, nutzlast: dict) -> None:
        """Baut den Kontextmanager für eine Modellantwort."""
        modell = patch("agents.wissen_rueckweg.zuordnung.model_service")
        gemockt = modell.start()
        gemockt.chat.submit_sync.return_value.parsed = nutzlast
        self.addCleanup(modell.stop)

    def test_keine_datei_ist_ein_ergebnis(self) -> None:
        """Der häufigere und der billigere Ausgang."""
        self._antwort({"ziel": None, "begruendung": "Begebenheit", "kern": "x"})
        ergebnis = zuordnung.ziel_bestimmen("Fund", KANDIDATEN)
        self.assertIsNotNone(ergebnis)
        self.assertIsNone(ergebnis["ziel"])
        self.assertEqual("Begebenheit", ergebnis["begruendung"])

    def test_nummer_ausserhalb_der_vorlage_wird_verworfen(self) -> None:
        """Die falsche Datei ist teurer als keine."""
        self._antwort({"ziel": 99, "begruendung": "b", "kern": "k"})
        self.assertIsNone(zuordnung.ziel_bestimmen("Fund", KANDIDATEN))

    def test_gewaehltes_ziel_ohne_kern_wird_verworfen(self) -> None:
        """Ohne Gehalt gibt es nichts einzuarbeiten."""
        self._antwort({"ziel": 11, "begruendung": "b", "kern": "   "})
        self.assertIsNone(zuordnung.ziel_bestimmen("Fund", KANDIDATEN))

    def test_treffer_traegt_die_zeile_und_nicht_die_nummer(self) -> None:
        """Der Aufrufer braucht den Pfad, nicht die Nummer."""
        self._antwort({"ziel": 12, "begruendung": "b", "kern": "Velamen speichert Wasser"})
        ergebnis = zuordnung.ziel_bestimmen("Fund", KANDIDATEN)
        self.assertEqual("/knowledge/b.md", ergebnis["ziel"]["dateipfad"])

    def test_ohne_kandidaten_kein_aufruf(self) -> None:
        """Eine leere Bibliothek ist keine Frage an das Modell."""
        with patch("agents.wissen_rueckweg.zuordnung.model_service") as modell:
            self.assertIsNone(zuordnung.ziel_bestimmen("Fund", []))
            modell.chat.submit_sync.assert_not_called()

    def test_vorlage_traegt_die_datenbank_nummer(self) -> None:
        """Ohne sie müsste die Antwort umgerechnet werden."""
        vorlage: str = zuordnung._vorlage_bauen(KANDIDATEN)
        self.assertIn("[11]", vorlage)
        self.assertIn("Velamen", vorlage)


class EinarbeitungTest(unittest.TestCase):
    """Der Anker wird geprüft, bevor geschrieben wird."""

    def _antwort(self, nutzlast: dict) -> None:
        """Baut den Kontextmanager für eine Modellantwort."""
        modell = patch("agents.wissen_rueckweg.einarbeitung.model_service")
        gemockt = modell.start()
        gemockt.chat.submit_sync.return_value.parsed = nutzlast
        self.addCleanup(modell.stop)

    def test_mehrdeutiger_anker_wird_verworfen(self) -> None:
        """Nie ein Schnitt an der ersten Fundstelle."""
        self._antwort({"absatz": "neu", "nach": "Satz.", "ergaenzung": "e"})
        self.assertIsNone(
            einarbeitung.absatz_bestimmen("Satz. Noch ein Satz.", "Kern")
        )

    def test_unauffindbarer_anker_wird_verworfen(self) -> None:
        """Ein Vorbild, das nicht dasteht, ist kein Vorbild."""
        self._antwort({"absatz": "neu", "nach": "steht nicht drin", "ergaenzung": "e"})
        self.assertIsNone(einarbeitung.absatz_bestimmen("Ein Text.", "Kern"))

    def test_steht_schon_da_ist_ein_ergebnis(self) -> None:
        """Eine Wiederholung ist kein Zuwachs."""
        self._antwort({"absatz": "", "nach": None, "ergaenzung": ""})
        ergebnis = einarbeitung.absatz_bestimmen("Ein Text.", "Kern")
        self.assertIsNotNone(ergebnis)
        self.assertIsNone(ergebnis["nach"])

    def test_eindeutiger_anker_kommt_durch(self) -> None:
        """Der Regelfall — genau einmal im Text."""
        self._antwort({"absatz": "Neuer Satz.", "nach": "Ein Text.", "ergaenzung": "und mehr"})
        ergebnis = einarbeitung.absatz_bestimmen("Ein Text. Anderes.", "Kern")
        self.assertEqual("Ein Text.", ergebnis["nach"])

    def test_leerer_kern_arbeitet_nichts_ein(self) -> None:
        """Ohne Gehalt kein Aufruf."""
        with patch("agents.wissen_rueckweg.einarbeitung.model_service") as modell:
            self.assertIsNone(einarbeitung.absatz_bestimmen("Text", "  "))
            modell.chat.submit_sync.assert_not_called()

    def test_ohne_vorschlag_bleibt_die_datei_unberuehrt(self) -> None:
        """Kein Schnitt, keine Version — und ein Grund im Bericht."""
        with patch.object(einarbeitung, "aktuell_lesen", return_value="Ein Text."), \
             patch.object(einarbeitung, "absatz_bestimmen", return_value=None), \
             patch.object(einarbeitung, "version_fortschreiben") as version, \
             patch.object(einarbeitung, "absatz_einfuegen") as schnitt:
            ergebnis = einarbeitung.einarbeiten("/knowledge/a.md", "/knowledge", "Kern")
        version.assert_not_called()
        schnitt.assert_not_called()
        self.assertFalse(ergebnis["geschrieben"])
        self.assertEqual("kein_brauchbarer_vorschlag", ergebnis["grund"])

    def test_die_version_steigt_vor_dem_schnitt(self) -> None:
        """Sonst nennt der Archiveintrag eine Version, die die Datei nicht zeigt."""
        reihenfolge: list[str] = []
        with patch.object(einarbeitung, "aktuell_lesen", return_value="Ein Text."), \
             patch.object(einarbeitung, "absatz_bestimmen",
                          return_value={"absatz": "A", "nach": "Ein Text.", "ergaenzung": "e"}), \
             patch.object(einarbeitung, "version_fortschreiben",
                          side_effect=lambda *a: reihenfolge.append("version") or "1.1"), \
             patch.object(einarbeitung, "absatz_einfuegen",
                          side_effect=lambda *a, **k: reihenfolge.append("schnitt") or
                          {"erfolg": True, "marke": "[i1>]", "zeichen": 10}):
            ergebnis = einarbeitung.einarbeiten("/knowledge/a.md", "/knowledge", "Kern")
        self.assertEqual(["version", "schnitt"], reihenfolge)
        self.assertTrue(ergebnis["geschrieben"])
        self.assertEqual("1.1", ergebnis["version"])


class VerdrahtungTest(unittest.TestCase):
    """Den Baustein zu prüfen genügt nicht — die Verdrahtung ist der Defekt."""

    def test_die_aufgabe_hat_ihren_agenten(self) -> None:
        """Ohne Eintrag im Routing wählt der Heartbeat und findet niemanden."""
        self.assertEqual("wissen_rueckweg", _QUEUE_ROUTING["wissen_rueckweg"])

    def test_der_dienst_faehrt_die_llm_spur(self) -> None:
        """Zwei Modellaufrufe je Fund — die CPU-Spur würde laut scheitern."""
        agent = WissenRueckwegAgent()
        self.assertEqual("llm", agent.lastart)
        self.assertEqual("queue", agent.zustellart)
        self.assertEqual(["pixie"], agent.graph_eignung)

    def test_der_ausloeser_reisst_die_promotion_nicht(self) -> None:
        """Ein Fehlschlag beim Einreihen kostet eine Einarbeitung, kein Gedächtnis."""
        from agents.synapsen_promotion.agent import SynapsenPromotionAgent

        with patch("agents.synapsen_promotion.agent.material_waehlen",
                   return_value=("Text", "roh")), \
             patch("agents.synapsen_promotion.agent.shadow_queue_push",
                   side_effect=RuntimeError("Queue weg")):
            SynapsenPromotionAgent._rueckweg_einreihen(
                kzg_key="k1", user_id=PAAR_USER, character_id=PAAR_FIGUR,
                inhalt="Fund", themen_str="Thema", salienz=0.9, turn_id="t1",
            )

    def test_ohne_inhalt_wird_nicht_eingereiht(self) -> None:
        """Ein Auftrag ohne Fund hätte nichts einzuarbeiten."""
        from agents.synapsen_promotion.agent import SynapsenPromotionAgent

        with patch("agents.synapsen_promotion.agent.shadow_queue_push") as push:
            SynapsenPromotionAgent._rueckweg_einreihen(
                kzg_key="k1", user_id=PAAR_USER, character_id=PAAR_FIGUR,
                inhalt="   ", themen_str="Thema", salienz=0.9, turn_id="t1",
            )
        push.assert_not_called()

    def test_der_kurzzeit_eintrag_traegt_seinen_turnbezug(self) -> None:
        """Ohne ihn kann der Rückweg nur das Destillat einarbeiten."""
        from pathlib import Path

        quelle: str = (Path(__file__).resolve().parents[1] / "memory" / "kzg.py").read_text(
            encoding="utf-8",
        )
        self.assertIn('"turn_id":            turn_id,', quelle)


if __name__ == "__main__":
    unittest.main()
