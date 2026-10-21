"""Such-Node — Findet Termine per Keyword, Datumsbereich oder listet anstehende auf.

Drei Such-Modi:
  1. Keyword: target vorhanden → Suche nach Titel
  2. Zeitraum: zeitausdruck vorhanden → `time_window` (`graph/appointments.py`)
     → Zeitraum oder Tag
  3. Uebersicht: weder target noch zeitausdruck → das proaktive Fenster

**Lesen geht ueber den gemeinsamen Leseweg** (`read_answer`): dasselbe Lesen
wie der Leseschritt hinter dem Router (`memory/timeline_reading.py`), ohne
Erinnerungs-Anker, in denselben Zeilen (`graph/format/appointments.py`).

**Aendern, Loeschen und Verschieben ohne genannten Titel schreiben nie**
(`period_question`): Kein, ein oder mehrere Treffer im Zeitraum ergeben eine
Klaerung, die die gefundenen Termine nennt und um den Termin mit seinem Namen
bittet. Die Antwort darauf schreibt nichts (`resume.py`); erst ein neuer
Auftrag mit Titel geht den Schreibweg. Ein Erinnerungs-Anker ist dort nie ein
Kandidat. Aendern und Loeschen mit genanntem Titel lesen den Rohbestand: Sie
sehen alles, auch den Anker.
"""

import json
import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from agents.base import AgentState
from agents.timeline.event_time import precision_has_time
from config import (
    TIMELINE_SUCHE_LIMIT,
    TIMEZONE,
)
from graph.appointments import (
    SEARCH_LIMIT_MAX,
    Appointment,
    AppointmentWindow,
    proactive_window,
    search_window,
    time_window,
)
from memory.timeline_types import ANCHOR_TYPE, NOT_APPOINTMENTS
from utils.local_time import now_local

logger = logging.getLogger("ki_server.agents.timeline.suche")

#: Die Schreibaktionen, die ohne genannten Titel einen Termin aus einem
#: Zeitraum waehlen muessten — dort wird gefragt, nie geraten.
PERIOD_WRITE_ACTIONS: frozenset[str] = frozenset({"update", "delete", "reschedule"})

#: Das Verb der Rueckfrage je Schreibaktion.
ACTION_VERBS: dict[str, str] = {
    "update": "ändern", "delete": "löschen", "reschedule": "verschieben",
}


