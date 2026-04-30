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
import math

import numpy as np
import psycopg2

from config import (
    POSTGRES_URL,
    EMOTION_SEKTOR_MAP,
    SEKTOR_GRUPPE,
    PROMPTS,
    get_node_config,
    # GV4 — Wissenslücken
    GV_NEUGIER_CAP,
    GV_SESSION_AKT_CAP,
    GV_NEUGIER_EMOTION,
    GV_NEUGIER_VEKTOR,
    GV_NEUGIER_MODUS,
    GV_NEUGIER_DYNAMIK,
    GV_NEUGIER_STIL,
    GV_REGISTER_SACHLICH_EMOTIONAL,
    GV_REGISTER_SACHLICH_MILD,
    GV_REGISTER_SACHLICH_NEUTRAL,
    GV_REGISTER_OFFEN_EMOTIONAL,
    # GV4 — Wissensluecken-Suche
    GV_LUECKEN_MAX,
    GV_LUECKEN_MIN_RELEVANZ,
    GV_NEUGIER_BOOST_SCHWELLE,
    GV_CHARAKTER_RESONANZ_SCHWELLE,
    GV_QUELLEN_FAKTOR,
    GV_LUECKEN_SIM_OBERGRENZE,
    GV_STRATEGIE_MIN_LAENGE,
    EMBED_MODEL,
    ollama_gpu_client,
    redis_client,
)
from graph.state import ConversationState
from memory.embedding import embedding_create
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
# GV4: Effektive Neugier (6 Saeulen)
# ─────────────────────────────────────────────
# Berechnet Novas aktuelle Neugier aus ihrem emotionalen Zustand,
# dem Gespraechsregister und ihrer Grundpersoenlichkeit.
# Rein deterministisch (Python). Ergebnis: [0, 1] via sin^0.5.
# Konzept: Chat 71 — 6 Saeulen × NOVA_NEUGIER, gedeckelt.


def _sektor_distanz(sektor_a: int, sektor_b: int) -> int:
    """Kuerzeste Distanz auf dem Plutchik-Oktagon (0-4)."""
    d: int = abs(sektor_a - sektor_b)
    return min(d, 8 - d)


def _sin_sqrt_norm(wert: float, cap: float) -> float:
    """sin^0.5 Normalisierung: Wert/Cap -> [0, 1].

    Steil am Anfang, flach am Ende. Cap = Obergrenze
    ab der der Wert 1.0 erreicht.
    Gleiches Pattern wie EI-Arousal-Glaettung (Chat 61).
    """
    if wert <= 0:
        return 0.0
    anteil: float = min(wert / cap, 1.0)
    return math.sin(anteil * math.pi / 2) ** 0.5


