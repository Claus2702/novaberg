"""Zeugen: Ein Modell-Override laesst keine Regel des Defaults fallen.

Ziel: Die Prompt-Modellebene **ersetzt** einen Block, sie ergaenzt ihn nicht
(`prompt_loader.prompt_laden`: `prompts.update(bloecke)`). Wer einen Block
ueberschreibt, um einen Absatz zu aendern, uebernimmt damit die Pflege aller
uebrigen — und die faellt still aus, sobald jemand den Default erweitert.

**Der Fall ist keine Erfindung.** Am 05.09.2026 wurde `responder.rules` fuer
das Fernmodell ueberschrieben, um die Antwortlaenge zu begrenzen. Der Block
traegt daneben das Verbot der Service-Floskeln, das Butler-Prinzip, die Regel
gegen interne Tags und das Verbot, eine Aktion ohne Auftrag zu bestaetigen.
Faellt einer dieser Absaetze beim naechsten Ausbau aus dem Override, gilt er
fuer das aktive Modell **nicht mehr** — und nichts meldet es.

Zeugen dieser Datei:
  * **Geprueft wird gegen den Default, nicht gegen eine Liste.** Eine
    Aufzaehlung der Regeln hier waere eine dritte Fassung neben Default und
    Override und veraltete als erste.
  * **Das Kriterium ist das Stichwort des Absatzes**, nicht sein Wortlaut —
    ein Override darf umformulieren, das ist sein Zweck. Er darf nur nichts
    weglassen.
  * **Der Zeuge prueft zuerst, dass es ueberhaupt Overrides gibt.** Ohne
    diesen Schritt liefe er auf einer leeren Menge und meldete Erfolg.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest
from pathlib import Path

#: Die Wurzel der Prompt-Bloecke.
PROMPTS: Path = Path(__file__).resolve().parent.parent / "prompts"

#: Ein Absatz-Stichwort: ein Wort am Zeilenanfang, gefolgt von einem
#: Doppelpunkt. So fuehren die Bloecke ihre Regeln.
STICHWORT: re.Pattern = re.compile(r"^([A-ZÄÖÜ][\w-]{3,}):", re.M)


def overrides() -> list[tuple[Path, Path]]:
    """Alle Blockdateien ausserhalb von `default/`, mit ihrem Default daneben."""
    paare: list[tuple[Path, Path]] = []
    for datei in sorted(PROMPTS.rglob("*.txt")):
        if "default" in datei.parts:
            continue
        vorlage = PROMPTS / "default" / datei.name
        if vorlage.exists():
            paare.append((datei, vorlage))
    return paare


class TestOverrideDeckung(unittest.TestCase):
    """Kein Absatz geht beim Ueberschreiben verloren."""

    def test_es_gibt_ueberhaupt_overrides(self) -> None:
        """Sonst prueft der Rest eine leere Menge und meldet Erfolg."""
        self.assertTrue(overrides(), f"keine Override-Bloecke unter {PROMPTS}")

    def test_jedes_stichwort_des_defaults_steht_im_override(self) -> None:
        fehlend: list[str] = []
        for datei, vorlage in overrides():
            default_text = vorlage.read_text(encoding="utf-8")
            override_text = datei.read_text(encoding="utf-8")
            for wort in STICHWORT.findall(default_text):
                if wort not in override_text:
                    fehlend.append(
                        f"{datei.relative_to(PROMPTS)}: '{wort}:' fehlt "
                        f"(steht in default/{vorlage.name})"
                    )
        self.assertEqual(
            fehlend, [],
            "Ein Override laesst eine Regel des Defaults fallen — sie gilt fuer "
            "das aktive Modell dann nicht mehr:\n  " + "\n  ".join(fehlend),
        )

    def test_die_bloecke_tragen_ihre_marke(self) -> None:
        """Ein Block ohne `[NAME]`-Kopf wird an falscher Stelle eingesetzt."""
        ohne: list[str] = []
        for datei, vorlage in overrides():
            if vorlage.read_text(encoding="utf-8").lstrip().startswith("["):
                if not datei.read_text(encoding="utf-8").lstrip().startswith("["):
                    ohne.append(str(datei.relative_to(PROMPTS)))
        self.assertEqual(ohne, [], f"Override ohne Blockmarke: {ohne}")


if __name__ == "__main__":
    unittest.main()
