"""Zeugen für den Fakten-Agenten: vom Auftrag des Turns bis zur Zeile in `fakten`.

Was diese Datei zusichert:
  * **Ein Modellaufruf je Auftrag mit Kandidaten des Menschen**, und nur
    diese Kandidaten gehen hinein; ohne sie kein Aufruf und der Ausgang
    `nur_andere_sprecher`.
  * **Eine dauerhafte Aussage wird ein Fakt, mit Bitte und ohne**, mit Paar
    und der Herkunft aus dem Sprecher des Kandidaten; eine einwertige
    Beziehung löst ab, derselbe Wert schreibt nichts (`identisch`).
  * **Jedes Tripel hat seinen Ausgang**; was die Prüfung nicht besteht, ist
    `verworfen:<grund>` und schreibt nichts.
  * **Das Subjekt nimmt die Entität, an die das Objekt gebunden ist**, sonst
    die Namenssuche; zwei gleichnamige Entitäten ergeben `mehrdeutig`,
    ohne Text, und es wird nichts geschrieben und nichts angelegt.
  * **Ein Ausfall des Modells ist ein Ausfall**, nie *kein Tripel*.
  * **`abgeschlossen` nur nach bestandener Verifikation.**
  * **Anmeldung und Brett:** `fakten` ist ein Dienst der Queue, ohne
    Objekt-Merkmal, ohne Aushang und ohne Dispatch des Planners; das Brett
    trägt keinen Zettel für ihn.
  * **Kein Manager `fakten`:** Die Registry der Manager kennt den Namen nicht;
    ein Router-Ziel `fakten` führt den Planner laut zu den Notizen, und der
    Enricher ruft jeden registrierten Manager, gleich wie er heißt.
  * **Die Wand:** Unter `agents/fakten/` kein Import aus `tools.` und kein
    `psycopg2`.

Die Klassifikation antwortet aus einem festen Modellausgang; kein Zeuge ruft
ein Modell. Die Kandidaten des Turns sind ersetzt (`turn_candidates`), der
Eintrag `log_db_write` wird abgefangen. Die Datenbank ist die
Wegwerf-Datenbank der Suite; jedes Fixture bringt ein eigenes Paar mit und
räumt in tearDown ab.
"""

import importlib
import re
import unittest
import uuid
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras
from langgraph.graph import END

import agents.fakten
import graph.nodes.enricher as enricher_mod
from agents import AgentRegistry, discover_agents, get_dispatch
from agents.fakten import dispatch as fakten_dispatch_mod
from agents.fakten import suche as suche_mod
from agents.fakten.agent import FactsAgent
from agents.fakten.bestaetigung import confirm
from agents.fakten.beziehungen import KANON
from agents.fakten.klassifikation import (
    AnswerFormError,
    ModelCallError,
    build_classify_prompt,
    check_answer,
    classify_candidates,
    vet_triple,
)
from agents.fakten.suche import binding_for
from agents.nmcp import anmelden, aushaenge_sammeln
from config import POSTGRES_URL
from ei.gravitation import Gravitationsterm
from graph.nodes import planner
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.repositories.fakten_repository import FaktenRepository
from memory.services import entity_resolution as entity_resolution_mod
from plugins import discover_managers, get_registry

VEKTOR: list[float] = [1.0] + [0.0] * 767
_MARKE: re.Pattern[str] = re.compile(r"^[A-Z][A-Z-]+-ERKENNUNG:", re.M)
_WAND: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*(?:from|import)\s+tools\b", re.M),
    re.compile(r"\bpsycopg2\b"),
)
_AUFTRAG: dict = {"ziel": "fakten", "aktion": "pruefen", "daten": {
    "turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.62,
    "user_intentionen": ["mitteilen"], "abgelegt": True,
}}


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


def _kandidat(objekt: str, eigenschaft: str, wert: str, **felder: object) -> dict:
    """Ein Kandidat wie aus `turn_candidates`; `felder` setzt etwa sprecher und klasse."""
    kandidat: dict = {"id": 1, "objekt_id": 1, "objekt": objekt, "klasse": "person",
                      "entitaet_id": None, "entitaet_bindung": None,
                      "eigenschaft": eigenschaft, "wert": wert, "sprecher": "nutzer"}
    kandidat.update(felder)
    if kandidat["entitaet_id"] is not None:
        kandidat["entitaet_bindung"] = "turn_magnet"
    return kandidat


def _antwort(*tripel: tuple, dauerhaft: bool = True) -> dict:
    """Eine Antwort des Modells: je Tripel (kandidat, subjekt, beziehung, objekt)."""
    return {"dauerhafte_aussage": dauerhaft, "grund": "Probe", "tripel": [
        {"kandidat": k, "subjekt": s, "beziehung": b, "objekt": o} for k, s, b, o in tripel
    ]}


def _zustand(parameter: dict | None = None) -> dict:
    return {
        "aufgabe": "Ilva wohnt in Ostheim", "aufgabe_typ": "workflow", "agent_name": "fakten",
        "kontext": {"user_id": "u", "character_id": "c"},
        "parameter": parameter if parameter is not None else {
            "subjekt": "Ilva", "beziehung": "wohnt_in", "objekt": "Ostheim",
            "herkunft": "mensch", "kandidat": 1, "subjekt_entitaet_id": None,
        },
        "schritte": [], "ergebnis": None, "status": "laufend",
        "rueckfrage": None, "fehler": None,
    }


