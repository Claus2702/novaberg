"""Tests: die Haltungsrechnung hat einen Aufrufer, und ihr Ergebnis kommt an.

Gegenstand ist nicht die Rechnung — die prueft `test_haltung.py` gegen
Literale. Hier steht die Frage davor: **Laeuft sie ueberhaupt, und ueberlebt
ihr Ergebnis die Knotengrenze?** Beides war bis zum 31.07.2026 nicht der Fall;
`haltung_berechnen` hatte keinen einzigen Aufrufer ausserhalb der Tests.

Zeugen dieser Datei:
  * Das Rad stammt aus `novaberg-haltungsraum_k.md` §2.2a — das am 31.07.2026
    real gemessene Zuwendungsrad, nicht ein fuer den Test erfundenes.
  * Die Position im Graphen stammt aus demselben Konzept §2 ("Wer rechnet"):
    nach dem GV-Node, **vor** der Verzweigung zum Verfasser.
  * Die Gegenprobe stammt aus §5 des Konzepts: Steht die Zuwendung auf der
    Nabe, muessen sich die fuenf Werte aendern — sonst entscheidet der
    Charakter nichts und die Rechnung ist eine Cluster-Tabelle.
  * Die Zusicherung zum Kanal stammt aus
    `novaberg-lesson_l_stategraph-channel-zwang.md`.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from contextlib import AbstractContextManager
from unittest.mock import MagicMock, patch

from graph.nodes.haltung import haltung_bestimmen
from graph.state import ConversationState
from langgraph.graph import END, StateGraph

HALTUNG_LOGGER: str = "ki_server.graph.haltung"

# Novas Zuwendung zum Nutzer, gemessen am 31.07.2026 und im Konzept §2.2a
# abgedruckt. Die uebrigen sieben Speichen standen auf null und fehlen hier
# genau deshalb: Der Lader liefert nur belegte Speichen, und die Rechnung muss
# damit zurechtkommen.
RAD_GEMESSEN: dict[str, float] = {
    "treue":          0.5,
    "aufmerksamkeit": 0.5,
    "wissbegier":     1.0,
    "wohlwollen":     1.0,
    "distanz":        0.5,
}

# Die fuenf Groessennamen als Literal — aus dem Konzept §2, nicht aus
# `ei.haltung.GROESSEN`. Ein Test, der seine Erwartung aus dem Pruefobjekt
# bezieht, prueft nichts.
FUENF_GROESSEN: set[str] = {"umfang", "fragen", "naehe", "waerme", "draengen"}


def _state(**felder: object) -> dict:
    """Baut einen Zustand, der fuer den Haltungs-Node ausreicht.

    Vorbedingung: keine.
    Nachbedingung: Alle Felder, die der Node liest, sind belegt.
    Fehlerfaelle: keine.

    Returns:
        Der Zustand.
    """
    basis: dict = {
        "user_prompt":      "Wie entsteht ein Gammablitz?",
        "user_id":          "meister",
        "character_id":     "nova",
        "turn_id":          "t",
        "gv_detail":        {"cluster": "glut"},
        "task_context_cut": False,
        "node_annotations": [],
    }
    basis.update(felder)
    return basis


def _mit_rad(
    rad: dict[str, float], quelle: str = "destilliert",
) -> AbstractContextManager[MagicMock]:
    """Ersetzt den Radzugriff durch einen Zeugen.

    Der Node soll ohne Datenbank pruefbar sein; der Lader hat seine eigenen
    Tests (`test_charakter_rad_laden.py`).

    Args:
        rad:    Speichenname -> Auspraegung.
        quelle: 'destilliert' oder 'default', wie beim echten Lader.

    Returns:
        Der Patch-Kontext.
    """
    return patch(
        "graph.nodes.haltung.nutzer_gewichtung_rad_laden",
        return_value=(rad, quelle),
    )


class DerKanalIstDeklariertTest(unittest.TestCase):
    """Ein Schreibvorgang in einen unbekannten Kanal wirkt nicht."""

    def test_haltung_steht_im_zustandsschema(self) -> None:
        """Ohne diese Zeile laeuft der Node und der Wert ist danach weg."""
        self.assertIn("haltung", ConversationState.__annotations__)

    def test_haltung_wird_nicht_vorbelegt(self) -> None:
        """Ein leerer Startwert loeschte den Unterschied zu 'nicht gelaufen'.

        Konzept §2.0a: Ein Turn ohne Rechnung traegt keine Haltung statt einer
        leeren. Wer den Schluessel in `create_state` vorbelegt, macht beides
        ununterscheidbar, bevor irgendeine Pruefung stattfinden kann.
        """
        from graph.base import GraphBase

        quelle: str = GraphBase.create_state.__code__.co_consts.__str__()
        self.assertNotIn("haltung", quelle)


class DerWertUeberlebtDieKnotengrenzeTest(unittest.TestCase):
    """Der teure Fall: innerhalb des Nodes lesbar, danach weg.

    Geprueft wird gegen das echte Framework, nicht gegen eine Attrappe — die
    Falle sitzt in seiner Rekonstruktion des Zustands pro Node.
    """

    def test_ein_nachfolgender_node_sieht_die_haltung(self) -> None:
        """Der zweite Node liest, was der erste geschrieben hat."""
        def schreiber(state: ConversationState) -> ConversationState:
            return haltung_bestimmen(state, "postgresql://attrappe")

        def leser(state: ConversationState) -> dict:
            haltung = state.get("haltung")
            return {"node_annotations": [
                haltung.cluster if haltung is not None else "FEHLT",
            ]}

        graph = StateGraph(ConversationState)
        graph.add_node("schreiber", schreiber)
        graph.add_node("leser",     leser)
        graph.set_entry_point("schreiber")
        graph.add_edge("schreiber", "leser")
        graph.add_edge("leser",     END)
        gebaut = graph.compile()

        with _mit_rad(RAD_GEMESSEN):
            ergebnis = gebaut.invoke(_state())

        self.assertEqual(
            ["glut"], ergebnis["node_annotations"],
            "die Haltung hat die Knotengrenze nicht ueberlebt",
        )


class DieVerdrahtungLaeuftUeberDenHaltungsraumTest(unittest.TestCase):
    """Der Node haengt zwischen GV-Node und Verzweigung, in jedem Turn.

    Der Graph wird ohne `__init__` gebaut: Die Verdrahtung braucht weder Redis
    noch Postgres, und ein Test, der beides braucht, liefe gegen den
    Produktivbestand.
    """

    def _kanten(self) -> set[tuple[str, str]]:
        from graph.character_graph import CharacterGraph

        gebaut = CharacterGraph.build(object.__new__(CharacterGraph))
        return {(e.source, e.target) for e in gebaut.get_graph().edges}

    def test_der_gv_node_fuehrt_in_den_haltungsraum(self) -> None:
        """Erst die Landschaft, dann die Haltung — anders gibt es keinen Cluster."""
        self.assertIn(("gv_node", "haltungsraum"), self._kanten())

    def test_beide_zweige_gehen_vom_haltungsraum_ab(self) -> None:
        """Auch der Kontext-Schnitt laeuft ueber die Rechnung."""
        kanten: set[tuple[str, str]] = self._kanten()
        self.assertIn(("haltungsraum", "verfasser"), kanten)
        self.assertIn(("haltungsraum", "responder"), kanten)

    def test_kein_zweig_umgeht_den_haltungsraum(self) -> None:
        """Die Gegenprobe zur Position: kein Weg vom GV-Node am Raum vorbei."""
        kanten: set[tuple[str, str]] = self._kanten()
        self.assertNotIn(("gv_node", "verfasser"), kanten)
        self.assertNotIn(("gv_node", "responder"), kanten)


class DerKnotenRechnetTest(unittest.TestCase):
    """Ein gewoehnlicher Turn hinterlaesst eine vollstaendige Haltung."""

    def test_die_haltung_traegt_die_landschaft_des_turns(self) -> None:
        """Der Cluster kommt aus `gv_detail`, nicht aus einem Vorgabewert."""
        with _mit_rad(RAD_GEMESSEN):
            ergebnis = haltung_bestimmen(
                _state(gv_detail={"cluster": "werkstatt"}), "postgresql://attrappe",
            )

        self.assertEqual("werkstatt", ergebnis["haltung"].cluster)

    def test_alle_fuenf_groessen_stehen_darin(self) -> None:
        """Vier von fuenf waeren ein halber Raum — und fielen erst beim Leser auf."""
        with _mit_rad(RAD_GEMESSEN):
            ergebnis = haltung_bestimmen(_state(), "postgresql://attrappe")

        self.assertEqual(FUENF_GROESSEN, set(ergebnis["haltung"].werte))

    def test_die_meldung_nennt_die_herkunft_des_rades(self) -> None:
        """Ein Default-Rad rechnet sich so glatt wie ein destilliertes.

        Ohne die Herkunft in der Zeile ist an keiner Messung erkennbar, ob der
        Charakter gemessen oder nur angenommen war.
        """
        with _mit_rad(RAD_GEMESSEN, quelle="default"):
            with self.assertLogs(HALTUNG_LOGGER, level="INFO") as protokoll:
                haltung_bestimmen(_state(), "postgresql://attrappe")

        self.assertIn("default", "\n".join(protokoll.output))


class DieZuwendungEntscheidetMitTest(unittest.TestCase):
    """Gegenprobe aus Konzept §5: Die Nabe muss andere Werte ergeben.

    Bleiben die fuenf Groessen gleich, wenn das Rad leer ist, dann ist die
    Rechnung in Wahrheit eine Cluster-Tabelle und der Charakter entscheidet
    nichts.
    """

    def _werte(self, rad: dict[str, float]) -> dict[str, float]:
        with _mit_rad(rad):
            ergebnis = haltung_bestimmen(_state(), "postgresql://attrappe")
        return {
            name: wert.ergebnis
            for name, wert in ergebnis["haltung"].werte.items()
        }

    def test_das_gemessene_rad_verschiebt_die_werte(self) -> None:
        """Mit Zuwendung steht Nova anders da als auf der Nabe."""
        self.assertNotEqual(self._werte({}), self._werte(RAD_GEMESSEN))

    def test_auf_der_nabe_bleiben_die_grundwerte_stehen(self) -> None:
        """Ohne Zuwendung sagt allein die Landschaft, was angemessen ist."""
        werte: dict[str, float] = self._werte({})
        # `glut` aus dem Konzept §2.0, als Literal und nicht aus dem Modul.
        self.assertEqual(0.70, round(werte["umfang"], 2))
        self.assertEqual(0.20, round(werte["draengen"], 2))


class DerAusfallBleibtLeerTest(unittest.TestCase):
    """Ein Turn ohne Rechnung traegt keine Haltung — und sagt es laut."""

    def test_ohne_landschaft_keine_haltung(self) -> None:
        """Ein leerer Cluster ist ein Defekt des GV-Nodes, kein stiller Fall."""
        with _mit_rad(RAD_GEMESSEN):
            with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
                ergebnis = haltung_bestimmen(
                    _state(gv_detail={}), "postgresql://attrappe",
                )

        self.assertNotIn("haltung", ergebnis)

    def test_ohne_nutzer_keine_haltung(self) -> None:
        """Das Rad haengt an einem Paar; ohne Nutzer ist es nicht ladbar."""
        with _mit_rad(RAD_GEMESSEN):
            with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
                ergebnis = haltung_bestimmen(
                    _state(user_id=""), "postgresql://attrappe",
                )

        self.assertNotIn("haltung", ergebnis)

    def test_ein_nicht_ladbares_rad_erzeugt_keine_grundwert_haltung(self) -> None:
        """Der teure Ausweg waere, mit den Grundwerten weiterzurechnen.

        Das saehe wie eine Haltung aus, waere aber eine Cluster-Tabelle — und
        niemand koennte im Nachhinein sehen, dass der Charakter gefehlt hat.
        """
        with patch(
            "graph.nodes.haltung.nutzer_gewichtung_rad_laden",
            return_value=(None, "fehlt"),
        ):
            with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
                ergebnis = haltung_bestimmen(_state(), "postgresql://attrappe")

        self.assertNotIn("haltung", ergebnis)

    def test_eine_unbekannte_landschaft_wird_abgelehnt(self) -> None:
        """Die Rechnung lehnt ab, der Node schreibt nichts."""
        with _mit_rad(RAD_GEMESSEN):
            with self.assertLogs(HALTUNG_LOGGER, level="ERROR"):
                ergebnis = haltung_bestimmen(
                    _state(gv_detail={"cluster": "sonnenschein"}),
                    "postgresql://attrappe",
                )

        self.assertNotIn("haltung", ergebnis)


if __name__ == "__main__":
    unittest.main()
