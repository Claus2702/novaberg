"""Such-Knoten — löst Subjekt und Objekt eines Tripels auf.

Das Subjekt nimmt die Entität, an die das Objekt der Sachlage gebunden ist,
wenn das Tripel von diesem Objekt spricht (`binding_for`); sonst wird es wie
das Objekt über den Namen gesucht. Drei Ausgänge je gesuchtem Namen:
  * **kein Treffer** → eine neue Entität, außerhalb der Transaktion des Fakts;
  * **ein Treffer** → diese Entität;
  * **zwei oder mehr** → `mehrdeutig`. Es wird nichts geschrieben, nichts
    gebunden und **kein Text** gebaut: Der Agent ist passiv, niemand hat ihn
    gefragt, und eine Frage an den Menschen gehört an das Objekt der Lage.

Erst werden alle Namen aufgelöst, dann wird angelegt. Sonst bliebe bei einem
mehrdeutigen Objekt ein schon angelegtes Subjekt zurück.

Ein Fehler der Suche endet als `fehler` und legt **keine** Entität an — ein
verschluckter Fehler sähe aus wie *kein Treffer* und legte ein Duplikat an.
"""

import logging

from agents.base import AgentState
from agents.fakten.beziehungen import KANON, TYP_SONSTIGES, Relation
from config import POSTGRES_URL
from memory.services.entity_resolution import EntityResolutionService

logger = logging.getLogger("ki_server.agents.fakten.suche")


