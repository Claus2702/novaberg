"""Haltungs-Node — die Rechnung des Haltungsraums bekommt ihren Aufrufer.

Aus der Landschaft des Turns und Novas Zuwendung zum Nutzer folgen fuenf
Verhaltensgroessen (novaberg-haltungsraum_k.md §2). Dieser Node laedt beides
und legt das Ergebnis in den Zustand; gerechnet wird in `ei/haltung.py`, ohne
Datenzugriff.

Position im Graph — nur CharacterGraph, zwischen GV-Node und der Verzweigung
zum Verfasser:

    gv_node -> haltungsraum -> [task_context_cut?] -> verfasser | responder
       |             |
       |             +-- laedt das Rad, rechnet, schreibt `haltung`
       +-- setzt gv_detail["cluster"], die Landschaft dieses Turns

Der Node heisst `haltungsraum`, sein Kanal `haltung`: LangGraph lehnt einen
Node ab, der wie ein State-Key heisst.

Zwei Gruende fuer genau diese Stelle, beide aus dem Konzept (§2 "Wer rechnet"):

  * **Nach dem GV-Node**, weil erst er die Landschaft bestimmt. Davor gibt es
    keinen Cluster und damit keine Grundwerte.
  * **Vor der Verzweigung**, weil der Verfasser den Umfang kennen muss, bevor
    er Inhalt zusammenstellt — und weil er bei `task_context_cut` uebersprungen
    wird. Eine Rechnung in ihm fiele genau in der Lage aus, in der der
    Responder allein steht.

Kein LLM-Call. Ein Lesezugriff auf `charakter_hash`.

**Der Node schreibt noch kein Protokoll.** Drei Zahlen je Groesse ins
`pipeline_log` und eine Zeile in die Spur sind ein eigener Auftrag
(HALTUNG-PROTOKOLL-FEHLT im Backlog). Bis dahin traegt die Logzeile dieses
Nodes das Ergebnis.
"""

import logging

from ei.haltung import GROESSEN, Haltung, haltung_berechnen
from memory.charakter import nutzer_gewichtung_rad_laden

from graph.state import ConversationState

logger = logging.getLogger("ki_server.graph.haltung")

def haltung_bestimmen(state: ConversationState, postgres_url: str) -> ConversationState:
    """Rechnet die Haltung dieses Turns und legt sie in den Zustand.

    Ablauf (EVA):
      Eingabe      — Landschaft aus `gv_detail`, Nutzer aus dem Zustand. Fehlt
                     eines von beidem, gibt es nichts zu rechnen.
      Verarbeitung — Rad laden, `haltung_berechnen()` rufen.
      Ausgabe      — die fremde Nachbedingung am Verbraucher pruefen, dann
                     `haltung` schreiben und das Ergebnis melden.

    Args:
        state:        Zustand des laufenden CharacterGraph-Durchlaufs.
        postgres_url: Verbindungszeichenkette fuer den Radzugriff.

    Returns:
        Denselben Zustand. Mit `haltung`, wenn die Rechnung lief — **ohne den
        Schluessel**, wenn nicht. Ein Turn ohne Rechnung traegt keine Haltung
        statt einer leeren (Konzept §2.0a): "nicht gelaufen" muss von "alles
        auf null" unterscheidbar bleiben.

    Nachbedingung: Ist `haltung` gesetzt, traegt sie einen Eintrag je Groesse
        aus GROESSEN.

    Fehlerfaelle: fehlende Landschaft, leere user_id, nicht ladbares Rad,
        abgelehnte Rechnung — je `logger.error` und ein Zustand ohne `haltung`.
        Keiner davon bricht den Turn ab: Nova antwortet dann wie vor dem
        Haltungsraum, und das ist eine Verschlechterung, kein Ausfall.
    """
    # ── Eingabe-Validierung ─────────────────────
    gv_detail: dict = state.get("gv_detail") or {}
    cluster:   str  = gv_detail.get("cluster", "")
    user_id:   str  = state.get("user_id", "")

    if not cluster:
        # Der GV-Node laeuft unmittelbar davor und setzt den Cluster immer.
        # Ist er leer, hat der GV-Node nicht geliefert — das ist ein Defekt
        # dort, nicht ein Turn ohne Landschaft.
        logger.error(
            "Haltungs-Node: keine Landschaft in gv_detail "
            f"({len(gv_detail)} Felder) — ohne Cluster gibt es keine "
            "Grundwerte, keine Haltung fuer diesen Turn"
        )
        return state

    if not user_id:
        logger.error(
            "Haltungs-Node: leere user_id im Zustand — das Rad ist einem Paar "
            f"zugeordnet und ohne Nutzer nicht ladbar, Landschaft {cluster!r}"
        )
        return state

    # ── Verarbeitung ────────────────────────────
    rad, quelle = nutzer_gewichtung_rad_laden(postgres_url, user_id)

    if rad is None:
        # Der Lader hat den Grund bereits benannt; hier steht die Folge.
        logger.error(
            f"Haltungs-Node: Rad fuer {user_id!r} nicht ladbar (Herkunft "
            f"{quelle!r}) — keine Haltung fuer diesen Turn, Landschaft "
            f"{cluster!r}. Die Grundwerte allein waeren keine Haltung, sondern "
            "eine Cluster-Tabelle."
        )
        return state

    haltung: Haltung | None = haltung_berechnen(cluster, rad)

    if haltung is None:
        # `haltung_berechnen` hat den Fall bereits mit Wert benannt.
        logger.error(
            f"Haltungs-Node: Rechnung abgelehnt fuer Landschaft {cluster!r} "
            f"mit {len(rad)} Speichen — keine Haltung fuer diesen Turn"
        )
        return state

    # ── Ausgabe-Verifikation ────────────────────
    # Die Vollstaendigkeit ist Nachbedingung von `haltung_berechnen`. Sie wird
    # hier trotzdem geprueft, weil dieser Node der Verbraucher eines fremden
    # Vertrages ist: Wer Daten liest, prueft Plausibilitaet. Eine unvollstaendige
    # Haltung wuerde erst beim Leser auffallen — im Verfasser oder im Responder,
    # zwei Nodes spaeter und ohne Bezug zur Ursache.
    fehlend: set[str] = set(GROESSEN) - set(haltung.werte)
    if fehlend:
        logger.error(
            f"Haltungs-Node: Rechnung lieferte {sorted(haltung.werte)} und es "
            f"fehlen {sorted(fehlend)} — verworfen, Landschaft {cluster!r}"
        )
        return state

    state["haltung"] = haltung

    # Die Herkunft des Rades steht in der Meldung, weil sie den Unterschied
    # zwischen Messung und Ausfall traegt: Ein Default-Rad rechnet sich genauso
    # glatt wie ein destilliertes, sagt aber nichts ueber diesen Charakter.
    logger.info(
        f"Haltungs-Node: {haltung.kurzfassung()} (Rad {quelle!r}, "
        f"{len(rad)} Speichen)"
    )

    return state
