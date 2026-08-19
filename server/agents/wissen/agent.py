"""WissenAgent — die eigene Bibliothek als bestellbarer Dienst.

Spezifikation: docs/novaberg-autonomous-wissen_k.md §7.2, §7.3, §7.5 ·
docs/novaberg-convention-nmcp.md §3, §6, §6a.

**Der Bestand war angebunden wie ein Gedächtnis, nicht wie eine Quelle.**
Bis zum 19.08.2026 trug `wissen_manager` `immer_aktiv` und keinen Zettel: Die
Bibliothek floss bei jedem Turn bei, und **niemand konnte sie bestellen** —
weder der Mensch noch sie selbst. Von den drei Rollen eines Silos (§6a) trug
das eigene erarbeitete Wissen genau eine, und es war das am schlechtesten
angebundene Silo von neun.

**Er schreibt nichts.** Die Bibliothek wird von den Hintergrund-Agenten
gefüllt, nicht aus dem Gespräch. Dieses Modul importiert deshalb aus dem
Repository die Lesepfade und **nicht** `speichern` — ein Recht, das nicht im
Modul liegt, kann kein Prompt herbeireden.

**Die Suche liegt nicht hier, sondern im Repository** (§6a.1). Sie ist
dieselbe, mit der die Quelle in jedem Turn sucht; dieser Eingang wählt allein
die Tiefe. Zwei Abfragen über denselben Bestand ergäben zwei Rangfolgen, und
die Abweichung fiele erst auf, wenn jemand dieselbe Frage zweimal stellt.

**Die Tiefe ist Stufe 1 und der Dienst sagt es** (§7.3). Er liefert Thema und
Zusammenfassung, nicht den Wortlaut der Ausarbeitung — Stufe 2 ist nicht
gebaut. Das steht in `grenze` und in jeder Auskunft, weil ein unbenannter
Verzicht sich als Vollständigkeit liest.
"""

import logging

import psycopg2
from config import (
    POSTGRES_URL,
    WISSEN_AUFTRAG_TOP_K,
    WISSEN_RETRIEVAL_SCHWELLE,
)
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from memory.repositories.autonomous_wissen_repository import (
    AutonomousWissenRepository,
    Bibliotheksfrage,
    Bibliothekszeile,
)
from memory.utils import embedding_zu_pgvector_str

from agents.base import AgentState, BaseAgent, Bedarf, Korrektur
from agents.wissen.auskunft import auskunft_bauen, beleg_bauen

logger = logging.getLogger("ki_server.agents.wissen")

#: Der Typ, den dieser Dienst befragt. Die Bibliothek trägt zwei Sorten —
#: das *Was* (`wissen`) und das *Wie* (`bericht`, §7.5). Gefragt ist hier
#: immer das Was: Ein Bericht beschreibt den Suchverlauf und beantwortet
#: keine Sachfrage. Geschlossene Wahl, kein Parameter — ein Eingang, der
#: beides könnte, müsste entscheiden, und dafür gibt es kein Kriterium.
TYP_WISSEN: str = "wissen"


