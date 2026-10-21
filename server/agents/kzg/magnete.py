"""Magnet-Aufloesung — Roh-Strings aus Salience zu Entitaets-IDs und Timeline-ID.

Dieser Node sitzt im KzgAgent-Subgraph zwischen `schwelle_pruefen` und
`verdichten`. Er laeuft nur fuer Eintraege oberhalb der Salienz-Schwelle.

Eingabe (aus state["parameter"]["salienz_obj"]):
  - entitaeten_roh: list[str]  -- Eigennamen, Salience-Extraktion
  - zeitausdruck_roh: str      -- Zeitausdruck, Salience-Extraktion

Eingabe (aus state["kontext"]):
  - user_id, turn_id
  - timeline_id (optional Clipboard): vom TimelineAgent in diesem Turn
    gesetzte ID. Wenn vorhanden, wird sie uebernommen statt einen
    eigenen Erinnerungs-Anker anzulegen.

Ausgabe (in state["parameter"]):
  - entitaet_ids: list[int]
  - timeline_id:  int | None

EVA-Disziplin: Eingabe-Validierung (leere Roh-Felder -> leeres Ergebnis,
kein Fehler), Verarbeitung (Resolve + ggf. Create), Ausgabe-Logging.

Ausfall: Die Auflösung wirft bei einem Fehler der Datenbank oder des
Embeddings. Hier endet er, je Name: Der Name bekommt keine ID, es wird keine
Entität angelegt, der Ausfall steht als `error` und als Eintrag `fehler` im
Pipeline-Log; die übrigen Namen werden aufgelöst, und der Eintrag des
Kurzzeitgedächtnisses wird mit den Magneten geschrieben, die stehen.

Spezifikation: docs/novaberg-memory-synapsen_k.md §13.5.
"""

import logging

from agents.base import AgentState
from config import POSTGRES_URL, redis_client
from memory.pipeline_log import log_fehler
from memory.repositories.timeline_repository import TimelineRepository
from memory.services.entity_resolution import EntityResolutionService, ResolvedEntity
from utils.zeitparser import ZeitVektor, zeit_parsen_vektor

logger = logging.getLogger("ki_server.agents.kzg.magnete")


# Konvention: KZG-Schreibpfad legt zeitbezogene Anker (keine bindenden Termine)
# als event_type "erinnerungs_anker" in der Timeline ab. Klasse: Bezug
# nach docs/novaberg-convention-magneten.md §5 (Flags False/False/False).
EVENT_TYPE_ERINNERUNGS_ANKER: str = "erinnerungs_anker"


def magnete_aufloesen(state: AgentState) -> dict:
    """Resolviert Salience-Roh-Strings zu Magnet-IDs.

    Vorbedingung: state["parameter"] enthaelt 'salienz_obj' mit Roh-Feldern.
    Nachbedingung: state["parameter"] traegt 'entitaet_ids' (list[int])
    und 'timeline_id' (int | None).
    Fehlerfaelle: Salience hat keine Roh-Erkennungen geliefert -> leeres
    Ergebnis, kein Abbruch (Magnete sind optional gemaess
    convention-magneten.md §3). Ein Ausfall der Auflösung verlässt den
    Knoten nicht: Er kostet nur den Namen, an dem er auftritt, und der
    Schritt nennt ihn unter 'ausgefallen'.
    """
    # ── Eingabe-Validierung ─────────────────────
    salienz_obj: dict = state["parameter"].get("salienz_obj", {})
    user_id:     str  = state["kontext"].get("user_id", "")
    if not user_id:
        logger.error("magnete_aufloesen: user_id fehlt im kontext — verworfen")
        return {
            "parameter": {
                **state["parameter"],
                "entitaet_ids": [],
                "timeline_id":  None,
            },
            "schritte": state["schritte"] + [
                {"node": "magnete_aufloesen", "ergebnis": "fehler",
                 "grund": "user_id fehlt"}
            ],
        }

    entitaeten_roh:   list[str] = salienz_obj.get("entitaeten_roh", []) or []
    zeitausdruck_roh: str       = salienz_obj.get("zeitausdruck_roh", "") or ""
    clipboard_tlid:   int | None = state["kontext"].get("timeline_id")

    turn_id: str = state["kontext"].get("turn_id", "")

    # ── Verarbeitung: Entitaeten ───────────────
    entitaet_ids, ausgefallen = _entitaeten_aufloesen(
        roh_namen = entitaeten_roh,
        user_id   = user_id,
        turn_id   = turn_id,
    )

    # ── Verarbeitung: Timeline ─────────────────
    timeline_id: int | None = _timeline_aufloesen(
        clipboard_id     = clipboard_tlid,
        zeitausdruck_roh = zeitausdruck_roh,
        user_id          = user_id,
    )

    # ── Ausgabe-Logging ─────────────────────────
    logger.info(
        f"magnete_aufloesen: entitaet_ids={entitaet_ids}, "
        f"timeline_id={timeline_id}, "
        f"clipboard_uebernommen={clipboard_tlid is not None and timeline_id == clipboard_tlid}, "
        f"ausgefallen={ausgefallen}"
    )

    return {
        "parameter": {
            **state["parameter"],
            "entitaet_ids": entitaet_ids,
            "timeline_id":  timeline_id,
        },
        "schritte": state["schritte"] + [
            {"node":         "magnete_aufloesen",
             "ergebnis":     "abgeschlossen",
             "entitaet_ids": entitaet_ids,
             "timeline_id":  timeline_id,
             "ausgefallen":  ausgefallen}
        ],
    }


