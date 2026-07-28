"""
Farbmisch-System: 8 unabhaengige Dimensionen → Landschaftsbeschreibung.

Jede Dimension traegt einen kurzen Satz bei, aber NUR wenn sie
etwas Auffaelliges zu sagen hat. Neutrale Werte schweigen.
Analog zu EI-MIKRO: Python waehlt, LLM interpretiert.
"""

import logging

from graph.state import ConversationState
from ei.utils import POSITIVE_EMOTIONEN, NEGATIVE_EMOTIONEN

logger = logging.getLogger("ki_server.ei.farbton")


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
    if emotion in POSITIVE_EMOTIONEN:
        if arousal >= 0.7:
            return "Die Stimmung ist lebhaft und positiv."
        elif arousal >= 0.4:
            return "Eine warme Grundstimmung liegt im Raum."
        else:
            return ""  # leise positive Stimmung — schweigt
    if emotion in NEGATIVE_EMOTIONEN:
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
    """Wie tief gehen wir?

    Deckt alle zehn Modi aus MODUS_KANON ab. Die Saetze beschreiben den Raum,
    nicht den Nutzer — der Farbton sagt, was IST, nicht wer es tut.
    """
    farben: dict[str, str] = {
        "fachgespraech":             "Das Gespraech ist fachlich und konzentriert.",
        "philosophischer_austausch": "Das Gespraech sucht die Tiefe hinter der Sache.",
        "lernmodus":                 "Hier wird Wissen aufgebaut, Schritt fuer Schritt.",
        "emotional":                 "Gefuehle stehen im Vordergrund.",
        "spielerisch":               "Die Stimmung ist verspielt und leicht.",
        "kreativ":                   "Hier wird gerade etwas erfunden.",
        "arbeitsmodus":              "Der Fokus liegt auf der Aufgabe.",
        "beratend":                  "Eine Entscheidung will abgewogen werden.",
        "berichtend":                "Es wird berichtet, nicht diskutiert.",
        "alltag":                    "",  # schweigt — Normalzustand
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


def farbton_berechnen(state: ConversationState) -> str:
    """Mischt die 8 Dimensionen zu einer Landschaftsbeschreibung.

    Jede Dimension traegt einen kurzen Satz bei — aber nur wenn sie
    etwas Auffaelliges zu sagen hat. Neutrale Werte schweigen.
    Das Ergebnis sind 2-5 Saetze die dem LLM die emotionale und
    kognitive Landschaft beschreiben, ohne Handlungsanweisungen.
    """
    internal = state.get("internal")
    emotion: str   = internal.emotion.emotion              if internal else "neutral"
    arousal: float = internal.emotion.arousal              if internal else 0.5
    vektor:  str   = internal.emotion.emotions_vector      if internal else ""
    modus:   str   = internal.emotion.mode                 if internal else "alltag"
    intent:  str   = internal.emotion.intent               if internal else ""
    dynamik: str   = internal.emotion.relationship_dynamic if internal else "neutral"
    stil:    str   = internal.emotion.language_style       if internal else "neutral"
    tone:    str   = internal.emotion.tone                 if internal else "sachlich"

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
