"""
Chat-Rendering über eine eingebettete WebKitGTK-WebView.

Die gesamte Nachrichtendarstellung läuft über ein HTML-Template, das
beim Start geladen wird. Neue Nachrichten, Pipeline-Stages und Impulse
werden per JavaScript in den DOM des Templates eingefügt.

Design-Entscheidungen:
- Kein externer Ressourcen-Zugriff (kein CDN, kein externes CSS/JS).
- Emojis rendern nativ über die System-Schriften.
- User-Text wird HTML-escaped (kein Markdown), Assistant/Impuls-Text
  wird per Python-Markdown zu HTML konvertiert.
"""

import html
import logging

import gi
import markdown

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import WebKit  # noqa: E402

from config import (  # noqa: E402
    ASSISTANT_BUBBLE_COLOR,
    BACKGROUND_COLOR,
    BLOCKQUOTE_BORDER_COLOR,
    BLOCKQUOTE_TEXT_COLOR,
    FONT_FAMILY,
    FONT_SIZE,
    IMPULSE_BORDER_COLOR,
    IMPULSE_BUBBLE_COLOR,
    LINK_COLOR,
    MAX_MESSAGE_WIDTH_PERCENT,
    STAGE_TEXT_COLOR,
    TABLE_BORDER_COLOR,
    TEXT_COLOR,
    USER_BUBBLE_COLOR,
)


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HTML-Template (wird einmalig beim Start geladen)
#
# Die Platzhalter {USER_BUBBLE_COLOR} etc. werden per .format() ersetzt.
# Die JavaScript-Funktionen nutzen keine Template-Platzhalter und bleiben
# deshalb in geschweiften Klammern — doppelte Klammern {{ }} schützen sie.
# ─────────────────────────────────────────────
_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nova Chat</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    background-color: {BACKGROUND_COLOR};
    color: {TEXT_COLOR};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE};
    padding: 12px;
}}

#chat-container {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.message {{
    max-width: {MAX_MESSAGE_WIDTH_PERCENT}%;
    padding: 10px 14px;
    border-radius: 12px;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

.message-user {{
    background-color: {USER_BUBBLE_COLOR};
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}}

.message-assistant {{
    background-color: {ASSISTANT_BUBBLE_COLOR};
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}}

.message-impulse {{
    background-color: {IMPULSE_BUBBLE_COLOR};
    align-self: flex-start;
    border-bottom-left-radius: 4px;
    border-left: 3px solid {IMPULSE_BORDER_COLOR};
}}

.stage {{
    align-self: center;
    font-size: 12px;
    color: {STAGE_TEXT_COLOR};
    font-style: italic;
    padding: 1px 0;
}}

/* Aufeinanderfolgende Stage-Zeilen enger setzen: nimmt den 8px-Container-gap
   zwischen zwei Stages weitgehend zurueck, ohne die Message-Bubble-Abstaende
   anzufassen. Netto-Abstand Stage↔Stage ~4px statt ~16px. */
.stage + .stage {{
    margin-top: -6px;
}}

/* Markdown-Elemente in Assistant-/Impuls-Bubbles */
.message p {{ margin: 0.4em 0; }}
.message p:first-child {{ margin-top: 0; }}
.message p:last-child {{ margin-bottom: 0; }}

.message code {{
    background-color: rgba(0,0,0,0.3);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.9em;
}}

.message pre {{
    background-color: rgba(0,0,0,0.3);
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 8px 0;
}}

.message pre code {{
    background: none;
    padding: 0;
}}

.message table {{
    border-collapse: collapse;
    margin: 8px 0;
    width: 100%;
}}

.message th, .message td {{
    border: 1px solid {TABLE_BORDER_COLOR};
    padding: 6px 10px;
    text-align: left;
}}

.message th {{
    background-color: rgba(255,255,255,0.1);
}}

.message a {{ color: {LINK_COLOR}; }}

.message ul, .message ol {{
    padding-left: 1.5em;
    margin: 0.4em 0;
}}

.message blockquote {{
    border-left: 3px solid {BLOCKQUOTE_BORDER_COLOR};
    padding-left: 12px;
    margin: 8px 0;
    color: {BLOCKQUOTE_TEXT_COLOR};
}}
</style>
</head>
<body>
<div id="chat-container"></div>
<script>
// Fügt eine Nachrichten-Bubble in den Container ein. Vorher werden
// sämtliche Pipeline-Stage-Einträge entfernt, damit der Verlauf
// übersichtlich bleibt.
function addMessage(html, cssClass) {{
    const container = document.getElementById('chat-container');
    removeStages();
    const div = document.createElement('div');
    div.className = 'message ' + cssClass;
    div.innerHTML = html;
    container.appendChild(div);
    scrollToBottom();
}}

// Zeigt den Fortschritt eines Pipeline-Nodes an (klein, kursiv, zentriert).
function addStage(text) {{
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.className = 'stage';
    div.textContent = text;
    container.appendChild(div);
    scrollToBottom();
}}

// Entfernt sämtliche Stage-Einträge (z.B. nach Eintreffen der Antwort).
function removeStages() {{
    const stages = document.querySelectorAll('.stage');
    stages.forEach(s => s.remove());
}}

