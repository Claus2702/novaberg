"""
Enricher Node — Reichert den State mit Kontext aus dem Gedaechtnis an.

Dispatcher-Architektur (Phase 4):
  enrich()             — Dispatcher nach ei_calc_rolle
  _enrich_human()      — Schlanker HumanGraph-Lauf (nur produktive Outputs)
  _enrich_character()  — Voller CharacterGraph-Lauf (1:1 zum bisherigen
                         enrich-Verhalten)

Kern-Quellen im CG-Lauf:
  1. Session-Kontext
  2. KZG/LZG (nur wenn Eintraege existieren)
  3. Charakter-Hash

Plugin-Quellen (dynamisch, nur im CG-Lauf):
  4. Jeder registrierte Manager mit enrich()-Hook
     z.B. FaktenManager → Fakten laden
          TimelineManager → anstehende Termine
          NotizenManager → betroffene Notiz bei Management-Intent

Im HG-Lauf entfallen Plugin-Hooks, Memory-Search (KZG/LZG), Charakter-
Hash-ContextEntry und emotionale Gravitation — kein HG-Konsument liest
diese Felder.

Kein LLM-Aufruf — nur Datenzugriff und Embedding-Erzeugung.
"""

import json
import logging

import psycopg2
import redis

from config import (
    ASSISTANT_USER_ID,
)
from graph.context_entry import ContextEntry
from graph.state         import ConversationState
from memory.kzg          import kzg_entries_retrieve, _kzg_prefix
from memory.lzg_knoten   import spreading_lesen
from memory.utils        import embedding_zu_pgvector_str
from memory.session      import session_turns_retrieve, _session_key
from memory.ziele        import ziele_aktive_laden
from memory.pipeline_log import (
    span_start,
    span_end,
    log_eingang,
    log_berechnung,
    log_switch,
    log_ausgabe,
)
from ei.gravitation      import (
    ziel_gravitation_berechnen,
    gravitationsterm_berechnen,
    emotionale_gravitation_scannen,
)
from ei.dreischicht      import CLUSTER_ENRICHER_SPRUENGE
from plugins             import get_registry
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.enricher")

# Default-Cluster fuer den Spreading-Lesepfad (§8.2.1), wenn der Vorturn-Cluster
# nicht aus Redis gv:detail gelesen werden kann. paradox = Konzept-Default, Tiefe 1.
SPREADING_DEFAULT_CLUSTER: str = "paradox"


# ═══════════════════════════════════════════════════════════════════
# Dispatcher
# ═══════════════════════════════════════════════════════════════════

def enrich(
    state:        ConversationState,
    redis_client: redis.Redis,
    postgres_url: str,
    user_id:      str,
) -> ConversationState:
    """Dispatcher: verzweigt nach ei_calc_rolle in HG- oder CG-Pfad.

    Vorbedingung: state ist ein valider ConversationState.
    Nachbedingung: bei rolle="user" sind die produktiven HG-Outputs
                   gesetzt; bei rolle="character" (oder fehlendem/
                   unbekanntem Marker) der volle CG-Lauf.
    Fallback: fehlt oder ist der Marker unbekannt, laeuft der CG-
              Vollpfad — sicherer Default, kein Funktionsverlust.
    """

    # ── Eingabe-Validierung ─────────────────────
    rolle: str = state.get("ei_calc_rolle", "character")

    # ── Verarbeitung ────────────────────────────
    if rolle == "user":
        return _enrich_human(
            state, redis_client, postgres_url, user_id,
        )

    return _enrich_character(
        state, redis_client, postgres_url, user_id,
    )


# ═══════════════════════════════════════════════════════════════════
# Helper — gemeinsame produktive Schritte
# ═══════════════════════════════════════════════════════════════════

