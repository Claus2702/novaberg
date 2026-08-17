"""BaseAgent, AgentState, AgentResult — Fundament des Agent-Systems."""

import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

from config import ASSISTANT_USER_ID

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State eines einzelnen Agenten. Der Agent sieht nie den ConversationState."""

    aufgabe: str                  # Was soll getan werden (Freitext)
    aufgabe_typ: str              # "workflow" | "kognitiv"
    agent_name: str               # Name des ausführenden Agenten
    kontext: dict                 # user_id, session_id, memory_context, ...
    parameter: dict               # Agent-spezifische Parameter
    schritte: list[dict]          # Bisherige Schritte + Ergebnisse (Audit-Trail)
    ergebnis: Any                 # Finales Ergebnis
    status: str                   # "laufend" | "abgeschlossen" | "fehler" | "rueckfrage"
    rueckfrage: str | None        # Rückfrage-Text bei status="rueckfrage"
    fehler: str | None            # Fehler-Beschreibung bei status="fehler"


@dataclass
class PeriodicTask:
    """Beschreibung einer periodischen Pixie-Aufgabe."""

    name: str
    priority: float     # 0.0 – 1.0
    interval: int       # Abklingzeit in Sekunden
    description: str


#: Geschlossene Menge der Ergebnis-Zustaende. Kanon nach EVA — eine
#: Teilmengen-Pruefung koennte einen unbekannten Status nicht von einem
#: gueltigen Nein unterscheiden.
#:
#: **`rejected` ist Bestand und die Vorform des vierten Ausgangs.** Vier
#: Dispatches setzen ihn, wenn die Klassifikation den Prompt als
#: Nicht-Auftrag erkennt — der Dienst sagt damit "ich bin nicht
#: zustaendig". Das ist ein Urteil und keine Stoerung, also inhaltlich
#: schon die vierte Sorte; es fehlt ihm nur alles, was ihn brauchbar
#: macht: Befund, Beleg und Vorschlag.
#:
#: `abgelehnt` ist dieselbe Aussage mit diesen drei Teilen. Der Weg
#: fuehrt von `rejected` dorthin, nicht daneben — deshalb stehen beide im
#: Kanon, und `NMCP_SACKGASSE` benennt die abzuloesende Form.
#: **`dismissed` ist der Rueckweg der Rueckfrage, kein Ausgang.** Nicht
#: der Dienst lehnt ab, sondern der Auftraggeber am Tor. Damit ist er die
#: Aufloesung von `rueckfrage` und gehoert zur Pipeline, nicht zu den
#: Ausgaengen — er steht hier, weil er das Ergebnisobjekt erreicht.
#:
#: Am 17.08.2026 gezaehlt: **Einer von vier Torwaechtern** hat diesen
#: Rueckweg (`charakter_identitaet`). Die uebrigen drei stellen eine
#: Rueckfrage, ohne ein unterscheidbares Nein zu kennen — genau die Lage,
#: vor der die Konvention warnt: Eine differenzierte Rueckfrage ohne
#: eigenen Rueckweg taeuscht eine Genauigkeit vor, die sie nicht einloest.
STATUS_KANON: frozenset[str] = frozenset(
    {
        "abgeschlossen",
        "fehler",
        "rueckfrage",
        "abgelehnt",
        "rejected",     # Vorform des vierten Ausgangs — ohne Begruendung
        "dismissed",    # Rueckweg der Rueckfrage — der Mensch sagt nein
    }
)

#: Der Status, dessen Ablösung aussteht: eine Ablehnung ohne Begruendung.
#: Formal zulaessig, praktisch eine Sackgasse — der Auftraggeber weiss,
#: dass es nicht ging, und nicht, was ginge.
NMCP_SACKGASSE: str = "rejected"

#: Geschlossene Menge der zulaessigen Quoten-Stufen (Prozent).
QUOTEN_KANON: frozenset[int] = frozenset({0, 25, 50, 75, 100})

#: Geschlossene Menge der Graphen, fuer die eine Quote gelten kann.
GRAPH_KANON: frozenset[str] = frozenset({"user", "pixie"})

#: Wie ein Dienst seine Auftraege bekommt. Nur "empfang" durchlaeuft eine
#: Zustellentscheidung und braucht deshalb Aushang und Quote.
ZUSTELLART_KANON: frozenset[str] = frozenset({"empfang", "zeitplan", "queue"})


@dataclass(frozen=True)
class Bedarf:
    """Ein Zustandswert, den ein Dienst bei der Anmeldung verlangt.

    Der Bedarf wird bei der Registrierung gegen den Katalog der Zusagen
    gehalten. Ohne Zusage wird der Dienst nicht eingebunden — laut, beim
    Start, und nicht still im dritten Durchlauf.

    `bedeutung` ist der Teil, der leicht wegfaellt und am meisten kostet:
    Ein Schluessel kann den angelegten oder den gefundenen Eintrag
    tragen, und der Unterschied entscheidet ueber die Richtigkeit des
    Ergebnisses.
    """

    schluessel: str    # Name des Zustands-Schluessels
    typ: str           # Erwarteter Typ, als Text ("int | None", "str", "dict")
    bedeutung: str     # Was der Wert bedeutet — nicht was er heisst


@dataclass(frozen=True)
class Zusage:
    """Die verbindliche Antwort des Empfangs auf einen Bedarf.

    Vier Teile. Wer einen davon wegfallen laesst, hat geraten statt
    zugesagt: Ein Schluessel mit dem erwarteten Namen und einem anderen
    Typ ist schlimmer als ein fehlender.
    """

    schluessel: str
    typ: str
    bedeutung: str
    lebensdauer: str   # z.B. "ein Durchlauf" — beim fremden Dienst nicht implizit
    verbraucher_art: str = "agent"   # "agent" | "knoten"
    """Wer diesen Kanal liest.

    Die Clipboard-Regel gilt zwischen **Stufen**, nicht nur zwischen
    Agenten — der Bestand enthaelt Kanaele, die Knoten zu Knoten laufen.
    Fuer die gilt kein Agenten-Bedarf, und eine Pruefung, die ihn
    verlangt, meldet einen Fehlalarm.

    Am 17.08.2026 gemessen: Von drei Zusagen sind zwei knotenseitig
    (`session_turn_kern` → Dispatcher-Knoten, `lzg_resonanz` → Reducer und
    Gespraechsvektor) und nur eine agentenseitig (`timeline_id` → KZG).
    Ohne dieses Feld meldete das Gesamtbild alle drei als toten Kanal.
    """


@dataclass
class Korrektur:
    """Gegenangebot einer Fachabteilung bei status='abgelehnt'.

    Drei Teile, und keiner ist entbehrlich: Ohne Befund weiss der
    Auftraggeber nicht, was nicht stimmt; ohne Beleg nicht, woran der
    Dienst es erkannt hat; ohne Vorschlag hat er eine Sackgasse statt
    eines Gegenangebots.

    Der Vorschlag geht an den Auftraggeber und **nicht** in den Bestand.
    Ein Dienst, der seine eigene Korrektur ausfuehrt, hat den Auftrag
    ersetzt statt ihn beurteilt.
    """

    befund: str      # Was am Auftrag nicht stimmt, in der Sprache des Auftraggebers
    beleg: str       # Welcher Bestandsteil widerspricht
    vorschlag: str   # Was der Dienst stattdessen taete, als ausfuehrbarer Auftrag


@dataclass
class AgentResult:
    """Typisiertes Ergebnis-Objekt, das der Dispatch in den ConversationState schreibt.

    Vier Ausgaenge, und die Trennung von `fehler` und `abgelehnt` ist der
    Kern: Ein Fehler ist eine Stoerung und geht den Betreiber an, eine
    Ablehnung ist ein Urteil und geht den Auftraggeber an. Wer beide in
    denselben Ausgang legt, macht die wertvollste Leistung der
    Fachabteilung als Stoerung sichtbar.
    """

    agent_name: str
    ergebnis: Any                          # Agent-spezifisches Ergebnis
    status: str                            # STATUS_KANON
    fehler: str | None = None
    rueckfrage: str | None = None
    korrektur: Korrektur | None = None     # Pflicht bei status="abgelehnt"
    schritte: list[dict] = field(default_factory=list)   # Audit-Trail
    meta: dict = field(default_factory=dict)              # Dauer, Token, Telemetrie

    def __post_init__(self) -> None:
        """Verifiziert den Ausgang gegen den Kanon und seine Pflichtfelder.

        Nachbedingung: `status` liegt in STATUS_KANON; bei "abgelehnt" ist
        `korrektur` gesetzt, bei "fehler" ist `fehler` gesetzt, bei
        "rueckfrage" ist `rueckfrage` gesetzt.

        Ein Verstoss wird laut gemeldet und nicht zurechtgebogen: Ein
        stillschweigend auf "fehler" gedrehter Status machte aus einem
        Urteil eine Stoerung — genau die Verwechslung, gegen die die vier
        Ausgaenge gebaut sind.
        """
        # ── Ausgabe-Verifikation ────────────────────────────────
        if self.status not in STATUS_KANON:
            logger.error(
                "AgentResult von '%s': Status '%s' nicht im Kanon %s — "
                "Ergebnis unbrauchbar",
                self.agent_name, self.status, sorted(STATUS_KANON),
            )
            raise ValueError(f"Unbekannter AgentResult-Status: {self.status!r}")

        pflicht = {
            "abgelehnt": ("korrektur", self.korrektur),
            "fehler": ("fehler", self.fehler),
            "rueckfrage": ("rueckfrage", self.rueckfrage),
        }.get(self.status)

        if pflicht is not None and pflicht[1] is None:
            feld = pflicht[0]
            logger.error(
                "AgentResult von '%s': Status '%s' ohne Pflichtfeld '%s' — "
                "der Ausgang ist ohne dieses Feld nicht auswertbar",
                self.agent_name, self.status, feld,
            )
            raise ValueError(
                f"Status {self.status!r} ohne {feld!r} (Agent {self.agent_name!r})"
            )


class BaseAgent(ABC):
    """Abstrakte Basisklasse für alle Agenten."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        ...

    @property
    def beschreibung(self) -> str:
        """Lädt AGENT.md aus dem eigenen Verzeichnis."""
        pfad = Path(inspect.getfile(self.__class__)).parent / "AGENT.md"
        if pfad.exists():
            return pfad.read_text(encoding="utf-8")
        return ""

    @property
    def typ(self) -> str:
        """'workflow' (Typ 1) oder 'kognitiv' (Typ 2)."""
        return "workflow"

    @property
    def faehigkeiten(self) -> list[str]:
        """Liste der Fähigkeiten für den Planner-Prompt."""
        return []

    @property
    def graph_eignung(self) -> list[str]:
        """In welchen Graphen darf dieser Agent laufen: ['user'], ['pixie'], oder beide."""
        return ["user", "pixie"]

    @property
    def lastart(self) -> str:
        """Welche Pixie-Spur diesen Agenten faehrt: 'llm' oder 'cpu'.

        Der Hintergrund laeuft in zwei Spuren, weil zwei Lasten sich nicht
        behindern: Wer das Sprachmodell braucht, haelt es minutenlang; wer
        nur rechnet und einbettet, ist in Sekunden fertig. In einer
        gemeinsamen Schlange verhungert der Schnelle hinter dem Langsamen —
        gemessen am 09.08.2026: Die Synapsen-Promotion kam waehrend eines
        28-Minuten-Bogens **einmal** dran und brachte 1 von 72 Auftraegen
        durch, weil jeder Gespraechsauftrag mit 0,94 bis 1,00 ueber ihrer
        Basis von 0,90 stand.

        **Die Vorgabe ist `llm`, und das ist eine Entscheidung.** Ein neu
        hinzugekommener Agent, den niemand eingeordnet hat, landet damit in
        der langsamen Spur — dort ist Blockieren erwartet und schadet nichts.
        Die Vorgabe `cpu` waere die gefaehrliche: Ein uebersehener
        LLM-Aufrufer verstopfte die schnelle Spur und erzeugte genau den
        Defekt wieder, gegen den die Trennung gebaut ist.

        **Die Angabe wird erzwungen, nicht geglaubt** (`_spur_kontext` in
        `services/model_services`): Ein Agent der `cpu`-Spur, der doch das
        Sprachmodell ruft, scheitert laut, statt seine Spur zu verstopfen.
        Der Grund steht in der Messung, die zu dieser Trennung gefuehrt hat:
        Die Lastart ist eine Eigenschaft des ganzen Aufrufbaums, nicht der
        Klasse — beim ersten Einordnen wurde `charakter` faelschlich fuer
        modellfrei gehalten, weil sein Modellaufruf ein Modul tiefer steht.
        """
        return "llm"

    def periodic_task(self) -> PeriodicTask | None:
        """Periodische Aufgabe dieses Agenten fuer Pixie-Scheduling.
        None = Agent arbeitet nur Queue-basiert.
        """
        return None

    @property
    def context_user(self) -> str:
        """Wessen Gedaechtnis wird gelesen/geschrieben?
        'user' = Gedaechtnis des Users (KZG/LZG/Fakten).
        'nova' = Novas eigenes Gedaechtnis.
        """
        return "user"

    @property
    def identity_user(self) -> str:
        """Wessen Charakter wird fuer LLM-Calls verwendet?
        Immer die Assistentin (ASSISTANT_USER_ID) — Pixie denkt als Nova.
        """
        return ASSISTANT_USER_ID

    # ══════════════════════════════════════════════════════════════════
    # NMCP-Anmeldung — die Angaben, die der Aufrufer zum Entscheiden
    # braucht. Alle tragen einen Vorgabewert, der "nicht deklariert"
    # bedeutet: Der Handshake soll die Luecke melden, nicht beim Start
    # abstuerzen. Was fehlt, steht im Anmeldebefund.
    # ══════════════════════════════════════════════════════════════════

    @property
    def zustellart(self) -> str:
        """Wie dieser Dienst seine Auftraege bekommt: ZUSTELLART_KANON.

        Nur ein Dienst am **Empfang** braucht einen Aushang und eine
        Quote: Er ist der einzige, ueber dessen Zustellung entschieden
        wird. Ein Dienst, der nach Zeitplan oder aus einer Queue laeuft,
        wird nicht gewaehlt — von ihm einen Aushang zu verlangen ist eine
        Forderung ohne Gegenstand.

        Kosten, Kadenz, Datenhoheit und Audit gelten fuer alle drei.

        Die Vorgabe ist abgeleitet und nicht gesetzt: Wer im
        Nutzergraphen zugelassen ist, ist ueber den Empfang erreichbar;
        wer eine periodische Aufgabe hat, laeuft nach Zeitplan; alles
        uebrige haengt an einer Queue. Ein Dienst, bei dem das nicht
        stimmt, ueberschreibt die Eigenschaft — und `delegation` ist
        genau so ein Fall (deklariert `user`, laeuft ueber den
        Hintergrund-Router).
        """
        if "user" in self.graph_eignung:
            return "empfang"
        return "zeitplan" if self.periodic_task() is not None else "queue"

    @property
    def aushang(self) -> str:
        """Woran der Empfang erkennt, dass er diesen Dienst braucht.

        In der **Sprache des Empfangs**, nicht in der Fachsprache des
        Dienstes. Der Empfang kennt die Fachsprache keiner Abteilung und
        darf sie nicht kennen — sonst ist er wieder die zentrale
        Zuordnung. Der Aushang benennt deshalb Merkmale der Aeusserung
        ("enthaelt eine Zeitangabe"), keine Operationen des Dienstes
        ("termin_erstellen").

        Nachbedingung: leerer Text heisst "nicht deklariert" und wird vom
        Handshake gemeldet.

        **Die Vorgabe erbt den Aushang des gleichnamigen Managers.** Ein
        Manager und ein Agent desselben Namens sind zwei Gesichter einer
        Fachabteilung und nicht zwei Plugins — die Zuordnung laeuft
        ueber den Namen und nicht ueber einen Import, genauso wie der
        Empfang den Agenten heute schon findet. Damit bekommt die
        Deklarationsflaeche der Agenten den Leser, den die
        Manager-Flaeche seit Monaten hat, ohne den Text zu verdoppeln.
        """
        from plugins import get_registry  # lokal: Zyklus plugins <-> agents

        manager = get_registry().get(self.name)
        if manager is None:
            return ""
        return manager.router_prompt or ""

    @property
    def negativfaelle(self) -> list[str]:
        """Aeusserungen, die dieser Dienst ausdruecklich NICHT will.

        Eine Eigenschaft der **Aeusserung**, niemals ein anderer Dienst.
        Ein Dienst kann seinen Nachbarn nicht kennen; und ein
        Ausschlussrecht waere Gift, weil es im Fehlerfall den korrekten
        Dienst mit ausschloesse — aus dem billigen sichtbaren Fehler
        wuerde der teure unsichtbare.

        Fehlrouting scheitert fast nie an fehlender Faehigkeit, sondern
        an oberflaechlicher Aehnlichkeit. Deshalb sind Negativfaelle
        Pflicht und nicht Kuer.
        """
        return []

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst ausdruecklich nicht tut.

        Unterschieden vom Negativfall: Der Negativfall steuert die
        Zustellung, die Grenze beschreibt das Koennen. Eine hohe
        Ablehnungsquote bei zutreffender Zustellquote heisst: Der Aushang
        trifft und diese Angabe fehlt.
        """
        return []

    @property
    def quote(self) -> dict[str, int]:
        """Geschaetzter Anteil der Aeusserungen je Graph, in Prozent.

        Zulaessig sind nur die Stufen aus QUOTEN_KANON. Jede Stufe ist ein
        Band, kein Punkt — niemand kann ueber seinen eigenen Dienst 37 %
        schaetzen, und wer es behauptet, hat Genauigkeit vorgetaeuscht.

        Die Angabe ist nicht dafuer da, genau zu sein, sondern dafuer,
        **falsifizierbar** zu sein: Sie gibt dem Aushang einen Leser, der
        ihm widersprechen kann. Ohne sie ist "ich bin fuer X zustaendig"
        eine Behauptung, die nicht falsch sein kann.

        Je Graph getrennt, weil die Impulsrate des Hintergrunds keinem
        Fachdienst gehoert: Ein gemeinsamer Nenner schwankt, sobald
        jemand den Takt aendert.

        Nachbedingung: leeres Dict heisst "nicht deklariert".
        """
        return {}

    @property
    def bedarf(self) -> list[Bedarf]:
        """Zustandswerte, die dieser Dienst verlangt.

        Der Dienst erhaelt, was er angemeldet hat — nicht, was vorhanden
        ist. Ohne Anmeldung bedeutet "nimm dir, was du brauchst"
        faktisch "ich gebe dir alles", und damit ist der Zustand kein
        Clipboard mehr, sondern ein Kontext-Abwurf.

        Nachbedingung: leere Liste heisst "braucht nichts" und ist
        zulaessig — nicht dasselbe wie "nicht deklariert", weil ein
        Dienst ohne Vorbedingung der Normalfall ist.
        """
        return []

    @property
    def ausgaenge(self) -> frozenset[str]:
        """Welche der vier Ausgaenge dieser Dienst bedient.

        Der vierte Ausgang ("abgelehnt") ist die Bedingung dafuer, dass
        der Dienst Zweifelsfaelle bekommen darf: Die Zustellung im
        Zweifel setzt voraus, dass die Fachabteilung ablehnen **kann**.
        Ein Dienst ohne begruendete Ablehnung fuehrt aus, was ihn
        erreicht — er beurteilt es nicht.

        Vorgabe ist der Bestand vor NMCP: drei Ausgaenge, ohne den
        vierten. Das ist Absicht — eine Vorgabe, die den vierten
        behauptet, wo er fehlt, waere eine ungelesene Deklaration mit
        Anlaufzeremonie.
        """
        return frozenset({"abgeschlossen", "fehler", "rueckfrage"})

    @abstractmethod
    def build_graph(self):
        """Baut den LangGraph-Subgraph des Agenten. Gibt CompiledStateGraph zurück."""
        ...

    def setup(self, postgres_url: str) -> None:
        """Schema anlegen via init.sql, falls vorhanden."""
        sql_pfad = Path(inspect.getfile(self.__class__)).parent / "init.sql"
        if sql_pfad.exists():
            from tools.db_manager import db_manager
            sql = sql_pfad.read_text(encoding="utf-8")
            db_manager.execute_script(sql)
            logger.info(f"Schema für Agent '{self.name}' angelegt")

    def _zustand_zuschneiden(self, state: AgentState) -> AgentState:
        """Entfernt Clipboard-Werte, die dieser Dienst nicht angemeldet hat.

        Vorbedingung: `state` traegt ein `kontext`-Dict; fehlt es, wird der
        Zustand unveraendert zurueckgegeben und der Fall gemeldet.

        Nachbedingung: `kontext` enthaelt von den zusagbaren Schluesseln
        genau die, die dieser Dienst als Bedarf angemeldet hat. Alle
        uebrigen sind entfernt, jeder einzeln protokolliert.

        **Ein Dienst erhaelt, was er angemeldet hat — nicht, was vorhanden
        ist.** Ohne diesen Schnitt bedeutet "nimm dir, was du brauchst"
        faktisch "ich gebe dir alles", und damit ist der Zustand kein
        Clipboard mehr, sondern ein Kontext-Abwurf.

        Der Schnitt sitzt hier und nicht in den Dispatches, weil das der
        einzige Engpass ist, durch den jeder Dienst laeuft. In jedem
        Dispatch einzeln waere er vierzehnmal zu pflegen und beim
        fuenfzehnten vergessen.
        """
        from agents.nmcp import ZUSAGEN  # lokal: Zyklus base <-> nmcp

        # ── Eingabe-Validierung ──────────────────────────────────────
        kontext = state.get("kontext")
        if not isinstance(kontext, dict):
            logger.error(
                "Zustandszuschnitt '%s': kontext ist %s statt dict — kein "
                "Schnitt, der Dienst erhaelt den Zustand unveraendert",
                self.name, type(kontext).__name__,
            )
            return state

        # ── Verarbeitung ─────────────────────────────────────────────
        angemeldet = {b.schluessel for b in self.bedarf}
        ungebeten = [
            s for s in kontext
            if s in ZUSAGEN and s not in angemeldet
        ]
        if not ungebeten:
            return state

        beschnitten = {k: v for k, v in kontext.items() if k not in ungebeten}
        for schluessel in ungebeten:
            logger.error(
                "Zustandszuschnitt '%s': Clipboard '%s' wurde uebergeben, "
                "aber nicht angemeldet — entfernt. Wer den Wert braucht, "
                "meldet ihn als Bedarf an; wer ihn ohne Anmeldung "
                "durchreicht, hat den Zustand zum Kontext-Abwurf gemacht",
                self.name, schluessel,
            )

        # ── Ausgabe-Verifikation ─────────────────────────────────────
        verblieben = {s for s in beschnitten if s in ZUSAGEN}
        if not verblieben <= angemeldet:
            logger.error(
                "Zustandszuschnitt '%s': nach dem Schnitt stehen %s im "
                "Kontext, angemeldet sind %s — der Schnitt hat nicht "
                "gegriffen",
                self.name, sorted(verblieben), sorted(angemeldet),
            )

        return {**state, "kontext": beschnitten}

    def invoke(self, state: AgentState) -> AgentState:
        """Führt den Subgraph aus und gibt den finalen State zurück.

        Vorbedingung: `state` ist ein AgentState mit `kontext`.
        Nachbedingung: der finale Zustand des Subgraphen.

        Vor dem Lauf wird der Zustand auf den angemeldeten Bedarf
        zugeschnitten (`_zustand_zuschneiden`).
        """
        graph = self.build_graph()
        return graph.invoke(self._zustand_zuschneiden(state))
