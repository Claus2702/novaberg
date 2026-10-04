"""Arbeitsereignisse an den Client: Pixies Aufträge und Novas Impulse.

Der Client zeigt daraus, woran gerade gearbeitet wird — in der Statuszeile und im
Avatar. Zwei Ereignisse, gelesen von `client/ui/work_events.py`:

  `pixie_auftrag`  Pixie beginnt oder beendet einen Auftrag mit Nutzer.
  `impuls_denkt`   Der CharacterGraph beginnt oder beendet einen eigenen Impuls.

**Die Ereignisse sind Beiwerk.** Gesendet wird mit `await broadcast(...)` aus dem
Event-Loop. Ein Fehler beim Senden schreibt eine Error-Zeile und hält weder den
Auftrag noch den Turn an. `broadcast_threadsafe` ist hier falsch: Es wartet auf
eine Coroutine desselben Loops und hielte ihn bis zum Ablauf seiner Frist an.

**Abwesend, nicht leer:** Trägt ein Auftrag keine Emotion, kein Arousal oder kein
Thema, fehlt das Feld in der Nutzlast. Ein leerer Wert sähe aus wie eine Angabe.
"""

import json
import logging
from collections.abc import AsyncIterator, Awaitable, Mapping
from contextlib import asynccontextmanager

from api.websocket import broadcast
from services.model_services.spur import SPUR_CPU, SPUR_LLM
from services.pixie.router import QUEUE_JOB_KINDS

logger = logging.getLogger("ki_server.work_events")

PHASE_BEGIN: str = "beginn"
PHASE_END: str = "ende"
PHASES: tuple[str, ...] = (PHASE_BEGIN, PHASE_END)
TRACKS: tuple[str, ...] = (SPUR_LLM, SPUR_CPU)

# Die Quellen, deren Aufträge einem Nutzer gehören. Periodische Aufgaben gehören
# keinem und senden nichts.
USER_JOB_SOURCES: tuple[str, ...] = ("shadow_auftrag", "queue")
PERIODIC_SOURCE: str = "periodisch"

# Die Herkunft eines Reizes, den Nova selbst angestoßen hat (gesetzt von der
# Zustellung der Impulse).
IMPULSE_ORIGIN: str = "eigener_impuls"


def job_user(candidate: Mapping) -> str | None:
    """Der Nutzer, dem ein Gewinner des Heartbeats gehört.

    Vorbedingung: `candidate` ist ein Kandidat aus `kandidaten_sammeln` mit `quelle`
    und `daten`.
    Nachbedingung: die `user_id` des Auftrags bei einer Queue-Quelle; None bei einer
    periodischen Aufgabe, denn sie gehört keinem Nutzer.
    Fehlerfälle: ValueError bei einer unbekannten Quelle und bei einem Auftrag ohne
    `user_id`.
    """
    # ── Eingabe-Validierung ──
    source = candidate.get("quelle")
    if source == PERIODIC_SOURCE:
        return None
    if source not in USER_JOB_SOURCES:
        raise ValueError(f"unbekannte Quelle {source!r}")
    data = candidate.get("daten")
    if not isinstance(data, Mapping):
        raise ValueError(f"Auftrag aus {source!r} ohne Daten")

    # ── Verarbeitung ──
    user_id = data.get("user_id")

    # ── Ausgabe-Verifikation ──
    if not isinstance(user_id, str) or not user_id:
        raise ValueError(f"Auftrag aus {source!r} ohne user_id")
    return user_id


def mood_fields(data: Mapping) -> dict:
    """Emotion und Arousal eines Auftrags — nur die, die er trägt.

    Vorbedingung: `data` sind die Daten eines Auftrags; `emotion` ist Text oder None,
    `arousal` eine Zahl oder None.
    Nachbedingung: ein dict mit höchstens `emotion` (nichtleerer Text) und `arousal`
    (Zahl in 0..1). Eine leere oder fehlende Emotion und ein fehlendes Arousal fehlen
    auch hier.
    Fehlerfälle: ValueError, wenn `emotion` kein Text ist oder `arousal` keine Zahl in
    0..1.
    """
    # ── Eingabe-Validierung ──
    emotion = data.get("emotion")
    if emotion is not None and not isinstance(emotion, str):
        raise ValueError(f"emotion ist kein Text (Typ {type(emotion).__name__})")
    arousal = data.get("arousal")
    is_number: bool = isinstance(arousal, int | float) and not isinstance(arousal, bool)
    if arousal is not None and not is_number:
        raise ValueError(f"arousal ist keine Zahl (Typ {type(arousal).__name__})")
    if arousal is not None and not 0.0 <= arousal <= 1.0:
        raise ValueError(f"arousal {arousal!r} liegt nicht in 0..1")

    # ── Verarbeitung ──
    fields: dict = {}
    if emotion:
        fields["emotion"] = emotion
    if arousal is not None:
        fields["arousal"] = float(arousal)

    # Keine Ausgabe-Verifikation: Jeder Wert ist oben geprüft und bleibt unverändert.
    return fields


