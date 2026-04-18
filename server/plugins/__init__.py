"""
Plugin Auto-Discovery — Scannt plugins/ nach Unterordnern mit BaseManager-Subklassen.

Jeder Unterordner mit __init__.py wird importiert.
Klassen die BaseManager erben werden automatisch registriert.
"""

import importlib
import inspect
import logging
from pathlib import Path

from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins")

_registry: dict[str, BaseManager] = {}


def discover_managers() -> dict[str, BaseManager]:
    """
    Scannt plugins/ nach Unterordnern mit BaseManager-Subklassen.
    Instanziiert und registriert sie nach 'ziel'.
    """

    _registry.clear()

    package_path: Path = Path(__file__).parent

    for item in sorted(package_path.iterdir()):
        # Nur Unterordner mit __init__.py
        if not item.is_dir():
            continue
        if item.name.startswith("_"):
            continue
        if not (item / "__init__.py").exists():
            continue

        try:
            module = importlib.import_module(f"plugins.{item.name}")

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseManager) and obj is not BaseManager:
                    instance: BaseManager = obj()
                    _registry[instance.ziel] = instance
                    logger.info(f"Plugin registriert: '{instance.ziel}' ({item.name})")

        except Exception as fehler:
            logger.error(f"Plugin '{item.name}' konnte nicht geladen werden: {fehler}")

    logger.info(f"Plugin-Discovery abgeschlossen: {len(_registry)} Manager registriert")
    return _registry


def get_registry() -> dict[str, BaseManager]:
    """Gibt die aktuelle Registry zurück. Führt Discovery aus falls leer."""
    if not _registry:
        discover_managers()
    return _registry


def get_combined_router_prompt() -> str:
    """Sammelt alle router_prompt-Erweiterungen der registrierten Manager."""
    parts: list[str] = []
    for manager in _registry.values():
        prompt: str = manager.router_prompt
        if prompt:
            parts.append(prompt.strip())
    return "\n\n".join(parts)


def get_combined_salienz_prompt() -> str:
    """Sammelt alle salienz_prompt-Erweiterungen der registrierten Manager."""
    parts: list[str] = []
    for manager in _registry.values():
        prompt: str = manager.salienz_prompt
        if prompt:
            parts.append(prompt.strip())
    return "\n\n".join(parts)
