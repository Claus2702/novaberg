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
    EMOTION_SEKTOR_MAP,
    EMOTION_SYNONYM_MAP,
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


def anker_retrieval(
    postgres_url: str,
    user_id: str,
    character_id: str,
    embedding_str: str,
    *,
    top_k: int = 3,
    min_similarity: float = 0.5,
) -> list[dict]:
    """
    Initial-Retrieval des Synapsen-Lesepfads (Konzept §8.1): liefert die
    Top-K (default 3) Anker-Knoten einer Paar-Partition per pgvector-Cosine.

    Geladen werden nur aktive Knoten mit Embedding; nach dem Fetch werden
    Treffer unter min_similarity verworfen (ein schwacher Cosine ist kein
    sinnvoller Anker, analog zur 0.5-Schwelle des alten B2-Reads).

    Bewusster Unterschied zu kandidaten_mit_cosine_laden (die der Kanten-
    bildung §7.2 dient): hier zaehlt die aktuelle Praesenz, daher
    gewicht_decay statt gewicht_absolut (Konzept §8.3.1/§9.4), eine
    Similarity-Schwelle und ein Top-K-Limit. embedding selbst wird nicht
    zurueckgegeben (nur fuer die Sortierung genutzt).

    Rueckgabe: list[dict], nach Cosine absteigend, max top_k Eintraege ueber
    der Schwelle. Leere Liste bei keinen Treffern oder DB-Fehler.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    id,
                    inhalt,
                    dimension,
                    gewicht_decay,
                    emotion,
                    arousal,
                    themen,
                    entitaet_ids,
                    erstellt_am,
                    1 - (embedding <=> %s::vector) AS cosine
                FROM lzg_knoten
                WHERE user_id = %s
                  AND character_id = %s
                  AND aktiv = TRUE
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding_str, user_id, character_id, embedding_str, top_k),
            )
            roh = [dict(row) for row in cur.fetchall()]
        # Schwellen-Filter (§8.1): schwache Cosine-Treffer sind keine Anker.
        anker = [a for a in roh if a["cosine"] is not None and a["cosine"] >= min_similarity]
        logger.info(
            "Anker-Retrieval: paar=%s/%s anker=%d/%d (Schwelle %.2f) top_cosine=%.4f min_cosine=%.4f",
            user_id, character_id, len(anker), len(roh), min_similarity,
            anker[0]["cosine"] if anker else float("nan"),
            anker[-1]["cosine"] if anker else float("nan"),
        )
        for a in anker:
            logger.debug("Anker: knoten=%s cosine=%.4f gewicht_decay=%.3f",
                         a["id"], a["cosine"], a["gewicht_decay"])
        return anker
    except psycopg2.Error as exc:
        logger.error("anker_retrieval fehlgeschlagen paar=%s/%s: %s", user_id, character_id, exc)
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


def knoten_laden(postgres_url: str, knoten_id: int) -> Optional[dict]:
    """
    Laedt einen einzelnen Knoten mit seinem Timeline-Bezug in derselben Form
    wie ein Kandidat aus kandidaten_mit_cosine_laden (ohne cosine). Dient der
    Kantenbildung des frisch angelegten Knotens (Trigger 1): der neue Knoten
    muss fuer schichten_ermitteln dieselben Felder tragen wie die Kandidaten
    (gewicht_absolut, entitaet_ids, themen, timeline_praezision,
    timeline_event_time).

    Rueckgabe: Knoten-Dict oder None (nicht gefunden / Fehler).
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT k.id, k.gewicht_absolut, k.entitaet_ids, k.themen,
                       k.timeline_id,
                       t.event_time AS timeline_event_time,
                       t.precision  AS timeline_praezision
                FROM lzg_knoten k
                LEFT JOIN timeline t ON t.id = k.timeline_id
                WHERE k.id = %s
                """,
                (knoten_id,),
            )
            zeile = cur.fetchone()
        if zeile is None:
            logger.error("knoten_laden: Knoten %s nicht gefunden", knoten_id)
            return None
        return dict(zeile)
    except psycopg2.Error as exc:
        logger.error("knoten_laden fehlgeschlagen id=%s: %s", knoten_id, exc)
        return None
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# Synapsen-Lesepfad — Spreading-Activation (Synapsen P5, Konzept §8.2/§8.3)
# ════════════════════════════════════════════════════════════════════════
# Das Sortier-Gewicht einer Erinnerung ist gewicht_decay × SCHALEN_FAKTOR ×
# Plutchik-Sektor-Faktor (§8.3.1). Die folgenden Modul-Konstanten parametrieren
# die Geometrie des Schweifens.

# Daempfung pro Schale (Sprung-Distanz vom Anker): direkte Treffer voll,
# entferntere Assoziationen zunehmend gedaempft (§8.3.1).
SCHALEN_FAKTOR: dict[int, float] = {0: 1.0, 1: 0.75, 2: 0.50, 3: 0.25}

# K pro Schale (§8.2.2): wie viele staerkste Kanten pro Knoten je Sprung
# verfolgt werden. Schale 1 faechert breiter auf als die tieferen Schalen.
K_PRO_TIEFE: dict[int, int] = {0: 0, 1: 3, 2: 2, 3: 2}

# Ring-Abstand (0-4) zweier Plutchik-Sektoren -> Affinitaets-Faktor (§8.3.1).
SEKTOR_ABSTAND_FAKTOR: dict[int, float] = {0: 1.0, 1: 0.9, 2: 0.8, 3: 0.7, 4: 0.6}


def _sektor_faktor(emotion_a: str, emotion_b: str) -> float:
    """
    Plutchik-Affinitaet zweier Emotionen (§8.3.1): wie aehnlich faerbt die
    aktuelle Stimmung (a) eine erinnerte Emotion (b).

    Beide Labels werden via EMOTION_SYNONYM_MAP kanonisiert und ueber
    EMOTION_SEKTOR_MAP auf ihren Plutchik-Sektor (1-8) abgebildet. Hat eine
    Seite keinen Sektor (neutral/leer/unbekannt), faerbt sie nicht: Faktor 1.0
    ("Sachliches Denken faerbt Erinnerungen nicht").

    Der Ring-Abstand wird hier selbst gerechnet (min(|d|, 8-|d|)), weil
    EMOTION_SEKTOR_DISTANZ aus config.py Normalisierungs-Exponenten liefert,
    nicht den reinen Ring-Abstand.
    """
    def _sektor(emotion: str) -> Optional[int]:
        label = (emotion or "").strip().lower()
        if not label or label == "neutral":
            return None
        label = EMOTION_SYNONYM_MAP.get(label, label)
        return EMOTION_SEKTOR_MAP.get(label)

    sektor_a = _sektor(emotion_a)
    sektor_b = _sektor(emotion_b)
    if sektor_a is None or sektor_b is None:
        return 1.0
    direkt = abs(sektor_a - sektor_b)
    abstand = min(direkt, 8 - direkt)
    return SEKTOR_ABSTAND_FAKTOR[abstand]


def _kanten_nachbarn(
    postgres_url: str,
    knoten_id: int,
    vorgaenger_knoten_id: Optional[int],
    top_k: int,
) -> list[dict]:
    """
    Laedt die staerksten AUSGEHENDEN Kanten eines Knotens fuer das Spreading
    (§8.2.2).

    lzg_kanten ist gerichtet (knoten_a_id = Quelle, knoten_b_id = Ziel; A->B
    und B->A sind separate Zeilen mit verschiedenen Gewichten). Es werden nur
    ausgehende Kanten verfolgt (knoten_a_id = X); der Nachbar ist stets das
    Ziel knoten_b_id. Die Vorgaenger-Sperre (§8.2.3) verhindert den direkten
    Ruecksprung: die ausgehende Kante, deren Ziel der Vorgaenger-Knoten ist,
    wird ausgeschlossen (vorgaenger_knoten_id, falls gesetzt). Der Ruecksprung
    B->A ist eine eigene gerichtete Kante, daher knoten- statt kanten-id-basiert.
    Kanten-Gewicht ist gewicht_absolut (§8.2.2/§9.5: Kanten referenzieren die
    Anker-Staerke), absteigend sortiert, max top_k.

    Rueckgabe pro Nachbar-Kante: {nachbar_knoten_id, kante_id, gewicht_absolut,
    verbindungs_gruende, geteilte_entitaet_ids, geteilte_themen}. Leere Liste
    bei DB-Fehler.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, knoten_a_id, knoten_b_id, gewicht_absolut,
                       verbindungs_gruende, geteilte_entitaet_ids, geteilte_themen
                FROM lzg_kanten
                WHERE knoten_a_id = %s
                  AND (%s::int IS NULL OR knoten_b_id <> %s::int)
                ORDER BY gewicht_absolut DESC
                LIMIT %s
                """,
                (knoten_id, vorgaenger_knoten_id, vorgaenger_knoten_id, top_k),
            )
            kanten = [dict(row) for row in cur.fetchall()]
        nachbarn: list[dict] = []
        for kante in kanten:
            # Gerichtete Kante: knoten_a_id = X (Quelle), Nachbar = Ziel knoten_b_id.
            nachbarn.append({
                "nachbar_knoten_id":     kante["knoten_b_id"],
                "kante_id":              kante["id"],
                "gewicht_absolut":       kante["gewicht_absolut"],
                "verbindungs_gruende":   kante["verbindungs_gruende"],
                "geteilte_entitaet_ids": kante["geteilte_entitaet_ids"],
                "geteilte_themen":       kante["geteilte_themen"],
            })
        logger.debug("Kanten-Nachbarn: knoten=%s vorgaenger=%s -> %d ausgehende Nachbarn",
                     knoten_id, vorgaenger_knoten_id, len(nachbarn))
        return nachbarn
    except psycopg2.Error as exc:
        logger.error("_kanten_nachbarn fehlgeschlagen knoten=%s: %s", knoten_id, exc)
        return []
    finally:
        conn.close()


def _knoten_details_laden(postgres_url: str, knoten_id: int) -> Optional[dict]:
    """
    Laedt die Lesepfad-Detailfelder eines Knotens (§8.4.2 Erinnerungs-Ebene):
    id, inhalt, dimension, gewicht_decay, emotion, arousal, themen,
    entitaet_ids, erstellt_am. Nur aktive Knoten (§8.3.1).

    Eigene Quelle statt knoten_laden, weil knoten_laden fuer die Kantenbildung
    gewicht_absolut (ohne emotion/inhalt) liefert; der Lesepfad braucht die
    aktuelle Praesenz gewicht_decay und die emotionalen/inhaltlichen Felder.

    Rueckgabe: Knoten-Dict oder None (inaktiv, geloescht oder DB-Fehler).
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, inhalt, dimension, gewicht_decay, emotion,
                       arousal, themen, entitaet_ids, erstellt_am
                FROM lzg_knoten
                WHERE id = %s AND aktiv = TRUE
                """,
                (knoten_id,),
            )
            zeile = cur.fetchone()
        if zeile is None:
            logger.debug("_knoten_details_laden: Knoten %s nicht gefunden/inaktiv", knoten_id)
            return None
        return dict(zeile)
    except psycopg2.Error as exc:
        logger.error("_knoten_details_laden fehlgeschlagen id=%s: %s", knoten_id, exc)
        return None
    finally:
        conn.close()


def _sortier_gewicht(
    gewicht_decay: float,
    schale: int,
    nova_emotion: str,
    knoten_emotion: str,
) -> float:
    """
    Sortier-Gewicht einer Erinnerung im Lesepfad (§8.3.1):
    gewicht_decay × SCHALEN_FAKTOR[schale] × _sektor_faktor(nova, knoten).
    """
    return (
        (gewicht_decay or 0.0)
        * SCHALEN_FAKTOR.get(schale, 0.0)
        * _sektor_faktor(nova_emotion, knoten_emotion)
    )


def spreading_lesen(
    postgres_url: str,
    user_id: str,
    character_id: str,
    embedding_str: str,
    cluster: str,
    nova_emotion: str,
    *,
    anker_anzahl: int = 3,
) -> list[dict]:
    """
    Herzstueck des Synapsen-Lesepfads (Konzept §8.2/§8.3): holt die Anker
    (anker_retrieval, Schale 0), schweift cluster-abhaengig tief ueber
    lzg_kanten (Spreading-Activation mit Vorgaenger-Sperre und K pro Schale),
    gewichtet (gewicht_decay × Schale × Plutchik-Sektor), dedupliziert mit
    Schalen-Praeferenz und liefert die Top-3 Erinnerungen inklusive
    Pfad-Information (§8.4.2 Erinnerungs-Ebene).

    Die umgebende State-Struktur (sprung_tiefe, cluster, nova_sektor, ...) baut
    der Enricher (Teil 4); diese Funktion liefert nur die Erinnerungs-Liste.
    Leerer Anker-Pool (kein Cosine-Treffer) -> leere Liste (Cold-Start).
    """
    from ei.dreischicht import CLUSTER_ENRICHER_SPRUENGE

    # 1. Sprung-Tiefe aus dem GV-Cluster (Default 1 = paradox-Fallback bei
    #    unbekanntem Cluster).
    tiefe = CLUSTER_ENRICHER_SPRUENGE.get(cluster, 1)

    # 2. Anker (Schale 0). Kein Treffer -> sauberer Cold-Start.
    anker = anker_retrieval(
        postgres_url, user_id, character_id, embedding_str, top_k=anker_anzahl
    )
    if not anker:
        logger.info("Spreading-Lesen: 0 Anker (Cold-Start) paar=%s/%s cluster=%s",
                    user_id, character_id, cluster)
        return []

    pool: list[dict] = []
    for a in anker:
        pool.append({
            "knoten_id":         a["id"],
            "inhalt":            a.get("inhalt"),
            "themen":            a.get("themen"),
            "entitaet_ids":      a.get("entitaet_ids"),
            "emotion":           a.get("emotion") or "",
            "erstellt_am":       a.get("erstellt_am"),
            "gewicht_decay":     a.get("gewicht_decay") or 0.0,
            "schale":            0,
            "pfad":              [],
            "vorgaenger_knoten_id": None,
        })

    # 4. Spreading-Schleife Schale 1..tiefe. Von jedem Knoten der Vorschale aus
    #    die K staerksten ausgehenden Kanten verfolgen; der Ruecksprung zum
    #    Vorgaenger-Knoten ist gesperrt.
    vorschale: list[dict] = list(pool)
    for schale in range(1, tiefe + 1):
        k = K_PRO_TIEFE.get(schale, 0)
        naechste: list[dict] = []
        for knoten in vorschale:
            nachbarn = _kanten_nachbarn(
                postgres_url, knoten["knoten_id"],
                vorgaenger_knoten_id=knoten["vorgaenger_knoten_id"], top_k=k,
            )
            for nachbar in nachbarn:
                detail = _knoten_details_laden(postgres_url, nachbar["nachbar_knoten_id"])
                if detail is None:
                    continue  # inaktiv/geloescht -> Sackgasse, kein Fehler
                schritt = {
                    "von_knoten_id":         knoten["knoten_id"],
                    "kante_id":              nachbar["kante_id"],
                    "verbindungs_gruende":   nachbar["verbindungs_gruende"],
                    "geteilte_entitaet_ids": nachbar["geteilte_entitaet_ids"],
                    "geteilte_themen":       nachbar["geteilte_themen"],
                }
                naechste.append({
                    "knoten_id":         detail["id"],
                    "inhalt":            detail.get("inhalt"),
                    "themen":            detail.get("themen"),
                    "entitaet_ids":      detail.get("entitaet_ids"),
                    "emotion":           detail.get("emotion") or "",
                    "erstellt_am":       detail.get("erstellt_am"),
                    "gewicht_decay":     detail.get("gewicht_decay") or 0.0,
                    "schale":            schale,
                    "pfad":              knoten["pfad"] + [schritt],
                    "vorgaenger_knoten_id": knoten["knoten_id"],
                })
        pool.extend(naechste)
        vorschale = naechste
        if not vorschale:
            break  # nichts Neues erreicht -> tiefer schweifen sinnlos

    groesse_vor_dedup = len(pool)

    # 5. Dedup mit Schalen-Praeferenz (§8.3.2): pro knoten_id den Eintrag mit
    #    der kleinsten Schale behalten; bei Gleichstand den ersten.
    bestes: dict[int, dict] = {}
    for eintrag in pool:
        vorhanden = bestes.get(eintrag["knoten_id"])
        if vorhanden is None or eintrag["schale"] < vorhanden["schale"]:
            bestes[eintrag["knoten_id"]] = eintrag
    dedup = list(bestes.values())

    # 6. Sortier-Gewicht je Eintrag.
    for eintrag in dedup:
        eintrag["sortier_gewicht"] = _sortier_gewicht(
            eintrag["gewicht_decay"], eintrag["schale"], nova_emotion, eintrag["emotion"]
        )

    # 7. Absteigend nach Sortier-Gewicht, Top 3.
    dedup.sort(key=lambda e: e["sortier_gewicht"], reverse=True)
    top = dedup[:3]

    # 8. Erinnerungs-Ebene (§8.4.2) mit Rang.
    ergebnis: list[dict] = []
    for rang, eintrag in enumerate(top, start=1):
        ergebnis.append({
            "rang":            rang,
            "knoten_id":       eintrag["knoten_id"],
            "inhalt":          eintrag["inhalt"],
            "themen":          eintrag["themen"],
            "entitaet_ids":    eintrag["entitaet_ids"],
            "emotion":         eintrag["emotion"],
            "erstellt_am":     eintrag["erstellt_am"],
            "gewicht_decay":   eintrag["gewicht_decay"],
            "schale":          eintrag["schale"],
            "sortier_gewicht": eintrag["sortier_gewicht"],
            "pfad":            eintrag["pfad"],
        })

    logger.info(
        "Spreading-Lesen: paar=%s/%s cluster=%s tiefe=%d anker=%d "
        "pool_vor_dedup=%d nach_dedup=%d top=%d",
        user_id, character_id, cluster, tiefe, len(anker),
        groesse_vor_dedup, len(dedup), len(ergebnis),
    )
    for eintrag in ergebnis:
        logger.info("  Top-%d knoten=%s schale=%d sortier_gewicht=%.4f",
                    eintrag["rang"], eintrag["knoten_id"],
                    eintrag["schale"], eintrag["sortier_gewicht"])
    return ergebnis
