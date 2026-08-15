"""Tests: Der Level, den ein Gedanke mittraegt — Bauteil B.

Ein Gedanke wird in einem Zustand gefasst und bringt ihn mit, wenn er
auftaucht. Der Kanal dafuer war seit dem 15.08.2026 vorne bedient
(`stack_push` nimmt `arousal`) und hinten tot: Die Zustellung reichte den Wert
nicht ins Ereignis, und der Zugriffsknoten verwarf den mitgereichten Zustand
auf dem Impuls-Pfad ohnehin.

Drei Zusicherungen, und die zweite ist die scharfe:

  * **Der hinterlegte Level hebt** einen niedrigeren Zustand.
  * **Er setzt nicht.** Ein Einwurf kann mitten in ein Gespraech fallen; ein
    Setzen zoege beide heraus, wenn der hinterlegte Wert der niedrigere ist.
    Also gilt der hoehere von beiden.
  * **Ein leerer Level aendert nichts.** Auf dem Stapel liegen Eintraege, die
    nie einen bekommen werden — ein leeres Feld darf kein Wert werden, kein
    Vorgabewert und keine Null.

Dazu die **Naht**: Der Wert muss den Weg von der Zustellung in den
Zugriffsknoten nehmen. Am 15.08.2026 kostete genau diese Klasse einen halben
Tag — ein Router kannte einen neu eingefuehrten Wert nicht, und kein einziger
Auftrag lief mehr, bei 1404 gruenen Tests. Ein Zeuge auf die Funktion prueft
nicht die Verdrahtung.

Konzept: novaberg-eigenzeit_k.md §2.3, §5.2.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from graph.nodes import db_zugriff as db_zugriff_modul
from graph.nodes import thinker as thinker_modul
from graph.nodes.db_zugriff import Protokollkopf, _level_anheben
from graph.personality import Emotion
from graph.reiz import LEVEL_FELD, reiz_level
from services import shadow_delivery as delivery_modul


def _kopf() -> Protokollkopf:
    """Ein Protokollkopf fuer das produktive Paar."""
    return Protokollkopf(
        turn_id      = "zeuge-level",
        quelle       = "character",
        span_id      = "",
        user_id      = "meister",
        character_id = "nova",
    )


def _zustand(arousal: float) -> Emotion:
    """Novas geladener Zustand mit einer bestimmten Erregung."""
    return Emotion(
        emotion              = "neutral",
        arousal              = arousal,
        mode                 = "alltag",
        relationship_dynamic = "vertraut",
    )


def _impuls_zustand(level: object) -> dict:
    """Ein Durchlauf-Zustand, wie ihn ein Impuls-Ereignis erzeugt."""
    return {
        "event_payload": {
            "reiz_herkunft": "eigener_impuls",
            LEVEL_FELD:      level,
        },
    }


class DerLevelHebtTest(unittest.TestCase):
    """Was `_level_anheben` mit dem geladenen Zustand macht."""

    def test_der_hinterlegte_level_hebt_einen_niedrigeren_zustand(self) -> None:
        """Der Gedanke holt sie in den Zustand zurueck, in dem er entstand."""
        ergebnis = _level_anheben(_kopf(), _zustand(0.30), 0.85, "eigener_impuls")

        self.assertAlmostEqual(0.85, ergebnis.arousal, places=4)

    def test_derselbe_level_senkt_einen_hoeheren_zustand_nicht(self) -> None:
        """Die scharfe Zusicherung: Er hebt, er setzt nicht.

        Ein Einwurf mitten in ein Gespraech darf beide nicht herausziehen.
        """
        ergebnis = _level_anheben(_kopf(), _zustand(0.92), 0.60, "eigener_impuls")

        self.assertAlmostEqual(0.92, ergebnis.arousal, places=4)

    def test_ohne_hinterlegten_level_bleibt_der_zustand_stehen(self) -> None:
        """Ein leeres Feld wird kein Wert — kein Vorgabewert, keine Null."""
        ergebnis = _level_anheben(_kopf(), _zustand(0.42), None, "eigener_impuls")

        self.assertAlmostEqual(0.42, ergebnis.arousal, places=4)

    def test_gleichstand_bleibt_gleichstand(self) -> None:
        """Der Randfall auf der Kante — kein Sprung nach oben oder unten."""
        ergebnis = _level_anheben(_kopf(), _zustand(0.70), 0.70, "eigener_impuls")

        self.assertAlmostEqual(0.70, ergebnis.arousal, places=4)

    def test_auf_einem_nutzer_turn_hebt_nichts(self) -> None:
        """Die Weiche: Ein Level gehoert zu einem Gedanken, nicht zu einer Rede."""
        ergebnis = _level_anheben(_kopf(), _zustand(0.30), 0.85, "nutzer_turn")

        self.assertAlmostEqual(0.30, ergebnis.arousal, places=4)

    def test_die_kategorien_bleiben_unberuehrt(self) -> None:
        """Gehoben wird eine Zahl. Ein Maximum auf einer Kategorie bedeutet nichts."""
        ergebnis = _level_anheben(_kopf(), _zustand(0.30), 0.85, "eigener_impuls")

        self.assertEqual("neutral",  ergebnis.emotion)
        self.assertEqual("alltag",   ergebnis.mode)
        self.assertEqual("vertraut", ergebnis.relationship_dynamic)


class DerLevelKommtAusDemEreignisTest(unittest.TestCase):
    """Was `reiz_level` aus dem Payload liest — und was es ablehnt."""

    def test_der_wert_wird_gelesen(self) -> None:
        """Der Normalfall."""
        self.assertAlmostEqual(0.75, reiz_level(_impuls_zustand(0.75)), places=4)

    def test_ein_fehlendes_feld_heisst_unbekannt(self) -> None:
        """Nicht null, nicht ein Vorgabewert — nichts."""
        zustand: dict = {"event_payload": {"reiz_herkunft": "eigener_impuls"}}

        self.assertIsNone(reiz_level(zustand))

    def test_ein_ausdrueckliches_none_heisst_unbekannt(self) -> None:
        """Der Fall des Bestands: Das Feld steht da und ist leer.

        Ein Default deckt den fehlenden Schluessel, nicht den gesetzten
        Null-Wert — beide Schreibweisen muessen auf denselben Leerfall
        abgebildet werden.
        """
        self.assertIsNone(reiz_level(_impuls_zustand(None)))

    def test_ein_nutzer_turn_bringt_keinen_level_mit(self) -> None:
        """Niemand hat einen Gedanken gefasst — es gibt keinen Stand."""
        zustand: dict = {"event_payload": {LEVEL_FELD: 0.9}}

        self.assertIsNone(reiz_level(zustand))

    def test_ein_unlesbarer_wert_meldet_sich_und_hebt_nicht(self) -> None:
        """Kaputt ist nicht dasselbe wie leer — und es wird laut."""
        with self.assertLogs("ki_server.graph.reiz", level="ERROR") as protokoll:
            ergebnis = reiz_level(_impuls_zustand("ziemlich aufgedreht"))

        self.assertIsNone(ergebnis)
        self.assertIn(LEVEL_FELD, "\n".join(protokoll.output))

    def test_ein_wert_ausserhalb_der_spanne_wird_verworfen_nicht_gekappt(self) -> None:
        """Eine stille Kappung machte aus einem Rechenfehler ein plausibles Ergebnis."""
        with self.assertLogs("ki_server.graph.reiz", level="ERROR") as protokoll:
            ergebnis = reiz_level(_impuls_zustand(1.4))

        self.assertIsNone(ergebnis)
        self.assertIn("1.4", "\n".join(protokoll.output))

    def test_ein_wahrheitswert_ist_keine_erregung(self) -> None:
        """`True` ist in Python eine 1 — und hier trotzdem kein Messwert."""
        with self.assertLogs("ki_server.graph.reiz", level="ERROR"):
            self.assertIsNone(reiz_level(_impuls_zustand(True)))


class DieNahtTest(unittest.TestCase):
    """Beide Enden an einem Zeugen: Was die Zustellung schreibt, liest der Knoten.

    Dieser Zeuge existiert wegen des 15.08.2026: Ein neu eingefuehrter Wert
    hatte einen Schreiber und einen Leser, die einander nicht kannten. Wer
    einen Wert einfuehrt, muss seine Leser suchen — und ein Zeuge auf die
    Funktion prueft nicht die Verdrahtung.
    """

    def _payload_der_zustellung(self, eintrag: dict) -> dict:
        """Faehrt die Zustellung und gibt das Payload zurueck, das sie baut."""
        erzeuger = MagicMock(return_value="event-1")

        with patch.object(delivery_modul, "event_erzeugen", erzeuger):
            erfolg: bool = delivery_modul._impuls_in_den_charaktergraph(
                MagicMock(), "meister", "turn-1", "ein Gedanke", eintrag,
            )

        self.assertTrue(erfolg)
        return erzeuger.call_args.kwargs["payload"]

    def test_die_zustellung_reicht_den_level_ins_ereignis(self) -> None:
        """Der Wert des Stapel-Eintrags steht im Payload."""
        payload: dict = self._payload_der_zustellung(
            {"thema": "Enceladus", "aufgabe": "nachfragen", "arousal": 0.8},
        )

        self.assertAlmostEqual(0.8, payload[LEVEL_FELD], places=4)

    def test_ein_eintrag_ohne_level_traegt_das_feld_trotzdem(self) -> None:
        """Das Feld steht auch dann im Payload, wenn es leer ist.

        Ein weggelassenes Feld waere von einem Eintrag alter Bauart nicht zu
        unterscheiden.
        """
        payload: dict = self._payload_der_zustellung(
            {"thema": "Enceladus", "aufgabe": "recherche"},
        )

        self.assertIn(LEVEL_FELD, payload)
        self.assertIsNone(payload[LEVEL_FELD])

    def test_der_knoten_liest_genau_das_geschriebene_feld(self) -> None:
        """Die Naht selbst: Payload der Zustellung, Leser des Knotens."""
        payload: dict = self._payload_der_zustellung(
            {"thema": "Enceladus", "aufgabe": "nachfragen", "arousal": 0.8},
        )

        self.assertAlmostEqual(0.8, reiz_level({"event_payload": payload}), places=4)


class DerZweiteErzeugerTest(unittest.TestCase):
    """Der Wiederholungsversuch baut das Payload neu — und muss den Stand mitnehmen.

    Gefunden bei der Nachprüfung, nicht beim Bau, und genau in der Klasse, die
    diesen Umbau schon einmal getroffen hat: **Ein neu eingefuehrter Wert hat
    mehr als einen Erzeuger.** Die Zustellung war bedient, der Thinker-Retry
    nicht — er setzt `reiz_herkunft` auf `eigener_impuls` und baut die uebrigen
    Reiz-Felder von Hand nach.

    **Der Ausfall waere still gewesen.** Der Zugriffsknoten meldet dann
    ordnungsgemaess `kein_level`; die Meldung ist richtig, ihre Ursache ist es
    nicht — und von einem Eintrag ohne Stand ist der Fall nicht zu
    unterscheiden.
    """

    def test_der_retry_eines_impulses_traegt_den_stand_mit(self) -> None:
        """Was ankam, reist weiter."""
        nutzlast: dict = thinker_modul._retry_nutzlast({
            "eigener_gedanke": "ein Gedanke",
            "turn_id":         "t-1",
            "event_payload":   {
                "reiz_herkunft": "eigener_impuls",
                LEVEL_FELD:      0.77,
            },
        })

        self.assertAlmostEqual(0.77, nutzlast[LEVEL_FELD], places=4)

    def test_der_folgelauf_liest_denselben_wert(self) -> None:
        """Die Naht: Payload des Retrys, Leser des Knotens."""
        nutzlast: dict = thinker_modul._retry_nutzlast({
            "eigener_gedanke": "ein Gedanke",
            "turn_id":         "t-1",
            "event_payload":   {
                "reiz_herkunft": "eigener_impuls",
                LEVEL_FELD:      0.77,
            },
        })

        self.assertAlmostEqual(
            0.77, reiz_level({"event_payload": nutzlast}), places=4,
        )

    def test_ein_impuls_ohne_stand_traegt_das_feld_leer_weiter(self) -> None:
        """Kein Wert wird erfunden, nur weil das Feld Pflicht ist."""
        nutzlast: dict = thinker_modul._retry_nutzlast({
            "eigener_gedanke": "ein Gedanke",
            "turn_id":         "t-1",
            "event_payload":   {"reiz_herkunft": "eigener_impuls"},
        })

        self.assertIn(LEVEL_FELD, nutzlast)
        self.assertIsNone(nutzlast[LEVEL_FELD])

    def test_ein_nutzer_retry_bringt_keinen_stand_mit(self) -> None:
        """Auf dem Nutzer-Weg hat niemand einen Gedanken gefasst."""
        nutzlast: dict = thinker_modul._retry_nutzlast({
            "user_prompt":   "Wie entsteht ein Gammablitz?",
            "turn_id":       "t-1",
            "event_payload": {},
        })

        self.assertIsNone(nutzlast[LEVEL_FELD])


class DieVerdrahtungTest(unittest.TestCase):
    """Der Ladepfad hebt an — sonst ist der Bauteil tot und still.

    Am 15.08.2026 blieben nach dem testweisen Ausklinken eines Aufrufs alle
    1363 Tests gruen. Die Zusicherungen oben pruefen `_level_anheben` direkt
    und haetten den toten Bauteil nie bemerkt.
    """

    def _geladen(self, level: float | None, herkunft: str) -> Emotion:
        """Faehrt `_nova_zustand_laden` gegen einen Zustand mit Erregung 0,30."""
        redis_mock = MagicMock()
        redis_mock.hgetall.return_value = {
            "emotion": "neutral",
            "arousal": "0.30",
            "mode":    "alltag",
        }

        with patch.object(db_zugriff_modul, "redis_client", redis_mock):
            emotion, _raum = db_zugriff_modul._nova_zustand_laden(
                _kopf(), herkunft, level,
            )
        return emotion

    def test_der_ladepfad_wendet_das_anheben_an(self) -> None:
        """Geladen 0,30, hinterlegt 0,85 — am Ausgang steht 0,85."""
        self.assertAlmostEqual(0.85, self._geladen(0.85, "eigener_impuls").arousal, places=4)

    def test_der_ladepfad_ohne_level_laesst_den_zustand_stehen(self) -> None:
        """Der positive Zwilling: derselbe Weg, kein Wert, keine Wirkung."""
        self.assertAlmostEqual(0.30, self._geladen(None, "eigener_impuls").arousal, places=4)

    def test_der_knoten_hebt_den_zustand_eines_impulses(self) -> None:
        """Der ganze Weg: Payload → Leser → Ladepfad → `internal`.

        Ohne diese Zusicherung koennte `db_zugriff` den Leser weglassen und
        `None` durchreichen — alle Zeugen darueber blieben gruen.
        """
        state: dict = {
            "user_id":       "meister",
            "character_id":  "nova",
            "event_source":  "character",
            "turn_id":       "zeuge-level-knoten",
            "event_payload": {
                "reiz_herkunft": "eigener_impuls",
                LEVEL_FELD:      0.85,
            },
        }
        ergebnis: dict = self._knoten_fahren(state)

        self.assertAlmostEqual(0.85, ergebnis["internal"].emotion.arousal, places=4)

    def test_der_knoten_laesst_einen_nutzer_turn_in_ruhe(self) -> None:
        """Der negative Zwilling: derselbe Wert im Payload, andere Herkunft."""
        state: dict = {
            "user_id":       "meister",
            "character_id":  "nova",
            "event_source":  "user",
            "turn_id":       "zeuge-level-nutzer",
            "event_payload": {LEVEL_FELD: 0.85},
        }
        ergebnis: dict = self._knoten_fahren(state)

        self.assertAlmostEqual(0.30, ergebnis["internal"].emotion.arousal, places=4)

    def _knoten_fahren(self, state: dict) -> dict:
        """Faehrt `db_zugriff` mit gesetztem Zustand und stillgelegten Ladern.

        Die drei Postgres-Lader gehoeren nicht zu diesem Zeugen; sie sind
        ersetzt, damit der Zeuge nicht am Bestand der Datenbank haengt.
        """
        redis_mock = MagicMock()
        redis_mock.hgetall.return_value = {
            "emotion": "neutral",
            "arousal": "0.30",
            "mode":    "alltag",
        }
        from graph.personality import Character

        with (
            patch.object(db_zugriff_modul, "redis_client", redis_mock),
            patch.object(
                db_zugriff_modul, "_charaktere_laden",
                MagicMock(return_value=(Character(), Character())),
            ),
            patch.object(db_zugriff_modul, "_identities_laden", MagicMock(return_value=[])),
            patch.object(db_zugriff_modul, "_directives_laden", MagicMock(return_value=[])),
        ):
            return db_zugriff_modul.db_zugriff(state)


if __name__ == "__main__":
    unittest.main()
