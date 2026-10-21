"""Zeugen für den Fakten-Agenten: vom Subgraphen bis zur Zeile in `fakten`.

Was diese Datei zusichert:
  * **Eine Beziehung des Kanons wird genau ein Fakt** mit Paar und Herkunft
    `mensch`; eine einwertige löst ab, eine mehrwertige fügt hinzu, derselbe
    Wert schreibt nichts.
  * **Ohne Beziehung im Kanon lehnt der Dienst ab** (`rejected`) und
    schreibt nichts.
  * **Zwei gleichnamige Entitäten ergeben eine Rückfrage**, nie eine
    Ablehnung, und es wird nichts geschrieben und nichts angelegt.
  * **Ein Fehler der Namenssuche ist `fehler`** und legt keine Entität an.
  * **`abgeschlossen` nur nach bestandener Verifikation.**
  * **Anmeldung und Brett:** `fakten` ist ein Dienst der Queue, ohne
    Objekt-Merkmal und ohne Dispatch des Planners; das Brett trägt keinen
    Zettel für ihn, und das Plugin hat weder Text noch Intent.
  * **Die Wand:** Unter `agents/fakten/` kein Import aus `tools.` und kein
    `psycopg2`.

Die Klassifikation antwortet aus einem festen Modellausgang; kein Zeuge ruft
ein Modell. Die Datenbank ist die Wegwerf-Datenbank der Suite; jedes Fixture
bringt ein eigenes Paar mit und räumt in tearDown ab.
"""

import re
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras
from langgraph.graph import END

import agents.fakten
from agents import AgentRegistry, discover_agents, get_dispatch
from agents.fakten.agent import FactsAgent
from agents.fakten.bestaetigung import confirm
from agents.fakten.beziehungen import KANON
from agents.fakten.klassifikation import build_classify_prompt, check_answer, classify
from agents.fakten.suche import UNTERSCHEIDUNG_BITTE
from agents.nmcp import anmelden, aushaenge_sammeln
from config import POSTGRES_URL
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.repositories.fakten_repository import FaktenRepository
from plugins import discover_managers
from plugins.fakten_manager.manager import FaktenManager
from plugins.notizen_manager.manager import NotizenManager

VEKTOR: list[float] = [1.0] + [0.0] * 767
_MARKE: re.Pattern[str] = re.compile(r"^[A-Z][A-Z-]+-ERKENNUNG:", re.M)
_WAND: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*(?:from|import)\s+tools\b", re.M),
    re.compile(r"\bpsycopg2\b"),
)


def _ausfuehren(sql: str, params: tuple) -> list[dict]:
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            zeilen: list[dict] = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return zeilen
    finally:
        conn.close()


def _wandverstoesse(quelltext: str) -> list[str]:
    """Nennt jedes Muster der Wand, das im Quelltext vorkommt."""
    return [muster.pattern for muster in _WAND if muster.search(quelltext)]


def _block(brett: str, marke: str) -> str:
    """Schneidet den Block einer Marke aus dem Brett — bis zur nächsten Marke."""
    anfaenge: list[int] = [m.start() for m in _MARKE.finditer(brett)]
    start: int = brett.index(marke)
    folgende: list[int] = [a for a in anfaenge if a > start]
    return brett[start:folgende[0]] if folgende else brett[start:]


def _zustand(aufgabe: str = "merk dir, dass Ilva in Ostheim wohnt") -> dict:
    return {
        "aufgabe": aufgabe, "aufgabe_typ": "workflow", "agent_name": "fakten",
        "kontext": {"user_id": "u", "character_id": "c"}, "parameter": {},
        "schritte": [], "ergebnis": None, "status": "laufend",
        "rueckfrage": None, "fehler": None,
    }


