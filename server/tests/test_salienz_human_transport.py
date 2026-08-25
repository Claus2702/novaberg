"""Tests fuer salienz_human — die Salienz des Reizes erreicht den CharacterGraph.

Ziel: Novas Segmente bekommen einen Boden aus dem, was der Nutzer gesagt hat.
Die Formel `max(salienz_human × nutzer_gewichtung, salienz_charakter)` braucht
salienz_human als Operanden; ohne ihn faellt sie auf den Eigen-Pfad zusammen
und Nova speichert ihre Antworten auf einen wichtigen Satz so gering wie ihre
Antworten auf eine Floskel.

Befund, aus dem das entstand (Chat 112): Der Wert existierte, kam aber nie an.
Turn 08246994 vom 27.07.2026 — drei Nutzer-Segmente mit 0.4/0.7/0.6 um 19:25,
zwei Nova-Segmente um 19:26. Vierzig Sekunden, dieselbe turn_id, dieselbe
Tabelle. Der CharacterGraph hat das LLM erneut geraten lassen.

Zwei Dinge werden hier scharf getrennt:
  - None  = es gab keine Nutzeraeusserung (AgentGraph, eigener Impuls)
  - 0.0   = es gab eine, sie war belanglos
Wer beides zusammenwirft, kann einen fehlenden Wert nicht mehr von einem
gemessenen unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.base import GraphBase
from graph.nodes.enricher import _intentionen_bestimmen
from graph.nodes.salience import (
    _intentionen_human_ermitteln,
    _salienz_human_ermitteln,
    _salienz_wert_lesen,
    analyze,
)

REIZ:     str = "Die Rotverschiebung entfernter Galaxien belegt die Ausdehnung des Raums."
REAKTION: str = "Und diese Ausdehnung beschleunigt sich, was niemand erwartet hatte."

LOGGER: str = "ki_server.salience"


def _antwort(salienz, intentionen: list | None = None) -> MagicMock:
    """Baut eine LLM-Antwort-Attrappe mit einem bestimmten Salienzwert.

    Vorbedingung: salienz ist der Wert, den das Modell im Feld 'salienz'
        liefern soll — bewusst ohne Typannahme, damit auch unlesbare Werte
        ("hoch", None) geprueft werden koennen.
    Nachbedingung: ein Objekt mit den drei Attributen, die analyze() liest.
    Fehlerfaelle: keine.
    """
    antwort = MagicMock()
    antwort.parsed = {
        "salienz":        salienz,
        "themen":         ["Kosmologie"],
        "dimension":      "wissen",
        "gedaechtnistyp": "semantisch",
        "emotion":        "neugier",
        "arousal":        0.4,
        "modus":          "sachlich",
        "intentionen":    intentionen if intentionen is not None else [],
    }
    antwort.token_total = 11
    antwort.text        = "{}"
    return antwort


def _state(graph_rolle: str, **kw) -> dict:
    """Erzeugt den Eingangs-State fuer einen analyze()-Lauf."""
    zustand: dict = {
        "graph_rolle":      graph_rolle,
        "ei_calc_rolle":    "character" if graph_rolle in ("character", "agent") else "user",
        "user_prompt":      REIZ,
        "response":         REAKTION,
        "pending_writes":   [],
        "token_total":      0,
        "turn_id":          "t-salienz-human",
        "character_id":     "nova",
        "gravitationsterm": 0.0,
        "salienz_human":    None,
    }
    zustand.update(kw)
    return zustand


def _lauf(
    graph_rolle: str,
    salienzen: list,
    postgres_url: str = "",
    intentionen_je_segment: list | None = None,
    **kw,
) -> tuple[list, dict]:
    """Fuehrt analyze() mit je einem Segment pro Salienzwert aus.

    Vorbedingung: salienzen ist nicht leer; jeder Eintrag ist der Wert, den das
        Modell fuer das jeweilige Segment liefern soll.
    Nachbedingung: Rueckgabe (pipeline_log-Eintraege, Ergebnis-State).
    Fehlerfaelle: leere Liste — ValueError, weil ein Lauf ohne Segment nichts
        misst und der Test dann etwas anderes pruefte als er behauptet.

    postgres_url wird durchgereicht, weil der Node daran entscheidet, ob er den
    Charakter-Faktor laedt. Leer heisst: kein Pflicht-Pfad. Die Formel-Tests in
    test_salienz_formel.py nutzen denselben Helfer — eine zweite Kopie liefe
    beim naechsten Umbau des Nodes auseinander.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not salienzen:
        raise ValueError("_lauf: mindestens ein Salienzwert noetig")

    # ── Verarbeitung ────────────────────────────
    puffer  = MagicMock()
    zustand = _state(graph_rolle, **kw)
    modell  = __import__("services.model_services", fromlist=["model_service"]).model_service

    with patch("memory.pipeline_log.get_buffer", return_value=puffer):
        with patch(
            "graph.nodes.salience._prompt_segmentieren",
            side_effect=lambda t: [t] * len(salienzen),
        ):
            with patch.object(
                modell.chat, "submit_sync",
                side_effect=[
                    _antwort(wert, (intentionen_je_segment or [None] * len(salienzen))[i])
                    for i, wert in enumerate(salienzen)
                ],
            ) as chat_mock:
                ergebnis = analyze(zustand, MagicMock(), "meister", postgres_url)

                # Innerhalb des Patches abgreifen — draussen ist das Original
                # wiederhergestellt und die Aufrufliste weg. Damit koennen
                # Tests den System-Prompt pruefen, der WIRKLICH ans Modell
                # ging, statt einen, den ein Hilfsaufruf daneben erzeugt.
                ergebnis["_system_prompts"] = [
                    ruf.args[0].system for ruf in chat_mock.call_args_list
                ]

    # ── Ausgabe ─────────────────────────────────
    return [ruf.args[0] for ruf in puffer.put_threadsafe.call_args_list], ergebnis


