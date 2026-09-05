"""Datenzugriff auf die abstrakte Schicht — Qualitaetsknoten und ihre Kanten.

Der Traeger einer Faszination ist nicht die Entitaet, sondern ein
Merkmalsprofil (`novaberg-thinking-faszination_k.md` §4.1). Hier liegt der
Speicher dafuer: `abstrakt_knoten` traegt den geschlossenen Satz der sechs
Qualitaetsdimensionen, `traeger_qualitaet` die vorzeichenlose Kante von einem
LZG-Knoten dorthin.

**Vorzeichenlos ist die eine Zeile, in der sich diese Schicht von der
Meinungsschicht unterscheidet.** `lzg_knoten_haltung.ladung` traegt Vorzeichen
und Staerke und sagt, was gelten soll; `traeger_qualitaet.auspraegung` sagt,
wie viel wovon. Ohne die Trennung truege Kriegsgeschichte weniger Faszination
als Gartenkraeuter (§4.4).

Keine Business-Logik: Wie sich sechs Auspraegungen zu einem Merkmalszug
verrechnen, entscheidet `ei/fascination.py` — hier wird nur geschrieben und
gelesen.
"""

import logging

import psycopg2
import psycopg2.extras

from config import (
    QUALITAET_KANON,
    QUALITAET_LAENGE_MIN,
    QUALITAET_WIEDERKEHR_MIN,
)

logger = logging.getLogger("ki_server.memory.repositories.quality_profile")

# Die Spanne der Auspraegung. Sie steht auch als CHECK im Schema; hier faellt
# eine Verletzung frueher und mit einer lesbaren Meldung.
AUSPRAEGUNG_MIN: float = 0.0
AUSPRAEGUNG_MAX: float = 1.0


