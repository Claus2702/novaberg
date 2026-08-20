"""Die Schreib- und Lesezugriffe auf `dateien_index`.

Spezifikation: docs/novaberg-agent-dateien_k.md §4, §5.5.

**Was hier geschrieben wird, sind Zeilen ueber Dateien — nie Dateien.**
Kein Schreibpfad ins Dateisystem, auch nicht mittelbar.
"""

import json
import logging

from tools.db_manager import db_manager

from agents.dateien_index.indizieren import Erschliessung
from agents.dateien_index.wandern import Fund

logger = logging.getLogger("ki_server.agents.dateien_index.speicher")


def wurzeln_aktiv() -> list[dict]:
    """Liest die Freigaben, die der Waechter abzulaufen hat.

    Vorbedingung: keine.
    Nachbedingung: Liste der aktiven Wurzeln ueber **alle** Paare. Der
    Waechter ist ein Wartungslauf und kein Turn — er arbeitet nicht fuer
    ein Paar, sondern fuer den Bestand.
    """
    return db_manager.select(
        "SELECT id, user_id, character_id, pfad, bezeichnung FROM dateien_wurzeln "
        "WHERE aktiv = TRUE ORDER BY id",
    )


def bestand_je_wurzel(wurzel_id: int) -> dict[str, dict]:
    """Liest den Index einer Wurzel als Abbildung Pfad → Zeile.

    Vorbedingung: `wurzel_id` bezeichnet eine Freigabe.
    Nachbedingung: Ein Woerterbuch; leer, wenn noch nichts indiziert ist.
    **Auch die stillgelegten Zeilen sind darin** — eine wiederaufgetauchte
    Datei muss als dieselbe erkennbar sein (§5.5).
    """
    zeilen: list[dict] = db_manager.select(
        "SELECT id, pfad, groesse, inhalt_hash, geaendert_am, aktiv "
        "FROM dateien_index WHERE wurzel_id = %s",
        (wurzel_id,),
    )
    return {zeile["pfad"]: zeile for zeile in zeilen}


def zeile_schreiben(
    wurzel_id: int, fund: Fund, erschliessung: Erschliessung, suchtext: str,
) -> int | None:
    """Legt eine Indexzeile an oder bringt sie auf den neuen Stand.

    Vorbedingung: `erschliessung.thema` ist nicht leer — eine Zeile ohne
    Thema behauptete eine Erschliessung, die nicht stattgefunden hat.
    Nachbedingung: Die Nummer der Zeile, oder None mit Fehlermeldung.
    Der Aufruf ist **idempotent** ueber (`wurzel_id`, `pfad`): Ein zweiter
    Lauf ueber dieselbe unveraenderte Datei erzeugt keine zweite Zeile.

    `aktiv` wird beim Schreiben ausdruecklich auf TRUE gesetzt und
    `verschwunden_am` geleert: Eine Datei, die wieder auftaucht, ist damit
    ohne Sonderweg wieder da.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not erschliessung.thema:
        logger.error(
            "Index: '%s' ohne Thema — keine Zeile geschrieben", fund.pfad_relativ,
        )
        return None

    ergebnis: dict | None = db_manager.execute_returning(
        """
        INSERT INTO dateien_index
            (wurzel_id, pfad, name, thema, zusammenfassung, stichwoerter,
             themen_embedding, struktur, groesse, zeilen, inhalt_hash,
             geaendert_am, indiziert_am, aktiv, verschwunden_am, suchtext)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                to_timestamp(%s), NOW(), TRUE, NULL, to_tsvector('german', %s))
        ON CONFLICT (wurzel_id, pfad) DO UPDATE SET
            name             = EXCLUDED.name,
            thema            = EXCLUDED.thema,
            zusammenfassung  = EXCLUDED.zusammenfassung,
            stichwoerter     = EXCLUDED.stichwoerter,
            themen_embedding = EXCLUDED.themen_embedding,
            struktur         = EXCLUDED.struktur,
            groesse          = EXCLUDED.groesse,
            zeilen           = EXCLUDED.zeilen,
            inhalt_hash      = EXCLUDED.inhalt_hash,
            geaendert_am     = EXCLUDED.geaendert_am,
            indiziert_am     = NOW(),
            aktiv            = TRUE,
            verschwunden_am  = NULL,
            suchtext         = EXCLUDED.suchtext
        RETURNING id
        """,
        (
            wurzel_id, fund.pfad_relativ, fund.name,
            erschliessung.thema, erschliessung.zusammenfassung,
            erschliessung.stichwoerter,
            erschliessung.embedding,
            # SQL-NULL statt JSON-"null": Die Spalte unterscheidet damit
            # "nicht erhoben" von der leeren Karte, und zwar in derselben
            # Form wie jede andere nicht erhobene Groesse des Schemas.
            None if erschliessung.struktur is None
            else json.dumps(erschliessung.struktur, ensure_ascii=False),
            fund.groesse, fund.zeilen, fund.inhalt_hash,
            fund.geaendert_am, suchtext,
        ),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not ergebnis or not ergebnis.get("id"):
        logger.error(
            "Index: Schreiben von '%s' lieferte keine Nummer — ein gelungener "
            "Aufruf ist nicht dasselbe wie eine geschriebene Zeile",
            fund.pfad_relativ,
        )
        return None

    return ergebnis["id"]


def verschwunden_markieren(zeilen_ids: list[int]) -> int:
    """Setzt verschwundene Dateien auf `aktiv = false`, ohne sie zu loeschen.

    Vorbedingung: `zeilen_ids` sind Nummern aus `dateien_index`.
    Nachbedingung: Die Zahl der geaenderten Zeilen. Weicht sie von der Zahl
    der uebergebenen Nummern ab, wird das gemeldet — eine Zeile, die nicht
    markiert wurde, sieht im Index aus wie eine vorhandene Datei.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not zeilen_ids:
        return 0

    # ── Verarbeitung ────────────────────────────
    betroffen: int = db_manager.execute(
        "UPDATE dateien_index SET aktiv = FALSE, verschwunden_am = NOW() "
        "WHERE id = ANY(%s) AND aktiv = TRUE",
        (zeilen_ids,),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if betroffen != len(zeilen_ids):
        logger.error(
            "Index: %d Zeilen als verschwunden gemeldet, %d markiert — die "
            "Differenz steht weiter als vorhanden im Index",
            len(zeilen_ids), betroffen,
        )
    else:
        logger.info("Index: %d Zeilen als verschwunden markiert", betroffen)

    return betroffen


def suchtext_bauen(erschliessung: Erschliessung, fund: Fund) -> str:
    """Setzt den lexikalischen Kanal aus dem zusammen, was erhoben wurde.

    Vorbedingung: `erschliessung.thema` ist nicht leer.
    Nachbedingung: Ein Text aus Name, Thema, Zusammenfassung und
    Stichwoertern — **rekonstruierbar aus dem persistierten Zustand**, wie
    es die Embedding-Konvention fuer jeden abgeleiteten Text verlangt.
    Der Dateiinhalt gehoert ausdruecklich nicht hinein: Der Index ist die
    Karte, nicht der Inhalt.
    """
    teile: list[str] = [
        fund.name,
        erschliessung.thema,
        erschliessung.zusammenfassung,
        " ".join(erschliessung.stichwoerter),
    ]
    return "\n".join(teil for teil in teile if teil)
