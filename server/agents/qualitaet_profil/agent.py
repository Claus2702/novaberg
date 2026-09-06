"""QualitaetProfilAgent — die sechs Qualitaeten je Traeger, taeglich.

**Dieser Agent ist aus `synapsen_decay` herausgeloest, und der Grund ist
gemessen** `[06.09.2026]`. Der Schritt lief dort seit dem 03.09.2026 als
achter von zehn — und hat **nie einen einzigen Traeger profiliert**: zwei
Laeufe im `hintergrund_log`, beide `0 von 20`, im Log jedes Mal
`SpurVerletzungError`.

**Der Riegel hat richtig gehandelt, nicht falsch.** Der Tageslauf faehrt die
`cpu`-Spur, und dort ist das Sprachmodell verriegelt, weil ein Modellaufruf
die schnelle Spur minutenlang haelt (`services/model_services/spur.py`). Sein
eigener Docstring sagt *„Reine Rechnung ueber Bestandswerte, kein
Modellaufruf"* — die Zusicherung stand da und wurde beim Einbau gebrochen.
Ein Profil kostet **einen Modellaufruf je Traeger**.

**Warum ein eigener Agent und nicht `lastart = "llm"` am Tageslauf:** Der
Tageslauf ist zu neun Zehnteln reine Rechnung. Ihn in die langsame Spur zu
haengen, um einen Schritt willen, machte aus einer Zusicherung eine
Ausnahme — und die uebrigen neun Schritte warteten hinter dem Modell.

**`lastart` steht hier absichtlich nicht.** Die Vorgabe in `agents/base.py`
ist `llm`, und sie ist die richtige: Ein Agent, der das Sprachmodell ruft,
gehoert in die langsame Spur. Wer sie hier wiederholte, machte aus einer
tragenden Vorgabe eine Kopie, die spaeter auseinanderlaufen kann.

Der Agent traegt keine Fachlogik: Auswahl, Modellaufruf und Schreibpfad
liegen in `memory/quality_profile.py`, hier steht der Ausloeser plus Audit
und Forensik.
"""

import logging
import uuid

from agents.base import AgentState, BaseAgent, PeriodicTask
from config import (
    DEFAULT_USER_ID,
    PIXIE_QUALITAET_INTERVALL_SEKUNDEN,
    PIXIE_QUALITAET_PRIORITAET,
    POSTGRES_URL,
)
from memory import pipeline_log, quality_profile
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.qualitaet_profil")


