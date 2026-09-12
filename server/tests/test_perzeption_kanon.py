"""Tests: Alle sechs Wertefelder der Perzeption haben einen Kanon und einen Zug.

ZIEL: Kein Wert aus der Modellantwort laeuft ungeprueft durch, und ein Wert in
der falschen Spalte wird als solcher benannt.

**Der Befund** `[gemessen 10.09.2026 ueber 2694 Perzeptionen]`:

    Dimension          erlaubt  vorgekommen  ausserhalb   Kanon-Zug
    tone                     4          16   153 (5,7 %)  nein
    intent                   6          12   119 (4,4 %)  nein
    sprach_stil              6          11    39 (1,4 %)  nein
    beziehungs_dynamik       6           7     1 (0,0 %)  nein
    emotion                 17          24    14 (0,5 %)  **ja**
    modus                   10          11     1 (0,0 %)  **ja**

**Die beiden Dimensionen mit Zug sind sauber, drei der vier ohne sind es
nicht.** Drei der vier hatten zudem ueberhaupt keine deklarierte Wertemenge —
sie standen nur als Aufzaehlung im Prompt, und `11_EVA` nennt genau das: eine
geschlossene Menge ohne Obermenge ist benutzbar und nicht pruefbar.

**Die Hauptmenge sind keine Schreibvarianten, sondern verrutschte Spalten:**
`philosophischer_austausch` steht 108-mal in `intent`, `begeisterung` 59-mal in
`tone`, `sachlich` 19-mal in `sprach_stil`. Ein Deutsch-Englisch-Array faengt
diese Klasse nicht — die Meldung muss sagen, **welches** Feld gemeint war.

**Die Prompt-Datei ist der Zeuge, nicht der Code.** Sie legt fest, was das
Modell liefern darf, und ist keine Ableitung aus dem, was hier geprueft wird.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest
from pathlib import Path

from config import (
    BEZIEHUNGS_DYNAMIK_KANON,
    INTENT_KANON,
    MODUS_KANON,
    PERZEPTION_INTENT_KANON,
    PERZEPTION_TONE_KANON,
    SPRACH_STIL_KANON,
)
from graph.nodes.perzeption import _FELDER_KANON
from utils.canon import fremdes_feld, to_canonical

SERVER_WURZEL: Path = Path(__file__).resolve().parents[1]
PROMPT: Path = SERVER_WURZEL / "prompts" / "default" / "perzeption.task.txt"
CANON_LOGGER: str = "ki_server.utils.canon"


def _werte_aus_prompt(feld: str) -> set[str]:
    """Liest die erlaubten Werte eines Feldes aus der Prompt-Datei.

    Die Zeile hat die Form `"feld": "a|b|c"` — dieselbe Form, die
    `test_modus_kanon.py` schon liest.
    """
    text: str = PROMPT.read_text(encoding="utf-8")
    treffer = re.search(rf'"{feld}":\s*"([^"]+)"', text)
    if not treffer:
        raise AssertionError(f"Feld {feld!r} steht nicht in {PROMPT.name}")
    return {w.strip() for w in treffer.group(1).split("|") if w.strip()}


class KanonGegenPromptTest(unittest.TestCase):
    """Jede Konstante ist wortgleich mit der Aufzaehlung im Prompt.

    Laufen die beiden auseinander, meldet der Zug im Betrieb einen gueltigen
    Modellwert als Ausreisser — oder er laesst einen durch, den niemand
    erwartet hat.
    """

    def test_intent(self) -> None:
        self.assertEqual(_werte_aus_prompt("intent"), set(PERZEPTION_INTENT_KANON))

    def test_tone(self) -> None:
        self.assertEqual(_werte_aus_prompt("tone"), set(PERZEPTION_TONE_KANON))

    def test_sprach_stil(self) -> None:
        self.assertEqual(_werte_aus_prompt("sprach_stil"), set(SPRACH_STIL_KANON))

    def test_beziehungs_dynamik(self) -> None:
        self.assertEqual(
            _werte_aus_prompt("beziehungs_dynamik"), set(BEZIEHUNGS_DYNAMIK_KANON),
        )

    def test_modus(self) -> None:
        """Der bestand schon — er steht hier, damit alle sechs an einem Ort sind."""
        self.assertEqual(_werte_aus_prompt("modus"), set(MODUS_KANON))


class ZweiIntentsZweiMengenTest(unittest.TestCase):
    """`INTENT_KANON` und `PERZEPTION_INTENT_KANON` sind verschiedene Sachen.

    Der Name war vergeben: `INTENT_KANON` traegt die **sechzehn** Intentionen
    der Salienz, die Perzeption kennt **sechs**. Zwei Wertemengen unter einem
    Begriff sind genau die Verwechslung, die das Modell in seinen Ausgaben
    ebenfalls macht — der Zeuge haelt sie auseinander.
    """

    def test_die_beiden_mengen_sind_verschieden(self) -> None:
        self.assertNotEqual(set(INTENT_KANON), set(PERZEPTION_INTENT_KANON))

    def test_sie_ueberschneiden_sich_in_genau_einem_wert(self) -> None:
        """`smalltalk` steht in beiden — und ist der einzige."""
        self.assertEqual(
            set(INTENT_KANON) & set(PERZEPTION_INTENT_KANON), {"smalltalk"},
        )


class AlleSechsAmZugTest(unittest.TestCase):
    """Das Wortverzeichnis deckt genau die sechs Wertefelder ab."""

    def test_sechs_felder(self) -> None:
        self.assertEqual(
            set(_FELDER_KANON),
            {"intent", "tone", "emotion", "modus", "sprach_stil", "beziehungs_dynamik"},
        )

    def test_thema_steht_nicht_darin(self) -> None:
        """Freitext hat keinen Kanon — ein Zug darauf meldete jeden Turn."""
        self.assertNotIn("thema", _FELDER_KANON)


class FremdesFeldTest(unittest.TestCase):
    """Ein Wert in der falschen Spalte wird als solcher erkannt."""

    def test_modus_wert_im_intent_feld(self) -> None:
        """Der haeufigste Fall im Bestand: 108-mal."""
        self.assertEqual(
            fremdes_feld("philosophischer_austausch", "intent", _FELDER_KANON), "modus",
        )

    def test_emotion_im_tone_feld(self) -> None:
        """Der zweithaeufigste: 59-mal."""
        self.assertEqual(
            fremdes_feld("begeisterung", "tone", _FELDER_KANON), "emotion",
        )

    def test_tone_im_stil_feld(self) -> None:
        """Der dritte: 19-mal."""
        self.assertEqual(
            fremdes_feld("sachlich", "sprach_stil", _FELDER_KANON), "tone",
        )

    def test_das_eigene_feld_zaehlt_nicht(self) -> None:
        """Sonst meldete jeder gueltige Wert sich selbst als fremd."""
        self.assertIsNone(fremdes_feld("knowledge", "intent", _FELDER_KANON))

    def test_echter_muell_hat_kein_feld(self) -> None:
        """Ein Wert, der nirgends steht, ist keine Verwechslung."""
        self.assertIsNone(fremdes_feld("bildhaft", "sprach_stil", _FELDER_KANON))


class ZugMeldetDieVerwechslungTest(unittest.TestCase):
    """Die Meldung nennt das fremde Feld — sonst fuehrt sie nicht zur Ursache."""

    def test_verwechslung_nennt_das_feld(self) -> None:
        with self.assertLogs(CANON_LOGGER, level="WARNING") as protokoll:
            ergebnis = to_canonical(
                "philosophischer_austausch", PERZEPTION_INTENT_KANON,
                "intent", "probe", fremde=_FELDER_KANON,
            )
        self.assertIsNone(ergebnis, "Ein Fremdwert bleibt im eigenen Feld ungueltig")
        self.assertIn("'modus'", protokoll.output[0])

    def test_muell_meldet_die_zahl_der_erlaubten(self) -> None:
        with self.assertLogs(CANON_LOGGER, level="WARNING") as protokoll:
            to_canonical("bildhaft", SPRACH_STIL_KANON, "sprach_stil",
                         "probe", fremde=_FELDER_KANON)
        self.assertIn("keinem anderen bekannten Feld", protokoll.output[0])

    def test_ohne_wortverzeichnis_bleibt_die_alte_meldung(self) -> None:
        """Die Erweiterung ist additiv — bestehende Aufrufer aendern sich nicht."""
        with self.assertLogs(CANON_LOGGER, level="WARNING") as protokoll:
            to_canonical("philosophischer_austausch", PERZEPTION_INTENT_KANON,
                         "intent", "probe")
        self.assertIn("keinem anderen bekannten Feld", protokoll.output[0])

    def test_der_gueltige_wert_meldet_nichts(self) -> None:
        with self.assertNoLogs(CANON_LOGGER, level="WARNING"):
            self.assertEqual(
                to_canonical("knowledge", PERZEPTION_INTENT_KANON,
                             "intent", "probe", fremde=_FELDER_KANON),
                "knowledge",
            )

    def test_die_schreibvariante_wird_weiter_gezogen(self) -> None:
        """Umlaut und Grossschreibung gehen vor der Fremdfeld-Pruefung."""
        with self.assertLogs(CANON_LOGGER, level="INFO"):
            self.assertEqual(
                to_canonical("Formell", SPRACH_STIL_KANON, "sprach_stil",
                             "probe", fremde=_FELDER_KANON),
                "formell",
            )


if __name__ == "__main__":
    unittest.main()


class VerdrahtungTest(unittest.TestCase):
    """Die Felder laufen wirklich durch den Zug, und das Protokoll wird gerufen.

    **Ohne diese Klasse waere der Bau unbewacht.** Die erste Gegenprobe nahm
    vier der sechs Felder vom Zug und entfernte das Ausreisser-Protokoll
    vollstaendig — **19 Zeugen, einer wurde rot**, und der prueft die Funktion
    isoliert. Die uebrigen belegen, dass der Zug *kann*, nicht dass er
    *gerufen wird* (`20_TESTS/verdrahtung.md`).
    """

    def _quelltext(self) -> str:
        import inspect

        from graph.nodes import perzeption as pz_mod

        return inspect.getsource(pz_mod)

    def test_alle_sechs_felder_rufen_den_zug(self) -> None:
        """Sechsmal `_kanonisch` im Leser, einmal je Wertefeld."""
        self.assertEqual(self._quelltext().count("= _kanonisch("), 6)

    def test_der_zug_bekommt_das_wortverzeichnis(self) -> None:
        """Ohne es kann er die Verwechslung nicht benennen.

        Seit dem 12.09.2026 stehen beide Tabellen als Schluesselwort — der Zug
        bekommt dazu die Uebersetzungen. Der Zeuge prueft deshalb die
        **Zuweisung** und nicht mehr die Zeichenfolge des ganzen Aufrufs: Die
        war an der Stellung gebunden und haette bei jeder Umstellung gerissen,
        ohne dass etwas fehlte.
        """
        quelle = self._quelltext()
        self.assertIn("fremde=_FELDER_KANON", quelle)
        self.assertIn("synonyme=_FELDER_SYNONYME.get(feld)", quelle)

    def test_der_knoten_ruft_das_ausreisser_protokoll(self) -> None:
        """Die Funktion allein hinterlaesst keine Zeile."""
        self.assertIn("_ausreisser_protokollieren(state, wahr, rolle)",
                      self._quelltext())


class AusreisserProtokollTest(unittest.TestCase):
    """Die Zeile entsteht beim Ausreisser — und nur dann."""

    def _lauf(self, wahr) -> list:
        from unittest.mock import patch

        from graph.nodes import perzeption as pz_mod

        zeilen: list = []
        with patch.object(pz_mod, "log_berechnung",
                          side_effect=lambda **kw: zeilen.append(kw["inhalt"])):
            pz_mod._ausreisser_protokollieren(
                {"turn_id": "probe", "user_id": "u", "character_id": "c"},
                wahr, "user",
            )
        return zeilen

    def _wahrnehmung(self, **felder):
        from graph.nodes.perzeption import Wahrnehmung

        vorgabe = {
            "intent": "knowledge", "tone": "sachlich", "emotion": "neutral",
            "modus": "alltag", "sprach_stil": "neutral",
            "beziehungs_dynamik": "neutral",
        }
        vorgabe.update(felder)
        return Wahrnehmung(**vorgabe)

    def test_der_saubere_lauf_schreibt_nichts(self) -> None:
        """Eine Zeile je Turn waere der Regelfall und damit kein Befund."""
        self.assertEqual(self._lauf(self._wahrnehmung()), [])

    def test_die_verwechslung_nennt_das_fremde_feld(self) -> None:
        """Der haeufigste Fall im Bestand: 108-mal `philosophischer_austausch`."""
        zeilen = self._lauf(self._wahrnehmung(intent="philosophischer_austausch"))
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(zeilen[0]["anzahl"], 1)
        self.assertEqual(zeilen[0]["verwechselt"], 1)
        self.assertEqual(zeilen[0]["ausreisser"][0]["fremdes_feld"], "modus")

    def test_echter_muell_traegt_kein_fremdes_feld(self) -> None:
        """`bildhaft` steht in keinem der sechs Kanons — im Bestand einmal."""
        zeilen = self._lauf(self._wahrnehmung(sprach_stil="bildhaft"))
        self.assertEqual(zeilen[0]["verwechselt"], 0)
        self.assertIsNone(zeilen[0]["ausreisser"][0]["fremdes_feld"])

    def test_mehrere_ausreisser_stehen_in_einer_zeile(self) -> None:
        """Drei Zeilen je Turn waeren dreimal derselbe Befund."""
        zeilen = self._lauf(self._wahrnehmung(
            intent="philosophischer_austausch", tone="begeisterung",
            sprach_stil="sachlich",
        ))
        self.assertEqual(len(zeilen), 1)
        self.assertEqual(zeilen[0]["anzahl"], 3)
        self.assertEqual(zeilen[0]["verwechselt"], 3)

    def test_der_umlaut_ist_kein_ausreisser(self) -> None:
        """Er wird vom Zug gerettet, bevor das Protokoll ihn sieht."""
        from graph.nodes.perzeption import _EMOTION_ODER_SYNONYM, _kanonisch

        gezogen = _kanonisch("mitgefühl", _EMOTION_ODER_SYNONYM, "emotion")
        self.assertEqual(self._lauf(self._wahrnehmung(emotion=gezogen)), [])
