"""
Datenzugriffsschicht für die fakten-Tabelle (Knowledge Graph Edges).
Keine Business-Logik — reine CRUD-Operationen.

Drei Regeln gelten für jede Funktion dieser Datei:

- **Jede Abfrage filtert nach dem Paar** (`user_id`, `character_id`). Ein Fakt
  gehört zu einer Beziehung, nicht zu einem Menschen allein.
- **Kein Lesen schreibt.** Die Lesefunktionen lesen mit `SELECT` und ohne
  Commit; `last_touched` setzt nur ein Schreiben. Ein Lesen, das den Anker des
  Verfalls nachzieht, hielte jeden gelesenen Fakt künstlich frisch.
- **Geschrieben wird auf dem Cursor des Aufrufers**, wo mehr als eine Zeile
  zusammengehört (`insert`, `abloesen`). Commit und Rollback hat der Aufrufer;
  eine Ablösung gilt ganz oder gar nicht. `schreiben` ist dieser Aufrufer für
  einen einzelnen Fakt: eine Verbindung, eine Transaktion.
"""

import logging
from dataclasses import dataclass
from datetime import datetime

import psycopg2
import psycopg2.extras

from config import FAKTEN_DECAY_RATE
from memory.utils import embedding_zu_pgvector_str

logger = logging.getLogger("ki_server.memory.repositories.fakten")

# Die erlaubten Herkünfte. Dieselbe Liste prüft die Datenbank
# (chk_fakten_herkunft); hier steht sie, damit ein Fehler vor dem Schreiben
# mit Namen gemeldet wird und nicht erst als Verletzung einer Prüfung.
HERKUNFT_WERTE: frozenset[str] = frozenset({"mensch", "nova", "modell", "recherche"})

# Die Stärke einer neuen Kante. Sie ist der Wert der Verfallsformel am Anker,
# exp(−rate · 0) = 1: Eine eben geschriebene Kante hat noch nichts verloren.
# Die Spalte hat keinen Vorgabewert; `insert` schreibt diesen Wert ausdrücklich.
NEW_EDGE_STRENGTH: float = 1.0


@dataclass(frozen=True)
class NewFact:
    """Ein Fakt, wie er angelegt werden soll — ohne Paar, Subjekt und Beziehung.

    Paar, Subjekt und Beziehung übergibt der Aufrufer getrennt, weil `abloesen`
    sie auch für das Invalidieren braucht. Geprüft wird in `insert`.
    """

    fakt_text:   str
    herkunft:    str
    einwertig:   bool
    objekt_id:   int | None = None
    objekt_wert: str | None = None
    embedding:   list[float] | None = None
    t_valid:     datetime | None = None
    timeline_id: int | None = None


# Was `schreiben` getan hat. Eine geschlossene Menge, damit ein Aufrufer jeden
# Fall benennen muss und kein vierter still durchrutscht.
SCHREIBUNG_ARTEN: frozenset[str] = frozenset({"identisch", "angelegt", "abgeloest"})


@dataclass(frozen=True)
class Schreibung:
    """Das Ergebnis von `FaktenRepository.schreiben`.

    `fakt_id` ist die Zeile, die nach dem Schreiben gilt; bei `identisch` die
    schon vorhandene. `art` ist eines aus `SCHREIBUNG_ARTEN`.
    """

    fakt_id: int
    art:     str

    def __post_init__(self) -> None:
        """Weist eine Art außerhalb von `SCHREIBUNG_ARTEN` ab.

        Vorbedingung: keine.
        Nachbedingung: `art` ist eine bekannte Art, `fakt_id` eine positive Zahl.
        Fehlerfälle: ValueError sonst.
        """
        # ── Eingabe-Validierung ─────────────────────
        if self.art not in SCHREIBUNG_ARTEN:
            raise ValueError(f"Schreibung: unbekannte Art {self.art!r}")
        if not isinstance(self.fakt_id, int) or self.fakt_id <= 0:
            raise ValueError(f"Schreibung: ungültige fakt_id {self.fakt_id!r}")


