"""Der Erinnerungsanker — Fakten und Erinnerungen der gebundenen Personen im Kontext.

Sitzt zwischen der Sachlage und dem Router. Die Sachlage legt die gebundenen
Entitaeten ihrer akuten Objekte in den Kanal `objekt_entitaeten`; der Anker
liest je Entitaet die Mappe (`load_mappe`) und sucht mit allen Entitaeten im
Langzeitgedaechtnis des Paares (`knoten_zu_entitaeten`). Die Fakten stehen
danach als Eintraege der Quelle `fakten` im Gedaechtnis, die Erinnerungen
hinter der Resonanz des Enrichers — entdoppelt nach dem Knoten, gekappt,
angehaengt. Den Gedaechtnisblock rendert er fuer beide Leser neu, mit
demselben Formatter wie der Reducer.

**Gesucht wird immer, auch ohne Fakten:** Eine Person kann Erinnerungen
tragen, ohne dass ein Fakt zu ihr gespeichert ist. Ohne gebundene Entitaet,
oder wenn nichts Neues dazukommt, gehen die vier Werte unveraendert zurueck,
und der Prompt bleibt zeichengleich.

Je Turn genau ein Protokolleintrag `berechnung`, auf jedem Weg, beim
Uebersprung mit Grund.
"""

import logging

from config import ANKER_MAX_ENTITAETEN, ANKER_MAX_ERINNERUNGEN
from graph.context_entry import ContextEntry
from graph.format import format_memory_entries
from graph.format.memory_context import LESER_ANALYSE, LESER_VERFASSER, QUELLE_FAKTEN
from graph.state import pipeline_quelle, zustand_verifizieren
from memory.fakten_mappe import Mappe, load_mappe
from memory.lzg_knoten import knoten_zu_entitaeten
from memory.pipeline_log import log_berechnung, span_end, span_start
from memory.repositories.fakten_repository import EntityNotFoundError

logger = logging.getLogger("ki_server.erinnerungsanker")

#: Der Name des Knotens im Graphen und im Protokoll.
NODE_NAME: str = "erinnerungsanker"

# Die Felder, die JEDER Rueckkehrpfad dieses Knotens setzt — auch der
# Uebersprung, dann mit den Werten, die er vorfand.
WRITES = frozenset({
    "memory_entries", "memory_context", "memory_context_verfasser", "lzg_resonanz",
})


