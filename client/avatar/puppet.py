"""Die Puppe: Ausdruck, Animator, Sprechen, Blinzeln, Atem und Takt in einem Bild.

Hier laufen die Fäden zusammen, wie im Prototyp `frame()` ohne Testbedienung:
Ein neues Ziel (`puppet_cue`) setzt den Ausdruck mit Mundversatz und beginnt das
Sprechen des Texts; jeder Schritt (`puppet_step`) schreibt Feder und Sprechen
fort, blinzelt, atmet und liefert die `Pose` für das Zeichnen.

Das Modul liest keine Uhr. Zeit kommt als Parameter in Sekunden, von einer
einzigen Uhr für alles; der Zufall der Blinzelabstände kommt als
`random.Random` von außen.

`utterance_from_turn` setzt die Antwort an den Client in eine `Utterance` um:
der Name der Emotion wird zum Sektor über die Namen der Schlüsselbilder, das
Arousal wird begrenzt, der Text bleibt, wie er ist.
"""

import logging
import math
import random
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from avatar.animator import AnimatorState, advance, set_target, start
from avatar.compose import BOIL_MS
from avatar.expression import face_target
from avatar.face import NEUTRAL
from avatar.pose import Pose
from avatar.speech import SILENT, SpeechState, mouth_state_combine, speech_step, start_speech

logger = logging.getLogger(__name__)

FIRST_BLINK_MS = 1800.0  # das erste Blinzeln, gezählt ab dem ersten Bild
BLINK_MS = 160.0  # Dauer eines Blinzelns
BLINK_GAP_MIN_MS = 2400.0  # Abstand bis zum nächsten Blinzeln: mindestens
BLINK_GAP_SPAN_MS = 3200.0  # und zufällig bis zu so viel länger
BREATH_PERIOD_MS = 950.0  # Atem: sin(t / 950) wie im Prototyp
MAX_STEP_S = 0.1  # längster Zeitschritt des Sprechens, wie im Prototyp

# Name der Emotion -> Sektor; je Sektor das `hi` (intensiv) und das `lo` (moderat)
# der Schlüsselbilder. `neutral` ist kein Sektor (None). Die Stärke kommt nicht aus
# dem Namen, sondern aus dem Arousal.
SECTOR_BY_NAME: Mapping[str, int | None] = MappingProxyType({
    "neutral": None,
    "begeisterung": 1, "freude": 1,
    "dankbarkeit": 2, "zufriedenheit": 2,
    "stress": 3, "unsicherheit": 3,
    "ueberrascht": 4, "verwundert": 4,
    "verzweiflung": 5, "traurigkeit": 5,
    "frustration": 6, "enttaeuschung": 6,
    "wut": 7, "aerger": 7,
    "hoffnung": 8, "neugierig": 8,
})
SECTOR_COUNT = 8


@dataclass(frozen=True)
class Utterance:
    """Eine Äußerung Novas: Sektor (1–8, None = neutral), Arousal in 0..1, Text."""

    sector: int | None
    arousal: float
    text: str


@dataclass
class Puppet:
    """Der Zustand der Puppe zwischen zwei Bildern.

    `start_s` ist die Zeit des ersten Bildes; Blinzeln, Atem und Takt zählen ab dort.
    `last_step_s` ist die Zeit des letzten Schritts. `blink_at_ms` ist der Beginn des
    laufenden Blinzelns oder None, `next_blink_ms` der frühestmögliche nächste.
    """

    start_s: float
    last_step_s: float
    animator: AnimatorState
    speech: SpeechState
    rng: random.Random
    next_blink_ms: float
    blink_at_ms: float | None


NEUTRAL_UTTERANCE = Utterance(None, 0.0, "")


def _check_now(now: float, where: str) -> None:
    """Wirft ValueError, wenn `now` keine endliche Zahl ist."""
    # ── Eingabe-Validierung ──
    is_number = isinstance(now, int | float) and not isinstance(now, bool)

    # ── Verarbeitung ──
    valid = is_number and math.isfinite(now)

    # ── Ausgabe-Verifikation ──
    if not valid:
        raise ValueError(f"{where}: Zeit {now!r} ist keine endliche Zahl")


