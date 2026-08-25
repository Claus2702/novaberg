"""Zeugen dafuer, dass die Profil-Prompts jede Traeger-Form als Datum bekommen.

**Zwei gemessene Defekte, eine Ursache** — `_perspektive_aufloesen` lieferte
bis zum 22.08.2026 drei Formen und keine vierte:

- `PERSPEKTIVE-OHNE-DATIV` (11.08.2026): Vier der fuenf Prompts setzten den
  Traeger hinter »von« ein; bei jedem menschlichen Paar stand dort »ein
  kompaktes Persoenlichkeitsprofil von **der Nutzer**«.
- `PROFILPROMPT-OHNE-GESCHLECHT` (19.08.2026): Kein Prompt kannte das Genus
  seines Traegers. Belegt am 18.08.2026 am Traeger »Juno« — der Kern-Hash
  fuehrte durchgehend »er«, das im **selben Lauf** erzeugte Beziehungsprofil
  im Schlusssatz das saechliche Pronomen.

**Der Zeuge prueft den gerenderten Text, nicht die Funktion.** Eine
Zusicherung ueber den Rueckgabewert von `_perspektive_aufloesen` wuerde gruen
bleiben, waehrend eine neue Prompt-Zeile die falsche Form einsetzt — und
genau so ist der Dativfehler entstanden. Deshalb steht unten eine Liste
falscher Formen, gegen die **jeder** Prompt in **beiden** Perspektiven
gehalten wird.

**Die Liste ist am Bestand gewachsen, nicht ausgedacht.** Der Defekteintrag
nannte vier Stellen; das Rendern beider Perspektiven fand am 22.08.2026
**neun** — darunter »charakterisiert der Nutzer«, »welche Emotionen tragen
der Nutzer« und »an dem man der Nutzer erkennt«, die in keinem Eintrag
standen.
"""

import unittest

from agents.charakter.destillation import (
    _PRONOMEN,
    _TRAEGERFORMEN,
    ADAPTIVE_HASH_PROMPT,
    BEZIEHUNGS_PROFIL_PROMPT,
    EMOTIONS_PROFIL_PROMPT,
    INTENTIONS_PROFIL_PROMPT,
    KERN_HASH_PROMPT,
    _perspektive_aufloesen,
)
from config import ASSISTANT_USER_ID, DEFAULT_USER_ID

# Die fuenf Profil-Prompts, so wie `agent.py` sie rendert.
PROFIL_PROMPTS: tuple[tuple[str, str], ...] = (
    ("kern",       KERN_HASH_PROMPT),
    ("adaptiv",    ADAPTIVE_HASH_PROMPT),
    ("intention",  INTENTIONS_PROFIL_PROMPT),
    ("emotion",    EMOTIONS_PROFIL_PROMPT),
    ("beziehung",  BEZIEHUNGS_PROFIL_PROMPT),
)

# Jede Form, die am 22.08.2026 im gerenderten Text stand und falsch war.
# Eine neue Prompt-Zeile mit dem falschen Kasus faellt hier auf.
FALSCHE_FORMEN: tuple[str, ...] = (
    "von der Nutzer",             # Dativ verlangt
    "von des Nutzers",            # »von« + Genitiv
    "über der Nutzer",            # Akkusativ verlangt
    "ueber der Nutzer",
    "charakterisiert der Nutzer",
    "tragen der Nutzer",
    "man der Nutzer",
    "was der Nutzer wichtig",
    "des Nutzers erkennt",
)


