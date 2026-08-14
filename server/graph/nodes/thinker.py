"""
Thinker Node — Logisches Nachdenken mit ReAct Pattern.
Sitzt zwischen Responder und Tribunal.

Nutzt LangChain ReAct: Das LLM entscheidet selbst,
welche Tools es braucht und ruft sie eigenstaendig auf.

Denken → Handeln → Beobachten → Denken → ...

Verfuegbare Tools:
  - timeline_check: Termine an einem Datum abfragen
  - timeline_search: Termine nach Keyword suchen
  - memory_search: Gedaechtnis semantisch durchsuchen
  - web_search: Externe Recherche via SearXNG
  - web_fetch: Vollstaendigen Seiteninhalt laden (nach web_search)

Prompt-Schema: [BLOCKNAME]-Format (nova-01-t-d, Chat 27).
"""

import hashlib
import json
import logging

from datetime import datetime
from typing   import Annotated

import redis

from langchain_core.tools import tool

from agents.timeline.event_time import precision_has_time, precision_format
from graph.nodes.thinker_cache import ThinkerToolCache
from graph.reiz          import reiz_ist_eigener_gedanke, reiz_text
from graph.state         import ConversationState
from memory.repositories.timeline_repository import TimelineRepository
from memory.lzg_knoten    import anker_retrieval
from memory.utils         import embedding_zu_pgvector_str
from config              import get_node_config, PROMPTS
from services.model_services import model_service, ChatRequest, EmbedRequest

logger = logging.getLogger("ki_server.thinker")

from tools.web.search import web_search_manager
from tools.web.fetch import page_fetch
from tools.thinking_normalizer import get_thinking_normalizer


# Block 3 Teil B: Nachfass-Iteration bei Ollama-thinking/content-Split.
# Separate Haertung -- zaehlt NICHT gegen max_iterations, lieber einmal zu
# viel, dann Schluss. Wortlaut + Limit dokumentiert in
# tools/thinking_normalizer.py.
NACHFASS_MAX: int = 2


# ─────────────────────────────────────────────
# Tool-Factory
# ─────────────────────────────────────────────
# Tools werden als Closures erzeugt, damit sie
# Zugriff auf postgres_url, redis_client etc. haben.

