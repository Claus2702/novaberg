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
from services.model_services import model_service, ChatRequest

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


def _reiz_ist_eigener_gedanke(state: ConversationState) -> bool:
    """Prueft, ob der Reiz dieses Durchlaufs von Nova selbst stammt.

    Ein Pixie-Impuls reist als `user_prompt` durch den Graphen — derselbe
    Reiz-Platz wie eine Nutzer-Eingabe, aber anderer Urheber. Der Marker steht
    ausdruecklich im Event-Payload; `event_source == "character"` allein
    genuegt nicht, weil der Thinker-Retry dieselbe Quelle traegt und dabei eine
    echte Nutzer-Aeusserung wiederholt.

    Vorbedingung: keine — ein fehlender Payload heisst „nicht von Nova".
    Nachbedingung: True nur bei ausdruecklich markierter eigener Herkunft.
    """
    # ── Eingabe-Validierung ─────────────────────
    payload: dict = state.get("event_payload") or {}

    # ── Verarbeitung / Ausgabe ──────────────────
    return payload.get("reiz_herkunft") == "eigener_impuls"


def _build_system_prompt(state: ConversationState) -> str:
    """Baut den System-Prompt nach einheitlichem [BLOCKNAME]-Schema."""
    parts: list[str] = []

    external = state.get("external")
    internal = state.get("internal")

    # ── [IDENTITAET] ── Primacy: Wer bin ich ──
    jetzt = datetime.now()
    identitaet_parts: list[str] = [
        "[IDENTITAET]\n"
        f"Du bist {ASSISTANT_NAME}, ein persoenlicher KI-Assistent. Du antwortest auf deutsch."
    ]

    # Die Charakter-Anweisungen stehen NICHT mehr hier, sondern als letzter
    # Block des Prompts ([DEIN WESEN]). Oben bilden alle Bloecke zusammen eine
    # breite Grundlage — Persoenlichkeit, Stimmung, Beziehung, Regeln. Das
    # vom Nutzer gesetzte Wesen soll sich dagegen nicht einreihen, sondern
    # zuletzt stehen und damit staerker wirken (Recency).

    # Gewachsene Persoenlichkeit (kern aus LZG-Destillation, internal.character.core)
    nova_kern: str = internal.character.core if internal else ""
    if nova_kern:
        identitaet_parts.append(f"Deine gewachsene Persoenlichkeit:\n{nova_kern}")

    # Was Nova gerade beschaeftigt (adaptive aus KZG-Destillation)
    nova_adaptiv: str = internal.character.adaptive if internal else ""
    if nova_adaptiv:
        identitaet_parts.append(f"Was dich gerade beschaeftigt:\n{nova_adaptiv}")

    # Emotionale Grundstimmung (emotions_profil aus LZG-Destillation)
    nova_emotions: str = internal.character.emotions if internal else ""
    if nova_emotions:
        identitaet_parts.append(f"Deine emotionale Grundstimmung:\n{nova_emotions}")

    # Wie Nova kommuniziert (intentions_profil aus LZG-Destillation)
    nova_intentionen: str = internal.character.intentions if internal else ""
    if nova_intentionen:
        identitaet_parts.append(f"Deine Art zu kommunizieren:\n{nova_intentionen}")

    # Bild vom Nutzer (beziehungsprofil aus LZG-Destillation)
    nova_beziehung: str = internal.character.relationship if internal else ""
    if nova_beziehung:
        identitaet_parts.append(f"So siehst du deinen Nutzer:\n{nova_beziehung}")

    # Datum + Rollenklarheit + Regeln (Recency — am Ende des Blocks)
    identitaet_parts.append(
        # Drei Saetze sind seit der Trennung in den Verfasser gewandert: der
        # Hinweis auf den Charakter-Kontext im Gedaechtnis, "erwaehne nur
        # Informationen die im Kontext stehen" und der Internetzugang. Alle
        # drei sprechen ueber Wissen, das der Responder nicht mehr sieht — eine
        # Anweisung zu Quellen, die nicht im Prompt stehen, ist entweder
        # wirkungslos oder eine Aufforderung zum Erfinden
        # (novaberg-node-verfasser_k.md §2.2).
        #
        # Datum und Uhrzeit bleiben hier UND stehen beim Verfasser: Sie sind
        # kein Wissen aus einer Quelle, sondern die Lage, in der beide Stufen
        # stehen. Novas Art um 03:00 ist eine andere als um 14:00.
        f"Heute ist {jetzt.strftime('%A, %d.%m.%Y')}, es ist {jetzt.strftime('%H:%M')} Uhr.\n"
        "Sprich als du selbst, niemals als der Nutzer."
    )

    if nova_kern or nova_beziehung:
        logger.info(
            f"Responder: Nova-Identitaet in [IDENTITAET] "
            f"(kern={len(nova_kern)} Zeichen, beziehung={len(nova_beziehung)} Zeichen)"
        )

    parts.append("\n\n".join(identitaet_parts))

    # ── [EIGENE_EMOTION] ── Novas eigener Emotionszustand (Dual-Emotion Phase 2) ──
    nova_emotions_verlauf: list = state.get("nova_emotions_verlauf", [])
    # RESPONDER-VEKTOR-TOT (Chat 106): Der Vektor liegt seit dem
    # Personality-Umbau in internal.emotion.emotions_vector, NICHT in einem
    # flachen State-Key. Der alte Lesepfad `state.get("nova_emotions_vektor")`
    # fiel still auf "" — die Vektor-Zeile erschien nie im Prompt.
    # `internal` ist weiter oben in dieser Funktion bereits belegt.
    nova_emotions_vektor: str = ""
    if internal is not None and internal.emotion is not None:
        nova_emotions_vektor = internal.emotion.emotions_vector or ""
    else:
        logger.error(
            "Responder: internal/emotion fehlt — Novas Emotions-Vektor "
            "nicht verfuegbar, [EIGENE_EMOTION] bleibt ohne Vektor-Zeile"
        )
    nova_emotion_konflikt: bool = state.get("nova_emotion_konflikt", False)

    if not nova_emotions_vektor:
        logger.warning(
            "Responder: Novas Emotions-Vektor ist leer — [EIGENE_EMOTION] "
            "ohne Vektor-Zeile (Kaltstart oder ei_calc lief nicht)"
        )
    elif nova_emotions_vektor not in EMOTIONS_VEKTOREN_NOVA:
        logger.error(
            "Responder: Unbekannter Emotions-Vektor '%s' — nicht in "
            "EMOTIONS_VEKTOREN_NOVA, Zeile entfaellt",
            nova_emotions_vektor,
        )

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

    # ── [EIGENER GEDANKE] ── Reiz stammt von Nova selbst ──
    # Ein Pixie-Impuls geht als user_prompt in den Graphen, weil er derselbe
    # Reiz ist wie eine Nutzer-Eingabe. Ohne diesen Block liest der Responder
    # ihn als fremde Aeusserung und dankt dem Nutzer fuer Novas eigenen
    # Gedanken (gemessen 26.07.2026). Der Marker kommt ausdruecklich aus dem
    # Event-Payload — event_source allein wuerde den Thinker-Retry mitfangen,
    # der eine echte Nutzer-Aeusserung wiederholt.
    if _reiz_ist_eigener_gedanke(state):
        parts.append(PROMPTS["responder.eigener_gedanke"])
        logger.info("Responder: [EIGENER GEDANKE] gesetzt — Reiz stammt von Nova selbst")

    # ── [AUFGABE] ── Fertiger Block aus dem Planner ──
    task_block: str = state.get("task_block", "")

    if task_block:
        parts.append(task_block)

    # ── [KOMMUNIKATION] ── EI + Tonalitaet + Stil ──
    emotions_verlauf:   list = state.get("emotions_verlauf", [])
    user_intentionen:   list = state.get("user_intentionen", [])

    emotions_vektor:    str  = external.emotion.emotions_vector      if external else ""
    sprach_stil:        str  = external.emotion.language_style       if external else ""
    beziehungs_kontext: str  = external.character.relationship       if external else ""
    gespraechs_modus:   str  = external.emotion.mode                 if external else ""
    current_emotion:    str  = external.emotion.emotion              if external else "neutral"
    current_arousal:    float= external.emotion.arousal              if external else 0.5
    beziehungs_dynamik: str  = external.emotion.relationship_dynamic if external else "neutral"

    # Beim eigenen Impuls traegt `external` laut db_zugriff eine Kopie von
    # `internal` — die Werte unten sind dann Novas Zustand, nicht der des
    # Nutzers. Die Ueberschrift muss das sagen, sonst behauptet der Block eine
    # fremde Verfassung, die niemand gemessen hat.
    if _reiz_ist_eigener_gedanke(state):
        komm_kopf: str = "[KOMMUNIKATION]\nSo ist deine eigene Verfassung gerade:"
    else:
        komm_kopf = "[KOMMUNIKATION]\nSo nimmt der Nutzer gerade am Gespraech teil:"

    komm_parts: list[str] = [komm_kopf]

    # Emotionale Daten
    if emotions_verlauf:
        emotions_text: str = ", ".join(
            f"{e['emotion']} ({e['gewicht']:.0%}, a={e.get('arousal', 0.5):.0%})"
            for e in emotions_verlauf[:4]
        )
        komm_parts.append(f"Emotionaler Zustand: {emotions_text}")
    elif current_emotion and current_emotion != "neutral":
        komm_parts.append(f"Aktuelle Emotion: {current_emotion}")

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
    user_tone: str = external.emotion.tone if external else "sachlich"
    tone_text: str = TONE_INSTRUCTIONS.get(user_tone, TONE_INSTRUCTIONS["sachlich"])
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

    # ── [GESPRAECHSVEKTOR] ── entfaellt hier ──
    #
    # Landschaft, Strategie, Vehikel und Leitgedanke gehoeren zum Inhalt und
    # stehen beim Verfasser (novaberg-node-verfasser_k.md §2.1). Standen sie
    # zusaetzlich hier, sah der Responder denselben Leitgedanken ein zweites
    # Mal — und gab ihn woertlich weiter, statt ihm eine Form zu geben.

    # ── [INHALT] ── Was gesagt wird, kommt fertig vom Verfasser ──
    #
    # Gedaechtnis und Web-Recherche stehen hier NICHT mehr. Der Responder sieht
    # das Wissen nicht und kann daraus folglich nichts erfinden — die Lehre aus
    # den vier Fix-Iterationen ist damit eine Eigenschaft der Bauart statt
    # einer Fallunterscheidung (novaberg-node-verfasser_k.md §2.2).
    #
    # Bei aktivem Kontext-Schnitt laeuft der Verfasser nicht; dann ist das Feld
    # leer und der [AUFGABE]-Block traegt allein, genau wie bisher (§5.1).
    antwort_inhalt: str = state.get("antwort_inhalt", "")
    if antwort_inhalt:
        parts.append(
            f"[INHALT]\n"
            f"Das ist der fachliche Inhalt deiner Antwort. Sag ihn auf deine "
            f"Art.\n\n"
            f"{antwort_inhalt}"
        )

    # ── [REGELN] ── zur Probe ausgesetzt (31.07.2026) ──
    #
    # Die Regeln sind Narben: verbotene Floskeln, Antwortkuerze, Butler-Prinzip,
    # Tag-Unterdrueckung, das Verbot falscher Erfolgsmeldungen. Jede ist gegen
    # ein Verhalten gewachsen, das der ueberladene Prompt hervorgebracht hat —
    # ein Modell, das gleichzeitig Wissen sichten, Inhalt bestimmen und Form
    # finden sollte, greift zu Floskeln und Fuellseln.
    #
    # Seit der Trennung ist diese Ursache weg. Ob die Narben noch gebraucht
    # werden, ist damit eine offene Frage — und sie ist nur zu beantworten,
    # indem man sie einmal weglaesst. Nachjustiert wird, was sich als noetig
    # zeigt, statt alles vorsorglich stehen zu lassen.
    #
    # Der Prompt-Baustein `responder.rules` bleibt bestehen; nur der Aufruf
    # entfaellt. Zurueckholen ist damit eine Zeile.

    # ── [DIREKTIVEN] ── Absolute Verhaltensanweisungen vom Nutzer ──
    direktiven: list[dict] = list(internal.directives) if internal else []
    if direktiven:
        dir_zeilen: list[str] = [PROMPTS["responder.direktiven"]]
        for d in direktiven:
            dir_zeilen.append(f"- {d['anweisung']}")
            if d.get("kontext"):
                dir_zeilen.append(f"  (Kontext: {d['kontext']})")
        parts.append("\n".join(dir_zeilen))
        logger.info(f"Responder: {len(direktiven)} Direktiven in [DIREKTIVEN]")

    # ── [DEIN WESEN] ── zuletzt, damit es am staerksten wirkt ──
    #
    # Alles darueber ist Grundlage: gewachsene Persoenlichkeit, Stimmung,
    # Beziehung, Lage, Regeln. Das vom Nutzer gesetzte Wesen soll sich dort
    # nicht einreihen — es steht am Ende und damit an der Stelle, an der eine
    # Vorgabe am meisten ausrichtet.
    #
    # Nur wenn es eine gibt. Ein leerer Block waere eine Ueberschrift ohne
    # Aussage und naehme der Stelle genau die Wirkung, fuer die sie gewaehlt ist.
    charakter_anweisungen: list[str] = list(internal.identities) if internal else []
    if charakter_anweisungen:
        wesen_zeilen: list[str] = [
            "[DEIN WESEN]",
            "So bist du gemeint. Das hier ist keine Beschreibung neben anderen,",
            "sondern der Kern, aus dem heraus du sprichst:",
        ]
        wesen_zeilen.extend(f"- {anweisung}" for anweisung in charakter_anweisungen)
        parts.append("\n".join(wesen_zeilen))
        logger.info(
            f"Responder: {len(charakter_anweisungen)} Charakter-Anweisungen "
            f"als [DEIN WESEN] am Prompt-Ende"
        )

    return "\n\n".join(parts)


