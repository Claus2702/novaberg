"""Tests fuer die Zerlegung des Themenfeldes (Konvention 4).

Ziel: Aus dem Themenfeld einer Ausarbeitung entstehen genau die Themen, die
darin stehen — jedes einmal, in Reihenfolge, ohne Reste.

Warum das eine eigene Datei wert ist: `themen_zerlegen` ist die EINE Quelle
fuer Live-Pfad und Wartungswerkzeug (`F-EMBED-1`). Zwei Zerlegungen ergaeben
zwei Mengen von Themenvektoren, und der Unterschied fiele erst auf, wenn
jemand dieselbe Frage zweimal stellt — einmal vor und einmal nach einer
Nachbettung.

Die Randfaelle sind aus dem Bestand genommen, nicht erfunden: Das Feld traegt
im Mittel 4,37 Themen, hoechstens 17, und ein Eintrag von 250 traegt gar kein
Trennzeichen.
"""

import unittest

from memory.repositories.autonomous_wissen_repository import (
    THEMA_MINDESTLAENGE,
    themen_zerlegen,
)


class ZerlegungTest(unittest.TestCase):
    """Was aus einem Themenfeld wird."""

    def test_mehrere_themen_in_reihenfolge(self) -> None:
        """Der Normalfall — 249 von 250 Feldern sehen so aus."""
        self.assertEqual(
            ["Begegnung", "Entropie", "Informationsaustausch", "Ontologie"],
            themen_zerlegen("Begegnung, Entropie, Informationsaustausch, Ontologie"),
        )

    def test_einzelnes_thema_bleibt_eines(self) -> None:
        """Ein Feld ohne Trennzeichen ergibt genau ein Thema, nicht null."""
        self.assertEqual(["Larvalentwicklung"], themen_zerlegen("Larvalentwicklung"))

    def test_leeres_feld_ergibt_leere_liste(self) -> None:
        """Kein Thema ist ein Fall fuer den Aufrufer, kein Fehler der Zerlegung."""
        self.assertEqual([], themen_zerlegen(""))
        self.assertEqual([], themen_zerlegen("   "))

    def test_semikolon_trennt_ebenso(self) -> None:
        """Selten, aber wo es vorkommt, trennt es genauso wie das Komma."""
        self.assertEqual(["Mut", "Vertrauen"], themen_zerlegen("Mut; Vertrauen"))

    def test_dubletten_verschwinden(self) -> None:
        """Zweimal dasselbe Thema waere zweimal derselbe Vektor im Ergebnis."""
        self.assertEqual(
            ["Entropie", "Ontologie"],
            themen_zerlegen("Entropie, Ontologie, Entropie"),
        )

    def test_leere_glieder_fallen_weg(self) -> None:
        """Ein doppeltes Trennzeichen erzeugt kein leeres Thema."""
        self.assertEqual(["Entropie", "Ontologie"], themen_zerlegen("Entropie,, Ontologie,"))

    def test_zu_kurze_glieder_fallen_weg(self) -> None:
        """Ein Rest unter der Mindestlaenge ist kein Gegenstand."""
        kurz: str = "a" * (THEMA_MINDESTLAENGE - 1)
        lang: str = "a" * THEMA_MINDESTLAENGE
        self.assertEqual([lang], themen_zerlegen(f"{kurz}, {lang}"))

    def test_kurze_echte_themen_bleiben(self) -> None:
        """Der Fall, der die Mindestlaenge von 4 auf 2 korrigiert hat.

        `KI` steht viermal im Bestand, `AuD` und `AUM` je einmal. Eine
        Abkuerzung ist ein Thema wie jedes andere — wer sie wegwirft, macht
        die Ausarbeitung darueber unauffindbar, und niemand bemerkt es.
        """
        self.assertEqual(["Mut", "Vertrauen"], themen_zerlegen("Mut; Vertrauen"))
        self.assertEqual(["KI", "Ethik"], themen_zerlegen("KI, Ethik"))

    def test_umgebende_leerzeichen_gehoeren_nicht_zum_thema(self) -> None:
        """Sonst waeren ' Entropie' und 'Entropie' zwei Themen."""
        self.assertEqual(["Entropie", "Ontologie"], themen_zerlegen("  Entropie ,  Ontologie  "))

    def test_siebzehn_themen_bleiben_siebzehn(self) -> None:
        """Der gemessene Hoechstwert des Bestandes — nichts wird gekappt."""
        feld: str = ", ".join(f"Thema{n:02d}" for n in range(17))
        self.assertEqual(17, len(themen_zerlegen(feld)))

    def test_nicht_text_scheitert_laut(self) -> None:
        """Eine Zerlegung ueber einem Nicht-Text ergaebe Zufallsvektoren."""
        with self.assertRaises(TypeError):
            themen_zerlegen(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
