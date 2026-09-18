"""Der Ausgang einer Schreibung folgt ihrer Verifikation.

**Der Defekt, den dieser Baustein abloest** (`DIENST-MELDET-ABGESCHLOSSEN-OHNE-
VERIFIKATION`): Die Empfangsdienste pruefen nach jedem Schreiben, ob die Zeile
wirklich dasteht — und meldeten danach unbedingt `abgeschlossen`. Das Ergebnis
der Pruefung stand nur in `schritte` und im INFO-Log. Der Riegel aus Scheibe 12 A
liest den Status als Deckung; eine gescheiterte Schreibung deckte damit die
Behauptung, sie sei erfolgt. `[gemessen 17.09.2026, Betrieb]` Die Timeline
meldete `abgeschlossen`, und in `timeline` stand keine Zeile.

Die Konvention verlangt es seit langem anders (`novaberg-convention-nmcp.md`
§6.6/§6.7): **Ein Dienst meldet, was seine eigene Verifikation ergab.**
"""

import logging

logger = logging.getLogger("ki_server.agents.write_outcome")

# Was der Nutzer hoert, wenn die Schreibung nicht bestaetigt ist. Kein
# Erfolgssatz: Der Verfasser liest `ergebnis`, und ein "eingetragen" an dieser
# Stelle waere genau die Zusage, die der Defekt ausgab.
_NOT_CONFIRMED: str = "Die Speicherung liess sich nicht bestaetigen"


def verified_outcome(result: dict, verified: bool) -> dict:
    """Setzt den Ausgang einer Schreibung nach ihrer Verifikation.

    Vorbedingung: `result` ist die Rueckgabe eines Schreibpfads mit
        `status == "abgeschlossen"` und `ergebnis`; `verified` ist das Ergebnis
        der Pruefung, die der Dienst nach dem Schreiben gerechnet hat.
    Nachbedingung: `verified` — `result` unveraendert. Sonst eine Kopie mit
        `status = "fehler"`, einer Begruendung in `fehler`, die den
        urspruenglichen Satz als Beleg nennt, und einem `ergebnis`, das nichts
        zusagt; `schritte` bleiben, samt `verifiziert: False`.
    Fehlerfaelle: Ein `result` ohne `abgeschlossen` wird unveraendert
        zurueckgegeben und laut gemeldet — dieser Baustein entscheidet nur
        ueber Erfolg, nicht ueber Rueckfragen oder Ablehnungen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(result, dict) or result.get("status") != "abgeschlossen":
        logger.error("Schreibausgang: kein abgeschlossener Ausgang zu pruefen (%r) — unveraendert",
                     result.get("status") if isinstance(result, dict) else type(result).__name__)
        return result
    if verified is True:
        return result

    # ── Verarbeitung ────────────────────────────
    behauptet: str = str(result.get("ergebnis") or "")
    ausgang: dict = {
        **result,
        "status":   "fehler",
        "fehler":   f"Schreibung nicht bestaetigt (Verifikation fehlgeschlagen) — gemeldet waere: {behauptet[:200]}",
        "ergebnis": _NOT_CONFIRMED,
    }

    # ── Ausgabe-Verifikation ────────────────────
    logger.error("Schreibausgang: Verifikation fehlgeschlagen — Status fehler statt abgeschlossen: %s",
                 behauptet[:120])
    return ausgang