def erinnerungsanker(state: dict, postgres_url: str) -> dict:
    """Der Knoten: ergaenzt Fakten und Erinnerungen der gebundenen Entitaeten.

    Klammert die Rechnung in `span_start`/`span_end` und schreibt genau einen
    Protokolleintrag `berechnung` — auf jedem Weg, auch beim Uebersprung.

    Vorbedingung: der Zustand hinter dem Reducer und der Sachlage
        (`memory_entries`, `memory_context`, `memory_context_verfasser`,
        `objekt_entitaeten`); `postgres_url` nicht leer.
    Nachbedingung: die vier Felder aus `WRITES`, gegen den Zustandstyp
        gehalten; ohne etwas Neues unveraendert.
    Fehlerfaelle: eine leere URL wirft `ValueError`; Fehler in der Form des
        Zustands werfen (siehe `compute_anchor`).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not postgres_url:
        msg: str = "Erinnerungsanker: ohne Datenbank-URL"
        raise ValueError(msg)
    turn_id: str = state.get("turn_id", "unbekannt")
    user_id: str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")
    source: str = pipeline_quelle(state)
    span_id = span_start(
        turn_id=turn_id, node=NODE_NAME, quelle=source,
        user_id=user_id, character_id=character_id,
    )

    # ── Verarbeitung ────────────────────────────
    result, protocol = compute_anchor(state, postgres_url)
    log_berechnung(
        turn_id=turn_id, node=NODE_NAME, quelle=NODE_NAME, inhalt=protocol,
        span_id=span_id, user_id=user_id, character_id=character_id,
    )
    span_end(
        turn_id=turn_id, node=NODE_NAME, quelle=source, span_id=span_id,
        inhalt={"zweig": protocol["zweig"], "neu": protocol["neu"]},
        user_id=user_id, character_id=character_id,
    )

    # ── Ausgabe-Verifikation ────────────────────
    return zustand_verifizieren(result, NODE_NAME, WRITES)


def compute_anchor(state: dict, postgres_url: str) -> tuple[dict, dict]:
    """Die Rechnung des Ankers, ohne Protokoll: das Ergebnis und dessen Protokollinhalt.

    Vorbedingung: wie `erinnerungsanker`.
    Nachbedingung: (Ergebnis, Protokoll). Das Ergebnis traegt die vier Felder
        aus `WRITES`; ohne gebundene Entitaet oder ohne etwas Neues sind es
        die vorgefundenen Werte. Das Protokoll nennt den Zweig, beim
        Uebersprung den Grund, dazu Entitaeten, Mappen, `unbekannt`,
        `ausfall`, gefunden/neu, `knoten_neu_ids` und die Laengen vorher und
        nachher. `gefunden` ist `None`, wenn nicht gesucht wurde oder die
        Suche ausfiel — nie `0`.
    Fehlerfaelle: ein Feld des Gedaechtnisses im falschen Typ oder ein
        Element des Kanals ohne Name und ganzzahlige Kennung wirft
        (`TypeError`/`ValueError`): Das waere ein Fehler im Bau, nicht in
        den Daten. Ein fehlender oder unlesbarer Kanal und ein unvollstaendiges
        Paar sind laut (`ERROR`), uebersprungen. Ein Ausfall der Mappe oder
        der Suche ist laut und gezaehlt; der Turn laeuft weiter. Eine neue
        Erinnerung oder ein Block der Fakten, der im gerenderten Text fehlt,
        wirft `RuntimeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    unchanged: dict = {field: state.get(field) for field in WRITES}
    reason: str | None = _skip_reason(state)
    protocol: dict = _new_protocol(state)
    if reason is not None:
        protocol["grund"] = reason
        return unchanged, protocol

    # ── Verarbeitung ────────────────────────────
    user_id: str = state["user_id"]
    character_id: str = state["character_id"]
    channel: list[dict] = state["objekt_entitaeten"]
    entities: list[dict] = channel[:ANKER_MAX_ENTITAETEN]
    protocol["entitaeten"] = [dict(e) for e in entities]
    protocol["entitaeten_weggelassen"] = len(channel) - len(entities)
    counters: dict[str, int] = {"unbekannt": 0, "ausfall": 0}
    facts, searched_ids, protocol["mappen"] = _read_fact_maps(
        postgres_url, user_id, character_id, entities, counters,
    )
    resonanz: dict | None = state.get("lzg_resonanz")
    previous: list[dict] = list((resonanz or {}).get("erinnerungen") or [])
    nova_emotion: str = _nova_emotion(state)
    found: list[dict] | None = None
    if searched_ids:
        protocol["gesucht"] = True
        found = knoten_zu_entitaeten(
            postgres_url, user_id, character_id, searched_ids, nova_emotion,
            ANKER_MAX_ERINNERUNGEN + len(previous),
        )
    if searched_ids and found is None:
        counters["ausfall"] += 1
        logger.error(
            f"Erinnerungsanker: Suche zu {searched_ids} ausgefallen — ohne neue Erinnerungen"
        )
    added: list[dict] = new_memories(found or [], previous, ANKER_MAX_ERINNERUNGEN)
    protocol.update(
        counters, gefunden=None if found is None else len(found), neu=len(added),
        knoten_neu_ids=[e["knoten_id"] for e in added],
    )
    if not facts and not added:
        protocol["zweig"] = "nichts_neu"
        return unchanged, protocol
    extended: dict = _extend_resonanz(resonanz, previous, added, nova_emotion)
    entries: list[ContextEntry] = list(state["memory_entries"]) + facts
    result: dict = {
        "memory_entries": entries,
        "memory_context": format_memory_entries(
            entries, lzg_resonanz=extended, leser=LESER_ANALYSE),
        "memory_context_verfasser": format_memory_entries(
            entries, lzg_resonanz=extended, leser=LESER_VERFASSER),
        "lzg_resonanz": extended,
    }
    protocol.update(
        zweig="ergaenzt", fakten_eintraege=len(facts),
        laenge_nachher=len(result["memory_context"]),
        laenge_verfasser_nachher=len(result["memory_context_verfasser"]),
    )

    # ── Ausgabe-Verifikation ────────────────────
    _check_rendered(result["memory_context"], facts, added)
    _check_rendered(result["memory_context_verfasser"], facts, added)
    return result, protocol


def _new_protocol(state: dict) -> dict:
    """Der Protokollinhalt eines Laufs vor der Rechnung — der Stand des Uebersprungs.

    Ohne Ausgabe-Verifikation: Das Ergebnis ist ein Literal, und jede
    Nachbedingung gilt per Konstruktion — eine Pruefung dagegen koennte nicht
    anschlagen.

    Vorbedingung: beide Kontexte des Zustands sind Text (`_skip_reason` hat
        die Typen geprueft).
    Nachbedingung: alle Schluessel des Protokolls, `zweig` `uebersprungen`,
        `gefunden` `None` (nicht gesucht), die Laengen vorher gleich nachher.
    Fehlerfaelle: ein Kontext, der kein Text ist, wirft `TypeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    context: object = state.get("memory_context")
    context_verfasser: object = state.get("memory_context_verfasser")
    if not isinstance(context, str) or not isinstance(context_verfasser, str):
        msg: str = "Erinnerungsanker: Protokoll ohne Kontexte als Text"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    return {
        "zweig": "uebersprungen", "grund": None,
        "entitaeten": [], "entitaeten_weggelassen": 0, "mappen": [],
        "unbekannt": 0, "ausfall": 0, "gesucht": False, "gefunden": None,
        "neu": 0, "knoten_neu_ids": [], "fakten_eintraege": 0,
        "laenge_vorher": len(context), "laenge_nachher": len(context),
        "laenge_verfasser_vorher": len(context_verfasser),
        "laenge_verfasser_nachher": len(context_verfasser),
    }


