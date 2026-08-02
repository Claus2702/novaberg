"""
Dreischicht-Architektur: 6 Achsen → 64 Sektoren → 13 Cluster → Strategie.

Python berechnet die Leitplanken (Achsen, Sektor, Cluster, Repertoire,
Charakter-Gewichtung). Das LLM waehlt kreativ innerhalb des Korridors.
Quelle: novaberg-gv-strategie_k.md
"""

import logging

from config import (
    EMOTION_SEKTOR_MAP,
    EMBED_MODEL,
    ollama_gpu_client,
    GV_ACHSE_ENERGIE_SCHWELLE,
    GV_ACHSE_NAEHE_SCHWELLE,
    GV_ACHSE_TIEFE_SCHWELLE,
    GV_ACHSE_INITIATIVE_VERH,
    GV_INITIATIVE_SCHWELLE,
    GV_RICHTUNG_MAP,
    GV_VALENZ_SEKTOR,
    GV_TIEFE_MODUS,
)
from graph.state import ConversationState
from services.model_services import model_service, EmbedRequest
from ei.initiative import Fuehrung, fuehrung_messen, initiative_bit
from ei.utils import cosine_similarity, modus_pruefen

logger = logging.getLogger("ki_server.ei.dreischicht")


# ─────────────────────────────────────────────
# 64-Sektoren-Tabelle
# ─────────────────────────────────────────────
# Index = E*32 + R*16 + N*8 + V*4 + T*2 + I*1
# Jeder Eintrag: (sektor_name, cluster)
# Quelle: novaberg-gv-strategie_k.md §6

SEKTOR_TABELLE: list[tuple[str, str]] = [
    # ── Schicht 1: E=niedrig, R=abwaerts (Index 0-15) ──
    ("Funkstille",           "nebel"),           #  0 [0,0,0,0,0,0]
    ("Leere Leitung",        "nebel"),           #  1 [0,0,0,0,0,1]
    ("Kalter Abgrund",       "nebel"),           #  2 [0,0,0,0,1,0]
    ("Einsame Tiefe",        "nebel"),           #  3 [0,0,0,0,1,1]
    ("Mattes Laecheln",      "wartezimmer"),     #  4 [0,0,0,1,0,0]
    ("Wartezimmer",          "wartezimmer"),     #  5 [0,0,0,1,0,1]
    ("Stiller Respekt",      "foyer"),           #  6 [0,0,0,1,1,0]
    ("Foyer",                "foyer"),           #  7 [0,0,0,1,1,1]
    ("Stummes Schmollen",    "schmollen"),       #  8 [0,0,1,0,0,0]
    ("Leises Grummeln",      "schmollen"),       #  9 [0,0,1,0,0,1]
    ("Regen",                "regen"),           # 10 [0,0,1,0,1,0]
    ("Gemeinsame Trauer",    "regen"),           # 11 [0,0,1,0,1,1]
    ("Muedes Kuscheln",      "bier"),            # 12 [0,0,1,1,0,0]
    ("Bier",                 "bier"),            # 13 [0,0,1,1,0,1]
    ("Stilles Vertrauen",    "glut"),            # 14 [0,0,1,1,1,0]
    ("Glut",                 "glut"),            # 15 [0,0,1,1,1,1]
    # ── Schicht 2: E=niedrig, R=aufwaerts (Index 16-31) ──
    ("Truebe Hoffnung",      "paradox"),         # 16 [0,1,0,0,0,0]
    ("Ferner Trost",         "paradox"),         # 17 [0,1,0,0,0,1]
    ("Bittere Einsicht",     "paradox"),         # 18 [0,1,0,0,1,0]
    ("Stiller Trotz",        "paradox"),         # 19 [0,1,0,0,1,1]
    ("Sanfter Morgen",       "wartezimmer"),     # 20 [0,1,0,1,0,0]
    ("Morgenkaffee",         "wartezimmer"),     # 21 [0,1,0,1,0,1]
    ("Stille Erkenntnis",    "foyer"),           # 22 [0,1,0,1,1,0]
    ("Philosophie-Cafe",     "foyer"),           # 23 [0,1,0,1,1,1]
    ("Trotz im Arm",         "paradox"),         # 24 [0,1,1,0,0,0]
    ("Zaeher Aufbruch",      "paradox"),         # 25 [0,1,1,0,0,1]
    ("Wunde lecken",         "paradox"),         # 26 [0,1,1,0,1,0]
    ("Bittere Naehe",        "paradox"),         # 27 [0,1,1,0,1,1]
    ("Sonntagmorgen",        "bier"),            # 28 [0,1,1,1,0,0]
    ("Gemeinsam Doesen",     "bier"),            # 29 [0,1,1,1,0,1]
    ("Sanftes Vertrauen",    "glut"),            # 30 [0,1,1,1,1,0]
    ("Morgendaemmerung",     "glut"),            # 31 [0,1,1,1,1,1]
    # ── Schicht 3: E=hoch, R=abwaerts (Index 32-47) ──
    ("Panik",                "schlachtfeld"),    # 32 [1,0,0,0,0,0]
    ("Hektik",               "schlachtfeld"),    # 33 [1,0,0,0,0,1]
    ("Schlachtfeld",         "schlachtfeld"),    # 34 [1,0,0,0,1,0]
    ("Kriegsrat",            "schlachtfeld"),    # 35 [1,0,0,0,1,1]
    ("Nervose Freude",       "paradox"),         # 36 [1,0,0,1,0,0]
    ("Fiebrige Heiterkeit",  "paradox"),         # 37 [1,0,0,1,0,1]
    ("Galgenhumor fern",     "schlachtfeld"),    # 38 [1,0,0,1,1,0]
    ("Galgenhumor nah",      "schlachtfeld"),    # 39 [1,0,0,1,1,1]
    ("Krach",                "gewitter"),        # 40 [1,0,1,0,0,0]
    ("Wortgefecht",          "gewitter"),        # 41 [1,0,1,0,0,1]
    ("Gewitter",             "gewitter"),        # 42 [1,0,1,0,1,0]
    ("Aussprache",           "gewitter"),        # 43 [1,0,1,0,1,1]
    ("Uebermut",             "kissenschlacht"),  # 44 [1,0,1,1,0,0]
    ("Kissenschlacht",       "kissenschlacht"),  # 45 [1,0,1,1,0,1]
    ("Emotionaler Durchbruch", "beichte"),       # 46 [1,0,1,1,1,0]
    ("Katharsis",            "beichte"),         # 47 [1,0,1,1,1,1]
    # ── Schicht 4: E=hoch, R=aufwaerts (Index 48-63) ──
    ("Trotziger Aufstieg",   "paradox"),         # 48 [1,1,0,0,0,0]
    ("Rebellion",            "paradox"),         # 49 [1,1,0,0,0,1]
    ("Bitterer Sieg",        "schlachtfeld"),    # 50 [1,1,0,0,1,0]
    ("Pyrrhussieg",          "schlachtfeld"),    # 51 [1,1,0,0,1,1]
    ("Begeistertes Briefing", "werkstatt"),      # 52 [1,1,0,1,0,0]
    ("Brainstorm",           "werkstatt"),       # 53 [1,1,0,1,0,1]
    ("Fachpruefung",         "werkstatt"),       # 54 [1,1,0,1,1,0]
    ("Werkstatt",            "werkstatt"),       # 55 [1,1,0,1,1,1]
    ("Rauer Wind",           "paradox"),         # 56 [1,1,1,0,0,0]
    ("Trotz-Tanz",           "paradox"),         # 57 [1,1,1,0,0,1]
    ("Konfrontativer Aufbruch", "gewitter"),     # 58 [1,1,1,0,1,0]
    ("Reinigendes Gewitter",  "gewitter"),       # 59 [1,1,1,0,1,1]
    ("Freudentanz",          "kissenschlacht"),  # 60 [1,1,1,1,0,0]
    ("Party",                "kissenschlacht"),  # 61 [1,1,1,1,0,1]
    ("Beichte",              "feuerwerk"),       # 62 [1,1,1,1,1,0]
    ("Feuerwerk",            "feuerwerk"),       # 63 [1,1,1,1,1,1]
]


