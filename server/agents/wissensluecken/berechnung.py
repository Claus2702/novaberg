"""Wissensluecken — die reinen Rechnungen.

Ohne LLM, ohne Datenbank, ohne Redis. Alles hier ist eine reine Funktion
ueber seinen Eingaben und damit von Hand nachrechenbar
(novaberg-convention-abgeleitete-werte.md).

Konzept: docs/novaberg-wissensluecken_k.md §3
"""

import logging

from config import NOVA_NEUGIER

logger = logging.getLogger("ki_server.agents.wissensluecken")


# Ab dieser Aehnlichkeit gilt ein Kandidat als bereits erfasst. Deutlich
# strenger als LZG_KNOTEN_MATCH_SCHWELLE (0.82): Dort wird gefragt "dieselbe
# Erinnerung?" und dann VERSCHMOLZEN, hier "dasselbe Thema?" und dann
# VERWORFEN. Bei 0.95 kommen "Dunkle Materie" und "Dunkle Materie im fruehen
# Universum" als zwei Luecken durch — verschiedene Tiefen desselben Feldes,
# und das ist gewollt.
LUECKE_DUBLETTE_SCHWELLE: float = 0.95

# Zustaende. Alle drei sperren gleichermassen neue Vorschlaege zum selben
# Thema; sie unterscheiden sich nur darin, WARUM.
STATUS_OFFEN:          str = "offen"
STATUS_GESCHLOSSEN:    str = "geschlossen"
STATUS_AUSGESCHLOSSEN: str = "ausgeschlossen"

STATUS_ALLE: frozenset[str] = frozenset(
    {STATUS_OFFEN, STATUS_GESCHLOSSEN, STATUS_AUSGESCHLOSSEN}
)


def neuheit_berechnen(hoechste_aehnlichkeit: float) -> float:
    """Wie neu ist ein Thema, gemessen an seinem naechsten Nachbarn im Bestand.

    Vorbedingung: `hoechste_aehnlichkeit` ist die groesste Cosine-Similarity
        des Kandidaten zu irgendeinem bekannten Eintrag, in [-1.0, 1.0].
        Ein leerer Bestand liefert 0.0 — dann ist alles maximal neu.
    Nachbedingung: Rueckgabe in [0.0, 1.0].
    Fehlerfaelle: keine. Negative Cosine-Werte (Gegensatz statt Naehe) gelten
        als maximal neu und werden auf 1.0 geklemmt, nicht auf > 1.0.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(hoechste_aehnlichkeit, (int, float)) or isinstance(
        hoechste_aehnlichkeit, bool
    ):
        raise ValueError(
            f"neuheit_berechnen: erwartet Zahl, bekam "
            f"{type(hoechste_aehnlichkeit).__name__}"
        )

    # ── Verarbeitung / Ausgabe ──────────────────
    return max(0.0, min(1.0, 1.0 - float(hoechste_aehnlichkeit)))


def neugier_vektor_berechnen(resonanz: float, neuheit: float) -> float:
    """Der Zug zu einem Thema: NOVA_NEUGIER * resonanz * neuheit.

    Das Produkt ergibt Berlynes umgekehrte U-Kurve, ohne dass sie eigens
    modelliert werden muss: Hohe Resonanz verlangt Naehe zu ihr, hohe Neuheit
    verlangt Ferne zum Bekannten. Beides zugleich geht nur am RAND ihres
    Feldes. Eine Summe haette diese Eigenschaft nicht — sie wuerde ein voellig
    fremdes Thema mit maximaler Neuheit belohnen.

    Vorbedingung: beide Werte in [0.0, 1.0].
    Nachbedingung: Rueckgabe in [0.0, NOVA_NEUGIER].
    Fehlerfaelle: Werte ausserhalb des Bereichs — ValueError. Ein Wert, der
        seinen Bereich verlaesst, ist ein Defekt beim Aufrufer; ihn hier
        stillschweigend zu klemmen wuerde ihn verbergen.
    """
    # ── Eingabe-Validierung ─────────────────────
    for name, wert in (("resonanz", resonanz), ("neuheit", neuheit)):
        if not isinstance(wert, (int, float)) or isinstance(wert, bool):
            raise ValueError(
                f"neugier_vektor_berechnen: '{name}' ist nicht numerisch "
                f"({type(wert).__name__})"
            )
        if not 0.0 <= float(wert) <= 1.0:
            raise ValueError(
                f"neugier_vektor_berechnen: '{name}' = {wert} liegt "
                f"ausserhalb von 0.0–1.0"
            )

    # ── Verarbeitung / Ausgabe ──────────────────
    return NOVA_NEUGIER * float(resonanz) * float(neuheit)


def ist_dublette(hoechste_aehnlichkeit_zu_luecken: float) -> bool:
    """Ob ein Kandidat bereits als Luecke erfasst ist.

    Geprueft wird gegen ALLE bestehenden Zeilen, unabhaengig vom Status:
    offen, geschlossen und ausgeschlossen sperren gleichermassen.

    Vorbedingung: hoechste Cosine-Similarity zu den bestehenden Luecken.
        Eine leere Tabelle liefert 0.0.
    Nachbedingung: True, wenn der Kandidat aufgefrischt statt neu angelegt
        werden soll.
    """
    # ── Verarbeitung / Ausgabe ──────────────────
    return float(hoechste_aehnlichkeit_zu_luecken) >= LUECKE_DUBLETTE_SCHWELLE