def _skip_reason(state: dict) -> str | None:
    """Prueft den Eingang; der Grund, aus dem der Anker nichts tut, oder None.

    Vorbedingung: keine.
    Nachbedingung: None, wenn ein vollstaendiges Paar und mindestens eine
        gebundene Entitaet im Kanal stehen und jedes Element die Form
        `{name, entitaet_id}` hat; sonst der Grund in Worten.
    Fehlerfaelle: `memory_entries` keine Liste, `memory_context` oder
        `memory_context_verfasser` kein Text, `lzg_resonanz` weder None noch
        Abbildung, der Kanal weder None noch Liste → `TypeError`; ein Element
        ohne Namen oder ganzzahlige Kennung → `ValueError`. Ein fehlender oder
        unlesbarer Kanal und ein unvollstaendiges Paar sind ein Grund und
        stehen als `ERROR` im Log; ein leerer Kanal ist ein Grund ohne Fehler.
    """
    # ── Eingabe-Validierung ─────────────────────
    _check_memory_types(state)

    # ── Verarbeitung ────────────────────────────
    if "objekt_entitaeten" not in state:
        logger.error("Erinnerungsanker: der Kanal objekt_entitaeten fehlt — uebersprungen")
        return "Kanal fehlt"
    channel: object = state["objekt_entitaeten"]
    if channel is None:
        logger.error("Erinnerungsanker: Bindungen nicht lesbar (Kanal None) — uebersprungen")
        return "Kanal nicht lesbar"
    if not isinstance(channel, list):
        msg: str = f"Erinnerungsanker: objekt_entitaeten ist {type(channel).__name__}"
        raise TypeError(msg)
    if not channel:
        return "keine gebundene Entitaet"
    if not state.get("user_id") or not state.get("character_id"):
        logger.error("Erinnerungsanker: ohne vollstaendiges Paar — uebersprungen")
        return "ohne vollstaendiges Paar"

    # ── Ausgabe-Verifikation ────────────────────
    defective: list = [e for e in channel if not _is_channel_element(e)]
    if defective:
        msg = f"Erinnerungsanker: Elemente des Kanals ohne Name oder Kennung {defective!r}"
        raise ValueError(msg)
    return None


