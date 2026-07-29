"""Tests: Ein Abbruch der Urteilsreihe kostet nichts mehr.

Ziel: Ein wiederaufgenommener Lauf holt kein Urteil zweimal, wiederholt jeden
Fehlschlag und uebernimmt die Aggregate der Reihe.

Hintergrund: Eine Reihe von rund 200 Sprachmodell-Urteilen ging am 29.07.2026
durch eine einzelne Zeitueberschreitung vollstaendig verloren — sie stand nur
im Prozessspeicher. Ein Urteil kostet hier Minuten, ein Rohwert Millisekunden;
deshalb wird genau das Urteil gesichert.

Zeugen dieser Datei:
  * Die Erwartungen sind **Literale im Test**, keine Rueckgaben der geprueften
    Funktionen. Was geschrieben wurde, wird gegen das geprueft, was der Test
    hineingegeben hat — die Datei ist die zweite Quelle.
  * Die Regel „ein Fehlschlag wird wiederholt, ein Urteil nicht" ist eine
    Vorgabe an den Code und nicht aus ihm abgelesen: Ein uebersprungener
    Fehlschlag hinterlaesst eine Luecke, die aussieht wie ein Ergebnis.
  * Die Randfaelle sind aus dem **Eingaberaum** der Parameter hergeleitet, nicht
    aus den vorhandenen Pruefungen im Code. Eine Funktion, die einen Check
    vergessen hat, bekaeme sonst keinen Test — und genau sie braucht einen.

Skopus: Jeder Test benutzt einen eigenen Reihennamen und verwirft ihn am Ende.
Die Reihe `meister-nova` des Produktivlaufs wird nie angefasst — die Suite
laeuft gegen den echten Bestand.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import os
import unittest

from agents.kalibrierung.lauf import _reihenname, _zeugenkennung
from agents.kalibrierung.zwischenstand import (
    _pfad,
    aggregat_schreiben,
    fehlschlag_schreiben,
    stand_lesen,
    urteil_schreiben,
    verwerfen,
)


class ZwischenstandBasis(unittest.TestCase):
    """Gemeinsamer Skopus: eigener Reihenname je Test, danach verworfen."""

    def setUp(self) -> None:
        self.reihe: str = f"test-{self.id().rsplit('.', 1)[-1]}"
        verwerfen(self.reihe)

    def tearDown(self) -> None:
        verwerfen(self.reihe)


class TestSchreibenUndLesen(ZwischenstandBasis):
    """Was hineingeschrieben wurde, kommt unveraendert zurueck."""

    def test_urteil_wird_gelesen_wie_geschrieben(self) -> None:
        urteil_schreiben(self.reihe, "turn-1", True)
        urteil_schreiben(self.reihe, "turn-2", False)

        stand = stand_lesen(self.reihe)

        self.assertEqual({"turn-1": True, "turn-2": False}, stand.urteile)
        self.assertEqual(set(), stand.gescheitert)

    def test_fehlschlag_landet_nicht_bei_den_urteilen(self) -> None:
        # Der Kern der Regel: Ein Fehlschlag ist kein Urteil "False".
        fehlschlag_schreiben(self.reihe, "turn-1", "Zeitueberschreitung")

        stand = stand_lesen(self.reihe)

        self.assertEqual({}, stand.urteile)
        self.assertEqual({"turn-1"}, stand.gescheitert)

    def test_wiederholung_ueberschreibt_den_fehlschlag(self) -> None:
        fehlschlag_schreiben(self.reihe, "turn-1", "Zeitueberschreitung")
        urteil_schreiben(self.reihe, "turn-1", True)

        stand = stand_lesen(self.reihe)

        self.assertEqual({"turn-1": True}, stand.urteile)
        self.assertEqual(set(), stand.gescheitert)

    def test_spaeteres_urteil_gewinnt_gegen_frueheres(self) -> None:
        # Doppelung derselben Kennung: die spaetere Zeile gilt.
        urteil_schreiben(self.reihe, "turn-1", True)
        urteil_schreiben(self.reihe, "turn-1", False)

        self.assertEqual({"turn-1": False}, stand_lesen(self.reihe).urteile)

    def test_aggregat_wird_gelesen_wie_geschrieben(self) -> None:
        aggregat_schreiben(self.reihe, "positions_kontrolle", {
            "bestanden": True, "anteil_nutzer": 0.795,
        })

        stand = stand_lesen(self.reihe)

        self.assertTrue(stand.aggregate["positions_kontrolle"]["bestanden"])
        self.assertEqual(0.795, stand.aggregate["positions_kontrolle"]["anteil_nutzer"])

    def test_jede_zeile_traegt_einen_zeitpunkt_in_utc(self) -> None:
        urteil_schreiben(self.reihe, "turn-1", True)

        with open(_pfad(self.reihe), "r", encoding="utf-8") as datei:
            satz = json.loads(datei.readline())

        self.assertIn("zeit", satz)
        self.assertTrue(satz["zeit"].endswith("+00:00"))


class TestRandfaelle(ZwischenstandBasis):
    """Aus dem Eingaberaum hergeleitet, nicht aus den if-Zeilen."""

    def test_fehlende_datei_ist_der_normalfall(self) -> None:
        # Leer gegen nicht vorhanden: Der erste Lauf hat keine Datei, und das
        # ist kein Fehler.
        stand = stand_lesen("test-existiert-nicht")

        self.assertEqual({}, stand.urteile)
        self.assertEqual({}, stand.aggregate)

    def test_leere_datei_liefert_leeren_stand(self) -> None:
        # Der zweite der beiden Faelle: Datei da, aber ohne Inhalt.
        open(_pfad(self.reihe), "w", encoding="utf-8").close()

        self.assertEqual({}, stand_lesen(self.reihe).urteile)

    def test_leere_kennung_wird_abgewiesen(self) -> None:
        with self.assertLogs(
            "ki_server.agents.kalibrierung.zwischenstand", level="ERROR"
        ) as log:
            urteil_schreiben(self.reihe, "", True)

        self.assertIn("leere Kennung", "".join(log.output))
        self.assertFalse(os.path.exists(_pfad(self.reihe)))

    def test_fehlschlag_ohne_grund_wird_abgewiesen(self) -> None:
        # Ein unbenannter Fehlschlag ist beim Wiederanlauf nicht deutbar: Man
        # kann nicht entscheiden, ob er wiederholbar ist. Er wird deshalb nicht
        # geschrieben — der Fall gilt dann als nie versucht und wird ohnehin
        # wiederholt.
        with self.assertLogs(
            "ki_server.agents.kalibrierung.zwischenstand", level="ERROR"
        ) as log:
            fehlschlag_schreiben(self.reihe, "turn-1", "")

        self.assertIn("ohne Grund", "".join(log.output))
        self.assertFalse(os.path.exists(_pfad(self.reihe)))

    def test_fehlschlag_mit_grund_wird_geschrieben(self) -> None:
        # Der positive Zwilling zur Abweisung darueber: Ohne ihn bestuende der
        # Test auch dann, wenn nie ein Fehlschlag geschrieben wuerde.
        fehlschlag_schreiben(self.reihe, "turn-1", "Zeitueberschreitung")

        self.assertEqual({"turn-1"}, stand_lesen(self.reihe).gescheitert)

    def test_aggregat_ohne_schluessel_wird_abgewiesen(self) -> None:
        with self.assertLogs(
            "ki_server.agents.kalibrierung.zwischenstand", level="ERROR"
        ) as log:
            aggregat_schreiben(self.reihe, "", {"a": 1})

        self.assertIn("ohne Schluessel", "".join(log.output))

    def test_pfadtrenner_im_namen_wird_abgewiesen(self) -> None:
        # Falscher Typ im weiteren Sinn: ein Name, der aus dem Verzeichnis
        # herausfuehrt.
        for name in ("../ausbruch", "unter/verzeichnis", "rueck\\waerts"):
            with self.subTest(name=name):
                with self.assertLogs(
                    "ki_server.agents.kalibrierung.zwischenstand", level="ERROR"
                ):
                    with self.assertRaises(ValueError):
                        _pfad(name)

    def test_unlesbare_zeile_wird_gezaehlt_nicht_verschwiegen(self) -> None:
        # Freitext, wo JSON erwartet wird. Eine stillschweigend uebergangene
        # Zeile waere eine Luecke, die aussieht wie ein nie versuchter Fall.
        urteil_schreiben(self.reihe, "turn-1", True)
        with open(_pfad(self.reihe), "a", encoding="utf-8") as datei:
            datei.write("das ist kein JSON\n")

        with self.assertLogs(
            "ki_server.agents.kalibrierung.zwischenstand", level="ERROR"
        ) as log:
            stand = stand_lesen(self.reihe)

        self.assertIn("unlesbare Zeilen", "".join(log.output))
        self.assertEqual({"turn-1": True}, stand.urteile)

    def test_zeile_ohne_kennung_wird_gezaehlt(self) -> None:
        with open(_pfad(self.reihe), "a", encoding="utf-8") as datei:
            datei.write(json.dumps({"urteil": True}) + "\n")

        with self.assertLogs(
            "ki_server.agents.kalibrierung.zwischenstand", level="ERROR"
        ):
            self.assertEqual({}, stand_lesen(self.reihe).urteile)

    def test_urteil_als_freitext_gilt_als_fehlschlag(self) -> None:
        # Ein Sprachmodell kann alles liefern. Nur ein echtes Boolean zaehlt
        # als Urteil; "true" als Zeichenkette ist keins.
        with open(_pfad(self.reihe), "a", encoding="utf-8") as datei:
            datei.write(json.dumps({"kennung": "turn-1", "urteil": "true"}) + "\n")

        stand = stand_lesen(self.reihe)

        self.assertEqual({}, stand.urteile)
        self.assertEqual({"turn-1"}, stand.gescheitert)

    def test_grosse_reihe_bleibt_vollstaendig(self) -> None:
        # Unerwartet gross: Der Zwischenstand ist fuer Hunderte Faelle gebaut.
        for i in range(500):
            urteil_schreiben(self.reihe, f"turn-{i}", i % 2 == 0)

        stand = stand_lesen(self.reihe)

        self.assertEqual(500, len(stand.urteile))
        self.assertTrue(stand.urteile["turn-0"])
        self.assertFalse(stand.urteile["turn-1"])


class TestVerwerfen(ZwischenstandBasis):
    """Arbeitsmaterial bleibt nicht liegen."""

    def test_verwerfen_entfernt_die_datei(self) -> None:
        urteil_schreiben(self.reihe, "turn-1", True)
        self.assertTrue(os.path.exists(_pfad(self.reihe)))

        verwerfen(self.reihe)

        self.assertFalse(os.path.exists(_pfad(self.reihe)))

    def test_verwerfen_einer_fehlenden_datei_ist_kein_fehler(self) -> None:
        verwerfen("test-gibt-es-nicht")


class TestZwischenstandLiegtAusserhalbDesRepos(unittest.TestCase):
    """Ein Zwischenstand unter /app waere committfaehig."""

    def test_pfad_liegt_nicht_unter_app(self) -> None:
        # /app ist das eingehaengte Server-Verzeichnis und damit Teil des
        # Repositoriums. Ein Zwischenstand dort traegt Turn-Kennungen in einen
        # Commit.
        pfad: str = _pfad("test-lage")

        self.assertFalse(pfad.startswith("/app"))
        verwerfen("test-lage")


class TestZeugenkennung(unittest.TestCase):
    """Urteile zweier Prompt-Fassungen werden nicht vermischt."""

    def test_kennung_ist_stabil(self) -> None:
        self.assertEqual(_zeugenkennung(), _zeugenkennung())

    def test_kennung_haengt_am_prompt(self) -> None:
        # Zeuge ist eine eigene Rechnung im Test, nicht die geprüfte Funktion:
        # Derselbe Algorithmus auf einem geaenderten Text muss abweichen.
        import hashlib
        from agents.kalibrierung.zeuge import ZEUGE_PROMPT

        anders: str = hashlib.sha256(
            (ZEUGE_PROMPT + " geaendert").encode("utf-8")
        ).hexdigest()[:12]

        self.assertNotEqual(anders, _zeugenkennung())

    def test_reihenname_traegt_das_paar(self) -> None:
        self.assertEqual("meister-nova", _reihenname("meister", "nova"))


if __name__ == "__main__":
    unittest.main()