class _OrderRun(unittest.TestCase):
    """Fährt einen Auftrag durch `process_fact_orders` — Kandidaten und Modell ersetzt."""

    user: str = "u"
    char: str = "c"

    def setUp(self) -> None:
        self.modell = MagicMock()
        ersatz = patch("agents.fakten.klassifikation.model_service", self.modell)
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def _laufen(self, aeusserung: str, kandidaten: list[dict],
                antwort: dict | None = None) -> tuple[dict, dict]:
        """(Ausgang, Inhalt des einen Eintrags `log_db_write`)."""
        self.modell.chat.submit_sync.return_value.parsed = antwort
        zustand: dict = {"user_id": self.user, "character_id": self.char,
                         "turn_id": "probe-turn", "user_prompt": aeusserung}
        with patch.object(fakten_dispatch_mod, "turn_candidates", return_value=kandidaten), \
             patch.object(fakten_dispatch_mod, "log_db_write") as eintrag:
            ausgang: dict = fakten_dispatch_mod.process_fact_orders(
                zustand, [_AUFTRAG], POSTGRES_URL,
            )[0]
        eintrag.assert_called_once()
        return ausgang, eintrag.call_args.kwargs["inhalt"]

    def _nachricht(self) -> str:
        """Die Nachricht des einen Modellaufrufs."""
        self.assertEqual(self.modell.chat.submit_sync.call_count, 1)
        return self.modell.chat.submit_sync.call_args.args[0].messages[0]["content"]


class OrderInputTest(_OrderRun):
    """V4, die Eingabe: ein Aufruf je Auftrag, nur mit den Kandidaten des Menschen."""

    def test_one_call_carries_exactly_the_candidate_of_the_human(self) -> None:
        kandidaten = [_kandidat("Ilva", "Wohnort", "Ostheim"),
                      _kandidat("Vela-Pulsar", "Periode", "89 ms", sprecher="nova",
                                klasse="sache")]
        ausgang, _ = self._laufen("Ilva ist übrigens nach Ostheim gezogen", kandidaten,
                                  _antwort())
        nachricht = self._nachricht()
        self.assertIn("[1] Objekt: Ilva (Klasse: person) | Eigenschaft: Wohnort | Wert: Ostheim",
                      nachricht)
        self.assertIn("Ilva ist übrigens nach Ostheim gezogen", nachricht)
        self.assertNotIn("Vela-Pulsar", nachricht)
        self.assertNotIn("[2]", nachricht)
        self.assertEqual(ausgang["ausgang"], "kein_tripel")

    def test_without_a_candidate_of_the_human_no_call_and_its_own_outcome(self) -> None:
        # Zwilling: nur Novas Kandidat und einer ohne Sprecher.
        kandidaten = [_kandidat("Vela-Pulsar", "Periode", "89 ms", sprecher="nova"),
                      _kandidat("Rotverschiebung", "Ursache", "Expansion", sprecher=None)]
        ausgang, inhalt = self._laufen("Wie entsteht die Rotverschiebung?", kandidaten,
                                       _antwort())
        self.assertEqual(self.modell.chat.submit_sync.call_count, 0)
        self.assertEqual(ausgang["ausgang"], "nur_andere_sprecher")
        self.assertEqual((inhalt["ausgang"], inhalt["kandidaten"], inhalt["je_sprecher"]),
                         ("nur_andere_sprecher", 2, {"nova": 1, "ohne": 1}))
        self.assertEqual(inhalt["salienz_human"], 0.62)


class ModelFailureTest(_OrderRun):
    """V5: Ein Ausfall des Modells ist ein eigener Ausgang, nie *kein Tripel*."""

    def test_a_model_that_raises_is_a_failure_and_the_entry_stands(self) -> None:
        self.modell.chat.submit_sync.side_effect = TimeoutError("Modell antwortet nicht")
        with patch.object(FactsAgent, "invoke") as agent:
            ausgang, inhalt = self._laufen("Ilva ist nach Ostheim gezogen",
                                           [_kandidat("Ilva", "Wohnort", "Ostheim")])
        self.assertEqual(ausgang["ausgang"], "modell_ausfall")
        self.assertEqual(inhalt["ausgang"], "modell_ausfall")
        self.assertIn("TimeoutError", inhalt["fehler"])
        agent.assert_not_called()

    def test_an_answer_without_its_form_is_a_failure_too(self) -> None:
        with patch.object(FactsAgent, "invoke") as agent:
            ausgang, _ = self._laufen("Ilva ist nach Ostheim gezogen",
                                      [_kandidat("Ilva", "Wohnort", "Ostheim")],
                                      {"subjekt": "Ilva", "beziehung": "wohnt_in"})
        self.assertEqual(ausgang["ausgang"], "antwort_defekt")
        agent.assert_not_called()

    def test_an_answer_without_triples_is_no_triple_not_a_failure(self) -> None:
        # Zwilling: eine Antwort in Form, ohne Tripel.
        ausgang, inhalt = self._laufen("Sei ab jetzt frecher, Nova",
                                       [_kandidat("Nova", "Ton", "frecher")],
                                       _antwort(dauerhaft=False))
        self.assertEqual(ausgang["ausgang"], "kein_tripel")
        self.assertEqual((inhalt["tripel_zahl"], inhalt["dauerhaft"]), (0, False))


