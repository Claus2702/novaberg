"""Unit-Test fuer _standard_interpretieren (Phase 0).

Scope: die Keyword-Klassifikation der User-Antwort, dazu der Einstieg
`resume` mit dem Status, den er daraus macht (`ClosedConsentTest`).
Strategy-Hook und End-to-End-Flow sind NICHT abgedeckt (kommt mit Phase 1).

Bestaetigt wird nur eine Antwort aus nichts als Zustimmung (geschlossene
Annahme): *„Wie bitte?“*, *„Moment, bitte“*, *„ja, vergiss es“* sind
unklar, je mit einem Zwilling, der bestaetigt. Auch die Zeichen sind
geschlossen: *„ja？“*, *„ja 👎“*, *„na ja“* sind unklar (`ClosedSignsTest`).

Die Ablehnung sucht ihre Staemme (`REFUSAL_STEMS`) auch mitten im Wort —
*keinesfalls*, *mitnichten*, *abbrechen*, *ablehnen*, *ohne* lehnen ab, und
*vernichten* ebenso (die sichere Richtung). Gesucht wird im Text ohne die
Zustimmungswoerter (`CONSENT_WORDS`): `"ne"` in *gerne* und *meinetwegen*
lehnt nicht ab, jedes andere `"ne"` schon, auch der Artikel. Die Zustimmung
zaehlt ganze Woerter: `"ja"` trifft *Jahr* nicht. Treffen beide Seiten,
gewinnt die Ablehnung.
"""

import re
import unicodedata
import unittest
from unittest.mock import patch

