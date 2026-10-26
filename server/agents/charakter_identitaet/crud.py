"""CRUD-Nodes -- Erstellen, Aktualisieren, Loeschen, Reaktivieren von Charakter-Anweisungen.

Erweitert in Chat 44 (Epic 15): normalisiert-Feld aus Classify im Debug-Log.
Erweitert in Chat 42 (CRUD-Haertung):
- reactivate- und replace-Aktion
- Vorher/Nachher-Snapshot fuer Verifikation
- Validierung gegen DB-Zustand vor Ausfuehrung
- Verifikation nach Ausfuehrung
"""

import logging

from agents.base import AgentState
from agents.crud_validation import ValidationResult
from agents.write_outcome import verified_outcome
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.charakter_identitaet.crud")


def _previous_state_trace(vorher: dict | None) -> dict:
    """Der ersetzte Inhalt als Eingangsgroesse der Entscheidung.

    Der Datensatz wird vor jedem Schreibvorgang gelesen; ohne diesen Eintrag
    laege er nur im Arbeitsspeicher und waere nach dem UPDATE nicht mehr
    rekonstruierbar. `18_NACHVOLLZIEHBARKEIT` verlangt die Eingangsgroessen
    einzeln, nicht nur das Ergebnis.

    Fehlt der Datensatz, sagt die Spur das ausdruecklich: `gelesen=False`. Ein
    leerer String saehe aus wie eine leere Anweisung und waere ein Default, der
    wie ein Messwert aussieht.
    """
    if vorher is None:
        return {"gelesen": False}
    return {
        "gelesen":   True,
        "anweisung": vorher.get("anweisung", ""),
    }


# ============================================================
# Lese-Funktionen (auch von klassifikation.py genutzt)
# ============================================================

def _count_aktive(user_id: str) -> int:
    """Zaehlt aktive Charakter-Anweisungen."""
    row = db_manager.select_one(
        "SELECT COUNT(*) AS cnt FROM charakter_anweisungen WHERE user_id = %s AND aktiv = TRUE",
        (user_id,),
    )
    return row["cnt"] if row else 0


def _read_aktive(user_id: str) -> list[dict]:
    """Liest alle aktiven Charakter-Anweisungen."""
    return db_manager.select(
        "SELECT id, anweisung, erstellt_am FROM charakter_anweisungen "
        "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
        (user_id,),
    )


def _read_inaktive(user_id: str) -> list[dict]:
    """Liest alle inaktiven Charakter-Anweisungen (fuer reactivate)."""
    return db_manager.select(
        "SELECT id, anweisung, erstellt_am, geaendert_am FROM charakter_anweisungen "
        "WHERE user_id = %s AND aktiv = FALSE ORDER BY geaendert_am DESC LIMIT 10",
        (user_id,),
    )


def _read_by_id(anweisung_id: int, user_id: str) -> dict | None:
    """Liest eine einzelne Charakter-Anweisung per ID — nur eine Zeile dieses Menschen.

    Die Kennung kann aus einer Modellausgabe stammen; ohne `user_id` in der
    Bedingung traefe eine falsche Zahl die Anweisung eines anderen Menschen.
    Vorbedingung: `anweisung_id` ist eine Ganzzahl, `user_id` die des Menschen.
    Nachbedingung: Die Zeile, wenn sie diesem Menschen gehoert, sonst `None`.
    """
    return db_manager.select_one(
        "SELECT id, anweisung, aktiv, erstellt_am, geaendert_am FROM charakter_anweisungen "
        "WHERE id = %s AND user_id = %s",
        (anweisung_id, user_id),
    )


def _ist_kennung(target_id: object) -> bool:
    """Ist `target_id` eine Kennung, die an SQL gehen darf?

    Vorbedingung: keine — `target_id` darf beliebigen Typs sein.
    Nachbedingung: `True` nur fuer eine Ganzzahl > 0; `bool` ist eine
    Unterklasse von `int` und zaehlt nicht (`True` waere sonst Zeile 1).
    """
    return isinstance(target_id, int) and not isinstance(target_id, bool) and target_id > 0