def new_puppet(now: float, rng: random.Random) -> Puppet:
    """Eine Puppe in Ruhe zur Zeit `now`: neutrales Gesicht, kein Sprechen.

    Vorbedingung: `now` endliche Zahl in Sekunden, `rng` ein `random.Random`.
    Nachbedingung: Animator in Ruhe auf `NEUTRAL`, Sprechen still, das erste
    Blinzeln steht bei `FIRST_BLINK_MS` nach `now`.
    Fehlerfälle: ValueError bei ungültiger Zeit, TypeError ohne `random.Random`.
    """
    # ── Eingabe-Validierung ──
    _check_now(now, "new_puppet")
    if not isinstance(rng, random.Random):
        raise TypeError(f"new_puppet: Zufallsquelle ist kein random.Random: {type(rng).__name__}")

    # ── Verarbeitung ──
    puppet = Puppet(
        start_s=float(now),
        last_step_s=float(now),
        animator=start(NEUTRAL, float(now)),
        speech=SILENT,
        rng=rng,
        next_blink_ms=FIRST_BLINK_MS,
        blink_at_ms=None,
    )

    # ── Ausgabe-Verifikation ──
    if puppet.animator.time_s != puppet.start_s or puppet.speech.active:
        raise RuntimeError("new_puppet: Puppe nicht in Ruhe")
    return puppet


def puppet_cue(puppet: Puppet, utterance: Utterance, now: float) -> None:
    """Gibt der Puppe zur Zeit `now` eine neue Äußerung.

    Der Ausdruck wird neues Ziel: Brauen und Augen folgen sofort, der Mund mit
    Versatz (`set_target`). Ist der Text nicht leer, beginnt sein Sprechen zur selben
    Zeit. Beides geht vom sichtbaren Zustand aus weiter; ein neuer Text mitten im
    Sprechen ersetzt den alten ohne Sprung.
    Vorbedingung: `utterance` mit Sektor None oder 1–8, Arousal in 0..1, Text str;
    `now` nicht vor dem letzten Schritt oder der letzten Äußerung.
    Nachbedingung: Animator steht bei `now` mit dem neuen Ziel; bei Text ist das
    Sprechen aktiv und beginnt bei `now`.
    Fehlerfälle: TypeError oder ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(puppet, Puppet):
        raise TypeError(f"puppet_cue: keine Puppe: {type(puppet).__name__}")
    if not isinstance(utterance, Utterance):
        raise TypeError(f"puppet_cue: keine Utterance: {type(utterance).__name__}")
    sector = utterance.sector
    if sector is not None and (
        isinstance(sector, bool) or not isinstance(sector, int) or not 1 <= sector <= SECTOR_COUNT
    ):
        raise ValueError(f"puppet_cue: Sektor {sector!r} weder None noch 1–{SECTOR_COUNT}")
    arousal = utterance.arousal
    if isinstance(arousal, bool) or not isinstance(arousal, int | float) or not 0 <= arousal <= 1:
        raise ValueError(f"puppet_cue: Arousal {utterance.arousal!r} nicht in 0..1")
    if not isinstance(utterance.text, str):
        raise TypeError(f"puppet_cue: Text ist kein str: {type(utterance.text).__name__}")
    _check_now(now, "puppet_cue")
    earliest = max(puppet.last_step_s, puppet.animator.time_s)
    if now < earliest:
        raise ValueError(f"puppet_cue: Zeit {now} liegt vor {earliest}")

    # ── Verarbeitung ──
    target = face_target(0 if sector is None else sector, float(arousal))
    puppet.animator = set_target(puppet.animator, target, float(now))
    speaks = bool(utterance.text.strip())
    if speaks:
        puppet.speech = start_speech(puppet.speech, utterance.text, now * 1000.0)

    # ── Ausgabe-Verifikation ──
    if puppet.animator.time_s != now:
        raise RuntimeError(f"puppet_cue: Animator steht bei {puppet.animator.time_s}, nicht {now}")
    if speaks and (not puppet.speech.active or puppet.speech.start_ms != now * 1000.0):
        raise RuntimeError("puppet_cue: Sprechen nicht zur Zeit der Äußerung begonnen")


def _blink(puppet: Puppet, t_ms: float) -> float:
    """Das Blinzeln zur Zeit `t_ms` ab dem ersten Bild: 1 offen, 0 geschlossen.

    Wie im Prototyp: Ist der nächste Zeitpunkt überschritten, beginnt ein Blinzeln
    von `BLINK_MS`; ist es vorbei, fällt der nächste Zeitpunkt zufällig
    `BLINK_GAP_MIN_MS` bis `BLINK_GAP_MIN_MS + BLINK_GAP_SPAN_MS` später.
    Vorbedingung: `t_ms` endlich, nicht vor dem Beginn des laufenden Blinzelns.
    Nachbedingung: Rückgabe in 0..1; die Blinzelfelder der Puppe sind fortgeschrieben.
    Fehlerfälle: RuntimeError, wenn der Wert außerhalb 0..1 läge.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(t_ms):
        raise ValueError(f"_blink: Zeit {t_ms!r} nicht endlich")

    # ── Verarbeitung ──
    if puppet.blink_at_ms is None and t_ms > puppet.next_blink_ms:
        puppet.blink_at_ms = t_ms
    openness = 1.0
    if puppet.blink_at_ms is not None:
        q = (t_ms - puppet.blink_at_ms) / BLINK_MS
        if q >= 1:
            puppet.blink_at_ms = None
            puppet.next_blink_ms = t_ms + BLINK_GAP_MIN_MS + puppet.rng.random() * BLINK_GAP_SPAN_MS
        else:
            openness = abs(math.cos(q * math.pi))

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= openness <= 1.0:
        raise RuntimeError(f"_blink: Öffnung {openness!r} außerhalb 0..1")
    return openness