def _schritt(eintraege: list, name: str) -> list:
    """Filtert berechnung-Eintraege nach ihrem schritt-Feld."""
    return [e for e in eintraege if e.art == "berechnung" and e.inhalt.get("schritt") == name]


class SalienzWertLesenTest(unittest.TestCase):
    """Ein unlesbarer Wert darf nicht als 0.0 durchgehen."""

    def test_zahl_wird_gelesen(self):
        self.assertEqual(_salienz_wert_lesen({"salienz": 0.6}), 0.6)

    def test_zahl_als_zeichenkette_wird_gelesen(self):
        """Das Modell liefert gelegentlich "0.6" statt 0.6 — beides ist derselbe Wert."""
        self.assertEqual(_salienz_wert_lesen({"salienz": "0.6"}), 0.6)

    def test_fehlendes_feld_meldet_und_liefert_none(self):
        with self.assertLogs(LOGGER, level="ERROR") as protokoll:
            self.assertIsNone(_salienz_wert_lesen({"themen": ["Kosmologie"]}))
        self.assertIn("ohne Feld 'salienz'", "\n".join(protokoll.output))

    def test_unlesbarer_wert_meldet_und_nennt_ihn(self):
        with self.assertLogs(LOGGER, level="ERROR") as protokoll:
            self.assertIsNone(_salienz_wert_lesen({"salienz": "hoch"}))
        zeilen: str = "\n".join(protokoll.output)
        self.assertIn("nicht numerisch", zeilen)
        # Der Wert selbst gehoert in die Zeile — sonst ist nicht feststellbar,
        # was das Modell geliefert hat.
        self.assertIn("hoch", zeilen)


