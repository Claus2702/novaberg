"""Die Puppe: Leerlauf, Feder, Sprechen, Lidschlag, Atem und Takt in einem Bild.

Hier laufen die Fäden zusammen. Die Puppe hält eine `IdleLogic`; jeder Schritt
(`puppet_step`) gibt ihr den Blick, den die Feder gerade zeigt, nimmt ihre Ziele
und führt die Feder je Kanalgruppe dorthin — Blick ω 35, Pupille ω 5, alle übrigen
Kanäle das ω des Gesichts aus dem Leerlauf, ohne Mundversatz. Das Lid ist das des
Leerlaufs. In der Antwort liegt die Sprechschicht über dem Mund.

Eine Antwort (`puppet_cue`) geht mit der Dauer ihrer Wiedergabe an den Leerlauf;
gesprochen wird sie erst, wenn der Leerlauf sie beginnen lässt — nach dem
Einatmen oder, wenn sie eine laufende ablöst, sofort. Ihr Sprechen dauert genau
die gemeldete Dauer, so endet es, wo der Leerlauf die Wiedergabe enden lässt.
Verlässt der Leerlauf die Antwort vorher, etwa bei einem neuen Turn, endet es dort.
Die übrigen Ereignisse gibt `puppet_event` weiter.

Das Modul liest keine Uhr. Zeit kommt als Parameter in Sekunden, von einer
einzigen Uhr für alles; der Leerlauf zählt in ms ab dem ersten Bild. Sein
Startwert kommt aus dem `random.Random`, das der Aufrufer übergibt.

`utterance_from_turn` setzt die Antwort an den Client in eine `Utterance` um:
der Name der Emotion wird zum Sektor über die Namen der Schlüsselbilder, das
Arousal wird begrenzt, der Text bleibt, wie er ist.
"""

import logging
import math
import random
from collections.abc import Mapping
from dataclasses import dataclass, fields, replace
from types import MappingProxyType

from avatar.animator import spring_step_each
from avatar.compose import BOIL_MS
from avatar.face import NEUTRAL, FaceState
from avatar.idle import (
    AnswerArrives,
    IdleFrame,
    IdleLogic,
    ImpulseThinks,
    PixieJob,
    TurnBegins,
    TurnFailed,
)
from avatar.pose import Pose
from avatar.speech import (
    SILENT,
    SpeechState,
    mouth_state_combine,
    speech_step,
    speech_timeline,
    start_speech,
    text_to_phonemes,
)

logger = logging.getLogger(__name__)

BREATH_PERIOD_MS = 950.0  # Atem: sin(t / 950) wie im Prototyp
MAX_STEP_S = 0.1  # längster Zeitschritt des Sprechens, wie im Prototyp
GAZE_OMEGA = 35.0  # 1/s: eine Sakkade erreicht 95 % nach 0,14 s
PUPIL_OMEGA = 5.0  # 1/s
# Die Kanäle mit eigenem ω; alle übrigen folgen dem ω des Gesichts aus dem Leerlauf.
GROUP_OMEGA: Mapping[str, float] = MappingProxyType({
    "gaze_x": GAZE_OMEGA, "gaze_y": GAZE_OMEGA, "pupil_size": PUPIL_OMEGA,
})
# Ereignisse, die `puppet_event` weitergibt; die Antwort geht über `puppet_cue`.
FORWARDED_EVENTS = (TurnBegins, TurnFailed, ImpulseThinks, PixieJob)
SEED_BITS = 32  # Startwert des Leerlaufs: so breit wie der Zustand von mulberry32

_CHANNELS: tuple[str, ...] = tuple(f.name for f in fields(FaceState))
_STILL = FaceState(**dict.fromkeys(_CHANNELS, 0.0))

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
# Sektor -> ein Name, wie der Leerlauf ihn erwartet: der erste der Tabelle oben. Beide
# Namen eines Sektors führen im Leerlauf zum selben Sektor.
NAME_BY_SECTOR: Mapping[int | None, str] = MappingProxyType(
    {sector: name for name, sector in reversed(SECTOR_BY_NAME.items())}
)


