"""Kalibrierung der Initiative-Schwelle gegen einen unabhaengigen Zeugen.

Die Schwelle entscheidet, ab welchem Rohwert die Achse auf "Nutzer fuehrt"
kippt. Sie ist **nicht** der Median des Bestands: Ein Median sichert zwar, dass
beide Bits erreichbar sind, erzwingt aber einen 50/50-Schnitt, den die
Wirklichkeit nicht hergibt. Gemessen (Chat 116, 83 Turns, ein Paar) trennte der
Median mit 65,1 % Uebereinstimmung und kappa 0,286; die gegen einen Zeugen
gesuchte Schwelle bei -0.45 mit 83,1 % und kappa 0,482.

**Was dieses Modul tut und was nicht.** Hier steht nur die Rechnung: Cohens
kappa, die Suche ueber ein Schwellenraster und die Auswertung der
Positions-Kontrolle. Keine LLM-Calls, keine Datenbank, kein Redis — der Zeuge
selbst sitzt in `agents/kalibrierung/zeuge.py`, der Korpus in `korpus.py`.
Eine Rechenschicht, die ihre Eingaben selbst holt, ist ohne die Datenbank nicht
pruefbar; genau deshalb sind die drei getrennt.

**Warum kappa und nicht die reine Uebereinstimmung.** Bei einer schiefen
Verteilung erreicht eine Schwelle, die fast alles auf ein Bit legt, hohe
Uebereinstimmung, ohne irgendetwas zu trennen. Kappa rechnet die zufaellig
erwartete Uebereinstimmung heraus und faellt in genau diesem Fall.

**Erreichbarkeit ist Nebenbedingung, nicht Nebenprodukt.** Die beste Schwelle
nach kappa waere ohne die Bedingung womoeglich eine, die der Minderheit nur
wenige Prozent laesst — und damit einen Teil der 64 Sektoren praktisch wieder
schliesst. Genau das war der Defekt, den die Achse abgeloest hat.

Konzept: novaberg-gv-initiative_k.md §7 (der Agent), §12 (Zeuge und Suche).
"""

import logging
from dataclasses import dataclass, field

from config import (
    KALIBRIERUNG_MIN_MINDERHEIT,
    KALIBRIERUNG_MIN_POSITIONSDIFFERENZ,
    KALIBRIERUNG_MIN_TURNS,
    KALIBRIERUNG_RASTER_MAX,
    KALIBRIERUNG_RASTER_MIN,
    KALIBRIERUNG_RASTER_SCHRITT,
)
from ei.initiative import initiative_bit

logger = logging.getLogger("ki_server.ei.kalibrierung")


@dataclass
class Urteilspaar:
    """Ein Turn mit beiden Lesarten: der gerechneten und der bezeugten.

    Die beiden Seiten stammen aus verschiedenen Quellen und duerfen sich nie
    berueheren, bevor sie hier verglichen werden — der Rohwert kommt aus
    `fuehrung_messen`, das Urteil aus einem Modell, das nur zwei Texte gesehen
    hat. Ein Vergleich, dessen Seiten sich vorher treffen, vergleicht nichts.
    """

    turn_id: str
    # Turn des Nutzers, gegen dessen Vorantwort gemessen wurde.

    rohwert: float
    # Ergebnis von `fuehrung_messen`, in [-1, +1]. OHNE Charakter-Versatz:
    # Kalibriert wird die Schwelle, nicht die Charakterverschiebung.

    zeuge_fuehrt: bool
    # Das Urteil: Hat der Nutzer in diesem Turn die Richtung gesetzt?


@dataclass
class Schwellenkandidat:
    """Eine geprueete Schwelle mit allem, was ihre Wahl begruendet."""

    schwelle:        float
    uebereinstimmung: float   # Anteil gleicher Lesarten, [0, 1]
    kappa:           float    # Cohens kappa, [-1, +1]
    bit0_anteil:     float    # Anteil "Nutzer fuehrt" nach dieser Schwelle
    minderheit:      float    # min(bit0_anteil, 1 - bit0_anteil)
    zulaessig:       bool     # traegt die Minderheit die Nebenbedingung?


