"""Zeugen fuer den Kanal des Erinnerungsankers und die Suche nach seinen Erinnerungen.

Zwei Teile, beide ohne Leser im Turn:

  * **Der Kanal `objekt_entitaeten`** — am Ende von `sachlage_assess`, auf
    jedem ihrer drei Wege (frisch, Ausfall uebernommen, Impuls): die
    gebundenen Entitaeten der akuten Objekte, einmal je Entitaet, in der
    Ordnung der Objekte. `[]` heisst *nichts gebunden*, `None` *nicht
    lesbar*. Geprueft hinter der Knotengrenze eines echten Graphen, denn ein
    undeklarierter Schluessel faellt dort still weg.
  * **`knoten_zu_entitaeten`** — gegen die Testdatenbank (`config`), mit
    eigenen Paaren, die vorher und nachher abgeraeumt werden. Das fremde Paar
    teilt den Menschen und unterscheidet sich nur im Charakter: Nur so faellt
    eine Abfrage auf, die den Charakter vergisst.

Die Doppel sind das Modell (der Call der Sachlage ist ersetzt) und die
Bindungen (`bound_entities`); die Suche liest die echte Datenbank, weil ein
ersetzter Cursor die Abfrage nicht saehe.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import logging
import unittest
from unittest.mock import patch

import psycopg2
from langgraph.graph import END, StateGraph

from config import POSTGRES_URL
from graph.nodes.sachlage import (
    HERKUNFT_AUSFALL,
    HERKUNFT_FRISCH,
    HERKUNFT_IMPULS,
    object_entities,
    sachlage_assess,
)
from graph.state import ConversationState
from memory.lzg_knoten import knoten_zu_entitaeten
from memory.sachlage_properties import text_key

_SACHLAGE_LOGGER: str = "ki_server.sachlage"
_KNOTEN_LOGGER: str = "memory.lzg_knoten"

# Die Bindungen des Doppels: zwei Namen derselben Person, ein Grossvater und
# ein Rasen, der nur erwaehnt wird.
_BINDINGS: dict[str, int] = {
    text_key("Lena"): 41, text_key("Lenchen"): 41, text_key("Opa"): 52, text_key("Rasen"): 77,
}


def _artifact(*objects: tuple[str, bool]) -> dict:
    """Ein Artefakt mit den genannten Objekten (Name, akut)."""
    return {
        "thema": "Familie", "gegenstand": "Besuch der Familie",
        "nutzerziel": "vermutlich erzaehlen", "ausdrucksweise": "beilaeufig",
        "objekte": [
            {"name": name, "klasse": "person", "akut": akut, "gedeckt": {}, "offen": []}
            for name, akut in objects
        ],
    }


def _state(**fields: object) -> dict:
    """Ein Zustand, wie ihn der Knoten liest."""
    base: dict = {
        "user_id": "u", "character_id": "c", "turn_id": "t",
        "user_prompt": "Opa und Lena kommen am Wochenende",
        "session_turns": [], "event_payload": {}, "event_source": "user",
    }
    base.update(fields)
    return base


def _fake_bound(bindings: dict[str, int] | None) -> object:
    """Ein Doppel fuer `bound_entities`: liefert nur die erfragten Schluessel."""
    def fake(_url: str, _user: str, _char: str, keys: list[str]) -> dict[str, int] | None:
        if bindings is None:
            return None
        return {k: bindings[k] for k in keys if k in bindings}
    return fake


def _through_graph(state: dict) -> dict:
    """Faehrt `sachlage_assess` als Knoten eines echten Graphen; der Endzustand.

    Der Knoten heisst wie im echten Graphen: LangGraph weist einen Knotennamen
    ab, der zugleich ein Schluessel des Zustands ist (`sachlage`).
    """
    graph = StateGraph(ConversationState)
    graph.add_node("sachlage_node", sachlage_assess)
    graph.set_entry_point("sachlage_node")
    graph.add_edge("sachlage_node", END)
    return graph.compile().invoke(state)


def _run_path(path: str, artifact: dict, bindings: dict[str, int] | None) -> dict:
    """Ein Weg der Sachlage hinter der Knotengrenze; Modell und Bindungen als Doppel.

    `frisch`: kein Vorgaenger, der Call liefert `artifact`. `ausfall`: der Call
    faellt aus, der Vorgaenger `artifact` wird uebernommen. `impuls`: Novas
    eigener Impuls, der Vorgaenger `artifact` bleibt.
    """
    state: dict = _state()
    previous: dict | None = dict(artifact)
    derived: dict | None = None
    if path == "frisch":
        previous, derived = None, dict(artifact)
    elif path == "impuls":
        state = _state(event_payload={"reiz_herkunft": "eigener_impuls"})
    with patch("graph.nodes.sachlage.sachlage_load", return_value=(previous, False)), \
         patch("graph.nodes.sachlage._derive", return_value=derived), \
         patch("graph.nodes.sachlage.memory_offer", return_value=[]), \
         patch("graph.nodes.sachlage._resume_lookup", return_value=None), \
         patch("graph.nodes.sachlage.sachlage_bridge_build", return_value={}), \
         patch("graph.nodes.sachlage._sachlage_store"), \
         patch("graph.nodes.sachlage._persist_history", return_value=None), \
         patch("graph.nodes.sachlage.short_goal_track"), \
         patch("graph.nodes.sachlage.log_berechnung"), \
         patch("graph.nodes.sachlage.bound_entities", side_effect=_fake_bound(bindings)):
        return _through_graph(state)


class TheChannelOnEveryPathTest(unittest.TestCase):
    """Der Kanal steht auf allen drei Wegen hinter dem Knoten."""

    def test_the_channel_stands_behind_the_node_on_all_three_paths(self) -> None:
        # Opa vor Lena: Die Ordnung ist die der Objekte, nicht die der Schluessel.
        artifact: dict = _artifact(("Opa", True), ("Lena", True))
        expected: list[dict] = [
            {"name": "Opa", "entitaet_id": 52}, {"name": "Lena", "entitaet_id": 41},
        ]
        for path, herkunft in (
            ("frisch", HERKUNFT_FRISCH), ("ausfall", HERKUNFT_AUSFALL),
            ("impuls", HERKUNFT_IMPULS),
        ):
            with self.subTest(path=path):
                result: dict = _run_path(path, artifact, _BINDINGS)
                self.assertEqual(result["sachlage"]["herkunft"], herkunft)
                self.assertEqual(result["objekt_entitaeten"], expected)

    def test_twin_an_object_not_acute_is_missing(self) -> None:
        result: dict = _run_path(
            "frisch", _artifact(("Lena", True), ("Rasen", False)), _BINDINGS,
        )
        self.assertEqual(result["objekt_entitaeten"], [{"name": "Lena", "entitaet_id": 41}])

    def test_twin_two_objects_of_one_entity_stand_once(self) -> None:
        result: dict = _run_path(
            "frisch", _artifact(("Lenchen", True), ("Opa", True), ("Lena", True)), _BINDINGS,
        )
        self.assertEqual(
            result["objekt_entitaeten"],
            [{"name": "Lenchen", "entitaet_id": 41}, {"name": "Opa", "entitaet_id": 52}],
        )


class EmptyAgainstUnreadableTest(unittest.TestCase):
    """`[]` heisst *nichts gebunden*, `None` *nicht lesbar* — nie verwechselt."""

    def test_without_a_bound_object_the_channel_is_empty(self) -> None:
        result: dict = _run_path("ausfall", _artifact(("Opa", True)), {})
        self.assertEqual(result["objekt_entitaeten"], [])

    def test_unreadable_bindings_give_none_loudly(self) -> None:
        with self.assertLogs(_SACHLAGE_LOGGER, level="ERROR") as log:
            result: dict = _run_path("impuls", _artifact(("Opa", True)), None)
        self.assertIsNone(result["objekt_entitaeten"])
        self.assertTrue(any("nicht lesbar" in line for line in log.output))

    def test_without_a_pair_the_channel_is_none_and_nothing_is_read(self) -> None:
        with patch("graph.nodes.sachlage.bound_entities") as bound, \
             self.assertLogs(_SACHLAGE_LOGGER, level="ERROR"):
            self.assertIsNone(object_entities(_artifact(("Opa", True)), "", "c"))
        bound.assert_not_called()

    def test_twin_without_acute_objects_nothing_is_read(self) -> None:
        with patch("graph.nodes.sachlage.bound_entities") as bound:
            self.assertEqual(object_entities(_artifact(("Rasen", False)), "u", "c"), [])
        bound.assert_not_called()


# Eigene Paare: derselbe Mensch, zwei Charaktere — und Kennungen, die kein
# Bestand traegt, damit ein Treffer nur eine Fixture-Zeile sein kann.
_USER: str = "test_c5a_mensch"
_OWN_CHAR: str = "test_c5a_nova"
_OTHER_CHAR: str = "test_c5a_andere"
_LENA: int = 970_041
_OPA: int = 970_052
_NOBODY: int = 970_099


class _NodeFixture(unittest.TestCase):
    """Legt Knoten in der Testdatenbank an und raeumt sie ab."""

    def setUp(self) -> None:
        self.conn = psycopg2.connect(POSTGRES_URL)
        # Autocommit: eine offene Lesetransaktion haelt sonst die Migration auf.
        self.conn.autocommit = True
        self._clean()
        self.addCleanup(self.conn.close)
        self.addCleanup(self._clean)
        self._serial: int = 0

    def _clean(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM lzg_knoten WHERE user_id = %s", (_USER,))

    def _node(
        self, character_id: str, inhalt: str, entitaet_ids: list[int],
        gewicht: float = 0.5, aktiv: bool = True,
    ) -> int:
        """Ein Knoten des Paares (`_USER`, `character_id`); seine id."""
        self._serial += 1
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO lzg_knoten
                    (user_id, character_id, beobachter, inhalt, dimension,
                     gewicht_roh, gewicht_absolut, gewicht_decay,
                     kzg_quell_key, kzg_erstellt_am, entitaet_ids, aktiv)
                VALUES (%s, %s, 'user', %s, 'fakt', %s, %s, %s, %s, NOW(), %s, %s)
                RETURNING id
                """,
                (_USER, character_id, inhalt, gewicht, gewicht, gewicht,
                 f"test-c5a-{self._serial}", entitaet_ids, aktiv),
            )
            return int(cur.fetchone()[0])

    def _search(self, entitaet_ids: list[int], limit: int = 10) -> list[dict] | None:
        return knoten_zu_entitaeten(POSTGRES_URL, _USER, _OWN_CHAR, entitaet_ids, "", limit)