def _load_raw_turns(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> list[dict]:
    """Laedt rohe Session-Turns aus Redis.

    Vorbedingung: Redis-Client ist verbunden.
    Nachbedingung: liefert Turn-Liste (kann leer sein bei Cold-Start).
    """
    return session_turns_retrieve(redis_client, user_id, character_id)


def _extract_user_intentionen(raw_turns: list[dict]) -> list:
    """Liest Intentionen aus dem juengsten User-Turn mit modus.

    Vorbedingung: raw_turns ist eine Liste (kann leer sein).
    Nachbedingung: Liste der Intentionen aus dem juengsten User-Turn
                   mit gesetztem modus; leere Liste falls keiner.
    """

    # ── Verarbeitung ────────────────────────────
    for turn in reversed(raw_turns):
        if turn.get("rolle") == "user" and turn.get("modus"):
            return turn.get("intentionen", [])

    # ── Ausgabe ─────────────────────────────────
    return []


def _create_prompt_embedding(
    state: ConversationState,
) -> list[float]:
    """Erzeugt das Embedding fuer den aktuellen User-Prompt.

    Vorbedingung: state["user_prompt"] vorhanden und nicht leer.
    Nachbedingung: liefert Embedding-Vektor.
    """
    request = EmbedRequest(text=state["user_prompt"])
    embed_response = model_service.embed.submit_sync(request)
    embedding = embed_response.embedding
    logger.debug(
        "Enricher: Prompt-Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
        len(embedding),
        embed_response.duration_seconds,
    )
    return embedding


def _compute_ziele_und_gravitation(
    embedding:    list[float],
    postgres_url: str,
) -> tuple[list[dict], float]:
    """Laedt aktive Ziele, berechnet Aktivierung und Gravitationsterm.

    Vorbedingung: embedding gueltig, postgres_url verbunden.
    Nachbedingung: Tupel (aktivierte_ziele_dicts, gravitationsterm).
                   Beide leer / 0.0, wenn keine Ziele vorhanden sind.
    """

    # ── Eingabe-Validierung ─────────────────────
    ziele: list[dict] = ziele_aktive_laden(postgres_url, user_id=ASSISTANT_USER_ID)

    if not ziele:
        return [], 0.0

    # ── Verarbeitung ────────────────────────────
    aktiviert: list = ziel_gravitation_berechnen(embedding, ziele)

    aktivierte_dicts: list[dict] = [
        {
            "ziel_id":     g.ziel_id,
            "ziel_typ":    g.ziel_typ,
            "zielsatz":    g.zielsatz,
            "motivation":  g.motivation,
            "emotion":     g.emotion,
            "arousal":     g.arousal,
            "similarity":  g.similarity,
            "gravitation": g.gravitation,
        }
        for g in aktiviert
    ]
    grav: float = gravitationsterm_berechnen(aktiviert)

    # ── Ausgabe ─────────────────────────────────
    return aktivierte_dicts, grav


# ═══════════════════════════════════════════════════════════════════
# HumanGraph-Pfad — schlanker Lauf
# ═══════════════════════════════════════════════════════════════════

def _enrich_human(
    state:        ConversationState,
    redis_client: redis.Redis,
    postgres_url: str,
    user_id:      str,
) -> ConversationState:
    """Schlanker HumanGraph-Lauf — schreibt nur produktive Outputs.

    Produktive Felder im HG: raw_turns, user_intentionen,
       prompt_embedding, aktivierte_ziele, gravitationsterm.

    Bewusst nicht geschrieben (kein HG-Konsument): session_turns,
       memory_entries, memory_context, emotionale_gravitationspunkte,
       Plugin-Outputs, KZG/LZG-Eintraege, Charakter-Hash.

    Vorbedingung: state["ei_calc_rolle"] == "user", state["user_prompt"]
                  vorhanden.
    Nachbedingung: die fuenf produktiven Felder oben sind im state
                   gesetzt.
    """

    # ── Pipeline-Log: Span-Start ────────────────
    turn_id_log:  str = state.get("turn_id", "unbekannt")
    quelle_log:   str = state.get("ei_calc_rolle", "user")
    character_id: str = state.get("character_id", "")
    span_id           = span_start(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = quelle_log,
        user_id      = user_id,
        character_id = character_id,
    )

    # ── Verarbeitung ────────────────────────────

    # 1. Rohe Session-Turns aus Redis.
    raw_turns: list[dict] = _load_raw_turns(redis_client, user_id, character_id)
    state["raw_turns"] = raw_turns

    # 2. User-Intentionen aus juengstem User-Turn.
    letzte_intentionen: list = _extract_user_intentionen(raw_turns)
    state["user_intentionen"] = letzte_intentionen

    if letzte_intentionen:
        logger.info(
            f"Enricher (HG): User-Intentionen aus letztem Turn: {letzte_intentionen}"
        )

    log_eingang(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "session",
        inhalt  = {
            "user_id":         user_id,
            "character_id":    character_id,
            "raw_turns_count": len(raw_turns) if raw_turns else 0,
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # 3. Prompt-Embedding (fuer Ziel-Gravitation).
    embedding: list[float] = _create_prompt_embedding(state)
    state["prompt_embedding"] = embedding

    log_berechnung(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "embedding",
        inhalt  = {
            "prompt_length": len(state.get("user_prompt", "")),
            "embedding_dim": len(embedding) if embedding else 0,
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # 4 + 5. Aktivierte Ziele + Gravitationsterm.
    aktivierte_ziele, gravitationsterm = _compute_ziele_und_gravitation(
        embedding, postgres_url,
    )
    state["aktivierte_ziele"] = aktivierte_ziele
    state["gravitationsterm"] = gravitationsterm

    if aktivierte_ziele:
        logger.info(
            f"Enricher (HG): {len(aktivierte_ziele)} Ziele aktiviert, "
            f"Gravitationsterm={gravitationsterm:.3f}"
        )

    # ── Ausgabe-Verifikation ────────────────────
    log_ausgabe(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "state",
        inhalt  = {
            "raw_turns_count":        len(state.get("raw_turns", [])),
            "user_intentionen_count": len(state.get("user_intentionen", [])),
            "embedding_dim":          len(state.get("prompt_embedding") or []),
            "aktivierte_ziele_count": len(state.get("aktivierte_ziele", [])),
            "gravitationsterm":       state.get("gravitationsterm", 0.0),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    span_end(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = quelle_log,
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    return state


# ═══════════════════════════════════════════════════════════════════
# CharacterGraph-Pfad — voller Lauf (1:1 zum bisherigen enrich)
# ═══════════════════════════════════════════════════════════════════

def _vorturn_cluster_lesen(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> str:
    """Liest den GV-Cluster des vorigen Turns aus Redis (§8.2.1).

    Der GV-Node laeuft nach dem Enricher, daher ist der Cluster des aktuellen
    Turns noch nicht berechnet. Der Dispatcher des Vorturns legt ihn unter
    ``gv:detail:{user_id}:{character_id}`` als JSON ab (Feld ``cluster``).

    Fallback bei fehlendem Key, Parse-Fehler oder fehlendem Feld:
    SPREADING_DEFAULT_CLUSTER (paradox, Tiefe 1).
    """
    key: str = f"gv:detail:{user_id}:{character_id}"
    try:
        roh = redis_client.get(key)
        if roh:
            cluster = (json.loads(roh) or {}).get("cluster")
            if cluster:
                logger.info(f"Spreading: Cluster '{cluster}' aus Redis-Vorturn ({key})")
                return cluster
            logger.info(
                f"Spreading: gv:detail ohne 'cluster' — Default '{SPREADING_DEFAULT_CLUSTER}'"
            )
        else:
            logger.info(
                f"Spreading: kein gv:detail im Vorturn — Default '{SPREADING_DEFAULT_CLUSTER}'"
            )
    except Exception as exc:
        logger.warning(
            f"Spreading: gv:detail-Lesen/Parse fehlgeschlagen ({exc}) — "
            f"Default '{SPREADING_DEFAULT_CLUSTER}'"
        )
    return SPREADING_DEFAULT_CLUSTER


def _enrich_character(
    state:        ConversationState,
    redis_client: redis.Redis,
    postgres_url: str,
    user_id:      str,
) -> ConversationState:
    """Voller CharacterGraph-Lauf — funktional 1:1 zum bisherigen enrich.

    Sammelt Kontext aus Kern-Quellen (Session, KZG/LZG, Charakter-Hash),
    laesst Plugin-Hooks laufen, baut Ziel- und emotionale Gravitation
    und schreibt memory_entries fuer den nachgelagerten Reducer.

    Vorbedingung: state ist valider ConversationState, state["user_prompt"]
                  und character_id gesetzt.
    Nachbedingung: alle CG-konsumierten Felder im state gesetzt
                   (raw_turns, session_turns, user_intentionen,
                   prompt_embedding, memory_entries, aktivierte_ziele,
                   gravitationsterm, emotionale_gravitationspunkte).
    """

    # ── Pipeline-Log: Span-Start (Anker 1) ──────
    # ei_calc_rolle ist projektweit etablierter Marker (siehe
    # graph/character_graph.py:43, kzg/dispatch.py:42).
    turn_id_log: str = state.get("turn_id", "unbekannt")
    quelle_log:  str = state.get("ei_calc_rolle", "user")
    span_id          = span_start(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = quelle_log,
        user_id      = user_id,
        character_id = character_id,
    )

    entries: list[ContextEntry] = []

    # ─────────────────────────────────────────
    # 1. Session-Kontext (immer, als erstes)
    # ─────────────────────────────────────────

    # Session-Summary in den Kontext (aeltere Turns, zusammengefasst)
    character_id: str = state.get("character_id", "")
    summary_key: str  = _session_key(user_id, character_id, "summary")
    summary:     str  = redis_client.get(summary_key) or ""

    if summary:
        entries.append({
            "quelle":  "summary",
            "subtyp":  "",
            "inhalt":  summary,
            "gewicht": 1.0,
            "meta":    {},
        })
        logger.info("Enricher: Session-Summary geladen (1 Eintrag)")

    # Rohe Turns laden
    raw_turns: list[dict] = _load_raw_turns(redis_client, user_id, character_id)
    state["raw_turns"] = raw_turns

    # Session-Turns vollstaendig durchreichen — kein Datenverlust.
    # Formatierung ist Sache der konsumierenden Nodes.
    gefilterte_turns: list[dict] = []

    for turn in raw_turns:
        # Shadow-Impulse ausblenden
        if turn.get("kern") and turn["kern"].startswith("[Nova-Impuls]"):
            continue

        gefilterte_turns.append(turn)

    state["session_turns"] = gefilterte_turns

    # Intentionen aus dem letzten User-Turn ableiten (vom Dispatcher
    # gelesen). Modus und Emotion liegen seit Phase 3 in den Personality-
    # Klassen — keine Spiegelung mehr.
    letzte_intentionen: list = _extract_user_intentionen(raw_turns)
    state["user_intentionen"] = letzte_intentionen

    if letzte_intentionen:
        logger.info(
            f"Enricher: User-Intentionen aus letztem Turn: {letzte_intentionen}"
        )

    # ── Pipeline-Log: Eingang (Anker 2) ─────────
    # Session-Kontext geladen, vor Plugin-Loop und Memory-Suche.
    log_eingang(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "session",
        inhalt  = {
            "user_id":              user_id,
            "character_id":         character_id,
            "raw_turns_count":      len(raw_turns) if raw_turns else 0,
            "filtered_turns_count": len(gefilterte_turns) if gefilterte_turns else 0,
            "has_summary":          bool(summary),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # ─────────────────────────────────────────
    # 2. Plugin-Hooks: enrich() aller Manager
    # ─────────────────────────────────────────
    registry: dict = get_registry()

    for name, manager in registry.items():
        # DEAKTIVIERT Chat 71 — Fakten-Enrichment produziert 130+ Rausch-Eintraege
        # Wird reaktiviert nach Fakten-Bereinigung
        if name == "fakten":
            # plugin_entries = manager.enrich_entries(state, postgres_url)
            logger.info("Enricher: Fakten-Enrichment deaktiviert (Chat 71)")
            continue

        try:
            plugin_entries: list[ContextEntry] = manager.enrich_entries(state, postgres_url)

            if plugin_entries:
                entries.extend(plugin_entries)
                logger.info(
                    f"Enricher: Plugin '{name}' lieferte {len(plugin_entries)} Eintraege"
                )

        except Exception as fehler:
            logger.error(f"Enricher: Plugin '{name}' Fehler — {fehler}")

    # ─────────────────────────────────────────
    # 3. KZG/LZG semantische Suche
    # ─────────────────────────────────────────
    kzg_keys: list = redis_client.keys(_kzg_prefix(user_id, character_id))
    has_lzg:  bool = False

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM lzg_knoten "
            "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE)",
            (user_id, character_id),
        )
        has_lzg = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    # Prompt-Embedding (fuer KZG/LZG + Gravitation)
    embedding: list[float] = _create_prompt_embedding(state)

    # In den State stellen, damit der Dispatcher es spaeter neben dem
    # User-Turn in der Session ablegen kann (Gravitationsgraph-Panel).
    state["prompt_embedding"] = embedding

    # ── Pipeline-Log: Berechnung (Anker 3) ──────
    # Prompt-Embedding erzeugt. Dimensions-Check als Plausibilitaets-Anker:
    # erwartet werden 768 (nomic-embed-text).
    log_berechnung(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "embedding",
        inhalt  = {
            "prompt_length":  len(state.get("user_prompt", "")),
            "embedding_dim":  len(embedding) if embedding else 0,
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # Lokale Initialisierung, damit der Switch-Inhalt unten den KZG-Count
    # unabhaengig vom Pfad sicher referenzieren kann. Die Spreading-Erinnerungen
    # zaehlt der Switch aus state["lzg_resonanz"] (kein memory_entries-Akkumulator).
    kzg_entries: list[ContextEntry] = []

    if kzg_keys or has_lzg:
        logger.info(
            f"Enricher: {len(kzg_keys)} KZG, LZG={'ja' if has_lzg else 'nein'} — suche Kontext..."
        )

        if kzg_keys:
            kzg_entries = kzg_entries_retrieve(
                redis_client, user_id, character_id, embedding,
            )
            if kzg_entries:
                entries.extend(kzg_entries)
                logger.info(f"Enricher: KZG lieferte {len(kzg_entries)} Eintraege")

        if has_lzg:
            # B2 (§8.1-8.4): gerichteter Spreading-Lesepfad statt flachem LZG-Read.
            # Cluster aus dem Redis-Vorturn (GV-Node laeuft nach dem Enricher, §8.2.1).
            cluster: str = _vorturn_cluster_lesen(redis_client, user_id, character_id)

            # Novas dominante Emotion des aktuellen Turns: [0] ist die staerkste
            # (Verlauf in allen ei_calc-Pfaden absteigend nach Gewicht sortiert).
            # Empty-Guard: leer/fehlend -> "" (Neutral-Faktor 1.0 in _sektor_faktor).
            nova_verlauf: list = state.get("nova_emotions_verlauf") or []
            nova_emotion: str = nova_verlauf[0]["emotion"] if nova_verlauf else ""

            embedding_str: str = embedding_zu_pgvector_str(embedding)
            erinnerungen: list[dict] = spreading_lesen(
                postgres_url, user_id, character_id, embedding_str,
                cluster=cluster, nova_emotion=nova_emotion,
            )

            # §8.4.2: lzg_resonanz — Kontext-Rahmen + Top-3-Erinnerungen mit Pfad.
            # Einzige Transport-Quelle der Spreading-Erinnerungen: der Reducer
            # reicht sie an den Formatter, der den [GEDAECHTNIS]-Block rendert
            # (§8.4.3/§8.4.4). Keine flache Einspeisung in memory_entries mehr.
            state["lzg_resonanz"] = {
                "anker_anzahl": 3,
                "sprung_tiefe": CLUSTER_ENRICHER_SPRUENGE.get(cluster, 1),
                "cluster":      cluster,
                "nova_sektor":  nova_emotion,
                "erinnerungen": erinnerungen,
            }
            logger.info(
                f"Enricher: Spreading-Lesepfad lieferte {len(erinnerungen)} "
                f"Erinnerungen (lzg_resonanz)"
            )

        # ── Pipeline-Log: Switch — Memory aktiv (Anker 4a) ──
        log_switch(
            turn_id = turn_id_log,
            node    = "enricher",
            quelle  = "memory",
            inhalt  = {
                "kzg_keys_count":     len(kzg_keys),
                "has_lzg":            has_lzg,
                "kzg_entries_count":  len(kzg_entries),
                "lzg_resonanz_count": len((state.get("lzg_resonanz") or {}).get("erinnerungen", [])),
                "zweig":              "memory_aktiv",
            },
            span_id = span_id,
            user_id      = user_id,
            character_id = character_id,
        )
    else:
        # ── Pipeline-Log: Switch — Memory uebersprungen (Anker 4b) ──
        log_switch(
            turn_id = turn_id_log,
            node    = "enricher",
            quelle  = "memory",
            inhalt  = {
                "kzg_keys_count":  0,
                "has_lzg":         False,
                "zweig":           "memory_uebersprungen",
            },
            span_id = span_id,
            user_id      = user_id,
            character_id = character_id,
        )

    # ─────────────────────────────────────────
    # 4. Charakter-Hash als ContextEntry
    #     Der Hash-String wird inline aus external.character.core/adaptive
    #     formatiert und in memory_entries gehaengt. Geladen wird er im
    #     db_zugriff-Node (CharacterGraph) — im HumanGraph ist external
    #     leer und der Eintrag entfaellt.
    # ─────────────────────────────────────────
    external_perso = state.get("external")

    char_hash: str = ""
    if external_perso and (external_perso.character.core or external_perso.character.adaptive):
        parts: list[str] = []
        if external_perso.character.core:
            parts.append(f"Kern-Persoenlichkeit: {external_perso.character.core}")
        if external_perso.character.adaptive:
            parts.append(f"Aktuelle Phase: {external_perso.character.adaptive}")
        char_hash = "\n".join(parts)

    if char_hash:
        entries.append({
            "quelle":  "charakter",
            "subtyp":  "",
            "inhalt":  char_hash,
            "gewicht": 1.0,
            "meta":    {},
        })
        logger.info("Enricher: Charakter-Hash aus external.character als ContextEntry")

    # ─────────────────────────────────────────
    # 5. Ziele + Gravitation (Drive)
    # ─────────────────────────────────────────
    aktivierte_ziele, gravitationsterm = _compute_ziele_und_gravitation(
        embedding, postgres_url,
    )
    state["aktivierte_ziele"] = aktivierte_ziele
    state["gravitationsterm"] = gravitationsterm

    if aktivierte_ziele:
        logger.info(
            f"Enricher: {len(aktivierte_ziele)} Ziele aktiviert, "
            f"Gravitationsterm={gravitationsterm:.3f}"
        )

    # ─────────────────────────────────────────
    # 6. Emotionale Gravitation (EI Phase 3)
    # ─────────────────────────────────────────
    emotionale_punkte: list[dict] = emotionale_gravitation_scannen(
        turn_embedding=embedding,
        redis_client=redis_client,
        postgres_url=postgres_url,
        user_id=user_id,
        character_id=character_id,
    )

    state["emotionale_gravitationspunkte"] = emotionale_punkte

    if emotionale_punkte:
        logger.info(
            f"Enricher: {len(emotionale_punkte)} emotionale Gravitationspunkte — "
            f"staerkster: {emotionale_punkte[0].get('emotion', '?')} "
            f"(grav={emotionale_punkte[0].get('gravitation', 0):.3f}, "
            f"quelle={emotionale_punkte[0].get('quelle', '?')})"
        )
    else:
        logger.debug("Enricher: Keine emotionalen Gravitationspunkte")

    # ─────────────────────────────────────────
    # State aktualisieren
    # ─────────────────────────────────────────
    state["memory_entries"] = entries

    if not entries:
        logger.info("Enricher: Pipeline abgeschlossen, 0 Eintraege gesammelt")
    else:
        logger.info(f"Enricher: Pipeline abgeschlossen, {len(entries)} Eintraege gesammelt")

    # ── Pipeline-Log: Ausgabe (Anker 5) ─────────
    # Zustand des State am Enricher-Ausgang.
    log_ausgabe(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "state",
        inhalt  = {
            "memory_entries_count":              len(state.get("memory_entries", [])),
            "aktivierte_ziele_count":            len(state.get("aktivierte_ziele", [])),
            "gravitationsterm":                  state.get("gravitationsterm", 0.0),
            "emotionale_gravitationspunkte_count": len(
                state.get("emotionale_gravitationspunkte", [])
            ),
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # ── Pipeline-Log: Span-End (Anker 6) ────────
    span_end(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = quelle_log,
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    return state
