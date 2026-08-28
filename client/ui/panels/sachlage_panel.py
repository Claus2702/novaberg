"""
Gespraechskontext-Panel — die fuenf Scheiben des Lage-Konzepts in einem Tab.

Das Panel ist ``turn_reactive`` und holt seine Daten ueber
``GET /drive/kontext`` (server: ``api/drive.py::kontext_lesen``). Der
Sachlage-Knoten (``graph/nodes/sachlage.py``, Konzept
``novaberg-thinking-lage_k.md``) schreibt die Blase je Turn fortgeschrieben
nach Redis und jede gerechnete als Faktum nach ``sachlage_verlauf``; das
Panel laedt beim Oeffnen und nach jedem Turn neu.

Anzeige (kompakt):

    Blase: Rettich-Bewaesserung          fortgeschrieben · vor 12 s
    Verfall  ████████░░  3,9 h von 4 h
    Worum es geht:   Die Bewertung von Bewaesserungsmethoden fuer Rettich
    Nutzerziel:      vermutlich die schonendere Methode kennen
    Ausdrucksweise:  pruefend
    ↩ zurueck zu »Gravitationslinse«  (Kosinus 0,62, vor 2 h)          [Scheibe 5]

    ● Rettich bewaessern  (vorgang, akut)   Strecke 2/2 → Ziel #28576  [Scheibe 2]
      ✓ problemstellung: Wurzeln platzen
      ★ Intervall   ○ Kosten                                            [Scheibe 3]

    Rueckfrage-Gegenstand: Rettich bewaessern — was dazu noch offen ist: Intervall

    Kurzfristige Ziele
      #28576  Rettich bewaessern   ██████░░░░ 0,53   verfaellt in 5,4 h

    Verlauf der Blasen
      18:47  Exoplaneten-Transitmethodik   Die Bestimmung der Umlaufzeit …
      17:24  Astrophysikalische Magnetfelder  …

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte und Logs deutsch.
"""

import logging
from datetime import datetime, timezone

import requests

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from config import PANEL_REQUEST_TIMEOUT, SERVER_URL  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


class SachlagePanel(PanelBase):
    """Der Gespraechskontext: Blase, Objekte, Frage-Gegenstand, Kurzziele, Verlauf."""

    PANEL_ID    = "sachlage"
    PANEL_LABEL = "🫧 Gesprächskontext"
    UNIQUE      = True
    CATEGORY    = "turn_reactive"
    NEEDS_USER_SELECTOR = False
    DEFAULT_WIDTH  = 560
    DEFAULT_HEIGHT = 720

    def _build_content(self) -> None:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        scroll.set_child(self._outer_box)

        self._outer_box.append(_dim_label("Noch kein Gesprächskontext empfangen"))
        self.content_area.append(scroll)

    def load_data(self) -> dict:
        """Holt den Gespraechskontext vom Server (Redis-Snapshot, Ziele, Verlauf)."""
        url: str = f"{SERVER_URL}/drive/kontext"
        logger.debug(f"SachlagePanel: GET {url}")
        response = requests.get(url, timeout=PANEL_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json() or {}

    def _update_ui(self, data: dict) -> None:
        """Baut die Sektionen aus der aktuellen Antwort neu auf."""
        _clear_box(self._outer_box)
        sachlage: dict = data.get("sachlage") or {}

        if not sachlage and not data.get("verlauf"):
            self._outer_box.append(_dim_label("Noch kein Gesprächskontext empfangen"))
            return

        if sachlage:
            self._outer_box.append(_build_bubble_section(
                sachlage, float(data.get("verfall_sekunden") or 0),
            ))
            self._outer_box.append(_build_objects_section(
                sachlage, data.get("kurzziel") or {}, data.get("frage_gegenstand"),
            ))
        else:
            self._outer_box.append(_dim_label("Keine lebende Blase — die letzte ist verfallen"))

        self._outer_box.append(_build_short_goals_section(
            data.get("kurzziele") or [], float(data.get("deaktivierungs_schwelle") or 0.15),
        ))
        self._outer_box.append(_build_history_section(data.get("verlauf") or []))

    # ═══════════════════════════════════════════════════════════════
    # Turn-Reactive: nach jedem Turn neu vom Server laden
    # ═══════════════════════════════════════════════════════════════
    def on_turn_received(self, turn_data: dict) -> None:
        """Wird nach jedem Turn aufgerufen — Refresh holt frische Daten via REST."""
        self.refresh()


# ═══════════════════════════════════════════════════════════════════
# Hilfsfunktionen — Layout
# ═══════════════════════════════════════════════════════════════════
def _clear_box(box: Gtk.Box) -> None:
    child = box.get_first_child()
    while child is not None:
        box.remove(child)
        child = box.get_first_child()


def _dim_label(text: str) -> Gtk.Label:
    label = Gtk.Label(label=text)
    label.set_xalign(0.0)
    label.set_wrap(True)
    label.add_css_class("dim-label")
    return label


def _heading(text: str) -> Gtk.Label:
    label = Gtk.Label(label=text)
    label.set_xalign(0.0)
    label.set_hexpand(True)
    label.add_css_class("heading")
    return label


def _text_row(text: str, css: str = "") -> Gtk.Label:
    label = Gtk.Label(label=text)
    label.set_xalign(0.0)
    label.set_wrap(True)
    if css:
        label.add_css_class(css)
    return label


def _alter_text(sekunden: float) -> str:
    """Menschlich lesbares Alter."""
    if sekunden < 90:
        return f"vor {sekunden:.0f} s"
    if sekunden < 5400:
        return f"vor {sekunden / 60:.0f} min"
    if sekunden < 172800:
        return f"vor {sekunden / 3600:.1f} h"
    return f"vor {sekunden / 86400:.0f} Tagen"


def _age_seconds(iso: str) -> float | None:
    """Alter eines ISO-Zeitstempels in Sekunden; None, wenn unlesbar."""
    try:
        damals = datetime.fromisoformat(str(iso))
    except (TypeError, ValueError):
        return None
    if damals.tzinfo is None:
        damals = damals.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - damals).total_seconds())


