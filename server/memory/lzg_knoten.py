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
    EMOTION_SEKTOR_MAP,
    EMOTION_SYNONYM_MAP,
    LZG_KNOTEN_DAEMPFUNG_EXP,
    LZG_KNOTEN_DECAY_RATE,
    LZG_KNOTEN_GEWICHT_CAP,
    LZG_KNOTEN_MATCH_SCHWELLE,
    LZG_KNOTEN_MIN_GEWICHT,
    LZG_KNOTEN_REINFORCEMENT_BOOST,
)

logger = logging.getLogger(__name__)


def embed_text_bauen(inhalt: str) -> str:
    """
    Baut den Embed-Text eines lzg_knoten — die EINZIGE Formel fuer diese
    Spalte (Chat 107). Live-Pfad und Migrations-/Re-Embedding-Werkzeuge
    rufen dieselbe Funktion; der Text ist aus der persistierten Spalte
    `inhalt` vollstaendig rekonstruierbar.

    E: inhalt muss nicht-leer sein — ein leerer Pflichttext ist ein
       Fehler im Aufrufer, kein Leerstring-Embedding.
    V: Formel ist die Identitaet (Live-Formel seit Synapsen P4).
    A: der unveraenderte inhalt.
    """
    if not inhalt or not inhalt.strip():
        raise ValueError("embed_text_bauen(lzg_knoten): inhalt ist leer — kein Embed-Text baubar")
    return inhalt


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
        logger.exception(
            "%s: knoten_anlegen fehlgeschlagen quell=%s",
            type(exc).__name__, kzg_quell_key,
        )
        return None
    finally:
        conn.close()


