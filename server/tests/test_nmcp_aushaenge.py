"""Tests: Das schwarze Brett traegt jeden Zettel einmal und ohne Rangfolge.

Ziel: Der Aushang kommt vom Dienst, wo es einen gibt, und sonst vom Manager;
kein Aushang des alten Aggregators geht verloren; die Negativfaelle stehen bei
jedem Dienst in derselben Form; und ein Dienst ohne vierten Ausgang bekommt die
Zweifelsregel ausdruecklich zurueckgenommen.

Zeugen dieser Datei:
  * **Die Abdeckung wird gegen den alten Aggregator gemessen**, nicht gegen
    eine Liste im Test. Der Bestand entscheidet, was nicht verlorengehen darf —
    eine Liste im Test waere eine zweite Ableitung derselben Absicht.
  * **Die Doppelung ist der eigentliche Gegenstand.** Dienst und Manager
    tragen im Bestand denselben Text; geprueft wird, dass er EINMAL im Brett
    steht. Zwei Regeln, die dasselbe sagen, heben sich in der Wirkung auf.
  * **Die Rangfolge wird negativ geprueft.** Das Brett darf kein Wort
    enthalten, das ein Verhaeltnis zwischen zwei Zetteln herstellt — sonst
    traegt der Empfang Verhaeltniswissen, und das ist die zentrale
    Zuordnungstabelle.
  * **Was dieser Test NICHT kann:** die Unabhaengigkeit des Urteils. Ob das
    Modell zwei Zettel doch gegeneinander abwaegt, entscheidet ein Lauf und
    kein Zeuge. Die Gegenprobe dazu steht in der Konvention (§3.6a) und
    braucht eine Messung.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import re
import unittest

from agents import AgentRegistry, discover_agents
from agents.nmcp import aushaenge_sammeln
from plugins import discover_managers, get_combined_router_prompt, get_registry


def _marken(text: str) -> set[str]:
    """Findet die Erkennungsmarken eines Aushang-Textes.

    Vorbedingung: `text` ist Text. Nachbedingung: Menge der Marken der Form
    `NAME-ERKENNUNG:` — sie identifizieren einen Zettel unabhaengig von
    seinem Wortlaut.
    """
    return set(re.findall(r"^[A-Z][A-Z-]+-ERKENNUNG:", text, re.M))


class AbdeckungTest(unittest.TestCase):
    """Kein Zettel des alten Aggregators geht verloren."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand — er entscheidet, was nicht fehlen darf."""
        discover_managers()
        discover_agents()

    def test_jede_marke_des_alten_aggregators_kommt_vor(self) -> None:
        """Die Umstellung darf keinen Dienst unerreichbar machen.

        Gemessen gegen `get_combined_router_prompt()`, den Weg, der bis zur
        Umstellung gelesen wurde. Eine Liste im Test waere eine zweite
        Ableitung derselben Absicht und koennte denselben Fehler enthalten.
        """
        alt = _marken(get_combined_router_prompt())
        neu = _marken(aushaenge_sammeln("user"))
        self.assertTrue(alt, "Der alte Aggregator traegt Marken — sonst misst nichts")
        self.assertEqual(
            alt - neu, set(),
            f"Diese Aushaenge fehlen im neuen Brett: {sorted(alt - neu)}",
        )

    def test_manager_ohne_dienst_bleibt_erreichbar(self) -> None:
        """Ein Manager ohne gleichnamigen Dienst muss weiter im Brett stehen.

        Im Bestand ist das `fakten`. Faellt er weg, ist das Faktengedaechtnis
        vom Empfang nicht mehr erreichbar — und kein Fehler meldet es, weil
        der Router einfach nie dorthin routet.
        """
        agenten = set(AgentRegistry.alle())
        ohne_dienst = [
            ziel for ziel, m in get_registry().items()
            if ziel not in agenten and (m.router_prompt or "").strip()
        ]
        self.assertTrue(
            ohne_dienst,
            "Der Bestand hat einen Manager ohne Dienst — sonst misst nichts",
        )
        brett = aushaenge_sammeln("user")
        for ziel in ohne_dienst:
            marke = _marken(get_registry()[ziel].router_prompt)
            self.assertTrue(
                marke <= _marken(brett),
                f"Manager '{ziel}' fehlt im Brett",
            )


class DoppelungTest(unittest.TestCase):
    """Dienst und Manager tragen denselben Text — das Brett traegt ihn einmal."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand."""
        discover_managers()
        discover_agents()

    def test_jede_marke_steht_genau_einmal(self) -> None:
        """Zwei Regeln, die dasselbe sagen, heben sich in der Wirkung auf.

        Der Dienst erbt den Aushang vom gleichnamigen Manager. Ohne die
        Dienst-gewinnt-Regel stuende jeder der vier CRUD-Aushaenge zweimal
        im Prompt.
        """
        brett = aushaenge_sammeln("user")
        for marke in _marken(brett):
            self.assertEqual(
                brett.count(marke), 1,
                f"Marke '{marke}' steht {brett.count(marke)}-mal im Brett",
            )

    def test_dienste_mit_manager_sind_nicht_verdoppelt(self) -> None:
        """Fuer jeden Dienst mit gleichnamigem Manager gilt: eine Quelle."""
        agenten = AgentRegistry.alle()
        doppelt = [
            ziel for ziel in get_registry()
            if ziel in agenten
            and (get_registry()[ziel].router_prompt or "").strip()
        ]
        self.assertTrue(doppelt, "Der Bestand hat solche Paare — sonst misst nichts")
        brett = aushaenge_sammeln("user")
        for ziel in doppelt:
            text = (get_registry()[ziel].router_prompt or "").strip()
            kopf = text.splitlines()[0]
            self.assertEqual(
                brett.count(kopf), 1,
                f"Aushang von '{ziel}' steht mehrfach im Brett",
            )


