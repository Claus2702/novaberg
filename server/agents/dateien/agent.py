"""DateienAgent — der lesende Dienst am Empfang.

Spezifikation: docs/novaberg-agent-dateien_k.md §8.1, §8.1a, §8.2 · §3.1.

**Er schreibt nichts, in keiner Zone.** Der Verbund importiert die lesenden
Module und **nicht** den Schreibpfad — nicht „er benutzt ihn nicht", sondern er
hat ihn nicht (§7 Regel 2). Ein Recht, das nicht im Modul liegt, kann kein
Prompt herbeireden.

**Warum es diesen Dienst gibt, ist gemessen und nicht argumentiert** (§8.1a):
Am 18.08.2026 nannte ein Turn die Fundstelle im Wortlaut und umschrieb die
Zahlen, die in der Datei stehen — *„eine bestimmte kritische Marke"* statt
0,67379. Der Grund ist bauartbedingt: Der Enricher-Weg liefert Thema und
Zusammenfassung, nicht den Inhalt. **Fundstelle richtig, Auskunft daneben,
beides im selben Satz.** Dieser Dienst ist die Antwort darauf: Er liest.

Graph-Aufbau und Routing hier; die Fachlogik liegt in:
  klassifikation.py — wonach gesucht wird und wie tief
  suche.py          — die drei Kanäle, scharf vor unscharf (§6.3)
  zoom.py           — Karte, Block, Nadel (§6.4)
  auskunft.py       — die Beschriftung, die die Herkunft trägt (§10)
"""

import logging

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.base import AgentState, BaseAgent, Bedarf, Korrektur
from agents.dateien.auskunft import auskunft_bauen, auskunft_finden, fundstelle
from agents.dateien.klassifikation import (
    AKTION_FINDEN,
    AKTION_LESEN,
    klassifizieren,
)
from agents.dateien.suche import bestand_zaehlen, kandidaten_finden
from agents.dateien.zoom import (
    STUFE_BLOCK,
    STUFE_KARTE,
    STUFE_NADEL,
    block_holen,
    karte_lesen,
    nadel_suchen,
)

logger = logging.getLogger("ki_server.agents.dateien")

#: Die beiden Tiefen, die der Dispatch ohne Klassifikation setzen darf, plus
#: die Sammelform "agent" für den Weg über den Empfang. Geschlossene Menge —
#: ein unbekannter Wert ist ein Defekt und kein stiller Durchlauf.
AKTIONEN_KANON: frozenset[str] = frozenset({AKTION_FINDEN, AKTION_LESEN})
EINGANGS_KANON: frozenset[str] = AKTIONEN_KANON | {"agent"}


