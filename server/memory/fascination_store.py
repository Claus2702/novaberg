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
import statistics

import psycopg2

from config import QUALITAET_KANON
from ei.fascination import (
    bindung_roh,
    faszination,
    merkmalszug,
    qualitaet_verfall,
)

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


# Die Traeger, ueber die der Bestandslauf rechnet: alle mit Qualitaetsprofil.
# Ein Traeger ohne Profil hat keinen Merkmalszug und damit keine Faszination
# — er gehoert nicht in die Reihe, sondern in ihre Fussnote.
_TRAEGER_MIT_PROFIL = """
SELECT DISTINCT knoten_id FROM traeger_qualitaet ORDER BY knoten_id
"""


def bestandslauf(postgres_url: str) -> dict:
    """Rechnet die **Traegerseite** der Faszination ueber alle profilierten Traeger.

    **Ohne Turn-Modulatoren, und das ist der Zweck.** Am 05.09.2026 gemessen
    spannen die sechs Modulatoren Faktor **16,2**, die Traegerseite nur
    **2,0** — im Turn ist deshalb nicht zu trennen, ob ein hoher Wert vom
    Traeger oder von der Lage kommt. Dieser Lauf misst die eine Haelfte allein
    und macht ihre Entwicklung ueber Tage ablesbar.

    **Er schreibt nichts in den Bestand**, nur eine Protokollzeile je Lauf.
    Die Faszination hat keine Tabelle, und sie braucht heute keine: Was
    fehlt, ist die Reihe ueber die Zeit, nicht der letzte Wert.

    Vorbedingung: keine — ein Bestand ohne profilierte Traeger ist der
        Zustand vor dem ersten Profil-Lauf und kein Fehler.
    Nachbedingung: {traeger, gerechnet, ohne_bindung, werte, roh_min,
        roh_median, roh_max, error}. `ohne_bindung` zaehlt die Traeger, deren
        Anker 0 ergibt — **sie sind der heutige Regelfall** und der Grund,
        warum die Reihe zunaechst flach liegt (§10.2, die offene Frage, ob
        Lesen eine Beruehrung ist).

    Args:
        postgres_url: Verbindungs-URL (Hausstil: Parameter, kein Modul-Global).

    Returns:
        Die Buchfuehrung des Laufs samt Verteilung.
    """
    # ── Eingabe-Validierung ─────────────────────
    ergebnis: dict = {
        "traeger": 0, "gerechnet": 0, "ohne_bindung": 0, "werte": {},
        "roh_min": None, "roh_median": None, "roh_max": None, "error": None,
    }
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor() as cur:
                cur.execute(_TRAEGER_MIT_PROFIL)
                ids: list[int] = [int(z[0]) for z in cur.fetchall()]
        finally:
            conn.close()
    except psycopg2.Error as fehler:
        ergebnis["error"] = f"Traegerliste nicht lesbar: {type(fehler).__name__}"
        logger.exception(f"Faszination: {ergebnis['error']}")
        return ergebnis

    ergebnis["traeger"] = len(ids)
    if not ids:
        logger.info(
            "Faszination: kein profilierter Traeger im Bestand — "
            "der Lauf hat nichts zu rechnen"
        )
        return ergebnis

    # ── Verarbeitung ────────────────────────────
    daten: dict[int, dict] = traegerdaten_lesen(postgres_url, ids)
    rohe: list[float] = []
    for knoten_id in ids:
        eintrag: dict = daten.get(knoten_id) or {}
        profil: dict = eintrag.get("profil") or {}
        if not profil:
            continue
        bindung: float = bindung_roh(
            eintrag.get("tage", 0),
            eintrag.get("turns", 0),
            eintrag.get("eigenimpuls"),
        )
        if bindung <= 0.0:
            ergebnis["ohne_bindung"] += 1
        # Der Praegungszug steht auf 1.0 — er ist eine Turn-Groesse und hat
        # ausserhalb eines Turns keinen Reiz, gegen den er rechnen koennte.
        wert, roh = faszination(bindung, merkmalszug(profil), 1.0, None)
        ergebnis["werte"][str(knoten_id)] = round(wert, 4)
        rohe.append(roh)
        ergebnis["gerechnet"] += 1

    # ── Ausgabe-Verifikation ────────────────────
    if rohe:
        geordnet = sorted(rohe)
        ergebnis["roh_min"] = round(geordnet[0], 4)
        ergebnis["roh_max"] = round(geordnet[-1], 4)
        ergebnis["roh_median"] = round(statistics.median(geordnet), 4)
    if ergebnis["gerechnet"] and ergebnis["ohne_bindung"] == ergebnis["gerechnet"]:
        # **Kein Fehler, aber eine Meldung wert:** Steht der ganze Bestand auf
        # null, misst die Reihe nichts — und das faellt sonst erst auf, wenn
        # jemand die Werte ansieht.
        logger.warning(
            f"Faszination: alle {ergebnis['gerechnet']} gerechneten Traeger "
            f"haben Bindung 0 — die Reihe liegt flach; vermutlich fehlen die "
            f"Bruecken (§10.2)"
        )
    logger.info(
        f"Faszination: {ergebnis['gerechnet']} von {ergebnis['traeger']} "
        f"Traegern gerechnet, {ergebnis['ohne_bindung']} ohne Bindung; "
        f"roh {ergebnis['roh_min']} … {ergebnis['roh_max']}"
    )
    return ergebnis
