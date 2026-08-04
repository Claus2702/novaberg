"""Wissens-Manager — die Bibliothek als sechste Kontextquelle des Enrichers.

Nova erarbeitet Wissen in Dateien (`WIS-3`). Dieser Manager macht es im
Gespräch auffindbar — **über die Datenbank, nicht über den Dateiinhalt.**

| Stufe | Was | Kosten |
|---|---|---|
| **1 — Metadaten** | Embedding-Nähe gegen `zusammenfassung` | eine SQL-Abfrage |
| 2 — Datei | den Block lesen, der wirklich gebraucht wird | Dateizugriff, **noch nicht gebaut** |

Gebaut ist Stufe 1. Sie liefert Thema und Zusammenfassung; das reicht in den
meisten Fällen als Kontext und kostet nichts als eine Abfrage. Erst wenn die
Zusammenfassung nicht reicht, lohnt der Griff zur Datei — dafür fehlt der
Lesepfad in `tools/dateien/` noch (Spezifikation: §7.3).

**Der Suchschlüssel kommt aus dem State, nicht aus einem eigenen Embedding.**
`state["such_vektor"]` trägt den Vektor, mit dem in diesem Turn auch KZG und
LZG gesucht haben — die Frage plus Novas Motivation. Ein eigenes Embedding
zu rechnen hieße, denselben Prompt ein zweites Mal einzubetten (~1,6 s je
Turn) und dabei die Wahrnehmungs-Gravitation zu verlieren. Die Bibliothek ist
Langzeitgedächtnis in Dateiform; sie wird mit demselben Ohr gehört.

Spezifikation: docs/novaberg-autonomous-wissen_k.md §7.2, §7.3, §7.5, §11.
"""

import logging

import psycopg2
import redis
from config import (
    LZG_KNOTEN_GEWICHT_CAP,
    WISSEN_RETRIEVAL_SCHWELLE,
    WISSEN_RETRIEVAL_TOP_K,
)
from graph.context_entry import ContextEntry
from memory.utils import embedding_zu_pgvector_str

from plugins.base import BaseManager

logger = logging.getLogger("ki_server.plugins.wissen")


