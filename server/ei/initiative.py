"""Initiative: wer im aktuellen Turn die Richtung setzt.

Fuehren heisst, eine Richtung zu setzen. Mitgehen ist keine Fuehrung, auch
nicht mit Tiefe. Drei Formen setzen eine Richtung, und jede hat ihr Mass:

  M1 Wollen     — die Frage, die eine Information verlangt (Intentionen)
  M2 Thema      — der Themenwechsel (Embedding-Abstand zur Vorantwort)
  M3 Register   — tiefer eintauchen oder zurueckgehen (Weg auf der Tiefe-Skala)

**Warum nicht die Turn-Laenge.** Die abgeloeste Achse verglich die
durchschnittliche Zeichenzahl beider Seiten gegen eine Schwelle von 1.5.
Gemessen ueber 15 Laeufe stand sie 15 Mal auf demselben Wert: Der Nutzer
schreibt 51 Zeichen je Turn, Nova 433 — fuer ein Verhaeltnis von 1.5 muesste
er das 12,6-fache schreiben. 32 der 64 Sektoren waren damit nicht selten,
sondern unerreichbar.

**Warum je Dimension gewichtet und nicht je Mass.** M2 und M3 stimmen je Turn
zu 72,7 % ueberein — wer das Thema wechselt, wechselt meist auch das Register.
M1 ist von beiden unabhaengig (55,6 % und 48,1 %, Zufall liegt bei 50 %).
Gleichgewichtung je Mass gaebe der redundanten Paarung stillschweigend zwei
Drittel. Deshalb: Bewegung = Mittel(M2, M3) als eine Stimme, Wollen = M1 als
zweite.

**Kein Mass wird still auf null gesetzt.** Fehlt eine Quelle, traegt das
Ergebnis ihren Namen in `fehlend` und die Rechnung laeuft mit den uebrigen.
Ein Rohwert aus zwei Massen ist etwas anderes als einer aus dreien, und der
Unterschied muss am Ergebnis ablesbar sein.

Konzept: novaberg-gv-initiative_k.md
"""

import logging
from dataclasses import dataclass, field

from config import (
    GV_INITIATIVE_FUEHREND,
    GV_INITIATIVE_M2_THEMA,
    GV_INITIATIVE_M3_REGISTER,
    GV_INITIATIVE_SCHWELLE,
    GV_INITIATIVE_VERSATZ,
    GV_INITIATIVE_VERSATZ_MAX,
    GV_TIEFE_MODUS,
)
from ei.utils import modus_pruefen

logger = logging.getLogger("ki_server.ei.initiative")


@dataclass
class Fuehrung:
    """Das Ergebnis der Initiative-Messung eines Turns.

    Alle Werte entstehen aus derselben Rechnung, werden zusammen erzeugt und
    zusammen weitergereicht — deshalb eine Klasse und keine flachen Felder
    (Handbuch §6).

    Die drei `*_roh`-Werte tragen die Messung in ihrer eigenen Einheit, die
    zwei Dimensionen die auf [-1, +1] normierte Fassung. `rohwert` ist ihr
    Mittel, `wert` derselbe Wert nach dem Charakter-Versatz. Getrennt, damit
    am Panel ablesbar bleibt, was gemessen wurde und was der Charakter daraus
    gemacht hat.

    `fehlend` nennt die Masse, deren Quelle im Turn nicht vorlag. Ist die
    Liste leer, stehen alle drei; ist sie voll, ist `wert` None und die Achse
    hat nichts zu sagen.
    """

    m1_roh:   int | None   = None   # 1 = fuehrende Intention vorhanden
    m2_roh:   float | None = None   # Cosinus-Abstand zur Vorantwort
    m3_roh:   float | None = None   # Weg auf der Tiefe-Skala

    wollen:   float | None = None   # M1 normiert, [-1, +1]
    bewegung: float | None = None   # Mittel(M2, M3) normiert, [-1, +1]

    rohwert:  float | None = None   # Mittel(bewegung, wollen)
    versatz:  float        = 0.0    # Charakter-Versatz
    wert:     float | None = None   # rohwert + versatz, gekappt

    fehlend:  list[str]    = field(default_factory=list)


