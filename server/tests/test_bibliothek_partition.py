"""Zeugen ueber die Partition der Bibliothek — drei Spalten, nicht zwei.

Ziel: `autonomous_wissen` traegt die Paar-Partition dreispaltig — `user_id`
(der Mensch), `character_id` (die Figur), `beobachter` (wer die Zeile
geschrieben hat). Bis zum 23.08.2026 filterten **alle vier** Lesepfade nur auf
die ersten beiden.

**Folgenlos, und genau deshalb gefaehrlich.** Heute schreiben allein die
Hintergrund-Agenten; gemessen am 23.08.2026 tragen **831 von 831** aktiven
Zeilen `beobachter='assistant'`. (Der Befund nannte 274 — das war der Stand
vom 19.08.2026, und die Zahl war beim Bauen unbesehen mitgewandert.)

Kommt ein zweiter Schreiber dazu, erscheinen fremde Zeilen als Novas eigene
Ausarbeitung — und **nichts schlaegt an**: Eine Trefferliste, die zu viel
enthaelt, sieht aus wie eine Bibliothek mit Bestand.

Die Zusicherungen:

  1. **Jede Abfrage gegen `autonomous_wissen`, die auf das Paar filtert,
     filtert dreispaltig.** Der Zeuge laeuft als **Kriterium ueber den Baum**
     und nicht als Aufzaehlung der vier bekannten Stellen: Der Befund nannte
     zwei, die Suche fand vier. Eine fuenfte, die morgen dazukommt, ist damit
     mitgeprueft.
  2. **`Bibliotheksfrage` verlangt die Perspektive.** Sie hat keinen Default —
     ein Pflichtfeld hat keinen (11_EVA §5).
  3. **Ein Wert ausserhalb des Kanons wird laut abgelehnt**, nicht auf
     `assistant` zurechtgebogen. Geprueft wird gegen `BEOBACHTER_KANON` und
     nicht gegen den einen erwarteten Wert — sonst waere ein unbekannter Wert
     von einem gueltigen zweiten nicht zu unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import os
import re
import unittest
from pathlib import Path

from config import BEOBACHTER_KANON
from memory.repositories.autonomous_wissen_repository import (
    BIBLIOTHEK_BEOBACHTER,
    Bibliotheksfrage,
)

#: Die Wurzel des Produktivbaums; `tests/` steht nicht darin.
SERVER: Path = Path(__file__).resolve().parent.parent

#: Die Tabelle, deren Partition dieser Zeuge bewacht.
TABELLE: str = "autonomous_wissen"

#: Woran eine Abfrage erkannt wird, die auf das Paar filtert. Nicht am
#: Vorkommen des Tabellennamens allein: Ein `INSERT` nennt ihn auch, und ein
#: Kommentar ebenfalls.
PAARFILTER: re.Pattern = re.compile(r"user_id\s*=\s*%s", re.IGNORECASE)


def _sql_literale(datei: Path) -> list[tuple[int, str]]:
    """Die Zeichenketten-Literale einer Datei, mit ihrer Zeile.

    Vorbedingung: `datei` ist lesbarer Python-Quelltext.
    Nachbedingung: Liste aus (Zeile, Inhalt). Nebeneinanderstehende Literale
    (`"SELECT …" "WHERE …"`) fasst der Parser bereits zu **einem** Knoten
    zusammen — genau die Bauart, in der die Abfragen hier stehen; ein Zeuge,
    der zeilenweise suchte, saehe `WHERE user_id = %s` ohne sein `FROM`.
    """
    baum = ast.parse(datei.read_text(encoding="utf-8"))
    return [
        (knoten.lineno, knoten.value)
        for knoten in ast.walk(baum)
        if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str)
    ]


def _zweispaltige_abfragen() -> list[str]:
    """Nennt jede Abfrage auf die Bibliothek, die den Beobachter auslaesst.

    Vorbedingung: keine.
    Nachbedingung: Liste aus `pfad:zeile`, leer wenn jede Abfrage dreispaltig
    filtert.

    **Die Unterscheidung, die der Zeuge treffen muss:** Eine Abfrage, die gar
    nicht auf das Paar filtert (ein `INSERT`, ein Zugriff ueber die `id`), ist
    kein Befund — sie partitioniert nicht und kann die Partition nicht
    verletzen. Gesucht ist die Abfrage, die **zwei Drittel** der Partition
    nennt.
    """
    befunde: list[str] = []
    for pfad in sorted(SERVER.rglob("*.py")):
        text: str = str(pfad)
        if "__pycache__" in text or f"{os.sep}tests{os.sep}" in text:
            continue
        for zeile, inhalt in _sql_literale(pfad):
            if TABELLE not in inhalt:
                continue
            if not PAARFILTER.search(inhalt):
                continue
            if "beobachter" in inhalt:
                continue
            befunde.append(f"{pfad.relative_to(SERVER)}:{zeile}")
    return befunde


class PartitionsfilterTest(unittest.TestCase):
    """Zusicherung 1 — das Kriterium ueber den Baum."""

    def test_jede_bibliotheksabfrage_filtert_dreispaltig(self) -> None:
        """Vier Stellen waren es am 23.08.2026, der Befund nannte zwei.

        `suchen` und `zaehlen` im Repository, der Vorcheck im Enricher und die
        Kandidatenauswahl des Rueckwegs. Die letzten beiden fand erst die
        Suche — das ist der Grund, warum dieser Zeuge ein Kriterium ist.
        """
        befunde: list[str] = _zweispaltige_abfragen()
        self.assertEqual(
            befunde, [],
            f"Abfragen auf `{TABELLE}` ohne `beobachter`: {befunde}",
        )

    def test_der_zeuge_sieht_die_abfragen_ueberhaupt(self) -> None:
        """Ein leerer Grep ist kein Nachweis der Abwesenheit (22_STILLE_FEHLER).

        Ohne diese Probe waere Zusicherung 1 auch dann gruen, wenn das Muster
        nicht mehr passt oder der Baum nicht gefunden wird.
        """
        gefunden: int = 0
        for pfad in sorted(SERVER.rglob("*.py")):
            text: str = str(pfad)
            if "__pycache__" in text or f"{os.sep}tests{os.sep}" in text:
                continue
            for _, inhalt in _sql_literale(pfad):
                if TABELLE in inhalt and PAARFILTER.search(inhalt):
                    gefunden += 1
        self.assertGreaterEqual(
            gefunden, 4,
            f"Der Zeuge findet nur {gefunden} paargefilterte Abfragen auf "
            f"`{TABELLE}` — am 23.08.2026 waren es 4",
        )


class BibliotheksfrageTest(unittest.TestCase):
    """Zusicherungen 2 und 3 — die Perspektive am Eingang."""

    def _frage(self, beobachter: str) -> Bibliotheksfrage:
        """Eine vollstaendige Frage, bis auf die Perspektive."""
        return Bibliotheksfrage(
            postgres_url = "postgresql://ungenutzt",
            user_id      = "meister",
            character_id = "nova",
            beobachter   = beobachter,
            vektor_str   = "[0.0]",
            typ          = "wissen",
            schwelle     = 0.5,
            limit        = 3,
        )

    def test_die_perspektive_ist_ein_pflichtfeld(self) -> None:
        """Ein Pflichtfeld hat keinen Default (11_EVA §5).

        Stuende hier einer, waere der Defekt zurueck: Ein Aufrufer, der die
        Perspektive nicht kennt, bekaeme lautlos die eine, die heute stimmt.
        """
        with self.assertRaises(TypeError):
            Bibliotheksfrage(                       # type: ignore[call-arg]
                postgres_url = "postgresql://ungenutzt",
                user_id      = "meister",
                character_id = "nova",
                vektor_str   = "[0.0]",
                typ          = "wissen",
                schwelle     = 0.5,
                limit        = 3,
            )

    def test_die_gelesene_perspektive_liegt_im_kanon(self) -> None:
        """Sonst prueft die Suche gegen einen Wert, den es nicht geben darf."""
        self.assertIn(BIBLIOTHEK_BEOBACHTER, BEOBACHTER_KANON)

    def test_ein_fremder_beobachter_wird_laut_abgelehnt(self) -> None:
        """Nicht zurechtgebogen — die Ablehnung nennt den Wert und den Kanon.

        Die Pruefung laeuft vor jedem Verbindungsaufbau; die unbrauchbare
        `postgres_url` ist deshalb kein Hindernis und zugleich der Beleg,
        dass die Validierung wirklich zuerst kommt.
        """
        from memory.repositories.autonomous_wissen_repository import (
            AutonomousWissenRepository,
        )

        with self.assertRaises(ValueError) as fall:
            AutonomousWissenRepository.suchen(self._frage("beobachter_x"))
        self.assertIn("beobachter_x", str(fall.exception))
        self.assertIn("Kanon", str(fall.exception))


if __name__ == "__main__":
    unittest.main()
