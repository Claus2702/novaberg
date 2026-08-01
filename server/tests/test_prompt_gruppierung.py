"""Tests: der Empfangszeitpunkt einer Nutzeraeusserung wird vor der Verarbeitung genommen.

Die Ereignis-Nutzlast trug bisher nur `erstellt_am` — den Zeitpunkt, zu dem das
Ereignis in die Queue ging, also **nach** Pfad 1. Zwischen Empfang und
Ereignis liegen 11 bis 13 Sekunden (Perzeption und Salienz), und die zweite
Nachricht wartet in dieser Zeit am `llm_lock`. Ein Fenster, das auf
`erstellt_am` rechnet, misst deshalb die Traegheit des Systems mit und nicht
den Abstand zwischen zwei Aeusserungen.

`empfangen_am` ist die einzige Groesse, die diesen Abstand misst. Sie wird als
erste Anweisung des Endpunkts genommen — vor jeder Verarbeitung, vor jedem
Modellaufruf.

Zeugen dieser Datei:
  * Der Zeitpunkt selbst wird gegen eine Uhr geprueft, die der Test haelt —
    nicht gegen einen Wert, den derselbe Aufruf erzeugt hat.
  * Dass er **vor** der Verarbeitung genommen wird, ist eine Aussage ueber die
    Struktur des Endpunkts. Sie wird deshalb am Syntaxbaum geprueft: Die
    Zuweisung steht vor dem ersten Aufruf, der ein Modell beschaeftigt. Ein
    Test ueber den Wert allein koennte das nicht sehen — eine spaeter genommene
    Uhr liefert ebenfalls eine plausible Zahl.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import json
import time
import unittest
from unittest.mock import MagicMock

import api.chat as chat_mod

# Aufrufe, die ein Modell beschaeftigen oder den Zustand aufbauen. Steht die
# Zeitnahme dahinter, misst sie nicht mehr den Empfang.
VERARBEITUNG: frozenset[str] = frozenset({
    "create_state", "invoke", "stream", "_stream_oder_abbruch",
    "_user_entitaet_sicherstellen", "nachricht_einreihen",
})


class EmpfangszeitInDerNutzlastTest(unittest.TestCase):
    """Die Nutzlast traegt den Empfang, nicht nur die Ereigniszeit."""

    def test_nutzlast_traegt_empfangen_am(self) -> None:
        """Ohne das Feld hat die Gruppierung keine Bezugsgroesse."""
        nutzlast: dict = chat_mod._ereignis_nutzlast(
            "t-1", 1_754_000_000.0, "Wie entsteht ein Gammablitz?", {},
        )

        self.assertEqual(nutzlast["empfangen_am"], 1_754_000_000.0)

    def test_empfangen_am_ist_eine_zahl(self) -> None:
        """Eine Zeichenkette laesst sich nicht subtrahieren."""
        nutzlast: dict = chat_mod._ereignis_nutzlast("t-1", 1_754_000_000.0, "x", {})

        self.assertIsInstance(nutzlast["empfangen_am"], float)

    def test_wert_ueberlebt_die_json_runde(self) -> None:
        """Die Nutzlast reist als JSON durch Redis."""
        nutzlast: dict = chat_mod._ereignis_nutzlast("t-1", 1_754_000_000.5, "x", {})

        wieder: dict = json.loads(json.dumps(nutzlast, ensure_ascii=False))
        self.assertEqual(wieder["empfangen_am"], 1_754_000_000.5)

    def test_die_uebrigen_felder_bleiben(self) -> None:
        """Charakterisierung: der Vertrag von vor der Erweiterung."""
        nutzlast: dict = chat_mod._ereignis_nutzlast("t-1", 1.0, "Frage?", {})

        self.assertEqual(nutzlast["turn_id"], "t-1")
        self.assertEqual(nutzlast["user_prompt"], "Frage?")
        self.assertIsNone(nutzlast["salienz_human"])
        self.assertEqual(nutzlast["user_intentionen"], [])
        self.assertNotIn("pfad1_ausfall", nutzlast)

    def test_der_ausfallvermerk_bleibt_bedingt(self) -> None:
        """Ein dauerhaftes leeres Feld waere ein stiller Default."""
        aussen = MagicMock()
        aussen.emotion.emotion = "neugier"

        nutzlast: dict = chat_mod._ereignis_nutzlast(
            "t-1", 1.0, "Frage?", {"external": aussen}, "TimeoutError: ",
        )

        self.assertEqual(nutzlast["pfad1_ausfall"], "TimeoutError: ")
        self.assertEqual(nutzlast["current_emotion"], "neugier")


class ZeitnahmeStehtVorDerVerarbeitungTest(unittest.TestCase):
    """Die Verdrahtung ist der Zeuge — ein spaeter genommener Wert sieht gleich aus.

    Geprueft wird am Syntaxbaum, nicht am Ergebnis: Eine Uhr, die nach der
    Perzeption gestartet wird, liefert eine ebenso plausible Zahl und waere
    ueber den Wert nicht von der richtigen zu unterscheiden.
    """

    def _funktion(self, name: str) -> ast.FunctionDef:
        """Holt den Syntaxbaum einer Funktion aus dem Chat-Modul."""
        baum: ast.Module = ast.parse(inspect.getsource(chat_mod))

        for knoten in ast.walk(baum):
            ist_funktion: bool = isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef))
            if ist_funktion and knoten.name == name:
                return knoten

        self.fail(f"Funktion '{name}' nicht gefunden")

    def _zeile_der_zeitnahme(self, funktion: ast.FunctionDef) -> int:
        """Zeilennummer der Zuweisung an `empfangen_am`."""
        for knoten in ast.walk(funktion):
            if not isinstance(knoten, (ast.Assign, ast.AnnAssign)):
                continue
            ziele = knoten.targets if isinstance(knoten, ast.Assign) else [knoten.target]
            for ziel in ziele:
                if isinstance(ziel, ast.Name) and ziel.id == "empfangen_am":
                    return knoten.lineno

        self.fail("Keine Zuweisung an 'empfangen_am' gefunden")
        return 0

    def _erste_verarbeitungszeile(self, funktion: ast.FunctionDef) -> int:
        """Zeilennummer des ersten Aufrufs, der etwas verarbeitet."""
        zeilen: list[int] = []

        for knoten in ast.walk(funktion):
            if not isinstance(knoten, ast.Call):
                continue
            name: str = ""
            if isinstance(knoten.func, ast.Name):
                name = knoten.func.id
            elif isinstance(knoten.func, ast.Attribute):
                name = knoten.func.attr
            if name in VERARBEITUNG:
                zeilen.append(knoten.lineno)

        self.assertTrue(zeilen, "Kein Verarbeitungsaufruf gefunden — Test blind")
        return min(zeilen)

    def test_synchroner_endpunkt_nimmt_die_zeit_zuerst(self) -> None:
        """Der Endpunkt, den der Telegram-Bot benutzt."""
        funktion: ast.FunctionDef = self._funktion("ChatSenden")

        self.assertLess(
            self._zeile_der_zeitnahme(funktion),
            self._erste_verarbeitungszeile(funktion),
        )

    def test_streamender_endpunkt_nimmt_die_zeit_zuerst(self) -> None:
        """Der Endpunkt, den der Desktop-Client benutzt.

        Geprueft wird die aeussere Funktion, nicht der Generator: Die Zeitnahme
        gehoert vor die Entitaetspruefung, und der Generator laeuft ohnehin
        erst, wenn der Client zu lesen beginnt.
        """
        funktion: ast.FunctionDef = self._funktion("ChatStreamSenden")

        self.assertLess(
            self._zeile_der_zeitnahme(funktion),
            self._erste_verarbeitungszeile(funktion),
        )

    def test_beide_endpunkte_reichen_die_zeit_weiter(self) -> None:
        """Positiver Zwilling: genommen und auch uebergeben, nicht nur genommen.

        Seit Pfad 1 hinter der Eingangs-Queue laeuft, geht die Zeit nicht mehr
        direkt in die Ereignis-Nutzlast, sondern ueber die Einreihung: Beide
        Endpunkte bauen eine `EingehendeNachricht` mit ihr.
        """
        baum: ast.Module = ast.parse(inspect.getsource(chat_mod))

        weitergaben: int = sum(
            1
            for knoten in ast.walk(baum)
            if isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id == "EingehendeNachricht"
            and any(
                isinstance(arg, ast.Name) and arg.id == "empfangen_am"
                for arg in knoten.args
            )
        )

        self.assertEqual(weitergaben, 2)


class DieUhrLaeuftVorwaertsTest(unittest.TestCase):
    """Der Zeuge ist eine Uhr ausserhalb des Pruefobjekts."""

    def test_wert_liegt_zwischen_zwei_eigenen_messungen(self) -> None:
        """Ein erfundener oder eingefrorener Wert faellt hier durch."""
        vorher: float = time.time()
        nutzlast: dict = chat_mod._ereignis_nutzlast("t-1", time.time(), "x", {})
        nachher: float = time.time()

        self.assertGreaterEqual(nutzlast["empfangen_am"], vorher)
        self.assertLessEqual(nutzlast["empfangen_am"], nachher)


if __name__ == "__main__":
    unittest.main()