def _check_memory_types(state: dict) -> None:
    """Prueft die Typen der vier Felder, die der Anker liest und zurueckgibt.

    Vorbedingung: keine.
    Nachbedingung: nichts zurueck; `memory_entries` ist eine Liste, beide
        Kontexte sind Text, `lzg_resonanz` ist None oder eine Abbildung.
    Fehlerfaelle: jedes andere Feld wirft `TypeError` — ein Fehler im Bau,
        nicht in den Daten.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(state.get("memory_entries"), list):
        msg: str = f"Erinnerungsanker: memory_entries ist {type(state.get('memory_entries'))}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    for field in ("memory_context", "memory_context_verfasser"):
        if not isinstance(state.get(field), str):
            msg = f"Erinnerungsanker: {field} ist {type(state.get(field)).__name__}, kein Text"
            raise TypeError(msg)

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(state.get("lzg_resonanz"), dict | None):
        msg = f"Erinnerungsanker: lzg_resonanz ist {type(state.get('lzg_resonanz')).__name__}"
        raise TypeError(msg)


def _is_channel_element(element: object) -> bool:
    """Ob ein Element des Kanals die Form `{name, entitaet_id}` hat.

    Ohne Ausgabe-Verifikation: Die Antwort ist das Urteil selbst, ein
    Wahrheitswert per Konstruktion.

    Vorbedingung: keine.
    Nachbedingung: True genau fuer eine Abbildung mit nicht leerem Namen und
        ganzzahliger Kennung ab 1 (`bool` zaehlt nicht als Zahl).
    Fehlerfaelle: keine — die Antwort ist das Urteil.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(element, dict):
        return False

    # ── Verarbeitung ────────────────────────────
    entity_id: object = element.get("entitaet_id")
    name: object = element.get("name")
    integral: bool = isinstance(entity_id, int) and not isinstance(entity_id, bool)
    return integral and entity_id >= 1 and isinstance(name, str) and bool(name.strip())


