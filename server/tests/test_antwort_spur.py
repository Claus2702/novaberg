"""Tests für die Spur der Antwort — jede Schreibstelle ist sichtbar.

Ziel: `state["response"]` ist der Wert, der beim Menschen ankommt. Wird er
unterwegs leer, muss im Protokoll stehen **wer** ihn geleert hat. Bis zum
19.08.2026 schrieben sechs Stellen ihn, und keine protokollierte es.

Die Zusicherungen:

  1. **Keine Schreibstelle umgeht den Helfer.** Das ist der tragende Zeuge:
     Eine Zuweisung an `state["response"]` irgendwo im Graphen ist
     unsichtbar und sieht im Protokoll aus wie gar keine Schreibung.
  2. **Jede Schreibung erzeugt genau eine Zeile** mit alter Länge, neuer
     Länge und Schreibername.
  3. **Nichtleer → leer ist ein Fehler, keine Warnung.** Ein Pfad, der die
     Arbeit nicht tut, ist ein Fehler, unabhängig davon, wie harmlos er
     wirkt.
  4. **Der Umschlag des Anbieters wird vor jeder Zuweisung protokolliert**,
     samt `done_reason` — dem Feld, dessen Fehlen den offenen Defekt
     unaufklärbar machte.
  5. **Ein Umschlag mit erzeugten Token und leeren Ausgabefeldern ist ein
     Fehler** und trägt den Rumpf mit.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import unittest
from pathlib import Path

from graph.antwort_spur import antwort_setzen
from services.llm_provider import _antwort_umschlag_melden

#: Der Baum, in dem keine Zuweisung am Helfer vorbeigehen darf.
WURZEL: Path = Path(__file__).resolve().parent.parent

#: Die einzige Datei, die `state["response"]` direkt setzen darf — dort
#: steht die Zuweisung, die der Helfer selbst ausführt.
HELFER: str = "antwort_spur.py"


def _direkte_schreibstellen(baum: Path) -> list[str]:
    """Findet jede Zuweisung an `state["response"]` außerhalb des Helfers.

    Vorbedingung: `baum` ist ein Verzeichnis mit Python-Dateien.
    Nachbedingung: Liste von `datei:zeile`, leer wenn keine Stelle den
    Helfer umgeht.

    **Über den AST, nicht über eine Textsuche.** Ein Grep auf
    `state["response"]` träfe auch jedes Lesen — und ein Zeuge, der bei
    jedem Lesezugriff anschlägt, wird weggeschaltet statt gelesen.
    """
    treffer: list[str] = []
    for datei in sorted(baum.rglob("*.py")):
        # `tests/` ist ausgenommen, und das ist eine Entscheidung: Ein Zeuge,
        # der einen Zustand als Vorbedingung aufbaut, schreibt keine Antwort
        # in den Laufzeitpfad — er stellt eine her. Der Riegel bewacht den
        # Weg, den ein echter Turn nimmt.
        if (datei.name == HELFER
                or "__pycache__" in str(datei)
                or datei.parts[len(baum.parts):][:1] == ("tests",)):
            continue
        try:
            gebaut = ast.parse(datei.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for knoten in ast.walk(gebaut):
            if not isinstance(knoten, ast.Assign):
                continue
            for ziel in knoten.targets:
                if (isinstance(ziel, ast.Subscript)
                        and isinstance(ziel.slice, ast.Constant)
                        and ziel.slice.value == "response"):
                    treffer.append(f"{datei.relative_to(baum)}:{knoten.lineno}")
    return treffer


class SpurVollstaendigTest(unittest.TestCase):
    """Der Riegel: keine Schreibstelle geht am Helfer vorbei."""

    def test_keine_zuweisung_umgeht_den_helfer(self) -> None:
        """Eine unsichtbare Schreibung sieht aus wie keine Schreibung."""
        umgehungen: list[str] = _direkte_schreibstellen(WURZEL)
        self.assertEqual(
            [], umgehungen,
            f"Diese Stellen schreiben an der Spur vorbei: {umgehungen}",
        )

    def test_der_riegel_findet_eine_umgehung(self) -> None:
        """Der Auslösefall des Riegels.

        Ohne ihn ist ein schweigender Riegel von einem sauberen Bestand nicht
        zu unterscheiden.
        """
        with self.assertLogs("ki_server.antwort_spur"):
            antwort_setzen({}, "x", "auslösefall")

        baum = ast.parse('def f(state):\n    state["response"] = "x"\n')
        gefunden = [
            k for k in ast.walk(baum)
            if isinstance(k, ast.Assign)
            and any(isinstance(z, ast.Subscript)
                    and isinstance(z.slice, ast.Constant)
                    and z.slice.value == "response"
                    for z in k.targets)
        ]
        self.assertEqual(1, len(gefunden), "Das Suchmuster trifft nichts mehr")


class SchreibungTest(unittest.TestCase):
    """Jede Schreibung hinterlässt genau eine lesbare Zeile."""

    def test_schreibung_nennt_beide_laengen_und_den_schreiber(self) -> None:
        """Ohne den Schreibernamen ist die Zeile nicht zuzuordnen."""
        alt:  str  = "alte Antwort"
        neu:  str  = "neue laengere Antwort"
        zustand: dict = {"response": alt}
        with self.assertLogs("ki_server.antwort_spur", level="INFO") as protokoll:
            antwort_setzen(zustand, neu, "thinker/korrektur")
        zeile: str = protokoll.output[0]
        self.assertIn("thinker/korrektur", zeile)
        # Gerechnet statt hingeschrieben: Eine Zahl im Zeugen, die aus einem
        # Literal daneben folgt, wird beim naechsten Wortwechsel falsch.
        self.assertIn(f"{len(alt)} → {len(neu)}", zeile)
        self.assertEqual(neu, zustand["response"])

    def test_nichtleer_zu_leer_ist_ein_fehler(self) -> None:
        """Ein Pfad, der die Arbeit nicht tut, ist ein Fehler."""
        zustand: dict = {"response": "eine fertige Antwort"}
        with self.assertLogs("ki_server.antwort_spur", level="ERROR") as protokoll:
            antwort_setzen(zustand, "", "responder")
        self.assertIn("verloren", protokoll.output[0])
        self.assertIn("responder", protokoll.output[0])

    def test_leer_zu_leer_wird_ebenfalls_gemeldet(self) -> None:
        """Ein Schreiber ohne Inhalt wird gemeldet.

        Sonst ist er von einem, der gar nicht lief, nicht zu unterscheiden.
        """
        with self.assertLogs("ki_server.antwort_spur", level="ERROR"):
            antwort_setzen({"response": ""}, "", "responder")

    def test_falscher_typ_wird_gemeldet_und_nicht_durchgereicht(self) -> None:
        """Ein Typbruch wird gemeldet und nicht durchgereicht.

        Er liefe sonst bis zur Zustellung und sähe dort wie eine leere
        Antwort aus.
        """
        zustand: dict = {"response": "text"}
        with self.assertLogs("ki_server.antwort_spur", level="ERROR"):
            antwort_setzen(zustand, None, "thinker/korrektur")
        self.assertEqual("", zustand["response"])


class UmschlagTest(unittest.TestCase):
    """Die Anbieter-Antwort wird vor jeder Zuweisung protokolliert."""

    def test_umschlag_nennt_den_abbruchgrund(self) -> None:
        """`done_reason` ist das Feld, dessen Fehlen den Defekt offen liess."""
        antwort: dict = {
            "message": {"content": "Text", "thinking": ""},
            "done": True, "done_reason": "stop",
            "prompt_eval_count": 100, "eval_count": 20,
        }
        with self.assertLogs("ki_server.llm_provider", level="INFO") as protokoll:
            _antwort_umschlag_melden(antwort, "responder")
        zeile: str = protokoll.output[0]
        self.assertIn("done_reason='stop'", zeile)
        self.assertIn("eval_count=20", zeile)
        self.assertIn("content=4", zeile)

    def test_token_ohne_ausgabefeld_ist_ein_fehler_mit_rumpf(self) -> None:
        """Genau der Fall vom 19.08.2026: 243 Token, beide Felder leer."""
        antwort: dict = {
            "message": {"content": "", "thinking": None},
            "done": True, "done_reason": "stop",
            "prompt_eval_count": 6190, "eval_count": 243,
        }
        with self.assertLogs("ki_server.llm_provider", level="ERROR") as protokoll:
            _antwort_umschlag_melden(antwort, "responder")
        zeile: str = protokoll.output[-1]
        self.assertIn("243", zeile)
        self.assertIn("WEDER content NOCH thinking", zeile)
        self.assertIn("Rumpf:", zeile)

    def test_umschlag_liest_auch_das_pydantic_modell_des_clients(self) -> None:
        """Der Client liefert `ChatResponse`, kein Dict — gemessen am 19.08.2026.

        Die erste Fassung prüfte auf `dict`, meldete einen Vertragsbruch, wo
        keiner war, und verschluckte dabei genau den Umschlag, um
        dessentwillen sie gebaut ist. Der Zeuge fährt deshalb ein Modell mit
        `model_dump`, nicht ein Dict.
        """
        class _Modell:
            """Ein Doppel des Client-Objekts — kann `model_dump`, ist kein Dict."""

            @staticmethod
            def model_dump() -> dict:
                """Liefert die Felder, wie das Pydantic-Modell es tut."""
                return {
                    "message": {"content": "Antwort", "thinking": None},
                    "done": True, "done_reason": "stop",
                    "prompt_eval_count": 10, "eval_count": 3,
                }

        with self.assertLogs("ki_server.llm_provider", level="INFO") as protokoll:
            _antwort_umschlag_melden(_Modell(), "responder")
        zeile: str = protokoll.output[0]
        self.assertIn("done_reason='stop'", zeile)
        self.assertNotIn("Vertragsbruch", zeile)

    def test_umschlag_nennt_die_kanaele_der_nachricht(self) -> None:
        """Ein Kanal, den niemand liest, sieht aus wie eine leere Ausgabe.

        Der Parser des Modells legt die Ausgabe in Kanäle. Der Bestand liest
        `content` und `thinking`; kommt ein dritter hinzu, ist er ohne die
        Schlüsselliste unsichtbar.
        """
        antwort: dict = {
            "message": {"content": "", "thinking": "", "tool_calls": [{"x": 1}]},
            "done": True, "done_reason": "stop",
            "prompt_eval_count": 10, "eval_count": 40,
        }
        with self.assertLogs("ki_server.llm_provider", level="INFO") as protokoll:
            _antwort_umschlag_melden(antwort, "responder")
        self.assertIn("tool_calls", protokoll.output[0])
        # Und der Ausfall nennt sie ebenfalls — dort wird sie gebraucht.
        self.assertIn("tool_calls", protokoll.output[-1])

    def test_leere_kanaele_erscheinen_nicht(self) -> None:
        """Gemessen am 19.08.2026: `model_dump` liefert ALLE Felder.

        Beim Bestand sind das immer dieselben sechs, gleich was drinsteht.
        Eine Liste, die sich nie ändert, kann keinen Befund tragen — gezählt
        wird deshalb, was belegt ist.
        """
        antwort: dict = {
            "message": {
                "content": "Text", "role": "assistant",
                "thinking": None, "tool_calls": None,
                "images": None, "tool_name": None,
            },
            "done": True, "done_reason": "stop",
            "prompt_eval_count": 5, "eval_count": 2,
        }
        with self.assertLogs("ki_server.llm_provider", level="INFO") as protokoll:
            _antwort_umschlag_melden(antwort, "responder")
        zeile: str = protokoll.output[0]
        self.assertIn("kanaele=['content']", zeile)
        self.assertNotIn("tool_calls", zeile)
        self.assertNotIn("images", zeile)

    def test_fehlender_abbruchgrund_wird_benannt_statt_ersetzt(self) -> None:
        """Ein Vorgabewert an dieser Stelle sähe wie eine Meldung aus."""
        with self.assertLogs("ki_server.llm_provider", level="INFO") as protokoll:
            _antwort_umschlag_melden({"message": {"content": "x"}}, "responder")
        self.assertIn("(nicht gemeldet)", protokoll.output[0])


if __name__ == "__main__":
    unittest.main()
