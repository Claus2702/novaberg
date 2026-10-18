"""Tests fuer die Deutung einer Antwort am Tor der Notizen (`agents/notizen/resume.py`).

Die Zusicherungen:

  1. **Eine Ablehnung wird nie zur Zustimmung.** Traegt die Antwort beide
     Seiten (*„nein, bitte nicht“*), gewinnt die Ablehnung, und es wird
     nichts angelegt.
  2. **Eine Zustimmung oder Wahl zaehlt nur als ganzes Wort.** *erneut* ist
     nicht *neu*, *11 Uhr* ist nicht die Wahl 1, *Jahr* ist nicht *ja*.
     Die Ablehnung sucht ihre Staemme (`REFUSAL_STEMS`) dagegen auch mitten
     im Wort (*keinesfalls*, *ablehnen*), im Text ohne die Zustimmungswoerter
     (`CONSENT_WORDS`): `"ne"` in *gerne* lehnt nicht ab, jedes andere schon.
  3. **Was keine Seite trifft, fuehrt zur erneuten Frage**, nie zum Schreiben.

Kein Zeuge oeffnet eine Datenbank oder ein Netz: Die Deutung schreibt nicht,
sie gibt nur den naechsten Zustand zurueck.
"""

import json
import re
import unittest

from agents.notizen.resume import (
    CONSENT_WORDS,
    REFUSAL_STEMS,
    _candidate_keys,
    _has_stem,
    _has_word,
    _resume_disambiguierung,
    _resume_duplikat,
    _resume_nicht_gefunden,
    _without_words,
    resume,
)

# Je Ablehnungsstamm Antworten, die ihn tragen, jede mit einem
# Zustimmungswort daneben — auch Formen, in denen er nur mitten im Wort steht.
_FORMS_BY_STEM: dict[str, tuple[str, ...]] = {
    "nein": ("nein danke, ok", "ok, neinnein"),
    "ne": (
        "bitte ablehnen", "ok, ich lehne ab", "bitte ohne mich", "ja ne danke",
        "ja, leg ne neue an",
    ),
    "nee": ("ok, neee", "bitte nee"),
    "nicht": ("bitte nicht", "bitte nichts ändern", "ok, mitnichten"),
    "kein": ("bitte keinesfalls", "ok, keineswegs", "bitte keine Änderung"),
    "lass": ("ja, lass das", "ok, lasst das", "bitte lasse es"),
    "abbruch": ("ok, abbruch", "ja, Abbruch bitte"),
    "abbrech": ("ok, abbrechen", "bitte abbrechen"),
    "stopp": ("ok, stoppt das", "bitte stoppen"),
    "stop": ("ok, stop", "bitte stop"),
}

# Antwortformen, an denen die Deutung schon einmal falsch lag oder gemessen
# wurde — Zustimmung, Ablehnung und beides in einer Antwort.
_KNOWN_FORMS: tuple[str, ...] = (
    "ja, gerne", "gerne", "meinetwegen", "ja bitte", "ok, meinetwegen",
    "ja, leg ne neue an", "leg 'ne neue an", "ja, ne neue", "ne, lass mal", "ja ne",
    "ja ne danke", "ja, ne, danke", "nene, ich mach das selber",
    "bitte ablehnen", "ok, ablehnen", "ok, ich lehne ab", "ablehnen, bitte",
    "bitte ohne mich", "ok, lieber eine neue",
    "bitte nichts ändern", "ok, lieber nichts", "nichts übernehmen, danke, ok",
    "bitte nichts anlegen", "nichts dagegen", "nein, bitte nicht",
    "bitte keine Änderung", "bitte auf keinen Fall", "keine Ahnung",
    "bitte keinesfalls", "ok, keineswegs", "bitte keinesfalls anlegen", "nein, keine neue",
    "ja, lass das", "ok, abbrechen",
)

_NOT_FOUND: dict = {
    "typ": "nicht_gefunden",
    "agent": "notizen",
    "aktion": "add_content",
    "target": "Einkauf",
    "original_aufgabe": "Schreib Milch auf die Einkaufsliste",
}

_TWO_CANDIDATES: dict = {
    "typ": "disambiguierung",
    "agent": "notizen",
    "aktion": "read",
    "kandidaten": [{"id": 7, "name": "Einkauf"}, {"id": 8, "name": "Urlaub"}],
}


def _state(**parameter: object) -> dict:
    """Ein Zustand mit leerem Audit-Pfad und den gegebenen Parametern."""
    return {"parameter": dict(parameter), "schritte": []}


def _not_found(answer: str) -> dict:
    """Die Antwort auf *„Die Notiz gibt es nicht — soll ich sie anlegen?“*."""
    return _resume_nicht_gefunden(_state(), dict(_NOT_FOUND), answer)


