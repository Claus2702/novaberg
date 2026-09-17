"""Tests: Der Empfang rechnet die Objekt-Naehe im Schatten und stellt danach nichts anders zu.

Ziel (Scheibe 12, Teil C2): Jeder Durchlauf des Routers hinterlaesst genau einen
Protokolleintrag mit dem Urteil ueber jedes akute Objekt der Lage — je Zettel fuer
sich: an jedem Dienst, dessen Merkmal die Untergrenze erreicht —, und kein Feld
des Zustands aendert sich dadurch.

Zeugen dieser Datei:
  * **Der Objekttext ist die Formel der Eichung.** Die Schwellen gelten fuer
    genau diese Zeichen; der Zeuge haelt die Formel gegen feste Erwartungen.
  * **Je Zettel fuer sich.** Ein Objekt ueber beiden Untergrenzen steht an
    beiden Zetteln, wie nah die zwei Naehen auch beieinander liegen; das Urteil
    ueber einen Dienst haengt nicht davon ab, welches andere Merkmal angemeldet
    ist. Die Grenze ist eingeschlossen, wie in der Eichung (`>=`).
  * **Der Zustand nach `route()` ist mit und ohne Schatten gleich** — gefahren
    durch den echten Knoten, nicht nur durch die Funktion. Der Aufruf im
    Router ist die Verdrahtung, und die Verdrahtung ist der Defekt, den ein
    Bausteinzeuge nicht sieht.
  * **Jeder Rueckkehrpfad schreibt einen Eintrag**, auch der Ausfall.

**Was dieser Test NICHT kann:** ob die Schwellen im Betrieb tragen. Das zeigt
der Schattenlauf selbst.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import copy
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.object_feature import FeatureVector
from agents.object_nearness import (
    OUTCOME_ASSIGNED,
    OUTCOME_BELOW_FLOOR,
    OUTCOME_SEVERAL,
    build_object_text,
    cosine,
    judge,
    shadow_nearness,
)
from graph.nodes import router


def _merkmale() -> dict[str, FeatureVector]:
    """Zwei Merkmale auf orthogonalen Achsen — Naehen sind dann ablesbar."""
    return {
        "notizen":  FeatureVector("notizen", "N", (0.0, 1.0, 0.0)),
        "timeline": FeatureVector("timeline", "T", (1.0, 0.0, 0.0)),
    }


def _objekt(name: str, akut: bool = True) -> dict:
    return {"name": name, "klasse": "vorgang", "akut": akut,
            "gedeckt": {"Datum": "morgen"}, "offen": ["Uhrzeit"]}


class ObjekttextTest(unittest.TestCase):
    """Die Formel der Eichung, Zeichen fuer Zeichen."""

    def test_volles_objekt(self) -> None:
        self.assertEqual(
            build_object_text({"name": "Zahnarzt", "klasse": "vorgang",
                               "gedeckt": {"Tag": "Montag", "Ort": "Praxis"},
                               "offen": ["Uhrzeit"]}),
            "Klasse: vorgang. Name: Zahnarzt. Eigenschaften: Tag, Ort, Uhrzeit",
        )

    def test_ohne_klasse_und_ohne_eigenschaften(self) -> None:
        self.assertEqual(build_object_text({"name": "Mehl"}), "Klasse: ohne. Name: Mehl")

    def test_werte_stehen_nicht_im_text(self) -> None:
        self.assertNotIn("Montag", build_object_text({"name": "X", "gedeckt": {"Tag": "Montag"}}))

    def test_kein_dict_ist_ein_fehler(self) -> None:
        with self.assertRaises(TypeError):
            build_object_text(["Zahnarzt"])  # type: ignore[arg-type]


class UrteilTest(unittest.TestCase):
    """Je Zettel fuer sich, die Grenze eingeschlossen."""

    def test_ein_empfaenger(self) -> None:
        u = judge(_objekt("A"), [1.0, 0.0, 0.0], _merkmale(), 0.40)
        self.assertEqual((u.receivers, u.outcome), (("timeline",), OUTCOME_ASSIGNED))
        self.assertAlmostEqual(u.top, 1.0)
        self.assertAlmostEqual(u.margin, 1.0)

    def test_unter_der_untergrenze_still(self) -> None:
        v = [0.3, 0.0, (1 - 0.09) ** 0.5]
        u = judge(_objekt("A"), v, _merkmale(), 0.40)
        self.assertEqual((u.receivers, u.outcome), ((), OUTCOME_BELOW_FLOOR))

    def test_knapp_beieinander_steht_an_beiden_zetteln(self) -> None:
        """Der Fall, den der Abstand still machte: 0,60 gegen 0,58."""
        v = [0.6, 0.58, (1 - 0.36 - 0.3364) ** 0.5]
        u = judge(_objekt("A"), v, _merkmale(), 0.40)
        self.assertEqual((u.receivers, u.outcome), (("notizen", "timeline"), OUTCOME_SEVERAL))

    def test_nur_ein_merkmal_ueber_der_grenze_bei_kleinem_abstand(self) -> None:
        """0,41 gegen 0,39: ein Empfaenger, obwohl der Abstand klein ist."""
        v = [0.41, 0.39, (1 - 0.1681 - 0.1521) ** 0.5]
        u = judge(_objekt("A"), v, _merkmale(), 0.40)
        self.assertEqual((u.receivers, u.outcome), (("timeline",), OUTCOME_ASSIGNED))

    def test_das_urteil_ueber_einen_zettel_haengt_nicht_am_nachbarn(self) -> None:
        """Ein weiteres, nahes Merkmal nimmt der Timeline das Objekt nicht."""
        v = [0.6, 0.0, 0.8]
        allein = judge(_objekt("A"), v, {"timeline": _merkmale()["timeline"]}, 0.40)
        mit_nachbar = judge(
            _objekt("A"), v,
            {**_merkmale(), "nachbar": FeatureVector("nachbar", "X", (0.6, 0.0, 0.8))}, 0.40,
        )
        self.assertIn("timeline", allein.receivers)
        self.assertIn("timeline", mit_nachbar.receivers)

    def test_grenze_ist_eingeschlossen(self) -> None:
        """Die Grenze ist der exakt gerechnete Kosinus — 0,5 als Literal lag
        im ersten Lauf knapp darunter, und die Gegenprobe blieb gruen."""
        v = [0.5, 0.0, (1 - 0.25) ** 0.5]
        grenze = cosine(v, _merkmale()["timeline"].vector)
        u = judge(_objekt("A"), v, _merkmale(), grenze)
        self.assertEqual(u.receivers, ("timeline",), u.top)

    def test_ein_merkmal_hat_keinen_abstand(self) -> None:
        nur = {"timeline": _merkmale()["timeline"]}
        u = judge(_objekt("A"), [1.0, 0.0, 0.0], nur, 0.40)
        self.assertIsNone(u.margin)
        self.assertEqual(u.outcome, OUTCOME_ASSIGNED)

    def test_ohne_merkmale_ist_ein_fehler(self) -> None:
        with self.assertRaises(ValueError):
            judge(_objekt("A"), [1.0, 0.0, 0.0], {}, 0.40)

    def test_kosinus_verweigert_null_und_fremde_dimension(self) -> None:
        with self.assertRaises(ValueError):
            cosine([0.0, 0.0], [1.0, 0.0])
        with self.assertRaises(ValueError):
            cosine([1.0], [1.0, 0.0])


def _gefangen() -> tuple[list[dict], MagicMock]:
    eintraege: list[dict] = []
    mock = MagicMock(side_effect=lambda **kw: eintraege.append(kw))
    return eintraege, mock


class SchattenTest(unittest.TestCase):
    """Jeder Rueckkehrpfad ein Eintrag; der Zustand bleibt unberuehrt."""

    def _fahren(self, state: dict, embed=None, features=None) -> tuple[dict, list[dict]]:  # noqa: ANN001
        eintraege, mock = _gefangen()
        vorher = copy.deepcopy(state)
        with patch("memory.pipeline_log.log_berechnung", mock):
            ergebnis = shadow_nearness(state, embed_batch=embed, features=features)
        self.assertEqual(state, vorher, "der Schatten hat den Zustand veraendert")
        self.assertEqual(len(eintraege), 1)
        self.assertEqual((eintraege[0]["node"], eintraege[0]["quelle"]), ("router", "objekt_naehe"))
        self.assertIs(eintraege[0]["inhalt"], ergebnis)
        return ergebnis, eintraege

    def test_ohne_sachlage(self) -> None:
        e, _ = self._fahren({"turn_id": "t"})
        self.assertEqual(e["ergebnis"], "ohne_sachlage")

    def test_sachlage_ohne_objektliste_ist_kein_fehlen_der_sachlage(self) -> None:
        e, _ = self._fahren({"turn_id": "t", "sachlage": {"herkunft": "impuls_uebernommen"}})
        self.assertEqual((e["ergebnis"], e["herkunft"]), ("ohne_objektliste", "impuls_uebernommen"))

    def test_nur_latente_objekte(self) -> None:
        e, _ = self._fahren({"turn_id": "t", "sachlage": {"objekte": [_objekt("A", akut=False)]}})
        self.assertEqual((e["ergebnis"], e["latente"]), ("ohne_akute_objekte", 1))

    def test_ohne_merkmale(self) -> None:
        e, _ = self._fahren({"turn_id": "t", "sachlage": {"objekte": [_objekt("A")]}}, features={})
        self.assertEqual(e["ergebnis"], "ohne_merkmale")

    def test_gerechnet_nur_ueber_akute(self) -> None:
        gesehen: list[list[str]] = []

        def einbetten(texte: list[str], frist: float) -> list[list[float]]:
            gesehen.append(texte)
            return [[1.0, 0.0, 0.0] for _ in texte]

        state = {"turn_id": "t", "user_id": "u", "character_id": "c",
                 "sachlage": {"herkunft": "gerechnet",
                              "objekte": [_objekt("A"), _objekt("B", akut=False), _objekt("C")]}}
        e, _ = self._fahren(state, embed=einbetten, features=_merkmale())
        self.assertEqual(e["ergebnis"], "gerechnet")
        self.assertEqual([o["name"] for o in e["objekte"]], ["A", "C"])
        self.assertEqual(len(gesehen[0]), 2)
        self.assertEqual(e["objekte"][0]["ausgang"], OUTCOME_ASSIGNED)
        self.assertEqual(e["objekte"][0]["empfaenger"], ["timeline"])
        self.assertEqual(e["untergrenze"], 0.40)
        self.assertNotIn("abstand", e)

    def test_ausfall_des_embed_ist_ein_eintrag_und_wirft_nicht(self) -> None:
        def kaputt(texte: list[str], frist: float) -> list[list[float]]:
            raise TimeoutError("Frist")

        with self.assertLogs("ki_server.agents.object_nearness", level="ERROR"):
            e, _ = self._fahren({"turn_id": "t", "sachlage": {"objekte": [_objekt("A")]}},
                                embed=kaputt, features=_merkmale())
        self.assertEqual((e["ergebnis"], e["fehlerart"]), ("ausfall", "TimeoutError"))

    def test_falsche_vektorzahl_und_nullvektor_sind_ausfall(self) -> None:
        for antwort in ([], [[0.0, 0.0, 0.0]]):
            with self.subTest(antwort=antwort):
                with self.assertLogs("ki_server.agents.object_nearness", level="ERROR"):
                    e, _ = self._fahren(
                        {"turn_id": "t", "sachlage": {"objekte": [_objekt("A")]}},
                        embed=lambda texte, frist, a=antwort: a, features=_merkmale(),
                    )
                self.assertEqual(e["ergebnis"], "ausfall")


class VerdrahtungTest(unittest.TestCase):
    """Der echte Router ruft den Schatten — und entscheidet danach dasselbe."""

    ROUTING = {"needs_memory": True, "needs_web": False, "needs_timeline": True,
               "timeline_query": {}, "momentum": "mid",
               "management_action": "create", "management_target": "timeline",
               "management_target_typ": "titel"}

    def _route(self, mit_schatten: bool) -> tuple[dict, list[dict]]:
        eintraege, log_mock = _gefangen()
        chat = MagicMock()
        chat.submit_sync.return_value = SimpleNamespace(text="{}", parsed=dict(self.ROUTING))
        state = {"turn_id": "t", "user_id": "u", "character_id": "c", "user_prompt": "Probe",
                 "sachlage": {"herkunft": "gerechnet", "objekte": [_objekt("A")]}}
        schatten = (
            patch.object(router, "shadow_nearness",
                         side_effect=lambda s: shadow_nearness(
                             s, embed_batch=lambda t, f: [[1.0, 0.0, 0.0] for _ in t],
                             features=_merkmale()))
            if mit_schatten else patch.object(router, "shadow_nearness", MagicMock())
        )
        with patch.object(router, "REGISTER"), \
             patch.object(router, "session_turns_retrieve", return_value=[]), \
             patch.object(router, "model_service", SimpleNamespace(chat=chat)), \
             patch("tools.redis_manager.redis_manager.get_json", return_value=None), \
             patch("memory.pipeline_log.log_berechnung", log_mock), \
             schatten as aufruf:
            ergebnis = router.route(state)
            if not mit_schatten:
                aufruf.assert_called_once()
        return dict(ergebnis), eintraege

    def test_der_router_schreibt_den_eintrag(self) -> None:
        _, eintraege = self._route(mit_schatten=True)
        self.assertEqual([e["quelle"] for e in eintraege], ["objekt_naehe"])
        self.assertEqual(eintraege[0]["inhalt"]["ergebnis"], "gerechnet")

    def test_die_routing_entscheidung_ist_mit_und_ohne_naehe_gleich(self) -> None:
        """Seit D1 reist das Urteil als `objekt_urteil` mit — alles andere bleibt gleich."""
        mit, _ = self._route(mit_schatten=True)
        ohne, _ = self._route(mit_schatten=False)
        self.assertEqual(mit.pop("objekt_urteil")["ergebnis"], "gerechnet")
        ohne.pop("objekt_urteil")
        self.assertEqual(mit, ohne)
        for schluessel, wert in self.ROUTING.items():
            self.assertEqual(mit[schluessel], wert)


if __name__ == "__main__":
    unittest.main()
