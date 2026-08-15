"""Eigenzeit: was zwischen zwei Turns mit Novas Zustand geschieht.

**Ausloeser ist die Nutzeraeusserung, nicht die Uhr.** Kein Hintergrundlauf
dreht etwas herunter. Trifft eine Aeusserung ein, wird das Intervall seit der
vorigen bestimmt und der gespeicherte Zustand fuer diesen Turn entsprechend
gesenkt; danach zieht die Wahrnehmung der Aeusserung ihn wieder hinauf — von
dem Wert aus, auf den er gefallen ist.

Zwei Groessen, zwei Bauarten:

* **Die Erregung ist eine Zahl.** Sie wird zur Ruhelage hin gezogen, nicht
  gegen null multipliziert: 0,00 waere keine Ruhe, sondern ein toter Wert.
* **Modus, Sprachstil, Ton und Emotion sind Kategorien.** Sie kennen keinen
  Zwischenwert und **springen** auf ihren Neutralwert, sobald die Kurve unter
  die Schwelle faellt. Ein halber Modus bedeutet nichts.

**Gedaempft wird das Fluechtige, nicht das Bindende.** Naehe, Tiefe und
Beziehungsdynamik bleiben unberuehrt — wer morgens hereinkommt, soll eine
ruhige Nova vorfinden, keine fremde. Der Raumzug laeuft ausdruecklich ueber
mehrere Turns; ein taeglicher Rueckbau naehme ihm seinen Gegenstand.

Konzept: novaberg-eigenzeit_k.md §2.2 (die Kurve), §5.1 (Bauteil A).
"""

import logging

from config import (
    EIGENZEIT_AROUSAL_RUHE,
    EIGENZEIT_HALBWERT_FAKTOR,
    EIGENZEIT_HALBWERT_SEKUNDEN,
    EIGENZEIT_KATEGORIE_SCHWELLE,
    EIGENZEIT_KIPPPUNKT_FAKTOR,
    EIGENZEIT_KIPPPUNKT_SEKUNDEN,
    EIGENZEIT_NULLPUNKT_SEKUNDEN,
)

logger = logging.getLogger("ki_server.ei.eigenzeit")


# Die Neutralwerte der Kategorien. Sie stammen aus `Wahrnehmung()` in
# `graph/nodes/perzeption.py` — dem Ausfallwert der Wahrnehmung — und werden
# hier bewusst wiederholt statt importiert: Der Neutralwert einer Kategorie
# ist die Ruhelage, in die der Verfall zurueckfaellt, und das ist eine andere
# Aussage als „was die Wahrnehmung liefert, wenn sie nichts erkennt". Faellt
# eine der beiden Bedeutungen weg, soll die andere nicht stillschweigend
# mitwandern.
KATEGORIE_NEUTRAL: dict[str, str] = {
    "emotion":        "neutral",
    "mode":           "alltag",
    "language_style": "neutral",
    "tone":           "sachlich",
}


def verfall_faktor(pause_sekunden: float) -> float:
    """Bestimmt den Daempfungsfaktor fuer eine Pause.

    Die Kurve laeuft ueber drei Marken — Kipppunkt, Halbwert, Nullpunkt — und
    interpoliert linear dazwischen. Sie faellt erst flach, dann steil, dann auf
    null; ein Exponentialverfall waere falsch, weil er sofort am steilsten
    faellt und jeder kurzen Unterbrechung ihre Energie naehme.

    Args:
        pause_sekunden: Abstand zur letzten Nutzeraeusserung. Negative Werte
            gelten als 0 — eine Uhr, die rueckwaerts laeuft, ist kein Grund,
            etwas zu daempfen.

    Returns:
        Faktor in [0.0, 1.0]. 1.0 heisst unveraendert, 0.0 vollstaendig
        zurueckgefallen.
    """
    # ── Eingabe ─────────────────────────────────
    if pause_sekunden <= 0.0:
        return 1.0

    # ── Verarbeitung ────────────────────────────
    # Stuetzstellen der Kurve, aufsteigend nach Zeit.
    stuetzstellen: list[tuple[float, float]] = [
        (0.0,                           1.0),
        (EIGENZEIT_KIPPPUNKT_SEKUNDEN,  EIGENZEIT_KIPPPUNKT_FAKTOR),
        (EIGENZEIT_HALBWERT_SEKUNDEN,   EIGENZEIT_HALBWERT_FAKTOR),
        (EIGENZEIT_NULLPUNKT_SEKUNDEN,  0.0),
    ]

    if pause_sekunden >= EIGENZEIT_NULLPUNKT_SEKUNDEN:
        return 0.0

    for (t_links, f_links), (t_rechts, f_rechts) in zip(
        stuetzstellen, stuetzstellen[1:], strict=False
    ):
        if t_links <= pause_sekunden < t_rechts:
            spanne: float = t_rechts - t_links
            if spanne <= 0.0:
                # Zwei Marken auf derselben Zeit — die Konfiguration ist
                # widerspruechlich. Der rechte Wert gewinnt, und es wird
                # gesagt statt stillschweigend geteilt.
                logger.error(
                    "Eigenzeit: Marken bei %.0f s fallen zusammen — "
                    "Konfiguration pruefen (Kipppunkt/Halbwert/Nullpunkt)",
                    t_links,
                )
                return f_rechts
            anteil: float = (pause_sekunden - t_links) / spanne
            return f_links + (f_rechts - f_links) * anteil

    # ── Ausgabe ─────────────────────────────────
    # Unerreichbar, solange die Marken aufsteigend sind. Wenn nicht, ist das
    # ein Konfigurationsfehler und keine Rundungsfrage.
    logger.error(
        "Eigenzeit: Pause %.0f s liegt in keiner Spanne — Marken nicht "
        "aufsteigend? (%.0f / %.0f / %.0f)",
        pause_sekunden,
        EIGENZEIT_KIPPPUNKT_SEKUNDEN,
        EIGENZEIT_HALBWERT_SEKUNDEN,
        EIGENZEIT_NULLPUNKT_SEKUNDEN,
    )
    return 1.0


def arousal_daempfen(arousal: float, faktor: float) -> float:
    """Zieht die Erregung anteilig zur Ruhelage.

    Args:
        arousal: Der gespeicherte Wert.
        faktor: Ergebnis von `verfall_faktor`.

    Returns:
        Bei Faktor 1.0 der Ausgangswert, bei 0.0 die Ruhelage.
    """
    return EIGENZEIT_AROUSAL_RUHE + (arousal - EIGENZEIT_AROUSAL_RUHE) * faktor


def kategorien_gesprungen(faktor: float) -> bool:
    """Sagt, ob die Kategorien auf ihren Neutralwert zurueckfallen.

    Args:
        faktor: Ergebnis von `verfall_faktor`.

    Returns:
        True, wenn der Faktor unter der Schwelle liegt.
    """
    return faktor < EIGENZEIT_KATEGORIE_SCHWELLE
