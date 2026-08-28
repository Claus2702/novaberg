"""Der Frame-Aufloeser, Konversationsfassung — Scheibe 6 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 6; das Zielbild
ist Schritt 4.3 in `docs/novaberg-thinking-cognitive-pipeline_k.md`: Luecken
eines Frames gegen Wissensquellen halten und je aufgeloestem Slot die
Quelle vermerken.

**Warum kein zweiter Suchlauf:** Der Enricher sucht bei jedem Turn KZG,
LZG, die Bibliothek (`autonomous_wissen`) und die Aufzeichnungen mit dem
Suchvektor des Turns und legt sie in `state["memory_entries"]` und
`state["aufzeichnungen"]` ab — bevor die Sachlage rechnet. Der Aufloeser
macht aus diesem Pool ein **nummeriertes Angebot** (G1 … Gn).

**Warum ein eigener Call, und kein Feld im Sachlage-Call:** `[gemessen]`
28.08.2026, Pulsar-Anordnung, 5 Laeufe je Fassung. Als Feld im Sachlage-
Call beanspruchte das Modell die richtige Eigenschaft in einer Fassung 5/5
— angeschoben vom Beispiel »G2« im Prompt, das zufaellig der richtige
Eintrag war —, in drei weiteren Fassungen 0/5, 1/5 und 1/5, und dazu je
Lauf ein bis zwei Eigenschaften, die nie offen waren. Der Sachlage-Call
schreibt fort und soll nicht zugleich urteilen. Der Aufloeser-Call bekommt
deshalb **nur** die offenen Eigenschaften der akuten Objekte und das
Angebot, und seine Antwort wird **gegen das Angebot gehalten**: Nur eine
Referenz, die angeboten war, deckt — und dann traegt das Objekt die Quelle
in `quellen`. Er laeuft nur, wenn es Angebot und offene Eigenschaften gibt.

**Was nicht befragt wird:** Der Fakten-Graph des Pipeline-Konzepts traegt
fuer das Paar 0 Zeilen (28.08.2026); Notizen nicht, weil der einzige Leser
mit Treffersemantik `last_touched` schreibt.

**Die Reihenfolge des Angebots ist je Quelle fest, nicht ueber Quellen
sortiert:** Kalender (Namenstreffer), dann der Pool nach Gewicht, dann die
Aufzeichnungen nach Kosinus. Eine Rangfolge ueber drei Skalen waere eine
Rangfolge aus Skalen statt aus Bedeutungen (`plugins/wissen_manager`).

**Was hier nicht liegt:** die Suche je offener Eigenschaft (der Pool ist mit
dem Reiz gesucht, nicht mit der Luecke), das Frame-Lager, die Kritikalitaet
einer Luecke, die Plausibilitaet.
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from config import (
    POSTGRES_URL,
    SACHLAGE_BESTAND_KALENDER_LIMIT,
    SACHLAGE_BESTAND_MAX_EINTRAEGE,
    get_node_config,
)
from memory.repositories.timeline_repository import TimelineRepository
from services.model_services import model_service
from services.model_services.types import ChatRequest

logger = logging.getLogger("ki_server.sachlage.resolver")

# Die Quellen, die ein Angebotseintrag tragen kann. `kzg`, `lzg` und
# `plugin_wissen` sind die `quelle`-Marken des ContextEntry-Pools
# (`graph/context_entry.py`); die beiden anderen vergibt dieses Modul.
SOURCE_KZG:      str = "kzg"
SOURCE_LZG:      str = "lzg"
SOURCE_LIBRARY:  str = "plugin_wissen"
SOURCE_RECORDS:  str = "aufzeichnung"
SOURCE_CALENDAR: str = "timeline"

# Welche Pool-Quellen ins Angebot duerfen. Charakter-Hash und
# Gespraechs-Zusammenfassung sagen nichts ueber eine Sache.
_POOL_SOURCES: frozenset[str] = frozenset({SOURCE_KZG, SOURCE_LZG, SOURCE_LIBRARY})

# Wie der Verfasser die Herkunft einer Deckung hoert — nicht der
# Tabellenname, sondern woher Nova es weiss.
SOURCE_LABELS: dict[str, str] = {
    SOURCE_KZG:      "aus frueheren Gespraechen",
    SOURCE_LZG:      "aus frueheren Gespraechen",
    SOURCE_LIBRARY:  "aus ihrer Recherche",
    SOURCE_RECORDS:  "aus Unterlagen",
    SOURCE_CALENDAR: "aus dem Kalender",
}

# Wie viel von einem Eintrag das Angebot zeigt. Bibliothekszeilen sind im
# Mittel ~690 Zeichen lang, bis 3624 (28.08.2026) — ganz gezeigt frisst ein
# einziger Eintrag das Fenster, das die Sachlage fuer den Verlauf braucht.
ENTRY_MAX_CHARS: int = 320

# Das Angebot im Prompt. Beginnt wie die Wiederaufnahme-Sektion mit einer
# Leerzeile; ohne Angebot bleibt der Prompt zeichengleich mit dem vorigen.
_SECTION_HEAD: str = (
    "\nWas Novas Gedaechtnis zu dieser Sache haelt (nummeriertes Angebot):\n"
)


@dataclass(frozen=True)
class MemoryHit:
    """Ein Eintrag des Angebots — reiner Datencontainer.

    `key` ist die Nummer, ueber die das Modell ihn referenziert (»G3«);
    `source` eine der SOURCE_*-Marken; `origin` die Fundstelle (Dateipfad,
    Kalender-id, LZG-Dimension), damit eine Deckung rueckverfolgbar bleibt;
    `content` der gekuerzte Text.
    """

    key:     str
    source:  str
    origin:  str
    content: str


def _field(record: object, name: str) -> object:
    """Liest ein Feld aus einer Dataclass oder einem dict.

    Die Aufzeichnungen kommen als Dataclass, nach einer Serialisierung des
    Zustands als dict.
    """
    if isinstance(record, dict):
        return record.get(name)
    return getattr(record, name, None)


def _calendar_hits(state: dict, previous: dict | None) -> list[tuple[str, str, str]]:
    """Kalendereintraege zu den akuten Objekten der vorigen Blase.

    Vorbedingung: `previous` ist ein Artefakt oder None.
    Nachbedingung: Tripel (Quelle, Herkunft, Text), hoechstens
        `SACHLAGE_BESTAND_KALENDER_LIMIT` je Objekt; ohne akute Objekte leer.
    Fehlerfaelle: Ein Datenbankfehler ist laut und liefert keine
        Kalendereintraege — der Turn geht vor.
    """
    if not previous:
        return []
    user_id: str = str(state.get("user_id", ""))
    hits: list[tuple[str, str, str]] = []
    for objekt in previous.get("objekte") or []:
        name: str = str(objekt.get("name", "")).strip()
        if not objekt.get("akut") or not name:
            continue
        try:
            rows: list[dict] = TimelineRepository.find_by_keyword(
                POSTGRES_URL, user_id, name, "both", SACHLAGE_BESTAND_KALENDER_LIMIT,
            )
        except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
            logger.warning(
                f"Sachlage-Aufloeser: Kalendersuche zu '{name[:40]}' ausgefallen "
                f"({type(fehler).__name__}: {fehler}) — ohne Kalender"
            )
            return hits
        for row in rows:
            zeit = row.get("event_time")
            datum: str = (
                zeit.strftime("%d.%m.%Y") if isinstance(zeit, datetime) else str(zeit or "")
            )
            text: str = f"Kalender {datum}: {row.get('title', '')}"
            if row.get("details"):
                text += f" — {row['details']}"
            hits.append((SOURCE_CALENDAR, f"timeline#{row.get('id', '')}", text))
    return hits


def memory_offer(state: dict, previous: dict | None) -> list[MemoryHit]:
    """Das Angebot dieses Turns: was Novas Gedaechtnis zur Sache haelt.

    Vorbedingung: `state` traegt, was der Enricher abgelegt hat —
        `memory_entries` (ContextEntry-Pool) und `aufzeichnungen`; beide
        duerfen fehlen.
    Nachbedingung: Hoechstens `SACHLAGE_BESTAND_MAX_EINTRAEGE` Eintraege,
        durchnummeriert G1 … Gn, Kalender zuerst, dann Pool nach Gewicht,
        dann Aufzeichnungen nach Kosinus; jeder Text gekuerzt. Die Groessen
        stehen im Log, bevor gekappt wird (F-LOG-3).
    Fehlerfaelle: keine — ein leerer Pool ist ein regulaerer Fall.
    """
    # ── Eingabe-Validierung ─────────────────────
    entries: list = state.get("memory_entries") or []
    records: list = state.get("aufzeichnungen") or []

    # ── Verarbeitung ────────────────────────────
    candidates: list[tuple[str, str, str]] = _calendar_hits(state, previous)
    kalender: int = len(candidates)

    pool: list[tuple[float, str, str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        source: str = str(entry.get("quelle", ""))
        content: str = str(entry.get("inhalt", "")).strip()
        if source not in _POOL_SOURCES or not content:
            continue
        meta: dict = entry.get("meta") or {}
        origin: str = str(
            meta.get("dateipfad") or meta.get("dimension") or entry.get("subtyp") or ""
        )
        pool.append((float(entry.get("gewicht", 0.0)), source, origin, content))
    pool.sort(key=lambda p: p[0], reverse=True)
    candidates.extend((s, o, c) for _, s, o, c in pool)

    unterlagen: list[tuple[float, str, str, str]] = []
    for record in records:
        thema: str = str(_field(record, "thema") or "").strip()
        zusammenfassung: str = str(_field(record, "zusammenfassung") or "").strip()
        if not thema and not zusammenfassung:
            continue
        unterlagen.append((
            float(_field(record, "kosinus") or 0.0),
            SOURCE_RECORDS,
            str(_field(record, "fundstelle") or ""),
            f"{thema}: {zusammenfassung}" if thema else zusammenfassung,
        ))
    unterlagen.sort(key=lambda u: u[0], reverse=True)
    candidates.extend((s, o, c) for _, s, o, c in unterlagen)

    logger.info(
        f"Sachlage-Aufloeser: Angebot aus Kalender {kalender}, Pool {len(pool)} "
        f"(von {len(entries)}), Aufzeichnungen {len(unterlagen)} — "
        f"gekappt auf {SACHLAGE_BESTAND_MAX_EINTRAEGE}"
    )
    hits: list[MemoryHit] = [
        MemoryHit(
            key     = f"G{nummer}",
            source  = source,
            origin  = origin,
            content = content[:ENTRY_MAX_CHARS],
        )
        for nummer, (source, origin, content)
        in enumerate(candidates[:SACHLAGE_BESTAND_MAX_EINTRAEGE], start=1)
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if len({h.key for h in hits}) != len(hits):
        raise ValueError("Sachlage-Aufloeser: Angebot mit doppelter Nummer")
    return hits


def render_memory_section(hits: list[MemoryHit]) -> str:
    """Die Angebots-Sektion des Sachlage-Prompts — leer ohne Angebot.

    Vorbedingung: `hits` aus `memory_offer`.
    Nachbedingung: "" ohne Eintraege — der Prompt bleibt dann zeichengleich
        mit dem ohne Aufloeser; sonst eine Zeile je Eintrag mit Nummer und
        Herkunftslabel.
    """
    if not hits:
        return ""
    zeilen: list[str] = [
        f"{h.key} [{SOURCE_LABELS.get(h.source, h.source)}] {h.content}" for h in hits
    ]
    return _SECTION_HEAD + "\n".join(zeilen) + "\n"


RESOLVER_PROMPT: str = """Du pruefst, ob Eintraege aus Novas Gedaechtnis offene Fragen zu
einer Sache beantworten. Du antwortest nicht dem Nutzer.
{angebot}
Die offenen Eigenschaften:
{offen}

