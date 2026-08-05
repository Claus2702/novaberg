"""Tests: Der NachfragenAgent legt nur bei aktuellem Druck einen Reiz ab.

Ziel des Bauteils (novaberg-pixie-nachfragen_k.md §8.6): Steht der Nutzer beim
Lauf unter Druck, hinterlaesst ein `nachfragen`-Auftrag genau einen
Stapel-Eintrag mit `aufgabe="nachfragen"`; steht er nicht mehr unter Druck,
hinterlaesst er keinen und einen Audit-Eintrag mit dem Grund.

Zeugen dieser Datei:
  * **Die Vektornamen sind Literale**, aus dem Konzept und aus
    `ei/berechnung.py` uebernommen — nicht aus den Konstanten, gegen die der
    Agent prueft. Wer `EMOTIONS_VEKTOREN_DRUCK` importierte und dagegen
    testete, vergliche die Konstante mit sich selbst: Beide Seiten treffen
    sich, bevor sie durch das Prueflobjekt gelaufen sind.
  * **Geprueft wird, was an den Stapel geht** — der Agent gibt einen Zustand
    zurueck, aber seine Wirkung ist der Aufruf von `stack_push`.
  * **Der Anlass ist ein Literal im Auftrag** und wird im Reiz wiedergefunden.
  * Die Aufgabenkennung `nachfragen` steht hier als Literal, weil die
    Zustellung sie als Literal vergleicht. Eine Konstante auf beiden Seiten
    wuerde eine Umbenennung mitmachen, die den Agenten unsichtbar macht.

Negativ-Zusicherungen haben ihren positiven Zwilling: Zu jedem Test, der
**keinen** Stapel-Eintrag erwartet, steht einer mit derselben Bauart, der
genau einen erwartet.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from agents.nachfragen.agent import NachfragenAgent

USER: str = "testnutzer"

# Aus dem Konzept, nicht aus der Konstante des Prueflings.
DRUCK_VEKTOREN: tuple[str, ...] = ("absturz", "spirale", "einbruch")
RUHIGE_VEKTOREN: tuple[str, ...] = (
    "plateau", "stabilisierung", "erholung", "aufbluehen",
    "eskalation", "abkuehlung",
)

ANLASS: str = "Der Waermetod des Universums beschaeftigt ihn seit Tagen."
THEMA: str = "Waermetod, Entropie"


def _turn(vektor: str, *, rolle: str = "user") -> str:
    """Baut einen annotierten Session-Turn als Redis-Rohsatz."""
    return json.dumps({
        "rolle":              rolle,
        "inhalt":             "…",
        "emotion":            "traurigkeit",
        "arousal":            0.8,
        "emotions_vektor":    vektor,
        "beziehungs_dynamik": "hilfesuchend",
        "modus":              "emotional",
    })


def _auftrag(thema: str = THEMA, kontext: str = ANLASS) -> dict:
    """Baut einen Queue-Auftrag, wie ihn die Shadow-Queue traegt."""
    return {
        "aufgabe":  "nachfragen",
        "user_id":  USER,
        "thema":    thema,
        "kontext":  kontext,
        "erstellt": "2026-07-27T20:14:42.520339",
    }


def _state(auftrag: dict) -> dict:
    """Baut den AgentState, wie ihn der Pixie-Dispatch uebergibt."""
    return {
        "aufgabe":    "nachfragen",
        "aufgabe_typ": "workflow",
        "agent_name": "nachfragen",
        "kontext":    {"user_id": USER},
        "parameter":  auftrag,
        "schritte":   [],
        "ergebnis":   None,
        "status":     "laufend",
        "rueckfrage": None,
        "fehler":     None,
    }


class NachfragenAgentTest(unittest.TestCase):
    """Der Agent legt genau dann ab, wenn aktuell Druck herrscht."""

    def setUp(self) -> None:
        """Ein frischer Agent je Test — er haelt keinen Zustand."""
        self.agent = NachfragenAgent()

    def _lauf(
        self,
        saetze: list[str],
        auftrag: dict | None = None,
    ) -> tuple[dict, MagicMock, MagicMock]:
        """Fuehrt einen Durchlauf mit gegebenen Session-Turns aus.

        Gibt (state, stack_push_mock, audit_mock) zurueck.
        """
        redis = MagicMock()
        redis.lrange.return_value = saetze

        with patch("agents.nachfragen.agent.redis_client", redis), \
             patch("agents.nachfragen.agent.stack_push") as push, \
             patch.object(NachfragenAgent, "_audit_log") as audit:
            state = self.agent.invoke(_state(auftrag or _auftrag()))

        return state, push, audit

    # ── Druck: genau ein Eintrag ────────────────

    def test_druckvektor_legt_genau_einen_eintrag_ab(self) -> None:
        """Jeder der drei Druck-Vektoren erzeugt einen Stapel-Eintrag."""
        for vektor in DRUCK_VEKTOREN:
            with self.subTest(vektor=vektor):
                state, push, _ = self._lauf([_turn(vektor)])

                self.assertEqual(1, push.call_count)
                self.assertEqual("abgeschlossen", state["status"])
                self.assertTrue(state["ergebnis"]["abgelegt"])

    def test_eintrag_traegt_die_aufgabenkennung_nachfragen(self) -> None:
        """Die Zustellung vergleicht genau diese Zeichenkette."""
        _, push, _ = self._lauf([_turn("absturz")])

        self.assertEqual("nachfragen", push.call_args.kwargs["aufgabe"])

    def test_reiz_traegt_lage_und_anlass(self) -> None:
        """Ohne Anlass wuesste Nova nicht, worum sie sich sorgt."""
        _, push, _ = self._lauf([_turn("absturz")])
        reiz: str = push.call_args.kwargs["inhalt"]

        # Der Satz zum Vektor stammt aus ei/farbton.py und steht hier als
        # Literal — er ist der Zeuge, nicht eine zweite Ableitung.
        self.assertIn("Die Stimmung ist eingebrochen.", reiz)
        self.assertIn(ANLASS, reiz)

    def test_reiz_adressiert_niemanden(self) -> None:
        """Ein an den Nutzer gerichteter Satz waere die falsche Bauart.

        Der Reiz geht als `user_prompt` in den AgentGraph. Eine Anrede
        darin liesse Nova darauf reagieren, als haette jemand sie ihr
        gesagt — der Defekt, den der Zustellungspfad fuer sich behoben hat.
        """
        _, push, _ = self._lauf([_turn("absturz")])
        reiz: str = push.call_args.kwargs["inhalt"]

        self.assertNotIn("?", reiz)
        for anrede in ("du ", "dir ", "dich ", "Du ", "Dir ", "Dich "):
            with self.subTest(anrede=anrede):
                self.assertNotIn(anrede, reiz)

    # ── Kein Druck: kein Eintrag, aber erledigt ──

    def test_ruhiger_vektor_legt_nichts_ab(self) -> None:
        """Der haeufigste Ausgang bei einem alten Auftrag."""
        for vektor in RUHIGE_VEKTOREN:
            with self.subTest(vektor=vektor):
                state, push, _ = self._lauf([_turn(vektor)])

                self.assertEqual(0, push.call_count)
                self.assertFalse(state["ergebnis"]["abgelegt"])

    def test_kein_druck_ist_erledigt_und_kein_fehler(self) -> None:
        """Der Agent hat richtig gearbeitet und richtig geschwiegen."""
        state, _, audit = self._lauf([_turn("plateau")])

        self.assertEqual("abgeschlossen", state["status"])

        status_werte = [ruf.args[1] for ruf in audit.call_args_list]
        self.assertIn("erledigt", status_werte)
        self.assertNotIn("fehler", status_werte)

    def test_kein_druck_nennt_den_vektor_im_audit(self) -> None:
        """Ohne den Wert ist der Eintrag beim Auswerten unbrauchbar."""
        _, _, audit = self._lauf([_turn("plateau")])

        begruendungen = [ruf.args[2] for ruf in audit.call_args_list]
        self.assertTrue(
            any("plateau" in text for text in begruendungen),
            f"Vektor fehlt in den Audit-Begruendungen: {begruendungen}",
        )

    # ── Kanon: unbekannt ist nicht dasselbe wie ruhig ──

    def test_unbekannter_vektor_ist_ein_fehler(self) -> None:
        """Die Teilmengen-Falle: Muell darf nicht wie Ruhe aussehen."""
        state, push, audit = self._lauf([_turn("transportfehler")])

        self.assertEqual(0, push.call_count)
        self.assertEqual("fehler", state["status"])

        status_werte = [ruf.args[1] for ruf in audit.call_args_list]
        self.assertIn("fehler", status_werte)

    def test_unbekannter_und_ruhiger_vektor_enden_verschieden(self) -> None:
        """Der eine ist ein Defekt, der andere eine gueltige Aussage."""
        ruhig, _, _ = self._lauf([_turn("plateau")])
        muell, _, _ = self._lauf([_turn("transportfehler")])

        self.assertNotEqual(ruhig["status"], muell["status"])

    # ── Eingabe-Validierung ─────────────────────

    def test_auftrag_ohne_thema_und_kontext_ist_ein_fehler(self) -> None:
        """Ohne Anlass waere der Reiz inhaltslos."""
        state, push, _ = self._lauf(
            [_turn("absturz")], _auftrag(thema="", kontext=""),
        )

        self.assertEqual(0, push.call_count)
        self.assertEqual("fehler", state["status"])

    def test_auftrag_mit_nur_thema_genuegt(self) -> None:
        """Der positive Zwilling: eines von beiden reicht."""
        state, push, _ = self._lauf(
            [_turn("absturz")], _auftrag(kontext=""),
        )

        self.assertEqual(1, push.call_count)
        self.assertEqual("abgeschlossen", state["status"])

    def test_leere_session_ist_ein_fehler(self) -> None:
        """Kein Turn heisst nicht „kein Druck", sondern „nicht feststellbar"."""
        state, push, _ = self._lauf([])

        self.assertEqual(0, push.call_count)
        self.assertEqual("fehler", state["status"])

    def test_nur_assistant_turns_ist_ein_fehler(self) -> None:
        """Der Druck liegt auf dem Nutzer, nicht auf Nova."""
        state, push, _ = self._lauf([_turn("absturz", rolle="assistant")])

        self.assertEqual(0, push.call_count)
        self.assertEqual("fehler", state["status"])

    def test_juengster_user_turn_entscheidet(self) -> None:
        """Der Druck wird frisch gelesen — der aeltere Turn zaehlt nicht.

        Der Auftrag traegt einen Absturz von damals; die Session sagt, dass
        er vorbei ist. Zuwendung zu einem Druck, der vorbei ist, ist keine.
        """
        state, push, _ = self._lauf([_turn("absturz"), _turn("erholung")])

        self.assertEqual(0, push.call_count)
        self.assertFalse(state["ergebnis"]["abgelegt"])

    def test_juengster_user_turn_entscheidet_auch_andersherum(self) -> None:
        """Der positive Zwilling: frischer Druck nach ruhiger Phase."""
        state, push, _ = self._lauf([_turn("plateau"), _turn("absturz")])

        self.assertEqual(1, push.call_count)
        self.assertTrue(state["ergebnis"]["abgelegt"])

    # ── Audit-Pflicht ───────────────────────────

    def test_jeder_durchlauf_beginnt_mit_gestartet(self) -> None:
        """Jeder Durchlauf beginnt mit einem Start-Eintrag.

        Ohne ihn ist ein Ausfall von einem Nichtlauf nicht zu unterscheiden.
        """
        for saetze in ([], [_turn("plateau")], [_turn("absturz")]):
            with self.subTest(turns=len(saetze)):
                _, _, audit = self._lauf(saetze)

                status_werte = [ruf.args[1] for ruf in audit.call_args_list]
                self.assertEqual("gestartet", status_werte[0])
                self.assertGreaterEqual(len(status_werte), 2)


if __name__ == "__main__":
    unittest.main()
