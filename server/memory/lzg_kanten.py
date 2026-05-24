"""
LZG-Kanten — Assoziationen zwischen Synapsen-Knoten (Schreibpfad, Konzept §5/§7).

Die Kante hat keine eigene Substanz (Konzept §2.3): Sie ist ein abgeleiteter
Cache der aktuellen Knoten-Anker-Staerken (lzg_knoten.gewicht_absolut) und der
bei Bildung eingefrorenen Schicht-Werte. Kein eigenes Decay, kein eigenes
Reinforcement, keine Aktivierungs-Historie.

Dieses Modul kapselt:
  - die reine Kanten-Mathematik (Schicht-Auswahl, Sinus-Geometrie, Tiefe-Faktor)
  - die Schicht-Ausloesung (vier Schichten: Entitaet, Embedding, Themen, Timeline)
  - die CRUD-Upsert-Operation auf lzg_kanten
  - Trigger 1 (Kantenbildung bei Knoten-Anlage)
  - Trigger 2 (Neuberechnung aller Kanten eines Knotens bei Reinforcement)

Hausstil mirrort memory/lzg.py: synchrone psycopg2-Verbindung, deutsche
Docstrings (ae/oe/ue-Transliteration), logger.info/error an DB-Operationen.
"""

import logging
import math
from datetime import datetime
from typing import Optional

import psycopg2
import psycopg2.extras