from agents.charakter_identitaet import resume as charakter_resume
from agents.charakter_identitaet.resume import (
    ABLEHNUNG,
    ASKING_VERBS,
    BESTAETIGUNG,
    CLAUSE_SEPARATORS,
    CONSENT_WORDS,
    DROPPED_SIGNS,
    FILLER_WORDS,
    REFUSAL_STEMS,
    SUBJECT_WORDS,
    UNKLAR,
    _asks_by_word_order,
    _consists_of_consent,
    _has_stem,
    _has_word,
    _standard_interpretieren,
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

# Formen aus `_FORMS_BY_STEM`, deren Rest ohne das Wort mit dem Stamm noch ein
# Wort traegt, das weder zustimmt noch ein Fuellwort ist (*ab*, *ändern*,
# *Änderung*, *leg ... an*). Bis zur geschlossenen Annahme bestaetigte der
# Rest; jetzt ist er unklar -- er lehnt aber nicht ab, und darauf kommt es an.
_REST_KEEPS_A_WORD: frozenset[str] = frozenset({
    "ok, ich lehne ab", "ja, leg ne neue an", "bitte nichts ändern", "bitte keine Änderung",
})

# Die Schliessbedingung: Rueckfrage, Warten, Aufschub, je mit dem Zwilling
# ohne den zurueckhaltenden Teil.
_HOLDING_BACK_PAIRS: tuple[tuple[str, str], ...] = (
    ("Wie bitte?", "Bitte"), ("Ja?", "Ja"), ("Moment, bitte", "Bitte"),
    ("Sekündchen, bitte", "Bitte"), ("wait, ok", "ok"),
    ("ja, aber erst morgen", "ja"), ("ok, ich überleg noch", "ok"),
)

# Die Antworten der Nachprobe zur geschlossenen Annahme, je mit dem Zwilling,
# der sich nur im Zeichen oder im zoegernden Wort unterscheidet und bestaetigt.
# Bis die Zeichen geschlossen waren, fiel jedes Zeichen ohne Buchstaben und
# Ziffern ausser dem ASCII-`?` weg, und *na*, *nun*, *also* waren Fuellwoerter:
# Alle diese Antworten bestaetigten.
_SIGN_PAIRS: tuple[tuple[str, str], ...] = (
    ("ja？", "ja!"), ("ok？", "ok!"), ("ja¿", "ja!"), ("ja‽", "ja!"),
    ("ja ❓", "ja :)"), ("ok ❔", "ok :)"), ("ja 👎", "ja :)"), ("ok ❌", "ok :)"),
    ("ja 🛑", "ja :)"), ("ja 🤔", "ja :)"), ("ja 🙄", "ja :)"),
    ("na ja", "ja ja"), ("nun ja", "ja ja"), ("also ja", "ja ja"),
)
# Zeichen, die vor der Pruefung ohne Luecke wegfallen (das Apostroph).
_APOSTROPHE_SIGNS: str = "'’‘`´"
# Die feste Menge der Zeichen, die wegfallen — ASCII-Leerraum und
# `. , ! ; : - ( )` —, als eigenes Literal und nicht aus `DROPPED_SIGNS`
# gerechnet: Ein Zeichen, das dort hinzukommt, fällt sonst aus der Prüfung
# heraus, statt sie rot zu machen.
_ALLOWED_SIGNS: str = " \t\n\r\f\v.,!;:-()"
# Antworten, die beide Zweige erreichen: Die Ablehnung liest den Text mit dem
# Apostroph und findet *ne*, die Zustimmung liest ihn ohne und findet *gerne*.
# Je mit dem Zwilling ohne Apostroph, der nur die Zustimmung erreicht.
_BOTH_BRANCHES: tuple[tuple[str, str], ...] = (
    ("ger'ne", "gerne"), ("Ger’ne!", "Gerne!"), ("meinet'wegen", "meinetwegen"),
)
# Die Woerter, die nach der Regel von `FILLER_WORDS` nie darin stehen: die der
# Einschraenkung oder des Aufschubs und die Partikeln des Zoegerns.
_EXCLUDED_WORDS: tuple[str, ...] = (
    "aber", "sondern", "statt", "erst", "nur", "noch", "lieber", "später", "spaeter",
    "morgen", "na", "nun", "also",
)
# Die fragenden Verben — finit, kein Imperativ — unter den Zustimmungs- und
# Fuellwoertern des Dienstes, als eigenes Literal und nicht aus `ASKING_VERBS`
# gerechnet: Ein Verb, das dort fehlt, faellt sonst aus der Pruefung heraus,
# statt sie rot zu machen. *passt* steht hier in keiner der beiden Listen.
_ASKING_VERBS: frozenset[str] = frozenset({"ist"})
# Die Fuellwoerter, die Subjekt sein koennen, ebenso als eigenes Literal.
_SUBJECT_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "ein", "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "dies", "diese", "dieses", "dieser",
})
# Fragen ohne `?`, die nur ihre Wortstellung zur Frage macht, je mit dem
# Zwilling in der Wortstellung der Aussage. Bis zur Regel der Wortstellung
# bestaetigten beide: *ist* ist Fuellwort.
_WORD_ORDER_PAIRS: tuple[tuple[str, str], ...] = (
    ("ist das ok", "das ist ok"), ("ist es ok", "es ist ok"),
)
# Die Zeichen, an denen ein Satzteil endet — `, . ! ; :` —, als eigenes
# Literal und nicht aus `CLAUSE_SEPARATORS` gerechnet: Ein Trennzeichen, das
# dort hinzukommt, teilte eine Frage in zwei Satzteile, ohne dass ein Zeuge
# es merkt.
_CLAUSE_SEPARATORS: str = ",.!;:"
# Fragen, deren Verb und Subjekt ein Zeichen trennt, das keinen Satzteil
# beendet, je mit dem Zwilling, der nur am Trennzeichen bestaetigt.
_SEPARATOR_PAIRS: tuple[tuple[str, str], ...] = (
    ("ist - das ok", "ist, das ok"), ("ist (das) ok", "ist, (das) ok"),
    ("ist) das ok", "ist), das ok"),
)


def _signs_of_a_category() -> list[str]:
    """Jedes Satz-, Symbol- und Trennzeichen (Unicode-Kategorien P, S, Z) bis zu den Emoji.

    Ausgenommen sind `_ALLOWED_SIGNS` und die Apostrophe — alles andere muss
    eine Zustimmung unklar machen.
    """
    return [
        sign for sign in map(chr, range(0x21, 0x1FB00))
        if unicodedata.category(sign)[0] in "PSZ"
        and sign not in _ALLOWED_SIGNS and sign not in _APOSTROPHE_SIGNS
    ]


