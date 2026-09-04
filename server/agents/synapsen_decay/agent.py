"""Pixie-Agent: synapsen_decay — täglicher Decay-Lauf für das Synapsen-Netz.

Orchestriert einmal täglich sechs entkoppelte Wartungsaufgaben (Konzept
synapsen_k §9, P6; queue-verfall_k §11; faszination_k §7.4, §7.7):

  1. run_node_decay      — materialisiert gewicht_decay je aktivem lzg_knoten
                           (exponentieller Verfall aus verstaerkt_am) und
                           deaktiviert Knoten unter LZG_KNOTEN_MIN_GEWICHT.
  2. delete_expired_entries — TTL-Cleanup alter pipeline_log-Einträge.
  3. verfall_lauf        — dasselbe für die Shadow-Queue, mit **eigener Rate**
                           (30 Tage statt 787) und eigenem Audit-Eintrag.
  4. alle_faeden_nachfuehren — faltet `ausschlag_aktuell` jedes Prägungsfadens
                           auf heute. Der Verfall **zwischen** zwei Berührungen
                           hat kein Ereignis, an dem er hängen könnte.
  5. faeden_ohne_strang_zuordnen — holt die Strangzuordnung nach, die
                           außerhalb der Fadentransaktion läuft und deshalb
                           ausfallen darf.
  6. Strang-Richtungen und -Ladung — rechnet je Strang Annäherung oder
                           Vermeidung aus Histogramm und Charakter-Rad, dazu die
                           Stärke aus Salienz, Valenz, Anzahl und Präsenz, und
                           schreibt beides in **eine** Protokollzeile. Kein
                           Bestand: beide hängen am Zustand.

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
from agents.charakter import rad_messreihe
from config import (
    DEFAULT_USER_ID,
    PIXIE_DECAY_INTERVALL_SEKUNDEN,
    PIXIE_DECAY_PRIORITAET,
    POSTGRES_URL,
    SYNAPSEN_DECAY_AKTIV,
)
from memory import lzg_knoten, pipeline_log, praegung, quality_profile
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

    def _richtungen_protokollieren(self, run_id: str) -> int:
        """Rechnet fuer jeden Strang die Richtung und schreibt sie ins Protokoll.

        Konzept §7.7. **Kein Bestand, kein Verhalten — eine Beobachtungszeile.**
        Die Richtung haengt am Charakter-Rad und damit am Zustand; sie wird bei
        jedem Lesen neu gerechnet. Bis der Praegungszug sie liest, ist dieser
        Lauf ihr einziger Leser, und seine Protokollzeilen sind die Reihe, an
        der `PRAEGUNG_SEKTOR8_ZUG` und `PRAEGUNG_KONFRONTATION_SCHWELLE`
        kalibrierbar werden.

        **Das Rad wird je Paar geladen, nicht je Strang.** Mehrere Straenge
        eines Paares teilen dasselbe Rad; ein Ladevorgang je Strang waere
        dieselbe Abfrage mehrfach.

        Vorbedingung: keine.
        Nachbedingung: je Strang eine Zeile der Art `berechnung` unter dem
            Knoten `praegung_strang`, mit Richtung, Grund, Histogramm und dem
            Konfrontationsmass.
        Fehlerfaelle: Ein Paar ohne vollstaendiges Rad ergibt `unbestimmt` —
            der Lauf bricht nicht ab. Ein junges Paar hat noch kein Rad, und
            das ist der Regelfall am Anfang.

        Args:
            run_id: Die Korrelation dieses Tageslaufs.

        Returns:
            Zahl der protokollierten Straenge.
        """
        # ── Eingabe-Validierung ─────────────────────
        try:
            straenge: list[dict] = db_manager.select(
                "SELECT id, user_id, character_id, sektor_histogramm "
                "FROM praegung_strang ORDER BY id",
            )
        except Exception as fehler:
            logger.exception(
                f"{type(fehler).__name__}: Synapsen-Decay: Straenge fuer die "
                f"Richtung nicht lesbar — kein Eintrag dieses Laufs"
            )
            return 0

        # ── Verarbeitung ────────────────────────────
        raeder: dict[tuple[str, str], dict | None] = {}
        gezaehlt: int = 0
        for zeile in straenge:
            paar = (zeile["user_id"], zeile["character_id"])
            if paar not in raeder:
                gesammelt: dict[str, float] = {}
                for rad_art in ("zuwendung", "initiative"):
                    teil = rad_messreihe.rad_zusammenfassen(
                        rad_messreihe.reihe_laden(paar[0], paar[1], rad_art),
                    )
                    if teil:
                        gesammelt.update(teil)
                raeder[paar] = gesammelt or None

            mass = (
                praegung.konfrontationsmass(raeder[paar])
                if raeder[paar] else None
            )
            histogramm: list[int] = list(zeile["sektor_histogramm"] or [])
            richtung, grund = praegung.strang_richtung(histogramm, mass)

            # Die Ladung daneben, in derselben Zeile: Richtung **und** Staerke
            # sind die beiden Groessen, die der Praegungszug zusammen braucht
            # (§10.3, `max_j(sim_j · ladung_j)` ueber Straenge mit Annaeherung).
            # Getrennt protokolliert waeren sie im Nachhinein nicht mehr
            # demselben Zeitpunkt zuzuordnen.
            ladung = praegung.strang_staerke(POSTGRES_URL, zeile["id"]) or {}

            pipeline_log.log_berechnung(
                turn_id      = run_id,
                node         = "praegung_strang",
                quelle       = "synapsen_decay",
                inhalt       = {
                    "schritt":        "strang_richtung",
                    "strang_id":      zeile["id"],
                    "richtung":       richtung,
                    "grund":          grund,
                    "histogramm":     histogramm,
                    "konfrontation":  mass,
                    # Die Teile neben der Summe: Ohne sie ist nicht zu sehen,
                    # welcher Eingang die Zahl gemacht hat.
                    **{f"ladung_{k}": v for k, v in ladung.items()},
                },
                user_id      = paar[0],
                character_id = paar[1],
            )
            gezaehlt += 1

        # ── Ausgabe-Verifikation ────────────────────
        logger.info(
            f"Synapsen-Decay: {gezaehlt} von {len(straenge)} Strang-Richtungen "
            f"protokolliert"
        )
        return gezaehlt

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

            # 5. Nachzug der Straenge (Konzept §7.7). Die Zuordnung eines
            #    Fadens laeuft ausserhalb seiner Transaktion und darf
            #    ausfallen; dieser Lauf ist ihr Rueckweg — und zugleich der
            #    Weg, auf dem ein Bestand aus der Zeit vor der Strangschicht
            #    seine Straenge bekommt. Ueber einen vollstaendig zugeordneten
            #    Bestand laeuft er leer, und das kostet eine Abfrage.
            self._audit_log(
                DEFAULT_USER_ID, "praegung_straenge", "gestartet", f"run_id={run_id}",
            )
            strang_zugeordnet, strang_offen = praegung.faeden_ohne_strang_zuordnen(
                POSTGRES_URL
            )
            self._audit_log(
                DEFAULT_USER_ID, "praegung_straenge", "erledigt",
                f"{strang_zugeordnet} von {strang_offen} Faeden zugeordnet",
            )
            logger.info(
                f"Synapsen-Decay: {strang_zugeordnet} von {strang_offen} "
                f"Faeden einem Strang zugeordnet"
            )

            # 6. Die Richtung jedes Strangs (Konzept §7.7) — **gerechnet, nicht
            #    gespeichert.** Ein Strang ist Bestand, das Charakter-Rad ist
            #    Zustand: Es bewegte sich am 31.07.2026 binnen zwei Stunden um
            #    100 %. Eine Spalte traege damit die Antwort von gestern auf die
            #    Frage von heute.
            #
            #    **Der Schritt steht hier, weil er sonst keinen Aufrufer haette.**
            #    Der Leser der Richtung ist der Praegungszug, und der ist nicht
            #    gebaut; eine Rechenfunktion ohne Aufrufer war in dieser Schicht
            #    binnen zwei Tagen dreimal der Befund. So entsteht stattdessen
            #    eine Beobachtungsreihe im Protokoll — und genau die braucht die
            #    Kalibrierung der beiden Schwellen.
            richtungen: int = self._richtungen_protokollieren(run_id)

            # 7. Die Einfaerbung — die zweite Stimme des Verfalls (Konzept
            #    §7.9). Dieselbe Faltung, Zeitachse mal Sektorfaktor: Ein Faden
            #    aus einem negativen Sektor verliert sein **Gefuehl** schneller
            #    als seine **Ladung**. Auch sie steht nicht im Bestand, aus
            #    demselben Grund wie Richtung und Ladung — sie haengt am
            #    heutigen Tag.
            #
            #    **Und auch sie steht hier, weil ihre Leser fehlen.** Ziele,
            #    LZG-Erinnerungen und EI-Calc (§8) sind nicht gebaut; bis dahin
            #    ist diese Reihe das Material, an dem `PRAEGUNG_SEKTOR_FAKTOR`
            #    kalibrierbar wird.
            einfaerbung_result: dict = praegung.alle_einfaerbungen(POSTGRES_URL)

            # 8. Die Qualitaetsprofile — der Erzeuger der abstrakten Schicht
            #    (`novaberg-thinking-faszination_k.md` §5, §6). Ein
            #    Modellaufruf je Traeger, deshalb **gedeckelt**: 368
            #    Kandidaten standen am 03.09.2026 im Bestand, und ebenso
            #    viele Aufrufe passen nicht in einen Heartbeat-Platz.
            #
            #    **Er steht hier und nicht im Turn**, weil er nichts
            #    entscheidet, was der Turn braucht: Ein Profil beschreibt den
            #    Gegenstand und aendert sich zwischen zwei Tagen nicht. Der
            #    Turn-Pfad liest es spaeter, er erzeugt es nicht.
            #
            #    **Eigener Audit-Eintrag**, aus demselben Grund wie beim
            #    dritten Schritt: Ein Lauf ohne Kandidaten und ein Lauf, der
            #    nicht lief, sind sonst dasselbe.
            self._audit_log(
                DEFAULT_USER_ID, "qualitaet_profil", "gestartet", f"run_id={run_id}",
            )
            profil_result: dict = quality_profile.profil_lauf(POSTGRES_URL)
            if profil_result["error"]:
                self._audit_log(
                    DEFAULT_USER_ID, "qualitaet_profil", "fehler",
                    profil_result["error"],
                )
            else:
                self._audit_log(
                    DEFAULT_USER_ID, "qualitaet_profil", "erledigt",
                    f"{profil_result['profiliert']} von "
                    f"{profil_result['versucht']} Traegern profiliert, "
                    f"Bestand {profil_result['traeger_gesamt']}",
                )
            logger.info(
                f"Synapsen-Decay: {profil_result['profiliert']} von "
                f"{profil_result['versucht']} Traegern profiliert "
                f"({profil_result['gescheitert']} gescheitert)"
            )

            # --- Ausgabe (EVA): Ergebnis + Fehler aggregieren ---
            fehler = [
                e
                for e in (
                    decay_result["error"], cleanup_result["error"],
                    queue_result["error"], faltung_result["error"],
                    einfaerbung_result["error"], profil_result["error"],
                )
                if e is not None
            ]
            state["ergebnis"] = {
                "decay": decay_result,
                "cleanup": cleanup_result,
                "queue_verfall": queue_result,
                "praegung_faltung": faltung_result,
                "praegung_einfaerbung": einfaerbung_result,
                "qualitaet_profil": profil_result,
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
                "einfaerbungen": einfaerbung_result["gerechnet"],
                "einfaerbung_abstand_max": einfaerbung_result["abstand_max"],
                "profile_versucht": profil_result["versucht"],
                "profile_geschrieben": profil_result["profiliert"],
                "profile_bestand": profil_result["traeger_gesamt"],
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
