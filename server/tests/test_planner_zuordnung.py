"""Tests für die Zuordnung des Planners über `management_target`.

Ziel: Ein Auftrag erreicht den Dienst, den er meint — auch wenn zwei
Dienstnamen denselben Wortstamm teilen.

Die Zusicherungen, die hier geprüft werden:

  1. **Ein exakter Treffer schlägt jeden unscharfen.** Sonst entscheidet die
     Reihenfolge des sortierten Verzeichnis-Scans, und die ist keine
     fachliche Aussage.
  2. **Mehrdeutigkeit wird gemeldet und nicht aufgelöst.** Zwei Dienste, auf
     die dasselbe Ziel unscharf passt, ergeben keinen Gewinner — der Planner
     fällt auf seine späteren Prioritäten zurück.
  3. **Der Bestandsfall bleibt erreichbar:** Wo nur ein Dienst unscharf
     passt, wird er weiterhin gewählt.

**Der erste Zeuge stellt die Kollision her, statt sie zu beschreiben.**
`dateien` und `dateien_wurzeln` sind das erste Paar im Bestand, bei dem
`ziel_a in ziel_b` gilt; der Fund dazu stand in `novaberg-fundliste.md`,
bevor der zweite Dienst gebaut wurde. Ein Zeuge, der nur die Hilfsfunktion
mit erfundenen Namen aufruft, prüfte eine Regel und nicht diesen Fall.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes.planner import _manager_zu_target


class _Dienst:
    """Ein Manager-Doppel, das genau das kann, was die Zuordnung liest."""

    def __init__(self, ziel: str) -> None:
        """Merkt sich den Zielnamen."""
        self.ziel = ziel


def _registry(*ziele: str) -> dict:
    """Baut eine Registry in der Reihenfolge, die der Verzeichnis-Scan liefert.

    Die Reihenfolge ist Teil des Prüfgegenstands: Der Scan sortiert
    alphabetisch, und genau darauf ist die alte Fassung hereingefallen.
    """
    return {f"{ziel}_manager": _Dienst(ziel) for ziel in sorted(ziele)}


class TestExaktSchlaegtUnscharf(unittest.TestCase):
    """Der Fall, für den der Riegel gebaut wurde."""

    def test_freigabe_landet_nicht_beim_lesenden_dienst(self) -> None:
        """`dateien` steckt in `dateien_wurzeln` — und kommt alphabetisch zuerst."""
        registry: dict = _registry("dateien", "dateien_wurzeln")

        # Vorbedingung des Zeugen: Die Falle ist wirklich gestellt.
        self.assertEqual(["dateien", "dateien_wurzeln"],
                         [m.ziel for m in registry.values()])
        self.assertIn("dateien", "dateien_wurzeln")

        treffer = _manager_zu_target(registry, "dateien_wurzeln")

        self.assertIsNotNone(treffer)
        self.assertEqual("dateien_wurzeln", treffer.ziel)

    def test_der_lesende_dienst_bleibt_erreichbar(self) -> None:
        """Die Gegenrichtung: Sein eigenes Ziel muss ihn weiterhin treffen."""
        registry: dict = _registry("dateien", "dateien_wurzeln")

        treffer = _manager_zu_target(registry, "dateien")

        self.assertEqual("dateien", treffer.ziel)


class TestMehrdeutigkeitWirdGemeldet(unittest.TestCase):
    """Kein Gewinner nach Verzeichnisreihenfolge."""

    def test_zwei_unscharfe_treffer_ergeben_keinen(self) -> None:
        """Der erste wäre der alphabetisch erste — das ist keine Zuordnung."""
        registry: dict = _registry("notiz", "notizen")

        with self.assertLogs("ki_server.planner", level="ERROR"):
            treffer = _manager_zu_target(registry, "notizen_und_mehr")

        self.assertIsNone(treffer)

    def test_die_meldung_nennt_beide_dienste(self) -> None:
        """Wer den Fall aufräumen soll, braucht die Namen, nicht die Zahl."""
        registry: dict = _registry("notiz", "notizen")

        with self.assertLogs("ki_server.planner", level="ERROR") as protokoll:
            _manager_zu_target(registry, "notizen_und_mehr")

        text: str = "\n".join(protokoll.output)
        self.assertIn("notiz", text)
        self.assertIn("notizen", text)


class TestDerBestandsfallBleibt(unittest.TestCase):
    """Ein einzelner unscharfer Treffer wird weiterhin gewählt."""

    def test_ein_unscharfer_treffer_gewinnt(self) -> None:
        """„Einkaufsliste" trifft `notizen` nicht exakt und soll trotzdem hin."""
        registry: dict = _registry("notizen", "timeline")

        treffer = _manager_zu_target(registry, "notizen")

        self.assertEqual("notizen", treffer.ziel)

    def test_teilzeichenkette_in_die_andere_richtung(self) -> None:
        """Das Ziel steckt im Dienstnamen, nicht umgekehrt."""
        registry: dict = _registry("charakter_identitaet", "timeline")

        treffer = _manager_zu_target(registry, "charakter")

        self.assertEqual("charakter_identitaet", treffer.ziel)

    def test_ohne_treffer_kein_dienst(self) -> None:
        """Kein Treffer ist eine Antwort — der Planner hat weitere Prioritäten."""
        registry: dict = _registry("notizen", "timeline")

        self.assertIsNone(_manager_zu_target(registry, "wetterbericht"))

    def test_leeres_ziel_wird_laut_abgelehnt(self) -> None:
        """Der Aufrufer prüft es vorher; kommt es doch, ist es ein Fehler."""
        with self.assertLogs("ki_server.planner", level="ERROR"):
            self.assertIsNone(_manager_zu_target(_registry("notizen"), ""))


if __name__ == "__main__":
    unittest.main()
