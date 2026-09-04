"""Die Rechnung der Faszination — `novaberg-thinking-faszination_k.md` §10.

Faszination ist eine **Bindungsgroesse, keine Emotion** (§15, Entscheidung 1):
Kriegsgeschichte und Gartenkraeuter sind derselbe Mechanismus mit
unterschiedlicher Haerte, und zwei gegensaetzliche Plutchik-Lagen koennen
denselben Zustand tragen. Der Wert ist deshalb **valenzblind**.

Heute steht hier ein Faktor von neun:

    roh = bindung_roh x merkmalszug x praegungszug
                      x f_arousal x f_besetzung x f_verlauf
                      x f_intent  x f_modus     x f_anlage

`merkmalszug` (§10.1) rechnet hier, `praegungszug` (§10.3) in
`memory/praegung.py`. `bindung_roh` (§10.2) und die sechs Turn-Modulatoren
(§10.5) sind nicht gebaut, und damit auch nicht die Zusammenfuehrung (§10.6).

Reine Funktionen: keine Datenbank, kein Modell, kein Zustand.
"""

import logging

from config import MERKMALSZUG_BONUS, QUALITAET_KANON

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
