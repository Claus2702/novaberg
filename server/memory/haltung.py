"""Der zuletzt gerechnete Haltungsstand eines Paares — Zustand, nicht Verlauf.

Novas Haltung entsteht je Turn im Graphen und stand bis zum 15.08.2026 nur im
Zustand des Durchlaufs. Ein Dienst ausserhalb des Graphen konnte sie nicht
sehen — und damit war der Zuwendungs-Riegel nicht baubar, der entscheidet, **ob**
Nova von sich aus zugeht (`novaberg-eigenzeit_k.md` §2.5).

**Das ist kein Widerspruch zu „kein Redis-Blob".** `novaberg-haltungsraum_k.md`
§2.0a verbietet, die **Messreihe** durch einen Schluessel zu ersetzen, den jeder
Turn ueberschreibt — mit der Begruendung, ein solcher Speicher trage den
Zustand und nicht den Verlauf. Genau der Zustand wird hier gebraucht: Der
Riegel fragt nicht, wie es war, sondern wie es **ist**. Die Reihe bleibt
unberuehrt im ``pipeline_log``; dieser Schluessel ist eine zweite Auskunft mit
einem anderen Gegenstand, kein Ersatz.

**Der teure Fehler dieses Speichers hat einen Namen.** Der Weg von
``gv:detail:`` schreibt je Paar einen Schluessel ohne Frist, und ein
uebersprungener Turn hinterlaesst dort den Vorstand **ohne Kennzeichnung** —
seit Chat 116 in der Fundliste. Ein Riegel darauf entschiede nach der Lage von
vorgestern, und niemand saehe es. Deshalb gilt hier:

  * **Jeder Turn schreibt, auch der ohne Rechnung.** Ein Ausfall setzt die
    Marke und seinen Grund, statt den alten Stand stehen zu lassen.
  * **Jeder Schreibvorgang setzt jedes Feld.** Ein ``hset`` mit einer Teilmenge
    liesse die Zahlen des vorigen Turns im Hash — genau der Vorstand, den die
    Marke verhindern soll, nur eine Ebene tiefer.
  * **Drei Faelle, drei Antworten.** Kein Schluessel heisst *nie gerechnet*,
    die Marke heisst *diesmal nicht gerechnet*, ein unlesbarer Wert heisst
    *defekt*. Sie duerfen nicht auf einem Ergebnis liegen.

Kein TTL — konsistent zu ``nova_state``: Jeder Lauf ueberschreibt, und das
Alter reist im Stand mit, damit der Leser selbst entscheiden kann, ob ihm ein
Stand von gestern reicht.
"""

import logging
import time
from dataclasses import dataclass

import redis

logger = logging.getLogger("ki_server.memory.haltung")

# Die fuenf Verhaltensgroessen. Als Literal und nicht als Import aus
# `ei.haltung.GROESSEN`: Was im Speicher liegt, ist ein **Format** und wandert
# nicht automatisch mit der Rechnung mit. Kaeme dort eine Groesse hinzu, muesste
# jemand entscheiden, was mit den Bestandsschluesseln geschieht — ein
# stillschweigend mitgewanderter Import naehme ihm die Entscheidung ab.
GROESSEN_FELDER: tuple[str, ...] = ("umfang", "fragen", "naehe", "waerme", "draengen")

# Das Fuehrungsmass des Turns — **keine sechste Verhaltensgroesse.** Es steht
# bewusst neben `GROESSEN_FELDER` und nicht darin:
#
#   * Es ist ein anderer Gegenstand. Die fuenf beschreiben, **wie Nova sich
#     verhaelt**; dieses misst, **wer das Gespraech treibt**. Zwei Bedeutungen
#     unter einem Namen ist der Defekt, der am 15.08.2026 in `kzg_store` eine
#     gemessene Erregung still ueberschrieben hat.
#   * Es hat einen **eigenen Ausfall**. Die Haltung faellt aus, wenn das Rad
#     fehlt; das Fuehrungsmass, wenn seine Masse im Turn keine Quelle hatten.
#     Laegen beide auf `gerechnet`, verdeckte ein Ausfall der Haltung das
#     Fuehrungsmass — und damit **Riegel 1 den Riegel 2**, genau das, was
#     `novaberg-eigenzeit_k.md` §2.5 als nicht mehr kalibrierbar benennt.
#
# Deshalb ein Wertfeld **und** ein Grundfeld, wie beim Stand als Ganzem.
INITIATIVE_FELDER: tuple[str, ...] = ("initiative", "initiative_grund")