class DateienAgent(BaseAgent):
    """Beantwortet eine Frage aus den freigegebenen Unterlagen — finden und lesen."""

    @property
    def name(self) -> str:
        """Eindeutiger Name, identisch mit dem Verzeichnisnamen."""
        return "dateien"

    @property
    def faehigkeiten(self) -> list[str]:
        """Auskunft für Menschen und Anzeige — nie Auswahlkriterium.

        Die Auswahl läuft über den Aushang (`novaberg-convention-nmcp.md`
        §3.4); eine Liste von Verben sagt dem Empfang nicht, welche Äußerung
        dazu passt.
        """
        return [
            "fundstelle_suchen",
            "abschnitt_lesen",
            "wortlaut_suchen",
        ]

    @property
    def graph_eignung(self) -> list[str]:
        """Beide Graphen — auch ein eigener Gedanke darf nachsehen.

        §8.1 nennt `user` und `pixie` ausdrücklich: Der Anlass, in Unterlagen
        nachzusehen, hängt an der Frage und nicht daran, wer sie gestellt hat.
        """
        return ["user", "pixie"]

    @property
    def negativfaelle(self) -> list[str]:
        """Äußerungen, die oberflächlich passen und nicht hierher gehören.

        Eigenschaften der Äußerung, nie ein anderer Dienst — ein
        Ausschlussrecht verwandelte eine Fehlzustellung in eine ausgebliebene
        (`novaberg-convention-nmcp.md` §3.6b). Deshalb steht hier auch nichts
        über das eigene Wissen und nichts über das Netz: Ob dort **zusätzlich**
        zu suchen wäre, ist ein Urteil über andere Anbieter (§3.0c).
        """
        return [
            "eine Frage nach Weltwissen ohne Bezug auf Unterlagen "
            "('wie funktioniert Photosynthese') — das ist Wissen, keine Fundstelle",
            "eine Frage nach etwas Erlebtem ('was habe ich dir letzte Woche "
            "erzaehlt') — das ist Gedaechtnis, keine Datei",
            "die Bitte, etwas abzulegen oder zu schreiben — dieser Dienst "
            "schreibt nichts",
            "die Freigabe eines Verzeichnisses als Ganzes — das ist eine "
            "Festlegung ueber einen Ordner, kein Lesen",
        ]

    @property
    def grenze(self) -> list[str]:
        """Was dieser Dienst ausdrücklich nicht tut."""
        return [
            "schreibt nichts, in keiner Zone",
            "liefert keine Zusammenfassung ganzer Verzeichnisse",
            "sucht nicht im Inhalt ohne vorherige Einschränkung",
            "kennt nur die freigegebenen Wurzeln des Paares",
        ]

    @property
    def quote(self) -> dict[str, int]:
        """Geschätzter Anteil der Äußerungen: eine Ausnahme.

        **0 % ist eine Schätzung, die widerlegt werden soll** (§8.1). Bis der
        Mensch Verzeichnisse einlegt, kommt der Fall selten vor; genau dafür
        steht die Angabe da, und der Quotenzähler am Empfang gibt ihr einen
        Leser, der ihr widersprechen kann.
        """
        return {"user": 0, "pixie": 0}

    @property
    def bedarf(self) -> list[Bedarf]:
        """Der Suchschlüssel des Turns — kein zweites Embedding.

        Ein eigenes Embedding zu rechnen hieße, denselben Text ein zweites Mal
        einzubetten und dabei die Verschiebung zu verlieren, mit der in diesem
        Turn auch KZG, LZG und die Bibliothek gesucht haben (§8.1).
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
        """Alle vier — und der vierte ist hier besonders brauchbar (§8.2).

        Eine Suche, die nichts findet, hat fast immer einen benachbarten
        Treffer. Ein blankes *„nichts gefunden"* ist die Sackgasse, gegen die
        die Konvention gebaut ist: Der Mensch weiß dann nicht, ob die Datei
        fehlt oder seine Frage.
        """
        return frozenset({"abgeschlossen", "fehler", "rueckfrage", "abgelehnt"})

    def build_graph(self) -> CompiledStateGraph:
        """Baut den Subgraphen: validieren → klassifizieren → suchen → zoomen.

        **Kein Tor und keine Rückfrage im Regelweg.** Dieser Dienst ändert
        nichts; eine Bestätigung hätte keinen Gegenstand. Was er nicht
        beantworten kann, geht durch den vierten Ausgang und trägt einen
        Vorschlag.
        """
        graph = StateGraph(AgentState)

        graph.add_node("validieren",     self._validieren)
        graph.add_node("klassifizieren", klassifizieren)
        graph.add_node("suchen",         self._suchen)
        graph.add_node("zoomen",         self._zoomen)

        graph.set_entry_point("validieren")
        graph.add_conditional_edges("validieren",     self._nach_validierung)
        graph.add_conditional_edges("klassifizieren", self._nach_klassifikation)
        graph.add_conditional_edges("suchen",         self._nach_suche)
        graph.add_edge("zoomen", END)

        return graph.compile()

    # --- Routing ---

    def _nach_validierung(self, state: AgentState) -> str:
        """Nach der Eingangsprüfung: Ende, oder Klassifikation, oder direkt suchen."""
        if state["status"] == "fehler":
            return END
        if state["parameter"].get("action", "") in AKTIONEN_KANON:
            return "suchen"
        return "klassifizieren"

    def _nach_klassifikation(self, state: AgentState) -> str:
        """Nach der Klassifikation: Ende bei Fehler oder Ablehnung, sonst suchen."""
        if state["status"] in ("fehler", "rejected"):
            return END
        return "suchen"

    def _nach_suche(self, state: AgentState) -> str:
        """Nach der Suche: Ende ohne Kandidaten, sonst zoomen."""
        if state["status"] in ("fehler", "abgelehnt", "abgeschlossen"):
            return END
        return "zoomen"

    # --- Eingabe-Validierung ---

    def _validieren(self, state: AgentState) -> dict:
        """Prüft den Eingangsauftrag gegen den Kanon.

        Vorbedingung: `state["parameter"]` trägt `action`.
        Nachbedingung: Bei `status="laufend"` liegt `action` in EINGANGS_KANON.
        Ein unbekannter Wert wird gemeldet und nicht auf eine Vorgabe
        abgebildet — sonst wäre eine defekte Zustellung von einer gültigen
        nicht zu unterscheiden (`11_EVA` §2).
        Fehlerfaelle: fehlende oder unbekannte Aktion.
        """
        # ── Eingabe-Validierung ─────────────────
        action: str = state["parameter"].get("action", "")
        logger.debug("dateien._validieren: Einstieg — action='%s'", action)

        if not action:
            logger.error("dateien: Auftrag ohne Aktion — abgewiesen")
            return {
                "status": "fehler",
                "fehler": "Keine Aktion angegeben",
                "schritte": state["schritte"] + [
                    {"node": "validieren", "ergebnis": "keine_aktion"}
                ],
            }

        if action not in EINGANGS_KANON:
            logger.error(
                "dateien: Aktion %r nicht im Kanon %s — abgewiesen",
                action, sorted(EINGANGS_KANON),
            )
            return {
                "status": "fehler",
                "fehler": f"Unbekannte Aktion: {action}",
                "schritte": state["schritte"] + [
                    {"node": "validieren", "ergebnis": "ungueltige_aktion"}
                ],
            }

        # ── Ausgabe-Verifikation ────────────────
        return {
            "status": "laufend",
            "schritte": state["schritte"] + [
                {"node": "validieren", "ergebnis": "ok", "action": action}
            ],
        }

    # --- Die Suche ---

    def _suchen(self, state: AgentState) -> dict:
        """Findet die Kandidaten über die drei Kanäle — scharf vor unscharf.

        Vorbedingung: `parameter` trägt `action` aus AKTIONEN_KANON; `kontext`
        trägt das Paar und — sofern angemeldet und vorhanden — `such_vektor`.
        Nachbedingung: Entweder `parameter["kandidaten"]` mit mindestens einem
        Treffer, oder `status="abgelehnt"` mit einer Korrektur, die den
        Bestand als Beleg trägt (§8.2).
        Fehlerfaelle: unvollständiges Paar meldet `fehler` — ein Treffer ohne
        Paar käme aus einer fremden Freigabe.

        **Der Suchschlüssel darf fehlen, und das ist kein Fehler.** Fehlt er,
        arbeiten nur die scharfen Kanäle; fehlen auch die, ist nichts zu
        suchen, und genau das wird gesagt.
        """
        # ── Eingabe-Validierung ─────────────────
        user_id: str = state["kontext"].get("user_id", "")
        character_id: str = state["kontext"].get("character_id", "")
        if not user_id or not character_id:
            logger.error(
                "dateien._suchen: unvollständiges Paar (user_id=%r, "
                "character_id=%r) — keine Suche", user_id, character_id,
            )
            return {
                "status": "fehler",
                "fehler": "Auftrag ohne vollständiges Paar",
                "schritte": state["schritte"] + [
                    {"node": "suchen", "ergebnis": "paar_unvollstaendig"}
                ],
            }

        name: str = state["parameter"].get("name", "") or ""
        begriffe: list[str] = state["parameter"].get("begriffe") or []
        nadel: str = state["parameter"].get("nadel", "") or ""
        such_vektor: list[float] = state["kontext"].get("such_vektor") or []

        # Die Nadel ist zugleich ein Stichwort: Wonach im Text gesucht wird,
        # steht oft auch in den erhobenen Stichwörtern der Datei. Sie tritt
        # deshalb hinten an die Begriffe — vorn stünde sie über den Begriffen,
        # die die Frage selbst genannt hat.
        woerter: list[str] = begriffe + ([nadel] if nadel and nadel not in begriffe else [])

        if not name and not woerter and not such_vektor:
            logger.error(
                "dateien._suchen: weder Name noch Begriffe noch Suchschlüssel — "
                "es gibt nichts zu suchen"
            )
            return {
                "status": "fehler",
                "fehler": "Kein Suchschlüssel — weder Name, Begriff noch Vektor.",
                "schritte": state["schritte"] + [
                    {"node": "suchen", "ergebnis": "kein_schluessel"}
                ],
            }

        # ── Verarbeitung ────────────────────────
        kandidaten: list[dict] = kandidaten_finden(
            user_id, character_id, name, woerter, such_vektor,
        )
        logger.info(
            "dateien._suchen: name='%s', woerter=%s, vektor=%s → %d Kandidaten",
            name[:40], woerter, "ja" if such_vektor else "nein", len(kandidaten),
        )

        # ── Ausgabe-Verifikation ────────────────
        if not kandidaten:
            gesucht: str = name or ", ".join(woerter) or "der Sinn der Frage"
            bestand: int = bestand_zaehlen(user_id, character_id)
            beleg: str = (
                f"{bestand} Dateien im Index dieses Paares, kein Treffer für {gesucht!r}."
                if bestand >= 0 else
                f"Kein Treffer für {gesucht!r}; der Bestand ließ sich nicht zählen."
            )
            korrektur = Korrektur(
                befund="Dazu liegt in den freigegebenen Unterlagen nichts.",
                beleg=beleg,
                vorschlag=(
                    "Nenn mir den Dateinamen, wenn du ihn kennst, oder ein "
                    "Fachwort, das im Text vorkommen muss — danach wird exakt "
                    "gesucht statt der Bedeutung nach."
                    if bestand > 0 else
                    "Gib mir zuerst ein Verzeichnis frei, dann kann ich darin "
                    "nachsehen."
                ),
            )
            return {
                "parameter": {**state["parameter"], "korrektur": korrektur},
                "status": "abgelehnt",
                "schritte": state["schritte"] + [
                    {"node": "suchen", "ergebnis": f"kein_treffer/bestand={bestand}"}
                ],
            }

        return {
            "parameter": {**state["parameter"], "kandidaten": kandidaten},
            "schritte": state["schritte"] + [
                {"node": "suchen",
                 "ergebnis": f"{len(kandidaten)}/{kandidaten[0].get('kanal', '?')}"}
            ],
        }

    # --- Der Zoom ---

    def _zoomen(self, state: AgentState) -> dict:
        """Wählt die Stufe und baut die Auskunft — Karte, Block oder Nadel.

        Vorbedingung: `parameter["kandidaten"]` ist nicht leer.
        Nachbedingung: `ergebnis` trägt einen nichtleeren Text mit Fundstelle,
        und `status` ist "abgeschlossen" — oder `status="abgelehnt"` mit einer
        Korrektur, deren Vorschlag die Blockkarte als Angebot trägt.
        Fehlerfaelle: eine Auskunft, die leer bliebe, wird als Störung
        gemeldet und nicht als leere Antwort zugestellt.

        **Die Stufe folgt der Frage und wird nicht geraten** (§6.4): Wer einen
        Abschnitt nennt, bekommt den Block; wer einen Wortlaut nennt, bekommt
        die Nadel samt Zeilennummer; wer nur wissen will, wo etwas steht,
        bekommt die Karte — und die kostet keinen Dateizugriff.
        """
        # ── Eingabe-Validierung ─────────────────
        kandidaten: list[dict] = state["parameter"].get("kandidaten") or []
        if not kandidaten:
            logger.error(
                "dateien._zoomen: ohne Kandidaten erreicht — das Routing hätte "
                "hier nicht herführen dürfen"
            )
            return {
                "status": "fehler",
                "fehler": "Zoom ohne Kandidaten",
                "schritte": state["schritte"] + [
                    {"node": "zoomen", "ergebnis": "ohne_kandidaten"}
                ],
            }

        action: str = state["parameter"].get("action", "")
        abschnitt: str = state["parameter"].get("abschnitt", "") or ""
        nadel: str = state["parameter"].get("nadel", "") or ""
        begriffe: list[str] = state["parameter"].get("begriffe") or []
        erster: dict = kandidaten[0]

        # ── Verarbeitung ────────────────────────
        # Die Karte kostet nichts — sie steht im Index (§6.4). Sie wird
        # deshalb immer geholt: als eigene Auskunft, und sonst als Vorschlag
        # für den Fall, dass die gewählte Stufe nichts findet.
        karte: list[dict] = karte_lesen(erster)

        if action == AKTION_FINDEN:
            text: str = auskunft_finden(kandidaten, karte)
            return self._abschluss(state, STUFE_KARTE, text, kandidaten)

        if abschnitt:
            block: dict | None = block_holen(erster, abschnitt)
            if block:
                text = auskunft_bauen(STUFE_BLOCK, kandidaten, block, karte, abschnitt)
                return self._abschluss(state, STUFE_BLOCK, text, kandidaten)
            logger.info(
                "dateien._zoomen: Abschnitt '%s' in %s nicht lesbar — die "
                "Karte tritt an seine Stelle", abschnitt, fundstelle(erster),
            )

        # **Jeder Begriff bekommt einen Versuch, nicht nur der erste.** Die
        # Klassifikation liefert eine Liste, und die Nadel sucht zeichengenau:
        # Ein deutsches Kompositum aus der Frage ("Salienzschwelle") steht so
        # fast nie im Text, ein Wort daneben schon. Gemessen am 18.08.2026 —
        # der erste Begriff traf nicht, und der Turn endete im vierten
        # Ausgang, obwohl die Zahl eine Zeile weiter stand.
        #
        # Der Preis ist bekannt und gedeckelt: höchstens ein Dateizugriff je
        # Begriff auf **eine** Datei, und die Zahl der Begriffe ist gekappt.
        versuche: list[str] = [b for b in ([nadel] + begriffe) if b]
        gepruefte: list[str] = []
        for gesucht in versuche:
            if gesucht in gepruefte:
                continue
            gepruefte.append(gesucht)
            treffer: dict | None = nadel_suchen(erster, gesucht)
            if treffer is not None and int(treffer.get("anzahl") or 0) > 0:
                text = auskunft_bauen(STUFE_NADEL, kandidaten, treffer, karte, gesucht)
                return self._abschluss(state, STUFE_NADEL, text, kandidaten)

        if gepruefte:
            # Der Fall aus §8.2, zweite Zeile: Die Datei ist gefunden, der
            # Satz steht nicht darin. Das ist ein Urteil und keine Störung —
            # und der benachbarte Treffer liegt bereit, es ist die Karte.
            return self._ohne_fundstelle(state, kandidaten, karte, ", ".join(gepruefte))

        text = auskunft_bauen(STUFE_KARTE, kandidaten, None, karte, "")
        return self._abschluss(state, STUFE_KARTE, text, kandidaten)

    def _abschluss(
        self, state: AgentState, stufe: str, text: str, kandidaten: list[dict],
    ) -> dict:
        """Schließt den Durchlauf mit einer Auskunft ab.

        Vorbedingung: `text` ist die gebaute Auskunft.
        Nachbedingung: `status="abgeschlossen"` mit nichtleerem `ergebnis` —
        oder `status="fehler"`, wenn der Text leer blieb.
        Fehlerfaelle: **Eine leere Auskunft wird als Störung gemeldet.** Sie
        zuzustellen hieße, dem Verfasser einen Aufgabenblock ohne Inhalt zu
        geben; er füllte ihn mit plausibler Prosa, und genau das ist der
        Defekt, gegen den dieser Dienst gebaut ist (§8.1a).
        """
        # ── Ausgabe-Verifikation ────────────────
        if not text.strip():
            logger.error(
                "dateien: Stufe '%s' lief über %d Kandidaten und lieferte einen "
                "leeren Text — als Störung gemeldet statt leer zugestellt",
                stufe, len(kandidaten),
            )
            return {
                "status": "fehler",
                "fehler": f"Auskunft der Stufe '{stufe}' blieb leer",
                "schritte": state["schritte"] + [
                    {"node": "zoomen", "ergebnis": f"leer/{stufe}"}
                ],
            }

        logger.info(
            "dateien: Stufe '%s' über %s → %d Zeichen Auskunft",
            stufe, fundstelle(kandidaten[0]), len(text),
        )
        return {
            "ergebnis": text,
            "status": "abgeschlossen",
            "schritte": state["schritte"] + [
                {"node": "zoomen", "ergebnis": f"{stufe}/{len(text)}"}
            ],
        }

    def _ohne_fundstelle(
        self, state: AgentState, kandidaten: list[dict], karte: list[dict],
        gesucht: str,
    ) -> dict:
        """Der vierte Ausgang, wenn die Datei steht und der Satz fehlt (§8.2).

        Vorbedingung: `kandidaten` ist nicht leer; `gesucht` war der Wortlaut.
        Nachbedingung: `status="abgelehnt"` mit vollständiger Korrektur —
        Befund, Beleg mit Zahlen, und als Vorschlag der benachbarte Treffer.
        """
        # ── Verarbeitung ────────────────────────
        ueberschriften: list[str] = [
            str(block.get("header", "")).strip()
            for block in karte[:5]
            if str(block.get("header", "")).strip()
        ]
        vorschlag: str = (
            f"In {fundstelle(kandidaten[0])} gibt es die Abschnitte "
            f"{' · '.join(ueberschriften)} — soll ich einen davon lesen?"
            if ueberschriften else
            "Nenn mir ein anderes Wort, das im Text stehen müsste — "
            "gesucht wird zeichengenau."
        )

        logger.info(
            "dateien: %r steht in %s nicht — vierter Ausgang mit %d Abschnitten "
            "als Vorschlag", gesucht, fundstelle(kandidaten[0]), len(ueberschriften),
        )

        # ── Ausgabe-Verifikation ────────────────
        return {
            "parameter": {
                **state["parameter"],
                "korrektur": Korrektur(
                    befund=f"{gesucht!r} steht in dieser Datei nicht.",
                    beleg=(
                        f"{len(kandidaten)} Kandidat(en), 0 Treffer für {gesucht!r} "
                        f"in {fundstelle(kandidaten[0])}."
                    ),
                    vorschlag=vorschlag,
                ),
            },
            "status": "abgelehnt",
            "schritte": state["schritte"] + [
                {"node": "zoomen", "ergebnis": f"nadel_leer/{gesucht[:30]}"}
            ],
        }
