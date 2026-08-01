"""Messreihe der Charakter-Raeder — akuter Zustand, ueber Tage stabilisiert.

Das Rad speicherte bis zum 01.08.2026 ausschliesslich sein Ergebnis: einen
einzigen Zug, beim naechsten Lauf ueberschrieben. Ob eine Aenderung Bewegung
oder Rauschen war, liess sich aus den Daten nicht beantworten — die vorige
Erhebung existierte nicht mehr.

Dieses Modul haelt die rohen Messungen und rechnet daraus den gelesenen Wert.
Die Richtung ist die der Konvention ueber abgeleitete Werte, Regel (1): **Die
Messreihe ist die Eingabe, das Rad ist ihr Ergebnis.**

Konzept: novaberg-charakter-rad-messreihe_k.md

Aufteilung nach der Schichtregel:

    gewichte()             reine Funktion, kein Datenzugriff
    rad_zusammenfassen()   reine Funktion, kein Datenzugriff
    messung_faellig()      liest
    messung_ablegen()      schreibt
    reihe_laden()          liest

**In diese Tabelle wird nie ein Mittelwert geschrieben.** Nur rohe Laeufe —
sonst mittelt jeder Lauf ueber Werte, die selbst schon Mittel waren, und nach
wenigen Laeufen ist nicht mehr rekonstruierbar, was je gemessen wurde
(Konvention Regel 2, derselbe Fehler wie beim Ziel-Decay).
"""

import hashlib
import json
import logging
import math
import uuid
from dataclasses import dataclass

from config import (
    RAD_DECAY_BASE,
    RAD_DECAY_FACTOR,
    RAD_HISTORIEN_GEWICHT,
    RAD_MESSREIHE_FENSTER,
    RAD_MESSUNG_ABSTAND_STUNDEN,
)
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.charakter.messreihe")

# Die beiden Raeder, die in derselben Tabelle liegen. Als Konstante, damit ein
# Tippfehler nicht als leere Reihe erscheint — eine unbekannte Radart liefert
# sonst null Zeilen und sieht aus wie "noch nie gemessen".
RAD_ART_ZUWENDUNG: str = "zuwendung"
RAD_ART_INITIATIVE: str = "initiative"
RAD_ARTEN: tuple[str, ...] = (RAD_ART_ZUWENDUNG, RAD_ART_INITIATIVE)


def gewichte(anzahl: int) -> list[float]:
    """Gewicht je Rang, 0 = juengste Messung.

    Dieselbe Kurve wie der Emotions-Verlauf ueber Turns: Die juengste Messung
    zaehlt voll, aeltere verfallen logarithmisch und werden zusaetzlich auf
    RAD_HISTORIEN_GEWICHT gestaucht. Die Kurve allein ist flach — Rang 9 traegt
    noch 0.56 —, erst die Stauchung macht daraus "aktuell praegt".

    Args:
        anzahl: Zahl der vorliegenden Messungen, >= 1.

    Returns:
        Liste der Gewichte, absteigend nach Aktualitaet. Leer bei `anzahl` < 1.

    Nachbedingung: Das erste Gewicht ist 1.0, alle weiteren sind kleiner.
    """
    # ── Eingabe-Validierung ─────────────────────
    if anzahl < 1:
        logger.error(
            f"Rad-Messreihe: gewichte({anzahl}) — es gibt keine Reihe ohne "
            "Messung, leere Liste"
        )
        return []

    # ── Verarbeitung ────────────────────────────
    ergebnis: list[float] = []
    for rang in range(anzahl):
        verfall: float = 1.0 / (
            1.0 + RAD_DECAY_FACTOR * math.log(1.0 + rang, RAD_DECAY_BASE)
        )
        ergebnis.append(verfall if rang == 0 else verfall * RAD_HISTORIEN_GEWICHT)

    return ergebnis


