"""Formatter fuer den memory_context-String.

Wandelt eine Liste strukturierter ContextEntry-Eintraege in den
finalen memory_context-String um, den der Responder als Reasoning-
Hintergrund liest und den der Thinker im memory_search-Tool an das
LLM zurueckgibt.

Die Funktion ist als oeffentliche, wiederverwendbare API ausgelegt.
Aktuelle Konsumenten:
- Reducer-Node (STRUCT-6): nach Dedup auf state["memory_entries"]
- Thinker memory_search-Tool: nach Abruf via lzg_entries_retrieve

Format-Vertrag und Reihenfolge sind durch das Reducer-Umbau-
Konzept (novaberg-reducer-umbau_k.md, Abschnitte 6 und 9) festgelegt.
"""

import logging

from graph.context_entry import ContextEntry

logger = logging.getLogger(__name__)


_SUMMARY_HEADER: str = "═══ BISHERIGER GESPRÄCHSVERLAUF ═══"


def format_memory_entries(entries: list[ContextEntry]) -> str:
    """Baut den finalen memory_context-String aus strukturierten Entries.

    Sortiert die Entries nach Quellen-Reihenfolge (siehe Konzept §9 R5),
    formatiert pro Quelle nach Format-Vertrag (siehe Konzept §6) und
    fuegt die Bloecke mit Newlines zusammen.

    Reihenfolge:
        1. summary  — alle, in Eingangsreihenfolge
        2. charakter — alle, in Eingangsreihenfolge
        3. kzg + lzg — gemeinsam, nach gewicht absteigend (stabil)
        4. plugin_*  — alle, in Eingangsreihenfolge
        5. unbekannte Quellen — am Ende, in Eingangsreihenfolge,
           mit Logging-Warnung pro Eintrag (kein Crash)

    Args:
        entries: Liste strukturierter ContextEntry-Eintraege, vorsortiert
                 oder unsortiert. Die Funktion uebernimmt die Sortierung.

    Returns:
        Der finale memory_context-String. Leerstring, wenn entries leer.
    """
    logger.info(f"format_memory_entries: {len(entries)} Eintraege erhalten")

    if not entries:
        logger.info("format_memory_entries: Output-Laenge 0 Zeichen")
        return ""

    # ── Buckets nach Quelle ──────────────────
    summary_group:   list[ContextEntry] = []
    charakter_group: list[ContextEntry] = []
    memory_group:    list[ContextEntry] = []   # kzg + lzg, sortiert nach gewicht
    plugin_group:    list[ContextEntry] = []
    unknown_group:   list[ContextEntry] = []

    for entry in entries:
        quelle: str = entry.get("quelle", "")
        if quelle == "summary":
            summary_group.append(entry)
        elif quelle == "charakter":
            charakter_group.append(entry)
        elif quelle in ("kzg", "lzg"):
            memory_group.append(entry)
        elif quelle.startswith("plugin_"):
            plugin_group.append(entry)
        else:
            logger.warning(
                f"format_memory_entries: Unbekannte Quelle '{quelle}' "
                f"— wird ans Ende angehaengt"
            )
            unknown_group.append(entry)

    # KZG/LZG: nach gewicht absteigend, stabil
    memory_group.sort(key=lambda e: e.get("gewicht", 0.0), reverse=True)

    logger.debug(f"format_memory_entries: Gruppe summary: {len(summary_group)} Eintraege")
    logger.debug(f"format_memory_entries: Gruppe charakter: {len(charakter_group)} Eintraege")
    logger.debug(f"format_memory_entries: Gruppe kzg+lzg: {len(memory_group)} Eintraege")
    logger.debug(f"format_memory_entries: Gruppe plugin_*: {len(plugin_group)} Eintraege")
    if unknown_group:
        logger.debug(f"format_memory_entries: Gruppe unbekannt: {len(unknown_group)} Eintraege")

    # ── Formatieren ──────────────────────────
    blocks: list[str] = []

    for entry in summary_group:
        blocks.append(_format_summary(entry))

    for entry in charakter_group:
        blocks.append(_format_charakter(entry))

    for entry in memory_group:
        if entry.get("quelle") == "kzg":
            blocks.append(_format_kzg(entry))
        else:
            blocks.append(_format_lzg(entry))

    for entry in plugin_group:
        blocks.append(_format_plugin(entry))

    for entry in unknown_group:
        blocks.append(_format_unknown(entry))

    result: str = "\n".join(blocks)
    logger.info(f"format_memory_entries: Output-Laenge {len(result)} Zeichen")
    return result


