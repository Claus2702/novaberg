"""Zeugen fuer den Matrix-Connector.

**Sie laufen NICHT in der Server-Suite**, und das ist keine Nachlaessigkeit,
sondern die Lage: Der Connector ist ein eigener Dienst mit eigenem Behaelter
und eigenem Abhaengigkeitssatz; `unittest discover` im Server sieht ihn nicht.
Aufruf:

    docker compose exec matrix-bot python -m unittest discover -p "test_*.py"

**Was hier bezeugt wird, ist die Absenderwahl** — der einzige Grund, warum
dieser Kanal existiert. Ein Fehler darin sieht im Betrieb aus wie eine
gewoehnliche Nachricht und faellt erst auf, wenn jemand den Verlauf liest.
"""

import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("MATRIX_AS_TOKEN", "test-as-token")
os.environ.setdefault("MATRIX_HS_TOKEN", "test-hs-token")

import bot  # noqa: E402
from matrix_api import MatrixFehler, kennung  # noqa: E402


class KennungTest(unittest.TestCase):
    """Der lokale Teil wird zur vollstaendigen Kennung."""

    def test_baut_die_vollstaendige_form(self) -> None:
        self.assertEqual(kennung("meister"), "@meister:novaberg.de")

    def test_weist_eine_bereits_vollstaendige_zurueck(self) -> None:
        """Eine doppelte Aufloesung ergaebe `@@meister:novaberg.de:novaberg.de`
        — und der Homeserver antwortet darauf mit einem Fehler, dessen Ursache
        weit weg von hier liegt."""
        for eingabe in ("@meister", "meister:novaberg.de", "@meister:novaberg.de"):
            with self.subTest(eingabe=eingabe), self.assertRaises(ValueError):
                kennung(eingabe)

    def test_weist_leer_zurueck(self) -> None:
        for eingabe in ("", "   "):
            with self.subTest(eingabe=eingabe), self.assertRaises(ValueError):
                kennung(eingabe)


class AbsenderwahlTest(unittest.TestCase):
    """Der Kern: Wer steht im Verlauf als Absender?

    **Diese Klasse prueft `absender_fuer` und nicht den Sendeweg**, und der
    Unterschied ist gemessen: Die erste Fassung rief `_in_raum` selbst auf und
    behauptete damit, was sie pruefen sollte. Die Gegenprobe baute das
    `[Du]`-Praefix zurueck — **kein Test wurde rot**.
    """

    def test_die_antwort_kommt_von_der_figur(self) -> None:
        self.assertEqual(bot.absender_fuer("character_response", "meister"), "nova")

    def test_ein_eigener_impuls_kommt_von_der_figur(self) -> None:
        self.assertEqual(bot.absender_fuer("shadow_delivery", "meister"), "nova")

    def test_eine_fremde_aeusserung_kommt_vom_menschen(self) -> None:
        """**Der Zeuge, der den Kanal rechtfertigt.**

        Im Telegram-Kanal steht hier `[Du] ...`, gesendet vom Bot. Wird diese
        Zusicherung rot, ist der einzige Grund fuer den Matrix-Kanal entfallen
        — und zwar lautlos: Die Nachricht kaeme an, nur vom Falschen.
        """
        self.assertEqual(bot.absender_fuer("user_message", "meister"), "meister")

    def test_die_beiden_sorten_sind_verschieden(self) -> None:
        """Der eigentliche Satz: Antwort und fremde Aeusserung tragen
        **verschiedene** Absender. Ein Kanal, in dem beide gleich sind, ist
        der Telegram-Kanal."""
        self.assertNotEqual(
            bot.absender_fuer("character_response", "meister"),
            bot.absender_fuer("user_message", "meister"),
        )

    def test_zwischenstaende_gehen_nicht_in_den_raum(self) -> None:
        """Ein Raum ist kein Fortschrittsbalken."""
        for typ in ("character_stage", "verbindung", "echo", "unbekannt"):
            with self.subTest(typ=typ):
                self.assertIsNone(bot.absender_fuer(typ, "meister"))