def binding_for(subjekt: str, kandidat: dict) -> int | None:
    """Die Entität, die das Subjekt eines Tripels aus der Bindung seines Kandidaten nimmt.

    Gebunden wird nur, wenn das Objekt der Sachlage an eine Entität gebunden
    ist **und** das Tripel von ihm spricht: Die Wörter des Subjekts stehen
    als zusammenhängende Folge im Namen des Objekts (*Ilva* in *Ilva Berger*).
    Bei *„Mein Hund heißt Rufus“* ist der gebundene Hund das Objekt des
    Tripels, nicht sein Subjekt ICH — blind gebunden entstünde still
    *Rufus hat_haustier Rufus*.

    Vorbedingung: `subjekt` ist nicht leer; `kandidat` ist eine Zeile aus
        `turn_candidates` mit `objekt` und `entitaet_id`.
    Nachbedingung: die ID > 0 der gebundenen Entität oder None — dann sucht
        `search` das Subjekt über den Namen.
    Fehlerfälle: ValueError bei leerem Subjekt; KeyError, wenn dem Kandidaten
        `objekt` oder `entitaet_id` fehlt; ValueError bei einer ID, die keine
        ganze Zahl > 0 ist.
    Ohne Ausgabe-Verifikation: Die Rückgabe ist die ID, die die
        Eingabe-Validierung geprüft hat, oder None — es bleibt nichts, das
        danach anschlagen könnte.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not subjekt.strip():
        raise ValueError("binding_for: leeres Subjekt")  # noqa: TRY003
    entitaet_id: object = kandidat["entitaet_id"]
    objekt: str = str(kandidat["objekt"] or "")
    if entitaet_id is None:
        return None
    if not isinstance(entitaet_id, int) or isinstance(entitaet_id, bool) or entitaet_id <= 0:
        raise ValueError(f"binding_for: keine Entität {entitaet_id!r}")  # noqa: TRY003

    # ── Verarbeitung ────────────────────────────
    soll: list[str] = subjekt.casefold().split()
    ist: list[str] = objekt.casefold().split()
    spricht_davon: bool = any(
        ist[start:start + len(soll)] == soll for start in range(len(ist) - len(soll) + 1)
    )
    return entitaet_id if spricht_davon else None


def search(state: AgentState) -> dict:
    """Löst Subjekt und Objekt auf und legt fehlende Entitäten an.

    Vorbedingung: Die Parameter tragen `subjekt`, `beziehung` (im Kanon) und
        `objekt`, dazu `subjekt_entitaet_id` (int > 0 oder None); der Kontext
        trägt `user_id`.
    Nachbedingung: Bei Erfolg tragen die Parameter `subjekt_id`,
        `subjekt_name` und — wenn das Objekt eine Entität ist — `objekt_id`,
        sonst `objekt_wert`; `neue_entitaeten` nennt die angelegten IDs. Ist
        `subjekt_entitaet_id` gesetzt, ist sie `subjekt_id`, und der Name des
        Subjekts wird nicht gesucht. Bei zwei oder mehr Treffern zu einem
        Namen `status = "mehrdeutig"`, kein Text und nichts angelegt.
    Fehlerfälle: Eine Beziehung außerhalb des Kanons, ein Fehler der Suche
        oder des Anlegens ergibt `status = "fehler"`; nach einem Fehler der
        Suche ist keine Entität angelegt.
    """
    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    user_id: str = state["kontext"].get("user_id", "")
    beziehung: Relation | None = KANON.get(parameter.get("beziehung", ""))
    gebunden: object = parameter["subjekt_entitaet_id"]
    if beziehung is None or not user_id or not _valid_binding(gebunden):
        return _with_step(state, {"status": "fehler",
                                  "fehler": "Suche ohne Beziehung des Kanons, ohne user_id "
                                            f"oder mit ungültiger Bindung {gebunden!r}"},
                          "ungueltig")
    namen: dict[str, str] = {} if gebunden is not None else {"subjekt": parameter["subjekt"]}
    if beziehung.objekt_ist_entitaet:
        namen["objekt"] = parameter["objekt"]

    # ── Verarbeitung ────────────────────────────
    treffer: dict[str, list[dict]] = {}
    try:
        for rolle, name in namen.items():
            treffer[rolle] = EntityResolutionService.resolve_by_name(POSTGRES_URL, user_id, name)
    except Exception as fehler:
        logger.exception("suchen: Namenssuche fehlgeschlagen — keine Entität angelegt")
        return _with_step(state, {"status": "fehler",
                                  "fehler": f"Namenssuche fehlgeschlagen: {fehler}"},
                          "suchfehler")

    mehrdeutig: list[str] = [rolle for rolle, liste in treffer.items() if len(liste) > 1]
    if mehrdeutig:
        rolle: str = mehrdeutig[0]
        logger.info("suchen: %r mehrdeutig (%d Treffer) — nichts geschrieben", namen[rolle],
                    len(treffer[rolle]))
        return _with_step(state, {"status": "mehrdeutig"}, f"mehrdeutig/{rolle}")

    typen: dict[str, str] = {"subjekt": TYP_SONSTIGES, "objekt": beziehung.objekt_typ}
    try:
        ids, neue = _bind_or_create(user_id, namen, treffer, typen)
    except Exception as fehler:
        logger.exception("suchen: Anlegen einer Entität fehlgeschlagen")
        return _with_step(state, {"status": "fehler",
                                  "fehler": f"Entität nicht angelegt: {fehler}"},
                          "anlegefehler")
    if gebunden is not None:
        ids["subjekt"] = gebunden

    # ── Ausgabe-Verifikation ────────────────────
    if set(ids) != {"subjekt", *namen} or any(i <= 0 for i in ids.values()):
        raise RuntimeError(f"suchen: Auflösung unvollständig {ids} für {sorted(namen)}")
    subjekt_name: str = (
        str(treffer["subjekt"][0]["name"]) if treffer.get("subjekt") else parameter["subjekt"]
    )
    aufgeloest: dict = {"subjekt_id": ids["subjekt"], "subjekt_name": subjekt_name,
                        "neue_entitaeten": neue}
    if beziehung.objekt_ist_entitaet:
        aufgeloest["objekt_id"] = ids["objekt"]
    else:
        aufgeloest["objekt_wert"] = parameter["objekt"]
    herkunft_subjekt: str = "gebunden" if gebunden is not None else "name"
    return _with_step(state, {"parameter": {**parameter, **aufgeloest}},
                      f"aufgeloest/{ids}/subjekt={herkunft_subjekt}/neu={neue}")


def _valid_binding(gebunden: object) -> bool:
    """Sagt, ob die Bindung des Subjekts eine mögliche Entität ist.

    Vorbedingung: keine; `gebunden` kommt aus `binding_for` über die Parameter.
    Nachbedingung: True bei None (ungebunden) oder einer ganzen Zahl > 0.
    Fehlerfälle: keine — False heißt *ungültig*, und der Aufrufer endet als `fehler`.
    """
    # ── Verarbeitung ────────────────────────────
    if gebunden is None:
        return True
    return isinstance(gebunden, int) and not isinstance(gebunden, bool) and gebunden > 0


def _bind_or_create(
    user_id: str,
    namen: dict[str, str],
    treffer: dict[str, list[dict]],
    typen: dict[str, str],
) -> tuple[dict[str, int], list[int]]:
    """Bindet je Rolle den einen Treffer oder legt eine neue Entität an.

    Vorbedingung: Zu jeder Rolle in `namen` liegen höchstens ein Treffer und
        ein Typ vor — die Mehrdeutigkeit ist vorher entschieden.
    Nachbedingung: je Rolle eine ID > 0; die zweite Liste nennt die neu
        angelegten IDs.
    Fehlerfälle: ValueError bei mehr als einem Treffer; ein Fehler beim
        Anlegen geht nach oben.
    """
    # ── Eingabe-Validierung ─────────────────────
    if any(len(treffer[rolle]) > 1 for rolle in namen):
        raise ValueError(f"_bind_or_create: mehrdeutige Treffer {treffer}")

    # ── Verarbeitung ────────────────────────────
    ids: dict[str, int] = {}
    neue: list[int] = []
    for rolle, name in namen.items():
        if treffer[rolle]:
            ids[rolle] = int(treffer[rolle][0]["id"])
            continue
        ids[rolle] = EntityResolutionService.create_new_entity(
            POSTGRES_URL, user_id, name, typ=typen[rolle],
        )
        neue.append(ids[rolle])
    return ids, neue


def _with_step(state: AgentState, aenderung: dict, ergebnis: str) -> dict:
    """Hängt den Schritt der Suche an eine Zustandsänderung.

    Vorbedingung: `aenderung` ist die Änderung des Zustands ohne `schritte`.
    Nachbedingung: dieselbe Änderung mit einem Schritt mehr.
    Fehlerfälle: ValueError, wenn `aenderung` selbst Schritte trägt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "schritte" in aenderung:
        raise ValueError("Suche Fakten: Änderung trägt schon Schritte")

    # ── Verarbeitung ────────────────────────────
    return {**aenderung,
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": ergebnis}]}
