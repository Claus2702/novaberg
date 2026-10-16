"""Bestandsabgleich der Speicherbehauptung — eine wahre Wiederholung bleibt stehen.

Die Pruefung in `storage_claims.py` sieht nur den laufenden Turn: Hat kein
Dienst `abgeschlossen` gemeldet, gilt jede Speicherbehauptung als nicht belegt.
Wiederholt die Antwort aber eine fruehere, echte Schreibung, ist die Behauptung
wahr, und die Korrektur schriebe sie falsch um — samt dem Korrektursatz, es sei
nichts gespeichert.

Entschieden am 15.09.2026: **Hinter dem Verfasser prueft der Riegel den Bestand
selbst, nicht das Thinker-Modell.** Beim Termin ist das die Timeline, gefragt
mit Tag und Uhrzeit des akuten Objekts der Lage dieses Turns. Gefunden: eine
Wiederholung, keine Korrektur. Nicht gefunden, kein akutes Objekt mit Tag und
Uhrzeit, oder die Abfrage scheitert: Korrektur wie ohne Abgleich.

**Ein gefundener Termin deckt nur die Behauptung, die ihn nennt.** Die Lage
traegt das akute Objekt des Turns, nicht den Gegenstand jedes Satzes: Ein
*„notiert, dass der Ersatzschluessel beim Nachbarn liegt"* wiederholt keinen
Zahnarzttermin, auch wenn der im Bestand steht. Als Wiederholung gilt ein
Satz deshalb nur, wenn er einen gefundenen Termin nennt — seine Uhrzeit,
seinen Tag oder ein Inhaltswort seines Titels (`names_appointment`). Nennt
ein behauptender Satz keinen, wird korrigiert wie ohne Abgleich, und der
Ausgang `gefunden_nicht_genannt` steht im dauerhaften Eintrag.

Diese Datei liest die Zeitpunkte aus der Lage und bildet den Ausgang. Die
Abfrage selbst bekommt sie vom Aufrufer (`lookup`), damit die Rechenschicht
nicht vom Dienst abhaengt, dessen Bestand sie liest.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from datetime import date, datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE
from utils.local_time import weekday_name
from utils.storage_claims import (
    INVENTORY_FOUND,
    INVENTORY_NO_MOMENT,
    INVENTORY_NOT_FOUND,
    INVENTORY_NOT_NAMED,
    InventoryCheck,
    StorageClaim,
)
from utils.zeitparser import TimeReading, read_time, zeit_parsen_vektor

logger = logging.getLogger("ki_server.storage_inventory")

#: Ein Inhaltswort: grossgeschrieben und mindestens vier Buchstaben lang — im
#: Deutschen ein Hauptwort oder ein Name (*Zahnarzt*, *Berger*). Zugelassen
#: wird, was den Termin positiv nennt; Artikel und Praepositionen fallen durch
#: die Kleinschreibung heraus, *Dr* durch die Laenge. Gelesen wird so der Titel
#: und der behauptende Satz.
_CONTENT_WORD = re.compile(r"\b[A-ZÄÖÜ]\w{3,}")

#: Ein Tag in Ziffern, *„17.10."* oder *„17.10.2026"*. `read_time` blendet diese
#: Form als Datum aus und zaehlt sie nicht unter seinen Tagen.
_NUMERIC_DAY = re.compile(r"\b(\d{1,2})\.\s?(\d{1,2})\.")

#: Die Tagesworte zum Abstand des Termins von heute in Tagen.
_DEICTIC_DAYS: dict[int, tuple[str, ...]] = {
    0: ("heute",),
    1: ("morgen",),
    2: ("übermorgen", "uebermorgen"),
}

#: Die Wege, auf denen ein Satz einen Termin nennt — ihre Namen stehen im Log.
NAMED_BY: tuple[str, ...] = ("uhrzeit", "tag", "titel")

#: Herkunft einer Lage, die nach einem Ausfall vom Vorturn uebernommen wurde
#: (`graph/nodes/sachlage.py::HERKUNFT_AUSFALL`). Ihre Objekte sind nicht die
#: dieses Turns. Eine Kopie, weil die Rechenschicht den Knoten nicht importiert
#: (er zieht die Modelldienste nach); ein Zeuge haelt sie gegen ihre Quelle
#: (`tests/test_storage_inventory.py`, `CopiesBoundToSourceTest`).
FALLBACK_ORIGIN: str = "ausfall_uebernommen"


def object_moment(obj: dict) -> datetime | None:
    """Der Zeitpunkt eines Objekts aus Tag und Uhrzeit seiner gedeckten Werte.

    Jeder gedeckte Wert wird fuer sich mit `zeit_parsen_vektor` gelesen, nicht
    ueber den Namen der Eigenschaft: Ob sie *Datum*, *Tag* oder *Wann* heisst,
    vergibt das Modell. Tag und Uhrzeit duerfen in einem Wert stehen
    (*„Freitag um 10 Uhr"*) oder in zweien (*„Freitag"*, *„10 Uhr"*).

    Vorbedingung: `obj` ist ein Objekt der Lage in der Form von
        `sachlage_form` — `gedeckt` eine Zuordnung Text → Text.
    Nachbedingung: ein zeitzonenbewusster Zeitpunkt in `TIMEZONE`, wenn die
        Werte **genau einen** Tag und **genau eine** Uhrzeit nennen; sonst None.
        Zwei Tage oder zwei Uhrzeiten sind kein Zeitpunkt: Welcher gemeint ist,
        bleibt offen, und ein geratener koennte einen fremden Termin treffen.
    Fehlerfaelle: `gedeckt` ohne Zuordnung oder ein Wert, der kein Text ist,
        wird laut gemeldet und uebergangen. Ein Fehler des Zeitparsers wird
        nicht gefangen — ihn faengt der Knoten, der kompensieren kann.
    """
    # ── Eingabe-Validierung ─────────────────────
    gedeckt: object = obj.get("gedeckt")
    if not isinstance(gedeckt, dict):
        if gedeckt is not None:
            logger.error(
                f"Bestandsabgleich: 'gedeckt' an '{obj.get('name')}' ist "
                f"{type(gedeckt).__name__} statt dict — kein Zeitpunkt"
            )
        return None

    # ── Verarbeitung ────────────────────────────
    tz = ZoneInfo(TIMEZONE)
    days: set[date] = set()
    clock_times: set[tuple[int, int]] = set()
    for prop_name, value in gedeckt.items():
        if not isinstance(value, str):
            logger.error(
                f"Bestandsabgleich: Wert von '{prop_name}' ist "
                f"{type(value).__name__} statt str — uebergangen"
            )
            continue
        parsed = zeit_parsen_vektor(value)
        if parsed.datum is None:
            continue
        local: datetime = parsed.datum.astimezone(tz)
        if parsed.tag_erkannt:
            days.add(local.date())
        if parsed.uhrzeit_erkannt:
            clock_times.add((local.hour, local.minute))

    # ── Ausgabe-Verifikation ────────────────────
    if len(days) != 1 or len(clock_times) != 1:
        return None
    (day,) = days
    ((hour, minute),) = clock_times
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=tz)


def acute_moments(sachlage: object) -> list[datetime]:
    """Die Zeitpunkte der akuten Objekte der Lage dieses Turns.

    Vorbedingung: `sachlage` ist `state["sachlage"]` — ein dict mit `objekte`,
        oder leer.
    Nachbedingung: je akutem Objekt mit Tag und Uhrzeit sein Zeitpunkt
        (`object_moment`), ohne Doppel, in der Reihenfolge der Lage. Leer, wenn
        es keine Lage gibt, wenn sie nach einem Ausfall vom Vorturn uebernommen
        ist, oder wenn kein akutes Objekt Tag und Uhrzeit traegt.
    Fehlerfaelle: eine Lage, die kein dict ist, oder `objekte`, die keine
        Liste sind, werden laut gemeldet und ergeben keine Zeitpunkte — dann
        wird korrigiert wie ohne Abgleich.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not sachlage:
        return []
    if not isinstance(sachlage, dict) or not isinstance(sachlage.get("objekte"), list):
        logger.error(
            f"Bestandsabgleich: Lage ist {type(sachlage).__name__} ohne Objektliste "
            f"— keine Zeitpunkte"
        )
        return []
    if sachlage.get("herkunft") == FALLBACK_ORIGIN:
        logger.info("Bestandsabgleich: Lage nach Ausfall uebernommen — keine Zeitpunkte")
        return []

    # ── Verarbeitung ────────────────────────────
    moments: list[datetime] = []
    for obj in sachlage["objekte"]:
        if not isinstance(obj, dict) or obj.get("akut") is not True:
            continue
        moment: datetime | None = object_moment(obj)
        if moment is not None and moment not in moments:
            moments.append(moment)

    # ── Ausgabe-Verifikation ────────────────────
    if any(m.tzinfo is None for m in moments):  # pragma: no cover — per Konstruktion
        logger.error("Bestandsabgleich: naiver Zeitpunkt aus object_moment — verworfen")
        return []
    return moments


def title_words(rows: list[dict]) -> frozenset[str]:
    """Die Inhaltswoerter der Titel gefundener Termine, kleingeschrieben.

    Gelesen wird der Titel aus dem Bestand, nicht der Name des Objekts der
    Lage: Den Namen vergibt das Modell, der Titel ist, was geschrieben wurde.

    Vorbedingung: `rows` sind Zeilen von `lookup` — dicts mit `title`.
    Nachbedingung: jedes Wort von `_CONTENT_WORD` aus jedem Titel; leer, wenn
        kein Titel eines traegt. Dann nennt ein Satz den Termin nur ueber
        Uhrzeit oder Tag.
    Fehlerfaelle: ein Titel, der kein Text ist, wird laut gemeldet und
        uebergangen — er traegt kein Wort, ein Satz kann ihn nicht nennen.
    """
    # ── Eingabe-Validierung ─────────────────────
    titles: list[str] = []
    for row in rows:
        title: object = row.get("title")
        if not isinstance(title, str):
            logger.error(
                f"Bestandsabgleich: Titel der Timeline-Zeile id={row.get('id')} ist "
                f"{type(title).__name__} statt str — kein Titelwort"
            )
            continue
        titles.append(title)

    # ── Verarbeitung ────────────────────────────
    words: frozenset[str] = frozenset(
        word.lower() for title in titles for word in _CONTENT_WORD.findall(title)
    )

    # ── Ausgabe-Verifikation ────────────────────
    if titles and not words:
        logger.info(
            f"Bestandsabgleich: {len(titles)} Titel ohne Inhaltswort — "
            f"genannt nur ueber Uhrzeit oder Tag"
        )
    return words


def names_appointment(
    sentence: str, moment: datetime, words: frozenset[str], today: date,
) -> tuple[str, ...]:
    """Auf welchen Wegen ein Satz einen gefundenen Termin nennt.

    **Zugelassen wird, was den Termin positiv nennt**, nicht ausgeschlossen,
    was ihn nicht meint — der Wortschatz der Antworten ist offen:
    - `uhrzeit`: eine Stunde des Satzes nach `read_time` (*„um 11 Uhr"*,
      *„um elf"*, *„11:00"*) ist Stunde und Minute des Termins;
    - `tag`: der Satz nennt seinen Tag in Ziffern (*„17.10."*), als Tag des
      Monats (*„den 17."*, *„17. Oktober"*), als Wochentag oder als
      *heute*, *morgen*, *uebermorgen* vom heutigen Tag aus;
    - `titel`: ein Inhaltswort des Satzes beginnt mit einem des Titels oder
      umgekehrt (*Zahnarztes*, *Zahnarzttermin*, *Bergers*). Ein Name traegt
      wie die Art des Termins: Antworten nennen oft den Namen.

    Vorbedingung: `moment` zeitzonenbewusst, `words` aus `title_words`,
        `today` der lokale Tag des Turns.
    Nachbedingung: die zutreffenden Wege in der Reihenfolge von `NAMED_BY`;
        leer heisst, der Satz nennt den Termin nicht.
    Fehlerfaelle: ein naiver `moment` wirft `ValueError`; ein Fehler des
        Zeitparsers wird nicht gefangen — ihn faengt der Knoten.
    """
    # ── Eingabe-Validierung ─────────────────────
    if moment.tzinfo is None:
        msg: str = "Bestandsabgleich: Nennung gegen einen naiven Zeitpunkt"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    local: datetime = moment.astimezone(ZoneInfo(TIMEZONE))
    reading: TimeReading = read_time(sentence, today)
    lowered: str = sentence.lower()
    day_words: tuple[str, ...] = (
        weekday_name(local.date()).lower(),
        *_DEICTIC_DAYS.get((local.date() - today).days, ()),
    )
    by_clock: bool = (local.hour, local.minute) in reading.hours
    by_day: bool = (
        any((d.month, d.day) == (local.month, local.day) for d in reading.days)
        or any(
            (int(m.group(2)), int(m.group(1))) == (local.month, local.day)
            for m in _NUMERIC_DAY.finditer(sentence)
        )
        or any(re.search(rf"\b{w}\b", lowered) for w in day_words)
    )
    sentence_words: list[str] = [w.lower() for w in _CONTENT_WORD.findall(sentence)]
    by_title: bool = any(
        s.startswith(t) or t.startswith(s) for s in sentence_words for t in words
    )

    # ── Ausgabe-Verifikation ────────────────────
    ways: tuple[str, ...] = tuple(
        way for way, hit in zip(NAMED_BY, (by_clock, by_day, by_title), strict=True) if hit
    )
    logger.debug(f"Bestandsabgleich: Satz nennt den Termin {local:%d.%m. %H:%M} ueber {ways}")
    return ways


def check_inventory(
    sachlage: object,
    user_id: str,
    lookup: Callable[[str, datetime], list[dict]],
    claims: tuple[StorageClaim, ...],
    today: date,
) -> InventoryCheck:
    """Haelt eine Behauptung ohne abgeschlossenen Dienst gegen den Bestand.

    Gerufen nur, wenn die Antwort eine Speicherbehauptung traegt und kein
    Dienst dieses Turns sie deckt. **Gefunden ist erst, was fuer jeden
    Zeitpunkt der Lage gefunden ist:** Welche Sache der behauptende Satz meint,
    ist im Text nicht entscheidbar; traegt die Lage zwei Termine, und nur einer
    steht im Bestand, bleibt der andere eine moegliche falsche Behauptung.

    **Und gedeckt ist erst, was jede Behauptung nennt:** Ein gefundener Termin
    deckt nur den Satz, der ihn nennt (`names_appointment`) — die Lage sagt,
    welcher Termin akut ist, nicht, wovon jeder Satz spricht. Nennt einer von
    zwei behauptenden Saetzen keinen gefundenen Termin, bleibt er eine
    moegliche falsche Behauptung, und die Antwort wird korrigiert.

    Vorbedingung: `lookup(user_id, moment)` liefert die Termine zu diesem
        Zeitpunkt, ohne Erinnerungs-Anker (`find_at_moment`), und wirft bei
        einem Lesefehler. `claims` sind die Behauptungen der Antwort, `today`
        der lokale Tag des Turns.
    Nachbedingung: `gefunden`, wenn die Lage mindestens einen Zeitpunkt traegt,
        `lookup` zu jedem einen Termin liefert und jede Behauptung einen davon
        nennt; `gefunden_nicht_genannt`, wenn alles gefunden ist, aber eine
        Behauptung keinen nennt; `kein_akutes_objekt_mit_zeit` ohne Zeitpunkt
        (dann wird nicht gefragt); sonst `nicht_gefunden`.
    Fehlerfaelle: keine Behauptung wirft `ValueError` — der Abgleich hat dann
        nichts zu decken. Ein Fehler von `lookup` oder vom Zeitparser geht an
        den Aufrufer — er ist nie `gefunden`, und das stellt der Aufrufer sicher.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not claims:
        msg: str = "Bestandsabgleich ohne Behauptung"
        raise ValueError(msg)
    moments: list[datetime] = acute_moments(sachlage)
    if not moments:
        return InventoryCheck(outcome=INVENTORY_NO_MOMENT, moments=0)

    # ── Verarbeitung ────────────────────────────
    found: dict[datetime, list[dict]] = {m: lookup(user_id, m) for m in moments}
    missing: list[datetime] = [m for m, rows in found.items() if not rows]
    unnamed: list[StorageClaim] = []
    if not missing:
        words_at: dict[datetime, frozenset[str]] = {
            m: title_words(rows) for m, rows in found.items()
        }
        unnamed = [
            claim for claim in claims
            if not any(names_appointment(claim.sentence, m, w, today) for m, w in words_at.items())
        ]

    # ── Ausgabe-Verifikation ────────────────────
    outcome: str = INVENTORY_FOUND
    if missing:
        outcome = INVENTORY_NOT_FOUND
    elif unnamed:
        outcome = INVENTORY_NOT_NAMED
    naming: str = (
        "Nennung nicht geprueft" if missing
        else f"{len(claims) - len(unnamed)} von {len(claims)} Behauptung(en) nennen einen Termin"
    )
    logger.info(
        f"Bestandsabgleich: {len(moments) - len(missing)} von {len(moments)} "
        f"Zeitpunkt(en) im Bestand, {naming} — {outcome}"
    )
    return InventoryCheck(outcome=outcome, moments=len(moments))
