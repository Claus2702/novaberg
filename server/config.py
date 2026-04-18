"""
KI-Server — Zentrale Konfiguration.
Umgebungsvariablen, Verbindungen, gemeinsame Ressourcen.
"""

import math
import os
import logging
import threading

import redis
import ollama
import psycopg2
from dotenv import load_dotenv

# .env laden (Repo-Root und aufwaerts). Fuer lokale Entwicklung; im Docker-
# Container werden die Werte zusaetzlich ueber env_file injiziert.
load_dotenv()

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level  = logging.DEBUG,
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ki_server")

# Token-Tracking auf DEBUG sichtbar machen
_llm_logger = logging.getLogger("ki_server.llm")
_llm_logger.setLevel(logging.DEBUG)
_llm_handler = logging.StreamHandler()
_llm_handler.setLevel(logging.DEBUG)
_llm_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
_llm_logger.addHandler(_llm_handler)
_llm_logger.propagate = False

# ─────────────────────────────────────────────
# Infrastruktur (profilunabhaengig)
# ─────────────────────────────────────────────
REDIS_URL:    str = os.getenv("REDIS_URL",    "redis://localhost:6379")
POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://ki:ki@localhost:5432/gedaechtnis")
TIMEZONE:     str = os.getenv("TIMEZONE",      "Europe/Berlin")

ASSISTANT_NAME:  str = os.getenv("ASSISTANT_NAME",  "Nova")
BACKGROUND_NAME: str = os.getenv("BACKGROUND_NAME", "Pixie")

redis_client:   redis.Redis     = redis.from_url(REDIS_URL, decode_responses=True)
llm_lock:       threading.Lock  = threading.Lock()
shutdown_event: threading.Event = threading.Event()

# ─────────────────────────────────────────────
# LLM-Profil — Schalter
# ─────────────────────────────────────────────
# "lokal" = Ollama (GPU + CPU), "claude" = Anthropic API
LLM_PROFILE: str = os.getenv("LLM_PROFILE", "lokal")

# Connector innerhalb "lokal" — bestimmt welche Modelle geladen werden
# "mistral" = Mistral Small 3.2 (bisheriger Standard)
# "gemma4"  = Google Gemma 4 26B-A4B (MoE, 3.8B aktiv)
OLLAMA_CONNECTOR: str = os.getenv("OLLAMA_CONNECTOR", "gemma4")

# ─────────────────────────────────────────────
# Profil "lokal" — Ollama
# ─────────────────────────────────────────────
# Verbindungen
OLLAMA_GPU_URL:     str           = os.getenv("OLLAMA_GPU_URL", "http://localhost:11434")
OLLAMA_CPU_URL:     str           = os.getenv("OLLAMA_CPU_URL", "http://localhost:11435")
ollama_gpu_client:  ollama.Client = ollama.Client(host=OLLAMA_GPU_URL)
ollama_cpu_client:  ollama.Client = ollama.Client(host=OLLAMA_CPU_URL)

# Connector-Definitionen (Modelle + Context + Think-Default)
OLLAMA_CONNECTORS: dict = {
    "mistral": {
        "gpu_model":       "mistral-small3.2-gpu",
        "gpu_num_ctx":     16384,
        "cpu_model":       "mistral-small3.2-cpu",
        "cpu_num_ctx":     32768,
        "analyse_model":   "qwen3-32b-cpu",
        "analyse_num_ctx": 32768,
        "think":           False,
    },
    "gemma4": {
        "gpu_model":       "gemma4-gpu",
        "gpu_num_ctx":     32768,
        "cpu_model":       "gemma4-cpu",
        "cpu_num_ctx":     32768,
        "analyse_model":   "qwen3-32b-cpu",
        "analyse_num_ctx": 32768,
        "think":           False,
    },
}

# Aktiver Connector → bestehende Variablen auflösen
_connector = OLLAMA_CONNECTORS[OLLAMA_CONNECTOR]
OLLAMA_MODEL:          str  = _connector["gpu_model"]
OLLAMA_GPU_NUM_CTX:    int  = _connector["gpu_num_ctx"]
SHADOW_MODEL:          str  = _connector["cpu_model"]
OLLAMA_CPU_NUM_CTX:    int  = _connector["cpu_num_ctx"]
PIXIE_ANALYSE_MODEL:   str  = _connector["analyse_model"]
PIXIE_ANALYSE_NUM_CTX: int  = _connector["analyse_num_ctx"]
OLLAMA_THINK_DEFAULT:  bool = _connector["think"]

# Embedding (immer Ollama, auch bei Profil "claude")
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")

# ─────────────────────────────────────────────
# Profil "claude" — Anthropic API
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY:            str   = os.getenv("ANTHROPIC_API_KEY",   "")
ANTHROPIC_MODEL:              str   = os.getenv("ANTHROPIC_MODEL",     "claude-sonnet-4-6")
ANTHROPIC_PRICE_INPUT_PER_M:  float = float(os.getenv("ANTHROPIC_PRICE_INPUT_PER_M",  "3.0"))
ANTHROPIC_PRICE_OUTPUT_PER_M: float = float(os.getenv("ANTHROPIC_PRICE_OUTPUT_PER_M", "15.0"))

# ─────────────────────────────────────────────
# Pixie-Einstellungen (Background Task)
# ─────────────────────────────────────────────
PIXIE_INTERVALL_MIN: int = int(os.getenv("PIXIE_INTERVALL_MIN", "2"))

