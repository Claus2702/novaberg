"""Aufgriff — hat die endgueltige Antwort eine angebotene offene Frage aufgenommen?

Der Gespraechsvektor bietet dem Turn bis zu drei offene Fragen an (`[OFFENE
FRAGEN]`). Ob Nova eine davon aufgreift, hat bis hierher niemand gemessen; die
einzige Zahl war von Hand gezaehlt (12.09.2026: in 15 Turns dieselben drei, keine
aufgegriffen). Dieser Knoten steht hinter der Freigabe der Antwort und schreibt
je Turn **einen** Eintrag in `pipeline_log` mit einem von vier Ausgaengen:

| Ausgang | Bedeutung |
|---|---|
| `nicht_angeboten` | Dem Turn wurde keine Frage angeboten. |
| `angeboten_nicht_aufgegriffen` | Fragen waren angeboten, keine liegt der Antwort nah. |
| `aufgegriffen` | Mindestens eine angebotene Frage liegt der Antwort nah (Kennungen im Eintrag). |
| `nicht_beurteilbar` | Das Urteil liess sich nicht rechnen; der Grund steht im Eintrag. |

**Das Maß:** Cosinus-Naehe zwischen dem Vektor der Antwort und dem Vektor des
Themas (`wissensluecken.embedding`), gerechnet in der Datenbank. Ein Thema, das
nicht angeboten war, wird nie gelesen — die Abfrage kennt nur die Kennungen des
Angebots. Der Knoten aendert weder Antwort noch Zustand ausser dem Protokoll.
"""

import logging
from typing import Any

from graph.state import ConversationState, pipeline_quelle
from memory.pipeline_log import log_berechnung
from memory.repositories.wissensluecken_repository import gap_proximities
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.graph.aufgriff")

NOT_OFFERED: str = "nicht_angeboten"
NOT_TAKEN_UP: str = "angeboten_nicht_aufgegriffen"
TAKEN_UP: str = "aufgegriffen"
NOT_JUDGEABLE: str = "nicht_beurteilbar"

OUTCOMES: frozenset[str] = frozenset({NOT_OFFERED, NOT_TAKEN_UP, TAKEN_UP, NOT_JUDGEABLE})

#: Ab welcher Cosinus-Naehe zwischen Antwort und Thema eine Frage als aufgegriffen gilt.
#:
#: **Ungeeicht — ein Anfangswert, den die erste Messreihe pruefen muss.** Er liegt
#: ueber `OFFENE_FRAGEN_MIN_NAEHE` (0,49): Die angebotenen Fragen waren dem Reiz
#: schon so nah, und eine Antwort auf den Reiz liegt ihnen ohnehin nah; wer
#: dieselbe Grenze nahme, zaehlte jedes Angebot als aufgegriffen. Ab 0,52 galten
#: in der Eichung des Angebots rund 12 von 12 Paaren als passend — 0,55 verlangt
#: etwas mehr als das. Jeder Eintrag traegt die Naehe je Frage, so dass die Grenze
#: nachtraeglich an den Eintraegen verschoben werden kann, ohne neu zu messen.
TAKE_UP_MIN_PROXIMITY: float = 0.55

#: Wie viele Zeichen der Antwort in den Vektor gehen (wie bei der Praegung).
ANSWER_CHARS_EMBEDDED: int = 1200


