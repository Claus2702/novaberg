"""
Gravitationsberechnung — Ziele als Anziehungspunkte im semantischen Raum.

Reine Funktionen ohne I/O. Berechnet die Gravitationswirkung von Zielen
auf den aktuellen Turn über Embedding-Similarity × Motivation.

Wird verwendet von:
  - graph/nodes/enricher.py  (Phase 2 — Ziele laden + Gravitation berechnen)
  - graph/nodes/salience.py  (Phase 2 — Salienz-Boost)
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import redis

from config import (
    EMOTIONALE_GRAVITATION_FAKTOR_KZG,
    EMOTIONALE_GRAVITATION_FAKTOR_LZG,
    EMOTIONALE_GRAVITATION_MAX_PRO_TURN,
    EMOTIONALE_GRAVITATION_ZEIT_HALBWERT,
    EMOTIONALE_GRAVITATIONS_SCHWELLE,
    GRAVITATIONS_SALIENZ_FAKTOR,
    GRAVITATIONS_SCHWELLE,
    LZG_KNOTEN_GEWICHT_CAP,
    REDIS_URL,
)

logger = logging.getLogger("ki_server.ei.gravitation")


@dataclass
class ActivatedGoal:
    """Ein Ziel, dessen Aktivierungs-Stärke über der Schwelle liegt.

    Attributes:
        ziel_id: Datenbank-ID des Ziels.
        ziel_typ: "langfristig", "mittelfristig" oder "kurzfristig" (seit
            28.08.2026 — das kurzfristige ist per Bauart aktiviert, sein
            Tor ist der Verfall, nicht die Schwelle).
        zielsatz: Der Zieltext.
        motivation: Motivationsstärke (0.0-1.0).
        emotion: Emotionale Valenz des Ziels.
        arousal: Emotionale Intensität.
        similarity: Cosine-Similarity zwischen Turn und Ziel.
        aktivierungs_staerke: similarity × motivation — wie stark dieses
            EINE Ziel den Turn anzieht, 0.0 bis 1.0. Nicht zu verwechseln
            mit dem Cluster-Faktor der Wahrnehmungs-Gravitation: der ist
            ein globaler Wert pro Turn (`CLUSTER_GRAVITATION_FAKTOR`).
        embedding: Das Ziel-Embedding, mit dem `similarity` gerechnet wurde.
            Trägt die Verschiebungs-Rechnung (`wahrnehmung_verschieben`);
            None nur, wenn die Quelle keins hatte — dann ist das Ziel gar
            nicht erst aktiviert worden.
    """

    ziel_id:              int
    ziel_typ:             str
    zielsatz:             str
    motivation:           float
    emotion:              str
    arousal:              float
    similarity:           float
    aktivierungs_staerke: float
    embedding:            list[float] | None = None


@dataclass
class Verschiebung:
    """Ergebnis der Wahrnehmungs-Gravitation für genau einen Turn.

    Reiner Datencontainer. Die Rechnung steht in `wahrnehmung_verschieben`,
    die Zerlegung ist für das Pipeline-Log gedacht: ein zusammengesetzter
    Wert ist ohne seine Eingangsgrößen nicht beurteilbar.

    Attributes:
        vektor: Der Suchschlüssel für die Vektorsuche. Bei jeder Herkunft
            außer "verschoben" ist das unverändert das Anfrage-Embedding —
            das Feld ist nie leer, solange die Eingabe gültig war.
        faktor: Der angewandte Mischungs-Anteil, 0.0 bis 0.30.
        cluster: Der GV-Cluster, aus dem der Faktor stammt.
        ziel_anteile: Aktivierungs-Stärke je beitragendem Ziel, in der
            Reihenfolge der Ziele. Einzeln, nicht summiert — sonst ist die
            Zahl später nicht nachrechenbar.
        cosinus_zu_roh: Cosine zwischen rohem und verschobenem Vektor.
            1.0 = nicht verschoben, kleiner = stärker gedreht.
        herkunft: Warum das Ergebnis so aussieht. Geschlossene Menge:
            "verschoben"              — gerechnet
            "anweisung"               — Imperativ-Override, roh gesucht
            "keine_ziele"             — kein aktives Ziel, roh gesucht
            "kein_ziel_embedding"     — Ziele aktiv, aber ohne Embedding
            "verworfen_ausser_spanne" — gerechnet und verworfen, roh gesucht
    """

    vektor:         list[float]
    faktor:         float
    cluster:        str
    ziel_anteile:   list[float]
    cosinus_zu_roh: float
    herkunft:       str


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Berechnet die Cosine Similarity zwischen zwei Vektoren.

    Args:
        vec_a: Erster Vektor.
        vec_b: Zweiter Vektor.

    Returns:
        Cosine Similarity als Float (0.0-1.0), oder 0.0 bei leeren Vektoren.
    """
    if not vec_a or not vec_b:
        return 0.0

    a: np.ndarray = np.array(vec_a)
    b: np.ndarray = np.array(vec_b)

    dot:    float = np.dot(a, b)
    norm_a: float = np.linalg.norm(a)
    norm_b: float = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