@dataclass
class Kalibrierung:
    """Das Ergebnis eines Kalibrierlaufs.

    `schwelle` ist None, wenn keine Schwelle bestimmt werden konnte — zu wenige
    Turns oder kein zulaessiger Kandidat. Dann steht der Grund in `grund`, und
    der Aufrufer schreibt nichts: Eine Schwelle aus zu wenigen Turns saehe aus
    wie eine Messung.
    """

    schwelle:   float | None            = None
    kappa:      float | None            = None
    uebereinstimmung: float | None      = None
    n:          int                     = 0
    grund:      str                     = ""
    kandidaten: list[Schwellenkandidat] = field(default_factory=list)


@dataclass
class Vierfeldertafel:
    """Die vier Felder eines Vergleichs zweier zweiwertiger Lesarten.

    Vier Werte aus einer Zaehlung, zusammen erzeugt und nur zusammen deutbar —
    deshalb eine Klasse und keine vier Argumente. Die Buchstaben a bis d der
    Fachliteratur sagen an der Aufrufstelle nichts; `Vierfeldertafel(beide_ja=20,
    …)` sagt es.

    Belegt mit den Namen dieses Vergleichs: „Achse" ist der gerechnete Wert,
    „Zeuge" das unabhaengige Urteil.
    """

    beide_ja:   int = 0   # a — Achse und Zeuge sagen "der Nutzer fuehrt"
    nur_achse:  int = 0   # b — nur die Achse sagt es
    nur_zeuge:  int = 0   # c — nur der Zeuge sagt es
    beide_nein: int = 0   # d — keiner von beiden sagt es

    @property
    def summe(self) -> int:
        """Zahl der verglichenen Faelle."""
        return self.beide_ja + self.nur_achse + self.nur_zeuge + self.beide_nein


def cohens_kappa(tafel: Vierfeldertafel) -> float:
    """Rechnet Cohens kappa aus einer Vierfeldertafel.

        po = (a + d) / n
        pe = ((a+b)(a+c) + (c+d)(b+d)) / n^2
        kappa = (po - pe) / (1 - pe)

    Vorbedingung: alle vier Felder >= 0, ihre Summe > 0.
    Nachbedingung: Rueckgabe in [-1, +1].
    Fehlerfaelle: Leere Tafel — nicht rechenbar, laut gemeldet, 0.0. Ein pe von
    exakt 1.0 (beide Lesarten legen alles auf dasselbe Bit) — dann ist kappa
    nicht definiert, weil die Zufallserwartung bereits vollstaendige
    Uebereinstimmung ist; das ist ein Befund und keine perfekte Trennung,
    deshalb 0.0 und eine Log-Zeile.

    Returns:
        Cohens kappa.
    """

    # ── Eingabe-Validierung ─────────────────────
    a, b = tafel.beide_ja,  tafel.nur_achse
    c, d = tafel.nur_zeuge, tafel.beide_nein

    if min(a, b, c, d) < 0:
        logger.error(
            f"Kappa: negatives Tafelfeld (a={a}, b={b}, c={c}, d={d}) — "
            f"nicht rechenbar"
        )
        return 0.0

    n: int = tafel.summe
    if n == 0:
        logger.error("Kappa: leere Tafel — nicht rechenbar")
        return 0.0

    # ── Verarbeitung ────────────────────────────
    po: float = (a + d) / n
    pe: float = ((a + b) * (a + c) + (c + d) * (b + d)) / (n * n)

    if pe >= 1.0:
        logger.warning(
            f"Kappa: Zufallserwartung liegt bei {pe:.4f} — beide Lesarten "
            f"legen alles auf dasselbe Bit (a={a}, b={b}, c={c}, d={d}). "
            f"Kappa ist hier nicht definiert und wird als 0.0 gefuehrt"
        )
        return 0.0

    kappa: float = (po - pe) / (1.0 - pe)

    # ── Ausgabe-Verifikation ────────────────────
    if not (-1.001 <= kappa <= 1.001):
        logger.error(
            f"Kappa: Ergebnis {kappa:.4f} ausserhalb [-1, +1] "
            f"(po={po:.4f}, pe={pe:.4f}) — die Tafel ist defekt"
        )
        return 0.0

    return round(max(-1.0, min(1.0, kappa)), 4)


