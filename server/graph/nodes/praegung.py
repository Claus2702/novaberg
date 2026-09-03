"""Das Faden-Tor — entscheidet, ob ein Turn eine Praegung hinterlaesst.

Position im Graphen: **nach `salience`, vor `dispatcher`**. Frueher ginge nicht,
weil die Salienz eine der beiden Torbedingungen ist und erst dort gerechnet wird;
spaeter gaebe es den Turn nicht mehr.

Konzept: `novaberg-thinking-faszination_k.md` §7.3.

**Der Node protokolliert jede Pruefung, auch die abgelehnte.** Das ist keine
Vorsicht, sondern die Lehre vom Vortag: `EMGRAV-SCHWELLE-TOT` lief wochenlang
ohne Ablehnung, und niemandem fiel es auf, weil nichts gezaehlt wurde. Die beiden
Torschwellen sind Setzungen; erst diese Zeilen machen sie kalibrierbar.
"""

import logging

from agents.charakter import rad_messreihe
from config import POSTGRES_URL
from graph.state import ConversationState, pipeline_quelle
from memory.pipeline_log import log_berechnung
from memory.praegung import (
    faden_anlegen,
    konfrontationsmass,
    praegungszug,
    tor_urteil,
)
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.praegung_node")


def _staerkstes_segment(state: ConversationState) -> dict | None:
    """Das Segment mit der groessten effektiven Salienz — Traeger des Fadens.

    Der Salienz-Node rechnet je Segment und legt Salienz **und** perzipierte
    Emotion gemeinsam in `salienz_obj` ab; ein Einzelwert steht nicht im
    Verbund. Das **Maximum** ist die richtige Wahl: Ein Turn mit einem einzigen
    einschneidenden Satz ist einschneidend, auch wenn drei belanglose daneben
    stehen — ein Mittel verduennte ihn.

    **Salienz und Emotion kommen aus demselben Segment.** Sonst truege der Faden
    die Wucht des einen und den Sektor eines anderen.

    Returns:
        Das `salienz_obj` des staerksten Segments, oder None. Der **Text** des
        Segments steht unter dem Schluessel `_segment_text` daneben — er ist
        der Traeger des scharfen Embeddings (siehe `_faden_embedding`).
    """
    bestes: dict | None = None
    for eintrag in state.get("pending_writes") or []:
        daten = eintrag.get("daten") or eintrag
        obj = daten.get("salienz_obj") if isinstance(daten, dict) else None
        if not isinstance(obj, dict) or obj.get("salienz") is None:
            continue
        if bestes is None or float(obj["salienz"]) > float(bestes["salienz"]):
            bestes = {**obj, "_segment_text": (daten.get("segment") or "")
                      if isinstance(daten, dict) else ""}
    return bestes


def _faden_embedding(segment_text: str, state: ConversationState) -> tuple[list[float], str]:
    """Der Vektor, unter dem ein Faden spaeter wiedergefunden wird.

    **Das Segment, nicht der Turn.** Salienz und Emotion des Fadens kommen aus
    dem staerksten Segment, mit der ausdruecklichen Begruendung, ein Mittel
    verduenne den einschneidenden Satz (`_staerkstes_segment`). Fuer das
    Embedding galt das bis zum 01.09.2026 **nicht**: Es kam aus
    `prompt_embedding` und trug damit den ganzen Turn — bei einem Turn mit einem
    einschneidenden Satz und drei belanglosen genau die Verduennung, gegen die
    die Segmentwahl gebaut ist.

    **Warum das die Verstaerkung traegt.** Ein Faden wird ueber Embedding-Naehe
    wiedergefunden (Konzept §7.12). `[gemessen]` 01.09.2026 ueber 19.900
    Knotenpaare: Ohne geteiltes Thema liegt die Aehnlichkeit im Median bei 0,355,
    mit geteiltem bei 0,504 — die Verteilungen ueberlappen breit. Auf einem
    verduennten Vektor ist diese Trennung noch schwaecher, und ein Faden, der
    durch Zufallsaehnlichkeit aufgefrischt wird, wird unsterblich (§7.4).

    Vorbedingung: keine.
    Nachbedingung: (Vektor, Herkunft) — Herkunft ist `segment`, `prompt` oder
    `keins` und wird protokolliert. **Ein Rueckfall, den niemand zaehlen kann,
    waere von einem scharfen Vektor nicht zu unterscheiden.**
    Fehlerfaelle: Faellt der Embed-Dienst aus, wird laut gemeldet und auf den
    Turn-Vektor zurueckgefallen — ein grober Faden ist besser als keiner, aber
    er sagt es.
    """
    # ── Eingabe-Validierung ─────────────────────
    if segment_text.strip():
        # ── Verarbeitung ────────────────────────
        try:
            vektor: list[float] = model_service.embed.submit_sync(
                EmbedRequest(text=segment_text[:1200])
            ).embedding
            if vektor:
                return vektor, "segment"
            logger.error(
                "Praegung: Embed-Dienst lieferte einen leeren Vektor fuer das "
                "Segment — Rueckfall auf den Turn-Vektor, der Faden wird grob"
            )
        except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
            # `exception` statt `error`: Faellt der Embed-Dienst aus, ist der
            # Stapel die einzige Auskunft darueber, woran — und ein Faden, der
            # dadurch grob wird, ist spaeter nicht mehr nachzubessern.
            logger.exception(
                f"Praegung: Segment nicht eingebettet ({type(fehler).__name__}) "
                f"— Rueckfall auf den Turn-Vektor, der Faden wird grob"
            )
    else:
        logger.error(
            "Praegung: das staerkste Segment traegt keinen Text — Rueckfall auf "
            "den Turn-Vektor, der Faden wird grob"
        )

    # ── Ausgabe-Verifikation ────────────────────
    turn_vektor: list[float] = state.get("prompt_embedding") or []
    return turn_vektor, ("prompt" if turn_vektor else "keins")


