"""
GV4: Wissensluecken — semantisch nahe, aber unbesprochene Konzepte.

Durchsucht LZG (PostgreSQL/pgvector) und KZG (Redis/RediSearch).
Berechnet Relevanz aus 6 Systemen: Gedaechtnis, Aktualitaet, Drive,
Neugier, Register, Charakter.
Konzept: Chat 71 — validiert über 58-Testfälle-Matrix.
"""

import logging

import numpy as np
import psycopg2

from config import (
    POSTGRES_URL,
    EMBED_MODEL,
    ollama_gpu_client,
    redis_client,
    GV_LUECKEN_MAX,
    GV_LUECKEN_MIN_RELEVANZ,
    GV_NEUGIER_BOOST_SCHWELLE,
    GV_CHARAKTER_RESONANZ_SCHWELLE,
    GV_QUELLEN_FAKTOR,
    GV_LUECKEN_SIM_OBERGRENZE,
)
from graph.state import ConversationState
from services.model_services import model_service, EmbedRequest
from ei.utils import cosine_similarity
from ei.neugier import register_kompatibilitaet

logger = logging.getLogger("ki_server.ei.wissensluecken")


def ist_bereits_erwaehnt(inhalt: str, session_turns: list[dict]) -> bool:
    """Prueft ob der Inhalt einer Luecke bereits in der Session erwaehnt wurde.

    Einfacher Token-Overlap: Wenn mehr als 40% der Woerter des Inhalts
    in den letzten 8 Session-Turns vorkommen, gilt es als bereits besprochen.
    """
    if not session_turns:
        return False

    inhalt_woerter: set[str] = {
        w.lower() for w in inhalt.split() if len(w) > 3
    }
    if not inhalt_woerter:
        return False

    session_text: str = " ".join(
        turn.get("inhalt", "") for turn in session_turns[-8:]
    ).lower()

    treffer: int = sum(1 for w in inhalt_woerter if w in session_text)
    overlap: float = treffer / len(inhalt_woerter)
    return overlap > 0.4


def lzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
) -> list[dict]:
    """Sucht semantisch nahe Eintraege im LZG via pgvector.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht, gap_arousal, quelle.
    """
    kandidaten: list[dict] = []

    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        embedding_str: str = "[" + ",".join(str(v) for v in turn_embedding) + "]"

        cursor.execute(
            """
            SELECT inhalt,
                   1 - (embedding <=> %s::vector) AS similarity,
                   gewicht_decay,
                   COALESCE(arousal, 0.3) AS gap_arousal
            FROM lzg_knoten
            WHERE user_id = %s
              AND character_id = %s
              AND aktiv = TRUE
            ORDER BY embedding <=> %s::vector
            LIMIT 10
            """,
            (embedding_str, user_id, character_id, embedding_str),
        )

        for row in cursor.fetchall():
            inhalt, similarity, gewicht, gap_arousal = row
            if similarity and similarity > 0.1:
                kandidaten.append({
                    "konzept":    inhalt,
                    "similarity": float(similarity),
                    "gewicht":    float(gewicht) if gewicht else 0.5,
                    "gap_arousal": float(gap_arousal),
                    "quelle":     "lzg",
                })

        conn.close()
        logger.info(f"GV4-LZG: {len(kandidaten)} Kandidaten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-LZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def kzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
) -> list[dict]:
    """Sucht semantisch nahe Eintraege im KZG via RediSearch KNN.

    Nutzt config.redis_client. Da wir nur Text-/Numeric-Felder zurueckliefern
    (kein Embedding-Blob), spielt decode_responses=True hier keine Rolle —
    die Query-Bytes werden via PARAMS unbeeinflusst durchgereicht.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht (=salienz), gap_arousal, quelle.
    """
    kandidaten: list[dict] = []

    try:
        query_blob: bytes = np.array(turn_embedding, dtype=np.float32).tobytes()

        ergebnis = redis_client.execute_command(
            "FT.SEARCH", "idx:kzg",
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN 10 @embedding $vec AS score]",
            "PARAMS", "2", "vec", query_blob,
            "SORTBY", "score",
            "LIMIT", "0", "10",
            "RETURN", "4", "inhalt", "salienz", "arousal", "score",
            "DIALECT", "2",
        )

        if ergebnis and isinstance(ergebnis, list) and len(ergebnis) > 1:
            idx: int = 1
            while idx < len(ergebnis) - 1:
                _key = ergebnis[idx]
                felder = ergebnis[idx + 1]
                idx += 2

                feld_dict: dict = {}
                for i in range(0, len(felder), 2):
                    k = felder[i].decode("utf-8") if isinstance(felder[i], bytes) else felder[i]
                    v = felder[i + 1].decode("utf-8") if isinstance(felder[i + 1], bytes) else felder[i + 1]
                    feld_dict[k] = v

                inhalt:  str   = feld_dict.get("inhalt", "")
                salienz: float = float(feld_dict.get("salienz", "0.5"))
                arousal: float = float(feld_dict.get("arousal", "0.3"))
                score:   float = float(feld_dict.get("score", "1.0"))
                similarity: float = 1.0 - score

                if inhalt and similarity > 0.1:
                    kandidaten.append({
                        "konzept":     inhalt,
                        "similarity":  similarity,
                        "gewicht":     salienz,
                        "gap_arousal": arousal,
                        "quelle":      "kzg",
                    })

        logger.info(f"GV4-KZG: {len(kandidaten)} Kandidaten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-KZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def wissensluecken_finden(
    state:             ConversationState,
    effektive_neugier: float,
) -> list[dict]:
    """Findet semantisch nahe, aber unbesprochene Konzepte.

    Durchsucht LZG (pgvector) und KZG (RediSearch), filtert bereits
    Erwaentes und zu Aehnliches heraus, berechnet Relevanz aus
    6 Systemen und gibt die Top-N Luecken zurueck.

    Systeme:
      1. Gedaechtnis     — similarity × gewicht (aus DB)
      2. Aktualitaet     — nur Session-Turns (hier: alle DB = 1.0)
      3. Drive           — Ziel-Gravitation (neugier_boost)
      4. Neugier         — effektive_neugier (6 Saeulen, sin^0.5)
      5. Register        — register_kompatibilitaet (sachlich/offen)
      6. Charakter       — kern_hash Cosine >= Schwelle

    Returns:
        Top GV_LUECKEN_MAX Luecken sortiert nach Relevanz,
        oder leere Liste wenn nichts gefunden.
    """
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "nova")
    user_prompt:  str = state.get("user_prompt", "")
    internal = state.get("internal")
    modus:        str = internal.emotion.mode                 if internal else "alltag"
    dynamik:      str = internal.emotion.relationship_dynamic if internal else "neutral"

    if not user_prompt or not user_id:
        return []

    # ── 1. Turn-Embedding ──
    # Bevorzugt das vom Enricher bereits berechnete Embedding (spart ~1.6s).
    turn_embedding: list[float] = state.get("prompt_embedding") or []
    if not turn_embedding:
        try:
            request = EmbedRequest(text=user_prompt)
            embed_response = model_service.embed.submit_sync(request)
            turn_embedding = embed_response.embedding
            logger.debug(
                "Wissensluecken: GV4-Fallback Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(turn_embedding),
                embed_response.duration_seconds,
            )
        except Exception as fehler:
            logger.warning(f"GV4: Embedding fehlgeschlagen: {fehler}")
            return []

    # ── 2. Kandidaten aus LZG + KZG ──
    lzg_kandidaten: list[dict] = lzg_kandidaten_suchen(
        turn_embedding, user_id, character_id
    )
    kzg_kandidaten: list[dict] = kzg_kandidaten_suchen(
        turn_embedding, user_id, character_id
    )
    alle_kandidaten: list[dict] = lzg_kandidaten + kzg_kandidaten

    if not alle_kandidaten:
        logger.info("GV4: Keine Kandidaten gefunden")
        return []

    # ── 3. Filter: bereits erwaehnt ──
    session_turns: list[dict] = state.get("session_turns", [])
    gefiltert: list[dict] = [
        k for k in alle_kandidaten
        if not ist_bereits_erwaehnt(k["konzept"], session_turns)
    ]

    gefiltert = [
        k for k in gefiltert
        if k["similarity"] <= GV_LUECKEN_SIM_OBERGRENZE
    ]

    if not gefiltert:
        logger.info("GV4: Alle Kandidaten bereits erwaehnt oder zu aehnlich")
        return []

    # ── 4. Relevanz berechnen ──
    aktivierte_ziele: list[dict] = state.get("aktivierte_ziele", [])

    for k in gefiltert:
        basis: float = k["similarity"] * k["gewicht"] * GV_QUELLEN_FAKTOR

        # Neugier-Boost aus Ziel-Gravitation (Turn-Embedding als Proxy)
        neugier_boost: float = 0.0
        if aktivierte_ziele:
            max_grav: float = 0.0
            for ziel in aktivierte_ziele:
                ziel_embedding = ziel.get("embedding")
                if not ziel_embedding:
                    continue
                ziel_sim: float = cosine_similarity(
                    turn_embedding, ziel_embedding
                )
                grav: float = ziel_sim * ziel.get("motivation", 0.5)
                max_grav = max(max_grav, grav)
            if max_grav >= GV_NEUGIER_BOOST_SCHWELLE:
                neugier_boost = max_grav

        register: float = register_kompatibilitaet(
            k["gap_arousal"], modus, dynamik
        )

        relevanz: float = (
            basis
            * (1.0 + neugier_boost)
            * effektive_neugier
            * register
        )

        k["relevanz"]      = relevanz
        k["neugier_boost"] = neugier_boost
        k["register"]      = register

    # ── 5. Charakter-Filter ──
    nova_kern: str = internal.character.core if internal else ""
    if nova_kern:
        try:
            request = EmbedRequest(text=nova_kern)
            embed_response = model_service.embed.submit_sync(request)
            kern_embedding: list[float] = embed_response.embedding
            logger.debug(
                "Wissensluecken: Charakter-Kern Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(kern_embedding),
                embed_response.duration_seconds,
            )
            for k in gefiltert:
                # Turn-Embedding als Proxy fuer Luecken-Embedding
                k["charakter_resonanz"] = cosine_similarity(
                    turn_embedding, kern_embedding
                )
        except Exception as fehler:
            logger.warning(f"GV4: Kern-Embedding fehlgeschlagen: {fehler}")
            for k in gefiltert:
                k["charakter_resonanz"] = 0.5
    else:
        for k in gefiltert:
            k["charakter_resonanz"] = 0.5

    qualifiziert: list[dict] = [
        k for k in gefiltert
        if k["relevanz"] >= GV_LUECKEN_MIN_RELEVANZ
        and k["charakter_resonanz"] >= GV_CHARAKTER_RESONANZ_SCHWELLE
    ]

    qualifiziert.sort(key=lambda k: k["relevanz"], reverse=True)

    # Deduplizierung: Wenn zwei Luecken untereinander zu aehnlich sind,
    # nur die mit der hoeheren Relevanz behalten.
    dedupliziert: list[dict] = []
    for kandidat in qualifiziert:
        ist_duplikat: bool = False
        for behalten in dedupliziert:
            # Einfacher Token-Overlap als Proxy (kein Embedding noetig)
            woerter_a: set[str] = {w.lower() for w in kandidat["konzept"].split() if len(w) > 3}
            woerter_b: set[str] = {w.lower() for w in behalten["konzept"].split() if len(w) > 3}
            if woerter_a and woerter_b:
                overlap: float = len(woerter_a & woerter_b) / min(len(woerter_a), len(woerter_b))
                if overlap > 0.6:
                    ist_duplikat = True
                    logger.debug(
                        f"GV4-Dedup: '{kandidat['konzept'][:50]}' "
                        f"ist Duplikat von '{behalten['konzept'][:50]}' "
                        f"(Overlap {overlap:.0%})"
                    )
                    break
        if not ist_duplikat:
            dedupliziert.append(kandidat)
    qualifiziert = dedupliziert

    # ── 6. Top N ──
    qualifiziert.sort(key=lambda k: k["relevanz"], reverse=True)
    ergebnis: list[dict] = qualifiziert[:GV_LUECKEN_MAX]

    if ergebnis:
        logger.info(
            f"GV4: {len(ergebnis)} Wissensluecken qualifiziert — "
            + ", ".join(
                f"'{l['konzept'][:40]}' ({l['quelle']}, rel={l['relevanz']:.3f})"
                for l in ergebnis
            )
        )
    else:
        logger.info(
            f"GV4: {len(gefiltert)} Kandidaten geprueft, "
            f"keine ueber Relevanz-Schwelle {GV_LUECKEN_MIN_RELEVANZ}"
        )

    return ergebnis
