"""Tests: die Eingangs-Queue schneidet zusammengehoerige Nachrichten zu einem Block.

Zwei Nachrichten gehoeren zu demselben Prompt, wenn sie hoechstens
`EINGANG_FENSTER` Sekunden auseinander eintrafen — gemessen am Abstand zum
**unmittelbaren Vorgaenger**, nicht zum Beginn des Blocks. Eine Kette kurzer
Abstaende ist ein zusammenhaengender Gedanke.

Zeugen dieser Datei:
  * Die Schwelle kommt aus der Konstante, nicht aus einer Zahl im Test
    — die Beispiele werden daraus gerechnet, damit sie einer
    spaeteren Kalibrierung folgen. Die Zusicherung ueber die *Lage* steht
    daneben.
  * Die erwarteten Blockgroessen sind von Hand abgezaehlt, nicht von der
    Funktion erzeugt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock

from services.prompt_eingang import (
    EINGANG_FENSTER,
    EingehendeNachricht,
    block_schneiden,
    block_zu_prompt,
    nachricht_einreihen,
    naechster_block,
    turn_beenden,
    turn_beginnen,
)

EINGANG_LOGGER: str = "ki_server.prompt_eingang"

# Ein Bezugsmoment ohne Bedeutung — alle Abstaende werden relativ dazu gebildet.
T0: float = 1_754_000_000.0


def _nachricht(versatz: float, text: str = "Frage?", **felder: object) -> dict:
    """Ein Eingangs-Eintrag mit Abstand `versatz` zum Bezugsmoment."""
    eintrag: dict = {
        "nachrichten_id": f"n-{versatz:g}",
        "prompt":         text,
        "empfangen_am":   T0 + versatz,
        "client_id":      "desktop",
    }
    eintrag.update(felder)
    return eintrag


class BlockSchneidenTest(unittest.TestCase):
    """Die Regel selbst, ohne Redis."""

    def test_leere_eingabe_ergibt_leeren_block(self) -> None:
        """Nichts zu schneiden ist kein Fehler."""
        self.assertEqual(block_schneiden([]), [])

    def test_eine_nachricht_ist_ein_block(self) -> None:
        """Der haeufigste Fall — und der, den ein Fenster nicht verzoegern darf."""
        block: list[dict] = block_schneiden([_nachricht(0.0)])

        self.assertEqual(len(block), 1)

    def test_knapp_innerhalb_gehoert_dazu(self) -> None:
        """Der Wert wird aus der Konstante gerechnet, nicht gesetzt."""
        knapp: float = EINGANG_FENSTER - 0.1
        self.assertLess(knapp, EINGANG_FENSTER)

        block: list[dict] = block_schneiden([_nachricht(0.0), _nachricht(knapp)])

        self.assertEqual(len(block), 2)

    def test_genau_auf_der_schwelle_gehoert_dazu(self) -> None:
        """Die Regel lautet 'hoechstens', nicht 'weniger als'."""
        block: list[dict] = block_schneiden([_nachricht(0.0), _nachricht(EINGANG_FENSTER)])

        self.assertEqual(len(block), 2)

    def test_knapp_darueber_trennt(self) -> None:
        """Die Gegenseite der Schwelle — sonst prueft der Test nur eine Richtung."""
        drueber: float = EINGANG_FENSTER + 0.1
        self.assertGreater(drueber, EINGANG_FENSTER)

        block: list[dict] = block_schneiden([_nachricht(0.0), _nachricht(drueber)])

        self.assertEqual(len(block), 1)

    def test_die_kette_zaehlt_zum_vorgaenger_nicht_zum_anfang(self) -> None:
        """Vier Nachrichten im halben Fenster sind ein Gedanke, kein Block-Ende."""
        schritt: float = EINGANG_FENSTER / 2
        nachrichten: list[dict] = [_nachricht(i * schritt) for i in range(4)]

        block: list[dict] = block_schneiden(nachrichten)

        # Erste und letzte liegen 1,5 Fenster auseinander — trotzdem ein Block.
        self.assertEqual(len(block), 4)
        self.assertGreater(
            block[-1]["empfangen_am"] - block[0]["empfangen_am"], EINGANG_FENSTER,
        )

    def test_der_rest_bleibt_liegen(self) -> None:
        """Was nach der Luecke kommt, gehoert zum naechsten Durchlauf."""
        nachrichten: list[dict] = [
            _nachricht(0.0), _nachricht(1.0),
            _nachricht(EINGANG_FENSTER * 3), _nachricht(EINGANG_FENSTER * 3 + 1),
        ]

        block: list[dict] = block_schneiden(nachrichten)

        self.assertEqual(len(block), 2)
        self.assertEqual(block, nachrichten[:2])

    def test_das_ergebnis_ist_ein_praefix_der_eingabe(self) -> None:
        """Nachbedingung: nichts wird umsortiert oder erfunden."""
        nachrichten: list[dict] = [_nachricht(0.0), _nachricht(2.0), _nachricht(999.0)]

        block: list[dict] = block_schneiden(nachrichten)

        self.assertEqual(block, nachrichten[:len(block)])


class UnbrauchbarerZeitstempelTest(unittest.TestCase):
    """Leer, fehlend und falsch getippt sind drei Faelle — und keiner ist still."""

    def test_fehlender_zeitstempel_trennt(self) -> None:
        """Ohne Bezugspunkt ist jede Zuordnung geraten."""
        ohne: dict = _nachricht(1.0)
        del ohne["empfangen_am"]

        block: list[dict] = block_schneiden([_nachricht(0.0), ohne])

        self.assertEqual(len(block), 1)

    def test_fehlender_zeitstempel_wird_gemeldet(self) -> None:
        """Ein stiller Schnitt saehe aus wie eine echte Luecke."""
        ohne: dict = _nachricht(1.0)
        del ohne["empfangen_am"]

        with self.assertLogs(EINGANG_LOGGER, level="ERROR") as protokoll:
            block_schneiden([_nachricht(0.0), ohne])

        self.assertIn("Zeitstempel", "\n".join(protokoll.output))

    def test_zeichenkette_gilt_nicht_als_zeit(self) -> None:
        """Ein Datum als Text laesst sich nicht subtrahieren."""
        falsch: dict = _nachricht(1.0, empfangen_am="2026-08-01T20:00:00")

        block: list[dict] = block_schneiden([_nachricht(0.0), falsch])

        self.assertEqual(len(block), 1)

    def test_wahrheitswert_gilt_nicht_als_zeit(self) -> None:
        """`True` ist in Python eine Ganzzahl — und hier trotzdem kein Zeitpunkt."""
        falsch: dict = _nachricht(1.0, empfangen_am=True)

        block: list[dict] = block_schneiden([_nachricht(0.0), falsch])

        self.assertEqual(len(block), 1)

    def test_erste_nachricht_ohne_zeit_wird_allein_verarbeitet(self) -> None:
        """Sie geht nicht verloren — sie nimmt nur nichts mit."""
        ohne: dict = _nachricht(0.0)
        del ohne["empfangen_am"]

        block: list[dict] = block_schneiden([ohne, _nachricht(1.0)])

        self.assertEqual(len(block), 1)
        self.assertEqual(block[0], ohne)

    def test_eine_echte_null_ist_ein_gueltiger_zeitpunkt(self) -> None:
        """Der positive Zwilling: 0.0 ist ein Wert, kein Fehlen."""
        with self.assertNoLogs(EINGANG_LOGGER, level="ERROR"):
            block: list[dict] = block_schneiden([
                {"nachrichten_id": "a", "prompt": "x", "empfangen_am": 0.0},
                {"nachrichten_id": "b", "prompt": "y", "empfangen_am": 1.0},
            ])

        self.assertEqual(len(block), 2)


class EinreihenTest(unittest.TestCase):
    """Der Anfragepfad nimmt an und rechnet nicht."""

    def test_nachricht_landet_in_der_queue(self) -> None:
        """Der Eintrag traegt Text, Kennung und Empfangszeit."""
        redis = MagicMock()
        redis.rpush.return_value = 1
        redis.ttl.return_value = -1

        kennung: str = nachricht_einreihen(redis, "meister", "nova",
                                             EingehendeNachricht("Frage?", T0, "desktop"))

        self.assertTrue(kennung)
        eintrag: dict = json.loads(redis.rpush.call_args.args[1])
        self.assertEqual(eintrag["prompt"], "Frage?")
        self.assertEqual(eintrag["empfangen_am"], T0)
        self.assertEqual(eintrag["nachrichten_id"], kennung)

    def test_leerer_prompt_wird_abgelehnt(self) -> None:
        """Eine leere Aeusserung hat nichts, was beantwortet werden koennte."""
        redis = MagicMock()

        with self.assertLogs(EINGANG_LOGGER, level="ERROR"):
            kennung: str = nachricht_einreihen(redis, "meister", "nova",
                                             EingehendeNachricht("   ", T0))

        self.assertEqual(kennung, "")
        redis.rpush.assert_not_called()

    def test_ttl_wird_nur_einmal_gesetzt(self) -> None:
        """Ein neuer Eintrag darf die Frist der Queue nicht verlaengern."""
        redis = MagicMock()
        redis.rpush.return_value = 2
        redis.ttl.return_value = 900

        nachricht_einreihen(redis, "meister", "nova", EingehendeNachricht("Frage?", T0))

        redis.expire.assert_not_called()


class NaechsterBlockTest(unittest.TestCase):
    """Lesen ohne zu entnehmen, entnehmen erst nach dem Schnitt."""

    def _redis_mit(self, nachrichten: list[dict]) -> MagicMock:
        """Redis-Attrappe, deren Queue die uebergebenen Eintraege enthaelt."""
        redis = MagicMock()
        redis.lrange.return_value = [
            json.dumps(n, ensure_ascii=False) for n in nachrichten
        ]
        return redis

    def test_leere_queue_ergibt_leeren_block(self) -> None:
        """Kein Eintrag, kein Entnehmen."""
        redis = MagicMock()
        redis.lrange.return_value = []

        self.assertEqual(naechster_block(redis, "meister", "nova"), [])
        redis.lpop.assert_not_called()

    def test_es_wird_genau_der_block_entnommen(self) -> None:
        """Zwei von vier — der Rest bleibt fuer den naechsten Durchlauf."""
        redis = self._redis_mit([
            _nachricht(0.0), _nachricht(1.0),
            _nachricht(EINGANG_FENSTER * 4), _nachricht(EINGANG_FENSTER * 4 + 1),
        ])

        block: list[dict] = naechster_block(redis, "meister", "nova")

        self.assertEqual(len(block), 2)
        self.assertEqual(redis.lpop.call_count, 2)

    def test_gelesen_wird_vor_dem_entnehmen(self) -> None:
        """Ein `lpop` vor dem Schnitt haette ein Fenster, in dem nichts existiert."""
        redis = self._redis_mit([_nachricht(0.0)])

        naechster_block(redis, "meister", "nova")

        redis.lrange.assert_called_once()

    def test_unlesbarer_eintrag_wird_gemeldet_und_entfernt(self) -> None:
        """Er blockiert die Queue nicht, und er wird nicht verschwiegen."""
        redis = MagicMock()
        redis.lrange.return_value = ["{kein json", json.dumps(_nachricht(1.0))]

        with self.assertLogs(EINGANG_LOGGER, level="ERROR"):
            block: list[dict] = naechster_block(redis, "meister", "nova")

        self.assertEqual(block, [])
        self.assertEqual(redis.lpop.call_count, 1)


class BlockZuPromptTest(unittest.TestCase):
    """Aus mehreren Aeusserungen wird ein Text."""

    def test_texte_werden_in_reihenfolge_verkettet(self) -> None:
        """Von Hand gebildeter Zeuge."""
        block: list[dict] = [_nachricht(0.0, "Hallo"), _nachricht(1.0, "Was machst Du?")]

        self.assertEqual(block_zu_prompt(block), "Hallo\nWas machst Du?")

    def test_leerer_block_ergibt_leeren_text(self) -> None:
        """Kein erfundener Inhalt, wo keiner war."""
        self.assertEqual(block_zu_prompt([]), "")

    def test_eine_nachricht_bleibt_unveraendert(self) -> None:
        """Der haeufigste Fall darf keine Trennzeichen bekommen."""
        self.assertEqual(block_zu_prompt([_nachricht(0.0, "Nur eine Frage?")]),
                         "Nur eine Frage?")


if __name__ == "__main__":
    unittest.main()


class QueueWaechterTest(unittest.IsolatedAsyncioTestCase):
    """Eingespeist wird erst, wenn der ganze Turn durch ist.

    Der Waechter ist die Verdrahtung, nicht der Baustein — und genau dort sass
    der Defekt: Der `llm_lock` wird zwischen Pfad 1 und CharacterGraph kurz
    frei, ein zweiter Block geriet in diesen Spalt, und sein Modellaufruf lief
    am 01.08.2026 in einen Timeout. Der Marker umspannt beide Haelften.
    """

    def _umgebung(self) -> tuple:
        """Redis mit einer wartenden Queue und ein Loop, der eine Runde dreht."""
        redis = MagicMock()
        redis.keys.return_value = ["prompt_queue:meister:nova"]

        halt = MagicMock()
        halt.is_set.side_effect = [False, True]

        return redis, halt

    async def _eine_runde(self, turn_frei: bool) -> tuple:
        """Laesst den Loop eine Runde drehen; gibt Nehmer und Beender zurueck."""
        from unittest.mock import patch

        import services.prompt_consumer as modul

        redis, halt = self._umgebung()

        with patch.object(modul, "redis_client", redis), \
             patch.object(modul, "shutdown_event", halt), \
             patch.object(modul, "POLL_INTERVAL", 0.0), \
             patch.object(modul, "turn_beginnen", return_value=turn_frei) as beginn, \
             patch.object(modul, "event_wartet", return_value=False), \
             patch.object(modul, "turn_beenden") as ende, \
             patch.object(modul, "naechster_block", return_value=[]) as nehmer:
            await modul.prompt_consumer_loop(MagicMock(), MagicMock())

        return nehmer, ende, beginn

    async def test_laufender_turn_nimmt_nichts(self) -> None:
        """Die Aeusserungen bleiben liegen, bis der CharacterGraph durch ist."""
        nehmer, _, _ = await self._eine_runde(turn_frei=False)

        nehmer.assert_not_called()

    async def test_freier_turn_nimmt(self) -> None:
        """Der positive Zwilling — sonst bestuende der Test auch bei totem Loop."""
        nehmer, _, _ = await self._eine_runde(turn_frei=True)

        nehmer.assert_called_once()

    async def test_leerer_takt_gibt_den_marker_zurueck(self) -> None:
        """Ein Takt ohne Block darf die naechste Aeusserung nicht sperren."""
        _, ende, _ = await self._eine_runde(turn_frei=True)

        ende.assert_called_once()

    async def test_der_marker_traegt_die_turn_kennung(self) -> None:
        """Ohne sie ist im Log nicht zuzuordnen, welcher Turn gerade laeuft."""
        _, _, beginn = await self._eine_runde(turn_frei=True)

        self.assertTrue(beginn.call_args.args[3], "keine turn_id im Marker")


class TurnMarkerTest(unittest.TestCase):
    """Setzen und Loesen — atomar und idempotent."""

    def test_marker_wird_atomar_gesetzt(self) -> None:
        """`NX` macht Pruefen und Setzen zu einer Operation."""
        redis = MagicMock()
        redis.set.return_value = True

        self.assertTrue(turn_beginnen(redis, "meister", "nova", "t-1"))
        self.assertTrue(redis.set.call_args.kwargs["nx"])
        self.assertGreater(redis.set.call_args.kwargs["ex"], 0)

    def test_belegter_marker_meldet_falsch(self) -> None:
        """Der zweite Aufrufer erfaehrt, dass schon einer laeuft."""
        redis = MagicMock()
        redis.set.return_value = None

        self.assertFalse(turn_beginnen(redis, "meister", "nova", "t-2"))

    def test_ohne_turn_id_kein_marker(self) -> None:
        """Ein Marker ohne Kennung waere im Log nicht zuzuordnen."""
        redis = MagicMock()

        with self.assertLogs(EINGANG_LOGGER, level="ERROR"):
            self.assertFalse(turn_beginnen(redis, "meister", "nova", ""))

        redis.set.assert_not_called()

    def test_beenden_ist_idempotent(self) -> None:
        """Nicht jeder Durchlauf hat einen Marker gesetzt bekommen."""
        redis = MagicMock()
        redis.delete.return_value = 0

        turn_beenden(redis, "meister", "nova")

        redis.delete.assert_called_once()


class PixieUndWaechterTest(unittest.IsolatedAsyncioTestCase):
    """Ein eigener Impuls ist auch ein Turn — und er wartet auf seinen Durchlauf.

    Der Marker allein reicht nicht: Ein Impuls loescht ihn am Ende seines
    eigenen Durchlaufs, auch wenn das Nutzer-Ereignis dahinter noch in der
    Ereignis-Queue liegt. Dann steht der Marker frei und ein unfertiger Turn
    trotzdem aus.
    """

    def _consumer(self) -> object:
        """Das Consumer-Modul, dessen Waechter geprueft wird."""
        import services.prompt_consumer as modul
        return modul

    async def test_wartendes_ereignis_verhindert_das_nehmen(self) -> None:
        """Der zweite Riegel: nicht 'laeuft gerade', sondern 'kommt noch'."""
        from unittest.mock import patch

        modul = self._consumer()

        with patch.object(modul, "turn_beginnen", return_value=True), \
             patch.object(modul, "event_wartet", return_value=True), \
             patch.object(modul, "turn_beenden") as ende:
            erlaubt: bool = modul._darf_nehmen("meister", "nova", "t-1")

        self.assertFalse(erlaubt)
        ende.assert_called_once()

    async def test_freie_bahn_erlaubt_das_nehmen(self) -> None:
        """Der positive Zwilling — beide Bedingungen frei."""
        from unittest.mock import patch

        modul = self._consumer()

        with patch.object(modul, "turn_beginnen", return_value=True), \
             patch.object(modul, "event_wartet", return_value=False), \
             patch.object(modul, "turn_beenden") as ende:
            erlaubt: bool = modul._darf_nehmen("meister", "nova", "t-1")

        self.assertTrue(erlaubt)
        ende.assert_not_called()

    async def test_der_marker_wird_bei_abbruch_zurueckgegeben(self) -> None:
        """Ein gesetzter und nicht genutzter Marker sperrte bis zum Verfall."""
        from unittest.mock import patch

        modul = self._consumer()

        with patch.object(modul, "turn_beginnen", return_value=True), \
             patch.object(modul, "event_wartet", return_value=True), \
             patch.object(modul, "turn_beenden") as ende:
            modul._darf_nehmen("meister", "nova", "t-1")

        ende.assert_called_once_with(modul.redis_client, "meister", "nova")

    async def test_ein_impuls_setzt_den_marker_ebenfalls(self) -> None:
        """Sonst bliebe die Eingabe waehrend seines Durchlaufs offen."""
        import ast
        import inspect

        import services.event_consumer as ec

        quelle: str = inspect.getsource(ec)
        baum: ast.Module = ast.parse(quelle)

        rufe: set[str] = {
            k.func.id
            for k in ast.walk(baum)
            if isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
        }

        self.assertIn("turn_beginnen", rufe, "der Consumer setzt keinen Marker")
        self.assertIn("turn_beenden", rufe, "der Consumer loescht keinen Marker")
