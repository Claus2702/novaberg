"""Misst den dritten Zugriff auf die Bibliothek: den Enricher-Weg.

Die Bibliothek hat drei Konsumenten, und sie fragen mit drei verschiedenen
Groessen:

  1. Bestellung (`wissen`-Dienst)  — die nackte Frage, ~60-100 Zeichen
  2. Rueckweg (`kandidaten_laden`) — ein Kontexttext, Ø 833 Zeichen
  3. **Enricher (`WissenManager`)** — `state["such_vektor"]`, und das ist die
     eingebettete Nutzeraeusserung, VERSCHOBEN um die aktivierten Ziele und
     den Vorturn-Cluster (`ei/gravitation.py::wahrnehmung_verschieben`).

Der dritte wurde beim Umbau auf Themenvektoren und Schwelle 0,50 mitgezogen,
obwohl beide an der Anfrage des ERSTEN kalibriert sind. Diese Messung holt
das nach und beantwortet genau eine Frage:

    **Was kostet die Verschiebung an Auffindbarkeit?**

Aufbau: dieselbe Methode wie an den anderen beiden Zugriffen — je Frage ist
die richtige Antwort bekannt (die Ausarbeitung, aus deren Themenfeld die Frage
gebaut wurde). Gemessen wird derselbe Vektor einmal unverschoben und einmal
durch `wahrnehmung_verschieben` geschickt, gegen beide Ziele.

Das Werkzeug laeuft IM Behaelter, weil es die Produktivfunktion aufruft statt
sie nachzubilden — eine nachgebaute Verschiebung maesse die Nachbildung.

Veraendert nichts.

Aufruf:  python -m tools.messung_enricher_ziel [stichprobe]
"""

import logging
import random
import statistics
import sys

import psycopg2

from config import POSTGRES_URL, WISSEN_RETRIEVAL_SCHWELLE
from ei.gravitation import wahrnehmung_verschieben, ziel_gravitation_berechnen
from memory.repositories.autonomous_wissen_repository import themen_zerlegen
from memory.utils import embedding_zu_pgvector_str
from memory.ziele import ziele_aktive_laden
from tools.reembed_all import embedding_berechnen

logger = logging.getLogger("ki_server.tools.messung_enricher_ziel")

SEED:      int = 20260819
SCHABLONE: str = "Was hast du dir selbst zu {} erarbeitet?"


def _rang_und_kosinus(
    conn: psycopg2.extensions.connection, literal: str, ziel: str,
) -> tuple[str | None, float, float]:
    """Fragt ein Ziel ab und liefert (beste_id, kosinus_bester, kosinus_eigener_platz).

    Args:
        conn: offene Verbindung.
        literal: pgvector-Literal des Suchvektors.
        ziel: "thema" für die Themenvektoren, "destillat" für die alte Spalte.

    Returns:
        (id des besten Treffers, sein Kosinus, 0.0 als Platzhalter)
    """
    if ziel == "thema":
        sql = (
            "SELECT w.id::text, MAX(1 - (t.embedding <=> %s::vector)) AS c "
            "FROM autonomous_wissen w JOIN autonomous_wissen_thema t ON t.wissen_id = w.id "
            "WHERE w.user_id='meister' AND w.character_id='nova' AND w.aktiv "
            "AND w.typ='wissen' AND t.embedding IS NOT NULL "
            "GROUP BY w.id ORDER BY c DESC LIMIT 1"
        )
    else:
        sql = (
            "SELECT id::text, 1 - (themen_embedding <=> %s::vector) AS c "
            "FROM autonomous_wissen "
            "WHERE user_id='meister' AND character_id='nova' AND aktiv "
            "AND typ='wissen' AND themen_embedding IS NOT NULL "
            "ORDER BY c DESC LIMIT 1"
        )
    with conn.cursor() as cur:
        cur.execute(sql, (literal,))
        zeile = cur.fetchone()
    return (zeile[0], float(zeile[1]), 0.0) if zeile else (None, 0.0, 0.0)


def _eigener_kosinus(
    conn: psycopg2.extensions.connection, literal: str, ziel: str, wissen_id: str,
) -> float:
    """Der Kosinus der RICHTIGEN Ausarbeitung, unabhaengig von ihrem Rang."""
    if ziel == "thema":
        sql = (
            "SELECT MAX(1 - (t.embedding <=> %s::vector)) FROM autonomous_wissen_thema t "
            "WHERE t.wissen_id = %s AND t.embedding IS NOT NULL"
        )
    else:
        sql = (
            "SELECT 1 - (themen_embedding <=> %s::vector) FROM autonomous_wissen "
            "WHERE id = %s AND themen_embedding IS NOT NULL"
        )
    with conn.cursor() as cur:
        cur.execute(sql, (literal, int(wissen_id)))
        zeile = cur.fetchone()
    return float(zeile[0]) if zeile and zeile[0] is not None else 0.0


