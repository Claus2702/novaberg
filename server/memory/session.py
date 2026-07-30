"""
Session-Kontext — Gesprächsverlauf in Redis.
Temporär (TTL), mit automatischer Zusammenfassung.
"""

import json
import logging
import time

import redis

from services.model_services import model_service, ChatRequest

logger = logging.getLogger("ki_server.memory.session")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
SESSION_MAX_TURNS:    int = 20
SESSION_TTL:          int = 7200    # 2 Stunden Inaktivität
SESSION_SUMMARIZE_AT: int = 25      # Ab 25 Turns: älteste 10 zusammenfassen


def _session_key(user_id: str, character_id: str, suffix: str) -> str:
    """Baut den Redis-Key für eine Session-Partition.

    Format: session:{user_id}:{character_id}:{suffix}
    Beispiel: session:meister:nova:turns
    """
    return f"session:{user_id}:{character_id}:{suffix}"


# ─────────────────────────────────────────────
# Turn speichern
# ─────────────────────────────────────────────
def session_turn_store(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    rolle:        str,
    inhalt:       str,
    intentionen:  list = None,
    emotion:      str  = "",
    arousal:      float = 0.5,
    modus:        str  = "",
    kern:         str  = "",
    emotions_vektor:    str = "",
    sprach_stil:        str = "",
    beziehungs_dynamik: str = "",
    tone:               str = "",
    themen:             list[str] | None = None,
    embedding:          list[float] | None = None,
    herkunft:           str = "",
) -> None:
    """Speichert einen Turn in der Session, vollständig mit allen Meta-Daten.

    `herkunft` benennt den Vorgang, der den Turn erzeugt hat — `nutzer_turn`
    oder `eigener_impuls`. Leer bleibt sie nur dort, wo der Aufrufer sie nicht
    bestimmen kann; **leer heisst unbekannt und nicht "vom Nutzer"**.
    """
    key: str = _session_key(user_id, character_id, "turns")

    turn_data: dict = {
        "rolle":        rolle,
        "inhalt":       inhalt,
        "zeit":         time.time(),
        "intentionen":  intentionen or [],
        "emotion":      emotion,
        "arousal":      arousal,
        "modus":        modus,
        "kern":         kern,
        "emotions_vektor":    emotions_vektor,
        "sprach_stil":        sprach_stil,
        "beziehungs_dynamik": beziehungs_dynamik,
        "tone":               tone,
        # Wer diesen Turn erzeugt hat. Zwei Vorgaenge schreiben Eintraege
        # derselben Form in diesen Verlauf — die Antwort auf eine
        # Nutzeraeusserung und Novas eigener Impuls —, und ohne dieses Feld
        # sind sie in den Daten nicht zu unterscheiden. Sie waren es bis zum
        # 30.07.2026 nicht: Die Herkunft stand allein im Laufzeit-Protokoll,
        # und wer den Verlauf aus dem Speicher las, hielt einen Impuls fuer
        # eine Antwort (novaberg-bugs.md -> PFAD1-TIMEOUT-TURNVERLUST).
        #
        # Leer heisst **unbekannt**, nicht "nutzer_turn". Turns von vor dieser
        # Aenderung tragen das Feld nicht, und ein Default haette aus ihnen
        # rueckwirkend eine Aussage gemacht, die niemand erhoben hat.
        "herkunft":           herkunft,
    }

    if themen is not None:
        turn_data["themen"] = themen

    # Embedding als JSON-Array mitspeichern (nur fuer User-Turns relevant — wird
    # vom Gravitationsgraph-Panel gelesen, um Turns auf 2D zu projizieren).
    if embedding:
        turn_data["embedding"] = list(embedding)

    turn: str = json.dumps(turn_data, ensure_ascii=False)

    redis_client.rpush(key, turn)
    redis_client.expire(key, SESSION_TTL)

    laenge: int = redis_client.llen(key)
    logger.info(f"Session: Turn gespeichert ({rolle}, {laenge} Turns)")