// Scrollt ans untere Ende, damit die neueste Nachricht sichtbar ist.
function scrollToBottom() {{
    window.scrollTo(0, document.body.scrollHeight);
}}
</script>
</body>
</html>
"""


class ChatView:
    """Kapselt die WebView und bietet eine High-Level-API für Nachrichten."""

    def __init__(self) -> None:
        logger.debug("ChatView wird initialisiert")

        # WebView anlegen und Grund-Konfiguration vornehmen
        self.webview = WebKit.WebView()
        settings: WebKit.Settings = self.webview.get_settings()
        # JavaScript benötigen wir für unsere Helfer-Funktionen.
        settings.set_enable_javascript(True)
        # Keine Datei-Zugriffe, keine Clipboard-Eskapaden.
        settings.set_javascript_can_access_clipboard(False)
        settings.set_allow_file_access_from_file_urls(False)
        settings.set_allow_universal_access_from_file_urls(False)
        # Entwickler-Werkzeuge helfen beim Debuggen des CSS/JS.
        settings.set_enable_developer_extras(True)

        # HTML-Template einmalig laden; die Farben/Schriften kommen aus config.
        html_content: str = _HTML_TEMPLATE.format(
            BACKGROUND_COLOR          = BACKGROUND_COLOR,
            TEXT_COLOR                = TEXT_COLOR,
            FONT_FAMILY               = FONT_FAMILY,
            FONT_SIZE                 = FONT_SIZE,
            MAX_MESSAGE_WIDTH_PERCENT = MAX_MESSAGE_WIDTH_PERCENT,
            USER_BUBBLE_COLOR         = USER_BUBBLE_COLOR,
            ASSISTANT_BUBBLE_COLOR    = ASSISTANT_BUBBLE_COLOR,
            IMPULSE_BUBBLE_COLOR      = IMPULSE_BUBBLE_COLOR,
            IMPULSE_BORDER_COLOR      = IMPULSE_BORDER_COLOR,
            STAGE_TEXT_COLOR          = STAGE_TEXT_COLOR,
            TABLE_BORDER_COLOR        = TABLE_BORDER_COLOR,
            LINK_COLOR                = LINK_COLOR,
            BLOCKQUOTE_BORDER_COLOR   = BLOCKQUOTE_BORDER_COLOR,
            BLOCKQUOTE_TEXT_COLOR     = BLOCKQUOTE_TEXT_COLOR,
        )
        self.webview.load_html(html_content, None)
        logger.info("ChatView: HTML-Template geladen")

    # ─────────────────────────────────────────────
    # Öffentliche API — alle Methoden erwarten den UI-Thread
    # ─────────────────────────────────────────────
    def add_user_message(self, text: str) -> None:
        """User-Eingabe als Bubble rechts anzeigen (Markdown gerendert)."""
        logger.debug(f"ChatView.add_user_message: {len(text)} Zeichen")
        rendered: str = self._markdown_to_html(text)
        self._render_message(rendered, "message-user")

    def add_assistant_message(self, text: str) -> None:
        """Nova-Antwort als Bubble links (Markdown → HTML)."""
        logger.debug(f"ChatView.add_assistant_message: {len(text)} Zeichen")
        rendered: str = self._markdown_to_html(text)
        self._render_message(rendered, "message-assistant")

    def add_impulse_message(self, text: str) -> None:
        """Pixie-Impuls als hervorgehobene Bubble links."""
        logger.debug(f"ChatView.add_impulse_message: {len(text)} Zeichen")
        rendered: str = self._markdown_to_html(text)
        self._render_message(rendered, "message-impulse")

    def show_stage(self, label: str, detail: str = "") -> None:
        """Pipeline-Stage (z.B. 'Perzeption — Wahrnehmung') anzeigen."""
        text: str = f"{label} · {detail}" if detail else label
        logger.debug(f"ChatView.show_stage: {text}")
        escaped: str = self._js_string(text)
        self._run_js(f"addStage({escaped});")

    def clear_stages(self) -> None:
        """Alle bestehenden Stage-Einträge entfernen."""
        logger.debug("ChatView.clear_stages")
        self._run_js("removeStages();")

    # ─────────────────────────────────────────────
    # Interne Hilfsfunktionen
    # ─────────────────────────────────────────────
    def _render_message(self, inner_html: str, css_class: str) -> None:
        """Erzeugt den addMessage-Call mit korrekt escaptem HTML-String."""
        js_html:  str = self._js_string(inner_html)
        js_class: str = self._js_string(css_class)
        self._run_js(f"addMessage({js_html}, {js_class});")

    @staticmethod
    def _markdown_to_html(text: str) -> str:
        """Konvertiert Markdown zu HTML für die Chat-Darstellung."""
        return markdown.markdown(
            text,
            extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
        )

    @staticmethod
    def _js_string(text: str) -> str:
        """Wandelt einen Python-String in ein JavaScript-String-Literal um.

        Escaped Backslashes, Anführungszeichen, Zeilenumbrüche und </script>-
        Sequenzen, damit der Browser kein vorzeitiges Tag-Ende sieht.
        """
        escaped: str = (
            text.replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\u2028", "\\u2028")
                .replace("\u2029", "\\u2029")
                .replace("</", "<\\/")
        )
        return f"'{escaped}'"

    def _run_js(self, script: str) -> None:
        """Einheitlicher Wrapper um WebView.evaluate_javascript().

        Die Signatur in WebKitGTK 6.0 ist:
            evaluate_javascript(script, length, world_name, source_uri,
                                cancellable, callback, user_data)
        Wir nutzen -1 für length (auto) und None für die restlichen Argumente.
        """
        logger.debug(f"ChatView._run_js ({len(script)} Zeichen)")
        self.webview.evaluate_javascript(
            script,
            -1,     # length: -1 = auto (bis Null-Terminator)
            None,   # world_name
            None,   # source_uri
            None,   # cancellable
            None,   # callback
            None,   # user_data
        )