def read_answer(state: AgentState, now: datetime) -> dict:
    """Der Leseast: liest ueber den gemeinsamen Leseweg und antwortet in seinen Zeilen.

    Das Fenster ist eine Suche nach Titel (`target`), der Zeitraum des
    Zeitausdrucks (`time_window`) oder das proaktive Fenster. Gelesen wird mit
    `read_appointments` — ohne Erinnerungs-Anker, ein angekommener wird laut
    verworfen —, jede Zeile kommt aus `appointment_line`, ein leeres Fenster
    sagt `empty_line`.

    Vorbedingung: `state["parameter"]["action"]` ist `read`; `now` ist
        zeitzonenbewusst in Ortszeit.
    Nachbedingung: `status` `abgeschlossen` mit je Termin des Paares einer
        Zeile, oder dem Satz *Keine Termine ...*, der das Fenster nennt;
        `fehler` ohne `user_id` oder ohne `character_id`. Ein unlesbarer
        Zeitausdruck sagt, dass nichts gelesen wurde — er ist kein leerer
        Zeitraum.
    Fehlerfaelle: eine andere Aktion oder ein naiver Zeitpunkt wirft
        `ValueError`; ein Lesefehler geht an den Aufrufer.
    """
    from config import POSTGRES_URL
    from graph.format.appointments import appointment_line, empty_line
    from memory.timeline_reading import read_appointments

    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    if parameter.get("action") != "read":
        msg: str = f"read_answer: Aktion {parameter.get('action')!r} ist kein Lesen"
        raise ValueError(msg)
    if now.tzinfo is None:
        msg = "read_answer: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)
    user_id: str = state["kontext"].get("user_id", "")
    if not user_id:
        logger.error("suchen: Lesen ohne user_id — nichts gelesen")
        return {
            "status": "fehler",
            "fehler": "Ohne Nutzerkennung lassen sich keine Termine lesen.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "ohne_user_id"}],
        }
    character_id: str = state["kontext"].get("character_id", "")
    if not character_id:
        logger.error("suchen: Lesen ohne character_id — nichts gelesen")
        return {
            "status": "fehler",
            "fehler": "Ohne Figur lassen sich keine Termine lesen.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "ohne_character_id"}],
        }
    target: str = parameter.get("target", "")
    zeitausdruck: str = parameter.get("zeitausdruck", "")

    # ── Verarbeitung ────────────────────────────
    if target:
        window: AppointmentWindow | None = search_window(
            {"keyword": target, "limit": SEARCH_LIMIT_MAX},
        )
    elif zeitausdruck:
        window = time_window(zeitausdruck, now)
    else:
        window = proactive_window(now)
    if window is None:
        return {
            "ergebnis": f"Den Zeitraum '{zeitausdruck}' konnte ich nicht lesen — "
                        f"es wurden keine Termine gelesen.",
            "status": "abgeschlossen",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "zeit_unlesbar"}],
        }
    reading = read_appointments(window, user_id, character_id, POSTGRES_URL, now)
    lines: list[str] = [appointment_line(a, now) for a in reading.appointments]

    # ── Ausgabe-Verifikation ────────────────────
    if len(lines) != len(reading.appointments):
        msg = f"read_answer: {len(lines)} Zeilen fuer {len(reading.appointments)} Termine"
        raise RuntimeError(msg)
    if not lines:
        empty: str = empty_line(reading)
        logger.debug(f"suchen: Read — {empty}")
        return {
            "ergebnis": f"{empty[0].upper()}{empty[1:]}.",
            "status": "abgeschlossen",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden"}],
        }
    logger.debug(f"suchen: Read — {len(lines)} Termine zurueckgegeben")
    return {
        "ergebnis": "\n".join(lines),
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": f"{len(lines)} Treffer"}],
    }


def raw_matches(
    target: str, zeitausdruck: str, user_id: str, character_id: str, now: datetime,
) -> list[dict]:
    """Die Treffer im Rohbestand fuer Anlegen und fuer Aendern und Loeschen mit Titel.

    Der Schreibweg sieht den ganzen Bestand des Paares, auch den
    Erinnerungs-Anker (`exclude_event_types=()`). Die Fenster sind dieselben
    wie beim Lesen: Suche nach Titel, `time_window` oder das proaktive
    Fenster. Aendern und Loeschen ohne Titel kommen nicht hierher, sondern zu
    `period_question`.

    Vorbedingung: `now` ist zeitzonenbewusst in Ortszeit; das Paar
        (`user_id`, `character_id`) ist vollstaendig.
    Nachbedingung: eine Liste von Zeilen des Paares aus dem Repository, bei
        der Suche nach Titel nur aktive; leer, wenn sich der Zeitausdruck
        nicht lesen laesst.
    Fehlerfaelle: ein naiver Zeitpunkt wirft `ValueError`, ein
        unvollstaendiges Paar ebenso (aus dem Repository); ein Lesefehler geht
        an den Aufrufer; eine Antwort, die keine Liste ist, wirft `TypeError`.
    """
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository

    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "raw_matches: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    treffer: list[dict] = []
    if target:
        treffer = TimelineRepository.find_by_keyword(
            POSTGRES_URL, user_id, character_id, target, "both", TIMELINE_SUCHE_LIMIT,
            exclude_event_types=(),
        )
        treffer = [t for t in treffer if t.get("aktiv", True)]
        logger.debug(f"suchen: Keyword-Suche '{target}' — {len(treffer)} Treffer")
    else:
        window: AppointmentWindow | None = (
            time_window(zeitausdruck, now) if zeitausdruck else proactive_window(now)
        )
        if window is not None:
            treffer = TimelineRepository.find_by_date_range(
                POSTGRES_URL, user_id, character_id, window.start, window.end,
                exclude_event_types=(),
            )
            logger.debug(f"suchen: Zeitraum {window.start:%d.%m.}–{window.end:%d.%m.} "
                         f"({window.kind}) — {len(treffer)} Treffer")

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(treffer, list):
        msg = f"raw_matches: Timeline lieferte {type(treffer).__name__} statt list"
        raise TypeError(msg)
    return treffer


