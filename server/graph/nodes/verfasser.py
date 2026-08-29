"""
Verfasser Node — bestimmt den fachlichen Inhalt der Antwort.

Sitzt zwischen GV-Node und Responder. Er sieht das Wissen — Gedaechtnis,
Web-Recherche, Aufgabe, Gespraechsvektor — und entscheidet, WAS gesagt wird.
Der Responder bekommt das Ergebnis fertig und gibt ihm Novas Form.

**Warum die Trennung.** Der Responder entschied bisher in einem Zug ueber
Substanz und Klang. Der Preis steht als Kommentar in `responder.py`: Der
Sprachstil-Block musste ans Ende der Nutzer-Nachricht wandern, "dort, wo eine
Anweisung gegen 8.400 Tokens fremder Prosa noch etwas ausrichtet". Eine
Stilanweisung, die sich ihren Platz erkaempfen muss, steht nicht dort, wo sie
hingehoert, sondern dort, wo sie ueberlebt.

**Was der Responder dadurch verliert, ist der tragende Teil:** Gedaechtnis und
Web-Recherche sieht er nicht mehr. Er kann dann nichts aus einem Wissen
erfinden, das ihm gar nicht vorliegt.

**Die Bloecke werden verschoben, nicht umformuliert.** `[GEDAECHTNIS]`,
`[WEB-RECHERCHE]` und die `[AUFGABE]`-Varianten sind dieselben Prompt-
Bausteine, die der Responder benutzt hat. Eine Umformulierung im selben Zug
haette den Schnitt mit einer Prompt-Ueberarbeitung vermischt: Bei einer
Verschlechterung waere nicht mehr trennbar, welche der beiden es war.

Konzept: novaberg-node-verfasser_k.md
"""

import logging
from datetime import datetime

from config import PROMPTS, get_node_config
from ei.haltungssprache import stoffzeilen
from graph.einwand import kopf_anweisung, urteil_lesen

# Die Marke gehoert zum Vertrag von `gv_detail` und hat genau eine Quelle.
# Sie hier als Literal zu wiederholen waere der zweite Ort fuer denselben
# Wert — und der Fall, in dem sie gebraucht wird, ist
# genau der, in dem niemand hinsieht.
from graph.nodes.gespraechsvektor import VORAUSDENKEN_GELAUFEN
from graph.reiz import reiz_ist_eigener_gedanke, reiz_text
from graph.state import ConversationState
from graph.vorzeichen import Vorzeichenbefund, vorzeichen_pruefen
from memory.pipeline_log import log_berechnung
from memory.session import (
    Verlaufsbeitrag,
    fenster_waehlen,
    sprecher_bezeichnen,
    verlauf_gruppieren,
)
from services.model_services import ChatRequest, model_service

#: Wieviele Wortwechsel der Verfasser im Verlauf sieht. Vorher sah er den
#: ganzen `session_turns`-Bestand; die Zahl ist die Obergrenze, die es bis
#: zum 24.08.2026 nicht gab, und sie liegt bewusst hoeher als die fuenf der
#: uebrigen Leser: Der Verfasser bestimmt den Inhalt und braucht den Bezug
#: auf frueher Gesagtes.
VERFASSER_WORTWECHSEL: int = 8

logger = logging.getLogger("ki_server.verfasser")


