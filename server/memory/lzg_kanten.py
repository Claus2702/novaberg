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
        logger.exception(
            "%s: kanten_fuer_neuen_knoten_bilden fehlgeschlagen knoten=%s",
            type(exc).__name__, neuer_id,
        )
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
        logger.exception(
            "%s: kanten_neuberechnen_fuer_knoten fehlgeschlagen knoten=%s",
            type(exc).__name__, knoten_id,
        )
        return 0
    finally:
        conn.close()


def embedding_cosine_alle_aktualisieren(postgres_url: str) -> int:
    """
    Frischt embedding_cosine_initial ALLER Kanten aus den aktuellen
    Knoten-Embeddings auf und berechnet danach die Kanten-Gewichte neu
    (Re-Embedding-Pfad, EMBEDDING-CASING-BLIND Phase 2, Chat 107).

    Hintergrund: kanten_neuberechnen_fuer_knoten (Trigger 2) nutzt die
    EINGEFRORENE Initial-Cosine — nach einem Re-Embedding der Knoten
    waeren das Alt-Werte aus einem fremden Vektorraum. Diese Funktion
    setzt die Cosine per Set-UPDATE aus den frischen Embeddings neu
    (1 - (a.embedding <=> b.embedding)) und ruft anschliessend fuer
    jeden beteiligten Knoten den bestehenden Gewichts-Baustein auf.
    Kein Struktureingriff: verbindungs_gruende bleiben; faellt eine neue
    Cosine unter LZG_EMBEDDING_SCHWELLWERT, liefert embedding_tiefe 0.0
    und die Kante verliert nur Gewicht.

    Vorbedingung: lzg_knoten.embedding traegt bereits die NEUEN Vektoren.
    Nachbedingung: jede Kante mit gesetzter Initial-Cosine und zwei
    bebilderten Endknoten traegt den frischen Wert; Gewichte neu.
    Fehlerfaelle: DB-Fehler -> logger.error, Rueckgabe 0 (nichts halb).

    Liefert die Anzahl aufgefrischter Kanten.
    """

    # ── Eingabe-Validierung / Verarbeitung Teil 1: Cosine-Refresh ──────
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE lzg_kanten k
                SET embedding_cosine_initial = 1 - (a.embedding <=> b.embedding)
                FROM lzg_knoten a, lzg_knoten b
                WHERE a.id = k.knoten_a_id
                  AND b.id = k.knoten_b_id
                  AND k.embedding_cosine_initial IS NOT NULL
                  AND a.embedding IS NOT NULL
                  AND b.embedding IS NOT NULL
                """
            )
            aufgefrischt: int = cur.rowcount

            # Beteiligte Knoten fuer den Gewichts-Neuaufbau einsammeln.
            cur.execute(
                "SELECT DISTINCT knoten_a_id FROM lzg_kanten "
                "UNION SELECT DISTINCT knoten_b_id FROM lzg_kanten"
            )
            knoten_ids: list[int] = [row[0] for row in cur.fetchall()]
        conn.commit()
    except psycopg2.Error as exc:
        conn.rollback()
        logger.exception(
            "%s: embedding_cosine_alle_aktualisieren fehlgeschlagen",
            type(exc).__name__,
        )
        return 0
    finally:
        conn.close()

    # ── Verarbeitung Teil 2: Gewichte ueber den bestehenden Baustein ───
    # Pro Knoten werden alle anliegenden Kanten neu berechnet; Kanten
    # zwischen zwei Knoten laufen dabei zweimal — idempotent, kein Schaden.
    gewichte_gesamt: int = 0
    for knoten_id in knoten_ids:
        gewichte_gesamt += kanten_neuberechnen_fuer_knoten(postgres_url, knoten_id)

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        "Kanten-Cosine-Refresh: %d Kanten aufgefrischt, %d Gewichts-Neuberechnungen ueber %d Knoten",
        aufgefrischt, gewichte_gesamt, len(knoten_ids),
    )
    if aufgefrischt == 0 and knoten_ids:
        logger.error(
            "Kanten-Cosine-Refresh: 0 Kanten aufgefrischt trotz %d beteiligter Knoten — "
            "Initial-Cosines fehlen oder Knoten ohne Embedding?",
            len(knoten_ids),
        )
    return aufgefrischt


def kanten_alle_loeschen(postgres_url: str) -> int:
    """
    Loescht ALLE Kanten (Migrations-Reset, Chat 107). Gefahrlos belegt:
    Kanten referenzieren nur Knoten (ON DELETE CASCADE dort), nichts
    referenziert lzg_kanten. Nach dem Loeschen entstehen Kanten fuer
    Bestandsknoten NICHT von selbst (Trigger 1 laeuft nur beim Anlegen) —
    kanten_alle_neu_aufbauen ist der Gegenpart.

    Liefert die Anzahl geloeschter Kanten; -1 bei DB-Fehler.
    """

    # ── Verarbeitung ────────────────────────────
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM lzg_kanten")
            geloescht: int = cur.rowcount
        conn.commit()
    except psycopg2.Error as exc:
        conn.rollback()
        logger.exception("%s: kanten_alle_loeschen fehlgeschlagen", type(exc).__name__)
        return -1
    finally:
        conn.close()

    # ── Ausgabe ─────────────────────────────────
    logger.info("Kanten-Reset: %d Kanten geloescht", geloescht)
    return geloescht


def kanten_alle_neu_aufbauen(postgres_url: str) -> dict:
    """
    Baut das Kantennetz fuer den Bestand neu auf (Migrations-Rebuild,
    Chat 107) — chronologisch ueber kzg_erstellt_am, exakt wie der Bestand
    entstanden waere: pro Knoten werden nur FRUEHERE Knoten als Kandidaten
    betrachtet (Migrationstool-Semantik), Kandidaten kommen aus der echten
    kandidaten_mit_cosine_laden, die Kantenbildung aus dem echten Trigger 1
    (kanten_fuer_neuen_knoten_bilden). Keine nachgebaute Formel.

    ⚠ Reihenfolge zwingend (kein Stil): kanten_staerke_berechnen liest
    gewicht_absolut — ein Rebuild VOR dem Gewichts-Reset wuerde die
    Zufallsgewichte in die Kantenstaerken einfrieren. Ebenso muessen die
    Embeddings frisch sein (Cosine der Embedding-Schicht). Also:
    Re-Embedding -> Reset -> Rebuild.

    Nur aktive Knoten — deckungsgleich mit dem Live-Anlegen (Kandidaten
    sind dort ebenfalls nur aktive). Liefert {knoten, paare, error}.
    """

    # ── Eingabe-Validierung: Bestand chronologisch laden ───────────────
    ergebnis: dict = {"knoten": 0, "paare": 0, "error": None}
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT k.id, k.user_id, k.character_id, k.gewicht_absolut,
                       k.entitaet_ids, k.themen, k.timeline_id, k.kzg_erstellt_am,
                       k.embedding::text AS embedding_str,
                       t.event_time AS timeline_event_time,
                       t.precision  AS timeline_praezision
                FROM lzg_knoten k
                LEFT JOIN timeline t ON t.id = k.timeline_id
                WHERE k.aktiv = TRUE AND k.embedding IS NOT NULL
                ORDER BY k.kzg_erstellt_am, k.id
                """
            )
            knoten = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    ergebnis["knoten"] = len(knoten)
    if not knoten:
        logger.error("Kanten-Rebuild: keine aktiven Knoten mit Embedding — nichts aufzubauen")
        ergebnis["error"] = "kein_bestand"
        return ergebnis

    # ── Verarbeitung: Trigger 1 pro Knoten, nur fruehere Kandidaten ────
    from memory.lzg_knoten import kandidaten_mit_cosine_laden  # zyklusfrei: lokaler Import

    for i, k in enumerate(knoten, start=1):
        kandidaten = kandidaten_mit_cosine_laden(
            postgres_url, k["user_id"], k["character_id"], k["embedding_str"],
        )
        fruehere_ids: set[int] = {
            f["id"] for f in knoten[: i - 1]
            if f["user_id"] == k["user_id"] and f["character_id"] == k["character_id"]
        }
        kandidaten = [c for c in kandidaten if c["id"] in fruehere_ids]
        if kandidaten:
            ergebnis["paare"] += kanten_fuer_neuen_knoten_bilden(postgres_url, k, kandidaten)
        if i % 25 == 0:
            logger.info("Kanten-Rebuild: %d/%d Knoten verarbeitet, %d Paare", i, len(knoten), ergebnis["paare"])

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        "Kanten-Rebuild abgeschlossen: %d Knoten, %d Kanten-Paare gebildet",
        ergebnis["knoten"], ergebnis["paare"],
    )
    if ergebnis["paare"] == 0:
        logger.error(
            "Kanten-Rebuild: 0 Paare bei %d Knoten — greift keine Schicht? "
            "Gewichte/Embeddings pruefen (Reihenfolge Re-Embedding -> Reset -> Rebuild eingehalten?)",
            ergebnis["knoten"],
        )
    return ergebnis


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