def _uhrzeit(iso: str) -> str:
    """HH:MM (UTC) aus einem ISO-Zeitstempel; leer, wenn unlesbar."""
    try:
        return datetime.fromisoformat(str(iso)).strftime("%H:%M")
    except (TypeError, ValueError):
        return ""


def _build_bubble_section(sachlage: dict, verfall_sekunden: float) -> Gtk.Box:
    """Scheibe 1 (und 5): die Blase — Thema, Herkunft, Alter, Verfall, Verstehen, Wiederaufnahme."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    kopf = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    thema: str = str(sachlage.get("thema") or "").strip()
    kopf.append(_heading(f"Blase: {thema}" if thema else "Blase"))
    herkunft: str = str(sachlage.get("herkunft", ""))
    alter = sachlage.get("alter_sekunden")
    meta_teile: list[str] = [t for t in (
        herkunft, _alter_text(float(alter)) if alter is not None else "",
    ) if t]
    if meta_teile:
        meta = Gtk.Label(label=" · ".join(meta_teile))
        meta.add_css_class("dim-label")
        kopf.append(meta)
    section.append(kopf)

    if alter is not None and verfall_sekunden > 0:
        rest: float = max(0.0, verfall_sekunden - float(alter))
        section.append(_build_bar_row(
            "Verfall", 0.0, verfall_sekunden, rest,
            f"{rest / 3600:.1f} h",
            f"von {verfall_sekunden / 3600:.0f} h — ohne Turn verfällt die Blase",
        ))

    for titel, schluessel in (
        ("Worum es geht", "gegenstand"),
        ("Nutzerziel", "nutzerziel"),
        ("Ausdrucksweise", "ausdrucksweise"),
    ):
        section.append(_text_row(f"{titel}:  {sachlage.get(schluessel) or '—'}"))

    fruehere: dict = sachlage.get("wiederaufnahme") or {}
    if fruehere:
        alter_frueher = _age_seconds(str(fruehere.get("erstellt_am", "")))
        teile: list[str] = [f"↩ zurück zu »{fruehere.get('thema', '?')}«"]
        if fruehere.get("kosinus") is not None:
            teile.append(f"Kosinus {float(fruehere['kosinus']):.2f}")
        if alter_frueher is not None:
            teile.append(_alter_text(alter_frueher))
        section.append(_text_row("  ".join(teile) + "   [Wiederaufnahme]"))

    return section


def _build_objects_section(
    sachlage: dict, kurzziel: dict, frage_gegenstand: str | None,
) -> Gtk.Box:
    """Die Referenzobjekte samt Strecke (Scheibe 2) und Frage-Gegenstand (Scheibe 3)."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    objekte: list = [o for o in (sachlage.get("objekte") or []) if isinstance(o, dict)]
    if not objekte:
        section.append(_dim_label("Keine Referenzobjekte im Raum"))
        return section

    strecken: dict = kurzziel.get("strecken") or {}
    ziel_ids: dict = kurzziel.get("ziele") or {}
    ziel_eigenschaft: str = _property_of(frage_gegenstand)

    for objekt in objekte:
        block = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        akut: bool = bool(objekt.get("akut"))
        name: str = str(objekt.get("name", "?"))
        schluessel: str = " ".join(name.lower().split())
        titel_teile: list[str] = [
            f"{'●' if akut else '○'} {name}  "
            f"({objekt.get('klasse') or '?'}, {'akut' if akut else 'latent'})",
        ]
        if akut and schluessel in strecken:
            ziel_text: str = f" → Ziel #{ziel_ids[schluessel]}" if ziel_ids.get(schluessel) else ""
            titel_teile.append(f"Strecke {strecken[schluessel]}/2{ziel_text}")
        titel = _text_row("   ".join(titel_teile), "heading" if akut else "dim-label")
        block.append(titel)

        for eigenschaft, wert in list((objekt.get("gedeckt") or {}).items())[:6]:
            block.append(_text_row(f"  ✓ {eigenschaft}: {wert}"))

        offen: list = objekt.get("offen") or []
        if offen:
            marken: list[str] = [
                f"{'★' if akut and str(o) == ziel_eigenschaft else '○'} {o}" for o in offen[:5]
            ]
            block.append(_text_row("  " + "   ".join(marken)))
        section.append(block)

    if frage_gegenstand:
        section.append(_text_row(
            f"Rückfrage-Gegenstand:  {frage_gegenstand}   "
            f"(★ — ob gefragt wird, entscheidet die Haltung)",
        ))
    else:
        section.append(_dim_label(
            "Rückfrage-Gegenstand:  keiner — kein akutes Objekt mit offener Eigenschaft",
        ))
    return section


