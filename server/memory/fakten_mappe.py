"""Die Mappe einer Entität — die eine Lesefunktion über das Faktengedächtnis.

Zu einer Entität eines Paares liefert `load_mappe` ihre aktiven, nicht
ruhenden Fakten in beiden Richtungen bis zu einer Tiefe, Referenz- wie
Wert-Fakten, gekappt in Zeichen. Geladen wird über
`FaktenRepository.find_umgebung`; hier stehen die Kappung und die Form.

Drei Zustände, die ein Leser unterscheiden muss:

- **leer:** `entries == ()` und nicht `truncated` — die Entität hat keine
  Fakten in diesem Paar;
- **gekürzt:** `truncated` — die Kappung in Zeichen oder die Grenze der Zeilen
  je Grad hat Fakten weggelassen;
- **Ausfall:** eine Ausnahme, nie eine leere Mappe. Eine unbekannte Entität,
  oder die eines anderen Menschen, ist ein `EntityNotFoundError` aus dem
  Repository; jede andere Ausnahme ist ein Ausfall, auch ein `ValueError`
  oder `LookupError` aus dem Inneren.

Die Mappe rendert keinen Text für einen Prompt; das tun ihre Leser. Kein
Lesen schreibt: `last_touched` bleibt in `fakten` und `entitaeten` stehen.
"""

import logging
import math
from dataclasses import dataclass

from config import (
    FAKTEN_MAPPE_MAX_ZEICHEN,
    FAKTEN_MAPPE_MAX_ZEILEN_JE_GRAD,
    FAKTEN_MAPPE_MIN_STAERKE,
    FAKTEN_MAPPE_TIEFE,
)
from memory.repositories.fakten_repository import FaktenRepository, Surroundings

logger = logging.getLogger("ki_server.memory.fakten_mappe")


@dataclass(frozen=True)
class MappeEntry:
    """Ein Fakt in der Mappe.

    `degree` ist der kleinste Grad, über den der Fakt erreicht wurde. Bei einem
    Wert-Fakt sind `object_id` und `object_name` None und `object_value`
    gesetzt, bei einem Referenz-Fakt umgekehrt. `text` ist der `fakt_text` der
    Zeile, `strength` ihre `staerke_decay`.
    """

    fact_id:      int
    degree:       int
    subject_id:   int
    subject_name: str
    relation:     str
    object_id:    int | None
    object_name:  str | None
    object_value: str | None
    text:         str
    origin:       str
    strength:     float


@dataclass(frozen=True)
class Mappe:
    """Die Mappe einer Entität.

    `entries` steht in der Ordnung der Kappung: Grad 1 vor Grad 2, je Grad
    nach Stärke und dann nach ID absteigend. `truncated` sagt, dass Fakten
    weggelassen wurden; `omitted` zählt die, die die Kappung in Zeichen
    weggelassen hat — was die Grenze der Zeilen abschneidet, liest die Abfrage
    nicht und zählt deshalb nicht mit. `chars` ist die Summe von `len(text)`.
    """

    entity_id:   int
    entity_name: str
    depth:       int
    entries:     tuple[MappeEntry, ...]
    truncated:   bool
    omitted:     int
    chars:       int