def _period_label(window: AppointmentWindow) -> str:
    """Der Zeitraum eines Fensters als Text: *am TT.MM.JJJJ* oder *vom ... bis ...*.

    Vorbedingung: `window` traegt `start` und `end` (Art `range` oder
        `proactive`).
    Nachbedingung: ein Text, der jeden Tag des Fensters eindeutig nennt.
    Fehlerfaelle: ein Fenster ohne Zeitraum wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if window.start is None or window.end is None:
        msg: str = f"_period_label: Fenster der Art {window.kind} ohne Zeitraum"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    first: str = window.start.strftime("%d.%m.%Y")
    last: str = window.end.strftime("%d.%m.%Y")
    label: str = f"am {first}" if first == last else f"vom {first} bis {last}"

    # ── Ausgabe-Verifikation ────────────────────
    if first not in label or last not in label:
        msg = f"_period_label: {label!r} nennt den Zeitraum {first}–{last} nicht"
        raise RuntimeError(msg)
    return label


def period_candidates(
    window: AppointmentWindow, user_id: str, character_id: str, now: datetime,
) -> list[dict]:
    """Die Termine eines Zeitraums als Kandidaten einer Klaerung, ohne Erinnerungs-Anker.

    Gelesen wird ueber den gemeinsamen Leseweg (`fetch_rows`, der Anker ist in
    der Abfrage ausgeschlossen); `to_appointment` verwirft jeden Anker, der
    trotzdem ankommt, laut. Jeder Kandidat traegt `id`, `title`, `typ` und
    `zeile` aus `appointment_line` — die Zeile nennt die Klaerung.

    Vorbedingung: `window` traegt einen Zeitraum; `user_id` und
        `character_id` nicht leer; `now` zeitzonenbewusst in Ortszeit.
    Nachbedingung: Kandidaten des Paares nach Zeitpunkt sortiert, keiner vom
        Typ `ANCHOR_TYPE`, jeder mit einer `id`.
    Fehlerfaelle: leere `user_id` oder `character_id` wirft `ValueError` (aus
        `fetch_rows`); ein
        Lesefehler geht an den Aufrufer; ein Anker oder eine Zeile ohne `id`
        im Ergebnis wirft `RuntimeError`.
    """
    from config import POSTGRES_URL
    from graph.format.appointments import appointment_line
    from memory.timeline_reading import fetch_rows, to_appointment

    # ── Eingabe-Validierung ─────────────────────
    if now.tzinfo is None:
        msg: str = "period_candidates: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    rows: list = fetch_rows(window, user_id, character_id, POSTGRES_URL, now)
    found: list[tuple[dict, Appointment | None]] = [(row, to_appointment(row, now)) for row in rows]
    kept: list[tuple[dict, Appointment]] = sorted(
        ((row, appointment) for row, appointment in found if appointment is not None),
        key=lambda pair: pair[1].moment,
    )
    candidates: list[dict] = [
        {
            "id": row.get("id"),
            "title": appointment.title,
            "typ": row.get("event_type") or "termin",
            "zeile": appointment_line(appointment, now),
        }
        for row, appointment in kept
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if any(c["typ"] == ANCHOR_TYPE or c["id"] is None for c in candidates):
        msg = f"period_candidates: Anker oder Zeile ohne id unter den Kandidaten: {candidates}"
        raise RuntimeError(msg)
    return candidates


def _question_text(
    action: str, zeitausdruck: str, window: AppointmentWindow | None, candidates: list[dict],
) -> str:
    """Der Text der Klaerung: was im Zeitraum steht, und die Bitte um den Namen.

    Vorbedingung: `action` in `ACTION_VERBS`; `window` ist `None` nur, wenn
        sich `zeitausdruck` nicht lesen liess, und dann ist `candidates` leer.
    Nachbedingung: ein Text, der den Zeitraum nennt (oder den unlesbaren
        Ausdruck), jeden Kandidaten in der Zeile von `appointment_line` und
        die Bitte, den Termin mit seinem Namen zu nennen.
    Fehlerfaelle: eine unbekannte Aktion wirft `KeyError`; Kandidaten ohne
        Fenster werfen `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    verb: str = ACTION_VERBS[action]
    if window is None and candidates:
        msg: str = f"_question_text: {len(candidates)} Kandidaten ohne Fenster"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    ask_name: str = f"Nenn mir den Termin, den ich {verb} soll, mit seinem Namen."
    if window is None:
        text: str = f"Den Zeitraum '{zeitausdruck}' kann ich nicht lesen. {ask_name}"
    else:
        label: str = _period_label(window)
        period: str = f"{label[0].upper()}{label[1:]}"
        lines: str = "\n".join(c["zeile"] for c in candidates)
        if not candidates:
            text = f"{period} finde ich keinen Termin. {ask_name}"
        elif len(candidates) == 1:
            text = (
                f"{period} habe ich diesen Termin gefunden: {candidates[0]['zeile'][2:]}. "
                f"Sag mir mit seinem Namen, ob ich ihn {verb} soll."
            )
        else:
            text = (
                f"{period} habe ich diese Termine gefunden:\n{lines}\n"
                f"Sag mir mit seinem Namen, welchen ich {verb} soll."
            )

    # ── Ausgabe-Verifikation ────────────────────
    if "mit seinem Namen" not in text or any(c["zeile"][2:] not in text for c in candidates):
        msg = f"_question_text: {text!r} nennt nicht jeden Kandidaten und den Namen"
        raise RuntimeError(msg)
    return text


def period_question(state: AgentState, now: datetime) -> dict:
    """Aendern, Loeschen und Verschieben ohne genannten Titel: eine Klaerung, nie ein Schreiben.

    Die Treffer kommen nur aus einem Zeitraum — dem des Zeitausdrucks oder dem
    proaktiven Fenster. Wer *„Loesch meinen Termin im November“* sagt, nennt
    keinen Termin; ein einzelner Treffer ist eine Vermutung, keine Auswahl,
    und ein Ja oder eine Wahl darauf liest sich nicht sicher genug, um zu
    schreiben. Darum ergeben kein, ein und mehrere Treffer dieselbe Klaerung
    (`clarification` im Parameter, den der Dispatch mit der Rueckfrage in
    Redis ablegt): Sie nennt die gefundenen Termine und bittet um den Termin
    mit seinem Namen. Die Antwort darauf schreibt nichts
    (`resume.resume_clarification`).

    Vorbedingung: `action` in `PERIOD_WRITE_ACTIONS`, kein `target`; `now`
        zeitzonenbewusst in Ortszeit.
    Nachbedingung: `status` `rueckfrage` mit `clarification` und ohne `termin`
        im Parameter — der Graph endet, nichts wird geschrieben, und auch die
        Antwort im naechsten Turn schreibt nicht; `fehler` ohne `user_id`
        oder ohne `character_id`.
    Fehlerfaelle: eine andere Aktion, ein genannter Titel oder ein naiver
        Zeitpunkt wirft `ValueError`; ein Lesefehler geht an den Aufrufer.
    """
    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    action: str = parameter.get("action", "")
    if action not in PERIOD_WRITE_ACTIONS or parameter.get("target"):
        msg: str = f"period_question: {action!r} mit Titel {parameter.get('target')!r}"
        raise ValueError(msg)
    if now.tzinfo is None:
        msg = "period_question: Zeitpunkt ohne Zeitzone"
        raise ValueError(msg)
    user_id: str = state["kontext"].get("user_id", "")
    if not user_id:
        logger.error(f"suchen: {action} ohne user_id — nichts gelesen, nichts geschrieben")
        return {
            "status": "fehler",
            "fehler": "Ohne Nutzerkennung lassen sich keine Termine finden.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "ohne_user_id"}],
        }
    character_id: str = state["kontext"].get("character_id", "")
    if not character_id:
        logger.error(f"suchen: {action} ohne character_id — nichts gelesen, nichts geschrieben")
        return {
            "status": "fehler",
            "fehler": "Ohne Figur lassen sich keine Termine finden.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "ohne_character_id"}],
        }
    zeitausdruck: str = parameter.get("zeitausdruck", "")

    # ── Verarbeitung ────────────────────────────
    window: AppointmentWindow | None = (
        time_window(zeitausdruck, now) if zeitausdruck else proactive_window(now)
    )
    candidates: list[dict] = (
        [] if window is None else period_candidates(window, user_id, character_id, now)
    )
    question: str = _question_text(action, zeitausdruck, window, candidates)
    pending: dict = {**parameter, "clarification": True}

    # ── Ausgabe-Verifikation ────────────────────
    if "termin" in pending:
        msg = f"period_question: Rueckfrage traegt einen Termin {pending['termin']!r}"
        raise RuntimeError(msg)
    logger.info(f"suchen: {action} ohne Titel — {len(candidates)} Kandidaten, Klaerung")
    return {
        "parameter": pending,
        "status": "rueckfrage",
        "rueckfrage": question,
        "schritte": state["schritte"]
        + [{"node": "suchen", "ergebnis": "klaerung", "anzahl": len(candidates)}],
    }


def suchen(state: AgentState) -> dict:
    """Sucht Termine in der Datenbank — Lesen ueber `read_answer`, sonst im Rohbestand."""
    target = state["parameter"].get("target", "")
    zeitausdruck = state["parameter"].get("zeitausdruck", "")
    action = state["parameter"].get("action", "")
    user_id = state["kontext"].get("user_id", "")
    tz = ZoneInfo(TIMEZONE)
    now: datetime = now_local()

    logger.debug(f"suchen: Einstieg — action='{action}', target='{target}', "
                 f"zeit='{zeitausdruck}', user_id='{user_id}'")

    # ── Read: der gemeinsame Leseweg ──
    if action == "read":
        return read_answer(state, now)

    # ── Update/Delete ohne Titel: eine Klaerung, die nie schreibt ──
    # ~~Ein Zeitraum ohne Titel waehlte den Einzeltreffer und schrieb~~ → seit
    # dem 17.10.2026 klaert er. *„Loesch den Termin im November“*
    # loeschte sonst ohne Rueckfrage, was im Monat allein stand — auch einen
    # Erinnerungs-Anker; ein Ja oder eine Wahl darauf las sich nicht sicher.
    if action in PERIOD_WRITE_ACTIONS and not target:
        return period_question(state, now)

    # Ab hier der Schreibweg: Aendern und Loeschen sehen den ganzen Bestand
    # des Paares. Ohne Figur wird nichts gesucht und nichts geschrieben.
    character_id: str = state["kontext"].get("character_id", "")
    if not character_id:
        logger.error(f"suchen: {action} ohne character_id — nichts gesucht, nichts geschrieben")
        return {
            "status": "fehler",
            "fehler": "Ohne Figur lassen sich keine Termine schreiben.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "ohne_character_id"}],
        }
    treffer: list[dict] = raw_matches(target, zeitausdruck, user_id, character_id, now)

    # ── Create: Duplikat-Pruefung (Scheibe 12 F) ──
    # ~~Jeder Treffer der Suche oben galt als Duplikat~~ → seit dem 18.09.2026
    # nur ein aktiver Termin am selben Tag mit aehnlichem Titel. `[gemessen
    # 17.09.2026, Betrieb]` Ohne Ziel und Zeit fiel die Suche in die Uebersicht
    # (±14 Tage), und ein Erinnerungs-Anker der KZG galt als Duplikat: Der
    # Dienst meldete "bereits eingetragen" fuer etwas anderes und legte nichts an.
    if action == "create":
        treffer = find_duplicates(target, zeitausdruck, state["aufgabe"], user_id, character_id)
        if treffer:
            # Derselbe Termin steht schon da → melden, nicht doppelt anlegen
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
        logger.debug("suchen: Update/Delete — keine Treffer → Fehler")
        return {
            "status": "fehler",
            "fehler": f"Kein Termin '{target or zeitausdruck}' gefunden.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden"}],
        }

    # ── Update/Delete/Reschedule: Disambiguierung bei mehreren Treffern ──
    # ~~Verschieben nahm bei mehreren Treffern still den ersten~~ → seit dem
    # 17.10.2026 geht es in dieselbe Auswahl. Bei gleichnamigen Terminen wurde
    # sonst der falsche verschoben, ohne dass jemand es merkte.
    if len(treffer) > 1 and action in ("update", "delete", "reschedule"):
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
            # Die Antwort darauf waehlt nicht und schreibt nie, so will es
            # _resume_disambiguierung in resume.py
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


