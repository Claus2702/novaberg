"""Tests: Jeder Turn traegt eine Landschaft — auch der ohne Vorausdenken.

Ziel (B1 aus `novaberg-erreichbarkeit_k.md` §7): Die Landschafts-Ablesung
faellt nicht mehr aus, weil das Vorausdenken ausfaellt. Wo die Antizipation
trotzdem nicht laeuft, benennt `gv_detail['vorausdenken']` den Grund, und
zwar so, dass keine Auswertung ihn als ruhige Lage zaehlen kann.

Hintergrund, gemessen am 08.08.2026 ueber 845 Rohturns aus `pipeline_log`
(`art='turn_roh'`, die dort gespeicherte `user_emotion` ist dieselbe, die der
Node gelesen hat — die spaete Perzeption im CharacterGraph laeuft mit
`perzeption_rolle='assistant'` und schreibt nach `internal`):

    ohne Landschaft            184 von 845  (21,8 %)
      davon Skip                88
      davon Krise                4
      davon Laenge 0 gerechnet  92

    zwoelf Validierungsboegen  101 von 360  (28,1 %)

Die Aufteilung nach Beziehungsdynamik ist der eigentliche Befund:

    neutral        0 von 340        distanz       82 von 164  (50 %)
    vertrauen      0 von 296        hilfesuchend   9 von  23  (39 %)
    dankbar        0 von   7        angriff        5 von  15  (33 %)

**Das Messgeraet schaltete sich genau auf der fernen Haelfte der Naehe-Achse
ab und nie auf der nahen** — also dort, wo `wartezimmer`, `schlachtfeld`,
`nebel` und `regen` liegen. Der Befund des Konzepts, im echten Gespraech seien
vier Landschaften nie betreten worden, stand damit auf einer Ablesung, die auf
genau diesen Eingaben aus war.

Zeuge: Die Erwartung stammt aus dem Konzept, nicht aus dem Code, der sie
erfuellt. `novaberg-gv-strategie_k.md` §3 definiert die Landschaft als Lage
des Gespraechs auf sechs Achsen; `novaberg-node-gv_k.md` definiert die
Vektorlaenge als Zahl der erlaubten Gedankenspruenge. Das eine ist ein
Zustand, das andere eine Entscheidung darueber — dass die Entscheidung den
Zustand loeschte, folgt aus keinem der beiden Dokumente.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from graph.nodes import gespraechsvektor as gv_modul
from graph.personality import Emotion, Personality

# Die vierzehn Landschaften, von Hand aus `novaberg-gv-strategie_k.md` §6
# uebertragen — nicht aus dem Modul importiert, damit die Erwartung eine
# andere Quelle hat als das Prueobjekt. Ein leerer oder erfundener Cluster
# faellt damit auf, und nicht nur ein leerer String.
BEKANNTE_LANDSCHAFTEN: frozenset = frozenset({
    "feuerwerk", "kissenschlacht", "werkstatt", "glut", "bier", "foyer",
    "regen", "schmollen", "nebel", "gewitter", "schlachtfeld", "beichte",
    "wartezimmer", "paradox",
})


def _turn(**emotionsfelder: str | float) -> dict:
    """Ein Zustand mit echtem Perzeptionsobjekt, sonst leer.

    `internal` bleibt weg: Ohne Novas Raum greifen die Neutralwerte von
    `achsen_berechnen`, und genau das ist der Cold-Start-Fall, in dem ein
    Messbogen anfaengt.
    """
    return {
        "user_id":      "test_gv_landschaft",
        "character_id": "test_gv_landschaft",
        "external":     Personality(emotion=Emotion(**emotionsfelder)),
    }


def _detail(zustand: dict) -> dict:
    """Laesst den Node echt laufen und gibt sein `gv_detail` zurueck.

    Nur der LLM-Aufruf ist ersetzt. Alles andere — Farbton, Neugier,
    Initiative, Achsen, Sektor — rechnet, und zwar in der Reihenfolge, um die
    es hier geht.
    """
    with patch.object(gv_modul, "_hypothese_destillieren",
                      return_value=("Hypothese", {})):
        ergebnis = gv_modul.gespraechsvektor(zustand)
    return ergebnis.get("gv_detail") or {}


class JederAusgangTraegtEineLandschaftTest(unittest.TestCase):
    """Alle drei Wege durch den Node liefern eine Landschaft."""

    def test_der_skip_traegt_eine_landschaft(self) -> None:
        """Begruessung und Meta reden auch in einem Raum."""
        detail: dict = _detail(_turn(intent="meta"))

        self.assertEqual(gv_modul.VORAUSDENKEN_SKIP, detail["vorausdenken"])
        self.assertIn(detail["cluster"], BEKANNTE_LANDSCHAFTEN)

    def test_die_gerechnete_null_traegt_eine_landschaft(self) -> None:
        """Der haeufigste Ausfall des Bestands: `distanz`, sonst nichts.

        1,0 minus 0,5 fuer die Distanz ergibt genau 0,5 — und `round(0.5)`
        ist in Python 0. Diese eine Lage stand 18 mal im Bestand.
        """
        detail: dict = _detail(_turn(
            intent="knowledge", mode="berichtend", emotion="neutral",
            relationship_dynamic="distanz", language_style="fachlich",
        ))

        self.assertEqual(gv_modul.VORAUSDENKEN_LAENGE_NULL, detail["vorausdenken"])
        self.assertEqual(0, detail["laenge"])
        self.assertIn(detail["cluster"], BEKANNTE_LANDSCHAFTEN)

    def test_die_krise_traegt_eine_landschaft(self) -> None:
        """Der Turn, in dem die Lage am meisten zaehlt, hatte bisher keine."""
        detail: dict = _detail(_turn(
            intent="personal", emotion="traurigkeit",
            emotions_vector="absturz", arousal=0.9,
        ))

        self.assertEqual(gv_modul.VORAUSDENKEN_KRISE, detail["vorausdenken"])
        self.assertIn(detail["cluster"], BEKANNTE_LANDSCHAFTEN)

    def test_der_normale_weg_meldet_sich_als_gelaufen(self) -> None:
        """Der positive Zwilling.

        Ohne ihn koennte der Node auf allen Wegen `skip` melden und alle
        Zusicherungen darueber blieben gruen.
        """
        detail: dict = _detail(_turn(
            intent="knowledge", emotion="begeisterung", arousal=0.8,
            relationship_dynamic="vertrauen", language_style="locker",
        ))

        self.assertEqual(gv_modul.VORAUSDENKEN_GELAUFEN, detail["vorausdenken"])
        self.assertGreater(detail["laenge"], 0)
        self.assertIn(detail["cluster"], BEKANNTE_LANDSCHAFTEN)


class DieKriseIstVonDerArithmetikUnterscheidbarTest(unittest.TestCase):
    """Zwei Wege zur Laenge 0, zwei Marken.

    Das ist die Zeile, die B1 verlangt: die Ausfaelle **je Ursache getrennt**.
    Eine gemeinsame Marke haette die Messung um genau die Frage gebracht, fuer
    die sie erhoben wird — die Krise ist eine Entscheidung des Konzepts, die
    gerechnete Null ein Ergebnis der Gewichte.
    """

    def test_beide_liefern_laenge_null(self) -> None:
        """Vorbedingung: Beide Wege enden wirklich bei derselben Zahl."""
        krise: dict = _detail(_turn(
            emotion="traurigkeit", emotions_vector="absturz", arousal=0.9,
        ))
        arithmetik: dict = _detail(_turn(
            mode="fachgespraech", relationship_dynamic="distanz",
        ))

        self.assertEqual(0, krise["laenge"])
        self.assertEqual(0, arithmetik["laenge"])

    def test_und_tragen_trotzdem_verschiedene_marken(self) -> None:
        """Und genau das ist die Trennung, die B1 verlangt."""
        krise: dict = _detail(_turn(
            emotion="traurigkeit", emotions_vector="absturz", arousal=0.9,
        ))
        arithmetik: dict = _detail(_turn(
            mode="fachgespraech", relationship_dynamic="distanz",
        ))

        self.assertNotEqual(krise["vorausdenken"], arithmetik["vorausdenken"])


class KeinAusgangLaesstFelderWegTest(unittest.TestCase):
    """Alle drei Wege liefern dieselbe Schluesselmenge.

    Der Grund ist kein Ordnungssinn: Der Dispatcher schreibt `gv_detail` nach
    Redis, das GV-Panel liest es, und der Haltungs-Knoten nimmt den Cluster
    daraus. Ein Weg, der einen Schluessel weglaesst, bricht sie erst beim
    Verbraucher — zwei Knoten spaeter und ohne Bezug zur Ursache. Genau so
    entstand der Befund, den B1 behebt: Zwei Wege schrieben ueberhaupt kein
    `gv_detail`, und der Haltungs-Knoten erbte ein leeres Dict.
    """

    def test_skip_und_normalweg_tragen_dieselben_schluessel(self) -> None:
        """Der Weg, der frueher gar nichts schrieb."""
        skip: dict = _detail(_turn(intent="meta"))
        voll: dict = _detail(_turn(
            intent="knowledge", emotion="begeisterung", arousal=0.8,
            relationship_dynamic="vertrauen", language_style="locker",
        ))

        self.assertEqual(set(voll), set(skip))

    def test_die_gerechnete_null_traegt_dieselben_schluessel(self) -> None:
        """Der zweite Weg, der frueher gar nichts schrieb."""
        null: dict = _detail(_turn(
            mode="fachgespraech", relationship_dynamic="distanz",
        ))
        voll: dict = _detail(_turn(
            intent="knowledge", emotion="begeisterung", arousal=0.8,
            relationship_dynamic="vertrauen", language_style="locker",
        ))

        self.assertEqual(set(voll), set(null))


class DieAntizipationsHaelfteBleibtEhrlichLeerTest(unittest.TestCase):
    """Eine Landschaft ohne Strategie ist etwas anderes als eine mit leerer.

    `22_STILLE_FEHLER.md` §3: Ein Wert allein kann den Unterschied nicht
    tragen, es braucht ein zweites Feld. Seit die Landschaft in jedem Turn
    dasteht, ist `vorausdenken` dieses Feld — ohne es waere ein Turn ohne
    Vorausdenken von einem mit ergebnislosem Vorausdenken nicht zu trennen.
    """

    def test_ohne_vorausdenken_bleiben_strategie_und_vehikel_leer(self) -> None:
        """Ohne Lauf gibt es kein Werkzeug — und keins wird erfunden."""
        detail: dict = _detail(_turn(intent="meta"))

        self.assertEqual("", detail["strategie"])
        self.assertEqual("", detail["vehikel"])
        self.assertEqual("", detail["absicht"])
        self.assertFalse(detail["strategie_aktiv"])

    def test_die_luechensuche_laeuft_auf_keinem_der_beiden_wege(self) -> None:
        """Die vorgezogene Messung darf das teure Tor nicht mitziehen.

        Die Suche stellt Datenbankabfragen. Liefe sie ab sofort auch in
        Turns ohne Vorausdenken, waere die Reparatur teurer als der Defekt.
        """
        for name, zustand in (
            ("skip",   _turn(intent="meta")),
            ("laenge", _turn(mode="fachgespraech", relationship_dynamic="distanz")),
        ):
            with self.subTest(weg=name), \
                 patch.object(gv_modul, "_hypothese_destillieren",
                              return_value=("Hypothese", {})), \
                 patch.object(gv_modul, "wissensluecken_finden") as suche:
                gv_modul.gespraechsvektor(zustand)
                suche.assert_not_called()

    def test_die_aufnahmebereitschaft_wird_auch_ohne_vorausdenken_gemessen(self) -> None:
        """Dieselbe Luecke wie bei der Landschaft, eine Groesse weiter.

        Chat 116 zog die Bereitschaft vor die Laengen-SCHWELLE (Laenge < 2),
        nicht vor die beiden `return`s davor. Bei Skip und bei Laenge 0 wurde
        sie deshalb bis zum 08.08.2026 nie gerechnet — und 0.00 ist der Wert,
        den das Konzept fuer die Krise reserviert.
        """
        detail: dict = _detail(_turn(intent="meta"))

        self.assertGreater(detail["aufnahmebereitschaft"], 0.0)


if __name__ == "__main__":
    unittest.main()
