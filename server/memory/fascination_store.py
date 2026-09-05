"""Die Traegerseite der Faszination — was die Rechnung aus der Datenbank braucht.

`ei/fascination.py` rechnet rein: Es bekommt Zahlen und gibt Zahlen zurueck.
Dieses Modul holt die Zahlen. Getrennt, weil die Rechnung ohne Datenbank
pruefbar bleiben soll (`10_CODE_QUALITAET`, Separation of Concerns) — und weil
genau diese Trennung erlaubt, die Rechnung im Labor ueber den ganzen Bestand
laufen zu lassen, ohne einen Turn zu fahren.

Konzept: `novaberg-thinking-faszination_k.md` §10.2 (der Anker) und §10.6.

**Der Traeger ist ein LZG-Knoten mit Qualitaetsprofil.** Nicht jeder Knoten ist
einer: `[gemessen]` 05.09.2026 tragen **28 von 3.357 aktiven Knoten** ein
Profil, und **27 davon** haben zugleich eine Bruecke. Ein Knoten ohne Profil
hat keinen Merkmalszug und damit keine Faszination — das ist kein Ausfall,
sondern die Aussage der Groesse.
"""

import logging

import psycopg2

from config import QUALITAET_KANON
from ei.fascination import qualitaet_verfall

logger = logging.getLogger("ki_server.memory.fascination_store")

# Die drei Zaehler des Ankers in einer Abfrage. Der LEFT JOIN auf die
# Rohturn-Zeile ist der einzige Weg an die Herkunft: `verbindung` traegt keine
# Herkunftsspalte (§10.2), und ohne sie waere `eigenimpuls` nicht bestimmbar.
_ANKER = """
SELECT v.lzg_id,
       count(DISTINCT v.erstellt_am::date) AS tage,
       count(DISTINCT v.turn_id)           AS turns,
       count(DISTINCT p.turn_id) FILTER (
           WHERE p.inhalt->>'herkunft' = 'eigener_impuls')      AS eigen,
       count(DISTINCT p.turn_id) FILTER (
           WHERE p.inhalt->>'herkunft' IN ('eigener_impuls', 'nutzer_turn')
       )                                                        AS bekannt
FROM verbindung v
LEFT JOIN pipeline_log p
       ON p.turn_id = v.turn_id AND p.art = 'turn_roh'
WHERE v.lzg_id = ANY(%s)
GROUP BY v.lzg_id
"""

# `verstaerkt_am` traegt den Zeitverfall (§10.4). Er wird **hier** gelesen und
# nicht beim Aufrufer gerechnet: Die Kante weiss, wann sie zuletzt beruehrt
# wurde, der Knoten nicht.
_PROFILE = """
SELECT tq.knoten_id, ak.name, tq.auspraegung,
       EXTRACT(EPOCH FROM (NOW() - tq.verstaerkt_am)) / 86400.0 AS tage
FROM traeger_qualitaet tq
JOIN abstrakt_knoten ak ON ak.id = tq.qualitaet_id
WHERE tq.knoten_id = ANY(%s)
"""


