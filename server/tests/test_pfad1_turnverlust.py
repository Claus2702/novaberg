"""Tests: Ein Abbruch in Pfad 1 loescht die Nutzeraeusserung nicht.

Ziel: Das Ereignis, das den CharacterGraph ausloest, entsteht auch dann, wenn
der HumanGraph mit einer Ausnahme endet — und es traegt den Vermerk, dass es
das getan hat.

Befund, aus dem das entstand (Chat 119, PFAD1-TIMEOUT-TURNVERLUST): Ein
Modellaufruf brauchte 60,0 s gegen einen Median von 2,3 s. `submit_sync` gab
bei 60,000 s auf, die Antwort kam 6 ms spaeter vollstaendig an. Die Ausnahme
flog aus der Stream-Schleife, `event_erzeugen` stand dahinter und lief nie —
kein Ereignis, kein CharacterGraph, keine Antwort. Nicht verzoegert: weg. Der
Nutzer sah "Fehler:" und hatte keinen Weg zur Wiederholung.

Zwei Dinge werden hier scharf getrennt, und beide muessen gelten:
  - Der Turn ueberlebt.
  - Der Ausfall ist am Ereignis erkennbar. Ohne den Vermerk fuellt
    `db_zugriff` die Perzeptionsfelder mit den Defaults der Datenklasse
    (neutral, 0.5, alltag), und ein Zusammenbruch waere von einer ruhigen
    Nutzeraeusserung nicht mehr zu unterscheiden.

Zeugen dieser Datei:
  * Die Erwartung "der Turn ueberlebt" stammt aus dem Bug-Eintrag, nicht aus
    dem Code, der sie erfuellen soll.
  * Die Default-Werte, gegen die der Vermerk schuetzt, stehen in der
    Datenklasse `Emotion` und werden von dort gelesen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace

from api.chat import _ereignis_nutzlast, _Pfad1Abbruch, _stream_oder_abbruch

TURN: str = "t-pfad1"
REIZ: str = "Wie entstehen die Ringe des Saturn?"
# Empfangszeitpunkt der Aeusserung — fuer diese Datei ohne Bedeutung,
# aber Pflichtargument: Die Nutzlast traegt ihn seit der Prompt-Gruppierung.
EMPFANG: float = 1_754_000_000.0


def _zustand(**kw: object) -> dict:
    """Baut einen Pfad-1-Zustand mit gefuellter Perzeption."""
    aussen = SimpleNamespace(emotion=SimpleNamespace(
        emotion="neugierig", arousal=0.6, mode="fachgespraech",
        intent="knowledge", tone="sachlich", language_style="fachlich",
        relationship_dynamic="vertrauen", emotions_vector="plateau",
        prompt_topic="Saturnringe",
    ))
    zustand: dict = {
        "external":         aussen,
        "salienz_human":    0.7,
        "user_intentionen": ["information_erfragen"],
    }
    zustand.update(kw)
    return zustand


class NutzlastOhneAusfall(unittest.TestCase):
    """Der Regelfall — damit der Ausfallfall etwas hat, wogegen er sich abhebt."""

    def test_die_perzeptionswerte_reisen_mit(self) -> None:
        """Was Pfad 1 gemessen hat, steht im Ereignis."""
        n = _ereignis_nutzlast(TURN, EMPFANG, REIZ, _zustand())
        self.assertEqual(n["current_emotion"], "neugierig")
        self.assertEqual(n["current_arousal"], 0.6)
        self.assertEqual(n["gespraechs_modus"], "fachgespraech")

    def test_salienz_und_intentionen_reisen_mit(self) -> None:
        """Die beiden Werte, die der CharacterGraph nicht selbst erheben kann."""
        n = _ereignis_nutzlast(TURN, EMPFANG, REIZ, _zustand())
        self.assertEqual(n["salienz_human"], 0.7)
        self.assertEqual(n["user_intentionen"], ["information_erfragen"])

    def test_ohne_ausfall_kein_vermerk(self) -> None:
        """Der positive Zwilling: Das Feld erscheint nur, wenn es etwas sagt.

        Ein immer vorhandenes `pfad1_ausfall: ""` waere ein stiller Default —
        jeder Leser muesste den Leerstring als "alles gut" deuten, statt das
        Fehlen des Feldes zu sehen.
        """
        self.assertNotIn("pfad1_ausfall", _ereignis_nutzlast(TURN, EMPFANG, REIZ, _zustand()))


class NutzlastMitAusfall(unittest.TestCase):
    """Der Turn ueberlebt, und der Ausfall ist ihm anzusehen."""

    def test_das_ereignis_entsteht_trotzdem(self) -> None:
        """Der Kern: Ohne Ereignis gibt es nie eine Antwort, nicht nur spaeter keine."""
        n = _ereignis_nutzlast(TURN, EMPFANG, REIZ, {}, "TimeoutError: zu spaet")
        self.assertEqual(n["turn_id"], TURN)
        self.assertEqual(n["user_prompt"], REIZ)

    def test_der_ausfall_wird_benannt(self) -> None:
        """Mit dem Ausnahmetyp, nicht nur mit einem Flag."""
        n = _ereignis_nutzlast(TURN, EMPFANG, REIZ, {}, "TimeoutError: zu spaet")
        self.assertIn("TimeoutError", n["pfad1_ausfall"])

    def test_ohne_perzeption_stehen_leere_werte_und_kein_erfundener_zustand(self) -> None:
        """Leere Zeichenketten, nicht 'neutral' — der Unterschied ist der Punkt.

        `db_zugriff` setzt fehlende Schluessel auf die Defaults der
        Datenklasse. Wuerde hier bereits 'neutral' stehen, waere der Ausfall
        eine Ebene frueher zu einem plausiblen Messwert geworden.
        """
        n = _ereignis_nutzlast(TURN, EMPFANG, REIZ, {}, "TimeoutError: zu spaet")
        self.assertEqual(n["current_emotion"], "")
        self.assertEqual(n["gespraechs_modus"], "")
        self.assertIsNone(n["salienz_human"])
        self.assertEqual(n["user_intentionen"], [])


class StreamHuelleMachtAusDemAbbruchEinElement(unittest.TestCase):
    """Die Ausnahme darf den Generator nicht verlassen.

    Verlaesst sie ihn, endet die Schleife des Aufrufers, und das
    `event_erzeugen` dahinter laeuft nie — genau der beobachtete Verlust.
    """

    @staticmethod
    def _graph(chunks: list, fehler: Exception | None = None) -> object:
        """Baut einen Graphen, der die Chunks liefert und dann optional wirft."""
        def stream(_zustand: dict) -> object:
            yield from chunks
            if fehler is not None:
                raise fehler
        return SimpleNamespace(stream=stream)

    def test_ohne_ausnahme_kommen_alle_chunks_durch(self) -> None:
        """Der positive Zwilling: Die Huelle veraendert den Regelfall nicht."""
        chunks = [{"a": 1}, {"b": 2}]
        self.assertEqual(list(_stream_oder_abbruch(self._graph(chunks), {})), chunks)

    def test_die_ausnahme_wird_zum_letzten_element(self) -> None:
        """Der Abbruch kommt als Wert an, nicht als Ausnahme."""
        with self.assertLogs("ki_server.chat", level="ERROR"):
            ergebnis = list(_stream_oder_abbruch(
                self._graph([{"a": 1}], TimeoutError("zu spaet")), {},
            ))

        self.assertEqual(ergebnis[0], {"a": 1})
        self.assertIsInstance(ergebnis[-1], _Pfad1Abbruch)
        self.assertIn("TimeoutError", ergebnis[-1].text)

    def test_der_traceback_wird_im_ausnahmekontext_geschrieben(self) -> None:
        """Er gehoert dorthin, wo gefangen wird.

        Beim Aufrufer ist die Ausnahme nur noch ein Wert; ein `exception()`
        oder `exc_info=` dort haette keinen Kontext. Die harte LOG-Regel des
        Linters hat genau diese Verwechslung beim Bau gemeldet.
        """
        with self.assertLogs("ki_server.chat", level="ERROR") as protokoll:
            list(_stream_oder_abbruch(self._graph([], ValueError("kaputt")), {}))

        gemeinsam: str = "\n".join(protokoll.output)
        self.assertIn("ValueError", gemeinsam)
        self.assertIn("Traceback", gemeinsam)


class ConsumerErzeugtDasEreignisTrotzAusnahme(unittest.IsolatedAsyncioTestCase):
    """Der eigentliche Regressionsschutz — am Kontrollfluss, nicht am Baustein.

    Die Tests oben pruefen `_ereignis_nutzlast` und `_stream_oder_abbruch`
    einzeln. Beide waren gruen, als der `except`-Zweig testweise durch ein
    `raise` ersetzt wurde — also als der urspruengliche Defekt vollstaendig
    wiederhergestellt war. **Ein Netz, das den Baustein prueft und nicht seine
    Verdrahtung, haette den Defekt erneut durchgelassen.**

    Die Zusicherung ist mit dem Code gewandert: Pfad 1 laeuft seit der
    Eingangs-Queue im Prompt-Consumer, nicht mehr im Endpunkt. Die Regel
    dahinter ist unveraendert — ein Abbruch darf die Nutzeraeusserung nicht
    loeschen.
    """

    async def _fahren(self, fehler: Exception | None) -> list:
        """Laesst den Consumer einen Block gegen einen Graphen fahren, der optional wirft.

        Returns:
            Die Aufrufe von `event_erzeugen` als Liste von kwargs.
        """
        from unittest.mock import MagicMock, patch

        import services.prompt_consumer as modul

        graph = MagicMock()
        if fehler is None:
            graph.stream.return_value = iter([{"perzeption": _zustand()}])
        else:
            graph.stream.side_effect = fehler

        block: list[dict] = [{
            "nachrichten_id": "n-1",
            "prompt":         REIZ,
            "empfangen_am":   EMPFANG,
            "client_id":      "desktop",
        }]

        with patch.object(modul, "event_erzeugen") as ereignis, \
             patch.object(modul, "redis_client", MagicMock()), \
             patch.object(modul, "shadow_cooldown_reset", MagicMock()), \
             patch.object(modul, "broadcast_threadsafe", MagicMock()), \
             patch.object(modul, "_audit_log", MagicMock()), \
             patch.object(modul, "turn_beenden", MagicMock()):
            await modul._block_verarbeiten(
                block, ("meister", "nova"), "t-block",
                MagicMock(create_state=MagicMock(return_value={})),
                graph,
            )

        return [ruf.kwargs for ruf in ereignis.call_args_list]

    async def test_ohne_ausnahme_entsteht_ein_ereignis(self) -> None:
        """Der positive Zwilling zum Test darunter.

        Ohne ihn bestuende der auch bei einem Consumer, der ueberhaupt kein
        Ereignis mehr erzeugt.
        """
        rufe = await self._fahren(None)
        self.assertEqual(1, len(rufe))
        self.assertNotIn("pfad1_ausfall", rufe[0]["payload"])

    async def test_mit_ausnahme_entsteht_es_ebenfalls(self) -> None:
        """Das ZIEL: Die Nutzeraeusserung ueberlebt den Abbruch."""
        with self.assertLogs("ki_server.prompt_consumer", level="ERROR"):
            rufe = await self._fahren(TimeoutError("zu spaet"))

        self.assertEqual(1, len(rufe), "kein Ereignis — der Turn waere verloren")
        self.assertEqual(rufe[0]["payload"]["user_prompt"], REIZ)

    async def test_und_traegt_dann_den_vermerk(self) -> None:
        """Ueberleben allein genuegt nicht — der Ausfall muss sichtbar sein."""
        with self.assertLogs("ki_server.prompt_consumer", level="ERROR"):
            rufe = await self._fahren(TimeoutError("zu spaet"))

        self.assertIn("TimeoutError", rufe[0]["payload"]["pfad1_ausfall"])

    async def test_die_kennungen_des_blocks_reisen_mit(self) -> None:
        """Ohne sie kann der Client seine offenen Fragen nicht schliessen."""
        rufe = await self._fahren(None)

        self.assertEqual(rufe[0]["payload"]["nachrichten_ids"], ["n-1"])
