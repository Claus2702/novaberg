"""
Kurzzeitgedächtnis — Redis Stack mit Vektorsuche.
TTL-basiert, Promotion ins LZG bei Schwellwert.

Key-Schema: kzg:{user_id}:{character_id}:{entry_id}
Das Paar (user_id, character_id) definiert das gemeinsame Gespraech.
Feld `beobachter` unterscheidet, ob der Eintrag aus Sicht des Users (HumanGraph)
oder des Charakters (CharacterGraph) entstanden ist.
"""

import json
import logging
import math
import time

from typing import Optional

import numpy as np
import redis

from config                                import (
    ASSISTANT_USER_ID,
    KZG_SALIENZ_MINIMUM,
    KZG_SALIENZ_MID,
    KZG_SALIENZ_HIGH,
    KZG_SALIENZ_CAP,
    KZG_SALIENZ_DAEMPFUNG_EXP,
    KZG_SALIENZ_BOOST,
    KZG_TTL_LOW_SEKUNDEN,
    KZG_TTL_MID_SEKUNDEN,
    KZG_TTL_HIGH_SEKUNDEN,
    PIXIE_AKTIV,
    MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION,
)
from graph.context_entry                   import ContextEntry
from memory.pipeline_log                   import log_db_write
from services.shadow_agent                 import shadow_queue_push
from services.shadow_agent.utils           import promotion_queue_push

from redis.commands.search.field           import TextField, NumericField, VectorField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query           import Query

logger = logging.getLogger("ki_server.memory.kzg")

# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
EMBEDDING_DIM:        int   = 768
# Kalibriert auf nomic-embed-text-v2-moe (Chat 107).
# Grundrauschen 0.16, Median 0.26, p99 0.57 — gemessen an 302 lzg_knoten.
# Vorher 0.85 im casing-blinden Raum (Grundrauschen 0.74) — funktionslos.
# Einziger Nutzer kzg_similar_find hat derzeit keinen Live-Aufrufer; bei
# Reaktivierung soll er nicht mit einem toten Wert starten.
SIMILARITY_THRESHOLD: float = 0.75
# DEAD CODE (Chat 91, Pre-P4-Fix): Ersetzt durch KZG_SALIENZ_HIGH (= 0.7)
# in config.py. Wird mit dem Rest der alten Promotion in P9 entfernt.
# Nicht löschen vor P9 — könnte noch in nicht-aktivem Legacy-Code
# referenziert sein.
PROMOTION_THRESHOLD: float = 0.8  # Legacy, nicht mehr verwendet
KZG_INDEX_NAME:       str   = "idx:kzg"
KZG_PREFIX:           str   = "kzg:"


# ─────────────────────────────────────────────
# Key-Helfer
# ─────────────────────────────────────────────
def _kzg_key(user_id: str, character_id: str, entry_id: str) -> str:
    """Baut den Redis-Key fuer einen KZG-Eintrag."""
    return f"kzg:{user_id}:{character_id}:{entry_id}"


def _kzg_prefix(user_id: str, character_id: str) -> str:
    """Prefix fuer alle KZG-Eintraege eines Gespraechspaares."""
    return f"kzg:{user_id}:{character_id}:*"


# ─────────────────────────────────────────────
# Intention → Shadow-Aufgabe Mapping
# ─────────────────────────────────────────────
_INTENTION_AUFGABE_MAP: dict[str, str] = {
    # Kein Auftrag: `nachfragen` setzt einen von der EI erkannten **Druck**
    # voraus, und diese Intention deckt jede Gefuehlsaeusserung ab, auch
    # Freude und Begeisterung. Die Aufgabe blieb bis 05.08.2026 auf
    # "nachfragen" und erzeugte ueberwiegend Auftraege ohne Druck.
    # Den Druck liefert der Emotionsvektor-Pfad des Routers.
    "emotionaler_ausdruck": "",
    "information_teilen":   "vertiefen",
    "recherche_vertiefen":  "recherche",
    "reflexion":            "recherche",
    "gemeinsam_eruieren":   "recherche",
    "hilferuf":             "nachfragen",
    "information_erfragen": "recherche",
    "feedback_geben":       "",
    "feedback_erfragen":    "",
    "smalltalk":            "",
    "bestätigung":          "",
    "abschluss":            "",
    "anweisung":            "",
    "planung":              "",
    "humor":                "",
    "widerspruch":          "",
}


