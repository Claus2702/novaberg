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


# Die Namen des Lesers (30.08.2026). Das Modell ist der Schauspieler, der
# Charakter der Auftrag — kein Block spricht das Modell als den Charakter an.
# Die Analyse-Knoten (Thinker, Tribunal, Corrector) lesen in dritter Person
# mit Namen; der Verfasser kennt nur Person A (den Charakter) und Person B
# (den Menschen). Bis zum 30.08.2026 trug der Block »Du fuehlst dazu« und
# »Sie ist dir eingefallen« — das »du« meinte den Charakter, und der
# Verfasser-Prompt sprach in zwei Namenssystemen.
LESER_ANALYSE:   str = "analyse"
LESER_VERFASSER: str = "verfasser"
_NAMES: dict[str, dict[str, str]] = {
    LESER_ANALYSE:   {"nova": "Nova",     "nutzer": "Nutzer"},
    LESER_VERFASSER: {"nova": "Person A", "nutzer": "Person B"},
}


def reader_names(leser: str, aufrufer: str) -> dict[str, str]:
    """Die Personennamen fuer den Leser eines Blocks — oder ein lauter Fehler.

    Vorbedingung: `leser` ist LESER_ANALYSE oder LESER_VERFASSER.
    Nachbedingung: das Namens-Dict (`nova`, `nutzer`); ein unbekannter Leser
        ist ein ValueError, kein Rueckfall — ein Block im falschen
        Namenssystem saehe richtig aus.
    """
    if leser not in _NAMES:
        meldung: str = f"{aufrufer}: unbekannter Leser {leser!r}"
        raise ValueError(meldung)
    return _NAMES[leser]


def format_memory_entries(
    entries: list[ContextEntry],
    lzg_resonanz: dict | None = None,
    leser: str = LESER_ANALYSE,
) -> str:
    """Baut den finalen memory_context-String aus strukturierten Entries.

    Sortiert die Entries nach Quellen-Reihenfolge (siehe Konzept §9 R5),
    formatiert pro Quelle nach Format-Vertrag (siehe Konzept §6) und
    fuegt die Bloecke mit Newlines zusammen — in den Namen des Lesers
    (`leser`: LESER_ANALYSE nennt Nova und den Nutzer, LESER_VERFASSER
    Person A und Person B; ein anderer Wert ist ein ValueError).

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
    names: dict[str, str] = reader_names(leser, "format_memory_entries")
    logger.info(f"format_memory_entries: {len(entries)} Eintraege erhalten (Leser {leser})")

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
            blocks.append(_format_kzg(entry, names))
        else:
            blocks.append(_format_lzg(entry))

    for entry in plugin_group:
        blocks.append(_format_plugin(entry))

    for entry in unknown_group:
        blocks.append(_format_unknown(entry))

    # LZG-Resonanz (§8.4.4): assoziative Spreading-Erinnerungen ganz am Ende,
    # direkt vor dem, was der Responder zuletzt liest. Zusaetzlich, ersetzt nichts.
    if lzg_resonanz and lzg_resonanz.get("erinnerungen"):
        resonanz_block: str = _format_lzg_resonanz(lzg_resonanz, names)
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
    werden belassen).
    """
    inhalt: str = entry.get("inhalt", "")
    return f"[Charakter] {inhalt}"


# Der Sprecher eines Gedaechtniseintrags, in Worten. `beobachter` ist der
# Schreiber des Eintrags (Paar-Schema: user = das Gegenueber, assistant = Nova)
# und damit, wer die Sache gesagt hat. Seit dem 29.08.2026 steht er im Block:
# Ohne ihn erschien ein Nutzersatz als Novas Erinnerung — `[gemessen]` am
# Bestand desselben Tages: 3029 `assistant` / 219 `user` in `lzg_knoten`,
# im KZG 276 / 24 von 300. Die Worte sind die des Gespraechsvektors; die
# Umstellung des ganzen Blocks auf die Namen seines Lesers steht aus.
_SPEAKER_KEYS: dict[str, str] = {"user": "nutzer", "assistant": "nova"}


def speaker_label(beobachter: object, names: dict[str, str] | None = None) -> str:
    """Der Sprecher eines Eintrags in Worten — oder 'unbekannt', und das gemeldet.

    Vorbedingung: keine — jeder Wert ist zulaessig, nur zwei sind bekannt.
    Nachbedingung: das Wort des Lesers fuer den Nutzer oder den Charakter
        (`names`, ohne Angabe die der Analyse: 'Nutzer', 'Nova') oder
        'unbekannt'; ein Wert ausserhalb des Kanons (auch None und '') steht
        im Log als Warnung, denn ein Eintrag ohne Sprecher ist ein Defekt
        seiner Quelle, kein Normalfall.

    Args:
        beobachter: der Schreiber des Eintrags, wie die Quelle ihn liefert.
        names: die Namen des Lesers (`reader_names`).

    Returns:
        Das Wort fuer den Sprecher.
    """
    woerter: dict[str, str] = names if names is not None else _NAMES[LESER_ANALYSE]
    if isinstance(beobachter, str) and beobachter in _SPEAKER_KEYS:
        return woerter[_SPEAKER_KEYS[beobachter]]
    logger.warning(
        f"format_memory_entries: beobachter {beobachter!r} ausserhalb des Kanons "
        f"(user|assistant) — Sprecher unbekannt"
    )
    return "unbekannt"


