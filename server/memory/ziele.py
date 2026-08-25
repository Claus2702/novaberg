"""
Ziele — Novas Antrieb aus PostgreSQL.

Langfristige Ziele (aus der Charakter-Destillation) und mittelfristige
Ziele (aus Pixie-Aktivitäten) mit Embedding für Gravitationsberechnung.
"""

import logging
import math
from datetime import datetime, timezone

import psycopg2

from config import ASSISTANT_USER_ID, DEFAULT_USER_ID, ZIEL_MITTELFRISTIG_DECAY_TAGE
from memory.utils import embedding_zu_pgvector_str
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.memory.ziele")


def ziel_paar_bestimmen(turn_user_id: str, turn_character_id: str) -> tuple[str, str]:
    """Leitet das Ziel-Paar aus dem Paar eines Turns ab.

    Novas Ziele stehen nach dem Paar-Schema als `(Subjekt=nova,
    Gegenueber=Mensch)` — sie sind Aussagen ueber Nova im Kontext genau einer
    Beziehung (`novaberg-convention-paar-schema.md` §2).

    Ein Turn nennt sein Paar dagegen in der Reihenfolge seines eigenen
    Subjekts: Der Human-Pfad laeuft als `(meister, nova)`, Novas eigener Pfad
    als `(nova, meister)`. Wer das Ziel-Paar aus dem Turn-Paar direkt
    uebernimmt, liest auf dem einen Pfad die Ziele und auf dem anderen nichts.
    Deshalb steht die Ableitung hier und nicht in vier Aufrufern.

    Vorbedingung: Mindestens eine der beiden Kennungen ist gesetzt.
    Nachbedingung: Ein Tupel `(nova, gegenueber)`; das Gegenueber ist nie Nova
        selbst.
    Fehlerfaelle: Beide Kennungen leer oder beide Nova — `logger.error` und
        Rueckfall auf `DEFAULT_USER_ID` als Gegenueber. Der Rueckfall ist
        benannt, nicht still: Eine Ausnahme wuerde hier einen laufenden Turn
        kappen, und ein leeres Gegenueber laege als Zeile in der Datenbank.

    Args:
        turn_user_id: Subjekt des Turns.
        turn_character_id: Gegenueber des Turns.

    Returns:
        `(subjekt, gegenueber)` fuer den Zugriff auf `ziele`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turn_user_id and not turn_character_id:
        logger.error(
            "ziel_paar_bestimmen: beide Kennungen leer — Gegenueber faellt auf "
            f"'{DEFAULT_USER_ID}' zurueck, die gelesenen Ziele koennen fremde sein"
        )
        return ASSISTANT_USER_ID, DEFAULT_USER_ID

    # ── Verarbeitung ────────────────────────────
    # Der Mensch ist die Kennung, die nicht Nova und nicht leer ist — gleich
    # auf welcher Seite des Turn-Paares er steht. Die Reihenfolge entscheidet
    # nur, wenn beide Seiten Menschen nennen; dann gilt das Subjekt des Turns.
    kandidaten: list[str] = [
        kennung for kennung in (turn_user_id, turn_character_id)
        if kennung and kennung != ASSISTANT_USER_ID
    ]
    gegenueber: str = kandidaten[0] if kandidaten else ""

    # ── Ausgabe-Verifikation ────────────────────
    if not gegenueber or gegenueber == ASSISTANT_USER_ID:
        logger.error(
            f"ziel_paar_bestimmen: kein Gegenueber in ({turn_user_id!r}, "
            f"{turn_character_id!r}) — Rueckfall auf '{DEFAULT_USER_ID}'. "
            f"Ein Turn ohne Menschen ist kein Turn"
        )
        return ASSISTANT_USER_ID, DEFAULT_USER_ID

    return ASSISTANT_USER_ID, gegenueber


def embed_text_bauen(zielsatz: str) -> str:
    """
    Baut den Embed-Text eines Ziels — die EINZIGE Formel für diese Spalte
    (Chat 107). Der Text ist aus der persistierten Spalte zielsatz
    vollständig rekonstruierbar; alle Erzeuger (CharakterAgent,
    RechercheAgent, Startup-Backfill) rufen dieselbe Funktion.

    E: zielsatz muss nicht-leer sein.
    V: Formel ist die Identität (Live-Formel aller drei Erzeuger).
    A: der unveränderte zielsatz.
    """
    if not zielsatz or not zielsatz.strip():
        raise ValueError("embed_text_bauen(ziele): zielsatz ist leer — kein Embed-Text baubar")
    return zielsatz


def motivation_berechnen(
    motivation_basis:    float,
    motivation_basis_am: datetime,
    jetzt:               datetime | None = None,
    halbwertszeit_tage:  int = ZIEL_MITTELFRISTIG_DECAY_TAGE,
) -> float:
    """Berechnet die aktuelle Motivation eines Ziels aus seinem Anker.

    Formel: motivation = basis x exp(-ln2 / halbwertszeit x tage_seit_anker)

    Reine Funktion. Keine Eingabe wurde je aus dem Ergebnis berechnet, nichts
    wird zurueckgeschrieben. Damit ist der Wert unabhaengig davon, ob und wie
    oft ein Decay-Lauf stattgefunden hat — hundert Laeufe liefern dasselbe wie
    keiner (novaberg-convention-abgeleitete-werte.md, Regeln 2 bis 4).

    Die Vorgaengerfassung las ihre Zeitbasis aus `erstellt_am`, multiplizierte
    die bereits verfallene Motivation erneut mit dem Faktor des GESAMTALTERS und
    schrieb das Ergebnis zurueck. Der Verfall wuchs dadurch quadratisch mit der
    Zahl der Laeufe statt linear mit der Zeit (ZIEL-DECAY-FORMEL-KUMULATIV).

    Vorbedingung: motivation_basis in [0.0, 1.0], motivation_basis_am gesetzt.
    Nachbedingung: Rueckgabe in [0.0, motivation_basis] — der Verfall kann eine
    Motivation nur senken, nie heben.
    Fehlerfaelle: Ein Anker ausserhalb von [0,1] wird laut protokolliert und
    geklemmt; ein Ankerzeitpunkt in der Zukunft ergibt den vollen Anker, damit
    eine schiefe Uhr keine Motivation erfindet.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 0.0 <= motivation_basis <= 1.0:
        logger.error(
            f"motivation_berechnen: Anker {motivation_basis} liegt ausserhalb "
            f"[0.0, 1.0] — geklemmt. Der Schreiber des Ankers ist defekt"
        )
        motivation_basis = max(0.0, min(1.0, motivation_basis))

    if halbwertszeit_tage <= 0:
        logger.error(
            f"motivation_berechnen: Halbwertszeit {halbwertszeit_tage} Tage ist "
            f"kein gueltiger Zeitraum — Anker unveraendert zurueckgegeben"
        )
        return motivation_basis

    if jetzt is None:
        jetzt = datetime.now(timezone.utc)
    if motivation_basis_am.tzinfo is None:
        motivation_basis_am = motivation_basis_am.replace(tzinfo=timezone.utc)

    # ── Verarbeitung ────────────────────────────
    tage:       float = max(0.0, (jetzt - motivation_basis_am).total_seconds() / 86400.0)
    decay_rate: float = math.log(2) / halbwertszeit_tage
    motivation: float = motivation_basis * math.exp(-decay_rate * tage)

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 <= motivation <= motivation_basis:
        logger.error(
            f"motivation_berechnen: Ergebnis {motivation} liegt nicht in "
            f"[0.0, {motivation_basis}] (tage={tage:.2f}) — auf den Anker geklemmt"
        )
        motivation = max(0.0, min(motivation_basis, motivation))

    return motivation


