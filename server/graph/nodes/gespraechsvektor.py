"""
Gespraechsvektor Node — Antizipiert die Richtung des Gespraechs.

Bestimmt WOHIN das Gespraech fuehrt, basierend auf:
- WOHER + WO (Session-Turns + Perzeption)
- 8 EI-Dimensionen → Richtung im mehrdimensionalen Raum
- EI-Modell → Vektorlaenge (0-3 Gedankenschritte)
- Entity-Hop → verwandte Fakten fuer Assoziationen
- Novas Charakter → Linse fuer die Selektion

Konzept: nova-09-k.md
"""

import logging

import psycopg2

from config import (
    POSTGRES_URL,
    EMOTION_SEKTOR_MAP,
    SEKTOR_GRUPPE,
    PROMPTS,
    get_node_config,
)
from graph.state import ConversationState
from memory.session import format_session_turns_numbered
from services.llm_provider import get_chat_provider

logger = logging.getLogger("ki_server.gespraechsvektor")


# ─────────────────────────────────────────────
# Emotions-Gruppen aus dem Plutchik-Modell
# ─────────────────────────────────────────────
_POSITIVE_EMOTIONEN: set[str] = {
    emotion for emotion, sektor in EMOTION_SEKTOR_MAP.items()
    if SEKTOR_GRUPPE.get(sektor) == "positiv"
}
_NEGATIVE_EMOTIONEN: set[str] = {
    emotion for emotion, sektor in EMOTION_SEKTOR_MAP.items()
    if SEKTOR_GRUPPE.get(sektor) == "negativ"
}


# ─────────────────────────────────────────────
# Skip-Check
# ─────────────────────────────────────────────

def _ist_skip(state: ConversationState) -> bool:
    """Prueft ob der GV-Node uebersprungen werden soll.

    Nur bei reiner Begruessung oder Meta-Operationen.
    Management-Intents werden NICHT uebersprungen —
    auch bei Tasks kann Nova vorausdenken (Zahnarzt → Metzgerei).
    """
    intent: str = state.get("intent", "")
    if intent in ("begruessung", "meta", "system"):
        return True
    return False


# ─────────────────────────────────────────────
# Laengenberechnung aus EI-Dimensionen
# ─────────────────────────────────────────────

def _vektor_laenge_berechnen(state: ConversationState) -> int:
    """Berechnet die maximale Vektorlaenge aus den 8 EI-Dimensionen.

    Deterministisch (Python). Das LLM darf kuerzer, aber nicht laenger.
    Hartes Limit: 3 Schritte (Cognitive Load Theory).

    Faktoren:
      - Emotion (positiv/negativ) + Arousal → Grundlaenge
      - Beziehungsdynamik (Vertrautheit) → Erhoehung
      - Modus (fachlich/emotional) → Reduktion
      - Sprachstil (locker/formell) → Feintuning
      - Emotions-Vektor (Krise) → Notbremse auf 0
    """
    arousal:  float = state.get("current_arousal", 0.5)
    emotion:  str   = state.get("current_emotion", "neutral")
    modus:    str   = state.get("gespraechs_modus", "alltag")
    dynamik:  str   = state.get("beziehungs_dynamik", "neutral")
    stil:     str   = state.get("sprach_stil", "neutral")
    vektor:   str   = state.get("emotions_vektor", "")

    # Krise → sofort 0 (nur Empathie, keine Antizipation)
    if vektor in ("spirale", "absturz") and arousal >= 0.7:
        logger.info("GV-Laenge: 0 (Krise — spirale/absturz bei hohem Arousal)")
        return 0

    laenge: float = 1.0

    # Positive Emotion + Arousal → mehr Spruenge
    if emotion in _POSITIVE_EMOTIONEN:
        laenge += 0.5 + (arousal * 0.5)
    elif emotion in _NEGATIVE_EMOTIONEN:
        laenge -= arousal * 0.5

    # Vertrautheit erhoeht die erlaubte Laenge
    if dynamik == "vertrauen":
        laenge += 0.5
    elif dynamik == "distanz":
        laenge -= 0.5

    # Fachliche Komplexitaet bremst
    if modus == "fachgespraech":
        laenge -= 0.3
    elif modus == "emotional":
        laenge -= 0.2

    # Lockerer Stil erlaubt groessere Spruenge
    if stil == "locker":
        laenge += 0.3
    elif stil == "formell":
        laenge -= 0.2

    ergebnis: int = max(0, min(3, round(laenge)))
    logger.info(
        f"GV-Laenge: {ergebnis} "
        f"(emotion={emotion}, a={arousal:.2f}, modus={modus}, "
        f"dynamik={dynamik}, stil={stil}, vektor={vektor})"
    )
    return ergebnis


