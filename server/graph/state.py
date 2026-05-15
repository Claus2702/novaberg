"""
Graph State — Zentrale Datenstruktur für den Gesprächsgraphen.
Jeder Node liest und schreibt auf diesem State.

Erweiterungen A1:
  - Management-Felder (Router → Planner → Manager)
  - pending_writes (Salienz/Planner → Dispatcher → Manager-Plugins)
"""

from typing import TypedDict

from graph.context_entry import ContextEntry


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

    # ── Perzeption ──────────────────────────
    perzeption_rolle:     str     # "user" (Default) oder "assistant"
    # Welcher Graph ruft den EI-Calc auf: "user" (HumanGraph) oder "character" (CharacterGraph)
    ei_calc_rolle: str
    intent:               str     # smalltalk | knowledge | personal | task | creative | meta
    tone:                 str     # empathisch | sachlich | kreativ | direkt
    prompt_thema:         str     # Kurzbeschreibung des Themas (2-5 Worte)
    current_emotion:      str     # Dominante Emotion des aktuellen Prompts
    current_arousal:      float   # Energie-Level: 0.0 (flach) bis 1.0 (maximal)
    beziehungs_dynamik:   str     # "vertrauen", "distanz", "angriff", "hilfesuchend", "dankbar", "neutral"

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
    memory_entries_raw: list[ContextEntry]   # Ungekuerzte Eintraege vor Reducer-Dedup (Debug)
    web_context:       str
    session_turns:     list   # list[dict] — destillierte Turns für den Responder
    gespraechs_modus:  str    # Aktueller Modus aus letzten Turns
    user_intentionen:  list   # Intentionen des aktuellen Turns
    user_emotion:      str    # Emotion des aktuellen Turns
    raw_turns:         list[dict]    # Ungefilterte Session-Turns (für EI-Calc)
    char_hash_dict:    dict          # Charakter-Hash als Dict (für EI-Calc)
    session_turn_kern: str           # Komprimierter Turn-Inhalt (vom KZG-Agent, für Session-Turn)

    # Emotionale Intelligenz (Enricher → Responder)
    emotions_verlauf:     list    # [{emotion: str, gewicht: float}, ...] — gewichtetes Array
    emotions_vektor:      str     # Richtung: "absturz", "spirale", "erholung", etc.
    sprach_stil:          str     # Erkannter Sprachstil ("locker", "formell", "fachlich", "emotional", "jugendlich")
    beziehungs_kontext:   str     # Beziehungsprofil-Text aus dem Charakter-Hash

    # Nova-Emotion (Dual-Emotion Phase 2 — EI-Calc → Responder)
    nova_emotions_verlauf:  list[dict]   # Novas gewichteter Emotions-Verlauf (mit Empathie)
    nova_emotions_vektor:   str          # Novas Emotions-Vektor (Richtung)
    nova_emotion_konflikt:  bool         # Empathie-Vektor vs. eigener Zustand

    # Novas eigener Charakter (Enricher → Responder)
    nova_kern:            str     # Novas gewachsene Persönlichkeit (kern_hash der Assistentin, ASSISTANT_USER_ID)
    nova_beziehung:       str     # Novas Bild vom Nutzer (beziehungsprofil der Assistentin, ASSISTANT_USER_ID)
    nova_adaptiv:         str     # Novas aktuelle Themen (adaptiv_hash der Assistentin, ASSISTANT_USER_ID)
    nova_intentionen:     str     # Novas Kommunikationsstil (intentions_profil der Assistentin, ASSISTANT_USER_ID)
    nova_emotions:        str     # Novas emotionale Grundstimmung (emotions_profil der Assistentin, ASSISTANT_USER_ID)

    # ── Planner (Management Plan-Phase) ──────
    management_result:  str
    management_detail:  str
    task_block:         str    # Fertiger [AUFGABE]-Block fuer den Responder (leer = kein Block)
    task_context_cut:   bool   # True = Responder soll Gedaechtnis/Web weglassen

    # ── Responder ────────────────────────────
    response:    str
    model:       str
    token_total: int

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

    # ── Charakter-Identität + Direktiven ────────────
    charakter_anweisungen: list[str]        # Aktive Charakter-Anweisungen
    direktiven: list[dict]                   # Aktive Direktiven [{"anweisung": "...", "kontext": "..."}]

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
    