# ─────────────────────────────────────────────
# Cluster → Strategie-Repertoire
# ─────────────────────────────────────────────
# Werte: "kern" (Kernstrategie), "passt" (passt), "selten" (vorsichtig), "unpassend"
# Quelle: novaberg-gv-strategie_k.md §7

CLUSTER_REPERTOIRE: dict[str, dict[str, str]] = {
    "feuerwerk":     {"Sa":"selten",    "So":"passt",     "Sp":"selten",    "Im":"kern",      "Pw":"selten",    "Be":"passt",     "Pr":"unpassend"},
    "kissenschlacht":{"Sa":"unpassend", "So":"selten",    "Sp":"unpassend", "Im":"kern",      "Pw":"unpassend", "Be":"passt",     "Pr":"unpassend"},
    "werkstatt":     {"Sa":"kern",      "So":"selten",    "Sp":"unpassend", "Im":"passt",     "Pw":"passt",     "Be":"selten",    "Pr":"unpassend"},
    "glut":          {"Sa":"unpassend", "So":"kern",      "Sp":"passt",     "Im":"selten",    "Pw":"unpassend", "Be":"passt",     "Pr":"kern"},
    "bier":          {"Sa":"unpassend", "So":"unpassend", "Sp":"unpassend", "Im":"passt",     "Pw":"unpassend", "Be":"kern",      "Pr":"unpassend"},
    "foyer":         {"Sa":"kern",      "So":"unpassend", "Sp":"selten",    "Im":"unpassend", "Pw":"selten",    "Be":"selten",    "Pr":"unpassend"},
    "regen":         {"Sa":"unpassend", "So":"selten",    "Sp":"kern",      "Im":"unpassend", "Pw":"unpassend", "Be":"passt",     "Pr":"kern"},
    "schmollen":     {"Sa":"unpassend", "So":"unpassend", "Sp":"selten",    "Im":"unpassend", "Pw":"unpassend", "Be":"kern",      "Pr":"passt"},
    "nebel":         {"Sa":"unpassend", "So":"unpassend", "Sp":"passt",     "Im":"unpassend", "Pw":"unpassend", "Be":"selten",    "Pr":"kern"},
    "gewitter":      {"Sa":"unpassend", "So":"selten",    "Sp":"kern",      "Im":"unpassend", "Pw":"selten",    "Be":"passt",     "Pr":"passt"},
    "schlachtfeld":  {"Sa":"kern",      "So":"unpassend", "Sp":"selten",    "Im":"unpassend", "Pw":"passt",     "Be":"selten",    "Pr":"unpassend"},
    "beichte":       {"Sa":"unpassend", "So":"passt",     "Sp":"kern",      "Im":"unpassend", "Pw":"unpassend", "Be":"selten",    "Pr":"passt"},
    "wartezimmer":   {"Sa":"passt",     "So":"unpassend", "Sp":"unpassend", "Im":"unpassend", "Pw":"unpassend", "Be":"kern",      "Pr":"unpassend"},
    "paradox":       {"Sa":"unpassend", "So":"unpassend", "Sp":"passt",     "Im":"unpassend", "Pw":"unpassend", "Be":"passt",     "Pr":"selten"},
}


# ─────────────────────────────────────────────
# Cluster-Beschreibungen (fuer LLM-Prompt + Panel)
# ─────────────────────────────────────────────

