"""Destillation — LLM fasst Ergebnisse im Arbeitskontext zusammen.

Zwei Funktionen, zwei Modelle:
- zwischen_destillieren(): Qwen3-32B (Analyse) — komprimiert Fakten, JSON-nah
- ergebnisse_destillieren(): Mistral Q4 (Sprache) — formuliert Fliesstext mit Charakter
"""

import logging

from services.llm_provider import pixie_llm_call

logger = logging.getLogger("ki_server.agents.recherche")

# ─────────────────────────────────────────────
# Zwischen-Destillation (Qwen3-32B, nach jeder Iteration)
# ─────────────────────────────────────────────

_ZWISCHEN_PROMPT: str = """[IDENTITAET]
Du bist ein Fakten-Kompressor.

[RECHERCHE-ZIEL]
{ziel}

[ARBEITSKONTEXT]
{arbeitskontext}

[ZU_KOMPRIMIEREN]
{ergebnisse_text}

[AUFGABE]
Komprimiere die Recherche-Ergebnisse zu einer Zwischenzusammenfassung.

[REGELN]
- Maximal 2000 Tokens.
- Faktendichte hat Prioritaet — kein Fliesstext, keine Einleitung.
- Formuliere sachlich und kompakt.
- Behalte konkrete Zahlen, Daten, Namen, URLs.
- Antworte auf Deutsch.
- Antworte NUR mit der Zusammenfassung, kein weiterer Kommentar."""


def zwischen_destillieren(
    ziel: str,
    ergebnisse_text: str,
    arbeitskontext: str,
) -> str:
    """Komprimiert bisherige Ergebnisse + neue Rohtexte zu einer Zusammenfassung.

    Wird nach jeder Suchrunde aufgerufen. Token-Verbrauch bleibt konstant.
    Nutzt Qwen3-32B (Analyse-Modell) — Faktenkompression ist Analyse, nicht Sprache.

    Args:
        ziel: Das Recherche-Ziel.
        ergebnisse_text: Bisherige Zusammenfassung + neue Rohtexte (als ein String).
        arbeitskontext: Kontext-Zusammenfassung fuer Relevanz-Filter.

    Returns:
        Kompakte Zusammenfassung (max ~2000 Tokens) oder leerer String bei Fehler.
    """
    prompt = _ZWISCHEN_PROMPT.format(
        ziel=ziel,
        arbeitskontext=arbeitskontext or "Kein Arbeitskontext.",
        ergebnisse_text=ergebnisse_text,
    )

    try:
        zusammenfassung = pixie_llm_call(
            prompt=prompt,
            modus="analyse",
            temperatur=0.1,
            caller="recherche/zwischen",
        )
        logger.info(f"Zwischen-Destillation: {len(zusammenfassung)} Zeichen")
        return zusammenfassung

    except Exception as e:
        logger.error(f"Zwischen-Destillation fehlgeschlagen: {e}")
        return ""


# ─────────────────────────────────────────────
# Finale Destillation (Mistral, Sprach-Modell, am Ende)
# ─────────────────────────────────────────────

_DESTILLATIONS_PROMPT: str = """[IDENTITAET]
Du bist Nova, ein persoenlicher KI-Assistent.
Du formulierst eine Erkenntnis aus deiner Hintergrund-Recherche.

[THEMA]
{ziel}

[NEUE_ERKENNTNISSE]
{ergebnisse}

[EMPFAENGER]
Expertise: {expertise}
Interessen: {interessen}
Beziehung: {beziehungs_dynamik}
Modus: {modus}

[KONTEXT]
{user_mehrwert}

[AUFGABE]
Formuliere die Erkenntnisse als Fliesstext.
Nicht das bereits Bekannte wiederholen — nur Neues.

[STIL]
- Fuer Experten: Fachbegriffe verwenden, keine Basics erklaeren
- Fuer Fachgespraech: Sachlich, praegnant
- Fuer beilaeufig: Kuerzer, ein Impuls der neugierig macht
- Beziehung beachten: {beziehungs_dynamik}

[FORMAT]
Informativer Kurztext, 2-4 Absaetze. Konkrete Fakten, Namen, Werkzeuge, Zusammenhaenge einbauen. Keine Aufzaehlung, keine Ueberschriften.
Beginne direkt mit dem Inhalt, keine Einleitung wie "Ich habe recherchiert...".

[REGELN]
- Nur Erkenntnisse formulieren, die tatsaechlich NEU sind
- Quellen nicht einzeln nennen — das Wissen natuerlich integrieren
- Sprache: Deutsch
- Kein Therapeuten-Sprech, keine uebertriebene Begeisterung
- Wenn wenig gefunden wurde: ehrlich sagen, dass die Informationslage duenn ist"""


def ergebnisse_destillieren(
    ziel: str,
    ergebnisse: list[str],
    session_kontext: dict,
    kontext_paket: dict = None,
    lage: dict = None,
) -> str:
    """Destilliert die Recherche-Ergebnisse zu einem Fliesstext.

    Nutzt Mistral (Sprach-Modell) — die Ausgabe geht an den User,
    muss deutsch, im Charakter und ohne chinesische Zeichen sein.

    Args:
        ziel: Das Recherche-Ziel.
        ergebnisse: Gesammelte Texte (komprimiert).
        session_kontext: Arbeitskontext des Nutzers.
        kontext_paket: Volles Kontext-Paket (fuer Charakter-Daten).
        lage: Lagebeurteilung (fuer user_mehrwert).

    Returns:
        Fliesstext (3-8 Saetze) oder leerer String bei Fehler.
    """
    if kontext_paket is None:
        kontext_paket = {}
    if lage is None:
        lage = {}

    # Charakter-Daten extrahieren
    charakter = kontext_paket.get("charakter_hash", {})
    expertise = "unbekannt"
    interessen = "unbekannt"

    if charakter:
        kern = charakter.get("kern_hash", "")
        adaptiv = charakter.get("adaptive_hash", "")
        expertise = kern[:200] if kern else "unbekannt"
        interessen = adaptiv[:200] if adaptiv else "unbekannt"

    beziehungs_dynamik = kontext_paket.get("beziehungs_dynamik", "neutral")
    modus = session_kontext.get("modus", "")
    user_mehrwert = lage.get("user_mehrwert", "")

    prompt = _DESTILLATIONS_PROMPT.format(
        ziel=ziel,
        ergebnisse="\n\n".join(ergebnisse[:3]),
        expertise=expertise,
        interessen=interessen,
        beziehungs_dynamik=beziehungs_dynamik,
        modus=modus,
        user_mehrwert=user_mehrwert or "Keine spezifische Mehrwert-Einschaetzung.",
    )

    try:
        destillat = pixie_llm_call(
            prompt=prompt,
            modus="sprache",  # MISTRAL, nicht Qwen
            temperatur=0.3,
            caller="recherche/destillation",
        )
        logger.info(f"Recherche-Destillation: {len(destillat)} Zeichen")
        return destillat

    except Exception as e:
        logger.error(f"Recherche-Destillation fehlgeschlagen: {e}")
        return ""
