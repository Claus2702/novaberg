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
  4. **Angelegt wird nur, wenn die Antwort aus nichts als Zustimmung
     besteht** (geschlossene Annahme): *„Wie bitte?“*, *„Moment, bitte“*,
     *„ja, vergiss es“* fragen erneut, je mit einem Zwilling, der anlegt.
     Auch die Zeichen sind geschlossen: *„ja？“*, *„ja 👎“*, *„na ja“*
     fragen erneut.

Kein Zeuge oeffnet eine Datenbank oder ein Netz: Die Deutung schreibt nicht,
sie gibt nur den naechsten Zustand zurueck.
"""

import json
import re
import unicodedata
import unittest
from unittest.mock import patch

from agents.notizen import resume as notizen_resume
from agents.notizen.resume import (
    ASKING_VERBS,
    CLAUSE_SEPARATORS,
    CONSENT_WORDS,
    DROPPED_SIGNS,
    FILLER_WORDS,
    REFUSAL_STEMS,
    SUBJECT_WORDS,
    _asks_by_word_order,
    _candidate_keys,
    _consists_of_consent,
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

# Formen aus `_FORMS_BY_STEM`, deren Rest ohne das Wort mit dem Stamm noch ein
# Wort traegt, das weder zustimmt noch ein Fuellwort ist (*ab*, *ändern*,
# *Änderung*, *leg ... an*). Bis zur geschlossenen Annahme legte der Rest an;
# jetzt fragt er erneut -- er lehnt aber nicht ab, und darauf kommt es an.
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
# der sich nur im Zeichen oder im zoegernden Wort unterscheidet und anlegt.
# Bis die Zeichen geschlossen waren, fiel jedes Zeichen ohne Buchstaben und
# Ziffern ausser dem ASCII-`?` weg, und *na*, *nun*, *also* waren Fuellwoerter:
# Alle diese Antworten legten an.
_SIGN_PAIRS: tuple[tuple[str, str], ...] = (
    ("ja？", "ja!"), ("ok？", "ok!"), ("ja¿", "ja!"), ("ja‽", "ja!"),
    ("ja ❓", "ja :)"), ("ok ❔", "ok :)"), ("ja 👎", "ja :)"), ("ok ❌", "ok :)"),
    ("ja 🛑", "ja :)"), ("ja 🤔", "ja :)"), ("ja 🙄", "ja :)"),
    ("na ja", "ja ja"), ("nun ja", "ja ja"), ("also ja", "ja ja"),
)
# Zeichen, die vor der Pruefung ohne Luecke wegfallen (das Apostroph).
_APOSTROPHE_SIGNS: str = "'’‘`´"
# Die feste Menge der Zeichen, die wegfallen -- ASCII-Leerraum und
# `. , ! ; : - ( )` --, als eigenes Literal und nicht aus `DROPPED_SIGNS`
# gerechnet: Ein Zeichen, das dort hinzukommt, faellt sonst aus der Pruefung
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
# Die fragenden Verben -- finit, kein Imperativ -- unter den Zustimmungs- und
# Fuellwoertern des Dienstes, als eigenes Literal und nicht aus `ASKING_VERBS`
# gerechnet: Ein Verb, das dort fehlt, faellt sonst aus der Pruefung heraus,
# statt sie rot zu machen.
_ASKING_VERBS: frozenset[str] = frozenset({"ist", "passt"})
# Die Fuellwoerter, die Subjekt sein koennen, ebenso als eigenes Literal.
_SUBJECT_WORDS: frozenset[str] = frozenset({
    "der", "die", "das", "ein", "ich", "du", "er", "sie", "es", "wir", "ihr", "man",
    "dies", "diese", "dieses", "dieser",
})
# Fragen ohne `?`, die nur ihre Wortstellung zur Frage macht, je mit dem
# Zwilling in der Wortstellung der Aussage. Bis zur Regel der Wortstellung
# legten alle an: *ist* ist Fuellwort, *passt* Zustimmungswort.
_WORD_ORDER_PAIRS: tuple[tuple[str, str], ...] = (
    ("ist das ok", "das ist ok"), ("ist es ok", "es ist ok"),
    ("passt es", "es passt"), ("passt das", "das passt"),
)
# Die Zeichen, an denen ein Satzteil endet -- `, . ! ; :` --, als eigenes
# Literal und nicht aus `CLAUSE_SEPARATORS` gerechnet: Ein Trennzeichen, das
# dort hinzukommt, teilte eine Frage in zwei Satzteile, ohne dass ein Zeuge
# es merkt.
_CLAUSE_SEPARATORS: str = ",.!;:"
# Fragen, deren Verb und Subjekt ein Zeichen trennt, das keinen Satzteil
# beendet, je mit dem Zwilling, der nur am Trennzeichen anlegt.
_SEPARATOR_PAIRS: tuple[tuple[str, str], ...] = (
    ("ist - das ok", "ist, das ok"), ("ist (das) ok", "ist, (das) ok"),
    ("ist) das ok", "ist), das ok"), ("passt - es", "passt, es"),
)


def _signs_of_a_category() -> list[str]:
    """Jedes Satz-, Symbol- und Trennzeichen (Unicode-Kategorien P, S, Z) bis zu den Emoji.

    Ausgenommen sind `_ALLOWED_SIGNS` und die Apostrophe -- alles andere muss
    eine Zustimmung unklar machen.
    """
    return [
        sign for sign in map(chr, range(0x21, 0x1FB00))
        if unicodedata.category(sign)[0] in "PSZ"
        and sign not in _ALLOWED_SIGNS and sign not in _APOSTROPHE_SIGNS
    ]

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
        for answer in ("ja, gerne", "gerne", "meinetwegen", "ja bitte", "klar", "ok"):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "laufend")
                self.assertEqual(result["parameter"]["action"], "create")

    def test_na_klar_asks_again(self) -> None:
        """Umgedreht mit den geschlossenen Zeichen: *„na klar“* legte oben an.

        *na* ist eine Partikel des Zoegerns (*„na ja“*) und kein Fuellwort
        mehr; *„na klar“* fragt ein zweites Mal -- der Preis in der sicheren
        Richtung. Zwilling: *„klar“* legt an (oben).
        """
        self.assertTrue(_asks_again(_not_found("na klar")))

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
        dass die Ablehnung am Stamm haengt und nicht an etwas anderem. Traegt
        der Rest noch ein fremdes Wort (`_REST_KEEPS_A_WORD`), fragt er seit
        der geschlossenen Annahme erneut statt anzulegen; abgelehnt wird auch
        dann nicht.
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
                    expected: str = "rueckfrage" if answer in _REST_KEEPS_A_WORD else "laufend"
                    self.assertEqual(rest["status"], expected)

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


def _asks_again(result: dict) -> bool:
    """Stellt das Ergebnis die Frage *„soll ich anlegen?“* erneut, ohne anzulegen?"""
    return (
        result["status"] == "rueckfrage"
        and json.loads(result["rueckfrage"])["typ"] == "nicht_gefunden"
        and "parameter" not in result
    )


def _creates(result: dict) -> bool:
    """Fuehrt das Ergebnis zum Anlegen der Notiz?"""
    return result["status"] == "laufend" and result["parameter"]["action"] == "create"


class ClosedConsentTest(unittest.TestCase):
    """Angelegt wird nur auf eine Antwort aus nichts als Zustimmung -- je mit Zwilling."""

    def test_holding_back_asks_again_and_its_twin_creates(self) -> None:
        """Rueckfrage, Warten und Aufschub fragen erneut; ohne das Zurueckhaltende angelegt."""
        for unclear, consent in _HOLDING_BACK_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertTrue(_asks_again(_not_found(unclear)))
                self.assertTrue(_creates(_not_found(consent)))

    def test_pure_consent_creates(self) -> None:
        """Die Zwillinge des Auftrags, dazu Fuellwoerter und das Apostroph."""
        for answer in (
            "ja", "Ja, bitte!", "Ja :)", "ok", "ja, gerne", "Ja, mach das", "Mach's",
            "ok, danke", "auf jeden",
        ):
            with self.subTest(answer=answer):
                self.assertTrue(_creates(_not_found(answer)))

    def test_refusal_without_a_stem_creates_nothing(self) -> None:
        """Die Saetze von *Ablehnung ohne Stamm* fragen erneut, je mit Zwilling, der anlegt."""
        for unclear, consent in (
            ("ja, vergiss es", "ja"), ("ok nö", "ok"), ("bitte niemals", "bitte"),
        ):
            with self.subTest(unclear=unclear, consent=consent):
                self.assertTrue(_asks_again(_not_found(unclear)))
                self.assertTrue(_creates(_not_found(consent)))

    def test_a_word_outside_the_fillers_asks_again(self) -> None:
        """Je eine Wortart ausserhalb der Menge neben 'ja' -- Verb, Nomen, Zahl, 'aber'."""
        for word in ("kommt", "Kaffee", "3", "aber"):
            with self.subTest(word=word):
                self.assertNotIn(word.lower(), FILLER_WORDS)
                self.assertTrue(_asks_again(_not_found(f"ja, {word}")))
                self.assertTrue(_creates(_not_found("ja, das")))

    def test_refusal_still_wins(self) -> None:
        """'nein, bitte nicht' und 'ja, aber lieber nicht' lehnen ab wie bisher."""
        for answer in ("nein, bitte nicht", "ja, aber lieber nicht"):
            with self.subTest(answer=answer):
                result: dict = _not_found(answer)
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertNotIn("parameter", result)

    def test_resume_creates_only_on_pure_consent(self) -> None:
        """Ueber `resume`: *„Wie bitte?“* und die Bug-Saetze legen nichts an, 'ja' schon."""
        rueckfrage: str = json.dumps(_NOT_FOUND)
        for answer in ("Wie bitte?", "ja, vergiss es", "ok nö", "bitte niemals", "Moment, bitte"):
            with self.subTest(answer=answer):
                result: dict = resume(_state(user_answer=answer, original_rueckfrage=rueckfrage))
                self.assertTrue(_asks_again(result))
        confirmed: dict = resume(_state(user_answer="ja", original_rueckfrage=rueckfrage))
        self.assertTrue(_creates(confirmed))

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
        with patch.object(notizen_resume, "FILLER_WORDS", FILLER_WORDS | {"keinesfalls"}):
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
    """Auch die Zeichen sind geschlossen: nur `DROPPED_SIGNS` fallen weg -- je mit Zwilling."""

    def test_sign_pairs_ask_again_and_their_twins_create(self) -> None:
        """Fragezeichen anderer Schriften, Emoji, *na*/*nun*/*also* fragen erneut."""
        for unclear, consent in _SIGN_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertTrue(_asks_again(_not_found(unclear)))
                self.assertTrue(_creates(_not_found(consent)))

    def test_dropped_signs_are_exactly_the_fixed_set(self) -> None:
        """`DROPPED_SIGNS` ist genau `_ALLOWED_SIGNS` -- kein Zeichen mehr, keins weniger."""
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
        """Traegt die Menge ein `?`, ist das ein Defekt der Listen -- 'ja!' wirft nicht."""
        with patch.object(notizen_resume, "DROPPED_SIGNS", DROPPED_SIGNS | {"?"}):
            with self.assertRaises(RuntimeError):
                _consists_of_consent("ja?")
            self.assertTrue(_consists_of_consent("ja!"))

    def test_resume_creates_nothing_on_a_sign_answer(self) -> None:
        """Ueber `resume`: *„ja？“*, *„ja 👎“*, *„na ja“* legen nichts an, *„ja!“* schon."""
        rueckfrage: str = json.dumps(_NOT_FOUND)
        for answer in ("ja？", "ja 👎", "na ja"):
            with self.subTest(answer=answer):
                result: dict = resume(_state(user_answer=answer, original_rueckfrage=rueckfrage))
                self.assertTrue(_asks_again(result))
        confirmed: dict = resume(_state(user_answer="ja!", original_rueckfrage=rueckfrage))
        self.assertTrue(_creates(confirmed))


class RefusalFirstTest(unittest.TestCase):
    """Die Ablehnung wird vor der Zustimmung geprueft -- an einer Antwort, die beide erreicht."""

    def test_an_answer_reaching_both_branches_creates_nothing(self) -> None:
        """*„ger'ne“* traegt *ne* fuer die Ablehnung und *gerne* fuer die Zustimmung.

        Zwilling: *„gerne“* ohne Apostroph erreicht nur die Zustimmung und legt an.
        """
        for both, consent in _BOTH_BRANCHES:
            with self.subTest(both=both, consent=consent):
                self.assertTrue(_consists_of_consent(both.lower()))
                result: dict = _not_found(both)
                self.assertEqual(result["status"], "abgeschlossen")
                self.assertNotIn("parameter", result)
                self.assertTrue(_creates(_not_found(consent)))

    def test_resume_creates_nothing_on_an_answer_reaching_both_branches(self) -> None:
        """Ueber `resume`: *„ger'ne“* legt nichts an, *„gerne“* schon."""
        rueckfrage: str = json.dumps(_NOT_FOUND)
        refused: dict = resume(_state(user_answer="ger'ne", original_rueckfrage=rueckfrage))
        self.assertEqual(refused["status"], "abgeschlossen")
        self.assertNotIn("parameter", refused)
        confirmed: dict = resume(_state(user_answer="gerne", original_rueckfrage=rueckfrage))
        self.assertTrue(_creates(confirmed))