def _aufgabe_aus_intention(intentionen: list) -> str:
    """Leitet die Shadow-Aufgabe aus der primären Intention ab."""
    if not intentionen:
        return "recherche"

    aufgabe: str = _INTENTION_AUFGABE_MAP.get(intentionen[0], "recherche")

    return aufgabe if aufgabe else ""


# ─────────────────────────────────────────────
# Index-Erstellung (einmalig beim Start)
# ─────────────────────────────────────────────
def kzg_index_create(redis_client: redis.Redis) -> None:
    """Erstellt den RediSearch-Index für KZG-Einträge falls nicht vorhanden."""
    try:
        redis_client.ft(KZG_INDEX_NAME).info()
        logger.info("KZG-Index existiert bereits.")
        return
    except Exception:
        pass

    schema = (
        TagField("user_id"),
        TagField("character_id"),
        TagField("beobachter"),
        TextField("themen"),
        TextField("inhalt"),
        NumericField("salienz"),
        NumericField("haeufigkeit"),
        TextField("gedaechtnistyp"),
        TextField("dimension"),
        NumericField("erstellt_am"),
        NumericField("arousal"),
        TextField("emotions_vektor"),
        TextField("sprach_stil"),
        TextField("tone"),
        TagField("emotion"),
        TagField("modus"),
        TagField("entitaet_ids", separator=","),
        NumericField("timeline_id"),
        VectorField(
            "embedding",
            "FLAT",
            {
                "TYPE":            "FLOAT32",
                "DIM":             EMBEDDING_DIM,
                "DISTANCE_METRIC": "COSINE",
            },
        ),
    )

    definition = IndexDefinition(
        prefix=[KZG_PREFIX],
        index_type=IndexType.HASH,
    )

    redis_client.ft(KZG_INDEX_NAME).create_index(
        fields=schema,
        definition=definition,
    )

    logger.info("KZG-Index erstellt.")


# ─────────────────────────────────────────────
# Ähnlichen Eintrag suchen
# ─────────────────────────────────────────────
def kzg_similar_find(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    embedding:    list[float],
    top_k:        int = 1
) -> Optional[dict]:
    """Sucht den ähnlichsten KZG-Eintrag per Vektorsuche (paar-skopiert)."""
    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()

    query = (
        Query(
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN {top_k} @embedding $vec AS score]"
        )
        .sort_by("score")
        .return_fields("themen", "inhalt", "salienz", "haeufigkeit",
                       "gedaechtnistyp", "dimension", "score")
        .dialect(2)
    )

    try:
        results = redis_client.ft(KZG_INDEX_NAME).search(
            query,
            query_params={"vec": embedding_bytes},
        )

        if results.total == 0:
            return None

        treffer    = results.docs[0]
        score:      float = float(treffer.score)
        similarity: float = 1.0 - (score / 2.0)

        if similarity < SIMILARITY_THRESHOLD:
            logger.info(f"KZG: Kein ähnlicher Eintrag (beste Similarity: {similarity:.3f})")
            return None

        logger.info(f"KZG: Ähnlicher Eintrag gefunden (Similarity: {similarity:.3f})")

        return {
            "key":            treffer.id,
            "themen":         treffer.themen,
            "inhalt":         treffer.inhalt,
            "salienz":        float(treffer.salienz),
            "haeufigkeit":    int(float(treffer.haeufigkeit)),
            "gedaechtnistyp": treffer.gedaechtnistyp,
            "dimension":      treffer.dimension,
            "similarity":     similarity,
        }

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: KZG-Suche fehlgeschlagen")
        return None