def _ziel_pruefen(target_id: object, user_id: str, aktiv_erwartet: bool) -> str | None:
    """Prueft, ob die Kennung zu einer Zeile dieses Menschen gehoert, die die Aktion treffen kann.

    Vorbedingung: `target_id` ist nicht `None`.
    Nachbedingung: `None`, wenn eine Zeile dieses Menschen mit `aktiv ==
    aktiv_erwartet` dasteht; sonst der Grund, laut geloggt. Eine fremde und
    eine fehlende Zeile tragen denselben Grund — die Antwort verraet nicht,
    dass es die Kennung bei einem anderen Menschen gibt.
    Fehlerfaelle: keine Kennung (falscher Typ), keine Zeile, falscher Zustand.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not _ist_kennung(target_id):
        grund: str = f"Charakter-Anweisung: target_id {target_id!r} ist keine Kennung"
        logger.error(f"validieren_gegen_db: {grund}")
        return grund

    # ── Verarbeitung ────────────────────────────
    eintrag: dict | None = _read_by_id(target_id, user_id)

    # ── Ausgabe-Verifikation ────────────────────
    if not eintrag:
        grund = f"Charakter-Anweisung ID {target_id} nicht gefunden"
    elif bool(eintrag.get("aktiv")) != aktiv_erwartet:
        grund = f"Charakter-Anweisung ID {target_id} ist " + (
            "bereits inaktiv" if aktiv_erwartet else "bereits aktiv"
        )
    else:
        return None
    logger.error(f"validieren_gegen_db: {grund} (user_id='{user_id}')")
    return grund


# ============================================================
# Validierung (Phase 2: Python gegen DB-Zustand)
# ============================================================

def validieren_gegen_db(state: AgentState) -> ValidationResult:
    """Prueft die klassifizierte Aktion gegen den aktuellen DB-Zustand."""
    action = state["parameter"].get("action", "")
    user_id = state["kontext"].get("user_id", "")
    anweisung = state["parameter"].get("anweisung", "")
    target_id = state["parameter"].get("target_id")

    # --- delete/update/reactivate: Die Kennung gehoert diesem Menschen ---
    # Aktiv fuer delete und update, inaktiv fuer reactivate. Ohne Kennung
    # (`None`) bleiben die Wege wie bisher (Stichwort, bei delete: alle).
    if action in ("delete", "update", "reactivate") and target_id is not None:
        grund_ziel: str | None = _ziel_pruefen(
            target_id, user_id, aktiv_erwartet=action != "reactivate"
        )
        if grund_ziel:
            return ValidationResult(ok=False, grund=grund_ziel)

    # --- reactivate ohne Kennung: Inaktiver Eintrag per Stichwort ---
    if action == "reactivate":
        if target_id is None:
            inaktive = _read_inaktive(user_id)
            treffer = (
                [
                    a
                    for a in inaktive
                    if anweisung.lower() in a["anweisung"].lower()
                    or a["anweisung"].lower() in anweisung.lower()
                ]
                if anweisung
                else inaktive
            )
            if not treffer:
                return ValidationResult(
                    ok=False, grund="Keine inaktive Charakter-Anweisung gefunden"
                )
            if len(treffer) > 1:
                zeilen = [f"  [{a['id']}] {a['anweisung']}" for a in treffer]
                return ValidationResult(
                    ok=False,
                    grund="Mehrere inaktive Anweisungen passen",
                    bestaetigung_noetig=True,
                    bestaetigung_text="Mehrere fruehere Charakter-Anweisungen gefunden:\n"
                    + "\n".join(zeilen)
                    + "\nWelche soll ich wiederherstellen?",
                )

    # --- create: Pruefen ob inaktive Version existiert → Auto-Korrektur ---
    if action == "create" and anweisung:
        inaktive = _read_inaktive(user_id)
        for a in inaktive:
            if (
                anweisung.lower().strip() in a["anweisung"].lower()
                or a["anweisung"].lower() in anweisung.lower().strip()
            ):
                return ValidationResult(
                    ok=True,
                    korrektur="reactivate",
                    grund=f"Inaktive Anweisung gefunden: [{a['id']}] {a['anweisung']} — auto-korrigiert zu reactivate",
                    bestaetigung_noetig=True,
                    bestaetigung_text=f"Es gibt eine fruehere Charakter-Anweisung: '{a['anweisung']}'. Soll ich die wiederherstellen statt eine neue anzulegen?",
                )

    # --- Pflicht-Rueckfrage fuer alle Schreiboperationen ---
    if action in ("create", "delete", "update", "reactivate", "replace", "konsolidieren"):
        beschreibung = {
            "create": f"Neue Charakter-Anweisung anlegen: '{anweisung}'",
            "delete": "Charakter-Anweisung loeschen"
            + (f" (ID {target_id})" if target_id else " (alle)"),
            "update": f"Charakter-Anweisung aendern (ID {target_id}): '{anweisung}'",
            "reactivate": "Charakter-Anweisung wiederherstellen",
            "replace": f"Charakter komplett ersetzen durch: '{anweisung}'",
            "konsolidieren": "Charakter-Anweisungen zusammenfassen",
        }
        return ValidationResult(
            ok=True,
            grund="Pflicht-Rueckfrage fuer Charakter-Schreiboperation",
            bestaetigung_noetig=True,
            bestaetigung_text=f"Soll ich das ausfuehren? {beschreibung.get(action, action)}",
        )

    # read → immer ok
    return ValidationResult(ok=True, grund="Leseoperation")


# ============================================================
# Verifikation (Phase 4: DB-Read nach Write)
# ============================================================

def _verifizieren(action: str, target_id: int | None, user_id: str, erwartung: dict) -> bool:
    """Prueft ob die DB-Operation den erwarteten Effekt hatte — an der Zeile dieses Menschen."""
    if not target_id:
        return True

    eintrag = _read_by_id(target_id, user_id)
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
# CRUD-Operationen
# ============================================================

def _zustand_setzen(target_id: int, user_id: str, aktiv: bool) -> int:
    """Setzt `aktiv` einer Charakter-Anweisung — nur an der Zeile dieses Menschen.

    Vorbedingung: `target_id` ist eine Kennung (`_ist_kennung`), `user_id` nicht leer.
    Nachbedingung: Die Zahl der getroffenen Zeilen (`0` bei einer fremden oder
    fehlenden Kennung — die Bedingung traegt die `user_id`).
    Fehlerfaelle: Eine verletzte Vorbedingung ist ein Programmierfehler des
    Aufrufers und wirft `ValueError`, bevor etwas geschrieben wird; eine
    Rueckgabe, die keine Zeilenzahl ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not _ist_kennung(target_id) or not user_id:
        msg: str = f"_zustand_setzen: Kennung {target_id!r} / user_id {user_id!r} unbrauchbar"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    sql: str = (
        "UPDATE charakter_anweisungen SET aktiv = TRUE, geaendert_am = NOW() "
        "WHERE id = %s AND user_id = %s"
        if aktiv else
        "UPDATE charakter_anweisungen SET aktiv = FALSE, geaendert_am = NOW() "
        "WHERE id = %s AND user_id = %s"
    )
    betroffen: object = db_manager.execute(sql, (target_id, user_id))

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(betroffen, int) or isinstance(betroffen, bool) or betroffen < 0:
        msg = f"_zustand_setzen: execute lieferte keine Zeilenzahl: {betroffen!r}"
        raise TypeError(msg)
    return betroffen