def rad_zusammenfassen(reihe: list[dict[str, float]]) -> dict[str, float] | None:
    """Fasst die Messungen einer Reihe zu einem Rad zusammen.

    Gewichtetes arithmetisches Mittel je Speiche, juengste Messung zuerst.

    **Das Ergebnis liegt bewusst nicht mehr auf der Dreierskala** der Messung
    (0.0 / 0.5 / 1.0). Die Stufung ist eine Eigenschaft des Messgeraets — das
    Modell kann nur diese drei Werte vergeben —, nicht der Groesse. Ein Mittel
    ueber grobe Urteile darf feiner sein als ein einzelnes; beide Verbraucher
    (Faktor und Haltungsraum) rechnen auf [0.0, 1.0] und nicht auf Stufen.

    Args:
        reihe: Messungen, juengste zuerst, je ein Abbild Speichenname -> Wert.

    Returns:
        Ein Rad mit denselben Speichennamen, oder None bei leerer Reihe oder
        uneinheitlichen Speichennamen.

    Fehlerfaelle: leere Reihe, abweichende Speichenmenge zwischen Messungen —
        je `logger.error` und None. Eine Messung mit anderen Namen ist keine
        Messung derselben Groesse, und ein Mittel darueber waere eine Zahl ohne
        Gegenstand.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not reihe:
        logger.error("Rad-Messreihe: leere Reihe — kein Rad zusammenzufassen")
        return None

    namen: set[str] = set(reihe[0])
    if not namen:
        logger.error("Rad-Messreihe: erste Messung traegt keine Speiche — verworfen")
        return None

    for nummer, messung in enumerate(reihe[1:], start=2):
        if set(messung) != namen:
            logger.error(
                f"Rad-Messreihe: Messung {nummer} traegt {sorted(set(messung))} "
                f"statt {sorted(namen)} — die Reihe misst nicht dieselbe "
                "Groesse, verworfen"
            )
            return None

    # ── Verarbeitung ────────────────────────────
    gewicht: list[float] = gewichte(len(reihe))
    summe:   float       = sum(gewicht)

    rad: dict[str, float] = {}
    for name in namen:
        # `strict=True` ist hier nicht Formsache: Sind Reihe und Gewichte
        # verschieden lang, kuerzt `zip` stillschweigend — und ein Mittel ueber
        # weniger Messungen als geladen sieht aus wie ein gueltiges Ergebnis.
        rad[name] = sum(
            float(messung[name]) * g
            for messung, g in zip(reihe, gewicht, strict=True)
        ) / summe

    # ── Ausgabe-Verifikation ────────────────────
    # Ein gewichtetes Mittel von Werten aus [0, 1] liegt in [0, 1]. Liegt es
    # daneben, ist eine Eingabe ausserhalb ihres Bereichs gewesen — und die
    # faellt sonst erst beim Verbraucher auf, zwei Schichten spaeter.
    ausreisser: list[str] = [n for n, w in rad.items() if not (0.0 <= w <= 1.0)]
    if ausreisser:
        logger.error(
            f"Rad-Messreihe: Ergebnis verlaesst [0.0, 1.0] bei {sorted(ausreisser)} "
            f"— eine Messung lag ausserhalb ihres Wertebereichs, verworfen"
        )
        return None

    return rad


def messung_faellig(user_id: str, character_id: str, rad_art: str) -> bool:
    """Sagt, ob seit der letzten Messung genug Zeit vergangen ist.

    Der Takt ist fest (RAD_MESSUNG_ABSTAND_STUNDEN), damit Rang und Zeit
    dasselbe bedeuten: Die Gewichtskurve verfaellt ueber den Rang.

    Args:
        user_id:      Subjekt des kanonischen Paares.
        character_id: Gegenueber.
        rad_art:      aus RAD_ARTEN.

    Returns:
        True, wenn gemessen werden soll. **Bei einem Lesefehler ebenfalls
        True** — eine zusaetzliche Messung kostet einen Modellaufruf, eine
        ausgefallene reisst eine Luecke in die Reihe.

    Fehlerfaelle: unbekannte Radart — `logger.error` und False, weil sonst bei
        jedem Lauf gemessen wuerde, ohne dass die Reihe je gefunden wird.
    """
    # ── Eingabe-Validierung ─────────────────────
    if rad_art not in RAD_ARTEN:
        logger.error(
            f"Rad-Messreihe: unbekannte Radart {rad_art!r} — bekannt sind "
            f"{RAD_ARTEN}, nicht gemessen"
        )
        return False

    # ── Verarbeitung ────────────────────────────
    try:
        zeile: dict | None = db_manager.select_one(
            """
            SELECT gemessen_am,
                   EXTRACT(EPOCH FROM (now() - gemessen_am)) / 3600.0 AS stunden_her
            FROM charakter_rad_messung
            WHERE user_id = %s AND character_id = %s AND rad_art = %s
            ORDER BY gemessen_am DESC
            LIMIT 1
            """,
            (user_id, character_id, rad_art),
        )
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Rad-Messreihe: letzte Messung fuer "
            f"{user_id}/{character_id} nicht lesbar — es wird gemessen, damit "
            "die Reihe keine Luecke bekommt"
        )
        return True

    if zeile is None:
        logger.info(
            f"Rad-Messreihe: noch keine Messung fuer {user_id}/{character_id} "
            f"({rad_art}) — erste Erhebung"
        )
        return True

    stunden: float = float(zeile["stunden_her"])
    faellig: bool  = stunden >= RAD_MESSUNG_ABSTAND_STUNDEN

    logger.info(
        f"Rad-Messreihe: letzte Messung {rad_art} fuer {user_id}/{character_id} "
        f"liegt {stunden:.1f} h zurueck, Takt {RAD_MESSUNG_ABSTAND_STUNDEN} h — "
        f"{'faellig' if faellig else 'uebersprungen'}"
    )
    return faellig


@dataclass(frozen=True)
class Messung:
    """Eine einzelne Erhebung eines Rades — was gemessen wurde und womit.

    Reiner Datencontainer. Die Felder stammen aus einem Aufruf und werden
    zusammen weitergereicht; einzeln ergibt keines von ihnen Sinn.

    Attributes:
        user_id:      Subjekt des kanonischen Paares.
        character_id: Gegenueber.
        rad_art:      aus RAD_ARTEN — 'zuwendung' oder 'initiative'.
        speichen:     Speichenname -> Auspraegung, roh wie geliefert. Auf der
                      Dreierskala 0.0 / 0.5 / 1.0, weil das Modell nur diese
                      drei Werte vergeben kann.
        faktor:       der Skalar dieses einen Laufs. Zusaetzlich, nicht
                      stattdessen — aus `speichen` nachrechenbar.
        modell:       Modellname, mit dem gemessen wurde.
        temperatur:   Temperatur des Aufrufs.
        quelle:       der Profiltext, aus dem gelesen wurde. Gespeichert werden
                      nur Pruefsumme und Laenge, nie der Text.
        erhebung_id:  klammert die Laeufe einer Erhebung; leer erzeugt eine neue.
        lauf:         Nummer innerhalb der Erhebung, >= 1.
    """

    user_id:      str
    character_id: str
    rad_art:      str
    speichen:     dict[str, float]
    faktor:       float
    modell:       str
    temperatur:   float
    quelle:       str
    erhebung_id:  str = ""
    lauf:         int = 1


def messung_ablegen(messung: Messung) -> bool:
    """Legt eine rohe Messung ab.

    Returns:
        True bei Erfolg.

    Fehlerfaelle: unbekannte Radart, leere Speichen, Schreibfehler — je
        `logger.error` und False. Der Aufrufer arbeitet weiter: Eine fehlende
        Zeile kostet die Reihe einen Punkt, ein Abbruch kostet den Charakter.
    """
    # ── Eingabe-Validierung ─────────────────────
    if messung.rad_art not in RAD_ARTEN:
        logger.error(
            f"Rad-Messreihe: unbekannte Radart {messung.rad_art!r} — nicht abgelegt"
        )
        return False

    if not messung.speichen:
        logger.error(
            f"Rad-Messreihe: leeres Rad fuer {messung.user_id}/"
            f"{messung.character_id} — nicht abgelegt, eine Messung ohne "
            "Speichen ist keine"
        )
        return False

    # Die Pruefsumme beantwortet spaeter die teuerste Frage dieser Reihe:
    # Gleiche Quelle mit anderem Ergebnis ist Verfahrensstreuung, andere Quelle
    # mit anderem Ergebnis kann Bewegung sein.
    pruefsumme: str = hashlib.md5(
        messung.quelle.encode("utf-8"), usedforsecurity=False,
    ).hexdigest()

    # ── Verarbeitung ────────────────────────────
    try:
        db_manager.execute(
            """
            INSERT INTO charakter_rad_messung
                (user_id, character_id, rad_art, erhebung_id, lauf,
                 speichen, faktor, modell, temperatur,
                 quelle_pruefsumme, quelle_zeichen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                messung.user_id, messung.character_id, messung.rad_art,
                messung.erhebung_id or str(uuid.uuid4()), messung.lauf,
                json.dumps(messung.speichen), messung.faktor,
                messung.modell, messung.temperatur,
                pruefsumme, len(messung.quelle),
            ),
        )
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Rad-Messreihe: Messung fuer "
            f"{messung.user_id}/{messung.character_id} ({messung.rad_art}) "
            "nicht abgelegt — die Reihe hat eine Luecke, der Turn laeuft weiter"
        )
        return False

    logger.info(
        f"Rad-Messreihe: Messung abgelegt — {messung.rad_art} fuer "
        f"{messung.user_id}/{messung.character_id}, Faktor {messung.faktor:.3f}, "
        f"Quelle {len(messung.quelle)} Zeichen ({pruefsumme[:8]})"
    )
    return True