class TransaktionTest(unittest.IsolatedAsyncioTestCase):
    """Was der Homeserver liefert — und was davon weitergereicht wird."""

    async def asyncSetUp(self) -> None:
        bot.RAEUME.clear()
        bot.RAEUME["meister"] = "!raum:novaberg.de"
        bot.EIGENE_EVENTS.clear()

    def _ereignis(self, **felder) -> dict:
        basis: dict = {
            "type": "m.room.message",
            "event_id": "$abc",
            "sender": "@meister:novaberg.de",
            "room_id": "!raum:novaberg.de",
            "content": {"msgtype": "m.text", "body": "Hallo"},
        }
        basis.update(felder)
        return basis

    async def test_eine_nachricht_des_menschen_geht_an_novaberg(self) -> None:
        with patch.object(bot, "_an_novaberg", new=AsyncMock()) as weiter:
            await bot._ereignis_behandeln(self._ereignis())
        weiter.assert_awaited_once_with("meister", "Hallo")

    async def test_das_eigene_echo_geht_nicht_zurueck(self) -> None:
        """**Ohne diese Zusicherung laeuft der Kanal im Kreis.**

        Was der Connector als `@meister` einstellt, liefert der Homeserver
        ihm zurueck. Ginge es erneut an `POST /chat`, beantwortete Nova jede
        Desktop-Aeusserung ein zweites Mal.
        """
        bot.EIGENE_EVENTS.add("$abc")
        with patch.object(bot, "_an_novaberg", new=AsyncMock()) as weiter:
            await bot._ereignis_behandeln(self._ereignis())
        weiter.assert_not_awaited()

    async def test_die_figur_speist_sich_nicht_selbst_ein(self) -> None:
        with patch.object(bot, "_an_novaberg", new=AsyncMock()) as weiter:
            await bot._ereignis_behandeln(
                self._ereignis(sender="@nova:novaberg.de", event_id="$x"))
        weiter.assert_not_awaited()

    async def test_eine_unbekannte_kennung_wird_uebergangen(self) -> None:
        """Dieselbe weisse Liste wie im Telegram-Kanal, aus demselben Grund."""
        with patch.object(bot, "_an_novaberg", new=AsyncMock()) as weiter:
            await bot._ereignis_behandeln(
                self._ereignis(sender="@fremder:novaberg.de", event_id="$y"))
        weiter.assert_not_awaited()

    async def test_ein_anderer_ereignistyp_wird_uebergangen(self) -> None:
        with patch.object(bot, "_an_novaberg", new=AsyncMock()) as weiter:
            await bot._ereignis_behandeln(
                self._ereignis(type="m.room.member", event_id="$z"))
        weiter.assert_not_awaited()

    async def test_ein_bild_wird_uebergangen(self) -> None:
        """Kein Text, keine Aeusserung — aber auch kein Fehler."""
        with patch.object(bot, "_an_novaberg", new=AsyncMock()) as weiter:
            await bot._ereignis_behandeln(self._ereignis(
                event_id="$i", content={"msgtype": "m.image", "body": "bild.png"}))
        weiter.assert_not_awaited()

    async def test_der_raum_der_nachricht_gewinnt(self) -> None:
        """Kommt eine Nachricht aus einem anderen Raum, wird dort geantwortet.

        Sonst spraeche Nova in einen Raum, den niemand mehr liest — etwa nach
        einem von Hand angelegten zweiten Raum.
        """
        with patch.object(bot, "_an_novaberg", new=AsyncMock()), \
             patch.object(bot, "_raeume_sichern", lambda r: None):
            await bot._ereignis_behandeln(
                self._ereignis(room_id="!anderer:novaberg.de", event_id="$r"))
        self.assertEqual(bot.RAEUME["meister"], "!anderer:novaberg.de")


class FehlerFormTest(unittest.TestCase):
    """Ein abgelehnter Aufruf sagt, warum."""

    def test_der_matrixfehler_traegt_code_und_status(self) -> None:
        """`M_EXCLUSIVE` heisst falscher Namensraum, `M_FORBIDDEN` falscher
        Token — die beiden verlangen Verschiedenes, und ein Fehler ohne den
        Code liesse das offen."""
        fehler = MatrixFehler(403, "M_EXCLUSIVE", "nicht im Namensraum")
        self.assertEqual(fehler.status, 403)
        self.assertEqual(fehler.code, "M_EXCLUSIVE")
        self.assertIn("M_EXCLUSIVE", str(fehler))


if __name__ == "__main__":
    unittest.main()


class FormatierungTest(unittest.TestCase):
    """Markdown wird zu der Teilmenge, die Matrix-Clients zeigen."""

    def test_fettdruck_wird_ausgezeichnet(self) -> None:
        from formatierung import nach_matrix_html
        self.assertIn("<strong>wichtig</strong>", nach_matrix_html("Das ist **wichtig**."))

    def test_spitze_klammern_werden_maskiert(self) -> None:
        """**Maskiert wird zuerst.** Ein Modell, das ueber Code spricht,
        schreibt `<` — und ein Client, der es als Element liest, verwirft die
        halbe Nachricht."""
        from formatierung import nach_matrix_html
        html_text = nach_matrix_html("Wenn a < b, dann <script>")
        self.assertNotIn("<script>", html_text)
        self.assertIn("&lt;", html_text)

    def test_codeblock_behaelt_seine_sternchen(self) -> None:
        """Innerhalb von Code ist ein Sternchen ein Sternchen."""
        from formatierung import nach_matrix_html
        html_text = nach_matrix_html("```\na ** b\n```")
        self.assertIn("<pre><code>", html_text)
        self.assertNotIn("<strong>", html_text)

    def test_ohne_auszeichnung_kein_zweites_feld(self) -> None:
        """Ein `formatted_body`, das nur den Text wiederholt, traegt nichts."""
        from formatierung import inhalt_bauen
        inhalt = inhalt_bauen("Ein schlichter Satz ohne alles.")
        self.assertNotIn("formatted_body", inhalt)
        self.assertEqual(inhalt["body"], "Ein schlichter Satz ohne alles.")

    def test_body_bleibt_markdown(self) -> None:
        """`body` ist die Rueckfallform und soll lesbar sein — dafuer ist
        Markdown gebaut."""
        from formatierung import inhalt_bauen
        inhalt = inhalt_bauen("Das ist **wichtig**.")
        self.assertEqual(inhalt["body"], "Das ist **wichtig**.")
        self.assertIn("formatted_body", inhalt)
