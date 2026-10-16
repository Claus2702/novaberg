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

**Der gezielte Lesevorgang steht hinter dem Router**
(`memory/timeline_reading.py`, gerufen in `graph/base.py::_node_route`).
Der Enricher laeuft vor dem Router; `needs_timeline` und `timeline_query`
sind hier noch nicht gesetzt, und ein gezielter Zweig an dieser Stelle war
nie erreichbar. Was dieser Manager liefert, ist das proaktive Fenster fuer
die Analyse-Leser von `memory_context`. Der Verfasser liest die Termine aus
dem `[TERMINE]`-Block, nicht aus diesen Eintraegen.
"""

import logging
from datetime import datetime

import redis

from graph.appointments import proactive_window
from graph.context_entry import ContextEntry
from graph.format.appointments import appointment_line
from memory.timeline_reading import read_appointments
from plugins.base import BaseManager
from utils.local_time import now_local

logger = logging.getLogger("ki_server.plugins.timeline")

#: Die Quelle der Eintraege dieses Managers — der Formatter laesst sie fuer
#: den Verfasser weg, der die Termine im `[TERMINE]`-Block bekommt.
TIMELINE_SOURCE: str = "plugin_timeline"


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
Setze management_action = "agent" wenn der User die Zeitachse AUSDRUECKLICH
beauftragt oder befragt:

- Eintragen: "Trag ein: Zahnarzt am Donnerstag", "Merk dir Annas Geburtstag am 15. Mai"
- Erinnern: "Erinnere mich morgen um 8 Uhr"
- Aendern: "Verschieb den Zahnarzt auf Freitag", "Leg fuer das Meeting 90 Minuten fest"
- Loeschen: "Sag den Termin am Freitag ab"
- Abfragen: "Was steht morgen an?", "Wann hat Anna Geburtstag?"

Entscheidend ist der Auftrag oder die Frage an die Zeitachse. Eine
Zeitangabe allein ist kein Auftrag — auch nicht mit Uhrzeit und Ereignis.

Bei Erkennung:
  management_action = "agent"
  management_target = "timeline"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Erinnere mich morgen frueh um 8 Uhr ans Meeting"
- "Trag mir den IT-Termin in Frankfurt um 10 Uhr ein"
- "Was steht morgen an?"
- "Merk dir: Zahnarzt am Donnerstag um 14:30"
- "Verschieb das Meeting auf 11 Uhr"
"""

    # ─────────────────────────────────────────
    # Enricher-Hook
    # ─────────────────────────────────────────
    def enrich_entries(self, state: dict, postgres_url: str) -> list[ContextEntry]:
        """Liefert das proaktive Fenster als ContextEntry-Liste, ohne Erinnerungs-Anker.

        Gelesen wird ueber denselben Weg wie der `[TERMINE]`-Block
        (`read_appointments`): drei Tage zurueck, vierzehn voraus, ein
        Erinnerungs-Anker ist kein Termin.

        Mapping pro Termin (ein Entry pro Termin):
          quelle  = "plugin_timeline"
          subtyp  = "vergangen" / "anstehend"
          inhalt  = die Zeile des Blocks ohne Spiegelstrich — Wochentag, Datum,
                    Uhrzeit in Ortszeit, Titel und der Bezug zu heute
          gewicht = 1.0
          meta    = {"praefix": "Timeline/{subtyp}", "datum": TT.MM.JJJJ,
                     "titel": Titel}

        Vorbedingung: `state` traegt `user_id`.
        Nachbedingung: je Termin des Fensters ein Eintrag; keiner davon ein
            Erinnerungs-Anker.
        Fehlerfaelle: ohne `user_id` und bei einem Lesefehler wird laut
            gemeldet und `[]` geliefert — der Turn laeuft weiter.
        """
        # ── Eingabe-Validierung ─────────────────────
        user_id: str = str(state.get("user_id") or "")
        if not user_id:
            logger.error("TimelineManager.enrich_entries: Zustand ohne user_id — keine Termine")
            return []

        # ── Verarbeitung ────────────────────────────
        now = now_local()
        try:
            reading = read_appointments(proactive_window(now), user_id, postgres_url, now)
        except Exception:
            logger.exception(
                "TimelineManager.enrich_entries: Timeline nicht gelesen — "
                "die Analyse-Leser bekommen keine Termine"
            )
            return []
        entries: list[ContextEntry] = [
            self._appointment_entry(appointment_line(a, now)[2:], a.past, a.moment, a.title)
            for a in reading.appointments
        ]

        # ── Ausgabe-Verifikation ────────────────────
        if len(entries) != len(reading.appointments):
            msg: str = "TimelineManager.enrich_entries: Eintraege und Termine verschieden viele"
            raise RuntimeError(msg)
        logger.info(f"TimelineManager.enrich_entries: {len(entries)} Eintraege geliefert")
        return entries

    @staticmethod
    def _appointment_entry(line: str, past: bool, moment: datetime, title: str) -> ContextEntry:
        """Baut einen ContextEntry aus der fertigen Zeile eines Termins.

        Vorbedingung: `line` ist nicht leer; `moment` ist ein Zeitpunkt.
        Nachbedingung: ein Eintrag der Quelle `plugin_timeline` mit dem
            Praefix `Timeline/vergangen` oder `Timeline/anstehend`.
        Fehlerfaelle: eine leere Zeile wirft `ValueError`.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not line:
            msg: str = "TimelineManager: Termin ohne Zeile"
            raise ValueError(msg)

        # ── Verarbeitung ────────────────────────────
        subtype: str = "vergangen" if past else "anstehend"
        entry: ContextEntry = {
            "quelle":  TIMELINE_SOURCE,
            "subtyp":  subtype,
            "inhalt":  line,
            "gewicht": 1.0,
            "meta": {
                "praefix": f"Timeline/{subtype}",
                "datum":   moment.strftime("%d.%m.%Y"),
                "titel":   title,
            },
        }

        # ── Ausgabe-Verifikation ────────────────────
        if not entry["meta"]["praefix"].endswith(subtype):
            msg = f"TimelineManager: Praefix ohne Subtyp: {entry['meta']['praefix']!r}"
            raise RuntimeError(msg)
        return entry

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
