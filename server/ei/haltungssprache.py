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
#
# **Am 20.08.2026 halbiert.** Der Anlass ist ein Befund aus dem Betrieb: Auf
# einen Gruss von zwoelf Zeichen kamen 838 Zeichen zurueck, bei einem Korridor
# von 350 bis 700. Die Entscheidung ist eine Setzung des Meisters und keine
# Messung — sie gilt fuer jede Landschaft gleich, weil der Befund an der
# Groessenordnung haengt und nicht an einem einzelnen Raum.
#
# **Was die Halbierung nicht leistet:** Die Vorgabe bindet nur schwach. Am
# 17.08.2026 ueber zehn Turns gemessen streute die Antwortlaenge bei
# IDENTISCHER Vorgabe um den Faktor 2,68 (813 bis 2181 Zeichen); die Richtung
# stimmt mit r = +0,78, die Bindung fehlt. Halbierte Korridore halbieren die
# Antworten deshalb nicht — sie verschieben sie.
UMFANG_SPANNE: tuple[tuple[float, tuple[int, int]], ...] = (
    (0.20, (0, 60)),
    (0.45, (60, 175)),
    (0.70, (175, 350)),
    (0.88, (350, 700)),
    (99.0, (700, 1250)),
)

# ─────────────────────────────────────────────
# Der dritte Einfluss: die Laenge der Aeusserung
# ─────────────────────────────────────────────
# Der Raum sagt, wieviel Nova hier ueberhaupt redet; der Korridor uebersetzt
# das in Zeichen. Beides steht fest, bevor der Turn da ist — und deshalb
# bekommt ein Gruss von zwoelf Zeichen dieselbe Vorgabe wie ein Absatz.
#
# **Die Laenge allein taugt nicht als Mass.** *„Erklaere mir die
# Tritiumvorkommen"* ist kurz und verlangt trotzdem eine Antwort in
# Sachlaenge. Was die beiden Faelle trennt, ist nicht die Zeichenzahl,
# sondern die **Intention**: Am 20.08.2026 im Betrieb gemessen trug
# *„Hey Kleines!"* die Intention `smalltalk`, *„Wie entsteht bei einem
# Gammablitz…"* trug `information_erfragen`.
#
# Der Abschlag greift deshalb nur, wenn der Turn **ausschliesslich** leichte
# Intentionen traegt. Eine einzige inhaltliche darunter setzt ihn aus — und
# ein Turn ohne erhobene Intention ebenso: Eine fehlende Erhebung ist keine
# Erlaubnis zu kuerzen.
LEICHTE_INTENTIONEN: frozenset[str] = frozenset({
    "smalltalk", "bestaetigung", "abschluss", "humor",
})

#: Wieviel Text eine leichte Aeusserung nach sich ziehen darf, als Vielfaches
#: ihrer eigenen Laenge, und der Sockel, unter den der Deckel nie faellt.
#: **Startwerte ohne Messung** — dieselbe Sorte Zahl wie `UMFANG_SPANNE` bei
#: ihrer Einfuehrung, und sie gehoeren genauso nachgezogen. Gewaehlt so, dass
#: der Deckel oberhalb von rund 30 Zeichen Aeusserung nicht mehr greift: Ab
#: dort traegt der Korridor der Landschaft allein.
LEICHT_FAKTOR: int = 12
LEICHT_SOCKEL: int = 80

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


