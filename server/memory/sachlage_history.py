"""Sachlage-Verlauf — das Gedaechtnis der Sachlage, je gerechnetem Turn eine Zeile.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 4. Die Sachlage
selbst lebt fortgeschrieben in Redis (`graph/nodes/sachlage.py`) und wird
dort ueberschrieben. Diese Tabelle haelt fest, **was die Sachlage eines
Turns war** — ein Faktum, das nicht verfaellt (`F-VERFALL-1`), damit eine
Zustellung spaeter an ihren Anlass anknuepfen kann und ein Thema zu den
Turns fuehrt, in denen es Gegenstand war.

**Drei Zugriffe, keine Geschaeftslogik:** schreiben, per `turn_id` lesen,
per Embedding die aehnlichste Zeile eines Paares finden. Wer entscheidet,
ob eine Zeile geschrieben wird oder was ein Treffer bedeutet, ist der
Knoten.

**Der Embed-Text ist der `gegenstand`-Satz** (`F-EMBED-1`): aus der Zeile
rekonstruierbar, eine benannte Funktion, die jeder Erzeuger ruft. Der
Vektor selbst wird hier nicht gerechnet — der Aufrufer bringt ihn mit,
oder er bringt `None`, und die Zeile steht ohne ihn.
"""

import json
import logging
from datetime import datetime

import psycopg2
import psycopg2.extras

from memory.utils import embedding_zu_pgvector_str

logger = logging.getLogger("ki_server.memory.sachlage_history")

TABELLE: str = "sachlage_verlauf"

# Die Spalten, die ein Leser zurueckbekommt — als Konstante, damit die beiden
# Leseabfragen nicht auseinanderdriften.
_LESE_SPALTEN: str = (
    "turn_id, user_id, character_id, thema, gegenstand, nutzerziel, "
    "ausdrucksweise, objekte, herkunft, erstellt_am"
)


def build_embed_text(gegenstand: str) -> str:
    """Der Embed-Text einer Verlaufszeile — die EINZIGE Formel fuer diese Spalte.

    Vorbedingung: `gegenstand` ist nicht leer.
    Nachbedingung: Der unveraenderte Gegenstand-Satz (Identitaet) — aus der
        persistierten Spalte vollstaendig rekonstruierbar (`F-EMBED-1`).
    Fehlerfaelle: Leerer Gegenstand ist ein `ValueError`, kein leerer Vektor.
    """
    if not gegenstand or not gegenstand.strip():
        raise ValueError(
            "build_embed_text(sachlage_history): gegenstand ist leer — kein Embed-Text baubar"
        )
    return gegenstand


def _row_to_dict(zeile: dict) -> dict:
    """Macht die Zeile zustandstauglich: Zeitstempel als ISO-Text."""
    ergebnis: dict = dict(zeile)
    erstellt = ergebnis.get("erstellt_am")
    if isinstance(erstellt, datetime):
        ergebnis["erstellt_am"] = erstellt.isoformat()
    return ergebnis


def history_write(
    postgres_url: str,
    *,
    turn_id:      str,
    user_id:      str,
    character_id: str,
    sachlage:     dict,
    embedding:    list[float] | None,
) -> int | None:
    """Schreibt die Sachlage eines gerechneten Turns als Faktum.

    Vorbedingung: `turn_id`, Paar und die Pflichtfelder des Artefakts
        (`thema`, `gegenstand`, `nutzerziel`, `ausdrucksweise`, `objekte`,
        `herkunft`) sind gesetzt — die Tabelle erzwingt sie mit NOT NULL.
    Nachbedingung: Genau eine neue Zeile; ihre id.
    Fehlerfaelle: Fehlende Kennung — `logger.error`, kein Schreibversuch,
        None. DB-Fehler — `logger.exception`, None. Der Turn laeuft in
        beiden Faellen weiter; die Reihe hat dann eine Luecke, und die
        Zeile sagt es.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turn_id or not user_id or not character_id:
        logger.error(
            "sachlage_verlauf: unvollstaendige Kennung (turn='%s', paar=%r/%r) "
            "— nichts geschrieben", turn_id, user_id, character_id,
        )
        return None
    fehlend: list[str] = [
        f for f in ("thema", "gegenstand", "nutzerziel", "ausdrucksweise", "objekte", "herkunft")
        if f not in sachlage
    ]
    if fehlend:
        logger.error(
            "sachlage_verlauf: Artefakt ohne %s — nichts geschrieben (turn=%s)",
            fehlend, turn_id,
        )
        return None

    # ── Verarbeitung ────────────────────────────
    vektor: str | None = embedding_zu_pgvector_str(embedding) if embedding else None
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {TABELLE}
                        (turn_id, user_id, character_id, thema, gegenstand,
                         nutzerziel, ausdrucksweise, objekte, herkunft, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                    RETURNING id
                    """,  # noqa: S608 — TABELLE ist eine Konstante
                    (turn_id, user_id, character_id,
                     str(sachlage["thema"]), str(sachlage["gegenstand"]),
                     str(sachlage["nutzerziel"]), str(sachlage["ausdrucksweise"]),
                     json.dumps(sachlage["objekte"], ensure_ascii=False),
                     str(sachlage["herkunft"]), vektor),
                )
                zeilen_id: int = cur.fetchone()[0]
            conn.commit()
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception(
            "sachlage_verlauf: Zeile fuer turn=%s nicht geschrieben — die Reihe "
            "hat eine Luecke", turn_id,
        )
        return None

    # ── Ausgabe ─────────────────────────────────
    logger.info(
        "Sachlage-Verlauf: turn=%s '%s' abgelegt (id=%d, vektor=%s)",
        turn_id, str(sachlage["thema"])[:40], zeilen_id, "ja" if vektor else "nein",
    )
    return zeilen_id