class WissenAgent(BaseAgent):
    """Beantwortet eine Frage aus der eigenen Bibliothek — lesen, nie schreiben."""

    @property
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen und dem Manager-Ziel."""
        return "wissen"

    @property
    def faehigkeiten(self) -> list[str]:
        """Auskunft für Menschen und Anzeige — nie Auswahlkriterium.

        Die Auswahl läuft über den Aushang (`novaberg-convention-nmcp.md`
        §3.4). Eine Liste von Verben sagt dem Empfang nicht, welche Äußerung
        dazu passt — sie hat im eigenen Bestand vier Monate keinen Leser
        gefunden.
        """
        return [
            "bibliothek_befragen",
            "bestand_beziffern",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        """Beide Graphen — auch ein eigener Gedanke darf im eigenen Wissen nachsehen.

        Der Anlass, das selbst Erarbeitete zu befragen, hängt an der Frage und
        nicht daran, wer sie gestellt hat. Der Hintergrund braucht ihn sogar
        dringender: `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT` beschreibt einen
        Agenten, der eine Bibliothek füllt, die er nie befragt.
        """
        return ["user", "pixie"]

    @property
    def lastart(self) -> str:
        """Rechenspur — dieser Dienst ruft kein Sprachmodell.

        Die Klassifikation der Äußerung hat der Empfang schon getan; was
        bleibt, ist eine Abfrage gegen einen Vektor, der im Zustand liegt.
        **Die Angabe wird erzwungen, nicht geglaubt** (`_spur_kontext`): Ein
        Modellaufruf aus diesem Aufrufbaum scheitert laut, statt die schnelle
        Spur zu verstopfen.
        """
        return "cpu"

    @property
    def negativfaelle(self) -> list[str]:
        """Äußerungen, die oberflächlich passen und nicht hierher gehören.

        Eigenschaften der Äußerung, **niemals ein anderer Dienst** (§3.6b).
        Ein Ausschlussrecht verwandelte eine Fehlzustellung in eine
        ausgebliebene: Im Fehlerfall schlösse dieser Zettel den korrekten
        Dienst mit aus, und aus dem billigen sichtbaren Fehler würde der
        teure unsichtbare.

        Die drei Grenzen liegen dort, wo die Ähnlichkeit am größten ist —
        fremdes Schriftgut, erlebte Gespräche, und das noch nicht Gewusste.
        Keine davon ist eine Fähigkeitsgrenze; alle drei sehen aus wie diese
        Sache und sind es nicht.
        """
        return [
            "eine Frage nach dem Inhalt eines vom Menschen abgelegten "
            "Schriftstuecks ('was steht in der Anleitung') — das ist fremdes "
            "Material, keine eigene Ausarbeitung",
            "eine Frage nach etwas Erlebtem ('was habe ich dir letzte Woche "
            "erzaehlt', 'worueber haben wir gesprochen') — das ist Erinnerung "
            "an ein Gespraech, keine Ausarbeitung",
            "die Bitte, etwas Neues herauszufinden oder draussen nachzusehen "
            "('finde raus', 'schau mal nach') — hier liegt nur, was schon "
            "erarbeitet ist, und nichts Neues entsteht",
            "die Bitte, etwas abzulegen oder aufzuschreiben — dieser Dienst "
            "schreibt nichts",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst ausdrücklich nicht tut.

        Die erste Zeile ist die wichtigste und steht deshalb oben: Sie ist
        der Verzicht, der sich ohne Nennung als Vollständigkeit liest.
        """
        return [
            "liefert Thema und Zusammenfassung, nicht den Wortlaut der "
            "Ausarbeitung — die zweite Stufe ist nicht gebaut (§7.3)",
            "schreibt nichts, in keiner Zone",
            "sucht nur ueber die Bedeutung; es gibt keinen Wortkanal",
            "kennt nur die Ausarbeitungen dieses Paares",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschätzter Anteil der Äußerungen je Graph.

        **25 % im Gespräch ist eine Schätzung, die widerlegt werden soll.**
        Sie liegt über der des lesenden Dienstes, und der Grund ist der
        Bestand: 274 eigene Ausarbeitungen gegen eine Handvoll freigegebener
        Verzeichnisse. Der Quotenzähler am Empfang ist der Leser, der ihr
        widersprechen kann — ohne ihn wäre die Anmeldung eine Behauptung,
        die nicht falsch sein kann (§8.2a).

        **0 % im Hintergrund ist keine Enthaltung, sondern der heutige
        Stand:** Der Impulsweg fragt selten nach dem eigenen Wissen, und
        genau das soll sich mit `RECHERCHE-LIEST-IHRE-BIBLIOTHEK-NICHT`
        ändern. Steigt die Zahl, ist das der Beleg dafür.
        """
        return {"user": 25, "pixie": 0}

    @property
    def bedarf(self) -> list[Bedarf]:
        """Der Suchschlüssel des Turns — kein zweites Embedding.

        Derselbe Vektor, mit dem in diesem Turn auch KZG, LZG und die
        Bibliothek als Quelle gesucht haben. Ein eigenes Embedding zu rechnen
        hieße, denselben Text ein zweites Mal einzubetten (~1,6 s je Turn) und
        dabei die Wahrnehmungs-Gravitation zu verlieren — **und es wäre die
        zweite Rangfolge über demselben Bestand**, gegen die §6a.1 steht.
        """
        return [
            Bedarf(
                schluessel="such_vektor",
                typ="list[float]",
                bedeutung=(
                    "Der Suchschluessel DIESES Turns, verschoben um die "
                    "Wahrnehmungs-Gravitation. NICHT das rohe Embedding der "
                    "Aeusserung."
                ),
            ),
        ]

    @property
    def ausgaenge(self) -> frozenset[str]:
        """Alle vier — und der vierte ist hier der eigentliche Zugewinn.

        Die Quelle kann nur beitragen oder schweigen. Schweigen ist keine
        Antwort: *„dazu habe ich nichts"* und *„dazu habe ich nicht
        nachgesehen"* sehen im Gespräch gleich aus. Der vierte Ausgang trennt
        beides und trägt die Zahl, an der man es nachprüfen kann.
        """
        return frozenset({"abgeschlossen", "fehler", "rueckfrage", "abgelehnt"})

    def build_graph(self) -> CompiledStateGraph:
        """Baut den Subgraphen: validieren → befragen.

        **Kein Tor und keine Klassifikation.** Dieser Dienst ändert nichts,
        also gibt es nichts zu bestätigen; und wonach gesucht wird, steht
        bereits im Suchschlüssel des Turns — ein Modellaufruf, um die Frage
        noch einmal zu deuten, wäre die zweite Deutung derselben Äußerung.
        """
        graph = StateGraph(AgentState)

        graph.add_node("validieren", self._validieren)
        graph.add_node("befragen",   self._befragen)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren", self._nach_validierung)
        graph.add_edge("befragen", END)

        return graph.compile()

    # --- Routing ---

    def _nach_validierung(self, state: AgentState) -> str:
        """Nach der Eingangsprüfung: Ende bei Fehler, sonst befragen."""
        if state["status"] == "fehler":
            return END
        return "befragen"

    # --- Eingabe-Validierung ---

    def _validieren(self, state: AgentState) -> dict:
        """Prüft Paar und Suchschlüssel, bevor eine Abfrage läuft.

        Vorbedingung: `state["kontext"]` trägt das Paar und `such_vektor`.
        Nachbedingung: Bei `status="laufend"` sind beide vorhanden.
        Fehlerfaelle: unvollständiges Paar, fehlender Suchschlüssel — beide
        als `fehler` und nicht als Ablehnung.

        **Der fehlende Suchschlüssel ist eine Störung, kein Urteil** (§6.7).
        Die Bibliothek hat genau einen Kanal, die Bedeutung; ohne Vektor gibt
        es nichts zu durchsuchen. Das an den Auftraggeber als Ablehnung zu
        geben hieße, ihm einen Mangel des Zustands als Befund über seine
        Frage zurückzumelden.
        """
        # ── Eingabe-Validierung ─────────────────
        user_id:      str = state["kontext"].get("user_id", "")
        character_id: str = state["kontext"].get("character_id", "")
        such_vektor: list = state["kontext"].get("such_vektor") or []

        logger.debug(
            "wissen._validieren: Einstieg — paar=%r/%r, vektor=%s",
            user_id, character_id, "ja" if such_vektor else "nein",
        )

        if not user_id or not character_id:
            logger.error(
                "wissen._validieren: unvollstaendiges Paar (user_id=%r, "
                "character_id=%r) — keine Abfrage. Ein Treffer ohne Paar "
                "kaeme aus einer fremden Beziehung", user_id, character_id,
            )
            return {
                "status": "fehler",
                "fehler": "Auftrag ohne vollstaendiges Paar",
                "schritte": state["schritte"] + [
                    {"node": "validieren", "ergebnis": "paar_unvollstaendig"}
                ],
            }

        if not such_vektor:
            logger.error(
                "wissen._validieren: kein Suchschluessel im Zustand — die "
                "Bibliothek hat nur den Bedeutungskanal, es gibt nichts zu "
                "durchsuchen"
            )
            return {
                "status": "fehler",
                "fehler": (
                    "Kein Suchschluessel im Turn — die Bibliothek sucht "
                    "nur ueber die Bedeutung."
                ),
                "schritte": state["schritte"] + [
                    {"node": "validieren", "ergebnis": "kein_schluessel"}
                ],
            }

        # ── Ausgabe-Verifikation ────────────────
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [
                {"node": "validieren", "ergebnis": "ok"}
            ],
        }

    # --- Die Befragung ---

    def _befragen(self, state: AgentState) -> dict:
        """Befragt die Bibliothek und baut Auskunft oder Ablehnung.

        Vorbedingung: `validieren` ist durchgelaufen; Paar und Suchschlüssel
        liegen im Kontext.
        Nachbedingung: Entweder `status="abgeschlossen"` mit einer Auskunft,
        die je Treffer eine Fundstelle trägt, oder `status="abgelehnt"` mit
        einer Korrektur, deren Beleg eine Zahl nennt.
        Fehlerfaelle: ein Datenbankfehler wird zu `fehler` — **nicht** zu
        einer Ablehnung. Ein Fehler ist eine Störung und geht den Betreiber
        an; eine Ablehnung ist ein Urteil und geht den Auftraggeber an
        (§6.7). Genau diese Trennung war der Grund, die Abfrage im
        Repository laut scheitern zu lassen statt leer zurückzukehren.
        """
        # ── Eingabe-Validierung ─────────────────
        user_id:      str = state["kontext"]["user_id"]
        character_id: str = state["kontext"]["character_id"]
        vektor_str:   str = embedding_zu_pgvector_str(state["kontext"]["such_vektor"])

        # ── Verarbeitung ────────────────────────
        try:
            treffer: list[Bibliothekszeile] = AutonomousWissenRepository.suchen(
                Bibliotheksfrage(
                    postgres_url = POSTGRES_URL,
                    user_id      = user_id,
                    character_id = character_id,
                    vektor_str   = vektor_str,
                    typ          = TYP_WISSEN,
                    schwelle     = WISSEN_RETRIEVAL_SCHWELLE,
                    limit        = WISSEN_AUFTRAG_TOP_K,
                )
            )
        except psycopg2.Error as fehler:
            logger.exception(
                "wissen._befragen: Abfrage der Bibliothek gescheitert — als "
                "Stoerung gemeldet und nicht als Ablehnung: Der Auftrag war "
                "in Ordnung, die Abfrage nicht"
            )
            return {
                "status": "fehler",
                "fehler": f"Bibliothek nicht abfragbar: {type(fehler).__name__}",
                "schritte": state["schritte"] + [
                    {"node": "befragen", "ergebnis": "db_fehler"}
                ],
            }

        logger.info(
            "wissen._befragen: %d Treffer ueber Schwelle %.2f (Tiefe %d)",
            len(treffer), WISSEN_RETRIEVAL_SCHWELLE, WISSEN_AUFTRAG_TOP_K,
        )

        if treffer:
            # ── Ausgabe-Verifikation ────────────
            return {
                "ergebnis": auskunft_bauen(treffer),
                "status": "abgeschlossen",
                "schritte": state["schritte"] + [
                    {"node": "befragen",
                     "ergebnis": f"{len(treffer)} Treffer/"
                                 f"cos={treffer[0].cosine:.4f}"}
                ],
            }

        return self._ohne_treffer(state, user_id, character_id, vektor_str)

    def _ohne_treffer(
        self,
        state:        AgentState,
        user_id:      str,
        character_id: str,
        vektor_str:   str,
    ) -> dict:
        """Baut den vierten Ausgang: Befund, Beleg mit Zahl, Vorschlag.

        Vorbedingung: die Suche über der Schwelle war leer.
        Nachbedingung: `status="abgelehnt"` mit vollständiger Korrektur.
        Fehlerfaelle: Scheitert die Erhebung des Belegs, wird die Ablehnung
        trotzdem gebaut — **ohne die Zahl und mit dem Vermerk, dass sie
        fehlt.** Eine Ablehnung, die an ihrem eigenen Beleg scheitert, wäre
        aus einem Urteil eine Störung geworden.

        **Der knappste Verfehler wird eigens geholt.** Er kostet eine zweite
        Abfrage und nur im Ablehnungsfall — dafür trennt seine Zahl *„ich
        habe nichts dazu"* von *„es lag knapp daneben"*, und das sind zwei
        verschiedene Antworten an den Menschen.
        """
        # ── Verarbeitung ────────────────────────
        bestand: int = -1
        naechste: Bibliothekszeile | None = None
        try:
            bestand = AutonomousWissenRepository.zaehlen(
                POSTGRES_URL, user_id, character_id, TYP_WISSEN,
            )
            knapp: list[Bibliothekszeile] = AutonomousWissenRepository.suchen(
                Bibliotheksfrage(
                    postgres_url = POSTGRES_URL,
                    user_id      = user_id,
                    character_id = character_id,
                    vektor_str   = vektor_str,
                    typ          = TYP_WISSEN,
                    # Ohne Schwelle: Gesucht ist der knappste Verfehler, und
                    # der liegt per Definition unter ihr.
                    schwelle     = 0.0,
                    limit        = 1,
                )
            )
            naechste = knapp[0] if knapp else None
        except psycopg2.Error:
            logger.exception(
                "wissen._ohne_treffer: Beleg nicht erhebbar — die Ablehnung "
                "geht ohne Zahl hinaus und sagt das"
            )

        beleg: str = (
            beleg_bauen(bestand, naechste, WISSEN_RETRIEVAL_SCHWELLE)
            if bestand >= 0 else
            "Der Bestand liess sich nicht zaehlen — kein Beleg zu dieser Ablehnung."
        )

        logger.info(
            "wissen._ohne_treffer: abgelehnt — Bestand %d, naechste Naehe %s",
            bestand, f"{naechste.cosine:.4f}" if naechste else "keine",
        )

        # ── Ausgabe-Verifikation ────────────────
        korrektur = Korrektur(
            befund="Dazu habe ich mir selbst noch nichts erarbeitet.",
            beleg=beleg,
            vorschlag=(
                "Nenn mir das Thema mit einem Fachwort, dann suche ich noch "
                "einmal — oder sag mir, dass ich mich damit befassen soll."
            ),
        )
        return {
            "parameter": {**state["parameter"], "korrektur": korrektur},
            "status": "abgelehnt",
            "schritte": state["schritte"] + [
                {"node": "befragen", "ergebnis": f"kein_treffer/bestand={bestand}"}
            ],
        }
