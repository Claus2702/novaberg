"""Konfiguration des Matrix-Connectors — alles aus der Umgebung.

Kein Wert steht hier fest verdrahtet, der ein Geheimnis waere: Die beiden
Tokens kommen aus `matrix/config/as-tokens.env`, das neben dem Repositorium
liegt (Konzept §4).
"""

import os

# ── Der Homeserver ───────────────────────────
#: Basis-URL der Client-Server-API, aus Sicht des Behaelters.
MATRIX_HOMESERVER: str = os.getenv("MATRIX_HOMESERVER", "http://synapse:8008")

#: Der Servername — Teil jeder Kennung, nicht die Adresse. Beide fallen
#: auseinander, und das ist Absicht (Konzept §3.1).
MATRIX_SERVER_NAME: str = os.getenv("MATRIX_SERVER_NAME", "novaberg.de")

# ── Die Tokens des Application Service ───────
#: Womit der Connector sich beim Homeserver ausweist. Er steht in der
#: Registrierungsdatei und wird als Bearer gesendet — an derselben Stelle,
#: an der ein gewoehnlicher Client seinen Access-Token traegt.
MATRIX_AS_TOKEN: str = os.getenv("MATRIX_AS_TOKEN", "")

#: Womit der **Homeserver** sich beim Connector ausweist. Jede eingehende
#: Transaktion traegt ihn; eine ohne ihn ist keine vom Homeserver.
MATRIX_HS_TOKEN: str = os.getenv("MATRIX_HS_TOKEN", "")

# ── Die Zuordnung Mensch ↔ Kennung ───────────
#: Format `matrix_localpart:novaberg_user_id`, mehrere durch Komma getrennt.
#: Eine Kennung ohne Eintrag wird nicht bedient — dieselbe Weisse Liste wie
#: beim Telegram-Bot, und aus demselben Grund.
MATRIX_USER_MAP: dict[str, str] = {}
_roh: str = os.getenv("MATRIX_USER_MAP", "meister:meister")
for _paar in _roh.split(","):
    _teile = _paar.strip().split(":")
    if len(_teile) == 2 and _teile[0].strip() and _teile[1].strip():
        MATRIX_USER_MAP[_teile[0].strip()] = _teile[1].strip()

#: Die Kennung der Figur — sie sendet die Antworten.
MATRIX_CHARACTER: str = os.getenv("MATRIX_CHARACTER", "nova")

#: Wie die Figur im Client heisst. Ohne ihn zeigt ein Client den lokalen Teil
#: der Kennung — also die Kleinschreibung des Kontonamens.
MATRIX_CHARACTER_NAME: str = os.getenv("MATRIX_CHARACTER_NAME", "Nova")

#: Ihr Profilbild. Fehlt die Datei, bleibt das Profil ohne Bild — das ist ein
#: Zustand und kein Ausfall, und er wird einmal protokolliert.
MATRIX_CHARACTER_AVATAR: str = os.getenv(
    "MATRIX_CHARACTER_AVATAR", "/config/avatar-nova.png")

#: Der Novaberg-Charakter, dessen WebSocket abgehoert wird.
NOVA_CHARACTER_ID: str = os.getenv("NOVA_CHARACTER_ID", "nova")

# ── Novaberg ─────────────────────────────────
NOVA_API_URL: str = os.getenv("NOVA_API_URL", "http://server:8000")
NOVA_API_TIMEOUT: int = int(os.getenv("NOVA_API_TIMEOUT", "120"))

# ── Der eigene Dienst ────────────────────────
#: Der Port, auf dem der Homeserver seine Transaktionen abliefert. Er steht
#: in der `url` der Registrierungsdatei und muss dazu passen.
MATRIX_BOT_PORT: int = int(os.getenv("MATRIX_BOT_PORT", "8010"))

#: Wartezeit vor einem neuen Anlauf, wenn der WebSocket abreisst.
WS_RECONNECT_DELAY: float = float(os.getenv("WS_RECONNECT_DELAY", "5.0"))

#: Wo die Raum-Kennung liegt. Sie wird beim ersten Lauf ermittelt oder
#: angelegt und dann hier gehalten — ein Raum je Paar.
RAUM_DATEI: str = os.getenv("RAUM_DATEI", "/state/raeume.json")

#: Wo der Fingerabdruck des zuletzt gesetzten Profilbildes liegt.
#:
#: **Ohne ihn laedt jeder Start dasselbe Bild erneut hoch.** Der Medienspeicher
#: vergibt je Aufruf eine neue Adresse; nach dreissig Neustarts liegen dort
#: dreissig Kopien, und keine faellt auf.
PROFIL_DATEI: str = os.getenv("PROFIL_DATEI", "/state/profil.json")
