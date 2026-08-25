"""CRUD-Nodes -- Erstellen, Aktualisieren, Loeschen, Reaktivieren von Direktiven.

Erweitert in Chat 44 (Epic 15): normalisiert-Feld aus Classify im Debug-Log.
Erweitert in Chat 42 (CRUD-Haertung):
- reactivate-Aktion
- Vorher/Nachher-Snapshot fuer Verifikation
- Validierung gegen DB-Zustand vor Ausfuehrung
- Verifikation nach Ausfuehrung
"""

import logging

from agents.base import AgentState
from agents.crud_validation import ValidationResult
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.direktiven.crud")


# ============================================================
# Lese-Funktionen (auch von klassifikation.py genutzt)
# ============================================================

def _read_aktive(user_id: str) -> list[dict]:
    """Liest alle aktiven Direktiven."""
    return db_manager.select(
        "SELECT id, anweisung, kontext, erstellt_am FROM direktiven "
        "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
        (user_id,),
    )


def _read_inaktive(user_id: str) -> list[dict]:
    """Liest alle inaktiven Direktiven (fuer reactivate)."""
    return db_manager.select(
        "SELECT id, anweisung, kontext, erstellt_am, geaendert_am FROM direktiven "
        "WHERE user_id = %s AND aktiv = FALSE ORDER BY geaendert_am DESC LIMIT 10",
        (user_id,),
    )


def _read_by_id(direktive_id: int) -> dict | None:
    """Liest eine einzelne Direktive per ID."""
    return db_manager.select_one(
        "SELECT id, anweisung, kontext, aktiv, erstellt_am, geaendert_am FROM direktiven WHERE id = %s",
        (direktive_id,),
    )


def _suche_by_keyword(user_id: str, keyword: str) -> list[dict]:
    """ILIKE-Suche in anweisung fuer delete/update Target-Aufloesung."""
    return db_manager.select(
        "SELECT id, anweisung, kontext FROM direktiven "
        "WHERE user_id = %s AND aktiv = TRUE AND anweisung ILIKE %s "
        "ORDER BY erstellt_am DESC LIMIT 5",
        (user_id, f"%{keyword}%"),
    )


def _suche_inaktive_by_keyword(user_id: str, keyword: str) -> list[dict]:
    """ILIKE-Suche in inaktiven Direktiven fuer reactivate."""
    return db_manager.select(
        "SELECT id, anweisung, kontext FROM direktiven "
        "WHERE user_id = %s AND aktiv = FALSE AND anweisung ILIKE %s "
        "ORDER BY geaendert_am DESC LIMIT 5",
        (user_id, f"%{keyword}%"),
    )


# ============================================================
# Validierung (Phase 2: Python gegen DB-Zustand)
# ============================================================

def validieren_gegen_db(state: AgentState) -> ValidationResult:
    """Prueft die klassifizierte Aktion gegen den aktuellen DB-Zustand."""
    action = state["parameter"].get("action", "")
    user_id = state["kontext"].get("user_id", "")
    anweisung = state["parameter"].get("anweisung", "")
    target_id = state["parameter"].get("target_id")

    # --- create: Duplikat-Check ---
    if action == "create":
        aktive = _read_aktive(user_id)
        for d in aktive:
            if anweisung.lower().strip() in d["anweisung"].lower() or d["anweisung"].lower() in anweisung.lower().strip():
                return ValidationResult(
                    ok=False,
                    grund=f"Aehnliche Direktive existiert bereits: [{d['id']}] {d['anweisung']}",
                    bestaetigung_noetig=True,
                    bestaetigung_text=f"Eine aehnliche Direktive existiert bereits: '{d['anweisung']}'. Trotzdem anlegen?",
                )

        # Pruefen ob inaktive Version existiert → Auto-Korrektur zu reactivate
        inaktive = _suche_inaktive_by_keyword(user_id, anweisung)
        if inaktive:
            return ValidationResult(
                ok=True,
                korrektur="reactivate",
                grund=f"Inaktive Direktive gefunden: [{inaktive[0]['id']}] {inaktive[0]['anweisung']} — auto-korrigiert zu reactivate",
                bestaetigung_noetig=True,
                bestaetigung_text=f"Es gibt eine frueher geloeschte Direktive: '{inaktive[0]['anweisung']}'. Soll ich die wiederherstellen statt eine neue anzulegen?",
            )

    # --- delete: Target existiert? ---
    if action == "delete":
        if target_id:
            eintrag = _read_by_id(target_id)
            if not eintrag or not eintrag.get("aktiv"):
                return ValidationResult(ok=False, grund=f"Direktive ID {target_id} nicht gefunden oder bereits inaktiv")

    # --- reactivate: Inaktiver Eintrag existiert? ---
    if action == "reactivate":
        if target_id:
            eintrag = _read_by_id(target_id)
            if not eintrag:
                return ValidationResult(ok=False, grund=f"Direktive ID {target_id} nicht gefunden")
            if eintrag.get("aktiv"):
                return ValidationResult(ok=False, grund=f"Direktive ID {target_id} ist bereits aktiv")
        else:
            treffer = _suche_inaktive_by_keyword(user_id, anweisung)
            if not treffer:
                return ValidationResult(ok=False, grund=f"Keine inaktive Direktive gefunden die zu '{anweisung}' passt")
            if len(treffer) > 1:
                zeilen = [f"  [{t['id']}] {t['anweisung']}" for t in treffer]
                return ValidationResult(
                    ok=False,
                    grund="Mehrere inaktive Direktiven passen",
                    bestaetigung_noetig=True,
                    bestaetigung_text="Mehrere geloeschte Direktiven passen:\n" + "\n".join(zeilen) + "\nWelche soll ich wiederherstellen?",
                )

    # --- Pflicht-Rueckfrage fuer alle Schreiboperationen ---
    if action in ("create", "delete", "update", "reactivate"):
        beschreibung = {
            "create": f"Neue Direktive anlegen: '{anweisung}'",
            "delete": f"Direktive loeschen (ID {target_id})",
            "update": f"Direktive aendern (ID {target_id}): '{anweisung}'",
            "reactivate": f"Direktive wiederherstellen (ID {target_id})",
        }
        return ValidationResult(
            ok=True,
            grund="Pflicht-Rueckfrage fuer Direktiven-Schreiboperation",
            bestaetigung_noetig=True,
            bestaetigung_text=f"Soll ich das ausfuehren? {beschreibung.get(action, action)}",
        )

    # read → immer ok, keine Rueckfrage
    return ValidationResult(ok=True, grund="Leseoperation")


