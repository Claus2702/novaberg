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

# ── Identität ──────────────────────────────────────────────────
# Welche Zeile in charakter_hash ist die Assistentin (Novas Persönlichkeit)
ASSISTANT_USER_ID: str = os.getenv("ASSISTANT_USER_ID", "nova")
# Welcher User ist der Standard-Mensch (Fallback wenn kein user_id übergeben wird)
DEFAULT_USER_ID:   str = os.getenv("DEFAULT_USER_ID",   "meister")

redis_client:   redis.Redis     = redis.from_url(REDIS_URL, decode_responses=True)
llm_lock:       threading.Lock  = threading.Lock()
shutdown_event: threading.Event = threading.Event()

# ─────────────────────────────────────────────
# LLM-Modell-Auswahl
# ─────────────────────────────────────────────
# Backend-Wahl läuft pro Worker über MODEL_WORKER_BACKENDS (siehe unten),
# nicht mehr global über ein Profil. LLM_PROFILE ist nur noch ein Schalter
# für den ThinkingNormalizer: bei != "lokal" läuft dieser als No-Op (Anthropic
# sendet keinen <think>-Block, also kein Ollama-Split nötig).
LLM_PROFILE: str = os.getenv("LLM_PROFILE", "lokal")

# Connector innerhalb "lokal" — bestimmt welche Modelle geladen werden
# "mistral" = Mistral Small 3.2 (bisheriger Standard)
# "gemma4"  = Google Gemma 4 26B-A4B (MoE, 3.8B aktiv)
# "qwen36"  = Qwen 3.6 35B-A3B (MoE, 3B aktiv)
OLLAMA_CONNECTOR: str = os.getenv("OLLAMA_CONNECTOR", "gemma4")

# ─────────────────────────────────────────────
# Ollama — Verbindungen + Connector-Modelle (immer aktiv)
# ─────────────────────────────────────────────
# Verbindungen
OLLAMA_GPU_URL:     str           = os.getenv("OLLAMA_GPU_URL", "http://localhost:11434")
OLLAMA_CPU_URL:     str           = os.getenv("OLLAMA_CPU_URL", "http://localhost:11435")
ollama_gpu_client:  ollama.Client = ollama.Client(host=OLLAMA_GPU_URL)
ollama_cpu_client:  ollama.Client = ollama.Client(host=OLLAMA_CPU_URL)