def ziel_gravitation_berechnen(
    turn_embedding: list[float],
    ziele: list[dict],
) -> list[ActivatedGoal]:
    """Berechnet die Gravitationswirkung aller Ziele auf den aktuellen Turn.

    Für jedes Ziel: similarity = cosine(turn, ziel), gravitation = similarity × motivation.
    Über GRAVITATIONS_SCHWELLE → aktiviert.

    Args:
        turn_embedding: Embedding des aktuellen Turns (768-dim).
        ziele: Liste von Ziel-Dicts (aus ziele_aktive_laden).

    Returns:
        Liste der aktivierten Ziele, absteigend nach Gravitation sortiert.
    """
    if not turn_embedding:
        logger.debug("Gravitation: Kein Turn-Embedding — keine Berechnung")
        return []

    if not ziele:
        logger.debug("Gravitation: Keine aktiven Ziele")
        return []

    aktiviert: list[ActivatedGoal] = []

    for ziel in ziele:
        ziel_embedding: list[float] | None = ziel.get("embedding")

        if not ziel_embedding:
            logger.debug(
                f"Gravitation: Ziel id={ziel['id']} hat kein Embedding — übersprungen"
            )
            continue

        similarity: float = _cosine_similarity(turn_embedding, ziel_embedding)
        motivation: float = ziel.get("motivation", 0.5)
        staerke:    float = similarity * motivation

        # Ein kurzfristiges Ziel ist per Bauart aktiviert, solange es lebt
        # (novaberg-thinking-lage_k.md §4, Scheibe 2): Es entstand aus dem
        # laufenden Gespraech und verfaellt in Stunden. `[gemessen]` —
        # 28.08.2026: Sein Zielsatz (»Ich moechte dem Nutzer bei seinem
        # Vorhaben helfen: …«) liegt zur Nutzeraeusserung bei Kosinus 0,13
        # bis 0,41, Staerke 0,09 bis 0,29 — die Schwelle 0,40 haette es nie
        # passiert. Die Zahlen bleiben echt: sim und staerke werden nicht
        # gehoben, nur das Tor entfaellt.
        kurzfristig: bool = ziel.get("ziel_typ") == "kurzfristig"
        if staerke >= GRAVITATIONS_SCHWELLE or kurzfristig:
            goal = ActivatedGoal(
                ziel_id=ziel["id"],
                ziel_typ=ziel.get("ziel_typ", "mittelfristig"),
                zielsatz=ziel.get("zielsatz", ""),
                motivation=motivation,
                emotion=ziel.get("emotion", ""),
                arousal=ziel.get("arousal", 0.5),
                similarity=round(similarity, 3),
                aktivierungs_staerke=round(staerke, 3),
                embedding=ziel_embedding,
            )
            aktiviert.append(goal)

            logger.info(
                f"Gravitation: Ziel AKTIVIERT"
                f"{' (kurzfristig, per Bauart)' if kurzfristig and staerke < GRAVITATIONS_SCHWELLE else ''}"
                f" — id={ziel['id']}, "
                f"typ={goal.ziel_typ}, sim={goal.similarity:.3f}, "
                f"mot={motivation:.2f}, staerke={goal.aktivierungs_staerke:.3f}, "
                f"'{goal.zielsatz[:50]}'"
            )
        else:
            logger.debug(
                f"Gravitation: Ziel id={ziel['id']} unter Schwelle — "
                f"sim={similarity:.3f}, mot={motivation:.2f}, "
                f"staerke={staerke:.3f} < {GRAVITATIONS_SCHWELLE}"
            )

    # Absteigend nach Aktivierungs-Stärke sortieren — kurzfristige zuerst:
    # Der GV nimmt die ersten drei, und das Ziel aus dem laufenden Gespraech
    # darf nicht hinter drei staerkeren Charakterzielen verschwinden.
    aktiviert.sort(
        key=lambda g: (g.ziel_typ == "kurzfristig", g.aktivierungs_staerke), reverse=True,
    )

    if aktiviert:
        logger.info(
            f"Gravitation: {len(aktiviert)} Ziele aktiviert von {len(ziele)} — "
            f"stärkstes: staerke={aktiviert[0].aktivierungs_staerke:.3f}, "
            f"'{aktiviert[0].zielsatz[:50]}'"
        )
    else:
        logger.debug(
            f"Gravitation: 0 Ziele aktiviert von {len(ziele)} "
            f"(Schwelle={GRAVITATIONS_SCHWELLE})"
        )

    return aktiviert


