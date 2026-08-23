"""Die Zuordnung — in welche vorhandene Wissensdatei ein Fund gehört.

Spezifikation: docs/novaberg-agent-dateien_k.md §4a, §4a.1, §4b.1a.

**Die Frage ist keine Ähnlichkeitsfrage, und deshalb steht hier keine
Schwelle.** Ein Embedding misst Wortwahl, nicht Zugehörigkeit: *„Napoleons
Feldzüge in Ägypten"* liegt näher an einer Napoleon-Datei, weil *„Feldzüge"*
lexikalisch ein Napoleon-Wort ist — das ist eine Aussage über den
Sprachgebrauch und keine darüber, wohin das Wissen gehört.

**Das Kriterium ist Pflegbarkeit** (§4a.1): Die richtige Datei ist die, in der
der Fund zusammen mit verwandtem Material gepflegt werden kann. Darüber
entscheidet ein Modellaufruf über die **Zusammenfassungen** der Kandidaten —
nicht ein Kosinus über ihre Vektoren.

**Der Vektor bleibt trotzdem im Spiel, aber eine Stufe früher:** Er bildet die
Kandidatenmenge, damit der Aufruf nicht alle Dateien der Bibliothek sehen
muss. Wer die Auswahl dem Vektor überließe, hätte genau die Bauart gebaut, die
§4a widerlegt.
"""

import json
import logging

from config import PROMPTS, get_node_config
from memory.repositories.autonomous_wissen_repository import BIBLIOTHEK_BEOBACHTER
from memory.utils import embedding_zu_pgvector_str
from services.model_services import ChatRequest, model_service
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.wissen_rueckweg.zuordnung")

#: Wie viele Dateien dem Aufruf vorgelegt werden. Die Zahl ist eine
#: Platzfrage und keine Messfrage: Jeder Kandidat kostet seine
#: Zusammenfassung im Prompt, und ein Planer, der zwanzig Themen gegeneinander
#: hält, entscheidet nicht besser, sondern länger.
KANDIDATEN_KAPPUNG: int = 8

#: Kappung der Zusammenfassung je Kandidat. Sie ist die Entscheidungsgrundlage
#: und wird deshalb großzügiger gekappt als eine Fundstelle.
ZUSAMMENFASSUNG_KAPPUNG: int = 600


