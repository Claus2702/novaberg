"""Tests: Der Intentions-Kanon im Code ist dieselbe Liste wie im Prompt.

Ziel: Kein Wert, den die Salienz liefern darf, ist dem Code unbekannt — und
kein Wert, den der Code kennt, fehlt im Prompt.

Hintergrund: `GV_INITIATIVE_FUEHREND` ist eine **Teilmenge** von fuenf der
sechzehn Intentionen. Wer nur gegen die Teilmenge prueft, kann einen unbekannten
Wert nicht von einer gueltigen Nicht-Zugehoerigkeit unterscheiden — beides ergibt
"kein Treffer". Genau daran lief M1 der Initiative-Achse zwei Monate als
Konstante: Der Korpus las Bruchstuecke eines Transportformats, sie trafen die
fuenf nie, und weil die Liste nicht leer war, galt M1 als "nicht fuehrend" statt
als "fehlend". 0 von 144 Turns fuehrend, geparst 40 von 99
(`novaberg-lesson_l_teilmenge-verdeckt-muell.md`).

Zeugen dieser Datei:
  * **Die Prompt-Datei ist der Zeuge**, nicht der Code. Sie legt fest, was das
    LLM liefern DARF; der Kanon im Code hat sich nach ihr zu richten und nicht
    umgekehrt. Dieselbe Bauart wie `test_modus_kanon.py`.
  * **Die Teilmengen-Zusicherung ist der eigentliche Waechter:** Ein Tippfehler
    in `GV_INITIATIVE_FUEHREND` wuerde die betroffene Intention klanglos
    unwirksam machen — genau die Fehlerklasse, aus der dieser Test entstand.
    Ein Test, der nur Kanon gegen Prompt prueft, saehe das nicht.
  * Die Zahl 16 steht **nicht** als Literal in den Erwartungen. Eine
    Aufzaehlung, die man beim Ergaenzen anpassen muss, wird beim Ergaenzen
    vergessen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest
from pathlib import Path

from config import GV_INITIATIVE_FUEHREND, INTENT_KANON

SERVER_WURZEL = Path(__file__).resolve().parent.parent
PROMPT = SERVER_WURZEL / "prompts" / "default" / "salienz.dimensionen.txt"


def _intentionen_aus_prompt(pfad: Path) -> set[str]:
    """Liest die Intentionen aus dem Aufzaehlungsblock der Prompt-Datei.

    Vorbedingung: Die Datei enthaelt einen Abschnitt `6. INTENTIONEN:` mit
    Zeilen der Form `- "name" — Erklaerung`.
    Nachbedingung: Menge der genannten Intentionen.
    Fehlerfaelle: Kein Abschnitt oder keine Eintraege — Rueckgabe ist leer, und
    der Test schlaegt daraufhin fehl statt still zu bestehen.

    Returns:
        Die Intentionen aus dem Prompt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not pfad.is_file():
        return set()

    text: str = pfad.read_text(encoding="utf-8")

    # ── Verarbeitung ────────────────────────────
    # Vom Abschnittskopf bis zum naechsten numerierten Abschnitt.
    block = re.search(r"^\d+\.\s*INTENTIONEN:.*?(?=^\d+\.\s)", text,
                      re.MULTILINE | re.DOTALL)
    if not block:
        return set()

    # ── Ausgabe-Verifikation ────────────────────
    return set(re.findall(r'^\s*-\s*"([a-z_]+)"', block.group(0), re.MULTILINE))


class KanonGegenPrompt(unittest.TestCase):
    """Der Kanon im Code und die Aufzaehlung im Prompt sind dieselbe Liste."""

    def test_prompt_liefert_ueberhaupt_werte(self) -> None:
        """Gegenprobe zum Parser: Ohne Treffer prueft der Vergleich nichts.

        Ein Parser, der nichts findet, laesst jeden Vergleich gegen eine leere
        Menge laufen — und der ist gruen, sobald auch der Kanon leer ist.
        """
        self.assertTrue(
            _intentionen_aus_prompt(PROMPT),
            f"{PROMPT} liefert keine Intentionen — der Parser greift nicht, "
            f"der Vergleich unten prueft dann nichts",
        )

    def test_kanon_ist_die_liste_aus_dem_prompt(self) -> None:
        """Code und Prompt nennen genau dieselben Intentionen."""
        aus_prompt = _intentionen_aus_prompt(PROMPT)
        self.assertEqual(
            INTENT_KANON, aus_prompt,
            f"nur im Code: {sorted(INTENT_KANON - aus_prompt)} | "
            f"nur im Prompt: {sorted(aus_prompt - INTENT_KANON)}",
        )


class FuehrendeIntentionen(unittest.TestCase):
    """Die fuehrenden Intentionen sind eine echte Teilmenge des Kanons."""

    def test_jede_fuehrende_intention_steht_im_kanon(self) -> None:
        """Der Waechter gegen den Tippfehler, der klanglos wirkungslos macht.

        Ein Wert in `GV_INITIATIVE_FUEHREND`, den der Kanon nicht kennt, kann
        nie treffen. M1 wuerde die betroffene Intention nie als fuehrend lesen,
        ohne dass irgendetwas anschlaegt.
        """
        fremd = GV_INITIATIVE_FUEHREND - INTENT_KANON
        self.assertEqual(
            fremd, set(),
            f"{sorted(fremd)} steht in GV_INITIATIVE_FUEHREND, aber nicht im "
            f"Kanon — diese Intention kann nie treffen",
        )

    def test_fuehrend_ist_echte_teilmenge(self) -> None:
        """Nicht alle Intentionen fuehren — sonst waere M1 konstant.

        Ein M1, das jede Intention als fuehrend liest, traegt in jedem Turn
        denselben Wert. Das ist derselbe Zustand wie der Defekt, nur mit
        umgekehrtem Vorzeichen.
        """
        self.assertTrue(
            GV_INITIATIVE_FUEHREND < INTENT_KANON,
            "GV_INITIATIVE_FUEHREND ist keine echte Teilmenge des Kanons — "
            "M1 waere konstant",
        )


if __name__ == "__main__":
    unittest.main()
