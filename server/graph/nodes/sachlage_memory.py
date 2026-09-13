"""Scheibe 11 im Knoten — die Objekte eines Turns ablegen und an die Welt binden.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 11. Das Ablegen
selbst macht `memory/sachlage_properties.py`; hier sitzt, was daraus folgt:

**Die Entitaet kommt spaeter (Entscheidung des Eigentuemers, 13.09.2026).**
Erst wird festgehalten, dann gebunden, sobald es eine Referenz gibt. Die
Referenzen eines Turns sind seine Magnete (F-MAGNET-1): Die Salienz liest
Eigennamen aus, `agents/kzg/magnete.py` loest sie zu `entitaeten` auf und
schreibt sie in den KZG-Eintrag, `verbindung` haelt Turn und Eintrag zusammen.
`[gemessen 12.09.2026, 22:50 UTC]` Die Haelfte des Nutzers steht **vor** der
Sachlage (22:50:26 gegen 22:50:46), die von Novas Antwort erst danach. Ein
Objekt ohne Entitaet wird deshalb bei **jedem** Auftreten gegen die Magnete
seiner juengsten Turns gehalten (`SACHLAGE_BINDUNG_TURN_FENSTER`) — so holt der
naechste Turn die zweite Haelfte nach, und ein Objekt, das erst Tage spaeter
wieder genannt wird, findet seine Referenz ueber den LZG-Knoten, wenn der
KZG-Eintrag laengst verfallen ist.

**Die Namensregel ist streng:** gleich, oder Enthaltensein ab vier Zeichen —
dieselbe Schwelle wie die Objektzuordnung der Plausibilitaet — und nie, wenn
zwei Entitaeten passen. Eine falsche Bindung haengt eine Sache an die falsche
Welt; eine fehlende wird beim naechsten Auftreten nachgeholt.

**Der Zeitanker ist enger:** Nur wenn die Magnete **dieses** Turns genau einen
Timeline-Eintrag nennen und der Wert einer gedeckten Eigenschaft einen
Zeitausdruck traegt (`utils/zeitparser`), bekommt diese Eigenschaft ihn.
"""

import logging
from dataclasses import dataclass

from config import POSTGRES_URL, SACHLAGE_BINDUNG_TURN_FENSTER, redis_client
from memory.sachlage_properties import (
    BINDING_TURN_MAGNET,
    bind_entity,
    bind_timeline,
    entity_names,
    record_turn_objects,
    text_key,
    turn_links,
    unbound_objects,
)
from utils.zeitparser import zeit_parsen_vektor

logger = logging.getLogger("ki_server.sachlage.memory")

# Ab welcher Laenge ein Name in einem anderen enthalten sein darf, um zu binden.
MIN_CONTAINED_CHARS: int = 4


@dataclass(frozen=True)
class TurnMagnet:
    """Die Magnete eines KZG-Eintrags eines Turns — reiner Datencontainer."""

    turn_id: str
    entitaet_ids: tuple[int, ...]
    timeline_id: int | None


def _ids(roh: object) -> tuple[int, ...]:
    """Entitaets-ids aus dem KZG-Feld (»3,4«) oder der LZG-Spalte (Liste)."""
    teile: list = roh if isinstance(roh, list) else str(roh or "").split(",")
    ids: list[int] = []
    for teil in teile:
        try:
            ids.append(int(str(teil).strip()))
        except ValueError:
            continue
    return tuple(ids)


def _timeline(roh: object) -> int | None:
    try:
        return int(str(roh).strip()) if roh not in (None, "", "None") else None
    except ValueError:
        return None


def collect_magnets(turn_ids: list[str]) -> list[TurnMagnet]:
    """Die Magnete der genannten Turns: aus dem KZG-Hash, sonst aus dem LZG-Knoten.

    Vorbedingung: `turn_ids` sind Kennungen aus `sachlage_objekt_turn`.
    Nachbedingung: Ein TurnMagnet je Verbindung, die Entitaeten oder einen
        Zeitanker traegt; Verbindungen ohne beides fallen weg.
    Fehlerfaelle: Ein Redis-Fehler ist laut und laesst die KZG-Seite leer —
        die LZG-Seite traegt dann, wo es sie gibt.
    """
    magnete: list[TurnMagnet] = []
    for link in turn_links(POSTGRES_URL, turn_ids):
        try:
            kzg_ids, kzg_zeit = redis_client.hmget(str(link["kzg_id"]), "entitaet_ids", "timeline_id")
        except Exception as fehler:  # noqa: BLE001 — die LZG-Seite traegt weiter
            logger.warning(
                f"Sachlage-Bindung: KZG-Magnete von '{link['kzg_id']}' nicht lesbar "
                f"({type(fehler).__name__}: {fehler})"
            )
            kzg_ids, kzg_zeit = None, None
        entitaeten: tuple[int, ...] = _ids(kzg_ids) or _ids(link.get("lzg_entitaet_ids"))
        zeit: int | None = _timeline(kzg_zeit) or _timeline(link.get("lzg_timeline_id"))
        if entitaeten or zeit is not None:
            magnete.append(TurnMagnet(str(link["turn_id"]), entitaeten, zeit))
    return magnete


