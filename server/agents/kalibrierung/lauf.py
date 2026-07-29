"""Der Kalibrierlauf: Korpus holen, Zeugen befragen, Schwelle suchen.

Der Ablauf in einer Funktion, die der Agent ruft und ein Skript ebenso. Was
gerechnet wird, steht in `ei/kalibrierung.py`; was geladen wird, in
`korpus.py`; wer urteilt, in `zeuge.py`. Hier steht nur die Reihenfolge.

**Erheben und Anwenden sind getrennt** (`KALIBRIERUNG_ANWENDEN`). Auf `false`
laeuft alles bis zum Ergebnis und schreibt nichts. Der Grund ist nicht
Vorsicht um ihrer selbst willen: Eine Schwelle aus einem ungeprueften Zeugen
dreht das Achsen-Bit fuer einen grossen Teil der Turns um, und die Wirkung
zeigt sich erst im Sektor-Histogramm der naechsten Tage. Wer sie anwendet,
soll die Zahl vorher gesehen haben.

Konzept: novaberg-gv-initiative_k.md §7, §12.
"""

import logging
from dataclasses import dataclass, field

from agents.kalibrierung.korpus import (
    Turnpaar,
    embedding_holen,
    rohturns_laden,
    rohwert_rechnen,
)
from agents.kalibrierung.zeuge import ZEUGE_PROMPT, zeuge_befragen
from agents.kalibrierung.zwischenstand import (
    Reihenstand,
    aggregat_schreiben,
    stand_lesen,
    verwerfen,
    zeile_schreiben,
)
from config import KALIBRIERUNG_POSITIONSPROBE
from ei.kalibrierung import (
    Kalibrierung,
    Urteilspaar,
    positions_kontrolle,
    schwelle_suchen,
)

logger = logging.getLogger("ki_server.agents.kalibrierung.lauf")


def _reihenname(user_id: str, character_id: str) -> str:
    """Bildet den Namen der Zwischenstandsdatei aus dem Paar."""
    return f"{user_id}-{character_id}"


def _zeugenkennung() -> str:
    """Kennung des Zeugen-Prompts, um Urteile zweier Fassungen zu trennen.

    Ein Urteil haengt am Turn **und** am Prompt. Aendert sich der Prompt, sind
    die alten Urteile ungueltig: Ein Wiederanlauf wuerde zwei verschiedene
    Zeugen zu einer Zahl mischen, und die Zahl saehe aus wie eine Messung.

    Vorbedingung: keine.
    Nachbedingung: Eine kurze, stabile Kennung derselben Prompt-Fassung.
    Fehlerfaelle: keine.

    Returns:
        Die Kennung.
    """

    # ── Verarbeitung ────────────────────────────
    import hashlib
    roh: str = hashlib.sha256(ZEUGE_PROMPT.encode("utf-8")).hexdigest()

    # ── Ausgabe ─────────────────────────────────
    return roh[:12]


@dataclass
class Laufergebnis:
    """Was ein Kalibrierlauf hinterlaesst — auch wenn er nichts geschrieben hat.

    `ausfaelle` zaehlt getrennt, woran Turns aus dem Korpus fielen. Eine
    Gesamtzahl wuerde die Frage verdecken, ob die Grundlage schmal ist, weil
    der Zeuge schweigt oder weil die Achse nichts messen konnte.
    """

    kalibrierung:        Kalibrierung
    positions_bestanden: bool           = False
    positions_text:      str            = ""
    turnpaare:           int            = 0
    verwertet:           int            = 0
    ausfaelle:           dict[str, int] = field(default_factory=dict)
    angewandt:           bool           = False


