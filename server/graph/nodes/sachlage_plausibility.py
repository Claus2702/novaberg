"""Die Plausibilitaetspruefung gegen Weltwissen — Scheibe 7 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 7; das Zielbild
ist Schritt 4.5 in `docs/novaberg-thinking-cognitive-pipeline_k.md` und
`docs/novaberg-thinking-frames_k.md` §6: *„Mein Elefant ist gestern
hergeflogen"* — Nova soll nicht stumm zustimmen.

**Was geprueft wird und was nicht:** die Sachbehauptungen des Nutzers ueber
die akute Sache, gegen das Weltwissen des Modells. Nicht Novas eigene
Antworten (der Thinker), nicht das Gedaechtnis (Scheibe 6, der Aufloeser),
nicht ein Einwand des Nutzers gegen einen Wert, den Nova genannt hat
(`graph/einwand.py`, Sykophanz-Sprint B1). Eine Frage ist keine Behauptung.

**Warum ein eigener Call:** dieselbe Lehre wie beim Aufloeser (28.08.2026):
Der Sachlage-Call schreibt fort und soll nicht zugleich urteilen. Der Call
laeuft nur, wenn die Sachlage ein akutes Objekt traegt — Smalltalk hat keine
Frames und bekommt keine Pruefung (Frames §4.3).

**Die vier Stufen** sind die aus Frames §6.2. `plausibel` ist der Normalfall
und wird nicht gespeichert; nur die drei darueber stehen im Artefakt, damit
der Verfasser sie sieht. **Die Form der Reaktion bleibt Sache von Haltung und
Vehikel** (Frames §6.3): Die Lage sagt, dass und warum — nicht wie.
"""

import logging

from config import get_node_config
from services.model_services import model_service
from services.model_services.types import ChatRequest

logger = logging.getLogger("ki_server.sachlage.plausibility")

# Die vier Stufen (Frames §6.2), in aufsteigender Schwere. Die einzige Quelle
# der gueltigen Werte — der Prompt bekommt sie eingesetzt.
LEVEL_PLAUSIBLE:   str = "plausibel"
LEVEL_WORTH_ASKING: str = "frage_wert"
LEVEL_CONFLICT:    str = "konflikt"
LEVEL_IMPOSSIBLE:  str = "unmoeglich"
LEVELS: tuple[str, ...] = (
    LEVEL_PLAUSIBLE, LEVEL_WORTH_ASKING, LEVEL_CONFLICT, LEVEL_IMPOSSIBLE,
)
# Was im Artefakt bleibt: alles ueber dem Normalfall.
REPORTED_LEVELS: frozenset[str] = frozenset(LEVELS[1:])

# Wie viel von der Aeusserung der Call sieht — dieselbe Grenze wie der
# Sachlage-Call fuer die Aeusserung.
_UTTERANCE_MAX_CHARS: int = 1200
# Wie viele Befunde je Objekt behalten werden. Mehr als drei Zweifel an einer
# Aeusserung sind Pedanterie, nicht Verstehen.
_MAX_FINDINGS_PER_OBJECT: int = 3

PLAUSIBILITY_PROMPT: str = """Du pruefst, ob eine Aeusserung Sachbehauptungen enthaelt, die dem
Weltwissen widersprechen. Du antwortest nicht dem Nutzer.

Die Aeusserung des Nutzers:
{aeusserung}

Worum es geht (die Sachen im Raum, mit dem, was dazu schon gesagt wurde):
{objekte}

Pruefe nur BEHAUPTUNGEN des Nutzers ueber diese Sachen — eine Frage, eine
Vermutung, ein Zitat und ein Scherz sind keine Behauptung. Stufen:
- {plausibel}: passt zum Weltwissen — der Normalfall, wird nicht genannt
- {frage_wert}: physikalisch moeglich, aber ungewoehnlich genug fuer eine
  Nachfrage
- {konflikt}: widerspricht dem, was gemessen oder etabliert ist
- {unmoeglich}: verletzt ein Naturgesetz oder eine feste Grenze

Ein Befund braucht einen Gegenwert: Der Grund nennt, was stattdessen gilt.
Stimmt der genannte Wert mit deinem Wissen ueberein, ist er {plausibel} —
auch wenn Einzelheiten fehlen.

Antworte NUR mit JSON, je Objekt eine Liste der Befunde ueber {plausibel};
ein Objekt ohne Befund bekommt eine leere Liste:
{{"<Objekt>": [{{"behauptung": "die Behauptung in wenigen Worten",
              "stufe": "{frage_wert}|{konflikt}|{unmoeglich}",
              "grund": "ein Satz, was dagegen spricht"}}]}}"""


