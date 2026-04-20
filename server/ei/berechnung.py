"""
EI-Berechnungsfunktionen — Emotionale Intelligenz.

Reine Funktionen ohne I/O (kein Redis, kein PostgreSQL, kein Ollama).
Alle Operationen sind deterministisch: Emotions-Verlauf, Vektor-Berechnung,
Sprachstil-Erkennung, EI-Plausibilitäts-Gate.

Extrahiert aus enricher.py in Chat 58 (Dual-Emotion Phase 2, AP1).
Wird verwendet von:
  - graph/nodes/enricher.py (Enricher-Node, User-EI)
  - graph/nodes/ei_calc.py  (EI-Calc-Node, User + Nova EI, kommt in AP2)
"""

import logging
import math
import re

from config import (
    EMOTION_DECAY_FACTOR,
    EMOTION_DECAY_BASE,
    EMOTION_DEFAULT_AROUSAL,
    EMOTION_MAX_TURNS,
    EMOTION_MIN_WEIGHT,
    EMOTION_VEKTOR_TURNS,
    STIL_ANALYSE_TURNS,
    EI_AROUSAL_PERSISTENCE,
    EI_DYNAMIK_FAKTOREN,
    EI_INTENT_FAKTOREN,
    EI_TONE_FAKTOREN,
    EI_GEWICHTE,
    EI_PASSIV_NEGATIVE,
    EMOTION_SEKTOR_MAP,
    EMOTION_SYNONYM_MAP,
    EMOTION_KANON,
    EMOTION_SEKTOR_DISTANZ,
    SEKTOR_GRUPPE,
    EMOTION_AROUSAL_DECAY,
    EI_AROUSAL_DOMINANZ,
    EMPATHIE_ALPHA,
    EMPATHIE_ALPHA_NEUTRAL,
    EMPATHIE_KONFLIKT_DISTANZ,
    EMPATHIE_KONFLIKT_MIN_AROUSAL,
)

logger = logging.getLogger("ki_server.ei.berechnung")


def _emotion_kanonisieren(emotion: str) -> str:
    """
    Löst Synonyme auf und prüft auf kanonische Emotionen.

    Drei Stufen:
    1. Kanonisch → direkt zurückgeben
    2. Synonym → auf kanonische Form mappen
    3. Unbekannt → Error-Log, Originalwert zurückgeben
    """
    if emotion in EMOTION_KANON:
        return emotion

    if emotion in EMOTION_SYNONYM_MAP:
        kanonisch: str = EMOTION_SYNONYM_MAP[emotion]
        logger.info(f"EI-Calc: Emotion '{emotion}' → '{kanonisch}' (Synonym)")
        return kanonisch

    if emotion and emotion != "neutral":
        logger.error(
            f"EI-Calc: Unbekannte Emotion '{emotion}' — "
            f"nicht in EMOTION_KANON und nicht in EMOTION_SYNONYM_MAP. "
            f"Muss in config.py ergänzt werden."
        )

    return emotion


# Abwärtskompatibilität: String-Arousal aus älteren Session-Turns → Float
_AROUSAL_STR_TO_FLOAT: dict[str, float] = {"high": 0.8, "mid": 0.5, "low": 0.2}


def _arousal_to_float(raw, emotion: str = "neutral") -> float:
    """Konvertiert einen Arousal-Wert (float oder Legacy-String) zu Float."""
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str) and raw in _AROUSAL_STR_TO_FLOAT:
        return _AROUSAL_STR_TO_FLOAT[raw]
    return EMOTION_DEFAULT_AROUSAL.get(emotion, 0.5)


