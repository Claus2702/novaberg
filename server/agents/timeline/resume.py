"""Resume-Node — Loest User-Antworten auf Rueckfragen auf.

Zwei Szenarien, beide schreiben nie:
  1. Disambiguierung (mehrere Termin-Kandidaten auf dem Weg mit Titel): Die
     Antwort waehlt nicht, sie fuehrt zu einer Klaerung, die die Kandidaten
     mit Datum nennt und sagt, dass zwischen ihnen noch nicht gewaehlt wird.
  2. Klaerung (`clarification`): Aendern, Loeschen oder Verschieben ohne
     Titel fand im Zeitraum keinen, einen oder mehrere Termine.
Kein Duplikat-Szenario wie bei Notizen — gleiche Titel sind bei Terminen normal.
"""

import json
import logging

from agents.base import AgentState

logger = logging.getLogger("ki_server.agents.timeline.resume")


def resume_clarification(state: AgentState) -> dict:
    """Die Antwort auf die Klaerung *„… Sag mir mit seinem Namen, ob ich ihn loeschen soll.“*.

    Die Klaerung folgt auf Aendern, Loeschen oder Verschieben ohne Titel, bei
    keinem, einem oder mehreren Treffern im Zeitraum. Auch ein *„Ja“* oder
    *„den zweiten“* darauf schreibt nicht: Eine Antwort, die nur zustimmt oder
    waehlt, liest sich nicht sicher genug. Der Auftrag endet ohne Schreiben und
    sagt, wie er gegeben werden muss; ein neuer Auftrag mit Titel geht den Weg
    mit Titel.

    Vorbedingung: `parameter["clarification"]` ist gesetzt.
    Nachbedingung: `status` `abgeschlossen` ohne `termin` — nichts wird
        geschrieben.
    Fehlerfaelle: ein Zustand ohne `clarification` wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    parameter: dict = state["parameter"]
    if not parameter.get("clarification"):
        msg: str = "resume_clarification: keine Klaerung offen"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    answer: str = str(parameter.get("user_answer", ""))
    sentence: str = (
        "Ich habe nichts geändert. Nenn mir den Termin mit seinem Namen, "
        "dann suche ich ihn."
    )

    # ── Ausgabe-Verifikation ────────────────────
    if "termin" in parameter:
        msg = f"resume_clarification: Klaerung traegt einen Termin {parameter['termin']!r}"
        raise RuntimeError(msg)
    logger.info(f"resume: Antwort auf die Klaerung — nichts geschrieben ('{answer[:60]}')")
    return {
        "status": "abgeschlossen",
        "ergebnis": sentence,
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "klaerung_beantwortet"}],
    }


def _failed(state: AgentState, text: str, outcome: str) -> dict:
    """Ein `fehler` des Resume-Knotens mit Schritt im Audit-Trail.

    Vorbedingung: `text` und `outcome` sind nicht leer.
    Nachbedingung: `status` `fehler`, `fehler` ist `text`.
    Fehlerfaelle: ein leerer Text wirft `ValueError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not text or not outcome:
        msg: str = "_failed: leerer Fehlertext oder Ausgang"
        raise ValueError(msg)

    # ── Verarbeitung ────────────────────────────
    result: dict = {
        "status": "fehler",
        "fehler": text,
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": outcome}],
    }

    # ── Ausgabe-Verifikation ────────────────────
    if result["fehler"] != text:
        msg = "_failed: Fehlertext nicht uebernommen"
        raise RuntimeError(msg)
    return result


def resume(state: AgentState) -> dict:
    """Loest die User-Antwort auf eine Rueckfrage auf."""
    user_answer = state["parameter"].get("user_answer", "")
    rueckfrage = state["parameter"].get("original_rueckfrage", "")
    action = state["parameter"].get("action", "")

    logger.debug(f"resume: Einstieg — action='{action}', user_answer='{user_answer[:80]}', "
                 f"rueckfrage='{rueckfrage[:80]}'")

    # Aendern, Loeschen und Verschieben ohne Titel: die Klaerung schreibt nie,
    # gestellt wird sie von period_question in suche.py
    if state["parameter"].get("clarification"):
        return resume_clarification(state)

    # Disambiguierung-JSON parsen
    try:
        disamb = json.loads(rueckfrage)
        if disamb.get("typ") == "disambiguierung":
            return _resume_disambiguierung(state, disamb, user_answer)
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: Konnte Rueckfrage-Typ nicht erkennen
    logger.warning(f"resume: Unbekannter Rueckfrage-Typ — rueckfrage='{rueckfrage[:100]}'")
    return {
        "status": "fehler",
        "fehler": "Konnte die Rueckfrage-Antwort nicht zuordnen.",
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "unbekannt"}],
    }


def _resume_disambiguierung(state: AgentState, disamb: dict, user_answer: str) -> dict:
    """Die Antwort auf eine Auswahl: eine Klaerung, nie ein Schreiben.

    ~~Die Antwort waehlte einen Kandidaten und schrieb~~ → seit dem 17.10.2026
    klaert sie. Bei der Auswahl mit Titel tragen alle Kandidaten denselben
    Titel; *„den Zahnarzt am 9.“* traf so den ersten Kandidaten, dessen Titel
    in der Antwort stand, und Ziffern wurden als Teilzeichenkette gelesen.
    Geschrieben wurde still am falschen Termin. Die Klaerung nennt jeden
    Kandidaten mit Datum und sagt, dass Nova zwischen ihnen noch nicht waehlen
    kann. Sie verspricht keinen Weg: Ein Datum im neuen Auftrag grenzt die
    Suche nach dem Titel nicht ein, und beim Verschieben ist es die neue Zeit.

    Vorbedingung: `disamb["kandidaten"]` ist eine nicht leere Liste, jeder
        Kandidat traegt `title` und `datum`.
    Nachbedingung: `status` `abgeschlossen` ohne `parameter` — nichts wird
        gelesen oder geschrieben; sonst `fehler` ohne `parameter`.
    Fehlerfaelle: keine Kandidaten oder ein Kandidat ohne Titel oder Datum
        ergeben `fehler` mit ERROR; ein Text, der einen Kandidaten nicht nennt,
        wirft `RuntimeError`.
    """
    # ── Eingabe-Validierung ─────────────────────
    candidates: object = disamb.get("kandidaten")
    if not isinstance(candidates, list) or not candidates:
        logger.error(f"resume: Auswahl ohne Kandidaten — nichts geschrieben, {disamb}")
        return _failed(state, "Keine Kandidaten in der Disambiguierung.", "keine_kandidaten")
    if any(not c.get("title") or not c.get("datum") for c in candidates):
        logger.error(f"resume: Kandidat ohne Titel oder Datum — nichts geschrieben, {candidates}")
        return _failed(state, "Die Auswahl laesst sich keinem Termin zuordnen.", "defekt")

    # ── Verarbeitung ────────────────────────────
    lines: str = "\n".join(f"- {c['title']} am {c['datum']}" for c in candidates)
    sentence: str = (
        f"Ich habe nichts geändert. Gefunden hatte ich diese Termine:\n{lines}\n"
        "Zwischen ihnen kann ich noch nicht wählen, auch nicht über ein Datum im Auftrag."
    )

    # ── Ausgabe-Verifikation ────────────────────
    if any(f"{c['title']} am {c['datum']}" not in sentence for c in candidates):
        msg: str = f"_resume_disambiguierung: {sentence!r} nennt nicht jeden Kandidaten"
        raise RuntimeError(msg)
    logger.info(
        f"resume: Antwort auf die Auswahl ({len(candidates)} Kandidaten) — nichts geschrieben "
        f"('{user_answer[:60]}')"
    )
    return {
        "status": "abgeschlossen",
        "ergebnis": sentence,
        "schritte": state["schritte"] + [{"node": "resume", "ergebnis": "auswahl_beantwortet"}],
    }