# Der vollstaendige Feldsatz. Er steht hier, weil **jeder** Schreibvorgang ihn
# setzt; ohne ihn waere die Vollstaendigkeit eine Absicht statt einer Regel.
HALTUNG_FELDER: tuple[str, ...] = (
    "gerechnet", "cluster", "turn_id", "zeit", "grund",
    *GROESSEN_FELDER, *INITIATIVE_FELDER,
)


@dataclass(frozen=True)
class Standkopf:
    """Wem der Stand gehoert und welcher Turn ihn geschrieben hat.

    Zusammen gesetzt, zusammen weitergegeben — deshalb eine Klasse und nicht
    drei Parameter (`novaberg-lesson_l_klassen-statt-flache-keys.md`). Dieselbe
    Bauart wie `Protokollkopf` im Zugriffsknoten, aus demselben Grund.

    Attributes:
        user_id:      das Subjekt des Paares.
        character_id: das Gegenueber.
        turn_id:      der schreibende Turn.
    """

    user_id:      str
    character_id: str
    turn_id:      str


@dataclass(frozen=True)
class Haltungsstand:
    """Der Stand, den der letzte Turn dieses Paares hinterlassen hat.

    Attributes:
        gerechnet: ob der letzte Turn eine Haltung ergeben hat.
        cluster:   die Landschaft, aus der sie stammt; leer bei einem Ausfall.
        werte:     je Groessenname das Ergebnis; **leer** bei einem Ausfall.
        turn_id:   der Turn, der diesen Stand geschrieben hat.
        zeit:      Epochensekunden des Schreibvorgangs.
        grund:     was gefehlt hat; leer, wenn gerechnet wurde.
        initiative: das Fuehrungsmass des Turns auf [-1, +1], oder ``None``.
            **Unabhaengig von `gerechnet`** — es ist eine eigene Messung mit
            einem eigenen Ausfall (siehe `INITIATIVE_FELDER`).
        initiative_grund: warum es fehlt; leer, wenn es da ist.
    """

    gerechnet: bool
    cluster:   str
    werte:     dict[str, float]
    turn_id:   str
    zeit:      float
    grund:     str
    initiative:       float | None
    initiative_grund: str

    def alter_sekunden(self, jetzt: float) -> float:
        """Wie alt dieser Stand ist.

        Als Methode mit uebergebener Zeit und nicht als Eigenschaft mit
        ``time.time()``: Ein Wert, der sich beim Lesen aendert, ist gegen ein
        Literal nicht pruefbar.

        Args:
            jetzt: die Bezugszeit in Epochensekunden.

        Returns:
            Der Abstand in Sekunden; negativ, wenn die Bezugszeit vor dem
            Schreibvorgang liegt — das wird nicht geglaettet, weil eine Uhr,
            die rueckwaerts laeuft, ein Befund ist.
        """
        # ── Ausgabe ─────────────────────────────────
        return jetzt - self.zeit


def haltung_schluessel(user_id: str, character_id: str) -> str:
    """Der Redis-Schluessel des Paares.

    An einer Stelle, weil Schreiber und Leser ihn brauchen — zweimal
    hingeschrieben waere er die Stelle, an der beide auseinanderlaufen.

    Args:
        user_id:      das Subjekt des Paares.
        character_id: das Gegenueber.

    Returns:
        Der Schluessel.
    """
    # ── Ausgabe ─────────────────────────────────
    return f"haltung:{user_id}:{character_id}"


