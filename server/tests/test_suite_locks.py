"""Zeugen gegen den Haenger zwischen Suite und Serverstart.

Anlass, gemessen am 18.09.2026: Ein Reload von uvicorn startete die Migration
von `db/init.sql`, waehrend ein Zeuge eine Lesetransaktion auf `ziele` offen
hielt. Die Migration (`ALTER TABLE`) wartete auf den Zeugen, der naechste
Schreibzugriff des Zeugen auf die Migration — ein Deadlock ueber zwei
Prozesse, den Postgres erst sah, als die Transaktion von Hand beendet war.
**Der Serverstart hing 89 Minuten**, die Suite ebenso
(`ZEUGE-FLACKERT-OHNE-REPRODUKTION`).

Zeugen dieser Datei:
  * **Die Migration wartet begrenzt**: Sie verbindet mit `lock_timeout`, und
    eine abgelaufene Frist ist eine `error`-Zeile mit Grund, kein Absturz.
  * **Kein Zeuge haelt eine Verbindung ohne Autocommit** ueber die Dauer
    eines Tests — die Bauart, die die Sperre hielt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import pathlib
import re
import unittest
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.errors

import main

TESTS: pathlib.Path = pathlib.Path(__file__).resolve().parent


class MigrationWaitsBoundedTest(unittest.TestCase):
    """Die Migration beim Start haengt nicht an einer fremden Sperre."""

    def _migrate(self, cursor: MagicMock) -> tuple[MagicMock, list[str]]:
        conn = MagicMock()
        conn.cursor.return_value = cursor
        with patch.object(psycopg2, "connect", return_value=conn) as verbinden, \
                self.assertLogs("ki_server", level="INFO") as logs:
            main.schema_migrieren("postgresql://unbenutzt")
        return verbinden, logs.output

    def test_connects_with_lock_timeout(self) -> None:
        verbinden, _ = self._migrate(MagicMock())
        self.assertEqual(
            verbinden.call_args.kwargs["options"],
            f"-c lock_timeout={main.MIGRATION_SPERRFRIST_MS}",
        )

    def test_timeout_is_bounded_and_positive(self) -> None:
        self.assertGreater(main.MIGRATION_SPERRFRIST_MS, 0)
        self.assertLessEqual(main.MIGRATION_SPERRFRIST_MS, 60_000)

    def test_lock_timeout_is_an_error_with_reason(self) -> None:
        cursor = MagicMock()
        cursor.execute.side_effect = psycopg2.errors.LockNotAvailable("lock timeout")
        _, logs = self._migrate(cursor)
        fehler = [z for z in logs if z.startswith("ERROR")]
        self.assertEqual(len(fehler), 1, logs)
        self.assertIn("NICHT ausgeführt", fehler[0])
        self.assertIn(str(main.MIGRATION_SPERRFRIST_MS), fehler[0])

    def test_success_is_reported(self) -> None:
        _, logs = self._migrate(MagicMock())
        self.assertTrue(any("db/init.sql ausgeführt" in z for z in logs), logs)


class NoTestHoldsATransactionTest(unittest.TestCase):
    """Eine Verbindung, die ueber einen Test lebt, laeuft mit Autocommit."""

    def test_persistent_connections_use_autocommit(self) -> None:
        ohne = []
        for pfad in sorted(TESTS.glob("test_*.py")):
            zeilen = pfad.read_text(encoding="utf-8").split("\n")
            for nr, zeile in enumerate(zeilen):
                if not re.search(r"self\.conn\s*(?::[^=]*)?=\s*psycopg2\.connect\(", zeile):
                    continue
                folgend = "\n".join(zeilen[nr + 1:nr + 6])
                if "self.conn.autocommit = True" not in folgend:
                    ohne.append(f"{pfad.name}:{nr + 1}")
        self.assertEqual(ohne, [])


if __name__ == "__main__":
    unittest.main()
