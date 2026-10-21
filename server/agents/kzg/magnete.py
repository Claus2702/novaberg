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

Auflösung nur über den Namen: Ein Name, der keine eigene Entität hat, wird
eine neue — auch wenn eine bestehende ihm nur ähnelt (*Lena*, wo nur *Lea*
steht). Zwei Akten derselben Person werden später auf Rückfrage
zusammengelegt, nicht hier still verbunden.

Ausfall: Die Suche wirft bei einem Fehler der Datenbank und bei *ICH* ohne
Entität des Menschen, das Anlegen bei einem Fehler des Schreibens. Hier
endet er, je Name: Der Name bekommt keine ID, es wird keine
Entität angelegt, der Ausfall steht als `error` und als Eintrag `fehler` im
Pipeline-Log; die übrigen Namen werden aufgelöst, und der Eintrag des
Kurzzeitgedächtnisses wird mit den Magneten geschrieben, die stehen.

Spezifikation: docs/novaberg-memory-synapsen_k.md §13.5.
"""

import logging

from agents.base import AgentState
from config import POSTGRES_URL
from memory.pipeline_log import log_fehler
from memory.repositories.timeline_repository import TimelineRepository
from memory.services.entity_resolution import EntityResolutionService
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

    Je Name, nur über den Namen (`_namen_suchen`): Der Name wird getrimmt,
    ein leerer übersprungen. Kein Treffer → eine neue Entität mit dem
    getrimmten Namen und Typ `sonstiges`; ein Treffer → seine ID; mehr als
    einer → kein Magnet, nichts angelegt, eine Zeile `info` — der KZG-Pfad ist
    nicht interaktiv und kann nicht zurückfragen (convention-magneten.md).

    Je Name, nicht je Liste, weil Suche und Anlegen bei einem Ausfall werfen:
    Ein Aufruf für alle Namen verlöre mit dem einen Ausfall auch die übrigen.

    Vorbedingung: user_id ist nicht leer (geprüft im Knoten).
    Nachbedingung: Die erste Liste trägt die IDs der aufgelösten oder neu
        angelegten Namen in der Reihenfolge der Eingabe; die zweite nennt die
        Namen, deren Suche oder Anlegen ausfiel — für sie wurde keine Entität
        angelegt, und je Name stehen eine Zeile `error` und ein Eintrag
        `fehler` im Pipeline-Log. Leere und mehrdeutige Namen stehen in
        keiner der beiden Listen.
    Fehlerfälle: ValueError bei leerer user_id. Ein Fehler der Suche (auch
        *ICH* ohne Entität des Menschen) oder des Anlegens verlässt die
        Funktion nicht.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not roh_namen:
        return [], []
    if not user_id:
        raise ValueError("_entitaeten_aufloesen: user_id ist leer")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    entitaet_ids: list[int] = []
    ausgefallen:  list[str] = []
    for roh in roh_namen:
        stufe: str = "suche"
        try:
            name: str = roh.strip()
            if not name:
                continue
            treffer: list[dict] = _namen_suchen(name, user_id)
            if len(treffer) > 1:
                logger.info(
                    f"magnete_aufloesen: '{name}' mehrdeutig ({len(treffer)} "
                    f"Entitaeten) — im KZG-Pfad kein Magnet (nicht-interaktiv)"
                )
                continue
            if treffer:
                entitaet_id: int = treffer[0]["id"]
            else:
                stufe = "anlegen"
                entitaet_id = EntityResolutionService.create_new_entity(
                    postgres_url = POSTGRES_URL,
                    user_id      = user_id,
                    name         = name,
                    typ          = "sonstiges",
                )
                logger.info(
                    f"magnete_aufloesen: Neue Entitaet '{name}' "
                    f"angelegt (id={entitaet_id})"
                )
        except Exception as fehler:  # noqa: BLE001 — ein Ausfall kostet nur diesen Namen
            _ausfall_melden(roh, stufe, fehler, user_id, turn_id)
            ausgefallen.append(roh)
            continue

        entitaet_ids.append(entitaet_id)

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
) -> list[dict]:
    """Sucht einen einzelnen Namen nur über den Namen (resolve_by_name).

    Ohne Rückfall über Embeddings: Ein ähnlicher Name ist kein Treffer, und
    der Aufrufer legt für ihn eine neue Entität an, statt ihn still an eine
    fremde zu binden.

    Vorbedingung: user_id und name sind nicht leer, name ist getrimmt.
    Nachbedingung: die Treffer der Suche, jeder mit einer ID > 0 — leer
        heißt: die Suche lief und fand nichts. *ICH* ergibt die Entität des
        Menschen.
    Fehlerfälle: ValueError bei leerer Eingabe. Jeder Fehler der Suche geht
        durch, auch LookupError bei *ICH* ohne Entität des Menschen — der
        Aufrufer fängt je Name. RuntimeError, wenn ein Treffer keine ID > 0
        trägt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id:
        raise ValueError("_namen_suchen: user_id ist leer")  # noqa: TRY003
    if not name or name != name.strip():
        raise ValueError(  # noqa: TRY003
            f"_namen_suchen: name {name!r} ist leer oder nicht getrimmt"
        )

    # ── Verarbeitung ────────────────────────────
    treffer: list[dict] = EntityResolutionService.resolve_by_name(
        POSTGRES_URL, user_id, name,
    )

    # ── Ausgabe-Verifikation ────────────────────
    for zeile in treffer:
        if not isinstance(zeile.get("id"), int) or zeile["id"] <= 0:
            raise RuntimeError(  # noqa: TRY003
                f"_namen_suchen: Treffer für '{name}' ohne ID > 0: {zeile.get('id')!r}"
            )
    return treffer


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