def create_tools(
    postgres_url:  str,
    user_id:       str,
    character_id:  str,
    cache:         ThinkerToolCache,
) -> list:
    """Erzeugt die Tools für den Thinker-Agent.

    Der Per-Turn-Cache wird nur an memory_search durchgereicht — Stufe 2
    (Result-Hash) lebt strukturell ausschliesslich dort. Die Stufe-1-
    Pruefung haengt auf der Aufruf-Schicht in _execute_tool_call().
    """

    @tool
    def timeline_check(datum: Annotated[str, "Datum im Format YYYY-MM-DD"]) -> str:
        """Prüfe welche Termine an einem bestimmten Datum existieren.
        Nutze dieses Tool wenn in der Antwort Termine, Daten oder Zeitangaben vorkommen.
        Damit kannst du prüfen ob es zeitliche Konflikte mit bestehenden Terminen gibt.
        Bedenke: Termine haben eine Dauer und erfordern physische Anwesenheit —
        zwei Termine zur gleichen Zeit am gleichen Tag sind ein Konflikt."""
        logger.info(f"Thinker-Tool: timeline_check({datum})")

        from datetime import datetime as dt
        from zoneinfo import ZoneInfo
        from config import TIMEZONE

        try:
            tag = dt.strptime(datum, "%Y-%m-%d")
        except ValueError:
            return f"Ungültiges Datum: {datum}"

        tz = ZoneInfo(TIMEZONE)
        von = tag.replace(hour=0, minute=0, second=0, tzinfo=tz)
        bis = tag.replace(hour=23, minute=59, second=59, tzinfo=tz)

        rows: list[dict] = TimelineRepository.find_by_date_range(
            postgres_url, user_id, von, bis
        )

        if not rows:
            return f"Keine Termine am {datum} gefunden."

        parts: list[str] = []
        for r in rows:
            zeit = r["event_time"].strftime("%H:%M") if precision_has_time(r.get("precision", "day")) else ""
            detail = f" — {r['details']}" if r.get("details") else ""
            parts.append(f"[{r['event_type']}] {zeit} {r['title']}{detail}".strip())

        return f"Termine am {datum}:\n" + "\n".join(parts)

    @tool
    def timeline_search(keyword: Annotated[str, "Suchbegriff für Termine"]) -> str:
        """Suche nach Terminen anhand eines Begriffs (z.B. 'Friseur', 'Zahnarzt', 'Geburtstag').
        Nutze dieses Tool wenn du prüfen willst, ob es bereits ähnliche Termine gibt
        oder wann der nächste/letzte Termin einer bestimmten Art war."""
        logger.info(f"Thinker-Tool: timeline_search({keyword})")

        rows: list[dict] = TimelineRepository.find_by_keyword(
            postgres_url, user_id, keyword, "both", 5
        )

        if not rows:
            return f"Keine Termine zu '{keyword}' gefunden."

        parts: list[str] = []
        for r in rows:
            zeit = r["event_time"].strftime("%d.%m.%Y")
            if precision_has_time(r.get("precision", "day")):
                zeit += f" {r['event_time'].strftime('%H:%M')}"
            detail = f" — {r['details']}" if r.get("details") else ""
            parts.append(f"[{r['event_type']}] {zeit}: {r['title']}{detail}")

        return "\n".join(parts)

    @tool
    def memory_search(frage: Annotated[str, "Semantische Suchanfrage ans Gedächtnis"]) -> str:
        """Durchsuche das Langzeitgedächtnis des Nutzers nach relevanten Informationen.
        Nutze dieses Tool wenn du Fakten über den Nutzer prüfen willst,
        z.B. ob eine Behauptung in der Antwort mit dem übereinstimmt, was bekannt ist."""
        # Implementierung (Faktencheck-Read): liest direkt die lzg_knoten.
        # 1. Embedding der Query erzeugen, in pgvector-Literal wandeln.
        # 2. anker_retrieval() liefert die Top-20 lzg_knoten-Dicts (Cosine-sortiert,
        #    ohne Similarity-Filter — der Faktencheck soll auch schwache Treffer sehen).
        # 3. _format_faktencheck_treffer() baut den schlanken Faktencheck-Block.

        logger.info(f"Thinker.memory_search: query={frage[:60]}")

        request = EmbedRequest(text=frage)
        embed_response = model_service.embed.submit_sync(request)
        embedding: list[float] = embed_response.embedding
        logger.debug(
            "Thinker: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(embedding),
            embed_response.duration_seconds,
        )

        embedding_str: str = embedding_zu_pgvector_str(embedding)
        treffer: list[dict] = anker_retrieval(
            postgres_url=postgres_url,
            user_id=user_id,
            character_id=character_id,
            embedding_str=embedding_str,
            top_k=20,
            min_similarity=0.0,
        )

        # Stufe 2 (THINK-MEM-LOOP): Result-Hash ueber stabile, identifizierende
        # Felder. Effektives Gewicht und Arousal sind Decay-volatil bzw.
        # Float-instabil — bewusst ausgeschlossen, sonst waere der Hash
        # zwischen zwei Aufrufen wackelig. Reihenfolge bleibt wie aus
        # anker_retrieval geliefert (pgvector-Sortierung deterministisch
        # bei identischer Query). Die lzg_knoten-id (PK) ist der stabile
        # Identifikator.
        hash_input: tuple = tuple(e.get("id") for e in treffer)
        result_hash: str = hashlib.sha256(repr(hash_input).encode()).hexdigest()

        if cache.stufe2_kennt(result_hash):
            logger.info(
                "Thinker.memory_search: Stufe-2-Treffer — identische Treffer "
                "wie frueherer Aufruf in diesem Turn, gebe Hinweis zurueck"
            )
            return (
                "Suche mit anderen Worten ergibt dieselben Treffer wie eine "
                "vorherige Anfrage in diesem Turn. Verwende ein anderes Tool "
                "oder antworte direkt."
            )

        cache.stufe2_speichern(result_hash)

        if not treffer:
            logger.info("Thinker.memory_search: keine Treffer")
            return "Keine relevanten Einträge im Langzeitgedächtnis gefunden."

        formatierter_kontext: str = _format_faktencheck_treffer(treffer)
        logger.info(
            f"Thinker.memory_search: {len(treffer)} Treffer, "
            f"Output-Laenge {len(formatierter_kontext)}"
        )
        return formatierter_kontext

    @tool
    def web_search(suchbegriff: Annotated[str, "Suchbegriff für Web-Recherche"]) -> str:
        """Durchsuche das Internet nach aktuellen Informationen.
        Nutze dieses Tool wenn:
        - Die Antwort Fakten enthaelt die sich auf aktuelle Ereignisse beziehen
        - Du Behauptungen gegen externe Quellen pruefen willst
        - Der Nutzer nach Informationen fragt die nicht im Gedaechtnis sind
        - Der Router needs_web=true gesetzt hat

        Liefert eine Trefferliste plus den vollstaendigen Artikeltext
        des relevantesten Ergebnisses. Fuer weitere URLs nutze web_fetch(url)."""
        logger.info(f"Thinker-Tool: web_search({suchbegriff})")

        try:
            results: list[dict] = web_search_manager.suchen(suchbegriff, max_results=5)

            if not results:
                return f"Keine Ergebnisse fuer '{suchbegriff}' gefunden."

            # Uebersicht aller Treffer (Snippets)
            parts: list[str] = []
            for i, r in enumerate(results, 1):
                parts.append(f"{i}. {r['title']}\n   URL: {r['url']}\n   {r['content']}")

            uebersicht: str = f"Web-Ergebnisse fuer '{suchbegriff}':\n\n" + "\n\n".join(parts)

            # Automatisch Top-Treffer fetchen
            top_url: str = results[0]["url"]
            logger.info(f"Thinker-Tool: auto-fetch({top_url})")
            volltext: str = page_fetch(top_url)

            if volltext:
                return (
                    f"{uebersicht}\n\n"
                    f"--- Vollstaendiger Inhalt von {top_url} ---\n\n"
                    f"{volltext}"
                )

            return uebersicht

        except Exception as fehler:
            logger.exception(f"{type(fehler).__name__}: Thinker: Web-Suche fehlgeschlagen")
            return f"Web-Suche fehlgeschlagen: {fehler}"

    @tool
    def web_fetch(url: Annotated[str, "URL der Webseite"]) -> str:
        """Lade den vollstaendigen Textinhalt einer Webseite.
        web_search laedt bereits automatisch den Top-Treffer.
        Nutze dieses Tool nur wenn du eine ANDERE URL aus der
        Trefferliste laden willst.
        Gibt den extrahierten Artikeltext zurueck (ohne Navigation, Werbung, Footer)."""
        logger.info(f"Thinker-Tool: web_fetch({url})")

        text: str = page_fetch(url)
        if not text:
            return f"Seite konnte nicht geladen werden: {url}"
        return f"Seiteninhalt von {url}:\n\n{text}"

    return [timeline_check, timeline_search, memory_search, web_search, web_fetch]


