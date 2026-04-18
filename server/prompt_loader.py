"""
Prompt-Lade-System fuer LLM-Connector-Segregation.

Laedt statische Prompt-Bloecke aus Textdateien.
Default-Werte werden durch Connector-spezifische Overrides ergaenzt.
Einmal beim Start laden, danach im RAM.
"""

import os
import logging

logger = logging.getLogger("ki_server.prompts")


def prompt_laden(connector: str, prompt_dir: str = "") -> dict[str, str]:
    """
    Laedt alle Prompt-Bloecke fuer den aktiven Connector.

    1. Liest alle .txt aus prompts/default/
    2. Liest alle .txt aus prompts/{connector}/, ueberschreibt Defaults
    3. Gibt Dict zurueck: {"node.block": "text", ...}

    Args:
        connector: Name des Connectors (z.B. "gemma4", "mistral")
        prompt_dir: Pfad zum prompts/-Verzeichnis. Default: relativ zu dieser Datei.
    """
    if not prompt_dir:
        prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

    prompts: dict[str, str] = {}

    # 1. Default-Bloecke laden
    default_path: str = os.path.join(prompt_dir, "default")
    if not os.path.isdir(default_path):
        logger.error(f"Prompt-Verzeichnis nicht gefunden: {default_path}")
        return prompts

    for datei in sorted(os.listdir(default_path)):
        if datei.endswith(".txt"):
            key: str = datei[:-4]  # "router.rules"
            dateipfad: str = os.path.join(default_path, datei)
            with open(dateipfad, "r", encoding="utf-8") as f:
                prompts[key] = f.read().strip()

    default_count: int = len(prompts)
    logger.info(f"Prompts: {default_count} Default-Bloecke geladen")

    # 2. Connector-Override
    connector_path: str = os.path.join(prompt_dir, connector)
    override_count: int = 0
    if os.path.isdir(connector_path):
        for datei in sorted(os.listdir(connector_path)):
            if datei.endswith(".txt"):
                key = datei[:-4]
                dateipfad = os.path.join(connector_path, datei)
                with open(dateipfad, "r", encoding="utf-8") as f:
                    prompts[key] = f.read().strip()
                    override_count += 1

    if override_count > 0:
        logger.info(f"Prompts: {override_count} Override(s) fuer Connector '{connector}'")
    else:
        logger.info(f"Prompts: Keine Overrides fuer Connector '{connector}'")

    return prompts