def _gespraechsvektor_block(state: ConversationState) -> str:
    """Baut den [GESPRAECHSVEKTOR]-Block aus dem Ergebnis des GV-Node.

    Traegt Landschaft, Strategie, Absicht, Vehikel und den Leitgedanken —
    alle vier gehoeren zum Inhalt. Auch das Vehikel: Ob geantwortet,
    zurueckgefragt oder geschwiegen wird, ist eine Entscheidung ueber die
    Substanz und laesst sich nicht stilistisch nachformen
    (novaberg-node-verfasser_k.md §2.1).

    Der Zusatz "Finde deine eigenen Worte" des alten Responder-Blocks
    entfaellt: Das ist ab jetzt die Aufgabe der zweiten Stufe und keine Bitte
    mehr (§2.4).

    **Der Block haengt an der Landschaft, nicht an der Hypothese.** Bis zum
    14.08.2026 kehrte er bei leerem `gespraechsvektor` sofort leer zurueck —
    und nahm die Landschaft mit, obwohl sie in `gv_detail` steht. Der GV-Node
    war am 08.08.2026 ausdruecklich so umgebaut worden, dass sie **jeden**
    Turn traegt; diese Zeile hob das fuer den Verfasser wieder auf. Gemessen
    am 13.08.2026: In **15 von 26** Verfasser-Laeufen stand gar kein Block,
    waehrend der Auftrag viermal auf ihn verwies. Der Responder macht es
    richtig und liest `gv_detail` unmittelbar.

    **Der Ausfall des Vorausdenkens wird benannt, nicht verschwiegen.** Eine
    fehlende Strategie ist eine Vorgabe — naemlich die des Vorgabewerts, den
    das Modell aus der Dichte seines Materials waehlt. Welcher der beiden
    Faelle vorliegt, sagt `vorausdenken`: Der leere Strategie-String allein
    trueg den Unterschied nicht, weil `korridor_pruefen` ihn auch auf einem
    gelaufenen Turn leert.

    Vorbedingung: `state` stammt aus dem CharacterGraph.
    Nachbedingung: Leerer String genau dann, wenn keine Landschaft vermessen
    wurde — das ist der Zustand vor dem ersten Turn und der einzige Fall, in
    dem der Auftrag ins Leere zeigt.
    Fehlerfaelle: keine — ein fehlendes Vorausdenken ist kein Defekt, sondern
    eine Entscheidung des GV-Node, und der Block sagt sie an.

    Returns:
        Der Block oder ein leerer String.
    """
    # ── Eingabe-Validierung ─────────────────────
    detail:  dict = state.get("gv_detail") or {}
    cluster: str  = detail.get("cluster", "")
    if not cluster:
        return ""

    # ── Verarbeitung ────────────────────────────
    from ei.dreischicht import (
        CLUSTER_BESCHREIBUNGEN,
        STRATEGIE_NAMEN,
    )

    strategie: str = detail.get("strategie", "")
    vehikel:   str = detail.get("vehikel", "")
    impuls:    str = detail.get("impuls", "")
    hypothese: str = state.get("gespraechsvektor", "")

    # Die Fragenfrequenz aus `CLUSTER_FRAGEN` steht hier seit dem 22.08.2026
    # **nicht** mehr, aus demselben Grund wie im Responder seit dem
    # 13.08.2026 (`graph/nodes/responder.py`): Dieselbe Aussage kommt aus der
    # Haltungsgroesse `fragen`, und zwar **charakterabhaengig** statt fuer
    # jede Nova gleich. Sie erreicht diesen Knoten als Rueckfrage-Zeile des
    # `[MASS]`-Blocks (`ei/haltungssprache.py::stoffzeilen`), seit der Block
    # am 20.08.2026 dazukam.
    #
    # Bis dahin stand hier eine Zeile ohne Bedingung: Keine der drei
    # Pruefbedingungen des Auftrags verlangte etwas von ihr, und das Vehikel
    # der Dreischicht sagt fuer den einzelnen Turn ohnehin, ob gefragt wird
    # (`FRAGEN-ZEILE-OHNE-BEDINGUNG`). Zuletzt war sie nicht mehr nur
    # wirkungslos, sondern eine zweite Stimme: *„Selten, jeder 3.-4. Turn"*
    # kann gegen eine hohe charakterabhaengige Rueckfrage-Vorgabe stehen.
    #
    # Die Tabelle bleibt, weil der GV-Knoten sie fuer die Strategiewahl
    # braucht (`ei/dreischicht.py`) und die Haltungsgroesse aus ihr
    # uebersetzt ist (`ei/haltung.py`).
    zeilen: list[str] = [
        f"Gespraechslandschaft: {cluster.capitalize()} — "
        f"{CLUSTER_BESCHREIBUNGEN.get(cluster, '')}",
    ]

    if strategie:
        satz: str = (
            f"Die gewaehlte Strategie: "
            f"{STRATEGIE_NAMEN.get(strategie, strategie)}"
        )
        if vehikel:
            satz += f" als {vehikel.capitalize()}"
        zeilen.append(satz + ".")

    if hypothese:
        zeilen.append("")
        zeilen.append("So bewegt sich das Gespraech gerade.")
        zeilen.append("")
        zeilen.append(hypothese)

    if impuls:
        zeilen.append("")
        zeilen.append(f"Leitgedanke fuer diese Antwort: {impuls}")

    # Die Ansage des Ausfalls. Sie steht zuletzt, damit sie nicht zwischen
    # Landschaft und Hypothese gelesen wird, als gehoerte sie zur Lage.
    if detail.get("vorausdenken", "") != VORAUSDENKEN_GELAUFEN:
        zeilen.append("")
        zeilen.append(
            "Fuer diesen Turn wurde nicht vorausgedacht: Es gibt weder eine "
            "gewaehlte Strategie noch einen Leitgedanken. Die Landschaft "
            "oben ist die ganze Vorgabe."
        )
    elif not strategie:
        zeilen.append("")
        zeilen.append(
            "Fuer diesen Turn steht kein Mittel fest. Die Landschaft oben "
            "ist die Vorgabe."
        )

    # ── Ausgabe ─────────────────────────────────
    return "[GESPRAECHSVEKTOR]\n" + "\n".join(zeilen)


