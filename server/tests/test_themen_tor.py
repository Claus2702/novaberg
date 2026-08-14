"""Tests: Ein Gedanke erreicht ein laufendes Gespraech nur, wenn er dazu passt.

Bauteil C. Der Zustellfilter verglich bis zum 14.08.2026 ein Embedding des
Stapel-Eintrags gegen ein Embedding der **letzten fuenf Session-Turns** — und
die Session enthaelt ihre eigenen Einwuerfe. Je mehr zu einem Thema gesendet
war, desto besser passte der naechste Einwurf desselben Themas. **Der Filter
mass, ob ein Gedanke zu ihr passt, nicht ob er zum Gespraech passt.**

Gemessen ueber 56 Impulse aus sechs Tagen:

    Stapeltext gegen Stapeltext          Median 0,557   misst die Textsorte
    Stapeltext gegen Nutzeraeusserung    Median 0,105   Maximum 0,438

Auf der falschen Paarung lag der Bestand ueber der alten Schwelle von 0,40:
**52 von 56** kamen durch. Eine Zahl ohne ihre Paarung ist keine Schwelle.

Zeugen dieser Datei:
  * **Die Schwelle stammt aus dem Konzept**, nicht aus dem Pruefobjekt: 0,30,
    gemessen an etikettierten Paaren, mit 0,438 als bestem echten Treffer.
  * **Beide Richtungen.** Dass ein fernes Thema abgewiesen wird, ist erst eine
    Aussage, wenn ein nahes durchkommt — sonst waere auch ein zugemauertes Tor
    gruen.
  * **Der Bezugsvektor wird an seiner Zusammensetzung geprueft**, nicht an
    seinem Ergebnis. Ein Vektor aus allen Rollen liefert plausible Zahlen; dass
    sie die falsche Frage beantworten, sieht man ihnen nicht an.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from services import shadow_delivery as sd

# Von Hand aus `novaberg-eigenzeit_k.md` §2.4 uebernommen.
SCHWELLE: float = 0.30
BESTER_ECHTER_TREFFER: float = 0.438

AEUSSERUNG: str = "Wie kommt eigentlich Wasser auf einen Mond?"
NOVA_TURN: str = (
    "Die Kohaerenz dieser Struktur ist bemerkenswert — eine Resonanz, die "
    "sich selbst traegt und dabei eine epistemische Tiefe eroeffnet."
)


def _eintrag(thema: str, vektor: list[float] | None) -> str:
    """Ein Stapel-Eintrag, wie ihn die Recherche hinterlaesst."""
    return json.dumps({
        "thema": thema, "aufgabe": "recherche", "inhalt": "…",
        "modus": "fachgespraech",
        **({"embedding": vektor} if vektor is not None else {}),
    })


def _speicher(eintraege: list[str]) -> MagicMock:
    """Ein Redis, das genau diesen Stapel fuehrt."""
    r = MagicMock()
    r.lrange.return_value = eintraege
    return r


class DieSchwelleGehoertZuIhrerPaarungTest(unittest.TestCase):
    """Eine Zahl ohne Paarung ist keine Schwelle."""

    def test_die_schwelle_steht_bei_null_komma_drei(self) -> None:
        """0,40 galt auf Langtext gegen Langtext und liess 52 von 56 durch."""
        self.assertAlmostEqual(sd.THEMEN_SCHWELLE, SCHWELLE, places=3)

    def test_die_schwelle_liegt_unter_dem_besten_echten_treffer(self) -> None:
        """Die Schwelle bleibt erreichbar.

        Eine Schwelle oberhalb der letzten darstellbaren Stufe ihrer Quelle
        ist keine strenge Schwelle, sondern eine abgeschaltete.
        """
        self.assertLess(sd.THEMEN_SCHWELLE, BESTER_ECHTER_TREFFER)


class DerBezugsvektorKommtVomMenschenTest(unittest.TestCase):
    """Der Vektor entscheidet, welche Frage die Zahl beantwortet."""

    def _kontext(self, turns: list[dict]) -> str:
        """Liefert den Text, aus dem der Bezugsvektor gebildet wird."""
        import asyncio
        from types import SimpleNamespace

        gefangen: dict = {}

        async def _fangen(auftrag: object) -> object:
            gefangen["text"] = auftrag.text
            return SimpleNamespace(embedding=[0.1] * 8, duration_seconds=0.0)

        async def _lauf() -> None:
            with patch.object(sd, "session_turns_retrieve", return_value=turns):
                with patch.object(sd.model_service.embed, "submit",
                                  side_effect=_fangen):
                    await sd._gespraechs_embedding(MagicMock(), "meister", "nova")

        asyncio.run(_lauf())
        return gefangen.get("text", "")

    def test_novas_eigene_turns_stehen_nicht_darin(self) -> None:
        """Sonst misst der Filter, ob ein Gedanke zu ihren eigenen passt."""
        text: str = self._kontext([
            {"rolle": "user", "inhalt": AEUSSERUNG},
            {"rolle": "assistant", "inhalt": NOVA_TURN},
        ])
        self.assertIn(AEUSSERUNG, text)
        self.assertNotIn("Kohaerenz", text)

    def test_ohne_aeusserung_gibt_es_keinen_vektor(self) -> None:
        """Kein erfundener Bezug: leer heisst leer."""
        import asyncio

        with patch.object(sd, "session_turns_retrieve", return_value=[
            {"rolle": "assistant", "inhalt": NOVA_TURN},
        ]):
            vektor = asyncio.run(
                sd._gespraechs_embedding(MagicMock(), "meister", "nova"),
            )
        self.assertEqual(vektor, [])


class DasTorEntscheidetAmThemaTest(unittest.TestCase):
    """Beide Richtungen, auf demselben Stapel."""

    def _gewaehlt(self, sim: float) -> tuple:
        with patch.object(sd, "_cosine_similarity", return_value=sim):
            return sd._besten_eintrag_finden(
                _speicher([_eintrag("Eismonde", [0.2] * 8)]),
                "meister", [0.1] * 8, "neugierig", "fachgespraech",
            )

    def test_ein_fernes_thema_bleibt_liegen(self) -> None:
        """Unter der Schwelle wird nicht gewaehlt — der Eintrag wartet."""
        eintrag, index = self._gewaehlt(0.18)
        self.assertIsNone(eintrag)
        self.assertEqual(index, -1)

    def test_das_laufende_thema_kommt_durch(self) -> None:
        """Der positive Zwilling — ohne ihn bestuende auch ein totes Tor."""
        eintrag, index = self._gewaehlt(0.36)
        self.assertIsNotNone(eintrag)
        self.assertEqual(index, 0)

    def test_genau_auf_der_schwelle_kommt_durch(self) -> None:
        """Die Kante wird benannt, nicht dem Zufall des Rasters ueberlassen."""
        self.assertIsNotNone(self._gewaehlt(SCHWELLE)[0])

    def test_die_alte_schwelle_reicht_nicht_mehr(self) -> None:
        """0,40 auf der richtigen Paarung waere oberhalb des besten Treffers.

        Der Zeuge gegen die Rueckkehr der alten Zahl: 0,438 ist das Maximum,
        das ein echter Treffer je erreicht hat.
        """
        self.assertIsNotNone(self._gewaehlt(0.35)[0])


class EinAusfallSiehtNichtWieEinTrefferAusTest(unittest.TestCase):
    """Ein Eintrag ohne Embedding galt als exakt auf der Schwelle."""

    def test_ohne_embedding_wird_abgelehnt(self) -> None:
        """Nicht pruefbar ist nicht dasselbe wie passend."""
        eintrag, _ = sd._besten_eintrag_finden(
            _speicher([_eintrag("Eismonde", None)]),
            "meister", [0.1] * 8, "neugierig", "fachgespraech",
        )
        self.assertIsNone(eintrag)

    def test_die_ablehnung_ist_laut(self) -> None:
        """Ein fehlender Wert ist ein Defekt und kein Randfall."""
        with self.assertLogs("ki_server.shadow_delivery", level="ERROR") as log:
            sd._besten_eintrag_finden(
                _speicher([_eintrag("Eismonde", None)]),
                "meister", [0.1] * 8, "neugierig", "fachgespraech",
            )
        self.assertIn("ohne Embedding", "".join(log.output))


if __name__ == "__main__":
    unittest.main()
