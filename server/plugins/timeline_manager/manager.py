"""
Timeline-Manager — Speichert und verwaltet temporale Fakten.
Termine, Geburtstage, Deadlines mit Precision und Recurring.
Optional: Nur aktiv wenn Salienz-Agent temporalen Fakt erkannt hat
          oder Router timeline_management erkennt.

Erweitert um:
- Entity Resolution für beteiligte Personen/Orte (via M3 Service)
- Entitätsreferenzen in Timeline-Einträgen
- Wiedervorlage-Spalte für den Butler-Task
- Rückfragen bei fehlenden Informationen
"""

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from agents.timeline.event_time import precision_has_time, precision_format
from config import TIMEZONE
from utils.zeitparser import zeit_parsen, zeit_parsen_vektor, ZeitVektor

import redis

from graph.context_entry import ContextEntry
from plugins.base import BaseManager
from memory.repositories.timeline_repository import TimelineRepository
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.services.entity_resolution import (
    EntityResolutionService,
    ResolvedEntity,
    ResolutionResult,
)

if TYPE_CHECKING:
    import ollama

from config import get_node_config
from services.llm_provider import get_chat_provider

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

        intent:   str               = state.get("intent", "")
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
    # Planner-Hook
    # ─────────────────────────────────────────
    def plan(
        self,
        state:        dict,
        postgres_url: str
    ) -> dict:
        """
        Plant Timeline-Operationen basierend auf management_action.

        - read: Enricher hat den Kontext bereits geladen
        - delete: Termin per Titel suchen, bei Mehrdeutigkeit disambiguieren
        - update: Alten Termin finden, neues Datum parsen, pending_writes erzeugen
        - create: Datum aus User-Prompt parsen, pending_write erzeugen
        """
        action:  str = state.get("management_action", "")
        target:  str = state.get("management_target", "")
        user_id: str = state.get("user_id", "")
        prompt:  str = state.get("user_prompt", "")

        tz = ZoneInfo(TIMEZONE)

        if action == "read":
            return {
                "pending_writes":    [],
                "management_result": "Timeline-Daten geladen",
                "management_detail": state.get("memory_context", ""),
            }

        # ── Bestehenden Termin suchen ──────────────────
        treffer: list[dict] = []
        if action in ("update", "delete") and target:
            treffer = TimelineRepository.find_by_keyword(
                postgres_url, user_id, target, "both", 10
            )
            treffer = [t for t in treffer if t.get("aktiv", True)]

        # ── DELETE ──────────────────────────────────────
        if action == "delete":
            if len(treffer) == 0:
                return {
                    "pending_writes":    [],
                    "management_result": f"Kein Termin '{target}' gefunden",
                    "management_detail": "",
                }

            if len(treffer) == 1:
                return {
                    "pending_writes": [{
                        "ziel":         "timeline",
                        "aktion":       "delete",
                        "daten":        {"termin_id": treffer[0]["id"]},
                        "beschreibung": f"Termin löschen: {treffer[0]['title']}",
                    }],
                    "management_result": f"Termin '{treffer[0]['title']}' wird gelöscht",
                    "management_detail": "",
                }

            optionen_str: str = ", ".join(
                f"'{t['title']}' am {t['event_time'].astimezone(tz).strftime('%d.%m.%Y %H:%M')}"
                for t in treffer
            )
            return {
                "pending_writes":    [],
                "management_result": f"Mehrere Termine gefunden: {optionen_str}. Welchen meinst du?",
                "management_detail": "",
            }

        # ── UPDATE (Verschieben) ───────────────────────
        if action == "update":
            if len(treffer) == 0:
                return {
                    "pending_writes":    [],
                    "management_result": f"Kein Termin '{target}' gefunden zum Verschieben",
                    "management_detail": "",
                }

            # Bei mehreren: den zeitlich nächsten in der Zukunft nehmen
            from datetime import datetime as dt_cls
            jetzt = dt_cls.now(ZoneInfo(TIMEZONE))
            zukunft_treffer: list[dict] = [
                t for t in treffer if t["event_time"] > jetzt
            ]
            alter_termin: dict = zukunft_treffer[0] if zukunft_treffer else treffer[0]

            # Neues Datum aus dem User-Prompt extrahieren (LLM)
            provider = get_chat_provider()
            antwort = provider.chat(
                messages = [
                    {"role": "user", "content": prompt},
                ],
                system = (
                    "Extrahiere den neuen Zeitpunkt aus dem folgenden Text. "
                    "Antworte NUR mit dem Zeitausdruck, z.B. 'Freitag um 10 Uhr', "
                    "'morgen um 14:00', '15. April 9 Uhr'. "
                    "Kein erklärender Text. Nur der Zeitausdruck."
                ),
                temperature       = get_node_config("planner").get("temperature", 0.2),
                max_output_tokens = get_node_config("planner").get("max_output_tokens"),
                caller            = "planner/timeline",
            )

            zeit_text: str = antwort.content.strip()

            # ── Phase 1: Vektor und Referenz-Modus erkennen ──
            vektor: ZeitVektor = zeit_parsen_vektor(zeit_text)

            # Fallback: Gesamten Prompt parsen wenn LLM-Extraktion scheitert
            if vektor.datum is None:
                vektor = zeit_parsen_vektor(prompt)

            if vektor.datum is None:
                return {
                    "pending_writes":    [],
                    "management_result": f"Konnte das neue Datum nicht erkennen. Wann soll '{target}' stattfinden?",
                    "management_detail": "",
                }

            # ── Phase 2: Referenz bestimmen und ggf. neu parsen ──
            alte_zeit: datetime = alter_termin["event_time"]
            if not alte_zeit.tzinfo:
                alte_zeit = alte_zeit.replace(tzinfo=tz)

            if vektor.referenz_modus == "absolut":
                # "diesen Freitag" -> Referenz = jetzt (Default, schon korrekt geparst)
                logger.info("TimelineManager: Referenz-Modus 'absolut' — Referenz ist heute")

            elif vektor.referenz_modus == "relativ":
                # "nächsten Freitag" / "Freitag" -> Referenz = alter Termin
                vektor_neu: ZeitVektor = zeit_parsen_vektor(zeit_text, referenz=alte_zeit)
                if vektor_neu.datum is None:
                    vektor_neu = zeit_parsen_vektor(prompt, referenz=alte_zeit)
                if vektor_neu.datum is not None:
                    vektor = vektor_neu
                logger.info(
                    f"TimelineManager: Referenz-Modus 'relativ' — Referenz ist alter Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y %H:%M')})"
                )

            elif vektor.referenz_modus == "relativ_rueckwaerts":
                # "letzten Freitag" -> Referenz = alter Termin, Vergangenheit bevorzugt
                vektor_neu = zeit_parsen_vektor(zeit_text, referenz=alte_zeit, zukunft_bevorzugt=False)
                if vektor_neu.datum is None:
                    vektor_neu = zeit_parsen_vektor(prompt, referenz=alte_zeit, zukunft_bevorzugt=False)
                if vektor_neu.datum is not None:
                    vektor = vektor_neu
                logger.info(
                    f"TimelineManager: Referenz-Modus 'relativ_rueckwaerts' — Referenz ist alter Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y %H:%M')}), Vergangenheit bevorzugt"
                )

            neues_datum: datetime = vektor.datum

            # ── Vektor mit altem Termin kombinieren (Tag/Uhrzeit) ──
            if vektor.tag_erkannt and not vektor.uhrzeit_erkannt:
                # Nur Tag erkannt -> Uhrzeit vom alten Termin uebernehmen
                neues_datum = neues_datum.replace(
                    hour=alte_zeit.hour,
                    minute=alte_zeit.minute,
                    second=0,
                    microsecond=0,
                )
                logger.info(
                    f"TimelineManager: Vektor-Modus — Tag neu, Uhrzeit vom alten Termin "
                    f"({alte_zeit.strftime('%H:%M')})"
                )

            elif not vektor.tag_erkannt and vektor.uhrzeit_erkannt:
                # Nur Uhrzeit erkannt -> Tag vom alten Termin uebernehmen
                neues_datum = alte_zeit.replace(
                    hour=neues_datum.hour,
                    minute=neues_datum.minute,
                    second=0,
                    microsecond=0,
                )
                logger.info(
                    f"TimelineManager: Vektor-Modus — Uhrzeit neu, Tag vom alten Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y')})"
                )

            # Wenn beides erkannt: neues_datum bleibt wie geparst (Standard-Verhalten)

            # Bi-temporal: Alten Termin invalidieren, neuen anlegen
            lokale_zeit: str = neues_datum.astimezone(tz).strftime("%d.%m.%Y %H:%M")

            return {
                "pending_writes": [
                    {
                        "ziel":         "timeline",
                        "aktion":       "delete",
                        "daten":        {"termin_id": alter_termin["id"]},
                        "beschreibung": f"Alten Termin invalidieren: {alter_termin['title']}",
                    },
                    {
                        "ziel":         "timeline",
                        "aktion":       "create",
                        "daten": {
                            "title":      alter_termin["title"],
                            "event_time": neues_datum,
                            "event_type": alter_termin.get("event_type", "termin"),
                            "details":    alter_termin.get("details"),
                            "precision":  "minute" if vektor.uhrzeit_erkannt or alte_zeit.hour > 0 or alte_zeit.minute > 0 else "day",
                            "recurring":  alter_termin.get("recurring", False),
                        },
                        "beschreibung": f"Neuen Termin anlegen: {alter_termin['title']} am {lokale_zeit}",
                    },
                ],
                "management_result": f"Termin '{alter_termin['title']}' wird auf {lokale_zeit} verschoben",
                "management_detail": f"Alter Termin (ID {alter_termin['id']}) wird invalidiert, neuer Termin angelegt.",
            }

        # ── CREATE ─────────────────────────────────────
        if action == "create":
            import json

            provider = get_chat_provider()
            antwort = provider.chat(
                messages = [
                    {"role": "user", "content": prompt},
                ],
                system = (
                    "Extrahiere den Zeitpunkt und die Beschreibung aus dem Text. "
                    "Antworte NUR mit JSON: "
                    '{"zeitausdruck": "Freitag um 10 Uhr", "title": "Kurze Beschreibung", '
                    '"event_type": "termin|geburtstag|deadline|jahrestag", '
                    '"details": "Zusatzinfos oder null", '
                    '"recurring": false}'
                ),
                temperature       = get_node_config("planner").get("temperature", 0.2),
                format_json       = True,
                max_output_tokens = get_node_config("planner").get("max_output_tokens"),
                caller            = "planner/timeline",
            )

            try:
                plan_data: dict = json.loads(antwort.content)
            except (json.JSONDecodeError, KeyError):
                return {
                    "pending_writes":    [],
                    "management_result": "Konnte den Termin nicht aus dem Text extrahieren.",
                    "management_detail": "",
                }

            zeit_text = plan_data.get("zeitausdruck", "")
            parsed_time = zeit_parsen(zeit_text)
            if parsed_time is None:
                parsed_time = zeit_parsen(prompt)

            if parsed_time is None:
                return {
                    "pending_writes":    [],
                    "management_result": "Konnte das Datum nicht erkennen. Wann genau?",
                    "management_detail": "",
                }

            return {
                "pending_writes": [{
                    "ziel":         "timeline",
                    "aktion":       "create",
                    "daten": {
                        "title":      plan_data.get("title", target),
                        "event_time": parsed_time,
                        "event_type": plan_data.get("event_type", "termin"),
                        "details":    plan_data.get("details"),
                        "precision":  "minute" if parsed_time.hour > 0 or parsed_time.minute > 0 else "day",
                        "recurring":  plan_data.get("recurring", False),
                    },
                    "beschreibung": f"Termin anlegen: {plan_data.get('title', target)}",
                }],
                "management_result": f"Termin '{plan_data.get('title', target)}' wird eingetragen",
                "management_detail": "",
            }

        return {
            "pending_writes":    [],
            "management_result": f"Unbekannte Timeline-Aktion: {action}",
            "management_detail": "",
        }

    # ─────────────────────────────────────────
    # Ausführung
    # ─────────────────────────────────────────
    def execute(
        self,
        writes:        list[dict],
        user_id:       str,
        redis_client:  redis.Redis,
        postgres_url:  str,
        embed_client  = None,
        embed_model:   str = ""
    ) -> int:
        """
        Verarbeitet pending_writes für Timeline.
        Unterstützt altes Format (fact aus Salienz) und neues M5-Format.
        """
        verarbeitet: int = 0

        for write in writes:
            aktion: str  = write.get("aktion", "")
            daten:  dict = write.get("daten", {})

            # ── Neuer M5-Pfad: entitaeten oder termin-spezifische Daten ──────
            if "title" in daten and "event_time" in daten:
                ergebnis: dict = self.termin_verarbeiten(
                    aktion=aktion or "create",
                    daten=daten,
                    user_id=user_id,
                    postgres_url=postgres_url,
                    redis_client=redis_client,
                    embed_client=embed_client,
                    embed_model=embed_model,
                    turn_id=daten.get("turn_id"),
                )
                if ergebnis.get("erfolg"):
                    verarbeitet += 1
                logger.info(
                    f"TimelineManager M5: {ergebnis.get('aktion', '')} "
                    f"— {ergebnis.get('details', '')}"
                )
                continue

            # ── Delete/Update über M5 ──────
            if aktion in ("delete", "update") and ("termin_id" in daten or "datum" in daten):
                ergebnis = self.termin_verarbeiten(
                    aktion=aktion,
                    daten=daten,
                    user_id=user_id,
                    postgres_url=postgres_url,
                    redis_client=redis_client,
                    embed_client=embed_client,
                    embed_model=embed_model,
                    turn_id=daten.get("turn_id"),
                )
                if ergebnis.get("erfolg"):
                    verarbeitet += 1
                continue

            # ── Alter Pfad: fact aus Salienz ──────
            fact: dict = daten.get("fact", {})
            if fact:
                try:
                    from utils.zeitparser import zeit_parsen

                    raw_date: str = fact.get("date") or ""
                    parsed_time = zeit_parsen(raw_date) if isinstance(raw_date, str) else raw_date

                    if parsed_time is None:
                        logger.warning(
                            f"TimelineManager: Kein gültiges Datum aus '{raw_date}' — übersprungen"
                        )
                        continue

                    TimelineRepository.insert(
                        postgres_url=postgres_url,
                        user_id=user_id,
                        event_time=parsed_time,
                        event_type=fact.get("type", "termin"),
                        title=fact.get("title", ""),
                        details=fact.get("details"),
                        recurring=fact.get("recurring", False),
                        precision=fact.get("precision", "day"),
                    )
                    verarbeitet += 1
                except Exception as fehler:
                    logger.error(f"TimelineManager: Alter Pfad fehlgeschlagen — {fehler}")

        return verarbeitet

    # ─────────────────────────────────────────
    # M5: Termin verarbeiten
    # ─────────────────────────────────────────
    def termin_verarbeiten(
        self,
        aktion:         str,
        daten:          dict,
        user_id:        str,
        postgres_url:   str,
        redis_client:   "redis.Redis",
        embed_client:  "ollama.Client | None" = None,
        embed_model:    str = "",
        turn_id:        str | None = None,
    ) -> dict:
        """
        Verarbeitet Termin-Aktionen (create, update, delete, query).

        Returns:
            dict mit erfolg, aktion, details, braucht_klärung, klärungsfrage, agent_state
        """
        if aktion == "create":
            return self._termin_create(
                daten, user_id, postgres_url, redis_client,
                embed_client, embed_model, turn_id
            )

        elif aktion == "delete":
            return self._termin_delete(daten, user_id, postgres_url)

        elif aktion == "update":
            return self._termin_update(daten, postgres_url)

        elif aktion == "query":
            return self._termin_query(
                daten, user_id, postgres_url, redis_client,
                embed_client, embed_model, turn_id
            )

        return {
            "erfolg": False,
            "aktion": aktion,
            "details": f"Unbekannte Aktion: {aktion}",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────
    def _termin_create(
        self,
        daten:          dict,
        user_id:        str,
        postgres_url:   str,
        redis_client:   "redis.Redis",
        embed_client:  "ollama.Client | None",
        embed_model:    str,
        turn_id:        str | None,
    ) -> dict:
        """Neuen Termin anlegen."""
        title:      str                    = daten.get("title", "")
        event_time: str | datetime | None  = daten.get("event_time")
        event_type: str                    = daten.get("event_type", "termin")
        details:    str | None             = daten.get("details")
        precision:  str                    = daten.get("precision", "day")
        recurring:  bool                   = daten.get("recurring", False)
        entitaeten: list[dict]             = daten.get("entitaeten", [])

        # ── Vollständigkeits-Check ──────
        fehlend: list[str] = []
        if not title:
            fehlend.append("Bezeichnung des Termins")
        if not event_time:
            fehlend.append("Datum")

        if fehlend:
            return {
                "erfolg": False,
                "aktion": "klärung",
                "details": "",
                "braucht_klärung": True,
                "klärungsfrage": f"Mir fehlt noch: {', '.join(fehlend)}",
                "agent_state": {
                    "aktiver_agent": "timeline",
                    "aktion": "create",
                    "vorhandene_daten": daten,
                    "fehlt": fehlend,
                },
            }

        # ── Entity Resolution (falls Entitäten angegeben) ──────
        entitaet_ids: list[int] = []
        if entitaeten:
            resolution: ResolutionResult = EntityResolutionService.resolve_batch(
                entitaeten=entitaeten,
                postgres_url=postgres_url,
                user_id=user_id,
                redis_client=redis_client,
                turn_id=turn_id,
                embed_client=embed_client,
                embed_model=embed_model,
            )

            if resolution.braucht_klärung:
                return {
                    "erfolg": False,
                    "aktion": "klärung",
                    "details": "",
                    "braucht_klärung": True,
                    "klärungsfrage": " ".join(resolution.klärungsfragen),
                    "agent_state": {
                        "aktiver_agent": "timeline",
                        "aktion": "create",
                        "vorhandene_daten": daten,
                    },
                }

            # Neue Entitäten anlegen
            for entity in resolution.aufgeloest:
                if entity.ist_neu and entity.ist_referenz:
                    neue_id: int = EntityResolutionService.create_new_entity(
                        postgres_url=postgres_url,
                        user_id=user_id,
                        name=entity.name,
                        typ=entity.typ,
                        embed_client=embed_client,
                        embed_model=embed_model,
                    )
                    entity.bekannte_id = neue_id

                if entity.bekannte_id is not None:
                    entitaet_ids.append(entity.bekannte_id)

        # ── INSERT ──────
        termin_id: int = TimelineRepository.insert(
            postgres_url=postgres_url,
            user_id=user_id,
            event_time=event_time,
            event_type=event_type,
            title=title,
            details=details,
            recurring=recurring,
            precision=precision,
            entitaet_ids=entitaet_ids if entitaet_ids else None,
        )

        logger.info(f"TimelineManager: Termin '{title}' angelegt (ID {termin_id})")

        return {
            "erfolg": True,
            "aktion": "create",
            "details": f"Termin '{title}' eingetragen",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────
    def _termin_delete(
        self,
        daten:        dict,
        user_id:      str,
        postgres_url: str,
    ) -> dict:
        """Termin deaktivieren (Soft-Delete)."""
        termin_id: int | None = daten.get("termin_id")

        if termin_id:
            TimelineRepository.invalidate(postgres_url, termin_id)
            logger.info(f"TimelineManager: Termin {termin_id} invalidiert")
            return {
                "erfolg": True,
                "aktion": "delete",
                "details": "Termin gelöscht",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        # Kein ID → nach Datum suchen
        datum = daten.get("datum")
        if not datum:
            return {
                "erfolg": False,
                "aktion": "delete",
                "details": "Kein Termin identifizierbar (weder ID noch Datum)",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        treffer: list[dict] = TimelineRepository.find_by_date(
            postgres_url, user_id, datum
        )

        if len(treffer) == 0:
            return {
                "erfolg": False,
                "aktion": "delete",
                "details": "Kein Termin an diesem Datum gefunden",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        if len(treffer) == 1:
            TimelineRepository.invalidate(postgres_url, treffer[0]["id"])
            logger.info(
                f"TimelineManager: Termin '{treffer[0]['title']}' invalidiert"
            )
            return {
                "erfolg": True,
                "aktion": "delete",
                "details": f"Termin '{treffer[0]['title']}' gelöscht",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        # Mehrere Treffer → Disambiguierung
        optionen: str = ", ".join(
            f"'{t['title']}' um {t['event_time'].strftime('%H:%M')}"
            if precision_has_time(t.get("precision", "day"))
            else f"'{t['title']}'"
            for t in treffer
        )
        return {
            "erfolg": False,
            "aktion": "klärung",
            "details": "",
            "braucht_klärung": True,
            "klärungsfrage": (
                f"Ich habe {len(treffer)} Termine an dem Tag: "
                f"{optionen}. Welchen meinst du?"
            ),
            "agent_state": {
                "aktiver_agent": "timeline",
                "aktion": "delete",
                "kandidaten": [
                    {"id": t["id"], "title": t["title"]}
                    for t in treffer
                ],
            },
        }

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────
    def _termin_update(
        self,
        daten:        dict,
        postgres_url: str,
    ) -> dict:
        """Termin aktualisieren."""
        termin_id: int | None = daten.get("termin_id")

        if not termin_id:
            return {
                "erfolg": False,
                "aktion": "update",
                "details": "Keine Termin-ID angegeben",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        TimelineRepository.update(
            postgres_url=postgres_url,
            termin_id=termin_id,
            event_time=daten.get("event_time"),
            title=daten.get("title"),
            details=daten.get("details"),
            entitaet_ids=daten.get("entitaet_ids"),
        )

        logger.info(f"TimelineManager: Termin {termin_id} aktualisiert")

        return {
            "erfolg": True,
            "aktion": "update",
            "details": "Termin aktualisiert",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # QUERY
    # ─────────────────────────────────────────
    def _termin_query(
        self,
        daten:          dict,
        user_id:        str,
        postgres_url:   str,
        redis_client:   "redis.Redis",
        embed_client:  "ollama.Client | None",
        embed_model:    str,
        turn_id:        str | None,
    ) -> dict:
        """Termine abfragen — nach Datum, Entität oder beides."""
        datum         = daten.get("datum")
        entitaet_name: str | None = daten.get("entitaet")

        termine: list[dict] = []

        # Nach Entität suchen
        if entitaet_name:
            resolved: ResolvedEntity = EntityResolutionService.resolve_single(
                name=entitaet_name, typ="sonstiges",
                postgres_url=postgres_url, user_id=user_id,
                redis_client=redis_client, turn_id=turn_id,
                embed_client=embed_client, embed_model=embed_model,
            )

            if resolved.braucht_klärung:
                return {
                    "erfolg": False,
                    "aktion": "query",
                    "details": "",
                    "braucht_klärung": True,
                    "klärungsfrage": resolved.klärungsfrage,
                    "agent_state": None,
                }

            if resolved.bekannte_id is not None:
                termine = TimelineRepository.find_by_entitaet(
                    postgres_url, user_id, resolved.bekannte_id
                )

        # Nach Datum suchen
        elif datum:
            termine = TimelineRepository.find_by_date(
                postgres_url, user_id, datum
            )

        return {
            "erfolg": True,
            "aktion": "query",
            "details": f"{len(termine)} Termine gefunden",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }
