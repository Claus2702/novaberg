"""Zeugen: Ein Wert ausserhalb des Kanons wirkt an keiner Verwendungsstelle staerker als neutral.

Die Perzeption und die Salienz sind durchlaessig: Sie ziehen Schreibvarianten
auf den Kanon und lassen einen unbekannten Wert durch, damit er stromabwaerts
gemeldet wird. **Abgelehnt wird an der Verwendungsstelle** — in den
Faktortabellen des EI-Gates, der Neugier und der Faszination mit einem
neutralen Faktor, im Kurzzeitgedaechtnis mit einem leeren Modus und ohne die
fremde Intention. Jede Stelle schreibt eine Fehlerzeile mit Feld und Wert.

Die Fremdwerte sind die gemessenen: `philosophischer_austausch` (ein Modus)
im Feld `intent`, `begeisterung` (eine Emotion) im Feld `tone`, ein Modus in
Prosa im Feld `modus` der Salienz.

Reine Funktionen und Attrappen fuer Redis und die Auftragsqueue: kein Dienst,
keine Datenbank. Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import json
import logging
import re
import unittest
from collections.abc import Callable, Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.kzg import queues, speicher
from config import (
    EI_DYNAMIK_FAKTOREN,
    EI_DYNAMIK_NEUTRAL,
    EI_INTENT_FAKTOREN,
    EI_INTENT_NEUTRAL,
    EI_TONE_FAKTOREN,
    EI_TONE_NEUTRAL,
    FASZ_INTENT_FAKTOREN,
    FASZ_INTENT_NEUTRAL,
    FASZ_MODUS_FAKTOREN,
    FASZ_MODUS_NEUTRAL,
    GV_AUFNAHMEBEREITSCHAFT_DYNAMIK,
    GV_AUFNAHMEBEREITSCHAFT_DYNAMIK_NEUTRAL,
    GV_AUFNAHMEBEREITSCHAFT_MODUS,
    GV_AUFNAHMEBEREITSCHAFT_MODUS_NEUTRAL,
    GV_AUFNAHMEBEREITSCHAFT_STIL,
    GV_AUFNAHMEBEREITSCHAFT_STIL_NEUTRAL,
)
from ei import fascination
from ei.berechnung import _ei_arousal_berechnen, _ei_faktor_lesen
from ei.neugier import _neugier_faktor_lesen, aufnahmebereitschaft_berechnen
from graph.personality import Emotion, InternalPersonality
from memory.kzg import _kanon_felder_pruefen, kzg_store

SERVER: Path = Path(__file__).resolve().parents[1]

FOREIGN_MODE: str = "Philosophisch-spielerischer Austausch"
FOREIGN_INTENTIONS: list[str] = ["reflexion", "philosophischer_austausch"]
CANON_INTENTIONS: list[str] = ["reflexion", "planung"]

# Jede Faktortabelle eines Kanon-Felds der Perzeption mit ihrem neutralen
# Faktor — der Gegenstand des Vollstaendigkeitszeugen unten.
TABLE_NEUTRAL: dict[str, str] = {
    "EI_DYNAMIK_FAKTOREN":             "EI_DYNAMIK_NEUTRAL",
    "EI_INTENT_FAKTOREN":              "EI_INTENT_NEUTRAL",
    "EI_TONE_FAKTOREN":                "EI_TONE_NEUTRAL",
    "GV_AUFNAHMEBEREITSCHAFT_MODUS":   "GV_AUFNAHMEBEREITSCHAFT_MODUS_NEUTRAL",
    "GV_AUFNAHMEBEREITSCHAFT_DYNAMIK": "GV_AUFNAHMEBEREITSCHAFT_DYNAMIK_NEUTRAL",
    "GV_AUFNAHMEBEREITSCHAFT_STIL":    "GV_AUFNAHMEBEREITSCHAFT_STIL_NEUTRAL",
    "FASZ_INTENT_FAKTOREN":            "FASZ_INTENT_NEUTRAL",
    "FASZ_MODUS_FAKTOREN":             "FASZ_MODUS_NEUTRAL",
}


def _errors(records: list[logging.LogRecord]) -> list[str]:
    """Die Fehlerzeilen eines `assertLogs`-Mitschnitts als Text."""
    return [r.getMessage() for r in records if r.levelno >= logging.ERROR]


def _lines_naming(errors: list[str], field: str, value: str) -> list[str]:
    """Die Fehlerzeilen, die Feld und Wert zugleich nennen."""
    return [z for z in errors if f"`{field}`" in z and value in z]


class EiGateTakesTheNeutralFactorTest(unittest.TestCase):
    """`_ei_arousal_berechnen` — ein fremder Wert verstaerkt das EI-Gate nicht."""

    def test_the_measured_foreign_values_get_the_neutral_factors(self) -> None:
        """0.5 x (0.40 x 1.0 + 0.35 x 0.533 + 0.25 x 0.725) = 0.3839, nicht 0.5."""
        with self.assertLogs("ki_server.ei.berechnung", "INFO") as log:
            wert: float = _ei_arousal_berechnen(
                0.5, "neutral", "philosophischer_austausch", "begeisterung",
            )
        self.assertAlmostEqual(0.3839, wert, 4)
        errors: list[str] = _errors(log.records)
        self.assertEqual(1, len(_lines_naming(errors, "intent", "philosophischer_austausch")))
        self.assertEqual(1, len(_lines_naming(errors, "tone", "begeisterung")))
        self.assertEqual(2, len(errors), errors)

    def test_a_foreign_dynamic_gets_its_neutral_factor(self) -> None:
        """0.5 x (0.40 x 1.0 + 0.35 x 0.3 + 0.25 x 0.3) = 0.29 — der Eintrag `neutral`."""
        with self.assertLogs("ki_server.ei.berechnung", "INFO") as log:
            wert: float = _ei_arousal_berechnen(0.5, "wohlwollend", "knowledge", "sachlich")
        self.assertAlmostEqual(0.29, wert, 4)
        errors: list[str] = _errors(log.records)
        self.assertEqual(1, len(_lines_naming(errors, "beziehungs_dynamik", "wohlwollend")))
        self.assertEqual(1, len(errors), errors)

    def test_canon_values_act_as_before(self) -> None:
        """Zwilling: 0.5 x (0.40 x 1.1 + 0.35 x 1.0 + 0.25 x 1.3) = 0.5575, ohne Fehlerzeile."""
        with self.assertLogs("ki_server.ei.berechnung", "INFO") as log:
            wert: float = _ei_arousal_berechnen(0.5, "vertrauen", "personal", "empathisch")
        self.assertAlmostEqual(0.5575, wert, 4)
        self.assertEqual([], _errors(log.records))

    def test_a_neutral_at_the_maximum_is_refused(self) -> None:
        """Der Riegel gegen die Klasse selbst: 1.0 ist das Maximum der Intent-Tabelle."""
        with self.assertRaises(ValueError):
            _ei_faktor_lesen(EI_INTENT_FAKTOREN, 1.0, "personal", "intent")


class CuriosityTakesTheNeutralFactorTest(unittest.TestCase):
    """`_neugier_faktor_lesen` — die Saeulen M, D, S der Neugier."""

    def test_a_foreign_style_gets_the_neutral_factor(self) -> None:
        with self.assertLogs("ki_server.ei.neugier", "ERROR") as log:
            faktor: float = _neugier_faktor_lesen(
                GV_AUFNAHMEBEREITSCHAFT_STIL, GV_AUFNAHMEBEREITSCHAFT_STIL_NEUTRAL,
                "sachlich", "sprach_stil",
            )
        self.assertEqual(1.0, faktor)
        self.assertEqual(1, len(_lines_naming(_errors(log.records), "sprach_stil", "sachlich")))

    def test_a_foreign_mode_gets_the_neutral_factor_not_the_maximum(self) -> None:
        with self.assertLogs("ki_server.ei.neugier", "ERROR"):
            faktor: float = _neugier_faktor_lesen(
                GV_AUFNAHMEBEREITSCHAFT_MODUS, GV_AUFNAHMEBEREITSCHAFT_MODUS_NEUTRAL,
                FOREIGN_MODE, "modus",
            )
        self.assertEqual(1.140, faktor)

    def test_a_canon_value_acts_as_before(self) -> None:
        """Zwilling: `locker` traegt 1.20, ohne Fehlerzeile."""
        with self.assertLogs("ki_server.ei.neugier", "DEBUG") as log:
            logging.getLogger("ki_server.ei.neugier").debug("Zeuge: Mitschnitt offen")
            faktor: float = _neugier_faktor_lesen(
                GV_AUFNAHMEBEREITSCHAFT_STIL, GV_AUFNAHMEBEREITSCHAFT_STIL_NEUTRAL,
                "locker", "sprach_stil",
            )
        self.assertEqual(1.20, faktor)
        self.assertEqual([], _errors(log.records))


# Die Faktoren der Saeulen M, D, S in der Zeile, die die Neugier je Lauf schreibt.
_PILLARS: re.Pattern[str] = re.compile(r"M=(\d+\.\d\d), D=(\d+\.\d\d), S=(\d+\.\d\d)")


# Emotion, Arousal und Vektor, unter denen die Saeulen E, A, V auf 1.25, 1.15
# und 0.90 stehen — keine davon auf 1.0, keine zwei gleich.
EAV_OFF_NEUTRAL: tuple[str, float, str] = ("freude", 0.6, "abkuehlung")


def _curiosity_state(
    modus: str, dynamik: str, stil: str,
    eav: tuple[str, float, str] = ("neutral", 0.5, ""),
) -> dict:
    """Ein Zustand ohne Emotionsverlauf: die Neugier liest Novas eigene Emotion."""
    emotion_name, arousal, vektor = eav
    emotion: Emotion = Emotion(
        emotion=emotion_name, arousal=arousal, emotions_vector=vektor, mode=modus,
        relationship_dynamic=dynamik, language_style=stil,
    )
    return {"nova_emotions_verlauf": [], "internal": InternalPersonality(emotion=emotion)}


class CuriosityPillarsTakeTheNeutralFactorTest(unittest.TestCase):
    """`aufnahmebereitschaft_berechnen` — jede Saeule liest ihre eigene Tabelle.

    Gefahren wird der ganze Weg, nicht die Pruefung allein: Eine Saeule, die
    ihre Tabelle nicht mehr liest oder den neutralen Faktor einer anderen
    Tabelle nimmt, faellt nur hier auf. Die Erwartung steht als Literal.

    Die Zeile nennt die Faktoren, nicht ihr Produkt: Eine Saeule, die aus der
    Produktzeile faellt, steht dort weiter. Deshalb prueft je ein Zeuge das
    Ergebnis, mit Eingaben, unter denen jede der sechs Saeulen einen eigenen
    Faktor ungleich 1.0 traegt — gerechnet aus den Literalen der Tabellen.
    """

    def _run(self, modus: str, dynamik: str, stil: str) -> tuple[tuple[str, ...], list[str]]:
        with self.assertLogs("ki_server.ei.neugier", "INFO") as log:
            aufnahmebereitschaft_berechnen(_curiosity_state(modus, dynamik, stil))
        saeulen: list[tuple[str, ...]] = [
            treffer.groups() for r in log.records
            if (treffer := _PILLARS.search(r.getMessage()))
        ]
        self.assertEqual(1, len(saeulen), [r.getMessage() for r in log.records])
        return saeulen[0], _errors(log.records)

    def test_foreign_values_get_the_neutral_factor_of_each_pillar(self) -> None:
        """M 1.14 (Mittel der Modus-Tabelle), D und S 1.00 (ihr Eintrag `neutral`)."""
        saeulen, errors = self._run(FOREIGN_MODE, "wohlwollend", "sachlich")
        self.assertEqual(("1.14", "1.00", "1.00"), saeulen)
        self.assertEqual(1, len(_lines_naming(errors, "modus", FOREIGN_MODE)))
        self.assertEqual(1, len(_lines_naming(errors, "beziehungs_dynamik", "wohlwollend")))
        self.assertEqual(1, len(_lines_naming(errors, "sprach_stil", "sachlich")))
        self.assertEqual(3, len(errors), errors)

    def test_canon_values_reach_each_pillar(self) -> None:
        """Zwilling: 1.30, 1.30, 1.20 — eine abgeklemmte Saeule stuende auf 1.00."""
        saeulen, errors = self._run("lernmodus", "vertrauen", "locker")
        self.assertEqual(("1.30", "1.30", "1.20"), saeulen)
        self.assertEqual([], errors)

    def test_every_pillar_reaches_the_result(self) -> None:
        """E 1.25 (`freude`, Distanz 1), A 1.15 (0.6), V 0.90, M 1.40, D 0.85, S 0.95.

        Produkt 1.4625844, roh 0.5 x 1.4625844 = 0.7312922;
        sqrt(sin(0.7312922 / 2.5 x pi/2)) = 0.66595. Ohne eine Saeule laege
        der Wert mindestens 0.015 daneben (ohne S: 0.68193).
        """
        with self.assertLogs("ki_server.ei.neugier", "INFO") as log:
            wert: float = aufnahmebereitschaft_berechnen(_curiosity_state(
                "spielerisch", "hilfesuchend", "fachlich", EAV_OFF_NEUTRAL,
            ))
        self.assertAlmostEqual(0.66595, wert, 4)
        self.assertEqual([], _errors(log.records))

    def test_foreign_values_reach_the_result_with_the_neutral_factors(self) -> None:
        """E 1.25, A 1.15, V 0.90 wie oben; M 1.14, D 1.00, S 1.00 (die neutralen).

        Produkt 1.474875, roh 0.7374375; sqrt(sin(0.7374375 / 2.5 x pi/2))
        = 0.66854.
        """
        with self.assertLogs("ki_server.ei.neugier", "INFO") as log:
            wert: float = aufnahmebereitschaft_berechnen(_curiosity_state(
                FOREIGN_MODE, "wohlwollend", "sachlich", EAV_OFF_NEUTRAL,
            ))
        self.assertAlmostEqual(0.66854, wert, 4)
        self.assertEqual(3, len(_errors(log.records)), _errors(log.records))


class FascinationTakesTheNeutralFactorTest(unittest.TestCase):
    """`f_intent`, `f_modus` — die Modulatoren aus den Kanon-Feldern der Perzeption."""

    def test_a_foreign_intent_is_an_error_with_the_neutral_factor(self) -> None:
        with self.assertLogs("ki_server.ei.fascination", "ERROR") as log:
            faktor: float = fascination.f_intent("philosophischer_austausch")
        self.assertEqual(1.000, faktor)
        self.assertEqual(
            1, len(_lines_naming(_errors(log.records), "intent", "philosophischer_austausch")),
        )

    def test_a_foreign_mode_is_an_error_with_the_neutral_factor(self) -> None:
        with self.assertLogs("ki_server.ei.fascination", "ERROR") as log:
            faktor: float = fascination.f_modus(FOREIGN_MODE)
        self.assertEqual(1.020, faktor)
        self.assertEqual(1, len(_errors(log.records)))

    def test_a_canon_mode_acts_as_before(self) -> None:
        """Zwilling: `lernmodus` traegt 1.15."""
        self.assertEqual(1.15, fascination.f_modus("lernmodus"))


class NoNeutralIsTheMaximumOfItsTableTest(unittest.TestCase):
    """Das Kriterium: neutral liegt unter dem Maximum und nicht unter dem Minimum.

    Die Erwartung steht als Literal. Traegt die Tabelle einen Eintrag
    `neutral`, ist der neutrale Faktor dessen Wert, sonst das Mittel der
    Tabelle; beides wird zusaetzlich gegen das Literal gehalten, damit eine
    geaenderte Tabelle ohne neuen neutralen Faktor rot wird.
    """

    CASES: tuple[tuple[str, dict[str, float], float, float], ...] = (
        ("EI_DYNAMIK", EI_DYNAMIK_FAKTOREN, EI_DYNAMIK_NEUTRAL, 1.0),
        ("EI_INTENT", EI_INTENT_FAKTOREN, EI_INTENT_NEUTRAL, 0.533),
        ("EI_TONE", EI_TONE_FAKTOREN, EI_TONE_NEUTRAL, 0.725),
        ("GV_MODUS", GV_AUFNAHMEBEREITSCHAFT_MODUS, GV_AUFNAHMEBEREITSCHAFT_MODUS_NEUTRAL, 1.140),
        ("GV_DYNAMIK", GV_AUFNAHMEBEREITSCHAFT_DYNAMIK,
         GV_AUFNAHMEBEREITSCHAFT_DYNAMIK_NEUTRAL, 1.0),
        ("GV_STIL", GV_AUFNAHMEBEREITSCHAFT_STIL, GV_AUFNAHMEBEREITSCHAFT_STIL_NEUTRAL, 1.0),
        ("FASZ_INTENT", FASZ_INTENT_FAKTOREN, FASZ_INTENT_NEUTRAL, 1.000),
        ("FASZ_MODUS", FASZ_MODUS_FAKTOREN, FASZ_MODUS_NEUTRAL, 1.020),
    )

    # Die Tabellen mit einem Eintrag `neutral` — als Literal, damit ein
    # verschwundener Eintrag rot wird und nicht still aufs Mittel faellt.
    WITH_NEUTRAL_ENTRY: frozenset[str] = frozenset({"EI_DYNAMIK", "GV_DYNAMIK", "GV_STIL"})

    def test_every_table_of_a_canon_field_is_covered(self) -> None:
        """Ein Fall je Tabelle des Vollstaendigkeitszeugen — keiner fehlt."""
        self.assertEqual(len(TABLE_NEUTRAL), len(self.CASES))

    def test_the_neutral_lies_below_the_maximum(self) -> None:
        for name, tabelle, neutral, _ in self.CASES:
            with self.subTest(tabelle=name):
                self.assertLess(neutral, max(tabelle.values()))

    def test_the_neutral_lies_not_below_the_minimum(self) -> None:
        for name, tabelle, neutral, _ in self.CASES:
            with self.subTest(tabelle=name):
                self.assertGreaterEqual(neutral, min(tabelle.values()))

    def test_the_neutral_entry_is_where_the_literal_says(self) -> None:
        for name, tabelle, _, _ in self.CASES:
            with self.subTest(tabelle=name):
                self.assertEqual(name in self.WITH_NEUTRAL_ENTRY, "neutral" in tabelle)

    def test_the_neutral_is_the_literal_by_the_criterion(self) -> None:
        for name, tabelle, neutral, erwartet in self.CASES:
            with self.subTest(tabelle=name):
                self.assertEqual(erwartet, neutral)
                if "neutral" in tabelle:
                    self.assertEqual(erwartet, tabelle["neutral"])
                else:
                    mittel: float = sum(tabelle.values()) / len(tabelle)
                    self.assertAlmostEqual(erwartet, mittel, delta=0.0005)


def _redis() -> MagicMock:
    """Ein Redis, das keine Nachbarn kennt."""
    client = MagicMock()
    client.keys.return_value = []
    return client


def _salience(modus: str, intentionen: list[str]) -> dict:
    """Eine Bewertung der Salienz ueber dem Auftragstor."""
    return {
        "salienz": 0.95, "themen": ["Neutronensterne"], "dimension": "wissen",
        "zusammenfassung": "Ein synthetischer Eintrag.", "emotion": "neugierig",
        "modus": modus, "intentionen": intentionen,
    }


class KzgStoreWritesOnlyCanonValuesTest(unittest.TestCase):
    """`memory/kzg.py::kzg_store` — Hash und Auftrag."""

    def _store(self, modus: str, intentionen: list[str]) -> tuple[dict, MagicMock, list]:
        rc = _redis()
        with patch("memory.kzg.shadow_queue_push") as push, \
             patch("memory.kzg.promotion_queue_push"), \
             patch("memory.kzg.log_db_write"), \
             patch("memory.kzg.PIXIE_AKTIV", True), \
             self.assertLogs("ki_server.memory.kzg", "INFO") as log:
            kzg_store(
                redis_client=rc, user_id="zeuge", character_id="nova", beobachter="user",
                salienz_obj=_salience(modus, intentionen), embedding=[0.0] * 768,
                turn_id="t-kanon",
            )
        return rc.hset.call_args_list[0].kwargs["mapping"], push, _errors(log.records)

    def test_a_foreign_mode_goes_in_empty(self) -> None:
        mapping, push, errors = self._store(FOREIGN_MODE, CANON_INTENTIONS)
        self.assertEqual("", mapping["modus"])
        self.assertEqual("", push.call_args.kwargs["modus"])
        self.assertEqual(1, len(_lines_naming(errors, "modus", FOREIGN_MODE)))

    def test_only_the_foreign_intention_is_dropped(self) -> None:
        mapping, push, errors = self._store("fachgespraech", FOREIGN_INTENTIONS)
        self.assertEqual(["reflexion"], json.loads(mapping["intentionen"]))
        self.assertEqual(["reflexion"], push.call_args.kwargs["intentionen"])
        self.assertEqual(
            1, len(_lines_naming(errors, "intentionen", "philosophischer_austausch")),
        )

    def test_canon_values_go_in_unchanged(self) -> None:
        """Zwilling: kein Wert faellt weg, keine Fehlerzeile."""
        mapping, push, errors = self._store("fachgespraech", CANON_INTENTIONS)
        self.assertEqual("fachgespraech", mapping["modus"])
        self.assertEqual(CANON_INTENTIONS, json.loads(mapping["intentionen"]))
        self.assertEqual(CANON_INTENTIONS, push.call_args.kwargs["intentionen"])
        self.assertEqual([], errors)


class KzgAgentWritesOnlyCanonValuesTest(unittest.TestCase):
    """`agents/kzg/speicher.py::_neu_anlegen` — der Hash des Agenten-Pfads."""

    def _store(self, modus: str, intentionen: list[str]) -> tuple[dict, list]:
        rc = MagicMock()
        with patch("agents.kzg.speicher.log_db_write"), \
             self.assertLogs("ki_server.agents.kzg.speicher", "INFO") as log:
            speicher._neu_anlegen(
                rc, "zeuge", "nova", "user", _salience(modus, intentionen),
                "Kern.", [0.1, 0.2], 0.95, turn_id="t-kanon",
            )
        return rc.hset.call_args.kwargs["mapping"], _errors(log.records)

    def test_foreign_values_are_refused(self) -> None:
        mapping, errors = self._store(FOREIGN_MODE, FOREIGN_INTENTIONS)
        self.assertEqual("", mapping["modus"])
        self.assertEqual(["reflexion"], json.loads(mapping["intentionen"]))
        self.assertEqual(1, len(_lines_naming(errors, "modus", FOREIGN_MODE)))
        self.assertEqual(
            1, len(_lines_naming(errors, "intentionen", "philosophischer_austausch")),
        )

    def test_canon_values_go_in_unchanged(self) -> None:
        mapping, errors = self._store("fachgespraech", CANON_INTENTIONS)
        self.assertEqual("fachgespraech", mapping["modus"])
        self.assertEqual(CANON_INTENTIONS, json.loads(mapping["intentionen"]))
        self.assertEqual([], errors)


class KzgQueueOrdersOnlyCanonValuesTest(unittest.TestCase):
    """`agents/kzg/queues.py::queues_befuellen` — der Auftrag aus dem Eintrag."""

    def _fill(self, modus: str, intentionen: list[str]) -> tuple[MagicMock, list]:
        zustand: dict = {
            "parameter": {
                "salienz_obj": _salience(modus, intentionen),
                "speicher_status": "neu", "neue_salienz": 0.99, "kzg_key": "kzg:zeuge:nova:1",
                "kzg_themen_str": "Neutronensterne", "kzg_dimension": "wissen", "kern": "Kern.",
            },
            "kontext": {"user_id": "zeuge", "character_id": "nova", "turn_id": "t-kanon"},
            "schritte": [],
        }
        with patch.object(queues, "PIXIE_AKTIV", True), \
             patch.object(queues, "redis_client"), \
             patch.object(queues, "promotion_queue_push", return_value=True), \
             patch.object(queues, "shadow_queue_push") as push, \
             self.assertLogs("ki_server.agents.kzg.queues", "INFO") as log:
            queues.queues_befuellen(zustand)
        return push, _errors(log.records)

    def test_foreign_values_are_refused(self) -> None:
        push, errors = self._fill(FOREIGN_MODE, FOREIGN_INTENTIONS)
        self.assertEqual("", push.call_args.kwargs["modus"])
        self.assertEqual(["reflexion"], push.call_args.kwargs["intentionen"])
        self.assertEqual(2, len(errors), errors)

    def test_canon_values_go_in_unchanged(self) -> None:
        push, errors = self._fill("fachgespraech", CANON_INTENTIONS)
        self.assertEqual("fachgespraech", push.call_args.kwargs["modus"])
        self.assertEqual(CANON_INTENTIONS, push.call_args.kwargs["intentionen"])
        self.assertEqual([], errors)


class CanonCheckEdgesTest(unittest.TestCase):
    """`_kanon_felder_pruefen` — die Raender, die der Schreibweg nicht zeigt."""

    def test_an_empty_mode_is_no_error(self) -> None:
        """Leer ist der erlaubte Wert, kein Freitext."""
        with self.assertLogs("ki_server.memory.kzg", "DEBUG") as log:
            logging.getLogger("ki_server.memory.kzg").debug("Zeuge: Mitschnitt offen")
            modus, intentionen = _kanon_felder_pruefen({"modus": "", "intentionen": []}, "Zeuge")
        self.assertEqual(("", []), (modus, intentionen))
        self.assertEqual([], _errors(log.records))

    def test_intentions_that_are_no_list_are_dropped_loudly(self) -> None:
        with self.assertLogs("ki_server.memory.kzg", "ERROR"):
            _, intentionen = _kanon_felder_pruefen({"intentionen": "reflexion"}, "Zeuge")
        self.assertEqual([], intentionen)


# Die drei Kopien der Pruefung, je mit dem Logger ihres Moduls.
COPIES: tuple[tuple[str, Callable[[dict, str], tuple[str, list[str]]], str], ...] = (
    ("memory.kzg", _kanon_felder_pruefen, "ki_server.memory.kzg"),
    ("agents.kzg.speicher", speicher._kanon_felder_pruefen, "ki_server.agents.kzg.speicher"),
    ("agents.kzg.queues", queues._kanon_felder_pruefen, "ki_server.agents.kzg.queues"),
)


class TheThreeCopiesAgreeTest(unittest.TestCase):
    """Die drei Kopien von `_kanon_felder_pruefen` — dieselbe Eingabe, dieselbe Antwort.

    Je Kopie: dieselbe Rueckgabe, jede Zeile ab WARNING ist ein ERROR, und
    jede erwartete Zeile nennt Feld und Wert. Die Erwartung steht als Literal
    und nicht als Vergleich der Kopien untereinander — sonst bliebe ein
    Fehler gruen, den alle drei teilen.
    """

    def _agree(
        self, eingabe: dict, rueckgabe: tuple[str, list[str]], zeilen: list[tuple[str, str]],
    ) -> None:
        for name, pruefen, logger_name in COPIES:
            with self.subTest(kopie=name):
                with self.assertLogs(logger_name, "DEBUG") as log:
                    logging.getLogger(logger_name).debug("Zeuge: Mitschnitt offen")
                    ergebnis: tuple[str, list[str]] = pruefen(dict(eingabe), "Zeuge")
                self.assertEqual(rueckgabe, ergebnis)
                gemeldet: list[logging.LogRecord] = [
                    r for r in log.records if r.levelno >= logging.WARNING
                ]
                texte: list[str] = [r.getMessage() for r in gemeldet]
                self.assertEqual(
                    [logging.ERROR] * len(zeilen), [r.levelno for r in gemeldet], texte,
                )
                for feld, wert in zeilen:
                    self.assertEqual(1, len(_lines_naming(texte, feld, wert)), texte)

    def test_a_foreign_value(self) -> None:
        self._agree(
            {"modus": FOREIGN_MODE, "intentionen": FOREIGN_INTENTIONS},
            ("", ["reflexion"]),
            [("modus", FOREIGN_MODE), ("intentionen", "philosophischer_austausch")],
        )

    def test_a_canon_value(self) -> None:
        """Zwilling: kein Wert faellt weg, keine Zeile."""
        self._agree(
            {"modus": "fachgespraech", "intentionen": CANON_INTENTIONS},
            ("fachgespraech", CANON_INTENTIONS),
            [],
        )

    def test_an_empty_mode(self) -> None:
        """Leer ist der erlaubte Wert, kein Freitext — keine Zeile."""
        self._agree({"modus": "", "intentionen": []}, ("", []), [])

    def test_intentions_that_are_no_list(self) -> None:
        self._agree({"intentionen": "reflexion"}, ("", []), [("intentionen", "reflexion")])


# ── Vollstaendigkeit ────────────────────────────
_VIOLATION: re.Pattern[str] = re.compile(
    r"\b(" + "|".join(TABLE_NEUTRAL) + r")\s*(?:\.get\s*\(|\[)"
)
# Die drei Pruefungen und die Stelle ihres Tabellen-Arguments; der neutrale
# Faktor folgt direkt dahinter. `_aus_tabelle` nimmt den Wert zuerst.
CHECKS: dict[str, int] = {"_ei_faktor_lesen": 0, "_neugier_faktor_lesen": 0, "_aus_tabelle": 1}
NEUTRALS: frozenset[str] = frozenset(TABLE_NEUTRAL.values())


def _sources() -> dict[str, str]:
    """Die Quelltexte unter `server/` ohne die Zeugen und ohne `config.py`."""
    quellen: dict[str, str] = {}
    for pfad in SERVER.rglob("*.py"):
        if "tests" in pfad.relative_to(SERVER).parts or pfad.name == "config.py":
            continue
        quellen[str(pfad.relative_to(SERVER))] = pfad.read_text(encoding="utf-8")
    return quellen


def _call_name(aufruf: ast.Call) -> str:
    """Der Name der gerufenen Funktion, ob als Name oder als Attribut."""
    if isinstance(aufruf.func, ast.Name):
        return aufruf.func.id
    if isinstance(aufruf.func, ast.Attribute):
        return aufruf.func.attr
    return ""


def _arg_name(aufruf: ast.Call, stelle: int) -> str:
    """Der Name des Positionsarguments an `stelle`, leer fuer alles andere."""
    if stelle < len(aufruf.args) and isinstance(aufruf.args[stelle], ast.Name):
        return aufruf.args[stelle].id
    return ""


def _check_calls(text: str) -> tuple[int, int]:
    """Zaehlt die Aufrufe der drei Pruefungen: die mit falschem Paar und die mit richtigem.

    Gezaehlt wird ein Aufruf, der eine Tabelle oder einen neutralen Faktor
    eines Kanon-Felds traegt; alle anderen Aufrufe bleiben aussen vor.
    """
    if not any(f"{name}(" in text for name in CHECKS):
        return 0, 0
    falsch: int = 0
    richtig: int = 0
    for knoten in ast.walk(ast.parse(text)):
        if not isinstance(knoten, ast.Call) or _call_name(knoten) not in CHECKS:
            continue
        stelle: int = CHECKS[_call_name(knoten)]
        tabelle: str = _arg_name(knoten, stelle)
        neutral: str = _arg_name(knoten, stelle + 1)
        if tabelle not in TABLE_NEUTRAL and neutral not in NEUTRALS:
            continue
        if TABLE_NEUTRAL.get(tabelle) == neutral:
            richtig += 1
        else:
            falsch += 1
    return falsch, richtig


def _places(text: str) -> tuple[int, int]:
    """Zaehlt in einem Quelltext die ungeprueften und die geprueften Leser der Tabellen."""
    falsch, richtig = _check_calls(text)
    return len(_VIOLATION.findall(text)) + falsch, richtig


class EveryReaderUsesTheCheckTest(unittest.TestCase):
    """Jede Stelle unter `server/`, die eine dieser Tabellen liest, nutzt die Pruefung.

    Ungeprueft ist ein Zugriff `TABELLE.get(` oder `TABELLE[` (gesucht nach
    Wort) und ein Aufruf einer der drei Pruefungen, der eine Tabelle mit dem
    neutralen Faktor einer anderen paart. Geprueft ist ein Aufruf mit dem
    richtigen Paar (gesucht im Syntaxbaum, Importzeilen zaehlen nicht); ihre
    Zahl je Datei steht genau.

    Grenze: Ein Leser ueber einen Alias (`tab = GV_AUFNAHMEBEREITSCHAFT_STIL;
    tab.get(stil, 1.0)`) oder ueber einen Import unter anderem Namen bleibt
    unsichtbar — die Suche kennt nur die Namen der Tabellen selbst.
    """

    def test_the_search_finds_a_violation(self) -> None:
        """Verstoss als Text — sonst bliebe die Suche bei jedem Muster gruen."""
        self.assertEqual((1, 0), _places("f = EI_INTENT_FAKTOREN.get(intent, 1.0)"))

    def test_the_search_accepts_the_check(self) -> None:
        """Zwilling als Text."""
        self.assertEqual(
            (0, 1),
            _places('f = _ei_faktor_lesen(EI_INTENT_FAKTOREN, EI_INTENT_NEUTRAL, intent, "x")'),
        )

    def test_the_search_finds_the_neutral_of_another_table(self) -> None:
        """Verstoss als Text: die Modus-Tabelle mit dem neutralen Faktor des Stils."""
        self.assertEqual((1, 0), _places(
            "m = _neugier_faktor_lesen(GV_AUFNAHMEBEREITSCHAFT_MODUS,"
            " GV_AUFNAHMEBEREITSCHAFT_STIL_NEUTRAL, modus, 'modus')"
        ))

    def test_the_search_reads_the_value_first_in_the_fascination(self) -> None:
        """Zwilling als Text: `_aus_tabelle` traegt das Paar an zweiter Stelle."""
        self.assertEqual((0, 1), _places(
            "f = _aus_tabelle(mode, FASZ_MODUS_FAKTOREN, FASZ_MODUS_NEUTRAL, 'mode')"
        ))

    def test_the_search_skips_the_imports(self) -> None:
        """Ein Importblock nennt Tabelle und neutralen Faktor nebeneinander — kein Leser."""
        self.assertEqual((0, 0), _places(
            "from config import (\n    EI_DYNAMIK_FAKTOREN,\n    EI_DYNAMIK_NEUTRAL,\n)"
        ))

    def test_no_reader_goes_around_the_check(self) -> None:
        verstoesse: list[str] = [pfad for pfad, text in _sources().items() if _places(text)[0]]
        self.assertEqual([], verstoesse)

    def test_the_search_finds_the_known_readers(self) -> None:
        """Genau: drei im EI-Gate, drei in der Neugier, zwei in der Faszination."""
        gefunden: dict[str, int] = {}
        for pfad, text in _sources().items():
            richtig: int = _places(text)[1]
            if richtig:
                gefunden[pfad] = richtig
        self.assertEqual(
            {"ei/berechnung.py": 3, "ei/neugier.py": 3, "ei/fascination.py": 2}, gefunden,
        )


# ── Schreibseite ────────────────────────────────
# Die Felder, die nur als Kanon-Werte in den KZG gehen.
WRITTEN_FIELDS: frozenset[str] = frozenset({"modus", "intentionen"})


def _own_nodes(funktion: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[ast.AST]:
    """Die Knoten einer Funktion ohne die ihrer inneren Funktionen."""
    stapel: list[ast.AST] = list(ast.iter_child_nodes(funktion))
    while stapel:
        knoten: ast.AST = stapel.pop()
        if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        yield knoten
        stapel.extend(ast.iter_child_nodes(knoten))


def _checked_names(knoten: list[ast.AST]) -> set[str]:
    """Die Namen, die eine Funktion aus `_kanon_felder_pruefen(...)` bindet."""
    namen: set[str] = set()
    for zuweisung in knoten:
        if not isinstance(zuweisung, ast.Assign) or not isinstance(zuweisung.value, ast.Call):
            continue
        if _call_name(zuweisung.value) != "_kanon_felder_pruefen":
            continue
        for ziel in zuweisung.targets:
            elemente: list[ast.expr] = ziel.elts if isinstance(ziel, ast.Tuple) else [ziel]
            namen.update(e.id for e in elemente if isinstance(e, ast.Name))
    return namen


def _written_values(knoten: list[ast.AST]) -> list[ast.expr]:
    """Die Werte, die eine Funktion als `modus` oder `intentionen` schreibt.

    In den Hash: ein Schluessel im Mapping einer Funktion, die `hset` ruft.
    In den Schatten-Auftrag: ein Schluesselwort von `shadow_queue_push`.
    """
    schreibt_hash: bool = any(
        isinstance(k, ast.Call) and _call_name(k) == "hset" for k in knoten
    )
    werte: list[ast.expr] = []
    for k in knoten:
        if schreibt_hash and isinstance(k, ast.Dict):
            werte += [
                wert for schluessel, wert in zip(k.keys, k.values, strict=True)
                if isinstance(schluessel, ast.Constant) and schluessel.value in WRITTEN_FIELDS
            ]
        if isinstance(k, ast.Call) and _call_name(k) == "shadow_queue_push":
            werte += [kw.value for kw in k.keywords if kw.arg in WRITTEN_FIELDS]
    return werte


def _is_checked(wert: ast.expr, geprueft: set[str]) -> bool:
    """Ein Wert aus der Pruefung: ihr Name, auch in `json.dumps(...)`."""
    if isinstance(wert, ast.Call) and _call_name(wert) == "dumps" and len(wert.args) == 1:
        wert = wert.args[0]
    return isinstance(wert, ast.Name) and wert.id in geprueft


def _writes(text: str) -> tuple[int, int]:
    """Zaehlt die Schreibstellen der beiden Felder: die mit Rohwert und die mit geprueftem Wert.

    Gezaehlt wird nur in Funktionen, die `salienz_obj` lesen.
    """
    if "salienz_obj" not in text:
        return 0, 0
    roh: int = 0
    geprueft: int = 0
    for funktion in ast.walk(ast.parse(text)):
        if not isinstance(funktion, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        knoten: list[ast.AST] = list(_own_nodes(funktion))
        if not any(isinstance(k, ast.Name) and k.id == "salienz_obj" for k in knoten):
            continue
        namen: set[str] = _checked_names(knoten)
        for wert in _written_values(knoten):
            if _is_checked(wert, namen):
                geprueft += 1
            else:
                roh += 1
    return roh, geprueft


_RAW_WRITER: str = """
def f(rc, salienz_obj):
    rc.hset("k", mapping={"modus": salienz_obj.get("modus", "")})