from config import (
    LZG_KANTEN_GEWICHT_CAP,
    LZG_KANTEN_DAEMPFUNG_EXP,
    LZG_KANTEN_ZIEH_FAKTOR_HOCH,
    LZG_KANTEN_ZIEH_FAKTOR_RUNTER,
    LZG_KANTEN_SCHICHT_BONUS,
    LZG_SCHICHT_FAKTOR_ENTITAET,
    LZG_SCHICHT_FAKTOR_EMBEDDING,
    LZG_SCHICHT_FAKTOR_THEMEN,
    LZG_SCHICHT_FAKTOR_TIMELINE,
    LZG_EMBEDDING_SCHWELLWERT,
    LZG_TIMELINE_TOLERANZ_MINUTE,
    LZG_TIMELINE_TOLERANZ_TAG,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schicht-Bezeichner — werden eingefroren in lzg_kanten.verbindungs_gruende
# gespeichert. Trigger 2 leitet die Schicht-Auswahl wieder aus diesen Strings
# ab, daher muessen die Werte stabil bleiben.
# ---------------------------------------------------------------------------
SCHICHT_ENTITAET = "entitaet"
SCHICHT_EMBEDDING = "embedding"
SCHICHT_THEMEN = "themen"
SCHICHT_TIMELINE = "timeline"

# Statische Wertigkeit der Verbindungsquelle (Konzept §7.4). Die greifende
# Schicht mit dem hoechsten Faktor gewinnt und setzt Anker und Tiefe.
SCHICHT_FAKTOREN = {
    SCHICHT_ENTITAET: LZG_SCHICHT_FAKTOR_ENTITAET,    # 1.0
    SCHICHT_EMBEDDING: LZG_SCHICHT_FAKTOR_EMBEDDING,  # 0.8
    SCHICHT_THEMEN: LZG_SCHICHT_FAKTOR_THEMEN,        # 0.5
    SCHICHT_TIMELINE: LZG_SCHICHT_FAKTOR_TIMELINE,    # 0.4
}

# Timeline-Toleranz pro Live-Praezision. Die DB kennt aktuell nur 'day' und
# 'minute' (timeline.precision VARCHAR(10)); beide rechnen die Distanz in
# Tagen (Konzept §7.6.2). Weitere Stufen werden ergaenzt, sobald der
# Zeitparser sie liefert.
TIMELINE_TOLERANZ_TAGE = {
    "minute": LZG_TIMELINE_TOLERANZ_MINUTE,  # 7
    "day": LZG_TIMELINE_TOLERANZ_TAG,        # 21
}


# ===========================================================================
# Reine Mathematik (ohne DB, voll unit-testbar)
# ===========================================================================

def kante_daempfen(gewicht_roh: float) -> float:
    """
    Daempft den frei berechneten Kanten-Roh-Wert auf den gekappten
    gewicht_absolut (Konzept §5.4 Schritt 5 / §7.9.1 Schritt 8).

    Formel: cap * sin(min(roh/cap, 1) * pi/2) ** exp
    """
    anteil = min(gewicht_roh / LZG_KANTEN_GEWICHT_CAP, 1.0)
    return LZG_KANTEN_GEWICHT_CAP * (math.sin(anteil * math.pi / 2) ** LZG_KANTEN_DAEMPFUNG_EXP)


def themen_tiefe(themen_a: list[str], themen_b: list[str]) -> tuple[float, list[str]]:
    """
    Tiefe-Faktor der Themen-Schicht (Konzept §7.4): geteilte / max(laenge_a,
    laenge_b). 'max' straft Breite — ein themenbreiter Knoten bindet anteilig
    schwaecher. Liefert (tiefe, geteilte_themen).
    """
    menge_a = {t for t in (themen_a or []) if t}
    menge_b = {t for t in (themen_b or []) if t}
    geteilt = sorted(menge_a & menge_b)
    if not geteilt:
        return 0.0, []
    nenner = max(len(menge_a), len(menge_b))
    tiefe = len(geteilt) / nenner if nenner else 0.0
    return tiefe, geteilt


def embedding_tiefe(cosine: float) -> float:
    """
    Tiefe-Faktor der Embedding-Schicht (Konzept §7.4): linear von 0.0 am
    Schwellwert bis 1.0 bei Cosine 1.0. Vorbedingung: cosine ueber Schwellwert
    (sonst greift die Schicht gar nicht).
    """
    spanne = 1.0 - LZG_EMBEDDING_SCHWELLWERT
    if spanne <= 0:
        return 1.0
    return max(0.0, min(1.0, (cosine - LZG_EMBEDDING_SCHWELLWERT) / spanne))


def timeline_distanz_tage(
    event_time_a: Optional[datetime],
    event_time_b: Optional[datetime],
) -> Optional[int]:
    """
    Ganzzahlige Distanz in Tagen zwischen zwei Zeitpunkten. None, wenn ein
    Zeitpunkt fehlt.
    """
    if event_time_a is None or event_time_b is None:
        return None
    return abs((event_time_a.date() - event_time_b.date()).days)


def timeline_tiefe(
    praezision_a: Optional[str],
    praezision_b: Optional[str],
    event_time_a: Optional[datetime],
    event_time_b: Optional[datetime],
) -> tuple[float, Optional[int]]:
    """
    Tiefe-Faktor der Timeline-Schicht (Konzept §7.6). Drei harte Bedingungen
    muessen gleichzeitig gelten, sonst greift die Schicht nicht:
      1. beide Knoten haben einen Timeline-Bezug,
      2. ihre Praezisions-Stufen sind identisch,
      3. die Distanz liegt innerhalb der Toleranz dieser Praezision.

    Liefert (tiefe, distanz_tage). tiefe 0.0 signalisiert: Schicht greift nicht.
    """
    if not praezision_a or not praezision_b or praezision_a != praezision_b:
        return 0.0, None
    toleranz = TIMELINE_TOLERANZ_TAGE.get(praezision_a)
    if toleranz is None:
        # Praezisions-Stufe noch nicht abgebildet — Schicht greift nicht.
        return 0.0, None
    distanz = timeline_distanz_tage(event_time_a, event_time_b)
    if distanz is None or distanz > toleranz:
        return 0.0, None
    tiefe = (toleranz - distanz) / toleranz
    return tiefe, distanz


def schichten_ermitteln(neuer: dict, kandidat: dict) -> tuple[dict, dict]:
    """
    Prueft alle vier Schichten zwischen neuem Knoten und Kandidat (Konzept §7.3)
    und liefert (schicht_tiefen, freeze).

    neuer/kandidat sind Dicts mit den Schluesseln: gewicht_absolut, entitaet_ids,
    themen, timeline_praezision, timeline_event_time. 'kandidat' traegt
    zusaetzlich 'cosine' (vorab in SQL berechnete Cosine-Similarity zum neuen
    Knoten).

    schicht_tiefen: {schicht_name: tiefe_faktor} nur fuer greifende Schichten.
    freeze: einzufrierende Verbindungs-Charakteristik fuer lzg_kanten.
    """
    schicht_tiefen: dict[str, float] = {}
    freeze = {
        "verbindungs_gruende": [],
        "geteilte_entitaet_ids": [],
        "geteilte_themen": [],
        "timeline_naehe_tage": None,
        "embedding_cosine_initial": None,
    }

    # Entitaets-Schicht: mindestens eine geteilte Entitaet
    geteilte_ent = sorted(set(neuer.get("entitaet_ids") or []) & set(kandidat.get("entitaet_ids") or []))
    if geteilte_ent:
        schicht_tiefen[SCHICHT_ENTITAET] = 1.0  # binaer (Konzept §7.4)
        freeze["verbindungs_gruende"].append(SCHICHT_ENTITAET)
        freeze["geteilte_entitaet_ids"] = geteilte_ent

    # Embedding-Schicht: Cosine ueber Schwellwert
    cosine = kandidat.get("cosine")
    if cosine is not None and cosine > LZG_EMBEDDING_SCHWELLWERT:
        schicht_tiefen[SCHICHT_EMBEDDING] = embedding_tiefe(cosine)
        freeze["verbindungs_gruende"].append(SCHICHT_EMBEDDING)
        freeze["embedding_cosine_initial"] = cosine

    # Themen-Schicht: mindestens ein geteiltes Thema
    t_tiefe, geteilte_themen = themen_tiefe(neuer.get("themen"), kandidat.get("themen"))
    if geteilte_themen:
        schicht_tiefen[SCHICHT_THEMEN] = t_tiefe
        freeze["verbindungs_gruende"].append(SCHICHT_THEMEN)
        freeze["geteilte_themen"] = geteilte_themen

    # Timeline-Schicht: Praezisions-Gleichheit + Distanz in Toleranz
    tl_tiefe, distanz = timeline_tiefe(
        neuer.get("timeline_praezision"), kandidat.get("timeline_praezision"),
        neuer.get("timeline_event_time"), kandidat.get("timeline_event_time"),
    )
    if tl_tiefe > 0.0 or distanz is not None:
        # distanz ist nur dann nicht None, wenn alle drei Timeline-Bedingungen
        # erfuellt sind (timeline_tiefe liefert sonst (0.0, None)).
        if distanz is not None:
            schicht_tiefen[SCHICHT_TIMELINE] = tl_tiefe
            freeze["verbindungs_gruende"].append(SCHICHT_TIMELINE)
            freeze["timeline_naehe_tage"] = distanz

    return schicht_tiefen, freeze


def kanten_staerke_berechnen(
    a_absolut: float,
    b_absolut: float,
    schicht_tiefen: dict[str, float],
) -> tuple[float, float]:
    """
    Berechnet die gerichteten Kanten-Roh-Staerken (A->B, B->A) aus den
    Anker-Staerken beider Knoten und den greifenden Schichten (Konzept §7.5).

    Ablauf:
      1. Gewinner-Schicht = hoechster Schicht-Faktor unter den greifenden.
         max_faktor + Tiefe stammen ausschliesslich vom Gewinner. Andere
         greifende Schichten tragen nur ueber den Schicht-Bonus bei.
      2. Vorgewichtete Anker: A' = A.absolut * max_faktor + bonus (analog B').
      3. Sinus-Geometrie auf dem schwaecheren/staerkeren Anker: der schwaechere
         wird stark hochgezogen (ZIEH_HOCH), der staerkere leicht herunter
         (ZIEH_RUNTER).
      4. Anhebung * Tiefe, Anker ist immer der schwaechere Wert (die Kante kann
         ihn nicht unterschreiten).

    Liefert die Roh-Werte (gewicht_roh) der beiden Richtungen — die Daempfung
    auf gewicht_absolut erfolgt separat ueber kante_daempfen.
    """
    if not schicht_tiefen:
        raise ValueError("kanten_staerke_berechnen ohne greifende Schicht aufgerufen")

    gewinner = max(schicht_tiefen, key=lambda s: SCHICHT_FAKTOREN[s])
    max_faktor = SCHICHT_FAKTOREN[gewinner]
    tiefe = schicht_tiefen[gewinner]
    bonus = LZG_KANTEN_SCHICHT_BONUS * (len(schicht_tiefen) - 1)

    a1 = a_absolut * max_faktor + bonus
    b1 = b_absolut * max_faktor + bonus

    weak, strong = (a1, b1) if a1 <= b1 else (b1, a1)
    diff = strong - weak
    sinus_weak_strong = weak + diff * LZG_KANTEN_ZIEH_FAKTOR_HOCH
    sinus_strong_weak = strong - diff * LZG_KANTEN_ZIEH_FAKTOR_RUNTER

    # Anker = schwaecherer Knoten; Anhebung mit der Tiefe skaliert.
    kante_weak_strong = weak + (sinus_weak_strong - weak) * tiefe
    kante_strong_weak = weak + (sinus_strong_weak - weak) * tiefe

    if a1 <= b1:
        return kante_weak_strong, kante_strong_weak  # A schwach: A->B, B->A
    return kante_strong_weak, kante_weak_strong       # A stark:  A->B, B->A


# ===========================================================================
# CRUD + Trigger
# ===========================================================================

def _kante_upsert(cur, knoten_a_id: int, knoten_b_id: int, roh: float, freeze: dict) -> None:
    """
    Schreibt eine gerichtete Kante (A->B) per UPSERT. Bei bestehender Kante
    (UNIQUE knoten_a_id, knoten_b_id) wird der Cache-Wert plus die eingefrorene
    Charakteristik aktualisiert (Trigger 2). Erwartet einen offenen Cursor.
    """
    absolut = kante_daempfen(roh)
    cur.execute(
        """
        INSERT INTO lzg_kanten (
            knoten_a_id, knoten_b_id, gewicht_roh, gewicht_absolut,
            verbindungs_gruende, geteilte_entitaet_ids, geteilte_themen,
            timeline_naehe_tage, embedding_cosine_initial, anzahl_schichten
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (knoten_a_id, knoten_b_id) DO UPDATE SET
            gewicht_roh = EXCLUDED.gewicht_roh,
            gewicht_absolut = EXCLUDED.gewicht_absolut
        """,
        (
            knoten_a_id, knoten_b_id, roh, absolut,
            freeze["verbindungs_gruende"],
            freeze["geteilte_entitaet_ids"],
            freeze["geteilte_themen"],
            freeze["timeline_naehe_tage"],
            freeze["embedding_cosine_initial"],
            len(freeze["verbindungs_gruende"]),
        ),
    )


def kanten_fuer_neuen_knoten_bilden(
    postgres_url: str,
    neuer: dict,
    kandidaten: list[dict],
) -> int:
    """
    Trigger 1 (Konzept §7.9.2): Bildet Kanten vom neuen Knoten zu allen
    Kandidaten, bei denen mindestens eine Schicht greift. Pro Treffer entstehen
    zwei gerichtete Kanten (A->B und B->A).

    neuer: Dict mit 'id', 'gewicht_absolut', 'entitaet_ids', 'themen',
           'timeline_praezision', 'timeline_event_time'.
    kandidaten: Liste gleicher Dicts, jeweils mit zusaetzlichem 'cosine'.

    Liefert die Anzahl gebildeter Knoten-Paare (nicht Einzel-Kanten).
    """
    neuer_id = neuer["id"]
    paare = 0
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            for kandidat in kandidaten:
                if kandidat["id"] == neuer_id:
                    continue
                schicht_tiefen, freeze = schichten_ermitteln(neuer, kandidat)
                if not schicht_tiefen:
                    continue
                roh_ab, roh_ba = kanten_staerke_berechnen(
                    neuer["gewicht_absolut"], kandidat["gewicht_absolut"], schicht_tiefen
                )
                _kante_upsert(cur, neuer_id, kandidat["id"], roh_ab, freeze)
                _kante_upsert(cur, kandidat["id"], neuer_id, roh_ba, freeze)
                paare += 1
                logger.info(
                    "Kante gebildet: %s<->%s gruende=%s roh(a->b)=%.3f roh(b->a)=%.3f",
                    neuer_id, kandidat["id"], freeze["verbindungs_gruende"], roh_ab, roh_ba,
                )
        conn.commit()
        logger.info("Trigger 1 abgeschlossen: Knoten %s, %d Kanten-Paare gebildet", neuer_id, paare)
        return paare
    except psycopg2.Error as exc:
        conn.rollback()
        logger.error("kanten_fuer_neuen_knoten_bilden fehlgeschlagen knoten=%s: %s", neuer_id, exc)
        return 0
    finally:
        conn.close()


def kanten_neuberechnen_fuer_knoten(postgres_url: str, knoten_id: int) -> int:
    """
    Trigger 2 (Konzept §7.9.2): Nach einer Aktivierung (Reinforcement) eines
    Knotens werden alle Kanten von und zu ihm neu berechnet. Eingaben sind die
    aktuellen Anker-Staerken beider Endknoten und die eingefrorenen Schicht-
    Werte der Kante (verbindungs_gruende, embedding_cosine_initial,
    timeline_naehe_tage) plus die Live-Themen/Timeline-Daten der Knoten.

    Liefert die Anzahl neu berechneter gerichteter Kanten.
    """
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Alle gerichteten Kanten, an denen der Knoten beteiligt ist, plus
            # die Live-Daten beider Endknoten fuer die Tiefe-Rekonstruktion.
            cur.execute(
                """
                SELECT k.id, k.knoten_a_id, k.knoten_b_id,
                       k.verbindungs_gruende, k.embedding_cosine_initial,
                       k.timeline_naehe_tage,
                       a.gewicht_absolut AS a_absolut, a.themen AS a_themen,
                       b.gewicht_absolut AS b_absolut, b.themen AS b_themen,
                       ta.precision AS a_praezision, tb.precision AS b_praezision
                FROM lzg_kanten k
                JOIN lzg_knoten a ON a.id = k.knoten_a_id
                JOIN lzg_knoten b ON b.id = k.knoten_b_id
                LEFT JOIN timeline ta ON ta.id = a.timeline_id
                LEFT JOIN timeline tb ON tb.id = b.timeline_id
                WHERE k.knoten_a_id = %s OR k.knoten_b_id = %s
                """,
                (knoten_id, knoten_id),
            )
            kanten = cur.fetchall()

            aktualisiert = 0
            for kante in kanten:
                schicht_tiefen = _schicht_tiefen_aus_frozen(kante)
                if not schicht_tiefen:
                    # Sollte nicht vorkommen — Kante ohne Grund. Defensiv ueberspringen.
                    logger.error("Kante %s ohne rekonstruierbare Schicht — uebersprungen", kante["id"])
                    continue
                # Richtung der gespeicherten Kante: knoten_a_id -> knoten_b_id.
                roh_ab, _ = kanten_staerke_berechnen(
                    kante["a_absolut"], kante["b_absolut"], schicht_tiefen
                )
                cur.execute(
                    "UPDATE lzg_kanten SET gewicht_roh = %s, gewicht_absolut = %s WHERE id = %s",
                    (roh_ab, kante_daempfen(roh_ab), kante["id"]),
                )
                aktualisiert += 1
        conn.commit()
        logger.info("Trigger 2 abgeschlossen: Knoten %s, %d Kanten neu berechnet", knoten_id, aktualisiert)
        return aktualisiert
    except psycopg2.Error as exc:
        conn.rollback()
        logger.error("kanten_neuberechnen_fuer_knoten fehlgeschlagen knoten=%s: %s", knoten_id, exc)
        return 0
    finally:
        conn.close()


def _schicht_tiefen_aus_frozen(kante: dict) -> dict[str, float]:
    """
    Rekonstruiert die schicht_tiefen einer bestehenden Kante aus ihren
    eingefrorenen Gruenden plus den Live-Daten beider Knoten (Trigger 2).
    Entitaet ist binaer; Embedding nutzt die eingefrorene Initial-Cosine;
    Themen werden aus den Live-Themen neu bestimmt; Timeline aus der
    eingefrorenen Naehe und den Live-Praezisionen.
    """
    gruende = kante.get("verbindungs_gruende") or []
    schicht_tiefen: dict[str, float] = {}

    if SCHICHT_ENTITAET in gruende:
        schicht_tiefen[SCHICHT_ENTITAET] = 1.0
    if SCHICHT_EMBEDDING in gruende and kante.get("embedding_cosine_initial") is not None:
        schicht_tiefen[SCHICHT_EMBEDDING] = embedding_tiefe(kante["embedding_cosine_initial"])
    if SCHICHT_THEMEN in gruende:
        t_tiefe, geteilt = themen_tiefe(kante.get("a_themen"), kante.get("b_themen"))
        if geteilt:
            schicht_tiefen[SCHICHT_THEMEN] = t_tiefe
    if SCHICHT_TIMELINE in gruende and kante.get("timeline_naehe_tage") is not None:
        praezision = kante.get("a_praezision")
        toleranz = TIMELINE_TOLERANZ_TAGE.get(praezision)
        if toleranz:
            distanz = kante["timeline_naehe_tage"]
            schicht_tiefen[SCHICHT_TIMELINE] = max(0.0, (toleranz - distanz) / toleranz)

    return schicht_tiefen