class WissenManager(BaseManager):
    """Liest Novas erarbeitete Bibliothek über ihre Metadaten."""

    @property
    def ziel(self) -> str:
        """Der Name, unter dem die Registry diesen Manager führt."""
        return "wissen"

    @property
    def immer_aktiv(self) -> bool:
        """Läuft in jedem Turn — der Enricher fragt, die Abfrage entscheidet."""
        return True

    def execute(
        self,
        writes:       list[dict],
        user_id:      str,
        redis_client: redis.Redis,
        postgres_url: str,
    ) -> int:
        """Kein Schreibpfad — die Bibliothek wird von Pixie gefüllt, nicht im Gespräch.

        Die Methode ist abstrakt in `BaseManager` und muss deshalb existieren.
        Sie tut nichts und sagt das laut, wenn doch jemand mit Schreibaufträgen
        kommt: Ein Manager, der Aufträge stillschweigend verschluckt, sieht wie
        einer aus, der sie ausführt.

        Vorbedingung: keine. Nachbedingung: gibt immer 0 zurück.
        """
        if writes:
            logger.error(
                f"WissenManager: {len(writes)} Schreibauftraege erhalten und "
                f"verworfen — die Bibliothek wird von den Pixie-Agenten "
                f"geschrieben, nicht aus dem Gespraech"
            )
        return 0

    def enrich_entries(self, state: dict, postgres_url: str) -> list[ContextEntry]:
        """Liefert Bibliothekstreffer als ContextEntry-Liste.

        Vorbedingung: `state` trägt `such_vektor`, `user_id` und
        `character_id`. Fehlt der Suchschlüssel, lief in diesem Turn keine
        Gedächtnissuche — dann gibt es auch nichts zu durchsuchen, und die
        leere Liste ist die richtige Antwort, kein Fehler.
        Nachbedingung: höchstens `WISSEN_RETRIEVAL_TOP_K` Einträge, alle mit
        `quelle="plugin_wissen"` und einem Gewicht in [0.0, 1.0].
        Fehlerfälle: Ein Datenbankfehler wird protokolliert und ergibt eine
        leere Liste — der Enricher fängt ihn ohnehin ab, aber dann ohne zu
        sagen, welcher Teil gescheitert ist.

        Mapping je Eintrag:
          quelle  = "plugin_wissen"
          subtyp  = der Modus, aus dem das Wissen stammt
          inhalt  = "{thema}: {zusammenfassung}"
          gewicht = gewicht_decay / cap, auf [0,1] gebracht
          meta    = praefix, thema, dateipfad, cosine, status
        """
        # ── Eingabe-Validierung ─────────────────────
        such_vektor: list = state.get("such_vektor") or []
        user_id:     str  = state.get("user_id", "")
        character_id: str = state.get("character_id", "")

        if not such_vektor:
            # Kein Fehler: In diesem Turn hat keine Gedaechtnisschicht
            # gesucht, es gibt also keinen Schluessel. Auf DEBUG, weil der
            # Fall bei jedem Kaltstart eintritt.
            logger.debug("WissenManager: kein Suchschluessel im State — keine Abfrage")
            return []

        if not user_id or not character_id:
            logger.error(
                f"WissenManager: unvollstaendiges Paar (user_id={user_id!r}, "
                f"character_id={character_id!r}) — keine Abfrage. Ohne beide "
                f"Kennungen waere der Treffer aus einer fremden Beziehung"
            )
            return []

        # ── Verarbeitung ────────────────────────────
        vektor_str: str = embedding_zu_pgvector_str(such_vektor)

        try:
            conn = psycopg2.connect(postgres_url)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT thema, zusammenfassung, dateipfad, modus, status,
                               gewicht_decay,
                               1 - (themen_embedding <=> %s::vector) AS cosine
                        FROM   autonomous_wissen
                        WHERE  user_id = %s AND character_id = %s
                          AND  aktiv = TRUE
                          AND  typ = 'wissen'
                          AND  themen_embedding IS NOT NULL
                          AND  1 - (themen_embedding <=> %s::vector) >= %s
                        ORDER  BY themen_embedding <=> %s::vector
                        LIMIT  %s
                        """,
                        (
                            vektor_str, user_id, character_id, vektor_str,
                            WISSEN_RETRIEVAL_SCHWELLE, vektor_str,
                            WISSEN_RETRIEVAL_TOP_K,
                        ),
                    )
                    zeilen: list = cur.fetchall()
            finally:
                conn.close()
        except psycopg2.Error:
            logger.exception(
                "WissenManager: Abfrage der Bibliothek fehlgeschlagen — "
                "kein Bibliothekskontext in diesem Turn"
            )
            return []

        # ── Ausgabe-Verifikation ────────────────────
        eintraege: list[ContextEntry] = []
        for thema, zusammenfassung, dateipfad, modus, status, gewicht, cosine in zeilen:
            # Der Pool erwartet 0.0 bis 1.0; die Bibliothek rechnet mit den
            # Knoten-Konstanten und laeuft bis zum Cap. Ohne die Umrechnung
            # schluege ein Bibliothekseintrag im Reducer jeden KZG-Treffer,
            # weil dort "hoechstes Gewicht gewinnt" — und das waere eine
            # Rangfolge aus zwei Skalen statt aus zwei Bedeutungen.
            normiert: float = min(float(gewicht) / LZG_KNOTEN_GEWICHT_CAP, 1.0)

            eintraege.append({
                "quelle":  "plugin_wissen",
                "subtyp":  modus or "",
                "inhalt":  f"{thema}: {zusammenfassung}",
                "gewicht": normiert,
                "meta":    {
                    "praefix":   f"Wissen/{thema}",
                    "thema":     thema,
                    "dateipfad": dateipfad,
                    "status":    status or "",
                    "cosine":    round(float(cosine), 4),
                },
            })

        if eintraege:
            logger.info(
                f"WissenManager: {len(eintraege)} Bibliothekstreffer "
                f"(Cosinus {eintraege[0]['meta']['cosine']:.3f} bis "
                f"{eintraege[-1]['meta']['cosine']:.3f}, Schwelle "
                f"{WISSEN_RETRIEVAL_SCHWELLE})"
            )

        return eintraege