def _emotions_verlauf_berechnen(
    turns: list[dict],
    current_emotion: str = "neutral",
    current_arousal: float = 0.5,
    rolle: str = "user",
) -> list[dict]:
    """
    Berechnet einen gewichteten Emotions-Verlauf über alle User-Turns.

    Verwendet logarithmischen Decay: Neuere Turns haben mehr Gewicht,
    ältere klingen ab. Der aktuelle Prompt (current_emotion von der Perzeption)
    wird als Turn 0 eingefügt — damit ist er sofort sichtbar, auch wenn
    die Salienz-Annotation erst nach dem Responder läuft.

    Args:
        rolle: Welche Turns berücksichtigt werden ("user" oder "assistant").

    Returns:
        Liste von {emotion: str, gewicht: float, arousal: float},
        absteigend nach Gewicht.
    """

    # 1. Nur User-Turns mit nicht-neutraler Emotion (kanonisiert)
    emotion_turns: list[dict] = []
    for t in turns:
        if t.get("rolle") != rolle or not t.get("emotion"):
            continue
        kanon: str = _emotion_kanonisieren(t["emotion"])
        if kanon == "neutral":
            continue
        emotion_turns.append({
            **t,
            "emotion": kanon,
        })

    # 2. Letzte N Turns
    emotion_turns = emotion_turns[-EMOTION_MAX_TURNS:]

    # 2b. Aktuellen Prompt als virtuellen Turn 0 einfügen (neuester)
    has_current: bool = current_emotion and current_emotion != "neutral"

    if has_current:
        kanon_current: str = _emotion_kanonisieren(current_emotion)
        if kanon_current != "neutral":
            emotion_turns.append({
                "rolle": rolle,
                "emotion": kanon_current,
                "arousal": current_arousal,
            })
            has_current = True
        else:
            has_current = False

    if not emotion_turns:
        return []

    # 3. Decay berechnen (neuester Turn zuerst)
    akkumuliert: dict[str, float] = {}
    arousal_map: dict[str, float] = {}

    for i, turn in enumerate(reversed(emotion_turns)):
        emotion: str = turn["emotion"]
        arousal: float = _arousal_to_float(turn.get("arousal"), emotion)

        # Arousal-basierter Decay: Starke Emotionen halten länger.
        # Hoher Arousal → niedrigerer effective_decay → langsamerer Verfall.
        # Kleiner Ärger (0.2) verfällt schnell, Kündigung (0.8) hält.
        effective_decay: float = EMOTION_DECAY_FACTOR * (1.0 - arousal * EI_AROUSAL_PERSISTENCE)
        decay: float = 1.0 / (1.0 + effective_decay * math.log(1.0 + i, EMOTION_DECAY_BASE))
        akkumuliert[emotion] = akkumuliert.get(emotion, 0.0) + decay

        # Arousal mit emotionsspezifischem Decay dämpfen
        decay_rate: float = EMOTION_AROUSAL_DECAY.get(emotion, 0.05)
        gedaempfter_arousal: float = arousal * math.exp(-decay_rate * i)

        # Neuesten (höchsten) gedämpften Arousal merken
        if emotion not in arousal_map or gedaempfter_arousal > arousal_map[emotion]:
            arousal_map[emotion] = gedaempfter_arousal

    # 4. Sektorabhängige Normalisierung (Plutchik-Modell)
    max_gewicht: float = max(akkumuliert.values())

    if max_gewicht <= 0:
        return []

    # Dominante Emotion über Effektivwert bestimmen (Gewicht × Arousal^n)
    effektiv_werte: dict[str, float] = {}
    for emotion, gewicht in akkumuliert.items():
        ar: float = arousal_map.get(emotion, 0.5)
        effektiv_werte[emotion] = gewicht * (ar ** EI_AROUSAL_DOMINANZ)

    dominante_emotion: str = max(effektiv_werte, key=effektiv_werte.get)
    dominante_sektor: int | None = EMOTION_SEKTOR_MAP.get(dominante_emotion)
    dominante_arousal: float = arousal_map.get(dominante_emotion, 0.5)

    normalisiert: dict[str, float] = {}

    for emotion, gewicht in akkumuliert.items():
        # Basis-Normalisierung (wie bisher)
        basis_norm: float = gewicht / max_gewicht

        if emotion == dominante_emotion:
            normalisiert[emotion] = 1.0
            continue

        # Sektor der aktuellen Emotion
        emotion_sektor: int | None = EMOTION_SEKTOR_MAP.get(emotion)

        # Sektorlose Emotionen oder unbekannte: Exponent 1.0 (wie bisher)
        if dominante_sektor is None or emotion_sektor is None:
            normalisiert[emotion] = basis_norm
            continue

        # Basis-Exponent aus Distanzmatrix
        basis_exponent: float = EMOTION_SEKTOR_DISTANZ.get(
            (dominante_sektor, emotion_sektor), 1.0
        )

        # Arousal-Skalierung: Niedrige Arousal → Exponent wandert Richtung 1.0
        eff_exponent: float = 1.0 + (basis_exponent - 1.0) * dominante_arousal

        # Potenz-Transformation
        normalisiert[emotion] = basis_norm ** eff_exponent

    # 5. Filtern + Sortieren
    ergebnis: list[dict] = [
        {
            "emotion": emotion,
            "gewicht": round(gewicht, 2),
            "arousal": round(arousal_map.get(emotion, 0.5), 2),
        }
        for emotion, gewicht in normalisiert.items()
        if gewicht >= EMOTION_MIN_WEIGHT
    ]

    ergebnis.sort(key=lambda e: e["gewicht"], reverse=True)
    return ergebnis


