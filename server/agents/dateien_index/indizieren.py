"""Das Indizieren einer einzelnen Datei — Thema, Karte, Kanaele.

Spezifikation: docs/novaberg-agent-dateien_k.md §4, §5.3, §5.4.

Hier sitzt der Modellaufruf, und deshalb sitzt hier auch die Sparsamkeit:
Der Waechter entscheidet ohne Modell, WELCHE Dateien hierher kommen
(`wandern.py`). Was hier ankommt, hat eine Aenderung im Inhalt.

**Eingebettet werden Thema und Stichwoerter, nicht der Dateiinhalt** (§5.4).
Ein Volltext-Embedding ueber eine lange Datei mittelt alles zu einem
Mittelwert und findet dann nichts genau; der Inhalt ist ueber `datei_grep`
erreichbar und braucht dafuer kein Embedding.

**Dies ist der erste Aufrufer der Werkzeugschicht.** `struktur_analysieren`
liefert die Blockkarte, damit ein spaeterer Zoom ohne Dateizugriff beginnen
kann — die Schicht ist seit dem 18.08.2026 gebaut und hatte bis hierher
keinen.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from config import EMBED_MODEL, PROMPTS, get_node_config, ollama_gpu_client
from services.model_services import ChatRequest, model_service
from tools.dateien.operationen import StrukturUnklarError, struktur_analysieren

logger = logging.getLogger("ki_server.agents.dateien_index.indizieren")

#: Wie viele Zeichen vom Dateianfang das Modell sieht. Der Prompt des
#: Hintergrundpfads traegt 262144 Token; die Grenze hier ist nicht der
#: Kontext, sondern die Aussage: Ein Auszug soll ein Auszug bleiben und
#: nicht so tun, als waere er die Datei. Der Prompt sagt das ausdruecklich
#: dazu, damit das Modell keine Vollstaendigkeit behauptet.
AUSZUG_ZEICHEN: int = 6000

#: Wie viele Bloecke der Karte in den Prompt gehen. Die Karte selbst wird
#: vollstaendig gespeichert — gekuerzt wird nur, was das Modell sieht.
STRUKTUR_ZEILEN: int = 40


@dataclass(frozen=True)
class Erschliessung:
    """Was das Modell ueber eine Datei gesagt hat, plus die Blockkarte.

    `thema` leer heisst: Der Modellaufruf ist gescheitert oder unbrauchbar.
    Der Aufrufer schreibt dann keine Zeile — eine Indexzeile ohne Thema
    behauptete, die Datei sei erschlossen.

    **`struktur` kennt drei Zustaende, nicht zwei.** Eine Liste ist die
    erhobene Karte; die leere Liste heisst *„nachgesehen, keine
    Ueberschriften"*; `None` heisst *„nicht erhoben"* — kein Erkenner fuer
    dieses Format, oder die Auszeichnung geht nicht auf. Waeren die letzten
    beiden derselbe Wert, sagte der Index ueber eine ungelesene Datei aus,
    sie sei ein durchgehender Text.
    """

    thema: str
    zusammenfassung: str
    stichwoerter: list[str]
    struktur: list[dict] | None
    embedding: list[float] | None


def _auszug_lesen(datei: Path) -> str:
    """Liest den Anfang einer Datei als Text.

    Vorbedingung: `datei` existiert und ist lesbar.
    Nachbedingung: Hoechstens AUSZUG_ZEICHEN Zeichen. Nicht dekodierbare
    Bytes werden ersetzt statt zu werfen — eine Datei mit einem kaputten
    Byte ist trotzdem erschliessbar, und ein Abbruch waere hier teurer als
    ein Fragezeichen im Auszug.
    """
    roh: bytes = datei.read_bytes()[: AUSZUG_ZEICHEN * 4]
    return roh.decode("utf-8", errors="replace")[:AUSZUG_ZEICHEN]


def _struktur_text(struktur: list[dict] | None) -> str:
    """Formt die Blockkarte fuer den Prompt.

    Vorbedingung: `struktur` ist das Ergebnis von `struktur_analysieren`
    oder `None`, wenn die Karte nicht erhoben werden konnte.
    Nachbedingung: Ein mehrzeiliger Text, oder ein ausdruecklicher Hinweis —
    und die beiden Hinweise sagen Verschiedenes. Die leere Karte heisst, die
    Datei traegt keine Blockstruktur; **das ist der Normalfall im Bestand**
    und keine Stoerung: Am 17.08.2026 trugen 223 von 223 Wissensdateien keine
    einzige Ueberschrift. `None` heisst dagegen, dass niemand nachgesehen
    hat — dem Modell dieselbe Zeile zu zeigen hiesse, ihm einen Befund zu
    melden, den es nicht gibt.
    """
    if struktur is None:
        return "(Gliederung nicht erhoben — das Format ist unbekannt oder die Datei defekt)"

    if not struktur:
        return "(keine Ueberschriften — die Datei ist ein durchgehender Text)"

    zeilen: list[str] = [
        f"  {'#' * block.get('ebene', 1)} {block.get('header', '?')}"
        for block in struktur[:STRUKTUR_ZEILEN]
    ]
    if len(struktur) > STRUKTUR_ZEILEN:
        zeilen.append(f"  … und {len(struktur) - STRUKTUR_ZEILEN} weitere")
    return "\n".join(zeilen)


def embed_text_bauen(thema: str, stichwoerter: list[str]) -> str:
    """Baut den Einbettungstext einer Indexzeile — die eine Stelle dafuer.

    Vorbedingung: `thema` ist nicht leer.
    Nachbedingung: Ein Text aus Thema und Stichwoertern, **allein aus dem
    persistierten Zustand rekonstruierbar** — beide Teile stehen als eigene
    Spalten in `dateien_index`.

    **Diese Funktion ist die einzige Stelle, an der der Einbettungstext
    entsteht** (`F-EMBED-1`). Ein spaeteres Wartungswerkzeug, das den Index
    neu einbettet, ruft sie und baut den Text nicht noch einmal nach; sonst
    laufen Live-Pfad und Nachlauf auseinander, und der Unterschied faellt
    an keiner Stelle auf — er sieht aus wie ein schlechteres Ergebnis.

    **Der Dateiinhalt gehoert nicht hinein** (§5.4): Ein Volltext-Embedding
    ueber eine lange Datei mittelt alles zu einem Mittelwert. Und was man
    exakt vergleichen kann — Name, Pfad, Groesse —, gehoert ebenfalls nicht
    in den Vektor: Der Vektor findet den Kandidatenraum, die strukturierten
    Felder entscheiden danach.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not thema.strip():
        meldung: str = "embed_text_bauen(dateien_index): thema ist leer"
        raise ValueError(meldung)

    # ── Verarbeitung ────────────────────────────
    return f"{thema}\n{' '.join(stichwoerter)}".strip()


