"""Pixie-Agent: synapsen_decay — täglicher Decay-Lauf für das Synapsen-Netz.

Orchestriert einmal täglich drei entkoppelte Wartungsaufgaben (Konzept
synapsen_k §9, P6; queue-verfall_k §11):

  1. run_node_decay      — materialisiert gewicht_decay je aktivem lzg_knoten
                           (exponentieller Verfall aus verstaerkt_am) und
                           deaktiviert Knoten unter LZG_KNOTEN_MIN_GEWICHT.
  2. delete_expired_entries — TTL-Cleanup alter pipeline_log-Einträge.
  3. verfall_lauf        — dasselbe für die Shadow-Queue, mit **eigener Rate**
                           (30 Tage statt 787) und eigenem Audit-Eintrag.
  4. alle_faeden_nachfuehren — faltet `ausschlag_aktuell` jedes Prägungsfadens
                           auf heute. Der Verfall **zwischen** zwei Berührungen
                           hat kein Ereignis, an dem er hängen könnte.

**Der dritte Schritt steht hier und nicht in einem eigenen Agenten**, weil er
so keinen zusätzlichen Platz im Heartbeat kostet — bei einem einzigen
seriellen Platz konkurriert jeder neue periodische Auftrag mit den
bestehenden. Ein eigener Agent bleibt die richtige Wahl, falls der
Queue-Verfall später eine andere Frequenz braucht als der Knoten-Verfall.

Struktur nach dem Konventions-Träger synapsen_promotion: kein LangGraph
(build_graph gibt None), die Arbeit läuft synchron in invoke. Der Agent selbst
öffnet keine DB-Connection — die Fachlogik lebt in den memory-Modulen
(lzg_knoten, pipeline_log), der Audit läuft über db_manager.

Gated durch SYNAPSEN_DECAY_AKTIV (doppelt: in periodic_task und in invoke).
Halbreaktivierung (§9.3) ist NICHT hier, sondern im Schreibpfad von
memory/lzg_knoten.py (P6 Teil B).
"""

import logging
import uuid

from agents.base import AgentState, BaseAgent, PeriodicTask
from config import (
    DEFAULT_USER_ID,
    PIXIE_DECAY_INTERVALL_SEKUNDEN,
    PIXIE_DECAY_PRIORITAET,
    POSTGRES_URL,
    SYNAPSEN_DECAY_AKTIV,
)
from memory import lzg_knoten, pipeline_log, praegung
from memory.repositories.shadow_auftrag_repository import ShadowAuftragRepository
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.synapsen_decay")

# Forensik-Korrelation im pipeline_log (analog synapsen_promotion).
QUELLE = "pixie"
NODE = "synapsen_decay"


