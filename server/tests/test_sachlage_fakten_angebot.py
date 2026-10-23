"""Zeugen: Teil H — die Fakten einer gebundenen Person im Angebot der Sachlage.

**Konzept:** `docs/novaberg-memory-fakten_b.md` (*Das Angebot der Sachlage*) und
`docs/novaberg-memory-fakten_e.md` A Nr. 13: Eigenschaft und Fakt sind
getrennt. Ist ein akutes Objekt mit offener Eigenschaft an eine Entitaet
gebunden, stehen die Fakten ihrer Mappe vor der Eigenschaft im Angebot, und
eine Eigenschaft, die aus einem Fakt stammt, steht dort nicht noch einmal
(Regel (c)) — nur dann, wenn genau dieser Fakt angeboten ist. Der Kalender
hat eine eigene Grenze und verdraengt weder Fakten noch den Pool.

Zeugen dieser Datei:
  * Fakten vor der Eigenschaft, die Eigenschaft aus einem Fakt fehlt;
    Zwilling ungebunden,
  * ist ihr Fakt nicht angeboten (Mappe leer, ausgefallen, hinter der
    Grenze), bleibt die Eigenschaft; Zwilling: der Fakt ist angeboten,
  * ein voller Monat im Kalender: 5 Zeilen, Fakten und Pool bleiben;
    Zwilling 3 Termine,
  * ohne Fakten bleibt das Angebot zeichengleich,
  * eine unbekannte Entitaet ist `unbekannt`, ein anderer Fehler `ausfall`,
  * nicht lesbare Bindungen sind laut und nicht *nicht gebunden*,
  * gegen die Testdatenbank: `bound_entities` und Regel (c) in der Auswahl
    von `active_properties`.

Die Datenbank der Sachlage und das Modell sind in den oberen Zeugen Doppel;
die zwei unteren Klassen laufen gegen die Testdatenbank mit eigenem Paar.
"""

import unittest
from datetime import datetime
from unittest.mock import patch

import psycopg2

from config import POSTGRES_URL
from graph.nodes import sachlage as sachlage_mod
from graph.nodes import sachlage_resolver as resolver_mod
from graph.nodes.sachlage import _derive
from graph.nodes.sachlage_resolver import (
    SOURCE_CALENDAR,
    SOURCE_FACTS,
    SOURCE_LABELS,
    SOURCE_PROPERTIES,
    MemoryHit,
    fact_hits,
    property_hits,
    render_memory_section,
)
from memory.fakten_mappe import Mappe, MappeEntry
from memory.repositories.fakten_repository import EntityNotFoundError
from memory.sachlage_properties import (
    BINDING_TURN_MAGNET,
    active_properties,
    bind_entity,
    bound_entities,
    text_key,
)
from tests.test_sachlage_calendar_reading import (
    _CLOCK,
    BERLIN,
    NOW,
    FakeTimeline,
    _period,
    _repository,
    _row,
)
from tests.test_sachlage_properties_schema import _PairFixture

_RESOLVER_LOGGER: str = "ki_server.sachlage.resolver"
_PROPERTIES_LOGGER: str = "ki_server.memory.sachlage_properties"

LENA_ENTITY: int = 42

FACTS: tuple[MappeEntry, ...] = (
    MappeEntry(
        fact_id=7, degree=1, subject_id=LENA_ENTITY, subject_name="Lena",
        relation="wohnt_in", object_id=None, object_name=None, object_value="Freiburg",
        text="Lena wohnt in Freiburg.", origin="nutzer", strength=0.8,
    ),
    MappeEntry(
        fact_id=8, degree=1, subject_id=LENA_ENTITY, subject_name="Lena",
        relation="arbeitet_als", object_id=None, object_name=None,
        object_value="Tischlerin", text="Lena arbeitet als Tischlerin.", origin="nutzer",
        strength=0.6,
    ),
)


def _mappe(entries: tuple[MappeEntry, ...] = FACTS) -> Mappe:
    """Die Mappe der Entitaet Lena."""
    return Mappe(
        entity_id=LENA_ENTITY, entity_name="Lena", depth=1, entries=entries,
        truncated=False, omitted=0, chars=sum(len(e.text) for e in entries),
    )


