"""
EI-Calc Node — Berechnet Emotionale Intelligenz, rollenabhängig.

Position im Graph — UNTERSCHIEDLICH je Graph:
  HumanGraph:     perzeption → enricher → ei_calc
                  raw_turns liegt im State (der Enricher lief davor).
  CharacterGraph: db_zugriff → ei_calc → enricher
                  raw_turns liegt NICHT im State — _ei_calc_character lädt die
                  Session-Turns selbst aus Redis (session_turns_retrieve).

Die CG-Reihenfolge ist bewusst so (Commit 630d357, Chat 89): Der Enricher
liest nova_emotions_verlauf, das ei_calc erzeugt — die Erinnerungs-Auswahl
soll auf Novas empathie-modifizierter Lage stehen, nicht auf der des
Vorturns. Deshalb lädt der Konsument selbst, statt die Kanten zu tauschen.

I/O: ein Redis-Read (Session-Turns) auf der Character-Seite. Kein LLM-Call.
Schreibt EI-Ergebnisse zurück in den State.
"""

import logging

from config import redis_client
from ei.berechnung import (
    _emotions_verlauf_berechnen,
    stimmungsvektor_bestimmen,
    _sprach_stil_erkennen,
    _ei_arousal_berechnen,
    _modus_plausibilitaet,
    _stil_plausibilitaet,
    _nova_empathie_berechnen,
)
from ei.raum import raum_nachfuehren
from graph.personality import InternalPersonality, Personality
from graph.state import ConversationState
from memory.session import session_turns_retrieve

logger = logging.getLogger("ki_server.ei_calc")