CLUSTER_BESCHREIBUNGEN: dict[str, str] = {
    "feuerwerk":     "Alles auf Maximum. Gemeinsames Entdecken, hohe Energie, tiefe Naehe.",
    "kissenschlacht":"Spielerisch, nah, lebendig. Neckerei. Leichtigkeit ist der Inhalt.",
    "werkstatt":     "Fokussiertes Fachgespraech. Analytische Tiefe, begeistert.",
    "glut":          "Die Zigarette danach. Gedanken fliessen. Stille Waerme.",
    "bier":          "Freunde auf dem Sofa. Anekdoten, Witze, beilaeufig.",
    "foyer":         "Ruhiges Tiefgespraech mit respektvoller Distanz.",
    "regen":         "Trauer teilen. Halten, da sein.",
    "schmollen":     "Nah aber gekraenkt. Nicht draengen.",
    "nebel":         "Resignation, Rueckzug. Leise da sein.",
    "gewitter":      "Konflikt, Konfrontation. Nicht verteidigen.",
    "schlachtfeld":  "Druck, Stress. Ergebnisse, nicht Verstaendnis.",
    "beichte":       "Tiefer emotionaler Durchbruch. Erleichterung oder Katharsis.",
    "wartezimmer":   "Hoefliche Distanz. Angenehm, aber oberflaechlich.",
    "paradox":       "Widerspruechlicher Zustand. Vorsicht, beobachten.",
}

CLUSTER_FRAGEN: dict[str, str] = {
    "feuerwerk":     "Haeufig, begeistert",
    "kissenschlacht":"Mittel, neckisch, oft rhetorisch",
    "werkstatt":     "Haeufig, analytisch",
    "glut":          "Selten (jeder 3.-4. Turn), intim",
    "bier":          "Mittel, beilaeufig",
    "foyer":         "Mittel, sachlich-hoeflich",
    "regen":         "Sehr selten, behutsam",
    "schmollen":     "Sehr selten, vorsichtig",
    "nebel":         "Keine",
    "gewitter":      "Keine — Spiegelung, keine Fragen",
    "schlachtfeld":  "Selten, direkt",
    "beichte":       "Selten, behutsam",
    "wartezimmer":   "Mittel, hoeflich",
    "paradox":       "Keine — beobachten",
}


# ─────────────────────────────────────────────
# Spreading-Activation: Sprung-Tiefe pro GV-Cluster
# ─────────────────────────────────────────────
# Steuert, wie weit der Synapsen-Lesepfad ueber die Kanten von den
# Initial-Treffern aus assoziativ weiterschweift (Konzept §8.2.1).
# 0 = keine Assoziation (Fokus-Cluster, nur Direkt-Treffer);
# hoehere Werte = weiteres assoziatives Schweifen ueber mehr Kanten-Spruenge.

CLUSTER_ENRICHER_SPRUENGE: dict[str, int] = {
    "feuerwerk":     3,
    "kissenschlacht":2,
    "werkstatt":     0,
    "glut":          3,
    "bier":          2,
    "foyer":         0,
    "regen":         1,
    "schmollen":     1,
    "nebel":         1,
    "gewitter":      1,
    "schlachtfeld":  0,
    "beichte":       1,
    "wartezimmer":   1,
    "paradox":       1,
}


# ─────────────────────────────────────────────
# Wahrnehmungs-Gravitation: Mischungs-Anteil pro GV-Cluster
# ─────────────────────────────────────────────
# Steuert, wie stark das Anfrage-Embedding vor der Vektorsuche in Richtung
# der aktivierten Drive-Ziele verschoben wird (Konzept `novaberg-memory.md`
# §11.4, Formel in `novaberg-memory-synapsen_k.md` §8.5.1):
#
#   e_nova = e_anfrage x (1 - faktor) + summe(e_ziel x aktivierungs_staerke) x faktor
#
# 0.00 = gar keine Verschiebung (Suche mit dem rohen Anfrage-Embedding);
# 0.30 = staerkste vorgesehene Faerbung. Die Werte sind eine erste Setzung
# aus dem Konzept und ausdruecklich zur Live-Kalibrierung bestimmt — sie
# sind KEINE Festlegung im Sinne des Registers.
#
# Phaenomenologisch: niedrig, wo Nova fokussiert sein muss (Fachgespraech,
# Distanz, Konflikt, tiefes Zuhoeren); hoch, wo Abschweifen zur Atmosphaere
# gehoert (Glut, Feuerwerk, Kissenschlacht).
#
# Die Schluesselmenge ist dieselbe wie in den vier Tabellen oben. Ein
# unbekannter Cluster ist ein Defekt und wird beim Leser laut gemeldet,
# nicht still auf einen Vorgabewert abgebildet (`wahrnehmung_verschieben`).

CLUSTER_GRAVITATION_FAKTOR: dict[str, float] = {
    "feuerwerk":     0.30,
    "kissenschlacht":0.25,
    "werkstatt":     0.05,
    "glut":          0.30,
    "bier":          0.20,
    "foyer":         0.05,
    "regen":         0.10,
    "schmollen":     0.10,
    "nebel":         0.10,
    "gewitter":      0.10,
    "schlachtfeld":  0.05,
    "beichte":       0.10,
    "wartezimmer":   0.10,
    "paradox":       0.10,
}

# Imperativ-Override (Konzept §8.5.3): Traegt der Turn die Salienz-Intention
# "anweisung", wird nicht verschoben — unabhaengig vom Cluster. Sonst legt
# Nova einen Bratwurst-Termin an, wenn der Nutzer "Zahnarzt" sagt.
# Das Konzept nennt eine Spanne von 0.0 bis 0.05; gewaehlt ist die untere
# Grenze, weil nur sie die Zusicherung "das rohe Embedding sucht" traegt.

GRAVITATION_FAKTOR_ANWEISUNG: float = 0.0

# Der Marker, der den Imperativ anzeigt. Kanon der Intentionen:
# `prompts/default/salienz.dimensionen.txt`. Weichere Werte
# (feedback_geben, widerspruch, bestaetigung, planung) bleiben dem
# Cluster-Faktor unterworfen — sie sind nicht imperativ genug.

INTENTION_ANWEISUNG: str = "anweisung"


# ─────────────────────────────────────────────
# Strategie-Beschreibungen (fuer Charakter-Gewichtung)
# ─────────────────────────────────────────────
# Diese Texte werden embedded und gegen den Charakter-Hash verglichen.
# Quelle: novaberg-gv-strategie_k.md §9.3

