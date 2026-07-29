"""Zwischenstand einer Urteilsreihe — damit ein Abbruch nichts kostet.

Eine Reihe teurer Einzelaufrufe, die abbricht, ist ohne Zwischenstand
vollstaendig verloren. Gemessen am 29.07.2026: rund 200 Urteile durch eine
einzelne Zeitueberschreitung, weil sie nur im Prozessspeicher standen.

**Die Datei ist Arbeitsmaterial, kein Messprotokoll.** Sie wird nach dem
Bericht verworfen. Das Ergebnis der Reihe geht in den Bericht, und wo es eine
Entscheidung traegt, in die dauerhafte Ablage — nicht hierher.

**Sie liegt ausserhalb des Repositoriums.** Das Server-Verzeichnis ist als
`/app` eingehaengt und damit Teil des Repos; ein Zwischenstand dort waere
committfaehig und wuerde Turn-Kennungen veroeffentlichen.

**Sie enthaelt keine Gespraechsinhalte.** Geschrieben wird die Turn-Kennung,
nicht der Text. Wer den Turn braucht, liest ihn ueber die Kennung aus dem
Bestand.

Drei Eigenschaften, jede aus einem Verlust gelernt:

1. **Sofort geschrieben, nicht am Ende.** Ein Puffer, der am Ende geleert wird,
   ist dasselbe wie keine Datei.
2. **Fehlschlaege werden mitgeschrieben**, als solche markiert. Sonst
   ueberspringt ein wiederaufgenommener Lauf sie stillschweigend, und die Reihe
   hat Luecken, die aussehen wie Ergebnisse.
3. **Auch die Aggregate der Reihe** — etwa eine Gueltigkeitspruefung, die vor
   der Erhebung laeuft — gehoeren hinein. Sie sind selbst Ergebnisse und beim
   Abbruch sonst verloren, obwohl jeder Einzelfall gesichert war.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from config import KALIBRIERUNG_ZWISCHENSTAND

logger = logging.getLogger("ki_server.agents.kalibrierung.zwischenstand")


@dataclass
class Reihenstand:
    """Was aus einer unterbrochenen Reihe wiederverwendbar ist.

    `urteile` traegt nur die gelungenen Faelle: Kennung → Urteil. `gescheitert`
    traegt die Kennungen, deren Aufruf fehlschlug — sie werden beim
    Wiederanlauf **erneut versucht**, nicht uebersprungen. `aggregate` traegt
    benannte Zwischenergebnisse der Reihe.
    """

    urteile:     dict[str, bool]
    gescheitert: set[str]
    aggregate:   dict[str, dict]


def _pfad(name: str) -> str:
    """Baut den Dateipfad einer Reihe und legt das Verzeichnis an.

    Vorbedingung: `name` ist ein Bezeichner ohne Pfadtrenner — er stammt aus
    dem Code, nicht aus einer Eingabe.
    Nachbedingung: Das Verzeichnis existiert, der Pfad ist beschreibbar.
    Fehlerfaelle: Ein Name mit Pfadtrenner wird abgewiesen, weil er aus dem
    vorgesehenen Verzeichnis herausfuehren koennte.

    Returns:
        Der vollstaendige Pfad.
    """

    # ── Eingabe-Validierung ─────────────────────
    if "/" in name or "\\" in name or not name:
        logger.error(
            f"Zwischenstand: unzulaessiger Reihenname '{name}' — "
            f"Pfadtrenner sind nicht erlaubt"
        )
        raise ValueError(f"unzulaessiger Reihenname: {name!r}")

    # ── Verarbeitung ────────────────────────────
    os.makedirs(KALIBRIERUNG_ZWISCHENSTAND, exist_ok=True)

    # ── Ausgabe ─────────────────────────────────
    return os.path.join(KALIBRIERUNG_ZWISCHENSTAND, f"{name}.jsonl")


def zeile_schreiben(
    name:    str,
    kennung: str,
    urteil:  bool | None,
    fehler:  str = "",
) -> None:
    """Haengt ein Einzelergebnis an — sofort, nicht gepuffert.

    Vorbedingung: `name` und `kennung` sind gesetzt. `urteil` ist None genau
    dann, wenn der Fall fehlschlug; dann traegt `fehler` den Grund.
    Nachbedingung: Eine Zeile im Zwischenstand, mit Zeitpunkt in UTC.
    Fehlerfaelle: Schreibfehler werden als `error` gemeldet und verschluckt —
    ein defekter Zwischenstand darf die Reihe nicht beenden, sonst ersetzt die
    Sicherung den Verlust, den sie verhindern soll. Die Reihe verliert dann
    ihre Wiederaufnahmefaehigkeit, und das steht im Log.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not kennung:
        logger.error("Zwischenstand: leere Kennung — Zeile nicht geschrieben")
        return

    if urteil is None and not fehler:
        logger.error(
            f"Zwischenstand: Fall '{kennung}' ohne Urteil und ohne Grund — "
            f"ein unbenannter Fehlschlag ist beim Wiederanlauf nicht deutbar"
        )
        fehler = "unbenannt"

    # ── Verarbeitung ────────────────────────────
    satz: dict = {
        "kennung": kennung,
        "urteil":  urteil,
        "fehler":  fehler,
        "zeit":    datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    # ── Ausgabe-Verifikation ────────────────────
    try:
        with open(_pfad(name), "a", encoding="utf-8") as datei:
            datei.write(json.dumps(satz, ensure_ascii=False) + "\n")
            datei.flush()
            os.fsync(datei.fileno())
    except (OSError, ValueError) as ex:
        logger.error(
            f"Zwischenstand '{name}': Zeile fuer '{kennung}' nicht geschrieben "
            f"({type(ex).__name__}: {ex}) — die Reihe laeuft weiter, ist aber "
            f"ab hier nicht mehr wiederaufnehmbar"
        )


def aggregat_schreiben(name: str, schluessel: str, wert: dict) -> None:
    """Haengt ein benanntes Zwischenergebnis der Reihe an.

    Fuer Groessen, die nicht zu einem Einzelfall gehoeren — etwa das Ergebnis
    einer Gueltigkeitspruefung, die vor der Erhebung laeuft. Ohne sie ist ein
    solches Ergebnis beim Abbruch verloren, obwohl jeder Einzelfall gesichert
    war.

    Vorbedingung: `schluessel` ist gesetzt, `wert` ist JSON-serialisierbar.
    Nachbedingung: Eine Zeile mit `aggregat`-Marke im Zwischenstand.
    Fehlerfaelle: wie bei `zeile_schreiben` — gemeldet, nicht geworfen.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not schluessel:
        logger.error("Zwischenstand: Aggregat ohne Schluessel — nicht geschrieben")
        return

    # ── Verarbeitung ────────────────────────────
    satz: dict = {
        "aggregat":  schluessel,
        "wert":      wert,
        "zeit":      datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    # ── Ausgabe-Verifikation ────────────────────
    try:
        with open(_pfad(name), "a", encoding="utf-8") as datei:
            datei.write(json.dumps(satz, ensure_ascii=False) + "\n")
            datei.flush()
            os.fsync(datei.fileno())
    except (OSError, ValueError) as ex:
        logger.error(
            f"Zwischenstand '{name}': Aggregat '{schluessel}' nicht geschrieben "
            f"({type(ex).__name__}: {ex})"
        )


def stand_lesen(name: str) -> Reihenstand:
    """Liest den Zwischenstand einer Reihe.

    Vorbedingung: keine — eine fehlende Datei ist der Normalfall beim ersten
    Lauf und kein Fehler.
    Nachbedingung: Ein Reihenstand. Bei mehreren Zeilen zur selben Kennung
    gewinnt die spaetere: Ein Wiederholungsversuch soll den Fehlschlag
    ueberschreiben, nicht neben ihm stehen.
    Fehlerfaelle: Eine unlesbare Zeile wird uebersprungen und **gezaehlt** —
    stillschweigend uebergangen waere sie eine Luecke, die aussieht wie ein
    nie versuchter Fall.

    Returns:
        Der Reihenstand.
    """

    # ── Eingabe-Validierung ─────────────────────
    try:
        pfad: str = _pfad(name)
    except ValueError:
        return Reihenstand({}, set(), {})

    if not os.path.exists(pfad):
        logger.info(f"Zwischenstand '{name}': keine Datei — die Reihe beginnt neu")
        return Reihenstand({}, set(), {})

    # ── Verarbeitung ────────────────────────────
    urteile:     dict[str, bool] = {}
    gescheitert: set[str]        = set()
    aggregate:   dict[str, dict] = {}
    defekt:      int             = 0

    with open(pfad, "r", encoding="utf-8") as datei:
        for zeile in datei:
            zeile = zeile.strip()
            if not zeile:
                continue
            try:
                satz: dict = json.loads(zeile)
            except json.JSONDecodeError:
                defekt += 1
                continue

            if "aggregat" in satz:
                aggregate[satz["aggregat"]] = satz.get("wert", {})
                continue

            kennung = satz.get("kennung")
            if not kennung:
                defekt += 1
                continue

            if isinstance(satz.get("urteil"), bool):
                urteile[kennung] = satz["urteil"]
                gescheitert.discard(kennung)
            else:
                gescheitert.add(kennung)

    # ── Ausgabe-Verifikation ────────────────────
    if defekt:
        logger.error(
            f"Zwischenstand '{name}': {defekt} unlesbare Zeilen uebersprungen — "
            f"die betroffenen Faelle gelten als nicht versucht und werden "
            f"wiederholt"
        )

    logger.info(
        f"Zwischenstand '{name}': {len(urteile)} Urteile, "
        f"{len(gescheitert)} Fehlschlaege zur Wiederholung, "
        f"{len(aggregate)} Aggregate"
    )
    return Reihenstand(urteile, gescheitert, aggregate)


def verwerfen(name: str) -> None:
    """Loescht den Zwischenstand einer Reihe.

    Wird nach dem Bericht gerufen: Die Datei ist Arbeitsmaterial und soll nicht
    liegenbleiben, damit ein spaeterer Lauf nicht auf Urteilen eines anderen
    Zeugen aufbaut.

    Vorbedingung: keine.
    Nachbedingung: Die Datei existiert nicht mehr.
    Fehlerfaelle: Eine fehlende Datei ist kein Fehler. Ein Loeschfehler wird
    gemeldet, weil ein liegengebliebener Stand den naechsten Lauf verfaelscht.
    """

    # ── Eingabe-Validierung / Verarbeitung ──────
    try:
        pfad: str = _pfad(name)
        if os.path.exists(pfad):
            os.remove(pfad)
            logger.info(f"Zwischenstand '{name}': verworfen")
    except (OSError, ValueError) as ex:
        logger.error(
            f"Zwischenstand '{name}': nicht geloescht ({type(ex).__name__}: "
            f"{ex}) — ein naechster Lauf wuerde darauf aufbauen"
        )