def _lage_zeilen(gv_detail: dict) -> list[str]:
    """Die Lage des Turns in drei Aufloesungen, von grob nach fein.

    Landschaft (eine von vierzehn), Sektor (einer von 64) und die sechs
    Achsen sind **nicht drei Angaben, sondern eine in drei Koernungen** — der
    Sektor ist aus den Achsen gebaut, die Landschaft fasst Sektoren zusammen.
    Sie stehen trotzdem alle drei da: Der grobe Rahmen zuerst, die genaue
    Situation zuletzt und damit am dichtesten am Generierungspunkt.

    Vorbedingung: keine. Ein leeres `gv_detail` ergibt eine leere Liste.
    Nachbedingung: Die Reihenfolge der Liste ist die Reihenfolge grob → fein.
    Fehlerfaelle: Keine eigenen; eine unbeschreibbare Achsenlage meldet
        `achsen_klartext` selbst.

    Args:
        gv_detail: das Detail-Dict des GV-Nodes.

    Returns:
        Null bis drei Zeilen.
    """
    from ei.dreischicht import CLUSTER_BESCHREIBUNGEN, achsen_klartext

    # ── Eingabe ─────────────────────────────────
    cluster:     str  = gv_detail.get("cluster", "")
    sektor_name: str  = gv_detail.get("sektor_name", "")
    achsen:      dict = gv_detail.get("achsen") or {}

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = []

    if cluster:
        beschreibung: str = CLUSTER_BESCHREIBUNGEN.get(cluster, "")
        zeilen.append(f"Landschaft: {cluster.capitalize()} — {beschreibung}")

    # Der Sektor entfaellt, wenn er wie die Landschaft heisst: In 10 der 64
    # Sektoren sind die Namen gleich ("Wartezimmer", "Foyer", "Regen"). Eine
    # Zeile, die die darueber wiederholt, kostet Kontext und traegt nichts —
    # und sie verwaessert die Staffelung, die dieser Block herstellen soll.
    if sektor_name and sektor_name.lower() != cluster.lower():
        zeilen.append(f"Genauer: {sektor_name}")

    lage: str = achsen_klartext(achsen)
    if lage:
        zeilen.append(f"Lage: {lage}")

    # ── Ausgabe ─────────────────────────────────
    return zeilen