def _urteilspaare_sammeln(
    paare: list[Turnpaar],
    reihe: str,
    stand: Reihenstand,
) -> tuple[list[Urteilspaar], dict]:
    """Rechnet Rohwerte und holt Urteile — beide Seiten des Vergleichs.

    **Jedes Urteil wird geschrieben, sobald es vorliegt.** Ein bereits
    bezeugter Turn wird nicht erneut gefragt: Das Urteil kostet Minuten, der
    Rohwert Millisekunden, und nur der Rohwert wird jedes Mal neu gerechnet.

    Die Embeddings werden zwischengespeichert: Novas Antwort aus Turn n ist
    die Vorantwort von Turn n+1, und ein zweites Embedding desselben Textes
    waere ein zweiter Call fuer denselben Vektor.

    Vorbedingung: `paare` stammt aus `rohturns_laden`, `stand` aus
    `stand_lesen`.
    Nachbedingung: Liste der Turns, fuer die **beide** Seiten vorliegen, plus
    eine Aufschluesselung der Ausfaelle. Der Zwischenstand traegt danach jedes
    geholte Urteil und jeden Fehlschlag.
    Fehlerfaelle: Ein Turn ohne Rohwert oder ohne Urteil faellt heraus und
    wird gezaehlt. Kein Ersatzwert — ein Ausfall auf einer regulaeren
    Achsenposition ist genau der Defekt, den die neue Achse abgeloest hat.

    Returns:
        (Urteilspaare, Ausfallzaehler)
    """

    # ── Eingabe-Validierung ─────────────────────
    if not paare:
        logger.error("Kalibrierlauf: keine Turnpaare — nichts zu sammeln")
        return [], {"ohne_turnpaare": 0}

    # ── Verarbeitung ────────────────────────────
    ergebnis:  list[Urteilspaar] = []
    ausfaelle: dict[str, int]    = {
        "ohne_rohwert": 0, "ohne_urteil": 0, "ohne_embedding": 0,
    }
    aus_stand: int = 0
    cache:     dict[str, list[float]] = {}

    def _embedding(text: str) -> list[float] | None:
        if text not in cache:
            vektor = embedding_holen(text)
            if vektor is None:
                return None
            cache[text] = vektor
        return cache[text]

    for paar in paare:
        emb_prompt  = _embedding(paar.user_prompt)
        emb_antwort = _embedding(paar.vor_antwort)

        if emb_prompt is None or emb_antwort is None:
            ausfaelle["ohne_embedding"] += 1
            continue

        rohwert = rohwert_rechnen(paar, emb_prompt, emb_antwort)
        if rohwert is None:
            ausfaelle["ohne_rohwert"] += 1
            continue

        # Der teure Teil: nur holen, was noch nicht bezeugt ist. Fehlschlaege
        # aus einem frueheren Lauf stehen bewusst nicht in `urteile` und werden
        # deshalb wiederholt.
        if paar.turn_id in stand.urteile:
            urteil: bool | None = stand.urteile[paar.turn_id]
            aus_stand += 1
        else:
            urteil = zeuge_befragen(paar.vor_antwort, paar.user_prompt)
            zeile_schreiben(
                reihe, paar.turn_id, urteil,
                fehler="" if urteil is not None else "kein Urteil",
            )

        if urteil is None:
            ausfaelle["ohne_urteil"] += 1
            continue

        ergebnis.append(Urteilspaar(paar.turn_id, rohwert, urteil))

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        f"Kalibrierlauf: {len(ergebnis)} von {len(paare)} Turnpaaren verwertet "
        f"({aus_stand} Urteile aus dem Zwischenstand, "
        f"{len(ergebnis) - aus_stand} neu geholt; Ausfaelle: {ausfaelle})"
    )
    return ergebnis, ausfaelle


def _positions_kontrolle_fahren(
    paare: list[Turnpaar],
    reihe: str,
    stand: Reihenstand,
) -> tuple[bool, str]:
    """Legt eine Stichprobe in beiden Richtungen vor und wertet sie aus.

    **Ihr Ergebnis wird als Aggregat geschrieben.** Die Kontrolle laeuft vor
    der Erhebung; ohne diese Zeile ist sie beim Abbruch verloren, obwohl jeder
    Einzelfall gesichert war — genau so ist am 29.07.2026 das Ergebnis aus 60
    Urteilen verschwunden. Liegt sie im Zwischenstand, wird sie nicht erneut
    gefahren.

    Vorbedingung: `paare` ist nicht leer.
    Nachbedingung: (bestanden, Begruendung) aus `positions_kontrolle`, im
    Zwischenstand unter `positions_kontrolle` abgelegt.
    Fehlerfaelle: Zu wenige gueltige Urteile — dann ist die Kontrolle selbst
    nicht aussagekraeftig und gilt als nicht bestanden; das wird laut gesagt,
    weil eine ausgefallene Kontrolle sonst wie eine bestandene aussaehe.

    Returns:
        (bestanden, Klartext)
    """

    # ── Eingabe-Validierung ─────────────────────
    vorher: dict = stand.aggregate.get("positions_kontrolle", {})
    if vorher:
        logger.info(
            f"Positions-Kontrolle: aus dem Zwischenstand uebernommen "
            f"({vorher.get('text', '?')})"
        )
        return bool(vorher.get("bestanden")), str(vorher.get("text", ""))

    stichprobe: list[Turnpaar] = paare[:KALIBRIERUNG_POSITIONSPROBE]
    if not stichprobe:
        logger.error("Positions-Kontrolle: leere Stichprobe")
        return False, "keine Stichprobe"

    # ── Verarbeitung ────────────────────────────
    b_nutzer: list[bool] = []
    b_nova:   list[bool] = []

    for paar in stichprobe:
        # B = der Nutzer: seine Antwort auf Novas Beitrag.
        urteil_n = zeuge_befragen(paar.vor_antwort, paar.user_prompt)
        # B = Nova: dieselben zwei Texte, Rollen vertauscht.
        urteil_v = zeuge_befragen(paar.user_prompt, paar.vor_antwort)

        if urteil_n is not None:
            b_nutzer.append(urteil_n)
        if urteil_v is not None:
            b_nova.append(urteil_v)

    # ── Ausgabe-Verifikation ────────────────────
    if not b_nutzer or not b_nova:
        logger.error(
            f"Positions-Kontrolle: zu wenige Urteile "
            f"(B=Nutzer {len(b_nutzer)}, B=Nova {len(b_nova)}) — "
            f"die Kontrolle selbst ist ausgefallen und gilt als nicht bestanden"
        )
        aggregat_schreiben(reihe, "positions_kontrolle", {
            "bestanden": False, "text": "zu wenige Urteile",
            "n_nutzer": len(b_nutzer), "n_nova": len(b_nova),
        })
        return False, "zu wenige Urteile"

    anteil_nutzer: float = sum(b_nutzer) / len(b_nutzer)
    anteil_nova:   float = sum(b_nova) / len(b_nova)
    bestanden, text = positions_kontrolle(anteil_nutzer, anteil_nova)

    aggregat_schreiben(reihe, "positions_kontrolle", {
        "bestanden":     bestanden,
        "text":          text,
        "anteil_nutzer": round(anteil_nutzer, 4),
        "anteil_nova":   round(anteil_nova, 4),
        "n_nutzer":      len(b_nutzer),
        "n_nova":        len(b_nova),
    })
    return bestanden, text


