"""Zeugen darueber, dass der periodische Promotions-Lauf jedes Paar erreicht.

Ziel: Was in einer Promotions-Queue liegt, wird abgearbeitet — gleich, welchem
Paar die Queue gehoert.

**Bis zum 01.09.2026 erreichte er genau eines.** `invoke` las

    user_id = state["kontext"].get("user_id", "") or DEFAULT_USER_ID

und der **periodische** Pixie-Lauf uebergibt keinen Kontext. Der Agent nahm den
Rueckfall `meister`, sah in `queue:meister` nach und meldete alle fuenf Minuten
*„Queue leer — nichts zu tun"*. Die Meldung stimmte fuer das Paar, in das er
schaute.

`[gemessen]` 01.09.2026: **13 Promotionsauftraege ueber fuenf Paare** lagen im
Bestand — `b1_live` 2, `nmcp_probe` 5, `nmcp_live` 2, `sektorprobe` 2,
`scheibe2probe` 2. Zwei davon waren zwei Minuten alt, elf standen laenger. Fuer
jedes Paar ausser dem Standard gilt: Der KZG-Hash ueberlebt seine sieben bis
dreissig Tage und wird nie promotet — **das Langzeitgedaechtnis eines solchen
Paars bleibt leer**, und `praegung_beruehrung` damit auch, weil eine
Reaktivierung LZG-Knoten braucht.

Die Zusicherungen:

  1. **Ein periodischer Lauf erreicht alle Paare mit Auftraegen.** Ohne diese
     Zusicherung ist der Fix mit einer Fassung erfuellt, die weiterhin nur eines
     nimmt.
  2. **Ein Lauf mit ausdruecklicher `user_id` bleibt bei diesem Paar.** Sonst
     wuerde ein gezielter Aufruf stillschweigend fremde Queues leeren.
  3. **Nebenlisten sind keine Paare.** `queue:{paar}:arbeit` und `:versuche`
     duerfen nicht als eigene Warteschlangen gelesen werden.

     > Eine vierte Zusicherung stand hier und ist **gestrichen**: dass fremde
     > Aufgabenarten in derselben Queue liegen bleiben. Die Shadow-Queue liegt
     > seit dem 15.08.2026 in PostgreSQL; `queue:{paar}` traegt nur
     > Promotions-Auftraege. Ein Zeuge auf einen Fall, den der Bestand nicht
     > hervorbringt, prueft nichts.
  4. **Die Zaehlung im Ergebnis summiert ueber alle Paare.** Eine Zahl, die nur
     das letzte Paar meldet, waere von einem Lauf ohne Arbeit nicht zu
     unterscheiden.

Redis ist ein Fake mit echter Listen-Semantik — wie in
`test_promotion_arbeitsliste.py`. Geprueft wird, was am Ende in den Listen
steht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from collections.abc import Iterator
from unittest.mock import patch

from agents.base import AgentState
from agents.synapsen_promotion.agent import SynapsenPromotionAgent

AGENT_MODUL: str = "agents.synapsen_promotion.agent"

#: Der Ausfall, den der Zeuge herbeifuehrt — als Konstante, damit die Meldung
#: nicht im Ausdruck steht.
AUSFALL: str = "Worker aus"


class FakeRedis:
    """Minimal-Redis mit den Operationen, die `invoke` nutzt — plus `scan_iter`."""

    def __init__(self, listen: dict[str, list[str]] | None = None) -> None:
        """Legt die Listen an; Hashes entstehen beim ersten Zugriff."""
        self.listen: dict[str, list[str]] = {k: list(v) for k, v in (listen or {}).items()}
        self.hashes: dict[str, dict[str, int]] = {}

    def scan_iter(self, match: str = "*", count: int = 100) -> Iterator[str]:
        """Die Schluessel, die zum Muster passen — nur `queue:*` wird gebraucht."""
        vorsilbe: str = match.rstrip("*")
        for key in list(self.listen):
            if key.startswith(vorsilbe):
                yield key

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


def _promotion(paar: str, nummer: int) -> str:
    return json.dumps({
        "aufgabe": "lzg_promotion", "user_id": paar,
        "key": f"kzg:{paar}:nova:{nummer}", "salienz": 0.9,
    })


def _zustand(user_id: str | None = None) -> AgentState:
    """Der periodische Lauf uebergibt **keinen** Kontext — das ist der Fall."""
    return {
        "aufgabe": "Test", "aufgabe_typ": "workflow",
        "agent_name": "synapsen_promotion",
        "kontext": {"user_id": user_id} if user_id else {},
        "parameter": {}, "schritte": [], "ergebnis": None,
        "status": "laufend", "rueckfrage": None, "fehler": None,
    }


class PeriodischerLaufErreichtAllePaareTest(unittest.TestCase):
    """Der Zeuge fuer den Defekt: ein Lauf ohne Kontext darf keines auslassen."""

    def test_ein_periodischer_lauf_arbeitet_jedes_paar_ab(self) -> None:
        fake = FakeRedis({
            "queue:meister":       [_promotion("meister", 1)],
            "queue:scheibe2probe": [_promotion("scheibe2probe", 2)],
            "queue:b1_live":       [_promotion("b1_live", 3)],
        })
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(
            ergebnis["promotet"], 3,
            "Ein periodischer Lauf hat nicht alle Paare erreicht — jedes ausser "
            "dem Standard staut sich unbegrenzt",
        )
        for paar in ("meister", "scheibe2probe", "b1_live"):
            self.assertEqual(fake.liste(f"queue:{paar}"), [], f"{paar} nicht geleert")

    def test_ein_gezielter_lauf_bleibt_bei_seinem_paar(self) -> None:
        """Sonst leerte ein Aufruf fuer ein Paar stillschweigend fremde Queues."""
        fake = FakeRedis({
            "queue:meister":       [_promotion("meister", 1)],
            "queue:scheibe2probe": [_promotion("scheibe2probe", 2)],
        })
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand("meister"))["ergebnis"]

        self.assertEqual(ergebnis["promotet"], 1)
        self.assertEqual(fake.liste("queue:meister"), [])
        self.assertEqual(
            len(fake.liste("queue:scheibe2probe")), 1,
            "Ein gezielter Lauf hat ein fremdes Paar mitgeleert",
        )

    def test_arbeitslisten_sind_keine_paare(self) -> None:
        """`:arbeit` und `:versuche` sind Nebenlisten, keine Warteschlangen.

        Wer die Paare aus `queue:*` ableitet, faengt sie mit — und zaehlte dann
        einen liegengebliebenen Rest als Arbeit eines neuen Paars.
        """
        fake = FakeRedis({
            "queue:meister":          [_promotion("meister", 1)],
            "queue:meister:arbeit":   [_promotion("meister", 9)],
            "queue:meister:versuche": [],
        })
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        # Der Rest aus `:arbeit` wird zurueckgelegt und mitverarbeitet — das ist
        # die Mechanik der Arbeitsliste. Was **nicht** passieren darf: dass
        # `meister:arbeit` als eigenes Paar gilt und eine Queue `queue:meister:arbeit:arbeit`
        # entsteht.
        self.assertEqual(
            fake.liste("queue:meister:arbeit:arbeit"), [],
            "Eine Nebenliste wurde als Paar gelesen",
        )
        self.assertGreaterEqual(ergebnis["promotet"], 1)

    def test_die_zaehlung_summiert_ueber_alle_paare(self) -> None:
        """Eine Zahl, die nur das letzte Paar meldet, verbirgt die Arbeit."""
        fake = FakeRedis({
            "queue:a": [_promotion("a", 1), _promotion("a", 2)],
            "queue:b": [_promotion("b", 3)],
        })
        agent = SynapsenPromotionAgent()

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", return_value=None):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["promotet"], 3)

    def test_ein_fehler_in_einem_paar_stoppt_die_uebrigen_nicht(self) -> None:
        """Sonst genuegte ein kaputtes Paar, um alle anderen auszuhungern."""
        fake = FakeRedis({
            "queue:kaputt": [_promotion("kaputt", 1)],
            "queue:heil":   [_promotion("heil", 2)],
        })
        agent = SynapsenPromotionAgent()

        def launisch(auftrag: dict, user_id: str) -> None:
            if user_id == "kaputt":
                raise RuntimeError(AUSFALL)

        with patch(f"{AGENT_MODUL}.redis_client", fake), \
             patch.object(agent, "_eintrag_verarbeiten", side_effect=launisch):
            ergebnis = agent.invoke(_zustand())["ergebnis"]

        self.assertEqual(ergebnis["fehler"], 1)
        self.assertEqual(
            ergebnis["promotet"], 1,
            "Ein gescheitertes Paar hat die uebrigen mitgerissen",
        )
        self.assertEqual(
            fake.liste("queue:kaputt:arbeit"), [_promotion("kaputt", 1)],
            "Der gescheiterte Auftrag liegt nicht in seiner Arbeitsliste",
        )


if __name__ == "__main__":
    unittest.main()
