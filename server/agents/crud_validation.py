"""Gemeinsame CRUD-Validierungsinfrastruktur fuer alle Agenten.

Stellt Datenklassen, Keyword-Hints und Verb-Mapping-Logik bereit.
Konzept: nova-14-k.md (Chat 42).
"""

import re
import logging
from dataclasses import dataclass, field

from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.crud_validation")


# ============================================================
# Datenklassen
# ============================================================

@dataclass
class KlassifikationsErgebnis:
    """Output des Classify-Node nach Keyword-Hints + LLM."""
    aktion: str
    target: str | None = None
    slots: dict = field(default_factory=dict)
    keyword_hints: list[str] = field(default_factory=list)
    konfidenz: str = "niedrig"


@dataclass
class ValidationResult:
    """Ergebnis der Validierung gegen DB-Zustand."""
    ok: bool
    korrektur: str | None = None
    grund: str = ""
    bestaetigung_noetig: bool = False
    bestaetigung_text: str | None = None


@dataclass
class CrudErgebnis:
    """Ergebnis einer CRUD-Operation mit Vorher/Nachher-Snapshot."""
    erfolg: bool
    aktion: str
    vorher: dict | None = None
    nachher: dict | None = None
    verifiziert: bool = False
    meldung: str = ""


# ============================================================
# Statische Keyword-Hints
# ============================================================

KEYWORD_HINTS: dict[str, str] = {
    r"wiederherstellen|wieder\s*her|reaktivieren|zurueckholen|zurueck\s*holen": "reactivate",
    r"rueckgaengig|undo|zuruecknehmen|zurueck\s*nehmen": "reactivate",
    r"loesch|lösch|entfern|weg\s+damit": "delete",
    r"fuege.*hinzu|füge.*hinzu|hinzufuegen|hinzufügen|aufnehmen|nimm.*auf|ergaenz|ergänz": "add_content",
    r"streich|nimm.*raus|entferne.*von|runter\s+von": "remove_content",
    r"leere|alles\s+loeschen|alles\s+löschen|komplett\s+leeren": "clear_content",
    r"aender|änder|aktualisier|korrigier": "update",
    r"verschieb|verleg": "reschedule",
    r"zeig|was\s+hast|welche|liste|auflisten|aufzaehlen|aufzählen": "read",
    r"erstell|anlegen|leg.*an|mach.*neu|neu.*anlegen": "create",
}


def keyword_hints_ermitteln(text: str) -> list[str]:
    """Gibt passende Hint-Aktionen zurueck (koennen mehrere sein)."""
    hints: list[str] = []
    for pattern, aktion in KEYWORD_HINTS.items():
        if re.search(pattern, text, re.IGNORECASE):
            if aktion not in hints:
                hints.append(aktion)
    return hints


# ============================================================
# Lernende Verb-Mappings (PostgreSQL)
# ============================================================

def verb_mappings_laden(user_id: str, agent: str) -> list[dict]:
    """Laedt gelernte Verb-Mappings fuer einen User+Agent."""
    return db_manager.select(
        "SELECT ausdruck, aktion, konfidenz FROM verb_mappings "
        "WHERE user_id = %s AND agent = %s ORDER BY konfidenz DESC",
        (user_id, agent),
    )


def verb_mapping_pruefen(text: str, user_id: str, agent: str) -> list[str]:
    """Prueft ob gelernte Ausdruecke im Text vorkommen. Gibt Hint-Aktionen zurueck."""
    mappings = verb_mappings_laden(user_id, agent)
    hints: list[str] = []
    text_lower = text.lower()
    for m in mappings:
        if m["ausdruck"].lower() in text_lower:
            if m["aktion"] not in hints:
                hints.append(m["aktion"])
    return hints


def verb_mapping_lernen(user_id: str, agent: str, ausdruck: str, aktion: str) -> None:
    """Speichert oder verstaerkt ein Verb-Mapping."""
    existing = db_manager.select_one(
        "SELECT id, konfidenz FROM verb_mappings "
        "WHERE user_id = %s AND ausdruck = %s AND agent = %s",
        (user_id, ausdruck, agent),
    )
    if existing:
        db_manager.execute(
            "UPDATE verb_mappings SET konfidenz = konfidenz + 1 WHERE id = %s",
            (existing["id"],),
        )
        logger.info(f"verb_mapping: Verstaerkt '{ausdruck}' → {aktion} (konfidenz={existing['konfidenz'] + 1})")
    else:
        db_manager.execute(
            "INSERT INTO verb_mappings (user_id, ausdruck, aktion, agent) VALUES (%s, %s, %s, %s)",
            (user_id, ausdruck, aktion, agent),
        )
        logger.info(f"verb_mapping: Neu gelernt '{ausdruck}' → {aktion}")


# ============================================================
# Konfidenz-Berechnung
# ============================================================

KONFIDENZ_SCHWELLE_GELERNT: int = 3


def konfidenz_berechnen(
    llm_aktion: str,
    keyword_hints: list[str],
    verb_mapping_hints: list[str],
    verb_mappings_raw: list[dict] | None = None,
) -> str:
    """
    Berechnet die Konfidenz der Klassifikation.

    Returns: "hoch", "mittel", "niedrig", "konflikt"
    """
    alle_hints = keyword_hints + verb_mapping_hints

    if not alle_hints:
        return "niedrig"

    if llm_aktion in alle_hints:
        if verb_mappings_raw:
            for m in verb_mappings_raw:
                if m["aktion"] == llm_aktion and m["konfidenz"] >= KONFIDENZ_SCHWELLE_GELERNT:
                    return "hoch"
        if llm_aktion in keyword_hints:
            return "hoch"
        return "mittel"

    return "konflikt"


# ============================================================
# Erkennungshilfe-Block fuer den Classify-Prompt
# ============================================================

def erkennungshilfe_block(
    keyword_hints: list[str],
    verb_mapping_hints: list[str],
    verb_mappings_raw: list[dict] | None = None,
) -> str | None:
    """Baut den [ERKENNUNGSHILFE]-Block fuer den Classify-Prompt. Gibt None zurueck wenn leer."""
    zeilen: list[str] = []

    for hint in keyword_hints:
        zeilen.append(f"- {hint} (Schluesselwort erkannt)")

    if verb_mappings_raw:
        for m in verb_mappings_raw:
            if m["aktion"] in verb_mapping_hints:
                zeilen.append(f"- {m['aktion']} (Gelernt: \"{m['ausdruck']}\", Konfidenz: {m['konfidenz']})")

    if not zeilen:
        return None

    return (
        "[ERKENNUNGSHILFE]\n"
        "Schluesselwoerter und gelernte Ausdruecke im Text deuten auf folgende Aktionen:\n"
        + "\n".join(zeilen)
        + "\nDiese Hinweise sind NICHT bindend, aber beruecksichtige sie."
    )
