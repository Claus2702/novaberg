"""
Datenzugriffsschicht für die verbindung-Tabelle (Brücke Turn ↔ Gedächtnis-Eintrag).
Keine Business-Logik — reine CRUD-Operationen.

Spezifikation: docs/novaberg-charakter-resonanz_k.md §12, Bauteil 1b.
"""

import logging

import psycopg2

logger = logging.getLogger("ki_server.memory.repositories.verbindung")


class VerbindungRepository:
    """Datenzugriffsschicht für die verbindung-Tabelle. Keine Business-Logik."""

    @staticmethod
    def insert(
        postgres_url: str,
        turn_id:      str,
        kzg_id:       str,
        lzg_id:       int | None = None,
    ) -> int:
        """Legt eine verbindung-Zeile an und gibt ihre ID zurück.

        Eine Zeile bezeugt: dieser Turn hat diesen KZG-Eintrag erzeugt. Das
        lzg_id-Feld bleibt bei der Geburt leer und wird erst bei der Promotion
        nachgetragen (§11 Schritt 2).

        Vorbedingung: turn_id und kzg_id sind nicht leer — beide Spalten sind
        NOT NULL, und eine Zeile ohne eine der beiden Seiten belegt nichts.
        Nachbedingung: genau eine Zeile existiert, ihre ID wird zurückgegeben.
        Fehlerfälle: leere turn_id oder kzg_id (ValueError), INSERT ohne
        RETURNING-Zeile (RuntimeError), Datenbankfehler (psycopg2.Error) —
        alle drei werden an den Aufrufer durchgereicht, nicht geschluckt.
        """

        # ── Eingabe-Validierung ─────────────────────
        if not turn_id:
            raise ValueError("VerbindungRepository.insert: turn_id ist leer")
        if not kzg_id:
            raise ValueError("VerbindungRepository.insert: kzg_id ist leer")

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verbindung (turn_id, kzg_id, lzg_id)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (turn_id, kzg_id, lzg_id))
            zeile: tuple | None = cursor.fetchone()
            conn.commit()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if not zeile:
            raise RuntimeError(
                f"VerbindungRepository.insert: INSERT lieferte keine ID zurueck "
                f"— turn_id={turn_id}, kzg_id={kzg_id}"
            )

        verbindung_id: int = int(zeile[0])
        logger.debug(
            "VerbindungRepository: Zeile %d angelegt — turn_id=%s, kzg_id=%s",
            verbindung_id, turn_id, kzg_id,
        )
        return verbindung_id
