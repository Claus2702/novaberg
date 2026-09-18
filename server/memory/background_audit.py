"""Audit of background work — one writer for `hintergrund_log`.

Every background run writes `gestartet` at its start and `erledigt` or
`fehler` at its end. Until 18.09.2026 nine modules carried their own copy of
the same INSERT, and they had already drifted apart: two caught only database
and network errors, the others everything; one checked the status, the rest
did not. This module is the one copy they all delegate to.

The failsafe is the same for every caller: a failed INSERT is reported with
`logger.critical` and never retried — a retry on a broken audit sink would
loop, and the audit must not take the background run down with it.
"""

import logging

import psycopg2

from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.memory.background_audit")

AUDIT_STATUSES: frozenset[str] = frozenset({"gestartet", "erledigt", "fehler"})


def write_audit(user_id: str, task: str, status: str, result: str) -> bool:
    """Schreibt einen Eintrag ins `hintergrund_log`.

    **Gefangen werden Datenbank- und Netzfehler**, also das, was ein INSERT
    tatsaechlich wirft. Ein Defekt ausserhalb dieser Menge soll sichtbar
    werden, statt als verlorener Audit-Eintrag zu erscheinen — die engere der
    beiden Fassungen, die im Bestand nebeneinander standen.

    Vorbedingung: `user_id` und `task` sind nicht leer, `status` ist einer
        aus `AUDIT_STATUSES`.
    Nachbedingung: eine Zeile im `hintergrund_log`, oder eine kritische
        Logmeldung mit dem verlorenen Eintrag.
    Fehlerfaelle: Eine verletzte Vorbedingung ist ein Fehler des Aufrufers und
        wirft `ValueError` — alle Aufrufer setzen Literale.

    Args:
        user_id: Der Mensch, fuer den gearbeitet wurde (`DEFAULT_USER_ID` bei
            Wartungslaeufen ohne Paar).
        task: Name der Aufgabe, stabil und greppbar.
        status: `gestartet`, `erledigt` oder `fehler`.
        result: Die Zahlen oder der Fehler des Laufs im Klartext.

    Returns:
        True, wenn die Zeile geschrieben ist.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        raise ValueError(f"Audit '{task}/{status}': leere user_id")
    if not task:
        raise ValueError(f"Audit mit Status '{status}': leere Aufgabe")
    if status not in AUDIT_STATUSES:
        raise ValueError(
            f"Audit '{task}': Status '{status}' ist keiner aus {sorted(AUDIT_STATUSES)}"
        )

    # ── Verarbeitung ────────────────────────────
    try:
        zeilen: int = db_manager.execute(
            """
            INSERT INTO hintergrund_log
                (user_id, aufgabe, status, ergebnis, verarbeitet_am)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (user_id, task, status, result),
        )
    except (psycopg2.Error, OSError) as fehler:
        logger.critical(
            "hintergrund_log-INSERT fehlgeschlagen (%s: %s) — verlorener "
            "Audit-Eintrag: %s/%s/%s",
            type(fehler).__name__, fehler, task, status, (result or "")[:100],
        )
        return False

    # ── Ausgabe-Verifikation ────────────────────
    if zeilen != 1:
        logger.critical(
            "hintergrund_log-INSERT schrieb %s Zeilen statt einer — Eintrag "
            "%s/%s fraglich", zeilen, task, status,
        )
        return False
    return True