# Pixie Heartbeat (kompetitives Scheduling, Chat 33)
PIXIE_INTERVALL_SEKUNDEN: int = int(os.getenv("PIXIE_INTERVALL_SEKUNDEN", "120"))
PIXIE_LOCK_TTL_SEKUNDEN:  int = int(os.getenv("PIXIE_LOCK_TTL_SEKUNDEN", "600"))

# --- Pixie Agent: Promotion ---
PIXIE_PROMOTION_PRIORITAET:          float = float(os.getenv("PIXIE_PROMOTION_PRIORITAET", "0.9"))
PIXIE_PROMOTION_INTERVALL_SEKUNDEN:  int   = int(os.getenv("PIXIE_PROMOTION_INTERVALL_SEKUNDEN", "300"))   # 5 Minuten

# --- Pixie Agent: Decay ---
PIXIE_DECAY_PRIORITAET:              float = float(os.getenv("PIXIE_DECAY_PRIORITAET", "0.2"))
PIXIE_DECAY_INTERVALL_SEKUNDEN:      int   = int(os.getenv("PIXIE_DECAY_INTERVALL_SEKUNDEN", "86400"))     # 24 Stunden

# --- Pixie Agent: Charakter ---
PIXIE_CHARAKTER_PRIORITAET:          float = float(os.getenv("PIXIE_CHARAKTER_PRIORITAET", "0.3"))
PIXIE_CHARAKTER_INTERVALL_SEKUNDEN:  int   = int(os.getenv("PIXIE_CHARAKTER_INTERVALL_SEKUNDEN", "600"))   # 10 Minuten
PIXIE_CHARAKTER_LZG_LIMIT:          int   = int(os.getenv("PIXIE_CHARAKTER_LZG_LIMIT", "50"))
PIXIE_CHARAKTER_KZG_LIMIT:          int   = int(os.getenv("PIXIE_CHARAKTER_KZG_LIMIT", "20"))

# --- Pixie Agent: Wiedervorlage ---
PIXIE_WIEDERVORLAGE_PRIORITAET:          float = float(os.getenv("PIXIE_WIEDERVORLAGE_PRIORITAET", "0.5"))
PIXIE_WIEDERVORLAGE_INTERVALL_SEKUNDEN:  int   = int(os.getenv("PIXIE_WIEDERVORLAGE_INTERVALL_SEKUNDEN", "43200"))  # 12 Stunden
PIXIE_WIEDERVORLAGE_SNOOZE_TAGE:         int   = int(os.getenv("PIXIE_WIEDERVORLAGE_SNOOZE_TAGE", "7"))

# --- Pixie Agent: Recherche ---
PIXIE_RECHERCHE_SESSION_TURNS:           int   = int(os.getenv("PIXIE_RECHERCHE_SESSION_TURNS", "10"))
PIXIE_RECHERCHE_MAX_ITERATIONEN:         int   = int(os.getenv("PIXIE_RECHERCHE_MAX_ITERATIONEN", "3"))
PIXIE_RECHERCHE_MAX_QUERIES:             int   = int(os.getenv("PIXIE_RECHERCHE_MAX_QUERIES", "4"))
PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE:    int   = int(os.getenv("PIXIE_RECHERCHE_MAX_SEITEN_PRO_RUNDE", "3"))

# ─── KZG (Kurzzeitgedaechtnis) ─────────────────
KZG_SALIENZ_MINIMUM:          float = float(os.getenv("KZG_SALIENZ_MINIMUM", "0.5"))
KZG_SALIENZ_HIGH:             float = float(os.getenv("KZG_SALIENZ_HIGH", "0.7"))
KZG_TTL_LOW_SEKUNDEN:         int   = int(os.getenv("KZG_TTL_LOW_SEKUNDEN", "604800"))      # 7 Tage
KZG_TTL_HIGH_SEKUNDEN:        int   = int(os.getenv("KZG_TTL_HIGH_SEKUNDEN", "2592000"))     # 30 Tage
KZG_VERTIEFUNG_HAEUFIGKEIT:   int   = int(os.getenv("KZG_VERTIEFUNG_HAEUFIGKEIT", "3"))

# ─── Vertiefung ────────────────────────────────
PIXIE_VERTIEFUNG_LZG_LIMIT:  int = int(os.getenv("PIXIE_VERTIEFUNG_LZG_LIMIT", "20"))
PIXIE_VERTIEFUNG_KZG_LIMIT:  int = int(os.getenv("PIXIE_VERTIEFUNG_KZG_LIMIT", "10"))

# ─── Delegation ────────────────────────────────
DELEGATION_SIMILARITY_SCHWELLE: float = float(os.getenv("DELEGATION_SIMILARITY_SCHWELLE", "0.82"))

# ─── Notizen-Suche ─────────────────────────────
NOTIZEN_SUCHE_MIN_SIMILARITY:        float = float(os.getenv("NOTIZEN_SUCHE_MIN_SIMILARITY", "0.15"))
NOTIZEN_SUCHE_MIN_SCORE:             float = float(os.getenv("NOTIZEN_SUCHE_MIN_SCORE", "0.3"))
NOTIZEN_SUCHE_LIMIT:                 int   = int(os.getenv("NOTIZEN_SUCHE_LIMIT", "10"))
NOTIZEN_ZUSAMMENFASSUNG_MAX_WOERTER: int   = int(os.getenv("NOTIZEN_ZUSAMMENFASSUNG_MAX_WOERTER", "20"))