def _sprachstil_block(state: ConversationState) -> str:
    """Baut den Sprachstil-Block, der hinter den Verlauf gehaengt wird.

    Alles, was Nova sagt WIE sie antworten soll, stand bis Chat 114 im
    System-Prompt — am weitesten weg vom Generierungspunkt. Unmittelbar vor
    der Generierung lag stattdessen der Gespraechsverlauf: gemessen rund drei
    Viertel der 11.254 Eingabe-Tokens eines Turns, gegenueber 1.376 Zeichen
    Gespraechsvektor. Das Ergebnis war im Log zu sehen — Cluster
    `kissenschlacht`, Strategie Impuls, Stil locker, und eine Antwort ueber
    thermische Entropie. Die Metadaten stimmten, die Sprache kam aus dem
    Verlauf.

    Der Block wiederholt deshalb die kurze Fassung des WIE dort, wo
    Anweisungen wirken. Er beschreibt und fuehrt hin, statt zu verbieten:
    Der Verlauf ist nicht falsch, er ist nur in einer anderen Lage entstanden.

    Quellen der Zeilen: Landschaft, Sektor, Achsen und Fragefrequenz aus der
    Lage des Turns (die ueber Novas Raum traegheitsbehaftet nachzieht), der
    Ton aus `external` — also aus dem Register DIESES Nutzer-Turns, nicht aus
    Novas alten Labels.

    **Die Zeilen stehen von grob nach fein, und das ist ihre Ordnung, nicht
    ihre Reihenfolge.** Dieselbe Lage erscheint dreimal in wachsender
    Aufloesung: die Landschaft ist eine von vierzehn, der Sektor einer von 64,
    die Achsen sind die sechs Groessen, aus denen beide gebaut sind. Wer nur
    den groben Rahmen braucht, findet ihn oben; wer die genaue Situation
    braucht, liest weiter nach unten, wo sie am dichtesten am
    Generierungspunkt steht.

    Seit dem 08.08.2026 traegt **jeder** Turn eine Landschaft — auch der ohne
    Vorausdenken (`novaberg-erreichbarkeit_k.md` B1). Die Werkzeug-Zeile fehlt
    in diesen Turns weiterhin, weil es kein Werkzeug gibt: Sie stammt aus dem
    LLM-Lauf, der nicht stattgefunden hat. Der Rahmen steht trotzdem.

    Vorbedingung: Keine — fehlende Teile werden weggelassen.
    Nachbedingung: Rueckgabe ist der fertige Block oder "", wenn keine
    einzige Angabe vorliegt.
    Fehlerfaelle: Keine; ein unbekannter Cluster liefert nur keine Landschaft.
    """
    # ── Eingabe ─────────────────────────────────
    from ei.dreischicht import CLUSTER_FRAGEN, STRATEGIE_NAMEN

    gv_detail: dict = state.get("gv_detail", {}) or {}
    cluster:   str  = gv_detail.get("cluster", "")
    strategie: str  = gv_detail.get("strategie", "")
    vehikel:   str  = gv_detail.get("vehikel", "")

    external = state.get("external")
    stil: str = external.emotion.language_style if external else ""

    # ── Verarbeitung ────────────────────────────
    # Grob bis genau: Landschaft, Sektor, Achsen.
    zeilen: list[str] = _lage_zeilen(gv_detail)

    # Am genauesten — wie in dieser Lage zu sprechen ist.
    ton_teile: list[str] = []
    if stil and stil != "neutral":
        ton_teile.append(f"Ton: {stil}")
    if cluster:
        fragen: str = CLUSTER_FRAGEN.get(cluster, "")
        if fragen:
            ton_teile.append(f"Fragen: {fragen}")
    if strategie:
        werkzeug: str = STRATEGIE_NAMEN.get(strategie, strategie)
        if vehikel:
            werkzeug += f", als {vehikel.capitalize()}"
        ton_teile.append(f"Werkzeug: {werkzeug}")
    if ton_teile:
        zeilen.append(" · ".join(ton_teile))

    # Der Leitgedanke steht hier NICHT mehr. Er ist Inhalt und gehoert zum
    # Verfasser — hier war er die zweite Tuer: Der GV-Block war schon aus dem
    # System-Prompt entfernt, und derselbe Text kam ueber den Sprachstil am
    # Ende der Nutzer-Nachricht zurueck. Live beobachtet am 31.07.2026
    # (novaberg-node-verfasser_k.md §2.1).
    #
    # Was bleibt, ist Stil: Landschaft, Ton, Fragenfrequenz, Werkzeug.

    # ── Ausgabe-Verifikation ────────────────────
    if not zeilen:
        logger.info("Responder: Sprachstil-Block leer — weder Cluster noch Stil")
        return ""

    block: str = PROMPTS["responder.sprachstil"].format(
        stil_zeilen="\n".join(zeilen),
    )
    logger.info(
        "Responder: Sprachstil-Block hinter dem Verlauf (%d Zeichen, "
        "Cluster=%s, Stil=%s)", len(block), cluster or "—", stil or "—",
    )
    return block


