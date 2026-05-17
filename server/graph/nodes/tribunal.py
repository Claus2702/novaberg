"""
Tribunal Node — Bewertet die generierte Antwort aus drei Perspektiven.
Jeder Agent ist eine eigenstaendige Funktion mit eigenem System-Prompt.
Agenten koennen ergaenzt, ersetzt oder deaktiviert werden.

Architektur:
  Responder -> Jurist -> Psychologe -> Ethik -> Auswertung -> Entscheidung

Voting-System:
  2x ablehnen  -> ablehnen
  2x warnung   -> warnung (mit Korrektur)
  sonst        -> ok

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import json
import logging
from typing import Callable

from graph.state import ConversationState, TribunalVote
from config import (
    get_node_config, PROMPTS,
    TRIBUNAL_JURIST_WARNUNG, TRIBUNAL_JURIST_ABLEHNEN,
    TRIBUNAL_PSYCHOLOGE_WARNUNG, TRIBUNAL_PSYCHOLOGE_ABLEHNEN,
    TRIBUNAL_ETHIK_WARNUNG, TRIBUNAL_ETHIK_ABLEHNEN,
    TRIBUNAL_JURIST_DIREKTIVE_WARNUNG, TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN,
)
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.tribunal")


AGENTS: list[dict[str, str]] = [
    {
        "name": "jurist",
        "system_prompt": PROMPTS["tribunal_jurist.system"],
    },
    {
        "name": "psychologe",
        "system_prompt": PROMPTS["tribunal_psychologe.system"],
    },
    {
        "name": "ethik",
        "system_prompt": PROMPTS["tribunal_ethik.system"],
    },
]


# ─────────────────────────────────────────────
# Score → Vote Ableitung (T1)
# ─────────────────────────────────────────────

_SCHWELLWERTE: dict[str, tuple[float, float]] = {
    "jurist":     (TRIBUNAL_JURIST_WARNUNG,     TRIBUNAL_JURIST_ABLEHNEN),
    "psychologe": (TRIBUNAL_PSYCHOLOGE_WARNUNG, TRIBUNAL_PSYCHOLOGE_ABLEHNEN),
    "ethik":      (TRIBUNAL_ETHIK_WARNUNG,      TRIBUNAL_ETHIK_ABLEHNEN),
}


def _score_to_vote(agent_name: str, score: float) -> str:
    """Leitet Vote aus Score und konfigurierbaren Schwellwerten ab."""
    warnung_schwelle, ablehnen_schwelle = _SCHWELLWERTE.get(
        agent_name, (0.7, 0.9)
    )
    if score >= ablehnen_schwelle:
        return "ablehnen"
    elif score >= warnung_schwelle:
        return "warnung"
    return "ok"


def _score_to_vote_direktive(score: float) -> str:
    """Leitet Vote aus Direktiven-Score mit strengeren Schwellwerten ab."""
    if score >= TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN:
        return "ablehnen"
    elif score >= TRIBUNAL_JURIST_DIREKTIVE_WARNUNG:
        return "warnung"
    return "ok"


# ─────────────────────────────────────────────
# Einzelner Agent-Aufruf (generisch)
# ─────────────────────────────────────────────
def _agent_vote(
    agent_name:    str,
    system_prompt: str,
    state:         ConversationState,
) -> TribunalVote:
    """Fuehrt einen einzelnen Tribunal-Agenten aus und gibt sein Votum zurueck."""

    external = state.get("external")
    intent: str = external.emotion.intent if external else "smalltalk"
    tone:   str = external.emotion.tone   if external else "sachlich"

    msg_parts: list[str] = [
        "[LAGEBILD]\n"
        "Hintergrund — nicht Teil der Bewertung. "
        "Erklaert den Kontext des Nutzers.\n\n"
        f"Intent: {intent}\n"
        f"Gewuenschter Ton: {tone}"
    ]

    if state.get("memory_context"):
        msg_parts[0] += (
            f"\n\nPersoenlicher Kontext des Nutzers:\n"
            f"{state['memory_context']}"
        )

    if state.get("node_annotations"):
        msg_parts.append(
            "[ANMERKUNGEN]\n"
            "Qualifizierte Hinweise vorheriger Pruefungen.\n\n"
            + "\n".join(state["node_annotations"])
        )

    # Direktiven als Pruefkriterium (differenziert pro Agent) — aus internal.directives
    internal = state.get("internal")
    direktiven: list[dict] = list(internal.directives) if internal else []
    if direktiven:
        if agent_name == "jurist":
            # Jurist: Vertragspruefer — woertliche Pruefung
            dir_zeilen: list[str] = []
            for d in direktiven:
                if isinstance(d, dict):
                    dir_zeilen.append(f"- {d.get('anweisung', '')}")
                    kontext = d.get("kontext", "")
                    if kontext:
                        dir_zeilen.append(f"  (Kontext: {kontext})")
                else:
                    dir_zeilen.append(f"- {d}")
            dir_text: str = "\n".join(dir_zeilen)
            msg_parts.append(
                PROMPTS["tribunal_jurist.direktiven_pruefung"].format(
                    direktiven_text=dir_text
                )
            )
        # Psychologe + Ethiker: keine Direktiven-Pruefung

    msg_parts.append(
        "[BEWERTUNGSOBJEKT]\n"
        "Bewerte NUR den folgenden Teil.\n\n"
        f"Benutzeranfrage:\n{state['user_prompt']}\n\n"
        f"Antwort des Assistenten:\n{state['response']}"
    )

    bewertungs_prompt: str = "\n\n".join(msg_parts)

    logger.info(f"Tribunal [{agent_name}]: Bewerte Antwort...")
    logger.info(f"Tribunal [{agent_name}]: System-Prompt:\n{system_prompt}")
    logger.info(f"Tribunal [{agent_name}]: Bewertungs-Prompt:\n{bewertungs_prompt}")

    node_cfg = get_node_config("tribunal")
    provider = get_chat_provider()
    antwort  = provider.chat(
        messages = [
            {"role": "user", "content": bewertungs_prompt}
        ],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.2),
        format_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = f"tribunal/{agent_name.lower()}",
    )

    try:
        ergebnis: dict = json.loads(antwort.content)
        reasoning: str = ergebnis.get("reasoning", "")

        # Score-Auswertung mit Fallback auf altes Format
        raw_score = ergebnis.get("score")
        if raw_score is None:
            # Fallback: altes vote-Format
            old_vote: str = ergebnis.get("vote", "ok")
            score: float = {"ok": 0.0, "warnung": 0.7, "ablehnen": 1.0}.get(old_vote, 0.0)
            direktiven_score: float = 0.0
            derived_vote: str = old_vote
        else:
            score = max(0.0, min(1.0, float(raw_score)))

            if agent_name == "jurist":
                # Dual-Score: allgemein + Direktiven
                direktiven_score = max(0.0, min(1.0, float(ergebnis.get("direktiven_score", 0.0))))
                allgemein_vote: str = _score_to_vote("jurist", score)
                dir_vote: str = _score_to_vote_direktive(direktiven_score)
                _VOTE_RANG: dict[str, int] = {"ok": 0, "warnung": 1, "ablehnen": 2}
                derived_vote = max([allgemein_vote, dir_vote], key=lambda v: _VOTE_RANG[v])
            else:
                direktiven_score = 0.0
                derived_vote = _score_to_vote(agent_name, score)

        vote: TribunalVote = {
            "agent":     agent_name,
            "vote":      derived_vote,
            "reasoning": reasoning,
        }

    except (json.JSONDecodeError, KeyError, ValueError) as fehler:
        logger.warning(f"Tribunal [{agent_name}]: Parsing fehlgeschlagen ({fehler}), Fallback 'ok'")
        score = 0.0
        direktiven_score = 0.0
        vote: TribunalVote = {
            "agent":     agent_name,
            "vote":      "ok",
            "reasoning": f"Parsing-Fehler: {fehler}",
        }

    if agent_name == "jurist":
        logger.info(f"Tribunal [jurist]: score={score:.2f}, dir={direktiven_score:.2f} → vote={vote['vote']}")
    else:
        logger.info(f"Tribunal [{agent_name}]: score={score:.2f} → vote={vote['vote']}")

    return vote


# ─────────────────────────────────────────────
# Tribunal-Durchlauf (alle Agenten sequenziell)
# ─────────────────────────────────────────────
def judge(state: ConversationState) -> ConversationState:
    """Fuehrt alle Tribunal-Agenten sequenziell aus und sammelt Voten."""

    logger.info(f"Tribunal: Starte Bewertung (Runde {state['correction_round']}, "
                f"{len(AGENTS)} Agenten)")

    votes: list[TribunalVote] = []

    for agent_def in AGENTS:
        vote: TribunalVote = _agent_vote(
            agent_name    = agent_def["name"],
            system_prompt = agent_def["system_prompt"],
            state         = state,
        )
        votes.append(vote)

    state["tribunal_votes"] = votes

    return state


# ─────────────────────────────────────────────
# Tribunal-Auswertung (Mehrheitsentscheid)
# ─────────────────────────────────────────────
def evaluate(state: ConversationState) -> ConversationState:
    """Wertet die Voten aus und bildet das Gesamturteil."""

    votes: list[TribunalVote] = state["tribunal_votes"]

    rejections: list[TribunalVote] = [v for v in votes if v["vote"] == "ablehnen"]
    warnings:   list[TribunalVote] = [v for v in votes if v["vote"] == "warnung"]

    # Mehrheitsentscheid
    if len(rejections) >= 2:
        state["tribunal_verdict"] = "ablehnen"
    elif len(warnings) + len(rejections) >= 2:
        state["tribunal_verdict"] = "warnung"
    else:
        state["tribunal_verdict"] = "ok"

    # Zusammenfassung fuer den Corrector
    critical_feedback: list[str] = [
        f"[{v['agent']}] {v['reasoning']}"
        for v in votes
        if v["vote"] in ("ablehnen", "warnung")
    ]
    state["tribunal_summary"] = "\n".join(critical_feedback) if critical_feedback else ""

    logger.info(f"Tribunal-Auswertung: verdict={state['tribunal_verdict']} "
                f"(ablehnungen={len(rejections)}, warnungen={len(warnings)})")

    for vote in votes:
        logger.info(f"  [{vote['agent']}] {vote['vote']}: {vote['reasoning'][:80]}")

    return state
