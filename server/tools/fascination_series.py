"""Die Reihe des Faszinations-Bestandslaufs — lesen, nicht rechnen.

Der neunte Schritt des Tageslaufs rechnet die Traegerseite der Faszination und
schreibt **eine** `pipeline_log`-Zeile je Lauf (`phase = 'faszination_bestand'`).
Er schreibt nichts in den Bestand, und das ist Absicht: Was der Groesse fehlt,
ist nicht der letzte Wert, sondern die Reihe ueber die Zeit
(`novaberg-thinking-faszination_k.md` §10.6).

**Eine Reihe, die niemand liest, ist keine.** Dieses Werkzeug haelt die Zeilen
gegeneinander und beantwortet die eine Frage, fuer die der Lauf gebaut wurde:
*Bewegt sich die Traegerseite, und reicht ihre Spanne, um Deckel und
Halbstrecken zu kalibrieren?*

**Es rechnet nichts nach.** Jede Zahl stammt aus der Zeile, die der Lauf
geschrieben hat — eine zweite Rechnung ergaebe eine zweite Wahrheit, und der
Unterschied fiele erst auf, wenn jemand beide vergleicht.

Aufruf im Behaelter:
    python -m tools.fascination_series             # die letzten 30 Laeufe
    python -m tools.fascination_series --alle      # alle
    python -m tools.fascination_series --traeger   # dazu die Bewegung je Traeger
"""

import json
import logging
import sys

import psycopg2
import psycopg2.extras

from config import FASZ_MAXIMUM, POSTGRES_URL

logger = logging.getLogger("ki_server.tools.fascination_series")

# Die Zeile des neunten Tageslauf-Schritts. `node` und `quelle` stehen im
# Agenten (`agents/synapsen_decay/agent.py`); die Phase unterscheidet sie von
# den uebrigen Forensikzeilen desselben Laufs.
_REIHE = """
SELECT erstellt_am, inhalt
FROM pipeline_log
WHERE node = 'synapsen_decay'
  AND inhalt->>'phase' = 'faszination_bestand'
ORDER BY erstellt_am DESC
LIMIT %s
"""

# Ohne zwei Punkte gibt es keine Bewegung, nur einen Wert. Der Unterschied
# gehoert in die Ausgabe, weil ein einzelner Lauf sonst wie eine flache Reihe
# aussieht.
MINDEST_PUNKTE: int = 2


def series_load(postgres_url: str, limit: int = 30) -> dict:
    """Liest die Zeilen des Bestandslaufs, juengste zuerst.

    Vorbedingung: `limit` ist eine positive ganze Zahl.
    Nachbedingung: {laeufe, error}. `laeufe` ist chronologisch **aufsteigend**
        sortiert — die Reihe wird vorwaerts gelesen, auch wenn die Abfrage
        rueckwaerts holt.

    Args:
        postgres_url: Verbindungs-URL (Hausstil: Parameter, kein Modul-Global).
        limit: Wie viele Laeufe hoechstens.

    Returns:
        Die Laeufe samt Fehlerfeld.
    """
    # ── Eingabe-Validierung ─────────────────────
    ergebnis: dict = {"laeufe": [], "error": None}
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        ergebnis["error"] = f"Deckel {limit!r} — erwartet eine positive ganze Zahl"
        logger.error(f"Faszinations-Reihe: {ergebnis['error']}, verworfen")
        return ergebnis

    # ── Verarbeitung ────────────────────────────
    try:
        conn = psycopg2.connect(postgres_url)
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(_REIHE, (limit,))
                zeilen = cur.fetchall()
        finally:
            conn.close()
    except psycopg2.Error as fehler:
        ergebnis["error"] = f"Reihe nicht lesbar: {type(fehler).__name__}"
        logger.exception(f"Faszinations-Reihe: {ergebnis['error']}")
        return ergebnis

    laeufe: list[dict] = []
    for zeile in reversed(zeilen):
        inhalt: dict = zeile["inhalt"] or {}
        laeufe.append({
            "zeitpunkt":    zeile["erstellt_am"],
            "traeger":      inhalt.get("traeger"),
            "gerechnet":    inhalt.get("gerechnet"),
            "ohne_bindung": inhalt.get("ohne_bindung"),
            # **Kann fehlen, und das ist eine Auskunft, keine Luecke.** Vor dem
            # 05.09.2026 trug die Zeile das Feld nicht; ein `None` sagt, dass
            # dieser Lauf aelter ist als der Strangzug im Protokoll.
            "ohne_strang":  inhalt.get("ohne_strang"),
            "roh_min":      inhalt.get("roh_min"),
            "roh_median":   inhalt.get("roh_median"),
            "roh_max":      inhalt.get("roh_max"),
            "werte":        inhalt.get("werte") or {},
        })

    # ── Ausgabe-Verifikation ────────────────────
    ergebnis["laeufe"] = laeufe
    logger.info(
        f"Faszinations-Reihe: {len(laeufe)} Laeufe gelesen "
        f"(Deckel {limit})"
    )
    return ergebnis