def _emotion_zu_gruppe(emotion: str) -> str:
    """Ordnet eine Emotion einer Gruppe zu basierend auf dem Plutchik-Sektor."""
    sektor: int | None = EMOTION_SEKTOR_MAP.get(emotion)
    if sektor is None:
        return "neutral"
    return SEKTOR_GRUPPE.get(sektor, "neutral")


def _dominante_gruppe(turns: list[dict]) -> str:
    """Bestimmt die dominante Emotions-Gruppe einer Turn-Liste."""
    zaehler: dict[str, int] = {"positiv": 0, "negativ": 0, "neutral": 0}

    for turn in turns:
        emotion: str = turn.get("emotion", "neutral")
        gruppe: str = _emotion_zu_gruppe(emotion)
        zaehler[gruppe] += 1

    max_count: int = max(zaehler.values())
    kandidaten: list[str] = [g for g, c in zaehler.items() if c == max_count]

    if len(kandidaten) == 1:
        return kandidaten[0]

    # Gleichstand: Gruppe der zeitlich letzten Emotion gewinnt
    if turns:
        letzte_emotion: str = turns[-1].get("emotion", "neutral")
        return _emotion_zu_gruppe(letzte_emotion)

    return "neutral"


def _emotions_vektor_bestimmen(
    turns: list[dict],
    current_emotion: str = "neutral",
    rolle: str = "user",
) -> str:
    """
    Bestimmt den emotionalen Vektor (Richtung) aus den letzten User-Turns.

    Der aktuelle Prompt (current_emotion von der Perzeption) wird als neuester
    Datenpunkt eingefügt, damit der Vektor Richtungswechsel sofort erkennt.

    Args:
        rolle: Welche Turns berücksichtigt werden ("user" oder "assistant").

    Returns:
        Einer der 9 Vektor-Namen: "absturz", "spirale", "stabilisierung",
        "erholung", "aufbluehen", "eskalation", "abkuehlung", "einbruch", "plateau"
    """

    # 1. Nur User-Turns mit Emotion, kanonisiert, eigenes kurzes Fenster
    emotion_turns: list[dict] = []
    for t in turns:
        if t.get("rolle") != rolle or not t.get("emotion"):
            continue
        kanon: str = _emotion_kanonisieren(t["emotion"])
        emotion_turns.append({**t, "emotion": kanon})
    emotion_turns = emotion_turns[-EMOTION_VEKTOR_TURNS:]

    # 1b. Aktuellen Prompt als neuesten Turn einfügen
    if current_emotion:
        kanon_current: str = _emotion_kanonisieren(current_emotion)
        emotion_turns.append({
            "rolle": rolle,
            "emotion": kanon_current,
        })

    # 2. Zu wenig Daten
    if len(emotion_turns) < 2:
        return "plateau"

    # 3. In zwei Hälften teilen
    if len(emotion_turns) <= 3:
        neuere: list[dict] = emotion_turns[-1:]
        aeltere: list[dict] = emotion_turns[:-1]
    else:
        neuere = emotion_turns[-2:]
        aeltere = emotion_turns[-5:-2] if len(emotion_turns) >= 5 else emotion_turns[:-2]

    # 4. Dominante Gruppe je Hälfte
    gruppe_alt: str = _dominante_gruppe(aeltere)
    gruppe_neu: str = _dominante_gruppe(neuere)

    # 5. Intensitäts-Check für Spirale/Eskalation
    # Neue Emotion die vorher nicht vorkam = Intensitätsanstieg
    emotionen_alt: set[str] = {t.get("emotion", "") for t in aeltere}
    emotionen_neu: set[str] = {t.get("emotion", "") for t in neuere}
    neue_emotionen: set[str] = emotionen_neu - emotionen_alt

    # 6. Vektor-Mapping
    uebergang: tuple[str, str] = (gruppe_alt, gruppe_neu)

    vektor_map: dict[tuple[str, str], str] = {
        ("positiv", "negativ"):  "absturz",
        ("negativ", "neutral"):  "stabilisierung",
        ("negativ", "positiv"):  "erholung",
        ("neutral", "positiv"):  "aufbluehen",
        ("positiv", "neutral"):  "abkuehlung",
        ("neutral", "negativ"):  "einbruch",
        ("neutral", "neutral"):  "plateau",
    }

    # Spezialfälle: gleiche Gruppe → Spirale/Eskalation oder Plateau
    if uebergang == ("negativ", "negativ"):
        return "spirale" if neue_emotionen else "plateau"

    if uebergang == ("positiv", "positiv"):
        return "eskalation" if neue_emotionen else "plateau"

    return vektor_map.get(uebergang, "plateau")


