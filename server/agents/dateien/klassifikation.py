"""Klassifikation — wonach in den Unterlagen gesucht wird, und wie tief.

Spezifikation: docs/novaberg-agent-dateien_k.md §8.1, §6.3, §6.4.

Dieser Schritt entscheidet die **Absicht** und den **Suchschlüssel**, nicht die
Datei. Welche Datei einschlägig ist, entscheidet die Suche über ihre drei Kanäle
(§6.3) — scharf vor unscharf, und der Kosinus ordnet innerhalb der Kandidaten.

> **Deshalb steht der Dateibestand ausdrücklich nicht im Prompt.** Ihn dem
> Modell vorzulegen hieße, die Auswahl vom Index in eine Schätzung zu verlegen:
> Das Modell sähe 14 Namen und wählte einen, während der scharfe Kanal denselben
> Namen exakt trifft oder eben gar keinen. Ein Kandidat, der aus einer Liste
> geraten ist, ist von einem gefundenen nicht mehr zu unterscheiden.

**Die Tiefe ist eine eigene Angabe, weil sie Geld kostet.** `finden` beantwortet
*„wo steht etwas"* und bleibt im Index; `lesen` beantwortet *„was steht dort"*
und greift zur Datei (§6.4).

Prompt-Schema: [BLOCKNAME]-Format wie bei den übrigen Klassifikatoren.
"""

import json
import logging

from config import PROMPTS, get_node_config, redis_client
from memory.session import format_session_turns_numbered, session_turns_retrieve
from services.model_services import ChatRequest, model_service

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.dateien.klassifikation")

#: Der Kanon der Klassifikations-Ausgänge. `rejected` ist die Vorform des
#: vierten Ausgangs und gehört dazu, obwohl es keine Aktion ist.
AKTION_FINDEN: str = "finden"
AKTION_LESEN: str = "lesen"
GUELTIGE_AKTIONEN: frozenset[str] = frozenset(
    {AKTION_FINDEN, AKTION_LESEN, "rejected"}
)

#: Höchstzahl der Begriffe, die in den scharfen Kanal gehen. Mehr Begriffe
#: verbreitern die Kandidatenmenge statt sie zu schärfen: Die Abfrage
#: verknüpft sie mit ODER, und ein einziger unspezifischer Begriff darunter
#: holt den halben Bestand herein.
BEGRIFFE_KAPPUNG: int = 4

#: Kappung für einen einzelnen Begriff. Was länger ist, ist ein Satzfragment
#: und kein Begriff — und ein Satzfragment trifft im lexikalischen Kanon nichts.
BEGRIFF_MAX_ZEICHEN: int = 60


