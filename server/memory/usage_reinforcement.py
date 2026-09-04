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
from dataclasses import dataclass, field

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

# Die sechs Ausgaenge von `used_memories_find`. Sie sind der Grund, warum diese
# Funktion einen Befund und keine Liste liefert: Fuenf davon geben eine leere
# Trefferliste zurueck, und in einer Protokollzeile sahen sie bis zum
# 04.09.2026 alle gleich aus wie der sechste — `verwendet: 0`. Ein Nullbefund
# war damit nicht von einem Ausfall zu unterscheiden: Ein Uebersprung ohne
# eigene Marke sieht aus wie ein Ergebnis.
AUSGANG_GERECHNET:      str = "gerechnet"        # die Naehe wurde gerechnet
AUSGANG_ANTWORT_LEER:   str = "antwort_leer"     # kein Text, nichts hergenommen
AUSGANG_OHNE_KANDIDAT:  str = "ohne_kandidat"    # keine Erinnerung gelesen
AUSGANG_EMBED_FEHLER:   str = "embed_fehler"     # Einbetten warf
AUSGANG_VEKTOR_LEER:    str = "vektor_leer"      # Einbetten lieferte nichts
AUSGANG_DB_FEHLER:      str = "db_fehler"        # Naehe nicht lesbar


@dataclass
class Verwendungsbefund:
    """Was die Naehepruefung ergeben hat — samt der Groessen, die sie erzeugten.

    Traegt die Felder, die eine Zeile nachrechenbar machen: das Ergebnis (`treffer`), die **Eingangsgroessen
    einzeln** (`naehen_alle`), den **geltenden Massstab** (`schwelle`,
    `deckel`) und die **Herkunftsmarke** (`ausgang`).

    `naehen_alle` ist der Teil, der den Nullbefund erklaerbar macht: Ohne ihn
    ist `treffer == []` nicht davon zu unterscheiden, ob die Kandidaten knapp
    unter der Schwelle lagen oder gar nichts miteinander zu tun hatten.
    """

    treffer:     list[tuple[int, float]] = field(default_factory=list)
    naehen_alle: dict[int, float]        = field(default_factory=dict)
    ausgang:     str                     = AUSGANG_GERECHNET
    schwelle:    float                   = VERWENDUNG_NAEHE_SCHWELLE
    deckel:      int                     = VERWENDUNG_MAX_JE_TURN

    def knappster_verworfener(self) -> float | None:
        """Die hoechste Naehe unterhalb der Schwelle, oder None.

        Die eine Zahl, die beim Kalibrieren zaehlt: Sie sagt, wie weit die
        Schwelle vom Bestand entfernt steht.
        """
        genommen: set[int] = {k for k, _ in self.treffer}
        verworfen: list[float] = [
            n for k, n in self.naehen_alle.items() if k not in genommen
        ]
        return max(verworfen) if verworfen else None


