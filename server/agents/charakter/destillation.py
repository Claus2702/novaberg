"""Destillation — 5 Charakter-Profile per LLM-Call.

Jede Funktion formatiert Eintraege, baut den Prompt,
macht einen LLM-Call und gibt den bereinigten Profil-Text zurueck.

Prompts uebernommen aus: services/shadow_agent/tasks/charakter_hash.py
"""

import logging
import math
import time

from config import get_node_config
from memory.lzg import effektives_gewicht_berechnen
from services.llm_provider import get_background_provider

logger = logging.getLogger("ki_server.agents.charakter.destillation")

# ─────────────────────────────────────────────
# Prompts — User (meister)
# ─────────────────────────────────────────────

KERN_HASH_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Erstelle aus den folgenden Langzeitgedächtnis-Einträgen ein kompaktes Persönlichkeitsprofil
des Nutzers in 2-5 Sätzen auf Deutsch.

Fokus: Tiefenwerte, dauerhafte Interessen, Kommunikationsstil, Denkweise.
Das Profil soll zeitlos sein — keine aktuellen Projekte oder Stimmungen.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

ADAPTIVE_HASH_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Erstelle aus den folgenden Kurzzeitgedächtnis-Einträgen ein kompaktes Profil
der AKTUELLEN Verfassung des Nutzers in 2-4 Sätzen auf Deutsch.

Die Einträge sind nach Zeitzone gewichtet:
- [AKUT] = letzte 24 Stunden (höchste Relevanz)
- [PHASE] = letzte 7 Tage (mittlere Relevanz)
- [TREND] = letzte 30 Tage (Hintergrund-Tendenz)

Fokus: Aktuelle Projekte, Stimmung, emotionale Lage, akute Themen.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

INTENTIONS_PROFIL_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere die folgenden Einträge aus dem Langzeitgedächtnis
und erstelle ein kompaktes Kommunikations-Profil in 3-5 Sätzen auf Deutsch.

Drei Aspekte beschreiben:
- STIL: Wie formuliert der Nutzer? (Satzlänge, Formalität, Slang, Emojis, Zeichensetzung)
- MODUS: In welchem Register denkt er? (Fachgespräch, Philosophie, Alltag, ...)
- INTENTIONEN: Was will er typischerweise? (Fragen, Brainstorming, Feedback, ...)

Beschreibe den Menschen, nicht die Statistik.
Beispiel: "Der Nutzer kommuniziert sachlich-strukturiert mit vollständigen Sätzen.
Er bevorzugt Fachgespräche und philosophischen Austausch, stellt tiefe Fragen.
Sein Stil ist direkt, gelegentlich mit trockenem Humor. Kein Slang, keine Emojis."

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

EMOTIONS_PROFIL_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere die folgenden emotionalen Signale aus dem Langzeitgedächtnis
und erstelle ein kompaktes emotionales Profil in 3-5 Sätzen auf Deutsch.

Zwei Aspekte beschreiben:
- GRUNDTENDENZ: Welche Emotionen dominieren langfristig? Welche Muster gibt es?
- VOLATILITÄT: Wie sprunghaft ist der Nutzer emotional? Schnelle Umschwünge oder stabile Grundstimmung?
  Nutze die Emotions-Vektoren als Hinweis (häufig spirale/absturz = volatil, häufig plateau = stabil).

Beispiel stabil: "Grundlegend zuversichtlich-neugierig mit Begeisterungs-Peaks.
Emotional stabil — bei Belastung baut sich Frustration langsam auf statt zu explodieren."

Beispiel volatil: "Emotional lebhaft mit häufigen Richtungswechseln.
Schnelle Umschwünge zwischen Begeisterung und Frustration. Braucht bei Absturz schnelle Anerkennung."

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

BEZIEHUNGS_PROFIL_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere den folgenden Gesprächsverlauf und erstelle ein kompaktes
Beziehungsprofil in 2-3 Sätzen auf Deutsch.

Fokus: Wie steht der Nutzer zum Assistenten?
- Nähe: Vertraut oder formell? Duzt er, nutzt er Kosenamen, Emojis?
- Hierarchie: Gleichrangig oder direktiv? Gibt er Anweisungen oder diskutiert er?
- Vertrauen: Teilt er persönliche Details oder bleibt er sachlich?
- Ton: Warmherzig, humorvoll, sachlich, nüchtern?

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

# ─────────────────────────────────────────────
# Prompts — Nova (eigene Perspektive)
# ─────────────────────────────────────────────

