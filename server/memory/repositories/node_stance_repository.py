"""Datenzugriff auf `lzg_knoten_haltung` — die Ladung eines Gedaechtnisknotens.

Die Meinungsschicht als additive Annotation auf dem assoziativen Gedaechtnis
(`novaberg-thinking-opinion_k.md` §5). Keine Business-Logik: Wie sich mehrere
Ladungen eines Knotens zu einer Netto-Haltung verrechnen, entscheidet der
Aufrufer — hier wird nur geschrieben, verstaerkt und gelesen.

**Der Name traegt die Trennung.** `haltung` ist die Ladung gegenueber der
SACHE; `valenz` heisst im Bestand die binaere Gespraechsachse des GV, die den
TURN faerbt und einen Turn lebt. Zwei Gegenstaende, zwei Woerter.
"""

import logging

import psycopg2
import psycopg2.extras

logger = logging.getLogger("ki_server.memory.repositories.node_stance")

# Die Spalten, die Leser und Auswertung brauchen — als Konstante, damit
# Abfrage und Verarbeitung nicht getrennt voneinander driften.
READ_COLUMNS: str = (
    "id, knoten_id, eigenschaft, ladung, emotion, praemisse_knoten_id, "
    "quelle, staerke_roh, staerke_decay, haeufigkeit, aktiv, "
    "erstellt_am, verstaerkt_am, decay_am"
)
# Dieselben Spalten mit Tabellenkuerzel — der Leseweg verbindet mit dem Knoten.
SELECT_COLUMNS: str = ", ".join(f"h.{spalte.strip()}" for spalte in READ_COLUMNS.split(","))

# Die Spanne der Ladung. Sie steht auch als CHECK in der Schemadefinition;
# hier faellt eine Verletzung frueher und mit einer lesbaren Meldung.
LADUNG_MIN: float = -1.0
LADUNG_MAX: float = 1.0


def stance_upsert(  # noqa: PLR0913, PLR0917 — eine Zeile der Tabelle, ein Argument je Feld
    postgres_url: str,
    knoten_id:    int,
    ladung:       float,
    *,
    eigenschaft:  str = "",
    emotion:      str = "",
    quelle:       str = "",
    praemisse_knoten_id: int | None = None,
) -> int | None:
    """Legt eine Ladung an oder verstaerkt die vorhandene.

    **Eine zweite Beobachtung ist kein zweiter Eintrag.** Traegt der Knoten zu
    dieser Eigenschaft schon eine Ladung, wandert die neue mit halbem Gewicht
    hinein (gleitender Mittelwert), `haeufigkeit` steigt und die Staerke wird
    auf 1.0 zurueckgesetzt — eine bestaetigte Haltung ist wieder frisch. So
    kippt ein einzelner Ausreisser eine gewachsene Haltung nicht um, und eine
    wiederholte Erfahrung setzt sich trotzdem durch.

    Vorbedingung: `ladung` liegt in [-1.0, 1.0]; `knoten_id` verweist auf einen
        bestehenden Knoten. Beides wird geprueft und laut verworfen.
    Nachbedingung: Die ID der Zeile, oder None bei verletzter Vorbedingung
        oder Datenbankfehler.

    Args:
        knoten_id: Der Gedaechtnisknoten, an dem die Ladung haengt.
        ladung: Vorzeichen und Staerke, -1.0 bis +1.0.
        eigenschaft: Der Gegenstand der Ladung; leer = die Sache als ganze.
        emotion: Die Emotion dahinter, aus dem Plutchik-Kanon; leer erlaubt.
        quelle: Woher die Ladung stammt — ohne sie ist sie nicht nachrechenbar.
        praemisse_knoten_id: Der Werte-Knoten, auf dem das Urteil steht.

    Returns:
        Die ID der angelegten oder verstaerkten Zeile, sonst None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(ladung, (int, float)) or ladung != ladung:  # NaN
        logger.error(f"Haltung: Ladung {ladung!r} an Knoten {knoten_id} ist keine Zahl — verworfen")
        return None
    if not (LADUNG_MIN <= ladung <= LADUNG_MAX):
        logger.error(
            f"Haltung: Ladung {ladung} an Knoten {knoten_id} liegt ausserhalb "
            f"[{LADUNG_MIN}, {LADUNG_MAX}] — verworfen, nicht gekappt"
        )
        return None
    if not quelle:
        logger.error(
            f"Haltung: Ladung {ladung} an Knoten {knoten_id} ohne Quelle — "
            f"verworfen; eine Haltung ohne Herkunft ist nicht nachrechenbar"
        )
        return None

    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lzg_knoten_haltung
                (knoten_id, eigenschaft, ladung, emotion, praemisse_knoten_id, quelle)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (knoten_id, eigenschaft) DO UPDATE SET
                ladung        = (lzg_knoten_haltung.ladung + EXCLUDED.ladung) / 2.0,
                emotion       = COALESCE(NULLIF(EXCLUDED.emotion, ''), lzg_knoten_haltung.emotion),
                quelle        = EXCLUDED.quelle,
                haeufigkeit   = lzg_knoten_haltung.haeufigkeit + 1,
                staerke_decay = 1.0,
                aktiv         = TRUE,
                verstaerkt_am = NOW()
            RETURNING id, haeufigkeit
        """, (knoten_id, eigenschaft, float(ladung), emotion, praemisse_knoten_id, quelle))
        zeile = cursor.fetchone()
        conn.commit()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Haltung: Schreiben an Knoten {knoten_id} ('{eigenschaft}') "
            f"fehlgeschlagen — {type(fehler).__name__}"
        )
        conn.rollback()
        return None
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    if not zeile:
        logger.error(f"Haltung: Schreiben an Knoten {knoten_id} lieferte keine Zeile")
        return None
    haltung_id, haeufigkeit = zeile[0], zeile[1]
    logger.info(
        f"Haltung: Knoten {knoten_id} '{eigenschaft or '(die Sache)'}' → "
        f"{ladung:+.2f} (Quelle {quelle}, {haeufigkeit}. Beobachtung)"
    )
    return int(haltung_id)