class ExcludedWordsTest(unittest.TestCase):
    """Die Regel der Fuellwoerter: kein Wort des Aufschubs, der Einschraenkung, des Zoegerns."""

    def test_no_excluded_word_is_a_filler(self) -> None:
        """Keines der ausgeschlossenen Woerter steht in `FILLER_WORDS`; die Menge ist nicht leer."""
        self.assertIn("das", FILLER_WORDS)
        for word in _EXCLUDED_WORDS:
            with self.subTest(word=word):
                self.assertNotIn(word, FILLER_WORDS)

    def test_each_excluded_word_beside_ja_asks_again(self) -> None:
        """Jedes davon allein neben 'ja' fragt erneut; Zwilling 'ja das' legt an."""
        self.assertTrue(_creates(_not_found("ja das")))
        for word in _EXCLUDED_WORDS:
            with self.subTest(word=word):
                self.assertTrue(_asks_again(_not_found(f"ja {word}")))
                self.assertTrue(_asks_again(_not_found(f"{word}, ja")))


class WordOrderTest(unittest.TestCase):
    """Die Frage ohne `?`: ein finites Verb vor seinem Subjekt fragt erneut -- je mit Zwilling."""

    def test_word_order_pairs_ask_again_and_their_twins_create(self) -> None:
        """*„ist das ok“*, *„passt es“* ... fragen erneut; die Aussage legt an."""
        for unclear, consent in _WORD_ORDER_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertTrue(_asks_again(_not_found(unclear)))
                self.assertTrue(_creates(_not_found(consent)))

    def test_asking_verbs_and_subjects_are_exactly_the_fixed_sets(self) -> None:
        """`ASKING_VERBS` und `SUBJECT_WORDS` sind genau die Literale, in beide Richtungen."""
        self.assertEqual(ASKING_VERBS, _ASKING_VERBS)
        self.assertEqual(SUBJECT_WORDS, _SUBJECT_WORDS)

    def test_every_asking_verb_before_every_subject_asks_again(self) -> None:
        """Jedes Verb des Literals vor jedem Subjekt neben 'ok' fragt erneut, dahinter legt an."""
        for verb in sorted(_ASKING_VERBS):
            for subject in sorted(_SUBJECT_WORDS):
                with self.subTest(verb=verb, subject=subject):
                    self.assertTrue(_asks_again(_not_found(f"{verb} {subject} ok")))
                    self.assertTrue(_creates(_not_found(f"{subject} {verb} ok")))

    def test_the_imperative_of_consent_creates(self) -> None:
        """*„mach das“*, *„Ja, mach das“* legen weiter an -- der Imperativ fragt nicht."""
        for answer in ("mach das", "Ja, mach das", "mach es", "mache das", "mach ich"):
            with self.subTest(answer=answer):
                self.assertTrue(_creates(_not_found(answer)))

    def test_a_subject_in_another_clause_does_not_ask(self) -> None:
        """'passt, mach das' legt an -- 'das' steht hinter dem Komma; ohne Komma fragt es erneut."""
        self.assertTrue(_creates(_not_found("passt, mach das")))
        self.assertTrue(_asks_again(_not_found("passt mach das")))

    def test_an_asking_verb_outside_the_consent_raises(self) -> None:
        """Ein fragendes Verb, das in keiner Zustimmung stehen kann, ist ein Defekt der Listen."""
        self.assertTrue(_asks_by_word_order("ist das ok"))
        with patch.object(notizen_resume, "ASKING_VERBS", ASKING_VERBS | {"fragt"}):
            with self.assertRaises(RuntimeError):
                _asks_by_word_order("ist das ok")

    def test_resume_creates_nothing_on_a_word_order_question(self) -> None:
        """Ueber `resume`: *„ist das ok“* legt nichts an, *„das ist ok“* schon."""
        rueckfrage: str = json.dumps(_NOT_FOUND)
        unclear: dict = resume(_state(user_answer="ist das ok", original_rueckfrage=rueckfrage))
        self.assertTrue(_asks_again(unclear))
        confirmed: dict = resume(_state(user_answer="das ist ok", original_rueckfrage=rueckfrage))
        self.assertTrue(_creates(confirmed))


