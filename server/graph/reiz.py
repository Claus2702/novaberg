"""Woher der Reiz dieses Durchlaufs stammt — eine Auskunft für beide Stufen.

**Ein eigener Gedanke hat seit dem 15.08.2026 einen eigenen Platz.** Er steht in
`eigener_gedanke`, `user_prompt` traegt allein, was das Gegenueber gesagt hat,
und die Herkunft steht im Ereignis. Bis dahin teilten sich beide den Reiz-Platz
— und wer ihn las, ohne nach der Herkunft zu fragen, hielt Novas eigenen
Gedanken fuer eine fremde Aeusserung.

**Diese Datei ist der einzige Zugang zu beidem.** Drei Fragen, drei Funktionen:
*von wem* (`reiz_ist_eigener_gedanke`), *was* (`reiz_text`) und *in welchem
Zustand er gefasst wurde* (`reiz_level`). Kein Node liest die Felder direkt, und
**es gibt keinen Rueckfall vom einen Platz auf den anderen** — ein Impuls ohne
Gedanken ist ein Defekt und soll wie einer aussehen.

**Warum die Funktion hier steht und nicht im Responder.** Sie stand dort, und
das war richtig, solange der Responder den Inhalt selbst formulierte. Seit der
Trennung von Inhalt und Form schreibt der **Verfasser** den Text — und er hatte
die Pruefung nicht. Gemessen am 13.08.2026: **13 von 14 eigenen Impulsen** eines
Tages begannen mit »Du hast …«, fuenf davon wortgleich, obwohl der Responder
seinen Schutzblock gesetzt hatte. Die Zuschreibung stand schon im Material.

**Die Lehre daraus ist groesser als der eine Fall:** Ein Schutz, den nur die
zweite Stufe kennt, greift ins Leere, sobald die erste den Text schreibt. Was
beide Stufen brauchen, gehoert an einen Ort — sonst laeuft die Kopie irgendwann
auseinander (`novaberg-bugs.md` → `VERFASSER-KENNT-DIE-QUELLE-NICHT`).
"""

import logging

logger = logging.getLogger("ki_server.graph.reiz")

# Der Platz, an dem der Level eines Gedankens durch das Ereignis reist. Als
# Konstante, weil die Zustellung ihn schreibt und dieser Leser ihn liest —
# zwei Seiten einer Naht. Der Schreiber liegt in der Dienstschicht und darf
# den Graphen nicht importieren; was beide zusammenhaelt, ist deshalb der
# Zeuge auf die Naht und nicht ein gemeinsamer Import.
LEVEL_FELD: str = "gedanke_arousal"


def reiz_ist_eigener_gedanke(state: dict) -> bool:
    """Prueft, ob der Reiz dieses Durchlaufs von Nova selbst stammt.

    Der Marker steht ausdruecklich im Event-Payload; `event_source ==
    "character"` allein genuegt nicht, weil der Thinker-Retry dieselbe Quelle
    traegt und dabei eine echte Nutzer-Aeusserung wiederholt.

    Vorbedingung: keine — ein fehlender Payload heisst „nicht von Nova".
    Nachbedingung: True nur bei ausdruecklich markierter eigener Herkunft.

    Args:
        state: der Zustand des Durchlaufs.

    Returns:
        True, wenn der Reiz Novas eigener Impuls ist.
    """
    # ── Eingabe-Validierung ─────────────────────
    payload: dict = state.get("event_payload") or {}

    # ── Verarbeitung / Ausgabe ──────────────────
    return payload.get("reiz_herkunft") == "eigener_impuls"


