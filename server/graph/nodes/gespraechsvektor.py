"""
Gespraechsvektor Node — Antizipiert die Richtung des Gespraechs.

Schlanker Orchestrator: Berechnet die Vektorlaenge, holt die zweite
Wissensquelle und assembliert den LLM-Prompt. Alle EI-Berechnungen
(Farbton, Neugier, Wissensluecken, Dreischicht) sind in server/ei/
ausgelagert.

Zweite Wissensquelle seit Chat 115: die Spreading-Erinnerungen des
Enrichers (`_resonanz_kontext_laden`). Davor der Entity-Hop ueber die
`fakten`-Tabelle — der schlaeft, bis M2.5b sie wieder befuellt; die
Begruendung steht am Block ueber `_entity_kontext_laden`.

Konzept: novaberg-gv-strategie_k.md
"""

import logging

import psycopg2

from config import (
    POSTGRES_URL,
    PROMPTS,
    get_node_config,
    GV_LAENGE_MODUS_DELTA,
    GV_STRATEGIE_MIN_LAENGE,
)
from graph.state import ConversationState
from memory.pipeline_log import log_fehler
from memory.session import format_session_turns_numbered
from services.model_services import model_service, ChatRequest

from ei.utils import POSITIVE_EMOTIONEN, NEGATIVE_EMOTIONEN, modus_pruefen
from ei.farbton import farbton_berechnen
from ei.neugier import aufnahmebereitschaft_berechnen
from ei.wissensluecken import wissensluecken_finden
from ei.dreischicht import (
    achsen_berechnen,
    sektor_bestimmen,
    repertoire_laden,
    charakter_gewichtung_berechnen,
    dreischicht_prompt_bauen,
    gv_output_parsen,
    korridor_pruefen,
)

logger = logging.getLogger("ki_server.gespraechsvektor")


# ─────────────────────────────────────────────
# Skip-Check
# ─────────────────────────────────────────────

def _ist_skip(state: ConversationState) -> bool:
    """Prueft ob der GV-Node uebersprungen werden soll.

    Nur bei reiner Begruessung oder Meta-Operationen.
    Management-Intents werden NICHT uebersprungen —
    auch bei Tasks kann Nova vorausdenken (Zahnarzt → Metzgerei).
    """
    external = state.get("external")
    intent: str = external.emotion.intent if external else ""
    if intent in ("begruessung", "meta", "system"):
        return True
    return False


# ─────────────────────────────────────────────
# Laengenberechnung aus EI-Dimensionen
# ─────────────────────────────────────────────

def _vektor_laenge_berechnen(state: ConversationState) -> int:
    """Berechnet die maximale Vektorlaenge aus den 8 EI-Dimensionen.

    Deterministisch (Python). Das LLM darf kuerzer, aber nicht laenger.
    Hartes Limit: 3 Schritte (Cognitive Load Theory).

    Faktoren:
      - Emotion (positiv/negativ) + Arousal → Grundlaenge
      - Beziehungsdynamik (Vertrautheit) → Erhoehung
      - Modus → Zu-/Abschlag aus GV_LAENGE_MODUS_DELTA (alle Modi des Kanons)
      - Sprachstil (locker/formell) → Feintuning
      - Emotions-Vektor (Krise) → Notbremse auf 0
    """
    external = state.get("external")
    arousal:  float = external.emotion.arousal              if external else 0.5
    emotion:  str   = external.emotion.emotion              if external else "neutral"
    modus:    str   = external.emotion.mode                 if external else "alltag"
    dynamik:  str   = external.emotion.relationship_dynamic if external else "neutral"
    stil:     str   = external.emotion.language_style       if external else "neutral"
    vektor:   str   = external.emotion.emotions_vector      if external else ""

    # Krise → sofort 0 (nur Empathie, keine Antizipation)
    if vektor in ("spirale", "absturz") and arousal >= 0.7:
        logger.info("GV-Laenge: 0 (Krise — spirale/absturz bei hohem Arousal)")
        return 0

    laenge: float = 1.0

    # Positive Emotion + Arousal → mehr Spruenge
    if emotion in POSITIVE_EMOTIONEN:
        laenge += 0.5 + (arousal * 0.5)
    elif emotion in NEGATIVE_EMOTIONEN:
        laenge -= arousal * 0.5

    # Vertrautheit erhoeht die erlaubte Laenge
    if dynamik == "vertrauen":
        laenge += 0.5
    elif dynamik == "distanz":
        laenge -= 0.5

    # Fachliche Komplexitaet bremst, assoziative Register erlauben mehr.
    # Tabelle statt if/elif: Sie deckt alle zehn Modi aus MODUS_KANON ab, und
    # ein fehlender Eintrag faellt im Test auf statt still auf 0.0.
    modus_pruefen(modus, "GV-Laenge")
    laenge += GV_LAENGE_MODUS_DELTA.get(modus, 0.0)

    # Lockerer Stil erlaubt groessere Spruenge
    if stil == "locker":
        laenge += 0.3
    elif stil == "formell":
        laenge -= 0.2

    ergebnis: int = max(0, min(3, round(laenge)))
    logger.info(
        f"GV-Laenge: {ergebnis} "
        f"(emotion={emotion}, a={arousal:.2f}, modus={modus}, "
        f"dynamik={dynamik}, stil={stil}, vektor={vektor})"
    )
    return ergebnis