def _without_stem_word(answer: str, stem: str) -> str:
    """Die Antwort ohne das Wort, das den Stamm traegt — es bleibt die Zustimmung."""
    return re.sub(rf"\w*{re.escape(stem)}\w*", "", answer.lower())


def _head_refuses(text: str) -> bool:
    """Das alte Verfahren: ein Stamm irgendwo im ganzen Text lehnt ab."""
    return any(stem in text for stem in REFUSAL_STEMS)


def _stem_outside_consent(text: str) -> bool:
    """Steht ein Stamm noch da, wenn die Zustimmungswoerter als ganze Woerter fehlen?"""
    rest: str = text
    for word in CONSENT_WORDS:
        rest = re.sub(rf"(?<!\w){re.escape(word)}(?!\w)", " ", rest)
    return any(stem in rest for stem in REFUSAL_STEMS)


class NotFoundConsentTest(unittest.TestCase):
    """Die Frage, ob eine fehlende Notiz angelegt wird — die schreibende Seite."""

    def test_consent_creates(self) -> None:
        """Zustimmungen fuehren zum Anlegen — auch die mit 'ne' im Wort."""
        for answer in ("ja, gerne", "gerne", "meinetwegen", "ja bitte", "na klar", "ok"):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "laufend")
                self.assertEqual(result["parameter"]["action"], "create")

    def test_refusal_creates_nothing(self) -> None:
        """Ablehnungen enden ohne Anlegen — auch wenn ein Zustimmungswort darin steht."""
        for answer in (
            "nein", "ne", "nee", "nein, bitte nicht", "lieber nicht", "mach das nicht",
        ):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertNotIn("parameter", result)

    def test_every_ne_refuses_also_as_article(self) -> None:
        """'ne' ausserhalb eines Zustimmungsworts lehnt ab — auch als Artikel.

        Hier stand *„ja, leg ne neue an“* als Anlegen, weil `ne` zwischen
        zwei Woertern als Artikel galt. Welches `ne` einen Wunsch ablehnt,
        ist an der Stelle nicht zu erkennen; es gilt die sichere Richtung.
        """
        for answer in (
            "ne", "Ne.", "ne, lass mal", "ja ne", "ja, ne.", "ja ne danke",
            "ja, leg ne neue an",
        ):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertNotIn("parameter", result)

    def test_ne_inside_a_refusing_word_refuses_next_to_a_consent_word(self) -> None:
        """'ablehnen', 'lehne' und 'ohne' tragen 'ne' — neben 'bitte' oder 'ok' lehnen sie ab."""
        for answer in (
            "bitte ablehnen", "ok, ablehnen", "ok, ich lehne ab", "ablehnen, bitte",
            "bitte ohne mich",
        ):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertNotIn("parameter", result)

    def test_nichts_and_kein_refuse_next_to_a_consent_word(self) -> None:
        """'bitte nichts anlegen' traegt 'bitte' — es wird trotzdem nichts angelegt."""
        for answer in (
            "bitte nichts ändern", "ok, lieber nichts", "bitte nichts anlegen",
            "bitte keine Änderung", "bitte auf keinen Fall", "keine Ahnung",
            "bitte keinesfalls", "nein, bitte nicht",
        ):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertNotIn("parameter", result)
        for answer in ("ja, gerne", "meinetwegen"):
            with self.subTest(answer=answer):
                result = _not_found(answer)
                self.assertEqual(result["status"], "laufend")
                self.assertEqual(result["parameter"]["action"], "create")

    def test_every_refusal_stem_refuses_next_to_a_consent_word(self) -> None:
        """Jeder Stamm lehnt ab, auch mitten im Wort und neben 'bitte' oder 'ok'.

        Ohne das Wort mit dem Stamm legt dieselbe Antwort an — so ist belegt,
        dass die Ablehnung am Stamm haengt und nicht an etwas anderem.
        Die Stammliste und die Formen decken sich in beiden Richtungen: Ein
        gestrichener Stamm faellt so ebenso auf wie einer ohne Formen.
        """
        self.assertEqual(set(REFUSAL_STEMS) - set(_FORMS_BY_STEM), set())
        self.assertEqual(set(_FORMS_BY_STEM) - set(REFUSAL_STEMS), set())
        for stem in REFUSAL_STEMS:
            for answer in _FORMS_BY_STEM[stem]:
                with self.subTest(stem=stem, answer=answer):
                    self.assertIn(stem, answer.lower())
                    result: dict = _not_found(answer)
                    self.assertEqual(result["status"], "abgeschlossen")
                    self.assertNotIn("parameter", result)
                    rest: dict = _not_found(_without_stem_word(answer, stem))
                    self.assertEqual(rest["status"], "laufend")

    def test_old_refusal_stays_unless_only_a_consent_word_carried_it(self) -> None:
        """Was das alte Verfahren ablehnte, bleibt Ablehnung — ausser in 'gerne' und 'meinetwegen'.

        Das alte Verfahren ist hier nachgebildet: ein Stamm irgendwo im ganzen
        Text. Steht nach dem Herausnehmen der Zustimmungswoerter noch ein
        Stamm da, wird nichts angelegt; steckte jeder Stamm in einem
        Zustimmungswort, wird angelegt. Beide Faelle muessen vorkommen,
        sonst prueft die Liste die Regel nicht.
        """
        refused: int = 0
        confirmed: int = 0
        for answer in _KNOWN_FORMS:
            text: str = answer.lower()
            if not _head_refuses(text):
                continue
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                if _stem_outside_consent(text):
                    refused += 1
                    self.assertEqual(result["status"], "abgeschlossen")
                    self.assertNotIn("parameter", result)
                else:
                    confirmed += 1
                    self.assertEqual(result["status"], "laufend")
                    self.assertEqual(result["parameter"]["action"], "create")
        self.assertGreater(refused, 0)
        self.assertGreater(confirmed, 0)

    def test_doubled_ne_refuses(self) -> None:
        """'nene' ist nie der Artikel — auch nicht neben 'mach'."""
        for answer in ("nene, ich mach das selber", "ok nene"):
            with self.subTest(answer=answer):
                self.assertEqual(_not_found(answer)["status"], "abgeschlossen")

    def test_word_inside_another_word_is_no_consent(self) -> None:
        """'Jahr' traegt 'ja', 'vielleicht' kein bekanntes Wort — beides fragt erneut.

        'keine Ahnung' stand hier als unklar; seit 'keine' ein Ablehnungswort
        ist, lehnt es ab (die sichere Richtung).
        """
        for answer in ("Jahr", "vielleicht"):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "rueckfrage")
                self.assertEqual(json.loads(result["rueckfrage"])["typ"], "nicht_gefunden")

    def test_resume_routes_the_answer_to_the_gate(self) -> None:
        """Ueber den Einstieg: die Rueckfrage im Zustand fuehrt zur selben Deutung."""
        rueckfrage: str = json.dumps(_NOT_FOUND)
        refused: dict = resume(_state(
            user_answer="nein, bitte nicht", original_rueckfrage=rueckfrage,
        ))
        confirmed: dict = resume(_state(user_answer="ja, gerne", original_rueckfrage=rueckfrage))
        self.assertEqual(refused["status"], "abgeschlossen")
        self.assertEqual(confirmed["status"], "laufend")


