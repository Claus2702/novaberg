"""
GV4: das Gewicht eines Lueckenkandidaten auf einer Skala, gleich aus welcher Quelle.

Die Lueckensuche fuehrt zwei Quellen in **ein** Relevanzprodukt: Kandidaten aus
dem Langzeitgedaechtnis tragen `gewicht_decay` (im Bestand 3 bis 10), Kandidaten
aus dem Kurzzeitgedaechtnis ihre `salienz` (0 bis 1). Roh multipliziert gewinnt
das LZG allein durch seine Skala: `[gemessen 12.09.2026]` 77 von 83 Luecken im
Prompt kamen aus dem LZG, bei 8 bis 10 KZG-Kandidaten in jedem Turn.

**Die Abbildung ist der Rang in der eigenen Quelle** — der Anteil der Eintraege
desselben Paares und derselben Quelle, deren Gewicht nicht groesser ist. Damit
steht an der Naht fuer beide dieselbe Skala [0, 1], gemessen statt angenommen,
ordnungserhaltend und ohne Kappung.

Warum der Rang und nicht eine lineare Form: Vorher gerechnet ueber die elf
Nutzerturns desselben Abends gegen den Bestand. Teilen durch die Obergrenze
kehrte die Schieflage nur um (3 LZG gegen 59 KZG), Min-Max ebenso (4 gegen 48)
— die KZG-Salienz liegt mit Median 0,97 fast am oberen Rand, das LZG-Gewicht
mit Median 3,89 nahe am unteren. Nur der Rang mischte (22 gegen 18).

Die Verteilung wird je Paar geladen und fuer `GV_GEWICHT_VERTEILUNG_TTL_S`
zwischengehalten: Sie wandert mit dem Bestand, aber nicht von Turn zu Turn.
"""

import bisect
import logging
import math
import threading
import time
from collections.abc import Sequence

from config import GV_GEWICHT_VERTEILUNG_TTL_S, redis_client
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.ei.source_weights")

SOURCES: tuple[str, ...] = ("lzg", "kzg")

# Seitengroesse der KZG-Abfrage. RediSearch liefert ohne LIMIT nur zehn Treffer.
_KZG_PAGE: int = 1000

_cache: dict[tuple[str, str], tuple[float, dict[str, list[float]]]] = {}
_cache_lock = threading.Lock()


