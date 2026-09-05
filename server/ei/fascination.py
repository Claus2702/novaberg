"""Die Rechnung der Faszination — `novaberg-thinking-faszination_k.md` §10.

Faszination ist eine **Bindungsgroesse, keine Emotion** (§15, Entscheidung 1):
Kriegsgeschichte und Gartenkraeuter sind derselbe Mechanismus mit
unterschiedlicher Haerte, und zwei gegensaetzliche Plutchik-Lagen koennen
denselben Zustand tragen. Der Wert ist deshalb **valenzblind**.

Heute steht hier ein Faktor von neun:

    roh = bindung_roh x merkmalszug x praegungszug
                      x f_arousal x f_besetzung x f_verlauf
                      x f_intent  x f_modus     x f_anlage

`merkmalszug` (§10.1), `bindung_roh` (§10.2) und die sechs Turn-Modulatoren
(§10.5) rechnen hier, `praegungszug` (§10.3) in `memory/praegung.py`. Die
Zusammenfuehrung (§10.6) steht am Ende dieser Datei.

Reine Funktionen: keine Datenbank, kein Modell, kein Zustand.
"""

import logging
import math

from config import (
    BINDUNG_GEWICHTE,
    BINDUNG_HALBSTRECKE_VERWEILDAUER,
    BINDUNG_HALBSTRECKE_WIEDERKEHR,
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
    FASZ_MAXIMUM,
    FASZ_MODUS_FAKTOREN,
    FASZ_STRANGZUG_HALBSTRECKE_FAEDEN,
    FASZ_STRANGZUG_HUB,
    FASZ_VERLAUF_FAKTOREN,
    MERKMALSZUG_BONUS,
    QUALITAET_KANON,
    QUALITAET_VERFALL_BODEN,
    QUALITAET_VERFALL_HALBSTRECKE_BERUEHRUNGEN,
    QUALITAET_VERFALL_HALBSTRECKE_TAGE,
    QUALITAET_VERFALL_UEBER_BERUEHRUNGEN,
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


# ─────────────────────────────────────────────
# Der Anker — Bindung ueber Episoden (§10.2)
# ─────────────────────────────────────────────


def norm_saettigung(zahl: float, halbstrecke: float) -> float:
    """Normiert einen nach oben offenen Zaehler auf [0, 1).

        norm(n) = n / (n + H)

    **Bezugspunktfrei, und das ist der Grund fuer diese Form.** Eine Min-Max-
    Streckung ueber den Bestand haette einen wandernden Massstab: Derselbe
    Traeger bekaeme morgen einen anderen Wert, weil ein anderer gewachsen ist
    — und was gemessen wurde, waere danach nicht mehr von der Skala zu
    trennen. Hier haengt der Wert allein am eigenen Zaehler.

    Bei `zahl == halbstrecke` steht das Ergebnis exakt auf 0,5. Die Kurve
    erreicht 1 nie; das passt zu Zaehlern ohne Obergrenze (§13).

    Rein. Vorbedingung: `zahl` >= 0 und `halbstrecke` > 0. Beides wird
        geprueft — eine negative Zahl deutet auf einen Zaehlfehler, eine
        Halbstrecke <= 0 auf eine leere Konfiguration.
    Nachbedingung: ein Wert in [0, 1).
    """
    # ── Eingabe-Validierung ─────────────────────
    n: float = float(zahl)
    h: float = float(halbstrecke)
    if n < 0.0:
        logger.error(
            f"Faszination: Zaehler {n} ist negativ — als 0 gewertet; "
            f"ein Zaehler zaehlt nicht rueckwaerts"
        )
        n = 0.0
    if h <= 0.0:
        logger.error(
            f"Faszination: Halbstrecke {h} ist nicht positiv — die Normierung "
            f"liefert 0.0; die Konstante ist zu pruefen"
        )
        return 0.0

    # ── Verarbeitung / Ausgabe ──────────────────
    return n / (n + h)


def bindung_roh(
    wiederkehr:   float,
    verweildauer: float,
    eigenimpuls:  float | None,
) -> float:
    """Die Bindung eines Traegers ueber Episoden — §10.2.

        bindung_roh = 0.50 * norm(wiederkehr)
                    + 0.20 * norm(verweildauer)
                    + 0.30 * eigenimpuls

    **`eigenimpuls` darf None sein, und das ist keine Bequemlichkeit.** Die
    Bruecke `verbindung` traegt keine Herkunft; sie steht in der Rohturn-Zeile,
    und **318 von 1027 Rohturns haben keine** `[gemessen 04.09.2026]`. Wer
    daraus 0.0 machte, zaehlte *„unbekannt"* wie *„der Nutzer hat es
    aufgebracht"* — und senkte damit genau die Traeger, ueber deren Herkunft
    nichts bekannt ist.

    **Bei None werden die Gewichte der beiden uebrigen Terme renormiert**, so
    dass die Summe wieder 1.0 ergibt. Der Wert bleibt damit auf derselben
    Skala und ist mit einem vollstaendigen vergleichbar; er stuetzt sich nur
    auf weniger Belege.

    Rein. Vorbedingung: die Zaehler sind >= 0, `eigenimpuls` liegt in [0, 1]
        oder ist None.
    Nachbedingung: ein Wert in [0, 1].
    """
    # ── Eingabe-Validierung ─────────────────────
    anteil: float | None = None
    if eigenimpuls is not None:
        anteil = float(eigenimpuls)
        if not 0.0 <= anteil <= 1.0:
            logger.error(
                f"Faszination: eigenimpuls {anteil:.4f} liegt ausserhalb "
                f"[0, 1] — geklemmt; er ist ein Anteil, kein Zaehler"
            )
            anteil = max(0.0, min(1.0, anteil))

    # ── Verarbeitung ────────────────────────────
    teile: dict[str, float] = {
        "wiederkehr":   norm_saettigung(
            wiederkehr, BINDUNG_HALBSTRECKE_WIEDERKEHR),
        "verweildauer": norm_saettigung(
            verweildauer, BINDUNG_HALBSTRECKE_VERWEILDAUER),
    }
    if anteil is not None:
        teile["eigenimpuls"] = anteil

    gewicht_summe: float = sum(BINDUNG_GEWICHTE[name] for name in teile)
    if gewicht_summe <= 0.0:
        logger.error(
            "Faszination: kein Bindungsterm traegt ein Gewicht — "
            "BINDUNG_GEWICHTE ist zu pruefen"
        )
        return 0.0
    wert: float = sum(
        BINDUNG_GEWICHTE[name] * anteil_wert for name, anteil_wert in teile.items()
    ) / gewicht_summe

    # ── Ausgabe-Verifikation ────────────────────
    return _in_spanne(wert, 0.0, 1.0, "bindung_roh")


# ─────────────────────────────────────────────
# Die Zusammenfuehrung (§10.6)
# ─────────────────────────────────────────────


def faszination(
    bindung:      float,
    merkmalszug_wert: float,
    praegungszug_wert: float,
    modulatoren:  dict[str, float] | None = None,
) -> tuple[float, float]:
    """Die Faszination eines Traegers im laufenden Turn — neun Faktoren.

        roh = bindung x merkmalszug x praegungszug
                      x f_arousal x f_besetzung x f_verlauf
                      x f_intent  x f_modus     x f_anlage

        faszination = sin( min(roh, FASZ_MAXIMUM) / FASZ_MAXIMUM * pi/2 ) ^ 0.5

    **Die Seltenheit ist konstruiert, nicht erhofft** (§10.6): Qualitaeten
    sind haeufig — fast jeder komplexe Text traegt `komplexitaet`. Praegungen
    sind selten. Ihr Produkt ist selten.

    **`sin^0.5` ist hier richtig, anders als beim Faden** (§7.2): Dieser Wert
    entsteht aus einem Produkt vieler Faktoren, nicht aus einem einzelnen
    Erlebnis, und soll auch schwache Faszinationen sichtbar machen. Die Kurve
    ist steil unten, damit eine entstehende Faszination sichtbar wird, und
    flach oben, damit ein intensiver Tag keine Dauerfaszination erzeugt; am
    Deckel steht sie exakt auf 1,0.

    **Der Rohwert wird mit zurueckgegeben, und das ist kein Komfort.** Die
    Glaettung ist nicht umkehrbar, sobald der Deckel greift: Zwei Traeger mit
    roh = 2,0 und roh = 6,0 stehen beide auf 1,0. Wer spaeter kalibriert,
    braucht die Zahl davor — sonst misst er die Kurve statt den Bestand.

    Rein. Vorbedingung: die drei Zuege sind >= 0; `modulatoren` traegt die
        sechs Faktoren aus §10.5 oder ist None (dann moduliert nichts).
    Nachbedingung: (faszination in [0, 1], roh >= 0).
    """
    # ── Eingabe-Validierung ─────────────────────
    zuege: dict[str, float] = {
        "bindung": float(bindung),
        "merkmalszug": float(merkmalszug_wert),
        "praegungszug": float(praegungszug_wert),
    }
    for name, wert in zuege.items():
        if wert < 0.0:
            logger.error(
                f"Faszination: {name} ist {wert:.4f} und damit negativ — "
                f"als 0 gewertet; ein Zug zieht nicht rueckwaerts"
            )
            zuege[name] = 0.0

    # ── Verarbeitung ────────────────────────────
    roh: float = zuege["bindung"] * zuege["merkmalszug"] * zuege["praegungszug"]
    for name, faktor in (modulatoren or {}).items():
        if faktor <= 0.0:
            # Regel (a) aus §10.0: keine Null aus einer Multiplikation. Ein
            # Modulator, der 0 liefert, ist ein Baufehler in dieser Datei.
            logger.error(
                f"Faszination: Modulator '{name}' lieferte {faktor:.4f} — "
                f"uebergangen; kein Turn darf die Bindung loeschen"
            )
            continue
        roh *= float(faktor)

    gedeckelt: float = min(roh, FASZ_MAXIMUM)
    wert: float = math.sin(gedeckelt / FASZ_MAXIMUM * math.pi / 2) ** 0.5

    # ── Ausgabe-Verifikation ────────────────────
    if roh > FASZ_MAXIMUM:
        logger.info(
            f"Faszination: roh {roh:.4f} ueber dem Deckel {FASZ_MAXIMUM} — "
            f"geglaettet auf 1.0; der Rohwert bleibt im Rueckgabewert"
        )
    return (_in_spanne(wert, 0.0, 1.0, "faszination"), roh)


def modulatoren_aus_turn(
    arousal:          float,
    emotion:          str,
    emotions_vector:  str,
    intent:           str,
    mode:             str,
    wissbegier:       float | None = None,
) -> dict[str, float]:
    """Baut die sechs Modulatoren eines Turns — die Klammer um §10.5.

    Sie steht hier, damit der Aufrufer die Reihenfolge nicht kennen muss und
    **keiner der sechs vergessen werden kann**: Ein fehlender Faktor waere
    stumm ein Faktor 1,0, und das ist von einem gemessenen neutralen Wert
    nicht zu unterscheiden.

    Rein. Nachbedingung: genau sechs Eintraege, jeder > 0.
    """
    return {
        "f_arousal":    f_arousal(arousal),
        "f_besetzung":  f_besetzung(emotion),
        "f_verlauf":    f_verlauf(emotions_vector),
        "f_intent":     f_intent(intent),
        "f_modus":      f_modus(mode),
        "f_anlage":     f_anlage(wissbegier),
    }


# ─────────────────────────────────────────────
# Der Verfall der Qualitaeten (§10.4)
# ─────────────────────────────────────────────


def qualitaet_verfall(
    dimension:    str,
    auspraegung:  float,
    tage:         float,
    beruehrungen: int,
) -> float:
    """Die verfallene Auspraegung einer Qualitaet — je Dimension verschieden.

    **`ungewissheit` verfaellt mit der Zahl der Beruehrungen, alle uebrigen
    mit der Zeit** (§10.4). Der Satz dahinter: *Faszination erlischt genau
    dann, wenn ihre tragende Dimension erschoepfbar ist.* Wer eine Sache oft
    genug angesehen hat, weiss, wie sie ausgeht — aber ihre Komplexitaet
    vergeht nicht dadurch, dass niemand hinsieht.

    Die Kurve ist dieselbe wie beim Praegungsverfall: hyperbolisch mit Boden,
    `v(x) = boden + (1 - boden) / (1 + x/H)`. **Der Boden liegt hoeher** als
    dort (0,40 gegen 0,20), weil eine Qualitaet beschreibt, was eine Sache
    *ist*: Was verfaellt, ist ihre Zugkraft, nicht ihr Bestand.

    Rein. Vorbedingung: `dimension` gehoert zum Kanon — sonst wird der
        Zeitverfall angewandt und gemeldet, denn er ist der Regelfall.
        `auspraegung` in [0, 1]; `tage` und `beruehrungen` >= 0.
    Nachbedingung: ein Wert in [0, auspraegung].
    """
    # ── Eingabe-Validierung ─────────────────────
    wert: float = float(auspraegung)
    if not 0.0 <= wert <= 1.0:
        logger.error(
            f"Faszination: Auspraegung {wert:.4f} von '{dimension}' liegt "
            f"ausserhalb [0, 1] — geklemmt"
        )
        wert = max(0.0, min(1.0, wert))
    if dimension not in QUALITAET_KANON:
        logger.warning(
            f"Faszination: '{dimension}' gehoert nicht zum Qualitaets-Kanon — "
            f"Zeitverfall angewandt; der Kanon ist zu pruefen"
        )

    # ── Verarbeitung ────────────────────────────
    if dimension in QUALITAET_VERFALL_UEBER_BERUEHRUNGEN:
        strecke: float = max(0.0, float(beruehrungen))
        halbstrecke: float = QUALITAET_VERFALL_HALBSTRECKE_BERUEHRUNGEN
    else:
        strecke = max(0.0, float(tage))
        halbstrecke = QUALITAET_VERFALL_HALBSTRECKE_TAGE

    boden: float = QUALITAET_VERFALL_BODEN
    anteil: float = boden + (1.0 - boden) / (1.0 + strecke / halbstrecke)

    # ── Ausgabe-Verifikation ────────────────────
    return _in_spanne(wert * anteil, 0.0, wert, "qualitaet_verfall")


def profil_verfallen(
    profil:       dict[str, float],
    tage:         float,
    beruehrungen: int,
) -> dict[str, float]:
    """Wendet den Verfall auf ein ganzes Profil an — je Dimension ihre Regel.

    Die Klammer um `qualitaet_verfall`, damit der Aufrufer die Trennung
    zwischen den beiden Verfallsarten nicht kennen muss und sie nicht auf
    halbem Weg vergessen kann.

    Rein. Nachbedingung: dieselben Schluessel, verfallene Werte.
    """
    return {
        name: qualitaet_verfall(name, wert, tage, beruehrungen)
        for name, wert in (profil or {}).items()
    }


def strangzug(naehe: float | None, faden_zahl: int) -> float:
    """Wie stark eine Praegung diesen **Traeger** anzieht — §10.3a.

        strangzug = 1.0 + HUB * naehe * saettigung(faden_zahl)

    **Nicht zu verwechseln mit dem Praegungszug** (§10.3): Der misst die Lage
    **des Turns** zum Strang und liefert einen Wert je Turn; alle Traeger
    eines Turns bekommen denselben. Dieser hier misst die Lage **des
    Traegers**, und erst damit unterscheidet sich ein Knoten im Zentrum eines
    Strangs von einem an seinem Rand.

    **In der Mitte stark, am Rand schwach** — die Naehe ist das Mass, nicht
    eine Schwelle. Ein Knoten ohne Strangbezug bekommt 1.0: **neutral, nicht
    null.** Regel (a) aus §10.0 gilt hier wie ueberall — eine Null im Produkt
    loeschte auch alles, was der Traeger sonst mitbringt.

    **Die Fadenzahl traegt mit, weil ein starker Strang weiter zieht**, und
    zwar gesaettigt: Vierzig Faeden ziehen nicht vierzigmal so weit wie einer.

    Rein. Vorbedingung: `naehe` in [-1, 1] oder None (kein Strangbezug),
        `faden_zahl` >= 0. Eine negative Naehe bedeutet Gegenlage und zieht
        nicht — sie wird auf 0 gesetzt, nicht gespiegelt.
    Nachbedingung: ein Faktor in [1.0, 1.0 + FASZ_STRANGZUG_HUB].
    """
    # ── Eingabe-Validierung ─────────────────────
    if naehe is None:
        return 1.0
    wert: float = float(naehe)
    if not -1.0 <= wert <= 1.0:
        logger.error(
            f"Faszination: Strangnaehe {wert:.4f} liegt ausserhalb [-1, 1] — "
            f"geklemmt; eine Kosinusnaehe kann das nicht sein"
        )
        wert = max(-1.0, min(1.0, wert))
    if wert <= 0.0:
        # Gegenlage zieht nicht — und sie stoesst auch nicht ab: Der Traeger
        # hat mit dieser Praegung nichts zu tun.
        return 1.0

    # ── Verarbeitung ────────────────────────────
    staerke: float = norm_saettigung(
        max(0, int(faden_zahl)), FASZ_STRANGZUG_HALBSTRECKE_FAEDEN,
    )
    faktor: float = 1.0 + FASZ_STRANGZUG_HUB * wert * staerke

    # ── Ausgabe-Verifikation ────────────────────
    return _in_spanne(
        faktor, 1.0, 1.0 + FASZ_STRANGZUG_HUB, "strangzug",
    )
