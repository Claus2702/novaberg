"""Haltungssprache — von der Zahl zum Wort.

`ei/haltung.py` rechnet fuenf Verhaltensgroessen aus Landschaft und
Zuwendungsrad. Dieses Modul uebersetzt sie in die Woerter, die im Prompt
stehen. Die Trennung ist Absicht: Wer die Rechnung aendert, aendert nicht die
Sprache, und wer ein Wort austauscht, verschiebt keine Zahl.

Konzept: `novaberg-haltungsraum_k.md` §3.0aa (die Baender), §3.0ab (die
Energie). Die Grenzen und Woerter sind **gesetzt, nicht gerechnet** — wie die
Beitragstabellen selbst (§4). Eine Formel, die sie erzeugt, ersetzte die
Landkarte durch eine Gerade.

Drei Regeln aus der Messung vom 12.08.2026 (§3.0):

  * **Die Zahl bindet, das Adjektiv nicht.** Dieselbe Form ohne Mengenangabe
    lieferte 6 Saetze statt 2. Deshalb traegt `umfang` als einzige Groesse
    eine Spanne — und deshalb steht seine Zeile **immer**, auch wenn er nicht
    vom Grundwert abweicht. Eine Regie ohne Zahl ist am 12.08. um das
    Fuenffache verfehlt worden (626 Zeichen statt 120).
  * **Die Spanne gehoert in Zeichen, nicht in Saetze.** "1 bis 2 Saetze"
    bindet und zerstoert dabei den Telegrammstil: Es verlangt *Saetze* und
    bekommt ordentliche Prosa.
  * **Gesprochen wird nur, was abweicht.** Was die Landschaft ohnehin vorgibt,
    steht schon in der Szene; es ein zweites Mal zu sagen fuellt den Prompt
    und verwaessert die Stelle, an der die Regie wirkt.
"""

import logging

from ei.haltung import GROESSEN, Haltung

logger = logging.getLogger("ki_server.ei.haltungssprache")


# ─────────────────────────────────────────────
# Die Baender — Konzept §3.0aa
# ─────────────────────────────────────────────
# Je Groesse fuenf Baender mit ihrer oberen Grenze. Die letzte Grenze liegt
# ueber 1.0, weil `ergebnis` die Zielspanne verlassen darf: Ein Ueberlauf ist
# ein Befund und wird gemeldet, nicht gekappt (`novaberg-haltungsraum_k.md`
# §3.1) — ein Wort braucht er trotzdem, sonst faellt die Zeile genau dort aus,
# wo der Wert am staerksten ist.
#
# **Die Wortzahl traegt die Intensitaet mit.** An den Enden zwei bis drei
# Woerter, in der Mitte eines: Die Verdopplung legt die Schwaeche oder die
# Kraft ins Feld. Bei `fragen` sind die zwei Woerter der mittleren Stufen
# Handwerk statt Steigerung — die Zeile benennt die Groesse nicht, also muss
# jedes Wort seine Achse selbst mitbringen.
#
# **`naehe` und `waerme` haben getrennte Wortfamilien**, und das ist Absicht:
# Man kann vertraut und kuehl sein (alte Ehe) oder fremd und herzlich (guter
# Gastgeber). Aus demselben Wortfeld gespeist, verschmelzen die beiden Achsen.
BAENDER: dict[str, tuple[tuple[float, str], ...]] = {
    "umfang": (
        (0.20, "einsilbig, wortkarg"),
        (0.45, "knapp"),
        (0.70, "gemessen"),
        (0.88, "ausfuehrlich"),
        (99.0, "ausholend, umfangreich"),
    ),
    "fragen": (
        (0.20, "verschlossen, ohne Rueckfrage"),
        (0.45, "sparsam fragend"),
        (0.70, "nachfragend"),
        (0.88, "nachhakend"),
        (99.0, "brennend interessiert"),
    ),
    "naehe": (
        (0.20, "fremd, distanziert, auf Abstand"),
        (0.45, "sachlich"),
        (0.70, "zugewandt"),
        (0.88, "vertraut"),
        (99.0, "ganz nah, unmittelbar"),
    ),
    "waerme": (
        (0.20, "kuehl, nuechtern"),
        (0.45, "verhalten"),
        (0.70, "freundlich"),
        (0.88, "warm"),
        (99.0, "herzlich, innig"),
    ),
    "draengen": (
        (0.20, "abwartend, geduldig"),
        (0.45, "gelassen"),
        (0.70, "anstossend"),
        (0.88, "vorantreibend"),
        (99.0, "draengend"),
    ),
}

# Die Zeichenspanne des Umfangs — dieselben Grenzen wie sein Band.
# **Startwerte**, abgeleitet aus den Laeufen vom 12.08.2026 (»weit« lieferte
# 1011 bis 1384 Zeichen, »karg« 102 bis 166). Sie gehoeren in der ersten Reihe
# nachgezogen und sind deshalb hier und nicht in `haltung.py`: Wer sie
# kalibriert, fasst keine Rechnung an.
UMFANG_SPANNE: tuple[tuple[float, tuple[int, int]], ...] = (
    (0.20, (0, 120)),
    (0.45, (120, 350)),
    (0.70, (350, 700)),
    (0.88, (700, 1400)),
    (99.0, (1400, 2500)),
)

