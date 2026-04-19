"""RechercheAgent — Iterative Web-Recherche zu Themen des Users.

Queue-basiert (aufgabe: recherche). Nutzt Session-Kontext + Web-Suche
fuer einen breiten Ueberblick. Ergebnis -> Shadow-Stack + Novas KZG.
"""

import logging

from agents.base import BaseAgent, AgentState
from agents.recherche.lagebeurteilung import kontext_paket_bauen, lagebeurteilung_erstellen
from agents.recherche.planung import recherche_planen
from agents.recherche.suche import suche_ausfuehren
from agents.recherche.bewertung import ergebnisse_bewerten
from agents.recherche.destillation import ergebnisse_destillieren, zwischen_destillieren
from memory.kontext import session_kontext_extrahieren
from services.pixie.stack import stack_push
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    redis_client,
    ollama_cpu_client,
    EMBED_MODEL,
    PIXIE_RECHERCHE_MAX_ITERATIONEN,
)

logger = logging.getLogger("ki_server.agents.recherche")


class RechercheAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "recherche"

    @property
    def typ(self) -> str:
        return "workflow"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["web_recherche", "themen_analyse"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    def build_graph(self):
        """Kein LangGraph-Subgraph — der Ablauf ist eine lineare
        Python-Schleife mit Iteration. Subgraph waere Overhead."""
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Orchestriert den Recherche-Ablauf.

        1. Session-Kontext destillieren
        2. Suchqueries planen (LLM)
        3. Web-Suche + Page-Fetch
        4. Ergebnisse bewerten (LLM) -> fertig oder Luecken
        5. Bei Luecken: neue Queries -> Schritt 3 (max N Iterationen)
        6. Destillation (LLM)
        7. Ergebnis -> Shadow-Stack + Novas KZG
        """
        user_id: str = state["kontext"].get("context_user_id", DEFAULT_USER_ID)
        queue_eintrag: dict = state.get("parameter", {})
        thema: str = queue_eintrag.get("thema", "")

        logger.info(f"RechercheAgent: Start — Thema aus Queue: '{thema}'")

        # -- 1. Session-Kontext destillieren --
        session_kontext: dict = session_kontext_extrahieren(user_id)

        if not session_kontext and not thema:
            logger.warning("RechercheAgent: Kein Kontext und kein Thema — Abbruch")
            state["status"] = "fehler"
            state["fehler"] = "Kein Kontext verfuegbar"
            return state

        logger.info(f"RechercheAgent: Session-Kontext — {session_kontext.get('thema_kern', '?')}")

        # -- 2a. Kontext-Paket bauen (deterministisch, kein LLM) --
        kontext_paket: dict = kontext_paket_bauen(
            thema=thema or session_kontext.get("thema_kern", ""),
            queue_eintrag=queue_eintrag,
            user_id=user_id,
        )

        # -- 2b. Lagebeurteilung (Qwen3-32B, Analyse-Modell) --
        lage: dict = lagebeurteilung_erstellen(kontext_paket, suchmodus="recherche")
        logger.info(
            f"RechercheAgent: Lagebeurteilung — "
            f"{len(lage.get('wissensluecken', []))} Luecken, "
            f"{len(lage.get('ausschluss', []))} Ausschluesse"
        )

        # -- 3. Planung (Qwen3-32B, mit Lagebeurteilung) --
        plan: dict = recherche_planen(thema, session_kontext, lage)

        if not plan:
            state["status"] = "fehler"
            state["fehler"] = "Planung fehlgeschlagen"
            return state

        recherche_ziel: str = plan.get("ziel", "")
        queries: list[str] = plan.get("queries", [])
        kriterien: list[str] = plan.get("kriterien", [])

        logger.info(f"RechercheAgent: Ziel — {recherche_ziel}")
        logger.info(f"RechercheAgent: {len(queries)} Queries geplant")

        # -- 3-4. Such-Iterations-Schleife mit Zwischen-Destillation --
        bisherige_zusammenfassung: str = ""
        max_iterationen: int = PIXIE_RECHERCHE_MAX_ITERATIONEN

        for iteration in range(max_iterationen):
            logger.info(f"RechercheAgent: Iteration {iteration + 1} von {max_iterationen}")

            # 3. Suche + Fetch
            neue_ergebnisse: list[str] = suche_ausfuehren(queries)

            if not neue_ergebnisse and not bisherige_zusammenfassung:
                logger.warning("RechercheAgent: Keine Ergebnisse gefunden — Abbruch")
                break

            if not neue_ergebnisse:
                logger.info("RechercheAgent: Keine neuen Ergebnisse — destilliere bisherige")
                break

            # Zwischen-Destillation: bisherige Zusammenfassung + neue Rohtexte komprimieren
            if bisherige_zusammenfassung:
                destillations_input = bisherige_zusammenfassung + "\n\n" + "\n\n".join(neue_ergebnisse)
            else:
                destillations_input = "\n\n".join(neue_ergebnisse)

            arbeitskontext: str = session_kontext.get("zusammenfassung", "")

            bisherige_zusammenfassung = zwischen_destillieren(
                ziel=recherche_ziel,
                ergebnisse_text=destillations_input,
                arbeitskontext=arbeitskontext,
            )

            if not bisherige_zusammenfassung:
                logger.warning("RechercheAgent: Zwischen-Destillation fehlgeschlagen")
                break

            logger.info(
                f"RechercheAgent: Zwischen-Destillation — "
                f"{len(bisherige_zusammenfassung)} Zeichen"
            )

            # 4. Bewertung (Qwen3-32B, mit Vorwissen-Abgleich)
            bewertung: dict = ergebnisse_bewerten(
                recherche_ziel, kriterien, bisherige_zusammenfassung, lage
            )

            # Fertig oder weiter?
            if bewertung.get("status") == "fertig":
                logger.info("RechercheAgent: Bewertung — fertig")
                break

            neue_queries: list[str] = bewertung.get("queries", [])
            if not neue_queries:
                logger.info("RechercheAgent: Keine neuen Queries — fertig")
                break

            queries = neue_queries
            logger.info(f"RechercheAgent: Luecken — {len(neue_queries)} neue Queries")

        # -- 5. Finale Destillation --
        # bisherige_zusammenfassung ist kompakt (Fakten, ~800 Zeichen).
        # Finale Destillation macht daraus nutzerfreundlichen Fliesstext.
        destillat: str = ergebnisse_destillieren(
            recherche_ziel, [bisherige_zusammenfassung], session_kontext,
            kontext_paket=kontext_paket, lage=lage,
        ) if bisherige_zusammenfassung else ""

        if not destillat:
            state["status"] = "fehler"
            state["fehler"] = "Destillation fehlgeschlagen"
            return state

        logger.info(f"RechercheAgent: Destillat — {destillat[:100]}...")

        # -- 6. Ergebnis auf Shadow-Stack --
        try:
            stack_push(
                redis_client=redis_client,
                user_id=user_id,
                aufgabe="recherche",
                thema=thema or session_kontext.get("thema_kern", ""),
                inhalt=destillat,
                embed_client=ollama_cpu_client,
                embed_model=EMBED_MODEL,
            )
        except Exception as e:
            logger.warning(f"RechercheAgent: Stack-Push fehlgeschlagen — {e}")

        # -- 7. In Novas KZG speichern (Post-Hook nova_gedaechtnis) --
        try:
            from tools.embedding_manager import embedding_manager
            from memory.kzg import kzg_store

            salienz_obj: dict = {
                "salienz": 0.7,
                "themen": session_kontext.get("themen", []),
                "intentionen": ["information_teilen"],
                "emotion": "neutral",
                "modus": session_kontext.get("modus", ""),
                "gedaechtnistyp": "kurz",
                "dimension": "kontext",
            }

            embedding: list[float] = embedding_manager.embed(destillat)

            kzg_store(
                redis_client=redis_client,
                user_id=ASSISTANT_USER_ID,
                salienz_obj=salienz_obj,
                embedding=embedding,
            )
            logger.info("RechercheAgent: In Novas KZG gespeichert")
        except Exception as e:
            logger.warning(f"RechercheAgent: KZG-Write fehlgeschlagen — {e}")

        state["status"] = "abgeschlossen"
        state["ergebnis"] = destillat
        return state