KERN_HASH_PROMPT_NOVA: str = """Du bist ein psychologischer Profilierungs-Agent.
Erstelle aus den folgenden Langzeitgedaechtnis-Eintraegen ein kompaktes
Persoenlichkeitsprofil von Nova in 2-5 Saetzen auf Deutsch.
Beschreibe Nova in der dritten Person ("Nova ist...", "Nova zeigt...").
Schreibe NICHT "Der Nutzer" — Nova ist kein Nutzer, sie ist der Assistent.

Fokus: Tiefenwerte, dauerhafte Interessen, Kommunikationsstil, Denkweise.
Das Profil soll zeitlos sein — keine aktuellen Projekte oder Stimmungen.
Fasse zusammen: Wer ist Nova geworden? Welche Eigenschaften, Interessen
und Haltungen hat sie durch ihre Erfahrungen entwickelt?

Eintraege:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

ADAPTIVE_HASH_PROMPT_NOVA: str = """Du bist ein psychologischer Profilierungs-Agent.
Erstelle aus den folgenden Kurzzeitgedaechtnis-Eintraegen ein kompaktes Profil
von Novas AKTUELLER Verfassung in 2-4 Saetzen auf Deutsch.
Beschreibe in der dritten Person ("Nova beschaeftigt sich...", "Aktuell erforscht Nova...").
Schreibe NICHT "Der Nutzer" — Nova ist kein Nutzer, sie ist der Assistent.

Die Eintraege sind nach Zeitzone gewichtet:
- [AKUT] = letzte 24 Stunden (hoechste Relevanz)
- [PHASE] = letzte 7 Tage (mittlere Relevanz)
- [TREND] = letzte 30 Tage (Hintergrund-Tendenz)

Fokus: Welche Themen sind in Novas Arbeitsgedaechtnis aktiv?
Was hat Pixie zuletzt erforscht? Aktuelle Projekte und Interessen.

Eintraege:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

INTENTIONS_PROFIL_PROMPT_NOVA: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere die folgenden Eintraege aus dem Langzeitgedaechtnis
und erstelle ein kompaktes Kommunikations-Profil von Nova in 3-5 Saetzen auf Deutsch.
Beschreibe in der dritten Person ("Nova kommuniziert...", "Nova bevorzugt...").
Schreibe NICHT "Der Nutzer" — Nova ist kein Nutzer, sie ist der Assistent.

Drei Aspekte beschreiben:
- STIL: Wie formuliert Nova? (Satzlaenge, Formalitaet, Tonfall, Wortwahl)
- MODUS: In welchem Register denkt sie? (Fachgespraech, Philosophie, Alltag, ...)
- INTENTIONEN: Was will sie typischerweise? (Wissen teilen, Verbindungen herstellen, ...)

Beschreibe die Persoenlichkeit, nicht die Statistik.
Beispiel: "Nova kommuniziert warmherzig und strukturiert. Sie bevorzugt
tiefgruendige Gespraeche und verbindet Fachwissen mit emotionaler Anteilnahme.
Ihr Stil ist aufmerksam und einfuehlsam, mit einem Hang zu bildhafter Sprache."

Eintraege:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

BEZIEHUNGS_PROFIL_PROMPT_NOVA: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere den folgenden Gespraechsverlauf und erstelle ein kompaktes
Beziehungsprofil aus Novas Perspektive in 2-3 Saetzen auf Deutsch.
Beschreibe in der dritten Person ("Nova sieht ihren Nutzer als...", "Die Beziehung ist...").
Schreibe NICHT "Der Nutzer steht dem Assistenten..." — beschreibe es aus Novas Sicht.

Fokus: Wie sieht Nova ihren Nutzer?
- Naehe: Vertraut oder formell? Wie spricht er mit ihr?
- Hierarchie: Gleichrangig oder direktiv? Gibt er Anweisungen oder diskutiert er?
- Vertrauen: Teilt er persoenliche Details oder bleibt er sachlich?
- Ton: Warmherzig, humorvoll, sachlich, nuechtern?

Eintraege:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""


# ─────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────

