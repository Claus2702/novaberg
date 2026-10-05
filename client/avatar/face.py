"""Datentypen des Gesichts: ein Feld je Kanal, dazu der Neutralzustand.

Die Werte stehen in den Einheiten der Vorlage, nicht normiert: Brauen, Mund und
Kiefer in Pixeln, Augenöffnung und Pupille als Faktor (1 = neutral), Blick in
-1..1, Röte, Träne, Schweiß und die Mundmuskeln nach FACS in 0..1.

`PROTOTYPE_KEYS` ordnet jedem Feld den Kurznamen des Kanals im Prototyp zu. Über
ihn werden die Schlüsselbilder geschrieben und die Referenzwerte gelesen; die
Reihenfolge ist die des Prototyps.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FaceState:
    """Ein Zustand des Gesichts — Ziel, sichtbarer Zustand oder Geschwindigkeit je Kanal."""

    brow_left_inner: float  # bli, Pixel, negativ = hoch
    brow_left_outer: float  # blo
    brow_right_inner: float  # bri
    brow_right_outer: float  # bro
    eye_open: float  # eo, Faktor, 1 = neutral
    eye_arc: float  # arc, Überblendung zu Lachaugen
    lid_upper: float  # lidU, hängendes Oberlid
    gaze_x: float  # gx
    gaze_y: float  # gy
    pupil_size: float  # ps, Faktor
    brow_arch: float  # barch, Pixel, negativ = runder Bogen
    mouth_curve: float  # mc, Pixel, positiv = Lächeln
    mouth_open: float  # mo, Lippenöffnung in Pixeln
    jaw: float  # jaw, Kieferöffnung in Pixeln
    mouth_width: float  # mw, Pixel
    mouth_asym: float  # ma, Pixel
    blush: float  # blush
    tear: float  # tear
    sweat: float  # sweat
    # Mundmuskeln nach FACS, paarige je Seite aus Sicht der Figur
    au10_left: float  # au10L, Oberlippenheber
    au10_right: float  # au10R
    au12_left: float  # au12L, Jochbeinmuskel
    au12_right: float  # au12R
    au15_left: float  # au15L, Mundwinkelsenker
    au15_right: float  # au15R
    au16_left: float  # au16L, Unterlippensenker
    au16_right: float  # au16R
    au20_left: float  # au20L, Lachmuskel
    au20_right: float  # au20R
    au17: float  # Kinnmuskel
    au18: float  # Lippen spitzen
    au22: float  # Lippen trichterförmig vorstülpen
    au23: float  # Lippen spannen
    au24: float  # Lippen pressen
    au28: float  # Unterlippe unter die Oberzähne


PROTOTYPE_KEYS: dict[str, str] = {
    "brow_left_inner": "bli",
    "brow_left_outer": "blo",
    "brow_right_inner": "bri",
    "brow_right_outer": "bro",
    "eye_open": "eo",
    "eye_arc": "arc",
    "lid_upper": "lidU",
    "gaze_x": "gx",
    "gaze_y": "gy",
    "pupil_size": "ps",
    "brow_arch": "barch",
    "mouth_curve": "mc",
    "mouth_open": "mo",
    "jaw": "jaw",
    "mouth_width": "mw",
    "mouth_asym": "ma",
    "blush": "blush",
    "tear": "tear",
    "sweat": "sweat",
    "au10_left": "au10L",
    "au10_right": "au10R",
    "au12_left": "au12L",
    "au12_right": "au12R",
    "au15_left": "au15L",
    "au15_right": "au15R",
    "au16_left": "au16L",
    "au16_right": "au16R",
    "au20_left": "au20L",
    "au20_right": "au20R",
    "au17": "au17",
    "au18": "au18",
    "au22": "au22",
    "au23": "au23",
    "au24": "au24",
    "au28": "au28",
}

# Grad Augendrehung je Einheit gx: Die Iris wandert 0,5 · hw je Einheit (IRIS_TRAVEL_X),
# und 0,075 · hw entsprechen etwa 5°. Die Entfernung des fixierten Punkts ist
# vernachlässigt (bei 5 m: +2 %). Plan und Zeichnung des Blickhalts lesen dieselbe Zahl.
EYE_DEG_PER_GAZE = 34.0

NEUTRAL = FaceState(
    brow_left_inner=0.0,
    brow_left_outer=0.0,
    brow_right_inner=0.0,
    brow_right_outer=0.0,
    eye_open=1.0,
    eye_arc=0.0,
    lid_upper=0.0,
    gaze_x=0.0,
    gaze_y=0.0,
    pupil_size=1.0,
    brow_arch=0.0,
    mouth_curve=4.0,
    mouth_open=0.0,
    jaw=0.0,
    mouth_width=78.0,
    mouth_asym=0.0,
    blush=0.0,
    tear=0.0,
    sweat=0.0,
    au10_left=0.0,
    au10_right=0.0,
    au12_left=0.0,
    au12_right=0.0,
    au15_left=0.0,
    au15_right=0.0,
    au16_left=0.0,
    au16_right=0.0,
    au20_left=0.0,
    au20_right=0.0,
    au17=0.0,
    au18=0.0,
    au22=0.0,
    au23=0.0,
    au24=0.0,
    au28=0.0,
)
