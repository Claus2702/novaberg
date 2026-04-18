"""
ui — PySide6-Oberflaeche des KI-Assistenten.

Enthaelt alle Panel-Widgets, das Hauptfenster und die Statusleiste.
Jedes Panel kommuniziert eigenstaendig mit dem FastAPI-Server.
Icons werden zentral ueber das icons-Modul (qtawesome) bereitgestellt.

Module:
    icons             Zentrales Icon-Mapping (qtawesome → Token-System)
    hauptfenster      Hauptfenster mit Sidebar-Navigation und Panel-Wechsel
    chat_panel        Chat mit SSE-Stream und WebSocket-Impulsen
    status_bar        Permanente Statusleiste mit Health-Polling
    fakten_panel      Entitaeten und Relationen (Knowledge Graph)
    gedaechtnis_panel KZG, LZG, Charakter-Hash, Session-Kontext
    system_panel      Health-Check-Uebersicht aller Dienste
    schatten_panel    Platzhalter: Schatten-Agent-Aktivitaeten
    timeline_panel    Platzhalter: Terminuebersicht
"""
