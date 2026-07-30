"""
Emotionen-Panel — aktueller Emotionszustand eines Users.

Liest ``GET /gedaechtnis/emotionen/{user_id}`` und zeigt aggregierte
Arousal-Werte pro Einzelemotion, getrennt nach Session und KZG.

Response-Format (siehe ``server/api/gedaechtnis.py``):

    {
        "session":        {emotion_name: avg_arousal, ...},
        "kzg":            {emotion_name: avg_arousal, ...},
        "session_turns":  int,
        "kzg_eintraege":  int,
    }

Darstellung: Alle 16 kanonischen Emotionen werden immer angezeigt,
gruppiert nach den 8 Plutchik-Sektoren (je 2 Emotionen). Fehlende
Server-Werte werden als 0.0 dargestellt — nötig für die EI-Kalibrierung.
``neutral`` gehört keinem Sektor an und wird bei Bedarf separat unten
gezeigt.
"""

import logging

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402
from ui.widgets.radar_chart import RadarChart  # noqa: E402


logger = logging.getLogger(__name__)


# Kurzformen der 8 Plutchik-Sektoren für die Radar-Achsen, in derselben
# Reihenfolge wie ``EMOTION_SEKTOREN``. Sie stehen hier und nicht im Widget:
# Das Radar-Diagramm zeichnet Achsen, es kennt keine Emotionen.
_RADAR_ACHSEN: list[str] = ["Fr", "Zv", "An", "Üb", "Tr", "En", "Är", "Ne"]


# Deutsche Anzeigenamen für die Gruppen-Farbklassen im CSS.
_GROUP_CSS_CLASS: dict[str, str] = {
    "positiv": "emotion-positiv",
    "negativ": "emotion-negativ",
    "neutral": "emotion-neutral",
}


