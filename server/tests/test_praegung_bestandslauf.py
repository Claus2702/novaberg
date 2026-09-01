"""Zeugen ueber den Bestandslauf: altert der Wert auch ohne Beruehrung?

Ziel: Ein Faden, den seit Wochen niemand angesprochen hat, steht in der Spalte
nicht mehr so hoch wie am Tag seiner letzten Auffrischung.

**Diese Zeugen fassen den Produktivbestand nicht an.** `alle_faeden_nachfuehren`
laeuft ueber **alle** Paare — das ist ihr Zweck und macht sie zum gefaehrlichsten
Kandidaten fuer einen Zeugen, der im laufenden System schreibt. `[gemessen]`
01.09.2026: Die erste Fassung dieser Datei tat genau das und faltete bei jedem
Suitenlauf die vier Faeden des Messpaars mit. Der globale Weg wird deshalb gegen
eine **nachgebildete** Verbindung gefahren; die echte Datenbank sehen nur die
Zeugen mit ausdruecklicher Faden-Kennung in `test_praegung_nachfuehrung.py`
(`20_TESTS`: wer einem Knoten einen Schreibvorgang gibt, macht die Suite zum
Schreiber im laufenden System).

**Der Anlass steht im Bestand.** Seit dem 01.09.2026 fuehrt
`ausschlag_aktuell_nachfuehren` den Wert nach, **wenn eine Beruehrung
entsteht**. Der Verfall **zwischen** zwei Beruehrungen hat kein Ereignis, an dem
er haengen koennte — `[gemessen]` am selben Tag: Faden 353 trug eine Beruehrung
und stand danach unveraendert auf `ausschlag_absolut`
(`FALTUNG-OHNE-PERIODISCHEN-LAUF`).

Zwei Ebenen, und die zweite ist die, die gefehlt hat:

  1. **Die Rechnung ueber den Bestand** — laeuft sie vollstaendig, und sagt sie
     es, wenn nicht?
  2. **Die Verdrahtung** — ruft der Tageslauf sie ueberhaupt? Genau diese Frage
     stellte bei der Faltung selbst kein Zeuge, und die Funktion stand einen Tag
     lang ohne Aufrufer (`20_TESTS/verdrahtung.md`).

Die Zusicherungen:

  1. **Der Lauf gibt jeden Faden an die Rechnung** — auch den nie beruehrten.
  2. **Er meldet Vollstaendigkeit als zwei Zahlen.** `gefaltet` allein waere von
     einem halben Lauf nicht zu unterscheiden.
  3. **Ein halber Lauf meldet sich** statt Erfolg zu melden.
  4. **Ein kleiner Stapel laesst keinen Abschnitt aus.**
  5. **Ein leerer Bestand ist kein Fehler** — er ist der Regelfall am Anfang.
  6. **Eine unbrauchbare Stapelgroesse faellt aus und meldet**, statt in eine
     Endlosschleife zu gehen.
  7. **Der Tageslauf ruft ihn.** Ohne diesen Zeugen bliebe der Bestandslauf
     gebaut, bezeugt und ungerufen — derselbe Defekt, dessen Behebung er ist.
  8. **Sein Fehler faerbt den Tageslauf rot**, statt still zu bleiben.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import unittest
from unittest.mock import patch

from memory.praegung import alle_faeden_nachfuehren

AGENT_MODUL: str = "agents.synapsen_decay.agent"


class BestandslaufTest(unittest.TestCase):
    """Die Faltung ueber alle Faeden — gegen eine nachgebildete Verbindung.

    Geprueft wird, **welche Kennungen** der Lauf an die Rechnung gibt und wie er
    die beiden Zahlen bildet. Die Rechnung selbst hat ihre Zeugen in
    `test_praegung_faltung.py`, ihr Schreibweg in `test_praegung_nachfuehrung.py`.
    """

    IDS: list[int] = [11, 22, 33, 44, 55]

    def _lauf(self, ids: list[int], stapel: int = 500,
              je_aufruf: int | None = None) -> tuple[dict, list[list[int]]]:
        """Faehrt den Bestandslauf mit vorgegebenen Kennungen."""
        stapel_folge: list[list[int]] = []

        def _nachfuehren(_url: str, teil: list[int],
                         _jetzt: object = None) -> int:
            stapel_folge.append(list(teil))
            return len(teil) if je_aufruf is None else je_aufruf

        with patch("memory.praegung.psycopg2.connect") as verbindung, \
             patch("memory.praegung.ausschlag_aktuell_nachfuehren", _nachfuehren):
            zeiger = verbindung.return_value.__enter__.return_value.cursor
            zeiger.return_value.__enter__.return_value.fetchall.return_value = [
                (i,) for i in ids
            ]
            ergebnis = alle_faeden_nachfuehren("postgresql://nachgebildet", None, stapel)
        return ergebnis, stapel_folge

    def test_der_lauf_erreicht_jeden_faden(self) -> None:
        ergebnis, stapel = self._lauf(self.IDS)
        self.assertEqual(
            [i for teil in stapel for i in teil], self.IDS,
            "Der Lauf hat nicht jeden Faden an die Rechnung gegeben — ein Faden, "
            "den niemand anspricht, altert dann nie",
        )
        self.assertIsNone(ergebnis["error"])

    def test_die_vollstaendigkeit_steht_als_zwei_zahlen(self) -> None:
        ergebnis, _ = self._lauf(self.IDS)
        self.assertEqual(ergebnis["gefaltet"], len(self.IDS))
        self.assertEqual(
            ergebnis["gesamt"], len(self.IDS),
            "Ohne die zweite Zahl waere ein halber Lauf von einem ganzen nicht "
            "zu unterscheiden",
        )

    def test_ein_halber_lauf_meldet_sich(self) -> None:
        ergebnis, _ = self._lauf(self.IDS, 500, je_aufruf=2)
        self.assertEqual(ergebnis["gefaltet"], 2)
        self.assertEqual(ergebnis["gesamt"], 5)
        self.assertEqual(
            ergebnis["error"], "unvollstaendig",
            "Ein Lauf ueber zwei von fuenf Faeden meldet Erfolg — der Aufrufer "
            "haelt den Bestand fuer nachgefuehrt",
        )

    def test_ein_kleiner_stapel_erreicht_trotzdem_alles(self) -> None:
        ergebnis, stapel = self._lauf(self.IDS, stapel=2)
        self.assertEqual(
            stapel, [[11, 22], [33, 44], [55]],
            "Die Schleife ueber die Stapel laesst einen Abschnitt aus",
        )
        self.assertEqual(ergebnis["gefaltet"], 5)

    def test_unbrauchbare_stapelgroesse_faellt_aus_und_meldet(self) -> None:
        ergebnis, stapel = self._lauf(self.IDS, stapel=0)
        self.assertEqual(ergebnis["gefaltet"], 0)
        self.assertEqual(stapel, [], "Die Rechnung lief trotz Stapelgroesse 0")
        self.assertIsNotNone(
            ergebnis["error"],
            "Eine Stapelgroesse von 0 laeuft stillschweigend durch — der "
            "Aufrufer haelt den Lauf fuer erledigt",
        )


class LeererBestandTest(unittest.TestCase):
    """Ein Bestand ohne Faeden ist der Regelfall am Anfang, kein Fehler."""

    def test_leerer_bestand_ist_kein_fehler(self) -> None:
        with patch("memory.praegung.psycopg2.connect") as verbindung:
            zeiger = verbindung.return_value.__enter__.return_value.cursor
            zeiger.return_value.__enter__.return_value.fetchall.return_value = []
            ergebnis = alle_faeden_nachfuehren("postgresql://nachgebildet")
        self.assertEqual(ergebnis, {"gefaltet": 0, "gesamt": 0, "error": None})


class TageslaufRuftDenBestandslaufTest(unittest.TestCase):
    """Die Verdrahtung: ohne sie bleibt der Lauf gebaut und ungerufen.

    **Jeder Schritt des Tageslaufs wird ersetzt, auch die, um die es hier nicht
    geht.** `invoke` ruft sie alle; was nicht ersetzt ist, laeuft gegen
    `POSTGRES_URL`. `[gemessen]` 01.09.2026: Der am selben Tag hinzugekommene
    fuenfte Schritt stand hier nicht — und legte bei jedem Suitenlauf einen
    Strang ueber die vier Faeden des Messpaars an. Der Zeuge war nicht
    geaendert worden; er wurde gefaehrlich, weil der Gegenstand wuchs
    (`20_TESTS/neuer-seiteneffekt-alte-zeugen.md`, dritter Fall in fuenf Tagen).

    **Wer den Tageslauf erweitert, erweitert diese Liste** — sonst schreibt der
    naechste Schritt hier still weiter.

    `[2×]` — 01.09.2026, derselbe Tag: Der **sechste** Schritt (die
    Strang-Richtungen) kam dazu und stand wieder nicht in der Liste. Er lief
    harmlos leer, weil `patch(db_manager)` einen `MagicMock` liefert und dessen
    `__iter__` leer ist — **das ist Zufall und keine Absicht.** Ein Schritt, der
    seine Zeilen anders holt, schriebe an derselben Stelle. Er steht jetzt
    ausdruecklich in der Liste.
    """

    def _lauf(self, faltung: dict) -> tuple[object, object]:
        from agents.base import AgentState
        from agents.synapsen_decay.agent import SynapsenDecayAgent

        leer: dict = {"error": None, "total_processed": 0, "deactivated_count": 0,
                      "deleted_count": 0, "verarbeitet": 0, "deaktiviert": 0}
        with patch(f"{AGENT_MODUL}.SYNAPSEN_DECAY_AKTIV", True), \
             patch(f"{AGENT_MODUL}.lzg_knoten.run_node_decay", return_value=leer), \
             patch(f"{AGENT_MODUL}.pipeline_log.delete_expired_entries", return_value=leer), \
             patch(f"{AGENT_MODUL}.ShadowAuftragRepository.verfall_lauf", return_value=leer), \
             patch(f"{AGENT_MODUL}.db_manager"), \
             patch(f"{AGENT_MODUL}.praegung.alle_faeden_nachfuehren",
                   return_value=faltung) as gerufen, \
             patch(f"{AGENT_MODUL}.praegung.faeden_ohne_strang_zuordnen",
                   return_value=(0, 0)), \
             patch.object(SynapsenDecayAgent, "_richtungen_protokollieren",
                          return_value=0):
            zustand: AgentState = SynapsenDecayAgent().invoke(
                AgentState(auftrag="", kontext={}),
            )
        return zustand, gerufen

    def test_der_tageslauf_ruft_den_bestandslauf(self) -> None:
        zustand, gerufen = self._lauf(
            {"gefaltet": 7, "gesamt": 7, "error": None},
        )
        gerufen.assert_called_once()
        self.assertEqual(
            zustand["ergebnis"]["praegung_faltung"]["gefaltet"], 7,
            "Der Tageslauf ruft den Bestandslauf nicht oder verwirft sein "
            "Ergebnis — der Verfall zwischen zwei Beruehrungen bliebe liegen",
        )
        self.assertEqual(zustand["status"], "abgeschlossen")

    def test_ein_unvollstaendiger_lauf_faerbt_rot(self) -> None:
        zustand, _ = self._lauf(
            {"gefaltet": 3, "gesamt": 7, "error": "unvollstaendig"},
        )
        self.assertEqual(
            zustand["status"], "fehler",
            "Ein Bestandslauf ueber drei von sieben Faeden faellt still durch — "
            "dann ist ein halber Lauf von einem ganzen nicht zu unterscheiden",
        )


if __name__ == "__main__":
    unittest.main()
