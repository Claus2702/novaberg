"""Tests: Ein eigener Gedanke verbraucht keine Rueckfrage.

Nova darf handeln. An seiner Stelle antworten darf sie nicht — das ist die
Grenze derselben Entscheidung. Eine Rueckfrage richtet sich an den Menschen;
sie zu beantworten ist keine eigene Handlung, sondern eine an seiner Statt.

**Der Defekt, gegen den hier geprueft wird.** Der Wartezustand eines Agenten
wird im Resume-Pfad geloescht, **bevor** der Agent laeuft — ausdruecklich, gegen
Endlosschleifen. Lief ein Impuls-Turn dort hinein, war die Rueckfrage danach
weg, und der Mensch hat sie nie beantworten koennen.

**Zwei Riegel, zwei verschiedene Fragen:**
  * Der **Router** entscheidet die Zustaendigkeit: Ein Reiz eigener Herkunft
    nimmt den Resume-Pfad nicht. Das gilt unabhaengig vom Zeitpunkt der
    Zustellung — auch ein Wiederholungsversuch traegt dieselbe Marke.
  * Die **Zustellung** entscheidet den Zeitpunkt: Solange ein Agent wartet,
    bleibt der Eintrag auf dem Stapel. Er verfaellt nicht.

Der zweite ersetzt den ersten nicht. Wer nur den Zeitpunkt sichert, hat den
Weg offen gelassen, auf dem der Reiz ohne Zustellung ankommt.

Zeugen dieser Datei:
  * **Beide Herkuenfte werden geprueft.** Dass der Impuls den Pfad meidet, ist
    erst eine Aussage, wenn eine echte Aeusserung ihn weiterhin nimmt — sonst
    waere auch ein abgeschalteter Resume-Pfad gruen.
  * **Die Zusicherung haengt an einer Stelle, und der Zeuge sitzt dort.** Ein
    erster Entwurf prueft die nicht geloeschte Wartemarke — seine Gegenprobe
    blieb gruen, weil geloescht wird, wo der Router gar nicht hinkommt. Ein
    Zeuge, der nicht rot werden kann, ist keiner.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.nodes import router as router_mod
from services import shadow_delivery as sd_mod

GEDANKE: str = (
    "Cassini hat beim Abtauchen zwischen Ringen und Planet weniger Staub "
    "gemessen, als jedes Modell vorhergesagt hatte."
)
AEUSSERUNG: str = "Die zweite Notiz, die mit dem Vortrag."
WARTEZUSTAND: dict = {"agent_name": "notizen", "action": "update",
                      "rueckfrage": "Welche Notiz meinst du?"}


def _zustand(eigener: bool) -> dict:
    """Ein Turn beider Herkuenfte, wie der Router ihn liest."""
    if eigener:
        return {
            "user_prompt": "", "eigener_gedanke": GEDANKE,
            "event_payload": {"reiz_herkunft": "eigener_impuls"},
            "user_id": "meister", "character_id": "nova",
        }
    return {
        "user_prompt": AEUSSERUNG, "eigener_gedanke": "",
        "event_payload": {},
        "user_id": "meister", "character_id": "nova",
    }


def _routen(eigener: bool) -> dict:
    """Faehrt den Router mit einem wartenden Agenten.

    Vorbedingung: keine.
    Nachbedingung: der Zustand nach dem Lauf.
    Fehlerfaelle: keine — der Modellaufruf ist abgefangen.
    """
    from types import SimpleNamespace

    zustand: dict = _zustand(eigener)
    antwort = SimpleNamespace(parsed={}, text="{}", token_total=0)
    with patch("tools.redis_manager.redis_manager.get_json",
               return_value=WARTEZUSTAND):
        with patch.object(router_mod.model_service.chat, "submit_sync",
                          return_value=antwort):
            return router_mod.route(zustand)


class DerRouterSchuetztDieRueckfrageTest(unittest.TestCase):
    """Die Zustaendigkeit — unabhaengig davon, wie der Reiz hereinkam."""

    def test_ein_eigener_gedanke_nimmt_den_resume_pfad_nicht(self) -> None:
        """Sonst beantwortet er eine Frage, die ihm nicht gestellt wurde."""
        self.assertNotEqual(_routen(eigener=True).get("management_action"), "resume")

    def test_eine_echte_aeusserung_nimmt_ihn_weiterhin(self) -> None:
        """Die Gegenrichtung — sonst waere auch ein toter Pfad gruen."""
        self.assertEqual(_routen(eigener=False).get("management_action"), "resume")

    def test_die_uebrigen_routing_felder_bleiben_unberuehrt(self) -> None:
        """Der Impuls nimmt den normalen Weg, nicht einen dritten.

        **Hier stand bis 14.08.2026 ein Zeuge auf die nicht geloeschte
        Wartemarke.** Seine Gegenprobe blieb gruen: Geloescht wird eine Schicht
        tiefer, im Agenten-Dispatch, und der Router loest das nie aus — der
        Test konnte gar nicht rot werden. Die Zusicherung haengt an einer
        einzigen Stelle, und die prueft der Zeuge darueber.
        """
        zustand: dict = _routen(eigener=True)

        self.assertEqual(zustand.get("management_target", ""), "")
        self.assertIn("needs_memory", zustand)

    def test_die_entscheidung_wird_benannt(self) -> None:
        """Ein stiller Riegel ist von einem fehlenden nicht zu unterscheiden."""
        with self.assertLogs("ki_server.router", level="INFO") as log:
            _routen(eigener=True)
        self.assertIn("beantwortet keine Rueckfrage", "".join(log.output))


class DieZustellungWartetTest(unittest.TestCase):
    """Der Zeitpunkt — der Eintrag verfaellt nicht, er wartet."""

    def test_ein_wartender_agent_haelt_den_impuls_zurueck(self) -> None:
        """Der Fall, fuer den die Wartebedingung gebaut wurde."""
        speicher = MagicMock()
        speicher.exists.return_value = 1
        self.assertTrue(sd_mod._rueckfrage_offen(speicher, "meister"))

    def test_ohne_wartenden_agenten_wird_zugestellt(self) -> None:
        """Der positive Zwilling: Die Zustellung ist nicht einfach abgeschaltet."""
        speicher = MagicMock()
        speicher.exists.return_value = 0
        self.assertFalse(sd_mod._rueckfrage_offen(speicher, "meister"))

    def test_die_zurueckstellung_wird_benannt(self) -> None:
        """Sonst sieht ein stiller Tag aus wie ein Tag ohne Gedanken."""
        speicher = MagicMock()
        speicher.exists.return_value = 1
        with self.assertLogs("ki_server.shadow_delivery", level="INFO") as log:
            sd_mod._rueckfrage_offen(speicher, "meister")
        self.assertIn("bleibt auf dem Stapel", "".join(log.output))

    def test_ein_ausgefallener_speicher_legt_die_zustellung_nicht_still(self) -> None:
        """Ein Riegel, der bei einem Ausfall dauerhaft schliesst, ist ein Ausfall."""
        speicher = MagicMock()
        speicher.exists.side_effect = ConnectionError("Redis weg")
        with self.assertLogs("ki_server.shadow_delivery", level="ERROR") as log:
            offen: bool = sd_mod._rueckfrage_offen(speicher, "meister")
        self.assertFalse(offen)
        self.assertIn("nicht lesbar", "".join(log.output))

    def test_die_pruefung_steht_vor_dem_burst_zaehler(self) -> None:
        """Die Wartebedingung steht vor dem Burst-Zaehler.

        Ein Zaehler, der fuer einen unterdrueckten Impuls hochliefe,
        verbrauchte die naechste Gelegenheit mit.
        """
        import inspect

        quelle: str = inspect.getsource(sd_mod.shadow_delivery_loop)
        self.assertLess(
            quelle.index("_rueckfrage_offen"), quelle.index("_burst_erlaubt"),
        )


if __name__ == "__main__":
    unittest.main()
