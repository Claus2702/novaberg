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
import math
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

#: Wie nah ein offenes Thema dem Reiz liegen muss, damit es in den Turn geht.
#:
#: **Gemessen, und zwar an der Statistik des Mechanismus** (12.09.2026). Paarung:
#: kurze Themenphrase gegen den Reiz. Der Leser waehlt unter **allen** Themen
#: ueber der Grenze nach Zug — also zaehlt der Anteil passender Themen je
#: Naehe-Band, nicht die hoechste Naehe je Turn. Gelesen an 64 Turns (60 Nutzer-
#: turns des Bestands, vier Impulse), zwoelf Paare je Band:
#:
#:     0,40–0,43  6/12 · 0,43–0,46  6/12 · 0,46–0,49  8/12 · 0,49–0,52  10/12 · ab 0,52  ~12/12
#:
#: **Die erste Eichung stand auf 0,41 und war falsch**: Sie nahm die hoechste
#: Naehe je Turn, die nur entscheidet, *ob* etwas kommt. Durch den gebauten
#: Leser gefahren kamen dann bei einem Impuls ueber Schwarze Loecher
#: *Orbitale Kognitions-Logik* (0,415) statt *Hawking-Entropie* (0,548) — rund
#: 60 % der waehlbaren Themen passten. Ab 0,49 sind es gut 90 %, und Fragen
#: kommen noch in etwa einem Drittel der Turns. Eine andere Paarung braucht
#: eine andere Zahl.
OFFENE_FRAGEN_MIN_NAEHE: float = 0.49


def staerkste_luecken(
    user_id: str,
    character_id: str,
    turn_embedding: list[float],
    deckel: int = LUECKEN_JE_TURN,
    min_naehe: float = OFFENE_FRAGEN_MIN_NAEHE,
) -> list[dict[str, Any]]:
    """Die offenen Fragen mit dem staerksten Zug **unter denen, die dem Turn nah sind**.

    **Seit dem 12.09.2026 zuerst nach Naehe, dann nach Zug** (`F-GV-2`). Bis dahin
    kamen die drei mit dem hoechsten Zug ueberhaupt — in 15 Betriebsturns
    dieselben drei in jedem Turn, und keine wurde je aufgegriffen, weil keine
    zum Gespraech passte. Eine leere Auswahl ist jetzt der Normalfall eines
    Turns, der Novas Themen nicht beruehrt.

    Vorbedingung: `user_id` und `character_id` sind gesetzt; `turn_embedding`
        ist der Vektor des Reizes — beim Nutzerturn seine Aeusserung, beim
        Impuls Novas Gedanke — und traegt nur endliche Zahlen.
    Nachbedingung: Hoechstens `deckel` Zeilen, alle mit Status `offen` und mit
        `naehe >= min_naehe`, absteigend nach `neugier_vektor`. Eine leere Liste
        ist ein gueltiges Ergebnis und kein Fehler.
    Fehlerfaelle: Ein Datenbankfehler wird gemeldet und als leere Liste
        weitergereicht — eine ausgefallene Nebenangabe darf den Turn nicht
        toeten. **Sie wird dabei laut**, damit ein dauerhafter Ausfall nicht
        wie ein leerer Bestand aussieht.

    Args:
        user_id: der Mensch des Paares.
        character_id: die Figur des Paares.
        turn_embedding: der Vektor des Reizes dieses Turns.
        deckel: Hoechstzahl der gelieferten Zeilen.
        min_naehe: Untergrenze der Cosinus-Naehe zwischen Thema und Reiz.

    Returns:
        Je Zeile `thema`, `neugier_vektor`, `neuheit`, `resonanz`,
        `herkunft`, das Alter in Tagen und die `naehe` zum Reiz.

    Raises:
        ValueError: bei leerem Paar, leerem oder ungueltigem Vektor, nicht
            positivem Deckel oder einer Naehe-Grenze ausserhalb [0, 1].
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        raise ValueError(
            f"staerkste_luecken: Paar unvollstaendig "
            f"(user_id={user_id!r}, character_id={character_id!r}) — "
            "die Tabelle ist paargebunden"
        )
    if not turn_embedding or any(
        isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
        for x in turn_embedding
    ):
        raise ValueError(
            f"staerkste_luecken: Turn-Vektor leer oder ungueltig "
            f"(Laenge {len(turn_embedding) if turn_embedding else 0}) — "
            "ohne Reiz ist keine Frage nah"
        )
    if deckel <= 0:
        raise ValueError(f"staerkste_luecken: deckel={deckel} muss positiv sein")
    if not 0.0 <= min_naehe <= 1.0:
        raise ValueError(f"staerkste_luecken: min_naehe={min_naehe} ausserhalb [0, 1]")

    # ── Verarbeitung ────────────────────────────
    vektor: str = "[" + ",".join(str(float(x)) for x in turn_embedding) + "]"
    try:
        zeilen: list[dict] = db_manager.select(
            """
            SELECT thema, neugier_vektor, neuheit, resonanz, herkunft,
                   EXTRACT(DAY FROM NOW() - erstellt_am)::int AS alter_tage,
                   1 - (embedding <=> %s::vector) AS naehe
              FROM wissensluecken
             WHERE user_id = %s AND character_id = %s AND status = 'offen'
               AND 1 - (embedding <=> %s::vector) >= %s
             ORDER BY neugier_vektor DESC
             LIMIT %s
            """,
            (vektor, user_id, character_id, vektor, min_naehe, deckel),
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
    zu_fern: list[dict] = [z for z in zeilen if float(z["naehe"]) < min_naehe]
    if zu_fern:
        raise RuntimeError(
            f"staerkste_luecken: {len(zu_fern)} Zeile(n) unter der Naehe {min_naehe} — "
            "die Bedingung hat nicht gegriffen"
        )

    logger.info(
        "Wissensluecken: %d offene Frage(n) fuer %s/%s nah am Reiz (>= %.2f; Zug %s; Naehe %s)",
        len(zeilen), user_id, character_id, min_naehe,
        ", ".join(f"{z['neugier_vektor']:.4f}" for z in zeilen) or "—",
        ", ".join(f"{float(z['naehe']):.3f}" for z in zeilen) or "—",
    )
    return zeilen
