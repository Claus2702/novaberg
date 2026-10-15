"""Zeugen: die vier Falsifikationsproben der Faszination (§12 des Konzepts).

Ziel: Ob die Faszination tut, wofuer sie entworfen wurde, steht als Zeuge in
der Suite — nicht als Rechnung auf Papier. Jede Probe laeuft ueber den ganzen
Faktorsatz (Bindung, Merkmalszug, Praegungs- und Strangzug, Modulatoren,
`faszination`), nicht ueber einen einzelnen Faktor.

    1. Valenzblindheit   Kriegsgeschichte und Gartenkraeuter ziehen gleich.
    2. Neugier           Nur `ungewissheit` erschoepft sich durch Hinsehen.
    3. Der Zwilling      Ein nie gezaehlter Traeger erbt die Faszination seines
                         gezaehlten Zwillings. HEUTE ROT (siehe unten).
    4. Der Botaniker     Dieselbe Sache, mehr Naehe und Faeden: ein anderer Wert.

**Was „deutlich“ heisst.** Der Strangzug liegt auf [1,0, 1,0 + FASZ_STRANGZUG_HUB].
Deutlich ist ein Unterschied im Strangzug ab einem Viertel des Hubs (0,15) und
ein Unterschied in der Faszination ab 0,05 — einem Zwanzigstel der Skala [0, 1]
und rund das Fuenfhundertfache der Rundung auf vier Stellen, mit der die
Traegerwerte ins Protokoll gehen. Beide Schwellen stehen unter dem kleinsten
Unterschied der Beispiele unten (Faden-Achse allein: Strangzug 0,243,
Faszination 0,061).

**Die Beispiele sind unter der Deckelung gerechnet.** `faszination` kappt bei
`roh = FASZ_MAXIMUM`; zwei Traeger ueber dem Deckel stehen beide auf 1,0, und
„gleich“ waere dann keine Aussage. Jeder Gleichheits-Zeuge prueft deshalb auch
`roh < FASZ_MAXIMUM`.

Reine Rechnung: keine Datenbank, kein Modell, kein Netz. Wo der Bestandspfad
gefahren wird, ersetzt ein Doppel die beiden Lesefunktionen des Speichers oder
den Cursor.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from config import (
    BINDUNG_HALBSTRECKE_VERWEILDAUER,
    BINDUNG_HALBSTRECKE_WIEDERKEHR,
    FASZ_AROUSAL_SCHEITEL,
    FASZ_MAXIMUM,
    FASZ_STRANGZUG_HUB,
    QUALITAET_KANON,
    QUALITAET_VERFALL_BODEN,
    QUALITAET_VERFALL_HALBSTRECKE_BERUEHRUNGEN,
    QUALITAET_VERFALL_UEBER_BERUEHRUNGEN,
)
from ei.fascination import (
    bindung_roh,
    dominante_dimension,
    faszination,
    merkmalszug,
    modulatoren_aus_turn,
    profil_verfallen,
    qualitaet_verfall,
    strangzug,
)
from memory.fascination_store import faszination_der_gelesenen
from memory.praegung import einfaerbung_falten, strang_staerke
from tests.test_praegung_strang import _Cursor, _mit_cursor
from tests.test_praegung_zug import NEGATIV, SCHUETZEND
from tests.test_praegung_zug import _lauf as zug_lauf

STORE: str = "memory.fascination_store"
NOW: datetime = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)

#: Awe-Dyade: Furcht (Sektor 3) und Ueberraschung (Sektor 4) zusammen —
#: Regel 2 von `strang_richtung`, Annaeherung, ohne das Rad zu fragen.
WAR: list[int] = [0, 0, 2, 2, 0, 0, 0, 0]
#: Dominant Freude (Sektor 1) — Regel 3, Annaeherung.
GARDEN: list[int] = [4, 0, 0, 0, 0, 0, 0, 0]

#: Eine Reihe der Strangabfrage: (emotion, faeden, faeden mit Salienz, Salienzsumme).
WAR_ROWS: list[tuple] = [("stress", 2, 2, 1.0), ("ueberrascht", 2, 2, 1.0)]
GARDEN_ROWS: list[tuple] = [("freude", 4, 4, 2.0)]

#: Zehn Beruehrungen: zweimal die Halbstrecke, `ungewissheit` steht klar unten.
RESEARCHED: int = int(2 * QUALITAET_VERFALL_HALBSTRECKE_BERUEHRUNGEN)

#: Unterschiede, ab denen zwei Werte „deutlich“ verschieden heissen (siehe Kopf).
CLEAR_ZUG: float = 0.25 * FASZ_STRANGZUG_HUB
CLEAR_VALUE: float = 0.05


def _profile(**levels: float) -> dict[str, float]:
    """Ein volles Profil: alle sechs Dimensionen, nicht genannte auf 0,0."""
    return {name: levels.get(name, 0.0) for name in QUALITAET_KANON}


def _counted_bindung() -> float:
    """Die Bindung eines gezaehlten Traegers: beide Zaehler auf der Halbstrecke."""
    return bindung_roh(
        BINDUNG_HALBSTRECKE_WIEDERKEHR, BINDUNG_HALBSTRECKE_VERWEILDAUER, 0.5,
    )


def _turn(emotion: str) -> dict[str, float]:
    """Die sechs Modulatoren eines Turns; nur die Emotion wechselt."""
    return modulatoren_aus_turn(
        arousal=FASZ_AROUSAL_SCHEITEL,
        emotion=emotion,
        emotions_vector="plateau",
        intent="task",
        mode="alltag",
        wissbegier=None,
    )


def _ladung(rows: list[tuple]) -> float:
    """Die echte Ladung eines Strangs aus `strang_staerke`, ueber einen Cursor."""
    cursor = _Cursor([rows, (0.0,)])
    with _mit_cursor(cursor):
        parts = strang_staerke("postgresql://nachgebildet", 1)
    assert parts is not None
    return parts["staerke"]


def _store_values(carriers: dict[int, dict], nearness: dict[int, dict]) -> dict[str, float]:
    """Die Werte, die der Speicher fuer gelesene Traeger rechnet — nur die Leser ersetzt."""
    with patch(f"{STORE}.traegerdaten_lesen", return_value=carriers), \
         patch(f"{STORE}.traeger_strangnaehe", return_value=nearness):
        result = faszination_der_gelesenen("postgresql://nachgebildet", sorted(carriers))
    return result["werte"]


class ValenceBlindnessTest(unittest.TestCase):
    """§12.1 — Kriegsgeschichte und Gartenkraeuter sind derselbe Mechanismus."""

    def _carrier(self, rows_hist: list[int], emotion: str) -> tuple[dict, float, float]:
        """Ein Traeger gleicher Bindung und gleichen Profils zu einem Strang."""
        run, _, _ = zug_lauf([(7, rows_hist, 0.8)], ladung=0.5, konfrontation=SCHUETZEND)
        value, roh = faszination(
            _counted_bindung(), merkmalszug(_profile(komplexitaet=1.0)),
            run["zug"], _turn(emotion),
        )
        return run, value, roh

    def test_war_and_garden_strands_give_the_same_value(self) -> None:
        war, war_value, war_roh = self._carrier(WAR, "traurigkeit")
        garden, garden_value, garden_roh = self._carrier(GARDEN, "freude")

        self.assertEqual("annaeherung", war["richtung"])
        self.assertIn("Awe-Dyade", war["grund"], "Der Kriegsstrang zieht nicht ueber Regel 2")
        self.assertEqual("annaeherung", garden["richtung"])
        self.assertEqual(
            garden["zug"], war["zug"],
            "Der Praegungszug unterscheidet nach der Valenz des Strangs",
        )
        self.assertGreater(war["zug"], 1.0, "Der Zug ist neutral — die Probe saehe nichts")
        self.assertLess(max(war_roh, garden_roh), FASZ_MAXIMUM, "Der Deckel macht beide gleich")
        self.assertEqual(garden_value, war_value)
        self.assertGreater(war_value, 0.0)

    def test_a_strand_read_as_avoidance_does_not_pull(self) -> None:
        """Gegenfall: Vermeidung zieht absichtlich nicht — das ist keine Valenzfrage."""
        avoided, avoided_value, _ = self._carrier(NEGATIV, "traurigkeit")
        _, war_value, _ = self._carrier(WAR, "traurigkeit")

        self.assertIsNone(avoided["richtung"], "Der Vermeidungsstrang traegt zum Zug bei")
        self.assertEqual("kein Strang mit Zug", avoided["grund"])
        self.assertEqual(1.0, avoided["zug"])
        self.assertLess(avoided_value, war_value)

    def test_the_turn_takes_no_side(self) -> None:
        """Dieselbe Sache im selben Turn, einmal froh und einmal traurig erlebt."""
        bindung = _counted_bindung()
        zug = merkmalszug(_profile(komplexitaet=1.0))
        happy, happy_roh = faszination(bindung, zug, 1.24, _turn("freude"))
        sad, sad_roh = faszination(bindung, zug, 1.24, _turn("traurigkeit"))
        flat, _ = faszination(bindung, zug, 1.24, _turn("neutral"))

        self.assertLess(max(happy_roh, sad_roh), FASZ_MAXIMUM)
        self.assertEqual(happy, sad)
        self.assertLess(flat, sad, "Ein unbesetzter Turn bindet so gut wie ein besetzter")

    def test_the_load_of_a_strand_is_blind_to_the_sign_of_its_threads(self) -> None:
        """Dieselben Betraege, anderes Vorzeichen, dieselbe Ladung."""
        negative = _ladung([("traurigkeit", 4, 4, 2.0)])
        positive = _ladung([("freude", 4, 4, 2.0)])
        # |−0,8| == |0,8|: derselbe Betrag, das Vorzeichen allein macht nichts.
        self.assertEqual(positive, negative)

    def test_the_negative_clock_never_reaches_the_pull_or_the_value(self) -> None:
        """§8.4 — `sektor_faktor` laeuft nur in der Einfaerbung, nie in der Faszination."""
        with patch("memory.praegung.sektor_faktor", return_value=(1.5, 5)) as clock:
            run, _, _ = zug_lauf([(7, WAR, 0.8)], konfrontation=SCHUETZEND)
            _ladung(WAR_ROWS)
            faszination(_counted_bindung(), 1.0, run["zug"], _turn("traurigkeit"))
            _store_values(
                {1: {"profil": _profile(komplexitaet=1.0), "tage": 3, "turns": 3,
                     "eigenimpuls": 0.5}},
                {1: {"naehe": 0.8, "faden_zahl": 4}},
            )

        self.assertEqual(
            0, clock.call_count,
            "Der valenzabhaengige Verfall erreicht die Faszination — das Alte Unrecht "
            "wuerde dann auch an der Aufmerksamkeit leiser",
        )

    def test_the_colouring_is_the_reader_of_the_negative_clock(self) -> None:
        """Zwilling des Zeugen davor: Der Doppelgaenger sitzt an der Stelle, die ruft."""
        with patch("memory.praegung.sektor_faktor", return_value=(1.5, 5)) as clock:
            einfaerbung_falten(0.8, "traurigkeit", NOW - timedelta(days=60), [], NOW)

        self.assertEqual(1, clock.call_count)

    def test_the_negative_clock_does_run_in_the_colouring(self) -> None:
        """Zwilling: dieselbe Uhr wirkt auf die Einfaerbung — sonst saehe die Probe nichts."""
        sad = einfaerbung_falten(0.8, "traurigkeit", NOW - timedelta(days=60), [], NOW)
        glad = einfaerbung_falten(0.8, "freude", NOW - timedelta(days=60), [], NOW)

        self.assertEqual(glad["ausschlag_aktuell"], sad["ausschlag_aktuell"])
        self.assertAlmostEqual(0.0, glad["abstand"], places=9)
        self.assertGreater(sad["abstand"], 0.0, "Die negative Uhr laeuft nicht schneller")
        self.assertLess(sad["einfaerbung"], glad["einfaerbung"])

    # Befund, kein Baufehler: Die Ladung traegt `mittel(|valenz|)`, und die Awe-Dyade
    # zieht eine Ueberraschung (|0,1|) in den Betrag. Ein Kriegsstrang aus zwei
    # Furcht- und zwei Ueberraschungsfaeden laedt deshalb schwaecher (0,48) als ein
    # Gartenstrang aus vier Freudefaeden (0,56) — gegen die Probe aus §12.1, die
    # *denselben* Wert verlangt. Der Zeuge haelt den heutigen Zustand fest.
    def test_finding_the_awe_dyade_loads_weaker_than_a_pure_strand(self) -> None:
        war_load = _ladung(WAR_ROWS)
        garden_load = _ladung(GARDEN_ROWS)

        self.assertLess(war_load, garden_load)
        war, _, _ = zug_lauf([(7, WAR, 0.8)], ladung=war_load, konfrontation=SCHUETZEND)
        garden, _, _ = zug_lauf([(7, GARDEN, 0.8)], ladung=garden_load, konfrontation=SCHUETZEND)
        self.assertLess(war["zug"], garden["zug"])


class NeugierBoundaryTest(unittest.TestCase):
    """§12.2 — Faszination erlischt genau dann, wenn ihre tragende Dimension erschoepfbar ist."""

    def _before_after(self, profile: dict[str, float]) -> tuple[float, float, float, float]:
        """Wert und Rohwert desselben Traegers vor und nach der Recherche."""
        after = profil_verfallen(profile, tage=0, beruehrungen=RESEARCHED)
        before_value, before_roh = faszination(_counted_bindung(), merkmalszug(profile), 1.0)
        after_value, after_roh = faszination(_counted_bindung(), merkmalszug(after), 1.0)
        return before_value, before_roh, after_value, after_roh

    def test_a_carrier_not_standing_on_uncertainty_keeps_its_fascination(self) -> None:
        profile = _profile(komplexitaet=1.0)
        before_value, _, after_value, _ = self._before_after(profile)

        self.assertGreater(before_value, 0.0)
        self.assertAlmostEqual(before_value, after_value, places=9)

    def test_a_carrier_standing_on_uncertainty_sinks(self) -> None:
        profile = _profile(ungewissheit=1.0)
        before_value, before_roh, after_value, after_roh = self._before_after(profile)

        self.assertLess(after_value, before_value)
        self.assertLess(after_roh, 0.75 * before_roh, "Zehn Beruehrungen senken kaum")
        self.assertGreaterEqual(
            after_roh, QUALITAET_VERFALL_BODEN * before_roh - 1e-9,
            "Der Boden ist unterschritten — eine Qualitaet verschwindet nicht",
        )

    def test_a_mixed_profile_keeps_its_dominant_dimension_and_almost_its_value(self) -> None:
        profile = _profile(komplexitaet=1.0, ungewissheit=0.5)
        after = profil_verfallen(profile, tage=0, beruehrungen=RESEARCHED)
        _, before_roh, _, after_roh = self._before_after(profile)

        self.assertEqual("komplexitaet", dominante_dimension(after)[0])
        # Nur der Zuschlag aus den uebrigen Dimensionen gibt nach; die tragende
        # Dimension haelt den Rest. Gerechnet: 1,035 vor, 1,021 nach — rund 99 %.
        self.assertGreaterEqual(after_roh, 0.9 * before_roh)

    def test_only_uncertainty_wears_out_by_looking(self) -> None:
        for name in QUALITAET_KANON:
            with self.subTest(dimension=name):
                after = qualitaet_verfall(name, 1.0, tage=0, beruehrungen=RESEARCHED)
                if name in QUALITAET_VERFALL_UEBER_BERUEHRUNGEN:
                    self.assertLess(after, 1.0)
                else:
                    self.assertAlmostEqual(1.0, after, places=9)

    def test_time_alone_does_not_exhaust_uncertainty(self) -> None:
        """Gegenrichtung: Ein Jahr ohne Hinsehen — die Neugier bleibt, die Weite nicht."""
        self.assertAlmostEqual(
            1.0, qualitaet_verfall("ungewissheit", 1.0, tage=365, beruehrungen=0), places=9,
        )
        self.assertLess(qualitaet_verfall("komplexitaet", 1.0, tage=365, beruehrungen=0), 1.0)


class TwinTest(unittest.TestCase):
    """§12.3 — Ein nie gezaehlter Traeger erbt die Faszination seines gezaehlten Zwillings."""

    PROFILE: dict[str, float] = _profile(komplexitaet=1.0, konflikt=0.5)

    def _values(self) -> dict[str, float]:
        """Zwei Knoten, ein Profil: der eine gezaehlt, der andere nie."""
        counted = {"profil": self.PROFILE, "tage": 3, "turns": 3, "eigenimpuls": 0.5}
        never = {"profil": self.PROFILE, "tage": 0, "turns": 0, "eigenimpuls": None}
        return _store_values({1: counted, 2: never}, {})

    def test_today_the_never_counted_twin_stands_at_zero(self) -> None:
        """Der heutige Zustand: Bindung 0, und die Bindung ist der erste Faktor der Kette."""
        values = self._values()

        self.assertEqual(0.0, bindung_roh(0, 0, None))
        self.assertGreater(values["1"], 0.0, "Der gezaehlte Zwilling traegt nichts")
        self.assertEqual(0.0, values["2"])

    # Heute rot, und zwar nach Lesart des Codes: Ein nie gezaehlter Traeger hat
    # `bindung_roh(0, 0, None) == 0.0`, und die Bindung ist der erste Faktor der
    # Kette. Das Konzept (`_k` §4.2, `_t` §10.2) will die Zaehler den Qualitaeten
    # gutgeschrieben, die der Traeger trug; gebaut ist das nicht (`_b` §14).
    # Kennung: FASZINATION-ZWILLING-ERBT-NICHT (Backlog Charakter). Wird der
    # Zeuge gruen, meldet der Lauf *unexpected success* — dann Kennzeichnung
    # entfernen und den Zeugen an die Naht der Gutschrift legen.
    @unittest.expectedFailure
    def test_the_never_counted_twin_inherits_the_fascination(self) -> None:
        values = self._values()

        self.assertGreater(
            values["2"], 0.0,
            "Der Zwilling mit demselben Profil erbt nichts — er steht auf null",
        )


class BotanistTest(unittest.TestCase):
    """§12.4 — Wer mehr Naehe und mehr Faeden hat, wird anders gezogen."""

    CARRIER: dict = {
        "profil": _profile(komplexitaet=1.0), "tage": 3, "turns": 3, "eigenimpuls": 0.5,
    }

    def _value(self, nearness: dict) -> float:
        """Der Wert desselben Traegers bei einer anderen Lage zum Strang."""
        return _store_values({1: dict(self.CARRIER)}, {1: nearness} if nearness else {})["1"]

    def test_more_threads_and_more_nearness_pull_clearly_harder(self) -> None:
        near_many = strangzug(0.9, 7)
        far_few = strangzug(0.2, 1)

        self.assertGreaterEqual(near_many - far_few, CLEAR_ZUG)
        self.assertGreaterEqual(
            self._value({"naehe": 0.9, "faden_zahl": 7})
            - self._value({"naehe": 0.2, "faden_zahl": 1}),
            CLEAR_VALUE,
        )

    def test_nearness_alone_changes_the_value_clearly(self) -> None:
        self.assertGreaterEqual(strangzug(0.9, 7) - strangzug(0.2, 7), CLEAR_ZUG)
        self.assertGreaterEqual(
            self._value({"naehe": 0.9, "faden_zahl": 7})
            - self._value({"naehe": 0.2, "faden_zahl": 7}),
            CLEAR_VALUE,
        )

    def test_thread_count_alone_changes_the_value_clearly(self) -> None:
        self.assertGreaterEqual(strangzug(0.9, 7) - strangzug(0.9, 1), CLEAR_ZUG)
        self.assertGreaterEqual(
            self._value({"naehe": 0.9, "faden_zahl": 7})
            - self._value({"naehe": 0.9, "faden_zahl": 1}),
            CLEAR_VALUE,
        )

    def test_no_strand_is_neutral_and_not_avoidance(self) -> None:
        """Abwesenheit ist nicht Vermeidung: ohne Strang steht der Wert nicht unter dem ohne Zug."""
        bare, _ = faszination(
            _counted_bindung(), merkmalszug(self.CARRIER["profil"]), 1.0,
        )
        absent = self._value({})

        self.assertEqual(1.0, strangzug(None, 0))
        self.assertGreater(absent, 0.0)
        self.assertEqual(round(bare, 4), absent)

    def test_a_strand_on_the_far_side_or_without_threads_does_not_push_away(self) -> None:
        for nearness, threads in ((-0.5, 7), (0.0, 7), (0.9, 0)):
            with self.subTest(naehe=nearness, faeden=threads):
                self.assertEqual(1.0, strangzug(nearness, threads))

    def test_no_strand_at_all_leaves_the_turn_pull_neutral(self) -> None:
        run, _, _ = zug_lauf([])

        self.assertEqual(1.0, run["zug"])
        self.assertEqual("kein Strang", run["grund"])
        self.assertGreater(
            faszination(_counted_bindung(), 1.0, run["zug"])[0], 0.0,
        )


if __name__ == "__main__":
    unittest.main()
