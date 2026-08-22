"""Klassifikation — welche der fuenf Aktionen der Mensch gemeint hat.

Spezifikation: docs/novaberg-agent-dateien_k.md §2a.2.

Dieser Schritt entscheidet die **Absicht**, nicht die **Zulaessigkeit**. Der
genannte Pfad wird unveraendert uebernommen und nicht korrigiert; ob er
freigebbar ist, entscheidet der Aussenrand und nicht ein Sprachmodell (§7).

Prompt-Schema: [BLOCKNAME]-Format wie bei den uebrigen Klassifikatoren.
"""

import json
import logging

from config import PROMPTS, get_node_config, redis_client
from memory.session import format_session_turns_numbered, session_turns_retrieve
from services.model_services import ChatRequest, model_service

from agents.base import AgentState
from agents.dateien_wurzeln.crud import EIGENTUM_KANON, Paar, _read_aktive, _read_inaktive

logger = logging.getLogger("ki_server.agents.dateien_wurzeln.klassifikation")

#: Der Kanon der Klassifikations-Ausgaenge. `rejected` ist die Vorform des
#: vierten Ausgangs und gehoert deshalb dazu, obwohl es keine Aktion ist.
GUELTIGE_AKTIONEN: frozenset[str] = frozenset(
    {"create", "read", "update", "delete", "reactivate", "rejected"}
)


def _bestand_text(eintraege: list[dict]) -> str:
    """Formt die Bestandsliste fuer den Prompt.

    Vorbedingung: `eintraege` ist eine Liste von Zeilen aus `dateien_wurzeln`.
    Nachbedingung: Ein mehrzeiliger Text oder "(keine)".
    """
    if not eintraege:
        return "(keine)"

    zeilen: list[str] = []
    for eintrag in eintraege:
        zeile: str = f"  [{eintrag['id']}] {eintrag['pfad']}"
        if eintrag.get("bezeichnung"):
            zeile += f" ({eintrag['bezeichnung']})"
        zeilen.append(zeile)
    return "\n".join(zeilen)



def _ziffer_oder_nichts(roh: object) -> int | None:
    """Macht aus der Modellangabe eine Nummer oder ausdruecklich keine.

    Vorbedingung: `roh` ist, was das Sprachmodell geliefert hat — eine Zahl,
    eine Zeichenkette, `None` oder etwas anderes.
    Nachbedingung: Eine Ganzzahl oder `None`. Ein unbrauchbarer Wert wird
    gemeldet und zu `None`, nicht zu einer geratenen Nummer.

    Der Grund fuer diese Funktion ist die Grenze: Eine Modellantwort ist die
    unzuverlaessigste Quelle im System (`11_EVA` §1). `"3"` und `3` kommen
    beide vor, und weiter unten entscheidet der Wert, **welche** Freigabe
    zurueckgenommen wird — dort darf keine Zeichenkette ankommen.
    """
    if roh is None:
        return None
    if isinstance(roh, bool):
        # bool ist eine Unterklasse von int — True waere sonst Freigabe 1.
        logger.error(
            "dateien_wurzeln: target_id kam als Wahrheitswert %r — verworfen", roh,
        )
        return None
    if isinstance(roh, int):
        return roh
    if isinstance(roh, str) and roh.strip().isdigit():
        return int(roh.strip())

    logger.error(
        "dateien_wurzeln: target_id %r (%s) ist keine Nummer — verworfen; die "
        "Freigabe wird stattdessen ueber das Stichwort gesucht",
        roh, type(roh).__name__,
    )
    return None


def _build_classify_prompt(
    aktive_wurzeln: str,
    inaktive_wurzeln: str,
    session_turns: str | None = None,
) -> str:
    """Baut den Klassifikations-System-Prompt aus den Bloecken."""
    aktionen_text: str = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_dateien_wurzeln.identity"].format(),
        PROMPTS["classify_dateien_wurzeln.task"].format(
            aktionen_text=aktionen_text,
            aktive_wurzeln=aktive_wurzeln,
            inaktive_wurzeln=inaktive_wurzeln,
        ),
    ]

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf fuer Kontext-Aufloesung — besonders bei "
            "'nimm das wieder weg'.\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["classify_dateien_wurzeln.fachsprache"].format())
    bloecke.append(PROMPTS["classify_dateien_wurzeln.rules"].format())

    return "\n\n".join(bloecke)


