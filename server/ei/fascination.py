"""Die Rechnung der Faszination — `novaberg-thinking-faszination_k.md` §10.

Faszination ist eine **Bindungsgroesse, keine Emotion** (§15, Entscheidung 1):
Kriegsgeschichte und Gartenkraeuter sind derselbe Mechanismus mit
unterschiedlicher Haerte, und zwei gegensaetzliche Plutchik-Lagen koennen
denselben Zustand tragen. Der Wert ist deshalb **valenzblind**.

Heute steht hier ein Faktor von neun:

    roh = bindung_roh x merkmalszug x praegungszug
                      x f_arousal x f_besetzung x f_verlauf
                      x f_intent  x f_modus     x f_anlage

`merkmalszug` (§10.1) und die sechs Turn-Modulatoren (§10.5) rechnen hier,
`praegungszug` (§10.3) in `memory/praegung.py`. `bindung_roh` (§10.2) ist
nicht gebaut, und damit auch nicht die Zusammenfuehrung (§10.6).

Reine Funktionen: keine Datenbank, kein Modell, kein Zustand.
"""

import logging

from config import (
    FASZ_ANLAGE_MAX,
    FASZ_ANLAGE_MIN,
    FASZ_AROUSAL_BREITE_LINKS,
    FASZ_AROUSAL_BREITE_RECHTS,
    FASZ_AROUSAL_MAX,
    FASZ_AROUSAL_MIN,
    FASZ_AROUSAL_SCHEITEL,
    FASZ_AWE_EMOTIONEN,
    FASZ_BESETZUNG_AWE,
    FASZ_BESETZUNG_NEUTRAL,
    FASZ_BESETZUNG_SEKTOR,
    FASZ_INTENT_FAKTOREN,
    FASZ_MODUS_FAKTOREN,
    FASZ_VERLAUF_FAKTOREN,
    MERKMALSZUG_BONUS,
    QUALITAET_KANON,
)

logger = logging.getLogger("ki_server.ei.fascination")