class NegativfaelleTest(unittest.TestCase):
    """Die Negativfaelle stehen bei jedem Dienst in derselben Form."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand."""
        discover_managers()
        discover_agents()

    def test_jeder_empfangsdienst_mit_negativfaellen_hat_seinen_block(self) -> None:
        """Fehlrouting scheitert an Aehnlichkeit, nicht an fehlender Faehigkeit."""
        empfang = [
            a for a in AgentRegistry.alle().values()
            if a.zustellart == "empfang" and a.negativfaelle
        ]
        self.assertTrue(empfang, "Der Bestand hat solche Dienste — sonst misst nichts")
        brett = aushaenge_sammeln("user")
        self.assertEqual(
            brett.count("NICHT zustellen bei:"), len(empfang),
            f"{len(empfang)} Dienste mit Negativfaellen, aber "
            f"{brett.count('NICHT zustellen bei:')} Bloecke im Brett",
        )

    def test_jeder_einzelne_negativfall_steht_im_brett(self) -> None:
        """Ein Negativfall, der nicht im Prompt steht, wirkt nicht."""
        brett = aushaenge_sammeln("user")
        for agent in AgentRegistry.alle().values():
            if agent.zustellart != "empfang":
                continue
            for fall in agent.negativfaelle:
                self.assertIn(
                    fall, brett,
                    f"Negativfall von '{agent.name}' fehlt im Brett: {fall[:50]}",
                )


class ZweifelsregelTest(unittest.TestCase):
    """Ohne vierten Ausgang wird die Zweifelsregel zurueckgenommen."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand."""
        discover_managers()
        discover_agents()

    def test_manager_ohne_dienst_bekommt_keine_zweifelsfaelle(self) -> None:
        """Ein Manager hat keine vier Ausgaenge und kann nicht ablehnen.

        Die Zustellung im Zweifel ist nur billig, weil die Fachabteilung
        ablehnen KANN. Wer nicht ablehnen kann, fuehrt aus, was ihn
        erreicht — er beurteilt es nicht.
        """
        agenten = set(AgentRegistry.alle())
        ohne_dienst = [
            ziel for ziel, m in get_registry().items()
            if ziel not in agenten and (m.router_prompt or "").strip()
        ]
        brett = aushaenge_sammeln("user")
        self.assertEqual(
            brett.count("BEI UNSICHERHEIT NICHT ZUSTELLEN"), len(ohne_dienst),
            f"{len(ohne_dienst)} Anbieter ohne vierten Ausgang, aber "
            f"{brett.count('BEI UNSICHERHEIT NICHT ZUSTELLEN')} Ruecknahmen",
        )

    def test_dienst_mit_viertem_ausgang_bekommt_keine_ruecknahme(self) -> None:
        """Die Gegenprobe: wer ablehnen kann, behaelt die Zweifelsregel.

        Ohne diese Haelfte liesse der Test offen, ob die Ruecknahme einfach
        bei jedem Zettel steht.
        """
        brett = aushaenge_sammeln("user")
        mit_ausgang = [
            a for a in AgentRegistry.alle().values()
            if a.zustellart == "empfang" and "abgelehnt" in a.ausgaenge
        ]
        self.assertTrue(mit_ausgang, "Der Bestand hat solche Dienste")
        # Die Zahl der Ruecknahmen darf die Zahl der Dienste OHNE vierten
        # Ausgang nicht uebersteigen.
        ohne_ausgang = [
            a for a in AgentRegistry.alle().values()
            if a.zustellart == "empfang" and "abgelehnt" not in a.ausgaenge
        ]
        agenten = set(AgentRegistry.alle())
        manager_ohne = [
            z for z, m in get_registry().items()
            if z not in agenten and (m.router_prompt or "").strip()
        ]
        self.assertEqual(
            brett.count("BEI UNSICHERHEIT NICHT ZUSTELLEN"),
            len(ohne_ausgang) + len(manager_ohne),
        )


class KeineRangfolgeTest(unittest.TestCase):
    """Das Brett stellt kein Verhaeltnis zwischen zwei Zetteln her."""

    @classmethod
    def setUpClass(cls) -> None:
        """Faehrt den Bestand."""
        discover_managers()
        discover_agents()

    def test_brett_traegt_kein_rangwort(self) -> None:
        """Ein Vorrang im Prompt ist die zentrale Zuordnungstabelle.

        Der Empfang beurteilt jeden Zettel fuer sich. Ein Wort, das zwei
        Zettel in ein Verhaeltnis setzt, gibt ihm Verhaeltniswissen — gleich
        ob zur Laufzeit gebildet oder bei der Registrierung berechnet.
        """
        brett = aushaenge_sammeln("user").lower()
        verboten = [
            "vorrang", "hat prioritaet", "bevorzugt gegenueber",
            "nur wenn kein anderer", "schlaegt den", "wichtiger als",
            "rangfolge", "zuerst pruefen ob",
        ]
        gefunden = [w for w in verboten if w in brett]
        self.assertEqual(
            gefunden, [],
            f"Das Brett traegt Rangworte: {gefunden}",
        )

    def test_unbekannter_graph_ergibt_leeres_brett(self) -> None:
        """Ein Graph ausserhalb des Kanons liefert nichts, statt zu raten."""
        self.assertEqual(aushaenge_sammeln("erfunden"), "")


if __name__ == "__main__":
    unittest.main()