def _ausschlag_der_emotion(verlauf: list[dict], emotion: str) -> float:
    """Wie stark **diese** Emotion im Verlauf gerade steht.

    Nicht das Gewicht der fuehrenden Emotion: Der Faden traegt den Sektor des
    Turns, und seine Staerke muss sich auf denselben Sektor beziehen. Sonst
    misst der Ausschlag eine Emotion, die der Faden gar nicht hat.

    **Vorbehalt:** Auch dieser Wert kommt aus dem Verlauf und traegt damit
    Historie — `akkumuliert[emotion] += beitrag` laeuft ueber alle Turns, der
    aktuelle voll, aeltere als Echo. Das Konzept will die Staerke *im Moment des
    Erlebens* (§7.2); eine reine Turn-Staerke liefert das System heute nicht.
    Die Emotion selbst ist jetzt die des Turns, ihre Staerke bleibt eine
    Naeherung.
    """
    for eintrag in verlauf:
        if eintrag.get("emotion") == emotion:
            return float(eintrag.get("gewicht", 0.0))
    return 0.0


def _konfrontation_des_paares(user_id: str, character_id: str) -> float | None:
    """Novas Mass, der unangenehmen Sache nachzugehen — aus **beiden** Raedern.

    Wissbegier und Pflicht stehen im Zuwendungs-Rad, Eigensinn und Behutsamkeit
    im Initiative-Rad; wer nur eines liest, sieht die halbe Anlage und bekommt
    von `konfrontationsmass` ein None.

    Vorbedingung: das Paar ist gesetzt.
    Nachbedingung: das Mass auf [-1, 1], oder None bei unvollstaendigem Rad.
    Fehlerfaelle: Ein Lesefehler ergibt None — der Zug rechnet dann mit
        `unbestimmt` weiter, statt einen Vorgabewert ueber Novas Charakter zu
        erfinden.

    Args:
        user_id: der Mensch (`novaberg-convention-paar-schema.md` §2).
        character_id: die Figur.

    Returns:
        Das Konfrontationsmass, oder None.
    """
    # ── Eingabe ────────────────────────────────
    if not user_id or not character_id:
        return None

    # ── Verarbeitung ───────────────────────────
    gesammelt: dict[str, float] = {}
    for rad_art in ("zuwendung", "initiative"):
        try:
            teil = rad_messreihe.rad_zusammenfassen(
                rad_messreihe.reihe_laden(user_id, character_id, rad_art),
            )
        except Exception as fehler:
            logger.warning(
                f"Praegung-Zug: {rad_art}-Rad von {user_id}/{character_id} nicht "
                f"lesbar — {fehler}. Das Mass bleibt unvollstaendig"
            )
            continue
        if teil:
            gesammelt.update(teil)

    # ── Ausgabe ────────────────────────────────
    return konfrontationsmass(gesammelt) if gesammelt else None


