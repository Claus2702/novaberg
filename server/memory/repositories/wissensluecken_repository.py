"""Lesezugriff auf die Tabelle `wissensluecken` — Novas offene Fragen.

**Diese Tabelle hatte bis zum 08.09.2026 keinen Leser.** `[gemessen]` Alle
Zugriffe kamen aus ihrem eigenen Agenten, und beide dienten der
Dublettenvermeidung: ein Wink an das Modell, welche Themen schon erfasst
sind, und die Nachbarsuche im Embedding-Raum. **1782 Zeilen, ausnahmslos
`offen`**, aelteste vom 27.07.2026.

**Warum das mehr ist als eine ungenutzte Tabelle.** Der Eintrag
`LUECKEN-WERDEN-NIE-GESCHLOSSEN` sagt, der Erkenntniszyklus arbeite *„gegen
eine Menge, die seine eigene Arbeit nie kleiner macht"*. Er arbeitet gar
nicht gegen sie. Und *geschlossen* ist ohne Verwender nicht bestimmbar: Es
hiesse *„Nova weiss es jetzt"*, und das kann nur feststellen, wer die Luecke
zum Lernen benutzt hat. **Der fehlende Leser ist die Ursache, der nie
gesetzte Status die Folge.**

**Nicht zu verwechseln mit `ei/wissensluecken.py`.** Das ist die *Turn*-Luecke
aus GV4 — semantisch nahe Konzepte, die im laufenden Gespraech noch nicht
gefallen sind, gueltig fuer einen Turn. Diese Tabelle traegt den **Zug zu
einem Thema ueber den Turn hinaus**. Der Namens- und Zustandsvermerk in
`novaberg-thinking-curiosity_k.md` trennt beide ausdruecklich; sie sind
schon einmal verwechselt worden, und der Vermerk selbst tut es in seinem
Fliesstext ein zweites Mal.
"""

import logging
from typing import Any

from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.memory.wissensluecken")

#: Wie viele offene Fragen hoechstens in einen Turn gehen.
#:
#: **Eine Anzahl und keine Schwelle, und das ist der ganze Punkt.** Eine
#: Schwelle auf `neugier_vektor` waere gegen eine Skala gesetzt, die ihren
#: Wertebereich zu 20 % nutzt (0,0102 bis 0,1148 bei Spanne [0 … 0,5],
#: `[gemessen 08.09.2026]`). Genau daran waere `TRAUM_NEUGIER_SCHWELLE` aus
#: dem Konzept gescheitert: Mit 0,25 haette sie **kein einziges Mal**
#: ausgeloest. Eine Anzahl braucht die Skala nicht zu kennen — sie nimmt die
#: staerksten, welchen Betrag sie auch tragen.
LUECKEN_JE_TURN: int = 3


def staerkste_luecken(
    user_id: str, character_id: str, deckel: int = LUECKEN_JE_TURN,
) -> list[dict[str, Any]]:
    """Die offenen Fragen mit dem staerksten Zug, fuer dieses Paar.

    Vorbedingung: `user_id` und `character_id` sind gesetzt. Ein leeres Paar
        ist ein Aufruffehler — die Tabelle ist paargebunden, und eine
        Abfrage ohne Paar liefert fremde Fragen.
    Nachbedingung: Hoechstens `deckel` Zeilen, absteigend nach
        `neugier_vektor`, nur mit Status `offen`. Eine leere Liste ist ein
        gueltiges Ergebnis und kein Fehler.
    Fehlerfaelle: Ein Datenbankfehler wird gemeldet und als leere Liste
        weitergereicht — eine ausgefallene Nebenangabe darf den Turn nicht
        toeten. **Sie wird dabei laut**, damit ein dauerhafter Ausfall nicht
        wie ein leerer Bestand aussieht.

    Args:
        user_id: der Mensch des Paares.
        character_id: die Figur des Paares.
        deckel: Hoechstzahl der gelieferten Zeilen.

    Returns:
        Je Zeile `thema`, `neugier_vektor`, `neuheit`, `resonanz`,
        `herkunft` und das Alter in Tagen.

    Raises:
        ValueError: bei leerem Paar oder nicht positivem Deckel.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        raise ValueError(
            f"staerkste_luecken: Paar unvollstaendig "
            f"(user_id={user_id!r}, character_id={character_id!r}) — "
            "die Tabelle ist paargebunden"
        )
    if deckel <= 0:
        raise ValueError(f"staerkste_luecken: deckel={deckel} muss positiv sein")

    # ── Verarbeitung ────────────────────────────
    try:
        zeilen: list[dict] = db_manager.select(
            """
            SELECT thema, neugier_vektor, neuheit, resonanz, herkunft,
                   EXTRACT(DAY FROM NOW() - erstellt_am)::int AS alter_tage
              FROM wissensluecken
             WHERE user_id = %s AND character_id = %s AND status = 'offen'
             ORDER BY neugier_vektor DESC
             LIMIT %s
            """,
            (user_id, character_id, deckel),
        )
    except Exception as fehler:
        logger.error(
            "Wissensluecken: Abfrage der staerksten Fragen fehlgeschlagen "
            "(%s: %s) — der Turn laeuft ohne sie weiter, aber ein "
            "dauerhafter Ausfall sieht hier aus wie ein leerer Bestand",
            type(fehler).__name__, fehler,
        )
        return []

    # ── Ausgabe-Verifikation ────────────────────
    if len(zeilen) > deckel:
        raise RuntimeError(
            f"staerkste_luecken: {len(zeilen)} Zeilen bei Deckel {deckel} — "
            "das LIMIT hat nicht gegriffen"
        )

    logger.info(
        "Wissensluecken: %d offene Frage(n) fuer %s/%s gelesen (Zug %s)",
        len(zeilen), user_id, character_id,
        ", ".join(f"{z['neugier_vektor']:.4f}" for z in zeilen) or "—",
    )
    return zeilen
