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

    @staticmethod
    def lzg_id_nachtragen(
        postgres_url: str,
        kzg_id:       str,
        lzg_id:       int,
    ) -> dict[str, int]:
        """Traegt die lzg_id in alle verbindung-Zeilen dieses KZG-Keys nach.

        Der Schritt bei der Promotion (§11.2): Zieht ein KZG-Eintrag in einen
        LZG-Knoten um, zeigen seine Bruecken-Zeilen danach auf den Knoten statt
        nur auf den fluechtigen Redis-Key. Ohne den Nachtrag verwaist die Zeile,
        sobald die TTL den Key raeumt.

        Vorbedingung: kzg_id ist nicht leer, lzg_id ist eine bestehende
        lzg_knoten-ID (Fremdschluessel).
        Nachbedingung: jede Zeile mit dieser kzg_id traegt diese lzg_id.
        Rueckgabe: {"gefunden": Zeilen mit dieser kzg_id, "geaendert": davon
        tatsaechlich geschrieben}. Beide Zahlen zusammen unterscheiden „kein
        Treffer" von „stand schon richtig" — eine Zahl allein koennte das nicht.
        Fehlerfaelle: leere kzg_id oder unplausible lzg_id (ValueError),
        Datenbankfehler (psycopg2.Error) — beide werden durchgereicht.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not kzg_id:
            raise ValueError("VerbindungRepository.lzg_id_nachtragen: kzg_id ist leer")
        if lzg_id is None or lzg_id <= 0:
            raise ValueError(
                f"VerbindungRepository.lzg_id_nachtragen: unplausible lzg_id={lzg_id}"
            )

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT count(*) FROM verbindung WHERE kzg_id = %s", (kzg_id,)
            )
            gefunden: int = int(cursor.fetchone()[0])

            # IS DISTINCT FROM statt IS NULL: ein zweiter Lauf schreibt nichts
            # mehr (idempotent), ein umgezogener Knoten wird trotzdem korrigiert.
            cursor.execute("""
                UPDATE verbindung
                SET    lzg_id = %s
                WHERE  kzg_id = %s
                  AND  lzg_id IS DISTINCT FROM %s
            """, (lzg_id, kzg_id, lzg_id))
            geaendert: int = cursor.rowcount
            conn.commit()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if geaendert > gefunden:
            raise RuntimeError(
                f"VerbindungRepository.lzg_id_nachtragen: {geaendert} Zeilen geaendert, "
                f"aber nur {gefunden} gefunden — kzg_id={kzg_id}"
            )

        logger.debug(
            "VerbindungRepository: lzg_id=%d nachgetragen — kzg_id=%s, "
            "gefunden=%d, geaendert=%d",
            lzg_id, kzg_id, gefunden, geaendert,
        )
        return {"gefunden": gefunden, "geaendert": geaendert}
