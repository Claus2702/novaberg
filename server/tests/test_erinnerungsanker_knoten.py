"""Zeugen fuer den Knoten des Erinnerungsankers.

Der Knoten liest je gebundener Entitaet die Mappe und sucht immer im
Langzeitgedaechtnis des Paares; die Fakten stehen danach als Gruppe `fakten`
vor den Erinnerungen, die neuen Erinnerungen hinter der Resonanz — entdoppelt
nach dem Knoten, gekappt, angehaengt. Ohne gebundene Entitaet oder ohne etwas
Neues bleiben die vier Werte zeichengleich.

Die Doppel sind die Mappe (`load_mappe`) und das Protokoll (`span_start`,
`span_end`, `log_berechnung`); die Suche liest die Testdatenbank (`config`)
mit einem eigenen Paar, das vorher und nachher abgeraeumt wird — ein ersetzter
Cursor saehe weder die Grenze noch die Ordnung der Abfrage.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import logging
import unittest
from dataclasses import replace
from unittest.mock import MagicMock, patch

import psycopg2

from config import POSTGRES_URL
from graph.format import format_memory_entries
from graph.format.memory_context import LESER_ANALYSE, LESER_VERFASSER
from graph.nodes.erinnerungsanker import (
    _extend_resonanz,
    _is_channel_element,
    _nova_emotion,
    erinnerungsanker,
    facts_entry,
)
from memory.fakten_mappe import Mappe, MappeEntry
from memory.repositories.fakten_repository import EntityNotFoundError

_ANKER_LOGGER: str = "ki_server.erinnerungsanker"
_FORMAT_LOGGER: str = "graph.format.memory_context"
_MODUL: str = "graph.nodes.erinnerungsanker"

# Ein eigenes Paar und Kennungen, die kein Bestand traegt: Ein Treffer kann
# nur eine Zeile dieser Fixture sein.
_USER: str = "test_c5b_mensch"
_CHAR: str = "test_c5b_nova"
_LENA: int = 970_141
_OPA: int = 970_152
_ANDERE: int = 970_163

# Ein Eintrag des Kurzzeitgedaechtnisses, damit die Ordnung der Gruppen
# sichtbar ist: `fakten` steht vor `kzg`.
_KZG: dict = {
    "quelle": "kzg", "subtyp": "", "inhalt": "Wir haben ueber den Urlaub gesprochen",
    "gewicht": 0.8, "meta": {"themen": ["Urlaub"], "beobachter": "user"},
}


def _mappe(kennung: int, name: str, *texte: str) -> Mappe:
    """Eine Mappe der Entitaet mit je einem Wert-Fakt je Text."""
    eintraege: tuple[MappeEntry, ...] = tuple(
        MappeEntry(
            fact_id=nummer, degree=1, subject_id=kennung, subject_name=name,
            relation="hat", object_id=None, object_name=None, object_value=text,
            text=text, origin="test", strength=0.5,
        )
        for nummer, text in enumerate(texte, start=1)
    )
    return Mappe(
        entity_id=kennung, entity_name=name, depth=1, entries=eintraege,
        truncated=False, omitted=0, chars=sum(len(t) for t in texte),
    )


def _erinnerung(knoten_id: int, inhalt: str, rang: int) -> dict:
    """Eine Erinnerung der Resonanz, wie der Enricher sie traegt (Direkttreffer)."""
    return {
        "rang": rang, "knoten_id": knoten_id, "inhalt": inhalt, "emotion": "",
        "beobachter": "user", "schale": 0, "sortier_gewicht": 0.5, "pfad": [],
    }


def _state(kanal: list[dict] | None, resonanz: dict | None = None, **felder: object) -> dict:
    """Ein Zustand hinter Reducer und Sachlage; beide Kontexte aus demselben Formatter."""
    eintraege: list[dict] = [dict(_KZG)]
    state: dict = {
        "user_id": _USER, "character_id": _CHAR, "turn_id": "t",
        "memory_entries": eintraege,
        "memory_context": format_memory_entries(eintraege, resonanz, LESER_ANALYSE),
        "memory_context_verfasser": format_memory_entries(eintraege, resonanz, LESER_VERFASSER),
        "lzg_resonanz": resonanz, "objekt_entitaeten": kanal, "nova_emotions_verlauf": [],
    }
    state.update(felder)
    return state


def _mappen_doppel(mappen: dict[int, Mappe | Exception]) -> object:
    """Ein Doppel fuer `load_mappe`: die Mappe der Kennung, oder es wirft."""
    def fake(_url: str, _user: str, _char: str, kennung: int) -> Mappe:
        wert: Mappe | Exception = mappen[kennung]
        if isinstance(wert, Exception):
            raise wert
        return wert
    return fake


def _run(state: dict, mappen: dict[int, Mappe | Exception]) -> tuple[dict, MagicMock]:
    """Faehrt den Knoten; das Ergebnis und das Doppel von `log_berechnung`."""
    with patch(f"{_MODUL}.load_mappe", side_effect=_mappen_doppel(mappen)), \
         patch(f"{_MODUL}.span_start", return_value="span"), \
         patch(f"{_MODUL}.span_end"), \
         patch(f"{_MODUL}.log_berechnung") as log:
        result: dict = erinnerungsanker(state, POSTGRES_URL)
    return result, log


def _protokoll(log: MagicMock) -> dict:
    """Der Inhalt des einen Protokolleintrags."""
    return log.call_args.kwargs["inhalt"]


class _NodeFixture(unittest.TestCase):
    """Legt Knoten des Paares in der Testdatenbank an und raeumt sie ab."""

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

    def _node(self, inhalt: str, entitaet_ids: list[int], gewicht: float = 0.5) -> int:
        """Ein aktiver Knoten des Paares; seine id."""
        self._serial += 1
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO lzg_knoten
                    (user_id, character_id, beobachter, inhalt, dimension,
                     gewicht_roh, gewicht_absolut, gewicht_decay,
                     kzg_quell_key, kzg_erstellt_am, entitaet_ids, aktiv)
                VALUES (%s, %s, 'user', %s, 'fakt', %s, %s, %s, %s, NOW(), %s, TRUE)
                RETURNING id
                """,
                (_USER, _CHAR, inhalt, gewicht, gewicht, gewicht,
                 f"test-c5b-{self._serial}", entitaet_ids),
            )
            return int(cur.fetchone()[0])