# ─────────────────────────────────────────────
# Entity-Hop ueber Fakten-Tabelle
# ─────────────────────────────────────────────

def _resonanz_kontext_laden(state: ConversationState) -> str:
    """Formatiert die Spreading-Erinnerungen des Enrichers fuer den GV-Prompt.

    Dies ist die zweite Wissensquelle des GV-Nodes — die Stelle, an der er
    erfaehrt, was zum aktuellen Thema schon erlebt wurde. Bis Chat 115 kam
    sie aus der `fakten`-Tabelle (`_entity_kontext_laden`, direkt darunter,
    seither schlafend); warum sie umgehaengt wurde, steht dort.

    Die Quelle ist `state["lzg_resonanz"]`, das der Enricher legt. Sie ist
    bereits eine Zwei-Stufen-Traversierung im Sinn des Konzepts, nur ueber
    den Erinnerungs- statt den Faktengraphen:

      Schale 0 — Anker aus der Cosine-Suche ueber `lzg_knoten`
      Schale 1+ — Nachbarn entlang `lzg_kanten` (Spreading-Activation)

    Der GV-Node fragt hier bewusst **nicht** selbst die Datenbank. Zwei
    Abfragen mit zwei verschiedenen Ankern in einem Turn waeren zwei
    Wahrheiten ueber dasselbe Gespraech — die Fehlerklasse, die dieses
    Projekt mehrfach Arbeit gekostet hat. Der Enricher laeuft ohnehin vor
    dem GV-Node (character_graph.py: enricher → … → gv_node).

    Vorbedingung: keine. Fehlt `lzg_resonanz` oder ist es leer, ist das ein
    legitimer Leerfall (Cold-Start, Enricher ohne Gedaechtnis-Zweig).
    Nachbedingung: nicht-leerer Rueckgabewert genau dann, wenn mindestens
    eine Erinnerung einen nicht-leeren `inhalt` hatte.
    Fehlerfaelle: Erinnerungen ohne `inhalt` werden benannt uebersprungen —
    ein Knoten ohne Text ist ein Defekt der Schreibseite, kein Leerfall.
    """

    # ── Eingabe-Validierung ─────────────────────
    resonanz: dict = state.get("lzg_resonanz") or {}
    erinnerungen: list[dict] = resonanz.get("erinnerungen") or []

    if not erinnerungen:
        logger.info(
            "GV-Resonanz: keine Erinnerungen im lzg_resonanz (Cluster '%s') "
            "— leerer Kontext",
            resonanz.get("cluster", ""),
        )
        return ""

    # ── Verarbeitung ────────────────────────────
    zeilen:      list[str] = []
    ohne_inhalt: list[int] = []

    for erinnerung in erinnerungen:
        inhalt: str = (erinnerung.get("inhalt") or "").strip()
        if not inhalt:
            ohne_inhalt.append(erinnerung.get("knoten_id", -1))
            continue

        # Die Schale sagt, wie die Erinnerung erreicht wurde: 0 ist der
        # direkte Treffer auf das aktuelle Thema, alles darueber wurde ueber
        # eine Assoziation gefunden. Der Unterschied gehoert in den Prompt —
        # sonst liest das LLM einen Nachbarn zweiter Ordnung als Kernbezug.
        schale: int = erinnerung.get("schale", 0)
        herkunft: str = "direkt zum Thema" if schale == 0 else f"assoziiert ueber {schale} Sprung(e)"

        themen_roh = erinnerung.get("themen") or []
        themen: str = ", ".join(str(t) for t in themen_roh if t)

        zeile: str = f"  {inhalt} ({herkunft}"
        if themen:
            zeile += f"; Themen: {themen}"
        emotion: str = (erinnerung.get("emotion") or "").strip()
        if emotion:
            zeile += f"; Faerbung: {emotion}"
        zeile += ")"
        zeilen.append(zeile)

    if ohne_inhalt:
        # Kein Leerfall: lzg_knoten ohne Text ist ein Schreibseiten-Defekt.
        # Den Wert nennen, nicht die Anzahl (Arbeitsweise §7).
        logger.error(
            "GV-Resonanz: %d Erinnerung(en) ohne Inhalt uebersprungen "
            "(knoten_ids: %s)",
            len(ohne_inhalt), ohne_inhalt,
        )

    # ── Ausgabe-Verifikation ────────────────────
    if not zeilen:
        logger.error(
            "GV-Resonanz: %d Erinnerung(en) geliefert, aber keine mit Inhalt "
            "— leerer Kontext trotz gefuellter Resonanz",
            len(erinnerungen),
        )
        return ""

    resonanz_text: str = "\n".join(zeilen)
    logger.info(
        "GV-Resonanz: %d Erinnerung(en) in den Prompt (Cluster '%s', "
        "Schalen: %s)",
        len(zeilen), resonanz.get("cluster", ""),
        [e.get("schale") for e in erinnerungen],
    )
    return resonanz_text


