"""Tests: Jeder Dienst am Empfang mit Objekt-Merkmal haelt genau einen gueltigen Vektor.

Ziel (Scheibe 12, Teil C1): Nach dem Start liegt fuer jeden Dienst am Empfang,
der ein Objekt-Merkmal deklariert, genau ein gueltiger Vektor seines Merkmals
bereit — heute Timeline und Notizen —, und kein Zustellweg aendert sich.

Zeugen dieser Datei:
  * **Der Wortlaut ist bezeugt, nicht nur vorhanden.** Die Schwellen der Naehe
    (Untergrenze 0,40, Abstand 0,04) gelten fuer genau diese Zeichen und dieses
    Modell; eine Umformulierung, auch nur Umlaute statt Umschrift, macht die
    Eichung ungueltig und soll hier rot werden, nicht erst im Schattenlauf.
  * **Der Empfang liest das Merkmal nicht.** Das Brett traegt den Merkmalstext
    nicht — die Deklaration ist Struktur, keine Zustellregel.
  * **Ein unbrauchbarer Vektor fehlt laut**, statt als Nullvektor jede Naehe
    auf "nicht nahe" zu druecken.

**Was dieser Test NICHT kann:** ob der Embed-Worker im Betrieb dieselben Vektoren
liefert wie die Eichung. Das zeigt die Messung am laufenden Server.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import math
import unittest

from agents import AgentRegistry, discover_agents
from agents.base import BaseAgent
from agents.nmcp import aushaenge_sammeln
from agents.object_feature import (
    _VECTORS,
    build_embed_text,
    feature_vectors,
    feature_vectors_ensure,
)
from plugins import discover_managers

# Die geeichten Fassungen vom 16.09.2026 (T3_verben, N3_sache), Zeichen fuer Zeichen.
GEEICHT_TIMELINE = (
    "Eine Handlung, die zu einer Zeit ausgefuehrt wird, oder ein Ereignis, das zu "
    "einer Zeit eintritt: hingehen, abgeben, treffen, anrufen, abholen, stattfinden, "
    "beginnen, enden, ablaufen."
)
GEEICHT_NOTIZEN = (
    "Ein Gegenstand, ein Bedarf oder eine Eigenschaft, die festgehalten wird und "
    "nicht stattfindet: Mehl brauchen, Passwort, Reifengroesse, Unvertraeglichkeit, "
    "Vorrat, Rezept, Zaehlerstand."
)


class _Dienst:
    """Ein Stellvertreter mit genau den zwei Angaben, die das Modul liest."""

    def __init__(self, zustellart: str, objekt_merkmal: str) -> None:
        self.zustellart = zustellart
        self.objekt_merkmal = objekt_merkmal


def _vektor(text: str) -> list[float]:
    """Ein deterministischer Vektor je Text, nie Null."""
    return [float(len(text)), 1.0, 0.5]


async def _einbetten(text: str) -> list[float]:
    return _vektor(text)


class DeklarationTest(unittest.TestCase):
    """Die Dienste tragen den geeichten Wortlaut; der Empfang liest ihn nicht."""

    @classmethod
    def setUpClass(cls) -> None:
        discover_managers()
        discover_agents()

    def test_timeline_traegt_die_geeichte_fassung(self) -> None:
        self.assertEqual(AgentRegistry.finden("timeline").objekt_merkmal, GEEICHT_TIMELINE)

    def test_notizen_traegt_die_geeichte_fassung(self) -> None:
        self.assertEqual(AgentRegistry.finden("notizen").objekt_merkmal, GEEICHT_NOTIZEN)

    def test_die_vorgabe_ist_kein_merkmal(self) -> None:
        self.assertEqual(BaseAgent.objekt_merkmal.fget(object()), "")

    def test_genau_zwei_dienste_am_empfang_deklarieren_ein_merkmal(self) -> None:
        """Ein drittes Merkmal waere ungeeicht — es soll bemerkt werden, nicht mitlaufen."""
        mit = sorted(
            n for n, a in AgentRegistry.alle().items()
            if a.zustellart == "empfang" and a.objekt_merkmal.strip()
        )
        self.assertEqual(mit, ["notizen", "timeline"])

    def test_das_brett_traegt_das_merkmal_nicht(self) -> None:
        brett = aushaenge_sammeln("user")
        self.assertTrue(brett.strip())
        for merkmal in (GEEICHT_TIMELINE, GEEICHT_NOTIZEN):
            self.assertNotIn(merkmal, brett)
            self.assertNotIn(merkmal.split(":")[1].strip(), brett)


class EmbedTextTest(unittest.TestCase):
    """Der Embed-Text ist das Merkmal selbst."""

    def test_leeres_merkmal_ist_ein_fehler(self) -> None:
        for leer in ("", "   ", "\n"):
            with self.assertRaises(ValueError):
                build_embed_text(leer)

    def test_der_text_bleibt_bis_auf_den_rand_unveraendert(self) -> None:
        self.assertEqual(build_embed_text(f"  {GEEICHT_TIMELINE}\n"), GEEICHT_TIMELINE)


class EinbettenTest(unittest.IsolatedAsyncioTestCase):
    """Genau ein gueltiger Vektor je Dienst mit Merkmal, sonst laut keiner."""

    def setUp(self) -> None:
        _VECTORS.clear()

    def tearDown(self) -> None:
        _VECTORS.clear()

    async def test_nur_dienste_am_empfang_mit_merkmal_bekommen_einen_vektor(self) -> None:
        dienste = {
            "a": _Dienst("empfang", "Ein Objekt."),
            "b": _Dienst("empfang", ""),
            "c": _Dienst("queue", "Ein anderes Objekt."),
            "d": _Dienst("empfang", "Noch ein Objekt."),
        }
        ergebnis = await feature_vectors_ensure(dienste, embed=_einbetten)
        self.assertEqual(sorted(ergebnis), ["a", "d"])
        self.assertEqual(ergebnis["a"].text, "Ein Objekt.")
        self.assertEqual(ergebnis["a"].vector, tuple(_vektor("Ein Objekt.")))

    async def test_mit_logs_der_bestand_wird_benannt(self) -> None:
        with self.assertLogs("ki_server.agents.object_feature", level="INFO") as log:
            await feature_vectors_ensure({"a": _Dienst("empfang", "X.")}, embed=_einbetten)
        self.assertTrue(any("1 von 1" in z for z in log.output))

    async def test_ein_fehler_nimmt_nur_diesem_dienst_den_vektor(self) -> None:
        async def einbetten(text: str) -> list[float]:
            if text == "kaputt":
                raise RuntimeError("Embed-Worker aus")
            return _vektor(text)

        dienste = {"a": _Dienst("empfang", "kaputt"), "b": _Dienst("empfang", "heil")}
        with self.assertLogs("ki_server.agents.object_feature", level="ERROR") as log:
            ergebnis = await feature_vectors_ensure(dienste, embed=einbetten)
        self.assertEqual(sorted(ergebnis), ["b"])
        self.assertTrue(any("'a'" in z for z in log.output))

    async def test_unbrauchbare_vektoren_werden_laut_verworfen(self) -> None:
        for kaputt in ([], [0.0, 0.0, 0.0], [1.0, math.nan, 0.0], [1.0, math.inf, 0.0]):
            with self.subTest(vektor=kaputt):
                _VECTORS.clear()

                async def einbetten(text: str, v: list[float] = kaputt) -> list[float]:
                    return v

                with self.assertLogs("ki_server.agents.object_feature", level="ERROR"):
                    ergebnis = await feature_vectors_ensure(
                        {"a": _Dienst("empfang", "X.")}, embed=einbetten,
                    )
                self.assertEqual(ergebnis, {})

    async def test_abweichende_dimension_wird_verworfen(self) -> None:
        async def einbetten(text: str) -> list[float]:
            return [1.0, 2.0] if text == "kurz" else [1.0, 2.0, 3.0]

        dienste = {"a": _Dienst("empfang", "lang"), "b": _Dienst("empfang", "kurz")}
        with self.assertLogs("ki_server.agents.object_feature", level="ERROR"):
            ergebnis = await feature_vectors_ensure(dienste, embed=einbetten)
        self.assertEqual(sorted(ergebnis), ["a"])

    async def test_ein_gescheiterter_neulauf_laesst_keinen_alten_vektor_stehen(self) -> None:
        dienste = {"a": _Dienst("empfang", "alt")}
        await feature_vectors_ensure(dienste, embed=_einbetten)
        self.assertIn("a", feature_vectors())

        async def kaputt(text: str) -> list[float]:
            raise RuntimeError("aus")

        with self.assertLogs("ki_server.agents.object_feature", level="ERROR"):
            await feature_vectors_ensure({"a": _Dienst("empfang", "neu")}, embed=kaputt)
        self.assertNotIn("a", feature_vectors())

    async def test_eine_kaputte_deklaration_nimmt_nur_diesem_dienst_den_vektor(self) -> None:
        """Wie bei der Anmeldung: ein fehlerhafter Dienst verhindert den Start nicht."""

        class _Wirft:
            zustellart = "empfang"

            @property
            def objekt_merkmal(self) -> str:
                raise AttributeError("kaputt")

        dienste = {
            "a": _Wirft(),
            "b": _Dienst("empfang", None),  # type: ignore[arg-type]
            "c": _Dienst("empfang", "heil"),
        }
        with self.assertLogs("ki_server.agents.object_feature", level="ERROR") as log:
            ergebnis = await feature_vectors_ensure(dienste, embed=_einbetten)
        self.assertEqual(sorted(ergebnis), ["c"])
        self.assertTrue(any("'a'" in z for z in log.output))
        self.assertTrue(any("'b'" in z for z in log.output))

    async def test_der_leser_bekommt_eine_kopie(self) -> None:
        await feature_vectors_ensure({"a": _Dienst("empfang", "X.")}, embed=_einbetten)
        kopie = feature_vectors()
        kopie.clear()
        self.assertIn("a", feature_vectors())

    async def test_falscher_eingabetyp_ist_ein_fehler(self) -> None:
        with self.assertRaises(TypeError):
            await feature_vectors_ensure([], embed=_einbetten)


if __name__ == "__main__":
    unittest.main()