def pixie_job_payload(candidate: Mapping, track: str, phase: str) -> dict:
    """Die Nutzlast von `pixie_auftrag` für einen Gewinner des Heartbeats.

    Vorbedingung: `candidate` ist ein Kandidat aus einer Queue-Quelle mit `daten`
    (darin `aufgabe`) und `themen`; `track` ist eine Spur aus `TRACKS`, `phase` eine
    aus `PHASES`.
    Nachbedingung: ein dict mit `typ`, `phase`, `spur` und `art` aus
    `QUEUE_JOB_KINDS`; `emotion`, `arousal` und `thema` nur, wenn der Auftrag sie
    trägt. Kein Wert ist None oder leer.
    Fehlerfälle: ValueError bei unbekannter Phase oder Spur, einer Art außerhalb der
    Menge des Routers, einem Thema, das kein Text ist, und aus `mood_fields`.
    """
    # ── Eingabe-Validierung ──
    if phase not in PHASES:
        raise ValueError(f"phase {phase!r} ist unbekannt")
    if track not in TRACKS:
        raise ValueError(f"spur {track!r} ist unbekannt")
    data = candidate.get("daten")
    if not isinstance(data, Mapping):
        raise ValueError("Auftrag ohne Daten")
    kind = data.get("aufgabe")
    if not isinstance(kind, str) or kind not in QUEUE_JOB_KINDS:
        raise ValueError(f"art {kind!r} gehört nicht zur Menge des Routers")
    topic = candidate.get("themen")
    if topic is not None and not isinstance(topic, str):
        raise ValueError(f"thema ist kein Text (Typ {type(topic).__name__})")

    # ── Verarbeitung ──
    payload: dict = {"typ": "pixie_auftrag", "phase": phase, "spur": track, "art": kind}
    payload.update(mood_fields(data))
    if topic:
        payload["thema"] = topic

    # ── Ausgabe-Verifikation ──
    if None in payload.values() or "" in payload.values():
        raise ValueError(f"Nutzlast mit leerem Feld (Felder: {sorted(payload)})")
    return payload


def pixie_job_announcement(candidate: Mapping, track: str) -> tuple[str, dict] | None:
    """Nutzer und Nutzlast `beginn` eines Gewinners, oder None, wenn nichts zu senden ist.

    Vorbedingung: `candidate` ist der Gewinner des Heartbeats, `track` seine Spur.
    Nachbedingung: (Nutzer, Nutzlast mit `phase` `beginn`) bei einem Auftrag mit
    Nutzer; None bei einer periodischen Aufgabe, und None nach einer Error-Zeile,
    wenn aus dem Auftrag keine gültige Nutzlast entsteht. Wirft nie ValueError.
    """
    # ── Verarbeitung ──
    try:
        user_id = job_user(candidate)
        payload = None if user_id is None else pixie_job_payload(candidate, track, PHASE_BEGIN)
    except ValueError:
        # Das Thema steht nicht in der Zeile: Es ist Gesprächsinhalt.
        logger.exception(
            f"pixie_auftrag: kein Ereignis für '{candidate.get('name')}' "
            f"(Quelle {candidate.get('quelle')!r}) — der Auftrag läuft trotzdem"
        )
        return None

    # ── Ausgabe-Verifikation ──
    if user_id is None or payload is None:
        return None
    return user_id, payload


async def send_work_event(user_id: str, payload: Mapping, character_id: str = "") -> bool:
    """Sendet ein Arbeitsereignis an die Clients eines Nutzers.

    Vorbedingung: `user_id` ist nichtleer; `payload` trägt `typ` und `phase`.
    Nachbedingung: True, wenn `broadcast` ohne Ausnahme zurückkam; sonst False nach
    einer Error-Zeile. Wirft keine Exception — ein Ereignis hält keinen Auftrag und
    keinen Turn an. Ein Abbruch (`CancelledError`) geht durch.
    """
    # ── Eingabe-Validierung ──
    typ = payload.get("typ")
    phase = payload.get("phase")
    if not user_id:
        logger.error(f"Arbeitsereignis '{typ}' ({phase}) ohne Nutzer — nicht gesendet")
        return False

    # ── Verarbeitung ──
    try:
        message: str = json.dumps(payload, ensure_ascii=False)
        await broadcast(user_id, message, character_id=character_id)
    except Exception:  # noqa: BLE001 — ein Ereignis hält keinen Auftrag an
        logger.exception(f"Arbeitsereignis '{typ}' ({phase}) an '{user_id}' nicht gesendet")
        return False

    # Keine Ausgabe-Verifikation: `broadcast` meldet und räumt kaputte Verbindungen selbst.
    return True


