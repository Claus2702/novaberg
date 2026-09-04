"""Zeuge fuer die abstrakte Schicht, Scheibe 1: die Qualitaets-Knoten.

Ziel: Ein LZG-Knoten, der oft genug wiedergekehrt ist, traegt ein Profil auf
den sechs Qualitaetsdimensionen aus `novaberg-thinking-faszination_k.md` §6.1 —
und die Kante dorthin ist **vorzeichenlos**, anders als die Wert-Kante der
Haltung (§4.4).

**Diese Datei ist der Zuender**: Sie ist eine Python-Datei und loest
denselben Neustart aus wie jede andere. Sie wird vor dem Schema-Edit angelegt,
damit die rote Phase nicht verloren geht — ein Test, den man nie hat scheitern
sehen, ist eine Behauptung ueber sich selbst.

Sie importiert deshalb **nichts aus dem Bauteil**, nur die Verbindung: Ein
ImportError waere kein roter Test, sondern ein kaputter.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

import psycopg2

from config import POSTGRES_URL

# Der geschlossene Satz aus Konzept §6.1. Er steht hier ausgeschrieben und
# nicht als Import, aus dem Grund im Modul-Docstring — und weil ein Zeuge, der
# seine Erwartung aus dem Pruefling bezieht, jede Umbenennung mitmacht.
ERWARTETE_QUALITAETEN: set[str] = {
    "komplexitaet",
    "ungewissheit",
    "konflikt",
    "weite",
    "schemasprengung",
    "bedrohungsrelevanz",
}


def _spalten(tabelle: str) -> set[str]:
    """Die Spaltennamen einer Tabelle, leer wenn es sie nicht gibt."""
    with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s", (tabelle,),
        )
        return {zeile[0] for zeile in cur.fetchall()}


class DieAbstraktenKnotenStehenTest(unittest.TestCase):
    """Der Speicher der geschlossenen Saetze — Qualitaeten und Werte."""

    ERWARTET: set[str] = {
        "id", "art", "name", "beschreibung", "herkunft", "erstellt_am",
    }

    def test_abstrakt_knoten_traegt_alle_felder(self) -> None:
        """Ohne `art` sickert die Valenz von der Werte- auf die Qualitaetsseite.

        Konzept §4.4: Die Wert-Kante ist vorzeichenbehaftet, die
        Qualitaets-Kante nicht. Ohne Typ-Diskriminator waere der Fehler fest
        im Schema verbaut — Kriegsgeschichte truege weniger Faszination als
        Gartenkraeuter.
        """
        vorhanden: set[str] = _spalten("abstrakt_knoten")
        self.assertTrue(vorhanden, "Tabelle `abstrakt_knoten` existiert nicht")
        fehlend: set[str] = self.ERWARTET - vorhanden
        self.assertFalse(
            fehlend, f"Felder fehlen in `abstrakt_knoten`: {sorted(fehlend)}",
        )

    def test_die_sechs_qualitaeten_sind_gesetzt(self) -> None:
        """Das Vokabular ist gesetzt, nicht geerntet (Konzept §5).

        Drei Ernteversuche sind am 30.08.2026 gemessen gescheitert; der Satz
        kommt aus der Literatur und steht deshalb im Schema, nicht im Bestand.
        """
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM abstrakt_knoten WHERE art = 'qualitaet'"
            )
            gefunden: set[str] = {zeile[0] for zeile in cur.fetchall()}
        self.assertEqual(
            ERWARTETE_QUALITAETEN, gefunden,
            f"Der Satz der Qualitaeten weicht ab — fehlend "
            f"{sorted(ERWARTETE_QUALITAETEN - gefunden)}, "
            f"unerwartet {sorted(gefunden - ERWARTETE_QUALITAETEN)}",
        )

    def test_die_art_ist_auf_den_kanon_beschraenkt(self) -> None:
        """Ein dritter Typ waere ein stiller Fehler, kein neuer Fall.

        Die Pruefung stellt den Verstoss her, statt den Normalfall zu
        beobachten: Ein `CHECK`, den nie jemand gerissen hat, ist eine
        Behauptung.
        """
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            with self.assertRaises(psycopg2.errors.CheckViolation):
                cur.execute(
                    "INSERT INTO abstrakt_knoten (art, name) "
                    "VALUES ('etwas_drittes', 'zeuge')"
                )
            conn.rollback()


class DieQualitaetsKanteStehtTest(unittest.TestCase):
    """Die vorzeichenlose Kante Traeger → Qualitaet (Konzept §4.4)."""

    ERWARTET: set[str] = {
        "id", "knoten_id", "qualitaet_id", "auspraegung", "quelle",
        "haeufigkeit", "erstellt_am", "verstaerkt_am",
    }

    def test_traeger_qualitaet_traegt_alle_felder(self) -> None:
        """Ohne `quelle` ist eine Auspraegung nicht nachrechenbar."""
        vorhanden: set[str] = _spalten("traeger_qualitaet")
        self.assertTrue(vorhanden, "Tabelle `traeger_qualitaet` existiert nicht")
        fehlend: set[str] = self.ERWARTET - vorhanden
        self.assertFalse(
            fehlend, f"Felder fehlen in `traeger_qualitaet`: {sorted(fehlend)}",
        )

    def test_die_auspraegung_ist_vorzeichenlos(self) -> None:
        """0,8 — nicht »gut 0,8«. Der Unterschied ist der ganze Punkt.

        Eine negative Auspraegung waere eine Wert-Aussage an einer
        Qualitaets-Kante. Das Schema muss sie ablehnen, nicht der Aufrufer:
        `lzg_knoten_haltung` steht daneben und laesst genau das zu.
        """
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute("SELECT id FROM lzg_knoten LIMIT 1")
            zeile = cur.fetchone()
            self.assertIsNotNone(zeile, "Kein LZG-Knoten im Bestand — Zeuge untauglich")
            cur.execute(
                "SELECT id FROM abstrakt_knoten WHERE art = 'qualitaet' LIMIT 1"
            )
            qualitaet = cur.fetchone()
            self.assertIsNotNone(qualitaet, "Keine Qualitaet gesetzt")

            with self.assertRaises(psycopg2.errors.CheckViolation):
                cur.execute(
                    "INSERT INTO traeger_qualitaet "
                    "(knoten_id, qualitaet_id, auspraegung, quelle) "
                    "VALUES (%s, %s, -0.5, 'zeuge')",
                    (zeile[0], qualitaet[0]),
                )
            conn.rollback()

    def test_ein_traeger_traegt_je_qualitaet_genau_eine_kante(self) -> None:
        """Eine zweite Profilierung verstaerkt, sie dupliziert nicht.

        Ohne die Eindeutigkeit truege ein Knoten nach zehn Laeufen zehn
        Auspraegungen derselben Dimension, und der Merkmalszug summierte
        Wiederholungen statt Merkmale.
        """
        with psycopg2.connect(POSTGRES_URL) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT constraint_name FROM information_schema.table_constraints "
                "WHERE table_name = 'traeger_qualitaet' AND constraint_type = 'UNIQUE'"
            )
            namen: set[str] = {zeile[0] for zeile in cur.fetchall()}
            self.assertTrue(
                namen, "`traeger_qualitaet` traegt keine Eindeutigkeit",
            )
            cur.execute(
                "SELECT a.attname FROM pg_constraint c "
                "JOIN pg_attribute a ON a.attrelid = c.conrelid "
                "                   AND a.attnum = ANY(c.conkey) "
                "WHERE c.conrelid = 'traeger_qualitaet'::regclass AND c.contype = 'u'"
            )
            spalten: set[str] = {zeile[0] for zeile in cur.fetchall()}
            self.assertEqual(
                {"knoten_id", "qualitaet_id"}, spalten,
                f"Die Eindeutigkeit steht auf {sorted(spalten)} statt auf "
                f"(knoten_id, qualitaet_id)",
            )


if __name__ == "__main__":
    unittest.main()