def qualities_load(postgres_url: str) -> dict[str, int]:
    """Der geschlossene Satz der Qualitaetsdimensionen, Name auf ID.

    Der Satz steht im Schema und wird von dort gelesen, nicht aus der
    Konstante abgeleitet: Die Konstante sagt, was gelten SOLL, die Tabelle,
    was steht. Weichen sie ab, ist das ein Befund und keine Variante — die
    Meldung nennt beide Seiten.

    Vorbedingung: keine.
    Nachbedingung: {name: id} mit genau den Namen aus `QUALITAET_KANON`; bei
        Abweichung oder Datenbankfehler ein leeres Dict, und der Grund steht
        im Log.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, id FROM abstrakt_knoten WHERE art = 'qualitaet'"
        )
        zeilen = cursor.fetchall()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Qualitaet: Lesen des Kanons fehlgeschlagen — {type(fehler).__name__}"
        )
        return {}
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    gefunden: dict[str, int] = {str(name): int(kennung) for name, kennung in zeilen}
    erwartet: set[str] = set(QUALITAET_KANON)
    if set(gefunden) != erwartet:
        logger.error(
            f"Qualitaet: Der Satz im Schema weicht vom Kanon ab — fehlend "
            f"{sorted(erwartet - set(gefunden))}, unerwartet "
            f"{sorted(set(gefunden) - erwartet)}; verworfen"
        )
        return {}
    return gefunden


def quality_upsert(
    postgres_url: str,
    knoten_id: int,
    qualitaet_id: int,
    auspraegung: float,
    quelle: str,
) -> int | None:
    """Schreibt eine Auspraegung oder verstaerkt die vorhandene.

    **Eine zweite Profilierung ist kein zweiter Eintrag.** Traegt der Knoten
    zu dieser Dimension schon eine Auspraegung, wandert die neue mit halbem
    Gewicht hinein und `haeufigkeit` steigt — dieselbe Bauart wie bei der
    Haltung (`node_stance_repository.stance_upsert`), und aus demselben
    Grund: Ein einzelner Ausreisser kippt kein gewachsenes Profil, eine
    wiederholte Bewertung setzt sich trotzdem durch.

    **Kein Verfall an dieser Kante.** Eine Qualitaet beschreibt den
    Gegenstand und ist nicht revidierbar (§4.4) — anders als eine Haltung,
    die mit dem Wegfall ihrer Praemisse zerfaellt. Der Verfall der
    Qualitaeten ist je Dimension verschieden (§10.4) und noch nicht gebaut;
    er gehoert an den Leser, nicht an den Speicher.

    Vorbedingung: `auspraegung` liegt in [0.0, 1.0]; `knoten_id` und
        `qualitaet_id` verweisen auf bestehende Zeilen; `quelle` ist gesetzt.
        Alles wird geprueft und laut verworfen.
    Nachbedingung: Die ID der Zeile, oder None bei verletzter Vorbedingung
        oder Datenbankfehler.

    Args:
        knoten_id: Der Traeger — heute ein LZG-Knoten.
        qualitaet_id: Die Dimension aus `abstrakt_knoten`.
        auspraegung: Wie viel wovon, 0.0 bis 1.0, vorzeichenlos.
        quelle: Woher die Bewertung stammt.

    Returns:
        Die ID der angelegten oder verstaerkten Zeile, sonst None.
    """
    # ── Eingabe-Validierung ─────────────────────
    # `bool` steht vorn, weil `True` in Python ein `int` ist und sonst als
    # 1.0 durchginge — als voller Ausschlag, nicht als Defekt.
    if (isinstance(auspraegung, bool)
            or not isinstance(auspraegung, (int, float))
            or auspraegung != auspraegung):  # NaN
        logger.error(
            f"Qualitaet: Auspraegung {auspraegung!r} an Knoten {knoten_id} "
            f"ist keine Zahl — verworfen"
        )
        return None
    if not (AUSPRAEGUNG_MIN <= auspraegung <= AUSPRAEGUNG_MAX):
        logger.error(
            f"Qualitaet: Auspraegung {auspraegung} an Knoten {knoten_id} liegt "
            f"ausserhalb [{AUSPRAEGUNG_MIN}, {AUSPRAEGUNG_MAX}] — verworfen, "
            f"nicht gekappt; eine negative Auspraegung waere eine Wert-Aussage "
            f"an einer Qualitaets-Kante"
        )
        return None
    if not quelle:
        logger.error(
            f"Qualitaet: Auspraegung {auspraegung} an Knoten {knoten_id} ohne "
            f"Quelle — verworfen; ohne Herkunft ist sie nicht nachrechenbar"
        )
        return None

    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO traeger_qualitaet
                (knoten_id, qualitaet_id, auspraegung, quelle)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (knoten_id, qualitaet_id) DO UPDATE SET
                auspraegung   = (traeger_qualitaet.auspraegung + EXCLUDED.auspraegung) / 2.0,
                quelle        = EXCLUDED.quelle,
                haeufigkeit   = traeger_qualitaet.haeufigkeit + 1,
                verstaerkt_am = NOW()
            RETURNING id, haeufigkeit
        """, (knoten_id, qualitaet_id, float(auspraegung), quelle))
        zeile = cursor.fetchone()
        conn.commit()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Qualitaet: Schreiben an Knoten {knoten_id} (Dimension "
            f"{qualitaet_id}) fehlgeschlagen — {type(fehler).__name__}"
        )
        conn.rollback()
        return None
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    if not zeile:
        logger.error(
            f"Qualitaet: Schreiben an Knoten {knoten_id} lieferte keine Zeile"
        )
        return None
    kanten_id, haeufigkeit = int(zeile[0]), int(zeile[1])
    logger.debug(
        f"Qualitaet: Knoten {knoten_id} Dimension {qualitaet_id} → "
        f"{auspraegung:.2f} (Quelle {quelle}, {haeufigkeit}. Bewertung)"
    )
    return kanten_id


