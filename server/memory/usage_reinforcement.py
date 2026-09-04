"""Verstaerkung setzt Verwendung voraus — `novaberg-memory-synapsen_k.md` §7.1a.

Die Gedaechtnissysteme lesen und bieten an; **das verstaerkt nichts** (§7.1).
Nova entscheidet bei der Formulierung, was sie davon hernimmt — und nur das
wird verstaerkt.

**Woran „hergenommen" erkannt wird: an der Embedding-Naehe zwischen Antwort und
Erinnerung.** Die naheliegende Alternative — den Verfasser fragen — ist
verworfen: Er baut die fachliche Antwort und *koennte* es wissen, aber er
koennte auch fantasieren, und eine Verstaerkung auf einer Selbstauskunft saehe
aus wie eine Messung.

**Die Antwort geht als Ganzes hinein, und das ist gemessen und nicht bequem.**
Der Entwurf sah eine Segmentierung vor — dieselbe Abhilfe, mit der
`FADEN-EMBEDDING-VERDUENNT` behoben wurde. `[gemessen]` 04.09.2026 ueber 25
echte Antworten: **25 von 25 ergeben genau ein Segment.** Die Segmentierung
greift bei Antworten dieser Bauart nie und kostet dabei **1,53 s Median** als
Modellaufruf — im Dispatcher, der synchron im Turn laeuft, waere das reine
Latenz. Das Einbetten der Antwort kostet **0,151 s**.

Der Ort ist der Dispatcher: Der Responder formuliert, er persistiert nicht.
"""

import logging

import psycopg2

from config import (
    VERWENDUNG_MAX_JE_TURN,
    VERWENDUNG_NAEHE_SCHWELLE,
)
from memory import lzg_knoten
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.memory.usage_reinforcement")

# Wie viel Text der Antwort eingebettet wird. Dieselbe Grenze wie beim
# Praegungsfaden — ein laengerer Ausschnitt verduennt den Vektor, ohne mehr
# Aussage zu tragen.
EMBED_ZEICHEN_MAX: int = 1200