def _effektive_neugier_berechnen(state: ConversationState) -> float:
    """Berechnet Novas aktuelle Neugier aus 6 EI-Dimensionen.

    Basis: NOVA_NEUGIER (0.5, Persoenlichkeitsparameter)
    Moduliert durch:
      E — Emotion (Sektor-Distanz zu Neugier/Sektor 8)
      A — Arousal (Energielevel, Krise = Kill)
      V — Vektor (Richtung der Stimmung)
      M — Modus (Fach/Spielerisch/Emotional)
      D — Dynamik (Vertrauen/Distanz)
      S — Stil (Locker/Formell)

    Ergebnis: sin^0.5 normiert auf [0, 1].
    Hohe Neugier (P1/P2) → ~0.96-0.99
    Neutral (P3) → ~0.56
    Traurig (P4) → ~0.32
    Krise (P5) → 0.00
    """
    # Novas Emotion (aus Dual-Emotion, falls vorhanden)
    nova_verlauf: list = state.get("nova_emotions_verlauf", [])
    if nova_verlauf:
        nova_emotion: str = nova_verlauf[0].get("emotion", "neutral")
        nova_arousal: float = nova_verlauf[0].get("arousal", 0.5)
    else:
        # Fallback: User-Emotion als Proxy (vor Dual-Emotion)
        nova_emotion = state.get("current_emotion", "neutral")
        nova_arousal = state.get("current_arousal", 0.5)

    vektor: str = state.get("nova_emotions_vektor",
                            state.get("emotions_vektor", ""))
    modus:   str = state.get("gespraechs_modus", "alltag")
    dynamik: str = state.get("beziehungs_dynamik", "neutral")
    stil:    str = state.get("sprach_stil", "neutral")

    # ── Krise: sofortiger Kill ──
    if vektor in ("spirale", "absturz") and nova_arousal >= 0.7:
        logger.info("GV4-Neugier: 0.00 (Krise)")
        return 0.0

    # ── E: Emotion → Sektor-Distanz zu Neugier (Sektor 8) ──
    sektor: int | None = EMOTION_SEKTOR_MAP.get(nova_emotion)
    if sektor is not None:
        distanz: int = _sektor_distanz(sektor, 8)
        logger.debug(
            f"GV4-Neugier Detail: emotion='{nova_emotion}' → sektor={sektor}, "
            f"distanz_zu_8={distanz if sektor is not None else 'n/a'}"
        )
        faktor_e: float = GV_NEUGIER_EMOTION.get(distanz, 1.0)
    else:
        faktor_e = 1.0  # neutral — keine Modulation

    # ── A: Arousal ──
    if nova_arousal >= 0.7:
        faktor_a: float = 1.25
    elif nova_arousal >= 0.5:
        faktor_a = 1.15
    elif nova_arousal >= 0.3:
        faktor_a = 1.00
    else:
        faktor_a = 0.85

    # ── V, M, D, S: Lookup ──
    faktor_v: float = GV_NEUGIER_VEKTOR.get(vektor, 1.0)
    faktor_m: float = GV_NEUGIER_MODUS.get(modus, 1.0)
    faktor_d: float = GV_NEUGIER_DYNAMIK.get(dynamik, 1.0)
    faktor_s: float = GV_NEUGIER_STIL.get(stil, 1.0)

    # ── Rohwert → sin^0.5 → [0, 1] ──
    from config import NOVA_NEUGIER  # Persoenlichkeitsparameter (0.5)
    produkt: float = faktor_e * faktor_a * faktor_v * faktor_m * faktor_d * faktor_s
    rohwert: float = NOVA_NEUGIER * produkt
    effektiv: float = _sin_sqrt_norm(rohwert, GV_NEUGIER_CAP)

    logger.info(
        f"GV4-Neugier: {effektiv:.3f} "
        f"(roh={rohwert:.2f}, produkt={produkt:.2f}, "
        f"emotion='{nova_emotion}' sektor={sektor} dist={distanz if sektor is not None else 'n/a'}, "
        f"E={faktor_e:.2f}, A={faktor_a:.2f}, V={faktor_v:.2f}, "
        f"M={faktor_m:.2f}, D={faktor_d:.2f}, S={faktor_s:.2f})"
    )

    return effektiv


def _register_kompatibilitaet(
    gap_arousal: float,
    modus:       str,
    dynamik:     str,
) -> float:
    """Passt die emotionale Ladung der Luecke zum Gespraechsregister?

    Sachlich (Fachgespraech/Arbeit/Distanz):
      → Emotionale Luecken gedaempft, sachliche bevorzugt.
    Offen (Spielerisch/Vertrauen):
      → Emotionale Luecken willkommen.
    Neutral: Keine Modulation.
    """
    ist_sachlich: bool = (
        modus in ("fachgespraech", "arbeitsmodus")
        or dynamik == "distanz"
    )
    ist_offen: bool = (
        modus == "spielerisch"
        or dynamik == "vertrauen"
    )

    if ist_sachlich:
        if gap_arousal >= 0.6:
            return GV_REGISTER_SACHLICH_EMOTIONAL   # 0.60
        elif gap_arousal >= 0.3:
            return GV_REGISTER_SACHLICH_MILD         # 0.90
        else:
            return GV_REGISTER_SACHLICH_NEUTRAL      # 1.15

    if ist_offen:
        if gap_arousal >= 0.4:
            return GV_REGISTER_OFFEN_EMOTIONAL       # 1.20
        else:
            return 1.0

    return 1.0


def _session_aktualitaet(turn_abstand: int) -> float:
    """Berechnet die Frische eines Session-Turns.

    Invertierte sin^0.5: Steil am Anfang (schnelles Vergessen),
    lang nachhallend (noch praesent nach vielen Turns).
    Nach GV_SESSION_AKT_CAP Turns = 0.

    Turn 0: 1.00, Turn 1: 0.75, Turn 5: 0.44,
    Turn 10: 0.23, Turn 15: 0.10, Turn 20: 0.03
    """
    return 1.0 - _sin_sqrt_norm(turn_abstand, GV_SESSION_AKT_CAP)