def match_entity(object_name: str, names: dict[int, str]) -> int | None:
    """Die eine Entitaet, deren Name zum Objekt passt — sonst keine.

    Nachbedingung: Eine id, wenn genau eine Entitaet gleich heisst oder (ab
        `MIN_CONTAINED_CHARS`) den Objektnamen enthaelt bzw. in ihm steht.
    """
    schluessel: str = text_key(object_name)
    if not schluessel:
        return None
    treffer: list[int] = []
    for entitaet_id, name in names.items():
        anderer: str = text_key(name)
        if not anderer:
            continue
        kuerzer: int = min(len(schluessel), len(anderer))
        if anderer == schluessel or (
            kuerzer >= MIN_CONTAINED_CHARS and (anderer in schluessel or schluessel in anderer)
        ):
            treffer.append(entitaet_id)
    if len(treffer) > 1:
        logger.info(
            f"Sachlage-Bindung: '{object_name}' passt zu {len(treffer)} Entitaeten "
            f"{sorted(treffer)} — nicht gebunden"
        )
        return None
    return treffer[0] if treffer else None


def _has_time_expression(wert: str) -> bool:
    """Traegt der Wert einen Tag oder eine Uhrzeit?"""
    try:
        vektor = zeit_parsen_vektor(wert)
    except Exception as fehler:  # noqa: BLE001 — ein Parserfehler bindet nichts
        logger.warning(f"Sachlage-Bindung: Zeitparser an {wert[:60]!r} gescheitert ({fehler})")
        return False
    return bool(vektor.tag_erkannt or vektor.uhrzeit_erkannt)


def remember_objects(
    user_id:      str,
    character_id: str,
    turn_id:      str,
    verlauf_id:   int,
    sachlage:     dict,
) -> dict:
    """Legt die Objekte einer gerechneten Sachlage ab und bindet, was sich binden laesst.

    Vorbedingung: `sachlage` ist gegen die Form gehalten; `verlauf_id` ist die
        Zeile dieses Turns in `sachlage_verlauf`.
    Nachbedingung: Ein dict mit `abgelegt`, Zaehlung, `gebunden` und
        `zeitanker` — auf jedem Weg, auch ohne Ablage (dann `abgelegt=False`).
    Fehlerfaelle: Die Repository-Funktionen melden selbst und liefern leer;
        hier wirft nichts.

    Returns:
        Die Zusammenfassung fuer Log und Protokoll.
    """
    # ── Eingabe-Validierung ─────────────────────
    ergebnis = record_turn_objects(
        POSTGRES_URL, user_id=user_id, character_id=character_id,
        turn_id=turn_id, verlauf_id=verlauf_id, sachlage=sachlage,
    )
    if ergebnis is None:
        return {"abgelegt": False, "gebunden": 0, "zeitanker": 0}

    # ── Verarbeitung: Entitaeten ────────────────
    offen: list[dict] = unbound_objects(
        POSTGRES_URL, user_id, character_id, list(ergebnis.object_ids),
        SACHLAGE_BINDUNG_TURN_FENSTER,
    )
    turn_ids: list[str] = sorted({t for o in offen for t in (o.get("turn_ids") or [])} | {turn_id})
    magnete: list[TurnMagnet] = collect_magnets(turn_ids)
    gebunden: int = 0
    if offen:
        je_turn: dict[str, set[int]] = {}
        for magnet in magnete:
            je_turn.setdefault(magnet.turn_id, set()).update(magnet.entitaet_ids)
        alle: set[int] = set().union(*je_turn.values()) if je_turn else set()
        namen: dict[int, str] = entity_names(POSTGRES_URL, sorted(alle))
        for objekt in offen:
            eigene: set[int] = set().union(
                *(je_turn.get(t, set()) for t in objekt.get("turn_ids") or [])
            )
            kandidat: int | None = match_entity(
                str(objekt["name"]), {i: n for i, n in namen.items() if i in eigene},
            )
            if kandidat is not None and bind_entity(
                POSTGRES_URL, int(objekt["id"]), kandidat, BINDING_TURN_MAGNET,
            ):
                gebunden += 1
                logger.info(
                    f"Sachlage-Bindung: '{objekt['name']}' → Entitaet {kandidat} "
                    f"'{namen.get(kandidat, '')}'"
                )

    # ── Verarbeitung: Zeitanker ─────────────────
    anker: set[int] = {m.timeline_id for m in magnete if m.turn_id == turn_id and m.timeline_id}
    zeitanker: int = 0
    if len(anker) == 1:
        timeline_id: int = next(iter(anker))
        for objekt in sachlage.get("objekte") or []:
            if not isinstance(objekt, dict) or not objekt.get("akut"):
                continue
            for eigenschaft, wert in (objekt.get("gedeckt") or {}).items():
                zeilen_id = ergebnis.property_ids.get((text_key(objekt["name"]), text_key(eigenschaft)))
                if zeilen_id and _has_time_expression(str(wert)) and bind_timeline(
                    POSTGRES_URL, zeilen_id, timeline_id,
                ):
                    zeitanker += 1
    elif len(anker) > 1:
        logger.info(
            f"Sachlage-Bindung: turn={turn_id} nennt {len(anker)} Zeitanker "
            f"{sorted(anker)} — keiner gesetzt"
        )

    # ── Ausgabe ─────────────────────────────────
    zusammenfassung: dict = {
        "abgelegt": True, "objekte": ergebnis.objects, "neu": ergebnis.new,
        "bestaetigt": ergebnis.confirmed, "abgeloest": ergebnis.replaced,
        "ungebunden_geprueft": len(offen), "gebunden": gebunden, "zeitanker": zeitanker,
    }
    logger.info(f"Sachlage-Gedaechtnis: turn={turn_id} {zusammenfassung}")
    return zusammenfassung
