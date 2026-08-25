"""DateienIndexAgent — der Waechter am Zeitplan.

Spezifikation: docs/novaberg-agent-dateien_k.md §5 und §8.3.

Er haelt den Index gegen die freigegebenen Verzeichnisse: neu indizieren,
Geaendertes auffrischen, Verschwundenes markieren. Er **liest** Dateien und
schreibt ausschliesslich in die Indextabelle — er legt keine Datei an,
aendert keine und loescht keine.

**Kein Aushang, keine Quote, keine Negativfaelle.** Er laeuft nach Zeitplan
und wird nicht gewaehlt; von einem Dienst, ueber dessen Zustellung niemand
entscheidet, einen Aushang zu verlangen waere eine Forderung ohne
Gegenstand (`novaberg-convention-nmcp.md` §11).

**Der Takt steht auf None, und das ist eine Messentscheidung.** §8.3
verlangt, dass die Kadenz der Aenderungsrate des Verzeichnisses folgt und
nicht dem Gefuehl. Diese Rate ist nicht erhoben; bis dahin laeuft der
Waechter von Hand ueber `/admin/dateien/index`. Ein geratener Takt waere
genau die Sorte Zahl, gegen die dieses Projekt an anderer Stelle bezahlt
hat.
"""

import logging
import uuid
from pathlib import Path

from agents.base import AgentState, BaseAgent, PeriodicTask
from agents.dateien_index.indizieren import Erschliessung, erschliessen
from agents.dateien_index.speicher import (
    bestand_je_wurzel,
    stilllegen,
    suchtext_bauen,
    wurzeln_aktiv,
    zeile_schreiben,
)
from agents.dateien_index.wandern import (
    GRUND_AUSSERHALB,
    GRUND_GELOESCHT,
    Wanderung,
    wandern,
)
from agents.dateien_wurzeln.aussenrand import wurzel_pruefen
from config import DATEIEN_INDEX_MAX_PRO_LAUF, DEFAULT_USER_ID
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.dateien_index")

AUFGABE: str = "dateien_index"


