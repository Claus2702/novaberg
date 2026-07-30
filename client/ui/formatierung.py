"""
Gemeinsame Anzeigeformate für alle Panels.

Hier steht, wie ein Wert im Client aussieht — an **einer** Stelle. Vorher
trugen `lzg_panel.py` und `goals_panel.py` denselben Zeitformatierer
wortgleich zweimal, das Charakter-Panel einen dritten und die Profile
darunter gar keinen. Vier Darstellungen desselben Datums in einem Fenster
sind kein Geschmacksfehler: Wer zwei Panels nebeneinander liest, vergleicht
Zeitpunkte, und drei Schreibweisen kosten ihn jedes Mal einen Moment.

Sprach-Regeln: Code/Bezeichner englisch, UI-Texte deutsch.
"""

import datetime
import logging


logger = logging.getLogger(__name__)


# Deutsche Reihenfolge, Punkte statt Bindestriche, Minutengenauigkeit.
# Das ist der Unterschied zum rohen ISO-Wert, der ein 'T', Mikrosekunden und
# einen numerischen Zonenversatz mitfuehrt und dadurch als Block gelesen
# werden muss statt als Datum.
_ANZEIGE: str = "%d.%m.%Y %H:%M"


def zeit_kurz(iso: str) -> str:
    """Formatiert einen ISO-8601-Zeitpunkt als ``TT.MM.JJJJ HH:MM UTC``.

    Der Zonenkürzel steht ausdrücklich dabei. Alle Zeitstempel des Servers
    sind UTC, die Uhr des Betrachters ist es nicht — eine Anzeige ohne
    Kürzel liest sich als Ortszeit und geht in dieser Umgebung um zwei
    Stunden daneben. Der rohe ISO-Wert trug den Versatz mit; ihn beim
    Kürzen wegzulassen wäre kein Kürzen, sondern ein Verlust.

    Args:
        iso: Zeitpunkt in ISO-8601, wie ihn die Server-Endpunkte liefern.
            Ein leerer String heisst "kein Zeitpunkt" und bleibt leer.

    Returns:
        Der formatierte Zeitpunkt, oder bei unlesbarer Eingabe die Eingabe
        selbst — unverändert und damit erkennbar, statt still verschluckt.
    """
    # ── Eingabe ──────────────────────────────────────────────────────
    if not iso:
        return ""

    # ── Verarbeitung ─────────────────────────────────────────────────
    try:
        zeitpunkt: datetime.datetime = datetime.datetime.fromisoformat(iso)
    except (ValueError, TypeError):
        # Kein Absturz im Anzeigepfad, aber auch kein leerer String: Ein
        # unlesbarer Zeitstempel bleibt sichtbar und ist damit meldbar.
        logger.warning(f"zeit_kurz: nicht als ISO-8601 lesbar: {iso!r}")
        return iso

    # ── Ausgabe ──────────────────────────────────────────────────────
    if zeitpunkt.tzinfo is None:
        # Ohne Zonenangabe wird nichts behauptet, was nicht dasteht.
        return zeitpunkt.strftime(_ANZEIGE)

    return zeitpunkt.astimezone(datetime.timezone.utc).strftime(_ANZEIGE) + " UTC"