def profiles_load(postgres_url: str, knoten_ids: list[int]) -> dict[int, dict[str, float]]:
    """Die Qualitaetsprofile einer Menge Traeger, nach Traeger gebuendelt.

    **Der Leseweg prueft die Aktivitaet des Knotens mit**, aus demselben
    Grund wie bei der Haltung: Der Graph loescht nicht, er laesst ruhen
    Ein Knoten unter der Schwelle steht auf `aktiv = FALSE`
    und bleibt stehen — sein Profil ebenso, und es darf trotzdem nicht mehr
    sprechen. Ohne den Verbund haette eine Qualitaet ihren Gegenstand
    ueberlebt, ohne dass irgendwo etwas falsch aussieht.

    Ein Traeger ohne Profil fehlt im Ergebnis. Das ist der Fall
    *ungeprueft* — und er ist vom Fall *auf allen sechs Dimensionen null*
    dadurch unterschieden, dass letzterer sechs Zeilen traegt.

    Vorbedingung: keine. Eine leere Liste ist ein gueltiger Fall.
    Nachbedingung: {knoten_id: {dimension: auspraegung}} nur fuer profilierte
        Knoten; bei einem Datenbankfehler ein leeres Dict, und der Fehler
        steht im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    ids: list[int] = [int(k) for k in (knoten_ids or []) if isinstance(k, int)]
    if not ids:
        return {}

    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT t.knoten_id, a.name, t.auspraegung "
            "FROM traeger_qualitaet t "
            "JOIN abstrakt_knoten a ON a.id = t.qualitaet_id "
            "JOIN lzg_knoten      k ON k.id = t.knoten_id "
            "WHERE t.knoten_id = ANY(%s) AND k.aktiv AND a.art = 'qualitaet'",
            (ids,),
        )
        zeilen = cursor.fetchall()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Qualitaet: Lesen zu {len(ids)} Traegern fehlgeschlagen — "
            f"{type(fehler).__name__}"
        )
        return {}
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    gebuendelt: dict[int, dict[str, float]] = {}
    for zeile in zeilen:
        traeger: int = int(zeile["knoten_id"])
        gebuendelt.setdefault(traeger, {})[str(zeile["name"])] = float(
            zeile["auspraegung"]
        )
    unvollstaendig: list[int] = [
        traeger for traeger, profil in gebuendelt.items()
        if len(profil) != len(QUALITAET_KANON)
    ]
    if unvollstaendig:
        logger.error(
            f"Qualitaet: {len(unvollstaendig)} Traeger tragen ein "
            f"unvollstaendiges Profil (erwartet {len(QUALITAET_KANON)} "
            f"Dimensionen): {unvollstaendig[:10]} — ein Profillauf schreibt "
            f"alle sechs auf einmal, eine Luecke ist ein abgebrochener Lauf"
        )
    logger.debug(
        f"Qualitaet: Profile zu {len(gebuendelt)} von {len(ids)} Traegern gelesen"
    )
    return gebuendelt


def candidates_load(postgres_url: str, limit: int) -> list[dict]:
    """Die naechsten Traeger, die ein Profil verdienen und keines haben.

    **Profiliert wird erst, was wiedergekehrt ist** (§6.3) — man fragt sich
    nicht beim ersten Mal, was einen an einer Sache fasziniert. Dazu ein
    Laengenfilter: Die Sachtexte sind mehrere hundert Woerter, die
    Sprechakt-Vermerke ein bis zwei Saetze, und ein Laengenschnitt trifft
    fast dieselbe Menge wie eine Formklassifikation.

    ~~Die haeufigsten zuerst — wer oft wiederkehrt, ist der bessere Kandidat.~~
    **Berichtigt am 05.09.2026: `haeufigkeit` misst Wiederholung, nicht
    Wiederkehr.** Ueber verschiedene Turns gezaehlt fallen die Traeger mit
    Wiederkehr >= 2 von 1.250 auf 106 — 91,5 % der scheinbaren Wiederkehr sind
    Wiederholung desselben Turns (`novaberg-memory-synapsen_k.md` §7.1a). Eine
    Sortierung darauf waehlt die durch die KZG-Schleife aufgeblaehten Knoten.

    **Sortiert wird deshalb nach der Zahl verschiedener Turns**, die einen
    Knoten beruehrt haben — die Bruecke `verbindung` zaehlt sie. Das ist die
    Groesse, die der Docstring immer gemeint hat. `haeufigkeit` bleibt als
    zweiter Schluessel: Ein Knoten ohne Bruecke faellt sonst ans Ende, obwohl
    ueber ihn nichts Schlechtes bekannt ist, sondern nichts.

    `[gemessen 05.09.2026]`: Die profilierten Knoten tragen `haeufigkeit` **56,1**
    gegen **5,5** im Schnitt aller aktiven — die alte Sortierung hat genau die
    aufgeblaehten gewaehlt. Von 36 je Turn gelesenen Knoten trugen **2** ein
    Profil.

    Vorbedingung: `limit` ist positiv. Wird geprueft und laut verworfen.
    Nachbedingung: Bis zu `limit` Eintraege mit `id`, `inhalt`, `haeufigkeit`,
        `themen` und `beruehrt` (Zahl verschiedener Turns); bei einem
        Datenbankfehler eine leere Liste, und der Fehler steht im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(limit, int) or limit <= 0:
        logger.error(
            f"Qualitaet: Kandidatensuche mit Deckel {limit!r} — verworfen, "
            f"erwartet eine positive ganze Zahl"
        )
        return []

    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT k.id, k.inhalt, k.haeufigkeit, k.themen, "
            "       COALESCE(b.turns, 0) AS beruehrt "
            "FROM lzg_knoten k "
            "LEFT JOIN ("
            "      SELECT lzg_id, count(DISTINCT turn_id) AS turns "
            "      FROM verbindung WHERE lzg_id IS NOT NULL GROUP BY lzg_id"
            "  ) b ON b.lzg_id = k.id "
            "WHERE k.aktiv "
            "  AND k.haeufigkeit >= %s "
            "  AND length(k.inhalt) >= %s "
            "  AND NOT EXISTS ("
            "      SELECT 1 FROM traeger_qualitaet t WHERE t.knoten_id = k.id"
            "  ) "
            "ORDER BY COALESCE(b.turns, 0) DESC, k.haeufigkeit DESC, k.id "
            "LIMIT %s",
            (QUALITAET_WIEDERKEHR_MIN, QUALITAET_LAENGE_MIN, limit),
        )
        zeilen = cursor.fetchall()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Qualitaet: Kandidatensuche fehlgeschlagen — {type(fehler).__name__}"
        )
        return []
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    kandidaten: list[dict] = [dict(zeile) for zeile in zeilen]
    zu_kurz: list[int] = [
        int(k["id"]) for k in kandidaten
        if len(str(k.get("inhalt") or "")) < QUALITAET_LAENGE_MIN
    ]
    if zu_kurz:
        logger.error(
            f"Qualitaet: {len(zu_kurz)} Kandidaten unterschreiten die "
            f"Laengenschwelle {QUALITAET_LAENGE_MIN} trotz Filter: {zu_kurz[:10]}"
        )
        return []
    logger.info(
        f"Qualitaet: {len(kandidaten)} Kandidaten (Wiederkehr >= "
        f"{QUALITAET_WIEDERKEHR_MIN}, Laenge >= {QUALITAET_LAENGE_MIN}, "
        f"Deckel {limit})"
    )
    return kandidaten


def profile_count(postgres_url: str) -> tuple[int, int]:
    """Wie viele Traeger ein Profil tragen und wie viele Kanten das sind.

    Die Zahl fuer den Bericht des Tageslaufs und fuer die Messung: Ohne sie
    ist ein Lauf, der nichts fand, von einem, der nicht lief, nicht zu
    unterscheiden.

    Vorbedingung: keine.
    Nachbedingung: (Traeger, Kanten); (0, 0) bei einem Datenbankfehler, und
        der Fehler steht im Log.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count(DISTINCT knoten_id), count(*) FROM traeger_qualitaet"
        )
        zeile = cursor.fetchone()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Qualitaet: Zaehlen fehlgeschlagen — {type(fehler).__name__}"
        )
        return (0, 0)
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    if not zeile:
        logger.error("Qualitaet: Zaehlen lieferte keine Zeile")
        return (0, 0)
    return (int(zeile[0]), int(zeile[1]))
