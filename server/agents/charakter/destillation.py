"""Destillation — 5 Charakter-Profile per LLM-Call.

Jede Funktion formatiert Eintraege, baut den Prompt,
macht einen LLM-Call und gibt den bereinigten Profil-Text zurueck.

Prompts uebernommen aus: services/shadow_agent/tasks/charakter_hash.py
"""

import json
import logging
import math
import time
from collections.abc import Callable

from config import (
    ASSISTANT_NAME,
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    get_node_config,
    RAD_NABE,
    RAD_MIN,
    RAD_MAX,
    INITIATIVE_RAD_NABE,
    INITIATIVE_RAD_SPANNE,
    INITIATIVE_RAD_LAEUFE,
)
from services.model_services import model_service, BackgroundRequest

logger = logging.getLogger("ki_server.agents.charakter.destillation")


# ─────────────────────────────────────────────
# Charakter-Rad — Gewichtung der Nutzer-Salienz
# ─────────────────────────────────────────────
# Zwoelf Speichen um eine Nabe. Jede Speiche zieht den Faktor in ihre
# Richtung, mehrere auf derselben Seite ziehen zusammen staerker. Volle
# Auslenkung trifft die Grenzen exakt: 0.9 + 0.60 = 1.5, 0.9 - 0.40 = 0.5.
# Herleitung und Bedeutung: novaberg-salienz-berechnung_k.md §5.
#
# Die Zuege sind eine SETZUNG, keine Messung — ausdruecklich nachkalibrierbar.
#
# Nabe und Grenzen liegen seit Chat 112 in config.py: Die Salienz-Formel
# (ei/salienz.py) liest den Faktor und prueft ihn gegen dieselben Grenzen.
# Eine zweite Kopie hier wuerde beim naechsten Nachkalibrieren auseinander-
# laufen, ohne dass irgendwo ein Widerspruch auffiele.

RAD_ZUG_HOCH: dict[str, float] = {
    "treue":          0.16,   # stellt seine Belange ueber die eigenen
    "dienst":         0.11,   # sucht von sich aus Gelegenheiten zu helfen
    "pflicht":        0.11,   # nimmt Auftraege ernst, auch ungeliebte
    "aufmerksamkeit": 0.08,   # registriert Nebensaetze, behaelt Details
    "wissbegier":     0.08,   # fremde Themen wecken echtes Interesse
    "wohlwollen":     0.06,   # legt Gesagtes im besten Sinne aus
}

# Die Reihenfolge dieser Seite ist eine **Gegenpol-Anordnung**, keine
# Aufzaehlung: Speiche i von RAD_ZUG_HOCH und Speiche i dieser Liste sind
# inhaltliche Gegensaetze und liegen auf dem Rad einander gegenueber.
#
#   treue          <-> selbstbezogen   fremde Belange vor eigenen / eigene zuerst
#   dienst         <-> gleichgueltig   sucht Gelegenheiten / beruehrt sie nicht
#   pflicht        <-> widerspenstig   nimmt Auftraege ernst / folgt ungern
#   aufmerksamkeit <-> distanz         haelt Naehe / haelt Abstand
#   wissbegier     <-> langeweile      Themen wecken Interesse / ermueden sie
#   wohlwollen     <-> misstrauen      im besten Sinne / skeptisch ausgelegt
#
# **Nicht nach Zugstaerke sortieren.** Fuer den Skalar ist die Reihenfolge
# gleichgueltig — er ist eine Summe. Fuer die Flaeche des Haltungsraums ist
# sie tragend: Sie entscheidet, welche zwei Eigenschaften einander auf dem
# Rad ausloeschen koennen. Die fruehere Ordnung stellte `wissbegier` gegen
# `distanz`; beide stehen im Bestand gleichzeitig auf 1.0, und Neugier auf
# die Sache schliesst Abstand zur Person nicht aus (siehe das dritte
# Beispiel in novaberg-salienz-berechnung_k.md §5).
#
# `GegenpolAnordnungTest` in tests/test_hash_raeder.py haelt die Paare fest.
RAD_ZUG_RUNTER: dict[str, float] = {
    "selbstbezogen":  0.08,   # kehrt zu ihren eigenen Themen zurueck
    "gleichgueltig":  0.10,   # seine Belange beruehren sie nicht
    "widerspenstig":  0.12,   # widerspricht, lenkt ab, folgt ungern
    "distanz":        0.03,   # haelt ihn auf Abstand
    "langeweile":     0.05,   # fremde Themen ermueden sie
    "misstrauen":     0.02,   # legt Gesagtes skeptisch aus
}