# ─────────────────────────────────────────────
# Die Energie — Konzept §3.0ab
# ─────────────────────────────────────────────
# Arousal gibt **eine** Formulierung ab: mit wieviel Kraft der Charakter
# auftreten darf. Die Laengenvorgabe, die es bis zum 12.08.2026 zusaetzlich
# trug, gehoert `umfang`.
#
# **Die Grenzen sitzen, wo die Verteilung liegt** — vier Stufen unter 0.45, wo
# 56 % der Turns sind, vier darueber. Gemessen ueber 522 Turns: Median 0.334,
# zweigipflig mit Bergen bei 0.1–0.3 und 0.4–0.6. Eine gleichmaessige
# Achteilung haette die Haelfte der Stufen in den leeren Raum gelegt.
#
# Kein Satz spricht ueber Laenge, keiner ueber den Nutzer. Das Erste gehoert
# `umfang`, das Zweite dem Intent.
ENERGIE_STUFEN: tuple[tuple[float, str], ...] = (
    (0.15, "Kaum Energie. Sprich leise und ohne Antrieb — hier draengt nichts."),
    (0.25, "Wenig Energie. Ruhig, ohne Schwung, ohne Aufbau."),
    (0.35, "Gedaempfte Energie. Du bist da, du treibst nichts."),
    (0.45, "Verhaltene Kraft. Wach, aber ohne Zug nach vorn."),
    (0.55, "Mittlere Energie. Bewegung ist erlaubt, Beschleunigung nicht."),
    (0.68, "Spuerbare Energie. Nimm Tempo auf, geh mit."),
    (0.80, "Hohe Energie. Kraft ist erlaubt — klarer Rhythmus, kein Zoegern."),
    (99.0, "Volle Energie. Lass sie fliessen, halte nichts zurueck."),
)

# **Das Band selbst ist das tote Band** (Konzept §3.1). Gesprochen wird, was
# der Landschaft widerspricht — und der Widerspruch ist der **Bandwechsel**,
# nicht ein Abstand in der Zahl.
#
# Die erste Fassung vom 13.08.2026 verglich Zahlen und schwieg unter 0.10
# Differenz. Das verschluckte genau die Faelle, auf die es ankommt: Ein
# hoeflich distanzierter Charakter (`distanz` 0.92) drueckt die Naehe im
# `feuerwerk` von 0.90 auf 0.82 — acht Hundertstel, also stumm, obwohl aus
# »ganz nah« ein »vertraut« geworden ist. Gemessen: Unter der alten Regel bekam
# er **dieselbe** Regie wie Nova und wurde dreimal von drei als sie gelesen.
#
# Gegen das Flattern schuetzt die Diskretisierung selbst: Eine Schwankung
# aendert das Wort nur, wenn der Wert ohnehin auf einer Bandgrenze sitzt — und
# dort sind beide Woerter richtig.


def band(groesse: str, wert: float) -> str:
    """Das Wort, das dieser Wert in seinem Band traegt.

    Vorbedingung: `groesse` steht in `GROESSEN`, `wert` ist nicht negativ.
        Ein unbekannter Name ist ein Aufruffehler und kein leeres Wort — sonst
        verschwaende die Zeile still, sobald jemand eine Groesse umbenennt.
    Nachbedingung: nichtleerer Text.

    Args:
        groesse: Name der Verhaltensgroesse.
        wert:    ihr Ergebnis, ueblicherweise in [0, 1].

    Returns:
        Das Bandwort, zum Beispiel "einsilbig, wortkarg".

    Raises:
        ValueError: bei unbekannter Groesse oder negativem Wert.
    """
    # ── Eingabe-Validierung ─────────────────────
    if groesse not in BAENDER:
        raise ValueError(f"Unbekannte Groesse {groesse!r} — bekannt: {sorted(BAENDER)}")
    if wert < 0.0:
        raise ValueError(f"{groesse}={wert} ist negativ; die Spanne beginnt bei 0.0")

    # ── Verarbeitung ────────────────────────────
    for grenze, wort in BAENDER[groesse]:
        if wert <= grenze:
            return wort

    # ── Ausgabe-Verifikation ────────────────────
    # Unerreichbar, solange das letzte Band bei 99.0 endet. Die Zeile steht
    # trotzdem: Wer die Tabelle kuerzt, bekommt einen Fehler statt einer
    # Funktion, die None zurueckgibt.
    raise ValueError(f"{groesse}={wert} liegt ueber jedem Band")


