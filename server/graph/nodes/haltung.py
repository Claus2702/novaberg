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

from config import redis_client
from ei.haltung import GROESSEN, Haltung, haltung_berechnen
from graph.state import ConversationState, pipeline_quelle
from memory.charakter import nutzer_gewichtung_rad_laden
from memory.haltung import Standkopf, haltung_speichern
from memory.pipeline_log import log_berechnung, log_fehler

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
        rad_quelle: 'destilliert', 'default' oder 'neutral' — die Herkunft
            des Rades. Der dritte Wert kam am 22.08.2026 dazu und meint ein
            Paar, ueber das noch nichts erhoben wurde; er steht neben
            'default', weil jenes ein Rad meint, das erhoben wurde und nichts
            ergab. Im Protokoll bleiben beide unterscheidbar.
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


def _initiative_aus_state(state: ConversationState) -> tuple[float | None, str]:
    """Holt das Fuehrungsmass des Turns aus dem Zustand.

    Der Gespraechsvektor-Knoten rechnet es und legt es **in `gv_detail`** ab;
    er laeuft vor diesem Knoten (`graph.add_edge("gv_node", "haltungsraum")`).
    Hier wird es nur weitergereicht — gerechnet wird an einer Stelle.

    **Es steht in `gv_detail` und nicht auf der obersten Ebene** — bis zum
    23.08.2026 las diese Funktion `state["initiative"]`, und den Schluessel
    setzt niemand. Gemessen ueber den ganzen Baum: **ein** Schreiber
    (`_gv_detail_bauen`), **ein** Leser (hier), zwei verschiedene Ebenen. Der
    Rueckgabewert war damit auf jedem Turn `(None, "gv_ohne_lauf")`, und
    Riegel 2 sperrte seit seinem Bau am 15.08.2026 **immer**. Der letzte
    Impuls-Turn stammt vom selben Tag.

    **Warum es acht Tage niemand sah, gehoert zur Regel:** Der Riegel schliesst
    bei Unbekanntem, und das ist richtig so (`novaberg-eigenzeit_k.md` §2.5).
    Ein dauerhaft geschlossener Riegel sieht deshalb aus wie eine Figur, die
    gerade nicht zugehen will — und `gv_ohne_lauf` ist ein vorgesehener Grund,
    keine Fehlermeldung. **Ein Ausfall, der sich als gueltige Entscheidung
    tarnt, hat keinen Melder.** Derselbe Knoten liest die Landschaft 130 Zeilen
    weiter richtig aus `gv_detail`.

    **Der Ausfall wird benannt, nicht geglaettet.** Wer hier bei fehlendem Wert
    eine Zahl einsetzte, gaebe Riegel 2 eine Messung, die keine war. Und wer
    ``achsen["initiative"]`` naehme statt des rohen Wertes, erbte dessen
    Umkehrung: `ei/dreischicht.py` setzt bei fehlendem Mass **Bit 1** — *Nova
    fuehrt* —, was fuer eine Achse vertretbar ist und fuer einen Riegel den
    Schalter im Moment des Ausfalls **oeffnen** wuerde.

    **Die drei Gruende sind drei Sachverhalte und tragen drei Namen.** Sie
    zusammenzufassen war der zweite Teil desselben Defekts: `gv_ohne_lauf`
    behauptet, der Knoten sei nicht gelaufen, und genau das hat die
    Untersuchung verzoegert — der Stand trug `cluster=foyer` aus demselben
    `gv_detail` und belegte damit das Gegenteil.

    | Lage | Grund | was sie heisst |
    |---|---|---|
    | kein `gv_detail` | `gv_ohne_lauf` | der Knoten lief wirklich nicht |
    | `gv_detail` ohne `initiative` | `fuehrung_fehlt_im_detail` | er lief und liess das Mass aus |
    | `initiative` ohne Zahl | `masse_fehlen` / `ohne_wert` | er rechnete und kam nicht durch |

    Vorbedingung: keine.
    Nachbedingung: (Wert, Grund). Genau eines von beidem ist belegt.

    Args:
        state: Zustand des laufenden Durchlaufs.

    Returns:
        Das Fuehrungsmass und den Grund seines Fehlens.
    """
    # ── Eingabe-Validierung ─────────────────────
    gv_detail = state.get("gv_detail")
    if not isinstance(gv_detail, dict):
        # Der GV-Knoten hat nichts hinterlassen — uebersprungener Turn oder ein
        # Pfad, der ihn nicht durchlaeuft. Kein Messausfall, sondern gar keine
        # Messung; die beiden werden getrennt benannt.
        return None, "gv_ohne_lauf"

    roh = gv_detail.get("initiative")
    if not isinstance(roh, dict):
        # Er lief und hat das Mass ausgelassen. Das ist etwas anderes als ein
        # uebersprungener Turn, und der Unterschied entscheidet, wo man sucht.
        return None, "fuehrung_fehlt_im_detail"

    wert = roh.get("wert")
    if not isinstance(wert, (int, float)) or isinstance(wert, bool):
        fehlend = roh.get("fehlend") or []
        grund: str = (
            f"masse_fehlen: {sorted(str(m) for m in fehlend)}"
            if fehlend else "ohne_wert"
        )
        return None, grund

    # ── Ausgabe ─────────────────────────────────
    return float(wert), ""