class AgentWritesAFactTest(unittest.TestCase):
    """Der Weg im Subgraphen: Klassifikation → Suche → Schreiben → Verifikation."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def setUp(self) -> None:
        self.user = f"test-faktagent-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"
        self.modell = MagicMock()
        ersatz = patch("agents.fakten.klassifikation.model_service", self.modell)
        ersatz.start()
        self.addCleanup(ersatz.stop)
        einbettung = MagicMock()
        einbettung.embed.submit_sync.return_value.embedding = VEKTOR
        einbettung.embed.submit_sync.return_value.duration_seconds = 0.0
        ersatz = patch("memory.services.entity_resolution.model_service", einbettung)
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def tearDown(self) -> None:
        _ausfuehren("DELETE FROM fakten WHERE user_id = %s", (self.user,))
        _ausfuehren("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _entitaet(self, name: str, typ: str = "person") -> int:
        return _ausfuehren(
            "INSERT INTO entitaeten (user_id, name, typ) VALUES (%s, %s, %s) RETURNING id",
            (self.user, name, typ),
        )[0]["id"]

    def _fakten(self) -> list[dict]:
        return _ausfuehren("SELECT * FROM fakten WHERE user_id = %s ORDER BY id", (self.user,))

    def _entitaeten(self) -> list[dict]:
        return _ausfuehren(
            "SELECT id, name, typ FROM entitaeten WHERE user_id = %s ORDER BY id", (self.user,),
        )

    def _laufen(self, antwort: dict, bitte: str) -> tuple[dict, SimpleNamespace]:
        # Die Bitte trägt die Namen der Antwort: Die Klassifikation hält beide
        # gegeneinander und verwirft eine Antwort, deren Namen nicht dastehen.
        # Der Auftrag geht direkt an den Subgraphen.
        self.modell.chat.submit_sync.return_value.parsed = antwort
        zustand: dict = _zustand(bitte)
        zustand["kontext"] = {"user_id": self.user, "character_id": self.char}
        aus: dict = AgentRegistry.finden("fakten").invoke(zustand)
        return aus, SimpleNamespace(**aus)

    def test_a_relation_of_the_canon_writes_one_fact_with_pair_and_origin(self) -> None:
        ilva = self._entitaet("Ilva")
        _, ergebnis = self._laufen({
            "action": "speichern", "subjekt": "Ilva", "beziehung": "wohnt_in", "objekt": "Ostheim",
        }, bitte="merk dir, dass Ilva in Ostheim wohnt")
        self.assertEqual(ergebnis.status, "abgeschlossen", ergebnis.fehler)
        ostheim = [e for e in self._entitaeten() if e["name"] == "Ostheim"]
        self.assertEqual([e["typ"] for e in ostheim], ["ort"])
        zeilen = self._fakten()
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(
            {k: zeilen[0][k] for k in ("user_id", "character_id", "subjekt_id", "attribut",
                                         "objekt_id", "herkunft", "t_invalid")},
            {"user_id": self.user, "character_id": self.char, "subjekt_id": ilva,
             "attribut": "wohnt_in", "objekt_id": ostheim[0]["id"], "herkunft": "mensch",
             "t_invalid": None},
        )

    def test_a_single_valued_relation_replaces_the_old_value(self) -> None:
        self._entitaet("Ilva")
        self._laufen({"subjekt": "Ilva", "beziehung": "arbeitet_als", "objekt": "Tischlerin"},
                     bitte="merk dir, dass Ilva als Tischlerin arbeitet")
        _, ergebnis = self._laufen(
            {"subjekt": "Ilva", "beziehung": "arbeitet_als", "objekt": "Imkerin"},
            bitte="merk dir, dass Ilva jetzt als Imkerin arbeitet",
        )
        self.assertEqual(ergebnis.status, "abgeschlossen", ergebnis.fehler)
        zeilen = self._fakten()
        self.assertEqual([z["objekt_wert"] for z in zeilen], ["Tischlerin", "Imkerin"])
        self.assertEqual([z["t_invalid"] is None for z in zeilen], [False, True])

    def test_a_multi_valued_relation_adds_and_the_same_value_writes_nothing(self) -> None:
        self._entitaet("Ilva")
        rufus: str = "merk dir, dass Ilva einen Hund namens Rufus hat"
        self._laufen({"subjekt": "Ilva", "beziehung": "hat_haustier", "objekt": "Rufus"},
                     bitte=rufus)
        self._laufen({"subjekt": "Ilva", "beziehung": "hat_haustier", "objekt": "Merle"},
                     bitte="merk dir, dass Ilva auch Merle hat, eine Katze")
        _, ergebnis = self._laufen(
            {"subjekt": "Ilva", "beziehung": "hat_haustier", "objekt": "Rufus"}, bitte=rufus,
        )
        self.assertEqual(ergebnis.status, "abgeschlossen", ergebnis.fehler)
        self.assertTrue(str(ergebnis.ergebnis).startswith("Das weiß ich schon"))
        zeilen = self._fakten()
        self.assertEqual(len(zeilen), 2)
        self.assertTrue(all(z["t_invalid"] is None for z in zeilen))

    def test_without_a_relation_of_the_canon_it_refuses_and_writes_nothing(self) -> None:
        aus, ergebnis = self._laufen(
            {"action": "speichern", "subjekt": "ICH", "beziehung": "braucht", "objekt": "Mehl"},
            bitte="merk dir, dass wir Mehl brauchen",
        )
        self.assertEqual(ergebnis.status, "rejected")
        self.assertIn("braucht", aus["schritte"][-1]["ergebnis"])
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), [])

    def test_a_rejection_by_the_model_is_a_refusal(self) -> None:
        aus, ergebnis = self._laufen({"action": "rejected", "grund": "Einkaufsliste"},
                                     bitte="merk dir, dass wir Mehl brauchen")
        self.assertEqual(ergebnis.status, "rejected")
        self.assertIn("Einkaufsliste", aus["schritte"][-1]["ergebnis"])
        self.assertEqual(self._fakten(), [])

    def test_two_lenas_ask_back_and_write_nothing(self) -> None:
        self._entitaet("Lena")
        self._entitaet("Lena")
        vorher = self._entitaeten()
        _, ergebnis = self._laufen(
            {"subjekt": "Lena", "beziehung": "hat_haustier", "objekt": "Rufus"},
            bitte="merk dir, dass Lena einen Hund namens Rufus hat",
        )
        self.assertEqual(ergebnis.status, "rueckfrage")
        self.assertIn("Lena", ergebnis.rueckfrage)
        self.assertTrue(ergebnis.rueckfrage.endswith(UNTERSCHEIDUNG_BITTE))
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), vorher)

    def test_a_question_back_leaves_no_waiting_state(self) -> None:
        # Ohne Wartezustand kennt kein Modul des Dienstes einen Speicher, in dem ein
        # `pending_agent:*` entstehen könnte; das Muster mit Wartezustand schon.
        from agents.notizen import dispatch as notizen_dispatch
        for quelle in Path(agents.fakten.__file__).parent.glob("*.py"):
            self.assertNotIn("redis_manager", quelle.read_text(encoding="utf-8"), quelle.name)
        self.assertTrue(hasattr(notizen_dispatch, "redis_manager"))

    def test_a_failed_name_search_is_an_error_and_creates_nothing(self) -> None:
        fehler = psycopg2.OperationalError("Verbindung verloren")
        with patch.object(EntitaetenRepository, "find_by_name", side_effect=fehler):
            _, ergebnis = self._laufen(
                {"subjekt": "Ilva", "beziehung": "wohnt_in", "objekt": "Ostheim"},
                bitte="merk dir, dass Ilva in Ostheim wohnt",
            )
        self.assertEqual(ergebnis.status, "fehler")
        self.assertIn("Namenssuche", ergebnis.fehler)
        self.assertEqual(self._entitaeten(), [])
        self.assertEqual(self._fakten(), [])

    def test_a_failed_verification_is_an_error_never_completed(self) -> None:
        self._entitaet("Ilva")
        with patch.object(FaktenRepository, "find_by_id", return_value=None):
            _, ergebnis = self._laufen(
                {"subjekt": "Ilva", "beziehung": "wohnt_in", "objekt": "Ostheim"},
                bitte="merk dir, dass Ilva in Ostheim wohnt",
            )
        self.assertEqual(ergebnis.status, "fehler")
        self.assertIn("nicht bestaetigt", ergebnis.fehler)
        self.assertFalse(str(ergebnis.ergebnis).startswith("Gemerkt"))

    def test_an_object_with_a_verb_writes_nothing_and_is_loud(self) -> None:
        with self.assertLogs("ki_server.agents.fakten.klassifikation", "ERROR") as protokoll:
            _, ergebnis = self._laufen(
                {"action": "speichern", "subjekt": "ICH", "beziehung": "hat_nachbar",
                 "objekt": "Merten heisst"},
                bitte="Merk dir, dass mein Nachbar Merten heißt.",
            )
        self.assertEqual(ergebnis.status, "fehler")
        self.assertIn("verworfen", ergebnis.fehler)
        self.assertIn("'Merten heisst'", ergebnis.fehler)
        self.assertTrue(any("verworfen" in zeile for zeile in protokoll.output), protokoll.output)
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), [])

    def test_a_name_only_in_the_genitive_writes_nothing(self) -> None:
        vorher = [self._entitaet("Merten")]
        _, ergebnis = self._laufen(
            {"action": "speichern", "subjekt": "Mertens", "beziehung": "hat_schwester",
             "objekt": "Ilva"},
            bitte="Merk dir: Mertens Schwester heißt Ilva.",
        )
        self.assertEqual(ergebnis.status, "fehler")
        self.assertIn("verworfen", ergebnis.fehler)
        self.assertIn("Genitiv", ergebnis.fehler)
        self.assertEqual(self._fakten(), [])
        self.assertEqual([e["id"] for e in self._entitaeten()], vorher)

    def test_the_base_form_binds_the_existing_entity(self) -> None:
        # Zwilling zu den beiden Verwerfungen: dieselbe Bitte, richtig gelesen.
        merten = self._entitaet("Merten")
        _, ergebnis = self._laufen(
            {"action": "speichern", "subjekt": "Merten", "beziehung": "hat_schwester",
             "objekt": "Ilva"},
            bitte="Merk dir: Mertens Schwester heißt Ilva.",
        )
        self.assertEqual(ergebnis.status, "abgeschlossen", ergebnis.fehler)
        zeilen = self._fakten()
        self.assertEqual([(z["subjekt_id"], z["attribut"]) for z in zeilen],
                         [(merten, "hat_schwester")])
        self.assertEqual(sorted(e["name"] for e in self._entitaeten()), ["Ilva", "Merten"])


class FactsAgentNodesTest(unittest.TestCase):
    """Die Knoten ohne Datenbank: Validierung, Weichen, Klassifikation, Abschluss."""

    def setUp(self) -> None:
        self.agent = FactsAgent()

    def test_validation_needs_task_and_pair(self) -> None:
        self.assertEqual(self.agent._validate(_zustand())["status"], "laufend")
        ohne_paar = {**_zustand(), "kontext": {"user_id": "u"}}
        self.assertEqual(self.agent._validate(ohne_paar)["status"], "fehler")
        self.assertEqual(self.agent._validate(_zustand("  "))["status"], "fehler")

    def test_the_switches_end_on_rejection_question_and_error(self) -> None:
        def mit(status: str) -> dict:
            return {**_zustand(), "status": status}
        self.assertEqual(self.agent._after_validation(mit("laufend")), "klassifizieren")
        self.assertEqual(self.agent._after_validation(mit("fehler")), END)
        self.assertEqual(self.agent._after_classification(mit("laufend")), "suchen")
        self.assertEqual(self.agent._after_classification(mit("rejected")), END)
        self.assertEqual(self.agent._after_search(mit("laufend")), "ausfuehren")
        self.assertEqual(self.agent._after_search(mit("rueckfrage")), END)
        self.assertEqual(self.agent._after_search(mit("fehler")), END)

    def test_the_prompt_names_every_relation_of_the_canon(self) -> None:
        prompt = build_classify_prompt()
        self.assertTrue(all(f"  - {a}\n" in prompt for a in KANON))
        self.assertNotIn("  - ist_ein\n", prompt)

    def test_the_prompt_carries_direction_base_form_and_no_invention(self) -> None:
        prompt = build_classify_prompt()
        for regel in (
            '"X beziehung Y" heisst: Y ist die Beziehung von X.',
            "der ist das SUBJEKT",
            'Nie im Genitiv: aus "Ilvas" wird "Ilva"',
            'nie mit einem Verb ("Merten heisst")',
            "erfindest du nicht",
            'subjekt "Merten", beziehung "hat_mutter", objekt "Ilva"',
        ):
            with self.subTest(regel=regel):
                self.assertIn(regel, prompt)

    def test_an_answer_without_object_is_an_error_not_a_refusal(self) -> None:
        modell = MagicMock()
        modell.chat.submit_sync.return_value.parsed = {"subjekt": "Ilva", "beziehung": "wohnt_in"}
        with patch("agents.fakten.klassifikation.model_service", modell):
            self.assertEqual(classify(_zustand())["status"], "fehler")
            modell.chat.submit_sync.return_value.parsed = {
                "subjekt": "Ilva", "beziehung": "WOHNT_IN", "objekt": "Ostheim",
            }
            aenderung = classify(_zustand())
        self.assertNotIn("status", aenderung)
        self.assertEqual(aenderung["parameter"]["beziehung"], "wohnt_in")

    def test_a_model_failure_is_an_error(self) -> None:
        modell = MagicMock()
        modell.chat.submit_sync.side_effect = TimeoutError("Modell antwortet nicht")
        with patch("agents.fakten.klassifikation.model_service", modell):
            self.assertEqual(classify(_zustand())["status"], "fehler")

    def test_confirmation_never_invents_a_success(self) -> None:
        self.assertEqual(confirm({**_zustand(), "status": "laufend"})["status"], "fehler")
        self.assertNotIn("status", confirm({**_zustand(), "status": "abgeschlossen"}))
        self.assertNotIn("status", confirm({**_zustand(), "status": "rueckfrage"}))


class AnswerCheckTest(unittest.TestCase):
    """`check_answer` ohne Datenbank: je Verwerfung ein Zwilling, der durchgeht."""

    def _pruefen(self, bitte: str, subjekt: str, beziehung: str, objekt: str) -> str | None:
        return check_answer(bitte, subjekt, KANON[beziehung], objekt)

    def test_a_reversed_genitive_is_rejected(self) -> None:
        bitte = "Merk dir, dass Ilvas Bruder Merten ist."
        self.assertIn("vertauscht", self._pruefen(bitte, "Merten", "hat_bruder", "Ilva"))
        self.assertIsNone(self._pruefen(bitte, "Ilva", "hat_bruder", "Merten"))

    def test_a_reversed_of_is_rejected(self) -> None:
        bitte = "Merk dir, dass Merten der Freund von Ilva ist."
        self.assertIn("vertauscht", self._pruefen(bitte, "Merten", "hat_freund", "Ilva"))
        self.assertIsNone(self._pruefen(bitte, "Ilva", "hat_freund", "Merten"))

    def test_an_inversion_with_an_invented_gender_is_rejected(self) -> None:
        bitte = "Merk dir, dass Ilva die Mutter von Merten ist."
        self.assertIn("vertauscht", self._pruefen(bitte, "Ilva", "hat_sohn", "Merten"))
        self.assertIsNone(self._pruefen(bitte, "Merten", "hat_mutter", "Ilva"))

    def test_a_phrase_as_subject_is_rejected(self) -> None:
        bitte = "Merk dir, dass die Mutter von Merten Ilva heißt."
        self.assertIn("steht so nicht", self._pruefen(bitte, "Mertens Mutter", "heisst", "Ilva"))
        self.assertIsNone(self._pruefen(bitte, "Merten", "hat_mutter", "Ilva"))

    def test_the_possessor_does_not_carry_the_name_of_another(self) -> None:
        bitte = "Merk dir, dass Ilvas Hund Rufus heißt."
        self.assertIn("Besitzer", self._pruefen(bitte, "Ilva", "heisst", "Rufus"))
        self.assertIsNone(self._pruefen(bitte, "Ilva", "hat_haustier", "Rufus"))

    def test_the_self_needs_the_first_person(self) -> None:
        self.assertIn("nicht von dir", self._pruefen(
            "Merk dir, dass Ilva in Ostheim wohnt.", "ICH", "wohnt_in", "Ostheim"))
        self.assertIsNone(self._pruefen(
            "Merk dir, dass ich in Ostheim wohne.", "ICH", "wohnt_in", "Ostheim"))

    def test_the_genitive_form_alone_is_rejected_the_base_form_passes(self) -> None:
        bitte = "Merk dir: Mertens Schwester heißt Ilva."
        self.assertIn("Genitiv", self._pruefen(bitte, "Mertens", "hat_schwester", "Ilva"))
        self.assertIsNone(self._pruefen(bitte, "Merten", "hat_schwester", "Ilva"))

    def test_a_request_in_lower_case_still_needs_the_name(self) -> None:
        bitte = "merk dir, dass ilva in ostheim wohnt"
        self.assertIsNone(self._pruefen(bitte, "Ilva", "wohnt_in", "Ostheim"))
        self.assertIn("steht so nicht", self._pruefen(bitte, "Merten", "wohnt_in", "Ostheim"))


class RegistrationAndBoardTest(unittest.TestCase):
    """`fakten` ist in der Registry, aber kein Dienst am Empfang und ohne Zettel am Brett."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def test_the_registry_knows_fakten_as_a_queue_service_without_an_object_feature(self) -> None:
        agent = AgentRegistry.finden("fakten")
        self.assertIsInstance(agent, FactsAgent)
        self.assertEqual(agent.zustellart, "queue")
        self.assertEqual(agent.objekt_merkmal, "")
        # Zwilling: die Nachbarn behalten ihre Zustellart.
        self.assertEqual(AgentRegistry.finden("kzg").zustellart, "queue")
        self.assertEqual(AgentRegistry.finden("notizen").zustellart, "empfang")

    def test_the_handshake_reports_no_defect_for_fakten(self) -> None:
        befund = anmelden(AgentRegistry.finden("fakten"))
        self.assertTrue(befund.eingebunden, befund.maengel)
        self.assertEqual(list(befund.maengel), [])

    def test_the_board_carries_no_slip_for_fakten_but_still_the_one_for_notizen(self) -> None:
        brett = aushaenge_sammeln("user")
        self.assertNotIn("FAKTEN-ERKENNUNG:", brett)
        for negativ in FactsAgent().negativfaelle:
            self.assertNotIn(negativ, brett)
        # Zwilling: Der Block der Notizen steht unverändert am Brett.
        self.assertIn("NOTIZEN-ERKENNUNG:", brett)
        self.assertIn("NICHT zustellen bei:", _block(brett, "NOTIZEN-ERKENNUNG:"))

    def test_the_planner_has_no_dispatch_for_fakten(self) -> None:
        self.assertIsNone(get_dispatch("fakten"))
        # Zwilling: Ein Dienst am Empfang behält seinen Dispatch.
        self.assertIsNotNone(get_dispatch("notizen"))


