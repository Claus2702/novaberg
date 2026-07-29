"""Tests: Der GV-Node bekommt seine zweite Wissensquelle aus dem Erinnerungsgraphen.

Ziel: Ein Turn, dessen Enricher Erinnerungen gefunden hat, erreicht die
Hypothesen-Destillation mit einem nicht-leeren Wissensblock — und ein Turn
ohne Erinnerungen mit einem leeren.

Hintergrund (Chat 115): Der Entity-Hop des GV-Nodes las die `fakten`-Tabelle.
Gemessen am 28.07.2026 hat sie 0 Zeilen und seit Synapsen P4 (Festlegung K2)
keinen Produzenten; zusaetzlich traf Hop 1 konstruktiv nicht — der Schluessel
ist eine Themenphrase, die Entitaetsnamen sind Eigennamen, beide ILIKE-
Richtungen 0 Treffer. 45 von 45 Laeufen lieferten leeren Kontext.

Die Quelle ist jetzt `state["lzg_resonanz"]`, das der Enricher legt: Anker aus
der Cosine-Suche (Schale 0) plus Nachbarn entlang `lzg_kanten` (Schale 1+).

Zeuge: Die Erinnerungen sind Literale dieser Datei — von Hand geschrieben, mit
von Hand bestimmten Erwartungen. Keine Seite des Vergleichs stammt aus
`_resonanz_kontext_laden` oder aus `spreading_lesen`. Die Schalen-Beschriftung
ist aus dem Konzept abgeleitet (Schale 0 = Anker = direkter Themenbezug), nicht
aus dem Code gelesen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes.gespraechsvektor import _resonanz_kontext_laden

# Von Hand geschriebene Erinnerungen. Die Inhalte sind bewusst unverwechselbar,
# damit ihr Auftauchen im Ergebnis nicht zufaellig sein kann.
ANKER_ERINNERUNG: dict = {
    "rang":          1,
    "knoten_id":     4711,
    "inhalt":        "Der Ereignishorizont wurde als Grenze der Beobachtbarkeit besprochen",
    "themen":        ["Schwarze Loecher", "Ereignishorizont"],
    "entitaet_ids":  [12],
    "emotion":       "neugierig",
    "gewicht_decay": 0.82,
    "schale":        0,
    "pfad":          [],
}

NACHBAR_ERINNERUNG: dict = {
    "rang":          2,
    "knoten_id":     4712,
    "inhalt":        "Die Hawking-Strahlung kam als Gegenbewegung zur Sprache",
    "themen":        ["Hawking-Strahlung"],
    "entitaet_ids":  [],
    "emotion":       "",
    "gewicht_decay": 0.41,
    "schale":        2,
    "pfad":          [{"kante_id": 99}],
}

ERINNERUNG_OHNE_INHALT: dict = {
    "rang":          3,
    "knoten_id":     4713,
    "inhalt":        "",
    "themen":        ["Gravitation"],
    "entitaet_ids":  [],
    "emotion":       "neutral",
    "gewicht_decay": 0.10,
    "schale":        1,
    "pfad":          [],
}


def _state(erinnerungen: list[dict] | None, *, mit_resonanz: bool = True) -> dict:
    """Baut den State, wie ihn der GV-Node nach dem Enricher vorfindet."""
    if not mit_resonanz:
        return {}
    return {
        "lzg_resonanz": {
            "anker_anzahl": 3,
            "sprung_tiefe": 2,
            "cluster":      "kissenschlacht",
            "nova_sektor":  "neugierig",
            "erinnerungen": erinnerungen or [],
        }
    }


class TestResonanzKontextGefuellt(unittest.TestCase):
    """Der positive Zwilling: Erinnerungen sind da und kommen an."""

    def test_beide_erinnerungen_erscheinen_im_block(self) -> None:
        text: str = _resonanz_kontext_laden(
            _state([ANKER_ERINNERUNG, NACHBAR_ERINNERUNG])
        )

        self.assertIn("Ereignishorizont wurde als Grenze", text)
        self.assertIn("Hawking-Strahlung kam als Gegenbewegung", text)
        self.assertEqual(2, len(text.strip().splitlines()))

    def test_schale_trennt_direkten_treffer_von_assoziation(self) -> None:
        """Schale 0 ist der Anker, Schale 2 ein Nachbar zweiter Ordnung.

        Ohne diese Unterscheidung liest das LLM eine ueber zwei Spruenge
        erreichte Erinnerung als Kernbezug des aktuellen Themas.
        """
        text: str = _resonanz_kontext_laden(
            _state([ANKER_ERINNERUNG, NACHBAR_ERINNERUNG])
        )

        anker_zeile:  str = [z for z in text.splitlines() if "Ereignishorizont" in z][0]
        nachbar_zeile: str = [z for z in text.splitlines() if "Hawking" in z][0]

        self.assertIn("direkt zum Thema", anker_zeile)
        self.assertNotIn("direkt zum Thema", nachbar_zeile)
        self.assertIn("2 Sprung(e)", nachbar_zeile)

    def test_themen_und_faerbung_reisen_mit(self) -> None:
        text: str = _resonanz_kontext_laden(_state([ANKER_ERINNERUNG]))

        self.assertIn("Schwarze Loecher", text)
        self.assertIn("neugierig", text)

    def test_leere_faerbung_erzeugt_kein_leeres_feld(self) -> None:
        """NACHBAR_ERINNERUNG hat emotion="" — das darf nicht als Feld erscheinen."""
        text: str = _resonanz_kontext_laden(_state([NACHBAR_ERINNERUNG]))

        self.assertNotIn("Faerbung:", text)


class TestResonanzKontextLeer(unittest.TestCase):
    """Die Leerfaelle — jeder mit seinem eigenen Grund."""

    def test_kein_lzg_resonanz_im_state(self) -> None:
        self.assertEqual("", _resonanz_kontext_laden(_state(None, mit_resonanz=False)))

    def test_resonanz_ohne_erinnerungen(self) -> None:
        self.assertEqual("", _resonanz_kontext_laden(_state([])))


class TestResonanzKontextFehlerpfade(unittest.TestCase):
    """Ein Knoten ohne Text ist ein Defekt der Schreibseite, kein Leerfall.

    Die Zusicherung prueft die Log-Zeile, nicht nur, dass nichts abstuerzt.
    """

    def test_erinnerung_ohne_inhalt_wird_benannt_uebersprungen(self) -> None:
        with self.assertLogs("ki_server.gespraechsvektor", level="ERROR") as protokoll:
            text: str = _resonanz_kontext_laden(
                _state([ANKER_ERINNERUNG, ERINNERUNG_OHNE_INHALT])
            )

        # Die brauchbare Erinnerung ueberlebt, die defekte nicht.
        self.assertIn("Ereignishorizont", text)
        self.assertEqual(1, len(text.strip().splitlines()))

        # Die Log-Zeile nennt den Knoten, nicht nur die Anzahl.
        gemeinsam: str = "\n".join(protokoll.output)
        self.assertIn("4713", gemeinsam)

    def test_alle_ohne_inhalt_ist_ein_fehler_kein_leerfall(self) -> None:
        with self.assertLogs("ki_server.gespraechsvektor", level="ERROR") as protokoll:
            text: str = _resonanz_kontext_laden(_state([ERINNERUNG_OHNE_INHALT]))

        self.assertEqual("", text)
        gemeinsam: str = "\n".join(protokoll.output)
        self.assertIn("keine mit Inhalt", gemeinsam)


class TestFaktenHopSchlaeft(unittest.TestCase):
    """Der alte Entity-Hop darf nicht unbemerkt wieder in den Pfad geraten.

    `_entity_kontext_laden` liegt schlafend im Modul und wartet auf M2.5b.
    Wuerde ihn jemand wieder verdrahten, faende der GV-Node bis dahin
    weiterhin nichts — und der Befund GV-ENTITY-HOP-FINDET-NICHTS waere
    zurueck, ohne dass ein Test rot wird. Dieser hier wird rot.
    """

    def test_gv_node_ruft_den_faktenpfad_nicht(self) -> None:
        import inspect

        from graph.nodes import gespraechsvektor

        quelle: str = inspect.getsource(gespraechsvektor.gespraechsvektor)
        self.assertNotIn("_entity_kontext_laden", quelle)
        self.assertIn("_resonanz_kontext_laden", quelle)


if __name__ == "__main__":
    unittest.main()
