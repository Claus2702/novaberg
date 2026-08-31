"""
Emotionale-Gravitation Node — reaktivierte Erinnerungen faerben Novas Lage.

Emotional aufgeladene Erinnerungen wirken als Attraktoren auf Novas
Emotionsstrom: still und passiv, bis ein thematisch verwandtes Gespraech sie
anspricht (novaberg-thinking-drive_k.md §5.7, dritte Kraft nach Decay und
Empathie).

Position im Graph — nur CharacterGraph, zwischen Enricher und Reducer:

    db_zugriff -> ei_calc -> enricher -> emotionale_gravitation -> reducer
                     |          |                  |
                     |          |                  +-- wendet sie an
                     |          +-- findet die Gravitationspunkte
                     +-- erzeugt nova_emotions_verlauf (Decay + Empathie)

Warum genau hier, und nicht in ei_calc, wo der Aufruf bis Chat 113 stand: Der
Enricher liest `nova_emotions_verlauf`, um ueber die Sektor-Affinitaet seine
Erinnerungen zu waehlen — deshalb laeuft ei_calc im CharacterGraph VOR ihm
(Commit 630d357, Chat 89). Der Produzent der Gravitationspunkte kam damit nach
ihrem Verbraucher, und `state.get("emotionale_gravitationspunkte", [])` war an
der Lesestelle immer leer. Gemessen am 28.07.2026: 851 Berechnungen, null
Anwendungen.

Dass die Erinnerungsauswahl des Enrichers auf Novas Lage VOR der Gravitation
steht, ist kein Mangel, sondern verhindert eine Rueckkopplung: Sonst holte
Trauer traurige Erinnerungen, die wieder Trauer injizieren.

Vor dem GV-Node zu stehen ist eine Entscheidung mit Reichweite (Chat 113): Die
sechs Saeulen der Aufnahmebereitschaft und die Achsen der Dreischicht lesen
Novas Emotion. Eine reaktivierte Erinnerung veraendert damit nicht nur den Ton
der Antwort, sondern auch Novas Denkrichtung — "Freitag" darf an "Grillen"
denken lassen und dabei froh stimmen.

Kein LLM-Call, kein I/O. Reine State-Transformation.
"""

import logging

from config import POSTGRES_URL, PRAEGUNG_BERUEHRUNG_NAEHE
from ei.gravitation import emotionale_gravitation_auf_verlauf_anwenden
from graph.nodes.ei_calc import internal_emotion_uebertragen
from graph.reiz import reiz_ist_eigener_gedanke
from graph.state import ConversationState, pipeline_quelle
from memory.pipeline_log import log_berechnung
from memory.praegung import beruehrung_aus_reaktivierung

logger = logging.getLogger("ki_server.emotionale_gravitation")


def _faeden_auffrischen(state: ConversationState, punkte: list[dict]) -> None:
    """Legt Beruehrungen fuer die Faeden an, die den Reaktivierungen nahe stehen.

    Vorbedingung: `punkte` sind die aktivierten Gravitationspunkte dieses Turns.
    Nachbedingung: Je getroffenem Faden eine Zeile in `praegung_beruehrung`, und
    eine `pipeline_log`-Zeile mit der Zahl der Kandidaten und der Treffer.
    Fehlerfaelle: Keine eigenen — die Schreibfunktion meldet selbst und liefert
    eine leere Liste; der Turn laeuft weiter.

    **Die Log-Zeile zaehlt beide Seiten.** Eine Reihe ohne Beruehrungen kann
    daran liegen, dass die Schwelle zu hoch steht oder dass es keine Faeden
    gibt; ohne die Kandidatenzahl waeren die beiden Faelle ununterscheidbar —
    dieselbe Klasse wie ein Tor, dessen Neins niemand zaehlt.
    """
    # ── Eingabe-Validierung ─────────────────────
    lzg_ids: list[int] = [
        int(p["knoten_id"]) for p in punkte
        if p.get("quelle") == "lzg" and p.get("knoten_id") is not None
    ]
    if not lzg_ids:
        return

    # ── Verarbeitung ────────────────────────────
    treffer = beruehrung_aus_reaktivierung(
        POSTGRES_URL,
        state.get("user_id", ""), state.get("character_id", ""),
        lzg_ids, PRAEGUNG_BERUEHRUNG_NAEHE,
    )

    # ── Ausgabe-Verifikation ────────────────────
    log_berechnung(
        turn_id = state.get("turn_id", "unbekannt"),
        node    = "emotionale_gravitation",
        quelle  = pipeline_quelle(state),
        inhalt  = {
            "schritt":    "praegung_auffrischung",
            "kandidaten": len(lzg_ids),
            "schwelle":   PRAEGUNG_BERUEHRUNG_NAEHE,
            "treffer":    [
                {"knoten_id": k, "faden_id": f, "naehe": round(n, 3)}
                for k, f, n in treffer
            ],
        },
        user_id      = state.get("user_id"),
        character_id = state.get("character_id"),
    )


