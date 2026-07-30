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

from ei.gravitation import emotionale_gravitation_auf_verlauf_anwenden
from graph.nodes.ei_calc import internal_emotion_uebertragen
from graph.state import ConversationState

logger = logging.getLogger("ki_server.emotionale_gravitation")


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
    """
    # ── Eingabe-Validierung ─────────────────────
    punkte:  list[dict] = state.get("emotionale_gravitationspunkte") or []
    verlauf: list[dict] = state.get("nova_emotions_verlauf") or []

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