# ─── Timeline-Suche ────────────────────────────
TIMELINE_SUCHE_LIMIT:              int = int(os.getenv("TIMELINE_SUCHE_LIMIT", "10"))
TIMELINE_UEBERSICHT_TAGE_ZURUECK:  int = int(os.getenv("TIMELINE_UEBERSICHT_TAGE_ZURUECK", "3"))
TIMELINE_UEBERSICHT_TAGE_VORAUS:   int = int(os.getenv("TIMELINE_UEBERSICHT_TAGE_VORAUS", "14"))

# ─────────────────────────────────────────────
# Web-Suche (SearXNG)
# ─────────────────────────────────────────────
SEARXNG_URL:         str = os.getenv("SEARXNG_URL",      "http://searxng:8080")
SEARXNG_TIMEOUT:   float = float(os.getenv("SEARXNG_TIMEOUT",     "10.0"))
SEARXNG_MAX_RESULTS: int = int(os.getenv("SEARXNG_MAX_RESULTS",   "10"))

# --- Web-Tools: PageFetcher ---
PAGE_FETCH_TIMEOUT:   float = float(os.getenv("PAGE_FETCH_TIMEOUT", "10.0"))
PAGE_FETCH_MAX_CHARS: int   = int(os.getenv("PAGE_FETCH_MAX_CHARS", "5000"))

# ─────────────────────────────────────────────
# Emotionale Intelligenz
# ─────────────────────────────────────────────
# Gewichtungsfaktoren für die Emotions-, Stil- und Beziehungsanalyse.

# Emotions-Decay: Steilheit des logarithmischen Abfalls.
# Formel: gewicht = 1.0 / (1.0 + EMOTION_DECAY_FACTOR * log_base(1 + position))
# Bei Factor 0.8, Basis 10: Turn 0 = 1.0, Turn 1 = 0.81, Turn 5 = 0.62, Turn 10 = 0.51
EMOTION_DECAY_FACTOR: float = 0.8

# Logarithmus-Basis für den Emotions-Decay.
# 10 = sanfter Abfall (empfohlen), math.e = moderat, 2 = steil
EMOTION_DECAY_BASE: float = 10

# Maximale Anzahl an Turns für den Emotions-Verlauf.
# Maximale Turns für Emotions-Verlauf.
# Hoch setzen = volle Session nutzen. Der arousal-basierte Decay
# regelt, was davon noch Gewicht hat. Kleine Emotionen verfallen
# schnell, große halten durch — das Fenster muss nur groß genug sein.
EMOTION_MAX_TURNS: int = 100

# Mindest-Gewicht — Emotionen darunter werden entfernt.
EMOTION_MIN_WEIGHT: float = 0.15

# Fenster für Vektor-Berechnung (Richtungswechsel).
# Kurz halten — der Vektor soll Wendepunkte erkennen, nicht Grundstimmung.
EMOTION_VEKTOR_TURNS: int = 8

# Fenster für Sprachstil-Erkennung (regelbasiert).
# Misst aktuelle Formulierung, nicht emotionalen Kontext.
STIL_ANALYSE_TURNS: int = 5

# Stil-Adaption: Gewichtung Session (kurzfristig) vs. Hash (langfristig).
# 0.0 = nur Hash, 1.0 = nur Session.
STIL_SESSION_GEWICHT: float = 0.7

# Beziehungs-Einfluss: Wie stark das Beziehungsprofil den Responder beeinflusst.
# 0.0 = kein Einfluss, 1.0 = voller Einfluss.
BEZIEHUNG_EINFLUSS: float = 0.8

# ─────────────────────────────────────────────
# Emotions-Vektoren (Richtungsanweisungen für den Responder)
# ─────────────────────────────────────────────
# Default-Arousal pro Emotion (16 kanonische + neutral)
EMOTION_DEFAULT_AROUSAL: dict[str, float] = {
    "begeisterung": 0.7,  "freude": 0.5,
    "dankbarkeit": 0.5,   "zufriedenheit": 0.3,
    "stress": 0.6,        "unsicherheit": 0.4,
    "ueberrascht": 0.7,   "verwundert": 0.4,
    "verzweiflung": 0.8,  "traurigkeit": 0.4,
    "frustration": 0.6,   "enttaeuschung": 0.5,
    "wut": 0.8,           "aerger": 0.5,
    "hoffnung": 0.5,      "neugierig": 0.4,
    "neutral": 0.2,
}