def spanne_fuer_turn(
    umfang: float, reiz_zeichen: int, intentionen: tuple[str, ...],
) -> tuple[int, int]:
    """Der Zeichenkorridor dieses Turns — Raum, Korridor und Aeusserung.

    Drei Einfluesse an drei Stellen: Die Landschaft setzt `umfang`, die
    Tabelle uebersetzt ihn in Zeichen, und diese Funktion legt den Bezug zur
    Aeusserung darueber. Der dritte gehoert hierher und nicht in die
    Haltungsrechnung: `haltung_berechnen` ist eine reine Funktion aus
    Landschaft und Zuwendungsrad und sagt, **wer Nova hier ist**; wieviel
    Text ein einzelner Turn verlangt, ist eine Frage an den Turn.

    **Der Abschlag wirkt nur nach unten und nur bei leichten Turns.** Er
    greift, wenn der Turn mindestens eine Intention traegt und **alle**
    davon in `LEICHTE_INTENTIONEN` stehen. Eine inhaltliche darunter setzt
    ihn aus — *„Erklaere mir die Tritiumvorkommen"* ist kurz und verlangt
    trotzdem Sachlaenge. Ein Turn ohne erhobene Intention bleibt ebenfalls
    unberuehrt: Eine fehlende Erhebung ist keine Erlaubnis zu kuerzen.

    Vorbedingung: `umfang` ist nicht negativ, `reiz_zeichen` ist nicht
        negativ, `intentionen` sind Zeichenketten.
    Nachbedingung: Untergrenze < Obergrenze, beide nicht negativ, und beide
        hoechstens so gross wie ohne den Abschlag.
    Fehlerfaelle: negative Werte (ValueError) — beide waeren ein Aufruffehler
        und keine Lage.

    Args:
        umfang: die Haltungsgroesse dieses Turns.
        reiz_zeichen: Laenge der Nutzeraeusserung in Zeichen.
        intentionen: die erhobenen Intentionen des Turns.

    Returns:
        Untergrenze und Obergrenze in Zeichen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if reiz_zeichen < 0:
        meldung: str = f"spanne_fuer_turn: reiz_zeichen={reiz_zeichen} ist negativ"
        raise ValueError(meldung)

    unten, oben = zeichenspanne(umfang)

    # ── Verarbeitung ────────────────────────────
    leicht: bool = bool(intentionen) and all(
        art in LEICHTE_INTENTIONEN for art in intentionen
    )
    if leicht:
        deckel: int = max(LEICHT_SOCKEL, reiz_zeichen * LEICHT_FAKTOR)
        if deckel < oben:
            oben = deckel
            unten = min(unten, oben // 2)

    # ── Ausgabe-Verifikation ────────────────────
    roh_unten, roh_oben = zeichenspanne(umfang)
    if not 0 <= unten < oben:
        meldung = (
            f"spanne_fuer_turn: Korridor {unten} bis {oben} ist keine Spanne "
            f"(umfang={umfang}, reiz_zeichen={reiz_zeichen})"
        )
        raise ValueError(meldung)
    if unten > roh_unten or oben > roh_oben:
        meldung = (
            f"spanne_fuer_turn: Korridor {unten} bis {oben} liegt ueber dem "
            f"der Landschaft ({roh_unten} bis {roh_oben}) — der Abschlag darf "
            f"nur nach unten wirken"
        )
        raise ValueError(meldung)

    return unten, oben


# ─────────────────────────────────────────────
# Die fachliche Seite der Haltung — fuer den Verfasser
# ─────────────────────────────────────────────
# **Drei der fuenf Groessen betreffen den Inhalt, nicht den Ton.** Der
# Verfasser bestimmt laut seinem Auftrag, *„was sie feststellt, was sie offen
# laesst, was sie zurueckfragt"* — also genau `fragen` und `draengen`; und das
# Konzept sagt zum dritten woertlich: der Verfasser liest, *wie viel es zu
# sagen gibt*, der Responder, *wie viel davon sie sagt*
# (`novaberg-haltungsraum_k.md`, »Wer rechnet«).
#
# **`naehe` und `waerme` stehen hier nicht** und gehoeren auch nicht hierher:
# Sie sind reiner Ton, und ihn ein zweites Mal zu nennen waere die Doppelung,
# die der Umbau vom 13.08.2026 an anderer Stelle beseitigt hat.
#
# **Die Woerter sind andere als in `BAENDER`, die Grenzen dieselben.** Der
# Responder liest, wie eine Rueckfrage klingt; der Verfasser entscheidet, ob
# eine im Stoff vorkommt. Dieselbe Zahl, zwei Aufgaben, zwei Formulierungen —
# eine gemeinsame Wortliste haette eine der beiden Rollen falsch bedient.
STOFF_BAENDER: dict[str, tuple[tuple[float, str], ...]] = {
    "fragen": (
        (0.20, "keine Rueckfrage"),
        (0.45, "hoechstens eine kurze Rueckfrage"),
        (0.70, "eine Rueckfrage"),
        (0.88, "eine Rueckfrage, die nachhakt"),
        (99.0, "mehrere Rueckfragen"),
    ),
    "draengen": (
        (0.20, "kein Vorschlag, nichts anschieben"),
        (0.45, "hoechstens ein Hinweis"),
        (0.70, "ein Vorschlag ist erlaubt"),
        (0.88, "ein Vorschlag gehoert hinein"),
        (99.0, "ein Vorschlag und der naechste Schritt dazu"),
    ),
}


def stoff_band(groesse: str, wert: float) -> str:
    """Das inhaltliche Wort zu einer der fachlichen Groessen.

    Vorbedingung: `groesse` steht in `STOFF_BAENDER`, `wert` ist nicht negativ.
    Nachbedingung: nichtleeres Wort.
    Fehlerfaelle: unbekannte Groesse oder ein Wert ueber jedem Band
        (ValueError) — beides waere ein Aufruffehler und kein Zustand.
    """
    # ── Eingabe-Validierung ─────────────────────
    if groesse not in STOFF_BAENDER:
        meldung: str = (
            f"stoff_band: {groesse!r} ist keine fachliche Groesse — bekannt "
            f"sind {sorted(STOFF_BAENDER)}"
        )
        raise ValueError(meldung)
    if wert < 0.0:
        meldung = f"stoff_band: {groesse}={wert} ist negativ"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    for grenze, wort in STOFF_BAENDER[groesse]:
        if wert <= grenze:
            return wort

    meldung = f"stoff_band: {groesse}={wert} liegt ueber jedem Band"
    raise ValueError(meldung)


# Das unterste Band von `fragen`, aus der Tabelle gezogen statt getippt: Ein
# zweiter Wortlaut wuerde beim naechsten Umformulieren still falsch.
KEINE_RUECKFRAGE: str = STOFF_BAENDER["fragen"][0][1]


def _rueckfragenzeile(haltung: Haltung, gegenstand: str | None = None) -> str:
    """Die Rueckfrage-Zeile — Menge, Art UND Gegenstand, in einer Zeile.

    **Der Gegenstand kam am 28.08.2026 dazu (Scheibe 3 des Lage-Konzepts).**
    Menge und Art allein erzeugten weiter Floskeln: 2,2 Fragen je Turn,
    100 % Frage-Enden, und auf »Licht oder Wasser?« kamen vier Rueckfragen
    ohne Antwort. Der Gegenstand ist die wichtigste offene Eigenschaft eines
    akuten Objekts der Sachlage oder das Vorhaben des kurzfristigen Ziels
    (`graph/nodes/sachlage.py::question_target`). **Die Haltung bleibt der
    Regler:** Bei »keine Rueckfrage« entfaellt er wie die Art — die Lage
    erzeugt keine Frage an der Haltung vorbei.

    **Die Art stand bis zum 27.08.2026 nirgends im Auftrag des Verfassers.**
    Sie lag in `CLUSTER_FRAGE_ART` und lief ausschliesslich in den
    Strategie-Prompt des GV-Knotens. Der Knoten, der die Frage **schreibt**,
    bekam nur die Menge — und wer eine Menge bestellt und sonst nichts,
    greift zur Form, die zugleich die Vorschlagsvorgabe erledigt. Gemessen an
    84 Schlussfragen des produktiven Paares: 33 % beginnen als Angebot
    (»Sollen wir …«), 23 % zusaetzlich mit »oder«, neunzehn auf demselben
    Satzgeruest.

    **Sie haengt ausdruecklich NICHT am Vehikel `frage`.** Der erste Versuch
    desselben Tages tat das — und traf damit ein Feld, das im Betrieb meistens
    leer ist: ueber 610 GV-Parses stand `Vehikel` in **456** Faellen (75 %)
    auf nichts, `frage` in 53 (9 %). Eine Vorgabe, die in jedem elften Turn
    ankommt, ist keine. Die Landschaft dagegen steht immer.

    **Bei »keine Rueckfrage« entfaellt die Art**, denn dann gibt es keine
    Frage, die eine Art haben koennte.

    Vorbedingung: `haltung` traegt `fragen` und einen Cluster mit Eintrag in
        `CLUSTER_FRAGE_ART`; `gegenstand` ist ein Satzstueck oder None.
    Nachbedingung: eine Zeile, die mit "Rueckfrage: " beginnt; mit
        Gegenstand endet sie auf »ihr Gegenstand: …«.
    Fehlerfaelle: fehlender Cluster-Eintrag — laute Warnung, Menge allein.
        Ein stilles Weglassen waere von "keine Rueckfrage" nicht zu
        unterscheiden.
    """
    from ei.dreischicht import CLUSTER_FRAGE_ART

    menge: str = stoff_band("fragen", haltung.werte["fragen"].ergebnis)
    if menge == KEINE_RUECKFRAGE:
        return f"Rueckfrage: {menge}."

    anhang: str = f" — ihr Gegenstand: {gegenstand}" if gegenstand else ""
    art: str = CLUSTER_FRAGE_ART.get(haltung.cluster, "")
    if not art:
        logger.warning(
            f"_rueckfragenzeile: Landschaft '{haltung.cluster}' ohne "
            f"hinterlegte Frage-Art — die Frage entsteht ohne Vorgabe"
        )
        return f"Rueckfrage: {menge}{anhang}."
    return f"Rueckfrage: {menge}, und zwar {art}{anhang}."


def stoffzeilen(
    haltung: Haltung, reiz_zeichen: int, intentionen: tuple[str, ...],
    gegenstand: str | None = None,
) -> list[str]:
    """Die fachliche Vorgabe fuer den Verfasser: Menge, Rueckfrage, Vorschlag.

    Das Gegenstueck zu `regie_zeilen` auf der anderen Seite des Schnitts. Beide
    lesen dieselbe Haltung und dieselbe Turn-Lage; sie teilen sich die fuenf
    Groessen nach Zustaendigkeit statt sie zu doppeln.

    **Die Mengenangabe ist dieselbe Spanne wie beim Responder, und das ist
    Absicht.** Sie bedeutet hier etwas anderes: nicht *„so lang wird die
    Antwort"*, sondern *„fuer so viel Rede wird Stoff gebraucht"*. Wer dem
    Verfasser mehr Material bestellt, als gesagt werden darf, laesst den
    Responder streichen — und gestrichen wird, was zuletzt kam, nicht was am
    wenigsten trug.

    Vorbedingung: `haltung` traegt `umfang`, `fragen` und `draengen`.
    Nachbedingung: drei Zeilen, in fester Reihenfolge — Menge, Rueckfrage,
        Vorschlag.
    Fehlerfaelle: fehlende Groesse (ValueError). Eine stumm ausgelassene Zeile
        waere von einer Groesse am unteren Anschlag nicht zu unterscheiden.

    Args:
        haltung: das Ergebnis der Haltungsrechnung dieses Turns.
        reiz_zeichen: Laenge der Nutzeraeusserung in Zeichen.
        intentionen: die erhobenen Intentionen des Turns.
        gegenstand: der Frage-Gegenstand aus der Sachlage (Scheibe 3) oder None.

    Returns:
        Drei Zeilen fuer den Auftrag des Verfassers.
    """
    # ── Eingabe-Validierung ─────────────────────
    fachlich: tuple[str, ...] = ("umfang", "fragen", "draengen")
    fehlend: list[str] = [name for name in fachlich if name not in haltung.werte]
    if fehlend:
        meldung: str = (
            f"stoffzeilen: Haltung unvollstaendig — es fehlen: "
            f"{', '.join(fehlend)}"
        )
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    unten, oben = spanne_fuer_turn(
        haltung.werte["umfang"].ergebnis, reiz_zeichen, intentionen,
    )
    zeilen: list[str] = [
        f"Menge: Stoff fuer {unten} bis {oben} Zeichen Rede. Mehr wird nicht "
        f"gesagt, sondern gestrichen.",
        _rueckfragenzeile(haltung, gegenstand),
        f"Vorschlag: {stoff_band('draengen', haltung.werte['draengen'].ergebnis)}.",
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if len(zeilen) != len(fachlich):
        meldung = (
            f"stoffzeilen: {len(zeilen)} Zeilen fuer {len(fachlich)} Groessen"
        )
        raise ValueError(meldung)

    return zeilen


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


def regie_zeilen(
    haltung: Haltung, arousal: float, reiz_zeichen: int,
    intentionen: tuple[str, ...],
) -> list[str]:
    """Die Regie fuer diesen Turn: Umfang, abweichende Haltung, Energie.

    **Die Umfangszeile traegt seit dem 20.08.2026 drei Einfluesse**, nicht
    einen: den Raum (`umfang` aus der Landschaft), den Korridor
    (`UMFANG_SPANNE`) und die Laenge der Aeusserung, sofern der Turn nur
    leichte Intentionen traegt. Die Zeile selbst sieht unveraendert aus —
    eine Spanne und ein Wort —, weil der Prompt keine Rechnung lesen soll.

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
        reiz_zeichen: Laenge der Nutzeraeusserung in Zeichen.
        intentionen: die erhobenen Intentionen des Turns.

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
    unten, oben = spanne_fuer_turn(umfang.ergebnis, reiz_zeichen, intentionen)
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
