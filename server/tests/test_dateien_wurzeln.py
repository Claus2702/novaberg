"""Tests für den Wurzeln-Dienst (`agents/dateien_wurzeln/`).

Ziel: Ein Mensch gibt im Gespräch ein Verzeichnis frei, nimmt die Freigabe
zurück und erfährt, worauf Nova Zugriff hat — und ein Pfad außerhalb des
konfigurierten Außenrands wird abgewiesen, **auch auf Bestätigung**.

Die Zusicherungen, die hier geprüft werden:

  1. **Der Außenrand hält, und er hält gegen die Auflösung.** Ein Pfad, der
     über `..` oder über eine symbolische Verknüpfung hinausführt, wird
     abgewiesen — geprüft wird der aufgelöste Pfad, nicht die Zeichenkette.
  2. **Ein leerer Rand lässt nichts durch.** Der Ausfall ist geschlossen;
     "nicht konfiguriert" heißt nicht "alles erlaubt".
  3. **Das Tor zeigt die Auflösung, nicht die Eingabe.** Der Bestätigungstext
     trägt den aufgelösten Pfad und die Dateizahl.
  4. **Eine unklare Antwort am Tor führt nie zur Ausführung.**
  5. **Geschrieben wird der aufgelöste Pfad**, und was nicht ankommt, wird
     als Fehler gemeldet statt als Erfolg.
  6. **Ein unbekannter Aktionswert ist ein Defekt**, kein Griff zu einem
     Vorgabewert.

Zum Ausbruchs-Zeugen ausdrücklich: Das Ziel außerhalb des Randes
**existiert**. Ein Zeuge mit nicht existierendem Ziel belegt die
Wurzelprüfung nicht — er scheitert schon an der Existenzprüfung und bliebe
grün, wenn man den Rand aushebelte (Fundliste, 18.08.2026).

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents.base import AgentState
from agents.dateien_wurzeln import aussenrand, crud
from agents.dateien_wurzeln.agent import DateienWurzelnAgent
from agents.dateien_wurzeln.resume import ABLEHNUNG, BESTAETIGUNG, UNKLAR, _antwort_deuten, resume

PAAR_USER: str = "meister"
PAAR_FIGUR: str = "nova"


def _state(parameter: dict, aufgabe: str = "egal") -> AgentState:
    """Baut einen AgentState für den Dienst."""
    return {
        "aufgabe": aufgabe,
        "aufgabe_typ": "workflow",
        "agent_name": "dateien_wurzeln",
        "kontext": {"user_id": PAAR_USER, "character_id": PAAR_FIGUR},
        "parameter": parameter,
        "schritte": [],
        "ergebnis": None,
        "status": "laufend",
        "rueckfrage": None,
        "fehler": None,
    }


class Bank:
    """In-Memory-Ersatz für den `db_manager`.

    Er kennt genau die Abfragen dieses Dienstes und **wirft bei jeder
    anderen**. Ein Test-Double, das Unbekanntes stillschweigend mit einer
    leeren Liste beantwortet, macht einen Tippfehler in der Abfrage von
    einem leeren Bestand ununterscheidbar — dieselbe Fehlerklasse wie ein
    leerer Grep.
    """

    def __init__(self, zeilen: list[dict] | None = None) -> None:
        """Nimmt einen Anfangsbestand auf und vergibt Nummern wie die Datenbank."""
        self.zeilen: list[dict] = list(zeilen or [])
        self._naechste_id: int = max((z["id"] for z in self.zeilen), default=0) + 1
        self.schreibvorgaenge: list[tuple[str, tuple]] = []
        #: Schaltet die Wirkung von UPDATE/INSERT ab — damit die
        #: Ausgabe-Verifikation ihren Auslösefall bekommt.
        self.schreiben_wirkungslos: bool = False

    # --- Lesen ---

    def select(self, query: str, params: tuple = ()) -> list[dict]:
        """Beantwortet die Listen-Abfragen des Dienstes; alles andere wirft."""
        if "ORDER BY erstellt_am" in query and "aktiv = TRUE" in query:
            return [z for z in self._paar(params) if z["aktiv"]]
        if "aktiv = FALSE" in query and "ILIKE" not in query:
            return [z for z in self._paar(params) if not z["aktiv"]]
        if "ILIKE" in query:
            user_id, character_id, aktiv, muster, _ = params
            stich: str = muster.strip("%").lower()
            return [
                z for z in self.zeilen
                if z["user_id"] == user_id
                and z["character_id"] == character_id
                and z["aktiv"] is aktiv
                and (stich in z["pfad"].lower() or stich in (z["bezeichnung"] or "").lower())
            ]
        raise AssertionError(f"Bank: unbekannte SELECT-Abfrage: {query}")

    def select_one(self, query: str, params: tuple = ()) -> dict | None:
        """Beantwortet die Einzelabfragen; eine unbekannte wirft statt zu schweigen."""
        if "WHERE id = %s" in query:
            return next((z for z in self.zeilen if z["id"] == params[0]), None)
        if "AND pfad = %s" in query:
            user_id, character_id, pfad = params
            return next(
                (z for z in self.zeilen
                 if z["user_id"] == user_id
                 and z["character_id"] == character_id
                 and z["pfad"] == pfad),
                None,
            )
        raise AssertionError(f"Bank: unbekannte SELECT-ONE-Abfrage: {query}")

    # --- Schreiben ---

    def execute(self, query: str, params: tuple = ()) -> int:
        """Fuehrt UPDATE aus — oder laesst es wirkungslos, fuer die Verifikation."""
        self.schreibvorgaenge.append((query, params))
        if self.schreiben_wirkungslos:
            return 0
        if "SET aktiv = %s" in query:
            aktiv, zeilen_id = params
            for zeile in self.zeilen:
                if zeile["id"] == zeilen_id:
                    zeile["aktiv"] = aktiv
                    return 1
            return 0
        if "SET bezeichnung = %s" in query:
            bezeichnung, zeilen_id = params
            for zeile in self.zeilen:
                if zeile["id"] == zeilen_id:
                    zeile["bezeichnung"] = bezeichnung
                    return 1
            return 0
        raise AssertionError(f"Bank: unbekannte UPDATE-Abfrage: {query}")

    def execute_returning(self, query: str, params: tuple = ()) -> dict | None:
        """Fuehrt INSERT aus und liefert die vergebene Nummer."""
        self.schreibvorgaenge.append((query, params))
        if "INSERT INTO dateien_wurzeln" not in query:
            raise AssertionError(f"Bank: unbekannte INSERT-Abfrage: {query}")
        if self.schreiben_wirkungslos:
            return {"id": 999}
        user_id, character_id, pfad, bezeichnung, eigentum = params
        zeile: dict = {
            "id": self._naechste_id, "user_id": user_id, "character_id": character_id,
            "pfad": pfad, "bezeichnung": bezeichnung, "eigentum": eigentum,
            "aktiv": True, "erstellt_am": None, "geaendert_am": None,
        }
        self._naechste_id += 1
        self.zeilen.append(zeile)
        return {"id": zeile["id"]}

    def _paar(self, params: tuple) -> list[dict]:
        user_id, character_id = params[0], params[1]
        return [
            z for z in self.zeilen
            if z["user_id"] == user_id and z["character_id"] == character_id
        ]


class AussenrandTest(unittest.TestCase):
    """Die Schranke, die kein Gespräch verschieben kann."""

    def setUp(self) -> None:
        """Legt Rand, Innenraum und ein existierendes Ziel ausserhalb an."""
        self.basis: Path = Path(tempfile.mkdtemp(prefix="wurzeln_"))
        self.rand: Path = self.basis / "rand"
        self.innen: Path = self.rand / "projekt"
        self.innen.mkdir(parents=True)
        (self.innen / "eins.md").write_text("a", encoding="utf-8")
        (self.innen / "zwei.md").write_text("b", encoding="utf-8")

        # Das Ziel des Ausbruchs EXISTIERT — sonst belegt der Zeuge die
        # Existenzprüfung statt der Wurzelprüfung.
        self.draussen: Path = self.basis / "draussen"
        self.draussen.mkdir()
        (self.draussen / "geheim.md").write_text("x", encoding="utf-8")

        self._patch = patch.object(aussenrand, "DATEIEN_AUSSENRAND", [str(self.rand)])
        self._patch.start()

    def tearDown(self) -> None:
        """Raeumt Verzeichnisse und Attrappen wieder ab."""
        self._patch.stop()
        shutil.rmtree(self.basis, ignore_errors=True)

    def test_verzeichnis_im_rand_wird_angenommen(self) -> None:
        """Ein Verzeichnis innerhalb des Randes wird angenommen, mit gezaehlten Dateien."""
        befund = aussenrand.wurzel_pruefen(str(self.innen))
        self.assertTrue(befund.ok, befund.grund)
        self.assertEqual(befund.aufgeloest, self.innen.resolve())
        self.assertEqual(befund.dateizahl, 2)
        self.assertTrue(befund.gezaehlt_vollstaendig)

    def test_ausbruch_ueber_punkt_punkt_auf_existierendes_ziel(self) -> None:
        """`..` führt aus dem Rand heraus — und das Ziel existiert."""
        ausbruch: str = str(self.innen / ".." / ".." / "draussen")
        self.assertTrue(Path(ausbruch).resolve().is_dir(), "Zielprämisse verletzt")

        befund = aussenrand.wurzel_pruefen(ausbruch)

        self.assertFalse(befund.ok)
        self.assertEqual(befund.aufgeloest, self.draussen.resolve())
        self.assertIn("ausserhalb", befund.grund)

    def test_ausbruch_ueber_symlink_auf_existierendes_ziel(self) -> None:
        """Eine Verknüpfung im Rand zeigt nach draußen — abgewiesen."""
        verweis: Path = self.rand / "verweis"
        verweis.symlink_to(self.draussen, target_is_directory=True)
        self.assertTrue(verweis.resolve().is_dir(), "Zielprämisse verletzt")

        befund = aussenrand.wurzel_pruefen(str(verweis))

        self.assertFalse(befund.ok)
        self.assertEqual(befund.aufgeloest, self.draussen.resolve())

    def test_leerer_rand_laesst_nichts_durch(self) -> None:
        """Der Ausfall ist geschlossen — auch für einen Pfad, der sonst ginge."""
        with patch.object(aussenrand, "DATEIEN_AUSSENRAND", []):
            befund = aussenrand.wurzel_pruefen(str(self.innen))
        self.assertFalse(befund.ok)
        self.assertIn("kein zulaessiger Bereich", befund.grund)

    def test_datei_statt_verzeichnis_wird_abgewiesen(self) -> None:
        """Eine Datei ist keine Wurzel."""
        befund = aussenrand.wurzel_pruefen(str(self.innen / "eins.md"))
        self.assertFalse(befund.ok)
        self.assertIn("kein Verzeichnis", befund.grund)

    def test_fehlender_pfad_nennt_die_aufloesung(self) -> None:
        """Der Mensch soll erfahren, WO sein Pfad gelandet wäre."""
        befund = aussenrand.wurzel_pruefen(str(self.rand / "gibtsnicht"))
        self.assertFalse(befund.ok)
        self.assertIn(str((self.rand / "gibtsnicht").resolve()), befund.grund)

    def test_leere_eingabe_wird_abgewiesen(self) -> None:
        """Ohne genanntes Verzeichnis gibt es nichts freizugeben."""
        self.assertFalse(aussenrand.wurzel_pruefen("   ").ok)

    def test_zaehlgrenze_meldet_untergrenze_statt_endzahl(self) -> None:
        """Eine gekappte Zaehlung wird als Untergrenze ausgewiesen, nicht als Endzahl."""
        with patch.object(aussenrand, "DATEIEN_WURZEL_ZAEHLGRENZE", 1):
            befund = aussenrand.wurzel_pruefen(str(self.innen))
        self.assertTrue(befund.ok)
        self.assertFalse(befund.gezaehlt_vollstaendig)
        self.assertIn("mindestens", aussenrand.dateizahl_text(befund))

    def test_rand_text_nennt_die_grenze(self) -> None:
        """Die geltende Grenze ist nennbar — eine ungenannte kann niemand einhalten."""
        self.assertIn(str(self.rand.resolve()), aussenrand.rand_text())


class TorTest(unittest.TestCase):
    """Das Tor zeigt die Auflösung, nicht die Eingabe."""

    def setUp(self) -> None:
        """Legt Rand, Innenraum und ein existierendes Ziel ausserhalb an."""
        self.basis: Path = Path(tempfile.mkdtemp(prefix="wurzeln_tor_"))
        self.rand: Path = self.basis / "rand"
        self.innen: Path = self.rand / "projekt"
        self.innen.mkdir(parents=True)
        for name in ("a.md", "b.md", "c.md"):
            (self.innen / name).write_text("x", encoding="utf-8")
        self.draussen: Path = self.basis / "draussen"
        self.draussen.mkdir()

        self._rand_patch = patch.object(aussenrand, "DATEIEN_AUSSENRAND", [str(self.rand)])
        self._rand_patch.start()
        self.bank = Bank()
        self._bank_patch = patch.object(crud, "db_manager", self.bank)
        self._bank_patch.start()

    def tearDown(self) -> None:
        """Raeumt Verzeichnisse und Attrappen wieder ab."""
        self._bank_patch.stop()
        self._rand_patch.stop()
        shutil.rmtree(self.basis, ignore_errors=True)

    def test_create_fragt_mit_aufgeloestem_pfad_und_dateizahl(self) -> None:
        """Das Tor zeigt die Aufloesung samt Dateizahl, nicht die Eingabe."""
        umweg: str = str(self.innen / ".." / "projekt")
        ergebnis, korrektur = crud.validieren_gegen_db(
            _state({"action": "create", "pfad": umweg})
        )
        self.assertIsNone(korrektur)
        self.assertTrue(ergebnis.bestaetigung_noetig)
        self.assertIn(str(self.innen.resolve()), ergebnis.bestaetigung_text)
        self.assertIn("3 Dateien", ergebnis.bestaetigung_text)
        self.assertNotIn("..", ergebnis.bestaetigung_text)

    def test_create_ausserhalb_bekommt_kein_tor(self) -> None:
        """Ausserhalb wird abgewiesen — nicht zur Bestätigung vorgelegt."""
        ergebnis, korrektur = crud.validieren_gegen_db(
            _state({"action": "create", "pfad": str(self.draussen)})
        )
        self.assertFalse(ergebnis.ok)
        self.assertFalse(ergebnis.bestaetigung_noetig)
        self.assertIsNotNone(korrektur, "Randablehnung ohne Korrektur waere eine Sackgasse")

    def test_randablehnung_traegt_alle_drei_teile(self) -> None:
        """Ein Urteil ohne Beleg und Vorschlag ist eine Sackgasse, kein Nein."""
        _, korrektur = crud.validieren_gegen_db(
            _state({"action": "create", "pfad": str(self.draussen)})
        )
        self.assertTrue(korrektur.befund)
        self.assertIn(str(self.draussen.resolve()), korrektur.beleg)
        self.assertIn(str(self.rand.resolve()), korrektur.vorschlag)

    def test_fehlender_rand_ist_stoerung_und_kein_urteil(self) -> None:
        """Ein unkonfigurierter Rand geht den Betreiber an, nicht den Menschen."""
        with patch.object(aussenrand, "DATEIEN_AUSSENRAND", []):
            ergebnis, korrektur = crud.validieren_gegen_db(
                _state({"action": "create", "pfad": str(self.innen)})
            )
        self.assertFalse(ergebnis.ok)
        self.assertIsNone(korrektur, "Ein Betriebszustand ist keine Ablehnung")

    def test_bestehende_freigabe_ergibt_keine_zweite_zeile(self) -> None:
        """Dieselbe Freigabe zweimal ergibt die Auskunft, dass sie besteht."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": None, "aktiv": True,
        })
        ergebnis, korrektur = crud.validieren_gegen_db(
            _state({"action": "create", "pfad": str(self.innen)})
        )
        self.assertFalse(ergebnis.ok)
        self.assertIn("bereits freigegeben", ergebnis.grund)
        self.assertIsNotNone(korrektur)

    def test_stillgelegte_freigabe_wird_zu_reactivate(self) -> None:
        """Eine stillgelegte Freigabe wird wieder aufgenommen statt verdoppelt."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": None, "aktiv": False,
        })
        ergebnis, korrektur = crud.validieren_gegen_db(
            _state({"action": "create", "pfad": str(self.innen)})
        )
        self.assertEqual(ergebnis.korrektur, "reactivate")
        self.assertTrue(ergebnis.bestaetigung_noetig)
        self.assertIsNone(korrektur)

    def test_jede_schreiboperation_geht_durch_das_tor(self) -> None:
        """Keine Schreiboperation laeuft ohne Bestaetigung."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": "Projektdoku", "aktiv": True,
        })
        for aktion, zusatz in (
            ("delete", {"stichwort": "Projektdoku"}),
            ("update", {"stichwort": "Projektdoku", "bezeichnung": "Neu"}),
        ):
            with self.subTest(aktion=aktion):
                ergebnis, _ = crud.validieren_gegen_db(_state({"action": aktion, **zusatz}))
                self.assertTrue(ergebnis.bestaetigung_noetig, aktion)

    def test_read_braucht_kein_tor(self) -> None:
        """Eine Leseoperation aendert nichts und fragt deshalb nicht."""
        ergebnis, korrektur = crud.validieren_gegen_db(_state({"action": "read"}))
        self.assertTrue(ergebnis.ok)
        self.assertFalse(ergebnis.bestaetigung_noetig)
        self.assertIsNone(korrektur)

    def test_fremde_freigabe_ist_unsichtbar(self) -> None:
        """Eine ID eines anderen Paares ist nicht ansprechbar."""
        self.bank.zeilen.append({
            "id": 7, "user_id": "jemand_anders", "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": None, "aktiv": True,
        })
        ergebnis, korrektur = crud.validieren_gegen_db(
            _state({"action": "delete", "target_id": 7})
        )
        self.assertFalse(ergebnis.ok)
        self.assertIn("gibt es nicht", ergebnis.grund)
        self.assertIsNotNone(korrektur)

    def test_unbekannte_aktion_wird_abgewiesen(self) -> None:
        """Ein Wert ausserhalb des Kanons ist ein Defekt, kein Vorgabewert."""
        ergebnis, korrektur = crud.validieren_gegen_db(_state({"action": "vergessen"}))
        self.assertFalse(ergebnis.ok)
        self.assertIn("Unbekannte Aktion", ergebnis.grund)
        self.assertIsNone(korrektur, "Ein Kanonverstoss ist ein Defekt, kein Urteil")