class DuplicateTest(unittest.TestCase):
    """Die Frage, ob eine bestehende Notiz aktualisiert oder eine neue angelegt wird."""

    def test_new_creates_a_second_note(self) -> None:
        for answer in ("neu", "eine neue bitte", "leg eine neue an"):
            with self.subTest(answer=answer):
                result: dict = _resume_duplikat(_state(target="Einkauf"), answer)
                self.assertEqual(result["parameter"]["action"], "create")
                self.assertTrue(result["parameter"]["skip_duplikat_check"])

    def test_update_updates(self) -> None:
        for answer in ("aktualisieren", "aktualisiere sie", "überschreiben"):
            with self.subTest(answer=answer):
                result: dict = _resume_duplikat(_state(target="Einkauf"), answer)
                self.assertEqual(result["parameter"]["action"], "update")

    def test_erneut_is_not_neu(self) -> None:
        """'erneut' traegt 'neu' — es fragt erneut statt eine zweite Notiz anzulegen."""
        result: dict = _resume_duplikat(_state(target="Einkauf"), "frag mich erneut")
        self.assertEqual(result["status"], "rueckfrage")
        self.assertNotIn("parameter", result)


class DisambiguationTest(unittest.TestCase):
    """Die Wahl zwischen zwei Notizen."""

    def _choose(self, answer: str, disamb: dict | None = None) -> dict:
        """Die Antwort auf die Auswahl zwischen den Kandidaten."""
        return _resume_disambiguierung(_state(), disamb or _TWO_CANDIDATES, answer)

    def test_number_as_whole_word_chooses(self) -> None:
        for answer, name in (
            ("Nummer 2", "Urlaub"), ("die 1", "Einkauf"), ("die zweite", "Urlaub"),
            ("den unteren", "Urlaub"), ("Urlaub", "Urlaub"),
        ):
            with self.subTest(answer=answer):
                self.assertEqual(self._choose(answer)["parameter"]["notiz"]["name"], name)

    def test_digit_inside_a_number_is_no_choice(self) -> None:
        """'11 Uhr' traegt '1', '2026' traegt '2' — keine Wahl, erneute Frage."""
        for answer in ("um 11 Uhr", "im Jahr 2026"):
            with self.subTest(answer=answer):
                result: dict = self._choose(answer)
                self.assertEqual(result["status"], "rueckfrage")
                self.assertNotIn("parameter", result)

    def test_candidate_without_id_is_not_chosen_by_any_answer(self) -> None:
        """Eine fehlende ID ist der leere Text — und der stand frueher in jeder Antwort."""
        disamb: dict = {**_TWO_CANDIDATES, "kandidaten": [{"name": "Einkauf"}, {"name": "Urlaub"}]}
        self.assertEqual(self._choose("keine Ahnung", disamb)["status"], "rueckfrage")
        self.assertEqual(self._choose("Nummer 2", disamb)["parameter"]["notiz"]["name"], "Urlaub")

    def test_candidate_keys_are_position_and_id(self) -> None:
        """Position ab 1 und die ID; eine fehlende ID bringt keinen leeren Text mit."""
        self.assertEqual(_candidate_keys(0, {"id": 7, "name": "Einkauf"}), ["1", "7"])
        self.assertEqual(_candidate_keys(1, {"name": "Urlaub"}), ["2"])
        with self.assertRaises(ValueError):
            _candidate_keys(-1, {"id": 7})