def _keine_zeile_getroffen(
    state: AgentState, target_id: int, user_id: str, betroffen: int
) -> dict:
    """Der laute Ausgang eines Schreibwegs, der nicht genau eine Zeile dieses Menschen traf.

    Vorbedingung: `betroffen` ist die Rueckgabe von `_zustand_setzen` und nicht 1.
    Nachbedingung: Status `fehler` mit Grund, geloggt; kein Erfolgssatz.
    Fehlerfaelle: `betroffen == 1` ist ein Programmierfehler des Aufrufers
    (`ValueError`) — ein Erfolg darf nicht als Fehler gemeldet werden.
    """
    # ── Eingabe-Validierung ─────────────────────
    if betroffen == 1:
        msg: str = "_keine_zeile_getroffen: genau eine Zeile getroffen — kein Fehlerfall"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    grund: str = f"Charakter-Anweisung ID {target_id}: {betroffen} Zeilen getroffen statt einer"
    logger.error(f"ausfuehren: {grund} (user_id='{user_id}') — nichts geschrieben")
    return {
        "status": "fehler",
        "fehler": grund,
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_zeile"}],
    }


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
    elif action == "delete_alle":
        return _delete_alle(state)
    elif action == "reactivate":
        return _reactivate(state)
    elif action == "replace":
        return _replace(state)
    elif action == "konsolidieren":
        return _konsolidieren(state)

    return {
        "status": "fehler",
        "fehler": f"Unbehandelte Aktion: {action}",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "unbehandelt"}],
    }