def reihe_laden(
    user_id:      str,
    character_id: str,
    rad_art:      str,
    fenster:      int = RAD_MESSREIHE_FENSTER,
) -> list[dict[str, float]]:
    """Laedt die letzten Messungen eines Rades, juengste zuerst.

    Args:
        fenster: Zahl der Erhebungen, die einfliessen.

    Returns:
        Liste von Speichen-Abbildern, juengste zuerst. Leer, wenn nichts
        vorliegt oder der Zugriff scheitert — der Aufrufer behaelt dann seinen
        Einzelwert, statt mit einer halben Reihe zu rechnen.

    Fehlerfaelle: unbekannte Radart, `fenster` < 1, Lesefehler, unlesbares
        JSON in einer Zeile — je `logger.error` und leere Liste bzw.
        Ueberspringen der Zeile.
    """
    # ── Eingabe-Validierung ─────────────────────
    if rad_art not in RAD_ARTEN:
        logger.error(f"Rad-Messreihe: unbekannte Radart {rad_art!r} — leere Reihe")
        return []

    if fenster < 1:
        logger.error(
            f"Rad-Messreihe: Fenster {fenster} ist kleiner als 1 — leere Reihe"
        )
        return []

    # ── Verarbeitung ────────────────────────────
    # **Das Fenster zaehlt Erhebungen, nicht Zeilen.** Ein Rad mit drei Laeufen
    # je Erhebung fuellte sonst das Fenster mit weniger als zwei Erhebungen, und
    # die Reihe reichte nur noch Stunden zurueck statt Tage — lautlos, weil die
    # Zahl der Messungen unveraendert aussieht.
    try:
        zeilen: list[dict] = db_manager.select(
            """
            SELECT erhebung_id, speichen
            FROM charakter_rad_messung
            WHERE user_id = %s AND character_id = %s AND rad_art = %s
              AND erhebung_id IN (
                  SELECT erhebung_id
                  FROM charakter_rad_messung
                  WHERE user_id = %s AND character_id = %s AND rad_art = %s
                  GROUP BY erhebung_id
                  ORDER BY max(gemessen_am) DESC
                  LIMIT %s
              )
            ORDER BY gemessen_am DESC, id DESC
            """,
            (user_id, character_id, rad_art,
             user_id, character_id, rad_art, fenster),
        )
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Rad-Messreihe: Reihe fuer "
            f"{user_id}/{character_id} ({rad_art}) nicht lesbar — leere Reihe"
        )
        return []

    # Laeufe je Erhebung sammeln, Reihenfolge der Abfrage erhalten.
    nach_erhebung: dict[str, list[dict[str, float]]] = {}
    for nummer, zeile in enumerate(zeilen, start=1):
        rad: dict[str, float] | None = _speichen_lesen(zeile.get("speichen"), nummer)
        if rad is None:
            continue
        nach_erhebung.setdefault(str(zeile["erhebung_id"]), []).append(rad)

    # ── Ausgabe ─────────────────────────────────
    reihe: list[dict[str, float]] = []
    for erhebung_id, laeufe in nach_erhebung.items():
        verdichtet: dict[str, float] | None = (
            laeufe[0] if len(laeufe) == 1 else rad_zusammenfassen_gleichgewichtig(laeufe)
        )
        if verdichtet is None:
            logger.error(
                f"Rad-Messreihe: Erhebung {erhebung_id[:8]} mit {len(laeufe)} "
                "Laeufen nicht verdichtbar — uebersprungen"
            )
            continue
        reihe.append(verdichtet)

    return reihe


