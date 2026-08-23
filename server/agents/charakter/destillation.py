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
    ASSISTANT_GENUS,
    ASSISTANT_NAME,
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    get_node_config,
    PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE,
    RAD_NABE,
    RAD_MIN,
    RAD_MAX,
    INITIATIVE_RAD_NABE,
    INITIATIVE_RAD_SPANNE,
    INITIATIVE_RAD_LAEUFE,
    ZUWENDUNG_RAD_LAEUFE,
)
from services.model_services import model_service, BackgroundRequest
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.charakter.destillation")


# ─────────────────────────────────────────────
# Zeitgewicht des Adaptiv-Hash
# ─────────────────────────────────────────────
# Eine Quelle fuer Auswahl und Beschriftung. Bis zum 16.08.2026 rechnete nur
# die Destillation ein Gewicht — und schrieb es als Zahl in den Prompt, ohne
# dass es die Auswahl beruehrte. Die Auswahl nahm, was SCAN zuerst lieferte.
# Gemessen am produktiven Paar: 12 von 19 Eintraegen im Prompt waren 15 bis 20
# Tage alt und trugen ein Gewicht unter 0.09.


def zeitgewicht(alter_tage: float) -> float:
    """Gewicht eines KZG-Eintrags nach seinem Alter — stetig, ohne Kante.

    Vorbedingung: `alter_tage` ist nicht negativ. Ein negativer Wert hiesse,
        der Eintrag stammt aus der Zukunft; er wird auf 0 geklemmt, weil ein
        Gewicht ueber 1 die Ordnung gegen jede juengere Zeile kippen wuerde.
    Nachbedingung: Ergebnis in (0, 1]. 1.0 bei Alter 0, 0.5 nach einer
        Halbwertszeit; streng monoton fallend, nirgends springend.

    Die Form ist die kanonische Verfallsform des Systems — dieselbe wie in
    `memory/ziele.py` (`exp(-ln2/HWZ * t)`) und `memory/lzg_knoten.py`. Die
    abgeloeste Fassung setzte drei Stuecke aneinander (konstant, linear,
    exponentiell) und sprang dabei bei genau einem Tag von 1.00 auf 0.80: Zwei
    Eintraege, die eine Minute trennte, unterschieden sich um ein Fuenftel.
    """
    # ── Eingabe-Validierung ──
    if alter_tage < 0:
        logger.warning(
            f"zeitgewicht: negatives Alter {alter_tage:.4f} Tage — "
            f"auf 0 geklemmt (Eintrag aus der Zukunft?)"
        )
        alter_tage = 0.0

    if PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE <= 0:
        raise ValueError(
            f"zeitgewicht: Halbwertszeit "
            f"{PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE} Tage ist nicht "
            f"positiv — ohne sie hat der Verfall keine Skala"
        )

    # ── Verarbeitung ──
    zerfallsrate: float = math.log(2) / PIXIE_CHARAKTER_ADAPTIV_HALBWERTSZEIT_TAGE
    gewicht: float = math.exp(-zerfallsrate * alter_tage)

    # ── Ausgabe-Verifikation ──
    if not 0.0 < gewicht <= 1.0:
        raise ValueError(
            f"zeitgewicht: Gewicht {gewicht} liegt ausserhalb (0, 1] bei "
            f"Alter {alter_tage} Tagen — die Ordnung waere nicht mehr gueltig"
        )

    return gewicht


def alterszone(alter_tage: float) -> str:
    """Benennt das Alter fuer den Prompt — AKUT, PHASE oder TREND.

    Vorbedingung: `alter_tage` ist eine Zahl; negative gelten als frisch.
    Nachbedingung: einer der drei Namen, die `ADAPTIVE_HASH_PROMPT` erklaert.

    Die Zone beschreibt **wie alt**, das Gewicht **wie stark**. Bis zum
    16.08.2026 war beides dasselbe Stueckwerk, und die Kante zwischen zwei
    Zonen war zugleich ein Sprung im Gewicht.
    """
    if alter_tage <= 1:
        return "AKUT"
    if alter_tage <= 7:
        return "PHASE"
    return "TREND"


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
spricht, worauf {traeger} achtet, was {traeger_dat} wichtig ist, wie
{traeger} mit anderen umgeht — das dauerhafte Wesen dahinter.

Entscheidend: Die Einträge handeln oft von anderen Dingen oder Personen. Das
ist gleichgültig. Nicht WORÜBER {traeger} spricht charakterisiert
{traeger_akk}, sondern WIE. Wer beim Beschreiben eines Sonnenuntergangs ins Schwärmen gerät,
offenbart eine poetische, empfindsame Ader — unabhängig vom Sonnenuntergang
selbst.

Beschreibe das dauerhafte Wesen {traeger_gen} auf Deutsch. Tiefenwerte,
dauerhafte Interessen, Denkweise, Grundhaltung. Zeitlos — keine
Tagesstimmung, keine aktuellen Projekte.

Nimm dir den Raum, den der Gegenstand braucht. Verdichte nicht: Behalte die
Wendungen, den Ton und das Beilaeufige, an dem man {traeger_akk} erkennt. Ein
Beispiel im Wortlaut sagt mehr als ein Urteil darueber.

Einträge:
{eintraege}

Schreibe ueber {traeger_akk} durchgehend mit den Pronomen {pronomen} und
{possessiv}. Das grammatische Geschlecht steht damit fest.

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

Erstelle ein kompaktes Profil der aktuellen Verfassung {traeger_gen} in 2-4
Sätzen auf Deutsch.

Einträge:
{eintraege}

Schreibe ueber {traeger_akk} durchgehend mit den Pronomen {pronomen} und
{possessiv}. Das grammatische Geschlecht steht damit fest.

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

INTENTIONS_PROFIL_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegen Langzeit-Erinnerungen aus {perspektive} Blickwinkel — so wie
{traeger} sich mitteilt und mit anderen umgeht.