def _create(state: AgentState) -> dict:
    """Neue Charakter-Anweisung anlegen."""
    user_id = state["kontext"].get("user_id", "")
    anweisung = state["parameter"].get("anweisung", "")

    if not anweisung:
        return {
            "status": "fehler",
            "fehler": "Keine Anweisung angegeben",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_anweisung"}],
        }

    result = db_manager.execute_returning(
        "INSERT INTO charakter_anweisungen (user_id, anweisung) VALUES (%s, %s) RETURNING id",
        (user_id, anweisung),
    )
    anweisung_id = result["id"] if result else None

    verifiziert = _verifizieren("create", anweisung_id, user_id, {"aktiv": True})
    logger.info(
        f"CharakterAgent: Anweisung erstellt (ID {anweisung_id}), verifiziert={verifiziert}: "
        f"'{anweisung[:80]}'"
    )

    return verified_outcome({
        "ergebnis": f"Charakter-Anweisung gespeichert: {anweisung}",
        "status": "abgeschlossen",
        "schritte": state["schritte"]
        + [
            {
                "node": "ausfuehren",
                "ergebnis": "erstellt",
                "id": anweisung_id,
                "verifiziert": verifiziert,
            }
        ],
    }, verifiziert)


def _read(state: AgentState) -> dict:
    """Alle aktiven Charakter-Anweisungen auflisten."""
    user_id = state["kontext"].get("user_id", "")
    aktive = _read_aktive(user_id)

    if not aktive:
        return {
            "ergebnis": "Keine aktiven Charakter-Anweisungen vorhanden.",
            "status": "abgeschlossen",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "leer"}],
        }

    zeilen = [f"- [{a['id']}] {a['anweisung']}" for a in aktive]
    text = "Aktive Charakter-Anweisungen:\n" + "\n".join(zeilen)

    return {
        "ergebnis": text,
        "status": "abgeschlossen",
        "schritte": state["schritte"]
        + [{"node": "ausfuehren", "ergebnis": "gelesen", "anzahl": len(aktive)}],
    }