class SalienzHumanErmittelnTest(unittest.TestCase):
    """Das Maximum, und die Trennung von None und 0.0."""

    def test_maximum_gewinnt(self):
        """Ein Turn ist so gewichtig wie sein staerkster Teil."""
        self.assertEqual(_salienz_human_ermitteln([0.4, 0.7, 0.6]), 0.7)

    def test_einzelner_wert_bleibt_stehen(self):
        self.assertEqual(_salienz_human_ermitteln([0.35]), 0.35)

    def test_echte_null_bleibt_null(self):
        """Der positive Zwilling zum None-Fall: 0.0 ist ein Messergebnis."""
        self.assertEqual(_salienz_human_ermitteln([0.0, 0.0]), 0.0)

    def test_ohne_werte_none_statt_null(self):
        self.assertIsNone(_salienz_human_ermitteln([]))

    def test_ueber_eins_wird_gekappt_und_der_rohwert_genannt(self):
        with self.assertLogs(LOGGER, level="WARNING") as protokoll:
            self.assertEqual(_salienz_human_ermitteln([1.4]), 1.0)
        self.assertIn("1.40", "\n".join(protokoll.output))


class SalienzHumanImNodeTest(unittest.TestCase):
    """Wer den Wert setzt — und wer ihn ausdruecklich nicht setzt."""

    def test_humangraph_setzt_das_maximum_seiner_segmente(self):
        _, ergebnis = _lauf("human", [0.4, 0.7, 0.6])
        self.assertEqual(ergebnis["salienz_human"], 0.7)

    def test_charactergraph_ueberschreibt_den_gereichten_wert_nicht(self):
        """Er bewertet Novas Antwort — schriebe er hier, ersetzte die Reaktion den Reiz."""
        _, ergebnis = _lauf("character", [0.9], salienz_human=0.55)
        self.assertEqual(ergebnis["salienz_human"], 0.55)

    def test_agentgraph_laesst_none_stehen(self):
        """Ein eigener Gedanke hat keine Nutzeraeusserung."""
        _, ergebnis = _lauf("agent", [0.8])
        self.assertIsNone(ergebnis["salienz_human"])

    def test_unlesbares_segment_senkt_das_maximum_nicht(self):
        """Der Kern: ein nicht gelesener Wert ist kein Wert, keine Null."""
        with self.assertLogs(LOGGER, level="ERROR"):
            _, ergebnis = _lauf("human", [0.7, "hoch"])
        self.assertEqual(ergebnis["salienz_human"], 0.7)

    def test_gravitationsboost_faellt_nicht_in_den_wert(self):
        """salienz_human ist die LLM-Bewertung. Die Gravitation wird mit der
        Formel ein Antrieb des Eigen-Pfads und zaehlte hier ein zweites Mal.
        """
        _, ergebnis = _lauf("human", [0.5], gravitationsterm=0.3)
        self.assertEqual(ergebnis["salienz_human"], 0.5)


class SalienzHumanForensikTest(unittest.TestCase):
    """Der Wert ist ohne Container-Log nachvollziehbar."""

    def test_pipeline_log_traegt_wert_und_herkunft(self):
        eintraege, _ = _lauf("human", [0.4, 0.7])
        zeilen: list = _schritt(eintraege, "salienz_human")

        self.assertEqual(len(zeilen), 1)
        inhalt: dict = zeilen[0].inhalt
        self.assertEqual(inhalt["salienz_human"], 0.7)
        # Nicht nur das Ergebnis, auch die Werte, aus denen es entstand —
        # sonst ist das Maximum im Nachhinein nicht nachrechenbar.
        self.assertEqual(inhalt["segmentwerte"], [0.4, 0.7])

    def test_charactergraph_schreibt_keine_solche_zeile(self):
        eintraege, _ = _lauf("character", [0.9])
        self.assertEqual(_schritt(eintraege, "salienz_human"), [])

    def test_ohne_lesbaren_wert_fehlereintrag_und_logzeile(self):
        with self.assertLogs(LOGGER, level="ERROR") as protokoll:
            eintraege, ergebnis = _lauf("human", ["hoch"])

        self.assertIsNone(ergebnis["salienz_human"])
        self.assertIn("keinen Boden", "\n".join(protokoll.output))

        fehler: list = [
            e for e in eintraege
            if e.art == "fehler" and e.inhalt.get("grund") == "salienz_human_unermittelbar"
        ]
        self.assertEqual(len(fehler), 1)
        self.assertEqual(fehler[0].inhalt["lesbare_werte"], 0)


