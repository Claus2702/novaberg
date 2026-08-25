"""Reducer — dedupliziert memory_entries und baut den finalen memory_context.

Sitzt im Graph zwischen Enricher und Router (db_zugriff -> ei_calc ->
enricher -> reducer -> router). Liest die strukturierten
ContextEntry-Eintraege, die der Enricher gesammelt hat, dedupliziert sie
in zwei Stufen (Exakt-Dedup + Substring-Dedup), und ruft den zentralen
Formatter auf, der den finalen memory_context-String fuer den Responder
und nachfolgende Konsumenten baut.

Doku: novaberg-node-reducer.md (Format-Vertrag und Dedup-Mechanik).
"""

import logging
import re

from graph.context_entry import ContextEntry
from graph.format import format_memory_entries
from graph.state import zustand_verifizieren

logger = logging.getLogger(__name__)


# Die Felder, die JEDER Rueckkehrpfad dieses Knotens setzt. Ein Pfad, der eines
# auslaesst, liesse den vorigen Stand stehen — und der laese sich wie ein
# frisches Ergebnis (22_STILLE_FEHLER §5).
SCHREIBT = frozenset({"memory_entries_raw", "memory_entries", "memory_context"})


def reduce_memory(state: dict) -> dict:
    """Reducer-Node: dedupliziert memory_entries, baut memory_context.

    Stufe 1 — Exakt-Dedup:
        Schluessel: normalisiertes inhalt-Feld (lowercase, kollabierte
        Whitespaces). Bei Konflikt: Eintrag mit hoechstem gewicht gewinnt;
        Gleichstand → erster Eintrag (Eingangsreihenfolge).

    Stufe 2 — Substring-Dedup:
        Sortiert absteigend nach len(inhalt). Verwirft kuerzere Eintraege,
        deren normalisierter Inhalt vollstaendig im Inhalt eines laengeren
        Eintrags enthalten ist. Mindestlaenge 10 Zeichen, sonst Falsch-
        Positiv-Risiko bei kurzen Phrasen.

    Args:
        state: Graph-State, muss state["memory_entries"] enthalten.

    Returns:
        State-Update mit:
        - memory_entries_raw: list[ContextEntry] — Backup vor Dedup
        - memory_entries: list[ContextEntry] — dedupliziert
        - memory_context: str — formatierter String fuer den Responder
    """
    entries: list[ContextEntry] = state.get("memory_entries", [])
    eingangsanzahl: int = len(entries)
    logger.info(f"Reducer: Start, {eingangsanzahl} Eintraege erhalten")

    # Backup vor jeder Veraenderung
    raw_backup: list[ContextEntry] = list(entries)

    # Resonanz-Akte (§8.4.4) — Clipboard-Prinzip: der Reducer nimmt aus dem
    # State, was der Formatter braucht. Kein Pflichtfeld (AgentGraph/Cold-Start
    # → None, dann rendert der Formatter keinen Resonanz-Block).
    lzg_resonanz = state.get("lzg_resonanz")
    resonanz_anzahl: int = len((lzg_resonanz or {}).get("erinnerungen", []))

    if not entries:
        # Resonanz-only-Turn: Spreading-Erinnerungen ohne KZG/Charakter-Treffer.
        # Der Block darf NICHT verschluckt werden — Formatter trotzdem aufrufen.
        if resonanz_anzahl > 0:
            logger.info(
                f"Reducer: Keine Eintraege, aber lzg_resonanz mit {resonanz_anzahl} "
                f"Erinnerungen — nur Resonanz-Block"
            )
            # ── Ausgabe-Verifikation ────────────────────
            return zustand_verifizieren({
                "memory_entries_raw": raw_backup,
                "memory_entries": [],
                "memory_context": format_memory_entries([], lzg_resonanz=lzg_resonanz),
            }, "reducer", SCHREIBT)
        logger.info("Reducer: Keine Eintraege — leerer memory_context")
        # ── Ausgabe-Verifikation ────────────────────
        return zustand_verifizieren({
            "memory_entries_raw": raw_backup,
            "memory_entries": [],
            "memory_context": "",
        }, "reducer", SCHREIBT)

    # Stufe 1: Exakt-Dedup
    nach_stufe1: list[ContextEntry] = _exakt_dedup(entries)
    entfernt_stufe1: int = eingangsanzahl - len(nach_stufe1)
    if entfernt_stufe1 > 0:
        logger.info(f"Reducer: Stufe 1 (Exakt-Dedup) entfernte {entfernt_stufe1} Eintraege")

    # Stufe 2: Substring-Dedup
    nach_stufe2: list[ContextEntry] = _substring_dedup(nach_stufe1)
    entfernt_stufe2: int = len(nach_stufe1) - len(nach_stufe2)
    if entfernt_stufe2 > 0:
        logger.info(f"Reducer: Stufe 2 (Substring-Dedup) entfernte {entfernt_stufe2} Eintraege")

    # Formatter aufrufen — einziger Ort, an dem Format-Wissen lebt.
    # lzg_resonanz wird durchgereicht (§8.4.4-Block); None -> kein Block.
    if resonanz_anzahl > 0:
        logger.info(f"Reducer: lzg_resonanz mit {resonanz_anzahl} Erinnerungen an Formatter")
    else:
        logger.info("Reducer: keine lzg_resonanz")
    memory_context: str = format_memory_entries(nach_stufe2, lzg_resonanz=lzg_resonanz)

    logger.info(
        f"Reducer: Abgeschlossen — {eingangsanzahl} → {len(nach_stufe2)} Eintraege "
        f"({entfernt_stufe1 + entfernt_stufe2} entfernt), Output-Laenge {len(memory_context)} Zeichen"
    )

    # ── Ausgabe-Verifikation ────────────────────
    return zustand_verifizieren({
        "memory_entries_raw": raw_backup,
        "memory_entries": nach_stufe2,
        "memory_context": memory_context,
    }, "reducer", SCHREIBT)


