"""Per-Turn-Tool-Cache fuer den Thinker-Node.

Verhindert die in THINK-MEM-LOOP dokumentierte Endlos-Schleife identischer
Tool-Aufrufe. Strikt lokal pro think()-Aufruf instanziiert, damit zwischen
parallelen Graph-Laeufen mit unterschiedlichen (user_id, character_id)-
Paaren keine Datenverschmutzung moeglich ist.

Zwei-Stufen-Schutz:
- Stufe 1 (generisch): Cache-Treffer bei identischen Tool-Argumenten.
- Stufe 2 (nur memory_search): Cache-Treffer bei identischen Treffer-Listen
  trotz unterschiedlicher Queries — semantisch aequivalente Anfragen.

Beide Stufen verwenden OrderedDict mit FIFO-Verdraengung bei Erreichen
von MAX_GROESSE, damit der Cache nicht unbegrenzt waechst.

Dazu, seit dem 29.08.2026, das **Suchbudget des Turns**: So oft darf der
Thinker in diesem think()-Aufruf die Suchmaschine rufen
(`THINKER_WEBSUCHE_MAX_JE_TURN`). `[gemessen]` 29.08.2026, 20 Turns: 23
Suchen, bis zu drei je Turn, und die Wikipedia-API sperrte zweimal fuer
180 s. Das Budget lebt hier, weil es dieselbe Lebensdauer hat wie der Cache —
ein Turn — und aus demselben Grund strikt lokal bleiben muss.
"""

import logging
from collections import OrderedDict

from config import THINKER_WEBSUCHE_MAX_JE_TURN

logger = logging.getLogger("ki_server.thinker.cache")


class ThinkerToolCache:
    """Pro-Turn-Cache fuer Thinker-Tool-Aufrufe — und das Suchbudget des Turns.

    Lebensdauer: ein think()-Aufruf. Wird lokal instanziiert und nach
    Rueckkehr aus think() automatisch verworfen. Kann strukturell nicht
    zwischen parallelen Graph-Laeufen verschmutzen.
    """

    MAX_GROESSE: int = 20

    def __init__(self, web_search_budget: int = THINKER_WEBSUCHE_MAX_JE_TURN) -> None:
        # ── Eingabe-Validierung ─────────────────────
        if isinstance(web_search_budget, bool) or not isinstance(web_search_budget, int) \
                or web_search_budget < 0:
            raise ValueError(
                f"web_search_budget muss eine ganze Zahl >= 0 sein, ist {web_search_budget!r}"
            )
        # Stufe 1: tool_name::json(args) -> Tool-Output-String
        self._stufe1: OrderedDict[str, str] = OrderedDict()
        # Stufe 2: result_hash -> None (Set-Verhalten mit FIFO-Disziplin)
        self._stufe2: OrderedDict[str, None] = OrderedDict()
        # Suchbudget: so viele Aufrufe der Suchmaschine hat dieser Turn noch.
        self._web_searches_left: int = web_search_budget
        logger.debug(
            f"ThinkerToolCache initialisiert (MAX_GROESSE={self.MAX_GROESSE}, "
            f"Suchbudget={web_search_budget})"
        )

    # ── Suchbudget des Turns ─────────────────

    def web_search_allowed(self) -> bool:
        """True, solange dieser Turn noch eine Suche gegen die Suchmaschine hat."""
        return self._web_searches_left > 0

    def web_search_spent(self) -> None:
        """Verbucht eine Suche dieses Turns — auch eine aus der Sachlage bediente.

        Vorbedingung: `web_search_allowed()` war True; der Aufrufer hat gefragt.
        Nachbedingung: Der Rest ist um eins kleiner und steht im Log.
        Fehlerfaelle: Ein Verbuchen ohne Rest ist ein Defekt des Aufrufers
            und faellt laut — ein stilles Weiterzaehlen unter null saehe aus
            wie ein verbrauchtes Budget.
        """
        if self._web_searches_left <= 0:
            raise RuntimeError(
                "Suchbudget des Turns ist verbraucht — web_search_allowed() wurde nicht gefragt"
            )
        self._web_searches_left -= 1
        logger.info(f"Thinker-Suchbudget: eine Suche verbucht, Rest {self._web_searches_left}")

    # ── Stufe 1: Argument-Cache ──────────────

    def stufe1_treffer(self, schluessel: str) -> str | None:
        """Liefert den gecachten Tool-Output bei Treffer, sonst None."""
        ergebnis = self._stufe1.get(schluessel)
        if ergebnis is not None:
            logger.info(
                f"Stufe-1-Cache-Treffer fuer Schluessel '{schluessel[:80]}' "
                f"(Laenge={len(ergebnis)})"
            )
        return ergebnis

    def stufe1_speichern(self, schluessel: str, ergebnis: str) -> None:
        """Speichert Tool-Output unter Schluessel, FIFO-Drop bei Ueberlauf."""
        self._stufe1[schluessel] = ergebnis
        logger.debug(
            f"Stufe-1-Cache speichert Schluessel '{schluessel[:80]}' "
            f"(Bestand={len(self._stufe1)})"
        )
        if len(self._stufe1) > self.MAX_GROESSE:
            entfernt, _ = self._stufe1.popitem(last=False)
            logger.debug(f"Stufe-1-Cache voll, FIFO-Drop: '{entfernt[:80]}'")

    # ── Stufe 2: Result-Hash ─────────────────

    def stufe2_kennt(self, hash_wert: str) -> bool:
        """True, wenn der Result-Hash bereits in diesem Turn gesehen wurde."""
        bekannt = hash_wert in self._stufe2
        if bekannt:
            logger.info(f"Stufe-2-Cache-Treffer fuer Hash '{hash_wert[:16]}'")
        return bekannt

    def stufe2_speichern(self, hash_wert: str) -> None:
        """Merkt einen Result-Hash, FIFO-Drop bei Ueberlauf."""
        self._stufe2[hash_wert] = None
        logger.debug(
            f"Stufe-2-Cache speichert Hash '{hash_wert[:16]}' "
            f"(Bestand={len(self._stufe2)})"
        )
        if len(self._stufe2) > self.MAX_GROESSE:
            entfernt, _ = self._stufe2.popitem(last=False)
            logger.debug(f"Stufe-2-Cache voll, FIFO-Drop: '{entfernt[:16]}'")
