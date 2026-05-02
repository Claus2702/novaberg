"""
Reducer Node — Deduplizierung des memory_context.

Aufgabe (Chat 74):
  Der Enricher liefert memory_context als String aus mehreren Quellen
  (KZG, LZG, Plugin-Hooks, Charakter-Hash). Bei thematischer Verstaerkung
  und Quellen-Ueberlappung tauchen identische oder nahezu identische
  Eintraege mehrfach auf (siehe ENRICHER-DUP).

  Der Reducer reinigt den Kontext vor dem Responder:
    Stufe 1: Exakt-Dedup nach normalisiertem Inhalt.
    Stufe 2: Substring-Dedup — kuerzere Eintraege, die vollstaendig in
             laengeren enthalten sind, fallen weg.

  Bei Konflikt wird der Eintrag mit hoechster Salienz/Gewicht behalten.
  Original bleibt in memory_context_raw fuer Debugging.

Position im Graph:
  CharacterGraph: gv_node -> reducer -> responder

Designprinzip:
  Python-only, kein LLM-Call. Deterministisch, schnell, transparent.
  Komplexere Bewertung (Akten-basiertes Retrieval, semantische Dedup)
  bleibt dem Backlog vorbehalten.
"""

import logging
import re

from config     import REDUCER_AKTIV, REDUCER_LOG_REMOVED
from graph.state import ConversationState

logger = logging.getLogger("ki_server.reducer")


# ─────────────────────────────────────────────
# Eintrag-Parsing
# ─────────────────────────────────────────────
# Eintraege haben das Format:
#   "[QUELLE/...] (meta): inhalt"            (LZG mit Dimension)
#   "[KZG] themen (Salienz: x): inhalt"      (KZG)
#   "[Charakter] inhalt"                     (Charakter-Hash)
#   "═══ BISHERIGER GESPRAECHSVERLAUF ═══\n..." (Session-Summary)
#
# Wir splitten zeilenweise und behandeln jede nicht-leere Zeile als
# einen Kandidaten. Mehrzeilige Bloecke (z.B. Summary) werden als ein
# einzelner Block behandelt, weil sie mit einem ═══-Header eingeleitet
# werden.

_HEADER_RE = re.compile(r"^═══\s.+\s═══$")
_PRAEFIX_RE = re.compile(r"^\[([^\]]+)\]")


def _eintraege_extrahieren(memory_context: str) -> list[dict]:
    """Zerlegt den memory_context in einzelne Eintraege.

    Jeder Eintrag wird als Dict zurueckgegeben mit:
      - praefix: Quellen-Marker wie "KZG", "LZG/dimension", "Charakter"
      - inhalt: Der eigentliche Inhalt (nach dem Doppelpunkt)
      - gewicht: Numerisches Gewicht aus den Metadaten (fuer Konflikt-Aufloesung)
      - rohzeile: Originale Zeile (wird wieder eingesetzt nach Dedup)

    Mehrzeilige Bloecke (Session-Summary mit ═══-Header) bleiben
    als ein Block erhalten und werden nicht dedupliziert.
    """
    eintraege: list[dict] = []
    aktueller_block: list[str] = []
    in_block: bool = False

    for zeile in memory_context.split("\n"):
        # Erkenne ═══-Block-Header (Session-Summary)
        if _HEADER_RE.match(zeile):
            # Vorherigen Block abschliessen
            if aktueller_block:
                eintraege.append(_block_zu_eintrag("\n".join(aktueller_block)))
                aktueller_block = []
            # Neuen Block starten
            aktueller_block = [zeile]
            in_block = True
            continue

        # Im Block: Zeilen sammeln, bis naechste Quelle kommt
        if in_block:
            # Eine neue Quelle (mit [PRAEFIX]) beendet den Block
            if _PRAEFIX_RE.match(zeile):
                eintraege.append(_block_zu_eintrag("\n".join(aktueller_block)))
                aktueller_block = []
                in_block = False
                # Faellt durch zur regulaeren Verarbeitung
            else:
                aktueller_block.append(zeile)
                continue

        # Regulaerer einzeiliger Eintrag
        if zeile.strip():
            eintraege.append(_zeile_zu_eintrag(zeile))

    # Letzten Block abschliessen
    if aktueller_block:
        eintraege.append(_block_zu_eintrag("\n".join(aktueller_block)))

    return eintraege


# Pattern fuer Metadaten-Klammer am Ende eines Praefix-Headers:
#   [LZG/emotion] (Gewicht: 0.77, ...): inhalt
#   [KZG] themen (Salienz: 1.5): inhalt
# Sucht ein schliessendes ')' gefolgt von ':' (mit optionalem Whitespace).
_META_TRENNER_RE = re.compile(r"\)\s*:\s*")