@dataclass(frozen=True)
class Utterance:
    """Eine Äußerung Novas: Sektor (1–8, None = neutral), Arousal in 0..1, Text."""

    sector: int | None
    arousal: float
    text: str


@dataclass
class Puppet:
    """Der Zustand der Puppe zwischen zwei Bildern.

    `start_s` ist die Zeit des ersten Bildes; Leerlauf, Atem und Takt zählen ab dort.
    `last_step_s` ist die Zeit des letzten Schritts. `face` und `velocity` sind Lage
    und Geschwindigkeit der Feder (ohne Sprechschicht), `targets` die Ziele, denen sie
    im letzten Schritt folgte, `frame` das letzte Bild des Leerlaufs. `texts` hält den
    Text jeder Antwort, die noch nicht gesprochen wird, nach ihrer Zeit im Leerlauf;
    `speaking_at_ms` ist die Zeit der zuletzt begonnenen.
    """

    start_s: float
    last_step_s: float
    face: FaceState
    velocity: FaceState
    targets: FaceState
    frame: IdleFrame | None
    speech: SpeechState
    idle: IdleLogic
    texts: dict[float, str]
    speaking_at_ms: float | None


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


def _logic_ms(puppet: Puppet, now: float) -> float:
    """Die Zeit `now` in Sekunden als Zeit des Leerlaufs: ms ab dem ersten Bild.

    Vorbedingung: `now` geprüft, nicht vor dem letzten Schritt.
    Nachbedingung: eine endliche Zahl >= 0.
    Fehlerfälle: RuntimeError, wenn die Zeit vor dem ersten Bild läge.
    """
    # ── Eingabe-Validierung ──
    if now < puppet.start_s:
        raise RuntimeError(f"_logic_ms: Zeit {now} vor dem ersten Bild {puppet.start_s}")

    # ── Verarbeitung ──
    t_ms = (now - puppet.start_s) * 1000.0

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(t_ms) or t_ms < 0:
        raise RuntimeError(f"_logic_ms: Zeit des Leerlaufs {t_ms!r} ungültig")
    return t_ms


def _check_not_before_last_step(puppet: Puppet, now: float, where: str) -> None:
    """Wirft TypeError ohne Puppe, ValueError bei ungültiger oder rückläufiger Zeit."""
    # ── Eingabe-Validierung ──
    if not isinstance(puppet, Puppet):
        raise TypeError(f"{where}: keine Puppe: {type(puppet).__name__}")
    _check_now(now, where)

    # ── Ausgabe-Verifikation ──
    if now < puppet.last_step_s:
        raise ValueError(f"{where}: Zeit {now} liegt vor {puppet.last_step_s}")


def new_puppet(now: float, rng: random.Random) -> Puppet:
    """Eine Puppe in Ruhe zur Zeit `now`: neutral, still, der Leerlauf im Rauschen.

    Der Startwert des Leerlaufs ist eine Ziehung von `SEED_BITS` Bit aus `rng`: Mit
    demselben `rng` plant die Puppe gleich, mit einem anderen anders.
    Vorbedingung: `now` endliche Zahl in Sekunden, `rng` ein `random.Random`.
    Nachbedingung: Feder in Ruhe auf `NEUTRAL`, Sprechen still, keine Antwort wartet;
    der Leerlauf beginnt ohne Ereignis im Rauschen.
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
        face=NEUTRAL,
        velocity=_STILL,
        targets=NEUTRAL,
        frame=None,
        speech=SILENT,
        idle=IdleLogic(rng.getrandbits(SEED_BITS)),
        texts={},
        speaking_at_ms=None,
    )

    # ── Ausgabe-Verifikation ──
    if puppet.face is not NEUTRAL or puppet.speech.active or puppet.texts:
        raise RuntimeError("new_puppet: Puppe nicht in Ruhe")
    return puppet


def _playback_ms(text: str) -> float:
    """Die Dauer der Wiedergabe eines Texts in ms: das Ende seiner Zeitachse; 0 ohne Text.

    Vorbedingung: `text` ist ein str.
    Nachbedingung: 0 für einen leeren Text, sonst eine endliche Zahl > 0 — dieselbe
    Dauer, die `start_speech` für den Text ansetzt.
    Fehlerfälle: Fehler der Zeitachse (etwa ein Text ohne Laute) gehen durch.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(text, str):
        raise TypeError(f"_playback_ms: Text ist kein str: {type(text).__name__}")

    # ── Verarbeitung ──
    duration = speech_timeline(text_to_phonemes(text))[1] if text.strip() else 0.0

    # ── Ausgabe-Verifikation ──
    if not math.isfinite(duration) or duration < 0:
        raise RuntimeError(f"_playback_ms: Dauer {duration!r} ungültig")
    return duration


