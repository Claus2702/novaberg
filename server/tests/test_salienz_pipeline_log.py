"""Tests fuer die Forensik des Salienz-Nodes (SALIENZ-OHNE-PIPELINE-LOG).

Ziel: Nach einem Turn ist aus der Datenbank beantwortbar, welcher Text bewertet
wurde, in wie viele Segmente geschnitten wurde und welchen Salienzwert jedes
Segment bekam — ohne das fluechtige Container-Log.

Hintergrund: `graph/nodes/salience.py` schrieb in keinem Graphen eine Zeile ins
pipeline_log. Der Wert, der ueber Erinnern entscheidet, war forensisch
unsichtbar. Genau deshalb blieb `bewertungs_laenge=0` im AgentGraph unbemerkt,
seit es den Graphen gibt: Der Fehler war da, aber nichts hielt ihn fest.

Abgefangen wird am Puffer. `_log_eintrag` holt ihn ueber `get_buffer()`; ohne
laufenden Event-Loop landet der Eintrag in `put_threadsafe`. Ein MagicMock an
dieser Stelle sammelt die echten Eintrags-Objekte ein — geprueft wird also der
Weg bis zum Puffer, nicht eine Attrappe davor.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.nodes.salience import analyze

REIZ:     str = "Rotverschiebung entfernter Galaxien belegt die Ausdehnung des Raums."
REAKTION: str = "Und die Ausdehnung selbst beschleunigt sich, was niemand erwartet hatte."


def _state(graph_rolle: str, user_prompt: str = REIZ, response: str = REAKTION) -> dict:
    return {
        "graph_rolle":      graph_rolle,
        "ei_calc_rolle":    "character" if graph_rolle in ("character", "agent") else "user",
        "user_prompt":      user_prompt,
        "response":         response,
        "pending_writes":   [],
        "token_total":      0,
        "turn_id":          "t-forensik",
        "character_id":     "nova",
        "gravitationsterm": 0.0,
    }


def _lauf(graph_rolle: str, segmente: int = 1, **kw) -> tuple[list, dict]:
    """Fuehrt analyze() aus und liefert (pipeline_log-Eintraege, Ergebnis-State).

    Vorbedingung: graph_rolle ist eine der drei bekannten Rollen.
    Nachbedingung: die Liste enthaelt die Eintrags-Objekte in Schreibreihenfolge.
    Fehlerfaelle: keine — ein Lauf ohne Eintraege liefert eine leere Liste,
        was die Tests als Fehlschlag werten.
    """

    # ── Eingabe-Validierung ─────────────────────
    if segmente < 1:
        raise ValueError("_lauf: segmente muss mindestens 1 sein")

    # ── Verarbeitung ────────────────────────────
    antwort = MagicMock()
    antwort.parsed      = {"salienz": 0.72, "themen": ["Kosmologie"],
                           "dimension": "wissen", "gedaechtnistyp": "semantisch",
                           "emotion": "neugier", "arousal": 0.4, "modus": "sachlich"}
    antwort.token_total = 11
    antwort.text        = "{}"

    puffer = MagicMock()
    zustand: dict = _state(graph_rolle, **kw)

    with patch("memory.pipeline_log.get_buffer", return_value=puffer):
        with patch(
            "graph.nodes.salience._prompt_segmentieren",
            side_effect=lambda t: [t] * segmente,
        ):
            with patch.object(
                __import__("services.model_services", fromlist=["model_service"]).model_service.chat,
                "submit_sync", return_value=antwort,
            ):
                ergebnis = analyze(zustand, MagicMock(), "meister")

    # ── Ausgabe ─────────────────────────────────
    return [ruf.args[0] for ruf in puffer.put_threadsafe.call_args_list], ergebnis


def _mit_schritt(eintraege: list, schritt: str) -> list:
    """Filtert berechnung-Eintraege nach ihrem schritt-Feld."""
    return [e for e in eintraege if e.art == "berechnung" and e.inhalt.get("schritt") == schritt]


class SalienzSpanTest(unittest.TestCase):
    """Der Lauf haengt in einer Klammer und ist korrelierbar."""

    def test_lauf_schreibt_span_switch_bewertung_und_ende(self):
        eintraege, _ = _lauf("human")
        arten: list = [e.art for e in eintraege]

        self.assertIn("span_start", arten)
        self.assertIn("switch", arten)
        self.assertIn("berechnung", arten)
        self.assertIn("span_end", arten)
        self.assertEqual(arten[0],  "span_start")
        self.assertEqual(arten[-1], "span_end")

    def test_alle_eintraege_tragen_dieselbe_span_id(self):
        """Ohne gemeinsame span_id ist ein Lauf nicht von einem zweiten zu trennen."""
        eintraege, _ = _lauf("human")
        span_ids: set = {e.span_id for e in eintraege}
        self.assertEqual(len(span_ids), 1)
        self.assertIsNotNone(eintraege[0].span_id)

    def test_node_und_paar_stehen_an_jedem_eintrag(self):
        eintraege, _ = _lauf("character")
        for eintrag in eintraege:
            self.assertEqual(eintrag.node,         "salienz")
            self.assertEqual(eintrag.turn_id,      "t-forensik")
            self.assertEqual(eintrag.user_id,      "meister")
            self.assertEqual(eintrag.character_id, "nova")


class SalienzSwitchTest(unittest.TestCase):
    """Die Zeile, die bewertungs_laenge=0 sofort gezeigt haette."""

    def test_switch_nennt_rolle_und_beide_textlaengen(self):
        eintraege, _ = _lauf("human")
        switch = [e for e in eintraege if e.art == "switch"]
        self.assertEqual(len(switch), 1)

        inhalt: dict = switch[0].inhalt
        self.assertEqual(inhalt["graph_rolle"],       "human")
        self.assertEqual(inhalt["bewertungs_laenge"], len(REIZ))
        self.assertEqual(inhalt["lagebild_laenge"],   len(REAKTION))

    def test_agentgraph_bewertet_den_reiz_und_traegt_kein_lagebild(self):
        """Der Chat-110-Befund, jetzt dauerhaft nachweisbar."""
        eintraege, _ = _lauf("agent", response="")
        inhalt: dict = [e for e in eintraege if e.art == "switch"][0].inhalt

        self.assertEqual(inhalt["bewertungs_laenge"], len(REIZ))
        self.assertEqual(inhalt["lagebild_laenge"],   0)

    def test_agentgraph_ist_im_log_eine_eigene_quelle(self):
        eintraege, _ = _lauf("agent", response="")
        self.assertEqual({e.quelle for e in eintraege}, {"agent"})

    def test_humangraph_und_charactergraph_behalten_ihre_bestandswerte(self):
        human,     _ = _lauf("human")
        character, _ = _lauf("character")
        self.assertEqual({e.quelle for e in human},     {"user"})
        self.assertEqual({e.quelle for e in character}, {"character"})


class SalienzBewertungTest(unittest.TestCase):
    """Der Wert, der ueber Erinnern entscheidet."""

    def test_bewertung_traegt_salienzwert_und_themen(self):
        eintraege, _ = _lauf("human")
        bewertung = _mit_schritt(eintraege, "bewertung")
        self.assertEqual(len(bewertung), 1)

        inhalt: dict = bewertung[0].inhalt
        self.assertEqual(inhalt["salienz"],   0.72)
        self.assertEqual(inhalt["themen"],    ["Kosmologie"])
        self.assertEqual(inhalt["dimension"], "wissen")

    def test_segmentschnitt_ist_nachvollziehbar(self):
        """Wie viele KZG-Eintraege ein Turn erzeugt, haengt am Schnitt."""
        eintraege, _ = _lauf("human", segmente=3)
        segmentierung = _mit_schritt(eintraege, "segmentierung")
        self.assertEqual(len(segmentierung), 1)
        self.assertEqual(segmentierung[0].inhalt["segmente"], 3)

    def test_jedes_segment_bekommt_eine_eigene_bewertung(self):
        eintraege, _ = _lauf("human", segmente=3)
        bewertung = _mit_schritt(eintraege, "bewertung")
        self.assertEqual(len(bewertung), 3)
        self.assertEqual([e.inhalt["segment_index"] for e in bewertung], [0, 1, 2])

    def test_span_ende_meldet_segmente_und_pending_writes(self):
        eintraege, ergebnis = _lauf("human", segmente=2)
        ende = [e for e in eintraege if e.art == "span_end"][0]

        self.assertEqual(ende.inhalt["segmente"],       2)
        self.assertEqual(ende.inhalt["pending_writes"], 2)
        self.assertEqual(ende.inhalt["pending_writes"], len(ergebnis["pending_writes"]))
        self.assertFalse(ende.inhalt["abbruch"])


class SalienzGravitationTest(unittest.TestCase):
    """Kam die hohe Salienz vom Modell oder vom Ziel-Antrieb?"""

    def test_boost_bekommt_eine_eigene_zeile_mit_basis_und_ergebnis(self):
        eintraege, _ = _lauf("human", segmente=1)
        self.assertEqual(_mit_schritt(eintraege, "gravitationsboost"), [])

        zustand: dict = _state("human")
        zustand["gravitationsterm"] = 0.2

        antwort = MagicMock()
        antwort.parsed      = {"salienz": 0.5, "themen": ["T"], "dimension": "wissen"}
        antwort.token_total = 0
        antwort.text        = "{}"
        puffer = MagicMock()

        with patch("memory.pipeline_log.get_buffer", return_value=puffer):
            with patch("graph.nodes.salience._prompt_segmentieren", side_effect=lambda t: [t]):
                with patch.object(
                    __import__("services.model_services", fromlist=["model_service"]).model_service.chat,
                    "submit_sync", return_value=antwort,
                ):
                    analyze(zustand, MagicMock(), "meister")

        eintraege_boost: list = [ruf.args[0] for ruf in puffer.put_threadsafe.call_args_list]
        boost = _mit_schritt(eintraege_boost, "gravitationsboost")
        self.assertEqual(len(boost), 1)
        self.assertEqual(boost[0].inhalt["salienz_basis"],    0.5)
        self.assertEqual(boost[0].inhalt["gravitationsterm"], 0.2)
        self.assertEqual(boost[0].inhalt["salienz_neu"],      0.7)


class SalienzFehlerpfadTest(unittest.TestCase):
    """Ein Turn, der nichts ablegt, muss sagen warum."""

    def test_leeres_objekt_schreibt_fehler_und_schliesst_den_span(self):
        eintraege, ergebnis = _lauf("agent", user_prompt="", response="")

        fehler = [e for e in eintraege if e.art == "fehler"]
        self.assertEqual(len(fehler), 1)
        self.assertEqual(fehler[0].inhalt["grund"], "bewertungsobjekt_leer")

        self.assertEqual(ergebnis["pending_writes"], [])
        self.assertEqual(_mit_schritt(eintraege, "bewertung"), [])

        ende = [e for e in eintraege if e.art == "span_end"]
        self.assertEqual(len(ende), 1)
        self.assertTrue(ende[0].inhalt["abbruch"])

    def test_positiver_zwilling_gefuellter_text_legt_genau_eines_an(self):
        """Zwingend: die Zusicherung oben erwartet null und kann nie rot werden.

        Ohne diesen Zwilling bestuende der Fehlerpfad-Test die Gegenprobe auch
        dann, wenn der Node ueberhaupt nichts mehr schreibt.
        """
        eintraege, ergebnis = _lauf("agent", response="")

        self.assertEqual(len(ergebnis["pending_writes"]), 1)
        self.assertEqual(len(_mit_schritt(eintraege, "bewertung")), 1)
        self.assertEqual([e for e in eintraege if e.art == "fehler"], [])

    def test_verworfenes_segment_wird_als_fehler_vermerkt(self):
        """Ein uebersprungenes Segment ist ein verlorener Gedaechtnis-Eintrag."""
        kaputt = MagicMock()
        kaputt.token_total = 0
        kaputt.text        = "kein json"
        type(kaputt).parsed = property(
            lambda self: (_ for _ in ()).throw(KeyError("parsed"))
        )

        puffer = MagicMock()
        with patch("memory.pipeline_log.get_buffer", return_value=puffer):
            with patch("graph.nodes.salience._prompt_segmentieren", side_effect=lambda t: [t, t]):
                with patch.object(
                    __import__("services.model_services", fromlist=["model_service"]).model_service.chat,
                    "submit_sync", return_value=kaputt,
                ):
                    with self.assertLogs("ki_server.salience", level="ERROR"):
                        ergebnis = analyze(_state("human"), MagicMock(), "meister")

        eintraege: list = [ruf.args[0] for ruf in puffer.put_threadsafe.call_args_list]
        fehler = [e for e in eintraege if e.art == "fehler"]

        self.assertEqual(len(fehler), 2)
        self.assertEqual({e.inhalt["grund"] for e in fehler}, {"json_parsing"})
        self.assertEqual(ergebnis["pending_writes"], [])

        # Der Span schliesst trotzdem — sonst bliebe der Lauf offen.
        ende = [e for e in eintraege if e.art == "span_end"][0]
        self.assertEqual(ende.inhalt["segmente"],       2)
        self.assertEqual(ende.inhalt["pending_writes"], 0)


if __name__ == "__main__":
    unittest.main()