def _entitaeten_aufloesen(
    roh_namen: list[str],
    user_id:   str,
    turn_id:   str,
) -> tuple[list[int], list[str]]:
    """Loest eine Liste von Roh-Eigennamen zu Entitaets-IDs auf.

    Folgt dem Zwei-Schritt-Pattern der Entity Resolution, je Name:
    erst resolve_batch (Lookup), dann create_new_entity, wenn der Name
    `ist_neu=True` und `ist_referenz=True` ist. Disambiguierungs-Faelle
    (`braucht_klaerung=True`) werden im nicht-interaktiven KZG-Pfad
    uebersprungen (info) — siehe convention-magneten.md.

    Je Name, nicht je Liste, weil die Auflösung bei einem Ausfall wirft:
    Ein Aufruf für alle Namen verlöre mit dem einen Ausfall auch die übrigen.

    Vorbedingung: user_id ist nicht leer (geprüft im Knoten).
    Nachbedingung: Die erste Liste trägt die IDs der aufgelösten oder neu
        angelegten Namen in der Reihenfolge der Eingabe; die zweite nennt die
        Namen, deren Suche oder Anlegen ausfiel — für sie wurde keine Entität
        angelegt, und je Name stehen eine Zeile `error` und ein Eintrag
        `fehler` im Pipeline-Log.
    Fehlerfälle: ValueError bei leerer user_id. Ein Fehler der Auflösung
        oder des Anlegens verlässt die Funktion nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not roh_namen:
        return [], []
    if not user_id:
        raise ValueError("_entitaeten_aufloesen: user_id ist leer")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    entitaet_ids: list[int] = []
    ausgefallen:  list[str] = []
    for name in roh_namen:
        stufe: str = "suche"
        try:
            ent: ResolvedEntity | None = _namen_suchen(name, user_id, turn_id)
            if ent is not None and ent.ist_neu and ent.ist_referenz:
                stufe = "anlegen"
                ent.bekannte_id = EntityResolutionService.create_new_entity(
                    postgres_url = POSTGRES_URL,
                    user_id      = user_id,
                    name         = ent.name,
                    typ          = ent.typ,
                )
                logger.info(
                    f"magnete_aufloesen: Neue Entitaet '{ent.name}' "
                    f"angelegt (id={ent.bekannte_id})"
                )
        except Exception as fehler:  # noqa: BLE001 — ein Ausfall kostet nur diesen Namen
            _ausfall_melden(name, stufe, fehler, user_id, turn_id)
            ausgefallen.append(name)
            continue

        if ent is not None and ent.bekannte_id is not None:
            entitaet_ids.append(ent.bekannte_id)

    # ── Ausgabe-Verifikation ────────────────────
    if len(entitaet_ids) + len(ausgefallen) > len(roh_namen):
        raise RuntimeError(  # noqa: TRY003
            f"_entitaeten_aufloesen: {len(entitaet_ids)} IDs und {len(ausgefallen)} "
            f"Ausfälle aus {len(roh_namen)} Namen"
        )
    return entitaet_ids, ausgefallen


def _namen_suchen(
    name:    str,
    user_id: str,
    turn_id: str,
) -> ResolvedEntity | None:
    """Sucht einen einzelnen Namen über resolve_batch.

    Vorbedingung: user_id ist nicht leer.
    Nachbedingung: das eine Ergebnis der Auflösung, oder None, wenn der Name
        leer ist (resolve_batch überspringt ihn) oder mehrdeutig (im
        nicht-interaktiven KZG-Pfad ignoriert, info).
    Fehlerfälle: Jeder Fehler der Auflösung geht durch — der Aufrufer fängt
        je Name. RuntimeError, wenn die Auflösung für einen Namen mehr als ein
        Ergebnis liefert.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        raise ValueError("_namen_suchen: user_id ist leer")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    resolution = EntityResolutionService.resolve_batch(
        entitaeten   = [{"name": name, "typ": "sonstiges", "ist_referenz": True}],
        postgres_url = POSTGRES_URL,
        user_id      = user_id,
        redis_client = redis_client,
        turn_id      = turn_id or None,
    )

    # ── Ausgabe-Verifikation ────────────────────
    if len(resolution.aufgeloest) > 1:
        raise RuntimeError(  # noqa: TRY003
            f"_namen_suchen: {len(resolution.aufgeloest)} Ergebnisse für '{name}', "
            f"erwartet höchstens 1"
        )
    if not resolution.aufgeloest:
        return None
    ent: ResolvedEntity = resolution.aufgeloest[0]
    if ent.braucht_klärung:
        logger.info(
            f"magnete_aufloesen: '{name}' mehrdeutig "
            f"({len(ent.kandidaten)} Kandidaten) — im KZG-Pfad ignoriert (nicht-interaktiv)"
        )
        return None
    return ent


