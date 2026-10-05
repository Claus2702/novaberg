"""Das Label des Untertitels: immer zwei Zeilen hoch, zentriert, am Ende gekürzt.

Eine feste Höhe, damit das Gesicht darüber nicht springt, wenn ein Untertitel erscheint oder
verschwindet. Passt eine Tafel nicht in zwei Zeilen, kürzt das Label sie mit „…“.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

SUBTITLE_LINES = 2
SUBTITLE_SCALE = 1.35  # größer als die Phasenanzeige


def subtitle_label() -> Gtk.Label:
    """Legt das Label des Untertitels an, leer und schon zwei Zeilen hoch.

    Vorbedingung: GTK ist initialisiert.
    Nachbedingung: das Label bricht um, zeigt höchstens zwei Zeilen, kürzt am Ende, steht
    zentriert und ist so hoch wie zwei Zeilen seiner Schrift, auch ohne Text.
    """
    # ── Eingabe-Validierung ──
    # Keine Eingabe.

    # ── Verarbeitung ──
    label = Gtk.Label()
    label.set_wrap(True)
    label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    label.set_lines(SUBTITLE_LINES)
    label.set_ellipsize(Pango.EllipsizeMode.END)
    label.set_justify(Gtk.Justification.CENTER)
    label.set_xalign(0.5)
    label.set_hexpand(True)
    attributes = Pango.AttrList()
    attributes.insert(Pango.attr_scale_new(SUBTITLE_SCALE))
    label.set_attributes(attributes)
    label.set_text("A\nA")  # zwei Zeilen messen, dann leeren
    height = label.measure(Gtk.Orientation.VERTICAL, -1)[1]
    label.set_text("")
    label.set_size_request(-1, height)

    # ── Ausgabe-Verifikation ──
    if height <= 0 or label.get_text() != "":
        raise RuntimeError(f"subtitle_label: Höhe {height} oder Text nicht leer")
    if not label.get_wrap() or label.get_lines() != SUBTITLE_LINES:
        raise RuntimeError("subtitle_label: Label nicht auf zwei Zeilen begrenzt")
    return label


def set_subtitle_markup(label: Gtk.Label, markup: str) -> None:
    """Setzt den Untertitel als Pango-Markup; der leere Text leert das Label.

    Vorbedingung: `label` kommt aus `subtitle_label()`, `markup` ist gültiges Markup
    (`subtitle_markup` escaped den Text).
    Nachbedingung: das Label zeigt `markup`; die Höhe bleibt, wie sie war.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(label, Gtk.Label):
        raise TypeError(f"set_subtitle_markup: Label erwartet, bekam {type(label).__name__}")
    if not isinstance(markup, str):
        raise TypeError(f"set_subtitle_markup: Markup ist kein str: {type(markup).__name__}")

    # ── Verarbeitung ──
    label.set_markup(markup)

    # ── Ausgabe-Verifikation ──
    if bool(markup) != bool(label.get_text()):
        raise RuntimeError("set_subtitle_markup: Label zeigt nicht, was gesetzt wurde")