def reiz_text(state: dict) -> str:
    """Der Text, der diesen Durchlauf ausgeloest hat — gleich, von wem er kam.

    **Warum das nicht `state["user_prompt"]` ist.** Der Reiz-Platz traegt, was
    das Gegenueber gesagt hat. Auf einem Impuls-Turn hat niemand gesprochen —
    dort steht der Gedanke in `eigener_gedanke`, und `user_prompt` ist leer.
    Wer trotzdem den Reiz-Platz liest, bekommt eine leere Zeichenkette und
    meldet einen Ausfall, obwohl der Turn vollstaendig ist.

    **Kein Rueckfall auf den Reiz-Platz, wenn der Gedanke fehlt.** Ein Impuls
    ohne Gedanken ist ein Defekt und soll wie einer aussehen; ein Rueckfall
    machte daraus einen Turn, der laeuft und den falschen Text bewertet. Die
    Leerprueferei bleibt beim Aufrufer — er allein weiss, ob der Text fuer ihn
    Pflicht ist.

    Vorbedingung: keine — ein fehlendes Payload heisst „Nutzer-Turn".
    Nachbedingung: der Gedanke bei eigener Herkunft, sonst die Nutzer-
    Aeusserung; nie None.

    Args:
        state: der Zustand des Durchlaufs.

    Returns:
        Der Text des Reizes, moeglicherweise leer.
    """
    # ── Eingabe-Validierung / Verarbeitung ──────
    if reiz_ist_eigener_gedanke(state):
        return state.get("eigener_gedanke") or ""

    # ── Ausgabe ─────────────────────────────────
    return state.get("user_prompt") or ""


def reiz_level(state: dict) -> float | None:
    """Die Erregung, in der der Gedanke dieses Durchlaufs gefasst wurde.

    Ein Gedanke wird in einem Zustand gefasst und bringt ihn mit, wenn er
    auftaucht (`novaberg-eigenzeit_k.md` §2.3). Der Wert reist vom
    Stapel-Eintrag ueber das Ereignis hierher; was mit ihm geschieht,
    entscheidet der Zugriffsknoten — er **hebt**, er setzt nicht.

    **`None` heisst unbekannt und wird nie zu einer Zahl.** Drei Wege fuehren
    dorthin, und alle drei sind zulaessig: ein Nutzer-Turn (niemand hat einen
    Gedanken gefasst), ein fehlendes Feld (Eintrag alter Bauart) und ein
    ausdrueckliches Null (Eintrag neuer Bauart ohne Wert). Ein Vorgabewert
    waere hier der teuerste Fehler: Er saehe wie eine Messung aus und hoebe
    Novas Zustand auf eine erfundene Zahl.

    Vorbedingung: keine — ein fehlendes Payload heisst „kein Level".
    Nachbedingung: eine Zahl in [0.0, 1.0] oder ``None``. Ein Wert ausserhalb
        der Spanne wird **verworfen und gemeldet, nicht gekappt**: Eine stille
        Kappung machte aus einem Rechenfehler ein plausibles Ergebnis.

    Args:
        state: der Zustand des Durchlaufs.

    Returns:
        Der hinterlegte Level, oder ``None``, wenn keiner vorliegt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not reiz_ist_eigener_gedanke(state):
        return None

    payload: dict = state.get("event_payload") or {}
    roh: object = payload.get(LEVEL_FELD)
    if roh is None:
        return None

    # `bool` ist in Python eine Ganzzahl. Ein `True` wuerde hier als 1.0
    # durchgehen und Novas Zustand an den Anschlag heben.
    if isinstance(roh, bool) or not isinstance(roh, (int, float)):
        logger.error(
            "Reiz: %s traegt %r (%s) statt einer Zahl — kein Level angewandt",
            LEVEL_FELD, roh, type(roh).__name__,
        )
        return None

    # ── Verarbeitung ────────────────────────────
    level: float = float(roh)

    # ── Ausgabe-Verifikation ────────────────────
    # Spanne laut Nachbedingung: 0.0 bis 1.0 — dieselbe Skala, auf der die
    # Perzeption die Erregung fuehrt.
    if not (0.0 <= level <= 1.0):
        logger.error(
            "Reiz: %s traegt %r ausserhalb der Spanne 0.0–1.0 — verworfen, "
            "kein Level angewandt", LEVEL_FELD, level,
        )
        return None

    return level