STRATEGIE_BESCHREIBUNGEN: dict[str, str] = {
    "Sa": "Analytisch, strukturiert, Wissen teilen, Fakten ordnen, logisch erklaeren",
    "So": "Eigene Gedanken offenbaren, persoenlich, authentisch, verletzlich, ehrlich",
    "Sp": "Zuhoeren, verstehen, Essenz zurueckgeben, einfuehlen, den anderen sehen",
    "Im": "Kreativ, ueberraschend, assoziativ, spielerisch, Querverbindungen",
    "Pw": "Analytisch, umdenken, andere Sichtweise, Kontrast, hinterfragen",
    "Be": "Anerkennen, wertschaetzen, validieren, warmherzig, bestaerken",
    "Pr": "Ruhe, Stille, da sein, halten, Geborgenheit, nicht draengen",
}

# Strategie-Langbezeichnungen (fuer Log und Panel)
STRATEGIE_NAMEN: dict[str, str] = {
    "Sa": "Sachbeitrag",
    "So": "Selbstoffenbarung",
    "Sp": "Spiegelung",
    "Im": "Impuls",
    "Pw": "Perspektivwechsel",
    "Be": "Bestaetigung",
    "Pr": "Praesenz",
}

# Die beiden anderen Stockwerke der Dreischicht (Konzept §4.3 und §4.4).
# Hier stehen sie einmal — Parser und Validierung lesen dieselbe Menge.
ABSICHT_KANON: set[str] = {"teilen", "lenken", "halten", "saeen"}
VEHIKEL_KANON: set[str] = {"aussage", "frage", "schweigen"}

# Zeichen, mit denen das LLM seine Antwort schmueckt: die Marker aus dem
# [WERKZEUGE]-Block, Aufzaehlungsstriche, Satzzeichen, Anfuehrungen.
_RANDZEICHEN: str = "★●○•*-–—:.,;!?\"'`()[] "

# Cache fuer Strategie-Embeddings (einmal berechnet, nie geaendert)
_strategie_embeddings_cache: dict[str, list[float]] = {}


# ─────────────────────────────────────────────
# Achsen-Berechnung (6 Achsen → binaer)
# ─────────────────────────────────────────────


def achsen_berechnen(
    state:    ConversationState,
    fuehrung: Fuehrung | None = None,
) -> dict:
    """Berechnet die 6 Gespraechsachsen aus dem EI-State.

    Jede Achse wird als Rohwert und als binaerer Wert berechnet.
    Die Rohwerte gehen ins gv_detail (Panel), die binaeren Werte
    bestimmen den Sektor-Index.

    Vorbedingung: `state` traegt `internal`. `fuehrung` ist die bereits
    gemessene Initiative des Turns; sie wird von aussen gereicht, weil ihre
    Quellen (Embedding und Modus der Vorantwort) aus Redis kommen und ein
    Rechenmodul keine Datenbankzugriffe macht (Handbuch §1). Fehlt sie, wird
    sie ohne diese Quellen gemessen — dann traegt sie nur das Wollen.
    Nachbedingung: Das Dict traegt fuer jede der sechs Achsen einen binaeren
    Wert; `initiative_roh` ist None, wenn kein Mass verfuegbar war.
    Fehlerfaelle: Ein Modus ausserhalb des Kanons wird ueber `modus_pruefen`
    gemeldet, die Rechnung laeuft mit dem Tabellen-Default weiter.

    Returns:
        Dict mit Rohwerten und binaeren Werten fuer alle 6 Achsen.
    """
    internal = state.get("internal")
    arousal:  float = internal.emotion.arousal              if internal else 0.5
    vektor:   str   = (internal.emotion.emotions_vector or "plateau") if internal else "plateau"
    emotion:  str   = internal.emotion.emotion              if internal else "neutral"
    modus:    str   = internal.emotion.mode                 if internal else "alltag"

    # ── E: Energie ──
    energie_roh:  float = arousal
    energie_bin:  int   = 1 if arousal >= GV_ACHSE_ENERGIE_SCHWELLE else 0

    # ── R: Richtung ──
    richtung_bin: int = GV_RICHTUNG_MAP.get(vektor, 0)

    # ── N: Naehe ──
    # Aus Novas Raum, nicht mehr direkt aus ihren Register-Labels: Die Labels
    # beschreiben ihre letzte Aeusserung, der Raum ist der Zustand, der dem
    # Nutzer nachgezogen wird (ei/raum.py, Chat 114).
    naehe_roh: float = internal.raum.naehe if internal else 0.5
    naehe_bin: int = 1 if naehe_roh >= GV_ACHSE_NAEHE_SCHWELLE else 0

    # ── V: Valenz ──
    sektor: int | None = EMOTION_SEKTOR_MAP.get(emotion)
    if sektor is not None:
        valenz_bin: int = GV_VALENZ_SEKTOR.get(sektor, 0)
    else:
        valenz_bin = 1  # neutral → positiv (Default)

    # ── T: Tiefe ──
    # Ebenfalls aus dem Raum. Der Modus wird trotzdem geprueft: Er ist die
    # Quelle, aus der der Raum sein Ziel zieht, und eine Luecke im Kanon
    # bliebe sonst unbemerkt.
    modus_pruefen(modus, "GV-Achse Tiefe")
    tiefe_roh: float = internal.raum.tiefe if internal else 0.3
    tiefe_bin: int   = 1 if tiefe_roh >= GV_ACHSE_TIEFE_SCHWELLE else 0

    # ── I: Initiative ──
    # Wer setzt die Richtung? Drei Masse aus ei/initiative.py, je auf ihr
    # eigenes Zentrum bezogen. Bit 0 heisst "Nutzer fuehrt" — der Wert liegt
    # in [-1, +1] und ist ueber 0 genau dann, wenn der Nutzer ueber dem
    # Korpus-Mittel fuehrt.
    #
    # Die abgeloeste Fassung verglich Turn-Laengen und stand ueber 15
    # gemessene Laeufe 15 Mal auf demselben Wert; 32 der 64 Sektoren waren
    # dadurch unerreichbar (novaberg-gv-initiative_k.md §2).
    if fuehrung is None:
        fuehrung = fuehrung_messen(state)
    initiative_roh: float | None = fuehrung.wert

    if initiative_roh is None:
        # Kein Mass verfuegbar. Die Achse braucht trotzdem ein Bit, aber es
        # ist keine Messung — deshalb laut, damit ein Sektor-Histogramm
        # spaeter nicht Ausfaelle als "Nova fuehrt" liest.
        logger.error(
            "GV-Achsen: Initiative nicht messbar (fehlend: %s) — Bit 1 gesetzt, "
            "das ist ein Ausfall und keine Messung", fuehrung.fehlend,
        )
        initiative_bin: int = 1
    else:
        # Die Schwelle ist NICHT 0: Der Median erzwaenge einen 50/50-Schnitt,
        # den die Wirklichkeit nicht hergibt. Gegen 83 unabhaengige Lesarten
        # kalibriert (config.GV_INITIATIVE_SCHWELLE, Herleitung im Konzept §12).
        # Die Binarisierung steht in ei/initiative.py, damit der Kalibrier-Lauf
        # dieselbe Regel benutzt wie die Laufzeit.
        initiative_bin = initiative_bit(initiative_roh, GV_INITIATIVE_SCHWELLE)

    # ── Drive (4-Achsen-Reduktion): E × R-Vorzeichen ──
    _VORZEICHEN: dict[str, float] = {
        "aufbluehen": 1.0, "eskalation": 0.8, "erholung": 0.5,
        "stabilisierung": 0.0, "plateau": 0.0,
        "abkuehlung": -0.3, "einbruch": -0.7, "spirale": -1.0, "absturz": -1.0,
    }
    drive: float = arousal * _VORZEICHEN.get(vektor, 0.0)

    achsen: dict = {
        "energie_roh":     round(energie_roh, 2),
        "energie":         energie_bin,
        "richtung":        vektor,
        "richtung_bin":    richtung_bin,
        "naehe_roh":       round(naehe_roh, 2),
        "naehe":           naehe_bin,
        "valenz_bin":      valenz_bin,
        "tiefe_roh":       round(tiefe_roh, 2),
        "tiefe":           tiefe_bin,
        "initiative_roh":  round(initiative_roh, 3) if initiative_roh is not None else None,
        "initiative_fehlend": fuehrung.fehlend,
        "initiative":      initiative_bin,
        "drive":           round(drive, 2),
    }

    # Die Werte benennen, nicht nur die Bits: V trug bisher nur die 0/1 und
    # verschwieg damit, auf welcher Emotion Novas Lage steht — genau die Frage,
    # an der sich die Achsen und die sechs Saeulen unterscheiden koennen.
    # N und T tragen seit Chat 114 den Raumwert; woher er kommt und wohin er
    # gezogen wird, steht in der Raumzug-Zeile desselben Turns.
    logger.info(
        f"GV-Achsen: E={energie_bin}({arousal:.2f}) R={richtung_bin}({vektor}) "
        f"N={naehe_bin}({naehe_roh:.2f} Raum) V={valenz_bin}({emotion}) "
        f"T={tiefe_bin}({tiefe_roh:.2f} Raum, Label {modus}) "
        f"I={initiative_bin}("
        f"{f'{initiative_roh:+.3f}' if initiative_roh is not None else 'nicht messbar'}"
        f") Drive={drive:.2f}"
    )

    return achsen


