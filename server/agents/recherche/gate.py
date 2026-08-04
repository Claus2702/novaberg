"""Keep/Discard-Gate — was aus einem Durchlauf in die Bibliothek darf.

Der Schritt zwischen Destillation und Ablage. Er beantwortet eine einzige
Frage: Steht im Destillat etwas, das über Novas Vorwissen hinausgeht?

| Status | Wissen-Datei | Bericht-Datei |
|---|---|---|
| `echte_tiefe` | ja | ja |
| `ergaenzung` | ja | ja |
| `wiederholung` | **nein** | ja |
| `fehlschlag` | **nein** | ja |

**Ohne dieses Gate schreibt der Speicher unbedingt**, und die Bibliothek
füllt sich mit Wiederholungen, die jede spätere Ähnlichkeitssuche verwässern.

**Ein Ausfall des Modells ist kein Urteil.** Fällt der Aufruf aus oder liefert
er einen Status außerhalb des Kanons, wird `fehlschlag` zurückgegeben —
nicht `echte_tiefe`. Der Bericht entsteht dann trotzdem, die Wissen-Datei
nicht. Die umgekehrte Vorgabe wäre die teurere: Sie machte einen
ausgefallenen Aufruf von einem substanziellen Ergebnis ununterscheidbar und
schriebe genau das in die Bibliothek, was das Gate fernhalten soll.

Spezifikation: docs/novaberg-autonomous-wissen_k.md §5.
"""

import logging

from memory.repositories.autonomous_wissen_repository import WISSEN_STATUS
from services.model_services import BackgroundRequest, model_service

logger = logging.getLogger("ki_server.agents.recherche.gate")

_GATE_PROMPT: str = """[IDENTITAET]
Du bist das Bewertungs-Modul von Nova.
Deine Aufgabe: Entscheiden, ob ein Rechercheergebnis in Novas Wissensspeicher gehoert.

[RECHERCHE_ZIEL]
{ziel}

[NOVAS_VORWISSEN]
{vorwissen}

[DESTILLAT]
{destillat}

[AUFGABE]
Enthaelt das Destillat substanzielle Information, die ueber Novas Vorwissen hinausgeht?

[FORMAT]
Antworte ausschliesslich als JSON:
{{
  "status": "echte_tiefe" oder "ergaenzung" oder "wiederholung" oder "fehlschlag",
  "begruendung": "Ein bis zwei Saetze, woran du das festmachst"
}}

[REGELN]
- "echte_tiefe": substanzieller Zuwachs, ein neuer Zusammenhang oder mehrere neue Fakten
- "ergaenzung": kleiner Zuwachs, Randinformation, ein Detail zum Bekannten
- "wiederholung": nur Bekanntes, nichts das ueber das Vorwissen hinausgeht
- "fehlschlag": das Destillat traegt keine verwertbare Information zum Ziel
- Die Begruendung nennt, WAS neu ist — nicht, dass etwas neu ist
- Sprache: Deutsch"""


def ergebnis_einordnen(*, ziel: str, destillat: str, lage: dict | None = None) -> dict[str, str]:
    """Ordnet ein Destillat in den Status-Kanon ein.

    Vorbedingung: keine — ein leeres Destillat ist ein zulässiger Eingang
    und der klarste Fall von `fehlschlag`.
    Nachbedingung: Der zurückgegebene `status` liegt im Kanon
    `WISSEN_STATUS`; `begruendung` ist eine nicht-leere Zeichenkette.
    Fehlerfälle: keine nach außen. Ein Ausfall des Modells wird zu
    `fehlschlag` mit benannter Ursache — der Aufrufer soll ablegen können,
    ohne den Ausfall zu behandeln, und der Bericht trägt die Ursache.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not destillat or not destillat.strip():
        logger.error("Gate: leeres Destillat — als fehlschlag eingeordnet, keine Wissen-Datei")
        return {"status": "fehlschlag", "begruendung": "Das Destillat war leer."}

    if lage is None:
        lage = {}

    prompt: str = _GATE_PROMPT.format(
        ziel=ziel or "Kein Ziel protokolliert.",
        vorwissen=lage.get("vorwissen_zusammenfassung", "Kein Vorwissen."),
        destillat=destillat,
    )

    # ── Verarbeitung ────────────────────────────
    try:
        response = model_service.background.submit_sync(BackgroundRequest(
            messages    = [{"role": "user", "content": prompt}],
            modus       = "analyse",
            temperature = 0.1,
            expect_json = True,
            caller      = "recherche/gate",
        ))
        urteil: dict = response.parsed or {}
    except Exception as fehler:
        logger.exception(
            f"Gate: Aufruf fehlgeschlagen ({type(fehler).__name__}) — als fehlschlag "
            f"eingeordnet, keine Wissen-Datei"
        )
        return {
            "status": "fehlschlag",
            "begruendung": f"Das Gate konnte nicht urteilen: {type(fehler).__name__}.",
        }

    # ── Ausgabe-Verifikation ────────────────────
    # Zugehoerigkeit zum Kanon, nicht zu einer Teilmenge: Ein unbekannter
    # Status ist ein Defekt der Modellantwort und kein viertes Urteil.
    status: str = str(urteil.get("status", "")).strip()
    if status not in WISSEN_STATUS:
        logger.error(
            f"Gate: status={status!r} steht nicht im Kanon {sorted(WISSEN_STATUS)} — "
            f"als fehlschlag eingeordnet, keine Wissen-Datei"
        )
        return {
            "status": "fehlschlag",
            "begruendung": f"Das Gate lieferte den unbekannten Status {status!r}.",
        }

    begruendung: str = str(urteil.get("begruendung", "")).strip()
    if not begruendung:
        # Kein Abbruch: Das Urteil ist gueltig, nur seine Begruendung fehlt.
        # Sie steht spaeter im Bericht, und eine leere Stelle dort waere
        # nicht von einem unbegruendeten Urteil zu unterscheiden.
        logger.warning(f"Gate: Status {status} ohne Begruendung geliefert")
        begruendung = "Das Gate lieferte keine Begruendung."

    logger.info(f"Gate: {status} — {begruendung[:120]}")
    return {"status": status, "begruendung": begruendung}
