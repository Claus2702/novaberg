"""Tests: Die Erregung reist vom Turn durch die Queue bis auf den Stapel.

Die Shadow-Queue trug die Lage, aus der ein Auftrag entstand, seit jeher ueber
`emotion` und `modus` — und liess die **dritte Groesse derselben Lage** weg.
Die Folge war kein Fehler, sondern eine Leere: Die Recherche konnte keinen
Level auf den Stapel legen, weil sie keinen bekam, und Bauteil B
(`novaberg-eigenzeit_k.md` §5.2) war gebaut, bezeugt und ohne Eingabe —
gemessen am 15.08.2026 trug **kein einziger** Stapel-Eintrag einen Level.

Die Kette hat vier Nähte, und diese Datei prueft jede einzeln:

    salienz_obj -> shadow_queue_push -> ShadowAuftrag -> INSERT
                -> Auftrag -> stapel_werte_aus_auftrag -> stack_push

**`None` heisst unbekannt und wird nie zu einer Zahl.** Die Spalte ist deshalb
NULL-faehig und **ohne Vorgabewert** — anders als ihre beiden Nachbarn. Eine
0.5 saehe wie eine Messung aus und hoebe beim Einwurf Novas Zustand auf eine
erfundene Zahl; das ist dieselbe Fehlerklasse, die als
`KANDIDATEN-PRIORITAET-STILLE-NULL` im Register steht.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import inspect
import unittest
from unittest.mock import MagicMock, patch

from memory import kzg as kzg_modul
from memory.repositories.shadow_auftrag_repository import LESE_SPALTEN, ShadowAuftrag
from services.shadow_agent import utils as utils_modul


class DerAuftragTraegtDieErregungTest(unittest.TestCase):
    """Die Datenklasse und die Spaltenliste kennen sie."""

    def test_die_datenklasse_kennt_sie_ohne_ersatzwert(self) -> None:
        """`None` ist der Vorgabewert — und er bedeutet unbekannt, nicht null."""
        auftrag = ShadowAuftrag(
            user_id="u", character_id="nova", beobachter="user",
            aufgabe="recherche", thema="t", salienz=0.8,
        )

        self.assertIsNone(auftrag.arousal)

    def test_die_lesespalten_nennen_sie(self) -> None:
        """Sonst laesst der Auswahlpfad sie liegen, und der Agent bekommt nichts."""
        self.assertIn("arousal", LESE_SPALTEN)

    def test_der_insert_nennt_sie(self) -> None:
        """Eine Spalte, die kein INSERT nennt, bleibt fuer immer NULL."""
        from memory.repositories import shadow_auftrag_repository as repo

        quelle: str = inspect.getsource(repo.ShadowAuftragRepository.einreihen)

        self.assertIn("arousal", quelle)
        # Der Platzhalter muss mitgewachsen sein — sonst schiebt sich die
        # Werteliste um eins und jede Spalte danach traegt den falschen Wert.
        self.assertIn("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s", quelle)


class DerSchreiberReichtSieDurchTest(unittest.TestCase):
    """`shadow_queue_push` nimmt sie entgegen und legt sie in den Auftrag."""

    def _eingereichter_auftrag(self, **zusatz: object) -> ShadowAuftrag:
        """Faengt den Auftrag ab, den der Schreiber an das Repository gibt."""
        einreihen = MagicMock(return_value=(1, "angelegt"))
        with patch(
            "memory.repositories.shadow_auftrag_repository."
            "ShadowAuftragRepository.einreihen",
            einreihen,
        ):
            utils_modul.shadow_queue_push(
                redis_client = MagicMock(),
                user_id      = "meister",
                aufgabe      = "recherche",
                thema        = "Enceladus",
                prioritaet   = 0.8,
                **zusatz,
            )
        return einreihen.call_args[0][1]

    def test_die_erregung_erreicht_den_auftrag(self) -> None:
        """Der Normalfall."""
        self.assertAlmostEqual(0.72, self._eingereichter_auftrag(arousal=0.72).arousal, places=4)

    def test_ohne_erregung_bleibt_der_auftrag_leer(self) -> None:
        """Kein Ersatzwert — und der Aufrufer muss sie nicht kennen."""
        self.assertIsNone(self._eingereichter_auftrag().arousal)


class BeideAufrufstellenLesenSieAusDerLageTest(unittest.TestCase):
    """Zwei Erzeuger, und beide muessen bedient sein.

    Der Vortag hat gezeigt, was ein uebersehener Erzeuger kostet: Von zwei
    Aufrufern uebergab genau einer die Salienz, und der Aufruf des anderen sah
    dabei vollstaendig aus — 233 von 1036 Auftraegen mit einer stillen Null.
    """

    def test_der_kzg_speicher_liest_sie_aus_dem_salienz_objekt(self) -> None:
        """Dieselbe Quelle wie Emotion und Modus daneben."""
        quelle: str = inspect.getsource(kzg_modul.kzg_store)

        self.assertIn('salienz_obj.get("arousal")', quelle)
        # **Nicht `arousal`** — der Name traegt in dieser Funktion den
        # geklemmten Wert mit Ausfallwert 0.5 fuer den KZG-Hash. Die
        # Queue bekommt die ungefilterte Groesse.
        self.assertIn("arousal      = arousal_gemessen", quelle)

    def test_der_queue_knoten_liest_sie_aus_dem_salienz_objekt(self) -> None:
        """Der zweite Erzeuger, im KZG-Agenten."""
        from agents.kzg import queues as queues_modul

        quelle: str = inspect.getsource(queues_modul)

        self.assertIn('salienz_obj.get("arousal")', quelle)
        self.assertIn("arousal=arousal", quelle)

    def test_die_queue_bekommt_nie_den_geklemmten_wert(self) -> None:
        """Der Fund, der diesen Zeugen gerechtfertigt hat.

        `kzg_store` fuehrt **zwei** Erregungen: den geklemmten Wert mit
        Ausfallwert 0.5 fuer den KZG-Hash (Bestand) und den ungefilterten fuer
        die Queue. Unter einem Namen ueberschrieb die zweite Zuweisung die
        erste **vor** dem Queue-Aufruf — jeder Auftrag ohne gemessene Erregung
        haette eine 0.5 getragen, still und ohne rote Zeile.
        """
        quelle: str = inspect.getsource(kzg_modul.kzg_store)

        self.assertIn("arousal_gemessen: float | None", quelle)
        self.assertNotIn("arousal      = arousal,", quelle)

    def test_der_queue_knoten_erfindet_keinen_wert(self) -> None:
        """Der zweite Erzeuger hat die Doppelung nicht — und soll sie nicht bekommen."""
        from agents.kzg import queues as queues_modul

        quelle: str = inspect.getsource(queues_modul)

        self.assertNotIn('salienz_obj.get("arousal", 0', quelle)


if __name__ == "__main__":
    unittest.main()