def history_read_turn(postgres_url: str, turn_id: str) -> dict | None:
    """Die Verlaufszeile eines Turns — das harte Ende der Bruecke.

    Vorbedingung: `turn_id` ist nicht leer.
    Nachbedingung: Die Zeile als Dict (Zeitstempel als ISO-Text), oder None,
        wenn es keine gibt — was regulaer vorkommt: Der Ausloeser kann vor
        dem Bau der Tabelle liegen.
    Fehlerfaelle: DB-Fehler — `logger.exception`, None.
    """
    if not turn_id:
        return None
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    f"SELECT {_LESE_SPALTEN} FROM {TABELLE} WHERE turn_id = %s "
                    f"ORDER BY id DESC LIMIT 1",  # noqa: S608 — Konstanten
                    (turn_id,),
                )
                zeile = cur.fetchone()
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception("sachlage_verlauf: Lesen fuer turn=%s fehlgeschlagen", turn_id)
        return None
    return _row_to_dict(zeile) if zeile else None


def history_nearest(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    embedding:    list[float],
    min_kosinus:  float,
    ausser_thema: str | None = None,
) -> dict | None:
    """Die Verlaufszeile des Paares, die dem Vektor am naechsten liegt.

    Vorbedingung: Paar gesetzt, `embedding` nicht leer, `min_kosinus` in [0, 1].
    Nachbedingung: Die naechste Zeile samt `kosinus`, wenn sie ueber der
        Schwelle liegt — sonst None. **Unter der Schwelle ist kein Treffer**:
        Eine Bruecke zu einem Turn ohne Bezug waere schlimmer als keine.
        Mit `ausser_thema` bleiben Zeilen dieses Themas aussen vor — die
        Wiederaufnahme (Scheibe 5) sucht eine *fruehere* Blase, und die
        naechste Zeile ist sonst fast immer der eigene Vorturn.
    Fehlerfaelle: DB-Fehler — `logger.exception`, None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id or not embedding:
        logger.error(
            "sachlage_verlauf: Suche ohne Paar oder Vektor (paar=%r/%r, dim=%d)",
            user_id, character_id, len(embedding or []),
        )
        return None

    # ── Verarbeitung ────────────────────────────
    vektor: str = embedding_zu_pgvector_str(embedding)
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    f"""
                    SELECT {_LESE_SPALTEN},
                           1 - (embedding <=> %s::vector) AS kosinus
                    FROM   {TABELLE}
                    WHERE  user_id = %s AND character_id = %s
                           AND embedding IS NOT NULL
                           AND (%s::text IS NULL OR thema <> %s)
                    ORDER BY embedding <=> %s::vector
                    LIMIT 1
                    """,  # noqa: S608 — Konstanten
                    (vektor, user_id, character_id, ausser_thema, ausser_thema, vektor),
                )
                zeile = cur.fetchone()
        finally:
            conn.close()
    except psycopg2.Error:
        logger.exception(
            "sachlage_verlauf: Vektorsuche fuer %s/%s fehlgeschlagen", user_id, character_id,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if zeile is None:
        return None
    kosinus: float = float(zeile["kosinus"])
    if kosinus < min_kosinus:
        logger.info(
            "Sachlage-Verlauf: naechste Zeile (turn=%s) liegt bei %.2f unter der "
            "Schwelle %.2f — kein Treffer", zeile["turn_id"], kosinus, min_kosinus,
        )
        return None
    ergebnis: dict = _row_to_dict(zeile)
    ergebnis["kosinus"] = kosinus
    return ergebnis