def gravitationsterm_berechnen(aktivierte_ziele: list[ActivatedGoal]) -> float:
    """Berechnet den Salienz-Gravitationsterm aus aktivierten Zielen.

    Der Term ist die Summe aller Gravitationswerte, skaliert mit dem
    Salienz-Faktor. Er wird in Phase 2 auf die Basis-Salienz addiert.

    Args:
        aktivierte_ziele: Liste der aktivierten Ziele (aus ziel_gravitation_berechnen).

    Returns:
        Gravitationsterm als Float (kann > 1.0 sein, wird bei der Salienz gecapped).
    """
    if not aktivierte_ziele:
        return 0.0

    # Summe der Aktivierungs-Stärken × Salienz-Faktor.
    # Bei mehreren aktivierten Zielen verstärken sie sich.
    gesamt: float = sum(g.aktivierungs_staerke for g in aktivierte_ziele)
    term:   float = gesamt * GRAVITATIONS_SALIENZ_FAKTOR

    logger.debug(
        f"Gravitationsterm: {len(aktivierte_ziele)} Ziele, "
        f"summe={gesamt:.3f}, faktor={GRAVITATIONS_SALIENZ_FAKTOR}, "
        f"term={term:.3f}"
    )

    return round(term, 4)


# ─────────────────────────────────────────────
# Wahrnehmungs-Gravitation (Konzept §8.5)
# ─────────────────────────────────────────────

def _unverschoben(
    anfrage_embedding: list[float],
    cluster:           str,
    ziel_anteile:      list[float],
    herkunft:          str,
) -> Verschiebung:
    """Baut das Ergebnis für jeden Weg, der ohne Verschiebung endet.

    Es gibt fünf davon (siehe `Verschiebung.herkunft`), und jeder muss
    dieselben Felder setzen. Ein Rückkehrpfad, der die Zerlegung wegließe,
    machte "nicht verschoben" von "nicht gerechnet" ununterscheidbar.

    Vorbedingung: keine — die Funktion baut nur den Container.
    Nachbedingung: `vektor` ist das rohe Anfrage-Embedding, `faktor` 0.0,
        `cosinus_zu_roh` 1.0 (der Vektor ist mit sich selbst identisch).
    """
    return Verschiebung(
        vektor         = anfrage_embedding,
        faktor         = 0.0,
        cluster        = cluster,
        ziel_anteile   = ziel_anteile,
        cosinus_zu_roh = 1.0,
        herkunft       = herkunft,
    )