def _speichen_lesen(roh: object, nummer: int) -> dict[str, float] | None:
    """Liest das Speichen-Feld einer Zeile.

    psycopg2 liefert `jsonb` bereits als Abbildung; eine Zeichenkette waere ein
    abweichender Schreibweg und wird trotzdem gelesen.

    Returns:
        Speichenname -> Wert, oder None bei unlesbarem Inhalt.
    """
    if isinstance(roh, str):
        try:
            roh = json.loads(roh)
        except (json.JSONDecodeError, TypeError):
            logger.exception(
                f"Rad-Messreihe: Zeile {nummer} traegt unlesbares JSON — uebersprungen"
            )
            return None

    if not isinstance(roh, dict) or not roh:
        logger.error(
            f"Rad-Messreihe: Zeile {nummer} traegt kein Rad "
            f"({type(roh).__name__}) — uebersprungen"
        )
        return None

    return {name: float(wert) for name, wert in roh.items()}


def rad_zusammenfassen_gleichgewichtig(
    laeufe: list[dict[str, float]],
) -> dict[str, float] | None:
    """Verdichtet die Laeufe EINER Erhebung — ohne Verfall, alle gleich alt.

    Innerhalb einer Erhebung gibt es keine Reihenfolge, die etwas bedeutet: Die
    Laeufe liegen Sekunden auseinander und messen denselben Text. Ein Verfall
    ueber ihren Rang waere eine Aussage ueber nichts.

    Dieselbe Rechenart wie ueber die Erhebungen — ein arithmetisches Mittel je
    Speiche —, nur mit gleichen Gewichten.
    """
    if not laeufe:
        logger.error("Rad-Messreihe: Erhebung ohne Lauf — nicht verdichtbar")
        return None

    namen: set[str] = set(laeufe[0])
    for lauf in laeufe[1:]:
        if set(lauf) != namen:
            logger.error(
                f"Rad-Messreihe: Laeufe einer Erhebung tragen verschiedene "
                f"Speichen ({sorted(namen)} gegen {sorted(set(lauf))}) — verworfen"
            )
            return None

    return {
        name: sum(float(lauf[name]) for lauf in laeufe) / len(laeufe)
        for name in namen
    }