# ─────────────────────────────────────────────
# Entity-Hop ueber die Fakten-Tabelle — SCHLAFEND seit Chat 115
# ─────────────────────────────────────────────
#
# Diese Funktion hat KEINEN AUFRUFER und ist kein toter Code, den jemand
# vergessen hat. Sie wartet auf eine Datenquelle, die es derzeit nicht gibt.
#
# WARUM SIE SCHLAEFT (gemessen 28.07.2026):
#   Die `fakten`-Tabelle hat 0 Zeilen und keinen Produzenten. Die Tripel-
#   Extraktion wurde mit Synapsen P4 aus der Promotion herausgenommen —
#   Festlegung K2 in novaberg-memory-synapsen-p4-entscheidungen_k.md:
#   "Tripel-Extraktion entfaellt komplett in P4 ... Funktionalitaets-Bruch
#   zwischen P4 und M2.5b wird akzeptiert (keine neuen Tripel, ...,
#   eingefrorener Fakten-Bestand)."
#   Der eingefrorene Bestand (411 Fakten) ist beim Reset am 27.07.2026
#   weggefallen. Aus "eingefroren" wurde "leer" — eine Folge, die in der
#   Festlegung nicht vorgesehen war.
#
#   Unabhaengig davon trifft Hop 1 auch dann nicht: Der Schluessel ist eine
#   Themenphrase (`prompt_topic`, 2-5 Woerter), die Entitaetsnamen sind
#   Eigennamen (65 von 89 einwortig). Gemessen sind beide ILIKE-Richtungen
#   0 Treffer. Der zweite Zweig (`zusammenfassung ILIKE`) ist zusaetzlich
#   ohne Substrat: 88 von 89 Entitaeten haben keine Zusammenfassung, weil
#   der Magnet-Pfad nur Name und Typ setzt.
#
# WANN SIE AUFWACHT:
#   Mit M2.5b (FaktenAgent als eigenstaendige Fachabteilung, analog
#   TimelineAgent) — im Backlog gefuehrt. Vorbedingung laut Synapsen-Konzept
#   §3.2: der LZG-Kern steht. Wer sie reaktiviert, repariert vorher Hop 1;
#   der Schluessel-Mismatch bleibt sonst bestehen, auch mit vollen Tabellen.
#
# Details und Messungen: GV-ENTITY-HOP-FINDET-NICHTS in novaberg-bugs.md.
# ─────────────────────────────────────────────