def _update(state: AgentState) -> dict:
    """Charakter-Anweisung aktualisieren: Alten deaktivieren, neuen anlegen."""
    user_id = state["kontext"].get("user_id", "")
    target_id = state["parameter"].get("target_id")
    neue_anweisung = state["parameter"].get("anweisung", "")

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

    vorher = _read_by_id(target_id, user_id)

    # Traf die Deaktivierung keine Zeile dieses Menschen, wird auch nichts
    # angelegt — sonst stuende eine neue Anweisung neben einer unveraenderten.
    betroffen: int = _zustand_setzen(target_id, user_id, aktiv=False)
    if betroffen != 1:
        return _keine_zeile_getroffen(state, target_id, user_id, betroffen)

    result = db_manager.execute_returning(
        "INSERT INTO charakter_anweisungen (user_id, anweisung) VALUES (%s, %s) RETURNING id",
        (user_id, neue_anweisung),
    )
    neue_id = result["id"] if result else None

    verifiziert_alt = _verifizieren("delete", target_id, user_id, {"aktiv": False})
    verifiziert_neu = _verifizieren("create", neue_id, user_id, {"aktiv": True})
    verifiziert = verifiziert_alt and verifiziert_neu

    logger.info(
        f"CharakterAgent: Anweisung {target_id} -> {neue_id} aktualisiert, "
        f"verifiziert={verifiziert}"
    )

    return verified_outcome({
        "ergebnis": f"Charakter-Anweisung aktualisiert: {neue_anweisung}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren",
            "ergebnis": "aktualisiert",
            "alte_id": target_id,
            "neue_id": neue_id,
            "verifiziert": verifiziert,
            "vorher": _previous_state_trace(vorher),
        }],
    }, verifiziert)


def _delete(state: AgentState) -> dict:
    """Einzelne Charakter-Anweisung deaktivieren (Soft-Delete)."""
    user_id = state["kontext"].get("user_id", "")
    target_id = state["parameter"].get("target_id")

    if not target_id:
        return _delete_alle(state)

    vorher = _read_by_id(target_id, user_id)

    betroffen: int = _zustand_setzen(target_id, user_id, aktiv=False)
    if betroffen != 1:
        return _keine_zeile_getroffen(state, target_id, user_id, betroffen)

    verifiziert = _verifizieren("delete", target_id, user_id, {"aktiv": False})
    logger.info(f"CharakterAgent: Anweisung {target_id} deaktiviert, verifiziert={verifiziert}")

    return verified_outcome({
        "ergebnis": f"Charakter-Anweisung (ID {target_id}) entfernt.",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren",
            "ergebnis": "geloescht",
            "id": target_id,
            "verifiziert": verifiziert,
            "vorher": _previous_state_trace(vorher),
        }],
    }, verifiziert)


def _delete_alle(state: AgentState) -> dict:
    """Alle aktiven Charakter-Anweisungen deaktivieren."""
    user_id = state["kontext"].get("user_id", "")

    affected = db_manager.execute(
        "UPDATE charakter_anweisungen SET aktiv = FALSE, geaendert_am = NOW() "
        "WHERE user_id = %s AND aktiv = TRUE",
        (user_id,),
    )

    nachher_count = _count_aktive(user_id)
    verifiziert = nachher_count == 0

    logger.info(
        f"CharakterAgent: Alle Anweisungen deaktiviert ({affected} Zeilen), "
        f"verifiziert={verifiziert}"
    )

    return verified_outcome({
        "ergebnis": "Alle Charakter-Anweisungen entfernt. Standardverhalten wiederhergestellt.",
        "status": "abgeschlossen",
        "schritte": state["schritte"]
        + [
            {
                "node": "ausfuehren",
                "ergebnis": "alle_geloescht",
                "anzahl": affected,
                "verifiziert": verifiziert,
            }
        ],
    }, verifiziert)