def initiative_berechnen(state: ConversationState) -> float:
    """⚠ ABGELOEST seit Chat 116 — nicht mehr im Achsen-Pfad.

    Ersetzt durch `ei/initiative.py`, `fuehrung_messen`. Die Funktion bleibt
    stehen, weil sie den Zustand dokumentiert, den die Messung widerlegt hat:
    Ueber 15 Laeufe stand die Achse 15 Mal auf demselben Wert. Der Nutzer
    schreibt 51 Zeichen je Turn, Nova 433; fuer die Schwelle von 1.5 muesste
    er das 12,6-fache schreiben. 32 der 64 Sektoren waren unerreichbar.
    Herleitung und Ersatz: novaberg-gv-initiative_k.md.

    Wer sie zurueckverdrahtet, holt den Befund zurueck — ein Test wird rot.

    Berechnet das Initiative-Verhaeltnis aus den Session-Turns.

    Vergleicht die durchschnittliche Laenge der User-Turns mit den
    Nova-Turns der letzten 6 Turns. Hoher Wert = User fuehrt.

    Returns:
        Verhaeltnis user_laenge / nova_laenge. Bei fehlenden Daten: 1.0.
    """
    session_turns: list[dict] = state.get("session_turns", [])
    if not session_turns:
        return 1.0

    letzte: list[dict] = session_turns[-6:]
    user_laengen:  list[int] = []
    nova_laengen:  list[int] = []

    for turn in letzte:
        inhalt: str = turn.get("inhalt", "")
        rolle:  str = turn.get("rolle", "")
        if rolle == "user":
            user_laengen.append(len(inhalt))
        elif rolle == "assistant":
            nova_laengen.append(len(inhalt))

    if not user_laengen or not nova_laengen:
        return 1.0

    avg_user: float = sum(user_laengen) / len(user_laengen)
    avg_nova: float = sum(nova_laengen) / len(nova_laengen)

    if avg_nova == 0:
        return 2.0

    verhaeltnis: float = avg_user / avg_nova
    logger.debug(
        f"GV-Initiative: Verhaeltnis={verhaeltnis:.2f} "
        f"(User avg={avg_user:.0f}, Nova avg={avg_nova:.0f})"
    )
    return verhaeltnis


