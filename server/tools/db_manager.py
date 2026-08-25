"""DBManager — PostgreSQL-Zugriff, threadsafe durch Connection-Pooling."""

import logging

import psycopg2
import psycopg2.extras
import psycopg2.pool

from config import POSTGRES_URL

logger = logging.getLogger(__name__)


class DBManager:
    """Kapselt PostgreSQL-Zugriff. Threadsafe durch Connection-Pooling.

    Jeder Aufruf holt sich eine eigene Connection aus dem Pool,
    arbeitet damit, gibt sie zurück. Kein geteilter Zustand im Manager.
    """

    def __init__(self, postgres_url: str) -> None:
        self._pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=postgres_url,
        )

    def select(self, query: str, params: tuple = ()) -> list[dict]:
        """SELECT-Abfrage, gibt Liste von Dicts zurück."""
        conn = self._pool.getconn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self._pool.putconn(conn)

    def select_one(self, query: str, params: tuple = ()) -> dict | None:
        """SELECT-Abfrage, gibt ein Dict oder None zurück."""
        ergebnisse = self.select(query, params)
        return ergebnisse[0] if ergebnisse else None

    def execute(self, query: str, params: tuple = ()) -> int:
        """INSERT/UPDATE/DELETE, gibt affected rows zurück."""
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def execute_returning(self, query: str, params: tuple = ()) -> dict | None:
        """INSERT ... RETURNING, gibt eingefügten Datensatz zurück."""
        conn = self._pool.getconn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                conn.commit()
                result = cur.fetchone()
                return dict(result) if result else None
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def execute_script(self, sql: str) -> None:
        """Führt ein SQL-Script aus (z.B. init.sql). Für Schema-Setup."""
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)


# Modul-Level-Instanz — Pythons natürliches Singleton-Pattern
db_manager = DBManager(postgres_url=POSTGRES_URL)