def _embedding_holen(text: str) -> list[float] | None:
    """Bettet Thema und Stichwoerter ein.

    Vorbedingung: `text` ist nicht leer.
    Nachbedingung: Ein Vektor der erwarteten Laenge, oder None mit
    Fehlermeldung. **Eine falsche Laenge wird verworfen, nicht gespeichert** —
    eine Spalte `VECTOR(768)` nimmt nichts anderes an, und ein stiller
    Fehlschlag hier hiesse: Die Zeile steht, und der dense Kanal fehlt ihr,
    ohne dass es jemand sieht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not text.strip():
        logger.error("Indizieren: leerer Einbettungstext — kein Embedding")
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        antwort = ollama_gpu_client.embed(model=EMBED_MODEL, input=text)
        vektor: list[float] = antwort["embeddings"][0]
    except (KeyError, IndexError, TypeError, OSError) as fehler:
        logger.exception(
            "Indizieren: Einbettung fehlgeschlagen (%s) — die Zeile "
            "bekommt keinen dense Kanal",
            type(fehler).__name__,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(vektor, list) or len(vektor) != 768:
        logger.error(
            "Indizieren: Einbettung hat %s statt 768 Komponenten — verworfen",
            len(vektor) if isinstance(vektor, list) else type(vektor).__name__,
        )
        return None

    return vektor


def erschliessen(datei: Path, wurzel: Path, pfad_relativ: str) -> Erschliessung:
    """Erhebt Thema, Zusammenfassung, Stichwoerter, Karte und Einbettung.

    Vorbedingung: `datei` liegt unterhalb von `wurzel` und ist lesbar; die
    Wurzelpruefung laeuft in `struktur_analysieren` noch einmal mit.
    Nachbedingung: Eine `Erschliessung`. Ist `thema` leer, ist der
    Modellaufruf gescheitert und der Aufrufer schreibt **keine** Zeile.

    Der Modellaufruf steht in der LLM-Spur (§5.3). Die Lastart ist eine
    Eigenschaft des ganzen Aufrufbaums: Der Waechter erklaert sich deshalb
    als `llm`, obwohl das Wandern selbst reine Rechnung ist.
    """
    leer = Erschliessung("", "", [], [], None)

    # ── Eingabe-Validierung ─────────────────────
    # Zwei Ausgaenge, die frueher einer waren: `StrukturUnklarError` heisst NICHT
    # ERHOBEN und wird als `None` weitergereicht; die leere Liste bliebe die
    # Aussage "durchgehender Text" ueber eine Datei, die kein Erkenner
    # gelesen hat.
    struktur: list[dict] | None
    try:
        struktur = struktur_analysieren(datei, wurzel)
    except StrukturUnklarError as fehler:
        # `exception` statt `error`: Der Fall ist selten und der Auszug zeigt,
        # welcher Erkenner gefehlt hat. TRY400 verlangt es ausserdem.
        logger.exception(
            "Indizieren: Gliederung von '%s' nicht erhoben (%s) — die Zeile "
            "entsteht ohne Blockkarte; der Grund steht im Auszug",
            pfad_relativ, type(fehler).__name__,
        )
        struktur = None
    except (ValueError, OSError) as fehler:
        logger.exception(
            "Indizieren: Blockkarte fuer '%s' nicht erhebbar (%s)",
            pfad_relativ, type(fehler).__name__,
        )
        struktur = None

    try:
        auszug: str = _auszug_lesen(datei)
    except OSError as fehler:
        logger.exception(
            "Indizieren: '%s' nicht lesbar (%s) — nicht erschlossen",
            pfad_relativ, type(fehler).__name__,
        )
        return leer

    if not auszug.strip():
        logger.error("Indizieren: '%s' ist leer — nicht erschlossen", pfad_relativ)
        return leer

    # ── Verarbeitung ────────────────────────────
    system_prompt: str = "\n\n".join([
        PROMPTS["index_datei.identity"].format(),
        PROMPTS["index_datei.task"].format(
            name=datei.name,
            pfad=pfad_relativ,
            struktur=_struktur_text(struktur),
            auszug=auszug,
        ),
        PROMPTS["index_datei.rules"].format(),
    ])
    node_cfg: dict = get_node_config("router")

    try:
        antwort = model_service.chat.submit_sync(ChatRequest(
            messages          = [{"role": "user", "content": f"Erschliesse {pfad_relativ}."}],
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.05),
            expect_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "agent/dateien_index/erschliessen",
        ))
        ergebnis = antwort.parsed
    except (json.JSONDecodeError, KeyError, AttributeError, TypeError) as fehler:
        logger.exception(
            "Indizieren: Modellantwort fuer '%s' unbrauchbar (%s)",
            pfad_relativ, type(fehler).__name__,
        )
        return leer

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(ergebnis, dict):
        logger.error(
            "Indizieren: Modellantwort fuer '%s' ist %s statt dict — verworfen",
            pfad_relativ, type(ergebnis).__name__,
        )
        return leer

    thema: str = (ergebnis.get("thema") or "").strip()
    if not thema:
        logger.error(
            "Indizieren: Modellantwort fuer '%s' ohne Thema — keine Zeile, "
            "denn eine Indexzeile ohne Thema behauptet eine Erschliessung, "
            "die nicht stattgefunden hat", pfad_relativ,
        )
        return leer

    zusammenfassung: str = (ergebnis.get("zusammenfassung") or "").strip()
    rohe_woerter = ergebnis.get("stichwoerter") or []
    if not isinstance(rohe_woerter, list):
        logger.error(
            "Indizieren: stichwoerter fuer '%s' sind %s statt Liste — leer "
            "uebernommen", pfad_relativ, type(rohe_woerter).__name__,
        )
        rohe_woerter = []
    stichwoerter: list[str] = [
        str(wort).strip() for wort in rohe_woerter if str(wort).strip()
    ]

    embedding: list[float] | None = _embedding_holen(
        embed_text_bauen(thema, stichwoerter),
    )

    logger.info(
        "Indizieren: '%s' — Thema '%s', %d Stichwoerter, %s Bloecke, "
        "Einbettung %s",
        pfad_relativ, thema[:60], len(stichwoerter),
        "nicht erhoben" if struktur is None else len(struktur),
        "ja" if embedding else "NEIN",
    )
    return Erschliessung(thema, zusammenfassung, stichwoerter, struktur, embedding)
