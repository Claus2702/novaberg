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

**Der Node protokolliert seine Rechnung selbst** — drei Zahlen je Groesse ins
`pipeline_log` (Konzept §2.0a), nicht nur das Ergebnis. Faellt die Rechnung
aus, steht dort eine `fehler`-Zeile mit dem Grund und ausdruecklich **keine**
Berechnungszeile mit Nullen: Die waere in jeder Auswertung von einer
gemessenen Haltung ohne Ausschlag nicht zu unterscheiden.

Was noch fehlt: Kein Prompt liest die Werte. Novas Verhalten ist bis dahin
unveraendert, und genau das erlaubt es, die Zahlen gegen echte Turns zu
pruefen, ohne diese Turns beeinflusst zu haben.
"""

import logging
from collections.abc import Callable

from ei.haltung import GROESSEN, Haltung, haltung_berechnen
from memory.charakter import nutzer_gewichtung_rad_laden
from memory.pipeline_log import log_berechnung, log_fehler

from graph.state import ConversationState, pipeline_quelle

logger = logging.getLogger("ki_server.graph.haltung")

# Name dieses Knotens im Graphen und in der Protokollzeile. Eine Konstante,
# weil beide dieselbe Zeichenkette brauchen: Wer im `pipeline_log` sucht,
# sucht mit dem Namen, den die Spur ihm gezeigt hat.
KNOTEN: str = "haltungsraum"


def _protokoll_inhalt(haltung: Haltung, rad_quelle: str, speichen: int) -> dict:
    """Baut den Inhalt der Protokollzeile — drei Zahlen je Groesse, nicht eine.

    Ohne Grundwert und Modifikation ist am Ergebnis nicht erkennbar, ob die
    Landschaft den Wert gesetzt oder der Charakter ihn verschoben hat
    (novaberg-haltungsraum_k.md §3.1).

    Args:
        haltung:    das Ergebnis der Rechnung.
        rad_quelle: 'destilliert' oder 'default' — die Herkunft des Rades.
        speichen:   Zahl der belegten Speichen, die in die Rechnung gingen.

    Returns:
        Ein JSON-taugliches Abbild ohne Objekte.
    """
    return {
        "cluster":      haltung.cluster,
        "rad_quelle":   rad_quelle,
        "rad_speichen": speichen,
        "groessen": {
            name: {
                "grundwert":    wert.grundwert,
                "modifikation": wert.modifikation,
                "ergebnis":     wert.ergebnis,
                "art":          wert.art,
                "ausloeser":    wert.ausloeser,
            }
            for name, wert in haltung.werte.items()
        },
        # Beide Listen stehen zusaetzlich oben, obwohl sie aus `groessen`
        # ableitbar sind: **Wie oft die Rechnung die Spanne verlaesst, ist die
        # Messgroesse**, die zwischen kleineren Beitraegen und Saettigung
        # entscheidet (Konzept §6). Eine Reihe soll sie zaehlen koennen, ohne
        # je Zeile in die Tiefe zu steigen.
        "ausserhalb":   [n for n, w in haltung.werte.items() if w.ausserhalb],
        "uebersteuert": [n for n, w in haltung.werte.items() if w.art == "uebersteuerung"],
    }


def _pipeline_zeile(
    state:     ConversationState,
    schreiber: Callable[..., None],
    inhalt:    dict,
    was:       str,
) -> None:
    """Schreibt eine Zeile ins `pipeline_log`, oder sagt, warum nicht.

    Args:
        state:     Zustand, aus dem Turn- und Paarbezug stammen.
        schreiber: `log_berechnung` oder `log_fehler`.
        inhalt:    der Nutzinhalt der Zeile.
        was:       Kurzwort fuer die Meldung, falls es schiefgeht.

    Vorbedingung: `state` traegt eine `turn_id`. Fehlt sie, wird nicht
        geschrieben — eine Zeile ohne Turnbezug laesst sich keiner Messung
        zuordnen und ist damit wertlos.
    Nachbedingung: Eine Zeile im `pipeline_log`, oder eine Meldung.
    Fehlerfaelle: Ein Forensik-Schreibfehler darf den Turn nicht toeten —
        gekapselt und als `warning` gemeldet, wie in den uebrigen Knoten.
    """
    # ── Eingabe-Validierung ─────────────────────
    turn_id: str = state.get("turn_id", "")
    if not turn_id:
        logger.error(
            f"Haltungs-Protokoll: kein turn_id im State — die Zeile ({was}) "
            "waere keiner Messung zuzuordnen und wird nicht geschrieben"
        )
        return

    # ── Verarbeitung / Ausgabe ──────────────────
    try:
        schreiber(
            turn_id      = turn_id,
            node         = KNOTEN,
            quelle       = pipeline_quelle(state),
            inhalt       = inhalt,
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
        )
    except Exception as fehler:
        logger.warning(
            f"Haltungs-Protokoll ({was}) nicht geschrieben "
            f"({type(fehler).__name__}: {fehler}) — der Turn laeuft weiter, "
            "die Reihe hat eine Luecke"
        )


def _ausfall_protokollieren(state: ConversationState, grund: str, cluster: str) -> None:
    """Haelt fest, dass dieser Turn keine Haltung bekam, und warum.

    **Bewusst `log_fehler` und nicht `log_berechnung`.** Ein Ausfall als
    Berechnungszeile mit Nullen sieht in jeder Auswertung aus wie eine
    gemessene Haltung ohne Ausschlag; das Konzept verlangt deshalb keine Zeile
    statt einer leeren (§2.0a). Ganz zu schweigen ginge aber ebenso wenig — die
    Haeufigkeit der Ausfaelle gehoert zur Messreihe. Eine Fehlerzeile ist
    beides: nicht als Messwert lesbar und trotzdem zaehlbar.

    Args:
        state:   Zustand des laufenden Durchlaufs.
        grund:   was gefehlt hat, im Klartext.
        cluster: die Landschaft, soweit bekannt — sonst leer.
    """
    _pipeline_zeile(
        state,
        log_fehler,
        {"schritt": "haltung", "grund": grund, "cluster": cluster},
        "Ausfall",
    )


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
        _ausfall_protokollieren(state, "keine Landschaft in gv_detail", "")
        return state

    if not user_id:
        logger.error(
            "Haltungs-Node: leere user_id im Zustand — das Rad ist einem Paar "
            f"zugeordnet und ohne Nutzer nicht ladbar, Landschaft {cluster!r}"
        )
        _ausfall_protokollieren(state, "leere user_id", cluster)
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
        _ausfall_protokollieren(state, f"Rad nicht ladbar ({quelle})", cluster)
        return state

    haltung: Haltung | None = haltung_berechnen(cluster, rad)

    if haltung is None:
        # `haltung_berechnen` hat den Fall bereits mit Wert benannt.
        logger.error(
            f"Haltungs-Node: Rechnung abgelehnt fuer Landschaft {cluster!r} "
            f"mit {len(rad)} Speichen — keine Haltung fuer diesen Turn"
        )
        _ausfall_protokollieren(state, "Rechnung abgelehnt", cluster)
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
        _ausfall_protokollieren(
            state, f"unvollstaendig, es fehlen {sorted(fehlend)}", cluster,
        )
        return state

    state["haltung"] = haltung

    # Die Historie, nicht der Zustand: Die Beitragszahlen sind Setzungen und
    # werden nachkalibriert; ohne Verlauf ist das nicht moeglich (Konzept
    # §2.0a). Deshalb `pipeline_log` und ausdruecklich kein Redis-Blob, der
    # beim naechsten Turn ueberschrieben wird.
    _pipeline_zeile(
        state,
        log_berechnung,
        _protokoll_inhalt(haltung, quelle, len(rad)),
        "Berechnung",
    )

    # Die Herkunft des Rades steht in der Meldung, weil sie den Unterschied
    # zwischen Messung und Ausfall traegt: Ein Default-Rad rechnet sich genauso
    # glatt wie ein destilliertes, sagt aber nichts ueber diesen Charakter.
    logger.info(
        f"Haltungs-Node: {haltung.kurzfassung()} (Rad {quelle!r}, "
        f"{len(rad)} Speichen)"
    )

    return state
