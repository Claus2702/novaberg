"""Die Schreib- und Lesezugriffe auf `dateien_index`.

Spezifikation: docs/novaberg-agent-dateien_k.md §4, §5.5.

**Was hier geschrieben wird, sind Zeilen ueber Dateien — nie Dateien.**
Kein Schreibpfad ins Dateisystem, auch nicht mittelbar.
"""

import json
import logging

from agents.dateien_index.indizieren import Erschliessung
from agents.dateien_index.wandern import GRUENDE, GRUND_JE_FALL, Fund
from tools.db_manager import db_manager

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
    # `grund` gehoert dazu, seit der Wiedereintritt ihn braucht: Ein
    # Grabstein (`deleted`) mit anderem Hash ist eine Neuanlage, ein
    # ausgeschlossener (`excluded`) setzt fort (`_fall_bestimmen`).
    zeilen: list[dict] = db_manager.select(
        "SELECT id, pfad, groesse, inhalt_hash, geaendert_am, aktiv, grund "
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

    `aktiv` wird beim Schreiben ausdruecklich auf TRUE gesetzt: Eine Datei,
    die wieder auftaucht, ist damit ohne Sonderweg wieder da. `grund` und
    `grund_am` halten fest, **welcher** Uebergang das war und wann.

    **Bei `created` werden drei Spalten geraeumt.** `entitaet_ids`,
    `timeline_id` und `zuletzt_gelernt_hash` gehoeren der Datei, aus der sie
    gewonnen wurden. Trifft `created` eine bestehende Zeile, ist die alte
    Datei fort und eine andere liegt an ihrem Platz — dann waeren die drei
    Werte Aussagen ueber etwas, das es nicht mehr gibt. Der UPSERT liess
    sie bis zum 23.08.2026 stehen; folgenlos nur, weil keine der drei bis
    heute einen Schreiber hat (novaberg-bugs.md,
    DATEIINDEX-SPALTEN-OHNE-SCHREIBER). **Der erste Schreiber haette die
    Luecke scharf gemacht, und sie waere still gewesen.**
    """
    # ── Eingabe-Validierung ─────────────────────
    if not erschliessung.thema:
        logger.error(
            "Index: '%s' ohne Thema — keine Zeile geschrieben", fund.pfad_relativ,
        )
        return None

    # **Kein Ersatzwert.** Ein Fall, den `GRUND_JE_FALL` nicht kennt, ist ein
    # Defekt im Aufrufer und kein Grenzfall: `unveraendert` hierher zu geben
    # hiesse, eine Aenderung zu buchen, die niemand gemessen hat. Ein
    # `.get(..., GRUND_GEAENDERT)` haette genau das getan — still.
    if fund.fall not in GRUND_JE_FALL:
        logger.error(
            "Index: '%s' kommt mit Fall '%s' zum Schreiben — geschrieben "
            "werden nur %s. Keine Zeile geschrieben",
            fund.pfad_relativ, fund.fall, sorted(GRUND_JE_FALL),
        )
        return None
    grund: str = GRUND_JE_FALL[fund.fall]

    ergebnis: dict | None = db_manager.execute_returning(
        """
        INSERT INTO dateien_index
            (wurzel_id, pfad, name, thema, zusammenfassung, stichwoerter,
             themen_embedding, struktur, groesse, zeilen, inhalt_hash,
             geaendert_am, indiziert_am, aktiv, grund, grund_am, suchtext)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                to_timestamp(%s), NOW(), TRUE, %s, NOW(),
                to_tsvector('german', %s))
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
            grund            = EXCLUDED.grund,
            grund_am         = NOW(),
            -- Die Kette wird geschlossen: Eine Neuanlage erbt nichts von
            -- ihrem Vorgaenger. Bei `changed` bleiben die drei stehen —
            -- dieselbe Datei, neuer Inhalt.
            entitaet_ids     = CASE WHEN EXCLUDED.grund = 'created'
                                    THEN NULL ELSE dateien_index.entitaet_ids END,
            timeline_id      = CASE WHEN EXCLUDED.grund = 'created'
                                    THEN NULL ELSE dateien_index.timeline_id END,
            zuletzt_gelernt_hash = CASE WHEN EXCLUDED.grund = 'created'
                                    THEN NULL
                                    ELSE dateien_index.zuletzt_gelernt_hash END,
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
            fund.geaendert_am, grund, suchtext,
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


def stilllegen(zeilen_ids: list[int], grund: str) -> int:
    """Setzt Zeilen auf `aktiv = false` und haelt fest, warum.

    Vorbedingung: `zeilen_ids` sind Nummern aus `dateien_index`; `grund` ist
    `deleted` oder `excluded`.
    Nachbedingung: Die Zahl der geaenderten Zeilen. Weicht sie von der Zahl
    der uebergebenen Nummern ab, wird das gemeldet — eine Zeile, die nicht
    markiert wurde, sieht im Index aus wie eine vorhandene Datei.

    **Der Grund ist ein Parameter, seit es zwei gibt.** Die Vorgaengerin
    hiess `verschwunden_markieren` und konnte nur einen Ausgang kennen; sie
    schrieb `verschwunden_am` auch fuer Dateien, die dalagen und nur nicht
    mehr betrachtet wurden. Ein Name, der einen von zwei Faellen nennt, ist
    genau die Stelle, an der der zweite verschwindet.
    """
    # ── Eingabe-Validierung ─────────────────────
    if grund not in GRUENDE:
        logger.error(
            "Index: '%s' ist kein gueltiger Grund — keine Zeile stillgelegt", grund,
        )
        return 0
    if not zeilen_ids:
        return 0

    # ── Verarbeitung ────────────────────────────
    betroffen: int = db_manager.execute(
        "UPDATE dateien_index SET aktiv = FALSE, grund = %s, grund_am = NOW() "
        "WHERE id = ANY(%s) AND aktiv = TRUE",
        (grund, zeilen_ids),
    )

    # ── Ausgabe-Verifikation ────────────────────
    if betroffen != len(zeilen_ids):
        logger.error(
            "Index: %d Zeilen als '%s' gemeldet, %d stillgelegt — die "
            "Differenz steht weiter als vorhanden im Index",
            len(zeilen_ids), grund, betroffen,
        )
    else:
        logger.info("Index: %d Zeilen als '%s' stillgelegt", betroffen, grund)

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