def _turn_features_bewerten(turn_text: str) -> dict[str, float]:
    """
    Bewertet einen einzelnen User-Turn auf Stilmerkmale.

    Eingabe: Originaltext (nicht lowercased).
    Rückgabe: Scores pro Stil (positiv und negativ möglich).
    """

    text_lower: str = turn_text.lower()
    woerter: list[str] = text_lower.split()
    anzahl_woerter: int = len(woerter) if woerter else 1

    # Sätze splitten (an . ! ?)
    saetze: list[str] = [s.strip() for s in re.split(r'[.!?]+', turn_text) if s.strip()]
    mittlere_satzlaenge: float = (
        sum(len(s.split()) for s in saetze) / len(saetze) if saetze else 0
    )

    scores: dict[str, float] = {
        "locker": 0.0, "formell": 0.0, "fachlich": 0.0,
        "emotional": 0.0, "jugendlich": 0.0,
    }

    # ── 1. Satzlänge ──
    if mittlere_satzlaenge < 8:
        scores["locker"]     += 2.0
        scores["jugendlich"] += 1.0
    elif mittlere_satzlaenge > 15:
        scores["formell"]  += 2.0
        scores["fachlich"] += 1.0

    # ── 2. Nebensätze (Komma-Häufigkeit, normalisiert) ──
    komma_dichte: float = turn_text.count(",") / anzahl_woerter if anzahl_woerter > 3 else 0
    if komma_dichte > 0.1:
        scores["formell"]  += 2.0
        scores["fachlich"] += 1.0

    # ── 3. Zeichensetzung ──
    hat_punkt: bool = "." in turn_text
    hat_komma: bool = "," in turn_text
    ausrufezeichen: int = turn_text.count("!")

    if hat_punkt and hat_komma:
        scores["formell"]    += 1.0
        scores["fachlich"]   += 1.0
        scores["jugendlich"] -= 1.0

    if not hat_punkt and not hat_komma:
        scores["locker"]     += 1.0
        scores["formell"]    -= 2.0
        scores["emotional"]  += 1.0
        scores["jugendlich"] += 1.0

    if ausrufezeichen > 1:
        scores["emotional"]  += 2.0
        scores["jugendlich"] += 1.0

    # ── 4. Emojis ──
    emoji_pattern = re.compile(
        r'[\U0001F300-\U0001F9FF\U00002702-\U000027B0\u2600-\u26FF\u2700-\u27BF]'
    )
    hat_emoji: bool = bool(emoji_pattern.search(turn_text))
    if hat_emoji:
        scores["formell"]    -= 2.0
        scores["emotional"]  += 1.0
        scores["jugendlich"] += 1.0

    # ── 5. Slang-Wörter ──
    slang_marker: list[str] = [
        "yo", "brudi", "digga", "alter", "lol", "nice", "krass",
        "mega", "safe", "vibe", "sheesh", "geil", "ey", "vallah",
        "bro", "chillen", "lit", "slay",
    ]
    padded: str = f" {text_lower} "
    slang_treffer: int = sum(
        1 for m in slang_marker
        if f" {m} " in padded
    )
    if slang_treffer:
        scores["jugendlich"] += 3.0 * slang_treffer
        scores["formell"]    -= 2.0 * slang_treffer

    # ── 6. Höflichkeitsformen ──
    hoeflich_marker: list[str] = [
        "sie ", " ihnen ", "sehr geehrte", "mit freundlichen",
        "würde ich", "könnte ich", "dürfte ich", "gestatten",
    ]
    hoeflich_treffer: int = sum(1 for m in hoeflich_marker if m in text_lower)
    if hoeflich_treffer:
        scores["formell"] += 3.0 * hoeflich_treffer

    # ── 7. Fachbegriffe (lange Wörter) ──
    lange_woerter: int = sum(1 for w in woerter if len(w) > 10)
    if anzahl_woerter > 3 and lange_woerter / anzahl_woerter > 0.1:
        scores["fachlich"] += 3.0

    # ── 8. Interjektionen ──
    interjektionen: list[str] = [
        "oh", "wow", "ach", "oje", "mist", "verdammt", "boah",
        "puh", "hm", "hmm", "tja", "naja",
    ]
    inter_treffer: int = sum(
        1 for m in interjektionen
        if f" {m} " in padded
    )
    if inter_treffer:
        scores["locker"]     += 1.0
        scores["formell"]    -= 1.0
        scores["emotional"]  += 2.0
        scores["jugendlich"] += 2.0

    # ── 9. Ellipsen ──
    if "..." in turn_text:
        scores["emotional"] += 1.0

    # ── 10. Großbuchstaben-Wörter (WIRKLICH, TOTAL) ──
    caps_woerter: int = sum(
        1 for w in turn_text.split()
        if w.isupper() and len(w) >= 3 and not w.isdigit()
    )
    if caps_woerter:
        scores["formell"]    -= 1.0
        scores["emotional"]  += 2.0
        scores["jugendlich"] += 1.0

    # ── 11. Abkürzungen ──
    abkuerzungen: list[str] = ["vllt", "evtl", "bzgl", "mfg", "lg", "vg", "omg", "wtf", "tbh"]
    abk_treffer: int = sum(1 for m in abkuerzungen if f" {m} " in padded)
    if abk_treffer:
        scores["locker"]     += 1.0
        scores["formell"]    -= 1.0
        scores["jugendlich"] += 1.0

    # ── 12. Konjunktiv ──
    konjunktiv_marker: list[str] = ["hätte", "würde", "könnte", "dürfte", "möchte", "wäre", "sollte"]
    konj_treffer: int = sum(1 for m in konjunktiv_marker if f" {m} " in padded)
    if konj_treffer:
        scores["formell"] += 2.0

    # ── 13. Abwesenheit von Slang + Emojis + Abkürzungen ──
    if not slang_treffer and not hat_emoji and not abk_treffer:
        scores["formell"]  += 1.0
        scores["fachlich"] += 1.0

    return scores


