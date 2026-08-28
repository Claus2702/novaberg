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

import json
import logging
from dataclasses import dataclass

import psycopg2

from config import (
    GV_LAENGE_MODUS_DELTA,
    GV_STRATEGIE_MIN_LAENGE,
    POSTGRES_URL,
    PROMPTS,
    get_node_config,
)
from config import (
    redis_client as cfg_redis_client,
)
from ei.dreischicht import (
    achsen_berechnen,
    achsen_fassung,
    charakter_gewichtung_berechnen,
    dreischicht_prompt_bauen,
    gv_output_parsen,
    korridor_pruefen,
    repertoire_laden,
    sektor_bestimmen,
)
from ei.farbton import farbton_berechnen
from ei.initiative import Fuehrung, fuehrung_messen, skalenfassung
from ei.neugier import aufnahmebereitschaft_berechnen
from ei.utils import NEGATIVE_EMOTIONEN, POSITIVE_EMOTIONEN, modus_pruefen
from ei.wissensluecken import wissensluecken_finden
from graph.reiz import reiz_ist_eigener_gedanke, reiz_text
from graph.state import ConversationState, pipeline_quelle
from memory.charakter import initiative_versatz_laden
from memory.pipeline_log import log_berechnung, log_fehler
from memory.session import format_session_turns_numbered
from services.model_services import ChatRequest, EmbedRequest, model_service

logger = logging.getLogger("ki_server.gespraechsvektor")


# ─────────────────────────────────────────────
# Skip-Check
# ─────────────────────────────────────────────

