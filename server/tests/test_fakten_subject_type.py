"""Zeugen für den Typ des Subjekts: Ein Tripel schreibt nur, wenn die Beziehung ihn erlaubt.

Was diese Datei zusichert:
  * **Die Liste der Typen** (`ENTITY_TYPES`) und **die Typen des Subjekts je
    Beziehung** stehen als Literal: jede Beziehung nur `person`, `heisst`
    jeden Typ, `wohnt_in` und `geboren_in` dazu `tier`; `sonstiges` steht
    in keiner Menge, und `Relation` weist eine fremde Menge beim Import ab.
  * **`vet_triple` hält den Typ gegen die Beziehung**, je Regel und Ausnahme
    mit Zwilling: ein Ort, ein Tier, ein Objekt an einer Beziehung, die ihn
    nicht erlaubt, ist `verworfen:subjekt_typ`, laut im Log; `sonstiges`
    geht durch, mit einer Zeile im Log; ICH ist eine Person.
  * **Die Form des Felds:** fehlend, leer, außerhalb der Liste oder ein
    Wahrheitswert ist `verworfen:typ_form`, nie `sonstiges`.
  * **Die Reihenfolge der Stufen:** Scheitert ein Tripel an zwei Stufen, nennt
    das Urteil die frühere — Typ vor Äußerung und Figur, Kanon und
    Vorprüfung vor dem Typ; je mit Zwilling, der nur an einer Stufe scheitert.
  * **Jede Stufe vor dem Typ** steht als Literal mit ihrem Grund, und ein
    Tripel, das an ihr scheitert, zählt unter ihr — ohne `typ`, mit fremdem
    `typ` und mit `person`; die Stufen, der Typ und die Stufen danach ergeben
    genau `REJECT_REASONS`.
  * **Die Gründe:** `REJECT_REASONS` steht als Literal, und jeder Grund, den
    `vet_triple` und `link_event` liefern, liegt darin.
  * **Der Prompt** nennt jeden Typ; fehlt einer, wirft `build_classify_prompt`.
  * **Der Weg:** Ein Ort an `hat_hobby` ruft das Repository nicht auf, eine
    Person an derselben Stelle schreibt.

Kein Zeuge ruft ein Modell. Die Zeugen des Wegs schreiben in die
Wegwerf-Datenbank der Suite, mit eigenem Paar, und räumen in tearDown ab.
"""

import unittest
import uuid
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras

from agents import discover_agents
from agents.fakten import dispatch as fakten_dispatch_mod
from agents.fakten.beziehungen import ENTITY_TYPES, KANON, Relation
from agents.fakten.klassifikation import (
    REJECT_REASONS,
    build_classify_prompt,
    link_event,
    vet_triple,
)
from config import POSTGRES_URL, PROMPTS
from memory.repositories.fakten_repository import FaktenRepository
from plugins import discover_managers

VECTOR: list[float] = [1.0] + [0.0] * 767
LOGGER: str = "ki_server.agents.fakten.klassifikation"
ORDER: dict = {"ziel": "fakten", "aktion": "pruefen", "daten": {
    "turn_id": "probe-turn", "verlauf_id": 42, "salienz_human": 0.62,
    "user_intentionen": ["mitteilen"], "abgelegt": True,
}}
# Ein Satz über einen Ort, aus dem kein Fakt über einen Menschen wird.
PLACE_SENTENCE: str = "In Ostheim treffen sich jeden Herbst die Imker"