# Rad ohne jede Auspraegung — ergibt rechnerisch exakt die Nabe. Dient als
# Spalten-Default, damit eine frisch angelegte Zeile denselben Beleg traegt
# wie eine destillierte: die 0.9 ist dann nachrechenbar statt behauptet.
RAD_LEER: dict[str, dict[str, float]] = {
    "hoch":   {name: 0.0 for name in RAD_ZUG_HOCH},
    "runter": {name: 0.0 for name in RAD_ZUG_RUNTER},
}


# ─────────────────────────────────────────────
# Initiative-Rad — Versatz der Fuehrungsachse
# ─────────────────────────────────────────────
# Zehn Speichen um eine Nabe bei 0.0. Dieselbe Bauart wie oben, andere Frage:
# nicht "wie sehr gilt ihr das Gegenueber", sondern "ueberlaesst sie ihm die
# Fuehrung oder behaelt sie sie".
#
# **Entwurfsregel (Konzept §6.1): Handlung statt Haltung.** Das Rad darueber
# beschreibt Treue als "stellt seine Belange ueber die eigenen" — eine
# Haltung, aus der ein LLM leicht allgemeine Freundlichkeit liest. Jede
# Speiche hier nennt stattdessen eine beobachtbare Gespraechshandlung. Davon
# haengt ab, ob zehn Fragen zehn verschiedene Dinge messen oder zehnmal
# denselben Gesamteindruck.
#
# Volle Auslenkung trifft +/-INITIATIVE_RAD_SPANNE exakt; die Summen sind
# deshalb symmetrisch und je 0.25.
INITIATIVE_ZUG_HOCH: dict[str, float] = {
    "folgsamkeit":       0.08,   # uebernimmt das gesetzte Thema, ohne es zu drehen
    "anschlussfreude":   0.06,   # greift den letzten Punkt auf statt einen neuen zu setzen
    "zurueckhaltung":    0.05,   # bringt Eigenes erst, wenn danach gefragt wird
    "antwortende_rolle": 0.04,   # versteht ihren Beitrag als Antwort, nicht als eigenen daneben
    "behutsamkeit":      0.02,   # vermeidet Brueche, wechselt nicht abrupt weg
}

INITIATIVE_ZUG_RUNTER: dict[str, float] = {
    "lenkungsdrang":      0.08,  # fuehrt auf eine Erkenntnis hin, setzt die Route
    "eigensinn":          0.06,  # hat eigene Themen und bringt sie ungefragt ein
    "assoziationsdrang":  0.05,  # springt quer, oeffnet Nebenwege
    "widerspruchsfreude": 0.04,  # haelt dagegen, korrigiert, stellt in Frage
    "gespraechsdistanz":  0.02,  # geht nicht mit, haelt den Faden auf Abstand
}