class AgentWritesAFactTest(_OrderRun):
    """Gegen die Datenbank: Auftrag → Klassifikation → Suche → Schreiben → Verifikation."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def setUp(self) -> None:
        super().setUp()
        self.user = f"test-faktagent-{uuid.uuid4().hex[:8]}"
        self.char = "nova-test"
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

    def _ein_tripel(self, aeusserung: str, subjekt: str, beziehung: str, objekt: str,
                    kandidat: dict | None = None) -> dict:
        """Ein Kandidat, ein Tripel darauf; der Eintrag des Tripels."""
        kandidat = kandidat or _kandidat(subjekt, beziehung, objekt)
        _, inhalt = self._laufen(aeusserung, [kandidat],
                                 _antwort((1, subjekt, beziehung, objekt)))
        self.assertEqual(inhalt["tripel_zahl"], 1, inhalt)
        return inhalt["tripel"][0]

    # --- Schreiben, mit Bitte und ohne ---

    def test_a_statement_without_a_request_writes_one_fact_of_the_human(self) -> None:
        ilva = self._entitaet("Ilva")
        tripel = self._ein_tripel("Ilva ist übrigens nach Ostheim gezogen",
                                  "Ilva", "wohnt_in", "Ostheim",
                                  _kandidat("Ilva", "Wohnort", "Ostheim"))
        self.assertEqual(tripel["ausgang"], "angelegt")
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

    def test_a_new_place_replaces_and_the_same_place_is_identical(self) -> None:
        # Zwilling: vorher Kassel → abgeloest; noch einmal Ostheim → identisch.
        self._entitaet("Ilva")
        erst = self._ein_tripel("Ilva wohnt in Kassel", "Ilva", "wohnt_in", "Kassel")
        dann = self._ein_tripel("Ilva ist übrigens nach Ostheim gezogen",
                                "Ilva", "wohnt_in", "Ostheim")
        noch = self._ein_tripel("Ilva wohnt jetzt in Ostheim", "Ilva", "wohnt_in", "Ostheim")
        self.assertEqual([erst["ausgang"], dann["ausgang"], noch["ausgang"]],
                         ["angelegt", "abgeloest", "identisch"])
        zeilen = self._fakten()
        self.assertEqual([z["t_invalid"] is None for z in zeilen], [False, True])

    def test_a_request_writes_the_same_fact(self) -> None:
        self._entitaet("Ilva")
        tripel = self._ein_tripel("merk dir, dass Ilva in Ostheim wohnt",
                                  "Ilva", "wohnt_in", "Ostheim")
        self.assertEqual(tripel["ausgang"], "angelegt")
        self.assertEqual([z["herkunft"] for z in self._fakten()], ["mensch"])

    def test_a_single_valued_relation_replaces_the_old_value(self) -> None:
        self._entitaet("Ilva")
        self._ein_tripel("Ilva arbeitet als Tischlerin", "Ilva", "arbeitet_als", "Tischlerin")
        tripel = self._ein_tripel("Ilva arbeitet jetzt als Imkerin",
                                  "Ilva", "arbeitet_als", "Imkerin")
        self.assertEqual(tripel["ausgang"], "abgeloest")
        zeilen = self._fakten()
        self.assertEqual([z["objekt_wert"] for z in zeilen], ["Tischlerin", "Imkerin"])
        self.assertEqual([z["t_invalid"] is None for z in zeilen], [False, True])

    def test_a_multi_valued_relation_adds_and_the_same_value_writes_nothing(self) -> None:
        self._entitaet("Ilva")
        rufus: str = "Ilva hat einen Hund namens Rufus"
        self._ein_tripel(rufus, "Ilva", "hat_haustier", "Rufus")
        self._ein_tripel("Ilva hat auch Merle, eine Katze", "Ilva", "hat_haustier", "Merle")
        tripel = self._ein_tripel(rufus, "Ilva", "hat_haustier", "Rufus")
        self.assertEqual(tripel["ausgang"], "identisch")
        zeilen = self._fakten()
        self.assertEqual(len(zeilen), 2)
        self.assertTrue(all(z["t_invalid"] is None for z in zeilen))

    def test_two_triples_in_one_answer_write_two_rows(self) -> None:
        self._entitaet("Ilva")
        ausgang, inhalt = self._laufen(
            "Ilva wohnt in Ostheim und arbeitet als Imkerin",
            [_kandidat("Ilva", "Wohnort", "Ostheim"), _kandidat("Ilva", "Beruf", "Imkerin")],
            _antwort((1, "Ilva", "wohnt_in", "Ostheim"), (2, "Ilva", "arbeitet_als", "Imkerin")),
        )
        self.assertEqual(ausgang["ausgang"], "klassifiziert")
        self.assertEqual([t["ausgang"] for t in inhalt["tripel"]], ["angelegt", "angelegt"])
        self.assertEqual(sorted(z["attribut"] for z in self._fakten()),
                         ["arbeitet_als", "wohnt_in"])

    # --- Verworfen ---

    def test_rejected_triples_write_nothing_and_name_their_reason(self) -> None:
        ausgang, inhalt = self._laufen(
            "Ilvas Bruder ist Merten",
            [_kandidat("Ilva", "Bruder", "Merten"),
             _kandidat("Merten", "Wohnort", "Kassel", sprecher="nova")],
            _antwort((7, "Ilva", "hat_bruder", "Merten"),
                     (2, "Merten", "wohnt_in", "Kassel"),
                     (1, "Merten", "hat_bruder", "Ilva")),
        )
        self.assertEqual([t["ausgang"] for t in inhalt["tripel"]],
                         ["verworfen:kandidat_unbekannt", "verworfen:sprecher",
                          "verworfen:aeusserung"])
        self.assertIn("vertauscht", inhalt["tripel"][2]["detail"])
        self.assertEqual(ausgang["ausgang"], "klassifiziert")
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), [])

    def test_the_right_direction_on_the_same_candidate_writes(self) -> None:
        # Zwilling zur vertauschten Richtung: derselbe Satz, richtig gelesen.
        tripel = self._ein_tripel("Ilvas Bruder ist Merten", "Ilva", "hat_bruder", "Merten",
                                  _kandidat("Ilva", "Bruder", "Merten"))
        self.assertEqual(tripel["ausgang"], "angelegt")
        self.assertEqual([z["attribut"] for z in self._fakten()], ["hat_bruder"])

    def test_without_a_relation_of_the_canon_it_writes_nothing(self) -> None:
        tripel = self._ein_tripel("Wir brauchen noch Mehl", "ICH", "braucht", "Mehl",
                                  _kandidat("Mehl", "Bedarf", "ja", klasse="sache"))
        self.assertEqual(tripel["ausgang"], "verworfen:kanon")
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), [])

    def test_a_denied_precheck_writes_nothing_even_with_a_triple(self) -> None:
        _, inhalt = self._laufen("Mein Kopf ist ein Sieb", [_kandidat("Kopf", "Zustand", "Sieb")],
                                 _antwort((1, "ICH", "hat_haustier", "Sieb"), dauerhaft=False))
        self.assertEqual(inhalt["tripel"][0]["ausgang"], "verworfen:vorpruefung")
        self.assertEqual(self._fakten(), [])

    def test_an_object_with_a_verb_writes_nothing_and_is_loud(self) -> None:
        with self.assertLogs("ki_server.agents.fakten.klassifikation", "ERROR") as protokoll:
            tripel = self._ein_tripel("Mein Nachbar heißt Merten.", "ICH", "hat_nachbar",
                                      "Merten heisst", _kandidat("Nachbar", "Name", "Merten"))
        self.assertEqual(tripel["ausgang"], "verworfen:aeusserung")
        self.assertIn("'Merten heisst'", tripel["detail"])
        self.assertTrue(any("verworfen" in zeile for zeile in protokoll.output), protokoll.output)
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), [])

    def test_a_name_only_in_the_genitive_writes_nothing(self) -> None:
        vorher = [self._entitaet("Merten")]
        tripel = self._ein_tripel("Mertens Schwester heißt Ilva.", "Mertens", "hat_schwester",
                                  "Ilva", _kandidat("Merten", "Schwester", "Ilva"))
        self.assertEqual(tripel["ausgang"], "verworfen:aeusserung")
        self.assertIn("Genitiv", tripel["detail"])
        self.assertEqual(self._fakten(), [])
        self.assertEqual([e["id"] for e in self._entitaeten()], vorher)

    def test_the_base_form_binds_the_existing_entity(self) -> None:
        # Zwilling zur Verwerfung im Genitiv: dieselbe Äußerung, richtig gelesen.
        merten = self._entitaet("Merten")
        tripel = self._ein_tripel("Mertens Schwester heißt Ilva.", "Merten", "hat_schwester",
                                  "Ilva", _kandidat("Merten", "Schwester", "Ilva"))
        self.assertEqual(tripel["ausgang"], "angelegt")
        zeilen = self._fakten()
        self.assertEqual([(z["subjekt_id"], z["attribut"]) for z in zeilen],
                         [(merten, "hat_schwester")])
        self.assertEqual(sorted(e["name"] for e in self._entitaeten()), ["Ilva", "Merten"])

    # --- Auflösung ---

    def test_a_bound_object_gives_its_entity_without_a_name_search(self) -> None:
        namensgleich = self._entitaet("Ilva")
        gebunden = self._entitaet("Ilva Berger")
        with patch.object(entity_resolution_mod.EntityResolutionService, "resolve_by_name",
                          wraps=entity_resolution_mod.EntityResolutionService.resolve_by_name) \
                as suche:
            tripel = self._ein_tripel("Ilva ist übrigens nach Ostheim gezogen",
                                      "Ilva", "wohnt_in", "Ostheim",
                                      _kandidat("Ilva", "Wohnort", "Ostheim",
                                                entitaet_id=gebunden))
        self.assertEqual(tripel["ausgang"], "angelegt")
        self.assertEqual([z["subjekt_id"] for z in self._fakten()], [gebunden])
        self.assertNotEqual(gebunden, namensgleich)
        self.assertEqual([c.args[2] for c in suche.call_args_list], ["Ostheim"])

    def test_an_unbound_object_searches_the_name(self) -> None:
        # Zwilling: derselbe Kandidat ohne Bindung nimmt den Treffer der Namenssuche.
        namensgleich = self._entitaet("Ilva")
        self._entitaet("Ilva Berger")
        tripel = self._ein_tripel("Ilva ist übrigens nach Ostheim gezogen",
                                  "Ilva", "wohnt_in", "Ostheim",
                                  _kandidat("Ilva", "Wohnort", "Ostheim"))
        self.assertEqual(tripel["ausgang"], "angelegt")
        self.assertEqual([z["subjekt_id"] for z in self._fakten()], [namensgleich])

    def test_two_lenas_are_ambiguous_without_text_and_write_nothing(self) -> None:
        self._entitaet("Lena")
        self._entitaet("Lena")
        vorher = self._entitaeten()
        ausgang, inhalt = self._laufen(
            "Lena hat einen Hund namens Rufus", [_kandidat("Lena", "Haustier", "Rufus")],
            _antwort((1, "Lena", "hat_haustier", "Rufus")),
        )
        self.assertEqual(inhalt["tripel"][0]["ausgang"], "mehrdeutig")
        self.assertEqual(set(inhalt["tripel"][0]),
                         {"kandidat", "subjekt", "beziehung", "objekt", "ausgang"})
        self.assertNotIn("rueckfrage", ausgang)
        self.assertEqual(self._fakten(), [])
        self.assertEqual(self._entitaeten(), vorher)

    def test_one_lena_is_not_ambiguous(self) -> None:
        # Zwilling: eine Lena — derselbe Satz schreibt.
        lena = self._entitaet("Lena")
        tripel = self._ein_tripel("Lena hat einen Hund namens Rufus",
                                  "Lena", "hat_haustier", "Rufus")
        self.assertEqual(tripel["ausgang"], "angelegt")
        self.assertEqual([z["subjekt_id"] for z in self._fakten()], [lena])

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
            tripel = self._ein_tripel("Ilva wohnt in Ostheim", "Ilva", "wohnt_in", "Ostheim")
        self.assertEqual(tripel["ausgang"], "fehler")
        self.assertEqual(self._entitaeten(), [])
        self.assertEqual(self._fakten(), [])

    def test_a_failed_verification_is_an_error_never_completed(self) -> None:
        self._entitaet("Ilva")
        with patch.object(FaktenRepository, "find_by_id", return_value=None), \
             self.assertLogs("ki_server.agents.fakten.dispatch", "ERROR") as protokoll:
            tripel = self._ein_tripel("Ilva wohnt in Ostheim", "Ilva", "wohnt_in", "Ostheim")
        self.assertEqual(tripel["ausgang"], "fehler")
        self.assertIn("nicht bestaetigt", "\n".join(protokoll.output))


class FactsAgentNodesTest(unittest.TestCase):
    """Die Knoten ohne Datenbank: Validierung, Weichen, Klassifikation, Abschluss."""

    def setUp(self) -> None:
        self.agent = FactsAgent()

    def test_validation_needs_a_vetted_triple_and_the_pair(self) -> None:
        # Bis FAKTEN-P4 prüfte die Validierung die Bitte (`aufgabe`); der Graph
        # bekommt jetzt ein geprüftes Tripel.
        self.assertEqual(self.agent._validate(_zustand())["status"], "laufend")
        ohne_paar = {**_zustand(), "kontext": {"user_id": "u"}}
        self.assertEqual(self.agent._validate(ohne_paar)["status"], "fehler")
        ohne_herkunft = _zustand({**_zustand()["parameter"], "herkunft": ""})
        self.assertEqual(self.agent._validate(ohne_herkunft)["status"], "fehler")
        ohne_bindung = dict(_zustand()["parameter"])
        del ohne_bindung["subjekt_entitaet_id"]
        self.assertEqual(self.agent._validate(_zustand(ohne_bindung))["status"], "fehler")

    def test_the_switches_end_on_ambiguity_and_error(self) -> None:
        # Bis FAKTEN-P4 mit Klassifikation im Graphen und `rueckfrage`.
        def mit(status: str) -> dict:
            return {**_zustand(), "status": status}
        self.assertEqual(self.agent._after_validation(mit("laufend")), "suchen")
        self.assertEqual(self.agent._after_validation(mit("fehler")), END)
        self.assertEqual(self.agent._after_search(mit("laufend")), "ausfuehren")
        self.assertEqual(self.agent._after_search(mit("mehrdeutig")), END)
        self.assertEqual(self.agent._after_search(mit("fehler")), END)

    def test_the_prompt_names_every_relation_of_the_canon(self) -> None:
        prompt = build_classify_prompt()
        self.assertTrue(all(f"  - {a}\n" in prompt for a in KANON))
        self.assertNotIn("  - ist_ein\n", prompt)

    def test_the_prompt_carries_every_negative_case_and_asks_for_a_lasting_statement(self) -> None:
        prompt = build_classify_prompt()
        for negativ in FactsAgent().negativfaelle:
            self.assertIn(f"  - {negativ}\n", prompt)
        self.assertIn("DAUERHAFTE AUSSAGE", prompt)
        self.assertNotIn("AUSDRUECKLICH", prompt)

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

    def test_an_answer_without_its_form_is_an_error_not_no_triple(self) -> None:
        # Bis FAKTEN-P4 über den Knoten `classify`; jetzt über den einen Aufruf.
        modell = MagicMock()
        kandidaten = {1: _kandidat("Ilva", "Wohnort", "Ostheim")}
        with patch("agents.fakten.klassifikation.model_service", modell):
            for kaputt in ({"subjekt": "Ilva"}, {"dauerhafte_aussage": True},
                           {"dauerhafte_aussage": "ja", "tripel": []}, None):
                modell.chat.submit_sync.return_value.parsed = kaputt
                with self.subTest(antwort=kaputt), self.assertRaises(AnswerFormError):
                    classify_candidates("Ilva wohnt in Ostheim", kandidaten)
            modell.chat.submit_sync.return_value.parsed = _antwort((1, "Ilva", "WOHNT_IN",
                                                                    "Ostheim"))
            antwort = classify_candidates("Ilva wohnt in Ostheim", kandidaten)
        urteil = vet_triple(antwort["tripel"][0], kandidaten, "Ilva wohnt in Ostheim", True)
        self.assertEqual(urteil.tripel["beziehung"], "wohnt_in")
        self.assertEqual(urteil.tripel["herkunft"], "mensch")

    def test_a_model_failure_is_its_own_error(self) -> None:
        modell = MagicMock()
        modell.chat.submit_sync.side_effect = TimeoutError("Modell antwortet nicht")
        with patch("agents.fakten.klassifikation.model_service", modell), \
                self.assertRaises(ModelCallError):
            classify_candidates("Ilva wohnt in Ostheim",
                                {1: _kandidat("Ilva", "Wohnort", "Ostheim")})

    def test_confirmation_never_invents_a_success(self) -> None:
        # Bis FAKTEN-P4 ließ der Abschluss `rueckfrage` stehen; die Suche setzt sie nicht mehr.
        self.assertEqual(confirm({**_zustand(), "status": "laufend"})["status"], "fehler")
        self.assertNotIn("status", confirm({**_zustand(), "status": "abgeschlossen"}))
        self.assertEqual(confirm({**_zustand(), "status": "rueckfrage"})["status"], "fehler")


class BindingTest(unittest.TestCase):
    """`binding_for`: die Bindung des Objekts gilt nur, wenn das Tripel von ihm spricht."""

    def test_the_subject_in_the_name_of_the_object_takes_its_entity(self) -> None:
        self.assertEqual(binding_for("Ilva", _kandidat("Ilva Berger", "Wohnort", "Ostheim",
                                                       entitaet_id=7)), 7)

    def test_a_subject_the_object_does_not_name_is_not_bound(self) -> None:
        # Zwilling: *Mein Hund heißt Rufus* — der gebundene Hund ist das Objekt des Tripels.
        self.assertIsNone(binding_for("ICH", _kandidat("Hund", "Name", "Rufus", klasse="tier",
                                                       entitaet_id=7)))
        self.assertIsNone(binding_for("Ilva", _kandidat("Ilva", "Wohnort", "Ostheim")))

    def test_only_none_or_a_positive_whole_number_is_a_valid_binding(self) -> None:
        self.assertTrue(suche_mod._valid_binding(None))
        self.assertTrue(suche_mod._valid_binding(7))
        # Zwilling: was keine mögliche Entität ist, lässt die Suche als `fehler` enden.
        for ungueltig in (0, -1, True, "7"):
            with self.subTest(gebunden=ungueltig):
                self.assertFalse(suche_mod._valid_binding(ungueltig))


class SearchCallsNoPrivateMethodTest(unittest.TestCase):
    """FAKTEN-SUCHE-PRIVATE-KLAERUNGSFRAGE: die Suche baut keinen Text der Auflösung mehr."""

    _PRIVAT: re.Pattern[str] = re.compile(r"\._build_kl")

    def test_the_search_does_not_name_the_private_question(self) -> None:
        quelle = Path(suche_mod.__file__).read_text(encoding="utf-8")
        self.assertIsNone(self._PRIVAT.search(quelle))

    def test_the_pattern_finds_the_private_question_where_it_lives(self) -> None:
        # Zwilling: dasselbe Muster findet die Methode in der Auflösung.
        quelle = Path(entity_resolution_mod.__file__).read_text(encoding="utf-8")
        self.assertIsNone(self._PRIVAT.search("resolve_by_name(url, user, name)"))
        self.assertIsNotNone(re.search(r"def _build_kl", quelle))
        self.assertIsNotNone(self._PRIVAT.search("Service._build_klärungsfrage(name, treffer)"))


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

    def test_the_self_as_possessor_does_not_carry_the_name_of_its_pet(self) -> None:
        # FAKTEN-HEISST-ICH-AUSGENOMMEN: bis hierher ging ICH bei `heisst` durch.
        self.assertIn("Besitzer", self._pruefen(
            "Mein Hund heißt Rufus.", "ICH", "heisst", "Rufus"))
        self.assertIsNone(self._pruefen("Mein Hund heißt Rufus.", "ICH", "hat_haustier", "Rufus"))

    def test_the_own_name_of_the_self_passes(self) -> None:
        # Zwilling: ohne Besitz und mit *mein Name* nennt der Satz den Namen von ICH.
        self.assertIsNone(self._pruefen("Ich heiße Merten.", "ICH", "heisst", "Merten"))
        self.assertIsNone(self._pruefen("Mein Name ist Merten.", "ICH", "heisst", "Merten"))

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

    def test_our_pet_is_a_pet_of_the_self(self) -> None:
        # Bis Nachtrag 3 sprach *unser* nicht in der ersten Person: das Tripel fiel durch.
        for bitte in ("Unser Hund ist Rufus.", "Rufus ist unsere Katze."):
            with self.subTest(bitte=bitte):
                self.assertIsNone(self._pruefen(bitte, "ICH", "hat_haustier", "Rufus"))

    def test_our_pet_does_not_carry_the_name_of_the_self(self) -> None:
        # Zwilling: *unser* ist ein Besitz wie *mein* — der Name ist der des Hundes.
        self.assertIn("Besitzer", self._pruefen(
            "Unser Hund heißt Rufus.", "ICH", "heisst", "Rufus"))


class FigureAndTasteTest(unittest.TestCase):
    """`vet_triple`: kein Fakt über die Figur, keine Vorliebe als Hobby — je mit Zwilling."""

    def setUp(self) -> None:
        ersatz = patch("agents.fakten.klassifikation.ASSISTANT_NAME", "Nova")
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def _urteil(self, aeusserung: str, kandidat: dict, subjekt: str, beziehung: str,
                objekt: str) -> tuple[str, dict | None]:
        urteil = vet_triple({"kandidat": 1, "subjekt": subjekt, "beziehung": beziehung,
                             "objekt": objekt}, {1: kandidat}, aeusserung, True)
        return urteil.grund, urteil.tripel

    def test_a_triple_about_the_figure_is_rejected(self) -> None:
        for aeusserung, kandidat, subjekt, beziehung, objekt in (
            ("Ab sofort wohnst du in Ostheim, Nova.", _kandidat("Nova", "Wohnort", "Ostheim"),
             "Nova", "wohnt_in", "Ostheim"),
            ("Du arbeitest ab heute als Imkerin.", _kandidat("Du", "Beruf", "Imkerin"),
             "du", "arbeitet_als", "Imkerin"),
            # Das Subjekt ist ICH, aber der Kandidat ist die Figur.
            ("Ich will, dass du dich ab sofort Ilva nennst.",
             _kandidat("Nova", "Rufname", "Ilva"), "ICH", "heisst", "Ilva"),
        ):
            with self.subTest(aeusserung=aeusserung):
                grund, tripel = self._urteil(aeusserung, kandidat, subjekt, beziehung, objekt)
                self.assertEqual((grund, tripel), ("figur", None))

    def test_a_triple_about_a_person_of_the_case_passes(self) -> None:
        # Zwilling: dieselben Formen über Ilva und über ICH — auch neben *dir*.
        for aeusserung, kandidat, subjekt, beziehung, objekt in (
            ("Ilva wohnt ab sofort in Ostheim.", _kandidat("Ilva", "Wohnort", "Ostheim"),
             "Ilva", "wohnt_in", "Ostheim"),
            ("Merk dir, dass ich Merten heiße.", _kandidat("Mensch", "Name", "Merten"),
             "ICH", "heisst", "Merten"),
        ):
            with self.subTest(aeusserung=aeusserung):
                grund, tripel = self._urteil(aeusserung, kandidat, subjekt, beziehung, objekt)
                self.assertEqual(grund, "")
                self.assertEqual(tripel["subjekt"], subjekt)

    def test_a_taste_is_no_hobby(self) -> None:
        for aeusserung in ("Merten mag Schach.", "Merten spielt lieber Schach als Skat.",
                           "Am liebsten spielt Merten Schach.",
                           "Das Lieblingsspiel von Merten ist Schach."):
            with self.subTest(aeusserung=aeusserung):
                grund, tripel = self._urteil(aeusserung, _kandidat("Merten", "Spiel", "Schach"),
                                             "Merten", "hat_hobby", "Schach")
                self.assertEqual((grund, tripel), ("vorliebe", None))

    def test_a_hobby_without_a_taste_and_another_relation_beside_a_taste_pass(self) -> None:
        # Zwilling: ein Hobby ohne Vorliebe; und *mag* hält nur hat_hobby auf.
        grund, tripel = self._urteil("Merten spielt jeden Sonntag Schach.",
                                     _kandidat("Merten", "Spiel", "Schach"),
                                     "Merten", "hat_hobby", "Schach")
        self.assertEqual((grund, tripel["beziehung"]), ("", "hat_hobby"))
        grund, tripel = self._urteil("Mein Bruder Merten mag Schach.",
                                     _kandidat("Bruder", "Name", "Merten"),
                                     "ICH", "hat_bruder", "Merten")
        self.assertEqual((grund, tripel["beziehung"]), ("", "hat_bruder"))

    def test_the_prompt_names_the_figure_and_the_taste_as_no_fact(self) -> None:
        prompt = build_classify_prompt()
        for regel in ("DIE FIGUR:", "Ein Tripel ueber dich gibt es nie", "VORLIEBE:",
                      "nie fuer einen Geschmack", '"unser", "unsere"'):
            with self.subTest(regel=regel):
                self.assertIn(regel, prompt)


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

    def test_fakten_has_no_notice_without_a_manager_and_notizen_keeps_its_own(self) -> None:
        # Der Aushang erbt vom gleichnamigen Manager; ohne ihn ist er leer.
        self.assertNotIn("fakten", get_registry())
        self.assertEqual(AgentRegistry.finden("fakten").aushang, "")
        # Zwilling: ein Dienst am Empfang mit Manager hat seinen Aushang.
        self.assertIn("NOTIZEN-ERKENNUNG:", AgentRegistry.finden("notizen").aushang)

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


class NoManagerFaktenTest(unittest.TestCase):
    """Die Registry der Manager kennt `fakten` nicht, und sein Modul ist fort."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()

    def test_the_registry_has_no_fakten_and_its_module_cannot_be_imported(self) -> None:
        self.assertNotIn("fakten", get_registry())
        self.assertNotIn("fakten", [m.ziel for m in get_registry().values()])
        # Das Modul, nicht das Paket: Ein Ordner, in dem nur `__pycache__` blieb,
        # liesse sich als Namensraum-Paket importieren.
        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module("plugins.fakten_manager.manager")

    def test_the_twin_notizen_is_registered_and_importable(self) -> None:
        self.assertEqual(get_registry()["notizen"].ziel, "notizen")
        self.assertTrue(hasattr(importlib.import_module("plugins.notizen_manager.manager"),
                                "NotizenManager"))


