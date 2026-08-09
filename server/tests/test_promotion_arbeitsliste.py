"""Tests fuer die Arbeitsliste der LZG-Promotion.

Ziel: Ein Promotionsauftrag geht nicht verloren, wenn seine Verarbeitung
scheitert. Bis zum 09.08.2026 nahm `invoke` ihn per `lpop` aus der Liste,
BEVOR die Arbeit begann — scheiterte sie, war die Zeile weg, und nichts
reihte sie je wieder ein: Der Erzeuger schreibt nur bei einem neuen Turn.
Der KZG-Hash ueberlebte seine sieben bis dreissig Tage und wurde nie
promotet.

Belegt am 09.08.2026 an zwei echten Auftraegen mit Salienz 0,94: beide
verbraucht, beide gescheitert, das Langzeitgedaechtnis blieb bei null.

Zwei Zusicherungen, und die zweite ist die, die vorher fehlte:

  1. Was gruen durchlaeuft, ist aus beiden Listen verschwunden.
  2. Was rot laeuft, liegt in der Arbeitsliste — sichtbar, zaehlbar, und
     beim naechsten Lauf zurueckgelegt.

Dazu die Meldung: Ein Lauf, in dem ALLES scheitert, sagte vorher
"Queue leer — nichts zu tun" auf debug. Das ist die Sorte Stille, die einen
Verlust wie Arbeitslosigkeit aussehen laesst.

Redis ist ein Fake mit echter Listen-Semantik statt eines MagicMock — wie in
`test_promotion_queue_dubletten.py`. Geprueft wird, was am Ende in den Listen
steht, nicht welche Methoden gerufen wurden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import patch

from agents.base import AgentState
from agents.synapsen_promotion.agent import SynapsenPromotionAgent

AGENT_MODUL: str = "agents.synapsen_promotion.agent"
AGENT_LOGGER: str = "ki_server.agents.synapsen_promotion"


class FakeRedis:
    """Minimal-Redis mit den vier Listen-Operationen, die `invoke` nutzt."""

    def __init__(self, listen: dict[str, list[str]] | None = None) -> None:
        """Legt die Listen an; Hashes entstehen beim ersten Zugriff."""
        self.listen: dict[str, list[str]] = {k: list(v) for k, v in (listen or {}).items()}
        self.hashes: dict[str, dict[str, int]] = {}

    def lmove(self, quelle: str, ziel: str, woher: str, wohin: str) -> str | None:
        """Verschiebt einen Eintrag atomar — der Kern der Arbeitsliste."""
        eintraege: list[str] = self.listen.get(quelle, [])
        if not eintraege:
            return None
        wert: str = eintraege.pop(0) if woher == "LEFT" else eintraege.pop()
        zielliste: list[str] = self.listen.setdefault(ziel, [])
        if wohin == "LEFT":
            zielliste.insert(0, wert)
        else:
            zielliste.append(wert)
        return wert

    def lrem(self, key: str, anzahl: int, wert: str) -> int:
        """Entfernt genau einen Eintrag nach Wert."""
        eintraege: list[str] = self.listen.get(key, [])
        if wert in eintraege:
            eintraege.remove(wert)
            return 1
        return 0

    def lindex(self, key: str, index: int) -> str | None:
        """Blick auf einen Eintrag, ohne ihn zu bewegen."""
        eintraege: list[str] = self.listen.get(key, [])
        try:
            return eintraege[index]
        except IndexError:
            return None

    def hincrby(self, key: str, feld: str, betrag: int) -> int:
        """Zaehlt den Versuchszaehler hoch und gibt den neuen Stand."""
        hash_: dict[str, int] = self.hashes.setdefault(key, {})
        hash_[feld] = hash_.get(feld, 0) + betrag
        return hash_[feld]

    def hdel(self, key: str, feld: str) -> int:
        """Loescht einen Versuchszaehler."""
        return 1 if self.hashes.get(key, {}).pop(feld, None) is not None else 0

    def liste(self, key: str) -> list[str]:
        """Der Bestand einer Liste — fuer die Zusicherungen im Test."""
        return self.listen.get(key, [])


def _auftrag(nummer: int) -> str:
    return json.dumps({
        "aufgabe": "lzg_promotion", "user_id": "meister",
        "key": f"kzg:meister:nova:{nummer}", "salienz": 0.9,
    })


def _zustand() -> AgentState:
    return {
        "aufgabe": "Test", "aufgabe_typ": "workflow",
        "agent_name": "synapsen_promotion", "kontext": {"user_id": "meister"},
        "parameter": {}, "schritte": [], "ergebnis": None,
        "status": "laufend", "rueckfrage": None, "fehler": None,
    }


class GescheiterterAuftragBleibtLiegenTest(unittest.TestCase):
    """Der Zeuge fuer den Defekt: Rot darf den Auftrag nicht verlieren."""

    def test_ein_fehler_laesst_den_auftrag_in_der_arbeitsliste(self) -> None:
        """Das ZIEL: der gescheiterte Auftrag ist danach auffindbar."""
        fake = FakeRedis({"queue:meister": [_auftrag(1)]})
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", side_effect=RuntimeError("Worker aus")):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["fehler"], 1)
        self.assertEqual(ergebnis["promotet"], 0)
        self.assertEqual(fake.liste("queue:meister"), [])
        self.assertEqual(fake.liste("queue:meister:arbeit"), [_auftrag(1)],
                         "Der gescheiterte Auftrag muss in der Arbeitsliste liegen")

    def test_ein_gruener_auftrag_verschwindet_aus_beiden_listen(self) -> None:
        """Die Gegenprobe: Erfolg darf nichts liegen lassen."""
        fake = FakeRedis({"queue:meister": [_auftrag(1), _auftrag(2)]})
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["promotet"], 2)
        self.assertEqual(fake.liste("queue:meister"), [])
        self.assertEqual(fake.liste("queue:meister:arbeit"), [])

    def test_die_reste_eines_abgebrochenen_laufs_kommen_nach_vorn_zurueck(self) -> None:
        """Souveraenitaet: Wer laeuft, laeuft allein — ein voller Topf ist Rest.

        Und die Reihenfolge zaehlt: Die Reste sind aelter als das, was
        inzwischen dazukam, und gehoeren deshalb VOR die Warteschlange.
        """
        fake = FakeRedis({
            "queue:meister":        [_auftrag(3)],
            "queue:meister:arbeit": [_auftrag(1), _auftrag(2)],
        })
        agent = SynapsenPromotionAgent()
        gesehen: list[str] = []

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten",
                          side_effect=lambda a, u: gesehen.append(a["key"])):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["zurueckgelegt"], 2)
        self.assertEqual(ergebnis["promotet"], 3)
        self.assertEqual(
            gesehen,
            ["kzg:meister:nova:1", "kzg:meister:nova:2", "kzg:meister:nova:3"],
            "Die Reste gehoeren in ihrer urspruenglichen Reihenfolge nach vorn",
        )


class DerZaehlerBeendetDenKreiselTest(unittest.TestCase):
    """Ein dauerhaft unverarbeitbarer Auftrag darf nicht ewig kreisen.

    Er verbrennt sonst alle 300 s den einzigen Pixie-Platz — genau den, um
    den ohnehin 92 % der Takte scheitern. Nach `MAX_PROMOTION_RUECKSTELLUNGEN`
    Rueckstellungen geht er auf den Fehlerstapel: nicht wiederholt, aber
    gezaehlt und lesbar.
    """

    def _lauf(self, fake: FakeRedis) -> dict:
        agent = SynapsenPromotionAgent()
        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", side_effect=RuntimeError("dauerhaft")):
            return agent.invoke(_zustand())["ergebnis"]

    def test_nach_zwei_rueckstellungen_wandert_er_auf_den_fehlerstapel(self) -> None:
        """Das ZIEL: drei Verarbeitungsversuche, dann Schluss — aber nicht weg."""
        fake = FakeRedis({"queue:meister": [_auftrag(1)]})

        erster = self._lauf(fake)
        self.assertEqual(erster["fehler"], 1)
        self.assertEqual(fake.liste("queue:meister:arbeit"), [_auftrag(1)])

        zweiter = self._lauf(fake)
        self.assertEqual(zweiter["zurueckgelegt"], 1, "erste Rueckstellung")

        dritter = self._lauf(fake)
        self.assertEqual(dritter["zurueckgelegt"], 1, "zweite Rueckstellung")

        vierter = self._lauf(fake)
        self.assertEqual(vierter["endgueltig"], 1, "jetzt auf den Fehlerstapel")
        self.assertEqual(vierter["zurueckgelegt"], 0)

        self.assertEqual(fake.liste("queue:meister:gescheitert"), [_auftrag(1)],
                         "Der Auftrag ist nicht verschwunden, er ist benannt gescheitert")
        self.assertEqual(fake.liste("queue:meister"), [])
        self.assertEqual(fake.liste("queue:meister:arbeit"), [])

    def test_ein_unlesbarer_eintrag_kreist_gar_nicht_erst(self) -> None:
        """Was nie gruen werden kann, braucht keine drei Versuche."""
        fake = FakeRedis({"queue:meister:arbeit": ["{kein json"]})
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["endgueltig"], 1)
        self.assertEqual(ergebnis["zurueckgelegt"], 0)
        self.assertEqual(fake.liste("queue:meister:gescheitert"), ["{kein json"])

    def test_ein_erfolg_setzt_den_zaehler_zurueck(self) -> None:
        """Zwei Fehlversuche und dann gruen heisst: naechstes Mal wieder drei.

        Ohne das Zuruecksetzen liefe ein Auftrag, der einmal gestolpert ist,
        beim uebernaechsten Fehler sofort auf den Stapel — der Zaehler wuerde
        die Kennung bestrafen statt den Vorgang.
        """
        fake = FakeRedis({"queue:meister": [_auftrag(1)]})
        self._lauf(fake)
        self.assertEqual(fake.hashes.get("queue:meister:versuche", {}), {})

        agent = SynapsenPromotionAgent()
        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["promotet"], 1)
        self.assertEqual(fake.hashes.get("queue:meister:versuche", {}), {},
                         "Nach dem Erfolg steht kein Zaehler mehr")


class EinLaufOhneErfolgSagtEsTest(unittest.TestCase):
    """Die zweite Haelfte des Defekts: die Meldung.

    `promotet == 0` hiess vorher "Queue leer — nichts zu tun" auf debug,
    auch wenn jeder Eintrag gescheitert war.
    """

    def test_alles_gescheitert_meldet_nicht_queue_leer(self) -> None:
        """Das ZIEL: Verlust darf nicht wie Arbeitslosigkeit aussehen."""
        fake = FakeRedis({"queue:meister": [_auftrag(1), _auftrag(2)]})
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", side_effect=RuntimeError("kaputt")), \
             self.assertLogs(AGENT_LOGGER, level="INFO") as protokoll:
            agent.invoke(_zustand())

        meldungen: str = "\n".join(protokoll.output)
        self.assertIn("2 gescheitert", meldungen)
        self.assertNotIn("nichts zu tun", meldungen)

    def test_eine_wirklich_leere_queue_bleibt_still(self) -> None:
        """Die Gegenprobe: Ohne Arbeit soll auch nichts gemeldet werden."""
        fake = FakeRedis({})
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             self.assertLogs(AGENT_LOGGER, level="DEBUG") as protokoll:
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis, {"promotet": 0, "fehler": 0,
                                    "zurueckgelegt": 0, "endgueltig": 0})
        self.assertIn("nichts zu tun", "\n".join(protokoll.output))


if __name__ == "__main__":
    unittest.main()
