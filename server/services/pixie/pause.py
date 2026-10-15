"""Pausenschalter des Hintergrundlaufs — setzen, aufheben, laut melden.

**Ein vergessener Schalter soll im Log schreien, nicht schweigen.** Drei
Redis-Schluessel halten den Hintergrund an (`PIXIE_PAUSE_SCHLUESSEL`,
`PIXIE_AGENTEN_PAUSE_SCHLUESSEL`, `PIXIE_DELIVERY_PAUSE_SCHLUESSEL`); die Leser
fragen nur `exists`. Gemessen: Ein Schalter stand zehn Tage, und jeder Zyklus
verwarf sich mit einer `debug`-Zeile — im Log war nichts davon zu sehen.

**Der Zeitpunkt liegt in einem Nebenschluessel** (`<schluessel>:seit`), nicht im
Wert des Schalters: Die Leser bleiben unveraendert gueltig, und ein Schalter
ohne Nebenschluessel (Altbestand) wird als *seit unbekannt* gemeldet, nie als
*jetzt*.

**Die Drossel liegt in Redis** (`<schluessel>:warnung` mit Ablaufzeit), nicht im
Prozess: Der Dienst kann neu starten, und beide Spuren des Schedulers sowie die
Zustellschleife melden denselben Schalter — ein gemeinsamer Schluessel gibt
je Schalter und Intervall genau eine Zeile.
"""

import logging
from datetime import UTC, datetime

import redis

from config import (
    PIXIE_AGENTEN_PAUSE_SCHLUESSEL,
    PIXIE_DELIVERY_PAUSE_SCHLUESSEL,
    PIXIE_PAUSE_SCHLUESSEL,
    PIXIE_PAUSE_WARNUNG_SEKUNDEN,
)

logger = logging.getLogger("ki_server.pixie")

SINCE_SUFFIX: str = ":seit"
WARNING_SUFFIX: str = ":warnung"

# Meldungen der Ausnahme als Konstanten: Die Ausnahme bekommt den Grund als
# Argument, kein Textliteral steht am `raise`.
_ERR_UNKNOWN_KEY: str = "Kein Pausenschluessel"
_ERR_UNKNOWN_KEYS: str = "Keine Pausenschluessel"
_ERR_NOT_SET: str = "Pausenschalter steht nach dem Setzen nicht"
_ERR_STILL_SET: str = "Pausenschalter steht nach dem Aufheben noch"

# Was der jeweilige Schalter anhaelt — steht in der Zeile, damit der Leser nicht
# im Code nachsehen muss, welche Haelfte still ist.
_EFFECT: dict[str, str] = {
    PIXIE_PAUSE_SCHLUESSEL: "Agenten und Zustellung",
    PIXIE_AGENTEN_PAUSE_SCHLUESSEL: "Agenten",
    PIXIE_DELIVERY_PAUSE_SCHLUESSEL: "Zustellung",
}


class PauseError(ValueError):
    """Ein Pausenschluessel ist unbekannt oder ein Schalter steht nicht wie verlangt."""

    def __init__(self, reason: str, value: object) -> None:
        """Baut die Meldung aus dem Befund und dem betroffenen Wert."""
        super().__init__(f"{reason}: {value!r}")


def set_pause(client: redis.Redis, key: str, now: datetime | None = None) -> None:
    """Setzt einen Pausenschalter und merkt sich, seit wann er steht.

    Vorbedingung: `key` ist einer der drei Pausenschluessel.
    Nachbedingung: Der Schalter steht mit Wert `"1"`. War er neu, steht auch
        `<key>:seit` mit dem UTC-Zeitpunkt (ISO 8601). **Ein schon
        stehender Schalter behaelt seinen Zeitpunkt — oder dessen Fehlen**: Ein
        zweites Setzen aendert den Zustand nicht, und ein Altbestand ohne
        Zeitpunkt wird dadurch nicht zu *jetzt*.
    Fehlerfaelle: unbekannter Schluessel oder Schalter steht nicht ->
        `PauseError`; ein Redis-Ausfall schlaegt durch.
    """
    # ── Eingabe-Validierung ──
    if key not in _EFFECT:
        raise PauseError(_ERR_UNKNOWN_KEY, key)

    # ── Verarbeitung ──
    moment: datetime = now if now is not None else datetime.now(UTC)
    was_set: bool = bool(client.exists(key))
    client.set(key, "1")
    if not was_set:
        client.set(key + SINCE_SUFFIX, moment.isoformat())

    # ── Ausgabe-Verifikation ──
    if not client.exists(key):
        raise PauseError(_ERR_NOT_SET, key)


