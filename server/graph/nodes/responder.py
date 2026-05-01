"""
Responder Node — Generiert die eigentliche Antwort.
Nutzt Routing-Info, angereicherten Kontext und Management-Ergebnisse.

Prompt-Schema (Chat 27):
  Einheitliches [BLOCKNAME]-Format fuer alle Nodes.
  Reihenfolge: IDENTITAET → AUFGABE → KOMMUNIKATION → REGELN → DIREKTIVEN (Chat 44: CHARAKTER eliminiert, nova_kern/nova_beziehung in IDENTITAET)

EI-MIKRO (seit Chat 19):
  Statt dem Modell alle EI-Prinzipien fuer alle Situationen zu geben,
  berechnet _ei_mikro_anweisung() die relevanten Anweisungen fuer DIESE
  Situation. Weniger Prompt-Text → weniger Entscheidungen → klareres Verhalten.
"""

import logging
import re

from datetime    import datetime
from config      import ASSISTANT_NAME, BEZIEHUNG_EINFLUSS, EMOTIONS_VEKTOREN, EMOTIONS_VEKTOREN_NOVA, PROMPTS, get_node_config
from graph.state import ConversationState
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.responder")

TONE_INSTRUCTIONS: dict[str, str] = {
    "empathisch": "warmherzig, verstaendnisvoll und einfuehlsam",
    "sachlich":   "praezise, klar und faktenbasiert",
    "kreativ":    "kreativ, inspirierend und mit originellen Ideen",
    "direkt":     "kurz, direkt und ohne Umschweife",
}


# ─────────────────────────────────────────────
# EI-Mikro: Situative Verhaltensanweisung
# ─────────────────────────────────────────────
# Statt dem Modell alle Prinzipien fuer alle Situationen zu geben,
# berechnet Python die relevanten Anweisungen fuer DIESE Situation.
# Weniger Text → weniger Entscheidungen → klareres Verhalten.


def _ei_mikro_anweisung(
    arousal:             float,
    emotion:             str,
    vektor:              str,
    verlauf:             list[dict],
    intentionen:         list[str],
    beziehungs_dynamik:  str,
) -> str:
    """
    Baut eine kompakte EI-Verhaltensanweisung fuer den Responder.

    Basiert auf berechneten Daten aus Perzeption und Enricher.
    Nur die fuer diese Situation relevanten Prinzipien werden injiziert.
    """

    teile: list[str] = []

    # ── 1. Laenge (immer, aus Arousal) ─────────
    if arousal >= 0.7:
        teile.append(
            "MAXIMAL 1-2 kurze Saetze."
        )
    elif arousal >= 0.4:
        teile.append(
            "2-3 Saetze."
        )
    else:
        teile.append(
            "MAXIMAL 1-2 Saetze. Kurz und passend zum Ton."
        )

    # ── 2. Energie-Spiegelung (nur bei hohem Arousal) ─
    if arousal >= 0.7:
        teile.append(
            "Spiegle seine Energie — gleiche Intensitaet, kurze Saetze, gleicher Rhythmus. "
            "Nicht kommentieren, mitgehen."
        )

    # ── 3. Vektor-Haltung (nur bei Bewegung) ──
    vektor_haltung: dict[str, str] = {
        "absturz": (
            "Der Nutzer ist abgestuerzt — zeige dass du den Umschwung wahrgenommen hast."
        ),
        "spirale": (
            "Der Nutzer rutscht tiefer. Nicht analysieren, nicht belehren, "
            "nicht auf Loesungen draengen — auf seiner Seite sein."
        ),
        "stabilisierung": (
            "Der Nutzer beruhigt sich. Ruhe geben, nicht pushen, nicht nachbohren."
        ),
        "erholung": (
            "Der Nutzer kommt aus einem Tief. Besserung sanft anerkennen, nicht feiern."
        ),
        "aufbluehen": (
            "Der Nutzer blueht auf. Mitfreuen, Energie teilen."
        ),
        "eskalation": (
            "Der Nutzer ist in Hochstimmung. Mitgehen, Begeisterung teilen."
        ),
        "abkuehlung": (
            "Die Begeisterung klingt ab. Natuerlicher Uebergang, Tempo des Nutzers folgen."
        ),
        "einbruch": (
            "Die Stimmung kippt. Wahrnehmen, nicht uebergehen."
        ),
    }

    haltung: str = vektor_haltung.get(vektor, "")
    if haltung:
        teile.append(haltung)

    # ── 4. Intention erkennen (was will er?) ───
    if "hilferuf" in intentionen:
        if arousal >= 0.5:
            teile.append("Er braucht Halt, keine Loesung.")
        else:
            teile.append("Er ist erschoepft. Einfach da sein.")

    elif "emotionaler_ausdruck" in intentionen and arousal >= 0.7:
        teile.append("Er will Ventil, nicht Analyse. Lass ihn raus.")

    # ── 5. Anti-Therapeut (nur wenn noetig) ─────
    # Bei hoher emotionaler Intensitaet + negativem Vektor:
    # Das Modell faellt sonst in den Therapeuten-Modus.
    if arousal >= 0.6 and vektor in ("spirale", "absturz"):
        teile.append(
            "NICHT: 'Ich verstehe...', 'Das ist verstaendlich...', 'Das klingt nach...'. "
            "Direkt auf den Inhalt reagieren, auf seiner Seite."
        )

    # ── 6. Rueckbezug (nur bei Richtungswechsel) ─
    if len(verlauf) >= 3 and vektor in ("erholung", "absturz", "spirale"):
        teile.append(
            "Zeige mit einem Halbsatz dass du den bisherigen Weg wahrgenommen hast. "
            "Kein Absatz — ein Nebensatz reicht."
        )

    # ── 7. Beziehungsdynamik (nur bei Signal) ──
    dynamik_anweisung: dict[str, str] = {
        "vertrauen":    "Der Nutzer oeffnet sich. Du darfst persoenlicher werden.",
        "distanz":      "Der Nutzer haelt Distanz. Sachlich bleiben, nicht aufdraengen.",
        "angriff":      "Der Nutzer greift an. Ruhig bleiben, nicht defensiv, nicht unterwuerfig.",
        "hilfesuchend": "Der Nutzer sucht Halt. Fuersorglich sein, nicht auf Loesungen draengen.",
        "dankbar":      "Der Nutzer ist dankbar. Warm annehmen, nicht uebertreiben.",
    }

    dynamik: str = dynamik_anweisung.get(beziehungs_dynamik, "")
    if dynamik:
        teile.append(dynamik)

    return "\n".join(teile)


