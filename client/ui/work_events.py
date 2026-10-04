"""Arbeitszyklen als Ereignisse: Typen und ihre Bildung aus der Nutzlast des WebSockets.

Das Modul importiert kein GTK, damit Typen und Bildung ohne Fenster prüfbar sind.
Die Ereignisse tragen keine Zeit: Wer sie bekommt, setzt seine eigene Uhr an. Der
Server sendet `pixie_auftrag` und `impuls_denkt` und `turn_gescheitert`; „Turn beginnt“
entsteht im Client und hat keine Nutzlast.
"""

import logging
from collections.abc import Mapping
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PHASE_BEGIN = "beginn"
PHASE_END = "ende"
PHASES = (PHASE_BEGIN, PHASE_END)
TRACKS = ("llm", "cpu")


@dataclass(frozen=True)
class TurnStarted:
    """Der Nutzer sendet eine Nachricht, in diesem oder einem anderen Client."""


@dataclass(frozen=True)
class TurnFailure:
    """Der Turn ist gescheitert, oder das Senden ist es; es kommt keine Antwort."""


@dataclass(frozen=True)
class ImpulseThinking:
    """Ein Impuls geht in den CharacterGraph (`beginn`) oder ist dort fertig (`ende`)."""

    phase: str


@dataclass(frozen=True)
class PixieWork:
    """Pixie beginnt (`beginn`) oder beendet (`ende`) einen Auftrag in einer Spur.

    `emotion` und `arousal` sind None, wenn der Auftrag keine trägt; `topic` ist None,
    wenn die Nutzlast kein Thema nennt.
    """

    phase: str
    track: str
    job_kind: str
    emotion: str | None = None
    arousal: float | None = None
    topic: str | None = None


WorkEvent = TurnStarted | TurnFailure | ImpulseThinking | PixieWork
WORK_EVENT_TYPES = (TurnStarted, TurnFailure, ImpulseThinking, PixieWork)


def _required_text(data: Mapping, key: str) -> str:
    """Gibt das Feld als nichtleeren Text zurück; sonst ValueError ohne den Wert zu nennen."""
    # ── Eingabe-Validierung ──
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} fehlt oder ist kein Text (Typ {type(value).__name__})")

    # Keine Ausgabe-Verifikation: Die Prüfung oben ist die Aussage; der Wert bleibt unverändert.
    return value


def _optional_text(data: Mapping, key: str) -> str | None:
    """Gibt das Feld als nichtleeren Text zurück, None wenn es fehlt oder None ist."""
    # ── Eingabe-Validierung ──
    if data.get(key) is None:
        return None

    # Keine Ausgabe-Verifikation: Die Prüfung steht in `_required_text`.
    return _required_text(data, key)


def _choice(data: Mapping, key: str, allowed: tuple[str, ...]) -> str:
    """Gibt das Feld zurück, wenn es einer der erlaubten Werte ist; sonst ValueError."""
    # ── Eingabe-Validierung ──
    value = _required_text(data, key)
    if value not in allowed:
        raise ValueError(f"{key} {value!r} ist unbekannt (erlaubt: {', '.join(allowed)})")

    # Keine Ausgabe-Verifikation: Die Prüfung oben ist die Aussage; der Wert bleibt unverändert.
    return value


def _optional_arousal(data: Mapping) -> float | None:
    """Gibt `arousal` als Zahl von 0 bis 1 zurück, None wenn es fehlt oder None ist."""
    # ── Eingabe-Validierung ──
    value = data.get("arousal")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"arousal ist keine Zahl (Typ {type(value).__name__})")
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"arousal {value!r} liegt nicht in 0..1")

    # Keine Ausgabe-Verifikation: Die Prüfung oben ist die Aussage; der Wert ist eine Zahl.
    return float(value)


def _failure_from(data: Mapping) -> TurnFailure:
    """Bildet `turn_gescheitert`; das Ereignis trägt nichts aus der Nutzlast.

    Nachbedingung: ein `TurnFailure`, unabhängig vom Inhalt von `data`.
    """
    # Keine Eingabe-Validierung und keine Ausgabe-Verifikation: Der Typ trägt keine Felder.
    return TurnFailure()


def _impulse_from(data: Mapping) -> ImpulseThinking:
    """Bildet `impuls_denkt` aus `phase`.

    Nachbedingung: ein `ImpulseThinking` mit einer `phase` aus `PHASES`; sonst ValueError.
    """
    # Keine Ausgabe-Verifikation: Die Phase ist in `_choice` geprüft.
    return ImpulseThinking(phase=_choice(data, "phase", PHASES))


def _pixie_from(data: Mapping) -> PixieWork:
    """Bildet `pixie_auftrag` aus `phase`, `spur`, `art` und, wo vorhanden, dem Rest.

    Nachbedingung: ein `PixieWork` mit `phase` aus `PHASES`, `track` aus `TRACKS`, nichtleerer
    `job_kind`; `emotion`, `arousal` und `topic` sind None oder gültig (`arousal` in 0..1);
    sonst ValueError.
    """
    # Keine Ausgabe-Verifikation: Jedes Feld ist in seinem Prüfer geprüft.
    return PixieWork(
        phase=_choice(data, "phase", PHASES),
        track=_choice(data, "spur", TRACKS),
        job_kind=_required_text(data, "art"),
        emotion=_optional_text(data, "emotion"),
        arousal=_optional_arousal(data),
        topic=_optional_text(data, "thema"),
    )


_BUILDERS = {
    "turn_gescheitert": _failure_from,
    "impuls_denkt": _impulse_from,
    "pixie_auftrag": _pixie_from,
}


def work_event_from_payload(data: Mapping) -> WorkEvent | None:
    """Bildet aus der Nutzlast eines WebSocket-Ereignisses das Ereignis der Arbeitszyklen.

    Vorbedingung: `data` ist die Nutzlast als Mapping mit `typ` `turn_gescheitert`,
    `impuls_denkt` oder `pixie_auftrag`.
    Nachbedingung: das Ereignis; bei einem unbekannten `typ`, einer unbekannten `phase`
    oder Spur, einem `arousal` außerhalb von 0..1 und einem Feld des falschen Typs
    eine Error-Zeile und None. Die Zeile nennt das Feld; bei `typ`, `phase`, Spur und
    `arousal` nennt sie auch den Wert (Kennwörter und Zahlen des Servers). Das Thema
    nennt sie nie, denn es ist Gesprächsinhalt.
    Fehlerfall: TypeError, wenn `data` kein Mapping ist.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(data, Mapping):
        raise TypeError(f"work_event_from_payload: data ist {type(data).__name__}, kein Mapping")
    typ = data.get("typ")
    builder = _BUILDERS.get(typ)
    if builder is None:
        logger.error(f"Arbeitsereignis: unbekannter Typ {typ!r} — verworfen")
        return None

    # ── Verarbeitung ──
    try:
        event = builder(data)
    except ValueError as error:
        logger.error(f"Arbeitsereignis '{typ}' ungültig: {error} — verworfen")
        return None

    # ── Ausgabe-Verifikation ──
    if not isinstance(event, WORK_EVENT_TYPES):
        raise TypeError(f"work_event_from_payload: '{typ}' ergab {type(event).__name__}")
    return event