class DateienIndexAgent(BaseAgent):
    """Haelt den Dateienindex gegen die freigegebenen Verzeichnisse."""

    @property
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        return "dateien_index"

    @property
    def faehigkeiten(self) -> list[str]:
        """Auskunft fuer Menschen und Anzeige — nie Auswahlkriterium."""
        return ["dateien_indizieren", "dateien_auffrischen", "dateien_markieren"]

    @property
    def graph_eignung(self) -> list[str]:
        """Reiner Hintergrunddienst — er wird nie im Gespraech gewaehlt."""
        return ["pixie"]

    @property
    def lastart(self) -> str:
        """Die LLM-Spur, obwohl das Wandern reine Rechnung ist.

        Die Lastart ist eine Eigenschaft des ganzen Aufrufbaums und nicht
        der Klasse (§5.3): Wandern, Hashen und die Blockkarte kosten kein
        Modell, Thema und Stichwoerter je Datei sehr wohl. Ein Waechter,
        der sich fuer rechenfrei erklaerte, verstopfte die schnelle Spur —
        und die Angabe wird erzwungen, nicht geglaubt.
        """
        return "llm"

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst ausdruecklich nicht tut."""
        return [
            "indiziert nur die freigegebenen Wurzeln",
            "legt keine Datei an, aendert keine und loescht keine",
            "schreibt ausschliesslich in die Indextabelle",
            "liest keinen Dateiinhalt in den Index — nur die Karte und was das "
            "Modell darueber sagt",
        ]

    def build_graph(self) -> None:
        """Kein LangGraph — die Arbeit laeuft synchron in `invoke`.

        Rueckgabe None ist Pflicht: Der Default-`invoke` der Basisklasse
        riefe sonst `build_graph().invoke(state)` auf None auf.
        """
        return None

    def periodic_task(self) -> PeriodicTask | None:
        """Kein Zeitplan, solange die Aenderungsrate nicht gemessen ist.

        Nachbedingung: None — der Dienst bleibt schlafend und wird von Hand
        angestossen. §8.3 verlangt einen Takt, der der Aenderungsrate des
        Verzeichnisses folgt; die ist nicht erhoben, und eine geratene Zahl
        waere hier dasselbe wie eine geratene Schwelle.
        """
        return None

    @staticmethod
    def _audit(status: str, ergebnis: str) -> None:
        """Schreibt einen `hintergrund_log`-Eintrag (Audit-Pflicht).

        Vorbedingung: `status` ist `gestartet`, `erledigt` oder `fehler`.
        Nachbedingung: Eine Zeile im Audit, oder eine kritische Logmeldung.
        Kein Wiederholversuch — eine kaputte Audit-Senke darf keine Schleife
        erzeugen.
        """
        try:
            db_manager.execute(
                "INSERT INTO hintergrund_log "
                "(user_id, aufgabe, status, ergebnis, verarbeitet_am) "
                "VALUES (%s, %s, %s, %s, NOW())",
                (DEFAULT_USER_ID, AUFGABE, status, ergebnis),
            )
        except Exception as fehler:  # noqa: BLE001 — die Audit-Senke darf nichts reissen
            logger.critical(
                "hintergrund_log-INSERT fehlgeschlagen (%s: %s) — verlorener "
                "Eintrag: %s/%s/%s",
                type(fehler).__name__, fehler, AUFGABE, status, ergebnis[:100],
            )

    def invoke(self, state: AgentState) -> AgentState:
        """Faehrt einen Lauf ueber alle aktiven Wurzeln.

        Vorbedingung: keine — der Lauf entscheidet selbst, was zu tun ist.
        Nachbedingung: `state["ergebnis"]` traegt die Bilanz je Wurzel und
        in Summe; `status` ist `abgeschlossen` oder `fehler`. Der Audit
        traegt `gestartet` und danach genau eines von beiden.

        **Was die Obergrenze stehenlaesst, steht in der Bilanz.** Eine
        stille Kappung saehe aus wie ein vollstaendiger Lauf — dieselbe
        Form wie eine Kappung vor einem Grenzwert.
        """
        # ── Eingabe-Validierung ─────────────────
        lauf_id: str = f"dateien_index:{uuid.uuid4()}"
        wurzeln: list[dict] = wurzeln_aktiv()
        if not wurzeln:
            logger.info("Waechter: keine aktive Freigabe — nichts zu tun")
            self._audit("erledigt", f"{lauf_id}: keine aktive Wurzel")
            state["ergebnis"] = {"wurzeln": 0, "indiziert": 0, "offen": 0}
            state["status"] = "abgeschlossen"
            return state

        logger.info("Waechter: Lauf startet (%s), %d Wurzeln", lauf_id, len(wurzeln))
        self._audit("gestartet", f"{lauf_id}: {len(wurzeln)} Wurzeln")

        # ── Verarbeitung ────────────────────────
        bilanz: list[dict] = []
        budget: int = DATEIEN_INDEX_MAX_PRO_LAUF
        fehler: list[str] = []

        for wurzel in wurzeln:
            try:
                teil, budget = self._wurzel_bearbeiten(wurzel, budget)
                bilanz.append(teil)
            except Exception as ausnahme:  # noqa: BLE001 — eine Wurzel darf den Lauf nicht reissen
                logger.exception(
                    "%s: Waechter: Wurzel %s ('%s') abgebrochen",
                    type(ausnahme).__name__, wurzel["id"], wurzel["pfad"],
                )
                fehler.append(f"Wurzel {wurzel['id']}: {type(ausnahme).__name__}")

        # ── Ausgabe-Verifikation ────────────────
        indiziert: int = sum(t["indiziert"] for t in bilanz)
        offen: int = sum(t["offen"] for t in bilanz)
        gescheitert: int = sum(t.get("gescheitert", 0) for t in bilanz)
        ergebnis: dict = {
            "lauf_id": lauf_id,
            "wurzeln": len(wurzeln),
            "indiziert": indiziert,
            "offen": offen,
            # **Steht neben `fehler`, nicht darin.** `fehler` sammelt
            # Ausnahmen je WURZEL — ein abgebrochener Lauf. `gescheitert`
            # zaehlt Dateien, die der Lauf ueberging, ohne dass etwas warf.
            # Beides in einen Topf zu werfen machte aus einem stillen Verlust
            # einen lauten Fehler und aus einem lauten Fehler eine Statistik.
            "gescheitert": gescheitert,
            "fehler": fehler,
            "je_wurzel": bilanz,
        }

        if offen:
            logger.warning(
                "Waechter: %d Dateien bleiben offen — die Obergrenze von %d je "
                "Lauf war erreicht. Der Lauf ist damit NICHT vollstaendig",
                offen, DATEIEN_INDEX_MAX_PRO_LAUF,
            )

        # **`offen: 0` heisst nicht "alles ist drin".** Es heisst, die
        # Obergrenze hat nichts stehengelassen. Wer den Unterschied nicht
        # nennt, liefert die Sprache eines fertigen Laufs fuer einen, dem
        # Dateien fehlen — der Lauf vom 20.08.2026 meldete genau das.
        if gescheitert:
            logger.error(
                "Waechter: %d Dateien sind GESCHEITERT und stehen nicht im "
                "Index — der Lauf ist trotz 'offen %d' nicht vollstaendig",
                gescheitert, offen,
            )

        if fehler:
            self._audit("fehler", f"{lauf_id}: {'; '.join(fehler)[:400]}")
            state["status"] = "fehler"
            state["fehler"] = "; ".join(fehler)
        else:
            self._audit(
                "erledigt",
                f"{lauf_id}: {indiziert} indiziert, {offen} offen, "
                f"{gescheitert} gescheitert, {len(wurzeln)} Wurzeln",
            )
            state["status"] = "abgeschlossen"

        state["ergebnis"] = ergebnis
        logger.info(
            "Waechter: Lauf beendet (%s) — %d indiziert, %d offen, "
            "%d gescheitert, %d Fehler",
            lauf_id, indiziert, offen, gescheitert, len(fehler),
        )
        return state

    def _wurzel_bearbeiten(self, wurzel: dict, budget: int) -> tuple[dict, int]:
        """Faehrt eine Wurzel ab und schreibt, was sich geaendert hat.

        Vorbedingung: `wurzel` ist eine aktive Zeile aus `dateien_wurzeln`.
        Nachbedingung: (Bilanz, verbliebenes Budget). Die Bilanz nennt
        `offen` — die Zahl der Dateien, die diese Runde nicht mehr
        geschafft hat.

        **Der Aussenrand wird erneut geprueft**, obwohl die Freigabe ihn
        beim Anlegen bestanden hat: Zwischen Freigabe und Lauf kann der Rand
        enger geworden sein, und eine alte Zeile ist kein Recht.
        """
        befund = wurzel_pruefen(wurzel["pfad"])
        if not befund.ok:
            logger.error(
                "Waechter: Wurzel %s ('%s') haelt dem heutigen Rand nicht "
                "stand — uebersprungen: %s",
                wurzel["id"], wurzel["pfad"], befund.grund,
            )
            return {
                "wurzel_id": wurzel["id"], "pfad": wurzel["pfad"],
                "indiziert": 0, "offen": 0, "uebersprungen": befund.grund,
            }, budget

        basis: Path = befund.aufgeloest
        bestand: dict[str, dict] = bestand_je_wurzel(wurzel["id"])
        lauf: Wanderung = wandern(basis, bestand)

        zu_tun = lauf.neu + lauf.geaendert
        arbeit = zu_tun[:budget] if budget > 0 else []
        offen: int = len(zu_tun) - len(arbeit)

        indiziert: int = 0
        gescheitert: list[tuple[str, str]] = []
        for fund in arbeit:
            erschliessung: Erschliessung = erschliessen(
                fund.pfad_absolut, basis, fund.pfad_relativ,
            )
            # **Ein Fehlschlag je Datei hatte bis zum 20.08.2026 kein Fach.**
            # `erschliessen` gibt bei unbrauchbarer Modellantwort ein leeres
            # Ergebnis zurueck; der Lauf verbrauchte dafuer sein Budget,
            # schrieb keine Zeile und meldete nichts. Sichtbar war es allein
            # daran, dass `indiziert + offen` die Zahl der Kandidaten nicht
            # traf — fuenf von 160 Dateien fielen so heraus, dieselben in
            # jedem Lauf (novaberg-bugs.md, INDEXLAUF-VERSCHWEIGT-DATEIFEHLER).
            if not erschliessung.thema:
                gescheitert.append(
                    (fund.pfad_relativ, "Erschliessung ohne Thema — Modellantwort unbrauchbar"),
                )
                continue
            zeilen_id = zeile_schreiben(
                wurzel["id"], fund, erschliessung,
                suchtext_bauen(erschliessung, fund),
            )
            if zeilen_id is not None:
                indiziert += 1
            else:
                gescheitert.append(
                    (fund.pfad_relativ, "Zeile nicht geschrieben — Speicherfehler"),
                )

        # Zwei Ausgaenge, zwei Gruende. Der Unterschied ist nicht kosmetisch:
        # `deleted` beantwortet "wo war das noch" mit "sie ist weg",
        # `excluded` sagt, dass wir nicht mehr hinsehen — und nimmt die
        # Zeile zurueck, sobald der Filter es wieder tut.
        stilllegen([z["id"] for z in lauf.verschwunden], GRUND_GELOESCHT)
        stilllegen([z["id"] for z in lauf.ausserhalb], GRUND_AUSSERHALB)

        zahlen: dict[str, int] = lauf.zahlen()

        # ── Ausgabe-Verifikation ────────────────
        # **Die Identitaet ist die Probe, und sie ist der ganze Riegel.**
        # Kandidaten = geschrieben + stehengelassen + gescheitert. Geht sie
        # nicht auf, ist eine Datei zwischen die Faelle gefallen — und genau
        # diese Differenz war der Defekt: Wer `offen: 0, fehler: []` liest,
        # haelt einen Lauf fuer vollstaendig, dem fuenf Dateien fehlen.
        kandidaten: int = len(zu_tun)
        if kandidaten != indiziert + offen + len(gescheitert):
            logger.error(
                "Waechter: Wurzel %s ('%s') — %d Kandidaten, aber %d "
                "geschrieben + %d offen + %d gescheitert. Die Bilanz geht "
                "nicht auf; eine Datei faellt zwischen die Faelle",
                wurzel["id"], basis, kandidaten, indiziert, offen, len(gescheitert),
            )

        if gescheitert:
            logger.error(
                "Waechter: Wurzel %s ('%s') — %d von %d Dateien nicht "
                "erschlossen: %s",
                wurzel["id"], basis, len(gescheitert), kandidaten,
                ", ".join(pfad for pfad, _ in gescheitert)[:300],
            )

        logger.info(
            "Waechter: Wurzel %s ('%s') — %s, davon %d geschrieben, %d offen, "
            "%d gescheitert",
            wurzel["id"], basis, zahlen, indiziert, offen, len(gescheitert),
        )
        # **Die Gruende gehen mit in die Bilanz, nicht nur ihre Anzahl.**
        # Wer `uebergangen: 3` liest und nie erfaehrt, warum, hat eine Zahl
        # statt einer Auskunft — und genau das verspricht die Zusicherung in
        # `wandern.py` nicht. `[gemessen]` — 18.08.2026: Der Grundtext hatte
        # drei Erzeuger und keinen Leser ausserhalb der Zeugen.
        return {
            "wurzel_id": wurzel["id"], "pfad": str(basis),
            "indiziert": indiziert, "offen": offen, **zahlen,
            "uebergangen_gruende": [
                {"pfad": pfad, "grund": grund} for pfad, grund in lauf.uebergangen
            ],
            # Der abgeschnittene Ast gehoert in dieselbe Auskunft. Er ist
            # sonst der einzige Teil des Laufs, ueber den die Bilanz
            # schweigt — und ein nicht betretenes Verzeichnis sieht in ihr
            # genauso aus wie ein leeres.
            "uebergangene_verzeichnisse_gruende": [
                {"pfad": pfad, "grund": grund}
                for pfad, grund in lauf.uebergangene_verzeichnisse
            ],
            "gescheitert": len(gescheitert),
            "gescheitert_gruende": [
                {"pfad": pfad, "grund": grund} for pfad, grund in gescheitert
            ],
        }, max(0, budget - len(arbeit))