def haltung_speichern(
    redis_client: redis.Redis,
    kopf:         Standkopf,
    *,
    cluster:      str,
    werte:        dict[str, float],
    grund:        str,
    initiative:       float | None,
    initiative_grund: str,
) -> bool:
    """Schreibt den Stand dieses Turns — auch den, an dem nichts gerechnet wurde.

    `initiative` und `initiative_grund` sind **Pflichtargumente ohne
    Vorgabewert**, obwohl ein `None` bequem waere. Ein Vorgabewert hiesse, dass
    eine vergessene Uebergabe still „kein Fuehrungsmass" schreibt; Riegel 2
    laese das als *unbekannt* und blockte — richtig im Ergebnis, unsichtbar in
    der Ursache. So faellt eine vergessene Stelle beim ersten Aufruf auf.

    Args:
        redis_client: Verbindung.
        kopf:         Paar und schreibender Turn.
        cluster:      die Landschaft, oder leer bei einem Ausfall.
        werte:        je Groessenname das Ergebnis, oder leer bei einem Ausfall.
        grund:        was gefehlt hat; leer, wenn gerechnet wurde.
        initiative:       das Fuehrungsmass des Turns, oder ``None``.
        initiative_grund: warum es fehlt; leer, wenn es da ist.

    Vorbedingung: Die drei Felder des Kopfes sind belegt. Ein Stand ohne
        Turnbezug liesse sich keiner Lage zuordnen und wird nicht geschrieben.
    Nachbedingung: Der Hash traegt **alle** Felder aus `HALTUNG_FELDER`; die
        Zahlen sind bei einem Ausfall ausdruecklich leer und nicht null.
    Fehlerfaelle: Ein Speicherfehler ist eine Luecke in der Reihe und kein
        toter Turn — gemeldet und mit ``False`` beantwortet, nicht geworfen.
        **Nur Speicherfehler**: Ein Programmierfehler soll laut sein und wird
        nicht mitgefangen, sonst ist er von einem ausgefallenen Redis nicht
        mehr zu unterscheiden.

    Returns:
        True, wenn geschrieben wurde.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not kopf.user_id or not kopf.character_id:
        logger.error(
            "Haltungsstand: Paar unvollstaendig — user_id=%r, character_id=%r, "
            "nichts geschrieben", kopf.user_id, kopf.character_id,
        )
        return False

    if not kopf.turn_id:
        logger.error(
            "Haltungsstand: kein turn_id fuer %s:%s — ein Stand ohne Turnbezug "
            "waere keiner Lage zuzuordnen, nichts geschrieben",
            kopf.user_id, kopf.character_id,
        )
        return False

    gerechnet: bool = bool(werte)

    # ── Verarbeitung ────────────────────────────
    # **Jedes Feld, bei jedem Schreibvorgang.** Eine Teilmenge liesse die
    # Zahlen des vorigen Turns stehen — der Vorstand, den die Marke gerade
    # verhindern soll.
    inhalt: dict[str, str] = {
        "gerechnet": "1" if gerechnet else "0",
        "cluster":   cluster,
        "turn_id":   kopf.turn_id,
        "zeit":      str(time.time()),
        "grund":     grund,
    }
    for name in GROESSEN_FELDER:
        wert: float | None = werte.get(name)
        inhalt[name] = "" if wert is None else str(wert)

    # Das Fuehrungsmass wird **nicht** an `gerechnet` gehaengt: Ein Turn ohne
    # Haltung kann sehr wohl ein Fuehrungsmass getragen haben, und umgekehrt.
    inhalt["initiative"]       = "" if initiative is None else str(initiative)
    inhalt["initiative_grund"] = initiative_grund

    try:
        redis_client.hset(
            haltung_schluessel(kopf.user_id, kopf.character_id), mapping=inhalt,
        )
    except redis.RedisError:
        logger.exception(
            "Haltungsstand fuer %s:%s nicht geschrieben — der Turn laeuft "
            "weiter, der Riegel liest den vorigen Stand mit seinem Alter",
            kopf.user_id, kopf.character_id,
        )
        return False

    # ── Ausgabe-Verifikation ────────────────────
    logger.debug(
        "Haltungsstand fuer %s:%s geschrieben — turn=%s, gerechnet=%s%s",
        kopf.user_id, kopf.character_id, kopf.turn_id, gerechnet,
        "" if gerechnet else f", Grund: {grund}",
    )
    return True


def _werte_lesen(roh: dict, schluessel: str) -> tuple[dict[str, float], str]:
    """Liest die fuenf Zahlen aus dem Hash.

    Vorbedingung: `roh` traegt die Marke ``gerechnet = 1``.
    Nachbedingung: (Werte, Grund). Der Grund ist leer, wenn alle fuenf lesbar
        waren; sonst sind die Werte leer und der Grund benennt das erste
        unlesbare Feld.
    Fehlerfaelle: Ein unlesbarer Wert ist ein **Defekt**, kein Leerfall — er
        wird gemeldet und macht den ganzen Stand ungueltig. Vier von fuenf
        Groessen sind keine Haltung.

    Args:
        roh:        der Hash.
        schluessel: fuer die Meldung.

    Returns:
        Die Werte und den Grund.
    """
    # ── Verarbeitung ────────────────────────────
    werte: dict[str, float] = {}
    for name in GROESSEN_FELDER:
        try:
            werte[name] = float(roh.get(name, ""))
        except (TypeError, ValueError):
            logger.exception(
                "Haltungsstand %s: Feld %r traegt %r und ist keine Zahl — der "
                "Stand gilt als nicht gerechnet; vier von fuenf Groessen sind "
                "keine Haltung", schluessel, name, roh.get(name),
            )
            return {}, f"unlesbar: {name}"

    # ── Ausgabe ─────────────────────────────────
    return werte, ""


def _initiative_lesen(roh: dict, schluessel: str) -> tuple[float | None, str]:
    """Liest das Fuehrungsmass aus dem Hash.

    **Drei Faelle, wie beim Stand als Ganzem.** Ein Bestandsschluessel aus der
    Zeit vor diesem Feld traegt es gar nicht — das ist *nie geschrieben* und
    etwas anderes als ein Turn, in dem das Mass keine Quelle hatte. Beide
    liefern ``None``, aber mit verschiedenem Grund, damit eine Auswertung einen
    alten Schluessel nicht als Messausfall zaehlt.

    Vorbedingung: keine.
    Nachbedingung: (Wert, Grund). Der Grund ist leer, wenn ein Wert da ist.
    Fehlerfaelle: Ein unlesbarer Wert ist ein **Defekt** und wird gemeldet; er
        liefert ``None`` mit benanntem Grund, nie eine Zahl.

    Args:
        roh:        der Hash.
        schluessel: fuer die Meldung.

    Returns:
        Das Fuehrungsmass und den Grund seines Fehlens.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "initiative" not in roh:
        return None, "feld_fehlt"

    rohwert = roh.get("initiative", "")
    if rohwert == "":
        # Der Turn hat geschrieben und hatte kein Mass. Sein Grund steht im
        # Nachbarfeld; ist auch der leer, ist das selbst ein Befund.
        return None, str(roh.get("initiative_grund", "")) or "ohne_grund"

    # ── Verarbeitung / Ausgabe ──────────────────
    try:
        return float(rohwert), ""
    except (TypeError, ValueError):
        logger.exception(
            "Haltungsstand %s: Feld 'initiative' traegt %r und ist keine Zahl "
            "— gilt als kein Fuehrungsmass", schluessel, rohwert,
        )
        return None, "unlesbar"


