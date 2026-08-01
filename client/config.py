"""
Zentrale Konfiguration für den Nova GTK4-Client.

Alle veränderlichen Parameter (Server-Adressen, Farben, Fenstergrößen,
Timeouts, Logging-Einstellungen) werden hier gebündelt, damit andere
Module ausschließlich aus dieser Datei importieren.
"""

from dataclasses import dataclass

# ─────────────────────────────────────────────
# Server-Verbindung
# ─────────────────────────────────────────────
SERVER_HOST = "localhost"
SERVER_PORT = 8000
SERVER_URL  = f"http://{SERVER_HOST}:{SERVER_PORT}"
WS_URL      = f"ws://{SERVER_HOST}:{SERVER_PORT}/ws"
SSE_URL     = f"{SERVER_URL}/chat/stream"
HEALTH_URL  = f"{SERVER_URL}/health"

# ─────────────────────────────────────────────
# Netzwerk-Timeouts (Sekunden)
# ─────────────────────────────────────────────
SSE_CONNECT_TIMEOUT: float       = 10.0   # requests-Connect-Timeout für SSE
SSE_READ_TIMEOUT                 = None   # None = kein Read-Timeout (Server entscheidet)
WS_RECONNECT_INTERVAL: float     = 5.0    # Wartezeit zwischen WS-Reconnect-Versuchen
SSE_STOP_WAIT_TIMEOUT: float     = 5.0    # Schlafzeit in der WS-Reconnect-Schleife (stopbar)
THREAD_SHUTDOWN_TIMEOUT: float   = 2.0    # Max. Wartezeit beim Join während Shutdown
PANEL_REQUEST_TIMEOUT: float     = 8.0    # Einheitlicher Timeout für Panel-Requests

# ─────────────────────────────────────────────
# Benutzer / Gesprächspaar
# ─────────────────────────────────────────────
DEFAULT_USER_ID: str   = "meister"
ASSISTANT_USER_ID: str = "nova"


@dataclass(frozen=True)
class GespraechsPerspektive:
    """Ein Eintrag im Perspektive-Selector.

    Jede Perspektive legt drei API-Parameter fest: welches Gespräch
    (``user_id`` + ``character_id``) geladen wird und aus wessen Sicht
    (``beobachter``) gefiltert wird.
    """

    label:        str   # Anzeige im Dropdown.
    user_id:      str
    character_id: str
    beobachter:   str   # "user" oder "assistant"


# Im Panel-Header wählbare Gesprächspaar-Perspektiven.
# Später dynamisch aus Config/DB befüllen (alle bekannten
# user_id/character_id-Paare jeweils zweimal — einmal pro Beobachter).
PERSPEKTIVEN: list[GespraechsPerspektive] = [
    GespraechsPerspektive(
        label        = "Meister — Gespräch mit Nova",
        user_id      = DEFAULT_USER_ID,
        character_id = ASSISTANT_USER_ID,
        beobachter   = "user",
    ),
    GespraechsPerspektive(
        label        = "Nova — Gespräch mit Meister",
        user_id      = DEFAULT_USER_ID,
        character_id = ASSISTANT_USER_ID,
        beobachter   = "assistant",
    ),
]

# ─────────────────────────────────────────────
# Chat-Darstellung (wird in das HTML-Template eingesetzt)
# ─────────────────────────────────────────────
MAX_MESSAGE_WIDTH_PERCENT = 80
USER_BUBBLE_COLOR         = "#2B5278"   # Blau, rechts (User)
ASSISTANT_BUBBLE_COLOR    = "#1A3A2A"   # Grün-dunkel, links (Nova)
IMPULSE_BUBBLE_COLOR      = "#2A3A1A"   # Grün-leicht, links (Pixie-Impulse)
IMPULSE_BORDER_COLOR      = "#4A7A3A"   # Akzent-Rand links an Impuls-Bubbles
UNZUGEORDNET_BORDER_COLOR = "#C46A2A"   # Rand an Antworten, die nicht zur letzten Frage gehören
BACKGROUND_COLOR          = "#1E1E1E"   # Dunkler Hintergrund
TEXT_COLOR                = "#E0E0E0"   # Heller Text
STAGE_TEXT_COLOR          = "#888"      # Pipeline-Stage (kursiv, zentriert)
TABLE_BORDER_COLOR        = "#444"      # Zellenrahmen in Markdown-Tabellen
LINK_COLOR                = "#6CA6E8"   # Anchor-Farbe in Chat-Bubbles
BLOCKQUOTE_BORDER_COLOR   = "#555"      # Linker Rand von >-Zitaten
BLOCKQUOTE_TEXT_COLOR     = "#AAA"      # Textfarbe in >-Zitaten
FONT_FAMILY               = "system-ui, sans-serif"
FONT_SIZE                 = "15px"

# ─────────────────────────────────────────────
# Hauptfenster
# ─────────────────────────────────────────────
WINDOW_TITLE          = "Nova"
WINDOW_DEFAULT_WIDTH  = 900
WINDOW_DEFAULT_HEIGHT = 700
WINDOW_MIN_WIDTH      = 400
WINDOW_MIN_HEIGHT     = 300

# Toolbar / Statusbar (GTK-CSS via main_window._apply_css)
TOOLBAR_BG_COLOR      = "#252525"
STATUSBAR_BG_COLOR    = "#181818"
STATUSBAR_TEXT_COLOR  = "#AAAAAA"

# ─────────────────────────────────────────────
# Radar-Chart — Cairo-Farben (RGBA-Tupel, je 0.0–1.0)
# ─────────────────────────────────────────────
RADAR_TITLE_COLOR:       tuple[float, float, float, float] = (0.6, 0.6, 0.6, 1.0)
RADAR_GRID_COLOR:        tuple[float, float, float, float] = (0.4, 0.4, 0.4, 0.3)
RADAR_DATA_FILL_COLOR:   tuple[float, float, float, float] = (0.3, 0.8, 0.3, 0.25)
RADAR_DATA_STROKE_COLOR: tuple[float, float, float, float] = (0.3, 0.8, 0.3, 0.8)
RADAR_DATA_DOT_COLOR:    tuple[float, float, float, float] = (0.3, 0.8, 0.3, 1.0)
RADAR_LABEL_COLOR:       tuple[float, float, float, float] = (0.7, 0.7, 0.7, 1.0)
# Der Punkt, der zeigt, wie weit das Ergebnis von der Nabe abliegt. Bewusst
# nicht das Grün der Speichenfläche: Er ist keine elfte Achse, sondern die
# aus allen Achsen gerechnete Bilanz.
RADAR_NABE_COLOR:        tuple[float, float, float, float] = (0.95, 0.65, 0.2, 1.0)

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL  = "DEBUG"
