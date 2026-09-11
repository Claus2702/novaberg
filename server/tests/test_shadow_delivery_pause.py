"""Tests: Die Pixie-Pause haelt auch die Zustellung an.

**Den Scheduler anzuhalten ist die Haelfte, die man nicht braucht.** Er erzeugt
dann keine neuen Auftraege mehr — aber was fertig auf dem Stapel liegt, wurde
bis zum 10.09.2026 weiter zugestellt, mit voller Turnlast und mitten in einem
laufenden Gespraech.

`[gemessen 10.09.2026]` Waehrend einer Messreihe mit bestaetigtem Status
`{"paused": true}` liefen **fuenf Zustellungen mit `durchgelassen: true`** und
**ein vollstaendiger Fremdturn** mitten in der Reihe; sein Reiz war ein
Rechercheergebnis, das im Feld fuer die Nutzeraeusserung landete. Damit war
weder die Messreihe hintergrundfrei — `F-MESS-2` verlangt genau das — noch der
Betrieb vor einem Impuls geschuetzt, der sich zwischen zwei Nutzeraeusserungen
schiebt.

Zeugen dieser Datei:
  * **Der Anschlag wird im echten Pfad belegt**, nicht an der Bedingung: Die
    Schleife laeuft wirklich, und geprueft wird, dass sie den Stapel gar nicht
    erst ansieht. Ein Zeuge auf `redis_client.exists(...)` bliebe gruen, wenn
    der Riegel an der falschen Stelle staende.
  * **Das Fehlen bekommt einen positiven Zwilling:** Dass die Schleife pausiert
    nichts tut, ist erst eine Aussage, wenn sie ohne Pause etwas tut.
  * **Der Schluessel ist derselbe wie beim Scheduler.** Ein zweiter Schalter
    waere eine zweite Wahrheit; der Zeuge haelt die Konstante fest.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from config import (
    PIXIE_AGENTEN_PAUSE_SCHLUESSEL,
    PIXIE_DELIVERY_PAUSE_SCHLUESSEL,
    PIXIE_PAUSE_SCHLUESSEL,
)
from services import shadow_delivery


class _Redis:
    """Ein Redis, das mitschreibt, wonach die Schleife fragt."""

    def __init__(self, pausiert: bool) -> None:
        self.pausiert = pausiert
        self.gefragt: list[str] = []
        # Weitere gesetzte Schluessel — fuer die Teilschalter.
        self.zusaetzlich: set[str] = set()

    def exists(self, key: str) -> int:
        self.gefragt.append(key)
        if key in self.zusaetzlich:
            return 1
        return 1 if (self.pausiert and key == PIXIE_PAUSE_SCHLUESSEL) else 0

    def llen(self, key: str) -> int:
        self.gefragt.append(key)
        return 3          # der Stapel ist nicht leer

    def get(self, key: str) -> str | None:
        self.gefragt.append(key)
        return None

    def delete(self, key: str) -> None:
        self.gefragt.append(key)

    def lrange(self, key: str, start: int, ende: int) -> list:
        """Ein leerer Stapel — der Zwilling soll lesen, nicht zustellen."""
        self.gefragt.append(key)
        return []


def _einen_zyklus(pausiert: bool) -> _Redis:
    """Laesst die echte Schleife genau einen Durchgang laufen."""
    return _zyklus_mit(_Redis(pausiert))


def _zyklus_mit(redis: "_Redis") -> "_Redis":
    """Derselbe Durchgang, aber mit einem vorbereiteten Redis."""
    schalter = MagicMock()
    # Nach dem ersten Durchgang ist Schluss: erst False (Schleife laeuft),
    # dann True (Schleife bricht ab).
    schalter.is_set.side_effect = [False, True, True, True]

    with patch.object(shadow_delivery, "PRÜF_INTERVALL", 0.0), \
         patch.object(shadow_delivery, "shutdown_event", schalter):
        asyncio.run(shadow_delivery.shadow_delivery_loop(
            redis_client=redis,
            websocket_map={"meister": object()},
            graph_run_lock=None,
        ))
    return redis


class ZweiHaelftenZweiSchalter(unittest.TestCase):
    """Agenten und Zustellung lassen sich getrennt anhalten.

    **Vorgabe des Eigentuemers am 11.09.2026.** Der Vollschalter reicht fuer
    eine Messreihe, die keinen Hintergrund sehen soll — aber nicht fuer einen
    Test der Zustellung selbst: Dort soll der Stapel abgearbeitet werden,
    ohne dass frische Funde dazukommen. Umgekehrt will eine Messung am
    Hintergrund die Agenten laufen lassen, ohne dass ihre Ergebnisse mitten
    in die Reihe fallen.

    **Ein Teilschalter wirkt wie der Vollschalter fuer seine Haelfte**, und
    der Vollschalter bleibt, was er war.
    """

    def test_der_teilschalter_haelt_nur_die_zustellung_an(self) -> None:
        redis = _Redis(pausiert=False)
        redis.zusaetzlich.add(PIXIE_DELIVERY_PAUSE_SCHLUESSEL)
        _zyklus_mit(redis)

        self.assertFalse(
            [k for k in redis.gefragt if k.startswith("shadow_stack:")],
            f"Der Stapel wurde trotz Delivery-Pause gelesen: {redis.gefragt}",
        )

    def test_der_agenten_schalter_haelt_die_zustellung_nicht_an(self) -> None:
        """Der Zwilling — sonst waere die Trennung keine."""
        redis = _Redis(pausiert=False)
        redis.zusaetzlich.add("pixie:agenten_paused")
        _zyklus_mit(redis)

        self.assertTrue(
            [k for k in redis.gefragt if k.startswith("shadow_stack:")],
            "Der Agenten-Schalter hat die Zustellung mit angehalten",
        )

    def test_beide_schluessel_werden_gefragt(self) -> None:
        redis = _Redis(pausiert=False)
        _zyklus_mit(redis)

        self.assertIn(PIXIE_PAUSE_SCHLUESSEL, redis.gefragt)
        self.assertIn(PIXIE_DELIVERY_PAUSE_SCHLUESSEL, redis.gefragt)


class PausiertIstNichtStill(unittest.TestCase):
    """Die Pause verhindert den naechsten Zyklus, sie bricht keinen ab.

    **Und das ist richtig so** — ein Abbruch mitten im Lauf verloere die
    Arbeit des Agenten. Die Folge muss aber sichtbar sein: `[gemessen
    11.09.2026]` Eine Messreihe setzte die Agenten-Pause um 09:53:40; ein
    Recherche-Agent lief bis **10:03:41** weiter — zehn Minuten volle
    Modellast, waehrend der Status `agenten_pausiert: true` meldete. Wer auf
    diese Auskunft hin misst, misst den Hintergrund mit und weiss es nicht.

    Der Status traegt seither beides: was **pausiert** ist und was **laeuft**.
    `bereit_fuer_messung` ist die Verknuepfung, damit sie nicht jeder
    Aufrufer selbst zieht — und einer vergisst.
    """

    def test_pausiert_und_laufend_ist_nicht_bereit(self) -> None:
        zustand: dict = _status_mit(
            pausiert={PIXIE_AGENTEN_PAUSE_SCHLUESSEL}, laufend={"llm"})

        self.assertTrue(zustand["agenten_pausiert"])
        self.assertEqual(["llm"], zustand["agenten_laufend"])
        self.assertFalse(
            zustand["bereit_fuer_messung"],
            "Pausiert und laufend zugleich wurde als messbereit gemeldet",
        )

    def test_pausiert_und_still_ist_bereit(self) -> None:
        zustand: dict = _status_mit(
            pausiert={PIXIE_AGENTEN_PAUSE_SCHLUESSEL}, laufend=set())

        self.assertTrue(zustand["bereit_fuer_messung"])

    def test_still_ohne_pause_ist_nicht_bereit(self) -> None:
        """Der zweite Zwilling: Stille allein genuegt nicht — der naechste
        Heartbeat faellt in Sekunden.
        """
        zustand: dict = _status_mit(pausiert=set(), laufend=set())

        self.assertFalse(zustand["bereit_fuer_messung"])


def _status_mit(pausiert: set, laufend: set) -> dict:
    """Ruft den echten Status-Endpunkt gegen ein vorbereitetes Redis."""
    from unittest.mock import patch

    from api import admin

    class _StatusRedis:
        def exists(self, key: str) -> int:
            if key in pausiert:
                return 1
            return 1 if key.replace("pixie:running:", "") in laufend \
                and key.startswith("pixie:running:") else 0

    with patch.object(admin, "redis_client", _StatusRedis()):
        return admin.pixie_status()


class DiePauseHaeltDieZustellungAn(unittest.TestCase):
    """Pausiert verwirft die Schleife ihren Zyklus, bevor sie den Stapel ansieht."""

    def test_pausiert_wird_der_stapel_nicht_gelesen(self) -> None:
        redis = _einen_zyklus(pausiert=True)

        self.assertIn(PIXIE_PAUSE_SCHLUESSEL, redis.gefragt)
        self.assertFalse(
            [k for k in redis.gefragt if k.startswith("shadow_stack:")],
            f"Der Stapel wurde trotz Pause gelesen: {redis.gefragt}",
        )

    def test_ohne_pause_sieht_die_schleife_den_stapel_an(self) -> None:
        """Der Zwilling — sonst waere auch eine kaputte Schleife gruen."""
        redis = _einen_zyklus(pausiert=False)

        self.assertTrue(
            [k for k in redis.gefragt if k.startswith("shadow_stack:")],
            f"Ohne Pause wurde der Stapel nicht gelesen: {redis.gefragt}",
        )

    def test_die_pause_wird_vor_dem_burst_limit_geprueft(self) -> None:
        """Die Reihenfolge ist die Aussage: erst die Pause, dann alles andere.

        Stuende der Riegel hinter den Pruefungen je Nutzer, haette jede von
        ihnen schon Redis befragt — und bei mehreren Nutzern liefe die
        Schleife pro Nutzer ein Stueck weit.
        """
        redis = _einen_zyklus(pausiert=True)

        self.assertEqual(
            redis.gefragt[0], PIXIE_PAUSE_SCHLUESSEL,
            f"Erste Redis-Frage war {redis.gefragt[0]!r}, nicht die Pause",
        )


if __name__ == "__main__":
    unittest.main()
