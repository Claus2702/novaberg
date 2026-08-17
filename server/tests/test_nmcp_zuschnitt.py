"""Tests: Ein Dienst erhaelt, was er angemeldet hat — nicht, was vorhanden ist.

Ziel: Ein angemeldeter Clipboard-Wert kommt an, ein nicht angemeldeter wird
entfernt und gemeldet, und ein Wert, der keine Zusage ist, bleibt unberuehrt.

Zeugen dieser Datei:
  * **Die Gegenprobe laeuft in beide Richtungen.** Nur zu pruefen, dass der
    ungebetene Wert verschwindet, liesse offen, ob der Schnitt einfach alles
    entfernt — deshalb wird derselbe Schluessel einmal mit und einmal ohne
    Anmeldung gefahren.
  * **Der Schnitt wird am Engpass geprueft, nicht am Dispatch.** `invoke` ist
    die Stelle, durch die jeder Dienst laeuft; ein Zeuge auf einem einzelnen
    Dispatch sagte nichts ueber die dreizehn anderen.
  * **Ein Fremdschluessel ist der Randfall, der zaehlt.** Der Schnitt darf nur
    zusagbare Schluessel anfassen; wuerde er nach Gutdunken entfernen,
    verloeren alle Dienste ihre Nutzdaten und kein Test saehe es.
  * **Der Bestand wird mitgefahren:** `kzg` meldet `timeline_id` an und muss
    ihn nach dem Schnitt noch haben, sonst legt der Schreibpfad einen
    zweiten Erinnerungs-Anker an.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from agents import AgentRegistry, discover_agents
from agents.base import AgentState, BaseAgent, Bedarf
from agents.nmcp import ZUSAGEN
from plugins import discover_managers


class _Zuschnitt(BaseAgent):
    """Dienst, der nur den Zuschnitt sichtbar macht — kein Subgraph."""

    def __init__(self, bedarf: list[Bedarf] | None = None) -> None:
        """Legt einen Dienst mit dem uebergebenen Bedarf an."""
        self._bedarf = bedarf or []

    @property
    def name(self) -> str:
        """Name des Dienstes."""
        return "zuschnitt"

    @property
    def bedarf(self) -> list[Bedarf]:
        """Der angemeldete Bedarf."""
        return self._bedarf

    def build_graph(self) -> None:
        """Wird nicht gebraucht — der Test ruft nur den Schnitt."""
        raise NotImplementedError

    def schneiden(self, kontext: dict) -> dict:
        """Faehrt den Schnitt und gibt den beschnittenen Kontext zurueck.

        Vorbedingung: `kontext` ist ein Dict.
        Nachbedingung: der Kontext nach dem Schnitt.
        """
        state: AgentState = {
            "aufgabe": "probe", "aufgabe_typ": "workflow",
            "agent_name": self.name, "kontext": kontext, "parameter": {},
            "schritte": [], "ergebnis": None, "status": "laufend",
            "rueckfrage": None, "fehler": None,
        }
        return self._zustand_zuschneiden(state)["kontext"]


_SCHLUESSEL = "timeline_id"


class ZuschnittTest(unittest.TestCase):
    """Der Schnitt trennt Angemeldetes von Ungebetenem."""

    def setUp(self) -> None:
        """Stellt sicher, dass der Probeschluessel eine Zusage ist."""
        self.assertIn(
            _SCHLUESSEL, ZUSAGEN,
            "Der Test faehrt einen echten zusagbaren Schluessel",
        )

    def test_angemeldeter_wert_kommt_an(self) -> None:
        """Die eine Haelfte der Gegenprobe: mit Anmeldung bleibt der Wert."""
        zusage = ZUSAGEN[_SCHLUESSEL]
        dienst = _Zuschnitt([
            Bedarf(zusage.schluessel, zusage.typ, zusage.bedeutung)
        ])
        kontext = dienst.schneiden({_SCHLUESSEL: 4711, "user_id": "probe"})
        self.assertEqual(kontext[_SCHLUESSEL], 4711)

    def test_nicht_angemeldeter_wert_wird_entfernt(self) -> None:
        """Die andere Haelfte: ohne Anmeldung verschwindet derselbe Wert.

        Beide Haelften fahren denselben Schluessel mit demselben Wert. Ohne
        die erste Haelfte liesse dieser Test offen, ob der Schnitt einfach
        alles entfernt.
        """
        dienst = _Zuschnitt([])
        kontext = dienst.schneiden({_SCHLUESSEL: 4711, "user_id": "probe"})
        self.assertNotIn(_SCHLUESSEL, kontext)

    def test_fremdschluessel_bleibt_unberuehrt(self) -> None:
        """Der Schnitt fasst nur zusagbare Schluessel an.

        Wuerde er nach Gutdunken entfernen, verloeren alle Dienste ihre
        Nutzdaten — und kein Zeuge saehe es, weil die Clipboards weiterhin
        richtig behandelt wuerden.
        """
        dienst = _Zuschnitt([])
        kontext = dienst.schneiden({
            "user_id": "probe", "beobachter": "user", "turn_id": "abc",
        })
        self.assertEqual(
            kontext, {"user_id": "probe", "beobachter": "user", "turn_id": "abc"},
        )

    def test_leerer_kontext_bleibt_leer(self) -> None:
        """Ein Dienst ohne Kontext ist kein Fehlerfall."""
        self.assertEqual(_Zuschnitt([]).schneiden({}), {})

    def test_kontext_ohne_dict_wird_gemeldet_nicht_geworfen(self) -> None:
        """Ein defekter Kontext haelt den Dienst nicht an.

        Der Schnitt ist eine Zusicherung ueber den Zustand, kein Riegel: Ein
        Dienst, der wegen eines Zuschnitt-Problems gar nicht laeuft, waere
        teurer als einer, der ohne Schnitt laeuft und es gemeldet bekommt.
        """
        dienst = _Zuschnitt([])
        state: AgentState = {
            "aufgabe": "probe", "aufgabe_typ": "workflow",
            "agent_name": "zuschnitt", "kontext": None, "parameter": {},
            "schritte": [], "ergebnis": None, "status": "laufend",
            "rueckfrage": None, "fehler": None,
        }
        self.assertIs(dienst._zustand_zuschneiden(state), state)


class BestandZuschnittTest(unittest.TestCase):
    """Der Bestand muss den Schnitt ueberleben."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand, nicht seine Nachbildung."""
        discover_managers()
        discover_agents()

    def test_kzg_behaelt_seinen_angemeldeten_anker(self) -> None:
        """`kzg` meldet `timeline_id` an und muss ihn nach dem Schnitt haben.

        Faellt der Wert weg, legt der KZG-Schreibpfad einen zweiten
        Erinnerungs-Anker fuer denselben Tag an — ein Defekt, den kein
        Fehler meldet, weil beide Anker fuer sich gueltig sind.
        """
        agent = AgentRegistry.finden("kzg")
        self.assertIsNotNone(agent, "kzg muss im Bestand sein")
        self.assertIn(
            _SCHLUESSEL, {b.schluessel for b in agent.bedarf},
            "kzg muss timeline_id anmelden, sonst schneidet der Schnitt ihn weg",
        )

        state: AgentState = {
            "aufgabe": "kzg_verarbeitung", "aufgabe_typ": "workflow",
            "agent_name": "kzg",
            "kontext": {"user_id": "probe", _SCHLUESSEL: 99},
            "parameter": {}, "schritte": [], "ergebnis": None,
            "status": "laufend", "rueckfrage": None, "fehler": None,
        }
        beschnitten = agent._zustand_zuschneiden(state)
        self.assertEqual(beschnitten["kontext"][_SCHLUESSEL], 99)

    def test_kein_dienst_verliert_einen_angemeldeten_wert(self) -> None:
        """Ueber den ganzen Bestand: jeder angemeldete Bedarf kommt durch."""
        for name, agent in AgentRegistry.alle().items():
            angemeldet = {b.schluessel for b in agent.bedarf}
            if not angemeldet:
                continue
            kontext = {s: f"wert-{s}" for s in angemeldet}
            state: AgentState = {
                "aufgabe": "probe", "aufgabe_typ": "workflow",
                "agent_name": name, "kontext": dict(kontext), "parameter": {},
                "schritte": [], "ergebnis": None, "status": "laufend",
                "rueckfrage": None, "fehler": None,
            }
            self.assertEqual(
                agent._zustand_zuschneiden(state)["kontext"], kontext,
                f"Dienst '{name}' verliert einen angemeldeten Wert",
            )


if __name__ == "__main__":
    unittest.main()