def _aufzeichnungen_block(state: ConversationState) -> str:
    """Baut die Aufzeichnungs-Bloecke aus den Treffern des Dateien-Index.

    **Es sind zwei, seit dem 22.08.2026, und sie unterscheiden sich in einer
    Aussage:** `[AUFZEICHNUNGEN]` sagt *fremde Aufzeichnungen*,
    `[EIGENE FUNDE]` sagt *deine Arbeit*. Der zweite Name enthaelt den ersten
    bewusst **nicht** als Teilzeichenkette: Jede Pruefung, die einen Prompt an
    `[AUFZEICHNUNGEN]` zerteilt, traefe sonst auch den Eigen-Block und
    zerlegte ihn an der falschen Stelle — still. Welcher gilt, entscheidet
    `eigentum` an der **Wurzel** — eine Datei hat keinen Eigentuemer, eine
    Freigabe schon (§2.2).

    **Der Anlass ist gemessen.** Bis dahin gab es nur den Fremd-Block, und er
    behauptete von jedem Treffer, er sei fremd. Fuer `/files` und `/docs`
    stimmt das; fuer die Recherchen, die ihr eigener Hintergrundprozess
    ablegt, ist es die Anweisung, das eigene Material einem anderen
    zuzuschreiben. Am 22.08.2026 antwortete sie auf die ausdrueckliche
    Korrektur *„Du recherchierst ja, nicht ich"* mit *„die ganze Recherche war
    dein Werk, nicht meins. Ich habe nur beobachtet."*

    **`gemischt` laeuft in den Fremd-Block.** Eine Wurzel, bei der beides
    liegen kann, traegt keine Zusicherung, dass ein einzelner Treffer ihrer
    ist — und der teurere Fehler ist, Fremdes als eigenes auszugeben.

    Vorbedingung: `state["aufzeichnungen"]` traegt die Treffer dieses Turns
    (`agents.dateien_index.aufzeichnungen.Aufzeichnung`), moeglicherweise
    keine. Der Enricher setzt den Kanal in jedem Turn.
    Nachbedingung: Leerer String genau dann, wenn kein Treffer vorliegt —
    **ein Turn ohne diesen Block ist der Normalfall und kein Ausfall**
    (novaberg-agent-dateien_k.md §3.0a-bis). Sonst ein Block, in dem jeder
    Eintrag seine Fundstelle traegt.
    Fehlerfaelle: keine.

    **Der Block steht getrennt von [GEDAECHTNIS], und das ist seine Aussage**
    (§1a.2). Was in den Dateien steht, ist nicht Novas Erinnerung und nicht
    ihr Wissen; wer es unbeschriftet in denselben Block legt, bekommt den
    Fehler aus dem offenen Praezedenzfall mit schlechterer Quelle — dort hat
    sie die Biografie eines Menschen als ihre eigene uebernommen.

    **Die Fundstelle je Eintrag ist nicht kuerzbar.** Eine Aufzeichnung ohne
    Herkunft ist von einer Behauptung nicht zu unterscheiden — sie ist das,
    was "ich habe hier Aufzeichnungen" ueberpruefbar macht statt zur Floskel.
    Und sie hat eine zweite Aufgabe, die schwerer wiegt als die erste
    (§1a.4): Laeuft die Antwort durch den Gespraechsgraphen und wird bei
    hoher Salienz gespeichert, ist die Beschriftung das Einzige, was die
    Herkunft ueber den Gedaechtnis-Uebergang traegt. Faellt sie im Wortlaut
    weg, liegt beim naechsten Mal eine herkunftslose Aussage im Gedaechtnis.
    """
    # ── Eingabe-Validierung ─────────────────────
    treffer: list = state.get("aufzeichnungen") or []
    if not treffer:
        return ""

    # ── Verarbeitung ────────────────────────────
    # Getrennt nach Eigentum, und die Trennung ist der Zweck des Blocks: Der
    # Text des einen sagt "fremde Aufzeichnungen", der des anderen "deine
    # Arbeit". Eine gemeinsame Liste unter einer der beiden Ueberschriften
    # ist fuer die andere Haelfte eine falsche Aussage.
    eigene:  list = [e for e in treffer if getattr(e, "eigentum", "nutzer") == "figur"]
    fremde:  list = [e for e in treffer if getattr(e, "eigentum", "nutzer") != "figur"]

    bloecke: list[str] = []
    for menge, prompt_name, marke in (
        (eigene, "verfasser.eigene_aufzeichnungen", "[EIGENE FUNDE]"),
        (fremde, "verfasser.aufzeichnungen",        "[AUFZEICHNUNGEN]"),
    ):
        if not menge:
            continue
        zeilen: list[str] = [
            f"- {eintrag.fundstelle}: {eintrag.thema}"
            + (f" — {eintrag.zusammenfassung}" if eintrag.zusammenfassung else "")
            for eintrag in menge
        ]
        bloecke.append(PROMPTS[prompt_name].format(aufzeichnungen="\n".join(zeilen)))
        logger.info(
            f"Verfasser: {marke} mit {len(zeilen)} Eintrag(en), "
            f"Kosinus {menge[0].kosinus:.4f} bis {menge[-1].kosinus:.4f}"
        )

    # ── Ausgabe-Verifikation ────────────────────
    if not bloecke:
        logger.error(
            "Verfasser: %d Aufzeichnungstreffer, aber kein Block gebaut — "
            "kein Eintrag fiel in eine der beiden Mengen",
            len(treffer),
        )
        return ""
    return "\n\n".join(bloecke)


