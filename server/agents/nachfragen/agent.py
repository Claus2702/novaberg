"""NachfragenAgent — Zuwendung, wenn die EI einen Druck gefunden hat.

Queue-basiert (aufgabe: nachfragen). Beschafft nichts: Der Anlass ist ein
Zustand des Gegenuebers, kein Wissensdefizit. Der Agent liest den **aktuellen**
Druck aus den Session-Turns, verdichtet ihn deterministisch zu einem Reiz und
legt ihn auf den Shadow-Stack. Ob und wie daraus eine Frage wird, entscheiden
Zustellung und CharacterGraph.

Konzept: novaberg-pixie-nachfragen_k.md, insbesondere §7 und §8.
"""

import json
import logging

import psycopg2
import redis

from agents.base import AgentState, BaseAgent
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    EMOTION_VEKTOR_TURNS,
    EMOTIONS_VEKTOREN,
    EMOTIONS_VEKTOREN_DRUCK,
    redis_client,
)
from ei.farbton import lage_beschreiben
from memory.session import _session_key
from services.pixie.stack import stack_push
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.nachfragen")

# Name der Aufgabe auf dem Shadow-Stack.
#
# **Pflicht, kein Etikett.** `_emotional_kompatibel()` in
# `services/shadow_delivery.py` vergleicht genau diese Zeichenkette und laesst
# bei negativen Emotionen ausschliesslich sie durch. Ein abweichender Wert
# macht den Agenten unsichtbar fuer den einzigen Fall, fuer den er gebaut ist.
AUFGABE: str = "nachfragen"

# Vorgabewerte fuer Turn-Felder, die fehlen duerfen.
#
# Sie sind **keine** Defaults fuer Pflichtfelder: Der Vektor ist das
# Pflichtfeld und hat keinen Vorgabewert. Diese drei schmuecken die
# Beschreibung aus und duerfen schweigen — `lage_beschreiben()` traegt
# unbekannte Werte schlicht nicht bei.
TURN_EMOTION_LEER: str = "neutral"
TURN_AROUSAL_LEER: float = 0.5
TURN_DYNAMIK_LEER: str = "neutral"