# ─────────────────────────────────────────────
# Entity-Hop ueber Fakten-Tabelle
# ─────────────────────────────────────────────

def _entity_kontext_laden(state: ConversationState) -> str:
    """Laedt verwandte Entitaeten ueber die Fakten-Kanten.

    Hop 1: Schluesselentitaet → deren Fakten
    Hop 2: Verknuepfte Entitaeten → deren Fakten (Orts-/Themen-Verknuepfung)

    Gibt formatierten Text zurueck fuer den LLM-Prompt.
    """
    user_id: str = state.get("user_id", "")
    # Schluessel: management_target (bei Tasks) oder prompt_thema (bei Chat)
    management_target: str = state.get("management_target", "")
    prompt_thema:      str = state.get("prompt_thema", "")
    schluessel:        str = management_target or prompt_thema

    if not schluessel or not schluessel.strip():
        return ""

    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        # --- Hop 1: Entitaeten zum Schluessel finden ---
        cursor.execute(
            """
            SELECT id, name, typ, zusammenfassung
            FROM entitaeten
            WHERE user_id = %s AND aktiv = TRUE
              AND (name ILIKE %s OR zusammenfassung ILIKE %s)
            LIMIT 5
            """,
            (user_id, f"%{schluessel}%", f"%{schluessel}%"),
        )
        hop1_entitaeten: list[tuple] = cursor.fetchall()

        if not hop1_entitaeten:
            conn.close()
            return ""

        hop1_ids: list[int] = [e[0] for e in hop1_entitaeten]

        # --- Fakten zu Hop-1-Entitaeten laden ---
        cursor.execute(
            """
            SELECT e1.name, f.beziehung, e2.name, e2.id, e2.zusammenfassung
            FROM fakten f
            JOIN entitaeten e1 ON f.subjekt_id = e1.id
            JOIN entitaeten e2 ON f.objekt_id = e2.id
            WHERE f.user_id = %s AND f.aktiv = TRUE
              AND (f.subjekt_id = ANY(%s) OR f.objekt_id = ANY(%s))
            LIMIT 20
            """,
            (user_id, hop1_ids, hop1_ids),
        )
        hop1_fakten: list[tuple] = cursor.fetchall()

        # --- Hop 2: Verknuepfte Entitaeten → deren Fakten ---
        hop2_ids: list[int] = list({f[3] for f in hop1_fakten} - set(hop1_ids))
        hop2_fakten: list[tuple] = []

        if hop2_ids:
            cursor.execute(
                """
                SELECT e1.name, f.beziehung, e2.name, e2.id, e2.zusammenfassung
                FROM fakten f
                JOIN entitaeten e1 ON f.subjekt_id = e1.id
                JOIN entitaeten e2 ON f.objekt_id = e2.id
                WHERE f.user_id = %s AND f.aktiv = TRUE
                  AND (f.subjekt_id = ANY(%s) OR f.objekt_id = ANY(%s))
                LIMIT 20
                """,
                (user_id, hop2_ids, hop2_ids),
            )
            hop2_fakten = cursor.fetchall()

        conn.close()

        # --- Formatieren ---
        alle_fakten: list[tuple] = hop1_fakten + hop2_fakten
        if not alle_fakten:
            return ""

        # Deduplizieren (gleiche Kante nicht doppelt)
        gesehen: set[str] = set()
        zeilen: list[str] = []
        for subjekt, beziehung, objekt, _, zusammenfassung in alle_fakten:
            kante: str = f"{subjekt}|{beziehung}|{objekt}"
            if kante in gesehen:
                continue
            gesehen.add(kante)
            zeile: str = f"  {subjekt} → {beziehung} → {objekt}"
            if zusammenfassung:
                zeile += f" ({zusammenfassung})"
            zeilen.append(zeile)

        entity_text: str = "\n".join(zeilen)
        logger.info(f"GV-Entity-Hop: {len(zeilen)} Fakten geladen (Schluessel: '{schluessel}')")
        return entity_text

    except Exception as fehler:
        logger.warning(f"GV-Entity-Hop fehlgeschlagen: {fehler}")
        return ""


