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


def format_memory_entries(
    entries: list[ContextEntry],
    lzg_resonanz: dict | None = None,
) -> str:
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
        6. LZG-Resonanz — optionaler [GEDAECHTNIS]-Block ganz am Ende
           (assoziative Spreading-Erinnerungen mit Pfad-Begruendung, §8.4.4)

    Args:
        entries: Liste strukturierter ContextEntry-Eintraege, vorsortiert
                 oder unsortiert. Die Funktion uebernimmt die Sortierung.
        lzg_resonanz: Optionale Resonanz-Struktur aus dem Enricher (§8.4.2).
                 Enthaelt sie Erinnerungen, wird der §8.4.4-Block am Ende
                 angehaengt. None / ohne Erinnerungen -> kein Block (rueckwaerts-
                 kompatibel zu Aufrufern, die nur entries uebergeben).

    Returns:
        Der finale memory_context-String. Leerstring, wenn weder Entries noch
        Resonanz-Erinnerungen vorliegen.
    """
    logger.info(f"format_memory_entries: {len(entries)} Eintraege erhalten")

    hat_resonanz: bool = bool(lzg_resonanz and lzg_resonanz.get("erinnerungen"))
    if not entries and not hat_resonanz:
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

    # LZG-Resonanz (§8.4.4): assoziative Spreading-Erinnerungen ganz am Ende,
    # direkt vor dem, was der Responder zuletzt liest. Zusaetzlich, ersetzt nichts.
    if lzg_resonanz and lzg_resonanz.get("erinnerungen"):
        resonanz_block: str = _format_lzg_resonanz(lzg_resonanz)
        if resonanz_block:
            blocks.append(resonanz_block)

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
    """LZG-Block: [LZG/{subtyp}] (Gewicht/Arousal/Beobachter): {inhalt}.

    Defaults bei fehlenden meta-Feldern:
        arousal    = 0.0
        beobachter = "unbekannt"
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

    return (
        f"[LZG/{subtyp}] (Gewicht: {gewicht:.2f}, "
        f"Arousal: {arousal:.0%}, "
        f"Beobachter: {beobachter}): {inhalt}"
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


# ─────────────────────────────────────────────
# LZG-Resonanz-Block (§8.4.4)
# ─────────────────────────────────────────────
_ANZAHL_WOERTER: dict[int, str] = {1: "Eine", 2: "Zwei", 3: "Drei"}


def _schritt_verbalisieren(schritt: dict) -> str:
    """Verbalisiert einen einzelnen Pfad-Schritt aus seinen Verbindungs-Gruenden.

    Schritt-Felder: verbindungs_gruende (welche Schichten griffen) plus die
    konkreten geteilten Werte. Themen werden mit Namen ausgegeben; Entitaeten
    liegen nur als IDs vor (keine Namens-Aufloesung hier) und werden daher nur
    generisch erwaehnt (Backlog LZG-RESONANZ-ENTITAET-NAMEN).
    """
    gruende: list = schritt.get("verbindungs_gruende") or []
    teile: list[str] = []

    if "themen" in gruende:
        geteilte_themen: list = schritt.get("geteilte_themen") or []
        if geteilte_themen:
            teile.append(f"gemeinsames Thema {', '.join(geteilte_themen)}")

    if "entitaet" in gruende and not teile:
        # geteilte_entitaet_ids sind IDs (INTEGER[]), keine Namen — generisch.
        geteilte_ent: list = schritt.get("geteilte_entitaet_ids") or []
        if geteilte_ent:
            teile.append("eine gemeinsame Person/Sache")

    if "timeline" in gruende:
        teile.append("zeitliche Naehe")

    if "embedding" in gruende:
        teile.append("aehnlichen Inhalt")

    if not teile:
        return "eine Assoziation"
    return " und ".join(teile)


def _herkunft_zeile(pfad: list) -> str:
    """Baut die Herkunfts-Zeile einer Erinnerung aus ihrem Spreading-Pfad.

    Leerer Pfad (Schale 0) = Direkttreffer. Sonst werden alle Pfad-Schritte
    mit ' -> ' verkettet, sodass die assoziative Kette nachvollziehbar ist
    (§8.4.4: alle Pfad-Schritte aufgefuehrt).
    """
    if not pfad:
        return "Sie kam dir direkt zur Frage in den Sinn"
    schritte: list[str] = [_schritt_verbalisieren(s) for s in pfad]
    return "Sie ist dir eingefallen ueber: " + " -> ".join(schritte)


def _format_lzg_resonanz(resonanz: dict) -> str:
    """Rendert die assoziative Resonanz als Erinnerungs-Block (§8.4.4).

    Setzt KEINEN [GEDAECHTNIS]-Header — der Responder wickelt den gesamten
    memory_context bereits in das Template responder.gedaechtnis.txt, das
    selbst mit [GEDAECHTNIS] beginnt. Ein innerer Header waere eine Dopplung.

    Reihenfolge: nach sortier_gewicht AUFSTEIGEND (am wenigsten praesente
    zuerst, staerkste am Ende — Recency). Die Eingabe kommt vom Enricher
    absteigend (rang 1 = staerkste), wird hier also umgekehrt.

    Interne Werte (Gewicht, Schale, knoten_id) erscheinen NICHT im Output;
    erstellt_am wird nicht verwendet. Leere Erinnerungs-Liste -> Leerstring
    (keine Einleitungszeile).
    """
    erinnerungen: list = resonanz.get("erinnerungen") or []
    if not erinnerungen:
        return ""

    geordnet: list = sorted(erinnerungen, key=lambda e: e.get("sortier_gewicht", 0.0))
    anzahl: int = len(geordnet)

    if anzahl == 1:
        einleitung: str = "Eine Erinnerung ist dir gerade da."
    else:
        einleitung = (
            f"{_ANZAHL_WOERTER.get(anzahl, str(anzahl))} Erinnerungen sind dir gerade da. "
            "Die am wenigsten praesente zuerst, die staerkste am Ende."
        )

    zeilen: list[str] = [einleitung]
    for nummer, erinnerung in enumerate(geordnet, start=1):
        zeilen.append(f"----- Erinnerung {nummer} -----")
        inhalt: str = (erinnerung.get("inhalt") or "").strip()
        zeilen.append(f'"{inhalt}"')

        emotion: str = (erinnerung.get("emotion") or "").strip()
        if emotion and emotion.lower() != "neutral":
            zeilen.append(f"Du fuehlst dazu: {emotion.capitalize()}")

        zeilen.append(_herkunft_zeile(erinnerung.get("pfad") or []))

    return "\n".join(zeilen)