_DELETE_ALL_QUESTION: str = "Charakter-Anweisung loeschen (alle)? (ja/nein)"


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
        for answer in ("ja, gerne", "gerne", "meinetwegen", "ja bitte", "klar", "ok"):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), BESTAETIGUNG)

    def test_na_klar_and_na_los_are_unclear(self) -> None:
        """Umgedreht mit den geschlossenen Zeichen: *„na klar“*, *„na los“* bestaetigten.

        *na* ist eine Partikel des Zoegerns (*„na ja“*) und kein Fuellwort
        mehr; beide fragen ein zweites Mal -- der Preis in der sicheren
        Richtung. Zwillinge: *„klar“* (oben), *„los“*.
        """
        for unclear, consent in (("na klar", "klar"), ("na los", "los")):
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_standard_interpretieren(unclear), UNKLAR)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

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
        Traegt der Rest noch ein fremdes Wort (`_REST_KEEPS_A_WORD`), ist er
        seit der geschlossenen Annahme unklar statt bestaetigt; abgelehnt
        wird auch dann nicht.
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
                    expected: str = UNKLAR if answer in _REST_KEEPS_A_WORD else BESTAETIGUNG
                    self.assertEqual(_standard_interpretieren(rest), expected)

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


def _resume(answer: str) -> dict:
    """Der Einstieg `resume` auf *„... loeschen (alle)?“* mit der Antwort des Menschen."""
    return resume({
        "parameter": {
            "action": "delete",
            "resume": True,
            "user_answer": answer,
            "original_rueckfrage": _DELETE_ALL_QUESTION,
        },
        "schritte": [],
    })


class ClosedConsentTest(unittest.TestCase):
    """Bestaetigt wird nur eine Antwort aus nichts als Zustimmung -- je mit Zwilling."""

    def test_holding_back_is_unclear_and_its_twin_confirms(self) -> None:
        """Rueckfrage, Warten und Aufschub sind unklar; ohne das Zurueckhaltende bestaetigt."""
        for unclear, consent in _HOLDING_BACK_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_standard_interpretieren(unclear), UNKLAR)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

    def test_pure_consent_confirms(self) -> None:
        """Die Zwillinge des Auftrags, dazu Fuellwoerter und das Apostroph."""
        for answer in (
            "ja", "Ja, bitte!", "Ja :)", "ok", "ja, gerne", "Ja, mach das", "Mach's",
            "ok, danke", "los",
        ):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), BESTAETIGUNG)

    def test_refusal_without_a_stem_is_no_confirmation(self) -> None:
        """Die Saetze von *Ablehnung ohne Stamm*: unklar statt bestaetigt, je mit Zwilling."""
        for unclear, consent in (
            ("ja, vergiss es", "ja"), ("ok nö", "ok"), ("bitte niemals", "bitte"),
        ):
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_standard_interpretieren(unclear), UNKLAR)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

    def test_a_word_outside_the_fillers_is_unclear(self) -> None:
        """Je eine Wortart ausserhalb der Menge neben 'ja' -- Verb, Nomen, Zahl, 'aber'."""
        for word in ("kommt", "Kaffee", "3", "aber"):
            with self.subTest(word=word):
                self.assertNotIn(word.lower(), FILLER_WORDS)
                self.assertEqual(_standard_interpretieren(f"ja, {word}"), UNKLAR)
                self.assertEqual(_standard_interpretieren("ja, das"), BESTAETIGUNG)

    def test_refusal_still_wins(self) -> None:
        """'nein, bitte nicht' und 'ja, aber lieber nicht' lehnen ab wie bisher."""
        for answer in ("nein, bitte nicht", "ja, aber lieber nicht"):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), ABLEHNUNG)

    def test_resume_goes_on_only_on_pure_consent(self) -> None:
        """Ueber `resume` auf *„... loeschen (alle)?“*: weiter nur auf reine Zustimmung.

        Nur `laufend` fuehrt zu `ausfuehren` und damit zu `_delete_alle`; die
        Bug-Saetze und *„Wie bitte?“* stellen dieselbe Frage erneut.
        """
        for answer in ("Wie bitte?", "ja, vergiss es", "ok nö", "bitte niemals", "Moment, bitte"):
            with self.subTest(answer=answer):
                result: dict = _resume(answer)
                self.assertEqual(result["status"], "rueckfrage")
                self.assertEqual(result["rueckfrage"], _DELETE_ALL_QUESTION)
                self.assertNotIn("parameter", result)
        confirmed: dict = _resume("ja")
        self.assertEqual(confirmed["status"], "laufend")
        self.assertFalse(confirmed["parameter"]["resume"])
        self.assertEqual(_resume("nein, bitte nicht")["status"], "dismissed")

    def test_consists_of_consent_only_without_question_mark_and_foreign_words(self) -> None:
        self.assertFalse(_consists_of_consent("ja? "))
        self.assertFalse(_consists_of_consent("ja? :)"))
        self.assertFalse(_consists_of_consent("das ist es"))
        self.assertTrue(_consists_of_consent("ja, bitte."))
        self.assertTrue(_consists_of_consent("mach's"))
        with self.assertRaises(ValueError):
            _consists_of_consent("Ja")

    def test_consists_of_consent_raises_when_a_filler_carries_a_refusal_stem(self) -> None:
        """Ein Fuellwort mit Ablehnungsstamm ist ein Defekt der Listen, keine Zustimmung.

        Zwilling: Dieselbe Antwort ohne dieses Wort stimmt zu, ohne zu werfen.
        """
        with patch.object(charakter_resume, "FILLER_WORDS", FILLER_WORDS | {"keinesfalls"}):
            with self.assertRaises(RuntimeError):
                _consists_of_consent("ja, keinesfalls")
            self.assertTrue(_consists_of_consent("ja"))

    def test_no_filler_carries_a_refusal_stem_or_is_a_consent_word(self) -> None:
        """Die Listen widersprechen sich nicht: kein Fuellwort lehnt ab oder stimmt zu."""
        for word in FILLER_WORDS:
            with self.subTest(word=word):
                self.assertFalse(_has_stem(word, REFUSAL_STEMS))
                self.assertNotIn(word, CONSENT_WORDS)


