"""Ein ganzes Bild des Gesichts aus einer Pose, wie `frame` im Prototyp ohne Testbedienung.

Reihenfolge: Hintergrund, Atmen (Streckung um die Mitte der Unterkante),
Halsebene fest, Gesichtsebene mit dem Kiefer verzerrt, dann Brauen, Augen, Mund
und Extras (Brauenfalten, Röte, Träne, Schweiß). Von den drei Fassungen der
Ebenen gilt in jedem Takt der Strichlage die Fassung `boil_tick % 3`.

Die Zeit der fallenden Träne folgt aus dem Takt: Der Takt zählt `BOIL_MS`
Millisekunden wie `Math.floor(t / 110)` im Prototyp, die Träne rückt also im Takt
der Strichlage vor statt stetig.

Das Modul importiert weder Cairo noch GTK. Runde Linienenden und -ecken stehen als
Zahl (`LINE_CAP_ROUND`, `LINE_JOIN_ROUND`); Verläufe, Matrizen und neue Flächen
bauen die Adapter in `FaceTools`.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avatar.base_image import JAW_TOLERANCE, Canvas, WarpCache, paint_layer, warped_face
from avatar.drawing import check_face, draw_brows, draw_extras, draw_eyes
from avatar.drawing_tools import SRC, Gradients, check_tick, set_rgba
from avatar.layers import LAYER_VARIANTS, AvatarLayers
from avatar.mouth_drawing import draw_mouth
from avatar.pose import Pose

if TYPE_CHECKING:
    import cairo

BACKGROUND = (251.0, 251.0, 248.0)  # #fbfbf8
BREATH_X = 0.003  # Streckung durch den Atem, quer
BREATH_Y = 0.005  # und längs
BOIL_MS = 110  # Dauer eines Takts der Strichlage in Millisekunden
# Werte von `cairo.LINE_CAP_ROUND` und `cairo.LINE_JOIN_ROUND` (Enums `cairo.LineCap`,
# `cairo.LineJoin`), als Zahl, damit das Modul ohne pycairo lädt.
LINE_CAP_ROUND = 1
LINE_JOIN_ROUND = 1


@dataclass
class FaceTools:
    """Was das Zeichnen über die Pose hinaus braucht und der Aufrufer über die Bilder hält."""

    gradients: Gradients  # `CairoGradients` im Client
    canvas: Canvas  # `CairoCanvas` im Client
    warp_cache: WarpCache


def check_pose(pose: Pose, where: str) -> None:
    """Wirft ValueError, wenn `pose` keine gültige Pose ist.

    Gültig: `face` mit endlichen Kanälen, `tongue` und `blink` in 0..1, `breath` in
    −1..1, `boil_tick` ganze Zahl ≥ 0.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(pose, Pose):
        raise ValueError(f"{where}: {pose!r} ist keine Pose")

    # ── Verarbeitung ──
    check_face(pose.face, where)
    check_tick(pose.boil_tick, where)
    ranges = (
        ("tongue", pose.tongue, 0.0),
        ("blink", pose.blink, 0.0),
        ("breath", pose.breath, -1.0),
    )
    for name, value, low in ranges:
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ValueError(f"{where}: {name} {value!r} keine Zahl")
        if not low <= value <= 1.0:
            raise ValueError(f"{where}: {name} {value!r} außerhalb {low:g}..1")

    # Keine Ausgabe-Verifikation: Rückkehr heißt gültig.


def draw_face(
    cr: "cairo.Context", size: int, pose: Pose, layers: AvatarLayers, tools: FaceTools
) -> None:
    """Zeichnet ein ganzes Bild des Gesichts auf `size` × `size` Pixel.

    `cr` steht beim Aufruf in Gerätepixeln ohne Verschiebung; das Bild füllt das
    Quadrat von (0, 0) bis (`size`, `size`).
    Vorbedingung: `size` ganze Zahl > 0, gültige Pose (`check_pose`), `layers` aus
    `load_layers`.
    Nachbedingung: Hintergrund, Hals, verzerrtes Gesicht und alle Züge auf `cr`; `cr`
    steht danach wieder wie vorher; der Zwischenspeicher trägt die verzerrte Ebene der
    Fassung `boil_tick % 3` für den Kiefer der Pose.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise ValueError(f"draw_face: Größe {size!r} ungültig")
    check_pose(pose, "draw_face")
    if not isinstance(layers, AvatarLayers):
        raise ValueError(f"draw_face: {layers!r} sind keine AvatarLayers")

    # ── Verarbeitung ──
    face, tick = pose.face, pose.boil_tick
    variant = tick % LAYER_VARIANTS
    jaw = max(0.0, face.jaw)
    warped = warped_face(tools.warp_cache, tools.canvas, layers.face[variant], variant, jaw)
    cr.save()
    set_rgba(cr, BACKGROUND, 1.0)
    cr.rectangle(0, 0, size, size)
    cr.fill()
    cr.translate(size / 2, size)
    cr.scale(1 + pose.breath * BREATH_X, 1 + pose.breath * BREATH_Y)
    cr.translate(-size / 2, -size)
    cr.scale(size / SRC, size / SRC)
    paint_layer(cr, layers.neck[variant])
    paint_layer(cr, warped)
    cr.set_line_cap(LINE_CAP_ROUND)
    cr.set_line_join(LINE_JOIN_ROUND)
    draw_brows(cr, face, tick)
    draw_eyes(cr, tools.gradients, face, pose.blink, tick)
    draw_mouth(cr, tools.gradients, face, pose.tongue, tick)
    draw_extras(cr, face, float(tick * BOIL_MS), tick)
    cr.restore()

    # ── Ausgabe-Verifikation ──
    entry = tools.warp_cache.entries.get(variant)
    if entry is None or entry.surface is not warped or abs(entry.jaw - jaw) > JAW_TOLERANCE:
        raise RuntimeError("draw_face: Zwischenspeicher trägt die gezeichnete Ebene nicht")