Fuer jede offene Eigenschaft: Beantwortet einer der Eintraege genau diese
Eigenschaft — nicht nur dieselbe Sache? Dann nenne die Nummer des Eintrags
und in einem Satz, was er dazu sagt. Ein Eintrag, der die Eigenschaft nicht
nennt, deckt nichts; dann lass sie weg.

Antworte NUR mit JSON, je Objekt ein Schluessel, je gedeckter Eigenschaft
ihr Wortlaut:
{{"<Objekt>": {{"<Eigenschaft>": {{"eintrag": "G<n>", "inhalt": "was der Eintrag dazu sagt"}}}}}}
Ein Objekt ohne gedeckte Eigenschaft bekommt {{}}."""


def open_properties(artifact: dict) -> list[tuple[str, list[str]]]:
    """Die offenen Eigenschaften der akuten Objekte — der Gegenstand des Aufloeser-Calls.

    Vorbedingung: `artifact` ist validiert.
    Nachbedingung: Paare (Objektname, offen), nur akute Objekte mit
        mindestens einer offenen Eigenschaft; leer erlaubt.
    """
    return [
        (str(o.get("name", "")), [str(e) for e in o.get("offen") or []])
        for o in artifact.get("objekte") or []
        if isinstance(o, dict) and o.get("akut") and o.get("offen") and o.get("name")
    ]


def resolve_open_properties(
    offen: list[tuple[str, list[str]]],
    hits:  list[MemoryHit],
) -> dict:
    """Der Aufloeser-Call: welche offenen Eigenschaften das Angebot beantwortet.

    Vorbedingung: `offen` aus `open_properties`, nicht leer; `hits` das
        Angebot, nicht leer.
    Nachbedingung: Ein dict Objektname → {Eigenschaft → {eintrag, inhalt}},
        roh — die Pruefung gegen Angebot und `offen` macht
        `apply_memory_coverage`. Bei Ausfall oder unbrauchbarer Form leer,
        und das steht im Log.
    Fehlerfaelle: Ausnahmen des Workers werden gefangen und laut gemeldet —
        der Turn laeuft ohne Deckung aus dem Gedaechtnis weiter.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not offen or not hits:
        raise ValueError("Aufloeser-Call ohne offene Eigenschaften oder ohne Angebot")

    # ── Verarbeitung ────────────────────────────
    prompt: str = RESOLVER_PROMPT.format(
        angebot = render_memory_section(hits),
        offen   = "\n".join(f'Objekt "{name}": ' + "; ".join(eigen) for name, eigen in offen),
    )
    node_cfg: dict = get_node_config("sachlage_aufloeser")
    try:
        response = model_service.chat.submit_sync(ChatRequest(
            messages          = [{"role": "user", "content": prompt}],
            temperature       = node_cfg.get("temperature", 0.0),
            max_output_tokens = node_cfg.get("max_output_tokens", 384),
            expect_json       = True,
            caller            = "sachlage_aufloeser",
        ), timeout=node_cfg.get("timeout_s", 30.0))
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.error(
            f"Sachlage-Aufloeser: Call ausgefallen ({type(fehler).__name__}: {fehler}) "
            f"— keine Deckung aus dem Gedaechtnis in diesem Turn"
        )
        return {}

    # ── Ausgabe-Verifikation ────────────────────
    parsed: object = response.parsed
    if not isinstance(parsed, dict):
        logger.error(
            f"Sachlage-Aufloeser: Antwort ist {type(parsed).__name__} statt dict — verworfen"
        )
        return {}
    return parsed


