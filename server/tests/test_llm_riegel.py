"""Tests: Jeder Zugriff auf ein LLM haelt den Riegel seiner Ressource.

**Der Riegel schuetzt die Ressource, nicht den Vorgang** (`17_NEBENLAEUFIGKEIT/
riegel-schuetzt-ressource.md`). Bis zum 25.08.2026 hielt ihn genau ein
Aufrufer — `event_consumer.py` um den Lauf des CharakterGraphen —, waehrend
zwei Worker und zwei direkte Aufrufer dieselbe GPU ueber **einen geteilten
`ollama.Client`** ansprachen, also ueber einen geteilten httpx-Verbindungspool.
Gemessen ueber 42 Stunden: **7407 Embed- und 2897 Chat-Aufrufe** aus zwei
getrennt serialisierten Warteschlangen, die voneinander nichts wussten.
Kennung: `GPU-LOCK-SCHUETZT-EINEN-VON-FUENF`.

Die Zusicherungen hier:

  1. **Zwei Threads auf demselben Riegel ueberlappen nicht.** Der Zeuge misst
     die Ueberlappung, statt sie zu behaupten — er zaehlt, wie viele Aufrufe
     gleichzeitig im Client sind.
  2. **Verschiedene Ressourcen blockieren einander nicht.** Ein Riegel je
     Ressource, sonst waere er eine globale Bremse.
  3. **Es gibt keinen Weg am Riegel vorbei.** Ein unbekannter Methodenname
     wird abgewiesen, statt still am Riegel vorbei durchgereicht zu werden.
  4. **Kein Modul importiert den rohen Client.** Eine Strukturpruefung, denn
     Zusicherung 1 bis 3 nuetzen nichts, wenn jemand daneben zugreift.

Kein skipUnless, kein skipIf, kein try/except um Importe.
"""

import threading
import time
import unittest
from pathlib import Path

from services.llm_riegel import GesperrterOllamaClient


class _Zaehlclient:
    """Ein Attrappen-Client, der die gleichzeitige Nutzung mitzaehlt.

    **Er misst die Ueberlappung, statt sie zu behaupten.** Ein Zeuge, der nur
    prueft, dass beide Aufrufe ankommen, bliebe auch ohne Riegel gruen.
    """

    def __init__(self, dauer: float = 0.02) -> None:
        self.gleichzeitig: int = 0
        self.hoechststand: int = 0
        self.aufrufe: int = 0
        self._dauer = dauer
        self._zaehlsperre = threading.Lock()

    def _arbeiten(self, **_kwargs: object) -> str:
        with self._zaehlsperre:
            self.gleichzeitig += 1
            self.aufrufe += 1
            self.hoechststand = max(self.hoechststand, self.gleichzeitig)
        time.sleep(self._dauer)
        with self._zaehlsperre:
            self.gleichzeitig -= 1
        return "fertig"

    chat = _arbeiten
    embed = _arbeiten
    list = _arbeiten
    pull = _arbeiten


