"""Tests für den [MASS]-Block des Verfassers (`graph/nodes/verfasser.py`).

Ziel: Der Verfasser ist der **zweite** Leser der Haltung. Das Konzept sieht
ihn von Anfang an vor — *„Ein eigener Knoten, vor der Verzweigung zum
Verfasser. Beide lesen das Ergebnis aus dem Zustand"* —, und genau daraus
folgt die Position des Knotens im Graphen. Bis zum 20.08.2026 löste sie
niemand ein: `haltung` kam in dem Modul nicht vor.

Die Zusicherungen:

  1. **Drei der fünf Größen sind fachlich und stehen im Block:** `umfang`
     (wie viel es zu sagen gibt), `fragen` (kommt eine Rückfrage vor) und
     `draengen` (steht ein Vorschlag im Stoff).
  2. **`naehe` und `waerme` stehen nicht darin.** Sie sind reiner Ton und
     bleiben beim Responder; sie hier zu wiederholen wäre die Doppelung, die
     der Umbau vom 13.08.2026 beseitigt hat.
  3. **Die Mengenangabe trägt den Turn-Bezug**, also dieselbe Spanne, die der
     Responder bekommt — sie bedeutet hier nur etwas anderes.
  4. **Fehlt die Haltung, fällt der Block laut aus**, nicht still.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from ei.haltung import GROESSEN, Groessenwert, Haltung
from ei.haltungssprache import spanne_fuer_turn, stoff_band, stoffzeilen
from graph.nodes import verfasser as verf_mod

VERFASSER_LOGGER: str = "ki_server.verfasser"


def _haltung(**werte: float) -> Haltung:
    """Eine Haltung mit Vorgabewert 0,50 je Größe, einzeln überschreibbar."""
    gebaut: dict[str, Groessenwert] = {}
    for name in GROESSEN:
        wert: float = werte.get(name, 0.50)
        gebaut[name] = Groessenwert(
            name=name, grundwert=0.50, modifikation=wert - 0.50,
            ergebnis=wert, art="neigung", ausloeser="", ausserhalb=False,
        )
    return Haltung(cluster="bier", werte=gebaut)


def _state(reiz: str = "Ein Reiz.", **felder: object) -> dict:
    """Ein Zustand, wie ihn der Verfasser liest."""
    zustand: dict = {
        "user_prompt":      reiz,
        "event_source":     "user",
        "event_payload":    {},
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "web_context": "",
        "session_turns":    [], "task_block": "",
        "gespraechsvektor": "", "gv_detail": {},
        "node_annotations": {},
        "haltung":          _haltung(),
        "user_intentionen": [],
    }
    zustand.update(felder)
    return zustand


class MassBlockTest(unittest.TestCase):
    """Der Block im fertigen System-Prompt."""

    def test_der_massblock_steht_im_prompt(self) -> None:
        """Die tragende Zusicherung: Der Verfasser sieht die Haltung."""
        prompt: str = verf_mod._build_system_prompt(_state())
        self.assertIn("[MASS]", prompt)
        self.assertIn("Menge: Stoff fuer", prompt)
        self.assertIn("Rueckfrage:", prompt)
        self.assertIn("Vorschlag:", prompt)

    def test_naehe_und_waerme_stehen_nicht_im_massblock(self) -> None:
        """Reiner Ton bleibt beim Responder — sonst steht er zweimal."""
        prompt: str = verf_mod._build_system_prompt(
            _state(haltung=_haltung(naehe=0.95, waerme=0.95)))
        block: str = prompt.split("[MASS]")[1]
        self.assertNotIn("ganz nah", block)
        self.assertNotIn("herzlich", block)

    def test_die_menge_traegt_den_turn_bezug(self) -> None:
        """Ein kurzer Gruß bestellt weniger Stoff als eine Sachfrage."""
        gruss: str = verf_mod._build_system_prompt(
            _state("Hey!", user_intentionen=["smalltalk"]))
        frage: str = verf_mod._build_system_prompt(
            _state("Erklaere mir die Tritiumvorkommen",
                   user_intentionen=["information_erfragen"]))
        eng = spanne_fuer_turn(0.50, len("Hey!"), ("smalltalk",))
        weit = spanne_fuer_turn(0.50, 33, ("information_erfragen",))
        self.assertLess(eng[1], weit[1])
        self.assertIn(f"{eng[0]} bis {eng[1]} Zeichen", gruss)
        self.assertIn(f"{weit[0]} bis {weit[1]} Zeichen", frage)

    def test_eine_verschlossene_haltung_verbietet_die_rueckfrage(self) -> None:
        """Ein niedriges `fragen` verbietet die Rückfrage im Stoff."""
        prompt: str = verf_mod._build_system_prompt(
            _state(haltung=_haltung(fragen=0.10)))
        self.assertIn("Rueckfrage: keine Rueckfrage", prompt)

    def test_eine_draengende_haltung_bestellt_den_vorschlag(self) -> None:
        """Ein hohes `draengen` bestellt Vorschlag und nächsten Schritt."""
        prompt: str = verf_mod._build_system_prompt(
            _state(haltung=_haltung(draengen=0.95)))
        self.assertIn("Vorschlag: ein Vorschlag und der naechste Schritt", prompt)

    def test_ohne_haltung_meldet_der_knoten_laut(self) -> None:
        """Fail loud statt stiller Auslassung.

        Ein weggelassener Block wäre von einer Lage ohne Vorgabe nicht zu
        unterscheiden.
        """
        zustand: dict = _state()
        zustand["haltung"] = None
        with self.assertLogs(VERFASSER_LOGGER, level="ERROR") as protokoll:
            prompt: str = verf_mod._build_system_prompt(zustand)
        self.assertNotIn("[MASS]", prompt)
        self.assertIn("haltungsraum", "\n".join(protokoll.output))

    def test_gegenprobe_ohne_den_block_fehlte_jede_mengenangabe(self) -> None:
        """Belegt, dass die Zeugen oben etwas prüfen.

        Der übrige Prompt des Verfassers trägt keine einzige Zeichenzahl —
        sein Auftrag nennt als Maß nur die Landschaft. Ohne den Block gäbe es
        also keine Mengenangabe, und genau das war der Zustand bis heute.
        """
        zustand: dict = _state()
        zustand["haltung"] = None
        with self.assertLogs(VERFASSER_LOGGER, level="ERROR"):
            ohne: str = verf_mod._build_system_prompt(zustand)
        self.assertNotIn("Zeichen Rede", ohne)
        self.assertIn("Der Umfang folgt der Landschaft", ohne)


class StoffBandTest(unittest.TestCase):
    """Die inhaltlichen Wörter — andere als die des Responders."""

    def test_die_woerter_unterscheiden_sich_vom_ton(self) -> None:
        """Dieselbe Zahl, zwei Aufgaben, zwei Formulierungen."""
        from ei.haltungssprache import band
        self.assertNotEqual(stoff_band("fragen", 0.10), band("fragen", 0.10))
        self.assertNotEqual(stoff_band("draengen", 0.95), band("draengen", 0.95))

    def test_nur_die_fachlichen_groessen_haben_stoffwoerter(self) -> None:
        """`naehe` und `waerme` sind kein Stoff, und der Aufruf sagt es."""
        for tonal in ("naehe", "waerme", "umfang"):
            with self.assertRaises(ValueError):
                stoff_band(tonal, 0.50)

    def test_eine_unvollstaendige_haltung_ist_ein_fehler(self) -> None:
        """Eine fehlende Größe ist ein Aufruffehler.

        Eine stumm ausgelassene Zeile wäre von einem Anschlag am unteren
        Ende nicht zu unterscheiden.
        """
        werte = {n: w for n, w in _haltung().werte.items() if n != "fragen"}
        with self.assertRaises(ValueError):
            stoffzeilen(Haltung(cluster="bier", werte=werte), 10, ())


if __name__ == "__main__":
    unittest.main()