def kandidaten_laden(
    user_id: str, character_id: str, embedding: list[float],
    ausschluss_id: int | None = None,
) -> list[dict]:
    """Lädt die nächstliegenden Wissensdateien des Paares — die Vorauswahl.

    Vorbedingung: `embedding` ist der Vektor des Fundes; beide Kennungen des
    Paares liegen vor.
    Nachbedingung: Höchstens `KANDIDATEN_KAPPUNG` aktive Zeilen vom Typ
    `wissen`, jede mit `id`, `dateipfad`, `thema`, `zusammenfassung` und
    `kosinus`. Leer heißt: Die Bibliothek des Paares trägt nichts, wozu dieser
    Fund passen könnte.
    Fehlerfaelle: unvollständiges Paar oder fehlender Vektor werden gemeldet
    und ergeben eine leere Liste; ein Datenbankfehler ebenso.

    **Diese Funktion wählt nicht aus, sie schlägt vor.** Der Kosinus ordnet die
    Vorlage; die Entscheidung trifft `ziel_bestimmen` über die
    Zusammenfassungen.

    **`ausschluss_id` hält die eigene Zeile heraus, und ohne sie wäre der
    Verweis ein Selbstläufer.** Der Recherche-Weg legt Sekunden vor dem
    Auftrag eine Zeile mit genau der Zusammenfassung an, aus der das Material
    des Verweises stammt: Sie wäre der nächste Kandidat, mit Kosinus nahe
    eins, und jedes Ergebnis verstärkte seine eigene Zeile. Ein Ausschluss,
    der ins Leere zeigt, kostet einen Kandidaten zu viel und sonst nichts —
    deshalb steht hier kein Fremdschlüssel (`F-VERFALL-1` b).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        logger.error(
            "Rückweg-Zuordnung: unvollständiges Paar (user_id=%r, character_id=%r) "
            "— keine Kandidaten", user_id, character_id,
        )
        return []
    if not embedding:
        logger.error(
            "Rückweg-Zuordnung: kein Vektor für den Fund — ohne ihn gibt es "
            "keine Vorauswahl, und alle Dateien vorzulegen wäre keine"
        )
        return []

    # ── Verarbeitung ────────────────────────────
    vektor_str: str = embedding_zu_pgvector_str(embedding)
    try:
        zeilen: list[dict] = db_manager.select(
            "SELECT id, dateipfad, thema, zusammenfassung, haeufigkeit, "
            "       1 - (themen_embedding <=> %s::vector) AS kosinus "
            "FROM   autonomous_wissen "
            "WHERE  user_id = %s AND character_id = %s "
            "  AND  beobachter = %s "
            "  AND  typ = 'wissen' AND aktiv = TRUE "
            "  AND  themen_embedding IS NOT NULL "
            "  AND  (%s::int IS NULL OR id <> %s::int) "
            "ORDER  BY themen_embedding <=> %s::vector LIMIT %s",
            (vektor_str, user_id, character_id, BIBLIOTHEK_BEOBACHTER,
             ausschluss_id, ausschluss_id, vektor_str, KANDIDATEN_KAPPUNG),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Rückweg-Zuordnung: Kandidatenabfrage fehlgeschlagen",
            type(fehler).__name__,
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    for zeile in zeilen:
        zeile["kosinus"] = round(float(zeile.get("kosinus") or 0.0), 4)
    logger.info(
        "Rückweg-Zuordnung: %d Kandidaten für (%s x %s)%s, bester Kosinus %s",
        len(zeilen), user_id, character_id,
        f", Zeile {ausschluss_id} ausgeschlossen" if ausschluss_id else "",
        zeilen[0]["kosinus"] if zeilen else "—",
    )
    return zeilen


def _vorlage_bauen(kandidaten: list[dict]) -> str:
    """Formt die Kandidatenliste für den Prompt.

    Vorbedingung: `kandidaten` stammt aus `kandidaten_laden`.
    Nachbedingung: Ein Text mit einer nummerierten Zeile je Kandidat; die
    Nummer ist die **Datenbank-ID**, damit die Antwort ohne Umrechnung
    zuordenbar ist.
    """
    zeilen: list[str] = []
    for kandidat in kandidaten:
        zusammenfassung: str = (kandidat.get("zusammenfassung") or "").strip()
        zeilen.append(
            f"[{kandidat['id']}] {kandidat.get('thema', '(ohne Thema)')}\n"
            f"     {zusammenfassung[:ZUSAMMENFASSUNG_KAPPUNG]}"
        )
    return "\n".join(zeilen)


def ziel_bestimmen(
    fund: str, kandidaten: list[dict], *, verweis: bool = False,
) -> dict | None:
    """Entscheidet über die Zieldatei — oder ausdrücklich über keine.

    Vorbedingung: `fund` ist nicht leer; `kandidaten` ist nicht leer.
    `verweis` sagt, welche der beiden Fragen gestellt wird.
    Nachbedingung: Ein Wörterbuch mit `ziel` (ein Kandidat oder None),
    `begruendung` und `kern` — oder None, wenn der Aufruf unbrauchbar war.
    **`ziel=None` bei gesetzter Begründung ist ein Ergebnis und kein
    Fehlschlag**: „passt nirgends" ist die häufigere und die billigere
    Antwort, und eine erzwungene Zuordnung verschmutzt die Datei, die sie
    trifft (§4a.2).
    Fehlerfaelle: unbrauchbares JSON, Antwort ohne Objekt, eine Nummer
    außerhalb der Vorlage — jeder Fall wird gemeldet und ergibt None.

    **Zwei Zettel, kein Bedingungsblock.** Die beiden Wege stellen entgegen-
    gesetzte Fragen: Der Schnitt fragt, wo der Fund *gepflegt* werden kann,
    und verwirft ihn, wenn er dort schon steht — eine Wiederholung ist kein
    Zuwachs. Der Verweis fragt, welche Datei das Thema *führt*, und für ihn
    ist genau diese Wiederholung die **Bestätigung**. Beides in einen Zettel
    zu schreiben legte dem Modell zwei Regeln vor, die sich widersprechen;
    zwei Regeln, die dasselbe verneinen und bejahen, heben sich in der
    Wirkung auf (`F-PROMPT-1`).

    `[gemessen]` — 19.08.2026, fünfter echter Lauf: bester Kosinus **0,9226**,
    und die Ablehnung lautete *„exakte textliche Wiederholung … kein
    Wissenszuwachs"*. Der Verweis lehnte damit seinen besten Fall ab: Je
    besser die Zuordnung, desto sicherer die Ablehnung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not fund.strip():
        logger.error("Rückweg-Zuordnung: leerer Fund — nichts zuzuordnen")
        return None
    if not kandidaten:
        logger.info(
            "Rückweg-Zuordnung: keine Kandidaten — die Bibliothek des Paares "
            "trägt nichts, wozu dieser Fund passen könnte"
        )
        return None

    # ── Verarbeitung ────────────────────────────
    familie: str = "verweis_zuordnung" if verweis else "rueckweg_zuordnung"
    system_prompt: str = "\n\n".join([
        # Die Identität ist beiden gemeinsam: zuordnen, nicht formulieren.
        PROMPTS["rueckweg_zuordnung.identity"].format(),
        PROMPTS[f"{familie}.task"].format(),
        PROMPTS[f"{familie}.rules"].format(),
    ])
    node_cfg: dict = get_node_config("router")

    nachricht: str = (
        f"FUND:\n{fund.strip()}\n\n"
        f"VORHANDENE WISSENSDATEIEN:\n{_vorlage_bauen(kandidaten)}"
    )

    try:
        antwort = model_service.chat.submit_sync(ChatRequest(
            messages          = [{"role": "user", "content": nachricht}],
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.05),
            expect_json       = True,
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "agent/wissen_rueckweg/zuordnung",
        ))
        ergebnis: dict = antwort.parsed
    except (json.JSONDecodeError, KeyError, AttributeError) as fehler:
        logger.exception(
            "%s: Rückweg-Zuordnung: Modellantwort unbrauchbar", type(fehler).__name__,
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(ergebnis, dict):
        logger.error(
            "Rückweg-Zuordnung: Modellantwort ist %s statt dict — verworfen",
            type(ergebnis).__name__,
        )
        return None

    begruendung: str = (ergebnis.get("begruendung", "") or "").strip()
    kern: str = (ergebnis.get("kern", "") or "").strip()
    ziel_id = ergebnis.get("ziel")

    if ziel_id is None:
        logger.info(
            "Rückweg-Zuordnung: keine Datei passt — %s",
            begruendung or "ohne Begründung",
        )
        return {"ziel": None, "begruendung": begruendung, "kern": kern}

    nach_id: dict[int, dict] = {int(k["id"]): k for k in kandidaten}
    try:
        gewaehlt: dict | None = nach_id.get(int(ziel_id))
    except (TypeError, ValueError):
        logger.exception(
            "Rückweg-Zuordnung: `ziel` ist %r und keine Nummer — verworfen "
            "statt geraten; eine falsche Datei ist teurer als keine", ziel_id,
        )
        return None

    if gewaehlt is None:
        logger.error(
            "Rückweg-Zuordnung: Nummer %r steht nicht in der Vorlage %s — "
            "verworfen", ziel_id, sorted(nach_id),
        )
        return None

    if not kern:
        logger.error(
            "Rückweg-Zuordnung: Ziel '%s' gewählt, aber `kern` ist leer — ohne "
            "Gehalt gibt es nichts einzuarbeiten", gewaehlt["dateipfad"],
        )
        return None

    logger.info(
        "Rückweg-Zuordnung: → %s (Kosinus %s) — %s",
        gewaehlt["dateipfad"], gewaehlt.get("kosinus"), begruendung[:100],
    )
    return {"ziel": gewaehlt, "begruendung": begruendung, "kern": kern}