def skalenfassung(
    schwelle:      float = GV_INITIATIVE_SCHWELLE,
    quelle:        str   = "default",
    kalibriert_am: str   = "",
) -> dict:
    """Liefert die Skala, die einen Achsenwert gerade lesbar macht.

    **Warum das mitgeschrieben werden muss.** Sobald der Kalibrier-Agent die
    Schwelle je Paar erhebt, wandert der Massstab mit dem Gemessenen. Ein
    Rohwert von -0.30 heisst bei Schwelle -0.45 „der Nutzer fuehrt" und bei
    Schwelle -0.20 das Gegenteil. Steht im Protokoll nur der Rohwert, ist nach
    einigen Kalibrierungen nicht mehr trennbar, ob sich Nova bewegt hat oder
    die Skala — die Reihe ist dann nicht auswertbar. Dieselbe Fehlerklasse wie
    ein Ausfallwert, der aussieht wie eine Messung, nur ueber die Zeit statt
    ueber einen einzelnen Wert.

    Die Fassung steht deshalb an **einer** Stelle: Wer den Achsenwert
    protokolliert, holt sie hier und kann sie nicht anders zusammensetzen als
    die Rechnung selbst.

    Vorbedingung: `schwelle` liegt in [-1, +1].
    Nachbedingung: Ein flaches Dict, JSON-serialisierbar, mit Schwelle, den
    Spannen beider Bewegungsmasse, der Versatz-Grenze, der Herkunft und dem
    Zeitpunkt der Erhebung.
    Fehlerfaelle: Schwelle ausserhalb des Wertebereichs — laut gemeldet, die
    Fassung wird trotzdem gebaut: Ein Protokolleintrag mit einer auffaelligen
    Schwelle ist mehr wert als keiner.

    Returns:
        Die Skalenfassung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not -1.0 <= schwelle <= 1.0:
        logger.error(
            "Initiative: Skalenfassung mit Schwelle %.3f ausserhalb [-1, +1] — "
            "protokolliert, aber der Wert ist nicht plausibel", schwelle,
        )

    # ── Verarbeitung ────────────────────────────
    fassung: dict = {
        "schwelle":      round(schwelle, 3),
        "quelle":        quelle,
        "kalibriert_am": kalibriert_am,
        "m2_zentrum":    GV_INITIATIVE_M2_THEMA["zentrum"],
        "m2_min":        GV_INITIATIVE_M2_THEMA["min"],
        "m2_max":        GV_INITIATIVE_M2_THEMA["max"],
        "m3_zentrum":    GV_INITIATIVE_M3_REGISTER["zentrum"],
        "m3_min":        GV_INITIATIVE_M3_REGISTER["min"],
        "m3_max":        GV_INITIATIVE_M3_REGISTER["max"],
        "versatz_max":   GV_INITIATIVE_VERSATZ_MAX,
    }

    # ── Ausgabe ─────────────────────────────────
    return fassung


def initiative_bit(wert: float, schwelle: float) -> int:
    """Binarisiert den Initiative-Wert an einer Schwelle.

    Bit **0** heisst „Nutzer fuehrt", Bit **1** „gleich oder Nova". Verglichen
    wird strikt groesser: Wer genau auf der Schwelle liegt, fuehrt nicht.

    Die Regel steht hier und nur hier. Die Achse (`achsen_berechnen`) und die
    Kalibrierung (`ei/kalibrierung.py`) rufen dieselbe Funktion — eine zweite
    Kopie waere die Stelle, an der beide spaeter auseinanderlaufen, ohne dass
    es auffiele: Die Kalibrierung suchte dann eine Schwelle fuer eine
    Binarisierung, die es zur Laufzeit nicht gibt.

    Vorbedingung: `wert` in [-1, +1], `schwelle` im selben Bereich.
    Nachbedingung: 0 oder 1.
    Fehlerfaelle: Keine — ein Wert ausserhalb des Bereichs ist ein Turn
    jenseits des Korpus und wird trotzdem binarisiert; die Kappung sitzt in
    `fuehrung_messen`.

    Returns:
        0 (Nutzer fuehrt) oder 1 (gleich oder Nova).
    """
    # ── Eingabe-Validierung ─────────────────────
    # Keine: Beide Argumente sind Zahlen, jede Kombination ist entscheidbar.

    # ── Verarbeitung ────────────────────────────
    bit: int = 0 if wert > schwelle else 1

    # ── Ausgabe ─────────────────────────────────
    return bit


def _normieren(wert: float, skala: dict[str, float]) -> float:
    """Bildet einen Messwert auf [-1, +1] ab, Zentrum auf 0.

    Die Abbildung ist bewusst **asymmetrisch**: Sie normiert nach unten gegen
    den Abstand zum beobachteten Minimum, nach oben gegen den zum Maximum.
    Bei M3 liegt das Zentrum (0.100) sehr nahe am Minimum (0.000) und weit vom
    Maximum (0.600) — eine symmetrische Normierung wuerde die untere Haelfte
    der Skala auf ein Fuenftel stauchen und damit ein Mass erfinden, das die
    Daten nicht hergeben.

    Vorbedingung: `skala` traegt 'zentrum', 'min' und 'max', und die Spannen
    zu beiden Seiten sind groesser als null.
    Nachbedingung: Rueckgabe in [-1, +1]; das Zentrum bildet auf 0.0 ab.
    Fehlerfaelle: Entartete Skala (Spanne null) — dann ist keine Normierung
    moeglich, das wird laut gemeldet und 0.0 zurueckgegeben.

    Returns:
        Der normierte Wert.
    """
    # ── Eingabe-Validierung ─────────────────────
    zentrum: float = skala["zentrum"]
    unten:   float = zentrum - skala["min"]
    oben:    float = skala["max"] - zentrum

    if unten <= 0 or oben <= 0:
        logger.error(
            "Initiative: entartete Skala (zentrum=%.3f, min=%.3f, max=%.3f) — "
            "keine Normierung moeglich",
            zentrum, skala["min"], skala["max"],
        )
        return 0.0

    # ── Verarbeitung ────────────────────────────
    if wert >= zentrum:
        norm: float = (wert - zentrum) / oben
    else:
        norm = (wert - zentrum) / unten

    # ── Ausgabe-Verifikation ────────────────────
    # Ein Wert ausserhalb der erhobenen Spanne ist kein Fehler, sondern ein
    # Turn jenseits des Korpus. Er wird gekappt, nicht verworfen.
    return max(-1.0, min(1.0, norm))


def _wollen_messen(state: dict) -> int | None:
    """M1 — traegt der Turn eine Intention, die eine Richtung setzt?

    Quelle ist `user_intentionen` aus dem State, also die Perzeption des
    aktuellen Nutzer-Turns. Fuehrend sind Frage, Rueckfrage, Anweisung,
    Widerspruch und Themenwechsel (GV_INITIATIVE_FUEHREND).

    Vorbedingung: keine.
    Nachbedingung: 1 oder 0, wenn Intentionen vorlagen; sonst None.
    Fehlerfaelle: Keine Intentionen im State — das ist ein legitimer Leerfall
    (Perzeption ohne Intentionsschicht) und wird als None gemeldet, nicht als
    0 verrechnet.

    Returns:
        1 (fuehrend), 0 (folgend) oder None (nicht messbar).
    """
    # ── Eingabe-Validierung ─────────────────────
    intentionen: list = state.get("user_intentionen") or []
    if not intentionen:
        return None

    # ── Verarbeitung ────────────────────────────
    ausserhalb: list[str] = [
        i for i in intentionen if not isinstance(i, str)
    ]
    if ausserhalb:
        logger.error(
            "Initiative: Intentionen mit unerwartetem Typ verworfen: %s",
            ausserhalb,
        )

    treffer: set = GV_INITIATIVE_FUEHREND & {i for i in intentionen if isinstance(i, str)}

    # ── Ausgabe-Verifikation ────────────────────
    return 1 if treffer else 0


def _register_messen(state: dict, vorher_modus: str) -> float | None:
    """M3 — wie weit bewegt der Nutzer das Register gegenueber der Vorantwort?

    Weg auf der Tiefe-Skala GV_TIEFE_MODUS zwischen dem Modus der Vorantwort
    und dem des aktuellen Nutzer-Turns. Tiefer eintauchen und zurueckgehen
    zaehlen gleich — gemessen wird der Betrag, nicht die Richtung.

    Vorbedingung: `vorher_modus` ist der Modus des letzten Nova-Turns.
    Nachbedingung: Betrag in [0, 0.6], wenn beide Modi im Kanon liegen.
    Fehlerfaelle: Ein Modus ausserhalb des Kanons — dann ist der Abstand nicht
    berechenbar. Das wird ueber `modus_pruefen` laut gemeldet und als None
    zurueckgegeben, nicht als 0 (was 'kein Wechsel' hiesse).

    Returns:
        Der Betrag des Registerwegs oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    external = state.get("external")
    jetzt_modus: str = external.emotion.mode if external else ""

    if not jetzt_modus or not vorher_modus:
        return None

    modus_pruefen(jetzt_modus, "Initiative M3 (Nutzer-Turn)")
    modus_pruefen(vorher_modus, "Initiative M3 (Vorantwort)")

    if jetzt_modus not in GV_TIEFE_MODUS or vorher_modus not in GV_TIEFE_MODUS:
        return None

    # ── Verarbeitung ────────────────────────────
    weg: float = abs(GV_TIEFE_MODUS[jetzt_modus] - GV_TIEFE_MODUS[vorher_modus])

    # ── Ausgabe-Verifikation ────────────────────
    if weg < 0.0:
        logger.error("Initiative: negativer Registerweg %.3f — verworfen", weg)
        return None

    return round(weg, 3)