def _order_key(entry: MappeEntry) -> tuple[int, float, int]:
    """Der Schlüssel der Ordnung: Grad aufsteigend, Stärke und ID absteigend.

    Vorbedingung: `entry` ist ein `MappeEntry`.
    Nachbedingung: Ein kleinerer Schlüssel steht in der Mappe weiter vorn. Spanne:
        Grad und ID ab 1, die Stärke eine endliche Zahl.
    Fehlerfälle: TypeError bei einem anderen Typ — eine fremde Zeile hätte
        sonst einen Schlüssel, der zufällig passt. RuntimeError, wenn der
        Schlüssel die Spanne verlässt: Ein NaN in der Stärke ist mit nichts
        vergleichbar und machte jede Ordnung still zur richtigen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(entry, MappeEntry):
        raise TypeError(  # noqa: TRY003 — der fremde Typ gehoert in die Meldung
            f"fakten_mappe: kein MappeEntry ({type(entry).__name__})"
        )

    # ── Verarbeitung ────────────────────────────
    key: tuple[int, float, int] = (entry.degree, -entry.strength, -entry.fact_id)

    # ── Ausgabe-Verifikation ────────────────────
    if key[0] < 1 or key[2] > -1 or not math.isfinite(key[1]):
        raise RuntimeError(  # noqa: TRY003 — der Schluessel gehoert in die Meldung
            f"fakten_mappe: Fakt {entry.fact_id} mit Schlüssel {key} außerhalb der Spanne"
        )
    return key


def cap_entries(
    entries:   tuple[MappeEntry, ...],
    max_chars: int,
) -> tuple[tuple[MappeEntry, ...], int]:
    """Kappt die Einträge in Zeichen und gibt die behaltenen und die Zahl der weggelassenen.

    Rein, ohne Datenzugriff. Die Ordnung bleibt; der erste Eintrag, dessen
    `text` nicht mehr passt, beendet die Mappe, und kein kürzerer rückt nach —
    so steht jeder weggelassene Eintrag hinter jedem behaltenen.

    Vorbedingung: `entries` steht in der Ordnung der Mappe (`_order_key`);
        `max_chars` ist eine ganze Zahl ab 1.
    Nachbedingung: Die behaltenen Einträge sind ein Anfangsstück von `entries`,
        ihre Zeichen zusammen höchstens `max_chars`; behaltene und weggelassene
        ergeben zusammen alle.
    Fehlerfälle: ValueError bei ungültigem `max_chars` oder wenn `entries` nicht
        in der Ordnung steht — eine Kappung über eine falsche Ordnung ließe
        einen starken Fakt weg und behielte einen schwachen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
        raise ValueError(  # noqa: TRY003 — der abgewiesene Wert gehoert in die Meldung
            f"fakten_mappe.cap_entries: max_chars ungültig ({max_chars!r})"
        )
    keys: list[tuple[int, float, int]] = [_order_key(e) for e in entries]
    if keys != sorted(keys):
        raise ValueError(  # noqa: TRY003 — die Funktion gehoert in die Meldung
            "fakten_mappe.cap_entries: Einträge nicht in der Ordnung der Mappe"
        )

    # ── Verarbeitung ────────────────────────────
    kept_count: int = 0
    chars:      int = 0
    for entry in entries:
        if chars + len(entry.text) > max_chars:
            break
        chars += len(entry.text)
        kept_count += 1
    kept: tuple[MappeEntry, ...] = tuple(entries[:kept_count])
    omitted: int = len(entries) - kept_count

    # ── Ausgabe-Verifikation ────────────────────
    if sum(len(e.text) for e in kept) > max_chars or len(kept) + omitted != len(entries):
        raise RuntimeError(  # noqa: TRY003 — die Zahlen gehoeren in die Meldung
            f"fakten_mappe.cap_entries: {len(kept)} behalten, {omitted} weggelassen "
            f"von {len(entries)} bei {max_chars} Zeichen — die Kappung rechnet falsch"
        )
    return kept, omitted