# ─────────────────────────────────────────────
# Turn als Agent-Aktion markieren (KONTEXT1)
# ─────────────────────────────────────────────
def session_turn_mark_action(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    erledigt:     bool = True,
    erfolgreich:  bool = False,
) -> None:
    """Markiert den letzten User-Turn mit Agent-Aktionsstatus.

    Zwei Flags:
    - aktion_erledigt:    Agent hat Verarbeitung beendet (abgeschlossen oder fehler)
    - aktion_erfolgreich: Agent hat die Aktion umgesetzt (nur bei abgeschlossen)

    Wird NICHT aufgerufen bei Rueckfragen (status=rueckfrage).
    """
    key: str = _session_key(user_id, character_id, "turns")
    turns: list = redis_client.lrange(key, 0, -1)

    if not turns:
        return

    for idx in range(len(turns) - 1, -1, -1):
        try:
            turn: dict = json.loads(turns[idx])
        except json.JSONDecodeError:
            continue

        if turn.get("rolle") == "user":
            turn["aktion_erledigt"] = erledigt
            turn["aktion_erfolgreich"] = erfolgreich
            redis_client.lset(key, idx, json.dumps(turn, ensure_ascii=False))
            logger.debug(f"Session-Turn {idx} markiert: erledigt={erledigt}, erfolgreich={erfolgreich}")
            return


# ─────────────────────────────────────────────
# Zusammenfassung prüfen und erstellen
# ─────────────────────────────────────────────
def session_summarize_if_needed(
    redis_client:  redis.Redis,
    user_id:       str,
    character_id:  str,
) -> None:
    """Fasst älteste Turns zusammen wenn der Stack zu groß wird."""
    key:         str = _session_key(user_id, character_id, "turns")
    summary_key: str = _session_key(user_id, character_id, "summary")
    laenge:      int = redis_client.llen(key)

    if laenge <= SESSION_SUMMARIZE_AT:
        return

    # Älteste 10 Turns holen
    alte_turns_raw: list      = redis_client.lrange(key, 0, 9)
    alte_turns:     list[str] = []

    for raw in alte_turns_raw:
        try:
            turn:  dict = json.loads(raw)
            rolle: str  = "User" if turn["rolle"] == "user" else "Assistent"
            alte_turns.append(f"{rolle}: {turn['inhalt']}")
        except json.JSONDecodeError:
            continue

    if not alte_turns:
        return

    bisherige_summary: str = redis_client.get(summary_key) or ""

    zusammenfassung_prompt: str = (
        "Fasse den folgenden Gesprächsverlauf in 3-5 Sätzen zusammen. "
        "Behalte konkrete Namen, Fakten, Orte und Zahlen bei. "
        "Antworte NUR mit der Zusammenfassung.\n\n"
    )

    if bisherige_summary:
        zusammenfassung_prompt += (
            f"Bisherige Zusammenfassung:\n{bisherige_summary}\n\n"
            f"Neue Turns:\n"
        )

    zusammenfassung_prompt += "\n".join(alte_turns)

    try:
        # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
        # session_summarize_if_needed() wird vom CharacterGraph-dispatcher-Node
        # gerufen ([dispatcher.py:264]) — der CharacterGraph laeuft in
        # event_consumer.py via asyncio.to_thread(_graph_streamen, ...).
        # Kein Event-Loop im aufrufenden Thread → submit_sync. Einzige
        # nicht-Pixie-getriggerte G3-Stelle und damit live-verifizierbar
        # ohne Block 4.
        chat_request = ChatRequest(
            messages    = [{"role": "user", "content": zusammenfassung_prompt}],
            system      = "Du fasst Gespräche zusammen. Kurz, präzise, keine Details verlieren.",
            temperature = 0.2,
            caller      = "session/summary",
        )
        response = model_service.chat.submit_sync(chat_request)

        neue_summary: str = response.text.strip()

        redis_client.set(summary_key, neue_summary)
        redis_client.expire(summary_key, SESSION_TTL)
        redis_client.ltrim(key, 10, -1)

        logger.info(f"Session: 10 Turns zusammengefasst, {redis_client.llen(key)} verbleiben")

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Session-Zusammenfassung fehlgeschlagen")
        redis_client.ltrim(key, laenge - SESSION_MAX_TURNS, -1)