def messen(stichprobe: int = 30) -> None:
    """Fuehrt die Messung aus und schreibt das Ergebnis nach stdout.

    Args:
        stichprobe: Zahl der Fragen.
    """
    conn = psycopg2.connect(POSTGRES_URL)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, thema FROM autonomous_wissen "
                "WHERE user_id='meister' AND character_id='nova' AND aktiv "
                "AND typ='wissen' AND EXISTS (SELECT 1 FROM autonomous_wissen_thema t "
                "WHERE t.wissen_id = autonomous_wissen.id AND t.embedding IS NOT NULL) "
                "ORDER BY id"
            )
            bestand = [(z[0], z[1]) for z in cur.fetchall()]

        # **Das Paar steht hier UMGEKEHRT zur Bibliothek, und das ist richtig.**
        # `user_id` ist das Subjekt: Das Wissen handelt vom Menschen
        # (meister × nova), die Ziele sind Novas eigene (nova × meister).
        # Ein erster Anlauf uebergab die Bibliotheks-Reihenfolge und bekam
        # **0 von 0** aktiven Zielen — die Verschiebung war dann wieder die
        # Identitaet, und der gemessene Verlust wieder exakt 0,0000. Zweimal
        # dieselbe Nullmessung, zweimal wie ein Ergebnis aussehend.
        ziele = ziele_aktive_laden(POSTGRES_URL, "nova", "meister")

        random.seed(SEED)
        kandidaten = [(i, t) for i, t in bestand if len(themen_zerlegen(t)) >= 2]
        probe = random.sample(kandidaten, min(stichprobe, len(kandidaten)))
        print(f"Bestand {len(bestand)} · Stichprobe {len(probe)} (seed {SEED})\n")

        # Vier Zellen: {roh, verschoben} × {Themenvektoren, Destillat}
        treffer: dict[str, int] = {k: 0 for k in ("roh_thema", "versch_thema",
                                                  "roh_destillat", "versch_destillat")}
        kosinus: dict[str, list[float]] = {k: [] for k in treffer}
        verschiebungsverlust: list[float] = []

        for nr, (wissen_id, themenfeld) in enumerate(probe, 1):
            einzeln = random.choice(themen_zerlegen(themenfeld))
            roh_vec = embedding_berechnen(SCHABLONE.format(einzeln))

            # **Die Produktivfunktionen, nicht eine Nachbildung** — und mit
            # ECHTEN Zielen aus dem Bestand. Ein erster Anlauf mass mit
            # `aktivierte_ziele=[]` und `cluster=""`: Dann ist die
            # Verschiebung die Identitaet, der gemessene Verlust war exakt
            # 0,0000, und gemessen wurde der Fall, in dem sie gar nicht
            # stattfindet. `glut` traegt mit 0.30 den staerksten Faktor der
            # Tabelle — das ist der ungueenstigste Fall und damit die
            # OBERGRENZE des Verlusts.
            aktiviert = ziel_gravitation_berechnen(roh_vec, ziele)
            versch_vec = wahrnehmung_verschieben(
                anfrage_embedding=roh_vec, aktivierte_ziele=aktiviert,
                cluster="glut", ist_anweisung=False,
            ).vektor
            if nr == 1:
                print(f"  aktivierte Ziele je Frage: {len(aktiviert)} "
                      f"(von {len(ziele)} aktiven), Cluster 'glut' Faktor 0.30")

            for marke, vec in (("roh", roh_vec), ("versch", versch_vec)):
                literal = embedding_zu_pgvector_str(vec)
                for ziel in ("thema", "destillat"):
                    beste_id, _, _ = _rang_und_kosinus(conn, literal, ziel)
                    eigen = _eigener_kosinus(conn, literal, ziel, wissen_id)
                    schluessel = f"{marke}_{ziel}"
                    treffer[schluessel] += beste_id == wissen_id
                    kosinus[schluessel].append(eigen)

            verschiebungsverlust.append(
                kosinus["roh_thema"][-1] - kosinus["versch_thema"][-1]
            )
            if nr % 10 == 0:
                print(f"  {nr}/{len(probe)}")

        n = len(probe)
        print("\n" + "=" * 72)
        print("DER ENRICHER-WEG — was die Verschiebung kostet")
        print("=" * 72)
        for schluessel, name in (
            ("roh_thema",        "Frage roh        → Themenvektoren"),
            ("versch_thema",     "Frage VERSCHOBEN → Themenvektoren  (der Enricher)"),
            ("roh_destillat",    "Frage roh        → Destillat (alt)"),
            ("versch_destillat", "Frage VERSCHOBEN → Destillat (alt)"),
        ):
            med = statistics.median(kosinus[schluessel])
            ueber = sum(1 for k in kosinus[schluessel] if k >= WISSEN_RETRIEVAL_SCHWELLE)
            print(f"  {name:52s} Rang 1: {treffer[schluessel]:2d}/{n}  "
                  f"median={med:.4f}  ueber {WISSEN_RETRIEVAL_SCHWELLE}: {ueber:2d}/{n}")

        print(f"\n  Verlust durch die Verschiebung (Themenvektoren): "
              f"median={statistics.median(verschiebungsverlust):+.4f}")
        print("\n  Gemessen mit ECHTEN Zielen und dem staerksten Cluster-Faktor")
        print("  ('glut', 0.30). Das ist der unguenstigste Fall — der Verlust im")
        print("  Betrieb liegt darunter, die Zahl ist eine OBERGRENZE.")
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    messen(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