class OnlyThePairTest(_NodeFixture):
    """Ein Knoten eines anderen Paares mit derselben Entitaet fehlt."""

    def setUp(self) -> None:
        super().setUp()
        self.own: int = self._node(_OWN_CHAR, "Lena hat ein Fahrrad bekommen", [_LENA])
        self.foreign: int = self._node(_OTHER_CHAR, "Lena zieht nach Kiel", [_LENA])

    def test_a_node_of_another_pair_is_missing(self) -> None:
        found: list[dict] | None = self._search([_LENA])
        self.assertNotIn(self.foreign, [e["knoten_id"] for e in found])

    def test_twin_the_node_of_the_own_pair_is_there(self) -> None:
        found: list[dict] | None = self._search([_LENA])
        self.assertEqual([e["knoten_id"] for e in found], [self.own])
        self.assertEqual(found[0]["inhalt"], "Lena hat ein Fahrrad bekommen")


class TheFormOfAMemoryTest(_NodeFixture):
    """Die Form von `spreading_lesen`, erreicht in Schale 1 ueber eine Entitaet."""

    def test_shared_ids_carry_each_id_once(self) -> None:
        self._node(_OWN_CHAR, "Opa und Lena im Garten", [_LENA, _LENA, _OPA])
        found: list[dict] | None = self._search([_OPA, _LENA, _NOBODY])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["schale"], 1)
        self.assertEqual(found[0]["rang"], 1)
        self.assertEqual(found[0]["pfad"][0]["verbindungs_gruende"], ["entitaet"])
        self.assertEqual(found[0]["pfad"][0]["geteilte_entitaet_ids"], [_LENA, _OPA])

    def test_the_strongest_active_nodes_come_first_up_to_the_limit(self) -> None:
        self._node(_OWN_CHAR, "schwach", [_LENA], gewicht=0.2)
        strong: int = self._node(_OWN_CHAR, "stark", [_OPA], gewicht=0.9)
        self._node(_OWN_CHAR, "inaktiv und am staerksten", [_LENA], gewicht=1.0, aktiv=False)
        found: list[dict] | None = self._search([_LENA, _OPA], limit=1)
        self.assertEqual([e["knoten_id"] for e in found], [strong])


class EmptyAgainstFailedSearchTest(_NodeFixture):
    """Ein Datenbankfehler der Suche ist `None`, nicht `[]`."""

    def test_a_database_error_is_none_not_empty(self) -> None:
        with patch("memory.lzg_knoten.psycopg2.connect",
                   side_effect=psycopg2.OperationalError("Verbindung weg")), \
             self.assertLogs(_KNOTEN_LOGGER, level="ERROR"):
            self.assertIsNone(self._search([_LENA]))

    def test_twin_no_matching_nodes_is_an_empty_list(self) -> None:
        self._node(_OWN_CHAR, "Opa repariert das Dach", [_OPA])
        self.assertEqual(self._search([_NOBODY]), [])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
