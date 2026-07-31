"""Tests: Inhalt und Wesen sind getrennt.

Gegenstand ist die tragende Zusicherung des Umbaus — **der Responder sieht das
Wissen nicht mehr**. Alles andere folgt daraus: Was er nicht sieht, kann er
nicht erfinden.

Die Lehre dahinter steht im Bestand: Die Halluzination bei Agent-Erfolg
ueberlebte vier Fix-Iterationen, und die Loesung war nicht ein staerkerer
Prompt, sondern weniger Input. Bisher war das eine Fallunterscheidung
(`task_context_cut`); jetzt ist es die Bauart.

Zeugen dieser Datei:
  * Die Blocknamen `[GEDAECHTNIS]`, `[WEB-RECHERCHE]`, `[INHALT]` stammen aus
    den Prompt-Bausteinen bzw. aus dem Konzept, nicht aus dem Pruefobjekt.
  * Die Erwartung "ein Ausfall sieht nicht aus wie eine Antwort" stammt aus
    `novaberg-lesson_l_default-wie-fehlschlag.md`.
  * Die Zusicherung zum Kanal stammt aus
    `novaberg-lesson_l_stategraph-channel-zwang.md`: Ein Schreibvorgang in
    einen nicht deklarierten Kanal ist stillschweigend wirkungslos.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes import responder as resp_mod
from graph.nodes import verfasser as verf_mod
from graph.state import ConversationState


def _state(**felder: object) -> dict:
    """Baut einen State, der fuer beide Nodes ausreicht.

    Bewusst ein schlichtes Dict: Beide Nodes lesen ueber `.get`, und eine
    Attrappe, die mehr kann als noetig, verdeckt, was wirklich gebraucht wird.

    Vorbedingung: keine.
    Nachbedingung: Alle Felder, die die Pruefobjekte lesen, sind belegt.
    Fehlerfaelle: keine.

    Returns:
        Der State.
    """
    basis: dict = {
        "user_prompt":      "Wie entsteht ein Gammablitz?",
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "web_context": "",
        "session_turns":    [], "task_block": "", "task_context_cut": False,
        "gespraechsvektor": "", "gv_detail": {}, "antwort_inhalt": "",
        "emotions_verlauf": [], "nova_emotions_verlauf": [],
        "external": None, "internal": None,
    }
    basis.update(felder)
    return basis


class TestDerKanalIstDeklariert(unittest.TestCase):
    """Ein Schreibvorgang in einen unbekannten Kanal wirkt nicht."""

    def test_antwort_inhalt_steht_im_zustandsschema(self) -> None:
        """Ohne diese Zeile laeuft der Node und das Feld bleibt trotzdem leer."""
        self.assertIn("antwort_inhalt", ConversationState.__annotations__)

    def test_antwort_inhalt_wird_initialisiert(self) -> None:
        """Deklariert genuegt nicht — ein fehlender Startwert bricht `.get`-freie Leser."""
        from graph.base import GraphBase

        quelle: str = GraphBase.create_state.__code__.co_consts.__str__()
        self.assertIn("antwort_inhalt", quelle)


class TestDerResponderSiehtDasWissenNicht(unittest.TestCase):
    """Die tragende Zusicherung. Wird sie rot, ist der Umbau zurueckgenommen."""

    def test_kein_gedaechtnis_im_system_prompt(self) -> None:
        """Auch wenn der State ein volles Gedaechtnis traegt."""
        prompt: str = resp_mod._build_system_prompt(_state(
            memory_context="Der Nutzer interessiert sich fuer Astronomie.",
            antwort_inhalt="Ein Gammablitz entsteht beim Kollaps eines Sterns.",
        ))

        self.assertNotIn("[GEDAECHTNIS]", prompt)
        self.assertNotIn("Astronomie", prompt)

    def test_keine_web_recherche_im_system_prompt(self) -> None:
        """Dasselbe fuer die zweite Wissensquelle."""
        prompt: str = resp_mod._build_system_prompt(_state(
            web_context="Quelle: Gammablitze dauern Sekunden.",
            antwort_inhalt="Ein Gammablitz entsteht beim Kollaps eines Sterns.",
        ))

        self.assertNotIn("[WEB-RECHERCHE]", prompt)
        self.assertNotIn("Gammablitze dauern Sekunden", prompt)

    def test_der_inhalt_kommt_stattdessen_an(self) -> None:
        """Der positive Zwilling: Ohne ihn koennte der Prompt einfach leer sein."""
        prompt: str = resp_mod._build_system_prompt(_state(
            antwort_inhalt="Ein Gammablitz entsteht beim Kollaps eines Sterns.",
        ))

        self.assertIn("[INHALT]", prompt)
        self.assertIn("Kollaps eines Sterns", prompt)

    def test_keine_anweisung_zu_quellen_die_er_nicht_hat(self) -> None:
        """Der [IDENTITAET]-Block sprach ueber Gedaechtnis, Kontext und Web.

        Alle drei Saetze sind seit der Trennung im Verfasser. Eine Anweisung
        zu Quellen, die nicht im Prompt stehen, ist entweder wirkungslos oder
        eine Aufforderung zum Erfinden.
        """
        prompt: str = resp_mod._build_system_prompt(_state(
            antwort_inhalt="Ein Gammablitz entsteht beim Kollaps eines Sterns.",
        ))

        self.assertNotIn("Charakter-Kontext im Gedaechtnis", prompt)
        self.assertNotIn("Erwaehne nur Informationen die im Kontext stehen", prompt)
        self.assertNotIn("Internetzugang", prompt)

    def test_kein_gespraechsvektor_beim_responder(self) -> None:
        """Landschaft, Strategie und Leitgedanke gehoeren zum Inhalt.

        Standen sie zusaetzlich hier, sah der Responder denselben Leitgedanken
        ein zweites Mal — und gab ihn woertlich weiter, statt ihm eine Form zu
        geben. Live beobachtet am 31.07.2026.
        """
        prompt: str = resp_mod._build_system_prompt(_state(
            gespraechsvektor="Das Gespraech vertieft ein Sachthema.",
            gv_detail={"cluster": "resonanz", "strategie": "vertiefen",
                       "impuls": "Bezug zur Supernova"},
            antwort_inhalt="Ein Gammablitz entsteht beim Kollaps eines Sterns.",
        ))

        self.assertNotIn("[GESPRAECHSVEKTOR]", prompt)
        self.assertNotIn("Bezug zur Supernova", prompt)

    def test_das_wesen_steht_zuletzt(self) -> None:
        """Recency: Alles darueber ist Grundlage, das Wesen soll draengen."""
        from graph.personality import InternalPersonality

        # Die echte Klasse, nicht eine Attrappe: Sie kennt alle Felder, die der
        # Responder liest — eine eigene Nachbildung haette genau die Luecken,
        # die der Prompt-Bau nicht vertraegt.
        innen = InternalPersonality()
        innen.identities = ["Das kesse Maedel vom Land"]

        prompt: str = resp_mod._build_system_prompt(_state(internal=innen))

        self.assertIn("[DEIN WESEN]", prompt)
        self.assertIn("Das kesse Maedel vom Land", prompt)
        self.assertTrue(
            prompt.rstrip().endswith("- Das kesse Maedel vom Land"),
            "Das Wesen muss der letzte Block sein, sonst wirkt die Stelle nicht",
        )

    def test_ohne_eintrag_kein_wesensblock(self) -> None:
        """Eine Ueberschrift ohne Aussage nimmt der Stelle ihre Wirkung."""
        prompt: str = resp_mod._build_system_prompt(_state())

        self.assertNotIn("[DEIN WESEN]", prompt)

    def test_die_laenge_entscheidet_der_responder(self) -> None:
        """Der Umfang folgt der Lage, nicht der Vorlage.

        Laenge ist formal Stil, folgt aber aus dem Inhalt. Solange der
        Responder nichts weglassen durfte, war niemand zustaendig.

        Seit dem 31.07.2026 steht die Freigabe nicht mehr als Regel im Prompt,
        sondern gar nicht: Der Block nennt den Inhalt und ueberlaesst ihr den
        Rest. Was hier geprueft wird, ist die **Abwesenheit** der alten
        Fessel — nicht eine neue Anweisung an ihre Stelle.
        """
        prompt: str = resp_mod._build_system_prompt(_state(
            antwort_inhalt="Ein Gammablitz entsteht beim Kollaps eines Sterns.",
        ))

        self.assertIn("Sag ihn auf deine Art", prompt)
        self.assertNotIn("lass keine weg", prompt)

    def test_die_stimme_bleibt_beim_responder(self) -> None:
        """Der positive Zwilling: Die Rollenklarheit ist keine Wissensfrage."""
        prompt: str = resp_mod._build_system_prompt(_state())

        self.assertIn("Sprich als du selbst", prompt)

    def test_ohne_inhalt_kein_leerer_inhaltsblock(self) -> None:
        """Ein Block ohne Inhalt taeuscht eine Vorgabe vor, die es nicht gibt."""
        prompt: str = resp_mod._build_system_prompt(_state())

        self.assertNotIn("[INHALT]", prompt)


class TestDerVerfasserSiehtDasWissen(unittest.TestCase):
    """Die Gegenseite: Was der Responder verliert, muss hier ankommen."""

    def test_gedaechtnis_und_web_stehen_im_verfasser_prompt(self) -> None:
        """Beide Wissensquellen erreichen den Verfasser vollstaendig."""
        prompt: str = verf_mod._build_system_prompt(_state(
            memory_context="Der Nutzer interessiert sich fuer Astronomie.",
            web_context="Quelle: Gammablitze dauern Sekunden.",
        ))

        self.assertIn("[GEDAECHTNIS]", prompt)
        self.assertIn("Astronomie", prompt)
        self.assertIn("[WEB-RECHERCHE]", prompt)
        self.assertIn("Gammablitze dauern Sekunden", prompt)

    def test_der_verfasser_bekommt_keine_identitaet(self) -> None:
        """Er bestimmt den Inhalt, nicht die Form — Stil dort waere Ballast."""
        prompt: str = verf_mod._build_system_prompt(_state())

        for block in ("[IDENTITAET]", "[EIGENE_EMOTION]", "[KOMMUNIKATION]",
                      "[DIREKTIVEN]"):
            self.assertNotIn(block, prompt)

    def test_die_gewaehlte_strategie_wird_uebernommen(self) -> None:
        """Der Gespraechsvektor hat gewaehlt; der Verfasser fuehrt aus."""
        prompt: str = verf_mod._build_system_prompt(_state(
            gespraechsvektor="Das Gespraech vertieft ein Sachthema.",
            gv_detail={"cluster": "resonanz", "strategie": "vertiefen",
                       "vehikel": "aussage", "impuls": "Bezug zur Supernova"},
        ))

        self.assertIn("[GESPRAECHSVEKTOR]", prompt)
        self.assertIn("Bezug zur Supernova", prompt)

    def test_die_wissensanweisungen_sind_hier_angekommen(self) -> None:
        """Die Gegenseite zum Responder-Test: verschoben, nicht verloren."""
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("Charakter-Kontext im Gedaechtnis", prompt)
        self.assertIn("Erwaehne nur Informationen die im Kontext stehen", prompt)
        self.assertIn("Internetzugang", prompt)

    def test_der_leitgedanke_darf_nicht_abgeschrieben_werden(self) -> None:
        """Der Schutz, den ich im Konzept faelschlich fuer entbehrlich hielt.

        Ohne ihn formuliert niemand um: Der Verfasser uebernimmt den
        Leitgedanken woertlich, und der Responder darf den Inhalt nicht mehr
        aendern. Live beobachtet am 31.07.2026 — die Antwort an den Nutzer war
        der Hypothesentext des Hintergrundagenten, unveraendert durch beide
        Stufen.
        """
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("RICHTUNG, nicht der Text", prompt)
        self.assertIn("Schreibe ihn niemals ab", prompt)


class TestDerAusfallSiehtNichtWieEineAntwortAus(unittest.TestCase):
    """Kein Ersatztext, kein Rueckfall — ein leeres Ergebnis bleibt leer."""

    def test_leerer_prompt_wird_laut_gemeldet(self) -> None:
        """Ohne Frage gibt es nichts zu verfassen — laut, nicht still."""
        with self.assertLogs("ki_server.verfasser", level="ERROR") as log:
            ergebnis = verf_mod.verfassen(_state(user_prompt="   "))

        self.assertEqual("", ergebnis["antwort_inhalt"])
        self.assertIn("leerer user_prompt", "".join(log.output))

    def test_leere_modellantwort_wird_laut_gemeldet(self) -> None:
        """Das Modell antwortet, aber ohne Text. Kein Fuelltext, keine Ausrede."""
        class _Leer:
            text = "   "
            token_total = 0

        with patch.object(verf_mod.model_service.chat, "submit_sync",
                          return_value=_Leer()), \
             self.assertLogs("ki_server.verfasser", level="ERROR") as log:
            ergebnis = verf_mod.verfassen(_state())

        self.assertEqual("", ergebnis["antwort_inhalt"])
        self.assertIn("keinen Inhalt", "".join(log.output))

    def test_der_gutfall_schreibt_den_inhalt(self) -> None:
        """Der positive Zwilling zu beiden Ausfaellen."""
        class _Voll:
            text = "Ein Gammablitz entsteht beim Kollaps eines Sterns."
            token_total = 12

        with patch.object(verf_mod.model_service.chat, "submit_sync",
                          return_value=_Voll()):
            ergebnis = verf_mod.verfassen(_state())

        self.assertEqual(_Voll.text, ergebnis["antwort_inhalt"])


class TestDerKontextSchnittUmgehtDenVerfasser(unittest.TestCase):
    """Bei Agent-Erfolg bleibt der schmale Kontext schmal.

    Ein Verfasser wuerde dort Gedaechtnis und Web wieder einsammeln und
    verdichtet weiterreichen — genau den Input, dessen Entfernung die
    Halluzination beendet hat.
    """

    def _zweig(self, schnitt: bool) -> str:
        from graph.character_graph import CharacterGraph

        return CharacterGraph._after_gv(None, _state(task_context_cut=schnitt))

    def test_bei_schnitt_geht_es_direkt_zum_responder(self) -> None:
        """Mit Kontext-Schnitt bleibt der Verfasser aussen vor."""
        self.assertEqual("responder", self._zweig(True))

    def test_ohne_schnitt_laeuft_der_verfasser(self) -> None:
        """Ohne Schnitt ist der Verfasser der regulaere Weg."""
        self.assertEqual("verfasser", self._zweig(False))


class TestBeideTexteStehenImselbenRohturn(unittest.TestCase):
    """Ohne beide in einer Zeile ist der Abgleich eine Rekonstruktion."""

    def test_der_inhalt_wird_mitgeschrieben(self) -> None:
        """Der Rohturn traegt beide Texte in derselben Zeile."""
        from graph.nodes import dispatcher as disp_mod

        quelle: str = disp_mod._turn_roh_schreiben.__doc__ or ""
        self.assertIsNotNone(quelle)

        with open(disp_mod.__file__, encoding="utf-8") as datei:
            code: str = datei.read()

        self.assertIn('inhalt["antwort_inhalt"] = antwort_inhalt', code)

    def test_ein_leeres_feld_wird_nicht_geschrieben(self) -> None:
        """Ein dauerhaft leeres Feld waere von *lief nicht* nicht zu trennen."""
        from graph.nodes import dispatcher as disp_mod

        with open(disp_mod.__file__, encoding="utf-8") as datei:
            code: str = datei.read()

        self.assertIn("if antwort_inhalt:", code)


if __name__ == "__main__":
    unittest.main()
