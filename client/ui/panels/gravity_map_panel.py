"""
Gravitationsgraph-Panel — visualisiert Novas Antrieb auf einer 2D-Ebene.

Liest ``GET /drive/gravity_map`` und zeichnet via Cairo:

* den Gespraechspfad (User-Turns als gepunktet verbundene Punkte —
  kurzfristig),
* Gravitations-Connections vom Turn zum Rand des Graphen, mit Linien-
  Stil nach Zeithorizont (durchgezogen = langfristig, gestrichelt =
  mittelfristig),
* nummerierte Marker (①, ②, ...) am Rand fuer die Ziele, die in einer
  Leiste am unteren Rand mit Volltext referenziert werden,
* eine horizontale Legende mit Plutchik-Farben + Linien-Stilen.

Linien-Sprache fuer die drei Zeithorizonte:
  durchgezogen = langfristig | gestrichelt = mittelfristig | gepunktet = kurzfristig

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte und Logs deutsch.
"""

import logging
import math

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


# ─── Plutchik-Sektor-Farben (RGBA, 0.0–1.0) ─────────────────────────────
_RGBA = tuple[float, float, float, float]


def _hex_to_rgba(hex_str: str, alpha: float = 1.0) -> _RGBA:
    """Wandelt '#RRGGBB' in ein RGBA-Tupel (0.0–1.0)."""
    h: str = hex_str.lstrip("#")
    r: int = int(h[0:2], 16)
    g: int = int(h[2:4], 16)
    b: int = int(h[4:6], 16)
    return (r / 255.0, g / 255.0, b / 255.0, alpha)


_SEKTOR_FARBEN: list[tuple[str, str]] = [
    ("Freude",        "#FFD700"),
    ("Zuversicht",    "#2E8B57"),
    ("Angst",         "#556B2F"),
    ("Überraschung",  "#00CED1"),
    ("Trauer",        "#4169E1"),
    ("Enttäuschung",  "#9932CC"),
    ("Ärger",         "#DC143C"),
    ("Neugier",       "#FF8C00"),
]

_NEUTRAL_HEX: str = "#888888"


_EMOTION_HEX: dict[str, str] = {
    "begeisterung":   "#FFD700", "freude":        "#FFD700",
    "dankbarkeit":    "#2E8B57", "zufriedenheit": "#2E8B57",
    "vertrauen":      "#2E8B57",
    "stress":         "#556B2F", "unsicherheit":  "#556B2F",
    "angst":          "#556B2F",
    "ueberrascht":    "#00CED1", "verwundert":    "#00CED1",
    "ueberraschung":  "#00CED1",
    "verzweiflung":   "#4169E1", "traurigkeit":   "#4169E1",
    "trauer":         "#4169E1",
    "frustration":    "#9932CC", "enttaeuschung": "#9932CC",
    "ekel":           "#9932CC",
    "wut":            "#DC143C", "aerger":        "#DC143C",
    "hoffnung":       "#FF8C00", "neugierig":     "#FF8C00",
    "erwartung":      "#FF8C00",
    "neutral":        _NEUTRAL_HEX,
}


def _emotion_color(emotion: str, alpha: float = 1.0) -> _RGBA:
    """Liefert die RGBA-Farbe fuer eine Emotion (Fallback: Neutral-Grau)."""
    hex_str: str = _EMOTION_HEX.get((emotion or "").lower(), _NEUTRAL_HEX)
    return _hex_to_rgba(hex_str, alpha)


def _draw_rounded_rect(
    cr, x: float, y: float, w: float, h: float, radius: float = 6.0,
) -> None:
    """Legt einen Pfad fuer ein Rechteck mit abgerundeten Ecken an.

    Der Aufrufer entscheidet, ob er ``cr.fill()`` oder ``cr.stroke()``
    aufruft. Der Pfad wird mit ``cr.new_sub_path()`` begonnen, damit der
    erste ``arc()`` eindeutig die linke obere Ecke startet.
    """
    r: float = max(0.0, min(radius, w / 2.0, h / 2.0))
    cr.new_sub_path()
    # links-oben → rechts-oben → rechts-unten → links-unten
    cr.arc(x + w - r, y + r,         r, -math.pi / 2.0, 0.0)
    cr.arc(x + w - r, y + h - r,     r, 0.0,            math.pi / 2.0)
    cr.arc(x + r,     y + h - r,     r, math.pi / 2.0,  math.pi)
    cr.arc(x + r,     y + r,         r, math.pi,        3.0 * math.pi / 2.0)
    cr.close_path()