def zeichenspanne(umfang: float) -> tuple[int, int]:
    """Der Zeichenkorridor, den dieser Umfang verlangt.

    Vorbedingung: `umfang` ist nicht negativ.
    Nachbedingung: Untergrenze < Obergrenze, beide nicht negativ.

    Raises:
        ValueError: bei negativem Wert.
    """
    # ── Eingabe-Validierung ─────────────────────
    if umfang < 0.0:
        raise ValueError(f"umfang={umfang} ist negativ; die Spanne beginnt bei 0.0")

    # ── Verarbeitung ────────────────────────────
    for grenze, spanne in UMFANG_SPANNE:
        if umfang <= grenze:
            return spanne

    raise ValueError(f"umfang={umfang} liegt ueber jeder Spanne")


def energiesatz(arousal: float) -> str:
    """Der Energiesatz zu dieser Erregung.

    Vorbedingung: `arousal` liegt in [0, 1]. Ein Wert daneben ist ein
        Aufruffehler: Die Stufen sind auf die gemessene Verteilung gelegt, und
        ausserhalb ihrer Spanne beschreiben sie nichts.
    Nachbedingung: nichtleerer Satz.

    Raises:
        ValueError: wenn `arousal` die Spanne verlaesst.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not 0.0 <= arousal <= 1.0:
        raise ValueError(f"arousal={arousal} liegt ausserhalb von [0, 1]")

    # ── Verarbeitung ────────────────────────────
    for grenze, satz in ENERGIE_STUFEN:
        if arousal < grenze:
            return satz

    raise ValueError(f"arousal={arousal} liegt ueber jeder Stufe")


def regie_zeilen(haltung: Haltung, arousal: float) -> list[str]:
    """Die Regie fuer diesen Turn: Umfang, abweichende Haltung, Energie.

    **Der Umfang steht immer, die vier anderen nur bei Abweichung.** Das ist
    keine Inkonsequenz, sondern der Unterschied zwischen einer Vorgabe, die
    bindet, und einer, die faerbt: Ohne Mengenangabe verfehlte dieselbe Form
    am 12.08.2026 den Korridor um das Fuenffache, waehrend die Haltungswoerter
    das, was die Landschaft ohnehin vorgibt, nur wiederholen wuerden.

    Vorbedingung: `haltung` traegt jede Groesse aus `GROESSEN`. Eine fehlende
        ist ein Aufruffehler — eine stumm ausgelassene Zeile waere von einer
        Groesse ohne Abweichung nicht zu unterscheiden.
    Nachbedingung: Zwei Zeilen (Umfang und Energie) oder drei, wenn mindestens
        eine Groesse abweicht. Die Reihenfolge ist fest: Umfang, Haltung,
        Energie — die Zahl zuerst, weil sie bindet, die Energie zuletzt.
    Fehlerfaelle: Ein Ergebnis ausserhalb der Zielspanne bekommt sein Wort und
        eine Logzeile — gekappt wird nicht (§3.1).

    Args:
        haltung: das Ergebnis der Haltungsrechnung dieses Turns.
        arousal: die Erregung des Turns, aus der Perzeption.

    Returns:
        Zwei bis vier Zeilen fuer den `[REGIE]`-Block.

    Raises:
        ValueError: bei unvollstaendiger Haltung oder ungueltigem Arousal.
    """
    # ── Eingabe-Validierung ─────────────────────
    fehlend: list[str] = [name for name in GROESSEN if name not in haltung.werte]
    if fehlend:
        raise ValueError(
            f"Haltung unvollstaendig — es fehlen: {', '.join(fehlend)}"
        )

    # ── Verarbeitung ────────────────────────────
    umfang = haltung.werte["umfang"]
    unten, oben = zeichenspanne(umfang.ergebnis)
    zeilen: list[str] = [
        f"Umfang: {unten} bis {oben} Zeichen — {band('umfang', umfang.ergebnis)}."
    ]

    # Die vier uebrigen, sofern sie der Landschaft widersprechen. `umfang` ist
    # hier ausgenommen: Seine Zahl steht schon oben, und sein Wort mit ihr.
    gesprochen: list[str] = []
    for name in GROESSEN:
        if name == "umfang":
            continue
        wert = haltung.werte[name]
        # Der Bandwechsel entscheidet — die Begruendung steht bei der Tabelle.
        wort: str = band(name, wert.ergebnis)
        if wort == band(name, wert.grundwert):
            continue
        gesprochen.append(wort)
        if wert.ausserhalb:
            logger.warning(
                "Haltungssprache: %s=%.2f verlaesst die Zielspanne — das Wort "
                "%r steht trotzdem, gekappt wird nicht (Konzept §3.1)",
                name, wert.ergebnis, band(name, wert.ergebnis),
            )

    if gesprochen:
        zeilen.append(" · ".join(gesprochen))

    zeilen.append(f"Energie: {energiesatz(arousal)}")

    # ── Ausgabe-Verifikation ────────────────────
    if not 2 <= len(zeilen) <= 3:
        raise ValueError(
            f"Regie mit {len(zeilen)} Zeilen — erwartet sind zwei oder drei"
        )

    logger.info(
        "Haltungssprache: Regie aus %s — %d von 4 Groessen sprechen "
        "(Umfang %d-%d Zeichen)",
        haltung.cluster, len(gesprochen), unten, oben,
    )
    return zeilen