def _stand_schreiben(
    state:   ConversationState,
    cluster: str,
    werte:   dict[str, float],
    grund:   str,
) -> None:
    """Legt den Stand dieses Turns in den Speicher, aus dem Fremde lesen.

    **Zwei Speicher, zwei Gegenstaende.** Die Zeile im ``pipeline_log`` traegt
    den **Verlauf** und ist die Grundlage der Nachkalibrierung; dieser Stand
    traegt den **Zustand** und beantwortet die Frage eines Dienstes ausserhalb
    des Graphen: *Wie steht sie gerade zu ihm?* Das Verbot des Redis-Blobs aus
    Konzept §2.0a gilt dem ersten Gegenstand, nicht dem zweiten
    (`memory/haltung.py`).

    **Auch der Ausfall schreibt.** Bliebe der alte Stand stehen, entschiede der
    Zuwendungs-Riegel nach der Lage des letzten gerechneten Turns, ohne dass es
    jemand saehe — der benannte Fehler des ``gv:detail:``-Wegs.

    **Das Fuehrungsmass reist mit und haengt nicht an `werte`.** Ein Turn ohne
    Haltung kann eines getragen haben; laege es auf derselben Marke, verdeckte
    ein Ausfall der Haltung den Riegel 2 und seine Schwelle waere nicht mehr
    kalibrierbar (`novaberg-eigenzeit_k.md` §2.5). Deshalb wird es hier
    unabhaengig vom Ausgang der Rechnung aus dem Zustand geholt.

    Args:
        state:   Zustand des laufenden Durchlaufs.
        cluster: die Landschaft, oder leer bei einem Ausfall.
        werte:   je Groessenname das Ergebnis, oder leer bei einem Ausfall.
        grund:   was gefehlt hat; leer, wenn gerechnet wurde.
    """
    # ── Verarbeitung / Ausgabe ──────────────────
    initiative, initiative_grund = _initiative_aus_state(state)

    # Der Rueckgabewert wird nicht geprueft: `haltung_speichern` meldet seinen
    # Fehlschlag selbst, und ein Turn stirbt nicht an einem Speicherfehler.
    haltung_speichern(
        redis_client,
        Standkopf(
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
            turn_id      = state.get("turn_id", ""),
        ),
        cluster = cluster,
        werte   = werte,
        grund   = grund,
        initiative       = initiative,
        initiative_grund = initiative_grund,
    )


def _ausfall_protokollieren(state: ConversationState, grund: str, cluster: str) -> None:
    """Haelt fest, dass dieser Turn keine Haltung bekam, und warum.

    **Bewusst `log_fehler` und nicht `log_berechnung`.** Ein Ausfall als
    Berechnungszeile mit Nullen sieht in jeder Auswertung aus wie eine
    gemessene Haltung ohne Ausschlag; das Konzept verlangt deshalb keine Zeile
    statt einer leeren (§2.0a). Ganz zu schweigen ginge aber ebenso wenig — die
    Haeufigkeit der Ausfaelle gehoert zur Messreihe. Eine Fehlerzeile ist
    beides: nicht als Messwert lesbar und trotzdem zaehlbar.

    **Und derselbe Ausfall loescht den Stand.** Beides gehoert zusammen, weil
    ein Ausfall, der nur protokolliert wird, den Speicher des vorigen Turns
    stehen laesst — genau die Stelle, an der eine Messreihe stimmt und ein
    Riegel trotzdem falsch entscheidet.

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
    _stand_schreiben(state, cluster, {}, grund)


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
        # **Kein Defekt, sondern eine Weitergabe.** Der GV-Node kehrt bei
        # Vektorlaenge 0 ("kein Vorausdenken") und beim Skip zurueck, BEVOR er
        # `gv_detail` setzt. Dieser Knoten erbt die Luecke: keine Landschaft,
        # keine Grundwerte, keine Haltung.
        #
        # Gemessen am 31.07.2026: in einer Reihe von 20 Turns einmal, dazu
        # einmal auf Novas Eigenimpuls. Wer den Prompt-Block einhaengt, muss
        # den Fall beantworten — er tritt regelmaessig ein und nicht selten
        # (novaberg-backlog.md → HALTUNG-OHNE-LANDSCHAFT).
        logger.error(
            "Haltungs-Node: keine Landschaft in gv_detail "
            f"({len(gv_detail)} Felder) — der GV-Node ist vor dem Setzen "
            "zurueckgekehrt, keine Haltung fuer diesen Turn"
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
    _stand_schreiben(
        state,
        haltung.cluster,
        {name: wert.ergebnis for name, wert in haltung.werte.items()},
        "",
    )

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