def _check_pair(user_id: str, character_id: str) -> None:
    """Prüft das Paar, bevor eine Abfrage es benutzt.

    Vorbedingung: keine.
    Nachbedingung: Beide Teile sind nicht leer.
    Fehlerfälle: ValueError, wenn ein Teil fehlt — ohne Paar gäbe eine Abfrage
        die Fakten aller Beziehungen eines Menschen zurück.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        raise ValueError(
            f"fakten: Paar unvollständig (user_id={user_id!r}, "
            f"character_id={character_id!r}) — keine Abfrage ohne Paar"
        )


def _verify_rows(funktion: str, rows: list[dict], expected: dict[str, object]) -> list[dict]:
    """Prüft jede gelesene Zeile gegen die Bedingungen ihrer Abfrage.

    Die Ausgabe-Verifikation der Lesefunktionen: Eine Zeile, die nicht zum
    Paar gehört oder eine andere Bedingung der Abfrage verletzt, heißt, dass
    die Abfrage ihren Filter verloren hat. Das ist ein Programmierfehler,
    kein leeres Ergebnis.

    Verglichen wird ohne Umwandlung. Die Aufrufer nennen deshalb nur Werte,
    die der Code selbst setzt (Paar, `aktiv`): Eine ID aus der Antwort des
    Modells kann als Text ankommen, und die Datenbank wandelt sie still.

    Vorbedingung: `expected` nennt je Spalte den Wert, den jede Zeile tragen muss.
    Nachbedingung: Jede Zeile trägt jeden erwarteten Wert; `rows` kommt
        unverändert zurück.
    Fehlerfälle: ValueError, wenn `expected` leer ist — dann prüfte die
        Verifikation nichts. RuntimeError mit Funktion, Spalte und ID der
        ersten abweichenden Zeile, auch wenn eine Spalte fehlt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not expected:
        raise ValueError(f"fakten.{funktion}: keine Bedingung zu prüfen")

    # ── Verarbeitung ────────────────────────────
    abweichung: tuple[dict, str] | None = next(
        (
            (row, spalte)
            for row in rows
            for spalte, wert in expected.items()
            if spalte not in row or row[spalte] != wert
        ),
        None,
    )

    # ── Ausgabe-Verifikation ────────────────────
    if abweichung is not None:
        row, spalte = abweichung
        gelesen: str = repr(row[spalte]) if spalte in row else "keine Spalte"
        raise RuntimeError(
            f"fakten.{funktion}: Zeile id={row.get('id')} trägt {spalte}={gelesen}, "
            f"erwartet {expected[spalte]!r} — die Abfrage hat ihren Filter verloren"
        )
    return rows