def puppet_cue(puppet: Puppet, utterance: Utterance, now: float) -> None:
    """Eine Antwort trifft zur Zeit `now` ein: sie geht an den Leerlauf, ihr Text wartet.

    Die Dauer ihrer Wiedergabe ist das Ende der Zeitachse des Texts (0 ohne Text);
    mit ihr, dem Namen der Emotion und dem Arousal geht die Antwort als
    `AnswerArrives` an den Leerlauf. Gesprochen wird der Text erst in dem Schritt,
    in dem der Leerlauf diese Antwort beginnen lässt (`puppet_step`); eine zweite
    Antwort im Einatmen ersetzt die wartende, eine Antwort in der Antwort löst ab.
    Vorbedingung: `utterance` mit Sektor None oder 1–8, Arousal in 0..1, Text str;
    `now` nicht vor dem letzten Schritt und nicht die Zeit der zuletzt begonnenen
    Antwort — der Leerlauf löste mit derselben Zeit ab, und die Puppe spräche den
    alten Text mit der Dauer des neuen.
    Nachbedingung: die Antwort steht im Leerlauf zur Zeit `now`, ihr Text unter
    dieser Zeit in `texts`; Feder und Sprechen sind unberührt.
    Fehlerfälle: TypeError oder ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    _check_not_before_last_step(puppet, now, "puppet_cue")
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
    at_ms = _logic_ms(puppet, now)
    if at_ms == puppet.speaking_at_ms:
        raise ValueError(f"puppet_cue: bei {at_ms} ms hat schon eine Antwort begonnen")

    # ── Verarbeitung ──
    text = utterance.text
    answer = AnswerArrives(at_ms, NAME_BY_SECTOR[sector], float(arousal), _playback_ms(text))
    puppet.idle.post(answer)
    puppet.texts[at_ms] = text

    # ── Ausgabe-Verifikation ──
    if puppet.texts.get(at_ms) is not text:
        raise RuntimeError(f"puppet_cue: Text der Antwort bei {at_ms} ms nicht abgelegt")


def puppet_event(puppet: Puppet, event_type: type, now: float, **data: object) -> None:
    """Gibt ein Ereignis des Clients zur Zeit `now` an den Leerlauf weiter.

    Turn beginnt (`TurnBegins`), Turn gescheitert (`TurnFailed`), Impuls
    (`ImpulseThinks`, `phase=`) und Pixies Auftrag (`PixieJob`, `phase=`, `track=`,
    `job_kind=`, wo vorhanden `emotion=`, `arousal=`). Die Zeit des Ereignisses setzt
    die Puppe aus `now`: ms ab ihrem ersten Bild. Eine Antwort geht über `puppet_cue`.
    Vorbedingung: `event_type` einer aus `FORWARDED_EVENTS`; `data` seine Felder
    ohne `at_ms`; `now` nicht vor dem letzten Schritt.
    Nachbedingung: das Ereignis steht im Leerlauf zur Zeit `now`. Dass es eingereiht
    ist, prüft der Leerlauf selbst beim Einreihen; hier geprüft wird die Zeit, die es
    trägt — die Puppe setzt sie als erstes Feld, wie jedes Ereignis des Leerlaufs es
    heute führt.
    Fehlerfälle: TypeError bei einem anderen Typ oder falschen Feldern, ValueError bei
    ungültiger oder rückläufiger Zeit, RuntimeError, wenn das Ereignis eine andere
    Zeit trägt; was der Leerlauf abweist, geht durch.
    """
    # ── Eingabe-Validierung ──
    _check_not_before_last_step(puppet, now, "puppet_event")
    if event_type not in FORWARDED_EVENTS:
        raise TypeError(f"puppet_event: {event_type!r} ist kein weitergegebenes Ereignis")
    if "at_ms" in data:
        raise TypeError("puppet_event: die Zeit kommt aus now, nicht aus at_ms")

    # ── Verarbeitung ──
    at_ms = _logic_ms(puppet, now)
    event = event_type(at_ms, **data)
    puppet.idle.post(event)

    # ── Ausgabe-Verifikation ──
    if event.at_ms != at_ms:
        raise RuntimeError(f"puppet_event: {type(event).__name__} trägt {event.at_ms!r} "
                           f"statt der Zeit {at_ms} ms")


def _omegas(face_omega: float) -> dict[str, float]:
    """ω je Kanal: Blick und Pupille aus `GROUP_OMEGA`, alle übrigen `face_omega`.

    Vorbedingung: `face_omega` endlich und positiv (aus dem Leerlauf).
    Nachbedingung: ein ω für jeden Kanal von `FaceState`.
    Fehlerfälle: ValueError bei einem ungültigen ω des Gesichts.
    """
    # ── Eingabe-Validierung ──
    if not math.isfinite(face_omega) or face_omega <= 0:
        raise ValueError(f"_omegas: ω des Gesichts {face_omega!r} ungültig")

    # ── Verarbeitung ──
    omegas = dict.fromkeys(_CHANNELS, float(face_omega)) | dict(GROUP_OMEGA)

    # ── Ausgabe-Verifikation ──
    if len(omegas) != len(_CHANNELS):
        raise RuntimeError(f"_omegas: {len(omegas)} statt {len(_CHANNELS)} Kanäle")
    return omegas


def _begin_speaking(puppet: Puppet, frame: IdleFrame, now: float) -> None:
    """Beginnt das Sprechen, wenn der Leerlauf in diesem Schritt eine Antwort beginnen lässt.

    Eine Antwort beginnt, wenn `frame.answer_at_ms` gesetzt ist und nicht die zuletzt
    begonnene nennt — nach dem Einatmen oder als Ablösung einer laufenden. Gesprochen
    wird der Text dieser Antwort ab `now`; ältere wartende Texte entfallen, ihre
    Antworten hat der Leerlauf ersetzt oder verworfen. Beginnt eine Antwort ohne Text,
    während gesprochen wird, endet das Sprechen in diesem Schritt — auf demselben Weg
    wie in `_end_speaking`, ohne Sprung; ihre Wiedergabe dauert 0 ms.
    Vorbedingung: das Bild des Leerlaufs zu `now`.
    Nachbedingung: hat eine Antwort mit Text begonnen, spricht die Puppe sie ab `now`;
    hat eine ohne Text begonnen, ist das Sprechen inaktiv.
    Fehlerfälle: RuntimeError, wenn der Leerlauf eine Antwort beginnt, deren Text die
    Puppe nicht hält.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(frame, IdleFrame):
        raise TypeError(f"_begin_speaking: kein IdleFrame: {type(frame).__name__}")
    at_ms = frame.answer_at_ms
    begins = at_ms is not None and at_ms != puppet.speaking_at_ms
    if begins and at_ms not in puppet.texts:
        raise RuntimeError(f"_begin_speaking: Antwort bei {at_ms} ms ohne Text")

    # ── Verarbeitung ──
    text = ""
    if begins:
        text = puppet.texts.pop(at_ms)
        puppet.texts = {t: kept for t, kept in puppet.texts.items() if t > at_ms}
        puppet.speaking_at_ms = at_ms
    if text.strip():
        puppet.speech = start_speech(puppet.speech, text, now * 1000.0)
    elif begins and puppet.speech.active:
        puppet.speech = replace(puppet.speech, active=False)

    # ── Ausgabe-Verifikation ──
    if text.strip() and (not puppet.speech.active or puppet.speech.start_ms != now * 1000.0):
        raise RuntimeError("_begin_speaking: Sprechen nicht mit der Antwort begonnen")
    if begins and not text.strip() and puppet.speech.active:
        raise RuntimeError("_begin_speaking: Antwort mit leerem Text, altes Sprechen läuft")


