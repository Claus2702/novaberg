"""
LZG-Knoten — CRUD, Match-Erkennung und Reinforcement fuer das Synapsen-LZG.

Jeder promotete KZG-Eintrag wird zu einem eigenstaendigen lzg_knoten (Konzept
§2.1: Knoten erhalten, Aggregate vermeiden). Der Standardfall ist Knoten-Erhalt
— nur bei einer echten Quasi-Dublette (Hybrid Magnet + Vector, K10) wird der
bestehende Knoten verstaerkt statt eines neuen angelegt.

Dieses Modul kapselt:
  - die Daempfung gewicht_roh -> gewicht_absolut
  - das Anlegen eines Knotens (gewicht_roh = KZG-Salienz, K8)
  - das Laden der Kandidaten-Knoten einer Paar-Partition mit vorab in SQL
    berechneter Cosine-Similarity und allen Magnet-Feldern (dient sowohl der
    Match-Erkennung als auch der Kantenbildung)
  - das Reinforcement eines Knotens bei Match (Boost, Haeufigkeit, Zeitstempel)

Hausstil mirrort memory/lzg.py: synchrone psycopg2-Verbindung, deutsche
Docstrings (ae/oe/ue-Transliteration), logger.info/error an DB-Operationen.
"""

import logging
import math
from typing import Optional

import psycopg2
import psycopg2.extras

from config import (
    LZG_KNOTEN_GEWICHT_CAP,
    LZG_KNOTEN_DAEMPFUNG_EXP,
    LZG_KNOTEN_REINFORCEMENT_BOOST,
    LZG_KNOTEN_MATCH_SCHWELLE,
)

logger = logging.getLogger(__name__)


def gewicht_absolut_berechnen(gewicht_roh: float) -> float:
    """
    Daempft das frei wachsende gewicht_roh auf den gekappten Anker-Wert
    gewicht_absolut (Konzept §5.4 Schritt 5 / §7.9.1 Schritt 8).

    Formel: cap * sin(min(roh/cap, 1) * pi/2) ** exp
    """
    anteil = min(gewicht_roh / LZG_KNOTEN_GEWICHT_CAP, 1.0)
    return LZG_KNOTEN_GEWICHT_CAP * (math.sin(anteil * math.pi / 2) ** LZG_KNOTEN_DAEMPFUNG_EXP)


def knoten_anlegen(
    postgres_url: str,
    *,
    kzg_quell_key: str,
    user_id: str,
    character_id: str,
    beobachter: str,
    inhalt: str,
    embedding_str: str,
    dimension: str,
    gewicht_roh: float,
    kzg_erstellt_am: float,
    themen: list[str],
    gedaechtnistyp: Optional[str],
    entitaet_ids: list[int],
    timeline_id: Optional[int],
    emotion: str = "",
    arousal: float = 0.5,
    emotions_vektor: str = "",
    intentionen: str = "[]",
    modus: str = "",
    sprach_stil: str = "",
    beziehungs_dynamik: str = "",
    tone: str = "",
) -> Optional[int]:
    """
    Legt einen neuen lzg_knoten an und liefert die neue id.

    gewicht_roh wird direkt aus der KZG-Salienz uebernommen (K8). Daraus werden
    gewicht_absolut (gedaempft) und gewicht_decay (initial = gewicht_absolut)
    berechnet. embedding_str ist die pgvector-Literal-Darstellung "[v1,v2,...]".
    kzg_erstellt_am ist ein Unix-Timestamp (Float) -> TIMESTAMPTZ via to_timestamp.

    Rueckgabe: neue Knoten-id oder None bei Fehler.
    """
    gewicht_absolut = gewicht_absolut_berechnen(gewicht_roh)
    gewicht_decay = gewicht_absolut
    themen_pg = themen or []
    entitaet_ids_pg = entitaet_ids or []

    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO lzg_knoten (
                    kzg_quell_key, user_id, character_id, beobachter,
                    inhalt, embedding, dimension,
                    gewicht_roh, gewicht_absolut, gewicht_decay,
                    kzg_erstellt_am,
                    themen, gedaechtnistyp, entitaet_ids, timeline_id,
                    emotion, arousal, emotions_vektor, intentionen,
                    modus, sprach_stil, beziehungs_dynamik, tone
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s::vector, %s,
                    %s, %s, %s,
                    to_timestamp(%s),
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    kzg_quell_key, user_id, character_id, beobachter,
                    inhalt, embedding_str, dimension,
                    gewicht_roh, gewicht_absolut, gewicht_decay,
                    kzg_erstellt_am,
                    themen_pg, gedaechtnistyp, entitaet_ids_pg, timeline_id,
                    emotion, arousal, emotions_vektor, intentionen,
                    modus, sprach_stil, beziehungs_dynamik, tone,
                ),
            )
            neue_id = cur.fetchone()[0]
        conn.commit()
        logger.info(
            "lzg_knoten angelegt: id=%s quell=%s roh=%.3f absolut=%.3f entitaeten=%s themen=%d",
            neue_id, kzg_quell_key, gewicht_roh, gewicht_absolut, entitaet_ids_pg, len(themen_pg),
        )
        return neue_id
    except psycopg2.Error as exc:
        conn.rollback()
        logger.error("knoten_anlegen fehlgeschlagen quell=%s: %s", kzg_quell_key, exc)
        return None
    finally:
        conn.close()


