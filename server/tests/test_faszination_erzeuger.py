"""Zeugen: die Faszination wird je Turn gerechnet und protokolliert.

Ziel: Nach einem Turn steht eine `pipeline_log`-Zeile `faszination`, aus der
sich der Wert **nachrechnen** laesst — mit den Traegern, den Modulatoren und
dem Praegungszug, aus denen er entstand.

**Auch der leere Turn schreibt.** Ein Turn ohne Zeile waere von einem Turn
ohne Traeger nicht zu unterscheiden; dieselbe Lehre wie beim Faden-Tor, wo
`EMGRAV-SCHWELLE-TOT` wochenlang unbemerkt blieb, weil nichts gezaehlt wurde.

Diese Zeugen fassen den Produktivbestand nicht an: Der Speicher ist ersetzt.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

NODE: str = "graph.nodes.praegung"


def _emotion(**werte) -> MagicMock:
    """Ein Emotionsobjekt mit den Feldern, die die Modulatoren lesen."""
    e = MagicMock()
    e.arousal = werte.get("arousal", 0.5)
    e.emotion = werte.get("emotion", "neugierig")
    e.emotions_vector = werte.get("emotions_vector", "plateau")
    e.intent = werte.get("intent", "knowledge")
    e.mode = werte.get("mode", "alltag")
    return e


def _zustand(knoten_ids: list[int] | None = None) -> dict:
    """Ein Turn-Zustand mit gelesenen Erinnerungen."""
    aussen, innen = MagicMock(), MagicMock()
    aussen.emotion = _emotion()
    innen.emotion = _emotion()
    return {
        "turn_id": "t-1", "user_id": "meister", "character_id": "nova",
        "external": aussen, "internal": innen,
        "lzg_resonanz": {
            "erinnerungen": [{"knoten_id": k} for k in (knoten_ids or [])],
        },
    }


def _traeger(profil: bool = True, tage: int = 3, turns: int = 3) -> dict:
    """Ein Traegerdatensatz, wie ihn der Speicher liefert."""
    return {
        "tage": tage, "turns": turns, "eigenimpuls": 0.5,
        "profil": {"komplexitaet": 0.8, "weite": 0.4} if profil else {},
    }


class DieZeileEntstehtImmerTest(unittest.TestCase):
    """Ein Turn ohne Zeile waere von einem ohne Traeger nicht zu trennen."""

    def test_ohne_erinnerungen_wird_trotzdem_geschrieben(self) -> None:
        from graph.nodes.praegung import _faszination_protokollieren

        with patch(f"{NODE}.log_berechnung") as geschrieben:
            _faszination_protokollieren(_zustand([]), "meister", "nova", 1.0)
        inhalt = geschrieben.call_args.kwargs["inhalt"]
        self.assertEqual("faszination", inhalt["schritt"])
        self.assertEqual(0, inhalt["traeger_geprueft"])
        self.assertEqual("keine gelesenen Erinnerungen", inhalt["grund"])

    def test_ohne_emotionsobjekte_wird_der_grund_genannt(self) -> None:
        """Nicht stumm 1.0 — die Modulatoren waeren dann frei erfunden."""
        from graph.nodes.praegung import _faszination_protokollieren

        zustand = _zustand([11])
        zustand["internal"] = None
        with patch(f"{NODE}.log_berechnung") as geschrieben:
            _faszination_protokollieren(zustand, "meister", "nova", 1.0)
        self.assertIn(
            "fehlt", geschrieben.call_args.kwargs["inhalt"]["grund"],
        )

    def test_der_speicher_wird_ohne_traeger_nicht_gefragt(self) -> None:
        """Eine Abfrage ohne Kennungen kostet eine Verbindung fuer nichts."""
        from graph.nodes.praegung import _faszination_protokollieren

        with patch(f"{NODE}.log_berechnung"), \
             patch(f"{NODE}.traegerdaten_lesen") as gelesen:
            _faszination_protokollieren(_zustand([]), "meister", "nova", 1.0)
        gelesen.assert_not_called()


class DieZeileIstNachrechenbarTest(unittest.TestCase):
    """§10.6 — ohne die Eingangsgroessen ist der Wert eine Behauptung."""

    def test_sie_traegt_modulatoren_zug_und_rohwerte(self) -> None:
        from graph.nodes.praegung import _faszination_protokollieren

        with patch(f"{NODE}.log_berechnung") as geschrieben, \
             patch(f"{NODE}.traegerdaten_lesen", return_value={11: _traeger()}):
            _faszination_protokollieren(_zustand([11]), "meister", "nova", 1.3)
        inhalt = geschrieben.call_args.kwargs["inhalt"]
        self.assertEqual(6, len(inhalt["modulatoren"]))
        self.assertEqual(1.3, inhalt["praegungszug"])
        self.assertIn("11", inhalt["werte"])
        self.assertIn("11", inhalt["rohe"])
        self.assertGreater(inhalt["werte"]["11"], 0.0)

    def test_der_rohwert_steht_neben_dem_geglaetteten(self) -> None:
        """Ueber dem Deckel ist die Glaettung nicht umkehrbar."""
        from graph.nodes.praegung import _faszination_protokollieren

        with patch(f"{NODE}.log_berechnung") as geschrieben, \
             patch(f"{NODE}.traegerdaten_lesen", return_value={11: _traeger()}):
            _faszination_protokollieren(_zustand([11]), "meister", "nova", 1.6)
        inhalt = geschrieben.call_args.kwargs["inhalt"]
        self.assertNotEqual(inhalt["werte"]["11"], inhalt["rohe"]["11"])


class EinTraegerOhneProfilHatKeineFaszinationTest(unittest.TestCase):
    """Das ist die Aussage der Groesse, kein Ausfall."""

    def test_er_wird_gezaehlt_statt_gerechnet(self) -> None:
        from graph.nodes.praegung import _faszination_protokollieren

        with patch(f"{NODE}.log_berechnung") as geschrieben, \
             patch(f"{NODE}.traegerdaten_lesen",
                   return_value={11: _traeger(profil=False)}):
            _faszination_protokollieren(_zustand([11]), "meister", "nova", 1.0)
        inhalt = geschrieben.call_args.kwargs["inhalt"]
        self.assertEqual(1, inhalt["ohne_profil"])
        self.assertEqual({}, inhalt["werte"])

    def test_geprueft_zaehlt_auch_die_ohne_profil(self) -> None:
        """Sonst saehe ein Turn mit zehn profillosen Traegern leer aus."""
        from graph.nodes.praegung import _faszination_protokollieren

        with patch(f"{NODE}.log_berechnung") as geschrieben, \
             patch(f"{NODE}.traegerdaten_lesen",
                   return_value={11: _traeger(profil=False),
                                 12: _traeger(profil=True)}):
            _faszination_protokollieren(
                _zustand([11, 12]), "meister", "nova", 1.0,
            )
        inhalt = geschrieben.call_args.kwargs["inhalt"]
        self.assertEqual(2, inhalt["traeger_geprueft"])
        self.assertEqual(1, inhalt["ohne_profil"])
        self.assertEqual(1, len(inhalt["werte"]))


class DerZugWirdWeitergereichtTest(unittest.TestCase):
    """Er liegt nur im Praegungsknoten vor und ist einer der neun Faktoren."""

    def test_der_protokollierer_gibt_den_zug_zurueck(self) -> None:
        from graph.nodes.praegung import _zug_protokollieren

        with patch(f"{NODE}.log_berechnung"), \
             patch(f"{NODE}.praegungszug", return_value={"zug": 1.42}), \
             patch(f"{NODE}._konfrontation_des_paares", return_value=0.5):
            zustand = _zustand([])
            zustand["prompt_embedding"] = [0.1] * 768
            self.assertEqual(
                1.42, _zug_protokollieren(zustand, "meister", "nova"),
            )

    def test_ohne_zug_kommt_der_neutrale_wert(self) -> None:
        """1.0 daempft nicht — ein fehlender Zug darf nicht loeschen."""
        from graph.nodes.praegung import _zug_protokollieren

        with patch(f"{NODE}.log_berechnung"):
            zustand = _zustand([])
            zustand["prompt_embedding"] = []
            self.assertEqual(
                1.0, _zug_protokollieren(zustand, "meister", "nova"),
            )


class DerKnotenRuftDenErzeugerTest(unittest.TestCase):
    """Die Verdrahtung selbst — und sie ist die Lehre vom 04.09.2026.

    Dort riefen alle Zeugen der Verwendungs-Verstaerkung die Funktion
    **selbst**; keiner pruefte, dass der Knoten sie ruft. Die Gegenprobe sagte
    0 rot voraus und behielt recht — der Aufruf fehlte und niemand sah es.
    """

    def test_praegung_pruefen_ruft_die_faszination(self) -> None:
        from graph.nodes.praegung import praegung_pruefen

        # **Ohne Salienz und ohne Verlauf** — genau der Fall, in dem der Node
        # frueh zurueckkehrt. Beide Protokolle muessen trotzdem laufen.
        zustand = _zustand([11])
        with patch(f"{NODE}._faszination_protokollieren") as gerufen, \
             patch(f"{NODE}._zug_protokollieren", return_value=1.2), \
             patch(f"{NODE}.log_berechnung"):
            praegung_pruefen(zustand)
        gerufen.assert_called_once()
        self.assertEqual(
            1.2, gerufen.call_args[0][3],
            "Der Knoten muss den gerechneten Zug weiterreichen, nicht 1.0",
        )

    def test_die_faszination_laeuft_auch_ohne_verlauf(self) -> None:
        """Ein Rueckkehrpfad darf die Protokolle nicht mitnehmen.

        Faszination und Praegung sind zwei Groessen: Ein Turn kann einen
        Traeger beruehren, ohne einschneidend genug fuer einen Faden zu sein
        — und ein Turn, dem der Verlauf fehlt, ist genau der, ueber den man
        etwas wissen will.
        """
        from graph.nodes.praegung import praegung_pruefen

        zustand = _zustand([11])
        zustand["nova_emotions_verlauf"] = []
        with patch(f"{NODE}._faszination_protokollieren") as gerufen, \
             patch(f"{NODE}._zug_protokollieren", return_value=1.0), \
             patch(f"{NODE}.log_berechnung"):
            praegung_pruefen(zustand)
        gerufen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
