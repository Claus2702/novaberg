"""
Shadow Agent — Novas Unterbewusstsein.
Plugin-basierter Background-Worker auf CPU.
"""

from services.shadow_agent.utils import (
    shadow_queue_push,
    shadow_stack_pop,
    shadow_stack_peek,
    stack_push,
    log_schreiben,
)
from services.shadow_agent.runner import schatten_arbeit_ausfuehren

# Auto-Discovery: Alle Task-Klassen aus tasks/ laden
_TASK_REGISTRY: dict = {}


def discover_tasks() -> dict:
    """Scannt tasks/ und registriert alle BaseTask-Subklassen."""
    import importlib
    import logging
    import pkgutil
    from services.shadow_agent import tasks as task_package
    from services.shadow_agent.base_task import BaseTask

    logger = logging.getLogger("ki_server.shadow")

    for importer, modname, ispkg in pkgutil.iter_modules(task_package.__path__):
        module = importlib.import_module(f"services.shadow_agent.tasks.{modname}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type)
                and issubclass(attr, BaseTask)
                and attr is not BaseTask
                and attr.TASK_NAME):
                _TASK_REGISTRY[attr.TASK_NAME] = attr()
                logger.info(f"Task registriert: '{attr.TASK_NAME}' ({attr.BESCHREIBUNG})")

    return _TASK_REGISTRY


def get_task_registry() -> dict:
    """Gibt die Task-Registry zurück."""
    return _TASK_REGISTRY
