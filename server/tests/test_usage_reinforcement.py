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
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11, 12],
            )
        self.assertEqual([(11, 0.7916), (12, 0.61)], befund.treffer)
        self.assertEqual(usage_reinforcement.AUSGANG_GERECHNET, befund.ausgang)

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
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11, 12],
            )
        self.assertEqual([], befund.treffer)

    def test_der_deckel_greift(self) -> None:
        """Ein breiterer Lesepfad darf nicht beliebig viel verstaerken."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (i, 0.9 - i / 100) for i in range(6)
            ]
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", list(range(6)),
            )
        self.assertEqual(VERWENDUNG_MAX_JE_TURN, len(befund.treffer))
        self.assertEqual(0, befund.treffer[0][0], "Der staerkste Treffer fehlt")
        self.assertEqual(
            6, len(befund.naehen_alle),
            "Der Deckel darf die verworfenen Naehen nicht mitloeschen — sie "
            "sind die Eingangsgroessen der Entscheidung",
        )

    def test_eine_leere_antwort_bettet_nichts_ein(self) -> None:
        """Sie hat nichts hergenommen — und kostet keinen Aufruf."""
        dienst = _embed([0.1] * 768)
        with patch(f"{MODUL}.model_service", dienst):
            befund = usage_reinforcement.used_memories_find(POSTGRES_URL, "  ", [11])
        self.assertEqual([], befund.treffer)
        self.assertEqual(usage_reinforcement.AUSGANG_ANTWORT_LEER, befund.ausgang)
        dienst.embed.submit_sync.assert_not_called()

    def test_ohne_gelesene_erinnerungen_bettet_nichts_ein(self) -> None:
        """Der haeufigste Fall: 445 von 1296 Laeufen lieferten keine."""
        dienst = _embed([0.1] * 768)
        with patch(f"{MODUL}.model_service", dienst):
            befund = usage_reinforcement.used_memories_find(POSTGRES_URL, "Antwort", [])
        self.assertEqual([], befund.treffer)
        self.assertEqual(usage_reinforcement.AUSGANG_OHNE_KANDIDAT, befund.ausgang)
        dienst.embed.submit_sync.assert_not_called()

    def test_ein_leerer_vektor_verstaerkt_nichts(self) -> None:
        """Ein ausgefallener Einbetter darf nicht wie *nichts verwendet* aussehen."""
        with patch(f"{MODUL}.model_service", _embed([])), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "Antwort", [11],
            )
        self.assertEqual([], befund.treffer)
        self.assertEqual(usage_reinforcement.AUSGANG_VEKTOR_LEER, befund.ausgang)
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
        befund = usage_reinforcement.Verwendungsbefund(
            treffer=[(11, 0.72), (12, 0.61)],
            naehen_alle={11: 0.72, 12: 0.61, 13: 0.30},
        )
        with patch(f"{MODUL}.used_memories_find", return_value=befund), \
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
        befund = usage_reinforcement.Verwendungsbefund(
            treffer=[(11, 0.72), (12, 0.61)],
            naehen_alle={11: 0.72, 12: 0.61},
        )
        with patch(f"{MODUL}.used_memories_find", return_value=befund), \
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
                      "naehen": [0.72], "naehen_alle": {11: 0.72, 12: 0.30},
                      "knappster_verworfener": 0.30, "schwelle": 0.55,
                      "deckel": 3, "ausgang": usage_reinforcement.AUSGANG_GERECHNET,
                      "error": None}
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


class EinNullbefundSagtWarumTest(unittest.TestCase):
    """Die Entscheidung, nicht ihr Ergebnis.

    Der Anlass ist gemessen: Die beiden ersten Betriebszeilen vom 04.09.2026
    trugen `verwendet: 0, naehen: []` und konnten nicht sagen, warum. Fuenf
    Rueckkehrpfade und der Normalfall *nichts ueber der Schwelle* sahen in der
    Zeile identisch aus.
    """

    def test_die_verworfenen_naehen_bleiben_erhalten(self) -> None:
        """Die eine Zahl, die beim Kalibrieren zaehlt.

        Ohne sie ist nicht zu unterscheiden, ob die Kandidaten bei 0,54 lagen
        oder bei 0,12 — und damit nicht, ob die Schwelle zu hoch steht.
        """
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (11, 0.5412), (12, 0.1200),
            ]
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11, 12],
            )
        self.assertEqual([], befund.treffer)
        self.assertEqual({11: 0.5412, 12: 0.12}, befund.naehen_alle)
        self.assertEqual(0.5412, befund.knappster_verworfener())

    def test_der_knappste_verworfene_ignoriert_die_genommenen(self) -> None:
        """Er misst den Abstand der Schwelle zum Bestand, nicht zum Treffer."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (11, 0.9000), (12, 0.5400),
            ]
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11, 12],
            )
        self.assertEqual([(11, 0.9)], befund.treffer)
        self.assertEqual(0.54, befund.knappster_verworfener())

    def test_ohne_verworfene_gibt_es_keinen_knappsten(self) -> None:
        """Kein Vorgabewert: `None` heisst *es gab keinen*, 0.0 hiesse *sehr fern*."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (11, 0.9000),
            ]
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11],
            )
        self.assertIsNone(befund.knappster_verworfener())

    def test_ein_db_fehler_traegt_seine_eigene_marke(self) -> None:
        """Der sechste Ausgang — und der einzige, der ohne Marke wie Erfolg aussieht."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            import psycopg2 as _pg
            verbindung.return_value.cursor.return_value.execute.side_effect = (
                _pg.OperationalError("Verbindung weg")
            )
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11],
            )
        self.assertEqual([], befund.treffer)
        self.assertEqual(usage_reinforcement.AUSGANG_DB_FEHLER, befund.ausgang)
        self.assertEqual({}, befund.naehen_alle)

    def test_ein_embed_fehler_traegt_seine_eigene_marke(self) -> None:
        """Ein ausgefallener Einbetter ist kein Turn ohne Verwendung."""
        dienst = MagicMock()
        dienst.embed.submit_sync.side_effect = RuntimeError("Einbetter weg")
        with patch(f"{MODUL}.model_service", dienst):
            befund = usage_reinforcement.used_memories_find(
                POSTGRES_URL, "eine Antwort", [11],
            )
        self.assertEqual(usage_reinforcement.AUSGANG_EMBED_FEHLER, befund.ausgang)

    def test_die_sechs_ausgaenge_sind_unterscheidbar(self) -> None:
        """Sonst traegt die Marke nichts — sie soll gerade trennen."""
        marken: list[str] = [
            usage_reinforcement.AUSGANG_GERECHNET,
            usage_reinforcement.AUSGANG_ANTWORT_LEER,
            usage_reinforcement.AUSGANG_OHNE_KANDIDAT,
            usage_reinforcement.AUSGANG_EMBED_FEHLER,
            usage_reinforcement.AUSGANG_VEKTOR_LEER,
            usage_reinforcement.AUSGANG_DB_FEHLER,
        ]
        self.assertEqual(6, len(set(marken)))

    def test_der_lauf_reicht_massstab_und_ausgang_durch(self) -> None:
        """Was die Pruefung ergab, muss die Buchfuehrung auch weitergeben."""
        with patch(f"{MODUL}.model_service", _embed([0.1] * 768)), \
             patch(f"{MODUL}.psycopg2.connect") as verbindung:
            verbindung.return_value.cursor.return_value.fetchall.return_value = [
                (11, 0.5412),
            ]
            ergebnis = usage_reinforcement.reinforce_used(
                POSTGRES_URL, "eine Antwort", [11],
            )
        self.assertEqual(0, ergebnis["verwendet"])
        self.assertEqual({11: 0.5412}, ergebnis["naehen_alle"])
        self.assertEqual(0.5412, ergebnis["knappster_verworfener"])
        self.assertEqual(VERWENDUNG_NAEHE_SCHWELLE, ergebnis["schwelle"])
        self.assertEqual(VERWENDUNG_MAX_JE_TURN, ergebnis["deckel"])
        self.assertEqual(
            usage_reinforcement.AUSGANG_GERECHNET, ergebnis["ausgang"],
            "Ein Nullbefund aus gerechneter Naehe muss von einem Ausfall "
            "unterscheidbar bleiben",
        )


