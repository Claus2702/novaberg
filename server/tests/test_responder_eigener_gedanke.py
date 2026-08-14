"""Tests fuer die Herkunft des Reizes im Responder-Prompt.

Ziel: Nova nimmt einen Pixie-Impuls als ihren eigenen Gedanken wahr — nicht
als Aeusserung des Nutzers.

Gemessen am 26.07.2026: Auf einen eigenen Impuls antwortete sie mit „Deine
Synthese ist absolut brillant — du schlaegst hier eine Bruecke…". Der Reiz
reist auf dem user_prompt-Platz, und ohne Marker liest der Responder ihn als
fremde Aeusserung.

Abgegrenzt wird gegen den Thinker-Retry: der traegt dieselbe event_source,
wiederholt aber eine echte Nutzer-Aeusserung und darf den Block NICHT bekommen.
"""

import unittest

from graph.nodes.responder import _build_system_prompt
from graph.reiz import reiz_ist_eigener_gedanke

MARKER: str = "[EIGENER GEDANKE]"

# Die Koepfe des Lageblocks, nachgezogen am 13.08.2026 mit dem Umbau auf die
# Drehbuch-Gliederung. **Die Aussage ist dieselbe geblieben** — beim eigenen
# Impuls traegt `external` eine Kopie von `internal`, und der Block muss
# sagen, wessen Werte darunter stehen. Nur die Ueberschriften heissen jetzt
# nach den Personen statt nach der Funktion.
KOPF_EIGEN: str = "[PERSON A — WIE SIE GERADE DA IST]"
KOPF_FREMD: str = "[PERSON B — WIE ER GERADE DA IST]"


def _state(payload: dict | None = None, event_source: str = "user") -> dict:
    """Minimaler ConversationState, wie ihn der Responder liest."""
    return {
        "user_prompt":      "Ein Reiz.",
        "event_source":     event_source,
        "event_payload":    payload if payload is not None else {},
        "external":         None,
        "internal":         None,
        "task_block":       "",
        "emotions_verlauf": [],
        "user_intentionen": [],
        "gv_hypothese":     "",
        # Der Prompt-Bau greift auf diese beiden direkt zu, nicht ueber .get()
        "memory_context":   "",
        "web_context":      "",
    }


class ReizHerkunftTest(unittest.TestCase):
    """Der Marker entscheidet, nicht die event_source.

    Die Funktion liegt seit dem 13.08.2026 in `graph/reiz.py` — beide Stufen
    brauchen sie, und ein Schutz, den nur die zweite kennt, greift ins Leere,
    sobald die erste den Text schreibt (`VERFASSER-KENNT-DIE-QUELLE-NICHT`).
    Diese Klasse prueft sie weiter von hier aus, weil der Responder ihr
    aeltester Leser ist; die Zwillinge fuer den Verfasser stehen in
    `test_verfasser_herkunft.py`.
    """

    def test_eigener_impuls_wird_erkannt(self):
        self.assertTrue(reiz_ist_eigener_gedanke(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        ))

    def test_nutzer_turn_ist_kein_eigener_gedanke(self):
        self.assertFalse(reiz_ist_eigener_gedanke(_state()))

    def test_thinker_retry_ist_kein_eigener_gedanke(self):
        """Gleiche event_source, aber eine wiederholte NUTZER-Aeusserung."""
        self.assertFalse(reiz_ist_eigener_gedanke(
            _state({"thinker_unsicher_retry": True, "turn_id": "t-1"},
                   event_source="character")
        ))

    def test_fehlender_payload_gilt_als_fremd(self):
        zustand = _state()
        zustand["event_payload"] = None
        self.assertFalse(reiz_ist_eigener_gedanke(zustand))


