"""WissenRueckwegAgent — was im Gespräch entstand, wandert in die Dateien.

Spezifikation: docs/novaberg-agent-dateien_k.md §4b.

**Der Rückweg schließt den Kreis.** Bis heute führt kein Weg von einem Turn in
eine Wissensdatei: `ergebnis_ablegen` hat genau einen Aufrufer, den
Recherche-Agenten, und der arbeitet autonom im Hintergrund. Entsteht aus einem
Turn eine Erinnerung, kann derselbe Fund auch in eine themenbezogene Datei —
**eingeordnet, nicht angehängt.**

**Von den drei Wegen aus §4b.1a ist einer verdrahtet: das Überlebende.** Was
die Promotion ins Langzeitgedächtnis geschafft hat, hat die Bewährung über
Tage bereits bestanden; eine eigene Wartelogik daneben wäre eine zweite
Antwort auf dieselbe Frage. Die beiden anderen Wege — das Einprägsame
(`salienz_roh ≥ 0,7`, sofort) und das Zugehörige — sind je eine Zeile an ihrem
Einreihpunkt und ausdrücklich nicht Teil dieses Zuschnitts.

**Die LLM-Spur, und das ist keine Wahl.** Die Zuordnung ist nach §4a.1 eine
Modellentscheidung über die Zusammenfassungen; die Einarbeitung ist eine
zweite. Der Auslöser sitzt deshalb in der Promotion, der Vorgang aber nicht:
`synapsen_promotion` fährt die CPU-Spur, und ein Agent dieser Spur, der doch
das Sprachmodell ruft, scheitert laut.

**Er schreibt ausschließlich in ihre eigene Zone.** Die Wurzel ist
`WISSENSSPEICHER_WURZEL`; freigegebene Fremdverzeichnisse haben hier keinen Weg
hinein — nicht „werden nicht benutzt", sondern sind nicht erreichbar (§7).
"""

import logging
import uuid
from dataclasses import dataclass

from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    POSTGRES_URL,
    WISSENSSPEICHER_WURZEL,
)
from memory import pipeline_log
from memory.repositories.autonomous_wissen_repository import (
    AutonomousWissenRepository,
    WissensEintrag,
)
from services.model_services import EmbedRequest, model_service
from tools.db_manager import db_manager

from agents.base import AgentState, BaseAgent
from agents.wissen_rueckweg.einarbeitung import einarbeiten
from agents.wissen_rueckweg.herkunft import herkunft_lesen
from agents.wissen_rueckweg.zuordnung import kandidaten_laden, ziel_bestimmen

logger = logging.getLogger("ki_server.agents.wissen_rueckweg")


@dataclass(frozen=True)
class Ausgang:
    """Warum ein Durchlauf ohne Schnitt endete — die vier Angaben zusammen.

    Sie reisen gemeinsam ins Protokoll und werden gemeinsam gelesen: Der
    Grund allein sagt nicht, ob die Bibliothek leer war oder das Modell
    abgelehnt hat, und die Kandidatenzahl allein sagt nichts über beides.
    """

    grund:      str
    detail:     str
    quelle:     str
    kandidaten: int

#: Forensik-Markierung für das pipeline_log: quelle = Produzent, node = Stufe.
QUELLE: str = "pixie"
NODE: str = "wissen_rueckweg"

#: Der Aufgabenname in der Shadow-Queue. Er gehört genau dieser Rolle
#: (`F-AUFGABE-1`) und steht im Routing des Pixie-Routers.
AUFGABE: str = "wissen_rueckweg"