def used_memories_find(
    postgres_url: str, antwort: str, knoten_ids: list[int]
) -> list[tuple[int, float]]:
    """Welche der gelesenen Erinnerungen die Antwort tatsaechlich hergenommen hat.

    Ein Embed-Aufruf und eine Abfrage: Die Antwort wird eingebettet, die Naehe
    zu genau den **gelesenen** Knoten gerechnet, und was ueber der Schwelle
    liegt, gilt als verwendet.

    **Nur gegen die gelesenen Knoten**, nicht gegen den Bestand. Ein Knoten,
    den der Lesepfad nie angeboten hat, kann die Antwort nicht hergenommen
    haben — er waere Nachbarschaft, und genau die soll nicht verstaerken.

    Vorbedingung: `antwort` ist nicht leer, `knoten_ids` sind LZG-Kennungen des
        Paares. Beides wird geprueft.
    Nachbedingung: [(knoten_id, naehe), ...] absteigend nach Naehe, hoechstens
        `VERWENDUNG_MAX_JE_TURN` Eintraege, alle ueber der Schwelle. Leere
        Liste, wenn nichts trifft oder eine Vorbedingung verletzt ist — der
        Grund steht dann im Log.

    Args:
        antwort: Der fertige Antworttext.
        knoten_ids: Die Kennungen der gelesenen Erinnerungen.

    Returns:
        Die verwendeten Erinnerungen mit ihrer Naehe.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not antwort or not antwort.strip():
        logger.error(
            "Verwendung: leere Antwort — nichts verstaerkt; eine leere Antwort "
            "hat nichts hergenommen und ist kein Fehlerfall der Naehe"
        )
        return []
    ids: list[int] = [int(k) for k in (knoten_ids or []) if isinstance(k, int)]
    if not ids:
        return []

    # ── Verarbeitung ────────────────────────────
    try:
        vektor: list[float] = model_service.embed.submit_sync(
            EmbedRequest(text=antwort[:EMBED_ZEICHEN_MAX])
        ).embedding
    except Exception as fehler:  # noqa: BLE001 — der Turn laeuft ohne Verstaerkung weiter
        logger.exception(
            f"Verwendung: Einbetten der Antwort fehlgeschlagen — "
            f"{type(fehler).__name__}; {len(ids)} Erinnerungen nicht geprueft"
        )
        return []
    if not vektor:
        logger.error(
            f"Verwendung: Einbetten lieferte einen leeren Vektor — "
            f"{len(ids)} Erinnerungen nicht geprueft"
        )
        return []

    vec: str = "[" + ",".join(f"{x:.6f}" for x in vektor) + "]"
    conn = psycopg2.connect(postgres_url)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, 1 - (embedding <=> %s::vector) AS naehe "
            "FROM lzg_knoten "
            "WHERE id = ANY(%s) AND aktiv AND embedding IS NOT NULL "
            "ORDER BY embedding <=> %s::vector",
            (vec, ids, vec),
        )
        zeilen = cursor.fetchall()
    except psycopg2.Error as fehler:
        logger.exception(
            f"Verwendung: Naehe zu {len(ids)} Erinnerungen nicht lesbar — "
            f"{type(fehler).__name__}"
        )
        return []
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    treffer: list[tuple[int, float]] = []
    for kennung, naehe in zeilen:
        wert: float = float(naehe)
        if not (-1.0 <= wert <= 1.0):
            logger.error(
                f"Verwendung: Naehe {wert:.4f} zu Knoten {kennung} liegt "
                f"ausserhalb [-1, 1] — verworfen, nicht geklemmt"
            )
            continue
        if wert >= VERWENDUNG_NAEHE_SCHWELLE:
            treffer.append((int(kennung), wert))

    if len(treffer) > VERWENDUNG_MAX_JE_TURN:
        logger.warning(
            f"Verwendung: {len(treffer)} Erinnerungen ueber der Schwelle, "
            f"Deckel {VERWENDUNG_MAX_JE_TURN} — die schwaechsten fallen weg"
        )
        treffer = treffer[:VERWENDUNG_MAX_JE_TURN]
    logger.info(
        f"Verwendung: {len(treffer)} von {len(ids)} gelesenen Erinnerungen "
        f"hergenommen (Schwelle {VERWENDUNG_NAEHE_SCHWELLE})"
    )
    return treffer


def reinforce_used(
    postgres_url: str, antwort: str, knoten_ids: list[int]
) -> dict:
    """Verstaerkt die Erinnerungen, die die Antwort hergenommen hat.

    **Der eine Weg, auf dem im Turn ueberhaupt verstaerkt wird.** Alles andere
    ist Lesen (§7.1) oder Nachbarschaft (§7.1a) und darf nichts bewegen.

    Vorbedingung: keine — ein Turn ohne gelesene Erinnerungen ist der
        Normalfall und kein Fehler.
    Nachbedingung: {geprueft, verwendet, verstaerkt, naehen, error}. Die
        Buchfuehrung geht auf: `verwendet` ist die Zahl ueber der Schwelle,
        `verstaerkt` die Zahl der gelungenen Schreibvorgaenge. Weichen sie ab,
        steht der Grund im Log und in `error`.
    """
    ergebnis: dict = {
        "geprueft": len(knoten_ids or []), "verwendet": 0,
        "verstaerkt": 0, "naehen": [], "error": None,
    }
    treffer: list[tuple[int, float]] = used_memories_find(
        postgres_url, antwort, knoten_ids
    )
    ergebnis["verwendet"] = len(treffer)
    ergebnis["naehen"] = [round(n, 4) for _, n in treffer]

    for kennung, naehe in treffer:
        if lzg_knoten.knoten_verstaerken(postgres_url, kennung) is not None:
            ergebnis["verstaerkt"] += 1
            logger.info(
                f"Verwendung: Knoten {kennung} verstaerkt (Naehe {naehe:.4f})"
            )

    # ── Ausgabe-Verifikation ────────────────────
    if ergebnis["verstaerkt"] != ergebnis["verwendet"]:
        ergebnis["error"] = (
            f"{ergebnis['verwendet']} Erinnerungen hergenommen, aber nur "
            f"{ergebnis['verstaerkt']} verstaerkt"
        )
        logger.error(f"Verwendung: {ergebnis['error']}")
    return ergebnis