def knoten_embedding_aktualisieren(
    postgres_url: str,
    knoten_id: int,
    embedding_str: str,
) -> bool:
    """
    Ueberschreibt das Embedding eines bestehenden lzg_knoten — das bis
    Chat 107 im Repo fehlende UPDATE (Re-Embedding-Pfad, EMBEDDING-
    CASING-BLIND Phase 2). Live schreibt nur knoten_anlegen initial;
    dieses UPDATE gehoert dem Migrations-/Re-Embedding-Werkzeug.

    Vorbedingung: knoten_id > 0, embedding_str ist ein pgvector-Literal
    ("[v1,v2,...]"). Nachbedingung: genau eine Zeile aktualisiert.
    Fehlerfaelle: unplausible Eingabe, unbekannte knoten_id (rowcount 0),
    DB-Fehler — jeweils logger.error und False.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(knoten_id, int) or knoten_id <= 0:
        logger.error(
            "knoten_embedding_aktualisieren: unplausible knoten_id=%r — verworfen", knoten_id
        )
        return False
    if not embedding_str or not embedding_str.startswith("["):
        logger.error(
            "knoten_embedding_aktualisieren: embedding_str ist kein pgvector-Literal (knoten=%s) — "
            "verworfen",
            knoten_id,
        )
        return False

    # ── Verarbeitung ────────────────────────────
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE lzg_knoten SET embedding = %s::vector WHERE id = %s",
                (embedding_str, knoten_id),
            )
            aktualisiert: int = cur.rowcount
        conn.commit()
    except psycopg2.Error as exc:
        conn.rollback()
        logger.exception(
            "%s: knoten_embedding_aktualisieren fehlgeschlagen knoten=%s",
            type(exc).__name__, knoten_id,
        )
        return False
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    if aktualisiert != 1:
        logger.error(
            "knoten_embedding_aktualisieren: rowcount=%d fuer knoten=%s (erwartet 1) — Knoten "
            "existiert "
            "nicht?",
            aktualisiert, knoten_id,
        )
        return False
    return True


def knoten_gewichte_zuruecksetzen(
    postgres_url: str,
    *,
    commit: bool,
    beispiel_ids: list[int] | None = None,
) -> dict:
    """
    Setzt alle Knoten-Gewichte auf den rekonstruierten Anlagezustand zurueck
    (Migrations-Reset, EMBEDDING-CASING-BLIND Phase B, Chat 107). Anlass:
    2910 Reinforcements (93 %) entstanden durch Skelett-Kollisionen im
    casing-blinden Raum — die Gewichte sind Zufall. Ein Gewicht, von dem
    wir wissen, dass es Zufall ist, richtet mehr Schaden an als kein Gewicht.

    Rekonstruktion (exakt, kein Standardwert — Beleg: einziger Schreiber
    von gewicht_roh/haeufigkeit ist knoten_verstaerken, Boost seit
    Einfuehrung unveraendert, beide Felder aendern sich atomar gemeinsam):

        initial_roh     = gewicht_roh - (haeufigkeit - 1) * BOOST
        gewicht_absolut = gewicht_absolut_berechnen(initial_roh)  # ECHTE Funktion
        gewicht_decay   = gewicht_absolut
        haeufigkeit     = 1
        verstaerkt_am   = erstellt_am

    verstaerkt_am := erstellt_am, weil verstaerkt_am der Anker des Verfalls
    ist: Jedes Zufalls-Reinforcement hat ihn auf NOW() gezogen — ein Mai-
    Knoten, der im Juli faelschlich verstaerkt wurde, gilt heute als frisch;
    der Decay wuerde von einer Luege aus rechnen. NOW() fuer alle waere die
    schlechteste Variante: Kernfakt aus dem Mai und Randbemerkung von gestern
    haetten dieselbe Verfallsuhr. Das Alter ist Information — es liegt in
    erstellt_am. aktiv bleibt unangetastet.

    Idempotent: Nach einem Reset ist haeufigkeit 1 -> initial_roh == gewicht_roh.
    Vorbedingung/Abbruch (fail loud): Wird initial_roh bei irgendeinem Knoten
    <= 0, stimmt die Rekonstruktionsannahme nicht — ABBRUCH ohne jede
    Schreibaktion, die betroffenen Knoten werden aufgelistet.

    commit=False rechnet nur (Dry-Run). beispiel_ids: Knoten, fuer die
    vorher/nachher-Werte zurueckgegeben werden. Rueckgabe:
    {knoten, verletzungen, beispiele, geschrieben, error}.
    """
    # ── Eingabe-Validierung: Bestand laden, Reset-Plan pruefen ─────────
    ergebnis: dict = {
        "knoten": 0,
        "verletzungen": [],
        "beispiele": [],
        "geschrieben": 0,
        "error": None,
    }
    beispiel_menge: set[int] = set(beispiel_ids or [])

    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, gewicht_roh, gewicht_absolut, gewicht_decay, haeufigkeit, "
                "       verstaerkt_am, erstellt_am "
                "FROM lzg_knoten ORDER BY id"
            )
            knoten = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    ergebnis["knoten"] = len(knoten)
    # 4-Tupel passend zu den 4 Platzhaltern des UPDATE: roh, absolut,
    # decay (= absolut, wie bei knoten_anlegen), id. Ein 3-Tupel liess
    # execute_batch/mogrify mit IndexError scheitern (Chat 107).
    plan: list[tuple[float, float, float, int]] = []
    for k in knoten:
        initial_roh: float = (
            k["gewicht_roh"] - (k["haeufigkeit"] - 1) * LZG_KNOTEN_REINFORCEMENT_BOOST
        )
        if initial_roh <= 0:
            ergebnis["verletzungen"].append(
                {"id": k["id"], "gewicht_roh": k["gewicht_roh"], "haeufigkeit": k["haeufigkeit"],
                 "initial_roh": initial_roh}
            )
            continue
        initial_absolut: float = gewicht_absolut_berechnen(initial_roh)
        plan.append((initial_roh, initial_absolut, initial_absolut, k["id"]))
        if k["id"] in beispiel_menge:
            ergebnis["beispiele"].append({
                "id": k["id"],
                "vorher": {"roh": k["gewicht_roh"], "absolut": k["gewicht_absolut"],
                           "decay": k["gewicht_decay"], "haeufigkeit": k["haeufigkeit"],
                           "verstaerkt_am": str(k["verstaerkt_am"])},
                "nachher": {"roh": initial_roh, "absolut": initial_absolut,
                            "decay": initial_absolut, "haeufigkeit": 1,
                            "verstaerkt_am": str(k["erstellt_am"])},
            })

    if ergebnis["verletzungen"]:
        for v in ergebnis["verletzungen"]:
            logger.error(
                "Gewichts-Reset: Rekonstruktion verletzt bei Knoten %s — roh=%.3f, "
                "haeufigkeit=%d ergaebe initial_roh=%.3f (<= 0). ABBRUCH, nichts geschrieben.",
                v["id"], v["gewicht_roh"], v["haeufigkeit"], v["initial_roh"],
            )
        ergebnis["error"] = "rekonstruktion_verletzt"
        return ergebnis

    # ── Verarbeitung: nur bei commit, atomar in einer Transaktion ──────
    if commit and plan:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                psycopg2.extras.execute_batch(
                    cur,
                    """
                    UPDATE lzg_knoten
                    SET gewicht_roh = %s,
                        gewicht_absolut = %s,
                        gewicht_decay = %s,
                        haeufigkeit = 1,
                        verstaerkt_am = erstellt_am
                    WHERE id = %s
                    """,
                    plan,
                )
            conn.commit()
            ergebnis["geschrieben"] = len(plan)
        except psycopg2.Error as exc:
            conn.rollback()
            logger.exception(
                "%s: Gewichts-Reset fehlgeschlagen — Rollback, nichts geschrieben",
                type(exc).__name__,
            )
            ergebnis["error"] = str(exc)
            return ergebnis
        finally:
            conn.close()

    # ── Ausgabe ─────────────────────────────────
    logger.info(
        "Gewichts-Reset: %d Knoten geplant, %d geschrieben (commit=%s)",
        len(plan), ergebnis["geschrieben"], commit,
    )
    return ergebnis


def kandidaten_mit_cosine_laden(
    postgres_url: str,
    user_id: str,
    character_id: str,
    embedding_str: str,
    *,
    ausschluss_id: Optional[int] = None,
    include_inactive: bool = False,
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
            # aktiv-Filter bedingt: Standard nur aktive Knoten (Lese-/Match-Pfad),
            # mit include_inactive auch deaktivierte (Halbreaktivierung §9.3).
            aktiv_klausel = "" if include_inactive else "AND k.aktiv = TRUE"
            cur.execute(
                f"""
                SELECT k.id, k.gewicht_absolut, k.aktiv, k.entitaet_ids, k.themen,
                       k.timeline_id,
                       t.event_time AS timeline_event_time,
                       t.precision  AS timeline_praezision,
                       1 - (k.embedding <=> %s::vector) AS cosine
                FROM lzg_knoten k
                LEFT JOIN timeline t ON t.id = k.timeline_id
                WHERE k.user_id = %s AND k.character_id = %s {aktiv_klausel}
                  AND (%s::int IS NULL OR k.id <> %s::int)
                ORDER BY cosine DESC
                """,
                (embedding_str, user_id, character_id, ausschluss_id, ausschluss_id),
            )
            kandidaten = [dict(row) for row in cur.fetchall()]
        logger.info(
            "Kandidaten geladen: paar=%s/%s include_inactive=%s anzahl=%d top_cosine=%.4f",
            user_id, character_id, include_inactive, len(kandidaten),
            kandidaten[0]["cosine"] if kandidaten else float("nan"),
        )
        return kandidaten
    except psycopg2.Error as exc:
        logger.exception(
            "%s: kandidaten_mit_cosine_laden fehlgeschlagen paar=%s/%s",
            type(exc).__name__, user_id, character_id,
        )
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
    # Kalibriert auf nomic-embed-text-v2-moe (Chat 107). An diesem Wert haengt
    # Schale 0 der gesamten Spreading Activation. Abdeckungsmessung an 100
    # echten User-Prompts gegen 302 Knoten:
    #   0.50 -> 53 % Turns mit Anker (verliert echte Treffer)
    #   0.40 -> 82 %, im Schnitt 4.1 Anker (gewaehlt)
    #   0.35 -> 89 %, 10.2 Anker (Rauschen beginnt)
    # 100 % Abdeckung ist NICHT das Ziel — Cold Start ist bei ankerlosen
    # Prompts die richtige Antwort, kein Ausfall. Vorher 0.50 im casing-
    # blinden Raum: 100 % Abdeckung mit ~299,6 von 302 Knoten pro Turn.
    # ⚠ Wachposten: Prompt↔Knoten-Wert — begruendeter Startwert aus der
    # Abdeckungsmessung, kein Verteilungs-Messergebnis. Nach Live-Betrieb pruefen.
    min_similarity: float = 0.40,
) -> list[dict]:
    """
    Initial-Retrieval des Synapsen-Lesepfads (Konzept §8.1): liefert die
    Top-K (default 3) Anker-Knoten einer Paar-Partition per pgvector-Cosine.

    Geladen werden nur aktive Knoten mit Embedding; nach dem Fetch werden
    Treffer unter min_similarity verworfen (ein schwacher Cosine ist kein
    sinnvoller Anker).

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
                    beobachter,
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
        # Das Log zeigt die ROHEN Cosines VOR dem Schwellenfilter — nicht die
        # gefilterten. Der fruehere float("nan")-Platzhalter bei leerer Anker-
        # Liste hat behauptet, was er nicht wusste, und den IVFFLAT-RECALL-
        # KOLLAPS als Nullvektor-Verdacht verkleidet (Chat 107;
        # lesson_l_log-behauptet-was-es-weiss).
        if roh:
            logger.info(
                "Anker-Retrieval: paar=%s/%s %d Kandidaten geladen "
                "(beste Roh-Cosine %.4f, schwaechste %.4f), %d ueber Schwelle %.2f",
                user_id, character_id, len(roh),
                roh[0]["cosine"], roh[-1]["cosine"], len(anker), min_similarity,
            )
        else:
            logger.info(
                "Anker-Retrieval: paar=%s/%s 0 Kandidaten geladen — Partition leer "
                "oder kein Knoten mit Embedding",
                user_id, character_id,
            )
        for a in anker:
            logger.debug("Anker: knoten=%s cosine=%.4f gewicht_decay=%.3f",
                         a["id"], a["cosine"], a["gewicht_decay"])
        return anker
    except psycopg2.Error as exc:
        logger.exception(
            "%s: anker_retrieval fehlgeschlagen paar=%s/%s",
            type(exc).__name__, user_id, character_id,
        )
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
        logger.exception(
            "%s: knoten_verstaerken fehlgeschlagen id=%s",
            type(exc).__name__, knoten_id,
        )
        return None
    finally:
        conn.close()