def _hash_stil_extrahieren(charakter_hash: dict) -> str:
    """
    Extrahiert einen Stil-Hinweis aus dem Charakter-Hash.

    Sucht zuerst im kommunikations_profil (intentions_profil-Spalte),
    dann im kern_hash als Fallback.
    """

    profil: str = (
        charakter_hash.get("intentions_profil", "")
        or charakter_hash.get("kommunikations_profil", "")
        or ""
    ).lower()

    kern: str = (charakter_hash.get("kern", "") or "").lower()

    suchtext: str = f"{profil} {kern}"

    stil_hinweise: dict[str, list[str]] = {
        "locker":     ["locker", "informell", "umgangston", "entspannt", "kurze sätze"],
        "formell":    ["formell", "höflich", "strukturiert", "vollständige sätze",
                       "korrekte zeichensetzung", "distanziert"],
        "fachlich":   ["fachlich", "analytisch", "präzise", "technisch", "fachbegriffe"],
        "emotional":  ["emotional", "expressiv", "gefühlvoll", "leidenschaftlich"],
        "jugendlich": ["jugendlich", "slang", "umgangssprache", "emojis"],
    }

    for stil, marker in stil_hinweise.items():
        if any(m in suchtext for m in marker):
            return stil

    return "neutral"


def _sprach_stil_erkennen(turns: list[dict], charakter_hash: dict | None) -> str:
    """
    Erkennt den Sprachstil des Users via Feature-Scoring (kein LLM).

    Analysiert die letzten STIL_ANALYSE_TURNS User-Turns. Jeder Turn
    wird einzeln bewertet, die Scores werden über das Fenster akkumuliert.
    Bei Ambiguität dient der Charakter-Hash als Tiebreaker.

    Returns:
        Stilbegriff: "locker", "formell", "fachlich", "emotional",
                     "jugendlich", "neutral"
    """

    # 1. Letzte N User-Turns (Originaltext, nicht lowercased)
    user_turns: list[str] = [
        t.get("inhalt", "")
        for t in turns
        if t.get("rolle") == "user" and t.get("inhalt")
    ][-STIL_ANALYSE_TURNS:]

    if not user_turns:
        return "neutral"

    # 2. Per-Turn Scoring + Akkumulation
    gesamt_scores: dict[str, float] = {
        "locker": 0.0, "formell": 0.0, "fachlich": 0.0,
        "emotional": 0.0, "jugendlich": 0.0,
    }

    for turn_text in user_turns:
        turn_scores: dict[str, float] = _turn_features_bewerten(turn_text)
        for stil, score in turn_scores.items():
            gesamt_scores[stil] += score

    # 3. Session-Stil bestimmen
    max_score: float = max(gesamt_scores.values())

    if max_score < 1.5:
        session_stil: str = "neutral"
    else:
        # Sortieren für Top-1 und Top-2
        sortiert: list[tuple[str, float]] = sorted(
            gesamt_scores.items(), key=lambda x: x[1], reverse=True,
        )
        session_stil = sortiert[0][0]

        # 4. Hash als Tiebreaker bei Ambiguität
        if len(sortiert) >= 2:
            abstand: float = sortiert[0][1] - sortiert[1][1]

            if abstand < 2.0 and charakter_hash:
                hash_stil: str = _hash_stil_extrahieren(charakter_hash)

                if hash_stil != "neutral":
                    for kandidat, score in sortiert:
                        if kandidat == hash_stil and score > 0:
                            logger.info(
                                f"EI-Calc: Stil-Tiebreaker — "
                                f"{session_stil}({sortiert[0][1]:.1f}) vs "
                                f"{sortiert[1][0]}({sortiert[1][1]:.1f}), "
                                f"Hash sagt '{hash_stil}' → übernommen"
                            )
                            session_stil = hash_stil
                            break

    return session_stil


