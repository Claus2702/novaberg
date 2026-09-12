"""Zeugen: die Naht zwischen Langzeit- und Kurzzeitgedaechtnis im Lueckenprodukt.

Ziel: Ein Lueckenkandidat gewinnt nicht allein dadurch, aus welchem Speicher er
kommt. `[gemessen 12.09.2026, 15 Betriebsturns]` Von 83 Luecken im Prompt kamen
**77 aus dem LZG und 6 aus dem KZG**, obwohl beide Suchen in jedem Turn 8 bis 10
Kandidaten lieferten. Der Grund stand im Produkt
`similarity × gewicht × GV_QUELLEN_FAKTOR × …`: `gewicht` ist beim LZG
`gewicht_decay` (im Bestand 3,03–10,0, Median 3,89), beim KZG die `salienz`
(0,42–1,0, Median 0,97). Roh eingesetzt war ein mittelmaessiger LZG-Knoten viermal
schwerer als ein sehr salienter KZG-Eintrag.

**Die Abbildung ist der Rang in der eigenen Quelle.** Vorher gerechnet ueber elf
echte Nutzerturns gegen den Bestand: roh 74 LZG / 8 KZG, geteilt durch die
Obergrenze 3 / 59, Min–Max 4 / 48, **Rang 22 / 18**.

**Der Zeuge, der das Ziel festhaelt, ist der mit zwei Kandidaten gleicher Naehe,
die in ihrer eigenen Quelle denselben Rang haben:** Er verlangt dieselbe
Relevanz — roh stuende das LZG achtfach vorn.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import math
import unittest
from unittest.mock import patch

import ei.source_weights as source_weights
from ei.gap_topics import UserTopics
from ei.source_weights import load_weight_distributions, weight_rank
from ei.wissensluecken import wissensluecken_finden

# Nachgebildet nach der Form des Bestands: LZG breit und unten dicht, KZG oben
# gedraengt. Beide mit zehn Werten, damit ein Rang in Zehnteln ablesbar ist.
LZG = [3.0, 3.2, 3.5, 3.8, 4.0, 5.0, 7.0, 8.0, 9.5, 10.0]
KZG = [0.45, 0.7, 0.85, 0.9, 0.95, 0.97, 0.98, 0.99, 1.0, 1.0]


class RangInDerEigenenQuelle(unittest.TestCase):
    """`weight_rank` — die reine Abbildung."""

    def test_der_hoechste_wert_hat_rang_eins(self) -> None:
        self.assertEqual(weight_rank(10.0, LZG), 1.0)

    def test_der_kleinste_wert_hat_ein_zehntel(self) -> None:
        self.assertAlmostEqual(weight_rank(3.0, LZG), 0.1)

    def test_unter_dem_minimum_ist_null(self) -> None:
        self.assertEqual(weight_rank(0.1, LZG), 0.0)

    def test_ueber_dem_maximum_ist_eins(self) -> None:
        # Ein Eintrag, der nach dem Laden der Verteilung entstand.
        self.assertEqual(weight_rank(11.0, LZG), 1.0)

    def test_gleiche_gewichte_teilen_den_rang(self) -> None:
        self.assertEqual(weight_rank(1.0, KZG), 1.0)
        self.assertEqual(weight_rank(1.0, KZG), weight_rank(1.0, list(KZG)))

    def test_die_abbildung_ist_monoton(self) -> None:
        werte = [2.9 + i * 0.05 for i in range(160)]
        raenge = [weight_rank(w, LZG) for w in werte]
        self.assertEqual(raenge, sorted(raenge))

    def test_die_skala_ist_fuer_beide_quellen_dieselbe(self) -> None:
        """Das Ziel an der reinen Funktion: gleiche Stelle, gleicher Rang."""
        self.assertEqual(weight_rank(8.0, LZG), weight_rank(0.99, KZG))

    def test_leere_verteilung_wird_abgelehnt(self) -> None:
        with self.assertRaises(ValueError):
            weight_rank(4.0, [])

    def test_bool_ist_kein_gewicht(self) -> None:
        with self.assertRaises(ValueError):
            weight_rank(True, KZG)

    def test_nan_ist_kein_gewicht(self) -> None:
        with self.assertRaises(ValueError):
            weight_rank(float("nan"), KZG)


def zustand() -> dict:
    """Ein Turn, wie ihn die Lueckensuche liest — ohne Kern, damit allein die Relevanz entscheidet."""
    return {
        "user_prompt":      "Ein Reiz ueber Neutronensterne",
        "user_id":          "mensch",
        "character_id":     "figur",
        "prompt_embedding": TURN,
        "internal":         None,
        "session_turns":    [],
        "turn_id":          "t-naht",
    }


#: Der Turn als Einheitsvektor. Seit dem Umbau auf Themen (12.09.2026, abends)
#: ist die Naehe die des **Themas** zum Turn; die Zeugen legen sie ueber den
#: Themenvektor fest, nicht ueber die Suche.
TURN: list[float] = [1.0] + [0.0] * 7

LZG_THEMA = "Rotation eines Pulsars"
KZG_THEMA = "Gezeitenverformung dichter Materie"


def vektor_mit_naehe(naehe: float) -> list[float]:
    """Ein Vektor, dessen Cosinus zum Turn genau `naehe` ist."""
    return [naehe, math.sqrt(1.0 - naehe * naehe)] + [0.0] * 6


def lzg_kandidat(gewicht: float, similarity: float) -> dict:
    """Ein LZG-Knoten mit einem Thema; `similarity` wird die Naehe dieses Themas."""
    return {"konzept": "Nova hat die Rotation eines Pulsars erklaert", "similarity": similarity,
            "gewicht": gewicht, "gap_arousal": 0.3, "quelle": "lzg", "themen": [LZG_THEMA]}


def kzg_kandidat(salienz: float, similarity: float) -> dict:
    """Ein KZG-Eintrag mit einem Thema; `similarity` wird die Naehe dieses Themas."""
    return {"konzept": "Nova hat Gezeitenkraefte beschrieben", "similarity": similarity,
            "gewicht": salienz, "gap_arousal": 0.3, "quelle": "kzg", "themen": KZG_THEMA}


class DieNahtIstVerdrahtet(unittest.TestCase):
    """`wissensluecken_finden` rechnet mit dem Rang, nicht mit dem rohen Gewicht."""

    def finden(self, lzg: list[dict], kzg: list[dict], verteilungen=None) -> tuple[list[dict], object, object]:
        verteilungen = verteilungen if verteilungen is not None else {"lzg": LZG, "kzg": KZG}
        vektoren = {LZG_THEMA: vektor_mit_naehe(lzg[0]["similarity"]) if lzg else [],
                    KZG_THEMA: vektor_mit_naehe(kzg[0]["similarity"]) if kzg else []}
        with patch("ei.wissensluecken.lzg_kandidaten_suchen", return_value=lzg), \
             patch("ei.wissensluecken.kzg_kandidaten_suchen", return_value=kzg), \
             patch("ei.wissensluecken.load_weight_distributions", return_value=verteilungen), \
             patch("ei.wissensluecken.load_user_topics", return_value=UserTopics(set(), set())), \
             patch("ei.wissensluecken.embed_topics",
                   side_effect=lambda themen: {t: vektoren[t] for t in themen}), \
             patch("ei.wissensluecken.log_berechnung") as spur, \
             patch("ei.wissensluecken.logger") as log:
            ergebnis = wissensluecken_finden(zustand(), aufnahmebereitschaft=1.0)
        return ergebnis, spur, log

    def test_gleicher_rang_gleiche_relevanz(self) -> None:
        ergebnis, _, _ = self.finden([lzg_kandidat(8.0, 0.6)], [kzg_kandidat(0.99, 0.6)])
        self.assertEqual(len(ergebnis), 2)
        lzg, kzg = sorted(ergebnis, key=lambda k: k["quelle"], reverse=True)
        self.assertEqual(lzg["quelle"], "lzg")
        self.assertAlmostEqual(lzg["relevanz"], kzg["relevanz"])

    def test_der_naehere_kzg_eintrag_schlaegt_den_schwereren_lzg_knoten(self) -> None:
        """Roh: 0,6 × 8,0 = 4,8 gegen 0,7 × 0,99 = 0,69 — das LZG vorn. Mit Rang umgekehrt."""
        ergebnis, _, _ = self.finden([lzg_kandidat(8.0, 0.6)], [kzg_kandidat(0.99, 0.7)])
        self.assertEqual([k["quelle"] for k in ergebnis], ["kzg", "lzg"])

    def test_das_rohe_gewicht_bleibt_am_kandidaten(self) -> None:
        ergebnis, _, _ = self.finden([lzg_kandidat(8.0, 0.6)], [])
        self.assertEqual(ergebnis[0]["gewicht"], 8.0)
        self.assertAlmostEqual(ergebnis[0]["gewicht_rang"], 0.8)

    def test_die_mischung_steht_in_der_spur(self) -> None:
        _, spur, _ = self.finden([lzg_kandidat(8.0, 0.6)], [kzg_kandidat(0.99, 0.6)])
        naht = [c.kwargs["inhalt"] for c in spur.call_args_list
                if c.kwargs["inhalt"].get("schritt") == "gv4_quellen_naht"]
        self.assertEqual(len(naht), 1)
        self.assertEqual(naht[0]["ergebnis"], {"lzg": 1, "kzg": 1})
        self.assertEqual(naht[0]["kandidaten"], {"lzg": 1, "kzg": 1})

    def test_auch_ohne_treffer_steht_die_spur(self) -> None:
        # Beide unter der Untergrenze: Rang 0,1 und 0,1 bei geringer Naehe.
        ergebnis, spur, _ = self.finden([lzg_kandidat(3.0, 0.25)], [kzg_kandidat(0.45, 0.25)])
        self.assertEqual(ergebnis, [])
        schritte = [c.kwargs["inhalt"].get("schritt") for c in spur.call_args_list]
        self.assertIn("gv4_quellen_naht", schritte)

    def test_ohne_verteilung_keine_luecken_und_ein_fehler(self) -> None:
        with patch("ei.wissensluecken.lzg_kandidaten_suchen", return_value=[lzg_kandidat(8.0, 0.6)]), \
             patch("ei.wissensluecken.kzg_kandidaten_suchen", return_value=[]), \
             patch("ei.wissensluecken.load_weight_distributions", side_effect=RuntimeError("db weg")), \
             patch("ei.wissensluecken.log_berechnung"), \
             patch("ei.wissensluecken.logger") as log:
            ergebnis = wissensluecken_finden(zustand(), aufnahmebereitschaft=1.0)
        self.assertEqual(ergebnis, [])
        self.assertTrue(log.error.called)

    def test_eine_quelle_ohne_verteilung_verliert_nur_ihre_kandidaten(self) -> None:
        ergebnis, _, log = self.finden(
            [lzg_kandidat(8.0, 0.6)], [kzg_kandidat(0.99, 0.6)],
            verteilungen={"lzg": LZG, "kzg": []},
        )
        self.assertEqual([k["quelle"] for k in ergebnis], ["lzg"])
        self.assertTrue(log.error.called)


class DerLaderHaeltZwischen(unittest.TestCase):
    """`load_weight_distributions` — Zwischenspeicher, Neuladen, Paarpflicht."""

    def setUp(self) -> None:
        source_weights._cache.clear()

    def tearDown(self) -> None:
        source_weights._cache.clear()

    def test_innerhalb_der_frist_wird_nicht_neu_geladen(self) -> None:
        with patch.object(source_weights, "_load_lzg", return_value=[1.0]) as lzg, \
             patch.object(source_weights, "_load_kzg", return_value=[0.5]):
            load_weight_distributions("mensch", "figur")
            load_weight_distributions("mensch", "figur")
        self.assertEqual(lzg.call_count, 1)

    def test_refresh_laedt_neu(self) -> None:
        with patch.object(source_weights, "_load_lzg", return_value=[1.0]) as lzg, \
             patch.object(source_weights, "_load_kzg", return_value=[0.5]):
            load_weight_distributions("mensch", "figur")
            load_weight_distributions("mensch", "figur", refresh=True)
        self.assertEqual(lzg.call_count, 2)

    def test_nach_ablauf_der_frist_wird_neu_geladen(self) -> None:
        with patch.object(source_weights, "_load_lzg", return_value=[1.0]) as lzg, \
             patch.object(source_weights, "_load_kzg", return_value=[0.5]), \
             patch.object(source_weights, "GV_GEWICHT_VERTEILUNG_TTL_S", 0.0):
            load_weight_distributions("mensch", "figur")
            load_weight_distributions("mensch", "figur")
        self.assertEqual(lzg.call_count, 2)

    def test_paare_teilen_sich_keinen_eintrag(self) -> None:
        with patch.object(source_weights, "_load_lzg", side_effect=[[1.0], [2.0]]), \
             patch.object(source_weights, "_load_kzg", return_value=[0.5]):
            a = load_weight_distributions("mensch", "figur")
            b = load_weight_distributions("andere", "figur")
        self.assertNotEqual(a["lzg"], b["lzg"])

    def test_unvollstaendiges_paar_wird_abgelehnt(self) -> None:
        with self.assertRaises(ValueError):
            load_weight_distributions("", "figur")


class DieKzgAbfrageBlaettert(unittest.TestCase):
    """`_load_kzg` liest ueber mehrere Seiten und verwirft Unlesbares laut."""

    def test_zwei_seiten_und_ein_unlesbarer_eintrag(self) -> None:
        seiten = [
            [3, "kzg:a", ["salienz", "0.9"], "kzg:b", ["salienz", "0.5"]],
            [3, "kzg:c", ["salienz", "keine zahl"]],
        ]
        with patch.object(source_weights.redis_client, "execute_command", side_effect=seiten) as abfrage, \
             patch.object(source_weights, "_KZG_PAGE", 2), \
             patch.object(source_weights, "logger") as log:
            werte = source_weights._load_kzg("mensch", "figur")
        self.assertEqual(werte, [0.5, 0.9])
        self.assertEqual(abfrage.call_count, 2)
        self.assertTrue(log.error.called)

    def test_die_abfrage_nennt_das_paar(self) -> None:
        with patch.object(source_weights.redis_client, "execute_command",
                          return_value=[0]) as abfrage:
            source_weights._load_kzg("mensch", "figur")
        self.assertIn("@user_id:{mensch} @character_id:{figur}", abfrage.call_args.args)


if __name__ == "__main__":
    unittest.main()