def _ist_skip(state: ConversationState) -> bool:
    """Prueft ob der GV-Node uebersprungen werden soll.

    Nur bei reiner Begruessung oder Meta-Operationen.
    Management-Intents werden NICHT uebersprungen —
    auch bei Tasks kann Nova vorausdenken (Zahnarzt → Metzgerei).

    **Ein eigener Impuls wird nie uebersprungen.** Das Tor liest den Intent
    der NUTZER-Aeusserung; auf einem Impuls-Turn gibt es keine. `db_zugriff`
    setzt dort `external` als Kopie von `internal` (Pixie-Pfad), und der
    Intent beschreibt dann Novas **eigene letzte Antwort** — ein Wert ueber
    den vorigen Turn entscheidet ueber diesen.

    Gemessen am 13.08.2026 ueber einen Tag: **15 von 20** eigenen Impulsen
    fielen so aus dem Vorausdenken, die uebrigen fuenf nicht — allein danach,
    worauf Novas voriger Intent gefallen war. Der Verfasser bekam auf genau
    diesen 15 Turns keinen `[GESPRAECHSVEKTOR]`-Block, waehrend sein Auftrag
    viermal darauf verwies (`novaberg-fundliste.md`, 2026-08-14).

    Die Landschaft steht auch beim Skip — `_gv_detail_bauen` setzt sie auf
    jedem Weg. Was mit dieser Zeile zurueckkommt, ist die Antizipations-
    Haelfte: Strategie, Vehikel, Leitgedanke, Spruenge.

    Vorbedingung: keine. Ohne `external` gilt der leere Intent, also kein Skip.
    Nachbedingung: True genau dann, wenn eine NUTZER-Aeusserung vorliegt und
        ihr Intent in der geschlossenen Menge der drei Marken steht.
    Fehlerfaelle: keine.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Die Herkunftsfrage steht vor der Intent-Frage, weil sie entscheidet, ob
    # der Intent ueberhaupt etwas ueber diesen Reiz aussagt (`graph/reiz.py`).
    if reiz_ist_eigener_gedanke(state):
        logger.info(
            "Gespraechsvektor: eigener Impuls — das Skip-Tor greift nicht, "
            "es liest den Intent der Nutzer-Aeusserung und hier gibt es keine"
        )
        return False

    # ── Verarbeitung / Ausgabe ──────────────────
    external = state.get("external")
    intent: str = external.emotion.intent if external else ""
    return intent in ("begruessung", "meta", "system")


# ─────────────────────────────────────────────
# Laengenberechnung aus EI-Dimensionen
# ─────────────────────────────────────────────

def _ist_krise(state: ConversationState) -> bool:
    """Prueft die Notbremse: Stimmungsvektor im Absturz bei hohem Arousal.

    Eigene Funktion, weil zwei Aufrufer dieselbe Bedingung brauchen und keiner
    von beiden sie ein zweites Mal hinschreiben darf: `_vektor_laenge_berechnen`
    setzt daraufhin die Laenge auf 0, und `gespraechsvektor` muss die Krise vom
    arithmetisch erreichten Nullwert **unterscheiden koennen**. Beides aus einer
    Zeile abzulesen ginge nicht — eine 0 traegt ihren Grund nicht mit sich.

    Vorbedingung: keine. Ohne `external` gelten die Neutralwerte, also keine Krise.
    Nachbedingung: True genau dann, wenn das Konzept "nur Empathie, keine
        Antizipation" verlangt (novaberg-node-gv_k.md §Laengenberechnung).
    Fehlerfaelle: keine.
    """
    external = state.get("external")
    if external is None:
        return False
    return (
        external.emotion.emotions_vector in ("spirale", "absturz")
        and external.emotion.arousal >= 0.7
    )


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

    **Diese Zahl entscheidet ueber das Vorausdenken und ueber nichts sonst.**
    Bis zum 08.08.2026 hing die Landschafts-Ablesung mit an ihr: Bei 0 kehrte
    der Node zurueck, bevor er die Achsen gerechnet hatte. Gemessen ueber 845
    Rohturns fielen dadurch 184 Ablesungen aus, davon 82 von 164 Turns mit
    Beziehungsdynamik `distanz` und **keiner** der 340 mit `neutral` — das
    Messgeraet schaltete sich genau auf der fernen Haelfte der Naehe-Achse ab.
    """
    external = state.get("external")
    arousal:  float = external.emotion.arousal              if external else 0.5
    emotion:  str   = external.emotion.emotion              if external else "neutral"
    modus:    str   = external.emotion.mode                 if external else "alltag"
    dynamik:  str   = external.emotion.relationship_dynamic if external else "neutral"
    stil:     str   = external.emotion.language_style       if external else "neutral"
    vektor:   str   = external.emotion.emotions_vector      if external else ""

    # Krise → sofort 0 (nur Empathie, keine Antizipation)
    if _ist_krise(state):
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
        herkunft: str = (
            "direkt zum Thema" if schale == 0 else f"assoziiert ueber {schale} Sprung(e)"
        )

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
        # Die Zeile nennt die knoten_ids und nicht nur ihre Anzahl — eine
        # Zaehlung macht die Frage "welcher Knoten ist kaputt?" unbeobachtbar.
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
        logger.debug(
            "GV-Entity-Hop: kein Schluessel (weder management_target noch prompt_topic) — "
            "uebersprungen"
        )
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
            logger.info(
                "GV-Entity-Hop: keine Entitaeten zum Schluessel '%s' — leerer Kontext", schluessel
            )
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
    # Der Reiz, aus dem die Landschaft entsteht — auf einem Impuls-Turn ist
    # das Novas eigener Gedanke. Ein leerer Reiz-Platz vermaesse hier die
    # Landschaft eines Turns ohne Gegenstand.
    user_prompt: str   = reiz_text(state)

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

    # Die Sachlage — das sachliche Verstehen des Turns. Sie steht vor dem
    # Farbton: erst was der Fall ist, dann wie es sich anfuehlt.
    sachlage: dict = state.get("sachlage") or {}
    if sachlage.get("gegenstand") or sachlage.get("nutzerziel"):
        from graph.nodes.sachlage import sachlage_block
        system_parts.append("\n\n" + sachlage_block(sachlage))

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