class AusfuehrungTest(unittest.TestCase):
    """Was geschrieben wird, ist der aufgelöste Pfad — und es wird nachgesehen."""

    def setUp(self) -> None:
        """Legt Rand, Innenraum und ein existierendes Ziel ausserhalb an."""
        self.basis: Path = Path(tempfile.mkdtemp(prefix="wurzeln_exec_"))
        self.rand: Path = self.basis / "rand"
        self.innen: Path = self.rand / "projekt"
        self.innen.mkdir(parents=True)
        (self.innen / "a.md").write_text("x", encoding="utf-8")
        self.draussen: Path = self.basis / "draussen"
        self.draussen.mkdir()

        self._rand_patch = patch.object(aussenrand, "DATEIEN_AUSSENRAND", [str(self.rand)])
        self._rand_patch.start()
        self.bank = Bank()
        self._bank_patch = patch.object(crud, "db_manager", self.bank)
        self._bank_patch.start()

    def tearDown(self) -> None:
        """Raeumt Verzeichnisse und Attrappen wieder ab."""
        self._bank_patch.stop()
        self._rand_patch.stop()
        shutil.rmtree(self.basis, ignore_errors=True)

    def test_create_schreibt_den_aufgeloesten_pfad(self) -> None:
        """In der Tabelle steht das Verzeichnis, nicht die Zeichenkette.

        **Der Auftrag traegt seit dem 22.08.2026 `eigentum`.** Ohne die
        Angabe schreibt `_create` nicht mehr, sondern fragt — der Zeuge dafuer
        steht in `test_dateien_wurzeln_eigentum.py`.
        """
        umweg: str = str(self.innen / ".." / "projekt")
        ergebnis = crud.ausfuehren(_state({
            "action": "create", "pfad": umweg, "eigentum": "nutzer",
        }))

        self.assertEqual(ergebnis["status"], "abgeschlossen")
        self.assertEqual(len(self.bank.zeilen), 1)
        self.assertEqual(self.bank.zeilen[0]["pfad"], str(self.innen.resolve()))

    def test_create_prueft_den_rand_ein_zweites_mal(self) -> None:
        """Zwischen Tor und Bestätigung liegt beliebig viel Zeit."""
        ergebnis = crud.ausfuehren(
            _state({"action": "create", "pfad": str(self.draussen)})
        )
        self.assertEqual(ergebnis["status"], "abgelehnt")
        self.assertIsNotNone(ergebnis["parameter"]["korrektur"])
        self.assertEqual(self.bank.zeilen, [])

    def test_wirkungsloses_schreiben_wird_als_fehler_gemeldet(self) -> None:
        """Ein gelungener Aufruf ist nicht dasselbe wie eine geschriebene Zeile."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": None, "aktiv": True,
        })
        self.bank.schreiben_wirkungslos = True

        ergebnis = crud.ausfuehren(_state({"action": "delete", "target_id": 1}))

        self.assertEqual(ergebnis["status"], "fehler")
        self.assertIn("nicht angekommen", ergebnis["fehler"])

    def test_delete_und_reactivate_wechseln_den_zustand(self) -> None:
        """Ruecknahme und Wiederaufnahme sind zueinander symmetrisch."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": None, "aktiv": True,
        })

        crud.ausfuehren(_state({"action": "delete", "target_id": 1}))
        self.assertFalse(self.bank.zeilen[0]["aktiv"])

        crud.ausfuehren(_state({"action": "reactivate", "target_id": 1}))
        self.assertTrue(self.bank.zeilen[0]["aktiv"])

    def test_reactivate_haelt_die_alte_zeile_gegen_den_heutigen_rand(self) -> None:
        """Eine alte Freigabe ist kein Recht, wenn der Rand enger wurde."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.draussen.resolve()), "bezeichnung": None, "aktiv": False,
        })
        ergebnis = crud.ausfuehren(_state({"action": "reactivate", "target_id": 1}))

        self.assertEqual(ergebnis["status"], "abgelehnt")
        self.assertFalse(self.bank.zeilen[0]["aktiv"])

    def test_update_aendert_die_bezeichnung_und_nie_den_pfad(self) -> None:
        """Eine Umbenennung ist kein Weg an der Schranke vorbei."""
        self.bank.zeilen.append({
            "id": 1, "user_id": PAAR_USER, "character_id": PAAR_FIGUR,
            "pfad": str(self.innen.resolve()), "bezeichnung": "Alt", "aktiv": True,
        })
        crud.ausfuehren(
            _state({"action": "update", "target_id": 1, "bezeichnung": "Projektdoku"})
        )
        self.assertEqual(self.bank.zeilen[0]["bezeichnung"], "Projektdoku")
        self.assertEqual(self.bank.zeilen[0]["pfad"], str(self.innen.resolve()))

    def test_read_ohne_bestand_sagt_es(self) -> None:
        """Kein Bestand ist eine Auskunft, keine leere Antwort."""
        ergebnis = crud.ausfuehren(_state({"action": "read"}))
        self.assertEqual(ergebnis["status"], "abgeschlossen")
        self.assertIn("kein Verzeichnis", ergebnis["ergebnis"])

    def test_jeder_rueckkehrpfad_setzt_status_und_schritt(self) -> None:
        """Kein Pfad verlaesst die Ausfuehrung ohne Status und Audit-Schritt."""
        for parameter in (
            {"action": "read"},
            {"action": "create", "pfad": str(self.draussen)},
            {"action": "delete"},
            {"action": "unbekannt"},
        ):
            with self.subTest(parameter=parameter):
                ergebnis = crud.ausfuehren(_state(parameter))
                self.assertIn("status", ergebnis)
                self.assertTrue(ergebnis["schritte"])


class RueckwegTest(unittest.TestCase):
    """Der Mensch darf nein sagen — und Unklarheit führt nie zur Ausführung."""

    def test_nein_wird_zu_dismissed(self) -> None:
        """Ein Nein am Tor beendet den Vorgang, ohne zu schreiben."""
        ergebnis = resume(_state({
            "action": "create", "resume": True,
            "user_answer": "nein, lass mal", "original_rueckfrage": "Freigeben?",
        }))
        self.assertEqual(ergebnis["status"], "dismissed")

    def test_ja_fuehrt_weiter(self) -> None:
        """Eine gedeutete Zustimmung gibt die Ausfuehrung frei."""
        ergebnis = resume(_state({
            "action": "create", "resume": True,
            "user_answer": "ja, mach", "original_rueckfrage": "Freigeben?",
        }))
        self.assertEqual(ergebnis["status"], "laufend")
        self.assertFalse(ergebnis["parameter"]["resume"])

    def test_unklar_fragt_erneut_statt_auszufuehren(self) -> None:
        """Unklarheit fuehrt zur erneuten Frage und nie zur Ausfuehrung."""
        for antwort in ("", "hmm", "vielleicht später", "42"):
            with self.subTest(antwort=antwort):
                ergebnis = resume(_state({
                    "action": "create", "resume": True,
                    "user_answer": antwort, "original_rueckfrage": "Freigeben?",
                }))
                self.assertEqual(ergebnis["status"], "rueckfrage")
                self.assertEqual(ergebnis["rueckfrage"], "Freigeben?")

    def test_zustimmung_mit_ne_im_wort_ist_keine_ablehnung(self) -> None:
        """'ne' steckt in 'gerne' — ein Teilzeichenketten-Vergleich dreht die Antwort um."""
        for antwort in ("ja, gerne", "gerne", "meinetwegen", "ja gerne doch"):
            with self.subTest(antwort=antwort):
                self.assertEqual(_antwort_deuten(antwort), BESTAETIGUNG)

    def test_kurze_verneinungen_gelten_als_ganzes_wort(self) -> None:
        """'ne' und 'nee' allein sind eine Ablehnung — an Wortgrenzen erkannt."""
        for antwort in ("ne", "nee", "ne, lass mal", "noe"):
            with self.subTest(antwort=antwort):
                self.assertEqual(_antwort_deuten(antwort), ABLEHNUNG)

    def test_ablehnung_gewinnt_bei_zusammentreffen(self) -> None:
        """'ja, aber nicht das' trägt beide Wörter — die sichere Lesart gilt."""
        self.assertEqual(_antwort_deuten("ja, aber nicht das"), ABLEHNUNG)

    def test_die_drei_lesarten_sind_geschlossen(self) -> None:
        """Jede Antwort faellt in genau eine der drei Lesarten."""
        for antwort, erwartet in (
            ("nein", ABLEHNUNG), ("okay", BESTAETIGUNG), ("bla", UNKLAR),
        ):
            with self.subTest(antwort=antwort):
                self.assertEqual(_antwort_deuten(antwort), erwartet)


class AnmeldungTest(unittest.TestCase):
    """Die Anmeldung stand vor dem Code — sie wird gegen ihn gehalten."""

    def setUp(self) -> None:
        """Legt Rand, Innenraum und ein existierendes Ziel ausserhalb an."""
        self.agent = DateienWurzelnAgent()

    def test_zustellart_ist_empfang(self) -> None:
        """Der Dienst wird gewaehlt und braucht deshalb Aushang und Quote."""
        self.assertEqual(self.agent.zustellart, "empfang")

    def test_nur_nutzergraph(self) -> None:
        """Ein eigener Impuls darf sich kein Verzeichnis freigeben."""
        self.assertEqual(self.agent.graph_eignung, ["user"])

    def test_alle_vier_ausgaenge(self) -> None:
        """Der vierte Ausgang ist die Bedingung dafuer, Zweifelsfaelle zu bekommen."""
        self.assertIn("abgelehnt", self.agent.ausgaenge)
        self.assertEqual(len(self.agent.ausgaenge), 4)

    def test_quote_ist_deklariert(self) -> None:
        """Ein Aushang ohne Quote ist eine Behauptung, die nicht falsch sein kann."""
        self.assertEqual(self.agent.quote, {"user": 0})

    def test_negativfaelle_nennen_keinen_anderen_dienst(self) -> None:
        """Ein Zettel, der einen Nachbarn nennt, setzt Wissen voraus, das er nicht hat."""
        fremde: tuple[str, ...] = ("notizen", "timeline", "direktiven", "kzg", "fakten", "wissen")
        for fall in self.agent.negativfaelle:
            for name in fremde:
                self.assertNotIn(name, fall.lower(), f"Negativfall nennt '{name}': {fall}")

    def test_grenze_nennt_den_aussenrand(self) -> None:
        """Die Grenze muss sagen, dass eine Bestaetigung den Rand nicht aufhebt."""
        self.assertTrue(
            any("Bestaetigung" in g for g in self.agent.grenze),
            "Die Grenze muss sagen, dass eine Bestätigung den Rand nicht aufhebt",
        )

    def test_beschreibung_kommt_aus_agent_md(self) -> None:
        """Die Selbstauskunft haengt an AGENT.md und nicht an einem Literal."""
        self.assertIn("DateienWurzelnAgent", self.agent.beschreibung)

    def test_lastart_ist_die_langsame_spur(self) -> None:
        """Ein Modellaufrufer gehoert in die langsame Spur."""
        self.assertEqual(self.agent.lastart, "llm")


class EingangTest(unittest.TestCase):
    """Ein unbekannter Aktionswert ist ein Defekt, kein Vorgabewert."""

    def setUp(self) -> None:
        """Legt Rand, Innenraum und ein existierendes Ziel ausserhalb an."""
        self.agent = DateienWurzelnAgent()

    def test_leere_aktion_wird_gemeldet(self) -> None:
        """Ein Auftrag ohne Aktion ist defekt und wird gemeldet."""
        ergebnis = self.agent._validieren(_state({"action": ""}))
        self.assertEqual(ergebnis["status"], "fehler")

    def test_unbekannte_aktion_wird_gemeldet(self) -> None:
        """Ein Wert ausserhalb des Eingangskanons wird abgewiesen."""
        ergebnis = self.agent._validieren(_state({"action": "rm-rf"}))
        self.assertEqual(ergebnis["status"], "fehler")
        self.assertIn("Unbekannte Aktion", ergebnis["fehler"])

    def test_bekannte_aktionen_laufen_durch(self) -> None:
        """Jede Aktion des Kanons passiert die Eingangspruefung."""
        for aktion in sorted(crud.AKTIONEN_KANON | {"agent"}):
            with self.subTest(aktion=aktion):
                ergebnis = self.agent._validieren(_state({"action": aktion}))
                self.assertEqual(ergebnis["status"], "laufend")

    def test_resume_geht_ueber_den_rueckweg_und_nicht_in_die_ausfuehrung(self) -> None:
        """Eine Antwort am Tor wird gedeutet, bevor irgendetwas geschieht."""
        ziel: str = self.agent._nach_validierung(
            _state({"action": "create", "resume": True})
        )
        self.assertEqual(ziel, "resume")

    def test_nach_resume_fuehrt_nur_laufend_weiter(self) -> None:
        """Kein anderer Zustand als 'laufend' erreicht die Ausfuehrung."""
        weiter: dict[str, str] = {}
        for status in ("fehler", "rueckfrage", "dismissed", "abgeschlossen", "laufend"):
            zustand = _state({"action": "create"})
            zustand["status"] = status
            weiter[status] = self.agent._nach_resume(zustand)
        self.assertEqual(weiter["laufend"], "ausfuehren")
        for status in ("fehler", "rueckfrage", "dismissed", "abgeschlossen"):
            self.assertNotEqual(weiter[status], "ausfuehren", status)


class SchreibpfadTest(unittest.TestCase):
    """Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden."""

    def test_kein_modul_des_verbunds_importiert_einen_schreiber(self) -> None:
        """Der Verbund traegt keinen Schreibpfad ins Dateisystem."""
        verbund: Path = Path(__file__).resolve().parents[1] / "agents" / "dateien_wurzeln"
        verboten: tuple[str, ...] = (
            "datei_schreiben", "block_ersetzen", "block_anfuegen",
            "block_einfuegen", "str_replace_in_block", "shutil", "os.remove",
            "rmtree", "unlink",
        )
        treffer: list[str] = []
        for modul in sorted(verbund.glob("*.py")):
            text: str = modul.read_text(encoding="utf-8")
            treffer += [
                f"{modul.name}: {name}" for name in verboten if name in text
            ]
        self.assertEqual(treffer, [], f"Schreibpfad im Wurzeln-Verbund: {treffer}")


if __name__ == "__main__":
    unittest.main()
