"""Unit-Test fuer _standard_interpretieren (Phase 0).

Scope: Nur die Keyword-Klassifikation der User-Antwort.
Routing, Strategy-Hook und End-to-End-Flow sind NICHT abgedeckt
(kommt mit Phase 1).

Die Ablehnung sucht ihre Staemme (`REFUSAL_STEMS`) auch mitten im Wort —
*keinesfalls*, *mitnichten*, *abbrechen*, *ablehnen*, *ohne* lehnen ab, und
*vernichten* ebenso (die sichere Richtung). Gesucht wird im Text ohne die
Zustimmungswoerter (`CONSENT_WORDS`): `"ne"` in *gerne* und *meinetwegen*
lehnt nicht ab, jedes andere `"ne"` schon, auch der Artikel. Die Zustimmung
zaehlt ganze Woerter: `"ja"` trifft *Jahr* nicht. Treffen beide Seiten,
gewinnt die Ablehnung.
"""

import re
import unittest

from agents.charakter_identitaet.resume import (
    ABLEHNUNG,
    BESTAETIGUNG,
    CONSENT_WORDS,
    REFUSAL_STEMS,
    UNKLAR,
    _has_stem,
    _has_word,
    _standard_interpretieren,
    _without_words,
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


class StandardInterpretierenTest(unittest.TestCase):

    def test_nein_gross(self) -> None:
        self.assertEqual(_standard_interpretieren("Nein"), ABLEHNUNG)

    def test_nein_klein(self) -> None:
        self.assertEqual(_standard_interpretieren("nein"), ABLEHNUNG)

    def test_nein_mit_begruendung(self) -> None:
        self.assertEqual(
            _standard_interpretieren("Nein, ich muss das korrigieren"),
            ABLEHNUNG,
        )

    def test_ja(self) -> None:
        self.assertEqual(_standard_interpretieren("Ja"), BESTAETIGUNG)

    def test_ok_mach(self) -> None:
        self.assertEqual(_standard_interpretieren("ok mach"), BESTAETIGUNG)

    def test_vielleicht_ist_unklar(self) -> None:
        self.assertEqual(_standard_interpretieren("vielleicht"), UNKLAR)

    def test_leer_ist_unklar(self) -> None:
        self.assertEqual(_standard_interpretieren(""), UNKLAR)

    def test_consent_with_ne_inside_a_word_confirms(self) -> None:
        """'ne' steckt in 'gerne' und 'meinetwegen' — das ist keine Ablehnung."""
        for answer in ("ja, gerne", "gerne", "meinetwegen", "ja bitte", "na klar", "ok"):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), BESTAETIGUNG)

    def test_refusals_are_read_as_whole_words(self) -> None:
        """Kurze und gemischte Verneinungen lehnen ab."""
        for answer in (
            "nein", "ne", "nee", "nein, bitte nicht", "lieber nicht", "mach das nicht",
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)

    def test_every_ne_refuses_also_as_article(self) -> None:
        """'ne' ausserhalb eines Zustimmungsworts lehnt ab — auch als Artikel.

        Hier stand *„ja, leg ne neue an“* als Zustimmung, weil `ne` zwischen
        zwei Woertern als Artikel galt. Welches `ne` einen Wunsch ablehnt,
        ist an der Stelle nicht zu erkennen; es gilt die sichere Richtung.
        """
        for answer in (
            "ne", "Ne.", "ne, lass mal", "ja ne", "ja, ne.", "ja ne danke",
            "ja, leg ne neue an",
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)

    def test_ne_inside_a_refusing_word_refuses_next_to_a_consent_word(self) -> None:
        """'ablehnen', 'lehne' und 'ohne' tragen 'ne' — neben 'bitte' oder 'ok' lehnen sie ab."""
        for answer in (
            "bitte ablehnen", "ok, ablehnen", "ok, ich lehne ab", "ablehnen, bitte",
            "bitte ohne mich",
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)

    def test_nichts_and_kein_refuse_next_to_a_consent_word(self) -> None:
        """'bitte nichts aendern' traegt 'bitte' — die Ablehnung gewinnt trotzdem."""
        for answer in (
            "bitte nichts ändern", "ok, lieber nichts", "bitte nichts anlegen",
            "bitte keine Änderung", "bitte auf keinen Fall", "keine Ahnung",
            "bitte keinesfalls", "nein, bitte nicht",
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)
        for answer in ("ja, gerne", "meinetwegen"):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), BESTAETIGUNG)

    def test_refusal_wins_when_both_sides_hit(self) -> None:
        """'ja, aber lieber nicht' traegt beide Woerter — die sichere Lesart gilt."""
        self.assertEqual(_standard_interpretieren("ja, aber lieber nicht"), ABLEHNUNG)

    def test_word_inside_another_word_is_no_hit(self) -> None:
        """'Jahr' ist nicht 'ja' — es bleibt unklar.

        'vernichten' stand hier als unklar; seit die Ablehnung ihre Staemme
        mitten im Wort sucht, lehnt es ab wie vor der Wortgrenze (die sichere
        Richtung).
        """
        self.assertEqual(_standard_interpretieren("Jahr"), UNKLAR)
        self.assertEqual(_standard_interpretieren("vernichten"), ABLEHNUNG)

    def test_every_refusal_stem_refuses_next_to_a_consent_word(self) -> None:
        """Jeder Stamm lehnt ab, auch mitten im Wort und neben 'bitte' oder 'ok'.

        Ohne das Wort mit dem Stamm bestaetigt dieselbe Antwort — so ist
        belegt, dass die Ablehnung am Stamm haengt und nicht an etwas anderem.
        Die Stammliste und die Formen decken sich in beiden Richtungen: Ein
        gestrichener Stamm faellt so ebenso auf wie einer ohne Formen.
        """
        self.assertEqual(set(REFUSAL_STEMS) - set(_FORMS_BY_STEM), set())
        self.assertEqual(set(_FORMS_BY_STEM) - set(REFUSAL_STEMS), set())
        for stem in REFUSAL_STEMS:
            for answer in _FORMS_BY_STEM[stem]:
                with self.subTest(stem=stem, answer=answer):
                    self.assertIn(stem, answer.lower())
                    self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)
                    rest: str = _without_stem_word(answer, stem)
                    self.assertEqual(_standard_interpretieren(rest), BESTAETIGUNG)

    def test_old_refusal_stays_unless_only_a_consent_word_carried_it(self) -> None:
        """Was das alte Verfahren ablehnte, bleibt Ablehnung — ausser in 'gerne' und 'meinetwegen'.

        Das alte Verfahren ist hier nachgebildet: ein Stamm irgendwo im ganzen
        Text. Steht nach dem Herausnehmen der Zustimmungswoerter noch ein
        Stamm da, muss die Antwort ablehnen; steckte jeder Stamm in einem
        Zustimmungswort, bestaetigt sie. Beide Faelle muessen vorkommen,
        sonst prueft die Liste die Regel nicht.
        """
        refused: int = 0
        confirmed: int = 0
        for answer in _KNOWN_FORMS:
            text: str = answer.lower().strip()
            if not _head_refuses(text):
                continue
            with self.subTest(answer=answer):
                if _stem_outside_consent(text):
                    refused += 1
                    self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)
                else:
                    confirmed += 1
                    self.assertEqual(_standard_interpretieren(answer), BESTAETIGUNG)
        self.assertGreater(refused, 0)
        self.assertGreater(confirmed, 0)

    def test_doubled_ne_refuses(self) -> None:
        """'nene' ist nie der Artikel — auch nicht neben 'mach'."""
        for answer in ("nene, ich mach das selber", "ok nene"):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)

    def test_forms_behind_the_stem_still_count(self) -> None:
        """Was frueher als Teilzeichenkette mittraf, steht als eigene Form da."""
        for answer, expected in (
            ("jawohl", BESTAETIGUNG), ("machs", BESTAETIGUNG), ("klaro", BESTAETIGUNG),
            ("lassen wir das", ABLEHNUNG),
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), expected)


class HasWordTest(unittest.TestCase):
    """Der Vergleich selbst: ganze Woerter, und ein leeres Wort ist ein Defekt."""

    def test_whole_word_hits(self) -> None:
        self.assertTrue(_has_word("ja, gerne", ("gerne",)))

    def test_part_of_a_word_does_not_hit(self) -> None:
        self.assertFalse(_has_word("ja, gerne", ("ne",)))

    def test_empty_word_is_rejected(self) -> None:
        """Ein leeres Wort traefe an jeder Stelle — es wird abgewiesen, nicht gedeutet."""
        with self.assertRaises(ValueError):
            _has_word("egal", ("ja", ""))


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

    def test_whole_words_are_removed(self) -> None:
        self.assertNotIn("gerne", _without_words("ja, gerne", CONSENT_WORDS))
        self.assertNotIn("meinetwegen", _without_words("ok, meinetwegen", CONSENT_WORDS))

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