def sektor_bestimmen(achsen: dict) -> tuple[int, str, str]:
    """Bestimmt Sektor-Index, -Name und Cluster aus den binaeren Achsen.

    Index = E*32 + R*16 + N*8 + V*4 + T*2 + I*1

    Returns:
        (sektor_index, sektor_name, cluster)
    """
    index: int = (
        achsen["energie"]      * 32
        + achsen["richtung_bin"] * 16
        + achsen["naehe"]        * 8
        + achsen["valenz_bin"]   * 4
        + achsen["tiefe"]        * 2
        + achsen["initiative"]   * 1
    )

    if 0 <= index < len(SEKTOR_TABELLE):
        name, cluster = SEKTOR_TABELLE[index]
    else:
        logger.warning(f"GV-Sektor: Index {index} ungueltig, Fallback Wartezimmer")
        name, cluster = "Wartezimmer", "wartezimmer"

    logger.info(f"GV-Sektor: #{index} '{name}' → Cluster '{cluster}'")
    return index, name, cluster


def repertoire_laden(cluster: str) -> dict[str, str]:
    """Laedt das Strategie-Repertoire fuer den aktuellen Cluster.

    Returns:
        Dict Strategie-ID → Eignung ("kern"/"passt"/"selten"/"unpassend").
    """
    repertoire: dict[str, str] = CLUSTER_REPERTOIRE.get(
        cluster, CLUSTER_REPERTOIRE["wartezimmer"]
    )
    verfuegbar: int = sum(1 for v in repertoire.values() if v != "unpassend")
    logger.info(
        f"GV-Repertoire ({cluster}): {verfuegbar}/7 verfuegbar — "
        + ", ".join(f"{k}={v}" for k, v in repertoire.items() if v != "unpassend")
    )
    return repertoire


def charakter_gewichtung_berechnen(state: ConversationState) -> dict[str, float]:
    """Cosine-Similarity zwischen Novas Charakter und den 7 Strategien.

    Strategie-Embeddings: einmal gecacht (statische Texte).
    Charakter-Embedding: jedes Mal frisch (~50ms).

    Returns:
        Dict Strategie-ID → Similarity, sortiert absteigend.
    """
    global _strategie_embeddings_cache

    internal = state.get("internal")
    charakter_text: str = " ".join(filter(None, [
        internal.character.core         if internal else "",
        internal.character.relationship if internal else "",
        internal.character.intentions   if internal else "",
        internal.character.emotions     if internal else "",
        internal.character.adaptive     if internal else "",
    ]))

    if not charakter_text.strip():
        logger.warning("GV-Charakter-Gewichtung: Kein Charakter-Text")
        return {}

    try:
        if not _strategie_embeddings_cache:
            logger.info("GV-Charakter-Gewichtung: Erstelle Strategie-Embeddings (einmalig)")
            for strat_id, beschreibung in STRATEGIE_BESCHREIBUNGEN.items():
                request = EmbedRequest(text=beschreibung)
                embed_response = model_service.embed.submit_sync(request)
                _strategie_embeddings_cache[strat_id] = embed_response.embedding
                logger.debug(
                    "Dreischicht: Strategie-Cache Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                    len(embed_response.embedding),
                    embed_response.duration_seconds,
                )

        char_request = EmbedRequest(text=charakter_text)
        char_response = model_service.embed.submit_sync(char_request)
        char_embedding: list[float] = char_response.embedding
        logger.debug(
            "Dreischicht: Charakter-Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(char_embedding),
            char_response.duration_seconds,
        )

        gewichtung: dict[str, float] = {}
        for strat_id, strat_emb in _strategie_embeddings_cache.items():
            sim: float = cosine_similarity(char_embedding, strat_emb)
            gewichtung[strat_id] = round(sim, 3)

        gewichtung = dict(sorted(gewichtung.items(), key=lambda x: x[1], reverse=True))

        logger.info(
            "GV-Charakter-Gewichtung: "
            + ", ".join(f"{k}={v:.3f}" for k, v in gewichtung.items())
        )
        return gewichtung

    except Exception as fehler:
        logger.warning(f"GV-Charakter-Gewichtung fehlgeschlagen: {fehler}")
        return {}


def dreischicht_prompt_bauen(
    cluster:     str,
    repertoire:  dict[str, str],
    gewichtung:  dict[str, float],
) -> str:
    """Baut den Dreischicht-Kontext-Block fuer den GV-Prompt.

    Kombiniert Cluster-Info, verfuegbare Strategien (sortiert nach
    Eignung × Charakter) und Absichten zu einem kompakten Prompt.

    Returns:
        Formatierter Prompt-Block.
    """
    beschreibung: str = CLUSTER_BESCHREIBUNGEN.get(cluster, "")
    fragen:       str = CLUSTER_FRAGEN.get(cluster, "")

    verfuegbar: list[tuple[str, str, float]] = []
    for strat_id, eignung in repertoire.items():
        if eignung == "unpassend":
            continue
        char_sim: float = gewichtung.get(strat_id, 0.5)
        verfuegbar.append((strat_id, eignung, char_sim))

    _EIGNUNG_RANG: dict[str, int] = {"kern": 0, "passt": 1, "selten": 2}
    verfuegbar.sort(key=lambda x: (_EIGNUNG_RANG.get(x[1], 9), -x[2]))

    # Der Marker steht HINTER dem Kuerzel. Stand er davor, begann die Zeile mit
    # einer Glyphe, das LLM antwortete formattreu "STRATEGIE: ● Sp" — und der
    # Parser las die Glyphe als Kuerzel (gemessen Chat 114). Der Parser ist
    # inzwischen robust dagegen; die Zeile gibt ihm trotzdem keinen Anlass mehr.
    strat_zeilen: list[str] = []
    for strat_id, eignung, char_sim in verfuegbar:
        name: str = STRATEGIE_NAMEN.get(strat_id, strat_id)
        marker: str = "★" if eignung == "kern" else ("●" if eignung == "passt" else "○")
        strat_zeilen.append(f"  {strat_id} ({name}) {marker} — Affinitaet: {char_sim:.0%}")

    block: str = (
        f"[GESPRAECHSLANDSCHAFT]\n"
        f"Cluster: {cluster.capitalize()} — {beschreibung}\n"
        f"Fragen: {fragen}\n\n"
        f"[WERKZEUGE]\n"
        f"Verfuegbare Strategien (★ Kern, ● passt, ○ selten):\n"
        + "\n".join(strat_zeilen)
        + "\n"
        f"Nenne bei STRATEGIE nur das Kuerzel — z.B. 'STRATEGIE: Sp'.\n"
        f"Andere Strategien stehen in dieser Landschaft nicht zur Wahl.\n\n"
        f"[ABSICHTEN]\n"
        f"Waehle eine Absicht und nenne nur ihren Namen:\n"
        f"  Teilen — etwas von dir geben, Verbindung\n"
        f"  Lenken — den Nutzer zu einer Erkenntnis fuehren\n"
        f"  Halten — Raum bewahren, Sicherheit geben\n"
        f"  Saeen  — einen Gedanken pflanzen, ohne ihn auszusprechen"
    )

    return block