def ziele_aktive_laden(
    postgres_url: str,
    user_id:      str,
    character_id: str,
) -> list[dict]:
    """Lädt alle aktiven Ziele eines Paares mit Embedding.

    Beide Kennungen sind Pflicht und haben bewusst keinen Vorgabewert
    (`novaberg-convention-paar-schema.md` §5: „Defaults sind ein Code-Smell").
    Ein Vorgabewert fuer das Gegenueber liesse den Aufrufer glauben, er habe
    das Paar genannt, waehrend er die Ziele einer fremden Beziehung liest.

    Vorbedingung: Beide Kennungen sind gesetzt.
    Nachbedingung: Ausschliesslich Ziele dieses Paares, aktiv, nach Typ und
        Motivation sortiert.
    Fehlerfaelle: Leere Kennung — `logger.error`, leere Liste, kein Zugriff.
        DB-Fehler — `logger.exception`, leere Liste.

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        user_id: Subjekt — bei Novas Zielen `ASSISTANT_USER_ID`.
        character_id: Gegenueber — der Mensch der Beziehung.

    Returns:
        Liste von Ziel-Dicts mit id, ziel_typ, zielsatz, motivation,
        emotion, arousal, embedding, erstellt_am.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        logger.error(
            f"ziele_aktive_laden: unvollstaendiges Paar ({user_id!r}, "
            f"{character_id!r}) — nichts geladen. Ohne Gegenueber waere jede "
            f"Zeile ein Treffer"
        )
        return []

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, ziel_typ, zielsatz, motivation, emotion, arousal,
                   embedding::text, erstellt_am, COALESCE(thema, '')
            FROM ziele
            WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
            ORDER BY ziel_typ, motivation DESC
            """,
            (user_id, character_id),
        )

        rows = cursor.fetchall()
        conn.close()

        ziele: list[dict] = []
        for row in rows:
            # Embedding aus PostgreSQL-Text-Format parsen: "[0.1,0.2,...]" → list[float]
            embedding_raw: str | None = row[6]
            embedding: list[float] | None = None
            if embedding_raw:
                embedding = [
                    float(x) for x in embedding_raw.strip("[]").split(",")
                ]

            ziele.append({
                "id":          row[0],
                "ziel_typ":    row[1],
                "zielsatz":    row[2],
                "motivation":  row[3],
                "emotion":     row[4],
                "arousal":     row[5],
                "embedding":   embedding,
                "erstellt_am": row[7],
                "thema":       row[8] or "",
            })

        logger.info(
            f"Ziele geladen: {len(ziele)} aktive Ziele für Paar "
            f"({user_id}, {character_id}) "
            f"({sum(1 for z in ziele if z['ziel_typ'] == 'langfristig')} lang, "
            f"{sum(1 for z in ziele if z['ziel_typ'] == 'mittelfristig')} mittel)"
        )
        return ziele

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Ziele laden fehlgeschlagen")
        return []