def _entity_kontext_laden(state: ConversationState) -> str:
    """Laedt verwandte Entitaeten ueber die Fakten-Kanten. SCHLAEFT — siehe Block darueber.

    Hop 1: Schluesselentitaet → deren Fakten
    Hop 2: Verknuepfte Entitaeten → deren Fakten (Orts-/Themen-Verknuepfung)

    Nur Entitaet→Entitaet-Fakten (objekt_id gesetzt): auf einen objekt_wert
    kann nicht weitergehuepft werden, Wert-Fakten bleiben daher aussen vor.

    Gibt formatierten Text zurueck fuer den LLM-Prompt. Leerfaelle (kein
    Schluessel, keine Entitaeten, keine Fakten) sind legitim und liefern "";
    DB-Fehler sind Programmier-/Infrastrukturfehler und krachen laut
    (logger.error + Forensik), statt als Warning unterzugehen.
    """
    user_id: str = state.get("user_id", "")
    # Schluessel: management_target (bei Tasks) oder prompt_topic (bei Chat)
    external = state.get("external")
    management_target: str = state.get("management_target", "")
    prompt_thema:      str = external.emotion.prompt_topic if external else ""
    schluessel:        str = management_target or prompt_thema

    if not schluessel or not schluessel.strip():
        logger.debug("GV-Entity-Hop: kein Schluessel (weder management_target noch prompt_topic) — uebersprungen")
        return ""

    conn = None
    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        # --- Hop 1: Entitaeten zum Schluessel finden ---
        cursor.execute(
            """
            SELECT id, name, typ, zusammenfassung
            FROM entitaeten
            WHERE user_id = %s AND aktiv = TRUE
              AND (name ILIKE %s OR zusammenfassung ILIKE %s)
            LIMIT 5
            """,
            (user_id, f"%{schluessel}%", f"%{schluessel}%"),
        )
        hop1_entitaeten: list[tuple] = cursor.fetchall()

        if not hop1_entitaeten:
            logger.info("GV-Entity-Hop: keine Entitaeten zum Schluessel '%s' — leerer Kontext", schluessel)
            return ""

        hop1_ids: list[int] = [e[0] for e in hop1_entitaeten]

        # --- Fakten zu Hop-1-Entitaeten laden ---
        cursor.execute(
            """
            SELECT e1.name, f.attribut, e2.name, e2.id, e2.zusammenfassung
            FROM fakten f
            JOIN entitaeten e1 ON f.subjekt_id = e1.id
            JOIN entitaeten e2 ON f.objekt_id = e2.id
            WHERE f.user_id = %s AND f.aktiv = TRUE
              AND (f.subjekt_id = ANY(%s) OR f.objekt_id = ANY(%s))
            LIMIT 20
            """,
            (user_id, hop1_ids, hop1_ids),
        )
        hop1_fakten: list[tuple] = cursor.fetchall()

        # --- Hop 2: Verknuepfte Entitaeten → deren Fakten ---
        hop2_ids: list[int] = list({f[3] for f in hop1_fakten} - set(hop1_ids))
        hop2_fakten: list[tuple] = []

        if hop2_ids:
            cursor.execute(
                """
                SELECT e1.name, f.attribut, e2.name, e2.id, e2.zusammenfassung
                FROM fakten f
                JOIN entitaeten e1 ON f.subjekt_id = e1.id
                JOIN entitaeten e2 ON f.objekt_id = e2.id
                WHERE f.user_id = %s AND f.aktiv = TRUE
                  AND (f.subjekt_id = ANY(%s) OR f.objekt_id = ANY(%s))
                LIMIT 20
                """,
                (user_id, hop2_ids, hop2_ids),
            )
            hop2_fakten = cursor.fetchall()

    except psycopg2.Error as fehler:
        # Kein Laufzeitzufall: UndefinedColumn & Co. sind Programmierfehler,
        # Verbindungsfehler Infrastrukturdefekte. Laut protokollieren
        # (Fail loud), der Turn laeuft ohne Entity-Kontext weiter —
        # gleiches Muster wie turn_roh im Dispatcher.
        logger.error(
            "GV-Entity-Hop: DB-Zugriff fehlgeschlagen (Schluessel '%s'): %s",
            schluessel, fehler, exc_info=True,
        )
        log_fehler(
            turn_id      = state.get("turn_id", ""),
            node         = "gespraechsvektor",
            quelle       = "fakten",
            inhalt       = {
                "grund":      "entity_hop_db_fehler",
                "fehler":     str(fehler),
                "schluessel": schluessel,
            },
            user_id      = user_id,
            character_id = state.get("character_id", ""),
        )
        return ""
    finally:
        if conn is not None:
            conn.close()

    # --- Formatieren ---
    alle_fakten: list[tuple] = hop1_fakten + hop2_fakten
    if not alle_fakten:
        logger.info("GV-Entity-Hop: 0 Fakten zu Schluessel '%s' — leerer Kontext", schluessel)
        return ""

    # Deduplizieren (gleiche Kante nicht doppelt)
    gesehen: set[str] = set()
    zeilen: list[str] = []
    for subjekt, attribut, objekt, _, zusammenfassung in alle_fakten:
        kante: str = f"{subjekt}|{attribut}|{objekt}"
        if kante in gesehen:
            continue
        gesehen.add(kante)
        zeile: str = f"  {subjekt} → {attribut} → {objekt}"
        if zusammenfassung:
            zeile += f" ({zusammenfassung})"
        zeilen.append(zeile)

    entity_text: str = "\n".join(zeilen)
    logger.info("GV-Entity-Hop: %d Fakten geladen (Schluessel: '%s')", len(zeilen), schluessel)
    return entity_text


