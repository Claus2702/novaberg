"""Tests fuer die drei Ebenen des Prompt-Ladens (`prompt_loader.py`).

Ziel: Ein Prompt-Block, der fuer das antwortende Modell gebaut ist, wird
geladen — auch wenn der aktive Connector anders heisst.

Der Anlass ist gemessen: Zwei der drei Connectoren fahren im Gespraech
**dasselbe** GPU-Modell. Sieben fuer Gemma4 gebaute Bloecke lagen unter
dem Connector `qwen36` still, waehrend Gemma4 antwortete — im Betriebslog
als *"Keine Overrides fuer Connector 'qwen36'"*.

Die Zusicherungen:

  1. **Die Modellebene traegt.** Ein Block unter dem Modellnamen erreicht
     den Bestand, ohne dass der Connector so heisst.
  2. **Der Connector schlaegt das Modell.** Er ist der engere Schluessel:
     zwei Connectoren teilen sich ein Modell, kein Modell einen Connector.
  3. **Die Reihenfolge ist die Aussage** — default, Modell, Connector.
  4. **Ohne Default gibt es keinen Bestand**, und das wird gemeldet statt
     als leere Menge zurueckgegeben.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from prompt_loader import prompt_laden


class EbenenTest(unittest.TestCase):
    """Drei Verzeichnisse, und wer wen ueberschreibt."""

    def setUp(self) -> None:
        """Baut ein Prompt-Verzeichnis mit allen drei Ebenen."""
        self.wurzel: Path = Path(tempfile.mkdtemp(prefix="prompts_"))
        for ebene, texte in (
            ("default", {"a.rules": "default-a", "b.rules": "default-b",
                         "c.rules": "default-c"}),
            ("gemma4-gpu", {"b.rules": "modell-b", "c.rules": "modell-c"}),
            ("qwen36", {"c.rules": "connector-c"}),
        ):
            (self.wurzel / ebene).mkdir()
            for name, text in texte.items():
                (self.wurzel / ebene / f"{name}.txt").write_text(text, encoding="utf-8")

    def tearDown(self) -> None:
        """Raeumt das Verzeichnis ab."""
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _laden(self, connector: str = "qwen36", modell: str = "gemma4-gpu") -> dict:
        """Ruft den echten Lader über die vorbereitete Wurzel."""
        return prompt_laden(connector, str(self.wurzel), modell)

    def test_das_modell_ueberschreibt_den_default(self) -> None:
        """Der Fall, für den die Ebene gebaut wurde.

        `b.rules` steht nur unter dem Modell — der Connector heißt anders,
        und vor dem 23.08.2026 wäre der Block nie geladen worden.
        """
        self.assertEqual(self._laden()["b.rules"], "modell-b")

    def test_der_connector_schlaegt_das_modell(self) -> None:
        """Der engere Schlüssel gewinnt.

        Zwei Connectoren teilen sich ein Modell, kein Modell einen
        Connector: Wer nach Zusammenstellung schlüsselt, meint mehr.
        """
        self.assertEqual(self._laden()["c.rules"], "connector-c")

    def test_alle_drei_ebenen_in_einem_bestand(self) -> None:
        """Die Reihenfolge als **eine** Zusicherung, nicht als drei.

        Die Gegenprobe hat gezeigt, warum: Nimmt man die Modellebene
        heraus, fällt nur ein einziger der übrigen Zeugen — die anderen
        erwarten den Default und bekommen ihn dann auch. Ein Zeuge, der
        alle drei Ebenen **gleichzeitig** festhält, unterscheidet
        „Reihenfolge stimmt" von „jede Ebene für sich tut etwas".
        """
        self.assertEqual(
            self._laden(),
            {"a.rules": "default-a", "b.rules": "modell-b", "c.rules": "connector-c"},
        )

    def test_unberuehrtes_bleibt_default(self) -> None:
        """Die Gegenprobe — die Ebenen greifen nicht über ihre Blöcke hinaus."""
        self.assertEqual(self._laden()["a.rules"], "default-a")

    def test_ohne_modellebene_gilt_der_default(self) -> None:
        """Ein leerer Modellname überspringt die Ebene, statt zu raten."""
        self.assertEqual(self._laden(modell="")["b.rules"], "default-b")

    def test_ein_modellname_mit_schraegstrich_findet_sein_verzeichnis(self) -> None:
        """Ein Fernmodell nennt den Anbieter mit: `anbieter/modell-0731`.

        **Unveraendert eingesetzt ergaebe das ein verschachteltes
        Verzeichnis**, und das Zwischenglied waere eine Ebene, die niemand
        nachschlaegt — genau das, was `test_jedes_verzeichnis_ist_erreichbar`
        als totes Material meldet. Der Name wird deshalb flach gemacht.
        """
        (self.wurzel / "anbieter_modell-0731").mkdir()
        (self.wurzel / "anbieter_modell-0731" / "b.rules.txt").write_text(
            "fern-b", encoding="utf-8",
        )

        geladen = self._laden(modell="anbieter/modell-0731")

        self.assertEqual(geladen["b.rules"], "fern-b")
        self.assertFalse(
            (self.wurzel / "anbieter").exists(),
            "der Lader hat ein Zwischenverzeichnis erwartet statt eines flachen",
        )

    def test_ein_unbekanntes_modell_ist_kein_fehler(self) -> None:
        """Ein Modell ohne eigenes Verzeichnis lässt den Bestand unberührt."""
        bestand: dict = self._laden(connector="mistral", modell="gibtsnicht")
        self.assertEqual(bestand["b.rules"], "default-b")
        self.assertEqual(len(bestand), 3)

    def test_ohne_default_gibt_es_keinen_bestand_und_eine_meldung(self) -> None:
        """Kein stiller Leerfall: Jeder Knoten liefe sonst in einen KeyError."""
        shutil.rmtree(self.wurzel / "default")
        with self.assertLogs("ki_server.prompts", "ERROR"):
            self.assertEqual(self._laden(), {})


class BestandTest(unittest.TestCase):
    """Der echte Bestand — die Zeugen oben stellen ihre Eingabe selbst her."""

    def test_die_ueberschreibenden_bloecke_haben_ihren_default(self) -> None:
        """Ein Override ohne Default ist ein Block, den niemand kennt.

        Er würde nur unter einem Modell existieren und wäre unter jedem
        anderen ein `KeyError` — sichtbar erst im Betrieb, und nur dort.
        """
        prompts: Path = Path(__file__).resolve().parent.parent / "prompts"
        default: set[str] = {p.name for p in (prompts / "default").glob("*.txt")}

        for ebene in sorted(prompts.iterdir()):
            if not ebene.is_dir() or ebene.name == "default":
                continue
            ohne: set[str] = {p.name for p in ebene.glob("*.txt")} - default
            with self.subTest(ebene=ebene.name):
                self.assertEqual(
                    ohne, set(),
                    f"'{ebene.name}' überschreibt Blöcke, die es im Default "
                    f"nicht gibt: {sorted(ohne)}",
                )


    def test_jedes_verzeichnis_ist_erreichbar(self) -> None:
        """Ein Verzeichnis, das keine Ebene je nachschlägt, ist totes Material.

        Der Zeuge darüber prüft **Blocknamen** und hätte deshalb genau den
        Fall grün gelassen, der beim Umbenennen am 23.08.2026 beinahe
        entstanden wäre: ein stehengebliebenes `prompts/gemma4/` neben dem
        neuen `prompts/gemma4-gpu/`. Es hätte unter dem Connector `gemma4`
        weiter Overrides geliefert — aus einem Verzeichnis, das niemand
        mehr pflegt.

        Erreichbar ist ein Name, wenn ihn eine der drei Ebenen nachschlägt:
        `default`, ein Connectorname, oder eines der Modelle eines
        Connectors.
        """
        from config import MODELL_NACH_BACKEND, OLLAMA_CONNECTORS

        erreichbar: set[str] = {"default"} | set(OLLAMA_CONNECTORS)
        for eintrag in OLLAMA_CONNECTORS.values():
            erreichbar |= {
                wert for schluessel, wert in eintrag.items()
                if schluessel.endswith("_model")
            }
        # **Die Connector-Tabelle kennt nur die eigene Maschine.** Seit dem
        # 05.09.2026 kann hinter dem Chat-Worker ein Fernmodell stehen, und
        # seine Modellebene traegt dessen Namen — flach geschrieben, weil ein
        # Schraegstrich sonst ein Zwischenverzeichnis erzeugte.
        erreichbar |= {wert.replace("/", "_") for wert in MODELL_NACH_BACKEND.values()}

        prompts: Path = Path(__file__).resolve().parent.parent / "prompts"
        vorhanden: set[str] = {p.name for p in prompts.iterdir() if p.is_dir()}
        self.assertEqual(
            vorhanden - erreichbar, set(),
            f"Verzeichnisse, die keine Ebene nachschlägt: "
            f"{sorted(vorhanden - erreichbar)} — erreichbar wären "
            f"{sorted(erreichbar)}",
        )


if __name__ == "__main__":
    unittest.main()