def _run_sql(sql: str, params: tuple) -> list[dict]:
    """Führt eine Abfrage gegen die Wegwerf-Datenbank aus und gibt die Zeilen zurück."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows: list[dict] = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return rows
    finally:
        conn.close()


def _candidate(obj: str, prop: str, value: str) -> dict:
    """Ein Kandidat des Menschen wie aus `turn_candidates`."""
    return {"id": 1, "objekt_id": 1, "objekt": obj, "klasse": "person", "entitaet_id": None,
            "entitaet_bindung": None, "eigenschaft": prop, "wert": value, "sprecher": "nutzer"}


def _triple(subject: str, relation: str, obj: str, **fields: object) -> dict:
    """Ein Tripel der Antwort auf Kandidat 1; `fields` setzt oder ersetzt `typ`."""
    return {"kandidat": 1, "subjekt": subject, "beziehung": relation, "objekt": obj, **fields}


def _verdict(utterance: str, candidate: dict, triple: dict) -> tuple[str, dict | None]:
    """(Grund, Tripel) aus `vet_triple` bei bejahter Vorprüfung."""
    verdict = vet_triple(triple, {1: candidate}, utterance, True)
    return verdict.grund, verdict.tripel


def _stage_cases(fields: dict) -> dict[str, tuple[str, dict, dict, bool]]:
    """Je Stufe vor der Typprüfung ein Fall, der nur an ihr scheitert; `fields` trägt `typ`.

    Grundlage ist ein Ort an `hat_hobby`, den die Äußerung nennt: Mit `typ`
    person besteht er jede Stufe, ohne `typ` scheitert er an `typ_form`, mit
    `ort` an `subjekt_typ`. Jeder Fall verdirbt genau eine Stufe vor dem Typ;
    der des Kanons setzt dazu ICH als Subjekt.
    Ergebnis: Name der Stufe -> (Äußerung, Kandidaten, Tripel, Vorprüfung).
    """
    person: dict = _candidate("Ostheim", "Treffen", "Imker")
    base: dict = _triple("Ostheim", "hat_hobby", "Imkerei", **fields)
    return {
        "nummer": (PLACE_SENTENCE, {1: person}, {**base, "kandidat": None}, True),
        "kandidat": (PLACE_SENTENCE, {1: person}, {**base, "kandidat": 7}, True),
        "sprecher": (PLACE_SENTENCE, {1: {**person, "sprecher": "nova"}}, base, True),
        "vorpruefung": (PLACE_SENTENCE, {1: person}, base, False),
        # ICH, nicht der Ort: Ohne Beziehung des Kanons ist ein Typ nur bei ICH
        # fremd, gleich welche Beziehung eine vorgezogene Typprüfung annimmt.
        "kanon": (PLACE_SENTENCE, {1: person},
                  {**base, "subjekt": "ICH", "beziehung": "braucht"}, True),
        # Ein leeres Objekt, nicht ein leeres Subjekt: Vor die Stufe gezogen,
        # gäbe die Typprüfung einen Grund zurück, statt am Subjekt zu werfen.
        "leer": (PLACE_SENTENCE, {1: person}, {**base, "objekt": ""}, True),
    }


class TypeListAndCanonTest(unittest.TestCase):
    """Jede Menge als eigenes Literal: Ein Element mehr oder weniger macht rot."""

    def test_the_list_holds_exactly_the_six_types_in_prompt_order(self) -> None:
        self.assertEqual(ENTITY_TYPES,
                         ("person", "ort", "organisation", "tier", "objekt", "sonstiges"))

    def test_heisst_alone_takes_every_type(self) -> None:
        every: frozenset[str] = frozenset({"person", "ort", "organisation", "tier", "objekt"})
        self.assertEqual(KANON["heisst"].subjekt_typen, every)
        self.assertEqual({a for a, r in KANON.items() if r.subjekt_typen == every}, {"heisst"})

    def test_wohnt_in_and_geboren_in_alone_also_take_an_animal(self) -> None:
        animal: frozenset[str] = frozenset({"person", "tier"})
        self.assertEqual({a for a, r in KANON.items() if r.subjekt_typen == animal},
                         {"wohnt_in", "geboren_in"})

    def test_every_other_relation_takes_exactly_a_person(self) -> None:
        for attribut in sorted(set(KANON) - {"heisst", "wohnt_in", "geboren_in"}):
            with self.subTest(attribut=attribut):
                self.assertEqual(KANON[attribut].subjekt_typen, frozenset({"person"}))

    def test_no_set_holds_sonstiges(self) -> None:
        self.assertEqual([a for a, r in KANON.items() if "sonstiges" in r.subjekt_typen], [])

    def test_a_relation_with_a_foreign_set_is_rejected_on_import(self) -> None:
        for wrong in (frozenset({"stadt"}), frozenset(), frozenset({"sonstiges"}),
                      frozenset({"person", "Ort"})):
            with self.subTest(subjekt_typen=wrong), self.assertRaises(ValueError):
                Relation("hat_hobby", False, False, "", wrong)
        # Zwilling: eine Menge aus der Liste.
        self.assertEqual(Relation("hat_hobby", False, False, "",
                                  frozenset({"person", "tier"})).subjekt_typen,
                         frozenset({"person", "tier"}))


class SubjectTypeVettingTest(unittest.TestCase):
    """`vet_triple`: je Regel und Ausnahme ein Zeuge mit Zwilling."""

    def test_a_place_at_hat_hobby_is_rejected_and_loud(self) -> None:
        with self.assertLogs(LOGGER, "ERROR") as log:
            reason, triple = _verdict(PLACE_SENTENCE, _candidate("Ostheim", "Treffen", "Imker"),
                                      _triple("Ostheim", "hat_hobby", "Imkerei", typ="ort"))
        self.assertEqual((reason, triple), ("subjekt_typ", None))
        self.assertTrue(any("Typ ort" in line for line in log.output), log.output)

    def test_twin_a_person_at_hat_hobby_passes(self) -> None:
        reason, triple = _verdict(PLACE_SENTENCE, _candidate("Ostheim", "Treffen", "Imker"),
                                  _triple("Ostheim", "hat_hobby", "Imkerei", typ="person"))
        self.assertEqual((reason, triple["beziehung"]), ("", "hat_hobby"))

    def test_an_animal_where_it_lives_and_was_born_passes(self) -> None:
        for utterance, relation in (("Rufus wohnt bei Ilva in Ostheim", "wohnt_in"),
                                    ("Rufus ist in Ostheim geboren", "geboren_in")):
            with self.subTest(relation=relation):
                reason, triple = _verdict(utterance, _candidate("Rufus", "Ort", "Ostheim"),
                                          _triple("Rufus", relation, "Ostheim", typ="tier"))
                self.assertEqual((reason, triple["subjekt"]), ("", "Rufus"))

    def test_twin_an_animal_at_hat_hobby_is_rejected(self) -> None:
        reason, triple = _verdict("Rufus jagt jeden Tag Mäuse",
                                  _candidate("Rufus", "Beschäftigung", "Mäuse jagen"),
                                  _triple("Rufus", "hat_hobby", "Mäuse jagen", typ="tier"))
        self.assertEqual((reason, triple), ("subjekt_typ", None))

    def test_an_object_at_heisst_passes(self) -> None:
        reason, triple = _verdict("Ilvas Gitarre heißt Lotte",
                                  _candidate("Gitarre", "Name", "Lotte"),
                                  _triple("Gitarre", "heisst", "Lotte", typ="objekt"))
        self.assertEqual((reason, triple["beziehung"]), ("", "heisst"))

    def test_twin_an_object_at_arbeitet_als_is_rejected_a_person_there_passes(self) -> None:
        utterance: str = "Die Gitarre arbeitet als Türstopper"
        candidate: dict = _candidate("Gitarre", "Beruf", "Türstopper")
        reason, triple = _verdict(utterance, candidate,
                                  _triple("Gitarre", "arbeitet_als", "Türstopper", typ="objekt"))
        self.assertEqual((reason, triple), ("subjekt_typ", None))
        reason, triple = _verdict(utterance, candidate,
                                  _triple("Gitarre", "arbeitet_als", "Türstopper", typ="person"))
        self.assertEqual((reason, triple["beziehung"]), ("", "arbeitet_als"))

    def test_sonstiges_passes_with_a_line_in_the_log(self) -> None:
        with self.assertLogs(LOGGER, "INFO") as log:
            reason, triple = _verdict(PLACE_SENTENCE, _candidate("Ostheim", "Treffen", "Imker"),
                                      _triple("Ostheim", "hat_hobby", "Imkerei", typ="sonstiges"))
        self.assertEqual((reason, triple["subjekt"]), ("", "Ostheim"))
        self.assertTrue(any("sonstiges" in line and "INFO" in line for line in log.output),
                        log.output)

    def test_the_self_as_a_person_passes(self) -> None:
        reason, triple = _verdict("Ich spiele jeden Sonntag Schach",
                                  _candidate("Mensch", "Hobby", "Schach"),
                                  _triple("ICH", "hat_hobby", "Schach", typ="person"))
        self.assertEqual((reason, triple["subjekt"]), ("", "ICH"))

    def test_the_self_as_an_animal_is_rejected_even_where_an_animal_may_live(self) -> None:
        # Zwilling: derselbe Satz mit `person` schreibt.
        utterance: str = "Mein Hund wohnt in Ostheim"
        candidate: dict = _candidate("Hund", "Wohnort", "Ostheim")
        reason, triple = _verdict(utterance, candidate,
                                  _triple("ICH", "wohnt_in", "Ostheim", typ="tier"))
        self.assertEqual((reason, triple), ("subjekt_typ", None))
        reason, triple = _verdict(utterance, candidate,
                                  _triple("ICH", "wohnt_in", "Ostheim", typ="person"))
        self.assertEqual((reason, triple["subjekt"]), ("", "ICH"))


class SubjectTypeFormTest(unittest.TestCase):
    """Die Form des Felds: ein Ausfall der Antwort, nie `sonstiges` — je mit Zwilling."""

    def test_a_missing_empty_foreign_or_boolean_type_is_rejected_by_form_and_loud(self) -> None:
        candidate: dict = _candidate("Ilva", "Wohnort", "Ostheim")
        for label, triple in (
            ("fehlt", _triple("Ilva", "wohnt_in", "Ostheim")),
            ("leer", _triple("Ilva", "wohnt_in", "Ostheim", typ="")),
            ("Rand", _triple("Ilva", "wohnt_in", "Ostheim", typ="   ")),
            ("fremd", _triple("Ilva", "wohnt_in", "Ostheim", typ="mensch")),
            ("Wahrheitswert", _triple("Ilva", "wohnt_in", "Ostheim", typ=True)),
            ("null", _triple("Ilva", "wohnt_in", "Ostheim", typ=None)),
        ):
            with self.subTest(label=label), self.assertLogs(LOGGER, "ERROR"):
                reason, vetted = _verdict("Ilva wohnt in Ostheim", candidate, triple)
                self.assertEqual((reason, vetted), ("typ_form", None))

    def test_twin_a_value_of_the_list_passes_also_with_margin_and_capitals(self) -> None:
        candidate: dict = _candidate("Ilva", "Wohnort", "Ostheim")
        for value in ("person", " Person ", "PERSON"):
            with self.subTest(typ=value):
                reason, vetted = _verdict("Ilva wohnt in Ostheim", candidate,
                                          _triple("Ilva", "wohnt_in", "Ostheim", typ=value))
                self.assertEqual((reason, vetted["subjekt"]), ("", "Ilva"))


class StageOrderTest(unittest.TestCase):
    """Scheitert ein Tripel an zwei Stufen, nennt das Urteil die frühere — je mit Zwilling.

    Gezählt wird je Grund; ein Tripel, das unter der späteren Stufe zählt,
    verschiebt die Zählung, ohne dass sich ändert, ob geschrieben wird.
    """

    def test_type_and_utterance_both_missed_count_as_subject_type(self) -> None:
        # Ein Ort, den die Äußerung nicht nennt; *du* an einer Beziehung nur für Personen.
        for label, utterance, candidate, triple in (
            ("aeusserung", PLACE_SENTENCE, _candidate("Ostheim", "Treffen", "Imker"),
             _triple("Hessen", "hat_hobby", "Imkerei", typ="ort")),
            ("figur", "Du arbeitest ab heute als Imkerin.", _candidate("Du", "Beruf", "Imkerin"),
             _triple("du", "arbeitet_als", "Imkerin", typ="tier")),
        ):
            with self.subTest(label=label), self.assertLogs(LOGGER, "ERROR"):
                reason, vetted = _verdict(utterance, candidate, triple)
                self.assertEqual((reason, vetted), ("subjekt_typ", None))

    def test_twin_with_a_person_only_the_utterance_stage_rejects(self) -> None:
        for expected, utterance, candidate, triple in (
            ("aeusserung", PLACE_SENTENCE, _candidate("Ostheim", "Treffen", "Imker"),
             _triple("Hessen", "hat_hobby", "Imkerei", typ="person")),
            ("figur", "Du arbeitest ab heute als Imkerin.", _candidate("Du", "Beruf", "Imkerin"),
             _triple("du", "arbeitet_als", "Imkerin", typ="person")),
        ):
            with self.subTest(expected=expected):
                reason, vetted = _verdict(utterance, candidate, triple)
                self.assertEqual((reason, vetted), (expected, None))

    def test_outside_the_canon_without_or_with_a_foreign_type_counts_as_canon(self) -> None:
        candidate: dict = _candidate("Mehl", "Bedarf", "ja")
        for label, triple in (("fehlt", _triple("ICH", "braucht", "Mehl")),
                              ("ICH als Tier", _triple("ICH", "braucht", "Mehl", typ="tier"))):
            with self.subTest(label=label):
                reason, vetted = _verdict("Wir brauchen noch Mehl", candidate, triple)
                self.assertEqual((reason, vetted), ("kanon", None))

    def test_twin_the_canon_stage_alone_and_the_type_stage_alone(self) -> None:
        candidate: dict = _candidate("Mehl", "Bedarf", "ja")
        reason, vetted = _verdict("Wir brauchen noch Mehl", candidate,
                                  _triple("ICH", "braucht", "Mehl", typ="person"))
        self.assertEqual((reason, vetted), ("kanon", None))
        # Dasselbe ohne `typ` an einer Beziehung des Kanons scheitert am Typ.
        with self.assertLogs(LOGGER, "ERROR"):
            reason, vetted = _verdict("Ich habe einen Hund namens Rufus",
                                      _candidate("Hund", "Name", "Rufus"),
                                      _triple("ICH", "hat_haustier", "Rufus"))
        self.assertEqual((reason, vetted), ("typ_form", None))

    def test_a_denied_precheck_without_or_with_a_foreign_type_counts_as_precheck(self) -> None:
        candidate: dict = _candidate("Kopf", "Zustand", "Sieb")
        for label, triple in (("fehlt", _triple("ICH", "hat_haustier", "Sieb")),
                              ("ICH als Tier", _triple("ICH", "hat_haustier", "Sieb", typ="tier"))):
            with self.subTest(label=label):
                verdict = vet_triple(triple, {1: candidate}, "Mein Kopf ist ein Sieb", False)
                self.assertEqual((verdict.grund, verdict.tripel), ("vorpruefung", None))

    def test_twin_the_precheck_alone_and_the_type_alone_under_an_affirmed_precheck(self) -> None:
        candidate: dict = _candidate("Kopf", "Zustand", "Sieb")
        verdict = vet_triple(_triple("ICH", "hat_haustier", "Sieb", typ="person"), {1: candidate},
                             "Mein Kopf ist ein Sieb", False)
        self.assertEqual((verdict.grund, verdict.tripel), ("vorpruefung", None))
        with self.assertLogs(LOGGER, "ERROR"):
            verdict = vet_triple(_triple("ICH", "hat_haustier", "Sieb"), {1: candidate},
                                 "Mein Kopf ist ein Sieb", True)
        self.assertEqual((verdict.grund, verdict.tripel), ("typ_form", None))


class StagesBeforeTypeTest(unittest.TestCase):
    """Jede Stufe vor der Typprüfung verwirft unter ihrem Grund, ob `typ` fehlt oder fremd ist.

    Rückt die Typprüfung vor eine dieser Stufen, nennt das Urteil `typ_form`
    oder `subjekt_typ` — die Zählung je Grund verschiebt sich still.
    """

    # Die Stufen von `vet_triple` vor der Typprüfung, in ihrer Reihenfolge, je mit Grund.
    STAGES: tuple[tuple[str, str], ...] = (
        ("nummer", "form"),
        ("kandidat", "kandidat_unbekannt"),
        ("sprecher", "sprecher"),
        ("vorpruefung", "vorpruefung"),
        ("kanon", "kanon"),
        ("leer", "form"),
    )
    TYPE_REASONS: frozenset[str] = frozenset({"typ_form", "subjekt_typ"})
    # Danach: die Äußerung (`_against_utterance`) und das Ereignis (`link_event`).
    AFTER_TYPE: frozenset[str] = frozenset({"aeusserung", "figur", "vorliebe", "ereignis_fehlt"})

    def _assert_each_stage_rejects(self, fields: dict) -> None:
        """Jeder Fall aus `_stage_cases(fields)` trägt den Grund seiner Stufe und kein Tripel."""
        cases: dict[str, tuple[str, dict, dict, bool]] = _stage_cases(fields)
        for stage, expected in self.STAGES:
            utterance, candidates, triple, dauerhaft = cases[stage]
            with self.subTest(stage=stage, fields=fields):
                verdict = vet_triple(triple, candidates, utterance, dauerhaft)
                self.assertEqual((verdict.grund, verdict.tripel), (expected, None))

    def test_without_a_type_every_stage_counts_under_its_own_reason(self) -> None:
        self._assert_each_stage_rejects({})

    def test_with_a_foreign_type_every_stage_counts_under_its_own_reason(self) -> None:
        self._assert_each_stage_rejects({"typ": "ort"})

    def test_twin_with_a_person_every_stage_still_rejects_under_its_reason(self) -> None:
        self._assert_each_stage_rejects({"typ": "person"})

    def test_twin_the_base_passes_every_stage_and_misses_only_at_the_type(self) -> None:
        # Ohne den Fehler der Stufe scheitert dasselbe Tripel am Typ — oder schreibt.
        person: dict = _candidate("Ostheim", "Treffen", "Imker")
        for fields, expected in (({}, "typ_form"), ({"typ": "ort"}, "subjekt_typ")):
            with self.subTest(fields=fields), self.assertLogs(LOGGER, "ERROR"):
                verdict = vet_triple(_triple("Ostheim", "hat_hobby", "Imkerei", **fields),
                                     {1: person}, PLACE_SENTENCE, True)
                self.assertEqual((verdict.grund, verdict.tripel), (expected, None))
        verdict = vet_triple(_triple("Ostheim", "hat_hobby", "Imkerei", typ="person"),
                             {1: person}, PLACE_SENTENCE, True)
        self.assertEqual((verdict.grund, verdict.tripel["subjekt"]), ("", "Ostheim"))

    def test_the_stages_with_the_type_and_the_later_ones_make_up_the_reasons(self) -> None:
        # Wächst eine Stufe mit eigenem Grund, fehlt er hier und dieser Zeuge wird rot.
        self.assertEqual([stage for stage, _ in self.STAGES], list(_stage_cases({})))
        before: frozenset[str] = frozenset(reason for _, reason in self.STAGES)
        self.assertEqual(before | self.TYPE_REASONS | self.AFTER_TYPE, REJECT_REASONS)
        self.assertEqual(before & (self.TYPE_REASONS | self.AFTER_TYPE), frozenset())


class RejectReasonsTest(unittest.TestCase):
    """Die Gründe der Verwerfung: die Menge als Literal, jeder gelieferte Grund darin."""

    REASONS: frozenset[str] = frozenset({
        "form", "kandidat_unbekannt", "sprecher", "vorpruefung", "kanon", "aeusserung",
        "figur", "vorliebe", "ereignis_fehlt", "typ_form", "subjekt_typ",
    })

    def test_the_set_holds_exactly_the_eleven_reasons(self) -> None:
        self.assertEqual(REJECT_REASONS, self.REASONS)

    def test_every_reason_the_vetting_delivers_lies_in_the_set(self) -> None:
        person: dict = _candidate("Ostheim", "Treffen", "Imker")
        passing: tuple = (PLACE_SENTENCE, {1: person},
                          _triple("Ostheim", "hat_hobby", "Imkerei", typ="person"))
        paths: list[tuple[str, tuple, bool]] = [
            ("form", (PLACE_SENTENCE, {1: person}, "kein Objekt"), True),
            ("form", (PLACE_SENTENCE, {1: person}, _triple("", "hat_hobby", "Imkerei",
                                                           typ="person")), True),
            ("kandidat_unbekannt", (PLACE_SENTENCE, {1: person},
                                    {**passing[2], "kandidat": 7}), True),
            ("sprecher", (PLACE_SENTENCE, {1: {**person, "sprecher": "nova"}}, passing[2]), True),
            ("vorpruefung", passing, False),
            ("kanon", ("Wir brauchen noch Mehl", {1: _candidate("Mehl", "Bedarf", "ja")},
                       _triple("ICH", "braucht", "Mehl", typ="person")), True),
            ("typ_form", (PLACE_SENTENCE, {1: person},
                          _triple("Ostheim", "hat_hobby", "Imkerei")), True),
            ("subjekt_typ", (PLACE_SENTENCE, {1: person},
                             _triple("Ostheim", "hat_hobby", "Imkerei", typ="ort")), True),
            ("figur", ("Du arbeitest ab heute als Imkerin.",
                       {1: _candidate("Du", "Beruf", "Imkerin")},
                       _triple("du", "arbeitet_als", "Imkerin", typ="person")), True),
            ("vorliebe", ("Merten mag Schach.", {1: _candidate("Merten", "Spiel", "Schach")},
                          _triple("Merten", "hat_hobby", "Schach", typ="person")), True),
            ("aeusserung", (PLACE_SENTENCE, {1: person},
                            _triple("Hessen", "hat_hobby", "Imkerei", typ="person")), True),
        ]
        reached: set[str] = set()
        for expected, (utterance, candidates, triple), dauerhaft in paths:
            with self.subTest(expected=expected, triple=triple):
                reason: str = vet_triple(triple, candidates, utterance, dauerhaft).grund
                self.assertEqual(reason, expected)
                self.assertIn(reason, REJECT_REASONS)
                reached.add(reason)
        # Der Grund aus `link_event`: das Ereignis des Kandidaten fehlt.
        with self.assertLogs(LOGGER, "ERROR"):
            linked = link_event(vet_triple(passing[2], passing[1], passing[0], True), {1: None})
        self.assertEqual(linked.grund, "ereignis_fehlt")
        self.assertIn(linked.grund, REJECT_REASONS)
        reached.add(linked.grund)
        # Jeder Grund des Literals hat hier einen Pfad.
        self.assertEqual(reached, self.REASONS)


class SubjectTypePromptTest(unittest.TestCase):
    """Der Prompt fragt das Feld ab und nennt jeden Typ der Liste."""

    def test_the_prompt_names_every_type_and_asks_for_the_field(self) -> None:
        prompt: str = build_classify_prompt()
        for value in ("person", "ort", "organisation", "tier", "objekt", "sonstiges"):
            with self.subTest(typ=value):
                self.assertIn(f"  - {value}\n", prompt)
        self.assertIn('"typ":', prompt)
        self.assertIn("TYP DES SUBJEKTS", prompt)
        self.assertIn(f'"{PLACE_SENTENCE}"', prompt)

    def test_a_missing_type_makes_the_prompt_raise(self) -> None:
        task: str = PROMPTS["classify_fakten.task"]
        self.assertIn("{typen}", task)
        short: str = task.replace("{typen}", "  - person\n  - tier")
        with patch.dict(PROMPTS, {"classify_fakten.task": short}), \
                self.assertRaises(RuntimeError) as raised:
            build_classify_prompt()
        self.assertIn("'ort'", str(raised.exception))


class SubjectTypeOnTheWayTest(unittest.TestCase):
    """Der Weg bis zum Schreiben: Auftrag → Klassifikation → Prüfung → Repository."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def setUp(self) -> None:
        self.user: str = f"test-subjtyp-{uuid.uuid4().hex[:8]}"
        self.char: str = "nova-test"
        self.model = MagicMock()
        embedding = MagicMock()
        embedding.embed.submit_sync.return_value.embedding = VECTOR
        embedding.embed.submit_sync.return_value.duration_seconds = 0.0
        for target, double in (("agents.fakten.klassifikation.model_service", self.model),
                               ("memory.services.entity_resolution.model_service", embedding)):
            replacement = patch(target, double)
            replacement.start()
            self.addCleanup(replacement.stop)

    def tearDown(self) -> None:
        _run_sql("DELETE FROM fakten WHERE user_id = %s", (self.user,))
        _run_sql("DELETE FROM entitaeten WHERE user_id = %s", (self.user,))

    def _run(self, typ: str) -> tuple[dict, MagicMock]:
        """Ein Auftrag mit dem Satz über den Ort; (Eintrag des Tripels, Spion des Repositorys)."""
        self.model.chat.submit_sync.return_value.parsed = {
            "dauerhafte_aussage": True, "grund": "Probe",
            "tripel": [_triple("Ostheim", "hat_hobby", "Imkerei", typ=typ)],
        }
        state: dict = {"user_id": self.user, "character_id": self.char,
                       "turn_id": "probe-turn", "user_prompt": PLACE_SENTENCE}
        with patch.object(fakten_dispatch_mod, "turn_candidates",
                          return_value=[_candidate("Ostheim", "Treffen", "Imker")]), \
             patch.object(fakten_dispatch_mod, "log_db_write") as entry, \
             patch.object(FaktenRepository, "schreiben",
                          wraps=FaktenRepository.schreiben) as spy:
            fakten_dispatch_mod.process_fact_orders(state, [ORDER], POSTGRES_URL)
        entry.assert_called_once()
        content: dict = entry.call_args.kwargs["inhalt"]
        self.assertEqual(content["tripel_zahl"], 1, content)
        return content["tripel"][0], spy

    def _facts(self) -> list[dict]:
        return _run_sql("SELECT attribut, objekt_wert FROM fakten WHERE user_id = %s",
                        (self.user,))

    def test_a_place_at_hat_hobby_never_reaches_the_repository(self) -> None:
        triple, spy = self._run("ort")
        self.assertEqual(triple["ausgang"], "verworfen:subjekt_typ")
        spy.assert_not_called()
        self.assertEqual(self._facts(), [])
        self.assertEqual(_run_sql("SELECT id FROM entitaeten WHERE user_id = %s", (self.user,)),
                         [])

    def test_twin_a_person_at_hat_hobby_writes(self) -> None:
        triple, spy = self._run("person")
        self.assertEqual(triple["ausgang"], "angelegt")
        spy.assert_called_once()
        self.assertEqual(self._facts(), [{"attribut": "hat_hobby", "objekt_wert": "Imkerei"}])


if __name__ == "__main__":
    unittest.main()