class SearchedEvenWithoutFactsTest(_NodeFixture):
    """Zeuge 1: Gesucht wird immer, auch ohne Fakten."""

    def test_entity_without_facts_brings_three_memories(self) -> None:
        ids: list[int] = [
            self._node(f"Lena erzaehlt vom Turnier {n}", [_LENA], gewicht=0.9 - n / 10)
            for n in range(3)
        ]
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}])
        with self.assertNoLogs(_FORMAT_LOGGER, level="WARNING"):
            result, log = _run(state, {_LENA: _mappe(_LENA, "Lena")})
        self.assertEqual(_protokoll(log)["knoten_neu_ids"], ids)
        self.assertEqual(_protokoll(log)["zweig"], "ergaenzt")
        self.assertEqual([e["knoten_id"] for e in result["lzg_resonanz"]["erinnerungen"]], ids)
        for kontext in (result["memory_context"], result["memory_context_verfasser"]):
            self.assertNotIn("[Fakten zu", kontext)
            for n in range(3):
                self.assertIn(f'"Lena erzaehlt vom Turnier {n}"', kontext)

    def test_twin_without_bound_entity_everything_stays_and_nothing_is_read(self) -> None:
        self._node("Lena erzaehlt vom Turnier", [_LENA])
        state: dict = _state([])
        with patch("memory.lzg_knoten.psycopg2.connect") as connect:
            result, log = _run(state, {})
        connect.assert_not_called()
        for feld in ("memory_entries", "memory_context", "memory_context_verfasser",
                     "lzg_resonanz"):
            self.assertEqual(result[feld], state[feld])
        self.assertEqual(_protokoll(log)["grund"], "keine gebundene Entitaet")


