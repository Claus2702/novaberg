"""
Farbmisch-System: 8 unabhaengige Dimensionen → Landschaftsbeschreibung.

Jede Dimension traegt einen kurzen Satz bei, aber NUR wenn sie
etwas Auffaelliges zu sagen hat. Neutrale Werte schweigen.
Analog zu EI-MIKRO: Python waehlt, LLM interpretiert.
"""

import logging

from ei.utils import NEGATIVE_EMOTIONEN, POSITIVE_EMOTIONEN
from graph.reiz import reiz_ist_eigener_gedanke
from graph.state import ConversationState

# **Die zweite Seite ist da, ihr Wert ist es nicht.** Zu unterscheiden von
# `None`, das heisst *es gibt keine zweite Seite* (Hintergrundagenten) und die
# akteurslose Form ausloest. Hier steht ein Gegenueber im Raum, nur hat dieser
# Turn nichts an ihm gemessen — dann traegt der Satz Novas Haelfte allein.
NICHT_GEMESSEN: str = ""

logger = logging.getLogger("ki_server.ei.farbton")


# Die Gespraechsform je Seite, als Praedikat ohne Subjekt — der Satzbau
# entsteht in `_zwei_seiten`. `task` steht nicht hier: „Eine Aufgabe steht an"
# ist eine Aussage ueber den Raum und traegt keinen Akteur.
_INTENT_PRAEDIKAT: dict[str, str] = {
    "personal":  "bringt Persoenliches ein",
    "knowledge": "verfolgt einen Wissenspfad",
    "creative":  "ist im kreativen Modus",
}

# Dieselbe Lage ohne Akteur, fuer Aufrufer mit nur einer Seite.
_INTENT_RAUM: dict[str, str] = {
    "personal":  "Es geht um Persoenliches.",
    "knowledge": "Ein Wissenspfad wird verfolgt.",
    "creative":  "Es wird gerade erfunden.",
}

# Die Naehe je Seite, ebenfalls als Praedikat.
_DYNAMIK_PRAEDIKAT: dict[str, str] = {
    "vertrauen":    "ist offen und zugewandt",
    "distanz":      "haelt Abstand",
    "hilfesuchend": "sucht Halt",
    "dankbar":      "ist dankbar",
    "angriff":      "ist konfrontativ",
}

# Dieselbe Naehe ohne Akteur.
_DYNAMIK_RAUM: dict[str, str] = {
    "vertrauen":    "Offenheit traegt den Raum.",
    "distanz":      "Abstand liegt im Raum.",
    "hilfesuchend": "Im Raum wird Halt gesucht.",
    "dankbar":      "Dankbarkeit schwingt mit.",
    "angriff":      "Der Raum ist konfrontativ.",
}

# Wie die beiden Seiten heissen, je nachdem wer den Block liest. **Nicht ein
# Kompromiss fuer alle**, sondern die Namen des Lesers — `F-PROMPT-2`, und
# dieselbe Bauart wie `_NAMEN` in `graph/nodes/sachlage.py` (dort fuer den
# `[SACHLAGE]`-Block, der denselben Weg geht).
#
# **Der Schauspieler sitzt im Responder, und nur dort.** Der GV analysiert und
# darf den Charakter beim Namen nennen; der Verfasser bekommt Person A und
# Person B; der Responder spricht den Schauspieler als `du` an, weil dort das
# Modell die Rolle traegt. Ein Hintergrundagent hat keine zweite Seite und
# bekommt die akteurslose Form.
#
# Die Grossschreibung steht als eigener Eintrag, weil `str.capitalize()` den
# Rest kleinschreibt: aus `der Nutzer` wuerde `Der nutzer`.
LESER_GV:        str = "gv"
LESER_RESPONDER: str = "responder"
LESER_VERFASSER: str = "verfasser"

_NAMEN: dict[str, dict[str, str]] = {
    LESER_GV:        {"nova": "Nova",     "nutzer": "der Nutzer", "Nutzer": "Der Nutzer"},
    LESER_RESPONDER: {"nova": "Du",       "nutzer": "der Nutzer", "Nutzer": "Der Nutzer"},
    LESER_VERFASSER: {"nova": "Person A", "nutzer": "Person B",   "Nutzer": "Person B"},
}

