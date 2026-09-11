"""Admin-Endpunkte — Pixie-Steuerung für Tests und Wartung."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import (
    PIXIE_AGENTEN_PAUSE_SCHLUESSEL,
    PIXIE_DELIVERY_PAUSE_SCHLUESSEL,
    PIXIE_PAUSE_SCHLUESSEL,
    redis_client,
)
from memory.quality_profile import profil_lauf
from services.model_services.spur import SPUR_CPU, SPUR_LLM

logger = logging.getLogger("ki_server.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/pixie/pause")
def pixie_pausieren():
    """Pausiert Pixie — Scheduler **und** Zustellung.

    Der Scheduler-Job laeuft weiter und ueberspringt seine Arbeit; die
    Zustellschleife verwirft ihre Zyklen.

    **Bis zum 11.09.2026 galt die Pause nur fuer den Scheduler**, und das war
    die Haelfte, die man nicht braucht: Was fertig auf dem Stapel lag, wurde
    weiter zugestellt. `[gemessen]` Bei bestaetigtem `{"paused": true}` liefen
    fuenf Zustellungen durch und ein vollstaendiger Fremdturn mitten in einer
    Messreihe.
    """
    redis_client.set(PIXIE_PAUSE_SCHLUESSEL, "1")
    logger.info("Admin: Pixie pausiert")
    return {"status": "paused"}


@router.post("/pixie/resume")
def pixie_fortsetzen():
    """Setzt Pixie fort."""
    redis_client.delete(PIXIE_PAUSE_SCHLUESSEL)
    logger.info("Admin: Pixie fortgesetzt")
    return {"status": "resumed"}


@router.post("/pixie/agenten/pause")
def pixie_agenten_pausieren():
    """Pausiert **nur** die Hintergrundagenten — die Zustellung läuft weiter.

    Für eine Reihe, die zugestellte Impulse prüfen will: Der Stapel wird
    abgearbeitet, aber es kommt nichts Frisches dazu. Ohne diese Trennung
    schöbe sich während der Reihe ein neuer Fund dazwischen, und die
    geprüften Impulse wären andere als die vorbereiteten.

    Vorbedingung: keine — ein bereits gesetzter Schlüssel wird überschrieben,
        das ist derselbe Zustand.
    Nachbedingung: `pixie:agenten_paused` steht; der nächste Heartbeat-Zyklus
        entfällt. **Ein laufender Agent wird nicht abgebrochen** — bis zur
        Stille kann Last liegen, und die meldet `GET /admin/pixie/status`
        über `bereit_fuer_messung`.
    Fehlerfälle: Keine eigenen; ein Redis-Ausfall schlägt durch.
    """
    redis_client.set(PIXIE_AGENTEN_PAUSE_SCHLUESSEL, "1")
    logger.info("Admin: Pixie-Agenten pausiert (Zustellung laeuft weiter)")
    return {"status": "agenten_paused"}


@router.post("/pixie/agenten/resume")
def pixie_agenten_fortsetzen():
    """Setzt die Hintergrundagenten fort.

    Vorbedingung: keine — ein nicht gesetzter Schlüssel ist kein Fehler.
    Nachbedingung: `pixie:agenten_paused` ist weg. **Der Vollschalter bleibt
        unberührt**: Steht er, laufen die Agenten weiterhin nicht.
    Fehlerfälle: Keine eigenen.
    """
    redis_client.delete(PIXIE_AGENTEN_PAUSE_SCHLUESSEL)
    logger.info("Admin: Pixie-Agenten fortgesetzt")
    return {"status": "agenten_resumed"}


@router.post("/pixie/delivery/pause")
def pixie_delivery_pausieren():
    """Pausiert **nur** die Zustellung — die Agenten arbeiten weiter.

    Für eine Messung am Hintergrund: Er läuft, aber seine Ergebnisse fallen
    nicht mitten in die Reihe.

    Vorbedingung: keine.
    Nachbedingung: `pixie:delivery_paused` steht; die Zustellschleife verwirft
        ihre Zyklen, bevor sie den Stapel ansieht. Fertige Impulse bleiben
        liegen und gehen nicht verloren.
    Fehlerfälle: Keine eigenen.
    """
    redis_client.set(PIXIE_DELIVERY_PAUSE_SCHLUESSEL, "1")
    logger.info("Admin: Shadow-Delivery pausiert (Agenten laufen weiter)")
    return {"status": "delivery_paused"}


@router.post("/pixie/delivery/resume")
def pixie_delivery_fortsetzen():
    """Setzt die Zustellung fort.

    Vorbedingung: keine.
    Nachbedingung: `pixie:delivery_paused` ist weg; der Vollschalter bleibt
        unberührt.
    Fehlerfälle: Keine eigenen.
    """
    redis_client.delete(PIXIE_DELIVERY_PAUSE_SCHLUESSEL)
    logger.info("Admin: Shadow-Delivery fortgesetzt")
    return {"status": "delivery_resumed"}


@router.post("/delivery/jetzt")
async def delivery_jetzt(user_id: str = "meister",
                         riegel_uebergehen: bool = False):
    """Loest **sofort** einen Zustellversuch aus, statt auf den Takt zu warten.

    **Wozu er da ist.** Die Zustellung hängt an einer Inaktivitätsgrenze und
    an einer Riegelkette; eine Reihe, die prüfen will, *wie* ein Impuls
    formuliert ist, wartet sonst auf einen Zustand, den sie nicht herstellen
    kann. Der Endpunkt fährt denselben Pfad wie die Schleife — dieselbe
    Auswahl, dieselben Graphen, dieselbe Ablage.

    **Die Riegel gelten, wenn nichts anderes verlangt wird.** Sie entscheiden,
    *ob* zugestellt wird; für die Frage, *wie* der Beitrag klingt, sind sie
    ohne Belang. Wer sie für einen Formulierungstest übergeht, bekommt eine
    `warning` im Log — ein Instrument, das schweigt, wird vergessen und
    verfälscht die nächste Messung (dieselbe Begründung wie beim
    Umfangsregler weiter unten).

    Args:
        user_id: Das Paar, an das zugestellt wird.
        riegel_uebergehen: Setzt die Burst-Sperre zurück und markiert den
            Lauf im Log. Die Riegelkette selbst bleibt unberührt — sie
            schreibt ihre Entscheidung wie immer ins `pipeline_log`.

    Vorbedingung: Ein Client des Paares ist verbunden — sonst hätte der Impuls
        keinen Empfänger, und der Endpunkt antwortet mit 409 statt still eine
        Zustellung zu verbrauchen.
    Nachbedingung: Entweder ein vollständiger Turn samt Ablage, oder
        `zugestellt: False` mit dem Grund. Die Riegelkette schreibt ihre
        Entscheidung wie immer ins `pipeline_log`.
    Fehlerfälle: Kein Client verbunden (409, kein Nebeneffekt). Ein
        übergangener Burst wird als `warning` protokolliert — ein
        Messinstrument, das schweigt, verfälscht die nächste Messung.

    Returns:
        Was geschehen ist: `zugestellt` True/False und der Grund.
    """
    from api.websocket import aktive_verbindungen
    from services.shadow_delivery import _delivery_ausfuehren, shadow_burst_reset

    if riegel_uebergehen:
        logger.warning(
            "Admin: Zustellung mit uebergangener Burst-Sperre fuer '%s' — "
            "das ist ein Messinstrument und im Betrieb ein Defekt", user_id,
        )
        shadow_burst_reset(redis_client, user_id)

    if user_id not in aktive_verbindungen:
        logger.error(
            "Admin: Zustellung fuer '%s' verlangt, aber kein Client verbunden "
            "— der Impuls haette keinen Empfaenger", user_id,
        )
        return JSONResponse(
            status_code=409,
            content={"zugestellt": False, "grund": "kein_client_verbunden"},
        )

    erfolg: bool = await _delivery_ausfuehren(
        redis_client  = redis_client,
        user_id       = user_id,
        websocket_map = aktive_verbindungen,
    )
    logger.info("Admin: Zustellung fuer '%s' — erfolg=%s", user_id, erfolg)
    return {
        "zugestellt": erfolg,
        "grund": "" if erfolg else "riegel_oder_stapel — siehe pipeline_log/zustellung",
    }


@router.get("/pixie/status")
def pixie_status():
    """Gibt den Pixie-Status zurück — beide Hälften einzeln.

    **`paused` bleibt, was es war:** der Vollschalter. `agenten_pausiert` und
    `delivery_pausiert` sagen, ob die jeweilige Hälfte steht — durch den
    Vollschalter oder durch ihren eigenen. Wer nur `paused` liest, sieht
    sonst `false` und hält beides für laufend, während eine Hälfte steht.

    Vorbedingung: keine.
    Nachbedingung: Fünf Felder. `agenten_laufend` nennt die Spuren, deren
        Sperre gerade steht; **`bereit_fuer_messung` ist die einzige Auskunft,
        auf die eine Messreihe warten darf** — pausiert **und** still. Eine
        Pause bricht keinen laufenden Agenten ab, und zwischen ihr und der
        Stille kann volle Modellast liegen.
    Fehlerfälle: keine eigenen; ein Redis-Ausfall schlägt durch und wird
        ausdrücklich nicht abgefangen. Ein stiller Rückfall auf
        `bereit_fuer_messung: true` wäre die gefährlichste Antwort, die dieser
        Endpunkt geben kann — die Reihe liefe dann mit voller Hintergrundlast.
    """
    voll:     bool = redis_client.exists(PIXIE_PAUSE_SCHLUESSEL) > 0
    agenten:  bool = redis_client.exists(PIXIE_AGENTEN_PAUSE_SCHLUESSEL) > 0
    delivery: bool = redis_client.exists(PIXIE_DELIVERY_PAUSE_SCHLUESSEL) > 0

    # **Pausiert heisst nicht still.** Die Pause verhindert den naechsten
    # Heartbeat-Zyklus; einen laufenden Agenten bricht sie nicht ab, und das
    # ist richtig so — ein Abbruch mitten im Lauf verloere seine Arbeit.
    #
    # **Die Folge muss sichtbar sein.** `[gemessen 11.09.2026]` Eine Messreihe
    # setzte die Agenten-Pause um 09:53:40; ein Recherche-Agent lief bis
    # **10:03:41** weiter — zehn Minuten volle Modellast, waehrend der Status
    # `agenten_pausiert: true` meldete. Wer auf diese Auskunft hin misst, misst
    # den Hintergrund mit und weiss es nicht.
    #
    # Die Sperren des Schedulers beantworten die Frage: Sie stehen genau so
    # lange, wie ein Zyklus laeuft.
    laufend: list[str] = [
        spur for spur in (SPUR_LLM, SPUR_CPU)
        if redis_client.exists(f"pixie:running:{spur}")
    ]
    return {
        "paused":             voll,
        "agenten_pausiert":   voll or agenten,
        "delivery_pausiert":  voll or delivery,
        # Welche Spuren gerade arbeiten. Leer heisst still.
        "agenten_laufend":    laufend,
        # Die eine Auskunft, auf die eine Messreihe warten muss: pausiert
        # **und** still. Beides einzeln zu lesen und selbst zu verknuepfen
        # waere dieselbe Rechnung an jedem Aufrufer — und einer vergisst sie.
        "bereit_fuer_messung": (voll or agenten) and not laufend,
    }


# ── Der Messschalter fuer die Umfangszeile ────────────────────────────
#
# **Wozu er da ist.** `UMFANGSREGLER-BINDET-NICHT` verlangt als Pruefform
# *„dieselbe Turnreihe desselben Reizes mit und ohne Block"*. Ohne einen
# Schalter zur Laufzeit gaebe es diese Reihe nicht: Zwei Faehrten, durch
# einen Neustart getrennt, sind nicht dieselbe Reihe — dazwischen liegen ein
# Kaltstart, ein geleerter Prefix-Cache und ein gewachsenes Gedaechtnis.
#
# **Er liegt in Redis und nicht in der Umgebung**, aus demselben Grund wie
# `pixie:paused` (`F-MESS-2`): Eine Umgebungsvariable wird beim Import
# gelesen und waere nur mit einem Neustart zu aendern — also genau das, was
# hier vermieden werden soll.
#
# **Er ist ein Instrument und kein Merkmal.** Steht er, fehlt Nova die
# einzige Laengenzahl im Prompt; das ist im Betrieb ein Defekt und nur
# waehrend einer Messreihe erwuenscht. Deshalb meldet der Responder seinen
# Stand bei JEDEM Turn als `warning` — ein vergessener Schalter soll im Log
# schreien, nicht schweigen.
REGIE_AUS_SCHLUESSEL: str = "mess:regie_aus"


@router.post("/regie/aus")
def regie_abschalten():
    """Nimmt die Umfangszeile aus dem Responder-Prompt — nur fuer Messreihen."""
    redis_client.set(REGIE_AUS_SCHLUESSEL, "1")
    logger.warning(
        "Admin: Umfangszeile abgeschaltet — Nova bekommt ab jetzt KEINE "
        "Laengenvorgabe. Das ist ein Messzustand, kein Betriebszustand."
    )
    return {"regie_aus": True}


@router.post("/regie/an")
def regie_einschalten():
    """Stellt die Umfangszeile wieder her."""
    redis_client.delete(REGIE_AUS_SCHLUESSEL)
    logger.info("Admin: Umfangszeile wieder im Prompt")
    return {"regie_aus": False}


@router.get("/regie/status")
def regie_status():
    """Sagt, ob die Umfangszeile gerade im Prompt steht."""
    aus: bool = redis_client.exists(REGIE_AUS_SCHLUESSEL) > 0
    return {"regie_aus": aus}


@router.get("/naehte")
def naht_spannen(tage: int = 0):
    """Ist-Spanne gegen Zielspanne je Naht, in zwei Zeitfenstern.

    **Fuer das Naht-Panel des Clients.** Er zeigt, welche Groesse ihre
    Zielspanne verlaesst und welche sie kaum ausschoepft — die zweite
    Richtung hat sonst keinen Waechter.

    Args:
        tage: Breite des jungen Fensters. 0 nimmt den Vorgabewert.

    Returns:
        `{"tage": int, "naehte": [...], "fehler": int}`.
    """
    from memory.naht_spannen import FENSTER_TAGE, spannen_erheben

    ergebnis: dict = spannen_erheben(tage or FENSTER_TAGE)
    logger.info(
        "Admin: Naht-Spannen abgefragt — %d Naehte, %d Fehler",
        len(ergebnis["naehte"]), ergebnis["fehler"],
    )
    return ergebnis


# `response_model=None` ist Pflicht und keine Zierde: FastAPI leitet aus der
# Rueckgabeannotation ein Antwortmodell ab und wirft beim IMPORT, wenn dort
# ein Response-Typ steht. Der Import passiert in `main.py` auf Modulebene —
# der Fehler nimmt den ganzen Server mit, nicht nur diesen Endpunkt.
#
# `[gemessen]` — 18.08.2026: Die Annotation kam als Abhilfe gegen einen
# Linter-Befund hinzu und legte den Dienst 10 Minuten lahm. Gemerkt hat es
# keine der 1780 gruenen Zeugen: **0 von 126 Testdateien importieren die
# Anwendung.** Und `uvicorn --reload` haelt den Port im Elternprozess, auch
# wenn das Kind beim Import stirbt — die Antwort ist deshalb ein Timeout und
# nicht "Verbindung abgelehnt", und der Behaelterstatus bleibt "Up".
@router.post("/dateien/index", response_model=None)
def dateien_index_lauf() -> dict | JSONResponse:
    """Stoesst einen Lauf des Dateien-Waechters an und gibt seine Bilanz zurueck.

    Vorbedingung: keine.
    Nachbedingung: Die Bilanz des Laufs — je Wurzel und in Summe, samt der
    Zahl der Dateien, die die Obergrenze stehengelassen hat.

    **Von Hand statt nach Zeitplan, und das ist Absicht.** Die Kadenz eines
    Waechters soll der Aenderungsrate des Verzeichnisses folgen; die ist
    nicht erhoben (novaberg-agent-dateien_k.md §8.3). Bis dahin gibt es
    diesen Anstoss statt einer geratenen Zahl im Scheduler.
    """
    from agents import AgentRegistry

    agent = AgentRegistry.finden("dateien_index")
    if agent is None:
        logger.error("Admin: dateien_index nicht in der Registry")
        return JSONResponse(
            status_code=503,
            content={"fehler": "dateien_index nicht registriert"},
        )

    zustand = agent.invoke({
        "aufgabe": "Indexlauf von Hand", "aufgabe_typ": "workflow",
        "agent_name": "dateien_index", "kontext": {}, "parameter": {},
        "schritte": [], "ergebnis": None, "status": "laufend",
        "rueckfrage": None, "fehler": None,
    })

    logger.info("Admin: Indexlauf beendet — status=%s", zustand.get("status"))
    return {"status": zustand.get("status"), "bilanz": zustand.get("ergebnis")}


@router.post("/qualitaet/lauf")
def qualitaetsprofil_lauf(deckel: int = 0):
    """Stoesst den Profil-Lauf an, der sonst nur im Tageslauf laeuft.

    **Der Lauf braucht den Serverprozess**, und das ist der Grund fuer diesen
    Endpunkt: `traeger_profilieren` ruft den Hintergrund-Worker, und der lebt
    im Lifespan der Anwendung. Ein Labor-Skript daneben bekommt ihn nicht —
    `submit_sync` scheitert dort mit *Worker nicht gestartet*.

    Damit ist der Schritt messbar, ohne auf den naechsten Tageslauf zu warten;
    er schreibt dasselbe wie dort, nur frueher.

    Args:
        deckel: Wie viele Traeger hoechstens. 0 nimmt den Vorgabewert des
            Tageslaufs (`QUALITAET_PROFIL_JE_LAUF`).

    Returns:
        Die Buchfuehrung des Laufs — versucht, profiliert, gescheitert,
        Bestand und `error`.
    """
    ergebnis: dict = profil_lauf(deckel=deckel)
    logger.info(
        f"Admin: Qualitaetsprofil-Lauf angestossen — "
        f"{ergebnis['profiliert']} von {ergebnis['versucht']} profiliert"
    )
    if ergebnis.get("error"):
        return JSONResponse(status_code=500, content=ergebnis)
    return ergebnis
