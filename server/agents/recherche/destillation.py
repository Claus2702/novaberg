"""Destillation — LLM fasst Ergebnisse im Arbeitskontext zusammen.

Zwei Funktionen, zwei Modelle:
- zwischen_destillieren(): Qwen3-32B (Analyse) — komprimiert Fakten, JSON-nah
- ergebnisse_destillieren(): Mistral Q4 (Sprache) — formuliert Fliesstext mit Charakter
"""

import logging

from services.model_services import BackgroundRequest, model_service

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

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G4) ──
    # zwischen_destillieren() laeuft im RechercheAgent, sync invoked aus
    # services/pixie/dispatch.py via asyncio.to_thread → Worker-Thread ohne
    # Event-Loop → submit_sync. expect_json=False, da Fliesstext-Zusammen-
    # fassung. CJK-Guard bleibt im Worker.
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "analyse",
            temperature = 0.1,
            caller      = "recherche/zwischen",
        ))
        zusammenfassung = response.text
        logger.info(f"Zwischen-Destillation: {len(zusammenfassung)} Zeichen")
        return zusammenfassung

    except Exception as e:
        logger.exception(f"{type(e).__name__}: Zwischen-Destillation fehlgeschlagen")
        return ""


# ─────────────────────────────────────────────
# Finale Destillation (Mistral, Sprach-Modell, am Ende)
# ─────────────────────────────────────────────

_DESTILLATIONS_PROMPT: str = """[AUFGABE]
Du bereitest einen Fund auf. Was hier entsteht, ist **Material** — Wissen, das
gleich neben Gedaechtnis und Web-Recherche liegt und aus dem eine zweite Stufe
bestimmt, was davon gesagt wird und wie.

Deshalb hat es keinen Sprecher und keinen Empfaenger. Es sagt, was der Fall
ist, und niemand spricht darin.

[THEMA]
{ziel}

[NEUE_ERKENNTNISSE]
{ergebnisse}

[RAUM]
Du hast 600 bis 1200 Zeichen. Das ist der Platz, den ein Fund braucht, und er
gehoert ganz ihm.

Er reicht genau fuer die drei Bewegungen, die ein Fund hat:

- WAS GEFUNDEN WURDE. Der Sachverhalt, mit den Zahlen, Namen und Groessen, die
  ihn tragen.
- WORAUF ER STEHT. Woran er festzumachen ist — die Messung, das Verfahren, der
  Beleg.
- WAS OFFEN BLEIBT. Die Kante, an der das Wissen aufhoert.

Was in diese drei passt, ist der Fund. Was daneben stuende, waere schon die
Ausarbeitung — und die entsteht spaeter, aus diesem Material, von einer Stufe,
die die Lage kennt und du nicht.

[PRUEFBEDINGUNG]
Dein Ergebnis traegt, wenn jemand, der die Recherche nicht gelesen hat, daraus
sagen kann: was daran neu ist, woran es haengt, und wo es aufhoert.

[REGELN]
- Nur, was tatsaechlich neu ist — Bekanntes traegt nichts bei.
- Das Wissen ganz aufnehmen, Quellen nicht einzeln auffuehren.
- Sprache: Deutsch.
- Ist die Informationslage duenn, steht genau das da: was gesucht und was
  gefunden wurde."""



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

    # **Kein Empfaenger, kein Register.** Expertise, Interessen, Beziehung und
    # Modus standen bis zum 14.08.2026 im Prompt und haben aus dem Material
    # eine auf jemanden zugeschnittene Rede gemacht. Wer die Rede zuschneidet,
    # ist die zweite Stufe — sie kennt die Lage dieses Turns, dieser Lauf nicht:
    # Zwischen Recherche und Einwurf koennen Stunden liegen.
    prompt = _DESTILLATIONS_PROMPT.format(
        ziel=ziel,
        ergebnisse="\n\n".join(ergebnisse[:3]),
    )

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G4) ──
    # ergebnisse_destillieren() laeuft im RechercheAgent, sync invoked aus
    # services/pixie/dispatch.py via asyncio.to_thread → Worker-Thread ohne
    # Event-Loop → submit_sync. modus="sprache" → Mistral/Gemma-CPU (nicht
    # Qwen). expect_json=False, Fliesstext fuer den User-Charakter. CJK-
    # Guard im Worker — kritisch fuer user-faceende Sprach-Ausgabe.
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "sprache",
            temperature = 0.3,
            caller      = "recherche/destillation",
        ))
        destillat = response.text
        logger.info(f"Recherche-Destillation: {len(destillat)} Zeichen")
        return destillat

    except Exception as e:
        logger.exception(f"{type(e).__name__}: Recherche-Destillation fehlgeschlagen")
        return ""