def _normalized(text: object) -> str:
    """Der Vergleichsschluessel einer Eigenschaft: Kleinschreibung, ein Leerzeichen."""
    return " ".join(str(text).lower().split())


# Ein Anspruchsschluessel, der kuerzer ist, darf nicht per Enthaltensein
# treffen — »art« steckt in jeder »Bauart«.
_MIN_CONTAINMENT_CHARS: int = 4


def _match_open(claim_key: str, offen: list) -> str | None:
    """Die offene Eigenschaft, die ein Anspruchsschluessel meint.

    `[gemessen]` 28.08.2026: Das Modell schreibt den Schluessel als Kurzform
    (»zerfall« fuer »Zerfall des Feldes«) — ohne diesen Abgleich blieb die
    Eigenschaft gedeckt UND offen. Erst der woertliche Treffer, sonst
    Enthaltensein in beide Richtungen ab `_MIN_CONTAINMENT_CHARS`.

    Vorbedingung: `offen` die Liste des Objekts.
    Nachbedingung: Der Wortlaut aus `offen` oder None.
    """
    key: str = _normalized(claim_key)
    if not key:
        return None
    for eintrag in offen:
        if _normalized(eintrag) == key:
            return str(eintrag)
    if len(key) < _MIN_CONTAINMENT_CHARS:
        return None
    for eintrag in offen:
        kandidat: str = _normalized(eintrag)
        if key in kandidat or (len(kandidat) >= _MIN_CONTAINMENT_CHARS and kandidat in key):
            return str(eintrag)
    return None


