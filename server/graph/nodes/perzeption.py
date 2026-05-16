"""
Perzeption — Novas Wahrnehmung.

Analysiert den eingehenden User-Prompt auf drei Ebenen:
  Rational:       Was wird gesagt? Intent, Tone, Thema.
  Emotional:      Was wird gefuehlt? Emotion, Arousal.
  Psychologisch:  Was wird gebraucht? Modus, Stil, Beziehungsdynamik.

Laeuft VOR dem Router. Liefert ein vollstaendiges Bild des Prompts,
auf dessen Basis der Router Routing-Entscheidungen trifft.

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging
from datetime import datetime

from graph.state import ConversationState
from config import redis_client, get_node_config, PROMPTS
from memory.session import session_turns_retrieve, format_session_turns_numbered
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.perzeption")


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
    """Analysiert den User-Prompt auf rationaler, emotionaler und psychologischer Ebene."""

    rolle: str = state.get("perzeption_rolle", "user")

    # PFAD2-PERZEPTION-FIX Phase 2: Input-Switch nach Rolle. Bei
    # "assistant" wird Novas finale Antwort analysiert, sonst der
    # User-Prompt.
    if rolle == "assistant":
        eingabe_text: str = state.get("response", "")
    else:
        eingabe_text = state.get("user_prompt", "")

    logger.info(
        f"Perzeption: rolle={rolle}, eingabe_laenge={len(eingabe_text)}"
    )

    today: str = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr")

    # ── Session-Kontext laden (leichtgewichtig, Redis-Read) ──
    session_turns: str | None = None
    user_id: str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")
    if user_id:
        try:
            raw_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(raw_turns, max_turns=5) or None
            if session_turns:
                logger.info("Perzeption: Session-Kontext geladen (nummeriert)")
        except Exception as e:
            logger.warning(f"Perzeption: Session-Kontext konnte nicht geladen werden: {e}")

    system_prompt: str = _build_system_prompt(today, session_turns, rolle=rolle)

    logger.info(f"Perzeption: System-Prompt:\n{system_prompt}")

    node_cfg = get_node_config("perzeption")
    provider = get_chat_provider()
    antwort  = provider.chat(
        messages = [
            {"role": "user", "content": eingabe_text},
        ],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        format_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "perzeption",
    )

    try:
        ergebnis: dict = json.loads(antwort.content)

        rational:       dict = ergebnis.get("rational", {})
        emotional:      dict = ergebnis.get("emotional", {})
        psychologisch:  dict = ergebnis.get("psychologisch", {})

        # Rational
        intent: str = rational.get("intent", "smalltalk")
        tone:   str = rational.get("tone", "sachlich")
        thema:  str = rational.get("thema", "")

        state["intent"]       = intent
        state["tone"]         = tone
        state["prompt_thema"] = thema

        # Emotional
        emotion: str = emotional.get("emotion", "neutral")
        state["current_emotion"] = emotion

        raw_arousal = emotional.get("arousal", 0.5)
        try:
            arousal: float = max(0.0, min(1.0, float(raw_arousal)))
        except (ValueError, TypeError):
            arousal = 0.5
        state["current_arousal"] = arousal

        # Psychologisch
        modus:               str = psychologisch.get("modus", "alltag")
        sprach_stil:         str = psychologisch.get("sprach_stil", "neutral")
        beziehungs_dynamik:  str = psychologisch.get("beziehungs_dynamik", "neutral")

        state["gespraechs_modus"]    = modus
        state["sprach_stil"]         = sprach_stil
        state["beziehungs_dynamik"]  = beziehungs_dynamik

    except (json.JSONDecodeError, KeyError) as fehler:
        logger.warning(f"Perzeption: JSON-Parsing fehlgeschlagen ({fehler}), Fallback")

        intent             = "smalltalk"
        tone               = "sachlich"
        thema              = ""
        emotion            = "neutral"
        arousal            = 0.5
        modus              = "alltag"
        sprach_stil        = "neutral"
        beziehungs_dynamik = "neutral"

        state["intent"]              = intent
        state["tone"]                = tone
        state["prompt_thema"]        = thema
        state["current_emotion"]     = emotion
        state["current_arousal"]     = arousal
        state["gespraechs_modus"]    = modus
        state["sprach_stil"]         = sprach_stil
        state["beziehungs_dynamik"]  = beziehungs_dynamik

    logger.info(
        f"Perzeption: rational=({intent}, {tone}, {thema}) | "
        f"emotional=({emotion}, a={arousal:.2f}) | "
        f"psychologisch=({modus}, {sprach_stil}, {beziehungs_dynamik})"
    )

    return state
