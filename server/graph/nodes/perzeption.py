"""
Perzeption — Novas Wahrnehmung.

Analysiert den eingehenden User-Prompt auf drei Ebenen:
  Rational:       Was wird gesagt? Intent, Tone, Thema.
  Emotional:      Was wird gefuehlt? Emotion, Arousal.
  Psychologisch:  Was wird gebraucht? Modus, Stil, Beziehungsdynamik.

Laeuft VOR dem Router. Liefert ein vollstaendiges Bild des Prompts,
auf dessen Basis der Router Routing-Entscheidungen trifft.

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).

Phase-3-Output-Switch (PFAD2-PERZEPTION-FIX):
  rolle="user":      Werte landen in ``state["external"].emotion``.
  rolle="assistant": Werte landen in ``state["internal"].emotion``
                     (Novas eigene Wahrnehmung ihrer Antwort).
  ``emotions_vector`` wird hier nicht gesetzt — entsteht im EI-Calc.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime

from config import PROMPTS, get_node_config, redis_client
from graph.personality import InternalPersonality, Personality
from graph.reiz import reiz_text
from graph.state import ConversationState
from memory.session import format_session_turns_numbered, session_turns_retrieve
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.perzeption")

_ROLLE_NOVA: str = "assistant"


@dataclass
class Wahrnehmung:
    """Die acht klassifizierten Felder eines Perzeptions-Laufs.

    Zusammen gelesen, zusammen geschrieben, zusammen verworfen — deshalb eine
    Klasse und keine acht Variablen
    (`novaberg-lesson_l_klassen-statt-flache-keys.md`).

    **Die Defaults sind der Fallback.** Vorher standen die acht Standardwerte
    zweimal im Rumpf: einmal als `.get()`-Default beim Lesen, einmal im
    `except`-Zweig bei einem Parse-Fehler. Zwei Listen, die dasselbe bedeuten
    sollen, sind die Stelle, an der sie auseinanderlaufen. Jetzt ist
    `Wahrnehmung()` der Fallback, und es gibt nur eine Liste.

    `emotions_vector` steht hier bewusst **nicht**: Den setzt der EI-Calc aus
    dem Emotionsverlauf, nicht dieser Knoten.
    """

    intent:             str   = "smalltalk"
    tone:               str   = "sachlich"
    thema:              str   = ""
    emotion:            str   = "neutral"
    arousal:            float = 0.5
    modus:              str   = "alltag"
    sprach_stil:        str   = "neutral"
    beziehungs_dynamik: str   = "neutral"


def _arousal_lesen(roh: object) -> float:
    """Liest den Arousal-Wert und klemmt ihn auf [0, 1].

    Vorbedingung: `roh` ist der Wert aus dem Ergebnis, beliebigen Typs.
    Nachbedingung: Zahl in [0, 1].
    Fehlerfaelle: Ein nicht zahlbarer Wert nimmt 0.5. Der Rueckfall gilt genau
    diesem Feld — die uebrigen sieben bleiben, was das Modell geliefert hat.
    """
    # ── Verarbeitung ────────────────────────────
    try:
        return max(0.0, min(1.0, float(roh)))
    except (ValueError, TypeError):
        return 0.5


def _wahrnehmung_lesen(ergebnis: dict) -> Wahrnehmung:
    """Liest die acht Felder aus den drei Abschnitten des Modell-Ergebnisses.

    Vorbedingung: `ergebnis` ist das geparste JSON, auch ein leeres Dict.
    Nachbedingung: Wahrnehmung; fehlende Felder tragen die Defaults der
    Datenklasse — dieselben, die auch der Fallback benutzt.
    Fehlerfaelle: Keine eigenen; ein Parse-Fehler faellt beim Aufrufer an.
    """
    # ── Eingabe-Validierung ─────────────────────
    rational:      dict = ergebnis.get("rational", {})
    emotional:     dict = ergebnis.get("emotional", {})
    psychologisch: dict = ergebnis.get("psychologisch", {})

    # ── Ausgabe ─────────────────────────────────
    leer = Wahrnehmung()
    return Wahrnehmung(
        intent             = rational.get("intent",      leer.intent),
        tone               = rational.get("tone",        leer.tone),
        thema              = rational.get("thema",       leer.thema),
        emotion            = emotional.get("emotion",    leer.emotion),
        arousal            = _arousal_lesen(emotional.get("arousal", leer.arousal)),
        modus              = psychologisch.get("modus",              leer.modus),
        sprach_stil        = psychologisch.get("sprach_stil",        leer.sprach_stil),
        beziehungs_dynamik = psychologisch.get("beziehungs_dynamik",
                                              leer.beziehungs_dynamik),
    )


def _eingabe_waehlen(state: ConversationState, rolle: str) -> str:
    """Waehlt den zu analysierenden Text nach Rolle.

    Vorbedingung: `rolle` ist gesetzt.
    Nachbedingung: Novas Antwort bei der Nova-Rolle, sonst der Reiz dieses
    Durchlaufs — die Aeusserung des Menschen oder, auf einem Impuls-Turn,
    Novas eigener Gedanke.
    Fehlerfaelle: Keine — ein fehlendes Feld ergibt eine leere Zeichenkette,
    und die Laenge steht in der Log-Zeile des Aufrufers.
    """
    # ── Ausgabe ─────────────────────────────────
    if rolle == _ROLLE_NOVA:
        return state.get("response", "")
    return reiz_text(state)


def _ziel_personality(state: ConversationState, rolle: str) -> Personality:
    """Holt das Zielobjekt der Rolle und legt es an, wenn es fehlt.

    **Ein vorhandenes Objekt wird weiterbenutzt, nicht ersetzt.** Andere Knoten
    halten Verweise darauf; ein Austausch waere von aussen nicht sichtbar und
    wuerde ihre Sicht einfrieren.

    Vorbedingung: `rolle` ist gesetzt.
    Nachbedingung: Das Objekt liegt im State und wird zurueckgegeben.
    Fehlerfaelle: Keine.
    """
    # ── Verarbeitung ────────────────────────────
    schluessel: str = "internal" if rolle == _ROLLE_NOVA else "external"
    ziel = state.get(schluessel)

    if ziel is None:
        ziel = InternalPersonality() if rolle == _ROLLE_NOVA else Personality()
        state[schluessel] = ziel

    # ── Ausgabe ─────────────────────────────────
    return ziel


def _session_kontext_laden(user_id: str, character_id: str) -> str | None:
    """Holt die letzten Turns als nummerierten Kontextblock.

    Vorbedingung: keine — ohne `user_id` wird nicht gelesen.
    Nachbedingung: Der formatierte Verlauf oder None.
    Fehlerfaelle: Scheitert das Lesen, wird gewarnt und None zurueckgegeben;
    die Perzeption laeuft ohne Kontext weiter statt abzubrechen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        roh: list[dict] = session_turns_retrieve(
            redis_client, user_id, character_id,
        )
        verlauf: str | None = format_session_turns_numbered(roh, max_turns=5) or None
    except Exception as fehler:
        logger.warning(
            f"{type(fehler).__name__}: Perzeption: Session-Kontext konnte nicht "
            f"geladen werden"
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if verlauf:
        logger.info("Perzeption: Session-Kontext geladen (nummeriert)")
    return verlauf


def _wahrnehmung_erheben(eingabe_text: str, system_prompt: str) -> Wahrnehmung:
    """Fragt das Sprachmodell und liest sein Ergebnis.

    Vorbedingung: `system_prompt` ist gebaut.
    Nachbedingung: Wahrnehmung — aus dem Ergebnis oder, bei einem Parse-Fehler,
    die Defaults der Datenklasse.
    Fehlerfaelle: Ein unlesbares Ergebnis wird gewarnt und faellt auf die
    Defaults. Das ist derselbe Zustand wie ein Ergebnis mit leeren Abschnitten,
    und genau deshalb gibt es dafuer nur eine Liste von Werten.
    """
    # ── Verarbeitung ────────────────────────────
    node_cfg = get_node_config("perzeption")
    auftrag = ChatRequest(
        messages          = [{"role": "user", "content": eingabe_text}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "perzeption",
    )

    try:
        antwort = model_service.chat.submit_sync(auftrag)
        return _wahrnehmung_lesen(antwort.parsed)
    except (json.JSONDecodeError, KeyError) as fehler:
        logger.warning(
            f"{type(fehler).__name__}: Perzeption: JSON-Parsing fehlgeschlagen, "
            f"Fallback auf die Standardwerte"
        )
        return Wahrnehmung()


def _wahrnehmung_schreiben(ziel: Personality, wahr: Wahrnehmung) -> None:
    """Schreibt die acht Felder in die Emotion des Zielobjekts.

    `emotions_vector` bleibt unberuehrt — den setzt der EI-Calc.

    Vorbedingung: `ziel` traegt eine Emotion.
    Nachbedingung: Die acht Felder stehen darin.
    Fehlerfaelle: Keine.
    """
    ziel.emotion.intent               = wahr.intent
    ziel.emotion.tone                 = wahr.tone
    ziel.emotion.prompt_topic         = wahr.thema
    ziel.emotion.emotion              = wahr.emotion
    ziel.emotion.arousal              = wahr.arousal
    ziel.emotion.mode                 = wahr.modus
    ziel.emotion.language_style       = wahr.sprach_stil
    ziel.emotion.relationship_dynamic = wahr.beziehungs_dynamik


def _build_system_prompt(today: str, session_turns: str | None = None, rolle: str = "user") -> str:
    """Baut den Perzeption-System-Prompt aus [BLOCKNAME]-Bloecken zusammen.

    Reihenfolge nach Primacy/Recency (nova-01-t-d):
    OBEN:   [IDENTITAET] → [AUFGABE]
    MITTE:  [KONTEXT] (nur wenn Session-Turns vorhanden)
    UNTEN:  [REGELN] (direkt vor der User-Message)
    """
    task_key: str = "perzeption.task" if rolle == "user" else "perzeption.assistant_task"

    bloecke: list[str] = [
        PROMPTS["perzeption.identity"].format(today=today),
        PROMPTS[task_key],
    ]

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Die folgenden Gespraechsverlaeufe sind Hintergrund fuer "
            "Pronomen-Aufloesung, Emotions-Kontext und Themen-Kontinuitaet. "
            "Hoehere Nummern sind aktueller.\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["perzeption.rules"])

    return "\n\n".join(bloecke)


def perceive(
    state: ConversationState,
) -> ConversationState:
    """Analysiert den User-Prompt oder die Nova-Antwort und schreibt die
    klassifizierten EI-Dimensionen in die rollen-spezifische Personality.

    Vorbedingung: `perzeption_rolle` ist gesetzt oder fehlt (dann "user").
    Nachbedingung: Die acht Felder stehen in `external.emotion` oder
    `internal.emotion`; `emotions_vector` bleibt unberuehrt.
    Fehlerfaelle: Ein unlesbares Modell-Ergebnis und ein ausgefallener
    Session-Kontext werden gewarnt; der Knoten bricht nicht ab.
    """
    # ── Eingabe-Validierung ─────────────────────
    rolle:        str = state.get("perzeption_rolle", "user")
    eingabe_text: str = _eingabe_waehlen(state, rolle)
    logger.info(f"Perzeption: rolle={rolle}, eingabe_laenge={len(eingabe_text)}")

    ziel: Personality = _ziel_personality(state, rolle)

    # ── Verarbeitung ────────────────────────────
    system_prompt: str = _build_system_prompt(
        datetime.now().strftime("%d.%m.%Y, %H:%M Uhr"),
        _session_kontext_laden(
            state.get("user_id", ""), state.get("character_id", ""),
        ),
        rolle = rolle,
    )
    logger.info(f"Perzeption: System-Prompt:\n{system_prompt}")

    wahr: Wahrnehmung = _wahrnehmung_erheben(eingabe_text, system_prompt)

    # ── Ausgabe-Verifikation ────────────────────
    _wahrnehmung_schreiben(ziel, wahr)
    logger.info(
        f"Perzeption: rolle={rolle}, "
        f"ziel={'internal' if rolle == _ROLLE_NOVA else 'external'} | "
        f"rational=({wahr.intent}, {wahr.tone}, {wahr.thema}) | "
        f"emotional=({wahr.emotion}, a={wahr.arousal:.2f}) | "
        f"psychologisch=({wahr.modus}, {wahr.sprach_stil}, "
        f"{wahr.beziehungs_dynamik})"
    )
    return state
