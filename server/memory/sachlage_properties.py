"""Das Eigenschaftsgedaechtnis der Sachlage — Scheibe 11 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 11. Die Sachlage
eines Turns steht als Ganzes in `sachlage_verlauf` (Scheibe 4). Was dort fehlt,
ist die Sache selbst: Ein Objekt, ueber das an drei Abenden gesprochen wurde,
steht in drei Zeilen, und seine gedeckten Eigenschaften leben in JSON, das
niemand ueber Turns hinweg liest.

**Drei Tabellen, keine Geschaeftslogik:**

- `sachlage_objekt` — eine Zeile je Paar und Objektname, dauerhaft, mit der
  spaeter gesetzten Entitaet (`entitaeten`, F-MAGNET-1).
- `sachlage_objekt_turn` — je gerechnetem Turn die Objekte seiner Sachlage;
  ueber `turn_id` erreicht man `verbindung`, KZG, LZG und den Rohturn.
- `sachlage_eigenschaft` — je Eigenschaft ihr Wert mit Historie.

**Ein neuer Wert ueberschreibt nicht (Entscheidung des Eigentuemers,
13.09.2026).** Der alte wird inaktiv gesetzt — `aktiv = FALSE`, `t_invalid`,
`abgeloest_durch` —, der neue daneben geschrieben. So wie `fakten.invalidate`.
Wer sich korrigiert (erst der 1.7., dann der 1.8.), bleibt belegbar. Derselbe
Wert in einem spaeteren Turn ist eine Bestaetigung, keine neue Zeile.

**Was nicht ueberschreibt:** Eine Eigenschaft, die aus `gedeckt` verschwindet,
ist vergessen, nicht widerrufen — ihre Zeile bleibt aktiv. Nur ein anderer
Wert loest ab.

**Verfall:** keiner (F-VERFALL-1: was als Faktum protokolliert, bleibt).
Die Fremdschluessel auf Objekt und Verlauf stehen auf RESTRICT: Eine Historie
verschwindet nicht mit einem Loeschbefehl an anderer Stelle.
"""

import json
import logging
from dataclasses import dataclass

import psycopg2
import psycopg2.extras

logger = logging.getLogger("ki_server.memory.sachlage_properties")

OBJECT_TABLE:   str = "sachlage_objekt"
TURN_TABLE:     str = "sachlage_objekt_turn"
PROPERTY_TABLE: str = "sachlage_eigenschaft"

# Die Herkunft einer Entitaetsbindung — damit eine Bindung spaeter von einer
# anderen Regel unterscheidbar bleibt.
BINDING_TURN_MAGNET: str = "turn_magnet"

SPEAKERS: frozenset[str] = frozenset({"nutzer", "nova"})


def text_key(text: object) -> str:
    """Der Vergleichsschluessel fuer Namen, Eigenschaften und Werte.

    Kleinschreibung (casefold) und zusammengezogener Leerraum — dieselbe
    Formel wie `kurzziel.normalize_object_name`, erweitert um casefold, damit
    »Straße« und »STRASSE« nicht zwei Werte sind.
    """
    return " ".join(str(text or "").casefold().split())


@dataclass(frozen=True)
class RecordResult:
    """Was ein Schreiblauf getan hat — fuer Log und Aufrufer."""

    objects:   int
    new:       int
    confirmed: int
    replaced:  int
    object_ids: dict[str, int]
    property_ids: dict[tuple[str, str], int]


def _object_upsert(cur: object, user_id: str, character_id: str, objekt: dict) -> int:
    """Legt das Objekt des Paares an oder frischt Name, Klasse und Beruehrung auf.

    Vorbedingung: `cur` gehoert zu einer offenen Transaktion; `objekt["name"]`
        ist nicht leer.
    Nachbedingung: Genau eine Zeile je Paar und `text_key(name)`; ihre id.
    """
    name: str = str(objekt["name"]).strip()
    cur.execute(
        f"""
        INSERT INTO {OBJECT_TABLE} (user_id, character_id, name, name_schluessel, klasse)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id, character_id, name_schluessel)
        DO UPDATE SET name = EXCLUDED.name,
                      klasse = COALESCE(EXCLUDED.klasse, {OBJECT_TABLE}.klasse),
                      last_touched = NOW()
        RETURNING id
        """,  # noqa: S608 — Tabellenname ist eine Konstante
        (user_id, character_id, name, text_key(name), objekt.get("klasse")),
    )
    return int(cur.fetchone()[0])