def _ei_arousal_berechnen(
    current_arousal:    float,
    beziehungs_dynamik: str,
    intent:             str,
    tone:               str,
) -> float:
    """
    Berechnet den gewichteten EI-Arousal aus Perzeption-Signalen.

    Kombiniert Beziehungsdynamik, Intent und Tone zu einem Gesamtfaktor,
    der den Roh-Arousal verstärkt oder dämpft. Ergebnis bestimmt,
    ob der Gesprächsmodus "emotional" sein darf/muss.

    Returns:
        Float zwischen 0.0 und 1.0
    """
    dynamik_f: float = EI_DYNAMIK_FAKTOREN.get(beziehungs_dynamik, 1.0)
    intent_f:  float = EI_INTENT_FAKTOREN.get(intent, 1.0)
    tone_f:    float = EI_TONE_FAKTOREN.get(tone, 1.0)

    combined: float = (
        EI_GEWICHTE["dynamik"] * dynamik_f
        + EI_GEWICHTE["intent"] * intent_f
        + EI_GEWICHTE["tone"] * tone_f
    )

    ei_arousal: float = min(1.0, current_arousal * combined)

    logger.info(
        f"EI-Calc: EI-Gate — arousal={current_arousal:.2f} × "
        f"(dyn={dynamik_f}, int={intent_f}, tone={tone_f}) "
        f"= ei_arousal={ei_arousal:.2f}"
    )

    return ei_arousal