def clear_pause(client: redis.Redis, key: str) -> None:
    """Hebt einen Pausenschalter auf und raeumt Zeitpunkt und Drossel mit ab.

    Vorbedingung: `key` ist einer der drei Pausenschluessel; ein nicht
        gesetzter Schalter ist kein Fehler.
    Nachbedingung: Weder der Schalter noch `:seit` noch `:warnung` stehen.
        Der naechste Schalter beginnt mit frischem Zeitpunkt und frischer
        Drossel.
    Fehlerfaelle: unbekannter Schluessel oder Schalter steht noch ->
        `PauseError`.
    """
    # ── Eingabe-Validierung ──
    if key not in _EFFECT:
        raise PauseError(_ERR_UNKNOWN_KEY, key)

    # ── Verarbeitung ──
    client.delete(key)
    client.delete(key + SINCE_SUFFIX)
    client.delete(key + WARNING_SUFFIX)

    # ── Ausgabe-Verifikation ──
    if client.exists(key):
        raise PauseError(_ERR_STILL_SET, key)


def _since_text(client: redis.Redis, key: str) -> str:
    """Der Zeitpunkt als Text fuer die Zeile — oder *unbekannt*, nie *jetzt*.

    Vorbedingung: der Schalter steht.
    Nachbedingung: ein ISO-Zeitpunkt, `unbekannt` (kein Nebenschluessel) oder
        `unbekannt (unlesbar: ...)` bei einem Wert, der kein Zeitpunkt ist.
    Fehlerfaelle: keine; ein unlesbarer Wert wird in der Zeile benannt.
    """
    # ── Eingabe-Validierung ──
    raw = client.get(key + SINCE_SUFFIX)
    if raw is None:
        return "unbekannt"

    # ── Verarbeitung ──
    try:
        datetime.fromisoformat(str(raw))
    except ValueError:
        return f"unbekannt (unlesbar: {raw!r})"

    # ── Ausgabe-Verifikation ──
    return str(raw)


def check_pauses(client: redis.Redis, keys: list[str] | tuple[str, ...]) -> bool:
    """Sagt, ob einer der Schalter steht, und meldet jeden stehenden gedrosselt.

    Vorbedingung: `keys` enthaelt nur Pausenschluessel.
    Nachbedingung: Rueckgabe `True`, wenn mindestens einer steht. **Alle**
        Schluessel werden gefragt (kein Kurzschluss), damit auch ein zweiter
        stehender Schalter gemeldet wird. Je stehendem Schalter hoechstens eine
        `warning` je `PIXIE_PAUSE_WARNUNG_SEKUNDEN`, mit Schalter, Wirkung und
        Zeitpunkt.
    Fehlerfaelle: unbekannter Schluessel -> `PauseError`; ein Redis-Ausfall
        schlaegt durch.
    """
    # ── Eingabe-Validierung ──
    unknown: list[str] = [k for k in keys if k not in _EFFECT]
    if unknown:
        raise PauseError(_ERR_UNKNOWN_KEYS, unknown)

    # ── Verarbeitung ──
    stands: bool = False
    for entry in keys:
        if not client.exists(entry):
            continue
        stands = True
        # `nx`: nur der erste Melder im Intervall bekommt die Drossel.
        if client.set(entry + WARNING_SUFFIX, "1", nx=True, ex=PIXIE_PAUSE_WARNUNG_SEKUNDEN):
            logger.warning(
                f"Pixie: Pausenschalter {entry} steht seit "
                f"{_since_text(client, entry)} — {_EFFECT[entry]} angehalten"
            )

    # Die Rueckgabe ist die Verarbeitung selbst; es gibt nichts, was erst hier zu pruefen waere.
    return stands
