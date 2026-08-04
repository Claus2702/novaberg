"""RechercheAgent — Iterative Web-Recherche zu Themen des Users.

Queue-basiert (aufgabe: recherche). Nutzt Session-Kontext + Web-Suche
fuer einen breiten Ueberblick. Ergebnis -> Shadow-Stack + Novas KZG.
"""

import logging
from dataclasses import dataclass

import psycopg2

from agents.base import BaseAgent, AgentState
from agents.recherche.lagebeurteilung import kontext_paket_bauen, lagebeurteilung_erstellen
from agents.recherche.planung import recherche_planen
from agents.recherche.suche import suche_ausfuehren
from agents.recherche.bewertung import ergebnisse_bewerten
from agents.recherche.destillation import ergebnisse_destillieren, zwischen_destillieren
from agents.recherche.gate import ergebnis_einordnen
from memory.kontext import session_kontext_extrahieren
from services.pixie.stack import stack_push
from services.wissensspeicher import Arbeitsergebnis, embed_text_bauen, ergebnis_ablegen
from tools.db_manager import db_manager
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    redis_client,
    POSTGRES_URL,
    ZIEL_MAX_MITTELFRISTIG,
    PIXIE_RECHERCHE_MAX_ITERATIONEN,
)
from agents.kzg.speicher import embed_text_bauen as kzg_embed_text_bauen
from memory.ziele import ziel_speichern, ziele_aktive_laden
from memory.ziele import embed_text_bauen as ziel_embed_text_bauen
from services.model_services import model_service, EmbedRequest, BackgroundRequest

logger = logging.getLogger("ki_server.agents.recherche")


def _ziel_aus_recherche_extrahieren(recherche_ziel: str, destillat: str) -> dict | None:
    """Extrahiert einen mittelfristigen Zielsatz aus dem Recherche-Ergebnis.

    Args:
        recherche_ziel: Das ursprüngliche Recherche-Ziel.
        destillat: Der destillierte Ergebnis-Text.

    Returns:
        Dict mit zielsatz, motivation, emotion, arousal — oder None.
    """
    import json

    prompt: str = (
        "[IDENTITAET]\n"
        "Du bist Novas Reflexions-Modul.\n\n"
        "[RECHERCHE_ZIEL]\n"
        f"{recherche_ziel}\n\n"
        "[ERGEBNIS]\n"
        f"{destillat[:800]}\n\n"
        "[AUFGABE]\n"
        "Hat diese Recherche ein neues Interesse oder eine offene Frage aufgeworfen,\n"
        "die Nova weiterverfolgen möchte?\n\n"
        "Gib zusätzlich ein kurzes Themen-Label (2-3 Wörter) das den Wissensbereich\n"
        "des Ziels benennt. Beispiele: 'Gartengestaltung', 'KI und Kognition',\n"
        "'Beziehung', 'Natur und Kultur', 'Klimaanpassung'.\n\n"
        "[FORMAT]\n"
        "Wenn ja: JSON mit einem Ziel:\n"
        '{"zielsatz": "Ich möchte ...", "motivation": 0.6, "emotion": "neugierig", "arousal": 0.5, "thema": "Natur und Kultur"}\n\n'
        "Wenn nein (das Thema ist abgeschlossen): antworte mit:\n"
        '{"zielsatz": ""}\n\n'
        "[REGELN]\n"
        "- Nur EIN Ziel, 1-2 Sätze\n"
        "- Motivation 0.4-0.8 (Recherche hat Interesse geweckt, nicht Leidenschaft)\n"
        "- Thema: 2-3 Wörter, knappes Label (kein Satz)\n"
        "- Nicht das Recherche-Ziel wiederholen — das war der Auslöser, nicht das Ergebnis\n"
        "- Sprache: Deutsch, Ich-Perspektive"
    )

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G4) ──
    # _ziel_aus_recherche_extrahieren() laeuft im RechercheAgent, sync invoked
    # aus services/pixie/dispatch.py via asyncio.to_thread → submit_sync.
    # expect_json=True → response.parsed.
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "analyse",
            temperature = 0.3,
            expect_json = True,
            caller      = "recherche/ziel",
        ))
        ziel: dict = response.parsed

        if not ziel.get("zielsatz"):
            logger.info("RechercheAgent: Kein Folgeziel aus Recherche")
            return None

        logger.info(f"RechercheAgent: Folgeziel extrahiert — '{ziel['zielsatz'][:60]}'")
        return ziel

    except Exception as fehler:
        logger.warning(f"RechercheAgent: Ziel-Extraktion fehlgeschlagen — {fehler}")
        return None