class ClosedSignsTest(unittest.TestCase):
    """Auch die Zeichen sind geschlossen: nur `DROPPED_SIGNS` fallen weg — je mit Zwilling."""

    def test_sign_pairs_are_unclear_and_their_twins_confirm(self) -> None:
        """Fragezeichen anderer Schriften, Emoji, *na*/*nun*/*also* sind unklar."""
        for unclear, consent in _SIGN_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_standard_interpretieren(unclear), UNKLAR)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

    def test_dropped_signs_are_exactly_the_fixed_set(self) -> None:
        """`DROPPED_SIGNS` ist genau `_ALLOWED_SIGNS` — kein Zeichen mehr, keins weniger."""
        self.assertEqual(DROPPED_SIGNS, frozenset(_ALLOWED_SIGNS))

    def test_every_sign_outside_the_fixed_set_is_unclear(self) -> None:
        """Jedes Zeichen der Kategorien P, S und Z ausserhalb des Literals macht 'ja' unklar.

        Zwilling: jedes Zeichen des Literals neben 'ja' stimmt zu.
        """
        signs: list[str] = _signs_of_a_category()
        self.assertGreater(len(signs), 5000)
        consenting: list[str] = [
            sign for sign in signs if _consists_of_consent(f"ja {sign}".lower())
        ]
        self.assertEqual(consenting, [])
        for sign in _ALLOWED_SIGNS:
            with self.subTest(sign=sign):
                self.assertTrue(_consists_of_consent(f"ja{sign}"))

    def test_question_mark_in_the_signs_raises(self) -> None:
        """Traegt die Menge ein `?`, ist das ein Defekt der Listen — 'ja!' wirft nicht."""
        with patch.object(charakter_resume, "DROPPED_SIGNS", DROPPED_SIGNS | {"?"}):
            with self.assertRaises(RuntimeError):
                _consists_of_consent("ja?")
            self.assertTrue(_consists_of_consent("ja!"))

    def test_resume_goes_on_not_on_a_sign_answer(self) -> None:
        """Ueber `resume` auf *„... loeschen (alle)?“*: Zeichenantworten fragen erneut.

        *„ja？“*, *„ja 👎“*, *„na ja“* stellen dieselbe Frage.

        Zwilling: *„ja!“* geht weiter nach `ausfuehren`.
        """
        for answer in ("ja？", "ja 👎", "na ja"):
            with self.subTest(answer=answer):
                result: dict = _resume(answer)
                self.assertEqual(result["status"], "rueckfrage")
                self.assertEqual(result["rueckfrage"], _DELETE_ALL_QUESTION)
                self.assertNotIn("parameter", result)
        self.assertEqual(_resume("ja!")["status"], "laufend")