class TraegerformenTest(unittest.TestCase):
    """Die Funktion liefert jede Form, die ein Prompt einsetzen darf."""

    def test_beide_subjekte_liefern_jede_form(self) -> None:
        """Rot, sobald eine Form fehlt oder leer ist."""
        for user_id in (DEFAULT_USER_ID, ASSISTANT_USER_ID):
            with self.subTest(user_id=user_id):
                formen = _perspektive_aufloesen(user_id)
                for name in _TRAEGERFORMEN:
                    self.assertTrue(
                        formen.get(name),
                        f"{user_id}: Form '{name}' fehlt oder ist leer",
                    )

    def test_der_rollenbegriff_traegt_seine_eigenen_kasus(self) -> None:
        """»der Nutzer« ist grammatisch maskulin — das ist eine Aussage ueber
        das Wort, nicht ueber den Menschen. Die vier Kasus stehen fest.
        """
        formen = _perspektive_aufloesen(DEFAULT_USER_ID)
        self.assertEqual(formen["traeger"],      "der Nutzer")
        self.assertEqual(formen["traeger_gen"],  "des Nutzers")
        self.assertEqual(formen["traeger_dat"],  "dem Nutzer")
        self.assertEqual(formen["traeger_akk"],  "den Nutzer")
        self.assertEqual(formen["genus_quelle"], "rollenbegriff")

    def test_der_eigenname_bleibt_im_dativ_und_akkusativ_unflektiert(self) -> None:
        """»Novas Wesen« im Genitiv, »ueber Nova« im Akkusativ."""
        formen = _perspektive_aufloesen(ASSISTANT_USER_ID)
        self.assertEqual(formen["traeger_dat"], formen["traeger"])
        self.assertEqual(formen["traeger_akk"], formen["traeger"])
        self.assertTrue(formen["traeger_gen"].startswith(formen["traeger"]))

    def test_das_genus_der_figur_stammt_aus_der_konfiguration(self) -> None:
        """Nicht aus einer Vermutung des Modells — das ist der Defekt."""
        formen = _perspektive_aufloesen(ASSISTANT_USER_ID)
        self.assertEqual(formen["genus_quelle"], "konfiguration")
        self.assertIn(formen["pronomen"], {p["pronomen"] for p in _PRONOMEN.values()})

    def test_ein_unbekanntes_genus_bleibt_als_rueckfall_erkennbar(self) -> None:
        """Ein Rueckfall, der wie ein gesetzter Wert aussieht, ist ein stiller
        Fehler (`22_STILLE_FEHLER/default-nicht-wie-messwert.md`).
        """
        import agents.charakter.destillation as dest

        vorher = dest.ASSISTANT_GENUS
        try:
            dest.ASSISTANT_GENUS = "divers"
            formen = _perspektive_aufloesen(ASSISTANT_USER_ID)
        finally:
            dest.ASSISTANT_GENUS = vorher
        self.assertEqual(formen["genus_quelle"], "rueckfall")
        self.assertTrue(formen["pronomen"])


class GerenderteProfilPromptsTest(unittest.TestCase):
    """Der Zeuge am Text, den das Modell wirklich liest."""

    def test_kein_prompt_laesst_einen_platzhalter_offen(self) -> None:
        """Ein offener Platzhalter ist im Lauf ein KeyError, hier eine Zeile."""
        for user_id in (DEFAULT_USER_ID, ASSISTANT_USER_ID):
            formen = _perspektive_aufloesen(user_id)
            for name, prompt in PROFIL_PROMPTS:
                with self.subTest(user_id=user_id, prompt=name):
                    gefuellt = prompt.format(eintraege="…", **formen)
                    self.assertNotIn("{", gefuellt)

    def test_kein_prompt_traegt_eine_falsche_form(self) -> None:
        """Der eigentliche Zeuge: neun gemessene Fehlstellen, keine davon zurueck."""
        for user_id in (DEFAULT_USER_ID, ASSISTANT_USER_ID):
            formen = _perspektive_aufloesen(user_id)
            for name, prompt in PROFIL_PROMPTS:
                gefuellt = prompt.format(eintraege="…", **formen)
                for falsch in FALSCHE_FORMEN:
                    with self.subTest(user_id=user_id, prompt=name, form=falsch):
                        self.assertNotIn(
                            falsch, gefuellt,
                            f"{name} ({user_id}) setzt den falschen Kasus ein",
                        )

    def test_jeder_prompt_gibt_das_genus_vor(self) -> None:
        """Ohne die Zeile raet das Modell — im selben Lauf verschieden."""
        formen = _perspektive_aufloesen(ASSISTANT_USER_ID)
        for name, prompt in PROFIL_PROMPTS:
            with self.subTest(prompt=name):
                gefuellt = prompt.format(eintraege="…", **formen)
                self.assertIn("mit den Pronomen", gefuellt)
                self.assertIn(formen["pronomen"], gefuellt)
                self.assertIn(formen["possessiv"], gefuellt)


if __name__ == "__main__":
    unittest.main()
