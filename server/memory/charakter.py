"""
Charakter-Hash — Kern + Adaptiv aus PostgreSQL.
"""

import logging

import psycopg2

from config import ASSISTANT_USER_ID, RAD_MIN, RAD_MAX

logger = logging.getLogger("ki_server.memory.charakter")


def charakter_hash_retrieve(postgres_url: str, user_id: str, character_id: str = "") -> str:
    """Holt den aktuellen Charakter-Hash fuer ein Gespraechspaar."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            kern, adaptiv = row
            parts: list[str] = []
            if kern:
                parts.append(f"Kern-Persönlichkeit: {kern}")
            if adaptiv:
                parts.append(f"Aktuelle Phase: {adaptiv}")
            logger.info(f"Charakter-Hash gefunden fuer Paar '{user_id}/{character_id}'")
            return "\n".join(parts)

        return ""

    except Exception as fehler:
        logger.error(f"Charakter-Hash Abruf fehlgeschlagen: {fehler}")
        return ""


def charakter_hash_retrieve_dict(postgres_url: str, user_id: str, character_id: str = "") -> dict:
    """Holt den Charakter-Hash als Dict fuer ein Gespraechspaar."""

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT kern_hash, adaptive_hash, beziehungsprofil, intentions_profil, emotions_profil "
            "FROM charakter_hash WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "kern":              row[0] or "",
                "adaptiv":           row[1] or "",
                "beziehungsprofil":  row[2] or "",
                "intentions_profil": row[3] or "",
                "emotions_profil":   row[4] or "",
            }

        return {}

    except Exception as fehler:
        logger.error(f"Charakter-Hash-Dict Abruf fehlgeschlagen: {fehler}")
        return {}


def nova_charakter_hash_retrieve_dict(postgres_url: str, user_id: str) -> dict:
    """Laedt Novas Charakter-Hash fuer das Gespraech mit einem bestimmten User.

    Im Paar-Schema lebt Novas Charakter unter (ASSISTANT_USER_ID, user_id):
    ASSISTANT_USER_ID ist der Schreiber (Subjekt), user_id der Gegenueber.
    Diese Funktion macht die Argument-Reihenfolge logisch — ohne sie waere
    der Aufrufer auf den Vertausch von user_id und character_id angewiesen.

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: Liefert dict mit den fuenf Hash-Schichten oder {} bei
    fehlendem Datensatz.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("nova_charakter_hash_retrieve_dict: user_id leer — verworfen")
        return {}

    # ── Verarbeitung ────────────────────────────
    return charakter_hash_retrieve_dict(postgres_url, ASSISTANT_USER_ID, user_id)


def nutzer_gewichtung_laden(postgres_url: str, user_id: str) -> tuple[float | None, str]:
    """Laedt Novas Gewichtung des Nutzers — den Faktor des Charakter-Rads.

    Gelesen wird die Zeile (ASSISTANT_USER_ID, user_id), also **Novas Zuwendung
    zum Nutzer**. Die Gegenzeile (user_id, ASSISTANT_USER_ID) traegt dieselben
    Spaltennamen und ist seine Zuwendung zu ihr — sie hat bewusst keinen
    Verbraucher. Wer sie laese, bekaeme die Gewichtung auf dem Kopf: Ein
    aufmerksamer Nutzer machte dann IHR Gedaechtnis empfaenglicher, obwohl
    ueber ihre Bereitschaft nichts gesagt waere
    (novaberg-salienz-berechnung_k.md §8, "Welche Zeile die Formel liest").

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: (faktor, quelle) mit faktor in [RAD_MIN, RAD_MAX] und quelle
        aus {'default', 'destilliert'}.
    Fehlerfaelle: leere user_id, fehlender Datensatz oder DB-Fehler — dann
        (None, 'fehlt'). Ausdruecklich NICHT (0.9, 'default'): Der Aufrufer
        muss "nie destilliert" von "nicht gelesen" unterscheiden koennen, sonst
        sieht ein Lesefehler aus wie ein Charakter ohne Auspraegung.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        logger.error("nutzer_gewichtung_laden: user_id leer — verworfen")
        return None, "fehlt"

    # ── Verarbeitung ────────────────────────────
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nutzer_gewichtung, nutzer_gewichtung_quelle FROM charakter_hash "
            "WHERE user_id = %s AND character_id = %s",
            (ASSISTANT_USER_ID, user_id),
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as fehler:
        logger.error(
            f"nutzer_gewichtung_laden: Abruf fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' fehlgeschlagen — {fehler}"
        )
        return None, "fehlt"

    if not row:
        logger.error(
            f"nutzer_gewichtung_laden: keine charakter_hash-Zeile fuer Paar "
            f"'{ASSISTANT_USER_ID}/{user_id}' — Faktor nicht ermittelbar"
        )
        return None, "fehlt"

    faktor: float = float(row[0])
    quelle: str   = row[1] or "default"

    # ── Ausgabe-Verifikation ────────────────────
    # Die Destillation kappt bereits beim Schreiben. Greift die Pruefung hier
    # trotzdem, steht ein Wert in der Tabelle, den kein Rad erzeugt haben kann
    # — das gehoert benannt, nicht stillschweigend mitgerechnet.
    if not RAD_MIN <= faktor <= RAD_MAX:
        logger.warning(
            f"nutzer_gewichtung_laden: Faktor {faktor:.4f} ausserhalb "
            f"[{RAD_MIN}, {RAD_MAX}] fuer Paar '{ASSISTANT_USER_ID}/{user_id}' "
            f"— gekappt, Herkunft '{quelle}'"
        )
        faktor = max(RAD_MIN, min(RAD_MAX, faktor))

    logger.debug(
        f"nutzer_gewichtung_laden: {faktor:.4f} (Herkunft '{quelle}') "
        f"fuer Paar '{ASSISTANT_USER_ID}/{user_id}'"
    )
    return faktor, quelle