def _begriffe_pruefen(roh: object) -> list[str]:
    """Macht aus der Modellangabe eine Liste von Begriffen oder eine leere.

    Vorbedingung: `roh` ist, was das Sprachmodell geliefert hat — eine Liste,
    eine Zeichenkette, `None` oder etwas anderes.
    Nachbedingung: Höchstens `BEGRIFFE_KAPPUNG` nichtleere Begriffe, jeder
    höchstens `BEGRIFF_MAX_ZEICHEN` lang. Leer ist zulässig und heißt „die
    Frage trug keinen Fachbegriff" — dann sucht der dense Kanal (§6.3).
    Fehlerfaelle: Jeder verworfene Wert wird einzeln gemeldet. **Eine
    Zeichenkette wird als ein Begriff gelesen und nicht zerlegt**: Wer sie am
    Komma trennte, erzeugte aus einer Modellabweichung stillschweigend eine
    Begriffsliste, die niemand geliefert hat.
    """
    # ── Eingabe-Validierung ─────────────────────
    if roh is None:
        return []

    if isinstance(roh, str):
        einzeln: str = roh.strip()
        if not einzeln:
            return []
        logger.warning(
            "dateien: `begriffe` kam als Zeichenkette %r statt als Liste — als "
            "ein Begriff gelesen", einzeln[:60],
        )
        return [einzeln[:BEGRIFF_MAX_ZEICHEN]]

    if not isinstance(roh, list):
        logger.error(
            "dateien: `begriffe` ist %s statt einer Liste — verworfen; die "
            "Suche läuft dann über den dense Kanal", type(roh).__name__,
        )
        return []

    # ── Verarbeitung ────────────────────────────
    sauber: list[str] = []
    for eintrag in roh:
        if not isinstance(eintrag, str):
            logger.error(
                "dateien: Begriff %r ist %s statt einer Zeichenkette — verworfen",
                eintrag, type(eintrag).__name__,
            )
            continue
        wort: str = eintrag.strip()
        if not wort:
            continue
        if len(wort) > BEGRIFF_MAX_ZEICHEN:
            logger.warning(
                "dateien: Begriff mit %d Zeichen gekappt auf %d — was länger "
                "ist, ist ein Satzfragment", len(wort), BEGRIFF_MAX_ZEICHEN,
            )
            wort = wort[:BEGRIFF_MAX_ZEICHEN]
        sauber.append(wort)

    # ── Ausgabe-Verifikation ────────────────────
    if len(sauber) > BEGRIFFE_KAPPUNG:
        logger.info(
            "dateien: %d Begriffe auf %d gekappt — die Reihenfolge des Modells "
            "gilt, die tragenden stehen vorn", len(sauber), BEGRIFFE_KAPPUNG,
        )
        sauber = sauber[:BEGRIFFE_KAPPUNG]

    return sauber


def _build_classify_prompt(session_turns: str | None = None) -> str:
    """Baut den Klassifikations-System-Prompt aus den Blöcken.

    Vorbedingung: die vier Blöcke liegen in `PROMPTS`.
    Nachbedingung: nichtleerer Text mit [IDENTITAET], [AUFGABE], optional
    [KONTEXT], [FACHSPRACHE] und [REGELN].
    """
    aktionen_text: str = " | ".join(f'"{a}"' for a in sorted(GUELTIGE_AKTIONEN))

    bloecke: list[str] = [
        PROMPTS["classify_dateien.identity"].format(),
        PROMPTS["classify_dateien.task"].format(aktionen_text=aktionen_text),
    ]

    if session_turns:
        bloecke.append(
            "[KONTEXT]\n"
            "Nutze den Verlauf zur Kontext-Auflösung — besonders bei "
            "'lies mir den nächsten Abschnitt' oder 'und was steht da noch'.\n"
            f"\n{session_turns}"
        )

    bloecke.append(PROMPTS["classify_dateien.fachsprache"].format())
    bloecke.append(PROMPTS["classify_dateien.rules"].format())

    return "\n\n".join(bloecke)


