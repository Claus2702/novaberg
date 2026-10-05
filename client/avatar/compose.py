"""Ein ganzes Bild des Gesichts aus einer Pose, wie `frame` im Prototyp ohne Testbedienung.

Reihenfolge: Hintergrund, Atmen (Streckung um die Mitte der Unterkante),
Halsebene fest, Gesichtsebene mit dem Kiefer verzerrt, dann Brauen, Augen, Mund
und Extras (Brauenfalten, Röte, Träne, Schweiß). Von den drei Fassungen der
Ebenen gilt in jedem Takt der Strichlage die Fassung `boil_tick % 3`.

Die Zeit der fallenden Träne folgt aus dem Takt: Der Takt zählt `BOIL_MS`
Millisekunden wie `Math.floor(t / 110)` im Prototyp, die Träne rückt also im Takt
der Strichlage vor statt stetig.

Ist der Kopf um mehr als `TURN_MIN` Grad gedreht, wird das Bild ohne Atem — Hals,
verzerrtes Gesicht und alle Züge — zuerst auf eine Zwischenfläche gezeichnet und diese
dann mit dem Drehgitter (`avatar.head_turn`) aufgelegt, mit Atem und Maßstab. Bis
`TURN_MIN` bleibt der Zeichenweg genau der ungedrehte.

Das Modul importiert weder Cairo noch GTK. Runde Linienenden und -ecken stehen als
Zahl (`LINE_CAP_ROUND`, `LINE_JOIN_ROUND`); Verläufe, Matrizen und neue Flächen
bauen die Adapter in `FaceTools`.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avatar.base_image import JAW_TOLERANCE, Canvas, WarpCache, paint_layer, warped_face
from avatar.drawing import check_face, draw_brows, draw_extras, draw_eyes
from avatar.drawing_tools import SRC, Gradients, check_tick, set_rgba
from avatar.head_turn import TURN_MIN, draw_turned, yaw_grid, yaw_triangles
from avatar.idle_catalog import YAW_MAX as HEAD_YAW_MAX
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
    −1..1, `boil_tick` ganze Zahl ≥ 0, `head_yaw` in −15..15 Grad.
    Fehlerfälle: TypeError, wenn `head_yaw` keine Zahl ist.
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
    yaw = pose.head_yaw
    if isinstance(yaw, bool) or not isinstance(yaw, int | float):
        raise TypeError(f"{where}: head_yaw {yaw!r} keine Zahl")
    if not abs(yaw) <= HEAD_YAW_MAX:
        raise ValueError(f"{where}: head_yaw {yaw!r} außerhalb ±{HEAD_YAW_MAX:g}°")

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
    Fassung `boil_tick % 3` für den Kiefer der Pose. Bei |`head_yaw`| > `TURN_MIN`
    liegt das Bild durch das Drehgitter auf `cr`: die Zwischenfläche als Unterlage,
    darüber die verschobenen Dreiecke; sonst zeichnet es wie ohne Drehung.
    Fehlerfälle: ValueError bei verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ──
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise ValueError(f"draw_face: Größe {size!r} ungültig")
    check_pose(pose, "draw_face")
    if not isinstance(layers, AvatarLayers):
        raise ValueError(f"draw_face: {layers!r} sind keine AvatarLayers")

    # ── Verarbeitung ──
    variant = pose.boil_tick % LAYER_VARIANTS
    jaw = max(0.0, pose.face.jaw)
    warped = warped_face(tools.warp_cache, tools.canvas, layers.face[variant], variant, jaw)
    turned = abs(pose.head_yaw) > TURN_MIN
    triangles = yaw_triangles(yaw_grid(pose.head_yaw)) if turned else []
    cr.save()
    set_rgba(cr, BACKGROUND, 1.0)
    cr.rectangle(0, 0, size, size)
    cr.fill()
    cr.translate(size / 2, size)
    cr.scale(1 + pose.breath * BREATH_X, 1 + pose.breath * BREATH_Y)
    cr.translate(-size / 2, -size)
    cr.scale(size / SRC, size / SRC)
    if turned:
        head, ctx = tools.canvas.new_surface(size, size)
        ctx.scale(size / SRC, size / SRC)
        _draw_head(ctx, pose, layers, tools, warped)
        draw_turned(cr, tools.canvas, head, triangles)
    else:
        _draw_head(cr, pose, layers, tools, warped)
    cr.restore()

    # ── Ausgabe-Verifikation ──
    entry = tools.warp_cache.entries.get(variant)
    if entry is None or entry.surface is not warped or abs(entry.jaw - jaw) > JAW_TOLERANCE:
        raise RuntimeError("draw_face: Zwischenspeicher trägt die gezeichnete Ebene nicht")


def _draw_head(
    ctx: "cairo.Context", pose: Pose, layers: AvatarLayers, tools: FaceTools, warped: object
) -> None:
    """Hals, verzerrtes Gesicht und alle Züge auf `ctx`, in Pixeln der Vorlage.

    Vorbedingung: `ctx` steht in Pixeln der Vorlage; `warped` ist die verzerrte
    Gesichtsebene der Fassung `boil_tick % 3` aus dem Zwischenspeicher.
    Nachbedingung: Halsebene, Gesichtsebene, Brauen, Augen, Mund und Extras auf `ctx`,
    in dieser Reihenfolge, mit runden Linienenden und -ecken.
    Fehlerfälle: ValueError, wenn `warped` nicht die Ebene der Fassung im Zwischenspeicher ist.
    """
    # ── Eingabe-Validierung ──
    face, tick = pose.face, pose.boil_tick
    variant = tick % LAYER_VARIANTS
    entry = tools.warp_cache.entries.get(variant)
    if entry is None or entry.surface is not warped:
        raise ValueError("_draw_head: Gesichtsebene nicht aus dem Zwischenspeicher")

    # ── Verarbeitung ──
    paint_layer(ctx, layers.neck[variant])
    paint_layer(ctx, warped)
    ctx.set_line_cap(LINE_CAP_ROUND)
    ctx.set_line_join(LINE_JOIN_ROUND)
    draw_brows(ctx, face, tick)
    draw_eyes(ctx, tools.gradients, pose)
    draw_mouth(ctx, tools.gradients, face, pose.tongue, tick)
    draw_extras(ctx, face, float(tick * BOIL_MS), tick)

    # Keine Ausgabe-Verifikation: Die Zeichner prüfen ihre Eingaben selbst und
    # schreiben nur auf `ctx`.