# ─────────────────────────────────────────────
# Thinker System-Prompt ([BLOCKNAME]-Schema)
# ─────────────────────────────────────────────

def _build_thinker_prompt(today: str) -> str:
    """Baut den Thinker-System-Prompt aus [BLOCKNAME]-Bloecken zusammen."""
    return "\n\n".join([
        PROMPTS["thinker.identity"].format(today=today),
        PROMPTS["thinker.task"],
        PROMPTS["thinker.rules"],
    ])


# ─────────────────────────────────────────────
# Verarbeitungs-Block (THINK-TRANSITION-INFO)
# ─────────────────────────────────────────────
def _build_verarbeitungs_block(agent_results: list) -> str:
    """Baut den [VERARBEITUNG]-Block fuer den Thinker-Reasoning-Input.

    Liefert leeren String wenn keine erfolgreichen AgentResults vorliegen.
    Bei Erfolg (status='abgeschlossen'): operations-neutraler Block, der dem
    Thinker mitteilt, dass eine Aenderung in diesem Turn passiert ist.
    """
    from graph.format.agent_results import format_success_lines

    successes: list = [
        r for r in agent_results
        if hasattr(r, "status") and r.status == "abgeschlossen"
    ]

    if not successes:
        return ""

    ergebnis_texte: str = format_success_lines(successes)

    block: str = (
        "[VERARBEITUNG]\n"
        "Eine Fachabteilung hat in diesem Turn folgende Operation ausgefuehrt:\n\n"
        f"{ergebnis_texte}\n\n"
        "Diese Operation hat den Datenbestand bereits veraendert. Tool-Aufrufe,\n"
        "die zu dieser Operation passende Eintraege finden, zeigen das Ergebnis\n"
        "der Aenderung — nicht einen Konflikt. Eintraege im\n"
        "[GEDAECHTNIS], die der Aenderung widersprechen, zeigen den Stand VOR\n"
        "der Operation — auch das ist kein Konflikt. Eine Antwort, die die\n"
        "Operation bestaetigt, ist deshalb korrekt."
    )

    logger.debug(f"Thinker: Verarbeitungs-Block gebaut ({len(successes)} Operation(en))")
    return block