def _zug_protokollieren(
    state: ConversationState, user_id: str, character_id: str,
) -> None:
    """Rechnet den Praegungszug dieses Turns und schreibt ihn ins Protokoll.

    Konzept §10.3. **Kein Bestand, kein Verhalten — eine Beobachtungszeile.**
    Der Zug ist der letzte Bauteil vor der Faszination; bis die ihn liest, ist
    diese Zeile sein einziger Leser, und die Reihe daraus ist das Material, an
    dem `PRAEGUNG_ZUG_SPANNE_OBEN` und `PRAEGUNG_ZUG_UNBESTIMMT` kalibrierbar
    werden. Genauso stehen Richtung und Ladung seit dem 02.09.2026 im
    Tageslauf.

    **Er haengt nicht am Tor.** Ein Turn kann eine Praegung *anziehen*, ohne
    selbst eine zu hinterlassen — das ist der Regelfall: Das Tor liess 4 von 13
    Pruefungen durch, der Zug gilt fuer alle 13.

    Vorbedingung: keine.
    Nachbedingung: eine Zeile `praegung_zug` unter dem Knoten `praegung`, mit
        Zug, Strang, Naehe, Ladung und Richtung.
    Fehlerfaelle: Ein Turn ohne `prompt_embedding` hat keinen Ort auf der
        Landkarte; das wird als Grund protokolliert und nicht als Zug 1,0
        ausgegeben — sonst waere „kein Reiz" von „kein Strang" nicht zu
        unterscheiden.

    Args:
        state: Der Zustandsverbund dieses Turns.
        user_id: der Mensch (`novaberg-convention-paar-schema.md` §2).
        character_id: die Figur.

    Returns:
        Nichts — der Node schreibt ins Protokoll, nicht in den Verbund.
    """
    # ── Eingabe ────────────────────────────────
    reiz_vektor: list[float] = state.get("prompt_embedding") or []
    inhalt: dict = {"schritt": "praegung_zug"}

    # ── Verarbeitung ───────────────────────────
    if not reiz_vektor:
        inhalt |= {"zug": None, "grund": "kein prompt_embedding"}
        logger.warning(
            "Praegung-Zug: kein prompt_embedding in diesem Turn — ohne Ort auf "
            "der Landkarte gibt es keine Aehnlichkeit und keinen Zug"
        )
    else:
        ergebnis: dict | None = praegungszug(
            POSTGRES_URL,
            user_id       = user_id,
            character_id  = character_id,
            reiz_vektor   = reiz_vektor,
            konfrontation = _konfrontation_des_paares(user_id, character_id),
        )
        if ergebnis is None:
            inhalt |= {"zug": None, "grund": "Eingabe abgelehnt"}
        else:
            # Die Teile neben der Summe: Ein Zug von 1,0 entsteht aus fehlender
            # Naehe, fehlender Ladung oder lauter Vermeidung — drei Zustaende
            # mit derselben Zahl.
            inhalt |= ergebnis

    # ── Ausgabe ────────────────────────────────
    log_berechnung(
        turn_id      = state.get("turn_id", "unbekannt"),
        node         = "praegung",
        quelle       = pipeline_quelle(state),
        inhalt       = inhalt,
        user_id      = user_id,
        character_id = character_id,
    )


