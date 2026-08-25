"""Der Riegel vor einem LLM — eine Ressource, ein Sperrmittel.

**Ein Riegel schuetzt seine Ressource, nicht den Vorgang**
(`17_NEBENLAEUFIGKEIT/riegel-schuetzt-ressource.md`). Bis zum 25.08.2026 war
es umgekehrt gebaut: `llm_lock` umschloss in `event_consumer.py` den Lauf des
CharakterGraphen — also einen **Aufrufer** — waehrend die Ressource selbst
offen lag.

**Was daran gemessen wurde (42 Stunden Betriebslog, 25.08.2026):** Zwei
Worker sprachen dieselbe GPU ueber **ein geteiltes `ollama.Client`-Objekt**
an, also ueber einen geteilten httpx-Verbindungspool — **7407 Embed- und 2897
Chat-Aufrufe** aus zwei getrennt serialisierten Warteschlangen, die
voneinander nichts wussten. Dazu zwei Wege, die auch die Warteschlange
umgingen. Kennung: `GPU-LOCK-SCHUETZT-EINEN-VON-FUENF`.

**Die Bauart hier macht das Vorbeigehen unmoeglich statt unerwuenscht.** Der
rohe Client ist privat; nach aussen gibt es nur die gesperrten Methoden. Wer
eine Methode braucht, die hier nicht steht, bekommt einen `AttributeError`
und keine stille Durchreiche — **eine Liste, an die man sich halten muss, ist
genau die Bauart, die diesen Defekt erzeugt hat.**
"""

import logging
import threading
from typing import Any

logger = logging.getLogger("ki_server.llm_riegel")

#: Die Methoden, die unter dem Riegel laufen duerfen.
#:
#: `list` und `pull` stehen ausdruecklich dabei, obwohl sie keine Inferenz
#: sind: **`pull` laedt ein Modell und belegt die Ressource dabei laenger als
#: jeder Chat.** Ein Riegel, der nur die Inferenz kennt, laesst genau den
#: teuersten Zugriff daneben laufen.
_GESPERRTE_METHODEN: frozenset = frozenset({"chat", "embed", "list", "pull"})


class GesperrterOllamaClient:
    """Ein `ollama.Client`, dessen Zugriffe serialisiert sind.

    Ein Objekt dieser Klasse **ist** die Ressource, aus Sicht des Aufrufers.
    Wer es hat, braucht vom Riegel nichts zu wissen — und kann ihn nicht
    vergessen.
    """

    def __init__(self, client: Any, name: str) -> None:
        """Legt den Riegel um einen rohen Client.

        Args:
            client: Das `ollama.Client`-Objekt. Es wird privat gehalten.
            name: Der Name der Ressource, fuer die Protokollzeile.

        Vorbedingung: `name` ist nicht leer — er steht in jeder Wartemeldung
        und ist dort die einzige Angabe, die die Ressourcen unterscheidet.
        """
        # ── Eingabe-Validierung ─────────────────────
        if client is None:
            raise ValueError("GesperrterOllamaClient ohne Client")
        if not name or not name.strip():
            raise ValueError("GesperrterOllamaClient ohne Namen")

        self.__client = client
        self.__lock = threading.Lock()
        self.__name = name.strip()

    @property
    def name(self) -> str:
        """Der Name der Ressource — fuer Protokoll und Fehlermeldung."""
        return self.__name

    def _gesperrt(self, methode: str, *args: Any, **kwargs: Any) -> Any:
        """Fuehrt eine Client-Methode unter dem Riegel aus."""
        with self.__lock:
            return getattr(self.__client, methode)(*args, **kwargs)

    def chat(self, *args: Any, **kwargs: Any) -> Any:
        """Ein Chat-Aufruf, serialisiert gegen jeden anderen Zugriff."""
        return self._gesperrt("chat", *args, **kwargs)

    def embed(self, *args: Any, **kwargs: Any) -> Any:
        """Ein Embedding-Aufruf, serialisiert gegen jeden anderen Zugriff."""
        return self._gesperrt("embed", *args, **kwargs)

    def list(self, *args: Any, **kwargs: Any) -> Any:
        """Die Modellliste — auch sie geht ueber die Verbindung."""
        return self._gesperrt("list", *args, **kwargs)

    def pull(self, *args: Any, **kwargs: Any) -> Any:
        """Ein Modell laden. Belegt die Ressource laenger als jede Inferenz."""
        return self._gesperrt("pull", *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Weist jeden nicht aufgefuehrten Zugriff ab.

        **Keine stille Durchreiche.** Ein `getattr`-Fallback auf den rohen
        Client waere bequem und wuerde genau den Defekt zurueckholen, gegen
        den diese Klasse gebaut ist: einen Weg zur Ressource, der den Riegel
        nicht kennt.
        """
        raise AttributeError(
            f"'{name}' ist am Riegel '{self.__name}' nicht freigegeben. "
            f"Freigegeben sind: {sorted(_GESPERRTE_METHODEN)}. "
            f"Wer eine weitere Methode braucht, nimmt sie hier auf — "
            f"ein Zugriff am Riegel vorbei ist keine Loesung."
        )

    def __repr__(self) -> str:
        return f"<GesperrterOllamaClient '{self.__name}'>"