def _read_fact_maps(
    postgres_url: str, user_id: str, character_id: str,
    entities: list[dict], counters: dict[str, int],
) -> tuple[list[ContextEntry], list[int], list[dict]]:
    """Je Entitaet die Mappe; die Eintraege der Fakten und die Entitaeten fuer die Suche.

    Ohne Ausgabe-Verifikation: Jede Entitaet legt in jedem Zweig der Schleife
    genau eine Protokollzeile an, und die Bilanz unten gilt per Konstruktion.
    Was von aussen kommt, prueft `facts_entry` an der Mappe.

    Vorbedingung: das Paar ist vollstaendig; `entities` gegen
        `_is_channel_element` gehalten; `counters` traegt `unbekannt` und
        `ausfall`.
    Nachbedingung: (Eintraege `fakten`, je nicht leerer Mappe einer, in der
        Ordnung des Kanals; die Kennungen, die gesucht werden; je Entitaet
        eine Protokollzeile). Eine unbekannte Entitaet fehlt in der Suche, eine
        ausgefallene Mappe nicht.
    Fehlerfaelle: `EntityNotFoundError` heisst *unbekannt* — die Bindung
        zeigt auf eine Entitaet, die es im Paar nicht gibt —, laut, gezaehlt;
        jede andere Ausnahme beim Lesen oder Aufbereiten der Mappe ist ein
        Ausfall, laut mit Stacktrace, gezaehlt, und gesucht wird trotzdem.
        Zaehler ohne `unbekannt` oder `ausfall` werfen `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not {"unbekannt", "ausfall"} <= set(counters):
        msg: str = f"Erinnerungsanker: Zaehler unvollstaendig {sorted(counters)}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    facts: list[ContextEntry] = []
    searched_ids: list[int] = []
    rows: list[dict] = []
    for element in entities:
        entity_id: int = element["entitaet_id"]
        try:
            mappe: Mappe = load_mappe(postgres_url, user_id, character_id, entity_id)
            entry: ContextEntry | None = facts_entry(mappe, entity_id)
        except EntityNotFoundError:
            counters["unbekannt"] += 1
            # Ein erwarteter Fall der Daten, kein Programmfehler: ohne Stacktrace.
            logger.error(  # noqa: TRY400
                f"Erinnerungsanker: gebundene Entitaet {entity_id} ({element['name']}) "
                f"unbekannt — ohne Mappe und ohne Suche"
            )
            rows.append({"entitaet_id": entity_id, "zustand": "unbekannt"})
            continue
        except Exception:  # noqa: BLE001 — der Turn geht vor, gesucht wird trotzdem
            counters["ausfall"] += 1
            logger.exception(
                f"Erinnerungsanker: Mappe der Entitaet {entity_id} ausgefallen "
                f"— gesucht wird trotzdem"
            )
            searched_ids.append(entity_id)
            rows.append({"entitaet_id": entity_id, "zustand": "ausfall"})
            continue
        searched_ids.append(entity_id)
        rows.append({
            "entitaet_id": entity_id, "zustand": "gelesen", "fakten": len(mappe.entries),
            "zeichen": mappe.chars, "gekuerzt": mappe.truncated,
        })
        if entry is not None:
            facts.append(entry)
    return facts, searched_ids, rows


def facts_entry(mappe: Mappe, entity_id: int) -> ContextEntry | None:
    """Der Eintrag der Quelle `fakten` fuer eine Mappe — None, wenn sie leer ist.

    Je Fakt eine Zeile `- <Text>`, mit `(<seit>)`, wenn der Fakt ab einem
    Ereignis gilt, und einer Zeile `  vorher: <abgeloester Wert>` darunter.
    Ist die Mappe gekuerzt, sagt eine letzte Zeile das — sonst behauptete der
    Block, er trage alles, was zur Person gespeichert ist.

    Vorbedingung: `mappe` aus `load_mappe` fuer die Entitaet `entity_id`.
    Nachbedingung: None bei leerer Mappe; sonst `subtyp` der Name der
        Entitaet, `inhalt` mindestens eine Zeile je Fakt, `gewicht` die
        groesste Staerke der Fakten, in der Spanne 0 bis 1 von
        `staerke_decay` (exp(−Rate · Tage), hoechstens 1 am Tag der
        Beruehrung), `meta` Kennung, Fakt-IDs und `gekuerzt`.
    Fehlerfaelle: eine Mappe einer anderen Entitaet, ohne Namen oder mit
        einem leeren Fakt wirft `ValueError`, ebenso ein `gewicht` ausserhalb
        der Spanne 0 bis 1 (oder NaN) — das waere eine Staerke, die der
        Verfall nicht erzeugt, und sie ordnete den Block falsch ein. Der
        Aufrufer zaehlt jeden dieser Faelle als Ausfall.
    """
    # ── Eingabe-Validierung ─────────────────────
    if mappe.entity_id != entity_id or not mappe.entity_name.strip():
        msg: str = (
            f"Erinnerungsanker: Mappe {mappe.entity_id} ({mappe.entity_name!r}) "
            f"fuer Entitaet {entity_id}"
        )
        raise ValueError(msg)
    if not mappe.entries:
        return None
    empty: list[int] = [e.fact_id for e in mappe.entries if not e.text.strip()]
    if empty:
        msg = f"Erinnerungsanker: Fakten ohne Text {empty} in der Mappe {entity_id}"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    lines: list[str] = []
    for fact in mappe.entries:
        since: str = f" ({fact.since})" if fact.since else ""
        lines.append(f"- {fact.text.strip()}{since}")
        if fact.previous:
            lines.append(f"  vorher: {fact.previous}")
    if mappe.truncated:
        lines.append("- (weitere Fakten hier nicht aufgefuehrt)")
    entry: ContextEntry = ContextEntry(
        quelle=QUELLE_FAKTEN, subtyp=mappe.entity_name.strip(), inhalt="\n".join(lines),
        gewicht=max(e.strength for e in mappe.entries),
        meta={
            "entitaet_id": entity_id, "fakt_ids": [e.fact_id for e in mappe.entries],
            "gekuerzt": mappe.truncated,
        },
    )

    # ── Ausgabe-Verifikation ────────────────────
    # Spanne laut Nachbedingung: 0 bis 1; NaN faellt durch den Vergleich.
    if not 0.0 <= entry["gewicht"] <= 1.0:
        msg = (
            f"Erinnerungsanker: Gewicht {entry['gewicht']!r} der Mappe {entity_id} "
            f"ausserhalb der Spanne 0–1"
        )
        raise ValueError(msg)
    return entry


def new_memories(found: list[dict], previous: list[dict], max_new: int) -> list[dict]:
    """Die Erinnerungen der Suche, die die Resonanz noch nicht traegt — gekappt, fortgezaehlt.

    Entdoppelt nach `knoten_id` gegen die Resonanz und untereinander, in der
    Ordnung der Suche (die staerksten zuerst); hoechstens `max_new`. `rang`
    zaehlt hinter der Resonanz weiter.

    Ohne Ausgabe-Verifikation: Kappung und Entdoppeln stehen in der Schleife
    selbst; eine Pruefung des Ergebnisses gegen dieselbe Menge, aus der es
    gebaut ist, koennte nicht anschlagen. Bezeugt sind beide in
    `CappedAndDeduplicatedTest`.

    Vorbedingung: jede Erinnerung in `found` und `previous` traegt
        `knoten_id`; `max_new` ist eine ganze Zahl ab 1.
    Nachbedingung: hoechstens `max_new` Kopien der Treffer, keine
        `knoten_id` doppelt oder in `previous`, `rang` von
        `len(previous) + 1` an.
    Fehlerfaelle: eine Erinnerung ohne `knoten_id` oder eine Grenze unter 1
        wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if isinstance(max_new, bool) or not isinstance(max_new, int) or max_new < 1:
        msg: str = f"Erinnerungsanker: Grenze {max_new!r} ist keine ganze Zahl ab 1"
        raise ValueError(msg)
    without_id: list[dict] = [e for e in [*previous, *found] if e.get("knoten_id") is None]
    if without_id:
        msg = f"Erinnerungsanker: {len(without_id)} Erinnerungen ohne knoten_id"
        raise ValueError(msg)
    seen: set = {e["knoten_id"] for e in previous}

    # ── Verarbeitung ────────────────────────────
    added: list[dict] = []
    for hit in found:
        if len(added) == max_new:
            break
        if hit["knoten_id"] in seen:
            continue
        seen.add(hit["knoten_id"])
        added.append({**hit, "rang": len(previous) + len(added) + 1})
    return added