def respond(
    state: ConversationState,
) -> ConversationState:
    """Generiert die LLM-Antwort basierend auf angereichertem State."""
    system_prompt: str = _build_system_prompt(state)

    external = state.get("external")
    log_intent: str = external.emotion.intent if external else ""
    log_tone:   str = external.emotion.tone   if external else ""
    logger.info(f"Responder: Generiere Antwort (intent={log_intent}, tone={log_tone})")

    # Messages aus Session-History aufbauen
    messages: list[dict] = []

    # Der Sprachstil steht am ENDE der Nutzer-Nachricht, hinter dem Verlauf und
    # hinter dem aktuellen Prompt — dort, wo eine Anweisung gegen 8.400 Tokens
    # fremder Prosa noch etwas ausrichtet. Fuehrende Leerzeile, damit er sich
    # vom Prompt absetzt.
    sprachstil_block: str = _sprachstil_block(state)
    sprachstil: str = f"\n\n{sprachstil_block}" if sprachstil_block else ""

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
            f"{sprachstil}"
        )})
    else:
        messages.append({"role": "user", "content": user_prompt + sprachstil})

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

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # respond() laeuft im CharacterGraph (services/event_consumer.py ruft
    # den Graphen via asyncio.to_thread(_graph_streamen, ...) im Worker-
    # Thread). Kein Event-Loop im aufrufenden Thread → submit_sync bruckt
    # in den Worker-Loop (Loop-Binding-Lesson). Alle fuenf Sampling-
    # Parameter aus node_cfg werden 1:1 durchgereicht; None-Werte filtert
    # der ChatWorker beim Backend-Call, sodass Provider-Defaults greifen.
    chat_request = ChatRequest(
        messages          = messages,
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.7),
        top_p             = node_cfg.get("top_p"),
        repeat_penalty    = node_cfg.get("repeat_penalty"),
        presence_penalty  = node_cfg.get("presence_penalty"),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "responder",
    )
    response = model_service.chat.submit_sync(chat_request)

    state["response"]    = response.text
    state["model"]       = "chat_worker"
    state["token_total"] = response.token_total

    # ── Ausgabe-Verifikation ────────────────────
    # **Gezaehlt werden Zeichen, nicht Token.** Die fruehere Erfolgsmeldung
    # nannte die Tokenzahl — und die war bei beiden verlorenen Turns vierstellig,
    # waehrend der Text null Zeichen hatte. Eine Meldung, die Erfolg behauptet,
    # wo nichts steht, macht den Ausfall an genau der Stelle unsichtbar, an der
    # er entsteht (novaberg-bugs.md -> RESPONDER-LEERE-ANTWORT-STILL).
    #
    # Der Turn laeuft weiter: Abzubrechen hiesse, die Nutzeraeusserung zu
    # verlieren, und die ist der teurere Verlust (PFAD1-TIMEOUT-TURNVERLUST).
    # Die Stufen dahinter sehen die leere Antwort und koennen sie behandeln.
    if not state["response"].strip():
        logger.error(
            f"Responder: LEERE Antwort trotz {state['token_total']} Token — "
            f"der Verfasser hatte {len(state.get('antwort_inhalt', ''))} Zeichen "
            "Inhalt bereitgestellt. Der Turn erreicht den Nutzer nicht; die "
            "Ursache steht in der Zeile des ChatWorkers darueber."
        )
        return state

    logger.info(
        f"Responder: Antwort generiert ({len(state['response'])} Zeichen, "
        f"{state['token_total']} Tokens)"
    )

    return state
