"""Zeugen: Der CharakterAgent hinterlaesst eine Spur im `hintergrund_log`.

Ziel: Wer wissen will, wann destilliert wurde, liest das Audit — nicht das
Serverlog und nicht die Nebenwirkungen in anderen Tabellen.

`[gemessen]` — 06.09.2026: Beim Zaehlen der Destillationszyklen trug das
`hintergrund_log` **keine einzige** Zeile dieses Agenten, bei 51 993 Zeilen
insgesamt. Die Zahl musste ueber Serverlog und `charakter_rad_messung`
rekonstruiert werden. Genau dafuer gibt es die Audit-Pflicht.

Zeugen dieser Datei:
  * **Alle drei Zustaende einzeln:** `gestartet`, `erledigt`, `fehler`.
  * **Der Leerlauf schweigt.** Der Agent prueft alle zehn Minuten und findet
    meist kein `hash_dirty`; ein Eintrag je Pruefung waere 144 Zeilen am Tag,
    die nichts sagen. Ohne diesen Zeugen wuerde niemand merken, dass die
    Sparsamkeit verlorengeht — sie sieht im Betrieb aus wie mehr Sorgfalt.
  * **Die Exception wird weitergereicht.** Ein Agent, der sie schluckt,
    nimmt dem Dispatch die Entscheidung ueber Retry und Wiedervorlage.
  * **Der Abschluss traegt seine Zahlen**, auch die Null: Ein Lauf ohne
    Speicherung ist ein Ergebnis und von einem ausgefallenen nur an dieser
    Zeile zu unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from agents.charakter.agent import CharakterAgent

#: Der Importpfad — Ziel jedes `patch`.
_MODUL: str = "agents.charakter.agent"

#: Der Logger haengt eine Ebene hoeher als das Modul (`…charakter`, nicht
#: `…charakter.agent`). Wer auf den Modulpfad horcht, findet nie eine Zeile —
#: ein Zeuge, der gruen ist, weil er am falschen Ort lauscht.
_LOGGER: str = "ki_server.agents.charakter"


class TestDerLeerlaufSchweigt(unittest.TestCase):
    """Kein `hash_dirty`, keine Zeile."""

    def test_ohne_dirty_kein_audit(self) -> None:
        agent = object.__new__(CharakterAgent)
        with patch(f"{_MODUL}.redis_client") as redis, \
             patch.object(CharakterAgent, "_audit_log") as audit:
            redis.get.return_value = None
            zustand = CharakterAgent.invoke(agent, {})
        audit.assert_not_called()
        self.assertEqual(zustand["status"], "abgeschlossen")
        self.assertEqual(zustand["ergebnis"], {"destilliert": 0})


class TestDerFehlerpfad(unittest.TestCase):
    """Ein Abbruch hinterlaesst eine Zeile und bleibt ein Abbruch."""

    def test_die_exception_erzeugt_einen_fehler_eintrag(self) -> None:
        agent = object.__new__(CharakterAgent)
        with patch.object(CharakterAgent, "_profile_destillieren",
                          side_effect=RuntimeError("Redis weg")), \
             patch.object(CharakterAgent, "_audit_log") as audit:
            with self.assertRaises(RuntimeError):
                CharakterAgent.invoke(agent, {})
        audit.assert_called_once()
        _, status, text = audit.call_args[0]
        self.assertEqual(status, "fehler")
        self.assertIn("RuntimeError", text)
        self.assertIn("Redis weg", text)

    def test_die_exception_wird_weitergereicht(self) -> None:
        """Ueber Retry entscheidet der Dispatch, nicht der Agent."""
        agent = object.__new__(CharakterAgent)
        with patch.object(CharakterAgent, "_profile_destillieren",
                          side_effect=ValueError("kaputt")), \
             patch.object(CharakterAgent, "_audit_log"):
            with self.assertRaises(ValueError):
                CharakterAgent.invoke(agent, {})


class TestDieSenkeFaelltNichtDurch(unittest.TestCase):
    """Ein defektes Audit darf den Lauf nicht mitreissen."""

    def test_db_fehler_wird_kritisch_gemeldet_und_verschluckt(self) -> None:
        with patch(f"{_MODUL}.db_manager") as db, \
             self.assertLogs(_LOGGER, level="CRITICAL") as log:
            db.execute.side_effect = RuntimeError("Senke tot")
            CharakterAgent._audit_log("meister", "erledigt", "1 Profile")
        self.assertIn("verlorener Audit-Eintrag", "\n".join(log.output))

    def test_die_zeile_traegt_aufgabe_und_status(self) -> None:
        with patch(f"{_MODUL}.db_manager") as db:
            CharakterAgent._audit_log("meister", "gestartet", "hash_dirty gesetzt")
        werte = db.execute.call_args[0][1]
        self.assertEqual(werte[0], "meister")
        self.assertEqual(werte[1], "charakter_hash")
        self.assertEqual(werte[2], "gestartet")
        self.assertIn("hash_dirty", werte[3])


class TestDerAufruferSchreibtBeideZustaende(unittest.TestCase):
    """`gestartet` beim Beginn der Arbeit, `erledigt` am Ende des Paares."""

    def test_ein_dirty_lauf_meldet_start_und_abschluss(self) -> None:
        agent = object.__new__(CharakterAgent)
        with patch(f"{_MODUL}.redis_client") as redis, \
             patch.object(CharakterAgent, "_audit_log") as audit, \
             patch.object(CharakterAgent, "_kzg_laden", return_value=[]), \
             patch.object(CharakterAgent, "_turns_laden", return_value=[]), \
             patch.object(CharakterAgent, "_lzg_kern_laden", return_value=[]), \
             patch.object(CharakterAgent, "_lzg_intentionen_laden", return_value=[]), \
             patch.object(CharakterAgent, "_lzg_emotionen_laden", return_value=[]), \
             patch(f"{_MODUL}.db_manager", MagicMock()):
            redis.get.return_value = "1"
            CharakterAgent.invoke(agent, {})
        zustaende = [ruf[0][1] for ruf in audit.call_args_list]
        self.assertEqual(zustaende, ["gestartet", "erledigt"])
        self.assertIn("destilliert", audit.call_args_list[-1][0][2])


if __name__ == "__main__":
    unittest.main()