def _property_write(
    cur: object,
    objekt_id: int,
    eigenschaft: str,
    wert: str,
    sprecher: str | None,
    quelle: dict | None,
    turn_id: str,
) -> tuple[str, int]:
    """Schreibt einen Wert nach der Abloese-Regel; liefert (Ausgang, Zeilen-id).

    Vorbedingung: `cur` gehoert zu einer offenen Transaktion; `wert` hat die
        gepruefte Wertform (nicht leer).
    Nachbedingung: Danach steht genau ein aktiver Wert je Objekt und
        Eigenschaft: bestaetigt (gleicher Wert), neu, oder abgeloest (der alte
        inaktiv mit `t_invalid` und Verweis auf den neuen).
    """
    schluessel: str = text_key(eigenschaft)
    cur.execute(
        f"""
        SELECT id, wert, sprecher, quelle FROM {PROPERTY_TABLE}
        WHERE objekt_id = %s AND eigenschaft_schluessel = %s AND aktiv
        FOR UPDATE
        """,  # noqa: S608
        (objekt_id, schluessel),
    )
    bisher: tuple | None = cur.fetchone()
    if bisher is not None and text_key(bisher[1]) == text_key(wert):
        cur.execute(
            f"""
            UPDATE {PROPERTY_TABLE}
            SET bestaetigt_turn_id = %s, last_touched = NOW(),
                sprecher = COALESCE(sprecher, %s),
                quelle = COALESCE(quelle, %s::jsonb)
            WHERE id = %s
            """,  # noqa: S608
            (turn_id, sprecher, json.dumps(quelle) if quelle else None, bisher[0]),
        )
        return "bestaetigt", int(bisher[0])
    if bisher is not None:
        cur.execute(
            f"UPDATE {PROPERTY_TABLE} SET aktiv = FALSE, t_invalid = NOW() WHERE id = %s",  # noqa: S608
            (bisher[0],),
        )
    cur.execute(
        f"""
        INSERT INTO {PROPERTY_TABLE}
            (objekt_id, eigenschaft, eigenschaft_schluessel, wert, sprecher,
             quelle, turn_id, bestaetigt_turn_id)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)
        RETURNING id
        """,  # noqa: S608
        (objekt_id, eigenschaft, schluessel, wert, sprecher,
         json.dumps(quelle) if quelle else None, turn_id, turn_id),
    )
    neue_id: int = int(cur.fetchone()[0])
    if bisher is None:
        return "neu", neue_id
    cur.execute(
        f"UPDATE {PROPERTY_TABLE} SET abgeloest_durch = %s WHERE id = %s",  # noqa: S608
        (neue_id, bisher[0]),
    )
    return "abgeloest", neue_id


