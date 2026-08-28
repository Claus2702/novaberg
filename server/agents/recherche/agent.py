"""RechercheAgent — Iterative Web-Recherche zu Themen des Users.

Queue-basiert (aufgabe: recherche). Nutzt Session-Kontext + Web-Suche
fuer einen breiten Ueberblick. Ergebnis -> Shadow-Stack + Novas KZG.
"""

import logging
from dataclasses import dataclass

import psycopg2

from agents.base import AgentState, BaseAgent
from agents.kzg.speicher import embed_text_bauen as kzg_embed_text_bauen
from agents.recherche.bewertung import ergebnisse_bewerten
from agents.recherche.destillation import ergebnisse_destillieren, zwischen_destillieren
from agents.recherche.gate import ergebnis_einordnen
from agents.recherche.lagebeurteilung import kontext_paket_bauen, lagebeurteilung_erstellen
from agents.recherche.planung import recherche_planen
from agents.recherche.suche import suche_ausfuehren
from agents.wissen_rueckweg import AUFGABE_VERWEIS
from agents.wissen_rueckweg.herkunft import QUELLE_VERDICHTET
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    PIXIE_RECHERCHE_MAX_ITERATIONEN,
    POSTGRES_URL,
    ZIEL_MAX_MITTELFRISTIG,
    redis_client,
)
from memory.kontext import session_kontext_extrahieren
from memory.ziele import embed_text_bauen as ziel_embed_text_bauen
from memory.ziele import ziel_speichern, ziele_aktive_laden
from services.model_services import BackgroundRequest, EmbedRequest, model_service
from services.pixie.stack import stack_push
from services.shadow_agent.utils import shadow_queue_push
from services.wissensspeicher import Arbeitsergebnis, embed_text_bauen, ergebnis_ablegen
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.recherche")


def _ziel_aus_recherche_extrahieren(recherche_ziel: str, destillat: str) -> dict | None:
    """Extrahiert einen mittelfristigen Zielsatz aus dem Recherche-Ergebnis.

    Args:
        recherche_ziel: Das ursprüngliche Recherche-Ziel.
        destillat: Der destillierte Ergebnis-Text.

    Returns:
        Dict mit zielsatz, motivation, emotion, arousal — oder None.
    """
    prompt: str = (
        "[IDENTITAET]\n"
        "Du bist Novas Reflexions-Modul.\n\n"
        "[RECHERCHE_ZIEL]\n"
        f"{recherche_ziel}\n\n"
        "[ERGEBNIS]\n"
        f"{destillat[:800]}\n\n"
        "[AUFGABE]\n"
        "Hat diese Recherche ein neues Interesse oder eine offene Frage aufgeworfen,\n"
        "die Nova weiterverfolgen möchte?\n\n"
        "Gib zusätzlich ein kurzes Themen-Label (2-3 Wörter) das den Wissensbereich\n"
        "des Ziels benennt. Beispiele: 'Gartengestaltung', 'KI und Kognition',\n"
        "'Beziehung', 'Natur und Kultur', 'Klimaanpassung'.\n\n"
        "[FORMAT]\n"
        "Wenn ja: JSON mit einem Ziel:\n"
        '{"zielsatz": "Ich möchte ...", "motivation": 0.6, "emotion": "neugierig", "arousal": 0.5, "thema": "Natur und Kultur"}\n\n'
        "Wenn nein (das Thema ist abgeschlossen): antworte mit:\n"
        '{"zielsatz": ""}\n\n'
        "[REGELN]\n"
        "- Nur EIN Ziel, 1-2 Sätze\n"
        "- Motivation 0.4-0.8 (Recherche hat Interesse geweckt, nicht Leidenschaft)\n"
        "- Thema: 2-3 Wörter, knappes Label (kein Satz)\n"
        "- Nicht das Recherche-Ziel wiederholen — das war der Auslöser, nicht das Ergebnis\n"
        "- Sprache: Deutsch, Ich-Perspektive"
    )

    # ── LLM-Call via BackgroundWorker (Microservice-Welle Block 2 Phase 4, G4) ──
    # _ziel_aus_recherche_extrahieren() laeuft im RechercheAgent, sync invoked
    # aus services/pixie/dispatch.py via asyncio.to_thread → submit_sync.
    # expect_json=True → response.parsed.
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "analyse",
            temperature = 0.3,
            expect_json = True,
            caller      = "recherche/ziel",
        ))
        ziel: dict = response.parsed

        if not ziel.get("zielsatz"):
            logger.info("RechercheAgent: Kein Folgeziel aus Recherche")
            return None

        logger.info(f"RechercheAgent: Folgeziel extrahiert — '{ziel['zielsatz'][:60]}'")
        return ziel

    except Exception as fehler:
        logger.warning(f"RechercheAgent: Ziel-Extraktion fehlgeschlagen — {fehler}")
        return None


