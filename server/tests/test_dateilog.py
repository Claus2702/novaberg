"""Zeugen fuer das dauerhafte Datei-Log (`config._dateilog_einrichten`).

**Warum es das gibt.** Das Behaelter-Log stirbt mit dem Behaelter. Am
09.08.2026 kostete das drei Untersuchungen: Jedesmal hatte die Antwort im
Log gestanden, jedesmal war sie beim Nachsehen fort — und zweimal wurde die
leere Ausgabe als Ergebnis gelesen statt als fehlende Datei.

**Was hier geprueft wird, ist nicht, dass es funktioniert, sondern dass ein
Fehlschlag laut ist.** Ein Datei-Handler, der sich nicht anhaengen laesst
und daroeber schweigt, hinterlaesst einen Dienst, der normal aussieht und
kein dauerhaftes Log hat. Das faellt erst auf, wenn jemand das Log braucht —
also genau dann, wenn es zu spaet ist.
"""

import logging
import os
import tempfile
import unittest

import config


class DateilogTest(unittest.TestCase):
    """Der Rueckgabewert und die Logzeile beider Ausgaenge."""

    def setUp(self) -> None:
        """Merkt sich die Handler, damit der Test sie nicht hinterlaesst."""
        self._wurzel_vorher = list(logging.getLogger().handlers)
        self._llm_vorher = list(logging.getLogger("ki_server.llm").handlers)

    def tearDown(self) -> None:
        """Stellt beide Handler-Listen wieder her.

        Ohne das traegt jeder folgende Test die Handler dieses Tests mit —
        und ein Zeuge, der die Umgebung der anderen veraendert, erzeugt
        Fehlschlaege an Stellen, die nichts damit zu tun haben.
        """
        logging.getLogger().handlers = self._wurzel_vorher
        logging.getLogger("ki_server.llm").handlers = self._llm_vorher

    def test_leerer_pfad_wird_abgelehnt_und_gemeldet(self) -> None:
        """Kein Pfad, kein Handler — und eine `error`-Zeile darueber."""
        with self.assertLogs("ki_server", level="ERROR") as gefangen:
            ergebnis = config._dateilog_einrichten("")

        self.assertFalse(ergebnis)
        self.assertIn("leerer Pfad", "\n".join(gefangen.output))

    def test_unbeschreibbarer_pfad_meldet_fehler_statt_zu_schweigen(self) -> None:
        """Ein nicht anlegbarer Ort ist ein `error`, kein stiller Verzicht.

        Der Zeuge nimmt einen Pfad unterhalb einer *Datei* — dort kann kein
        Verzeichnis entstehen, und das gilt unabhaengig davon, unter welcher
        Kennung die Suite laeuft. Ein Test gegen `/proc/…` waere als `root`
        gruen und als Nutzer rot.
        """
        with tempfile.NamedTemporaryFile() as sperre:
            unmoeglich = os.path.join(sperre.name, "unter", "server.log")
            with self.assertLogs("ki_server", level="ERROR") as gefangen:
                ergebnis = config._dateilog_einrichten(unmoeglich)

        self.assertFalse(ergebnis)
        self.assertIn("nicht beschreibbar", "\n".join(gefangen.output))

    def test_beide_logger_bekommen_den_handler(self) -> None:
        """Wurzel **und** LLM-Logger schreiben in die Datei.

        Der LLM-Logger steht auf `propagate = False`. Ein Handler an der
        Wurzel erreicht ihn deshalb nicht — und die `LLM-Call`-Zeilen sind
        der meistgelesene Teil des Logs. Faellt die zweite Zuweisung weg,
        ist die Datei genau dort leer, wo zuerst hingesehen wird.
        """
        from logging.handlers import RotatingFileHandler

        with tempfile.TemporaryDirectory() as ordner:
            ziel = os.path.join(ordner, "server.log")
            self.assertTrue(config._dateilog_einrichten(ziel))

            # Geprueft wird die Identitaet, nicht die Anzahl: Beim Import
            # von `config` haengt bereits ein Handler auf `/logs/server.log`
            # an der Wurzel. Ein Zeuge, der zaehlt, misst diesen mit und
            # wird rot, obwohl das Gepruefte stimmt.
            for name in ("", "ki_server.llm"):
                ziele = [h.baseFilename
                         for h in logging.getLogger(name).handlers
                         if isinstance(h, RotatingFileHandler)]
                self.assertIn(
                    ziel, ziele,
                    f"Logger '{name or '(Wurzel)'}' schreibt nicht nach "
                    f"{ziel} — gefunden: {ziele}",
                )

            logging.getLogger("ki_server.llm").debug("Zeuge: LLM-Zeile")
            for handler in logging.getLogger("ki_server.llm").handlers:
                handler.flush()

            with open(ziel, encoding="utf-8") as datei:
                self.assertIn("Zeuge: LLM-Zeile", datei.read())


if __name__ == "__main__":
    unittest.main()
