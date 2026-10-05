"""Die Pose: alles, was das Zeichnen eines Bildes vom Gesicht braucht.

Animator und Sprechen liefern sie, das Zeichnen liest sie. Sie trägt keine Uhr:
Der Takt der Strichlage (`boil_tick`) ist schon eine ganze Zahl, Atem und
Blinzeln sind schon ausgewertet.
"""

from dataclasses import dataclass

from avatar.face import FaceState


@dataclass(frozen=True)
class Pose:
    """Ein Bild des Gesichts, wie es gezeichnet werden soll."""

    face: FaceState  # sichtbarer Zustand nach der Zusammenführung mit dem Sprechen
    tongue: float  # Zungenhöhe 0..1 (0 Mundboden, 1 Spitze am Gaumen)
    blink: float  # 1 offen, 0 geschlossen
    breath: float  # Atem in -1..1, der Sinus des Atemzugs
    boil_tick: int  # Takt der Strichlage, ganze Zahl ≥ 0
    # Drehung des Kopfes in Grad, wie die Kopffeder sie zeigt (plus = nach rechts aus
    # Sicht des Betrachters), |Wert| ≤ 15. Ohne Angabe 0: Wer keinen Kopf führt, zeigt
    # ihn gerade.
    head_yaw: float = 0.0