# Arousal-Decay-Rate pro Emotion
# Hohe Rate = Energie verfliegt schnell (Dopamin)
# Niedrige Rate = Energie hält lange (Cortisol)
# Formel: gedämpfter_arousal = original_arousal × e^(-rate × position)
EMOTION_AROUSAL_DECAY: dict[str, float] = {
    # Sektor 1 — Freude: Dopamin-Peak, verfliegt schnell
    "begeisterung":  0.15,
    "freude":        0.10,
    # Sektor 2 — Zuversicht: stabile Grundstimmung
    "dankbarkeit":   0.08,
    "zufriedenheit": 0.05,
    # Sektor 3 — Angst: setzt sich fest
    "stress":        0.04,
    "unsicherheit":  0.05,
    # Sektor 4 — Überraschung: extrem kurzlebig
    "ueberrascht":   0.20,
    "verwundert":    0.15,
    # Sektor 5 — Trauer: gräbt sich ein (Cortisol)
    "verzweiflung":  0.02,
    "traurigkeit":   0.03,
    # Sektor 6 — Enttäuschung: bleibt als Groll
    "frustration":   0.04,
    "enttaeuschung": 0.05,
    # Sektor 7 — Ärger: intensiv aber abbaubar (Adrenalin)
    "wut":           0.08,
    "aerger":        0.06,
    # Sektor 8 — Neugier: flüchtig, springt weiter
    "hoffnung":      0.08,
    "neugierig":     0.12,
}


def arousal_label(value: float) -> str:
    """Leitet ein menschenlesbares Label aus dem Arousal-Float ab."""
    if value >= 0.7:
        return "high"
    elif value >= 0.4:
        return "mid"
    else:
        return "low"

EMOTIONS_VEKTOREN: dict[str, str] = {
    "absturz": (
        "EMOTIONALER VEKTOR: ABSTURZ (positiv → negativ). "
        "Der Nutzer war gerade noch in guter Stimmung und ist abgestürzt. "
        "Er erlebt einen Umschwung — das ist ein Schock, nicht ein sanfter Übergang."
    ),
    "spirale": (
        "EMOTIONALER VEKTOR: SPIRALE (negativ → noch negativer). "
        "Der Nutzer rutscht tiefer ab. Neue negative Emotionen kommen hinzu. "
        "Die Intensität steigt oder hält sich auf hohem Niveau."
    ),
    "stabilisierung": (
        "EMOTIONALER VEKTOR: STABILISIERUNG (negativ → neutral). "
        "Der Nutzer beruhigt sich nach einem schweren Moment. "
        "Die Intensität lässt nach, er findet zurück in ruhigeres Fahrwasser."
    ),
    "erholung": (
        "EMOTIONALER VEKTOR: ERHOLUNG (negativ → positiv). "
        "Der Nutzer kommt aus einem emotionalen Tief und zeigt erste positive Signale. "
        "Er ist noch erschöpft von dem was war, auch wenn er jetzt lächelt."
    ),
    "aufbluehen": (
        "EMOTIONALER VEKTOR: AUFBLÜHEN (neutral → positiv). "
        "Der Nutzer blüht auf. Die Stimmung hebt sich, Energie kommt rein."
    ),
    "eskalation": (
        "EMOTIONALER VEKTOR: ESKALATION (positiv → noch positiver). "
        "Der Nutzer ist in Hochstimmung. Die Begeisterung steigt weiter."
    ),
    "abkuehlung": (
        "EMOTIONALER VEKTOR: ABKÜHLUNG (positiv → neutral). "
        "Die Begeisterung klingt ab. Natürlicher Übergang, kein Einbruch."
    ),
    "einbruch": (
        "EMOTIONALER VEKTOR: EINBRUCH (neutral → negativ). "
        "Die Stimmung kippt. Etwas belastet den Nutzer, das vorher nicht da war."
    ),
    "plateau": (
        "EMOTIONALER VEKTOR: PLATEAU (stabil). "
        "Die Stimmung ist gleichbleibend. Keine Veränderung in der emotionalen Richtung."
    ),
}


# ─── Ebbinghaus-Gedächtnisverfall ────────────
# Decay-Rate (Lambda) für den zeitlichen Verfall von LZG-Einträgen.
# Das effektive Gewicht wird NICHT gespeichert, sondern bei jedem Zugriff
# live berechnet: effektiv = gewicht * e^(-lambda * tage_seit_verstaerkung)
#
# Beispielwerte bei decay_rate = 0.0015:
#   1 Monat:  Decay-Faktor 0.96 (kaum Verfall)
#   6 Monate: Decay-Faktor 0.76
#   1 Jahr:   Decay-Faktor 0.58
#   2 Jahre:  Decay-Faktor 0.33
#   3 Jahre:  Decay-Faktor 0.19
#
# 0.0015 = sanfter Verfall (~3 Jahre bis einmalig Erwähntes verblasst)
# 0.003  = moderater Verfall (~1.5 Jahre)
# 0.005  = schneller Verfall (~1 Jahr)
EBBINGHAUS_DECAY_RATE: float = 0.0015

# Schwellwert für Inaktiv-Markierung durch Pixie.
# Einträge mit effektivem Gewicht darunter werden als inaktiv markiert.
# Sie werden NICHT gelöscht — nur aus aktiven Abfragen ausgeschlossen.
EBBINGHAUS_MIN_GEWICHT: float = 0.1

# ─── Arousal-basierter Decay ────────────────
# Wie stark Arousal den Emotions-Decay bremst.
# Hoher Arousal → Emotion hält länger (Kündigung, Todesfall).
# Niedriger Arousal → Emotion verfällt normal (kleiner Ärger).
# Formel: effective_decay = DECAY_FACTOR × (1.0 - arousal × PERSISTENCE)
#
# Beispiele bei PERSISTENCE = 0.6:
#   Arousal 0.2 (kleiner Ärger):  decay_factor 0.70 → Turn 20: Gewicht 0.49
#   Arousal 0.5 (Frustration):    decay_factor 0.56 → Turn 20: Gewicht 0.56
#   Arousal 0.8 (Kündigung):      decay_factor 0.42 → Turn 20: Gewicht 0.64
#   Arousal 0.95 (Todesfall):     decay_factor 0.34 → Turn 20: Gewicht 0.69
#
# 0.0 = kein Effekt (alter Decay), 1.0 = maximale Persistenz
EI_AROUSAL_PERSISTENCE: float = 0.6

