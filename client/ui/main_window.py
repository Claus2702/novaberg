"""
Hauptfenster des Nova-Clients.

Layout (vertikal, von oben nach unten):

    ┌───────────────────────────────────────┐
    │ Toolbar (Gtk.FlowBox mit Buttons)     │
    ├───────────────────────────────────────┤
    │ Chat-Bereich (ChatView.webview)       │
    ├───────────────────────────────────────┤
    │ [Eingabefeld_____________] [Senden]   │
    ├───────────────────────────────────────┤
    │ StatusBar                             │
    └───────────────────────────────────────┘

Alle Toolbar-Buttons sind derzeit Platzhalter — ihre Handler loggen
nur, dass das jeweilige Panel noch nicht implementiert ist. Die
eigentliche Geschäftslogik sitzt in :class:`ChatView` und
:class:`StreamHandler`.
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from config import (  # noqa: E402
    DEFAULT_USER_ID,
    STATUSBAR_BG_COLOR,
    STATUSBAR_TEXT_COLOR,
    TOOLBAR_BG_COLOR,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
)
from ui.chat_view      import ChatView                    # noqa: E402
from ui.panel_registry import PanelRegistry, create_default_registry  # noqa: E402
from ui.status_bar     import StatusBar                   # noqa: E402
from ui.stream_handler import (                           # noqa: E402
    StreamHandler,
    ZUORDNUNG_FREMD,
    ZUORDNUNG_UNBEOBACHTET,
)


logger = logging.getLogger(__name__)


# Panel-Buttons für die obere Toolbar (deutsche UI-Texte).
_TOOLBAR_PANELS: list[str] = [
    "Emotionen",
    "Session",
    "KZG",
    "LZG",
    "🧬 Charakter",
    "🎯 Ziele & Antrieb",
    "🌌 Gravitationsgraph",
    "🧭 Gesprächsvektor",
    "Fakten",
    "System",
    "Pixie",
    "PostgreSQL",
    "Redis",
    "Logs",
]


class MainWindow(Gtk.ApplicationWindow):
    """Nova-Hauptfenster inklusive Chat, Toolbar und Statuszeile."""

    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        logger.info("MainWindow wird initialisiert")

        # Grundeigenschaften
        self.set_title(WINDOW_TITLE)
        self.set_default_size(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.set_size_request(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Panel-Registry (liefert die Panel-Klassen für die Toolbar).
        self._registry: PanelRegistry = create_default_registry()

        # Kindmodule
        self._chat_view:  ChatView      = ChatView()
        self._status_bar: StatusBar     = StatusBar()
        self._stream:     StreamHandler = StreamHandler(
            on_stage      = self._handle_stage,
            on_answer     = self._handle_answer,
            on_error      = self._handle_error,
            on_done       = self._handle_done,
            on_impulse    = self._handle_impulse,
            on_connection = self._handle_connection,
            user_id       = DEFAULT_USER_ID,
        )

        # Flag: Warten wir auf eine WebSocket-Antwort nach Pfad 1?
        self._awaiting_response: bool = False

        # UI-Baum aufsetzen
        self._build_ui()

        # Eigenes CSS laden (Separator-Linien, StatusBar-Typo)
        self._apply_css()

        # Beim Schließen sauber aufräumen (Threads stoppen)
        self.connect("close-request", self._on_close_request)

        # Dauer-WebSocket starten
        self._stream.start_websocket()

        logger.info("MainWindow ist bereit")

    # ═════════════════════════════════════════════════════════════
    # UI-Aufbau
    # ═════════════════════════════════════════════════════════════
    def _build_ui(self) -> None:
        """Legt den Widget-Baum an und hängt ihn als Fenster-Inhalt ein."""
        logger.debug("MainWindow: UI wird aufgebaut")

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Toolbar
        toolbar = self._build_toolbar()
        toolbar.add_css_class("nova-toolbar")
        root.append(toolbar)
        root.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        # Chat-WebView — soll den gesamten verfügbaren Platz einnehmen
        chat_widget = self._chat_view.webview
        chat_widget.set_hexpand(True)
        chat_widget.set_vexpand(True)
        root.append(chat_widget)

        # Eingabezeile
        root.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        root.append(self._build_input_row())

        # Statuszeile
        root.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        root.append(self._status_bar)

        self.set_child(root)

    def _build_toolbar(self) -> Gtk.FlowBox:
        """Erzeugt die obere Panel-Leiste aus :data:`_TOOLBAR_PANELS`.

        Buttons, deren Label zu einem registrierten Panel passt, werden mit
        der Registry verdrahtet. Alle anderen Buttons bleiben Platzhalter
        und loggen beim Klick nur einen Hinweis.

        **Der Anzeigetext ist zugleich der Verbindungsschlüssel.** Ein
        Button findet sein Panel nur bei exakter Übereinstimmung mit
        ``PANEL_LABEL``. Wer eine Beschriftung an einer der beiden Stellen
        ändert, trennt die Verbindung — der Reiter öffnet dann nichts mehr,
        ohne dass ein Fehler entsteht. Dagegen steht die Prüfung unten.
        """
        # Label → PANEL_ID für alle registrierten Panels.
        label_to_panel_id: dict[str, str] = {
            panel_class.PANEL_LABEL: panel_class.PANEL_ID
            for panel_class in self._registry.get_panel_types()
        }

        # Ein registriertes Panel ohne Button ist unerreichbar. Das ist der
        # Ausgang jeder Beschriftungs-Drift und heute nur daran zu merken,
        # dass ein Klick nichts tut — deshalb hier laut, nicht erst dort.
        ohne_button: list[str] = [
            label for label in label_to_panel_id if label not in _TOOLBAR_PANELS
        ]
        if ohne_button:
            logger.error(
                f"Toolbar: {len(ohne_button)} registrierte Panels haben keinen "
                f"Button — Beschriftung und PANEL_LABEL laufen auseinander: "
                f"{', '.join(ohne_button)}"
            )

        # Gezählt wird, was verdrahtet wurde. Die frühere Fassung meldete
        # stattdessen die Zahl der registrierten Panels und wäre bei genau
        # dieser Drift unverändert geblieben
        # (novaberg-lesson_l_log-behauptet-was-es-weiss.md).
        verdrahtet: int = sum(1 for lbl in _TOOLBAR_PANELS if lbl in label_to_panel_id)
        logger.debug(
            f"Toolbar wird aufgebaut ({len(_TOOLBAR_PANELS)} Buttons, "
            f"davon {verdrahtet} verdrahtet, "
            f"{len(_TOOLBAR_PANELS) - verdrahtet} Platzhalter)"
        )

        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_homogeneous(False)
        flow.set_max_children_per_line(20)
        flow.set_min_children_per_line(1)
        flow.set_row_spacing(2)
        flow.set_column_spacing(2)
        flow.set_margin_start(4)
        flow.set_margin_end(4)
        flow.set_margin_top(3)
        flow.set_margin_bottom(3)

        for label in _TOOLBAR_PANELS:
            button = Gtk.Button(label=label)
            button.set_tooltip_text(f"Panel '{label}' öffnen")
            button.add_css_class("toolbar-button")

            panel_id: str | None = label_to_panel_id.get(label)
            if panel_id is not None:
                button.connect("clicked", self._on_panel_button_clicked, panel_id)
            else:
                button.connect("clicked", self._on_toolbar_click, label)

            child = Gtk.FlowBoxChild()
            child.set_child(button)
            flow.append(child)

        return flow

    def _build_input_row(self) -> Gtk.Box:
        """Erzeugt die Eingabezeile (Entry + Senden-Button)."""
        logger.debug("Eingabezeile wird aufgebaut")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_margin_start(8)
        row.set_margin_end(8)
        row.set_margin_top(6)
        row.set_margin_bottom(6)

        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("Nachricht an Nova …")
        self._entry.set_hexpand(True)
        self._entry.connect("activate", self._on_entry_activate)

        # Emoji-Picker (öffnet den gleichen Chooser wie Strg+Punkt).
        self._emoji_button = Gtk.Button(label="😊")
        self._emoji_button.set_tooltip_text("Emoji einfügen")
        self._emoji_button.set_focusable(False)
        self._emoji_button.set_focus_on_click(False)
        self._emoji_button.connect("clicked", self._on_emoji_clicked)

        self._send_button = Gtk.Button(label="Senden")
        self._send_button.add_css_class("suggested-action")
        self._send_button.connect("clicked", self._on_send_clicked)

        row.append(self._emoji_button)
        row.append(self._entry)
        row.append(self._send_button)
        return row

    def _apply_css(self) -> None:
        """Hängt globales CSS ans Display (Separator, Statuszeile)."""
        css_provider = Gtk.CssProvider()
        css: str = f"""
            .nova-toolbar {{
                background-color: {TOOLBAR_BG_COLOR};
            }}
            .nova-statusbar {{
                background-color: {STATUSBAR_BG_COLOR};
                color: {STATUSBAR_TEXT_COLOR};
            }}
            .nova-statusbar-label {{
                font-size: 12px;
                color: {STATUSBAR_TEXT_COLOR};
            }}
            .toolbar-button {{
                font-size: 11px;
                padding: 1px 6px;
                min-height: 0;
                min-width: 0;
            }}
        """
        # Gtk 4: load_from_string statt load_from_data (seit 4.12 empfohlen).
        if hasattr(css_provider, "load_from_string"):
            css_provider.load_from_string(css)
        else:
            css_provider.load_from_data(css.encode("utf-8"))

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        logger.debug("Eigenes CSS wurde an das Display gehängt")

    # ═════════════════════════════════════════════════════════════
    # Signal-Handler
    # ═════════════════════════════════════════════════════════════
    def _on_toolbar_click(self, button: Gtk.Button, panel_name: str) -> None:
        """Platzhalter-Handler für noch nicht registrierte Toolbar-Buttons."""
        logger.info(f"Panel noch nicht implementiert: {panel_name}")

    def _on_panel_button_clicked(self, button: Gtk.Button, panel_id: str) -> None:
        """Öffnet ein registriertes Panel über die :class:`PanelRegistry`."""
        logger.debug(f"Toolbar-Klick: Panel '{panel_id}' öffnen")
        child_window = self._registry.open_panel(panel_id, self)
        if child_window is not None:
            child_window.present()

    def _on_entry_activate(self, entry: Gtk.Entry) -> None:
        """Enter-Taste im Eingabefeld → Nachricht senden."""
        logger.debug("Eingabe via Enter-Taste ausgelöst")
        self._send_current_input()

    def _on_emoji_clicked(self, button: Gtk.Button) -> None:
        """Öffnet den GTK-Emoji-Chooser für das Eingabefeld.

        Das ``insert-emoji``-Signal hängt in GTK4 am internen ``Gtk.Text``-
        Delegate der ``Gtk.Entry``, nicht am Entry selbst. ``get_delegate()``
        liefert genau dieses Widget.
        """
        logger.debug("Emoji-Chooser wird geöffnet")
        text_widget = self._entry.get_delegate()
        if text_widget is None:
            logger.warning("Entry hat kein Text-Delegate — Emoji-Chooser nicht verfügbar")
            return
        # Fokus ohne Selektion zurück ins Textfeld (sonst markiert GTK den ganzen Inhalt).
        text_widget.grab_focus_without_selecting()
        text_widget.emit("insert-emoji")

    def _on_send_clicked(self, button: Gtk.Button) -> None:
        """Klick auf den Senden-Button → Nachricht senden."""
        logger.debug("Eingabe via Senden-Button ausgelöst")
        self._send_current_input()

    def _send_current_input(self) -> None:
        """Liest das Entry, zeigt die User-Bubble und startet den Stream."""
        text: str = self._entry.get_text().strip()
        if not text:
            logger.debug("Leere Eingabe — ignoriert")
            return

        logger.info(f"Nachricht wird gesendet ({len(text)} Zeichen)")
        self._entry.set_text("")

        # Bubble sofort anzeigen, damit der User Feedback sieht.
        self._chat_view.add_user_message(text)

        # **Keine Sperre mehr.** Der Server nimmt die Äußerung sofort an und
        # bestätigt in Millisekunden; was während eines laufenden Turns
        # eintrifft, wartet in der Eingangs-Queue und wird mit dem nächsten
        # Block zusammen verarbeitet. Die Sperre hätte keinen Nutzen mehr —
        # sie hatte aber einen Preis: Blieb eine Antwort aus, blieb die
        # Oberfläche unbenutzbar, bis irgendeine andere eintraf.
        self._awaiting_response = True
        self._status_bar.set_connection_status("Gesendet")

        self._stream.send_message(text)

    def _on_close_request(self, window: Gtk.ApplicationWindow) -> bool:
        """Beim Schließen: Threads stoppen, dann Fenster endgültig schließen."""
        logger.info("Schließen-Anforderung — StreamHandler wird gestoppt")
        self._stream.stop()
        # ``False`` → Schließen nicht verhindern (Default-Handler übernimmt).
        return False

    # ═════════════════════════════════════════════════════════════
    # Callbacks vom StreamHandler (laufen im UI-Thread)
    # ═════════════════════════════════════════════════════════════
    def _handle_stage(self, label: str, detail: str) -> None:
        logger.debug(f"Stage: {label} — {detail}")
        self._chat_view.show_stage(label, detail)

    def _handle_answer(self, antwort: str, meta: dict) -> None:
        zuordnung: str = meta.get("zuordnung", ZUORDNUNG_UNBEOBACHTET)

        logger.info(
            f"Antwort empfangen ({len(antwort)} Zeichen, "
            f"Modell={meta.get('modell', '?')}, "
            f"Tokens={meta.get('token_total', '?')}, "
            f"Zuordnung={zuordnung})"
        )
        self._chat_view.clear_stages()

        if zuordnung == ZUORDNUNG_FREMD:
            # Die letzte Nachricht ist unbeantwortet geblieben, und was hier
            # ankommt, gehoert zu einem anderen Reiz. Ohne den Vermerk waere
            # das nicht erkennbar: Die Antwort liest sich fluessig und
            # geschlossen, sie passt nur nicht zur Frage.
            self._chat_view.add_unzugeordnete_antwort(
                antwort,
                "⚠ **Diese Antwort gehört nicht zu deiner letzten Nachricht.** "
                "Sie blieb unbeantwortet.",
            )
        else:
            self._chat_view.add_assistant_message(antwort)

        self._awaiting_response = False
        self._status_bar.set_connection_status("Verbunden")

        # Pixie-Momentum-Anzeige aktualisieren (optional, nur wenn gesetzt)
        momentum: str = meta.get("momentum", "")
        if momentum:
            self._status_bar.set_pixie_status(f"Pixie: momentum={momentum}")

        # Turn-Daten an alle offenen turn_reactive-Panels weiterleiten.
        turn_data: dict = {"antwort": antwort, **meta}
        self._registry.broadcast_turn(turn_data)

    def _handle_error(self, message: str) -> None:
        logger.error(f"Stream-Fehler: {message}")
        self._chat_view.clear_stages()
        self._chat_view.add_assistant_message(f"**Fehler:** {message}")

        self._awaiting_response = False
        self._status_bar.set_connection_status("Getrennt")

    def _handle_done(self) -> None:
        """Der Endpunkt hat die Äußerung angenommen — mehr sagt das Stream-Ende nicht.

        Die Eingabe war nie gesperrt, es gibt also nichts freizugeben. Der
        Status sagt nur noch, ob noch eine Antwort erwartet wird.
        """
        if self._awaiting_response:
            logger.debug("Annahme bestätigt — die Antwort kommt per WebSocket")
            self._status_bar.set_connection_status("Verarbeite...")
            return

        self._status_bar.set_connection_status("Verbunden")

    def _handle_impulse(self, text: str, data: dict) -> None:
        if data.get("typ") == "user_message":
            # User-Eingabe von einem anderen Client — als User-Bubble anzeigen.
            logger.info(f"User-Nachricht von anderem Client: {text[:80]!r}")
            self._chat_view.add_user_message(text)
        else:
            logger.info(f"Pixie-Impuls empfangen: {text[:80]!r}")
            self._chat_view.add_impulse_message(text)

    def _handle_connection(self, status: str) -> None:
        logger.debug(f"Verbindungsstatus -> {status}")
        self._status_bar.set_connection_status(status)