def _question_target(sachlage: dict, state: dict) -> tuple[str | None, bool]:
    """Der Rueckfrage-Gegenstand der Lage und ob er Novas eigener Zug ist.

    Vorbedingung: `sachlage` ist das Artefakt des Turns (auch leer); `state`
        traegt `aktivierte_ziele` oder nicht.
    Nachbedingung: (Gegenstand oder None, eigener Zug) — protokolliert, auch
        wenn es keinen Gegenstand gibt: »keiner« ist eine Auskunft.
    """
    from graph.nodes.sachlage import GEGENSTAND_EIGENER_ZUG, question_target_origin
    quelle: tuple[str, str] | None = question_target_origin(
        sachlage, state.get("aktivierte_ziele") or [],
    )
    gegenstand: str | None = quelle[0] if quelle else None
    eigener_zug: bool = bool(quelle) and quelle[1] == GEGENSTAND_EIGENER_ZUG
    logger.info(
        f"Verfasser: Rueckfrage-Gegenstand: "
        f"{gegenstand[:80] if gegenstand else 'keiner'}"
        f"{' (Novas eigener Zug)' if eigener_zug else ''}"
    )
    return gegenstand, eigener_zug


def _build_system_prompt(state: ConversationState) -> str:
    """Baut den System-Prompt des Verfassers: Auftrag plus Wissen.

    Enthaelt ausdruecklich KEINE Identitaet, keine Emotion, keinen Sprachstil
    und keine Direktiven — die gehoeren zur Form und damit zum Responder.

    Vorbedingung: `state` traegt `memory_context`, `web_context` und
    `aufzeichnungen` (jedes moeglich leer).
    Nachbedingung: Der Auftragsblock steht immer, die Wissensbloecke nur, wenn
    sie Inhalt haben. **[GEDAECHTNIS] und [AUFZEICHNUNGEN] bleiben zwei
    Bloecke** — die Trennung ist eine Aussage ueber die Herkunft und keine
    Formatierung (novaberg-agent-dateien_k.md §1a.2).
    Fehlerfaelle: keine.

    Returns:
        Der System-Prompt.
    """
    # ── Verarbeitung ────────────────────────────
    jetzt = datetime.now()

    # Die drei Saetze stammen woertlich aus dem [IDENTITAET]-Block des
    # Responders. Sie sprechen ueber Gedaechtnis, Kontext und Web-Zugriff —
    # also ueber das Wissen, das seit der Trennung hier liegt. Verschoben,
    # nicht umformuliert: Eine Ueberarbeitung im selben Zug haette den Schnitt
    # mit einer Prompt-Aenderung vermischt.
    teile: list[str] = [
        PROMPTS["verfasser.auftrag"],
        # Der Kopfblock wird im Code gebaut, nicht im Prompttext ausgeschrieben:
        # Die gueltigen Bewertungen und Quellen stehen in `graph/einwand.py` und
        # duerfen nirgends ein zweites Mal stehen (13_DATENSTRUKTUREN §3).
        kopf_anweisung(),
        # **Die Herkunft des Reizes entscheidet ueber die Perspektive.**
        # Ein Pixie-Impuls reist auf dem Platz der Nutzereingabe; wer ihn ohne
        # diese Frage liest, schreibt Novas eigenen Gedanken ihrem Gegenueber
        # zu. Gemessen am 13.08.2026: **13 von 14 Impulsen** eines Tages
        # begannen mit "Du hast ...", fuenf davon wortgleich — obwohl der
        # Responder seinen Schutzblock gesetzt hatte. Die Zuschreibung stand
        # schon im Material, das hier entsteht
        # (`novaberg-bugs.md` -> VERFASSER-KENNT-DIE-QUELLE-NICHT).
        PROMPTS["verfasser.eigener_impuls"] if reiz_ist_eigener_gedanke(state)
        else PROMPTS["verfasser.fremder_reiz"],
        # Die Anreden folgen der Konstellation des Auftrags: "du" ist der
        # Verfasser, ueber Person A wird in dritter Person gesprochen, und der
        # Mensch heisst Person B. Vorher stand hier "den NUTZER" und "mit
        # deinen" — ein zweites Namenssystem im selben Prompt. Genau daran ist
        # der Responder am 13.08.2026 gemessen worden: In sieben von dreizehn
        # Bloecken wurde geduzt, und "du" meinte drei verschiedene Personen.
        f"Heute ist {jetzt.strftime('%A, %d.%m.%Y')}, es ist {jetzt.strftime('%H:%M')} Uhr.\n"
        "Der Charakter-Kontext im Gedaechtnis beschreibt PERSON B — verwechsle\n"
        "seine Eigenschaften nicht mit denen von Person A.\n"
        "Erwaehne nur Informationen die im Kontext stehen. Erfinde keine Details.\n"
        "Person A hat Zugriff auf aktuelle Informationen aus dem Internet ueber eine\n"
        "lokale Suchmaschine. Der Inhalt sagt nie, sie habe keinen Internetzugang.",
    ]

    # Der fertige [AUFGABE]-Block des Planners — unveraendert uebernommen.
    # Die Interpretation gehoert zum Produzenten; der Verfasser setzt ihn ein
    # wie der Responder es tat.
    task_block: str = state.get("task_block", "")
    if task_block:
        teile.append(task_block)

    # ── Die Sachlage, vor der Gespraechslage ──
    # Das sachliche Verstehen (graph/nodes/sachlage.py) steht VOR dem
    # Gespraechsvektor: erst worum es geht, dann wie sich das Gespraech
    # bewegt. Fehlt sie, faellt der Block laut aus — dieselbe Bauart wie
    # bei der Haltung unten.
    sachlage: dict = state.get("sachlage") or {}
    if sachlage.get("gegenstand") or sachlage.get("nutzerziel"):
        from graph.nodes.sachlage import LESER_VERFASSER, sachlage_block
        teile.append(sachlage_block(sachlage, leser=LESER_VERFASSER))
    elif sachlage.get("herkunft"):
        # Der Knoten LIEF und hat regulaer nichts — Novas Impuls oder ein
        # Ausfall ohne Vorgaenger. Ein `error` behauptete hier eine falsche
        # Diagnose (Fund der zweiten Kontrolle, 28.08.2026): Jeder Impuls
        # nach Gespraechspause erzeugte eine Fehlerzeile, obwohl nichts
        # defekt war.
        logger.info(
            f"Verfasser: Sachlage ohne Inhalt "
            f"(herkunft={sachlage['herkunft']}) — kein [SACHLAGE]-Block"
        )
    else:
        logger.error(
            "Verfasser: Keine Sachlage im Zustand — der Knoten `sachlage` "
            "ist nicht gelaufen."
        )

    # ── Die Bruecke: von jetzt zu damals (Scheibe 4) ──
    # Auf einem Impuls-Turn traegt der Zustand die Verlaufszeile des
    # Ausloesers; der Block sagt dem Verfasser, woran der Gedanke anknuepft.
    # Fehlt sie, fehlt der Block — ohne Meldung: Der Knoten hat schon
    # protokolliert, warum (kein Ausloeser, keine Zeile, unter der Schwelle).
    bruecke: dict = state.get("sachlage_bruecke") or {}
    if bruecke.get("damals"):
        from graph.nodes.sachlage import sachlage_bridge_block
        teile.append(sachlage_bridge_block(bruecke))

    gv_block: str = _gespraechsvektor_block(state)
    if gv_block:
        teile.append(gv_block)

    # ── Das Mass, unmittelbar hinter der Landschaft ──
    #
    # **Der Verfasser ist der zweite Leser der Haltung, und das Konzept hat
    # ihn von Anfang an so vorgesehen:** *„Ein eigener Knoten, vor der
    # Verzweigung zum Verfasser. Beide lesen das Ergebnis aus dem Zustand"*
    # (`novaberg-haltungsraum_k.md`, »Wer rechnet«). Genau daraus folgt die
    # Position des Knotens im Graphen — und bis zum 20.08.2026 loeste sie
    # niemand ein: `haltung` kam in diesem Modul nicht vor.
    #
    # **Drei der fuenf Groessen betreffen den Inhalt.** `umfang` nennt das
    # Konzept ausdruecklich (der Verfasser liest, *wie viel es zu sagen gibt*),
    # `fragen` und `draengen` stehen woertlich in seinem eigenen Auftrag: er
    # bestimmt, *„was sie feststellt, was sie offen laesst, was sie
    # zurueckfragt"*. `naehe` und `waerme` bleiben beim Responder — sie sind
    # reiner Ton, und ihn hier zu wiederholen waere die Doppelung, die der
    # Umbau vom 13.08.2026 beseitigt hat.
    #
    # **Fehlt die Haltung, faellt der Block laut aus.** Ein stilles Weglassen
    # waere von einer Lage ohne Vorgabe nicht zu unterscheiden — dieselbe
    # Bauart wie im Responder.
    haltung = state.get("haltung")
    if haltung is None:
        logger.error(
            "Verfasser: Keine Haltung im Zustand — dieser Turn bekommt KEINE "
            "Mengen-, Rueckfrage- und Vorschlagsvorgabe. Der Knoten "
            "`haltungsraum` ist nicht gelaufen."
        )
    else:
        # Dieselbe Ausnahme wie im Responder: Auf einem Impuls-Turn traegt
        # `reiz_text` Novas eigenen Gedanken (`F-REIZ-1`), und die geerbten
        # Intentionen stammen vom letzten Menschenturn. Beides taugt nicht
        # als Mass fuer den Stoff dieses Turns.
        eigener: bool = reiz_ist_eigener_gedanke(state)
        reiz_zeichen: int = 0 if eigener else len(reiz_text(state))
        intentionen: tuple[str, ...] = () if eigener else tuple(
            state.get("user_intentionen") or (),
        )
        # Scheibe 3 des Lage-Konzepts: Die Rueckfrage bekommt ihren Gegenstand
        # aus der Sachlage — die wichtigste offene Eigenschaft eines akuten
        # Objekts oder das Vorhaben des kurzfristigen Ziels. Ob daraus eine
        # Frage wird, entscheidet weiter die Haltung in der Zeile selbst.
        gegenstand, eigener_zug = _question_target(sachlage, state)
        teile.append(
            "[MASS]\n" + "\n".join(
                stoffzeilen(haltung, reiz_zeichen, intentionen, gegenstand, eigener_zug),
            ),
        )

    if state.get("memory_context"):
        teile.append(
            PROMPTS["responder.gedaechtnis"].format(
                memory_context=state["memory_context"]
            )
        )

    # Unmittelbar hinter dem Gedaechtnis, weil die Nachbarschaft die Grenze
    # lesbar macht: Der eine Block ist ihre Erinnerung, der andere ist es
    # nicht. Getrennt sind sie ohnehin — hier stehen sie so, dass der
    # Unterschied im Prompt sichtbar wird und nicht bloss zutrifft.
    aufzeichnungen_block: str = _aufzeichnungen_block(state)
    if aufzeichnungen_block:
        teile.append(aufzeichnungen_block)

    if state.get("web_context"):
        teile.append(
            PROMPTS["responder.web"].format(web_context=state["web_context"])
        )

    # ── Der Gedanke als Material, nicht als Rede ──
    # Er steht **hier**, neben Gedaechtnis und Recherche, und ausdruecklich
    # nicht als Nachricht in der Rolle des Gegenuebers. Was auf jenem Platz
    # steht, wird von einem Sprachmodell beantwortet, eingeordnet und jemandem
    # zugeschrieben — vier Anlaeufe im Prompttext haben dagegen angeschrieben
    # und verloren. Gemessen am 14.08.2026, 19:15 UTC, mit bereits leerem
    # Reiz-Platz: "PERSON B stellt die physikalische Beobachtung ... in den
    # Raum", obwohl Person B nichts gesagt hatte. Eine Rollenzuweisung ist
    # keine Anweisung, sie ist eine Struktur.
    if reiz_ist_eigener_gedanke(state):
        teile.append(
            PROMPTS["verfasser.eigener_gedanke"].format(gedanke=reiz_text(state))
        )

    # ── Ausgabe ─────────────────────────────────
    return "\n\n".join(teile)