class _StubGraph:
    """Traegt nur, was create_state von self liest."""

    MAX_CORRECTIONS: int = 2


class CreateStateTest(unittest.TestCase):
    """Der Default ist None, nicht 0.0."""

    def test_ohne_angabe_none(self):
        zustand = GraphBase.create_state(
            _StubGraph(), user_prompt="Wie entstehen schwarze Loecher?", user_id="meister",
        )
        self.assertIsNone(zustand["salienz_human"])

    def test_gereichter_wert_kommt_an(self):
        zustand = GraphBase.create_state(
            _StubGraph(), user_prompt=REAKTION, user_id="meister", salienz_human=0.62,
        )
        self.assertEqual(zustand["salienz_human"], 0.62)

    def test_echte_null_ueberlebt_die_uebergabe(self):
        """Der positive Zwilling: 0.0 darf nicht zu None werden."""
        zustand = GraphBase.create_state(
            _StubGraph(), user_prompt=REAKTION, user_id="meister", salienz_human=0.0,
        )
        self.assertEqual(zustand["salienz_human"], 0.0)
        self.assertIsNotNone(zustand["salienz_human"])


if __name__ == "__main__":
    unittest.main()


class IntentionenHumanErmittelnTest(unittest.TestCase):
    """Die Vereinigung ueber die Segmente, ohne Doppelungen."""

    def test_vereinigung_ueber_segmente(self) -> None:
        """Ein Turn setzt eine Richtung, wenn irgendein Teil von ihm sie setzt.

        Dieselbe Begruendung, aus der `_salienz_human_ermitteln` das Maximum
        nimmt: Ein beilaeufiger Nebensatz darf eine Frage nicht verduennen.
        """
        self.assertEqual(
            _intentionen_human_ermitteln(
                ["reflexion", "information_erfragen", "bestaetigung"],
            ),
            ["reflexion", "information_erfragen", "bestaetigung"],
        )

    def test_doppelungen_fallen_weg_die_erste_stellung_bleibt(self) -> None:
        """Ein Wert, der in zwei Segmenten steht, zaehlt einmal."""
        self.assertEqual(
            _intentionen_human_ermitteln(
                ["reflexion", "information_erfragen", "reflexion"],
            ),
            ["reflexion", "information_erfragen"],
        )

    def test_leerwerte_fallen_weg(self) -> None:
        """Leere und reine Leerzeichen-Eintraege sind keine Intentionen."""
        self.assertEqual(
            _intentionen_human_ermitteln(["", "  ", "reflexion"]), ["reflexion"],
        )

    def test_ohne_segmente_leere_liste(self) -> None:
        """Leer heisst fuer M1 **fehlend**, und zwar dort, nicht hier.

        Diese Funktion erfindet keinen Ersatzwert.
        """
        self.assertEqual(_intentionen_human_ermitteln([]), [])


