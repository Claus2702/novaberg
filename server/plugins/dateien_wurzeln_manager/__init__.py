"""Aushang des Wurzeln-Dienstes fuer die Plugin-Discovery."""

from plugins.dateien_wurzeln_manager.manager import DateienWurzelnManager

# Der Import ist der Zweck dieser Datei: Die Discovery findet den Manager
# ueber `inspect.getmembers` auf dem Paketmodul. `__all__` sagt das aus,
# statt es als unbenutzten Import aussehen zu lassen.
__all__ = ["DateienWurzelnManager"]
