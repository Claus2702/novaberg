"""Struktur-Zeugen ueber `config.py` und den Produktivbaum.

Ziel: Eine Konstante, die zweimal zugewiesen wird, sieht an der ersten
Stelle aus wie eine Deklaration und ist keine. Python nimmt die zweite,
ohne ein Wort — und **kein Werkzeug meldet es**: Ruffs `F811` deckt
Importe, Funktionen und Klassen, nicht das erneute Binden einer
Modulvariablen.

Die Zusicherungen:

  1. **Kein Modulname wird im Produktivcode zweimal zugewiesen.** Der Zeuge
     laeuft ueber den ganzen Baum und nicht nur ueber `config.py`: Der Fall,
     den er aufdeckte, war dort — die Klasse ist es nicht.
  2. **Die Druck-Teilmenge liegt im Kanon.** Sonst prueft der Nachfragen-Weg
     gegen eine Menge, aus der sein eigenes Kriterium herausfaellt.
  3. **Beide Lesearten des Kanons tragen.** Er wird auf Zugehoerigkeit
     geprueft und als Text nachgeschlagen; ein Woerterbuch kann beides, ein
     `frozenset` nur das erste.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import os
import unittest
from collections import Counter
from pathlib import Path

from config import EMOTIONS_VEKTOREN, EMOTIONS_VEKTOREN_DRUCK, EMOTIONS_VEKTOREN_NOVA

#: Die Wurzel des Produktivbaums — dieselbe, die auch die Codepruefungen
#: ablaufen. `tests/` steht nicht darin: Ein Zeuge, der sich selbst prueft,
#: verengt seinen Gegenstand auf sich.
SERVER: Path = Path(__file__).resolve().parent.parent


def _namen_eines_ziels(ziel: ast.expr) -> list[str]:
    """Die Namen, die ein Zuweisungsziel bindet — auch beim Entpacken.

    Vorbedingung: `ziel` ist der linke Teil einer Zuweisung.
    Nachbedingung: Die gebundenen Namen. `a, b = …` bindet zwei, `obj.feld = …`
    keinen (das ist eine Zuweisung an ein Attribut, keine Deklaration),
    `a[0] = …` ebenfalls keinen.
    """
    if isinstance(ziel, ast.Name):
        return [ziel.id]
    if isinstance(ziel, (ast.Tuple, ast.List)):
        return [n for teil in ziel.elts for n in _namen_eines_ziels(teil)]
    if isinstance(ziel, ast.Starred):
        return _namen_eines_ziels(ziel.value)
    return []


def _doppelte_modulnamen(datei: Path) -> dict[str, list[int]]:
    """Nennt die Namen, die auf Modulebene mehr als einmal zugewiesen werden.

    Vorbedingung: `datei` ist lesbarer Python-Quelltext.
    Nachbedingung: Abbildung Name → Zeilennummern, leer wenn keiner doppelt
    ist.

    **Was gezaehlt wird, und was ausdruecklich nicht.** Die erste Fassung
    fragte `hasattr(knoten, "target")` — und dieses Feld tragen vier
    Knotentypen, nicht einer: `AnnAssign`, `AugAssign`, `For` und `AsyncFor`.
    Damit meldete sie zwei legitime Bauarten als Doppeldeklaration: zwei
    Schleifen auf Modulebene mit derselben Laufvariablen, und ein `X += 1`
    nach `X = 1`. Gefunden von einer Nachpruefung, die nicht die gemeinte
    Menge nachbaute, sondern die Grammatik abfragte.

    | Form | gezaehlt | Grund |
    |---|---|---|
    | `X = …`, auch `a, b = …` | ja | eine Deklaration |
    | `X: T = …` | ja | dieselbe mit Typangabe |
    | `X += …` | **nein** | eine Fortschreibung, keine zweite Deklaration |
    | `for X in …:` | **nein** | eine Laufvariable |
    | `if …: X = a` / `else: X = b` | **nein** | eine gewollte Fallunterscheidung |
    | `global X` in einer Funktion | **nein** | ein Puffer, kein Kanon |
    | `globals()["X"] = …` | **nein** | zur Laufzeit, nicht statisch lesbar |

    **Die letzten drei Zeilen sind Grenzen und kein Versehen.** Ein Zeuge,
    der eine Fallunterscheidung meldet, wird bei der ersten legitimen
    Bauart abgeschaltet — und damit auch fuer den Fall, fuer den er da ist.
    Heute im Produktivcode: 3 bedingte Zuweisungen, 2 `global`-Bindungen,
    0 ueber `globals()`.
    """
    baum = ast.parse(datei.read_text(encoding="utf-8"))
    namen: list[tuple[str, int]] = []
    for knoten in baum.body:
        if isinstance(knoten, ast.Assign):
            ziele: list[ast.expr] = list(knoten.targets)
        elif isinstance(knoten, ast.AnnAssign):
            ziele = [knoten.target]
        else:
            continue
        for ziel in ziele:
            namen.extend((name, knoten.lineno) for name in _namen_eines_ziels(ziel))
    zaehler = Counter(name for name, _ in namen)
    return {
        name: [zeile for treffer, zeile in namen if treffer == name]
        for name, anzahl in zaehler.items() if anzahl > 1
    }


class DoppeldeklarationTest(unittest.TestCase):
    """Der Zeuge, den es am 23.08.2026 noch nicht gab."""

    def test_kein_modulname_wird_zweimal_zugewiesen(self) -> None:
        """Die erste Zuweisung ist toter Text, der wie eine Regel aussieht.

        `EMOTIONS_VEKTOREN` stand in `config.py` zweimal — Zeile 918 als
        `frozenset`, Zeile 1007 als `dict`, beide mit denselben neun Namen.
        **Folgenlos, weil die Mengen sich deckten**, und genau deshalb
        haette der naechste Zusatz an der falschen Haelfte nichts bewirkt.
        """
        befunde: dict[str, dict[str, list[int]]] = {}
        geprueft: int = 0
        for pfad in sorted(SERVER.rglob("*.py")):
            text: str = str(pfad)
            if "__pycache__" in text or f"{os.sep}tests{os.sep}" in text:
                continue
            geprueft += 1
            doppelt = _doppelte_modulnamen(pfad)
            if doppelt:
                befunde[str(pfad.relative_to(SERVER))] = doppelt

        self.assertGreater(geprueft, 100, "Der Zeuge muss den Baum wirklich sehen")
        self.assertEqual(
            befunde, {},
            f"Doppelt zugewiesene Modulnamen ({geprueft} Dateien geprüft): {befunde}",
        )


class ZaehlformTest(unittest.TestCase):
    """Der Zeuge über den Zeugen — was `_doppelte_modulnamen` zählt.

    Die Tabelle in seinem Docstring ist sonst eine Behauptung. Jede Zeile
    steht hier als Fall; zwei davon waren bis zum 23.08.2026 falsch.
    """

    def _probe(self, quelle: str) -> dict[str, list[int]]:
        """Schickt Quelltext durch die echte Funktion, über eine Datei."""
        import tempfile

        with tempfile.NamedTemporaryFile(
            "w", suffix=".py", delete=False, encoding="utf-8",
        ) as datei:
            datei.write(quelle)
            pfad = Path(datei.name)
        try:
            return _doppelte_modulnamen(pfad)
        finally:
            pfad.unlink()

    def test_zwei_zuweisungen_werden_gemeldet(self) -> None:
        """Der Fall, für den der Zeuge da ist."""
        self.assertEqual(
            self._probe("K = frozenset({1})\nK = {1: 'a'}\n"), {"K": [1, 2]},
        )

    def test_entpacken_wird_gesehen(self) -> None:
        """`a, b = …` bindet zwei Namen — die erste Fassung sah keinen."""
        self.assertEqual(
            self._probe("A, B = 1, 2\nA, C = 3, 4\n"), {"A": [1, 2]},
        )

    def test_laufvariable_ist_keine_deklaration(self) -> None:
        """Zwei Schleifen auf Modulebene sind kein Defekt.

        Die erste Fassung meldete sie, weil `ast.For` dasselbe Feld `target`
        trägt wie `ast.AnnAssign`. Im Baum steht heute **eine** solche
        Schleife (`utils/zeitparser.py`); die zweite hätte die Suite rot
        gemacht, ohne dass etwas falsch wäre.
        """
        self.assertEqual(
            self._probe("for _k in (1,):\n    pass\nfor _k in (2,):\n    pass\n"), {},
        )

    def test_fortschreibung_ist_keine_zweite_deklaration(self) -> None:
        """`X += 1` schreibt fort, es deklariert nicht neu."""
        self.assertEqual(self._probe("X = 1\nX += 1\n"), {})

    def test_fallunterscheidung_bleibt_still(self) -> None:
        """`if/else` ist eine gewollte Bauart und keine Doppeldeklaration."""
        self.assertEqual(
            self._probe("if True:\n    K = 1\nelse:\n    K = 2\n"), {},
        )

    def test_attribut_und_index_binden_keinen_namen(self) -> None:
        """`obj.feld = …` und `a[0] = …` deklarieren nichts."""
        self.assertEqual(
            self._probe("import os\nos.x = 1\nos.x = 2\n"), {},
        )


class KanonTest(unittest.TestCase):
    """Was der Kanon zusichert, seit er nur noch einmal dasteht."""

    def test_die_druck_teilmenge_liegt_im_kanon(self) -> None:
        """Sonst prüft der Nachfragen-Weg gegen eine Menge ohne sein Kriterium."""
        self.assertTrue(
            set(EMOTIONS_VEKTOREN_DRUCK) <= set(EMOTIONS_VEKTOREN),
            f"außerhalb: {sorted(set(EMOTIONS_VEKTOREN_DRUCK) - set(EMOTIONS_VEKTOREN))}",
        )

    def test_beide_lesearten_tragen(self) -> None:
        """Zugehörigkeit **und** Nachschlagen — ein `frozenset` könnte nur eins.

        Die beiden Produktivleser tun genau das: `agents/nachfragen/agent.py`
        prüft `in`, `graph/nodes/responder.py` prüft `in` und schlägt dann
        den Text nach.
        """
        for name in EMOTIONS_VEKTOREN:
            with self.subTest(vektor=name):
                self.assertIn(name, EMOTIONS_VEKTOREN)
                self.assertTrue(EMOTIONS_VEKTOREN[name].strip())

    def test_ein_unbekannter_wert_faellt_heraus(self) -> None:
        """Die Gegenprobe — sonst prüfte die Zugehörigkeit nichts."""
        self.assertNotIn("gibtsnicht", EMOTIONS_VEKTOREN)

    def test_novas_kanon_deckt_sich_mit_dem_des_nutzers(self) -> None:
        """Beide Perspektiven kennen dieselben Vektoren.

        Sie sind absichtlich getrennt kalibriert (der Text unterscheidet
        sich), aber ein Vektor, den nur eine Seite kennt, wäre auf der
        anderen ein stiller Ausfall: Der Block entfiele ohne Meldung.
        """
        self.assertEqual(
            set(EMOTIONS_VEKTOREN), set(EMOTIONS_VEKTOREN_NOVA),
            "Ein Vektor, den nur eine Perspektive kennt, entfällt auf der "
            "anderen ohne Meldung",
        )


if __name__ == "__main__":
    unittest.main()