#: Zwei gespeicherte Eigenschaften: »Wohnort« ist aus dem Fakt 7 gedeckt
#: worden (Regel (b)), »Beruf« aus einem frueheren Gespraech.
FROM_FACT: dict = {
    "id": 20, "objekt_id": 5, "name": "Lena", "eigenschaft": "Wohnort", "wert": "Freiburg",
    "sprecher": "nutzer", "turn_id": "alt",
    "quelle": {"quelle": "fakten", "herkunft": "fakten#7", "eintrag": "G1"},
}
FROM_TALK: dict = {
    "id": 21, "objekt_id": 5, "name": "Lena", "eigenschaft": "Beruf", "wert": "Tischlerin",
    "sprecher": "nutzer", "turn_id": "alt", "quelle": None,
}


def _store(rows: list[dict]) -> object:
    """Doppel von `active_properties`, das Regel (c) wie die Abfrage auswertet.

    Ohne diese Auswertung bliebe die Gegenprobe *ohne Filter (c)* gruen: Das
    Doppel lieferte die Zeile aus dem Fakt ohnehin.
    """
    def lesen(  # noqa: PLR0913 — dieselbe Unterschrift wie die Abfrage
        postgres_url: str, user_id: str, character_id: str, name_keys: list[str],
        limit: int, *, hidden_source: str = "", hidden_for: tuple[str, ...] = (),
        hidden_origins: tuple[str, ...] = (),
    ) -> list[dict]:
        return [
            dict(r) for r in rows
            if text_key(r["name"]) in name_keys
            and not (
                text_key(r["name"]) in hidden_for
                and (r.get("quelle") or {}).get("quelle") == hidden_source
                and (r.get("quelle") or {}).get("herkunft") in hidden_origins
            )
        ][:limit]
    return lesen


def _artifact() -> dict:
    """*Wie geht es Lena?* — Lena ist akut, ihr Wohnort offen."""
    return {
        "thema": "Lena", "gegenstand": "Wie es Lena geht", "nutzerziel": "wissen",
        "ausdrucksweise": "fragend",
        "objekte": [{"name": "Lena", "akut": True, "gedeckt": {}, "offen": ["Wohnort"]}],
    }


class _Derive:
    """Ein Lauf von `_derive` mit Paar; Modell, Bindung, Mappe und Speicher als Doppel."""

    def __init__(
        self, *, bound: dict | None, mappe: object = None, stored: list[dict] | None = None,
        bestand: list[MemoryHit] | None = None, claims: dict | None = None,
    ) -> None:
        """Faehrt den Lauf; `mappe` ist eine Mappe oder eine Ausnahme."""
        artefakt: dict = _artifact()

        class _Antwort:
            parsed = artefakt

        mappe_args: dict = (
            {"side_effect": mappe} if isinstance(mappe, Exception)
            else {"return_value": mappe if mappe is not None else _mappe()}
        )
        with patch.object(sachlage_mod.model_service.chat, "submit_sync",
                          return_value=_Antwort()), \
             patch.object(resolver_mod, "bound_entities", return_value=bound) as self.binding, \
             patch.object(resolver_mod, "load_mappe", **mappe_args) as self.load, \
             patch.object(resolver_mod, "active_properties",
                          side_effect=_store(stored if stored is not None else [])), \
             patch.object(sachlage_mod, "resolve_open_properties",
                          return_value=claims or {}) as self.resolver, \
             patch.object(sachlage_mod, "assess_plausibility", return_value={}), \
             patch.object(sachlage_mod, "research_open_property", side_effect=lambda a: a):
            self.result: dict | None = _derive(
                None, [], "Wie geht es Lena?", bestand=bestand, pair=("u", "c"),
            )

    @property
    def offer(self) -> list[MemoryHit]:
        """Das Angebot, das der Aufloeser gesehen hat."""
        return self.resolver.call_args.args[1]


POOL_HIT: MemoryHit = MemoryHit("G1", "kzg", "kognition", "Lena war im Sommer am See")