# **Die Beugung steht einmal.** Die Praedikat-Tabellen oben fuehren die dritte
# Person Singular; welche Form ein Satz braucht, haengt am Leser und daran, ob
# eine oder beide Seiten gemeint sind. Fuenf Verben decken beide Tabellen ab —
# eine allgemeine Konjugation waere ein Sprachmodul und hier nicht zu
# rechtfertigen; was nicht passt, bleibt unveraendert und liest sich holprig
# statt falsch.
# Die vier Formen stehen **alle** in der Tabelle, auch die unveraenderte
# dritte Person Singular. Sie implizit durchfallen zu lassen sah kuerzer aus
# und beugte `Nova ist` auf `Nova sind`, sobald eine Form fehlte — ein
# Rueckfall, der wie eine Absicht aussieht (`22_STILLE_FEHLER`).
_KONJUGATION: dict[str, dict[str, str]] = {
    #             3. Sg.              3. Pl.        2. Sg.        2. Pl.
    "ist":      {"er": "ist",      "sie": "sind",      "du": "bist",      "ihr": "seid"},
    "haelt":    {"er": "haelt",    "sie": "halten",    "du": "haeltst",   "ihr": "haltet"},
    "sucht":    {"er": "sucht",    "sie": "suchen",    "du": "suchst",    "ihr": "sucht"},
    "verfolgt": {"er": "verfolgt", "sie": "verfolgen", "du": "verfolgst", "ihr": "verfolgt"},
    "bringt":   {"er": "bringt",   "sie": "bringen",   "du": "bringst",   "ihr": "bringt"},
}


def _gebeugt(praedikat: str, form: str, einschub: str = "") -> str:
    """Beugt das Verb eines Praedikats und setzt einen Einschub dahinter.

    Der Einschub steht zwischen Verb und Rest, weil das Deutsche ihn dort
    verlangt: *„Ihr haltet **beide** Abstand"*, nicht *„Ihr haltet Abstand
    beide"*.

    Vorbedingung: `praedikat` stammt aus einer der beiden Praedikat-Tabellen;
        `form` ist ein Schluessel aus `_KONJUGATION`s Werten (`sie`, `du`,
        `ihr`).
    Nachbedingung: Das gebeugte Praedikat ohne fuehrendes Subjekt und ohne
        Satzzeichen. Ein Verb ausserhalb der Tabelle bleibt unveraendert.
    Fehlerfaelle: Keine.
    """
    # ── Verarbeitung ────────────────────────────
    verb, _, rest = praedikat.partition(" ")
    gebeugt: str = _KONJUGATION.get(verb, {}).get(form, verb)
    return " ".join(teil for teil in (gebeugt, einschub, rest) if teil)


def _namen_holen(leser: str) -> dict[str, str]:
    """Die Namen des Lesers, oder ein Fehler.

    Vorbedingung: `leser` ist einer der drei LESER_*-Werte.
    Nachbedingung: das Namens-Dict.
    Fehlerfaelle: Ein unbekannter Leser ist ein `ValueError`, **kein
        Rueckfall** — ein Block im falschen Namenssystem saehe richtig aus und
        spraeche den Schauspieler mit dem falschen Namen an.
    """
    # ── Eingabe-Validierung ─────────────────────
    if leser not in _NAMEN:
        meldung: str = f"Farbton: unbekannter Leser {leser!r}"
        raise ValueError(meldung)
    return _NAMEN[leser]


