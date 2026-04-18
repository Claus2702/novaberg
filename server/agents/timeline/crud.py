"""CRUD-Nodes — Erstellen, Verschieben, Loeschen von Timeline-Eintraegen.

Erweitert in Chat 44 (Epic 15): normalisiert-Feld aus Classify im Debug-Log.
Erweitert in Chat 42 (CRUD-Haertung):
- reschedule als eigene Aktion (Alias fuer _update mit zeitlicher Verschiebung)
- Verifikation nach Schreiboperationen (DB-Read nach Write)

Bi-temporales Modell: Update invalidiert den alten Eintrag und legt
einen neuen an. Kein Ueberschreiben — die Historie bleibt erhalten.
"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from agents.base import AgentState
from config import TIMEZONE

logger = logging.getLogger("ki_server.agents.timeline.crud")


def _verifizieren_termin(termin_id: int, erwartung: dict) -> bool:
    """Prueft ob die DB-Operation den erwarteten Effekt hatte.

    Timeline nutzt 'aktiv' fuer Soft-Delete (kein t_invalid-Feld):
    - aktiv=True  -> Eintrag ist live
    - aktiv=False -> Eintrag ist invalidiert/geloescht
    """
    from tools.db_manager import db_manager

    eintrag = db_manager.select_one(
        "SELECT id, aktiv FROM timeline WHERE id = %s",
        (termin_id,),
    )
    if not eintrag:
        logger.error(f"Verifikation: Termin ID {termin_id} nicht gefunden")
        return False

    if "aktiv" in erwartung and eintrag["aktiv"] != erwartung["aktiv"]:
        logger.error(f"Verifikation: Termin ID {termin_id} aktiv={eintrag['aktiv']}, erwartet={erwartung['aktiv']}")
        return False

    if "invalidiert" in erwartung and erwartung["invalidiert"] and eintrag["aktiv"]:
        logger.error(f"Verifikation: Termin ID {termin_id} sollte invalidiert sein, ist aber aktiv")
        return False

    return True


def ausfuehren(state: AgentState) -> dict:
    """Fuehrt die CRUD-Operation aus."""
    action = state["parameter"].get("action", "")
    normalisiert = state["parameter"].get("normalisiert", "")
    logger.debug(f"ausfuehren: Einstieg — action='{action}', normalisiert='{normalisiert}'")

    if state["status"] == "abgeschlossen":
        logger.debug("ausfuehren: Status bereits 'abgeschlossen' (Duplikat) — uebersprungen")
        return {}

    if action == "create":
        return _create(state)
    elif action in ("update", "reschedule"):
        return _update(state)
    elif action == "delete":
        return _delete(state)

    logger.debug(f"ausfuehren: Unbehandelte Aktion '{action}'")
    return {
        "status": "fehler",
        "fehler": f"Unbehandelte Aktion: {action}",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "unbehandelt"}],
    }


def _create(state: AgentState) -> dict:
    """Neuen Termin anlegen — Zeitparser fuer Datumsaufloesung."""
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository
    from utils.zeitparser import zeit_parsen_vektor, ZeitVektor

    user_id = state["kontext"].get("user_id", "")
    title = state["parameter"].get("target", "")
    zeitausdruck = state["parameter"].get("zeitausdruck", "")
    event_type = state["parameter"].get("event_type", "termin")
    prompt = state["aufgabe"]
    tz = ZoneInfo(TIMEZONE)

    logger.debug(f"_create: Einstieg — title='{title}', zeit='{zeitausdruck}', typ='{event_type}'")

    if not title:
        return {
            "status": "fehler",
            "fehler": "Kein Titel fuer den Termin erkannt.",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_titel"}],
        }

    vektor: ZeitVektor = zeit_parsen_vektor(zeitausdruck) if zeitausdruck else ZeitVektor(
        datum=None, tag_erkannt=False, uhrzeit_erkannt=False, referenz_modus="relativ"
    )

    if vektor.datum is None:
        vektor = zeit_parsen_vektor(prompt)

    if vektor.datum is None:
        return {
            "status": "fehler",
            "fehler": f"Konnte kein Datum erkennen. Wann soll '{title}' stattfinden?",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_datum"}],
        }

    event_time: datetime = vektor.datum
    precision = "minute" if vektor.uhrzeit_erkannt else "day"

    entitaet_ids: list[int] = []

    termin_id: int = TimelineRepository.insert(
        postgres_url=POSTGRES_URL,
        user_id=user_id,
        event_time=event_time,
        event_type=event_type,
        title=title,
        details=None,
        recurring=False,
        precision=precision,
        entitaet_ids=entitaet_ids if entitaet_ids else None,
    )

    verifiziert = _verifizieren_termin(termin_id, {"aktiv": True})

    lokale_zeit: str = event_time.astimezone(tz).strftime("%d.%m.%Y")
    if precision != "day":
        lokale_zeit += f" {event_time.astimezone(tz).strftime('%H:%M')}"

    logger.info(f"TimelineAgent: Termin '{title}' angelegt (ID {termin_id}, {lokale_zeit}), verifiziert={verifiziert}")

    return {
        "ergebnis": f"Termin '{title}' eingetragen fuer {lokale_zeit}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "erstellt", "termin_id": termin_id, "verifiziert": verifiziert}],
    }


def _update(state: AgentState) -> dict:
    """Termin verschieben — bi-temporales Modell.

    Wird sowohl fuer action='update' als auch action='reschedule' aufgerufen.
    """
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository
    from utils.zeitparser import zeit_parsen_vektor, ZeitVektor

    termin = state["parameter"].get("termin", {})
    termin_id = termin.get("id")
    zeitausdruck = state["parameter"].get("zeitausdruck", "")
    prompt = state["aufgabe"]
    tz = ZoneInfo(TIMEZONE)

    logger.debug(f"_update: Einstieg — termin_id={termin_id}, title='{termin.get('title')}', "
                 f"neuer zeit='{zeitausdruck}'")

    if not termin_id:
        return {
            "status": "fehler",
            "fehler": "Kein Termin zum Verschieben gefunden.",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_termin"}],
        }

    vektor: ZeitVektor = zeit_parsen_vektor(zeitausdruck) if zeitausdruck else ZeitVektor(
        datum=None, tag_erkannt=False, uhrzeit_erkannt=False, referenz_modus="relativ"
    )

    if vektor.datum is None:
        vektor = zeit_parsen_vektor(prompt)

    if vektor.datum is None:
        return {
            "status": "fehler",
            "fehler": f"Konnte das neue Datum nicht erkennen. Wann soll '{termin.get('title', '')}' stattfinden?",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_datum"}],
        }

    alte_zeit: datetime = termin["event_time"]
    if not alte_zeit.tzinfo:
        alte_zeit = alte_zeit.replace(tzinfo=tz)

    if vektor.referenz_modus == "absolut":
        logger.info("_update: Referenz-Modus 'absolut' — Referenz ist heute")

    elif vektor.referenz_modus == "relativ":
        vektor_neu: ZeitVektor = zeit_parsen_vektor(zeitausdruck, referenz=alte_zeit)
        if vektor_neu.datum is None:
            vektor_neu = zeit_parsen_vektor(prompt, referenz=alte_zeit)
        if vektor_neu.datum is not None:
            vektor = vektor_neu
        logger.info(f"_update: Referenz-Modus 'relativ' — Referenz ist alter Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y %H:%M')})")

    elif vektor.referenz_modus == "relativ_rueckwaerts":
        vektor_neu = zeit_parsen_vektor(zeitausdruck, referenz=alte_zeit, zukunft_bevorzugt=False)
        if vektor_neu.datum is None:
            vektor_neu = zeit_parsen_vektor(prompt, referenz=alte_zeit, zukunft_bevorzugt=False)
        if vektor_neu.datum is not None:
            vektor = vektor_neu
        logger.info(f"_update: Referenz-Modus 'relativ_rueckwaerts' — Referenz ist alter Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y %H:%M')}), Vergangenheit bevorzugt")

    neues_datum: datetime = vektor.datum

    if vektor.tag_erkannt and not vektor.uhrzeit_erkannt:
        neues_datum = neues_datum.replace(
            hour=alte_zeit.hour, minute=alte_zeit.minute,
            second=0, microsecond=0,
        )
        logger.info(f"_update: Tag neu, Uhrzeit vom alten Termin ({alte_zeit.strftime('%H:%M')})")

    elif not vektor.tag_erkannt and vektor.uhrzeit_erkannt:
        neues_datum = alte_zeit.replace(
            hour=neues_datum.hour, minute=neues_datum.minute,
            second=0, microsecond=0,
        )
        logger.info(f"_update: Uhrzeit neu, Tag vom alten Termin ({alte_zeit.strftime('%d.%m.%Y')})")

    precision = "minute" if vektor.uhrzeit_erkannt or alte_zeit.hour > 0 or alte_zeit.minute > 0 else "day"

    TimelineRepository.invalidate(POSTGRES_URL, termin_id)
    logger.debug(f"_update: Alter Termin {termin_id} invalidiert")

    verifiziert_alt = _verifizieren_termin(termin_id, {"invalidiert": True})

    neuer_id: int = TimelineRepository.insert(
        postgres_url=POSTGRES_URL,
        user_id=state["kontext"].get("user_id", ""),
        event_time=neues_datum,
        event_type=termin.get("event_type", "termin"),
        title=termin.get("title", ""),
        details=termin.get("details"),
        recurring=termin.get("recurring", False),
        precision=precision,
        entitaet_ids=None,
    )

    verifiziert_neu = _verifizieren_termin(neuer_id, {"aktiv": True})
    verifiziert = verifiziert_alt and verifiziert_neu

    lokale_zeit: str = neues_datum.astimezone(tz).strftime("%d.%m.%Y")
    if precision != "day":
        lokale_zeit += f" {neues_datum.astimezone(tz).strftime('%H:%M')}"

    logger.info(f"TimelineAgent: Termin '{termin.get('title')}' verschoben auf {lokale_zeit} "
                f"(alt={termin_id}, neu={neuer_id}), verifiziert={verifiziert}")

    return {
        "ergebnis": f"Termin '{termin.get('title')}' verschoben auf {lokale_zeit}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren",
            "ergebnis": "verschoben",
            "alter_id": termin_id,
            "neuer_id": neuer_id,
            "verifiziert": verifiziert,
        }],
    }


def _delete(state: AgentState) -> dict:
    """Termin invalidieren (Soft-Delete)."""
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository

    termin = state["parameter"].get("termin", {})
    termin_id = termin.get("id")
    title = termin.get("title", "")

    logger.debug(f"_delete: Einstieg — termin_id={termin_id}, title='{title}'")

    if not termin_id:
        return {
            "status": "fehler",
            "fehler": "Kein Termin zum Loeschen gefunden.",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_termin"}],
        }

    TimelineRepository.invalidate(POSTGRES_URL, termin_id)

    verifiziert = _verifizieren_termin(termin_id, {"invalidiert": True})

    logger.info(f"TimelineAgent: Termin '{title}' (ID {termin_id}) invalidiert, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Termin '{title}' geloescht",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "geloescht", "termin_id": termin_id, "verifiziert": verifiziert}],
    }
