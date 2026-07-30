"""Einmal-Migration: versorgt den KZG-Bestand mit `salienz_eingang`.

Anlass (Chat 113): Bis zum Skalenumbau war die KZG-Salienz ein Akkumulator mit
Cap 10.0 — die Eingangsbewertung des Modells wurde bei jeder Verstaerkung
ueberschrieben. Gemessen am 28.07.2026 standen 71 von 188 Eintraegen ueber 1.0,
der hoechste bei 5.636.

`novaberg-kzg-salienz_k.md` §10 erklaerte die Migration fuer erledigt, weil der
Reset vom 27.07.2026 die Partition geleert hatte. Seitdem ist wieder Bestand
entstanden. Der dort formulierte Vorbehalt greift damit woertlich: „Kommt jemals
ein Bestand ohne `salienz_eingang` hinzu, gilt die Regel wieder" — ein Default
darf nie aussehen wie ein echter Wert.

Zwei Faelle, nach Rekonstruierbarkeit getrennt:

  haeufigkeit <= 1  Nie verstaerkt, also ist `salienz` unveraendert die
                    Modellbewertung. Exakt uebernehmbar -> Herkunft "gemessen".

  haeufigkeit  > 1  Der Akkumulator ist pfadabhaengig, die Eingangsbewertung
                    existiert nirgends mehr. Gesetzt auf 0.6 (Meister-Setzung
                    28.07.2026) -> Herkunft "geschaetzt". Unter der neuen Kurve
                    liegt 0.6 zwischen MID und HIGH: Die Masse mit zwei oder
                    drei Verstaerkungen bleibt knapp unter dem Promotionstor,
                    nur was mindestens viermal wiederkam, geht durch.

Die Salienz wird in beiden Faellen aus den beiden Feldern neu gerechnet, nicht
fortgeschrieben.

Idempotent: Eintraege, die bereits ein `salienz_eingang` tragen, werden
uebersprungen. Das Skript darf beliebig oft laufen — insbesondere ein zweites
Mal, um Eintraege einzusammeln, die zwischen Serverstart und erstem Lauf
entstanden sind.

Aufruf:
    python scripts/migration_kzg_salienz_eingang.py [--trocken]
"""

import logging
import sys

from config import redis_client
from memory.kzg import salienz_berechnen

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("migration_kzg_salienz_eingang")

# Setzung des Meisters fuer nicht rekonstruierbare Eintraege (28.07.2026).
GESCHAETZTER_EINGANG: float = 0.6


def migrieren(trocken: bool = False) -> dict:
    """Versorgt jeden KZG-Eintrag ohne `salienz_eingang` mit einem Eingangswert.

    Vorbedingung: Redis erreichbar; die Hashes tragen `salienz` und `haeufigkeit`.
    Nachbedingung: Jeder Eintrag der Partition traegt `salienz_eingang`,
    `salienz_eingang_herkunft` und eine daraus neu gerechnete `salienz` in [0,1].
    Fehlerfaelle: Ein Eintrag ohne lesbare `salienz` oder `haeufigkeit` wird
    laut protokolliert und uebersprungen — er bleibt unversorgt und faellt beim
    naechsten Verstaerkungsversuch erneut auf.

    Args:
        trocken: Nur zaehlen und protokollieren, nichts schreiben.

    Returns:
        Zaehlwerk als Dict.
    """

    # ── Eingabe-Validierung ─────────────────────
    keys: list[str] = [
        k.decode("utf-8") if isinstance(k, bytes) else k
        for k in redis_client.scan_iter(match="kzg:*", count=200)
    ]

    if not keys:
        logger.error("Migration: Kein einziger kzg:*-Key gefunden — nichts zu tun")
        return {"gesamt": 0, "gemessen": 0, "geschaetzt": 0,
                "uebersprungen": 0, "defekt": 0}

    # ── Verarbeitung ────────────────────────────
    zaehler: dict = {"gesamt": len(keys), "gemessen": 0, "geschaetzt": 0,
                     "uebersprungen": 0, "defekt": 0}

    for key in keys:
        if redis_client.hget(key, "salienz_eingang") is not None:
            zaehler["uebersprungen"] += 1
            continue

        salienz_roh:     str | None = redis_client.hget(key, "salienz")
        haeufigkeit_roh: str | None = redis_client.hget(key, "haeufigkeit")

        if salienz_roh is None or haeufigkeit_roh is None:
            logger.error(
                f"Migration: {key} traegt kein salienz/haeufigkeit "
                f"(salienz={salienz_roh}, haeufigkeit={haeufigkeit_roh}) — uebersprungen"
            )
            zaehler["defekt"] += 1
            continue

        try:
            alte_salienz: float = float(salienz_roh)
            haeufigkeit:  int   = int(float(haeufigkeit_roh))
        except (TypeError, ValueError) as fehler:
            logger.exception(
                f"{type(fehler).__name__}: Migration: {key} unlesbare Werte — uebersprungen"
            )
            zaehler["defekt"] += 1
            continue

        if haeufigkeit <= 1:
            eingang:  float = min(1.0, alte_salienz)
            herkunft: str   = "gemessen"
            zaehler["gemessen"] += 1
        else:
            eingang  = GESCHAETZTER_EINGANG
            herkunft = "geschaetzt"
            zaehler["geschaetzt"] += 1

        neue_salienz: float = salienz_berechnen(eingang, haeufigkeit)

        logger.info(
            f"{'[trocken] ' if trocken else ''}{key}: haeufigkeit={haeufigkeit}, "
            f"salienz {alte_salienz:.4f} -> {neue_salienz:.4f} "
            f"(eingang={eingang:.2f}, {herkunft})"
        )

        if not trocken:
            redis_client.hset(key, mapping={
                "salienz_eingang":          str(eingang),
                "salienz_eingang_herkunft": herkunft,
                "salienz":                  str(neue_salienz),
            })

    # ── Ausgabe-Verifikation ────────────────────
    if not trocken:
        offen: int = sum(
            1 for k in keys if redis_client.hget(k, "salienz_eingang") is None
        )
        if offen != zaehler["defekt"]:
            logger.error(
                f"Migration: {offen} Eintraege ohne salienz_eingang, erwartet "
                f"{zaehler['defekt']} defekte — Nachbedingung verletzt"
            )

    logger.info(
        f"Migration abgeschlossen: {zaehler['gesamt']} Keys, "
        f"{zaehler['gemessen']} gemessen, {zaehler['geschaetzt']} geschaetzt, "
        f"{zaehler['uebersprungen']} bereits versorgt, {zaehler['defekt']} defekt"
    )
    return zaehler


if __name__ == "__main__":
    migrieren(trocken="--trocken" in sys.argv)
