"""Woher der Text kommt, der eingearbeitet wird — roh vor verdichtet.

Spezifikation: docs/novaberg-agent-dateien_k.md §4b.1b, §4b.3 · §9 Punkt 9.

**Entschieden am 18.08.2026: es wird die ROHE Fassung eingearbeitet.** Der
Grund ist der Platz und nicht die Sparsamkeit — `turn_roh` ist von der
Aufräumfrist ausgenommen und bleibt dauerhaft, während der Kurzzeit-Eintrag
nach 7 bis 30 Tagen verfällt. Und §4b.3 wiegt schwerer als der Preis je
Aufruf: Wer das Destillat einarbeitet, legt ein Destillat auf ein Destillat.

**Die Rohfassung ist über den Turn adressiert, und dieses Glied fehlte.** Der
Kurzzeit-Eintrag trug seinen `turn_id` nicht mit; er wurde beim Anlegen
übergeben und nur ins Protokoll geschrieben. Seit dem 18.08.2026 steht er im
Hash — für Einträge, die davor entstanden sind, gibt es ihn nicht.

> **Der Rückfall ist deshalb erlaubt und wird benannt.** Ein Eintrag ohne
> `turn_id` wird mit seiner verdichteten Fassung eingearbeitet, und das
> Ergebnis trägt `quelle="verdichtet"`. Ohne diese Marke wäre am Ende nicht
> mehr zu sehen, welcher Absatz aus dem Wortlaut stammt und welcher aus einer
> Zusammenfassung — und genau diese Unterscheidung ist der Gegenstand der
> Entscheidung.
"""

import json
import logging

from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.wissen_rueckweg.herkunft")

#: Die beiden Herkünfte des eingearbeiteten Textes. Geschlossene Menge.
QUELLE_ROH: str = "roh"
QUELLE_VERDICHTET: str = "verdichtet"

#: Kappung des Rohtextes. Ein Turn trägt Frage und Antwort; was darüber
#: hinausgeht, ist für die Einarbeitung eines Fundes kein Material mehr,
#: sondern Kontext, den der nächste Schritt ohnehin wegwirft.
ROHTEXT_KAPPUNG: int = 6000


