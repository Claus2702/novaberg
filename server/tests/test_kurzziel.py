"""Zeugen fuer das kurzfristige Ziel — Scheibe 2 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 2. Aus zwei
Lagen derselben Blase mit demselben Vorhaben entsteht ein
`ziel_typ='kurzfristig'` in der bestehenden `ziele`-Tabelle; es verfaellt in
Stunden statt Tagen und laeuft ohne weiteren Bau durch die Gravitation in
den `[GEDANKEN]`-Block.

**Dasselbe Vorhaben ist dasselbe akute Objekt**, nicht derselbe
Nutzerziel-Satz — gemessen am 28.08.2026 (Kosinus der Saetze 0,40 bis 0,42
beim selben Vorhaben gegen 0,35 beim Wechsel; das Objekt traegt woertlich
durch).

Die drei Zusicherungen des Konzepts, je ein Zeuge oder mehrere:
  * **Entstehung** — zweimal dasselbe akute Objekt → genau ein Eintrag, und
    beim dritten Mal kein zweiter; zwei Objekte, zwei Ziele.
  * **Nicht-Entstehung** — einmal → kein Eintrag; ein latentes Objekt zaehlt
    nicht; faellt ein Objekt aus der Blase, beginnt es neu; eine frisch
    begonnene Blase (frisch, verfallen_neu) beginnt bei eins, auch wenn
    Redis noch einen Stand traegt.
  * **Verfall** — die Halbwertszeit ist ein Bruchteil eines Tages; der
    Decay-Agent faehrt beide Typen, und der Lauf gegen echte Zeilen halbiert
    ein drei Stunden altes Ziel bei drei Stunden Halbwertszeit.

Dazu die Verdrahtung: Der rechnende Weg des Sachlage-Knotens ruft die
Verfolgung, der Impuls-Weg nicht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import psycopg2

from config import POSTGRES_URL
from memory.kurzziel import (
    build_short_goal_sentence,
    normalize_object_name,
    short_goal_track,
)
from memory.ziele import motivation_berechnen, ziel_decay_lauf

RETTICH: dict = {"name": "Rettich bewässern", "klasse": "vorgang", "akut": True,
                 "gedeckt": {"problemstellung": "Wurzeln platzen"}, "offen": ["Intervall"]}
RASEN:   dict = {"name": "Rasen", "klasse": "objekt", "akut": False, "gedeckt": {}, "offen": []}
FLUT:    dict = {"name": "Flutberge", "klasse": "anliegen", "akut": True, "gedeckt": {}, "offen": ["Ursache"]}

SACHLAGE: dict = {
    "thema":          "Rettich-Bewaesserung",
    "gegenstand":     "Die Bewertung von Bewaesserungsmethoden fuer Rettich.",
    "nutzerziel":     "Der Nutzer will die schonendere Methode kennen.",
    "ausdrucksweise": "pruefend",
    "objekte":        [RETTICH],
}

TEST_USER:      str = "test_kurzziel"
TEST_CHARACTER: str = "test_kurzziel_gegenueber"


def _redis(strecken: dict | None = None, ziele: dict | None = None) -> MagicMock:
    """Ein Redis, das einen Stand traegt und den geschriebenen festhaelt."""
    rc = MagicMock()
    rc.hgetall.return_value = {
        "strecken": json.dumps(strecken or {}), "ziele": json.dumps(ziele or {}),
    } if strecken is not None else {}
    return rc


def _geschrieben(rc: MagicMock) -> tuple[dict, dict]:
    mapping = rc.hset.call_args.kwargs["mapping"]
    return json.loads(mapping["strecken"]), json.loads(mapping["ziele"])


class DieFormelnTest(unittest.TestCase):
    """Schluessel und Zielsatz sind benannte Funktionen."""

    def test_der_schluessel_ist_unempfindlich_gegen_schreibweise(self) -> None:
        self.assertEqual(normalize_object_name("  Rettich   Bewässern "), "rettich bewässern")

    def test_der_zielsatz_spricht_aus_novas_sicht_und_nennt_das_vorhaben(self) -> None:
        satz: str = build_short_goal_sentence("Rettich bewässern", SACHLAGE["nutzerziel"])

        self.assertTrue(satz.startswith("Ich möchte"))
        self.assertIn("Rettich bewässern", satz)
        self.assertIn(SACHLAGE["nutzerziel"], satz)

    def test_ohne_nutzerziel_steht_das_vorhaben_allein(self) -> None:
        self.assertTrue(build_short_goal_sentence("x", "").endswith("x"))

    def test_leeres_vorhaben_ist_laut(self) -> None:
        with self.assertRaises(ValueError):
            build_short_goal_sentence(" ", "y")


class DieEntstehungTest(unittest.TestCase):
    """Zwei Lagen, ein Ziel — nicht eine, nicht drei."""

    def setUp(self) -> None:
        self._embed = patch("memory.kurzziel._embed", return_value=[1.0, 0.0])
        self._embed.start()
        self.addCleanup(self._embed.stop)
        self._speichern = patch("memory.kurzziel.ziel_speichern", return_value=4711)
        self.speichern = self._speichern.start()
        self.addCleanup(self._speichern.stop)

    def test_die_erste_lage_erzeugt_kein_ziel(self) -> None:
        rc = _redis()

        ergebnis = short_goal_track(rc, "meister", "nova", SACHLAGE, "fortgeschrieben")

        self.assertEqual(ergebnis["strecken"], {"Rettich bewässern": 1})
        self.assertEqual(ergebnis["neu"], [])
        self.speichern.assert_not_called()
        self.assertEqual(_geschrieben(rc)[0], {"rettich bewässern": 1})

    def test_die_zweite_lage_mit_demselben_objekt_erzeugt_genau_eines(self) -> None:
        rc = _redis({"rettich bewässern": 1})

        ergebnis = short_goal_track(rc, "meister", "nova", SACHLAGE, "fortgeschrieben")

        self.assertEqual(ergebnis["neu"], [4711])
        self.assertEqual(ergebnis["strecken"], {"Rettich bewässern": 2})
        self.speichern.assert_called_once()
        kw = self.speichern.call_args.kwargs
        self.assertEqual(kw["ziel_typ"], "kurzfristig")
        self.assertEqual((kw["user_id"], kw["character_id"]), ("nova", "meister"))
        self.assertEqual(kw["thema"], SACHLAGE["thema"])
        self.assertIn("Rettich bewässern", kw["zielsatz"])
        self.assertEqual(kw["embedding"], [1.0, 0.0])
        self.assertEqual(_geschrieben(rc)[1], {"rettich bewässern": "4711"})

    def test_die_dritte_lage_erzeugt_kein_zweites(self) -> None:
        rc = _redis({"rettich bewässern": 2}, {"rettich bewässern": "4711"})

        ergebnis = short_goal_track(rc, "meister", "nova", SACHLAGE, "fortgeschrieben")

        self.assertEqual(ergebnis["strecken"], {"Rettich bewässern": 3})
        self.assertEqual(ergebnis["ziele"], {"Rettich bewässern": 4711})
        self.assertEqual(ergebnis["neu"], [])
        self.speichern.assert_not_called()

    def test_zwei_akute_objekte_ergeben_zwei_ziele(self) -> None:
        self.speichern.side_effect = [1, 2]
        rc = _redis({"rettich bewässern": 1, "flutberge": 1})

        ergebnis = short_goal_track(
            rc, "meister", "nova", {**SACHLAGE, "objekte": [RETTICH, FLUT]}, "fortgeschrieben",
        )

        self.assertEqual(sorted(ergebnis["neu"]), [1, 2])
        self.assertEqual(self.speichern.call_count, 2)

    def test_ein_latentes_objekt_zaehlt_nicht(self) -> None:
        rc = _redis({"rasen": 1})

        ergebnis = short_goal_track(
            rc, "meister", "nova", {**SACHLAGE, "objekte": [RASEN]}, "fortgeschrieben",
        )

        self.assertEqual(ergebnis["strecken"], {})
        self.speichern.assert_not_called()
        self.assertEqual(_geschrieben(rc)[0], {})

    def test_ein_objekt_das_die_blase_verlaesst_faellt_aus_der_strecke(self) -> None:
        rc = _redis({"rettich bewässern": 2}, {"rettich bewässern": "4711"})

        ergebnis = short_goal_track(
            rc, "meister", "nova", {**SACHLAGE, "objekte": [FLUT]}, "fortgeschrieben",
        )

        self.assertEqual(ergebnis["strecken"], {"Flutberge": 1})
        strecken, ziele = _geschrieben(rc)
        self.assertNotIn("rettich bewässern", strecken)
        self.assertNotIn("rettich bewässern", ziele)
        self.speichern.assert_not_called()

    def test_eine_frische_blase_beginnt_bei_eins(self) -> None:
        """Redis traegt noch den Stand der alten Blase — die Herkunft entscheidet."""
        for herkunft in ("frisch", "verfallen_neu"):
            with self.subTest(herkunft=herkunft):
                rc = _redis({"rettich bewässern": 3}, {"rettich bewässern": "4711"})

                ergebnis = short_goal_track(rc, "meister", "nova", SACHLAGE, herkunft)

                self.assertEqual(ergebnis["strecken"], {"Rettich bewässern": 1})
                self.assertEqual(_geschrieben(rc)[1], {})
        self.speichern.assert_not_called()

    def test_ein_gescheiterter_schreiber_hinterlaesst_keine_id(self) -> None:
        self.speichern.return_value = None
        rc = _redis({"rettich bewässern": 1})

        ergebnis = short_goal_track(rc, "meister", "nova", SACHLAGE, "fortgeschrieben")

        self.assertEqual(ergebnis["neu"], [])
        self.assertEqual(_geschrieben(rc)[1], {})

    def test_ein_ausfall_des_embed_workers_kostet_den_vektor_nicht_das_ziel(self) -> None:
        self._embed.stop()
        with patch("memory.kurzziel._embed", side_effect=RuntimeError("Worker aus")):
            rc = _redis({"rettich bewässern": 1})
            short_goal_track(rc, "meister", "nova", SACHLAGE, "fortgeschrieben")
        self._embed.start()

        self.speichern.assert_called_once()
        self.assertIsNone(self.speichern.call_args.kwargs["embedding"])


class DerVerfallInStundenTest(unittest.TestCase):
    """Die Halbwertszeit ist ein Bruchteil eines Tages — Literale, nicht Konstanten."""

    def test_nach_drei_stunden_bleibt_die_haelfte(self) -> None:
        jetzt = datetime(2026, 8, 28, 18, 0, tzinfo=timezone.utc)

        wert = motivation_berechnen(
            0.8, jetzt - timedelta(hours=3), jetzt=jetzt, halbwertszeit_tage=0.125,
        )

        self.assertAlmostEqual(wert, 0.4, places=4)

    def test_der_agent_faehrt_beide_typen(self) -> None:
        from agents.ziel_decay import agent as decay

        with patch.object(decay, "ZIEL_DECAY_AKTIV", True), \
             patch.object(decay, "ziel_decay_lauf", return_value={
                 "verarbeitet": 1, "deaktiviert": 0, "ohne_anker": 0, "error": None,
             }) as lauf:
            instanz = decay.ZielDecayAgent()
            instanz._audit_log = MagicMock()
            instanz._log_forensik = MagicMock()
            state: dict = instanz.invoke({"parameter": {}, "schritte": []})

        typen = sorted(ruf.kwargs["ziel_typ"] for ruf in lauf.call_args_list)
        self.assertEqual(typen, ["kurzfristig", "mittelfristig"])
        kurz = next(r for r in lauf.call_args_list if r.kwargs["ziel_typ"] == "kurzfristig")
        self.assertLess(kurz.kwargs["halbwertszeit_tage"], 1.0)
        self.assertEqual(state["ergebnis"]["verarbeitet"], 2)


class DerLaufGegenEchteZeilenTest(unittest.TestCase):
    """Fixture mit eigenem Paar, Lauf darauf begrenzt, tearDown raeumt ab."""

    def setUp(self) -> None:
        self.conn = psycopg2.connect(POSTGRES_URL)
        self._aufraeumen()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ziele (user_id, character_id, ziel_typ, zielsatz,
                                   motivation, motivation_basis, motivation_basis_am)
                VALUES (%s, %s, 'kurzfristig', 'Testziel kurz', 0.8, 0.8,
                        NOW() - INTERVAL '3 hours'),
                       (%s, %s, 'kurzfristig', 'Testziel kurz alt', 0.8, 0.8,
                        NOW() - INTERVAL '12 hours')
                """,
                (TEST_USER, TEST_CHARACTER, TEST_USER, TEST_CHARACTER),
            )
        self.conn.commit()

    def tearDown(self) -> None:
        self._aufraeumen()
        self.conn.close()

    def _aufraeumen(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM ziele WHERE user_id = %s", (TEST_USER,))
        self.conn.commit()

    def test_drei_stunden_halbieren_und_zwoelf_deaktivieren(self) -> None:
        ergebnis = ziel_decay_lauf(
            POSTGRES_URL, ziel_typ="kurzfristig", deaktivierungs_schwelle=0.15,
            halbwertszeit_tage=0.125, user_id=TEST_USER,
        )

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT zielsatz, motivation, aktiv FROM ziele WHERE user_id = %s",
                (TEST_USER,),
            )
            stand = {satz: (wert, aktiv) for satz, wert, aktiv in cur.fetchall()}
        self.assertEqual(ergebnis["verarbeitet"], 2)
        self.assertAlmostEqual(stand["Testziel kurz"][0], 0.4, places=2)
        self.assertTrue(stand["Testziel kurz"][1])
        self.assertFalse(stand["Testziel kurz alt"][1])


