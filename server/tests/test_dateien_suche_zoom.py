"""Tests für die Kandidatensuche und den Zoom des lesenden Dienstes.

Ziel: Eine Frage in die Unterlagen findet die Datei über den **schärfsten**
Kanal, der etwas hergibt, und danach die Stelle darin — ohne dass irgendwo
ein Schreibpfad in Reichweite liegt.

Die Zusicherungen, die hier geprüft werden:

  1. **Scharf vor unscharf.** Ein Name schlägt ein Stichwort, ein Stichwort
     schlägt den Vektor. Der erste Kanal, der etwas findet, gewinnt.
  2. **Der Vektor ordnet innerhalb, er wählt nicht aus.** Fand die scharfe
     Suche eine Menge, kommt keine andere zurück — auch dann nicht, wenn der
     Vektorkanal Zeilen verliert.
  3. **Die leere Kandidatenliste ist nicht dasselbe wie keine.** `None`
     heißt „es gab keine Einschränkung", `[]` heißt „die scharfe Suche lief
     und fand nichts" — und im zweiten Fall darf der Vektor sie nicht
     aufheben.
  4. **Die Karte kostet keinen Dateizugriff**, denn sie steht im Index.
  5. **Null Treffer sind kein Ausfall.** „nichts gefunden" und „nicht
     nachgesehen" bleiben unterscheidbar.
  6. **Kein Schreibpfad in Reichweite** — geprüft am Modul, nicht an der
     Absicht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from agents.dateien import suche as suche_mod
from agents.dateien import zoom as zoom_mod
from agents.dateien.suche import (
    KANAL_NAME,
    KANAL_VEKTOR,
    kandidaten_finden,
    nach_vektor,
)
from agents.dateien.zoom import block_holen, karte_lesen, nadel_suchen


def _zeile(id_: int, name: str, struktur: object = None,
           kanal: str = KANAL_NAME) -> dict:
    """Baut eine Indexzeile, wie die Suche sie liefert.

    **Mit `kanal`, weil die echten Kanaele ihn vor der Rueckgabe setzen.** Eine
    Attrappe ohne ihn waere untreuer als die Wirklichkeit und pruefte damit
    einen Fall, den es im Betrieb nicht gibt (`20_TESTS/attrappe-grenze.md`).
    """
    return {
        "id": id_, "pfad": name, "name": name,
        "thema": "Ein Thema", "zusammenfassung": "Eine Zusammenfassung.",
        "stichwoerter": ["novaberg"], "struktur": struktur, "zeilen": 40,
        "wurzel": "/files", "bezeichnung": None, "kanal": kanal,
    }


class TestScharfVorUnscharf(unittest.TestCase):
    """Der erste Kanal, der etwas findet, gewinnt."""

    def test_der_name_schlaegt_stichwort_und_vektor(self) -> None:
        """Ein Namenstreffer beendet die Suche — die anderen laufen nicht."""
        with patch.object(suche_mod, "nach_name", return_value=[_zeile(1, "a.md")]) as name, \
             patch.object(suche_mod, "nach_stichwort") as stich, \
             patch.object(suche_mod, "nach_vektor") as vektor:
            treffer = kandidaten_finden("u", "c", "a.md", ["novaberg"], [0.1] * 768)

        self.assertEqual(1, len(treffer))
        name.assert_called_once()
        stich.assert_not_called()
        vektor.assert_not_called()

    def test_das_stichwort_schlaegt_den_vektor(self) -> None:
        """Ohne Namenstreffer entscheidet der lexikalische Kanal, nicht der dense."""
        with patch.object(suche_mod, "nach_name", return_value=[]), \
             patch.object(suche_mod, "nach_stichwort",
                          return_value=[_zeile(2, "b.md")]) as stich, \
             patch.object(suche_mod, "nach_vektor") as vektor:
            treffer = kandidaten_finden("u", "c", "nichts", ["novaberg"], [0.1] * 768)

        self.assertEqual(1, len(treffer))
        stich.assert_called_once()
        vektor.assert_not_called()

    def test_ohne_scharfen_treffer_darf_der_vektor_ueber_den_bestand(self) -> None:
        """Es gab keine Einschränkung — also gibt es auch keine aufzuheben."""
        with patch.object(suche_mod, "nach_name", return_value=[]), \
             patch.object(suche_mod, "nach_stichwort", return_value=[]), \
             patch.object(suche_mod, "nach_vektor",
                          return_value=[_zeile(3, "c.md")]) as vektor:
            kandidaten_finden("u", "c", "nichts", ["nichts"], [0.1] * 768)

        self.assertIsNone(vektor.call_args.kwargs["kandidaten_ids"])


class TestDerVektorOrdnetNurInnerhalb(unittest.TestCase):
    """Er ändert die Reihenfolge, nie die Menge."""

    def test_die_geordnete_menge_ist_dieselbe_menge(self) -> None:
        """Zwei Namenstreffer werden geordnet, nicht ergänzt."""
        scharf: list[dict] = [_zeile(1, "a.md"), _zeile(2, "b.md")]
        geordnet: list[dict] = [_zeile(2, "b.md"), _zeile(1, "a.md")]
        with patch.object(suche_mod, "nach_name", return_value=scharf), \
             patch.object(suche_mod, "nach_vektor", return_value=geordnet):
            treffer = kandidaten_finden("u", "c", "md", [], [0.1] * 768)

        self.assertEqual([2, 1], [t["id"] for t in treffer])
        self.assertEqual({1, 2}, {t["id"] for t in treffer})

    def test_der_scharfe_kanal_bleibt_am_treffer_stehen(self) -> None:
        """Er sagt, WARUM die Datei im Rennen ist — das überlebt die Ordnung."""
        scharf: list[dict] = [_zeile(1, "a.md"), _zeile(2, "b.md")]
        geordnet: list[dict] = [dict(z, kanal=KANAL_VEKTOR) for z in reversed(scharf)]
        with patch.object(suche_mod, "nach_name", return_value=scharf), \
             patch.object(suche_mod, "nach_vektor", return_value=geordnet):
            treffer = kandidaten_finden("u", "c", "md", [], [0.1] * 768)

        for eintrag in treffer:
            self.assertEqual(KANAL_NAME, eintrag["kanal"])

    def test_verlorene_zeilen_lassen_die_scharfe_menge_gelten(self) -> None:
        """Fehlt einem Treffer der Vektor, verschwindet er nicht stillschweigend."""
        scharf: list[dict] = [_zeile(1, "a.md"), _zeile(2, "b.md")]
        with patch.object(suche_mod, "nach_stichwort", return_value=scharf), \
             patch.object(suche_mod, "nach_name", return_value=[]), \
             patch.object(suche_mod, "nach_vektor", return_value=[_zeile(1, "a.md")]), \
             self.assertLogs(suche_mod.logger, level="WARNING"):
            treffer = kandidaten_finden("u", "c", "", ["novaberg"], [0.1] * 768)

        self.assertEqual(2, len(treffer))

    def test_kandidat_ohne_kanal_wird_gemeldet(self) -> None:
        """Fehlt der Kanal, ist das ein Defekt am liefernden Kanal — kein Absturz."""
        ohne: list[dict] = [dict(_zeile(1, "a.md")), dict(_zeile(2, "b.md"))]
        for eintrag in ohne:
            del eintrag["kanal"]
        with patch.object(suche_mod, "nach_name", return_value=ohne), \
             patch.object(suche_mod, "nach_vektor",
                          return_value=list(reversed(ohne))), \
             self.assertLogs(suche_mod.logger, level="ERROR"):
            treffer = kandidaten_finden("u", "c", "md", [], [0.1] * 768)

        self.assertEqual(2, len(treffer))


class TestLeereListeIstNichtNone(unittest.TestCase):
    """Die Unterscheidung, an der §6.3 hängt."""

    def test_leere_kandidatenliste_hebt_die_einschraenkung_nicht_auf(self) -> None:
        """Die scharfe Suche lief und fand nichts — dann gibt es nichts zu ordnen."""
        with patch.object(suche_mod.db_manager, "select") as select, \
             self.assertLogs(suche_mod.logger, level="INFO"):
            treffer = nach_vektor("u", "c", [0.1] * 768, kandidaten_ids=[])

        self.assertEqual([], treffer)
        select.assert_not_called()

    def test_ohne_kandidatenliste_wird_abgefragt(self) -> None:
        """`None` heißt: es gab keine Einschränkung."""
        with patch.object(suche_mod.db_manager, "select", return_value=[]) as select:
            nach_vektor("u", "c", [0.1] * 768, kandidaten_ids=None)

        select.assert_called_once()

    def test_unvollstaendiges_paar_wird_laut_abgelehnt(self) -> None:
        """Ohne beide Kennungen käme der Treffer aus einer fremden Freigabe."""
        with patch.object(suche_mod.db_manager, "select") as select, \
             self.assertLogs(suche_mod.logger, level="ERROR"):
            nach_vektor("u", "", [0.1] * 768)

        select.assert_not_called()


class TestDieKarteKostetKeinenDateizugriff(unittest.TestCase):
    """Sie steht im Index, bezahlt beim Indizieren."""

    def test_karte_kommt_aus_der_indexzeile(self) -> None:
        """Kein Griff zur Datei, kein Werkzeugaufruf."""
        bloecke: list[dict] = [{"header": "## AKTUELL", "zeile": 3}]
        with patch.object(zoom_mod, "block_lesen") as block, \
             patch.object(zoom_mod, "datei_grep") as grep:
            karte = karte_lesen(_zeile(1, "a.md", struktur=bloecke))

        self.assertEqual(bloecke, karte)
        block.assert_not_called()
        grep.assert_not_called()

    def test_karte_als_json_text_wird_gelesen(self) -> None:
        """`jsonb` kommt je nach Treiber als Text — das ist kein Fehlerfall."""
        karte = karte_lesen(_zeile(1, "a.md", struktur='[{"header": "## AKTUELL"}]'))

        self.assertEqual([{"header": "## AKTUELL"}], karte)

    def test_fehlende_karte_ist_leer_und_kein_fehler(self) -> None:
        """Eine Auskunft über den Index, nicht über den Zoom."""
        self.assertEqual([], karte_lesen(_zeile(1, "a.md", struktur=None)))

    def test_kaputte_karte_wird_laut_gemeldet(self) -> None:
        """Fehlend und kaputt müssen unterscheidbar bleiben."""
        with self.assertLogs(zoom_mod.logger, level="ERROR"):
            karte = karte_lesen(_zeile(1, "a.md", struktur="{kein json"))

        self.assertEqual([], karte)


class TestBlockUndNadel(unittest.TestCase):
    """Die beiden Stufen, die wirklich in die Datei greifen."""

    def test_mehrdeutiger_header_wird_nicht_zur_auswahl(self) -> None:
        """Die Werkzeugschicht wirft — der Zoom macht daraus keinen Griff zum Ersten."""
        with patch.object(zoom_mod, "block_lesen",
                          side_effect=ValueError("mehrdeutig")), \
             self.assertLogs(zoom_mod.logger, level="WARNING"):
            self.assertIsNone(block_holen(_zeile(1, "a.md"), "## AKTUELL"))

    def test_null_treffer_sind_kein_none(self) -> None:
        """„nichts gefunden" und „nicht nachgesehen" bleiben unterscheidbar."""
        with patch.object(zoom_mod, "datei_grep",
                          return_value={"treffer": [], "anzahl": 0, "gekappt": False}):
            ergebnis = nadel_suchen(_zeile(1, "a.md"), "Quark")

        self.assertIsNotNone(ergebnis)
        self.assertEqual(0, ergebnis["anzahl"])

    def test_die_kappung_wird_weitergereicht(self) -> None:
        """Eine gekürzte Liste, die wie eine vollständige aussieht, ist der Defekt."""
        with patch.object(zoom_mod, "datei_grep",
                          return_value={"treffer": [(1, "x")], "anzahl": 1,
                                        "gekappt": True}):
            ergebnis = nadel_suchen(_zeile(1, "a.md"), "x")

        self.assertTrue(ergebnis["gekappt"])

    def test_kandidat_ohne_ort_greift_nicht_zur_datei(self) -> None:
        """Ohne Pfad oder Wurzel gibt es keinen Zugriff, sondern eine Meldung."""
        ohne: dict = dict(_zeile(1, "a.md"), wurzel="")
        with patch.object(zoom_mod, "datei_grep") as grep, \
             self.assertLogs(zoom_mod.logger, level="ERROR"):
            self.assertIsNone(nadel_suchen(ohne, "x"))

        grep.assert_not_called()

    def test_der_pfad_wird_an_die_wurzel_gehaengt(self) -> None:
        """Relativ im Index, zusammengesetzt beim Zugriff — aufgelöst wird im Werkzeug."""
        with patch.object(zoom_mod, "datei_grep",
                          return_value={"treffer": [], "anzahl": 0,
                                        "gekappt": False}) as grep:
            nadel_suchen(_zeile(1, "unter/a.md"), "x")

        pfad, wurzel = grep.call_args[0][0], grep.call_args[0][1]
        self.assertEqual("/files/unter/a.md", str(pfad))
        self.assertEqual("/files", str(wurzel))


class TestKeinSchreibpfadInReichweite(unittest.TestCase):
    """Nicht „wird nicht benutzt", sondern nicht importiert."""

    def test_der_zoom_kennt_keine_redaktion(self) -> None:
        """Ein Recht, das nicht im Modul liegt, kann kein Prompt herbeireden."""
        quelltext: str = open(zoom_mod.__file__.replace(".pyc", ".py"),
                              encoding="utf-8").read()

        for verboten in ("redaktion", "versionierung", "absatz_einfuegen",
                         "absatz_aendern", "schreiben"):
            self.assertNotIn(f"import {verboten}", quelltext)
            self.assertNotIn(f"from tools.dateien.{verboten}", quelltext)

    def test_die_suche_kennt_nur_den_index(self) -> None:
        """Sie liest Zeilen über Dateien, nie Dateien."""
        quelltext: str = open(suche_mod.__file__.replace(".pyc", ".py"),
                              encoding="utf-8").read()

        self.assertNotIn("tools.dateien", quelltext)
        self.assertNotIn("open(", quelltext)


if __name__ == "__main__":
    unittest.main()
