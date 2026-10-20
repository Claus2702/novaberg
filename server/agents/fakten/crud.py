"""Ausführungs-Knoten — schreibt den Fakt und meldet, was die Verifikation ergab.

Geschrieben wird in einer Transaktion (`FaktenRepository.schreiben`), mit der
Herkunft `mensch`: Der Agent schreibt nur, worum der Mensch gebeten hat.
Danach wird die geltende Zeile frisch gelesen und gegen den Auftrag gehalten;
`abgeschlossen` meldet der Knoten nur, wenn sie dasteht (`verified_outcome`).
*identisch* ist ein Erfolg ohne neue Zeile.
"""

import logging

from agents.base import AgentState
from agents.fakten.beziehungen import KANON, Relation
from agents.write_outcome import verified_outcome
from config import POSTGRES_URL
from memory.repositories.fakten_repository import FaktenRepository, NewFact, Schreibung

logger = logging.getLogger("ki_server.agents.fakten.crud")

HERKUNFT_AGENT: str = "mensch"

# Was der Nutzer je Art der Schreibung hört.
MELDUNGEN: dict[str, str] = {
    "identisch": "Das weiß ich schon: {text}.",
    "angelegt":  "Gemerkt: {text}.",
    "abgeloest": "Gemerkt: {text}. Den alten Wert habe ich abgelöst.",
}


def execute(state: AgentState) -> dict:
    """Schreibt den aufgelösten Fakt und verifiziert ihn.

    Vorbedingung: Die Parameter tragen `beziehung` (im Kanon), `subjekt_id`,
        `subjekt_name`, `objekt` und genau eines von `objekt_id` und
        `objekt_wert`; der Kontext trägt `user_id` und `character_id`.
    Nachbedingung: `status = "abgeschlossen"` nur, wenn die geltende Zeile
        aktiv ist und Paar, Subjekt, Beziehung, Objekt und Herkunft trägt;
        sonst `status = "fehler"`.
    Fehlerfälle: Ein Fehler beim Schreiben ergibt `fehler`; die Transaktion
        ist dann zurückgenommen.
    """
    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    user_id: str = state["kontext"].get("user_id", "")
    character_id: str = state["kontext"].get("character_id", "")
    beziehung: Relation | None = KANON.get(parameter.get("beziehung", ""))
    if beziehung is None or not user_id or not character_id or not parameter.get("subjekt_id"):
        return _with_step(state, {"status": "fehler",
                                  "fehler": "Ausführung ohne Beziehung, Paar oder Subjekt"},
                          "ungueltig")
    text: str = (
        f"{parameter['subjekt_name']} {beziehung.attribut.replace('_', ' ')} "
        f"{parameter['objekt']}"
    )
    neu = NewFact(
        fakt_text=text, herkunft=HERKUNFT_AGENT, einwertig=beziehung.einwertig,
        objekt_id=parameter.get("objekt_id"), objekt_wert=parameter.get("objekt_wert"),
    )

    # ── Verarbeitung ────────────────────────────
    try:
        schreibung: Schreibung = FaktenRepository.schreiben(
            POSTGRES_URL, user_id, character_id, parameter["subjekt_id"],
            beziehung.attribut, neu,
        )
    except Exception as fehler:
        logger.exception("ausfuehren: Schreiben fehlgeschlagen — zurückgenommen")
        return _with_step(state, {"status": "fehler",
                                  "fehler": f"Fakt nicht geschrieben: {fehler}"},
                          "schreibfehler")
    zeile: dict | None = FaktenRepository.find_by_id(
        POSTGRES_URL, user_id, character_id, schreibung.fakt_id,
    )

    # ── Ausgabe-Verifikation ────────────────────
    erwartet: dict = {
        "subjekt_id": parameter["subjekt_id"], "attribut": beziehung.attribut,
        "objekt_id": neu.objekt_id, "herkunft": HERKUNFT_AGENT,
    }
    verifiziert: bool = zeile is not None and all(
        zeile.get(spalte) == wert for spalte, wert in erwartet.items()
    ) and (neu.objekt_wert is None
           or str(zeile.get("objekt_wert") or "").casefold() == neu.objekt_wert.casefold())
    logger.info("ausfuehren: id=%s %s, verifiziert=%s", schreibung.fakt_id, schreibung.art,
                verifiziert)
    ausgang: dict = verified_outcome({
        "status": "abgeschlossen",
        "ergebnis": MELDUNGEN[schreibung.art].format(text=text),
    }, verifiziert)
    return _with_step(state, {**ausgang, "parameter": {**parameter,
                                                       "fakt_id": schreibung.fakt_id,
                                                       "art": schreibung.art}},
                      f"{schreibung.art}/id={schreibung.fakt_id}/verifiziert={verifiziert}")


def _with_step(state: AgentState, aenderung: dict, ergebnis: str) -> dict:
    """Hängt den Schritt der Ausführung an eine Zustandsänderung.

    Vorbedingung: `aenderung` ist die Änderung des Zustands ohne `schritte`.
    Nachbedingung: dieselbe Änderung mit einem Schritt mehr.
    Fehlerfälle: ValueError, wenn `aenderung` selbst Schritte trägt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if "schritte" in aenderung:
        raise ValueError("Ausführung Fakten: Änderung trägt schon Schritte")

    # ── Verarbeitung ────────────────────────────
    return {**aenderung,
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": ergebnis}]}