class DieVerdrahtungTest(unittest.TestCase):
    """Der rechnende Weg verfolgt, der Impuls-Weg nicht."""

    def _state(self, **felder: object) -> dict:
        basis: dict = {
            "user_id": "meister", "character_id": "nova", "turn_id": "t",
            "user_prompt": "Wie waessert man Rettich?", "session_turns": [],
            "event_payload": {}, "event_source": "user",
        }
        basis.update(felder)
        return basis

    def test_der_rechnende_weg_ruft_die_verfolgung(self) -> None:
        from graph.nodes.sachlage import sachlage_assess

        with patch("graph.nodes.sachlage.sachlage_load", return_value=(None, False)), \
             patch("graph.nodes.sachlage._derive", return_value=dict(SACHLAGE)), \
             patch("graph.nodes.sachlage._sachlage_store"), \
             patch("graph.nodes.sachlage._persist_history"), \
             patch("graph.nodes.sachlage.log_berechnung"), \
             patch("graph.nodes.sachlage.short_goal_track",
                   return_value={"strecken": {}, "neu": [], "ziele": {}}) as track:
            sachlage_assess(self._state())

        track.assert_called_once()
        self.assertEqual(track.call_args.args[4], "frisch")

    def test_der_impuls_weg_verfolgt_nicht(self) -> None:
        from graph.nodes.sachlage import sachlage_assess

        with patch("graph.nodes.sachlage.sachlage_load", return_value=(dict(SACHLAGE), False)), \
             patch("graph.nodes.sachlage.log_berechnung"), \
             patch("graph.nodes.sachlage.sachlage_bridge_build", return_value={}), \
             patch("graph.nodes.sachlage.short_goal_track") as track:
            sachlage_assess(self._state(
                event_source="character",
                event_payload={"reiz_herkunft": "eigener_impuls", "eigener_gedanke": "x"},
            ))

        track.assert_not_called()


