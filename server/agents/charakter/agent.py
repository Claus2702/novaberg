"""CharakterAgent — Destilliert 5 Charakter-Profile aus LZG+KZG.

Ein LLM-Call pro Profil pro User. Nur aktiv wenn hash_dirty gesetzt.
Migriert aus: services/shadow_agent/tasks/charakter_hash.py
"""

import json
import logging

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    redis_client,
    ollama_gpu_client,
    EMBED_MODEL,
    POSTGRES_URL,
    ZIEL_MAX_LANGFRISTIG,
    PIXIE_CHARAKTER_PRIORITAET,
    PIXIE_CHARAKTER_INTERVALL_SEKUNDEN,
    PIXIE_CHARAKTER_LZG_LIMIT,
    PIXIE_CHARAKTER_KZG_LIMIT,
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
    RAD_NABE,
    INITIATIVE_RAD_NABE,
    RAD_LEER,
    INITIATIVE_RAD_LEER,
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

        paare: list[tuple[str, str]] = [
            (DEFAULT_USER_ID, ASSISTANT_USER_ID),
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
                    erhoben = charakter_rad_destillieren(rad_quelle, user_id=subjekt_user_id)
                    if erhoben is not None:
                        ergebnis["nutzer_gewichtung_rad"], ergebnis["nutzer_gewichtung"] = erhoben

                    # Zweites Rad, dieselbe Quelle, andere Frage: ueberlaesst
                    # sie im Gespraech die Fuehrung oder behaelt sie sie.
                    # Ein eigener Call, weil das erste Rad seine Speichen mit
                    # Wissbegier und Pflicht buendelt, die hier nichts zu
                    # suchen haben (novaberg-gv-initiative_k.md §6).
                    erhoben_init = initiative_rad_destillieren(
                        rad_quelle, user_id=subjekt_user_id,
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
                                # Alte langfristige Ziele deaktivieren
                                alte_ziele: list[dict] = ziele_aktive_laden(
                                    POSTGRES_URL, user_id=ASSISTANT_USER_ID,
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