# ─────────────────────────────────────────────
# Salienz als abgeleiteter Wert
# ─────────────────────────────────────────────
def salienz_berechnen(salienz_eingang: float, haeufigkeit: int) -> float:
    """Berechnet die Salienz eines KZG-Eintrags aus seinen zwei Eingaben.

    Die Salienz ist das Tor zwischen Kurz- und Langzeitgedaechtnis und bildet
    zwei Wege ab: den Einpraegsamen (das Modell bewertet beim Anlegen hoch) und
    den Angesammelten (mittelmaessig Wichtiges kommt wieder). Beide enden am
    selben Tor.

        salienz_roh = salienz_eingang + verstaerkungen x KZG_SALIENZ_BOOST
        anteil      = min(salienz_roh / CAP, 1.0)
        salienz     = CAP x sin(anteil x pi/2) ** EXP

    `verstaerkungen` ist `haeufigkeit - 1`: Ein frisch angelegter Eintrag traegt
    haeufigkeit 1 und null Verstaerkungen. Der Boost greift am Anker VOR der
    Kurve — ein Zuwachs auf den gekruemmten Wert bedeutete am unteren Ende der
    Skala etwas anderes als am oberen (novaberg-kzg-salienz_k.md §3).

    Reine Funktion: Keine Eingabe wurde je aus dem Ergebnis berechnet, nichts
    wird zurueckgeschrieben, zweimaliges Rechnen liefert bitgleiche Werte
    (novaberg-convention-abgeleitete-werte.md, Regeln 2 bis 4).

    Vorbedingung: salienz_eingang in [0.0, 1.0], haeufigkeit >= 1.
    Nachbedingung: Rueckgabe in [0.0, KZG_SALIENZ_CAP].
    Fehlerfaelle: Werte ausserhalb ihres Bereichs werden laut protokolliert und
    geklemmt — ein stiller Abbruch mitten in der Verdichtung waere der
    schlimmere Fehler, ein stilles Weiterrechnen der schlimmste.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 0.0 <= salienz_eingang <= 1.0:
        logger.error(
            f"salienz_berechnen: salienz_eingang={salienz_eingang} liegt ausserhalb "
            f"[0.0, 1.0] — geklemmt. Das Feld traegt die Modellbewertung und kann "
            f"diesen Bereich nicht verlassen; der Schreiber ist defekt"
        )
        salienz_eingang = max(0.0, min(1.0, salienz_eingang))

    if haeufigkeit < 1:
        logger.error(
            f"salienz_berechnen: haeufigkeit={haeufigkeit} — ein bestehender Eintrag "
            f"wurde mindestens einmal angelegt; auf 1 gesetzt"
        )
        haeufigkeit = 1

    # ── Verarbeitung ────────────────────────────
    verstaerkungen: int   = haeufigkeit - 1
    salienz_roh:    float = salienz_eingang + verstaerkungen * KZG_SALIENZ_BOOST
    anteil:         float = min(salienz_roh / KZG_SALIENZ_CAP, 1.0)
    salienz:        float = KZG_SALIENZ_CAP * (
        math.sin(anteil * math.pi / 2) ** KZG_SALIENZ_DAEMPFUNG_EXP
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 <= salienz <= KZG_SALIENZ_CAP:
        logger.error(
            f"salienz_berechnen: Ergebnis {salienz} ausserhalb [0.0, {KZG_SALIENZ_CAP}] "
            f"(eingang={salienz_eingang}, haeufigkeit={haeufigkeit}) — geklemmt"
        )
        salienz = max(0.0, min(KZG_SALIENZ_CAP, salienz))

    return salienz


# ─────────────────────────────────────────────
# Eintrag speichern oder verstärken
# ─────────────────────────────────────────────
def kzg_store(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    beobachter:   str,
    salienz_obj:  dict,
    embedding:    list[float],
    entitaet_ids: list[int] | None = None,
    timeline_id:  int | None       = None,
    turn_id:      str              = "",
) -> str:
    """
    Speichert einen neuen KZG-Eintrag und verstärkt thematisch verwandte
    Einträge in der Paar-Partition (kein Merge, nur Salienz/Häufigkeit/TTL).
    Gibt den Status zurück: 'neu' oder 'ignoriert'.

    Magnet-Felder (Synapsen P3, optional):
      entitaet_ids: kommagetrennter String im RediSearch-TagField. Leere
                    Liste -> leerer String "". Default-Verhalten fuer Legacy-
                    Aufrufer (Recherche, Shadow): keine Magnete -> leerer
                    String, kein Index-Bruch.
      timeline_id:  Integer im RediSearch-NumericField. None -> Feld wird
                    aus dem mapping= ausgelassen.
      turn_id:      Pipeline-Log-Korrelation; bei Legacy-Aufrufern leer.
    """
    # Der Wert aus dem Salienz-Node ist die Bewertung des Modells — der
    # unveraenderliche Eingang. Die Salienz, gegen die alle Tore pruefen, ist
    # daraus abgeleitet und wird ab hier durchgaengig verwendet.
    salienz_eingang: float = salienz_obj.get("salienz", 0.0)
    salienz:         float = salienz_berechnen(salienz_eingang, 1)

    if salienz < KZG_SALIENZ_MINIMUM:
        logger.info(
            f"KZG: Salienz {salienz:.4f} (Eingang {salienz_eingang:.2f}) unter "
            f"Schwellwert {KZG_SALIENZ_MINIMUM} — ignoriert"
        )
        return "ignoriert"

    # Meta-Daten aus Salienz-Analyse (Intentions-Schicht)
    intentionen: list = salienz_obj.get("intentionen", [])
    emotion:     str  = salienz_obj.get("emotion", "neutral")
    modus:       str  = salienz_obj.get("modus", "")

    # Thematisch verwandte Einträge verstärken (kein Merge, nur Boost)
    neue_themen: set[str] = set(
        t.strip().lower() for t in salienz_obj.get("themen", []) if t.strip()
    )

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()
    timestamp:       float = time.time()

    key:        str = _kzg_key(user_id, character_id, str(int(timestamp * 1000)))
    themen_str: str = ", ".join(salienz_obj.get("themen", []))
    dimension:  str = salienz_obj.get("dimension", "kontext")

    # **Zwei Groessen, zwei Namen — derselbe Rohwert, zwei Bedeutungen.**
    # Der KZG-Hash fuehrt `arousal` als Pflichtfeld und nimmt deshalb den
    # geklemmten Wert mit Ausfallwert 0.5; das ist Bestand und bleibt.
    # Die **Queue** darf ihn nicht bekommen: Dort heisst `None`
    # unbekannt, und eine 0.5 waere ein Messwert, den nie jemand gemessen
    # hat — sie hoebe beim Einwurf Novas Zustand auf eine erfundene Zahl
    # (Bauteil B, `novaberg-eigenzeit_k.md` §2.3).
    #
    # Ein einziger Name fuer beides waere die Falle gewesen: Die zweite
    # Zuweisung ueberschreibt die erste **vor** dem Queue-Aufruf, still
    # und ohne rote Zeile.
    arousal:          float = max(0.0, min(1.0, float(salienz_obj.get("arousal", 0.5))))
    arousal_gemessen: float | None = salienz_obj.get("arousal")
    emotions_vektor:  str   = salienz_obj.get("emotions_vektor", "")

    entitaet_ids_str: str = ",".join(str(eid) for eid in (entitaet_ids or []))

    mapping: dict = {
        "user_id":          user_id,
        "character_id":     character_id,
        "beobachter":       beobachter,
        "themen":           themen_str,
        "inhalt":           salienz_obj.get("zusammenfassung", salienz_obj.get("begruendung", "")),
        "salienz":          str(salienz),
        "salienz_eingang":  str(salienz_eingang),
        # Herkunft des Eingangswerts. Ein neu angelegter Eintrag traegt die
        # echte Modellbewertung — "gemessen". Der Bestand aus der Zeit vor dem
        # Skalenumbau traegt teils "geschaetzt" (Migration Chat 113): Ein
        # Default darf nie aussehen wie ein echter Wert
        # (novaberg-kzg-salienz_k.md §10).
        "salienz_eingang_herkunft": "gemessen",
        "haeufigkeit":      str(1),
        "gedaechtnistyp":   salienz_obj.get("gedaechtnistyp", "kurz"),
        "dimension":        dimension,
        "intentionen":      json.dumps(intentionen),
        "emotion":          emotion,
        "modus":            modus,
        "arousal":          str(arousal),
        "emotions_vektor":    emotions_vektor,
        "sprach_stil":        salienz_obj.get("sprach_stil", "neutral"),
        "beziehungs_dynamik": salienz_obj.get("beziehungs_dynamik", "neutral"),
        "tone":               salienz_obj.get("tone", "sachlich"),
        "erstellt_am":        str(timestamp),
        "entitaet_ids":       entitaet_ids_str,
        "embedding":        embedding_bytes,
    }
    if timeline_id is not None:
        mapping["timeline_id"] = str(timeline_id)

    redis_client.hset(key, mapping=mapping)

    if salienz >= KZG_SALIENZ_HIGH:
        ttl: int = KZG_TTL_HIGH_SEKUNDEN
    elif salienz >= KZG_SALIENZ_MID:
        ttl: int = KZG_TTL_MID_SEKUNDEN
    else:
        ttl: int = KZG_TTL_LOW_SEKUNDEN
    redis_client.expire(key, ttl)

    # Pipeline-Log: schreibender DB-Zugriff (Synapsen §10.2).
    log_db_write(
        turn_id = turn_id or "kzg-store-unbekannt",
        node    = "kzg_speicher",
        quelle  = user_id,
        inhalt  = {
            "tabelle":      "kzg",
            "operation":    "insert",
            "kzg_key":      key,
            "entitaet_ids": entitaet_ids or [],
            "timeline_id":  timeline_id,
            "themen":       themen_str,
            "dimension":    dimension,
            "salienz":      salienz,
            "ttl":          ttl,
            "aufrufer":     "kzg_store",
        },
        user_id      = user_id,
        character_id = character_id,
    )

    if salienz >= KZG_SALIENZ_HIGH:
        if PIXIE_AKTIV:
            # Dublettenpruefung im Helfer; das PIXIE_AKTIV-Gate steht hier
            # weiterhin, weil der folgende Block daran haengt.
            promotion_queue_push(
                redis_client, user_id, key, salienz, themen_str, dimension,
            )

            aufgabe: str = _aufgabe_aus_intention(intentionen)

            if aufgabe and user_id != ASSISTANT_USER_ID:
                shadow_queue_push(
                    redis_client = redis_client,
                    user_id      = user_id,
                    aufgabe      = aufgabe,
                    thema        = themen_str,
                    # Die Ausloese-Salienz gehoert an den Auftrag. Bis zum
                    # 15.08.2026 fehlte sie hier, und der Vorgabewert 0.0 der
                    # Signatur machte daraus einen gueltig aussehenden Wert
                    # unterhalb jeder Schwelle — 233 von 1036 Auftraegen
                    # (`KANDIDATEN-PRIORITAET-STILLE-NULL`).
                    prioritaet   = salienz,
                    kontext      = salienz_obj.get("zusammenfassung", ""),
                    intentionen  = intentionen,
                    emotion      = emotion,
                    modus        = modus,
                    arousal      = arousal_gemessen,
                )
        else:
            logger.debug("kzg: Promotion-Queue-Push uebersprungen (PIXIE_AKTIV=False)")

    logger.info(
        f"KZG: Neuer Eintrag — salienz={salienz:.2f}, themen={themen_str}, "
        f"arousal={arousal:.2f}, vektor={emotions_vektor}, TTL={ttl}s"
    )

    # Thematische Verstärkung: verwandte Einträge im KZG boosten
    if neue_themen:
        prefix: str = f"kzg:{user_id}:{character_id}:"
        for other_key in redis_client.keys(f"{prefix}*"):
            if isinstance(other_key, bytes):
                other_key = other_key.decode("utf-8")
            if other_key == key:
                continue
            try:
                other_themen_raw: str | None = redis_client.hget(other_key, "themen")
                if not other_themen_raw:
                    continue
                other_themen: set[str] = set(
                    t.strip().lower() for t in other_themen_raw.split(",") if t.strip()
                )
                if not neue_themen & other_themen:
                    continue

                # Der Eingangswert ist unveraenderlich; verstaerkt wird der
                # Zaehler. Die Salienz entsteht daraus neu — sie wird nicht
                # fortgeschrieben (novaberg-convention-abgeleitete-werte.md).
                eingang_roh: str | None = redis_client.hget(other_key, "salienz_eingang")
                if eingang_roh is None:
                    logger.error(
                        f"KZG-Verstaerkung: {other_key} traegt kein salienz_eingang — "
                        f"Eintrag stammt aus der Zeit vor dem Skalenumbau und ist nicht "
                        f"nachrechenbar; uebersprungen"
                    )
                    continue

                alte_sal: float = float(redis_client.hget(other_key, "salienz") or "0.0")
                alte_hfk: int   = int(float(redis_client.hget(other_key, "haeufigkeit") or "1"))
                eingang:  float = float(eingang_roh)
                neue_hfk: int   = alte_hfk + 1
                neue_sal: float = salienz_berechnen(eingang, neue_hfk)

                redis_client.hset(other_key, mapping={
                    "salienz":     str(neue_sal),
                    "haeufigkeit": str(neue_hfk),
                })

                if neue_sal >= KZG_SALIENZ_HIGH:
                    neuer_ttl: int = KZG_TTL_HIGH_SEKUNDEN
                elif neue_sal >= KZG_SALIENZ_MID:
                    neuer_ttl: int = KZG_TTL_MID_SEKUNDEN
                else:
                    neuer_ttl: int = KZG_TTL_LOW_SEKUNDEN

                verbleibend: int = redis_client.ttl(other_key)
                redis_client.expire(other_key, max(verbleibend if verbleibend > 0 else 0, neuer_ttl))

                logger.info(
                    f"KZG: Thematische Verstärkung {other_key} — "
                    f"salienz {alte_sal:.2f} → {neue_sal:.2f}, "
                    f"häufigkeit {alte_hfk} → {neue_hfk}"
                )
            except Exception as ex:
                logger.warning(f"KZG: Verstärkungsfehler bei {other_key}: {ex}")

    if not PIXIE_AKTIV:
        logger.debug("kzg: hash_dirty-Setzer uebersprungen (PIXIE_AKTIV=False)")
    elif MESSREIHE_OHNE_AUTOMATISCHE_DESTILLATION:
        # Im Messlauf stoesst der Bogenlaeufer an definierten Punkten an.
        logger.debug(
            "kzg: hash_dirty-Setzer uebersprungen (Messreihe steuert selbst)"
        )
    else:
        redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")
    return "neu"


# ─────────────────────────────────────────────
# Kontext abrufen für Enricher
# ─────────────────────────────────────────────
def kzg_entries_retrieve(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    embedding:    list[float],
    top_k:        int = 10
) -> list[ContextEntry]:
    """Holt die relevantesten KZG-Eintraege eines Paares als ContextEntry-Liste.

    Liefert strukturierte Daten ohne Format-Drumherum. Der Reducer
    dedupliziert auf dieser Ebene; der Formatter baut daraus den
    finalen memory_context-String fuer den Responder.

    Datenbeschaffung: KNN-Suche im RediSearch-Index (paar-skopiert auf
    user_id/character_id), Similarity-Schwelle 0.5, top_k Treffer.
    Filter, Schwellwerte und Index bleiben identisch zur Vorgaengerfunktion.

    Mapping pro KZG-Hash-Treffer auf ContextEntry:
      quelle  = "kzg" (Konstante)
      subtyp  = Hash-Feld `dimension` (Salienz-Dim 5: interessen,
                beziehungen, ...). Leer-String wenn nicht gesetzt.
      inhalt  = Hash-Feld `inhalt` (destillierter Kern)
      gewicht = Hash-Feld `salienz` als float
      meta    = {
          "themen":         Hash-Feld `themen` (String wie gespeichert),
          "beobachter":     Hash-Feld `beobachter`,
          "erstellt_am":    Hash-Feld `erstellt_am` (Unix-Timestamp, float),
          "arousal":        Hash-Feld `arousal` (float, fuer spaetere
                            Format-Erweiterungen),
          "emotion":        Hash-Feld `emotion`,
          "modus":          Hash-Feld `modus`,
          "gedaechtnistyp": Hash-Feld `gedaechtnistyp`,
          "emotions_vektor": Hash-Feld `emotions_vektor`,
      }

    Args:
        redis_client: Redis-Verbindung mit RediSearch-Modul.
        user_id:      Subjekt der Paar-Partition.
        character_id: Gegenueber der Paar-Partition.
        embedding:    Query-Vektor (768-dim) des aktuellen Prompts.
        top_k:        Maximale Treffer-Anzahl vor Similarity-Filter.

    Returns:
        Liste von ContextEntry-Dicts. Leer bei keinen Treffern oder Fehler.
    """
    logger.info(f"KZG-Entries-Retrieve: Paar={user_id}:{character_id}, Limit={top_k}")

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()

    query = (
        Query(
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN {top_k} @embedding $vec AS score]"
        )
        .sort_by("score")
        .return_fields(
            "themen", "inhalt", "salienz", "score",
            "dimension", "beobachter", "erstellt_am",
            "arousal", "emotion", "modus", "gedaechtnistyp",
            "emotions_vektor",
        )
        .dialect(2)
    )

    entries: list[ContextEntry] = []

    try:
        results = redis_client.ft(KZG_INDEX_NAME).search(
            query,
            query_params={"vec": embedding_bytes},
        )

        if results.total == 0:
            logger.info("KZG-Entries-Retrieve: 0 Eintraege geliefert")
            return entries

        for doc in results.docs:
            similarity: float = 1.0 - (float(doc.score) / 2.0)
            # Kalibriert auf nomic-embed-text-v2-moe (Chat 107). Vorher 0.5
            # im casing-blinden Raum (Grundrauschen 0.74) — passierte fast
            # alles; im neuen Raum (Grundrauschen 0.16) haette 0.5 fast
            # nichts mehr passieren lassen.
            # ⚠ Wachposten: Prompt↔Eintrag-Wert, nicht gemessen —
            # begruendeter Startwert, kein Messergebnis.
            if similarity < 0.40:
                continue

            subtyp:  str   = getattr(doc, "dimension", "") or ""
            inhalt:  str   = getattr(doc, "inhalt", "") or ""

            # Plausibilitaetspruefung am Lesepfad (Chat 107): Ein Eintrag ohne
            # Text darf nicht in den Kontext — egal woher er kommt und wie gut
            # sein Vektor matcht. Der Formatter wuerde sonst "[KZG] ...: " mit
            # baumelndem Doppelpunkt rendern. Laut verwerfen, damit sichtbar
            # wird, wenn irgendeine Quelle wieder textlose Eintraege schreibt.
            if not inhalt.strip():
                logger.warning(
                    "KZG-Entries-Retrieve: Eintrag ohne inhalt verworfen — key=%s, "
                    "themen='%s', beobachter=%s, similarity=%.3f",
                    doc.id,
                    getattr(doc, "themen", "") or "",
                    getattr(doc, "beobachter", "") or "",
                    similarity,
                )
                continue

            gewicht: float = float(getattr(doc, "salienz", 0.0) or 0.0)

            erstellt_am_raw = getattr(doc, "erstellt_am", "") or ""
            try:
                erstellt_am: float = float(erstellt_am_raw) if erstellt_am_raw else 0.0
            except (TypeError, ValueError):
                erstellt_am = 0.0

            try:
                arousal: float = float(getattr(doc, "arousal", 0.0) or 0.0)
            except (TypeError, ValueError):
                arousal = 0.0

            entry: ContextEntry = {
                "quelle":  "kzg",
                "subtyp":  subtyp,
                "inhalt":  inhalt,
                "gewicht": gewicht,
                "meta": {
                    "themen":          getattr(doc, "themen", "") or "",
                    "beobachter":      getattr(doc, "beobachter", "") or "",
                    "erstellt_am":     erstellt_am,
                    "arousal":         arousal,
                    "emotion":         getattr(doc, "emotion", "") or "",
                    "modus":           getattr(doc, "modus", "") or "",
                    "gedaechtnistyp":  getattr(doc, "gedaechtnistyp", "") or "",
                    "emotions_vektor": getattr(doc, "emotions_vektor", "") or "",
                },
            }
            entries.append(entry)

            logger.debug(
                f"KZG-Entry: subtyp={subtyp}, gewicht={gewicht:.2f}, "
                f"inhalt-snippet={inhalt[:60]}"
            )

        logger.info(f"KZG-Entries-Retrieve: {len(entries)} Eintraege geliefert")
        return entries

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: KZG-Entries-Retrieve fehlgeschlagen")
        return []
