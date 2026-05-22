"""Session-Kontext-Extraktion — Arbeitskontext aus dem Gespraechsverlauf destillieren.

Allgemeine Infrastruktur, nicht Pixie-spezifisch.
Nutzer: RechercheAgent, VertiefungsAgent, Gespraechsvektor-Node (Epic 9).

Liest annotierte Session-Turns aus Redis mit allen Salienz-Dimensionen
und laesst das CPU-LLM den Arbeitskontext destillieren. Das LLM sieht
den Verlauf als Ganzes — der aktuelle Turn ist das WO, die vorherigen
das WOHER. Das eigentliche Thema liegt zwischen den Zeilen.
"""

import json
import logging

from config import (
    ASSISTANT_USER_ID,
    PIXIE_RECHERCHE_SESSION_TURNS,
    redis_client,
)
from services.model_services import model_service, BackgroundRequest

logger = logging.getLogger(__name__)


def session_kontext_extrahieren(
    user_id: str,
    character_id: str = "",
    max_turns: int | None = None,
) -> dict:
    """Extrahiert den Arbeitskontext aus den letzten Session-Turns.

    Liest annotierte Turns aus Redis, formatiert sie als strukturierten
    Block mit allen Salienz-Dimensionen, und laesst das CPU-LLM den
    Kontext destillieren.

    Args:
        user_id: User-ID fuer den Session-Key.
        max_turns: Maximale Turns (default: PIXIE_RECHERCHE_SESSION_TURNS).

    Returns:
        Dict mit destilliertem Kontext:
        {
            "thema_kern": "Berufliche Neuorientierung nach Kuendigung",
            "themen": ["Karriere", "Bewerbung", "Unsicherheit"],
            "emotionale_lage": "Frustration mit Hoffnungsschimmer",
            "modus": "beratend",
            "intention": "gemeinsam_eruieren",
            "arousal": "hoch",
            "zusammenfassung": "Der Nutzer verarbeitet seine Kuendigung...",
        }
        Leeres Dict wenn keine Session oder LLM-Fehler.
    """
    limit: int = max_turns or PIXIE_RECHERCHE_SESSION_TURNS
    from memory.session import _session_key
    session_key: str = _session_key(user_id, character_id or ASSISTANT_USER_ID, "turns")

    # -- Turns aus Redis laden --
    try:
        raw_turns: list[bytes] = redis_client.lrange(session_key, 0, -1)
    except Exception as e:
        logger.error(f"Kontext: Redis-Fehler — {e}")
        return {}

    if not raw_turns:
        logger.info("Kontext: Keine Session-Turns vorhanden")
        return {}

    # -- Turns parsen --
    turns: list[dict] = []
    for raw in raw_turns:
        try:
            turn: dict = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        turns.append(turn)

    if not turns:
        return {}

    # Auf die letzten N begrenzen
    turns = turns[-limit:]

    # -- Strukturierten Block fuer das LLM aufbauen --
    turn_block: str = _turns_formatieren(turns)
    turn_count: int = len(turns)

    if not turn_block.strip():
        logger.info("Kontext: Keine verwertbaren Turns")
        return {}

    # -- LLM-Call (CPU-Modell) --
    prompt: str = _kontext_prompt(turn_block, turn_count)

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
    # session_kontext_extrahieren() laeuft sync aus Pixie- oder
    # CharacterGraph-Pfaden via asyncio.to_thread → submit_sync. modus=
    # "sprache", weil der heutige get_background_provider auf das CPU-
    # Sprachmodell mappt (gemma4-cpu). Beifund: JSON ueber Sprachmodell —
    # nicht im Rahmen dieser Phase korrigiert.
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "sprache",
            system      = _SYSTEM_PROMPT,
            temperature = 0.1,
            expect_json = True,
            caller      = "kontext",
        ))
        ergebnis: dict = response.parsed

        logger.info(
            f"Kontext: {turn_count} Turns analysiert — "
            f"Kern={ergebnis.get('thema_kern', '?')}, "
            f"Emotion={ergebnis.get('emotionale_lage', '?')}"
        )

        return ergebnis

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Kontext: LLM-Analyse fehlgeschlagen — {e}")
        return {}


# ---------------------------------------------
# Formatierung
# ---------------------------------------------