def _reactivate(state: AgentState) -> dict:
    """Inaktive Charakter-Anweisung wieder aktivieren."""
    user_id = state["kontext"].get("user_id", "")
    target_id = state["parameter"].get("target_id")
    anweisung = state["parameter"].get("anweisung", "")

    if not target_id:
        inaktive = _read_inaktive(user_id)
        treffer = (
            [
                a
                for a in inaktive
                if anweisung.lower() in a["anweisung"].lower()
                or a["anweisung"].lower() in anweisung.lower()
            ]
            if anweisung
            else inaktive
        )
        if len(treffer) == 1:
            target_id = treffer[0]["id"]
        elif len(treffer) > 1:
            zeilen = [f"  [{a['id']}] {a['anweisung']}" for a in treffer]
            return {
                "status": "rueckfrage",
                "rueckfrage": "Mehrere fruehere Anweisungen passen:\n"
                + "\n".join(zeilen)
                + "\nWelche soll ich wiederherstellen?",
                "schritte": state["schritte"]
                + [{"node": "ausfuehren", "ergebnis": "disambiguierung"}],
            }
        else:
            return {
                "status": "fehler",
                "fehler": "Keine inaktive Charakter-Anweisung gefunden",
                "schritte": state["schritte"]
                + [{"node": "ausfuehren", "ergebnis": "nicht_gefunden"}],
            }

    vorher = _read_by_id(target_id, user_id)

    betroffen: int = _zustand_setzen(target_id, user_id, aktiv=True)
    if betroffen != 1:
        return _keine_zeile_getroffen(state, target_id, user_id, betroffen)

    verifiziert = _verifizieren("reactivate", target_id, user_id, {"aktiv": True})
    nachher = _read_by_id(target_id, user_id)

    logger.info(f"CharakterAgent: Anweisung {target_id} reaktiviert, verifiziert={verifiziert}")

    return verified_outcome({
        "ergebnis": f"Charakter-Anweisung wiederhergestellt: {nachher['anweisung'] if nachher else '?'}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{
            "node": "ausfuehren",
            "ergebnis": "reaktiviert",
            "id": target_id,
            "verifiziert": verifiziert,
            "vorher": _previous_state_trace(vorher),
        }],
    }, verifiziert)


def _replace(state: AgentState) -> dict:
    """Charakter komplett ersetzen: Alle deaktivieren, neue anlegen."""
    user_id = state["kontext"].get("user_id", "")
    neue_anweisung = state["parameter"].get("anweisung", "")

    if not neue_anweisung:
        return {
            "status": "fehler",
            "fehler": "Keine neue Anweisung angegeben",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_anweisung"}],
        }

    affected = db_manager.execute(
        "UPDATE charakter_anweisungen SET aktiv = FALSE, geaendert_am = NOW() "
        "WHERE user_id = %s AND aktiv = TRUE",
        (user_id,),
    )

    result = db_manager.execute_returning(
        "INSERT INTO charakter_anweisungen (user_id, anweisung) VALUES (%s, %s) RETURNING id",
        (user_id, neue_anweisung),
    )
    neue_id = result["id"] if result else None

    verifiziert = _verifizieren("create", neue_id, user_id, {"aktiv": True})

    logger.info(
        f"CharakterAgent: Replace — {affected} deaktiviert, neue ID {neue_id}, "
        f"verifiziert={verifiziert}"
    )

    return verified_outcome({
        "ergebnis": f"Charakter komplett ersetzt durch: {neue_anweisung}",
        "status": "abgeschlossen",
        "schritte": state["schritte"]
        + [
            {
                "node": "ausfuehren",
                "ergebnis": "ersetzt",
                "deaktiviert": affected,
                "neue_id": neue_id,
                "verifiziert": verifiziert,
            }
        ],
    }, verifiziert)


def _konsolidieren(state: AgentState) -> dict:
    """Rueckfrage bei zu vielen aktiven Anweisungen (>=3)."""
    user_id = state["kontext"].get("user_id", "")
    aktive = _read_aktive(user_id)
    neue_anweisung = state["parameter"].get("anweisung", "")

    zeilen = [f"  [{a['id']}] {a['anweisung']}" for a in aktive]
    liste = "\n".join(zeilen)

    return {
        "status": "rueckfrage",
        "rueckfrage": (
            f"Du hast bereits {len(aktive)} aktive Charakter-Anweisungen:\n{liste}\n\n"
            f"Neue Anweisung: {neue_anweisung}\n\n"
            "Soll ich eine bestehende ersetzen, alle zusammenfassen, oder die neue trotzdem "
            "hinzufuegen?"
        ),
        "schritte": state["schritte"]
        + [{"node": "ausfuehren", "ergebnis": "konsolidierung_rueckfrage"}],
    }