def stances_load(postgres_url: str, knoten_ids: list[int]) -> dict[int, list[dict]]:
    """Die aktiven Ladungen zu einer Menge Knoten, nach Knoten gebuendelt.

    Der Leseweg des Spreading-Passes: Er kennt die aktivierten Knoten und
    fragt in EINER Abfrage, welche davon geladen sind. Ein Knoten ohne
    Ladung fehlt im Ergebnis — das ist der Fall *neutral*, und er ist vom
    Fall *nicht gefragt* nur beim Aufrufer zu unterscheiden.

    **Zwei Aktivitaeten, und beide muessen gelten.** Der Gedaechtnisgraph
    loescht nicht, er laesst ruhen (`F-VERFALL-1`): Ein Knoten unter der
    Schwelle steht auf `aktiv = FALSE` und bleibt stehen. Seine Ladung bleibt
    damit ebenfalls stehen — und darf trotzdem nicht mehr sprechen. Deshalb
    verbindet die Abfrage mit dem Knoten und prueft **seine** Aktivitaet mit.
    Ohne den Verbund haette eine Haltung ihren Gegenstand ueberlebt, ohne dass
    irgendwo etwas falsch aussieht.

    Vorbedingung: keine. Eine leere Liste ist ein gueltiger Fall.
    Nachbedingung: {knoten_id: [Ladung, ...]} nur fuer geladene Knoten; bei
        einem Datenbankfehler ein leeres Dict, und der Fehler steht im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    ids: list[int] = [int(k) for k in (knoten_ids or []) if isinstance(k, int)]
    if not ids:
        return {}

    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT " + SELECT_COLUMNS + " FROM lzg_knoten_haltung h "  # noqa: S608 — Konstante, keine Eingabe
            "JOIN lzg_knoten k ON k.id = h.knoten_id "
            "WHERE h.knoten_id = ANY(%s) AND h.aktiv AND k.aktiv "
            "ORDER BY h.knoten_id, abs(h.ladung) DESC",
            (ids,),
        )
        zeilen = cursor.fetchall()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Haltung: Lesen zu {len(ids)} Knoten fehlgeschlagen — {type(fehler).__name__}"
        )
        return {}
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    gebuendelt: dict[int, list[dict]] = {}
    for zeile in zeilen:
        eintrag = dict(zeile)
        gebuendelt.setdefault(int(eintrag["knoten_id"]), []).append(eintrag)
    logger.debug(
        f"Haltung: {len(zeilen)} Ladungen an {len(gebuendelt)} von {len(ids)} Knoten gelesen"
    )
    return gebuendelt


def net_stance(ladungen: list[dict]) -> float:
    """Verrechnet die Ladungen eines Knotens zu einer Netto-Haltung.

    **Nach Staerke gewichtet, nicht gemittelt.** Eine oft bestaetigte Ladung
    wiegt schwerer als eine einmalige; der Widerspruch bleibt im Ergebnis
    sichtbar, statt sich wegzukuerzen — ein Knoten mit +0.8 (10x) und -0.5
    (1x) ist netto positiv, aber nicht so positiv wie einer ohne Gegenstimme.

    **Die Charaktergewichtung fehlt.** Das Konzept fuehrt sie als offenen
    Punkt (§6): Wie sich widersprueckliche Eigenschaften charakterabhaengig
    verrechnen, ist nicht entschieden. Bis dahin zaehlt allein die Erfahrung.

    Rein. Vorbedingung: `ladungen` sind Eintraege aus `stances_load`.
    Nachbedingung: Ein Wert in [-1.0, 1.0]; 0.0 bei leerer Eingabe.
    """
    if not ladungen:
        return 0.0
    gewichte: float = 0.0
    summe:    float = 0.0
    for eintrag in ladungen:
        gewicht: float = float(eintrag.get("staerke_decay", 1.0)) * float(
            eintrag.get("haeufigkeit", 1)
        )
        summe    += float(eintrag.get("ladung", 0.0)) * gewicht
        gewichte += gewicht

    # ── Ausgabe-Verifikation ────────────────────
    if gewichte <= 0.0:
        logger.error(
            f"Haltung: Netto-Verrechnung ueber {len(ladungen)} Ladungen ohne "
            f"Gewicht — verworfen"
        )
        return 0.0
    netto: float = summe / gewichte
    if not (LADUNG_MIN <= netto <= LADUNG_MAX):
        logger.error(
            f"Haltung: Netto {netto:.4f} ausserhalb [{LADUNG_MIN}, {LADUNG_MAX}] "
            f"bei {len(ladungen)} Ladungen — verworfen"
        )
        return 0.0
    return netto