Deine Aufgabe ist nicht, die Einträge zusammenzufassen, sondern zu deuten:
Was verrät die ART der Kommunikation über {traeger_akk}? Lies drei Ebenen
heraus
— STIL (Satzbau, Formalität, Wortwahl, Humor), MODUS (in welchem Register
{traeger} denkt: fachlich, philosophisch, alltäglich), INTENTION (was
{traeger} typischerweise erreichen will).

Nicht WORÜBER geredet wird, sondern WIE. Wer knappe, präzise Sätze ohne
Floskeln wählt, offenbart einen anderen Charakter als jemand, der ausschweift
und ausschmückt — unabhängig vom Thema.

Erstelle ein kompaktes Kommunikations-Profil {traeger_gen} in 3-5 Sätzen auf
Deutsch. Beschreibe den Charakter hinter der Sprache, nicht die Statistik.

Einträge:
{eintraege}

Schreibe ueber {traeger_akk} durchgehend mit den Pronomen {pronomen} und
{possessiv}. Das grammatische Geschlecht steht damit fest.

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

EMOTIONS_PROFIL_PROMPT: str = """Du bist ein erfahrener psychologischer Profiler.
Vor dir liegen emotionale Signale aus Langzeit-Erinnerungen, aus {perspektive}
Blickwinkel — so wie {traeger} fühlt und emotional reagiert.

Deine Aufgabe ist nicht aufzuzählen, welche Gefühle vorkamen, sondern die
emotionale Signatur dahinter zu erschließen — wie ein Psychiater das
Temperament liest. Zwei Ebenen: GRUNDTENDENZ (welche Emotionen
{traeger_akk} langfristig tragen, welche Muster) und VOLATILITÄT (stabile Grundstimmung
oder sprunghafte Umschwünge — die Emotions-Vektoren als Hinweis: häufig
Spirale/Absturz = volatil, häufig Plateau = stabil).

Erstelle ein kompaktes emotionales Profil {traeger_gen} in 3-5 Sätzen auf
Deutsch.

Einträge:
{eintraege}

Schreibe ueber {traeger_akk} durchgehend mit den Pronomen {pronomen} und
{possessiv}. Das grammatische Geschlecht steht damit fest.

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

Schreibe ueber {traeger_akk} durchgehend mit den Pronomen {pronomen} und
{possessiv}. Das grammatische Geschlecht steht damit fest.

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


def rad_klemmen(rad: dict, rad_name: str) -> dict:
    """Holt Auspraegungen ausserhalb [0.0, 1.0] an ihren Rand zurueck.

    **Die Gegenleistung zur weggefallenen Rundungsvorgabe** (11.08.2026).
    Solange die Prompts »auf eine Nachkommastelle« verlangten, kam ein Wert
    ausserhalb der Spanne praktisch nicht vor. Ohne Raster ist eine 1.02
    wahrscheinlicher — und sie kostete bisher das **ganze** Rad, weil
    `nutzer_gewichtung_berechnen` sie als `ValueError` abweist und der
    Aufrufer die Erhebung verwirft. Zwoelf Urteile wegen einer zweiten
    Stelle wegzuwerfen ist der teurere Fehler.

    **Geklemmt wird laut.** Jede Korrektur bekommt ihre Zeile mit Speiche
    und Ausgangswert. Ein Modell, das regelmaessig ueber den Rand schreibt,
    soll sichtbar bleiben, statt in geglaetteten Zahlen zu verschwinden —
    und die Klemme darf nicht zu der stillen Korrektur werden, gegen die
    `22_STILLE_FEHLER.md` steht.

    Nicht-Zahlen bleiben unberuehrt: Sie sind kein Randfall, sondern ein
    kaputtes Rad, und gehoeren in die Ablehnung eine Stufe weiter.

    Args:
        rad:      geparste Modellantwort, Form {seite: {speiche: wert}}.
        rad_name: fuer die Logzeile, damit sie das Rad benennt.

    Returns:
        Ein neues Rad derselben Form. Die Eingabe bleibt unveraendert.
    """
    if not isinstance(rad, dict):
        return rad

    geklemmt: dict = {}
    for seite, werte in rad.items():
        if not isinstance(werte, dict):
            geklemmt[seite] = werte
            continue
        neue_seite: dict = {}
        for speiche, wert in werte.items():
            if isinstance(wert, bool) or not isinstance(wert, (int, float)):
                neue_seite[speiche] = wert
                continue
            rand: float = min(1.0, max(0.0, float(wert)))
            if rand != float(wert):
                logger.warning(
                    f"{rad_name}: Auspraegung von '{speiche}' war {wert} und "
                    f"liegt ausserhalb [0.0, 1.0] — auf {rand} geklemmt"
                )
            neue_seite[speiche] = rand
        geklemmt[seite] = neue_seite
    return geklemmt


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
    # Die Frist steht an der Aufrufstelle und nicht am Worker, aus demselben
    # Grund wie Temperatur und Penalty zwei Zeilen weiter unten: Der
    # Vorgabewert `MODEL_BACKGROUND_TIMEOUT_S = 300` gilt fuer **jeden**
    # Hintergrund-Aufrufer, und die Recherche braucht eine andere Zahl als
    # die Destillation.
    #
    # **Sie ist grosszuegig gesetzt, und das ist eine Entscheidung** und kein
    # Schaetzwert: Die Destillation darf die Zeit brauchen, die sie braucht.
    # Der offene Prompt erzeugt rund
    # fuenfmal so viel Text wie der gedeckelte; gemessen wurden 3288 Zeichen
    # und rund 18 Minuten fuer Kern und Rad zusammen, bei einem einzelnen
    # Rad-Aufruf von rund 8 Minuten. 300 s haetten den Aufruf sicher
    # abgebrochen — und ein Abbruch dauert dieselbe Zeit und hat nichts.
    #
    # Der Wert ist eine Obergrenze, kein Ziel: Ein Aufruf, der frueher fertig
    # ist, kostet nicht mehr. Eine genauere Zerlegung steht aus
    # (`labor/werkzeug/offen_frist_probe.py`, gebaut und nicht gefahren).
    response = model_service.background.submit_sync(BackgroundRequest(
        messages          = [{"role": "user", "content": prompt}],
        modus             = "sprache",
        temperature       = node_cfg.get("temperature", 0.2),
        presence_penalty  = node_cfg.get("presence_penalty", 0.0),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "pixie/hash",
    ), timeout=node_cfg.get("timeout_s", 1800))

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


# Die Beugung der Pronomen je grammatischem Geschlecht. Sie steht als Tabelle
# und nicht als Verzweigung, weil jede kuenftige Prompt-Zeile eine Form
# brauchen kann, die heute keine benutzt — ein `if` je Form waere fuenf
# Verzweigungen an fuenf Stellen.
_PRONOMEN: dict[str, dict[str, str]] = {
    "w": {"pronomen": "sie", "pronomen_dat": "ihr",  "pronomen_akk": "sie", "possessiv": "ihr"},
    "m": {"pronomen": "er",  "pronomen_dat": "ihm",  "pronomen_akk": "ihn", "possessiv": "sein"},
    "n": {"pronomen": "es",  "pronomen_dat": "ihm",  "pronomen_akk": "es",  "possessiv": "sein"},
}

# Die Formen des generischen Rollenbegriffs. »der Nutzer« ist grammatisch
# maskulin; das ist eine Aussage ueber das Wort, nicht ueber den Menschen
# dahinter, und deshalb steht hier eine feste Tabelle und keine Erhebung.
_ROLLE_NUTZER: dict[str, str] = {
    "traeger":     "der Nutzer",
    "traeger_gen": "des Nutzers",
    "traeger_dat": "dem Nutzer",
    "traeger_akk": "den Nutzer",
    "perspektive": "des Nutzers",
}

# Jede Form, die ein Prompt einsetzen darf. Die Ausgabe-Verifikation haelt die
# Rueckgabe dagegen: Ein fehlender Schluessel ist im `format()` ein KeyError
# mitten im Destillationslauf, hier eine Zeile vor dem Aufruf.
_TRAEGERFORMEN: tuple[str, ...] = (
    "traeger", "traeger_gen", "traeger_dat", "traeger_akk", "perspektive",
    "pronomen", "pronomen_dat", "pronomen_akk", "possessiv", "genus_quelle",
)


def _perspektive_aufloesen(user_id: str) -> dict[str, str]:
    """Loest aus der Subjekt-ID alle Traeger-Formen fuer die Prompts.

    beobachter/Subjekt == ASSISTANT_USER_ID -> Assistent (Name aus
    ASSISTANT_NAME, Genus aus ASSISTANT_GENUS); sonst -> generischer Nutzer
    (feste Formen, grammatisch maskulin).

    **Vollstaendig, nicht sparsam** (22.08.2026). Bis dahin lieferte die
    Funktion drei Formen — Nominativ, Genitiv und die Genitiv-Form fuer »aus
    X Blickwinkel« — und zwang damit zwei Fehler, die beide gemessen sind:

    - **Kein Dativ.** Vier der fuenf Profil-Prompts setzen den Traeger hinter
      »von« ein und lasen dadurch bei jedem menschlichen Paar »ein Profil von
      *der Nutzer*« (`PERSPEKTIVE-OHNE-DATIV`, 11.08.2026).
    - **Kein Pronomen.** Sobald ein Satz eins braucht, entscheidet das Modell
      — am 18.08.2026 im selben Lauf verschieden: der Kern-Hash fuehrte fuer
      den Traeger »Juno« durchgehend »er«, das Beziehungsprofil im Schlusssatz
      das saechliche (`PROFILPROMPT-OHNE-GESCHLECHT`).

    Eigennamen bleiben im Dativ und Akkusativ unflektiert; deshalb tragen die
    beiden Formen dort denselben Wert wie der Nominativ.

    Args:
        user_id: die Subjekt-ID, deren Perspektive destilliert wird.

    Returns:
        Alle Formen aus `_TRAEGERFORMEN`. `genus_quelle` sagt, woher das
        grammatische Geschlecht stammt (`konfiguration`, `rollenbegriff` oder
        `rueckfall`) — ein Genus, das aus einem Rueckfall stammt, ist von
        einem gesetzten sonst nicht unterscheidbar.
    """
    # ── Verarbeitung ──
    if user_id == ASSISTANT_USER_ID:
        name: str = ASSISTANT_NAME
        genus: str = (ASSISTANT_GENUS or "").strip().lower()
        quelle: str = "konfiguration"
        if genus not in _PRONOMEN:
            logger.error(
                "_perspektive_aufloesen: ASSISTANT_GENUS=%r ist keins von %s "
                "— die Prompts bekommen die Pronomen des Rueckfalls 'w'",
                ASSISTANT_GENUS, sorted(_PRONOMEN),
            )
            genus, quelle = "w", "rueckfall"
        aufloesung: dict[str, str] = {
            "traeger":     name,
            "traeger_gen": _genitiv_bilden(name),
            "traeger_dat": name,
            "traeger_akk": name,
            "perspektive": _genitiv_bilden(name),
            "genus_quelle": quelle,
            **_PRONOMEN[genus],
        }
    else:
        aufloesung = {
            **_ROLLE_NUTZER,
            "genus_quelle": "rollenbegriff",
            **_PRONOMEN["m"],
        }

    # ── Ausgabe-Verifikation ──
    fehlend: list[str] = [form for form in _TRAEGERFORMEN if not aufloesung.get(form)]
    if fehlend:
        raise ValueError(
            f"_perspektive_aufloesen: Formen ohne Wert fuer user_id={user_id}: "
            f"{fehlend} — ein Prompt, der eine davon einsetzt, bricht im Lauf"
        )

    # ── Ausgabe ──
    logger.debug(
        "_perspektive_aufloesen: user_id=%s -> traeger=%s, pronomen=%s (%s)",
        user_id, aufloesung["traeger"], aufloesung["pronomen"],
        aufloesung["genus_quelle"],
    )
    return aufloesung


def kern_hash_destillieren(turn_eintraege: list[dict], user_id: str = DEFAULT_USER_ID) -> str:
    """Destilliert die Grundpersoenlichkeit aus dem **Wortlaut** der Turns.

    **Der Prompt verlangt es woertlich.** `KERN_HASH_PROMPT` sagt: »Erschliesse
    aus dem WIE — wie {traeger} spricht, worauf {traeger} achtet« und schaerft
    nach: »Nicht WORUEBER {traeger} spricht charakterisiert {traeger}, sondern
    WIE.« Bis zum 10.08.2026 bekam er Langzeit-Knoten, also genau das
    Worueber: Aus »jo« ist dort »Der Nutzer weiss nicht, was er hier tun soll«
    geworden. Wie jemand spricht, ist daran nicht mehr ablesbar — die
    Satzlaenge nicht, die Kleinschreibung nicht, der Scherz nicht.

    **Gegenstand ist die eigene Seite.** Fuer das Profil des Menschen seine
    Aeusserungen, fuer das der Figur ihre Antworten — nie beide. Die Vorgabe
    stand seit je im Konzept (§6: »Gleicher Mechanismus, getrennte Daten«);
    der Umbau vom 10.08.2026 hat sie verloren, als er eine Quelle **mit**
    Perspektivfilter (`_lzg_kern_laden(user, character, beobachter)`) durch
    eine **ohne** ersetzte (`_turns_laden(user_id)`). Drei Argumente wurden zu
    einem, und der Filter verschwand mit dem dritten.

    Vorbedingung: Eintraege mit `aeusserung` und `antwort`.
    Nachbedingung: Profiltext oder "". Leere Eingabe wird gemeldet, nicht
        stillschweigend als leeres Profil zurueckgegeben — ebenso der Fall,
        dass Begegnungen vorliegen, aber keine mit einem Beitrag des Traegers.
    """
    if not turn_eintraege:
        logger.error(
            f"Kern-Hash ({user_id}): kein Wortlaut vorhanden — kein Profil"
        )
        return ""

    perspektive: dict[str, str] = _perspektive_aufloesen(user_id)
    traeger: str = perspektive["traeger"]
    traeger_gen: str = perspektive["traeger_gen"]

    # Gegenstand ist **die eigene Seite**, und sie traegt den Namen des
    # Traegers. Bis zum 16.08.2026 bekamen beide Perspektiven denselben Text
    # mit beiden Sprechern; unterschieden wurden sie allein durch die
    # Anweisung, und die ist 1,4 % des Prompts. Gemessen am produktiven Paar:
    # 90,5 % des Materials stammte von der Figur (Faktor 9,5), und der Traeger
    # "der Nutzer" kam im Material **null mal** vor — der Mensch stand dort nur
    # als "Gegenueber", ein relativer Begriff, dessen Bezugspunkt die Anweisung
    # gerade verschiebt. Der Traeger im Text macht ihn auffindbar.
    feld: str = "antwort" if user_id == ASSISTANT_USER_ID else "aeusserung"
    zeilen: list[str] = [
        f"  {traeger}: „{(row.get(feld) or '').strip()}“"
        for row in turn_eintraege
        if (row.get(feld) or "").strip()
    ]

    if not zeilen:
        logger.error(
            f"Kern-Hash ({user_id}): {len(turn_eintraege)} Begegnungen, aber "
            f"keine einzige mit einem Beitrag {traeger_gen} — kein Profil"
        )
        return ""

    eintraege: str = "\n".join(zeilen)
    logger.info(
        f"Kern-Hash ({user_id}): {len(zeilen)} Beitraege {traeger_gen}, "
        f"{len(eintraege)} Zeichen"
    )

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
    ohne_themen: int = 0

    for eintrag in kzg_eintraege:
        themen: str = eintrag.get("themen", "")
        if not themen:
            # Frueher ein stilles `continue`: Der Aufrufer sah 20 geladene
            # Eintraege und wusste nicht, dass weniger im Prompt landeten.
            ohne_themen += 1
            continue

        inhalt:   str   = eintrag.get("inhalt", "")
        salienz:  float = float(eintrag.get("salienz", 0))
        erstellt: float = float(eintrag.get("erstellt_am", 0))

        alter_tage: float = (jetzt - erstellt) / 86400

        gewicht:           float = zeitgewicht(alter_tage)
        effektive_salienz: float = salienz * gewicht

        zonen_eintraege.append(
            f"[{alterszone(alter_tage)}] (Salienz: {effektive_salienz:.2f}) "
            f"{themen}: {inhalt}"
        )

    # Die Zahl gehoert in den Verlauf, nicht nur ins Ergebnis: Ohne sie ist
    # "wenig Material" von "viel Material, davon das meiste verworfen" nicht
    # zu unterscheiden.
    logger.info(
        f"Adaptive-Hash ({user_id}): {len(zonen_eintraege)} von "
        f"{len(kzg_eintraege)} Eintraegen im Prompt, "
        f"{ohne_themen} ohne Themen verworfen"
    )

    if not zonen_eintraege:
        logger.error(
            f"Adaptive-Hash ({user_id}): kein einziger von "
            f"{len(kzg_eintraege)} Eintraegen war brauchbar — Profil bleibt leer"
        )
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


def wortlaut_holen(kzg_schluessel: list[str]) -> dict[str, dict[str, str]]:
    """Holt zu KZG-Schluesseln den Wortlaut ihrer Turns.

    Der Weg ist `verbindung.kzg_id` -> `verbindung.turn_id` ->
    `pipeline_log` mit `art = 'turn_roh'`. Die Tabelle fuehrt ihn seit jeher;
    fuer das Beziehungsprofil hat ihn nie jemand benutzt.

    **Impulse bleiben draussen.** Ein eigener Impuls legt seinen Text in
    dasselbe Feld `user_prompt` wie eine Nutzeraeusserung; ungefiltert kaeme
    er hier als Aeusserung des Gegenuebers zurueck — im Profil der Figur also
    ihr eigener Monolog als Rede des Menschen. Gemessen am 17.08.2026: **591
    von 744 rueckverfolgbaren KZG-Verweisen des produktiven Paares stammen aus
    Impuls-Turns**, im Fenster der letzten zwei Tage 86 von 122.
    `IS DISTINCT FROM` statt `<>`, damit ein Turn ohne Marke erhalten bleibt —
    er ist nicht nachweislich ein Impuls.

    Vorbedingung: nichtleere Liste von Schluesseln.
    Nachbedingung: Abbildung Schluessel -> {'aeusserung', 'antwort'}. Ein
        Schluessel ohne Verbindung **oder aus einem Impuls** fehlt in der
        Rueckgabe — der Aufrufer entscheidet, was das bedeutet, und meldet es.
    """
    if not kzg_schluessel:
        return {}

    zeilen: list[dict] = db_manager.select(
        """
        SELECT v.kzg_id,
               p.inhalt ->> 'user_prompt' AS aeusserung,
               p.inhalt ->> 'response'    AS antwort
        FROM verbindung v
        JOIN pipeline_log p
          ON p.turn_id = v.turn_id AND p.art = 'turn_roh'
        WHERE v.kzg_id = ANY(%s)
          AND p.inhalt ->> 'herkunft' IS DISTINCT FROM 'eigener_impuls'
        """,
        (kzg_schluessel,),
    ) or []

    return {
        z["kzg_id"]: {"aeusserung": z["aeusserung"] or "",
                      "antwort":    z["antwort"] or ""}
        for z in zeilen
    }


def beziehungsprofil_destillieren(kzg_eintraege: list[dict], user_id: str = DEFAULT_USER_ID) -> str:
    """Destilliert das Beziehungsprofil aus dem **Wortlaut** der Turns.

    **Warum nicht mehr aus dem KZG-Inhalt.** Der Prompt fragt nach NAEHE —
    Anrede, Kosenamen, Ton. Der KZG-Inhalt ist bereits eine Aussage in der
    dritten Person: aus »jo« wird »Der Nutzer weiss nicht, was er hier tun
    soll«. Die Anrede ueberlebt diese Umwandlung nicht, und mit ihr der
    ganze Gegenstand der Frage. Gemessen am 09.08.2026: `distanz` stand in
    jeder Zelle eines Kreuzversuchs auf 1.00 — bei beiden Materialien und
    beiden Etiketten. Das Rad hat nicht die Beziehung gelesen, sondern die
    Tonlage eines Aktenauszugs.

    Die Metadaten stehen weiterhin dabei, aber als Beiwerk. Ein `tone:
    sachlich` ist die fertige Charakterisierung; wer den Umgang deuten
    soll, braucht den Satz, an dem sie haengt, nicht das Urteil darueber.

    Nachbedingung: Profiltext oder "". Findet sich zu **keinem** Eintrag ein
        Wortlaut, wird das als Fehler gemeldet und nicht auf die
        Zusammenfassung zurueckgefallen — ein stiller Rueckfall ergaebe
        denselben Defekt mit einem Umweg und saehe wie ein Ergebnis aus.
    """
    if not kzg_eintraege:
        return ""

    schluessel: list[str] = [e["_key"] for e in kzg_eintraege if e.get("_key")]
    ohne_schluessel: int = len(kzg_eintraege) - len(schluessel)
    if ohne_schluessel:
        logger.error(
            f"Beziehungsprofil: {ohne_schluessel} von {len(kzg_eintraege)} "
            "KZG-Eintraegen ohne '_key' — fuer sie ist der Wortlaut nicht "
            "erreichbar"
        )

    wortlaute: dict[str, dict[str, str]] = wortlaut_holen(schluessel)

    beziehungs_eintraege: list[str] = []
    for eintrag in kzg_eintraege:
        wortlaut = wortlaute.get(eintrag.get("_key", ""))
        if not wortlaut or not (wortlaut["aeusserung"] or wortlaut["antwort"]):
            continue

        kopf: str = (
            f"[Modus: {eintrag.get('modus', '')}, "
            f"Emotion: {eintrag.get('emotion', '')}, "
            f"Dynamik: {eintrag.get('beziehungs_dynamik', '')}, "
            f"Tone: {eintrag.get('tone', '')}]"
        )
        # **Beide Sprecher tragen ihren Namen, nicht ihre Rolle.** Anders als
        # beim Kern sind hier beide Seiten noetig — der Prompt fragt nach
        # NAEHE, und Anrede ist relational. Was nicht bleiben darf, ist das
        # relative "Gegenueber": Sein Bezugspunkt ist die Figur, waehrend der
        # Traeger im Prompt wechselt. Fuer das Profil des Menschen bezeichnete
        # dasselbe Wort damit ihn selbst, fuer ihres seinen Gespraechspartner.
        beziehungs_eintraege.append(
            f"{kopf}\n"
            f"  der Nutzer: „{wortlaut['aeusserung']}“\n"
            f"  {ASSISTANT_NAME}: „{wortlaut['antwort']}“"
        )

    if not beziehungs_eintraege:
        logger.error(
            f"Beziehungsprofil ({user_id}): zu keinem von "
            f"{len(kzg_eintraege)} KZG-Eintraegen ist ein Wortlaut "
            "erreichbar — kein Profil. Kein Rueckfall auf den KZG-Inhalt: "
            "der traegt die Anrede nicht, nach der der Prompt fragt"
        )
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

Gib je Verhalten einen Wert zwischen 0.0 und 1.0. Runde nicht — die Zahl
darf so fein sein, wie dein Urteil es hergibt. Die drei Marken bleiben als
Anhalt:
  0.0  = nicht erkennbar
  0.5  = angedeutet
  1.0  = ausgepraegt
Zwischenwerte sind ausdruecklich erlaubt und erwuenscht: 0.72 heisst
"deutlich mehr als angedeutet, aber nicht durchgaengig".

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

Gib je Eigenschaft einen Wert zwischen 0.0 und 1.0. Runde nicht — die Zahl
darf so fein sein, wie dein Urteil es hergibt. Die drei Marken bleiben als
Anhalt:
  0.0  = nicht erkennbar
  0.5  = angedeutet
  1.0  = ausgepraegt
Zwischenwerte sind ausdruecklich erlaubt und erwuenscht: 0.72 heisst
"deutlich mehr als angedeutet, aber nicht durchgaengig".

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


def _zuwendung_rad_einmal(
    profil_text: str,
    user_id:     str = DEFAULT_USER_ID,
) -> tuple[dict, float] | None:
    """Erhebt die zwoelf Speichen EINMAL und rechnet den Faktor.

    Laeuft NACH den fuenf Profilen und liest deren Ergebnis, nicht erneut das
    KZG — das Rad ist eine Eigenschaft des destillierten Charakters, keine
    zweite Beobachtung der Rohdaten.

    Der einzelne Lauf; die Wiederholung steht in
    `charakter_rad_destillieren`. Getrennt, damit die Schleife dieselbe
    Gestalt hat wie beim Initiative-Rad und beide Raeder von derselben
    Stelle aus zu lesen sind.

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

    rad = rad_klemmen(rad, f"Charakter-Rad ({user_id})")

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