def _record_object(
    cur: object,
    user_id: str,
    character_id: str,
    turn_id: str,
    verlauf_id: int,
    objekt: dict,
    zaehlung: dict[str, int],
    property_ids: dict[tuple[str, str], int],
) -> int:
    """Legt ein Objekt, seinen Turn-Eintrag und seine gedeckten Werte in der offenen Transaktion ab.

    Vorbedingung: `cur` gehoert zu einer offenen Transaktion; `objekt` traegt
        einen nicht leeren Namen und ist gegen die Form gehalten.
    Nachbedingung: Objektzeile und Turn-Zeile existieren; je `text_key` einer
        Eigenschaft hoechstens ein Schreibvorgang; `zaehlung` und
        `property_ids` sind fortgeschrieben. Liefert die Objekt-id.
    """
    objekt_id: int = _object_upsert(cur, user_id, character_id, objekt)
    cur.execute(
        f"""
        INSERT INTO {TURN_TABLE} (verlauf_id, objekt_id, turn_id, akut)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (verlauf_id, objekt_id) DO NOTHING
        """,  # noqa: S608
        (verlauf_id, objekt_id, turn_id, bool(objekt.get("akut"))),
    )
    sprecher_je: dict = objekt.get("sprecher") or {}
    quellen_je: dict = objekt.get("quellen") or {}
    gesehen: set[str] = set()
    for eigenschaft, wert in (objekt.get("gedeckt") or {}).items():
        # Zwei Schreibweisen derselben Eigenschaft im selben Turn waeren sonst
        # eine Abloesung durch sich selbst.
        if text_key(eigenschaft) in gesehen:
            logger.warning(
                "Eigenschaftsgedaechtnis: '%s' an '%s' doppelt im Turn — der erste Wert bleibt",
                eigenschaft, objekt["name"],
            )
            continue
        gesehen.add(text_key(eigenschaft))
        sprecher: object = sprecher_je.get(eigenschaft)
        quelle: object = quellen_je.get(eigenschaft)
        ausgang, zeilen_id = _property_write(
            cur, objekt_id, str(eigenschaft), str(wert),
            sprecher if sprecher in SPEAKERS else None,
            quelle if isinstance(quelle, dict) else None,
            turn_id,
        )
        zaehlung[ausgang] += 1
        property_ids[(text_key(objekt["name"]), text_key(eigenschaft))] = zeilen_id
    return objekt_id


def record_turn_objects(
    postgres_url: str,
    *,
    user_id:      str,
    character_id: str,
    turn_id:      str,
    verlauf_id:   int,
    sachlage:     dict,
) -> RecordResult | None:
    """Legt die Objekte einer gerechneten Sachlage und ihre gedeckten Werte ab.

    Vorbedingung: Paar, `turn_id` und `verlauf_id` (die Zeile in
        `sachlage_verlauf`) sind gesetzt; `sachlage` ist gegen die Form
        gehalten (`sachlage_form`): `gedeckt` ist Text → Text mit Wert.
    Nachbedingung: Jedes Objekt hat eine Zeile in `sachlage_objekt` und eine
        in `sachlage_objekt_turn`; jede gedeckte Eigenschaft ist neu,
        bestaetigt oder hat ihren Vorgaenger abgeloest — in einer Transaktion.
    Fehlerfaelle: Unvollstaendige Kennung — `logger.error`, None, nichts
        geschrieben. DB-Fehler — `logger.exception`, Rollback, None. Der Turn
        laeuft weiter; die Luecke steht im Log.

    Returns:
        Die Zaehlung samt Objekt- und Eigenschafts-ids, oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id or not turn_id or not isinstance(verlauf_id, int):
        logger.error(
            "Eigenschaftsgedaechtnis: unvollstaendige Kennung (turn=%r, verlauf=%r, "
            "paar=%r/%r) — nichts geschrieben", turn_id, verlauf_id, user_id, character_id,
        )
        return None
    objekte: list[dict] = [
        o for o in sachlage.get("objekte") or []
        if isinstance(o, dict) and str(o.get("name") or "").strip()
    ]

    # ── Verarbeitung ────────────────────────────
    zaehlung: dict[str, int] = {"neu": 0, "bestaetigt": 0, "abgeloest": 0}
    object_ids: dict[str, int] = {}
    property_ids: dict[tuple[str, str], int] = {}
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                for objekt in objekte:
                    object_ids[text_key(objekt["name"])] = _record_object(
                        cur, user_id, character_id, turn_id, verlauf_id,
                        objekt, zaehlung, property_ids,
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception(
            "Eigenschaftsgedaechtnis: turn=%s nicht abgelegt — die Reihe hat eine Luecke",
            turn_id,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if len(object_ids) != len({text_key(o["name"]) for o in objekte}):
        logger.error(
            "Eigenschaftsgedaechtnis: %d Objekte gelesen, %d ids — Namen kollidieren",
            len(objekte), len(object_ids),
        )
    ergebnis = RecordResult(
        objects=len(object_ids), new=zaehlung["neu"], confirmed=zaehlung["bestaetigt"],
        replaced=zaehlung["abgeloest"], object_ids=object_ids, property_ids=property_ids,
    )
    logger.info(
        "Eigenschaftsgedaechtnis: turn=%s — %d Objekte, Eigenschaften neu %d, "
        "bestaetigt %d, abgeloest %d",
        turn_id, ergebnis.objects, ergebnis.new, ergebnis.confirmed, ergebnis.replaced,
    )
    return ergebnis


def active_properties(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    name_keys:    list[str],
    limit:        int,
) -> list[dict]:
    """Die aktiven Eigenschaften der genannten Objekte des Paares, juengste zuerst.

    Vorbedingung: `name_keys` aus `text_key`; `limit` > 0.
    Nachbedingung: Hoechstens `limit` dicts mit objekt_id, name, eigenschaft,
        wert, sprecher, turn_id, id; leer ohne Namen.
    Fehlerfaelle: DB-Fehler — `logger.exception`, leere Liste.
    """
    if not name_keys or limit <= 0 or not user_id or not character_id:
        return []
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT e.id, e.objekt_id, o.name, e.eigenschaft, e.wert,
                           e.sprecher, e.turn_id
                    FROM {PROPERTY_TABLE} e
                    JOIN {OBJECT_TABLE} o ON o.id = e.objekt_id
                    WHERE o.user_id = %s AND o.character_id = %s
                      AND o.name_schluessel = ANY(%s) AND e.aktiv
                    ORDER BY e.last_touched DESC
                    LIMIT %s
                    """,  # noqa: S608
                    (user_id, character_id, list(name_keys), limit),
                )
                return [dict(z) for z in cur.fetchall()]
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: aktive Eigenschaften nicht lesbar")
        return []


