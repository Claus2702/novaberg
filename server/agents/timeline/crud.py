"""CRUD-Nodes — Erstellen, Verschieben, Loeschen von Timeline-Eintraegen.

Erweitert in Chat 44 (Epic 15): normalisiert-Feld aus Classify im Debug-Log.
Erweitert in Chat 42 (CRUD-Haertung):
- reschedule als eigene Aktion (Alias fuer _update mit zeitlicher Verschiebung)
- Verifikation nach Schreiboperationen (DB-Read nach Write)

Bi-temporales Modell: Update invalidiert den alten Eintrag und legt
einen neuen an. Kein Ueberschreiben — die Historie bleibt erhalten.
"""

import logging
from dataclasses import replace
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from agents.base import AgentState
from agents.timeline.event_time import precision_has_time
from agents.write_outcome import verified_outcome
from config import TIMEZONE
from utils.local_time import weekday_name

if TYPE_CHECKING:
    from agents.timeline.positive_form import RawTimeForm
    from utils.zeitparser import TimeReading, ZeitVektor

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
        logger.error(
            f"Verifikation: Termin ID {termin_id} aktiv={eintrag['aktiv']}, "
            f"erwartet={erwartung['aktiv']}"
        )
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


def _unknown_type(state: AgentState, name: str) -> dict:
    """Das Ergebnis eines Auftrags, dessen Typ die Typquelle nicht kennt.

    Vorbedingung: `name` ist der Typ des Auftrags; `memory/timeline_types.py::
        event_type` hat ihn schon als `ERROR` protokolliert.
    Nachbedingung: ein Fehler mit `ergebnis: unbekannter_typ`; nichts ist
        geschrieben.
    Fehlerfaelle: keine — die Funktion baut nur das Ergebnis.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(state.get("schritte"), list):
        msg: str = f"_unknown_type: schritte ist keine Liste ({state.get('schritte')!r})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    result: dict = {
        "status": "fehler",
        "fehler": f"Unbekannter Termintyp '{name}' — nichts eingetragen.",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "unbekannter_typ"}],
    }

    # ── Ausgabe-Verifikation ────────────────────
    if result["schritte"][-1]["ergebnis"] != "unbekannter_typ":
        msg = "_unknown_type: letzter Schritt traegt nicht den Ausgang"
        raise RuntimeError(msg)
    return result


def _create(state: AgentState) -> dict:
    """Neuen Termin anlegen — Zeitparser fuer Datumsaufloesung."""
    from agents.timeline.magneten import (
        themen_aus_event_type,
        verhaltens_flags_aus_event_type,
    )
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository
    from memory.timeline_types import resubmission_at
    from utils.zeitparser import ZeitVektor, zeit_parsen_vektor

    user_id = state["kontext"].get("user_id", "")
    title = state["parameter"].get("target", "")
    zeitausdruck = state["parameter"].get("zeitausdruck", "")
    event_type = state["parameter"].get("event_type", "termin")
    prompt = state["aufgabe"]
    tz = ZoneInfo(TIMEZONE)

    logger.debug(f"_create: Einstieg — title='{title}', zeit='{zeitausdruck}', typ='{event_type}'")

    # Ein unbekannter Typ bekaeme Merkmale, die niemand fuer ihn entschieden
    # hat; `event_type` hat ihn schon laut protokolliert, geschrieben wird nichts.
    try:
        binding, remind, conflict_check = verhaltens_flags_aus_event_type(event_type)
    except ValueError:
        return _unknown_type(state, event_type)
    themen = themen_aus_event_type(event_type)
    logger.debug(
        f"_create: Magneten abgeleitet — themen={themen}, "
        f"binding={binding}, remind={remind}, conflict_check={conflict_check}"
    )

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

    # Scheibe 12 D: Eine Spanne ("von 10 bis 12 Uhr") loest der Zeitparser
    # nicht auf — der Anfang wird ohne ihren Endteil gelesen.
    if vektor.datum is None:
        from utils.time_span import span_start_text
        for ausdruck in (zeitausdruck, prompt):
            if ausdruck and span_start_text(ausdruck) != ausdruck:
                vektor = zeit_parsen_vektor(span_start_text(ausdruck))
                if vektor.datum is not None:
                    break

    if vektor.datum is None:
        return {
            "status": "fehler",
            "fehler": f"Konnte kein Datum erkennen. Wann soll '{title}' stattfinden?",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_datum"}],
        }

    event_time: datetime = vektor.datum
    precision = "minute" if vektor.uhrzeit_erkannt else "day"

    entitaet_ids: list[int] = []

    # Scheibe 12 D: Nennt der Auftrag eine Spanne, bekommt der Termin sein Ende.
    from utils.time_span import span_end
    event_ende = span_end(zeitausdruck, event_time) or span_end(prompt, event_time, strict=True)

    termin_id: int = TimelineRepository.insert(
        postgres_url=POSTGRES_URL,
        user_id=user_id,
        character_id=state["kontext"].get("character_id", ""),
        event_time=event_time,
        event_type=event_type,
        title=title,
        details=None,
        recurring=False,
        precision=precision,
        entitaet_ids=entitaet_ids if entitaet_ids else None,
        wiedervorlage_am=resubmission_at(remind, event_time),
        themen=themen,
        binding=binding,
        remind=remind,
        conflict_check=conflict_check,
        event_ende=event_ende,
    )

    verifiziert = _verifizieren_termin(termin_id, {"aktiv": True})

    lokale_zeit: str = event_time.astimezone(tz).strftime("%d.%m.%Y")
    if precision_has_time(precision):
        lokale_zeit += f" {event_time.astimezone(tz).strftime('%H:%M')}"

    logger.info(
        f"TimelineAgent: Termin '{title}' angelegt (ID {termin_id}, {lokale_zeit}), "
        f"verifiziert={verifiziert}"
    )

    return verified_outcome({
        "ergebnis": f"Termin '{title}' eingetragen fuer {lokale_zeit}",
        "status": "abgeschlossen",
        "schritte": state["schritte"]
        + [
            {
                "node": "ausfuehren",
                "ergebnis": "erstellt",
                "termin_id": termin_id,
                "verifiziert": verifiziert,
            }
        ],
    }, verifiziert)


def _update(state: AgentState) -> dict:
    """Termin verschieben — bi-temporales Modell.

    Wird sowohl fuer action='update' als auch action='reschedule' aufgerufen.
    Geschrieben wird nur, wenn die Lesung und die Positivform des Rohtexts
    dieselbe neue Uhrzeit ergeben, ein anderer Tag als der des Termins nur,
    wenn eine Form ihn nennt (`_raw_form_agrees`, sonst Ausgang
    `keine_eindeutige_zeit`), und wenn diese Uhrzeit ihre Tageshaelfte
    traegt: Eine Stunde von 1 bis 12 ohne Tageszeit an ihr ("auf 4 Uhr")
    endet in der Rueckfrage nach morgens oder nachmittags
    (`_open_half_of_day`, Ausgang `tageshaelfte_offen`). Sonst endet der
    Auftrag mit der Rueckfrage, ohne `verschieben`. Mit "morgens" an der
    Stunde ("4 Uhr morgens", "morgens um 4") sieht `zeit_parsen_vektor` den
    Tag "morgen" (`tag_erkannt`): Ohne Datum endet der Auftrag in
    `kein_datum`; mit einem Datum, das nicht der Tag des Termins ist, in
    `keine_eindeutige_zeit`; faellt das Datum des Parsers auf den Tag des
    Termins, wird dort die Uhrzeit der Form geschrieben.

    Das Schreiben ist ein Aufruf: `TimelineRepository.verschieben` legt die
    neue Zeile mit Paar, Typ, Merkmalen und `entitaet_ids` der alten an und
    legt die alte mit Verweis auf sie ab, in einer Transaktion.
    """
    from agents.timeline.magneten import verhaltens_flags_aus_event_type
    from config import POSTGRES_URL
    from memory.repositories.timeline_repository import TimelineRepository
    from memory.timeline_types import resubmission_at
    from utils.zeitparser import ZeitVektor, dotted_clock_times, zeit_parsen_vektor

    termin = state["parameter"].get("termin", {})
    termin_id = termin.get("id")
    raw_expression: str = state["parameter"].get("zeitausdruck") or ""
    raw_prompt: str = state["aufgabe"]
    tz = ZoneInfo(TIMEZONE)

    event_type_alt: str = termin.get("event_type", "termin")
    logger.debug(f"_update: Einstieg — termin_id={termin_id}, title='{termin.get('title')}', "
                 f"neuer zeit='{raw_expression}', event_type='{event_type_alt}'")

    try:
        remind: bool = verhaltens_flags_aus_event_type(event_type_alt)[1]
    except ValueError:
        return _unknown_type(state, event_type_alt)

    if not termin_id:
        return {
            "status": "fehler",
            "fehler": "Kein Termin zum Verschieben gefunden.",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_termin"}],
        }

    # Der neue Termin gehoert demselben Paar; `verschieben` uebernimmt es aus
    # der alten Zeile. Ohne Figur im Kontext wird gar nichts angefasst.
    character_id: str = state["kontext"].get("character_id", "")
    if not character_id:
        logger.error(f"_update: Termin {termin_id} ohne character_id — nichts verschoben")
        return {
            "status": "fehler",
            "fehler": "Ohne Figur laesst sich kein Termin verschieben.",
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "ohne_character_id"},
            ],
        }

    # "auf 11.30." am Satzende liest die Normalisierung als Datum; die
    # Positivform unten liest weiter den Rohtext.
    zeitausdruck: str = dotted_clock_times(raw_expression)
    prompt: str = dotted_clock_times(raw_prompt)
    vektor, source_text, reading = _choose_vector(zeitausdruck, prompt)

    if _no_new_time(vektor, reading):
        return {
            "status": "fehler",
            "fehler": f"Konnte das neue Datum nicht erkennen. Wann soll '{termin.get('title', '')}' stattfinden?",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_datum"}],
        }

    alte_zeit: datetime = termin["event_time"]
    if not alte_zeit.tzinfo:
        alte_zeit = alte_zeit.replace(tzinfo=tz)
    # Tag und Uhrzeit des Termins gelten in Ortszeit: "11 Uhr" ist 11 Uhr
    # hier, und der Tag eines Termins um 00:30 ist nicht der Vortag in UTC.
    alte_zeit = alte_zeit.astimezone(tz)
    clock_time: time | None = reading.clock_time()
    decided: bool = _decided_by_reading(vektor, reading)

    if decided:
        # Die Lesung entscheidet: eine Uhrzeit ohne Tag ("bitte auf 11 Uhr")
        # oder ein Tag des Monats ("auf den 20."); was fehlt, kommt vom Termin.
        # Ohne diesen Zweig endete "bitte auf 11 Uhr" in der Rueckfrage nach
        # dem Datum. Ein Datum, das der Parser dazu gerechnet hat, zaehlt
        # nicht: Bei "von 10 Uhr auf 11 Uhr" traegt es die erste Uhrzeit.
        vektor = replace(vektor, datum=_on_day_of(reading, alte_zeit))
        logger.info(f"_update: Lesung entscheidet ({vektor.datum.strftime('%d.%m.%Y %H:%M')}), "
                    f"Rest vom alten Termin ({alte_zeit.strftime('%d.%m.%Y %H:%M')})")

    elif vektor.referenz_modus == "absolut":
        logger.info("_update: Referenz-Modus 'absolut' — Referenz ist heute")

    elif vektor.referenz_modus == "relativ":
        # Ohne Zeitausdruck der Text des Vektors: Ein Tagesausdruck aus dem Satz
        # rechnet dann vom Termin aus wie derselbe als Zeitausdruck.
        vektor_neu: ZeitVektor = zeit_parsen_vektor(zeitausdruck or source_text, referenz=alte_zeit)
        if vektor_neu.datum is None:
            vektor_neu = zeit_parsen_vektor(prompt, referenz=alte_zeit)
        if vektor_neu.datum is not None:
            vektor = vektor_neu
        logger.info(f"_update: Referenz-Modus 'relativ' — Referenz ist alter Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y %H:%M')})")

    elif vektor.referenz_modus == "relativ_rueckwaerts":
        vektor_neu = zeit_parsen_vektor(
            zeitausdruck or source_text, referenz=alte_zeit, zukunft_bevorzugt=False,
        )
        if vektor_neu.datum is None:
            vektor_neu = zeit_parsen_vektor(prompt, referenz=alte_zeit, zukunft_bevorzugt=False)
        if vektor_neu.datum is not None:
            vektor = vektor_neu
        logger.info(f"_update: Referenz-Modus 'relativ_rueckwaerts' — Referenz ist alter Termin "
                    f"({alte_zeit.strftime('%d.%m.%Y %H:%M')}), Vergangenheit bevorzugt")

    neues_datum: datetime = vektor.datum.astimezone(tz)

    if vektor.tag_erkannt and not decided and clock_time is None:
        neues_datum = neues_datum.replace(
            hour=alte_zeit.hour, minute=alte_zeit.minute,
            second=0, microsecond=0,
        )
        logger.info(f"_update: Tag neu, Uhrzeit vom alten Termin ({alte_zeit.strftime('%H:%M')})")
        neues_datum = _own_weekday_means_next_week(neues_datum, alte_zeit, source_text)

    elif vektor.tag_erkannt and not decided:
        # Tag vom Parser, Uhrzeit aus der Lesung: Bei "Freitag von 10 auf 11"
        # nimmt der Parser die erste Uhrzeit, die neue ist die hinter "auf".
        neues_datum = neues_datum.replace(
            hour=clock_time.hour, minute=clock_time.minute, second=0, microsecond=0,
        )
        logger.info(
            f"_update: Tag vom Parser, Uhrzeit aus der Lesung ({clock_time.strftime('%H:%M')})"
        )

    # Ohne Titel ist kein Wort als Bezug zugelassen: nur mehr Rueckfragen.
    title: str = termin.get("title") or ""
    if not _raw_form_agrees(
        (raw_expression, raw_prompt), title, clock_time, neues_datum, alte_zeit,
    ):
        logger.info(f"_update: Lesung und Positivform des Rohtexts uneins "
                    f"({neues_datum.strftime('%d.%m.%Y %H:%M')}) — Rueckfrage")
        return {
            "status": "fehler",
            "fehler": (f"Konnte die neue Uhrzeit nicht eindeutig erkennen. "
                       f"Wann soll '{termin.get('title', '')}' stattfinden?"),
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "keine_eindeutige_zeit"},
            ],
        }

    # "auf 4 Uhr" kann 04:00 oder 16:00 meinen: nicht raten, sondern fragen.
    open_clock: time | None = _open_half_of_day((raw_expression, raw_prompt), title)
    if open_clock is not None:
        logger.info(f"_update: Tageshaelfte zu {open_clock.strftime('%H:%M')} offen — Rueckfrage")
        return {
            "status": "fehler",
            "fehler": _half_of_day_question(open_clock, title),
            "schritte": state["schritte"] + [
                {"node": "ausfuehren", "ergebnis": "tageshaelfte_offen"},
            ],
        }

    precision = (
        "minute"
        if clock_time is not None or vektor.uhrzeit_erkannt
        or alte_zeit.hour > 0 or alte_zeit.minute > 0
        else "day"
    )

    try:
        neuer_id: int = TimelineRepository.verschieben(
            POSTGRES_URL, termin_id,
            event_time=neues_datum,
            precision=precision,
            wiedervorlage_am=resubmission_at(remind, neues_datum),
        )
    except ValueError as exc:
        # Die alte Zeile ist schon abgelegt oder fehlt; `verschieben` hat
        # zurueckgerollt und den Traceback protokolliert.
        logger.error(f"_update: Termin {termin_id} nicht verschoben — {exc}")  # noqa: TRY400
        return {
            "status": "fehler",
            "fehler": f"Der Termin '{termin.get('title', '')}' ist nicht mehr aktiv.",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "nicht_aktiv"}],
        }
    logger.debug(f"_update: Termin {termin_id} verschoben auf {neuer_id}")

    verifiziert_alt = _verifizieren_termin(termin_id, {"invalidiert": True})
    verifiziert_neu = _verifizieren_termin(neuer_id, {"aktiv": True})
    verifiziert = verifiziert_alt and verifiziert_neu

    lokale_zeit: str = neues_datum.astimezone(tz).strftime("%d.%m.%Y")
    if precision_has_time(precision):
        lokale_zeit += f" {neues_datum.astimezone(tz).strftime('%H:%M')}"

    logger.info(f"TimelineAgent: Termin '{termin.get('title')}' verschoben auf {lokale_zeit} "
                f"(alt={termin_id}, neu={neuer_id}), verifiziert={verifiziert}")

    return verified_outcome({
        "ergebnis": f"Termin '{termin.get('title')}' verschoben auf {lokale_zeit}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren",
            "ergebnis": "verschoben",
            "alter_id": termin_id,
            "neuer_id": neuer_id,
            "verifiziert": verifiziert,
        }],
    }, verifiziert)


def _choose_vector(
    time_expression: str | None, prompt: str,
) -> tuple["ZeitVektor", str, "TimeReading"]:
    """Waehlt den Zeitvektor eines Verschiebeauftrags, seinen Text und die Lesung beider Texte.

    Der Vektor: zuerst der des Zeitausdrucks der Klassifikation; ergibt er
    kein Datum, der der ganzen Aeusserung. Erkennt der einen Tag, aber kein
    Datum — dateparser liest keinen Satz ("Verschieb den Zahnarzt auf
    Freitag.") —, gilt der Vektor des Tagesausdrucks allein (`day_phrase`,
    zuerst aus dem Zeitausdruck, dann aus der Aeusserung), wenn er ein Datum
    ergibt; steht ein weiteres Wort am Tag, gibt es keinen, und der Vektor
    ohne Datum bleibt. Die Lesung (`read_time`) liest Zeitausdruck und
    Aeusserung je fuer sich — welche Stunde ein Text als neue nennt, Lage (a)
    oder die Form "von X auf Y" — und fuehrt beide zusammen: Ist einer
    unentschieden oder nennen beide verschiedene, gibt es keine neue Uhrzeit;
    eine Uhrzeit des Zeitausdrucks geht nicht verloren, wenn der Vektor der
    Aeusserung gilt.

    Vorbedingung: `prompt` ist die Aeusserung des Auftrags; `time_expression`
        darf leer oder None sein (die Klassifikation fand keinen).
    Nachbedingung: ein Vektor, der Text, aus dem er gelesen ist (Zeitausdruck,
        Aeusserung oder Tagesausdruck), und die Lesung beider Texte; traegt der
        Vektor ein Datum, hat es eine Zeitzone.
    Fehlerfaelle: eine Aeusserung, die kein Text ist, wirft `TypeError`; ein
        Datum ohne Zeitzone aus dem Parser wirft `ValueError` — der Tag des
        Termins waere sonst in der Zone des Behaelters gelesen.
    """
    from utils.zeitparser import (
        TimeReading,
        ZeitVektor,
        day_phrase,
        read_time,
        zeit_parsen_vektor,
    )

    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(prompt, str):
        msg: str = f"_choose_vector: Aeusserung ist kein Text ({type(prompt).__name__})"
        raise TypeError(msg)
    expression: str = time_expression or ""

    # ── Verarbeitung ────────────────────────────
    vector: ZeitVektor = zeit_parsen_vektor(expression) if expression else ZeitVektor(
        datum=None, tag_erkannt=False, uhrzeit_erkannt=False, referenz_modus="relativ"
    )
    source_text: str = expression
    if vector.datum is None:
        vector, source_text = zeit_parsen_vektor(prompt), prompt
    phrase: str = ""
    if vector.datum is None and vector.tag_erkannt:
        phrase = day_phrase(expression) or day_phrase(prompt)
    phrase_vector: ZeitVektor | None = zeit_parsen_vektor(phrase) if phrase else None
    if phrase_vector is not None and phrase_vector.datum is not None:
        logger.info(f"_choose_vector: Satz ohne Datum, Tag aus '{phrase}'")
        vector, source_text = phrase_vector, phrase
    reading: TimeReading = read_time(expression).merged(read_time(prompt))

    # ── Ausgabe-Verifikation ────────────────────
    if vector.datum is not None and vector.datum.tzinfo is None:
        msg = f"_choose_vector: Datum ohne Zeitzone ({vector.datum}) aus '{source_text}'"
        raise ValueError(msg)
    return vector, source_text, reading


def _no_new_time(vector: "ZeitVektor", reading: "TimeReading") -> bool:
    """Ob Vektor und Lesung keinen neuen Zeitpunkt hergeben, ohne zu raten.

    Wahr — also die Rueckfrage, kein Schreiben — in drei Lagen:
    1. Die Lesung ist unklar (`TimeReading.unclear`): Stunden ohne neue
       Uhrzeit. Neu ist eine Stunde nur, wenn ein Text genau eine traegt oder
       genau zwei in der Form "von X auf Y" / "von X nach Y" (`_stated_hour`
       im Zeitparser) und Satz und Zeitausdruck nicht zwei verschiedene
       nennen. Jede andere Lage mit Stunden ist unklar: zwei Stunden ohne
       diese Form ("auf 10 oder 11 Uhr", "auf 11, nicht auf 10 Uhr", "auf 11
       Uhr und den Friseur auf 14 Uhr", "von 10 bis 12 Uhr", "zwischen 10 und
       11 Uhr"), drei Stunden ("von 10 auf 11 oder 12 Uhr"), eine nackte Zahl
       allein nicht hinter "auf"/"nach" ("Meeting 2"), eine unmoegliche ("25
       Uhr"). Eine Stunde ist auch ein Zahlwort ("auf zehn, nicht auf elf
       Uhr", "auf elf oder zwoelf Uhr"), eine Ordinalzahl nicht ("den
       zehnten"; `_read_time` im Zeitparser). Dazu eine Zahl im Zweifel ("auf
       11.", "viertel nach 11", "elf Uhr dreissig") und mehr als ein Tag des
       Monats. Ebenso, wenn der Parser eine Uhrzeit erkennt und die Lesung
       keine neue hergibt.
    2. Der Parser erkennt einen Tag, aber kein Datum — auch nicht aus dem
       Tagesausdruck allein (`_choose_vector`): ein Widerspruch wie "heute
       Freitag" an einem Donnerstag, oder ein weiteres Wort am Tag ("Freitag
       naechste Woche"). Oder sein Datum liegt an einem anderen Tag als dem
       genannten Tag des Monats.
    3. Kein Datum, und die Lesung entscheidet nicht (`_decided_by_reading`).

    Vorbedingung: `vector` und `reading` stammen aus `_choose_vector`.
    Nachbedingung: wahr genau dann, wenn `_update` mit der Rueckfrage enden
        muss; ist es falsch, traegt der Vektor ein Datum mit Zone oder die
        Lesung entscheidet.
    Fehlerfaelle: ein Datum ohne Zone wirft `ValueError`, keine Lesung
        `TypeError` (`_decided_by_reading`).
    """
    # ── Eingabe-Validierung ─────────────────────
    if vector.datum is not None and vector.datum.tzinfo is None:
        msg: str = f"_no_new_time: Datum ohne Zone ({vector.datum})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    decided: bool = _decided_by_reading(vector, reading)
    named_day: date | None = reading.day()
    unclear: bool = reading.unclear() or (
        vector.uhrzeit_erkannt and reading.clock_time() is None
    )
    day_disagrees: bool = vector.tag_erkannt and (
        vector.datum is None
        or (named_day is not None
            and vector.datum.astimezone(ZoneInfo(TIMEZONE)).date() != named_day)
    )
    no_time: bool = unclear or day_disagrees or (vector.datum is None and not decided)

    # ── Ausgabe ─────────────────────────────────
    return no_time


def _decided_by_reading(vector: "ZeitVektor", reading: "TimeReading") -> bool:
    """Ob die Lesung den neuen Zeitpunkt bestimmt statt des Datums aus dem Parser.

    So ist es, wenn die Lesung einen Tag des Monats nennt ("auf den 20."), den
    der Parser nicht kennt, oder eine neue Uhrzeit ohne Tag ("auf 11 Uhr"). Ein
    Datum, das der Parser fuer eine Uhrzeit ohne Tag rechnet, zaehlt nicht: Es
    liegt heute oder morgen und traegt bei zwei Uhrzeiten die erste ("von 10
    Uhr auf 11 Uhr" -> 10:00).

    Vorbedingung: `reading` stammt aus `read_time`.
    Nachbedingung: wahr genau dann, wenn `reading.day()` gesetzt ist oder der
        Parser keinen Tag erkennt und `reading.clock_time()` gesetzt ist.
    Fehlerfaelle: etwas anderes als eine `TimeReading` ist ein
        Programmierfehler und wirft `TypeError`.
    """
    from utils.zeitparser import TimeReading

    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(reading, TimeReading):
        msg: str = f"_decided_by_reading: keine TimeReading ({type(reading).__name__})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    decided: bool = reading.day() is not None or (
        not vector.tag_erkannt and reading.clock_time() is not None
    )

    # ── Ausgabe ─────────────────────────────────
    return decided


def _raw_form_agrees(
    texts: tuple[str, ...], title: str, reading_clock: time | None,
    new_time: datetime, old_time: datetime,
) -> bool:
    """Ob die Positivform des Rohtexts dieselbe neue Uhrzeit ergibt, die geschrieben wuerde.

    Die zweite, unabhaengige Pruefung vor jedem Schreiben: `raw_time_form`
    liest Zeitausdruck und Aeusserung, wie sie ankamen, vor jeder
    Normalisierung; ein leerer Text zaehlt nicht. Ausserhalb der Form laesst
    sie nur das Verb, Fuellwoerter und ganze Inhaltswoerter von `title`, dem
    Titel des Termins, zu, dazu Inhaltswort + ["s"] + "termin". Wahr nur in
    zwei Lagen:
    1. Kein Text liegt ausserhalb der Formen, die Formen nennen zusammen
       genau eine Uhrzeit, und sie ist die Uhrzeit der Lesung und die von
       `new_time` ("auf 16 Uhr", "von 10 auf 15:30", "auf Freitag um 4 Uhr
       nachmittags"). Eine Tageszeit an der Uhrzeit rechnet die Form mit
       ("4 Uhr nachmittags" ist 16:00). Wahr heisst hier noch nicht
       schreiben: Nennt eine Form eine Stunde von 1 bis 12 ohne Tageszeit
       ("auf 11 Uhr", "von 10 auf 11:30", "auf Freitag um 11"), fragt
       `_update` danach nach der Tageshaelfte (`_open_half_of_day`).
    2. Kein Text liegt ausserhalb der Formen und keine Form nennt eine
       Uhrzeit ("auf Freitag", "Freitag"): Dann nennt auch die Lesung keine,
       und `new_time` traegt die Uhrzeit von `old_time`.
    In beiden Lagen gilt fuer den Tag: Nennt keine Form einen Tag
    (`RawTimeForm.day_named`), muss `new_time` am Tag von `old_time` liegen.
    Der Zeitparser liest einen Tag auch dort, wo der Satz keinen nennt —
    "morgens" enthaelt "morgen" —, und "4 Uhr morgens" schriebe sonst still
    den Tag nach dem Termin oder nach heute.
    Sonst falsch, also die Rueckfrage: ein Text ausserhalb der Formen ("auf
    11h", "vom Vormittag auf den Nachmittag", "auf halb elf", "auf Fr. um 11
    Uhr", ein unbekanntes Wort), zwei
    verschiedene Uhrzeiten in Zeitausdruck und Aeusserung, Form und Lesung
    uneins, oder ein anderer Tag als der des Termins, den keine Form nennt.
    Ob der genannte Tag der geschriebene ist, vergleicht die Pruefung nicht.

    Vorbedingung: `texts` sind die Rohtexte, `title` ein Text (leer erlaubt);
        `new_time` und `old_time` in Ortszeit mit Zone.
    Nachbedingung: wahr genau in den zwei Lagen oben, verglichen auf die
        Minute, und ohne genannten Tag am Tag von `old_time`.
    Fehlerfaelle: ein Text oder Titel, der keiner ist, wirft `TypeError`;
        eine Zeit ohne Zone `ValueError`.
    """
    from agents.timeline.positive_form import raw_time_form

    # ── Eingabe-Validierung ─────────────────────
    if not all(isinstance(text, str) for text in (*texts, title)):
        msg: str = f"_raw_form_agrees: kein Text unter {texts!r}, {title!r}"
        raise TypeError(msg)
    if new_time.tzinfo is None or old_time.tzinfo is None:
        msg = f"_raw_form_agrees: Zeit ohne Zone ({new_time}, {old_time})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    forms: list["RawTimeForm | None"] = [
        raw_time_form(text, title) for text in texts if text.strip()
    ]
    written: time = time(new_time.hour, new_time.minute)
    if any(form is None for form in forms):
        agrees: bool = False
    else:
        named: set[time] = {form.clock for form in forms if form.clock is not None}
        day_allowed: bool = (
            any(form.day_named for form in forms) or new_time.date() == old_time.date()
        )
        agrees = day_allowed and (
            named == {written} and reading_clock == written
            if named
            else reading_clock is None and written == time(old_time.hour, old_time.minute)
        )

    # ── Ausgabe ─────────────────────────────────
    return agrees


#: Die Woerter der Rueckfrage nach der Tageshaelfte: (erste Stunde, letzte
#: Stunde, Tageszeit der Lesart bis Mittag, Tageszeit der Lesart danach), fuer
#: jede Stunde von 1 bis 12 genau eine Zeile. Jedes Wort ist ein Schluessel der
#: Tageszeiten des Zeitparsers (`TIME_VOCABULARY.dayparts`).
_HALF_OF_DAY_WORDS: tuple[tuple[int, int, str, str], ...] = (
    (1, 5, "morgens", "nachmittags"),
    (6, 10, "morgens", "abends"),
    (11, 11, "vormittags", "abends"),
    (12, 12, "mittags", "nachts"),
)


def _open_half_of_day(texts: tuple[str, ...], title: str) -> time | None:
    """Die neue Uhrzeit, deren Tageshaelfte der Auftrag offen laesst — oder None.

    Nennt eine Positivform eine Stunde von 1 bis 12 ohne Tageszeit an ihr
    ("auf 4 Uhr", "auf 4:30", "auf Freitag um 11"), ist offen, ob morgens
    oder nachmittags gemeint ist; `_update` schreibt dann nicht, sondern
    fragt. Das gilt unabhaengig von der Uhrzeit des Termins. Gelesen werden
    dieselben Rohtexte wie in `_raw_form_agrees`, also auch der Zeitausdruck
    des Modells: Laesst er die Tageszeit weg, die der Satz nennt, fragt
    `_update` lieber einmal zu oft. Eine Tageszeit nur im Titel
    ("Nachmittagskaffee") oder ohne Stunde zaehlt nicht.

    Vorbedingung: `texts` sind die Rohtexte, `title` der Titel; fuer beide
        hat `_raw_form_agrees` wahr ergeben.
    Nachbedingung: die Uhrzeit der ersten Form mit offener Tageshaelfte
        (`RawTimeForm.half_of_day_open`), sonst None.
    Fehlerfaelle: ein Text oder Titel, der keiner ist, wirft `TypeError`; ein
        Text ohne Positivform `ValueError` — dann waere die Funktion vor
        `_raw_form_agrees` gerufen worden.
    """
    from agents.timeline.positive_form import raw_time_form

    # ── Eingabe-Validierung ─────────────────────
    if not all(isinstance(text, str) for text in (*texts, title)):
        msg: str = f"_open_half_of_day: kein Text unter {texts!r}, {title!r}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    forms: list["RawTimeForm | None"] = [
        raw_time_form(text, title) for text in texts if text.strip()
    ]
    if any(form is None for form in forms):
        msg = f"_open_half_of_day: ein Text ohne Positivform unter {texts!r}"
        raise ValueError(msg)
    open_clocks: list[time] = [
        form.clock for form in forms
        if form is not None and form.clock is not None and form.half_of_day_open()
    ]

    # ── Ausgabe ─────────────────────────────────
    return open_clocks[0] if open_clocks else None


def _half_of_day_question(clock: time, title: str) -> str:
    """Die Rueckfrage nach der Tageshaelfte einer Uhrzeit von 1 bis 12 Uhr.

    Der Satz nennt den Titel, die Stunde und beide Lesarten mit Tageszeit und
    Uhrzeit: "Soll 'Kaffee' um 4 Uhr morgens (04:00) oder um 4 Uhr
    nachmittags (16:00) stattfinden?"; mit Minuten "um 4:30 Uhr morgens
    (04:30)". Die Woerter je Stunde stehen in `_HALF_OF_DAY_WORDS`; an der
    12 sind es "mittags" (12:00) und "nachts" (00:00).

    Vorbedingung: `clock` hat eine Stunde in 1..12, `title` ist ein Text.
    Nachbedingung: ein Fragesatz mit beiden Lesarten, die zweite zwoelf
        Stunden nach der ersten.
    Fehlerfaelle: eine Uhrzeit ausserhalb 1..12 Uhr wirft `ValueError`, ein
        Titel, der kein Text ist, `TypeError`; ein Wort, das nicht in
        `TIME_VOCABULARY.dayparts` steht, `ValueError`.
    """
    from utils.zeitparser import TIME_VOCABULARY

    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(clock, time) or not 1 <= clock.hour <= 12:
        msg: str = f"_half_of_day_question: keine Uhrzeit von 1 bis 12 Uhr ({clock!r})"
        raise ValueError(msg)
    if not isinstance(title, str):
        msg = f"_half_of_day_question: kein Titel ({title!r})"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    first_word, second_word = next(
        (first, second) for low, high, first, second in _HALF_OF_DAY_WORDS
        if low <= clock.hour <= high
    )
    other: time = time((clock.hour + 12) % 24, clock.minute)
    spoken: str = f"{clock.hour}:{clock.minute:02d}" if clock.minute else str(clock.hour)
    question: str = (
        f"Soll '{title}' um {spoken} Uhr {first_word} ({clock.strftime('%H:%M')}) "
        f"oder um {spoken} Uhr {second_word} ({other.strftime('%H:%M')}) stattfinden?"
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not {first_word, second_word} <= TIME_VOCABULARY.dayparts.keys():
        msg = f"_half_of_day_question: Tageszeit ohne Schluessel ({first_word}, {second_word})"
        raise ValueError(msg)
    return question


def _on_day_of(reading: "TimeReading", old_time: datetime) -> datetime:
    """Der neue Zeitpunkt aus der Lesung; was sie nicht nennt, kommt vom Termin.

    Der Tag ist `reading.day()`, sonst der Tag von `old_time`; die Uhrzeit ist
    `reading.clock_time()`, sonst die Uhrzeit von `old_time` auf die Minute.

    Vorbedingung: `old_time` traegt eine Zeitzone (Ortszeit), die Lesung
        nennt einen Tag oder eine Uhrzeit.
    Nachbedingung: ein Zeitpunkt in der Zone von `old_time` am Ziel-Tag.
    Fehlerfaelle: keine Lesung wirft `TypeError`; eine Zeit ohne Zone oder
        eine Lesung ohne Tag und ohne Uhrzeit ist ein Programmierfehler und
        wirft `ValueError`.
    """
    from utils.zeitparser import TimeReading

    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(reading, TimeReading):
        msg: str = f"_on_day_of: keine TimeReading ({type(reading).__name__})"
        raise TypeError(msg)
    named_day: date | None = reading.day()
    clock_time: time | None = reading.clock_time()
    if old_time.tzinfo is None or (named_day is None and clock_time is None):
        msg = f"_on_day_of: Zeit ohne Zone oder Lesung ohne Tag und Uhrzeit ({reading}, {old_time})"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    target_day: date = named_day if named_day is not None else old_time.date()
    target_clock: time = (
        clock_time if clock_time is not None else time(old_time.hour, old_time.minute)
    )
    new_time: datetime = datetime.combine(target_day, target_clock, tzinfo=old_time.tzinfo)

    # ── Ausgabe-Verifikation ────────────────────
    if new_time.date() != target_day:
        msg = f"_on_day_of: Tag gewechselt ({target_day} -> {new_time})"
        raise ValueError(msg)
    return new_time


def _own_weekday_means_next_week(
    new_time: datetime, old_time: datetime, source_text: str,
) -> datetime:
    """Ein genannter Wochentag, der auf den Tag des Termins selbst faellt, meint den naechsten.

    "Verschieb den Zahnarzt auf Freitag" bei einem Termin am Freitag ist
    keine Verschiebung auf denselben Tag.

    Vorbedingung: beide Zeitpunkte in Ortszeit; `source_text` ist der Text,
        aus dem der neue Tag gelesen wurde.
    Nachbedingung: `new_time` unveraendert, ausser es liegt am Tag von
        `old_time` und der Text nennt dessen Wochentag — dann sieben Tage spaeter.
    Fehlerfaelle: eine Zeit ohne Zone wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if new_time.tzinfo is None or old_time.tzinfo is None:
        msg: str = f"_own_weekday_means_next_week: Zeit ohne Zone ({new_time}, {old_time})"
        raise ValueError(msg)
    if new_time.date() != old_time.date():
        return new_time

    # ── Verarbeitung ────────────────────────────
    if weekday_name(old_time).lower() not in (source_text or "").lower():
        return new_time
    moved: datetime = new_time + timedelta(days=7)
    logger.info(f"_update: Wochentag des Termins selbst genannt — naechster "
                f"({moved.strftime('%d.%m.%Y')})")

    # ── Ausgabe-Verifikation ────────────────────
    if moved.date() <= old_time.date():
        msg = f"_own_weekday_means_next_week: {moved} liegt nicht nach {old_time}"
        raise ValueError(msg)
    return moved


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

    logger.info(
        f"TimelineAgent: Termin '{title}' (ID {termin_id}) invalidiert, verifiziert={verifiziert}"
    )

    return verified_outcome({
        "ergebnis": f"Termin '{title}' geloescht",
        "status": "abgeschlossen",
        "schritte": state["schritte"]
        + [
            {
                "node": "ausfuehren",
                "ergebnis": "geloescht",
                "termin_id": termin_id,
                "verifiziert": verifiziert,
            }
        ],
    }, verifiziert)