def _render_objects(artifact: dict) -> str:
    """Die akuten Objekte mit ihren gedeckten Eigenschaften, eine Zeile je Objekt."""
    zeilen: list[str] = []
    for objekt in artifact.get("objekte") or []:
        if not isinstance(objekt, dict) or not objekt.get("akut") or not objekt.get("name"):
            continue
        gedeckt: dict = objekt.get("gedeckt") or {}
        inhalt: str = "; ".join(f"{k}: {v}" for k, v in list(gedeckt.items())[:6])
        zeilen.append(f'Objekt "{objekt["name"]}"' + (f" — {inhalt}" if inhalt else ""))
    return "\n".join(zeilen)


def has_acute_object(artifact: dict) -> bool:
    """Ob die Sachlage ein akutes Objekt mit Namen traegt — die Bedingung des Calls."""
    return any(
        isinstance(o, dict) and o.get("akut") and o.get("name")
        for o in artifact.get("objekte") or []
    )


def assess_plausibility(aeusserung: str, artifact: dict) -> dict:
    """Der Plausibilitaets-Call: welche Behauptungen der Aeusserung nicht passen.

    Vorbedingung: `aeusserung` ist nicht leer; `artifact` traegt ein akutes
        Objekt (`has_acute_object`).
    Nachbedingung: Ein dict Objektname → Liste roher Befunde — die Pruefung
        gegen Stufen und Objekte macht `apply_plausibility`. Bei Ausfall
        oder unbrauchbarer Form leer, und das steht im Log.
    Fehlerfaelle: Ausnahmen des Workers werden gefangen und laut gemeldet —
        der Turn laeuft ohne Plausibilitaetsbefund weiter.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not aeusserung.strip():
        raise ValueError("Plausibilitaets-Call ohne Aeusserung")
    if not has_acute_object(artifact):
        raise ValueError("Plausibilitaets-Call ohne akutes Objekt")

    # ── Verarbeitung ────────────────────────────
    prompt: str = PLAUSIBILITY_PROMPT.format(
        aeusserung = aeusserung.strip()[:_UTTERANCE_MAX_CHARS],
        objekte    = _render_objects(artifact),
        plausibel  = LEVEL_PLAUSIBLE,
        frage_wert = LEVEL_WORTH_ASKING,
        konflikt   = LEVEL_CONFLICT,
        unmoeglich = LEVEL_IMPOSSIBLE,
    )
    node_cfg: dict = get_node_config("sachlage_plausibilitaet")
    try:
        response = model_service.chat.submit_sync(ChatRequest(
            messages          = [{"role": "user", "content": prompt}],
            temperature       = node_cfg.get("temperature", 0.0),
            max_output_tokens = node_cfg.get("max_output_tokens", 384),
            expect_json       = True,
            caller            = "sachlage_plausibilitaet",
        ), timeout=node_cfg.get("timeout_s", 30.0))
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.error(
            f"Sachlage-Plausibilitaet: Call ausgefallen ({type(fehler).__name__}: "
            f"{fehler}) — kein Befund in diesem Turn"
        )
        return {}

    # ── Ausgabe-Verifikation ────────────────────
    parsed: object = response.parsed
    if not isinstance(parsed, dict):
        logger.error(
            f"Sachlage-Plausibilitaet: Antwort ist {type(parsed).__name__} statt dict "
            f"— verworfen"
        )
        return {}
    return parsed


def _normalized(text: object) -> str:
    """Der Vergleichsschluessel eines Objektnamens."""
    return " ".join(str(text).lower().split())


# Ein Objektname, der kuerzer ist, trifft nicht per Enthaltensein — sonst
# traefe »Stern« jeden Stern.
_MIN_CONTAINMENT_CHARS: int = 4


def _match_object(name: str, objekte: dict[str, dict]) -> dict | None:
    """Das akute Objekt, das ein gemeldeter Name meint.

    `[gemessen]` 29.08.2026: Das Modell benennt das Objekt selbst — »Lichtge-
    schwindigkeit« fuer das Objekt »Pulsar«, »Neutronensternen-Rotation« fuer
    »Neutronenstern-Rotation« —, und ein woertlicher Abgleich verwarf im Labor
    3 von 3 erkannten Unmoeglichkeiten und im Betrieb die erste. Erst
    woertlich, dann Enthaltensein in beide Richtungen, und gibt es genau EIN
    akutes Objekt, gehoert der Befund ihm: Die Aeusserung handelt von ihm.

    Vorbedingung: `objekte` die akuten Objekte nach normalisiertem Namen.
    Nachbedingung: das Objekt oder None.
    """
    key: str = _normalized(name)
    if key in objekte:
        return objekte[key]
    if len(key) >= _MIN_CONTAINMENT_CHARS:
        for kandidat, objekt in objekte.items():
            if key in kandidat or (len(kandidat) >= _MIN_CONTAINMENT_CHARS and kandidat in key):
                return objekt
    if len(objekte) == 1:
        einziges: dict = next(iter(objekte.values()))
        logger.info(
            f"Sachlage-Plausibilitaet: Befund an '{name}' dem einzigen akuten Objekt "
            f"'{einziges.get('name')}' zugeordnet"
        )
        return einziges
    return None


def _valid_finding(objekt_name: str, befund: object) -> dict | None:
    """Ein Befund, gehalten gegen Stufen und Pflichtfelder — oder None, laut."""
    if not isinstance(befund, dict):
        logger.warning(
            f"Sachlage-Plausibilitaet: Befund an '{objekt_name}' ist "
            f"{type(befund).__name__} statt dict — verworfen"
        )
        return None
    stufe: str = str(befund.get("stufe", "")).strip().lower()
    behauptung: str = str(befund.get("behauptung", "")).strip()
    grund: str = str(befund.get("grund", "")).strip()
    if stufe == LEVEL_PLAUSIBLE:
        return None  # der Normalfall, kein Befund
    if stufe not in REPORTED_LEVELS or not behauptung:
        logger.warning(
            f"Sachlage-Plausibilitaet: Befund an '{objekt_name}' mit Stufe {stufe!r} "
            f"{'ohne Behauptung ' if not behauptung else ''}— verworfen"
        )
        return None
    return {"behauptung": behauptung[:200], "stufe": stufe, "grund": grund[:300]}


def _apply_object_findings(objekt: dict, name: str, befunde: list) -> tuple[int, int]:
    """Die Befunde eines Objekts: uebernommen und verworfen, gezaehlt.

    Vorbedingung: `objekt` ist akut und traegt `plausibilitaet`.
    Nachbedingung: hoechstens `_MAX_FINDINGS_PER_OBJECT` Befunde am Objekt;
        `plausibel` zaehlt weder als uebernommen noch als verworfen.
    """
    accepted: int = 0
    rejected: int = 0
    for befund in befunde:
        gueltig: dict | None = _valid_finding(name, befund)
        if gueltig is None:
            ist_normalfall: bool = (
                isinstance(befund, dict)
                and str(befund.get("stufe", "")).strip().lower() == LEVEL_PLAUSIBLE
            )
            rejected += not ist_normalfall
            continue
        if len(objekt["plausibilitaet"]) >= _MAX_FINDINGS_PER_OBJECT:
            break
        objekt["plausibilitaet"].append(gueltig)
        accepted += 1
    return accepted, rejected


def apply_plausibility(artifact: dict, findings: dict) -> dict:
    """Haelt die Befunde des Calls gegen die Objekte und schreibt sie ins Artefakt.

    Vorbedingung: `artifact` ist validiert; `findings` die Antwort des Calls
        oder leer.
    Nachbedingung: Jedes akute Objekt traegt `plausibilitaet` als Liste (auch
        leer), hoechstens `_MAX_FINDINGS_PER_OBJECT` Befunde, nur mit Stufen
        aus REPORTED_LEVELS. Die Zaehlung steht im Log, sobald der Call lief.
    Fehlerfaelle: Befunde an unbekannte oder latente Objekte, mit unbekannter
        Stufe oder ohne Behauptung — Warnung, verworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    objekte: dict[str, dict] = {}
    for objekt in artifact.get("objekte") or []:
        if isinstance(objekt, dict) and objekt.get("akut"):
            objekt.setdefault("plausibilitaet", [])
            objekte[_normalized(objekt.get("name", ""))] = objekt
    accepted: int = 0
    rejected: int = 0

    # ── Verarbeitung ────────────────────────────
    for name, befunde in (findings or {}).items():
        objekt: dict | None = _match_object(str(name), objekte)
        if objekt is None or not isinstance(befunde, list):
            logger.warning(
                f"Sachlage-Plausibilitaet: Befunde an '{name}' verworfen — "
                + ("unbekanntes oder latentes Objekt" if objekt is None
                   else f"{type(befunde).__name__} statt Liste")
            )
            rejected += 1
            continue
        uebernommen, verworfen = _apply_object_findings(objekt, str(name), befunde)
        accepted += uebernommen
        rejected += verworfen

    # ── Ausgabe-Verifikation ────────────────────
    if findings or accepted or rejected:
        logger.info(
            f"Sachlage-Plausibilitaet: {accepted} Befunde uebernommen, {rejected} verworfen"
            + (
                " — " + ", ".join(
                    f"{o.get('name')}: {b['stufe']} ({b['behauptung'][:40]})"
                    for o in objekte.values() for b in o["plausibilitaet"]
                ) if accepted else ""
            )
        )
    for objekt in objekte.values():
        if any(b["stufe"] not in REPORTED_LEVELS for b in objekt["plausibilitaet"]):
            raise ValueError("Sachlage-Plausibilitaet: Befund mit unzulaessiger Stufe im Artefakt")
    return artifact