@asynccontextmanager
async def pixie_job_events(candidate: Mapping, track: str) -> AsyncIterator[None]:
    """Meldet `beginn` vor und `ende` nach dem Lauf eines Gewinners — auch wenn er scheitert.

    Vorbedingung: `candidate` ist der Gewinner des Heartbeats, für den ein Agent
    gefunden ist; `track` ist seine Spur.
    Nachbedingung: Bei einem Auftrag mit Nutzer ging `beginn` vor dem Block an diesen
    Nutzer und `ende` nach ihm, auch wenn der Block eine Ausnahme warf; bei einer
    periodischen Aufgabe ging nichts.
    Fehlerfälle: Ein Auftrag ohne gültige Nutzlast und ein Fehler beim Senden
    schreiben eine Error-Zeile; der Block läuft trotzdem.
    """
    # ── Eingabe-Validierung ──
    announcement = pixie_job_announcement(candidate, track)
    if announcement is None:
        yield
        return

    # ── Verarbeitung ──
    user_id, begin = announcement
    await send_work_event(user_id, begin)
    try:
        yield
    finally:
        await send_work_event(user_id, {**begin, "phase": PHASE_END})


def is_impulse(event: Mapping) -> bool:
    """Ob ein Ereignis der Event-Queue einen eigenen Impuls Novas trägt.

    Vorbedingung: `event` ist ein Ereignis der Event-Queue; `payload` ist ein Mapping
    oder fehlt.
    Nachbedingung: True nur bei `reiz_herkunft == "eigener_impuls"` im Payload.
    Fehlerfälle: TypeError, wenn `payload` weder fehlt noch ein Mapping ist.
    """
    # ── Eingabe-Validierung ──
    payload = event.get("payload") or {}
    if not isinstance(payload, Mapping):
        raise TypeError(f"is_impulse: payload ist {type(payload).__name__}, kein Mapping")

    # Keine Ausgabe-Verifikation: Der Vergleich ergibt einen Wahrheitswert.
    return payload.get("reiz_herkunft") == IMPULSE_ORIGIN


def impulse_payload(phase: str) -> dict:
    """Die Nutzlast von `impuls_denkt` — ohne Inhalt, nur die Phase.

    Vorbedingung: `phase` ist eine aus `PHASES`.
    Nachbedingung: ein dict mit genau `typ` und `phase`.
    Fehlerfälle: ValueError bei einer unbekannten Phase.
    """
    # ── Eingabe-Validierung ──
    if phase not in PHASES:
        raise ValueError(f"phase {phase!r} ist unbekannt")

    # Keine Ausgabe-Verifikation: Die Nutzlast besteht aus zwei geprüften Konstanten.
    return {"typ": "impuls_denkt", "phase": phase}


@asynccontextmanager
async def impulse_thinking(event: Mapping, user_id: str, character_id: str) -> AsyncIterator[None]:
    """Meldet `beginn` vor und `ende` nach dem CharacterGraph eines Impulses.

    Vorbedingung: `event` ist das Ereignis, das der Block verarbeitet; `user_id` und
    `character_id` sind das Paar seiner Queue.
    Nachbedingung: Bei einem Impuls ging `impuls_denkt` `beginn` vor dem Block an die
    Clients dieses Paares und `ende` nach ihm — auch ohne Antwort und auch, wenn der
    Block eine Ausnahme warf. Bei jedem anderen Ereignis ging nichts.
    Fehlerfälle: Ein Fehler beim Senden schreibt eine Error-Zeile; der Block läuft
    trotzdem.
    """
    # ── Eingabe-Validierung ──
    if not is_impulse(event):
        yield
        return

    # ── Verarbeitung ──
    await send_work_event(user_id, impulse_payload(PHASE_BEGIN), character_id=character_id)
    try:
        yield
    finally:
        await send_work_event(user_id, impulse_payload(PHASE_END), character_id=character_id)


async def with_impulse_events(
    event: Mapping, user_id: str, character_id: str, run: Awaitable[None],
) -> None:
    """Wartet auf den Durchlauf `run` und meldet ihn als `impuls_denkt`, wenn er ein Impuls ist.

    Die Form für den Event-Consumer: Dort steht der Aufruf schon tief verschachtelt,
    und ein `async with` fügte eine Ebene hinzu.

    Vorbedingung: `run` ist der noch nicht gestartete Durchlauf des CharacterGraph für
    `event`; die übrigen wie bei `impulse_thinking`.
    Nachbedingung: `run` ist abgeschlossen; Meldungen wie bei `impulse_thinking`.
    Fehlerfälle: Eine Ausnahme aus `run` geht nach der Meldung `ende` weiter.
    """
    # Keine Eingabe-Validierung und keine Ausgabe-Verifikation: Beides liegt bei
    # `impulse_thinking` und beim Durchlauf selbst.
    async with impulse_thinking(event, user_id, character_id):
        await run