class NachfragenAgent(BaseAgent):
    """Legt bei erkanntem Druck einen Zuwendungs-Reiz auf den Shadow-Stack."""

    @property
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        return "nachfragen"

    @property
    def faehigkeiten(self) -> list[str]:
        """Fuer den Planner-Prompt — dieser Agent kann genau eines."""
        return ["nachfragen"]

    @property
    def graph_eignung(self) -> list[str]:
        """Nur im Pixie-Graphen: Der Auftrag entsteht im Hintergrund."""
        return ["pixie"]

    @property
    def context_user(self) -> str:
        """Gearbeitet wird am Gedaechtnis des Menschen, nicht an Novas."""
        return "user"

    @property
    def identity_user(self) -> str:
        """Handelnde ist Nova."""
        return ASSISTANT_USER_ID

    def periodic_task(self) -> None:
        """Kein periodischer Lauf — der Agent haengt an der Shadow-Queue."""
        return None

    def build_graph(self) -> None:
        """Kein Untergraph — der Ablauf ist geradlinig und steht in `invoke`."""
        return None

    # ─────────────────────────────────────────
    # Audit
    # ─────────────────────────────────────────

    @staticmethod
    def _audit_log(user_id: str, status: str, ergebnis: str) -> None:
        """Schreibt einen hintergrund_log-Eintrag fuer den Durchlauf.

        Failsafe: Bei DB-Fehler nur `logger.critical`, kein Retry — ein Retry
        auf einer kaputten Audit-Senke liefe endlos.

        Gefangen werden Datenbank- und Netzfehler, also das, was ein INSERT
        tatsaechlich wirft. Ein Defekt ausserhalb dieser Menge soll sichtbar
        werden, statt als verlorener Audit-Eintrag zu erscheinen.

        Vorbedingung: `status` ist "gestartet", "erledigt" oder "fehler".
            Pruefung erfolgt beim Aufrufer — alle Aufrufe stehen in dieser
            Datei und setzen ein Literal.
        Nachbedingung: Eintrag geschrieben oder `logger.critical` abgesetzt.
        """
        try:
            db_manager.execute(
                """
                INSERT INTO hintergrund_log
                    (user_id, aufgabe, status, ergebnis, verarbeitet_am)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, AUFGABE, status, ergebnis),
            )
        except (psycopg2.Error, OSError) as ex:
            logger.critical(
                f"hintergrund_log-INSERT fehlgeschlagen: {ex} "
                f"(verlorener Audit-Eintrag: {AUFGABE}/{status}/{ergebnis[:100]})"
            )

    # ─────────────────────────────────────────
    # Der aktuelle Druck
    # ─────────────────────────────────────────

    @staticmethod
    def _juengster_user_turn(user_id: str) -> dict | None:
        """Liest den juengsten annotierten User-Turn aus der Session.

        **Der Druck wird frisch gelesen, nicht dem Auftrag entnommen** (Konzept
        §8.1): Auftraege liegen Tage in der Queue, und Zuwendung zu einem
        Druck, der vorbei ist, ist keine.

        Vorbedingung: `user_id` ist nicht leer. Pruefung erfolgt beim Aufrufer.
        Nachbedingung: Ein Turn-Dict mit belegtem `emotions_vektor`, oder
            `None`, wenn die Session leer ist oder kein User-Turn im Fenster
            einen Vektor traegt.
        Fehlerfaelle: Redis nicht erreichbar oder unlesbare Saetze -> `None`
            mit `logger.exception`. Ein unlesbarer Satz wird gemeldet und
            uebersprungen, nicht stillschweigend verschluckt.

            Gefangen wird, was ein `lrange` tatsaechlich wirft: Redis- und
            Netzfehler. Ein Defekt ausserhalb dieser Menge soll sichtbar
            werden, statt als „kein Druck feststellbar" zu erscheinen —
            dieselbe Abwaegung wie beim Audit-Schreibvorgang.
        """
        session_key: str = _session_key(user_id, ASSISTANT_USER_ID, "turns")

        try:
            roh: list = redis_client.lrange(session_key, 0, -1)
        except (redis.RedisError, OSError):
            logger.exception(
                f"Nachfragen: Session '{session_key}' nicht lesbar — "
                f"kein Druck feststellbar"
            )
            return None

        if not roh:
            logger.error(
                f"Nachfragen: Session '{session_key}' ist leer — "
                f"kein Druck feststellbar"
            )
            return None

        turns: list[dict] = []
        for satz in roh[-EMOTION_VEKTOR_TURNS:]:
            try:
                turns.append(json.loads(satz))
            except (json.JSONDecodeError, TypeError):
                logger.exception(
                    f"Nachfragen: unlesbarer Turn in '{session_key}' — "
                    f"uebersprungen"
                )

        # Rueckwaerts: der juengste Turn, der ueberhaupt einen Vektor traegt.
        for turn in reversed(turns):
            if turn.get("rolle") != "user":
                continue
            if turn.get("emotions_vektor"):
                return turn

        logger.info(
            f"Nachfragen: kein User-Turn mit Vektor in den letzten "
            f"{len(turns)} Turns von '{session_key}'"
        )
        return None

    # ─────────────────────────────────────────
    # Der Reiz
    # ─────────────────────────────────────────

    @staticmethod
    def _reiz_bauen(turn: dict, thema: str, kontext: str) -> str:
        """Verdichtet Druck und Anlass zu einem Reiz — ohne Modellaufruf.

        Stufe 1 kommt ohne Sprachmodell aus (Konzept §8.3): Der Farbton spricht
        bereits im Zielregister — er beschreibt einen Zustand und adressiert
        niemanden —, ein Hintergrundaufruf kostet auf dieser Anlage 35 bis 38
        Sekunden am einzigen seriellen Platz, und die deterministische Fassung
        ist der Zeuge, gegen den eine spaetere Modellfassung zu messen waere.

        **Der Anlass gehoert ins Material, auch wenn er nicht ausgesprochen
        wird** (§8.4): Ohne ihn weiss Nova nicht, worum sie sich sorgt. Ob sie
        ihn nennt, entscheidet der CharacterGraph.

        Vorbedingung: `turn` traegt einen `emotions_vektor` aus dem Kanon;
            mindestens eines von `thema` und `kontext` ist nicht leer.
            Pruefung erfolgt beim Aufrufer.
        Nachbedingung: Nicht-leere Zeichenkette.
        Fehlerfaelle: Keine.
        """
        arousal_roh = turn.get("arousal")
        arousal: float = (
            float(arousal_roh)
            if isinstance(arousal_roh, (int, float))
            else TURN_AROUSAL_LEER
        )

        lage: str = lage_beschreiben(
            vektor=turn["emotions_vektor"],
            emotion=turn.get("emotion") or TURN_EMOTION_LEER,
            arousal=arousal,
            dynamik=turn.get("beziehungs_dynamik") or TURN_DYNAMIK_LEER,
        )

        anlass: str = kontext.strip() or thema.strip()

        return f"{lage} Es ging zuletzt um: {anlass}"

    # ─────────────────────────────────────────
    # Durchlauf
    # ─────────────────────────────────────────

    @staticmethod
    def _abbrechen(state: AgentState, user_id: str, grund: str) -> AgentState:
        """Beendet den Durchlauf als Fehler: Log, Audit, Zustand.

        Die drei Schritte stehen zusammen, weil sie immer zusammen gehoeren —
        getrennt faellt beim naechsten Fehlerpfad einer davon aus, und das ist
        genau der stille Fehler, den die Audit-Pflicht verhindern soll.

        Vorbedingung: `grund` nennt den Wert, nicht nur das Feld.
        Nachbedingung: `status="fehler"`, Audit-Eintrag geschrieben.
        """
        logger.error(f"NachfragenAgent: {grund} — verworfen")
        NachfragenAgent._audit_log(user_id, "fehler", grund)
        state["status"] = "fehler"
        state["fehler"] = grund
        return state

    def invoke(self, state: AgentState) -> AgentState:
        """Legt bei aktuellem Druck einen Zuwendungs-Reiz ab.

        Vorbedingung: `state["parameter"]` ist der Queue-Auftrag und traegt
            `thema` oder `kontext`; `state["kontext"]` traegt `user_id`.
        Nachbedingung: Bei Druck genau ein Stapel-Eintrag mit
            `aufgabe="nachfragen"` und Audit `erledigt`. Ohne Druck kein
            Eintrag und Audit `erledigt` mit Grund. Bei verletzter
            Vorbedingung kein Eintrag und Audit `fehler`.
        Fehlerfaelle: siehe die einzelnen Ruecksprungpfade — jeder meldet den
            Grund und schreibt einen Audit-Eintrag.
        """
        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID
        auftrag: dict = state.get("parameter") or {}

        self._audit_log(user_id, "gestartet", f"Auftrag fuer '{user_id}'")
        logger.info(f"NachfragenAgent: Start fuer '{user_id}'")

        # ── Eingabe-Validierung ─────────────────────
        if not isinstance(auftrag, dict):
            return self._abbrechen(
                state, user_id,
                f"Auftrag ist {type(auftrag).__name__}, erwartet dict",
            )

        thema: str = (auftrag.get("thema") or "").strip()
        kontext: str = (auftrag.get("kontext") or "").strip()

        if not thema and not kontext:
            return self._abbrechen(
                state, user_id,
                f"Auftrag ohne Thema und ohne Kontext, Felder vorhanden: "
                f"{sorted(auftrag)}",
            )

        # ── Verarbeitung: der aktuelle Druck ────────
        turn: dict | None = self._juengster_user_turn(user_id)

        if turn is None:
            return self._abbrechen(
                state, user_id,
                f"kein annotierter User-Turn mit Vektor fuer '{user_id}'",
            )

        vektor: str = turn["emotions_vektor"]

        # Zugehoerigkeit zum Kanon **vor** der Teilmengen-Frage. Ohne sie
        # waere ein unbekannter Wert von einem gueltigen „kein Druck" nicht
        # zu unterscheiden, und ein Transportfehler liefe als Ruhe durch.
        if vektor not in EMOTIONS_VEKTOREN:
            return self._abbrechen(
                state, user_id,
                f"Vektor '{vektor}' gehoert nicht zum Kanon "
                f"{sorted(EMOTIONS_VEKTOREN)}",
            )

        if vektor not in EMOTIONS_VEKTOREN_DRUCK:
            # Kein Fehler: Der Agent hat richtig gearbeitet und richtig
            # geschwiegen. Der haeufigste Ausgang bei einem alten Auftrag,
            # dessen Anlass vorbei ist (Konzept §8.5).
            grund: str = (
                f"kein Druck — Vektor '{vektor}' liegt ausserhalb von "
                f"{sorted(EMOTIONS_VEKTOREN_DRUCK)}, Auftrag vom "
                # `erstellt_am` seit dem Umzug der Queue (15.08.2026);
                # `erstellt` war der Name in der Redis-Fassung.
                f"{auftrag.get('erstellt_am', auftrag.get('erstellt', '?'))}"
            )
            logger.info(f"NachfragenAgent: {grund} — kein Stapel-Eintrag")
            self._audit_log(user_id, "erledigt", grund)
            state["status"] = "abgeschlossen"
            state["ergebnis"] = {"abgelegt": False, "vektor": vektor}
            return state

        logger.info(
            f"NachfragenAgent: Druck erkannt — Vektor '{vektor}', "
            f"Emotion '{turn.get('emotion', '')}', "
            f"Arousal {turn.get('arousal', '?')}"
        )

        reiz: str = self._reiz_bauen(turn, thema, kontext)

        # ── Ausgabe-Verifikation ────────────────────
        if not reiz.strip():
            return self._abbrechen(
                state, user_id,
                f"Reiz ist leer trotz Vektor '{vektor}' und Anlass",
            )

        # Gefangen wird, was der Ablagepfad tatsaechlich wirft: Redis- und
        # Netzfehler sowie ein Ausfall des Embed-Workers. Ein Defekt
        # ausserhalb dieser Menge soll sichtbar werden, statt als
        # fehlgeschlagene Ablage zu erscheinen.
        try:
            stack_push(
                redis_client=redis_client,
                user_id=user_id,
                aufgabe=AUFGABE,
                thema=thema or kontext[:80],
                inhalt=reiz,
                emotion=turn.get("emotion") or TURN_EMOTION_LEER,
                modus=turn.get("modus") or "",
                # Die Erregung des ausloesenden Turns ist der Wert, in dem
                # dieser Gedanke gefasst wurde — Bauteil B hebt Novas Zustand
                # spaeter darauf, falls er niedriger liegt. **Hier `None` statt
                # `TURN_AROUSAL_LEER`:** Der Ausfallwert taugt fuer eine
                # Lagebeschreibung, aber nicht als hinterlegter Level; ein
                # erfundener Wert wuerde Novas Zustand tatsaechlich verschieben.
                arousal=(
                    float(turn["arousal"])
                    if isinstance(turn.get("arousal"), (int, float))
                    else None
                ),
            )
        except (redis.RedisError, OSError, RuntimeError, ValueError) as ex:
            return self._abbrechen(
                state, user_id,
                f"{type(ex).__name__}: Stack-Push fehlgeschlagen — {ex}",
            )

        logger.info(
            f"NachfragenAgent: Reiz abgelegt ({len(reiz)} Zeichen, "
            f"Vektor '{vektor}')"
        )
        self._audit_log(
            user_id, "erledigt",
            f"Reiz abgelegt, Vektor '{vektor}', {len(reiz)} Zeichen",
        )

        state["status"] = "abgeschlossen"
        state["ergebnis"] = {"abgelegt": True, "vektor": vektor, "reiz": reiz}
        return state