class QualitaetProfilAgent(BaseAgent):
    """Profiliert die naechsten Traeger — gedeckelt, einmal am Tag."""

    @property
    def name(self) -> str:
        return "qualitaet_profil"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["qualitaet_profil"]

    @property
    def graph_eignung(self) -> list[str]:
        # Reiner Pixie-Hintergrund-Agent, keine User-Graph-Eignung.
        return ["pixie"]

    def periodic_task(self) -> PeriodicTask | None:
        """Registriert den taeglichen Lauf.

        **Der Takt ist eine Setzung des Eigentuemers, 06.09.2026: einmal am
        Tag.** Gemessen an diesem Tag standen **350 Kandidaten** offen; bei
        `QUALITAET_PROFIL_JE_LAUF = 20` fuellt sich der Bestand damit in rund
        **18 Tagen**. Ein engerer Takt waere moeglich — die Zahl steht hier,
        damit die Wahl nachrechenbar bleibt und nicht spaeter als
        Selbstverstaendlichkeit gilt.
        """
        return PeriodicTask(
            name="qualitaet_profil",
            priority=PIXIE_QUALITAET_PRIORITAET,
            interval=PIXIE_QUALITAET_INTERVALL_SEKUNDEN,
            description="Qualitaetsprofile der naechsten Traeger (gedeckelt)",
        )

    def build_graph(self):
        return None

    @staticmethod
    def _audit_log(user_id: str, status: str, ergebnis: str) -> None:
        """Schreibt einen hintergrund_log-Eintrag (Audit-Pflicht).

        Failsafe: Bei DB-Fehler nur `logger.critical`, kein Retry — sonst
        droht Endlos-Rekursion bei kaputter Audit-Senke. Muster wie
        `ziel_decay`.
        """
        try:
            db_manager.execute(
                """
                INSERT INTO hintergrund_log
                    (user_id, aufgabe, status, ergebnis, verarbeitet_am)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (user_id, "qualitaet_profil", status, ergebnis),
            )
        except Exception as ex:  # noqa: BLE001 — siehe Docstring
            logger.critical(
                f"hintergrund_log-INSERT fehlgeschlagen: {ex} (verlorener "
                f"Audit-Eintrag: qualitaet_profil/{status}/{ergebnis[:100]})"
            )

    @staticmethod
    def _log_forensik(run_id: str, inhalt: dict) -> None:
        """Schreibt eine `pipeline_log`-Zeile (best effort).

        Paar-los: Ein Wartungslauf gehoert zu keinem Turn und zu keinem Paar.
        Ein Forensik-Schreibfehler darf den Lauf nicht kosten.
        """
        try:
            pipeline_log.log_berechnung(
                turn_id=run_id, node="qualitaet_profil", quelle="pixie",
                inhalt=inhalt,
            )
        except Exception as ex:  # noqa: BLE001 — siehe Docstring
            logger.warning(f"pipeline_log-Forensik nicht geschrieben: {ex}")

    def invoke(self, state: AgentState) -> AgentState:
        """Loest den Profil-Lauf aus.

        Ablauf (EVA):
          Eingabe      — keine; die Auswahl trifft `candidates_load`.
          Verarbeitung — `profil_lauf` profiliert bis zum Deckel.
          Ausgabe      — Ergebnis in `state["ergebnis"]`, Status und Audit.

        **Ein Totalausfall ist ein Fehler, kein Ergebnis.** `profil_lauf`
        setzt `error`, wenn es Kandidaten gab und keiner durchkam — genau der
        Melder, der den Spur-Riegel am 05.09.2026 sichtbar gemacht hat.
        Der Status folgt ihm; ein Lauf ohne Kandidaten bleibt `erledigt`.

        Args:
            state: Der Agenten-Zustand.

        Returns:
            Der Zustand mit `ergebnis`, `status` und ggf. `fehler`.
        """
        run_id: str = f"qualitaet_profil:{uuid.uuid4()}"
        self._audit_log(DEFAULT_USER_ID, "gestartet", f"run_id={run_id}")

        try:
            ergebnis: dict = quality_profile.profil_lauf(POSTGRES_URL)
        except Exception as fehler:  # noqa: BLE001 — der Lauf darf Pixie nicht kosten
            logger.exception("Qualitaetsprofil-Lauf abgebrochen")
            self._audit_log(DEFAULT_USER_ID, "fehler", str(fehler))
            self._log_forensik(run_id, {"phase": "ende", "fehler": str(fehler)})
            state["status"] = "fehler"
            state["fehler"] = str(fehler)
            return state

        # ── Ausgabe-Verifikation ────────────────
        bilanz: str = (
            f"{ergebnis['profiliert']} von {ergebnis['versucht']} Traegern "
            f"profiliert, Bestand {ergebnis['traeger_gesamt']}"
        )
        state["ergebnis"] = ergebnis

        if ergebnis.get("error"):
            state["status"] = "fehler"
            state["fehler"] = ergebnis["error"]
            self._audit_log(DEFAULT_USER_ID, "fehler", ergebnis["error"])
            logger.error(f"Qualitaetsprofil-Lauf: {ergebnis['error']}")
        else:
            state["status"] = "erledigt"
            self._audit_log(DEFAULT_USER_ID, "erledigt", bilanz)
            logger.info(f"Qualitaetsprofil-Lauf: {bilanz}")

        self._log_forensik(run_id, {"phase": "ende", **ergebnis})
        return state
