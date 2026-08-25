"""Tests: Jeder Turn und jeder Impuls ist eindeutig einer Person zuzuordnen.

Ziel: Ein Eigen-Impuls faellt nicht aus dem Verlauf, und er steht nicht auf dem
Platz der fremden Rede. Der Sprecher kommt aus dem Feld `herkunft`, nie aus der
Position in der Liste.

Hintergrund, gemessen am 24.08.2026: Beide Verlaufs-Renderer bildeten Paare
`user` -> `assistant` und uebersprangen alles, was nicht hineinpasste. Ein
Eigen-Impuls ist ein **alleinstehender** assistant-Turn und traf genau diesen
Zweig. Von 24 Turns eines laufenden Gespraechs erreichten **8** den Verlauf
nicht. Die Folge im Betrieb: Nova schlug um 18:37:40 UTC aus eigenem Antrieb
ein Vorhaben vor, der Nutzer fragte sieben Sekunden spaeter nach, worum es
gehe — und Nova fragte zurueck, worauf **er** damit hinauswolle. Ihr eigener
Vorschlag stand in dem Verlauf, den sie las, nicht mehr drin.

Die Turns unten sind **nachgebaut**, nicht kopiert: Sie tragen die Abfolge des
Betriebsfalls und keinen Gespraechsinhalt.

Zeugen dieser Datei:
  * **Die Zaehlung ist der schaerfste Zeuge.** `verlauf_gruppieren` muss so
    viele Beitraege liefern, wie Turns mit Inhalt hineingingen — das prueft den
    Zweck der Funktion (nichts geht verloren) und nicht ihre Bauart.
  * **Die Reihenfolge des Betriebsfalls wird nachgespielt**, mit genau der
    Abfolge, die den Defekt erzeugt hat: Antwort, Impuls, Nutzerfrage.
  * **Der Sprecher wird gegen die Position gehaerte t**: Zwei Turns mit
    identischer Position, aber verschiedener `herkunft`, muessen verschieden
    bezeichnet werden. Ein Test, der nur die Anwesenheit prueft, wuerde eine
    Rueckkehr zur Positionslogik nicht bemerken.
  * **Leere Herkunft ist ein eigener Fall.** `session_turn_store` sagt: leer
    heisst *unbekannt* und nicht *vom Nutzer*. Der Verlauf muss das sagen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from memory.session import (
    HERKUNFT_EIGENER_IMPULS,
    Verlaufsbeitrag,
    fenster_waehlen,
    format_session_turns_numbered,
    sprecher_bezeichnen,
    verlauf_gruppieren,
)


def _turn(rolle: str, inhalt: str, herkunft: str = "nutzer_turn", **rest) -> dict:
    """Ein gespeicherter Turn in der Form, die `session_turn_store` schreibt."""
    return {"rolle": rolle, "inhalt": inhalt, "herkunft": herkunft, **rest}


#: Die **Abfolge** des Betriebsfalls vom 24.08.2026, mit synthetischem Inhalt.
#: Traeger des Zeugen ist die Reihenfolge — Antwort, Impuls, Nachfrage —, nicht
#: der Wortlaut; der gehoert nicht in ein veroeffentlichtes Repositorium.
VORSCHLAG: str = "Wir koennten das Ganze einmal von hinten aufrollen."

BETRIEBSFALL: list[dict] = [
    _turn("user",      "Das passt gut zusammen."),
    _turn("assistant", "Und wie weit sollen wir damit gehen?"),
    _turn("assistant", VORSCHLAG, herkunft=HERKUNFT_EIGENER_IMPULS),
    _turn("user",      "Womit denn?"),
]


class KeinTurnFaelltAusTest(unittest.TestCase):
    """Die Zusicherung, die den Zweck prueft: nichts verschwindet."""

    def test_jeder_turn_mit_inhalt_erreicht_genau_eine_gruppe(self) -> None:
        gruppen = verlauf_gruppieren(BETRIEBSFALL)
        self.assertEqual(sum(len(g) for g in gruppen), len(BETRIEBSFALL))

    def test_der_impuls_steht_im_formatierten_verlauf(self) -> None:
        aus = format_session_turns_numbered(BETRIEBSFALL, max_turns=10, max_chars=500)
        self.assertIn(VORSCHLAG, aus)

    def test_ein_impuls_am_ende_geht_nicht_verloren(self) -> None:
        """Der Impuls ohne folgenden Nutzer-Turn — er hat keinen Partner."""
        turns = [_turn("assistant", "Mir faellt gerade etwas ein.",
                       herkunft=HERKUNFT_EIGENER_IMPULS)]
        gruppen = verlauf_gruppieren(turns)
        self.assertEqual(sum(len(g) for g in gruppen), 1)
        self.assertIn("Mir faellt gerade etwas ein.",
                      format_session_turns_numbered(turns, max_chars=500))

    def test_zwei_impulse_hintereinander_bleiben_zwei(self) -> None:
        turns = [
            _turn("assistant", "Erster Gedanke.", herkunft=HERKUNFT_EIGENER_IMPULS),
            _turn("assistant", "Zweiter Gedanke.", herkunft=HERKUNFT_EIGENER_IMPULS),
        ]
        gruppen = verlauf_gruppieren(turns)
        self.assertEqual(len(gruppen), 2)
        self.assertEqual(sum(len(g) for g in gruppen), 2)

    def test_ein_turn_ohne_inhalt_ist_der_einzige_der_entfaellt(self) -> None:
        turns = [_turn("user", ""), _turn("user", "Da bin ich.")]
        self.assertEqual(sum(len(g) for g in verlauf_gruppieren(turns)), 1)


class DerSprecherKommtAusDemFeldTest(unittest.TestCase):
    """Gegen eine Rueckkehr zur Positionslogik gehaertet."""

    def test_gleiche_position_verschiedene_herkunft_verschiedener_name(self) -> None:
        """Der eigentliche Riegel: Position identisch, Bezeichnung verschieden."""
        antwort = Verlaufsbeitrag(sprecher="nova", inhalt="x", aus_eigenem_antrieb=False)
        impuls  = Verlaufsbeitrag(sprecher="nova", inhalt="x", aus_eigenem_antrieb=True)
        self.assertNotEqual(sprecher_bezeichnen(antwort), sprecher_bezeichnen(impuls))

    def test_der_impuls_ist_als_eigener_antrieb_gekennzeichnet(self) -> None:
        aus = format_session_turns_numbered(BETRIEBSFALL, max_turns=10, max_chars=500)
        zeile = next(z for z in aus.split("\n") if VORSCHLAG in z)
        self.assertIn("von sich aus", zeile)

    def test_der_impuls_steht_nicht_auf_dem_platz_des_nutzers(self) -> None:
        aus = format_session_turns_numbered(BETRIEBSFALL, max_turns=10, max_chars=500)
        zeile = next(z for z in aus.split("\n") if VORSCHLAG in z)
        self.assertNotIn("USER", zeile)

    def test_leere_herkunft_heisst_unbekannt_und_nicht_auf_zuruf(self) -> None:
        ohne = Verlaufsbeitrag(sprecher="nova", inhalt="x", herkunft_bekannt=False)
        self.assertIn("unbekannt", sprecher_bezeichnen(ohne))

    def test_eine_normale_antwort_traegt_keinen_zusatz(self) -> None:
        antwort = Verlaufsbeitrag(sprecher="nova", inhalt="x")
        self.assertEqual(sprecher_bezeichnen(antwort), "NOVA")

    def test_emotion_und_anlass_stehen_in_einer_klammer(self) -> None:
        impuls = Verlaufsbeitrag(sprecher="nova", inhalt="x", aus_eigenem_antrieb=True)
        wer = sprecher_bezeichnen(impuls, zusatz="begeisterung")
        self.assertEqual(wer.count("("), 1)
        self.assertIn("von sich aus", wer)
        self.assertIn("begeisterung", wer)


class DerBetriebsfallTest(unittest.TestCase):
    """Die Abfolge, die den Defekt erzeugt hat — als Ganzes."""

    def test_die_nutzerfrage_folgt_sichtbar_auf_novas_vorschlag(self) -> None:
        aus = format_session_turns_numbered(BETRIEBSFALL, max_turns=10, max_chars=500)
        zeilen = aus.split("\n")
        i_impuls = next(i for i, z in enumerate(zeilen) if VORSCHLAG in z)
        i_frage  = next(i for i, z in enumerate(zeilen) if "Womit denn?" in z)
        self.assertLess(i_impuls, i_frage)

    def test_impuls_und_nutzerfrage_stehen_in_verschiedenen_gruppen(self) -> None:
        """Sonst laese sich die Frage als Teil desselben Beitrags."""
        aus = format_session_turns_numbered(BETRIEBSFALL, max_turns=10, max_chars=500)
        nummer = {}
        for z in aus.split("\n"):
            if VORSCHLAG in z:
                nummer["impuls"] = z.split("]")[0]
            if "Womit denn?" in z:
                nummer["frage"] = z.split("]")[0]
        self.assertNotEqual(nummer["impuls"], nummer["frage"])


class AlleRendererNennenDenAnlassTest(unittest.TestCase):
    """Sieben Renderer lesen den Verlauf — vier reichten nicht.

    Die zweite Kontrolle suchte am 24.08.2026 **alle** Verlaufs-Renderer des
    Baums statt der zwei, an denen der Defekt auffiel. Drei weitere trugen
    zwar jeden Turn (kein Verlust), nannten aber den **Anlass** nicht: Sie
    schrieben `ASSISTANT:` / `Nova:` / `{"role": "assistant"}` und machten
    damit einen Eigen-Impuls von einer Antwort ununterscheidbar.
    Person-eindeutig, Anlass unbekannt.

    Diese Zeugen halten die Kennzeichnung an allen dreien fest. Sie pruefen
    **beides**: dass kein Turn fehlt UND dass der Impuls kenntlich ist — eine
    Rueckkehr zu `rolle`-allein wuerde die zweite Haelfte rot machen, ohne die
    erste zu beruehren.
    """

    def test_kontext_formatierung_nennt_den_anlass(self) -> None:
        from memory.kontext import _turns_formatieren
        aus = _turns_formatieren(BETRIEBSFALL)
        self.assertIn(VORSCHLAG, aus)
        self.assertIn("von sich aus", aus)

    def test_kontext_formatierung_verliert_keinen_turn(self) -> None:
        from memory.kontext import _turns_formatieren
        aus = _turns_formatieren(BETRIEBSFALL)
        for turn in BETRIEBSFALL:
            self.assertIn(turn["inhalt"], aus)

    def test_der_verfasser_verlauf_nennt_den_anlass(self) -> None:
        from graph.nodes.verfasser import VERFASSER_WORTWECHSEL
        gruppen = fenster_waehlen(verlauf_gruppieren(BETRIEBSFALL), VERFASSER_WORTWECHSEL)
        zeilen = [f"{sprecher_bezeichnen(b, nova_name='Nova')}: {b.inhalt}"
                  for g in gruppen for b in g]
        block = "\n".join(zeilen)
        self.assertIn(VORSCHLAG, block)
        self.assertIn("Nova (von sich aus)", block)

    def test_der_verfasser_verlauf_verliert_keinen_turn(self) -> None:
        from graph.nodes.verfasser import VERFASSER_WORTWECHSEL
        gruppen = fenster_waehlen(verlauf_gruppieren(BETRIEBSFALL), VERFASSER_WORTWECHSEL)
        self.assertEqual(sum(len(g) for g in gruppen), len(BETRIEBSFALL))

    def test_der_impuls_steht_in_keiner_assistant_nachricht(self) -> None:
        """Der Grund fuer den Textblock: kein Marker in Novas eigenem Mund.

        Ein Praefix im Inhalt einer `assistant`-Nachricht ist Iteration 1 aus
        `novaberg-pixie_l_kontamination.md` — das Modell schrieb den Marker
        damals mit. Im Textblock steht er in der Sprecherzeile, also im
        Rahmen.
        """
        beitrag = Verlaufsbeitrag(sprecher="nova", inhalt=VORSCHLAG,
                                  aus_eigenem_antrieb=True)
        self.assertNotIn("von sich aus", beitrag.inhalt)


class DerImpulsVerdraengtDenNutzerNichtTest(unittest.TestCase):
    """Die Kehrseite der Behebung — sie war einen Zug lang gebaut.

    `max_turns` hiess bis zum 24.08.2026 *Turn-Paare*, und ein Impuls zaehlte
    gar nicht, weil er uebersprungen wurde. Zaehlt danach **jede** Gruppe, kehrt
    sich der behobene Defekt um: Der Impuls faellt nicht mehr aus dem Verlauf,
    aber er schiebt den Nutzer aus dem Fenster derer, die nur fuenf Einheiten
    sehen. Acht der neun Aufrufer uebergeben unveraendert `5`.

    Gefunden hat es die zweite Kontrolle, indem sie die echte Session Zustand
    fuer Zustand nachfuhr — bei n=13 stand dort ein Verlauf aus fuenf
    aufeinanderfolgenden Impulsen und **keinem Wort des Nutzers**.
    """

    def _wechsel(self, anzahl: int, impulse_dazwischen: int) -> list[dict]:
        turns: list[dict] = []
        for i in range(anzahl):
            turns.append(_turn("user", f"Frage {i}"))
            turns.append(_turn("assistant", f"Antwort {i}"))
            for j in range(impulse_dazwischen):
                turns.append(_turn("assistant", f"Impuls {i}.{j}",
                                   herkunft=HERKUNFT_EIGENER_IMPULS))
        return turns

    def test_fuenf_impulse_verdraengen_keinen_wortwechsel(self) -> None:
        turns = self._wechsel(anzahl=5, impulse_dazwischen=1)
        aus = format_session_turns_numbered(turns, max_turns=5, max_chars=99)
        self.assertEqual(sum(1 for z in aus.split("\n") if "] USER" in z), 5)

    def test_das_fenster_ist_nie_ohne_nutzer_wenn_es_einen_gab(self) -> None:
        """Der Zustand, den die zweite Kontrolle fand: n=13, null Nutzer."""
        turns = self._wechsel(anzahl=1, impulse_dazwischen=8)
        aus = format_session_turns_numbered(turns, max_turns=5, max_chars=99)
        self.assertIn("] USER", aus)

    def test_impulse_zwischen_zwei_wortwechseln_bleiben_drin(self) -> None:
        turns = self._wechsel(anzahl=2, impulse_dazwischen=2)
        aus = format_session_turns_numbered(turns, max_turns=5, max_chars=99)
        self.assertEqual(aus.count("von sich aus"), 4)

    def test_max_turns_zaehlt_wortwechsel_nicht_gruppen(self) -> None:
        gruppen = verlauf_gruppieren(self._wechsel(anzahl=6, impulse_dazwischen=1))
        gewaehlt = fenster_waehlen(gruppen, 3)
        mit_nutzer = sum(1 for g in gewaehlt if any(b.sprecher == "user" for b in g))
        self.assertEqual(mit_nutzer, 3)

    def test_null_liefert_ein_leeres_fenster(self) -> None:
        gruppen = verlauf_gruppieren(self._wechsel(anzahl=3, impulse_dazwischen=0))
        self.assertEqual(fenster_waehlen(gruppen, 0), [])

    def test_ein_verlauf_nur_aus_impulsen_geht_nicht_verloren(self) -> None:
        """Ohne Wortwechsel gibt es nichts zu zaehlen — trotzdem nichts wegwerfen."""
        turns = [_turn("assistant", f"Impuls {i}", herkunft=HERKUNFT_EIGENER_IMPULS)
                 for i in range(4)]
        aus = format_session_turns_numbered(turns, max_turns=5, max_chars=99)
        self.assertEqual(aus.count("von sich aus"), 4)


if __name__ == "__main__":
    unittest.main()