def used_memories_find(
    postgres_url: str, antwort: str, knoten_ids: list[int]
) -> Verwendungsbefund:
    """Welche der gelesenen Erinnerungen die Antwort tatsaechlich hergenommen hat.

    Ein Embed-Aufruf und eine Abfrage: Die Antwort wird eingebettet, die Naehe
    zu genau den **gelesenen** Knoten gerechnet, und was ueber der Schwelle
    liegt, gilt als verwendet.

    **Nur gegen die gelesenen Knoten**, nicht gegen den Bestand. Ein Knoten,
    den der Lesepfad nie angeboten hat, kann die Antwort nicht hergenommen
    haben — er waere Nachbarschaft, und genau die soll nicht verstaerken.

    Vorbedingung: `antwort` ist nicht leer, `knoten_ids` sind LZG-Kennungen des
        Paares. Beides wird geprueft.
    Nachbedingung: Ein `Verwendungsbefund`. `treffer` traegt die Knoten ueber
        der Schwelle, absteigend nach Naehe, hoechstens `VERWENDUNG_MAX_JE_TURN`
        Eintraege. `naehen_alle` traegt **jede** gerechnete Naehe, auch die
        verworfenen, und `ausgang` sagt, welcher der sechs Wege hierher fuehrte.
        Ein leerer `treffer` ist damit erklaerbar statt bloss leer.

    Args:
        antwort: Der fertige Antworttext.
        knoten_ids: Die Kennungen der gelesenen Erinnerungen.

    Returns:
        Der Befund samt Eingangsgroessen und Ausgang.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not antwort or not antwort.strip():
        logger.error(
            "Verwendung: leere Antwort — nichts verstaerkt; eine leere Antwort "
            "hat nichts hergenommen und ist kein Fehlerfall der Naehe"
        )
        return Verwendungsbefund(ausgang=AUSGANG_ANTWORT_LEER)
    ids: list[int] = [int(k) for k in (knoten_ids or []) if isinstance(k, int)]
    if not ids:
        return Verwendungsbefund(ausgang=AUSGANG_OHNE_KANDIDAT)

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
        return Verwendungsbefund(ausgang=AUSGANG_EMBED_FEHLER)
    if not vektor:
        logger.error(
            f"Verwendung: Einbetten lieferte einen leeren Vektor — "
            f"{len(ids)} Erinnerungen nicht geprueft"
        )
        return Verwendungsbefund(ausgang=AUSGANG_VEKTOR_LEER)

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
        return Verwendungsbefund(ausgang=AUSGANG_DB_FEHLER)
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    befund = Verwendungsbefund()
    for kennung, naehe in zeilen:
        wert: float = float(naehe)
        if not (-1.0 <= wert <= 1.0):
            logger.error(
                f"Verwendung: Naehe {wert:.4f} zu Knoten {kennung} liegt "
                f"ausserhalb [-1, 1] — verworfen, nicht geklemmt"
            )
            continue
        # Jede gerechnete Naehe wird festgehalten, auch die verworfene: Sie ist
        # die Eingangsgroesse, aus der das Ergebnis entstand (§3).
        befund.naehen_alle[int(kennung)] = round(wert, 4)
        if wert >= VERWENDUNG_NAEHE_SCHWELLE:
            befund.treffer.append((int(kennung), wert))

    if len(befund.treffer) > VERWENDUNG_MAX_JE_TURN:
        logger.warning(
            f"Verwendung: {len(befund.treffer)} Erinnerungen ueber der "
            f"Schwelle, Deckel {VERWENDUNG_MAX_JE_TURN} — die schwaechsten "
            f"fallen weg"
        )
        befund.treffer = befund.treffer[:VERWENDUNG_MAX_JE_TURN]

    knapp: float | None = befund.knappster_verworfener()
    logger.info(
        f"Verwendung: {len(befund.treffer)} von {len(ids)} gelesenen "
        f"Erinnerungen hergenommen (Schwelle {VERWENDUNG_NAEHE_SCHWELLE}, "
        f"knappster verworfener {knapp if knapp is not None else '—'})"
    )
    return befund


def reinforce_used(
    postgres_url: str, antwort: str, knoten_ids: list[int]
) -> dict:
    """Verstaerkt die Erinnerungen, die die Antwort hergenommen hat.

    **Der eine Weg, auf dem im Turn ueberhaupt verstaerkt wird.** Alles andere
    ist Lesen (§7.1) oder Nachbarschaft (§7.1a) und darf nichts bewegen.

    Vorbedingung: keine — ein Turn ohne gelesene Erinnerungen ist der
        Normalfall und kein Fehler.
    Nachbedingung: {geprueft, verwendet, verstaerkt, naehen, naehen_alle,
        knappster_verworfener, schwelle, deckel, ausgang, error}. Die
        Buchfuehrung geht auf: `verwendet` ist die Zahl ueber der Schwelle,
        `verstaerkt` die Zahl der gelungenen Schreibvorgaenge. Weichen sie ab,
        steht der Grund im Log und in `error`.

        **Die letzten fuenf Felder tragen die Entscheidung, nicht ihr
        Ergebnis**: Ohne sie ist `verwendet: 0`
        stumm — es sagt nicht, ob die Kandidaten knapp unter der Schwelle
        lagen, ob es keine gab oder ob das Einbetten ausfiel.
    """
    befund: Verwendungsbefund = used_memories_find(
        postgres_url, antwort, knoten_ids
    )
    ergebnis: dict = {
        "geprueft":   len(knoten_ids or []),
        "verwendet":  len(befund.treffer),
        "verstaerkt": 0,
        "naehen":     [round(n, 4) for _, n in befund.treffer],
        # Die Eingangsgroessen einzeln, der Massstab und die Herkunftsmarke.
        "naehen_alle":           befund.naehen_alle,
        "knappster_verworfener": befund.knappster_verworfener(),
        "schwelle":              befund.schwelle,
        "deckel":                befund.deckel,
        "ausgang":               befund.ausgang,
        "error":                 None,
    }

    for kennung, naehe in befund.treffer:
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