def verfassen(state: ConversationState) -> ConversationState:
    """Bestimmt den fachlichen Inhalt der Antwort und legt ihn in den State.

    Vorbedingung: Der Reiz dieses Durchlaufs ist gesetzt — die Nutzer-
    Aeusserung auf einem Nutzer-Turn, Novas Gedanke auf einem Impuls-Turn.
    **Nicht `user_prompt`:** Auf einem Impuls-Turn hat niemand gesprochen, und
    dieses Feld ist dort leer. Der Aufrufer stellt sicher, dass
    dieser Node bei `task_context_cut=True` gar nicht erst laeuft — dort ist
    das Wenig-Kontext-Verhalten Absicht (novaberg-node-verfasser_k.md §5.1).
    Nachbedingung: `antwort_inhalt` traegt einen nicht-leeren Text.
    Fehlerfaelle: Leerer Prompt oder leere Modellantwort — beides laut
    gemeldet, `antwort_inhalt` bleibt leer. **Kein Ersatztext und kein
    Rueckfall auf die alte Responder-Bauart:** Ein Ausfall darf nicht wie eine
    Antwort aussehen (§5.3).

    Returns:
        Der State mit gesetztem `antwort_inhalt`.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Der Reiz, nicht der Reiz-Platz: Auf einem Impuls-Turn steht die Vorlage
    # in `eigener_gedanke`, und ein leerer `user_prompt` ist dort kein Ausfall,
    # sondern die Auskunft, dass niemand gesprochen hat.
    reiz: str = reiz_text(state)
    if not reiz.strip():
        # Die Meldung nennt die Herkunft: Ohne sie ist ein Nutzer-Turn ohne
        # Eingabe von einem Impuls ohne Gedanken nicht zu unterscheiden — zwei
        # Defekte an zwei verschiedenen Stellen, mit derselben Zeile.
        logger.error(
            "Verfasser: leerer Reiz (herkunft=%s) — es gibt nichts zu "
            "beantworten, antwort_inhalt bleibt leer",
            "eigener_impuls" if reiz_ist_eigener_gedanke(state) else "nutzer_turn",
        )
        state["antwort_inhalt"] = ""
        return state

    # ── Verarbeitung ────────────────────────────
    system_prompt: str = _build_system_prompt(state)

    # Der Verlauf gibt dem Inhalt seinen Bezug: Ohne ihn beantwortet der
    # Verfasser jede Rueckfrage als staende sie allein.
    # **Der Verlauf steht als benannter Textblock, nicht als Nachrichtenfolge**
    # — seit dem 24.08.2026, und die Wahl ist begruendet.
    #
    # Vorher trug jeder Turn seine Chat-Rolle: `user` oder `assistant`. Damit
    # ist die **Person** eindeutig und der **Anlass** nicht — ein Eigen-Impuls
    # und eine Antwort auf eine Frage sind beide `assistant`, und Nova hielt
    # daraufhin ihren eigenen Vorschlag fuer den des Nutzers
    # (`IMPULS-FAELLT-AUS-DEM-VERLAUF`).
    #
    # In einer Chat-Nachricht gibt es fuer den Anlass nur einen Platz: den
    # Inhalt. **Genau dort darf er nicht stehen.** Ein Praefix im Text der
    # eigenen Aeusserung ist Iteration 1 aus `novaberg-pixie_l_kontamination.md`
    # — das Modell hat den Marker damals mitgeschrieben. Im Textblock steht
    # der Anlass in der **Sprecherzeile**, also im Rahmen und nicht in Novas
    # Mund; dieselbe Form faehrt der Responder.
    #
    # Der Preis ist benannt: Das Modell sieht den Verlauf nicht mehr in seinem
    # nativen Format. Woran ein Rueckschlag zu erkennen waere: `(von sich aus)`
    # taucht in Novas Antworten auf, oder der Bezug auf frueher Gesagtes wird
    # schlechter als vorher.
    gruppen: list[list[Verlaufsbeitrag]] = fenster_waehlen(
        verlauf_gruppieren(state.get("session_turns", [])), VERFASSER_WORTWECHSEL,
    )
    verlauf_zeilen: list[str] = []
    for gruppe in gruppen:
        for beitrag in gruppe:
            wer: str = sprecher_bezeichnen(beitrag, nova_name="Nova")
            verlauf_zeilen.append(f"{wer}: {beitrag.inhalt}")

    messages: list[dict] = []
    if verlauf_zeilen:
        messages.append({"role": "user", "content": (
            "[GESPRAECHSVERLAUF]\n"
            "Bisherige Turns dieses Gespraechs, aelteste zuerst. "
            "`Nova (von sich aus)` heisst: Diese Aeusserung hat sie selbst "
            "begonnen, niemand hat danach gefragt.\n\n"
            + "\n".join(verlauf_zeilen)
        )})

    # **Auf einem Impuls-Turn bleibt der Platz des Gegenuebers leer.** Der
    # Gedanke steht als Block im System-Prompt; hier steht nur der Auftrag,
    # denn die Nachrichtenfolge darf nicht leer sein und ein Auftrag ist keine
    # fremde Rede. Der Zeuge dafuer prueft die Nachrichtenfolge, nicht den
    # Prompttext — eine Gegenprobe im Text war viermal gruen, waehrend das
    # Verhalten blieb.
    if reiz_ist_eigener_gedanke(state):
        messages.append({
            "role": "user", "content": PROMPTS["verfasser.auftrag_ohne_reiz"],
        })
    else:
        # Der Reiz steht immer als eigene Nachricht. Die fruehere Bedingung
        # `messages[-1]["content"] != reiz` verglich gegen den letzten Turn
        # der Folge; seit der Verlauf **ein** Block ist, verglich sie gegen
        # den ganzen Block und war damit immer wahr — eine Pruefung, die
        # nicht mehr prueft. Die Doppelung, die sie verhindern sollte, kann
        # nicht mehr entstehen: Der Verlaufsblock traegt den aktuellen Reiz
        # nicht, weil `session_turns` ihn beim Verfasser noch nicht enthaelt.
        messages.append({"role": "user", "content": reiz})

    # Log: Inhalt direkt ausgeben, ohne JSON-Wrapping — dieselbe Form wie beim
    # Responder, damit sich beide Stufen im Log gegenueberstellen lassen.
    messages_text: str = "\n\n".join(
        f"═══ {m['role'].upper()} ═══\n{m['content']}" for m in messages
    )

    logger.info(
        "=== VERFASSER LLM-INPUT ===\n"
        "═══ SYSTEM-PROMPT ═══\n%s\n\n"
        "%s\n"
        "=== ENDE VERFASSER LLM-INPUT ===",
        system_prompt,
        messages_text,
    )

    node_cfg = get_node_config("verfasser")

    antwort = model_service.chat.submit_sync(ChatRequest(
        messages          = messages,
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.4),
        top_p             = node_cfg.get("top_p"),
        repeat_penalty    = node_cfg.get("repeat_penalty"),
        presence_penalty  = node_cfg.get("presence_penalty"),
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "verfasser",
    ))

    # ── Ausgabe-Verifikation ────────────────────
    roh: str = (antwort.text or "").strip()
    if not roh:
        logger.error(
            "Verfasser: Modell lieferte keinen Inhalt (Tokens: %s) — "
            "antwort_inhalt bleibt leer, der Responder hat nichts zu formen",
            antwort.token_total,
        )
        state["antwort_inhalt"] = ""
        return state

    # Kopfblock vom Inhalt trennen (B1). Misslingt der Kopf, bleibt die Prosa
    # erhalten — ein ausgefallenes Urteil darf den Turn nicht kosten.
    urteil, inhalt = urteil_lesen(roh)
    state["einwandsurteil"] = urteil

    if not inhalt:
        logger.error(
            "Verfasser: nach dem Kopfblock blieb kein Inhalt (%s Zeichen roh) — "
            "antwort_inhalt bleibt leer",
            len(roh),
        )
        state["antwort_inhalt"] = ""
        return state

    if not urteil.geliefert:
        # Laut, nicht still: Ohne diese Zeile ist ein ausgefallener Kopfblock
        # in der Fallenbatterie von einem Turn ohne Einwand nicht zu
        # unterscheiden, und die Rate zaehlte Ausfaelle als Erfolge.
        # Der Auszug traegt den **ganzen** Kopfblock, nicht seinen Anfang.
        # `[gemessen]` — 22.08.2026: Mit 120 Zeichen endete er mitten im
        # zweiten von fuenf Feldern. Ein Auszug, aus dem sich die Ursache
        # nicht bestimmen laesst, macht den Ausfall zwar sichtbar, aber nicht
        # untersuchbar — fuenf protokollierte Faelle liessen offen, woran sie
        # scheiterten.
        logger.error(
            "Verfasser: kein lesbares Urteil im Kopfblock — die Ausbausperre "
            "greift in diesem Turn nicht. Kopfblock der Rohantwort (%d Zeichen "
            "gesamt): %r",
            len(roh), roh[:500],
        )

    state["antwort_inhalt"] = inhalt

    # ── B4 Stufe 1: die Vorzeichenpruefung ──────
    # Zaehlt, ohne zu aendern. Sie steht hier, weil hier zum ersten und
    # einzigen Mal drei Dinge zusammen vorliegen: das Urteil, die
    # den Reiz dieses Turns und Novas Text. Nachgelagert waere sie nicht
    # baubar — das Urteil wird nirgends persistiert.
    #
    # Der Eintrag entsteht NUR bei 'abweichend'. Das ist die Gegenprobe des
    # Bauteils: Ein Turn ohne Einwand hinterlaesst keine Spur, sonst waere
    # die Rate nicht lesbar.
    befund: Vorzeichenbefund = vorzeichen_pruefen(urteil, reiz, inhalt)
    if befund.geprueft:
        log_berechnung(
            turn_id      = state.get("turn_id", ""),
            node         = "verfasser",
            quelle       = "vorzeichenpruefung",
            inhalt       = {
                "werte":            befund.werte,
                "uebernommen":      befund.uebernommen,
                "kandidat":         befund.kandidat,
                # Getrennt gefuehrt, weil "kein Wert gefunden" etwas anderes
                # ist als "kein Wert uebernommen" — sonst zaehlte eine
                # ausgeschriebene Zahl wie ein Erfolg.
                "werte_gefunden":   len(befund.werte),
                "staerke":          urteil.staerke,
                "quelle_des_urteils": urteil.quelle,
            },
            user_id      = state.get("user_id", ""),
            character_id = state.get("character_id", ""),
        )

    # Die Kosten dieser Stufe gehoeren in die Anzeige. `token_total` scheidet
    # aus — das Feld gehoert dem Responder und wuerde ueberschrieben. Der
    # bestehende Anmerkungs-Kanal traegt es, ohne dass ein weiterer noetig ist.
    anmerkungen: list = state.get("node_annotations") or []
    anmerkungen.append(f"[Verfasser] {antwort.token_total} Tokens")
    state["node_annotations"] = anmerkungen

    # Das Urteil gehoert ins Protokoll, nicht nur in den State: Ohne diese
    # Zeile ist im Nachhinein nicht feststellbar, ob der Verfasser geurteilt
    # hat — und die Anlaufquote von B1 waere so wenig messbar wie die des
    # Thinkers vor B-1.
    logger.info(
        "Verfasser: Urteil %s (Einwand=%s, Bewertung=%s, Staerke=%s, Quelle=%s) — %s",
        "gefaellt" if urteil.geliefert else "AUSGEFALLEN",
        urteil.vorhanden, urteil.bewertung, urteil.staerke, urteil.quelle,
        (urteil.geprueft or "—")[:160],
    )

    logger.info(
        "Verfasser: Inhalt bestimmt (%s Zeichen, %s Tokens, "
        "Wissen: Gedaechtnis=%s Web=%s Aufzeichnungen=%s)",
        len(inhalt), antwort.token_total,
        bool(state.get("memory_context")), bool(state.get("web_context")),
        len(state.get("aufzeichnungen") or []),
    )
    return state