class SynapsenDecayAgent(BaseAgent):
    """Täglicher Decay-Lauf für lzg_knoten plus pipeline_log-TTL-Cleanup.

    Ein globaler Bulk-Lauf über alle Paar-Partitionen — die Decay-Formel ist
    knoten-lokal, ein globaler Sweep ist bit-identisch zur Paar-Schleife.
    """

    @property
    def name(self) -> str:
        # Muss dem Verzeichnisnamen entsprechen (Discovery-Konvention).
        return "synapsen_decay"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["synapsen_decay"]

    @property
    def lastart(self) -> str:
        """Die CPU-Spur. Reine Rechnung ueber Bestandswerte, kein Modellaufruf."""
        return "cpu"

    @property
    def graph_eignung(self) -> list[str]:
        # Reiner Pixie-Hintergrund-Agent, keine User-Graph-Eignung.
        return ["pixie"]

    def build_graph(self):
        """Kein LangGraph — die Arbeit läuft synchron in invoke().

        Rückgabe None ist Pflicht: Der Default-invoke der Basisklasse würde
        sonst build_graph().invoke(state) auf None aufrufen und crashen. Da
        invoke() hier komplett selbst implementiert ist, wird build_graph()
        nie zur Graph-Ausführung verwendet.
        """
        return None

    def periodic_task(self) -> PeriodicTask | None:
        """Registriert den täglichen Lauf — oder gar nicht, wenn deaktiviert.

        Rückgabe None => kein Scheduling-Eintrag (Agent bleibt dormant). Das
        ist das erste von zwei Gates (zweites in invoke).
        """
        if not SYNAPSEN_DECAY_AKTIV:
            logger.info(
                "synapsen_decay deaktiviert (SYNAPSEN_DECAY_AKTIV=false) — "
                "kein periodisches Scheduling"
            )
            return None
        return PeriodicTask(
            name="synapsen_decay",
            priority=PIXIE_DECAY_PRIORITAET,
            interval=PIXIE_DECAY_INTERVALL_SEKUNDEN,
            description="Täglicher Synapsen-Decay (lzg_knoten) + pipeline_log-TTL-Cleanup (P6)",
        )

    @staticmethod
    def _audit_log(user_id: str, aufgabe: str, status: str, ergebnis: str) -> None:
        """Schreibt einen hintergrund_log-Audit-Eintrag (Audit-Pflicht).

        Failsafe: Bei DB-Fehler nur logger.critical, kein Retry — verhindert
        Endlos-Rekursion bei kaputter Audit-Senke. Muster wie synapsen_promotion.
        """
        try:
            db_manager.execute(
                """
                INSERT INTO hintergrund_log
                    (user_id, aufgabe, status, ergebnis, verarbeitet_am)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, aufgabe, status, ergebnis),
            )
        except Exception as ex:
            logger.critical(
                f"hintergrund_log-INSERT fehlgeschlagen: {ex} "
                f"(verlorener Audit-Eintrag: {aufgabe}/{status}/{ergebnis[:100]})"
            )

    @staticmethod
    def _log_forensik(run_id: str, inhalt: dict) -> None:
        """Schreibt eine pipeline_log-Zeile (best-effort).

        Die Forensik ist nice-to-have (Lauf-Start/-Ende), nicht kritisch für
        den Decay selbst. Ein Schreibfehler (z. B. nicht initialisierter Buffer
        im Pixie-Kontext) darf den Lauf NICHT killen — daher gekapselt mit
        logger.warning statt Weiterreichen der Exception.
        """
        try:
            # Bewusst paar-los (Kategorie C, Chat 104): Der Decay-Lauf ist ein
            # Wartungslauf ueber ALLE Paare, kein Turn — user_id/character_id bleiben
            # NULL. Kein vergessener Anschluss, sondern korrekte Semantik.
            pipeline_log.log_berechnung(
                turn_id=run_id, node=NODE, quelle=QUELLE, inhalt=inhalt
            )
        except Exception as ex:
            logger.warning(
                f"pipeline_log-Forensik nicht geschrieben ({inhalt.get('phase', '?')}): {ex}"
            )

    def _faltung_lauf(self, run_id: str) -> dict:
        """Faltet `ausschlag_aktuell` jedes Praegungsfadens auf heute.

        Der Verfall **zwischen** zwei Beruehrungen hat kein Ereignis, an dem er
        haengen koennte: `ausschlag_aktuell_nachfuehren` laeuft, wenn eine
        Beruehrung entsteht, und dazwischen steht der Wert still
        (`FALTUNG-OHNE-PERIODISCHEN-LAUF`).

        **Eigener Audit-Eintrag wie beim Queue-Verfall.** Ohne ihn waere
        hinterher nicht zu unterscheiden, ob der Lauf ueber einen leeren
        Bestand ging oder gar nicht lief — und ein leerer Bestand ist am Anfang
        der Regelfall.

        Vorbedingung: keine.
        Nachbedingung: Jeder Faden traegt einen auf heute gerechneten Wert;
        `gefaltet == gesamt`, wenn nichts ausfiel.
        Fehlerfaelle: Keine eigenen — die Fachfunktion meldet selbst und
        liefert ihren Fehler im Ergebnis.

        Args:
            run_id: Die Korrelation dieses Tageslaufs.

        Returns:
            Das Ergebnis von `alle_faeden_nachfuehren`.
        """
        # ── Eingabe-Validierung ─────────────────────
        self._audit_log(
            DEFAULT_USER_ID, "praegung_faltung", "gestartet", f"run_id={run_id}",
        )

        # ── Verarbeitung ────────────────────────────
        ergebnis: dict = praegung.alle_faeden_nachfuehren(POSTGRES_URL)

        # ── Ausgabe-Verifikation ────────────────────
        stand: str = f"{ergebnis['gefaltet']} von {ergebnis['gesamt']}"
        if ergebnis["error"]:
            self._audit_log(
                DEFAULT_USER_ID, "praegung_faltung", "fehler",
                f"{stand}: {ergebnis['error']}",
            )
        else:
            self._audit_log(
                DEFAULT_USER_ID, "praegung_faltung", "erledigt",
                f"{stand} Faeden nachgefuehrt",
            )
        logger.info(f"Synapsen-Decay: {stand} Praegungsfaeden nachgefuehrt")
        return ergebnis

    def invoke(self, state: AgentState) -> AgentState:
        """Führt den täglichen Decay-Lauf aus (globaler Bulk-Lauf).

        Ablauf (EVA):
          Eingabe      — Feature-Gate prüfen.
          Verarbeitung — run_node_decay + delete_expired_entries (entkoppelt,
                         beide laufen unabhängig, Fehler werden aggregiert).
          Ausgabe      — Ergebnis in state["ergebnis"], Status + Audit setzen.

        pipeline_log-Forensik: zwei Zeilen (Lauf gestartet / Lauf beendet),
        korreliert über einen synthetischen run_id (kein echter Turn im
        periodischen Lauf).
        """
        # --- Eingabe (EVA): zweites Gate ---
        if not SYNAPSEN_DECAY_AKTIV:
            logger.info(
                "synapsen_decay invoke übersprungen (SYNAPSEN_DECAY_AKTIV=false)"
            )
            state["ergebnis"] = {"aktiv": False}
            state["status"] = "abgeschlossen"
            return state

        run_id = f"synapsen_decay:{uuid.uuid4()}"
        logger.info(f"Synapsen-Decay-Lauf startet (run_id={run_id})")
        self._audit_log(DEFAULT_USER_ID, "synapsen_decay", "gestartet", f"run_id={run_id}")
        self._log_forensik(run_id, {"phase": "start"})

        try:
            # --- Verarbeitung: zwei entkoppelte Wartungsläufe ---
            # 1. Knoten-Decay (global über alle Paar-Partitionen).
            decay_result = lzg_knoten.run_node_decay(POSTGRES_URL)
            logger.info(
                f"Synapsen-Decay: {decay_result['total_processed']} Knoten verarbeitet, "
                f"{decay_result['deactivated_count']} deaktiviert"
            )

            # 2. TTL-Cleanup des pipeline_log (unabhängig vom Decay-Ergebnis —
            #    läuft auch, wenn der Decay einen Fehler meldete).
            cleanup_result = pipeline_log.delete_expired_entries(POSTGRES_URL)
            logger.info(
                f"Synapsen-Decay: {cleanup_result['deleted_count']} "
                f"pipeline_log-Einträge per TTL entfernt"
            )

            # 3. Verfall der Shadow-Queue (novaberg-queue-verfall_k.md §11).
            #    Ein dritter Schritt im vorhandenen Tageslauf kostet **keinen
            #    zusätzlichen Platz im Heartbeat** — bei einem einzigen
            #    seriellen Platz ist das ausschlaggebend.
            #
            #    **Eigener Audit-Eintrag**, und nur dieser Schritt hat einen:
            #    Ein Lauf, der drei Dinge tut, färbt bei einem Fehlschlag im
            #    dritten den ganzen Auftrag rot. Ohne getrennte Zeile ist
            #    hinterher nicht unterscheidbar, ob der Verfall lief und
            #    nichts fand, oder ob er gar nicht lief. Die beiden Schritte
            #    darüber haben diese Trennung noch nicht.
            self._audit_log(
                DEFAULT_USER_ID, "queue_verfall", "gestartet", f"run_id={run_id}",
            )
            queue_result = ShadowAuftragRepository.verfall_lauf(POSTGRES_URL)
            if queue_result["error"]:
                self._audit_log(
                    DEFAULT_USER_ID, "queue_verfall", "fehler", queue_result["error"],
                )
            else:
                self._audit_log(
                    DEFAULT_USER_ID, "queue_verfall", "erledigt",
                    f"{queue_result['verarbeitet']} verarbeitet, "
                    f"{queue_result['deaktiviert']} deaktiviert",
                )
            logger.info(
                f"Synapsen-Decay: {queue_result['verarbeitet']} Queue-Aufträge "
                f"verarbeitet, {queue_result['deaktiviert']} deaktiviert"
            )

            # 4. Faltung des Praegungs-Ausschlags (novaberg-node-praegung.md
            #    §7, S36 der Rechenkette). Vierter Schritt aus demselben Grund
            #    wie der dritte: kein zusaetzlicher Platz im Heartbeat.
            faltung_result = self._faltung_lauf(run_id)

            # --- Ausgabe (EVA): Ergebnis + Fehler aggregieren ---
            fehler = [
                e
                for e in (
                    decay_result["error"], cleanup_result["error"],
                    queue_result["error"], faltung_result["error"],
                )
                if e is not None
            ]
            state["ergebnis"] = {
                "decay": decay_result,
                "cleanup": cleanup_result,
                "queue_verfall": queue_result,
                "praegung_faltung": faltung_result,
            }

            ende_inhalt = {
                "phase": "ende",
                "total_processed": decay_result["total_processed"],
                "deactivated_count": decay_result["deactivated_count"],
                "deleted_count": cleanup_result["deleted_count"],
                "queue_verarbeitet": queue_result["verarbeitet"],
                "queue_deaktiviert": queue_result["deaktiviert"],
                "faeden_gefaltet": faltung_result["gefaltet"],
                "faeden_gesamt": faltung_result["gesamt"],
            }

            if fehler:
                # Teil-Fehlschlag: Lauf lief durch, aber mindestens eine
                # Wartungsaufgabe meldete einen (fail-soft) DB-Fehler.
                fehler_text = "; ".join(fehler)
                state["status"] = "fehler"
                state["fehler"] = fehler_text
                ende_inhalt["status"] = "fehler"
                ende_inhalt["fehler"] = fehler_text
                self._log_forensik(run_id, ende_inhalt)
                self._audit_log(
                    DEFAULT_USER_ID, "synapsen_decay", "fehler", fehler_text
                )
                logger.error(
                    f"Synapsen-Decay-Lauf mit Fehler beendet (run_id={run_id}): {fehler_text}"
                )
                return state

            state["status"] = "abgeschlossen"
            ende_inhalt["status"] = "abgeschlossen"
            self._log_forensik(run_id, ende_inhalt)
            self._audit_log(
                DEFAULT_USER_ID,
                "synapsen_decay",
                "erledigt",
                f"{decay_result['total_processed']} verarbeitet, "
                f"{decay_result['deactivated_count']} deaktiviert, "
                f"{cleanup_result['deleted_count']} Logs entfernt",
            )
            logger.info(f"Synapsen-Decay-Lauf abgeschlossen (run_id={run_id})")
            return state

        except Exception as ex:
            # Unerwarteter Fehler (nicht die fail-soft DB-Fehler oben, sondern
            # z. B. ein Programmier-/Importfehler in einer memory-Funktion).
            fehler_text = str(ex)
            state["status"] = "fehler"
            state["fehler"] = fehler_text
            self._log_forensik(
                run_id, {"phase": "ende", "status": "exception", "fehler": fehler_text}
            )
            self._audit_log(DEFAULT_USER_ID, "synapsen_decay", "fehler", fehler_text)
            logger.exception(
                f"Synapsen-Decay-Lauf abgebrochen (run_id={run_id}): {fehler_text}"
            )
            return state