# Die drei Ausgaenge eines Anspruchs — die Zaehlung im Log haengt daran.
CLAIM_COVERED:  str = "gedeckt"
CLAIM_REJECTED: str = "verworfen"
CLAIM_NOT_OPEN: str = "nicht_offen"


def _apply_claim(
    objekt:          dict,
    eigenschaft:     str,
    claim:           object,
    offered:         dict[str, MemoryHit],
    previously_open: list,
) -> str:
    """Ein Anspruch des Modells auf eine Deckung aus dem Gedaechtnis.

    **Offen heisst: offen vor oder nach diesem Turn.** Das Modell nimmt eine
    Eigenschaft, die es fuer gedeckt haelt, aus `offen` heraus — dann steht
    sie nur noch in der vorigen Blase. Beide Listen zaehlen; der Wortlaut,
    unter dem sie gefuehrt wird, ist der aus `offen`, sonst der vorige.

    Vorbedingung: `objekt` ist akut und traegt `quellen`; `offered` das
        Angebot nach Nummer; `previously_open` die `offen`-Liste desselben
        Objekts in der vorigen Blase (leer erlaubt).
    Nachbedingung: Einer der drei CLAIM_*-Ausgaenge. Bei CLAIM_COVERED steht
        die Eigenschaft in `gedeckt` und `quellen` und nicht mehr in `offen`;
        sonst ist das Objekt unveraendert.
    Fehlerfaelle: nicht angeboten oder ohne Inhalt — Warnung; nicht offen —
        INFO (die Regel des Modells, kein Defekt).
    """
    key: str = str(claim.get("eintrag", "")) if isinstance(claim, dict) else ""
    inhalt: str = str(claim.get("inhalt", "")).strip() if isinstance(claim, dict) else ""
    if key not in offered or not inhalt:
        logger.warning(
            f"Sachlage-Aufloeser: Deckung von '{eigenschaft}' an "
            f"'{objekt.get('name')}' verweist auf {key!r}"
            f"{' ohne Inhalt' if not inhalt else ' — nicht angeboten'} — verworfen"
        )
        return CLAIM_REJECTED
    offene: str | None = (
        _match_open(eigenschaft, objekt.get("offen") or [])
        or _match_open(eigenschaft, previously_open)
    )
    if offene is None:
        logger.info(
            f"Sachlage-Aufloeser: '{eigenschaft}' an '{objekt.get('name')}' war nicht "
            f"offen — Anspruch aus {key} nicht uebernommen"
        )
        return CLAIM_NOT_OPEN
    hit: MemoryHit = offered[key]
    gedeckt: dict = objekt.get("gedeckt") or {}
    gedeckt[offene] = inhalt
    objekt["gedeckt"] = gedeckt
    objekt["quellen"][offene] = {
        "quelle": hit.source, "herkunft": hit.origin, "eintrag": key,
    }
    objekt["offen"] = [o for o in objekt["offen"] if str(o) != offene]
    return CLAIM_COVERED


