"""Akte — Erstellen und Anreichern von Delegations-Akten.

akte_erstellen: Neue Akte mit Header + erster Seite.
akte_anreichern: Bestehende Akte um eine Seite erweitern, Prioritaet erhoehen.
"""

import json
import logging

import numpy as np

from agents.base import AgentState
from config import (
    postgres_verbinden,
    DELEGATION_VERSTAERKUNG_DIVISOR,
    DELEGATION_AROUSAL_BOOST,
)

logger = logging.getLogger("ki_server.agents.delegation.akte")


def embed_text_bauen(themen: str, zusammenfassung: str = "") -> str:
    """
    Baut den Embed-Text einer Delegations-Akte — die EINZIGE Formel für
    themen_embedding (Chat 107). Der Text ist aus den persistierten
    Header-Spalten themen + zusammenfassung vollständig rekonstruierbar.

    E: mindestens eines der beiden Felder muss nicht-leer sein.
    V: Live-Formel aus duplikat_pruefen: "{themen}. {zusammenfassung}";
       ein leeres Optionalfeld entfällt sauber aus dem Text.
    A: "{themen}. {zusammenfassung}", nur "{themen}" oder nur
       "{zusammenfassung}".
    """
    hat_themen = bool(themen and themen.strip())
    hat_zusammenfassung = bool(zusammenfassung and zusammenfassung.strip())
    if not hat_themen and not hat_zusammenfassung:
        raise ValueError("embed_text_bauen(delegation): themen und zusammenfassung sind leer — kein Embed-Text baubar")
    if hat_themen and hat_zusammenfassung:
        return f"{themen}. {zusammenfassung}"
    return themen if hat_themen else zusammenfassung


def _seiten_dict(state: AgentState) -> dict:
    """Baut das Seiten-Dict aus den State-Parametern."""
    param:       dict = state["parameter"]
    salienz_obj: dict = param.get("salienz_obj", {})

    # Session-Auszug: letzte 5 User-Turns kompakt
    session_turns: list = param.get("session_turns", [])
    session_auszug: list[dict] = []
    user_count: int = 0
    for turn in reversed(session_turns):
        if turn.get("rolle") == "user" and user_count < 5:
            session_auszug.append({
                "inhalt": turn.get("inhalt", "")[:200],
                "emotion": turn.get("emotion", ""),
                "arousal": turn.get("arousal", 0.0),
            })
            user_count += 1
    session_auszug.reverse()

    # Emotions-Verlauf kompakt (Top 4)
    emotions_verlauf: list = param.get("emotions_verlauf", [])
    verlauf_kompakt: list[dict] = [
        {"emotion": e.get("emotion", ""), "gewicht": e.get("gewicht", 0.0),
         "arousal": e.get("arousal", 0.5)}
        for e in emotions_verlauf[:4]
    ]

    return {
        "trigger":             param.get("trigger", ""),
        "user_prompt":         param.get("user_prompt", ""),
        "zusammenfassung":     salienz_obj.get("zusammenfassung", ""),
        "salienz":             salienz_obj.get("salienz", 0.0),
        "valenz":              salienz_obj.get("emotionen", {}).get("valenz", "neutral"),
        "emotion":             param.get("current_emotion", "neutral"),
        "arousal":             param.get("current_arousal", 0.5),
        "emotions_vektor":     param.get("emotions_vektor", ""),
        "emotions_verlauf":    verlauf_kompakt,
        "intentionen":         param.get("user_intentionen", []),
        "modus":               param.get("gespraechs_modus", ""),
        "sprach_stil":         param.get("sprach_stil", "neutral"),
        "beziehungs_dynamik":  param.get("beziehungs_dynamik", "neutral"),
        "tone":                param.get("tone", "sachlich"),
        "session_auszug":      session_auszug,
        "fakten":              salienz_obj.get("facts", []),
    }


