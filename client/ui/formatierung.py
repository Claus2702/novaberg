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


def kosten_zeile(
    turn:  float | None,
    heute: float | None,
    monat: float | None,
) -> str:
    """Baut die Kostenzeile der Statusleiste — drei Posten, eine Genauigkeit.

    **Alle drei mit vier Nachkommastellen.** Der erste Betriebsblick am
    06.09.2026 zeigte `Heute: $0.009 · Monat: $0.01` — **derselbe Wert**,
    $0,013799, einmal auf drei und einmal auf zwei Stellen gerundet.
    Solange der Monat jung ist, sind Tag und Monat gleich; verschiedene
    Stellenzahlen machen daraus zwei Zahlen, die man gegeneinander liest.
    Vier Stellen, weil ein ganzer Turn bei $0,0016 bis $0,0032 liegt und
    bei zweien verschwaende.

    **Ein Strich ist keine Null.** `None` heisst *nicht ermittelt*; stuende
    dort `$0.0000`, saehe ein ausgefallener Zaehler aus wie ein kostenloser
    Betrieb.

    Vorbedingung: keine — jeder Posten darf `None` sein.
    Nachbedingung: Eine Zeile mit drei benannten Posten, nie leer.
    Fehlerfaelle: keine.

    Args:
        turn: Kosten des Turns in USD.
        heute: Kosten des laufenden Tages (UTC), Hintergrund eingerechnet.
        monat: Kosten des laufenden Kalendermonats.

    Returns:
        Zum Beispiel `Turn: $0.0032 · Heute: $0.0222 · Monat: $0.0222`.
    """
    # ── Verarbeitung ────────────────────────────
    def _betrag(wert: float | None) -> str:
        return "—" if wert is None else f"${wert:.4f}"

    zeile: str = (
        f"Turn: {_betrag(turn)} · "
        f"Heute: {_betrag(heute)} · "
        f"Monat: {_betrag(monat)}"
    )

    # ── Ausgabe-Verifikation ────────────────────
    if zeile.count("·") != 2:
        logger.error(f"kosten_zeile: {zeile!r} traegt nicht drei Posten")
    return zeile