def _extend_resonanz(
    resonanz: dict | None, previous: list[dict], added: list[dict], nova_emotion: str,
) -> dict:
    """Die Resonanz mit den neuen Erinnerungen hinten angehaengt.

    Ohne Resonanz legt der Anker den Rahmen an, den der Enricher anlegt —
    mit den Werten dieses Laufs: kein Anker ueber das Embedding
    (`anker_anzahl` 0), ein Sprung (Schale 1), kein Cluster.

    Ohne Ausgabe-Verifikation: Das Ergebnis ist `previous + added` per
    Konstruktion. Geprueft wird stattdessen der Eingang — dass `previous`
    die Erinnerungen von `resonanz` sind; sonst haengte der Anker an eine
    andere Liste an, als die Resonanz traegt.

    Vorbedingung: `previous` sind die Erinnerungen von `resonanz` (ohne
        Resonanz leer); `added` aus `new_memories`.
    Nachbedingung: eine neue Abbildung — der Rahmen von `resonanz` oder der
        angelegte, `erinnerungen` == `previous + added` in dieser Ordnung.
        Die Eingabe bleibt unveraendert.
    Fehlerfaelle: `previous`, deren Knoten nicht die der Resonanz sind, in
        derselben Ordnung, werfen `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    carried: list = [e.get("knoten_id") for e in (resonanz or {}).get("erinnerungen") or []]
    if carried != [e.get("knoten_id") for e in previous]:
        msg: str = (
            f"Erinnerungsanker: Erinnerungen {[e.get('knoten_id') for e in previous]} "
            f"sind nicht die der Resonanz {carried}"
        )
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    frame: dict = dict(resonanz) if resonanz is not None else {
        "anker_anzahl": 0, "sprung_tiefe": 1, "cluster": None, "nova_sektor": nova_emotion,
    }
    return {**frame, "erinnerungen": [*previous, *added]}


def _nova_emotion(state: dict) -> str:
    """Novas dominante Emotion dieses Turns — dieselbe Quelle wie im Enricher.

    Vorbedingung: keine.
    Nachbedingung: die Emotion des ersten Eintrags von
        `nova_emotions_verlauf` (der staerkste) als Text, oder leer bei leerem
        Verlauf — leer heisst *ungefaerbt* in `knoten_zu_entitaeten`, wie im
        Enricher.
    Fehlerfaelle: ein erster Eintrag, der keine Abbildung ist, oder eine
        Emotion, die kein Text ist (auch eine fehlende), wirft `TypeError` —
        der Enricher liest dieselbe Stelle ohne Rueckfall; ein leerer Text
        faerbte die Suche still nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    history: list = state.get("nova_emotions_verlauf") or []
    if not history:
        return ""
    if not isinstance(history[0], dict):
        msg: str = f"Erinnerungsanker: Emotionsverlauf beginnt mit {type(history[0]).__name__}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    emotion: object = history[0].get("emotion")

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(emotion, str):
        msg = f"Erinnerungsanker: fuehrende Emotion ist {type(emotion).__name__}, kein Text"
        raise TypeError(msg)
    return emotion