class HasWordTest(unittest.TestCase):
    """Der Vergleich selbst."""

    def test_whole_word_and_phrase_hit(self) -> None:
        self.assertTrue(_has_word("ja, gerne", ("gerne",)))
        self.assertTrue(_has_word("auf jeden fall", ("auf jeden",)))

    def test_part_of_a_word_does_not_hit(self) -> None:
        self.assertFalse(_has_word("frag erneut", ("neu",)))
        self.assertFalse(_has_word("um 11 uhr", ("1",)))

    def test_name_ending_in_punctuation_hits(self) -> None:
        """Hinter ')' traefe eine Wortgrenze nie — die Umgebung ohne Wortzeichen trifft."""
        self.assertTrue(_has_word("nimm einkauf (alt) bitte", ("einkauf (alt)",)))

    def test_empty_word_is_rejected(self) -> None:
        """Ein leeres Wort traefe an jeder Stelle — es wird abgewiesen."""
        with self.assertRaises(ValueError):
            _has_word("egal", ("",))
        with self.assertRaises(ValueError):
            _has_word("egal", ())


class HasStemTest(unittest.TestCase):
    """Der Stammvergleich: auch mitten im Wort, und ein leerer Stamm ist ein Defekt."""

    def test_stem_inside_a_word_hits(self) -> None:
        self.assertTrue(_has_stem("bitte keinesfalls", ("kein",)))

    def test_text_without_the_stem_does_not_hit(self) -> None:
        """Hier stand *„ja, gerne“*; seit `"ne"` ein Stamm ist, trifft es dort."""
        self.assertFalse(_has_stem("ja, bitte", REFUSAL_STEMS))

    def test_stem_inside_a_consent_word_hits(self) -> None:
        """Der Stammvergleich allein trifft *gerne* — erst das Herausnehmen schuetzt es."""
        self.assertTrue(_has_stem("ja, gerne", REFUSAL_STEMS))
        self.assertFalse(_has_stem(_without_words("ja, gerne", CONSENT_WORDS), REFUSAL_STEMS))

    def test_empty_or_upper_stem_is_rejected(self) -> None:
        """Ein leerer Stamm traefe jede Antwort, ein grossgeschriebener keine."""
        for stems in ((), ("kein", ""), ("Kein",)):
            with self.subTest(stems=stems), self.assertRaises(ValueError):
                _has_stem("egal", stems)

    def test_text_not_lowered_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _has_stem("Keinesfalls", ("kein",))


class WithoutWordsTest(unittest.TestCase):
    """Das Herausnehmen: nur ganze Woerter, und ein leeres Wort ist ein Defekt."""

    def test_whole_words_and_phrases_are_removed(self) -> None:
        self.assertNotIn("gerne", _without_words("ja, gerne", CONSENT_WORDS))
        self.assertNotIn("meinetwegen", _without_words("ok, meinetwegen", CONSENT_WORDS))
        self.assertNotIn("auf jeden", _without_words("auf jeden fall", CONSENT_WORDS))

    def test_parts_of_other_words_stay(self) -> None:
        """'ja' in 'jahr' ist kein Wort, 'ne' neben 'ja' gehoert zu keinem — beides bleibt."""
        self.assertIn("jahr", _without_words("jahr", CONSENT_WORDS))
        self.assertIn("ablehnen", _without_words("bitte ablehnen", CONSENT_WORDS))
        self.assertIn("ne", _without_words("ja ne danke", CONSENT_WORDS))

    def test_empty_word_is_rejected(self) -> None:
        for words in ((), ("ja", "")):
            with self.subTest(words=words), self.assertRaises(ValueError):
                _without_words("egal", words)


if __name__ == "__main__":
    unittest.main()
