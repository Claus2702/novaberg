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
from memory.repositories.autonomous_wissen_repository import (
    AutonomousWissenRepository,
    Bibliotheksfrage,
    Bibliothekszeile,
)
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
        """Läuft in jedem Turn — der Enricher fragt, die Abfrage entscheidet.

        **Bleibt True, obwohl es seit dem 19.08.2026 auch einen Zettel gibt.**
        Quelle und Zettel sind zwei Rollen desselben Silos und schließen
        einander nicht aus (`novaberg-convention-nmcp.md` §6a): Die Quelle
        fließt bei, ohne dass jemand sie bestellt; der Zettel wird bestellt,
        wenn die Äußerung danach fragt. Wer die Quelle beim Bau des Zettels
        abschaltet, nimmt der Bibliothek ihr Beifließen und tauscht eine
        Lücke gegen die andere.
        """
        return True

    @property
    def router_intents(self) -> list[str]:
        """Keine Intent-Kürzel — die Erkennung läuft über den Aushang."""
        return []

    @property
    def router_prompt(self) -> str:
        """Der Zettel am schwarzen Brett — Merkmale der Äußerung.

        Bis zum 19.08.2026 trug dieser Manager **keinen** Zettel: Die
        Bibliothek war angebunden wie ein Gedächtnis und nicht wie eine
        Quelle, die man befragen kann. Sie floss bei jedem Turn bei, und
        niemand konnte sie **bestellen** — weder der Mensch (*„Was hast du
        selbst dazu erarbeitet?"*) noch sie selbst. Der Befund steht als
        Lücke schon in `novaberg-agent-dateien_k.md` §3.0c.

        **Der Zettel spricht die Sprache des Empfangs** (§3.2): Er benennt
        Merkmale der Äußerung und keine Operationen — der Empfang kennt die
        Fachsprache keiner Abteilung und darf sie nicht kennen.

        **Er enthält sich über die Nachbarn** (§3.0c, §3.6b). *„Weißt du was
        über X"* heißt „such in allem, was du hast"; dieser Zettel sagt
        allein, woran man erkennt, dass in **selbst Erarbeitetem** etwas zu
        holen ist. Ob zusätzlich anderswo zu suchen wäre, ist ein Urteil
        über andere Anbieter, und kein Zettel darf das.

        Nachbedingung: nichtleerer Text, der die beiden Management-Felder
        benennt. Ohne sie wäre der Zettel eine Beschreibung ohne Wirkung.
        """
        return """
ERARBEITETES WISSEN ABFRAGEN:
Setze management_action = "agent" wenn:
1. Der User danach fragt, was SIE SELBST zu einem Thema erarbeitet hat:
   "Was hast du selbst zu ... herausgefunden?", "Was ist bei deiner
   Beschaeftigung mit ... rausgekommen?", "Was hast du dir zu ... angelesen?"
2. Der User den Stand ihres eigenen Wissens zu einem Thema wissen will:
   "Kennst du dich mit ... aus?", "Weisst du was ueber ...?",
   "Hast du zu ... schon was zusammengetragen?"
3. Der User nach dem Umfang oder Bestand dieses Wissens fragt:
   "Wozu hast du ueberhaupt schon gearbeitet?", "Hast du dazu was liegen?"

Erkennungsmerkmal:
- Der Bezug geht auf EIGENE, VORHER ERARBEITETE Durchdringung eines Themas —
  etwas, das sie sich selbst zusammengetragen hat, bevor die Frage kam.
- Entscheidend ist der Bezug, nicht die Satzform: Auch eine schlichte
  Sachfrage passt, wenn ihre Antwort in einer eigenen Ausarbeitung steht.
- "selbst", "eigenes", "erarbeitet", "angelesen" sind starke Merkmale.

Bei Erkennung:
  management_action = "agent"
  management_target = "wissen"
  management_target_typ = ""

BEISPIELE (alle -> management_action = "agent"):
- "Was hast du selbst zur Resonanz erarbeitet?"
- "Kennst du dich mit assoziativem Gedaechtnis aus?"
- "Hast du zu Gravitationswellen schon was zusammengetragen?"
- "Wozu hast du dir eigentlich schon Wissen aufgebaut?"
"""

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
        # Die Abfrage liegt im Repository und nicht hier: Seit dem 19.08.2026
        # ist die Bibliothek über zwei Eingänge erreichbar — als Quelle, die
        # beifließt, und als Dienst, den man bestellt. Zwei Abfragen über
        # denselben Bestand ergäben zwei Rangfolgen, die auseinanderlaufen
        # (`novaberg-convention-nmcp.md` §6a.1).
        vektor_str: str = embedding_zu_pgvector_str(such_vektor)

        try:
            zeilen: list[Bibliothekszeile] = AutonomousWissenRepository.suchen(
                Bibliotheksfrage(
                    postgres_url = postgres_url,
                    user_id      = user_id,
                    character_id = character_id,
                    vektor_str   = vektor_str,
                    typ          = "wissen",
                    schwelle     = WISSEN_RETRIEVAL_SCHWELLE,
                    limit        = WISSEN_RETRIEVAL_TOP_K,
                )
            )
        except psycopg2.Error:
            # Hier verschluckt, im Dienst nicht: Die Quelle hat keinen
            # Ausgang, über den sie "ich konnte nicht" sagen könnte — sie
            # trägt bei oder sie trägt nicht bei. Deshalb reicht das
            # Repository den Fehler hoch, statt ihn selbst zu schlucken:
            # Der Dienst braucht die Unterscheidung, die Quelle hat sie nicht.
            logger.exception(
                "WissenManager: Abfrage der Bibliothek fehlgeschlagen — "
                "kein Bibliothekskontext in diesem Turn"
            )
            return []

        # ── Ausgabe-Verifikation ────────────────────
        eintraege: list[ContextEntry] = []
        for zeile in zeilen:
            # Der Pool erwartet 0.0 bis 1.0; die Bibliothek rechnet mit den
            # Knoten-Konstanten und laeuft bis zum Cap. Ohne die Umrechnung
            # schluege ein Bibliothekseintrag im Reducer jeden KZG-Treffer,
            # weil dort "hoechstes Gewicht gewinnt" — und das waere eine
            # Rangfolge aus zwei Skalen statt aus zwei Bedeutungen.
            normiert: float = min(zeile.gewicht_decay / LZG_KNOTEN_GEWICHT_CAP, 1.0)

            eintraege.append({
                "quelle":  "plugin_wissen",
                "subtyp":  zeile.modus,
                "inhalt":  f"{zeile.thema}: {zeile.zusammenfassung}",
                "gewicht": normiert,
                "meta":    {
                    "praefix":   f"Wissen/{zeile.thema}",
                    "thema":     zeile.thema,
                    "dateipfad": zeile.dateipfad,
                    "status":    zeile.status,
                    "cosine":    round(zeile.cosine, 4),
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