def merkmalszug(profil: dict[str, float]) -> float:
    """Verrechnet ein Qualitaetsprofil zu einem Zug — ein weiches ODER.

    **Die staerkste Dimension traegt allein und vollstaendig; Kombination ist
    ein Zuschlag, keine Bedingung.**

        merkmalszug = m_max + MERKMALSZUG_BONUS * Mittel(uebrige fuenf)

    Beide naheliegenden Formen sind falsch, und zwar aus verschiedenen
    Gruenden. **Ein Mittelwert** gaebe bei einer Dimension auf 1,0 und fuenf
    auf 0 den Wert 0,17 — der Zauberer bekaeme keine Faszination, obwohl
    gerade seine Ungewissheit sie traegt. **Ein Produkt** verstiesse gegen
    Regel (a) aus §10.0: Eine Null darf nicht aus einer Multiplikation
    entstehen, nur weil ein Faktor mit geringem Einfluss auf null steht.

    Rein. Vorbedingung: `profil` bildet Dimensionsnamen auf Auspraegungen in
        [0,1] ab. Unbekannte Namen und Werte ausserhalb der Spanne werden
        gemeldet und verworfen — die Pruefung steht hier und nicht beim
        Aufrufer, weil das Profil aus der Datenbank kommt und damit eine
        externe Quelle ist.
    Nachbedingung: Ein Wert in [0.0, 1.0 + MERKMALSZUG_BONUS]; 0.0 bei
        leerer oder verworfener Eingabe.

    Args:
        profil: {dimension: auspraegung}, idealerweise alle sechs.

    Returns:
        Der Merkmalszug. Die Obergrenze wird nur erreicht, wenn alle sechs
        Dimensionen auf 1,0 stehen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not profil:
        return 0.0
    fremde: list[str] = [name for name in profil if name not in QUALITAET_KANON]
    if fremde:
        logger.error(
            f"Merkmalszug: Profil traegt Dimensionen ausserhalb des Kanons "
            f"{sorted(fremde)} — verworfen; ein unbekannter Name ist ein "
            f"Defekt und kein neuer Fall"
        )
        return 0.0
    werte: list[float] = []
    for name, wert in profil.items():
        # `bool` steht vorn, weil `True` in Python ein `int` ist und die
        # Zahlenpruefung sonst passiert — als 1.0, also als voller Ausschlag.
        if isinstance(wert, bool) or not isinstance(wert, (int, float)) or wert != wert:  # NaN
            logger.error(
                f"Merkmalszug: Auspraegung von '{name}' ist {wert!r} und keine "
                f"Zahl — verworfen"
            )
            return 0.0
        if not (0.0 <= float(wert) <= 1.0):
            logger.error(
                f"Merkmalszug: Auspraegung von '{name}' ist {wert} und liegt "
                f"ausserhalb [0.0, 1.0] — verworfen, nicht geklemmt"
            )
            return 0.0
        werte.append(float(wert))

    # ── Verarbeitung ────────────────────────────
    hoechste: float = max(werte)
    uebrige: list[float] = sorted(werte, reverse=True)[1:]
    zuschlag: float = (
        MERKMALSZUG_BONUS * (sum(uebrige) / len(uebrige)) if uebrige else 0.0
    )
    zug: float = hoechste + zuschlag

    # ── Ausgabe-Verifikation ────────────────────
    # Spanne laut Nachbedingung: 0.0 bis 1.0 + MERKMALSZUG_BONUS. Die
    # Obergrenze ist durch Konstruktion erreichbar (alle sechs auf 1,0) und
    # wird deshalb nicht gekappt — was darueber laege, waere ein Rechenfehler.
    obergrenze: float = 1.0 + MERKMALSZUG_BONUS
    if not (0.0 <= zug <= obergrenze):
        logger.error(
            f"Merkmalszug: Ergebnis {zug:.4f} ausserhalb der Spanne "
            f"[0.0, {obergrenze:.2f}] bei {len(werte)} Dimensionen "
            f"(hoechste {hoechste:.2f}, Zuschlag {zuschlag:.4f}) — verworfen"
        )
        return 0.0
    return zug


def dominante_dimension(profil: dict[str, float]) -> tuple[str, float]:
    """Die staerkste Dimension eines Profils und ihre Auspraegung.

    Sie ist die Groesse, an der sich der Satz pruefen laesst: §6.2 hat 50
    Knoten von Hand bewertet und ihre Verteilung festgehalten. Eine
    maschinelle Bewertung, die dieselbe Verteilung trifft, ist der erste
    Beleg dafuer, dass der gesetzte Satz am Bestand traegt.

    **Bei Gleichstand entscheidet die Reihenfolge des Kanons**, damit zwei
    Laeufe ueber dasselbe Profil dieselbe Antwort geben. Ein Gleichstand ist
    kein Randfall: Bei drei erlaubten Stufen ist er der Regelfall.

    Rein. Vorbedingung: `profil` ist gegen den Kanon geprueft — der Aufrufer
        hat `merkmalszug` gerufen oder prueft selbst.
    Nachbedingung: (Name, Auspraegung); ("", 0.0) bei leerer Eingabe.
    """
    if not profil:
        return ("", 0.0)
    rang: dict[str, int] = {name: i for i, name in enumerate(QUALITAET_KANON)}
    name: str = min(
        profil, key=lambda d: (-float(profil[d]), rang.get(d, len(rang)))
    )
    return (name, float(profil[name]))


# ─────────────────────────────────────────────
# Die sechs Turn-Modulatoren (§10.5)
# ─────────────────────────────────────────────
#
# Sie beantworten nicht, *ob* ein Traeger fasziniert, sondern *wie stark der
# laufende Turn dazu beitraegt*. Alle sechs sind Faktoren um 1.0 und werden
# nie 0 — sonst loeschte ein einzelner Turn die ganze Bindung (Regel (a),
# §10.0).
#
# **Ein unbekannter Wert ist ein Befund, kein Vorgabefall.** Jede der drei
# Tabellen ist vollstaendig gegen ihren Kanon; trifft trotzdem etwas
# Unbekanntes ein, wird 1.0 zurueckgegeben **und laut gemeldet**. Der
# neutrale Wert ist hier richtig — er verzerrt das Produkt nicht —, aber er
# darf nicht stumm bleiben: Genau so faende ein Kanonbruch nie jemand.
# `[gemessen]` 04.09.2026: Der Bestand traegt in `intent` 28-mal
# `philosophischer_austausch`, einen Wert, den der Intent-Kanon nicht kennt.


def f_arousal(arousal: float) -> float:
    """Der Erregungs-Modulator — ein umgekehrtes U mit Scheitel bei 0,65.

    **Weder Reglosigkeit noch Ueberreizung binden Aufmerksamkeit muehelos**
    (Berlyne; §2.1). Das Maximum liegt dort, wo ein Reiz wach macht, ohne zu
    ueberfordern; zu beiden Seiten faellt der Faktor auf `FASZ_AROUSAL_MIN`.

    **Die beiden Flanken sind verschieden breit.** Der Scheitel liegt nicht
    in der Mitte, also wird jede Flanke ueber ihren eigenen Abstand zum Rand
    normiert; sonst erreichte nur die linke ihr Minimum. Die rechte faellt
    dadurch steiler — Ueberreizung entzieht schneller als Reglosigkeit, was
    §10.5 mit *ueber 0,85 fallend* ausdruecklich verlangt.

    Rein. Vorbedingung: `arousal` liegt in [0, 1]; Werte ausserhalb werden
        geklemmt und gemeldet, weil sie auf einen Rechenfehler beim Aufrufer
        deuten.
    Nachbedingung: ein Faktor in [FASZ_AROUSAL_MIN, FASZ_AROUSAL_MAX].
    """
    # ── Eingabe-Validierung ─────────────────────
    wert: float = float(arousal)
    if not 0.0 <= wert <= 1.0:
        logger.error(
            f"Faszination: arousal {wert:.4f} liegt ausserhalb [0, 1] — "
            f"geklemmt; der Aufrufer rechnet auf einer anderen Skala"
        )
        wert = max(0.0, min(1.0, wert))

    # ── Verarbeitung ────────────────────────────
    # Normierter Abstand zum Scheitel, je Flanke: 0 am Scheitel, 1 am Rand.
    breite: float = (
        FASZ_AROUSAL_BREITE_LINKS if wert < FASZ_AROUSAL_SCHEITEL
        else FASZ_AROUSAL_BREITE_RECHTS
    )
    abstand: float = abs(wert - FASZ_AROUSAL_SCHEITEL) / breite
    hub: float = FASZ_AROUSAL_MAX - FASZ_AROUSAL_MIN
    faktor: float = FASZ_AROUSAL_MAX - hub * min(abstand, 1.0) ** 2

    # ── Ausgabe-Verifikation ────────────────────
    return _in_spanne(faktor, FASZ_AROUSAL_MIN, FASZ_AROUSAL_MAX, "f_arousal")


def f_besetzung(emotion: str) -> float:
    """Der Besetzungs-Modulator — ist ueberhaupt ein Sektor belegt?

    **Valenzblind, und das ist die Entscheidung** (§10.5): `SEKTOR_GRUPPE`
    wird bewusst ignoriert. Ein negativ besetzter Sektor bindet so gut wie
    ein positiver; Kriegsgeschichte und Gartenkraeuter sind derselbe
    Mechanismus (§15, Entscheidung 1).

    Die eine Ausnahme nach oben ist die **Awe-Dyade** — Ehrfurcht aus Furcht
    und Ueberraschung. Sie ist der Zustand, den die Literatur ausdruecklich
    mit Faszination verbindet.

    Rein. Vorbedingung: keine — ein leerer Wert ist der Normalfall eines
        Turns ohne Emotionsurteil.
    Nachbedingung: einer der drei Faktoren.
    """
    name: str = (emotion or "").strip().lower()
    if not name or name == "neutral":
        return FASZ_BESETZUNG_NEUTRAL
    if name in FASZ_AWE_EMOTIONEN:
        return FASZ_BESETZUNG_AWE
    return FASZ_BESETZUNG_SEKTOR


def f_verlauf(emotions_vector: str) -> float:
    """Der Verlaufs-Modulator — die Bewegung, nicht die Richtung.

    **`eskalation` steht oben, obwohl sie negativ ist**, und das ist der
    Kern: Ein sich aufbauender Zustand bindet Aufmerksamkeit, ein flacher
    nicht. Die Achse ist die Bewegung.

    Rein. Nachbedingung: ein Faktor aus `FASZ_VERLAUF_FAKTOREN`, oder 1.0
        bei einem Wert ausserhalb des Kanons — dann mit Meldung.
    """
    return _aus_tabelle(
        emotions_vector, FASZ_VERLAUF_FAKTOREN, "emotions_vector",
    )


def f_intent(intent: str) -> float:
    """Der Intentions-Modulator — wie stark der Turn an einen Gegenstand bindet.

    `knowledge` und `creative` tragen am meisten, weil sie eine Sache
    verhandeln; `task` und `meta` am wenigsten, weil sie den Ablauf
    verhandeln.

    Rein. Nachbedingung: ein Faktor aus `FASZ_INTENT_FAKTOREN`, oder 1.0 bei
        einem Wert ausserhalb des Kanons — dann mit Meldung.
    """
    return _aus_tabelle(intent, FASZ_INTENT_FAKTOREN, "intent")


def f_modus(mode: str) -> float:
    """Der Modus-Modulator — wird in dieser Gespraechsform vertieft?

    Rein. Nachbedingung: ein Faktor aus `FASZ_MODUS_FAKTOREN`, oder 1.0 bei
        einem Wert ausserhalb des Kanons — dann mit Meldung.
    """
    return _aus_tabelle(mode, FASZ_MODUS_FAKTOREN, "mode")


def f_anlage(wissbegier: float | None) -> float:
    """Der Anlage-Modulator — Novas Zuwendung zum Gegenstand.

    **Von zwoelf Radspeichen traegt genau eine**: `wissbegier <-> langeweile`
    ist die einzige, die die Zuwendung zum **Gegenstand** beschreibt statt
    zur Person (§10.5). Die uebrigen elf stehen in Gegenpol-Anordnung zur
    Person und gehoeren in die Salienz, nicht hierher.

    Vorbedingung: `wissbegier` liegt in [0, 1] oder ist None. **None ist der
        ehrliche Fall** — es gibt noch keine Radmessung fuer dieses Paar —,
        und er liefert 1.0, den neutralen Faktor: Eine fehlende Anlage darf
        die Faszination weder heben noch senken.
    Nachbedingung: ein Faktor in [FASZ_ANLAGE_MIN, FASZ_ANLAGE_MAX].
    """
    if wissbegier is None:
        return 1.0
    wert: float = float(wissbegier)
    if not 0.0 <= wert <= 1.0:
        logger.error(
            f"Faszination: wissbegier {wert:.4f} liegt ausserhalb [0, 1] — "
            f"geklemmt; das Rad rechnet auf einer anderen Skala"
        )
        wert = max(0.0, min(1.0, wert))
    faktor: float = FASZ_ANLAGE_MIN + wert * (FASZ_ANLAGE_MAX - FASZ_ANLAGE_MIN)
    return _in_spanne(faktor, FASZ_ANLAGE_MIN, FASZ_ANLAGE_MAX, "f_anlage")


def _aus_tabelle(wert: str, tabelle: dict[str, float], feld: str) -> float:
    """Ein Faktor aus einer Kanon-Tabelle — ein Fehltreffer wird gemeldet.

    Der neutrale Rueckfall 1.0 ist richtig (er verzerrt das Produkt nicht)
    und darf trotzdem nicht stumm sein: Ein Wert ausserhalb des Kanons ist
    ein Befund ueber die Perzeption, und stumm faende ihn niemand.
    """
    name: str = (wert or "").strip().lower()
    if not name:
        return 1.0
    if name not in tabelle:
        logger.warning(
            f"Faszination: `{feld}` traegt den Wert '{name}', den der Kanon "
            f"nicht kennt — Faktor 1.0, und der Kanon ist zu pruefen"
        )
        return 1.0
    return tabelle[name]


def _in_spanne(wert: float, unten: float, oben: float, name: str) -> float:
    """Haelt einen gerechneten Faktor in seiner zugesagten Spanne.

    Eine Verletzung ist ein Rechenfehler in dieser Datei, kein Eingabefehler
    — sie wird deshalb laut gemeldet und nicht geklemmt weitergereicht,
    ohne dass es jemand erfaehrt.
    """
    if not unten - 1e-9 <= wert <= oben + 1e-9:
        logger.error(
            f"Faszination: {name} lieferte {wert:.4f} ausserhalb "
            f"[{unten}, {oben}] — geklemmt; die Rechnung ist zu pruefen"
        )
    return max(unten, min(oben, wert))