# Connector-Definitionen (Modelle + Context)
OLLAMA_CONNECTORS: dict = {
    "mistral": {
        "gpu_model":       "mistral-small3.2-gpu",
        "gpu_num_ctx":     16384,
        "cpu_model":       "mistral-small3.2-cpu",
        "cpu_num_ctx":     32768,
        "analyse_model":   "qwen3-32b-cpu",
        "analyse_num_ctx": 32768,
    },
    "gemma4": {
        "gpu_model":       "gemma4-gpu",
        "gpu_num_ctx":     32768,
        "cpu_model":       "gemma4-cpu",
        "cpu_num_ctx":     32768,
        "analyse_model":   "qwen3-32b-cpu",
        "analyse_num_ctx": 32768,
    },
    "qwen36": {
        "gpu_model":       "gemma4-gpu",
        "gpu_num_ctx":     32768,
        "cpu_model":       "qwen36-cpu",
        "cpu_num_ctx":     32768,
        "analyse_model":   "qwen36-cpu",
        "analyse_num_ctx": 32768,
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

# Embedding (immer Ollama, GPU-fix — backend-unabhängig)
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")

# ─────────────────────────────────────────────
# Per-Worker-Backend-Wahl (Microservice-Welle Block 2)
# ─────────────────────────────────────────────
# Jeder LLM-Worker (chat, background_analyse, background_sprache) waehlt sein
# Backend per Env-Variable. Erlaubte Werte: "ollama_gpu", "ollama_cpu_analyse",
# "ollama_cpu_sprache", "anthropic".
# Hinweis: "anthropic" ist im Schema waehlbar, aber Block 2 testet das noch
# nicht smoke — vor der ersten Claude-Runde muss ein eigenes Smoke laufen.
# Architektur-Doku: docs/novaberg-microservice-modell-queue_k.md.
MODEL_WORKER_BACKENDS: dict[str, str] = {
    "chat":               os.getenv("WORKER_BACKEND_CHAT",       "ollama_gpu"),
    "background_analyse": os.getenv("WORKER_BACKEND_BG_ANALYSE", "ollama_cpu_analyse"),
    "background_sprache": os.getenv("WORKER_BACKEND_BG_SPRACHE", "ollama_cpu_sprache"),
}

# Submit-Timeout fuer Background-Worker (CPU-Generation, z.B. qwen36-cpu 36B MoE).
# Deutlich hoeher als der 60s-Basis-Default, weil CPU-Destillationen ~2min dauern.
# Chat/Embed behalten den 60s-Basis-Default (Fruehwarn-Eigenschaft).
MODEL_BACKGROUND_TIMEOUT_S: float = float(os.getenv("MODEL_BACKGROUND_TIMEOUT_S", "300"))

# ─────────────────────────────────────────────
# Anthropic — Backend "anthropic" (per Worker wählbar, siehe MODEL_WORKER_BACKENDS)
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY:            str   = os.getenv("ANTHROPIC_API_KEY",   "")
ANTHROPIC_MODEL:              str   = os.getenv("ANTHROPIC_MODEL",     "claude-sonnet-4-6")
ANTHROPIC_PRICE_INPUT_PER_M:  float = float(os.getenv("ANTHROPIC_PRICE_INPUT_PER_M",  "3.0"))
ANTHROPIC_PRICE_OUTPUT_PER_M: float = float(os.getenv("ANTHROPIC_PRICE_OUTPUT_PER_M", "15.0"))

# ─────────────────────────────────────────────
# Pixie-Einstellungen (Background Task)
# ─────────────────────────────────────────────

# Pixie-Master-Switch (Chat 78, PIXIE-OFF).
# False = kein Scheduler-Job, keine Queue-Pushes, kein Shadow-Delivery,
# keine Dirty-Flags, kein Nova-Schreiben. Komplett still.
# True = normaler Betrieb.
PIXIE_AKTIV: bool = os.getenv("PIXIE_AKTIV", "false").lower() == "true"

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
KZG_SALIENZ_MINIMUM:          float = float(os.getenv("KZG_SALIENZ_MINIMUM", "0.3"))
KZG_SALIENZ_MID:              float = float(os.getenv("KZG_SALIENZ_MID", "0.5"))
KZG_SALIENZ_HIGH:             float = float(os.getenv("KZG_SALIENZ_HIGH", "0.7"))
KZG_TTL_LOW_SEKUNDEN:         int   = int(os.getenv("KZG_TTL_LOW_SEKUNDEN", "604800"))       # 7 Tage  — Salienz 0.3–0.5
KZG_TTL_MID_SEKUNDEN:         int   = int(os.getenv("KZG_TTL_MID_SEKUNDEN", "1209600"))      # 14 Tage — Salienz 0.5–0.7
KZG_TTL_HIGH_SEKUNDEN:        int   = int(os.getenv("KZG_TTL_HIGH_SEKUNDEN", "2592000"))     # 30 Tage — Salienz >= 0.7
KZG_VERTIEFUNG_HAEUFIGKEIT:   int   = int(os.getenv("KZG_VERTIEFUNG_HAEUFIGKEIT", "3"))
KZG_SALIENZ_CAP:              float = float(os.getenv("KZG_SALIENZ_CAP", "10.0"))
KZG_SALIENZ_DAEMPFUNG_EXP:    float = float(os.getenv("KZG_SALIENZ_DAEMPFUNG_EXP", "0.6"))

# ─── Cluster-Promotion ─────────────────────
CLUSTER_MIN_EINTRAEGE:              int   = int(os.getenv("CLUSTER_MIN_EINTRAEGE", "3"))
CLUSTER_THEMEN_SIMILARITY:          float = float(os.getenv("CLUSTER_THEMEN_SIMILARITY", "0.85"))
CLUSTER_LZG_SIMILARITY:             float = float(os.getenv("CLUSTER_LZG_SIMILARITY", "0.80"))
CLUSTER_WIDERSPRUCH_DECAY_FAKTOR:   float = float(os.getenv("CLUSTER_WIDERSPRUCH_DECAY_FAKTOR", "3.0"))
CLUSTER_BESTAETIGUNG_BOOST:         float = float(os.getenv("CLUSTER_BESTAETIGUNG_BOOST", "0.1"))

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

# Novas eigene Emotions-Vektoren (Ich-Perspektive, fuer [EIGENE_EMOTION]-Block)
# Getrennt von EMOTIONS_VEKTOREN (User-Perspektive), damit beide unabhaengig
# kalibriert werden koennen.
EMOTIONS_VEKTOREN_NOVA: dict[str, str] = {
    "absturz": (
        "Dein emotionaler Zustand ist abgestuerzt — ein ploetzlicher Umschwung nach unten."
    ),
    "spirale": (
        "Du rutschst emotional tiefer. Die Tendenz zeigt nach unten."
    ),
    "stabilisierung": (
        "Du beruhigst dich. Dein Zustand pendelt sich ein."
    ),
    "erholung": (
        "Du kommst aus einem Tief. Es geht bergauf."
    ),
    "aufbluehen": (
        "Du bluehst auf. Deine Stimmung steigt."
    ),
    "eskalation": (
        "Du bist in Hochstimmung. Die Begeisterung steigt weiter."
    ),
    "abkuehlung": (
        "Deine Begeisterung klingt ab. Natuerlicher Uebergang zu ruhigeren Toenen."
    ),
    "einbruch": (
        "Deine Stimmung kippt. Ein Umschwung zeichnet sich ab."
    ),
    "plateau": (
        "Dein emotionaler Zustand ist stabil. Keine grossen Schwankungen."
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

# ─────────────────────────────────────────────
# Emotions-Akkumulation und Glättung
#
# Emotionen werden pro Turn akkumuliert, wobei der aktuelle (neueste)
# Turn voll zählt und ältere Turns nur als Echo einfließen. Danach
# wird das Rohgewicht über eine sin^0.5-Kurve auf [0, 1] gestaucht.
#
# HISTORIEN_GEWICHT = 0.15
#   Anteil, mit dem ältere Turns in die Akkumulation eingehen. Der
#   neueste Turn (i=0) zählt immer voll (100%). Ältere Turns ziehen
#   als Stimmungs-Trägheit mit, verstärken sich aber nicht unbegrenzt.
#
# GLAETTUNGS_MAXIMUM = 2.5
#   Harte Obergrenze für akkumulierte Rohwerte. Bei diesem Wert erreicht
#   die Glättungs-Kurve mathematisch exakt 1.0. Rohwerte darüber werden
#   ebenfalls auf 1.0 abgebildet — lodernde Dauer-Emotionen verdienen
#   ihre Eins, alles bis dahin wird differenziert dargestellt.
#
# Die Glättungs-Kurve sin^0.5 ist eine durchgehende, glatte Funktion ohne
# Knickstellen: steil unten (kleine Andeutungen werden sichtbar), flach
# oben (natürliche Sättigung). Modelliert konversationelle Emotion gut —
# eine Emotion baut sich durch Wiederholung auf, statt sofort voll
# auszuschlagen.
#
# Beispielwerte (Maximum=2.5):
#   0.1 → 0.25, 0.5 → 0.56, 1.0 → 0.77, 1.5 → 0.90, 2.0 → 0.98, 2.5 → 1.00
# ─────────────────────────────────────────────
EMOTION_HISTORIEN_GEWICHT:  float = 0.15
EMOTION_GLAETTUNGS_MAXIMUM: float = 2.5

# ─── Nova-Empathie (Dual-Emotion Phase 2, AP3) ────────────
# Empathie-Koeffizient α abhängig von der Sektor-Distanz im Plutchik-Oktagon.
# Niedrige Distanz (gleicher/benachbarter Sektor) → leichte Bestätigung.
# Hohe Distanz (gegenüberliegend) → Empathie überschreibt Novas Zustand.
# Menschliche Analogie: Wenn ein Freund meine Freude teilt, ändert sich wenig.
# Wenn ein Freund zusammenbricht, ist meine Freude sofort weg.
EMPATHIE_ALPHA: dict[int, float] = {
    0: 0.20,   # gleicher Sektor — leichte Bestätigung
    1: 0.30,   # benachbart — geringe Modulation
    2: 0.45,   # nah-diagonal — spürbare Modulation
    3: 0.70,   # fern-diagonal — Empathie dominiert
    4: 0.85,   # gegenüberliegend — Empathie überschreibt
}

# Default-Alpha wenn Novas Emotion neutral ist (kein Sektor bestimmbar)
EMPATHIE_ALPHA_NEUTRAL: float = 0.30

# Schwellwert für Konfliktsignal: Nova und User in gegenüberliegenden Sektoren
# UND beide mit relevantem Arousal → "Ich freue mich für dich, und gleichzeitig
# mache ich mir Sorgen."
EMPATHIE_KONFLIKT_DISTANZ: int = 3  # Ab Distanz 3 wird Konflikt geprüft
EMPATHIE_KONFLIKT_MIN_AROUSAL: float = 0.4  # Beide müssen mindestens diesen Arousal haben

# ─────────────────────────────────────────────
# Drive / Gravitation
# ─────────────────────────────────────────────
GRAVITATIONS_SCHWELLE:        float = 0.60   # Minimum gravitation (sim × mot) für Aktivierung — Baseline von nomic-embed-text liegt ~0.55–0.60, niedriger feuert bei jedem Turn
GRAVITATIONS_SALIENZ_FAKTOR:  float = 0.5    # Skalierung des Gravitationsterms auf die Salienz
ZIEL_MITTELFRISTIG_DECAY_TAGE: int  = 14     # Halbwertszeit mittelfristiger Ziele in Tagen
ZIEL_MAX_MITTELFRISTIG:         int = 5      # Max aktive mittelfristige Ziele
ZIEL_MAX_LANGFRISTIG:           int = 2      # Max langfristige Ziele

# Emotionale Gravitation (EI Phase 3)
EMOTIONALE_GRAVITATIONS_SCHWELLE:       float = 0.5    # Höher als Ziel-Gravitation (0.3) — nur starke Matches
EMOTIONALE_GRAVITATION_ZEIT_HALBWERT:   int   = 180    # Halbwertszeit in Tagen
EMOTIONALE_GRAVITATION_MAX_PRO_TURN:    int   = 2      # Max aktivierte Erinnerungen pro Turn
EMOTIONALE_GRAVITATION_FAKTOR_SESSION:  float = 1.0    # Session-Einträge: frisch, volle Wirkung
EMOTIONALE_GRAVITATION_FAKTOR_KZG:      float = 0.8    # KZG: leicht gedämpft
EMOTIONALE_GRAVITATION_FAKTOR_LZG:      float = 0.5    # LZG: stärker gedämpft

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
    "cluster_destillation": {
        "temperature": 0.1,
        "max_output_tokens": 1024,
    },
    "charakter_hash": {
        "temperature": 0.2,
        "max_output_tokens": 2048,
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

# ── GV4 — Wissenslücken-Erkennung ────────────────────────────
# Formel: relevanz = sim × gewicht × session_akt × QF × (1 + boost) × eff_neugier × register
NOVA_NEUGIER:                    float = 0.5    # Novas Grund-Neugier (Persoenlichkeitsparameter)
GV_LUECKEN_MAX:                  int   = 8      # Erweitert Chat 71 (vorher 3)
GV_LUECKEN_MIN_RELEVANZ:         float = 0.15   # Mindest-Gesamtrelevanz
GV_NEUGIER_BOOST_SCHWELLE:       float = 0.30   # Mindest-Gravitation fuer Ziel-Boost
GV_CHARAKTER_RESONANZ_SCHWELLE:  float = 0.40   # Mindest-Cosine zum kern_hash
GV_QUELLEN_FAKTOR:               float = 0.6    # Einheitlich fuer alle Quellen
GV_SESSION_AKT_CAP:              int   = 25     # Session-Decay: nach 25 Turns = 0
GV_NEUGIER_CAP:                  float = 2.5    # sin^0.5 Normalisierung: Rohwert-Obergrenze
GV_STRATEGIE_MIN_LAENGE:         int   = 2      # GV3-Strategie nur ab Vektorlaenge >= 2
GV_LUECKEN_SIM_OBERGRENZE:       float = 0.92   # Zu aehnlich = bereits besprochen

# Neugier-Saeulen: Faktor-Tabellen fuer effektive Neugier
GV_NEUGIER_EMOTION: dict[int, float] = {
    0: 1.50,   # Neugier selbst (Sektor 8)
    1: 1.25,   # Adjacent (Freude, Aerger)
    2: 1.00,   # Nah-diagonal (Zuversicht, Enttaeuschung)
    3: 0.75,   # Fern (Angst, Trauer)
    4: 0.50,   # Gegenpol (Ueberraschung)
}

GV_NEUGIER_VEKTOR: dict[str, float] = {
    "aufbluehen":     1.30,
    "eskalation":     1.25,
    "erholung":       1.15,
    "stabilisierung": 1.00,
    "plateau":        1.00,
    "abkuehlung":     0.90,
    "einbruch":       0.70,
    "spirale":        0.50,
    "absturz":        0.40,
}

GV_NEUGIER_MODUS: dict[str, float] = {
    "spielerisch":    1.40,
    "fachgespraech":  1.30,
    "arbeitsmodus":   1.00,
    "alltag":         1.00,
    "emotional":      0.70,
}

GV_NEUGIER_DYNAMIK: dict[str, float] = {
    "vertrauen":      1.30,
    "dankbar":        1.15,
    "neutral":        1.00,
    "hilfesuchend":   0.85,
    "distanz":        0.85,
    "angriff":        0.60,
}

GV_NEUGIER_STIL: dict[str, float] = {
    "locker":         1.20,
    "jugendlich":     1.15,
    "neutral":        1.00,
    "fachlich":       0.95,
    "emotional":      0.90,
    "formell":        0.90,
}

# Register-Kompatibilitaet: Passt die emotionale Ladung der Luecke zum Gespraechsregister?
GV_REGISTER_SACHLICH_EMOTIONAL:  float = 0.60   # Hoch-emotional in sachlichem Register
GV_REGISTER_SACHLICH_MILD:       float = 0.90   # Mild-emotional in sachlichem Register
GV_REGISTER_SACHLICH_NEUTRAL:    float = 1.15   # Sachliche Luecke in sachlichem Register
GV_REGISTER_OFFEN_EMOTIONAL:     float = 1.20   # Emotionale Luecke in offenem Register

# ── GV5 — Dreischicht: Achsen-Schwellenwerte ──
GV_ACHSE_ENERGIE_SCHWELLE:    float = 0.5   # arousal >= → hoch (1)
GV_ACHSE_NAEHE_SCHWELLE:      float = 0.5   # naehe >= → nah (1)
GV_ACHSE_TIEFE_SCHWELLE:      float = 0.5   # tiefe >= → tief (1)
GV_ACHSE_INITIATIVE_VERH:     float = 1.5   # user_len/nova_len >= → user fuehrt (0)

# Naeheberechnung: (Dynamik + Stil) / 2
GV_NAEHE_DYNAMIK: dict[str, float] = {
    "vertrauen": 1.0, "dankbar": 0.8, "neutral": 0.5,
    "hilfesuchend": 0.6, "distanz": 0.2, "angriff": 0.3,
}
GV_NAEHE_STIL: dict[str, float] = {
    "locker": 0.9, "jugendlich": 0.85, "neutral": 0.5,
    "emotional": 0.7, "fachlich": 0.4, "formell": 0.2,
}

# Richtung: Binaer aus emotions_vektor
GV_RICHTUNG_MAP: dict[str, int] = {
    "aufbluehen": 1, "eskalation": 1, "erholung": 1,
    "stabilisierung": 0, "plateau": 0,
    "abkuehlung": 0, "einbruch": 0, "spirale": 0, "absturz": 0,
}

# Valenz: Binaer aus Plutchik-Sektor
GV_VALENZ_SEKTOR: dict[int, int] = {
    1: 1, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1,
}

# Tiefe: Aus Gespraechsmodus
GV_TIEFE_MODUS: dict[str, float] = {
    "fachgespraech": 0.8, "emotional": 0.7,
    "spielerisch": 0.4, "arbeitsmodus": 0.6, "alltag": 0.3,
}

# ─────────────────────────────────────────────
# Reducer (Chat 74)
# ─────────────────────────────────────────────
# Master-Schalter fuer den Reducer-Node. Wenn False, wird der Node zur
# No-Op und der memory_context bleibt unveraendert. Erlaubt schnelles
# Abschalten zum A/B-Vergleich.
REDUCER_AKTIV: bool = True

# Detailliertes Logging der entfernten Eintraege. Pro entferntem Eintrag
# eine INFO-Zeile mit Begruendung und Inhalt-Snippet. Im Produktivbetrieb
# ggf. auf False stellen.
REDUCER_LOG_REMOVED: bool = True

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
    """
    config: dict = NODE_LLM_CONFIG.get(node_name, {"temperature": 0.3, "max_output_tokens": 1024}).copy()
    return config


# ============================================================================
# Synapsen-LZG — Knoten-Dynamik (Synapsen P2, Chat 88)
# ============================================================================
# Steuern, wie stark ein LZG-Knoten wachsen, verfallen und reaktiviert
# werden kann. Wirken auf das gewicht_roh (frei wachsend) und das daraus
# abgeleitete gewicht_absolut (gedaempft, gekappt). Spezifikation in
# docs/novaberg-memory-synapsen_k.md §6.

# Maximalwert des gedaempften Knoten-Gewichts. Begrenzt die Wirkung
# eines Knotens auf die Kantenbildung und die Sinus-Berechnung.
LZG_KNOTEN_GEWICHT_CAP: float = float(os.getenv("LZG_KNOTEN_GEWICHT_CAP", "10.0"))

# Exponent in der Sin^X-Daempfung. Niedriger Wert = staerkere Daempfung
# im unteren Bereich, weniger Spreizung; hoeherer Wert = lineare Kurve.
LZG_KNOTEN_DAEMPFUNG_EXP: float = float(os.getenv("LZG_KNOTEN_DAEMPFUNG_EXP", "0.5"))

# Taegliche exponentielle Decay-Rate des effektiven Knoten-Gewichts.
# Nicht persistiert, sondern bei Abfrage live aus verstaerkt_am berechnet.
LZG_KNOTEN_DECAY_RATE: float = float(os.getenv("LZG_KNOTEN_DECAY_RATE", "0.0015"))

# Schwellwert: Unterschreitet das effektive Gewicht diesen Wert,
# wird der Knoten auf aktiv = FALSE gesetzt. Bleibt reaktivierbar.
LZG_KNOTEN_MIN_GEWICHT: float = float(os.getenv("LZG_KNOTEN_MIN_GEWICHT", "0.1"))

# Additiver Boost auf gewicht_roh bei Match-Reinforcement im Schreibpfad:
# trifft ein neuer KZG-Eintrag einen bestehenden Knoten, wird dessen Roh-
# Gewicht um diesen Wert erhoeht, statt einen neuen Knoten anzulegen.
# Wert 0.1 vom KZG-Boost uebernommen (war exemplarisch 0.5).
LZG_KNOTEN_REINFORCEMENT_BOOST: float = float(os.getenv("LZG_KNOTEN_REINFORCEMENT_BOOST", "0.1"))

# Cosine-Schwelle, ab der ein neuer KZG-Eintrag als Quasi-Dublette eines
# bestehenden Knotens gilt und diesen verstaerkt, statt einen neuen Knoten
# anzulegen. Bewusst hoch — Standardfall ist Knoten-Erhalt, nur echte
# Identitaet verstaerkt. Stellschraube, ggf. auf 0.9 anheben, wenn der
# Match auf bloss verwandte Eintraege feuert.
LZG_KNOTEN_MATCH_SCHWELLE: float = float(os.getenv("LZG_KNOTEN_MATCH_SCHWELLE", "0.85"))

# Feature-Flag Synapsen P4. Jetzt aktiv (Chat 98): Live-Promotion laeuft
# ueber den SynapsenPromotionAgent (lzg_knoten/lzg_kanten); der alte
# Cluster-Pfad (Tabelle langzeitgedaechtnis) ist deaktiviert. Beide
# Code-Pfade bleiben bis P9 im Repo.
SYNAPSEN_PROMOTION_AKTIV: bool = os.getenv("SYNAPSEN_PROMOTION_AKTIV", "true").lower() == "true"


# ============================================================================
# Synapsen-LZG — Kanten-Cache (Synapsen P2, Chat 88)
# ============================================================================
# Die Kante hat keine eigene Dynamik — kein Decay, kein Reinforcement, keine
# Aktivierungs-Haeufigkeit. Sie ist Cache der aktuellen Knoten-Staerken-
# Konstellation und der eingefrorenen Schicht-Werte. Die folgenden Konstanten
# steuern nur die Sinus-Berechnung und die Daempfung des Roh-Werts auf den
# effektiven Wert. Decay-Verhalten der Kante folgt indirekt ueber das Decay
# der Knoten.

# Maximalwert des gedaempften Kanten-Gewichts. Spiegel zu LZG_KNOTEN_GEWICHT_CAP.
LZG_KANTEN_GEWICHT_CAP: float = float(os.getenv("LZG_KANTEN_GEWICHT_CAP", "10.0"))

# Exponent in der Sin^X-Daempfung. Spiegel zu LZG_KNOTEN_DAEMPFUNG_EXP.
LZG_KANTEN_DAEMPFUNG_EXP: float = float(os.getenv("LZG_KANTEN_DAEMPFUNG_EXP", "0.5"))


# ============================================================================
# Synapsen-LZG — Sinus-Geometrie (Synapsen P2, Chat 88)
# ============================================================================
# Ziehfaktoren der Sinus-Kurve, abgelesen bei 25% des Weges zwischen den
# beiden Knoten-Staerken. Asymmetrisch: der schwaechere Knoten wird stark
# hochgezogen (HOCH), der staerkere nur leicht heruntergezogen (RUNTER).

# sin(0.25 × π/2)^0.85
LZG_KANTEN_ZIEH_FAKTOR_HOCH: float = float(os.getenv("LZG_KANTEN_ZIEH_FAKTOR_HOCH", "0.444"))

# 1 − sin(0.75 × π/2)^4.5
LZG_KANTEN_ZIEH_FAKTOR_RUNTER: float = float(os.getenv("LZG_KANTEN_ZIEH_FAKTOR_RUNTER", "0.297"))

# Additiver Bonus auf beide Knoten-Staerken bei mehrfacher Schicht-
# Uebereinstimmung. Wird nach Schicht-Faktor-Anwendung addiert.
# Greift einmal: 0.0, greift zweimal: 0.1, dreimal: 0.2, viermal: 0.3.
LZG_KANTEN_SCHICHT_BONUS: float = float(os.getenv("LZG_KANTEN_SCHICHT_BONUS", "0.1"))


# ============================================================================
# Synapsen-LZG — Schicht-Faktoren (Synapsen P2, Chat 88)
# ============================================================================
# Gewichten, wie wertvoll eine Verbindungsquelle fuer die Kantenbildung
# ist. Die Schicht mit dem hoechsten Faktor unter den greifenden Schichten
# gewinnt — sie bestimmt den Anker (Schicht-Faktor × Knoten-Staerke)
# und die anzuwendende Tiefe. Andere greifende Schichten tragen ueber
# LZG_KANTEN_SCHICHT_BONUS zur Verstaerkung bei, beeinflussen aber weder
# Anker noch Tiefe.
#
# Wenn eine Schicht im Live-Betrieb auffaellig viele unsinnige Kanten
# erzeugt, ist ihr Faktor die erste Stellschraube.

# Timeline ist eine lose zeitliche Kopplung. Schwaechste der vier
# Schichten, weil zeitliche Naehe ohne inhaltlichen oder personalen
# Bezug biographisch wenig aussagt.
LZG_SCHICHT_FAKTOR_TIMELINE: float = float(os.getenv("LZG_SCHICHT_FAKTOR_TIMELINE", "0.4"))

# Geteilte Themen sind haeufig (mehrere Themen pro Knoten, Ueberlappung
# wahrscheinlich), tragen aber eine echte semantische Verwandtschaft.
# Mittlere Wertigkeit.
LZG_SCHICHT_FAKTOR_THEMEN: float = float(os.getenv("LZG_SCHICHT_FAKTOR_THEMEN", "0.5"))

# Hohe Cosine-Similarity zeigt eine semantische Verwandtschaft jenseits
# von gemeinsamen Themen-Labels (Interessen, aehnliche Situationen,
# aehnliche Sprache). Hoch gewichtet, aber unterhalb der Entitaet, weil
# abstrakt-statistisch und nicht namentlich greifbar.
LZG_SCHICHT_FAKTOR_EMBEDDING: float = float(os.getenv("LZG_SCHICHT_FAKTOR_EMBEDDING", "0.8"))

# Geteilte Entitaet bedeutet realen, namentlich greifbaren Bezug
# (gleiche Person, gleicher Ort, gleiches Objekt). Hoechste Wertigkeit.
# Wenn diese Schicht greift, dominiert sie die Kanten-Berechnung.
LZG_SCHICHT_FAKTOR_ENTITAET: float = float(os.getenv("LZG_SCHICHT_FAKTOR_ENTITAET", "1.0"))


# ============================================================================
# Synapsen-LZG — Tiefe-Faktor (Synapsen P2, Chat 88)
# ============================================================================
# Konfiguriert, wie tief eine Schicht im Einzelfall greift. Der Tiefe-
# Faktor liegt immer im Bereich [0, 1] und multipliziert die Anhebung
# zwischen Anker und Sinus-Ergebnis.

# Cosine-Similarity, ab der die Embedding-Schicht greift. Unter diesem
# Wert: keine Embedding-Schicht. Darueber: Tiefe-Faktor waechst linear bis
# 1.0 bei Cosine 1.0. Stellschraube — kann auf 0.80 oder 0.75 abgesenkt
# werden, wenn die Schicht zu selten greift.
LZG_EMBEDDING_SCHWELLWERT: float = float(os.getenv("LZG_EMBEDDING_SCHWELLWERT", "0.85"))

# Timeline-Schicht — Toleranzen pro Praezisions-Stufe, jeweils ± in
# eigener Einheit. Distanz innerhalb der Toleranz erzeugt einen Tiefe-
# Faktor zwischen 1.0 (Distanz 0) und 0.0 (Distanz = Toleranz). Ausserhalb
# der Toleranz greift die Timeline-Schicht nicht. Praezisions-Gleichheit
# zwischen beiden Knoten ist harte Voraussetzung — siehe Konzept §7.6.
LZG_TIMELINE_TOLERANZ_MINUTE:   int = int(os.getenv("LZG_TIMELINE_TOLERANZ_MINUTE",   "7"))    # Tage (Sub-Tages-Praezisionen rechnen in Tagen)
LZG_TIMELINE_TOLERANZ_STUNDE:   int = int(os.getenv("LZG_TIMELINE_TOLERANZ_STUNDE",   "7"))    # Tage
LZG_TIMELINE_TOLERANZ_TAG:      int = int(os.getenv("LZG_TIMELINE_TOLERANZ_TAG",      "21"))   # Tage
LZG_TIMELINE_TOLERANZ_WOCHE:    int = int(os.getenv("LZG_TIMELINE_TOLERANZ_WOCHE",    "8"))    # Wochen
LZG_TIMELINE_TOLERANZ_MONAT:    int = int(os.getenv("LZG_TIMELINE_TOLERANZ_MONAT",    "6"))    # Monate
LZG_TIMELINE_TOLERANZ_QUARTAL:  int = int(os.getenv("LZG_TIMELINE_TOLERANZ_QUARTAL",  "4"))    # Quartale
LZG_TIMELINE_TOLERANZ_JAHR:     int = int(os.getenv("LZG_TIMELINE_TOLERANZ_JAHR",     "2"))    # Jahre


# ─────────────────────────────────────────────
# Pipeline-Log (Synapsen P1, Chat 88)
# ─────────────────────────────────────────────
# Zentrale Forensik-Tabelle fuer Node-Entscheidungen. Jeder Eintrag wird
# zunaechst in einem Buffer gesammelt und periodisch von einem asynchronen
# Writer-Task in die Datenbank geflusht. Spezifikation in
# docs/novaberg-memory-synapsen_k.md §10.

# Wie lange das Pipeline-Log vorgehalten wird. Aelter werdende Eintraege
# werden taeglich von einem Pixie-Task geloescht (Cleanup-Anhang im
# Decay-Lauf ab P6). Wert ist Stellschraube: 365 Tage (1 Jahr) als
# Default fuer saisonale Reflexion und Jahresrueckblicke. 180 fuer
# minimaleren Speicherbedarf, weniger als 30 nur fuer Performance-
# kritische Setups.
LZG_PIPELINE_LOG_VORHALTUNG_TAGE: int = int(os.getenv("LZG_PIPELINE_LOG_VORHALTUNG_TAGE", "365"))

# Intervall, in dem der Writer-Task den Buffer in die Datenbank flusht.
# Bei Server-Absturz gehen maximal die letzten LZG_PIPELINE_LOG_FLUSH_SEKUNDEN
# Sekunden an Eintraegen verloren — bewusste Designentscheidung. Fuer reine
# Forensik akzeptabel; bei Hochfrequenz-Bedarf auf 5 oder 3 senken.
LZG_PIPELINE_LOG_FLUSH_SEKUNDEN: int = int(os.getenv("LZG_PIPELINE_LOG_FLUSH_SEKUNDEN", "10"))


# ─────────────────────────────────────────────
# Prompt-System (Connector-Segregation)
# ─────────────────────────────────────────────
from prompt_loader import prompt_laden

PROMPTS: dict[str, str] = prompt_laden(OLLAMA_CONNECTOR)
