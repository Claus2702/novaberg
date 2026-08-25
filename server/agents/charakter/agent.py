"""CharakterAgent — Destilliert 5 Charakter-Profile aus LZG+KZG.

Ein LLM-Call pro Profil pro User. Nur aktiv wenn hash_dirty gesetzt.
Migriert aus: services/shadow_agent/tasks/charakter_hash.py
"""

import json
import logging
import time
import uuid

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    AKTIVES_PAAR_USER_ID,
    ASSISTANT_USER_ID,
    redis_client,
    EMBED_MODEL,
    POSTGRES_URL,
    ZIEL_MAX_LANGFRISTIG,
    PIXIE_CHARAKTER_PRIORITAET,
    PIXIE_CHARAKTER_INTERVALL_SEKUNDEN,
    PIXIE_CHARAKTER_LZG_LIMIT,
    PIXIE_CHARAKTER_KZG_LIMIT,
    PIXIE_CHARAKTER_KZG_LADEGRENZE_TAGE,
    PIXIE_ANALYSE_MODEL,
    get_node_config,
)
from tools.db_manager import db_manager
from agents.charakter.destillation import (
    zeitgewicht,
    kern_hash_destillieren,
    adaptive_hash_destillieren,
    intentions_profil_destillieren,
    emotions_profil_destillieren,
    beziehungsprofil_destillieren,
    langfristige_ziele_destillieren,
    charakter_rad_destillieren,
    initiative_rad_destillieren,
    initiative_versatz_berechnen,
    nutzer_gewichtung_berechnen,
    flache_reihe_als_raeder,
    speichenweise_mediane,
    speichen_ohne_mehrheit,
    RAD_NABE,
    INITIATIVE_RAD_NABE,
    RAD_LEER,
    INITIATIVE_RAD_LEER,
)
from agents.charakter.rad_messreihe import (
    Messung,
    RAD_ART_INITIATIVE,
    RAD_ART_ZUWENDUNG,
    messung_ablegen,
    messung_faellig,
    rad_zusammenfassen,
    reihe_laden,
)
from memory.ziele import ziel_speichern, ziele_aktive_laden, ziel_deaktivieren
from memory.ziele import embed_text_bauen as ziel_embed_text_bauen
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.agents.charakter")


def _hget(rc, key: str, field: str, default: str = "") -> str:
    """Redis HGET mit Bytes-Decoding."""
    val = rc.hget(key, field)
    if val is None:
        return default
    return val.decode("utf-8") if isinstance(val, bytes) else val


def _begegnungs_schluessel(user_id: str, character_id: str) -> set[str]:
    """Die KZG-Schluessel, die auf einen echten Turn zurueckgehen.

    Vorbedingung: kanonisches Paar.
    Nachbedingung: Menge der Schluessel, deren Ursprungs-Turn **nicht**
        als `eigener_impuls` markiert ist. Ein Schluessel ohne Bruecke
        fehlt — fuer ihn ist kein Wortlaut erreichbar, und genau darauf
        kommt es dem einzigen Aufrufer an.

    Eine Abfrage statt einer je Kandidat: Die Menge wird einmal geholt und
    als Nachschlagewerk benutzt.
    """
    zeilen = db_manager.select(
        """
        SELECT v.kzg_id
        FROM verbindung v
        JOIN pipeline_log p
          ON p.turn_id = v.turn_id AND p.art = 'turn_roh'
        WHERE v.kzg_id LIKE %s
          AND p.inhalt ->> 'herkunft' IS DISTINCT FROM 'eigener_impuls'
        """,
        (f"kzg:{user_id}:{character_id}:%",),
    ) or []
    return {z["kzg_id"] for z in zeilen}


class CharakterAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "charakter"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["charakter_hash"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    @property
    def identity_user(self) -> str:
        return ASSISTANT_USER_ID

    def periodic_task(self) -> PeriodicTask | None:
        return PeriodicTask(
            name="charakter_hash",
            priority=PIXIE_CHARAKTER_PRIORITAET,
            interval=PIXIE_CHARAKTER_INTERVALL_SEKUNDEN,
            description="5 Profile destillieren (bei hash_dirty)",
        )

    def build_graph(self):
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Destilliert 5 Charakter-Profile aus dem kanonischen Paar.

        Seit Chat 60: Ein kanonisches Paar pro (User, Charakter)-Beziehung.
        Perspektiv-Unterscheidung User-Profil vs. Nova-Profil ueber das
        beobachter-Feld im KZG, nicht ueber Paar-Richtung.
        """
        # Das Paar dieses Laufs kommt aus der Konfiguration, nicht aus dem
        # Fallback fuer eine fehlende Anfrage (Chat 125). Beide Werte sind im
        # Regelbetrieb derselbe Mensch; fuer eine Messreihe wird
        # AKTIVES_PAAR_USER_ID umgestellt, und dann destilliert der Agent
        # Profile und Raeder genau fuer die Testperson.
        #
        # Die Liste bleibt eine Liste: Der Backlog-Eintrag PAARLISTE-FEST
        # verlangt die Iteration ueber den Bestand, und die kommt hier hinein.
        # Bis dahin ist die Menge bewusst einelementig — mehrere Paare je Lauf
        # brauchen erst eine benannte Obergrenze.
        paare: list[tuple[str, str]] = [
            (AKTIVES_PAAR_USER_ID, ASSISTANT_USER_ID),
        ]
        gesamt_destilliert: int = 0

        for kanon_user_id, kanon_character_id in paare:
            # ── Dirty-Check ──────────────────────
            dirty = redis_client.get(f"hash_dirty:{kanon_user_id}:{kanon_character_id}")
            if not dirty:
                logger.debug(
                    f"CharakterAgent: Kein hash_dirty fuer "
                    f"{kanon_user_id}:{kanon_character_id}"
                )
                continue

            logger.info(
                f"CharakterAgent: Lade KZG fuer Paar "
                f"({kanon_user_id}, {kanon_character_id}) — "
                f"kanonisches Schema, Perspektive ueber beobachter"
            )

            # Profil-Konfigurationen: User-Profil (beobachter=user) und
            # Nova-Profil (beobachter=assistant) aus demselben kanonischen Paar.
            # Storage-Key (charakter_hash) bleibt (subjekt_user_id, subjekt_character_id),
            # damit bestehende Enricher-Lesepfade unveraendert funktionieren.
            profil_konfig: list[tuple[str, str, str]] = [
                ("user",      kanon_user_id,      kanon_character_id),  # User-Profil
                ("assistant", kanon_character_id, kanon_user_id),       # Nova-Profil
            ]

            paar_etwas_gespeichert: bool = False

            for beobachter, subjekt_user_id, subjekt_character_id in profil_konfig:
                logger.info(
                    f"CharakterAgent: Profil-Build — "
                    f"subjekt={subjekt_user_id}, beobachter={beobachter}"
                )

                # ── LZG-Eintraege laden (kanonisches Paar + beobachter-Filter) ──
                # CHAR-LZG-LEAK: LZG-Lookup ueber das kanonische Paar (analog
                # zum KZG-Lookup), nicht ueber subjekt_user_id. Damit fliessen
                # nur Eintraege der gewuenschten Perspektive ins Profil.
                # Der Kern liest den **Wortlaut**, nicht die Langzeit-Knoten.
                # `KERN_HASH_PROMPT` verlangt es woertlich: »Erschliesse aus
                # dem WIE — wie {traeger} spricht« und schaerft nach: »Nicht
                # WORUEBER {traeger} spricht charakterisiert {traeger},
                # sondern WIE.« Die Knoten tragen das Worueber; aus »jo« ist
                # dort »Der Nutzer weiss nicht, was er hier tun soll«
                # geworden. Wie jemand spricht, ist daran nicht mehr
                # ablesbar. Vorgabe des Meisters vom 10.08.2026.
                turn_wortlaut = self._turns_laden(kanon_user_id)
                lzg_intentionen = self._lzg_intentionen_laden(
                    kanon_user_id, kanon_character_id, beobachter,
                )
                lzg_emotionen = self._lzg_emotionen_laden(
                    kanon_user_id, kanon_character_id, beobachter,
                )

                # ── KZG-Eintraege laden (kanonisches Paar + beobachter-Filter) ──
                # Zwei Auswahlen, weil zwei Fragen: Der Adaptiv-Hash fragt,
                # was den Traeger gerade beschaeftigt — dazu gehoeren seine
                # eigenen Gedanken. Das Beziehungsprofil fragt nach der Naehe
                # zum Gegenueber und liest dafuer den Wortlaut; ein Impuls hat
                # dort kein Gegenueber und erschiene als dessen Rede.
                # Entscheidung vom 17.08.2026.
                kzg_eintraege = self._kzg_laden(
                    kanon_user_id, kanon_character_id,
                    beobachter_filter=beobachter,
                )
                kzg_begegnungen = self._kzg_laden(
                    kanon_user_id, kanon_character_id,
                    beobachter_filter=beobachter,
                    nur_begegnungen=True,
                )

                # ── 5 Profile destillieren ───────────
                ergebnis: dict = {
                    "kern": "", "adaptiv": "",
                    "intentions_profil": "", "emotions_profil": "",
                    "beziehungsprofil": "",
                    # Leer bzw. None heisst "nicht erhoben" — der Schreibpfad
                    # laesst den bestehenden Wert dann stehen, statt ihn durch
                    # einen erfundenen zu ersetzen.
                    "nutzer_gewichtung_rad": "",
                    "nutzer_gewichtung":     None,
                    "initiative_versatz_rad": "",
                    "initiative_versatz":     None,
                }

                try:
                    ergebnis["kern"] = kern_hash_destillieren(turn_wortlaut, user_id=subjekt_user_id)
                except Exception as ex:
                    logger.exception(f"{type(ex).__name__}: CharakterAgent: Kern-Hash fehlgeschlagen fuer {subjekt_user_id}")

                try:
                    ergebnis["adaptiv"] = adaptive_hash_destillieren(kzg_eintraege, user_id=subjekt_user_id)
                except Exception as ex:
                    logger.exception(f"{type(ex).__name__}: CharakterAgent: Adaptive-Hash fehlgeschlagen fuer {subjekt_user_id}")

                try:
                    ergebnis["intentions_profil"] = intentions_profil_destillieren(lzg_intentionen, user_id=subjekt_user_id)
                except Exception as ex:
                    logger.exception(f"{type(ex).__name__}: CharakterAgent: Intentions-Profil fehlgeschlagen fuer {subjekt_user_id}")

                try:
                    ergebnis["emotions_profil"] = emotions_profil_destillieren(lzg_emotionen, user_id=subjekt_user_id)
                except Exception as ex:
                    logger.exception(f"{type(ex).__name__}: CharakterAgent: Emotions-Profil fehlgeschlagen fuer {subjekt_user_id}")

                try:
                    ergebnis["beziehungsprofil"] = beziehungsprofil_destillieren(kzg_begegnungen, user_id=subjekt_user_id)
                except Exception as ex:
                    logger.exception(f"{type(ex).__name__}: CharakterAgent: Beziehungsprofil fehlgeschlagen fuer {subjekt_user_id}")

                # ── Charakter-Rad aus den frischen Profilen ──
                # Laeuft NACH den fuenf Profilen und liest deren Ergebnis, nicht
                # erneut das KZG: Das Rad ist eine Eigenschaft des destillierten
                # Charakters, keine zweite Beobachtung der Rohdaten.
                #
                # Das Rad misst die Haltung des Subjekts GEGENUEBER seinem
                # Gegenueber. Auf der Zeile (nova, meister) ist das Novas
                # Zuwendung zum Nutzer — der Wert, den die Salienz-Formel
                # liest. Auf (meister, nova) entsteht spiegelbildlich seine
                # Zuwendung zu ihr; die hat bewusst keinen Verbraucher
                # (novaberg-salienz-berechnung_k.md §8).
                rad_quelle: str = "\n\n".join(
                    t for t in (ergebnis["kern"], ergebnis["beziehungsprofil"]) if t
                )
                if rad_quelle:
                    # Fester Takt statt bei jedem Lauf: Das Rad misst einen
                    # akuten Zustand, aber eine einzelne Erhebung bewegte ihn
                    # bisher voll. Gemessen 31.07.2026 — Faktor 1.215 -> 0.980
                    # in zwei Stunden, bei einer Verfahrensstreuung von 0.08
                    # (novaberg-charakter-rad-messreihe_k.md §1).
                    if not messung_faellig(
                        subjekt_user_id, subjekt_character_id, RAD_ART_ZUWENDUNG,
                    ):
                        logger.info(
                            f"CharakterAgent: Zuwendungs-Rad fuer {subjekt_user_id} "
                            "nicht faellig — bestehender Wert bleibt"
                        )
                    else:
                        # Jeder Lauf geht als eigene Zeile in die Reihe —
                        # dieselbe Bauart wie beim Initiative-Rad, mit
                        # gemeinsamer `erhebung_id`. Die Senke wirft nicht.
                        node_cfg_rad: dict = get_node_config("charakter_hash")
                        erhebung_zuw: str  = str(uuid.uuid4())

                        def lauf_ablegen_zuw(nummer: int, rad: dict,
                                             faktor: float,
                                             _u=subjekt_user_id,
                                             _c=subjekt_character_id,
                                             _q=rad_quelle,
                                             _e=erhebung_zuw,
                                             _n=node_cfg_rad) -> None:
                            """Senke fuer `charakter_rad_destillieren`."""
                            messung_ablegen(Messung(
                                user_id      = _u,
                                character_id = _c,
                                rad_art      = RAD_ART_ZUWENDUNG,
                                speichen     = {**rad.get("hoch", {}),
                                                **rad.get("runter", {})},
                                faktor       = faktor,
                                modell       = PIXIE_ANALYSE_MODEL,
                                temperatur   = float(_n.get("temperature", 0.2)),
                                presence_penalty = float(
                                    _n.get("presence_penalty", 0.0)),
                                quelle       = _q,
                                erhebung_id  = _e,
                                lauf         = nummer,
                            ))

                        erhoben = charakter_rad_destillieren(
                            rad_quelle, user_id=subjekt_user_id,
                            lauf_melden=lauf_ablegen_zuw,
                        )
                        if erhoben is not None:
                            ergebnis["nutzer_gewichtung_rad"], ergebnis["nutzer_gewichtung"] = (
                                self._rad_ueber_reihe_stabilisieren(
                                    subjekt_user_id, subjekt_character_id,
                                    erhoben, rad_quelle,
                                )
                            )

                    # Zweites Rad, dieselbe Quelle, andere Frage: ueberlaesst
                    # sie im Gespraech die Fuehrung oder behaelt sie sie.
                    # Ein eigener Call, weil das erste Rad seine Speichen mit
                    # Wissbegier und Pflicht buendelt, die hier nichts zu
                    # suchen haben (novaberg-gv-initiative_k.md §6).
                    #
                    # Derselbe Takt und dieselbe Reihe wie beim Zuwendungs-Rad.
                    # Seine drei Laeufe bleiben: Sie nehmen die Streuung INNER-
                    # HALB einer Erhebung heraus, die Reihe die zwischen ihnen.
                    if not messung_faellig(
                        subjekt_user_id, subjekt_character_id, RAD_ART_INITIATIVE,
                    ):
                        logger.info(
                            f"CharakterAgent: Initiative-Rad fuer {subjekt_user_id} "
                            "nicht faellig — bestehender Wert bleibt"
                        )
                    else:
                        erhoben_init = self._initiative_ueber_reihe_stabilisieren(
                            subjekt_user_id, subjekt_character_id, rad_quelle,
                        )
                        if erhoben_init is not None:
                            (ergebnis["initiative_versatz_rad"],
                             ergebnis["initiative_versatz"]) = erhoben_init
                else:
                    logger.warning(
                        f"CharakterAgent: kein Kern- und kein Beziehungsprofil fuer "
                        f"{subjekt_user_id} — Charakter-Rad nicht erhoben, "
                        f"bestehender Faktor bleibt"
                    )

                # ── In PostgreSQL speichern ──────────
                hat_aenderungen: bool = any(v for v in ergebnis.values())

                if hat_aenderungen:
                    try:
                        self._ergebnis_speichern(subjekt_user_id, subjekt_character_id, ergebnis)
                        paar_etwas_gespeichert = True
                        gesamt_destilliert += 1
                        logger.info(
                            f"CharakterAgent: {subjekt_user_id} destilliert "
                            f"(5 Profile, beobachter={beobachter})"
                        )
                    except Exception as ex:
                        logger.exception(f"{type(ex).__name__}: CharakterAgent: Speicherung fehlgeschlagen fuer {subjekt_user_id}")

                    # ── Langfristige Ziele aus Kern-Hash destillieren ──
                    # Nur fuer Novas eigenen Hash (ASSISTANT_USER_ID als subjekt_user_id),
                    # nicht fuer den User-Hash.
                    if subjekt_user_id == ASSISTANT_USER_ID and ergebnis["kern"]:
                        try:
                            neue_ziele: list[dict] = langfristige_ziele_destillieren(
                                ergebnis["kern"], user_id=ASSISTANT_USER_ID,
                            )

                            if neue_ziele:
                                # Alte langfristige Ziele DIESES Paares
                                # deaktivieren. Das Gegenueber ist Pflicht:
                                # Ohne es raeumte die Destillation eines Paares
                                # die Ziele jedes anderen ab (Chat 125).
                                alte_ziele: list[dict] = ziele_aktive_laden(
                                    POSTGRES_URL, ASSISTANT_USER_ID, kanon_user_id,
                                )
                                for altes in alte_ziele:
                                    if altes["ziel_typ"] == "langfristig":
                                        ziel_deaktivieren(POSTGRES_URL, altes["id"])

                                # Neue Ziele speichern (mit Embedding)
                                for z in neue_ziele[:ZIEL_MAX_LANGFRISTIG]:
                                    try:
                                        request = EmbedRequest(text=ziel_embed_text_bauen(z["zielsatz"]))
                                        embed_response = model_service.embed.submit_sync(request)
                                        emb: list[float] | None = embed_response.embedding
                                        logger.debug(
                                            "CharakterAgent: Langfrist-Ziel Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                                            len(emb),
                                            embed_response.duration_seconds,
                                        )
                                    except Exception:
                                        emb = None

                                    ziel_speichern(
                                        postgres_url=POSTGRES_URL,
                                        user_id=ASSISTANT_USER_ID,
                                        character_id=kanon_user_id,
                                        ziel_typ="langfristig",
                                        zielsatz=z["zielsatz"],
                                        motivation=0.8,
                                        emotion=z.get("emotion", "neugierig"),
                                        arousal=z.get("arousal", 0.6),
                                        thema=z.get("thema", ""),
                                        embedding=emb,
                                    )

                                logger.info(
                                    f"CharakterAgent: {len(neue_ziele)} langfristige Ziele "
                                    f"für {ASSISTANT_USER_ID} erneuert"
                                )

                        except Exception as ziel_fehler:
                            logger.warning(
                                f"CharakterAgent: Ziel-Destillation fehlgeschlagen — {ziel_fehler}"
                            )
                else:
                    logger.info(
                        f"CharakterAgent: Keine Aenderungen fuer {subjekt_user_id} "
                        f"(beobachter={beobachter})"
                    )

            # Dirty-Flag erst nach beiden Profil-Builds loeschen.
            if paar_etwas_gespeichert:
                redis_client.delete(f"hash_dirty:{kanon_user_id}:{kanon_character_id}")

        state["ergebnis"] = {"destilliert": gesamt_destilliert}
        state["status"] = "abgeschlossen"
        return state

    # ─────────────────────────────────────────
    # Daten laden
    # ─────────────────────────────────────────

    def _turns_laden(self, user_id: str, grenze: int = 40) -> list[dict]:
        """Laedt den Wortlaut der Begegnungen eines Paares aus `pipeline_log`.

        Vorbedingung: `user_id` ist die Kennung des Menschen im Paar — unter
            ihr laufen die Rohturns, unabhaengig davon, wessen Charakter
            destilliert wird. Die Perspektive macht der Prompt.
        Nachbedingung: Liste von {'aeusserung', 'antwort'}, aelteste zuerst,
            **ausschliesslich aus Turns mit `herkunft='nutzer_turn'`**.
            Leer heisst: keine Begegnung vorhanden, und der Aufrufer meldet es.

        **Ein eigener Impuls ist keine Begegnung und gehoert in kein Profil.**
        Beide Raeder messen eine Haltung GEGENUEBER jemandem; bei einem Impuls
        gibt es kein Gegenueber, also nichts zu bewerten — weder fuer den
        Menschen noch fuer die Figur. Vorgabe vom 16.08.2026.

        Der Grund, warum das nicht bloss eine Feinheit ist: Ein Impuls legt
        seinen Text in dasselbe Feld `user_prompt` wie eine Nutzeraeusserung.
        Ungefiltert las diese Funktion die eigenen Gedanken der Figur als
        Aeusserungen des Menschen und destillierte daraus **sein** Wesen.
        `[gemessen]` — 16.08.2026 am produktiven Paar: Von den 40 gelesenen
        Turns waren **25 eigene Impulse mit 95,4 % des Materials**; die
        tatsaechlichen Aeusserungen des Menschen trugen 1761 Zeichen (4,6 %).
        Die Marke `herkunft` liegt seit dem 05.08.2026 in derselben Zeile.
        """
        zeilen = db_manager.select(
            """
            SELECT inhalt ->> 'user_prompt' AS aeusserung,
                   inhalt ->> 'response'    AS antwort
            FROM pipeline_log
            WHERE art = 'turn_roh' AND user_id = %s
              AND inhalt ->> 'herkunft' = 'nutzer_turn'
            ORDER BY erstellt_am DESC
            LIMIT %s
            """,
            (user_id, grenze),
        ) or []

        # Wieviel der Bestand haette liefern koennen — ohne diese Zahl ist
        # "wenig Material" nicht von "viel Material, davon das meiste
        # ausgenommen" zu unterscheiden.
        gesamt = db_manager.select(
            """
            SELECT count(*) FILTER (
                       WHERE inhalt ->> 'herkunft' = 'eigener_impuls') AS impulse,
                   count(*) FILTER (
                       WHERE coalesce(inhalt ->> 'herkunft', '') = '')  AS ohne_marke
            FROM pipeline_log
            WHERE art = 'turn_roh' AND user_id = %s
            """,
            (user_id,),
        ) or [{"impulse": 0, "ohne_marke": 0}]

        eintraege = [
            {"aeusserung": z["aeusserung"] or "", "antwort": z["antwort"] or ""}
            for z in reversed(zeilen)
            if (z["aeusserung"] or z["antwort"])
        ]

        if not eintraege:
            logger.error(
                f"CharakterAgent: kein Begegnungs-Wortlaut fuer '{user_id}' — "
                f"{gesamt[0]['impulse']} Impulse und "
                f"{gesamt[0]['ohne_marke']} unmarkierte Turns bleiben ausgenommen"
            )
        else:
            logger.info(
                f"CharakterAgent: Wortlaut geladen fuer '{user_id}' — "
                f"{len(eintraege)} Begegnungen "
                f"({gesamt[0]['impulse']} Impulse ausgenommen, "
                f"{gesamt[0]['ohne_marke']} ohne Marke)"
            )
        return eintraege

    def _lzg_kern_laden(
        self,
        user_id:      str,
        character_id: str,
        beobachter:   str,
    ) -> list[dict]:
        """Laedt Knoten fuer Kern-Hash (gewichtet nach Anker-Staerke gewicht_absolut + Haeufigkeit).

        Filtert auf das kanonische Paar (user_id, character_id) und die
        gewuenschte Perspektive (beobachter). Spiegelung des KZG-Lesepfads
        (CHAR-HASH-FILTER, Chat 73) auf LZG-Seite.
        """
        logger.debug(
            f"CharakterAgent: LZG-Kern laden fuer user={user_id}, "
            f"character={character_id}, beobachter={beobachter}"
        )
        return db_manager.select(
            """
            SELECT dimension, inhalt, gewicht_absolut, haeufigkeit
            FROM lzg_knoten
            WHERE user_id = %s AND character_id = %s AND beobachter = %s
              AND aktiv = TRUE
            ORDER BY gewicht_absolut DESC, haeufigkeit DESC
            LIMIT %s
            """,
            (user_id, character_id, beobachter, PIXIE_CHARAKTER_LZG_LIMIT),
        )

    def _lzg_intentionen_laden(
        self,
        user_id:      str,
        character_id: str,
        beobachter:   str,
    ) -> list[dict]:
        """Laedt LZG-Eintraege mit Kommunikations-Signalen (paar- + perspektivgefiltert).

        Vorbedingung: kanonisches Paar und eine Perspektive ('user' oder
            'assistant').
        Nachbedingung: hoechstens `PIXIE_CHARAKTER_LZG_LIMIT` Knoten, absteigend
            nach Anker-Staerke, **ohne solche aus eigenen Impulsen**.

        **Warum hier gefiltert wird und beim Emotions- und Adaptiv-Profil
        nicht:** Dieses Profil fragt, wie der Traeger **mit anderen umgeht** —
        eine Aussage ueber Umgang setzt ein Gegenueber voraus, und ein Impuls
        hat keines. Was jemanden gerade beschaeftigt (adaptiv) und was er
        fuehlt (emotionen) steht dagegen sehr wohl in seinen eigenen Gedanken;
        dort waere der Filter ein Verlust. Entscheidung vom 17.08.2026.

        Der Filter laeuft ueber die Bruecke `verbindung` -> `pipeline_log`.
        `IS DISTINCT FROM` statt `<>`, und ein Knoten **ohne** Bruecke bleibt
        erhalten: Er ist nicht nachweislich ein Impuls, und am 17.08.2026 waren
        das 371 von 1922 Knoten der Figur (19 %).
        """
        logger.debug(
            f"CharakterAgent: LZG-Intentionen laden fuer user={user_id}, "
            f"character={character_id}, beobachter={beobachter}"
        )
        return db_manager.select(
            """
            SELECT l.intentionen, l.emotion, l.modus, l.sprach_stil, l.tone,
                   l.dimension, l.inhalt
            FROM lzg_knoten l
            LEFT JOIN verbindung v   ON v.kzg_id = l.kzg_quell_key
            LEFT JOIN pipeline_log p ON p.turn_id = v.turn_id
                                    AND p.art = 'turn_roh'
            WHERE l.user_id = %s AND l.character_id = %s AND l.beobachter = %s
              AND l.aktiv = TRUE
              AND (l.intentionen != '[]' OR l.emotion != '' OR l.sprach_stil != '')
              AND p.inhalt ->> 'herkunft' IS DISTINCT FROM 'eigener_impuls'
            ORDER BY l.gewicht_absolut DESC
            LIMIT %s
            """,
            (user_id, character_id, beobachter, PIXIE_CHARAKTER_LZG_LIMIT),
        )

    def _lzg_emotionen_laden(
        self,
        user_id:      str,
        character_id: str,
        beobachter:   str,
    ) -> list[dict]:
        """Laedt LZG-Eintraege mit emotionalen Signalen (paar- + perspektivgefiltert)."""
        logger.debug(
            f"CharakterAgent: LZG-Emotionen laden fuer user={user_id}, "
            f"character={character_id}, beobachter={beobachter}"
        )
        return db_manager.select(
            """
            SELECT emotion, arousal,
                   dimension, inhalt, gewicht_absolut
            FROM lzg_knoten
            WHERE user_id = %s AND character_id = %s AND beobachter = %s
              AND aktiv = TRUE AND emotion != ''
            ORDER BY gewicht_absolut DESC
            LIMIT %s
            """,
            (user_id, character_id, beobachter, PIXIE_CHARAKTER_LZG_LIMIT),
        )

    def _kzg_laden(
        self,
        user_id:           str,
        character_id:      str,
        beobachter_filter: str = "",
        nur_begegnungen:   bool = False,
    ) -> list[dict]:
        """Laedt die staerksten KZG-Eintraege des kanonischen Paares.

        Vorbedingung: `user_id` und `character_id` bilden das kanonische Paar;
            `beobachter_filter` ist 'user', 'assistant' oder leer.
        Nachbedingung: hoechstens `PIXIE_CHARAKTER_KZG_LIMIT` Eintraege,
            absteigend nach `salienz x zeitgewicht`. Leer heisst: kein
            Material in der Ladegrenze, und der Aufrufer meldet es.

        **`nur_begegnungen`** beschraenkt auf Eintraege, deren Ursprungs-Turn
        kein eigener Impuls war. Das Beziehungsprofil braucht das, weil es den
        **Wortlaut** liest und ein Impuls dort als Rede des Gegenuebers
        erschiene. Der Filter gehoert in die Auswahl und nicht dahinter:
        `[gemessen]` 17.08.2026 — von Novas zwanzig staerksten KZG-Eintraegen
        hatten **null** einen erreichbaren Begegnungs-Wortlaut. Nachgelagert
        gefiltert waere ihr Beziehungsprofil dauerhaft leer geblieben, und es
        ist die zweite Haelfte der Rad-Quelle. Derselbe Fehler wie beim
        fehlenden Themenfeld, an derselben Stelle.

        **Ausgewaehlt wird nach Staerke, nicht nach Fundreihenfolge.** Bis zum
        16.08.2026 nahm diese Funktion die ersten 20, die `scan_iter` lieferte,
        und brach ab. SCAN gibt keine Ordnung zu — gemessen am produktiven
        Paar lagen die genommenen 20 auf den Zeitraengen 245 bis 2162 von
        2202, im Mittel 18 Tage alt, fuer ein Profil mit der Frage "Was
        beschaeftigt ihn gerade?".

        Der Aufwand bleibt trotz vollstaendiger Ordnung klein, und zwar
        beweisbar: Die Schluessel tragen ihren Zeitstempel, lassen sich also
        ohne einen einzigen Redis-Zugriff sortieren. Wird absteigend gelesen,
        faellt das Zeitgewicht monoton. Sobald es unter die schwaechste bereits
        gewaehlte effektive Salienz sinkt, kann kein aelterer Eintrag mehr
        aufholen — denn `salienz` ist durch 1 begrenzt, also
        `salienz x gewicht <= gewicht`. Ab da wird nicht weitergelesen.
        """
        # ── Eingabe-Validierung ──
        if beobachter_filter and beobachter_filter not in ("user", "assistant"):
            raise ValueError(
                f"_kzg_laden: unbekannte Perspektive '{beobachter_filter}' — "
                f"erlaubt sind 'user', 'assistant' oder leer"
            )

        jetzt: float = time.time()
        praefix: str = f"kzg:{user_id}:{character_id}:"
        begegnungen: set[str] = (
            _begegnungs_schluessel(user_id, character_id)
            if nur_begegnungen else set()
        )

        # ── Schluessel in Zeitordnung bringen (ohne Redis-Zugriff) ──
        datiert:   list[tuple[float, str]] = []
        undatiert: list[str] = []
        for key in redis_client.scan_iter(match=f"{praefix}*", count=100):
            if isinstance(key, bytes):
                key = key.decode("utf-8")
            marke: str = key.rsplit(":", 1)[-1]
            try:
                # Der Schluessel fuehrt Millisekunden, `erstellt_am` Sekunden.
                datiert.append((float(marke) / 1000.0, key))
            except ValueError:
                # Kein Grund zum Verwerfen: Der Schluessel ist nur die
                # Sortierhilfe, massgeblich ist `erstellt_am` aus dem Hash.
                undatiert.append(key)

        datiert.sort(reverse=True)
        if undatiert:
            logger.warning(
                f"CharakterAgent: {len(undatiert)} KZG-Schluessel ohne lesbare "
                f"Zeitmarke unter '{praefix}' — sie werden zusaetzlich geprueft"
            )

        # Ein Schluessel ohne lesbare Marke gilt als frisch und wird zuerst
        # geprueft: Lieber einmal zuviel geladen als eine Zeile uebersehen,
        # deren wahres Alter erst im Hash steht.
        kandidaten: list[tuple[float, str]] = [(jetzt, k) for k in undatiert] + datiert

        # ── Kandidaten sammeln, staerkster zuerst ──
        gewaehlt:      list[tuple[float, dict]] = []
        fremde_sicht:  int = 0
        gelesen:       int = 0
        zu_alt:        int = 0
        ohne_themen:   int = 0
        ohne_begegnung: int = 0
        abgebrochen:   bool = False

        for position, (zeit, key) in enumerate(kandidaten):
            alter_tage: float = (jetzt - zeit) / 86400

            if alter_tage > PIXIE_CHARAKTER_KZG_LADEGRENZE_TAGE:
                # Zeitsortiert: ab hier ist alles Weitere aelter.
                zu_alt = len(kandidaten) - position
                break

            gewicht: float = zeitgewicht(alter_tage)

            # Der Beweis-Abbruch. `gewicht` ist die Obergrenze jeder
            # effektiven Salienz, die hier noch entstehen kann.
            if len(gewaehlt) >= PIXIE_CHARAKTER_KZG_LIMIT and gewicht <= gewaehlt[-1][0]:
                abgebrochen = True
                break

            if nur_begegnungen and key not in begegnungen:
                ohne_begegnung += 1
                continue

            if beobachter_filter:
                if _hget(redis_client, key, "beobachter") != beobachter_filter:
                    fremde_sicht += 1
                    continue

            gelesen += 1
            eintrag: dict = {
                # Der Schluessel wandert mit. Ueber ihn findet das
                # Beziehungsprofil via `verbindung` zurueck zum Wortlaut des
                # Turns — bis zum 09.08.2026 wurde er hier fallengelassen,
                # und damit war der Weg zur Aeusserung abgeschnitten,
                # obwohl die Tabelle ihn die ganze Zeit fuehrte.
                "_key":               key,
                "themen":             _hget(redis_client, key, "themen"),
                "inhalt":             _hget(redis_client, key, "inhalt"),
                "salienz":            _hget(redis_client, key, "salienz", "0"),
                "erstellt_am":        _hget(redis_client, key, "erstellt_am", "0"),
                "modus":              _hget(redis_client, key, "modus"),
                "emotion":            _hget(redis_client, key, "emotion"),
                "beziehungs_dynamik": _hget(redis_client, key, "beziehungs_dynamik"),
                "tone":               _hget(redis_client, key, "tone"),
            }

            # Ein Eintrag ohne Themenfeld kann im Adaptiv-Prompt nicht landen —
            # die Destillation verwirft ihn. Er darf deshalb keinen der zwanzig
            # Plaetze belegen. Gemessen am 16.08.2026: Unter den juengsten
            # `assistant`-Eintraegen tragen nur 70 % ein Themenfeld, unter den
            # `user`-Eintraegen 100 %; ohne diesen Filter waehlt die Auswahl
            # gerade fuer Nova Plaetze, die garantiert leer bleiben.
            # Das Beziehungsprofil verliert dadurch nichts: Es liest den
            # Wortlaut ueber `_key`, nicht die Themen.
            if not eintrag["themen"].strip():
                ohne_themen += 1
                continue

            # Massgeblich ist `erstellt_am`, nicht die Marke im Schluessel.
            echtes_alter: float = (jetzt - float(eintrag["erstellt_am"] or 0)) / 86400
            effektive_salienz: float = (
                float(eintrag["salienz"] or 0) * zeitgewicht(echtes_alter)
            )

            gewaehlt.append((effektive_salienz, eintrag))
            gewaehlt.sort(key=lambda paar: paar[0], reverse=True)
            del gewaehlt[PIXIE_CHARAKTER_KZG_LIMIT:]

        eintraege: list[dict] = [eintrag for _, eintrag in gewaehlt]

        # ── Ausgabe-Verifikation ──
        if len(eintraege) > PIXIE_CHARAKTER_KZG_LIMIT:
            raise ValueError(
                f"_kzg_laden: {len(eintraege)} Eintraege bei Limit "
                f"{PIXIE_CHARAKTER_KZG_LIMIT} — die Kuerzung hat nicht gegriffen"
            )

        spanne: str = "leer"
        if eintraege:
            alter = [(jetzt - float(e["erstellt_am"] or 0)) / 86400 for e in eintraege]
            spanne = f"{min(alter):.1f} bis {max(alter):.1f} Tage"

        logger.info(
            f"CharakterAgent: KZG gewaehlt fuer Paar ({user_id}, {character_id}) — "
            f"{len(eintraege)} von {gelesen} gelesenen, Alter {spanne} "
            f"(beobachter={beobachter_filter or 'alle'}, "
            f"{fremde_sicht} fremde Perspektive, {zu_alt} ueber der Ladegrenze, "
            f"{ohne_themen} ohne Themen, {ohne_begegnung} ohne Begegnung, "
            f"Abbruch durch Gewichtsschranke: {'ja' if abgebrochen else 'nein'})"
        )

        return eintraege

    # ─────────────────────────────────────────
    # Messreihe der Raeder
    # ─────────────────────────────────────────

    @staticmethod
    def _rad_ueber_reihe_stabilisieren(
        user_id:      str,
        character_id: str,
        erhoben:      tuple[dict, float],
        quelle:       str,
    ) -> tuple[dict, float]:
        """Legt die frische Messung ab und rechnet das Rad aus der Reihe.

        Die frische Messung ist eine von N. Sie geht roh in die Reihe, und der
        gelesene Wert ist deren gewichtetes Mittel — nie umgekehrt
        (novaberg-charakter-rad-messreihe_k.md §2).

        Args:
            erhoben: (Rad, Faktor) der frischen Erhebung, verschachtelt nach
                'hoch'/'runter' wie die Destillation es liefert.
            quelle:  der Profiltext, aus dem gemessen wurde.

        Returns:
            (Rad, Faktor) zum Speichern — aus der Reihe gerechnet. **Bei jedem
            Fehler die frische Messung unveraendert**: Das entspricht dem
            Verhalten vor der Messreihe und ist damit die mildere Abweichung.

        Nachbedingung: Die frische Messung liegt in der Reihe, unabhaengig
            davon, ob die Zusammenfassung gelang.
        """
        # ── Eingabe-Validierung ─────────────────
        rad_frisch, faktor_frisch = erhoben
        hoch:   dict = rad_frisch.get("hoch", {})
        runter: dict = rad_frisch.get("runter", {})
        if not hoch or not runter:
            logger.error(
                f"CharakterAgent: frisches Rad fuer {user_id} traegt "
                f"{len(hoch)} + {len(runter)} Speichen — nicht in die Reihe "
                "aufgenommen, Einzelwert bleibt"
            )
            return rad_frisch, faktor_frisch

        # ── Verarbeitung ────────────────────────
        # **Hier wird nicht mehr abgelegt.** Seit dem 11.08.2026 erhebt
        # `charakter_rad_destillieren` mehrfach und meldet JEDEN Lauf an die
        # Senke des Aufrufers; der Median ist einer davon und liegt damit
        # bereits in der Reihe. Eine Ablage an dieser Stelle zaehlte ihn ein
        # zweites Mal und zoege das Reihenmittel zu ihm hin.
        reihe: list[dict] = reihe_laden(user_id, character_id, RAD_ART_ZUWENDUNG)
        if len(reihe) < 2:
            logger.info(
                f"CharakterAgent: Reihe fuer {user_id} traegt {len(reihe)} "
                "Messung(en) — nichts zu stabilisieren, Einzelwert gilt"
            )
            return rad_frisch, faktor_frisch

        flach: dict[str, float] | None = rad_zusammenfassen(reihe)
        if flach is None:
            logger.error(
                f"CharakterAgent: Reihe fuer {user_id} nicht zusammenfassbar — "
                "Einzelwert bleibt"
            )
            return rad_frisch, faktor_frisch

        # Zurueck in die verschachtelte Form, die der Faktor erwartet. Die
        # Namen kommen aus der frischen Messung, nicht aus einer zweiten Liste:
        # Eine Speiche, die dort fehlt, fehlt auch im Mittel.
        #
        # **Fortgeschrieben statt aufgezaehlt** (23.08.2026). Bis dahin stand
        # hier ein Literal mit genau zwei Schluesseln, und alles andere fiel
        # weg: Am Bestand gemessen trugen **20 von 24** destillierten
        # Zuwendungs-Raedern nur `hoch` und `runter` — `laeufe` und `streuung`
        # waren nie in der Spalte angekommen, obwohl die Erhebung sie liefert.
        # Eine Aufzaehlung verliert lautlos, was sie nicht kennt, und beim
        # naechsten neuen Metadatum wieder.
        rad_neu: dict = dict(rad_frisch)
        rad_neu["hoch"]   = {name: flach[name] for name in hoch}
        rad_neu["runter"] = {name: flach[name] for name in runter}

        # **Beide Speichenfelder werden hier neu gerechnet, ueber die Reihe.**
        # Sie beantworten die Frage *steht hinter dem gespeicherten Wert eine
        # Mehrheit* — und gespeichert wird ab hier das Reihenmittel, nicht das
        # Rad des Median-Laufs. Die Fassung der frischen Erhebung mitzuschleppen
        # ergaebe eine Liste, die einen Median der drei Laeufe gegen eine
        # Speiche aus dem Mittel ueber alle Erhebungen haelt: zwei Groessen,
        # ein Vergleich, keine Aussage.
        #
        # `laeufe` und `streuung` bleiben dagegen die der frischen Erhebung —
        # sie **beschreiben** sie und vergleichen nichts.
        raeder_der_reihe: list[dict] = flache_reihe_als_raeder(reihe, rad_frisch)
        rad_neu["speichen_median"] = speichenweise_mediane(raeder_der_reihe)
        rad_neu["speichen_ohne_mehrheit"] = speichen_ohne_mehrheit(
            rad_neu, rad_neu["speichen_median"],
        )

        try:
            faktor_neu: float = nutzer_gewichtung_berechnen(rad_neu)
        except ValueError as fehler:
            logger.exception(
                f"CharakterAgent: Faktor aus der Reihe nicht berechenbar "
                f"({fehler}) — Einzelwert bleibt"  # noqa: TRY401  — Blatt-Typ
            )
            return rad_frisch, faktor_frisch

        # ── Ausgabe-Verifikation ────────────────
        logger.info(
            f"CharakterAgent: Rad ueber {len(reihe)} Messungen stabilisiert — "
            f"Faktor frisch {faktor_frisch:.3f} -> aus der Reihe {faktor_neu:.3f}"
        )
        return rad_neu, faktor_neu

    @staticmethod
    def _initiative_ueber_reihe_stabilisieren(
        user_id:      str,
        character_id: str,
        quelle:       str,
    ) -> tuple[dict, float] | None:
        """Erhebt das Initiative-Rad, legt jeden Lauf ab und mittelt ueber die Reihe.

        Zwei Stufen, die verschiedene Streuungen wegnehmen: Die drei Laeufe
        einer Erhebung nehmen die des Verfahrens heraus (gemessen 01.08.2026:
        Spanne 0.12 ueber drei Laeufe), die Reihe die zwischen den Erhebungen.

        Returns:
            (Rad, Versatz) aus der Reihe, oder None, wenn keine Erhebung gelang
            — dann behaelt der Aufrufer den bestehenden Wert.

        Nachbedingung: Jeder gelungene Lauf liegt als eigene Zeile in der
            Messreihe, mit derselben `erhebung_id`.
        """
        # ── Verarbeitung ────────────────────────
        node_cfg:    dict = get_node_config("charakter_hash")
        erhebung_id: str  = str(uuid.uuid4())

        def lauf_ablegen(nummer: int, rad: dict, versatz: float) -> None:
            """Senke fuer `initiative_rad_destillieren` — wirft nicht."""
            messung_ablegen(Messung(
                user_id      = user_id,
                character_id = character_id,
                rad_art      = RAD_ART_INITIATIVE,
                speichen     = {**rad.get("hoch", {}), **rad.get("runter", {})},
                faktor       = versatz,
                modell       = PIXIE_ANALYSE_MODEL,
                temperatur   = float(node_cfg.get("temperature", 0.2)),
                presence_penalty = float(node_cfg.get("presence_penalty", 0.0)),
                quelle       = quelle,
                erhebung_id  = erhebung_id,
                lauf         = nummer,
            ))

        erhoben = initiative_rad_destillieren(
            quelle, user_id=user_id, lauf_melden=lauf_ablegen,
        )
        if erhoben is None:
            return None

        rad_frisch, versatz_frisch = erhoben
        reihe: list[dict] = reihe_laden(user_id, character_id, RAD_ART_INITIATIVE)
        if len(reihe) < 2:
            logger.info(
                f"CharakterAgent: Initiative-Reihe fuer {user_id} traegt "
                f"{len(reihe)} Erhebung(en) — nichts zu stabilisieren"
            )
            return rad_frisch, versatz_frisch

        flach: dict[str, float] | None = rad_zusammenfassen(reihe)
        if flach is None:
            logger.error(
                f"CharakterAgent: Initiative-Reihe fuer {user_id} nicht "
                "zusammenfassbar — Einzelwert bleibt"
            )
            return rad_frisch, versatz_frisch

        # Die Metadaten des frischen Laufs reisen mit: Sie beschreiben die
        # juengste Erhebung, nicht die Reihe, und ohne sie verloere die Zeile
        # ihre Herkunftsangabe.
        #
        # **Fortgeschrieben statt aufgezaehlt** (23.08.2026). Die Aufzaehlung
        # nannte `laeufe` und `streuung` und liess damit `speichen_median` und
        # `speichen_ohne_mehrheit` fallen, die am selben Tag dazugekommen
        # waren — gebaut, bezeugt und ohne Wirkung, weil die Stabilisierung
        # der Normalfall ist und nicht der Rand.
        rad_neu: dict = dict(rad_frisch)
        rad_neu["hoch"]       = {name: flach[name] for name in rad_frisch["hoch"]}
        rad_neu["runter"]     = {name: flach[name] for name in rad_frisch["runter"]}
        rad_neu["erhebungen"] = len(reihe)

        # **Beide Speichenfelder werden hier neu gerechnet, ueber die Reihe.**
        # Sie beantworten die Frage *steht hinter dem gespeicherten Wert eine
        # Mehrheit* — und gespeichert wird ab hier das Reihenmittel, nicht das
        # Rad des Median-Laufs. Die Fassung der frischen Erhebung mitzuschleppen
        # ergaebe eine Liste, die einen Median der drei Laeufe gegen eine
        # Speiche aus dem Mittel ueber alle Erhebungen haelt: zwei Groessen,
        # ein Vergleich, keine Aussage.
        #
        # `laeufe` und `streuung` bleiben dagegen die der frischen Erhebung —
        # sie **beschreiben** sie und vergleichen nichts.
        raeder_der_reihe: list[dict] = flache_reihe_als_raeder(reihe, rad_frisch)
        rad_neu["speichen_median"] = speichenweise_mediane(raeder_der_reihe)
        rad_neu["speichen_ohne_mehrheit"] = speichen_ohne_mehrheit(
            rad_neu, rad_neu["speichen_median"],
        )

        try:
            versatz_neu: float = initiative_versatz_berechnen(rad_neu)
        except ValueError as fehler:
            logger.exception(
                f"CharakterAgent: Versatz aus der Reihe nicht berechenbar "
                f"({fehler}) — Einzelwert bleibt"  # noqa: TRY401  — Blatt-Typ
            )
            return rad_frisch, versatz_frisch

        # ── Ausgabe-Verifikation ────────────────
        logger.info(
            f"CharakterAgent: Initiative-Rad ueber {len(reihe)} Erhebungen "
            f"stabilisiert — Versatz frisch {versatz_frisch:+.4f} -> aus der "
            f"Reihe {versatz_neu:+.4f}"
        )
        return rad_neu, versatz_neu

    # ─────────────────────────────────────────
    # Ergebnis speichern
    # ─────────────────────────────────────────

    @staticmethod
    def _ergebnis_speichern(user_id: str, character_id: str, ergebnis: dict) -> None:
        """Schreibt die 5 Profile per UPSERT in charakter_hash (Paar-Schema).

        Jedes Profil wird nur ueberschrieben wenn der neue Wert nicht-leer ist.
        Der zugehoerige Zeitstempel wird nur dann auf NOW() gesetzt.
        """
        # Rad-Werte vorbereiten. `_erhoben` ist die einzige Bedingung: Ist es
        # None, blieb die Erhebung aus, und alle vier Spalten bleiben, wie sie
        # sind. Ein erfundener Faktor waere schlimmer als ein alter.
        _erhoben:    float | None = ergebnis.get("nutzer_gewichtung")
        _rad_faktor: float = _erhoben if _erhoben is not None else RAD_NABE
        _rad_quelle: str   = "destilliert" if _erhoben is not None else "default"
        _rad_json:   str   = (
            ergebnis.get("nutzer_gewichtung_rad") or json.dumps(RAD_LEER)
        )
        if isinstance(_rad_json, dict):
            _rad_json = json.dumps(_rad_json)

        # Initiative-Rad, dieselbe Logik: None heisst "nicht erhoben", dann
        # bleiben alle vier Spalten stehen.
        _init_erhoben: float | None = ergebnis.get("initiative_versatz")
        _init_wert:    float = _init_erhoben if _init_erhoben is not None else INITIATIVE_RAD_NABE
        _init_quelle:  str   = "destilliert" if _init_erhoben is not None else "default"
        _init_json:    str   = (
            ergebnis.get("initiative_versatz_rad") or json.dumps(INITIATIVE_RAD_LEER)
        )
        if isinstance(_init_json, dict):
            _init_json = json.dumps(_init_json)

        db_manager.execute(
            """
            INSERT INTO charakter_hash
                (user_id, character_id,
                 kern_hash, adaptive_hash,
                 intentions_profil, emotions_profil, beziehungsprofil,
                 kern_aktualisiert_am, adaptive_aktualisiert_am,
                 intentions_aktualisiert_am, emotions_aktualisiert_am,
                 beziehung_aktualisiert_am,
                 nutzer_gewichtung, nutzer_gewichtung_quelle,
                 nutzer_gewichtung_rad, nutzer_gewichtung_am,
                 initiative_versatz, initiative_versatz_quelle,
                 initiative_versatz_rad, initiative_versatz_am)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW(), NOW(), NOW(),
                    %s, %s, %s,
                    CASE WHEN %s IS NOT NULL THEN NOW() ELSE NULL END,
                    %s, %s, %s,
                    CASE WHEN %s IS NOT NULL THEN NOW() ELSE NULL END)
            ON CONFLICT (user_id, character_id) DO UPDATE SET
                kern_hash = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.kern_hash END,
                adaptive_hash = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.adaptive_hash END,
                intentions_profil = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.intentions_profil END,
                emotions_profil = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.emotions_profil END,
                beziehungsprofil = CASE WHEN %s != '' THEN %s
                    ELSE charakter_hash.beziehungsprofil END,
                kern_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.kern_aktualisiert_am END,
                adaptive_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.adaptive_aktualisiert_am END,
                intentions_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.intentions_aktualisiert_am END,
                emotions_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.emotions_aktualisiert_am END,
                beziehung_aktualisiert_am = CASE WHEN %s != '' THEN NOW()
                    ELSE charakter_hash.beziehung_aktualisiert_am END,
                -- Charakter-Rad: NULL heisst "nicht erhoben". Dann bleibt der
                -- bestehende Faktor stehen — ein misslungener Lauf darf einen
                -- destillierten Wert nicht durch den Default ersetzen.
                nutzer_gewichtung = CASE WHEN %s IS NOT NULL THEN %s
                    ELSE charakter_hash.nutzer_gewichtung END,
                nutzer_gewichtung_quelle = CASE WHEN %s IS NOT NULL THEN 'destilliert'
                    ELSE charakter_hash.nutzer_gewichtung_quelle END,
                nutzer_gewichtung_rad = CASE WHEN %s IS NOT NULL THEN %s
                    ELSE charakter_hash.nutzer_gewichtung_rad END,
                nutzer_gewichtung_am = CASE WHEN %s IS NOT NULL THEN NOW()
                    ELSE charakter_hash.nutzer_gewichtung_am END,
                -- Initiative-Rad: dieselbe Regel. Ein misslungener Lauf darf
                -- einen destillierten Versatz nicht durch die Nabe ersetzen.
                initiative_versatz = CASE WHEN %s IS NOT NULL THEN %s
                    ELSE charakter_hash.initiative_versatz END,
                initiative_versatz_quelle = CASE WHEN %s IS NOT NULL THEN 'destilliert'
                    ELSE charakter_hash.initiative_versatz_quelle END,
                initiative_versatz_rad = CASE WHEN %s IS NOT NULL THEN %s
                    ELSE charakter_hash.initiative_versatz_rad END,
                initiative_versatz_am = CASE WHEN %s IS NOT NULL THEN NOW()
                    ELSE charakter_hash.initiative_versatz_am END
            """,
            (
                user_id, character_id,
                ergebnis["kern"], ergebnis["adaptiv"],
                ergebnis["intentions_profil"], ergebnis["emotions_profil"],
                ergebnis["beziehungsprofil"],
                # INSERT — Charakter-Rad. Ohne Erhebung die Spalten-Defaults,
                # damit eine neue Zeile denselben Beleg traegt wie eine
                # destillierte: die 0.9 ist dann nachrechenbar statt behauptet.
                _rad_faktor, _rad_quelle, _rad_json, _rad_faktor,
                _init_wert, _init_quelle, _init_json, _init_wert,
                # ON CONFLICT — Profil-Werte (je 2×: Bedingung + Wert)
                ergebnis["kern"], ergebnis["kern"],
                ergebnis["adaptiv"], ergebnis["adaptiv"],
                ergebnis["intentions_profil"], ergebnis["intentions_profil"],
                ergebnis["emotions_profil"], ergebnis["emotions_profil"],
                ergebnis["beziehungsprofil"], ergebnis["beziehungsprofil"],
                # ON CONFLICT — Zeitstempel-Bedingungen (je 1×)
                ergebnis["kern"],
                ergebnis["adaptiv"],
                ergebnis["intentions_profil"],
                ergebnis["emotions_profil"],
                ergebnis["beziehungsprofil"],
                # ON CONFLICT — Charakter-Rad (Bedingung je 1×, Werte 2×)
                _erhoben, _rad_faktor,
                _erhoben,
                _erhoben, _rad_json,
                _erhoben,
                # ON CONFLICT — Initiative-Rad (Bedingung je 1×, Werte 2×)
                _init_erhoben, _init_wert,
                _init_erhoben,
                _init_erhoben, _init_json,
                _init_erhoben,
            ),
        )