"""
_RAW_BESIDE_THE_CHECK: str = """
def f(rc, salienz_obj):
    modus, intentionen = _kanon_felder_pruefen(salienz_obj, "x")
    rc.hset("k", mapping={"modus": modus})
    rc.hset("n", mapping={"modus": salienz_obj["modus"]})
"""
_RAW_ORDER: str = """
def f(rc, salienz_obj):
    shadow_queue_push(rc, "u", "a", intentionen=salienz_obj["intentionen"])
"""
_CHECKED_WRITER: str = """
def f(rc, salienz_obj):
    modus, intentionen = _kanon_felder_pruefen(salienz_obj, "x")
    rc.hset("k", mapping={"modus": modus, "intentionen": json.dumps(intentionen)})
    shadow_queue_push(rc, "u", "a", modus=modus, intentionen=intentionen)
"""


class EveryWriterUsesTheCheckTest(unittest.TestCase):
    """Jeder Schreiber von `modus` und `intentionen` in den KZG nutzt die Pruefung.

    Ein Schreiber ist eine Funktion unter `server/`, die `salienz_obj` liest
    und eines der beiden Felder in ein Hash-Mapping (`hset`) oder in einen
    Schatten-Auftrag (`shadow_queue_push`) schreibt. Geprueft ist ein Wert,
    den dieselbe Funktion aus `_kanon_felder_pruefen(...)` bindet (auch in
    `json.dumps`); jeder andere ist ein Rohwert — auch dann, wenn die
    Pruefung in derselben Funktion steht. Die Zahl je Datei steht genau.

    Grenze: Die Suche sieht nur das Mapping-Literal und das Schluesselwort.
    Unsichtbar bleiben die Feld/Wert-Form (`hset(key, "modus", wert)`), die
    Zuweisung ins Mapping (`mapping["modus"] = wert`), eine Salienz unter
    anderem Namen als `salienz_obj` und eine Hilfsfunktion, die das Mapping
    ohne `hset` baut; ebenso ein positionaler Wert in `shadow_queue_push`.
    Ein neu gebundener Pruefname faellt nur der genauen Zahl auf. Heute
    steht keine dieser Formen im Baum: Von den `hset`-Aufrufen unter
    `server/` schreiben nur zwei die Felder, beide als Mapping-Literal.
    """

    def test_the_search_finds_a_raw_writer(self) -> None:
        """Verstoss als Text — ohne Pruefung."""
        self.assertEqual((1, 0), _writes(_RAW_WRITER))

    def test_the_search_finds_a_raw_writer_beside_the_check(self) -> None:
        """Verstoss als Text — die Pruefung steht da, der zweite Hash bekommt den Rohwert."""
        self.assertEqual((1, 1), _writes(_RAW_BESIDE_THE_CHECK))

    def test_the_search_finds_a_raw_order(self) -> None:
        """Verstoss als Text — der Schatten-Auftrag."""
        self.assertEqual((1, 0), _writes(_RAW_ORDER))

    def test_the_search_accepts_the_check(self) -> None:
        """Zwilling als Text: Hash und Auftrag mit den geprueften Werten."""
        self.assertEqual((0, 4), _writes(_CHECKED_WRITER))

    def test_no_writer_goes_around_the_check(self) -> None:
        verstoesse: list[str] = [pfad for pfad, text in _sources().items() if _writes(text)[0]]
        self.assertEqual([], verstoesse)

    def test_the_search_finds_the_known_writers(self) -> None:
        """Genau: Hash und Auftrag im Store, der Hash des Agenten, der Auftrag des Agenten."""
        gefunden: dict[str, int] = {}
        for pfad, text in _sources().items():
            geprueft: int = _writes(text)[1]
            if geprueft:
                gefunden[pfad] = geprueft
        self.assertEqual(
            {"memory/kzg.py": 4, "agents/kzg/speicher.py": 2, "agents/kzg/queues.py": 2},
            gefunden,
        )


if __name__ == "__main__":
    unittest.main()