if __name__ == "__main__":
    unittest.main()


class DieGravitationTraegtDasKurzeZielTest(unittest.TestCase):
    """`[gemessen]` 28.08.2026: Der Zielsatz liegt zur Nutzeraeusserung bei
    Kosinus 0,13 bis 0,41 — die Schwelle 0,40 haette das Ziel nie in den
    [GEDANKEN]-Block gelassen. Ein kurzfristiges Ziel ist per Bauart
    aktiviert, solange es lebt; sein Tor ist der Verfall.
    """

    def _ziele(self) -> list[dict]:
        return [
            {"id": 1, "ziel_typ": "kurzfristig", "zielsatz": "kurz", "motivation": 0.7,
             "emotion": "", "arousal": 0.5, "embedding": [0.0, 1.0]},
            {"id": 2, "ziel_typ": "mittelfristig", "zielsatz": "mittel", "motivation": 0.7,
             "emotion": "", "arousal": 0.5, "embedding": [0.0, 1.0]},
            {"id": 3, "ziel_typ": "langfristig", "zielsatz": "lang", "motivation": 0.9,
             "emotion": "", "arousal": 0.5, "embedding": [1.0, 0.0]},
        ]

    def test_das_kurze_ziel_ist_aktiviert_obwohl_die_staerke_unter_der_schwelle_liegt(self) -> None:
        from ei.gravitation import ziel_gravitation_berechnen

        aktiviert = ziel_gravitation_berechnen([1.0, 0.0], self._ziele())

        typen = [g.ziel_typ for g in aktiviert]
        self.assertIn("kurzfristig", typen)
        self.assertNotIn("mittelfristig", typen)
        kurz = next(g for g in aktiviert if g.ziel_typ == "kurzfristig")
        self.assertAlmostEqual(kurz.similarity, 0.0)
        self.assertAlmostEqual(kurz.aktivierungs_staerke, 0.0)

    def test_das_kurze_ziel_steht_vorn(self) -> None:
        """Der GV nimmt drei — das Ziel aus dem Gespraech darf nicht hinter
        staerkeren Charakterzielen verschwinden.
        """
        from ei.gravitation import ziel_gravitation_berechnen

        aktiviert = ziel_gravitation_berechnen([1.0, 0.0], self._ziele())

        self.assertEqual(aktiviert[0].ziel_typ, "kurzfristig")
        self.assertEqual(aktiviert[1].ziel_typ, "langfristig")

    def test_ohne_vektor_bleibt_auch_das_kurze_ziel_draussen(self) -> None:
        from ei.gravitation import ziel_gravitation_berechnen

        ziele = self._ziele()
        ziele[0]["embedding"] = None

        self.assertEqual([g.ziel_typ for g in ziel_gravitation_berechnen([1.0, 0.0], ziele)], ["langfristig"])