# ─────────────────────────────────────────────
# Turns abrufen
# ─────────────────────────────────────────────
def session_turns_retrieve(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> list[dict]:
    """Holt alle Turns der aktuellen Session."""
    key:        str       = _session_key(user_id, character_id, "turns")
    raw_turns:  list      = redis_client.lrange(key, 0, -1)
    turns:      list[dict] = []

    for raw in raw_turns:
        try:
            turns.append(json.loads(raw))
        except json.JSONDecodeError:
            continue

    return turns


# ─────────────────────────────────────────────
# Nummerierte Turn-Formatierung (Chat 24)
# ─────────────────────────────────────────────
def format_session_turns_numbered(
    turns: list[dict],
    max_turns: int = 5,
    max_chars: int = 100,
) -> str:
    """Formatiert Session-Turns mit Naehenummerierung.

    Hohere Nummer = naeher am aktuellen Prompt.

    Args:
        turns: Liste von Turn-Dicts aus Redis
        max_turns: Maximale Anzahl Turn-Paare
        max_chars: Maximale Zeichen pro Turn-Inhalt

    Returns:
        Formatierter String mit nummerierten Turns, leer wenn keine Turns
    """
    if not turns:
        return ""

    # Turns in Paare gruppieren (User + Assistant)
    paare: list[dict] = []
    i = 0
    while i < len(turns):
        turn = turns[i]
        paar: dict = {}

        if turn.get("rolle") == "user":
            text: str = turn.get("inhalt", "")
            if text:
                if len(text) > max_chars:
                    text = text[:max_chars] + "..."
                paar["user"] = text
                # Metadaten fuer Kontext-Annotation
                emotion: str = turn.get("emotion", "")
                if emotion:
                    paar["user_emotion"] = emotion
                if turn.get("aktion_erledigt"):
                    paar["user_erledigt"] = True
                    paar["user_erfolgreich"] = bool(turn.get("aktion_erfolgreich"))

            # Naechster Turn = Assistant?
            if i + 1 < len(turns) and turns[i + 1].get("rolle") == "assistant":
                a_turn: dict = turns[i + 1]
                a_text: str = a_turn.get("inhalt", "")
                if a_text:
                    if len(a_text) > max_chars:
                        a_text = a_text[:max_chars] + "..."
                    paar["assistant"] = a_text
                i += 2
            else:
                i += 1
        else:
            # Alleinstehender Assistant-Turn (z.B. Shadow) — ueberspringen
            i += 1
            continue

        if paar.get("user"):
            paare.append(paar)

    # Nur die letzten N Paare
    paare = paare[-max_turns:]

    # Nummerierung: 1 = aeltester, hoechste Nummer = aktuellster
    zeilen: list[str] = []
    for nr, paar in enumerate(paare, start=1):
        emo: str = paar.get("user_emotion", "")
        emo_suffix: str = f" ({emo})" if emo else ""
        if paar.get("user_erledigt"):
            marker: str = " [ERLEDIGT]" if paar.get("user_erfolgreich") else " [FEHLGESCHLAGEN]"
        else:
            marker = ""
        zeilen.append(f"[{nr}] USER{emo_suffix}{marker}: {paar['user']}")
        if paar.get("assistant"):
            zeilen.append(f"[{nr}] NOVA: {paar['assistant']}")

    return "\n".join(zeilen)


# ─────────────────────────────────────────────
# Kontext bauen (Summary + Turns)
# ─────────────────────────────────────────────
def session_context_build(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> str:
    """Baut den vollständigen Session-Kontext: Zusammenfassung + aktuelle Turns."""
    parts: list[str] = []

    summary_key: str = _session_key(user_id, character_id, "summary")
    summary:     str = redis_client.get(summary_key) or ""

    if summary:
        parts.append(f"[Bisheriger Gesprächsverlauf, zusammengefasst]\n{summary}")

    turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)

    if turns:
        turn_lines: list[str] = []
        for turn in turns:
            rolle: str = "User" if turn["rolle"] == "user" else "Assistent"
            turn_lines.append(f"{rolle}: {turn['inhalt']}")

        parts.append("[Aktuelle Unterhaltung]\n" + "\n".join(turn_lines))

    return "\n\n".join(parts) if parts else ""


# ─────────────────────────────────────────────
# Session zurücksetzen
# ─────────────────────────────────────────────
def session_reset(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> None:
    """Löscht die aktuelle Session komplett."""
    redis_client.delete(_session_key(user_id, character_id, "turns"))
    redis_client.delete(_session_key(user_id, character_id, "summary"))
    redis_client.delete(_session_key(user_id, character_id, "stack"))
    redis_client.delete(_session_key(user_id, character_id, "pending"))

    logger.info(f"Session: Zurückgesetzt für user '{user_id}', charakter '{character_id}'")
