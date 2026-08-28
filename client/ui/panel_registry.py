"""
Panel-Registry — verwaltet Panel-Typen und offene Instanzen.

Die Registry kennt zwei Datenstrukturen:

* ``_panel_types`` — Abbildung von ``PANEL_ID`` auf die Panel-Klasse.
  Das Hauptfenster liest diese Liste, um Toolbar-Buttons für jeden
  registrierten Panel-Typ anzulegen.

* ``_open_panels`` — Tracking offener Fenster für ``UNIQUE``-Panels,
  Key ``(panel_id, user_id)``. Nicht-``UNIQUE``-Panels werden hier nicht
  getrackt (davon darf es beliebig viele geben).

Darüber hinaus bietet die Registry :meth:`broadcast_turn`, um Turn-
Ereignisse (SSE-Answer) an alle offenen ``turn_reactive``-Panels
weiterzuleiten.
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from ui.child_window import ChildWindow  # noqa: E402
from ui.panel_base import PanelBase  # noqa: E402


logger = logging.getLogger(__name__)


class PanelRegistry:
    """Zentrale Registrierung und Lifecycle-Verwaltung von Panels."""

    def __init__(self) -> None:
        logger.debug("PanelRegistry wird initialisiert")
        # {"system": SystemPanel, "kzg": KzgPanel, ...}
        self._panel_types: dict[str, type[PanelBase]] = {}
        # {("system", "meister"): ChildWindow, ...} — nur für UNIQUE-Panels.
        self._open_panels: dict[tuple[str, str], ChildWindow] = {}

    # ═══════════════════════════════════════════════════════════════
    # Registrierung
    # ═══════════════════════════════════════════════════════════════
    def register(self, panel_class: type[PanelBase]) -> None:
        """Registriert eine Panel-Klasse anhand ihrer ``PANEL_ID``."""
        panel_id: str = panel_class.PANEL_ID
        if not panel_id:
            logger.warning(
                f"Panel-Klasse {panel_class.__name__} hat keine PANEL_ID — ignoriert"
            )
            return

        if panel_id in self._panel_types:
            logger.warning(
                f"Panel-ID '{panel_id}' wird überschrieben "
                f"(alt: {self._panel_types[panel_id].__name__}, "
                f"neu: {panel_class.__name__})"
            )

        self._panel_types[panel_id] = panel_class
        logger.info(
            f"Panel registriert: '{panel_id}' ({panel_class.__name__}, "
            f"Label='{panel_class.PANEL_LABEL}')"
        )

    def get_panel_types(self) -> list[type[PanelBase]]:
        """Gibt alle registrierten Panel-Klassen (in Einfüge-Reihenfolge) zurück."""
        return list(self._panel_types.values())

    # ═══════════════════════════════════════════════════════════════
    # Öffnen / Schließen
    # ═══════════════════════════════════════════════════════════════
    def open_panel(
        self,
        panel_id: str,
        parent_window: Gtk.Window,
    ) -> ChildWindow | None:
        """Öffnet ein Panel.

        Rückgabewerte:
        * ``ChildWindow`` — neu erzeugtes Panel-Fenster, noch nicht präsentiert.
        * ``None`` — Panel war ``UNIQUE`` und bereits offen. In diesem Fall
          wird das existierende Fenster fokussiert.
        """
        panel_class: type[PanelBase] | None = self._panel_types.get(panel_id)
        if panel_class is None:
            logger.warning(f"Panel-ID '{panel_id}' ist nicht registriert")
            return None

        # Für UNIQUE-Panels prüfen, ob schon ein Fenster für diesen User offen ist.
        # User-ID bestimmen wir aus der (noch nicht erzeugten) Default-Auswahl:
        # Panels ohne User-Selector haben user_id == "meister" (Default).
        # Daher reicht es, die Instanz erst zu bauen und DANN zu prüfen.
        panel: PanelBase = panel_class()
        user_id: str = panel.user_id
        key: tuple[str, str] = (panel_id, user_id)

        if panel_class.UNIQUE and key in self._open_panels:
            # Existierendes Fenster in den Vordergrund holen.
            existing: ChildWindow = self._open_panels[key]
            logger.info(
                f"Panel '{panel_id}' (user='{user_id}') ist bereits offen — "
                f"Fenster wird fokussiert"
            )
            existing.present()
            return None

        # Neues Fenster erzeugen.
        child_window = ChildWindow(panel=panel, registry=self)
        child_window.set_transient_for(parent_window)

        if panel_class.UNIQUE:
            self._open_panels[key] = child_window
            logger.info(
                f"UNIQUE-Panel geöffnet: '{panel_id}' (user='{user_id}') — "
                f"insgesamt offen: {len(self._open_panels)}"
            )
        else:
            logger.info(f"Panel geöffnet: '{panel_id}' (nicht UNIQUE, ungetrackt)")

        # Erstes Laden der Daten.
        panel.refresh()
        return child_window

    def on_panel_closed(self, panel: PanelBase) -> None:
        """Entfernt ein geschlossenes UNIQUE-Panel aus dem Tracking."""
        if not panel.UNIQUE:
            logger.debug(f"Panel '{panel.PANEL_ID}' geschlossen (nicht UNIQUE)")
            return

        key: tuple[str, str] = (panel.PANEL_ID, panel.user_id)
        if key in self._open_panels:
            del self._open_panels[key]
            logger.info(
                f"UNIQUE-Panel entfernt: '{panel.PANEL_ID}' (user='{panel.user_id}') — "
                f"verbleibend: {len(self._open_panels)}"
            )
        else:
            # Kann passieren, wenn der User-Selector nach dem Öffnen umgestellt
            # wurde; dann passt der aktuelle user_id-Schlüssel nicht mehr. In
            # diesem Fall alle Einträge mit passender panel_id entfernen.
            stale_keys = [k for k in self._open_panels if k[0] == panel.PANEL_ID]
            for k in stale_keys:
                if self._open_panels[k].panel is panel:
                    del self._open_panels[k]
                    logger.info(
                        f"UNIQUE-Panel (Schlüssel veraltet) entfernt: {k}"
                    )
                    return
            logger.debug(
                f"Panel '{panel.PANEL_ID}' geschlossen, aber kein Tracking-Eintrag "
                f"gefunden (key={key})"
            )

    # ═══════════════════════════════════════════════════════════════
    # Turn-Broadcast
    # ═══════════════════════════════════════════════════════════════
    def broadcast_turn(self, turn_data: dict) -> None:
        """Leitet Turn-Daten an alle offenen turn_reactive-Panels weiter."""
        if not self._open_panels:
            return

        benachrichtigt: int = 0
        for child_window in self._open_panels.values():
            panel: PanelBase = child_window.panel
            if panel.CATEGORY != "turn_reactive":
                continue
            try:
                panel.on_turn_received(turn_data)
                benachrichtigt += 1
            except Exception as fehler:
                logger.error(
                    f"Panel '{panel.PANEL_ID}': on_turn_received fehlgeschlagen: {fehler}"
                )

        if benachrichtigt:
            logger.debug(f"Turn an {benachrichtigt} Panel(s) verteilt")


# ═══════════════════════════════════════════════════════════════════
# Default-Registry mit allen bekannten Panel-Typen
# ═══════════════════════════════════════════════════════════════════
def create_default_registry() -> PanelRegistry:
    """Erzeugt eine Registry mit allen aktuell implementierten Panels."""
    logger.debug("Default-PanelRegistry wird erstellt")
    registry = PanelRegistry()

    # Bereits implementierte Panels.
    from ui.panels.character_panel import CharacterPanel
    from ui.panels.emotions_panel import EmotionsPanel
    from ui.panels.goals_panel import GoalsPanel
    from ui.panels.gravity_map_panel import GravityMapPanel
    from ui.panels.gv_panel import GvPanel
    from ui.panels.kzg_panel import KzgPanel
    from ui.panels.lzg_panel import LzgPanel
    from ui.panels.sachlage_panel import SachlagePanel
    from ui.panels.session_panel import SessionPanel
    from ui.panels.system_panel import SystemPanel

    registry.register(EmotionsPanel)
    registry.register(SessionPanel)
    registry.register(KzgPanel)
    registry.register(LzgPanel)
    registry.register(CharacterPanel)
    registry.register(GoalsPanel)
    registry.register(GravityMapPanel)
    registry.register(GvPanel)
    registry.register(SachlagePanel)
    registry.register(SystemPanel)

    # Platzhalter — werden in späteren Prompts registriert:
    # ...

    logger.info(
        f"Default-PanelRegistry fertig "
        f"({len(registry.get_panel_types())} Panel-Typen registriert)"
    )
    return registry