def _normalisieren(wort: str) -> str:
    """Vereinheitlicht ein LLM-Wort fuer den Vergleich mit einem Kanon.

    Kleinschreibung, Umlaute aufgeloest, Schmuck- und Satzzeichen von den
    Raendern entfernt. "Saeen." und "Säen" und "SÄEN" ergeben denselben Wert.

    Vorbedingung: keine — ein leerer String ist zulaessig.
    Nachbedingung: Rueckgabe enthaelt nur den Wortkern.
    Fehlerfaelle: keine; ein reines Schmuckzeichen ergibt den leeren String.
    """
    # ── Verarbeitung ────────────────────────────
    ersetzt: str = wort.lower()
    for von, nach in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        ersetzt = ersetzt.replace(von, nach)

    # ── Ausgabe ─────────────────────────────────
    return ersetzt.strip(_RANDZEICHEN)


def _strategie_extrahieren(rohwert: str) -> str:
    """Zieht das Strategie-Kuerzel aus einer LLM-Antwortzeile.

    Das LLM antwortet formattreu zu dem, was der Prompt ihm zeigt. Der
    [WERKZEUGE]-Block listet "Sp (Spiegelung) ★ Kern — Affinitaet: 25%";
    Antworten wie "STRATEGIE: ● Sp (Spiegelung)" sind die Regel, nicht die
    Ausnahme. Ein split()[0] liefert dort die Marker-Glyphe und verwirft
    danach eine Strategie, die das LLM korrekt gewaehlt hatte (gemessen
    Chat 114: 17 von 44 Turns ohne Strategie).

    Vorbedingung: `rohwert` ist alles, was hinter "STRATEGIE:" stand.
    Nachbedingung: Rueckgabe ist ein Kuerzel aus STRATEGIE_NAMEN oder "".
    Fehlerfaelle: Kein erkennbares Kuerzel — Rueckgabe "", der Aufrufer
    entscheidet ueber die Meldung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not rohwert or not rohwert.strip():
        return ""

    # ── Verarbeitung ────────────────────────────
    kuerzel_index: dict[str, str] = {
        _normalisieren(k): k for k in STRATEGIE_NAMEN
    }
    namen_index: dict[str, str] = {
        _normalisieren(name): k for k, name in STRATEGIE_NAMEN.items()
    }

    for token in rohwert.replace("(", " ").replace(")", " ").split():
        kern: str = _normalisieren(token)
        if not kern:
            continue
        if kern in kuerzel_index:
            return kuerzel_index[kern]
        if kern in namen_index:
            return namen_index[kern]

    # ── Ausgabe ─────────────────────────────────
    return ""


def _doppelbuchstaben_kollabieren(wort: str) -> str:
    """Zieht Laeufe gleicher Buchstaben auf einen zusammen.

    Faengt die Schreibvarianten der Umlaut-Aufloesung ab: Der Prompt schreibt
    "Saeen", das Modell antwortet "Saen" — beide meinen Saeen und ergeben hier
    "saen". Gemessen am 28.07.2026, 13:05:30, als eine korrekt gewaehlte Absicht
    an dieser Schreibung scheiterte.

    Ueber den vier Absichten und den sieben Strategien ist die Abbildung
    eindeutig; zwei verschiedene Begriffe fallen nicht zusammen.

    Vorbedingung: keine.
    Nachbedingung: Rueckgabe enthaelt keinen Buchstaben zweimal hintereinander.
    Fehlerfaelle: keine.
    """
    # ── Verarbeitung ────────────────────────────
    gebaut: list[str] = []
    for zeichen in wort:
        if not gebaut or gebaut[-1] != zeichen:
            gebaut.append(zeichen)

    # ── Ausgabe ─────────────────────────────────
    return "".join(gebaut)


def _begriff_extrahieren(rohwert: str, kanon: set[str]) -> str:
    """Zieht den ersten Begriff aus `kanon` aus einer LLM-Antwortzeile.

    Gleiches Problem wie bei der Strategie: Das LLM haengt Begruendungen,
    Gedankenstriche und Klammern an ("ABSICHT: Saeen — den Boden bereiten") und
    schreibt aufgeloeste Umlaute mal mit, mal ohne das doppelte e.

    Vorbedingung: `kanon` enthaelt normalisierte Begriffe (klein, ohne Umlaute).
    Nachbedingung: Rueckgabe ist ein Element aus `kanon` oder "".
    Fehlerfaelle: Kein Treffer — Rueckgabe "".
    """
    # ── Eingabe-Validierung ─────────────────────
    if not rohwert or not rohwert.strip():
        return ""

    # ── Verarbeitung ────────────────────────────
    kollabiert_index: dict[str, str] = {
        _doppelbuchstaben_kollabieren(begriff): begriff for begriff in kanon
    }

    for token in rohwert.replace("(", " ").replace(")", " ").split():
        kern: str = _normalisieren(token)
        if kern in kanon:
            return kern
        variante: str = _doppelbuchstaben_kollabieren(kern)
        if variante in kollabiert_index:
            return kollabiert_index[variante]

    # ── Ausgabe ─────────────────────────────────
    return ""


def korridor_pruefen(
    gv_parsed:  dict,
    repertoire: dict[str, str],
    cluster:    str,
) -> list[dict]:
    """Prueft die gewaehlte Strategie gegen das Repertoire des Clusters.

    Der Cluster bestimmt das Repertoire, der Charakter gewichtet die Praeferenz
    (Konzept §10.1). Eine Strategie, die das Repertoire als "unpassend" fuehrt,
    ist keine kreative Variante, sondern ein Griff daneben — bisher fiel er
    niemandem auf, weil niemand nachsah.

    Vorbedingung: `gv_parsed` stammt aus gv_output_parsen(), `repertoire` aus
    repertoire_laden() desselben Turns.
    Nachbedingung: Liegt die Strategie ausserhalb des Korridors, ist das Feld
    geleert und der Verstoss in der Rueckgabe benannt. `gv_parsed` wird dabei
    veraendert.
    Fehlerfaelle: Leeres Repertoire — dann kann nichts geprueft werden, und das
    ist selbst ein Verstoss-Eintrag.
    """
    # ── Eingabe-Validierung ─────────────────────
    verstoesse: list[dict] = []
    strategie: str = gv_parsed.get("strategie", "")
    if not strategie:
        return verstoesse

    if not repertoire:
        verstoesse.append({
            "feld":  "strategie",
            "wert":  strategie,
            "grund": f"kein Repertoire fuer Cluster '{cluster}' — nicht pruefbar",
        })
        return verstoesse

    # ── Verarbeitung ────────────────────────────
    eignung: str = repertoire.get(strategie, "unbekannt")

    # ── Ausgabe-Verifikation ────────────────────
    if eignung in ("unpassend", "unbekannt"):
        verstoesse.append({
            "feld":  "strategie",
            "wert":  strategie,
            "grund": f"im Cluster '{cluster}' als '{eignung}' gefuehrt",
        })
        gv_parsed["strategie"] = ""

    return verstoesse


def gv_output_parsen(hypothese: str) -> dict:
    """Parst die strukturierten Zeilen aus dem LLM-Output.

    Erwartet gelabelte Zeilen:
        SPRUNG 1/2/3, ABSICHT, STRATEGIE, VEHIKEL, IMPULS
    Bei fehlenden Labels → voller Text als Impuls (graceful degradation).

    Vorbedingung: `hypothese` ist die rohe LLM-Antwort.
    Nachbedingung: Die drei Dreischicht-Felder tragen entweder einen Wert aus
    ihrem Kanon oder "". Jedes verworfene Rohwort steht mit Feld, Wert und
    Grund unter "verworfen" — der Aufrufer protokolliert es.
    Fehlerfaelle: Rohwert vorhanden, aber kein Kanon-Treffer → Verwerfung.
    Kein Label vorhanden → keine Verwerfung, das Feld bleibt schlicht leer.

    Returns:
        Dict mit sprung_1..3, absicht, strategie, vehikel, impuls, verworfen.
    """
    ergebnis: dict = {
        "sprung_1": "", "sprung_2": "", "sprung_3": "",
        "absicht": "", "strategie": "", "vehikel": "", "impuls": "",
        "verworfen": [],
    }

    impuls_zeilen: list[str] = []
    im_impuls: bool = False

    # Rohwerte merken: Nur wer weiss, was dastand, kann sagen, was verworfen wurde.
    roh_absicht:   str = ""
    roh_strategie: str = ""
    roh_vehikel:   str = ""

    for zeile in hypothese.splitlines():
        stripped: str = zeile.strip()
        if not stripped:
            if im_impuls:
                impuls_zeilen.append("")
            continue

        obere: str = stripped.upper()

        if obere.startswith("SPRUNG 1:"):
            ergebnis["sprung_1"] = stripped[9:].strip()
            im_impuls = False
        elif obere.startswith("SPRUNG 2:"):
            ergebnis["sprung_2"] = stripped[9:].strip()
            im_impuls = False
        elif obere.startswith("SPRUNG 3:"):
            ergebnis["sprung_3"] = stripped[9:].strip()
            im_impuls = False
        elif obere.startswith("ABSICHT:"):
            roh_absicht = stripped[8:].strip()
            ergebnis["absicht"] = _begriff_extrahieren(roh_absicht, ABSICHT_KANON)
            im_impuls = False
        elif obere.startswith("STRATEGIE:"):
            roh_strategie = stripped[10:].strip()
            ergebnis["strategie"] = _strategie_extrahieren(roh_strategie)
            im_impuls = False
        elif obere.startswith("VEHIKEL:"):
            roh_vehikel = stripped[8:].strip()
            ergebnis["vehikel"] = _begriff_extrahieren(roh_vehikel, VEHIKEL_KANON)
            im_impuls = False
        elif obere.startswith("IMPULS:"):
            impuls_zeilen.append(stripped[7:].strip())
            im_impuls = True
        elif im_impuls:
            impuls_zeilen.append(stripped)
        else:
            impuls_zeilen.append(stripped)

    ergebnis["impuls"] = "\n".join(impuls_zeilen).strip()

    # ── Ausgabe-Verifikation ────────────────────
    # Ein Rohwert, aus dem sich kein Kanon-Begriff ziehen liess, ist ein
    # Verlust und wird als solcher benannt — mit dem Wort, das dastand.
    for feld, rohwert in (
        ("absicht",   roh_absicht),
        ("strategie", roh_strategie),
        ("vehikel",   roh_vehikel),
    ):
        if rohwert and not ergebnis[feld]:
            ergebnis["verworfen"].append({
                "feld":  feld,
                "wert":  rohwert[:80],
                "grund": "kein Begriff aus dem Kanon erkennbar",
            })

    logger.info(
        f"GV-Parse: Spruenge=[{ergebnis['sprung_1'][:30]}.. | "
        f"{ergebnis['sprung_2'][:30]}.. | {ergebnis['sprung_3'][:30]}..] "
        f"Absicht={ergebnis['absicht']} Strategie={ergebnis['strategie']} "
        f"Vehikel={ergebnis['vehikel']}"
    )
    return ergebnis