# ============================================================
# Verifikation (Phase 4: DB-Read nach Write)
# ============================================================

def _verifizieren(action: str, target_id: int | None, erwartung: dict) -> bool:
    """Prueft ob die DB-Operation den erwarteten Effekt hatte."""
    if not target_id:
        return True

    eintrag = _read_by_id(target_id)
    if not eintrag:
        logger.error(f"Verifikation: Eintrag ID {target_id} nicht gefunden nach {action}")
        return False

    if action == "delete" and eintrag.get("aktiv"):
        logger.error(f"Verifikation: Eintrag ID {target_id} ist noch aktiv nach delete")
        return False

    if action == "reactivate" and not eintrag.get("aktiv"):
        logger.error(f"Verifikation: Eintrag ID {target_id} ist noch inaktiv nach reactivate")
        return False

    if action == "create" and not eintrag.get("aktiv"):
        logger.error(f"Verifikation: Neuer Eintrag ID {target_id} ist nicht aktiv nach create")
        return False

    return True


# ============================================================
# CRUD-Operationen (mit Vorher/Nachher-Snapshot)
# ============================================================

def ausfuehren(state: AgentState) -> dict:
    """Fuehrt die CRUD-Operation aus."""
    action = state["parameter"].get("action", "")
    normalisiert = state["parameter"].get("normalisiert", "")
    logger.debug(f"ausfuehren: Einstieg -- action='{action}', normalisiert='{normalisiert}'")

    if action == "create":
        return _create(state)
    elif action == "read":
        return _read(state)
    elif action == "update":
        return _update(state)
    elif action == "delete":
        return _delete(state)
    elif action == "reactivate":
        return _reactivate(state)

    return {
        "status": "fehler",
        "fehler": f"Unbehandelte Aktion: {action}",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "unbehandelt"}],
    }


def _create(state: AgentState) -> dict:
    """Neue Direktive anlegen."""
    user_id = state["kontext"].get("user_id", "")
    anweisung = state["parameter"].get("anweisung", "")
    kontext = state["parameter"].get("kontext") or None

    if not anweisung:
        return {
            "status": "fehler",
            "fehler": "Keine Anweisung angegeben",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_anweisung"}],
        }

    result = db_manager.execute_returning(
        "INSERT INTO direktiven (user_id, anweisung, kontext) VALUES (%s, %s, %s) RETURNING id",
        (user_id, anweisung, kontext),
    )
    direktive_id = result["id"] if result else None

    verifiziert = _verifizieren("create", direktive_id, {"aktiv": True})

    logger.info(f"DirektivenAgent: Direktive erstellt (ID {direktive_id}), verifiziert={verifiziert}: '{anweisung[:80]}'")

    kontext_info = f" (Kontext: {kontext})" if kontext else ""
    return {
        "ergebnis": f"Direktive gespeichert: {anweisung}{kontext_info}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "erstellt", "id": direktive_id, "verifiziert": verifiziert}],
    }


def _read(state: AgentState) -> dict:
    """Alle aktiven Direktiven auflisten."""
    user_id = state["kontext"].get("user_id", "")
    aktive = _read_aktive(user_id)

    if not aktive:
        return {
            "ergebnis": "Keine aktiven Direktiven vorhanden.",
            "status": "abgeschlossen",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "leer"}],
        }

    zeilen = []
    for d in aktive:
        zeile = f"- [{d['id']}] {d['anweisung']}"
        if d.get("kontext"):
            zeile += f" ({d['kontext']})"
        zeilen.append(zeile)

    text = "Aktive Direktiven:\n" + "\n".join(zeilen)

    return {
        "ergebnis": text,
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "gelesen", "anzahl": len(aktive)}],
    }