def internal_emotion_uebertragen(
    internal, nova_emotions_verlauf: list[dict],
    quelle: str = "EI-Calc/Character",
) -> bool:
    """Uebertraegt Novas dominante Emotion dieses Turns nach internal.emotion.

    Zwei Nodes rufen die Funktion nacheinander: `ei_calc` setzt den Stand aus
    Decay und Empathie, der EmGrav-Node zieht ihn nach, wenn eine reaktivierte
    Erinnerung Novas Lage verschoben hat. `quelle` benennt den Aufrufer in der
    Log-Zeile — sonst behauptet die zweite Zeile, sie komme aus ei_calc.

    Vorbedingung: `internal` traegt eine Emotion (aus db_zugriff, Stand
    Vorturn); `nova_emotions_verlauf` ist absteigend nach Gewicht sortiert.
    Nachbedingung: Bei nicht-leerem Verlauf tragen `emotion` und `arousal` den
    fuehrenden Eintrag. Bei leerem Verlauf bleibt der Vorturn-Stand stehen.
    Fehlerfaelle: Leerer Verlauf — laut protokolliert, weil der GV-Node dann
    seinen Cluster auf einer veralteten Lage waehlt.

    Returns:
        True, wenn uebertragen wurde; False, wenn der Vorturn-Wert stehenblieb.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not nova_emotions_verlauf:
        logger.error(
            "%s: nova_emotions_verlauf ist leer — internal.emotion "
            "behaelt den Stand des Vorturns (%s). Der GV-Node waehlt seinen "
            "Cluster damit auf einer veralteten Lage",
            quelle, internal.emotion.emotion,
        )
        return False

    # ── Verarbeitung ────────────────────────────
    fuehrend: dict = nova_emotions_verlauf[0]
    internal.emotion.emotion = fuehrend["emotion"]
    # Ein Eintrag ohne arousal darf keine 0.0 erfinden — der bisherige Wert
    # ist die ehrlichere Auskunft als eine Null, die wie eine Messung aussieht.
    internal.emotion.arousal = fuehrend.get("arousal", internal.emotion.arousal)

    # ── Ausgabe-Verifikation ────────────────────
    # Bis Chat 114 endete diese Zeile mit "gilt ab hier fuer den GV-Node". Das
    # stimmte nicht mehr, seit der EmGrav-Node zwischen hier und dem GV-Node
    # Novas Lage erneut aendert: Die Zeile behauptete eine Geltung, die sie
    # nicht mehr besass. Jetzt sagt sie, wer geschrieben hat.
    logger.info(
        "%s: internal.emotion gesetzt — %s (a=%.2f)",
        quelle, internal.emotion.emotion, internal.emotion.arousal,
    )
    return True


def ei_calc(state: ConversationState) -> ConversationState:
    """Berechnet EI-Werte, rollenabhängig.

    Rolle "user":      Nur User-EI-Block (Pfad 1, HumanGraph).
    Rolle "character": Nur Nova-EI-Block (Pfad 2, CharacterGraph).

    Die saubere Trennung vermeidet Doppelarbeit und semantische Vermischung.
    """
    rolle: str = state.get("ei_calc_rolle", "user")
    logger.info(f"EI-Calc: Starte Berechnung (rolle={rolle})")

    if rolle == "user":
        _ei_calc_user(state)
    elif rolle == "character":
        _ei_calc_character(state)
    else:
        logger.warning(f"EI-Calc: Unbekannte rolle '{rolle}' — fallback auf user")
        _ei_calc_user(state)

    logger.info("EI-Calc: Berechnung abgeschlossen")
    return state


def _ei_calc_user(state: ConversationState) -> None:
    """User-EI-Block — für Pfad 1 (HumanGraph).

    Liest die User-Wahrnehmung aus ``state["external"]`` (von perzeption
    gesetzt) und schreibt Emotions-Verlauf, Vektor und korrigierte
    Modus-/Stil-Werte zurueck in dieselbe Personality.
    Keine Nova-Berechnung hier — das passiert in Pfad 2.
    """
    raw_turns: list[dict] = state.get("raw_turns", [])

    external = state.get("external")
    if external is None:
        external = Personality()
        state["external"] = external

    current_emotion:    str   = external.emotion.emotion
    current_arousal:    float = external.emotion.arousal
    beziehungs_dynamik: str   = external.emotion.relationship_dynamic
    intent:             str   = external.emotion.intent
    tone:               str   = external.emotion.tone
    perzeption_modus:   str   = external.emotion.mode
    perzeption_stil:    str   = external.emotion.language_style

    # 1. Emotions-Verlauf (logarithmischer Decay, mit current_emotion als Turn 0)
    emotions_verlauf: list[dict] = _emotions_verlauf_berechnen(
        raw_turns, current_emotion, current_arousal, rolle="user",
    )
    state["emotions_verlauf"] = emotions_verlauf

    # 2. Emotions-Vektor (in external.emotion.emotions_vector)
    stimmung = stimmungsvektor_bestimmen(
        raw_turns, current_emotion, rolle="user",
    )
    emotions_vektor: str = stimmung.vektor
    external.emotion.emotions_vector = emotions_vektor
    external.emotion.emotions_vector_quelle = stimmung.quelle
    logger.info(
        "EI-Calc: Emotions-Vektor — %s (Grundlage %s)",
        stimmung.vektor, stimmung.quelle,
    )

    # 3. EI-Arousal
    ei_arousal: float = _ei_arousal_berechnen(
        current_arousal, beziehungs_dynamik, intent, tone,
    )

    # 4. Modus-Plausibilität (korrigiert external.emotion.mode)
    korrigierter_modus: str = _modus_plausibilitaet(
        current_emotion, ei_arousal, perzeption_modus,
    )
    external.emotion.mode = korrigierter_modus

    # 5. Sprachstil-Plausibilität (Tiebreaker-Hash aus external.character)
    char_hash_dict: dict = {
        "kern":              external.character.core,
        "adaptiv":           external.character.adaptive,
        "beziehungsprofil":  external.character.relationship,
        "intentions_profil": external.character.intentions,
        "emotions_profil":   external.character.emotions,
    }
    regelbasiert_stil: str = _sprach_stil_erkennen(
        raw_turns,
        char_hash_dict if any(char_hash_dict.values()) else None,
        rolle="user",
    )
    sprach_stil: str = _stil_plausibilitaet(
        current_emotion, ei_arousal, perzeption_stil,
        regelbasiert_stil, tone,
    )
    external.emotion.language_style = sprach_stil

    # Logging
    if emotions_verlauf:
        top_emotions: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f},a={e.get('arousal', 0.5):.2f})"
            for e in emotions_verlauf[:4]
        )
        logger.info(f"EI-Calc/User: Emotions-Verlauf — {top_emotions}")

    if emotions_vektor and emotions_vektor != "plateau":
        logger.info(f"EI-Calc/User: Emotions-Vektor — {emotions_vektor}")

    if sprach_stil and sprach_stil != "neutral":
        logger.info(f"EI-Calc/User: Sprachstil — {sprach_stil}")

    if external.character.relationship:
        logger.info("EI-Calc/User: Beziehungs-Kontext (external.character.relationship) gesetzt")


def _ei_calc_character(state: ConversationState) -> None:
    """Character-EI-Block — für Pfad 2 (CharacterGraph).

    Berechnet Novas Emotion aus ihrer eigenen Turn-Historie plus
    optionaler Empathie vom User (abhängig von event_source).
    Kein virtueller Turn 0 — Novas aktuelle Emotion wird erst nach
    der Antwort-Generierung durch die Perzeption analysiert.
    """
    # ── Eingabe (EVA): Session-Turns selbst laden ──
    # Im CG laeuft ei_calc VOR dem Enricher (Reihenfolge aus 630d357) —
    # state["raw_turns"] ist zu diesem Zeitpunkt immer leer. Der Konsument
    # beschafft seinen Emotionsverlauf deshalb selbst aus Redis. Bewusst NICHT
    # nach state["raw_turns"] geschrieben: Der Key gehoert dem Enricher, ein
    # zweiter Schreiber waere Doppelbesitz.
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")

    raw_turns: list[dict] = []
    if not user_id or not character_id:
        logger.error(
            "EI-Calc/Character: Session-Turns nicht ladbar — Paar unvollstaendig "
            "(user_id='%s', character_id='%s'); rechne mit leerem Verlauf",
            user_id, character_id,
        )
    else:
        try:
            raw_turns = session_turns_retrieve(redis_client, user_id, character_id)
        except Exception as fehler:
            logger.exception(
                "%s: EI-Calc/Character: Session-Turns-Read fehlgeschlagen "
                "(%s:%s); rechne mit leerem Verlauf",
                type(fehler).__name__, user_id, character_id,
            )

    # User-Werte werden gelesen, aber NICHT als Turn 0 in Novas Verlauf injiziert.
    # Sie werden nur für die Empathie-Berechnung gebraucht.
    external = state.get("external")
    current_emotion: str   = external.emotion.emotion if external else "neutral"
    current_arousal: float = external.emotion.arousal if external else 0.5

    # Kraft 1: Novas vorheriger Zustand mit Decay (rein auf historischen Nova-Turns)
    nova_turns: list[dict] = [
        t for t in raw_turns if t.get("rolle") == "assistant"
    ]
    nova_verlauf_basis: list[dict] = _emotions_verlauf_berechnen(
        nova_turns, rolle="assistant", inject_current=False,
    )

    # Sichtbarkeit Kraft 1: seit 630d357 war diese Basis immer leer — die Zeile
    # zeigt, WORAUF die historische Emotions-Gravitation rechnet. Bewusst ohne
    # Gate: eine leere Basis wird sichtbar ausgegeben, nicht verschluckt.
    if nova_verlauf_basis:
        basis_top: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f},a={e.get('arousal', 0.5):.2f})"
            for e in nova_verlauf_basis[:4]
        )
        logger.info("EI-Calc/Character: Emotions-Verlauf — %s", basis_top)
    else:
        logger.info(
            "EI-Calc/Character: Emotions-Verlauf — (leer, %d Nova-Turns)",
            len(nova_turns),
        )

    # Kraft 2: Asymmetrische Empathie vom User-Vektor
    event_source: str = state.get("event_source", "user")

    if event_source == "user":
        empathie_ergebnis: dict = _nova_empathie_berechnen(
            nova_verlauf_basis, current_emotion, current_arousal,
        )

        # Die emotionale Gravitation wird NICHT hier angewendet. Sie stand bis
        # Chat 113 an dieser Stelle und konnte nie greifen: Der Enricher setzt
        # die Gravitationspunkte, laeuft im CharacterGraph aber NACH ei_calc
        # (siehe Modul-Docstring). Die Liste war hier immer leer — 851
        # Berechnungen, null Anwendungen. Der Verbraucher ist jetzt ein eigener
        # Node zwischen Enricher und Reducer.

        state["nova_emotions_verlauf"] = empathie_ergebnis["nova_verlauf_modifiziert"]
        state["nova_emotion_konflikt"] = empathie_ergebnis["nova_konflikt"]
        logger.info("EI-Calc/Character: Nova-Empathie berechnet (event_source=user)")
    else:
        state["nova_emotions_verlauf"] = nova_verlauf_basis
        state["nova_emotion_konflikt"] = False
        logger.info("EI-Calc/Character: Nova-Empathie übersprungen (event_source=character, nur Decay)")

    # Novas Emotions-Vektor (in internal.emotion.emotions_vector)
    #    Kein `inject_current`: Novas Wahrnehmung ihrer eigenen Antwort steht
    #    bereits als juengster `assistant`-Turn in `nova_turns`.
    nova_stimmung = stimmungsvektor_bestimmen(
        nova_turns, rolle="assistant", inject_current=False,
    )
    nova_emotions_vektor: str = nova_stimmung.vektor
    internal = state.get("internal")
    if internal is None:
        internal = InternalPersonality()
        state["internal"] = internal
    internal.emotion.emotions_vector = nova_emotions_vektor
    internal.emotion.emotions_vector_quelle = nova_stimmung.quelle
    logger.info(
        "EI-Calc/Character: Emotions-Vektor — %s (nova_turns=%d, Grundlage %s)",
        nova_emotions_vektor, len(nova_turns), nova_stimmung.quelle,
    )

    # Novas dominante Emotion dieses Turns in internal.emotion uebertragen.
    #
    # Bis Chat 113 stand hier nur der Emotions-Vektor, und `emotion`/`arousal`
    # trugen weiter den Wert, den db_zugriff aus redis:nova_state geladen hatte —
    # den Stand vom ENDE des letzten Turns (einziger Setzer sonst:
    # perzeption/assistant, der erst nach dem Responder laeuft). Zwischen hier
    # und dort liest genau ein Konsument diese Felder: der GV-Node. Seine
    # Dreischicht-Achsen waehlten Sektor, Cluster und Strategie-Repertoire damit
    # auf Novas Lage von gestern, waehrend die sechs Saeulen der
    # Aufnahmebereitschaft im selben Node bereits auf nova_emotions_verlauf
    # standen — zwei Zeitstaende fuer dieselbe Groesse in einem Node.
    #
    # Nova hoert den Input mit der Stimmung, die sie JETZT hat; darauf antwortet
    # ihr Gedaechtnis, und daraus entsteht die Verschiebung, die der GV-Node
    # ausarbeitet. Der Vorturn-Wert bleibt nur stehen, wenn es keinen Verlauf
    # gibt — und das wird gemeldet, statt still zu geschehen.
    #
    # Das ist der Stand VOR der emotionalen Gravitation. Der EmGrav-Node laeuft
    # spaeter im CharacterGraph (enricher → emotionale_gravitation → reducer)
    # und zieht die Uebertragung nach, wenn eine Erinnerung Novas Lage
    # verschoben hat. Erst danach steht fest, worauf der GV-Node rechnet.
    internal_emotion_uebertragen(
        internal, state.get("nova_emotions_verlauf") or [],
        quelle="EI-Calc/Character (vor der Gravitation)",
    )

    # ── Raumzug: das Register folgt dem, der zuletzt gesprochen hat ──
    # Die Emotion hat zwei Kraefte — Novas eigenen Verlauf und den Zug des
    # Nutzers (Empathie, oben). Das Register hatte bis Chat 114 nur die erste:
    # `internal.emotion.mode` und `.language_style` beschreiben Novas letzte
    # Aeusserung, ueberleben in Redis, und nichts zog daran. Gemessen wurde
    # daraus eine Divergenz statt einer Annaeherung — der Nutzer wurde lockerer,
    # Nova foermlicher, und die Dreischicht-Achsen folgten ihr.
    #
    # Bei einem Nutzer-Turn ist sein geschaetztes Register das Ziel und der
    # Charakterfaktor greift. Bei einem Eigen-Impuls folgt der Raum Nova selbst:
    # Wenn sie in der Zwischenzeit eigenen Dingen nachgeht, schiebt sich der
    # Raum dorthin — ohne Faktor, gegen sich selbst straeubt sie sich nicht.
    if event_source == "user":
        raum_nachfuehren(internal, external, quelle="Nutzer")
    else:
        raum_nachfuehren(
            internal, internal, quelle="Eigen-Impuls", charakter_faktor=1.0,
        )

    if state["nova_emotions_verlauf"]:
        nova_top: str = ", ".join(
            f"{e['emotion']}({e['gewicht']:.2f})"
            for e in state["nova_emotions_verlauf"][:3]
        )
        logger.info(f"EI-Calc/Character: Nova-Emotion — {nova_top}")

    if state["nova_emotion_konflikt"]:
        logger.info("EI-Calc/Character: Nova-Emotion — Konflikt erkannt (gegenüberliegende Sektoren)")
