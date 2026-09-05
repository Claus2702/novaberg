"""Zeugen: Jede Deutungsebene der Destillation nennt ihren Traeger.

Ziel: Die Destillations-Prompts zaehlen Ebenen auf, an denen das Modell den
Charakter ablesen soll — `NAEHE (…)`, `HIERARCHIE (…)`, `STIL (…)`. Nennt eine
davon den Traeger nicht, steht dort eine Eigenschaft ohne Subjekt, und das
Modell sucht sich eines.

`[gemessen]` — 05.09.2026: Das Beziehungsprofil aus der Perspektive des
Menschen ergab *„Er adressiert Nova als 'Chef'"*. **Die Richtung ist
vertauscht** — die Figur nennt den Menschen so, nicht umgekehrt. Die Ursache
liegt im Zusammentreffen dreier Umstaende: Die Ebene `NAEHE` erklaerte die
**Anrede** zum Merkmal, ohne einen Sprecher zu nennen; das Material des
Beziehungsprofils traegt **beide** Sprecher, weil der Umgang sonst nicht
lesbar waere; und die einzige Anrede darin stammte vom Gegenueber.

Zeugen dieser Datei:
  * **Geprueft wird der gerenderte Prompt, nicht die Vorlage.** In der
    Vorlage steht `{traeger}`; ob er nach dem Einsetzen tatsaechlich in jeder
    Klammer steht, sieht man erst am fertigen Text — und den bekommt das
    Modell.
  * **Die Ebenen werden gesucht, nicht aufgezaehlt.** Eine Liste im Zeugen
    waere eine zweite Wahrheit neben dem Prompt und veraltete beim naechsten
    Zusatz still.
  * **Der Zeuge hat eine Gegenprobe im eigenen Bauch:** Er prueft zuerst,
    dass er ueberhaupt Ebenen findet. Ein Muster, das nichts trifft, meldet
    sonst *„keine Verstoesse"* und ist von einer erfuellten Regel nicht zu
    unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest

from agents.charakter import destillation as dest

#: Ein Trägername, der in keinem Prompttext zufaellig vorkommt.
MARKER: str = "ZZTRAEGERZZ"

#: Die Platzhalter, die alle denselben Traeger meinen. Sie bekommen denselben
#: Marker, damit jede Beugungsform als Nennung zaehlt.
TRAEGER_FELDER: tuple[str, ...] = (
    "traeger", "traeger_akk", "traeger_dat", "traeger_gen",
)

#: Ein Grossbuchstaben-Wort, gefolgt von einer Klammer — die Form, in der die
#: Prompts ihre Deutungsebenen fuehren.
EBENE: re.Pattern = re.compile(r"\b([A-ZÄÖÜ]{4,})\s*\(([^)]*)\)")

#: Die Prompts, die einen Traeger fuehren. Sie werden aus dem Modul geholt und
#: nicht aufgezaehlt: Ein neuer Prompt soll mitgeprueft werden, ohne dass
#: jemand diese Datei anfasst.
#:
#: **Die Rad-Prompts stehen ausdruecklich nicht darin, und der Grund ist ihr
#: Material.** Sie bekommen ein fertiges Profil, keinen Gespraechsverlauf —
#: dort gibt es keinen zweiten Sprecher, mit dem sich der Traeger verwechseln
#: liesse. Das Kriterium ist deshalb nicht der Name des Prompts, sondern die
#: Frage, ob er einen Traeger **kennt**: Wer ihn fuehrt, fuehrt ihn in jeder
#: Deutungsebene.
PROMPTS: dict[str, str] = {
    name: wert
    for name, wert in vars(dest).items()
    if name.endswith("_PROMPT") and isinstance(wert, str) and "{traeger" in wert
}


def rendern(vorlage: str) -> str:
    """Setzt alle Platzhalter ein und gibt den Text, den das Modell bekaeme."""
    werte: dict[str, str] = {f: MARKER for f in TRAEGER_FELDER}
    werte.update({
        "perspektive": f"{MARKER}s", "pronomen": "sie", "possessiv": "ihr",
        "pronomen_dat": "ihr", "pronomen_akk": "sie",
        "eintraege": "(hier steht das Material)",
    })
    while True:
        try:
            return vorlage.format(**werte)
        except KeyError as fehlt:
            werte[fehlt.args[0]] = "(Platzhalter)"


class TestEbenenNennenDenTraeger(unittest.TestCase):
    """Keine Deutungsebene ohne Subjekt."""

    def test_es_gibt_ueberhaupt_prompts(self) -> None:
        """Sonst prueft der Rest eine leere Menge und meldet Erfolg."""
        self.assertGreaterEqual(len(PROMPTS), 4, f"gefunden: {sorted(PROMPTS)}")

    def test_das_muster_findet_ebenen(self) -> None:
        """Die Gegenprobe im eigenen Bauch: ein Muster ohne Treffer ist blind."""
        gefunden = {
            name: [m.group(1) for m in EBENE.finditer(rendern(text))]
            for name, text in PROMPTS.items()
        }
        gesamt = sum(len(v) for v in gefunden.values())
        self.assertGreaterEqual(gesamt, 8, f"gefundene Ebenen: {gefunden}")

    def test_jede_ebene_nennt_den_traeger(self) -> None:
        verstoesse: list[str] = []
        for name, text in PROMPTS.items():
            for treffer in EBENE.finditer(rendern(text)):
                ebene, inhalt = treffer.group(1), treffer.group(2)
                if MARKER not in inhalt:
                    verstoesse.append(f"{name}/{ebene}: ({inhalt.strip()[:70]})")
        self.assertEqual(
            verstoesse, [],
            "Deutungsebene ohne Traeger — das Modell sucht sich ein Subjekt:\n  "
            + "\n  ".join(verstoesse),
        )


class TestPerspektiveIstGesetzt(unittest.TestCase):
    """Der Traeger steht ueberhaupt im Prompt, und zwar mehrfach."""

    def test_die_traeger_prompts_sind_vollzaehlig(self) -> None:
        """Deckungszusicherung: die vier Profil-Prompts sind dabei.

        Ohne sie liefe der Zeuge auf einer Teilmenge und meldete Erfolg,
        sobald jemand einen Prompt umbenennt.
        """
        for name in ("KERN_HASH_PROMPT", "ADAPTIVE_HASH_PROMPT",
                     "INTENTIONS_PROFIL_PROMPT", "EMOTIONS_PROFIL_PROMPT",
                     "BEZIEHUNGS_PROFIL_PROMPT"):
            with self.subTest(prompt=name):
                self.assertIn(name, PROMPTS)

    def test_jeder_prompt_nennt_den_traeger(self) -> None:
        for name, text in PROMPTS.items():
            with self.subTest(prompt=name):
                self.assertIn(MARKER, rendern(text))

    def test_das_beziehungsprofil_trennt_die_seiten(self) -> None:
        """Sein Material traegt beide Sprecher — der Prompt sagt, wessen Seite zaehlt."""
        text = rendern(dest.BEZIEHUNGS_PROFIL_PROMPT)
        self.assertIn("beide Seiten", text)
        self.assertGreaterEqual(text.count(MARKER), 8, "Traeger zu selten genannt")


if __name__ == "__main__":
    unittest.main()