# ─── Layout-Konstanten ─────────────────────────────────────────────────
_MARGIN_X:           float = 60.0    # Linker/Rechter Rand fuer Labels
_MARGIN_TOP:         float = 50.0    # Themen-Header oben
_TURN_RADIUS:        float = 18.0    # Doppelt so gross wie zuvor (markant)
_GOAL_INDICATOR_RADIUS: float = 26.0 # Nummerierter Goal-Kreis im Graph-Raum (verdoppelt)
_BAR_ROW_HEIGHT:     float = 20.0
_BAR_PADDING:        float = 8.0
_GRAPH_BOTTOM_GAP:   float = 10.0    # Abstand Graph → Goal-Bar
_LEGEND_HEIGHT:      float = 24.0
_LEGEND_GAP:         float = 6.0     # Abstand Bar → Legende
_EVENT_HORIZON_ALPHA: float = 0.10   # halbtransparente Fuellung
_EVENT_HORIZON_BORDER_ALPHA: float = 0.20

# Linien-Sprache fuer die drei Zeithorizonte (Cairo-Dash-Pattern)
_DASH_LONG:  list[float] = []                # durchgezogen
_DASH_MID:   list[float] = [4.0, 3.0]        # gestrichelt
_DASH_SHORT: list[float] = [1.0, 3.0]        # gepunktet