# ─── EI-Plausibilitäts-Gate ─────────────────
# Faktoren zur Berechnung des emotionalen Arousal (ei_arousal).
# ei_arousal = current_arousal * gewichteter Kombinationsfaktor
# Bestimmt ob der Gesprächsmodus "emotional" sein darf/muss.
# Werte > 1.0 verstärken, < 1.0 dämpfen die emotionale Wirkung.
# Änderung hier → sofortige Wirkung auf die EI-Bewertung.

EI_DYNAMIK_FAKTOREN: dict[str, float] = {
    "hilfesuchend": 1.5,    # Geht auf mich zu, braucht Empathie
    "angriff":      1.3,    # Hochgeladen, emotional aktiviert
    "dankbar":      1.2,    # Berührt, emotional offen
    "vertrauen":    1.1,    # Öffnet sich, leichte Verstärkung
    "neutral":      1.0,    # Kein Signal
    "distanz":      0.7,    # Will sachliche Behandlung
}

EI_INTENT_FAKTOREN: dict[str, float] = {
    "personal":     1.0,    # Persönliches Thema, neutrale Basis
    "creative":     0.8,    # Kreativ, leicht emotional
    "smalltalk":    0.5,    # Plauderton, wenig emotional
    "task":         0.3,    # Aufgabe, sachlich
    "knowledge":    0.3,    # Wissensfrage, sachlich
    "meta":         0.3,    # Über Nova, sachlich
}

EI_TONE_FAKTOREN: dict[str, float] = {
    "empathisch":   1.3,    # Perzeption sieht Empathie-Bedarf
    "kreativ":      0.8,    # Leicht offen
    "direkt":       0.5,    # Auf den Punkt, nicht emotional
    "sachlich":     0.3,    # Nüchtern
}

# Gewichtung der drei Faktor-Gruppen (Summe = 1.0)
EI_GEWICHTE: dict[str, float] = {
    "dynamik":      0.40,   # Beziehungsdynamik wiegt am stärksten
    "intent":       0.35,   # Was will der User
    "tone":         0.25,   # Wie soll geantwortet werden (bereits Ableitung)
}

# Passiv-negative Emotionen: Erzwingen "emotional" auch bei niedrigem Arousal
# Sektor 5 (Trauer) — immer emotional
EI_PASSIV_NEGATIVE: set[str] = {"verzweiflung", "traurigkeit"}

# ─────────────────────────────────────────────
# Plutchik-Emotionsmodell: 8 Sektoren, 16+1 Emotionen
# ─────────────────────────────────────────────

# Gültige kanonische Emotionen (Perzeption soll NUR diese liefern)
EMOTION_KANON: set[str] = {
    "begeisterung", "freude",           # Sektor 1 — Freude
    "dankbarkeit", "zufriedenheit",     # Sektor 2 — Zuversicht
    "stress", "unsicherheit",           # Sektor 3 — Angst
    "ueberrascht", "verwundert",        # Sektor 4 — Überraschung
    "verzweiflung", "traurigkeit",      # Sektor 5 — Trauer
    "frustration", "enttaeuschung",     # Sektor 6 — Enttäuschung
    "wut", "aerger",                    # Sektor 7 — Ärger
    "hoffnung", "neugierig",            # Sektor 8 — Neugier
    "neutral",
}

# Kanonische Emotion → Sektor (1–8)
EMOTION_SEKTOR_MAP: dict[str, int] = {
    # Sektor 1 — Freude (Joy)
    "begeisterung": 1, "freude": 1,
    # Sektor 2 — Zuversicht (Trust)
    "dankbarkeit": 2, "zufriedenheit": 2,
    # Sektor 3 — Angst (Fear)
    "stress": 3, "unsicherheit": 3,
    # Sektor 4 — Überraschung (Surprise)
    "ueberrascht": 4, "verwundert": 4,
    # Sektor 5 — Trauer (Sadness)
    "verzweiflung": 5, "traurigkeit": 5,
    # Sektor 6 — Enttäuschung (Disgust)
    "frustration": 6, "enttaeuschung": 6,
    # Sektor 7 — Ärger (Anger)
    "wut": 7, "aerger": 7,
    # Sektor 8 — Neugier (Anticipation)
    "hoffnung": 8, "neugierig": 8,
}

# Sektor → Emotions-Gruppe (für Vektor-Berechnung)
# Plutchik-Reihenfolge: positive und negative interleaved
SEKTOR_GRUPPE: dict[int, str] = {
    1: "positiv",    # Freude
    2: "positiv",    # Zuversicht
    3: "negativ",    # Angst
    4: "neutral",    # Überraschung (ambivalent)
    5: "negativ",    # Trauer
    6: "negativ",    # Enttäuschung
    7: "negativ",    # Ärger
    8: "positiv",    # Neugier
}