def _thema_messen(state: dict, vorher_embedding: list[float] | None) -> float | None:
    """M2 — wie weit bewegt der Nutzer das Thema gegenueber der Vorantwort?

    Cosinus-Abstand zwischen dem Embedding des aktuellen Nutzer-Prompts
    (`prompt_embedding`, vom Enricher gesetzt) und dem der letzten Nova-
    Antwort. Beide sind Rohtext-Embeddings, keine Verdichtungen: Die
    Verdichtung ist bereits eine Deutung, und wer den Themensprung darauf
    misst, misst die Bewegung der Zusammenfassung.

    Vorbedingung: beide Vektoren gleich lang und normiert (der EmbedWorker
    liefert normierte Vektoren).
    Nachbedingung: Abstand in [0, 2]; praktisch beobachtet 0.29 bis 0.98.
    Fehlerfaelle: Ein Vektor fehlt (erster Turn eines Paars) — legitimer
    Leerfall, None. Ungleiche Laenge — Defekt, laut gemeldet, None.

    Returns:
        Der Cosinus-Abstand oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    jetzt = state.get("prompt_embedding")
    if not jetzt or not vorher_embedding:
        return None

    if len(jetzt) != len(vorher_embedding):
        logger.error(
            "Initiative: Embedding-Laengen weichen ab (%d gegen %d) — "
            "M2 nicht berechenbar",
            len(jetzt), len(vorher_embedding),
        )
        return None

    # ── Verarbeitung ────────────────────────────
    skalar: float = sum(a * b for a, b in zip(jetzt, vorher_embedding))
    abstand: float = 1.0 - skalar

    # ── Ausgabe-Verifikation ────────────────────
    if not (-0.01 <= abstand <= 2.01):
        logger.error(
            "Initiative: Cosinus-Abstand %.3f ausserhalb [0, 2] — die Vektoren "
            "sind vermutlich nicht normiert; M2 verworfen", abstand,
        )
        return None

    return round(abstand, 3)


def fuehrung_messen(
    state:            dict,
    vorher_embedding: list[float] | None = None,
    vorher_modus:     str = "",
    versatz:          float = GV_INITIATIVE_VERSATZ,
) -> Fuehrung:
    """Misst, wer im aktuellen Turn die Richtung setzt.

    Rechnet die drei Masse, normiert jedes auf sein eigenes Zentrum und fasst
    sie je Dimension zusammen: Bewegung (Thema + Register) und Wollen. Der
    Charakter-Versatz verschiebt anschliessend den Rohwert.

    Vorbedingung: `state` traegt `external` und optional `prompt_embedding`
    und `user_intentionen`. `vorher_embedding` und `vorher_modus` stammen aus
    dem letzten Nova-Turn desselben Paars; fehlen sie, ist das der erste Turn.
    Nachbedingung: Die zurueckgegebene `Fuehrung` traegt fuer jedes nicht
    messbare Mass dessen Namen in `fehlend`. `wert` ist None genau dann, wenn
    kein einziges Mass vorlag.
    Fehlerfaelle: Alle drei Masse fehlen — dann hat die Achse nichts zu sagen,
    was laut gemeldet wird. Ein Versatz ausserhalb der Grenze wird gekappt und
    gemeldet.

    Returns:
        Die gemessene Fuehrung.
    """
    # ── Eingabe-Validierung ─────────────────────
    f = Fuehrung()

    if abs(versatz) > GV_INITIATIVE_VERSATZ_MAX:
        logger.error(
            "Initiative: Charakter-Versatz %.3f ausserhalb +/-%.2f — gekappt",
            versatz, GV_INITIATIVE_VERSATZ_MAX,
        )
        versatz = max(-GV_INITIATIVE_VERSATZ_MAX,
                      min(GV_INITIATIVE_VERSATZ_MAX, versatz))
    f.versatz = versatz

    # ── Verarbeitung ────────────────────────────
    f.m1_roh = _wollen_messen(state)
    f.m2_roh = _thema_messen(state, vorher_embedding)
    f.m3_roh = _register_messen(state, vorher_modus)

    if f.m1_roh is None:
        f.fehlend.append("wollen")
    else:
        f.wollen = 1.0 if f.m1_roh else -1.0

    bewegungs_teile: list[float] = []
    if f.m2_roh is None:
        f.fehlend.append("thema")
    else:
        bewegungs_teile.append(_normieren(f.m2_roh, GV_INITIATIVE_M2_THEMA))
    if f.m3_roh is None:
        f.fehlend.append("register")
    else:
        bewegungs_teile.append(_normieren(f.m3_roh, GV_INITIATIVE_M3_REGISTER))

    if bewegungs_teile:
        f.bewegung = round(sum(bewegungs_teile) / len(bewegungs_teile), 3)

    # Je Dimension, nicht je Mass: Bewegung und Wollen zaehlen gleich, auch
    # wenn Bewegung aus zwei Messungen entsteht. Faellt eine Dimension ganz
    # aus, traegt die andere allein — das ist besser als ein erfundener
    # Nullwert, aber es steht in `fehlend`.
    dimensionen: list[float] = [
        d for d in (f.bewegung, f.wollen) if d is not None
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if not dimensionen:
        logger.error(
            "Initiative: kein einziges Mass verfuegbar (fehlend: %s) — "
            "die Achse hat fuer diesen Turn nichts zu sagen", f.fehlend,
        )
        return f

    f.rohwert = round(sum(dimensionen) / len(dimensionen), 3)
    f.wert = round(max(-1.0, min(1.0, f.rohwert + f.versatz)), 3)

    logger.info(
        "Initiative: wert=%.3f (roh=%.3f, versatz=%+.2f) — "
        "wollen=%s bewegung=%s [M1=%s M2=%s M3=%s]%s",
        f.wert, f.rohwert, f.versatz,
        f"{f.wollen:+.1f}" if f.wollen is not None else "—",
        f"{f.bewegung:+.3f}" if f.bewegung is not None else "—",
        f.m1_roh if f.m1_roh is not None else "—",
        f"{f.m2_roh:.3f}" if f.m2_roh is not None else "—",
        f"{f.m3_roh:.3f}" if f.m3_roh is not None else "—",
        f" fehlend={f.fehlend}" if f.fehlend else "",
    )
    return f
