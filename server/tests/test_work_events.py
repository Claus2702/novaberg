"""Zeugen: Pixies Aufträge und Novas Impulse erreichen den Client als Ereignisse.

Der Client liest `pixie_auftrag` und `impuls_denkt` (`client/ui/work_events.py`).
Bis hierher sendete der Server beides nicht; die Arbeit Pixies stand nur in einem
Statusschlüssel, den der Heartbeat nach **jedem** Lauf zurücksetzt — auch nach
einem leeren. Ein Ende, das daran hinge, käme alle dreißig Sekunden.

Zeugen dieser Datei:
  * Ein Auftrag meldet `beginn` vor und `ende` nach seinem Lauf, mit allen Feldern
    samt Thema; ohne Emotion fehlen `emotion` und `arousal`, statt leer zu sein.
  * Ein leerer Heartbeat, eine periodische Aufgabe und ein Kandidat ohne Agent
    melden nichts.
  * Ein Fehler beim Senden schreibt eine Error-Zeile, der Auftrag läuft weiter; ein
    Fehler im Agenten meldet trotzdem `ende`.
  * Ein Impuls meldet `impuls_denkt` `beginn` und `ende` — das Ende auch ohne
    Antwort und nach ihr; ein Nutzer-Turn meldet nichts.
  * Mit echtem Event-Loop und echtem `broadcast`: Das Senden aus dem Heartbeat hält
    den Loop nicht an. Ein ersetzter Broadcast sähe ein `broadcast_threadsafe` im
    Loop nicht — es wartete dort auf eine Coroutine desselben Loops.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import time
import unittest
from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import api.websocket as websocket_mod
import services.event_consumer as ec_mod
import services.work_events as we_mod
from services.pixie import scheduler

USER: str = "nutzer-7"
CHARACTER: str = "nova"
AGENT_NAME: str = "vertiefung"
WORK_LOGGER: str = "ki_server.work_events"

# Die Felder, die der Client in `pixie_auftrag` kennt (`client/ui/work_events.py`).
CLIENT_PIXIE_FIELDS: frozenset[str] = frozenset(
    {"typ", "phase", "spur", "art", "emotion", "arousal", "thema"},
)


def _shadow_job(**fields: object) -> dict:
    """Ein Gewinner aus der Shadow-Queue, wie ihn `kandidaten_sammeln` liefert."""
    daten: dict = {
        "id": 11, "user_id": USER, "character_id": CHARACTER, "beobachter": "user",
        "aufgabe": "vertiefen", "thema": "Gezeiten", "emotion": "neugierig",
        "arousal": 0.62, "aktiv": True,
    }
    daten.update(fields)
    return {
        "name": daten["aufgabe"], "prioritaet": 0.95, "prioritaet_basis": 0.95,
        "ueberfaellig_s": None, "quelle": "shadow_auftrag", "daten": daten,
        "auftrag_id": 11, "queue_key": None, "queue_raw": None, "schedule_key": None,
        "themen": daten["thema"],
    }


def _periodic_job() -> dict:
    """Eine fällige periodische Aufgabe: kein Nutzer, keine Emotion."""
    return {
        "name": "Decay", "prioritaet": 0.5, "prioritaet_basis": 0.5,
        "ueberfaellig_s": 3.0, "quelle": "periodisch", "auftrag_id": None,
        "daten": {"priority": "0.5", "interval": "300"}, "queue_key": None,
        "queue_raw": None, "schedule_key": "pixie:schedule:decay", "themen": "",
    }


class _Recorder:
    """Fängt ab, was `broadcast` an die Clients geben würde, in der Reihenfolge."""

    def __init__(self) -> None:
        """Beginnt ohne Sendung."""
        self.sent: list[tuple[str, dict, str]] = []

    async def __call__(
        self, user_id: str, nachricht: str, character_id: str = "", exclude_client: str = "",
    ) -> None:
        """Merkt Empfänger, Nutzlast und Charakter-Filter."""
        self.sent.append((user_id, json.loads(nachricht), character_id))

    def payloads(self, typ: str) -> list[dict]:
        """Die Nutzlasten eines Typs."""
        return [payload for _, payload, _ in self.sent if payload["typ"] == typ]

    def types(self) -> list[str]:
        """Die Typen aller Sendungen, in der Reihenfolge."""
        return [payload["typ"] for _, payload, _ in self.sent]


def _heartbeat_patches(
    stack: ExitStack, candidates: list[dict], agent: AsyncMock, track: str,
    agent_name: str | None = AGENT_NAME,
) -> MagicMock:
    """Ersetzt Redis, Kandidaten, Spur, Router und Agent des Heartbeats.

    Gibt den ersetzten `abschluss` zurück. `broadcast` bleibt unberührt.
    """
    redis = MagicMock()
    redis.exists.return_value = False
    stack.enter_context(patch.object(scheduler, "redis_client", redis))
    stack.enter_context(patch.object(scheduler, "kandidaten_sammeln", return_value=candidates))
    stack.enter_context(patch.object(scheduler, "_spur_von", return_value=track))
    stack.enter_context(patch.object(scheduler, "route", return_value=agent_name))
    stack.enter_context(patch.object(scheduler, "agent_ausfuehren", agent))
    return stack.enter_context(patch.object(scheduler, "abschluss"))


class _HeartbeatRun(unittest.IsolatedAsyncioTestCase):
    """Fährt den Heartbeat selbst, nicht den Nutzlast-Bau allein."""

    async def _run(
        self, candidates: list[dict], broadcast: object, agent: AsyncMock | None = None,
        track: str = "llm",
    ) -> tuple[AsyncMock, MagicMock]:
        """Lässt einen Heartbeat laufen; gibt Agent und Abschluss zurück."""
        agent = agent or AsyncMock(return_value=True)
        with ExitStack() as stack:
            closing = _heartbeat_patches(stack, candidates, agent, track)
            stack.enter_context(patch.object(we_mod, "broadcast", broadcast))
            await scheduler.pixie_heartbeat(MagicMock(), spur=track)
        return agent, closing


class PixieJobEventsTest(_HeartbeatRun):
    """Ein Auftrag mit Nutzer meldet seinen Lauf — und nur seinen Lauf."""

    async def test_ein_auftrag_meldet_beginn_und_ende_mit_allen_feldern(self) -> None:
        recorder = _Recorder()
        await self._run([_shadow_job()], recorder)

        expected: dict = {
            "typ": "pixie_auftrag", "phase": "beginn", "spur": "llm", "art": "vertiefen",
            "emotion": "neugierig", "arousal": 0.62, "thema": "Gezeiten",
        }
        self.assertEqual(
            recorder.payloads("pixie_auftrag"), [expected, {**expected, "phase": "ende"}],
        )
        self.assertEqual([user for user, _, _ in recorder.sent], [USER, USER])
        self.assertLessEqual(set(expected), CLIENT_PIXIE_FIELDS)

    async def test_beginn_vor_dem_agenten_und_ende_nach_ihm(self) -> None:
        recorder = _Recorder()
        seen_at_start: list[int] = []

        async def agent(*_args: object) -> bool:
            seen_at_start.append(len(recorder.sent))
            return True

        await self._run([_shadow_job()], recorder, agent=AsyncMock(side_effect=agent))

        self.assertEqual(seen_at_start, [1], "beginn muss vor dem Lauf gesendet sein")
        self.assertEqual(len(recorder.sent), 2)

    async def test_ein_auftrag_ohne_emotion_sendet_die_felder_nicht(self) -> None:
        recorder = _Recorder()
        await self._run([_shadow_job(emotion="", arousal=None)], recorder)

        payloads: list[dict] = recorder.payloads("pixie_auftrag")
        self.assertEqual([p["phase"] for p in payloads], ["beginn", "ende"])
        for payload in payloads:
            self.assertNotIn("emotion", payload)
            self.assertNotIn("arousal", payload)
            self.assertEqual(payload["thema"], "Gezeiten")

    async def test_ein_leerer_heartbeat_sendet_nichts(self) -> None:
        recorder = _Recorder()
        agent, _ = await self._run([], recorder)

        agent.assert_not_awaited()
        self.assertEqual(recorder.sent, [])

    async def test_eine_periodische_aufgabe_sendet_nichts(self) -> None:
        recorder = _Recorder()
        agent, _ = await self._run([_periodic_job()], recorder, track="cpu")

        agent.assert_awaited_once()
        self.assertEqual(recorder.sent, [])

    async def test_ein_kandidat_ohne_agent_sendet_nichts(self) -> None:
        recorder = _Recorder()
        agent = AsyncMock(return_value=True)
        with ExitStack() as stack:
            _heartbeat_patches(stack, [_shadow_job()], agent, "llm", agent_name=None)
            stack.enter_context(patch.object(we_mod, "broadcast", recorder))
            await scheduler.pixie_heartbeat(MagicMock(), spur="llm")

        agent.assert_not_awaited()
        self.assertEqual(recorder.sent, [])

    async def test_ein_fehler_beim_senden_haelt_den_auftrag_nicht_an(self) -> None:
        broken = AsyncMock(side_effect=RuntimeError("Leitung weg"))
        with self.assertLogs(WORK_LOGGER, "ERROR") as log:
            agent, closing = await self._run([_shadow_job()], broken)

        agent.assert_awaited_once()
        closing.assert_called_once()
        self.assertIs(closing.call_args.args[1], True)
        self.assertEqual(broken.await_count, 2)
        lines: list[str] = [line for line in log.output if "pixie_auftrag" in line]
        self.assertEqual(len(lines), 2, log.output)

    async def test_ein_fehler_im_agenten_meldet_trotzdem_ende(self) -> None:
        recorder = _Recorder()
        broken_agent = AsyncMock(side_effect=RuntimeError("Agent gescheitert"))
        with self.assertLogs("ki_server.pixie", "ERROR"):
            await self._run([_shadow_job()], recorder, agent=broken_agent)

        phases: list[str] = [p["phase"] for p in recorder.payloads("pixie_auftrag")]
        self.assertEqual(phases, ["beginn", "ende"])

    async def test_ein_auftrag_mit_ungueltigem_arousal_laeuft_ohne_ereignis(self) -> None:
        recorder = _Recorder()
        with self.assertLogs(WORK_LOGGER, "ERROR"):
            agent, _ = await self._run([_shadow_job(arousal=1.7)], recorder)

        agent.assert_awaited_once()
        self.assertEqual(recorder.sent, [])


class PixieJobPayloadTest(unittest.TestCase):
    """Der Bau der Nutzlast, ohne Heartbeat."""

    def test_die_art_kommt_aus_der_menge_des_routers(self) -> None:
        with self.assertRaises(ValueError):
            we_mod.pixie_job_payload(_shadow_job(aufgabe="frei erfunden"), "llm", "beginn")
        payload: dict = we_mod.pixie_job_payload(_shadow_job(), "llm", "beginn")
        self.assertEqual(payload["art"], "vertiefen")

    def test_ein_leeres_thema_fehlt(self) -> None:
        payload: dict = we_mod.pixie_job_payload(_shadow_job(thema=""), "cpu", "ende")
        self.assertNotIn("thema", payload)
        self.assertEqual(payload["spur"], "cpu")

    def test_der_nutzer_eines_promotionsauftrags(self) -> None:
        candidate: dict = {
            "quelle": "queue", "themen": "",
            "daten": {"aufgabe": "lzg_promotion", "user_id": USER, "key": "kzg:1"},
        }
        self.assertEqual(we_mod.job_user(candidate), USER)
        self.assertIsNone(we_mod.job_user(_periodic_job()))

    def test_ein_auftrag_ohne_nutzer_ist_ein_fehler(self) -> None:
        with self.assertRaises(ValueError):
            we_mod.job_user(_shadow_job(user_id=""))


class SendingFromTheHeartbeatDoesNotWaitTest(unittest.IsolatedAsyncioTestCase):
    """Echter Event-Loop, echter `broadcast`, ersetzt ist nur der Socket."""

    async def test_das_senden_aus_dem_heartbeat_haelt_den_loop_nicht_an(self) -> None:
        received: list[dict] = []

        class _Socket:
            """Ein Socket, der sofort annimmt."""

            async def send_text(self, text: str) -> None:
                """Merkt die Nachricht."""
                received.append(json.loads(text))

        connection = websocket_mod.ClientConnection(
            client_id="desktop", character_id=CHARACTER, websocket=_Socket(),
        )
        with ExitStack() as stack:
            _heartbeat_patches(stack, [_shadow_job()], AsyncMock(return_value=True), "llm")
            stack.enter_context(
                patch.dict(websocket_mod.aktive_verbindungen, {USER: [connection]}, clear=True),
            )
            started: float = time.monotonic()
            await scheduler.pixie_heartbeat(MagicMock(), spur="llm")
            elapsed: float = time.monotonic() - started

        # Ein `broadcast_threadsafe` aus dem Loop wartete je Sendung bis zu seiner
        # Frist (5 s) auf eine Coroutine, die erst danach laufen kann.
        self.assertLess(elapsed, 2.0)
        self.assertEqual([p["phase"] for p in received], ["beginn", "ende"])


class _OnePass:
    """Lässt die Schleife des Event-Consumers genau einen Durchgang machen."""

    def __init__(self) -> None:
        """Noch kein Durchgang."""
        self.calls: int = 0

    def is_set(self) -> bool:
        """Beim ersten Blick nein, danach ja."""
        self.calls += 1
        return self.calls > 1


def _queue_event(source: str, **payload_fields: object) -> dict:
    """Ein Ereignis der Event-Queue."""
    payload: dict = {"turn_id": "turn-5d2a"}
    payload.update(payload_fields)
    return {
        "event_id": "ev-1", "user_id": USER, "character_id": CHARACTER, "source": source,
        "typ": "message", "payload": payload, "trigger_count": 0,
    }


def _impulse_event() -> dict:
    """Ein eigener Impuls Novas, wie ihn die Zustellung einreiht."""
    return _queue_event(
        "character", reiz_herkunft="eigener_impuls", eigener_gedanke="Ebbe und Flut.",
    )


def _graph_result(response: str) -> dict:
    """Das Ergebnis eines CharacterGraph-Laufs, so weit die Zustellung es liest."""
    return {"response": response, "turn_id": "turn-5d2a", "internal": None}


class ImpulseThinkingTest(unittest.IsolatedAsyncioTestCase):
    """Fährt die Schleife des Event-Consumers, nicht den Kontext allein."""

    async def _consume(self, event: dict, graph: dict) -> _Recorder:
        """Lässt den Consumer ein Ereignis verarbeiten; `graph` ersetzt den Graphenlauf."""
        recorder = _Recorder()
        redis = MagicMock()
        redis.keys.return_value = [f"event_queue:{USER}:{CHARACTER}"]
        redis.get.return_value = None
        with ExitStack() as stack:
            for name, value in (
                ("shutdown_event", _OnePass()), ("POLL_INTERVAL", 0), ("DEBOUNCE_DELAY", 0),
                ("redis_client", redis), ("broadcast", recorder),
            ):
                stack.enter_context(patch.object(ec_mod, name, value))
            stack.enter_context(
                patch.object(ec_mod, "event_naechstes", side_effect=[event, None, None]),
            )
            stack.enter_context(patch.object(ec_mod, "turn_beginnen"))
            stack.enter_context(patch.object(ec_mod, "turn_beenden"))
            stack.enter_context(patch.object(ec_mod, "kosten_summen", return_value=None))
            stack.enter_context(patch.object(ec_mod, "_graph_streamen", **graph))
            stack.enter_context(patch.object(we_mod, "broadcast", recorder))
            await ec_mod.event_consumer_loop(
                redis, MagicMock(), MagicMock(), {USER: ["ws"]}, MagicMock(),
            )
        return recorder

    async def test_ein_impuls_ohne_antwort_meldet_ende(self) -> None:
        recorder = await self._consume(
            _impulse_event(), {"return_value": _graph_result("")},
        )

        self.assertEqual(recorder.types(), ["impuls_denkt", "turn_gescheitert", "impuls_denkt"])
        self.assertEqual(
            recorder.payloads("impuls_denkt"),
            [{"typ": "impuls_denkt", "phase": "beginn"}, {"typ": "impuls_denkt", "phase": "ende"}],
        )
        self.assertEqual({character for _, _, character in recorder.sent}, {CHARACTER})

    async def test_das_ende_kommt_nach_der_antwort(self) -> None:
        recorder = await self._consume(
            _impulse_event(), {"return_value": _graph_result("Die Flut kommt zweimal.")},
        )

        self.assertEqual(
            recorder.types(), ["impuls_denkt", "character_response", "impuls_denkt"],
        )

    async def test_ein_scheiternder_graph_meldet_trotzdem_ende(self) -> None:
        with self.assertLogs("ki_server.event_consumer", "ERROR"):
            recorder = await self._consume(
                _impulse_event(), {"side_effect": RuntimeError("Graph gescheitert")},
            )

        phases: list[str] = [p["phase"] for p in recorder.payloads("impuls_denkt")]
        self.assertEqual(phases, ["beginn", "ende"])

    async def test_ein_nutzer_turn_meldet_kein_impuls_denkt(self) -> None:
        recorder = await self._consume(
            _queue_event("user", user_prompt="Wann kommt die Flut?"),
            {"return_value": _graph_result("Gegen sechs.")},
        )

        self.assertEqual(recorder.types(), ["character_response"])


if __name__ == "__main__":
    unittest.main()