# ─────────────────────────────────────────────
# Farbmisch-System: 8 unabhaengige Dimensionen
# ─────────────────────────────────────────────
# Jede Dimension traegt einen kurzen Satz zur Landschaftsbeschreibung bei,
# aber NUR wenn sie etwas Auffaelliges zu sagen hat.
# Neutrale Werte schweigen. Keine Imperative — nur Beschreibungen.
# Analog zu EI-MIKRO: Python waehlt, LLM interpretiert.


def _farbe_intent(intent: str) -> str:
    """Was fuer ein Gespraech ist das?"""
    farben: dict[str, str] = {
        "personal":    "Der Nutzer teilt etwas Persoenliches.",
        "knowledge":   "Der Nutzer verfolgt einen Wissenspfad.",
        "task":        "Eine Aufgabe steht an.",
        "creative":    "Der Nutzer ist im kreativen Modus.",
        "smalltalk":   "",  # schweigt — zu unspezifisch
        "begruessung": "",
        "meta":        "",
    }
    return farben.get(intent, "")


def _farbe_emotion(emotion: str, arousal: float) -> str:
    """Wie warm oder kalt ist die Stimmung?"""
    if emotion == "neutral":
        return ""
    if emotion in _POSITIVE_EMOTIONEN:
        if arousal >= 0.7:
            return "Die Stimmung ist lebhaft und positiv."
        elif arousal >= 0.4:
            return "Eine warme Grundstimmung liegt im Raum."
        else:
            return ""  # leise positive Stimmung — schweigt
    if emotion in _NEGATIVE_EMOTIONEN:
        if arousal >= 0.7:
            return "Schwere liegt ueber dem Gespraech."
        elif arousal >= 0.4:
            return "Eine Anspannung ist spuerbar."
        else:
            return "Eine leise Schwere ist da."
    return ""


def _farbe_vektor(vektor: str) -> str:
    """Wohin bewegt sich die Energie? Die wichtigste Farbe — beschreibt den Uebergang."""
    farben: dict[str, str] = {
        "absturz":         "Die Stimmung ist eingebrochen.",
        "spirale":         "Die Belastung nimmt zu. Neue negative Gefuehle kommen hinzu.",
        "einbruch":        "Die Stimmung kippt gerade ins Negative.",
        "abkuehlung":      "Die Stimmung wechselt von Begeisterung zu Sachlichkeit.",
        "stabilisierung":  "Die Stimmung beruhigt sich.",
        "plateau":         "",  # schweigt — keine Veraenderung
        "erholung":        "Die Stimmung hellt sich auf nach einem Tief.",
        "aufbluehen":      "Die Stimmung hebt sich. Positive Energie baut sich auf.",
        "eskalation":      "Die Begeisterung steigt weiter.",
    }
    return farben.get(vektor, "")


def _farbe_dynamik(dynamik: str) -> str:
    """Wie nah sind wir uns?"""
    farben: dict[str, str] = {
        "vertrauen":    "Der Nutzer ist offen und vertraut.",
        "distanz":      "Der Nutzer haelt Abstand.",
        "hilfesuchend": "Der Nutzer sucht Halt.",
        "dankbar":      "Dankbarkeit schwingt mit.",
        "angriff":      "Der Nutzer ist konfrontativ.",
        "neutral":      "",  # schweigt
    }
    return farben.get(dynamik, "")


def _farbe_modus(modus: str) -> str:
    """Wie tief gehen wir?"""
    farben: dict[str, str] = {
        "fachgespraech":  "Das Gespraech ist fachlich und konzentriert.",
        "emotional":      "Gefuehle stehen im Vordergrund.",
        "spielerisch":    "Die Stimmung ist verspielt und leicht.",
        "arbeitsmodus":   "Der Fokus liegt auf der Aufgabe.",
        "alltag":         "",  # schweigt — Normalzustand
    }
    return farben.get(modus, "")


def _farbe_stil(stil: str) -> str:
    """Wie foermlich ist der Raum?"""
    farben: dict[str, str] = {
        "formell":     "Der Ton ist nuechtern geworden.",
        "fachlich":    "Der Ton ist sachlich und praezise.",
        "emotional":   "Der Ton ist emotional gefaerbt.",
        "jugendlich":  "Der Ton ist jung und direkt.",
        "locker":      "",  # schweigt — Normalzustand fuer diesen User
        "neutral":     "",
    }
    return farben.get(stil, "")


