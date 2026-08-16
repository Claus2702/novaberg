"""Zeugen dafuer, dass die Zwischen-Destillation eine eigene Frist traegt.

**Gemessen, nicht gewaehlt** (16.08.2026). `zwischen_destillieren` nannte
keine Frist und fiel damit auf den Worker-Vorgabewert
`MODEL_BACKGROUND_TIMEOUT_S = 300` zurueck. Ueber 24 h, 190 Antworten des
Aufrufs `recherche/zwischen`:

    Groesse             Wert
    Median              181 s
    p90                 314 s
    Maximum             638 s
    Ausgabe-Token       Median 1330 · p90 2425 · Maximum 4176

**24 der 190 Antworten (12 %) trafen nach dem Fristablauf ein.** Das Modell
hatte gerechnet und geantwortet, nur hatte der Aufrufer schon aufgegeben —
die Frist beendet allein das Warten, nicht die Ausfuehrung. Der
belegte Platz blieb belegt, das Ergebnis wurde verworfen.

**Der Schaden lag in der Auswahl, nicht im einzelnen Aufruf.** Ein
Fehlversuch loescht den Queue-Eintrag nach drei Laeufen **hart**
(`versuch_zaehlen` → `DELETE`), waehrend der Verfall ihn nur weich
deaktiviert und weckbar laesst. Und die Fehlversuche trafen die Wichtigen:
Ueber die 582 aktiven `recherche`-Eintraege stieg die mittlere
`salienz_roh` monoton mit der Zahl der Versuche —

    versuche    n      salienz_roh
    0           539    0,867
    1            27    0,947
    2            16    0,990

— weil der Wichtigste zuerst gezogen wird, das meiste Material hat und
deshalb als erster in die Frist laeuft. Sechzehn Eintraege standen einen
Fehllauf vor der Loeschung.

**Drei Zeugen, und der dritte ist der, der den Defekt gefunden haette.** Die
beiden ersten pruefen die Werte; der dritte prueft am Syntaxbaum, dass die
Aufrufstelle sie ueberhaupt **liest**. Eine Konfiguration ohne Leser ist in
diesem Bestand eine belegte Fehlerklasse, und `NODE_LLM_CONFIG["recherche"]`
ist genau das: vorhanden, vollstaendig, von niemandem gerufen.
"""

import ast
import unittest
from pathlib import Path

from config import get_node_config

_AUFRUFSTELLE: Path = (
    Path(__file__).resolve().parent.parent / "agents" / "recherche" / "destillation.py"
)

# Groesste beobachtete Dauer und groesste beobachtete Ausgabe, 16.08.2026.
_GEMESSENES_MAXIMUM_S:      int = 638
_GEMESSENES_MAXIMUM_TOKEN:  int = 4176


class FristDerZwischenDestillationTest(unittest.TestCase):
    """Die beiden Obergrenzen des Aufrufs, je gegen ihre Messung."""

    def test_die_frist_traegt_den_laengsten_beobachteten_lauf(self) -> None:
        """300 s waeren ein Abbruch mitten in einer gelingenden Antwort.

        Die Frist muss ueber dem beobachteten Maximum liegen und nicht ueber
        dem Median: Ein Abbruch dauert dieselbe Zeit wie der Lauf und liefert
        nichts — er ist der teurere Fehler.
        """
        self.assertGreater(
            get_node_config("recherche_zwischen")["timeout_s"],
            _GEMESSENES_MAXIMUM_S,
            "Die Frist der Zwischen-Destillation liegt unter dem groessten "
            "gemessenen Lauf — der Aufruf bricht ab, der Eintrag verliert "
            "einen Versuch, und nach dreien wird er hart geloescht",
        )

    def test_der_token_deckel_schneidet_die_groesste_antwort_nicht(self) -> None:
        """Ein abgeschnittener Text sieht aus wie ein fertiger.

        Der Deckel ist eine Obergrenze gegen den Ausreisser, kein Mittel zur
        Verdichtung. Liegt er unter dem beobachteten Bedarf, entsteht ein
        mitten im Wort endender Faktentext ohne Fehler und ohne Meldung.
        """
        self.assertGreater(
            get_node_config("recherche_zwischen")["max_output_tokens"],
            _GEMESSENES_MAXIMUM_TOKEN,
            "Der Token-Deckel liegt unter der groessten gemessenen Antwort — "
            "die Zwischenzusammenfassung wird stillschweigend abgeschnitten",
        )

    def test_frist_und_deckel_stehen_als_paar(self) -> None:
        """Der Deckel muss innerhalb der Frist erreichbar sein.

        Beide Werte begrenzen denselben Aufruf von zwei Seiten. Ein Deckel,
        der bei der gemessenen Rate laenger braucht als die Frist erlaubt,
        ist wirkungslos — die Frist schlaegt vorher zu, und der Aufruf endet
        wieder im Abbruch statt an seiner Obergrenze.
        """
        cfg = get_node_config("recherche_zwischen")
        # Gemessen am 16.08.2026 ueber 196 Laeufe: rund 7,3 Token/s auf dem
        # CPU-Backend. Konservativ mit 6,0 gerechnet, damit der Zeuge nicht
        # bei normaler Schwankung des Durchsatzes anschlaegt.
        benoetigte_sekunden: float = cfg["max_output_tokens"] / 6.0
        self.assertLess(
            benoetigte_sekunden, cfg["timeout_s"],
            "Der Token-Deckel ist innerhalb der Frist nicht erreichbar — "
            "die beiden Werte widersprechen sich",
        )