def haltung_lesen(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> Haltungsstand | None:
    """Holt den zuletzt geschriebenen Haltungsstand eines Paares.

    Args:
        redis_client: Verbindung.
        user_id:      das Subjekt des Paares.
        character_id: das Gegenueber.

    Vorbedingung: keine.
    Nachbedingung: ``None`` heisst **nie gerechnet** fuer dieses Paar; ein
        Stand mit ``gerechnet = False`` heisst *diesmal nicht*, mit Grund. Die
        beiden Faelle liegen ausdruecklich nicht auf einem Ergebnis — sonst
        waere ein Paar ohne Historie von einem Turn ohne Landschaft nicht zu
        unterscheiden.
    Fehlerfaelle: Ein Lesefehler wird gemeldet und wie *nie gerechnet*
        behandelt; wer den Stand braucht, prueft ohnehin auf ``None``.

    Returns:
        Der Stand, oder ``None``.
    """
    # ── Eingabe-Validierung ─────────────────────
    schluessel: str = haltung_schluessel(user_id, character_id)

    try:
        roh: dict = redis_client.hgetall(schluessel) or {}
    except redis.RedisError:
        logger.exception(
            "Haltungsstand %s nicht lesbar — behandelt wie kein Stand",
            schluessel,
        )
        return None

    if not roh:
        return None

    # ── Verarbeitung ────────────────────────────
    gerechnet: bool = str(roh.get("gerechnet", "")) == "1"
    grund:     str  = str(roh.get("grund", ""))
    werte:     dict[str, float] = {}

    if gerechnet:
        werte, lesefehler = _werte_lesen(roh, schluessel)
        if lesefehler:
            gerechnet = False
            grund     = lesefehler

    try:
        zeit: float = float(roh.get("zeit", ""))
    except (TypeError, ValueError):
        logger.exception(
            "Haltungsstand %s: Zeitstempel %r unlesbar — der Stand gilt als "
            "beliebig alt", schluessel, roh.get("zeit"),
        )
        zeit = 0.0

    initiative, initiative_grund = _initiative_lesen(roh, schluessel)

    # ── Ausgabe ─────────────────────────────────
    return Haltungsstand(
        gerechnet = gerechnet,
        cluster   = str(roh.get("cluster", "")),
        werte     = werte,
        turn_id   = str(roh.get("turn_id", "")),
        zeit      = zeit,
        grund     = grund,
        initiative       = initiative,
        initiative_grund = initiative_grund,
    )