def judge_take_up(
    offered_ids: list[int],
    proximities: dict[int, float],
    threshold: float,
) -> tuple[str, list[int], str]:
    """Urteilt aus den gerechneten Naehen, welche angebotenen Fragen aufgegriffen sind.

    Vorbedingung: `offered_ids` nicht leer; `proximities` bildet Kennungen auf
        Naehen ab, nur Kennungen aus dem Angebot.
    Nachbedingung: (Ausgang, aufgegriffene Kennungen in Reihenfolge des
        Angebots, Grund). Aufgegriffen nur, was die Schwelle erreicht.
    Fehlerfaelle: Fehlt zu einer angebotenen Kennung die Naehe und keine andere
        erreicht die Schwelle, ist der Ausgang `nicht_beurteilbar` — die fehlende
        Frage haette die aufgegriffene sein koennen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not offered_ids:
        raise ValueError("judge_take_up: kein Angebot — der Aufrufer entscheidet vorher")
    stranger: list[int] = [i for i in proximities if i not in offered_ids]
    if stranger:
        raise ValueError(f"judge_take_up: Naehe zu nicht angebotenen Kennungen {stranger}")

    # ── Verarbeitung ────────────────────────────
    taken: list[int] = [i for i in offered_ids if proximities.get(i, -1.0) >= threshold]
    missing: list[int] = [i for i in offered_ids if i not in proximities]

    # ── Ausgabe-Verifikation ────────────────────
    if taken:
        return TAKEN_UP, taken, ""
    if missing:
        return NOT_JUDGEABLE, [], f"kennung_ohne_naehe:{missing}"
    return NOT_TAKEN_UP, [], ""


def _answer_vector(response: str) -> tuple[list[float], str]:
    """Der Vektor der Antwort — oder der Grund, warum es keinen gibt.

    Vorbedingung: `response` ist ein String.
    Nachbedingung: (Vektor, "") bei Erfolg, ([], Grund) sonst.
    Fehlerfaelle: leere Antwort, Ausfall des Embed-Dienstes oder leerer Vektor
        ergeben je einen Grund; nichts davon wirft.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not response.strip():
        return [], "antwort_leer"

    # ── Verarbeitung ────────────────────────────
    try:
        vector: list[float] = model_service.embed.submit_sync(
            EmbedRequest(text=response[:ANSWER_CHARS_EMBEDDED])
        ).embedding
    except Exception as error:  # noqa: BLE001 — der Turn geht vor
        logger.exception("Aufgriff: Antwort nicht eingebettet (%s)", type(error).__name__)
        return [], f"embedding_fehlgeschlagen:{type(error).__name__}"

    # ── Ausgabe-Verifikation ────────────────────
    if not vector:
        return [], "embedding_leer"
    return vector, ""


