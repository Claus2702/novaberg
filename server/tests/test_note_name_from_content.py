"""Tests: Eine Notiz ohne genannten Namen heisst nach ihrem Inhalt, nicht nach der Anweisung.

`NOTIZ-BEFEHL-ALS-TITEL`: Fuer "Notiere dir: ..." lieferte die Kette den Namen
"Neue Notiz" — die Anweisung selbst. Die zweite namenlose Notiz traf denselben
Namen, die Duplikat-Pruefung fragte nach, und es entstand keine Notiz.

Die Saetze sind nachgebildet aus einer Simulation an einem Pruef-Nutzer, nicht
aus einem echten Bestand. Modellantwort und Repository sind ersetzt; kein
Zeuge oeffnet eine Datenbank, ein Netz oder ruft ein Modell.

Zeugen dieser Datei:
  * **CreateTest** — `_create` mit ersetztem Modell und einem Repository im Speicher:
    Meta-Name verworfen, genannter Name und Name aus dem Inhalt bleiben, echte
    Gleichnamigkeit fragt weiter, die Verwerfung steht in genau einer Info-Zeile.
  * **HelperTest** — Beleg, Ableitung, genannte Namen und Faltung einzeln.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.notizen import crud
from memory.repositories.notizen_repository import NotizenRepository
from services.model_services import model_service

CRUD_LOGGER: str = "ki_server.agents.notizen.crud"

SENTENCE_11_TEXT: str = "Der Ersatzschlüssel liegt beim Nachbarn"
SENTENCE_11_NORMALIZED: str = (
    "create: Neue Notiz anlegen mit Inhalt: Der Ersatzschlüssel liegt beim Nachbarn (Typ: notiz)"
)
SENTENCE_12_TEXT: str = "Ich muss noch Druckerpapier kaufen"
SENTENCE_12_NORMALIZED: str = (
    "create: Neue Notiz anlegen mit Inhalt: Ich muss noch Druckerpapier kaufen (Typ: todo)"
)
HARDWARE_STORE_NORMALIZED: str = (
    "create: Neue Notiz 'Baumarkt' anlegen mit Inhalt: Schrauben (Typ: einkauf)"
)


class _Store:
    """Notizen im Speicher, Namensvergleich wie `find_by_stichwort` (lower(name) = lower(%s))."""

    def __init__(self) -> None:
        """Leerer Bestand; Namen in der Reihenfolge ihrer Anlage."""
        self.names: list[str] = []

    def find_by_stichwort(self, _url: str, _user_id: str, keyword: str) -> list[dict]:
        return [{"name": n} for n in self.names if n.lower() == keyword.lower()]

    def insert(self, **fields: object) -> int:
        self.names.append(str(fields["name"]))
        return len(self.names)


def _state(target: str, normalized: str, context: dict | None = None) -> dict:
    """Ein AgentState, wie ihn Dispatch und Klassifikation an `_create` uebergeben."""
    return {
        "aufgabe": "nachgebildete Aeusserung",
        "kontext": {"user_id": "pruef-nutzer", **(context or {})},
        "parameter": {"action": "create", "target": target, "normalisiert": normalized},
        "schritte": [],
    }


def _create_note(store: _Store, state: dict, model_name: str, text: str) -> dict:
    """Fuehrt `_create` mit ersetztem Modell, Repository und Verifikation aus."""
    reply = SimpleNamespace(parsed={"name": model_name, "typ": "notiz", "text": text,
                                    "themen": []})
    find = store.find_by_stichwort
    with patch.object(model_service.chat, "submit_sync", return_value=reply), \
         patch.object(NotizenRepository, "find_by_stichwort", side_effect=find), \
         patch.object(NotizenRepository, "insert", side_effect=store.insert), \
         patch.object(crud, "_verifizieren_notiz", return_value=True):
        return crud._create(state)


class CreateTest(unittest.TestCase):
    """Der Name, den `_create` speichert, je nach Herkunft des Kandidaten."""

    def test_sentence_11_meta_name_is_replaced_by_content(self) -> None:
        store = _Store()
        outcome = _create_note(
            store, _state("", SENTENCE_11_NORMALIZED), "Neue Notiz", SENTENCE_11_TEXT
        )
        self.assertEqual(outcome["status"], "abgeschlossen")
        self.assertEqual(store.names, ["Der Ersatzschlüssel liegt beim Nachbarn"])

    def test_sentences_11_and_12_give_two_names_without_query(self) -> None:
        store = _Store()
        first = _create_note(
            store, _state("", SENTENCE_11_NORMALIZED), "Neue Notiz", SENTENCE_11_TEXT
        )
        # Bei Satz 12 kommt der Meta-Name aus dem Ziel des Klassifikators.
        second = _create_note(
            store, _state("Neue Notiz", SENTENCE_12_NORMALIZED), "Notiz", SENTENCE_12_TEXT
        )
        self.assertEqual([first["status"], second["status"]], ["abgeschlossen", "abgeschlossen"])
        self.assertEqual(len(set(store.names)), 2)
        self.assertNotIn("Neue Notiz", store.names)
        self.assertEqual(store.names[1], "Ich muss noch Druckerpapier kaufen")

    def test_given_name_stays(self) -> None:
        # 'Baumarkt' teilt kein Wort mit dem Inhalt — nur die Nennung haelt ihn.
        store = _Store()
        state = _state("Baumarkt", HARDWARE_STORE_NORMALIZED)
        outcome = _create_note(store, state, "Baumarkt", "Schrauben")
        self.assertEqual(outcome["status"], "abgeschlossen")
        self.assertEqual(store.names, ["Baumarkt"])

    def test_given_name_without_target_stays(self) -> None:
        store = _Store()
        _create_note(store, _state("", HARDWARE_STORE_NORMALIZED), "baumarkt", "Schrauben")
        self.assertEqual(store.names, ["baumarkt"])

    def test_name_from_content_stays(self) -> None:
        store = _Store()
        _create_note(store, _state("", SENTENCE_12_NORMALIZED), "Druckerpapier", SENTENCE_12_TEXT)
        self.assertEqual(store.names, ["Druckerpapier"])

    def test_consented_offer_stays(self) -> None:
        store = _Store()
        context = {"angebot_satz": "Soll ich dir eine Notiz Geschenkideen anlegen?",
                   "objekt_bezug": [{"name": "Geschenkideen"}]}
        _create_note(
            store, _state("Geschenkideen", "", context), "Neue Notiz", "Ein Buch über Vögel"
        )
        self.assertEqual(store.names, ["Geschenkideen"])

    def test_true_duplicate_still_asks_back(self) -> None:
        store = _Store()
        first = _create_note(
            store, _state("Baumarkt", HARDWARE_STORE_NORMALIZED), "Baumarkt", "Schrauben"
        )
        second = _create_note(
            store, _state("Baumarkt", HARDWARE_STORE_NORMALIZED), "Baumarkt", "Dübel"
        )
        self.assertEqual(first["status"], "abgeschlossen")
        self.assertEqual(second["status"], "rueckfrage")
        self.assertIn("'Baumarkt'", second["rueckfrage"])
        self.assertEqual(store.names, ["Baumarkt"])

    def test_rejected_name_logged_with_replacement_in_one_info_line(self) -> None:
        with self.assertLogs(CRUD_LOGGER, level="INFO") as logs:
            _create_note(
                _Store(), _state("", SENTENCE_11_NORMALIZED), "Neue Notiz", SENTENCE_11_TEXT
            )
        rejected = [r for r in logs.records if "verworfen" in r.getMessage()]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0].levelname, "INFO")
        self.assertIn("'Neue Notiz'", rejected[0].getMessage())
        self.assertIn("'Der Ersatzschlüssel liegt beim Nachbarn'", rejected[0].getMessage())

    def test_grounded_name_logs_no_rejection(self) -> None:
        with self.assertLogs(CRUD_LOGGER, level="INFO") as logs:
            _create_note(
                _Store(), _state("", SENTENCE_12_NORMALIZED), "Druckerpapier", SENTENCE_12_TEXT
            )
        self.assertFalse([r for r in logs.records if "verworfen" in r.getMessage()])
        self.assertTrue([r for r in logs.records if "angelegt" in r.getMessage()])


class HelperTest(unittest.TestCase):
    """Beleg, Ableitung, genannte Namen und Faltung einzeln."""

    def test_grounds_named(self) -> None:
        self.assertEqual(crud._name_grounds("Baumarkt", "Schrauben", {"baumarkt"}), "genannt")

    def test_grounds_start_of_content(self) -> None:
        self.assertEqual(crud._name_grounds("Der Ersatzschlüssel", SENTENCE_11_TEXT, set()),
                         "Anfang des Inhalts")

    def test_grounds_content_word_across_umlaut_spelling(self) -> None:
        self.assertEqual(crud._name_grounds("Ersatzschluessel", SENTENCE_11_TEXT, set()),
                         "Inhaltswort 'ersatzschluessel'")

    def test_meta_names_without_grounds(self) -> None:
        for name in ("Neue Notiz", "Notiz", "neue Notiz anlegen"):
            with self.subTest(name=name):
                self.assertEqual(crud._name_grounds(name, SENTENCE_11_TEXT, set()), "")

    def test_short_shared_word_is_no_grounds(self) -> None:
        # 'das' steht im Inhalt, ist aber kein Inhaltswort.
        self.assertEqual(crud._name_grounds("das festhalten", "Wo das Auto steht", set()), "")

    def test_derivation_takes_start_without_punctuation(self) -> None:
        self.assertEqual(crud._derive_name("Der Ersatzschlüssel liegt beim Nachbarn."),
                         "Der Ersatzschlüssel liegt beim Nachbarn")
        self.assertEqual(crud._derive_name("eins zwei drei vier fünf sechs sieben"),
                         "eins zwei drei vier fünf")

    def test_derivation_without_word_is_loudly_empty(self) -> None:
        with self.assertLogs(CRUD_LOGGER, level="ERROR"):
            self.assertEqual(crud._derive_name("..."), "")

    def test_named_names_from_quotes_and_consent(self) -> None:
        context = {"angebot_satz": "Soll ich?", "objekt_bezug": [{"name": "Geschenkideen"}]}
        self.assertEqual(crud._named_names("add_content: Milch zu Notiz 'Einkaufsliste'", context),
                         {"Einkaufsliste", "Geschenkideen"})
        self.assertEqual(crud._named_names("create: Neue Notiz anlegen mit Inhalt: x", {}), set())

    def test_named_names_wrong_type_is_loudly_empty(self) -> None:
        with self.assertLogs(CRUD_LOGGER, level="ERROR"):
            self.assertEqual(crud._named_names(None, {}), set())  # type: ignore[arg-type]

    def test_fold_words(self) -> None:
        self.assertEqual(crud._fold_words("Größe, Übung!"), ["groesse", "uebung"])
        with self.assertLogs(CRUD_LOGGER, level="ERROR"):
            self.assertEqual(crud._fold_words(None), [])  # type: ignore[arg-type]

    def test_without_candidate_name_comes_from_content(self) -> None:
        with self.assertLogs(CRUD_LOGGER, level="INFO") as logs:
            self.assertEqual(crud._resolve_name(["", "  "], SENTENCE_12_TEXT, set()),
                             SENTENCE_12_TEXT)
        self.assertEqual(len(logs.records), 1)
        self.assertIn("kein Name geliefert", logs.records[0].getMessage())

    def test_without_content_no_name(self) -> None:
        self.assertEqual(crud._resolve_name(["Neue Notiz"], "   ", set()), "")


if __name__ == "__main__":
    unittest.main()