# ─────────────────────────────────────────────
# Faktencheck-Treffer (anker_retrieval → Prompt)
# ─────────────────────────────────────────────
def _retry_nutzlast(state: ConversationState) -> dict:
    """Baut das Ereignis-Payload fuer den zweiten Versuch desselben Reizes.

    **Der Reiz reist in derselben Gestalt weiter, in der er ankam.** Wer einen
    eigenen Gedanken auf den Reiz-Platz des Folge-Ereignisses legt, macht aus
    der Wiederholung einen Nutzer-Turn: Der Zugriffsknoten verzweigt danach,
    der Rohturn schreibt die Herkunft, und ab dem zweiten Versuch ist beides
    falsch. Auffallen kann es nicht — ein Nutzer-Turn mit Text sieht
    vollstaendig aus.

    Eigene Funktion und nicht drei Zeilen im Rumpf, weil die Zusicherung sonst
    nur ueber einen vollstaendigen Thinker-Lauf pruefbar waere.

    Vorbedingung: `state` traegt den Reiz dieses Durchlaufs.
    Nachbedingung: Genau eines von `user_prompt` und `eigener_gedanke` ist
        belegt, und `reiz_herkunft` benennt, welches.
    Fehlerfaelle: keine — ein leerer Reiz erzeugt ein leeres Feld, und der
        Folgelauf meldet ihn an derselben Stelle wie dieser.

    Args:
        state: der Zustand des Durchlaufs.

    Returns:
        Das Payload des Folge-Ereignisses.
    """
    # ── Eingabe-Validierung ─────────────────────
    eigener: bool = reiz_ist_eigener_gedanke(state)

    # ── Verarbeitung ────────────────────────────
    nutzlast: dict = {
        "user_prompt":            "" if eigener else state.get("user_prompt", ""),
        "eigener_gedanke":        state.get("eigener_gedanke", "") if eigener else "",
        "reiz_herkunft":          "eigener_impuls" if eigener else "",
        "turn_id":                state.get("turn_id", ""),
        "thinker_unsicher_retry": True,
    }

    # ── Ausgabe-Verifikation ────────────────────
    if nutzlast["user_prompt"] and nutzlast["eigener_gedanke"]:
        logger.error(
            "Thinker: Retry-Nutzlast traegt beide Reiz-Plaetze — der Folgelauf "
            "haette zwei Gegenstaende (turn_id=%s)", nutzlast["turn_id"],
        )

    return nutzlast


def _format_faktencheck_treffer(treffer: list[dict]) -> str:
    """Formatiert anker_retrieval-Knoten fuer den Thinker-Faktencheck.

    Schlank und faktenorientiert: nur inhalt + dimension, geordnet nach
    Cosine-Naehe (Reihenfolge aus der SQL erhalten, NICHT nach Gewicht
    umsortiert). Kein Gewichtswert im Output — ein Faktencheck prueft
    Wahrheit, nicht emotionale Salienz; das Gewicht waere Rauschen und
    koennte das LLM verleiten, Schwere mit Korrektheit zu verwechseln.

    Mit ausgegeben wird der beobachter (Schreiber der Erinnerung), weil er die
    Evidenzbewertung beim Faktencheck beeinflusst — eine User-Aussage ist
    andere Evidenz als eine Nova-Aussage.

    Args:
        treffer: list[dict] aus anker_retrieval (Keys: inhalt, dimension,
                 beobachter, cosine, ...). Bereits cosine-absteigend sortiert.

    Returns:
        Formatierter Prompt-Block. Leere Liste -> "".
    """
    # ── Eingabe-Validierung ─────────────────────
    if not treffer:
        return ""

    # ── Verarbeitung ────────────────────────────
    zeilen: list[str] = []
    for t in treffer:
        inhalt: str = t.get("inhalt", "")
        dimension: str = t.get("dimension", "")
        beobachter: str = t.get("beobachter", "")
        if not inhalt:
            continue
        zeilen.append(f"[LZG/{dimension}, Quelle: {beobachter}]: {inhalt}")

    # ── Ausgabe ─────────────────────────────────
    return "\n".join(zeilen)