class FactsBeforePropertiesTest(unittest.TestCase):
    """Gebunden — die Fakten vor jeder Eigenschaft, die Eigenschaft aus dem Fakt fehlt."""

    def test_a_bound_object_offers_its_facts_first_and_not_the_property_from_a_fact(
        self,
    ) -> None:
        lauf = _Derive(bound={"lena": LENA_ENTITY}, stored=[FROM_FACT, FROM_TALK],
                       bestand=[POOL_HIT])

        self.assertEqual(
            [(h.key, h.source, h.origin) for h in lauf.offer],
            [("G1", SOURCE_FACTS, "fakten#7"), ("G2", SOURCE_FACTS, "fakten#8"),
             ("G3", SOURCE_PROPERTIES, "sachlage_eigenschaft#21"), ("G4", "kzg", "kognition")],
        )
        self.assertEqual(
            [(h.content, h.value, h.subject) for h in lauf.offer[:2]],
            [("Lena wohnt in Freiburg.", "Freiburg", "wohnt_in"),
             ("Lena arbeitet als Tischlerin.", "Tischlerin", "arbeitet_als")],
        )
        lauf.load.assert_called_once_with(POSTGRES_URL, "u", "c", LENA_ENTITY)
        self.assertEqual(lauf.binding.call_args.args[1:], ("u", "c", ["lena"]))

    def test_twin_unbound_reads_no_mappe_and_keeps_the_property(self) -> None:
        lauf = _Derive(bound={}, stored=[FROM_FACT, FROM_TALK], bestand=[POOL_HIT])

        self.assertEqual(
            [(h.key, h.source, h.origin) for h in lauf.offer],
            [("G1", SOURCE_PROPERTIES, "sachlage_eigenschaft#20"),
             ("G2", SOURCE_PROPERTIES, "sachlage_eigenschaft#21"), ("G3", "kzg", "kognition")],
        )
        lauf.load.assert_not_called()

    def test_a_fact_covers_the_open_property_with_its_source(self) -> None:
        """Regel (b): Die Deckung aus einem Fakt traegt `fakten` als Quelle."""
        claims: dict = {"Lena": {"Wohnort": {"eintrag": "G1", "inhalt": "Freiburg"}}}
        lauf = _Derive(bound={"lena": LENA_ENTITY}, claims=claims)

        objekt: dict = lauf.result["objekte"][0]
        self.assertEqual(objekt["gedeckt"]["Wohnort"], "Freiburg")
        self.assertEqual(
            (objekt["quellen"]["Wohnort"]["quelle"], objekt["quellen"]["Wohnort"]["herkunft"]),
            (SOURCE_FACTS, "fakten#7"),
        )

    def test_the_author_hears_the_origin_of_a_fact(self) -> None:
        self.assertEqual(SOURCE_LABELS[SOURCE_FACTS], "aus ihrem gespeicherten Wissen")


