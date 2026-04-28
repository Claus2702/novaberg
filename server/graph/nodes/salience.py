"""
Salienz Node — Reiner Entscheider.

Analysiert den Gespraechs-Turn und bewertet emotionale Salienz,
Themen, Gedaechtnistyp und Dimension. 8 Dimensionen, kein kern.

SCHREIBT NICHT IN DIE DB. Legt pending_writes fuer KZG an
(ohne Embedding, ohne kern — das uebernimmt der KZG-Agent).

Fakten-Extraktion (Chat 27) und Verdichtung/kern (Chat 29) entfernt.
Fakten -> WissensAgent (Epic 11 Phase 2).
Verdichtung -> KZG-Agent (Chat 29).

Entscheider-Arbeiter-Trennung (A1.1):
  Salienz -> pending_writes -> Dispatcher -> KZG-Agent

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging

import redis

from graph.state import ConversationState
from config import get_node_config, PROMPTS
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.salience")


def _prompt_segmentieren(prompt: str) -> list[str]:
    """
    Zerlegt einen Prompt in semantische Einheiten.
    Gibt eine Liste von Segment-Texten zurueck.
    Bei einfachen Prompts (1 Segment) wird der Original-Prompt zurueckgegeben.
    """

    # Kurze Prompts brauchen keine Segmentierung
    if len(prompt) < 60 or "." not in prompt:
        return [prompt]

    try:
        node_cfg = get_node_config("salienz")
        provider = get_chat_provider()
        antwort  = provider.chat(
            messages = [
                {"role": "user", "content": prompt},
            ],
            system            = "\n\n".join([
                PROMPTS["salienz_segment.identity"],
                PROMPTS["salienz_segment.task"],
                PROMPTS["salienz_segment.rules"],
            ]),
            temperature       = node_cfg.get("temperature", 0.05),
            format_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "salienz/segment",
        )

        raw: str = antwort.content
        logger.debug(f"Salienz RAW: '{antwort.content[:500]}'")
        parsed = json.loads(raw)

        # JSON koennte ein Array oder ein Objekt mit Array sein
        if isinstance(parsed, list):
            segmente: list[str] = [s.get("segment", "") for s in parsed if s.get("segment")]
        elif isinstance(parsed, dict) and "segments" in parsed:
            segmente = [s.get("segment", "") for s in parsed["segments"] if s.get("segment")]
        else:
            return [prompt]

        if not segmente:
            return [prompt]

        if len(segmente) == 1:
            return [prompt]  # Original beibehalten, kein Rewrite

        logger.info(f"Segmentierer: {len(segmente)} Segmente erkannt")
        for idx, seg in enumerate(segmente):
            logger.info(f"  Segment {idx + 1}: {seg[:80]}")

        return segmente

    except (json.JSONDecodeError, KeyError, Exception) as fehler:
        logger.warning(f"Segmentierer: Fehler ({fehler}) — Fallback auf ganzen Prompt")
        return [prompt]


def _build_salienz_prompt() -> str:
    """Baut den Salienz-System-Prompt aus [BLOCKNAME]-Bloecken zusammen."""
    return "\n\n".join([
        PROMPTS["salienz.identity"],
        PROMPTS["salienz.task"],
        PROMPTS["salienz.rules"],
    ])


def analyze(
    state:        ConversationState,
    embed_client,
    embed_model:  str,
    redis_client: redis.Redis,
    user_id:      str,
    postgres_url: str = ""
) -> ConversationState:
    """
    Analysiert den Turn. Segmentiert bei Bedarf in Teilaussagen.
    Legt pending_writes fuer KZG an (ohne Embedding, ohne kern).
    Schreibt NICHT in die DB — das macht der KZG-Agent via Dispatcher.
    """

    logger.info("Salienz: Analysiere Gespraechs-Turn...")

    # ── Prompt segmentieren ──────────────────
    segmente: list[str] = _prompt_segmentieren(state["user_prompt"])

    pending:       list[dict] = state.get("pending_writes", []) or []
    gesamt_tokens: int        = 0

    salienz_prompt: str = _build_salienz_prompt()

    logger.info(f"Salienz: System-Prompt:\n{salienz_prompt}")

    for seg_idx, segment in enumerate(segmente):

        if len(segmente) > 1:
            logger.info(f"Salienz: Segment {seg_idx + 1}/{len(segmente)}: {segment[:60]}...")

        segment_hinweis: str = ""
        if len(segmente) > 1:
            segment_hinweis = (
                f"\nHINWEIS: Dies ist Segment {seg_idx + 1} von {len(segmente)} "
                f"aus einem laengeren Prompt. Analysiere NUR dieses Segment. "
                f"Ignoriere Inhalte aus anderen Teilen des Prompts.\n"
            )

        lagebild: str = ""
        if state.get("response"):
            lagebild = (
                "[LAGEBILD]\n"
                "Hintergrund — nicht bewerten. "
                "Dies ist die Antwort des Assistenten.\n\n"
                f"{state['response']}\n\n"
            )

        analyse_prompt: str = (
            f"{lagebild}"
            "[BEWERTUNGSOBJEKT]\n"
            "Analysiere und bewerte NUR den folgenden Teil.\n"
            f"{segment_hinweis}"
            f"Eingabe des Nutzers:\n{segment}"
        )

        node_cfg = get_node_config("salienz")
        provider = get_chat_provider()
        antwort  = provider.chat(
            messages = [
                {"role": "user", "content": analyse_prompt},
            ],
            system            = salienz_prompt,
            temperature       = node_cfg.get("temperature", 0.05),
            format_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "salienz",
        )

        gesamt_tokens += antwort.token_total

        try:
            logger.debug(f"Salienz RAW: '{antwort.content[:500]}'")
            salienz_obj: dict = json.loads(antwort.content)

            logger.info(
                f"Salienz: score={salienz_obj.get('salienz', 0):.2f}, "
                f"themen={salienz_obj.get('themen', [])}, "
                f"dimension={salienz_obj.get('dimension', '-')}, "
                f"typ={salienz_obj.get('gedaechtnistyp', '-')}, "
                f"intentionen={salienz_obj.get('intentionen', [])}, "
                f"emotion={salienz_obj.get('emotion', '-')}, "
                f"modus={salienz_obj.get('modus', '-')}"
            )

        except (json.JSONDecodeError, KeyError) as fehler:
            logger.warning(f"Salienz: JSON-Parsing fehlgeschlagen ({fehler}) — Segment uebersprungen")
            continue

        # ── Gravitationsterm auf Salienz addieren (Drive) ──
        gravitationsterm: float = state.get("gravitationsterm", 0.0)

        if gravitationsterm > 0.0:
            salienz_basis: float = salienz_obj.get("salienz", 0.0)
            salienz_neu:   float = min(1.0, salienz_basis + gravitationsterm)
            salienz_obj["salienz"] = round(salienz_neu, 2)

            logger.info(
                f"Salienz: Gravitationsboost — "
                f"basis={salienz_basis:.2f} + grav={gravitationsterm:.3f} "
                f"= {salienz_neu:.2f}"
            )

        # ── pending_write fuer KZG-Agent (ohne Embedding, ohne kern) ─
        pending.append({
            "ziel":         "kzg",
            "aktion":       "create",
            "daten": {
                "salienz_obj": salienz_obj,
            },
            "beschreibung": f"KZG: {', '.join(salienz_obj.get('themen', []))} "
                            f"(salienz={salienz_obj.get('salienz', 0):.2f})",
        })

    state["pending_writes"] = pending

    logger.info(f"Salienz: {len(pending)} pending_writes angelegt ({len(segmente)} Segment(e))")

    # ── Token-Zaehler aktualisieren ───────────
    state["token_total"] += gesamt_tokens

    return state
