"""Tests: Jeder Kandidat, den der Heartbeat waehlt, findet auch einen Agenten.

**Der Anlass ist ein Defekt, den der Umbau vom 15.08.2026 erzeugt hat.** Die
Shadow-Queue zog nach PostgreSQL, und ihre Kandidaten tragen seither
`quelle = "shadow_auftrag"` statt `"queue"`. Der Erzeuger wurde geaendert, die
Schreibpfade wurden geaendert, der Abschluss wurde geaendert — und
`services/pixie/router.py` verzweigte weiter auf `== "queue"`.

Die Folge war still und vollstaendig: Der Heartbeat waehlte im
Dreissig-Sekunden-Takt einen Auftrag, der Router fand keinen Agenten, und der
Auftrag blieb liegen. **Kein einziger Shadow-Auftrag lief mehr.** Im Log stand
nur eine Warnung je Zyklus, und die sah aus wie der lange bekannte Fall
"Auftrag fuer einen Agenten, den es nicht gibt".

> **Wer einen Wert einfuehrt, muss seine Leser suchen — nicht nur seine
> Schreiber.** Die Zeugen des Umbaus pruefen den Erzeuger, die Auswahl und den
> Abschluss. Zwischen Auswahl und Abschluss steht der Router, und ihn hat
> niemand gefragt.

Diese Datei prueft deshalb die **Kette**, nicht ihre Glieder: Was
`kandidaten_sammeln` an `quelle`-Werten erzeugen kann, muss `route` kennen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import ast
import inspect
import unittest

from services.pixie import kandidaten as kandidaten_modul
from services.pixie import router as router_modul

# Die Aufgabenarten, fuer die ein Agent existiert. `vertiefen` fehlt hier
# absichtlich — der Agent ist Roadmap, und ein Auftrag dafuer soll laut
# scheitern statt still zu verschwinden.
GEBAUTE_AUFGABEN: tuple[str, ...] = ("recherche", "nachfragen")


def _erzeugte_quellen() -> set[str]:
    """Alle `quelle`-Werte, die die Kandidatensammlung schreiben kann.

    Aus dem Quelltext gelesen statt aufgezaehlt: Eine Aufzaehlung waere beim
    naechsten neuen Wert wieder still veraltet — genau der Fehler, den dieser
    Zeuge festhaelt.
    """
    baum: ast.Module = ast.parse(inspect.getsource(kandidaten_modul))
    quellen: set[str] = set()
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.Dict):
            continue
        # strict=False: Bei `{**anderes}` traegt ast.Dict ein None als Key,
        # und die Listen sind zwar gleich lang, aber strict=True waere
        # eine Zusicherung ueber fremde Syntax statt ueber diese Suche.
        for schluessel, wert in zip(knoten.keys, knoten.values, strict=False):
            if (
                isinstance(schluessel, ast.Constant) and schluessel.value == "quelle"
                and isinstance(wert, ast.Constant) and isinstance(wert.value, str)
            ):
                quellen.add(wert.value)
    return quellen


def _kandidat(quelle: str, aufgabe: str = "recherche") -> dict:
    """Ein Kandidat, wie ihn die Sammlung liefert."""
    return {
        "name": aufgabe,
        "prioritaet": 1.0,
        "prioritaet_basis": 1.0,
        "ueberfaellig_s": None,
        "quelle": quelle,
        "daten": {"aufgabe": aufgabe, "user_id": "meister", "thema": "Gravitation"},
        "auftrag_id": 1 if quelle == "shadow_auftrag" else None,
        "queue_key": None,
        "queue_raw": None,
        "schedule_key": None,
        "themen": "Gravitation",
    }


class JedeQuelleIstDemRouterBekanntTest(unittest.TestCase):
    """Die Kette Auswahl → Router darf keine Luecke haben."""

    def test_die_sammlung_erzeugt_die_erwarteten_quellen(self) -> None:
        """Vorbedingung des naechsten Falls: Der Scan findet ueberhaupt etwas.

        Ein leeres Ergebnis hiesse nicht "keine Luecke", sondern "der Zeuge
        sucht falsch" — und der Fall darunter waere dann leer und gruen.
        """
        quellen = _erzeugte_quellen()
        self.assertIn("shadow_auftrag", quellen)
        self.assertIn("queue", quellen)
        self.assertIn("periodisch", quellen)

    def test_jede_erzeugte_quelle_liefert_einen_agenten(self) -> None:
        """Fuer jede Quelle der Sammlung findet der Router einen Agenten.

        `periodisch` ist ausgenommen: Dort entscheidet der `schedule_key`,
        nicht die Aufgabenart, und ein leerer Schluessel darf None liefern.
        """
        for quelle in sorted(_erzeugte_quellen() - {"periodisch"}):
            with self.subTest(quelle=quelle):
                self.assertIsNotNone(
                    router_modul.route(_kandidat(quelle)),
                    f"Der Router kennt die Quelle '{quelle}' nicht. Der "
                    f"Heartbeat waehlt solche Kandidaten, findet keinen Agenten "
                    f"und der Auftrag bleibt liegen — still, mit einer Warnung "
                    f"je Zyklus, die wie ein fehlender Agent aussieht.",
                )

    def test_gebaute_aufgabenarten_finden_ihren_agenten(self) -> None:
        """Die Aufgabenarten mit Agenten werden aus der neuen Quelle aufgeloest."""
        for aufgabe in GEBAUTE_AUFGABEN:
            with self.subTest(aufgabe=aufgabe):
                self.assertIsNotNone(
                    router_modul.route(_kandidat("shadow_auftrag", aufgabe)),
                    f"'{aufgabe}' hat einen gebauten Agenten und muss aufloesen.",
                )

    def test_eine_unbekannte_aufgabe_loest_nicht_auf(self) -> None:
        """Die Gegenprobe: Der Router erfindet keinen Agenten.

        Ohne diesen Fall bestuende der Test oben auch dann, wenn `route`
        pauschal irgendetwas zurueckgaebe.
        """
        self.assertIsNone(
            router_modul.route(_kandidat("shadow_auftrag", "gibt_es_nicht")),
        )

    def test_der_router_ist_eine_zweite_registry(self) -> None:
        """`vertiefen` loest auf einen Namen auf, den die Registry nicht kennt.

        **Das ist kein Fehler dieses Bauteils, sondern der gemessene Zustand**
        und der Grund, warum 383 Auftraege im Bestand liegen: Der Router fuehrt
        mit `_QUEUE_ROUTING` eine handgepflegte Tabelle neben der automatischen
        Agent-Discovery (`novaberg-pixie.md` §2, PIXIE-ROUTING-DOPPELREGISTRY).
        Er loest `vertiefen` auf `vertiefung` auf; ein Agent dieses Namens
        existiert nicht.

        Der Fall steht hier, damit die Luecke **bezeugt** ist statt vermutet —
        und damit auffaellt, wenn jemand den Agenten baut, ohne ihn zu
        registrieren, oder die Tabelle aendert, ohne den Bestand zu pruefen.
        """
        from agents import AgentRegistry

        name = router_modul.route(_kandidat("shadow_auftrag", "vertiefen"))
        self.assertEqual(
            "vertiefung", name,
            "Die Routing-Tabelle bildet `vertiefen` weiterhin ab.",
        )
        self.assertIsNone(
            AgentRegistry.finden(name),
            "Sobald ein Agent 'vertiefung' existiert, ist dieser Fall "
            "gegenstandslos und die 383 wartenden Auftraege werden abgearbeitet "
            "— dann ist er zu streichen, nicht anzupassen.",
        )


if __name__ == "__main__":
    unittest.main()
