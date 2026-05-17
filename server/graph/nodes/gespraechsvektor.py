"""
Gespraechsvektor Node — Antizipiert die Richtung des Gespraechs.

Schlanker Orchestrator: Berechnet die Vektorlaenge, laedt Entity-Kontext
und assembliert den LLM-Prompt. Alle EI-Berechnungen (Farbton, Neugier,
Wissensluecken, Dreischicht) sind in server/ei/ ausgelagert.

Konzept: novaberg-gv-strategie_k.md
"""

import logging

import psycopg2

from config import (
    POSTGRES_URL,
    PROMPTS,
    get_node_config,
    GV_STRATEGIE_MIN_LAENGE,
)
from graph.state import ConversationState
from memory.session import format_session_turns_numbered
from services.llm_provider import get_chat_provider

from ei.utils import POSITIVE_EMOTIONEN, NEGATIVE_EMOTIONEN
from ei.farbton import farbton_berechnen
from ei.neugier import effektive_neugier_berechnen
from ei.wissensluecken import wissensluecken_finden
from ei.dreischicht import (
    achsen_berechnen,
    sektor_bestimmen,
    repertoire_laden,
    charakter_gewichtung_berechnen,
    dreischicht_prompt_bauen,
    gv_output_parsen,
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
      - Modus (fachlich/emotional) → Reduktion
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

    # Fachliche Komplexitaet bremst
    if modus == "fachgespraech":
        laenge -= 0.3
    elif modus == "emotional":
        laenge -= 0.2

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

def _entity_kontext_laden(state: ConversationState) -> str:
    """Laedt verwandte Entitaeten ueber die Fakten-Kanten.

    Hop 1: Schluesselentitaet → deren Fakten
    Hop 2: Verknuepfte Entitaeten → deren Fakten (Orts-/Themen-Verknuepfung)

    Gibt formatierten Text zurueck fuer den LLM-Prompt.
    """
    user_id: str = state.get("user_id", "")
    # Schluessel: management_target (bei Tasks) oder prompt_topic (bei Chat)
    external = state.get("external")
    management_target: str = state.get("management_target", "")
    prompt_thema:      str = external.emotion.prompt_topic if external else ""
    schluessel:        str = management_target or prompt_thema

    if not schluessel or not schluessel.strip():
        return ""

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
            conn.close()
            return ""

        hop1_ids: list[int] = [e[0] for e in hop1_entitaeten]

        # --- Fakten zu Hop-1-Entitaeten laden ---
        cursor.execute(
            """
            SELECT e1.name, f.beziehung, e2.name, e2.id, e2.zusammenfassung
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
                SELECT e1.name, f.beziehung, e2.name, e2.id, e2.zusammenfassung
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

        conn.close()

        # --- Formatieren ---
        alle_fakten: list[tuple] = hop1_fakten + hop2_fakten
        if not alle_fakten:
            return ""

        # Deduplizieren (gleiche Kante nicht doppelt)
        gesehen: set[str] = set()
        zeilen: list[str] = []
        for subjekt, beziehung, objekt, _, zusammenfassung in alle_fakten:
            kante: str = f"{subjekt}|{beziehung}|{objekt}"
            if kante in gesehen:
                continue
            gesehen.add(kante)
            zeile: str = f"  {subjekt} → {beziehung} → {objekt}"
            if zusammenfassung:
                zeile += f" ({zusammenfassung})"
            zeilen.append(zeile)

        entity_text: str = "\n".join(zeilen)
        logger.info(f"GV-Entity-Hop: {len(zeilen)} Fakten geladen (Schluessel: '{schluessel}')")
        return entity_text

    except Exception as fehler:
        logger.warning(f"GV-Entity-Hop fehlgeschlagen: {fehler}")
        return ""


# ─────────────────────────────────────────────
# LLM-Call: Hypothese destillieren
# ─────────────────────────────────────────────

def _hypothese_destillieren(
    state:             ConversationState,
    max_laenge:        int,
    entity_kontext:    str,
    farbton:           str = "",
    wissensluecken:    list[dict] | None = None,
    strategie_aktiv:   bool = False,
    dreischicht_block: str = "",
) -> tuple[str, dict]:
    """Destilliert die Gespraechsvektor-Hypothese via LLM.

    Input: Session-Turns, Emotion, Charakter, Entity-Kontext
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

    if entity_kontext:
        user_parts.append(
            f"[VERWANDTE FAKTEN]\n"
            f"Bekanntes Wissen ueber Personen, Orte und Vorlieben des Nutzers:\n"
            f"{entity_kontext}"
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
    provider = get_chat_provider()

    logger.debug(
        "=== GV LLM-INPUT ===\n"
        "═══ SYSTEM ═══\n%s\n\n"
        "═══ USER ═══\n%s\n"
        "=== ENDE GV LLM-INPUT ===",
        system_prompt,
        user_message,
    )

    antwort = provider.chat(
        messages=[{"role": "user", "content": user_message}],
        system=system_prompt,
        temperature=node_cfg.get("temperature", 0.6),
        max_output_tokens=node_cfg.get("max_output_tokens", 512),
        caller="gespraechsvektor",
    )

    hypothese: str = antwort.content.strip()
    logger.info(f"GV-Hypothese ({antwort.token_total} Tokens): {hypothese[:500]}...")
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
      3. Entity-Hop ueber Fakten-Tabelle (Python, DB-Queries)
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

    # 3. Entity-Hop
    entity_kontext: str = _entity_kontext_laden(state)

    # 3b. Farbton (einmal berechnen, durchreichen)
    farbton: str = farbton_berechnen(state)
    if farbton:
        logger.info(f"GV-Farbton: {farbton}")

    # 3c. GV4: Effektive Neugier
    strategie_aktiv:    bool       = max_laenge >= GV_STRATEGIE_MIN_LAENGE
    effektive_neugier:  float      = 0.0
    wissensluecken:     list[dict] = []

    if strategie_aktiv:
        effektive_neugier = effektive_neugier_berechnen(state)

        # 3d. GV4: Wissensluecken finden (nur wenn Neugier > 0)
        if effektive_neugier > 0:
            wissensluecken = wissensluecken_finden(state, effektive_neugier)

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
        state, max_laenge, entity_kontext,
        farbton=farbton,
        wissensluecken=wissensluecken,
        strategie_aktiv=strategie_aktiv,
        dreischicht_block=dreischicht_block,
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
        "entity_hops":           entity_kontext[:500] if entity_kontext else "",
        "effektive_neugier":     effektive_neugier,
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
    }

    return state