@dataclass
class Durchlauf:
    """Was ein Recherche-Durchlauf erarbeitet hat — reiner Datencontainer.

    Traegt genau das, was der Bibliotheks-Schritt braucht, und wird an einer
    Stelle gebaut. `destillat` darf leer sein: Dann ist der Durchlauf
    gescheitert, und der Schritt legt einen Bericht statt einer Wissen-Datei
    an (§5.1).
    """

    thema:         str
    ziel:          str
    destillat:     str
    queries:       list[str]
    lage:          dict
    queue_eintrag: dict
    user_id:       str


def _salienz_aus_auftrag(queue_eintrag: dict) -> float:
    """Liest die auslösende Salienz aus dem Queue-Auftrag.

    Der Wert hat die Recherche ausgelöst und ist beim Schreiben immer
    bekannt — er ist kein Vorgabewert und wird auch nicht zu einem (§11.4).

    Vorbedingung: keine. Nachbedingung: eine Zahl in (0.0, 1.0].
    Fehlerfälle: fehlender, nicht-numerischer oder nicht-positiver Wert
    (ValueError). Der Aufrufer soll daran scheitern: Eine Null in
    `salienz_anfang` sähe später aus wie ein Messergebnis, und in der
    Shadow-Queue tragen belegbar Aufträge eine Null, die das
    Hochsalienz-Tor passiert haben.

    `get(schluessel, default)` allein reicht hier nicht: Ein ausdrücklich
    auf null gesetztes Feld kommt durch den Default hindurch (11_EVA §2).
    """
    # ── Eingabe-Validierung ─────────────────────
    # **`salienz_absolut` zuerst, seit dem Umzug der Queue am 15.08.2026.**
    # Der Auftrag traegt drei Salienz-Staende; gebraucht wird der **Anker** —
    # was er beim ausloesenden Anlass wert war, nicht was er heute noch wert
    # ist. `salienz_decay` waere die Praesenz und schriebe das Alter des
    # Auftrags in die Bibliothek.
    #
    # Die beiden alten Namen bleiben als Rueckfall stehen, weil derselbe
    # Helfer auch Auftraege aus der Promotions-Queue erreichen kann — die
    # liegt weiterhin in Redis und traegt `salienz`.
    roh = None
    for schluessel in ("salienz_absolut", "salienz", "prioritaet"):
        if schluessel in queue_eintrag:
            roh = queue_eintrag[schluessel]
            break

    if roh is None:
        meldung: str = (
            f"_salienz_aus_auftrag: Auftrag ohne Salienz und ohne Prioritaet, "
            f"Felder vorhanden: {sorted(queue_eintrag)}"
        )
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    try:
        salienz: float = float(roh)
    except (TypeError, ValueError) as fehler:
        meldung = f"_salienz_aus_auftrag: Salienz {roh!r} ist keine Zahl"
        raise ValueError(meldung) from fehler

    # ── Ausgabe-Verifikation ────────────────────
    if not 0.0 < salienz <= 1.0:
        meldung = (
            f"_salienz_aus_auftrag: Salienz {salienz!r} liegt ausserhalb der Spanne "
            f"(0.0, 1.0] — der Auftrag traegt keinen brauchbaren Ausloesewert"
        )
        raise ValueError(meldung)

    return salienz