@dataclass
class Durchlauf:
    """Was ein Recherche-Durchlauf erarbeitet hat — reiner Datencontainer.

    Traegt genau das, was der Bibliotheks-Schritt braucht, und wird an einer
    Stelle gebaut. `destillat` darf leer sein: Dann ist der Durchlauf
    gescheitert, und der Schritt legt einen Bericht statt einer Wissen-Datei
    an (§5.1).
    """

    thema:         str
    ziel:          str
    destillat:     str
    queries:       list[str]
    lage:          dict
    queue_eintrag: dict
    user_id:       str


def _salienz_aus_auftrag(queue_eintrag: dict) -> float:
    """Liest die auslösende Salienz aus dem Queue-Auftrag.

    Der Wert hat die Recherche ausgelöst und ist beim Schreiben immer
    bekannt — er ist kein Vorgabewert und wird auch nicht zu einem (§11.4).

    Vorbedingung: keine. Nachbedingung: eine Zahl in (0.0, 1.0].
    Fehlerfälle: fehlender, nicht-numerischer oder nicht-positiver Wert
    (ValueError). Der Aufrufer soll daran scheitern: Eine Null in
    `salienz_anfang` sähe später aus wie ein Messergebnis, und in der
    Shadow-Queue tragen belegbar Aufträge eine Null, die das
    Hochsalienz-Tor passiert haben.

    `get(schluessel, default)` allein reicht hier nicht: Ein ausdrücklich
    auf null gesetztes Feld kommt durch den Default hindurch (11_EVA §2).
    """
    # ── Eingabe-Validierung ─────────────────────
    roh = queue_eintrag.get("salienz", queue_eintrag.get("prioritaet"))
    if roh is None:
        meldung: str = (
            f"_salienz_aus_auftrag: Auftrag ohne Salienz und ohne Prioritaet, "
            f"Felder vorhanden: {sorted(queue_eintrag)}"
        )
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    try:
        salienz: float = float(roh)
    except (TypeError, ValueError) as fehler:
        meldung = f"_salienz_aus_auftrag: Salienz {roh!r} ist keine Zahl"
        raise ValueError(meldung) from fehler

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 < salienz <= 1.0:
        meldung = (
            f"_salienz_aus_auftrag: Salienz {salienz!r} liegt ausserhalb der Spanne "
            f"(0.0, 1.0] — der Auftrag traegt keinen brauchbaren Ausloesewert"
        )
        raise ValueError(meldung)

    return salienz


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

    @staticmethod
    def _audit_log(user_id: str, status: str, ergebnis: str) -> None:
        """Schreibt einen hintergrund_log-Eintrag fuer den Bibliotheks-Schritt.

        Eigener Eintrag je Schritt, keine Sammelmeldung: Erst dann ist im
        Nachhinein unterscheidbar, ob die Ablage lief und nichts fand oder
        ob sie gar nicht lief.

        Failsafe: Bei DB-Fehler nur logger.critical, kein Retry — ein Retry
        auf einer kaputten Audit-Senke liefe endlos.

        **Enger gefasst als das Muster in synapsen_decay**, das hier blind
        faengt: Aufgefangen werden Datenbank- und Netzfehler, also das, was
        ein INSERT tatsaechlich wirft. Die Rekursionsgefahr, die dort den
        breiten Fang begruendet, besteht ohne Retry nicht — und ein Defekt
        ausserhalb dieser Menge soll sichtbar werden, statt als verlorener
        Audit-Eintrag zu erscheinen.
        """
        try:
            db_manager.execute(
                """
                INSERT INTO hintergrund_log
                    (user_id, aufgabe, status, ergebnis, verarbeitet_am)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, "recherche_bibliothek", status, ergebnis),
            )
        except (psycopg2.Error, OSError) as ex:
            logger.critical(
                f"hintergrund_log-INSERT fehlgeschlagen: {ex} "
                f"(verlorener Audit-Eintrag: recherche_bibliothek/{status}/{ergebnis[:100]})"
            )

    def _bibliothek_schritt(self, durchlauf: Durchlauf, *, status: str = "") -> None:
        """Ordnet das Ergebnis ein und legt es in der Bibliothek ab.

        Eigener Schritt mit eigenem Audit-Eintrag: Ein Lauf, der mehreres
        tut, faerbt bei einem Fehlschlag im dritten Teil sonst den ganzen
        Auftrag rot, und hinterher ist nicht unterscheidbar, ob die Ablage
        lief und nichts fand oder gar nicht lief.

        `status` uebergeht das Gate. Genutzt wird das fuer den Fall, in dem
        es nichts einzuordnen gibt — eine gescheiterte Destillation ist ein
        `fehlschlag`, und ein Modellaufruf darueber waere eine Frage an ein
        leeres Blatt.

        Vorbedingung: keine — jeder Fehlerfall wird hier behandelt und nicht
        an den Aufrufer weitergereicht.
        Nachbedingung: Bericht-Datei geschrieben, Wissen-Datei bei
        `echte_tiefe`/`ergaenzung`, genau eine Metadatenzeile; in jedem Fall
        ein Audit-Eintrag mit `erledigt` oder `fehler`.
        Fehlerfaelle: Ein Fehlschlag der Ablage wird laut protokolliert und
        beendet den Schritt, **nicht die Recherche**. Ihr Ergebnis geht noch
        auf den Stack und in Novas Gedaechtnis. Was fehlt, ist die Datei —
        und genau das steht dann im Audit, statt still zu verschwinden.
        """
        self._audit_log(durchlauf.user_id, "gestartet", f"Bibliothek: '{durchlauf.thema}'")

        try:
            urteil: dict[str, str] = (
                {"status": status, "begruendung": "Die Destillation lieferte keinen Text."}
                if status else
                ergebnis_einordnen(
                    ziel=durchlauf.ziel, destillat=durchlauf.destillat, lage=durchlauf.lage,
                )
            )
            ergebnis: Arbeitsergebnis = Arbeitsergebnis(
                thema=durchlauf.thema,
                # Ohne Destillat traegt der Bericht das Ziel als Gegenstand.
                # Eine leere Zusammenfassung waere in der Metadatenzeile ein
                # Pflichtfeld ohne Inhalt und scheiterte am Repository.
                destillat=durchlauf.destillat or f"Ohne Ergebnis zum Ziel: {durchlauf.ziel}",
                status=urteil["status"],
                modus="recherche",
                # Paar-Schema (§11.2): Subjekt ist der Mensch, fuer den
                # recherchiert wurde; Gegenueber ist Nova; die Perspektive
                # des Inhalts ist ihre — sie hat ihn erarbeitet.
                user_id=durchlauf.user_id,
                character_id=ASSISTANT_USER_ID,
                beobachter="assistant",
                salienz=_salienz_aus_auftrag(durchlauf.queue_eintrag),
                ziel=durchlauf.ziel,
                begruendung=urteil["begruendung"],
                queries=durchlauf.queries,
            )
            ergebnis.themen_embedding = self._embedding_bauen(ergebnis.destillat)
            pfade: dict[str, str] = ergebnis_ablegen(ergebnis)
        except (ValueError, RuntimeError, OSError, psycopg2.Error) as fehler:
            logger.exception(
                f"RechercheAgent: Ablage in der Bibliothek fehlgeschlagen "
                f"({type(fehler).__name__}) — Thema '{durchlauf.thema}'. "
                f"Die Recherche selbst bleibt davon unberuehrt"
            )
            self._audit_log(durchlauf.user_id, "fehler", f"{type(fehler).__name__}: {fehler}")
            return

        self._audit_log(
            durchlauf.user_id, "erledigt",
            f"Status {ergebnis.status}, Zeile {pfade['zeilen_id']}, "
            f"Bericht {pfade['bericht_pfad']}"
            + (f", Wissen {pfade['wissen_pfad']}" if pfade["wissen_pfad"] else ""),
        )

    @staticmethod
    def _embedding_bauen(destillat: str) -> str | None:
        """Baut den Vektor der Zusammenfassung als pgvector-Literal.

        Nachbedingung: eine Zeichenkette der Form "[v1,v2,...]" oder None.
        None ist zulaessig — die Spalte ist nullbar, und eine Zeile ohne
        Vektor bleibt ueber Thema und Paar auffindbar. Ein Ausfall des
        Embedders darf die Ablage nicht verhindern; er wird protokolliert.

        Aufgefangen werden die Ausnahmen, die die Worker-Schicht ausdruecklich
        wirft (ValueError, RuntimeError) plus Netzfehler. Eine Ausnahme
        ausserhalb dieser Menge wird NICHT hier behandelt — sie waere ein
        unbekannter Zustand, und den still in ein `None` zu verwandeln waere
        genau der Fallback, der einen Defekt maskiert.
        """
        try:
            antwort = model_service.embed.submit_sync(
                EmbedRequest(text=embed_text_bauen(destillat.strip()[:500]))
            )
        except (ValueError, RuntimeError, OSError, TimeoutError):
            logger.exception(
                "RechercheAgent: Embedding der Zusammenfassung fehlgeschlagen — die "
                "Zeile entsteht ohne Vektor und ist ueber die Aehnlichkeitssuche "
                "nicht auffindbar"
            )
            return None

        return "[" + ",".join(str(w) for w in antwort.embedding) + "]"

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
        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID
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
        character_id: str = ASSISTANT_USER_ID if user_id == DEFAULT_USER_ID else DEFAULT_USER_ID
        kontext_paket: dict = kontext_paket_bauen(
            thema=thema or session_kontext.get("thema_kern", ""),
            queue_eintrag=queue_eintrag,
            user_id=user_id,
            character_id=character_id,
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

        durchlauf: Durchlauf = Durchlauf(
            thema=thema or session_kontext.get("thema_kern", ""),
            ziel=recherche_ziel,
            destillat=destillat,
            queries=queries,
            lage=lage,
            queue_eintrag=queue_eintrag,
            user_id=user_id,
        )

        # -- 6a. Gescheiterte Destillation ist ein Fehlschlag MIT Bericht --
        # Die Suche lief, sie hat nur nichts Brauchbares ergeben — genau der
        # Fall, den das Konzept `fehlschlag` nennt (§5.1). Ohne diesen Zweig
        # verbraucht ein Durchlauf zehn Minuten am einzigen seriellen Platz
        # und hinterlaesst keine Spur; die naechste Lagebeurteilung faengt
        # bei null an und sucht dasselbe noch einmal.
        if not destillat:
            self._bibliothek_schritt(durchlauf, status="fehlschlag")
            state["status"] = "fehler"
            state["fehler"] = "Destillation fehlgeschlagen"
            return state

        logger.info(f"RechercheAgent: Destillat — {destillat[:100]}...")

        # -- 6b. Keep/Discard-Gate und Ablage in der Bibliothek --
        self._bibliothek_schritt(durchlauf)

        # -- 7. Ergebnis auf Shadow-Stack --
        try:
            stack_push(
                redis_client=redis_client,
                user_id=user_id,
                aufgabe="recherche",
                thema=thema or session_kontext.get("thema_kern", ""),
                inhalt=destillat,
            )
        except Exception as e:
            logger.warning(f"RechercheAgent: Stack-Push fehlgeschlagen — {e}")

        # -- 8. In Novas KZG speichern (Post-Hook nova_gedaechtnis) --
        try:
            from memory.kzg import kzg_store

            themen_list: list = session_kontext.get("themen", [])

            # zusammenfassung = destillat: kzg_store persistiert daraus das
            # inhalt-Feld. Ohne diesen Schluessel entstanden Vektoren ohne
            # Quelltext (RECHERCHE-WISSEN-ERREICHT-LZG-NIE, Chat 107) — die
            # Synapsen-Promotion verwarf jeden dieser Eintraege in
            # Vorbedingung 3, Recherche-Wissen erreichte das LZG nie.
            salienz_obj: dict = {
                "salienz": 0.7,
                "themen": themen_list,
                "zusammenfassung": destillat,
                "intentionen": ["information_teilen"],
                "emotion": "neutral",
                "modus": session_kontext.get("modus", ""),
                "gedaechtnistyp": "kurz",
                "dimension": "kontext",
            }

            # Embed-Text ueber die eine KZG-Formel — kommagetrennte Themen
            # wie im Hash persistiert, kern = destillat. Damit ist der
            # Vektor aus den gespeicherten Feldern rekonstruierbar.
            themen_str: str = ", ".join(themen_list)
            embed_response = model_service.embed.submit_sync(
                EmbedRequest(text=kzg_embed_text_bauen(themen_str, destillat))
            )
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Recherche: Destillat Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )

            # Recherche-Erkenntnisse ins Paar (user_id, nova) — Beobachter "assistant".
            kzg_store(
                redis_client=redis_client,
                user_id=user_id,
                character_id=ASSISTANT_USER_ID,
                beobachter="assistant",
                salienz_obj=salienz_obj,
                embedding=embedding,
            )
            logger.info("RechercheAgent: In Novas KZG gespeichert")
        except Exception as e:
            logger.warning(f"RechercheAgent: KZG-Write fehlgeschlagen — {e}")

        # -- 9. Mittelfristiges Ziel extrahieren (Drive) --
        try:
            # Max-Check: nicht über ZIEL_MAX_MITTELFRISTIG
            # Novas Ziele stehen je Beziehung. `user_id` ist hier der Mensch,
            # in dessen Gespraech die Recherche lief — also das Gegenueber.
            aktive_ziele: list[dict] = ziele_aktive_laden(
                POSTGRES_URL, ASSISTANT_USER_ID, user_id,
            )
            mittelfristige: int = sum(1 for z in aktive_ziele if z["ziel_typ"] == "mittelfristig")

            if mittelfristige < ZIEL_MAX_MITTELFRISTIG:
                ziel_extrakt: dict | None = _ziel_aus_recherche_extrahieren(
                    recherche_ziel, destillat,
                )

                if ziel_extrakt:
                    try:
                        ziel_response = model_service.embed.submit_sync(
                            EmbedRequest(text=ziel_embed_text_bauen(ziel_extrakt["zielsatz"]))
                        )
                        ziel_emb: list[float] | None = ziel_response.embedding
                        logger.debug(
                            "Recherche: Ziel-Extrakt Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                            len(ziel_emb),
                            ziel_response.duration_seconds,
                        )
                    except Exception:
                        ziel_emb = None

                    ziel_speichern(
                        postgres_url=POSTGRES_URL,
                        user_id=ASSISTANT_USER_ID,
                        character_id=user_id,
                        ziel_typ="mittelfristig",
                        zielsatz=ziel_extrakt["zielsatz"],
                        motivation=ziel_extrakt.get("motivation", 0.6),
                        emotion=ziel_extrakt.get("emotion", "neugierig"),
                        arousal=ziel_extrakt.get("arousal", 0.5),
                        thema=(ziel_extrakt.get("thema") or "").strip()[:100],
                        embedding=ziel_emb,
                    )
            else:
                logger.info(
                    f"RechercheAgent: Max mittelfristige Ziele erreicht "
                    f"({mittelfristige}/{ZIEL_MAX_MITTELFRISTIG}) — kein neues Ziel"
                )

        except Exception as ziel_fehler:
            logger.warning(f"RechercheAgent: Ziel-Speicherung fehlgeschlagen — {ziel_fehler}")

        state["status"] = "abgeschlossen"
        state["ergebnis"] = destillat
        return state
