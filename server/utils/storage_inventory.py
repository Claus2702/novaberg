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

Diese Datei liest die Zeitpunkte aus der Lage und bildet den Ausgang. Die
Abfrage selbst bekommt sie vom Aufrufer (`lookup`), damit die Rechenschicht
nicht vom Dienst abhaengt, dessen Bestand sie liest.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date, datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE
from utils.storage_claims import (
    INVENTORY_FOUND,
    INVENTORY_NO_MOMENT,
    INVENTORY_NOT_FOUND,
    InventoryCheck,
)
from utils.zeitparser import zeit_parsen_vektor

logger = logging.getLogger("ki_server.storage_inventory")

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


def check_inventory(
    sachlage: object,
    user_id: str,
    lookup: Callable[[str, datetime], list[dict]],
) -> InventoryCheck:
    """Haelt eine Behauptung ohne abgeschlossenen Dienst gegen den Bestand.

    Gerufen nur, wenn die Antwort eine Speicherbehauptung traegt und kein
    Dienst dieses Turns sie deckt. **Gefunden ist erst, was fuer jeden
    Zeitpunkt der Lage gefunden ist:** Welche Sache der behauptende Satz meint,
    ist im Text nicht entscheidbar; traegt die Lage zwei Termine, und nur einer
    steht im Bestand, bleibt der andere eine moegliche falsche Behauptung.

    Vorbedingung: `lookup(user_id, moment)` liefert die Termine zu diesem
        Zeitpunkt, ohne Erinnerungs-Anker (`find_at_moment`), und wirft bei
        einem Lesefehler.
    Nachbedingung: `gefunden`, wenn die Lage mindestens einen Zeitpunkt traegt
        und `lookup` zu jedem einen Termin liefert; `kein_akutes_objekt_mit_zeit`
        ohne Zeitpunkt (dann wird nicht gefragt); sonst `nicht_gefunden`.
    Fehlerfaelle: ein Fehler von `lookup` oder vom Zeitparser geht an den
        Aufrufer — er ist nie `gefunden`, und das stellt der Aufrufer sicher.
    """
    # ── Eingabe-Validierung ─────────────────────
    moments: list[datetime] = acute_moments(sachlage)
    if not moments:
        return InventoryCheck(outcome=INVENTORY_NO_MOMENT, moments=0)

    # ── Verarbeitung ────────────────────────────
    missing: list[datetime] = [m for m in moments if not lookup(user_id, m)]

    # ── Ausgabe-Verifikation ────────────────────
    outcome: str = INVENTORY_NOT_FOUND if missing else INVENTORY_FOUND
    logger.info(
        f"Bestandsabgleich: {len(moments) - len(missing)} von {len(moments)} "
        f"Zeitpunkt(en) im Bestand — {outcome}"
    )
    return InventoryCheck(outcome=outcome, moments=len(moments))
