"""Tests: Ein eigener Impuls faellt nicht aus dem Vorausdenken.

Ziel: Landschaft, Strategie, Vehikel und Leitgedanke stehen auch dann, wenn
der Reiz Novas eigener Gedanke ist. Die Strategie ist das Mittel, mit dem ein
Gedanke an den Menschen herangetragen wird — sie haengt nicht daran, wer ihn
angestossen hat.

Hintergrund, gemessen am 13.08.2026 ueber einen Tag Serverlog:

    eigene Impulse                     20
      davon am Skip-Tor abgewiesen     15
    Verfasser-Laeufe                   26
      davon ohne [GESPRAECHSVEKTOR]    15   (dieselben 15)

**Die Auswahl war keine Regel, sondern ein Nebeneffekt.** Das Tor liest
`external.emotion.intent`. Auf einem Impuls-Turn setzt `db_zugriff` `external`
als Kopie von `internal` (Pixie-Pfad), und der Intent beschreibt dann Novas
**vorige eigene Antwort**. Fiel er auf `meta`, schwieg der GV-Node; fiel er
auf `knowledge`, lief er durch. Waere es eine Impuls-Regel gewesen, haette sie
20 von 20 getroffen statt 15.

Zeugen dieser Datei:
  * **Die Erwartung stammt nicht aus dem Code.** Dass ein eigener Impuls
    vorausdenken soll, ist eine Festlegung ueber das Verhalten des Systems;
    `novaberg-node-gv_k.md` definiert das Skip-Tor ueber die Art der
    **Nutzer-Aeusserung**, und ein Impuls hat keine.
  * **Beide Faelle werden geprueft.** Dass der Impuls durchlaeuft, ist erst
    eine Aussage, wenn derselbe Intent beim Nutzer-Turn weiterhin abweist —
    sonst waere auch ein abgeschaltetes Tor gruen.
  * **Der Thinker-Retry gehoert dazu:** gleiche `event_source`, aber eine
    wiederholte Nutzer-Aeusserung. Er behaelt das Tor.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from graph.nodes import gespraechsvektor as gv_modul
from graph.personality import Emotion, Personality

# Die drei Marken, von Hand aus `novaberg-node-gv_k.md` uebertragen statt aus
# dem Pruefobjekt importiert: Verschwindet eine aus dem Tor, faellt es hier
# auf und nicht erst im Betrieb.
SKIP_INTENTS: tuple = ("begruessung", "meta", "system")


def _turn(payload: dict | None = None, quelle: str = "user",
          **emotionsfelder: str | float) -> dict:
    """Ein Zustand, wie ihn der GV-Node am Tor liest.

    `external` traegt auf dem Impuls-Weg dieselben Werte wie `internal` — so
    baut `db_zugriff` ihn dort. Der Test bildet das nach, indem er den Intent
    auch beim Impuls setzt: Genau dieser Wert hat im Bestand entschieden.
    """
    return {
        "user_id":       "test_gv_impuls",
        "character_id":  "test_gv_impuls",
        "event_source":  quelle,
        "event_payload": payload if payload is not None else {},
        "external":      Personality(emotion=Emotion(**emotionsfelder)),
    }


def _impuls(**emotionsfelder: str | float) -> dict:
    """Ein Turn, dessen Reiz ausdruecklich Novas eigener Gedanke ist."""
    return _turn({"reiz_herkunft": "eigener_impuls"}, "character",
                 **emotionsfelder)


def _lauf(zustand: dict) -> dict:
    """Laesst den Node echt laufen und gibt den ganzen Zustand zurueck.

    Nur der LLM-Aufruf ist ersetzt; das Tor, die Laengenrechnung und die
    Landschaft laufen — und um deren Zusammenspiel geht es hier.

    **Die Strategie wird bewusst nicht mitgegeben.** `korridor_pruefen` leert
    jede Strategie, die das Repertoire der getroffenen Landschaft nicht
    fuehrt; eine erwartete Strategie im Zeugen haenge damit an einer Tabelle,
    die dieser Test gar nicht prueft.
    """
    with patch.object(gv_modul, "_hypothese_destillieren",
                      return_value=("Die Hypothese des Laufs", {})):
        return gv_modul.gespraechsvektor(zustand)


class DasTorGreiftBeimEigenenImpulsNichtTest(unittest.TestCase):
    """Der Defekt: ein Wert ueber den vorigen Turn entschied ueber diesen."""

    def test_kein_skip_bei_eigenem_impuls(self) -> None:
        """Auch mit genau dem Intent, der 15 von 20 Impulsen gekostet hat."""
        self.assertFalse(gv_modul._ist_skip(_impuls(intent="meta")))

    def test_keine_der_drei_marken_weist_einen_impuls_ab(self) -> None:
        """Nicht nur `meta` — das Tor gilt fuer den Impuls als Ganzes nicht."""
        for intent in SKIP_INTENTS:
            with self.subTest(intent=intent):
                self.assertFalse(gv_modul._ist_skip(_impuls(intent=intent)))

    def test_der_impuls_denkt_voraus(self) -> None:
        """Die Wirkung am Ergebnis, nicht nur am Tor.

        Ohne diesen Zeugen koennte das Tor durchlassen und eine Stufe
        spaeter etwas anderes den Lauf beenden.
        """
        zustand: dict = _lauf(_impuls(
            intent="meta", emotion="begeisterung", arousal=0.8,
            relationship_dynamic="vertrauen", language_style="locker",
        ))

        self.assertEqual(gv_modul.VORAUSDENKEN_GELAUFEN,
                         zustand["gv_detail"]["vorausdenken"])
        self.assertTrue(zustand["gv_detail"]["strategie_aktiv"])

    def test_die_hypothese_erreicht_den_zustand(self) -> None:
        """Der Weg, an dessen Ende der Verfasser-Block haengt.

        `vorausdenken` allein genuegt nicht: Die Marke koennte stehen und das
        Feld leer bleiben — genau die Lage, in der der Verfasser bisher gar
        keinen Block bekam.
        """
        zustand: dict = _lauf(_impuls(
            intent="meta", emotion="begeisterung", arousal=0.8,
            relationship_dynamic="vertrauen", language_style="locker",
        ))

        self.assertEqual("Die Hypothese des Laufs", zustand["gespraechsvektor"])

    def test_der_uebersprungene_nutzer_turn_bleibt_ohne_hypothese(self) -> None:
        """Die Gegenprobe dazu: Beim Skip bleibt das Feld leer."""
        zustand: dict = _lauf(_turn(intent="meta"))

        self.assertEqual("", zustand["gespraechsvektor"])
        self.assertEqual(gv_modul.VORAUSDENKEN_SKIP,
                         zustand["gv_detail"]["vorausdenken"])


class DerNutzerTurnBehaeltSeinTorTest(unittest.TestCase):
    """Der positive Zwilling. Ohne ihn waere ein totes Tor ebenfalls gruen."""

    def test_meta_weist_einen_nutzer_turn_weiterhin_ab(self) -> None:
        self.assertTrue(gv_modul._ist_skip(_turn(intent="meta")))

    def test_alle_drei_marken_weisen_einen_nutzer_turn_ab(self) -> None:
        for intent in SKIP_INTENTS:
            with self.subTest(intent=intent):
                self.assertTrue(gv_modul._ist_skip(_turn(intent=intent)))

    def test_ein_gewoehnlicher_intent_geht_durch(self) -> None:
        """Die Gegenprobe zur Gegenprobe: Das Tor sperrt nicht alles."""
        self.assertFalse(gv_modul._ist_skip(_turn(intent="knowledge")))

    def test_der_thinker_retry_behaelt_das_tor(self) -> None:
        """Gleiche Quelle wie der Impuls, aber eine echte Nutzer-Aeusserung.

        Wer beides ueber `event_source` unterschiede, raet — deshalb steht
        der Herkunfts-Marker ausdruecklich im Payload.
        """
        self.assertTrue(gv_modul._ist_skip(
            _turn({"thinker_unsicher_retry": True}, "character", intent="meta")))


class OhneWahrnehmungBleibtDasTorOffenTest(unittest.TestCase):
    """Ein fehlendes `external` ist kein Grund zu schweigen."""

    def test_ohne_external_kein_skip(self) -> None:
        zustand: dict = _turn()
        zustand["external"] = None

        self.assertFalse(gv_modul._ist_skip(zustand))


if __name__ == "__main__":
    unittest.main()


class DieAufgabeFolgtDemAusloeserTest(unittest.TestCase):
    """Der Knoten fuehrt den Faden des Ausloesers weiter — und der wechselt.

    **Die Aufgabe ist auf die Sicht des Ausloesers ausgerichtet, nicht auf den
    Kanal.** Sie fragt, was ihn beschaeftigt und welcher Gedanke bei ihm als
    naechstes kommt; der Knoten soll dessen Absicht erkennen und weiterfuehren,
    damit Nova beteiligter wirkt statt nur zu antworten.

    Meist ist der Ausloeser der Nutzer. **Auf einem eigenen Impuls ist es
    Nova** — und dann fragt die Nutzer-Fassung nach der falschen Seite: Der
    Faden, der weitergefuehrt werden soll, ist ihr eigener.
    `[gemessen 10.09.2026]` 154 von 1350 Turns tragen `eigener_impuls` (11,4 %).

    Zeuge: Die Erwartung stammt aus der Setzung des Eigentuemers vom
    11.09.2026, nicht aus dem Code — dieselbe Unterscheidung, die das Skip-Tor
    oben schon trifft.
    """

    def _system_prompt(self, zustand: dict) -> str:
        """Faengt den gebauten System-Prompt an der Modellgrenze ab.

        Gefangen wird am `submit_sync`, also an der Grenze zum Modell — nicht
        an der Funktion, die den Block auswaehlt. Ein Zeuge auf den Erzeuger
        bliebe gruen, wenn der Aufruf wegfiele.
        """
        gefangen: dict = {}

        def fangen(anfrage: object) -> object:
            gefangen["system"] = getattr(anfrage, "system", "") or ""
            return SimpleNamespace(text="Hypothese", token_total=0)

        with patch.object(gv_modul.model_service.chat, "submit_sync", fangen):
            gv_modul._hypothese_destillieren(
                zustand, max_laenge=1, resonanz_kontext="",
            )
        return str(gefangen.get("system", ""))

    def test_der_nutzer_turn_fragt_nach_dem_nutzer(self) -> None:
        prompt: str = self._system_prompt(_turn(intent="knowledge"))

        self.assertIn("Was beschaeftigt den Nutzer", prompt)
        self.assertNotIn("Was beschaeftigt Nova", prompt)

    def test_der_eigene_impuls_fragt_nach_nova(self) -> None:
        prompt: str = self._system_prompt(_impuls(intent="knowledge"))

        self.assertIn("Was beschaeftigt Nova", prompt)
        self.assertNotIn("Was beschaeftigt den Nutzer", prompt)

    def test_der_impuls_sagt_ausdruecklich_wessen_faden_gilt(self) -> None:
        """Ohne den Satz waere die gedrehte Frage nur eine Umbenennung."""
        prompt: str = self._system_prompt(_impuls(intent="knowledge"))

        self.assertIn("Anstoss dieses Turns kam von Nova selbst", prompt)

    def test_der_thinker_retry_bleibt_beim_nutzer(self) -> None:
        """Gleiche Quelle, echte Nutzer-Aeusserung — also die Nutzer-Fassung."""
        prompt: str = self._system_prompt(
            _turn({}, "character", intent="knowledge")
        )

        self.assertIn("Was beschaeftigt den Nutzer", prompt)
