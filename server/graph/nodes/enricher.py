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

~~Kein LLM-Aufruf — nur Datenzugriff und Embedding-Erzeugung.~~
Seit dem 20.08.2026 **ein** Modellaufruf: das Query Rewriting, das aus dem
Verlauf den Suchschluessel formt (`_suchtext_bauen`). Alles andere bleibt
Datenzugriff und Embedding-Erzeugung.
"""

import json
import logging

import psycopg2
import redis

from config              import (
    PROMPTS,
    QUERY_REWRITE_AKTIV,
    QUERY_REWRITE_FRIST_S,
    QUERY_REWRITE_MAX_ZEICHEN,
    QUERY_REWRITE_MIN_TURNS,
    get_node_config,
)
from services.model_services import ChatRequest
from graph.context_entry import ContextEntry
from graph.reiz          import reiz_text
from graph.state         import ConversationState, pipeline_quelle
from memory.kzg          import kzg_entries_retrieve, _kzg_prefix
from memory.lzg_knoten   import spreading_lesen
from memory.utils        import embedding_zu_pgvector_str
from memory.session      import session_turns_retrieve, _session_key
from memory.ziele        import ziel_paar_bestimmen, ziele_aktive_laden
from memory.pipeline_log import (
    span_start,
    span_end,
    log_eingang,
    log_berechnung,
    log_switch,
    log_ausgabe,
)
from ei.gravitation      import (
    Verschiebung,
    ziel_gravitation_berechnen,
    gravitationsterm_berechnen,
    emotionale_gravitation_scannen,
    wahrnehmung_verschieben,
)
from agents.dateien_index.aufzeichnungen import (
    Aufzeichnungsfund,
    aufzeichnungen_suchen,
)
from ei.dreischicht      import CLUSTER_ENRICHER_SPRUENGE, INTENTION_ANWEISUNG
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


def _intentionen_bestimmen(aus_ereignis: list, raw_turns: list[dict]) -> list:
    """Entscheidet, woher die Intentionen des aktuellen Turns stammen.

    **Der Wert aus dem Ereignis gewinnt.** Pfad 1 erhebt die Intentionen im
    Salienz-Node fuer genau diesen Turn und reicht sie mit dem Ereignis
    herueber. Die Ableitung aus `raw_turns` sieht denselben Wert nur, wenn der
    Dispatcher von Pfad 1 den Session-Turn schon geschrieben hat — eine
    Reihenfolge zwischen zwei Graphen, auf die sich nichts verlassen sollte.

    Der Rueckfall bleibt fuer Laeufe **ohne** Nutzeraeusserung: Ein eigener
    Impuls traegt keine Intentionen im Ereignis, hat aber eine Vorgeschichte.

    Ohne diesen Vorrang ueberschriebe der Enricher die Quelle von M1 der
    Initiative-Achse, und zwar sechs Nodes bevor die Achse sie liest.

    Vorbedingung: keine. Beide Argumente duerfen leer sein.
    Nachbedingung: (Liste der Intentionen, Herkunftsname). Die Liste ist
        leer, wenn keine der beiden Quellen etwas hat.
    Fehlerfaelle: keine — ein leeres Ergebnis ist ein legitimer Zustand und
        wird vom Empfaenger als **fehlend** gewertet, nicht als "keine
        Richtung" (`ei/initiative.py`).

    Returns:
        (Intentionen, Herkunftsname fuer die Logzeile)
    """
    # ── Eingabe-Validierung ─────────────────────
    # Keine: Jede Kombination aus leer und gefuellt ist entscheidbar.

    # ── Verarbeitung ────────────────────────────
    if aus_ereignis:
        return list(aus_ereignis), "Ereignis"

    # ── Ausgabe-Verifikation ────────────────────
    return _extract_user_intentionen(raw_turns), "letzter Session-Turn"


def _suchtext_bauen(
    state:     ConversationState,
    raw_turns: list[dict],
) -> tuple[str, str]:
    """Formt aus dem Gespraechsverlauf den Text, der den Suchschluessel traegt.

    **Warum nicht die rohe Aeusserung.** Ein Turn wie *„und wie weist man das
    nach?"* nennt seinen Gegenstand nicht — er zeigt auf ihn zurueck. Der
    Vektor daraus sucht ohne ihn, und zwar in allen drei Speichern zugleich,
    weil sie denselben Schluessel benutzen. Gemessen am 20.08.2026: Die rohe
    Aeusserung erreicht in **0 von 10** Faellen die Abrufschwelle, das Rewrite
    in **5 von 10**.

    **Die Antwort des Modells ist eine externe Quelle** und wird
    geprueft: erste Zeile, nicht leer, nicht laenger als die Plausibilitaets-
    grenze. Faellt sie durch, gilt die rohe Aeusserung — **laut**, nicht still.

    Vorbedingung: `raw_turns` ist eine Liste (darf leer sein); der Reiz ist
    gesetzt.
    Nachbedingung: liefert einen nicht-leeren Text und die Herkunft, aus der
    er stammt — `"rewrite"` oder einen benannten Grund fuer den Rueckfall.
    """
    # ── Eingabe ────────────────────────────────
    roh: str = reiz_text(state)
    if not roh:
        raise ValueError("Enricher: Reiz ist leer — kein Suchtext bildbar")
    if not QUERY_REWRITE_AKTIV:
        return roh, "abgeschaltet"
    if len(raw_turns) < QUERY_REWRITE_MIN_TURNS:
        return roh, "zu_wenig_verlauf"

    # ── Verarbeitung ───────────────────────────
    # Kein festes Fenster: Was die Session traegt, sieht das Modell. Ein `k`
    # muesste raten, wie weit ein Thema zurueckreicht.
    # Die Session legt ihre Turns unter `rolle` und `inhalt` ab, nicht unter
    # den englischen Namen des Chat-Formats. Am 20.08.2026 im Betrieb gemessen:
    # Mit `role`/`content` filterte die Bedingung **jeden** Turn weg, und das
    # Modell bekam die Aufgabe ohne Verlauf — es fragte danach, und die Frage
    # wurde zum Suchschluessel.
    namen: dict[str, str] = {"user": "Nutzer", "assistant": "Nova"}
    verlauf: str = "\n".join(
        f"{namen.get(t.get('rolle', 'user'), 'Nutzer')}: {t.get('inhalt', '')}"
        for t in raw_turns
        if t.get("inhalt")
    )
    # Ein leerer Verlauf bei vorhandenen Turns ist kein Randfall, sondern ein
    # Defekt am Feldnamen — und er darf nicht als Rewrite durchgehen.
    if not verlauf.strip():
        logger.error(
            "Enricher: Query-Rewrite bekaeme %d Turns ohne verwertbaren Inhalt "
            "— Feldnamen pruefen; der Suchschluessel traegt die rohe Aeusserung",
            len(raw_turns),
        )
        return roh, "verlauf_leer"
    node_cfg: dict = get_node_config("query_rewrite")
    chat_request = ChatRequest(
        messages          = [{
            "role":    "user",
            "content": PROMPTS["query_rewrite.task"].format(verlauf=verlauf),
        }],
        temperature       = node_cfg.get("temperature", 0.0),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "query_rewrite",
    )
    try:
        antwort: str = model_service.chat.submit_sync(
            chat_request, timeout=QUERY_REWRITE_FRIST_S,
        ).text
    except Exception as fehler:                       # noqa: BLE001 — jede Stoerung faellt zurueck
        logger.error(
            "Enricher: Query-Rewrite gescheitert (%s: %s) — der Suchschluessel "
            "traegt die rohe Aeusserung und damit keinen Rueckbezug",
            type(fehler).__name__, fehler,
        )
        return roh, "aufruf_gescheitert"

    # ── Ausgabe-Verifikation ───────────────────
    # Erste Zeile, und die Zerlegung darf keine leere Liste voraussetzen:
    # Eine Antwort aus reinem Weissraum ergibt genau die.
    zeilen: list[str] = (antwort or "").strip().splitlines()
    kandidat: str = zeilen[0].strip() if zeilen else ""
    kandidat = kandidat.strip('"').strip("'").strip()
    if kandidat.lower().startswith("suchanfrage:"):
        kandidat = kandidat.split(":", 1)[1].strip()

    if not kandidat:
        logger.error(
            "Enricher: Query-Rewrite lieferte nichts Verwertbares (%r) — "
            "der Suchschluessel traegt die rohe Aeusserung", antwort[:120],
        )
        return roh, "leer"
    if len(kandidat) > QUERY_REWRITE_MAX_ZEICHEN:
        logger.error(
            "Enricher: Query-Rewrite ist %d Zeichen lang (Grenze %d) und damit "
            "keine Suchanfrage — der Suchschluessel traegt die rohe Aeusserung",
            len(kandidat), QUERY_REWRITE_MAX_ZEICHEN,
        )
        return roh, "zu_lang"

    return kandidat, "rewrite"


def _create_prompt_embedding(
    state:    ConversationState,
    suchtext: str,
) -> list[float]:
    """Erzeugt das Embedding fuer den Reiz dieses Durchlaufs.

    Der Vektor ist der Suchschluessel fuer das Gedaechtnis **und** die Eingabe
    der Zielaktivierung. Er muss deshalb den Text tragen, um den es in diesem
    Turn geht — auf einem Impuls-Turn ist das Novas eigener Gedanke, und der
    Reiz-Platz ist dort leer.

    **Seit dem 20.08.2026 bettet er nicht mehr den Reiz selbst ein**, sondern
    den Text, den `_suchtext_bauen` daraus geformt hat — bei einem Turn mit
    Rueckbezug ist das die aufgeloeste Frage, sonst die rohe Aeusserung.

    Vorbedingung: `suchtext` ist nicht leer.
    Nachbedingung: liefert Embedding-Vektor.
    """
    if not suchtext:
        raise ValueError("Enricher: Suchtext ist leer — kein Embedding bildbar")
    request = EmbedRequest(text=suchtext)
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
    user_id:      str,
    character_id: str,
) -> tuple[list, float]:
    """Laedt die aktiven Ziele DIESES Paares, berechnet Aktivierung und Term.

    Das Turn-Paar wird uebergeben, nicht das Ziel-Paar: Die Ableitung steht in
    `ziel_paar_bestimmen` und gilt fuer beide Pfade des Enrichers, die ihr Paar
    in verschiedener Reihenfolge fuehren.

    Gibt die `ActivatedGoal`-Objekte zurueck, nicht die State-Dicts: Die
    Wahrnehmungs-Gravitation braucht das Ziel-Embedding, und das gehoert nicht
    in den State (`_ziele_als_dicts`).

    Vorbedingung: embedding gueltig, postgres_url verbunden, Turn-Paar gesetzt.
    Nachbedingung: Tupel (aktivierte_ziele, gravitationsterm), gebildet
                   ausschliesslich aus Zielen dieser Beziehung.
                   Beide leer / 0.0, wenn keine Ziele vorhanden sind.
    """
    # ── Eingabe-Validierung ─────────────────────
    ziel_subjekt, ziel_gegenueber = ziel_paar_bestimmen(user_id, character_id)
    ziele: list[dict] = ziele_aktive_laden(postgres_url, ziel_subjekt, ziel_gegenueber)

    if not ziele:
        return [], 0.0

    # ── Verarbeitung ────────────────────────────
    aktiviert: list = ziel_gravitation_berechnen(embedding, ziele)
    grav: float = gravitationsterm_berechnen(aktiviert)

    # ── Ausgabe ─────────────────────────────────
    return aktiviert, grav


def _ziele_als_dicts(aktiviert: list) -> list[dict]:
    """Bildet die aktivierten Ziele auf die State-Darstellung ab.

    **Das Ziel-Embedding bleibt draussen.** Es traegt die Verschiebungs-Rechnung
    im Enricher und hat im State keinen Leser; der Dispatcher legt
    `aktivierte_ziele` in Redis ab, und sieben Ziele mal 768 Werte je Turn waeren
    Ballast, den niemand liest.

    Vorbedingung: `aktiviert` enthaelt `ActivatedGoal`-Objekte (kann leer sein).
    Nachbedingung: Eine Liste gleicher Laenge mit acht flachen Feldern je Ziel.
    """
    return [
        {
            "ziel_id":              g.ziel_id,
            "ziel_typ":             g.ziel_typ,
            "zielsatz":             g.zielsatz,
            "motivation":           g.motivation,
            "emotion":              g.emotion,
            "arousal":              g.arousal,
            "similarity":           g.similarity,
            "aktivierungs_staerke": g.aktivierungs_staerke,
        }
        for g in aktiviert
    ]


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

    Vorbedingung: state["ei_calc_rolle"] == "user", der Reiz dieses
                  Durchlaufs vorhanden.
    Nachbedingung: die fuenf produktiven Felder oben sind im state
                   gesetzt.
    """
    # ── Pipeline-Log: Span-Start ────────────────
    turn_id_log:  str = state.get("turn_id", "unbekannt")
    # Quelle aus graph_rolle statt ei_calc_rolle: der AgentGraph setzt
    # ei_calc_rolle="character" und war im pipeline_log dadurch nicht vom
    # CharacterGraph zu unterscheiden. Die bestehenden Werte "user" und
    # "character" bleiben, damit alte Eintraege vergleichbar bleiben.
    quelle_log:   str = pipeline_quelle(state)
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
    # Roher Reiz, kein Rewrite: Dieser Pfad fuehrt keine Vektorsuche, und die
    # Zielaktivierung ist der Gegenstand, der am 20.08.2026 NICHT gemessen
    # wurde. Was ungemessen ist, wird nicht mitverschoben.
    embedding: list[float] = _create_prompt_embedding(state, reiz_text(state))
    state["prompt_embedding"] = embedding

    log_berechnung(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "embedding",
        inhalt  = {
            # Die Laenge des Textes, der wirklich eingebettet wurde. Stuende
            # hier der Reiz-Platz, meldete ein Impuls-Turn 0 Zeichen neben
            # einem 768er Vektor — und die Zeile saehe aus wie ein Ausfall.
            "prompt_length": len(reiz_text(state)),
            "embedding_dim": len(embedding) if embedding else 0,
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # 4 + 5. Aktivierte Ziele + Gravitationsterm.
    # Keine Wahrnehmungs-Gravitation im HG: Dieser Pfad fuehrt keine
    # Vektorsuche, es gibt keinen Suchschluessel zu verschieben.
    aktiviert, gravitationsterm = _compute_ziele_und_gravitation(
        embedding, postgres_url, user_id, character_id,
    )
    aktivierte_ziele: list[dict] = _ziele_als_dicts(aktiviert)
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


def _verschiebungs_protokoll(
    verschiebung: Verschiebung | None,
    anfrage_dim:  int,
) -> dict:
    """Baut den Protokoll-Inhalt der Wahrnehmungs-Gravitation.

    Ein zusammengesetzter Wert ist ohne seine Eingangsgroessen nicht
    beurteilbar, deshalb stehen die Aktivierungs-Staerken **einzeln** im
    Eintrag und nicht als Summe.

    `verschiebung=None` heisst: In diesem Turn lief **gar keine**
    Gedaechtnissuche — weder KZG noch LZG. Auch dieser Durchlauf bekommt
    einen Eintrag, sonst waere er von einem Turn ohne Verschiebung nicht zu
    unterscheiden.

    **Der Marker heisst seit dem 04.08.2026 `keine_gedaechtnis_suche`**, vorher
    `keine_lzg_suche`. Umbenannt, weil sich seine Bedeutung mit dem Umfang der
    Verschiebung geaendert hat: Solange nur das LZG den verschobenen Schluessel
    bekam, war „keine LZG-Suche" dasselbe wie „nichts zu verschieben"; seit das
    KZG mitzieht, ist es das nicht mehr. Denselben String weiterzuverwenden
    hiesse, Eintraege von vorher und nachher gleich aussehen zu lassen, obwohl
    sie Verschiedenes bedeuten — der Bruch gehoert in die Daten, nicht in eine
    Fussnote.

    Vorbedingung: keine.
    Nachbedingung: Eine Abbildung mit sieben Feldern; `herkunft` ist immer
        gesetzt und trennt die sieben Ausgaenge voneinander.
    """
    if verschiebung is None:
        return {
            "herkunft":       "keine_gedaechtnis_suche",
            "faktor":         0.0,
            "cluster":        "",
            "ziel_anteile":   [],
            "ziele_count":    0,
            "cosinus_zu_roh": 1.0,
            "anfrage_dim":    anfrage_dim,
        }

    return {
        "herkunft":       verschiebung.herkunft,
        "faktor":         verschiebung.faktor,
        "cluster":        verschiebung.cluster,
        "ziel_anteile":   verschiebung.ziel_anteile,
        "ziele_count":    len(verschiebung.ziel_anteile),
        "cosinus_zu_roh": verschiebung.cosinus_zu_roh,
        "anfrage_dim":    anfrage_dim,
    }


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

    Vorbedingung: state ist valider ConversationState, der Reiz dieses
                  Durchlaufs und character_id gesetzt.
    Nachbedingung: alle CG-konsumierten Felder im state gesetzt
                   (raw_turns, session_turns, user_intentionen,
                   prompt_embedding, memory_entries, aktivierte_ziele,
                   gravitationsterm, emotionale_gravitationspunkte).
    """
    # ── Pipeline-Log: Span-Start (Anker 1) ──────
    # ei_calc_rolle ist projektweit etablierter Marker (siehe
    # graph/character_graph.py:43, kzg/dispatch.py:42).
    turn_id_log: str = state.get("turn_id", "unbekannt")
    quelle_log:  str = pipeline_quelle(state)
    character_id: str = state.get("character_id", "")
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

    # Intentionen des Reizes. **Der Wert aus dem Ereignis gewinnt.**
    #
    # Pfad 1 erhebt sie im Salienz-Node fuer genau diesen Turn und reicht sie
    # mit dem Ereignis herueber. Die Ableitung aus `raw_turns` unten sieht
    # denselben Wert nur, wenn der Dispatcht von Pfad 1 den Session-Turn
    # bereits geschrieben hat — eine Reihenfolge zwischen zwei Graphen, auf
    # die sich nichts verlassen sollte. Sie bleibt als Rueckfall fuer Laeufe
    # ohne Nutzeraeusserung: Ein Eigen-Impuls traegt keine im Ereignis.
    #
    # Ohne diesen Vorrang ueberschriebe der Enricher die Quelle von M1 der
    # Initiative-Achse, und zwar sechs Nodes bevor die Achse sie liest.
    letzte_intentionen, herkunft = _intentionen_bestimmen(
        state.get("user_intentionen") or [], raw_turns,
    )
    state["user_intentionen"] = letzte_intentionen

    logger.info(
        "Enricher: User-Intentionen: %s (Quelle: %s)",
        letzte_intentionen or "keine", herkunft,
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
    # 2. Gedaechtnis-Suche (KZG, LZG) — Vorcheck
    # ─────────────────────────────────────────
    # Die Plugin-Hooks standen bis zum 04.08.2026 HIER, also vor dem
    # Prompt-Embedding. Ein Plugin, das ueber Embedding-Naehe sucht, haette
    # sich dreissig Zeilen vor dessen Erzeugung ein zweites rechnen lassen
    # muessen — rund 1,6 Sekunden je Turn fuer denselben Vektor. Sie stehen
    # jetzt hinter der Suche (Abschnitt 3b), damit jedes Plugin sowohl das
    # rohe Embedding als auch den verschobenen Suchschluessel vorfindet.
    kzg_keys:   list = redis_client.keys(_kzg_prefix(user_id, character_id))
    has_lzg:    bool = False
    has_wissen: bool = False

    try:
        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM lzg_knoten "
            "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE)",
            (user_id, character_id),
        )
        has_lzg = cursor.fetchone()[0]

        # Die Bibliothek ist die dritte Gedaechtnisschicht. Ihr Vorcheck steht
        # hier und nicht im Plugin, weil er darueber entscheidet, ob die
        # Verschiebung ueberhaupt gerechnet wird: Ein Turn, in dem nur die
        # Bibliothek Bestand hat, braucht denselben Suchschluessel wie einer
        # mit KZG.
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM autonomous_wissen "
            "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE)",
            (user_id, character_id),
        )
        has_wissen = cursor.fetchone()[0]
        conn.close()
    except Exception:
        pass

    # Prompt-Embedding (fuer die Ziel-Aktivierung) — am rohen Reiz.
    embedding: list[float] = _create_prompt_embedding(state, reiz_text(state))

    # In den State stellen, damit der Dispatcher es spaeter neben dem
    # User-Turn in der Session ablegen kann (Gravitationsgraph-Panel).
    state["prompt_embedding"] = embedding

    # ── Pipeline-Log: Berechnung (Anker 3) ──────
    # Prompt-Embedding erzeugt. Die Dimension wird hier nur GELOGGT, nicht
    # geprueft — erwartet werden 768 (nomic-embed-text-v2-moe, A4 Chat 107).
    # Harter Check fehlt repo-weit: EMBED-DIMENSIONSCHECK-FEHLT (Backlog).
    log_berechnung(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "embedding",
        inhalt  = {
            "prompt_length":  len(reiz_text(state)),
            "embedding_dim":  len(embedding) if embedding else 0,
        },
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # ─────────────────────────────────────────
    # 3a. Ziele + Gravitation (Drive)
    #     Steht VOR der Memory-Suche, weil die Wahrnehmungs-Gravitation
    #     (§8.5) den Suchschluessel aus den aktivierten Zielen bildet. Die
    #     Aktivierung selbst rechnet gegen das ROHE Anfrage-Embedding —
    #     mit dem verschobenen waere sie ihre eigene Eingabe.
    # ─────────────────────────────────────────
    aktiviert, gravitationsterm = _compute_ziele_und_gravitation(
        embedding, postgres_url, user_id, character_id,
    )
    aktivierte_ziele: list[dict] = _ziele_als_dicts(aktiviert)
    state["aktivierte_ziele"] = aktivierte_ziele
    state["gravitationsterm"] = gravitationsterm

    if aktivierte_ziele:
        logger.info(
            f"Enricher: {len(aktivierte_ziele)} Ziele aktiviert, "
            f"Gravitationsterm={gravitationsterm:.3f}"
        )

    # Lokale Initialisierung, damit der Switch-Inhalt unten den KZG-Count
    # unabhaengig vom Pfad sicher referenzieren kann. Die Spreading-Erinnerungen
    # zaehlt der Switch aus state["lzg_resonanz"] (kein memory_entries-Akkumulator).
    kzg_entries: list[ContextEntry] = []

    # None heisst: In diesem Turn lief GAR KEINE Gedaechtnissuche — weder KZG
    # noch LZG —, es gab also keinen Suchschluessel zu verschieben. Der
    # Protokoll-Eintrag unten haelt genau diesen Fall fest; ohne ihn saehe ein
    # Turn ohne Gedaechtnis aus wie ein Turn ohne Verschiebung.
    #
    # Bis zum 04.08.2026 hiess None enger "keine LZG-Suche", weil allein das
    # LZG den verschobenen Schluessel bekam. Die Bedeutung ist mit dem Umfang
    # mitgewandert — eine Protokoll-Zusicherung, die stehen bleibt, waehrend
    # ihr Gegenstand sich aendert, ist still falsch.
    verschiebung: Verschiebung | None = None

    if kzg_keys or has_lzg or has_wissen:
        logger.info(
            f"Enricher: {len(kzg_keys)} KZG, LZG={'ja' if has_lzg else 'nein'}, "
            f"Bibliothek={'ja' if has_wissen else 'nein'} — suche Kontext..."
        )

        # §8.5: Wahrnehmungs-Gravitation. Der Suchschluessel ist nicht mehr
        # allein die Frage, sondern die Frage plus Novas Motivation.
        #
        # **Einmal je Turn, fuer BEIDE Gedaechtnisschichten.** Bis zum
        # 04.08.2026 bekam ihn nur das LZG; fuer diese Grenze gab es keine
        # Begruendung — weder im Konzept noch im einfuehrenden Commit, der
        # sie nur als Umfang nennt. KZG und LZG sind dieselbe Art Speicher
        # mit verschiedenen Zeithorizonten, und Nova hoert nicht mit zwei
        # Ohren.
        #
        # Was ausdruecklich NICHT mitzieht: die Ziel-Aktivierung weiter oben.
        # Sie rechnet gegen das rohe Embedding, weil sie mit dem verschobenen
        # ihre eigene Eingabe waere.
        #
        # Der Cluster wird jetzt auch fuer einen Turn ohne LZG gelesen — ein
        # zusaetzlicher Redis-Zugriff, der den Preis dafuer traegt, dass beide
        # Suchen denselben Schluessel benutzen.
        cluster: str = _vorturn_cluster_lesen(redis_client, user_id, character_id)

        # Query Rewriting: Der Schluessel traegt den Gegenstand des Gespraechs,
        # auch wenn dieser Turn ihn nur als Rueckbezug nennt. Das rohe
        # Embedding von oben bleibt unberuehrt — es speist die Ziele, und die
        # sind ein anderer Gegenstand als die Suche.
        suchtext, suchtext_herkunft = _suchtext_bauen(state, raw_turns)
        such_embedding: list[float] = (
            _create_prompt_embedding(state, suchtext)
            if suchtext_herkunft == "rewrite"
            else embedding
        )
        state["suchtext"]           = suchtext
        state["suchtext_herkunft"]  = suchtext_herkunft
        log_berechnung(
            turn_id = turn_id_log,
            node    = "enricher",
            quelle  = "query_rewrite",
            inhalt  = {
                "herkunft":     suchtext_herkunft,
                "roh":          reiz_text(state)[:200],
                "suchtext":     suchtext[:200],
                "roh_laenge":   len(reiz_text(state)),
                "turns_gesehen": len(raw_turns),
            },
            span_id = span_id,
            user_id      = user_id,
            character_id = character_id,
        )

        verschiebung = wahrnehmung_verschieben(
            anfrage_embedding = such_embedding,
            aktivierte_ziele  = aktiviert,
            cluster           = cluster,
            ist_anweisung     = INTENTION_ANWEISUNG in letzte_intentionen,
        )
        such_vektor: list[float] = verschiebung.vektor

        # In den State, damit die Plugin-Schicht (Abschnitt 3b) mit
        # DEMSELBEN Schluessel sucht wie KZG und LZG.
        #
        # Das weitet den Gegenstand von §8.5.4 aus: Dort steht, der
        # verschobene Vektor sei „nicht eigenstaendig nutzbar — er existiert
        # ausschliesslich als Such-Schluessel fuer die unmittelbar folgende
        # pgvector-Abfrage". Das war richtig, solange es eine Abfrage gab.
        # Die Bibliothek ist eine zweite, und sie liegt in einem Plugin.
        # Entweder rechnet dieses Plugin sich denselben Vektor noch einmal,
        # oder der Enricher reicht ihn weiter — das Zweite ist billiger und
        # macht ausserdem sichtbar, dass alle Schichten denselben Schluessel
        # benutzen. Wer hier liest, liest keinen Zwischenstand: Der Wert ist
        # gesetzt, sobald ueberhaupt gesucht wird, und sonst nicht vorhanden.
        state["such_vektor"] = such_vektor

        if kzg_keys:
            kzg_entries = kzg_entries_retrieve(
                redis_client, user_id, character_id, such_vektor,
            )
            if kzg_entries:
                entries.extend(kzg_entries)
                logger.info(f"Enricher: KZG lieferte {len(kzg_entries)} Eintraege")

        if has_lzg:
            # B2 (§8.1-8.4): gerichteter Spreading-Lesepfad statt flachem LZG-Read.
            # Cluster aus dem Redis-Vorturn (GV-Node laeuft nach dem Enricher, §8.2.1).

            # Novas dominante Emotion des aktuellen Turns: [0] ist die staerkste
            # (Verlauf in allen ei_calc-Pfaden absteigend nach Gewicht sortiert).
            # Empty-Guard: leer/fehlend -> "" (Neutral-Faktor 1.0 in _sektor_faktor).
            nova_verlauf: list = state.get("nova_emotions_verlauf") or []
            nova_emotion: str = nova_verlauf[0]["emotion"] if nova_verlauf else ""

            embedding_str: str = embedding_zu_pgvector_str(such_vektor)
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

    # ── Pipeline-Log: Wahrnehmungs-Gravitation (Anker 4c) ──
    # Genau ein Eintrag je Durchlauf, auch wenn nichts verschoben wurde.
    log_berechnung(
        turn_id = turn_id_log,
        node    = "enricher",
        quelle  = "wahrnehmungs_gravitation",
        inhalt  = _verschiebungs_protokoll(
            verschiebung, len(embedding) if embedding else 0,
        ),
        span_id = span_id,
        user_id      = user_id,
        character_id = character_id,
    )

    # ─────────────────────────────────────────
    # 3b. Plugin-Hooks: enrich_entries() aller Manager
    # ─────────────────────────────────────────
    # Verschoben am 04.08.2026 von vor die Suche hierher. Der Grund ist eine
    # Reihenfolge, keine Vorliebe: Vorher lief die Plugin-Schicht, bevor das
    # Prompt-Embedding ueberhaupt existierte, und ein Plugin mit
    # Embedding-Suche haette sich ein zweites rechnen lassen muessen.
    #
    # Geprueft, was die Verschiebung anfasst: Von fuenf Managern liefern nur
    # Timeline und Notizen; beide lesen ausschliesslich Felder, die vor dem
    # Enricher feststehen (user_id, external, needs_timeline, timeline_query,
    # management_target), und **keiner schreibt in den State**. Der Formatter
    # gruppiert nach `quelle`, nicht nach Listenposition — die Plugin-Gruppe
    # steht als Block, gleich wann sie angehaengt wurde.
    #
    # Der eine gefundene Effekt, benannt statt weggeredet: Der Reducer
    # entdoppelt bei identischem Inhalt nach hoechstem Gewicht und bei
    # Gleichstand nach Eingangsreihenfolge. Traegt ein Plugin-Eintrag
    # denselben Text UND dasselbe Gewicht wie ein KZG-Treffer, ueberlebt
    # seit der Verschiebung der andere von beiden — und weil `quelle` das
    # Format steuert, erschiene derselbe Satz unter einem anderen Etikett.
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
            logger.exception(f"{type(fehler).__name__}: Enricher: Plugin '{name}' Fehler")

    # ─────────────────────────────────────────
    # 3c. Der Dateien-Index — die Quelle, die kein Dienst ist
    # ─────────────────────────────────────────
    # Sie steht hier und nicht in der Plugin-Schleife darueber, und der Grund
    # ist kein Ordnungsgeschmack: Ein Plugin liefert `ContextEntry` in den
    # `memory_entries`-Pool, und alles in diesem Pool wird vom Formatter unter
    # [GEDAECHTNIS] gerendert. **Dateiinhalt darf dort nicht hinein**
    # (novaberg-agent-dateien_k.md §1a.2) — was in den Dateien steht, ist
    # nicht ihr Gedaechtnis, und die Beschriftung ist die Aussage.
    #
    # Der Praezedenzfall steht offen im Bestand: Nova hat die Biografie eines
    # Menschen als ihre eigene uebernommen. Ein Dokument ist derselbe Fall
    # eine Stufe weiter — eine fremde Erinnerung gehoert wenigstens jemandem.
    #
    # Denselben Schluessel wie KZG, LZG und die Bibliothek: `such_vektor`
    # steht seit der Suche oben im State. Ein eigenes Embedding waere hier
    # der Fehler (§3.0).
    try:
        # Der Wortlaut des Turns geht mit, weil der scharfe Kanal ihn braucht
        # und kein Modell dafuer laeuft: Postgres zerlegt ihn mit
        # `to_tsvector` in Lexeme ohne Stoppwoerter. `reiz_text` liefert die
        # Aeusserung, gleich von wem sie stammt — auch ein eigener Gedanke
        # darf in Unterlagen nachsehen.
        fund: Aufzeichnungsfund = aufzeichnungen_suchen(
            state.get("such_vektor") or [], user_id, character_id,
            frage=reiz_text(state),
        )
        state["aufzeichnungen"] = fund.treffer
    except Exception as fehler:
        # Der Enricher faengt ab, damit ein Ausfall dieser Quelle den Turn
        # nicht mitnimmt — aber er sagt, welche Quelle es war.
        logger.exception(
            f"{type(fehler).__name__}: Enricher: Dateien-Index Fehler — "
            f"kein [AUFZEICHNUNGEN]-Block in diesem Turn"
        )
        state["aufzeichnungen"] = []

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
    # 5. Emotionale Gravitation (EI Phase 3)
    #     Rechnet gegen das ROHE Anfrage-Embedding: Sie sucht emotional
    #     geladene Erinnerungen zum Thema des Turns, nicht zum Thema von
    #     Novas Zielen.
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
            "aufzeichnungen_count":              len(state.get("aufzeichnungen", [])),
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