def wahrnehmung_verschieben(
    anfrage_embedding: list[float],
    aktivierte_ziele:  list[ActivatedGoal],
    cluster:           str,
    ist_anweisung:     bool,
) -> Verschiebung:
    """Verschiebt das Anfrage-Embedding in Richtung der aktivierten Ziele.

    Der Suchschlüssel der Vektorsuche ist dann nicht mehr allein die Frage,
    sondern die Frage plus Novas Motivation — cluster-abhängig stark:

        e_nova = e_anfrage × (1 − faktor)
               + summe(e_ziel × aktivierungs_staerke) × faktor

    Der Faktor ist ein globaler Wert pro Turn aus `CLUSTER_GRAVITATION_FAKTOR`;
    die Aktivierungs-Stärke ist eine Größe pro Ziel. Zwei verschiedene Dinge,
    die im Bestand einmal denselben Namen trugen.

    **Die Summe wird nicht normiert.** Das ist die Formel des Konzepts: Mehrere
    gleichzeitig aktivierte Ziele sollen sich verstärken. Die Folge — der
    Ziel-Anteil kann den Anfrage-Anteil überwiegen — ist der Grund für die
    Spannenprüfung unten.

    Vorbedingung: `anfrage_embedding` ist nicht leer; `cluster` stammt aus der
        Schlüsselmenge von `CLUSTER_GRAVITATION_FAKTOR`; die Ziele stammen aus
        `ziel_gravitation_berechnen` und tragen ihr Embedding.
    Nachbedingung: Der zurückgegebene `vektor` hat dieselbe Dimension wie die
        Eingabe und enthält nur endliche Zahlen. `cosinus_zu_roh` liegt in
        (0.0, 1.0] — ein Suchschlüssel, der von der Frage wegzeigt, ist keine
        Färbung mehr, sondern ein Austausch der Frage.
    Fehlerfälle: Jeder endet mit dem **rohen** Embedding als Suchschlüssel und
        einer Herkunftsmarke; keiner wirft. Leeres Anfrage-Embedding,
        unbekannter Cluster und ein Ergebnis außerhalb der Spanne sind
        `logger.error`; Imperativ, fehlende Ziele und Ziele ohne Embedding
        sind vorgesehene Zustände und werden auf `info` gemeldet.

    Args:
        anfrage_embedding: Rohes Embedding des Turns (768-dim).
        aktivierte_ziele: Ziele über der Schwelle, aus `ziel_gravitation_berechnen`.
        cluster: GV-Cluster des Turns — bestimmt den Mischungs-Anteil.
        ist_anweisung: Trägt der Turn die Salienz-Intention "anweisung".

    Returns:
        Die `Verschiebung` samt Zerlegung für das Pipeline-Log.
    """
    from ei.dreischicht import (
        CLUSTER_GRAVITATION_FAKTOR,
        GRAVITATION_FAKTOR_ANWEISUNG,
    )

    anteile: list[float] = [z.aktivierungs_staerke for z in aktivierte_ziele]

    # ── Eingabe-Validierung ─────────────────────
    if not anfrage_embedding:
        logger.error(
            f"Wahrnehmungs-Gravitation: leeres Anfrage-Embedding, "
            f"Cluster '{cluster}', {len(aktivierte_ziele)} Ziele — "
            f"keine Verschiebung, es gibt nichts zu verschieben"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "kein_anfrage_embedding")

    # Zugehörigkeit zum Kanon: Ein unbekannter Cluster ist ein Defekt und darf
    # nicht still auf einen Vorgabewert fallen — sonst faerbt ein neuer
    # 15. Cluster stillschweigend wie 'paradox'.
    if cluster not in CLUSTER_GRAVITATION_FAKTOR:
        logger.error(
            f"Wahrnehmungs-Gravitation: Cluster '{cluster}' steht nicht in "
            f"CLUSTER_GRAVITATION_FAKTOR ({len(CLUSTER_GRAVITATION_FAKTOR)} bekannt) "
            f"— keine Verschiebung, roh gesucht"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "cluster_unbekannt")

    if ist_anweisung:
        logger.info(
            f"Wahrnehmungs-Gravitation: Imperativ-Override (Intention "
            f"'anweisung'), Faktor {GRAVITATION_FAKTOR_ANWEISUNG} statt "
            f"{CLUSTER_GRAVITATION_FAKTOR[cluster]} aus '{cluster}' — roh gesucht"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "anweisung")

    if not aktivierte_ziele:
        logger.info(
            f"Wahrnehmungs-Gravitation: kein aktives Ziel im Cluster "
            f"'{cluster}' — roh gesucht"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "keine_ziele")

    beitragende: list[ActivatedGoal] = [z for z in aktivierte_ziele if z.embedding]

    if not beitragende:
        logger.info(
            f"Wahrnehmungs-Gravitation: {len(aktivierte_ziele)} Ziele aktiv, "
            f"aber keines mit Embedding — roh gesucht"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "kein_ziel_embedding")

    # ── Verarbeitung ────────────────────────────
    faktor: float = CLUSTER_GRAVITATION_FAKTOR[cluster]

    roh: np.ndarray = np.array(anfrage_embedding, dtype=float)

    ziel_summe: np.ndarray = np.zeros_like(roh)
    for ziel in beitragende:
        if len(ziel.embedding) != len(anfrage_embedding):
            logger.error(
                f"Wahrnehmungs-Gravitation: Ziel id={ziel.ziel_id} hat "
                f"Dimension {len(ziel.embedding)}, Anfrage {len(anfrage_embedding)} "
                f"— keine Verschiebung, roh gesucht"
            )
            return _unverschoben(anfrage_embedding, cluster, anteile, "dimension_ungleich")
        ziel_summe += np.array(ziel.embedding, dtype=float) * ziel.aktivierungs_staerke

    verschoben: np.ndarray = roh * (1.0 - faktor) + ziel_summe * faktor

    # ── Ausgabe-Verifikation ────────────────────
    if not np.all(np.isfinite(verschoben)):
        logger.error(
            f"Wahrnehmungs-Gravitation: Ergebnis enthaelt nicht-endliche Werte "
            f"(Cluster '{cluster}', Faktor {faktor}, {len(beitragende)} Ziele, "
            f"Anteile {[round(a, 3) for a in anteile]}) — verworfen, roh gesucht"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "verworfen_ausser_spanne")

    cosinus: float = _cosine_similarity(anfrage_embedding, verschoben.tolist())

    # Spanne laut Nachbedingung: (0.0, 1.0]. Ein Wert ausserhalb wird gemeldet
    # und verworfen, nicht gekappt — sonst waere eine umgedrehte Frage von
    # einer starken Faerbung nicht mehr zu unterscheiden.
    if not (0.0 < cosinus <= 1.0 + 1e-6):
        logger.error(
            f"Wahrnehmungs-Gravitation: Cosinus zum rohen Embedding "
            f"{cosinus:.4f} ausserhalb der Spanne (0.0, 1.0] — Cluster "
            f"'{cluster}', Faktor {faktor}, {len(beitragende)} Ziele, "
            f"Anteile {[round(a, 3) for a in anteile]} — verworfen, roh gesucht"
        )
        return _unverschoben(anfrage_embedding, cluster, anteile, "verworfen_ausser_spanne")

    logger.info(
        f"Wahrnehmungs-Gravitation: Cluster '{cluster}', Faktor {faktor}, "
        f"{len(beitragende)} Ziele (Anteile {[round(a, 3) for a in anteile]}), "
        f"Cosinus zum rohen Embedding {cosinus:.4f}"
    )

    return Verschiebung(
        vektor         = verschoben.tolist(),
        faktor         = faktor,
        cluster        = cluster,
        ziel_anteile   = anteile,
        cosinus_zu_roh = round(cosinus, 4),
        herkunft       = "verschoben",
    )