def charakter_rad_destillieren(
    profil_text: str,
    user_id:     str = DEFAULT_USER_ID,
    laeufe:      int = ZUWENDUNG_RAD_LAEUFE,
    lauf_melden: Callable[[int, dict, float], None] | None = None,
) -> tuple[dict, float] | None:
    """Erhebt das Zuwendungs-Rad mehrfach und nimmt den Median.

    **Warum mehrfach — und warum erst seit dem 11.08.2026.** Das
    Initiative-Rad wird seit dem 29.07.2026 dreimal erhoben; die Begruendung
    steht in `config.py` und gilt fuer dieses Rad woertlich genauso: Der Wert
    wird bei der Destillation EINMAL geschrieben und bleibt bis zur naechsten
    stehen, ein unglueklicher Lauf legte ihn sonst fuer Tage fest. Dass die
    Ueberlegung auf das Zuwendungs-Rad nie angewandt wurde, war eine Luecke
    und keine Entscheidung — und sie traf das Rad, das jeder Turn liest,
    waehrend das seltener gelesene geschuetzt war.

    **Zurueckgegeben wird das Rad des Median-Laufs**, nicht ein gemitteltes.
    Dieselbe Wahl wie beim Initiative-Rad: Ein Durchschnitt aus drei Raedern
    ergaebe Auspraegungen, die kein Lauf vergeben hat, und der Zusammenhang
    `Rad x Zuege = Faktor` waere nicht mehr von Hand nachrechenbar. Die
    Streuung reist als Metadatum mit.

    Args:
        lauf_melden: wird nach jedem **gelungenen** Lauf mit (Nummer, Rad,
            Faktor) gerufen — die Senke fuer die Messreihe.
            **Vertrag: Die Senke wirft nicht.** Eine Ausnahme aus ihr wuerde
            die Destillation abbrechen, und ein Forensik-Ziel darf einen
            Charakterlauf nicht toeten.

    Vorbedingung: `profil_text` ist nicht leer, `laeufe` >= 1.
    Nachbedingung: (rad, faktor) — das Rad traegt zusaetzlich 'laeufe',
        'streuung', 'speichen_median' und 'speichen_ohne_mehrheit'; der Faktor
        ist der Median der gelungenen Erhebungen und wird **allein** aus dem
        Median-Lauf-Rad gerechnet, nie aus den speichenweisen Medianen.
    Fehlerfaelle: **keine** gelungene Erhebung — dann None und eine
        error-Zeile; der Aufrufer behaelt den bestehenden Wert. Teilausfaelle
        sind kein Fehler, werden aber benannt und stehen in 'laeufe'.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Der leere Profiltext wird HIER abgefangen und nicht erst im Einzellauf:
    # sonst liefe die Schleife dreimal ins Leere und erzeugte vier Fehlerzeilen
    # fuer einen Fehler. Dieselbe Reihenfolge wie beim Initiative-Rad.
    if not profil_text or not profil_text.strip():
        logger.error(
            f"Charakter-Rad ({user_id}): Profiltext leer — nicht erhoben, "
            f"bestehender Faktor bleibt"
        )
        return None

    if laeufe < 1:
        logger.error(
            f"Charakter-Rad ({user_id}): laeufe={laeufe} ist kleiner als 1 — "
            f"nicht erhoben"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    erhebungen: list[tuple[dict, float]] = []
    for nummer in range(1, laeufe + 1):
        ergebnis = _zuwendung_rad_einmal(profil_text, user_id)
        if ergebnis is None:
            logger.error(
                f"Charakter-Rad ({user_id}): Lauf {nummer}/{laeufe} "
                f"gescheitert — zaehlt nicht mit"
            )
            continue
        erhebungen.append(ergebnis)
        if lauf_melden is not None:
            lauf_melden(nummer, ergebnis[0], ergebnis[1])

    if not erhebungen:
        logger.error(
            f"Charakter-Rad ({user_id}): alle {laeufe} Laeufe gescheitert — "
            f"nicht erhoben, bestehender Faktor bleibt"
        )
        return None

    # Median ueber die Faktoren; bei gerader Anzahl der untere der beiden
    # mittleren, damit ein ECHTES Rad gespeichert wird.
    erhebungen.sort(key=lambda paar: paar[1])
    rad, faktor = erhebungen[(len(erhebungen) - 1) // 2]

    werte:    list[float] = [f for _, f in erhebungen]
    streuung: float       = max(werte) - min(werte)

    # ── Ausgabe-Verifikation ────────────────────
    rad = dict(rad)
    rad["laeufe"]   = [round(w, 4) for w in werte]
    rad["streuung"] = round(streuung, 4)

    # Der Median je Speiche, neben dem Rad des Median-Laufs und ohne zu
    # rechnen (23.08.2026). Der Median-Lauf wird ueber den Faktor gewaehlt;
    # eine einzelne Speiche kann darin einen Wert tragen, den die Mehrheit
    # ihrer eigenen Laeufe nicht stuetzt, und nichts sagte es dem Leser.
    rad["speichen_median"] = speichenweise_mediane([r for r, _ in erhebungen])
    ohne_mehrheit: list[str] = speichen_ohne_mehrheit(rad, rad["speichen_median"])
    rad["speichen_ohne_mehrheit"] = ohne_mehrheit

    if ohne_mehrheit:
        logger.info(
            f"Charakter-Rad ({user_id}): {len(ohne_mehrheit)} Speiche(n) ohne "
            f"Mehrheit hinter ihrem Wert — {ohne_mehrheit}; der Faktor bleibt "
            f"der des Median-Laufs (F-RAD-2)"
        )

    if len(erhebungen) < laeufe:
        logger.error(
            f"Charakter-Rad ({user_id}): nur {len(erhebungen)} von {laeufe} "
            f"Laeufen gelungen — der Median steht auf duennerer Grundlage"
        )

    logger.info(
        f"Charakter-Rad ({user_id}) erhoben: nutzer_gewichtung={faktor:.4f} "
        f"(Median aus {len(erhebungen)} Laeufen: "
        f"{[f'{w:.4f}' for w in werte]}, Streuung {streuung:.4f})"
    )
    return rad, faktor


def speichenweise_mediane(erhebungen: list[dict]) -> dict[str, dict[str, float]]:
    """Der Median **je Speiche** ueber alle gelungenen Laeufe.

    **Warum das neben dem Median-Lauf-Rad steht und es nicht ersetzt.**
    `F-RAD-2` legt fest, dass das Rad des Median-Laufs gespeichert wird, und
    die Begruendung traegt: Ein gemitteltes Rad erzeugte Auspraegungen, die
    kein Lauf vergeben hat, und `Rad x Zuege = Faktor` waere nicht mehr von
    Hand nachrechenbar. Der Median-Lauf wird aber ueber den **Faktor**
    bestimmt, nicht je Speiche — und damit kann eine einzelne Speiche einen
    Wert tragen, den die Mehrheit ihrer eigenen Laeufe nicht stuetzt.

    `[gemessen]` — 19.08.2026 ueber drei Laeufe: Beim Initiative-Rad traf das
    **5 von 10** Speichen. `behutsamkeit` stand auf 0,60, waehrend zwei von
    drei Laeufen 0,40 sagten; `gespraechsdistanz` auf 0,10 bei Median 0,20.
    Beim Zuwendungsrad **0 von 12** — dort sind die stark ziehenden Speichen
    zeichengleich.

    **Dieses Feld rechnet nicht.** Es traegt keinen Faktor und keinen Versatz;
    es beantwortet allein die Frage eines Lesers, der eine einzelne Speiche
    ansieht: *steht hinter diesem Wert eine Mehrheit?* Wer daraus einen Faktor
    rechnete, haette genau das gemittelte Rad, das `F-RAD-2` ausschliesst.

    Bei gerader Anzahl wird der **untere** der beiden mittleren Werte genommen
    — dieselbe Wahl wie bei der Auswahl des Median-Laufs, damit beide Zahlen
    aus derselben Regel stammen und nicht zufaellig auseinanderlaufen.

    Vorbedingung: `erhebungen` ist nicht leer, und jedes Rad traegt 'hoch' und
    'runter' mit denselben Speichennamen.
    Nachbedingung: dieselbe zweistufige Gestalt wie ein Rad, mit je einem Wert
    auf vier Nachkommastellen. Eine Speiche, die nicht in jedem Lauf vorkommt,
    wird ueber die Laeufe gemittelt, in denen sie vorkam — sie fehlen zu lassen
    machte ihr Fehlen unsichtbar.

    Args:
        erhebungen: die Raeder aller gelungenen Laeufe, in Lauf-Reihenfolge.

    Returns:
        Abbildung Seite -> Speiche -> Median.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not erhebungen:
        meldung = (
            "speichenweise_mediane: keine Erhebungen — ein Median ueber die "
            "leere Menge waere kein Wert, sondern eine Erfindung"
        )
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    mediane: dict[str, dict[str, float]] = {}
    for seite in ("hoch", "runter"):
        gesammelt: dict[str, list[float]] = {}
        for rad in erhebungen:
            for name, wert in (rad.get(seite) or {}).items():
                gesammelt.setdefault(name, []).append(float(wert))
        mediane[seite] = {}
        for name, werte in gesammelt.items():
            werte.sort()
            mediane[seite][name] = round(werte[(len(werte) - 1) // 2], 4)

    # ── Ausgabe-Verifikation ────────────────────
    if not mediane["hoch"] and not mediane["runter"]:
        meldung = (
            f"speichenweise_mediane: {len(erhebungen)} Erhebung(en) ergaben "
            f"keine einzige Speiche — die Raeder tragen weder 'hoch' noch "
            f"'runter', und ein leeres Feld saehe aus wie Einigkeit"
        )
        raise ValueError(meldung)

    return mediane


def flache_reihe_als_raeder(
    reihe:  list[dict[str, float]],
    muster: dict,
) -> list[dict]:
    """Hebt flach abgelegte Messungen in die zweistufige Gestalt eines Rades.

    **Zwei Gestalten fuer denselben Gegenstand, und jeder Verbraucher muss
    beide kennen.** Die Destillation fuehrt ein Rad als `{"hoch": …,
    "runter": …}`; `charakter_rad_messung.speichen` und damit auch
    `reihe_laden` legen es **flach** ab (`{"treue": 0.85, …}`). Wer nur eine
    kennt, bekommt von der anderen null Speichen — und null sieht aus wie
    Einigkeit, nicht wie ein Lesefehler.

    `[gemessen]` — 23.08.2026: Genau so meldete ein Messwerkzeug 0 Speichen
    ueber 95 Erhebungen und einen Anteil von 0,0 %.

    Welche Speiche auf welche Seite gehoert, sagt das **Muster** und nicht eine
    zweite Liste: Die flache Ablage traegt die Zuordnung nicht mehr, und eine
    eigene Aufzaehlung liefe gegen die des Rades.

    Vorbedingung: `muster` traegt 'hoch' und 'runter'. Eine Messung darf
    Speichen fehlen lassen — sie fehlen dann auch im Ergebnis, statt mit einem
    erfundenen Wert aufzutauchen.
    Nachbedingung: je Messung ein Rad in der zweistufigen Gestalt, in der
    Reihenfolge der Eingabe. Speichen, die das Muster nicht kennt, entfallen.

    Args:
        reihe:  die Messungen, je ein Abbild Speichenname -> Wert.
        muster: ein Rad, dessen Seiten die Zuordnung tragen.

    Returns:
        Dieselben Messungen, zweistufig.
    """
    # ── Eingabe-Validierung ─────────────────────
    seiten: dict[str, set[str]] = {
        seite: set(muster.get(seite) or {}) for seite in ("hoch", "runter")
    }
    if not seiten["hoch"] and not seiten["runter"]:
        meldung = (
            "flache_reihe_als_raeder: das Muster traegt weder 'hoch' noch "
            "'runter' — ohne Zuordnung waere jedes Ergebnis leer, und leer "
            "sieht aus wie Einigkeit"
        )
        raise ValueError(meldung)

    # ── Verarbeitung / Ausgabe ──────────────────
    return [
        {
            seite: {
                name: float(wert) for name, wert in messung.items()
                if name in namen
            }
            for seite, namen in seiten.items()
        }
        for messung in reihe
    ]


def speichen_ohne_mehrheit(rad: dict, mediane: dict) -> list[str]:
    """Nennt die Speichen, deren gespeicherter Wert nicht ihr Median ist.

    Die Zahl, die den Befund belegbar macht: Ohne sie sagt das Medianfeld,
    *dass* es einen zweiten Wert gibt, aber nicht, *wo* die beiden auseinander
    liegen.

    Vorbedingung: beide tragen dieselbe zweistufige Gestalt.
    Nachbedingung: `seite.speiche` je Abweichung, sortiert; leer heisst, jeder
    gespeicherte Wert ist zugleich der Median seiner Laeufe.

    Args:
        rad:     das gespeicherte Rad des Median-Laufs.
        mediane: die speichenweisen Mediane.

    Returns:
        Die Namen der abweichenden Speichen.
    """
    # ── Verarbeitung / Ausgabe ──────────────────
    return sorted(
        f"{seite}.{name}"
        for seite in ("hoch", "runter")
        for name, wert in (mediane.get(seite) or {}).items()
        if round(float((rad.get(seite) or {}).get(name, wert)), 4) != round(wert, 4)
    )


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

    rad = rad_klemmen(rad, f"Initiative-Rad ({user_id})")

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
    Nachbedingung: (rad, versatz) — das Rad traegt zusaetzlich 'laeufe',
        'streuung', 'speichen_median' und 'speichen_ohne_mehrheit'; versatz ist
        der Median der gelungenen Erhebungen, wird **allein** aus dem
        Median-Lauf-Rad gerechnet und liegt in
        [-INITIATIVE_RAD_SPANNE, +INITIATIVE_RAD_SPANNE].
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

    # Dasselbe wie beim Zuwendungsrad, und aus demselben Grund: Der Median-Lauf
    # wird ueber den Versatz gewaehlt, nicht je Speiche. Am 19.08.2026 traf das
    # hier 5 von 10 Speichen — beim Zuwendungsrad keine einzige.
    rad["speichen_median"] = speichenweise_mediane([r for r, _ in erhebungen])
    ohne_mehrheit: list[str] = speichen_ohne_mehrheit(rad, rad["speichen_median"])
    rad["speichen_ohne_mehrheit"] = ohne_mehrheit

    if ohne_mehrheit:
        logger.info(
            f"Initiative-Rad ({user_id}): {len(ohne_mehrheit)} Speiche(n) ohne "
            f"Mehrheit hinter ihrem Wert — {ohne_mehrheit}; der Versatz bleibt "
            f"der des Median-Laufs (F-RAD-2)"
        )

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
            messages         = [{"role": "user", "content": prompt}],
            modus            = "analyse",
            temperature      = 0.3,
            # Wie bei den fuenf Profil-Aufrufen: `expect_json=True` macht
            # daraus eine praezise Aufgabe, und fuer die empfiehlt der
            # Hersteller 0.0 statt der 1.5 des Modelfiles. Dieser Aufruf war
            # am 09.08.2026 der einzige, der beim alten Wert stehenblieb —
            # er ruft nicht ueber `_llm_call`, sondern direkt.
            presence_penalty = 0.0,
            expect_json      = True,
            caller           = "charakter/ziele",
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
