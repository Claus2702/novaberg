"""Nachbettung der Themenvektoren (Konvention 4).

Legt für jede Ausarbeitung der Bibliothek je Thema eine Zeile in
`autonomous_wissen_thema` an und bettet sie ein. Für den Bestand, der vor
Konvention 4 entstanden ist, und als Reparaturweg, wenn ein Vektor fehlt.

**Die Zerlegung kommt aus `themen_zerlegen`, nicht aus einer eigenen Formel.**
Zwei Zerlegungen ergäben zwei Mengen von Themenvektoren, und der Unterschied
fiele erst auf, wenn jemand dieselbe Frage zweimal stellt (`F-EMBED-1`).

Idempotent: Ein zweiter Lauf schreibt dieselben Zeilen und bettet nur ein, was
noch keinen Vektor hat — es sei denn, `--alle` erzwingt die Neubettung.

Aufruf im Behälter:
    python -m tools.nachbetten_themen            # nur fehlende Vektoren
    python -m tools.nachbetten_themen --alle     # alles neu einbetten
    python -m tools.nachbetten_themen --probe    # nur zählen, nichts schreiben
"""

import logging
import sys

import psycopg2
from config import POSTGRES_URL

from memory.repositories.autonomous_wissen_repository import (
    AutonomousWissenRepository,
    themen_zerlegen,
)
from memory.utils import embedding_zu_pgvector_str
from tools.reembed_all import embedding_berechnen

logger = logging.getLogger("ki_server.tools.nachbetten_themen")

# **Weder der Embedding-Aufruf noch die Literal-Formung entstehen hier neu.**
# `embedding_berechnen` geht ueber denselben Endpunkt und dasselbe Modell wie
# der Live-Betrieb und prueft die Dimension; `embedding_zu_pgvector_str` ist
# die eine Formung im Bestand. Eine eigene Fassung waere eine zweite Formel
# fuer dasselbe Speicherziel und damit genau der Versatz, den `F-EMBED-1`
# verbietet — sichtbar wuerde er erst bei einer spaeteren Neubettung.


def nachbetten(*, alle: bool = False, probe: bool = False) -> dict[str, int]:
    """Legt fehlende Themenzeilen an und bettet sie ein.

    Vorbedingung: Die Tabelle `autonomous_wissen_thema` existiert.
    Nachbedingung: Jede aktive Ausarbeitung mit nicht-leerem Themenfeld hat je
    Thema eine Zeile; ohne `probe` trägt jede davon einen Vektor.

    Args:
        alle: Auch vorhandene Vektoren neu bilden.
        probe: Nur zählen, nichts schreiben.

    Returns:
        Zählstände: Ausarbeitungen, Themen, eingebettet, übersprungen, ohne Thema.
    """
    conn = psycopg2.connect(POSTGRES_URL)
    conn.autocommit = True
    zahlen: dict[str, int] = {
        "ausarbeitungen": 0, "themen": 0, "eingebettet": 0,
        "uebersprungen": 0, "ohne_thema": 0,
    }
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, thema FROM autonomous_wissen "
                "WHERE aktiv = TRUE AND thema <> '' ORDER BY id"
            )
            eintraege: list[tuple[int, str]] = list(cur.fetchall())

        for wissen_id, themenfeld in eintraege:
            zahlen["ausarbeitungen"] += 1
            themen: list[str] = themen_zerlegen(themenfeld)
            if not themen:
                zahlen["ohne_thema"] += 1
                continue

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT thema FROM autonomous_wissen_thema "
                    "WHERE wissen_id = %s AND embedding IS NOT NULL",
                    (wissen_id,),
                )
                schon_da: set[str] = {z[0] for z in cur.fetchall()}

            paare: list[tuple[str, str | None]] = []
            for thema in themen:
                zahlen["themen"] += 1
                if thema in schon_da and not alle:
                    zahlen["uebersprungen"] += 1
                    # Der vorhandene Vektor wird gelesen statt neu gebildet —
                    # sonst schriebe `themenvektoren_schreiben` ihn als NULL
                    # zurueck, weil es den Bestand vollstaendig ersetzt.
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT embedding::text FROM autonomous_wissen_thema "
                            "WHERE wissen_id = %s AND thema = %s",
                            (wissen_id, thema),
                        )
                        treffer = cur.fetchone()
                    paare.append((thema, treffer[0] if treffer else None))
                    continue
                if probe:
                    paare.append((thema, None))
                    continue
                paare.append(
                    (thema, embedding_zu_pgvector_str(embedding_berechnen(thema)))
                )
                zahlen["eingebettet"] += 1

            if not probe:
                AutonomousWissenRepository.themenvektoren_schreiben(
                    POSTGRES_URL, wissen_id, paare,
                )
    finally:
        conn.close()

    return zahlen


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ergebnis = nachbetten(alle="--alle" in sys.argv, probe="--probe" in sys.argv)
    print(
        f"Ausarbeitungen {ergebnis['ausarbeitungen']} · "
        f"Themen {ergebnis['themen']} · "
        f"eingebettet {ergebnis['eingebettet']} · "
        f"uebersprungen {ergebnis['uebersprungen']} · "
        f"ohne Thema {ergebnis['ohne_thema']}"
    )