def _modus_plausibilitaet(
    emotion:          str,
    ei_arousal:       float,
    perzeption_modus: str,
) -> str:
    """
    Bestimmt den plausiblen Gesprächsmodus basierend auf Emotion und EI-Arousal.
    """
    sektor: int | None = EMOTION_SEKTOR_MAP.get(emotion)
    gruppe: str = SEKTOR_GRUPPE.get(sektor, "neutral") if sektor else "neutral"

    # Sektorlos: emotional blockieren
    if sektor is None:
        if perzeption_modus == "emotional":
            logger.info(
                f"EI-Calc: Modus-Korrektur — emotional → alltag "
                f"(sektorlose Emotion: {emotion})"
            )
            return "alltag"
        return perzeption_modus

    # Passiv-negative (Sektor 5): Immer emotional
    if emotion in EI_PASSIV_NEGATIVE:
        if perzeption_modus != "emotional":
            logger.info(
                f"EI-Calc: Modus-Korrektur — {perzeption_modus} → emotional "
                f"(passiv-negative Emotion: {emotion})"
            )
        return "emotional"

    # Negative Emotionen: Ab Mid-Arousal emotional
    if gruppe == "negativ":
        if ei_arousal > 0.4:
            if perzeption_modus != "emotional":
                logger.info(
                    f"EI-Calc: Modus-Korrektur — {perzeption_modus} → emotional "
                    f"(negative Emotion {emotion}, ei_arousal={ei_arousal:.2f})"
                )
            return "emotional"
        return perzeption_modus

    # Positive Emotionen: Ab High-Arousal emotional
    if gruppe == "positiv":
        if ei_arousal > 0.7:
            if perzeption_modus != "emotional":
                logger.info(
                    f"EI-Calc: Modus-Korrektur — {perzeption_modus} → emotional "
                    f"(positive Emotion {emotion}, ei_arousal={ei_arousal:.2f})"
                )
            return "emotional"
        return perzeption_modus

    # Neutrale Gruppe (Überraschung): Perzeption vertrauen
    return perzeption_modus


def _stil_plausibilitaet(
    emotion:           str,
    ei_arousal:        float,
    perzeption_stil:   str,
    regelbasiert_stil: str,
    tone:              str,
) -> str:
    """
    Prüft ob der Perzeption-Sprachstil plausibel ist.

    Korrigiert "emotional" wenn die Textmerkmale (regelbasiert) das nicht stützen
    und die Emotion neutral ist. Bei echter emotionaler Lage bleibt der Stil.

    Returns:
        Korrigierter oder bestätigter Sprachstil.
    """
    # Bei negativer/positiver Emotion mit relevantem Arousal: Perzeption vertrauen
    sektor: int | None = EMOTION_SEKTOR_MAP.get(emotion)
    gruppe: str = SEKTOR_GRUPPE.get(sektor, "neutral") if sektor else "neutral"
    if gruppe == "negativ" and ei_arousal > 0.4:
        return perzeption_stil
    if gruppe == "positiv" and ei_arousal > 0.7:
        return perzeption_stil

    # Perzeption sagt "emotional" aber Textmerkmale sagen was anderes
    if perzeption_stil == "emotional" and regelbasiert_stil != "emotional":
        # Tone-Check: Wenn Perzeption selbst "sachlich" sagt, Widerspruch
        if tone == "sachlich":
            logger.info(
                f"EI-Calc: Stil-Korrektur — emotional → {regelbasiert_stil} "
                f"(tone=sachlich, regelbasiert={regelbasiert_stil})"
            )
            return regelbasiert_stil if regelbasiert_stil != "neutral" else "neutral"

        # Emotion neutral + Stil emotional = unplausibel
        if sektor is None:  # Sektorlos = neutral
            logger.info(
                f"EI-Calc: Stil-Korrektur — emotional → {regelbasiert_stil} "
                f"(emotion={emotion}, regelbasiert={regelbasiert_stil})"
            )
            return regelbasiert_stil if regelbasiert_stil != "neutral" else "neutral"

    # Sonst: Perzeption übernehmen wenn nicht neutral, sonst regelbasiert
    if perzeption_stil and perzeption_stil != "neutral":
        return perzeption_stil

    return regelbasiert_stil