def _zeile_zu_eintrag(zeile: str) -> dict:
    """Wandelt eine einzelne Zeile in einen Eintrag-Dict um.

    Inhalt-Extraktion folgt dem Format der Enricher-Quellen:
      [LZG/dim] (Gewicht: ..., ...): inhalt    -> nach '):'
      [KZG] themen (Salienz: ...): inhalt      -> nach '):'
      [Charakter] inhalt                       -> nach ']'
      [QUELLE] inhalt                          -> nach ']'

    Wir suchen primaer nach '):' (Metadaten-Klammer-Ende). Wenn nicht
    vorhanden, fallback auf das schliessende ']' des Praefix-Markers.
    """
    praefix_match = _PRAEFIX_RE.match(zeile)
    praefix: str = praefix_match.group(1) if praefix_match else ""

    # Primaer: Metadaten-Trenner '):' suchen
    meta_match = _META_TRENNER_RE.search(zeile)
    if meta_match:
        inhalt: str = zeile[meta_match.end():].strip()
    else:
        # Fallback: Alles nach dem schliessenden ']'
        bracket_pos: int = zeile.find("]")
        if bracket_pos > 0:
            inhalt = zeile[bracket_pos + 1:].strip()
        else:
            inhalt = zeile.strip()

    return {
        "praefix":  praefix,
        "inhalt":   inhalt,
        "gewicht":  _gewicht_extrahieren(zeile),
        "rohzeile": zeile,
    }


def _block_zu_eintrag(block: str) -> dict:
    """Wandelt einen mehrzeiligen Block in einen Eintrag-Dict um."""
    return {
        "praefix":  "BLOCK",
        "inhalt":   block,
        "gewicht":  0.0,
        "rohzeile": block,
    }


def _gewicht_extrahieren(zeile: str) -> float:
    """Extrahiert das Gewicht aus den Metadaten einer Zeile.

    Sucht nach 'Gewicht: x.xx', 'Salienz: x.xx' oder aehnlichen Mustern.
    Fallback: 0.0 wenn nichts gefunden.
    """
    # Salienz: x.xx
    sal_match = re.search(r"Salienz:\s*([\d.]+)", zeile)
    if sal_match:
        try:
            return float(sal_match.group(1))
        except ValueError:
            pass

    # Gewicht: x.xx
    gew_match = re.search(r"Gewicht:\s*([\d.]+)", zeile)
    if gew_match:
        try:
            return float(gew_match.group(1))
        except ValueError:
            pass

    return 0.0


def _normalisieren(inhalt: str) -> str:
    """Normalisiert einen Inhalt fuer den Vergleich.

    Klein, ohne fuehrende/trailing Whitespaces, kollabierte Mehrfach-
    Whitespaces. Keine semantische Aenderung — nur Formatierung.
    """
    return re.sub(r"\s+", " ", inhalt.lower()).strip()


# ─────────────────────────────────────────────
# Stufe 1: Exakt-Dedup
# ─────────────────────────────────────────────
def _exakt_dedup(eintraege: list[dict]) -> tuple[list[dict], list[dict]]:
    """Entfernt Eintraege mit identischem normalisiertem Inhalt.

    Bei Konflikt: behaelt den mit hoechstem Gewicht. Bei gleichem
    Gewicht: behaelt den ersten (chronologische Stabilitaet).

    Returns:
        (behaltene_eintraege, entfernte_eintraege)
    """
    gesehen: dict[str, dict] = {}
    entfernt: list[dict] = []

    for eintrag in eintraege:
        # Bloecke (Session-Summary) niemals deduplizieren — sie sind
        # einzigartig und nicht vergleichbar mit Fakten-Eintraegen.
        if eintrag["praefix"] == "BLOCK":
            schluessel: str = f"__BLOCK__{id(eintrag)}"
            gesehen[schluessel] = eintrag
            continue

        normal: str = _normalisieren(eintrag["inhalt"])
        if not normal:
            continue

        if normal in gesehen:
            vorhandener: dict = gesehen[normal]
            if eintrag["gewicht"] > vorhandener["gewicht"]:
                # Neuer Eintrag ist staerker — alten verwerfen
                entfernt.append({
                    **vorhandener,
                    "begruendung": (
                        f"exakt-dup, schwaecher als '{eintrag['praefix']}' "
                        f"(gewicht {vorhandener['gewicht']:.2f} < "
                        f"{eintrag['gewicht']:.2f})"
                    ),
                })
                gesehen[normal] = eintrag
            else:
                # Neuer Eintrag ist schwaecher (oder gleich) — verwerfen
                entfernt.append({
                    **eintrag,
                    "begruendung": (
                        f"exakt-dup, schwaecher als '{vorhandener['praefix']}' "
                        f"(gewicht {eintrag['gewicht']:.2f} <= "
                        f"{vorhandener['gewicht']:.2f})"
                    ),
                })
        else:
            gesehen[normal] = eintrag

    return list(gesehen.values()), entfernt