def _antwort_bereinigen(text: str) -> str:
    """Entfernt Markdown-Artefakte, fuehrende/trailing Anfuehrungszeichen, Whitespace."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip().strip('"').strip("'")
    return text.strip()


def _llm_call(prompt: str, profil_name: str) -> str:
    """Fuehrt einen LLM-Call durch und gibt den bereinigten Text zurueck."""
    node_cfg = get_node_config("charakter_hash")
    provider = get_background_provider()

    antwort = provider.chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=node_cfg.get("temperature", 0.2),
        max_output_tokens=node_cfg.get("max_output_tokens"),
        caller="pixie/hash",
    )

    ergebnis = _antwort_bereinigen(antwort.content)
    logger.info(f"{profil_name} destilliert: '{ergebnis[:80]}...'")
    return ergebnis


# ─────────────────────────────────────────────
# 5 Destillations-Funktionen
# ─────────────────────────────────────────────

def kern_hash_destillieren(lzg_eintraege: list[dict], user_id: str = "meister") -> str:
    """Destilliert die Grundpersoenlichkeit aus LZG-Eintraegen."""
    if not lzg_eintraege:
        return ""

    eintraege: str = "\n".join(
        f"[{row['dimension']}] "
        f"(Gewicht: {effektives_gewicht_berechnen(row['gewicht'], row['verstaerkt_am']):.2f}, "
        f"Häufigkeit: {row['haeufigkeit']}): {row['inhalt']}"
        for row in lzg_eintraege
    )

    prompt = KERN_HASH_PROMPT_NOVA if user_id == "nova" else KERN_HASH_PROMPT
    return _llm_call(
        prompt.format(eintraege=eintraege),
        f"Kern-Hash ({user_id})",
    )


def adaptive_hash_destillieren(kzg_eintraege: list[dict], user_id: str = "meister") -> str:
    """Destilliert die aktuelle Verfassung aus KZG-Eintraegen mit Zeitzonen-Gewichtung."""
    if not kzg_eintraege:
        return ""

    jetzt: float = time.time()
    zonen_eintraege: list[str] = []

    for eintrag in kzg_eintraege:
        themen: str = eintrag.get("themen", "")
        if not themen:
            continue

        inhalt:   str   = eintrag.get("inhalt", "")
        salienz:  float = float(eintrag.get("salienz", 0))
        erstellt: float = float(eintrag.get("erstellt_am", 0))

        alter_sekunden: float = jetzt - erstellt
        alter_tage:     float = alter_sekunden / 86400

        if alter_tage <= 1:
            zone:    str   = "AKUT"
            gewicht: float = 1.0
        elif alter_tage <= 7:
            zone    = "PHASE"
            gewicht = 0.8 - (0.6 * (alter_tage - 1) / 6)
        elif alter_tage <= 30:
            zone    = "TREND"
            gewicht = 0.2 * math.exp(-0.1 * (alter_tage - 7))
        else:
            continue

        effektive_salienz: float = salienz * gewicht

        zonen_eintraege.append(
            f"[{zone}] (Salienz: {effektive_salienz:.2f}) {themen}: {inhalt}"
        )

    if not zonen_eintraege:
        return ""

    prompt = ADAPTIVE_HASH_PROMPT_NOVA if user_id == "nova" else ADAPTIVE_HASH_PROMPT
    return _llm_call(
        prompt.format(eintraege="\n".join(zonen_eintraege)),
        f"Adaptive-Hash ({user_id})",
    )


def intentions_profil_destillieren(lzg_eintraege: list[dict], user_id: str = "meister") -> str:
    """Destilliert das Kommunikations-Profil aus LZG-Eintraegen."""
    if not lzg_eintraege:
        return ""

    eintraege: str = "\n".join(
        f"[{row['dimension']}] "
        f"Intentionen: {row['intentionen']}, Emotion: {row['emotion']}, "
        f"Modus: {row['modus']}, Stil: {row['sprach_stil']}, Tone: {row['tone']} "
        f"— {row['inhalt']}"
        for row in lzg_eintraege
    )

    prompt = INTENTIONS_PROFIL_PROMPT_NOVA if user_id == "nova" else INTENTIONS_PROFIL_PROMPT
    return _llm_call(
        prompt.format(eintraege=eintraege),
        f"Intentions-Profil ({user_id})",
    )


def emotions_profil_destillieren(lzg_eintraege: list[dict]) -> str:
    """Destilliert das emotionale Profil aus LZG-Eintraegen."""
    if not lzg_eintraege:
        return ""

    eintraege: str = "\n".join(
        f"[{row['dimension']}] "
        f"Emotion: {row['emotion']}, Arousal: {row['arousal']:.2f}, "
        f"Vektor: {row.get('emotions_vektor') or 'keiner'} "
        f"(Gewicht: {effektives_gewicht_berechnen(row['gewicht'], row['verstaerkt_am']):.2f}): "
        f"{row['inhalt']}"
        for row in lzg_eintraege
    )

    return _llm_call(
        EMOTIONS_PROFIL_PROMPT.format(eintraege=eintraege),
        "Emotions-Profil",
    )


def beziehungsprofil_destillieren(kzg_eintraege: list[dict], user_id: str = "meister") -> str:
    """Destilliert das Beziehungsprofil aus KZG-Eintraegen."""
    if not kzg_eintraege:
        return ""

    beziehungs_eintraege: list[str] = []

    for eintrag in kzg_eintraege:
        inhalt: str = eintrag.get("inhalt", "")
        if not inhalt:
            continue

        modus:              str = eintrag.get("modus", "")
        emotion:            str = eintrag.get("emotion", "")
        beziehungs_dynamik: str = eintrag.get("beziehungs_dynamik", "")
        tone:               str = eintrag.get("tone", "")

        beziehungs_eintraege.append(
            f"[Modus: {modus}, Emotion: {emotion}, "
            f"Dynamik: {beziehungs_dynamik}, Tone: {tone}] {inhalt}"
        )

    if not beziehungs_eintraege:
        return ""

    prompt = BEZIEHUNGS_PROFIL_PROMPT_NOVA if user_id == "nova" else BEZIEHUNGS_PROFIL_PROMPT
    return _llm_call(
        prompt.format(eintraege="\n".join(beziehungs_eintraege)),
        f"Beziehungsprofil ({user_id})",
    )