def traegerdaten_lesen(
    postgres_url: str, knoten_ids: list[int]
) -> dict[int, dict]:
    """Anker-Zaehler und Qualitaetsprofil je Traeger, in zwei Abfragen.

    **Zwei Abfragen und nicht eine.** Ein Knoten kann ein Profil ohne Bruecke
    haben und umgekehrt; ein gemeinsamer JOIN verloere die eine Haelfte
    stillschweigend, und der Aufrufer saehe nicht, welche.

    Vorbedingung: `knoten_ids` sind LZG-Kennungen. Eine leere Liste ist der
        Normalfall eines Turns ohne gelesene Erinnerungen und kein Fehler.
    Nachbedingung: {knoten_id: {tage, turns, eigenimpuls, profil, roh_profil}}.
        `profil` traegt die **verfallenen** Auspraegungen (§10.4), `roh_profil`
        die gespeicherten daneben — ohne sie waere spaeter nicht zu trennen, ob
        ein niedriger Wert so bewertet wurde oder verfallen ist. Ein Knoten
        ohne Bruecke traegt tage=0, turns=0; einer ohne bekannte Herkunft
        traegt `eigenimpuls=None` — **nicht 0.0**, denn *unbekannt* ist nicht
        *vom Nutzer* (§10.2). Ein Knoten ohne Profil traegt ein leeres.

    Args:
        postgres_url: Verbindungs-URL (Hausstil: Parameter, kein Modul-Global).
        knoten_ids: die Traeger, nach denen gefragt wird.

    Returns:
        Die Rohgroessen je Traeger, ungerechnet.
    """
    # ── Eingabe-Validierung ─────────────────────
    ids: list[int] = sorted({int(k) for k in (knoten_ids or []) if k is not None})
    if not ids:
        return {}

    daten: dict[int, dict] = {
        k: {"tage": 0, "turns": 0, "eigenimpuls": None,
            "profil": {}, "roh_profil": {}}
        for k in ids
    }

    # ── Verarbeitung ────────────────────────────
    try:
        conn = psycopg2.connect(postgres_url)
    except psycopg2.Error as fehler:
        logger.exception(
            f"Faszination: keine Verbindung fuer {len(ids)} Traeger — "
            f"{type(fehler).__name__}; die Rechnung entfaellt fuer diesen Turn"
        )
        return {}
    try:
        with conn.cursor() as cur:
            cur.execute(_ANKER, (ids,))
            for knoten_id, tage, turns, eigen, bekannt in cur.fetchall():
                eintrag = daten[int(knoten_id)]
                eintrag["tage"] = int(tage)
                eintrag["turns"] = int(turns)
                # None, wenn keine Beruehrung eine bekannte Herkunft traegt.
                eintrag["eigenimpuls"] = (
                    float(eigen) / float(bekannt) if bekannt else None
                )

            cur.execute(_PROFILE, (ids,))
            unbekannt: set[str] = set()
            for knoten_id, name, auspraegung, tage in cur.fetchall():
                if name not in QUALITAET_KANON:
                    unbekannt.add(str(name))
                    continue
                eintrag = daten[int(knoten_id)]
                # **Der Verfall wird hier angewandt, nicht beim Aufrufer.**
                # Die Alternative waere, `tage` mit durchzureichen — dann
                # koennte ein zweiter Leser ihn vergessen, und ein
                # unverfallenes Profil ist von einem frischen nicht zu
                # unterscheiden. Die Beruehrungen sind die des Traegers:
                # Wer den Knoten ansieht, sieht seine Qualitaeten an.
                eintrag["profil"][str(name)] = qualitaet_verfall(
                    str(name),
                    float(auspraegung),
                    float(tage or 0.0),
                    int(eintrag.get("turns", 0)),
                )
                eintrag.setdefault("roh_profil", {})[str(name)] = float(auspraegung)
            if unbekannt:
                logger.warning(
                    f"Faszination: {len(unbekannt)} Qualitaetsnamen ausserhalb "
                    f"des Kanons uebergangen — {sorted(unbekannt)}"
                )
    except psycopg2.Error as fehler:
        logger.exception(
            f"Faszination: Traegerdaten nicht lesbar — {type(fehler).__name__}; "
            f"die Rechnung entfaellt fuer diesen Turn"
        )
        return {}
    finally:
        conn.close()

    # ── Ausgabe-Verifikation ────────────────────
    ohne_profil: int = sum(1 for e in daten.values() if not e["profil"])
    if ohne_profil:
        logger.info(
            f"Faszination: {ohne_profil} von {len(ids)} Traegern ohne "
            f"Qualitaetsprofil — sie haben keinen Merkmalszug"
        )
    return daten