def ziel_speichern(
    postgres_url: str,
    user_id:      str,
    character_id: str,
    ziel_typ:     str,
    zielsatz:     str,
    motivation:   float,
    emotion:      str = "",
    arousal:      float = 0.5,
    thema:        str = "",
    embedding:    list[float] | None = None,
) -> int | None:
    """Speichert ein neues Ziel in PostgreSQL.

    Das Gegenueber ist Pflicht: Die Spalte `character_id` traegt seit Chat 125
    keinen Default mehr, ein INSERT ohne sie scheitert an NOT NULL. Das ist
    Absicht — ein Ziel ohne Beziehung waere in jedem Turn sichtbar.

    Vorbedingung: Beide Kennungen gesetzt, `zielsatz` nicht leer.
    Nachbedingung: Genau eine neue Zeile, deren Anker und materialisierter Wert
        identisch sind.
    Fehlerfaelle: Leere Kennung — `logger.error`, kein Schreibversuch, None.
        DB-Fehler — `logger.exception`, None.

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        user_id: Subjekt — bei Novas Zielen `ASSISTANT_USER_ID`.
        character_id: Gegenueber — der Mensch der Beziehung.
        ziel_typ: "langfristig" oder "mittelfristig".
        zielsatz: Der Ziel-Text (1-2 Sätze).
        motivation: Motivationsstärke (0.0-1.0).
        emotion: Emotionale Valenz des Ziels.
        arousal: Emotionale Intensität.
        thema: Kurzes Themen-Label (2-3 Wörter) für das Gravitationsgraph-Panel.
        embedding: Vorberechnetes Embedding (768-dim), oder None.

    Returns:
        ID des neuen Eintrags, oder None bei Fehler.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        logger.error(
            f"ziel_speichern: unvollstaendiges Paar ({user_id!r}, "
            f"{character_id!r}) — nichts geschrieben, '{zielsatz[:60]}' verworfen"
        )
        return None

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        embedding_str: str | None = None
        if embedding:
            embedding_str = embedding_zu_pgvector_str(embedding)

        cursor.execute(
            """
            INSERT INTO ziele (user_id, character_id, ziel_typ, zielsatz, motivation,
                               motivation_basis, motivation_basis_am,
                               emotion, arousal, thema, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s::vector)
            RETURNING id
            """,
            # Anker und materialisierter Wert sind beim Anlegen identisch: Der
            # Verfall ueber null Tage ist exakt 1.0. Beide werden gesetzt, weil
            # ein NULL-Anker "nie gesetzt" bedeutet und laut gemeldet wird.
            (user_id, character_id, ziel_typ, zielsatz, motivation,
             motivation, emotion, arousal, thema, embedding_str),
        )

        ziel_id: int = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        logger.info(
            f"Ziel gespeichert: id={ziel_id}, paar=({user_id}, {character_id}), "
            f"typ={ziel_typ}, motivation={motivation:.2f}, '{zielsatz[:60]}'"
        )
        return ziel_id

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Ziel speichern fehlgeschlagen")
        return None


def ziel_motivation_anpassen(
    postgres_url: str,
    ziel_id:      int,
    neue_motivation: float,
) -> bool:
    """Setzt die Motivation eines Ziels neu — als ANKER, nicht als Momentwert.

    Wer ein Ziel wieder aufgreift, setzt seine Vergessenskurve zurueck: Anker
    und Ankerzeitpunkt werden gemeinsam geschrieben, `motivation` bekommt
    denselben Wert, weil der Verfall ueber null Tage 1.0 ist. Dasselbe Muster
    wie `knoten_verstaerken` im LZG, das `verstaerkt_am` auf jetzt setzt.

    Wuerde hier nur `motivation` geschrieben, laese der naechste Decay-Lauf
    einen frisch gesetzten Wert als gealtert und zoege ihn sofort wieder nach
    unten — gegen einen Anker, der noch aus einer anderen Zeit stammt.

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        ziel_id: ID des Ziels.
        neue_motivation: Neuer Motivationswert (0.0-1.0).

    Returns:
        True bei Erfolg, False bei Fehler.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE ziele
            SET motivation          = %s,
                motivation_basis    = %s,
                motivation_basis_am = NOW(),
                aktualisiert_am     = NOW()
            WHERE id = %s
            """,
            (neue_motivation, neue_motivation, ziel_id),
        )

        conn.commit()
        conn.close()

        logger.info(
            f"Ziel-Motivation gesetzt: id={ziel_id}, anker={neue_motivation:.3f}, "
            f"Verfallsuhr auf jetzt zurueckgesetzt"
        )
        return True

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Ziel-Motivation anpassen fehlgeschlagen")
        return False


def ziel_decay_lauf(
    postgres_url:       str,
    ziel_typ:           str = "mittelfristig",
    deaktivierungs_schwelle: float = 0.15,
    halbwertszeit_tage: int = ZIEL_MITTELFRISTIG_DECAY_TAGE,
    user_id:            str | None = None,
) -> dict:
    """Materialisiert `motivation` fuer alle aktiven Ziele eines Typs.

    Zwei Statements in einer Transaktion, komplett in SQL — deterministisch,
    kein LLM, ein Bulk-UPDATE statt einer Schleife (Muster: run_node_decay in
    memory/lzg_knoten.py):

      1. motivation = motivation_basis x exp(-ln2/HWZ x tage_seit_anker)
      2. aktiv = FALSE, wo motivation unter die Schwelle gefallen ist

    Der Lauf ist idempotent: Er liest den Anker und die Zeit, nie den zuvor
    materialisierten Wert. Zweimal laufen aendert nichts, hundertmal auch nicht,
    und gar nicht zu laufen macht den Wert nur veraltet, nicht falsch.

    `ziel_typ` ist eine ALLOWLIST. Die Vorgaengerfassung uebersprang lediglich
    `langfristig` und decayte damit jeden anderen Typ mit der mittelfristigen
    Halbwertszeit — auch `kurzfristig`, das es heute nicht gibt und morgen
    geben kann (ZIEL-DECAY-TYP-FILTER).

    Ziele ohne Anker werden NICHT angefasst und laut gezaehlt: Sie stammen aus
    der Zeit vor dem Ankerfeld oder von einem Schreiber, der es nicht setzt.

    `user_id=None` laeuft ueber alle Zeilen — das ist der Produktivfall. Der
    Parameter existiert, damit ein Test seine Wirkung auf sein eigenes Fixture
    begrenzen kann: Die Suite laeuft gegen die Produktiv-Datenbank, und ein
    globaler Lauf fasst deren Ziele mit an.

    **Kein Filter auf das Gegenueber**, obwohl `ziele` seit Chat 125 das Paar
    traegt: Der Verfall misst Zeit, nicht Beziehung. Ein Ziel, das seit zwei
    Wochen niemand angeruehrt hat, ist in jeder Beziehung gleich weit
    verblasst, und ein Lauf je Paar ergaebe dasselbe Ergebnis in mehr
    Statements. Ein Parameter dafuer waere heute ohne Aufrufer und damit eine
    ungepruefte Verzweigung.

    Vorbedingung: Postgres erreichbar, Spalten motivation_basis/-_am vorhanden.
    Nachbedingung: Jedes aktive Ziel des Typs mit Anker traegt einen aus Anker
    und Zeit berechneten Wert; keines liegt aktiv unter der Schwelle.
    Fehlerfaelle: DB-Fehler -> Rollback, Zaehlwerk mit `error`, kein Teilstand.

    Returns:
        {"verarbeitet": int, "deaktiviert": int, "ohne_anker": int,
         "error": str | None}
    """
    # ── Eingabe-Validierung ─────────────────────
    if halbwertszeit_tage <= 0:
        fehlertext: str = (
            f"ziel_decay_lauf: Halbwertszeit {halbwertszeit_tage} Tage ist kein "
            f"gueltiger Zeitraum — Lauf abgebrochen, nichts geschrieben"
        )
        logger.error(fehlertext)
        return {"verarbeitet": 0, "deaktiviert": 0, "ohne_anker": 0, "error": fehlertext}

    if not 0.0 <= deaktivierungs_schwelle <= 1.0:
        fehlertext = (
            f"ziel_decay_lauf: Schwelle {deaktivierungs_schwelle} liegt ausserhalb "
            f"[0.0, 1.0] — Lauf abgebrochen, nichts geschrieben"
        )
        logger.error(fehlertext)
        return {"verarbeitet": 0, "deaktiviert": 0, "ohne_anker": 0, "error": fehlertext}

    conn = None
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        # ── Verarbeitung ────────────────────────
        # %s IS NULL als Passierschein: ohne user_id greift die Bedingung fuer
        # jede Zeile, mit user_id genau fuer die des Nutzers. Ein zweiter
        # Query-Zweig waere eine zweite Stelle, an der die Filter auseinanderlaufen.
        cursor.execute(
            """
            SELECT count(*) FROM ziele
            WHERE aktiv = TRUE AND ziel_typ = %s AND motivation_basis IS NULL
              AND (%s IS NULL OR user_id = %s)
            """,
            (ziel_typ, user_id, user_id),
        )
        ohne_anker: int = cursor.fetchone()[0]

        cursor.execute(
            """
            UPDATE ziele
            SET motivation = motivation_basis
                    * exp(-%s * (EXTRACT(EPOCH FROM (NOW() - motivation_basis_am)) / 86400.0))
            WHERE aktiv = TRUE
              AND ziel_typ = %s
              AND motivation_basis IS NOT NULL
              AND motivation_basis_am IS NOT NULL
              AND (%s IS NULL OR user_id = %s)
            """,
            (math.log(2) / halbwertszeit_tage, ziel_typ, user_id, user_id),
        )
        verarbeitet: int = cursor.rowcount

        # Liest die eben geschriebenen Werte (read-your-writes, selbe Transaktion).
        cursor.execute(
            """
            UPDATE ziele
            SET aktiv = FALSE, aktualisiert_am = NOW()
            WHERE aktiv = TRUE AND ziel_typ = %s AND motivation < %s
              AND (%s IS NULL OR user_id = %s)
            RETURNING id, zielsatz, motivation
            """,
            (ziel_typ, deaktivierungs_schwelle, user_id, user_id),
        )
        deaktivierte: list = cursor.fetchall()

        conn.commit()

        # ── Ausgabe-Verifikation ────────────────
        for ziel_id, zielsatz, motivation in deaktivierte:
            logger.info(
                f"ZielDecay: id={ziel_id} deaktiviert — motivation={motivation:.4f} "
                f"< {deaktivierungs_schwelle}, '{(zielsatz or '')[:50]}'"
            )

        if ohne_anker:
            logger.error(
                f"ZielDecay: {ohne_anker} aktive Ziele vom Typ '{ziel_typ}' tragen "
                f"keinen motivation_basis — nicht verfallen, nicht deaktiviert. "
                f"Ein Schreiber setzt den Anker nicht"
            )

        logger.info(
            f"ZielDecay: {verarbeitet} Ziele vom Typ '{ziel_typ}' materialisiert, "
            f"{len(deaktivierte)} deaktiviert, Halbwertszeit {halbwertszeit_tage} Tage"
        )
        return {
            "verarbeitet":  verarbeitet,
            "deaktiviert":  len(deaktivierte),
            "ohne_anker":   ohne_anker,
            "error":        None,
        }

    except psycopg2.Error as fehler:
        if conn:
            conn.rollback()
        fehlertext = f"ziel_decay_lauf fehlgeschlagen: {fehler}"
        logger.exception(fehlertext)
        return {"verarbeitet": 0, "deaktiviert": 0, "ohne_anker": 0, "error": fehlertext}

    finally:
        if conn:
            conn.close()


def ziel_deaktivieren(postgres_url: str, ziel_id: int) -> bool:
    """Deaktiviert ein Ziel (soft delete).

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
        ziel_id: ID des Ziels.

    Returns:
        True bei Erfolg, False bei Fehler.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE ziele SET aktiv = FALSE, aktualisiert_am = NOW() WHERE id = %s",
            (ziel_id,),
        )

        conn.commit()
        conn.close()

        logger.info(f"Ziel deaktiviert: id={ziel_id}")
        return True

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Ziel deaktivieren fehlgeschlagen")
        return False