def _update(state: AgentState) -> dict:
    """Direktive aktualisieren: Alte deaktivieren, neue anlegen."""
    user_id = state["kontext"].get("user_id", "")
    target_id = state["parameter"].get("target_id")
    neue_anweisung = state["parameter"].get("anweisung", "")
    neuer_kontext = state["parameter"].get("kontext")

    if not target_id:
        return {
            "status": "fehler",
            "fehler": "Keine target_id fuer Update angegeben",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
        }

    if not neue_anweisung:
        return {
            "status": "fehler",
            "fehler": "Keine neue Anweisung angegeben",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_anweisung"}],
        }

    vorher = _read_by_id(target_id)

    db_manager.execute(
        "UPDATE direktiven SET aktiv = FALSE, geaendert_am = NOW() WHERE id = %s",
        (target_id,),
    )

    result = db_manager.execute_returning(
        "INSERT INTO direktiven (user_id, anweisung, kontext) VALUES (%s, %s, %s) RETURNING id",
        (user_id, neue_anweisung, neuer_kontext),
    )
    neue_id = result["id"] if result else None

    verifiziert_alt = _verifizieren("delete", target_id, {"aktiv": False})
    verifiziert_neu = _verifizieren("create", neue_id, {"aktiv": True})
    verifiziert = verifiziert_alt and verifiziert_neu

    logger.info(f"DirektivenAgent: Direktive {target_id} -> {neue_id} aktualisiert, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Direktive aktualisiert: {neue_anweisung}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "aktualisiert", "alte_id": target_id, "neue_id": neue_id, "verifiziert": verifiziert}],
    }


def _delete(state: AgentState) -> dict:
    """Direktive deaktivieren (Soft-Delete)."""
    user_id = state["kontext"].get("user_id", "")
    target_id = state["parameter"].get("target_id")

    if not target_id:
        keyword = state["parameter"].get("anweisung", "")
        if keyword:
            treffer = _suche_by_keyword(user_id, keyword)
            if len(treffer) == 1:
                target_id = treffer[0]["id"]
            elif len(treffer) > 1:
                zeilen = [f"  [{t['id']}] {t['anweisung']}" for t in treffer]
                return {
                    "status": "rueckfrage",
                    "rueckfrage": "Mehrere Direktiven passen:\n" + "\n".join(zeilen) + "\n\nWelche soll ich entfernen?",
                    "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "disambiguierung"}],
                }
            else:
                return {
                    "status": "fehler",
                    "fehler": f"Keine Direktive gefunden die zu '{keyword}' passt",
                    "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "nicht_gefunden"}],
                }
        else:
            return {
                "status": "fehler",
                "fehler": "Keine target_id und kein Keyword zum Loeschen",
                "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
            }

    vorher = _read_by_id(target_id)

    db_manager.execute(
        "UPDATE direktiven SET aktiv = FALSE, geaendert_am = NOW() WHERE id = %s",
        (target_id,),
    )

    verifiziert = _verifizieren("delete", target_id, {"aktiv": False})

    logger.info(f"DirektivenAgent: Direktive {target_id} deaktiviert, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Direktive (ID {target_id}) entfernt.",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "geloescht", "id": target_id, "verifiziert": verifiziert}],
    }


def _reactivate(state: AgentState) -> dict:
    """Inaktive Direktive wieder aktivieren."""
    user_id = state["kontext"].get("user_id", "")
    target_id = state["parameter"].get("target_id")

    if not target_id:
        keyword = state["parameter"].get("anweisung", "")
        if keyword:
            treffer = _suche_inaktive_by_keyword(user_id, keyword)
            if len(treffer) == 1:
                target_id = treffer[0]["id"]
            elif len(treffer) > 1:
                zeilen = [f"  [{t['id']}] {t['anweisung']}" for t in treffer]
                return {
                    "status": "rueckfrage",
                    "rueckfrage": "Mehrere geloeschte Direktiven passen:\n" + "\n".join(zeilen) + "\n\nWelche soll ich wiederherstellen?",
                    "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "disambiguierung"}],
                }
            else:
                return {
                    "status": "fehler",
                    "fehler": f"Keine inaktive Direktive gefunden die zu '{keyword}' passt",
                    "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "nicht_gefunden"}],
                }
        else:
            return {
                "status": "fehler",
                "fehler": "Keine target_id und kein Keyword zum Reaktivieren",
                "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
            }

    vorher = _read_by_id(target_id)

    db_manager.execute(
        "UPDATE direktiven SET aktiv = TRUE, geaendert_am = NOW() WHERE id = %s",
        (target_id,),
    )

    verifiziert = _verifizieren("reactivate", target_id, {"aktiv": True})

    nachher = _read_by_id(target_id)
    logger.info(f"DirektivenAgent: Direktive {target_id} reaktiviert, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Direktive wiederhergestellt: {nachher['anweisung'] if nachher else '?'}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "reaktiviert", "id": target_id, "verifiziert": verifiziert}],
    }