def _arousal_aus_auftrag(queue_eintrag: dict) -> float | None:
    """Liest die Erregung des ausloesenden Turns aus dem Auftrag.

    Args:
        queue_eintrag: der Auftrag aus der Shadow-Queue.

    Vorbedingung: keine.
    Nachbedingung: Eine Zahl in [0.0, 1.0] oder ``None``. **`None` heisst
        unbekannt** — ein Auftrag alter Bauart traegt die Spalte gar nicht,
        und die Salienz-Quelle liefert sie stellenweise selbst als leer.
    Fehlerfaelle: Ein unbrauchbarer Wert wird gemeldet und zu ``None``. Er
        bricht die Ablage **nicht** ab: Der Gedanke ist fertig recherchiert,
        und ihn wegen eines fehlenden Standes zu verwerfen waere teurer, als
        ihn ohne abzulegen — dieselbe Abwaegung wie bei der Salienz.

    Returns:
        Der Stand, oder ``None``.
    """
    # ── Eingabe-Validierung ─────────────────────
    roh: object = queue_eintrag.get("arousal")
    if roh is None:
        return None

    # `bool` ist in Python eine Ganzzahl und hier trotzdem kein Messwert.
    if isinstance(roh, bool) or not isinstance(roh, (int, float)):
        logger.warning(
            "RechercheAgent: Auftrag traegt arousal=%r (%s) statt einer Zahl "
            "— Eintrag geht ohne Stand auf den Stapel", roh, type(roh).__name__,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    # Spanne laut Nachbedingung: 0.0 bis 1.0 — dieselbe Skala, auf der die
    # Perzeption die Erregung fuehrt. Ausserhalb wird verworfen, nicht gekappt.
    wert: float = float(roh)
    if not (0.0 <= wert <= 1.0):
        logger.warning(
            "RechercheAgent: Auftrag traegt arousal=%r ausserhalb 0.0–1.0 "
            "— Eintrag geht ohne Stand auf den Stapel", wert,
        )
        return None

    return wert


def stapel_werte_aus_auftrag(queue_eintrag: dict) -> dict:
    """Die Werte, die vom Auftrag mit auf den Stapel wandern.

    Der Auftrag traegt Emotion, Modus, Intentionen und den ausloesenden Wert;
    bis zum 15.08.2026 blieben sie an der Schreibstelle liegen. Als eigene
    Funktion, weil die Uebergabe sonst nur im Rumpf von `invoke` steht und
    dort von keinem Zeugen erreichbar ist — eine ausgeklinkte Uebergabe liess
    am 15.08.2026 alle 1370 Tests gruen.

    Args:
        queue_eintrag: der Auftrag aus der Shadow-Queue.

    Returns:
        Die Schluesselwoerter fuer `stack_push`. `salienz` ist ``None``, wenn
        der Auftrag keinen brauchbaren Ausloesewert traegt — **das bricht die
        Ablage nicht ab**: Der Gedanke ist fertig recherchiert, und ihn wegen
        eines fehlenden Rangwerts zu verwerfen waere teurer, als ihn ohne Rang
        abzulegen. Er reiht sich dann hinten ein.
    """
    # ── Eingabe-Validierung / Verarbeitung ──────
    try:
        salienz: float | None = _salienz_aus_auftrag(queue_eintrag)
    except ValueError as fehler:
        logger.warning(
            "RechercheAgent: Auftrag ohne brauchbare Salienz — Eintrag geht "
            "ohne Rangwert auf den Stapel (%s)", fehler,
        )
        salienz = None

    # ── Ausgabe ─────────────────────────────────
    return {
        "intentionen": queue_eintrag.get("intentionen") or [],
        "emotion":     queue_eintrag.get("emotion", ""),
        "modus":       queue_eintrag.get("modus", ""),
        "salienz":     salienz,
        # Der Stand, in dem der Auftrag entstand — seit dem 15.08.2026 eine
        # Spalte der Queue. **Kein Ersatzwert:** Ein Auftrag alter Bauart
        # traegt hier `None`, und das heisst unbekannt. Eine 0.5 saehe wie
        # eine Messung aus und hoebe beim Einwurf Novas Zustand auf eine
        # erfundene Zahl (Bauteil B, `novaberg-eigenzeit_k.md` §2.3).
        "arousal":     _arousal_aus_auftrag(queue_eintrag),
    }


class RechercheAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "recherche"

    @property
    def typ(self) -> str:
        return "workflow"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["web_recherche", "themen_analyse"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    def build_graph(self):
        """Kein LangGraph-Subgraph — der Ablauf ist eine lineare
        Python-Schleife mit Iteration. Subgraph waere Overhead.
        """
        return None

    @staticmethod
    def _audit_log(user_id: str, status: str, ergebnis: str) -> None:
        """Schreibt einen hintergrund_log-Eintrag fuer den Bibliotheks-Schritt.

        Eigener Eintrag je Schritt, keine Sammelmeldung: Erst dann ist im
        Nachhinein unterscheidbar, ob die Ablage lief und nichts fand oder
        ob sie gar nicht lief.

        Failsafe: Bei DB-Fehler nur logger.critical, kein Retry — ein Retry
        auf einer kaputten Audit-Senke liefe endlos.

        **Enger gefasst als das Muster in synapsen_decay**, das hier blind
        faengt: Aufgefangen werden Datenbank- und Netzfehler, also das, was
        ein INSERT tatsaechlich wirft. Die Rekursionsgefahr, die dort den
        breiten Fang begruendet, besteht ohne Retry nicht — und ein Defekt
        ausserhalb dieser Menge soll sichtbar werden, statt als verlorener
        Audit-Eintrag zu erscheinen.
        """
        try:
            db_manager.execute(
                """
                INSERT INTO hintergrund_log
                    (user_id, aufgabe, status, ergebnis, verarbeitet_am)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, "recherche_bibliothek", status, ergebnis),
            )
        except (psycopg2.Error, OSError) as ex:
            logger.critical(
                f"hintergrund_log-INSERT fehlgeschlagen: {ex} "
                f"(verlorener Audit-Eintrag: recherche_bibliothek/{status}/{ergebnis[:100]})"
            )

    def _bibliothek_schritt(self, durchlauf: Durchlauf, *, status: str = "") -> None:
        """Ordnet das Ergebnis ein und legt es in der Bibliothek ab.

        Eigener Schritt mit eigenem Audit-Eintrag: Ein Lauf, der mehreres
        tut, faerbt bei einem Fehlschlag im dritten Teil sonst den ganzen
        Auftrag rot, und hinterher ist nicht unterscheidbar, ob die Ablage
        lief und nichts fand oder gar nicht lief.

        `status` uebergeht das Gate. Genutzt wird das fuer den Fall, in dem
        es nichts einzuordnen gibt — eine gescheiterte Destillation ist ein
        `fehlschlag`, und ein Modellaufruf darueber waere eine Frage an ein
        leeres Blatt.

        Vorbedingung: keine — jeder Fehlerfall wird hier behandelt und nicht
        an den Aufrufer weitergereicht.
        Nachbedingung: Bericht-Datei geschrieben, Wissen-Datei bei
        `echte_tiefe`/`ergaenzung`, genau eine Metadatenzeile; in jedem Fall
        ein Audit-Eintrag mit `erledigt` oder `fehler`.
        Fehlerfaelle: Ein Fehlschlag der Ablage wird laut protokolliert und
        beendet den Schritt, **nicht die Recherche**. Ihr Ergebnis geht noch
        auf den Stack und in Novas Gedaechtnis. Was fehlt, ist die Datei —
        und genau das steht dann im Audit, statt still zu verschwinden.
        """
        self._audit_log(durchlauf.user_id, "gestartet", f"Bibliothek: '{durchlauf.thema}'")

        try:
            urteil: dict[str, str] = (
                {"status": status, "begruendung": "Die Destillation lieferte keinen Text."}
                if status else
                ergebnis_einordnen(
                    ziel=durchlauf.ziel, destillat=durchlauf.destillat, lage=durchlauf.lage,
                )
            )
            ergebnis: Arbeitsergebnis = Arbeitsergebnis(
                thema=durchlauf.thema,
                # Ohne Destillat traegt der Bericht das Ziel als Gegenstand.
                # Eine leere Zusammenfassung waere in der Metadatenzeile ein
                # Pflichtfeld ohne Inhalt und scheiterte am Repository.
                destillat=durchlauf.destillat or f"Ohne Ergebnis zum Ziel: {durchlauf.ziel}",
                status=urteil["status"],
                modus="recherche",
                # Paar-Schema (§11.2): Subjekt ist der Mensch, fuer den
                # recherchiert wurde; Gegenueber ist Nova; die Perspektive
                # des Inhalts ist ihre — sie hat ihn erarbeitet.
                user_id=durchlauf.user_id,
                character_id=ASSISTANT_USER_ID,
                beobachter="assistant",
                salienz=_salienz_aus_auftrag(durchlauf.queue_eintrag),
                ziel=durchlauf.ziel,
                begruendung=urteil["begruendung"],
                queries=durchlauf.queries,
            )
            ergebnis.themen_embedding = self._embedding_bauen(ergebnis.destillat)
            pfade: dict[str, str] = ergebnis_ablegen(ergebnis)
        except (ValueError, RuntimeError, OSError, psycopg2.Error) as fehler:
            logger.exception(
                f"RechercheAgent: Ablage in der Bibliothek fehlgeschlagen "
                f"({type(fehler).__name__}) — Thema '{durchlauf.thema}'. "
                f"Die Recherche selbst bleibt davon unberuehrt"
            )
            self._audit_log(durchlauf.user_id, "fehler", f"{type(fehler).__name__}: {fehler}")
            return

        # ── Der Rueckweg, Weg 3: das Zugehoerige (§4b.1a) ──────
        # **Das Ergebnis behaelt seine eigene Datei.** Sie ist die Ausarbeitung
        # ihres Wissens und steht fuer weitere Vertiefungen bereit; was der
        # Auftrag ausloest, ist deshalb kein zweiter Schnitt, sondern die
        # Verstaerkung der verwandten Zeile. Wer den Inhalt zusaetzlich
        # einarbeitete, legte ihn zweimal ab.
        self._verweis_einreihen(ergebnis, pfade["wissen_pfad"], pfade["zeilen_id"])

        self._audit_log(
            durchlauf.user_id, "erledigt",
            f"Status {ergebnis.status}, Zeile {pfade['zeilen_id']}, "
            f"Bericht {pfade['bericht_pfad']}"
            + (f", Wissen {pfade['wissen_pfad']}" if pfade["wissen_pfad"] else ""),
        )

    def _verweis_einreihen(
        self, ergebnis: Arbeitsergebnis, wissen_pfad: str, zeilen_id: str,
    ) -> None:
        """Reiht den Verweis auf eine verwandte Wissensdatei ein (§4b.1a, Weg 3).

        Vorbedingung: `ergebnis` ist abgelegt, `wissen_pfad` nennt die
        geschriebene Wissensdatei und `zeilen_id` ihre Bibliothekszeile.
        **Ein leerer Pfad ist der Regelfall bei einer gescheiterten
        Recherche** und beendet den Schritt.

        **Die eigene Zeilennummer reist mit, und ohne sie waere der Weg ein
        Selbstlaeufer.** Die gerade angelegte Zeile traegt dieselbe
        Zusammenfassung wie das Material des Verweises; sie waere der
        naechste Kandidat jeder Zuordnung, mit Kosinus nahe eins. Der
        Verweis verstaerkte dann bei **jedem** Recherche-Ergebnis seine
        eigene Zeile, und `haeufigkeit` und `gewicht_roh` sind die Groessen,
        nach denen die Bibliothek spaeter auswaehlt.
        Nachbedingung: Ein Auftrag `wissen_verweis` liegt in der Queue, oder
        der Grund seines Ausbleibens steht im Protokoll.
        Fehlerfaelle: **Ein Fehlschlag beim Einreihen reisst die Recherche
        nicht.** Sie ist zu diesem Zeitpunkt gueltig abgeschlossen und
        abgelegt; ein ausgefallener Verweis kostet eine Verstaerkung, ein
        abgebrochener Lauf kostet das Ergebnis.

        **Das Material ist die verdichtete Fassung, und das ist hier die
        richtige.** Der Text dient allein der Zuordnung, und die vergleicht
        Zusammenfassung gegen Zusammenfassung — die Kandidaten stehen mit
        ihrer eigenen in der Bibliothek. Die Entscheidung *rohe Fassung* aus
        §9 Punkt 9 gilt dem Text, der **eingearbeitet** wird; auf diesem Weg
        wird keiner eingearbeitet.
        """
        # ── Eingabe-Validierung ─────────────────
        # **Ohne Wissen gibt es nichts zuzuordnen.** Eine gescheiterte
        # Recherche schreibt nur einen Bericht, und ihr Destillat ist der
        # Platzhalter "Ohne Ergebnis zum Ziel: …". Ein Verweis darauf kostet
        # zwei Modellaufrufe und kann bestenfalls "keine Datei passt" sagen —
        # schlimmstenfalls verstaerkt er eine Zeile auf einen Platzhalter hin.
        # `[gemessen]` — 19.08.2026: Ohne diese Bedingung standen binnen
        # Minuten zwei Auftraege der Form "Gescheitert <hash>" in der Queue.
        if not wissen_pfad.strip():
            logger.info(
                "RechercheAgent: kein Verweis zu '%s' — ohne Wissen-Datei gibt "
                "es nichts zuzuordnen (Status %s)", ergebnis.thema, ergebnis.status,
            )
            return

        kern: str = (ergebnis.destillat or "").strip()
        if not kern:
            logger.error(
                "RechercheAgent: Verweis nicht eingereiht — '%s' traegt kein "
                "Destillat", ergebnis.thema,
            )
            return

        # ── Verarbeitung ────────────────────────
        try:
            shadow_queue_push(
                redis_client, ergebnis.user_id, AUFGABE_VERWEIS,
                thema=ergebnis.thema, prioritaet=ergebnis.salienz,
                kontext=kern, modus=f"rueckweg_{QUELLE_VERDICHTET}",
                bezug_id=int(zeilen_id) if zeilen_id.isdigit() else None,
            )
        except Exception as fehler:  # noqa: BLE001 — die Ablage steht bereits
            logger.exception(
                "%s: RechercheAgent: Verweis zu '%s' nicht eingereiht — die "
                "Ablage bleibt gueltig, die Verstaerkung faellt aus",
                type(fehler).__name__, ergebnis.thema,
            )
            return

        # ── Ausgabe-Verifikation ────────────────
        logger.info(
            "RechercheAgent: Verweis eingereiht — Thema '%s', prioritaet=%.3f, "
            "%d Zeichen Material, eigene Zeile %s ausgeschlossen",
            ergebnis.thema, ergebnis.salienz, len(kern), zeilen_id or "<keine>",
        )

    @staticmethod
    def _embedding_bauen(destillat: str) -> str | None:
        """Baut den Vektor der Zusammenfassung als pgvector-Literal.

        Nachbedingung: eine Zeichenkette der Form "[v1,v2,...]" oder None.
        None ist zulaessig — die Spalte ist nullbar, und eine Zeile ohne
        Vektor bleibt ueber Thema und Paar auffindbar. Ein Ausfall des
        Embedders darf die Ablage nicht verhindern; er wird protokolliert.

        Aufgefangen werden die Ausnahmen, die die Worker-Schicht ausdruecklich
        wirft (ValueError, RuntimeError) plus Netzfehler. Eine Ausnahme
        ausserhalb dieser Menge wird NICHT hier behandelt — sie waere ein
        unbekannter Zustand, und den still in ein `None` zu verwandeln waere
        genau der Fallback, der einen Defekt maskiert.
        """
        try:
            antwort = model_service.embed.submit_sync(
                EmbedRequest(text=embed_text_bauen(destillat.strip()[:500]))
            )
        except (ValueError, RuntimeError, OSError, TimeoutError):
            logger.exception(
                "RechercheAgent: Embedding der Zusammenfassung fehlgeschlagen — die "
                "Zeile entsteht ohne Vektor und ist ueber die Aehnlichkeitssuche "
                "nicht auffindbar"
            )
            return None

        return "[" + ",".join(str(w) for w in antwort.embedding) + "]"

    def invoke(self, state: AgentState) -> AgentState:
        """Orchestriert den Recherche-Ablauf.

        1. Session-Kontext destillieren
        2. Suchqueries planen (LLM)
        3. Web-Suche + Page-Fetch
        4. Ergebnisse bewerten (LLM) -> fertig oder Luecken
        5. Bei Luecken: neue Queries -> Schritt 3 (max N Iterationen)
        6. Destillation (LLM)
        7. Ergebnis -> Shadow-Stack + Novas KZG
        """
        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID
        queue_eintrag: dict = state.get("parameter", {})
        thema: str = queue_eintrag.get("thema", "")

        logger.info(f"RechercheAgent: Start — Thema aus Queue: '{thema}'")

        # -- 1. Session-Kontext destillieren --
        session_kontext: dict = session_kontext_extrahieren(user_id)

        if not session_kontext and not thema:
            logger.warning("RechercheAgent: Kein Kontext und kein Thema — Abbruch")
            state["status"] = "fehler"
            state["fehler"] = "Kein Kontext verfuegbar"
            return state

        logger.info(f"RechercheAgent: Session-Kontext — {session_kontext.get('thema_kern', '?')}")

        # -- 2a. Kontext-Paket bauen (deterministisch, kein LLM) --
        character_id: str = ASSISTANT_USER_ID if user_id == DEFAULT_USER_ID else DEFAULT_USER_ID
        kontext_paket: dict = kontext_paket_bauen(
            thema=thema or session_kontext.get("thema_kern", ""),
            queue_eintrag=queue_eintrag,
            user_id=user_id,
            character_id=character_id,
        )

        # -- 2b. Lagebeurteilung (Qwen3-32B, Analyse-Modell) --
        lage: dict = lagebeurteilung_erstellen(kontext_paket, suchmodus="recherche")
        logger.info(
            f"RechercheAgent: Lagebeurteilung — "
            f"{len(lage.get('wissensluecken', []))} Luecken, "
            f"{len(lage.get('ausschluss', []))} Ausschluesse"
        )

        # -- 3. Planung (Qwen3-32B, mit Lagebeurteilung) --
        plan: dict = recherche_planen(thema, session_kontext, lage)

        if not plan:
            state["status"] = "fehler"
            state["fehler"] = "Planung fehlgeschlagen"
            return state

        recherche_ziel: str = plan.get("ziel", "")
        queries: list[str] = plan.get("queries", [])
        kriterien: list[str] = plan.get("kriterien", [])

        logger.info(f"RechercheAgent: Ziel — {recherche_ziel}")
        logger.info(f"RechercheAgent: {len(queries)} Queries geplant")

        # -- 3-4. Such-Iterations-Schleife mit Zwischen-Destillation --
        bisherige_zusammenfassung: str = ""
        max_iterationen: int = PIXIE_RECHERCHE_MAX_ITERATIONEN

        for iteration in range(max_iterationen):
            logger.info(f"RechercheAgent: Iteration {iteration + 1} von {max_iterationen}")

            # 3. Suche + Fetch
            neue_ergebnisse: list[str] = suche_ausfuehren(queries)

            if not neue_ergebnisse and not bisherige_zusammenfassung:
                logger.warning("RechercheAgent: Keine Ergebnisse gefunden — Abbruch")
                break

            if not neue_ergebnisse:
                logger.info("RechercheAgent: Keine neuen Ergebnisse — destilliere bisherige")
                break

            # Zwischen-Destillation: bisherige Zusammenfassung + neue Rohtexte komprimieren
            if bisherige_zusammenfassung:
                destillations_input = (
                    bisherige_zusammenfassung + "\n\n" + "\n\n".join(neue_ergebnisse)
                )
            else:
                destillations_input = "\n\n".join(neue_ergebnisse)

            arbeitskontext: str = session_kontext.get("zusammenfassung", "")

            bisherige_zusammenfassung = zwischen_destillieren(
                ziel=recherche_ziel,
                ergebnisse_text=destillations_input,
                arbeitskontext=arbeitskontext,
            )

            if not bisherige_zusammenfassung:
                logger.warning("RechercheAgent: Zwischen-Destillation fehlgeschlagen")
                break

            logger.info(
                f"RechercheAgent: Zwischen-Destillation — "
                f"{len(bisherige_zusammenfassung)} Zeichen"
            )

            # 4. Bewertung (Qwen3-32B, mit Vorwissen-Abgleich)
            bewertung: dict = ergebnisse_bewerten(
                recherche_ziel, kriterien, bisherige_zusammenfassung, lage
            )

            # Fertig oder weiter?
            if bewertung.get("status") == "fertig":
                logger.info("RechercheAgent: Bewertung — fertig")
                break

            neue_queries: list[str] = bewertung.get("queries", [])
            if not neue_queries:
                logger.info("RechercheAgent: Keine neuen Queries — fertig")
                break

            queries = neue_queries
            logger.info(f"RechercheAgent: Luecken — {len(neue_queries)} neue Queries")

        # -- 5. Finale Destillation --
        # bisherige_zusammenfassung ist kompakt (Fakten, ~800 Zeichen).
        # Finale Destillation macht daraus nutzerfreundlichen Fliesstext.
        destillat: str = ergebnisse_destillieren(
            recherche_ziel, [bisherige_zusammenfassung], session_kontext,
            kontext_paket=kontext_paket, lage=lage,
        ) if bisherige_zusammenfassung else ""

        durchlauf: Durchlauf = Durchlauf(
            thema=thema or session_kontext.get("thema_kern", ""),
            ziel=recherche_ziel,
            destillat=destillat,
            queries=queries,
            lage=lage,
            queue_eintrag=queue_eintrag,
            user_id=user_id,
        )

        # -- 6a. Gescheiterte Destillation ist ein Fehlschlag MIT Bericht --
        # Die Suche lief, sie hat nur nichts Brauchbares ergeben — genau der
        # Fall, den das Konzept `fehlschlag` nennt (§5.1). Ohne diesen Zweig
        # verbraucht ein Durchlauf zehn Minuten am einzigen seriellen Platz
        # und hinterlaesst keine Spur; die naechste Lagebeurteilung faengt
        # bei null an und sucht dasselbe noch einmal.
        if not destillat:
            self._bibliothek_schritt(durchlauf, status="fehlschlag")
            state["status"] = "fehler"
            state["fehler"] = "Destillation fehlgeschlagen"
            return state

        logger.info(f"RechercheAgent: Destillat — {destillat[:100]}...")

        # -- 6b. Keep/Discard-Gate und Ablage in der Bibliothek --
        self._bibliothek_schritt(durchlauf)

        # -- 7. Ergebnis auf Shadow-Stack --
        try:
            stack_push(
                redis_client=redis_client,
                user_id=user_id,
                aufgabe="recherche",
                thema=thema or session_kontext.get("thema_kern", ""),
                inhalt=destillat,
                # Der Turn, aus dem der Auftrag entstand, wandert mit auf
                # den Stapel — das zweite Ende der Sachlage-Bruecke.
                ausloeser_turn_id=queue_eintrag.get("ausloeser_turn_id"),
                **stapel_werte_aus_auftrag(queue_eintrag),
            )
        except Exception as e:
            logger.warning(f"RechercheAgent: Stack-Push fehlgeschlagen — {e}")

        # -- 8. In Novas KZG speichern (Post-Hook nova_gedaechtnis) --
        try:
            from memory.kzg import kzg_store

            themen_list: list = session_kontext.get("themen", [])

            # zusammenfassung = destillat: kzg_store persistiert daraus das
            # inhalt-Feld. Ohne diesen Schluessel entstanden Vektoren ohne
            # Quelltext (RECHERCHE-WISSEN-ERREICHT-LZG-NIE, Chat 107) — die
            # Synapsen-Promotion verwarf jeden dieser Eintraege in
            # Vorbedingung 3, Recherche-Wissen erreichte das LZG nie.
            salienz_obj: dict = {
                "salienz": 0.7,
                "themen": themen_list,
                "zusammenfassung": destillat,
                "intentionen": ["information_teilen"],
                "emotion": "neutral",
                "modus": session_kontext.get("modus", ""),
                "gedaechtnistyp": "kurz",
                "dimension": "kontext",
            }

            # Embed-Text ueber die eine KZG-Formel — kommagetrennte Themen
            # wie im Hash persistiert, kern = destillat. Damit ist der
            # Vektor aus den gespeicherten Feldern rekonstruierbar.
            themen_str: str = ", ".join(themen_list)
            embed_response = model_service.embed.submit_sync(
                EmbedRequest(text=kzg_embed_text_bauen(themen_str, destillat))
            )
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Recherche: Destillat Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )

            # Recherche-Erkenntnisse ins Paar (user_id, nova) — Beobachter "assistant".
            kzg_store(
                redis_client=redis_client,
                user_id=user_id,
                character_id=ASSISTANT_USER_ID,
                beobachter="assistant",
                salienz_obj=salienz_obj,
                embedding=embedding,
            )
            logger.info("RechercheAgent: In Novas KZG gespeichert")
        except Exception as e:
            logger.warning(f"RechercheAgent: KZG-Write fehlgeschlagen — {e}")

        # -- 9. Mittelfristiges Ziel extrahieren (Drive) --
        try:
            # Max-Check: nicht über ZIEL_MAX_MITTELFRISTIG
            # Novas Ziele stehen je Beziehung. `user_id` ist hier der Mensch,
            # in dessen Gespraech die Recherche lief — also das Gegenueber.
            aktive_ziele: list[dict] = ziele_aktive_laden(
                POSTGRES_URL, ASSISTANT_USER_ID, user_id,
            )
            mittelfristige: int = sum(1 for z in aktive_ziele if z["ziel_typ"] == "mittelfristig")

            if mittelfristige < ZIEL_MAX_MITTELFRISTIG:
                ziel_extrakt: dict | None = _ziel_aus_recherche_extrahieren(
                    recherche_ziel, destillat,
                )

                if ziel_extrakt:
                    try:
                        ziel_response = model_service.embed.submit_sync(
                            EmbedRequest(text=ziel_embed_text_bauen(ziel_extrakt["zielsatz"]))
                        )
                        ziel_emb: list[float] | None = ziel_response.embedding
                        logger.debug(
                            "Recherche: Ziel-Extrakt Embedding via EmbedWorker (Dim: %d, Dauer: "
                            "%.3fs)",
                            len(ziel_emb),
                            ziel_response.duration_seconds,
                        )
                    except Exception:
                        ziel_emb = None

                    ziel_speichern(
                        postgres_url=POSTGRES_URL,
                        user_id=ASSISTANT_USER_ID,
                        character_id=user_id,
                        ziel_typ="mittelfristig",
                        zielsatz=ziel_extrakt["zielsatz"],
                        motivation=ziel_extrakt.get("motivation", 0.6),
                        emotion=ziel_extrakt.get("emotion", "neugierig"),
                        arousal=ziel_extrakt.get("arousal", 0.5),
                        thema=(ziel_extrakt.get("thema") or "").strip()[:100],
                        embedding=ziel_emb,
                    )
            else:
                logger.info(
                    f"RechercheAgent: Max mittelfristige Ziele erreicht "
                    f"({mittelfristige}/{ZIEL_MAX_MITTELFRISTIG}) — kein neues Ziel"
                )

        except Exception as ziel_fehler:
            logger.warning(f"RechercheAgent: Ziel-Speicherung fehlgeschlagen — {ziel_fehler}")

        state["status"] = "abgeschlossen"
        state["ergebnis"] = destillat
        return state
