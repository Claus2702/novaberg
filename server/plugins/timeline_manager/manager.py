"""
Timeline-Manager — Lese-Schicht fuer temporale Fakten.

Liefert Timeline-Kontext (Termine, Geburtstage, Deadlines) als
ContextEntry-Liste an den Enricher. Schreib-Operationen laufen
ueber den TimelineAgent (agents/timeline/), nicht mehr ueber diesen
Manager.

M2.5a: plan/execute/termin_verarbeiten und CRUD-Helper wurden entfernt.
Der Planner short-circuitet timeline_management ueber Agent-Discovery,
und kein Producer schreibt mehr ziel="timeline"-Writes. Sollte trotzdem
ein Write hier landen, schlaegt execute() lauf fehl — Absicht.
"""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import redis

from agents.timeline.event_time import precision_has_time
from config import TIMEZONE
from graph.context_entry import ContextEntry
from memory.repositories.timeline_repository import TimelineRepository
from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins.timeline")


class TimelineManager(BaseManager):

    @property
    def ziel(self) -> str:
        return "timeline"

    @property
    def immer_aktiv(self) -> bool:
        return False

    # ─────────────────────────────────────────
    # Prompt-Erweiterungen
    # ─────────────────────────────────────────
    @property
    def router_intents(self) -> list[str]:
        return ["timeline_management"]

    @property
    def router_prompt(self) -> str:
        return """
TIMELINE-ERKENNUNG:
Setze management_action = "agent" wenn der Prompt zeitgebundene Information
enthaelt — egal in welcher Satzform:

- Imperative: "Trag ein: Zahnarzt am Donnerstag"
- Fragen: "Wann hat Anna Geburtstag?"
- Aussagen: "Annas Geburtstag ist am 15. Mai"
- Beilaeufig: "Morgen muss ich Getraenke kaufen"
- Erinnerungen: "Erinnere mich morgen um 8 Uhr"
- Mit Uhrzeit: "Termin am Freitag um 10 Uhr in Frankfurt"

Entscheidend ist NICHT die Satzform, sondern ob der Prompt ein Datum,
eine Uhrzeit, einen Zeitraum oder ein zeitgebundenes Ereignis enthaelt.

Bei Erkennung:
  management_action = "agent"
  management_target = "timeline"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Erinnere mich morgen frueh um 8 Uhr ans Meeting"
- "IT-Termin in Frankfurt um 10 Uhr"
- "Was steht morgen an?"
- "Zahnarzt am Donnerstag um 14:30"
- "Naechste Woche Montag habe ich frei"

ODER der Gespraechsverlauf ein aktives Zeitereignis enthaelt
und der aktuelle Prompt sich darauf bezieht.
"""

    # ─────────────────────────────────────────
    # Enricher-Hook
    # ─────────────────────────────────────────
    def enrich_entries(self, state: dict, postgres_url: str) -> list[ContextEntry]:
        """Liefert Timeline-Kontext als strukturierte ContextEntry-Liste.

        Drei Zweige:
          - range: Router-Query mit Datum-Bereich (timeline_query.type == "range")
          - search: Router-Query per Keyword (timeline_query.type == "search")
          - proaktiv: Zeitfenster heute -3 bis +14 Tage

        Mapping pro Termin (ein Entry pro Termin):
          quelle  = "plugin_timeline"
          subtyp  = (range/search) Spalte event_type
                    (proaktiv)     "anstehend" / "vergangen"
          inhalt  = "{datum}: {titel}{detail_str}" — datum mit Uhrzeit, falls
                    precision != "day"; detail_str = " — {details}" oder ""
          gewicht = 1.0
          meta    = {
              "praefix":    "Timeline/{subtyp}",
              "datum":      Formatiertes Datum/Uhrzeit,
              "titel":      Termin-Titel,
              "details":    detail_str (mit fuehrendem " — " oder ""),
              "termin_id":  Datenbank-ID (wenn vorhanden),
          }
        """
        user_id: str = state.get("user_id", "")
        if not user_id:
            return []

        external = state.get("external")
        intent:   str               = external.emotion.intent if external else ""
        tl_query: dict              = state.get("timeline_query", {})
        entries:  list[ContextEntry] = []

        logger.info(f"TimelineManager.enrich_entries: intent={intent}")

        # Gezielter Query vom Router
        if state.get("needs_timeline") and tl_query:
            query_type: str = tl_query.get("type", "")

            if query_type == "range":
                try:
                    von_str: str = tl_query.get("from", "")
                    bis_str: str = tl_query.get("to", "")
                    tz = ZoneInfo(TIMEZONE)
                    von_dt = datetime.fromisoformat(von_str) if von_str else datetime.now(tz)
                    bis_dt = datetime.fromisoformat(bis_str) if bis_str else datetime.now(tz)
                    rows = TimelineRepository.find_by_date_range(
                        postgres_url, user_id, von_dt, bis_dt
                    )
                    logger.info(
                        f"TimelineManager.enrich_entries: branch=range, treffer={len(rows)}"
                    )
                    for r in rows:
                        entries.append(self._termin_zu_entry(r, subtyp_quelle="event_type"))
                except Exception as fehler:
                    logger.warning(f"TimelineManager enrich range: {fehler}")

                self._log_entries(entries)
                return entries

            elif query_type == "search":
                rows = TimelineRepository.find_by_keyword(
                    postgres_url, user_id,
                    tl_query.get("keyword", ""),
                    tl_query.get("direction", "forward"),
                    tl_query.get("limit", 5),
                )
                logger.info(
                    f"TimelineManager.enrich_entries: branch=search, treffer={len(rows)}"
                )
                for r in rows:
                    entries.append(self._termin_zu_entry(r, subtyp_quelle="event_type"))

                self._log_entries(entries)
                return entries

        # Neuer Pfad: Repository mit erweitertem Zeitfenster
        try:
            jetzt: datetime = datetime.now(ZoneInfo(TIMEZONE))
            von:   datetime = jetzt - timedelta(days=3)
            bis:   datetime = jetzt + timedelta(days=14)

            termine: list[dict] = TimelineRepository.find_by_date_range(
                postgres_url, user_id, von, bis
            )

            logger.info(
                f"TimelineManager.enrich_entries: branch=proaktiv, treffer={len(termine)}"
            )

            for t in termine:
                entries.append(
                    self._termin_zu_entry(t, subtyp_quelle="status", jetzt=jetzt)
                )

        except Exception as fehler:
            logger.warning(f"TimelineManager enrich (neu) fehlgeschlagen: {fehler}")

        self._log_entries(entries)
        return entries

    @staticmethod
    def _termin_zu_entry(
        termin:        dict,
        subtyp_quelle: str,
        jetzt:         datetime | None = None,
    ) -> ContextEntry:
        """Baut einen ContextEntry aus einer Timeline-Repository-Zeile.

        subtyp_quelle="event_type": subtyp = termin["event_type"] (range/search).
        subtyp_quelle="status":     subtyp = "vergangen"/"anstehend" (proaktiv).
        """
        zeitpunkt: str = termin["event_time"].strftime("%d.%m.%Y")
        if precision_has_time(termin.get("precision", "day")):
            zeitpunkt += f" {termin['event_time'].strftime('%H:%M')}"

        if subtyp_quelle == "status":
            subtyp: str = "vergangen" if termin["event_time"] < jetzt else "anstehend"
        else:
            subtyp = termin.get("event_type", "")

        detail_str: str = f" — {termin['details']}" if termin.get("details") else ""
        titel:      str = termin.get("title", "")
        inhalt:     str = f"{zeitpunkt}: {titel}{detail_str}"

        logger.debug(
            f"Timeline-Entry: subtyp={subtyp}, datum={zeitpunkt}, "
            f"titel={titel[:40]}"
        )

        return {
            "quelle":  "plugin_timeline",
            "subtyp":  subtyp,
            "inhalt":  inhalt,
            "gewicht": 1.0,
            "meta": {
                "praefix":   f"Timeline/{subtyp}",
                "datum":     zeitpunkt,
                "titel":     titel,
                "details":   detail_str,
                "termin_id": termin.get("id"),
            },
        }

    @staticmethod
    def _log_entries(entries: list[ContextEntry]) -> None:
        logger.info(
            f"TimelineManager.enrich_entries: {len(entries)} Eintraege geliefert"
        )

    # ─────────────────────────────────────────
    # Ausfuehrung — Loud-Failure-Stub
    # ─────────────────────────────────────────
    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> int:
        """Loud-Failure-Stub.

        Schreib-Operationen laufen ueber den TimelineAgent. Wenn dennoch
        ein Write mit ziel='timeline' hier ankommt, ist das ein Bug
        (z.B. ein Producer, der die Agent-Discovery umgeht). Wir verschlucken
        das nicht still — wir schmeissen.

        BaseManager.execute ist @abstractmethod, deshalb braucht die Klasse
        eine konkrete Implementierung, sonst koennte sie nicht instanziiert
        werden. Diese Stub-Methode erfuellt das, ohne ein No-Op zu sein.
        """
        raise NotImplementedError(
            f"TimelineManager.execute aufgerufen mit {len(writes)} write(s) — "
            f"Schreib-Operationen laufen ueber den TimelineAgent, nicht mehr "
            f"ueber diesen Manager. user_id={user_id}, writes={writes!r}"
        )