def _end_speaking(puppet: Puppet, frame: IdleFrame) -> None:
    """Beendet das Sprechen, wenn der Leerlauf die Antwort vor dem Ende der Wiedergabe verlässt.

    Ein neuer Turn unterbricht jeden Zustand, auch die Antwort; die Sprechschicht gehört
    in die Antwort. Das Sprechen endet auf demselben Weg wie an seinem regulären Ende:
    Die Äußerung wird inaktiv, Kanäle und Sprechanteil behalten Lage und Geschwindigkeit
    und laufen über ihre Federn zur Ruhe aus — ohne Sprung.
    Vorbedingung: das Bild des Leerlaufs zu diesem Schritt.
    Nachbedingung: außerhalb der Antwort ist das Sprechen inaktiv.
    Fehlerfälle: TypeError ohne IdleFrame.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(frame, IdleFrame):
        raise TypeError(f"_end_speaking: kein IdleFrame: {type(frame).__name__}")
    left_answer = frame.answer_at_ms is None

    # ── Verarbeitung ──
    if left_answer and puppet.speech.active:
        puppet.speech = replace(puppet.speech, active=False)

    # ── Ausgabe-Verifikation ──
    if left_answer and puppet.speech.active:
        raise RuntimeError("_end_speaking: Sprechen außerhalb der Antwort")


def puppet_step(puppet: Puppet, now: float) -> Pose:
    """Ein Bild der Puppe zur Zeit `now`.

    Reihenfolge wie im Referenzgenerator: zuerst der Schritt des Leerlaufs mit dem
    Blick, den die Feder vor dem Schritt zeigt; beginnt er eine Antwort, beginnt ihr
    Sprechen (ohne Text endet ein laufendes), verlässt er die Antwort vor dem Ende der
    Wiedergabe, endet es. Dann die
    Feder je Kanalgruppe zu seinen Zielen (`spring_step_each`, ω aus `_omegas`), der
    Sprechschritt, der Mund aus Feder und Sprechen (`mouth_state_combine`), das Lid
    des Leerlaufs, Atem `sin(t / 950)` und Takt der Strichlage `floor(t / 110)`; `t`
    in ms ab dem ersten Bild. Der Zeitschritt des Sprechens ist auf `MAX_STEP_S`
    begrenzt, die Feder rechnet exakt über die ganze Spanne.
    Vorbedingung: `now` endlich, nicht vor dem letzten Schritt.
    Nachbedingung: eine Pose mit endlichen Kanälen, Lid und Zunge in 0..1, Atem in
    −1..1, Takt ganze Zahl ≥ 0; das Lid ist das des Leerlaufs; die Puppe steht bei `now`.
    Fehlerfälle: TypeError ohne Puppe, ValueError bei ungültiger oder rückläufiger Zeit.
    """
    # ── Eingabe-Validierung ──
    _check_not_before_last_step(puppet, now, "puppet_step")

    # ── Verarbeitung ──
    t_ms = _logic_ms(puppet, now)
    dt_s = now - puppet.last_step_s
    frame = puppet.idle.step(t_ms, puppet.face.gaze_x, puppet.face.gaze_y)
    _begin_speaking(puppet, frame, now)
    _end_speaking(puppet, frame)
    puppet.face, puppet.velocity = spring_step_each(
        puppet.face, puppet.velocity, frame.targets, _omegas(frame.face_omega), dt_s)
    puppet.targets, puppet.frame = frame.targets, frame
    puppet.speech = speech_step(puppet.speech, now * 1000.0, min(dt_s, MAX_STEP_S))
    face, tongue = mouth_state_combine(puppet.face, puppet.speech)
    pose = Pose(
        face=face,
        tongue=tongue,
        blink=frame.lid_open,
        breath=math.sin(t_ms / BREATH_PERIOD_MS),
        boil_tick=math.floor(t_ms / BOIL_MS),
    )
    puppet.last_step_s = float(now)

    # ── Ausgabe-Verifikation ──
    if not all(math.isfinite(v) for v in (pose.tongue, pose.blink, pose.breath)):
        raise RuntimeError(f"puppet_step: Pose nicht endlich bei {now}")
    if not 0.0 <= pose.blink <= 1.0:
        raise RuntimeError(f"puppet_step: Lid {pose.blink} außerhalb 0..1")
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
