"""Zeugen: Ein zugestellter Impuls schliesst an das Gespraech an.

Ziel: Ein Gedanke, den Nova von sich aus einbringt, faellt an die Stelle des
Gespraechs, an der es gerade steht — im Thema und im Ton. Er wirkt nicht
eingeworfen, und er wiederholt nicht, was schon dasteht.

**Der Anlass ist eine Beobachtung des Eigentuemers, am Bestand nachgemessen.**
Die zugestellten Impulse nahmen auf ein Thema Bezug, aber nicht auf das, was
im Kontext gesagt wurde; Teile des Materials standen woertlich in der Antwort.
`[gemessen 11.09.2026 ueber 156 Impuls-Turns]` Die Uebernahmequote aus dem
Material liegt im Median bei **20 %**, im P90 bei **41 %**; **29 Antworten
(19 %) tragen eine woertlich uebernommene Passage von sechs Woertern oder
mehr**, und **6 Impulse (4 %)** kamen im Berichts-Rohformat mit Ueberschriften
wie `**WAS GEFUNDEN WURDE.**`.

**Die Ursache stand im Prompt und war eine uebersteuerte Abhilfe.**
`verfasser.eigener_impuls.txt` wies bis zum 11.09.2026 ausdruecklich an:
*„SIE EROEFFNET. Der erste Satz setzt etwas in den Raum, statt an etwas
anzuknuepfen. Was Person B zuletzt sagte, ist Vorgeschichte und nicht der
Anlass."* Die Zeile stammt vom 13.08.2026 und behob einen anderen Defekt —
13 von 14 Impulsen begannen mit *„Du hast …"* und schrieben Novas eigenen
Gedanken dem Nutzer zu (`VERFASSER-KENNT-DIE-QUELLE-NICHT`).

> **Zwei Fragen waren dabei vermischt worden.** *Von wem* ein Gedanke stammt
> und *woran* er anschliesst sind verschieden. Um die falsche Zuschreibung zu
> verhindern, war der Anschluss ganz verboten worden — und ein Beitrag ohne
> Anschluss wirkt maschinell eingefuegt.

Zeugen dieser Datei:
  * **Beide Zusicherungen zugleich.** Der Anschluss darf die Herkunft nicht
    aufweichen: Der Gedanke bleibt Novas, und die Zeile, die das sagt, steht
    weiter im Prompt. Ein Zeuge nur auf den Anschluss liesse den alten Defekt
    zurueckkehren.
  * **Die Verdrahtung, nicht der Text.** Dass ein Prompt eine Anweisung
    traegt, sagt nichts darueber, ob das Modell den Verlauf ueberhaupt sieht.
    Geprueft wird deshalb, dass der Verfasser auf einem Impuls-Turn den
    `[GESPRAECHSVERLAUF]`-Block baut.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest

from graph.nodes import verfasser
from prompt_loader import prompt_laden

PROMPTS: dict = prompt_laden("")


class DerImpulsKnuepftAn(unittest.TestCase):
    """Die Anweisung zum Anschluss steht in beiden Prompts."""

    def test_der_verfasser_wird_auf_den_verlauf_verwiesen(self) -> None:
        block: str = PROMPTS["verfasser.eigener_impuls"]

        self.assertIn("[GESPRAECHSVERLAUF]", block)
        self.assertIn("KNUEPFT AN", block)

    def test_der_responder_wird_auf_den_verlauf_verwiesen(self) -> None:
        block: str = PROMPTS["responder.eigener_gedanke"]

        self.assertIn("[GESPRAECHSVERLAUF]", block)
        self.assertIn("KNUEPFT AN", block)

    def test_beide_werden_auf_das_neue_gefuehrt(self) -> None:
        """**Positiv, nicht als Verbot** (`F-PROMPT-1`).

        Die erste Fassung dieses Zeugen hielt `WIEDERHOLT NICHT` fest — eine
        Verbotsform, die der Prompt-Festlegung widerspricht: Ein Verbot nennt
        das Unerwuenschte und macht es zum Gegenstand. Gehalten wird deshalb
        die Richtung, in die der Beitrag gehen soll.
        """
        for name in ("verfasser.eigener_impuls", "responder.eigener_gedanke"):
            self.assertIn("SIE BRINGT DAS NEUE", PROMPTS[name], name)

    def test_die_eroeffnung_ohne_bezug_ist_nicht_mehr_angewiesen(self) -> None:
        """Der Satz, der den Anschluss verbot — er darf nicht zurueckkehren."""
        block: str = PROMPTS["verfasser.eigener_impuls"]

        self.assertNotIn("statt an etwas", block)
        self.assertNotIn("Vorgeschichte und nicht der Anlass", block)


class DieHerkunftBleibtScharf(unittest.TestCase):
    """Der Anschluss weicht die Zuschreibung nicht auf.

    `VERFASSER-KENNT-DIE-QUELLE-NICHT`: 13 von 14 Impulsen begannen mit
    *„Du hast …"*. Wer den Anschluss einbaut und diese Zusicherung dabei
    verliert, hat den alten Defekt zurueckgebaut.
    """

    def test_der_gedanke_bleibt_novas(self) -> None:
        block: str = PROMPTS["verfasser.eigener_impuls"]

        self.assertIn("hat PERSON B NICHT gesagt", block)
        self.assertIn("nicht als der, von dem es stammt", block)

    def test_beide_fragen_werden_ausdruecklich_getrennt(self) -> None:
        """Ohne diesen Satz liest sich der Prompt als Widerspruch."""
        block: str = PROMPTS["verfasser.eigener_impuls"]

        self.assertIn("zwei verschiedene Fragen", block)


class DasMaterialIstRohstoff(unittest.TestCase):
    """Berichtsform ist die Ablageform, nicht die Sprechform."""

    def test_die_eigene_formulierung_ist_angewiesen(self) -> None:
        """Ebenfalls positiv gewendet: wohin die Energie geht, nicht wogegen."""
        self.assertIn("in ihrer eigenen Form",
                      PROMPTS["verfasser.eigener_gedanke"])
        self.assertIn("SIE SPRICHT IN IHREN EIGENEN WORTEN",
                      PROMPTS["verfasser.eigener_impuls"])

    def test_die_berichtsform_wird_als_ablageform_benannt(self) -> None:
        """`[Betriebsbeleg]` 6 von 156 Impulsen kamen mit `**WAS GEFUNDEN
        WURDE.**` und weiteren Gliederungsmarken — das ist die Form, in der
        ein Fund abgelegt wird, und keine, in der jemand spricht.
        """
        block: str = PROMPTS["verfasser.eigener_gedanke"]

        self.assertIn("Berichtsform", block)
        self.assertIn("Ueberschriften", block)

    def test_ein_leerer_fund_wird_als_leer_gesagt(self) -> None:
        """`[Betriebsbeleg 10.09.2026]` Eine Recherche zu Gamma-Oszillationen
        fand RTX-Grafikkarten und meldete selbst, dass die Anfrage scheitert —
        zugestellt wurde sie trotzdem.
        """
        block: str = PROMPTS["verfasser.eigener_gedanke"]

        self.assertIn("Was es nicht hergibt", block)
        self.assertIn("ist genau das die Auskunft", block)


class DerFerneFundBekommtEineBruecke(unittest.TestCase):
    """Liegt der Fund fern vom Gespraech, setzt der Verfasser einen Uebergang.

    **Die Zustellschwelle und die Anschlussschwelle sind verschieden.** Die
    Auswahl laesst ab einer thematischen Naehe von 0,30 durch — bewusst,
    damit ein Fund aus einem frueheren Auftrag nicht fuer immer liegen
    bleibt. Fuer einen Anschluss ohne Bruecke reicht das nicht.

    `[Betriebsbeleg 11.09.2026]` Ein Eintrag mit Naehe **0,37** wurde
    zugestellt, waehrend das Gespraech bei einem anderen Gegenstand stand.
    Der Beitrag war sprachlich gelungen, kein Satz abgeschrieben — und sprang
    ohne ein Wort des Uebergangs von Lagrange-Punkten zur Hubble-Spannung.
    """

    def test_ein_ferner_fund_setzt_den_uebergangsblock(self) -> None:
        block: str = verfasser._uebergangsblock(
            {"event_payload": {"thema_naehe": 0.37}})

        self.assertIn("[DER UEBERGANG]", block)
        self.assertIn("SIE NENNT DEN WECHSEL", block)

    def test_ein_naher_fund_braucht_keinen(self) -> None:
        """Der Zwilling: Sonst stuende der Block immer und saegte nichts."""
        self.assertEqual(
            "", verfasser._uebergangsblock(
                {"event_payload": {"thema_naehe": 0.82}}))

    def test_ohne_naehe_kein_block(self) -> None:
        """Jeder Weg ausser der Zustellung traegt sie nicht."""
        self.assertEqual("", verfasser._uebergangsblock({}))
        self.assertEqual("", verfasser._uebergangsblock({"event_payload": {}}))

    def test_ein_unbrauchbarer_wert_wird_gemeldet(self) -> None:
        """**Nicht still als 0.0.** Das waere die staerkste Aussage —
        *ganz fernes Thema* — aus einer fehlenden.
        """
        with self.assertLogs("ki_server.verfasser", level="WARNING") as log:
            block: str = verfasser._uebergangsblock(
                {"event_payload": {"thema_naehe": "nah"}})

        self.assertEqual("", block)
        self.assertTrue(any("thema_naehe" in z for z in log.output), log.output)

    def test_der_block_erlaubt_das_eingestaendnis(self) -> None:
        """Eine erzwungene Verbindung waere schlechter als ein offener Wechsel."""
        self.assertIn("nichts damit zu tun",
                      PROMPTS["verfasser.impuls_ferne"])


class DerVerlaufErreichtDenVerfasser(unittest.TestCase):
    """Die Verdrahtung — eine Anweisung auf einen Block, den niemand baut."""

    def test_der_verfasser_baut_den_verlaufsblock(self) -> None:
        import inspect

        from graph.nodes import verfasser

        quelle: str = inspect.getsource(verfasser)

        self.assertIn("[GESPRAECHSVERLAUF]", quelle)
        self.assertIn("session_turns", quelle)


if __name__ == "__main__":
    unittest.main()