def praegung_pruefen(state: ConversationState) -> ConversationState:
    """Prueft das Faden-Tor und legt bei Durchlass einen Faden an.

    Vorbedingung: `salienz_human` und `nova_emotions_verlauf` liegen vor; das
    Paar ist gesetzt. Fehlt eine der beiden Groessen, ist das **kein** stiller
    Ausfall — der Node meldet es und laesst den State unveraendert.

    Nachbedingung: Eine `pipeline_log`-Zeile `praegung_tor` mit beiden Werten und
    dem Urteil; bei Durchlass zusaetzlich eine Zeile in `praegung_faden`. Dazu
    **immer** eine Zeile `praegung_zug` — sie haengt nicht am Tor, denn ein Turn
    kann eine Praegung anziehen, ohne selbst eine zu hinterlassen.

    Args:
        state: Der Zustandsverbund nach der Salienzberechnung.

    Returns:
        Der unveraenderte State — dieser Node schreibt in die Datenbank, nicht
        in den Verbund. Auch der Praegungszug wirkt noch nicht: Er wird seit dem
        03.09.2026 je Turn gerechnet und protokolliert, aber von niemandem
        gelesen (§10.3).
    """
    # ── Eingabe ────────────────────────────────
    # **Die effektive Salienz, nicht `salienz_human`.** Das sind zwei Groessen:
    # `salienz_human` ist die Rohbewertung des Modells (Mittel 0,41, Maximum
    # 0,90 ueber 2757 Laeufe), die effektive ist das Rechenergebnis aus Eigen-
    # und Pflicht-Pfad (Mittel 0,80). Sie ist die, die ins LZG geht und
    # Erinnerungswuerdigkeit **bedeutet** — und nur sie erreicht den Bereich, in
    # dem eine Torschwelle sinnvoll liegt.
    #
    # `[gemessen]` 31.08.2026: Die erste Fassung las `salienz_human` gegen eine
    # auf der effektiven kalibrierte Schwelle und liess in sieben Betriebsturns
    # **null** Faeden durch; korpusweit haetten 3 von 2757 gereicht. Das ist die
    # Spiegelklasse von EMGRAV-SCHWELLE-TOT — dort liess eine Schwelle alles
    # durch, hier nichts, beide Male auf der einen Groesse kalibriert und gegen
    # eine andere geprueft.
    segment: dict | None  = _staerkstes_segment(state)
    salienz: float | None = float(segment["salienz"]) if segment else None
    verlauf: list[dict]   = state.get("nova_emotions_verlauf") or []
    user_id:      str     = state.get("user_id", "")
    character_id: str     = state.get("character_id", "")

    if salienz is None:
        logger.error(
            "Praegung-Tor: keine effektive Salienz in den pending_writes — der "
            "Node steht hinter `salience` und muesste sie sehen; Tor faellt aus, "
            "kein Faden"
        )
        return state

    if not verlauf:
        logger.error(
            f"Praegung-Tor: leerer nova_emotions_verlauf bei Salienz "
            f"{salienz:.2f} — ei_calc hat nichts geliefert, der Ausschlag ist "
            f"nicht ablesbar; Tor faellt aus, kein Faden"
        )
        return state

    # **Die Emotion des Turns, nicht die Fuehrung des Verlaufs.** Der Verlauf ist
    # eine Summe ueber die Historie und hinkt dem Reiz nach: `[gemessen]`
    # 31.08.2026 ueber acht Sektoren an einem frischen Paar erschien die
    # perzipierte `zufriedenheit` erst einen Turn spaeter im Verlauf, die
    # `traurigkeit` ebenso. Wer den Verlauf liest, gibt dem Faden den Sektor des
    # **vorigen** Turns — und darauf bauen das Sektor-Histogramm eines Strangs
    # (§7.8) und die acht Verfallsfaktoren (§7.9).
    emotion:   str   = segment.get("emotion", "")
    ausschlag: float = _ausschlag_der_emotion(verlauf, emotion)

    # ── Verarbeitung ───────────────────────────
    durch, grund = tor_urteil(salienz, ausschlag)

    faden_id: int | None = None
    embedding_quelle: str = ""
    if durch:
        embedding, embedding_quelle = _faden_embedding(
            segment.get("_segment_text", ""), state,
        )
        faden_id = faden_anlegen(
            POSTGRES_URL,
            user_id       = user_id,
            character_id  = character_id,
            emotion       = emotion,
            ausschlag_eingang = min(1.0, max(0.0, ausschlag)),
            embedding_str = ("[" + ",".join(str(x) for x in embedding) + "]"
                             if embedding else None),
            turn_id       = state.get("turn_id"),
            herkunft      = "erlebt",
            # Der erste der drei Eingaenge der Strangstaerke (§7.7): wie stark
            # der Reiz **draengte**. Der Ausschlag daneben sagt, wie stark er
            # **fuehlte** — bis zum 02.09.2026 ueberlebte die Salienz nur in der
            # Torzeile des Protokolls, und das verfaellt.
            salienz       = salienz,
        )

    # ── Ausgabe ────────────────────────────────
    # Auch die Ablehnung wird geschrieben: Eine Schwelle, deren Neins niemand
    # zaehlt, kann aufhoeren zu trennen, ohne dass es auffaellt.
    log_berechnung(
        turn_id = state.get("turn_id", "unbekannt"),
        node    = "praegung",
        quelle  = pipeline_quelle(state),
        inhalt  = {
            "schritt":   "praegung_tor",
            "salienz":   round(salienz, 3),
            "ausschlag": round(ausschlag, 3),
            "emotion":   emotion,
            "urteil":    "faden" if durch else "abgelehnt",
            "grund":     grund,
            "faden_id":  faden_id,
            # Ohne dieses Feld waere ein grob eingebetteter Faden von einem
            # scharfen nicht zu unterscheiden — und die Naehe-Schwelle der
            # Verstaerkung stuende auf gemischtem Material.
            "embedding_quelle": embedding_quelle if durch else None,
        },
        user_id      = user_id,
        character_id = character_id,
    )

    _zug_protokollieren(state, user_id, character_id)

    if durch and faden_id is None:
        logger.error(
            f"Praegung-Tor: Durchlass bei {grund}, aber kein Faden geschrieben — "
            f"die Vorbedingungen von `faden_anlegen` haben abgelehnt"
        )
    elif not durch:
        logger.debug(f"Praegung-Tor: kein Faden — {grund}")

    return state
