"""Zeugen fuer den Sprecher im [GEDAECHTNIS]-Block.

Anlass (Fundliste 29.08.2026): `_format_kzg` verwarf `meta['beobachter']`,
und die LZG-Resonanz lud die Spalte nicht — Nutzer- und Nova-Destillate
standen ununterscheidbar im Block, ein woertlich zitierter Nutzersatz las
sich als Novas Erinnerung. Am Bestand desselben Tages: 3029 `assistant` /
219 `user` in `lzg_knoten`.

Zeugen dieser Datei:
  * **`speaker_label` kennt zwei Werte und meldet jeden anderen.**
  * **Die KZG-Zeile nennt den Sprecher**; ein fehlender `beobachter` steht
    als 'unbekannt' im Block und als Warnung im Log.
  * **Die Resonanz nennt den Sprecher je Erinnerung**, hinter dem Zitat.
  * **Das Spreading traegt `beobachter` von Anker und Nachbar bis ins
    Ergebnis** (Verdrahtung, mit ersetzten Lesern).
  * **Der Detail-Lader liest die Spalte wirklich** — gegen den Bestand,
    lesend, an einem aktiven Knoten.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

import psycopg2

from config import POSTGRES_URL
from graph.format import memory_context as fmt
from graph.format.memory_context import (
    LESER_ANALYSE,
    _format_kzg,
    _format_lzg_resonanz,
    reader_names,
    speaker_label,
)
from memory import lzg_knoten
from memory.lzg_knoten import _knoten_details_laden, spreading_lesen

NAMEN = reader_names(LESER_ANALYSE, "test")


class SpeakerLabelTest(unittest.TestCase):
    """Zwei Werte im Kanon, alles andere ist gemeldet."""

    def test_known_values(self) -> None:
        self.assertEqual(speaker_label("user"), "Nutzer")
        self.assertEqual(speaker_label("assistant"), "Nova")

    def test_unknown_values_are_reported(self) -> None:
        for kaputt in (None, "", "nova", "USER", 3):
            with self.subTest(beobachter=kaputt):
                with self.assertLogs(fmt.logger, level="WARNING") as logs:
                    self.assertEqual(speaker_label(kaputt), "unbekannt")
                self.assertTrue(any("ausserhalb des Kanons" in z for z in logs.output))


class KzgLineNamesSpeakerTest(unittest.TestCase):
    """Die KZG-Zeile traegt den Sprecher hinter der Salienz."""

    @staticmethod
    def _entry(beobachter: object) -> dict:
        meta: dict = {"themen": ["Magnetar"], "erstellt_am": 0.0}
        if beobachter is not None:
            meta["beobachter"] = beobachter
        return {"quelle": "kzg", "subtyp": "themen", "inhalt": "Der Nutzer will den Rekord wissen.",
                "gewicht": 1.5, "meta": meta}

    def test_user_and_assistant(self) -> None:
        self.assertEqual(
            _format_kzg(self._entry("user"), NAMEN),
            "[KZG] Magnetar (Salienz: 1.5, Sprecher: Nutzer): Der Nutzer will den Rekord wissen.",
        )
        self.assertIn("Sprecher: Nova)", _format_kzg(self._entry("assistant"), NAMEN))

    def test_missing_speaker_is_unknown_and_logged(self) -> None:
        with self.assertLogs(fmt.logger, level="WARNING"):
            zeile = _format_kzg(self._entry(None), NAMEN)
        self.assertIn("Sprecher: unbekannt)", zeile)


class ResonanceNamesSpeakerTest(unittest.TestCase):
    """Jede Erinnerung traegt ihren Sprecher direkt hinter dem Zitat."""

    def test_speaker_line_follows_quote(self) -> None:
        resonanz = {"erinnerungen": [
            {"inhalt": "Anna ist meine Schwester", "emotion": "vertrauen",
             "beobachter": "user", "sortier_gewicht": 0.9, "pfad": []},
            {"inhalt": "Der Nutzer mag Schokolade", "emotion": "neutral",
             "beobachter": "assistant", "sortier_gewicht": 0.4, "pfad": []},
        ]}
        zeilen = _format_lzg_resonanz(resonanz, NAMEN).split("\n")
        # Aufsteigend nach Gewicht: die schwaechere (Nova) zuerst.
        self.assertEqual(zeilen[2], '"Der Nutzer mag Schokolade"')
        self.assertEqual(zeilen[3], "Sprecher: Nova")
        self.assertEqual(zeilen[6], '"Anna ist meine Schwester"')
        self.assertEqual(zeilen[7], "Sprecher: Nutzer")

    def test_missing_speaker_is_unknown_and_logged(self) -> None:
        resonanz = {"erinnerungen": [
            {"inhalt": "x", "emotion": "", "sortier_gewicht": 0.1, "pfad": []}]}
        with self.assertLogs(fmt.logger, level="WARNING"):
            block = _format_lzg_resonanz(resonanz, NAMEN)
        self.assertIn("Sprecher: unbekannt", block)


class SpreadingCarriesSpeakerTest(unittest.TestCase):
    """Anker und Nachbar reichen `beobachter` bis ins Ergebnis weiter."""

    def test_anchor_and_neighbour(self) -> None:
        anker = [{"id": 1, "inhalt": "Anker", "themen": [], "entitaet_ids": [], "emotion": "",
                  "beobachter": "user", "erstellt_am": None, "gewicht_decay": 0.8}]
        nachbar = [{"nachbar_knoten_id": 2, "kante_id": 9, "verbindungs_gruende": ["themen"],
                    "geteilte_entitaet_ids": [], "geteilte_themen": ["x"]}]
        detail = {"id": 2, "inhalt": "Nachbar", "themen": [], "entitaet_ids": [], "emotion": "",
                  "beobachter": "assistant", "erstellt_am": None, "gewicht_decay": 0.5}
        with patch.object(lzg_knoten, "anker_retrieval", return_value=anker), \
                patch.object(lzg_knoten, "_kanten_nachbarn", return_value=nachbar), \
                patch.object(lzg_knoten, "_knoten_details_laden", return_value=detail):
            ergebnis = spreading_lesen("postgresql://unbenutzt", "u", "c", "[0]",
                                       cluster="paradox", nova_emotion="")
        sprecher = {e["knoten_id"]: e["beobachter"] for e in ergebnis}
        self.assertEqual(sprecher, {1: "user", 2: "assistant"})


class DetailLoaderReadsSpeakerTest(unittest.TestCase):
    """Der Detail-Lader liest `beobachter` aus dem Bestand — lesend."""

    def test_active_node_carries_speaker(self) -> None:
        conn = psycopg2.connect(POSTGRES_URL)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM lzg_knoten WHERE aktiv = TRUE ORDER BY id LIMIT 1")
                zeile = cur.fetchone()
        finally:
            conn.close()
        self.assertIsNotNone(zeile, "kein aktiver Knoten im Bestand — der Zeuge braucht einen")
        detail = _knoten_details_laden(POSTGRES_URL, int(zeile[0]))
        self.assertIsNotNone(detail)
        self.assertIn(detail["beobachter"], ("user", "assistant"))


if __name__ == "__main__":
    unittest.main()