def _assert_covered_not_open(artifact: dict) -> None:
    """Die Nachbedingung des Aufloesers: nichts ist gedeckt und offen zugleich."""
    for objekt in artifact.get("objekte") or []:
        for eigenschaft in objekt.get("quellen") or {}:
            if eigenschaft in (objekt.get("offen") or []):
                raise ValueError(
                    f"Sachlage-Aufloeser: '{eigenschaft}' gedeckt und offen zugleich"
                )


def apply_memory_coverage(
    artifact: dict,
    hits:     list[MemoryHit],
    claims:   dict,
    previous: dict | None = None,
) -> dict:
    """Haelt die Ansprueche des Aufloeser-Calls gegen Angebot und offene Eigenschaften.

    `claims` ist die rohe Antwort des Calls: Objektname → Eigenschaft →
    {eintrag, inhalt}. Nur eine Referenz auf einen **angebotenen** Eintrag
    deckt, und nur eine Eigenschaft, die **offen** ist — vor oder nach
    diesem Turn: Die Eigenschaft wandert von `offen` nach `gedeckt`, und
    `quellen` traegt Quelle, Herkunft und Nummer. Alles andere wird
    verworfen und gesagt.

    **Ein Anspruch gilt nur einer Eigenschaft, die offen ist.** `[gemessen]`
    28.08.2026, Labor: Als Feld im Sachlage-Call meldete das Modell in 5 von
    5 Laeufen Deckungen fuer Eigenschaften, die nie offen waren (»entstehung«,
    »rotation«) — das Gedaechtnis weiss vieles, gefragt ist nur die Luecke.

    Vorbedingung: `artifact` ist validiert (`_validate_artifact`); `hits`
        das Angebot desselben Turns (leer erlaubt); `claims` die Antwort des
        Calls oder leer; `previous` die vorige Blase oder None — ihre
        `offen`-Listen zaehlen als offen.
    Nachbedingung: Jedes akute Objekt traegt `quellen` (auch leer); eine
        gedeckte Eigenschaft steht nicht mehr in `offen`, und sie traegt in
        `gedeckt` und `quellen` den Wortlaut aus `offen`. Die Zaehlung steht
        im Log, sobald ein Angebot vorlag.
    Fehlerfaelle: Eine Referenz ausserhalb des Angebots, ein Anspruch ohne
        Inhalt, ein Anspruch an ein unbekanntes oder latentes Objekt — je
        eine Warnung, kein Abbruch. Ein Anspruch auf eine nicht offene
        Eigenschaft wird gezaehlt und auf INFO genannt.
    """
    # ── Eingabe-Validierung ─────────────────────
    offered: dict[str, MemoryHit] = {h.key: h for h in hits}
    vorher_offen: dict[str, list] = {
        _normalized(o.get("name", "")): list(o.get("offen") or [])
        for o in (previous or {}).get("objekte") or []
        if isinstance(o, dict)
    }
    objekte: dict[str, dict] = {}
    for objekt in artifact.get("objekte") or []:
        if objekt.get("akut"):
            objekt.setdefault("quellen", {})
            objekte[_normalized(objekt.get("name", ""))] = objekt
    covered: int = 0
    rejected: int = 0
    not_open: int = 0

    # ── Verarbeitung ────────────────────────────
    for name, ansprueche in (claims or {}).items():
        objekt: dict | None = objekte.get(_normalized(name))
        if objekt is None or not isinstance(ansprueche, dict):
            grund: str = (
                "unbekanntes oder latentes Objekt" if objekt is None
                else f"{type(ansprueche).__name__} statt dict"
            )
            logger.warning(f"Sachlage-Aufloeser: Ansprueche an '{name}' verworfen — {grund}")
            rejected += 1
            continue
        previously_open: list = vorher_offen.get(_normalized(name), [])
        for eigenschaft, claim in ansprueche.items():
            ausgang: str = _apply_claim(
                objekt, str(eigenschaft), claim, offered, previously_open,
            )
            covered  += ausgang == CLAIM_COVERED
            rejected += ausgang == CLAIM_REJECTED
            not_open += ausgang == CLAIM_NOT_OPEN

    # ── Ausgabe-Verifikation ────────────────────
    if hits or covered or rejected or not_open:
        logger.info(
            f"Sachlage-Aufloeser: {covered} offene Eigenschaften aus dem Gedaechtnis "
            f"gedeckt, {not_open} Ansprueche auf nicht offene, {rejected} verworfen "
            f"(Angebot {len(hits)})"
        )
    _assert_covered_not_open(artifact)
    return artifact


