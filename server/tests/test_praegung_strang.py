"""Zeugen ueber den Strang: findet ein Faden seine Nachbarn oder gruendet er?

Ziel: Faeden, die thematisch beieinanderliegen, tragen dieselbe Strangkennung —
und ein Faden, der allein steht, gruendet einen Strang, statt keinen zu haben.

Konzept `novaberg-thinking-faszination_k.md` §7.7. Der Strang ist die groessere
Runde auf der Themenlandkarte; die drei Achsen (Ladung, Richtung, Valenz) und
die Staerke stehen **nicht** in dieser Scheibe — sie brauchen Gewichte, die
nirgends beziffert sind, und eine Annaeherungs-Tabelle, die das Konzept selbst
als gesetzt und ungemessen fuehrt (§13).

**Diese Zeugen fassen den Produktivbestand nicht an.** `strang_zuordnen`
schreibt in zwei Tabellen, und `faeden_ohne_strang_zuordnen` laeuft ueber
**alle** Paare — dieselbe Bauart wie `alle_faeden_nachfuehren` und damit
derselbe Kandidat fuer den Fehler, der am 01.09.2026 die Suite zum Schreiber im
laufenden System machte. Beide laufen hier gegen eine nachgebildete Verbindung.

Zwei Ebenen, und die zweite ist die, die in diesem Projekt dreimal in zwei Tagen
gefehlt hat:

  1. **Die Zuordnung** — Beitritt, Gruendung, Zentroid, die Ausfaelle.
  2. **Die Verdrahtung** — ruft `faden_anlegen` sie, und ruft der Tageslauf den
     Nachzug? Genau diese Frage stellte bei der Faltung kein Zeuge, und die
     Funktion stand einen Tag ohne Aufrufer (`20_TESTS/verdrahtung.md`, `A17`).

Die Zusicherungen:

  1. **Ueber der Schwelle tritt der Faden bei** — und die Strangzeile zaehlt mit.
  2. **Unter der Schwelle gruendet er**, statt ohne Strang zu bleiben.
  3. **Das Zentroid wird fortgeschrieben**, nicht ersetzt: `(alt·n + neu)/(n+1)`.
  4. **Ohne Embedding kein Strang** — der Faden bleibt fuer den Nachzug offen.
  5. **Ein Faden mit Strang wird nicht umgehaengt.**
  6. **Der Nachzug geht in der Reihenfolge der Zeit** — sonst ergibt derselbe
     Bestand bei jedem Lauf ein anderes Ergebnis, und keines davon ist falsch.
  7. **Der Nachzug meldet zwei Zahlen.** `zugeordnet` allein waere von einem
     Abbruch nicht zu unterscheiden.
  8. **`faden_anlegen` ruft die Zuordnung.**
  9. **Der Tageslauf ruft den Nachzug.**

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from config import PRAEGUNG_STRANG_NAEHE
from memory.praegung import (
    _vektor_lesen,
    _vektor_schreiben,
    faeden_ohne_strang_zuordnen,
    strang_zuordnen,
)

AGENT_MODUL: str = "agents.synapsen_decay.agent"
JETZT: datetime = datetime(2026, 9, 1, 19, 0, tzinfo=timezone.utc)

#: Kurze Vektoren statt 768 Stellen: Geprueft wird die Rechnung, nicht die
#: Laenge — und ein nachrechenbarer Mittelwert ist mit drei Zahlen ablesbar.
FADEN_VEKTOR:  list[float] = [1.0, 0.0, 0.0]
STRANG_ZENTROID: list[float] = [0.8, 0.6, 0.0]


class _Cursor:
    """Ein Cursor, der eine vorgegebene Folge von Antworten liefert.

    Er merkt sich jedes `execute` samt Parametern — daran ist ablesbar, **was**
    die Funktion geschrieben hat, und nicht nur, dass sie etwas geschrieben hat.
    """

    def __init__(self, antworten: list) -> None:
        self.antworten: list = list(antworten)
        self.befehle:   list[tuple[str, tuple]] = []

    def execute(self, sql: str, args: tuple = ()) -> None:
        self.befehle.append((" ".join(sql.split()), args))

    def fetchone(self):
        return self.antworten.pop(0) if self.antworten else None

    def fetchall(self):
        return self.antworten.pop(0) if self.antworten else []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _mit_cursor(cursor: _Cursor):
    """Nachgebildete Verbindung — die echte Datenbank bleibt unberuehrt."""
    verbindung = MagicMock()
    verbindung.return_value.__enter__.return_value.cursor.return_value = cursor
    return patch("memory.praegung.psycopg2.connect", verbindung)


def _faden_zeile(embedding: list[float] | None = None,
                 strang_id: int | None = None) -> tuple:
    return (
        "meister", "nova", "assistant",
        _vektor_schreiben(embedding) if embedding else None,
        JETZT, strang_id,
    )


class DerFadenFindetSeinenStrangTest(unittest.TestCase):
    """Ueber der Schwelle Beitritt, darunter Gruendung — und nichts dazwischen."""

    def test_ueber_der_schwelle_tritt_der_faden_bei(self) -> None:
        cursor = _Cursor([
            _faden_zeile(FADEN_VEKTOR),
            (7, _vektor_schreiben(STRANG_ZENTROID), 3, PRAEGUNG_STRANG_NAEHE + 0.05),
        ])
        with _mit_cursor(cursor):
            self.assertEqual(strang_zuordnen("postgresql://nachgebildet", 42), 7)

        gesetzt = [b for b in cursor.befehle if "SET strang_id" in b[0]]
        self.assertEqual(len(gesetzt), 1, "Der Faden traegt die Strangkennung nicht")
        self.assertEqual(gesetzt[0][1], (7, 42))

        gezaehlt = [b for b in cursor.befehle if "faden_zahl = faden_zahl + 1" in b[0]]
        self.assertEqual(
            len(gezaehlt), 1,
            "Die Strangzeile zaehlt den Beitritt nicht mit — der Divisor des "
            "Zentroids laeuft dann aus dem Tritt",
        )

    def test_unter_der_schwelle_gruendet_der_faden(self) -> None:
        cursor = _Cursor([
            _faden_zeile(FADEN_VEKTOR),
            (7, _vektor_schreiben(STRANG_ZENTROID), 3, PRAEGUNG_STRANG_NAEHE - 0.01),
            (99,),
        ])
        with _mit_cursor(cursor):
            self.assertEqual(strang_zuordnen("postgresql://nachgebildet", 42), 99)

        gegruendet = [b for b in cursor.befehle if "INSERT INTO praegung_strang" in b[0]]
        self.assertEqual(
            len(gegruendet), 1,
            "Ein Faden ohne nahen Strang bleibt ohne Strang, statt einen zu "
            "gruenden — ein Bestand aus lauter Einzelfaeden sieht dann aus wie "
            "ein Ausfall der Zuordnung",
        )

    def test_ohne_einen_einzigen_strang_gruendet_der_erste_faden(self) -> None:
        cursor = _Cursor([_faden_zeile(FADEN_VEKTOR), None, (1,)])
        with _mit_cursor(cursor):
            self.assertEqual(strang_zuordnen("postgresql://nachgebildet", 42), 1)


class DasZentroidWaechstMitTest(unittest.TestCase):
    """Es wird fortgeschrieben, nicht ersetzt — sonst waere es der letzte Faden."""

    def test_das_zentroid_ist_das_laufende_mittel(self) -> None:
        cursor = _Cursor([
            _faden_zeile(FADEN_VEKTOR),
            (7, _vektor_schreiben(STRANG_ZENTROID), 3, PRAEGUNG_STRANG_NAEHE + 0.05),
        ])
        with _mit_cursor(cursor):
            strang_zuordnen("postgresql://nachgebildet", 42)

        geschrieben = [b for b in cursor.befehle if "SET zentroid" in b[0]]
        self.assertEqual(len(geschrieben), 1)
        neu = _vektor_lesen(geschrieben[0][1][0])
        erwartet = [(a * 3 + b) / 4 for a, b in zip(STRANG_ZENTROID, FADEN_VEKTOR, strict=True)]
        for i, (ist, soll) in enumerate(zip(neu, erwartet, strict=True)):
            self.assertAlmostEqual(
                ist, soll, places=6,
                msg=f"Stelle {i}: das Zentroid ist kein laufendes Mittel",
            )

    def test_ein_unbrauchbares_zentroid_laesst_den_faden_offen(self) -> None:
        """Eine falsche Laenge ist ein Fehler, kein Anlass zum Zurechtbiegen."""
        cursor = _Cursor([
            _faden_zeile(FADEN_VEKTOR),
            (7, _vektor_schreiben([0.5, 0.5]), 3, PRAEGUNG_STRANG_NAEHE + 0.05),
        ])
        with _mit_cursor(cursor):
            self.assertIsNone(strang_zuordnen("postgresql://nachgebildet", 42))


class WasKeinenStrangBekommtTest(unittest.TestCase):
    """Zwei Faelle, und beide bleiben wiederholbar statt still."""

    def test_ohne_embedding_kein_strang(self) -> None:
        cursor = _Cursor([_faden_zeile(None)])
        with _mit_cursor(cursor):
            self.assertIsNone(strang_zuordnen("postgresql://nachgebildet", 42))
        self.assertEqual(
            [b for b in cursor.befehle if "INSERT INTO praegung_strang" in b[0]], [],
            "Ein Faden ohne Ort auf der Landkarte hat einen Strang gegruendet",
        )

    def test_ein_zugeordneter_faden_wird_nicht_umgehaengt(self) -> None:
        cursor = _Cursor([_faden_zeile(FADEN_VEKTOR, strang_id=5)])
        with _mit_cursor(cursor):
            self.assertEqual(strang_zuordnen("postgresql://nachgebildet", 42), 5)
        self.assertEqual(
            len(cursor.befehle), 1,
            "Ein Faden mit Strang wurde erneut zugeordnet — der Nachzug wuerde "
            "damit bei jedem Lauf Zentroide verschieben",
        )

    def test_eine_unbrauchbare_kennung_faellt_aus(self) -> None:
        self.assertIsNone(strang_zuordnen("postgresql://nachgebildet", 0))


class DerNachzugIstReproduzierbarTest(unittest.TestCase):
    """Online-Zuordnung ist reihenfolgeabhaengig — die Reihenfolge ist die Zeit."""

    def test_der_nachzug_sortiert_nach_entstehung(self) -> None:
        cursor = _Cursor([[(3,), (1,), (2,)]])
        with _mit_cursor(cursor), \
             patch("memory.praegung.strang_zuordnen", return_value=9) as zuordnen:
            zugeordnet, gesamt = faeden_ohne_strang_zuordnen("postgresql://nachgebildet")

        self.assertIn(
            "ORDER BY entstanden_am, id", cursor.befehle[0][0],
            "Ohne Sortierung ergibt derselbe Bestand bei jedem Lauf ein anderes "
            "Ergebnis, und keines davon ist falsch",
        )
        self.assertEqual([a.args[1] for a in zuordnen.call_args_list], [3, 1, 2])
        self.assertEqual((zugeordnet, gesamt), (3, 3))

    def test_die_vollstaendigkeit_steht_als_zwei_zahlen(self) -> None:
        cursor = _Cursor([[(1,), (2,), (3,)]])
        with _mit_cursor(cursor), \
             patch("memory.praegung.strang_zuordnen", side_effect=[9, None, 9]):
            self.assertEqual(
                faeden_ohne_strang_zuordnen("postgresql://nachgebildet"), (2, 3),
                "Ohne die zweite Zahl waere ein halber Lauf von einem ganzen "
                "nicht zu unterscheiden",
            )

    def test_faeden_ohne_embedding_stehen_nicht_im_lauf(self) -> None:
        cursor = _Cursor([[]])
        with _mit_cursor(cursor):
            faeden_ohne_strang_zuordnen("postgresql://nachgebildet")
        self.assertIn("embedding IS NOT NULL", cursor.befehle[0][0])


class DieVerdrahtungTest(unittest.TestCase):
    """Gebaut, bezeugt und ungerufen war in zwei Tagen dreimal der Befund."""

    def test_faden_anlegen_ruft_die_zuordnung(self) -> None:
        cursor = _Cursor([(42,)])
        with _mit_cursor(cursor), \
             patch("memory.praegung.strang_zuordnen") as zuordnen:
            from memory.praegung import faden_anlegen
            faden_anlegen(
                "postgresql://nachgebildet",
                user_id="meister", character_id="nova",
                emotion="freude", ausschlag_eingang=0.8,
                embedding_str=_vektor_schreiben(FADEN_VEKTOR),
            )
        zuordnen.assert_called_once()
        self.assertEqual(zuordnen.call_args.args[1], 42)

    def test_der_tageslauf_ruft_den_nachzug(self) -> None:
        import importlib
        agent_modul = importlib.import_module(AGENT_MODUL)
        quelle: str = agent_modul.__doc__ or ""
        self.assertIn(
            "faeden_ohne_strang_zuordnen", quelle,
            "Der Tageslauf nennt den Nachzug nicht in seinem Ablauf",
        )
        import inspect
        koerper: str = inspect.getsource(agent_modul.SynapsenDecayAgent.invoke)
        self.assertIn(
            "faeden_ohne_strang_zuordnen", koerper,
            "Der Nachzug ist gebaut und wird von nichts gerufen — derselbe "
            "Defekt, dessen Behebung er ist",
        )


if __name__ == "__main__":
    unittest.main()