def rohfassung_holen(turn_id: str, user_id: str, character_id: str) -> str:
    """Holt das Reiz-Reaktions-Paar des Turns aus dem dauerhaften Protokoll.

    Vorbedingung: `turn_id` ist die Kennung des Turns, aus dem der Eintrag
    stammt; das Paar ist vollständig.
    Nachbedingung: Ein Text aus Äußerung und Antwort — oder eine leere
    Zeichenkette, wenn die Zeile fehlt. **Leer ist eine Auskunft** und führt
    beim Aufrufer zum Rückfall auf die verdichtete Fassung.
    Fehlerfaelle: Datenbankfehler werden gemeldet und ergeben eine leere
    Zeichenkette.

    **Die Paarbedingung steht in der Abfrage und nicht im Vertrauen.** Ein
    `turn_id` ist eindeutig; wäre er es nicht, käme über diesen Weg fremdes
    Gesprächsmaterial in eine Wissensdatei.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turn_id.strip():
        logger.debug("Rückweg-Herkunft: kein turn_id — keine Abfrage")
        return ""
    if not user_id or not character_id:
        logger.error(
            "Rückweg-Herkunft: unvollständiges Paar (user_id=%r, character_id=%r) "
            "— keine Abfrage", user_id, character_id,
        )
        return ""

    # ── Verarbeitung ────────────────────────────
    try:
        zeilen: list[dict] = db_manager.select(
            "SELECT inhalt FROM pipeline_log "
            "WHERE turn_id = %s AND art = 'turn_roh' "
            "  AND user_id = %s AND character_id = %s "
            "ORDER BY id DESC LIMIT 1",
            (turn_id.strip(), user_id, character_id),
        )
    except Exception as fehler:
        logger.exception(
            "%s: Rückweg-Herkunft: Rohfassung zu '%s' nicht abrufbar",
            type(fehler).__name__, turn_id,
        )
        return ""

    if not zeilen:
        logger.info(
            "Rückweg-Herkunft: keine Rohfassung zu Turn '%s' — der Eintrag ist "
            "älter als das Mitschreiben des Turnbezugs", turn_id,
        )
        return ""

    # ── Ausgabe-Verifikation ────────────────────
    roh = zeilen[0].get("inhalt")
    if isinstance(roh, str):
        try:
            roh = json.loads(roh)
        except json.JSONDecodeError:
            logger.exception(
                "Rückweg-Herkunft: Rohfassung zu '%s' ist kein lesbares JSON", turn_id,
            )
            return ""

    if not isinstance(roh, dict):
        logger.error(
            "Rückweg-Herkunft: Rohfassung zu '%s' ist %s statt eines Objekts",
            turn_id, type(roh).__name__,
        )
        return ""

    prompt: str = (roh.get("user_prompt") or "").strip()
    antwort: str = (roh.get("response") or "").strip()
    if not prompt and not antwort:
        logger.error(
            "Rückweg-Herkunft: Rohfassung zu '%s' trägt weder Äußerung noch "
            "Antwort — als fehlend behandelt", turn_id,
        )
        return ""

    text: str = f"ÄUSSERUNG:\n{prompt}\n\nANTWORT:\n{antwort}".strip()
    logger.info(
        "Rückweg-Herkunft: Rohfassung zu '%s' — %d Zeichen", turn_id, len(text),
    )
    return text[:ROHTEXT_KAPPUNG]


def material_waehlen(
    turn_id: str, verdichtet: str, user_id: str, character_id: str,
) -> tuple[str, str]:
    """Wählt das Material der Einarbeitung: roh, sonst verdichtet.

    Vorbedingung: `verdichtet` ist der Text des Kurzzeit-Eintrags.
    Nachbedingung: Ein Paar aus Text und Herkunftsmarke aus
    {`QUELLE_ROH`, `QUELLE_VERDICHTET`}. Der Text ist nie leer, wenn
    `verdichtet` nicht leer war.
    Fehlerfaelle: keine eigenen — beide Wege melden selbst.

    **Die Marke reist mit, weil sie später die Frage beantwortet, die niemand
    mehr aus dem Text beantworten kann:** ob dieser Absatz aus dem Wortlaut
    entstand oder aus einer Zusammenfassung davon.
    """
    # ── Verarbeitung ────────────────────────────
    roh: str = rohfassung_holen(turn_id, user_id, character_id)
    if roh:
        return roh, QUELLE_ROH

    # ── Ausgabe-Verifikation ────────────────────
    logger.warning(
        "Rückweg-Herkunft: Rückfall auf die verdichtete Fassung (turn_id=%r) — "
        "das Ergebnis wird als '%s' gekennzeichnet und ist ein Destillat auf "
        "einem Destillat", turn_id, QUELLE_VERDICHTET,
    )
    return verdichtet.strip(), QUELLE_VERDICHTET


def herkunft_lesen(modus: str) -> str:
    """Liest die Herkunftsmarke aus dem `modus` des Queue-Auftrags.

    Vorbedingung: `modus` ist das Feld des Auftrags, gesetzt vom Auslöser als
    `rueckweg_<quelle>`.
    Nachbedingung: `QUELLE_ROH` oder `QUELLE_VERDICHTET`.
    Fehlerfaelle: Ein unbekannter oder fehlender Wert wird gemeldet und als
    `QUELLE_VERDICHTET` gelesen — **die vorsichtigere Lesart**: Wer die
    Rohfassung behauptet, ohne sie zu haben, macht ein Destillat unkenntlich;
    umgekehrt wird höchstens ein Wortlaut zu bescheiden gekennzeichnet.

    **Die Marke reist im `modus`, weil der Auftrag keine eigene Spalte dafür
    hat.** Eine anzulegen wäre eine Schemaänderung, und die wird angekündigt
    statt nebenbei gelegt. `modus` trägt die Lage, aus der ein Auftrag
    entstand — und genau das ist die Angabe.
    """
    # ── Eingabe-Validierung ─────────────────────
    wert: str = (modus or "").strip()
    if wert == f"rueckweg_{QUELLE_ROH}":
        return QUELLE_ROH
    if wert == f"rueckweg_{QUELLE_VERDICHTET}":
        return QUELLE_VERDICHTET

    # ── Ausgabe-Verifikation ────────────────────
    logger.error(
        "Rückweg-Herkunft: modus=%r nennt keine bekannte Herkunft — als '%s' "
        "gelesen; ein unmarkierter Wortlaut ist besser als ein Destillat, das "
        "sich als Wortlaut ausgibt", modus, QUELLE_VERDICHTET,
    )
    return QUELLE_VERDICHTET