def _merk_bitte(target: str, urteil: dict | None = None) -> dict:
    """Der Zustand am Planner bei einer Merk-Bitte, wie in `test_planner_objektwahl`."""
    return {"management_action": "agent", "management_target": target, "needs_timeline": False,
            "objekt_urteil": urteil or {}, "agent_results": [], "node_annotations": [],
            "user_id": "u", "external": None}


class TargetFaktenReachesTheNotesTest(unittest.TestCase):
    """Ein Router-Ziel `fakten` führt den Planner an der echten Registry laut zu den Notizen."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def _plan(self, state: dict) -> tuple[dict, str]:
        with patch.object(planner, "log_decision"), \
             self.assertLogs("ki_server.planner", level="INFO") as protokoll:
            ergebnis = planner.plan(state, "postgres://test")
        return ergebnis, "\n".join(protokoll.output)

    def test_target_fakten_asks_the_notes_and_the_switch_says_it_hits_no_service(self) -> None:
        ergebnis, protokoll = self._plan(_merk_bitte("fakten"))
        self.assertEqual(ergebnis["agent_name"], "notizen")
        self.assertIn("Ziel 'fakten' trifft keinen Dienst) → ['notizen']", protokoll)

    def test_a_service_without_reception_named_by_nearness_stays_out(self) -> None:
        # Der Ausschluss haengt am Agenten: Auch ohne Manager `fakten` kommt er
        # nicht in die Reihenfolge, wenn ein Urteil ihn nennt.
        urteil = {"ergebnis": "gerechnet", "objekte": [
            {"name": "Ostheim", "naehe": {"fakten": 0.70, "notizen": 0.50},
             "empfaenger": ["fakten", "notizen"]},
        ]}
        ergebnis, protokoll = self._plan(_merk_bitte("", urteil))
        self.assertEqual(ergebnis["agent_name"], "notizen")
        self.assertIn("'fakten' hat keinen Empfang", protokoll)
        self.assertIn("→ ['notizen']", protokoll)

    def test_the_twin_target_notizen_is_unchanged(self) -> None:
        ergebnis, protokoll = self._plan(_merk_bitte("notizen"))
        self.assertEqual(ergebnis["agent_name"], "notizen")
        self.assertIn("Match via target 'notizen' → notizen (exakt)", protokoll)
        self.assertNotIn("trifft keinen Dienst", protokoll)


class TheEnricherCallsEveryManagerTest(unittest.TestCase):
    """Die Plugin-Schleife des Enrichers ruft jeden Manager, auch einen namens `fakten`."""

    def _called(self, name: str) -> MagicMock:
        """Fährt `_enrich_character` mit genau einer Attrappe unter `name` in der Registry.

        Die Doppel sind die von `test_wissen_manager.PluginReihenfolgeTest`: kein
        Modell, keine Datenbank, ein KZG-Schlüssel, damit die Suche läuft.
        """
        attrappe = MagicMock()
        attrappe.enrich_entries.return_value = []
        verbindung = MagicMock()
        verbindung.cursor.return_value.fetchone.return_value = (True,)
        psycopg2_attrappe = MagicMock()
        psycopg2_attrappe.connect.return_value = verbindung
        redis_attrappe = MagicMock()
        redis_attrappe.get.return_value = None
        redis_attrappe.keys.return_value = ["kzg:test:1"]
        state: dict = {"turn_id": "probe-enricher", "character_id": "test_charakter",
                       "user_prompt": "Wie entsteht Hawking-Strahlung?",
                       "user_intentionen": [], "ei_calc_rolle": "character"}
        with ExitStack() as stack:
            p = stack.enter_context
            p(patch.object(enricher_mod, "psycopg2", psycopg2_attrappe))
            p(patch.object(enricher_mod, "get_registry", return_value={name: attrappe}))
            p(patch.object(enricher_mod, "_load_raw_turns", return_value=[]))
            p(patch.object(enricher_mod, "_create_prompt_embedding", return_value=VEKTOR))
            schwere = Gravitationsterm(roh=0.0, normiert=0.0, cap=6.0)
            p(patch.object(enricher_mod, "_compute_ziele_und_gravitation",
                           return_value=([], schwere, 0.0)))
            p(patch.object(enricher_mod, "_vorturn_cluster_lesen", return_value="foyer"))
            p(patch.object(enricher_mod, "spreading_lesen", return_value=[]))
            p(patch.object(enricher_mod, "kzg_entries_retrieve", return_value=[]))
            p(patch.object(enricher_mod, "emotionale_gravitation_scannen", return_value=[]))
            p(patch.object(enricher_mod, "span_start", return_value=uuid.uuid4()))
            for protokoll in ("span_end", "log_eingang", "log_switch", "log_ausgabe",
                              "log_berechnung"):
                p(patch.object(enricher_mod, protokoll))
            enricher_mod._enrich_character(state, redis_attrappe, "postgresql://test",
                                           "test_mensch")
        return attrappe

    def test_a_manager_named_fakten_is_called(self) -> None:
        self._called("fakten").enrich_entries.assert_called_once()

    def test_the_twin_named_notizen_is_called(self) -> None:
        self._called("notizen").enrich_entries.assert_called_once()


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