def _offered_ids(state: ConversationState) -> tuple[list[int], str]:
    """Die angebotenen Kennungen aus dem Zustand — oder der Grund, warum sie unlesbar sind.

    Vorbedingung: keine.
    Nachbedingung: (Kennungen, "") — leer, wenn nichts angeboten war —, oder
        ([], Grund), wenn der Wert keine Liste ganzer Zahlen ist.
    Fehlerfaelle: Ein falscher Typ ist kein Angebot, sondern ein Fehler des
        Schreibers und wird als `kennungen_ungueltig` gemeldet.
    """
    # ── Eingabe-Validierung ─────────────────────
    raw: Any = state.get("offene_fragen_ids") or []

    # ── Verarbeitung ────────────────────────────
    valid: bool = isinstance(raw, list) and all(
        isinstance(i, int) and not isinstance(i, bool) for i in raw
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not valid:
        return [], "kennungen_ungueltig"
    return list(raw), ""


def _verdict(state: ConversationState) -> dict[str, Any]:
    """Rechnet das Urteil dieses Turns.

    Vorbedingung: `state["response"]` ist die Antwort nach der letzten
        Korrekturrunde (der Knoten steht hinter der Freigabe).
    Nachbedingung: ein Dict mit `ausgang`, `angeboten`, `aufgegriffen`,
        `naehen`, `grund` — der Ausgang ist einer der vier aus `OUTCOMES`.
    Fehlerfaelle: Jeder Fehler beim Rechnen ergibt `nicht_beurteilbar` mit Grund,
        nie `angeboten_nicht_aufgegriffen`.
    """
    # ── Eingabe-Validierung ─────────────────────
    offered, reason = _offered_ids(state)
    verdict: dict[str, Any] = {
        "ausgang": NOT_JUDGEABLE, "angeboten": offered, "aufgegriffen": [],
        "naehen": {}, "grund": reason,
    }
    if reason:
        return verdict
    if not offered:
        verdict["ausgang"] = NOT_OFFERED
        return verdict

    # ── Verarbeitung ────────────────────────────
    vector, reason = _answer_vector(state.get("response") or "")
    proximities: dict[int, float] = {}
    if not reason:
        try:
            proximities = gap_proximities(
                state.get("user_id", ""), state.get("character_id", ""), offered, vector,
            )
        except Exception as error:  # noqa: BLE001 — ein Lesefehler ist kein "nicht aufgegriffen"
            logger.exception("Aufgriff: Naehen nicht gelesen (%s)", type(error).__name__)
            reason = f"lesefehler:{type(error).__name__}"
    if reason:
        verdict["grund"] = reason
        return verdict

    outcome, taken, reason = judge_take_up(offered, proximities, TAKE_UP_MIN_PROXIMITY)

    # ── Ausgabe-Verifikation ────────────────────
    if outcome not in OUTCOMES or (outcome != TAKEN_UP and taken):
        raise RuntimeError(f"Aufgriff: unstimmiges Urteil {outcome!r} mit Aufgegriffenen {taken}")
    verdict.update(
        ausgang=outcome, aufgegriffen=taken, grund=reason,
        naehen={str(i): round(n, 4) for i, n in proximities.items()},
    )
    return verdict


def offene_fragen_aufgriff(state: ConversationState) -> ConversationState:
    """Knoten: schreibt je Turn einen Eintrag, ob eine angebotene Frage aufgegriffen wurde.

    Zweck: macht den Aufgriff der offenen Fragen je Turn ablesbar.
    Vorbedingung: Der Knoten steht hinter der Freigabe der Antwort; der GV-Node
        hat `offene_fragen_ids` gesetzt (fehlt es, gilt: nichts angeboten).
    Nachbedingung: Genau ein `berechnung`-Eintrag `offene_fragen_aufgriff` im
        `pipeline_log`; der Zustand kommt unveraendert zurueck.
    Fehlerfaelle: Kein Fehler hier haelt den Turn an — er wird zu
        `nicht_beurteilbar` mit Grund `unerwartet:<Typ>` und steht im Log.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(state, dict):
        raise TypeError(f"offene_fragen_aufgriff: Zustand ist {type(state).__name__}, kein dict")

    # ── Verarbeitung ────────────────────────────
    try:
        verdict: dict[str, Any] = _verdict(state)
    except Exception as error:  # noqa: BLE001 — der Turn geht vor
        logger.exception("Aufgriff: Urteil nicht gerechnet (%s)", type(error).__name__)
        verdict = {
            "ausgang": NOT_JUDGEABLE, "angeboten": [], "aufgegriffen": [],
            "naehen": {}, "grund": f"unerwartet:{type(error).__name__}",
        }

    # ── Ausgabe-Verifikation ────────────────────
    missing_keys: list[str] = [
        k for k in ("ausgang", "angeboten", "aufgegriffen", "naehen", "grund") if k not in verdict
    ]
    if missing_keys or verdict["ausgang"] not in OUTCOMES:
        raise RuntimeError(f"Aufgriff: unvollstaendiges Urteil {verdict} (fehlt: {missing_keys})")
    log_berechnung(
        turn_id = state.get("turn_id", "unbekannt"),
        node    = "aufgriff",
        quelle  = pipeline_quelle(state),
        inhalt  = {
            "schritt":          "offene_fragen_aufgriff",
            **verdict,
            "mass":             "cosinus_antwort_thema",
            "schwelle":         TAKE_UP_MIN_PROXIMITY,
            "korrekturrunden":  state.get("correction_round", 0),
        },
        user_id      = state.get("user_id", ""),
        character_id = state.get("character_id", ""),
    )
    logger.info(
        "Aufgriff: %s (angeboten %s, aufgegriffen %s%s)",
        verdict["ausgang"], verdict["angeboten"], verdict["aufgegriffen"],
        f", Grund {verdict['grund']}" if verdict["grund"] else "",
    )
    return state