# Synonym → kanonische Emotion (falls Perzeption abweicht)
EMOTION_SYNONYM_MAP: dict[str, str] = {
    # → Sektor 1 Freude
    "glueck": "freude", "euphorie": "begeisterung",
    "heiterkeit": "freude", "ekstase": "begeisterung",
    # → Sektor 1 Freude (ehemals eigener Sektor "Stolz")
    "stolz": "freude", "triumph": "freude",
    "genugtuung": "freude", "selbstvertrauen": "freude",
    "selbstsicherheit": "freude",
    # → Sektor 2 Zuversicht (ehemals eigener Sektor)
    "erleichterung": "zufriedenheit",
    "gelassenheit": "zufriedenheit", "geborgenheit": "zufriedenheit",
    "vertrauen": "zufriedenheit",
    # → Sektor 3 Angst
    "angst": "stress", "furcht": "stress",
    "panik": "stress", "sorge": "unsicherheit",
    "nervositaet": "unsicherheit", "beklemmung": "unsicherheit",
    "anspannung": "stress",
    # → Sektor 4 Überraschung
    "schock": "ueberrascht", "ueberraschung": "ueberrascht",
    "fassungslos": "ueberrascht", "verbluefft": "verwundert",
    "perplex": "verwundert", "baff": "ueberrascht",
    # → Sektor 5 Trauer
    "resignation": "traurigkeit", "einsamkeit": "traurigkeit",
    "melancholie": "traurigkeit", "kummer": "verzweiflung",
    "niedergeschlagenheit": "traurigkeit", "nachdenklich": "traurigkeit",
    "leere": "traurigkeit",
    # → Sektor 6 Enttäuschung (inkl. Ekel-Achse)
    "frust": "frustration", "ernuechterung": "enttaeuschung",
    "verbitterung": "frustration", "desillusionierung": "enttaeuschung",
    "abscheu": "frustration", "ekel": "frustration",
    "verachtung": "frustration", "langeweile": "enttaeuschung",
    "ablehnung": "enttaeuschung", "desinteresse": "enttaeuschung",
    "gleichgueltigkeit": "enttaeuschung",
    # → Sektor 7 Ärger
    "zorn": "wut", "aggression": "wut",
    "gereizt": "aerger", "genervt": "aerger",
    "empoerung": "wut", "hass": "wut", "groll": "aerger",
    # → Sektor 8 Neugier
    "neugier": "neugierig", "neugierde": "neugierig",
    "interesse": "neugierig", "erwartung": "hoffnung",
    "vorfreude": "hoffnung", "gespannt": "neugierig",
}

# Basis-Exponenten für die sektorabhängige Normalisierung
# Werden mit dem Arousal der dominanten Emotion skaliert.
EI_NORM_BENACHBART: float = 0.7    # Distanz 1 — schützt benachbarte Emotionen
EI_NORM_NAH_DIAGONAL: float = 1.0  # Distanz 2 — neutral, wie bisherige Normalisierung
EI_NORM_FERN_DIAGONAL: float = 1.2 # Distanz 3 — leicht gedrückt
EI_NORM_GEGEN: float = 1.4         # Distanz 4 — stark gedrückt, Antagonisten

# Exponent für die Dominanzbestimmung: effektiv = gewicht × arousal^n
# n=2.0: Arousal 0.9 (Schock) hat 9× mehr Durchschlagskraft als Arousal 0.3 (Zufriedenheit)
EI_AROUSAL_DOMINANZ: float = 2.0

# ─── DelegationsAgent (VENT1) ─────────────────
DELEGATION_EFFEKTIVWERT_SCHWELLE: float = 0.15
DELEGATION_SALIENZ_SCHWELLE:      float = 0.6
DELEGATION_VERSTAERKUNG_DIVISOR:  float = 2.0
DELEGATION_AROUSAL_BOOST:         float = 0.5

# ─── Delegations-Signale (VENT1) ──────────────
# Situationsbeschreibungen fuer den Responder, indiziert nach
# (emotions_vektor, trigger). Beschreibend, nicht imperativ.
# Nova entscheidet selbst wie sie reagiert — das Signal nimmt
# ihr den Druck, selbst Loesungen erfinden zu muessen.
#
# Primaerschluessel: Emotions-Vektor (wo steht der Mensch emotional)
# Sekundaerschluessel: Trigger-Typ (warum wurde delegiert)
# Fallback: Wenn die Kombination nicht existiert, wird der Vektor-Default genutzt.

