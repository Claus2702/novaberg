"""Tests: Was ein Auftrag traegt, erreicht auch den Stapel.

Der Queue-Auftrag fuehrt seit jeher neun Werte — darunter `emotion`, `modus`
und den ausloesenden Wert. Bis zum 15.08.2026 blieben sie an der Schreibstelle
liegen: `stack_push` **nimmt** Emotion und Modus entgegen, und von drei
Agenten uebergab sie genau einer.

Gemessen am selben Tag ueber 1028 Auftraege:

    emotion   neugierig 450 · neutral 395 · begeisterung 78 · …   0 leer
    modus     philosophischer_austausch 546 · fachgespraech 158 · 141 leer
    salienz   existiert nicht — der Wert heisst `prioritaet`
              230 Auftraege tragen darin eine 0.0

Die Werte streuen also und traegen eine Aussage; sie kamen nur nie an. Der
Bestand des Stapels bestaetigte es: 86 Eintraege, belegt war einzig das
Embedding.

Zeugen dieser Datei:
  * **`None` heisst unbekannt und wird nie zu einer Zahl.** Eine 0.0 saehe wie
    eine Messung aus, und ein weggelassenes Feld waere von einem Eintrag alter
    Bauart nicht zu unterscheiden — beide Felder stehen deshalb immer im
    Eintrag, auch leer.
  * **Ein unbrauchbarer Ausloesewert bricht die Ablage nicht ab.** Er fuehrt zu
    `None`, nicht zu einer Ausnahme: Der Gedanke ist fertig recherchiert, und
    ihn wegen eines fehlenden Rangwerts zu verwerfen waere teurer als ihn
    ohne Rang abzulegen.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import json
import unittest
from unittest.mock import MagicMock, patch

from agents.recherche.agent import stapel_werte_aus_auftrag
from services.pixie import stack as stack_modul


def _redis() -> MagicMock:
    """Ein Redis, das den geschriebenen Eintrag festhaelt."""
    return MagicMock()


def _abgelegt(redis_mock: MagicMock) -> dict:
    """Liest den Eintrag, den stack_push geschrieben hat."""
    _key, roh = redis_mock.rpush.call_args[0]
    return json.loads(roh)


class DerEintragTraegtDieWerteTest(unittest.TestCase):
    """Was uebergeben wird, steht danach im Eintrag."""

    def setUp(self) -> None:
        """Der Embed-Worker wird nicht gebraucht — er liefert einen festen Vektor."""
        self._embed = patch.object(
            stack_modul.model_service, "embed",
            MagicMock(submit_sync=MagicMock(
                return_value=MagicMock(embedding=[0.1, 0.2], duration_seconds=0.01),
            )),
        )
        self._embed.start()
        self._aktiv = patch.object(stack_modul, "PIXIE_AKTIV", True)
        self._aktiv.start()

    def tearDown(self) -> None:
        """Beide Ersetzungen zurueck."""
        self._embed.stop()
        self._aktiv.stop()

    def test_salienz_und_erregung_stehen_im_eintrag(self) -> None:
        """Beide neuen Werte erreichen den Stapel."""
        r = _redis()
        stack_modul.stack_push(
            redis_client=r, user_id="meister", aufgabe="recherche",
            thema="Enceladus", inhalt="…",
            salienz=0.87, arousal=0.62,
        )
        eintrag = _abgelegt(r)

        self.assertAlmostEqual(0.87, eintrag["salienz"], places=4)
        self.assertAlmostEqual(0.62, eintrag["arousal"], places=4)

    def test_fehlende_werte_stehen_als_none_da(self) -> None:
        """Der positive Zwilling: Ohne Uebergabe sind die Felder da und leer.

        Nicht weggelassen — sonst waere ein Eintrag ohne Wert von einem
        Eintrag alter Bauart nicht zu unterscheiden.
        """
        r = _redis()
        stack_modul.stack_push(
            redis_client=r, user_id="meister", aufgabe="wiedervorlage",
            thema="Zahnarzt", inhalt="…",
        )
        eintrag = _abgelegt(r)

        self.assertIn("salienz", eintrag)
        self.assertIn("arousal", eintrag)
        self.assertIsNone(eintrag["salienz"])
        self.assertIsNone(eintrag["arousal"])

    def test_keine_null_als_ersatz(self) -> None:
        """Ein fehlender Wert wird nie zu 0.0 — das saehe wie eine Messung aus."""
        r = _redis()
        stack_modul.stack_push(
            redis_client=r, user_id="meister", aufgabe="recherche",
            thema="Titan", inhalt="…",
        )
        eintrag = _abgelegt(r)

        self.assertNotEqual(0.0, eintrag["salienz"])
        self.assertNotEqual(0.0, eintrag["arousal"])

    def test_emotion_und_modus_werden_durchgereicht(self) -> None:
        """Die beiden Felder gab es schon — sie wurden nur nicht befuellt."""
        r = _redis()
        stack_modul.stack_push(
            redis_client=r, user_id="meister", aufgabe="recherche",
            thema="Titan", inhalt="…",
            emotion="neugierig", modus="fachgespraech",
        )
        eintrag = _abgelegt(r)

        self.assertEqual("neugierig",     eintrag["emotion"])
        self.assertEqual("fachgespraech", eintrag["modus"])


class DieAgentenReichenDurchTest(unittest.TestCase):
    """Die Uebergabe an der Schreibstelle — nicht nur die Faehigkeit dazu.

    Dieser Zeuge existiert wegen einer **gruenen** Gegenprobe: Am 15.08.2026
    wurde die Werte-Uebergabe im RechercheAgenten testweise ausgeklinkt, und
    alle 1370 Tests blieben gruen. Die Zusicherungen darueber pruefen
    `stack_push` und haetten den stummen Agenten nie bemerkt — genau der
    Zustand, der zwei Monate lang bestand.
    """

    def test_der_auftrag_liefert_alle_vier_werte(self) -> None:
        """Emotion, Modus, Intentionen und Salienz stammen aus dem Auftrag."""
        werte = stapel_werte_aus_auftrag({
            "thema":       "Enceladus",
            "emotion":     "neugierig",
            "modus":       "fachgespraech",
            "prioritaet":  0.87,
            "intentionen": ["reflexion"],
        })

        self.assertEqual("neugierig",     werte["emotion"])
        self.assertEqual("fachgespraech", werte["modus"])
        self.assertEqual(["reflexion"],   werte["intentionen"])
        self.assertAlmostEqual(0.87,      werte["salienz"], places=4)

    def test_ein_auftrag_mit_null_liefert_keine_salienz(self) -> None:
        """230 von 1028 Auftraegen tragen eine 0.0 — sie ist kein Rangwert.

        Der Eintrag geht trotzdem auf den Stapel: Der Gedanke ist fertig
        recherchiert. Er bekommt nur keinen Rang.
        """
        werte = stapel_werte_aus_auftrag({"prioritaet": 0.0, "emotion": "neutral"})

        self.assertIsNone(werte["salienz"])
        self.assertEqual("neutral", werte["emotion"])

    def test_die_werte_passen_auf_die_signatur(self) -> None:
        """Der positive Zwilling: Was hier entsteht, nimmt stack_push entgegen.

        Ohne diese Zusicherung koennte die Funktion ein Feld liefern, das die
        Signatur nicht kennt — der Fehler kaeme erst zur Laufzeit im Agenten.
        """
        werte = stapel_werte_aus_auftrag({"prioritaet": 0.5})
        erlaubt = set(inspect.signature(stack_modul.stack_push).parameters)

        self.assertTrue(set(werte).issubset(erlaubt), f"unbekannt: {set(werte) - erlaubt}")


if __name__ == "__main__":
    unittest.main()