def _vorturn_laden(state: ConversationState) -> tuple[list[float] | None, str]:
    """Holt Embedding und Modus von Novas letzter Antwort fuer die Achse I.

    Der Dispatcher legt den Antworttext ab (`_persist_vorturn`), embeddet ihn
    aber nicht — das laege dort vor dem Broadcast. Hier faellt die Wartezeit
    ohnehin an, also wird hier embeddet.

    Vorbedingung: keine. Fehlt der Key, ist es der erste Turn des Paars.
    Nachbedingung: Entweder ein 768-Vektor und ein Modus, oder (None, "") —
    dann meldet `fuehrung_messen` die betroffenen Masse als fehlend statt sie
    als null zu rechnen.
    Fehlerfaelle: Unlesbarer Key, kaputtes JSON oder ein gescheiterter
    Embed-Call. Alle drei sind laut, keiner reisst den Turn.

    Returns:
        (Embedding der Vorantwort oder None, Modus der Vorantwort oder "").
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")
    if not user_id or not character_id:
        return None, ""

    key: str = f"gv:vorturn:{user_id}:{character_id}"

    try:
        roh = cfg_redis_client.get(key)
    except Exception as fehler:
        logger.error("GV-Initiative: Vorturn nicht lesbar (%s) — %s",
                     key, fehler, exc_info=True)
        return None, ""

    if not roh:
        logger.info("GV-Initiative: kein Vorturn unter %s — erster Turn "
                    "dieses Paars oder Bestand geleert", key)
        return None, ""

    # ── Verarbeitung ────────────────────────────
    try:
        daten: dict = json.loads(roh)
    except json.JSONDecodeError as fehler:
        logger.exception(
            "GV-Initiative: Vorturn unter %s nicht parsebar — %s",
            key, fehler,  # noqa: TRY401  — Blatt-Typ
        )
        return None, ""

    antwort: str = (daten.get("antwort") or "").strip()
    modus:   str = daten.get("modus") or ""

    if not antwort:
        logger.error("GV-Initiative: Vorturn unter %s ohne Antworttext — "
                     "der Themensprung ist fuer diesen Turn nicht messbar", key)
        return None, modus

    try:
        antwort_response = model_service.embed.submit_sync(EmbedRequest(text=antwort))
        embedding: list[float] = antwort_response.embedding
    except Exception as fehler:
        logger.error("GV-Initiative: Embedding der Vorantwort gescheitert — %s",
                     fehler, exc_info=True)
        return None, modus

    # ── Ausgabe-Verifikation ────────────────────
    if not embedding:
        logger.error("GV-Initiative: EmbedWorker lieferte einen leeren Vektor "
                     "fuer die Vorantwort")
        return None, modus

    return embedding, modus


def _initiative_protokollieren(
    state:    ConversationState,
    fuehrung: Fuehrung,
    achsen:   dict,
) -> None:
    """Schreibt Rohwert, Bit und geltende Skalenfassung in einer Zeile.

    **Beides zusammen oder keins von beidem.** Der Rohwert sagt allein nichts
    darueber, was er bedeutet hat: Sobald die Schwelle je Paar erhoben wird,
    verschiebt sich mit jeder Kalibrierung der Punkt, an dem dasselbe Bit
    kippt. Eine Reihe aus Rohwerten ohne ihre Fassung laesst spaeter nicht
    mehr trennen, ob sich Nova bewegt hat oder der Massstab.

    Geschrieben wird `art='berechnung'` mit `node='gespraechsvektor'` — die
    Forensik-Art verfaellt nach der Vorhaltefrist, was hier richtig ist: Die
    Reihe soll die letzten Wochen tragen, nicht die Projektgeschichte.

    Vorbedingung: `fuehrung` und `achsen` stammen aus demselben Turn.
    Nachbedingung: Eine `pipeline_log`-Zeile, oder eine `warning`, wenn das
    Schreiben scheiterte.
    Fehlerfaelle: Forensik-Schreibfehler duerfen den Turn nicht killen —
    gekapselt und als `warning` gemeldet, wie in den uebrigen Nodes. Ein
    fehlender Turn-Bezug ist dagegen ein `error`: Eine Zeile ohne `turn_id`
    laesst sich keiner Messung zuordnen und ist damit wertlos.
    """
    # ── Eingabe-Validierung ─────────────────────
    turn_id: str = state.get("turn_id", "")
    if not turn_id:
        logger.error(
            "Initiative-Protokoll: kein turn_id im State — die Zeile waere "
            "keiner Messung zuzuordnen und wird nicht geschrieben"
        )
        return

    # ── Verarbeitung ────────────────────────────
    inhalt: dict = {
        "rohwert":      fuehrung.rohwert,
        "wert":         fuehrung.wert,
        "versatz":      fuehrung.versatz,
        "bit":          achsen.get("initiative"),
        "m1_roh":       fuehrung.m1_roh,
        "m2_roh":       fuehrung.m2_roh,
        "m3_roh":       fuehrung.m3_roh,
        "wollen":       fuehrung.wollen,
        "bewegung":     fuehrung.bewegung,
        "fehlend":      fuehrung.fehlend,
        "skalenfassung": skalenfassung(),
    }

    # ── Ausgabe-Verifikation ────────────────────
    try:
        log_berechnung(
            turn_id      = turn_id,
            node         = "gespraechsvektor",
            quelle       = "character_graph",
            inhalt       = inhalt,
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
        )
    except Exception as fehler:
        logger.warning(
            f"Initiative-Protokoll nicht geschrieben ({type(fehler).__name__}: "
            f"{fehler}) — der Turn laeuft weiter, die Reihe hat eine Luecke"
        )


# ─────────────────────────────────────────────
# Landschaft — die Lage des Turns, unabhaengig vom Vorausdenken
# ─────────────────────────────────────────────

# Was aus dem Vorausdenken geworden ist. Ein Begleitfeld im Sinn von
# `22_STILLE_FEHLER.md` §3: Ohne es waere eine Landschaft ohne Strategie von
# einer Landschaft mit leerer Strategie nicht zu unterscheiden.
VORAUSDENKEN_GELAUFEN:    str = "gelaufen"
VORAUSDENKEN_SKIP:        str = "skip"
VORAUSDENKEN_KRISE:       str = "krise"
VORAUSDENKEN_LAENGE_NULL: str = "laenge_null"


def _landschaft_protokollieren(
    state:        ConversationState,
    achsen:       dict,
    sektor_index: int,
    sektor_name:  str,
    cluster:      str,
) -> None:
    """Schreibt die Achsen, den Sektor und die geltenden Grenzen in eine Zeile.

    **Das Ergebnis allein ist kein Bestand.** Bis zum 08.08.2026 wurde von der
    Landschaftsbestimmung nur der fertige Cluster haltbar (`haltungsraum`,
    `berechnung`); die sechs Bits, aus denen er entsteht, standen ausschliesslich
    im `gv_detail` und damit in einem Redis-Wert, den der naechste Turn
    ueberschreibt. Eine Abfrage ueber alle `pipeline_log`-Schluessel nach den
    Achsennamen kam an diesem Tag **leer** zurueck.

    Die Folge war keine Luecke in der Doku, sondern ein nicht fahrbares Bauteil:
    Die Justierung der Raumgrenzen (`novaberg-erreichbarkeit_k.md` B4) misst
    „dieselbe Entscheidungsfolge vor und nach der Justierung ueber denselben
    Bestand", und ihre Gegenprobe verlangt, dass unveraenderte Grenzen exakt
    dasselbe Ergebnis liefern. Beides ist ein Nachrechnen ueber gespeicherte
    Eingangsgroessen. Ohne sie kostet jede Grenzvariante einen neuen Messlauf,
    in dem sich ausser den Grenzen auch alles andere geaendert hat.

    **Die geltende Fassung reist mit.** Ein Naehe-Rohwert von 0,48 heisst bei
    Schwelle 0,50 „fern" und bei 0,45 „nah"; ohne die Grenze im selben Eintrag
    ist nach der ersten Justierung nicht mehr trennbar, ob sich Novas Raum
    bewegt hat oder der Massstab — dieselbe Fehlerklasse, gegen die die
    Initiative seit Chat 116 ihre `skalenfassung()` mitschreibt.

    Geschrieben wird auf **jedem** Weg des Nodes, weil diese Funktion aus
    `_lage_vermessen` heraus laeuft und das vor beiden Toren steht. Ein Bestand,
    der die Turns ohne Vorausdenken auslaesst, haette denselben blinden Fleck,
    den B1 gerade beseitigt hat.

    Args:
        state:        Zustand, aus dem Turn- und Paarbezug stammen.
        achsen:       das Dict aus `achsen_berechnen`, roh und binaer.
        sektor_index: 0 bis 63.
        sektor_name:  der Name des Sektors.
        cluster:      die Landschaft.

    Vorbedingung: `state` traegt eine `turn_id`; ohne sie ist die Zeile keiner
        Messung zuzuordnen und wird nicht geschrieben.
    Nachbedingung: Eine `pipeline_log`-Zeile mit `schritt='landschaft'`.
    Fehlerfaelle: Ein Forensik-Schreibfehler darf den Turn nicht toeten —
        gekapselt und als `warning` gemeldet, wie in den uebrigen Knoten.
    """
    # ── Eingabe-Validierung ─────────────────────
    turn_id: str = state.get("turn_id", "")
    if not turn_id:
        logger.error(
            "Landschafts-Protokoll: kein turn_id im State — die Zeile waere "
            "keiner Messung zuzuordnen und wird nicht geschrieben"
        )
        return

    # ── Verarbeitung / Ausgabe ──────────────────
    try:
        log_berechnung(
            turn_id      = turn_id,
            node         = "gespraechsvektor",
            quelle       = pipeline_quelle(state),
            inhalt       = {
                # Die Marke, an der diese Zeile von der Initiative-Zeile
                # desselben Knotens und Turns zu unterscheiden ist.
                "schritt":      "landschaft",
                "achsen":       achsen,
                "sektor_index": sektor_index,
                "sektor_name":  sektor_name,
                "cluster":      cluster,
                "fassung":      achsen_fassung(),
            },
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
        )
    except Exception as fehler:
        logger.warning(
            f"Landschafts-Protokoll nicht geschrieben ({type(fehler).__name__}: "
            f"{fehler}) — der Turn laeuft weiter, die Reihe hat eine Luecke"
        )


@dataclass(frozen=True)
class Lage:
    """Der vermessene Zustand eines Turns, bevor ueber das Vorausdenken entschieden ist.

    Ein Objekt statt acht loser Rueckgabewerte (`13_DATENSTRUKTUREN.md` §1):
    Die Teile gehoeren zusammen, weil sie aus **einer** Messung stammen und
    weil jeder der drei Ausgaenge des Nodes sie vollstaendig braucht. Wer den
    Sektor ohne die Achsen weiterreicht, reicht ein Ergebnis ohne seine
    Eingangsgroessen weiter.

    Was hier **nicht** hineingehoert: alles, was aus dem LLM-Lauf stammt. Die
    Grenze dieses Objekts ist genau die Grenze, an der die Tore stehen.
    """

    achsen:               dict
    sektor_index:         int
    sektor_name:          str
    cluster:              str
    fuehrung:             Fuehrung
    versatz_quelle:       str
    farbton:              str
    aufnahmebereitschaft: float


def _lage_vermessen(state: ConversationState) -> Lage:
    """Misst den Zustand des Turns: Farbton, Aufnahmebereitschaft, Landschaft.

    **Diese Rechnung steht vor jedem Tor des Nodes, und das ist ihr Zweck.**
    Sie ist ein Zustand des Gespraechs und keine Funktion des Vorausdenkens —
    dieselbe Begruendung, mit der die Aufnahmebereitschaft in Chat 116 vor die
    Laengen-Schwelle gezogen wurde (`novaberg-node-gv_k.md`, Abschnitt "Was
    hinter dem Laengen-Tor steht und was davor"). Sie stand trotzdem dahinter,
    bis das am 08.08.2026 gemessen wurde.

    Sie liest **`internal`**, nicht `external`: Naehe und Tiefe kommen aus
    Novas Raum. Die Tore davor lesen `external`. Der Ausfall entstand also
    daraus, dass eine Aussage ueber den Nutzer eine Messung an Nova abschaltete.

    Kosten ausserhalb des Prozesses: ein Redis-Lesezugriff mit Embedding der
    Vorantwort und ein Datenbanklauf fuer den Charakter-Versatz. Kein LLM.
    Farbton und Aufnahmebereitschaft sind rein — State-Lesen, Tabellen-
    Lookups, Arithmetik.

    Vorbedingung: keine. Fehlt `internal`, greifen die Neutralwerte von
        `achsen_berechnen`, und die Initiative meldet ihre Masse als fehlend.
    Nachbedingung: Jedes Feld ist besetzt; `cluster` ist nie leer, weil
        `sektor_bestimmen` fuer jeden der 64 Indizes einen Eintrag hat.
    Fehlerfaelle: Ein nicht ladbarer Charakter-Versatz wird laut gemeldet und
        die Achse rechnet ohne ihn — ein erfundener Versatz waere schlimmer
        als ein fehlender, weil er wie eine Charaktereigenschaft aussaehe.
    """
    # ── Eingabe ─────────────────────────────────
    farbton: str = farbton_berechnen(state)
    if farbton:
        logger.info(f"GV-Farbton: {farbton}")

    aufnahmebereitschaft: float = aufnahmebereitschaft_berechnen(state)

    vorher_embedding, vorher_modus = _vorturn_laden(state)

    # Der Charakter-Versatz kommt aus dem zweiten Rad (Chat 116). Faellt das
    # Laden aus, wird OHNE Versatz gerechnet statt mit einem erfundenen — der
    # Rohwert bleibt dann die reine Messung, und die Logzeile sagt es.
    versatz, versatz_quelle = initiative_versatz_laden(
        POSTGRES_URL, state.get("user_id", ""),
    )
    if versatz is None:
        logger.error(
            "GV-Initiative: Charakter-Versatz nicht ladbar (Herkunft '%s') — "
            "die Achse rechnet ohne ihn", versatz_quelle,
        )
        versatz = 0.0
    elif versatz_quelle != "destilliert":
        logger.info(
            "GV-Initiative: Versatz %+.4f stammt aus dem Default, nicht aus "
            "einer Destillation — der Charakter verschiebt die Achse noch nicht",
            versatz,
        )

    # ── Verarbeitung ────────────────────────────
    fuehrung: Fuehrung = fuehrung_messen(
        state, vorher_embedding, vorher_modus, versatz,
    )
    achsen: dict = achsen_berechnen(state, fuehrung)

    # Der Rohwert allein ist spaeter nicht auswertbar. Sobald der
    # Kalibrier-Agent die Schwelle je Paar erhebt, wandert der Massstab mit
    # dem Gemessenen: Ein Rohwert von -0.30 heisst bei Schwelle -0.45 "der
    # Nutzer fuehrt" und bei -0.20 das Gegenteil. Ohne die zum Zeitpunkt
    # geltende Fassung ist nach einigen Kalibrierungen nicht mehr trennbar, ob
    # sich Nova bewegt hat oder die Skala — dieselbe Fehlerklasse wie ein
    # Ausfallwert, der aussieht wie eine Messung, nur ueber die Zeit
    # (novaberg-lesson_l_default-wie-fehlschlag.md). Deshalb reisen Rohwert,
    # Bit und Skalenfassung in EINER Zeile.
    _initiative_protokollieren(state, fuehrung, achsen)

    sektor_index, sektor_name, cluster = sektor_bestimmen(achsen)

    # Der Bestand, gegen den die Raumgrenzen spaeter justiert werden. Steht
    # hier und nicht beim Aufrufer, damit er auf jedem Weg des Nodes entsteht.
    _landschaft_protokollieren(state, achsen, sektor_index, sektor_name, cluster)

    # ── Ausgabe-Verifikation ────────────────────
    # `sektor_bestimmen` faellt bei einem Index ausserhalb der Tabelle auf
    # 'wartezimmer' zurueck und meldet das. Ein leerer Cluster waere trotzdem
    # ein anderer Fehler — er kaeme aus einem luckenhaften Tabelleneintrag und
    # traefe den Verbraucher zwei Knoten spaeter.
    if not cluster:
        logger.error(
            "GV-Landschaft: Sektor #%d '%s' liefert keinen Cluster — die "
            "Landschaft dieses Turns ist nicht bestimmbar",
            sektor_index, sektor_name,
        )

    return Lage(
        achsen               = achsen,
        sektor_index         = sektor_index,
        sektor_name          = sektor_name,
        cluster              = cluster,
        fuehrung             = fuehrung,
        versatz_quelle       = versatz_quelle,
        farbton              = farbton,
        aufnahmebereitschaft = aufnahmebereitschaft,
    )


def _gv_detail_bauen(
    lage:         Lage,
    vorausdenken: str,
    max_laenge:   int,
    antizipation: dict | None = None,
) -> dict:
    """Baut `gv_detail` — **die einzige Stelle, an der die Felder stehen**.

    Alle drei Ausgaenge des Nodes gehen hier hindurch. Vorher schrieb nur der
    lange Weg ein `gv_detail`; die beiden frueh zurueckkehrenden Wege schrieben
    gar keins, und der Haltungs-Knoten erbte ein leeres Dict. Zwei Literale
    haetten dasselbe Problem in langsamer: Sie waeren beim naechsten neuen Feld
    auseinandergelaufen.

    Args:
        lage:         der vermessene Zustand — steht in jedem Turn.
        vorausdenken: eine der vier `VORAUSDENKEN_*`-Marken.
        max_laenge:   Zahl der erlaubten Gedankenspruenge, 0 bis 3.
        antizipation: die Ausbeute des LLM-Laufs, oder None, wenn er nicht
            stattgefunden hat. **Nicht `{}`** — ein leeres Dict waere von
            einem leer gebliebenen Lauf nicht zu unterscheiden.

    Returns:
        Das vollstaendige `gv_detail`. Jeder Schluessel ist auf jedem Weg
        vorhanden; die Antizipations-Haelfte traegt ihre Leerwerte, und
        `vorausdenken` sagt, ob das eine Messung oder ein Ausfall ist.
    """
    # ── Verarbeitung ────────────────────────────
    felder: dict = {
        "sprung_1": "", "sprung_2": "", "sprung_3": "",
        "absicht": "", "strategie": "", "vehikel": "", "impuls": "",
        "repertoire": {}, "charakter_gewichtung": {},
        "resonanz_kontext": "", "wissensluecken": [],
        "strategie_aktiv": False, "korridor_verstoesse": [],
    }
    if antizipation:
        felder.update(antizipation)

    return {
        **felder,
        # Achsen (Python, deterministisch)
        "achsen":       lage.achsen,
        "sektor_index": lage.sektor_index,
        "sektor_name":  lage.sektor_name,
        "cluster":      lage.cluster,
        "drive":        lage.achsen.get("drive", 0.0),
        # Bestehende Felder
        "laenge":       max_laenge,
        "farbton":      lage.farbton,
        "aufnahmebereitschaft": lage.aufnahmebereitschaft,
        # Das Begleitfeld. Es traegt den Unterschied, den die Landschaft allein
        # nicht mehr tragen kann, seit sie in jedem Turn dasteht.
        "vorausdenken": vorausdenken,
        # Initiative: die drei Masse einzeln, damit am Panel ablesbar bleibt,
        # woraus das Achsen-Bit entstanden ist und was gefehlt hat.
        "initiative": {
            "wert":     lage.fuehrung.wert,
            "rohwert":  lage.fuehrung.rohwert,
            "versatz":  lage.fuehrung.versatz,
            "wollen":   lage.fuehrung.wollen,
            "bewegung": lage.fuehrung.bewegung,
            "m1_roh":   lage.fuehrung.m1_roh,
            "m2_roh":   lage.fuehrung.m2_roh,
            "m3_roh":   lage.fuehrung.m3_roh,
            "fehlend":  lage.fuehrung.fehlend,
            "versatz_quelle": lage.versatz_quelle,
        },
    }


def gespraechsvektor(state: ConversationState) -> ConversationState:
    """Gespraechsvektor-Node: Antizipiert die Richtung des Gespraechs.

    Sequentieller Ablauf:
      1. Farbton, Aufnahmebereitschaft, Landschaft — der Zustand des Turns
      2. Skip-Check und Laenge — die beiden Tore des Vorausdenkens
      3. Resonanz-Kontext aus den Spreading-Erinnerungen des Enrichers
      3d. Wissensluecken finden (DB-Queries, Relevanz-Berechnung)
      3e. Repertoire und Charakter-Gewichtung fuer den Prompt
      4. LLM-Call → Hypothese + Strategie destillieren
      5. Ergebnis + Debug-Info in State schreiben

    **Schritt 1 steht vor Schritt 2 und nicht dahinter.** Was dort gerechnet
    wird, ist der Zustand des Gespraechs; ob vorausgedacht wird, ist eine
    Entscheidung darueber. Solange die Reihenfolge umgekehrt war, hatte ein
    Turn ohne Vorausdenken auch keine Landschaft — und ein leeres Feld sieht
    aus wie eine ruhige Lage. Die Kosten der Umstellung sind ein Embedding und
    ein Datenbanklauf auf den Wegen, die frueh zurueckkehren.

    Nachbedingung: `gv_detail` ist auf **jedem** Weg gesetzt und traegt eine
        Landschaft; `gv_detail['vorausdenken']` sagt, ob die Antizipations-
        Haelfte gemessen oder ausgefallen ist.
    """
    logger.info("Gespraechsvektor: Analyse gestartet")

    # 1. Der Zustand des Turns — vor jeder Verzweigung.
    #
    # Die Aufnahmebereitschaft wird in JEDEM Turn gerechnet, nicht erst ab der
    # Strategie-Laenge. Grund: Sie ist ein Zustand Novas (sechs Saeulen aus
    # Emotion, Arousal, Stimmungsrichtung, Modus, Dynamik, Stil) und keine
    # Funktion der Vektorlaenge. Der Wert 0.00 ist im Konzept fuer die Krise
    # reserviert — ein neutraler Zustand liegt bei ~0.56. Stand die Rechnung
    # hinter der Laengen-Schwelle, trug gv_detail bei jedem kurzen Vektor eine
    # 0.0, die von einer gemessenen Krise nicht zu unterscheiden war (Chat 116,
    # gemessen: 4 von 8 Laeufen; lesson_l_default-wie-fehlschlag).
    #
    # Am 08.08.2026 kam die Landschaft dazu, aus demselben Grund und mit
    # derselben Messung: Chat 116 zog die Bereitschaft vor die Laengen-
    # SCHWELLE (Laenge < 2), aber nicht vor die beiden `return`s davor. Bei
    # Skip und bei Laenge 0 fehlte deshalb bis heute nicht nur die Landschaft,
    # sondern `gv_detail` vollstaendig.
    lage: Lage = _lage_vermessen(state)

    # 2. Die beiden Tore des Vorausdenkens.
    if _ist_skip(state):
        logger.info(
            "Gespraechsvektor: Skip (Begruessung/Meta) — kein Vorausdenken, "
            f"Landschaft '{lage.cluster}' steht trotzdem"
        )
        state["gespraechsvektor"] = ""
        state["gv_detail"] = _gv_detail_bauen(lage, VORAUSDENKEN_SKIP, 0)
        return state

    max_laenge: int = _vektor_laenge_berechnen(state)

    if max_laenge == 0:
        # Die Krise ist eine Entscheidung des Konzepts, die arithmetische Null
        # ein Ergebnis der Gewichte. Beide auf dieselbe Marke zu schreiben
        # haette die Auswertung um genau die Frage gebracht, die B1 stellt.
        grund: str = VORAUSDENKEN_KRISE if _ist_krise(state) else VORAUSDENKEN_LAENGE_NULL
        logger.info(
            f"Gespraechsvektor: Laenge 0 ({grund}) — kein Vorausdenken, "
            f"Landschaft '{lage.cluster}' steht trotzdem"
        )
        state["gespraechsvektor"] = ""
        state["gv_detail"] = _gv_detail_bauen(lage, grund, 0)
        return state

    # 3. Zweite Wissensquelle: die Spreading-Erinnerungen des Enrichers.
    #    Bis Chat 115 der Entity-Hop ueber `fakten` — umgehaengt, weil die
    #    Tabelle seit Synapsen P4 keinen Produzenten mehr hat (K2).
    resonanz_kontext: str = _resonanz_kontext_laden(state)

    # 3d. GV4: Wissensluecken finden (DB-Queries — nur ab Strategie-Laenge,
    #     und nur wenn ueberhaupt Bereitschaft da ist). Das Laengen-Tor bleibt
    #     hier stehen, wo es hingehoert: an der teuren Suche, nicht an einer
    #     Messung.
    strategie_aktiv:    bool       = max_laenge >= GV_STRATEGIE_MIN_LAENGE
    wissensluecken:     list[dict] = []

    if strategie_aktiv and lage.aufnahmebereitschaft > 0:
        wissensluecken = wissensluecken_finden(state, lage.aufnahmebereitschaft)

    # 3e. Der Teil der Dreischicht, der nur den Prompt bedient. Die Messung —
    #     Achsen, Sektor, Cluster — ist oben schon gelaufen; hier kommt dazu,
    #     was ohne LLM-Lauf niemand braucht: das Repertoire des Clusters und
    #     die Charakter-Gewichtung, die ein frisches Embedding kostet.
    cluster: str = lage.cluster
    repertoire: dict[str, str] = repertoire_laden(cluster)
    charakter_gewichtung: dict[str, float] = charakter_gewichtung_berechnen(state)
    dreischicht_block: str = dreischicht_prompt_bauen(
        cluster, repertoire, charakter_gewichtung,
    )

    # 4. Hypothese destillieren
    hypothese, gv_parsed = _hypothese_destillieren(
        state, max_laenge, resonanz_kontext,
        farbton=lage.farbton,
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

    state["gv_detail"] = _gv_detail_bauen(
        lage, VORAUSDENKEN_GELAUFEN, max_laenge,
        antizipation = {
            # Spruenge (LLM-Output geparst)
            "sprung_1":  gv_parsed.get("sprung_1", ""),
            "sprung_2":  gv_parsed.get("sprung_2", ""),
            "sprung_3":  gv_parsed.get("sprung_3", ""),
            # Dreischicht (LLM waehlt aus Python-Korridor)
            "absicht":   gv_parsed.get("absicht", ""),
            "strategie": gv_parsed.get("strategie", ""),
            "vehikel":   gv_parsed.get("vehikel", ""),
            "impuls":    gv_parsed.get("impuls", ""),
            # Repertoire + Gewichtung (Python)
            "repertoire":           repertoire,
            "charakter_gewichtung": charakter_gewichtung,
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
            "resonanz_kontext": resonanz_kontext[:500] if resonanz_kontext else "",
            "wissensluecken": [
                {
                    "konzept":       luecke["konzept"][:120],
                    "quelle":        luecke["quelle"],
                    "relevanz":      round(luecke["relevanz"], 3),
                    "neugier_boost": round(luecke.get("neugier_boost", 0), 3),
                    "register":      round(luecke.get("register", 1.0), 2),
                }
                for luecke in wissensluecken
            ],
            "strategie_aktiv":     strategie_aktiv,
            "korridor_verstoesse": korridor_verstoesse,
        },
    )

    return state