INITIATIVE_RAD_LEER: dict[str, dict[str, float]] = {
    "hoch":   {name: 0.0 for name in INITIATIVE_ZUG_HOCH},
    "runter": {name: 0.0 for name in INITIATIVE_ZUG_RUNTER},
}

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
    # `presence_penalty` steht hier und nicht im Modelfile, aus demselben
    # Grund wie die Temperatur eine Zeile darueber: Das Modelfile gilt fuer
    # jeden Aufrufer des CPU-Modells, und Recherche und Lagebeurteilung sind
    # freie Textarbeit — fuer die empfiehlt der Hersteller 1.5. Die
    # Destillation ist es nicht: Sie fuellt feste Felder und liest am Ende ein
    # JSON mit zwoelf Schluesseln, also eine praezise Aufgabe, fuer die 0.0
    # empfohlen ist. Ein Modelfile-Wert haette beide zugleich gestellt.
    #
    # Und er steht hier, damit die Rad-Messreihe ihn mitschreiben kann: Ein
    # Herkunftsfeld, dessen Wert der Code nicht selbst setzt, faellt beim
    # naechsten Modelfile-Edit still auseinander.
    response = model_service.background.submit_sync(BackgroundRequest(
        messages          = [{"role": "user", "content": prompt}],
        modus             = "sprache",
        temperature       = node_cfg.get("temperature", 0.2),
        presence_penalty  = node_cfg.get("presence_penalty", 0.0),
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


INITIATIVE_RAD_PROMPT: str = """Du bist ein Gespraechsanalytiker. Vor dir liegt
ein Persoenlichkeitsprofil und ein Beziehungsprofil.

[PROFIL]
{profil}

[AUFGABE]
Bewerte zehn Gespraechs-Verhaltensweisen danach, wie stark sie in diesem
Profil erkennbar sind. Es geht ausschliesslich darum, WER IM GESPRAECH DIE
RICHTUNG SETZT — nicht um Freundlichkeit, Kompetenz oder Zuwendung.

Bewerte, was die Person TUT, nicht wie sie IST. Eine warmherzige Person kann
das Gespraech fest fuehren; eine distanzierte kann jedem Thema folgen.

Gib je Verhalten genau einen von drei Werten:
  0.0  = nicht erkennbar
  0.5  = angedeutet
  1.0  = ausgepraegt

Ueberlaesst die Fuehrung:
- folgsamkeit       — uebernimmt das gesetzte Thema, ohne es zu drehen
- anschlussfreude   — greift den letzten Punkt auf und spinnt ihn weiter, statt einen neuen zu setzen
- zurueckhaltung    — bringt Eigenes erst, wenn danach gefragt wird
- antwortende_rolle — versteht den eigenen Beitrag als Antwort, nicht als Beitrag daneben
- behutsamkeit      — vermeidet Brueche, wechselt nicht abrupt weg

Behaelt die Initiative:
- lenkungsdrang      — fuehrt auf eine Erkenntnis hin, setzt die Route
- eigensinn          — hat eigene Themen und bringt sie ungefragt ein
- assoziationsdrang  — springt quer, verknuepft Entferntes, oeffnet Nebenwege
- widerspruchsfreude — haelt dagegen, korrigiert, stellt in Frage
- gespraechsdistanz  — geht nicht mit, haelt den Faden auf Abstand

Ein Verhalten kann auch dann ausgepraegt sein, wenn sein Gegenstueck es
ebenfalls ist — jemand kann anschlussfreudig UND widerspruchsfreudig sein.

Steht im Profil nichts ueber das Gespraechsverhalten, bewerte alle zehn mit
0.0. Rate nicht aus dem allgemeinen Eindruck.

Antworte AUSSCHLIESSLICH mit diesem JSON, ohne erklaerenden Text:
{{"hoch": {{"folgsamkeit": 0.0, "anschlussfreude": 0.0, "zurueckhaltung": 0.0, "antwortende_rolle": 0.0, "behutsamkeit": 0.0}}, "runter": {{"lenkungsdrang": 0.0, "eigensinn": 0.0, "assoziationsdrang": 0.0, "widerspruchsfreude": 0.0, "gespraechsdistanz": 0.0}}}}
"""


CHARAKTER_RAD_PROMPT: str = """Du bist ein psychologischer Profiler. Vor dir liegt
ein Persoenlichkeitsprofil und ein Beziehungsprofil.

[PROFIL]
{profil}

[AUFGABE]
Bewerte zwoelf Eigenschaften danach, wie stark sie in diesem Profil erkennbar
sind. Es geht ausschliesslich um die Haltung GEGENUEBER DEM ANDEREN — nicht um
allgemeine Charakterstaerke.

Gib je Eigenschaft genau einen von drei Werten:
  0.0  = nicht erkennbar
  0.5  = angedeutet
  1.0  = ausgepraegt

Zuwendung zum Anderen:
- treue            — stellt die Belange des Anderen ueber die eigenen
- dienst           — sucht von sich aus Gelegenheiten zu helfen
- pflicht          — nimmt Auftraege ernst, auch ungeliebte
- aufmerksamkeit   — registriert Nebensaetze, behaelt Details
- wissbegier       — fremde Themen wecken echtes Interesse
- wohlwollen       — legt Gesagtes im besten Sinne aus

Abwendung vom Anderen:
- widerspenstig    — widerspricht, lenkt ab, folgt ungern
- gleichgueltig    — die Belange des Anderen beruehren nicht
- selbstbezogen    — kehrt zu den eigenen Themen zurueck
- langeweile       — fremde Themen ermueden
- distanz          — haelt den Anderen auf Abstand
- misstrauen       — legt Gesagtes skeptisch aus

Eine Eigenschaft kann auch dann ausgepraegt sein, wenn ihr Gegenstueck es
ebenfalls ist — jemand kann widerspenstig UND wissbegierig sein.

Antworte AUSSCHLIESSLICH mit diesem JSON, ohne erklaerenden Text:
{{"hoch": {{"treue": 0.0, "dienst": 0.0, "pflicht": 0.0, "aufmerksamkeit": 0.0, "wissbegier": 0.0, "wohlwollen": 0.0}}, "runter": {{"widerspenstig": 0.0, "gleichgueltig": 0.0, "selbstbezogen": 0.0, "langeweile": 0.0, "distanz": 0.0, "misstrauen": 0.0}}}}
"""


def nutzer_gewichtung_berechnen(rad: dict) -> float:
    """Rechnet aus den zwoelf Speichen den Gewichtungsfaktor.

    Reine Funktion: Dieselben Eingaben liefern immer denselben Wert, und der
    Wert haengt an keiner Stelle von einem frueheren Ergebnis ab
    (novaberg-convention-abgeleitete-werte.md, Regel 2 und 3).

    Vorbedingung: `rad` traegt die Schluessel 'hoch' und 'runter' mit je genau
        den Speichen aus RAD_ZUG_HOCH bzw. RAD_ZUG_RUNTER. Jede Auspraegung
        liegt zwischen 0.0 und 1.0.
    Nachbedingung: Rueckgabe liegt in [RAD_MIN, RAD_MAX].
    Fehlerfaelle: fehlende oder unbekannte Speiche, nicht-numerische oder
        ausserhalb liegende Auspraegung — ValueError. Ein unvollstaendiges Rad
        ist nicht rechenbar, und ein halb gerechneter Faktor waere schlimmer
        als keiner.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(rad, dict):
        raise ValueError(f"Charakter-Rad: erwartet dict, bekam {type(rad).__name__}")

    for seite, zuege in (("hoch", RAD_ZUG_HOCH), ("runter", RAD_ZUG_RUNTER)):
        werte = rad.get(seite)
        if not isinstance(werte, dict):
            raise ValueError(f"Charakter-Rad: Seite '{seite}' fehlt oder ist kein dict")

        fehlend: set[str] = set(zuege) - set(werte)
        fremd:   set[str] = set(werte) - set(zuege)
        if fehlend or fremd:
            raise ValueError(
                f"Charakter-Rad: Seite '{seite}' unvollstaendig — "
                f"fehlend={sorted(fehlend)}, unbekannt={sorted(fremd)}"
            )

        for name, auspraegung in werte.items():
            if not isinstance(auspraegung, (int, float)) or isinstance(auspraegung, bool):
                raise ValueError(
                    f"Charakter-Rad: '{seite}.{name}' ist nicht numerisch "
                    f"({type(auspraegung).__name__})"
                )
            if not 0.0 <= float(auspraegung) <= 1.0:
                raise ValueError(
                    f"Charakter-Rad: '{seite}.{name}' = {auspraegung} liegt "
                    f"ausserhalb von 0.0–1.0"
                )

    # ── Verarbeitung ────────────────────────────
    zug_hoch:   float = sum(float(rad["hoch"][n])   * z for n, z in RAD_ZUG_HOCH.items())
    zug_runter: float = sum(float(rad["runter"][n]) * z for n, z in RAD_ZUG_RUNTER.items())
    roh:        float = RAD_NABE + zug_hoch - zug_runter

    # ── Ausgabe-Verifikation ────────────────────
    # Volle Auslenkung trifft die Grenzen exakt; die Kappung ist Sicherung,
    # kein Formteil. Greift sie doch, ist eine Auspraegung ausser Rand geraten
    # — das gehoert benannt, nicht stillschweigend weggeschnitten.
    gekappt: float = max(RAD_MIN, min(RAD_MAX, roh))
    if abs(gekappt - roh) > 1e-9:
        logger.warning(
            f"Charakter-Rad: Faktor {roh:.4f} ausserhalb [{RAD_MIN}, {RAD_MAX}] "
            f"— gekappt auf {gekappt:.4f}. Zuege pruefen."
        )

    logger.debug(
        f"Charakter-Rad: Nabe {RAD_NABE} + {zug_hoch:.4f} - {zug_runter:.4f} "
        f"= {gekappt:.4f}"
    )
    return gekappt


def charakter_rad_destillieren(
    profil_text: str,
    user_id:     str = DEFAULT_USER_ID,
) -> tuple[dict, float] | None:
    """Erhebt die zwoelf Speichen aus dem Profiltext und rechnet den Faktor.

    Laeuft NACH den fuenf Profilen und liest deren Ergebnis, nicht erneut das
    KZG — das Rad ist eine Eigenschaft des destillierten Charakters, keine
    zweite Beobachtung der Rohdaten.

    Vorbedingung: `profil_text` ist nicht leer.
    Nachbedingung: (rad, faktor) mit vollstaendigem Rad und faktor in
        [RAD_MIN, RAD_MAX] — oder None.
    Fehlerfaelle: leerer Profiltext, unlesbares JSON, unvollstaendiges Rad.
        In allen Faellen None und eine error-Zeile; der Aufrufer behaelt dann
        den bestehenden Wert, statt einen erfundenen zu schreiben.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not profil_text or not profil_text.strip():
        logger.error(
            f"Charakter-Rad ({user_id}): Profiltext leer — nicht erhoben, "
            f"bestehender Faktor bleibt"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    roh: str = _llm_call(
        CHARAKTER_RAD_PROMPT.format(profil=profil_text),
        f"Charakter-Rad ({user_id})",
    )

    try:
        rad: dict = json.loads(roh)
    except (json.JSONDecodeError, TypeError) as fehler:
        logger.exception(
            f"Charakter-Rad ({user_id}): Antwort ist kein JSON "
            f"({type(fehler).__name__}) — nicht erhoben. Roh: '{roh[:120]}'"
        )
        return None

    try:
        faktor: float = nutzer_gewichtung_berechnen(rad)
    except ValueError as fehler:
        # Die ValueError-Meldung nennt die fehlende Speiche; sie gehoert auf die
        # Zeile, nicht nur in den Traceback. Ein Test prueft darauf.
        logger.exception(
            f"Charakter-Rad ({user_id}): {fehler} — nicht erhoben"  # noqa: TRY401  — Blatt-Typ
        )
        return None

    # ── Ausgabe ─────────────────────────────────
    logger.info(f"Charakter-Rad ({user_id}) erhoben: nutzer_gewichtung={faktor:.4f}")
    return rad, faktor


def initiative_versatz_berechnen(rad: dict) -> float:
    """Rechnet aus den zehn Speichen den Initiative-Versatz.

    Reine Funktion nach demselben Muster wie `nutzer_gewichtung_berechnen`:
    Dieselben Eingaben liefern immer denselben Wert, und der Wert haengt an
    keiner Stelle von einem frueheren Ergebnis ab
    (novaberg-convention-abgeleitete-werte.md, Regel 2 und 3).

    Vorbedingung: `rad` traegt 'hoch' und 'runter' mit je genau den Speichen
        aus INITIATIVE_ZUG_HOCH bzw. INITIATIVE_ZUG_RUNTER; jede Auspraegung
        liegt in [0.0, 1.0].
    Nachbedingung: Rueckgabe in [-INITIATIVE_RAD_SPANNE, +INITIATIVE_RAD_SPANNE].
        Volle Auslenkung trifft die Grenze exakt.
    Fehlerfaelle: fehlende oder unbekannte Speiche, nicht-numerische oder
        ausserhalb liegende Auspraegung — ValueError. Ein unvollstaendiges Rad
        wird abgelehnt, nicht ergaenzt: Eine fehlende Speiche als 0.0 zu
        ergaenzen hiesse, eine nicht gestellte Frage als beantwortet zu buchen.

    Returns:
        Der Versatz, der den Initiative-Rohwert verschiebt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(rad, dict):
        raise ValueError(f"Initiative-Rad: kein Dict ({type(rad).__name__})")

    for seite, erwartet in (("hoch", INITIATIVE_ZUG_HOCH),
                            ("runter", INITIATIVE_ZUG_RUNTER)):
        werte = rad.get(seite)
        if not isinstance(werte, dict):
            raise ValueError(f"Initiative-Rad: Seite '{seite}' fehlt oder ist kein Dict")

        fehlend: set = set(erwartet) - set(werte)
        fremd:   set = set(werte) - set(erwartet)
        if fehlend or fremd:
            raise ValueError(
                f"Initiative-Rad: Seite '{seite}' unvollstaendig — "
                f"fehlend={sorted(fehlend)}, unbekannt={sorted(fremd)}"
            )

        for name, auspraegung in werte.items():
            if not isinstance(auspraegung, (int, float)) or isinstance(auspraegung, bool):
                raise ValueError(
                    f"Initiative-Rad: '{seite}.{name}' ist nicht numerisch "
                    f"({type(auspraegung).__name__})"
                )
            if not 0.0 <= float(auspraegung) <= 1.0:
                raise ValueError(
                    f"Initiative-Rad: '{seite}.{name}' = {auspraegung} liegt "
                    f"ausserhalb von 0.0-1.0"
                )

    # ── Verarbeitung ────────────────────────────
    zug_hoch:   float = sum(float(rad["hoch"][n])   * z for n, z in INITIATIVE_ZUG_HOCH.items())
    zug_runter: float = sum(float(rad["runter"][n]) * z for n, z in INITIATIVE_ZUG_RUNTER.items())
    roh:        float = INITIATIVE_RAD_NABE + zug_hoch - zug_runter

    # ── Ausgabe-Verifikation ────────────────────
    gekappt: float = max(-INITIATIVE_RAD_SPANNE, min(INITIATIVE_RAD_SPANNE, roh))
    if abs(gekappt - roh) > 1e-9:
        logger.warning(
            f"Initiative-Rad: Versatz {roh:.4f} ausserhalb "
            f"+/-{INITIATIVE_RAD_SPANNE} — gekappt auf {gekappt:.4f}. Zuege pruefen."
        )

    logger.info(
        f"Initiative-Rad: Nabe {INITIATIVE_RAD_NABE} + {zug_hoch:.4f} "
        f"- {zug_runter:.4f} = {gekappt:+.4f}"
    )
    return gekappt


def _initiative_rad_einmal(profil_text: str, user_id: str) -> tuple[dict, float] | None:
    """Eine einzelne Erhebung des Initiative-Rads.

    Vorbedingung: `profil_text` ist nicht leer (vom Aufrufer geprueft).
    Nachbedingung: (rad, versatz) oder None.
    Fehlerfaelle: unlesbares JSON, unvollstaendiges Rad — beide laut, beide
        None. Der Aufrufer zaehlt die Ausfaelle und entscheidet.

    Returns:
        (Rad, Versatz) oder None.
    """
    # ── Verarbeitung ────────────────────────────
    roh: str = _llm_call(
        INITIATIVE_RAD_PROMPT.format(profil=profil_text),
        f"Initiative-Rad ({user_id})",
    )

    try:
        rad: dict = json.loads(roh)
    except (json.JSONDecodeError, TypeError) as fehler:
        logger.exception(
            f"Initiative-Rad ({user_id}): Antwort ist kein JSON "
            f"({type(fehler).__name__}). Roh: '{roh[:120]}'"
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    try:
        versatz: float = initiative_versatz_berechnen(rad)
    except ValueError as fehler:
        logger.exception(
            f"Initiative-Rad ({user_id}): {fehler}"  # noqa: TRY401  — Blatt-Typ
        )
        return None

    return rad, versatz


def initiative_rad_destillieren(
    profil_text: str,
    user_id:     str = DEFAULT_USER_ID,
    laeufe:      int = INITIATIVE_RAD_LAEUFE,
    lauf_melden: Callable[[int, dict, float], None] | None = None,
) -> tuple[dict, float] | None:
    """Erhebt das Initiative-Rad mehrfach und nimmt den Median.

    Laeuft wie das erste Rad NACH den fuenf Profilen und liest deren Ergebnis,
    nicht erneut das KZG — der Versatz ist eine Eigenschaft des destillierten
    Charakters, keine zweite Beobachtung der Rohdaten.

    **Warum mehrfach.** Gemessen am 29.07.2026: Zwei Laeufe gegen denselben
    Charaktertext bei Temperatur 0.2 ergaben -0.18 und -0.13. Die Richtung war
    beide Male eindeutig, der Betrag nicht — und genau der geht in die Achse
    ein. Anders als ein Turn-Wert wird der Versatz nicht ueber viele Turns
    gemittelt: Er wird bei der Destillation einmal geschrieben und bleibt bis
    zur naechsten stehen.

    **Zurueckgegeben wird das Rad des Median-Laufs**, nicht ein gemitteltes Rad.
    Ein Durchschnitt aus drei Raedern ergaebe Auspraegungen wie 0.67, die kein
    Lauf je vergeben hat — und der Zusammenhang `Rad x Zuege = Versatz` waere
    nicht mehr von Hand nachrechenbar. Die Streuung reist als Metadatum mit.

    **Was der Aufrufer daraus macht, ist seine Sache.** Seit dem 01.08.2026
    legt er die Einzellaeufe in die Messreihe und speichert ein ueber Tage
    stabilisiertes Rad (novaberg-charakter-rad-messreihe_k.md). Der Grund fuer
    "ein echtes Rad" faellt damit an dieser Stelle weg: Die Laeufe, aus denen
    es entsteht, bleiben einzeln erhalten — nur eben in der Messreihe statt im
    Rueckgabewert.

    Args:
        lauf_melden: wird nach jedem **gelungenen** Lauf mit (Nummer, Rad,
            Versatz) gerufen. Der Rueckgabewert wird nicht gelesen.
            **Vertrag: Die Senke wirft nicht** — eine Ausnahme aus ihr wuerde
            die Destillation abbrechen, und ein Forensik-Ziel darf einen
            Charakterlauf nicht toeten.

    Vorbedingung: `profil_text` ist nicht leer, `laeufe` >= 1.
    Nachbedingung: (rad, versatz) — das Rad traegt zusaetzlich 'laeufe' und
        'streuung'; versatz ist der Median der gelungenen Erhebungen und liegt
        in [-INITIATIVE_RAD_SPANNE, +INITIATIVE_RAD_SPANNE].
    Fehlerfaelle: leerer Profiltext oder **keine** gelungene Erhebung — dann
        None und eine error-Zeile; der Aufrufer behaelt den bestehenden Wert,
        statt einen erfundenen zu schreiben. Teilausfaelle sind kein Fehler,
        werden aber benannt und stehen in 'laeufe'.

    Returns:
        (Rad mit Metadaten, Median-Versatz) oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not profil_text or not profil_text.strip():
        logger.error(
            f"Initiative-Rad ({user_id}): Profiltext leer — nicht erhoben, "
            f"bestehender Versatz bleibt"
        )
        return None

    if laeufe < 1:
        logger.error(
            f"Initiative-Rad ({user_id}): laeufe={laeufe} ist kleiner als 1 — "
            f"nicht erhoben"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    erhebungen: list[tuple[dict, float]] = []
    for nummer in range(1, laeufe + 1):
        ergebnis = _initiative_rad_einmal(profil_text, user_id)
        if ergebnis is None:
            logger.error(
                f"Initiative-Rad ({user_id}): Lauf {nummer}/{laeufe} "
                f"gescheitert — zaehlt nicht mit"
            )
            continue
        erhebungen.append(ergebnis)
        if lauf_melden is not None:
            lauf_melden(nummer, ergebnis[0], ergebnis[1])

    if not erhebungen:
        logger.error(
            f"Initiative-Rad ({user_id}): alle {laeufe} Laeufe gescheitert — "
            f"nicht erhoben, bestehender Versatz bleibt"
        )
        return None

    # Median ueber die Versaetze; bei gerader Anzahl der untere der beiden
    # mittleren, damit ein ECHTES Rad gespeichert werden kann und nicht ein
    # gemitteltes, das kein Lauf vergeben hat.
    erhebungen.sort(key=lambda paar: paar[1])
    rad, versatz = erhebungen[(len(erhebungen) - 1) // 2]

    werte:    list[float] = [v for _, v in erhebungen]
    streuung: float       = max(werte) - min(werte)

    # ── Ausgabe-Verifikation ────────────────────
    rad = dict(rad)
    rad["laeufe"]   = [round(v, 4) for v in werte]
    rad["streuung"] = round(streuung, 4)

    if len(erhebungen) < laeufe:
        logger.error(
            f"Initiative-Rad ({user_id}): nur {len(erhebungen)} von {laeufe} "
            f"Laeufen gelungen — der Median steht auf duennerer Grundlage"
        )

    if versatz == 0.0:
        logger.info(
            f"Initiative-Rad ({user_id}): Versatz 0.0000 — die Speichen heben "
            f"sich auf oder das Profil sagt ueber Gespraechsfuehrung nichts. "
            f"Das gespeicherte Rad sagt, welcher der beiden Faelle vorliegt."
        )

    logger.info(
        f"Initiative-Rad ({user_id}) erhoben: versatz={versatz:+.4f} "
        f"(Median aus {len(erhebungen)} Laeufen: "
        f"{[f'{v:+.4f}' for v in werte]}, Streuung {streuung:.4f})"
    )
    return rad, versatz


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
        logger.exception(f"{type(fehler).__name__}: Ziel-Destillation fehlgeschlagen für {user_id}")
        return []
