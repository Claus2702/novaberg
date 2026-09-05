"""Zeugen: Die beiden Aufzaehlungen der Worker-Backends bleiben deckungsgleich.

Ziel: Der Kanon der Worker-Backends steht an **zwei** Stellen — als
Backend-Bauer in `services/model_services/registry.py::_build_backend` und
als Modell-Abbildung in `config.MODELL_NACH_BACKEND`. Zwei Aufzaehlungen
desselben Kanons laufen auseinander, und die Abweichung faellt erst auf, wenn
jemand umschaltet: Ein Backend, das gebaut werden kann, aber in der Abbildung
fehlt, laesst den Server beim Start abbrechen; eines, das nur in der Abbildung
steht, sagt eine Modellebene zu, die nie gebaut wird.

Zeugen dieser Datei:
  * **Beide Richtungen werden geprueft, nicht nur eine.** Die Teilmengen-Falle
    (`11_EVA` §2) ist genau hier zu Hause: Wer nur fragt *"kennt der Bauer
    jeden Schluessel der Abbildung?"*, sieht einen ueberzaehligen Bauer nicht.
  * **Die Verhaltensgleichheit des Bestands ist eigens bezeugt.** Bei
    `ollama_gpu` — dem Wert, unter dem das System heute laeuft — muss die
    Modellebene denselben Namen liefern wie vor dem Umbau, `OLLAMA_MODEL`.
  * **Ein Backend ausserhalb des Kanons faellt laut aus.** Kein stiller
    Rueckfall: Eine Prompt-Modellebene, die nach einem nicht sprechenden
    Modell geschluesselt ist, waere von einer richtigen nicht zu
    unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

import config
from config import MODELL_NACH_BACKEND, OLLAMA_MODEL, antwortendes_chat_modell
from services.model_services import registry


class TestKanonDeckung(unittest.TestCase):
    """Die beiden Aufzaehlungen gegeneinander."""

    def test_jeder_schluessel_der_abbildung_wird_gebaut(self) -> None:
        """Was eine Modellebene zugesagt bekommt, muss auch baubar sein."""
        with patch.object(registry, "ANTHROPIC_API_KEY", "sk-test"), \
             patch.object(registry, "OPENROUTER_API_KEY", "sk-or-test"):
            for schluessel in MODELL_NACH_BACKEND:
                with self.subTest(backend=schluessel):
                    self.assertIsNotNone(registry._build_backend(schluessel))

    def test_kein_bauer_ohne_eintrag_in_der_abbildung(self) -> None:
        """Die andere Richtung — sonst bliebe ein ueberzaehliger Bauer stumm.

        Die Menge der baubaren Schluessel wird aus dem Quelltext gelesen, nicht
        aus einer zweiten Liste: Eine dritte Aufzaehlung waere genau das
        Problem, das dieser Zeuge verhindern soll.
        """
        import ast
        import inspect

        baum = ast.parse(inspect.getsource(registry._build_backend))
        gebaut: set[str] = {
            knoten.comparators[0].value
            for knoten in ast.walk(baum)
            if isinstance(knoten, ast.Compare)
            and isinstance(knoten.left, ast.Name)
            and knoten.left.id == "kind"
            and isinstance(knoten.comparators[0], ast.Constant)
        }

        self.assertTrue(gebaut, "kein einziger Backend-Zweig gefunden — Zeuge blind")
        self.assertEqual(gebaut, set(MODELL_NACH_BACKEND))


class TestModellebene(unittest.TestCase):
    """Welches Modell die Prompt-Modellebene schluesselt."""

    def test_ollama_gpu_bleibt_beim_bisherigen_namen(self) -> None:
        """Der Bestandsfall — das Verhalten vor dem Umbau."""
        with patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "ollama_gpu"}):
            self.assertEqual(antwortendes_chat_modell(), OLLAMA_MODEL)

    def test_openrouter_schluesselt_nach_der_modell_id(self) -> None:
        with patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "openrouter"}), \
             patch.dict(config.MODELL_NACH_BACKEND, {"openrouter": "anbieter/modell-x"}):
            self.assertEqual(antwortendes_chat_modell(), "anbieter/modell-x")

    def test_unbekanntes_backend_faellt_laut_aus(self) -> None:
        with patch.dict(config.MODEL_WORKER_BACKENDS, {"chat": "erfunden"}):
            with self.assertLogs("ki_server", level="ERROR"):
                with self.assertRaises(ValueError):
                    antwortendes_chat_modell()


if __name__ == "__main__":
    unittest.main()
