"""Emotions-Avatar: Logik ohne GTK.

Das Paket rechnet aus Sektor und Arousal ein Ziel des Gesichts (`expression`) und
lässt den sichtbaren Zustand diesem Ziel stetig folgen (`animator`). Es importiert
weder GTK noch Netzwerkbibliotheken und liest keine Uhr: Die Zeit kommt als
Parameter von dem, der zeichnet. Die Abhängigkeit läuft nur von `ui` nach `avatar`.
"""