class RefusalFirstTest(unittest.TestCase):
    """Die Ablehnung wird vor der Zustimmung geprueft — an einer Antwort, die beide erreicht."""

    def test_an_answer_reaching_both_branches_is_a_refusal(self) -> None:
        """*„ger'ne“* traegt *ne* fuer die Ablehnung und *gerne* fuer die Zustimmung.

        Zwilling: *„gerne“* ohne Apostroph erreicht nur die Zustimmung.
        """
        for both, consent in _BOTH_BRANCHES:
            with self.subTest(both=both, consent=consent):
                self.assertTrue(_consists_of_consent(both.lower()))
                self.assertEqual(_standard_interpretieren(both), ABLEHNUNG)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

    def test_resume_dismisses_an_answer_reaching_both_branches(self) -> None:
        """Ueber `resume` auf *„... loeschen (alle)?“*: *„ger'ne“* lehnt ab.

        Zwilling: *„gerne“* geht weiter nach `ausfuehren`.
        """
        refused: dict = _resume("ger'ne")
        self.assertEqual(refused["status"], "dismissed")
        self.assertNotIn("parameter", refused)
        self.assertEqual(_resume("gerne")["status"], "laufend")


class ExcludedWordsTest(unittest.TestCase):
    """Die Regel der Fuellwoerter: kein Wort des Aufschubs, der Einschraenkung, des Zoegerns."""

    def test_no_excluded_word_is_a_filler(self) -> None:
        """Keines der ausgeschlossenen Woerter steht in `FILLER_WORDS`; die Menge ist nicht leer."""
        self.assertIn("das", FILLER_WORDS)
        for word in _EXCLUDED_WORDS:
            with self.subTest(word=word):
                self.assertNotIn(word, FILLER_WORDS)

    def test_each_excluded_word_beside_ja_is_unclear(self) -> None:
        """Jedes davon allein neben 'ja' ist unklar; Zwilling 'ja das' bestaetigt."""
        self.assertEqual(_standard_interpretieren("ja das"), BESTAETIGUNG)
        for word in _EXCLUDED_WORDS:
            with self.subTest(word=word):
                self.assertEqual(_standard_interpretieren(f"ja {word}"), UNKLAR)
                self.assertEqual(_standard_interpretieren(f"{word}, ja"), UNKLAR)


