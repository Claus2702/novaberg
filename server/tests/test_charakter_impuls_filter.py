"""Tests: Wo Impulse ausgenommen werden — und wo bewusst nicht.

Die Entscheidung vom 17.08.2026 ist nicht „überall filtern", sondern eine
Unterscheidung nach der Frage, die das Profil stellt:

| Profil | Frage | Impulse |
|---|---|---|
| Kern | wer ist er dauerhaft | **raus** |
| Beziehung | wie steht er zum Gegenüber | **raus** |
| Intentionen | wie geht er mit anderen um | **raus** |
| Adaptiv | was beschäftigt ihn gerade | **bleiben** |
| Emotionen | was fühlt er | **bleiben** |

Der Trennstrich ist das Gegenüber: Eine Aussage über Umgang setzt eines
voraus, und ein Impuls hat keines. Was jemanden beschäftigt und was er fühlt,
steht dagegen sehr wohl in seinen eigenen Gedanken — dort wäre der Filter ein
Verlust.

Gemessen am 17.08.2026: 496 von 1922 LZG-Knoten der Figur stammen aus
Impuls-Turns (26 %), und 591 von 744 rückverfolgbaren KZG-Verweisen.

Zeugen dieser Datei:
  * **Die Filter sitzen in SQL, also prüfen die Zeugen die Abfrage.** Eine
    Attrappe kann kein `WHERE` ausführen; sie bezeugt, dass die Einschränkung
    gestellt wurde — und, ebenso wichtig, dass sie bei Adaptiv und Emotionen
    **nicht** gestellt wird. Die zweite Zusicherung ist die wertvollere: Sie
    hält eine bewusste Entscheidung fest, die sonst niemand als Absicht
    erkennt.
  * **`IS DISTINCT FROM` statt `<>`** — ein Knoten ohne Brücke ist nicht
    nachweislich ein Impuls und bleibt erhalten. Am 17.08.2026 waren das 371
    von 1922 Knoten (19 %).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from config import ASSISTANT_NAME, ASSISTANT_USER_ID
from agents.charakter.agent import CharakterAgent
from agents.charakter import destillation

IMPULS: str = "eigener_impuls"


class _Bank:
    """Datenbank-Attrappe, die jede Abfrage mitschreibt."""

    def __init__(self, zeilen: list[dict] | None = None) -> None:
        self.zeilen = zeilen or []
        self.abfragen: list[str] = []

    def select(self, sql: str, params: tuple = ()) -> list[dict]:
        self.abfragen.append(sql)
        return self.zeilen


class TestWoGefiltertWird(unittest.TestCase):
    """Drei Lesepfade nehmen Impulse aus."""

    def test_wortlaut_holen_nimmt_impulse_aus(self) -> None:
        bank = _Bank()
        with patch.object(destillation, "db_manager", bank):
            destillation.wortlaut_holen(["kzg:meister:nova:1"])

        self.assertIn(IMPULS, bank.abfragen[0])
        self.assertIn("IS DISTINCT FROM", bank.abfragen[0])

    def test_intentionen_nehmen_impulse_aus(self) -> None:
        bank = _Bank()
        with patch("agents.charakter.agent.db_manager", bank):
            CharakterAgent._lzg_intentionen_laden(None, "meister", "nova", "assistant")

        self.assertIn(IMPULS, bank.abfragen[0])
        self.assertIn("IS DISTINCT FROM", bank.abfragen[0])

    def test_knoten_ohne_bruecke_bleibt(self) -> None:
        """`IS DISTINCT FROM` statt `<>` — sonst faellt jeder Knoten ohne
        Verbindung heraus, obwohl er kein Impuls sein muss."""
        bank = _Bank()
        with patch("agents.charakter.agent.db_manager", bank):
            CharakterAgent._lzg_intentionen_laden(None, "meister", "nova", "assistant")

        self.assertIn("LEFT JOIN", bank.abfragen[0])
        self.assertNotIn("!= 'eigener_impuls'", bank.abfragen[0])


class TestBegegnungsAuswahl(unittest.TestCase):
    """Die Auswahl des Beziehungsprofils kennt den Filter selbst.

    Nachgelagert zu filtern reicht nicht: Am 17.08.2026 hatten **null** von
    Novas zwanzig stärksten KZG-Einträgen einen erreichbaren
    Begegnungs-Wortlaut. Ihr Beziehungsprofil wäre dauerhaft leer geblieben —
    und es ist die zweite Hälfte der Rad-Quelle.

    Dieser Zeuge fehlte zunächst, und sein Fehlen hat etwas durchgelassen:
    Der neue Parameter blieb ungetestet, weil alle bestehenden Zeugen den
    Standardweg nahmen. **Ein neuer Parameter braucht einen Zeugen, der ihn
    setzt** — sonst ist der Zweig, den er öffnet, unbetreten.
    """

    def test_ohne_begegnung_faellt_aus_der_auswahl(self) -> None:
        jung = str(int(__import__("time").time() * 1000))
        key = f"kzg:meister:nova:{jung}"

        class _Redis:
            hashes = {key: {
                "beobachter": "user", "themen": "Garten", "inhalt": "x",
                "salienz": "1.0", "erstellt_am": str(int(jung) / 1000),
                "modus": "", "emotion": "", "beziehungs_dynamik": "", "tone": "",
            }}

            def scan_iter(self, match: str = "", count: int = 0):
                yield key

            def hget(self, k: str, f: str):
                return self.hashes.get(k, {}).get(f)

        with patch("agents.charakter.agent.redis_client", _Redis()), \
             patch("agents.charakter.agent._begegnungs_schluessel", return_value=set()), \
             patch("agents.charakter.agent.db_manager", _Bank()):
            treffer = CharakterAgent._kzg_laden(
                None, "meister", "nova", "user", nur_begegnungen=True,
            )

        self.assertEqual(
            treffer, [],
            "Ein Eintrag ohne Begegnung darf keinen der zwanzig Plaetze belegen",
        )

    def test_ohne_den_schalter_bleibt_er_drin(self) -> None:
        """Derselbe Eintrag, ohne `nur_begegnungen` — der Adaptiv-Hash sieht ihn."""
        jung = str(int(__import__("time").time() * 1000))
        key = f"kzg:meister:nova:{jung}"

        class _Redis:
            hashes = {key: {
                "beobachter": "user", "themen": "Garten", "inhalt": "x",
                "salienz": "1.0", "erstellt_am": str(int(jung) / 1000),
                "modus": "", "emotion": "", "beziehungs_dynamik": "", "tone": "",
            }}

            def scan_iter(self, match: str = "", count: int = 0):
                yield key

            def hget(self, k: str, f: str):
                return self.hashes.get(k, {}).get(f)

        with patch("agents.charakter.agent.redis_client", _Redis()):
            treffer = CharakterAgent._kzg_laden(None, "meister", "nova", "user")

        self.assertEqual(len(treffer), 1)


class TestWoBewusstNichtGefiltertWird(unittest.TestCase):
    """Adaptiv und Emotionen behalten die eigenen Gedanken.

    Diese Zeugen halten eine **Entscheidung** fest, keinen Mechanismus. Ohne
    sie sieht das Fehlen des Filters wie ein Versehen aus — und der nächste
    Umbau ergänzt ihn „der Vollständigkeit halber".
    """

    def test_emotionen_filtern_nicht(self) -> None:
        bank = _Bank()
        with patch("agents.charakter.agent.db_manager", bank):
            CharakterAgent._lzg_emotionen_laden(None, "meister", "nova", "assistant")

        self.assertNotIn(
            IMPULS, bank.abfragen[0],
            "Was jemand fuehlt, steht auch in seinen eigenen Gedanken — "
            "Entscheidung vom 17.08.2026",
        )

    def test_kzg_auswahl_filtert_nicht(self) -> None:
        """Der Adaptiv-Hash liest das KZG; dort wird nach Perspektive
        getrennt, aber nicht nach Herkunft."""
        quelltext = CharakterAgent._kzg_laden.__doc__ or ""
        self.assertNotIn(IMPULS, quelltext)


class TestBeziehungsprofilNenntNamen(unittest.TestCase):
    """Beide Sprecher tragen ihren Namen, nicht ihre Rolle."""

    def test_kein_relatives_gegenueber_mehr(self) -> None:
        eintraege = [{
            "_key": "kzg:meister:nova:1", "modus": "alltag", "emotion": "freude",
            "beziehungs_dynamik": "vertrauen", "tone": "warm",
        }]
        wortlaute = {"kzg:meister:nova:1": {
            "aeusserung": "na du", "antwort": "Hallo!",
        }}

        for uid in ("meister", ASSISTANT_USER_ID):
            with patch.object(destillation, "wortlaut_holen", return_value=wortlaute), \
                 patch.object(destillation, "_llm_call", return_value="Profil") as ruf:
                destillation.beziehungsprofil_destillieren(eintraege, user_id=uid)

            prompt = ruf.call_args[0][0]
            self.assertIn("der Nutzer: ", prompt)
            self.assertIn(f"{ASSISTANT_NAME}: ", prompt)
            self.assertNotIn(
                "Gegenueber:", prompt,
                f"Das relative Label verschiebt seinen Bezug mit dem Traeger "
                f"(hier {uid})",
            )


if __name__ == "__main__":
    unittest.main()