class GravityMapPanel(PanelBase):
    """Cairo-basiertes Panel fuer Novas Gravitationsgraphen."""

    PANEL_ID            = "gravity_map"
    PANEL_LABEL         = "🌌 Gravitationsgraph"
    PANEL_TITLE         = "Gravitationsgraph"
    UNIQUE              = True
    CATEGORY            = "turn_reactive"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH       = 900
    DEFAULT_HEIGHT      = 650

    def _build_content(self) -> None:
        """Eine einzige DrawingArea, die den gesamten Inhalt rendert."""
        self._map_data: dict | None = None

        self._canvas = Gtk.DrawingArea()
        self._canvas.set_hexpand(True)
        self._canvas.set_vexpand(True)
        self._canvas.set_draw_func(self._on_draw)

        self.content_area.append(self._canvas)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt Turns + Ziele + Connections vom Server."""
        url: str = f"{SERVER_URL}/drive/gravity_map"
        logger.debug(f"GravityMapPanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _update_ui(self, data: dict) -> None:
        """Speichert die Antwort und triggert einen Cairo-Redraw."""
        self._map_data = data or {}

        turns:       list = self._map_data.get("turns")       or []
        goals:       list = self._map_data.get("goals")       or []
        connections: list = self._map_data.get("connections") or []

        logger.info(
            f"GravityMapPanel: {len(turns)} Turns, {len(goals)} Ziele, "
            f"{len(connections)} Connections"
        )

        self._canvas.queue_draw()

    # ═══════════════════════════════════════════════════════════════
    # Turn-reactive
    # ═══════════════════════════════════════════════════════════════
    def on_turn_received(self, turn_data: dict) -> None:
        """Nach jedem Turn neu laden — der Graph entwickelt sich live mit."""
        logger.debug("GravityMapPanel: Turn empfangen — Refresh")
        self.refresh()

    # ═══════════════════════════════════════════════════════════════
    # Cairo-Rendering
    # ═══════════════════════════════════════════════════════════════
    def _on_draw(
        self, area: Gtk.DrawingArea, cr, width: int, height: int
    ) -> None:
        """Top-Level draw-Callback — Layer von hinten nach vorne.

        Reihenfolge:
          1. Hintergrund
          2. Ereignishorizont-Discs (halbtransparente Felder um Ziele)
          3. Gravitationslinien (zu den Zielen)
          4. Gespraechspfad (zwischen Turns)
          5. Turn-Kreise (mit zentriertem Label)
          6. Ziel-Indikator-Kreise (nummeriert, an Ziel-Position)
          7. Tags / Topic-Labels (unter Turns)
          8. Goal-Bar + Legende + Themen-Header
        """
        # 1. Hintergrund
        self._draw_background(cr, width, height)

        if not self._map_data:
            self._draw_placeholder(cr, width, height, "Lade Daten …")
            self._draw_legend(cr, width, height)
            return

        turns:       list = self._map_data.get("turns")       or []
        goals:       list = self._map_data.get("goals")       or []
        connections: list = self._map_data.get("connections") or []

        sorted_goals: list[tuple[int, dict]] = self._sort_goals(goals)
        server_to_sorted: dict[int, int] = {
            srv: srt for srt, (srv, _) in enumerate(sorted_goals)
        }

        layout: dict = self._compute_layout(height, len(sorted_goals))

        if not turns and not goals:
            self._draw_placeholder(cr, width, height, "Noch keine Daten")
            self._draw_legend(cr, width, height)
            return

        graph_top:    float = layout["graph_top"]
        graph_bottom: float = layout["graph_bottom"]
        bar_top:      float = layout["bar_top"]

        # 2. Ereignishorizont-Discs — ganz unten, als Hintergrund-Felder.
        self._draw_event_horizons(
            cr, width, sorted_goals, graph_top, graph_bottom,
        )
        # 2b. Themen-Region-Labels — gross, halbtransparent, als
        # Wasserzeichen-Orientierung zwischen Horizonten und Linien.
        self._draw_theme_regions(
            cr, width, sorted_goals, graph_top, graph_bottom,
        )
        # 3. Gravitationslinien deaktiviert — Gravitation wird ueber
        # raeumliche Naehe + Ereignishorizonte ausgedrueckt. Methode
        # ``_draw_gravity_lines`` bleibt fuer eine spaetere Reaktivierung.
        # 4. Gespraechspfad zwischen Turns.
        self._draw_conversation_path(
            cr, width, turns, graph_top, graph_bottom,
        )
        # 5. Turn-Kreise mit zentriertem Label.
        self._draw_turns(cr, width, turns, graph_top, graph_bottom)
        # 6. Ziel-Indikatoren (nummerierte Kreise an Ziel-Position).
        self._draw_goal_indicators(
            cr, width, sorted_goals, graph_top, graph_bottom,
        )
        # 7. Topic-Tags (unter den Turn-Kreisen).
        self._draw_topic_tags(cr, width, turns, graph_top, graph_bottom)
        # 8. Goal-Bar, Legende, Themen-Header.
        self._draw_goal_bar(cr, width, sorted_goals, bar_top)
        self._draw_legend(cr, width, height)
        self._draw_dominant_topics(cr, width, self._map_data.get("dominant_topics") or [])

    # ─── Layout ──────────────────────────────────────────────────────
    def _compute_layout(self, height: int, n_goals: int) -> dict:
        """Berechnet die vertikalen Zonen: Graph / Bar / Legende."""
        bar_height: float = (
            n_goals * _BAR_ROW_HEIGHT + 2 * _BAR_PADDING if n_goals else 0.0
        )

        legend_top:   float = height - _LEGEND_HEIGHT
        bar_bottom:   float = legend_top - _LEGEND_GAP
        bar_top:      float = bar_bottom - bar_height
        graph_bottom: float = bar_top - _GRAPH_BOTTOM_GAP
        graph_top:    float = _MARGIN_TOP

        # Defensive: kleines Fenster nicht in negative Hoehe kollabieren.
        if graph_bottom < graph_top + 40.0:
            graph_bottom = graph_top + 40.0

        return {
            "graph_top":    graph_top,
            "graph_bottom": graph_bottom,
            "bar_top":      bar_top,
            "bar_bottom":   bar_bottom,
            "legend_top":   legend_top,
        }

    # ─── Hintergrund + Hilfen ────────────────────────────────────────
    def _draw_background(self, cr, width: int, height: int) -> None:
        """Dunkler Hintergrund passend zum bestehenden Dark-Theme."""
        cr.set_source_rgba(*_hex_to_rgba("#1a1a2e", 1.0))
        cr.rectangle(0, 0, width, height)
        cr.fill()

    def _to_pixels(
        self, x: float, y: float,
        width: int, graph_top: float, graph_bottom: float,
    ) -> tuple[float, float]:
        """Mappt Server-Koordinaten 0..1 auf die Graph-Zone."""
        px: float = _MARGIN_X + x * (width - 2 * _MARGIN_X)
        py: float = graph_top + y * (graph_bottom - graph_top)
        return px, py

    def _draw_placeholder(
        self, cr, width: int, height: int, text: str
    ) -> None:
        """Mittiger Hinweis, wenn noch keine Daten da sind."""
        cr.set_source_rgba(0.7, 0.7, 0.75, 1.0)
        cr.select_font_face("Sans")
        cr.set_font_size(14)
        extents = cr.text_extents(text)
        tx: float = (width - extents.width) / 2.0 - extents.x_bearing
        ty: float = height / 2.0
        cr.move_to(tx, ty)
        cr.show_text(text)

    # ─── Ziele sortieren / Marker-Position ───────────────────────────
    @staticmethod
    def _sort_goals(goals: list[dict]) -> list[tuple[int, dict]]:
        """Sortiert Ziele: langfristig zuerst, dann mittelfristig.

        Sekundaer absteigend nach Motivation, damit das wichtigste Ziel
        oben in seiner Gruppe steht. Gibt (server_idx, goal)-Paare zurueck.
        """
        def sort_key(pair: tuple[int, dict]) -> tuple[int, float]:
            _, goal = pair
            type_rank: int = 0 if (goal.get("goal_type") or "") == "long_term" else 1
            try:
                motivation: float = float(goal.get("motivation", 0.0) or 0.0)
            except (TypeError, ValueError):
                motivation = 0.0
            return (type_rank, -motivation)

        return sorted(enumerate(goals), key=sort_key)

    def _normalized_to_pixel_radius(
        self, normalized_radius: float,
        width: int, graph_top: float, graph_bottom: float,
    ) -> float:
        """Mappt einen normalisierten 0..1-Radius auf Pixel.

        Da x- und y-Skalen unterschiedlich sind, wird der Mittelwert beider
        Skalen verwendet — das Ergebnis ist ein Kompromiss-Kreis, kein
        Ellipsenabschnitt.
        """
        scale_x: float = max(0.0, width - 2 * _MARGIN_X)
        scale_y: float = max(0.0, graph_bottom - graph_top)
        return normalized_radius * (scale_x + scale_y) / 2.0

    # ─── Ereignishorizont-Discs (Layer 2) ────────────────────────────
    def _draw_event_horizons(
        self, cr, width: int,
        sorted_goals: list[tuple[int, dict]],
        graph_top: float, graph_bottom: float,
    ) -> None:
        """Halbtransparente Felder um die Ziel-Positionen.

        Radius kommt vom Server (``event_horizon_radius`` in 0..1) — er
        spannt vom Ziel bis zum entferntesten verbundenen Turn. Alle
        Turn-Punkte innerhalb dieses Felds haben Connection zu diesem Ziel.
        """
        for _orig_idx, goal in sorted_goals:
            try:
                norm_r: float = float(goal.get("event_horizon_radius", 0.0) or 0.0)
            except (TypeError, ValueError):
                norm_r = 0.0
            if norm_r <= 0.0:
                continue

            gx, gy = self._to_pixels(
                float(goal.get("x", 0.5)), float(goal.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )
            r_px: float = self._normalized_to_pixel_radius(
                norm_r, width, graph_top, graph_bottom,
            )
            if r_px <= 0.0:
                continue

            r, g, b, _ = _emotion_color(goal.get("emotion", "neutral"), 1.0)

            # Halbtransparente Fuellung. ``new_sub_path`` schneidet den
            # current point ab, damit kein impliziter line_to vor dem Arc
            # entsteht (sonst Phantom-Linien beim stroke unten).
            cr.set_source_rgba(r, g, b, _EVENT_HORIZON_ALPHA)
            cr.new_sub_path()
            cr.arc(gx, gy, r_px, 0.0, 2.0 * math.pi)
            cr.fill()

            # Sehr duenner Rand, damit das Feld eine Kontur hat.
            cr.set_source_rgba(r, g, b, _EVENT_HORIZON_BORDER_ALPHA)
            cr.set_line_width(1.0)
            cr.new_sub_path()
            cr.arc(gx, gy, r_px, 0.0, 2.0 * math.pi)
            cr.stroke()

    # ─── Themen-Region-Labels (Wasserzeichen) ────────────────────────
    def _draw_theme_regions(
        self, cr, width: int,
        sorted_goals: list[tuple[int, dict]],
        graph_top: float, graph_bottom: float,
    ) -> None:
        """Gross, halbtransparent — gibt dem Graph-Raum Bedeutung.

        Die Labels liegen leicht oberhalb-links des Ziel-Indikators,
        damit sich Text und Indikator-Kreis nicht ueberdecken.
        """
        cr.select_font_face("Sans")
        cr.set_font_size(17)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.28)

        for _orig_idx, goal in sorted_goals:
            label: str = (goal.get("theme_label") or "").strip()
            if not label:
                continue

            gx, gy = self._to_pixels(
                float(goal.get("x", 0.5)), float(goal.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )

            extents = cr.text_extents(label)
            # Versatz nach links-oben — der Indikator-Kreis hat Radius
            # _GOAL_INDICATOR_RADIUS, also ein bisschen mehr Abstand
            # damit das Label nicht am Kreisrand klebt.
            offset: float = _GOAL_INDICATOR_RADIUS + 6.0
            tx: float = gx - offset - extents.width - extents.x_bearing
            ty: float = gy - offset

            # Falls das Label links aus dem Graph-Rand fallen wuerde,
            # spiegele die Versatzrichtung nach rechts.
            if tx < _MARGIN_X / 2.0:
                tx = gx + offset - extents.x_bearing
            # Falls das Label oben aus dem Graph-Rand fallen wuerde,
            # spiegele nach unten.
            if ty - extents.height < graph_top + 4.0:
                ty = gy + offset + extents.height

            cr.move_to(tx, ty)
            cr.show_text(label)

    # ─── Gespraechspfad (gepunktet = kurzfristig) ────────────────────
    def _draw_conversation_path(
        self, cr, width: int, turns: list[dict],
        graph_top: float, graph_bottom: float,
    ) -> None:
        """Verbindet die Turns chronologisch — gepunktet, Alpha steigt mit Alter.

        Linien starten/enden exakt im Mittelpunkt der Turn-Kreise.
        """
        total: int = len(turns)
        if total < 2:
            return

        cr.set_line_width(1.0)
        cr.set_dash(_DASH_SHORT, 0.0)

        points: list[tuple[float, float]] = [
            self._to_pixels(
                float(t.get("x", 0.5)), float(t.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )
            for t in turns
        ]

        for i in range(len(points) - 1):
            target_idx: int = i + 1
            alpha: float = max(0.1, (target_idx + 1) / total)
            cr.set_source_rgba(1.0, 1.0, 1.0, alpha)
            cr.move_to(*points[i])
            cr.line_to(*points[i + 1])
            cr.stroke()

        cr.set_dash([], 0.0)

    # ─── Turn-Kreise mit zentrierten Labels ──────────────────────────
    def _draw_turns(
        self, cr, width: int, turns: list[dict],
        graph_top: float, graph_bottom: float,
    ) -> None:
        """Gefuellte Kreise pro User-Turn, abgedunkelt nach Alter.

        Labels sind RELATIV (neuester = 0, davor -1, …) und stehen
        ZENTRIERT im Kreis.
        """
        total: int = len(turns)
        for idx, turn in enumerate(turns):
            x, y = self._to_pixels(
                float(turn.get("x", 0.5)), float(turn.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )

            r, g, b, _a = _emotion_color(turn.get("emotion", "neutral"), 1.0)
            brightness: float = 0.2 + 0.8 * (idx / max(total - 1, 1))
            # Alpha ist explizit 1.0 — die Fuellung muss die darunter
            # liegenden Linien vollstaendig ueberdecken.
            faded: _RGBA = (r * brightness, g * brightness, b * brightness, 1.0)

            cr.set_dash([], 0.0)

            # Schritt 1: Maskierungs-Kreis in Hintergrundfarbe (etwas
            # groesser als der Turn) — verdeckt Linien, Pfade und
            # Ereignishorizonte unter dem Turn endgueltig.
            cr.set_source_rgba(*_hex_to_rgba("#1a1a2e", 1.0))
            cr.new_sub_path()
            cr.arc(x, y, _TURN_RADIUS + 2.0, 0.0, 2.0 * math.pi)
            cr.fill()

            # Schritt 2: Farbiger Hauptkreis (opake Fuellung) + Rand.
            cr.set_source_rgba(*faded)
            cr.new_sub_path()
            cr.arc(x, y, _TURN_RADIUS, 0.0, 2.0 * math.pi)
            cr.fill_preserve()
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.3)
            cr.set_line_width(1.2)
            cr.stroke()

            # Relatives Label, zentriert im Kreis.
            relative_label: int = -(total - 1 - idx)
            label_text: str = str(relative_label)

            cr.set_source_rgba(0.98, 0.98, 1.0, 0.95)
            cr.select_font_face("Sans")
            cr.set_font_size(11)
            extents = cr.text_extents(label_text)
            tx: float = x - extents.width / 2.0 - extents.x_bearing
            ty: float = y - extents.y_bearing - extents.height / 2.0
            cr.move_to(tx, ty)
            cr.show_text(label_text)

    # ─── Topic-Tags als Pill-Badges (separater Layer) ────────────────
    def _draw_topic_tags(
        self, cr, width: int, turns: list[dict],
        graph_top: float, graph_bottom: float,
    ) -> None:
        """Erstes Topic je Turn als Pill-Badge rechts neben dem Punkt.

        Halbtransparenter dunkler Pill-Hintergrund, Text in Turn-Farbe
        (mit Brightness-Fading, damit alte Tags optisch zurueckweichen).
        Keine Kollisionsvermeidung — bei Ueberlappung gewinnt der spaeter
        gezeichnete (juengere) Tag visuell.
        """
        total: int = len(turns)
        for idx, turn in enumerate(turns):
            topics_raw = turn.get("topics") or []
            if not isinstance(topics_raw, list) or not topics_raw:
                continue
            label: str = str(topics_raw[0]).strip()
            if not label:
                continue

            x, y = self._to_pixels(
                float(turn.get("x", 0.5)), float(turn.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )

            cr.select_font_face("Sans")
            cr.set_font_size(9)
            extents = cr.text_extents(label)

            pad_x: float = 5.0
            pad_y: float = 3.0
            badge_w: float = extents.width + 2 * pad_x
            badge_h: float = extents.height + 2 * pad_y

            badge_x: float = x + _TURN_RADIUS + 4.0
            badge_y: float = y - badge_h / 2.0

            # Pill-Hintergrund (halbtransparent dunkel).
            _draw_rounded_rect(cr, badge_x, badge_y, badge_w, badge_h, radius=6.0)
            cr.set_source_rgba(0.1, 0.1, 0.18, 0.75)
            cr.fill()

            # Text in Turn-Farbe mit Brightness-Fading.
            r, g, b, _a = _emotion_color(turn.get("emotion", "neutral"), 1.0)
            brightness: float = 0.2 + 0.8 * (idx / max(total - 1, 1))
            cr.set_source_rgba(
                r * brightness, g * brightness, b * brightness, 1.0,
            )
            cr.move_to(
                badge_x + pad_x - extents.x_bearing,
                badge_y + pad_y + extents.height,
            )
            cr.show_text(label)

    # ─── Ziel-Indikatoren (Layer 6 — an Ziel-Position) ───────────────
    def _draw_goal_indicators(
        self, cr, width: int,
        sorted_goals: list[tuple[int, dict]],
        graph_top: float, graph_bottom: float,
    ) -> None:
        """Nummerierter Kreis am Ziel-Mittelpunkt, im Graph-Raum.

        Ueberdeckt die Turn-Kreise an seiner Position (kommt in der
        Render-Pipeline danach). Der Linien-Stil des Umrisses signalisiert
        den Zeithorizont (durchgezogen langfristig, gestrichelt mittel).
        """
        for sidx, (_orig_idx, goal) in enumerate(sorted_goals):
            gx, gy = self._to_pixels(
                float(goal.get("x", 0.5)), float(goal.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )

            # Dunkle Fuellung, damit die Nummer auf jedem Hintergrund lesbar ist.
            cr.set_dash([], 0.0)
            cr.set_source_rgba(0.10, 0.10, 0.15, 0.95)
            # new_sub_path verhindert, dass cr.arc einen impliziten line_to
            # vom letzten current point (Ende des show_text der Vor-Iteration)
            # zum Arc-Start zieht — sonst entstehen Phantom-Linien zwischen
            # den Goal-Indikatoren, die beim stroke() in Emotion-Farbe und
            # Dash-Stil sichtbar werden.
            cr.new_sub_path()
            cr.arc(gx, gy, _GOAL_INDICATOR_RADIUS, 0.0, 2.0 * math.pi)
            cr.fill_preserve()

            # Umriss in Emotion-Farbe + Linien-Stil nach Zeithorizont.
            color: _RGBA = _emotion_color(goal.get("emotion", "neutral"), 1.0)
            cr.set_source_rgba(*color)
            cr.set_line_width(1.8)
            goal_type: str = str(goal.get("goal_type") or "mid_term")
            cr.set_dash(_DASH_LONG if goal_type == "long_term" else _DASH_MID, 0.0)
            cr.stroke()
            cr.set_dash([], 0.0)

            # Ziffer manuell zentriert reinschreiben — ohne Unicode-
            # Sonderzeichen (Cairo's Toy-Font kann ① nicht rendern).
            label: str = str(sidx + 1)
            cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            cr.select_font_face("Sans")
            cr.set_font_size(11)
            extents = cr.text_extents(label)
            tx: float = gx - extents.width / 2.0 - extents.x_bearing
            ty: float = gy - extents.y_bearing - extents.height / 2.0
            cr.move_to(tx, ty)
            cr.show_text(label)

    # ─── Ziel-Leiste am unteren Rand ─────────────────────────────────
    def _draw_goal_bar(
        self, cr, width: int,
        sorted_goals: list[tuple[int, dict]],
        bar_top: float,
    ) -> None:
        """Eine Zeile pro Ziel — ``① Text  Stil 0.90`` (Motivation rechts)."""
        if not sorted_goals:
            return

        bar_left:   float = _MARGIN_X / 2.0
        bar_right:  float = width - _MARGIN_X / 2.0
        bar_height: float = (
            len(sorted_goals) * _BAR_ROW_HEIGHT + 2 * _BAR_PADDING
        )

        # Hintergrund-Box.
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.30)
        cr.rectangle(bar_left, bar_top, bar_right - bar_left, bar_height)
        cr.fill()

        cr.select_font_face("Sans")
        cr.set_font_size(11)

        for sidx, (_orig_idx, goal) in enumerate(sorted_goals):
            row_top: float = bar_top + _BAR_PADDING + sidx * _BAR_ROW_HEIGHT
            baseline: float = row_top + _BAR_ROW_HEIGHT - 6.0

            # Nummer in Emotion-Farbe — als einfache Ziffer mit Punkt
            # (Unicode-Circled-Digits ①… werden von Cairo's Toy-Font
            # nicht gerendert).
            color: _RGBA = _emotion_color(goal.get("emotion", "neutral"), 1.0)
            num: str = f"{sidx + 1}."
            cr.set_source_rgba(*color)
            cr.set_font_size(11)
            cr.move_to(bar_left + 10.0, baseline)
            cr.show_text(num)
            num_ext = cr.text_extents(num)
            x_cursor: float = bar_left + 10.0 + num_ext.width + 10.0

            # Goal-Text (~50 Zeichen).
            text: str = self._truncate(str(goal.get("goal_text") or ""), 50)
            cr.set_source_rgba(0.95, 0.95, 0.98, 0.95)
            cr.set_font_size(11)
            cr.move_to(x_cursor, baseline)
            cr.show_text(text)

            # Rechts: Linien-Stil-Vorschau + Typ-Glyph + Motivation.
            try:
                motivation: float = float(goal.get("motivation", 0.0) or 0.0)
            except (TypeError, ValueError):
                motivation = 0.0
            mot_text: str = f"{motivation:.2f}"

            goal_type: str = str(goal.get("goal_type") or "mid_term")
            type_glyph: str = "●" if goal_type == "long_term" else "◌"

            mot_ext = cr.text_extents(mot_text)
            glyph_ext = cr.text_extents(type_glyph)

            # Layout am rechten Rand: [stil-linie] [glyph] [motivation]
            right_pad: float = 10.0
            mot_x: float = bar_right - right_pad - mot_ext.width
            glyph_x: float = mot_x - glyph_ext.width - 8.0
            preview_x_end: float = glyph_x - 8.0
            preview_x_start: float = preview_x_end - 28.0

            # Linien-Stil-Preview als kurze Linie.
            cr.set_source_rgba(*color)
            cr.set_line_width(1.8)
            cr.set_dash(_DASH_LONG if goal_type == "long_term" else _DASH_MID, 0.0)
            cr.move_to(preview_x_start, baseline - 4.0)
            cr.line_to(preview_x_end,   baseline - 4.0)
            cr.stroke()
            cr.set_dash([], 0.0)

            # Typ-Glyph in Emotion-Farbe.
            cr.move_to(glyph_x, baseline)
            cr.show_text(type_glyph)

            # Motivation (heller Text).
            cr.set_source_rgba(0.95, 0.95, 0.98, 0.85)
            cr.move_to(mot_x, baseline)
            cr.show_text(mot_text)

    # ─── Gravitationslinien Turn → Ziel ──────────────────────────────
    def _draw_gravity_lines(
        self,
        cr,
        width: int,
        turns: list[dict],
        sorted_goals: list[tuple[int, dict]],
        server_to_sorted: dict[int, int],
        connections: list[dict],
        graph_top: float,
        graph_bottom: float,
        all_goals: list[dict],
    ) -> None:
        """Linien Turn-Mittelpunkt → Ziel-Mittelpunkt.

        Stil nach Zeithorizont des Ziels (long_term solid, mid_term dashed).
        Es werden NUR die vom Server gelieferten Connections gezeichnet —
        also nur Paare mit ``similarity >= GRAVITATIONS_SCHWELLE``. Wer
        zu viele Linien sieht, sollte am Server-Threshold drehen.
        """
        if not connections or not turns or not sorted_goals:
            return

        total: int = len(turns)

        for conn in connections:
            try:
                t_idx: int = int(conn.get("turn_index", -1))
                g_idx: int = int(conn.get("goal_index", -1))
            except (TypeError, ValueError):
                continue

            if not (0 <= t_idx < len(turns)):
                continue
            if g_idx not in server_to_sorted:
                continue

            turn: dict = turns[t_idx]
            tx, ty = self._to_pixels(
                float(turn.get("x", 0.5)), float(turn.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )

            goal: dict = (
                all_goals[g_idx] if 0 <= g_idx < len(all_goals)
                else sorted_goals[server_to_sorted[g_idx]][1]
            )
            gx, gy = self._to_pixels(
                float(goal.get("x", 0.5)), float(goal.get("y", 0.5)),
                width, graph_top, graph_bottom,
            )

            goal_type: str = str(goal.get("goal_type") or "mid_term")
            dashes: list[float] = _DASH_LONG if goal_type == "long_term" else _DASH_MID

            gravity_strength: float = float(conn.get("gravity_strength", 0.0))
            line_width: float = max(0.4, min(1.5, gravity_strength * 3.0))

            # Alpha wie der zugehoerige Turn-Punkt: aelter = transparenter.
            alpha: float = max(0.1, (t_idx + 1) / total)
            color: _RGBA = _emotion_color(goal.get("emotion", "neutral"), alpha)

            cr.set_source_rgba(*color)
            cr.set_line_width(line_width)
            cr.set_dash(dashes, 0.0)
            # Linie startet/endet exakt im Mittelpunkt — kein Offset.
            cr.move_to(tx, ty)
            cr.line_to(gx, gy)
            cr.stroke()
            cr.set_dash([], 0.0)

    # ─── Dominante Themen (Header oben) ──────────────────────────────
    def _draw_dominant_topics(
        self, cr, width: int, topics: list[str]
    ) -> None:
        """Tag-Reihe oben links ueber dem Graphen."""
        if not topics:
            return

        cr.select_font_face("Sans")
        cr.set_font_size(10)

        prefix: str = "Themen:"
        x_cursor: float = 12.0
        y_baseline: float = 22.0

        cr.set_source_rgba(0.8, 0.8, 0.85, 0.75)
        cr.move_to(x_cursor, y_baseline)
        cr.show_text(prefix)
        prefix_extents = cr.text_extents(prefix)
        x_cursor += prefix_extents.width + 8.0

        pad_x: float = 6.0
        pad_y: float = 3.0
        gap:   float = 5.0

        for topic in topics:
            text: str = str(topic).strip()
            if not text:
                continue

            extents = cr.text_extents(text)
            tag_w: float = extents.width + 2 * pad_x
            tag_h: float = 16.0

            if x_cursor + tag_w > width - 12.0:
                x_cursor = 12.0 + prefix_extents.width + 8.0
                y_baseline += tag_h + 4.0

            cr.set_source_rgba(0.0, 0.0, 0.0, 0.35)
            cr.rectangle(
                x_cursor, y_baseline - tag_h + pad_y,
                tag_w, tag_h,
            )
            cr.fill()

            cr.set_source_rgba(0.95, 0.95, 0.98, 0.85)
            cr.move_to(x_cursor + pad_x - extents.x_bearing, y_baseline)
            cr.show_text(text)

            x_cursor += tag_w + gap

    # ─── Legende (horizontaler Strip am Boden) ───────────────────────
    def _draw_legend(self, cr, width: int, height: int) -> None:
        """Horizontale Legende am unteren Rand: Plutchik-Farben + Linien-Stile."""
        bar_y: float = height - _LEGEND_HEIGHT
        bar_h: float = _LEGEND_HEIGHT

        # Hintergrund.
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.55)
        cr.rectangle(0.0, bar_y, width, bar_h)
        cr.fill()

        cr.select_font_face("Sans")
        cr.set_font_size(9)
        baseline: float = bar_y + bar_h - 7.0

        x_cursor: float = 8.0
        sq_size:  float = 10.0
        gap_inner: float = 4.0
        gap_entry: float = 12.0

        # 8 Sektor-Farben + Neutral als Quadrate.
        for name, hex_color in _SEKTOR_FARBEN + [("Neutral", _NEUTRAL_HEX)]:
            cr.set_source_rgba(*_hex_to_rgba(hex_color, 1.0))
            cr.rectangle(x_cursor, baseline - sq_size + 1.0, sq_size, sq_size)
            cr.fill()
            x_cursor += sq_size + gap_inner

            cr.set_source_rgba(0.95, 0.95, 0.98, 0.95)
            cr.move_to(x_cursor, baseline)
            cr.show_text(name)
            ext = cr.text_extents(name)
            x_cursor += ext.width + gap_entry

        # Trenner.
        cr.set_source_rgba(0.5, 0.5, 0.55, 0.6)
        cr.set_line_width(1.0)
        cr.move_to(x_cursor - 4.0, bar_y + 4.0)
        cr.line_to(x_cursor - 4.0, bar_y + bar_h - 4.0)
        cr.stroke()
        x_cursor += 6.0

        # Linien-Stile fuer die drei Zeithorizonte.
        line_entries: list[tuple[list[float], str]] = [
            (_DASH_LONG,  "langfristig"),
            (_DASH_MID,   "mittelfristig"),
            (_DASH_SHORT, "kurzfristig (Verlauf)"),
        ]
        line_y: float = baseline - 4.0
        line_w: float = 26.0

        for dashes, label in line_entries:
            cr.set_source_rgba(0.95, 0.95, 0.98, 0.9)
            cr.set_line_width(1.6)
            cr.set_dash(dashes, 0.0)
            cr.move_to(x_cursor, line_y)
            cr.line_to(x_cursor + line_w, line_y)
            cr.stroke()
            cr.set_dash([], 0.0)
            x_cursor += line_w + gap_inner

            cr.move_to(x_cursor, baseline)
            cr.show_text(label)
            ext = cr.text_extents(label)
            x_cursor += ext.width + gap_entry

    # ─── Hilfen ──────────────────────────────────────────────────────
    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        """Kuerzt einen String auf maximal ``limit`` Zeichen."""
        text = (text or "").strip()
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 1)].rstrip() + "…"