def _parallel(ziel, anzahl: int = 4) -> None:
    """Startet `anzahl` Threads auf `ziel` und wartet auf alle."""
    threads = [threading.Thread(target=ziel) for _ in range(anzahl)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


class DerRiegelSerialisiert(unittest.TestCase):
    """Zwei Threads auf derselben Ressource sind nie gleichzeitig drin."""

    def test_vier_threads_ueberlappen_nicht(self) -> None:
        roh = _Zaehlclient()
        client = GesperrterOllamaClient(roh, "probe")

        _parallel(lambda: client.chat(model="m", messages=[]))

        self.assertEqual(4, roh.aufrufe, "nicht alle Aufrufe kamen an")
        self.assertEqual(
            1, roh.hoechststand,
            f"{roh.hoechststand} Aufrufe waren gleichzeitig im Client — "
            f"der Riegel greift nicht",
        )

    def test_chat_und_embed_teilen_den_riegel_desselben_clients(self) -> None:
        """Ein Client, ein Riegel — gleich welche Methode ihn nimmt.

        Sonst schuetzt der Riegel die Methode statt die Ressource, und der
        geteilte Verbindungspool bleibt ungeschuetzt.
        """
        roh = _Zaehlclient()
        client = GesperrterOllamaClient(roh, "probe")

        def gemischt() -> None:
            client.chat(model="m", messages=[])
            client.embed(model="m", input="x")

        _parallel(gemischt, anzahl=3)

        self.assertEqual(6, roh.aufrufe)
        self.assertEqual(1, roh.hoechststand)

    def test_die_attrappe_wuerde_ueberlappung_zeigen(self) -> None:
        """Die Gegenprobe zum Zeugen: ohne Riegel misst er, was er messen soll.

        Ohne diesen Test waere `hoechststand == 1` auch dann gruen, wenn die
        Attrappe gar nicht zaehlen koennte (`20_TESTS/attrappe-grenze.md`).
        """
        roh = _Zaehlclient()

        _parallel(lambda: roh.chat(model="m", messages=[]))

        self.assertGreater(
            roh.hoechststand, 1,
            "die Attrappe kann keine Ueberlappung zeigen — der Zeuge oben misst nichts",
        )


class JedeRessourceIhrEigenerRiegel(unittest.TestCase):
    """Ein langsamer Zugriff auf die eine Ressource bremst die andere nicht."""

    def test_zwei_clients_laufen_gleichzeitig(self) -> None:
        roh_a, roh_b = _Zaehlclient(0.05), _Zaehlclient(0.05)
        a = GesperrterOllamaClient(roh_a, "a")
        b = GesperrterOllamaClient(roh_b, "b")

        beginn = time.monotonic()
        threads = [
            threading.Thread(target=lambda: a.chat(model="m", messages=[])),
            threading.Thread(target=lambda: b.chat(model="m", messages=[])),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        dauer = time.monotonic() - beginn

        self.assertLess(
            dauer, 0.09,
            f"{dauer:.3f}s fuer zwei Aufrufe a 0.05s — die Riegel sind nicht getrennt",
        )


class KeinWegVorbei(unittest.TestCase):
    """Was der Riegel nicht kennt, laesst er nicht durch."""

    def test_unbekannte_methode_wird_abgewiesen(self) -> None:
        client = GesperrterOllamaClient(_Zaehlclient(), "probe")
        with self.assertRaises(AttributeError) as fall:
            client.generate(model="m", prompt="x")
        self.assertIn("Riegel", str(fall.exception))

    def test_der_rohe_client_ist_nicht_erreichbar(self) -> None:
        """Kein oeffentlicher Zugriff auf das ungeschuetzte Objekt."""
        client = GesperrterOllamaClient(_Zaehlclient(), "probe")
        oeffentlich = [n for n in dir(client) if not n.startswith("_")]
        self.assertNotIn("client", oeffentlich)
        self.assertNotIn("roh", oeffentlich)


class NiemandGreiftAmRiegelVorbei(unittest.TestCase):
    """Strukturpruefung ueber den Serverbaum.

    **Die drei Zusicherungen oben nuetzen nichts, wenn jemand daneben
    zugreift.** Genau so ist der Befund entstanden: Der Riegel war da, und
    vier Wege kannten ihn nicht.
    """

    #: Wo der rohe Client entstehen darf — und sonst nirgends.
    #:
    #: **`scripts/` ist ausdruecklich NICHT ausgenommen.** Ein Messwerkzeug
    #: greift auf dieselbe Ressource zu wie der Betrieb; dass es seltener
    #: laeuft, macht den Zugriff nicht ungefaehrlich, sondern die Kollision
    #: nur schwerer erklaerbar.
    ERLAUBT: frozenset = frozenset({"config.py", "services/llm_riegel.py"})

    def test_kein_modul_baut_einen_eigenen_ollama_client(self) -> None:
        wurzel = Path(__file__).resolve().parents[1]
        treffer: list[str] = []
        for pfad in wurzel.rglob("*.py"):
            rel = pfad.relative_to(wurzel).as_posix()
            if rel.startswith("tests/") or rel in self.ERLAUBT:
                continue
            if "ollama.Client(" in pfad.read_text(encoding="utf-8"):
                treffer.append(rel)
        self.assertEqual(
            [], treffer,
            f"Diese Module bauen einen ungeschuetzten Client: {treffer}",
        )

    def test_kein_modul_importiert_einen_rohen_client(self) -> None:
        wurzel = Path(__file__).resolve().parents[1]
        treffer: list[str] = []
        for pfad in wurzel.rglob("*.py"):
            rel = pfad.relative_to(wurzel).as_posix()
            if rel.startswith("tests/") or rel in self.ERLAUBT:
                continue
            text = pfad.read_text(encoding="utf-8")
            if "ollama_gpu_client" in text or "ollama_cpu_client" in text:
                treffer.append(rel)
        self.assertEqual(
            [], treffer,
            f"Diese Module greifen am Riegel vorbei: {treffer}",
        )


if __name__ == "__main__":
    unittest.main()