class FaktenRepository:
    """Datenzugriffsschicht für die fakten-Tabelle. Keine Business-Logik."""

    @staticmethod
    def embed_text_bauen(fakt_text: str) -> str:
        """
        Baut den Embed-Text eines Fakts — die EINZIGE Formel für diese
        Spalte (Chat 107). Der Text ist aus der persistierten Spalte
        fakt_text vollständig rekonstruierbar.

        E: fakt_text muss nicht-leer sein.
        V: Formel ist die Identität (Live-Formel des FaktenManagers).
        A: der unveränderte fakt_text.
        """
        if not fakt_text or not fakt_text.strip():
            raise ValueError(
                "embed_text_bauen(fakten): fakt_text ist leer — kein Embed-Text baubar"
            )
        return fakt_text

    @staticmethod
    def insert(
        cur:          object,
        user_id:      str,
        character_id: str,
        subjekt_id:   int,
        attribut:     str,
        neu:          NewFact,
    ) -> int:
        """Legt einen Fakt auf dem Cursor des Aufrufers an und gibt seine ID zurück.

        Paar, Herkunft, Einwertigkeit und Stärke werden ausdrücklich
        geschrieben; keine der Spalten fällt auf einen Vorgabewert der
        Datenbank zurück.

        Vorbedingung: `cur` gehört zu einer offenen Transaktion; Commit und
            Rollback hat der Aufrufer.
        Nachbedingung: Eine neue, aktive Zeile steht in der Transaktion, mit
            der Stärke `NEW_EDGE_STRENGTH`.
        Fehlerfälle: ValueError bei unvollständigem Paar, leerer Beziehung,
            leerem Text, unbekannter Herkunft, nicht-boolescher Einwertigkeit
            oder wenn nicht genau eines von objekt_id und objekt_wert gesetzt
            ist. Ein Fehler der Datenbank (etwa ein zweiter aktiver Wert einer
            einwertigen Beziehung) wird nicht gefangen.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)
        if not attribut:
            raise ValueError("fakten.insert: attribut ist leer")
        if not neu.fakt_text or not neu.fakt_text.strip():
            raise ValueError("fakten.insert: fakt_text ist leer")
        if neu.herkunft not in HERKUNFT_WERTE:
            raise ValueError(
                f"fakten.insert: unbekannte Herkunft {neu.herkunft!r} — "
                f"erlaubt sind {sorted(HERKUNFT_WERTE)}"
            )
        if not isinstance(neu.einwertig, bool):
            raise ValueError(f"fakten.insert: einwertig ist kein bool ({neu.einwertig!r})")
        if (neu.objekt_id is None) == (neu.objekt_wert is None):
            raise ValueError(
                "Genau einer von objekt_id oder objekt_wert muss gesetzt sein."
            )

        # ── Verarbeitung ────────────────────────────
        embedding_str: str | None = (
            embedding_zu_pgvector_str(neu.embedding) if neu.embedding else None
        )
        cur.execute(
            """
            INSERT INTO fakten
                (user_id, character_id, subjekt_id, attribut, objekt_id,
                 objekt_wert, fakt_text, embedding, t_valid, herkunft,
                 einwertig, timeline_id, staerke_decay)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, character_id, subjekt_id, attribut, neu.objekt_id,
             neu.objekt_wert, neu.fakt_text, embedding_str, neu.t_valid,
             neu.herkunft, neu.einwertig, neu.timeline_id, NEW_EDGE_STRENGTH),
        )
        zeile: tuple | None = cur.fetchone()

        # ── Ausgabe-Verifikation ────────────────────
        if zeile is None:
            raise RuntimeError("fakten.insert: INSERT lieferte keine ID")
        return int(zeile[0])

    @staticmethod
    def abloesen(
        cur:          object,
        user_id:      str,
        character_id: str,
        subjekt_id:   int,
        attribut:     str,
        neu:          NewFact,
    ) -> int:
        """Löst den aktiven Wert einer einwertigen Beziehung ab und gibt die neue ID zurück.

        Invalidiert den aktiven Wert zu Paar, Subjekt und Beziehung (aktiv =
        FALSE, t_invalid gesetzt — die Zeile bleibt für die Historie) und legt
        den neuen an. Gibt es keinen aktiven Wert, wird nur angelegt. Beides
        geschieht auf dem Cursor des Aufrufers: Scheitert das Anlegen, nimmt
        sein Rollback auch das Invalidieren zurück.

        Ob der neue Wert derselbe ist wie der alte, entscheidet der Aufrufer
        vorher; diese Funktion schreibt immer.

        Vorbedingung: `cur` gehört zu einer offenen Transaktion; `neu` ist
            einwertig.
        Nachbedingung: In der Transaktion steht genau ein aktiver einwertiger
            Wert zu Paar, Subjekt und Beziehung — der neue.
        Fehlerfälle: ValueError, wenn `neu` nicht einwertig ist (eine
            mehrwertige Beziehung wird angelegt, nicht abgelöst), und alle
            Fehler von `insert`. RuntimeError, wenn danach nicht genau ein
            aktiver Wert steht. Nichts davon wird gefangen.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)
        if neu.einwertig is not True:
            raise ValueError(
                f"fakten.abloesen: {attribut!r} ist nicht einwertig — "
                f"eine mehrwertige Beziehung wird angelegt, nicht abgelöst"
            )

        # ── Verarbeitung ────────────────────────────
        cur.execute(
            """
            UPDATE fakten
            SET aktiv = FALSE, t_invalid = NOW()
            WHERE user_id = %s AND character_id = %s
              AND subjekt_id = %s AND attribut = %s
              AND aktiv AND einwertig
            RETURNING id
            """,
            (user_id, character_id, subjekt_id, attribut),
        )
        abgeloest: list[int] = [int(z[0]) for z in cur.fetchall()]
        neue_id: int = FaktenRepository.insert(
            cur, user_id, character_id, subjekt_id, attribut, neu,
        )

        # ── Ausgabe-Verifikation ────────────────────
        cur.execute(
            """
            SELECT count(*) FROM fakten
            WHERE user_id = %s AND character_id = %s
              AND subjekt_id = %s AND attribut = %s
              AND aktiv AND einwertig
            """,
            (user_id, character_id, subjekt_id, attribut),
        )
        aktive: int = int(cur.fetchone()[0])
        if aktive != 1:
            raise RuntimeError(
                f"fakten.abloesen: {aktive} aktive Werte zu {attribut!r} nach der "
                f"Ablösung — erwartet genau einer"
            )
        logger.info(
            "fakten.abloesen: %s abgelöst durch id=%s (%s)", abgeloest, neue_id, attribut,
        )
        return neue_id

    @staticmethod
    def schreiben(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        subjekt_id:   int,
        attribut:     str,
        neu:          NewFact,
    ) -> Schreibung:
        """Schreibt einen Fakt in einer eigenen Transaktion und sagt, was geschah.

        Ist derselbe Wert zu Paar, Subjekt und Beziehung schon aktiv, wird nur
        dessen `last_touched` nachgezogen (*identisch*). Verglichen wird gegen
        **jeden** aktiven Wert, nicht nur den jüngsten: Bei einer mehrwertigen
        Beziehung kann der genannte Wert ein älterer sein. Eine Objekt-Entität
        gilt als derselbe Wert bei derselben ID, ein Wert bei gleichem Text
        ohne Rücksicht auf Groß- und Kleinschreibung und Rand. Sonst löst eine
        einwertige Beziehung den alten Wert ab (`abloesen`), eine mehrwertige
        fügt hinzu (`insert`).

        Die aktiven Zeilen werden mit `FOR UPDATE` gelesen, damit ein zweiter
        Schreiber derselben Kante wartet, statt zwischen Prüfen und Schreiben
        einen Wert abzulösen.

        Herkunft, Text und Einwertigkeit prüft `insert` — erst nach dem
        Invalidieren. Ein Fehler dort nimmt deshalb auch das Invalidieren
        zurück; das ist der Zweck des Rollbacks.

        Vorbedingung: Das Paar ist vollständig, die Beziehung nicht leer, und
            genau eines von objekt_id und objekt_wert ist gesetzt.
        Nachbedingung: Nach dem Commit ist die Zeile `fakt_id` aktiv und gehört
            zu Paar, Subjekt und Beziehung. Bei `identisch` ist keine Zeile neu.
        Fehlerfälle: ValueError bei verletzter Vorbedingung und aus `insert`;
            RuntimeError, wenn die geltende Zeile die Nachbedingung verletzt;
            jeder Fehler der Datenbank. Bei jedem Fehler wird die ganze
            Transaktion zurückgenommen und der Fehler geworfen.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)
        if not attribut:
            raise ValueError("fakten.schreiben: attribut ist leer")
        if (neu.objekt_id is None) == (neu.objekt_wert is None):
            raise ValueError(
                "fakten.schreiben: genau einer von objekt_id oder objekt_wert muss gesetzt sein"
            )

        # ── Verarbeitung ────────────────────────────
        wert: str | None = (
            neu.objekt_wert.strip().casefold() if neu.objekt_wert is not None else None
        )
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, objekt_id, objekt_wert, einwertig FROM fakten
                    WHERE user_id = %s AND character_id = %s
                      AND subjekt_id = %s AND attribut = %s AND aktiv
                    ORDER BY id
                    FOR UPDATE
                    """,
                    (user_id, character_id, subjekt_id, attribut),
                )
                aktive: list[tuple] = cur.fetchall()
                gleich: list[int] = [
                    int(z[0]) for z in aktive
                    if (neu.objekt_id is not None and z[1] == neu.objekt_id)
                    or (wert is not None and z[2] is not None
                        and z[2].strip().casefold() == wert)
                ]
                if gleich:
                    fakt_id: int = gleich[0]
                    art: str = "identisch"
                    cur.execute(
                        "UPDATE fakten SET last_touched = NOW() WHERE id = %s", (fakt_id,),
                    )
                elif neu.einwertig is True:
                    fakt_id = FaktenRepository.abloesen(
                        cur, user_id, character_id, subjekt_id, attribut, neu,
                    )
                    art = "abgeloest" if any(z[3] for z in aktive) else "angelegt"
                else:
                    fakt_id = FaktenRepository.insert(
                        cur, user_id, character_id, subjekt_id, attribut, neu,
                    )
                    art = "angelegt"

                # ── Ausgabe-Verifikation ────────────────────
                # In derselben Transaktion: Eine geltende Zeile, die nicht zu
                # Paar, Subjekt und Beziehung gehört, nimmt alles zurück.
                cur.execute(
                    """
                    SELECT user_id, character_id, subjekt_id, attribut, aktiv
                    FROM fakten WHERE id = %s
                    """,
                    (fakt_id,),
                )
                geltend: tuple | None = cur.fetchone()
                erwartet: tuple = (user_id, character_id, subjekt_id, attribut, True)
                if geltend != erwartet:
                    raise RuntimeError(
                        f"fakten.schreiben: Zeile id={fakt_id} trägt {geltend!r}, "
                        f"erwartet {erwartet!r}"
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception(
                "fakten.schreiben: %s zu Subjekt %s zurückgenommen", attribut, subjekt_id,
            )
            raise
        finally:
            conn.close()

        logger.info("fakten.schreiben: id=%s %s (%s)", fakt_id, art, attribut)
        return Schreibung(fakt_id=fakt_id, art=art)

    @staticmethod
    def find_by_id(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        fakt_id:      int,
    ) -> dict | None:
        """Lädt einen aktiven Fakt des Paares per ID.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Nichts wurde geschrieben, auch nicht last_touched. Eine
            gelieferte Zeile ist aktiv und gehört zum Paar.
        Fehlerfälle: ValueError bei unvollständigem Paar. None, wenn der Fakt
            nicht aktiv ist oder einem anderen Paar gehört. RuntimeError, wenn
            die Zeile die Nachbedingung verletzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE id = %s AND user_id = %s AND character_id = %s
                  AND aktiv = TRUE
            """, (fakt_id, user_id, character_id))
            row = cursor.fetchone()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if row is None:
            return None
        return _verify_rows("find_by_id", [dict(row)], {
            "user_id": user_id, "character_id": character_id, "aktiv": True,
        })[0]

    @staticmethod
    def find_by_subjekt(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        subjekt_id:   int,
    ) -> list[dict]:
        """Lädt alle aktiven Fakten des Paares zu einer Entität.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Nichts wurde geschrieben, auch nicht last_touched. Jede
            Zeile ist aktiv und gehört zum Paar.
        Fehlerfälle: ValueError bei unvollständigem Paar. RuntimeError, wenn
            eine Zeile die Nachbedingung verletzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE user_id = %s AND character_id = %s
                  AND subjekt_id = %s AND aktiv = TRUE
                ORDER BY id
            """, (user_id, character_id, subjekt_id))
            rows = cursor.fetchall()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return _verify_rows("find_by_subjekt", [dict(row) for row in rows], {
            "user_id": user_id, "character_id": character_id, "aktiv": True,
        })

    @staticmethod
    def find_aktiv(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        subjekt_id:   int,
        attribut:     str,
    ) -> dict | None:
        """Findet den aktiven Fakt des Paares zu Subjekt und Beziehung.

        Für die Ablösung: Gibt es schon einen aktiven Wert? Bei einer
        mehrwertigen Beziehung kommt der jüngste.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Nichts wurde geschrieben, auch nicht last_touched. Eine
            gelieferte Zeile ist aktiv und gehört zum Paar.
        Fehlerfälle: ValueError bei unvollständigem Paar. RuntimeError, wenn
            die Zeile die Nachbedingung verletzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE user_id = %s AND character_id = %s
                  AND subjekt_id = %s AND attribut = %s AND aktiv = TRUE
                ORDER BY id DESC
                LIMIT 1
            """, (user_id, character_id, subjekt_id, attribut))
            row = cursor.fetchone()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if row is None:
            return None
        return _verify_rows("find_aktiv", [dict(row)], {
            "user_id": user_id, "character_id": character_id, "aktiv": True,
        })[0]

    @staticmethod
    def find_similar(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        embedding:    list[float],
        # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.80 im
        # casing-blinden Raum. Kein Live-Aufrufer — mitgezogen, damit der
        # Pfad bei Reaktivierung nicht mit einem toten Wert startet.
        # ⚠ Wachposten: nicht gemessen — begruendeter Startwert.
        threshold:    float = 0.70,
        limit:        int = 5,
    ) -> list[dict]:
        """Sucht aktive Fakten des Paares per Embedding-Ähnlichkeit.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Nichts wurde geschrieben; jede Zeile trägt 'similarity',
            ist aktiv und gehört zum Paar.
        Fehlerfälle: ValueError bei unvollständigem Paar. RuntimeError, wenn
            eine Zeile die Nachbedingung verletzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)
        embedding_str: str = embedding_zu_pgvector_str(embedding)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT *,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM fakten
                WHERE user_id = %s AND character_id = %s
                  AND aktiv = TRUE
                  AND embedding IS NOT NULL
                  AND 1 - (embedding <=> %s::vector) >= %s
                ORDER BY similarity DESC
                LIMIT %s
            """, (embedding_str, user_id, character_id, embedding_str, threshold, limit))
            rows = cursor.fetchall()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return _verify_rows("find_similar", [dict(row) for row in rows], {
            "user_id": user_id, "character_id": character_id, "aktiv": True,
        })

    @staticmethod
    def invalidate(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        fakt_id:      int,
    ) -> bool:
        """Invalidiert einen aktiven Fakt des Paares (nicht löschen!).

        Setzt aktiv=FALSE und t_invalid=NOW(); der Fakt bleibt für die
        Historie erhalten. Eigene Verbindung, eigener Commit — für eine
        Ablösung gilt `abloesen`.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Der Fakt ist nicht mehr aktiv.
        Fehlerfälle: ValueError bei unvollständigem Paar. False, wenn kein
            aktiver Fakt des Paares diese ID trägt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fakten
                SET aktiv = FALSE, t_invalid = NOW()
                WHERE id = %s AND user_id = %s AND character_id = %s
                  AND aktiv = TRUE
            """, (fakt_id, user_id, character_id))
            getroffen: int = cursor.rowcount
            conn.commit()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if getroffen != 1:
            logger.error(
                "fakten.invalidate: kein aktiver Fakt id=%s im Paar (%s, %s)",
                fakt_id, user_id, character_id,
            )
            return False
        return True

    @staticmethod
    def find_historie(
        postgres_url: str,
        user_id:      str,
        character_id: str,
        subjekt_id:   int,
        attribut:     str,
    ) -> list[dict]:
        """Lädt alle Fakten des Paares (aktiv und inaktiv) zu Subjekt und Beziehung.

        Für historische Abfragen: "Wo hat Michael früher gewohnt?"
        Sortiert nach t_valid DESC (neueste zuerst).

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Nichts wurde geschrieben. Jede Zeile gehört zum Paar,
            aktiv oder nicht.
        Fehlerfälle: ValueError bei unvollständigem Paar. RuntimeError, wenn
            eine Zeile die Nachbedingung verletzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE user_id = %s AND character_id = %s
                  AND subjekt_id = %s AND attribut = %s
                ORDER BY t_valid DESC NULLS LAST, id DESC
            """, (user_id, character_id, subjekt_id, attribut))
            rows = cursor.fetchall()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return _verify_rows("find_historie", [dict(row) for row in rows], {
            "user_id": user_id, "character_id": character_id,
        })

    @staticmethod
    def set_wiedervorlage(
        postgres_url:     str,
        user_id:          str,
        character_id:     str,
        fakt_id:          int,
        wiedervorlage_am: datetime | None,
    ) -> bool:
        """Setzt oder löscht das Wiedervorlage-Datum eines Fakts des Paares.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Der Fakt trägt das neue Datum.
        Fehlerfälle: ValueError bei unvollständigem Paar. False, wenn kein
            Fakt des Paares diese ID trägt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fakten
                SET wiedervorlage_am = %s
                WHERE id = %s AND user_id = %s AND character_id = %s
            """, (wiedervorlage_am, fakt_id, user_id, character_id))
            getroffen: int = cursor.rowcount
            conn.commit()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        if getroffen != 1:
            logger.error(
                "fakten.set_wiedervorlage: kein Fakt id=%s im Paar (%s, %s)",
                fakt_id, user_id, character_id,
            )
            return False
        return True

    @staticmethod
    def find_wiedervorlage_faellig(
        postgres_url: str,
        user_id:      str,
        character_id: str,
    ) -> list[dict]:
        """Lädt alle aktiven Fakten des Paares mit fälliger Wiedervorlage.

        Vorbedingung: Das Paar ist vollständig.
        Nachbedingung: Nichts wurde geschrieben. Jede Zeile ist aktiv und
            gehört zum Paar.
        Fehlerfälle: ValueError bei unvollständigem Paar. RuntimeError, wenn
            eine Zeile die Nachbedingung verletzt.
        """
        # ── Eingabe-Validierung ─────────────────────
        _check_pair(user_id, character_id)

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("""
                SELECT * FROM fakten
                WHERE user_id = %s AND character_id = %s
                  AND aktiv = TRUE
                  AND wiedervorlage_am IS NOT NULL
                  AND wiedervorlage_am <= NOW()
                ORDER BY wiedervorlage_am
            """, (user_id, character_id))
            rows = cursor.fetchall()
        finally:
            conn.close()

        # ── Ausgabe-Verifikation ────────────────────
        return _verify_rows("find_wiedervorlage_faellig", [dict(row) for row in rows], {
            "user_id": user_id, "character_id": character_id, "aktiv": True,
        })

    @staticmethod
    def run_fakten_decay(
        postgres_url: str,
        decay_rate:   float | None = None,
        stichtag:     datetime | None = None,
    ) -> dict:
        """Materialisiert `staerke_decay` und `decay_am` jeder aktiven Kante.

        Exponentieller Verfall ab dem letzten Schreiben, nach der Formel des
        Knotenverfalls (`lzg_knoten.run_node_decay`):

            staerke_decay = exp(−rate · Tage seit last_touched)

        Ein globaler Lauf über alle Paare — die Formel ist kantenlokal.

        **Der Lauf ändert `aktiv` nie.** `aktiv = FALSE` heißt in `fakten`
        *abgelöst* (bi-temporal), nicht *verblasst*; beides in einer Spalte
        machte eine schwache Kante von einer widerlegten ununterscheidbar. Ob
        eine schwache Kante ruht, entscheidet der Leser. Abgelöste Kanten
        bleiben unberührt.

        Vorbedingung: Die Rate ist nicht negativ; ein Stichtag trägt eine
            Zeitzone.
        Nachbedingung: Jede aktive Kante trägt decay_am = Stichtag und eine
            Stärke in [0, 1]. Ein zweiter Lauf am selben Stichtag schreibt
            dieselben Werte.
        Fehlerfälle: Ungültige Parameter und Datenbankfehler werden
            protokolliert und im Ergebnis benannt, nach einem Rollback — der
            Aufrufer schreibt daraus seinen Audit-Eintrag.

        Args:
            postgres_url: Verbindungsstring.
            decay_rate: Verfallsrate je Tag. None -> FAKTEN_DECAY_RATE.
            stichtag: Zeitpunkt, auf den gerechnet wird. None -> NOW() der
                Datenbank. Gesetzt für Zeugen und Messung.

        Returns:
            dict mit `verarbeitet` (int), `stichtag` (datetime | None) und
            `error` (str | None).
        """
        # ── Eingabe-Validierung ─────────────────────
        if decay_rate is None:
            decay_rate = FAKTEN_DECAY_RATE
        ergebnis: dict = {"verarbeitet": 0, "stichtag": None, "error": None}
        if decay_rate < 0:
            ergebnis["error"] = f"ungueltige Rate: {decay_rate}"
            logger.error("Fakten-Verfall abgebrochen: %s", ergebnis["error"])
            return ergebnis
        if stichtag is not None and stichtag.tzinfo is None:
            ergebnis["error"] = f"Stichtag ohne Zeitzone: {stichtag.isoformat()}"
            logger.error("Fakten-Verfall abgebrochen: %s", ergebnis["error"])
            return ergebnis

        # ── Verarbeitung ────────────────────────────
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COALESCE(%s::timestamptz, NOW())", (stichtag,))
                zeitpunkt: datetime = cur.fetchone()[0]
                # Vor dem Anker liegt kein Verfall: Ein last_touched hinter dem
                # Stichtag ergäbe sonst eine Stärke über 1.
                cur.execute(
                    """
                    UPDATE fakten
                    SET    staerke_decay = exp(-%s * GREATEST(0.0,
                               EXTRACT(EPOCH FROM (%s - last_touched)) / 86400.0)),
                           decay_am = %s
                    WHERE  aktiv = TRUE
                    """,
                    (decay_rate, zeitpunkt, zeitpunkt),
                )
                verarbeitet: int = cur.rowcount

                # ── Ausgabe-Verifikation ────────────────────
                # In derselben Transaktion: Eine Kante, die der Lauf verfehlt
                # hat oder deren Stärke aus [0, 1] fällt, nimmt ihn ganz zurück.
                cur.execute(
                    """
                    SELECT count(*) FROM fakten
                    WHERE  aktiv = TRUE
                      AND  (decay_am IS DISTINCT FROM %s
                            OR staerke_decay < 0 OR staerke_decay > 1)
                    """,
                    (zeitpunkt,),
                )
                abweichend: int = int(cur.fetchone()[0])
                if abweichend:
                    conn.rollback()
                    ergebnis["error"] = (
                        f"{abweichend} aktive Kanten nach dem Lauf nicht auf "
                        f"{zeitpunkt.isoformat()} oder ausserhalb [0, 1]"
                    )
                    logger.error("Fakten-Verfall zurückgenommen: %s", ergebnis["error"])
                    return ergebnis
            conn.commit()
        except psycopg2.Error as ex:
            conn.rollback()
            logger.exception("Fakten-Verfall fehlgeschlagen")
            ergebnis["error"] = f"{type(ex).__name__}: {ex}"
            return ergebnis
        finally:
            conn.close()

        ergebnis["verarbeitet"] = verarbeitet
        ergebnis["stichtag"] = zeitpunkt
        logger.info(
            "Fakten-Verfall abgeschlossen: %s aktive Kanten auf %s (rate=%.5f/Tag)",
            verarbeitet, zeitpunkt.isoformat(), decay_rate,
        )
        return ergebnis