def _property_of(frage_gegenstand: str | None) -> str:
    """Die Eigenschaft hinter »was dazu noch offen ist:« — fuer die ★-Markierung."""
    if not frage_gegenstand or "offen ist:" not in frage_gegenstand:
        return ""
    return frage_gegenstand.split("offen ist:", 1)[1].strip()


def _build_short_goals_section(kurzziele: list, schwelle: float) -> Gtk.Box:
    """Scheibe 2: die lebenden kurzfristigen Ziele mit Live-Motivation und Restlaufzeit."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    section.append(_heading("Kurzfristige Ziele"))
    if not kurzziele:
        section.append(_dim_label(
            "keine — entsteht, wenn zwei Lagen hintereinander dasselbe akute Objekt tragen",
        ))
        return section
    for ziel in kurzziele:
        vorhaben: str = str(ziel.get("zielsatz", "")).split("helfen: ", 1)[-1].split(" — ", 1)[0]
        motivation: float = float(ziel.get("motivation") or 0.0)
        rest = ziel.get("verfaellt_in_stunden")
        zusatz: str = f"verfällt in {float(rest):.1f} h" if rest is not None else "ohne Anker"
        section.append(_build_bar_row(
            f"#{ziel.get('id')}", 0.0, 1.0, motivation, f"{motivation:.2f}",
            f"{vorhaben[:48]} · {zusatz} (Schwelle {schwelle:.2f})",
        ))
    return section


def _build_history_section(verlauf: list) -> Gtk.Box:
    """Scheibe 4: die juengsten Blasen des Paares, juengste zuerst."""
    section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    section.append(_heading("Verlauf der Blasen"))
    if not verlauf:
        section.append(_dim_label("noch keine Verlaufszeile"))
        return section
    for zeile in verlauf:
        if not isinstance(zeile, dict):
            continue
        gegenstand: str = str(zeile.get("gegenstand") or "")
        section.append(_text_row(
            f"  {_uhrzeit(str(zeile.get('erstellt_am', '')))}  {zeile.get('thema') or '?'}"
            f"   {gegenstand[:90]}{'…' if len(gegenstand) > 90 else ''}",
            "caption",
        ))
    return section


def _build_bar_row(
    label_text: str, bar_min: float, bar_max: float, bar_value: float,
    wert_text: str, zusatz_text: str = "",
) -> Gtk.Box:
    """Eine Zeile: Label | LevelBar | Wert | (optional) Zusatz — wie im GV-Panel."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    name = Gtk.Label(label=label_text)
    name.set_xalign(0.0)
    name.set_width_chars(8)
    name.add_css_class("caption")
    row.append(name)
    bar = Gtk.LevelBar()
    bar.set_min_value(bar_min)
    bar.set_max_value(bar_max)
    bar.set_value(min(max(bar_value, bar_min), bar_max))
    bar.set_hexpand(True)
    bar.set_valign(Gtk.Align.CENTER)
    row.append(bar)
    wert = Gtk.Label(label=wert_text)
    wert.set_xalign(1.0)
    wert.set_width_chars(6)
    wert.add_css_class("caption")
    row.append(wert)
    if zusatz_text:
        zusatz = Gtk.Label(label=zusatz_text)
        zusatz.set_xalign(0.0)
        zusatz.set_wrap(True)
        zusatz.add_css_class("dim-label")
        zusatz.add_css_class("caption")
        row.append(zusatz)
    return row