def _zwei_seiten(nova: str, nutzer: str | None,
                 praedikate: dict[str, str],
                 raum: dict[str, str],
                 leser: str = LESER_GV) -> str:
    """Baut einen Satz ueber den Raum aus den Haltungen beider Seiten.

    **Der Raum entsteht aus beiden, nicht aus einem.** Ein Satz, der nur eine
    Seite nennt, waehrend beide Werte vorliegen, macht die eine zum Handelnden
    und die andere zum Gegenstand — genau das soll der Block nicht sagen
    (Absicht des Meisters, 10.09.2026, Register `F-FARBTON-1`).

    Vorbedingung: `nova` und `nutzer` stammen aus dem Kanon ihrer Dimension
        oder liegen ausserhalb; ausserhalb traegt nichts bei. `nutzer` ist
        `None`, wenn der Aufrufer keine zweite Seite hat — dann faellt der
        Satz auf die akteurslose Form zurueck, statt eine Seite zu erfinden.
    Nachbedingung: Ein Satz mit abschliessendem Punkt, oder der leere String,
        wenn keine der beiden Seiten etwas beizutragen hat.
    Fehlerfaelle: Keine. Unbekannte Werte schweigen, wie im ganzen Modul.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Kein Wert ist ein Fehler: Beide Kanons kennen einen neutralen Zustand,
    # der ausdruecklich schweigen soll. Nur beide stumm ergibt den leeren Satz.
    nova_teil:   str = praedikate.get(nova, "")
    nutzer_teil: str = praedikate.get(nutzer or "", "")

    # ── Verarbeitung ────────────────────────────
    # Ohne zweite Seite bleibt nur die Lage selbst — akteurslos, damit der
    # Satz nicht behauptet, wessen Haltung er beschreibt.
    if nutzer is None:
        return raum.get(nova, "")

    namen: dict[str, str] = _namen_holen(leser)
    # Beim Responder traegt das Modell die Rolle und wird angesprochen; bei
    # allen anderen Lesern wird ueber sie gesprochen (`F-PROMPT-2`).
    novas_form: str = "du" if leser == LESER_RESPONDER else "er"

    # **Gleichstand ist die staerkste Aussage ueber den Raum** — beide tragen
    # dieselbe Haltung. Sie zweimal hinzuschreiben verwaessert das zu zwei
    # Beobachtungen; ein Satz macht daraus einen Zustand.
    if nova_teil and nutzer_teil and nova == nutzer:
        if novas_form == "du":
            return f"Ihr {_gebeugt(nova_teil, 'ihr', einschub='beide')}."
        return (f"{namen['nova']} und {namen['nutzer']} "
                f"{_gebeugt(nova_teil, 'sie')}.")

    if nova_teil and nutzer_teil:
        return (f"{namen['nova']} {_gebeugt(nova_teil, novas_form)}, "
                f"{namen['nutzer']} {nutzer_teil}.")

    if nova_teil:
        return f"{namen['nova']} {_gebeugt(nova_teil, novas_form)}."
    if nutzer_teil:
        return f"{namen['Nutzer']} {nutzer_teil}."

    return ""




def _farbe_intent(intent: str, nutzer_intent: str | None = None,
                  leser: str = LESER_GV) -> str:
    """Was fuer ein Gespraech ist das — fuer beide Seiten?"""
    # `task` traegt keinen Akteur und gilt fuer den Raum als Ganzes.
    if intent == "task" or nutzer_intent == "task":
        return "Eine Aufgabe steht an."
    return _zwei_seiten(intent, nutzer_intent,
                        _INTENT_PRAEDIKAT, _INTENT_RAUM, leser)


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


def _farbe_dynamik(dynamik: str, nutzer_dynamik: str | None = None,
                   leser: str = LESER_GV) -> str:
    """Wie nah sind wir uns — und wer traegt welchen Teil davon?

    **Die Frage war immer beidseitig, die Antwort bis zum 10.09.2026 nicht.**
    Vier Saetze nannten den Nutzer, gespeist aus `internal` — also Novas
    eigenem Register. `[gemessen 10.09.2026]` In **419 von 826** Turns (50,7 %)
    behauptete der Satz eine andere Haltung als die am Nutzer gemessene;
    167-mal stand *„Der Nutzer ist offen und vertraut"*, waehrend er `distanz`
    trug.
    """
    return _zwei_seiten(dynamik, nutzer_dynamik,
                        _DYNAMIK_PRAEDIKAT, _DYNAMIK_RAUM, leser)


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


def lage_beschreiben(
    vektor:  str,
    emotion: str,
    arousal: float,
    dynamik: str,
) -> str:
    """Beschreibt eine emotionale Lage aus rohen Werten, ohne Zustandsverbund.

    Fuer Aufrufer ausserhalb des Graphen — Hintergrundagenten haben keinen
    `ConversationState`, brauchen aber dieselben Saetze. Die Texte stehen
    deshalb weiterhin nur hier: Eine zweite Formulierung derselben Lage
    liefe beim naechsten Nachschaerfen auseinander.

    Bewusst nur drei der acht Dimensionen — Bewegung, Stimmung, Naehe. Modus,
    Stil, Ton und Intent beschreiben die *Gespraechsform*; wer keinen Turn vor
    sich hat, sondern eine Lage, hat sie nicht und soll sie nicht raten.

    **Die Beschreibung adressiert niemanden.** Sie sagt „Die Stimmung ist
    eingebrochen", nicht „Wie geht es dir?". Genau darin liegt ihr Wert fuer
    den Shadow-Stack, der einen Reiz erwartet und keinen fertigen Satz.

    Vorbedingung: `arousal` liegt in [0.0, 1.0]; `vektor`, `emotion` und
        `dynamik` stammen aus ihren Kanons. Pruefung erfolgt beim Aufrufer —
        die Werte kommen dort von der Eingabegrenze, hier nicht mehr.
    Nachbedingung: Nicht-leere Zeichenkette. Schweigen alle drei Dimensionen,
        steht dort der Ersatzsatz — eine leere Lage waere fuer den Aufrufer
        von einem Fehlschlag nicht zu unterscheiden.
    Fehlerfaelle: Keine. Unbekannte Werte tragen nichts bei, statt zu werfen;
        die Zugehoerigkeit zum Kanon ist die Sache des Aufrufers.
    """
    farben: list[str] = [
        _farbe_vektor(vektor),
        _farbe_emotion(emotion, arousal),
        _farbe_dynamik(dynamik),
    ]

    lage: str = " ".join(f for f in farben if f)

    # ── Ausgabe-Verifikation ────────────────────
    if not lage:
        logger.info(
            f"Farbton: Lage aus vektor={vektor!r}, emotion={emotion!r}, "
            f"arousal={arousal:.2f}, dynamik={dynamik!r} ergab keinen Satz — "
            f"Ersatzsatz gesetzt"
        )
        return "Die Lage ist unauffaellig."

    return lage


def farbton_berechnen(state: ConversationState,
                      leser: str = LESER_GV) -> str:
    """Mischt die 8 Dimensionen zu einer Landschaftsbeschreibung.

    Jede Dimension traegt einen kurzen Satz bei — aber nur wenn sie
    etwas Auffaelliges zu sagen hat. Neutrale Werte schweigen.
    Das Ergebnis sind 2-5 Saetze die dem LLM die emotionale und
    kognitive Landschaft beschreiben, ohne Handlungsanweisungen.

    **Sechs Dimensionen lesen einen Zustand, zwei ein Verhaeltnis.** Stimmung,
    Bewegung, Modus, Stil, Energie und Ton sind Lagen und stehen in `internal`.
    Intent und Naehe sagen, wie zwei Seiten zueinander stehen; sie lesen
    deshalb `internal` **und** `external` (Register `F-FARBTON-1`, 10.09.2026).

    Vorbedingung: `state` traegt `internal`; `external` darf fehlen, dann
        formulieren die beiden Verhaeltnis-Dimensionen akteurslos.
    Nachbedingung: Nicht-leere Zeichenkette — schweigen alle acht, steht dort
        der Ersatzsatz.
    Fehlerfaelle: Keine.
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

    # **Die zweite Seite des Raums.** Sechs der acht Dimensionen beschreiben
    # eine Lage und brauchen nur einen Zustand; Intent und Naehe beschreiben
    # ein Verhaeltnis und brauchen beide. Fehlt `external`, bleibt es bei der
    # akteurslosen Form — ein erfundener Nutzerwert waere schlimmer als keiner.
    #
    # **Auf einem Impuls-Turn ist `external` eine Kopie von `internal`** und
    # beschreibt Novas vorige Antwort, nicht den Nutzer (`F-GV-1`). Der Wert
    # steht da, ist aber keine Messung am Gegenueber — wer ihn liest, laesst
    # den Farbton *Nova und der Nutzer sind einander zugewandt* sagen und
    # stuetzt das *beide* auf zweimal denselben Wert.
    #
    # `[gemessen 10.09.2026]` **81 von 154 Impuls-Turns** (52,6 %) haetten
    # genau diesen Paarsatz getragen. Deshalb gilt hier `NICHT_GEMESSEN`:
    # Die zweite Seite existiert, ihr Wert ist unbekannt, und der Satz nennt
    # dann nur Novas Haelfte — statt eine Uebereinstimmung zu behaupten.
    external = state.get("external")
    eigener_impuls: bool = reiz_ist_eigener_gedanke(state)

    if not external:
        nutzer_intent:  str | None = None
        nutzer_dynamik: str | None = None
    elif eigener_impuls:
        nutzer_intent  = NICHT_GEMESSEN
        nutzer_dynamik = NICHT_GEMESSEN
    else:
        nutzer_intent  = external.emotion.intent
        nutzer_dynamik = external.emotion.relationship_dynamic

    farben: list[str] = [
        _farbe_intent(intent, nutzer_intent, leser),
        _farbe_emotion(emotion, arousal),
        _farbe_vektor(vektor),
        _farbe_dynamik(dynamik, nutzer_dynamik, leser),
        _farbe_modus(modus),
        _farbe_stil(stil),
        _farbe_arousal(arousal),
        _farbe_tone(tone, stil),
    ]

    landschaft: str = " ".join(f for f in farben if f)

    if not landschaft:
        landschaft = "Das Gespraech ist ruhig und ausgeglichen."

    return landschaft
