"""Tests: Der Verfasser sieht die Lage in jedem Turn.

Ziel: Der `[GESPRAECHSVEKTOR]`-Block haengt an der **Landschaft**, nicht an
der Hypothese. Wo nicht vorausgedacht wurde, steht die Landschaft trotzdem —
und der Block sagt an, dass Strategie und Leitgedanke fehlen.

Hintergrund, gemessen am 13.08.2026 ueber einen Tag Serverlog:

    Verfasser-Laeufe                 26
      mit [GESPRAECHSVEKTOR]         11
      ohne                           15   (58 %)

In allen 26 verwies der Auftrag viermal auf den Block — er steht ja im
Prompttext, ob der Abschnitt darunter kommt oder nicht. Dieselbe Klasse wie
die Saetze ueber Gedaechtnis und Internetzugang, die aus dem Responder
entfernt wurden: Eine Anweisung zu einer Quelle, die nicht im Prompt steht,
ist wirkungslos oder eine Aufforderung zum Erfinden
(`novaberg-fundliste.md`, 2026-08-14).

Zeugen dieser Datei:
  * **Die Erwartung stammt aus dem GV-Node, nicht aus dem Verfasser.**
    `_gv_detail_bauen` sichert zu, dass `cluster` auf **jedem** Weg steht;
    dass der Verbraucher sie trotzdem wegwirft, folgt daraus nicht.
  * **Der Ausfall wird an seiner Ansage geprueft, nicht an seiner Leere.**
    Ein Block ohne Strategie und ohne Satz darueber waere von einem Turn mit
    Strategie nicht zu unterscheiden: Ein Wert allein kann den Unterschied
    nicht tragen, es braucht ein zweites Feld.
  * **Die Marke `vorausdenken` traegt den Unterschied, nicht der leere
    Strategie-String.** `korridor_pruefen` leert die Strategie auch auf einem
    Turn, der vorausgedacht hat; beide Faelle stehen unten getrennt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes import verfasser as verf_mod

# Von Hand uebertragen statt importiert: Aendert sich die Marke im GV-Node,
# soll das hier auffallen und nicht stillschweigend mitwandern.
GELAUFEN: str = "gelaufen"
SKIP:     str = "skip"


def _state(**felder: object) -> dict:
    """Ein Zustand, wie ihn der Verfasser liest."""
    basis: dict = {
        "user_prompt":      "Wie entsteht ein Gammablitz?",
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "web_context": "",
        "session_turns":    [], "task_block": "",
        "event_payload":    {}, "event_source": "user",
        "gespraechsvektor": "", "gv_detail": {},
    }
    basis.update(felder)
    return basis


def _ohne_vorausdenken() -> dict:
    """Der Turn, der 15 von 26 Laeufen ausmachte: Landschaft, sonst nichts.

    Die Feldmenge ist die von `_gv_detail_bauen` auf dem Skip-Weg — Landschaft
    belegt, Antizipations-Haelfte leer, `vorausdenken` als Begleitfeld.
    """
    return _state(
        gespraechsvektor="",
        gv_detail={
            "cluster": "werkstatt", "strategie": "", "vehikel": "",
            "impuls": "", "vorausdenken": SKIP,
        },
    )


class DieLandschaftStehtAuchOhneVorausdenkenTest(unittest.TestCase):
    """Der Defekt: Die Hypothese war das Tor fuer die ganze Lage."""

    def test_der_block_steht(self) -> None:
        """Geprueft am Abschnitt, nicht am Namen.

        `assertIn("[GESPRAECHSVEKTOR]", prompt)` waere hier gruen gewesen,
        **auch mit der alten Bauart** — der Auftrag nennt den Block ja. Genau
        diese Verwechslung hat den Befund am 14.08.2026 zuerst verdeckt und
        ist der Gegenprobe dieses Tests noch einmal aufgefallen.
        """
        block: str = verf_mod._gespraechsvektor_block(_ohne_vorausdenken())

        self.assertTrue(block.startswith("[GESPRAECHSVEKTOR]\n"))

    def test_die_landschaft_steht_darin(self) -> None:
        """Nicht nur die Ueberschrift — sonst waere ein leerer Block gruen."""
        prompt: str = verf_mod._build_system_prompt(_ohne_vorausdenken())

        self.assertIn("Gespraechslandschaft: Werkstatt", prompt)

    def test_der_ausfall_wird_angesagt(self) -> None:
        """Eine weggelassene Vorgabe ist die Vorgabe des Vorgabewerts."""
        prompt: str = verf_mod._build_system_prompt(_ohne_vorausdenken())

        self.assertIn("wurde nicht vorausgedacht", prompt)

    def test_keine_strategie_wird_erfunden(self) -> None:
        """Der Block behauptet kein Mittel, das der GV-Node nicht gewaehlt hat."""
        prompt: str = verf_mod._build_system_prompt(_ohne_vorausdenken())

        self.assertNotIn("Die gewaehlte Strategie", prompt)


class DerVolleTurnBleibtVollTest(unittest.TestCase):
    """Der positive Zwilling. Ohne ihn waere auch ein verstuemmelter Block gruen."""

    def _voll(self) -> str:
        return verf_mod._build_system_prompt(_state(
            gespraechsvektor="Das Gespraech vertieft ein Sachthema.",
            gv_detail={
                "cluster": "werkstatt", "strategie": "vertiefen",
                "vehikel": "aussage", "impuls": "Bezug zur Supernova",
                "vorausdenken": GELAUFEN,
            },
        ))

    def test_strategie_und_vehikel_stehen(self) -> None:
        prompt: str = self._voll()

        self.assertIn("Die gewaehlte Strategie", prompt)
        self.assertIn("Aussage", prompt)

    def test_hypothese_und_leitgedanke_stehen(self) -> None:
        prompt: str = self._voll()

        self.assertIn("Das Gespraech vertieft ein Sachthema.", prompt)
        self.assertIn("Bezug zur Supernova", prompt)

    def test_kein_ausfall_wird_gemeldet(self) -> None:
        """Die Ansage steht nur da, wo sie zutrifft."""
        prompt: str = self._voll()

        self.assertNotIn("wurde nicht vorausgedacht", prompt)
        self.assertNotIn("steht kein Mittel fest", prompt)


class DieGeleerteStrategieIstEinDritterFallTest(unittest.TestCase):
    """Vorausgedacht, aber ohne Mittel — `korridor_pruefen` hat es geleert.

    Der leere Strategie-String allein kann den Unterschied zum Skip nicht
    tragen. Das ist genau die Lage, fuer die `vorausdenken` als Begleitfeld
    gebaut wurde.
    """

    def _geleert(self) -> str:
        return verf_mod._build_system_prompt(_state(
            gespraechsvektor="Das Gespraech sucht einen Halt.",
            gv_detail={
                "cluster": "beichte", "strategie": "", "vehikel": "",
                "impuls": "", "vorausdenken": GELAUFEN,
            },
        ))

    def test_er_wird_nicht_als_fehlendes_vorausdenken_gemeldet(self) -> None:
        prompt: str = self._geleert()

        self.assertNotIn("wurde nicht vorausgedacht", prompt)

    def test_aber_das_fehlende_mittel_wird_gemeldet(self) -> None:
        prompt: str = self._geleert()

        self.assertIn("steht kein Mittel fest", prompt)


class OhneLandschaftKeinBlockTest(unittest.TestCase):
    """Die Gegenprobe: Der Block wird nicht bedingungslos gebaut.

    Vor dem ersten Turn gibt es keine Lage. Ein Block mit leerer Landschaft
    waere eine Ueberschrift ohne Aussage — und der Auftrag zeigte wieder ins
    Leere, nur diesmal sichtbar.
    """

    def test_leeres_detail_ergibt_keinen_block(self) -> None:
        """Geprueft wird der Bauteil, nicht der Prompt.

        Im ganzen Prompt kaeme `[GESPRAECHSVEKTOR]` ohnehin vor — der Auftrag
        verweist darauf. Genau diese Verwechslung hat den Befund am
        14.08.2026 zunaechst verdeckt: Eine Suche ueber den Prompt fand den
        Namen in **26 von 26** Laeufen und den Abschnitt in 11.
        """
        self.assertEqual("", verf_mod._gespraechsvektor_block(
            _state(gv_detail={})))

    def test_fehlendes_detail_ergibt_keinen_block(self) -> None:
        """`None` statt `{}` — derselbe Fall, andere Schreibweise."""
        self.assertEqual("", verf_mod._gespraechsvektor_block(
            _state(gv_detail=None)))

    def test_hypothese_ohne_landschaft_ergibt_keinen_block(self) -> None:
        """Der Fall, den die alte Bauart als einzigen kannte — jetzt umgekehrt."""
        self.assertEqual("", verf_mod._gespraechsvektor_block(_state(
            gespraechsvektor="Eine Hypothese ohne Lage.", gv_detail={})))


if __name__ == "__main__":
    unittest.main()
