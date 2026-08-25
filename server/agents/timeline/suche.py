"""Such-Node — Findet Termine per Keyword, Datumsbereich oder listet anstehende auf.

Drei Such-Modi:
  1. Keyword: target vorhanden → find_by_keyword
  2. Zeitraum: zeitausdruck vorhanden → Zeitparser → find_by_date_range
  3. Uebersicht: weder target noch zeitausdruck → anstehende Termine (±14 Tage)
"""

import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agents.base import AgentState
from agents.timeline.event_time import precision_has_time
from config import (
    TIMELINE_SUCHE_LIMIT,
    TIMELINE_UEBERSICHT_TAGE_VORAUS,
    TIMELINE_UEBERSICHT_TAGE_ZURUECK,
    TIMEZONE,
)

logger = logging.getLogger("ki_server.agents.timeline.suche")


def suchen(state: AgentState) -> dict:
    """Sucht Termine in der Datenbank."""
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository
    from utils.zeitparser import zeit_parsen

    target = state["parameter"].get("target", "")
    zeitausdruck = state["parameter"].get("zeitausdruck", "")
    action = state["parameter"].get("action", "")
    user_id = state["kontext"].get("user_id", "")
    tz = ZoneInfo(TIMEZONE)

    logger.debug(f"suchen: Einstieg — action='{action}', target='{target}', "
                 f"zeit='{zeitausdruck}', user_id='{user_id}'")

    treffer: list[dict] = []

    # ── Modus 1: Keyword-Suche (target vorhanden) ──
    if target:
        treffer = TimelineRepository.find_by_keyword(
            POSTGRES_URL, user_id, target, "both", TIMELINE_SUCHE_LIMIT
        )
        treffer = [t for t in treffer if t.get("aktiv", True)]
        logger.debug(f"suchen: Keyword-Suche '{target}' — {len(treffer)} Treffer")

    # ── Modus 2: Zeitraum-Suche (zeitausdruck vorhanden) ──
    elif zeitausdruck:
        parsed_time = zeit_parsen(zeitausdruck)
        if parsed_time:
            # Tagesbereich um den geparsten Zeitpunkt
            von = parsed_time.replace(hour=0, minute=0, second=0, microsecond=0)
            bis = von + timedelta(days=1) - timedelta(seconds=1)

            # Erweiterte Zeitraeume erkennen
            zeitausdruck_lower = zeitausdruck.lower()
            if any(w in zeitausdruck_lower for w in ["woche", "naechste woche", "diese woche"]):
                # Woche: Montag bis Sonntag
                tage_bis_montag = parsed_time.weekday()
                von = (parsed_time - timedelta(days=tage_bis_montag)).replace(
                    hour=0, minute=0, second=0, microsecond=0)
                bis = von + timedelta(days=7) - timedelta(seconds=1)
            elif any(w in zeitausdruck_lower for w in ["monat", "naechsten monat", "diesen monat"]):
                # Ganzer Monat
                von = parsed_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if von.month == 12:
                    bis = von.replace(year=von.year + 1, month=1) - timedelta(seconds=1)
                else:
                    bis = von.replace(month=von.month + 1) - timedelta(seconds=1)

            treffer = TimelineRepository.find_by_date_range(
                POSTGRES_URL, user_id, von, bis
            )
            logger.debug(f"suchen: Zeitraum {von.strftime('%d.%m.')}–{bis.strftime('%d.%m.')} "
                         f"— {len(treffer)} Treffer")
        else:
            logger.warning(f"suchen: Zeitparser konnte '{zeitausdruck}' nicht parsen")

    # ── Modus 3: Uebersicht (weder target noch zeitausdruck) ──
    else:
        jetzt = datetime.now(tz)
        von = jetzt - timedelta(days=TIMELINE_UEBERSICHT_TAGE_ZURUECK)
        bis = jetzt + timedelta(days=TIMELINE_UEBERSICHT_TAGE_VORAUS)
        treffer = TimelineRepository.find_by_date_range(
            POSTGRES_URL, user_id, von, bis
        )
        logger.debug(f"suchen: Uebersicht (±14 Tage) — {len(treffer)} Treffer")

    # ── Create: Duplikat-Pruefung ──
    if action == "create":
        if treffer:
            # Aehnlicher Eintrag existiert bereits → kein Duplikat anlegen
            existierend = treffer[0]
            datum = existierend["event_time"].astimezone(tz).strftime("%d.%m.%Y")
            if precision_has_time(existierend.get("precision", "day")):
                datum += f" {existierend['event_time'].astimezone(tz).strftime('%H:%M')}"
            logger.info(f"suchen: Duplikat erkannt — '{existierend['title']}' am {datum}")
            return {
                "ergebnis": f"'{existierend['title']}' ist bereits eingetragen ({datum}).",
                "status": "abgeschlossen",
                "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "duplikat"}],
            }
        # Kein Duplikat → weiter zu ausfuehren
        logger.debug("suchen: Create — kein Duplikat, weiter zu ausfuehren")
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "kein_duplikat"}],
        }

    # ── Keine Treffer ──
    if not treffer:
        if action == "read":
            ergebnis_text = "Keine Termine gefunden."
            if zeitausdruck:
                ergebnis_text = f"Keine Termine fuer '{zeitausdruck}' gefunden."
            elif target:
                ergebnis_text = f"Kein Termin '{target}' gefunden."
            logger.debug("suchen: Read — keine Treffer")
            return {
                "ergebnis": ergebnis_text,
                "status": "abgeschlossen",
                "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden"}],
            }
        logger.debug("suchen: Update/Delete — keine Treffer → Fehler")
        return {
            "status": "fehler",
            "fehler": f"Kein Termin '{target or zeitausdruck}' gefunden.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden"}],
        }

    # ── Read: Ergebnisse direkt zurueckgeben ──
    if action == "read":
        zeilen = []
        for t in treffer:
            datum = t["event_time"].astimezone(tz).strftime("%d.%m.%Y")
            if precision_has_time(t.get("precision", "day")):
                datum += f" {t['event_time'].astimezone(tz).strftime('%H:%M')}"
            detail = f" — {t['details']}" if t.get("details") else ""
            zeilen.append(f"[{t['event_type']}] {datum}: {t['title']}{detail}")

        logger.debug(f"suchen: Read — {len(treffer)} Treffer zurueckgegeben")
        return {
            "ergebnis": "\n".join(zeilen),
            "status": "abgeschlossen",
            "schritte": state["schritte"]
            + [{"node": "suchen", "ergebnis": f"{len(treffer)} Treffer"}],
        }

    # ── Update/Delete: Disambiguierung bei mehreren Treffern ──
    if len(treffer) > 1 and action in ("update", "delete"):
        kandidaten = [
            {
                "id": t["id"],
                "title": t["title"],
                "datum": t["event_time"].astimezone(tz).strftime("%d.%m.%Y %H:%M"),
                "typ": t.get("event_type", "termin"),
            }
            for t in treffer
        ]

        # Bei update/delete: den zeitlich naechsten in der Zukunft bevorzugen
        jetzt = datetime.now(tz)
        zukunft = [t for t in treffer if t["event_time"].astimezone(tz) > jetzt]
        if len(zukunft) == 1:
            # Genau ein Zukunfts-Treffer → klarer Gewinner
            termin = zukunft[0]
            logger.info(f"suchen: Zukunfts-Filter → klarer Gewinner: '{termin['title']}'")
            return {
                "parameter": {**state["parameter"], "termin": termin},
                "status": "laufend",
                "schritte": state["schritte"]
                + [{"node": "suchen", "ergebnis": f"zukunft: {termin['title']}"}],
            }

        logger.debug(f"suchen: Disambiguierung — {len(kandidaten)} Kandidaten")
        return {
            "status": "rueckfrage",
            "rueckfrage": json.dumps({
                "typ": "disambiguierung",
                "agent": "timeline",
                "aktion": action,
                "kandidaten": kandidaten,
            }, ensure_ascii=False),
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "mehrdeutig", "anzahl": len(treffer)}],
        }

    # ── Einzeltreffer: weiter zu ausfuehren ──
    termin = treffer[0]
    logger.debug(f"suchen: Einzeltreffer — id={termin['id']}, title='{termin['title']}'")
    return {
        "parameter": {**state["parameter"], "termin": termin},
        "status": "laufend",
        "schritte": state["schritte"]
        + [{"node": "suchen", "ergebnis": f"gefunden: {termin['title']}"}],
    }