class WordOrderTest(unittest.TestCase):
    """Die Frage ohne `?`: ein finites Verb vor seinem Subjekt ist unklar — je mit Zwilling."""

    def test_word_order_pairs_are_unclear_and_their_twins_confirm(self) -> None:
        """*„ist das ok“*, *„ist es ok“* sind unklar; die Aussage bestaetigt."""
        for unclear, consent in _WORD_ORDER_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_standard_interpretieren(unclear), UNKLAR)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

    def test_asking_verbs_and_subjects_are_exactly_the_fixed_sets(self) -> None:
        """`ASKING_VERBS` und `SUBJECT_WORDS` sind genau die Literale, in beide Richtungen."""
        self.assertEqual(ASKING_VERBS, _ASKING_VERBS)
        self.assertEqual(SUBJECT_WORDS, _SUBJECT_WORDS)

    def test_every_asking_verb_before_every_subject_is_unclear(self) -> None:
        """Jedes Verb des Literals vor jedem Subjekt neben 'ok' ist unklar, dahinter bestaetigt."""
        for verb in sorted(_ASKING_VERBS):
            for subject in sorted(_SUBJECT_WORDS):
                with self.subTest(verb=verb, subject=subject):
                    self.assertEqual(_standard_interpretieren(f"{verb} {subject} ok"), UNKLAR)
                    self.assertEqual(
                        _standard_interpretieren(f"{subject} {verb} ok"), BESTAETIGUNG,
                    )

    def test_the_imperative_of_consent_confirms(self) -> None:
        """*„mach das“*, *„Ja, mach das“* bestaetigen weiter — der Imperativ fragt nicht."""
        for answer in ("mach das", "Ja, mach das", "mach es", "mache das", "mach ich"):
            with self.subTest(answer=answer):
                self.assertEqual(_standard_interpretieren(answer), BESTAETIGUNG)

    def test_a_subject_in_another_clause_does_not_ask(self) -> None:
        """'ist ok, mach das' bestaetigt — 'das' steht hinter dem Komma; ohne Komma unklar."""
        self.assertEqual(_standard_interpretieren("ist ok, mach das"), BESTAETIGUNG)
        self.assertEqual(_standard_interpretieren("ist ok mach das"), UNKLAR)

    def test_an_asking_verb_outside_the_consent_raises(self) -> None:
        """Ein fragendes Verb, das in keiner Zustimmung stehen kann, ist ein Defekt der Listen."""
        self.assertTrue(_asks_by_word_order("ist das ok"))
        with patch.object(charakter_resume, "ASKING_VERBS", ASKING_VERBS | {"fragt"}):
            with self.assertRaises(RuntimeError):
                _asks_by_word_order("ist das ok")

    def test_resume_goes_on_not_on_a_word_order_question(self) -> None:
        """Ueber `resume` auf *„... loeschen (alle)?“*: *„ist das ok“* fragt erneut.

        Zwilling: *„das ist ok“* geht weiter nach `ausfuehren`.
        """
        result: dict = _resume("ist das ok")
        self.assertEqual(result["status"], "rueckfrage")
        self.assertEqual(result["rueckfrage"], _DELETE_ALL_QUESTION)
        self.assertNotIn("parameter", result)
        self.assertEqual(_resume("das ist ok")["status"], "laufend")


class ClauseSeparatorsTest(unittest.TestCase):
    """Die Trennzeichen der Satzteile sind fest: `- ( )` und Leerraum trennen nicht."""

    def test_clause_separators_are_exactly_the_fixed_set(self) -> None:
        """`CLAUSE_SEPARATORS` ist genau das Literal, in beide Richtungen."""
        self.assertEqual(CLAUSE_SEPARATORS, frozenset(_CLAUSE_SEPARATORS))

    def test_separator_pairs_are_unclear_and_their_twins_confirm(self) -> None:
        """*„ist - das ok“*, *„ist (das) ok“* sind unklar; mit Komma bestaetigen sie."""
        for unclear, consent in _SEPARATOR_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertEqual(_standard_interpretieren(unclear), UNKLAR)
                self.assertEqual(_standard_interpretieren(consent), BESTAETIGUNG)

    def test_every_other_dropped_sign_keeps_the_clause(self) -> None:
        """Jedes erlaubte Zeichen ausser den Trennzeichen zwischen Verb und Subjekt ist unklar.

        Zwilling: jedes Trennzeichen des Literals an derselben Stelle bestaetigt.
        """
        keeping: list[str] = sorted(set(_ALLOWED_SIGNS) - set(_CLAUSE_SEPARATORS))
        self.assertIn(" ", keeping)
        for sign in keeping:
            with self.subTest(sign=sign):
                self.assertEqual(_standard_interpretieren(f"ist {sign} das ok"), UNKLAR)
        for separator in _CLAUSE_SEPARATORS:
            with self.subTest(separator=separator):
                self.assertEqual(
                    _standard_interpretieren(f"ist {separator} das ok"), BESTAETIGUNG,
                )

    def test_a_separator_outside_the_dropped_signs_raises(self) -> None:
        """Ein Trennzeichen, das in keiner Zustimmung stehen kann, oder keines ist ein Defekt."""
        self.assertTrue(_asks_by_word_order("ist das ok"))
        for separators in (CLAUSE_SEPARATORS | {"?"}, frozenset()):
            with self.subTest(separators=sorted(separators)):
                patched = patch.object(charakter_resume, "CLAUSE_SEPARATORS", separators)
                with patched, self.assertRaises(RuntimeError):
                    _asks_by_word_order("ist das ok")


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