def schwelle_pruefen(paare: list[Urteilspaar], schwelle: float) -> Schwellenkandidat:
    """Wertet eine einzelne Schwelle gegen den Korpus aus.

    Binarisiert jeden Rohwert mit `initiative_bit` — derselben Funktion, die
    die Achse zur Laufzeit benutzt. Eine eigene Kopie der Regel waere die
    Stelle, an der Kalibrierung und Laufzeit spaeter auseinanderlaufen, ohne
    dass es jemandem auffiele.

    Vorbedingung: `paare` ist nicht leer.
    Nachbedingung: Der Kandidat traegt Uebereinstimmung, kappa, Bit-0-Anteil
    und die Aussage, ob er die Minderheiten-Nebenbedingung traegt.
    Fehlerfaelle: Leerer Korpus — laut gemeldet, ein Kandidat mit kappa 0.0
    und `zulaessig=False`.

    Returns:
        Der ausgewertete Kandidat.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not paare:
        logger.error("Schwellenpruefung: leerer Korpus — nichts auszuwerten")
        return Schwellenkandidat(schwelle, 0.0, 0.0, 0.0, 0.0, False)

    # ── Verarbeitung ────────────────────────────
    tafel = Vierfeldertafel()

    for p in paare:
        achse_fuehrt: bool = initiative_bit(p.rohwert, schwelle) == 0
        if achse_fuehrt and p.zeuge_fuehrt:
            tafel.beide_ja += 1
        elif achse_fuehrt and not p.zeuge_fuehrt:
            tafel.nur_achse += 1
        elif not achse_fuehrt and p.zeuge_fuehrt:
            tafel.nur_zeuge += 1
        else:
            tafel.beide_nein += 1

    n: int = len(paare)
    bit0_anteil: float = (tafel.beide_ja + tafel.nur_achse) / n
    minderheit:  float = min(bit0_anteil, 1.0 - bit0_anteil)

    # ── Ausgabe-Verifikation ────────────────────
    return Schwellenkandidat(
        schwelle         = round(schwelle, 3),
        uebereinstimmung = round((tafel.beide_ja + tafel.beide_nein) / n, 4),
        kappa            = cohens_kappa(tafel),
        bit0_anteil      = round(bit0_anteil, 4),
        minderheit       = round(minderheit, 4),
        zulaessig        = minderheit >= KALIBRIERUNG_MIN_MINDERHEIT,
    )


def schwelle_suchen(paare: list[Urteilspaar]) -> Kalibrierung:
    """Sucht die Schwelle mit dem besten kappa, die beide Bits offen laesst.

    Rastert den Wertebereich der Achse ab und waehlt unter den zulaessigen
    Kandidaten den mit dem hoechsten kappa. Zulaessig ist ein Kandidat, dessen
    schwaechere Seite mindestens KALIBRIERUNG_MIN_MINDERHEIT der Turns traegt.

    **Warum nicht einfach das Maximum.** Ohne die Nebenbedingung gewinnt bei
    schiefen Korpora regelmaessig eine Randschwelle: Sie legt fast alles auf
    ein Bit, trifft damit die Mehrheit der Zeugenurteile und schliesst die
    Haelfte der Sektoren wieder. Die Achse wurde genau deshalb ersetzt.

    Vorbedingung: mindestens KALIBRIERUNG_MIN_TURNS Paare, jedes mit einem
    Rohwert in [-1, +1].
    Nachbedingung: Bei Erfolg traegt das Ergebnis Schwelle, kappa,
    Uebereinstimmung, die Fallzahl und alle geprueften Kandidaten. Bei
    Misserfolg ist `schwelle` None und `grund` benennt ihn.
    Fehlerfaelle: Zu wenige Paare, oder kein Kandidat traegt die
    Nebenbedingung — beides fuehrt zu einem Ergebnis ohne Schwelle. Der
    Aufrufer schreibt dann nichts; die bestehende Schwelle bleibt stehen.

    Returns:
        Die Kalibrierung.
    """

    # ── Eingabe-Validierung ─────────────────────
    n: int = len(paare)

    if n < KALIBRIERUNG_MIN_TURNS:
        grund: str = (
            f"{n} Turn-Paare, verlangt sind {KALIBRIERUNG_MIN_TURNS} — "
            f"keine Kalibrierung"
        )
        logger.error(f"Schwellensuche: {grund}")
        return Kalibrierung(n=n, grund=grund)

    ausserhalb: list[str] = [
        p.turn_id for p in paare if not (-1.0 <= p.rohwert <= 1.0)
    ]
    if ausserhalb:
        logger.error(
            f"Schwellensuche: {len(ausserhalb)} Rohwerte ausserhalb [-1, +1] "
            f"(zuerst: {ausserhalb[:3]}) — die Messung ist defekt, "
            f"keine Kalibrierung"
        )
        return Kalibrierung(n=n, grund="Rohwerte ausserhalb des Wertebereichs")

    # ── Verarbeitung ────────────────────────────
    kandidaten: list[Schwellenkandidat] = []
    schritte:   int = int(
        round((KALIBRIERUNG_RASTER_MAX - KALIBRIERUNG_RASTER_MIN)
              / KALIBRIERUNG_RASTER_SCHRITT)
    )

    for i in range(schritte + 1):
        schwelle: float = KALIBRIERUNG_RASTER_MIN + i * KALIBRIERUNG_RASTER_SCHRITT
        kandidaten.append(schwelle_pruefen(paare, schwelle))

    zulaessige: list[Schwellenkandidat] = [k for k in kandidaten if k.zulaessig]

    # ── Ausgabe-Verifikation ────────────────────
    if not zulaessige:
        bester_unzulaessig = max(kandidaten, key=lambda k: k.kappa)
        grund = (
            f"kein Kandidat traegt die Minderheit von "
            f"{KALIBRIERUNG_MIN_MINDERHEIT:.0%} — bester waere "
            f"{bester_unzulaessig.schwelle:+.2f} mit kappa "
            f"{bester_unzulaessig.kappa:.3f} bei Minderheit "
            f"{bester_unzulaessig.minderheit:.1%}"
        )
        logger.error(f"Schwellensuche: {grund}")
        return Kalibrierung(n=n, grund=grund, kandidaten=kandidaten)

    # Bei gleichem kappa gewinnt die Schwelle mit der groesseren Minderheit:
    # Die Kurve ist um ihr Maximum herum flach (gemessen zwischen -0.55 und
    # -0.35), und auf einem Plateau ist die erreichbarere Seite die bessere.
    bester: Schwellenkandidat = max(
        zulaessige, key=lambda k: (k.kappa, k.minderheit)
    )

    logger.info(
        f"Schwellensuche: {bester.schwelle:+.2f} gewaehlt aus "
        f"{len(zulaessige)} zulaessigen von {len(kandidaten)} Kandidaten "
        f"(n={n}, kappa={bester.kappa:.3f}, "
        f"Uebereinstimmung {bester.uebereinstimmung:.1%}, "
        f"Bit0 {bester.bit0_anteil:.1%}, Minderheit {bester.minderheit:.1%})"
    )

    return Kalibrierung(
        schwelle         = bester.schwelle,
        kappa            = bester.kappa,
        uebereinstimmung = bester.uebereinstimmung,
        n                = n,
        grund            = "",
        kandidaten       = kandidaten,
    )


def positions_kontrolle(
    anteil_b_nutzer: float,
    anteil_b_nova:   float,
) -> tuple[bool, str]:
    """Prueft, ob der Zeuge die Sprecher liest und nicht ihre Reihenfolge.

    Der Zeuge bekommt zwei Texte und sagt, ob **B** die Richtung gesetzt hat.
    Laege er nur auf der Position — wer zuletzt spricht, fuehrt —, dann muesste
    er in beiden Richtungen denselben Anteil liefern. Gemessen (Chat 116):
    79,5 % bei B = Nutzer gegen 36,1 % bei B = Nova, also 43,4 Prozentpunkte
    Unterschied.

    **Diese Kontrolle zeigt nicht, dass der Zeuge richtig liegt.** Sie zeigt
    nur, dass er ueberhaupt zwischen den Sprechern unterscheidet. Ohne sie
    waere ein Zeuge, der stur "der zweite fuehrt" sagt, von einem echten
    Urteil nicht zu trennen — und die ganze Kalibrierung stuende auf einer
    Positionsregel.

    **Gewertet wird der Betrag, nicht das Vorzeichen** (korrigiert Chat 117).
    Die erste Fassung verlangte, dass der Nutzer-Anteil der hoehere ist. Das
    ist keine Eigenschaft eines guten Zeugen, sondern eine Aussage ueber das
    Paar: Fuehrt Nova in einem Korpus tatsaechlich haeufiger, muss ein
    korrekter Zeuge genau das sagen. Gemessen am 29.07.2026 mit einem
    nachgebauten Zeugen: 20,0 % gegen 90,0 %, also 70 Punkte in die andere
    Richtung — ein Zeuge, der **staerker** unterscheidet als der aus Chat 116
    (43,4 Punkte) und an der Vorzeichen-Pruefung dennoch gescheitert waere.
    Positionsblind heisst Differenz nahe null, in beiden Richtungen.

    Vorbedingung: beide Anteile in [0, 1].
    Nachbedingung: (bestanden, Begruendung). Bestanden heisst: Der Betrag der
    Differenz traegt mindestens KALIBRIERUNG_MIN_POSITIONSDIFFERENZ.
    Fehlerfaelle: Anteile ausserhalb [0, 1] — laut gemeldet, nicht bestanden.

    Returns:
        (bestanden, Klartext-Begruendung)
    """

    # ── Eingabe-Validierung ─────────────────────
    for name, wert in (("B=Nutzer", anteil_b_nutzer), ("B=Nova", anteil_b_nova)):
        if not (0.0 <= wert <= 1.0):
            text: str = f"Anteil {name} = {wert:.3f} ausserhalb [0, 1]"
            logger.error(f"Positions-Kontrolle: {text}")
            return False, text

    # ── Verarbeitung ────────────────────────────
    differenz: float = anteil_b_nutzer - anteil_b_nova

    # ── Ausgabe-Verifikation ────────────────────
    bestanden: bool = abs(differenz) >= KALIBRIERUNG_MIN_POSITIONSDIFFERENZ
    text = (
        f"B=Nutzer {anteil_b_nutzer:.1%} gegen B=Nova {anteil_b_nova:.1%}, "
        f"Differenz {differenz:+.1%} (Betrag {abs(differenz):.1%}, "
        f"verlangt {KALIBRIERUNG_MIN_POSITIONSDIFFERENZ:.0%})"
    )

    if bestanden:
        logger.info(f"Positions-Kontrolle bestanden: {text}")
    else:
        logger.error(
            f"Positions-Kontrolle NICHT bestanden: {text} — der Zeuge "
            f"unterscheidet die Sprecher nicht hinreichend; sein Urteil taugt "
            f"nicht als Kalibriergrundlage"
        )

    return bestanden, text
