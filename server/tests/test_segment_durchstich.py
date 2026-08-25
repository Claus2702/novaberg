"""Tests fuer den Segment-Durchstich Salienz -> Dispatch -> Verdichtung.

Ziel: Ein Turn mit drei Segmenten erzeugt drei Gedaechtnis-Eintraege mit drei
verschiedenen Inhalten — je einen zu seinem Segment.

Hintergrund (gemessen 27.07.2026 an Turn 975ec093...): Der Segmentierer schnitt
eine Antwort richtig in 137/487/222 Zeichen — Novas Reaktion auf den
Themenwechsel, den Sachkern, Novas Selbstbezug. Gespeichert wurden drei
Paraphrasen desselben Sachkerns; die anderen beiden Segmente landeten nie im
Gedaechtnis. Der `pending_write` trug das Segment nicht weiter, und die
Verdichtung las `user_prompt`/`response` aus dem State — also den ganzen Turn.
Drei Segmente ergaben drei LLM-Aufrufe mit bitgleicher Eingabe.

Geprueft werden alle drei Stationen: wer ablegt, wer weiterreicht, wer liest.
Ein Durchstich, dessen Mitte ungetestet bleibt, driftet genau dort auseinander.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.kzg.dispatch import dispatch_kzg
from agents.kzg.verdichtung import verdichten
from graph.nodes.salience import analyze
from services.model_services import model_service

VERDICHTUNG_LOGGER: str = "ki_server.agents.kzg.verdichtung"

SEG_0: str = "Ploetzlich also Astronomie? Ich mag diesen abrupten Wechsel."
SEG_1: str = "Die Rotverschiebung entfernter Galaxien belegt die Ausdehnung des Raums."
SEG_2: str = "In gewisser Weise ist das genau, was wir hier auch versuchen."
REIZ:  str = "Was weisst Du ueber die Ausdehnung des Universums?"


# ═══════════════════════════════════════════════════════════════════
# Station 1 — der Salienz-Node legt das Segment ab
# ═══════════════════════════════════════════════════════════════════

def _analyse(segmente: list[str]) -> list[dict]:
    """Fuehrt analyze() mit vorgegebenen Segmenten aus, liefert pending_writes."""
    antwort = MagicMock()
    antwort.parsed      = {"salienz": 0.5, "themen": ["Kosmologie"], "dimension": "wissen"}
    antwort.token_total = 0
    antwort.text        = "{}"

    zustand: dict = {
        "graph_rolle":      "character",
        "ei_calc_rolle":    "character",
        "user_prompt":      REIZ,
        "response":         " ".join(segmente),
        "pending_writes":   [],
        "token_total":      0,
        "turn_id":          "t-durchstich",
        "character_id":     "nova",
        "gravitationsterm": 0.0,
    }

    with patch("graph.nodes.salience._prompt_segmentieren", return_value=segmente):
        with patch.object(model_service.chat, "submit_sync", return_value=antwort):
            ergebnis = analyze(zustand, MagicMock(), "meister")

    return ergebnis["pending_writes"]


class SalienzLegtSegmentAbTest(unittest.TestCase):

    def test_jeder_pending_write_traegt_sein_eigenes_segment(self) -> None:
        writes: list[dict] = _analyse([SEG_0, SEG_1, SEG_2])
        self.assertEqual(len(writes), 3)

        self.assertEqual([w["daten"]["segment"] for w in writes], [SEG_0, SEG_1, SEG_2])
        self.assertEqual([w["daten"]["segment_index"] for w in writes], [0, 1, 2])
        self.assertEqual({w["daten"]["segment_gesamt"] for w in writes}, {3})

    def test_ein_segment_traegt_den_volltext_ohne_sonderfall(self) -> None:
        """Ein ungeschnittener Turn ist ein Turn mit einem Segment."""
        writes: list[dict] = _analyse([SEG_1])
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0]["daten"]["segment"],        SEG_1)
        self.assertEqual(writes[0]["daten"]["segment_gesamt"], 1)

    def test_salienz_obj_bleibt_daneben_stehen(self) -> None:
        """Das Segment ergaenzt die Bewertung, es ersetzt sie nicht."""
        writes: list[dict] = _analyse([SEG_0, SEG_1])
        for write in writes:
            self.assertIn("salienz_obj", write["daten"])
            self.assertAlmostEqual(
                write["daten"]["salienz_obj"]["salienz"], 0.5/1.3, places=4,
            )

    def test_die_modellbewertung_bleibt_unangetastet(self) -> None:
        """Der Eingang der Formel ueberlebt ihr Ergebnis.

        `salienz` traegt nach dem Lauf das **Ergebnis**; die Bewertung des
        Modells steht daneben in `salienz_modell` und wird nicht
        ueberschrieben. Ohne diese Trennung liest der Knoten beim zweiten
        Segment seinen eigenen Ausgang.
        """
        writes: list[dict] = _analyse([SEG_0, SEG_1])
        for write in writes:
            self.assertEqual(write["daten"]["salienz_obj"]["salienz_modell"], 0.5)

    def test_die_rechnung_ist_idempotent_ueber_die_segmente(self) -> None:
        """Zwei Segmente ergeben denselben Wert wie eines — Regel 4.

        **Der Fall, den es bis zum 24.08.2026 gab:** Der Knoten schrieb sein
        Ergebnis nach `salienz` und las von dort die Eingabe des naechsten
        Segments. Gemessen ergab derselbe Turn mit zwei Segmenten
        `0.5 / 1.3² = 0.2958` statt `0.5 / 1.3 = 0.3846`.

        **Latent, solange die Formel mit `(1 + zuschlag)` multiplizierte** —
        bei ruhigem Turn ist der Faktor 1,0 und die Wiederholung unsichtbar.
        Bei Erregung war sie es nie: Ein Fuenf-Segment-Turn bekam `(1 + z)^5`.
        """
        eins  = _analyse([SEG_0])
        zwei  = _analyse([SEG_0, SEG_1])
        drei  = _analyse([SEG_0, SEG_1, SEG_2])
        werte = [w["daten"]["salienz_obj"]["salienz"] for w in (eins + zwei + drei)]
        self.assertEqual(
            len(set(round(x, 6) for x in werte)), 1,
            f"Die Segmentzahl veraendert das Ergebnis: {sorted(set(werte))}",
        )


# ═══════════════════════════════════════════════════════════════════
# Station 2 — der Dispatch reicht es in den parameter-Kanal
# ═══════════════════════════════════════════════════════════════════

def _dispatch_parameter(writes: list[dict]) -> list[dict]:
    """Faengt die AgentStates ab, die dispatch_kzg an den Subgraphen gibt."""
    agent = MagicMock()
    agent.invoke.return_value = {"parameter": {}, "schritte": []}

    zustand: dict = {
        "user_id":       "meister",
        "character_id":  "nova",
        "ei_calc_rolle": "character",
        "graph_rolle":   "character",
        "turn_id":       "t-durchstich",
        "user_prompt":   REIZ,
        "response":      " ".join([SEG_0, SEG_1, SEG_2]),
        "internal":      None,
        "external":      None,
    }

    with patch("agents.kzg.dispatch.AgentRegistry.finden", return_value=agent):
        with patch("agents.kzg.dispatch.cfg_redis_client", MagicMock()):
            dispatch_kzg(zustand, writes)

    return [ruf.args[0]["parameter"] for ruf in agent.invoke.call_args_list]


class DispatchReichtSegmentWeiterTest(unittest.TestCase):

    def test_segment_kommt_im_parameter_kanal_an(self) -> None:
        writes: list[dict] = _analyse([SEG_0, SEG_1, SEG_2])
        parameter: list[dict] = _dispatch_parameter(writes)

        self.assertEqual(len(parameter), 3)
        self.assertEqual([p["segment"] for p in parameter], [SEG_0, SEG_1, SEG_2])
        self.assertEqual([p["segment_index"] for p in parameter], [0, 1, 2])

    def test_fremder_write_ohne_segment_kommt_als_leerstring_an(self) -> None:
        """Der RechercheAgent baut eigene pending_writes — ohne Segment.

        Leerstring statt None, damit die Rueckfall-Bedingung in der Verdichtung
        eine einzige Form hat und nicht zwei.
        """
        fremd: list[dict] = [{
            "ziel":   "kzg",
            "aktion": "create",
            "daten":  {"salienz_obj": {"salienz": 0.9, "themen": ["X"]}},
        }]
        parameter: list[dict] = _dispatch_parameter(fremd)

        self.assertEqual(len(parameter), 1)
        self.assertEqual(parameter[0]["segment"], "")
        self.assertIsInstance(parameter[0]["segment"], str)


# ═══════════════════════════════════════════════════════════════════
# Station 3 — die Verdichtung zieht es dem Volltext vor
# ═══════════════════════════════════════════════════════════════════

def _verdichtungs_state(segment: str, index: int = 0, gesamt: int = 3) -> dict:
    volltext: str = " ".join([SEG_0, SEG_1, SEG_2])
    return {
        "aufgabe": "kzg_verarbeitung",
        "kontext": {
            "user_id": "meister", "character_id": "nova", "turn_id": "t-durchstich",
            "beobachter": "assistant", "graph_rolle": "character",
        },
        "parameter": {
            "reiz":           REIZ,
            "response":       volltext,
            "segment":        segment,
            "segment_index":  index,
            "segment_gesamt": gesamt,
        },
        "schritte": [], "ergebnis": None,
        "status": "laufend", "rueckfrage": None, "fehler": None,
    }


def _bewertungsobjekt(state: dict) -> str:
    """Ruft verdichten() auf und schneidet das [BEWERTUNGSOBJEKT] heraus."""
    antwort = SimpleNamespace(text="ein Kern")
    with patch.object(model_service.chat, "submit_sync", return_value=antwort) as ruf:
        verdichten(state)
    nachricht: str = ruf.call_args.args[0].messages[0]["content"]
    return nachricht.split("[BEWERTUNGSOBJEKT]", 1)[1]


class VerdichtungBevorzugtSegmentTest(unittest.TestCase):

    def test_segment_steht_im_bewertungsobjekt_der_volltext_nicht(self) -> None:
        objekt: str = _bewertungsobjekt(_verdichtungs_state(SEG_1, index=1))
        self.assertIn(SEG_1, objekt)
        self.assertNotIn(SEG_0, objekt)
        self.assertNotIn(SEG_2, objekt)

    def test_drei_segmente_ergeben_drei_verschiedene_bewertungsobjekte(self) -> None:
        """Das ZIEL: drei Eintraege mit drei Inhalten, nicht dreimal einer."""
        objekte: list[str] = [
            _bewertungsobjekt(_verdichtungs_state(seg, index=i))
            for i, seg in enumerate([SEG_0, SEG_1, SEG_2])
        ]
        self.assertEqual(len(set(objekte)), 3)
        for seg, objekt in zip([SEG_0, SEG_1, SEG_2], objekte, strict=True):
            self.assertIn(seg, objekt)

    def test_lagebild_bleibt_die_andere_turn_haelfte(self) -> None:
        """Kein Volltext im Lagebild — sonst waere die Ursache reproduziert."""
        antwort = SimpleNamespace(text="ein Kern")
        with patch.object(model_service.chat, "submit_sync", return_value=antwort) as ruf:
            verdichten(_verdichtungs_state(SEG_1, index=1))

        nachricht: str = ruf.call_args.args[0].messages[0]["content"]
        lagebild:  str = nachricht.split("[BEWERTUNGSOBJEKT]", 1)[0]

        self.assertIn(REIZ, lagebild)
        self.assertNotIn(SEG_0, lagebild)
        self.assertNotIn(SEG_2, lagebild)

    def test_ohne_segment_volltext_und_eine_warnung_die_das_benennt(self) -> None:
        """Ein Rueckfall darf nicht aussehen wie der Normalfall."""
        zustand: dict = _verdichtungs_state("", index=0, gesamt=0)

        antwort = SimpleNamespace(text="ein Kern")
        with patch.object(model_service.chat, "submit_sync", return_value=antwort) as ruf:
            with self.assertLogs(VERDICHTUNG_LOGGER, level="WARNING") as log:
                verdichten(zustand)

        objekt: str = ruf.call_args.args[0].messages[0]["content"].split(
            "[BEWERTUNGSOBJEKT]", 1
        )[1]
        self.assertIn(SEG_0, objekt)
        self.assertIn(SEG_2, objekt)

        rueckfall = [
            r for r in log.records
            if r.levelname == "WARNING" and "kein Segment" in r.getMessage()
        ]
        self.assertEqual(len(rueckfall), 1)

    def test_positiver_zwilling_mit_segment_keine_rueckfall_warnung(self) -> None:
        """Zwingend: die Zusicherung oben erwartet eine Warnung.

        Ohne diesen Zwilling bliebe unbemerkt, wenn die Verdichtung IMMER
        warnt — auch dann, wenn ein Segment vorliegt.
        """
        with self.assertLogs(VERDICHTUNG_LOGGER, level="INFO") as log:
            _bewertungsobjekt(_verdichtungs_state(SEG_1, index=1))

        rueckfall = [r for r in log.records if "kein Segment" in r.getMessage()]
        self.assertEqual(rueckfall, [])

        quelle = [r for r in log.records if "quelle=segment" in r.getMessage()]
        self.assertEqual(len(quelle), 1)


if __name__ == "__main__":
    unittest.main()