def _entry_from_row(row: dict) -> MappeEntry:
    """Formt eine Zeile von `find_umgebung` zu einem Eintrag der Mappe.

    Vorbedingung: `row` trägt die Spalten von `find_umgebung` und `grad`.
    Nachbedingung: Der Eintrag trägt dieselben Werte unter den Namen der Mappe.
    Fehlerfälle: ValueError, wenn eine Spalte fehlt oder `fakt_text` leer ist —
        ein Eintrag ohne Text zählte null Zeichen und schlüpfte durch die Kappung.
    """
    # ── Eingabe-Validierung ─────────────────────
    columns: tuple[str, ...] = (
        "id", "grad", "subjekt_id", "subjekt_name", "attribut", "objekt_id",
        "objekt_name", "objekt_wert", "fakt_text", "herkunft", "staerke_decay",
    )
    missing: list[str] = [c for c in columns if c not in row]
    if missing:
        raise ValueError(  # noqa: TRY003 — Zeile und Spalten gehoeren in die Meldung
            f"fakten_mappe: Zeile id={row.get('id')} ohne Spalten {missing}"
        )
    if not row["fakt_text"] or not row["fakt_text"].strip():
        raise ValueError(  # noqa: TRY003 — die Zeile gehoert in die Meldung
            f"fakten_mappe: Zeile id={row['id']} ohne fakt_text"
        )

    # ── Verarbeitung ────────────────────────────
    entry: MappeEntry = MappeEntry(
        fact_id=row["id"], degree=row["grad"], subject_id=row["subjekt_id"],
        subject_name=row["subjekt_name"], relation=row["attribut"],
        object_id=row["objekt_id"], object_name=row["objekt_name"],
        object_value=row["objekt_wert"], text=row["fakt_text"],
        origin=row["herkunft"], strength=float(row["staerke_decay"]),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if (entry.object_id is None) == (entry.object_value is None):
        raise RuntimeError(  # noqa: TRY003 — Fakt und Werte gehoeren in die Meldung
            f"fakten_mappe: Fakt {entry.fact_id} trägt nicht genau eines von "
            f"Objekt und Wert ({entry.object_id!r}, {entry.object_value!r})"
        )
    return entry


def load_mappe(  # noqa: PLR0913 — Paar, Entität und zwei Stellgrößen; die zwei nur benannt
    postgres_url: str,
    user_id:      str,
    character_id: str,
    entity_id:    int,
    *,
    depth:        int = FAKTEN_MAPPE_TIEFE,
    max_chars:    int = FAKTEN_MAPPE_MAX_ZEICHEN,
) -> Mappe:
    """Lädt die Mappe einer Entität des Paares, gekappt in Zeichen.

    Vorbedingung: Das Paar ist vollständig; `depth` und `max_chars` sind ganze
        Zahlen ab 1. Die übrigen Werte prüft `find_umgebung`.
    Nachbedingung: Nichts wurde geschrieben. Die Einträge stehen in der
        Ordnung der Mappe, jeder Fakt einmal, keiner tiefer als `depth`;
        `chars ≤ max_chars`; `truncated` gilt genau dann, wenn die Kappung
        oder die Grenze der Zeilen Fakten weggelassen hat.
    Fehlerfälle: ValueError bei ungültiger Eingabe. `EntityNotFoundError`
        (aus dem Repository, ein LookupError) bei einer unbekannten Entität
        oder der eines anderen Menschen — nur dieser Fehler heißt *unbekannt*;
        ein ValueError oder LookupError aus dem Inneren ist ein Ausfall. Ein Fehler der
        Datenbank geht als Ausnahme an den Aufrufer — nie als leere Mappe.
        RuntimeError, wenn das Ergebnis die Nachbedingung verletzt.
    """
    # ── Eingabe-Validierung ─────────────────────
    for name, value in (("depth", depth), ("max_chars", max_chars)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(  # noqa: TRY003 — der abgewiesene Wert gehoert in die Meldung
                f"fakten_mappe.load_mappe: {name} ungültig ({value!r})"
            )

    # ── Verarbeitung ────────────────────────────
    surroundings: Surroundings = FaktenRepository.find_umgebung(
        postgres_url, user_id, character_id, entity_id, depth=depth,
        min_strength=FAKTEN_MAPPE_MIN_STAERKE, max_rows=FAKTEN_MAPPE_MAX_ZEILEN_JE_GRAD,
    )
    # Nicht neu sortiert: Die Ordnung kommt aus der Abfrage, und `cap_entries`
    # weist sie ab, wenn sie nicht stimmt — ein Sortieren hier verdeckte das.
    all_entries: tuple[MappeEntry, ...] = tuple(
        _entry_from_row(row) for row in surroundings.rows
    )
    kept, omitted = cap_entries(all_entries, max_chars)
    mappe: Mappe = Mappe(
        entity_id=entity_id, entity_name=surroundings.entity_name, depth=depth,
        entries=kept, truncated=omitted > 0 or surroundings.row_limit_hit,
        omitted=omitted, chars=sum(len(e.text) for e in kept),
    )

    # ── Ausgabe-Verifikation ────────────────────
    fact_ids: list[int] = [e.fact_id for e in mappe.entries]
    if len(set(fact_ids)) != len(fact_ids) or any(e.degree > depth for e in mappe.entries):
        raise RuntimeError(  # noqa: TRY003 — die Fakten gehoeren in die Meldung
            f"fakten_mappe.load_mappe: Entität {entity_id} — ein Fakt doppelt oder "
            f"tiefer als {depth} ({[(e.fact_id, e.degree) for e in mappe.entries]})"
        )
    if mappe.chars > max_chars:
        raise RuntimeError(  # noqa: TRY003 — die Zahlen gehoeren in die Meldung
            f"fakten_mappe.load_mappe: {mappe.chars} Zeichen über dem Maximum {max_chars}"
        )
    logger.info(
        "fakten_mappe: Entität %s, Tiefe %d — %d Einträge, %d Zeichen, gekürzt=%s "
        "(%d weggelassen, Grenze der Zeilen getroffen=%s)",
        entity_id, depth, len(mappe.entries), mappe.chars, mappe.truncated,
        omitted, surroundings.row_limit_hit,
    )
    return mappe