# ---------- Private Helfer ----------

_WHITESPACE_PATTERN = re.compile(r"\s+")


def _normalisiere(text: str) -> str:
    """Normalisiert Inhalt fuer Dedup-Vergleich: lowercase, kollabierte Whitespaces."""
    return _WHITESPACE_PATTERN.sub(" ", text.lower().strip())


def _exakt_dedup(entries: list[ContextEntry]) -> list[ContextEntry]:
    """Stufe 1: Bei identischem normalisiertem Inhalt → hoechstes Gewicht gewinnt.

    Bei Gleichstand: erster Eintrag bleibt (Eingangsreihenfolge).
    """
    seen: dict[str, ContextEntry] = {}
    result: list[ContextEntry] = []

    for entry in entries:
        key: str = _normalisiere(entry["inhalt"])
        if key not in seen:
            seen[key] = entry
            result.append(entry)
        else:
            existing: ContextEntry = seen[key]
            if entry["gewicht"] > existing["gewicht"]:
                # Tausch: alten Entry aus result entfernen, neuen einfuegen
                idx: int = result.index(existing)
                result[idx] = entry
                seen[key] = entry
                logger.debug(
                    f"Reducer: Stufe 1 ersetzt — quelle={entry['quelle']}, "
                    f"alt-gewicht={existing['gewicht']:.2f}, neu-gewicht={entry['gewicht']:.2f}, "
                    f"snippet={entry['inhalt'][:60]}"
                )
            else:
                logger.debug(
                    f"Reducer: Stufe 1 verwarf — quelle={entry['quelle']}, "
                    f"gewicht={entry['gewicht']:.2f}, snippet={entry['inhalt'][:60]}"
                )
    return result


_MIN_LENGTH: int = 10

def _substring_dedup(entries: list[ContextEntry]) -> list[ContextEntry]:
    """Stufe 2: Kuerzere Eintraege, die in laengeren enthalten sind, verwerfen.

    Mindestlaenge 10 Zeichen, sonst Falsch-Positiv-Risiko.
    Sortierung nach Inhalt-Laenge absteigend stellt sicher, dass das laengste
    Original bestehen bleibt und nur Kuerzlinge wegfallen.
    """
    sortiert: list[ContextEntry] = sorted(
        entries, key=lambda e: len(e["inhalt"]), reverse=True
    )
    result: list[ContextEntry] = []
    normalisierte: list[str] = []

    for entry in sortiert:
        norm: str = _normalisiere(entry["inhalt"])
        if len(norm) < _MIN_LENGTH:
            result.append(entry)
            normalisierte.append(norm)
            continue

        ist_substring: bool = any(norm in laengeres for laengeres in normalisierte)
        if ist_substring:
            logger.debug(
                f"Reducer: Stufe 2 verwarf Substring — quelle={entry['quelle']}, "
                f"snippet={entry['inhalt'][:60]}"
            )
        else:
            result.append(entry)
            normalisierte.append(norm)

    # Nach Stufe 2 die ursprüngliche Reihenfolge wiederherstellen — der Formatter
    # sortiert ohnehin selbst nach Quelle/Gewicht (Konzept §9 R5). Aber für
    # deterministisches Verhalten geben wir die Eingangsreihenfolge zurueck.
    eingangs_reihenfolge: dict[int, int] = {id(e): i for i, e in enumerate(entries)}
    result.sort(key=lambda e: eingangs_reihenfolge.get(id(e), 999999))
    return result
