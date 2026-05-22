"""Planung — LLM generiert Recherche-Ziel, Queries und Kriterien.

Nutzt das Analyse-Backend (Qwen3-32B im Lokal-Profil) via BackgroundWorker.
Bekommt die Lagebeurteilung als Kontext fuer gezielte Queries.
"""

import json
import logging

from services.model_services import model_service, BackgroundRequest

logger = logging.getLogger("ki_server.agents.recherche")

_PLANUNGS_PROMPT: str = """[IDENTITAET]
Du bist ein Recherche-Planer. Du formulierst Suchstrategien.

[THEMA]
{thema}

[ARBEITSKONTEXT]
Kern-Thema: {kern}
Sachthemen: {themen}
Gespraechsmodus: {modus}
Zusammenfassung: {zusammenfassung}

[LAGEBEURTEILUNG]
Vorwissen: {vorwissen}
Luecken: {luecken}
User-Mehrwert: {user_mehrwert}
Nicht suchen: {ausschluss}

[AUFGABE]
Formuliere einen Recherche-Plan, der die identifizierten Luecken fuellt.

[FORMAT]
Antworte ausschliesslich als JSON:
{{
  "ziel": "Was soll am Ende beantwortet sein? (1 Satz)",
  "queries": ["suchquery 1", "suchquery 2", "suchquery 3"],
  "kriterien": ["Woran erkenne ich Vollstaendigkeit 1", "Woran erkenne ich Vollstaendigkeit 2"]
}}

[REGELN]
- Max 4 Queries
- Queries sind kurz (2-5 Woerter), spezifisch, auf Deutsch oder Englisch je nach Thema
- Queries decken die Luecken ab, NICHT das bereits Bekannte
- Erfolgskriterien sind pruefbar (ja/nein), nicht vage
- Sprache: Deutsch"""


def recherche_planen(thema: str, session_kontext: dict, lage: dict = None) -> dict:
    """Plant die Recherche: Ziel, Queries, Erfolgskriterien.

    Args:
        thema: Thema aus dem Queue-Eintrag.
        session_kontext: Destillierter Session-Kontext aus memory/kontext.py.
        lage: Lagebeurteilung (optional, Fallback auf leere Werte).

    Returns:
        Dict mit ziel, queries, kriterien. Leeres Dict bei Fehler.
    """
    if lage is None:
        lage = {}

    themen_list = session_kontext.get("themen", [])
    if isinstance(themen_list, list):
        themen_str = ", ".join(themen_list)
    else:
        themen_str = str(themen_list)

    luecken_list = lage.get("wissensluecken", [])
    if isinstance(luecken_list, list):
        luecken_str = "\n".join(f"- {l}" for l in luecken_list) if luecken_list else "Keine Luecken identifiziert."
    else:
        luecken_str = str(luecken_list)

    ausschluss_list = lage.get("ausschluss", [])
    if isinstance(ausschluss_list, list):
        ausschluss_str = ", ".join(ausschluss_list) if ausschluss_list else "Keine Ausschluesse."
    else:
        ausschluss_str = str(ausschluss_list)

    prompt = _PLANUNGS_PROMPT.format(
        thema=thema or session_kontext.get("thema_kern", "unbekannt"),
        kern=session_kontext.get("thema_kern", ""),
        themen=themen_str,
        modus=session_kontext.get("modus", ""),
        zusammenfassung=session_kontext.get("zusammenfassung", ""),
        vorwissen=lage.get("vorwissen_zusammenfassung", "Kein Vorwissen."),
        luecken=luecken_str,
        user_mehrwert=lage.get("user_mehrwert", ""),
        ausschluss=ausschluss_str,
    )

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G4) ──
    # recherche_planen() laeuft im RechercheAgent. Der Agent wird sync invoked
    # aus services/pixie/dispatch.py via asyncio.to_thread(agent.invoke, ...)
    # — Worker-Thread ohne Event-Loop → submit_sync. JSON-Validierung +
    # CJK-Guard erledigt jetzt der BackgroundWorker (parse_json_strict +
    # contains_cjk/strip_cjk-Retry). Caller-seitiger json.loads entfaellt.
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "analyse",
            temperature = 0.2,
            expect_json = True,
            caller      = "recherche/planung",
        ))
        plan: dict = response.parsed
        logger.info(f"Recherche-Planung: Ziel={plan.get('ziel', '?')}")
        return plan

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Recherche-Planung fehlgeschlagen: {e}")
        return {}
