"""Zeugen: verstaerkt wird nur, was die Antwort hergenommen hat.

Ziel: Eine Erinnerung, die gelesen und **nicht** verwendet wurde, bewegt
nichts — und eine, die die Antwort aufgreift, wird verstaerkt.

**Diese Zeugen fassen den Produktivbestand nicht an.** Sie ersetzen den
Einbetter und den Speicher; die Validierungspfade kehren vor dem
Verbindungsaufbau zurueck.

Der Anlass steht im Bestand: Bis zum 04.09.2026 verstaerkte **kein** Weg an
der Verwendung. Zwei Mechanismen verstaerkten an der Nachbarschaft, und
`95,2 %` aller Verstaerkungen trugen einen identischen Vektor.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import MagicMock, patch

from config import POSTGRES_URL, VERWENDUNG_MAX_JE_TURN, VERWENDUNG_NAEHE_SCHWELLE
from memory import usage_reinforcement

MODUL:  str = "memory.usage_reinforcement"
AGENT:  str = "graph.nodes.dispatcher"


def _embed(vektor: list[float] | None) -> MagicMock:
    """Ein Einbetter, der genau diesen Vektor liefert."""
    antwort = MagicMock()
    antwort.embedding = vektor
    dienst = MagicMock()
    dienst.embed.submit_sync.return_value = antwort
    return dienst


class DieSchwelleTrenntVerwendungVonNachbarschaftTest(unittest.TestCase):
    """§7.1a — der Kern der Regel."""

    def test_der_wert_steht_auf_der_gemessenen_zahl(self) -> None:
        """0,55 liegt zwischen P99,9 (0,5412) und P99,99 (0,6672).

        Die Zahl steht als Literal und nicht als Ausdruck ueber der Konstante:
        Ein Zeuge, der seine Erwartung aus dem Prueflig rechnet, macht jede
        Aenderung mit — das ist am 03.09.2026 an 37 gruenen Zeugen gemessen
        worden.
        """
        self.assertEqual(
            0.55, VERWENDUNG_NAEHE_SCHWELLE,
            "Die Schwelle weicht vom gemessenen Wert ab — wurde sie bewusst "
            "geaendert, gehoert die Herleitung in `config.py` mitgezogen",
        )
        self.assertEqual(3, VERWENDUNG_MAX_JE_TURN)

    def test_ueber_der_schwelle_gilt_als_hergenommen(self) -> None:
        """Der Normalfall — sonst prueft der Rest der Klasse gegen nichts."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (11, 0.7916), (12, 0.6100),
            ]
            treffer = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11, 12],
            )
        self.assertEqual([(11, 0.7916), (12, 0.61)], treffer)

    def test_unter_der_schwelle_bewegt_nichts(self) -> None:
        """Gelesen und nicht verwendet — genau der Fall, den §7.1a sperrt.

        0,5305 war das Maximum der Zufallsverteilung ueber 75.975 Paare. Eine
        Erinnerung auf diesem Wert ist Nachbarschaft, keine Verwendung.
        """
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (11, 0.5305), (12, 0.4377),
            ]
            treffer = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11, 12],
            )
        self.assertEqual([], treffer)

    def test_der_deckel_greift(self) -> None:
        """Ein breiterer Lesepfad darf nicht beliebig viel verstaerken."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (i, 0.9 - i / 100) for i in range(6)
            ]
            treffer = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", list(range(6)),
            )
        self.assertEqual(VERWENDUNG_MAX_JE_TURN, len(treffer))
        self.assertEqual(0, treffer[0][0], "Der staerkste Treffer fehlt")

    def test_eine_leere_antwort_bettet_nichts_ein(self) -> None:
        """Sie hat nichts hergenommen — und kostet keinen Aufruf."""
        dienst = _embed([0.1] * 768)
        with patch(f"{MODUL}.model_service", dienst):
            self.assertEqual(
                [], usage_reinforcement.used_memories_find(POSTGRES_URL, "  ", [11]),
            )
        dienst.embed.submit_sync.assert_not_called()

    def test_ohne_gelesene_erinnerungen_bettet_nichts_ein(self) -> None:
        """Der haeufigste Fall: 445 von 1296 Laeufen lieferten keine."""
        dienst = _embed([0.1] * 768)
        with patch(f"{MODUL}.model_service", dienst):
            self.assertEqual(
                [], usage_reinforcement.used_memories_find(POSTGRES_URL, "Antwort", []),
            )
        dienst.embed.submit_sync.assert_not_called()

    def test_ein_leerer_vektor_verstaerkt_nichts(self) -> None:
        """Ein ausgefallener Einbetter darf nicht wie *nichts verwendet* aussehen."""
        with patch(f"{MODUL}.model_service", _embed([])), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            treffer = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "Antwort", [11],
            )
        self.assertEqual([], treffer)
        verbindung.assert_not_called()

    def test_nur_die_gelesenen_knoten_werden_gefragt(self) -> None:
        """Nicht gegen den Bestand — sonst waere es wieder Nachbarschaft.

        Ein Knoten, den der Lesepfad nie angeboten hat, kann die Antwort nicht
        hergenommen haben.
        """
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = []
            usage_reinforcement.used_memories_find(POSTGRES_URL, "Antwort", [11, 12])
            abfrage = verbindung.return_value.cursor.return_value.execute.call_args
        self.assertIn("id = ANY(", abfrage[0][0])
        self.assertEqual([11, 12], abfrage[0][1][1])


class DerLaufFuehrtBuchTest(unittest.TestCase):
    """`verwendet` und `verstaerkt` gehen auf, sonst ist der Lauf blind."""

    def test_jeder_treffer_wird_verstaerkt(self) -> None:
        with patch(f"{MODUL}.used_memories_find",
                   return_value=[(11, 0.72), (12, 0.61)]), \
             patch(f"{MODUL}.lzg_knoten.knoten_verstaerken", return_value=1.0) as v:
            ergebnis = usage_reinforcement.reinforce_used(POSTGRES_URL, "A", [11, 12, 13])
        self.assertEqual(3, ergebnis["geprueft"])
        self.assertEqual(2, ergebnis["verwendet"])
        self.assertEqual(2, ergebnis["verstaerkt"])
        self.assertEqual([0.72, 0.61], ergebnis["naehen"])
        self.assertIsNone(ergebnis["error"])
        self.assertEqual(2, v.call_count)

    def test_ein_gescheiterter_schreibvorgang_wird_gemeldet(self) -> None:
        """Sonst waere *hergenommen und nicht verstaerkt* unsichtbar."""
        with patch(f"{MODUL}.used_memories_find",
                   return_value=[(11, 0.72), (12, 0.61)]), \
             patch(f"{MODUL}.lzg_knoten.knoten_verstaerken", side_effect=[1.0, None]):
            ergebnis = usage_reinforcement.reinforce_used(POSTGRES_URL, "A", [11, 12])
        self.assertEqual(2, ergebnis["verwendet"])
        self.assertEqual(1, ergebnis["verstaerkt"])
        self.assertIsNotNone(ergebnis["error"])


class DerDispatcherRuftDieVerstaerkungTest(unittest.TestCase):
    """Die Verdrahtung — an dieser Schicht dreimal der Befund gewesen."""

    ZUSTAND: dict = {
        "antwort_inhalt": "Person A stellt fest, dass …",
        "lzg_resonanz": {"erinnerungen": [
            {"knoten_id": 11, "inhalt": "a"}, {"knoten_id": 12, "inhalt": "b"},
        ]},
        "turn_id": "t1", "user_id": "meister", "character_id": "nova",
    }

    def test_der_dispatcher_reicht_die_gelesenen_kennungen_weiter(self) -> None:
        from graph.nodes.dispatcher import _verwendung_verstaerken

        leer: dict = {"geprueft": 2, "verwendet": 1, "verstaerkt": 1,
                      "naehen": [0.72], "error": None}
        with patch(f"{AGENT}.usage_reinforcement.reinforce_used",
                   return_value=leer) as gerufen, \
             patch(f"{AGENT}.log_db_write"):
            _verwendung_verstaerken(dict(self.ZUSTAND), POSTGRES_URL)
        gerufen.assert_called_once()
        self.assertEqual([11, 12], gerufen.call_args[0][2])

    def test_dispatch_ruft_die_verstaerkung(self) -> None:
        """Die Frage, die keiner der Zeugen darueber stellt.

        `[gemessen]` 04.09.2026: Eine Gegenprobe, die den Aufruf aus `dispatch`
        entfernte, liess **alle 2964** Zeugen gruen — die Zeugen oben rufen
        `_verwendung_verstaerken` selbst und pruefen damit die Faehigkeit,
        nicht den Gebrauch. Genau diese Luecke hat an dieser Schicht schon
        dreimal einen Bauteil ohne Aufrufer stehen lassen.

        Der Zugriff ist der Quelltext und nicht ein Lauf durch `dispatch`:
        Der Knoten haengt an Redis, Registry und einem halben Dutzend Manager;
        ein Zeuge, der das alles nachbildet, prueft am Ende seine Attrappen.
        """
        import inspect

        from graph.nodes import dispatcher

        quelle: str = inspect.getsource(dispatcher.dispatch)
        self.assertIn(
            "_verwendung_verstaerken(", quelle,
            "`dispatch` ruft die Verstaerkung nicht — der Bauteil steht ohne "
            "Aufrufer, und keine Antwort verstaerkt mehr etwas",
        )

    def test_die_verstaerkung_laeuft_nach_dem_protokoll(self) -> None:
        """Sonst fehlt die Antwort im Protokoll, wenn das Einbetten ausfaellt."""
        import inspect

        from graph.nodes import dispatcher

        quelle: str = inspect.getsource(dispatcher.dispatch)
        # Erst die Anwesenheit, dann die Reihenfolge — sonst wirft `index`
        # statt zu scheitern, und die Meldung sagt nichts.
        self.assertIn("_verwendung_verstaerken(", quelle)
        self.assertIn("_turn_roh_schreiben(state)", quelle)
        self.assertLess(
            quelle.index("_turn_roh_schreiben(state)"),
            quelle.index("_verwendung_verstaerken("),
            "Die Verstaerkung laeuft vor dem Turn-Protokoll — faellt das "
            "Einbetten aus, fehlt die Antwort im Protokoll",
        )

    def test_ohne_erinnerungen_wird_nicht_gerufen(self) -> None:
        from graph.nodes.dispatcher import _verwendung_verstaerken

        zustand: dict = dict(self.ZUSTAND)
        zustand["lzg_resonanz"] = {"erinnerungen": []}
        with patch(f"{AGENT}.usage_reinforcement.reinforce_used") as gerufen:
            _verwendung_verstaerken(zustand, POSTGRES_URL)
        gerufen.assert_not_called()

    def test_ohne_antwort_wird_nicht_gerufen(self) -> None:
        """Ein Turn ohne Antwort hat nichts hergenommen."""
        from graph.nodes.dispatcher import _verwendung_verstaerken

        zustand: dict = dict(self.ZUSTAND)
        zustand["antwort_inhalt"] = ""
        with patch(f"{AGENT}.usage_reinforcement.reinforce_used") as gerufen:
            _verwendung_verstaerken(zustand, POSTGRES_URL)
        gerufen.assert_not_called()

    def test_ein_fehlschlag_beendet_den_turn_nicht(self) -> None:
        """Die Antwort ist zugestellt; eine Verstaerkung darf sie nicht kosten."""
        from graph.nodes.dispatcher import _verwendung_verstaerken

        with patch(f"{AGENT}.usage_reinforcement.reinforce_used",
                   side_effect=RuntimeError("Einbetter weg")):
            _verwendung_verstaerken(dict(self.ZUSTAND), POSTGRES_URL)


if __name__ == "__main__":
    unittest.main()