def akte_erstellen(state: AgentState) -> dict:
    """Erstellt eine neue Akte mit Header + erster Seite."""

    param:       dict        = state["parameter"]
    salienz_obj: dict        = param.get("salienz_obj", {})
    user_id:     str         = state["kontext"].get("user_id", "")
    embedding:   list[float] = param.get("themen_embedding", [])
    trigger:     str         = param.get("trigger", "")

    themen: str = ", ".join(salienz_obj.get("themen", []))
    salienz: float = salienz_obj.get("salienz", 0.0)
    arousal: float = param.get("current_arousal", 0.5)

    # Initiale Prioritaet
    prioritaet: float = salienz * (1.0 + arousal * DELEGATION_AROUSAL_BOOST)

    seite: dict = _seiten_dict(state)

    embedding_str: str = "[" + ",".join(str(v) for v in embedding) + "]"

    conn = None
    akte_id: int = 0

    try:
        conn = postgres_verbinden()
        cursor = conn.cursor()

        # Header. zusammenfassung ist der zweite Baustein des Embed-Texts
        # (duplikat_pruefen: "{themen}. {zusammenfassung}") — sie wird
        # mitpersistiert, damit der Vektor aus dem gespeicherten Zustand
        # rekonstruierbar bleibt (Chat 107).
        cursor.execute(
            """
            INSERT INTO delegations_akten (
                user_id, themen, zusammenfassung, themen_embedding,
                trigger, prioritaet, seiten
            ) VALUES (%s, %s, %s, %s::vector, %s, %s, 1)
            RETURNING id
            """,
            (user_id, themen, seite["zusammenfassung"], embedding_str, trigger, prioritaet),
        )
        akte_id = cursor.fetchone()[0]

        # Erste Seite
        cursor.execute(
            """
            INSERT INTO delegations_seiten (
                akte_id, seite, trigger, user_prompt, zusammenfassung,
                salienz, valenz, emotion, arousal, emotions_vektor,
                emotions_verlauf, intentionen, modus, sprach_stil,
                beziehungs_dynamik, tone, session_auszug, fakten
            ) VALUES (
                %s, 1, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                akte_id,
                seite["trigger"],
                seite["user_prompt"],
                seite["zusammenfassung"],
                seite["salienz"],
                seite["valenz"],
                seite["emotion"],
                seite["arousal"],
                seite["emotions_vektor"],
                json.dumps(seite["emotions_verlauf"]),
                json.dumps(seite["intentionen"]),
                seite["modus"],
                seite["sprach_stil"],
                seite["beziehungs_dynamik"],
                seite["tone"],
                json.dumps(seite["session_auszug"]),
                json.dumps(seite["fakten"]),
            ),
        )

        conn.commit()

        logger.info(
            f"Akte erstellt: id={akte_id}, themen='{themen}', "
            f"trigger={trigger}, prio={prioritaet:.2f}"
        )

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Akte erstellen fehlgeschlagen")
        if conn:
            conn.rollback()
        return {
            "status": "fehler",
            "fehler": str(fehler),
            "schritte": state["schritte"] + [{"node": "akte_erstellen", "ergebnis": "fehler"}],
        }

    finally:
        if conn:
            conn.close()

    return {
        "status": "abgeschlossen",
        "ergebnis": {"akte_id": akte_id, "aktion": "erstellt"},
        "schritte": state["schritte"] + [{
            "node": "akte_erstellen", "ergebnis": "erstellt", "akte_id": akte_id,
        }],
    }


def akte_anreichern(state: AgentState) -> dict:
    """Reichert eine bestehende Akte um eine neue Seite an."""

    param:    dict = state["parameter"]
    akte_id:  int  = param["bestehende_akte_id"]
    trigger:  str  = param.get("trigger", "")

    salienz_obj:  dict  = param.get("salienz_obj", {})
    neue_salienz: float = salienz_obj.get("salienz", 0.0)
    neuer_arousal: float = param.get("current_arousal", 0.5)

    seite: dict = _seiten_dict(state)

    conn = None
    neue_seite_nr: int = 0
    neue_prioritaet: float = 0.0

    # Trigger-Staerke: effektivwert(3) > vektor(2) > salienz(1)
    trigger_rang: dict[str, int] = {"effektivwert": 3, "vektor": 2, "salienz": 1}

    try:
        conn = postgres_verbinden()
        cursor = conn.cursor()

        # Bestehende Akte lesen
        cursor.execute(
            "SELECT seiten, trigger, prioritaet FROM delegations_akten WHERE id = %s",
            (akte_id,),
        )
        row = cursor.fetchone()
        if not row:
            logger.warning(f"Akte {akte_id} nicht gefunden")
            conn.close()
            return {
                "status": "fehler",
                "fehler": f"Akte {akte_id} nicht gefunden",
                "schritte": state["schritte"] + [{"node": "akte_anreichern", "ergebnis": "nicht_gefunden"}],
            }

        alte_seiten:     int   = row[0]
        alter_trigger:   str   = row[1]
        alte_prioritaet: float = row[2]
        neue_seite_nr = alte_seiten + 1

        # Max-Arousal ueber alle bisherigen Seiten
        cursor.execute(
            "SELECT COALESCE(MAX(arousal), 0.5) FROM delegations_seiten WHERE akte_id = %s",
            (akte_id,),
        )
        alter_max_arousal: float = cursor.fetchone()[0]
        max_arousal: float = max(alter_max_arousal, neuer_arousal)

        # Neue Prioritaet berechnen
        verstaerkung: float = neue_salienz / DELEGATION_VERSTAERKUNG_DIVISOR
        alter_boost:  float = 1.0 + alter_max_arousal * DELEGATION_AROUSAL_BOOST
        neuer_boost:  float = 1.0 + max_arousal * DELEGATION_AROUSAL_BOOST
        neue_prioritaet = (alte_prioritaet + verstaerkung) * neuer_boost / alter_boost

        # Trigger upgraden wenn neuer staerker
        neuer_trigger: str = alter_trigger
        if trigger_rang.get(trigger, 0) > trigger_rang.get(alter_trigger, 0):
            neuer_trigger = trigger

        # Header updaten. Bewusst NICHT dabei: themen, zusammenfassung,
        # themen_embedding — alle drei sind auf den Anlege-Zeitpunkt
        # eingefroren. Der Vektor wird beim Anreichern nicht neu erzeugt;
        # den Header-Text nachzuziehen, ohne neu zu embedden, wuerde Text
        # und Vektor auseinandertreiben (Chat 107). Die Zusammenfassung des
        # neuen Turns steht in der neuen Seite.
        cursor.execute(
            """
            UPDATE delegations_akten
            SET seiten = %s, prioritaet = %s, trigger = %s, aktualisiert_am = NOW()
            WHERE id = %s
            """,
            (neue_seite_nr, neue_prioritaet, neuer_trigger, akte_id),
        )

        # Neue Seite einfuegen
        cursor.execute(
            """
            INSERT INTO delegations_seiten (
                akte_id, seite, trigger, user_prompt, zusammenfassung,
                salienz, valenz, emotion, arousal, emotions_vektor,
                emotions_verlauf, intentionen, modus, sprach_stil,
                beziehungs_dynamik, tone, session_auszug, fakten
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                akte_id,
                neue_seite_nr,
                seite["trigger"],
                seite["user_prompt"],
                seite["zusammenfassung"],
                seite["salienz"],
                seite["valenz"],
                seite["emotion"],
                seite["arousal"],
                seite["emotions_vektor"],
                json.dumps(seite["emotions_verlauf"]),
                json.dumps(seite["intentionen"]),
                seite["modus"],
                seite["sprach_stil"],
                seite["beziehungs_dynamik"],
                seite["tone"],
                json.dumps(seite["session_auszug"]),
                json.dumps(seite["fakten"]),
            ),
        )

        conn.commit()

        logger.info(
            f"Akte angereichert: id={akte_id}, seite={neue_seite_nr}, "
            f"prio {alte_prioritaet:.2f} -> {neue_prioritaet:.2f}, "
            f"trigger={neuer_trigger}"
        )

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Akte anreichern fehlgeschlagen")
        if conn:
            conn.rollback()
        return {
            "status": "fehler",
            "fehler": str(fehler),
            "schritte": state["schritte"] + [{"node": "akte_anreichern", "ergebnis": "fehler"}],
        }

    finally:
        if conn:
            conn.close()

    return {
        "status": "abgeschlossen",
        "ergebnis": {"akte_id": akte_id, "aktion": "angereichert", "seite": neue_seite_nr},
        "schritte": state["schritte"] + [{
            "node": "akte_anreichern", "ergebnis": "angereichert",
            "akte_id": akte_id, "seite": neue_seite_nr,
        }],
    }
