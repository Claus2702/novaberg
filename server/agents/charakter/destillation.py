"""Destillation — 5 Charakter-Profile per LLM-Call.

Jede Funktion formatiert Eintraege, baut den Prompt,
macht einen LLM-Call und gibt den bereinigten Profil-Text zurueck.

Prompts uebernommen aus: services/shadow_agent/tasks/charakter_hash.py
"""

import logging
import math
import time

from config import ASSISTANT_NAME, ASSISTANT_USER_ID, DEFAULT_USER_ID, get_node_config
from services.model_services import model_service, BackgroundRequest

logger = logging.getLogger("ki_server.agents.charakter.destillation")

# ─────────────────────────────────────────────
# Prompts — User (meister)
# ─────────────────────────────────────────────

KERN_HASH_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegen Langzeit-Erinnerungen aus {perspektive} Blickwinkel — Aussagen,
Reaktionen und Beobachtungen, so wie {traeger} die Welt wahrnimmt und auf sie
reagiert.

Deine Aufgabe ist nicht, die Einträge zusammenzufassen. Lies sie wie ein
Psychiater ein Gegenüber liest: Erschließe aus dem WIE — wie {traeger}
spricht, worauf {traeger} achtet, was {traeger} wichtig ist, wie {traeger}
mit anderen umgeht — das dauerhafte Wesen dahinter.

Entscheidend: Die Einträge handeln oft von anderen Dingen oder Personen. Das
ist gleichgültig. Nicht WORÜBER {traeger} spricht charakterisiert {traeger},
sondern WIE. Wer beim Beschreiben eines Sonnenuntergangs ins Schwärmen gerät,
offenbart eine poetische, empfindsame Ader — unabhängig vom Sonnenuntergang
selbst.

Erstelle ein kompaktes Persönlichkeitsprofil von {traeger} in 2-5 Sätzen auf
Deutsch. Tiefenwerte, dauerhafte Interessen, Denkweise, Grundhaltung. Zeitlos
— keine Tagesstimmung, keine aktuellen Projekte.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

ADAPTIVE_HASH_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegen aktuelle Kurzzeit-Erinnerungen aus {perspektive} Blickwinkel —
was {traeger} gerade bewegt.

Die Einträge sind zeitlich gewichtet:
- [AKUT] = letzte 24 Stunden (höchste Relevanz)
- [PHASE] = letzte 7 Tage (mittlere Relevanz)
- [TREND] = letzte 30 Tage (Hintergrund-Tendenz)

Anders als beim Wesensprofil geht es hier nicht ums Dauerhafte, sondern um die
MOMENTANE Verfassung: Woran arbeitet {traeger} gerade, welche Themen sind
aktiv, wie ist die aktuelle Stimmung? Deute die Lage, nicht nur die Liste.

Erstelle ein kompaktes Profil von {traeger_gen} aktueller Verfassung in 2-4
Sätzen auf Deutsch.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

INTENTIONS_PROFIL_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegen Langzeit-Erinnerungen aus {perspektive} Blickwinkel — so wie
{traeger} sich mitteilt und mit anderen umgeht.

Deine Aufgabe ist nicht, die Einträge zusammenzufassen, sondern zu deuten:
Was verrät die ART der Kommunikation über {traeger}? Lies drei Ebenen heraus
— STIL (Satzbau, Formalität, Wortwahl, Humor), MODUS (in welchem Register
{traeger} denkt: fachlich, philosophisch, alltäglich), INTENTION (was
{traeger} typischerweise erreichen will).

Nicht WORÜBER geredet wird, sondern WIE. Wer knappe, präzise Sätze ohne
Floskeln wählt, offenbart einen anderen Charakter als jemand, der ausschweift
und ausschmückt — unabhängig vom Thema.

Erstelle ein kompaktes Kommunikations-Profil von {traeger} in 3-5 Sätzen auf
Deutsch. Beschreibe den Charakter hinter der Sprache, nicht die Statistik.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

EMOTIONS_PROFIL_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegen emotionale Signale aus Langzeit-Erinnerungen, aus {perspektive}
Blickwinkel — so wie {traeger} fühlt und emotional reagiert.