# Worte, die fuer die Aehnlichkeit zweier Titel nichts tragen.
_FUELLWORTE: frozenset[str] = frozenset({
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "am", "an", "im", "in",
    "zum", "zur", "mit", "und", "von", "bei", "termin", "fuer", "für",
})


def _title_words(title: str) -> set[str]:
    """Die tragenden Worte eines Titels, kleingeschrieben, ohne Fuellworte und Kuerzel."""
    return {w for w in re.findall(r"[a-zäöüß]+", str(title).casefold()) if len(w) > 2 and w not in _FUELLWORTE}


def find_duplicates(
    target: str, zeitausdruck: str, aufgabe: str, user_id: str, character_id: str,
) -> list[dict]:
    """Die Termine, die ein neuer Eintrag doppeln wuerde — Scheibe 12 F.

    Die Absicht (14.09.2026): *"Ob das Objekt schon gespeichert ist, kann die
    Fachabteilung besser einschaetzen als der Empfang."* Sie prueft den Bestand
    des Paares und meldet es mit ihrem Ausgang — ein Termin bei einer anderen
    Figur doppelt den neuen nicht.

    Vorbedingung: `target` ist der Titel des neuen Termins; `zeitausdruck` oder
        die Aufgabe tragen seinen Tag; das Paar ist vollstaendig.
    Nachbedingung: aktive Termine des Paares **am selben Tag**, deren Titel mindestens ein
        tragendes Wort mit dem neuen teilt — ohne die Typen aus
        `NOT_APPOINTMENTS`: den Erinnerungs-Anker (den legt die KZG an) und
        das Ereignis einer anderen Person; beide sind kein Termin des
        Menschen, und *„Umzug helfen"* doppelt nicht *„Umzug"* der
        Schwester. **Ohne Titel oder ohne
        erkennbaren Tag: keine Duplikate** — dann entscheidet das Anlegen
        selbst (es meldet den fehlenden Titel oder Tag), statt dass ein
        beliebiger Eintrag als Duplikat gilt.
    Fehlerfaelle: keine Ausnahme; ein Lesefehler des Bestands steht im Log und
        ergibt keine Duplikate — dann wird eher doppelt angelegt als gar nicht.
    """
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository
    from utils.zeitparser import zeit_parsen_vektor

    # ── Eingabe-Validierung ─────────────────────
    worte: set[str] = _title_words(target)
    if not worte:
        return []
    vektor = zeit_parsen_vektor(zeitausdruck) if zeitausdruck else None
    if vektor is None or vektor.datum is None:
        vektor = zeit_parsen_vektor(aufgabe)
    if vektor.datum is None:
        return []

    # ── Verarbeitung ────────────────────────────
    tz = ZoneInfo(TIMEZONE)
    tag = vektor.datum.astimezone(tz)
    von = tag.replace(hour=0, minute=0, second=0, microsecond=0)
    bis = von + timedelta(days=1) - timedelta(seconds=1)
    try:
        am_tag: list[dict] = TimelineRepository.find_by_date_range(
            POSTGRES_URL, user_id, character_id, von, bis,
        )
    except Exception as fehler:  # noqa: BLE001 — der Anlegepfad haelt nicht an
        logger.error(f"suchen: Duplikat-Pruefung nicht moeglich ({type(fehler).__name__}: {fehler}) — keine")
        return []

    # ── Ausgabe ─────────────────────────────────
    return [
        t for t in am_tag
        if t.get("aktiv", True)
        and t.get("event_type") not in NOT_APPOINTMENTS
        and worte & _title_words(t.get("title", ""))
    ]