# ─────────────────────────────────────────────
# GV4: Wissensluecken finden
# ─────────────────────────────────────────────
# Durchsucht LZG (PostgreSQL/pgvector) und KZG (Redis/RediSearch)
# nach semantisch nahen, aber unbesprochenen Konzepten.
# Berechnet Relevanz aus 6 Systemen: Gedaechtnis, Aktualitaet,
# Drive, Neugier, Register, Charakter.
# Konzept: Chat 71 — validiert über 58-Testfälle-Matrix.


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine-Similarity zwischen zwei Vektoren."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    dot: float = float(np.dot(a, b))
    norm_a: float = float(np.linalg.norm(a))
    norm_b: float = float(np.linalg.norm(b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _ist_bereits_erwaehnt(inhalt: str, session_turns: list[dict]) -> bool:
    """Prueft ob der Inhalt einer Luecke bereits in der Session erwaehnt wurde.

    Einfacher Token-Overlap: Wenn mehr als 40% der Woerter des Inhalts
    in den letzten 8 Session-Turns vorkommen, gilt es als bereits besprochen.
    """
    if not session_turns:
        return False

    inhalt_woerter: set[str] = {
        w.lower() for w in inhalt.split() if len(w) > 3
    }
    if not inhalt_woerter:
        return False

    session_text: str = " ".join(
        turn.get("inhalt", "") for turn in session_turns[-8:]
    ).lower()

    treffer: int = sum(1 for w in inhalt_woerter if w in session_text)
    overlap: float = treffer / len(inhalt_woerter)
    return overlap > 0.4


def _lzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
) -> list[dict]:
    """Sucht semantisch nahe Eintraege im LZG via pgvector.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht, gap_arousal, quelle.
    """
    kandidaten: list[dict] = []

    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        embedding_str: str = "[" + ",".join(str(v) for v in turn_embedding) + "]"

        cursor.execute(
            """
            SELECT inhalt,
                   1 - (embedding <=> %s::vector) AS similarity,
                   gewicht,
                   COALESCE(arousal, 0.3) AS gap_arousal
            FROM langzeitgedaechtnis
            WHERE user_id = %s
              AND character_id = %s
              AND aktiv = TRUE
            ORDER BY embedding <=> %s::vector
            LIMIT 10
            """,
            (embedding_str, user_id, character_id, embedding_str),
        )

        for row in cursor.fetchall():
            inhalt, similarity, gewicht, gap_arousal = row
            if similarity and similarity > 0.1:
                kandidaten.append({
                    "konzept":    inhalt,
                    "similarity": float(similarity),
                    "gewicht":    float(gewicht) if gewicht else 0.5,
                    "gap_arousal": float(gap_arousal),
                    "quelle":     "lzg",
                })

        conn.close()
        logger.info(f"GV4-LZG: {len(kandidaten)} Kandidaten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-LZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def _kzg_kandidaten_suchen(
    turn_embedding: list[float],
    user_id:        str,
    character_id:   str,
) -> list[dict]:
    """Sucht semantisch nahe Eintraege im KZG via RediSearch KNN.

    Nutzt config.redis_client. Da wir nur Text-/Numeric-Felder zurueckliefern
    (kein Embedding-Blob), spielt decode_responses=True hier keine Rolle —
    die Query-Bytes werden via PARAMS unbeeinflusst durchgereicht.

    Returns:
        Liste von Dicts mit konzept, similarity, gewicht (=salienz), gap_arousal, quelle.
    """
    kandidaten: list[dict] = []

    try:
        query_blob: bytes = np.array(turn_embedding, dtype=np.float32).tobytes()

        ergebnis = redis_client.execute_command(
            "FT.SEARCH", "idx:kzg",
            f"(@user_id:{{{user_id}}} @character_id:{{{character_id}}})"
            f"=>[KNN 10 @embedding $vec AS score]",
            "PARAMS", "2", "vec", query_blob,
            "SORTBY", "score",
            "LIMIT", "0", "10",
            "RETURN", "4", "inhalt", "salienz", "arousal", "score",
            "DIALECT", "2",
        )

        if ergebnis and isinstance(ergebnis, list) and len(ergebnis) > 1:
            idx: int = 1
            while idx < len(ergebnis) - 1:
                _key = ergebnis[idx]
                felder = ergebnis[idx + 1]
                idx += 2

                feld_dict: dict = {}
                for i in range(0, len(felder), 2):
                    k = felder[i].decode("utf-8") if isinstance(felder[i], bytes) else felder[i]
                    v = felder[i + 1].decode("utf-8") if isinstance(felder[i + 1], bytes) else felder[i + 1]
                    feld_dict[k] = v

                inhalt:  str   = feld_dict.get("inhalt", "")
                salienz: float = float(feld_dict.get("salienz", "0.5"))
                arousal: float = float(feld_dict.get("arousal", "0.3"))
                score:   float = float(feld_dict.get("score", "1.0"))
                similarity: float = 1.0 - score

                if inhalt and similarity > 0.1:
                    kandidaten.append({
                        "konzept":     inhalt,
                        "similarity":  similarity,
                        "gewicht":     salienz,
                        "gap_arousal": arousal,
                        "quelle":      "kzg",
                    })

        logger.info(f"GV4-KZG: {len(kandidaten)} Kandidaten gefunden")

    except Exception as fehler:
        logger.warning(f"GV4-KZG-Suche fehlgeschlagen: {fehler}")

    return kandidaten


def _wissensluecken_finden(
    state:             ConversationState,
    effektive_neugier: float,
) -> list[dict]:
    """Findet semantisch nahe, aber unbesprochene Konzepte.

    Durchsucht LZG (pgvector) und KZG (RediSearch), filtert bereits
    Erwaentes und zu Aehnliches heraus, berechnet Relevanz aus
    6 Systemen und gibt die Top-N Luecken zurueck.

    Systeme:
      1. Gedaechtnis     — similarity × gewicht (aus DB)
      2. Aktualitaet     — nur Session-Turns (hier: alle DB = 1.0)
      3. Drive           — Ziel-Gravitation (neugier_boost)
      4. Neugier         — effektive_neugier (6 Saeulen, sin^0.5)
      5. Register        — register_kompatibilitaet (sachlich/offen)
      6. Charakter       — kern_hash Cosine >= Schwelle

    Returns:
        Top GV_LUECKEN_MAX Luecken sortiert nach Relevanz,
        oder leere Liste wenn nichts gefunden.
    """
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "nova")
    user_prompt:  str = state.get("user_prompt", "")
    modus:        str = state.get("gespraechs_modus", "alltag")
    dynamik:      str = state.get("beziehungs_dynamik", "neutral")

    if not user_prompt or not user_id:
        return []

    # ── 1. Turn-Embedding ──
    # Bevorzugt das vom Enricher bereits berechnete Embedding (spart ~1.6s).
    turn_embedding: list[float] = state.get("prompt_embedding") or []
    if not turn_embedding:
        try:
            turn_embedding = embedding_create(
                user_prompt, ollama_gpu_client, EMBED_MODEL
            )
        except Exception as fehler:
            logger.warning(f"GV4: Embedding fehlgeschlagen: {fehler}")
            return []

    # ── 2. Kandidaten aus LZG + KZG ──
    lzg_kandidaten: list[dict] = _lzg_kandidaten_suchen(
        turn_embedding, user_id, character_id
    )
    kzg_kandidaten: list[dict] = _kzg_kandidaten_suchen(
        turn_embedding, user_id, character_id
    )
    alle_kandidaten: list[dict] = lzg_kandidaten + kzg_kandidaten

    if not alle_kandidaten:
        logger.info("GV4: Keine Kandidaten gefunden")
        return []

    # ── 3. Filter: bereits erwaehnt ──
    session_turns: list[dict] = state.get("session_turns", [])
    gefiltert: list[dict] = [
        k for k in alle_kandidaten
        if not _ist_bereits_erwaehnt(k["konzept"], session_turns)
    ]

    gefiltert = [
        k for k in gefiltert
        if k["similarity"] <= GV_LUECKEN_SIM_OBERGRENZE
    ]

    if not gefiltert:
        logger.info("GV4: Alle Kandidaten bereits erwaehnt oder zu aehnlich")
        return []

    # ── 4. Relevanz berechnen ──
    aktivierte_ziele: list[dict] = state.get("aktivierte_ziele", [])

    for k in gefiltert:
        basis: float = k["similarity"] * k["gewicht"] * GV_QUELLEN_FAKTOR

        # Neugier-Boost aus Ziel-Gravitation (Turn-Embedding als Proxy)
        neugier_boost: float = 0.0
        if aktivierte_ziele:
            max_grav: float = 0.0
            for ziel in aktivierte_ziele:
                ziel_embedding = ziel.get("embedding")
                if not ziel_embedding:
                    continue
                ziel_sim: float = _cosine_similarity(
                    turn_embedding, ziel_embedding
                )
                grav: float = ziel_sim * ziel.get("motivation", 0.5)
                max_grav = max(max_grav, grav)
            if max_grav >= GV_NEUGIER_BOOST_SCHWELLE:
                neugier_boost = max_grav

        register: float = _register_kompatibilitaet(
            k["gap_arousal"], modus, dynamik
        )

        relevanz: float = (
            basis
            * (1.0 + neugier_boost)
            * effektive_neugier
            * register
        )

        k["relevanz"]      = relevanz
        k["neugier_boost"] = neugier_boost
        k["register"]      = register

    # ── 5. Charakter-Filter ──
    nova_kern: str = state.get("nova_kern", "")
    if nova_kern:
        try:
            kern_embedding: list[float] = embedding_create(
                nova_kern, ollama_gpu_client, EMBED_MODEL
            )
            for k in gefiltert:
                # Turn-Embedding als Proxy fuer Luecken-Embedding
                k["charakter_resonanz"] = _cosine_similarity(
                    turn_embedding, kern_embedding
                )
        except Exception as fehler:
            logger.warning(f"GV4: Kern-Embedding fehlgeschlagen: {fehler}")
            for k in gefiltert:
                k["charakter_resonanz"] = 0.5
    else:
        for k in gefiltert:
            k["charakter_resonanz"] = 0.5

    qualifiziert: list[dict] = [
        k for k in gefiltert
        if k["relevanz"] >= GV_LUECKEN_MIN_RELEVANZ
        and k["charakter_resonanz"] >= GV_CHARAKTER_RESONANZ_SCHWELLE
    ]

    qualifiziert.sort(key=lambda k: k["relevanz"], reverse=True)

    # Deduplizierung: Wenn zwei Luecken untereinander zu aehnlich sind,
    # nur die mit der hoeheren Relevanz behalten.
    dedupliziert: list[dict] = []
    for kandidat in qualifiziert:
        ist_duplikat: bool = False
        for behalten in dedupliziert:
            # Einfacher Token-Overlap als Proxy (kein Embedding noetig)
            woerter_a: set[str] = {w.lower() for w in kandidat["konzept"].split() if len(w) > 3}
            woerter_b: set[str] = {w.lower() for w in behalten["konzept"].split() if len(w) > 3}
            if woerter_a and woerter_b:
                overlap: float = len(woerter_a & woerter_b) / min(len(woerter_a), len(woerter_b))
                if overlap > 0.6:
                    ist_duplikat = True
                    logger.debug(
                        f"GV4-Dedup: '{kandidat['konzept'][:50]}' "
                        f"ist Duplikat von '{behalten['konzept'][:50]}' "
                        f"(Overlap {overlap:.0%})"
                    )
                    break
        if not ist_duplikat:
            dedupliziert.append(kandidat)
    qualifiziert = dedupliziert

    # ── 6. Top N ──
    qualifiziert.sort(key=lambda k: k["relevanz"], reverse=True)
    ergebnis: list[dict] = qualifiziert[:GV_LUECKEN_MAX]

    if ergebnis:
        logger.info(
            f"GV4: {len(ergebnis)} Wissensluecken qualifiziert — "
            + ", ".join(
                f"'{l['konzept'][:40]}' ({l['quelle']}, rel={l['relevanz']:.3f})"
                for l in ergebnis
            )
        )
    else:
        logger.info(
            f"GV4: {len(gefiltert)} Kandidaten geprueft, "
            f"keine ueber Relevanz-Schwelle {GV_LUECKEN_MIN_RELEVANZ}"
        )

    return ergebnis