# ─────────────────────────────────────────────
# Private Formatter pro Quelle
# ─────────────────────────────────────────────
def _format_summary(entry: ContextEntry) -> str:
    """Spezial-Block: Header-Zeile, dann Inhalt darunter."""
    inhalt: str = entry.get("inhalt", "")
    return f"{_SUMMARY_HEADER}\n{inhalt}"


def _format_charakter(entry: ContextEntry) -> str:
    """Einzeiliger Praefix; Inhalt direkt anschliessend (Newlines im Inhalt
    werden belassen)."""
    inhalt: str = entry.get("inhalt", "")
    return f"[Charakter] {inhalt}"


def _format_kzg(entry: ContextEntry) -> str:
    """KZG-Block: [KZG] {themen} (Salienz: {gewicht}): {inhalt}.

    themen kann als Liste oder String vorliegen. Liste wird mit
    ', ' joined; String unveraendert; sonst Leerstring.
    gewicht wird mit der Default-Float-Repraesentation ausgegeben
    (1.5, nicht 1.50).
    """
    inhalt:  str = entry.get("inhalt", "")
    gewicht      = entry.get("gewicht", 0.0)
    meta:    dict = entry.get("meta", {}) or {}

    themen = meta.get("themen", "")
    if isinstance(themen, list):
        themen_str: str = ", ".join(themen)
    elif isinstance(themen, str):
        themen_str = themen
    else:
        themen_str = ""

    return f"[KZG] {themen_str} (Salienz: {gewicht}): {inhalt}"


def _format_lzg(entry: ContextEntry) -> str:
    """LZG-Block: [LZG/{subtyp}] (Gewicht/Arousal/Beobachter/Vektor): {inhalt}.

    Defaults bei fehlenden meta-Feldern:
        arousal    = 0.0
        beobachter = "unbekannt"
        vektor     = "unbekannt"
    Leerer subtyp wird unveraendert eingesetzt ([LZG/] ... ).
    """
    subtyp:  str   = entry.get("subtyp", "")
    inhalt:  str   = entry.get("inhalt", "")
    gewicht: float = entry.get("gewicht", 0.0)
    meta:    dict  = entry.get("meta", {}) or {}

    arousal = meta.get("arousal")
    if arousal is None:
        logger.debug("format_memory_entries: lzg arousal fehlt — Default 0.0")
        arousal = 0.0

    beobachter = meta.get("beobachter")
    if not beobachter:
        logger.debug("format_memory_entries: lzg beobachter fehlt — Default 'unbekannt'")
        beobachter = "unbekannt"

    vektor = meta.get("vektor")
    if not vektor:
        logger.debug("format_memory_entries: lzg vektor fehlt — Default 'unbekannt'")
        vektor = "unbekannt"

    return (
        f"[LZG/{subtyp}] (Gewicht: {gewicht:.2f}, "
        f"Arousal: {arousal:.0%}, "
        f"Beobachter: {beobachter}, "
        f"Vektor: {vektor}): {inhalt}"
    )


def _format_plugin(entry: ContextEntry) -> str:
    """Plugin-Block: [{meta.praefix}] {inhalt} (einzeilig) oder
    [{meta.praefix}]\\n{inhalt} (mehrzeilig).

    Fehlt meta['praefix'], wird WARNING geloggt und als Fallback
    quelle.replace('plugin_', '') verwendet.
    """
    quelle: str  = entry.get("quelle", "")
    inhalt: str  = entry.get("inhalt", "")
    meta:   dict = entry.get("meta", {}) or {}

    praefix = meta.get("praefix")
    if not praefix:
        logger.warning(
            f"format_memory_entries: plugin-Eintrag ohne meta['praefix'] "
            f"(quelle={quelle}, inhalt-snippet={inhalt[:60]}) — Fallback aus quelle"
        )
        praefix = quelle.replace("plugin_", "")

    if "\n" in inhalt:
        return f"[{praefix}]\n{inhalt}"
    return f"[{praefix}] {inhalt}"


def _format_unknown(entry: ContextEntry) -> str:
    """Fallback fuer unbekannte Quellen — generisches Klammer-Format,
    verhindert Crash. Logging erfolgt bereits im Bucketing.
    """
    quelle: str = entry.get("quelle", "")
    inhalt: str = entry.get("inhalt", "")
    if "\n" in inhalt:
        return f"[{quelle}]\n{inhalt}"
    return f"[{quelle}] {inhalt}"