# ─────────────────────────────────────────────
# Emotionale Gravitation (EI Phase 3)
# ─────────────────────────────────────────────

def emotionale_gravitation_scannen(
    turn_embedding: list[float],
    redis_client: redis.Redis,
    postgres_url: str,
    user_id: str,
    character_id: str,
) -> list[dict]:
    """Scannt KZG + LZG nach emotional aufgeladenen Erinnerungen.

    Berechnet die emotionale Gravitationskraft pro Eintrag:
    gravitation = similarity × gewicht × zeit_decay × quellen_faktor

    Nur Einträge über EMOTIONALE_GRAVITATIONS_SCHWELLE werden aktiviert.
    Maximal EMOTIONALE_GRAVITATION_MAX_PRO_TURN Einträge.

    Args:
        turn_embedding: Embedding des aktuellen Turns (768-dim).
        redis_client: Redis-Verbindung für KZG-Scan.
        postgres_url: PostgreSQL-URL für LZG-Scan.
        user_id: User-ID.
        character_id: Charakter-ID.

    Returns:
        Liste der aktivierten emotionalen Erinnerungen, absteigend nach Gravitation.
    """
    if not turn_embedding:
        return []

    kandidaten: list[dict] = []
    jetzt: datetime = datetime.now(timezone.utc)

    # ── KZG-Scan (Redis) ──
    kandidaten.extend(
        _kzg_emotionale_eintraege(turn_embedding, redis_client, user_id, character_id, jetzt)
    )

    # ── LZG-Scan (PostgreSQL) ──
    kandidaten.extend(
        _lzg_emotionale_eintraege(turn_embedding, postgres_url, user_id, character_id, jetzt)
    )

    # Sortieren nach Gravitation, Top-N
    kandidaten.sort(key=lambda k: k["gravitation"], reverse=True)
    aktiviert: list[dict] = kandidaten[:EMOTIONALE_GRAVITATION_MAX_PRO_TURN]

    if aktiviert:
        logger.info(
            f"Emotionale Gravitation: {len(aktiviert)} von {len(kandidaten)} "
            f"Kandidaten aktiviert"
        )

    return aktiviert


def _zeit_decay_faktor(erstellt: datetime, jetzt: datetime) -> float:
    """Berechnet den zeitlichen Decay-Faktor für emotionale Gravitation.

    Exponentieller Verfall mit EMOTIONALE_GRAVITATION_ZEIT_HALBWERT.

    Args:
        erstellt: Erstellungs-/Verstärkungszeitpunkt.
        jetzt: Aktuelle Zeit.

    Returns:
        Decay-Faktor zwischen 0.0 und 1.0.
    """
    if erstellt.tzinfo is None:
        erstellt = erstellt.replace(tzinfo=timezone.utc)

    tage: float = max(0.0, (jetzt - erstellt).total_seconds() / 86400.0)
    decay_rate: float = math.log(2) / EMOTIONALE_GRAVITATION_ZEIT_HALBWERT

    return math.exp(-decay_rate * tage)