def kandidaten_mit_cosine_laden(
    postgres_url: str,
    user_id: str,
    character_id: str,
    embedding_str: str,
    *,
    ausschluss_id: Optional[int] = None,
) -> list[dict]:
    """
    Laedt alle aktiven Knoten der Paar-Partition (user_id, character_id) mit
    ihren Magnet-Feldern, dem Timeline-Bezug (event_time, precision) und der in
    SQL berechneten Cosine-Similarity zum uebergebenen Embedding.

    Dient zwei Zwecken in einem Query (Konzept §7.2 Schritt 2):
      - Match-Erkennung: hoechste Cosine >= LZG_KNOTEN_MATCH_SCHWELLE -> Dublette
      - Kantenbildung: vollstaendige Kandidaten-Liste fuer die vier Schichten

    Cosine = 1 - Cosine-Distanz (pgvector-Operator '<=>'). Sortiert absteigend
    nach Cosine.

    Hinweis: K10 sieht einen Magnet-Vorfilter zur Verkleinerung des Vector-
    Rerank-Pools vor. Fuer ein Einzel-Nutzer-System wird hier bewusst die
    vollstaendige aktive Partition geladen, weil die Kantenbildung ohnehin alle
    Kandidaten braucht. Der Vorfilter ist eine spaetere Optimierung.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT k.id, k.gewicht_absolut, k.entitaet_ids, k.themen,
                       k.timeline_id,
                       t.event_time AS timeline_event_time,
                       t.precision  AS timeline_praezision,
                       1 - (k.embedding <=> %s::vector) AS cosine
                FROM lzg_knoten k
                LEFT JOIN timeline t ON t.id = k.timeline_id
                WHERE k.user_id = %s AND k.character_id = %s AND k.aktiv = TRUE
                  AND (%s::int IS NULL OR k.id <> %s::int)
                ORDER BY cosine DESC
                """,
                (embedding_str, user_id, character_id, ausschluss_id, ausschluss_id),
            )
            kandidaten = [dict(row) for row in cur.fetchall()]
        logger.info(
            "Kandidaten geladen: paar=%s/%s anzahl=%d top_cosine=%.4f",
            user_id, character_id, len(kandidaten),
            kandidaten[0]["cosine"] if kandidaten else float("nan"),
        )
        return kandidaten
    except psycopg2.Error as exc:
        logger.error("kandidaten_mit_cosine_laden fehlgeschlagen paar=%s/%s: %s", user_id, character_id, exc)
        return []
    finally:
        conn.close()


def match_pruefen(kandidaten: list[dict]) -> Optional[dict]:
    """
    Prueft, ob unter den (nach Cosine sortierten) Kandidaten eine Quasi-Dublette
    liegt (K10). Liefert den hoechsten Kandidaten mit Cosine >=
    LZG_KNOTEN_MATCH_SCHWELLE, sonst None.

    Bewusst hohe Schwelle: Standardfall ist Knoten-Erhalt, nur echte Identitaet
    verstaerkt. Erwartet absteigend nach Cosine sortierte Kandidaten.
    """
    if not kandidaten:
        return None
    top = kandidaten[0]
    if top.get("cosine") is not None and top["cosine"] >= LZG_KNOTEN_MATCH_SCHWELLE:
        logger.info("Match erkannt: knoten=%s cosine=%.4f (Schwelle %.2f) -> Reinforcement",
                    top["id"], top["cosine"], LZG_KNOTEN_MATCH_SCHWELLE)
        return top
    logger.info("Kein Match: top_cosine=%.4f < Schwelle %.2f -> Neuanlage",
                top.get("cosine") if top.get("cosine") is not None else float("nan"),
                LZG_KNOTEN_MATCH_SCHWELLE)
    return None


def knoten_verstaerken(postgres_url: str, knoten_id: int) -> Optional[float]:
    """
    Reinforcement-Pfad bei Match (K10): gewicht_roh += BOOST, gewicht_absolut
    neu daempfen, haeufigkeit += 1, verstaerkt_am = NOW(). Liefert das neue
    gewicht_absolut (Eingabe fuer Trigger 2, Kanten-Neuberechnung) oder None
    bei Fehler.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT gewicht_roh FROM lzg_knoten WHERE id = %s", (knoten_id,))
            zeile = cur.fetchone()
            if zeile is None:
                logger.error("knoten_verstaerken: Knoten %s nicht gefunden", knoten_id)
                return None
            neuer_roh = zeile[0] + LZG_KNOTEN_REINFORCEMENT_BOOST
            neuer_absolut = gewicht_absolut_berechnen(neuer_roh)
            cur.execute(
                """
                UPDATE lzg_knoten
                SET gewicht_roh = %s,
                    gewicht_absolut = %s,
                    gewicht_decay = %s,
                    haeufigkeit = haeufigkeit + 1,
                    verstaerkt_am = NOW()
                WHERE id = %s
                """,
                (neuer_roh, neuer_absolut, neuer_absolut, knoten_id),
            )
        conn.commit()
        logger.info("Knoten verstaerkt: id=%s roh=%.3f absolut=%.3f (+Boost %.2f)",
                    knoten_id, neuer_roh, neuer_absolut, LZG_KNOTEN_REINFORCEMENT_BOOST)
        return neuer_absolut
    except psycopg2.Error as exc:
        conn.rollback()
        logger.error("knoten_verstaerken fehlgeschlagen id=%s: %s", knoten_id, exc)
        return None
    finally:
        conn.close()