# ─────────────────────────────────────────────
# LLM-Call: Hypothese destillieren
# ─────────────────────────────────────────────

def _hypothese_destillieren(
    state:            ConversationState,
    max_laenge:       int,
    entity_kontext:   str,
    farbton:          str = "",
    wissensluecken:   list[dict] | None = None,
    strategie_aktiv:  bool = False,
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

    # Situativer Farbton (kommt als Parameter, nicht mehr hier berechnet)
    farbton_block: str = f"\n\n[SITUATION]\n{farbton}" if farbton else ""

    system_parts.append(
        PROMPTS["gv.task"].format(
            max_laenge=max_laenge,
            strategie_block=PROMPTS["gv.strategie"] if strategie_aktiv else (
                "Beschreibe die LANDSCHAFT — nicht die Route.\n"
                "Beschreibe WAS IST und WAS KOMMT — nicht was Nova tun soll."
            ),
        ) + farbton_block
    )

    if strategie_aktiv:
        logger.info("GV3: Strategie-Prompt eingefuegt (Laenge >= GV_STRATEGIE_MIN_LAENGE)")

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
    # Bewusst deaktiviert: GV-Node hat eigene Kontextquellen (Entity-Hops,
    # Wissensluecken) und braucht den Enricher-Dump nicht — entlastet Prompt.
    # memory_context: str = state.get("memory_context", "")
    # if memory_context:
    #     user_parts.append(
    #         f"[GEDAECHTNIS]\n"
    #         f"{memory_context}"
    #     )

    # Wissensluecken (GV4) — nur wenn vorhanden
    if wissensluecken:
        luecken_zeilen: list[str] = []
        for luecke in wissensluecken:
            zeile: str = (
                f"- {luecke['konzept'][:120]}"
                f" (Quelle: {luecke['quelle']}, Relevanz: {luecke['relevanz']:.2f})"
            )
            luecken_zeilen.append(zeile)
        user_parts.append(
            "[WISSENSLUECKEN]\n"
            "Semantisch nahe, aber noch nicht besprochen:\n"
            + "\n".join(luecken_zeilen)
            + "\n\nDu kannst diese Konzepte als naechsten Gedankenschritt "
            "einbringen — aber nur wenn sie zum Gespraechsfluss passen."
        )
        logger.info(f"GV4: {len(wissensluecken)} Luecken in Prompt eingefuegt")

    user_message: str = "\n\n".join(user_parts)

    logger.info(
        f"GV-Prompt: System={len(system_prompt)} Zeichen, "
        f"User={len(user_message)} Zeichen"
    )

    # --- LLM-Call ---
    node_cfg: dict = get_node_config("gespraechsvektor")
    provider = get_chat_provider()

    logger.debug(
        "=== GV LLM-INPUT ===\n"
        "═══ SYSTEM ═══\n%s\n\n"
        "═══ USER ═══\n%s\n"
        "=== ENDE GV LLM-INPUT ===",
        system_prompt,
        user_message,
    )

    antwort = provider.chat(
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
        temperature=node_cfg.get("temperature", 0.6),
        max_output_tokens=node_cfg.get("max_output_tokens", 512),
        caller="gespraechsvektor",
    )

    hypothese: str = antwort.content.strip()
    logger.info(f"GV-Hypothese ({antwort.token_total} Tokens): {hypothese[:500]}...")
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
      3b. Farbmisch-System (Python, 8 Dimensionen → Landschaftsbeschreibung)
      3c. GV4: Effektive Neugier berechnen (Python, 6 Saeulen)
      3d. GV4: Wissensluecken finden (DB-Queries, Relevanz-Berechnung)
      4. LLM-Call → Hypothese + Strategie destillieren
      5. Ergebnis + Debug-Info in State schreiben
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

    # 3b. Farbton (einmal berechnen, durchreichen)
    farbton: str = _gv_strategie(state)
    if farbton:
        logger.info(f"GV-Farbton: {farbton}")

    # 3c. GV4: Effektive Neugier
    strategie_aktiv:    bool       = max_laenge >= GV_STRATEGIE_MIN_LAENGE
    effektive_neugier:  float      = 0.0
    wissensluecken:     list[dict] = []

    if strategie_aktiv:
        effektive_neugier = _effektive_neugier_berechnen(state)

        # 3d. GV4: Wissensluecken finden (nur wenn Neugier > 0)
        if effektive_neugier > 0:
            wissensluecken = _wissensluecken_finden(state, effektive_neugier)

    # 4. Hypothese destillieren
    hypothese: str = _hypothese_destillieren(
        state, max_laenge, entity_kontext,
        farbton=farbton,
        wissensluecken=wissensluecken,
        strategie_aktiv=strategie_aktiv,
    )

    # 5. State schreiben
    state["gespraechsvektor"] = hypothese

    state["gv_detail"] = {
        "laenge":            max_laenge,
        "farbton":           farbton,
        "entity_hops":       entity_kontext[:500] if entity_kontext else "",
        "effektive_neugier": effektive_neugier,
        "wissensluecken": [
            {
                "konzept":       l["konzept"][:120],
                "quelle":        l["quelle"],
                "relevanz":      round(l["relevanz"], 3),
                "neugier_boost": round(l.get("neugier_boost", 0), 3),
                "register":      round(l.get("register", 1.0), 2),
            }
            for l in wissensluecken
        ],
        "strategie_aktiv": strategie_aktiv,
    }

    return state