def emotionale_gravitation_anwenden(state: ConversationState) -> ConversationState:
    """Injiziert die aktivierten Gravitationspunkte in Novas Emotions-Verlauf.

    Ablauf (EVA):
      Eingabe      — Punkte und Verlauf pruefen; ohne eines von beidem gibt es
                     nichts zu tun, und das ist der Normalfall.
      Verarbeitung — emotionale_gravitation_auf_verlauf_anwenden().
      Ausgabe      — Verlauf zurueckschreiben, internal.emotion nachziehen,
                     Wirkung protokollieren.

    Vorbedingung: `emotionale_gravitationspunkte` und `nova_emotions_verlauf`
    liegen im State (Enricher bzw. ei_calc haben sie gesetzt).
    Nachbedingung: `nova_emotions_verlauf` traegt die Emotionen der aktivierten
    Erinnerungen, absteigend nach Gewicht sortiert, und `internal.emotion`
    traegt denselben fuehrenden Eintrag — beide Beine des GV-Nodes stehen
    danach auf derselben Lage.
    Fehlerfaelle: Fehlt einer der beiden Werte, bleibt der State unveraendert.
    Ein leerer Punkte-Satz ist kein Fehler — er ist die Regel, weil nur wenige
    Turns eine Erinnerung ueber der Schwelle treffen. Ein leerer Verlauf bei
    vorhandenen Punkten dagegen ist einer: Dann hat ei_calc nichts geliefert,
    und die Injektion haette nichts, worauf sie wirken koennte.

    **Auf einem Impuls-Turn faellt die Injektion aus** (23.08.2026). Die
    Gravitation ist die Antwort auf einen *fremden* Reiz: Etwas kam von aussen,
    und eine Erinnerung faerbt, wie Nova es aufnimmt. Ein eigener Gedanke ist
    bereits ihrer; ihn ein zweites Mal zu faerben verdoppelt dieselbe Quelle
    und verschiebt Landschaft und Dreischicht, weil dieser Knoten vor dem
    GV-Node steht. Belegt am 13.08.2026, 05:59:56 — zweimal `neugierig` auf
    einem Impuls-Turn.
    """
    # ── Eingabe-Validierung ─────────────────────
    punkte:  list[dict] = state.get("emotionale_gravitationspunkte") or []
    verlauf: list[dict] = state.get("nova_emotions_verlauf") or []

    # Vor den Leerpruefungen, und mit der Zahl: Ein Ausfall, der als "keine
    # Punkte" protokolliert wuerde, waere von einem echten leeren Satz nicht
    # zu unterscheiden (22_STILLE_FEHLER §5).
    if reiz_ist_eigener_gedanke(state):
        logger.info(
            f"EmGrav-Node: eigener Impuls — Injektion faellt aus, "
            f"{len(punkte)} Gravitationspunkt(e) nicht angewendet; der Gedanke "
            f"ist bereits Novas eigener und braucht keine zweite Faerbung"
        )
        return state

    if not punkte:
        logger.debug(
            "EmGrav-Node: Keine aktivierten Gravitationspunkte — Verlauf unveraendert"
        )
        return state

    if not verlauf:
        logger.error(
            f"EmGrav-Node: {len(punkte)} Gravitationspunkte, aber leerer "
            f"nova_emotions_verlauf — ei_calc hat nichts geliefert, die "
            f"Injektion faellt aus"
        )
        return state

    # Welche Erinnerung aktiviert wurde, stand bis zum 30.08.2026 nirgends: Der
    # Kandidat trug keinen Schluessel, und die Logzeile nennt nur eine Anzahl.
    # Damit war die Reaktivierungshaeufigkeit eines Knotens nicht zaehlbar — und
    # ein Schwellwert, der nichts mehr ablehnt, faellt niemandem auf
    # (EMGRAV-KANDIDAT-OHNE-KENNUNG, EMGRAV-SCHWELLE-TOT).
    log_berechnung(
        turn_id = state.get("turn_id", "unbekannt"),
        node    = "emotionale_gravitation",
        quelle  = pipeline_quelle(state),
        inhalt  = {
            "schritt":    "emgrav_aktivierung",
            "aktiviert":  len(punkte),
            "kandidaten": [
                {
                    "knoten_id":   p.get("knoten_id"),
                    "quelle":      p.get("quelle"),
                    "emotion":     p.get("emotion"),
                    "similarity":  p.get("similarity"),
                    "gewicht":     p.get("gewicht"),
                    "gravitation": p.get("gravitation"),
                }
                for p in punkte
            ],
        },
        user_id      = state.get("user_id"),
        character_id = state.get("character_id"),
    )

    # Dieselben Reaktivierungen frischen Praegungsfaeden auf (Konzept §7.4).
    # **Hier und nicht im Praegungs-Node:** Die Auffrischung haengt an der
    # Reaktivierung, nicht am Turn — ein Turn ohne aktivierte Erinnerung
    # frischt nichts auf, auch wenn er thematisch passt. Nur LZG-Punkte: Eine
    # KZG-Reaktivierung hat keine Zeile in `lzg_knoten` und damit kein
    # Embedding, gegen das sich ein Faden vergleichen liesse.
    _faeden_auffrischen(state, punkte)

    # ── Verarbeitung ────────────────────────────
    vorher_emotion: str   = verlauf[0]["emotion"]
    vorher_gewicht: float = verlauf[0].get("gewicht", 0.0)

    modifiziert: list[dict] = emotionale_gravitation_auf_verlauf_anwenden(
        verlauf, punkte,
    )

    # ── Ausgabe-Verifikation ────────────────────
    if not modifiziert:
        logger.error(
            f"EmGrav-Node: Injektion lieferte einen leeren Verlauf zurueck "
            f"({len(punkte)} Punkte auf {len(verlauf)} Eintraege) — der bisherige "
            f"Verlauf bleibt stehen"
        )
        return state

    state["nova_emotions_verlauf"] = modifiziert

    # Novas Lage hat sich soeben geaendert — und internal.emotion traegt noch
    # den Stand, den ei_calc vor dieser Injektion uebertragen hat. Zwischen hier
    # und dem Responder liest genau ein Node beide Groessen: der GV-Node. Seine
    # sechs Saeulen rechnen auf nova_emotions_verlauf, seine Dreischicht-Achsen
    # auf internal.emotion. Ohne diesen Nachzug waehlen sie Sektor und Cluster
    # auf der Lage VOR der Erinnerung, waehrend die Neugier die danach kennt —
    # dieselben zwei Zeitstaende, die Chat 113 eine Node-Position frueher
    # geschlossen hat (gemessen Chat 114: Saeulen 'begeisterung', Achsen
    # 'neugierig', im selben Turn).
    internal = state.get("internal")
    if internal is None:
        logger.error(
            "EmGrav-Node: kein internal im State — internal.emotion behaelt den "
            "Stand vor der Injektion, der GV-Node waehlt seinen Cluster darauf"
        )
    else:
        internal_emotion_uebertragen(
            internal, modifiziert, quelle="EmGrav-Node (nachgezogen)",
        )

    # Die Wirkung benennen, nicht zaehlen: Welche Emotion oben stand und welche
    # jetzt oben steht, ist die Frage, die dieser Node beantwortet.
    nachher_emotion: str   = modifiziert[0]["emotion"]
    nachher_gewicht: float = modifiziert[0].get("gewicht", 0.0)
    quellen:         str   = ", ".join(
        f"{p.get('emotion', '?')}({p.get('quelle', '?')}, g={p.get('gravitation', 0):.2f})"
        for p in punkte
    )

    if nachher_emotion != vorher_emotion:
        logger.info(
            f"EmGrav-Node: Novas dominante Emotion gewechselt — "
            f"{vorher_emotion}({vorher_gewicht:.2f}) -> "
            f"{nachher_emotion}({nachher_gewicht:.2f}) durch [{quellen}]"
        )
    else:
        logger.info(
            f"EmGrav-Node: Verlauf gefaerbt, Fuehrung unveraendert bei "
            f"{nachher_emotion}({vorher_gewicht:.2f} -> {nachher_gewicht:.2f}) "
            f"durch [{quellen}]"
        )

    return state