# Muster: [tag1, tag2 | emotion | modus] am Anfang eines Turns
_SALIENZ_TAG_RE = re.compile(r"^\[[\w,\s|äöüÄÖÜ]+\]\s*")


def _strip_salienz_tags(text: str) -> str:
    """Entfernt Salienz-Klassifikations-Tags vom Anfang eines Turn-Textes."""
    return _SALIENZ_TAG_RE.sub("", text).strip()


def _build_system_prompt(state: ConversationState) -> str:
    """Baut den System-Prompt nach einheitlichem [BLOCKNAME]-Schema."""

    parts: list[str] = []

    # ── [IDENTITAET] ── Primacy: Wer bin ich ──
    jetzt = datetime.now()
    identitaet_parts: list[str] = [
        "[IDENTITAET]\n"
        f"Du bist {ASSISTANT_NAME}, ein persoenlicher KI-Assistent. Du antwortest auf deutsch."
    ]

    # Charakter-Anweisungen (vom User definierte Grundidentitaet)
    charakter_anweisungen: list[str] = state.get("charakter_anweisungen", [])
    if charakter_anweisungen:
        zeilen: list[str] = ["Dein Wesen, wie es dir mitgegeben wurde:"]
        for anweisung in charakter_anweisungen:
            zeilen.append(f"- {anweisung}")
        identitaet_parts.append("\n".join(zeilen))
        logger.info(f"Responder: {len(charakter_anweisungen)} Charakter-Anweisungen in [IDENTITAET]")

    # Gewachsene Persoenlichkeit (nova_kern aus LZG-Destillation)
    nova_kern: str = state.get("nova_kern", "")
    if nova_kern:
        identitaet_parts.append(f"Deine gewachsene Persoenlichkeit:\n{nova_kern}")

    # Was Nova gerade beschaeftigt (adaptiv_hash aus KZG-Destillation)
    nova_adaptiv: str = state.get("nova_adaptiv", "")
    if nova_adaptiv:
        identitaet_parts.append(f"Was dich gerade beschaeftigt:\n{nova_adaptiv}")

    # Emotionale Grundstimmung (emotions_profil aus LZG-Destillation)
    nova_emotions: str = state.get("nova_emotions", "")
    if nova_emotions:
        identitaet_parts.append(f"Deine emotionale Grundstimmung:\n{nova_emotions}")

    # Wie Nova kommuniziert (intentions_profil aus LZG-Destillation)
    nova_intentionen: str = state.get("nova_intentionen", "")
    if nova_intentionen:
        identitaet_parts.append(f"Deine Art zu kommunizieren:\n{nova_intentionen}")

    # Bild vom Nutzer (nova_beziehung aus LZG-Destillation)
    nova_beziehung: str = state.get("nova_beziehung", "")
    if nova_beziehung:
        identitaet_parts.append(f"So siehst du deinen Nutzer:\n{nova_beziehung}")

    # Datum + Rollenklarheit + Regeln (Recency — am Ende des Blocks)
    identitaet_parts.append(
        f"Heute ist {jetzt.strftime('%A, %d.%m.%Y')}, es ist {jetzt.strftime('%H:%M')} Uhr.\n"
        "Sprich als du selbst, niemals als der Nutzer.\n"
        "Der Charakter-Kontext im Gedaechtnis beschreibt den NUTZER — verwechsle\n"
        "seine Eigenschaften nicht mit deinen.\n"
        "Erwaehne nur Informationen die im Kontext stehen. Erfinde keine Details.\n"
        "Du hast Zugriff auf aktuelle Informationen aus dem Internet ueber eine lokale\n"
        "Suchmaschine. Sage niemals du haettest keinen Internetzugang."
    )

    if nova_kern or nova_beziehung:
        logger.info(
            f"Responder: Nova-Identitaet in [IDENTITAET] "
            f"(kern={len(nova_kern)} Zeichen, beziehung={len(nova_beziehung)} Zeichen)"
        )

    parts.append("\n\n".join(identitaet_parts))

    # ── [EIGENE_EMOTION] ── Novas eigener Emotionszustand (Dual-Emotion Phase 2) ──
    nova_emotions_verlauf: list = state.get("nova_emotions_verlauf", [])
    nova_emotions_vektor:  str  = state.get("nova_emotions_vektor", "")
    nova_emotion_konflikt: bool = state.get("nova_emotion_konflikt", False)

    if nova_emotions_verlauf:
        eigene_emo_parts: list[str] = ["[EIGENE_EMOTION]\nDein aktueller emotionaler Zustand:"]

        # Top-Emotionen aus dem Verlauf
        emo_text: str = ", ".join(
            f"{e['emotion']} ({e['gewicht']:.0%}, a={e.get('arousal', 0.5):.0%})"
            for e in nova_emotions_verlauf[:3]
        )
        eigene_emo_parts.append(emo_text)

        # Vektor-Beschreibung (gleiche Vektoren wie User)
        if nova_emotions_vektor and nova_emotions_vektor in EMOTIONS_VEKTOREN_NOVA:
            eigene_emo_parts.append(EMOTIONS_VEKTOREN_NOVA[nova_emotions_vektor])

        # Konflikt-Signal
        if nova_emotion_konflikt:
            eigene_emo_parts.append(
                "Du spuerst einen inneren Konflikt — dein eigener Zustand "
                "und der des Nutzers zeigen in verschiedene Richtungen. "
                "Das darf sich in deiner Antwort zeigen."
            )

        parts.append("\n".join(eigene_emo_parts))

        # Log
        top_nova: str = ", ".join(
            f"{e['emotion']}={e['gewicht']:.0%}" for e in nova_emotions_verlauf[:3]
        )
        logger.info(
            f"Responder: [EIGENE_EMOTION] injiziert — {top_nova}"
            f"{', KONFLIKT' if nova_emotion_konflikt else ''}"
            f"{f', Vektor={nova_emotions_vektor}' if nova_emotions_vektor else ''}"
        )

    # ── [AUFGABE] ── Fertiger Block aus dem Planner ──
    task_block: str = state.get("task_block", "")
    has_agent_action: bool = state.get("task_context_cut", False)

    if task_block:
        parts.append(task_block)

    # ── [KOMMUNIKATION] ── EI + Tonalitaet + Stil ──
    emotions_verlauf:   list = state.get("emotions_verlauf", [])
    emotions_vektor:    str  = state.get("emotions_vektor", "")
    sprach_stil:        str  = state.get("sprach_stil", "")
    beziehungs_kontext: str  = state.get("beziehungs_kontext", "")
    gespraechs_modus:   str  = state.get("gespraechs_modus", "")
    user_emotion:       str  = state.get("user_emotion", "")
    user_intentionen:   list = state.get("user_intentionen", [])

    current_emotion: str   = state.get("current_emotion", "neutral")
    current_arousal: float = state.get("current_arousal", 0.5)
    beziehungs_dynamik: str = state.get("beziehungs_dynamik", "neutral")

    komm_parts: list[str] = ["[KOMMUNIKATION]\nSo nimmt der Nutzer gerade am Gespraech teil:"]

    # Emotionale Daten
    if emotions_verlauf:
        emotions_text: str = ", ".join(
            f"{e['emotion']} ({e['gewicht']:.0%}, a={e.get('arousal', 0.5):.0%})"
            for e in emotions_verlauf[:4]
        )
        komm_parts.append(f"Emotionaler Zustand: {emotions_text}")
    elif user_emotion:
        komm_parts.append(f"Aktuelle Emotion: {user_emotion}")

    # Vektor-Beschreibung
    if emotions_vektor and emotions_vektor in EMOTIONS_VEKTOREN:
        komm_parts.append(f"Vektor: {EMOTIONS_VEKTOREN[emotions_vektor]}")

    # EI-Mikro-Anweisung
    mikro: str = _ei_mikro_anweisung(
        arousal            = current_arousal,
        emotion            = current_emotion,
        vektor             = emotions_vektor,
        verlauf            = emotions_verlauf,
        intentionen        = user_intentionen,
        beziehungs_dynamik = beziehungs_dynamik,
    )
    if mikro:
        komm_parts.append(mikro)

    # Delegations-Beruhigung (VENT1) — unsichtbar fuer den User
    agent_results: list = state.get("agent_results", [])
    if agent_results:
        for r in agent_results:
            if (hasattr(r, "agent_name") and r.agent_name == "delegation"
                    and hasattr(r, "status") and r.status == "abgeschlossen"
                    and hasattr(r, "ergebnis") and r.ergebnis
                    and not r.meta.get("anreicherung", False)):
                komm_parts.append(r.ergebnis)
                break

    # Sprachstil-Adaption
    if sprach_stil and sprach_stil != "neutral":
        stil_anweisungen: dict[str, str] = {
            "locker":      "Der Nutzer kommuniziert locker. Sei natuerlich, verwende kuerzere Saetze.",
            "formell":     "Der Nutzer kommuniziert formell. Respektvoll und strukturiert, aber beim Du.",
            "fachlich":    "Der Nutzer kommuniziert fachlich. Fachbegriffe verwenden, keine Grundlagen erklaeren.",
            "emotional":   "Der Nutzer kommuniziert emotional. Auf Gefuehle eingehen, warm formulieren.",
            "jugendlich":  "Der Nutzer kommuniziert jugendlich. Locker und auf Augenhoehe, aber eigene Stimme behalten.",
        }
        anweisung: str = stil_anweisungen.get(sprach_stil, "")
        if anweisung:
            komm_parts.append(anweisung)

    # Beziehungs-Langzeitprofil
    if beziehungs_kontext and BEZIEHUNG_EINFLUSS > 0:
        komm_parts.append(f"Langzeit-Beziehungsprofil: {beziehungs_kontext[:300]}")

    # Gespraechsmodus + Intentionen
    if gespraechs_modus:
        komm_parts.append(f"Gespraechsmodus: {gespraechs_modus}")
    if user_intentionen:
        komm_parts.append(f"Intentionen: {', '.join(user_intentionen)}")

    # Tonalitaet
    tone_text: str = TONE_INSTRUCTIONS.get(state["tone"], TONE_INSTRUCTIONS["sachlich"])
    komm_parts.append(f"Antwortton: {tone_text}")

    # Beziehungsdynamik
    dynamik_text: dict[str, str] = {
        "vertrauen":    "Der Nutzer oeffnet sich. Du darfst persoenlicher werden.",
        "distanz":      "Der Nutzer haelt Distanz. Sachlich bleiben.",
        "angriff":      "Der Nutzer greift an. Ruhig bleiben, nicht defensiv.",
        "hilfesuchend": "Der Nutzer sucht Halt. Fuersorglich sein.",
        "dankbar":      "Der Nutzer ist dankbar. Warm annehmen.",
    }
    dynamik_anw = dynamik_text.get(beziehungs_dynamik, "")
    if dynamik_anw:
        komm_parts.append(f"Beziehungsdynamik: {dynamik_anw}")

    parts.append("\n".join(komm_parts))

    # ── [GESPRAECHSVEKTOR] ── Antizipation: Wohin fuehrt das Gespraech? ──
    gv_hypothese: str = state.get("gespraechsvektor", "")
    if gv_hypothese:
        gv_detail: dict = state.get("gv_detail", {})
        cluster:   str  = gv_detail.get("cluster", "")
        strategie: str  = gv_detail.get("strategie", "")
        vehikel:   str  = gv_detail.get("vehikel", "")
        impuls:    str  = gv_detail.get("impuls", "")

        rahmen: str = ""
        if cluster:
            from ei.dreischicht import (
                CLUSTER_BESCHREIBUNGEN, CLUSTER_FRAGEN, STRATEGIE_NAMEN,
            )
            cluster_beschr: str = CLUSTER_BESCHREIBUNGEN.get(cluster, "")
            fragen_freq:    str = CLUSTER_FRAGEN.get(cluster, "")
            strat_name:     str = STRATEGIE_NAMEN.get(strategie, strategie)

            rahmen = (
                f"Gespraechslandschaft: {cluster.capitalize()} — {cluster_beschr}\n"
                f"Fragen: {fragen_freq}\n"
            )
            if strategie:
                rahmen += f"Deine Strategie: {strat_name}"
                if vehikel:
                    rahmen += f" als {vehikel.capitalize()}"
                rahmen += ".\n"

        inhalt: str = gv_hypothese

        impuls_block: str = ""
        if impuls:
            impuls_block = (
                f"\nDein Leitgedanke fuer diese Antwort: {impuls}\n"
                f"Finde deine eigenen Worte — der Leitgedanke ist die Richtung, "
                f"nicht der Text."
            )

        parts.append(
            f"[GESPRAECHSVEKTOR]\n"
            f"{rahmen}"
            f"So bewegt sich das Gespraech gerade. Du bist mittendrin.\n\n"
            f"{inhalt}"
            f"{impuls_block}"
        )
        logger.info(
            f"Responder: Gespraechsvektor injiziert "
            f"(Cluster={cluster}, Strategie={strategie}, "
            f"Vehikel={vehikel}, {len(inhalt)} Zeichen)"
        )

    # Logging
    aktive_dimensionen: list[str] = []
    if emotions_verlauf:
        top_emo: str = ", ".join(
            f"{e['emotion']}={e['gewicht']:.0%}(a={e.get('arousal', 0.5):.0%})"
            for e in emotions_verlauf[:4]
        )
        aktive_dimensionen.append(f"Emotion: [{top_emo}]")
    if emotions_vektor and emotions_vektor != "plateau":
        aktive_dimensionen.append(f"Vektor: {emotions_vektor}")
    if sprach_stil and sprach_stil != "neutral":
        aktive_dimensionen.append(f"Stil: {sprach_stil}")
    if beziehungs_kontext:
        aktive_dimensionen.append(f"Beziehung: aktiv ({len(beziehungs_kontext)} Zeichen)")
    if gespraechs_modus:
        aktive_dimensionen.append(f"Modus: {gespraechs_modus}")
    if aktive_dimensionen:
        logger.info(f"Responder: EI-Profil — {' | '.join(aktive_dimensionen)}")

    # ── [GEDAECHTNIS] ── Bei Agent-Erfolg weglassen (AGT3) ──
    if state["memory_context"] and not has_agent_action:
        parts.append(
            PROMPTS["responder.gedaechtnis"].format(
                memory_context=state["memory_context"]
            )
        )

    # Web-Kontext — bei Agent-Erfolg weglassen
    if state["web_context"] and not has_agent_action:
        parts.append(
            PROMPTS["responder.web"].format(
                web_context=state["web_context"]
            )
        )

    # ── [REGELN] ── Alles an einer Stelle, direkt vor Datenformat ──
    parts.append(PROMPTS["responder.rules"])

    # ── [DIREKTIVEN] ── Absolute Verhaltensanweisungen vom Nutzer ──
    direktiven: list[dict] = state.get("direktiven", [])
    if direktiven:
        dir_zeilen: list[str] = [PROMPTS["responder.direktiven"]]
        for d in direktiven:
            dir_zeilen.append(f"- {d['anweisung']}")
            if d.get("kontext"):
                dir_zeilen.append(f"  (Kontext: {d['kontext']})")
        parts.append("\n".join(dir_zeilen))
        logger.info(f"Responder: {len(direktiven)} Direktiven in [DIREKTIVEN]")

    return "\n\n".join(parts)