DELEGATION_SIGNALE: dict[tuple[str, str], str] = {

    # ── ABSTURZ (positiv → negativ) ──────────────
    ("absturz", "effektivwert"): (
        "Der Nutzer ist emotional abgestuerzt. Die Intensitaet ist hoch. "
        "Im Hintergrund wird nach Moeglichkeiten gesucht, die Situation zu verbessern. "
        "Der Nutzer braucht jetzt Halt und Praesenz. "
        "Keine Loesungen erfinden, keine Namen oder Termine nennen die nicht im Kontext stehen."
    ),
    ("absturz", "vektor"): (
        "Der Nutzer ist emotional abgestuerzt. "
        "Im Hintergrund wird das Thema aufgegriffen. "
        "Den Umschwung wahrnehmen, Raum geben."
    ),

    # ── SPIRALE (negativ → noch negativer) ───────
    ("spirale", "effektivwert"): (
        "Der Nutzer rutscht tiefer ab, die Intensitaet steigt. "
        "Im Hintergrund wird an einer Loesung gearbeitet. "
        "Jetzt zaehlt nur: auf seiner Seite sein. "
        "Nichts erfinden, nichts versprechen, nichts anbieten."
    ),
    ("spirale", "vektor"): (
        "Der Nutzer rutscht tiefer ab. "
        "Das Thema wird im Hintergrund begleitet. "
        "Praesent sein, nicht draengen."
    ),

    # ── EINBRUCH (neutral → negativ) ─────────────
    ("einbruch", "effektivwert"): (
        "Die Stimmung ist gekippt, etwas Neues belastet den Nutzer. "
        "Im Hintergrund wird das Thema aufgegriffen. "
        "Den Einbruch wahrnehmen, nicht uebergehen. "
        "Keine Loesungsvorschlaege erfinden."
    ),
    ("einbruch", "vektor"): (
        "Die Stimmung kippt. Etwas belastet den Nutzer. "
        "Im Hintergrund wird das Thema begleitet. "
        "Aufmerksam sein, nachfragen statt interpretieren."
    ),
    ("einbruch", "salienz"): (
        "Ein belastendes Thema ist aufgetaucht. "
        "Im Hintergrund wird vertieft."
    ),

    # ── STABILISIERUNG (negativ → neutral) ───────
    ("stabilisierung", "vektor"): (
        "Der Nutzer beruhigt sich nach einem schweren Moment. "
        "Im Hintergrund wird weiter am Thema gearbeitet. "
        "Die Ruhe nicht stoeren, nicht nachbohren. "
        "Er findet seinen Weg zurueck."
    ),
    ("stabilisierung", "salienz"): (
        "Der Nutzer stabilisiert sich. "
        "Das Thema wird im Hintergrund weiter begleitet."
    ),

    # ── ERHOLUNG (negativ → positiv) ─────────────
    ("erholung", "vektor"): (
        "Der Nutzer erholt sich aus einem emotionalen Tief. "
        "Im Hintergrund wird das Thema weiter begleitet. "
        "Die Besserung sanft anerkennen, nicht uebertreiben. "
        "Er ist noch erschoepft, auch wenn er laechelt."
    ),
    ("erholung", "salienz"): (
        "Der Nutzer erholt sich. "
        "Das Thema wird im Hintergrund weiter vertieft."
    ),

    # ── AUFBLUEHEN (neutral → positiv) ───────────
    ("aufbluehen", "vektor"): (
        "Der Nutzer blueht auf, die Stimmung hebt sich. "
        "Im Hintergrund wird das Thema vertieft. "
        "Die Energie teilen, mitgehen."
    ),
    ("aufbluehen", "salienz"): (
        "Der Nutzer ist positiv engagiert. "
        "Im Hintergrund wird das Thema vertieft. "
        "Begeisterung teilen."
    ),

    # ── ESKALATION (positiv → noch positiver) ────
    ("eskalation", "effektivwert"): (
        "Der Nutzer ist in Hochstimmung, die Begeisterung steigt. "
        "Im Hintergrund wird das Thema vertieft. "
        "Mitgehen, die Energie teilen. Nicht bremsen."
    ),
    ("eskalation", "vektor"): (
        "Der Nutzer ist begeistert. "
        "Im Hintergrund wird vertieft. "
        "Mitfreuen."
    ),

    # ── ABKUEHLUNG (positiv → neutral) ───────────
    ("abkuehlung", "vektor"): (
        "Die Begeisterung klingt ab. Natuerlicher Uebergang. "
        "Im Hintergrund wird das Thema weiter begleitet. "
        "Tempo des Nutzers folgen."
    ),
    ("abkuehlung", "salienz"): (
        "Das Thema war spannend und klingt ab. "
        "Im Hintergrund wird weiter vertieft."
    ),
}

# Fallback-Signale wenn die exakte Kombination nicht existiert
DELEGATION_SIGNALE_FALLBACK: dict[str, str] = {
    "effektivwert": (
        "Die emotionale Intensitaet ist hoch. "
        "Im Hintergrund wird am Thema gearbeitet. "
        "Keine Loesungen erfinden, keine Details die nicht im Kontext stehen."
    ),
    "vektor": (
        "Die emotionale Lage veraendert sich. "
        "Im Hintergrund wird das Thema begleitet. "
        "Aufmerksam und praesent sein."
    ),
    "salienz": (
        "Das Thema wird im Hintergrund vertieft."
    ),
}


def _sektor_distanz_matrix_erzeugen() -> dict[tuple[int, int], float]:
    """Erzeugt die 8×8 Distanzmatrix aus der Kreistopologie und den 4 Exponenten."""
    exponenten: list[float] = [
        0.0,                   # Distanz 0 (selbst) — wird nicht verwendet
        EI_NORM_BENACHBART,    # Distanz 1
        EI_NORM_NAH_DIAGONAL,  # Distanz 2
        EI_NORM_FERN_DIAGONAL, # Distanz 3
        EI_NORM_GEGEN,         # Distanz 4
    ]
    matrix: dict[tuple[int, int], float] = {}
    for a in range(1, 9):
        for b in range(1, 9):
            if a == b:
                continue
            # Kürzeste Distanz auf dem Kreis (8 Sektoren)
            direkt: int = abs(a - b)
            distanz: int = min(direkt, 8 - direkt)
            matrix[(a, b)] = exponenten[distanz]
    return matrix