class FactsBeforeMemoriesTest(_NodeFixture):
    """Zeuge 2: Ohne Fakten und Knoten zeichengleich; ein Fakt steht vor kzg/lzg."""

    def test_bound_entity_without_facts_and_nodes_stays_unchanged(self) -> None:
        self._node("Opa repariert das Dach", [_OPA])
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}])
        result, log = _run(state, {_LENA: _mappe(_LENA, "Lena")})
        self.assertEqual(result["memory_context"], state["memory_context"])
        self.assertEqual(result["memory_context_verfasser"], state["memory_context_verfasser"])
        self.assertEqual(result["memory_entries"], state["memory_entries"])
        self.assertIsNone(result["lzg_resonanz"])
        self.assertEqual(_protokoll(log)["neu"], 0)
        self.assertEqual(_protokoll(log)["gefunden"], 0)
        self.assertEqual(_protokoll(log)["zweig"], "nichts_neu")

    def test_twin_one_fact_stands_as_group_before_kzg(self) -> None:
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}])
        with self.assertNoLogs(_FORMAT_LOGGER, level="WARNING"):
            result, log = _run(state, {_LENA: _mappe(_LENA, "Lena", "Lena wohnt in Kiel")})
        for kontext in (result["memory_context"], result["memory_context_verfasser"]):
            self.assertIn("[Fakten zu Lena]\n- Lena wohnt in Kiel", kontext)
            self.assertLess(kontext.index("[Fakten zu Lena]"), kontext.index("[KZG]"))
        self.assertEqual(_protokoll(log)["fakten_eintraege"], 1)


class CappedAndDeduplicatedTest(_NodeFixture):
    """Zeuge 3: hoechstens drei neue, die staerksten, keiner der Resonanz doppelt."""

    def test_five_nodes_give_exactly_the_three_strongest(self) -> None:
        # Zwei fremde Erinnerungen in der Resonanz heben die Grenze der Suche
        # auf 5: Erst dann liefert die Abfrage mehr als drei, und die Kappung
        # im Knoten ist die einzige, die greift.
        fremd: int = self._node("Wir waren am Meer", [_ANDERE])
        fremd2: int = self._node("Der Zug war voll", [_ANDERE])
        resonanz: dict = {
            "anker_anzahl": 1, "sprung_tiefe": 1, "cluster": None, "nova_sektor": "",
            "erinnerungen": [_erinnerung(fremd, "Wir waren am Meer", 1),
                             _erinnerung(fremd2, "Der Zug war voll", 2)],
        }
        ids: list[int] = [
            self._node(f"Lena Knoten {n}", [_LENA], gewicht=0.9 - n / 10) for n in range(5)
        ]
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}], resonanz)
        result, log = _run(state, {_LENA: _mappe(_LENA, "Lena")})
        self.assertEqual(_protokoll(log)["gefunden"], 5)
        self.assertEqual(_protokoll(log)["knoten_neu_ids"], ids[:3])
        erinnerungen: list[dict] = result["lzg_resonanz"]["erinnerungen"]
        self.assertEqual([e["knoten_id"] for e in erinnerungen], [fremd, fremd2, *ids[:3]])
        self.assertEqual([e["rang"] for e in erinnerungen], [1, 2, 3, 4, 5])

    def test_the_strongest_in_the_resonance_do_not_take_the_places(self) -> None:
        ids: list[int] = [
            self._node(f"Lena Knoten {n}", [_LENA], gewicht=0.9 - n / 10) for n in range(6)
        ]
        resonanz: dict = {
            "anker_anzahl": 3, "sprung_tiefe": 1, "cluster": None, "nova_sektor": "",
            "erinnerungen": [_erinnerung(k, f"Lena Knoten {n}", n + 1)
                             for n, k in enumerate(ids[:3])],
        }
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}], resonanz)
        result, log = _run(state, {_LENA: _mappe(_LENA, "Lena")})
        self.assertEqual(_protokoll(log)["knoten_neu_ids"], ids[3:])
        self.assertEqual([e["knoten_id"] for e in result["lzg_resonanz"]["erinnerungen"]], ids)

    def test_twin_a_node_of_the_resonance_stands_once(self) -> None:
        alt: int = self._node("Lena hat Geburtstag", [_LENA], gewicht=0.9)
        neu: int = self._node("Lena backt einen Kuchen", [_LENA], gewicht=0.4)
        resonanz: dict = {
            "anker_anzahl": 1, "sprung_tiefe": 1, "cluster": None, "nova_sektor": "",
            "erinnerungen": [_erinnerung(alt, "Lena hat Geburtstag", 1)],
        }
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}], resonanz)
        result, log = _run(state, {_LENA: _mappe(_LENA, "Lena")})
        self.assertEqual(_protokoll(log)["knoten_neu_ids"], [neu])
        for kontext in (result["memory_context"], result["memory_context_verfasser"]):
            self.assertEqual(kontext.count('"Lena hat Geburtstag"'), 1)
            self.assertIn('"Lena backt einen Kuchen"', kontext)
            self.assertIn("eine gemeinsame Person/Sache", kontext)
        self.assertEqual(result["lzg_resonanz"]["erinnerungen"][1]["rang"], 2)