class PluginHasNoSlipTest(unittest.TestCase):
    """Das Plugin `fakten_manager` hat keinen Platz mehr am Brett des Routers."""

    def test_the_plugin_has_neither_a_prompt_nor_an_intent(self) -> None:
        manager = FaktenManager()
        self.assertEqual(manager.router_prompt.strip(), "")
        self.assertEqual(manager.router_intents, [])

    def test_the_twin_plugin_of_the_notes_keeps_both(self) -> None:
        manager = NotizenManager()
        self.assertIn("NOTIZEN-ERKENNUNG:", manager.router_prompt)
        self.assertNotEqual(manager.router_intents, [])


class TheWallTest(unittest.TestCase):
    """Unter `agents/fakten/` kein Import aus `tools.` und kein `psycopg2`."""

    def test_no_module_of_the_agent_crosses_the_wall(self) -> None:
        quellen = sorted(Path(agents.fakten.__file__).parent.glob("*.py"))
        self.assertGreaterEqual(len(quellen), 7)
        for quelle in quellen:
            self.assertEqual(_wandverstoesse(quelle.read_text(encoding="utf-8")), [], quelle.name)

    def test_the_wall_recognises_both_crossings(self) -> None:
        verstoss = "from tools.redis_manager import redis_manager\nimport psycopg2\n"
        self.assertEqual(len(_wandverstoesse(verstoss)), 2)


if __name__ == "__main__":
    unittest.main()
