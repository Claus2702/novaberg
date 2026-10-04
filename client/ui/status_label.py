"""Eine Zeile der Phasenanzeige: eine Zeile hoch, am Ende gekürzt, voller Text im Tooltip.

Ein Umbruch macht die Anzeige vom Text abhängig hoch und drückt das Gesicht darüber
zusammen; deshalb bricht keine Zeile um.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Pango  # noqa: E402


def status_label() -> Gtk.Label:
    """Legt eine Zeile der Phasenanzeige an.

    Vorbedingung: GTK ist initialisiert.
    Nachbedingung: das Label bricht nicht um, kürzt am Ende mit „…“, steht linksbündig
    und trägt die Klasse `dim-label`.
    """
    # ── Eingabe-Validierung ──
    # Keine Eingabe.

    # ── Verarbeitung ──
    label = Gtk.Label()
    label.set_xalign(0.0)
    label.set_wrap(False)
    label.set_ellipsize(Pango.EllipsizeMode.END)
    label.add_css_class("dim-label")

    # ── Ausgabe-Verifikation ──
    if label.get_wrap() or label.get_ellipsize() != Pango.EllipsizeMode.END:
        raise RuntimeError("status_label: Zeile nicht auf Kürzung am Ende gestellt")
    return label


def set_status_text(label: Gtk.Label, text: str, bold: bool = False) -> None:
    """Setzt den Text einer Zeile und legt ihn ungekürzt in den Tooltip.

    Vorbedingung: `label` kommt aus `status_label()`, `text` ist nicht leer.
    Nachbedingung: die Zeile zeigt `text` (fett bei `bold`), der Tooltip trägt ihn ganz.
    """
    # ── Eingabe-Validierung ──
    if not isinstance(label, Gtk.Label):
        raise TypeError(f"set_status_text: Label erwartet, bekam {type(label).__name__}")
    if not text:
        raise ValueError("set_status_text: Zeile ohne Text")

    # ── Verarbeitung ──
    if bold:
        label.set_markup(f"<b>{GLib.markup_escape_text(text)}</b>")
    else:
        label.set_text(text)
    label.set_tooltip_text(text)

    # ── Ausgabe-Verifikation ──
    if label.get_tooltip_text() != text:
        raise RuntimeError("set_status_text: Tooltip trägt nicht den vollen Text")