class PropertyHitsSetsRuleCTest(unittest.TestCase):
    """`property_hits` reicht Regel (c) an die Abfrage: gebundene Objekte, angebotene Fakten."""

    def _rule(
        self, bound: dict | None, offered: tuple[str, ...] = (),
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        with patch.object(resolver_mod, "active_properties", return_value=[]) as lesen:
            property_hits(_artifact(), "u", "c", bound, offered)
        self.assertEqual(lesen.call_args.kwargs["hidden_source"], SOURCE_FACTS)
        return lesen.call_args.kwargs["hidden_for"], lesen.call_args.kwargs["hidden_origins"]

    def test_a_bound_object_is_hidden_from_properties_from_a_fact(self) -> None:
        self.assertEqual(
            self._rule({"lena": LENA_ENTITY}, ("fakten#7",)), (("lena",), ("fakten#7",)),
        )

    def test_twin_unreadable_bindings_hide_nothing(self) -> None:
        """Ohne lesbare Bindung stehen keine Fakten im Angebot — die Eigenschaft bleibt."""
        self.assertEqual(self._rule(None), ((), ()))


class AFactNotOfferedKeepsItsPropertyTest(unittest.TestCase):
    """Regel (c) nach (A): verborgen nur, wenn genau der Fakt der Eigenschaft angeboten ist.

    `FROM_FACT` stammt aus dem Fakt 7. Steht der nicht im Angebot, bleibt die
    Eigenschaft — sonst stuenden weder Fakt noch Eigenschaft darin.
    """

    def _origins(self, lauf: _Derive) -> list[str]:
        return [h.origin for h in lauf.offer]

    def test_an_empty_mappe_keeps_the_property(self) -> None:
        lauf = _Derive(bound={"lena": LENA_ENTITY}, mappe=_mappe(()), stored=[FROM_FACT])

        lauf.load.assert_called_once()
        self.assertEqual(self._origins(lauf), ["sachlage_eigenschaft#20"])

    def test_a_failed_mappe_keeps_the_property(self) -> None:
        with self.assertLogs(_RESOLVER_LOGGER, level="ERROR"):
            lauf = _Derive(bound={"lena": LENA_ENTITY}, mappe=RuntimeError("Verbindung weg"),
                           stored=[FROM_FACT])

        self.assertEqual(self._origins(lauf), ["sachlage_eigenschaft#20"])

    def test_a_fact_behind_the_limit_keeps_the_property(self) -> None:
        """Fakt 8 vor Fakt 7 in der Mappe, Grenze 1: nur Fakt 8 wird angeboten."""
        with patch.object(resolver_mod, "SACHLAGE_FAKTEN_ANGEBOT_MAX", 1):
            lauf = _Derive(bound={"lena": LENA_ENTITY}, mappe=_mappe(FACTS[::-1]),
                           stored=[FROM_FACT])

        self.assertEqual(self._origins(lauf), ["fakten#8", "sachlage_eigenschaft#20"])

    def test_twin_the_offered_fact_hides_the_property(self) -> None:
        """Dieselbe Mappe, Grenze 2: Fakt 7 ist angeboten, die Eigenschaft fehlt."""
        with patch.object(resolver_mod, "SACHLAGE_FAKTEN_ANGEBOT_MAX", 2):
            lauf = _Derive(bound={"lena": LENA_ENTITY}, mappe=_mappe(FACTS[::-1]),
                           stored=[FROM_FACT])

        self.assertEqual(self._origins(lauf), ["fakten#8", "fakten#7"])


class WithoutFactsTheOfferIsUnchangedTest(unittest.TestCase):
    """Eine gebundene Entitaet ohne Fakten aendert das Angebot um kein Zeichen."""

    def test_an_empty_mappe_leaves_the_section_as_unbound(self) -> None:
        """Auch die Eigenschaft aus einem Fakt bleibt — ihr Fakt steht nicht im Angebot."""
        gebunden = _Derive(bound={"lena": LENA_ENTITY}, mappe=_mappe(()),
                           stored=[FROM_FACT, FROM_TALK], bestand=[POOL_HIT])
        ungebunden = _Derive(bound={}, stored=[FROM_FACT, FROM_TALK], bestand=[POOL_HIT])

        gebunden.load.assert_called_once()
        self.assertEqual(render_memory_section(gebunden.offer),
                         render_memory_section(ungebunden.offer))
        self.assertEqual(
            [h.origin for h in gebunden.offer],
            ["sachlage_eigenschaft#20", "sachlage_eigenschaft#21", "kognition"],
        )


class AMappeThatFailsTest(unittest.TestCase):
    """`EntityNotFoundError` ist *unbekannt*; jeder andere Fehler ein lauter Ausfall."""

    def _facts(self, mappe: object) -> tuple[list, list]:
        with patch.object(resolver_mod, "load_mappe", side_effect=mappe), \
             self.assertLogs(_RESOLVER_LOGGER, level="INFO") as logs:
            hits = fact_hits(_artifact(), "u", "c", {"lena": LENA_ENTITY})
        return hits, logs.records

    def test_an_unknown_entity_is_counted_unknown_not_a_failure(self) -> None:
        hits, records = self._facts(EntityNotFoundError("keine aktive Entitaet"))

        self.assertEqual(hits, [])
        self.assertTrue(any("unbekannt 1, ausfall 0" in r.getMessage() for r in records))
        self.assertEqual([r.getMessage() for r in records if r.levelname == "ERROR"], [])

    def test_twin_another_error_is_a_loud_failure_and_the_offer_has_no_facts(self) -> None:
        hits, records = self._facts(RuntimeError("Verbindung weg"))

        self.assertEqual(hits, [])
        self.assertTrue(any("unbekannt 0, ausfall 1" in r.getMessage() for r in records))
        self.assertEqual(len([r for r in records if r.levelname == "ERROR"]), 1)

    def test_a_failing_mappe_leaves_the_turn_running_with_the_rest_of_the_offer(self) -> None:
        lauf = _Derive(bound={"lena": LENA_ENTITY}, mappe=RuntimeError("Verbindung weg"),
                       stored=[FROM_FACT, FROM_TALK], bestand=[POOL_HIT])

        self.assertIsNotNone(lauf.result)
        self.assertEqual([h.source for h in lauf.offer],
                         [SOURCE_PROPERTIES, SOURCE_PROPERTIES, "kzg"])


class UnreadableBindingsTest(unittest.TestCase):
    """Nicht lesbare Bindungen sind laut — nicht still *nicht gebunden*."""

    def test_unreadable_bindings_are_loud_and_offer_no_facts(self) -> None:
        with patch.object(resolver_mod, "load_mappe", return_value=_mappe()) as lesen, \
             self.assertLogs(_RESOLVER_LOGGER, level="ERROR"):
            self.assertEqual(fact_hits(_artifact(), "u", "c", None), [])
        lesen.assert_not_called()

    def test_twin_readable_bindings_offer_the_facts(self) -> None:
        with patch.object(resolver_mod, "load_mappe", return_value=_mappe()):
            hits = fact_hits(_artifact(), "u", "c", {"lena": LENA_ENTITY})
        self.assertEqual([h[1] for h in hits], ["fakten#7", "fakten#8"])

    def test_the_facts_are_capped(self) -> None:
        with patch.object(resolver_mod, "load_mappe", return_value=_mappe()), \
             patch.object(resolver_mod, "SACHLAGE_FAKTEN_ANGEBOT_MAX", 1):
            hits = fact_hits(_artifact(), "u", "c", {"lena": LENA_ENTITY})
        self.assertEqual([h[1] for h in hits], ["fakten#7"])


def _november(count: int) -> list[dict]:
    """`count` Termine im November, je einer am Tag ab dem 2., um 10 Uhr."""
    return [
        _row(100 + day, datetime(2026, 11, 1 + day, 10, 0, tzinfo=BERLIN), f"Termin {day}")
        for day in range(1, count + 1)
    ]


#: Drei Eintraege des Pools, nach Gewicht absteigend.
POOL: list[dict] = [
    {"quelle": "kzg", "inhalt": f"Pool-Eintrag {i}", "gewicht": 0.9 - i / 10, "subtyp": f"p{i}"}
    for i in range(3)
]


class TheCalendarIsCappedTest(unittest.TestCase):
    """Ein voller Monat verdraengt weder den Pool noch die Fakten."""

    def _offer(self, count: int) -> tuple[list[MemoryHit], list[str]]:
        """Das Angebot eines Turns mit `count` Novemberterminen und drei Pool-Eintraegen."""
        state: dict = {"user_id": "pruefer", "character_id": "nova", "memory_entries": POOL}
        with _repository(FakeTimeline(_november(count))), patch(_CLOCK, return_value=NOW), \
             self.assertLogs(_RESOLVER_LOGGER, level="INFO") as logs:
            hits: list[MemoryHit] = resolver_mod.memory_offer(
                state, {"objekte": [_period("November")]},
            )
        return hits, logs.output

    def test_twelve_appointments_give_five_lines_and_keep_the_pool(self) -> None:
        hits, logs = self._offer(12)

        self.assertEqual(
            [h.origin for h in hits if h.source == SOURCE_CALENDAR],
            ["timeline#101", "timeline#102", "timeline#103", "timeline#104", "timeline#105"],
        )
        self.assertEqual([h.origin for h in hits if h.source == "kzg"], ["p0", "p1", "p2"])
        self.assertEqual([h.key for h in hits], [f"G{n}" for n in range(1, 9)])
        self.assertTrue(any("Kalender 12 gelesen, 7 weggelassen" in z for z in logs), logs)

    def test_twin_three_appointments_give_exactly_three(self) -> None:
        hits, logs = self._offer(3)

        self.assertEqual(
            [h.origin for h in hits if h.source == SOURCE_CALENDAR],
            ["timeline#101", "timeline#102", "timeline#103"],
        )
        self.assertEqual(len([h for h in hits if h.source == "kzg"]), 3)
        self.assertTrue(any("Kalender 3 gelesen, 0 weggelassen" in z for z in logs), logs)

    def test_the_facts_stay_beside_a_full_month(self) -> None:
        bestand, _ = self._offer(12)
        lauf = _Derive(bound={"lena": LENA_ENTITY}, bestand=bestand)

        self.assertEqual(
            [h.source for h in lauf.offer],
            [SOURCE_FACTS] * 2 + [SOURCE_CALENDAR] * 5 + ["kzg"] * 3,
        )


class _BoundPairFixture(_PairFixture):
    """Das Paar des Schemazeugen und eine eigene Entitaet, abgeraeumt auch bei Rot."""

    def _entity(self) -> int:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO entitaeten (user_id, name, typ)
                       VALUES (%s, 'Geburtstag', 'sonstiges') RETURNING id""",
                    (self.user,),
                )
                entity_id: int = cur.fetchone()[0]
            conn.commit()
        finally:
            conn.close()
        self.addCleanup(self._drop_entities)
        return entity_id

    def _drop_entities(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))
            conn.commit()
        finally:
            conn.close()


class BoundEntitiesTest(_BoundPairFixture):
    """`bound_entities` unterscheidet *nicht gebunden* (`{}`) von *nicht lesbar* (None)."""

    def test_unbound_is_empty_and_bound_is_named(self) -> None:
        erst = self._record(0, {"wann": "1. Juli"})
        self.assertEqual(
            bound_entities(POSTGRES_URL, self.user, self.char, ["geburtstag"]), {},
        )
        entity_id: int = self._entity()
        self.assertTrue(bind_entity(
            POSTGRES_URL, erst.object_ids["geburtstag"], entity_id, BINDING_TURN_MAGNET,
        ))
        self.assertEqual(
            bound_entities(POSTGRES_URL, self.user, self.char, ["geburtstag"]),
            {"geburtstag": entity_id},
        )

    def test_a_database_error_is_none_not_empty(self) -> None:
        with patch("memory.sachlage_properties.psycopg2.connect",
                   side_effect=psycopg2.OperationalError("Verbindung weg")), \
             self.assertLogs(_PROPERTIES_LOGGER, level="ERROR"):
            self.assertIsNone(
                bound_entities(POSTGRES_URL, self.user, self.char, ["geburtstag"]),
            )


class RuleCInTheSelectionTest(_BoundPairFixture):
    """Regel (c) wirkt in der Abfrage — eine verborgene Zeile belegt keinen Platz.

    `anlass` stammt aus dem Gespraech (Turn 0), `wann` aus dem Fakt 7 und ist
    die juengste Zeile (Turn 1, eigene Transaktion, spaeteres `last_touched`):
    Ohne die Bedingung waehlte `LIMIT 1` sie.
    """

    def setUp(self) -> None:
        super().setUp()
        self._record(0, {"anlass": "zehnter"})
        self._record(
            1, {"wann": "1. Juli"},
            quellen={"wann": {"quelle": "fakten", "herkunft": "fakten#7", "eintrag": "G1"}},
        )

    def _names(
        self, limit: int, hidden_for: tuple[str, ...], offered: tuple[str, ...] = ("fakten#7",),
    ) -> list[str]:
        rows: list[dict] = active_properties(
            POSTGRES_URL, self.user, self.char, ["geburtstag"], limit,
            hidden_source=SOURCE_FACTS, hidden_for=hidden_for, hidden_origins=offered,
        )
        return [r["eigenschaft"] for r in rows]

    def test_a_property_from_an_offered_fact_is_hidden_at_a_bound_object(self) -> None:
        self.assertEqual(self._names(10, ("geburtstag",)), ["anlass"])

    def test_twin_a_fact_not_offered_keeps_its_property(self) -> None:
        """(A): Fakt 8 ist angeboten, nicht Fakt 7 — `wann` bleibt, zuerst als juengste."""
        self.assertEqual(self._names(10, ("geburtstag",), ("fakten#8",)), ["wann", "anlass"])
        self.assertEqual(self._names(10, ("geburtstag",), ()), ["wann", "anlass"])

    def test_the_hidden_row_takes_no_place_under_the_limit(self) -> None:
        # Vorbedingung des Zeugen: Ohne Regel (c) belegt `wann` den einen Platz.
        self.assertEqual(self._names(1, (), ()), ["wann"])
        self.assertEqual(self._names(1, ("geburtstag",)), ["anlass"])

    def test_twin_at_another_object_it_stays_and_carries_its_source(self) -> None:
        self.assertEqual(self._names(10, ("feier",)), ["wann", "anlass"])
        rows: list[dict] = active_properties(
            POSTGRES_URL, self.user, self.char, ["geburtstag"], 10,
        )
        quelle: dict = next(r["quelle"] for r in rows if r["eigenschaft"] == "wann")
        self.assertEqual((quelle["quelle"], quelle["herkunft"]), (SOURCE_FACTS, "fakten#7"))

    def test_hidden_objects_without_a_source_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            active_properties(POSTGRES_URL, self.user, self.char, ["geburtstag"], 10,
                              hidden_for=("geburtstag",))

    def test_an_origin_of_another_source_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            active_properties(POSTGRES_URL, self.user, self.char, ["geburtstag"], 10,
                              hidden_source=SOURCE_FACTS, hidden_for=("geburtstag",),
                              hidden_origins=("timeline#7",))


if __name__ == "__main__":
    unittest.main()
