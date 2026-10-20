"""Such-Knoten — löst Subjekt und Objekt nur über den Namen auf.

Drei Ausgänge je Name:
  * **kein Treffer** → eine neue Entität, außerhalb der Transaktion des Fakts;
  * **ein Treffer** → diese Entität;
  * **zwei oder mehr** → Rückfrage mit der Bitte um eine Unterscheidung. Es
    wird nichts geschrieben und nichts gebunden: Eine Rückfrage ist kein
    Urteil über den Auftrag und deshalb nie eine Ablehnung.

Erst werden alle Namen aufgelöst, dann wird angelegt. Sonst bliebe bei einer
Rückfrage zum Objekt ein schon angelegtes Subjekt zurück.

Ein Fehler der Suche endet als `fehler` und legt **keine** Entität an — ein
verschluckter Fehler sähe aus wie *kein Treffer* und legte ein Duplikat an.
"""

import logging

from agents.base import AgentState
from agents.fakten.beziehungen import KANON, TYP_SONSTIGES, Relation
from config import POSTGRES_URL
from memory.services.entity_resolution import EntityResolutionService

logger = logging.getLogger("ki_server.agents.fakten.suche")

# Angehängt an die Klärungsfrage des Dienstes: Ohne Wartezustand kommt die
# Antwort als neue Bitte an, sie muss die Unterscheidung also selbst tragen.
UNTERSCHEIDUNG_BITTE: str = (
    "Sag es mir bitte noch einmal mit einer Unterscheidung, etwa dem Nachnamen."
)


def search(state: AgentState) -> dict:
    """Löst Subjekt und Objekt auf und legt fehlende Entitäten an.

    Vorbedingung: Die Parameter tragen `subjekt`, `beziehung` (im Kanon) und
        `objekt`; der Kontext trägt `user_id`.
    Nachbedingung: Bei Erfolg tragen die Parameter `subjekt_id`,
        `subjekt_name` und — wenn das Objekt eine Entität ist — `objekt_id`,
        sonst `objekt_wert`; `neue_entitaeten` nennt die angelegten IDs.
        Bei zwei oder mehr Treffern zu einem Namen `status = "rueckfrage"`
        und nichts angelegt.
    Fehlerfälle: Eine Beziehung außerhalb des Kanons, ein Fehler der Suche
        oder des Anlegens ergibt `status = "fehler"`; nach einem Fehler der
        Suche ist keine Entität angelegt.
    """
    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    user_id: str = state["kontext"].get("user_id", "")
    beziehung: Relation | None = KANON.get(parameter.get("beziehung", ""))
    if beziehung is None or not user_id:
        return _with_step(state, {"status": "fehler",
                                  "fehler": "Suche ohne Beziehung des Kanons oder ohne user_id"},
                          "ungueltig")
    namen: dict[str, str] = {"subjekt": parameter["subjekt"]}
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
        frage: str = (
            EntityResolutionService._build_klärungsfrage(namen[rolle], treffer[rolle])
            + " " + UNTERSCHEIDUNG_BITTE
        )
        logger.info("suchen: %r mehrdeutig (%d Treffer) — Rückfrage", namen[rolle],
                    len(treffer[rolle]))
        return _with_step(state, {"status": "rueckfrage", "rueckfrage": frage},
                          f"mehrdeutig/{namen[rolle]}")

    typen: dict[str, str] = {"subjekt": TYP_SONSTIGES, "objekt": beziehung.objekt_typ}
    try:
        ids, neue = _bind_or_create(user_id, namen, treffer, typen)
    except Exception as fehler:
        logger.exception("suchen: Anlegen einer Entität fehlgeschlagen")
        return _with_step(state, {"status": "fehler",
                                  "fehler": f"Entität nicht angelegt: {fehler}"},
                          "anlegefehler")

    # ── Ausgabe-Verifikation ────────────────────
    if set(ids) != set(namen) or any(i <= 0 for i in ids.values()):
        raise RuntimeError(f"suchen: Auflösung unvollständig {ids} für {sorted(namen)}")
    subjekt_name: str = (
        str(treffer["subjekt"][0]["name"]) if treffer["subjekt"] else parameter["subjekt"]
    )
    aufgeloest: dict = {"subjekt_id": ids["subjekt"], "subjekt_name": subjekt_name,
                        "neue_entitaeten": neue}
    if beziehung.objekt_ist_entitaet:
        aufgeloest["objekt_id"] = ids["objekt"]
    else:
        aufgeloest["objekt_wert"] = parameter["objekt"]
    return _with_step(state, {"parameter": {**parameter, **aufgeloest}},
                      f"aufgeloest/{ids}/neu={neue}")


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