def _nova_empathie_berechnen(
    nova_verlauf:   list[dict],
    user_emotion:   str,
    user_arousal:   float,
) -> dict:
    """
    Berechnet Novas Emotionszustand unter Empathie-Einfluss des Users.

    Novas eigener Verlauf (aus Decay über ihre Turn-Historie) bildet die
    Grundlage. Der User-Vektor modifiziert Novas Zustand abhängig von der
    Sektor-Distanz im Plutchik-Oktagon — je weiter entfernt Nova und User
    emotional stehen, desto stärker wirkt die Empathie.

    Args:
        nova_verlauf:  Novas decayed Emotions-Verlauf (aus _emotions_verlauf_berechnen
                       auf Novas Turns). Kann leer sein, wenn Nova keine
                       Emotions-Historie hat (bis AP4-7 den async-Pfad baut).
        user_emotion:  Aktuelle kanonische Emotion des Users (aus Perzeption).
        user_arousal:  Aktueller Arousal des Users (aus Perzeption).

    Returns:
        Dict mit:
          nova_emotion:  str   — Novas dominante Emotion für diesen Turn
          nova_arousal:  float — Novas Arousal für diesen Turn
          nova_konflikt: bool  — True wenn Empathie und eigener Zustand
                                 in gegenüberliegende Sektoren zeigen
          nova_verlauf_modifiziert: list[dict] — Novas Verlauf mit
                                                 Empathie-Einfluss
    """

    user_emotion_kanon: str = _emotion_kanonisieren(user_emotion)

    # ── 1. Novas Baseline bestimmen ──
    if nova_verlauf:
        nova_dominant:         str   = nova_verlauf[0]["emotion"]
        nova_dominant_arousal: float = nova_verlauf[0].get("arousal", 0.5)
    else:
        nova_dominant         = "neutral"
        nova_dominant_arousal = 0.2

    # ── 2. Sektor-Distanz berechnen ──
    nova_sektor: int | None = EMOTION_SEKTOR_MAP.get(nova_dominant)
    user_sektor: int | None = EMOTION_SEKTOR_MAP.get(user_emotion_kanon)

    if nova_sektor is not None and user_sektor is not None:
        # Kürzeste Distanz auf dem Kreis (8 Sektoren)
        direkt:  int = abs(nova_sektor - user_sektor)
        distanz: int = min(direkt, 8 - direkt)
        alpha:   float = EMPATHIE_ALPHA.get(distanz, EMPATHIE_ALPHA_NEUTRAL)
    else:
        # Mindestens eine Seite ist neutral/sektorlos
        distanz = -1
        alpha   = EMPATHIE_ALPHA_NEUTRAL

    # ── 3. Empathie-Einfluss berechnen ──
    # User-Emotion wird mit Gewicht alpha × user_arousal in Novas Verlauf injiziert
    empathie_gewicht: float = alpha * user_arousal

    modifiziert: list[dict] = list(nova_verlauf)  # Shallow copy

    if user_emotion_kanon and user_emotion_kanon != "neutral" and empathie_gewicht > 0.05:
        # Prüfen ob User-Emotion schon in Novas Verlauf existiert
        gefunden: bool = False
        for eintrag in modifiziert:
            if eintrag["emotion"] == user_emotion_kanon:
                # Boosten: bestehendes Gewicht + Empathie
                eintrag["gewicht"] = round(
                    min(1.0, eintrag["gewicht"] + empathie_gewicht), 2
                )
                eintrag["arousal"] = round(
                    max(eintrag["arousal"], user_arousal * alpha), 2
                )
                gefunden = True
                break

        if not gefunden:
            # Neue Emotion injizieren
            modifiziert.append({
                "emotion": user_emotion_kanon,
                "gewicht": round(empathie_gewicht, 2),
                "arousal": round(user_arousal * alpha, 2),
            })

        # Neu sortieren
        modifiziert.sort(key=lambda e: e["gewicht"], reverse=True)

    # ── 4. Novas resultierende Emotion bestimmen ──
    if modifiziert:
        nova_emotion_resultat: str   = modifiziert[0]["emotion"]
        nova_arousal_resultat: float = modifiziert[0].get("arousal", 0.3)
    else:
        nova_emotion_resultat = "neutral"
        nova_arousal_resultat = 0.2

    # ── 5. Konflikterkennung ──
    konflikt: bool = False
    if distanz >= EMPATHIE_KONFLIKT_DISTANZ:
        if (nova_dominant_arousal >= EMPATHIE_KONFLIKT_MIN_AROUSAL
                and user_arousal >= EMPATHIE_KONFLIKT_MIN_AROUSAL):
            konflikt = True
            logger.info(
                f"EI-Calc: Empathie-Konflikt — Nova={nova_dominant}(a={nova_dominant_arousal:.2f}), "
                f"User={user_emotion_kanon}(a={user_arousal:.2f}), Distanz={distanz}"
            )

    # ── Logging ──
    logger.info(
        f"EI-Calc: Nova-Empathie — Basis={nova_dominant}, "
        f"User={user_emotion_kanon}(a={user_arousal:.2f}), "
        f"Distanz={distanz}, α={alpha:.2f}, "
        f"Ergebnis={nova_emotion_resultat}(a={nova_arousal_resultat:.2f})"
    )

    return {
        "nova_emotion":              nova_emotion_resultat,
        "nova_arousal":              nova_arousal_resultat,
        "nova_konflikt":             konflikt,
        "nova_verlauf_modifiziert":  modifiziert,
    }
