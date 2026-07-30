"""Tests: Die Abschluss-Routine raeumt nach einem Pixie-Lauf auf.

Ziel: Das heutige Verhalten von `abschluss` ist festgeschrieben, bevor die
Funktion zerlegt wird. Ein **Charakterisierungs-Netz** — es behauptet nicht,
dass alles richtig ist, sondern dass sich nichts aendert.

Warum diese Funktion zuerst: Sie ist die kleinste der vier verbliebenen
Zaehlregel-Treffer (43 Zeilen), aber die riskanteste je Zeile. Sie entscheidet,
ob ein Queue-Auftrag entfernt, wiedereingereiht oder verworfen wird, sie hat
fuenf Verschachtelungsebenen — und sie hatte **keinen Test**. Ein Grep nach dem
Namen fand null Treffer in `tests/`, was hier wenigstens ehrlich war.

Zeugen dieser Datei:
  * **Die Erwartungen stammen aus dem Docstring der Funktion** — "Pop bei
    Erfolg, Retry-Counter bei Fehler" fuer die Queue, "next_run aktualisieren
    (auch bei Fehler)" fuer die periodische Aufgabe — und aus der Zahl 3, die
    als Grenze im Rumpf steht.
  * **Geprueft wird, was an Redis geht**, nicht was die Funktion zurueckgibt:
    Sie gibt nichts zurueck, ihre ganze Wirkung sind die Aufrufe. Ein Test auf
    den Rueckgabewert wuerde nichts messen.
  * **Der stille Verlustpfad wird ausdruecklich gepinnt.** Bei
    `PIXIE_AKTIV=False` wird der Eintrag entfernt und **nicht** wieder
    eingereiht — der Auftrag ist dann weg. Der Test behauptet nicht, dass das
    richtig ist; er haelt fest, dass es so ist, damit eine Zerlegung es nicht
    versehentlich aendert und eine Reparatur es absichtlich tut.
  * Die Zeit ist festgenagelt, damit `next_run` eine pruefbare Zahl ist und
    nicht ein Fenster.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from services.pixie.dispatch import abschluss

JETZT: float = 1_000_000.0

QUEUE_KEY: str = "shadow_queue:meister"
SCHEDULE_KEY: str = "pixie:schedule:ziel_decay"


def _queue_kandidat(eintrag: dict | str) -> dict:
    """Baut einen Queue-Kandidaten mit dem gegebenen Rohsatz."""
    roh: str = eintrag if isinstance(eintrag, str) else json.dumps(eintrag)
    return {
        "quelle":       "queue",
        "queue_key":    QUEUE_KEY,
        "queue_raw":    roh,
        "schedule_key": "",
    }


def _periodisch_kandidat(schedule_key: str = SCHEDULE_KEY) -> dict:
    """Baut einen periodischen Kandidaten."""
    return {
        "quelle":       "periodisch",
        "queue_key":    "",
        "queue_raw":    "",
        "schedule_key": schedule_key,
    }


class AbschlussBasis(unittest.TestCase):
    """Gemeinsamer Aufbau: Redis und die Zeit sind gemockt."""

    def _fahren(
        self, kandidat: dict, erfolg: bool, *,
        pixie_aktiv: bool = True, hash_daten: dict | None = None,
    ) -> MagicMock:
        """Ruft `abschluss` und liefert den Redis-Mock zur Pruefung."""
        redis = MagicMock()
        redis.hgetall.return_value = {} if hash_daten is None else hash_daten
        with patch("services.pixie.dispatch.redis_client", redis), \
             patch("services.pixie.dispatch.PIXIE_AKTIV", pixie_aktiv), \
             patch("services.pixie.dispatch.time.time", return_value=JETZT):
            abschluss(kandidat, erfolg)
        return redis


class QueueErfolg(AbschlussBasis):
    """Bei Erfolg wird der Eintrag entfernt und nichts eingereiht."""

    def test_eintrag_wird_genau_einmal_entfernt(self) -> None:
        """`lrem` mit Anzahl 1 auf denselben Rohsatz."""
        kandidat = _queue_kandidat({"aufgabe": "vertiefen"})
        redis = self._fahren(kandidat, erfolg=True)
        redis.lrem.assert_called_once_with(QUEUE_KEY, 1, kandidat["queue_raw"])

    def test_nichts_wird_wieder_eingereiht(self) -> None:
        """Ein erfolgreicher Auftrag kommt nicht zurueck in die Queue."""
        redis = self._fahren(_queue_kandidat({"aufgabe": "vertiefen"}), erfolg=True)
        redis.rpush.assert_not_called()


class QueueFehlerRetry(AbschlussBasis):
    """Bei Fehler zaehlt der Retry-Counter, bis die Grenze von 3 greift."""

    def test_erster_fehlversuch_wird_wieder_eingereiht(self) -> None:
        """Entfernen und mit `_retries` = 1 zurueck in die Queue."""
        redis = self._fahren(_queue_kandidat({"aufgabe": "vertiefen"}), erfolg=False)
        redis.lrem.assert_called_once()
        redis.rpush.assert_called_once()
        key, roh = redis.rpush.call_args.args
        self.assertEqual(key, QUEUE_KEY)
        self.assertEqual(json.loads(roh)["_retries"], 1)

    def test_der_zaehler_zaehlt_weiter(self) -> None:
        """Ein bestehender Zaehler wird erhoeht, nicht zurueckgesetzt."""
        redis = self._fahren(
            _queue_kandidat({"aufgabe": "vertiefen", "_retries": 1}), erfolg=False,
        )
        self.assertEqual(json.loads(redis.rpush.call_args.args[1])["_retries"], 2)

    def test_die_aufgabe_bleibt_beim_wiedereinreihen_erhalten(self) -> None:
        """Nur `_retries` kommt hinzu, der uebrige Satz bleibt."""
        redis = self._fahren(
            _queue_kandidat({"aufgabe": "vertiefen", "prioritaet": 0.7}), erfolg=False,
        )
        satz = json.loads(redis.rpush.call_args.args[1])
        self.assertEqual(satz["aufgabe"], "vertiefen")
        self.assertEqual(satz["prioritaet"], 0.7)

    def test_beim_dritten_fehlversuch_wird_verworfen(self) -> None:
        """Bei `_retries` = 2 erreicht der naechste Versuch 3 — Ende.

        Entfernt, nicht wieder eingereiht, und die Warnung nennt die Aufgabe,
        damit im Log steht, was verloren ging.
        """
        with self.assertLogs("ki_server.pixie", "WARNING") as log:
            redis = self._fahren(
                _queue_kandidat({"aufgabe": "vertiefen", "_retries": 2}), erfolg=False,
            )
        redis.lrem.assert_called_once()
        redis.rpush.assert_not_called()
        self.assertIn("vertiefen", log.output[-1])
        self.assertIn("3 Fehlversuchen", log.output[-1])


class QueueFehlerPixieAus(AbschlussBasis):
    """Bei abgeschaltetem Pixie geht der Auftrag verloren.

    Kein Werturteil, ein Befund: `lrem` steht **vor** der Abfrage auf
    `PIXIE_AKTIV`, der Eintrag ist also entfernt, bevor entschieden wird, ob er
    zurueckkommt. Heute nicht akut, weil der Schalter im Betrieb auf True steht
    — aber wer ihn umlegt, verliert damit jeden fehlgeschlagenen Auftrag.
    """

    def test_eintrag_ist_entfernt_und_kommt_nicht_zurueck(self) -> None:
        """Entfernt, kein Push — der Auftrag existiert danach nicht mehr."""
        redis = self._fahren(
            _queue_kandidat({"aufgabe": "vertiefen"}), erfolg=False,
            pixie_aktiv=False,
        )
        redis.lrem.assert_called_once()
        redis.rpush.assert_not_called()


class QueueFehlerUnlesbar(AbschlussBasis):
    """Ein unlesbarer Rohsatz laesst den Eintrag stehen."""

    def test_kaputtes_json_ruehrt_die_queue_nicht_an(self) -> None:
        """Weder entfernt noch eingereiht — der Docstring sagt "stehen lassen".

        `json.loads` ist die erste Anweisung im `try`; scheitert sie, ist noch
        kein `lrem` gelaufen. Der Eintrag bleibt und wird beim naechsten
        Heartbeat wieder Kandidat.
        """
        redis = self._fahren(_queue_kandidat('{"aufgabe": '), erfolg=False)
        redis.lrem.assert_not_called()
        redis.rpush.assert_not_called()


class PeriodischeAufgabe(AbschlussBasis):
    """Bei periodischen Aufgaben wird `next_run` fortgeschrieben."""

    def test_next_run_ist_jetzt_plus_intervall(self) -> None:
        """Der neue Zeitpunkt ist die feste Zeit plus das Intervall."""
        redis = self._fahren(
            _periodisch_kandidat(), erfolg=True, hash_daten={"interval": "600"},
        )
        redis.hset.assert_called_once_with(
            SCHEDULE_KEY, "next_run", str(JETZT + 600),
        )

    def test_auch_bei_fehler_wird_fortgeschrieben(self) -> None:
        """Der Docstring sagt es zu: auch bei Fehler."""
        redis = self._fahren(
            _periodisch_kandidat(), erfolg=False, hash_daten={"interval": "600"},
        )
        redis.hset.assert_called_once()

    def test_fehlendes_intervall_nimmt_eine_stunde(self) -> None:
        """Ohne `interval` im Hash gilt 3600 Sekunden."""
        redis = self._fahren(
            _periodisch_kandidat(), erfolg=True, hash_daten={"etwas": "anderes"},
        )
        redis.hset.assert_called_once_with(
            SCHEDULE_KEY, "next_run", str(JETZT + 3600),
        )

    def test_byte_schluessel_werden_dekodiert(self) -> None:
        """Ein Hash mit Byte-Schluesseln wird gelesen wie einer mit Zeichenketten."""
        redis = self._fahren(
            _periodisch_kandidat(), erfolg=True,
            hash_daten={b"interval": b"120"},
        )
        redis.hset.assert_called_once_with(
            SCHEDULE_KEY, "next_run", str(JETZT + 120),
        )

    def test_leerer_hash_schreibt_nichts(self) -> None:
        """Gibt es den Zeitplan-Eintrag nicht, wird nichts gesetzt."""
        redis = self._fahren(_periodisch_kandidat(), erfolg=True, hash_daten={})
        redis.hset.assert_not_called()

    def test_ohne_schedule_key_passiert_nichts(self) -> None:
        """Ein leerer `schedule_key` faellt aus der Bedingung heraus.

        Weder gelesen noch geschrieben — und ohne Log-Zeile. Der Fund dazu
        steht in der Fundliste: Ein periodischer Kandidat ohne Zeitplan-Eintrag
        behaelt sein `next_run` und gewinnt den naechsten Heartbeat erneut.
        """
        redis = self._fahren(_periodisch_kandidat(""), erfolg=True)
        redis.hgetall.assert_not_called()
        redis.hset.assert_not_called()


class UnbekannteQuelle(AbschlussBasis):
    """Eine Quelle, die keine der beiden ist, laesst alles unberuehrt."""

    def test_nichts_wird_angefasst(self) -> None:
        """Kein Redis-Aufruf — stillschweigend, ohne Log-Zeile."""
        kandidat = {
            "quelle": "erfunden", "queue_key": QUEUE_KEY,
            "queue_raw": "{}", "schedule_key": SCHEDULE_KEY,
        }
        redis = self._fahren(kandidat, erfolg=True)
        redis.lrem.assert_not_called()
        redis.rpush.assert_not_called()
        redis.hset.assert_not_called()
        redis.hgetall.assert_not_called()


if __name__ == "__main__":
    unittest.main()