class UnknownAgainstFailedTest(_NodeFixture):
    """Zeuge 5: Ausfall wird gezaehlt und gesucht, unbekannt faellt aus der Suche."""

    def test_failed_mappe_is_counted_and_the_search_runs(self) -> None:
        knoten: int = self._node("Lena faehrt Rad", [_LENA])
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}])
        with self.assertLogs(_ANKER_LOGGER, level="ERROR"):
            _result, log = _run(state, {_LENA: RuntimeError("Mappe weg")})
        self.assertEqual(_protokoll(log)["ausfall"], 1)
        self.assertEqual(_protokoll(log)["unbekannt"], 0)
        self.assertEqual(_protokoll(log)["knoten_neu_ids"], [knoten])

    def test_twin_unknown_entity_is_counted_and_not_searched(self) -> None:
        self._node("Lena faehrt Rad", [_LENA])
        opa: int = self._node("Opa repariert das Dach", [_OPA])
        state: dict = _state([
            {"name": "Lena", "entitaet_id": _LENA}, {"name": "Opa", "entitaet_id": _OPA},
        ])
        with self.assertLogs(_ANKER_LOGGER, level="ERROR"):
            result, log = _run(state, {
                _LENA: EntityNotFoundError(_LENA), _OPA: _mappe(_OPA, "Opa"),
            })
        self.assertEqual(_protokoll(log)["unbekannt"], 1)
        self.assertEqual(_protokoll(log)["ausfall"], 0)
        self.assertEqual(_protokoll(log)["knoten_neu_ids"], [opa])
        self.assertNotIn('"Lena faehrt Rad"', result["memory_context"])

    def test_twin_only_unknown_entities_search_nothing(self) -> None:
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}])
        with patch(f"{_MODUL}.knoten_zu_entitaeten") as suche, \
             self.assertLogs(_ANKER_LOGGER, level="ERROR"):
            _result, log = _run(state, {_LENA: EntityNotFoundError(_LENA)})
        suche.assert_not_called()
        self.assertFalse(_protokoll(log)["gesucht"])
        self.assertIsNone(_protokoll(log)["gefunden"])

    def test_twin_a_failed_search_is_none_not_zero(self) -> None:
        state: dict = _state([{"name": "Lena", "entitaet_id": _LENA}])
        with patch("memory.lzg_knoten.psycopg2.connect",
                   side_effect=psycopg2.OperationalError("Verbindung weg")), \
             self.assertLogs(_ANKER_LOGGER, level="ERROR"):
            result, log = _run(state, {_LENA: _mappe(_LENA, "Lena")})
        self.assertEqual(_protokoll(log)["ausfall"], 1)
        self.assertTrue(_protokoll(log)["gesucht"])
        self.assertIsNone(_protokoll(log)["gefunden"])
        self.assertEqual(result["memory_context"], state["memory_context"])