def carry_sources(artifact: dict, previous: dict | None) -> dict:
    """Schreibt die Quellen der vorigen Blase fort.

    Der Prompt sieht von der vorigen Blase die Sache, nicht die Buchfuehrung
    — `quellen` geht nicht mit (`_derive`). Damit eine Deckung aus dem
    Gedaechtnis ihre Herkunft nicht nach einem Turn verliert, erbt ein
    Objekt gleichen Namens die Quelle jeder Eigenschaft, die bei ihm noch
    gedeckt ist und keine neue Quelle bekam.

    Vorbedingung: `artifact` nach `apply_memory_coverage`; `previous` ein
        Artefakt oder None.
    Nachbedingung: Keine Quelle an einer Eigenschaft, die nicht gedeckt ist;
        neue Quellen bleiben unberuehrt.
    Fehlerfaelle: keine — ohne Vorgaenger oder ohne Quellen aendert sich nichts.
    """
    if not previous:
        return artifact
    vorige: dict[str, dict] = {
        _normalized(o.get("name", "")): o.get("quellen") or {}
        for o in previous.get("objekte") or []
        if isinstance(o, dict)
    }
    for objekt in artifact.get("objekte") or []:
        if not objekt.get("akut"):
            continue
        geerbt: dict = vorige.get(_normalized(objekt.get("name", "")), {})
        if not geerbt:
            continue
        gedeckt: dict[str, str] = {
            _normalized(k): str(k) for k in (objekt.get("gedeckt") or {})
        }
        quellen: dict = objekt.setdefault("quellen", {})
        for eigenschaft, quelle in geerbt.items():
            schluessel: str = _normalized(eigenschaft)
            if schluessel in gedeckt and gedeckt[schluessel] not in quellen:
                quellen[gedeckt[schluessel]] = dict(quelle)
    return artifact