class ClauseSeparatorsTest(unittest.TestCase):
    """Die Trennzeichen der Satzteile sind fest: `- ( )` und Leerraum trennen nicht."""

    def test_clause_separators_are_exactly_the_fixed_set(self) -> None:
        """`CLAUSE_SEPARATORS` ist genau das Literal, in beide Richtungen."""
        self.assertEqual(CLAUSE_SEPARATORS, frozenset(_CLAUSE_SEPARATORS))

    def test_separator_pairs_ask_again_and_their_twins_create(self) -> None:
        """*„ist - das ok“*, *„ist (das) ok“* fragen erneut; mit Komma legen sie an."""
        for unclear, consent in _SEPARATOR_PAIRS:
            with self.subTest(unclear=unclear, consent=consent):
                self.assertTrue(_asks_again(_not_found(unclear)))
                self.assertTrue(_creates(_not_found(consent)))

    def test_every_other_dropped_sign_keeps_the_clause(self) -> None:
        """Jedes erlaubte Zeichen ausser den Trennzeichen zwischen Verb und Subjekt fragt erneut.

        Zwilling: jedes Trennzeichen des Literals an derselben Stelle legt an.
        """
        keeping: list[str] = sorted(set(_ALLOWED_SIGNS) - set(_CLAUSE_SEPARATORS))
        self.assertIn(" ", keeping)
        for sign in keeping:
            with self.subTest(sign=sign):
                self.assertTrue(_asks_again(_not_found(f"ist {sign} das ok")))
        for separator in _CLAUSE_SEPARATORS:
            with self.subTest(separator=separator):
                self.assertTrue(_creates(_not_found(f"ist {separator} das ok")))

    def test_a_separator_outside_the_dropped_signs_raises(self) -> None:
        """Ein Trennzeichen, das in keiner Zustimmung stehen kann, oder keines ist ein Defekt."""
        self.assertTrue(_asks_by_word_order("ist das ok"))
        for separators in (CLAUSE_SEPARATORS | {"?"}, frozenset()):
            with self.subTest(separators=sorted(separators)):
                patched = patch.object(notizen_resume, "CLAUSE_SEPARATORS", separators)
                with patched, self.assertRaises(RuntimeError):
                    _asks_by_word_order("ist das ok")


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
