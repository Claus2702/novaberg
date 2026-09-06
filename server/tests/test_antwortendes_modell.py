"""Zeugen dafuer, dass eine Herkunftsangabe den Sprecher nennt.

**Vierte Fundstelle einer Klasse, die an einem Tag dreimal aufschlug** — nach
dem konfigurierten statt dem antwortenden Modell geschluesselt. Die drei
anderen (Prompt-Modellebene, Wahl des Reasoning-Aufraeumers) sind am
05.09.2026 geschlossen worden; diese blieb, weil es fuer die
Hintergrund-Rollen kein Gegenstueck zu `antwortendes_chat_modell` gab.

`[gemessen]` — 06.09.2026 gegen `charakter_rad_messung`: **24 Erhebungen**
seit dem Backendwechsel am 05.09. 18:04 UTC tragen `qwen36-cpu`, obwohl
`deepseek/deepseek-v4-flash-0731` gemessen hat. Die Reihe ist damit nicht
nach dem Modell trennbar, das sie erzeugt hat — und `F-RAD-2` stuetzt sich
auf sie.

**Ein zweiter Fehler stand daneben und war folgenlos:** Das Feld trug die
Konstante des **Analyse**-Modells, waehrend alle Profile und beide Raeder
ueber `_llm_call` mit `modus="sprache"` laufen. Im aktiven Connector tragen
`PIXIE_ANALYSE_MODEL` und `SHADOW_MODEL` denselben Wert (`qwen36-cpu`), also
fiel es nie auf. Es faellt auf, sobald jemand die beiden Rollen trennt.
"""

import unittest
from unittest.mock import patch

import config
from config import (
    MODEL_WORKER_BACKENDS,
    MODELL_NACH_BACKEND,
    antwortendes_chat_modell,
    antwortendes_modell,
)


class RollenTest(unittest.TestCase):
    """Jede Rolle loest auf, und keine faellt auf eine Konstante zurueck."""

    def test_jede_rolle_nennt_ihr_backend_modell(self) -> None:
        for rolle, backend in MODEL_WORKER_BACKENDS.items():
            with self.subTest(rolle=rolle):
                self.assertEqual(
                    antwortendes_modell(rolle), MODELL_NACH_BACKEND[backend],
                )

    def test_die_alte_naht_liefert_dasselbe(self) -> None:
        """`antwortendes_chat_modell` bleibt, sie ruft nur noch durch."""
        self.assertEqual(antwortendes_chat_modell(), antwortendes_modell("chat"))

    def test_eine_unbekannte_rolle_bricht_statt_zu_raten(self) -> None:
        """Ein Rueckfall waere von einer richtigen Antwort nicht zu unterscheiden."""
        with self.assertLogs("ki_server", level="ERROR"), \
             self.assertRaises(ValueError):
            antwortendes_modell("gibt_es_nicht")

    def test_ein_unbekanntes_backend_bricht_ebenso(self) -> None:
        with patch.dict(config.MODEL_WORKER_BACKENDS,
                        {"background_sprache": "wolke7"}), \
             self.assertLogs("ki_server", level="ERROR"), \
             self.assertRaises(ValueError):
            antwortendes_modell("background_sprache")


class HerkunftDerRadMessungTest(unittest.TestCase):
    """Die Stelle, an der die Klasse zuletzt offen stand."""

    def test_die_rad_messung_greift_nicht_mehr_zur_konstante(self) -> None:
        """Rot, sobald `PIXIE_ANALYSE_MODEL` dorthin zurueckkehrt.

        Der Zeuge liest die Quelle, weil das Herkunftsfeld sonst nur im Lauf
        gegen eine laufende Datenbank pruefbar waere — und dieser Lauf
        dauert Minuten und kostet einen Modellaufruf.
        """
        import pathlib
        quelle: str = pathlib.Path(
            "/app/agents/charakter/agent.py",
        ).read_text(encoding="utf-8")
        self.assertNotIn("PIXIE_ANALYSE_MODEL", quelle)
        self.assertIn('antwortendes_modell("background_sprache")', quelle)

    def test_der_weg_ist_sprache_nicht_analyse(self) -> None:
        """Warum `background_sprache` und nicht `background_analyse`.

        Alle fuenf Profile **und** beide Raeder laufen ueber `_llm_call`,
        und der faehrt `modus="sprache"`. Rot, sobald der Weg wechselt,
        ohne dass die Herkunftsangabe mitgeht.
        """
        import pathlib
        quelle: str = pathlib.Path(
            "/app/agents/charakter/destillation.py",
        ).read_text(encoding="utf-8")
        rumpf: str = quelle[quelle.index("def _llm_call("):]
        rumpf = rumpf[: rumpf.index("\ndef ", 1)]
        self.assertIn('modus             = "sprache"', rumpf)


if __name__ == "__main__":
    unittest.main()
