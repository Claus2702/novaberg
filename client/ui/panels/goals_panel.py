"""
Ziele-Panel — Drive-System: Langfristige, mittelfristige und kurzfristige Ziele.

Liest ``GET /drive/goals`` und zeigt:

* Config-Zeile mit den aktuellen Drive-Schwellwerten.
* Langfristige Ziele aus der Charakter-Destillation.
* Mittelfristige Ziele aus den Pixie-Agenten (mit Decay).
* Kurzfristige Aktivitaet (Gespraechsvektor + aktivierte Ziele +
  Gravitationsterm) — vom Dispatcher nach jedem Turn in Redis abgelegt.

Das Panel ist ``turn_reactive``: nach jedem Turn ruft die MainWindow-
Verdrahtung ``on_turn_received`` auf, das einen Refresh ausloest.

Response-Format (siehe ``server/api/drive.py``):

    {
        "long_term":  [ { id, goal_text, motivation, emotion, arousal,
                          active, created_at, updated_at }, ... ],
                      — aktiv UND inaktiv; das Panel zeigt seit dem 28.08.2026
                        nur die aktiven als Karten und nennt die Zahl der
                        ausgeblendeten (Wunsch: der Tab war voller Streichungen)
        "mid_term":   [ ... ],
        "short_term": null | {
            "conversation_vector": str,
            "activated_goals":     [ { goal_text, similarity, motivation,
                                       gravity_strength } ],
            "gravity_term":        float,
            "timestamp":           str
        },
        "config": {
            "gravity_threshold": float,
            "salience_factor":   float,
            "max_long_term":     int,
            "max_mid_term":      int,
            "decay_days":        int
        }
    }
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.formatierung import zeit_kurz  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


class GoalsPanel(PanelBase):
    """Anzeige fuer Novas Drive-System (Ziele und Gravitation)."""

    PANEL_ID    = "ziele"
    PANEL_LABEL = "🎯 Ziele & Antrieb"
    UNIQUE      = True
    CATEGORY    = "turn_reactive"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH  = 550
    DEFAULT_HEIGHT = 700

    def _build_content(self) -> None:
        """Scrollbarer Container mit Sektionen fuer alle drei Ziel-Ebenen."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        scroll.set_child(self._outer_box)

        placeholder = Gtk.Label(label="Lade Ziele …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._outer_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt Ziele und aktuellen Drive-Zustand vom Server.

        Auch wenn die Ziele immer Novas sind, wird ``_get_api_params()``
        aus Konsistenzgruenden aufgerufen — die Werte werden serverseitig
        nicht ausgewertet.
        """
        _ = self._get_api_params()
        url: str = f"{SERVER_URL}/drive/goals"
        logger.debug(f"GoalsPanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Baut alle Sektionen neu auf."""
        long_term:  list = data.get("long_term")  or []
        mid_term:   list = data.get("mid_term")   or []
        short_term: dict | None = data.get("short_term")
        config:     dict = data.get("config")     or {}

        logger.info(
            f"GoalsPanel: {len(long_term)} long_term, "
            f"{len(mid_term)} mid_term, "
            f"short_term={'gefuellt' if short_term else 'leer'}"
        )

        _clear_box(self._outer_box)

        self._outer_box.append(_build_config_row(config))
        self._outer_box.append(_build_section(
            titel="Langfristige Ziele",
            ziele=long_term,
            zeige_aktualisiert=False,
            leer_text="(keine langfristigen Ziele)",
        ))
        self._outer_box.append(_build_section(
            titel="Mittelfristige Ziele",
            ziele=mid_term,
            zeige_aktualisiert=True,
            leer_text="(keine mittelfristigen Ziele)",
        ))
        self._outer_box.append(_build_short_term_section(short_term))

    # ═══════════════════════════════════════════════════════════════
    # Turn-Reactive: nach jedem Turn neu laden
    # ═══════════════════════════════════════════════════════════════
    def on_turn_received(self, turn_data: dict) -> None:
        """Wird nach jedem SSE-Answer aufgerufen — Panel-Daten neu laden."""
        logger.debug("GoalsPanel: Turn empfangen — Refresh")
        self.refresh()


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen — Layout
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    """Entfernt alle Kind-Widgets aus einem Box-Container."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_config_row(config: dict) -> Gtk.Label:
    """Kompakte einzeilige Anzeige der aktuellen Drive-Konfiguration."""
    threshold:       float = float(config.get("gravity_threshold", 0.0))
    salience_factor: float = float(config.get("salience_factor", 0.0))
    decay_days:      int   = int(config.get("decay_days", 0))
    max_long:        int   = int(config.get("max_long_term", 0))
    max_mid:         int   = int(config.get("max_mid_term", 0))

    text: str = (
        f"Schwelle: {threshold:.2f}  ·  "
        f"Salienz-Faktor: {salience_factor:.2f}  ·  "
        f"Decay: {decay_days}d  ·  "
        f"Max: {max_long} lang / {max_mid} mittel"
    )
    label = Gtk.Label(label=text)
    label.set_xalign(0.0)
    label.set_wrap(True)
    label.add_css_class("dim-label")
    label.add_css_class("caption")
    return label


def _build_section(
    titel: str,
    ziele: list,
    zeige_aktualisiert: bool,
    leer_text: str,
) -> Gtk.Box:
    """Sektion mit Ueberschrift und einer Karte pro Ziel."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    header = Gtk.Label(label=titel)
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    # Nur lebende Ziele als Karten. Der Endpoint liefert aktiv und inaktiv;
    # die inaktiven (verfallen oder bei einer Destillation abgeloest) standen
    # bis zum 28.08.2026 durchgestrichen darunter — bei 333 langfristigen ein
    # Tab voller Streichungen. Ihre Zahl bleibt sichtbar, ihre Karten nicht.
    aktive:   list = [z for z in ziele if bool(z.get("active", True))]
    inaktive: int  = len(ziele) - len(aktive)

    if not aktive:
        leer = Gtk.Label(label=leer_text)
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
    for idx, ziel in enumerate(aktive):
        if idx > 0:
            section.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        section.append(_build_goal_card(ziel, zeige_aktualisiert=zeige_aktualisiert))

    if inaktive:
        hinweis = Gtk.Label(
            label=f"{inaktive} inaktive Ziele ausgeblendet (verfallen oder abgelöst)",
        )
        hinweis.set_xalign(0.0)
        hinweis.add_css_class("dim-label")
        hinweis.add_css_class("caption")
        section.append(hinweis)

    return section


def _build_goal_card(ziel: dict, zeige_aktualisiert: bool) -> Gtk.Box:
    """Eine Karte fuer ein Ziel — Zielsatz, Motivation, Emotion, Status."""
    active: bool = bool(ziel.get("active", True))

    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    card.set_margin_top(4)
    card.set_margin_bottom(4)

    # Kopfzeile: Status-Punkt + Emotion-Badge + Erstellt-Zeitstempel rechts.
    head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    status_label = Gtk.Label(label="●")
    status_label.set_tooltip_text("aktiv" if active else "inaktiv")
    if active:
        status_label.add_css_class("success")
    else:
        status_label.add_css_class("dim-label")
    head.append(status_label)

    emotion: str = str(ziel.get("emotion") or "")
    if emotion:
        badge = Gtk.Label(label=emotion)
        badge.add_css_class("caption")
        badge.add_css_class("accent")
        head.append(badge)

    spacer = Gtk.Box()
    spacer.set_hexpand(True)
    head.append(spacer)

    created: str = zeit_kurz(str(ziel.get("created_at") or ""))
    if created:
        ts_label = Gtk.Label(label=f"erstellt: {created}")
        ts_label.add_css_class("dim-label")
        ts_label.add_css_class("caption")
        ts_label.set_xalign(1.0)
        head.append(ts_label)

    card.append(head)

    # Zielsatz — mehrzeilig, ggf. durchgestrichen wenn inaktiv.
    goal_text: str = str(ziel.get("goal_text") or "")
    text_label = Gtk.Label(label=goal_text)
    text_label.set_xalign(0.0)
    text_label.set_wrap(True)
    text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    text_label.set_selectable(True)
    if not active:
        # Gedaempft + durchgestrichen darstellen.
        text_label.add_css_class("dim-label")
        attrs = Pango.AttrList()
        attrs.insert(Pango.attr_strikethrough_new(True))
        text_label.set_attributes(attrs)
    card.append(text_label)

    # Motivation — LevelBar + Zahlwert.
    motivation: float = float(ziel.get("motivation", 0.0))
    motivation_clamped: float = max(0.0, min(1.0, motivation))

    mot_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    mot_label = Gtk.Label(label="Motivation")
    mot_label.set_xalign(0.0)
    mot_label.set_width_chars(11)
    mot_label.add_css_class("caption")
    mot_row.append(mot_label)

    bar = Gtk.LevelBar()
    bar.set_min_value(0.0)
    bar.set_max_value(1.0)
    bar.set_value(motivation_clamped)
    bar.set_hexpand(True)
    bar.set_valign(Gtk.Align.CENTER)
    mot_row.append(bar)

    wert_label = Gtk.Label(label=f"{motivation:.2f}")
    wert_label.set_xalign(1.0)
    wert_label.set_width_chars(5)
    wert_label.add_css_class("caption")
    mot_row.append(wert_label)

    # Seit 29.08.2026 rechnet der Endpoint die Motivation live (wie die
    # Gravitation); der Wert des Tageslaufs steht daneben, wenn er abweicht.
    materialisiert = ziel.get("motivation_materialisiert")
    if materialisiert is not None and abs(float(materialisiert) - motivation) >= 0.005:
        tages_label = Gtk.Label(label=f"(Tageslauf {float(materialisiert):.2f})")
        tages_label.add_css_class("dim-label")
        tages_label.add_css_class("caption")
        tages_label.set_tooltip_text(
            "Wert, den der Tageslauf zuletzt schrieb — die Anzeige rechnet aus Anker und Alter"
        )
        mot_row.append(tages_label)

    card.append(mot_row)

    # Aktualisiert-am (nur fuer mittelfristige Ziele relevant).
    if zeige_aktualisiert:
        updated: str = zeit_kurz(str(ziel.get("updated_at") or ""))
        if updated:
            akt_label = Gtk.Label(label=f"aktualisiert: {updated}")
            akt_label.set_xalign(0.0)
            akt_label.add_css_class("dim-label")
            akt_label.add_css_class("caption")
            card.append(akt_label)

    return card


def _build_short_term_section(short_term: dict | None) -> Gtk.Box:
    """Sektion fuer Gespraechsvektor + aktivierte Ziele + Gravitationsterm."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    header = Gtk.Label(label="Kurzfristig — Gravitation")
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    if not short_term:
        leer = Gtk.Label(label="Noch kein Turn in dieser Session")
        leer.set_xalign(0.0)
        leer.add_css_class("dim-label")
        section.append(leer)
        return section

    # GV-Hypothese ist jetzt im GV-Panel (Chat 73).

    activated_goals: list = short_term.get("activated_goals") or []
    if activated_goals:
        akt_header = Gtk.Label(label="Aktivierte Ziele")
        akt_header.set_xalign(0.0)
        akt_header.add_css_class("caption")
        akt_header.add_css_class("dim-label")
        akt_header.set_margin_top(4)
        section.append(akt_header)

        for entry in activated_goals:
            section.append(_build_activated_goal_row(entry))

    gravity_term = short_term.get("gravity_term")
    if gravity_term is not None:
        try:
            gt: float = float(gravity_term)
        except (TypeError, ValueError):
            gt = 0.0
        gt_label = Gtk.Label(label=f"Gesamtgravitation: {gt:.3f}")
        gt_label.set_xalign(0.0)
        gt_label.add_css_class("heading")
        gt_label.set_margin_top(4)
        section.append(gt_label)

    return section


def _build_activated_goal_row(entry: dict) -> Gtk.Label:
    """Eine kompakte Zeile pro aktiviertem Ziel."""
    goal_text:  str   = str(entry.get("goal_text") or "")
    similarity: float = float(entry.get("similarity", 0.0))
    gravity:    float = float(entry.get("gravity_strength", 0.0))

    auszug: str = goal_text if len(goal_text) <= 60 else goal_text[:57] + "..."
    text:   str = f"🎯 {auszug} — Sim: {similarity:.2f} | Grav: {gravity:.3f}"

    label = Gtk.Label(label=text)
    label.set_xalign(0.0)
    label.set_wrap(True)
    label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    return label

