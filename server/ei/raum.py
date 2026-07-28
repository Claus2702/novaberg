"""Raumzug: Novas Register folgt dem des Nutzers.

Es gibt genau einen Raum, und es ist Novas. Was die Perzeption am Nutzer misst,
ist eine Schaetzung seines Raums — sie darf springen, weil sie eine Messung ist
und kein Zustand. Novas Raum springt nicht: Er wird gezogen, und ein Wechsel
dauert ein bis drei Turns.

Dieselbe Bauart wie die Empathie-Injektion der Emotion (`ei/berechnung.py`),
mit einem entscheidenden Unterschied im Vorzeichen: Bei der Emotion zieht ein
weit entfernter Nutzer STAERKER — das ist Empathie. Beim Register ist es die
Umstellung, die kostet, und hinauf (System 1 → System 2) kostet mehr als hinab.

Konzept: novaberg-gv-strategie_k.md §3.1 (die Achsen), Chat 114 (der Zug).
"""

import logging

from config import (
    GV_NAEHE_DYNAMIK,
    GV_NAEHE_STIL,
    GV_RAUM_ANKUNFT,
    GV_RAUM_CHARAKTER_FAKTOR,
    GV_RAUM_ZUG_HINAB,
    GV_RAUM_ZUG_HINAUF,
    GV_TIEFE_MODUS,
)
from ei.utils import modus_pruefen

logger = logging.getLogger("ki_server.ei.raum")


def raum_ziehen(
    aktuell:          float,
    ziel:             float,
    charakter_faktor: float = GV_RAUM_CHARAKTER_FAKTOR,
) -> float:
    """Zieht einen Achsenwert um einen Anteil des Abstands zum Ziel.

    Der Anteil haengt von der Richtung ab: hinauf langsamer als hinab. Der
    Charakterfaktor multipliziert ihn — eine anpassungsbereite Nova folgt
    schneller als eine widerspenstige.

    Vorbedingung: `aktuell` und `ziel` liegen in [0, 1]; `charakter_faktor`
    ist positiv.
    Nachbedingung: Rueckgabe liegt zwischen `aktuell` und `ziel` (nie
    darueber hinaus) und ist auf zwei Stellen gerundet — die Achsen-Tore
    vergleichen mit `>=`, und ein Wert, der die Schwelle nur in der
    Fliesskomma-Nachkommastelle verfehlt, waere ein Zufallsgenerator.
    Fehlerfaelle: Keine; ein negativer oder Null-Faktor haelt den Raum fest,
    was ein gueltiger Zustand ist (vollstaendig widerspenstig).

    Returns:
        Der neue Achsenwert.
    """

    # ── Eingabe-Validierung ─────────────────────
    if aktuell == ziel:
        return aktuell

    # ── Verarbeitung ────────────────────────────
    hinauf: bool  = ziel > aktuell
    zug:    float = GV_RAUM_ZUG_HINAUF if hinauf else GV_RAUM_ZUG_HINAB
    anteil: float = min(1.0, max(0.0, zug * charakter_faktor))

    neu: float = round(aktuell + anteil * (ziel - aktuell), 2)

    # Ankunft: Ein proportionaler Zug erreicht sein Ziel nie. Liegt das Ziel
    # exakt auf einer Achsen-Schwelle, waere es sonst von einer Seite
    # unerreichbar — in der Simulation gemessen fuer `kreativ` (0.5).
    if abs(ziel - neu) < GV_RAUM_ANKUNFT:
        neu = ziel

    # ── Ausgabe-Verifikation ────────────────────
    if hinauf and neu > ziel:
        neu = ziel
    elif not hinauf and neu < ziel:
        neu = ziel

    return neu


