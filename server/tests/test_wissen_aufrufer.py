"""Tests für den Aufrufer der eigenen Bibliothek (`agents/wissen/`).

Ziel: Eine Frage nach dem, was sie sich **selbst** erarbeitet hat, erreicht
einen Dienst — statt nur ungefragt beizufließen. Bis zum 19.08.2026 trug
`wissen_manager` `immer_aktiv` und keinen Zettel; die Bibliothek war
angebunden wie ein Gedächtnis und konnte von niemandem bestellt werden.

Die Zusicherungen, die hier geprüft werden:

  1. **Der Zettel ist da und trifft genau diesen Dienst.** Ohne die beiden
     Management-Felder ist er eine Beschreibung ohne Wirkung.
  2. **Die Quelle bleibt.** Zettel und Quelle sind zwei Rollen desselben
     Silos; wer beim Bau des einen das andere abschaltet, tauscht eine Lücke
     gegen die andere.
  3. **Eine Suche, zwei Eingänge** (`novaberg-convention-nmcp.md` §6a.1).
     Beide gehen durch dieselbe Abfrage, mit derselben Schwelle und
     derselben Ordnung — verschieden ist allein die Tiefe. Zwei Abfragen
     über denselben Bestand ergäben zwei Rangfolgen.
  4. **Fehler und Ablehnung sind zwei Ausgänge** (§6a.2). Ein
     Datenbankfehler ist eine Störung, „nichts gefunden" ein Urteil. Wer
     beide einebnet, macht die wertvollste Leistung des Dienstes als
     Störung sichtbar.
  5. **Die Ablehnung trägt eine Zahl.** *„Dazu habe ich nichts"* ohne Beleg
     ist von *„ich habe nicht nachgesehen"* nicht zu unterscheiden.
  6. **Jede Auskunft nennt ihre Tiefe.** Der Dienst liefert Thema und
     Zusammenfassung, nicht den Wortlaut — ein unbenannter Verzicht liest
     sich als Vollständigkeit.
  7. **Der Dienst hat keinen Schreibpfad.** Nicht „benutzt ihn nicht",
     sondern importiert ihn nicht.
  8. **Der angemeldete Bedarf hat eine Zusage**, und die Anmeldung ist
     vollständig.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

import psycopg2
from agents.base import AgentState
from agents.nmcp import ZUSAGEN, anmelden
from agents.wissen import auskunft
from agents.wissen.agent import TYP_WISSEN, WissenAgent
from config import WISSEN_AUFTRAG_TOP_K, WISSEN_RETRIEVAL_TOP_K
from graph.nodes.planner import _manager_zu_target

#: Der Endknoten des Graphen, wie LangGraph ihn benennt. Als Import und nicht
#: als Zeichenkette: Ein Zeuge, der "__end__" hinschreibt, bliebe bei einer
#: Umbenennung gruen und pruefte nichts mehr.
from langgraph.graph import END as END_FREI
from memory.repositories.autonomous_wissen_repository import Bibliothekszeile
from plugins.wissen_manager.manager import WissenManager

PAAR_USER:  str = "meister"
PAAR_FIGUR: str = "nova"

#: Die Nachbarn, die ein Zettel nicht benennen darf (§3.6b). `wissen` selbst
#: steht nicht dabei — es ist der eigene Name.
NACHBARN: tuple[str, ...] = (
    "dateien", "dateien_wurzeln", "notizen", "timeline", "recherche",
    "kzg", "fakten", "direktiven",
)


def _zeile(thema: str = "Resonanz", cosine: float = 0.72) -> Bibliothekszeile:
    """Baut einen Bibliothekstreffer, wie ihn das Repository liefert."""
    return Bibliothekszeile(
        thema=thema,
        zusammenfassung="Resonanz als physikalische Groesse, Kopplung, Guete",
        dateipfad=f"/knowledge/autonomous/nova/2026-08-14_{thema}_wissen.md",
        modus="recherche",
        status="echte_tiefe",
        gewicht_decay=0.83,
        haeufigkeit=2,
        cosine=cosine,
    )


def _state(such_vektor: list | None = None, paar: bool = True) -> AgentState:
    """Baut einen AgentState für den Bibliotheks-Dienst."""
    return {
        "aufgabe": "Was hast du selbst zur Resonanz erarbeitet?",
        "aufgabe_typ": "workflow",
        "agent_name": "wissen",
        "kontext": {
            "user_id": PAAR_USER if paar else "",
            "character_id": PAAR_FIGUR if paar else "",
            "such_vektor": [0.1, 0.2, 0.3] if such_vektor is None else such_vektor,
        },
        "parameter": {"action": "agent", "target": "wissen"},
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


class _Attrappe:
    """Ein Manager-Doppel mit nichts als seinem Ziel."""

    def __init__(self, ziel: str) -> None:
        self.ziel = ziel


class ZettelTest(unittest.TestCase):
    """Der Zettel am schwarzen Brett und seine Zuordnung."""

    def test_zettel_nennt_die_beiden_management_felder(self) -> None:
        """Ohne die Felder ist der Zettel eine Beschreibung ohne Wirkung."""
        zettel: str = WissenManager().router_prompt
        self.assertIn('management_action = "agent"', zettel)
        self.assertIn('management_target = "wissen"', zettel)

    def test_zettel_urteilt_nicht_ueber_andere_anbieter(self) -> None:
        """§3.0c, §3.6b — die Enthaltung: kein Zettel spricht über einen Nachbarn."""
        zettel: str = WissenManager().router_prompt.lower()
        for nachbar in NACHBARN:
            self.assertNotIn(nachbar, zettel, f"Zettel nennt '{nachbar}'")

    def test_zettel_benutzt_nicht_die_eigene_fachsprache(self) -> None:
        """§3.2 — der Empfang kennt die Fachsprache keiner Abteilung."""
        zettel: str = WissenManager().router_prompt.lower()
        for begriff in WissenAgent().faehigkeiten:
            self.assertNotIn(begriff.lower(), zettel, f"Zettel nennt '{begriff}'")

    def test_zuordnung_trifft_exakt_und_nicht_den_nachbarn(self) -> None:
        """`wissen` steckt in `wissen_rueckweg` — exakt schlägt unscharf."""
        registry: dict = {
            "wissen": WissenManager(),
            "wissen_rueckweg": _Attrappe("wissen_rueckweg"),
        }
        self.assertEqual("wissen", _manager_zu_target(registry, "wissen").ziel)
        self.assertEqual(
            "wissen_rueckweg",
            _manager_zu_target(registry, "wissen_rueckweg").ziel,
        )

    def test_die_quelle_bleibt_neben_dem_zettel(self) -> None:
        """Zwei Rollen desselben Silos — der Zettel löst die Quelle nicht ab (§6a)."""
        self.assertTrue(WissenManager().immer_aktiv)
        self.assertTrue(WissenManager().router_prompt.strip())

    def test_manager_hat_keinen_schreibpfad(self) -> None:
        """Die Bibliothek wird von den Hintergrund-Agenten gefüllt, nicht im Gespräch."""
        self.assertEqual(0, WissenManager().execute([{"irgendwas": 1}], PAAR_USER, None, ""))


class AnmeldungTest(unittest.TestCase):
    """Was der Dienst über sich erklärt — und ob die Naht dazu passt."""

    def setUp(self) -> None:
        """Ein Dienst je Zeuge — er hält keinen Zustand über den Lauf hinaus."""
        self.agent = WissenAgent()

    def test_anmeldung_ist_vollstaendig(self) -> None:
        """Ein Mangel am Handshake schränkt die Einbindung ein (§5.9)."""
        befund = anmelden(self.agent)
        self.assertEqual(
            "vollstaendig", befund.grad,
            [f"{m.regel}: {m.text}" for m in befund.maengel],
        )

    def test_negativfaelle_sind_eigenschaften_der_aeusserung(self) -> None:
        """Ein Negativfall nennt nie einen anderen Dienst (§3.6b)."""
        self.assertGreaterEqual(len(self.agent.negativfaelle), 3)
        for fall in self.agent.negativfaelle:
            for nachbar in NACHBARN:
                self.assertNotIn(nachbar, fall.lower(), f"Negativfall nennt '{nachbar}'")

    def test_vierter_ausgang_ist_deklariert(self) -> None:
        """Ohne ihn dürfte der Empfang im Zweifel nicht zustellen."""
        self.assertIn("abgelehnt", self.agent.ausgaenge)
        self.assertEqual(4, len(self.agent.ausgaenge))

    def test_bedarf_hat_eine_zusage(self) -> None:
        """Ein Bedarf ohne Zusage kommt im Dienst nie an."""
        angemeldet: list[str] = [b.schluessel for b in self.agent.bedarf]
        self.assertIn("such_vektor", angemeldet)
        for schluessel in angemeldet:
            self.assertIn(schluessel, ZUSAGEN, f"Bedarf '{schluessel}' ohne Zusage")

    def test_die_verschwiegene_tiefe_steht_in_der_grenze(self) -> None:
        """Stufe 2 fehlt — ein unbenannter Verzicht liest sich als Vollständigkeit."""
        self.assertTrue(
            any("Wortlaut" in g for g in self.agent.grenze),
            self.agent.grenze,
        )

    def test_rechenspur_deklariert(self) -> None:
        """Dieser Dienst ruft kein Sprachmodell — die schnelle Spur ist die richtige."""
        self.assertEqual("cpu", self.agent.lastart)


class EineSucheTest(unittest.TestCase):
    """§6a.1 — zwei Eingänge, eine Suche. Verschieden ist allein die Tiefe."""

    def test_beide_eingaenge_rufen_dieselbe_abfrage(self) -> None:
        """Zwei Abfragen über denselben Bestand ergäben zwei Rangfolgen."""
        from agents.wissen import agent as dienst_modul
        from plugins.wissen_manager import manager as quelle_modul

        with patch.object(quelle_modul, "AutonomousWissenRepository") as quelle_repo:
            quelle_repo.suchen.return_value = []
            WissenManager().enrich_entries(
                {"such_vektor": [0.1, 0.2], "user_id": PAAR_USER,
                 "character_id": PAAR_FIGUR},
                "postgresql://egal",
            )
        with patch.object(dienst_modul, "AutonomousWissenRepository") as dienst_repo:
            dienst_repo.suchen.return_value = [_zeile()]
            WissenAgent()._befragen(_state())

        quelle = quelle_repo.suchen.call_args.args[0]
        dienst = dienst_repo.suchen.call_args.args[0]

        # Dieselbe Ordnung: Schwelle und Typ sind für beide Eingänge gleich.
        self.assertEqual(quelle.schwelle, dienst.schwelle)
        self.assertEqual(quelle.typ, dienst.typ)
        self.assertEqual(TYP_WISSEN, dienst.typ)
        # Verschieden ist allein die Tiefe.
        self.assertEqual(WISSEN_RETRIEVAL_TOP_K, quelle.limit)
        self.assertEqual(WISSEN_AUFTRAG_TOP_K,   dienst.limit)
        self.assertGreater(WISSEN_AUFTRAG_TOP_K, WISSEN_RETRIEVAL_TOP_K)

    def test_kein_eingang_traegt_eine_eigene_abfrage(self) -> None:
        """Die Abfrage steht an genau einer Stelle — sonst laufen sie auseinander."""
        wurzel = Path(__file__).resolve().parent.parent
        eingaenge = [
            wurzel / "plugins" / "wissen_manager" / "manager.py",
            *(wurzel / "agents" / "wissen").glob("*.py"),
        ]
        for datei in eingaenge:
            text: str = datei.read_text(encoding="utf-8")
            self.assertNotIn(
                "autonomous_wissen", text.replace("autonomous_wissen_repository", ""),
                f"{datei.name} traegt eine eigene Abfrage gegen den Bestand",
            )


class BefragungTest(unittest.TestCase):
    """Die vier Ausgänge, und dass sie nicht eingeebnet sind."""

    def setUp(self) -> None:
        """Ein Dienst je Zeuge — er hält keinen Zustand über den Lauf hinaus."""
        self.agent = WissenAgent()

    def test_treffer_ergeben_eine_auskunft_mit_fundstelle(self) -> None:
        """Eine Auskunft ohne Ort ist von einer Erfindung nicht zu unterscheiden."""
        from agents.wissen import agent as modul

        with patch.object(modul, "AutonomousWissenRepository") as repo:
            repo.suchen.return_value = [_zeile()]
            ergebnis: dict = self.agent._befragen(_state())

        self.assertEqual("abgeschlossen", ergebnis["status"])
        self.assertIn("/knowledge/autonomous/nova/", ergebnis["ergebnis"])
        self.assertIn("0.7200", ergebnis["ergebnis"])

    def test_jede_auskunft_nennt_ihre_tiefe(self) -> None:
        """Stufe 1 ist nicht Stufe 2 — und das gehört in den Text."""
        text: str = auskunft.auskunft_bauen([_zeile()])
        self.assertIn(auskunft.TIEFE_HINWEIS, text)

    def test_kein_treffer_ist_ein_urteil_mit_zahl(self) -> None:
        """„Dazu habe ich nichts" ohne Beleg ist keine Antwort (§6.8)."""
        from agents.wissen import agent as modul

        with patch.object(modul, "AutonomousWissenRepository") as repo:
            repo.suchen.side_effect = [[], [_zeile(cosine=0.3912)]]
            repo.zaehlen.return_value = 274
            ergebnis: dict = self.agent._befragen(_state())

        self.assertEqual("abgelehnt", ergebnis["status"])
        korrektur = ergebnis["parameter"]["korrektur"]
        self.assertIn("274", korrektur.beleg)
        self.assertIn("0.3912", korrektur.beleg)
        self.assertTrue(korrektur.befund.strip())
        self.assertTrue(korrektur.vorschlag.strip())

    def test_datenbankfehler_ist_eine_stoerung_und_keine_ablehnung(self) -> None:
        """§6a.2 — der eingeebnete Ausgang: „ich konnte nicht" ist kein Urteil."""
        from agents.wissen import agent as modul

        with patch.object(modul, "AutonomousWissenRepository") as repo:
            repo.suchen.side_effect = psycopg2.OperationalError("Verbindung weg")
            ergebnis: dict = self.agent._befragen(_state())

        self.assertEqual("fehler", ergebnis["status"])
        self.assertNotEqual("abgelehnt", ergebnis["status"])
        self.assertTrue(ergebnis["fehler"].strip())

    def test_ablehnung_ohne_zaehlbaren_bestand_bleibt_eine_ablehnung(self) -> None:
        """Ein Beleg, der nicht zu erheben ist, macht aus dem Urteil keine Störung."""
        from agents.wissen import agent as modul

        with patch.object(modul, "AutonomousWissenRepository") as repo:
            repo.suchen.side_effect = [[], psycopg2.OperationalError("weg")]
            repo.zaehlen.side_effect = psycopg2.OperationalError("weg")
            ergebnis: dict = self.agent._befragen(_state())

        self.assertEqual("abgelehnt", ergebnis["status"])
        self.assertIn("kein Beleg", ergebnis["parameter"]["korrektur"].beleg)

    def test_fehlender_suchschluessel_ist_eine_stoerung(self) -> None:
        """Die Bibliothek hat nur den Bedeutungskanal — ohne Vektor gibt es nichts."""
        ergebnis: dict = self.agent._validieren(_state(such_vektor=[]))
        self.assertEqual("fehler", ergebnis["status"])
        self.assertEqual(END_FREI, self.agent._nach_validierung({"status": "fehler"}))

    def test_unvollstaendiges_paar_ist_eine_stoerung(self) -> None:
        """Ein Treffer ohne Paar käme aus einer fremden Beziehung."""
        ergebnis: dict = self.agent._validieren(_state(paar=False))
        self.assertEqual("fehler", ergebnis["status"])

    def test_auskunft_ohne_treffer_wird_gemeldet_statt_geliefert(self) -> None:
        """„Nichts gefunden" gehört in den vierten Ausgang, nicht in leeren Text."""
        self.assertEqual("", auskunft.auskunft_bauen([]))


