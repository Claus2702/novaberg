"""Zeugen fuer die Sachlage — das fortgeschriebene Verstehen des Gespraechs.

**Konzept:** `docs/novaberg-thinking-lage_k.md`, Scheibe 1. Der Knoten
`sachlage` laeuft vor dem Router und schreibt ein Artefakt mit Gegenstand,
vermutetem Nutzerziel, Ausdrucksweise und Referenzobjekten — fortgeschrieben
ueber Turns, verfallend nach vier Stunden.

Zeugen dieser Datei:
  * **Jeder Weg traegt seine Herkunfts-Marke.** Fuenf Wege fuehren zu einem
    Artefakt im State (frisch, fortgeschrieben, verfallen_neu, Impuls,
    Ausfall) — ohne Marke waere „nicht gerechnet" von „so gerechnet" nicht
    zu unterscheiden. Der Ausfallweg wird eigens geprueft, weil er der
    stille ist.
  * **Die Smalltalk-Schranke wird an der Pruefung gemessen, nicht am
    Prompt.** Der Prompt verlangt leere `offen`-Listen fuer latente
    Objekte; verlassen wird sich darauf nicht — `_validate_artifact` leert
    sie, und der Zeuge haelt das fest.
  * **Der Block wird an seinem Inhalt geprueft.** Ein latentes Objekt darf
    im [SACHLAGE]-Block keine offene Eigenschaft nennen — sonst erzeugt
    jede Beilaeufigkeit Fragestoff im Verfasser.
  * **Die Verdrahtung ist ein eigener Zeuge.** Ein Knoten, der rechnet und
    dessen Ergebnis niemand liest, war der Defekt der Frage-Art vom
    27.08.2026 — der Graph traegt die Kante, der Verfasser den Block.
  * **Die Wiederaufnahme** (Scheibe 5, 28.08.2026): Auf dem rechnenden Weg
    sucht der Knoten mit dem Prompt-Embedding die aehnlichste fruehere
    Blase des Paares — unter Ausschluss des eigenen Themas —, gibt sie dem
    Prompt als fruehere Sachlage mit und traegt die Kennung im Artefakt.
    Der Impuls-Weg sucht nicht; ohne Vektor laeuft der Turn ohne Suche und
    sagt es; der Block nennt die Rueckkehr.
  * **Der Verlauf traegt Novas Antwort ganz.** `[gemessen]` 28.08.2026: Eine
    offene Eigenschaft blieb drei Turns offen, obwohl Nova sie beantwortet
    hatte — die Antwort war 973 Zeichen lang, die Substanz begann bei 384,
    und das Rendering schnitt bei 400. Sechs von elf Antworten des Paares
    sind laenger als 400. Der Zeuge haelt das Rendering: Substanz jenseits
    der alten Grenze kommt an, Regieanweisungen (*…*) nicht, Zeilenumbrueche
    in einer Antwort machen keine zweite Verlaufszeile — und der Prompt, der
    zum Modell geht, traegt die Regel, dass Novas Antworten decken.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from graph.nodes.sachlage import (
    HERKUNFT_AUSFALL,
    HERKUNFT_FORTGESCHRIEBEN,
    HERKUNFT_FRISCH,
    HERKUNFT_IMPULS,
    HERKUNFT_VERFALLEN_NEU,
    _derive,
    _render_history,
    _validate_artifact,
    sachlage_assess,
    sachlage_block,
)
from config import SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS

VOLLSTAENDIG: dict = {
    # `thema` ist seit Scheibe 4 (28.08.2026) Pflichtfeld — der Anzeigename
    # der Blase und das Findewort neben dem Vektor, aus demselben Call.
    "thema":          "Geburtstag",
    "gegenstand":     "Ein anstehender Geburtstag",
    "nutzerziel":     "vermutlich Planung und Vorbereitung",
    "ausdrucksweise": "beilaeufig erzaehlend",
    "objekte": [
        {"name": "Geburtstag", "klasse": "vorgang", "akut": True,
         "gedeckt": {"anlass": "erwaehnt"}, "offen": ["wer", "wann", "geschenk"]},
    ],
}


def _state(**felder: object) -> dict:
    """Ein Zustand, wie ihn der Knoten liest."""
    basis: dict = {
        "user_id": "u", "character_id": "c", "turn_id": "t",
        "user_prompt": "bei uns steht ein Geburtstag an",
        "session_turns": [], "event_payload": {}, "event_source": "user",
    }
    basis.update(felder)
    return basis


class DasArtefaktWirdGeprueftTest(unittest.TestCase):
    """_validate_artifact — die Wand zwischen Parse und State."""

    def test_vollstaendig_geht_durch(self) -> None:
        """Die Positivprobe — sonst prueft der Rest nur das Ablehnen."""
        self.assertIsNotNone(_validate_artifact(dict(VOLLSTAENDIG)))

    def test_fehlende_pflichtfelder_werden_verworfen(self) -> None:
        """Ein halbes Artefakt ist keines."""
        kaputt: dict = {"gegenstand": "x"}

        self.assertIsNone(_validate_artifact(kaputt))

    def test_kein_dict_wird_verworfen(self) -> None:
        """Manche Modelle liefern Top-Level-Listen."""
        self.assertIsNone(_validate_artifact([VOLLSTAENDIG]))

    def test_latentes_objekt_verliert_offene_eigenschaften(self) -> None:
        """Die Smalltalk-Schranke: Beilaeufigkeit erzeugt keinen Fragestoff.

        Geprueft an der Pruefung, nicht am Prompt — der Prompt verlangt es,
        verlassen wird sich darauf nicht.
        """
        artefakt: dict = dict(VOLLSTAENDIG)
        artefakt["objekte"] = [
            {"name": "Rasen", "klasse": "objekt", "akut": False,
             "gedeckt": {}, "offen": ["flaeche", "sorte"]},
        ]

        geprueft = _validate_artifact(artefakt)

        self.assertEqual(geprueft["objekte"][0]["offen"], [])


class DerBlockTraegtNurAkutesTest(unittest.TestCase):
    """sachlage_block — was der Verfasser tatsaechlich liest."""

    def test_akutes_objekt_steht_mit_offenen_eigenschaften(self) -> None:
        """Der Kernfall: Geburtstag akut -> Wer/Wann/Geschenk im Block."""
        block: str = sachlage_block(VOLLSTAENDIG)

        self.assertTrue(block.startswith("[SACHLAGE]"))
        self.assertIn("Geburtstag", block)
        self.assertIn("wer", block)

    def test_latentes_objekt_erzeugt_keine_zeile(self) -> None:
        """Die Gegenprobe — sonst waere die Schranke nur im Parser."""
        artefakt: dict = dict(VOLLSTAENDIG)
        artefakt["objekte"] = [
            {"name": "Rasen", "klasse": "objekt", "akut": False,
             "gedeckt": {}, "offen": []},
        ]

        self.assertNotIn("Rasen", sachlage_block(artefakt))

    def test_nutzerziel_steht_immer(self) -> None:
        """Auch ohne Objekte traegt der Block das Verstehen."""
        artefakt: dict = dict(VOLLSTAENDIG)
        artefakt["objekte"] = []

        self.assertIn("vermutlich Planung", sachlage_block(artefakt))


class JederWegTraegtSeineMarkeTest(unittest.TestCase):
    """sachlage_assess — die fuenf Rueckkehrpfade."""

    def test_frisch_ohne_vorgaenger(self) -> None:
        """Cold-Start: kein Bestand, Erhebung liefert."""
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(None, False)), \
             patch("graph.nodes.sachlage._derive",
                   return_value=dict(VOLLSTAENDIG)), \
             patch("graph.nodes.sachlage._sachlage_store"), \
             patch("graph.nodes.sachlage.short_goal_track"), \
             patch("graph.nodes.sachlage._persist_history"), \
             patch("graph.nodes.sachlage.log_berechnung"):
            state = sachlage_assess(_state())

        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_FRISCH)

    def test_fortgeschrieben_mit_vorgaenger(self) -> None:
        """Der Regelfall: die Blase lebt weiter."""
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(dict(VOLLSTAENDIG), False)), \
             patch("graph.nodes.sachlage._derive",
                   return_value=dict(VOLLSTAENDIG)), \
             patch("graph.nodes.sachlage._sachlage_store"), \
             patch("graph.nodes.sachlage.short_goal_track"), \
             patch("graph.nodes.sachlage._persist_history"), \
             patch("graph.nodes.sachlage.log_berechnung"):
            state = sachlage_assess(_state())

        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_FORTGESCHRIEBEN)

    def test_verfallen_beginnt_neu_und_benennt_es(self) -> None:
        """Nach der Frist traegt das Artefakt die Verfallsmarke."""
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(None, True)), \
             patch("graph.nodes.sachlage._derive",
                   return_value=dict(VOLLSTAENDIG)), \
             patch("graph.nodes.sachlage._sachlage_store"), \
             patch("graph.nodes.sachlage.short_goal_track"), \
             patch("graph.nodes.sachlage._persist_history"), \
             patch("graph.nodes.sachlage.log_berechnung"):
            state = sachlage_assess(_state())

        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_VERFALLEN_NEU)

    def test_impuls_uebernimmt_ohne_call(self) -> None:
        """Novas eigener Impuls aendert das Nutzerziel nicht."""
        zustand: dict = _state(
            event_payload={"reiz_herkunft": "eigener_impuls"},
        )
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(dict(VOLLSTAENDIG), False)), \
             patch("graph.nodes.sachlage._derive") as erheben, \
             patch("graph.nodes.sachlage.log_berechnung"):
            state = sachlage_assess(zustand)

        erheben.assert_not_called()
        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_IMPULS)
        self.assertEqual(state["sachlage"]["gegenstand"],
                         VOLLSTAENDIG["gegenstand"])

    def test_ausfall_uebernimmt_den_vorgaenger_und_benennt_es(self) -> None:
        """Der stille Weg, laut gemacht: Call rot -> Vorgaenger mit Marke."""
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(dict(VOLLSTAENDIG), False)), \
             patch("graph.nodes.sachlage._derive", return_value=None), \
             patch("graph.nodes.sachlage.log_berechnung"):
            state = sachlage_assess(_state())

        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_AUSFALL)
        self.assertEqual(state["sachlage"]["gegenstand"],
                         VOLLSTAENDIG["gegenstand"])

    def test_ausfall_ohne_vorgaenger_liefert_leeres_artefakt_mit_marke(self) -> None:
        """Der doppelte Ausfall — auch er ist gekennzeichnet, nicht stumm."""
        with patch("graph.nodes.sachlage.sachlage_load",
                   return_value=(None, False)), \
             patch("graph.nodes.sachlage._derive", return_value=None), \
             patch("graph.nodes.sachlage.log_berechnung"):
            state = sachlage_assess(_state())

        self.assertEqual(state["sachlage"]["herkunft"], HERKUNFT_AUSFALL)


class DerVerlaufTraegtNovasAntwortTest(unittest.TestCase):
    """_render_history — was das Modell vom Verlauf sieht.

    Die Zahlen sind die der Messung vom 28.08.2026: Antwort 973 Zeichen,
    Substanz ab 384, Schnitt bei 400 — die Eigenschaft blieb offen.
    """

    def test_substanz_jenseits_von_400_zeichen_kommt_an(self) -> None:
        antwort = ("*Sie lehnt sich vor.* " + "Der Rettich braucht Wasser. " * 20
                   + "ENTSCHEIDEND: Wasser treibt das Wurzelwachstum staerker als Licht.")
        self.assertGreater(antwort.index("ENTSCHEIDEND"), 400)

        gerendert = _render_history([{"rolle": "assistant", "inhalt": antwort}])

        self.assertIn("ENTSCHEIDEND: Wasser treibt", gerendert)

    def test_regieanweisungen_stehen_nicht_im_verlauf(self) -> None:
        gerendert = _render_history([
            {"rolle": "assistant",
             "inhalt": "*Sie zieht eine Augenbraue hoch.* Wasser ist der Hebel. *Sie nickt.*"},
        ])

        self.assertEqual(gerendert, "Nova: Wasser ist der Hebel.")

    def test_eine_antwort_bleibt_eine_verlaufszeile(self) -> None:
        gerendert = _render_history([
            {"rolle": "user", "inhalt": "Licht oder Wasser?"},
            {"rolle": "assistant", "inhalt": "Wasser.\n\nUnd zwar gleichmaessig.\nOhne Schwall."},
        ])

        self.assertEqual(gerendert.splitlines(), [
            "Nutzer: Licht oder Wasser?", "Nova: Wasser. Und zwar gleichmaessig. Ohne Schwall.",
        ])

    def test_eine_reine_regieanweisung_erzeugt_keine_zeile(self) -> None:
        gerendert = _render_history([{"rolle": "assistant", "inhalt": "*Sie schweigt.*"}])

        self.assertEqual(gerendert, "(noch keine Beitraege)")

    def test_der_prompt_zum_modell_traegt_novas_antwort_und_die_deckungsregel(self) -> None:
        """Am gerenderten Prompt gemessen, nicht am Quelltext."""
        gesehen: dict = {}

        def _fang(request: object, timeout: float) -> None:
            gesehen["prompt"] = request.messages[0]["content"]
            raise RuntimeError("kein Modell im Zeugen")

        with patch("graph.nodes.sachlage.model_service") as ms:
            ms.chat.submit_sync.side_effect = _fang
            _derive(None, [{"rolle": "assistant", "inhalt": "Wasser treibt das Wurzelwachstum."}], "Stimmt das?")

        self.assertIn("Nova: Wasser treibt das Wurzelwachstum.", gesehen["prompt"])
        self.assertIn("Nova", gesehen["prompt"].split("Regeln:")[1])
        self.assertIn("deckt", gesehen["prompt"].split("Regeln:")[1])


class DasThemaBenenntDieSacheTest(unittest.TestCase):
    """Der Prompt sagt, dass `thema` und `gegenstand` die Sache nennen, nie den Wechsel.

    `[gemessen]` 28.08.2026, erster Betriebsturn nach Scheibe 4: Vorgaenger
    Rettich, Turn Neutronensterne — `thema='Themenwechsel'`, `gegenstand='Ein
    abruptes Abweichen vom biologischen Fachgespraech hin zu …'`. Der Vektor
    dieser Zeile zeigt halb auf das alte Thema; das Findewort ist keins. Der
    Zeuge haelt den gerenderten Prompt, die Wirkung misst das Labor
    (`labor/2026-08-28_sachlage_thema_wechsel.py`, fuenf Laeufe vorher/nachher).
    """

    def test_der_prompt_verlangt_die_sache_statt_des_wechsels(self) -> None:
        gesehen: dict = {}

        def _fang(request: object, timeout: float) -> None:
            gesehen["prompt"] = request.messages[0]["content"]
            raise RuntimeError("kein Modell im Zeugen")

        with patch("graph.nodes.sachlage.model_service") as ms:
            ms.chat.submit_sync.side_effect = _fang
            _derive(dict(VOLLSTAENDIG), [], "Warum leuchten Neutronensterne noch?")

        regeln = gesehen["prompt"].split("Regeln:")[1]
        self.assertIn("Themenwechsel", regeln)
        self.assertIn("neue Sache", regeln)


FRUEHERE: dict = {
    "turn_id": "t-frueher", "thema": "Gravitationslinse", "kosinus": 0.61,
    "gegenstand": "Die Lichtablenkung an Schwarzen Loechern.",
    "objekte": [{"name": "Gravitationslinse", "klasse": "vorgang", "akut": True,
                 "gedeckt": {"mechanismus": "Raumkruemmung"}, "offen": ["Massenbestimmung"]}],
    "erstellt_am": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
}


def _rechnender_lauf(state: dict, treffer: dict | None, erhoben: dict | None = None) -> dict:
    """Ein Lauf des Knotens mit gepatchten Nachbarn; `history_nearest` liefert `treffer`."""
    with patch("graph.nodes.sachlage.sachlage_load", return_value=(dict(VOLLSTAENDIG), False)), \
         patch("graph.nodes.sachlage.history_nearest", return_value=treffer) as suche, \
         patch("graph.nodes.sachlage._derive", return_value=dict(erhoben or VOLLSTAENDIG)), \
         patch("graph.nodes.sachlage._sachlage_store"), \
         patch("graph.nodes.sachlage.short_goal_track"), \
         patch("graph.nodes.sachlage._persist_history"), \
         patch("graph.nodes.sachlage.log_berechnung"):
        ergebnis = sachlage_assess(state)
    ergebnis["_suche"] = suche
    return ergebnis


class DieWiederaufnahmeTest(unittest.TestCase):
    """Scheibe 5 — die fruehere Blase kommt aus dem Faktum zurueck."""

    def test_die_suche_nutzt_das_prompt_embedding_und_schliesst_das_eigene_thema_aus(self) -> None:
        state = _state(prompt_embedding=[0.1, 0.2, 0.3])

        ergebnis = _rechnender_lauf(state, None)

        ruf = ergebnis["_suche"].call_args
        self.assertEqual(ruf.kwargs["embedding"], [0.1, 0.2, 0.3])
        self.assertEqual(ruf.kwargs["ausser_thema"], VOLLSTAENDIG["thema"])
        self.assertEqual(ruf.kwargs["min_kosinus"], SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS)

    def test_der_impuls_weg_sucht_nicht(self) -> None:
        state = _state(prompt_embedding=[0.1, 0.2, 0.3], event_source="shadow",
                       event_payload={"eigener_gedanke": True, "prompt_thema": "x", "inhalt": "y"})
        with patch("graph.nodes.sachlage.reiz_ist_eigener_gedanke", return_value=True):
            ergebnis = _rechnender_lauf(state, FRUEHERE)

        self.assertEqual(ergebnis["_suche"].call_count, 0)
        self.assertNotIn("wiederaufnahme", ergebnis["sachlage"])

    def test_ohne_treffer_ist_die_wiederaufnahme_null(self) -> None:
        ergebnis = _rechnender_lauf(_state(prompt_embedding=[1.0]), None)

        self.assertIsNone(ergebnis["sachlage"]["wiederaufnahme"])

    def test_mit_treffer_traegt_das_artefakt_die_kennung(self) -> None:
        ergebnis = _rechnender_lauf(_state(prompt_embedding=[1.0]), FRUEHERE)

        self.assertEqual(ergebnis["sachlage"]["wiederaufnahme"],
                         {"turn_id": "t-frueher", "thema": "Gravitationslinse", "kosinus": 0.61,
                          "erstellt_am": FRUEHERE["erstellt_am"]})

    def test_der_prompt_traegt_die_fruehere_blase_und_die_regel(self) -> None:
        gesehen: dict = {}

        def _fang(request: object, timeout: float) -> None:
            gesehen["prompt"] = request.messages[0]["content"]
            raise RuntimeError("kein Modell im Zeugen")

        with patch("graph.nodes.sachlage.model_service") as ms:
            ms.chat.submit_sync.side_effect = _fang
            _derive(dict(VOLLSTAENDIG), [], "Nochmal zurueck zur Gravitationslinse", wiederaufnahme=FRUEHERE)
            mit: str = gesehen["prompt"]
            _derive(dict(VOLLSTAENDIG), [], "Nochmal zurueck zur Gravitationslinse", wiederaufnahme=None)
            ohne: str = gesehen["prompt"]

        self.assertIn("Raumkruemmung", mit)
        self.assertIn("woertlich", mit.split("fruehere Sachlage")[1].lower())
        self.assertNotIn("fruehere Sachlage", ohne)

    def test_ohne_vektor_laeuft_der_turn_ohne_suche_und_sagt_es(self) -> None:
        state = _state()  # kein prompt_embedding
        with patch("graph.nodes.sachlage.model_service") as ms:
            ms.embed.submit_sync.side_effect = RuntimeError("Worker aus")
            with self.assertLogs("ki_server.sachlage", level="WARNING") as log:
                ergebnis = _rechnender_lauf(state, FRUEHERE)

        self.assertEqual(ergebnis["_suche"].call_count, 0)
        self.assertEqual(ergebnis["sachlage"]["herkunft"], HERKUNFT_FORTGESCHRIEBEN)
        self.assertIsNone(ergebnis["sachlage"]["wiederaufnahme"])
        self.assertTrue(any("Wiederaufnahme" in zeile for zeile in log.output))

    def test_der_block_nennt_die_rueckkehr(self) -> None:
        block = sachlage_block({**VOLLSTAENDIG, "wiederaufnahme": {
            "turn_id": "t", "thema": "Gravitationslinse", "kosinus": 0.6,
            "erstellt_am": FRUEHERE["erstellt_am"]}})

        self.assertIn("Gravitationslinse", block)
        self.assertIn("zurueck", block.lower().replace("ü", "ue"))
        self.assertNotIn("zurueck", sachlage_block(dict(VOLLSTAENDIG)).lower().replace("ü", "ue"))


class DieVerdrahtungStehtTest(unittest.TestCase):
    """Der Knoten haengt im Graphen, der Verfasser liest ihn."""

    def test_der_graph_traegt_die_kante(self) -> None:
        """reducer -> sachlage_node -> router, im Quelltext des Graphen."""
        import inspect

        from graph import character_graph
        quelle: str = inspect.getsource(character_graph)

        self.assertIn('graph.add_edge("reducer",    "sachlage_node")', quelle)
        self.assertIn('graph.add_edge("sachlage_node", "router")', quelle)

    def test_der_stream_kennt_den_knoten(self) -> None:
        """Fund der zweiten Kontrolle (28.08.2026): 21 Knoten, 20 Labels.

        Ohne Label broadcastet jeder Turn eine character_stage mit dem rohen
        Knotennamen an alle Clients. Geprueft gegen die Tabelle, nicht gegen
        den kompilierten Graphen — den prueft das Kontrollwerkzeug.
        """
        from services.event_consumer import CHARACTER_NODE_LABELS

        self.assertIn("sachlage_node", CHARACTER_NODE_LABELS)

    def test_leere_sachlage_mit_marke_ist_kein_fehler(self) -> None:
        """Fund der zweiten Kontrolle: Der Verfasser diagnostizierte
        »nicht gelaufen«, obwohl der Knoten lief und regulaer nichts trug
        (Impuls nach Verfall). Gelaufen-und-leer ist info, nicht error."""
        from ei.haltung import haltung_berechnen
        from graph.nodes import verfasser

        zustand: dict = {
            "user_prompt": "x", "user_id": "u", "character_id": "c",
            "turn_id": "t", "memory_context": "", "web_context": "",
            "session_turns": [], "task_block": "", "event_payload": {},
            "event_source": "user", "gespraechsvektor": "", "gv_detail": {},
            "sachlage": {"herkunft": "impuls_uebernommen"},
            # Eine echte Haltung, damit nur die Sachlage-Diagnose gemessen
            # wird — ohne sie feuert der (richtige) Haltungs-Error.
            "haltung": haltung_berechnen("werkstatt", {}),
        }
        with self.assertNoLogs("ki_server.verfasser", level="ERROR"):
            verfasser._build_system_prompt(zustand)

    def test_das_stage_detail_traegt_das_verstehen(self) -> None:
        """Der Client sieht Gegenstand, akute Objekte und Herkunft — nicht
        nur den Knotennamen (Screenshot-Format: Teile mit »·« verbunden)."""
        from services.event_consumer import _stage_detail_bauen

        detail: str = _stage_detail_bauen(
            "sachlage_node",
            {"sachlage": {**VOLLSTAENDIG, "herkunft": "frisch"}},
        )

        self.assertIn("Geburtstag", detail)
        self.assertIn("frisch", detail)
        self.assertIn(" · ", detail)

    def test_das_stage_detail_ohne_sachlage_ist_der_strich(self) -> None:
        """Die Gegenprobe: kein Artefakt, kein erfundenes Detail."""
        from services.event_consumer import _stage_detail_bauen

        self.assertEqual(_stage_detail_bauen("sachlage_node", {}), "—")

    def test_der_endpoint_liefert_sachlage_samt_alter(self) -> None:
        """GET /drive/sachlage — der Leseweg des Kontext-Panels."""
        import json as json_mod
        import time as time_mod

        from api import drive

        roh: dict = {
            "json": json_mod.dumps(VOLLSTAENDIG),
            "turn_zeit": str(time_mod.time() - 30),
        }
        with patch.object(drive.redis_client, "hgetall", return_value=roh):
            antwort: dict = drive.sachlage_lesen("u", "c")

        self.assertEqual(antwort["gegenstand"], VOLLSTAENDIG["gegenstand"])
        self.assertGreaterEqual(antwort["alter_sekunden"], 29.0)

    def test_der_verfasser_baut_den_block_ein(self) -> None:
        """Rot, sobald der Verfasser die Sachlage wieder verliert."""
        import inspect

        from graph.nodes import verfasser
        quelle: str = inspect.getsource(verfasser._build_system_prompt)

        self.assertIn("sachlage_block", quelle)