def _check_rendered(text: str, facts: list[ContextEntry], added: list[dict]) -> None:
    """Prueft, dass jeder Block der Fakten und jede neue Erinnerung im Text steht.

    Vorbedingung: `text` aus `format_memory_entries` mit diesen Eintraegen
        und dieser Resonanz.
    Nachbedingung: nichts zurueck; jede Kopfzeile `[Fakten zu <Name>]` und
        jeder Inhalt einer neuen Erinnerung (in Anfuehrungszeichen) steht im
        Text.
    Fehlerfaelle: ein fehlender Block oder eine fehlende Erinnerung wirft
        `RuntimeError` — der Formatter haette sie still verworfen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        msg: str = f"Erinnerungsanker: gerenderter Kontext ist {type(text).__name__}"
        raise TypeError(msg)

    # ── Verarbeitung ────────────────────────────
    missing: list[str] = [
        f"Fakten zu {e['subtyp']}" for e in facts if f"[Fakten zu {e['subtyp']}]" not in text
    ] + [
        f"Knoten {e['knoten_id']}" for e in added
        if f'"{(e.get("inhalt") or "").strip()}"' not in text
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if missing:
        msg = f"Erinnerungsanker: im gerenderten Kontext fehlen {missing}"
        raise RuntimeError(msg)