class IntentionenImNodeTest(unittest.TestCase):
    """Wer die Intentionen des Reizes in den State schreibt."""

    def test_humangraph_sammelt_ueber_alle_segmente(self) -> None:
        """Pfad 1 legt die Vereinigung in den State — die Quelle von M1."""
        _, ergebnis = _lauf(
            "human", [0.4, 0.7],
            intentionen_je_segment=[["reflexion"], ["information_erfragen"]],
        )
        self.assertEqual(
            ergebnis["user_intentionen"], ["reflexion", "information_erfragen"],
        )

    def test_charactergraph_ueberschreibt_den_gereichten_wert_nicht(self) -> None:
        """Der CharacterGraph bewertet Novas Antwort und schreibt hier nicht.

        Taete er es, ersetzte Novas Intention die des Nutzers — und M1 maesse
        die falsche Seite des Gespraechs.
        """
        _, ergebnis = _lauf(
            "character", [0.9],
            intentionen_je_segment=[["recherche_vertiefen"]],
            user_intentionen=["information_erfragen"],
        )
        self.assertEqual(ergebnis["user_intentionen"], ["information_erfragen"])

    def test_ein_segment_ohne_intentionen_liefert_die_leere_liste(self) -> None:
        """Der positive Zwilling zum Sammel-Test.

        Wenn nichts kommt, steht nichts da — kein Rueckfall auf einen
        erfundenen Wert.
        """
        _, ergebnis = _lauf("human", [0.5], intentionen_je_segment=[[]])
        self.assertEqual(ergebnis["user_intentionen"], [])


class IntentionenVorrangTest(unittest.TestCase):
    """Der Wert aus dem Ereignis schlaegt die Ableitung aus der Historie.

    Ohne diesen Vorrang ueberschriebe der Enricher die Quelle von M1, sechs
    Nodes bevor die Achse sie liest — und zwar mit einem Wert, der nur dann
    zufaellig stimmt, wenn Pfad 1 seinen Session-Turn schon geschrieben hat.
    """

    HISTORIE: list = [
        {"rolle": "user", "modus": "alltag", "intentionen": ["smalltalk"]},
    ]

    def test_ereignis_gewinnt(self) -> None:
        """Der Wert aus Pfad 1 schlaegt die Ableitung aus der Historie."""
        werte, herkunft = _intentionen_bestimmen(
            ["information_erfragen"], self.HISTORIE,
        )
        self.assertEqual(werte, ["information_erfragen"])
        self.assertEqual(herkunft, "Ereignis")

    def test_ohne_ereignis_traegt_die_historie(self) -> None:
        """Der Rueckfall bleibt — ein eigener Impuls hat keine Nutzeraeusserung."""
        werte, herkunft = _intentionen_bestimmen([], self.HISTORIE)
        self.assertEqual(werte, ["smalltalk"])
        self.assertEqual(herkunft, "letzter Session-Turn")

    def test_ohne_beides_leer(self) -> None:
        """Keine Quelle heisst leere Liste, nicht ein erfundener Wert."""
        werte, herkunft = _intentionen_bestimmen([], [])
        self.assertEqual(werte, [])
        self.assertEqual(herkunft, "letzter Session-Turn")

    def test_die_herkunft_unterscheidet_gleiche_werte(self) -> None:
        """Beide Quellen koennen denselben Wert tragen.

        Welche von beiden gegriffen hat, steht sonst nirgends — und genau das
        war zwei Monate unbeobachtbar.
        """
        _, aus_ereignis = _intentionen_bestimmen(["smalltalk"], self.HISTORIE)
        _, aus_historie = _intentionen_bestimmen([], self.HISTORIE)
        self.assertNotEqual(aus_ereignis, aus_historie)


class CreateStateIntentionenTest(unittest.TestCase):
    """Die Graphgrenze — der Wert muss sie ueberleben."""

    def test_ohne_angabe_leere_liste(self) -> None:
        """Ohne gereichten Wert steht die leere Liste, nicht None."""
        zustand = GraphBase.create_state(
            _StubGraph(), user_prompt=REAKTION, user_id="meister",
        )
        self.assertEqual(zustand["user_intentionen"], [])

    def test_gereichte_werte_kommen_an(self) -> None:
        """Der Wert ueberlebt die Grenze zwischen den beiden Graphen."""
        zustand = GraphBase.create_state(
            _StubGraph(), user_prompt=REAKTION, user_id="meister",
            user_intentionen=["information_erfragen", "reflexion"],
        )
        self.assertEqual(
            zustand["user_intentionen"], ["information_erfragen", "reflexion"],
        )