async def ziele_embeddings_sicherstellen(
    postgres_url: str,
) -> None:
    """Erzeugt Embeddings für Ziele die noch keins haben (Startup-Repair).

    Analog zu entitaeten_embeddings_sicherstellen in chat.py.

    Läuft im FastAPI-Lifespan im Haupt-Event-Loop und nutzt deshalb die
    async-API des EmbedWorkers direkt (submit), nicht die sync-Brücke
    (submit_sync würde den eigenen Loop blockierend belauern → Deadlock).

    Args:
        postgres_url: PostgreSQL-Verbindungs-URL.
    """
    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, zielsatz FROM ziele WHERE embedding IS NULL AND aktiv = TRUE"
        )

        rows = cursor.fetchall()
        conn.close()

    except Exception as fehler:
        logger.warning(f"Ziele Embedding-Repair: DB-Abfrage fehlgeschlagen — {fehler}")
        return

    if not rows:
        logger.debug("Ziele Embedding-Repair: Alle Ziele haben Embeddings")
        return

    for ziel_id, zielsatz in rows:
        try:
            request = EmbedRequest(text=embed_text_bauen(zielsatz))
            embed_response = await model_service.embed.submit(request)
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Ziele-Repair: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )

            conn   = psycopg2.connect(postgres_url)
            cursor = conn.cursor()

            embedding_str: str = embedding_zu_pgvector_str(embedding)
            cursor.execute(
                "UPDATE ziele SET embedding = %s::vector WHERE id = %s",
                (embedding_str, ziel_id),
            )

            conn.commit()
            conn.close()

            logger.info(
                f"Ziel id={ziel_id}: Embedding nachträglich erzeugt — "
                f"'{zielsatz[:60]}'"
            )

        except Exception as fehler:
            logger.warning(f"Ziele Embedding-Repair für id={ziel_id} fehlgeschlagen: {fehler}")
