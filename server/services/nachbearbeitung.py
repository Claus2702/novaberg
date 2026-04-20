"""
Nachbearbeitung — Asynchrone Pfade nach der Antwort-Auslieferung.

Wird als Background-Thread gestartet, sobald die Antwort an den User
ausgeliefert ist. Zwei parallele Pfade:

  User-Pfad:  Salienz(User) → Dispatcher(User)
  Nova-Pfad:  Perzeption(Nova) → Enricher(Nova) → Session-Turn annotieren

Der User wartet auf keinen der beiden Pfade.
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from config import ASSISTANT_USER_ID, llm_lock

logger = logging.getLogger("ki_server.nachbearbeitung")


def nachbearbeitung_starten(
    state: dict,
    human_graph,
    response: str,
    redis_client,
) -> None:
    """Startet die asynchrone Nachbearbeitung als Background-Thread."""

    thread = threading.Thread(
        target=_nachbearbeitung_ausfuehren,
        args=(state, human_graph, response, redis_client),
        daemon=True,
        name="nachbearbeitung",
    )
    thread.start()

    logger.info("Nachbearbeitung: Background-Thread gestartet")


def _nachbearbeitung_ausfuehren(
    state: dict,
    human_graph,
    response: str,
    redis_client,
) -> None:
    """Führt User- und Nova-Pfad parallel aus."""

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            user_future = executor.submit(
                _user_pfad, state, human_graph,
            )
            nova_future = executor.submit(
                _nova_pfad, state, human_graph, response, redis_client,
            )

            for name, future in [("User", user_future), ("Nova", nova_future)]:
                try:
                    future.result()
                except Exception as fehler:
                    logger.error(f"Nachbearbeitung: {name}-Pfad fehlgeschlagen — {fehler}")

    except Exception as fehler:
        logger.error(f"Nachbearbeitung: Executor-Fehler — {fehler}")


def _user_pfad(state: dict, human_graph) -> None:
    """Salienz(User) → Dispatcher(User). Schreibt ins Gedächtnis."""

    logger.info("Nachbearbeitung: User-Pfad startet — Salienz + Dispatcher")

    with llm_lock:
        state = human_graph._node_salience(state)

    # Dispatcher braucht kein LLM — kein Lock nötig
    state = human_graph._node_dispatch(state)

    logger.info("Nachbearbeitung: User-Pfad abgeschlossen")


def _nova_pfad(
    state: dict,
    human_graph,
    response: str,
    redis_client,
) -> None:
    """
    Perzeption(Nova) → Enricher(Nova) → Session-Turn annotieren.

    Analysiert Novas Antwort, extrahiert Emotion/Arousal/Modus,
    lädt Novas eigenen Kontext, annotiert den Session-Turn.
    """

    logger.info("Nachbearbeitung: Nova-Pfad startet — Perzeption + Enricher")

    # ── Nova-State bauen ──
    # Novas Antwort wird als "user_prompt" durchgereicht,
    # damit Perzeption sie analysiert. user_id = ASSISTANT_USER_ID.
    nova_state: dict = human_graph.create_state(
        user_prompt=response,
        user_id=ASSISTANT_USER_ID,
    )
    nova_state["perzeption_rolle"] = "assistant"

    # ── Perzeption(Nova) — GPU, braucht Lock ──
    with llm_lock:
        nova_state = human_graph._node_perceive(nova_state)

    logger.info(
        f"Nachbearbeitung: Nova-Perzeption — "
        f"emotion={nova_state.get('current_emotion', '?')}, "
        f"arousal={nova_state.get('current_arousal', 0):.2f}, "
        f"modus={nova_state.get('gespraechs_modus', '?')}"
    )

    # ── Enricher(Nova) — kein LLM, kein Lock ──
    nova_state = human_graph._node_enrich(nova_state)

    # ── Session-Turn annotieren ──
    # Den letzten Assistant-Turn im User-Session mit Novas
    # Emotions-Metadaten anreichern, damit der synchrone
    # EI-Calc im nächsten Turn Novas Historie sieht.
    try:
        from memory.session import session_assistant_turn_annotate

        session_assistant_turn_annotate(
            redis_client,
            state["user_id"],  # User-Session, nicht Nova-Session
            emotion=nova_state.get("current_emotion", ""),
            arousal=nova_state.get("current_arousal", 0.5),
            modus=nova_state.get("gespraechs_modus", ""),
            emotions_vektor=nova_state.get("emotions_vektor", ""),
            sprach_stil=nova_state.get("sprach_stil", ""),
            beziehungs_dynamik=nova_state.get("beziehungs_dynamik", ""),
        )
        logger.info("Nachbearbeitung: Assistant-Turn annotiert")

    except Exception as fehler:
        logger.warning(f"Nachbearbeitung: Turn-Annotation fehlgeschlagen — {fehler}")

    logger.info("Nachbearbeitung: Nova-Pfad abgeschlossen")
