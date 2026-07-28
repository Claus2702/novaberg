"""Tests: Jeder Gespraechsmodus, den die Perzeption liefern darf, wird gerechnet.

Ziel: Kein Modus faellt im GV-Pfad stillschweigend auf den Wert von "alltag".

Hintergrund (Chat 114, GV-Audit): Die Perzeption darf zehn Modi liefern, die
Tabellen des GV-Pfads kannten fuenf. Die fehlenden fuenf — philosophischer_
austausch, lernmodus, kreativ, beratend, berichtend — fielen auf den Default
0.3, denselben Wert, den "alltag" legitim traegt. Gemessen: 33 von 45 Laeufen
mit T=0(0.30), waehrend Novas Live-Modus `philosophischer_austausch` war. Aus
dem Log war ein echter Alltag von einer Vokabular-Luecke nicht zu unterscheiden.

Der Zeuge dieser Datei ist die Prompt-Datei: Sie legt fest, was das LLM liefern
DARF, und sie ist keine Ableitung aus dem Code, der hier geprueft wird. Die
Erwartung "philosophischer Austausch ist tief" stammt aus dem Konzept
(novaberg-gv-strategie_k.md §6.2, Sektor 24 "Philosophie-Cafe" mit T=tief),
nicht aus der Tabelle, die sie erfuellen soll.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest
from pathlib import Path

from config import (
    GV_ACHSE_TIEFE_SCHWELLE,
    GV_AUFNAHMEBEREITSCHAFT_MODUS,
    GV_LAENGE_MODUS_DELTA,
    GV_REGISTER_OFFEN_EMOTIONAL,
    GV_REGISTER_SACHLICH_NEUTRAL,
    GV_TIEFE_MODUS,
    MODUS_KANON,
)
from ei.farbton import _farbe_modus
from ei.neugier import register_kompatibilitaet
from ei.utils import modus_pruefen

SERVER_WURZEL: Path = Path(__file__).resolve().parents[1]
UTILS_LOGGER:  str  = "ki_server.ei.utils"

# "alltag" schweigt im Farbton bewusst — der Normalzustand traegt keine Farbe.
FARBTON_STUMM: set[str] = {"alltag"}


def _modi_aus_prompt(pfad: Path) -> set[str]:
    """Liest das modus-Enum aus einer Perzeptions-Prompt-Datei.

    Vorbedingung: Die Datei enthaelt eine Zeile der Form
    '"modus": "a|b|c",'.
    Nachbedingung: Rueckgabe ist die Menge der genannten Modi.
    Fehlerfaelle: Keine passende Zeile — Rueckgabe ist leer, der Test
    schlaegt daraufhin fehl (statt still zu bestehen).
    """
    treffer = re.search(r'"modus":\s*"([^"]+)"', pfad.read_text(encoding="utf-8"))
    if not treffer:
        return set()
    return {teil.strip() for teil in treffer.group(1).split("|") if teil.strip()}


def _prompt_dateien() -> list[Path]:
    """Alle Perzeptions-Prompts, die ein modus-Enum tragen.

    Kriterium statt Aufzaehlung: Eine spaeter hinzugefuegte Provider-Variante
    wird mitgeprueft, ohne dass diese Datei angefasst werden muss.
    """
    return [
        pfad for pfad in sorted(SERVER_WURZEL.glob("prompts/*/perzeption*.txt"))
        if _modi_aus_prompt(pfad)
    ]


class TestKanonGegenPrompt(unittest.TestCase):
    """Der Kanon im Code und das Enum im Prompt sind dieselbe Liste."""

    def test_prompt_dateien_gefunden(self) -> None:
        """Ohne Prompt-Datei prueft der Vergleich unten nichts.

        Ein leerer Zeuge waere ein Falsch-Negativ: Der Vergleich bestuende,
        weil er keine Gegenseite haette.
        """
        self.assertGreaterEqual(len(_prompt_dateien()), 1)

    def test_kanon_deckt_sich_mit_jedem_prompt_enum(self) -> None:
        for pfad in _prompt_dateien():
            with self.subTest(prompt=pfad.name):
                self.assertEqual(_modi_aus_prompt(pfad), MODUS_KANON)


class TestKanonInDenTabellen(unittest.TestCase):
    """Jeder Modus des Kanons hat in jeder Verzweigungsstelle einen Wert."""

    def test_tiefe_kennt_jeden_modus(self) -> None:
        self.assertEqual(set(GV_TIEFE_MODUS), MODUS_KANON)

    def test_neugier_kennt_jeden_modus(self) -> None:
        self.assertEqual(set(GV_AUFNAHMEBEREITSCHAFT_MODUS), MODUS_KANON)

    def test_laenge_kennt_jeden_modus(self) -> None:
        self.assertEqual(set(GV_LAENGE_MODUS_DELTA), MODUS_KANON)

    def test_farbton_spricht_fuer_jeden_modus_ausser_alltag(self) -> None:
        for modus in sorted(MODUS_KANON - FARBTON_STUMM):
            with self.subTest(modus=modus):
                self.assertNotEqual(_farbe_modus(modus), "")

    def test_register_ordnet_jeden_modus_zu(self) -> None:
        """Sachlich oder offen — nur Alltag und Emotional bleiben neutral.

        Ein nicht zugeordneter Modus liefe als 1.0 durch und waere von einer
        bewussten Neutralstellung nicht zu unterscheiden.
        """
        neutral_erlaubt: set[str] = {"alltag", "emotional"}
        for modus in sorted(MODUS_KANON):
            with self.subTest(modus=modus):
                # gap_arousal 0.0: sachlich hebt an, offen bleibt bei 1.0
                sachlich: float = register_kompatibilitaet(0.0, modus, "neutral")
                # gap_arousal 0.9: offen hebt an, sachlich daempft
                offen: float = register_kompatibilitaet(0.9, modus, "neutral")
                if modus in neutral_erlaubt:
                    self.assertEqual((sachlich, offen), (1.0, 1.0))
                else:
                    self.assertNotEqual(
                        (sachlich, offen), (1.0, 1.0),
                        f"'{modus}' ist weder sachlich noch offen zugeordnet",
                    )


class TestPhilosophischerAustausch(unittest.TestCase):
    """Der Modus, der den Befund ausgeloest hat.

    Zeuge ist das Konzept: novaberg-gv-strategie_k.md §6.2 fuehrt Sektor 24
    "Philosophie-Cafe" mit T=tief. Ein philosophischer Austausch, der als flach
    gerechnet wird, kann diesen Sektor nie erreichen.
    """

    def test_gilt_als_tief(self) -> None:
        self.assertGreaterEqual(
            GV_TIEFE_MODUS["philosophischer_austausch"], GV_ACHSE_TIEFE_SCHWELLE,
        )

    def test_ist_nicht_mehr_der_alltagswert(self) -> None:
        """Gegenprobe in Testform: 0.3 waere genau der alte Default."""
        self.assertNotEqual(
            GV_TIEFE_MODUS["philosophischer_austausch"], GV_TIEFE_MODUS["alltag"],
        )

    def test_gilt_im_register_als_offen(self) -> None:
        self.assertEqual(
            register_kompatibilitaet(0.9, "philosophischer_austausch", "neutral"),
            GV_REGISTER_OFFEN_EMOTIONAL,
        )

    def test_lernmodus_gilt_im_register_als_sachlich(self) -> None:
        """Positiver Zwilling zur offenen Seite."""
        self.assertEqual(
            register_kompatibilitaet(0.0, "lernmodus", "neutral"),
            GV_REGISTER_SACHLICH_NEUTRAL,
        )


class TestModusPruefung(unittest.TestCase):
    """Ein Modus ausserhalb des Kanons wird mit seinem Namen gemeldet."""

    def test_unbekannter_modus_nennt_den_wert(self) -> None:
        with self.assertLogs(UTILS_LOGGER, level="ERROR") as protokoll:
            bekannt: bool = modus_pruefen("traumtanz", "Test")

        self.assertFalse(bekannt)
        ausgabe: str = "\n".join(protokoll.output)
        self.assertIn("traumtanz", ausgabe)
        self.assertIn("Test", ausgabe)

    def test_leerer_modus_wird_gemeldet(self) -> None:
        with self.assertLogs(UTILS_LOGGER, level="ERROR"):
            self.assertFalse(modus_pruefen("", "Test"))

    def test_bekannter_modus_schweigt(self) -> None:
        """Positiver Zwilling: Ohne ihn wuerde auch eine Dauer-Fehlermeldung bestehen."""
        for modus in sorted(MODUS_KANON):
            with self.subTest(modus=modus):
                with self.assertNoLogs(UTILS_LOGGER, level="WARNING"):
                    self.assertTrue(modus_pruefen(modus, "Test"))


if __name__ == "__main__":
    unittest.main()