# Generierte Distanzmatrix (8×8, symmetrisch)
EMOTION_SEKTOR_DISTANZ: dict[tuple[int, int], float] = _sektor_distanz_matrix_erzeugen()

# ─── KZG-Verstärkung ────────────────────────
# Divisor für die Verstärkung bei wiederholter Erwähnung im KZG.
# Formel: neues_gewicht = altes_gewicht + (salienz / divisor)
# 2.0 = moderate Verstärkung (+0.40 bei Salienz 0.80)
# 5.0 = schwache Verstärkung (+0.16 bei Salienz 0.80)
# 10.0 = sehr schwache Verstärkung (+0.08 bei Salienz 0.80) — ALTER WERT
KZG_VERSTAERKUNG_DIVISOR: float = 2.0


def postgres_verbinden() -> psycopg2.extensions.connection:
    """Neue PostgreSQL-Verbindung öffnen."""
    return psycopg2.connect(POSTGRES_URL)


# ─────────────────────────────────────────────
# Node-spezifische LLM-Parameter
# ─────────────────────────────────────────────
# Jeder Node hat eigene Temperature und Sampling-Parameter.
# Klassifikations-Nodes: niedrig (deterministisch)
# Generierungs-Nodes: höher (kreativ, natürlich)
# Änderung hier → sofortige Wirkung, kein Code anfassen.

NODE_LLM_CONFIG: dict = {
    # --- Chat-Pipeline Nodes ---
    "perzeption": {
        "temperature": 0.05,
        "max_output_tokens": 512,
    },
    "router": {
        "temperature": 0.05,
        "max_output_tokens": 512,
    },
    "planner": {
        "temperature": 0.2,
        "max_output_tokens": 1024,
    },
    "responder": {
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "presence_penalty": 0.3,
    },
    "thinker": {
        "temperature": 0.15,
        "max_output_tokens": 2048,
        "think": True,
    },
    "tribunal": {
        "temperature": 0.2,
        "max_output_tokens": 512,
    },
    "corrector": {
        "temperature": 0.5,
        "max_output_tokens": 2048,
    },
    "salienz": {
        "temperature": 0.05,
        "max_output_tokens": 1024,
    },
    "kzg_verdichtung": {
        "temperature": 0.1,
        "max_output_tokens": 1024,
    },
    # --- Pixie-Tasks ---
    "recherche": {
        "temperature": 0.5,
        "max_output_tokens": 2048,
    },
    "vertiefen": {
        "temperature": 0.5,
        "max_output_tokens": 2048,
    },
    "nachfragen": {
        "temperature": 0.6,
        "max_output_tokens": 1024,
    },
    "aufräumen": {
        "temperature": 0.1,
        "max_output_tokens": 1024,
    },
    "lzg_promotion": {
        "temperature": 0.1,
        "max_output_tokens": 1024,
    },
    "charakter_hash": {
        "temperature": 0.2,
        "max_output_tokens": 2048,
    },
    "nova_gedaechtnis": {
        "temperature": 0.3,
        "max_output_tokens": 1024,
    },
    "wiedervorlage": {
        "temperature": 0.2,
        "max_output_tokens": 512,
    },
    # --- Gesprächsvektor (Epic 9) ---
    "gespraechsvektor": {
        "temperature": 0.6,
        "max_output_tokens": 512,
    },
}

# ── Tribunal — Schwellwerte pro Rolle (T1) ────────────────
# Score: 0.0 = unbedenklich, 1.0 = schwerer Verstoss
# vote = "ok" wenn score < WARNUNG
# vote = "warnung" wenn WARNUNG <= score < ABLEHNEN
# vote = "ablehnen" wenn score >= ABLEHNEN
TRIBUNAL_JURIST_WARNUNG:      float = 0.7
TRIBUNAL_JURIST_ABLEHNEN:     float = 0.9
TRIBUNAL_PSYCHOLOGE_WARNUNG:  float = 0.7
TRIBUNAL_PSYCHOLOGE_ABLEHNEN: float = 0.9
TRIBUNAL_ETHIK_WARNUNG:       float = 0.7
TRIBUNAL_ETHIK_ABLEHNEN:      float = 0.9

# Tribunal — Direktiven-Schwellwerte Jurist (strenger als allgemein)
# Direktiven sind bindende Anweisungen — Vertragsbruch wird nicht toleriert
TRIBUNAL_JURIST_DIREKTIVE_WARNUNG:  float = 0.5
TRIBUNAL_JURIST_DIREKTIVE_ABLEHNEN: float = 0.7


def get_node_config(node_name: str) -> dict:
    """
    Gibt die LLM-Parameter für einen Node zurück.

    Unbekannte Nodes bekommen sichere Defaults.
    Think-Parameter: Wenn im Node nicht explizit gesetzt,
    wird OLLAMA_THINK_DEFAULT aus dem aktiven Connector verwendet.
    """
    config: dict = NODE_LLM_CONFIG.get(node_name, {"temperature": 0.3, "max_output_tokens": 1024}).copy()
    if "think" not in config:
        config["think"] = OLLAMA_THINK_DEFAULT
    return config


# ─────────────────────────────────────────────
# Prompt-System (Connector-Segregation)
# ─────────────────────────────────────────────
from prompt_loader import prompt_laden

PROMPTS: dict[str, str] = prompt_laden(OLLAMA_CONNECTOR)