# ─────────────────────────────────────────────
# LLM-Call: Hypothese destillieren
# ─────────────────────────────────────────────

def _hypothese_destillieren(
    state:             ConversationState,
    max_laenge:        int,
    resonanz_kontext:  str,
    farbton:           str = "",
    wissensluecken:    list[dict] | None = None,
    strategie_aktiv:   bool = False,
    dreischicht_block: str = "",
) -> tuple[str, dict]:
    """Destilliert die Gespraechsvektor-Hypothese via LLM.

    Input: Session-Turns, Emotion, Charakter, Resonanz-Kontext
    Output: Natuerlichsprachliche Hypothese (2-4 Saetze) + geparste Felder.
    """
    # Session-Turns aufbereiten (letzte 8)
    session_turns: list[dict] = state.get("session_turns", [])
    if session_turns:
        # Nur die letzten 8 Turns fuer den Vektor
        relevante_turns: list[dict] = session_turns[-8:]
        verlauf_text: str = format_session_turns_numbered(relevante_turns)
    else:
        verlauf_text = "(Erster Turn — kein Verlauf)"

    # Emotions-Kontext (User-Sicht aus external)
    external = state.get("external")
    emotion:     str   = external.emotion.emotion              if external else "neutral"
    arousal:     float = external.emotion.arousal              if external else 0.5
    vektor:      str   = external.emotion.emotions_vector      if external else ""
    modus:       str   = external.emotion.mode                 if external else "alltag"
    dynamik:     str   = external.emotion.relationship_dynamic if external else "neutral"
    intentionen: list  = state.get("user_intentionen", [])
    user_prompt: str   = state.get("user_prompt", "")

    # Charakter (Nova-Linse aus internal.character)
    internal = state.get("internal")
    nova_kern:      str = internal.character.core         if internal else ""
    nova_beziehung: str = internal.character.relationship if internal else ""

    # --- System-Prompt ---
    system_parts: list[str] = [PROMPTS["gv.identity"]]

    # Novas Charakter als Linse
    if nova_kern:
        system_parts.append(
            PROMPTS["gv.charakter"].format(nova_kern=nova_kern)
        )
        if nova_beziehung:
            system_parts.append(
                f"Beziehung zum Nutzer:\n{nova_beziehung}"
            )

    # Aktivierte Ziele als innere Gedanken (Drive)
    aktivierte_ziele: list[dict] = state.get("aktivierte_ziele", [])

    if aktivierte_ziele:
        gedanken_zeilen: list[str] = [
            f"- {z['zielsatz']}" for z in aktivierte_ziele[:3]  # Max 3 Ziele
        ]
        gedanken_block: str = (
            "\n\n[GEDANKEN]\n"
            "Gedanken, die dir gerade durch den Kopf gehen:\n"
            + "\n".join(gedanken_zeilen)
        )
        system_parts.append(gedanken_block)

        logger.info(
            f"GV: {len(aktivierte_ziele)} aktivierte Ziele als [GEDANKEN]-Block eingefügt"
        )

    # Situativer Farbton (kommt als Parameter, nicht mehr hier berechnet)
    farbton_block: str = f"\n\n[SITUATION]\n{farbton}" if farbton else ""

    system_parts.append(
        PROMPTS["gv.task"].format(
            max_laenge=max_laenge,
            strategie_block=PROMPTS["gv.strategie"] if strategie_aktiv else (
                "Beschreibe die LANDSCHAFT — nicht die Route.\n"
                "Beschreibe WAS IST und WAS KOMMT — nicht was Nova tun soll."
            ),
        ) + farbton_block
    )

    if dreischicht_block:
        system_parts.append(dreischicht_block)

    if strategie_aktiv:
        logger.info("GV3: Strategie-Prompt eingefuegt (Laenge >= GV_STRATEGIE_MIN_LAENGE)")

    system_prompt: str = "\n\n".join(system_parts)

    # --- User-Message ---
    user_parts: list[str] = []

    user_parts.append(
        f"[GESPRAECHSVERLAUF]\n{verlauf_text}"
    )

    user_parts.append(
        f"[AKTUELLER PROMPT]\n{user_prompt}"
    )

    user_parts.append(
        f"[EMOTIONALER ZUSTAND]\n"
        f"Emotion: {emotion} (Arousal: {arousal:.0%})\n"
        f"Vektor: {vektor or 'keiner'}\n"
        f"Modus: {modus}\n"
        f"Beziehung: {dynamik}\n"
        f"Intentionen: {', '.join(intentionen) if intentionen else 'keine'}"
    )

    if resonanz_kontext:
        # Der Blockname sagt, was die Quelle ist. Er hiess bis Chat 115
        # [VERWANDTE FAKTEN] und versprach "bekanntes Wissen ueber Personen,
        # Orte und Vorlieben" — das war der Faktengraph. Diese Erinnerungen
        # sind episodisch: was erlebt wurde, nicht was der Fall ist. Ein
        # Block, der das Falsche behauptet, laesst das LLM sie als gesicherte
        # Auskunft lesen.
        user_parts.append(
            f"[VERWANDTE ERINNERUNGEN]\n"
            f"Woran dieses Thema anknuepft — Erlebtes, keine gesicherten Fakten:\n"
            f"{resonanz_kontext}"
        )

    # Gedaechtnis-Kontext (KZG + LZG + Notizen, vom Enricher geladen)
    # Bewusst deaktiviert: GV-Node hat eigene Kontextquellen (Entity-Hops,
    # Wissensluecken) und braucht den Enricher-Dump nicht — entlastet Prompt.
    # memory_context: str = state.get("memory_context", "")
    # if memory_context:
    #     user_parts.append(
    #         f"[GEDAECHTNIS]\n"
    #         f"{memory_context}"
    #     )

    # Wissensluecken (GV4) — nur wenn vorhanden
    if wissensluecken:
        luecken_zeilen: list[str] = []
        for luecke in wissensluecken:
            zeile: str = (
                f"- {luecke['konzept'][:120]}"
                f" (Quelle: {luecke['quelle']}, Relevanz: {luecke['relevanz']:.2f})"
            )
            luecken_zeilen.append(zeile)
        user_parts.append(
            "[WISSENSLUECKEN]\n"
            "Semantisch nahe, aber noch nicht besprochen:\n"
            + "\n".join(luecken_zeilen)
            + "\n\nDu kannst diese Konzepte als naechsten Gedankenschritt "
            "einbringen — aber nur wenn sie zum Gespraechsfluss passen."
        )
        logger.info(f"GV4: {len(wissensluecken)} Luecken in Prompt eingefuegt")

    user_message: str = "\n\n".join(user_parts)

    logger.info(
        f"GV-Prompt: System={len(system_prompt)} Zeichen, "
        f"User={len(user_message)} Zeichen"
    )

    # --- LLM-Call ---
    node_cfg: dict = get_node_config("gespraechsvektor")

    logger.debug(
        "=== GV LLM-INPUT ===\n"
        "═══ SYSTEM ═══\n%s\n\n"
        "═══ USER ═══\n%s\n"
        "=== ENDE GV LLM-INPUT ===",
        system_prompt,
        user_message,
    )

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G2) ──
    # _hypothese_destillieren() laeuft im CharacterGraph, der in
    # services/event_consumer.py via asyncio.to_thread(_graph_streamen, ...)
    # in einem Worker-Thread laeuft. Kein Event-Loop im aufrufenden Thread →
    # submit_sync nutzt die Bruecke ueber asyncio.run_coroutine_threadsafe
    # in den Haupt-Loop des Workers (Loop-Binding-Lesson).
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": user_message}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.6),
        max_output_tokens = node_cfg.get("max_output_tokens", 512),
        caller            = "gespraechsvektor",
    )
    response = model_service.chat.submit_sync(chat_request)

    hypothese: str = response.text.strip()
    logger.info(f"GV-Hypothese ({response.token_total} Tokens): {hypothese[:500]}...")
    gv_parsed: dict = gv_output_parsen(hypothese)
    return hypothese, gv_parsed


