"""Bewertung — LLM prueft ob die Ergebnisse das Ziel abdecken.

Nutzt Qwen3-32B (Analyse-Modell) via pixie_llm_call().
Bewertet gegen Kriterien UND bekanntes Vorwissen UND User-Relevanz.
"""

import json
import logging

from services.llm_provider import pixie_llm_call

logger = logging.getLogger("ki_server.agents.recherche")

_BEWERTUNGS_PROMPT: str = """[IDENTITAET]
Du bist das Bewertungs-Modul von Nova.
Deine Aufgabe: Pruefen ob die Recherche-Ergebnisse das Ziel abdecken.

[RECHERCHE_ZIEL]
{ziel}

[ERFOLGSKRITERIEN]
{kriterien}

[BEKANNTES_WISSEN]
{vorwissen}

[NICHT_SUCHEN]
{ausschluss}

[BISHERIGE_ERGEBNISSE]
{zusammenfassung}

[AUFGABE]
Bewerte die Ergebnisse anhand von drei Pruefungen:
1. Enthalten die Ergebnisse Information, die UEBER das bekannte Wissen hinausgeht?
2. Sind die Erfolgskriterien abgedeckt?
3. Waere das Ergebnis fuer den User nuetzlich?

[FORMAT]
Antworte ausschliesslich als JSON:
{{
  "status": "fertig" oder "luecken",
  "pruefung_neues_wissen": true oder false,
  "pruefung_kriterien": true oder false,
  "pruefung_user_relevant": true oder false,
  "zusammenfassung": "Was gefunden wurde (2-3 Saetze)",
  "fehlend": "Was noch fehlt (nur bei luecken)",
  "queries": ["neue query 1", "neue query 2"]
}}

[REGELN]
- "fertig" wenn mindestens Pruefung 1 UND Pruefung 2 erfuellt
- "luecken" wenn Pruefung 1 NEIN (nur Bekanntes gefunden) — andere Queries noetig
- "luecken" wenn Pruefung 2 NEIN — spezifischere Queries noetig
- Max 2 neue Queries bei Luecken
- Im Zweifel: "fertig". Lieber ein gutes Teilergebnis als endlose Iteration.
- Sprache: Deutsch"""


def ergebnisse_bewerten(
    ziel: str,
    kriterien: list[str],
    zusammenfassung: str,
    lage: dict = None,
) -> dict:
    """Bewertet ob die bisherige Zusammenfassung das Recherche-Ziel abdeckt.

    Args:
        ziel: Das Recherche-Ziel (1 Satz).
        kriterien: Erfolgskriterien.
        zusammenfassung: Komprimierte Zusammenfassung der bisherigen Ergebnisse.
        lage: Lagebeurteilung mit Vorwissen (optional).

    Returns:
        Dict mit status ("fertig"|"luecken") und ggf. neue queries.
    """
    if lage is None:
        lage = {}

    kriterien_str = "\n".join(f"- {k}" for k in kriterien) if kriterien else "Keine Kriterien definiert."

    ausschluss_list = lage.get("ausschluss", [])
    ausschluss_str = ", ".join(ausschluss_list) if ausschluss_list else "Keine."

    prompt = _BEWERTUNGS_PROMPT.format(
        ziel=ziel,
        kriterien=kriterien_str,
        vorwissen=lage.get("vorwissen_zusammenfassung", "Kein Vorwissen."),
        ausschluss=ausschluss_str,
        zusammenfassung=zusammenfassung,
    )

    try:
        antwort = pixie_llm_call(
            prompt=prompt,
            modus="analyse",
            temperatur=0.1,
            json_output=True,
            caller="recherche/bewertung",
        )
        bewertung: dict = json.loads(antwort)
        logger.info(
            f"Recherche-Bewertung: status={bewertung.get('status', '?')}, "
            f"neues_wissen={bewertung.get('pruefung_neues_wissen', '?')}, "
            f"kriterien={bewertung.get('pruefung_kriterien', '?')}"
        )
        return bewertung

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Recherche-Bewertung fehlgeschlagen: {e}")
        return {"status": "fertig"}  # Im Zweifel: fertig, nicht endlos
