"""Tests: Der Turn-Abschluss haengt nicht an den pending_writes.

ZIEL: Ein Turn mit erzeugter Antwort bekommt seine `turn_roh`-Zeile, auch wenn
kein Knoten einen Schreibauftrag hinterlassen hat — und der Dispatcher
hinterlaesst eine Spur, auch wenn er nichts schreibt.

**Der Befund, gezaehlt am 09.09.2026:** 15 von 227 Turns mit erzeugter Antwort
tragen keine `turn_roh`-Zeile (6,6 %); 14 davon nach demselben Ausfall — der
Salienz-Knoten scheiterte an seinem eigenen Modell-JSON. `turn_roh` ist die
Zeile, aus der jede Laengen-, Kosten- und Verhaltensmessung dieses Projekts
ihre Ergebnisgroesse zieht. Kennung `TURN-ROH-FEHLT-BEI-ERZEUGTER-ANTWORT`.

> **Ein so ausgefallener Turn sieht nicht aus wie ein Fehler, sondern wie ein
> Turn, den es nie gab.** Er hinterlaesst keine Luecke, die jemand zaehlen
> koennte. Faellt er in einer Messreihe in einem Arm haeufiger an als im
> anderen, verzerrt er das Ergebnis, ohne dass etwas fehlt.

**Zwei Zusicherungen, und die zweite ist die Voraussetzung der ersten:**

  1. **Der frueh ausgestiegene Dispatcher schliesst den Turn trotzdem ab.**
     `if not writes: return state` uebersprang `_session_turn_schreiben` und
     `_turn_roh_schreiben` — zwei Schritte, die mit den Writes nichts zu tun
     haben.
  2. **Der Dispatcher hinterlaesst eine Spur, auch wenn er nichts schreibt.**
     Er schrieb bis zum 09.09.2026 ausschliesslich bei Erfolg. Damit war
     *nicht gelaufen* von *erfolglos gelaufen* nicht zu unterscheiden — an
     genau dem Knoten, dessen Ausbleiben protokolliert werden soll. **Die
     Diagnose des Eintrags war daran nicht pruefbar**, und eine Zaehlung
     ueber fehlende Dispatcher-Zeilen zaehlt dieselbe Aussage zweimal.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.nodes import dispatcher as dispatcher_mod

USER:  str = "meister"
FIGUR: str = "nova"


class _Emotion:
    """Ein Personality-Doppel mit den Feldern, die der Nachlauf liest.

    `mode` und `arousal` stehen hier, weil `_persist_vorturn` sie im Pfad
    **mit** Writes liest — ein Doppel, das nur `to_dict()` kann, laesst den
    Zeugen an einer Stelle scheitern, die er gar nicht prueft.
    """

    mode:    str   = "sachlich"
    arousal: float = 0.5

    def to_dict(self) -> dict:
        return {"emotion": "neugierig", "arousal": 0.5}


class _Personality:
    def __init__(self) -> None:
        self.emotion = _Emotion()


def _zustand(*, writes: list | None = None, response: str = "Eine Antwort.") -> dict:
    """Der Zustand am Dispatcher-Eingang, so wie ihn ein echter Turn liefert."""
    return {
        "turn_id":        "probe-turn",
        "user_id":        USER,
        "character_id":   FIGUR,
        "pending_writes": writes if writes is not None else [],
        "response":       response,
        "external":       _Personality(),
        "internal":       _Personality(),
        "user_prompt":    "Wie entsteht die Rotverschiebung?",
    }


def _lauf(zustand: dict) -> tuple[list, list]:
    """Faehrt den Dispatcher und faengt ab, was er ins Protokoll geschrieben haette.

    Returns:
        (Berechnungs-Zeilen, `turn_roh`-Aufrufe) — beide als Liste der
        `inhalt`-Dicts.
    """
    berechnungen: list = []
    turn_roh:     list = []

    with patch.object(dispatcher_mod, "log_berechnung",
                      side_effect=lambda **kw: berechnungen.append(kw["inhalt"])), \
         patch.object(dispatcher_mod, "log_turn_roh",
                      side_effect=lambda **kw: turn_roh.append(kw)), \
         patch.object(dispatcher_mod, "_persist_short_term_drive"), \
         patch.object(dispatcher_mod, "_session_turn_schreiben"), \
         patch.object(dispatcher_mod, "reiz_text", return_value="Reiz"), \
         patch.object(dispatcher_mod, "reiz_herkunft", return_value="nutzer"):
        dispatcher_mod.dispatch(zustand, MagicMock(), "postgresql://attrappe")

    return berechnungen, turn_roh


class TurnAbschlussOhneWritesTest(unittest.TestCase):
    """Der Auslösefall: ein Turn mit Antwort und ohne Schreibauftrag."""

    def test_ohne_writes_entsteht_trotzdem_eine_turn_roh_zeile(self) -> None:
        """Die Zusicherung, um die es geht.

        Vor dem 09.09.2026 kehrte der Dispatcher hier zurueck, ohne den Turn
        abzuschliessen — und die Antwort verschwand aus dem dauerhaften
        Protokoll, obwohl sie erzeugt worden war.
        """
        _, turn_roh = _lauf(_zustand(writes=[]))
        self.assertEqual(len(turn_roh), 1)

    def test_die_zeile_traegt_die_antwort(self) -> None:
        """Nicht nur eine Zeile, sondern die Ergebnisgroesse darin."""
        _, turn_roh = _lauf(_zustand(writes=[], response="1722 Zeichen lang."))
        self.assertEqual(turn_roh[0]["inhalt"]["response"], "1722 Zeichen lang.")

    def test_mit_writes_entsteht_sie_weiterhin(self) -> None:
        """Die Gegenrichtung — der Normalfall darf nicht verlorengehen."""
        with patch.object(dispatcher_mod, "get_registry", return_value={}), \
             patch.object(dispatcher_mod, "_delegation_trigger_pruefen", return_value=""), \
             patch.object(dispatcher_mod, "_persist_vorturn"), \
             patch.object(dispatcher_mod, "_verwendung_verstaerken"):
            _, turn_roh = _lauf(_zustand(writes=[{"ziel": "kzg", "aktion": "create"}]))
        self.assertEqual(len(turn_roh), 1)


class SpurAmEingangTest(unittest.TestCase):
    """Der Dispatcher belegt seinen Lauf, nicht nur seinen Erfolg."""

    def test_der_eingang_schreibt_auch_ohne_writes(self) -> None:
        berechnungen, _ = _lauf(_zustand(writes=[]))
        eingang = [b for b in berechnungen if b.get("schritt") == "eingang"]
        self.assertEqual(len(eingang), 1)

    def test_die_spur_traegt_die_entscheidenden_groessen(self) -> None:
        """Ein Eintrag *„Dispatcher lief"* beantwortet die naechste Frage nicht.

        Die vier Felder sind genau die, an denen die beiden Schreibpfade
        entscheiden — ohne sie waere im Nachhinein nicht trennbar, ob die
        Antwort fehlte, das Paar oder die Personality.
        """
        berechnungen, _ = _lauf(_zustand(writes=[]))
        eingang = next(b for b in berechnungen if b.get("schritt") == "eingang")
        self.assertEqual(eingang["writes"], 0)
        self.assertTrue(eingang["hat_response"])
        self.assertTrue(eingang["hat_external"])
        self.assertTrue(eingang["hat_internal"])
        self.assertTrue(eingang["paar_vollstaendig"])


class UebersprungenMitGrundTest(unittest.TestCase):
    """Jeder Ausstieg hinterlaesst seinen Grund — im Protokoll, nicht im Log.

    Eine `logger.warning` haengt am Neustart des Containers. Die Frage *„warum
    fehlt dieser Turn"* stellt sich Tage spaeter, und dann ist sie damit nicht
    mehr beantwortbar.
    """

    def test_leere_antwort_im_charactergraph_ist_ein_ausfall(self) -> None:
        """Dort ist die Antwort erzeugt worden — ihr Fehlen ist der Befund."""
        zustand = _zustand(writes=[], response="")
        zustand["graph_rolle"] = "character"
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(len(gruende), 1)
        self.assertEqual(gruende[0]["grund"], "response_leer")

    def test_leere_antwort_im_humangraph_ist_erwartet(self) -> None:
        """Der HumanGraph laeuft, bevor Nova formuliert hat.

        `[gemessen 09.09.2026, 20:38:36 UTC]` Der erste Betriebsturn nach dem
        Bau meldete `response_leer` — aus dem HumanGraph, wo genau das der
        dokumentierte Normalfall ist. Eine Meldung, die bei jedem Turn
        erscheint, besetzt den Platz, an dem sonst jemand nachsaehe.
        """
        zustand = _zustand(writes=[], response="")
        zustand["graph_rolle"] = "human"
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(gruende[0]["grund"], "kein_antwortpfad")

    def test_die_beiden_faelle_sind_unterscheidbar(self) -> None:
        """Wer zaehlen will, wie oft eine erzeugte Antwort verlorenging,
        braucht beide getrennt — und wer die Zeile im erwarteten Fall
        weglaesst, macht ihn vom stillen Ausfall wieder ununterscheidbar.
        """
        gruende: list = []
        for rolle in ("human", "character"):
            zustand = _zustand(writes=[], response="")
            zustand["graph_rolle"] = rolle
            berechnungen, _ = _lauf(zustand)
            gruende += [b["grund"] for b in berechnungen
                        if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(len(set(gruende)), 2, f"beide Faelle melden {gruende}")

    def test_fehlende_personality_nennt_ihren_grund(self) -> None:
        zustand = _zustand(writes=[])
        zustand["internal"] = None
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(gruende[0]["grund"], "personality_fehlt")
        self.assertFalse(gruende[0]["hat_internal"])
        self.assertTrue(gruende[0]["hat_external"])

    def test_unvollstaendiges_paar_nennt_seinen_grund(self) -> None:
        zustand = _zustand(writes=[])
        zustand["character_id"] = ""
        berechnungen, turn_roh = _lauf(zustand)
        self.assertEqual(turn_roh, [])
        gruende = [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"]
        self.assertEqual(gruende[0]["grund"], "paar_unvollstaendig")

    def test_der_erfolgsfall_schreibt_keinen_grund(self) -> None:
        """Sonst waere die Meldung der Normalfall und niemand laese sie."""
        berechnungen, _ = _lauf(_zustand(writes=[]))
        self.assertEqual(
            [b for b in berechnungen if b.get("schritt") == "turn_roh_uebersprungen"], [],
        )


if __name__ == "__main__":
    unittest.main()