def reactivate_node(postgres_url: str, knoten_id: int) -> Optional[dict]:
    """
    Halbreaktivierung (§9.3): Weckt einen durch Decay deaktivierten Knoten.

    gewicht_decay springt auf den Halbwert zwischen Anker-Staerke und
    Deaktivierungs-Schwelle: (gewicht_absolut + LZG_KNOTEN_MIN_GEWICHT) / 2 —
    klar ueber der Schwelle, deutlich unter dem alten Anker. Der Knoten ist
    wieder praesent, aber nicht sofort an der Spitze; weitere echte
    Aktivierungen naehern ihn seinem alten Niveau an.

    Unangetastet: gewicht_roh (Akkumulator), gewicht_absolut (Anker-Staerke),
    haeufigkeit. Der Knoten wird geweckt, nicht verstaerkt — kein
    REINFORCEMENT_BOOST (der greift erst bei der naechsten echten Aktivierung
    im normalen Pfad).

    decay_am = NOW() wird mitgesetzt, damit der naechste run_node_decay den
    Verfall ab jetzt rechnet (run_node_decay rechnet aus verstaerkt_am, das
    ebenfalls auf NOW() gesetzt wird — beide konsistent zurueckgesetzt).

    Liefert ein Dict {knoten_id, gewicht_absolut, decay_alt, decay_neu} fuer die
    pipeline_log-Forensik (vorher/nachher) oder None bei Fehler/nicht gefunden.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT gewicht_absolut, gewicht_decay, aktiv FROM lzg_knoten WHERE id = %s",
                (knoten_id,),
            )
            zeile = cur.fetchone()
            if zeile is None:
                logger.error("reactivate_node: Knoten %s nicht gefunden", knoten_id)
                return None
            gewicht_absolut = zeile[0]
            decay_alt = zeile[1]
            war_aktiv = zeile[2]
            # Plausibilitaet (EVA): Halbreaktivierung gilt nur fuer deaktivierte
            # Knoten. Ein aktiver Knoten gehoert in den normalen Reinforcement-
            # Pfad (knoten_verstaerken) — hier waere er ein Logikfehler des
            # Aufrufers, also nicht schweigend halbieren.
            if war_aktiv:
                logger.warning(
                    "reactivate_node: Knoten %s ist bereits aktiv — "
                    "Halbreaktivierung uebersprungen (gehoert in knoten_verstaerken)",
                    knoten_id,
                )
                return None
            decay_neu = (gewicht_absolut + LZG_KNOTEN_MIN_GEWICHT) / 2
            cur.execute(
                """
                UPDATE lzg_knoten
                SET gewicht_decay = %s,
                    aktiv = TRUE,
                    verstaerkt_am = NOW(),
                    decay_am = NOW()
                WHERE id = %s
                """,
                (decay_neu, knoten_id),
            )
        conn.commit()
        logger.info(
            "Knoten halbreaktiviert: id=%s absolut=%.3f decay %.3f -> %.3f (Schwelle %.2f)",
            knoten_id, gewicht_absolut, decay_alt, decay_neu, LZG_KNOTEN_MIN_GEWICHT,
        )
        return {
            "knoten_id": knoten_id,
            "gewicht_absolut": gewicht_absolut,
            "decay_alt": decay_alt,
            "decay_neu": decay_neu,
        }
    except psycopg2.Error as exc:
        conn.rollback()
        logger.exception("%s: reactivate_node fehlgeschlagen id=%s", type(exc).__name__, knoten_id)
        return None
    finally:
        conn.close()


def run_node_decay(
    postgres_url: str,
    decay_rate: float | None = None,
    min_weight: float | None = None,
) -> dict:
    """Materialisiert gewicht_decay fuer alle aktiven Knoten (globaler Lauf).

    Exponentieller Verfall aus verstaerkt_am gemaess Konzept synapsen_k §9.2:
        gewicht_decay = gewicht_absolut * exp(-decay_rate * tage_seit_verstaerkung)
    gewicht_absolut bleibt unangetastet (Anker-Stärke). Knoten, deren neuer
    gewicht_decay unter min_weight faellt, werden auf aktiv = FALSE gesetzt
    (Soft-Delete, reaktivierbar via Halbreaktivierung §9.3).

    Laeuft global ueber alle Paar-Partitionen (WHERE aktiv = TRUE) — die Formel
    ist knoten-lokal, ein globaler Sweep ist bit-identisch zur Paar-Schleife.

    Args:
        postgres_url: Postgres-Verbindungsstring (Hausstil: pro Funktion
            explizit uebergeben, wie kandidaten_mit_cosine_laden).
        decay_rate: Verfallsrate pro Tag. None -> config-Default. Explizit
            setzbar fuer Unit-Tests (Formel-Pruefung statt Live-Wert).
        min_weight: Deaktivierungs-Schwelle. None -> config-Default.

    Returns:
        dict mit total_processed (int), deactivated_count (int),
        deactivated_ids (list[int]), error (str | None).
    """
    # --- Eingabe (EVA): Defaults aufloesen + validieren ---
    if decay_rate is None:
        decay_rate = LZG_KNOTEN_DECAY_RATE   # (3) config-konform referenzieren
    if min_weight is None:
        min_weight = LZG_KNOTEN_MIN_GEWICHT  # (3) config-konform referenzieren

    result = {
        "total_processed": 0,
        "deactivated_count": 0,
        "deactivated_ids": [],
        "error": None,
    }

    if decay_rate < 0:
        logger.error(f"Decay-Lauf abgebrochen: ungueltige decay_rate={decay_rate} (< 0)")
        result["error"] = "decay_rate < 0"
        return result
    if min_weight < 0:
        logger.error(f"Decay-Lauf abgebrochen: ungueltiges min_weight={min_weight} (< 0)")
        result["error"] = "min_weight < 0"
        return result

    logger.info(
        f"Decay-Lauf startet (global): decay_rate={decay_rate}, "
        f"min_weight={min_weight}"
    )

    # --- Verarbeitung ---
    conn = None
    try:
        conn = psycopg2.connect(postgres_url)  # (2) Muster aus kandidaten_mit_cosine_laden
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Statement 1: gewicht_decay + decay_am fuer alle aktiven Knoten
            # materialisieren. Verfall komplett in SQL (deterministisch, kein LLM).
            cur.execute(
                """
                UPDATE lzg_knoten
                SET gewicht_decay = gewicht_absolut
                        * exp(-%s * (EXTRACT(EPOCH FROM (NOW() - verstaerkt_am)) / 86400.0)),
                    decay_am = NOW()
                WHERE aktiv = TRUE
                """,
                (decay_rate,),
            )
            total_processed = cur.rowcount
            logger.info(
                f"Decay-Lauf: gewicht_decay materialisiert fuer {total_processed} aktive Knoten"
            )

            # Statement 2: Knoten unter der Schwelle deaktivieren. Liest die in
            # Statement 1 frisch geschriebenen Werte (read-your-writes, selbe TX).
            cur.execute(
                """
                UPDATE lzg_knoten
                SET aktiv = FALSE
                WHERE aktiv = TRUE AND gewicht_decay < %s
                RETURNING id
                """,
                (min_weight,),
            )
            deactivated_ids = [row["id"] for row in cur.fetchall()]

        conn.commit()

        # --- Ausgabe (EVA): Ergebnis konsolidieren + Plausibilitaet ---
        deactivated_count = len(deactivated_ids)
        if deactivated_count > total_processed:
            logger.warning(
                f"Decay-Lauf: deaktiviert ({deactivated_count}) > verarbeitet ({total_processed}) "
                "— "
                f"unerwartet, bitte pruefen"
            )
        result["total_processed"] = total_processed
        result["deactivated_count"] = deactivated_count
        result["deactivated_ids"] = deactivated_ids
        logger.info(
            f"Decay-Lauf abgeschlossen: {total_processed} verarbeitet, {deactivated_count} "
            "deaktiviert "
            f"(ids={deactivated_ids})"
        )
        return result

    except psycopg2.Error as ex:
        if conn is not None:
            conn.rollback()
        logger.exception(f"{type(ex).__name__}: Decay-Lauf DB-Fehler, Rollback")
        result["error"] = str(ex)
        return result
    finally:
        if conn is not None:
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
        logger.exception("%s: knoten_laden fehlgeschlagen id=%s", type(exc).__name__, knoten_id)
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
        logger.exception(
            "%s: _kanten_nachbarn fehlgeschlagen knoten=%s",
            type(exc).__name__, knoten_id,
        )
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
        logger.exception(
            "%s: _knoten_details_laden fehlgeschlagen id=%s",
            type(exc).__name__, knoten_id,
        )
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
