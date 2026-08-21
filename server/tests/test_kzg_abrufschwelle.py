"""Zeugen fuer die Abrufschwelle des Kurzzeitgedaechtnisses.

Ziel: Zu einer Frage, zu der das Kurzzeitgedaechtnis nichts Passendes haelt,
liefert es **nichts**. Ein Eintrag unterhalb von `KZG_RETRIEVAL_SCHWELLE`
erreicht den Kontext nicht, auch wenn ein Platz frei waere.

Hintergrund: Bis zum 21.08.2026 stand die Schwelle auf 0.40 — **unter** dem
Boden des Vektorraums. Gemessen an 2665 Eintraegen des Bestandes erreicht der
schlechteste Eintrag gegen eine beliebige Frage 0.48 bis 0.54; zehn Fragen zu
nie besprochenen Gegenstaenden bekamen alle zehn die vollen `top_k`. Die
Schwelle war nicht zu niedrig, sie war wirkungslos. Die Reihe zur heutigen
Zahl steht an der Konstante in `config.py`.

**Die Erwartungswerte sind Literale und werden nicht aus der Konstante
gerechnet.** Ein Test, der seine Grenze aus derselben Zahl bildet, gegen die
der Code prueft, liefe auf beiden Seiten des Vergleichs auf dieselbe Eingabe
zurueck. Steht die Konstante eines Tages woanders, wird dieser Zeuge rot —
und das ist seine Aufgabe.

**Die Attrappe ist gegen den echten Erzeuger gehalten** (21.08.2026): Ein
`Document` aus RediSearch traegt seine Felder als **Zeichenketten**, auch die
Zahlen — `score='0.457654714584'`, `salienz='1'`, `arousal='0.5'`,
`erstellt_am='1785188442.29'`. Eine Attrappe mit float-Feldern koennte den
Fall nicht bilden, an dem der Lesepfad scheitert.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from config import KZG_RETRIEVAL_SCHWELLE
from memory.kzg import kzg_entries_retrieve

# Die Umrechnung des Lesepfads: similarity = 1 - score/2, also score = 2(1-s).
# Von Hand gerechnet, damit der Zeuge nicht dieselbe Formel benutzt wie der
# Pruefling: s=0.72 -> 0.56 · s=0.71 -> 0.58 · s=0.90 -> 0.20 · s=0.60 -> 0.80
SCORE_AUF_SCHWELLE:  str = "0.56"
SCORE_KNAPP_DRUNTER: str = "0.58"
SCORE_DEUTLICH_UEBER: str = "0.20"
SCORE_ALTE_SCHWELLE: str = "0.80"


def _doc(key: str, score: str, inhalt: str) -> SimpleNamespace:
    """Ein Treffer, wie RediSearch ihn liefert — alle Felder als Zeichenkette."""
    return SimpleNamespace(
        id=key, score=score, inhalt=inhalt,
        themen="Gravitationswellen", salienz="1", dimension="kognition",
        beobachter="user", erstellt_am="1785188442.29", arousal="0.5",
        emotion="neugier", modus="sachlich", gedaechtnistyp="episodisch",
        emotions_vektor="",
    )


def _client(docs: list) -> MagicMock:
    """Eine Redis-Attrappe, deren Index genau diese Treffer liefert."""
    ergebnis = SimpleNamespace(total=len(docs), docs=docs)
    klient = MagicMock()
    klient.ft.return_value.search.return_value = ergebnis
    return klient


class AbrufschwelleTest(unittest.TestCase):
    """Was unter der Schwelle liegt, erreicht den Kontext nicht."""

    def test_die_schwelle_steht_auf_dem_gemessenen_wert(self) -> None:
        """Der Wert ist gemessen, nicht geraten — er steht als Literal daneben."""
        self.assertAlmostEqual(KZG_RETRIEVAL_SCHWELLE, 0.72, places=4)

    def test_ein_eintrag_knapp_unter_der_schwelle_wird_nicht_geliefert(self) -> None:
        """Ein freier Platz ist kein Grund, einen schwachen Treffer auszugeben."""
        docs = [_doc("kzg:m:n:1", SCORE_KNAPP_DRUNTER, "knapp daneben")]
        self.assertEqual([], kzg_entries_retrieve(_client(docs), "m", "n", [0.0] * 768))

    def test_ein_eintrag_auf_der_schwelle_wird_geliefert(self) -> None:
        """Wer genau die Grenze trifft, die das Tor meint, geht hindurch."""
        docs = [_doc("kzg:m:n:2", SCORE_AUF_SCHWELLE, "genau auf der Grenze")]
        treffer = kzg_entries_retrieve(_client(docs), "m", "n", [0.0] * 768)
        self.assertEqual(1, len(treffer))
        self.assertEqual("genau auf der Grenze", treffer[0]["inhalt"])

    def test_der_alte_wert_reicht_heute_nicht_mehr(self) -> None:
        """Ein Treffer bei Similarity 0.60 kam unter 0.40 durch — heute nicht.

        Das ist die Gegenprobe zur Aenderung vom 21.08.2026: Genau dieser
        Eintrag ist der Unterschied zwischen der alten und der neuen Schwelle.
        """
        docs = [_doc("kzg:m:n:3", SCORE_ALTE_SCHWELLE, "unter der alten Schwelle durchgekommen")]
        self.assertEqual([], kzg_entries_retrieve(_client(docs), "m", "n", [0.0] * 768))

    def test_das_kurzzeitgedaechtnis_darf_schweigen(self) -> None:
        """Eine leere Rueckgabe ist ein Ergebnis und kein Ausfall.

        Bis zum 21.08.2026 konnte dieser Fall nicht eintreten: Die Schwelle
        lag unter dem Boden des Raums, und die Plaetze waren immer voll.
        """
        docs = [
            _doc("kzg:m:n:4", SCORE_KNAPP_DRUNTER, "nichts davon passt"),
            _doc("kzg:m:n:5", SCORE_ALTE_SCHWELLE, "das auch nicht"),
        ]
        self.assertEqual([], kzg_entries_retrieve(_client(docs), "m", "n", [0.0] * 768))

    def test_starke_treffer_bleiben_unberuehrt(self) -> None:
        """Die Schwelle sperrt aus, sie sortiert nicht um."""
        docs = [
            _doc("kzg:m:n:6", SCORE_DEUTLICH_UEBER, "klar einschlaegig"),
            _doc("kzg:m:n:7", SCORE_KNAPP_DRUNTER, "knapp daneben"),
            _doc("kzg:m:n:8", SCORE_AUF_SCHWELLE, "auf der Grenze"),
        ]
        treffer = kzg_entries_retrieve(_client(docs), "m", "n", [0.0] * 768)
        self.assertEqual(
            ["klar einschlaegig", "auf der Grenze"],
            [e["inhalt"] for e in treffer],
        )


if __name__ == "__main__":
    unittest.main()