def series_report(laeufe: list[dict]) -> dict:
    """Beurteilt, ob die Reihe kalibrieren kann — und sagt, woran es liegt.

    Vorbedingung: keine — eine leere Reihe ist der Zustand vor dem ersten
        Tageslauf und kein Fehler.
    Nachbedingung: {punkte, median_min, median_max, median_spanne, roh_max,
        deckel_erreicht, traeger_bewegt, kalibrierfaehig, grund}.
        `kalibrierfaehig` ist **nie** ohne `grund` — eine Ampel ohne Begruendung
        ist ein Urteil, dessen Eingangsgroessen niemand nachrechnen kann.

    Args:
        laeufe: Die Reihe, chronologisch aufsteigend.

    Returns:
        Die Kennzahlen der Reihe.
    """
    # ── Eingabe-Validierung ─────────────────────
    bericht: dict = {
        "punkte": len(laeufe), "median_min": None, "median_max": None,
        "median_spanne": None, "roh_max": None, "deckel_erreicht": False,
        "traeger_bewegt": 0, "kalibrierfaehig": False, "grund": "",
    }
    if len(laeufe) < MINDEST_PUNKTE:
        bericht["grund"] = (
            f"{len(laeufe)} Lauf/Laeufe — eine Reihe braucht mindestens "
            f"{MINDEST_PUNKTE} Punkte, sonst gibt es einen Wert und keine Bewegung"
        )
        logger.info(f"Faszinations-Reihe: {bericht['grund']}")
        return bericht

    # ── Verarbeitung ────────────────────────────
    mediane: list[float] = [
        float(lauf["roh_median"]) for lauf in laeufe
        if lauf.get("roh_median") is not None
    ]
    maxima: list[float] = [
        float(lauf["roh_max"]) for lauf in laeufe
        if lauf.get("roh_max") is not None
    ]
    if not mediane or not maxima:
        bericht["grund"] = (
            "Kein Lauf der Reihe traegt Median oder Maximum — die Zeilen sind "
            "da und die Zahlen nicht"
        )
        logger.error(f"Faszinations-Reihe: {bericht['grund']}")
        return bericht

    bericht["median_min"] = round(min(mediane), 4)
    bericht["median_max"] = round(max(mediane), 4)
    bericht["median_spanne"] = round(max(mediane) - min(mediane), 4)
    bericht["roh_max"] = round(max(maxima), 4)
    bericht["deckel_erreicht"] = max(maxima) >= FASZ_MAXIMUM

    # **Die Bewegung je Traeger ist die eigentliche Auskunft.** Ein Median kann
    # stillstehen, waehrend einzelne Traeger steigen und andere fallen; nur die
    # Zaehlung ueber die Traeger trennt einen ruhenden Bestand von einem, in dem
    # sich nichts bewegt.
    erster: dict = laeufe[0].get("werte") or {}
    letzter: dict = laeufe[-1].get("werte") or {}
    bericht["traeger_bewegt"] = sum(
        1 for knoten_id, wert in letzter.items()
        if knoten_id in erster and float(wert) != float(erster[knoten_id])
    )

    # ── Ausgabe-Verifikation ────────────────────
    if bericht["median_spanne"] == 0.0 and bericht["traeger_bewegt"] == 0:
        bericht["grund"] = (
            f"Ueber {bericht['punkte']} Laeufe bewegt sich kein einziger "
            f"Traeger — die Reihe misst nichts, und das ist ein Befund ueber "
            f"den Bestand, nicht ueber die Rechnung"
        )
    elif not bericht["deckel_erreicht"]:
        bericht["kalibrierfaehig"] = True
        bericht["grund"] = (
            f"Die Reihe bewegt sich ({bericht['traeger_bewegt']} Traeger, "
            f"Median-Spanne {bericht['median_spanne']}). Der Deckel "
            f"{FASZ_MAXIMUM} bleibt bei roh_max {bericht['roh_max']} "
            f"unerreicht — kalibrierbar sind die Halbstrecken des Ankers, "
            f"nicht der Deckel"
        )
    else:
        bericht["kalibrierfaehig"] = True
        bericht["grund"] = (
            f"Die Reihe erreicht den Deckel {FASZ_MAXIMUM} "
            f"(roh_max {bericht['roh_max']}) — er ist damit erstmals pruefbar"
        )
    logger.info(f"Faszinations-Reihe: {bericht['grund']}")
    return bericht


