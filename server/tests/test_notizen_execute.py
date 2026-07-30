"""Tests: Der Notizen-Manager fuehrt eine Liste von Schreibauftraegen aus.

Ziel: Das heutige Verhalten von `NotizenManager.execute` ist festgeschrieben,
bevor die Methode zerlegt wird. Ein **Charakterisierungs-Netz** — es haelt fest,
was ist, nicht was sein sollte.

Hintergrund: 67 Zeilen, sechs Verschachtelungsebenen, ein Aktions-Dispatch als
`if/elif`-Kette in einer Schleife in einem `try` — und **kein Test**. Vier
Testdateien schienen die Methode zu rufen; es war jedes Mal `cur.execute()` auf
einem Datenbank-Cursor. Der Name allein ist keine Abdeckung.

Zeugen dieser Datei:
  * **Der Rueckgabewert ist die Zahl der verarbeiteten Auftraege**, und daran
    haengen die Erwartungen. Er ist das einzige, was die Methode nach aussen
    gibt.
  * **Die Asymmetrie der Zaehlung wird gepinnt, nicht geglaettet.** Der neue
    Pfad zaehlt nur bei `erfolg`, der alte Pfad zaehlt unbedingt. `verarbeitet`
    bedeutet damit je Pfad etwas anderes. Der Test behauptet nicht, dass das
    richtig ist — er haelt fest, dass es so ist.
  * **Der stille Uebersprung wird gepinnt.** Eine unbekannte Aktion erzeugt
    keine Zeile im Log und keine Zaehlung. Wer sie spaeter meldet, aendert
    Verhalten und soll das an einem roten Test merken.
  * **Der `try` steht in der Schleife, nicht darum.** Ein gescheiterter Auftrag
    darf die folgenden nicht mitnehmen; ein Test faehrt deshalb zwei Auftraege,
    von denen der erste wirft.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from plugins.notizen_manager.manager import NotizenManager

USER: str = "meister"
PG:   str = "postgresql://test"


def _schreiben(aktion: str, **daten: object) -> dict:
    """Baut einen Schreibauftrag."""
    return {"aktion": aktion, "daten": dict(daten)}


class ExecuteBasis(unittest.TestCase):
    """Gemeinsamer Aufbau: die Unterfunktionen der Methode sind gemockt."""

    def setUp(self) -> None:
        """Ein Manager, dessen Helfer alle austauschbar sind."""
        self.manager = NotizenManager()
        self.verarbeiten = MagicMock(return_value={"erfolg": True, "aktion": "create"})
        self.aktualisieren = MagicMock()
        self.loeschen = MagicMock()
        self.manager.notiz_verarbeiten = self.verarbeiten
        self.manager._aktualisieren = self.aktualisieren
        self.manager._loeschen = self.loeschen

    def _fahren(self, *writes: dict) -> int:
        """Ruft `execute` mit den gegebenen Auftraegen."""
        with patch(
            "plugins.notizen_manager.manager.NotizenRepository"
        ) as repo:
            self.repo = repo
            return self.manager.execute(
                list(writes), USER, MagicMock(), PG,
            )


class NeuerPfad(ExecuteBasis):
    """create, append und query gehen ueber `notiz_verarbeiten`."""

    def test_die_drei_aktionen_gehen_an_notiz_verarbeiten(self) -> None:
        """Jede der drei ruft den M6-Pfad mit ihrer eigenen Aktion."""
        for aktion in ("create", "append", "query"):
            self.verarbeiten.reset_mock()
            self._fahren(_schreiben(aktion, text="etwas"))
            self.assertEqual(
                self.verarbeiten.call_args.kwargs["aktion"], aktion,
            )

    def test_erfolg_wird_gezaehlt(self) -> None:
        """Ein erfolgreicher Auftrag erhoeht die Zahl."""
        self.assertEqual(self._fahren(_schreiben("create", text="x")), 1)

    def test_ohne_erfolg_wird_nicht_gezaehlt(self) -> None:
        """Meldet der M6-Pfad keinen Erfolg, zaehlt der Auftrag nicht."""
        self.verarbeiten.return_value = {"erfolg": False, "aktion": "create"}
        self.assertEqual(self._fahren(_schreiben("create", text="x")), 0)

    def test_die_turn_id_wird_aus_den_daten_gezogen(self) -> None:
        """`turn_id` reist im Datenteil und wird als eigenes Argument uebergeben."""
        self._fahren(_schreiben("create", text="x", turn_id="turn-7"))
        self.assertEqual(self.verarbeiten.call_args.kwargs["turn_id"], "turn-7")


class UpdateZweiPfade(ExecuteBasis):
    """Update geht ueber M6 oder den alten Pfad — je nach `notiz_id`."""

    def test_mit_notiz_id_geht_es_ueber_m6(self) -> None:
        """Liegt eine `notiz_id` vor, uebernimmt `notiz_verarbeiten`."""
        self.assertEqual(
            self._fahren(_schreiben("update", notiz_id=42, text="neu")), 1,
        )
        self.assertEqual(self.verarbeiten.call_args.kwargs["aktion"], "update")
        self.aktualisieren.assert_not_called()

    def test_ohne_notiz_id_geht_es_ueber_den_alten_pfad(self) -> None:
        """Ohne `notiz_id` uebernimmt `_aktualisieren` mit target und text."""
        self.assertEqual(
            self._fahren(_schreiben("update", target="Einkauf", text="neu")), 1,
        )
        self.aktualisieren.assert_called_once()
        self.verarbeiten.assert_not_called()

    def test_der_alte_pfad_zaehlt_unbedingt(self) -> None:
        """Die Asymmetrie, gepinnt: der alte Pfad zaehlt ohne Erfolgspruefung.

        `_aktualisieren` gibt nichts zurueck, also gibt es nichts zu pruefen —
        der Auftrag gilt als verarbeitet, sobald der Aufruf nicht geworfen hat.
        Der M6-Zweig daneben zaehlt nur bei `erfolg`. `verarbeitet` bedeutet
        damit je Pfad etwas anderes.
        """
        self.verarbeiten.return_value = {"erfolg": False}
        m6  = self._fahren(_schreiben("update", notiz_id=1, text="x"))
        alt = self._fahren(_schreiben("update", target="Liste", text="x"))
        self.assertEqual(m6, 0)
        self.assertEqual(alt, 1)


class DeleteZweiPfade(ExecuteBasis):
    """Delete invalidiert per Repository oder loescht ueber den alten Pfad."""

    def test_mit_notiz_id_wird_invalidiert(self) -> None:
        """Die `notiz_id` geht an das Repository."""
        with self.assertLogs("ki_server.plugins.notizen", "INFO") as log:
            zahl = self._fahren(_schreiben("delete", notiz_id=42))
        self.repo.invalidate.assert_called_once_with(PG, 42)
        self.loeschen.assert_not_called()
        self.assertEqual(zahl, 1)
        self.assertIn("42", log.output[-1])

    def test_ohne_notiz_id_geht_es_ueber_den_alten_pfad(self) -> None:
        """Ohne `notiz_id` uebernimmt `_loeschen`."""
        self.assertEqual(self._fahren(_schreiben("delete", target="Liste")), 1)
        self.loeschen.assert_called_once()

    def test_beide_delete_pfade_zaehlen(self) -> None:
        """Die Zaehlung steht hinter dem `if`, sie gilt beiden Zweigen."""
        self.assertEqual(
            self._fahren(
                _schreiben("delete", notiz_id=1),
                _schreiben("delete", target="Liste"),
            ), 2,
        )


class FehlerJeAuftrag(ExecuteBasis):
    """Ein gescheiterter Auftrag nimmt die folgenden nicht mit."""

    def test_der_naechste_auftrag_laeuft_weiter(self) -> None:
        """Der `try` steht in der Schleife: nach dem Fehler geht es weiter."""
        self.verarbeiten.side_effect = [
            RuntimeError("kaputt"), {"erfolg": True, "aktion": "create"},
        ]
        with self.assertLogs("ki_server.plugins.notizen", "ERROR"):
            zahl = self._fahren(
                _schreiben("create", text="eins"),
                _schreiben("create", text="zwei"),
            )
        self.assertEqual(zahl, 1)
        self.assertEqual(self.verarbeiten.call_count, 2)

    def test_der_fehler_nennt_aktion_und_typ(self) -> None:
        """Die Meldung traegt den Ausnahmetyp vorn und die Aktion."""
        self.verarbeiten.side_effect = RuntimeError("kaputt")
        with self.assertLogs("ki_server.plugins.notizen", "ERROR") as log:
            self._fahren(_schreiben("create", text="x"))
        self.assertIn("RuntimeError", log.output[-1])
        self.assertIn("create", log.output[-1])


class UnbekannteAktion(ExecuteBasis):
    """Eine unbekannte Aktion faellt stillschweigend durch."""

    def test_nichts_passiert_und_nichts_wird_gemeldet(self) -> None:
        """Kein Aufruf, keine Zaehlung, **keine Log-Zeile**.

        Gepinnt, nicht gebilligt: Ein Auftrag mit einer Aktion, die keiner der
        drei Zweige kennt, verschwindet ohne Spur. Wer das meldet, aendert
        Verhalten und merkt es an diesem Test.
        """
        with self.assertNoLogs("ki_server.plugins.notizen"):
            zahl = self._fahren(_schreiben("erfunden", text="x"))
        self.assertEqual(zahl, 0)
        self.verarbeiten.assert_not_called()
        self.aktualisieren.assert_not_called()
        self.loeschen.assert_not_called()

    def test_fehlende_aktion_ebenso(self) -> None:
        """Ein Auftrag ohne `aktion` verhaelt sich wie eine unbekannte."""
        self.assertEqual(self._fahren({"daten": {}}), 0)


class MehrereAuftraege(ExecuteBasis):
    """Die Zahl summiert ueber alle Auftraege."""

    def test_leere_liste_ergibt_null(self) -> None:
        """Ohne Auftraege gibt es nichts zu verarbeiten."""
        self.assertEqual(self._fahren(), 0)

    def test_gemischte_liste_wird_summiert(self) -> None:
        """Drei Aktionen, drei Zaehlungen."""
        self.assertEqual(
            self._fahren(
                _schreiben("create", text="x"),
                _schreiben("update", target="Liste", text="y"),
                _schreiben("delete", target="Liste"),
            ), 3,
        )


if __name__ == "__main__":
    unittest.main()