class DispatchTest(unittest.TestCase):
    """Jeder Rückkehrpfad setzt die Anzeigefelder."""

    def test_ohne_user_id_kein_lauf_und_trotzdem_ein_text(self) -> None:
        """Wer nur bei Erfolg schreibt, macht 'nicht gelaufen' unsichtbar."""
        from agents.wissen.dispatch import dispatch_wissen

        rueckgabe: dict = dispatch_wissen({"user_id": ""})
        self.assertEqual(1, len(rueckgabe["agent_results"]))
        self.assertEqual("fehler", rueckgabe["agent_results"][0].status)
        self.assertTrue(rueckgabe["management_result"].strip())
        self.assertEqual("", rueckgabe["agent_name"])

    def test_ablehnung_ohne_korrektur_wird_zur_stoerung(self) -> None:
        """Eine Ablehnung ohne Vorschlag ist eine Sackgasse."""
        from agents.wissen import dispatch as modul

        with patch.object(modul, "AgentRegistry") as registry, \
             patch.object(modul, "reiz_text", return_value="egal"):
            registry.finden.return_value.invoke.return_value = {
                "status": "abgelehnt", "parameter": {}, "schritte": [],
            }
            rueckgabe: dict = modul.dispatch_wissen(
                {"user_id": PAAR_USER, "such_vektor": [0.1]}
            )
        self.assertEqual("fehler", rueckgabe["agent_results"][0].status)

    def test_der_suchschluessel_wandert_in_den_kontext(self) -> None:
        """Ohne ihn hat der Dienst gar keinen Kanal (§6a.1)."""
        from agents.wissen import dispatch as modul

        with patch.object(modul, "AgentRegistry") as registry, \
             patch.object(modul, "reiz_text", return_value="egal"):
            registry.finden.return_value.invoke.return_value = {
                "status": "abgeschlossen", "ergebnis": "Text",
                "parameter": {}, "schritte": [],
            }
            modul.dispatch_wissen({"user_id": PAAR_USER, "such_vektor": [0.4, 0.5]})
            uebergeben = registry.finden.return_value.invoke.call_args[0][0]
        self.assertEqual([0.4, 0.5], uebergeben["kontext"]["such_vektor"])


class SchreibpfadTest(unittest.TestCase):
    """Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden."""

    def test_der_dienst_importiert_keinen_schreibpfad(self) -> None:
        """Nicht 'benutzt ihn nicht', sondern importiert ihn nicht."""
        verboten: tuple[str, ...] = ("speichern", "datei_schreiben", "redaktion")
        wurzel = Path(__file__).resolve().parent.parent / "agents" / "wissen"
        for datei in sorted(wurzel.glob("*.py")):
            baum = ast.parse(datei.read_text(encoding="utf-8"))
            for knoten in ast.walk(baum):
                if isinstance(knoten, ast.ImportFrom):
                    for alias in knoten.names:
                        self.assertNotIn(
                            alias.name, verboten,
                            f"{datei.name} importiert '{alias.name}'",
                        )

if __name__ == "__main__":
    unittest.main()
