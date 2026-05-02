"""
Langzeitgedächtnis — PostgreSQL + pgvector.
Embedding-basierte semantische Suche mit Ebbinghaus-Decay.
"""

import logging
import math
from datetime import datetime, timezone

import psycopg2

from config              import EBBINGHAUS_DECAY_RATE
from graph.context_entry import ContextEntry

logger = logging.getLogger("ki_server.memory.lzg")


def effektives_gewicht_berechnen(
    gewicht:       float,
    verstaerkt_am: datetime,
    jetzt:         datetime | None = None,
    decay_rate:    float = EBBINGHAUS_DECAY_RATE,
) -> float:
    """
    Berechnet das effektive Gewicht unter Berücksichtigung
    des zeitlichen Verfalls nach Ebbinghaus.

    Das gespeicherte Gewicht dokumentiert die Verstärkungshistorie.
    Der Decay wird live berechnet, nie gespeichert.

    Formel: effektiv = gewicht * e^(-decay_rate * tage)
    """
    if jetzt is None:
        jetzt = datetime.now(timezone.utc)

    if verstaerkt_am.tzinfo is None:
        verstaerkt_am = verstaerkt_am.replace(tzinfo=timezone.utc)

    tage: float = max(0.0, (jetzt - verstaerkt_am).total_seconds() / 86400.0)
    decay: float = math.exp(-decay_rate * tage)

    return round(gewicht * decay, 4)


def lzg_entries_retrieve(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    embedding:    list[float],
    top_k:        int = 10
) -> list[ContextEntry]:
    """Holt die relevantesten LZG-Eintraege eines Paares als ContextEntry-Liste.

    Liefert strukturierte Daten ohne Format-Drumherum. Der Reducer
    dedupliziert auf dieser Ebene; der Formatter baut daraus den
    finalen memory_context-String fuer den Responder.

    Datenbeschaffung: pgvector-KNN-Suche auf der Tabelle
    `langzeitgedaechtnis`, paar-skopiert auf user_id/character_id,
    nur aktive Eintraege mit Embedding, Similarity-Schwelle 0.5,
    top_k Treffer. Filter, Schwellwerte und Index bleiben identisch
    zur Vorgaengerfunktion.

    Effektives Gewicht: Wird live ueber `effektives_gewicht_berechnen()`
    aus dem gespeicherten `gewicht` und `verstaerkt_am` (Ebbinghaus-Decay)
    bestimmt. Top-Level-Feld `gewicht` traegt das effektive Gewicht;
    das Basis-Gewicht der DB-Zeile bleibt zusaetzlich als
    `meta.gewicht_basis` erhalten.

    Mapping pro DB-Zeile auf ContextEntry:
      quelle  = "lzg" (Konstante)
      subtyp  = Spalte `dimension` (kognition / emotion / werte /
                interessen / kommunikation / kontext)
      inhalt  = Spalte `inhalt`
      gewicht = effektives Gewicht (live, mit Decay)
      meta    = {
          "arousal":       Spalte `arousal` (float),
          "vektor":        Spalte `emotions_vektor` (str),
          "beobachter":    Spalte `beobachter` (str),
          "dimension":     Spalte `dimension` (str — duplikativ zu
                           subtyp, laut Format-Vertrag explizit erwartet),
          "erstellt_am":   Spalte `erstellt_am` als Unix-Timestamp,
          "verstaerkt_am": Spalte `verstaerkt_am` als Unix-Timestamp,
          "haeufigkeit":   Spalte `haeufigkeit` (int),
          "gewicht_basis": Spalte `gewicht` (float, gespeichertes
                           Basis-Gewicht ohne Decay),
      }

    Args:
        postgres_url: Connection-String fuer die LZG-Datenbank.
        user_id:      Subjekt der Paar-Partition.
        character_id: Gegenueber der Paar-Partition.
        embedding:    Query-Vektor (768-dim) des aktuellen Prompts.
        top_k:        Maximale Treffer-Anzahl vor Similarity-Filter.

    Returns:
        Liste von ContextEntry-Dicts. Leer bei keinen Treffern oder Fehler.
    """

    logger.info(f"LZG-Entries-Retrieve: Paar={user_id}:{character_id}, Limit={top_k}")

    embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

    entries: list[ContextEntry] = []

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT inhalt, dimension, gewicht, arousal, emotions_vektor,
                   verstaerkt_am, beobachter, erstellt_am, haeufigkeit,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM langzeitgedaechtnis
            WHERE user_id = %s
              AND character_id = %s
              AND embedding IS NOT NULL
              AND aktiv = TRUE
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (embedding_str, user_id, character_id, embedding_str, top_k))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            logger.info("LZG-Entries-Retrieve: 0 Eintraege geliefert (Similarity-Filter angewendet)")
            return entries

        for (inhalt, dimension, gewicht_basis, arousal, emotions_vektor,
             verstaerkt_am, beobachter, erstellt_am, haeufigkeit, similarity) in rows:
            if similarity < 0.5:
                continue

            eff_gewicht: float = effektives_gewicht_berechnen(gewicht_basis, verstaerkt_am)

            erstellt_ts:   float = erstellt_am.timestamp()   if erstellt_am   else 0.0
            verstaerkt_ts: float = verstaerkt_am.timestamp() if verstaerkt_am else 0.0

            entry: ContextEntry = {
                "quelle":  "lzg",
                "subtyp":  dimension or "",
                "inhalt":  inhalt or "",
                "gewicht": eff_gewicht,
                "meta": {
                    "arousal":       float(arousal) if arousal is not None else 0.0,
                    "vektor":        emotions_vektor or "",
                    "beobachter":    beobachter or "",
                    "dimension":     dimension or "",
                    "erstellt_am":   erstellt_ts,
                    "verstaerkt_am": verstaerkt_ts,
                    "haeufigkeit":   int(haeufigkeit) if haeufigkeit is not None else 0,
                    "gewicht_basis": float(gewicht_basis) if gewicht_basis is not None else 0.0,
                },
            }
            entries.append(entry)

            logger.debug(
                f"LZG-Entry: dimension={entry['subtyp']}, "
                f"eff_gewicht={eff_gewicht:.2f}, inhalt-snippet={(inhalt or '')[:60]}"
            )

        logger.info(
            f"LZG-Entries-Retrieve: {len(entries)} Eintraege geliefert "
            f"(Similarity-Filter angewendet)"
        )
        return entries

    except Exception as fehler:
        logger.error(f"LZG-Entries-Retrieve fehlgeschlagen: {fehler}")
        return []