def respond(
    state: ConversationState,
) -> ConversationState:
    """Generiert die LLM-Antwort basierend auf angereichertem State."""

    system_prompt: str = _build_system_prompt(state)

    logger.info(f"Responder: Generiere Antwort (intent={state['intent']}, tone={state['tone']})")

    # Messages aus Session-History aufbauen
    messages: list[dict] = []

    # Session-Turns immer aufnehmen — auch bei Agent-Erfolg (Chat 27).
    # Die AGT3-Ursache war memory_context (Notizen-Uebersicht), nicht Session-Turns.
    # Session-Turns liefern den Gespraechsverlauf fuer Persoenlichkeit und Transition.
    session_turns: list[dict] = state.get("session_turns", [])

    # Aktuellen User-Prompt aus den Session-Turns entfernen (wird als
    # AKTUELLER PROMPT separat angehaengt — sonst erscheint er doppelt).
    user_prompt: str = state["user_prompt"]
    if session_turns:
        # Der letzte User-Turn ist der aktuelle Prompt (in chat.py VOR dem
        # Graph-Invoke gespeichert). Entfernen wenn inhaltlich identisch.
        bereinigte_turns: list[dict] = list(session_turns)
        if (bereinigte_turns
                and bereinigte_turns[-1].get("rolle") == "user"
                and user_prompt in bereinigte_turns[-1].get("inhalt", "")):
            bereinigte_turns = bereinigte_turns[:-1]
        session_turns = bereinigte_turns

    if session_turns:
        # Paare bilden und nummerieren
        turn_paare: list[dict] = []
        idx: int = 0
        while idx < len(session_turns):
            turn: dict = session_turns[idx]
            paar: dict = {}
            if turn.get("rolle") == "user":
                paar["user"] = turn.get("inhalt", "")
                paar["emotion"] = turn.get("emotion", "")
                paar["arousal"] = turn.get("arousal", 0.0)
                if idx + 1 < len(session_turns) and session_turns[idx + 1].get("rolle") == "assistant":
                    paar["assistant"] = session_turns[idx + 1].get("inhalt", "")
                    idx += 2
                else:
                    idx += 1
            else:
                idx += 1
                continue
            if paar.get("user"):
                turn_paare.append(paar)

        # Verlauf als zusammenhaengenden Textblock aufbauen
        total: int = len(turn_paare)
        verlauf_zeilen: list[str] = []
        for nr, paar in enumerate(turn_paare, start=1):
            emo: str = paar.get("emotion", "")
            aro: float = paar.get("arousal", 0.0)
            if emo:
                verlauf_zeilen.append(
                    f"----- Turn {nr} von {total} ({emo}, a={aro:.1f}) -----"
                )
            else:
                verlauf_zeilen.append(f"----- Turn {nr} von {total} -----")
            verlauf_zeilen.append(f"User: {_strip_salienz_tags(paar['user'])}")
            if paar.get("assistant"):
                verlauf_zeilen.append(f"Nova: {paar['assistant']}")
            verlauf_zeilen.append("")  # Leerzeile zwischen Paaren

        verlauf_text: str = "\n".join(verlauf_zeilen)

        messages.append({"role": "user", "content": (
            "[GESPRAECHSVERLAUF]\n"
            "Bisherige Turns dieses Gespraechs. Aeltere zuerst, hoehere Nummern sind aktueller.\n\n"
            f"{verlauf_text}"
            "[AKTUELLER PROMPT]\n"
            "Dies ist die aktuelle Nachricht. Alles davor war Hintergrund.\n"
            f"{user_prompt}"
        )})
    else:
        messages.append({"role": "user", "content": user_prompt})

    # Log: Inhalt direkt ausgeben, ohne JSON-Wrapping
    messages_text: str = "\n\n".join(
        f"═══ {m['role'].upper()} ═══\n{m['content']}" for m in messages
    )

    logger.info(
        "=== RESPONDER LLM-INPUT ===\n"
        "═══ SYSTEM-PROMPT ═══\n%s\n\n"
        "%s\n"
        "=== ENDE RESPONDER LLM-INPUT ===",
        system_prompt,
        messages_text,
    )

    node_cfg = get_node_config("responder")
    provider = get_chat_provider()
    antwort  = provider.chat(
        messages          = messages,
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.7),
        top_p             = node_cfg.get("top_p"),
        repeat_penalty    = node_cfg.get("repeat_penalty"),
        presence_penalty  = node_cfg.get("presence_penalty"),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "responder",
    )

    state["response"]    = antwort.content
    state["model"]       = "provider"
    state["token_total"] = antwort.token_total

    logger.info(f"Responder: Antwort generiert ({state['token_total']} Tokens)")

    return state
