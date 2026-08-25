"""Tests: Der Verfasser bekommt eine Aufgabe, keine Beschreibung.

Ziel: Der Auftrag nennt die Konstellation, stellt eine Aufgabe und haengt an
jeden Block, den er einfuehrt, eine pruefbare Bedingung. Der Inhalt entsteht
in **dritter Person** — der Verfasser schreibt nicht Person As Rede, sondern
was sie feststellt.

Hintergrund, gemessen am 12./13.08.2026 an sechs Prompt-Formen:

    dieselbe Vorgabe als Aufgabe        6/6 Laengenkorridore
    dieselbe Vorgabe als Beschreibung   0/6
    Aufgabe mit Pruefbedingung          5,7 Profilmerkmale
    blosse Stilnotiz                    3,0

Daraus die Bauregel: **Ein Block, den der Auftrag nicht einfuehrt, ist Kontext
— und Kontext bindet nicht.** Der alte Auftrag war eine Beschreibung der
Zustaendigkeit ohne eine einzige pruefbare Bedingung.

Zeugen dieser Datei:
  * **Die Erwartung stammt aus der Messung, nicht aus dem Prompt.** Dass eine
    Aufgabe mit Pruefbedingung bindet und eine Beschreibung nicht, ist an
    sechs Formen gegen zwei Szenen erhoben worden.
  * **Geprueft wird die Aussage, nicht der Satzbau.** Was hier festgehalten
    ist: dass beide Personen vorkommen, dass drei Bedingungen dastehen und
    dass die erste Person ausgeschlossen ist.
  * **Der Schutz des Leitgedankens steht daneben.** Er ist am 31.07.2026 live
    als tragend gemessen worden; ein Umbau des Auftrags darf ihn nicht
    nebenbei verlieren.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes import verfasser as verf_mod


def _state() -> dict:
    """Ein Zustand, wie ihn der Verfasser liest."""
    return {
        "user_prompt":      "Wie entsteht ein Gammablitz?",
        "user_id":          "u", "character_id": "c", "turn_id": "t",
        "memory_context":   "", "web_context": "",
        "session_turns":    [], "task_block": "",
        "event_payload":    {}, "event_source": "user",
        "gespraechsvektor": "", "gv_detail": {},
    }


class DieKonstellationStehtImAuftragTest(unittest.TestCase):
    """Ohne sie ist der Mensch die einzige Adresse fuer alles im Prompt.

    Genau das war die Bedingung, unter der die Zuschreibung entstand: Ein
    eigener Impuls reist auf dem Platz der Nutzereingabe, und wer nur eine
    Adresse kennt, gibt ihm diese.
    """

    def test_beide_personen_kommen_vor(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("PERSON A", prompt)
        self.assertIn("PERSON B", prompt)

    def test_der_mensch_heisst_nicht_mehr_der_nutzer(self) -> None:
        """Ein zweites Namenssystem im selben Prompt ist der gemessene Fehler.

        Am 13.08.2026 gezaehlt: In sieben von dreizehn Bloecken des Responders
        wurde geduzt, und „du" meinte drei verschiedene Personen.
        """
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertNotIn("den NUTZER", prompt)
        self.assertNotIn("der Nutzer", prompt)


class DreiPruefbareBedingungenTest(unittest.TestCase):
    """Die Form, die 6 von 6 traf — nicht die, die 0 von 6 traf."""

    def test_der_auftrag_kuendigt_die_pruefung_an(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("geprueft", prompt)

    def test_alle_drei_bedingungen_stehen(self) -> None:
        """Herkunft des Materials, gewaehltes Mittel, Mass."""
        prompt: str = verf_mod._build_system_prompt(_state())

        for bedingung in ("HERKUNFT", "MITTEL", "MASS"):
            with self.subTest(bedingung=bedingung):
                self.assertIn(bedingung, prompt)

    def test_das_mittel_zeigt_auf_den_block_der_es_traegt(self) -> None:
        """Eine Bedingung ohne Gegenstand ist keine.

        Der Auftrag verwies bis zum 14.08.2026 viermal auf
        `[GESPRAECHSVEKTOR]`; in 15 von 26 Laeufen gab es den Abschnitt nicht.
        Der Block steht seither in jedem Turn mit einer Landschaft — die
        Bedingung darf deshalb auf ihn zeigen.
        """
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("[GESPRAECHSVEKTOR]", prompt)


class DerInhaltStehtInDritterPersonTest(unittest.TestCase):
    """Die Freiheit, Person A zu sein, gehoert der zweiten Stufe."""

    def test_die_dritte_person_wird_verlangt(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("dritten Person", prompt)

    def test_die_erste_person_wird_ausgeschlossen(self) -> None:
        """Positiv **und** negativ: Die Ansage allein liesse die Wahl offen."""
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn('Kein "ich" und kein "du"', prompt)

    def test_die_form_bleibt_ausdruecklich_bei_der_zweiten_stufe(self) -> None:
        """Der positive Zwilling: Der Verfasser verliert die Stimme, nicht den
        Inhalt.
        """
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("Wesen, Waerme, Naehe, Laune und Anrede", prompt)


class DerSchutzDesLeitgedankensUeberlebtDenUmbauTest(unittest.TestCase):
    """Am 31.07.2026 live als tragend gemessen — er faellt nicht nebenbei.

    Ohne ihn formuliert niemand um: Der Verfasser uebernimmt den Leitgedanken
    woertlich, und der Responder darf den Inhalt nicht mehr aendern. Die
    Antwort an den Nutzer war damals der Hypothesentext des
    Hintergrundagenten, unveraendert durch beide Stufen.
    """

    def test_die_richtungsklausel_steht(self) -> None:
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("RICHTUNG, nicht der Text", prompt)
        self.assertIn("Schreibe ihn niemals ab", prompt)

    def test_die_begruendung_trennt_die_beiden_personen(self) -> None:
        """Der Grund ist mit der dritten Person schaerfer geworden, nicht
        schwaecher.

        Vorher trennte er „was der Nutzer tut" von „was du sagst" — zwei
        Personen und zwei Formen. Jetzt sind beide Saetze in dritter Person,
        und die Unterscheidung haengt allein am Subjekt. Genau deshalb muss
        sie im Prompt ausgeschrieben stehen.
        """
        prompt: str = verf_mod._build_system_prompt(_state())

        self.assertIn("was PERSON B tut", prompt)
        self.assertIn("was PERSON A dazu feststellt", prompt)


if __name__ == "__main__":
    unittest.main()