def raum_ziel_bestimmen(personality, quelle: str = "Nutzer") -> tuple[float, float]:
    """Rechnet das Register einer Aeusserung auf die beiden Achsen um.

    Funktioniert fuer beide Akteure: Bei einem Nutzer-Turn ist die Quelle
    `external` (die Schaetzung seines Raums), bei einem Eigen-Impuls
    `internal` (Novas letzte eigene Aeusserung). Der Raum folgt dem, der
    zuletzt gesprochen hat.

    Vorbedingung: `personality` traegt eine Emotion mit Registerfeldern.
    Nachbedingung: (tiefe, naehe), beide in [0, 1].
    Fehlerfaelle: Fehlende Personality — laut protokolliert, Cold-Start-Werte.
    Ein Modus ausserhalb des Kanons wird von `modus_pruefen` benannt; die
    Tabelle nimmt dann ihren Default.

    Returns:
        (tiefe_ziel, naehe_ziel)
    """

    # ── Eingabe-Validierung ─────────────────────
    if personality is None:
        logger.error(
            "Raumzug: keine Perzeption (%s) im State — der Raum bleibt "
            "stehen, wo er ist", quelle,
        )
        return 0.3, 0.5

    # ── Verarbeitung ────────────────────────────
    modus:   str = personality.emotion.mode
    dynamik: str = personality.emotion.relationship_dynamic
    stil:    str = personality.emotion.language_style

    modus_pruefen(modus, f"Raumzug-Ziel ({quelle})")

    tiefe_ziel: float = GV_TIEFE_MODUS.get(modus, 0.3)
    naehe_ziel: float = (
        GV_NAEHE_DYNAMIK.get(dynamik, 0.5) + GV_NAEHE_STIL.get(stil, 0.5)
    ) / 2.0

    # ── Ausgabe ─────────────────────────────────
    return round(tiefe_ziel, 2), round(naehe_ziel, 2)


def raum_nachfuehren(
    internal,
    quelle_personality,
    quelle:           str = "Nutzer",
    charakter_faktor: float = GV_RAUM_CHARAKTER_FAKTOR,
) -> bool:
    """Zieht Novas Raum einen Schritt zu dem, der zuletzt gesprochen hat.

    Bei einem Nutzer-Turn ist `quelle_personality` das `external` dieses Turns
    und der Charakterfaktor greift — er beschreibt Novas Bereitschaft, IHM zu
    folgen. Bei einem Eigen-Impuls ist die Quelle Novas eigene letzte
    Aeusserung, und der Faktor bleibt 1.0: Gegen sich selbst straeubt sie sich
    nicht.

    Vorbedingung: `internal` traegt einen Raum (aus db_zugriff oder dem
    Cold-Start-Default).
    Nachbedingung: `internal.raum` liegt naeher am Ziel als vorher oder ist
    dort angekommen. Die Bewegung steht benannt im Log — Ausgangswert, Ziel
    und Ergebnis, denn eine Zahl, die sich still bewegt, ist nicht pruefbar.
    Fehlerfaelle: Fehlendes `internal` — laut protokolliert, keine Bewegung.

    Returns:
        True, wenn sich mindestens eine Achse bewegt hat.
    """

    # ── Eingabe-Validierung ─────────────────────
    if internal is None:
        logger.error("Raumzug: kein internal im State — Novas Raum bleibt stehen")
        return False

    # ── Verarbeitung ────────────────────────────
    tiefe_ziel, naehe_ziel = raum_ziel_bestimmen(quelle_personality, quelle)

    tiefe_alt: float = internal.raum.tiefe
    naehe_alt: float = internal.raum.naehe

    internal.raum.tiefe = raum_ziehen(tiefe_alt, tiefe_ziel, charakter_faktor)
    internal.raum.naehe = raum_ziehen(naehe_alt, naehe_ziel, charakter_faktor)

    bewegt: bool = (
        internal.raum.tiefe != tiefe_alt or internal.raum.naehe != naehe_alt
    )

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        "Raumzug (%s): Tiefe %.2f → %.2f (Ziel %.2f) · Naehe %.2f → %.2f "
        "(Ziel %.2f) · Faktor %.2f%s",
        quelle,
        tiefe_alt, internal.raum.tiefe, tiefe_ziel,
        naehe_alt, internal.raum.naehe, naehe_ziel,
        charakter_faktor,
        "" if bewegt else " · angekommen, keine Bewegung",
    )
    return bewegt