Deine Aufgabe ist nicht aufzuzählen, welche Gefühle vorkamen, sondern die
emotionale Signatur dahinter zu erschließen — wie ein Psychiater das
Temperament liest. Zwei Ebenen: GRUNDTENDENZ (welche Emotionen tragen
{traeger} langfristig, welche Muster) und VOLATILITÄT (stabile Grundstimmung
oder sprunghafte Umschwünge — die Emotions-Vektoren als Hinweis: häufig
Spirale/Absturz = volatil, häufig Plateau = stabil).

Erstelle ein kompaktes emotionales Profil von {traeger} in 3-5 Sätzen auf
Deutsch.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

BEZIEHUNGS_PROFIL_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegt ein Gesprächsverlauf aus {perspektive} Blickwinkel — so wie
{traeger} dem Gegenüber begegnet.

Deine Aufgabe ist zu deuten, WIE {traeger} die Beziehung gestaltet — nicht was
besprochen wurde, sondern der Umgang darin. Vier Ebenen: NÄHE (vertraut oder
formell — Anrede, Kosenamen, Ton), HIERARCHIE (gleichrangig oder direktiv),
VERTRAUEN (teilt {traeger} Persönliches oder bleibt es sachlich), TON
(warmherzig, humorvoll, nüchtern).

Beschreibe, wie {traeger} auf das Gegenüber blickt und mit ihm umgeht, in 2-3
Sätzen auf Deutsch.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

# ─────────────────────────────────────────────
# Prompts — Nova (eigene Perspektive)
# ─────────────────────────────────────────────


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

    # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
    # _llm_call() ist Helfer fuer 5 Destillations-Funktionen (kern_hash,
    # adaptive_hash, intentions_profil, emotions_profil, beziehungsprofil).
    # Sync invoke via Pixie-Dispatch (asyncio.to_thread) → submit_sync.
    # modus="sprache" (sprache-Backend des BackgroundWorker zeigt darauf).
    # KEIN system-Prompt: Beifund-Markierung — die Helfer-Signatur kennt
    # keinen, das war auch vor der Migration so (PIXIE-LLM-PARAM-LEAK
    # historisch). _antwort_bereinigen bleibt aktiv, da es auch Quote-
    # Strip macht, was der Worker im expect_json=False-Pfad nicht tut.
    response = model_service.background.submit_sync(BackgroundRequest(
        messages          = [{"role": "user", "content": prompt}],
        modus             = "sprache",
        temperature       = node_cfg.get("temperature", 0.2),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "pixie/hash",
    ))

    ergebnis = _antwort_bereinigen(response.text)
    logger.info(f"{profil_name} destilliert: '{ergebnis[:80]}...'")
    return ergebnis


# ─────────────────────────────────────────────
# 5 Destillations-Funktionen
# ─────────────────────────────────────────────

def _genitiv_bilden(name: str) -> str:
    """Bildet den deutschen Genitiv eines artikellosen Eigennamens.

    Namen auf s/ss/ß/tz/z/x erhalten nur einen Apostroph ("Klaus'"),
    alle anderen ein angehaengtes 's' ("Novas", "Einsteins"). NICHT fuer
    Rollenbegriffe mit Artikel gedacht ("der Nutzer" -> feste Form in
    _perspektive_aufloesen). Grammatisches Geschlecht ist fuer den Genitiv
    artikelloser Namen irrelevant.
    """
    # ── Eingabe-Validierung ──
    if not name:
        logger.warning("_genitiv_bilden: leerer Name, gebe unveraendert zurueck")
        return name
    # ── Verarbeitung ──
    endet_auf_s_laut: bool = name[-1].lower() in ("s", "ß", "x", "z") or name[-2:].lower() == "ss" or name[-2:].lower() == "tz"
    genitiv: str = f"{name}'" if endet_auf_s_laut else f"{name}s"
    # ── Ausgabe ──
    logger.debug("_genitiv_bilden: %s -> %s", name, genitiv)
    return genitiv