# ─────────────────────────────────────────────
# Thinker Node
# ─────────────────────────────────────────────
def think(
    state:         ConversationState,
    redis_client:  redis.Redis,
    postgres_url:  str,
    user_id:       str
) -> ConversationState:
    """
    Denkt über die Antwort nach.
    Nutzt ReAct-Pattern: Denken → Tool aufrufen → Beobachten → Weiterdenken.
    """
    jetzt = datetime.now()
    today: str = jetzt.strftime("%d.%m.%Y, %H:%M Uhr")

    # ── Schnell-Check: Braucht es überhaupt Nachdenken? ──
    response: str = state["response"]
    # Der Reiz dieses Durchlaufs, nicht der Reiz-Platz — auf einem Impuls-Turn
    # ist der Gegenstand Novas eigener Gedanke.
    prompt:   str = reiz_text(state)

    # Block 3 Teil D: Erkennen, ob wir bereits im Unsicherheits-Retry sind.
    # Der Self-Trigger aus dem ersten Doppel-Fehlschlag legt diesen Marker
    # ins event_payload (siehe Self-Trigger-Block unten). Im Retry darf der
    # Thinker KEINEN zweiten Trigger setzen — ein Retry, dann definitiv
    # Schluss, lieber unsichere Antwort raus als Endlosschleife.
    event_payload: dict = state.get("event_payload") or {}
    ist_unsicher_retry: bool = bool(event_payload.get("thinker_unsicher_retry", False))
    if ist_unsicher_retry:
        logger.info(
            "Thinker: Unsicherheits-Retry erkannt (event_payload.thinker_unsicher_retry=True) "
            "— ein weiterer Self-Trigger wird bei Doppel-Fehlschlag NICHT gesetzt"
        )

    fact_indicators: list[str] = [
        "am ", "um ", "20", "19", "Uhr", "Termin", "Datum",
        "März", "April", "Mai", "Juni", "Juli", "August",
        "September", "Oktober", "November", "Dezember", "Januar", "Februar",
        "morgen", "übermorgen", "nächste", "Montag", "Dienstag", "Mittwoch",
        "Donnerstag", "Freitag", "Samstag", "Sonntag",
        "Milliard", "Million", "Prozent", "%", "km", "kg",
    ]

    needs_thinking: bool = any(
        indicator in response or indicator in prompt
        for indicator in fact_indicators
    )

     # Router hat Web-Bedarf erkannt → immer denken
    if state.get("needs_web"):
        needs_thinking = True
        logger.info("Thinker: Router hat needs_web=true gesetzt — Reasoning erzwungen")


    if not needs_thinking:
        logger.info("Thinker: Keine prüfbaren Fakten erkannt — Durchlauf")
        return state

    logger.info("Thinker: Prüfbare Fakten erkannt — starte Reasoning...")

    character_id: str = state.get("character_id", "")

    # Per-Turn-Tool-Cache (THINK-MEM-LOOP). Strikt lokal — keine Verschmutzung
    # zwischen parallelen Graph-Laeufen mit unterschiedlichen (user_id,
    # character_id)-Paaren moeglich, weil Lebensdauer = Lebensdauer von think().
    tool_cache: ThinkerToolCache = ThinkerToolCache()
    logger.info("Thinker: Per-Turn-Tool-Cache instanziiert")

    tools: list = create_tools(
        postgres_url, user_id, character_id, tool_cache
    )

    # ── Reasoning-Prompt zusammenbauen ───────
    system_prompt: str = _build_thinker_prompt(today)

    tool_descriptions: str = "\n".join(
        f"- {t.name}: {t.description}" for t in tools
    )

    # ── User-Message aus Bloecken zusammenbauen ──
    msg_parts: list[str] = [
        "[TOOLS]\n"
        "Verfuegbare Tools fuer die Pruefung.\n"
        "Um ein Tool zu nutzen, schreibe: TOOL: toolname(parameter)\n"
        f"Beispiel: TOOL: timeline_check(2026-03-20)\n\n"
        f"{tool_descriptions}",

        f"[BENUTZERANFRAGE]\n"
        f"Der urspruengliche Prompt des Nutzers.\n\n"
        f"{prompt}",

        f"[ANTWORT]\n"
        f"Die folgende Antwort muss geprueft werden.\n\n"
        f"{response}",
    ]

    verarbeitungs_block: str = _build_verarbeitungs_block(state.get("agent_results", []))
    if verarbeitungs_block:
        msg_parts.insert(1, verarbeitungs_block)

    if state.get("memory_context"):
        msg_parts.append(
            f"[GEDAECHTNIS]\n"
            f"Bekannter Kontext ueber den Nutzer.\n\n"
            f"{state['memory_context']}"
        )

    if state.get("needs_web"):
        msg_parts.append(
            "[WEBSUCHE]\n"
            "Web-Suche ist erforderlich. Der Router hat needs_web=true gesetzt.\n"
            "Die Antwort wurde OHNE aktuelle Web-Informationen generiert.\n"
            "Du MUSST web_search() aufrufen, bevor du ERGEBNIS: OK schreibst.\n"
            "Formuliere den Suchbegriff aus der FRAGE DES NUTZERS."
        )

    msg_parts.append("Analysiere jetzt schrittweise.")

    reasoning_input: str = "\n\n".join(msg_parts)

    logger.info(f"Thinker: System-Prompt:\n{system_prompt}")
    logger.info(f"Thinker: Reasoning-Input:\n{reasoning_input}")

    # ── Reasoning-Loop (max 3 Iterationen) ───
    messages: list[dict] = [
        {"role": "user", "content": reasoning_input},
    ]

    max_iterations: int = 5
    tool_map:       dict = {t.name: t for t in tools}
    node_cfg = get_node_config("thinker")

    # Block 3 Teil B: Normalizer einmal holen (per-Connector, siehe
    # tools/thinking_normalizer.py). Nachfass-Zaehler ist turn-weit und
    # zaehlt NICHT gegen max_iterations — total max NACHFASS_MAX Nachfass-
    # Calls in diesem think()-Aufruf.
    normalizer = get_thinking_normalizer()
    nachfass_versuche: int = 0

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # think() laeuft im CharacterGraph (services/event_consumer.py ruft den
    # Graphen via asyncio.to_thread(_graph_streamen, ...) im Worker-Thread).
    # Kein Event-Loop im aufrufenden Thread → submit_sync bruckt in den
    # Worker-Loop (Loop-Binding-Lesson). Schleifenlogik unveraendert: ein
    # submit_sync pro Iteration, gleicher messages-/Tool-Zyklus.
    for i in range(max_iterations):
        logger.info(f"Thinker: Reasoning-Iteration {i + 1}")

        # Der Thinker ist der einzige Node mit echter Reasoning-Kette —
        # think=True ist hier Funktion, nicht Konfiguration. Default aller
        # anderen Nodes ist False. Nicht aus node_cfg lesen: think folgt aus
        # der Rolle des Nodes, nicht aus einer Config-Schraube (Block 3).
        chat_request = ChatRequest(
            messages          = messages,
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.15),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            think             = True,
            caller            = "thinker",
        )
        response = model_service.chat.submit_sync(chat_request)

        content: str = response.text
        messages.append({"role": "assistant", "content": content})

        state["token_total"] += response.token_total

        # ── Block 3 Teil B: Nachfass bei Ollama-thinking/content-Split ──
        # Ollama legt bei think=True den Output nicht-deterministisch mal in
        # content, mal NUR ins thinking-Feld. Der Normalizer erkennt das und
        # weist eine Nachfass-Iteration an, die das Reasoning als Material
        # gibt und das Steuer-FORMAT exakt einfordert. Nachfass laeuft mit
        # think=False, damit der Reparatur-Call nicht wieder ins thinking
        # driftet. Der Nachfass-content faellt in DERSELBEN max_iterations-
        # Runde durch die unten folgenden TOOL:/ERGEBNIS:-Pruefungen.
        befund = normalizer.pruefen(content, response.thinking)
        if befund.braucht_nachfass and nachfass_versuche < NACHFASS_MAX:
            nachfass_versuche += 1
            logger.info(
                "Thinker: content leer, thinking gefuellt (Ollama-Split) — "
                "Nachfass-Iteration %d/%d",
                nachfass_versuche,
                NACHFASS_MAX,
            )

            # Wortlaut bewusst minimal — die Marker MUESSEN exakt zu den
            # Pruefungen unten passen (TOOL:, ERGEBNIS: OK, ERGEBNIS:
            # KORREKTUR, PROBLEME:, KORRIGIERTE ANTWORT:). Aenderung hier
            # waere ein Bruch der Loop-Logik.
            nachfass_prompt: str = (
                "Du hast bereits analysiert. Deine bisherige Analyse:\n\n"
                f"{befund.thinking_material}\n\n"
                "Gib jetzt AUSSCHLIESSLICH deine Entscheidung in genau einem "
                "dieser Formate aus, ohne weiteren Text:\n"
                "TOOL: toolname(parameter)\n"
                "ERGEBNIS: OK\n"
                "ERGEBNIS: KORREKTUR\n"
                "PROBLEME: <stichpunkte>\n"
                "KORRIGIERTE ANTWORT: <die verbesserte Antwort>"
            )
            messages.append({"role": "user", "content": nachfass_prompt})

            nachfass_request = ChatRequest(
                messages          = messages,
                system            = system_prompt,
                temperature       = node_cfg.get("temperature", 0.15),
                max_output_tokens = node_cfg.get("max_output_tokens"),
                think             = False,
                caller            = "thinker_nachfass",
            )
            nachfass_response = model_service.chat.submit_sync(nachfass_request)
            content = nachfass_response.text
            messages.append({"role": "assistant", "content": content})
            state["token_total"] += nachfass_response.token_total

        elif befund.braucht_nachfass:
            # Doppel-Fehlschlag: Nachfass-Limit ist erschoepft.
            if ist_unsicher_retry:
                # Bereits im Retry — KEIN weiterer Self-Trigger (Haertung gegen
                # Endlos-Schleifen "Hmm... — Hmm... — Hmm..."). Antwort bleibt
                # unveraendert, wie das heutige max_iterations-Verhalten.
                logger.warning(
                    "Thinker: Nachfass-Limit erreicht (%d) im Unsicherheits-Retry "
                    "— kein weiterer Self-Trigger, Antwort bleibt unveraendert",
                    NACHFASS_MAX,
                )
                state["node_annotations"].append(
                    "[Thinker] Nachfass erschoepft im Retry — gebe beste Antwort "
                    "ohne weiteren Trigger"
                )
                return state

            # Erster Durchlauf, Doppel-Fehlschlag — Original-Antwort erhalten,
            # neutrale Geste anhaengen (laeuft NICHT durch Responder-Direktiven,
            # kann gegen keine Siezen/Duzen-Direktive verstossen), Self-Trigger
            # via Event-Queue setzen.
            geste: str = "Hmm... ich muss das nochmal durchgehen."
            bestehende_antwort: str = state.get("response") or ""
            if bestehende_antwort:
                state["response"] = f"{bestehende_antwort}\n\n{geste}"
            else:
                state["response"] = geste

            state["self_trigger"] = True
            state["self_trigger_payload"] = _retry_nutzlast(state)

            logger.warning(
                "Thinker: Doppel-Fehlschlag — Self-Trigger im State gesetzt "
                "(self_trigger=True) — Auslieferung haengt am Event-Consumer"
            )
            state["node_annotations"].append(
                "[Thinker] Doppel-Fehlschlag — Self-Trigger im State gesetzt "
                "(self_trigger=True) — Auslieferung haengt am Event-Consumer"
            )
            return state

        # Tool-Aufruf erkennen
        if "TOOL:" in content:
            tool_result: str = _execute_tool_call(content, tool_map, tool_cache)
            messages.append({"role": "user", "content": f"Tool-Ergebnis:\n{tool_result}"})
            logger.info(f"Thinker: Tool ausgeführt → {tool_result[:80]}...")
            continue

        # Ergebnis erkennen
        if "ERGEBNIS: OK" in content:
            logger.info("Thinker: Analyse abgeschlossen — Antwort ist korrekt")
            return state

        if "ERGEBNIS: KORREKTUR" in content:
            corrected:  str       = _extract_corrected_response(content)
            issues:     list[str] = _extract_issues(content)

            if corrected:
                logger.info("Thinker: Antwort korrigiert")
                state["response"] = corrected
                state["node_annotations"].append(
                    f"[Thinker] Korrektur durchgeführt: {', '.join(issues)}"
                )
                for issue in issues:
                    logger.info(f"Thinker: Problem → {issue}")
                    state["node_annotations"].append(f"[Thinker/Issue] {issue}")

            return state

    logger.info("Thinker: Max Iterationen erreicht — Antwort bleibt unverändert")
    return state