def property_history(postgres_url: str, objekt_id: int, eigenschaft: str) -> list[dict]:
    """Alle Werte einer Eigenschaft, aktiv und abgeloest, in zeitlicher Folge.

    Vorbedingung: `objekt_id` ist die id einer Zeile in `sachlage_objekt`.
    Nachbedingung: dicts in der Reihenfolge ihrer Gueltigkeit; leer ohne Werte.
    Fehlerfaelle: DB-Fehler — `logger.exception`, leere Liste.
    """
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT id, wert, aktiv, t_valid, t_invalid, abgeloest_durch,
                           turn_id, bestaetigt_turn_id, sprecher, timeline_id
                    FROM {PROPERTY_TABLE}
                    WHERE objekt_id = %s AND eigenschaft_schluessel = %s
                    ORDER BY t_valid, id
                    """,  # noqa: S608
                    (objekt_id, text_key(eigenschaft)),
                )
                return [dict(z) for z in cur.fetchall()]
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: Historie nicht lesbar")
        return []


def unbound_objects(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    name_keys:    list[str],
    turn_limit:   int,
) -> list[dict]:
    """Die genannten Objekte ohne Entitaet, je mit den turn_ids ihrer juengsten Turns.

    Nachbedingung: dicts mit id, name, turn_ids (hoechstens `turn_limit`,
        juengste zuerst); leer ohne Namen.
    Fehlerfaelle: DB-Fehler — `logger.exception`, leere Liste.
    """
    if not name_keys or not user_id or not character_id:
        return []
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT o.id, o.name,
                           (ARRAY(SELECT t.turn_id FROM {TURN_TABLE} t
                                  WHERE t.objekt_id = o.id
                                  ORDER BY t.erstellt_am DESC LIMIT %s)) AS turn_ids
                    FROM {OBJECT_TABLE} o
                    WHERE o.user_id = %s AND o.character_id = %s
                      AND o.name_schluessel = ANY(%s) AND o.entitaet_id IS NULL
                    """,  # noqa: S608
                    (turn_limit, user_id, character_id, list(name_keys)),
                )
                return [dict(z) for z in cur.fetchall()]
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: ungebundene Objekte nicht lesbar")
        return []