class WissenRueckwegAgent(BaseAgent):
    """Ordnet einen Fund einer Wissensdatei zu und arbeitet ihn dort ein."""

    @property
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        return "wissen_rueckweg"

    @property
    def faehigkeiten(self) -> list[str]:
        """Auskunft für Menschen und Anzeige — nie Auswahlkriterium."""
        return ["fund_zuordnen", "fund_einarbeiten"]

    @property
    def lastart(self) -> str:
        """Die LLM-Spur: zwei Modellaufrufe je Fund — Zuordnung und Absatz.

        Die Angabe wird erzwungen und nicht geglaubt: Ein Agent der CPU-Spur,
        der doch das Sprachmodell ruft, scheitert laut, statt die schnelle
        Spur zu verstopfen.
        """
        return "llm"

    @property
    def graph_eignung(self) -> list[str]:
        """Nur der Hintergrund — dieser Vorgang wird nicht gesprochen.

        Er hat deshalb weder Aushang noch Quote: Über seine Zustellung
        entscheidet niemand, er hängt an einer Queue.
        """
        return ["pixie"]

    @property
    def zustellart(self) -> str:
        """Queue — und ausdrücklich nicht abgeleitet.

        Ohne diese Angabe leitete die Vorgabe aus `periodic_task() is None`
        auf `queue`, was hier zwar stimmt, aber aus dem falschen Grund: Der
        Agent hat keine periodische Aufgabe, **weil** er auf einen Auslöser
        wartet, nicht umgekehrt.
        """
        return "queue"

    @property
    def context_user(self) -> str:
        """Das Gedächtnis des Menschen — der Fund stammt aus seinem Paar."""
        return "user"

    def build_graph(self) -> None:
        """Kein Subgraph — der Vorgang ist eine Kette ohne Verzweigung.

        Zuordnung, Einarbeitung, Verstärkung laufen nacheinander, und jeder
        Schritt hat genau einen Ausgang zum nächsten oder das Ende. Ein
        Graph darüber wäre eine Beschreibung ohne Entscheidung.
        """
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Arbeitet einen Auftrag ab: zuordnen, einarbeiten, verstärken.

        Vorbedingung: `state["parameter"]` trägt den Queue-Auftrag mit
        `kontext` (der verdichtete Fund), optional `turn_id`, und das Paar
        steht in `kontext`/`parameter`.
        Nachbedingung: `status` ist "abgeschlossen" — auch dann, wenn nichts
        geschrieben wurde. **Nicht geschrieben ist der Regelfall und kein
        Fehler**: Der häufigste Ausgang ist „keine Datei passt", und er ist
        billiger als jede erzwungene Zuordnung.
        Fehlerfaelle: fehlendes Paar, leerer Fund, gescheiterter Embed-Aufruf
        — jeder mit `status="fehler"` und einer Zeile im Protokoll.
        """
        # ── Eingabe-Validierung ─────────────────
        auftrag: dict = state.get("parameter", {}) or {}
        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID
        character_id: str = state["kontext"].get("character_id", "") or ASSISTANT_USER_ID
        material: str = (auftrag.get("kontext", "") or "").strip()
        thema: str = (auftrag.get("thema", "") or "").strip()
        quelle: str = herkunft_lesen(auftrag.get("modus", ""))

        span_id = pipeline_log.span_start(
            turn_id=NODE, node=NODE, quelle=QUELLE,
            inhalt={"phase": "start", "thema": thema, "material": quelle},
            user_id=user_id, character_id=character_id,
        )

        if not material:
            return self._abbruch(
                state, span_id, user_id=user_id, character_id=character_id,
                grund="Auftrag ohne Fundtext — es gibt nichts einzuarbeiten",
            )

        # ── Verarbeitung ────────────────────────
        try:
            embedding: list[float] = model_service.embed.submit_sync(
                EmbedRequest(text=material)
            ).embedding
        except Exception as fehler:  # noqa: BLE001 — der Worker meldet die Ursache
            logger.exception(
                "%s: Rückweg: Einbettung des Fundes fehlgeschlagen",
                type(fehler).__name__,
            )
            return self._abbruch(
                state, span_id, user_id=user_id, character_id=character_id,
                grund=f"Einbettung fehlgeschlagen: {type(fehler).__name__}",
            )

        kandidaten: list[dict] = kandidaten_laden(user_id, character_id, embedding)
        entscheidung: dict | None = ziel_bestimmen(material, kandidaten)

        if entscheidung is None or entscheidung["ziel"] is None:
            grund: str = (
                entscheidung.get("begruendung", "") if entscheidung else "Aufruf unbrauchbar"
            )
            return self._ohne_schnitt(
                state, span_id, user_id=user_id, character_id=character_id,
                ausgang=Ausgang("keine_zuordnung", grund, quelle, len(kandidaten)),
            )

        ziel: dict = entscheidung["ziel"]
        ergebnis: dict = einarbeiten(
            ziel["dateipfad"], WISSENSSPEICHER_WURZEL, entscheidung["kern"],
        )

        if not ergebnis.get("geschrieben"):
            return self._ohne_schnitt(
                state, span_id, user_id=user_id, character_id=character_id,
                ausgang=Ausgang(
                    ergebnis.get("grund", "unbekannt"), ziel["dateipfad"],
                    quelle, len(kandidaten),
                ),
            )

        self._verstaerken(ziel, ergebnis.get("ergaenzung", ""), user_id, character_id)

        # ── Ausgabe-Verifikation ────────────────
        pipeline_log.log_db_write(
            turn_id=NODE, node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={
                "dateipfad": ziel["dateipfad"], "marke": ergebnis.get("marke"),
                "version": ergebnis.get("version"), "material": quelle,
                "kandidaten": len(kandidaten), "kern": entscheidung["kern"][:300],
            },
            user_id=user_id, character_id=character_id,
        )
        pipeline_log.span_end(
            span_id=span_id, turn_id=NODE, node=NODE, quelle=QUELLE,
            inhalt={"phase": "ende", "geschrieben": True},
            user_id=user_id, character_id=character_id,
        )
        logger.info(
            "Rückweg: %s — %s eingearbeitet (Material %s, %d Kandidaten)",
            ziel["dateipfad"], ergebnis.get("marke"), quelle, len(kandidaten),
        )

        state["status"] = "abgeschlossen"
        state["ergebnis"] = {
            "dateipfad": ziel["dateipfad"], "marke": ergebnis.get("marke"),
            "version": ergebnis.get("version"), "material": quelle,
        }
        return state

    def _verstaerken(
        self, ziel: dict, ergaenzung: str, user_id: str, character_id: str,
    ) -> None:
        """Zieht die Bibliothekszeile nach: Häufigkeit, Gewicht, Zusammenfassung.

        Vorbedingung: Der Schnitt in der Datei ist gelungen.
        Nachbedingung: `haeufigkeit` ist um eins gestiegen, `gewicht_roh` um
        den Reinforcement-Boost, `verstaerkt_am` steht auf jetzt.
        Fehlerfaelle: Ein Fehlschlag wird gemeldet und **nicht geworfen** —
        die Datei ist bereits geändert und umkehrbar; ein Abbruch hier machte
        aus einer nachgezogenen Zeile einen abgebrochenen Vorgang.

        **Die Zusammenfassung wächst mit, und das ist keine Kosmetik.** Sie
        trägt den Embed-Text der Zeile (`F-EMBED-1`); bliebe sie stehen,
        während die Datei wächst, wäre der Zuwachs über die Suche nicht mehr
        auffindbar — die Datei wüchse und würde unsichtbarer.
        """
        # ── Eingabe-Validierung ─────────────────
        zusammenfassung: str = (ziel.get("zusammenfassung") or "").strip()
        if ergaenzung.strip():
            zusammenfassung = f"{zusammenfassung} {ergaenzung.strip()}".strip()
        else:
            logger.warning(
                "Rückweg: keine Ergänzung für die Zusammenfassung von %s — die "
                "Datei ist gewachsen, ihr Embed-Text nicht", ziel["dateipfad"],
            )

        # ── Verarbeitung ────────────────────────
        try:
            bestand: list[dict] = db_manager.select(
                "SELECT beobachter, typ, modus, status, salienz_anfang "
                "FROM autonomous_wissen WHERE id = %s", (ziel["id"],),
            )
            if not bestand:
                logger.error(
                    "Rückweg: Bibliothekszeile %s verschwunden zwischen Zuordnung "
                    "und Verstärkung — die Datei ist geändert, die Zeile nicht",
                    ziel["id"],
                )
                return

            zeile: dict = bestand[0]
            AutonomousWissenRepository.speichern(POSTGRES_URL, WissensEintrag(
                dateipfad       = ziel["dateipfad"],
                user_id         = user_id,
                character_id    = character_id,
                beobachter      = zeile["beobachter"],
                thema           = ziel.get("thema", ""),
                zusammenfassung = zusammenfassung,
                typ             = zeile["typ"],
                modus           = zeile["modus"],
                status          = zeile["status"],
                salienz_anfang  = float(zeile["salienz_anfang"]),
            ))
        except Exception as fehler:  # noqa: BLE001 — die Datei ist schon geschrieben
            logger.exception(
                "%s: Rückweg: Verstärkung der Zeile %s fehlgeschlagen — die Datei "
                "trägt den Absatz, die Zeile zählt ihn nicht",
                type(fehler).__name__, ziel["dateipfad"],
            )

    def _ohne_schnitt(
        self, state: AgentState, span_id: uuid.UUID, *, user_id: str,
        character_id: str, ausgang: Ausgang,
    ) -> AgentState:
        """Beendet den Durchlauf, ohne zu schreiben — der Regelfall.

        Nachbedingung: `status="abgeschlossen"`, und das Protokoll trägt den
        Grund samt Zahl der Kandidaten. **Ein Durchlauf ohne Schnitt ist kein
        Fehlschlag**; ohne diese Zeile wäre er von einem ausgefallenen aber
        nicht zu unterscheiden.
        """
        pipeline_log.span_end(
            span_id=span_id, turn_id=NODE, node=NODE, quelle=QUELLE,
            inhalt={
                "phase": "ende", "geschrieben": False, "grund": ausgang.grund,
                "detail": ausgang.detail[:200], "material": ausgang.quelle,
                "kandidaten": ausgang.kandidaten,
            },
            user_id=user_id, character_id=character_id,
        )
        logger.info(
            "Rückweg: nichts geschrieben — %s (%s), %d Kandidaten",
            ausgang.grund, ausgang.detail[:120], ausgang.kandidaten,
        )
        state["status"] = "abgeschlossen"
        state["ergebnis"] = {"geschrieben": False, "grund": ausgang.grund}
        return state

    def _abbruch(
        self, state: AgentState, span_id: uuid.UUID, *, user_id: str,
        character_id: str, grund: str,
    ) -> AgentState:
        """Beendet den Durchlauf als Störung — mit Zeile im Protokoll."""
        logger.error("Rückweg: %s", grund)
        pipeline_log.span_end(
            span_id=span_id, turn_id=NODE, node=NODE, quelle=QUELLE,
            inhalt={"phase": "ende", "geschrieben": False, "fehler": grund},
            user_id=user_id, character_id=character_id,
        )
        state["status"] = "fehler"
        state["fehler"] = grund
        return state