def weight_rank(value: float, distribution: Sequence[float]) -> float:
    """Der Rang eines Gewichts in seiner Verteilung, als Anteil in [0, 1].

    Vorbedingung: `distribution` ist nicht leer, aufsteigend sortiert und traegt
        nur endliche Zahlen — der Lader stellt das her.
    Nachbedingung: Anteil der Eintraege mit Gewicht <= `value`, also in [0, 1].
        Gleiche Gewichte bekommen denselben Rang; ein Wert ueber dem Maximum
        (ein Eintrag, der nach dem Laden entstand) bekommt 1,0, einer unter dem
        Minimum 0,0. Die Abbildung ist monoton: groesseres Gewicht, nie
        kleinerer Rang.
    Fehlerfaelle: `ValueError` bei leerer Verteilung und bei einem Wert, der
        keine endliche Zahl ist — ein `bool` zaehlt nicht als Zahl.

    Args:
        value: das rohe Gewicht des Kandidaten.
        distribution: alle Gewichte derselben Quelle des Paares, sortiert.

    Returns:
        Der Rang in [0, 1].

    Raises:
        ValueError: bei leerer Verteilung oder ungueltigem Wert.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not distribution:
        raise ValueError("weight_rank: leere Verteilung — es gibt keinen Rang")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"weight_rank: Gewicht {value!r} ist keine endliche Zahl")

    # ── Verarbeitung ────────────────────────────
    rank: float = bisect.bisect_right(distribution, value) / len(distribution)

    # ── Ausgabe-Verifikation ────────────────────
    # Spanne laut Nachbedingung: 0 bis 1. Durch Konstruktion eingehalten; ein
    # Wert ausserhalb waere ein Defekt dieser Zeile, nicht eine Randbedingung.
    if not 0.0 <= rank <= 1.0:
        raise ValueError(f"weight_rank: Rang {rank} ausserhalb [0, 1]")
    return rank


def _load_lzg(user_id: str, character_id: str) -> list[float]:
    """Alle `gewicht_decay` der aktiven LZG-Knoten des Paares, sortiert.

    Vorbedingung: Paar vollstaendig (prueft der Aufrufer).
    Nachbedingung: sortierte Liste endlicher Zahlen; leer, wenn das Paar keine
        aktiven Knoten hat. Eine Zeile mit nicht endlichem Gewicht wird laut
        verworfen, nicht mitgezaehlt.
    Fehlerfaelle: Datenbankfehler werden nicht gefangen — der Aufrufer
        entscheidet, was ein Turn ohne Verteilung tut.
    """
    zeilen: list[dict] = db_manager.select(
        "SELECT gewicht_decay FROM lzg_knoten "
        "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE",
        (user_id, character_id),
    )
    werte: list[float] = []
    verworfen: int = 0
    for zeile in zeilen:
        wert = zeile.get("gewicht_decay")
        if isinstance(wert, (int, float)) and not isinstance(wert, bool) and math.isfinite(wert):
            werte.append(float(wert))
        else:
            verworfen += 1
    if verworfen:
        logger.error(
            "Gewichtsverteilung LZG %s/%s: %d von %d Knoten ohne endliches "
            "gewicht_decay — nicht mitgezaehlt", user_id, character_id,
            verworfen, len(zeilen),
        )
    werte.sort()
    return werte


def _load_kzg(user_id: str, character_id: str) -> list[float]:
    """Alle `salienz` der KZG-Eintraege des Paares, sortiert.

    Vorbedingung: Paar vollstaendig (prueft der Aufrufer).
    Nachbedingung: sortierte Liste endlicher Zahlen; leer, wenn das Paar keine
        Eintraege hat. Ein Eintrag ohne lesbare Salienz wird laut verworfen.
    Fehlerfaelle: Redis-Fehler werden nicht gefangen.
    """
    abfrage: str = f"@user_id:{{{user_id}}} @character_id:{{{character_id}}}"
    werte: list[float] = []
    verworfen: int = 0
    offset: int = 0
    while True:
        ergebnis = redis_client.execute_command(
            "FT.SEARCH", "idx:kzg", abfrage,
            "RETURN", "1", "salienz",
            "LIMIT", str(offset), str(_KZG_PAGE),
            "DIALECT", "2",
        )
        gesamt: int = int(ergebnis[0])
        treffer: list = ergebnis[1:]
        for i in range(1, len(treffer), 2):
            felder = treffer[i]
            roh = dict(zip(felder[::2], felder[1::2], strict=True)).get("salienz")
            try:
                wert = float(roh)
            except (TypeError, ValueError):
                verworfen += 1
                continue
            if math.isfinite(wert):
                werte.append(wert)
            else:
                verworfen += 1
        offset += _KZG_PAGE
        if offset >= gesamt:
            break
    if verworfen:
        logger.error(
            "Gewichtsverteilung KZG %s/%s: %d Eintraege ohne lesbare salienz — "
            "nicht mitgezaehlt", user_id, character_id, verworfen,
        )
    werte.sort()
    return werte


def load_weight_distributions(
    user_id: str, character_id: str, *, refresh: bool = False,
) -> dict[str, list[float]]:
    """Die Gewichtsverteilungen beider Quellen fuer ein Paar, zwischengehalten.

    Vorbedingung: `user_id` und `character_id` sind gesetzt.
    Nachbedingung: ein Dict mit genau den Schluesseln `lzg` und `kzg`, je eine
        sortierte Liste (leer zulaessig). Innerhalb von
        `GV_GEWICHT_VERTEILUNG_TTL_S` kommt dieselbe Liste zurueck, es sei denn
        `refresh` ist gesetzt.
    Fehlerfaelle: `ValueError` bei unvollstaendigem Paar; Datenbank- und
        Redis-Fehler laufen durch.

    Args:
        user_id: der Mensch des Paares.
        character_id: die Figur des Paares.
        refresh: den Zwischenspeicher fuer dieses Paar uebergehen.

    Returns:
        `{"lzg": [...], "kzg": [...]}`.

    Raises:
        ValueError: bei unvollstaendigem Paar.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        raise ValueError(
            f"load_weight_distributions: Paar unvollstaendig "
            f"(user_id={user_id!r}, character_id={character_id!r})"
        )

    # ── Verarbeitung ────────────────────────────
    schluessel: tuple[str, str] = (user_id, character_id)
    jetzt: float = time.monotonic()
    with _cache_lock:
        eintrag = _cache.get(schluessel)
        if eintrag and not refresh and jetzt - eintrag[0] < GV_GEWICHT_VERTEILUNG_TTL_S:
            return eintrag[1]

    verteilungen: dict[str, list[float]] = {
        "lzg": _load_lzg(user_id, character_id),
        "kzg": _load_kzg(user_id, character_id),
    }

    # ── Ausgabe-Verifikation ────────────────────
    for quelle, werte in verteilungen.items():
        if any(b < a for a, b in zip(werte, werte[1:], strict=False)):
            raise ValueError(f"load_weight_distributions: {quelle} nicht sortiert")

    with _cache_lock:
        _cache[schluessel] = (jetzt, verteilungen)
    logger.info(
        "Gewichtsverteilung %s/%s geladen: LZG %d, KZG %d",
        user_id, character_id, len(verteilungen["lzg"]), len(verteilungen["kzg"]),
    )
    return verteilungen