def puppet_step(puppet: Puppet, now: float) -> Pose:
    """Ein Bild der Puppe zur Zeit `now`.

    Reihenfolge wie im Prototyp: fällige Mundziele übernehmen und Feder fortschreiben,
    Blinzeln, Sprechschritt, Mund aus Emotion und Sprechen zusammenführen, Atem
    `sin(t / 950)` und Takt der Strichlage `floor(t / 110)`; `t` in ms ab dem ersten
    Bild. Der Zeitschritt des Sprechens ist auf `MAX_STEP_S` begrenzt.
    Vorbedingung: `now` endlich, nicht vor dem letzten Schritt oder der letzten Äußerung.
    Nachbedingung: eine Pose mit endlichen Kanälen, Blinzeln und Zunge in 0..1, Atem
    in −1..1, Takt ganze Zahl ≥ 0; die Puppe steht bei `now`.
    Fehlerfälle: TypeError ohne Puppe, ValueError bei ungültiger oder rückläufiger Zeit.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(puppet, Puppet):
        raise TypeError(f"puppet_step: keine Puppe: {type(puppet).__name__}")
    _check_now(now, "puppet_step")
    earliest = max(puppet.last_step_s, puppet.animator.time_s)
    if now < earliest:
        raise ValueError(f"puppet_step: Zeit {now} liegt vor {earliest}")

    # ── Verarbeitung ──
    t_ms = max(0.0, (now - puppet.start_s) * 1000.0)
    dt_s = min(now - puppet.last_step_s, MAX_STEP_S)
    puppet.animator = advance(puppet.animator, float(now))
    blink = _blink(puppet, t_ms)
    puppet.speech = speech_step(puppet.speech, now * 1000.0, dt_s)
    face, tongue = mouth_state_combine(puppet.animator.current, puppet.speech)
    pose = Pose(
        face=face,
        tongue=tongue,
        blink=blink,
        breath=math.sin(t_ms / BREATH_PERIOD_MS),
        boil_tick=math.floor(t_ms / BOIL_MS),
    )
    puppet.last_step_s = float(now)

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in (pose.tongue, pose.blink, pose.breath)):
        raise RuntimeError(f"puppet_step: Pose nicht endlich bei {now}")
    if pose.boil_tick < 0:
        raise RuntimeError(f"puppet_step: Takt {pose.boil_tick} negativ")
    return pose


def _sector_from_name(name: object) -> int | None:
    """Der Sektor zum Namen einer Emotion; None für `neutral` und jeden Fehler.

    Vorbedingung: keine — jeder Wert wird geprüft.
    Nachbedingung: Rückgabe None oder 1–8.
    Fehlerfälle: kein str oder ein unbekannter Name ergibt eine Error-Zeile und None.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(name, str):
        logger.error(f"Avatar: nova_emotion {name!r} ist kein Name, zeige Neutral")
        return None
    if name not in SECTOR_BY_NAME:
        logger.error(f"Avatar: nova_emotion '{name}' unbekannt, zeige Neutral")
        return None

    # ── Verarbeitung ──
    sector = SECTOR_BY_NAME[name]

    # ── Ausgabe-Verifikation ──
    if sector is not None and not 1 <= sector <= SECTOR_COUNT:
        raise RuntimeError(f"_sector_from_name: Sektor {sector!r} für '{name}' ungültig")
    return sector