class DieProtokollzeileTraegtDieEntscheidungTest(unittest.TestCase):
    """Der Dispatcher schreibt die Groessen, nicht nur das Ergebnis."""

    ZUSTAND: dict = {
        "turn_id": "t-1", "user_id": "meister", "character_id": "nova",
        "antwort_inhalt": "eine Antwort",
        "lzg_resonanz": {"erinnerungen": [{"knoten_id": 11}]},
    }

    def test_die_zeile_traegt_schwelle_ausgang_und_alle_naehen(self) -> None:
        """Ohne diese drei ist `verwendet: 0` stumm (Fund 04.09.2026)."""
        from graph.nodes.dispatcher import _verwendung_verstaerken

        ergebnis: dict = {
            "geprueft": 3, "verwendet": 0, "verstaerkt": 0, "naehen": [],
            "naehen_alle": {11: 0.5412, 12: 0.12, 13: 0.09},
            "knappster_verworfener": 0.5412,
            "schwelle": 0.55, "deckel": 3,
            "ausgang": usage_reinforcement.AUSGANG_GERECHNET, "error": None,
        }
        with patch(f"{AGENT}.usage_reinforcement.reinforce_used",
                   return_value=ergebnis), \
             patch(f"{AGENT}.log_db_write") as geschrieben:
            _verwendung_verstaerken(dict(self.ZUSTAND), POSTGRES_URL)

        self.assertTrue(geschrieben.called, "Keine Protokollzeile geschrieben")
        inhalt: dict = geschrieben.call_args.kwargs["inhalt"]
        for feld in ("schwelle", "deckel", "ausgang", "naehen_alle",
                     "knappster_verworfener"):
            self.assertIn(
                feld, inhalt,
                f"`{feld}` fehlt — die Zeile kann den Nullbefund nicht erklaeren",
            )
        self.assertEqual(0.5412, inhalt["knappster_verworfener"])
        self.assertEqual(0.55, inhalt["schwelle"])


if __name__ == "__main__":
    unittest.main()