class OneProtocolEntryOnEveryPathTest(_NodeFixture):
    """Genau ein `log_berechnung` je Turn, auf jedem Weg, auch beim Uebersprung."""

    def test_skip_with_empty_channel(self) -> None:
        _result, log = _run(_state([]), {})
        self.assertEqual(log.call_count, 1)
        self.assertEqual(_protokoll(log)["zweig"], "uebersprungen")

    def test_skip_with_unreadable_channel_is_loud(self) -> None:
        with self.assertLogs(_ANKER_LOGGER, level="ERROR"):
            result, log = _run(_state(None), {})
        self.assertEqual(log.call_count, 1)
        self.assertEqual(_protokoll(log)["grund"], "Kanal nicht lesbar")
        self.assertEqual(result["memory_context"], _state(None)["memory_context"])

    def test_nothing_new(self) -> None:
        _result, log = _run(
            _state([{"name": "Lena", "entitaet_id": _LENA}]), {_LENA: _mappe(_LENA, "Lena")},
        )
        self.assertEqual(log.call_count, 1)
        self.assertEqual(_protokoll(log)["zweig"], "nichts_neu")

    def test_twin_completed(self) -> None:
        self._node("Lena faehrt Rad", [_LENA])
        _result, log = _run(
            _state([{"name": "Lena", "entitaet_id": _LENA}]), {_LENA: _mappe(_LENA, "Lena")},
        )
        self.assertEqual(log.call_count, 1)
        self.assertEqual(_protokoll(log)["zweig"], "ergaenzt")
        self.assertGreater(_protokoll(log)["laenge_nachher"], _protokoll(log)["laenge_vorher"])


class TheFormOfTheChannelTest(unittest.TestCase):
    """Ein Element des Kanals traegt einen Namen und eine ganzzahlige Kennung ab 1."""

    def test_an_element_without_name_or_integer_id_is_rejected(self) -> None:
        for element in (
            {"name": "", "entitaet_id": _LENA}, {"name": "Lena", "entitaet_id": True},
            {"name": "Lena", "entitaet_id": "970141"}, {"name": "Lena", "entitaet_id": 0},
            {"entitaet_id": _LENA}, ("Lena", _LENA),
        ):
            with self.subTest(element=element):
                self.assertFalse(_is_channel_element(element))

    def test_twin_a_complete_element_is_accepted(self) -> None:
        self.assertTrue(_is_channel_element({"name": "Lena", "entitaet_id": _LENA}))

    def test_the_node_throws_on_a_defect_element_before_reading(self) -> None:
        state: dict = _state([{"name": "Lena", "entitaet_id": None}])
        with patch(f"{_MODUL}.load_mappe") as mappe, \
             patch(f"{_MODUL}.span_start", return_value="span"), \
             patch(f"{_MODUL}.span_end"), patch(f"{_MODUL}.log_berechnung"), \
             self.assertRaises(ValueError):
            erinnerungsanker(state, POSTGRES_URL)
        mappe.assert_not_called()


def _mappe_mit_staerke(staerke: float) -> Mappe:
    """Eine Mappe Lenas mit einem Fakt der Staerke `staerke`."""
    mappe: Mappe = _mappe(_LENA, "Lena", "Lena wohnt in Kiel")
    return replace(mappe, entries=(replace(mappe.entries[0], strength=staerke),))