def _farbe_arousal(arousal: float) -> str:
    """Wie viel Energie ist im Raum?"""
    if arousal >= 0.7:
        return "Die Energie ist hoch."
    elif arousal <= 0.25:
        return "Die Energie ist ruhig."
    return ""  # Mittelbereich schweigt


def _farbe_tone(tone: str, stil: str) -> str:
    """Welches Licht faellt drauf? Schweigt wenn redundant zum Stil."""
    # Vermeidet Dopplung: sachlich + formell sagen dasselbe
    if tone == "sachlich" and stil in ("formell", "fachlich"):
        return ""
    if tone == "empathisch" and stil == "emotional":
        return ""
    farben: dict[str, str] = {
        "kreativ":    "Es darf unkonventionell gedacht werden.",
        "empathisch": "Waerme ist gefragt.",
        "direkt":     "Klarheit steht im Vordergrund.",
        "sachlich":   "",  # oft redundant, schweigt im Zweifel
    }
    return farben.get(tone, "")


def _gv_strategie(state: ConversationState) -> str:
    """Mischt die 8 Dimensionen zu einer Landschaftsbeschreibung.

    Jede Dimension traegt einen kurzen Satz bei — aber nur wenn sie
    etwas Auffaelliges zu sagen hat. Neutrale Werte schweigen.
    Das Ergebnis sind 2-5 Saetze die dem LLM die emotionale und
    kognitive Landschaft beschreiben, ohne Handlungsanweisungen.
    """
    emotion: str   = state.get("current_emotion", "neutral")
    arousal: float = state.get("current_arousal", 0.5)
    vektor:  str   = state.get("emotions_vektor", "")
    modus:   str   = state.get("gespraechs_modus", "alltag")
    intent:  str   = state.get("intent", "")
    dynamik: str   = state.get("beziehungs_dynamik", "neutral")
    stil:    str   = state.get("sprach_stil", "neutral")
    tone:    str   = state.get("tone", "sachlich")

    farben: list[str] = [
        _farbe_intent(intent),
        _farbe_emotion(emotion, arousal),
        _farbe_vektor(vektor),
        _farbe_dynamik(dynamik),
        _farbe_modus(modus),
        _farbe_stil(stil),
        _farbe_arousal(arousal),
        _farbe_tone(tone, stil),
    ]

    landschaft: str = " ".join(f for f in farben if f)

    if not landschaft:
        landschaft = "Das Gespraech ist ruhig und ausgeglichen."

    return landschaft


# ─────────────────────────────────────────────
# LLM-Call: Hypothese destillieren
# ─────────────────────────────────────────────