def bind_entity(postgres_url: str, objekt_id: int, entitaet_id: int, binding: str) -> bool:
    """Setzt die Entitaet eines Objekts — nur, wenn es noch keine hat.

    Nachbedingung: True, wenn genau eine Zeile gebunden wurde.
    Fehlerfaelle: DB-Fehler — `logger.exception`, False.
    """
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {OBJECT_TABLE}
                    SET entitaet_id = %s, entitaet_bindung = %s, last_touched = NOW()
                    WHERE id = %s AND entitaet_id IS NULL
                    """,  # noqa: S608
                    (entitaet_id, binding, objekt_id),
                )
                gebunden: bool = cur.rowcount == 1
            conn.commit()
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: Bindung objekt=%s nicht gesetzt", objekt_id)
        return False
    return gebunden


def bind_timeline(postgres_url: str, property_id: int, timeline_id: int) -> bool:
    """Setzt den Zeitanker einer Eigenschaft — nur, wenn sie noch keinen hat.

    Vorbedingung: `property_id` und `timeline_id` bezeichnen bestehende Zeilen.
    Nachbedingung: True, wenn genau eine Zeile den Anker bekam.
    Fehlerfaelle: DB-Fehler — `logger.exception`, False.
    """
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE {PROPERTY_TABLE} SET timeline_id = %s
                    WHERE id = %s AND timeline_id IS NULL
                    """,  # noqa: S608
                    (timeline_id, property_id),
                )
                gebunden: bool = cur.rowcount == 1
            conn.commit()
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: Zeitanker id=%s nicht gesetzt", property_id)
        return False
    return gebunden


def turn_links(postgres_url: str, turn_ids: list[str]) -> list[dict]:
    """Die Gedaechtnis-Verbindungen der genannten Turns samt LZG-Magneten.

    Liest `verbindung` (Turn → KZG-Key → LZG-Knoten) und, wo der Knoten schon
    existiert, dessen `entitaet_ids` und `timeline_id` — die bleiben, wenn der
    KZG-Eintrag in Redis laengst verfallen ist.

    Nachbedingung: dicts mit turn_id, kzg_id, lzg_id, lzg_entitaet_ids,
        lzg_timeline_id; leer ohne turn_ids.
    Fehlerfaelle: DB-Fehler — `logger.exception`, leere Liste.
    """
    if not turn_ids:
        return []
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT v.turn_id, v.kzg_id, v.lzg_id,
                           k.entitaet_ids AS lzg_entitaet_ids,
                           k.timeline_id  AS lzg_timeline_id
                    FROM verbindung v
                    LEFT JOIN lzg_knoten k ON k.id = v.lzg_id
                    WHERE v.turn_id = ANY(%s)
                    ORDER BY v.id
                    """,
                    (list(turn_ids),),
                )
                return [dict(z) for z in cur.fetchall()]
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: Verbindungen der Turns nicht lesbar")
        return []


def entity_names(postgres_url: str, entitaet_ids: list[int]) -> dict[int, str]:
    """Die Namen aktiver Entitaeten — ohne `last_touched` zu schreiben.

    `EntitaetenRepository.find_by_id` beruehrt jede gelesene Entitaet; eine
    Bindungspruefung ist kein Gebrauch und soll den Verfall nicht verschieben.

    Vorbedingung: `entitaet_ids` sind ganze Zahlen.
    Nachbedingung: id → Name nur fuer aktive Entitaeten; leer ohne ids.
    Fehlerfaelle: DB-Fehler — `logger.exception`, leeres dict.
    """
    if not entitaet_ids:
        return {}
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name FROM entitaeten WHERE id = ANY(%s) AND aktiv",
                    (list(entitaet_ids),),
                )
                return {int(r[0]): str(r[1]) for r in cur.fetchall()}
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("Eigenschaftsgedaechtnis: Entitaetsnamen nicht lesbar")
        return {}
