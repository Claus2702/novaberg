"""CharakterAgent — Destilliert 5 Charakter-Profile aus LZG+KZG.

Ein LLM-Call pro Profil pro User. Nur aktiv wenn hash_dirty gesetzt.
Migriert aus: services/shadow_agent/tasks/charakter_hash.py
"""

import json
import logging
import uuid

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    AKTIVES_PAAR_USER_ID,
    ASSISTANT_USER_ID,
    redis_client,
    ollama_gpu_client,
    EMBED_MODEL,
    POSTGRES_URL,
    ZIEL_MAX_LANGFRISTIG,
    PIXIE_CHARAKTER_PRIORITAET,
    PIXIE_CHARAKTER_INTERVALL_SEKUNDEN,
    PIXIE_CHARAKTER_LZG_LIMIT,
    PIXIE_CHARAKTER_KZG_LIMIT,
    PIXIE_ANALYSE_MODEL,
    get_node_config,
)
from tools.db_manager import db_manager
from agents.charakter.destillation import (
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
                lzg_kern = self._lzg_kern_laden(
                    kanon_user_id, kanon_character_id, beobachter,
                )
                lzg_intentionen = self._lzg_intentionen_laden(
                    kanon_user_id, kanon_character_id, beobachter,
                )
                lzg_emotionen = self._lzg_emotionen_laden(
                    kanon_user_id, kanon_character_id, beobachter,
                )

                # ── KZG-Eintraege laden (kanonisches Paar + beobachter-Filter) ──
                kzg_eintraege = self._kzg_laden(
                    kanon_user_id, kanon_character_id,
                    beobachter_filter=beobachter,
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
                    ergebnis["kern"] = kern_hash_destillieren(lzg_kern, user_id=subjekt_user_id)
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
                    ergebnis["beziehungsprofil"] = beziehungsprofil_destillieren(kzg_eintraege, user_id=subjekt_user_id)
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
                        erhoben = charakter_rad_destillieren(rad_quelle, user_id=subjekt_user_id)
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
        """Laedt LZG-Eintraege mit Kommunikations-Signalen (paar- + perspektivgefiltert)."""
        logger.debug(
            f"CharakterAgent: LZG-Intentionen laden fuer user={user_id}, "
            f"character={character_id}, beobachter={beobachter}"
        )
        return db_manager.select(
            """
            SELECT intentionen, emotion, modus, sprach_stil, tone,
                   dimension, inhalt
            FROM lzg_knoten
            WHERE user_id = %s AND character_id = %s AND beobachter = %s
              AND aktiv = TRUE
              AND (intentionen != '[]' OR emotion != '' OR sprach_stil != '')
            ORDER BY gewicht_absolut DESC
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
    ) -> list[dict]:
        """Laedt KZG-Eintraege aus dem kanonischen Paar via SCAN.

        Args:
            user_id: Subjekt-ID des kanonischen Paares.
            character_id: Charakter-ID des kanonischen Paares.
            beobachter_filter: Wenn gesetzt, nur Eintraege mit diesem
                Beobachter-Wert laden ('user' oder 'assistant').
                Leerer String = kein Filter.
        """
        eintraege: list[dict] = []
        uebersprungen: int = 0

        for key in redis_client.scan_iter(match=f"kzg:{user_id}:{character_id}:*", count=100):
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            # Beobachter-Filter: nur Eintraege der gewuenschten Perspektive
            if beobachter_filter:
                eintrag_beobachter: str = _hget(redis_client, key, "beobachter")
                if eintrag_beobachter != beobachter_filter:
                    uebersprungen += 1
                    continue

            eintrag: dict = {
                "themen":             _hget(redis_client, key, "themen"),
                "inhalt":             _hget(redis_client, key, "inhalt"),
                "salienz":            _hget(redis_client, key, "salienz", "0"),
                "erstellt_am":        _hget(redis_client, key, "erstellt_am", "0"),
                "modus":              _hget(redis_client, key, "modus"),
                "emotion":            _hget(redis_client, key, "emotion"),
                "beziehungs_dynamik": _hget(redis_client, key, "beziehungs_dynamik"),
                "tone":               _hget(redis_client, key, "tone"),
            }
            eintraege.append(eintrag)

            if len(eintraege) >= PIXIE_CHARAKTER_KZG_LIMIT:
                break

        if beobachter_filter:
            logger.info(
                f"CharakterAgent: KZG geladen fuer Paar ({user_id}, {character_id}) — "
                f"{len(eintraege)} Eintraege (beobachter={beobachter_filter}, "
                f"{uebersprungen} uebersprungen)"
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
        node_cfg: dict = get_node_config("charakter_hash")
        messung_ablegen(Messung(
            user_id      = user_id,
            character_id = character_id,
            rad_art      = RAD_ART_ZUWENDUNG,
            speichen     = {**hoch, **runter},
            faktor       = faktor_frisch,
            modell       = PIXIE_ANALYSE_MODEL,
            temperatur   = float(node_cfg.get("temperature", 0.2)),
            presence_penalty = float(node_cfg.get("presence_penalty", 0.0)),
            quelle       = quelle,
        ))

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
        rad_neu: dict = {
            "hoch":   {name: flach[name] for name in hoch},
            "runter": {name: flach[name] for name in runter},
        }

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

        # Die Metadaten des frischen Laufs (`laeufe`, `streuung`) reisen mit:
        # Sie beschreiben die juengste Erhebung, nicht die Reihe, und ohne sie
        # verloere die Zeile ihre Herkunftsangabe.
        rad_neu: dict = {
            "hoch":     {name: flach[name] for name in rad_frisch["hoch"]},
            "runter":   {name: flach[name] for name in rad_frisch["runter"]},
            "laeufe":   rad_frisch.get("laeufe", []),
            "streuung": rad_frisch.get("streuung", 0.0),
            "erhebungen": len(reihe),
        }

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