def kalibrierung_durchfuehren(
    user_id:      str,
    character_id: str,
) -> Laufergebnis:
    """Fuehrt einen vollstaendigen Kalibrierlauf fuer ein Paar durch.

    Reihenfolge: Korpus laden, Positions-Kontrolle fahren, Urteile sammeln,
    Schwelle suchen. Die Kontrolle laeuft **vor** der Erhebung — faellt sie
    durch, taugt der Zeuge nicht als Grundlage, und die 140 Urteile danach
    waeren verschwendet.

    Das Schreiben ist ausdruecklich **nicht** Teil dieser Funktion. Sie
    erhebt und berichtet; der Aufrufer entscheidet.

    Vorbedingung: Paar ist gesetzt, Rohturns liegen vor.
    Nachbedingung: Ein Laufergebnis mit Kalibrierung, Kontrolle und den
    Ausfallzahlen — auch dann, wenn keine Schwelle bestimmt werden konnte.
    Fehlerfaelle: Leerer Korpus, durchgefallene Kontrolle, zu wenige
    Urteilspaare — jeder Fall ist im Ergebnis benannt und fuehrt zu einer
    Kalibrierung ohne Schwelle.

    Returns:
        Das Laufergebnis.
    """

    # ── Eingabe-Validierung ─────────────────────
    paare: list[Turnpaar] = rohturns_laden(user_id, character_id)
    if not paare:
        return Laufergebnis(
            kalibrierung = Kalibrierung(grund="kein Korpus"),
        )

    reihe: str = _reihenname(user_id, character_id)
    stand: Reihenstand = stand_lesen(reihe)

    # Ein Urteil haengt am Turn UND am Prompt. Weicht die Kennung ab, stammen
    # die alten Urteile von einem anderen Zeugen; sie zu uebernehmen mischte
    # zwei Lesarten zu einer Zahl, und die Zahl saehe aus wie eine Messung.
    kennung: str = _zeugenkennung()
    gespeichert: str = str(stand.aggregate.get("zeuge", {}).get("kennung", ""))

    if gespeichert and gespeichert != kennung:
        logger.error(
            f"Kalibrierlauf {user_id}:{character_id}: Zwischenstand stammt von "
            f"Zeuge '{gespeichert}', dieser ist '{kennung}' — der Prompt hat "
            f"sich geaendert, die alten Urteile sind entwertet und werden "
            f"verworfen"
        )
        verwerfen(reihe)
        stand = Reihenstand({}, set(), {})

    if not stand.aggregate.get("zeuge"):
        aggregat_schreiben(reihe, "zeuge", {"kennung": kennung})

    # ── Verarbeitung ────────────────────────────
    bestanden, text = _positions_kontrolle_fahren(paare, reihe, stand)

    if not bestanden:
        logger.error(
            f"Kalibrierlauf {user_id}:{character_id}: Positions-Kontrolle nicht "
            f"bestanden ({text}) — die Erhebung wird nicht gefahren, "
            f"die bestehende Schwelle bleibt stehen"
        )
        return Laufergebnis(
            kalibrierung        = Kalibrierung(grund=f"Positions-Kontrolle: {text}"),
            positions_bestanden = False,
            positions_text      = text,
            turnpaare           = len(paare),
        )

    urteilspaare, ausfaelle = _urteilspaare_sammeln(paare, reihe, stand)
    kalibrierung: Kalibrierung = schwelle_suchen(urteilspaare)

    # ── Ausgabe-Verifikation ────────────────────
    ergebnis = Laufergebnis(
        kalibrierung        = kalibrierung,
        positions_bestanden = bestanden,
        positions_text      = text,
        turnpaare           = len(paare),
        verwertet           = len(urteilspaare),
        ausfaelle           = ausfaelle,
    )

    if kalibrierung.schwelle is None:
        logger.error(
            f"Kalibrierlauf {user_id}:{character_id}: keine Schwelle bestimmt "
            f"({kalibrierung.grund}) — nichts zu schreiben"
        )
    else:
        logger.info(
            f"Kalibrierlauf {user_id}:{character_id}: Schwelle "
            f"{kalibrierung.schwelle:+.2f} (kappa {kalibrierung.kappa:.3f}, "
            f"n={kalibrierung.n}, Uebereinstimmung "
            f"{kalibrierung.uebereinstimmung:.1%})"
        )

    return ergebnis