class EmotionsPanel(PanelBase):
    """Zeigt Session- und KZG-Emotionen als Balken-Liste."""

    PANEL_ID = "emotionen_aktuell"
    PANEL_LABEL = "Emotionen"
    UNIQUE = True
    CATEGORY = "on_demand"
    NEEDS_USER_SELECTOR = True
    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 500

    # Plutchik-Sektoren mit kanonischen Emotionen
    # Reihenfolge: Sektor 1–8, je 2 Emotionen pro Sektor
    EMOTION_SEKTOREN: list[tuple[str, list[str], str]] = [
        ("Freude",         ["begeisterung", "freude"],         "positiv"),
        ("Zuversicht",     ["dankbarkeit", "zufriedenheit"],   "positiv"),
        ("Angst",          ["stress", "unsicherheit"],         "negativ"),
        ("Überraschung",   ["ueberrascht", "verwundert"],      "neutral"),
        ("Trauer",         ["verzweiflung", "traurigkeit"],    "negativ"),
        ("Enttäuschung",   ["frustration", "enttaeuschung"],   "negativ"),
        ("Ärger",          ["wut", "aerger"],                  "negativ"),
        ("Neugier",        ["hoffnung", "neugierig"],          "positiv"),
    ]

    def _build_content(self) -> None:
        """Scrollbarer Container für Session- und KZG-Sektion."""
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scroll.set_child(self._outer_box)

        # Zwei Radar-Diagramme oben als visuelle Zusammenfassung.
        radar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        radar_box.set_halign(Gtk.Align.CENTER)

        self._session_radar = RadarChart(_RADAR_ACHSEN, title="Session", size=160)
        self._kzg_radar = RadarChart(_RADAR_ACHSEN, title="KZG", size=160)

        radar_box.append(self._session_radar)
        radar_box.append(self._kzg_radar)
        self._outer_box.append(radar_box)

        self._bars_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._outer_box.append(self._bars_box)

        placeholder = Gtk.Label(label="Lade Emotionen …")
        placeholder.set_xalign(0.0)
        placeholder.add_css_class("dim-label")
        self._bars_box.append(placeholder)

        self.content_area.append(scroll)

    # ═══════════════════════════════════════════════════════════════
    # Daten-Ladung
    # ═══════════════════════════════════════════════════════════════
    def load_data(self) -> dict:
        """Holt Emotions-Aggregate für die aktuell gewählte Perspektive.

        Der ``beobachter``-Filter wirkt serverseitig: Session-Turns werden
        auf die passende Rolle (user/assistant) gefiltert, KZG auf das
        ``beobachter``-Feld. So zeigen die Radare Meisters bzw. Novas
        Emotionsverlauf — je nach Dropdown-Wahl.
        """
        params: dict = self._get_api_params()
        url: str = f"{SERVER_URL}/gedaechtnis/emotionen/{params['user_id']}"
        query: dict = {
            "character_id": params["character_id"],
            "beobachter":   params["beobachter"],
        }
        logger.debug(f"EmotionsPanel: GET {url} {query}")
        response = requests.get(url, params=query, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # ═══════════════════════════════════════════════════════════════
    # UI-Update
    # ═══════════════════════════════════════════════════════════════
    def _update_ui(self, data: dict) -> None:
        """Baut zwei Sektionen: Session und KZG, je alle 16 Emotionen nach Sektor."""
        session: dict = data.get("session") or {}
        kzg: dict = data.get("kzg") or {}
        session_turns: int = int(data.get("session_turns", 0))
        kzg_eintraege: int = int(data.get("kzg_eintraege", 0))

        # Anzahl angezeigter Emotionen pro Sektion (16 Sektor-Emotionen + ggf. neutral).
        anzeige_count: int = sum(len(emos) for _, emos, _ in self.EMOTION_SEKTOREN)
        session_anzeige: int = anzeige_count + (1 if "neutral" in session else 0)
        kzg_anzeige: int = anzeige_count + (1 if "neutral" in kzg else 0)

        logger.info(
            f"EmotionsPanel '{self.user_id}': "
            f"Session={len(session)} geliefert / {session_anzeige} angezeigt "
            f"({session_turns} Turns), "
            f"KZG={len(kzg)} geliefert / {kzg_anzeige} angezeigt "
            f"({kzg_eintraege} Einträge)"
        )

        # Radar-Diagramme aktualisieren.
        self._session_radar.set_data(self._sector_values_from_emotions(session))
        self._kzg_radar.set_data(self._sector_values_from_emotions(kzg))

        _clear_box(self._bars_box)

        self._bars_box.append(
            _build_section(
                f"Session ({session_turns} Turns)", session, self.EMOTION_SEKTOREN
            )
        )
        self._bars_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self._bars_box.append(
            _build_section(
                f"KZG ({kzg_eintraege} Einträge)", kzg, self.EMOTION_SEKTOREN
            )
        )

    def _sector_values_from_emotions(self, emotion_data: dict) -> list[float]:
        """Berechnet 8 Sektorwerte aus den Emotionsdaten.

        Pro Sektor: Maximum der beiden zugehörigen Emotionen (nicht Durchschnitt).
        """
        values: list[float] = []
        for _sektor_name, emotionen, _gruppe in self.EMOTION_SEKTOREN:
            sektor_max = max(
                float(emotion_data.get(e, 0.0)) for e in emotionen
            )
            values.append(sektor_max)
        return values


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    """Entfernt alle Kind-Widgets aus einem Box-Container."""
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _build_section(
    title: str,
    emotions: dict[str, float],
    sektoren: list[tuple[str, list[str], str]],
) -> Gtk.Box:
    """Baut eine Sektion: Überschrift + alle 16 Emotionen nach Sektor gruppiert.

    Reihenfolge ist immer Sektor 1–8 (nicht nach Wert sortiert), damit die
    EI-Kalibrierung weiß, wo sie hinschauen muss. Fehlende Server-Werte
    werden als 0.0 angezeigt. ``neutral`` (kein Sektor) erscheint separat
    am Ende, falls vorhanden.
    """
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

    header = Gtk.Label(label=title)
    header.set_xalign(0.0)
    header.add_css_class("heading")
    section.append(header)

    for sektor_name, emo_namen, gruppe in sektoren:
        section.append(_build_sektor_label(sektor_name))
        for name in emo_namen:
            wert = float(emotions.get(name, 0.0))
            section.append(_build_emotion_row(name, wert, gruppe))

    # ``neutral`` gehört keinem Sektor an — separat unten anzeigen.
    if "neutral" in emotions:
        section.append(_build_sektor_label("Sonstige"))
        section.append(
            _build_emotion_row("neutral", float(emotions["neutral"]), "neutral")
        )

    return section


def _build_sektor_label(name: str) -> Gtk.Label:
    """Kleine, graue Sektor-Überschrift über jedem Emotions-Paar."""
    label = Gtk.Label(label=name)
    label.set_xalign(0.0)
    label.add_css_class("dim-label")
    label.add_css_class("caption")
    return label


def _build_emotion_row(name: str, wert: float, gruppe: str) -> Gtk.Box:
    """Baut eine Zeile: Name | Prozent | LevelBar (Gruppe als CSS-Klasse)."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

    name_label = Gtk.Label(label=f"  {name}")
    name_label.set_xalign(0.0)
    name_label.set_width_chars(16)
    row.append(name_label)

    wert_label = Gtk.Label(label=f"{wert:.2f}")
    wert_label.set_xalign(1.0)
    wert_label.set_width_chars(5)
    row.append(wert_label)

    bar = Gtk.LevelBar()
    bar.set_min_value(0.0)
    bar.set_max_value(1.0)
    bar.set_value(max(0.0, min(1.0, float(wert))))
    bar.set_hexpand(True)
    bar.set_valign(Gtk.Align.CENTER)

    bar.add_css_class(_GROUP_CSS_CLASS.get(gruppe, _GROUP_CSS_CLASS["neutral"]))
    row.append(bar)

    return row
