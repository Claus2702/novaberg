"""Tests: Wer zuordnen soll, sieht den ganzen Beitrag.

Ziel: `format_session_turns_numbered` kuerzt keinen Beitrag mehr. Wo eine
Grenze noetig ist, greift sie ueber das **ganze Fenster** und wirft die
aeltesten Gruppen weg — nie einen Beitrag in der Mitte.

Hintergrund, gemessen am 16.09.2026 ueber 1494 Rohturns: Die Funktion schnitt
jeden Beitrag nach 100 Zeichen ab, und keiner ihrer neun Aufrufer uebergab
einen anderen Wert. **94,2 % der Antworten Novas** liegen darueber (Median 440
Zeichen), 36,8 % der Nutzer-Aeusserungen. Ein Leser, der zuordnen soll, bekam
den Anfang einer Regieanweisung und nie das Angebot am Schluss. Die Kosten der
Abhilfe, ueber 1439 Fenster aus fuenf Gruppen: 893 Zeichen gekappt gegen 5572
ungekappt im Mittel; bei einem Budget von 8000 gehen 81,7 % der Fenster ganz
durch.

Zeugen dieser Datei:
  * **Der vollstaendige Beitrag ist der schaerfste Zeuge.** Ein Text ueber der
    alten Grenze muss Zeichen fuer Zeichen im Ergebnis stehen — das prueft das
    Ziel und nicht die Bauart. Er wird rot, sobald irgendwo wieder je Beitrag
    gekappt wird, gleich mit welchem Wert.
  * **Die Auslassungsmarke wird ausdruecklich ausgeschlossen.** Ein Test auf
    Anwesenheit des Anfangs wuerde eine Rueckkehr zur Kappung nicht bemerken,
    denn der Anfang steht auch im gekappten Text.
  * **Das Budget wird an seiner Wirkung geprueft, nicht an seinem Wert:**
    Faellt eine Gruppe weg, muss sie **ganz** weg sein und die uebrigen
    vollstaendig dastehen.
  * **Die juengste Gruppe ist der Randfall, der die Regel traegt.** Liegt sie
    allein ueber dem Budget, bleibt sie trotzdem — ein Fenster ohne den
    aktuellen Wortwechsel beantwortet keine Frage, die ein Leser stellt.
  * **Der Wegfall wird protokolliert.** Ohne die Zeile ist *nichts
    weggefallen* von *nicht gerechnet* nicht zu unterscheiden.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from memory.session import (
    HERKUNFT_EIGENER_IMPULS,
    SESSION_HISTORY_BUDGET_CHARS,
    Verlaufsbeitrag,
    budget_wahren,
    format_session_turns_numbered,
    verlauf_gruppieren,
)


def _turn(rolle: str, inhalt: str, herkunft: str = "nutzer_turn", **rest) -> dict:
    """Ein gespeicherter Turn in der Form, die `session_turn_store` schreibt."""
    return {"rolle": rolle, "inhalt": inhalt, "herkunft": herkunft, **rest}


#: Eine Antwort in der Groessenordnung des Betriebs: Median 440 Zeichen, mit
#: einer Regieanweisung davor, wie sie am 14.09.2026 mit 157 bis 208 Zeichen
#: gemessen wurde. Der Inhalt ist synthetisch; Traeger des Zeugen ist die
#: **Laenge** und die Stellung des Schlusses, nicht der Wortlaut.
REGIE: str = (
    "(Sie lehnt sich zurueck, laesst den Blick einen Moment in der Ferne "
    "haengen und sortiert die Gedanken, bevor sie antwortet, waehrend im "
    "Hintergrund das Ticken der Uhr den Takt vorgibt.) "
)
SCHLUSS: str = "Soll ich das fuer dich festhalten?"
LANGE_ANTWORT: str = REGIE + ("Der Gedanke traegt weiter, als er zunaechst " * 6) + SCHLUSS


class DerBeitragStehtGanzTest(unittest.TestCase):
    """Das ZIEL: kein Beitrag wird mehr in der Mitte abgeschnitten."""

    def test_ein_beitrag_ueber_der_alten_grenze_steht_vollstaendig(self) -> None:
        turns = [_turn("user", "Und dann?"), _turn("assistant", LANGE_ANTWORT)]

        aus = format_session_turns_numbered(turns)

        self.assertIn(LANGE_ANTWORT, aus)

    def test_der_schluss_erreicht_den_leser(self) -> None:
        # Der Fall aus dem Betrieb: Das Angebot steht am Ende, hinter einer
        # Regieanweisung, die allein schon laenger war als die alte Grenze.
        self.assertGreater(len(REGIE), 100)
        turns = [_turn("user", "Und dann?"), _turn("assistant", LANGE_ANTWORT)]

        aus = format_session_turns_numbered(turns)

        self.assertIn(SCHLUSS, aus)

    def test_ohne_max_chars_steht_keine_auslassungsmarke_im_verlauf(self) -> None:
        # Gegen die Rueckkehr zur Kappung: Der Anfang steht auch im gekappten
        # Text, die Marke nur im gekappten.
        turns = [_turn("user", "Und dann?"), _turn("assistant", LANGE_ANTWORT)]

        aus = format_session_turns_numbered(turns)

        self.assertNotIn("...", aus)

    def test_max_chars_gesetzt_kappt_weiterhin(self) -> None:
        # Die Grenze ist nicht entfallen, nur ihre Vorgabe. Wer sie setzt,
        # bekommt sie.
        turns = [_turn("user", "Und dann?"), _turn("assistant", LANGE_ANTWORT)]

        aus = format_session_turns_numbered(turns, max_chars=50)

        self.assertNotIn(SCHLUSS, aus)
        self.assertIn("...", aus)


class DasBudgetWirftGanzeGruppenWegTest(unittest.TestCase):
    """Wo eine Grenze bleibt, trifft sie die Gruppe, nicht den Beitrag."""

    @staticmethod
    def _gruppen(anzahl: int, zeichen: int) -> list[list[Verlaufsbeitrag]]:
        """`anzahl` Gruppen aus je einem Nutzerbeitrag von `zeichen` Laenge."""
        turns = [_turn("user", f"{i}" * zeichen) for i in range(anzahl)]
        return verlauf_gruppieren(turns)

    def test_die_aelteste_gruppe_faellt_ganz_weg(self) -> None:
        gruppen = self._gruppen(anzahl=3, zeichen=100)

        behalten, weggefallen = budget_wahren(gruppen, budget_chars=250)

        self.assertEqual(weggefallen, 1)
        self.assertEqual(len(behalten), 2)
        # Ganz weg heisst: die uebrigen stehen unversehrt.
        for gruppe in behalten:
            for beitrag in gruppe:
                self.assertEqual(len(beitrag.inhalt), 100)

    def test_die_juengste_gruppe_bleibt_als_erste_erhalten(self) -> None:
        gruppen = self._gruppen(anzahl=3, zeichen=100)

        behalten, _ = budget_wahren(gruppen, budget_chars=250)

        self.assertEqual(behalten[-1], gruppen[-1])

    def test_die_juengste_gruppe_bleibt_auch_allein_ueber_budget(self) -> None:
        gruppen = self._gruppen(anzahl=2, zeichen=500)

        behalten, weggefallen = budget_wahren(gruppen, budget_chars=100)

        self.assertEqual(len(behalten), 1)
        self.assertEqual(weggefallen, 1)
        self.assertEqual(len(behalten[0][0].inhalt), 500)

    def test_ein_fenster_im_budget_verliert_nichts(self) -> None:
        gruppen = self._gruppen(anzahl=3, zeichen=100)

        behalten, weggefallen = budget_wahren(gruppen, budget_chars=SESSION_HISTORY_BUDGET_CHARS)

        self.assertEqual(weggefallen, 0)
        self.assertEqual(len(behalten), 3)

    def test_ein_budget_ohne_wert_ist_ein_aufruffehler(self) -> None:
        gruppen = self._gruppen(anzahl=1, zeichen=10)

        with self.assertRaises(ValueError):
            budget_wahren(gruppen, budget_chars=0)

    def test_eine_leere_eingabe_liefert_leer_und_null(self) -> None:
        self.assertEqual(budget_wahren([], budget_chars=100), ([], 0))


class DerWegfallStehtImProtokollTest(unittest.TestCase):
    """Nichts weggefallen und nicht gerechnet duerfen nicht gleich aussehen."""

    def test_ein_wegfall_schreibt_seine_zahl(self) -> None:
        turns = [_turn("user", "x" * 300), _turn("user", "y" * 300)]

        with self.assertLogs("ki_server.memory.session", level="INFO") as protokoll:
            format_session_turns_numbered(turns, budget_chars=400)

        self.assertTrue(
            any("Gruppen wegen Budget" in zeile for zeile in protokoll.output),
            protokoll.output,
        )

    def test_ohne_wegfall_keine_zeile(self) -> None:
        turns = [_turn("user", "kurz"), _turn("assistant", "auch kurz")]

        with self.assertNoLogs("ki_server.memory.session", level="INFO"):
            format_session_turns_numbered(turns)


class DerImpulsBleibtImBudgetTest(unittest.TestCase):
    """Das Budget darf den Defekt vom 24.08.2026 nicht wieder einfuehren."""

    def test_ein_eigen_impuls_faellt_nicht_vor_einer_fremden_rede_weg(self) -> None:
        # Der Impuls steht in derselben Gruppe wie die Nachfrage, die er
        # ausgeloest hat; ein Budget darf nicht den Impuls und nicht die
        # Nachfrage allein wegnehmen.
        turns = [
            _turn("user", "a" * 200),
            _turn("assistant", "b" * 200, herkunft=HERKUNFT_EIGENER_IMPULS),
            _turn("user", "c" * 200),
        ]

        aus = format_session_turns_numbered(turns, budget_chars=450)

        self.assertIn("c" * 200, aus)
        self.assertIn("von sich aus", aus)
        self.assertNotIn("a" * 200, aus)


if __name__ == "__main__":
    unittest.main()
