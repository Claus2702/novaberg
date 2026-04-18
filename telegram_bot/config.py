import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

TELEGRAM_USER_MAP: dict[int, str] = {}

_raw_map = os.getenv("TELEGRAM_USER_MAP", "")
if _raw_map:
    for pair in _raw_map.split(","):
        parts = pair.strip().split(":")
        if len(parts) == 2:
            try:
                TELEGRAM_USER_MAP[int(parts[0].strip())] = parts[1].strip()
            except ValueError:
                pass

NOVA_API_URL = os.getenv("NOVA_API_URL", "http://server:8000")
NOVA_API_TIMEOUT = int(os.getenv("NOVA_API_TIMEOUT", "120"))