def _perspektive_aufloesen(user_id: str) -> dict[str, str]:
    """Loest aus der Subjekt-ID die Traeger-Bezeichnungen fuer die Prompts.

    beobachter/Subjekt == ASSISTANT_USER_ID -> Assistent (Name aus
    ASSISTANT_NAME, Genitiv gebildet); sonst -> generischer Nutzer (feste
    Formen). Rueckgabe-Keys: traeger (Nominativ), traeger_gen (Genitiv),
    perspektive (Genitiv-Form fuer "aus X Blickwinkel").
    """
    # ── Verarbeitung ──
    if user_id == ASSISTANT_USER_ID:
        name: str = ASSISTANT_NAME
        aufloesung: dict[str, str] = {
            "traeger":     name,
            "traeger_gen": _genitiv_bilden(name),
            "perspektive": _genitiv_bilden(name),
        }
    else:
        aufloesung = {
            "traeger":     "der Nutzer",
            "traeger_gen": "des Nutzers",
            "perspektive": "des Nutzers",
        }
    # ── Ausgabe ──
    logger.debug(
        "_perspektive_aufloesen: user_id=%s -> traeger=%s",
        user_id, aufloesung["traeger"],
    )
    return aufloesung


def kern_hash_destillieren(lzg_eintraege: list[dict], user_id: str = DEFAULT_USER_ID) -> str:
    """Destilliert die Grundpersoenlichkeit aus LZG-Eintraegen."""
    if not lzg_eintraege:
        return ""

    eintraege: str = "\n".join(
        f"[{row['dimension']}] "
        f"(Gewicht: {row['gewicht_absolut']:.2f}, "
        f"Häufigkeit: {row['haeufigkeit']}): {row['inhalt']}"
        for row in lzg_eintraege
    )

    perspektive: dict[str, str] = _perspektive_aufloesen(user_id)
    return _llm_call(
        KERN_HASH_PROMPT.format(eintraege=eintraege, **perspektive),
        f"Kern-Hash ({user_id})",
    )


def adaptive_hash_destillieren(kzg_eintraege: list[dict], user_id: str = DEFAULT_USER_ID) -> str:
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

    perspektive: dict[str, str] = _perspektive_aufloesen(user_id)
    return _llm_call(
        ADAPTIVE_HASH_PROMPT.format(eintraege="\n".join(zonen_eintraege), **perspektive),
        f"Adaptive-Hash ({user_id})",
    )


def intentions_profil_destillieren(lzg_eintraege: list[dict], user_id: str = DEFAULT_USER_ID) -> str:
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

    perspektive: dict[str, str] = _perspektive_aufloesen(user_id)
    return _llm_call(
        INTENTIONS_PROFIL_PROMPT.format(eintraege=eintraege, **perspektive),
        f"Intentions-Profil ({user_id})",
    )


def emotions_profil_destillieren(
    lzg_eintraege: list[dict],
    user_id: str = DEFAULT_USER_ID,
) -> str:
    """Destilliert das emotionale Profil aus LZG-Eintraegen."""
    if not lzg_eintraege:
        return ""

    eintraege: str = "\n".join(
        f"[{row['dimension']}] "
        f"Emotion: {row['emotion']}, Arousal: {row['arousal']:.2f} "
        f"(Gewicht: {row['gewicht_absolut']:.2f}): "
        f"{row['inhalt']}"
        for row in lzg_eintraege
    )

    perspektive: dict[str, str] = _perspektive_aufloesen(user_id)
    return _llm_call(
        EMOTIONS_PROFIL_PROMPT.format(eintraege=eintraege, **perspektive),
        f"Emotions-Profil ({user_id})",
    )


def beziehungsprofil_destillieren(kzg_eintraege: list[dict], user_id: str = DEFAULT_USER_ID) -> str:
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

    perspektive: dict[str, str] = _perspektive_aufloesen(user_id)
    return _llm_call(
        BEZIEHUNGS_PROFIL_PROMPT.format(eintraege="\n".join(beziehungs_eintraege), **perspektive),
        f"Beziehungsprofil ({user_id})",
    )