def _hypothese_destillieren(
    state:          ConversationState,
    max_laenge:     int,
    entity_kontext: str,
) -> str:
    """Destilliert die Gespraechsvektor-Hypothese via LLM.

    Input: Session-Turns, Emotion, Charakter, Entity-Kontext
    Output: Natuerlichsprachliche Hypothese (2-4 Saetze)
    """
    # Session-Turns aufbereiten (letzte 8)
    session_turns: list[dict] = state.get("session_turns", [])
    if session_turns:
        # Nur die letzten 8 Turns fuer den Vektor
        relevante_turns: list[dict] = session_turns[-8:]
        verlauf_text: str = format_session_turns_numbered(relevante_turns)
    else:
        verlauf_text = "(Erster Turn — kein Verlauf)"

    # Emotions-Kontext
    emotion:     str   = state.get("current_emotion", "neutral")
    arousal:     float = state.get("current_arousal", 0.5)
    vektor:      str   = state.get("emotions_vektor", "")
    modus:       str   = state.get("gespraechs_modus", "alltag")
    dynamik:     str   = state.get("beziehungs_dynamik", "neutral")
    intentionen: list  = state.get("user_intentionen", [])
    user_prompt: str   = state.get("user_prompt", "")

    # Charakter
    nova_kern:      str = state.get("nova_kern", "")
    nova_beziehung: str = state.get("nova_beziehung", "")

    # --- System-Prompt ---
    system_parts: list[str] = [PROMPTS["gv.identity"]]

    # Novas Charakter als Linse
    if nova_kern:
        system_parts.append(
            PROMPTS["gv.charakter"].format(nova_kern=nova_kern)
        )
        if nova_beziehung:
            system_parts.append(
                f"Beziehung zum Nutzer:\n{nova_beziehung}"
            )

    # Aktivierte Ziele als innere Gedanken (Drive)
    aktivierte_ziele: list[dict] = state.get("aktivierte_ziele", [])

    if aktivierte_ziele:
        gedanken_zeilen: list[str] = [
            f"- {z['zielsatz']}" for z in aktivierte_ziele[:3]  # Max 3 Ziele
        ]
        gedanken_block: str = (
            "\n\n[GEDANKEN]\n"
            "Gedanken, die dir gerade durch den Kopf gehen:\n"
            + "\n".join(gedanken_zeilen)
        )
        system_parts.append(gedanken_block)

        logger.info(
            f"GV: {len(aktivierte_ziele)} aktivierte Ziele als [GEDANKEN]-Block eingefügt"
        )

    # Situativer Farbton
    farbton: str = _gv_strategie(state)
    farbton_block: str = f"\n\n[SITUATION]\n{farbton}" if farbton else ""

    system_parts.append(
        PROMPTS["gv.task"].format(max_laenge=max_laenge) + farbton_block
    )

    system_prompt: str = "\n\n".join(system_parts)

    # --- User-Message ---
    user_parts: list[str] = []

    user_parts.append(
        f"[GESPRAECHSVERLAUF]\n{verlauf_text}"
    )

    user_parts.append(
        f"[AKTUELLER PROMPT]\n{user_prompt}"
    )

    user_parts.append(
        f"[EMOTIONALER ZUSTAND]\n"
        f"Emotion: {emotion} (Arousal: {arousal:.0%})\n"
        f"Vektor: {vektor or 'keiner'}\n"
        f"Modus: {modus}\n"
        f"Beziehung: {dynamik}\n"
        f"Intentionen: {', '.join(intentionen) if intentionen else 'keine'}"
    )

    if entity_kontext:
        user_parts.append(
            f"[VERWANDTE FAKTEN]\n"
            f"Bekanntes Wissen ueber Personen, Orte und Vorlieben des Nutzers:\n"
            f"{entity_kontext}"
        )

    # Gedaechtnis-Kontext (KZG + LZG + Notizen, vom Enricher geladen)
    memory_context: str = state.get("memory_context", "")
    if memory_context:
        user_parts.append(
            f"[GEDAECHTNIS]\n"
            f"{memory_context}"
        )

    user_message: str = "\n\n".join(user_parts)

    # --- LLM-Call ---
    node_cfg: dict = get_node_config("gespraechsvektor")
    provider = get_chat_provider()

    antwort = provider.chat(
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
        temperature=node_cfg.get("temperature", 0.6),
        max_output_tokens=node_cfg.get("max_output_tokens", 512),
        caller="gespraechsvektor",
    )

    hypothese: str = antwort.content.strip()
    logger.info(f"GV-Hypothese ({antwort.token_total} Tokens): {hypothese[:120]}...")
    return hypothese


# ─────────────────────────────────────────────
# Node-Funktion (Einsprungpunkt fuer den Graph)
# ─────────────────────────────────────────────

def gespraechsvektor(state: ConversationState) -> ConversationState:
    """Gespraechsvektor-Node: Antizipiert die Richtung des Gespraechs.

    Sequentieller Ablauf:
      1. Skip-Check (Begruessung/Meta → durchreichen)
      2. Laenge aus EI-Dimensionen berechnen (Python, deterministisch)
      3. Entity-Hop ueber Fakten-Tabelle (Python, DB-Queries)
      4. LLM-Call → Hypothese destillieren (mit Charakter + Entity-Kontext)
      5. Ergebnis in State schreiben
    """
    logger.info("Gespraechsvektor: Analyse gestartet")

    # 1. Skip?
    if _ist_skip(state):
        logger.info("Gespraechsvektor: Skip (Begruessung/Meta)")
        state["gespraechsvektor"] = ""
        return state

    # 2. Laenge berechnen
    max_laenge: int = _vektor_laenge_berechnen(state)

    if max_laenge == 0:
        logger.info("Gespraechsvektor: Laenge 0 — kein Vorausdenken")
        state["gespraechsvektor"] = ""
        return state

    # 3. Entity-Hop
    entity_kontext: str = _entity_kontext_laden(state)

    # 3b. Farbton loggen
    farbton: str = _gv_strategie(state)
    if farbton:
        logger.info(f"GV-Farbton: {farbton}")

    # 4. Hypothese destillieren
    hypothese: str = _hypothese_destillieren(state, max_laenge, entity_kontext)

    # 5. State schreiben
    state["gespraechsvektor"] = hypothese

    return state