# ─────────────────────────────────────────────
# Stufe 2: Substring-Dedup
# ─────────────────────────────────────────────
def _substring_dedup(eintraege: list[dict]) -> tuple[list[dict], list[dict]]:
    """Entfernt kuerzere Eintraege, die vollstaendig in laengeren enthalten sind.

    Algorithmus: Sortiere absteigend nach Inhalts-Laenge. Pruefe fuer
    jeden Eintrag, ob ein bereits behaltener Eintrag ihn als Substring
    enthaelt. Wenn ja: verwerfen.

    Returns:
        (behaltene_eintraege, entfernte_eintraege)
    """
    # Bloecke ausnehmen — werden direkt durchgereicht
    bloecke: list[dict] = [e for e in eintraege if e["praefix"] == "BLOCK"]
    fakten:  list[dict] = [e for e in eintraege if e["praefix"] != "BLOCK"]

    # Absteigend nach Laenge sortieren — laengere zuerst pruefen
    fakten_sortiert: list[dict] = sorted(
        fakten,
        key=lambda e: len(_normalisieren(e["inhalt"])),
        reverse=True,
    )

    behalten: list[dict] = []
    entfernt: list[dict] = []

    for eintrag in fakten_sortiert:
        normal: str = _normalisieren(eintrag["inhalt"])
        if not normal or len(normal) < 10:
            # Sehr kurze Eintraege nicht in Substring-Dedup einbeziehen —
            # zu hohe Falsch-Positiv-Rate.
            behalten.append(eintrag)
            continue

        ist_substring: bool = False
        umfasst_durch: dict | None = None

        for kandidat in behalten:
            kandidat_normal: str = _normalisieren(kandidat["inhalt"])
            if not kandidat_normal or kandidat["praefix"] == "BLOCK":
                continue
            if normal != kandidat_normal and normal in kandidat_normal:
                ist_substring = True
                umfasst_durch = kandidat
                break

        if ist_substring and umfasst_durch is not None:
            entfernt.append({
                **eintrag,
                "begruendung": (
                    f"substring von '{umfasst_durch['praefix']}'"
                ),
            })
        else:
            behalten.append(eintrag)

    # Bloecke an den Anfang stellen (Session-Summary gehoert vorne)
    return bloecke + behalten, entfernt


# ─────────────────────────────────────────────
# Hauptfunktion
# ─────────────────────────────────────────────
def reduce(state: ConversationState) -> ConversationState:
    """Dedupliziert den memory_context.

    Master-Schalter: REDUCER_AKTIV. Wenn False, wird der Node zur No-Op.

    Schreibt:
      - state["memory_context_raw"]: Original (Backup fuer Debugging)
      - state["memory_context"]:     Deduplizierte Version
    """
    memory_context: str = state.get("memory_context", "")

    if not REDUCER_AKTIV:
        logger.info("Reducer: deaktiviert (REDUCER_AKTIV=False) — kein Eingriff")
        state["memory_context_raw"] = memory_context
        return state

    if not memory_context.strip():
        logger.info("Reducer: leerer memory_context — nichts zu tun")
        state["memory_context_raw"] = memory_context
        return state

    # Original sichern
    state["memory_context_raw"] = memory_context

    # Eintraege extrahieren
    eintraege: list[dict] = _eintraege_extrahieren(memory_context)
    anzahl_initial: int = len(eintraege)

    if anzahl_initial == 0:
        logger.info("Reducer: keine Eintraege erkannt — Original beibehalten")
        return state

    logger.info(f"Reducer: {anzahl_initial} Eintraege erkannt")

    # Diagnose-Logging: ersten paar Eintraege mit extrahiertem Inhalt zeigen.
    # Hilft, Parser-Probleme zu erkennen (z.B. Metadaten als Inhalt missdeutet).
    if REDUCER_LOG_REMOVED:
        for idx, e in enumerate(eintraege[:5]):
            inhalt_kurz: str = _normalisieren(e["inhalt"])[:100]
            logger.info(
                f"Reducer: [PARSE-{idx}] praefix='{e['praefix']}' "
                f"gewicht={e['gewicht']:.2f} inhalt='{inhalt_kurz}'"
            )

    # Stufe 1: Exakt-Dedup
    eintraege, entfernt_exakt = _exakt_dedup(eintraege)
    if entfernt_exakt and REDUCER_LOG_REMOVED:
        for e in entfernt_exakt:
            inhalt_kurz: str = e["inhalt"][:80]
            logger.info(
                f"Reducer: [EXAKT] entfernt — {e['begruendung']} — '{inhalt_kurz}'"
            )

    # Stufe 2: Substring-Dedup
    eintraege, entfernt_sub = _substring_dedup(eintraege)
    if entfernt_sub and REDUCER_LOG_REMOVED:
        for e in entfernt_sub:
            inhalt_kurz: str = e["inhalt"][:80]
            logger.info(
                f"Reducer: [SUBSTR] entfernt — {e['begruendung']} — '{inhalt_kurz}'"
            )

    # Reduzierten Kontext zurueckschreiben
    neue_zeilen: list[str] = [e["rohzeile"] for e in eintraege]
    state["memory_context"] = "\n".join(neue_zeilen)

    anzahl_final:    int = len(eintraege)
    anzahl_entfernt: int = len(entfernt_exakt) + len(entfernt_sub)

    logger.info(
        f"Reducer: Fertig — {anzahl_initial} -> {anzahl_final} Eintraege "
        f"({anzahl_entfernt} entfernt: {len(entfernt_exakt)} exakt, "
        f"{len(entfernt_sub)} substring)"
    )

    return state
