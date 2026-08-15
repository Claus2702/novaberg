"""Tests fuer die zwei Pixie-Spuren und den Riegel dazwischen.

Ziel: Ein Agent ohne Sprachmodell wartet nicht hinter einem mit. Bis zum
09.08.2026 lief die gesamte Hintergrundarbeit durch einen Job mit
`max_instances=1`; gemessen an Konrads Bogen kam die Synapsen-Promotion in
28 Minuten **einmal** dran und brachte 1 von 72 Auftraegen durch — ihre
Prioritaetsbasis 0,90 stand gegen 63 Gespraechsauftraege zwischen 0,94 und
1,00, und eine laufende Recherche hielt den einen Platz minutenlang.

Drei Zusicherungen:

  1. Jede Spur sieht nur ihre eigenen Kandidaten.
  2. Die Spuren haben getrennte Sperren — eine laufende LLM-Spur haelt die
     CPU-Spur nicht auf. Das ist der ganze Zweck; eine gemeinsame Sperre
     haette die Trennung aufgehoben, ohne dass es auffiele.
  3. Der Riegel: Ein Agent der CPU-Spur, der doch das Sprachmodell ruft,
     scheitert laut, statt seine Spur minutenlang zu verstopfen.

Punkt 3 ist der wichtigste, und der Grund steht in der Entstehung: Beim
ersten Einordnen des Bestands wurde `charakter` fuer modellfrei gehalten,
weil sein Modellaufruf nicht in `agent.py` steht, sondern ein Modul tiefer.
**Die Lastart ist eine Eigenschaft des Aufrufbaums, nicht der Klasse** — eine
Angabe, die nichts erzwingt, driftet beim ersten Zusatz.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from services.model_services.spur import (
    SPUR_CPU,
    SPUR_LLM,
    SpurVerletzungError,
    aktive_spur,
    sprachmodell_erlaubt,
    spur_setzen,
    spur_zuruecksetzen,
)

SCHEDULER: str = "services.pixie.scheduler"


def _shadow_auftrag(salienz: float) -> dict:
    """Ein Auftrag, wie ihn ShadowAuftragRepository.bester_kandidat liefert."""
    return {
        "id": 1, "user_id": "meister", "character_id": "nova",
        "beobachter": "user", "aufgabe": "recherche", "thema": "Gravitation",
        "kontext": "", "intentionen": [], "emotion": "", "modus": "",
        "salienz_roh": salienz, "salienz_absolut": salienz,
        "salienz_decay": salienz, "haeufigkeit": 1, "aktiv": True,
        "erstellt_am": None, "verstaerkt_am": None, "decay_am": None,
        "versuche": 0,
    }


class DerRiegelZwischenDenSpurenTest(unittest.TestCase):
    """Die dritte Zusicherung: eine Fehleinsortierung faellt laut auf."""

    def test_sprachmodell_aus_der_cpu_spur_scheitert(self) -> None:
        """Das ZIEL: nicht blockieren, sondern werfen."""
        marke = spur_setzen(SPUR_CPU)
        try:
            with self.assertRaises(SpurVerletzungError) as fall:
                sprachmodell_erlaubt("background")
        finally:
            spur_zuruecksetzen(marke)

        self.assertIn("lastart", str(fall.exception),
                      "Die Meldung muss die Abhilfe nennen, nicht nur den Verstoss")

    def test_sprachmodell_aus_der_llm_spur_ist_erlaubt(self) -> None:
        """Die Gegenprobe: in der eigenen Spur darf gerufen werden."""
        marke = spur_setzen(SPUR_LLM)
        try:
            sprachmodell_erlaubt("background")
        finally:
            spur_zuruecksetzen(marke)

    def test_ausserhalb_jeder_spur_schweigt_der_riegel(self) -> None:
        """Der Gespraechspfad laeuft durch dieselbe Pruefung und darf rufen.

        Der Riegel bewacht die Spuren, nicht das Modell. Wuerde er ausserhalb
        greifen, stuende er quer im Chat-Pfad.
        """
        self.assertEqual(aktive_spur(), "")
        sprachmodell_erlaubt("chat")


class DerRiegelIstVerdrahtetTest(unittest.TestCase):
    """Ein Riegel, den niemand ruft, ist eine leere Sektionsmarke.

    Die Tests darueber pruefen die Funktion. Dieser prueft, dass der
    Sprachmodell-Worker sie tatsaechlich aufruft — und dass der Embed-Worker
    es **nicht** tut, denn den braucht die CPU-Spur.

    Der Zeuge nutzt einen ungestarteten Worker: Ohne Riegel scheitert der
    Aufruf am `RuntimeError` "nicht gestartet", mit Riegel vorher an der
    `SpurVerletzungError`. Die beiden Ausnahmen trennen die beiden Fassungen.
    """

    def test_der_background_worker_ruft_den_riegel(self) -> None:
        """Das ZIEL: der Verstoss faellt vor allem anderen auf."""
        from services.model_services.worker_base import ModelWorker

        worker: ModelWorker = ModelWorker("background")
        marke = spur_setzen(SPUR_CPU)
        try:
            with self.assertRaises(SpurVerletzungError):
                worker.submit_sync(object())
        finally:
            spur_zuruecksetzen(marke)

    def test_der_embed_worker_ist_ausgenommen(self) -> None:
        """Die Gegenprobe: Die CPU-Spur darf einbetten.

        Ohne diese Ausnahme haette der Riegel die Promotion erschlagen —
        sie ist der Grund fuer die ganze Trennung und bettet ein.
        """
        from services.model_services.worker_base import ModelWorker

        worker: ModelWorker = ModelWorker("embed")
        marke = spur_setzen(SPUR_CPU)
        try:
            with self.assertRaises(RuntimeError) as fall:
                worker.submit_sync(object())
        finally:
            spur_zuruecksetzen(marke)

        self.assertNotIsInstance(fall.exception, SpurVerletzungError)
        self.assertIn("nicht gestartet", str(fall.exception))


class JedeSpurSiehtNurIhreKandidatenTest(unittest.TestCase):
    """Die erste Zusicherung — sonst waere die Trennung eine Behauptung."""

    @staticmethod
    def _kandidat(name: str) -> dict:
        return {"name": name, "prioritaet": 1.0, "quelle": "periodisch"}

    def test_die_cpu_spur_uebergeht_einen_llm_kandidaten(self) -> None:
        """Das ZIEL: der Langlaeufer taucht in der schnellen Spur nicht auf."""
        from services.pixie import scheduler

        with patch.object(scheduler, "route", return_value="recherche"), \
             patch.object(scheduler.AgentRegistry, "finden",
                          return_value=type("A", (), {"lastart": SPUR_LLM})()):
            self.assertEqual(scheduler._spur_von(self._kandidat("recherche")), SPUR_LLM)

    def test_die_promotion_gehoert_in_die_cpu_spur(self) -> None:
        """Der Anlass der ganzen Trennung, an seinem Agenten geprueft."""
        from agents.synapsen_promotion.agent import SynapsenPromotionAgent

        self.assertEqual(SynapsenPromotionAgent().lastart, SPUR_CPU)

    def test_ein_agent_ohne_angabe_faehrt_in_der_llm_spur(self) -> None:
        """Die Vorgabe selbst, nicht nur der Weg drumherum.

        Ein neuer Agent, den niemand eingeordnet hat, gehoert in die
        langsame Spur — dort ist Blockieren erwartet. Die Gegenrichtung
        waere die gefaehrliche: Ein uebersehener Modellaufrufer verstopfte
        die schnelle Spur und erzeugte den Defekt wieder, gegen den die
        Trennung gebaut ist.
        """
        from agents.base import BaseAgent

        self.assertEqual(BaseAgent.lastart.fget(None), SPUR_LLM)

    def test_ein_unbekannter_agent_landet_in_der_langsamen_spur(self) -> None:
        """Die Vorgabe ist die sichere Richtung.

        Ein nicht eingeordneter Agent blockiert dann hoechstens dort, wo
        Blockieren erwartet wird. Die Gegenrichtung waere der Defekt, gegen
        den die Trennung gebaut ist.
        """
        from services.pixie import scheduler

        with patch.object(scheduler, "route", return_value=None):
            self.assertEqual(scheduler._spur_von(self._kandidat("unbekannt")), SPUR_LLM)


class BeideSpurenBekommenEinenKandidatenTest(unittest.TestCase):
    """Der Zeuge, der beim ersten Bau gefehlt hat — und es hat sofort gekostet.

    Geprueft war, dass der Filter richtig **einordnet**. Ungeprueft war, ob
    die CPU-Spur ueberhaupt je etwas zu sehen bekommt. `_queue_peek` faltete
    `shadow_queue` und `queue` auf **einen** Gewinner zusammen, und weil die
    Gespraechsauftraege mit 0,94 bis 1,00 gegen die Salienz der
    Promotionsauftraege immer gewinnen, war dieser eine stets ein
    LLM-Kandidat. Im Lauf vom 09.08.2026 meldete die CPU-Spur „Keine
    Kandidaten dieser Spur (1 gesamt)", waehrend 15 Promotionsauftraege
    danebenlagen.

    **Eine Zusammenfassung vor der Aufteilung macht die Aufteilung
    wirkungslos.**
    """

    def test_der_promotionsauftrag_ueberlebt_neben_einem_hoeheren_gespraechsauftrag(self) -> None:
        """Das ZIEL: zwei Quellen, zwei Gewinner — auch bei ungleicher Prioritaet.

        **Die beiden Spuren liegen seit dem 15.08.2026 in verschiedenen
        Speichern:** die Shadow-Queue in PostgreSQL, die Promotions-Queue
        weiterhin in Redis. Die Zusicherung ist dieselbe geblieben — wer vor
        der Aufteilung zusammenfasst, macht die Aufteilung wirkungslos.
        """
        import json as _json

        from services.pixie import kandidaten

        listen: dict[str, list[str]] = {
            "queue:meister": [_json.dumps({"aufgabe": "lzg_promotion", "salienz": 0.9})],
        }

        class _Redis:
            @staticmethod
            def lrange(key: str, _start: int, _stop: int) -> list[str]:
                return listen.get(key, [])

        with patch.object(kandidaten, "redis_client", _Redis), \
             patch.object(
                 kandidaten.ShadowAuftragRepository, "bester_kandidat",
                 return_value=_shadow_auftrag(1.0),
             ):
            gewinner = kandidaten._queue_peek("meister")

        namen = [g["name"] for g in gewinner]
        self.assertEqual(len(gewinner), 2, f"Beide Quellen muessen liefern, war: {namen}")
        self.assertIn("lzg_promotion", namen,
                      "Der Promotionsauftrag darf nicht vom Gespraechsauftrag verdeckt werden")

    def test_eine_leere_queue_liefert_keinen_kandidaten(self) -> None:
        """Die Gegenprobe: aus nichts wird kein Kandidat.

        **Beide Speicher werden leer gestellt.** Ein Test, der nur Redis
        leerte, liefe gegen den echten Tabellenbestand und faende dort 1036
        Auftraege — er haenge damit am aktiven Paar statt an seiner Aussage.
        """
        from services.pixie import kandidaten

        class _Redis:
            @staticmethod
            def lrange(_key: str, _start: int, _stop: int) -> list[str]:
                return []

        with patch.object(kandidaten, "redis_client", _Redis), \
             patch.object(
                 kandidaten.ShadowAuftragRepository, "bester_kandidat",
                 return_value=None,
             ):
            self.assertEqual(kandidaten._queue_peek("meister"), [])


class DieSpurenHabenGetrennteSperrenTest(unittest.TestCase):
    """Die zweite Zusicherung, und die am leichtesten zu verlieren.

    Eine gemeinsame `pixie:running` haette beide Spuren serialisiert. Der
    Schaden waere unsichtbar gewesen: Die Trennung stuende im Code, und die
    Wirkung waere dieselbe wie vorher.
    """

    def test_die_sperre_traegt_den_namen_der_spur(self) -> None:
        """Das ZIEL: zwei Schluessel, nicht einer."""
        import inspect

        from services.pixie import scheduler

        quelle: str = inspect.getsource(scheduler.pixie_heartbeat)
        self.assertIn('f"pixie:running:{spur}"', quelle)
        self.assertNotIn('"pixie:running"', quelle,
                         "Eine gemeinsame Sperre haette beide Spuren serialisiert")


if __name__ == "__main__":
    unittest.main()