def _bericht_text(laeufe: list[dict], bericht: dict, *, je_traeger: bool) -> str:
    """Formt die Reihe zu **einem** Block.

    Zeilenweises Drucken verzahnt sich mit den Logzeilen desselben Laufs; eine
    Tabelle, die dabei zerrissen wird, ist keine mehr.
    """
    zeilen: list[str] = [
        f"{'Zeitpunkt (UTC)':<20} {'gerch':>5} {'o.Bdg':>5} {'o.Str':>5} "
        f"{'min':>7} {'median':>7} {'max':>7} {'d-Median':>9}",
    ]
    vorher: float | None = None
    for lauf in laeufe:
        median = lauf.get("roh_median")
        delta = "" if vorher is None or median is None else f"{median - vorher:+.4f}"
        zeit = lauf["zeitpunkt"].strftime("%Y-%m-%d %H:%M:%S")
        strang = "—" if lauf.get("ohne_strang") is None else lauf["ohne_strang"]
        zeilen.append(
            f"{zeit:<20} {lauf.get('gerechnet', '?'):>5} "
            f"{lauf.get('ohne_bindung', '?'):>5} {strang:>5} "
            f"{lauf.get('roh_min', '?'):>7} "
            f"{median if median is not None else '?':>7} "
            f"{lauf.get('roh_max', '?'):>7} {delta:>9}"
        )

    zeilen.append("")
    zeilen.append(
        f"Punkte: {bericht['punkte']} · Median-Spanne {bericht['median_spanne']} "
        f"· bewegte Traeger {bericht['traeger_bewegt']} "
        f"· Deckel {'erreicht' if bericht['deckel_erreicht'] else 'unerreicht'}"
    )
    zeilen.append(
        f"Kalibrierfaehig: {'ja' if bericht['kalibrierfaehig'] else 'nein'} — "
        f"{bericht['grund']}"
    )

    if je_traeger and len(laeufe) >= MINDEST_PUNKTE:
        erster: dict = laeufe[0].get("werte") or {}
        letzter: dict = laeufe[-1].get("werte") or {}
        bewegt: dict = {
            knoten_id: (float(erster[knoten_id]), float(wert))
            for knoten_id, wert in letzter.items()
            if knoten_id in erster and float(wert) != float(erster[knoten_id])
        }
        zeilen.append("")
        zeilen.append(f"Bewegte Traeger ({len(bewegt)}):")
        for knoten_id, (alt, neu) in sorted(
            bewegt.items(), key=lambda paar: abs(paar[1][1] - paar[1][0]), reverse=True
        ):
            zeilen.append(
                f"  Knoten {knoten_id:>7}: {alt:.4f} -> {neu:.4f} ({neu - alt:+.4f})"
            )
    return "\n".join(zeilen)


def main(argv: list[str] | None = None) -> int:
    """Liest die Reihe und schreibt sie nach stdout.

    Returns:
        0 bei gelesener Reihe, 1 wenn sie nicht lesbar war.
    """
    argumente: list[str] = list(argv if argv is not None else sys.argv[1:])
    limit: int = 10_000 if "--alle" in argumente else 30
    gelesen: dict = series_load(POSTGRES_URL, limit)
    if gelesen["error"]:
        print(f"Fehler: {gelesen['error']}", file=sys.stderr)
        return 1

    laeufe: list[dict] = gelesen["laeufe"]
    bericht: dict = series_report(laeufe)
    if "--json" in argumente:
        print(json.dumps(bericht, ensure_ascii=False))
        return 0
    if not laeufe:
        print("Keine Zeile des Bestandslaufs im pipeline_log — der neunte "
              "Schritt des Tageslaufs ist noch nicht gelaufen.")
        return 0
    print(_bericht_text(laeufe, bericht, je_traeger="--traeger" in argumente))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    sys.exit(main())
