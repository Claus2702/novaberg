"""
Graph State — Zentrale Datenstruktur für den Gesprächsgraphen.
Jeder Node liest und schreibt auf diesem State.

Erweiterungen A1:
  - Management-Felder (Router → Planner → Manager)
  - pending_writes (Salienz/Planner → Dispatcher → Manager-Plugins)
"""

from typing import TypedDict

from graph.context_entry import ContextEntry
from graph.personality import Personality, InternalPersonality


class TribunalVote(TypedDict):
    """Einzelnes Votum eines Tribunal-Agenten."""
    agent:     str    # jurist | psychologe | ethik
    vote:      str    # ok | warnung | ablehnen
    reasoning: str


class PendingWrite(TypedDict):
    """Geplante DB-Operation — wird vom Dispatcher an Manager verteilt."""
    ziel:          str    # kzg | fakten | timeline | notizen | ...
    aktion:        str    # create | update | delete | upsert
    daten:         dict   # Manager-spezifische Nutzdaten
    beschreibung:  str    # Menschenlesbar, für Logging/Responder


class ConversationState(TypedDict):
    """Zustand, der durch alle Nodes fließt."""

    # ── Eingang ──────────────────────────────
    user_prompt:    str
    user_id:        str
    character_id:   str      # Aktiver Charakter (z.B. "nova") — bildet mit user_id den Session-Key
    turn_id:        str      # UUID4-Hex zur Korrelation von HumanGraph- und CharacterGraph-Lauf am selben Konversations-Turn. Befüllt im /chat-Handler.
    system_prompt:  str
    temperature:    float

    # ── Event Context ────────────────────────
    event_source:   str      # "user" | "character" — controls EI-Calc empathy switch
    event_payload:  dict     # Free dict from the event (remaining tasks, pending_agent, etc.)

    # ── Personality-Klassen (PFAD2-PERZEPTION-FIX Phase 3) ──
    # Single source of truth fuer die neun EI-Dimensionen plus
    # Charakter-Hashes. Loesen die frueheren flachen Keys ab.
    external: Personality          # Gegenüber im Gespräch (User, oder bei Pixie: Nova)
    internal: InternalPersonality  # Nova selbst

    # ── Rollen-Marker fuer Graph-Switches ─────
    perzeption_rolle:     str     # "user" (Default) oder "assistant"
    # Welcher Graph ruft den EI-Calc auf: "user" (HumanGraph) oder "character" (CharacterGraph)
    ei_calc_rolle: str
    # Welcher Graph laeuft gerade: "human" | "character" | "agent".
    #
    # Warum eigenstaendig und nicht aus ei_calc_rolle abgeleitet: Der AgentGraph
    # ist Novas Perspektive (ei_calc_rolle="character", damit beobachter
    # "assistant" wird), bewertet aber einen REIZ wie der HumanGraph — er hat
    # keinen Responder und damit nie eine Reaktion. Wer beides aus einem Marker
    # liest, bekommt fuer den AgentGraph zwangslaeufig einen der beiden Faelle
    # falsch. Gemessen 26.07.2026: Der Salienz-Node bewertete im AgentGraph
    # durchgaengig eine leere Zeichenkette (bewertungs_laenge=0).
    #
    # Gelesen von: salience (was wird bewertet), enricher (quelle im
    # pipeline_log), dispatcher (schreibt der Lauf den Session-Turn).
    graph_rolle: str

    # ── Router ───────────────────────────────
    needs_memory:   bool
    needs_web:      bool
    needs_timeline: bool
    timeline_query: dict    # {"type": "range|search|store", ...}
    momentum:       str     # low | mid | high — Gesprächsdynamik

    # ── Management-Routing (Router → Planner) ─
    management_action:     str  # create | update | delete | read | "" (leer = kein Management)
    management_target:     str  # "Einkaufsliste", "Zahnarzttermin", etc.
    management_target_typ: str  # "titel" | "inhalt" | "thema" — wie der User sucht

    # ── Enricher ─────────────────────────────
    memory_context:    str
    memory_entries:    list[ContextEntry]   # Strukturierte Eintraege (vor Reducer-Dedup, vor Formatter)
    lzg_resonanz: dict | None  # Assoziative Spreading-Resonanz (Synapsen §8.4.2): Enricher schreibt {anker_anzahl, sprung_tiefe, cluster, nova_sektor, erinnerungen[]}, Reducer/Formatter lesen. MUSS als Channel deklariert sein — StateGraph(ConversationState) rekonstruiert den State pro Node aus den Channels; ein undeklarierter Key wird am Node-Uebergang (Enricher → Reducer) still verworfen, nicht durchgereicht.
    memory_entries_raw: list[ContextEntry]   # Ungekuerzte Eintraege vor Reducer-Dedup (Debug)
    web_context:       str
    session_turns:     list   # list[dict] — destillierte Turns für den Responder
    user_intentionen:  list   # Intentionen des aktuellen Turns (aus letztem User-Turn)
    raw_turns:         list[dict]    # Ungefilterte Session-Turns (für EI-Calc)
    session_turn_kern: str           # Komprimierter Turn-Inhalt (vom KZG-Agent, für Session-Turn)
    timeline_id:       int | None    # Clipboard: vom TimelineAgent gesetzte ID; vom KzgAgent-magnete_aufloesen-Node uebernommen statt einen eigenen Erinnerungs-Anker anzulegen.

    # Emotionale Intelligenz (EI-Calc → Responder)
    emotions_verlauf:     list    # [{emotion: str, gewicht: float}, ...] — gewichtetes Array

    # Nova-Emotion (Dual-Emotion — EI-Calc → Responder)
    # nova_emotions_vektor wandert in internal.emotion.emotions_vector;
    # diese zwei bleiben flach, weil sie nicht in die Emotion-Klasse passen
    # (Verlauf-Liste mit Empathie-Modulation, Konflikt-Bool).
    nova_emotions_verlauf:  list[dict]   # Novas gewichteter Emotions-Verlauf (mit Empathie)
    nova_emotion_konflikt:  bool         # Empathie-Vektor vs. eigener Zustand

    # ── Planner (Management Plan-Phase) ──────
    management_result:  str
    management_detail:  str
    task_block:         str    # Fertiger [AUFGABE]-Block fuer den Responder (leer = kein Block)
    task_context_cut:   bool   # True = Responder soll Gedaechtnis/Web weglassen

    # ── Responder ────────────────────────────
    response:    str
    model:       str
    token_total: int

    # ── Thinker / Self-Trigger ───────────────
    self_trigger:         bool          # True = Folge-Durchlauf zur Klaerung anfordern. MUSS als Channel deklariert sein — StateGraph rekonstruiert den State pro Node aus den Channels. Ohne Deklaration wird der Wert am Node-Uebergang (Thinker → Tribunal) still verworfen und erreicht das finale Result nie. Live belegt Chat 106.
    self_trigger_payload: dict          # Payload fuer den Folge-Durchlauf (user_prompt, turn_id, ...)

    # ── Tribunal ─────────────────────────────
    tribunal_votes:   list[TribunalVote]
    tribunal_verdict: str   # ok | warnung | ablehnen
    tribunal_summary: str   # Zusammenfassung für Corrector

    # ── Korrektur-Loop ───────────────────────
    correction_round: int
    max_corrections:  int

    # ── Pending Writes (Salienz + Planner → Dispatcher) ──
    pending_writes: list[PendingWrite]

    # ── Agent-System (Epic 11) ───────────────────
    agent_name:    str    # Vom Planner gesetzt — welcher Agent soll arbeiten
    agent_results: list   # Liste von AgentResult-Objekten — Ergebnisse aller Agenten dieses Turns

    # ── Gesprächsvektor (Epic 9) ───────────────────
    gespraechsvektor: str
    gv_detail: dict          # GV4 Debug-Info (Neugier, Luecken, Farbton)

    # ── Drive / Gravitation (Chat 68) ────────────
    aktivierte_ziele:  list[dict]   # Ziele über Gravitationsschwelle [{zielsatz, motivation, gravitation, ...}]
    gravitationsterm:  float        # Salienz-Boost aus Ziel-Gravitation
    emotionale_gravitationspunkte: list[dict]   # Emotional aufgeladene Erinnerungen [{emotion, arousal, gravitation, ...}]
    prompt_embedding:  list[float]  # Embedding des aktuellen User-Prompts (768-dim, vom Enricher gesetzt)

    # ── Interne Anmerkungen (Node-übergreifend) ──
    node_annotations: list[str]
    