# ─────────────────────────────────────────────
# Hilfsfunktionen
# ─────────────────────────────────────────────
def _execute_tool_call(content: str, tool_map: dict, cache: ThinkerToolCache) -> str:
    """Extrahiert und führt einen Tool-Aufruf aus dem LLM-Output aus.

    Stufe 1 (THINK-MEM-LOOP): Bei identischen Argumenten in diesem Turn wird
    das Tool nicht erneut ausgefuehrt, sondern ein Hinweis-String
    zurueckgegeben. Greift generisch fuer alle 5 Thinker-Tools.
    """
    try:
        tool_line: str = ""
        for line in content.split("\n"):
            if "TOOL:" in line:
                tool_line = line.strip()
                break

        if not tool_line:
            return "Kein Tool-Aufruf erkannt."

        tool_part: str = tool_line.split("TOOL:")[1].strip()
        tool_name: str = tool_part.split("(")[0].strip()
        param:     str = tool_part.split("(")[1].rstrip(")").strip().strip("\"'")

        if tool_name not in tool_map:
            return f"Unbekanntes Tool: {tool_name}"

        # Stufe 1 (THINK-MEM-LOOP): Argument-Cache vor Tool-Invocation
        schluessel: str = f"{tool_name}::{json.dumps(param, sort_keys=True, default=str)}"
        treffer: str | None = cache.stufe1_treffer(schluessel)
        if treffer is not None:
            logger.info(
                f"Thinker: Stufe-1-Treffer fuer {tool_name} — Tool wird nicht "
                f"erneut ausgefuehrt"
            )
            return (
                "Bereits in diesem Turn ausgefuehrt mit identischen Argumenten "
                "— Ergebnis waere dasselbe. Verwende ein anderes Tool oder "
                "antworte direkt."
            )

        logger.info(f"Thinker: Führe Tool aus → {tool_name}({param})")

        result = tool_map[tool_name].invoke(param)
        ergebnis: str = str(result)

        # Stufe 1: Ergebnis fuer kuenftige identische Aufrufe in diesem Turn merken
        cache.stufe1_speichern(schluessel, ergebnis)

        return ergebnis

    except Exception as fehler:
        logger.exception(f"{type(fehler).__name__}: Thinker: Tool-Ausführung fehlgeschlagen")
        return f"Tool-Fehler: {fehler}"


def _extract_corrected_response(content: str) -> str:
    """Extrahiert die korrigierte Antwort aus dem Thinker-Output."""
    marker: str = "KORRIGIERTE ANTWORT:"
    if marker not in content:
        return ""

    corrected: str = content.split(marker)[1].strip()
    corrected = corrected.strip("`").strip()

    return corrected


def _extract_issues(content: str) -> list[str]:
    """Extrahiert die Problem-Liste aus dem Thinker-Output."""
    marker: str = "PROBLEME:"
    if marker not in content:
        return []

    problems_section: str = content.split(marker)[1]

    if "KORRIGIERTE ANTWORT:" in problems_section:
        problems_section = problems_section.split("KORRIGIERTE ANTWORT:")[0]

    issues: list[str] = [
        line.strip().lstrip("-").lstrip("•").strip()
        for line in problems_section.strip().split("\n")
        if line.strip() and len(line.strip()) > 2
    ]

    return issues