def _ausfall_melden(
    name:    str,
    stufe:   str,
    fehler:  Exception,
    user_id: str,
    turn_id: str,
) -> None:
    """Meldet den Ausfall der Auflösung eines Namens laut.

    Vorbedingung: stufe ist 'suche' oder 'anlegen'.
    Nachbedingung: eine Zeile `error` mit Name, Stufe und Fehlertyp und ein
        Eintrag `fehler` im Pipeline-Log (node 'magnete_aufloesen'), der über
        die turn_id neben dem Eintrag des Kurzzeitgedächtnisses steht.
    Fehlerfälle: ValueError bei unbekannter Stufe.
    """
    # ── Eingabe-Validierung ─────────────────────
    if stufe not in ("suche", "anlegen"):
        raise ValueError(f"_ausfall_melden: unbekannte Stufe {stufe!r}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    beschreibung: str = f"{type(fehler).__name__}: {fehler}"
    logger.error(
        "magnete_aufloesen: Auflösung von '%s' ausgefallen (Stufe %s) — "
        "kein Magnet, keine Entität: %s",
        name, stufe, beschreibung,
    )
    log_fehler(
        turn_id = turn_id,
        node    = "magnete_aufloesen",
        quelle  = user_id,
        inhalt  = {"name": name, "stufe": stufe, "fehler": beschreibung},
    )


def _timeline_aufloesen(
    clipboard_id:     int | None,
    zeitausdruck_roh: str,
    user_id:          str,
) -> int | None:
    """Loest einen Roh-Zeitausdruck zu einer Timeline-ID auf.

    Drei Pfade in Reihenfolge:
      1. Clipboard: wenn der TimelineAgent in diesem Turn schon eine
         timeline_id ins State geschrieben hat, uebernehmen.
      2. Zeit-Parsing: zeit_parsen_vektor liefert datetime. Existiert
         fuer (user_id, tag, event_type='erinnerungs_anker') bereits
         ein Eintrag, dessen ID nehmen (Idempotenz).
      3. Anlage: TimelineRepository.insert mit event_type=
         'erinnerungs_anker', Flags (False, False, False).

    Liefert None, wenn Salience keinen Zeitausdruck erkannt hat oder
    der Parser kein Datum extrahieren konnte.
    """
    # Pfad 1: Clipboard-Uebernahme
    if clipboard_id is not None:
        logger.info(
            f"magnete_aufloesen: Clipboard-Uebernahme timeline_id={clipboard_id}"
        )
        return clipboard_id

    # Pfad 2/3 brauchen einen Zeitausdruck
    if not zeitausdruck_roh:
        return None

    vektor: ZeitVektor = zeit_parsen_vektor(zeitausdruck_roh)
    if vektor.datum is None:
        logger.info(
            f"magnete_aufloesen: Zeitausdruck '{zeitausdruck_roh}' "
            f"nicht parsebar — kein Anker"
        )
        return None

    # Idempotenz: existierenden Anker am gleichen Tag wiederverwenden
    try:
        treffer: list[dict] = TimelineRepository.find_by_date(
            POSTGRES_URL, user_id, vektor.datum, precision="day"
        )
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: magnete_aufloesen: find_by_date fehlgeschlagen"
        )
        return None

    anker_treffer: list[dict] = [
        t for t in treffer if t.get("event_type") == EVENT_TYPE_ERINNERUNGS_ANKER
    ]
    if anker_treffer:
        existing_id: int = anker_treffer[0]["id"]
        logger.info(
            f"magnete_aufloesen: Bestehenden Erinnerungs-Anker wiederverwendet "
            f"(id={existing_id}, datum={vektor.datum:%Y-%m-%d})"
        )
        return existing_id

    # Anlage neuer Anker
    precision: str = "minute" if vektor.uhrzeit_erkannt else "day"
    try:
        neue_id: int = TimelineRepository.insert(
            postgres_url   = POSTGRES_URL,
            user_id        = user_id,
            event_time     = vektor.datum,
            event_type     = EVENT_TYPE_ERINNERUNGS_ANKER,
            title          = f"Erinnerungs-Anker {vektor.datum:%d.%m.%Y}",
            precision      = precision,
            binding        = False,
            remind         = False,
            conflict_check = False,
        )
        logger.info(
            f"magnete_aufloesen: Neuer Erinnerungs-Anker angelegt "
            f"(id={neue_id}, datum={vektor.datum:%Y-%m-%d}, precision={precision})"
        )
        return neue_id
    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: magnete_aufloesen: TimelineRepository.insert fehlgeschlagen"
        )
        return None