def _turns_formatieren(turns: list[dict]) -> str:
    """Formatiert Turns als strukturierten Block mit allen Dimensionen.

    Jeder Turn zeigt: Rolle, Inhalt, und (bei annotierten User-Turns)
    alle Salienz-Dimensionen.
    """
    parts: list[str] = []

    for i, turn in enumerate(turns, 1):
        rolle: str = turn.get("rolle", "?").upper()
        inhalt: str = turn.get("inhalt", "")

        if rolle == "USER" and turn.get("kern"):
            # Annotierter User-Turn: Alle Dimensionen zeigen
            meta_parts: list[str] = []

            kern: str = turn.get("kern", "")
            if kern:
                meta_parts.append(f"  Kern: {kern}")

            emotion: str = turn.get("emotion", "")
            if emotion:
                arousal = turn.get("arousal", "")
                vektor: str = turn.get("emotions_vektor", "")
                meta_parts.append(f"  Emotion: {emotion}, Arousal: {arousal}, Vektor: {vektor}")

            intentionen = turn.get("intentionen", [])
            if intentionen:
                meta_parts.append(f"  Intentionen: {', '.join(intentionen)}")

            modus: str = turn.get("modus", "")
            if modus:
                meta_parts.append(f"  Modus: {modus}")

            stil: str = turn.get("sprach_stil", "")
            dynamik: str = turn.get("beziehungs_dynamik", "")
            tone: str = turn.get("tone", "")
            if stil or dynamik or tone:
                meta_parts.append(f"  Stil: {stil}, Dynamik: {dynamik}, Ton: {tone}")

            themen = turn.get("themen", [])
            if themen and isinstance(themen, list):
                meta_parts.append(f"  Themen: {', '.join(themen)}")

            meta_block: str = "\n".join(meta_parts)
            parts.append(f"[{i}] {rolle}: {inhalt}\n{meta_block}")

        else:
            # Assistant-Turn oder nicht-annotierter User-Turn
            parts.append(f"[{i}] {rolle}: {inhalt}")

    return "\n\n".join(parts)


# ---------------------------------------------
# Prompts
# ---------------------------------------------

_SYSTEM_PROMPT: str = (
    "[IDENTITAET]\n"
    "Du bist ein Analyse-Agent. Du analysierst Gespraechsverlaeufe und "
    "destillierst den Arbeitskontext eines Nutzers.\n"
    "\n"
    "[AUFGABE]\n"
    "Analysiere den Gespraechsverlauf als Ganzes. Nicht einzelne Turns zaehlen — "
    "der Zusammenhang zaehlt. Ein Wetter-Turn zwischen zwei Karriere-Turns ist "
    "eine Atempause, nicht ein Themenwechsel.\n"
    "\n"
    "Der aktuelle Turn ist das WO — was beschaeftigt den Nutzer jetzt.\n"
    "Die vorherigen Turns sind das WOHER — wie ist er dorthin gekommen.\n"
    "Beides zusammen beschreibt, was das Thema ist — aber das eigentliche Thema\n"
    "liegt zwischen den Zeilen. Nicht die einzelnen Aussagen zaehlen,\n"
    "sondern was sie zusammen bedeuten.\n"
    "\n"
    "Bestimme:\n"
    "1. THEMA_KERN: Was beschaeftigt den Nutzer WIRKLICH? (1 Satz)\n"
    "   Das ist selten das woertlich Gesagte — es ist das, was dahinter liegt.\n"
    "2. THEMEN: Die konkreten Sachthemen (max 5)\n"
    "3. EMOTIONALE_LAGE: Wie geht es dem Nutzer? (1 Satz, kein Fachbegriff)\n"
    "4. MODUS: Der dominante Gespraechsrahmen\n"
    "5. INTENTION: Was will der Nutzer primaer erreichen?\n"
    "6. AROUSAL: Energieniveau (niedrig/mittel/hoch)\n"
    "7. ZUSAMMENFASSUNG: Worum geht es, fuer einen Agenten der im Hintergrund\n"
    "   hilfreiche Informationen suchen soll (2-4 Saetze)\n"
    "\n"
    "[REGELN]\n"
    "- Antworte AUSSCHLIESSLICH mit dem JSON-Objekt. Kein weiterer Text.\n"
    "- Antworte auf Deutsch.\n"
    "- Unterscheide Kernthemen von Nebenbemerkungen.\n"
    "- Die Zusammenfassung ist FUER einen Recherche-Agenten: "
    "Was muss er wissen, um hilfreiche Informationen zu finden?\n"
    "- Wenn der Verlauf keinen klaren Schwerpunkt hat: "
    'thema_kern = "Kein dominantes Thema"\n'
    "- Format:\n"
    "{\n"
    '  "thema_kern": "...",\n'
    '  "themen": ["...", "..."],\n'
    '  "emotionale_lage": "...",\n'
    '  "modus": "...",\n'
    '  "intention": "...",\n'
    '  "arousal": "niedrig|mittel|hoch",\n'
    '  "zusammenfassung": "..."\n'
    "}"
)


def _kontext_prompt(turn_block: str, turn_count: int) -> str:
    """Baut den User-Prompt fuer die Kontext-Analyse."""
    return (
        f"[GESPRAECHSVERLAUF]\n"
        f"{turn_count} Turns, chronologisch. Hoehere Nummern sind aktueller.\n"
        f"User-Turns zeigen alle Salienz-Dimensionen (Emotion, Arousal, "
        f"Intentionen, Modus, Stil, Themen).\n\n"
        f"{turn_block}\n\n"
        f"Analysiere den Verlauf und destilliere den Arbeitskontext."
    )