def _kzg_emotionale_eintraege(
    turn_embedding: list[float],
    redis_client: redis.Redis,
    user_id: str,
    character_id: str,
    jetzt: datetime,
) -> list[dict]:
    """Scannt KZG-Einträge mit Emotion und berechnet Gravitation.

    Iteriert über alle KZG-Einträge des Paares, filtert auf vorhandene
    Emotion, berechnet Cosine-Similarity gegen Turn-Embedding.

    Embedding wird über einen separaten decode_responses=False-Client gelesen,
    da der Default-Client (decode_responses=True) den Float32-Blob korrumpiert.

    Args:
        turn_embedding: Embedding des aktuellen Turns.
        redis_client: Redis-Verbindung (decode_responses=True, für Text-Felder).
        user_id: User-ID.
        character_id: Charakter-ID.
        jetzt: Aktuelle Zeit für Decay.

    Returns:
        Liste von Kandidaten-Dicts über der Schwelle.
    """
    from memory.kzg import _kzg_prefix

    kandidaten: list[dict] = []
    prefix: str = _kzg_prefix(user_id, character_id)

    # Separater Raw-Client für die Embedding-Bytes
    raw_redis: redis.Redis = redis.from_url(REDIS_URL, decode_responses=False)

    for key in redis_client.scan_iter(match=prefix, count=100):
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        emotion: str = redis_client.hget(key, "emotion") or ""
        if not emotion or emotion == "neutral":
            continue

        # Embedding aus dem Raw-Client (Float32-Bytes)
        embedding_bytes = raw_redis.hget(key, "embedding")
        if not embedding_bytes:
            continue

        try:
            eintrag_embedding: list[float] = np.frombuffer(
                embedding_bytes, dtype=np.float32
            ).tolist()
        except (ValueError, TypeError):
            continue

        # Similarity berechnen
        similarity: float = _cosine_similarity(turn_embedding, eintrag_embedding)

        # Salienz als Gewicht
        salienz_raw: str = redis_client.hget(key, "salienz") or ""
        gewicht: float = 0.5
        if salienz_raw:
            try:
                gewicht = float(salienz_raw)
            except (ValueError, TypeError):
                pass

        # Arousal
        arousal_raw: str = redis_client.hget(key, "arousal") or ""
        arousal: float = 0.5
        if arousal_raw:
            try:
                arousal = float(arousal_raw)
            except (ValueError, TypeError):
                pass

        # Erstellt-Zeitpunkt für Decay (Unix-Timestamp-String, siehe kzg_store)
        erstellt_raw: str = redis_client.hget(key, "erstellt_am") or ""
        zeit_decay: float = 1.0
        if erstellt_raw:
            try:
                erstellt: datetime = datetime.fromtimestamp(
                    float(erstellt_raw), tz=timezone.utc,
                )
                zeit_decay = _zeit_decay_faktor(erstellt, jetzt)
            except (ValueError, TypeError):
                pass

        # Gravitation berechnen
        gravitation: float = similarity * gewicht * zeit_decay * EMOTIONALE_GRAVITATION_FAKTOR_KZG

        if gravitation >= EMOTIONALE_GRAVITATIONS_SCHWELLE:
            inhalt: str = redis_client.hget(key, "inhalt") or ""

            kandidaten.append({
                "knoten_id":   key,
                "emotion":     emotion,
                "arousal":     arousal,
                "similarity":  round(similarity, 3),
                "gewicht":     round(gewicht, 3),
                "zeit_decay":  round(zeit_decay, 3),
                "gravitation": round(gravitation, 3),
                "quelle":      "kzg",
                "inhalt":      inhalt[:100],
            })

            logger.debug(
                f"EmGrav KZG: {emotion}(a={arousal:.2f}), "
                f"sim={similarity:.3f}, grav={gravitation:.3f}, "
                f"'{inhalt[:40]}'"
            )

    return kandidaten


def gravitation_lzg_berechnen(
    similarity:    float,
    gewicht_decay: float,
    zeit_decay:    float,
) -> float:
    """Berechnet die emotionale Gravitation eines LZG-Knotens.

    Eigene Funktion, weil die Formel sonst nur hinter einer Datenbankabfrage
    erreichbar waere — ein Zeuge muesste sie dann nachrechnen statt aufrufen und
    bliebe gruen, wenn sich die echte Rechnung aendert.

    `gewicht_decay` steht auf [0, LZG_KNOTEN_GEWICHT_CAP], die Schwelle auf
    [0,1]. Ohne die Division vergleicht die Rechnung zwei Skalen und lehnt
    nichts mehr ab: Gemessen am 30.08.2026 riss jeder der 1711 scanbaren Knoten
    die Schwelle schon bei `similarity < 0,30` (`gewicht_decay` Median 3,77,
    Maximum 9,98, alle 3266 aktiven Knoten ueber 1) — Bug EMGRAV-SCHWELLE-TOT.

    Geteilt wird durch die **Konstante**, nicht durch die Zahl, damit die
    Normierung einer Skalenaenderung folgt. Der Wert ist ohnehin normiert
    erzeugt: `gewicht_absolut_berechnen` rechnet `CAP * sin(...)**exp`, und der
    Sinusterm liegt in [0,1] — die Division nimmt nur den Streckfaktor zurueck
    und verliert nichts (755 verschiedene Werte bleiben 755).

    Args:
        similarity: Kosinus-Aehnlichkeit zum Turn-Embedding, [0,1].
        gewicht_decay: Praesenz-Wert des Knotens, [0, LZG_KNOTEN_GEWICHT_CAP].
        zeit_decay: Zeitfaktor der emotionalen Praesenz, [0,1].

    Returns:
        Gravitation auf [0, EMOTIONALE_GRAVITATION_FAKTOR_LZG].

    Raises:
        ValueError: Wenn `gewicht_decay` negativ ist oder den Deckel ueberschreitet.
    """
    # ── Eingabe ────────────────────────────────
    if not 0.0 <= gewicht_decay <= LZG_KNOTEN_GEWICHT_CAP:
        raise ValueError(
            f"gewicht_decay={gewicht_decay} liegt ausserhalb "
            f"[0, {LZG_KNOTEN_GEWICHT_CAP}] — die Skala ist nicht die erwartete, "
            f"und die Normierung darunter waere eine Behauptung statt einer Rechnung"
        )

    # ── Verarbeitung ───────────────────────────
    gewicht_norm: float = gewicht_decay / LZG_KNOTEN_GEWICHT_CAP
    gravitation:  float = (
        similarity * gewicht_norm * zeit_decay * EMOTIONALE_GRAVITATION_FAKTOR_LZG
    )

    # ── Ausgabe ────────────────────────────────
    return gravitation