def klassifizieren(state: AgentState) -> dict:
    """Bestimmt Aktion, Namensmuster, Begriffe, Abschnitt und Nadel.

    Vorbedingung: `state["aufgabe"]` trägt die Äußerung; `kontext` trägt
    `user_id` und `character_id`.
    Nachbedingung: `parameter["action"]` liegt in GUELTIGE_AKTIONEN, oder der
    Status ist "fehler". **Kein Zurücksetzen auf einen Vorgabewert** — eine
    unbekannte Aktion ist eine defekte Modellantwort und wird gemeldet, nicht
    als `finden` ausgeführt.
    Fehlerfaelle: leere Äußerung, unbrauchbares JSON, Antwort ohne Objekt,
    Aktion außerhalb des Kanons — jeder Fall mit eigenem Schritt-Eintrag.
    """
    # ── Eingabe-Validierung ─────────────────────
    prompt: str = state["aufgabe"]
    user_id: str = state["kontext"].get("user_id", "")
    character_id: str = state["kontext"].get("character_id", "")

    if not prompt or not prompt.strip():
        logger.error(
            "dateien.klassifizieren: leere Aufgabe für (%s x %s) — es gibt "
            "nichts zu klassifizieren", user_id, character_id,
        )
        return {
            "status": "fehler",
            "fehler": "Leere Äußerung — nichts zu klassifizieren.",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": "leere_aufgabe"}
            ],
        }

    logger.info(
        "dateien.klassifizieren: Einstieg — prompt='%s', user_id='%s'",
        prompt[:80], user_id,
    )

    # ── Verarbeitung ────────────────────────────
    session_turns: str | None = None
    if user_id:
        try:
            rohe_turns: list[dict] = session_turns_retrieve(
                redis_client, user_id, character_id,
            )
            session_turns = format_session_turns_numbered(rohe_turns, max_turns=5) or None
        except Exception as fehler:  # noqa: BLE001 — Kontext ist Zubehör, nicht Bedingung
            logger.warning(
                "dateien.klassifizieren: Session-Kontext fehlt (%s: %s) — es "
                "wird ohne Verlauf klassifiziert",
                type(fehler).__name__, fehler,
            )

    system_prompt: str = _build_classify_prompt(session_turns)
    node_cfg: dict = get_node_config("router")

    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": prompt}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "agent/dateien/klassifikation",
    )

    try:
        antwort = model_service.chat.submit_sync(chat_request)
        ergebnis: dict = antwort.parsed
    except (json.JSONDecodeError, KeyError, AttributeError) as fehler:
        logger.exception(
            "%s: dateien.klassifizieren: Modellantwort unbrauchbar",
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
            "dateien.klassifizieren: Modellantwort ist %s statt dict — verworfen",
            type(ergebnis).__name__,
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
            "dateien.klassifizieren: Aktion %r nicht im Kanon %s — verworfen "
            "statt ersetzt; ein Vorgabewert machte hier eine defekte Antwort "
            "von einer gültigen ununterscheidbar",
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
        logger.info("dateien.klassifizieren: REJECTED — %s", grund)
        return {
            "parameter": {**state["parameter"], "action": "rejected", "grund": grund},
            "status": "rejected",
            "schritte": state["schritte"] + [
                {"node": "klassifizieren", "ergebnis": f"rejected/{grund[:60]}"}
            ],
        }

    name: str = (ergebnis.get("name", "") or "").strip()
    abschnitt: str = (ergebnis.get("abschnitt", "") or "").strip()
    nadel: str = (ergebnis.get("nadel", "") or "").strip()
    begriffe: list[str] = _begriffe_pruefen(ergebnis.get("begriffe"))
    normalisiert: str = (ergebnis.get("normalisiert", "") or "").strip()

    # Ein Auftrag ohne jeden Suchschlüssel ist zulässig und nicht leer: Der
    # dense Kanal sucht dann mit dem `such_vektor` des Turns über den ganzen
    # Bestand (§6.3). Er wird gemeldet, weil er die teuerste Suche ist —
    # nicht abgewiesen, weil er die einzige ist, die eine Umschreibung findet.
    if not name and not begriffe and not nadel:
        logger.info(
            "dateien.klassifizieren: kein scharfer Schlüssel — die Suche läuft "
            "über den dense Kanal des ganzen Bestandes"
        )

    logger.info(
        "dateien.klassifizieren: action='%s', name='%s', begriffe=%s, "
        "abschnitt='%s', nadel='%s'",
        action, name[:40], begriffe, abschnitt[:40], nadel[:40],
    )

    return {
        "parameter": {
            **state["parameter"],
            "action": action,
            "name": name,
            "begriffe": begriffe,
            "abschnitt": abschnitt,
            "nadel": nadel,
            "normalisiert": normalisiert,
        },
        "schritte": state["schritte"] + [
            {"node": "klassifizieren",
             "ergebnis": f"{action}/{(name or ' '.join(begriffe))[:40]}"}
        ],
    }