def klassifizieren(state: AgentState) -> dict:
    """Bestimmt Aktion, Pfad, Bezeichnung und Ziel per Modellaufruf.

    Vorbedingung: `state["aufgabe"]` traegt die Aeusserung; `kontext` traegt
    `user_id` und `character_id`.
    Nachbedingung: `parameter["action"]` liegt in GUELTIGE_AKTIONEN, oder
    der Status ist "fehler". **Kein Ruecksetzen auf einen Vorgabewert** —
    eine unbekannte Aktion ist eine defekte Modellantwort und wird als
    solche gemeldet, nicht als "read" ausgefuehrt.
    """
    # ── Eingabe-Validierung ─────────────────────
    prompt: str = state["aufgabe"]
    user_id: str = state["kontext"].get("user_id", "")
    character_id: str = state["kontext"].get("character_id", "")

    if not prompt or not prompt.strip():
        logger.error(
            "dateien_wurzeln.klassifizieren: leere Aufgabe fuer (%s x %s) — "
            "es gibt nichts zu klassifizieren", user_id, character_id,
        )
        return {
            "status": "fehler",
            "fehler": "Leere Aeusserung — nichts zu klassifizieren.",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": "leere_aufgabe"}
            ],
        }

    logger.info(
        "dateien_wurzeln.klassifizieren: Einstieg — prompt='%s', user_id='%s'",
        prompt[:80], user_id,
    )

    # ── Verarbeitung ────────────────────────────
    paar: Paar = Paar(user_id=user_id, character_id=character_id)
    aktive_text: str = _bestand_text(_read_aktive(paar))
    inaktive_text: str = _bestand_text(_read_inaktive(paar))

    session_turns: str | None = None
    if user_id:
        try:
            rohe_turns: list[dict] = session_turns_retrieve(redis_client, user_id, character_id)
            session_turns = format_session_turns_numbered(rohe_turns, max_turns=5) or None
        except Exception as fehler:  # noqa: BLE001 — Kontext ist Zubehoer, nicht Bedingung
            logger.warning(
                "dateien_wurzeln.klassifizieren: Session-Kontext fehlt (%s: %s) — "
                "es wird ohne Verlauf klassifiziert",
                type(fehler).__name__, fehler,
            )

    system_prompt: str = _build_classify_prompt(aktive_text, inaktive_text, session_turns)
    node_cfg: dict = get_node_config("router")

    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/dateien_wurzeln/klassifikation",
    )

    try:
        antwort = model_service.chat.submit_sync(chat_request)
        ergebnis: dict = antwort.parsed
    except (json.JSONDecodeError, KeyError, AttributeError) as fehler:
        logger.exception(
            "%s: dateien_wurzeln.klassifizieren: Modellantwort unbrauchbar",
            type(fehler).__name__,
        )
        return {
            "status": "fehler",
            "fehler": f"Klassifikation fehlgeschlagen: {fehler}",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": "json_fehler"}
            ],
        }

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(ergebnis, dict):
        logger.error(
            "dateien_wurzeln.klassifizieren: Modellantwort ist %s statt dict — "
            "verworfen", type(ergebnis).__name__,
        )
        return {
            "status": "fehler",
            "fehler": "Klassifikation lieferte kein Objekt.",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": "kein_objekt"}
            ],
        }

    action: str = ergebnis.get("action", "") or ""
    if action not in GUELTIGE_AKTIONEN:
        logger.error(
            "dateien_wurzeln.klassifizieren: Aktion %r nicht im Kanon %s — "
            "verworfen statt ersetzt; ein Vorgabewert machte hier eine "
            "defekte Antwort von einer gueltigen ununterscheidbar",
            action, sorted(GUELTIGE_AKTIONEN),
        )
        return {
            "status": "fehler",
            "fehler": f"Klassifikation lieferte die unbekannte Aktion {action!r}.",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": f"aktion_unbekannt/{action[:30]}"}
            ],
        }

    if action == "rejected":
        grund: str = ergebnis.get("grund", "") or "kein Grund angegeben"
        logger.info("dateien_wurzeln.klassifizieren: REJECTED — %s", grund)
        return {
            "parameter": {**state["parameter"], "action": "rejected"},
            "status": "rejected",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": f"rejected/{grund[:60]}"}
            ],
        }

    pfad: str = ergebnis.get("pfad", "") or ""
    bezeichnung: str = ergebnis.get("bezeichnung", "") or ""
    stichwort: str = ergebnis.get("stichwort", "") or ""
    target_id: int | None = _ziffer_oder_nichts(ergebnis.get("target_id"))
    normalisiert: str = ergebnis.get("normalisiert", "") or ""

    # `eigentum` wird uebernommen, nicht erschlossen. Ein Wert ausserhalb des
    # Kanons ist kein Wert: Das Modell hat dann etwas anderes verstanden als
    # gefragt war, und der leere String fuehrt eine Zeile weiter zur
    # Rueckfrage — dorthin, wo eine unbeantwortete Frage hingehoert.
    eigentum: str = (ergebnis.get("eigentum", "") or "").strip().lower()
    if eigentum and eigentum not in EIGENTUM_KANON:
        logger.warning(
            "dateien_wurzeln.klassifizieren: eigentum=%r liegt ausserhalb %s "
            "— gilt als nicht genannt, es wird nachgefragt",
            eigentum, sorted(EIGENTUM_KANON),
        )
        eigentum = ""

    # Ein Stichwort, das fehlt, aber aus der Bezeichnung ablesbar ist: Der
    # Mensch spricht seine Freigabe ueber ihren Namen an, und das Modell legt
    # ihn mal in das eine, mal in das andere Feld. Das ist keine Ersetzung
    # eines Pflichtfeldes, sondern dieselbe Angabe an zweiter Stelle.
    if action in ("update", "delete", "reactivate") and not stichwort:
        stichwort = bezeichnung if action != "update" else ""

    logger.info(
        "dateien_wurzeln.klassifizieren: action='%s', pfad='%s', "
        "bezeichnung='%s', stichwort='%s', target_id=%s, eigentum='%s', "
        "normalisiert='%s'",
        action, pfad[:80], bezeichnung[:40], stichwort[:40], target_id,
        eigentum or "(nicht genannt)", normalisiert[:80],
    )

    return {
        "parameter": {
            **state["parameter"],
            "action": action,
            "pfad": pfad,
            "bezeichnung": bezeichnung,
            "stichwort": stichwort,
            "target_id": target_id,
            "normalisiert": normalisiert,
            "eigentum": eigentum,
        },
        "schritte": state["schritte"] + [
            {"node": "klassifizieren", "ergebnis": f"{action}/{(pfad or bezeichnung)[:40]}"}
        ],
    }
