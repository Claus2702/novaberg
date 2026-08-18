"""Tests für den Aufrufer des lesenden Dienstes (`agents/dateien/`).

Ziel: Eine Frage nach dem Inhalt einer freigegebenen Datei erreicht den Dienst,
und die Antwort trägt den **Wortlaut samt Fundstelle** statt einer Umschreibung.

Die Zusicherungen, die hier geprüft werden:

  1. **Der Aushang ist da und trifft genau einen Dienst.** `dateien` steckt in
     `dateien_wurzeln`; die Zuordnung muss exakt bleiben, sonst schluckt der
     lesende Dienst jede Freigabe.
  2. **Die Tiefe folgt der Frage, nicht der Vermutung.** Wer nur wissen will,
     wo etwas steht, löst keinen Dateizugriff aus; wer einen Abschnitt nennt,
     bekommt den Block; wer einen Wortlaut nennt, die Nadel.
  3. **Jede Auskunft trägt ihre Fundstelle.** Ein Text ohne Ort ist genau die
     Karte-statt-Gebiet-Lage, gegen die dieser Dienst gebaut ist.
  4. **Ein unbekannter Aktionswert ist ein Defekt**, kein Griff zu einem
     Vorgabewert.
  5. **Nichts gefunden ist ein Urteil mit Vorschlag**, keine Sackgasse — und
     der Beleg trägt eine Zahl.
  6. **Der Verbund hat keinen Schreibpfad.** Nicht "benutzt ihn nicht",
     sondern importiert ihn nicht.
  7. **Der angemeldete Bedarf hat eine Zusage.** Ohne sie käme der
     Suchschlüssel nie im Dienst an, und die Suche fiele auf die scharfen
     Kanäle zurück, ohne dass es auffällt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.base import AgentState
from agents.dateien import auskunft
from agents.dateien.agent import DateienAgent
from agents.dateien.klassifikation import (
    BEGRIFFE_KAPPUNG,
    GUELTIGE_AKTIONEN,
    _begriffe_pruefen,
    klassifizieren,
)
from agents.nmcp import ZUSAGEN
from graph.nodes.planner import _manager_zu_target
from plugins.dateien_manager.manager import DateienManager

PAAR_USER: str = "meister"
PAAR_FIGUR: str = "nova"

#: Ein Kandidat, wie ihn `suche.py` liefert — mit Karte im Index.
#: Ein gelesener Block, wie ihn `zoom.block_holen` liefert.
BLOCK: dict = {"inhalt": "Die Schwelle liegt bei 0.67379.", "rest": 0}

KANDIDAT: dict = {
    "id": 7,
    "pfad": "kzg-salienz.md",
    "wurzel": "/files",
    "name": "kzg-salienz.md",
    "thema": "Die Salienzrechnung des Kurzzeitgedaechtnisses",
    "zusammenfassung": "Schwelle, Baender und Fristen",
    "stichwoerter": ["Salienz", "Schwelle"],
    "struktur": [{"header": "## Die Schwelle", "start": 10, "ende": 20}],
    "zeilen": 80,
    "kanal": "stichwort",
}


def _state(parameter: dict, aufgabe: str = "Was steht zur Schwelle?") -> AgentState:
    """Baut einen AgentState für den lesenden Dienst."""
    return {
        "aufgabe": aufgabe,
        "aufgabe_typ": "workflow",
        "agent_name": "dateien",
        "kontext": {
            "user_id": PAAR_USER,
            "character_id": PAAR_FIGUR,
            "such_vektor": [0.1, 0.2, 0.3],
        },
        "parameter": parameter,
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


class AushangTest(unittest.TestCase):
    """Der Zettel am schwarzen Brett und seine Zuordnung."""

    def test_aushang_nennt_die_beiden_management_felder(self) -> None:
        """Ohne die Felder ist der Zettel eine Beschreibung ohne Wirkung."""
        zettel: str = DateienManager().router_prompt
        self.assertIn('management_action = "agent"', zettel)
        self.assertIn('management_target = "dateien"', zettel)

    def test_aushang_urteilt_nicht_ueber_andere_anbieter(self) -> None:
        """§3.0c — die Enthaltung: kein Zettel spricht über einen Nachbarn.

        GRENZE DER PRUEFUNG, ausdrücklich: Geprüft werden nur Zielnamen, die
        **keine Alltagswörter** sind. `wissen` ist als Dienstname geführt und
        als Verb unvermeidlich ("der User wissen will") — ein Zeuge darauf
        schlüge an, wo nichts ist, und würde weggeschaltet statt gelesen.
        """
        zettel: str = DateienManager().router_prompt.lower()
        for nachbar in ("dateien_wurzeln", "notizen", "timeline", "recherche"):
            self.assertNotIn(nachbar, zettel, f"Zettel nennt '{nachbar}'")

    def test_zuordnung_trifft_exakt_und_nicht_den_nachbarn(self) -> None:
        """`dateien` steckt in `dateien_wurzeln` — exakt schlägt unscharf."""
        registry: dict = {
            "dateien": DateienManager(),
            "dateien_wurzeln": _Attrappe("dateien_wurzeln"),
        }
        self.assertEqual("dateien", _manager_zu_target(registry, "dateien").ziel)
        self.assertEqual(
            "dateien_wurzeln", _manager_zu_target(registry, "dateien_wurzeln").ziel,
        )

    def test_manager_hat_keinen_schreibpfad(self) -> None:
        """Ein lesender Dienst schreibt auch über seinen Manager nichts."""
        geschrieben: int = DateienManager().execute(
            [{"irgendwas": 1}], PAAR_USER, None, "",
        )
        self.assertEqual(0, geschrieben)


class _Attrappe:
    """Ein Manager-Doppel mit nichts als seinem Ziel."""

    def __init__(self, ziel: str) -> None:
        self.ziel = ziel


class AnmeldungTest(unittest.TestCase):
    """Was der Dienst über sich erklärt — und ob die Naht dazu passt."""

    def setUp(self) -> None:
        """Ein Dienst je Zeuge — er hält keinen Zustand über den Lauf hinaus."""
        self.agent = DateienAgent()

    def test_negativfaelle_sind_eigenschaften_der_aeusserung(self) -> None:
        """Ein Negativfall nennt nie einen anderen Dienst (§3.6b)."""
        self.assertTrue(self.agent.negativfaelle)
        for fall in self.agent.negativfaelle:
            for nachbar in ("dateien_wurzeln", "notizen", "timeline"):
                self.assertNotIn(nachbar, fall, f"Negativfall nennt '{nachbar}'")

    def test_vierter_ausgang_ist_deklariert(self) -> None:
        """Ohne ihn dürfte der Empfang im Zweifel nicht zustellen."""
        self.assertIn("abgelehnt", self.agent.ausgaenge)

    def test_bedarf_hat_eine_zusage(self) -> None:
        """Ein Bedarf ohne Zusage kommt im Dienst nie an."""
        angemeldet: list[str] = [b.schluessel for b in self.agent.bedarf]
        self.assertIn("such_vektor", angemeldet)
        for schluessel in angemeldet:
            self.assertIn(schluessel, ZUSAGEN, f"Bedarf '{schluessel}' ohne Zusage")

    def test_beide_graphen_duerfen_nachsehen(self) -> None:
        """§8.1 — auch ein eigener Gedanke darf in Unterlagen nachsehen."""
        self.assertIn("user", self.agent.graph_eignung)
        self.assertIn("pixie", self.agent.graph_eignung)


class ValidierungTest(unittest.TestCase):
    """Der Eingangskanon — ein unbekannter Wert ist ein Defekt."""

    def setUp(self) -> None:
        """Ein Dienst je Zeuge — er hält keinen Zustand über den Lauf hinaus."""
        self.agent = DateienAgent()

    def test_unbekannte_aktion_wird_gemeldet_statt_ersetzt(self) -> None:
        """Kein Rückfall auf eine Vorgabe."""
        ergebnis: dict = self.agent._validieren(_state({"action": "loeschen"}))
        self.assertEqual("fehler", ergebnis["status"])
        self.assertIn("loeschen", ergebnis["fehler"])

    def test_fehlende_aktion_wird_gemeldet(self) -> None:
        """Ein Auftrag ohne Aktion ist keiner."""
        ergebnis: dict = self.agent._validieren(_state({}))
        self.assertEqual("fehler", ergebnis["status"])

    def test_weg_ueber_den_empfang_fuehrt_zur_klassifikation(self) -> None:
        """'agent' ist die Sammelform und wird klassifiziert, nicht ausgeführt."""
        zustand = _state({"action": "agent"})
        zustand["status"] = "laufend"
        self.assertEqual("klassifizieren", self.agent._nach_validierung(zustand))


class KlassifikationTest(unittest.TestCase):
    """Was das Modell liefert, wird geprüft und nicht geglaubt."""

    def test_begriffe_als_zeichenkette_werden_nicht_zerlegt(self) -> None:
        """Eine Zeichenkette ist ein Begriff — kein Trennen am Komma."""
        self.assertEqual(["Schwelle, Baender"], _begriffe_pruefen("Schwelle, Baender"))

    def test_begriffe_verwerfen_was_keine_zeichenkette_ist(self) -> None:
        """Ein Wert falschen Typs wird verworfen, nicht gecastet."""
        self.assertEqual(["Salienz"], _begriffe_pruefen(["Salienz", 7, None, "  "]))

    def test_begriffe_werden_gekappt(self) -> None:
        """Mehr Begriffe verbreitern die Menge, statt sie zu schärfen."""
        viele: list[str] = [f"wort{i}" for i in range(BEGRIFFE_KAPPUNG + 3)]
        self.assertEqual(BEGRIFFE_KAPPUNG, len(_begriffe_pruefen(viele)))

    def test_kein_objekt_ist_kein_dict(self) -> None:
        """Eine Modellantwort ohne Objekt wird gemeldet."""
        self.assertEqual([], _begriffe_pruefen({"a": 1}))

    def test_unbekannte_aktion_wird_verworfen(self) -> None:
        """Kein Vorgabewert — sonst wäre eine defekte Antwort eine gültige."""
        with patch("agents.dateien.klassifikation.model_service") as modell, \
             patch("agents.dateien.klassifikation.session_turns_retrieve", return_value=[]):
            modell.chat.submit_sync.return_value.parsed = {"action": "zoomen"}
            ergebnis: dict = klassifizieren(_state({"action": "agent"}))
        self.assertEqual("fehler", ergebnis["status"])
        self.assertIn("zoomen", ergebnis["fehler"])

    def test_rejected_traegt_seinen_grund(self) -> None:
        """Der vierte Ausgang braucht den Grund für seinen Beleg."""
        with patch("agents.dateien.klassifikation.model_service") as modell, \
             patch("agents.dateien.klassifikation.session_turns_retrieve", return_value=[]):
            modell.chat.submit_sync.return_value.parsed = {
                "action": "rejected", "grund": "Frage nach Weltwissen",
            }
            ergebnis: dict = klassifizieren(_state({"action": "agent"}))
        self.assertEqual("rejected", ergebnis["status"])
        self.assertEqual("Frage nach Weltwissen", ergebnis["parameter"]["grund"])

    def test_leere_aufgabe_wird_gemeldet(self) -> None:
        """Nichts zu klassifizieren ist ein Fehler und kein leerer Durchlauf."""
        ergebnis: dict = klassifizieren(_state({"action": "agent"}, aufgabe="   "))
        self.assertEqual("fehler", ergebnis["status"])

    def test_der_kanon_traegt_beide_tiefen(self) -> None:
        """Finden und Lesen sind zwei Antworten, nicht eine."""
        self.assertEqual({"finden", "lesen", "rejected"}, set(GUELTIGE_AKTIONEN))


class SucheTest(unittest.TestCase):
    """Ohne Treffer ein Urteil mit Vorschlag — und der Beleg trägt eine Zahl."""

    def setUp(self) -> None:
        """Ein Dienst je Zeuge — er hält keinen Zustand über den Lauf hinaus."""
        self.agent = DateienAgent()

    def test_ohne_treffer_folgt_der_vierte_ausgang(self) -> None:
        """Kein blankes 'nichts gefunden' (§8.2)."""
        with patch("agents.dateien.agent.kandidaten_finden", return_value=[]), \
             patch("agents.dateien.agent.bestand_zaehlen", return_value=14):
            ergebnis: dict = self.agent._suchen(
                _state({"action": "lesen", "name": "gibtsnicht", "begriffe": []})
            )
        self.assertEqual("abgelehnt", ergebnis["status"])
        korrektur = ergebnis["parameter"]["korrektur"]
        self.assertIn("14", korrektur.beleg)
        self.assertTrue(korrektur.vorschlag.strip())

    def test_unvollstaendiges_paar_sucht_nicht(self) -> None:
        """Ein Treffer ohne Paar käme aus einer fremden Freigabe."""
        zustand = _state({"action": "lesen", "begriffe": ["Salienz"]})
        zustand["kontext"] = {"user_id": PAAR_USER, "character_id": ""}
        ergebnis: dict = self.agent._suchen(zustand)
        self.assertEqual("fehler", ergebnis["status"])

    def test_ohne_jeden_schluessel_wird_nicht_gesucht(self) -> None:
        """Weder Name noch Begriff noch Vektor — dann gibt es nichts zu suchen."""
        zustand = _state({"action": "lesen", "name": "", "begriffe": []})
        zustand["kontext"]["such_vektor"] = []
        ergebnis: dict = self.agent._suchen(zustand)
        self.assertEqual("fehler", ergebnis["status"])

    def test_die_nadel_wandert_hinten_an_die_begriffe(self) -> None:
        """Der Wortlaut ist auch ein Stichwort — aber nicht vor der Frage."""
        with patch("agents.dateien.agent.kandidaten_finden", return_value=[KANDIDAT]) as suche:
            self.agent._suchen(_state({
                "action": "lesen", "name": "", "begriffe": ["Salienz"], "nadel": "0.67379",
            }))
        self.assertEqual(["Salienz", "0.67379"], suche.call_args[0][3])


class ZoomWahlTest(unittest.TestCase):
    """Die Tiefe folgt der Frage — und die Karte kostet nichts."""

    def setUp(self) -> None:
        """Ein Dienst je Zeuge — er hält keinen Zustand über den Lauf hinaus."""
        self.agent = DateienAgent()

    def test_finden_liest_keine_datei(self) -> None:
        """§6.4 — 'wo steht etwas' bleibt im Index."""
        with patch("agents.dateien.agent.karte_lesen", return_value=[]) as karte, \
             patch("agents.dateien.agent.block_holen") as block, \
             patch("agents.dateien.agent.nadel_suchen") as nadel:
            ergebnis: dict = self.agent._zoomen(_state({
                "action": "finden", "kandidaten": [KANDIDAT], "begriffe": ["Salienz"],
            }))
        karte.assert_called_once()
        block.assert_not_called()
        nadel.assert_not_called()
        self.assertEqual("abgeschlossen", ergebnis["status"])
        self.assertIn("/files/kzg-salienz.md", ergebnis["ergebnis"])

    def test_genannter_abschnitt_holt_den_block(self) -> None:
        """Wer einen Abschnitt nennt, bekommt den Abschnitt."""
        with patch("agents.dateien.agent.karte_lesen", return_value=[]), \
             patch("agents.dateien.agent.block_holen", return_value=BLOCK) as block, \
             patch("agents.dateien.agent.nadel_suchen") as nadel:
            ergebnis: dict = self.agent._zoomen(_state({
                "action": "lesen", "kandidaten": [KANDIDAT], "abschnitt": "## Die Schwelle",
            }))
        block.assert_called_once()
        nadel.assert_not_called()
        self.assertIn("0.67379", ergebnis["ergebnis"])

    def test_genannter_wortlaut_sucht_die_nadel(self) -> None:
        """Der Wortlaut kommt mit Zeilennummer zurück — das ist die Fundstelle."""
        with patch("agents.dateien.agent.karte_lesen", return_value=[]), \
             patch("agents.dateien.agent.nadel_suchen",
                   return_value={"treffer": [(42, "KZG_SALIENZ_MINIMUM = 0.67379")],
                                 "anzahl": 1, "gekappt": False}):
            ergebnis: dict = self.agent._zoomen(_state({
                "action": "lesen", "kandidaten": [KANDIDAT], "nadel": "0.67379",
            }))
        self.assertEqual("abgeschlossen", ergebnis["status"])
        self.assertIn("Zeile 42", ergebnis["ergebnis"])
        self.assertIn("0.67379", ergebnis["ergebnis"])

    def test_nadel_ohne_treffer_ist_ein_urteil_mit_angebot(self) -> None:
        """§8.2, zweite Zeile: Datei gefunden, Satz nicht darin."""
        with patch("agents.dateien.agent.karte_lesen",
                   return_value=[{"header": "## Die Schwelle"}]), \
             patch("agents.dateien.agent.nadel_suchen",
                   return_value={"treffer": [], "anzahl": 0, "gekappt": False}):
            ergebnis: dict = self.agent._zoomen(_state({
                "action": "lesen", "kandidaten": [KANDIDAT], "nadel": "Thomaskantor",
            }))
        self.assertEqual("abgelehnt", ergebnis["status"])
        korrektur = ergebnis["parameter"]["korrektur"]
        self.assertIn("0 Treffer", korrektur.beleg)
        self.assertIn("## Die Schwelle", korrektur.vorschlag)

    def test_unlesbarer_abschnitt_faellt_auf_die_karte_zurueck(self) -> None:
        """Ein unbekannter Header ist kein Fehler, sondern eine andere Stufe."""
        with patch("agents.dateien.agent.karte_lesen",
                   return_value=[{"header": "## Die Schwelle"}]), \
             patch("agents.dateien.agent.block_holen", return_value=None), \
             patch("agents.dateien.agent.nadel_suchen") as nadel:
            ergebnis: dict = self.agent._zoomen(_state({
                "action": "lesen", "kandidaten": [KANDIDAT], "abschnitt": "## Gibt es nicht",
            }))
        nadel.assert_not_called()
        self.assertEqual("abgeschlossen", ergebnis["status"])
        self.assertIn("## Die Schwelle", ergebnis["ergebnis"])

    def test_jeder_begriff_bekommt_einen_versuch(self) -> None:
        """Ein Kompositum trifft zeichengenau selten — das Wort daneben schon."""
        treffer: dict = {"treffer": [(47, "Sie liegt bei 0,67379")], "anzahl": 1}
        with patch("agents.dateien.agent.karte_lesen", return_value=[]), \
             patch("agents.dateien.agent.nadel_suchen",
                   side_effect=[{"treffer": [], "anzahl": 0}, treffer]) as nadel:
            ergebnis: dict = self.agent._zoomen(_state({
                "action": "lesen", "kandidaten": [KANDIDAT],
                "nadel": "Salienzschwelle", "begriffe": ["Schwelle"],
            }))
        self.assertEqual(2, nadel.call_count)
        self.assertEqual("abgeschlossen", ergebnis["status"])
        self.assertIn("0,67379", ergebnis["ergebnis"])

    def test_derselbe_begriff_wird_nicht_zweimal_gesucht(self) -> None:
        """Nadel und Begriff sind oft dasselbe Wort — ein Zugriff genügt."""
        with patch("agents.dateien.agent.karte_lesen", return_value=[]), \
             patch("agents.dateien.agent.nadel_suchen",
                   return_value={"treffer": [], "anzahl": 0}) as nadel:
            self.agent._zoomen(_state({
                "action": "lesen", "kandidaten": [KANDIDAT],
                "nadel": "Schwelle", "begriffe": ["Schwelle"],
            }))
        self.assertEqual(1, nadel.call_count)

    def test_zoom_ohne_kandidaten_ist_ein_defekt(self) -> None:
        """Das Routing hätte hier nicht herführen dürfen."""
        ergebnis: dict = self.agent._zoomen(_state({"action": "lesen", "kandidaten": []}))
        self.assertEqual("fehler", ergebnis["status"])

    def test_leere_auskunft_wird_als_stoerung_gemeldet(self) -> None:
        """Ein leerer Aufgabenblock lädt zu plausibler Prosa ein (§8.1a)."""
        ergebnis: dict = self.agent._abschluss(
            _state({"action": "lesen"}), "karte", "   ", [KANDIDAT],
        )
        self.assertEqual("fehler", ergebnis["status"])


class AuskunftTest(unittest.TestCase):
    """Jede Auskunft trägt ihre Fundstelle (§10)."""

    def test_fundstelle_setzt_wurzel_und_pfad_zusammen(self) -> None:
        """Der Pfad im Index ist relativ zur Wurzel (§4)."""
        self.assertEqual("/files/kzg-salienz.md", auskunft.fundstelle(KANDIDAT))

    def test_fundstelle_ohne_pfad_ist_nie_leer(self) -> None:
        """Eine Auskunft ohne Ort ist die Aussage, die verhindert werden soll."""
        self.assertTrue(auskunft.fundstelle({"wurzel": "/files"}).strip())

    def test_treffer_ohne_nummer_wird_verworfen(self) -> None:
        """Eine Zeile ohne Fundstelle belegt nichts."""
        self.assertEqual((None, ""), auskunft._treffer_zerlegen(("keine Zahl", "Text")))
        self.assertEqual((None, ""), auskunft._treffer_zerlegen("nur ein String"))

    def test_kappung_wird_genannt_und_nicht_verschluckt(self) -> None:
        """Eine gekürzte Liste ist von einer vollständigen sonst nicht zu unterscheiden."""
        text: str = auskunft.auskunft_nadel(
            [KANDIDAT],
            {"treffer": [(i, f"Zeile {i}") for i in range(auskunft.TREFFER_IM_TEXT + 5)],
             "anzahl": auskunft.TREFFER_IM_TEXT + 5, "gekappt": True},
            "Salienz",
        )
        self.assertIn("weitere Treffer nicht gezeigt", text)
        self.assertIn("gekappt", text)

    def test_karte_sagt_dass_nichts_gelesen_wurde(self) -> None:
        """Die Beschriftung ist die ganze Aussage der Stufe 1."""
        text: str = auskunft.auskunft_karte([KANDIDAT], [{"header": "## Die Schwelle"}])
        self.assertIn("NICHT gelesen", text)

    def test_jede_auskunft_nennt_ihre_herkunft(self) -> None:
        """Herkunft im Text — sonst überlebt sie den Übergang nicht (§1a.4)."""
        for text in (
            auskunft.auskunft_karte([KANDIDAT], []),
            auskunft.auskunft_finden([KANDIDAT], []),
            auskunft.auskunft_nadel([KANDIDAT], {"treffer": [(1, "x")], "anzahl": 1}, "x"),
        ):
            self.assertIn("UNTERLAGEN", text)
            self.assertIn("/files/kzg-salienz.md", text)


class DispatchTest(unittest.TestCase):
    """Jeder Rückkehrpfad setzt die Anzeigefelder."""

    def test_ohne_user_id_kein_lauf_und_trotzdem_ein_text(self) -> None:
        """Wer nur bei Erfolg schreibt, macht 'nicht gelaufen' unsichtbar."""
        from agents.dateien.dispatch import dispatch_dateien

        rueckgabe: dict = dispatch_dateien({"user_id": ""})
        self.assertEqual(1, len(rueckgabe["agent_results"]))
        self.assertEqual("fehler", rueckgabe["agent_results"][0].status)
        self.assertTrue(rueckgabe["management_result"].strip())
        self.assertEqual("", rueckgabe["agent_name"])

    def test_ablehnung_ohne_korrektur_wird_zur_stoerung(self) -> None:
        """Eine Ablehnung ohne Vorschlag ist eine Sackgasse."""
        from agents.dateien import dispatch as modul

        with patch.object(modul, "AgentRegistry") as registry, \
             patch.object(modul, "reiz_text", return_value="egal"):
            registry.finden.return_value.invoke.return_value = {
                "status": "abgelehnt", "parameter": {}, "schritte": [],
            }
            rueckgabe: dict = modul.dispatch_dateien(
                {"user_id": PAAR_USER, "such_vektor": [0.1]}
            )
        self.assertEqual("fehler", rueckgabe["agent_results"][0].status)

    def test_der_suchschluessel_wandert_in_den_kontext(self) -> None:
        """Ohne ihn fiele der dense Kanal aus, ohne dass es auffällt."""
        from agents.dateien import dispatch as modul

        with patch.object(modul, "AgentRegistry") as registry, \
             patch.object(modul, "reiz_text", return_value="egal"):
            registry.finden.return_value.invoke.return_value = {
                "status": "abgeschlossen", "ergebnis": "Text", "parameter": {}, "schritte": [],
            }
            modul.dispatch_dateien({"user_id": PAAR_USER, "such_vektor": [0.4, 0.5]})
            uebergeben = registry.finden.return_value.invoke.call_args[0][0]
        self.assertEqual([0.4, 0.5], uebergeben["kontext"]["such_vektor"])


def _schreibende_zugriffe(
    modul: Path, verbotene_module: tuple[str, ...], verbotene_namen: tuple[str, ...],
) -> list[str]:
    """Sammelt Importe und Aufrufe eines Moduls, die schreiben könnten.

    Vorbedingung: `modul` ist eine lesbare Python-Datei.
    Nachbedingung: Eine Liste von Fundstellen, leer wenn keine.
    Fehlerfaelle: keine — eine Datei ohne Importe liefert die leere Liste.

    **Geprüft wird der Baum, nicht der Text.** Ein Modul, das in seinem
    Docstring sagt, es importiere `redaktion` nicht, träfe jede Textsuche —
    und ein Zeuge, der an der eigenen Zusicherung anschlägt, wird abgeschaltet
    statt gelesen.
    """
    # ── Verarbeitung ────────────────────────────
    treffer: list[str] = []
    for knoten in ast.walk(ast.parse(modul.read_text(encoding="utf-8"))):
        if isinstance(knoten, ast.Import):
            treffer += [
                f"{modul.name}: import {teil.name}"
                for teil in knoten.names if teil.name in verbotene_module
            ]
        elif isinstance(knoten, ast.ImportFrom):
            if (knoten.module or "") in verbotene_module:
                treffer.append(f"{modul.name}: from {knoten.module}")
            treffer += [
                f"{modul.name}: {teil.name}"
                for teil in knoten.names if teil.name in verbotene_namen
            ]
        elif isinstance(knoten, ast.Call):
            name: str = _aufrufname(knoten.func)
            if name in verbotene_namen or name == "open":
                treffer.append(f"{modul.name}: Aufruf {name}()")

    # ── Ausgabe ─────────────────────────────────
    return treffer


def _aufrufname(ziel: ast.expr) -> str:
    """Der Name einer aufgerufenen Funktion, soweit er ohne Auflösung ablesbar ist.

    Vorbedingung: `ziel` ist der `func`-Teil eines Aufrufs.
    Nachbedingung: Der Name, oder eine leere Zeichenkette bei einem Ausdruck,
    der erst zur Laufzeit einen Namen hat.
    """
    if isinstance(ziel, ast.Attribute):
        return ziel.attr
    if isinstance(ziel, ast.Name):
        return ziel.id
    return ""


class SchreibpfadTest(unittest.TestCase):
    """Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden."""

    #: Module und Namen, die schreiben. Geprüft wird der **Import**, nicht der
    #: Text: Ein Modul, das in seinem Docstring sagt, es importiere
    #: `redaktion` nicht, träfe jede Textsuche — und ein Zeuge, der an der
    #: eigenen Zusicherung anschlägt, wird abgeschaltet statt gelesen.
    VERBOTENE_MODULE: tuple[str, ...] = (
        "tools.dateien.redaktion", "tools.dateien.versionierung",
        "tools.dateien.schreiben", "tools.dateien.hand", "shutil",
    )
    VERBOTENE_NAMEN: tuple[str, ...] = (
        "absatz_aendern", "absatz_einfuegen", "absatz_loeschen",
        "datei_schreiben", "write_text", "rmtree", "unlink", "remove",
    )

    def test_kein_modul_des_verbunds_importiert_einen_schreiber(self) -> None:
        """Der lesende Verbund trägt keinen Schreibpfad ins Dateisystem."""
        verbund: Path = Path(__file__).resolve().parents[1] / "agents" / "dateien"
        module: list[Path] = sorted(verbund.glob("*.py"))
        treffer: list[str] = []
        for modul in module:
            treffer += _schreibende_zugriffe(
                modul, self.VERBOTENE_MODULE, self.VERBOTENE_NAMEN,
            )

        self.assertEqual(treffer, [], f"Schreibpfad im lesenden Verbund: {treffer}")
        # Wirksamkeit: Ein leerer Baum bestünde diesen Zeugen ebenfalls.
        self.assertGreaterEqual(len(module), 5, "Der Verbund hat weniger Module als erwartet")


if __name__ == "__main__":
    unittest.main()