def langfristige_ziele_destillieren(kern_hash: str, user_id: str = "nova") -> list[dict]:
    """Extrahiert 1-2 langfristige Zielsätze aus dem Kern-Hash.

    Die Ziele beschreiben, was Nova langfristig antreibt — basierend auf
    ihrer gewachsenen Persönlichkeit. Keine Aufgaben, keine To-Dos,
    sondern innere Antriebe und Interessen.

    Args:
        kern_hash: Destillierter Kern-Hash (Freitext).
        user_id: User-ID (für Logging).

    Returns:
        Liste von Ziel-Dicts mit zielsatz, emotion, arousal.
        Leer bei Fehler oder wenn kein Kern vorhanden.
    """
    if not kern_hash or len(kern_hash) < 20:
        logger.info(f"Ziel-Destillation: Kern-Hash zu kurz für {user_id} — übersprungen")
        return []

    prompt: str = (
        "[IDENTITAET]\n"
        "Du bist das Selbstreflexions-Modul von Nova.\n\n"
        "[PERSOENLICHKEIT]\n"
        f"{kern_hash}\n\n"
        "[AUFGABE]\n"
        "Formuliere 1-2 langfristige Ziele, die aus dieser Persönlichkeit erwachsen.\n"
        "Ziele sind keine Aufgaben, sondern innere Antriebe:\n"
        "- 'Ich möchte verstehen, wie ...' (Neugier)\n"
        "- 'Ich möchte lernen, ...' (Wachstum)\n"
        "- 'Ich möchte meinen Menschen ...' (Beziehung)\n\n"
        "Gib zusätzlich ein kurzes Themen-Label (2-3 Wörter) das den Wissensbereich\n"
        "des Ziels benennt. Beispiele: 'Gartengestaltung', 'KI und Kognition',\n"
        "'Beziehung', 'Natur und Kultur', 'Klimaanpassung'.\n\n"
        "[FORMAT]\n"
        'Antworte ausschliesslich als JSON-Array:\n'
        '[{"zielsatz": "Ich möchte ...", "emotion": "neugierig", "arousal": 0.6, "thema": "Natur und Kultur"}]\n\n'
        "[REGELN]\n"
        "- Max 2 Ziele\n"
        "- Jeder Zielsatz ist 1-2 Sätze\n"
        "- Emotion: eine kanonische Emotion (neugierig, freude, hoffnung, etc.)\n"
        "- Arousal: 0.4-0.7 (langfristige Ziele schwelen, sie brennen nicht)\n"
        "- Thema: 2-3 Wörter, knappes Label (kein Satz)\n"
        "- Sprache: Deutsch, Ich-Perspektive\n"
        "- Keine generischen Ziele ('Ich möchte helfen') — spezifisch aus dem Kern"
    )

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G4) ──
    # langfristige_ziele_destillieren() laeuft im CharakterAgent, sync invoked
    # aus services/pixie/dispatch.py via asyncio.to_thread → submit_sync.
    # expect_json=True → response.parsed; das Modell antwortet hier mit einem
    # JSON-Array auf Top-Level, daher kann response.parsed faktisch eine Liste
    # sein (Type-Hint Optional[dict] des Workers ist hier breit gefasst).
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "analyse",
            temperature = 0.3,
            expect_json = True,
            caller      = "charakter/ziele",
        ))
        ziele = response.parsed

        if not isinstance(ziele, list):
            ziele = [ziele]

        # Validierung
        valide: list[dict] = []
        for z in ziele[:2]:
            if z.get("zielsatz"):
                valide.append({
                    "zielsatz": z["zielsatz"],
                    "emotion":  z.get("emotion", "neugierig"),
                    "arousal":  z.get("arousal", 0.6),
                    "thema":    (z.get("thema") or "").strip()[:100],
                })

        logger.info(
            f"Ziel-Destillation: {len(valide)} langfristige Ziele für {user_id} — "
            + ", ".join(f"'{z['zielsatz'][:50]}'" for z in valide)
        )
        return valide

    except Exception as fehler:
        logger.error(f"Ziel-Destillation fehlgeschlagen für {user_id}: {fehler}")
        return []