class DieAufrufstelleLiestDieKonfigurationTest(unittest.TestCase):
    """Am Syntaxbaum: Die Werte stehen nicht nur da, sie werden uebergeben."""

    def _der_aufruf(self) -> ast.Call:
        """Findet den `submit_sync`-Aufruf mit `caller="recherche/zwischen"`."""
        baum = ast.parse(
            _AUFRUFSTELLE.read_text(encoding="utf-8"), filename=str(_AUFRUFSTELLE)
        )
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            if getattr(knoten.func, "attr", "") != "submit_sync":
                continue
            for arg in knoten.args:
                if not isinstance(arg, ast.Call):
                    continue
                for schluessel in arg.keywords:
                    if (
                        schluessel.arg == "caller"
                        and isinstance(schluessel.value, ast.Constant)
                        and schluessel.value.value == "recherche/zwischen"
                    ):
                        return knoten
        self.fail(
            f"Kein submit_sync-Aufruf mit caller='recherche/zwischen' in "
            f"{_AUFRUFSTELLE} — die Aufrufstelle wurde umbenannt oder entfernt"
        )

    def test_der_aufruf_nennt_eine_eigene_frist(self) -> None:
        """Ohne `timeout=` gilt wieder der Vorgabewert des Workers.

        Das ist der Zustand, der den Defekt getragen hat: Die Zahl in der
        Konfiguration ist richtig, und niemand liest sie. Genau deshalb steht
        dieser Zeuge am Syntaxbaum und nicht auf dem Wert.
        """
        namen = {s.arg for s in self._der_aufruf().keywords}
        self.assertIn(
            "timeout", namen,
            "Die Aufrufstelle uebergibt kein `timeout` — sie faellt auf "
            "MODEL_BACKGROUND_TIMEOUT_S zurueck, und die Konfiguration "
            "`recherche_zwischen` waere eine Deklaration ohne Leser",
        )

    def test_der_aufruf_reicht_den_token_deckel_durch(self) -> None:
        """Ohne `max_output_tokens` bleibt `num_predict` ungesetzt.

        Dann ist die Ausgabe unbegrenzt — gemessen wurden 4176 Token, wo der
        Prompt um hoechstens 2000 bittet. Ein Prompt bittet, ein Parameter
        haelt.
        """
        argumente = self._der_aufruf().args
        self.assertTrue(argumente, "submit_sync ohne Request-Argument")
        namen = {
            s.arg for s in argumente[0].keywords
            if isinstance(argumente[0], ast.Call)
        }
        self.assertIn(
            "max_output_tokens", namen,
            "Die Aufrufstelle uebergibt kein `max_output_tokens` — die "
            "Ausgabelaenge bleibt unbegrenzt und der Deckel wirkungslos",
        )


if __name__ == "__main__":
    unittest.main()