def _format_kzg(entry: ContextEntry, names: dict[str, str]) -> str:
    """KZG-Block: [KZG] {themen} (Salienz: {gewicht}, Sprecher: {wer}): {inhalt}.

    themen kann als Liste oder String vorliegen. Liste wird mit
    ', ' joined; String unveraendert; sonst Leerstring.
    gewicht wird mit der Default-Float-Repraesentation ausgegeben
    (1.5, nicht 1.50). Der Sprecher kommt aus meta['beobachter']
    (`speaker_label`, in den Namen des Lesers) — bis zum 29.08.2026 verwarf
    diese Funktion ihn.
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

    sprecher: str = speaker_label(meta.get("beobachter"), names)
    return f"[KZG] {themen_str} (Salienz: {gewicht}, Sprecher: {sprecher}): {inhalt}"


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
    r"""Plugin-Block: [{meta.praefix}] {inhalt} (einzeilig) oder
    [{meta.praefix}]\n{inhalt} (mehrzeilig).

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


def _herkunft_zeile(pfad: list, wer: str) -> str:
    """Baut die Herkunfts-Zeile einer Erinnerung aus ihrem Spreading-Pfad.

    Leerer Pfad (Schale 0) = Direkttreffer. Sonst werden alle Pfad-Schritte
    mit ' -> ' verkettet, sodass die assoziative Kette nachvollziehbar ist
    (§8.4.4: alle Pfad-Schritte aufgefuehrt). `wer` ist der Name des
    Charakters in den Worten des Lesers — die Erinnerung ist seine, und der
    Block spricht ueber ihn, nicht zu ihm.
    """
    if not pfad:
        return f"Sie kam {wer} direkt zur Frage in den Sinn"
    schritte: list[str] = [_schritt_verbalisieren(s) for s in pfad]
    return f"Sie ist {wer} eingefallen ueber: " + " -> ".join(schritte)


def _format_lzg_resonanz(resonanz: dict, names: dict[str, str]) -> str:
    """Rendert die assoziative Resonanz als Erinnerungs-Block (§8.4.4).

    Setzt KEINEN [GEDAECHTNIS]-Header — der Verfasser wickelt den gesamten
    memory_context bereits in das Template responder.gedaechtnis.txt, das
    selbst mit [GEDAECHTNIS] beginnt. Ein innerer Header waere eine Dopplung.

    Reihenfolge: nach sortier_gewicht AUFSTEIGEND (am wenigsten praesente
    zuerst, staerkste am Ende — Recency). Die Eingabe kommt vom Enricher
    absteigend (rang 1 = staerkste), wird hier also umgekehrt.

    Interne Werte (Gewicht, Schale, knoten_id) erscheinen NICHT im Output;
    erstellt_am wird nicht verwendet. Leere Erinnerungs-Liste -> Leerstring
    (keine Einleitungszeile). Der Block spricht in dritter Person ueber den
    Charakter, in den Namen des Lesers (`names['nova']`) — bis zum
    30.08.2026 sagte er »dir« und »Du fuehlst« und meinte den Charakter.
    """
    erinnerungen: list = resonanz.get("erinnerungen") or []
    if not erinnerungen:
        return ""

    wer: str = names["nova"]
    geordnet: list = sorted(erinnerungen, key=lambda e: e.get("sortier_gewicht", 0.0))
    anzahl: int = len(geordnet)

    if anzahl == 1:
        einleitung: str = f"Eine Erinnerung ist {wer} gerade da."
    else:
        einleitung = (
            f"{_ANZAHL_WOERTER.get(anzahl, str(anzahl))} Erinnerungen sind {wer} gerade da. "
            "Die am wenigsten praesente zuerst, die staerkste am Ende."
        )

    zeilen: list[str] = [einleitung]
    for nummer, erinnerung in enumerate(geordnet, start=1):
        zeilen.append(f"----- Erinnerung {nummer} -----")
        inhalt: str = (erinnerung.get("inhalt") or "").strip()
        zeilen.append(f'"{inhalt}"')
        # Wer es gesagt hat — ein woertliches Zitat ohne Sprecher liest sich als
        # eigene Erinnerung, auch wenn es der Nutzer war (29.08.2026).
        zeilen.append(f"Sprecher: {speaker_label(erinnerung.get('beobachter'), names)}")

        emotion: str = (erinnerung.get("emotion") or "").strip()
        if emotion and emotion.lower() != "neutral":
            zeilen.append(f"{wer} fuehlt dazu: {emotion.capitalize()}")

        zeilen.append(_herkunft_zeile(erinnerung.get("pfad") or [], wer))

    return "\n".join(zeilen)