# ─────────────────────────────────────────────
# Node-Funktion (Einsprungpunkt fuer den Graph)
# ─────────────────────────────────────────────

def gespraechsvektor(state: ConversationState) -> ConversationState:
    """Gespraechsvektor-Node: Antizipiert die Richtung des Gespraechs.

    Sequentieller Ablauf:
      1. Skip-Check (Begruessung/Meta → durchreichen)
      2. Laenge aus EI-Dimensionen berechnen (Python, deterministisch)
      3. Resonanz-Kontext aus den Spreading-Erinnerungen des Enrichers
      3b. Farbmisch-System (8 Dimensionen → Landschaftsbeschreibung)
      3c. Effektive Neugier berechnen (6 Saeulen)
      3d. Wissensluecken finden (DB-Queries, Relevanz-Berechnung)
      3e. Dreischicht: Achsen → Sektor → Cluster → Repertoire
      4. LLM-Call → Hypothese + Strategie destillieren
      5. Ergebnis + Debug-Info in State schreiben
    """
    logger.info("Gespraechsvektor: Analyse gestartet")

    # 1. Skip?
    if _ist_skip(state):
        logger.info("Gespraechsvektor: Skip (Begruessung/Meta)")
        state["gespraechsvektor"] = ""
        return state

    # 2. Laenge berechnen
    max_laenge: int = _vektor_laenge_berechnen(state)

    if max_laenge == 0:
        logger.info("Gespraechsvektor: Laenge 0 — kein Vorausdenken")
        state["gespraechsvektor"] = ""
        return state

    # 3. Zweite Wissensquelle: die Spreading-Erinnerungen des Enrichers.
    #    Bis Chat 115 der Entity-Hop ueber `fakten` — umgehaengt, weil die
    #    Tabelle seit Synapsen P4 keinen Produzenten mehr hat (K2).
    resonanz_kontext: str = _resonanz_kontext_laden(state)

    # 3b. Farbton (einmal berechnen, durchreichen)
    farbton: str = farbton_berechnen(state)
    if farbton:
        logger.info(f"GV-Farbton: {farbton}")

    # 3c. GV4: Aufnahmebereitschaft — Novas Faehigkeit, jetzt neugierig zu sein.
    #
    # Sie wird in JEDEM Turn gerechnet, nicht erst ab der Strategie-Laenge.
    # Grund: Sie ist ein Zustand Novas (sechs Saeulen aus Emotion, Arousal,
    # Stimmungsrichtung, Modus, Dynamik, Stil) und keine Funktion der
    # Vektorlaenge. Der Wert 0.00 ist im Konzept fuer die Krise reserviert —
    # ein neutraler Zustand liegt bei ~0.56. Stand die Rechnung hinter der
    # Laengen-Schwelle, trug gv_detail bei jedem kurzen Vektor eine 0.0, die
    # von einer gemessenen Krise nicht zu unterscheiden war (Chat 116,
    # gemessen: 4 von 8 Laeufen; lesson_l_default-wie-fehlschlag).
    #
    # Die Rechnung ist rein: State-Lesen, Tabellen-Lookups, Arithmetik —
    # keine DB, kein LLM. Die Laengen-Schwelle bleibt dort, wo sie hingehoert,
    # naemlich an der teuren Luechensuche eine Zeile weiter unten.
    strategie_aktiv:    bool       = max_laenge >= GV_STRATEGIE_MIN_LAENGE
    wissensluecken:     list[dict] = []

    aufnahmebereitschaft: float = aufnahmebereitschaft_berechnen(state)

    # 3d. GV4: Wissensluecken finden (DB-Queries — nur ab Strategie-Laenge,
    #     und nur wenn ueberhaupt Bereitschaft da ist)
    if strategie_aktiv and aufnahmebereitschaft > 0:
        wissensluecken = wissensluecken_finden(state, aufnahmebereitschaft)

    # 3e. Dreischicht: Achsen → Sektor → Cluster → Repertoire
    achsen: dict = achsen_berechnen(state)
    sektor_index, sektor_name, cluster = sektor_bestimmen(achsen)
    repertoire: dict[str, str] = repertoire_laden(cluster)
    charakter_gewichtung: dict[str, float] = charakter_gewichtung_berechnen(state)
    dreischicht_block: str = dreischicht_prompt_bauen(
        cluster, repertoire, charakter_gewichtung,
    )

    # 4. Hypothese destillieren
    hypothese, gv_parsed = _hypothese_destillieren(
        state, max_laenge, resonanz_kontext,
        farbton=farbton,
        wissensluecken=wissensluecken,
        strategie_aktiv=strategie_aktiv,
        dreischicht_block=dreischicht_block,
    )

    # 4b. Korridor pruefen
    # Python setzt die Leitplanken, das LLM waehlt darin (Konzept §10.1). Ob es
    # das getan hat, hat bis Chat 114 niemand nachgesehen: Eine Strategie, die
    # der Parser nicht lesen konnte oder die im Cluster als unpassend gilt,
    # verschwand als leeres Feld — der Responder bekam eine Landschaft ohne
    # Werkzeug und nichts wies darauf hin.
    korridor_verstoesse: list[dict] = list(gv_parsed.get("verworfen", []))
    korridor_verstoesse.extend(
        korridor_pruefen(gv_parsed, repertoire, cluster)
    )
    for verstoss in korridor_verstoesse:
        logger.error(
            "GV-Korridor: %s '%s' verworfen — %s (Cluster '%s')",
            verstoss["feld"], verstoss["wert"], verstoss["grund"], cluster,
        )

    # 5. State schreiben
    state["gespraechsvektor"] = hypothese

    state["gv_detail"] = {
        # Spruenge (LLM-Output geparst)
        "sprung_1":              gv_parsed.get("sprung_1", ""),
        "sprung_2":              gv_parsed.get("sprung_2", ""),
        "sprung_3":              gv_parsed.get("sprung_3", ""),
        # Dreischicht (LLM waehlt aus Python-Korridor)
        "absicht":               gv_parsed.get("absicht", ""),
        "strategie":             gv_parsed.get("strategie", ""),
        "vehikel":               gv_parsed.get("vehikel", ""),
        "impuls":                gv_parsed.get("impuls", ""),
        # Achsen (Python, deterministisch)
        "achsen":                achsen,
        "sektor_index":          sektor_index,
        "sektor_name":           sektor_name,
        "cluster":               cluster,
        "drive":                 achsen.get("drive", 0.0),
        # Repertoire + Gewichtung (Python)
        "repertoire":            repertoire,
        "charakter_gewichtung":  charakter_gewichtung,
        # Bestehende Felder
        "laenge":                max_laenge,
        "farbton":               farbton,
        # Hiess bis Chat 115 "entity_hops" und trug den Faktengraph-Auszug.
        # Umbenannt mit der Quelle: ein Feldname, der eine Herkunft nennt,
        # die er nicht mehr hat, ist die teuerste Sorte Doku.
        #
        # Das Feld war von seiner Einfuehrung bis Chat 116 schreib-only — es
        # ging nach Redis und ueber GET /drive/gv_detail an den Client, ohne
        # dass es dort jemand las. Deshalb brach die Umbenennung nichts.
        #
        # Seit Chat 116 zeigt client/ui/panels/gv_panel.py es als Sektion
        # "Verwandte Erinnerungen" und liest 'entity_hops' uebergangsweise
        # mit (Redis-Key ohne TTL). Der Schluesselname ist damit ein Vertrag:
        # tests/test_gv_resonanz_kontext.py wird rot, wenn er hier
        # verschwindet — auch im Leerfall, wo er einen leeren String tragen
        # muss und nicht fehlen darf.
        "resonanz_kontext":      resonanz_kontext[:500] if resonanz_kontext else "",
        "aufnahmebereitschaft":     aufnahmebereitschaft,
        "wissensluecken": [
            {
                "konzept":       l["konzept"][:120],
                "quelle":        l["quelle"],
                "relevanz":      round(l["relevanz"], 3),
                "neugier_boost": round(l.get("neugier_boost", 0), 3),
                "register":      round(l.get("register", 1.0), 2),
            }
            for l in wissensluecken
        ],
        "strategie_aktiv":       strategie_aktiv,
        "korridor_verstoesse":   korridor_verstoesse,
    }

    return state