def _arousal_from_value(value: object) -> float | None:
    """Das Arousal begrenzt auf 0..1; None, wenn es keine endliche Zahl ist.

    Vorbedingung: keine — jeder Wert wird geprüft.
    Nachbedingung: Rückgabe None oder eine Zahl in 0..1.
    Fehlerfälle: keine endliche Zahl ergibt eine Error-Zeile und None; außerhalb 0..1
    eine Warnung und den begrenzten Wert.
    """
    # ── Eingabe-Validierung ──
    is_number = isinstance(value, int | float) and not isinstance(value, bool)
    if not is_number or not math.isfinite(value):
        logger.error(f"Avatar: nova_arousal {value!r} keine endliche Zahl, zeige Neutral")
        return None

    # ── Verarbeitung ──
    clamped = max(0.0, min(1.0, float(value)))
    if clamped != value:
        logger.warning(f"Avatar: nova_arousal {value!r} außerhalb 0..1, begrenzt auf {clamped}")

    # ── Ausgabe-Verifikation ──
    if not 0.0 <= clamped <= 1.0:
        raise RuntimeError(f"_arousal_from_value: {clamped!r} außerhalb 0..1")
    return clamped


def utterance_from_turn(turn_data: Mapping) -> Utterance:
    """Die Äußerung aus einer Antwort an den Client.

    `nova_emotion` wird über `SECTOR_BY_NAME` zum Sektor, `nova_arousal` auf 0..1
    begrenzt, `antwort` ist der Text.
    Vorbedingung: keine — die Antwort kommt vom Server und wird ganz geprüft.
    Nachbedingung: Sektor None oder 1–8, Arousal in 0..1, Text str.
    Fehlerfälle (je eine Error-Zeile, kein Absturz): Fehlen `nova_emotion` oder
    `nova_arousal`, ist der Name unbekannt oder das Arousal keine Zahl, zeigt das
    Gesicht Neutral; fehlt `antwort` oder ist sie kein Text, bleibt der Mund still.
    Ist die Antwort kein Mapping, ist alles neutral und still.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(turn_data, Mapping):
        logger.error(f"Avatar: Antwort ist kein Mapping: {type(turn_data).__name__}")
        return NEUTRAL_UTTERANCE
    missing = [key for key in ("nova_emotion", "nova_arousal") if key not in turn_data]
    if missing:
        logger.error(f"Avatar: Antwort ohne {missing}, zeige Neutral")

    # ── Verarbeitung ──
    sector: int | None = None
    arousal = 0.0
    if not missing:
        sector = _sector_from_name(turn_data["nova_emotion"])
        checked = _arousal_from_value(turn_data["nova_arousal"])
        if checked is None:
            sector = None
        else:
            arousal = checked
    text = turn_data.get("antwort")
    if not isinstance(text, str):
        logger.error(f"Avatar: antwort {type(text).__name__} ist kein Text, der Mund bleibt still")
        text = ""
    result = Utterance(sector, arousal, text)

    # ── Ausgabe-Verifikation ──
    if result.sector is not None and not 1 <= result.sector <= SECTOR_COUNT:
        raise RuntimeError(f"utterance_from_turn: Sektor {result.sector!r} ungültig")
    if not 0.0 <= result.arousal <= 1.0:
        raise RuntimeError(f"utterance_from_turn: Arousal {result.arousal!r} außerhalb 0..1")
    return result