class ResponderPromptTest(unittest.TestCase):
    """Der Block steht im Prompt — und nur dann, wenn er hingehoert."""

    def test_impuls_bekommt_den_block(self):
        prompt: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        self.assertIn(MARKER, prompt)

    def test_nutzer_turn_bekommt_den_block_nicht(self):
        prompt: str = _build_system_prompt(_state())
        self.assertNotIn(MARKER, prompt)

    def test_thinker_retry_bekommt_den_block_nicht(self):
        prompt: str = _build_system_prompt(
            _state({"thinker_unsicher_retry": True}, event_source="character")
        )
        self.assertNotIn(MARKER, prompt)

    def test_kommunikations_kopf_nennt_den_richtigen_traeger(self):
        """external ist beim Impuls eine Kopie von internal (db_zugriff)."""
        eigen: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        fremd: str = _build_system_prompt(_state())

        self.assertIn(KOPF_EIGEN, eigen)
        self.assertNotIn(KOPF_FREMD, eigen)
        self.assertIn(KOPF_FREMD, fremd)
        self.assertNotIn(KOPF_EIGEN, fremd)

    def test_der_block_fuehrt_die_zuschreibung_um(self):
        """Der gemessene Defekt war eine Zuschreibung — der Block adressiert sie.

        **Am 14.08.2026 umgedreht, nicht geloescht.** Bis dahin pruefte diese
        Zusicherung das Verbot woertlich („schreibt sie ihm nicht zu"). Der
        Gegenstand ist derselbe geblieben, das Mittel hat gewechselt: Der Block
        sagt jetzt, wem der Gedanke gehoert und wohin er geht, statt zu nennen,
        was nicht geschehen soll. Moeglich ist das erst, seit die Struktur die
        Zuschreibung verhindert.
        """
        prompt: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        # Bis zum Beginn des naechsten Blocks — der Block selbst enthaelt
        # Leerzeilen, ein Split auf "\n\n" wuerde ihn mittendrin abschneiden.
        block: str = prompt.split(MARKER, 1)[1].split("\n\n[", 1)[0]
        # Seit dem 13.08.2026 in dritter Person: „du" ist im Prompt der
        # Schauspieler, ueber Person A wird gesprochen.
        self.assertIn("SIE TEILT EINEN EINFALL", block)
        self.assertIn("SIE WENDET SICH IHM ZU", block)
        self.assertIn("IHRER", block)

    def test_der_block_traegt_kein_verbot_mehr(self) -> None:
        """Ergaenzen statt ersetzen waere der fuenfte Anlauf in neuer Kleidung."""
        prompt: str = _build_system_prompt(
            _state({"reiz_herkunft": "eigener_impuls"}, event_source="character")
        )
        block: str = prompt.split(MARKER, 1)[1].split("\n\n[", 1)[0]

        for verbot in ("schreibt sie ihm nicht zu", "dankt ihm nicht",
                       "lobt ihn nicht"):
            with self.subTest(verbot=verbot):
                self.assertNotIn(verbot, block)

    def test_beide_prompts_bleiben_im_blockschema(self):
        for payload, name in (({"reiz_herkunft": "eigener_impuls"}, "impuls"),
                              ({}, "nutzer")):
            with self.subTest(fall=name):
                prompt: str = _build_system_prompt(_state(payload, "character"))
                # Seit dem 13.08.2026 heissen die Bloecke nach den Personen:
                # `[ROLLE]` fuehrt die Konstellation ein, `[PERSON A — …]`
                # und `[PERSON B — …]` tragen, was vorher `[IDENTITAET]` und
                # `[KOMMUNIKATION]` hiessen. Das Schema selbst — ein Name in
                # eckigen Klammern je Block — gilt unveraendert.
                self.assertIn("[ROLLE]", prompt)
                self.assertIn("[SZENE]", prompt)
                self.assertIn("[PERSON A — WER SIE IST]", prompt)
                # [REGELN] steht seit dem 31.07.2026 zur Probe nicht mehr
                # im Prompt — die Regeln waren Narben des ueberladenen
                # Prompts, und die Ursache ist seit der Trennung von Inhalt
                # und Form weg. Wird der Block zurueckgeholt, gehoert diese
                # Zeile mit ihm zurueck.
                self.assertNotIn("[REGELN]", prompt)


if __name__ == "__main__":
    unittest.main()