class TheChecksOfTheResultTest(unittest.TestCase):
    """Die Pruefungen des Knotens, die an fremden Werten anschlagen — je mit Zwilling."""

    def test_a_fact_strength_outside_zero_to_one_is_rejected(self) -> None:
        for staerke in (1.5, -0.1, float("nan")):
            with self.subTest(staerke=staerke), self.assertRaises(ValueError):
                facts_entry(_mappe_mit_staerke(staerke), _LENA)

    def test_twin_the_edges_of_the_span_are_accepted(self) -> None:
        for staerke in (0.0, 1.0):
            with self.subTest(staerke=staerke):
                eintrag: dict = facts_entry(_mappe_mit_staerke(staerke), _LENA)
                self.assertEqual(eintrag["gewicht"], staerke)

    def test_a_leading_emotion_that_is_not_text_is_rejected(self) -> None:
        for verlauf in ([{"emotion": None, "gewicht": 0.5}], [{"gewicht": 0.5}]):
            with self.subTest(verlauf=verlauf), self.assertRaises(TypeError):
                _nova_emotion({"nova_emotions_verlauf": verlauf})

    def test_twin_the_leading_emotion_is_read(self) -> None:
        verlauf: list[dict] = [
            {"emotion": "freude", "gewicht": 0.7}, {"emotion": "trauer", "gewicht": 0.2},
        ]
        self.assertEqual(_nova_emotion({"nova_emotions_verlauf": verlauf}), "freude")
        self.assertEqual(_nova_emotion({"nova_emotions_verlauf": []}), "")

    def test_memories_other_than_those_of_the_resonance_are_rejected(self) -> None:
        resonanz: dict = {
            "anker_anzahl": 1, "sprung_tiefe": 1, "cluster": None, "nova_sektor": "",
            "erinnerungen": [_erinnerung(1, "Wir waren am See", 1)],
        }
        with self.assertRaises(ValueError):
            _extend_resonanz(resonanz, [], [_erinnerung(2, "Lena lachte", 2)], "")

    def test_twin_the_new_ones_stand_behind_the_resonance(self) -> None:
        alt: list[dict] = [_erinnerung(1, "Wir waren am See", 1)]
        resonanz: dict = {
            "anker_anzahl": 1, "sprung_tiefe": 1, "cluster": None, "nova_sektor": "",
            "erinnerungen": alt,
        }
        ergaenzt: dict = _extend_resonanz(resonanz, alt, [_erinnerung(2, "Lena lachte", 2)], "")
        self.assertEqual([e["knoten_id"] for e in ergaenzt["erinnerungen"]], [1, 2])
        self.assertEqual(resonanz["erinnerungen"], alt)
        ohne: dict = _extend_resonanz(None, [], [_erinnerung(2, "Lena lachte", 1)], "freude")
        self.assertEqual(ohne["anker_anzahl"], 0)
        self.assertEqual(ohne["nova_sektor"], "freude")


class TheWrapperTest(unittest.TestCase):
    """Der Wrapper im Graphen reicht den Zustand und die Datenbank-URL des Graphen an den Knoten."""

    def _graph(self, url: str) -> object:
        from graph.character_graph import CharacterGraph

        graph = object.__new__(CharacterGraph)
        graph.postgres_url = url
        return graph

    def test_the_wrapper_passes_the_state_and_the_url_of_the_graph(self) -> None:
        state: dict = _state([])
        with patch(f"{_MODUL}.erinnerungsanker", return_value={"memory_entries": []}) as knoten:
            result: dict = self._graph("postgresql://wrapper")._node_erinnerungsanker(state)
        knoten.assert_called_once_with(state, "postgresql://wrapper")
        self.assertEqual(result, {"memory_entries": []})

    def test_twin_a_graph_without_url_throws_before_the_protocol(self) -> None:
        with patch(f"{_MODUL}.span_start") as start, self.assertRaises(ValueError):
            self._graph("")._node_erinnerungsanker(_state([]))
        start.assert_not_called()


class TheEdgesTest(unittest.TestCase):
    """Zeuge 7: Der Anker steht zwischen Sachlage und Router, und der Stream kennt ihn.

    Der Graph wird ohne `__init__` gebaut: Die Verdrahtung braucht weder Redis
    noch Postgres.
    """

    def _kanten(self) -> set[tuple[str, str]]:
        from graph.character_graph import CharacterGraph

        gebaut = CharacterGraph.build(object.__new__(CharacterGraph))
        return {(e.source, e.target) for e in gebaut.get_graph().edges}

    def test_sachlage_leads_into_the_anchor_and_the_anchor_into_the_router(self) -> None:
        kanten: set[tuple[str, str]] = self._kanten()
        self.assertIn(("sachlage_node", "erinnerungsanker"), kanten)
        self.assertIn(("erinnerungsanker", "router"), kanten)

    def test_twin_no_path_from_the_sachlage_past_the_anchor(self) -> None:
        self.assertNotIn(("sachlage_node", "router"), self._kanten())

    def test_the_stream_knows_the_node(self) -> None:
        from services.event_consumer import CHARACTER_NODE_LABELS

        self.assertIn("erinnerungsanker", CHARACTER_NODE_LABELS)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