def _lzg_emotionale_eintraege(
    turn_embedding: list[float],
    postgres_url: str,
    user_id: str,
    character_id: str,
    jetzt: datetime,
) -> list[dict]:
    """Scannt LZG-Einträge mit Emotion und berechnet Gravitation.

    SQL-Query mit Embedding-Similarity und Emotion-Filter.

    Args:
        turn_embedding: Embedding des aktuellen Turns.
        postgres_url: PostgreSQL-URL.
        user_id: User-ID.
        character_id: Charakter-ID.
        jetzt: Aktuelle Zeit für Decay.

    Returns:
        Liste von Kandidaten-Dicts über der Schwelle.
    """
    import psycopg2

    embedding_str: str = "[" + ",".join(str(x) for x in turn_embedding) + "]"

    try:
        conn = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, inhalt, emotion, arousal, gewicht_decay, verstaerkt_am,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM lzg_knoten
            WHERE user_id = %s
              AND character_id = %s
              AND aktiv = TRUE
              AND embedding IS NOT NULL
              AND emotion != ''
              AND emotion != 'neutral'
            ORDER BY embedding <=> %s::vector
            LIMIT 10
        """, (embedding_str, user_id, character_id, embedding_str))

        rows = cursor.fetchall()
        conn.close()

    except Exception as fehler:
        logger.warning(f"EmGrav LZG-Scan fehlgeschlagen: {fehler}")
        return []

    kandidaten: list[dict] = []

    for knoten_id, inhalt, emotion, arousal, gewicht_decay, verstaerkt_am, similarity in rows:
        # `gewicht_decay` ist BEREITS der zeitlich abgewertete Praesenz-Wert:
        # Der Decay-Lauf materialisiert ihn taeglich als
        # `gewicht_absolut * exp(-rate * tage_seit_verstaerkung)`
        # (novaberg-memory-synapsen_k.md §9.2).
        #
        # Bis Chat 125 lief er hier ein zweites Mal durch dieselbe Formel mit
        # derselben Rate — die Absicht war, den Ebbinghaus-Verfall zu teilen,
        # aber die Eingabe war seit dem Synapsen-Umbau nicht mehr das rohe
        # Gewicht. Jede Erinnerung wurde damit gewichtet, als waere sie doppelt
        # so alt: exp(-2rt) statt exp(-rt).

        # Zeit-Decay für emotionale Gravitation (eigener, langsamerer Decay).
        # Er bleibt: Er ist keine Wiederholung, sondern eine zweite, bewusst
        # flachere Kurve fuer die emotionale Praesenz (§8.4.3).
        zeit_decay: float = _zeit_decay_faktor(verstaerkt_am, jetzt)

        # Gravitation berechnen — die Formel steht in einer eigenen Funktion,
        # damit ein Zeuge sie aufrufen kann statt sie nachzurechnen.
        gewicht_norm: float = gewicht_decay / LZG_KNOTEN_GEWICHT_CAP
        gravitation:  float = gravitation_lzg_berechnen(
            similarity, gewicht_decay, zeit_decay,
        )

        if gravitation >= EMOTIONALE_GRAVITATIONS_SCHWELLE:
            kandidaten.append({
                "knoten_id":   knoten_id,
                "emotion":     emotion,
                "arousal":     arousal or 0.5,
                "similarity":  round(similarity, 3),
                # `gewicht` bleibt der **gespeicherte** Wert: Die Zusicherung aus
                # P9a (kein zweiter Verfallsabzug beim Lesen) prueft ihn gegen die
                # Spalte. Der normierte Wert steht daneben, damit die Rechnung
                # nachvollziehbar bleibt, ohne die Spur zur Spalte zu verlieren.
                "gewicht":     round(gewicht_decay, 3),
                "gewicht_norm": round(gewicht_norm, 3),
                "zeit_decay":  round(zeit_decay, 3),
                "gravitation": round(gravitation, 3),
                "quelle":      "lzg",
                "inhalt":      (inhalt or "")[:100],
            })

            logger.debug(
                f"EmGrav LZG: {emotion}(a={arousal:.2f}), "
                f"sim={similarity:.3f}, gew_decay={gewicht_decay:.3f}, "
                f"grav={gravitation:.3f}, '{(inhalt or '')[:40]}'"
            )

    return kandidaten


def emotionale_gravitation_auf_verlauf_anwenden(
    nova_verlauf: list[dict],
    gravitationspunkte: list[dict],
) -> list[dict]:
    """Injiziert emotionale Gravitation in Novas Emotions-Verlauf.

    Für jeden aktivierten Gravitationspunkt wird dessen Emotion
    mit einem Gewicht proportional zur Gravitationsstärke in den
    Verlauf injiziert — analoges Muster zur Empathie-Injektion
    in _nova_empathie_berechnen().

    Args:
        nova_verlauf: Novas aktueller Verlauf (nach Decay + Empathie).
        gravitationspunkte: Aktivierte emotionale Erinnerungen
                           (aus state["emotionale_gravitationspunkte"]).

    Returns:
        Modifizierter Verlauf mit injizierten Erinnerungs-Emotionen.
    """
    if not gravitationspunkte:
        return nova_verlauf

    modifiziert: list[dict] = list(nova_verlauf)

    for punkt in gravitationspunkte:
        emotion:     str   = punkt.get("emotion", "")
        arousal:     float = punkt.get("arousal", 0.5)
        gravitation: float = punkt.get("gravitation", 0.0)

        if not emotion or emotion == "neutral":
            continue

        # Gravitation als Injektions-Gewicht. Gecapped auf 0.5 — Erinnerungen
        # sollen Novas Emotion färben, nicht überschreiben.
        #
        # **Faktor von 0.6 auf 0.25 gezogen am 31.08.2026**, mit der
        # Reizstärke-Kalibrierung (`novaberg-ei.md` §Reizstärke). Nicht die
        # Injektion ist gewachsen — **das Feld ist enger geworden**: Der Abstand
        # zwischen Führung und Platz zwei fiel im Median von 0,52 auf 0,27.
        # Dieselbe Injektion, die vorher unter jedem Abstand lag, sortierte
        # danach in 172 von 1178 Paarungen um (vorher 2). Bei 0.25 sind es 58,
        # davon 48 unvermeidbar: Zwei Zustände tragen einen exakten Gleichstand
        # an der Spitze, den jede Injektion über 0,005 kippt.
        #
        # **Der Cap greift nie und ist kein Stellrad.** Der höchste im Bestand
        # vorkommende Gravitationswert ist 0,558; mit Faktor 0.25 sind das
        # 0,140. Zwischen Cap 0.50 und 0.25 ändert sich nichts.
        #
        # Tiefer als 0.25 nicht: Bei Faktor 0.15 fallen 620 von 1178 Injektionen
        # unter EMOTION_MIN_WEIGHT und verschwinden aus dem Verlauf, während die
        # Umsortierungen nur von 58 auf 48 sinken — die Rechnung wäre tot.
        injektions_gewicht: float = min(0.5, gravitation * 0.25)

        # Prüfen ob die Emotion schon in Novas Verlauf existiert
        gefunden: bool = False
        for eintrag in modifiziert:
            if eintrag["emotion"] == emotion:
                eintrag["gewicht"] = round(
                    min(1.0, eintrag["gewicht"] + injektions_gewicht), 2
                )
                eintrag["arousal"] = round(
                    min(1.0, max(eintrag.get("arousal", 0.0), arousal * gravitation)), 2
                )
                gefunden = True
                break

        if not gefunden:
            modifiziert.append({
                "emotion": emotion,
                "gewicht": round(injektions_gewicht, 2),
                "arousal": round(min(1.0, arousal * gravitation), 2),
            })

        logger.info(
            f"EmGrav Injektion: {emotion} (grav={gravitation:.3f}, "
            f"gewicht={injektions_gewicht:.3f}, quelle={punkt.get('quelle', '?')})"
        )

    # Neu sortieren
    modifiziert.sort(key=lambda e: e["gewicht"], reverse=True)

    return modifiziert
