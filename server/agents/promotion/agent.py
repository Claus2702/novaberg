"""PromotionAgent — KZG -> LZG Promotion mit Zwei-Call-Pattern.

Call 1: Klassifikation (Fakt/Erinnerung) + Entitaeten-Erkennung.
Call 2: Fakten-Extraktion als Tripel (nur bei Fakten).
4 Qualitaetsfilter: Speaker (O5), Interface (O6), Objekt (O11), Tautologie (O12).

Migriert aus: services/shadow_agent/tasks/lzg_promotion.py
Queue wird VOLLSTAENDIG abgearbeitet (KZG hat TTL!).
"""

import json
import logging

from collections import Counter
from datetime    import datetime, timezone

import numpy as np

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ASSISTANT_USER_ID, DEFAULT_USER_ID,
    redis_client, POSTGRES_URL, get_node_config,
    PIXIE_PROMOTION_PRIORITAET, PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
    CLUSTER_MIN_EINTRAEGE, CLUSTER_THEMEN_SIMILARITY,
    CLUSTER_LZG_SIMILARITY, CLUSTER_WIDERSPRUCH_DECAY_FAKTOR,
    CLUSTER_BESTAETIGUNG_BOOST,
    PIXIE_AKTIV,
)
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.kzg import _kzg_prefix
from services.model_services import model_service, EmbedRequest, BackgroundRequest
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.promotion")


class PromotionAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "promotion"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["lzg_promotion", "fakten_extraktion"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    def periodic_task(self) -> PeriodicTask | None:
        return PeriodicTask(
            name="promotion",
            priority=PIXIE_PROMOTION_PRIORITAET,
            interval=PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
            description="KZG -> LZG Promotion (Zwei-Call, Fakten-Extraktion)",
        )

    def build_graph(self):
        return None

    # ─────────────────────────────────────────
    # Audit-Log (EVA — Eingabe/Ausgabe-Trail)
    # ─────────────────────────────────────────
    @staticmethod
    def _audit_log(
        user_id:  str,
        aufgabe:  str,
        status:   str,
        ergebnis: str,
    ) -> None:
        """Schreibt einen Audit-Eintrag ins hintergrund_log.

        Failsafe: Bei DB-Fehler wird nur logger.critical gerufen — kein
        retry, um Endlos-Rekursion bei kaputter Audit-Senke zu vermeiden.

        Args:
            user_id:  Owner des Auftrags (Queue-Schluessel).
            aufgabe:  Kurzbezeichnung der Aufgabe (z.B. "promotion:<kzg_key>").
            status:   "gestartet" | "erledigt" | "fehler".
            ergebnis: Freitext-Beschreibung des Ausgangs.
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

    def invoke(self, state: AgentState) -> AgentState:
        """Arbeitet die Promotion-Queue komplett ab."""
        user_id: str = state["kontext"].get("context_user_id", DEFAULT_USER_ID)
        queue_key: str = f"queue:{user_id}"
        promotet: int = 0
        fehler:   int = 0

        while True:
            raw = redis_client.lpop(queue_key)
            if not raw:
                break

            try:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                auftrag: dict = json.loads(raw)
                self._eintrag_verarbeiten(auftrag, user_id)
                promotet += 1
            except Exception as ex:
                logger.error(f"Promotion: Fehler bei Eintrag: {ex}", exc_info=True)
                fehler += 1

        if promotet > 0:
            logger.info(f"Promotion: {promotet} Eintraege promotet, {fehler} Fehler")
        else:
            logger.debug("Promotion: Queue leer — nichts zu tun")

        # Cluster-Promotion: thematisch verwandte KZG-Eintraege zusammenfuehren
        character_id: str = state["kontext"].get("character_id", ASSISTANT_USER_ID)
        cluster_promotet: int = self._cluster_promotion(user_id, character_id)

        state["ergebnis"] = {
            "promotet": promotet,
            "cluster_promotet": cluster_promotet,
            "fehler": fehler,
        }
        state["status"] = "abgeschlossen"
        return state

    # ─────────────────────────────────────────
    # Eintrag verarbeiten (EVA — Eingabe, Verarbeitung, Ausgabe)
    # ─────────────────────────────────────────
    def _eintrag_verarbeiten(self, auftrag: dict, user_id: str) -> None:
        """Verarbeitet einen einzelnen Queue-Eintrag nach EVA-Prinzip.

        Eingabe wird gegen Parameter und Quelldaten validiert, Ausgabe
        gegen das tatsaechliche Schreibergebnis verifiziert. Jeder Schritt
        wird ins hintergrund_log auditet (gestartet / erledigt / fehler).
        """

        kzg_key:   str   = auftrag.get("key", "")
        themen:    str   = auftrag.get("themen", "")
        salienz:   float = auftrag.get("salienz", 0.0)
        dimension: str   = auftrag.get("dimension", "kontext")

        aufgabe: str = f"promotion:{kzg_key or '?'}"

        # ── Eingabe-Audit ──────
        eingabe_zsf: str = (
            f"kzg_key='{kzg_key}', themen='{themen}', salienz={salienz:.3f}"
        )
        logger.info(f"Promotion: gestartet — {eingabe_zsf}")
        self._audit_log(user_id, aufgabe, "gestartet", eingabe_zsf)

        # ── Vorbedingung 1: KZG-Key vorhanden ──────
        if not kzg_key:
            grund: str = "Auftrag ohne KZG-Key — verworfen"
            logger.error(f"Promotion: {grund}")
            self._audit_log(user_id, aufgabe, "fehler", grund)
            return

        # ── Vorbedingung 2: KZG-Eintrag existiert noch in Redis ──────
        if not redis_client.exists(kzg_key):
            grund = (
                f"KZG-Key '{kzg_key}' nicht mehr vorhanden "
                f"(TTL abgelaufen) — verworfen"
            )
            logger.error(f"Promotion: {grund}")
            self._audit_log(user_id, aufgabe, "fehler", grund)
            return

        # ── KZG-Inhalt lesen ──────
        def _hget(field: str, default: str = "") -> str:
            val = redis_client.hget(kzg_key, field)
            if val is None:
                return default
            return val.decode("utf-8") if isinstance(val, bytes) else val

        inhalt: str = _hget("inhalt")

        # ── Vorbedingung 3: Inhalt nicht leer ──────
        if not inhalt:
            grund = (
                f"KZG-Key '{kzg_key}' existiert, aber Feld 'inhalt' "
                f"ist leer — verworfen"
            )
            logger.error(f"Promotion: {grund}")
            self._audit_log(user_id, aufgabe, "fehler", grund)
            return

        # ── Restliche KZG-Felder laden (nach erfolgreicher Validierung) ──
        haeufigkeit:        int   = int(float(_hget("haeufigkeit", "1")))
        intentionen:        str   = _hget("intentionen", "[]")
        emotion:            str   = _hget("emotion")
        modus:              str   = _hget("modus")
        arousal:            float = float(_hget("arousal", "0.5"))
        sprach_stil:        str   = _hget("sprach_stil")
        beziehungs_dynamik: str   = _hget("beziehungs_dynamik")
        tone:               str   = _hget("tone")

        # Paar-Felder aus dem KZG-Eintrag (KZG-Paar-Schema). Fallback fuer
        # Alt-Eintraege ohne diese Felder: Standardpaar + Beobachter "user".
        character_id: str = _hget("character_id") or ASSISTANT_USER_ID
        beobachter:   str = _hget("beobachter")   or "user"

        logger.info(f"LZG: Paar={user_id}:{character_id}, Beobachter={beobachter}")

        # ── 0. Bekannte Entitaeten laden ──────
        bekannte: list[dict] = EntitaetenRepository.find_by_user(POSTGRES_URL, user_id)

        user_name:  str        = user_id
        user_id_db: int | None = None
        for bek in bekannte:
            if bek.get("typ") == "user" or (bek.get("name") or "").lower() == user_id.lower():
                user_name  = bek["name"]
                user_id_db = bek["id"]
                break

        # ── 1. Call 1: Klassifikation + Entitaeten ──────
        call1_ergebnis: dict = self._klassifiziere(
            themen=themen, inhalt=inhalt, bekannte_entitaeten=bekannte,
        )
        call1_ergebnis = self._call1_nachbearbeiten(
            call1_ergebnis, user_name, user_id_db, bekannte,
        )

        klassifikation: str        = call1_ergebnis.get("klassifikation", "erinnerung")
        entitaeten:     list[dict] = call1_ergebnis.get("entitaeten", [])

        logger.info(
            f"Promotion Call 1: '{themen}' -> {klassifikation}, "
            f"{len(entitaeten)} Entitaeten"
        )

        # ── 2. Call 2: Fakten-Extraktion (nur bei fakt/gemischt) ──────
        extrahierte_fakten_anzahl: int = 0
        if klassifikation in ("fakt", "gemischt"):
            call2_ergebnis: dict = self._extrahiere_fakten(
                inhalt=inhalt, entitaeten=entitaeten,
                user_name=user_name, user_id_db=user_id_db,
            )
            call2_ergebnis = self._call2_nachbearbeiten(
                call2_ergebnis, entitaeten, user_name, bekannte,
            )

            extrahierte_fakten: list[dict] = call2_ergebnis.get("fakten", [])
            extrahierte_fakten_anzahl = len(extrahierte_fakten)
            logger.info(
                f"Promotion Call 2: {extrahierte_fakten_anzahl} Fakten extrahiert"
            )

            if extrahierte_fakten:
                try:
                    from plugins.fakten_manager.manager import FaktenManager
                    fakten_manager = FaktenManager()
                    fakten_manager.fakten_verarbeiten(
                        aktion="create",
                        entitaeten=entitaeten,
                        fakten=extrahierte_fakten,
                        user_id=user_id,
                        postgres_url=POSTGRES_URL,
                        redis_client=redis_client,
                    )
                except Exception as ex:
                    logger.error(f"Promotion: Fehler bei Fakten-Verarbeitung: {ex}", exc_info=True)

        # ── 3. Erinnerung ins LZG (bei erinnerung/gemischt) ──────
        lzg_eintrag_geschrieben: bool = False
        if klassifikation in ("erinnerung", "gemischt"):
            entitaets_tags: list[str] = [
                e["name"] for e in entitaeten if e.get("ist_referenz", False)
            ]

            embed_response = model_service.embed.submit_sync(
                EmbedRequest(text=f"{themen} {inhalt}")
            )
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Promotion: LZG-INSERT Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )
            embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

            themen_list: list[str] = sorted({t.strip() for t in themen.split(",") if t.strip()})

            kzg_erstellt_am_raw: str = _hget("erstellt_am")
            kzg_erstellt_am: datetime | None
            try:
                kzg_erstellt_am = (
                    datetime.fromtimestamp(float(kzg_erstellt_am_raw), tz=timezone.utc)
                    if kzg_erstellt_am_raw else None
                )
            except ValueError:
                kzg_erstellt_am = None

            db_manager.execute(
                """
                INSERT INTO langzeitgedaechtnis
                    (user_id, character_id, beobachter,
                     dimension, inhalt, gewicht, haeufigkeit,
                     embedding, intentionen, emotion, modus,
                     arousal,
                     sprach_stil, beziehungs_dynamik, tone,
                     themen, kzg_erstellt_am,
                     verstaerkt_am)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, NOW())
                """,
                (user_id, character_id, beobachter,
                 dimension, inhalt, min(salienz, 1.0), haeufigkeit,
                 embedding_str, intentionen, emotion, modus,
                 arousal,
                 sprach_stil, beziehungs_dynamik, tone,
                 themen_list, kzg_erstellt_am),
            )
            lzg_eintrag_geschrieben = True

            if PIXIE_AKTIV:
                redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")
            else:
                logger.debug("promotion: hash_dirty-Setzer uebersprungen (PIXIE_AKTIV=False)")

            logger.info(
                f"Promotion: '{themen}' -> LZG als Erinnerung "
                f"(tags: {entitaets_tags})"
            )
            logger.info(
                f"M3 Single-Promotion: themen={len(themen_list)} Tags, "
                f"kzg_erstellt_am={kzg_erstellt_am}"
            )

        # ── Ausgabe-Verifikation ──────
        if klassifikation not in ("fakt", "erinnerung", "gemischt"):
            grund = (
                f"Klassifikation '{klassifikation}' produziert weder Fakt "
                f"noch Erinnerung — kein LZG-Schreib-Pfad"
            )
            logger.error(f"Promotion: {grund}")
            self._audit_log(user_id, aufgabe, "fehler", grund)
            return

        ausgabe_zsf: str = (
            f"klassifikation={klassifikation}, "
            f"extrahierte_fakten_anzahl={extrahierte_fakten_anzahl}, "
            f"lzg_eintrag_geschrieben={str(lzg_eintrag_geschrieben).lower()}"
        )
        logger.info(f"Promotion: erledigt — {ausgabe_zsf}")
        self._audit_log(user_id, aufgabe, "erledigt", ausgabe_zsf)

    # ─────────────────────────────────────────
    # Call 1: Klassifikation + Entitaeten
    # ─────────────────────────────────────────
    @staticmethod
    def _klassifiziere(
        themen:              str,
        inhalt:              str,
        bekannte_entitaeten: list[dict],
    ) -> dict:
        """Call 1: Klassifikation + Entitaeten-Erkennung."""

        if bekannte_entitaeten:
            lines: list[str] = []
            for e in bekannte_entitaeten:
                if e.get("typ") == "user":
                    lines.insert(0,
                        f">>> SPEAKER: {e['name']} (ID:{e['id']}) — "
                        f"Das ist der User. 'Ich' = {e['name']}. "
                        f"Verwende IMMER '{e['name']}' als Name, "
                        f"NIEMALS 'Nutzer', 'User' oder 'Der Nutzer'. <<<"
                    )
                else:
                    lines.append(f"- {e['name']} (ID:{e['id']}, {e['typ']})")
            bekannte_str: str = "\n".join(lines)
        else:
            bekannte_str = "Keine bekannten Entitaeten"

        system_prompt: str = (
            "Du bist ein Wissensanalyst. Deine EINZIGE Aufgabe: "
            "Klassifiziere die Aussage und erkenne Entitaeten.\n\n"
            "KLASSIFIKATION:\n"
            '- "fakt" = enthaelt ueberpruefbare, dauerhafte Informationen '
            "ueber Personen, Orte, Beziehungen, Eigenschaften, Vorlieben, Abneigungen\n"
            '- "erinnerung" = Erlebnis, Emotion, Meinung, temporaerer Zustand '
            "(heute muede, gerade erkaeltet, bin sauer)\n"
            '- "gemischt" = enthaelt beides\n\n'
            "TEMPORAERE ZUSTAENDE sind IMMER \"erinnerung\". "
            "Signalwoerter: heute, gerade, momentan, jetzt, im Moment.\n"
            "Vorlieben und Abneigungen (mag Kaffee, hasst Fisch) sind FAKTEN "
            "auch wenn das Objekt ein Interface ist.\n"
            "Emotionale Ausrufe ohne konkrete dauerhafte Informationen "
            'sind IMMER "erinnerung".\n\n'
            'SPEAKER: "Ich" = User (immer erste Entitaet, immer Referenz)\n\n'
            "ENTITAETEN-TYPEN:\n"
            "- REFERENZ: Konkret, identifizierbar, hat einen EIGENNAMEN. "
            "Beispiele: Anna (Person), Nuernberg (Stadt), BMW (Firma). "
            "-> Eine Referenz ist etwas, das man auf ein Namensschild schreiben koennte.\n"
            "- INTERFACE: Allgemein, kein Eigenname, ein Gattungsbegriff oder Konzept. "
            "Beispiele: Gehirn, Kuenstliche Intelligenz, Wohnung, Kaffee, Astronomie. "
            "-> Wenn man es nicht auf ein Namensschild schreiben wuerde, ist es ein Interface.\n\n"
            "WICHTIG: Wissenschaftliche Begriffe, Fachgebiete, abstrakte Konzepte, "
            "Organe, Aktivitaeten und Lebensmittel sind IMMER Interfaces. "
            "Nur Eigennamen sind Referenzen.\n\n"
            "Extrahiere KEINE Fakten. Nur Klassifikation und Entitaeten.\n"
            "Antworte in JSON ohne Markdown-Backticks."
        )

        user_prompt: str = (
            f"THEMEN: {themen}\n"
            f"INHALT: {inhalt}\n"
            f"BEKANNTE ENTITAETEN: {bekannte_str}\n\n"
            "Format:\n"
            '{"klassifikation": "fakt|erinnerung|gemischt", '
            '"entitaeten": [{"name": "", "typ": "person|ort|organisation|objekt", '
            '"ist_referenz": true, "bekannte_id": null}]}'
        )

        node_cfg = get_node_config("lzg_promotion")

        # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
        # _klassifiziere() laeuft im PromotionAgent, sync invoked aus
        # services/pixie/dispatch.py via asyncio.to_thread → submit_sync.
        # modus="sprache" — das sprache-Backend des BackgroundWorker zeigt auf
        # das CPU-Sprachmodell. Beifund: JSON-Erwartung via Sprachmodell;
        # Routing-Korrektur nicht Teil von G5. Caller-seitiger Markdown-
        # Strip + json.loads entfernt — der Worker uebernimmt das via
        # parse_json_strict bei expect_json=True. Hardcoded Klassifikations-
        # Fallback bleibt unangetastet (HARTE GRENZE: Promotion-Logik).
        try:
            response = model_service.background.submit_sync(BackgroundRequest(
                messages          = [{"role": "user", "content": user_prompt}],
                modus             = "sprache",
                system            = system_prompt,
                temperature       = node_cfg.get("temperature", 0.1),
                expect_json       = True,
                max_output_tokens = node_cfg.get("max_output_tokens"),
                caller            = "pixie/promotion/call1",
            ))
            return response.parsed
        except json.JSONDecodeError as fehler:
            logger.error(f"Promotion Call 1: Ungueltiges JSON: {fehler}")
            return {"klassifikation": "erinnerung", "entitaeten": []}

    # ─────────────────────────────────────────
    # Call 2: Fakten-Extraktion
    # ─────────────────────────────────────────
    @staticmethod
    def _extrahiere_fakten(
        inhalt:     str,
        entitaeten: list[dict],
        user_name:  str = "",
        user_id_db: int | None = None,
    ) -> dict:
        """Call 2: Fakten-Extraktion als Tripel."""

        ent_str: str = "\n".join(
            f"- {e['name']} (ID:{e.get('bekannte_id', 'neu')}, "
            f"{'Referenz' if e.get('ist_referenz') else 'Interface'}, {e.get('typ', '')})"
            for e in entitaeten
        )

        system_prompt: str = (
            "Du bist ein Fakten-Extraktor. Du bekommst einen Text und "
            "eine Liste aufgeloester Entitaeten. Extrahiere alle Fakten als Tripel.\n\n"
            "REGELN:\n"
            "1. Subjekt ist IMMER eine Referenz-Entitaet aus der Liste\n"
            "2. Objekt ist entweder eine Referenz-Entitaet (Typ 1) oder "
            "ein Interface-Wert als String (Typ 2)\n"
            "3. Bei Referenz-Objekten: objekt_id setzen, objekt_wert=null\n"
            "4. Bei Interface-Objekten: objekt_id=null, objekt_wert=String\n"
            "5. Attribut in SCREAMING_SNAKE_CASE "
            "(WOHNORT, HAT_SCHWESTER, MAG_NICHT, ARBEITET_ALS)\n"
            "6. Fakt-Text muss eigenstaendig und kontextfrei sein\n"
            "7. Jeden Fakt genau EINMAL — keine Duplikate\n"
            '8. Negationen: "mag keinen Fisch" = MAG_NICHT, ist_negation=true\n'
            '9. temporal: "permanent" (Schwester sein), '
            '"aktuell" (wohnt in), "vergangen" (hat gewohnt in)\n'
            "10. Beziehungen vom User aus formulieren: "
            '"Claus HAT_SCHWESTER Anna" nicht "Anna IST_SCHWESTER"\n'
            "11. Interfaces ohne Bezug zu einer Referenz ignorieren\n\n"
            "Antworte in JSON ohne Markdown-Backticks."
        )

        speaker_line: str = (
            f"SPEAKER (User): {user_name} (ID:{user_id_db})\n"
            if user_name else ""
        )

        user_prompt: str = (
            f"{speaker_line}"
            f"INHALT: {inhalt}\n"
            f"AUFGELOESTE ENTITAETEN:\n{ent_str}\n\n"
            "Format:\n"
            '{"fakten": [{"subjekt": "", "subjekt_id": null, '
            '"attribut": "SCREAMING_SNAKE_CASE", "objekt": "", '
            '"objekt_id": null, "objekt_wert": null, '
            '"fakt_text": "", "ist_negation": false, '
            '"temporal": "permanent|aktuell|vergangen"}]}'
        )

        node_cfg = get_node_config("lzg_promotion")

        # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
        # _extrahiere_fakten() laeuft im PromotionAgent, gleicher to_thread-
        # Kontext wie _klassifiziere. modus="sprache" analog (Routing-
        # Beifund). HARTE GRENZE: Hardcoded Fakten-Fallback bleibt — die
        # Fakten-Extraktions-Logik wird nicht angefasst (PROMO-FAKT-LEER).
        try:
            response = model_service.background.submit_sync(BackgroundRequest(
                messages          = [{"role": "user", "content": user_prompt}],
                modus             = "sprache",
                system            = system_prompt,
                temperature       = node_cfg.get("temperature", 0.1),
                expect_json       = True,
                max_output_tokens = node_cfg.get("max_output_tokens"),
                caller            = "pixie/promotion/call2",
            ))
            return response.parsed
        except json.JSONDecodeError as fehler:
            logger.error(f"Promotion Call 2: Ungueltiges JSON: {fehler}")
            return {"fakten": []}

    # ─────────────────────────────────────────
    # Nachbearbeitung
    # ─────────────────────────────────────────
    @staticmethod
    def _call1_nachbearbeiten(
        ergebnis:   dict,
        user_name:  str,
        user_id_db: int | None,
        bekannte:   list[dict],
    ) -> dict:
        """Nachbearbeitung Call 1: User-Entitaet, bekannte_id Lookup."""

        entitaeten: list[dict] = ergebnis.get("entitaeten", [])

        # User als erste Entitaet sicherstellen
        user_vorhanden: bool = any(
            e.get("bekannte_id") == user_id_db
            or (e.get("name") or "").lower() == user_name.lower()
            for e in entitaeten
        )

        if not user_vorhanden and user_id_db is not None:
            entitaeten.insert(0, {
                "name": user_name,
                "typ": "person",
                "ist_referenz": True,
                "bekannte_id": user_id_db,
            })

        # bekannte_id nachschlagen
        for ent in entitaeten:
            ent_name: str = (ent.get("name") or "").lower()

            if ent_name in ("nutzer", "der nutzer", "user", "der user"):
                logger.warning(
                    f"Promotion: LLM liefert '{ent.get('name')}' statt User-Name. "
                    f"O5-Speaker-Fix greift moeglicherweise nicht."
                )

            if ent.get("bekannte_id") is None and ent.get("ist_referenz"):
                for bek in bekannte:
                    if (bek.get("name") or "").lower() == (ent.get("name") or "").lower():
                        ent["bekannte_id"] = bek["id"]
                        break

        ergebnis["entitaeten"] = entitaeten
        return ergebnis

    @staticmethod
    def _call2_nachbearbeiten(
        ergebnis:              dict,
        entitaeten:            list[dict],
        user_name:             str,
        bekannte_entitaeten:   list[dict] | None = None,
    ) -> dict:
        """Nachbearbeitung Call 2: Ich-Ersetzung, objekt_wert/id, Tautologie-Filter."""

        fakten: list[dict] = ergebnis.get("fakten", [])

        # User-Entitaet aus Entitaeten-Liste finden
        user_ent_id: int | None = None
        for ent in entitaeten:
            if (ent.get("name") or "").lower() == user_name.lower():
                user_ent_id = ent.get("bekannte_id")
                break

        for fakt in fakten:
            subjekt_name: str = fakt.get("subjekt") or ""
            if subjekt_name.lower() in ("nutzer", "der nutzer", "user", "der user"):
                logger.warning(
                    f"Promotion: LLM liefert '{subjekt_name}' statt User-Name. "
                    f"O5-Speaker-Fix greift moeglicherweise nicht."
                )

            # "Ich" im fakt_text ersetzen
            fakt_text: str = fakt.get("fakt_text") or ""
            if fakt_text.startswith("Ich "):
                fakt_text = user_name + fakt_text[3:]
            fakt_text = fakt_text.replace(" ich ", f" {user_name} ")
            fakt["fakt_text"] = fakt_text

            # subjekt_id: nicht-numerische Werte zuruecksetzen
            if isinstance(fakt.get("subjekt_id"), str):
                fakt["subjekt_id"] = None

            # subjekt_id nachschlagen
            if fakt.get("subjekt_id") is None:
                s_name: str = fakt.get("subjekt") or ""
                for ent in entitaeten:
                    if (ent.get("name") or "").lower() == s_name.lower():
                        fakt["subjekt_id"] = ent.get("bekannte_id")
                        break

            # objekt_id oder objekt_wert nachsetzen
            raw_objekt_id = fakt.get("objekt_id")
            if isinstance(raw_objekt_id, str):
                fakt["objekt_id"] = None

            if fakt.get("objekt_id") is None and fakt.get("objekt_wert") is None:
                objekt_name: str = fakt.get("objekt") or ""
                matched: bool = False
                for ent in entitaeten:
                    if (ent.get("name") or "").lower() == objekt_name.lower():
                        if ent.get("ist_referenz") and ent.get("bekannte_id"):
                            fakt["objekt_id"] = ent["bekannte_id"]
                        else:
                            fakt["objekt_wert"] = objekt_name
                        matched = True
                        break
                if not matched and objekt_name:
                    fakt["objekt_wert"] = objekt_name

        # Finaler Check: objekt_wert gegen bekannte DB-Entitaeten
        if bekannte_entitaeten:
            for fakt in fakten:
                if fakt.get("objekt_wert") and not fakt.get("objekt_id"):
                    obj_name: str = fakt["objekt_wert"]
                    for bek in bekannte_entitaeten:
                        if (bek.get("name") or "").lower() == obj_name.lower() and bek.get("id"):
                            logger.info(
                                f"Promotion: objekt_wert '{obj_name}' "
                                f"-> objekt_id {bek['id']} korrigiert"
                            )
                            fakt["objekt_id"] = bek["id"]
                            fakt["objekt_wert"] = None
                            break

        # Tautologische Fakten filtern
        def _ist_tautologisch(f: dict) -> bool:
            attribut: str = (f.get("attribut") or "").lower().replace("_", " ").replace("hat ", "")
            objekt: str = (f.get("objekt_wert") or f.get("objekt") or "").lower()
            if not attribut or not objekt:
                return False
            return objekt in attribut or attribut in objekt

        for f in fakten:
            if _ist_tautologisch(f):
                logger.info(f"Promotion: Tautologischer Fakt gefiltert: {f.get('fakt_text', '')}")

        fakten = [
            f for f in fakten
            if f.get("subjekt") and f.get("attribut") and f.get("fakt_text")
            and (f.get("objekt_id") is not None or f.get("objekt_wert") is not None)
            and not _ist_tautologisch(f)
        ]

        ergebnis["fakten"] = fakten
        return ergebnis

    # ─────────────────────────────────────────
    # Cluster-Promotion
    # ─────────────────────────────────────────

    def _cluster_promotion(self, user_id: str, character_id: str) -> int:
        """4-Phasen Cluster-Promotion: Rein Embedding-basiert mit Mehrfachzuordnung.

        Phase 1: Zentren finden (Greedy)
        Phase 2: Jeden Eintrag allen passenden Zentren zuordnen (Mehrfachzuordnung)
        Phase 3: Cluster >= 3 destillieren mit Kohaerenzpruefung
        Phase 4: Promovierte KZG-Eintraege loeschen

        Returns:
            Anzahl promoteter Cluster.
        """
        if user_id == ASSISTANT_USER_ID:
            logger.debug("Cluster-Promotion: Nova-Guard — uebersprungen")
            return 0

        eintraege: list[dict] = self._kzg_partition_laden(user_id, character_id)

        if len(eintraege) < CLUSTER_MIN_EINTRAEGE:
            logger.debug(
                f"Cluster-Promotion: Nur {len(eintraege)} Eintraege "
                f"fuer {user_id}:{character_id} — zu wenig"
            )
            return 0

        # --- Phase 1: Zentren finden ---
        zentren: list[int] = self._zentren_finden(eintraege)

        logger.info(
            f"Cluster-Promotion Phase 1: {len(eintraege)} Eintraege "
            f"→ {len(zentren)} Zentren"
        )

        # --- Phase 2: Mehrfachzuordnung ---
        cluster_map: dict[int, list[dict]] = self._mehrfach_zuordnen(
            eintraege, zentren,
        )

        # --- Phase 3: Promotion mit Kohaerenzpruefung ---
        promotet: int = 0
        promovierte_keys: set[str] = set()

        # 3a: Cluster mit >= 3 Mitgliedern → Destillation
        for zentrum_idx, mitglieder in cluster_map.items():
            if len(mitglieder) < CLUSTER_MIN_EINTRAEGE:
                continue

            zentrum_text: str = eintraege[zentrum_idx]["inhalt"][:50]
            logger.info(
                f"Cluster-Promotion Phase 3: Cluster '{zentrum_text}...' "
                f"mit {len(mitglieder)} Eintraegen → Destillation"
            )

            lzg_treffer: dict | None = self._lzg_thema_suchen(
                user_id, character_id,
                eintraege[zentrum_idx]["inhalt"],
                mitglieder,
            )

            if lzg_treffer:
                ergebnis: dict = self._cluster_update_kohaerenz(
                    user_id, character_id,
                    mitglieder, lzg_treffer,
                )
            else:
                ergebnis = self._cluster_insert_kohaerenz(
                    user_id, character_id, mitglieder,
                )

            kohaerenz: str = ergebnis.get("kohaerenz", "nein")
            ausreisser_texte: list[str] = ergebnis.get("ausreisser", [])

            if kohaerenz == "nein":
                logger.info(
                    f"Cluster-Promotion: Kohaerenzpruefung gescheitert "
                    f"fuer Cluster '{zentrum_text}...' — kein Destillat"
                )
                continue

            ausreisser_set: set[str] = set(ausreisser_texte)
            for eintrag in mitglieder:
                if eintrag["inhalt"] not in ausreisser_set:
                    promovierte_keys.add(eintrag["key"])

            promotet += 1

        # 3b: Einzelgaenger und Zweier → LZG-Magnetismus
        for zentrum_idx, mitglieder in cluster_map.items():
            if len(mitglieder) >= CLUSTER_MIN_EINTRAEGE:
                continue

            verbleibend: list[dict] = [
                e for e in mitglieder if e["key"] not in promovierte_keys
            ]
            if not verbleibend:
                continue

            lzg_treffer = self._lzg_thema_suchen(
                user_id, character_id,
                verbleibend[0]["inhalt"],
                verbleibend,
            )

            if lzg_treffer:
                logger.info(
                    f"Cluster-Promotion: LZG-Magnetismus — "
                    f"{len(verbleibend)} Einzelgaenger docken an "
                    f"LZG #{lzg_treffer['id']} an"
                )
                ergebnis = self._cluster_update_kohaerenz(
                    user_id, character_id,
                    verbleibend, lzg_treffer,
                )
                if ergebnis.get("kohaerenz") == "nein":
                    logger.debug(
                        f"Cluster-Promotion: Magnetismus abgelehnt — "
                        f"Kohaerenz 'nein'"
                    )
                    continue
                for eintrag in verbleibend:
                    promovierte_keys.add(eintrag["key"])
                promotet += 1

        # --- Phase 4: Aufraeumen ---
        if promovierte_keys:
            for key in promovierte_keys:
                redis_client.delete(key)
                logger.debug(f"Cluster-Promotion: KZG {key} geloescht")

            if PIXIE_AKTIV:
                redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")
            else:
                logger.debug("promotion: hash_dirty-Setzer uebersprungen (PIXIE_AKTIV=False)")
            logger.info(
                f"Cluster-Promotion Phase 4: {len(promovierte_keys)} "
                f"KZG-Eintraege geloescht, {promotet} Cluster promotet"
            )

        return promotet

    @staticmethod
    def _kzg_partition_laden(user_id: str, character_id: str) -> list[dict]:
        """Laedt alle KZG-Eintraege einer Paar-Partition aus Redis.

        Inkludiert die sieben EI-Felder (emotion, arousal, modus, sprach_stil,
        tone, beziehungs_dynamik, intentionen) fuer die Cluster-Aggregation
        in `_lzg_eintrag_schreiben`. emotions_vektor wird bewusst nicht
        geladen — das Feld existiert im LZG-Schema nicht mehr.
        """

        keys: list = redis_client.keys(_kzg_prefix(user_id, character_id))
        eintraege: list[dict] = []

        for key in keys:
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            try:
                inhalt:      str = redis_client.hget(key, "inhalt") or ""
                themen_raw:  str = redis_client.hget(key, "themen") or ""
                salienz_raw: str = redis_client.hget(key, "salienz") or "0.0"
                beobachter:  str = redis_client.hget(key, "beobachter") or "user"
                dimension:   str = redis_client.hget(key, "dimension") or "kontext"

                emotion:            str = redis_client.hget(key, "emotion") or ""
                modus:              str = redis_client.hget(key, "modus") or ""
                sprach_stil:        str = redis_client.hget(key, "sprach_stil") or ""
                tone:               str = redis_client.hget(key, "tone") or ""
                beziehungs_dynamik: str = redis_client.hget(key, "beziehungs_dynamik") or ""

                arousal_raw: str = redis_client.hget(key, "arousal") or ""
                try:
                    arousal: float | None = float(arousal_raw) if arousal_raw else None
                except ValueError:
                    arousal = None

                intentionen_raw: str = redis_client.hget(key, "intentionen") or "[]"
                try:
                    intentionen: list = json.loads(intentionen_raw)
                    if not isinstance(intentionen, list):
                        intentionen = []
                except (json.JSONDecodeError, TypeError):
                    intentionen = []

                themen: list[str] = [t.strip() for t in themen_raw.split(",") if t.strip()]

                erstellt_am_raw: str = redis_client.hget(key, "erstellt_am") or ""
                kzg_erstellt_am: datetime | None
                try:
                    kzg_erstellt_am = (
                        datetime.fromtimestamp(float(erstellt_am_raw), tz=timezone.utc)
                        if erstellt_am_raw else None
                    )
                except ValueError:
                    kzg_erstellt_am = None

                # Embedding frisch erzeugen — Redis-Blob ist durch decode_responses=True korrumpiert
                embed_response = model_service.embed.submit_sync(
                    EmbedRequest(text=inhalt)
                )
                entry_embedding: list[float] = embed_response.embedding
                logger.debug(
                    "Promotion: KZG-Re-Embedding Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                    len(entry_embedding),
                    embed_response.duration_seconds,
                )

                eintrag: dict = {
                    "key":                key,
                    "inhalt":             inhalt,
                    "themen":             themen,
                    "kzg_erstellt_am":    kzg_erstellt_am,
                    "salienz":            float(salienz_raw),
                    "beobachter":         beobachter,
                    "dimension":          dimension,
                    "embedding":          entry_embedding,
                    "emotion":            emotion,
                    "modus":              modus,
                    "sprach_stil":        sprach_stil,
                    "tone":               tone,
                    "beziehungs_dynamik": beziehungs_dynamik,
                    "arousal":            arousal,
                    "intentionen":        intentionen,
                }
                eintraege.append(eintrag)

                logger.debug(
                    f"Cluster-Promotion: KZG {key} geladen — "
                    f"emotion='{emotion}', modus='{modus}', arousal={arousal}, "
                    f"sprach_stil='{sprach_stil}', tone='{tone}', "
                    f"beziehungs_dynamik='{beziehungs_dynamik}', "
                    f"intentionen={len(intentionen)}"
                )
            except Exception as ex:
                logger.warning(f"Cluster-Promotion: Fehler bei Key {key}: {ex}")

        logger.info(
            f"Cluster-Promotion: {len(eintraege)} KZG-Eintraege "
            f"geladen fuer {user_id}:{character_id}"
        )
        return eintraege

    def _zentren_finden(self, eintraege: list[dict]) -> list[int]:
        """Phase 1: Identifiziert Cluster-Zentren per Greedy.

        Ein Eintrag wird Zentrum, wenn sein Embedding zu KEINEM bisherigen
        Zentrum Cosine >= CLUSTER_THEMEN_SIMILARITY hat.

        Aeltere Eintraege werden zuerst verarbeitet → stabile Zentren.

        Returns:
            Liste von Indizes in eintraege[].
        """
        zentren: list[int] = []
        zentren_embs: list[np.ndarray] = []

        for i, eintrag in enumerate(eintraege):
            emb_i: np.ndarray = np.array(eintrag["embedding"], dtype=np.float32)
            norm_i: float = float(np.linalg.norm(emb_i))
            if norm_i == 0:
                continue

            ist_zentrum: bool = True
            for z_emb in zentren_embs:
                similarity: float = float(
                    np.dot(emb_i, z_emb) / (norm_i * float(np.linalg.norm(z_emb)))
                )
                if similarity >= CLUSTER_THEMEN_SIMILARITY:
                    ist_zentrum = False
                    break

            if ist_zentrum:
                zentren.append(i)
                zentren_embs.append(emb_i)

        return zentren

    def _mehrfach_zuordnen(
        self,
        eintraege: list[dict],
        zentren:   list[int],
    ) -> dict[int, list[dict]]:
        """Phase 2: Ordnet jeden Eintrag ALLEN passenden Zentren zu.

        Ein Eintrag kann in 0, 1 oder N Clustern sein. Cosine >= threshold
        wird gegen jedes Zentrum geprueft.

        'Brokkoli mit Kaesesosse' kann sowohl in 'Vorlieben' als auch in
        'Lieblingsgerichte' landen — keine Information geht verloren.

        Returns:
            Dict: zentrum_index → Liste der zugeordneten Eintraege.
        """
        cluster_map: dict[int, list[dict]] = {z: [] for z in zentren}

        zentren_embs: list[tuple[int, np.ndarray, float]] = []
        for z_idx in zentren:
            z_emb: np.ndarray = np.array(eintraege[z_idx]["embedding"], dtype=np.float32)
            z_norm: float = float(np.linalg.norm(z_emb))
            zentren_embs.append((z_idx, z_emb, z_norm))

        zuordnungen: int = 0
        mehrfach: int = 0

        for eintrag in eintraege:
            emb_i: np.ndarray = np.array(eintrag["embedding"], dtype=np.float32)
            norm_i: float = float(np.linalg.norm(emb_i))
            if norm_i == 0:
                continue

            treffer: int = 0
            for z_idx, z_emb, z_norm in zentren_embs:
                if z_norm == 0:
                    continue
                similarity: float = float(np.dot(emb_i, z_emb) / (norm_i * z_norm))
                if similarity >= CLUSTER_THEMEN_SIMILARITY:
                    cluster_map[z_idx].append(eintrag)
                    treffer += 1

            if treffer > 1:
                mehrfach += 1
            zuordnungen += treffer

        logger.info(
            f"Cluster-Promotion Phase 2: {zuordnungen} Zuordnungen, "
            f"davon {mehrfach} Eintraege in mehreren Clustern"
        )

        return cluster_map

    @staticmethod
    def _lzg_thema_suchen(
        user_id:           str,
        character_id:      str,
        thema:             str,
        cluster_eintraege: list[dict],
    ) -> dict | None:
        """Sucht im LZG nach einem bestehenden Eintrag zum Cluster-Thema.

        Verwendet Embedding-Suche mit pgvector.
        Schwelle: CLUSTER_LZG_SIMILARITY (0.80, etwas lockerer als KZG,
        da LZG-Eintraege bereits destilliert und abstrakter sind).
        """
        embed_response = model_service.embed.submit_sync(EmbedRequest(text=thema))
        thema_embedding: list[float] = embed_response.embedding
        logger.debug(
            "Promotion: LZG-Thema-Suche Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(thema_embedding),
            embed_response.duration_seconds,
        )
        embedding_str: str = "[" + ",".join(str(x) for x in thema_embedding) + "]"

        try:
            row: dict | None = db_manager.select_one(
                """
                SELECT id, inhalt, gewicht, dimension, verstaerkt_am,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM langzeitgedaechtnis
                WHERE user_id = %s
                  AND character_id = %s
                  AND aktiv = TRUE
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT 1
                """,
                (embedding_str, user_id, character_id, embedding_str),
            )

            if row and row["similarity"] >= CLUSTER_LZG_SIMILARITY:
                logger.info(
                    f"Cluster-Promotion: LZG-Treffer "
                    f"(Similarity {row['similarity']:.2f}) → UPDATE"
                )
                return {
                    "id":            row["id"],
                    "inhalt":        row["inhalt"],
                    "gewicht":       row["gewicht"],
                    "dimension":     row["dimension"],
                    "verstaerkt_am": row["verstaerkt_am"],
                }

            logger.info(f"Cluster-Promotion: Kein LZG-Treffer fuer '{thema[:50]}' → INSERT")
            return None

        except Exception as ex:
            logger.error(f"Cluster-Promotion: LZG-Suche fehlgeschlagen: {ex}")
            return None

    def _cluster_update(
        self,
        user_id:           str,
        character_id:      str,
        thema:             str,
        cluster_eintraege: list[dict],
        lzg_treffer:       dict,
    ) -> None:
        """Aktualisiert bestehenden LZG-Eintrag mit neuen KZG-Daten.

        Backpropagation: Bestaetigung verstaerkt, Widerspruch schwaecht.
        Harmonisiert mit Ebbinghaus: verstaerkt_am und gewicht steuern den Decay.
        """
        neue_kerne: list[str] = [e["inhalt"] for e in cluster_eintraege]
        alter_text: str = lzg_treffer["inhalt"]

        ergebnis: dict = self._destillation_update(alter_text, neue_kerne, thema, user_id)

        zusammenfassung: str  = ergebnis.get("zusammenfassung", "")
        ist_widerspruch: bool = ergebnis.get("widerspruch", False)

        if not zusammenfassung:
            logger.warning(f"Cluster-Promotion: Leere Destillation fuer '{thema}' — uebersprungen")
            return

        embed_response = model_service.embed.submit_sync(
            EmbedRequest(text=zusammenfassung)
        )
        neues_embedding: list[float] = embed_response.embedding
        logger.debug(
            "Promotion: Cluster-Widerspruch Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(neues_embedding),
            embed_response.duration_seconds,
        )
        embedding_str: str = "[" + ",".join(str(x) for x in neues_embedding) + "]"

        if ist_widerspruch:
            logger.info(
                f"Cluster-Promotion: Widerspruch fuer '{thema}' — "
                f"Decay x{CLUSTER_WIDERSPRUCH_DECAY_FAKTOR}, neuer Eintrag"
            )
            db_manager.execute(
                """
                UPDATE langzeitgedaechtnis
                SET gewicht = gewicht / %s
                WHERE id = %s
                """,
                (CLUSTER_WIDERSPRUCH_DECAY_FAKTOR, lzg_treffer["id"]),
            )

            self._lzg_eintrag_schreiben(
                user_id, character_id, zusammenfassung, embedding_str,
                cluster_eintraege, thema,
            )
        else:
            logger.info(
                f"Cluster-Promotion: Bestaetigung fuer '{thema}' — "
                f"UPDATE + Gewicht +{CLUSTER_BESTAETIGUNG_BOOST}"
            )
            db_manager.execute(
                """
                UPDATE langzeitgedaechtnis
                SET inhalt = %s,
                    embedding = %s::vector,
                    gewicht = LEAST(gewicht + %s, 5.0),
                    verstaerkt_am = NOW()
                WHERE id = %s
                """,
                (zusammenfassung, embedding_str,
                 CLUSTER_BESTAETIGUNG_BOOST, lzg_treffer["id"]),
            )

    def _cluster_insert_kohaerenz(
        self,
        user_id:           str,
        character_id:      str,
        cluster_eintraege: list[dict],
    ) -> dict:
        """Destillation mit Kohaerenzpruefung fuer neue LZG-Eintraege.

        Der LLM prueft ob die Eintraege zusammengehoeren bevor er destilliert.

        Returns:
            {"kohaerenz": "ja|teilweise|nein",
             "zusammenfassung": "...",
             "ausreisser": ["Kern-Text", ...]}
        """
        kerne: list[str] = [e["inhalt"] for e in cluster_eintraege]
        kerne_formatiert: str = "\n".join(f"- {k}" for k in kerne)

        system_prompt: str = (
            "Du bist ein Gedaechtnissystem. "
            "Deine Aufgabe: Pruefe ob die folgenden Beobachtungen thematisch "
            "zusammengehoeren, und fasse die zusammengehoerigen zusammen.\n\n"
            "SCHRITT 1 — KOHAERENZ PRUEFEN:\n"
            "- 'ja': Alle Beobachtungen handeln vom selben Thema.\n"
            "- 'teilweise': Die meisten gehoeren zusammen, aber einzelne "
            "Ausreisser passen nicht.\n"
            "- 'nein': Die Beobachtungen sind zu verschieden fuer eine "
            "gemeinsame Zusammenfassung.\n\n"
            "SCHRITT 2 — ZUSAMMENFASSEN (nur bei 'ja' oder 'teilweise'):\n"
            "- Behalte ALLE konkreten Namen, Orte, Zahlen\n"
            "- Ein bis drei Saetze\n"
            f"- Dritte Person ('{user_id} mag...')\n"
            "- Bei 'teilweise': Nur die zusammengehoerigen zusammenfassen, "
            "Ausreisser im Feld 'ausreisser' auflisten (exakter Text).\n"
            "- Kein Kommentar, keine Einleitung\n\n"
            "ANTWORTFORMAT (JSON ohne Backticks):\n"
            '{"kohaerenz": "ja|teilweise|nein", '
            '"zusammenfassung": "...", '
            '"ausreisser": ["exakter Text des Ausreissers", ...]}'
        )

        user_prompt: str = f"Beobachtungen:\n{kerne_formatiert}"

        node_cfg = get_node_config("cluster_destillation")

        # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
        # _cluster_insert_kohaerenz() laeuft im PromotionAgent, sync invoke
        # via Pixie-asyncio.to_thread → submit_sync. modus="sprache"
        # (Routing-Beifund). expect_json=False (Brief-DEVIATION von TRUE):
        # _parse_kohaerenz_antwort enthaelt eine Recovery-Fallback-Logik,
        # die einen Nicht-JSON-Text in {"kohaerenz":"ja","zusammenfassung":
        # raw} hochstuft — das ist Promotion-Klassifikations-Logik (HARTE
        # GRENZE) und muss unangetastet bleiben. Daher Worker-Text-Pfad
        # + Helfer beibehalten.
        response = model_service.background.submit_sync(BackgroundRequest(
            messages          = [{"role": "user", "content": user_prompt}],
            modus             = "sprache",
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.1),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/promotion/cluster_insert_kohaerenz",
        ))

        ergebnis: dict = self._parse_kohaerenz_antwort(response.text)

        kohaerenz: str = ergebnis.get("kohaerenz", "nein")
        zusammenfassung: str = ergebnis.get("zusammenfassung", "")

        if kohaerenz == "nein" or not zusammenfassung:
            logger.info(
                f"Cluster-Promotion: Kohaerenz '{kohaerenz}' "
                f"— kein LZG-Eintrag"
            )
            return ergebnis

        embed_response = model_service.embed.submit_sync(
            EmbedRequest(text=zusammenfassung)
        )
        neues_embedding: list[float] = embed_response.embedding
        logger.debug(
            "Promotion: Cluster-Kohärenz Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(neues_embedding),
            embed_response.duration_seconds,
        )
        embedding_str: str = "[" + ",".join(str(x) for x in neues_embedding) + "]"

        ausreisser_set: set[str] = set(ergebnis.get("ausreisser", []))
        kohaerente_eintraege: list[dict] = [
            e for e in cluster_eintraege
            if e["inhalt"] not in ausreisser_set
        ]
        if not kohaerente_eintraege:
            kohaerente_eintraege = cluster_eintraege

        self._lzg_eintrag_schreiben(
            user_id, character_id, zusammenfassung, embedding_str,
            kohaerente_eintraege, zusammenfassung[:50],
        )

        logger.info(
            f"Cluster-Promotion: LZG INSERT — Kohaerenz '{kohaerenz}', "
            f"{len(kohaerente_eintraege)} Quellen, "
            f"{len(ausreisser_set)} Ausreisser zurueck ins KZG"
        )

        return ergebnis

    def _cluster_update_kohaerenz(
        self,
        user_id:           str,
        character_id:      str,
        cluster_eintraege: list[dict],
        lzg_treffer:       dict,
    ) -> dict:
        """Destillation mit Kohaerenzpruefung fuer LZG-Updates (Backpropagation).

        Returns:
            {"kohaerenz": "ja|teilweise|nein",
             "zusammenfassung": "...",
             "widerspruch": bool,
             "ausreisser": ["...", ...]}
        """
        kerne: list[str] = [e["inhalt"] for e in cluster_eintraege]
        kerne_formatiert: str = "\n".join(f"- {k}" for k in kerne)
        alter_text: str = lzg_treffer["inhalt"]

        system_prompt: str = (
            "Du bist ein Gedaechtnissystem. "
            "Deine Aufgabe: Pruefe ob neue Beobachtungen zu einer bestehenden "
            "Erinnerung passen, und aktualisiere sie.\n\n"
            "SCHRITT 1 — KOHAERENZ PRUEFEN:\n"
            "- 'ja': Alle neuen Beobachtungen passen zur bestehenden Erinnerung.\n"
            "- 'teilweise': Manche passen, manche sind Ausreisser.\n"
            "- 'nein': Die Beobachtungen haben nichts mit der Erinnerung zu tun.\n\n"
            "SCHRITT 2 — WIDERSPRUCH PRUEFEN:\n"
            "- Widersprechen die neuen Beobachtungen der bestehenden Erinnerung?\n\n"
            "SCHRITT 3 — ZUSAMMENFASSEN (nur bei 'ja' oder 'teilweise'):\n"
            "- Bei Widerspruch: Neue Aussage nur aus den neuen Beobachtungen.\n"
            "- Sonst: Bestehende Erinnerung und neue Beobachtungen vereinen.\n"
            "- Behalte ALLE konkreten Namen, Orte, Zahlen\n"
            "- Ein bis drei Saetze\n"
            f"- Dritte Person ('{user_id} mag...')\n"
            "- Kein Kommentar, keine Einleitung\n\n"
            "ANTWORTFORMAT (JSON ohne Backticks):\n"
            '{"kohaerenz": "ja|teilweise|nein", '
            '"widerspruch": true/false, '
            '"zusammenfassung": "...", '
            '"ausreisser": ["exakter Text", ...]}'
        )

        user_prompt: str = (
            f"Bestehende Erinnerung:\n\"{alter_text}\"\n\n"
            f"Neue Beobachtungen:\n{kerne_formatiert}"
        )

        node_cfg = get_node_config("cluster_destillation")

        # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
        # _cluster_update_kohaerenz(): analog _cluster_insert_kohaerenz.
        # expect_json=False (Brief-DEVIATION) zum Erhalt von
        # _parse_kohaerenz_antwort-Fallback (HARTE GRENZE).
        response = model_service.background.submit_sync(BackgroundRequest(
            messages          = [{"role": "user", "content": user_prompt}],
            modus             = "sprache",
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.1),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/promotion/cluster_update_kohaerenz",
        ))

        ergebnis: dict = self._parse_kohaerenz_antwort(response.text)

        kohaerenz: str = ergebnis.get("kohaerenz", "nein")
        zusammenfassung: str = ergebnis.get("zusammenfassung", "")
        ist_widerspruch: bool = ergebnis.get("widerspruch", False)

        if kohaerenz == "nein" or not zusammenfassung:
            return ergebnis

        embed_response = model_service.embed.submit_sync(
            EmbedRequest(text=zusammenfassung)
        )
        neues_embedding: list[float] = embed_response.embedding
        logger.debug(
            "Promotion: Cluster-generisch Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(neues_embedding),
            embed_response.duration_seconds,
        )
        embedding_str: str = "[" + ",".join(str(x) for x in neues_embedding) + "]"

        if ist_widerspruch:
            logger.info(
                f"Cluster-Promotion: Widerspruch — "
                f"Decay x{CLUSTER_WIDERSPRUCH_DECAY_FAKTOR}, neuer Eintrag"
            )
            db_manager.execute(
                """
                UPDATE langzeitgedaechtnis
                SET gewicht = gewicht / %s,
                    verstaerkt_am = NOW()
                WHERE id = %s
                """,
                (CLUSTER_WIDERSPRUCH_DECAY_FAKTOR, lzg_treffer["id"]),
            )

            ausreisser_set: set[str] = set(ergebnis.get("ausreisser", []))
            kohaerente: list[dict] = [
                e for e in cluster_eintraege
                if e["inhalt"] not in ausreisser_set
            ] or cluster_eintraege

            self._lzg_eintrag_schreiben(
                user_id, character_id, zusammenfassung, embedding_str,
                kohaerente, zusammenfassung[:50],
            )
        else:
            logger.info(
                f"Cluster-Promotion: Bestaetigung — "
                f"UPDATE + Gewicht +{CLUSTER_BESTAETIGUNG_BOOST}"
            )
            db_manager.execute(
                """
                UPDATE langzeitgedaechtnis
                SET inhalt = %s,
                    embedding = %s::vector,
                    gewicht = LEAST(gewicht + %s, 5.0),
                    verstaerkt_am = NOW()
                WHERE id = %s
                """,
                (zusammenfassung, embedding_str,
                 CLUSTER_BESTAETIGUNG_BOOST, lzg_treffer["id"]),
            )

        return ergebnis

    def _parse_kohaerenz_antwort(self, raw_content: str) -> dict:
        """Parst die JSON-Antwort des Kohaerenz-LLM-Calls.

        Robustes Parsing mit Backtick-Cleanup und Fallbacks.
        """
        raw: str = raw_content.strip()

        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                f"Cluster-Promotion: Ungueltiges Kohaerenz-JSON: {raw[:200]}"
            )
            if raw and len(raw) > 10:
                return {
                    "kohaerenz": "ja",
                    "zusammenfassung": raw,
                    "ausreisser": [],
                }
            return {"kohaerenz": "nein", "zusammenfassung": "", "ausreisser": []}

    @staticmethod
    def _lzg_eintrag_schreiben(
        user_id:           str,
        character_id:      str,
        zusammenfassung:   str,
        embedding_str:     str,
        cluster_eintraege: list[dict],
        thema:             str,
    ) -> None:
        """Schreibt einen neuen LZG-Eintrag (gleiches INSERT wie Einzelpromotion).

        Aggregation der EI-Felder aus den Cluster-Quellen:
          - emotion / modus / sprach_stil / tone / beziehungs_dynamik:
            Counter-Mehrheit, leere Strings und None vorher gefiltert.
            Tie-Break ueber Counter.most_common(1) (Insertion-Order).
          - arousal: Mittelwert aller nicht-None-Werte, Fallback 0.5.
          - intentionen: Mengen-Vereinigung aller Listen, leere Listen ignoriert.
        """

        beobachter_counts = Counter(e["beobachter"] for e in cluster_eintraege)
        beobachter: str = beobachter_counts.most_common(1)[0][0]

        avg_salienz: float = sum(e["salienz"] for e in cluster_eintraege) / len(cluster_eintraege)

        dim_counts = Counter(e["dimension"] for e in cluster_eintraege)
        dimension: str = dim_counts.most_common(1)[0][0]

        def _mehrheit(feld: str) -> str:
            werte = [e.get(feld) for e in cluster_eintraege]
            werte = [w for w in werte if w]  # None und "" ausfiltern
            if not werte:
                return ""
            return Counter(werte).most_common(1)[0][0]

        emotion:            str = _mehrheit("emotion")
        modus:              str = _mehrheit("modus")
        sprach_stil:        str = _mehrheit("sprach_stil")
        tone:               str = _mehrheit("tone")
        beziehungs_dynamik: str = _mehrheit("beziehungs_dynamik")

        arousal_werte: list[float] = [
            e.get("arousal") for e in cluster_eintraege
            if e.get("arousal") is not None
        ]
        arousal: float = (
            sum(arousal_werte) / len(arousal_werte) if arousal_werte else 0.5
        )

        intentionen_set: set[str] = set()
        for e in cluster_eintraege:
            werte = e.get("intentionen") or []
            for v in werte:
                if v:
                    intentionen_set.add(v)
        intentionen_str: str = json.dumps(sorted(intentionen_set))

        themen_vereinigt: list[str] = sorted({
            t for e in cluster_eintraege for t in (e.get("themen") or [])
        })

        kzg_zeiten: list[datetime] = [
            e["kzg_erstellt_am"] for e in cluster_eintraege
            if e.get("kzg_erstellt_am")
        ]
        kzg_erstellt_am_min: datetime | None = min(kzg_zeiten) if kzg_zeiten else None

        logger.info(
            f"Cluster-Promotion: Aggregation fuer '{thema[:40]}' "
            f"(Cluster-Groesse {len(cluster_eintraege)}) — "
            f"emotion='{emotion}', modus='{modus}', arousal={arousal:.3f}, "
            f"sprach_stil='{sprach_stil}', tone='{tone}', "
            f"beziehungs_dynamik='{beziehungs_dynamik}', "
            f"intentionen={len(intentionen_set)}"
        )
        logger.info(
            f"M3 Cluster-Promotion: {len(cluster_eintraege)} Mitglieder, "
            f"themen={len(themen_vereinigt)} Tags (vereinigt), "
            f"kzg_erstellt_am={kzg_erstellt_am_min} (frühestes)"
        )

        db_manager.execute(
            """
            INSERT INTO langzeitgedaechtnis
                (user_id, character_id, beobachter,
                 dimension, inhalt, gewicht, haeufigkeit,
                 embedding,
                 intentionen, emotion, modus,
                 arousal,
                 sprach_stil, beziehungs_dynamik, tone,
                 themen, kzg_erstellt_am,
                 verstaerkt_am)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s::vector,
                 %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (user_id, character_id, beobachter,
             dimension, zusammenfassung, min(avg_salienz, 1.0),
             len(cluster_eintraege),
             embedding_str,
             intentionen_str, emotion, modus,
             arousal,
             sprach_stil, beziehungs_dynamik, tone,
             themen_vereinigt, kzg_erstellt_am_min),
        )

    # ─────────────────────────────────────────
    # LLM-Calls fuer Cluster-Destillation
    # ─────────────────────────────────────────

    @staticmethod
    def _destillation_insert(kerne: list[str], thema: str, user_id: str) -> str:
        """LLM-Call: Destilliert mehrere KZG-Kerne zu einer LZG-Zusammenfassung."""

        kerne_formatiert: str = "\n".join(f"- {k}" for k in kerne)

        system_prompt: str = (
            "Du bist ein Gedaechtnissystem. "
            "Deine Aufgabe: Mehrere Einzelbeobachtungen zu einer praezisen "
            "Zusammenfassung verdichten.\n\n"
            "REGELN:\n"
            "- Behalte ALLE konkreten Namen, Orte, Zahlen, Beziehungen\n"
            "- Entferne Redundanzen — dreimal dasselbe reicht einmal\n"
            "- Ein bis drei Saetze\n"
            f"- Schreibe in der dritten Person ('{user_id} mag...', "
            f"'{user_id} hat...')\n"
            "- Kein Kommentar, keine Einleitung, nur die Zusammenfassung"
        )

        user_prompt: str = (
            f"Thema: {thema}\n\n"
            f"Beobachtungen:\n{kerne_formatiert}"
        )

        node_cfg = get_node_config("cluster_destillation")

        # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
        # _destillation_insert(): Sync Pixie-Pfad via asyncio.to_thread →
        # submit_sync. modus="sprache" (Routing-Beifund). expect_json=False
        # (Brief), liefert reine Zusammenfassung als Fliesstext.
        response = model_service.background.submit_sync(BackgroundRequest(
            messages          = [{"role": "user", "content": user_prompt}],
            modus             = "sprache",
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.1),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/promotion/cluster_insert",
        ))

        return response.text.strip()

    @staticmethod
    def _destillation_update(
        alter_text: str, kerne: list[str], thema: str, user_id: str,
    ) -> dict:
        """LLM-Call: Gleicht neue Beobachtungen mit bestehender Erinnerung ab.

        Returns:
            {"zusammenfassung": str, "widerspruch": bool}
        """
        kerne_formatiert: str = "\n".join(f"- {k}" for k in kerne)

        system_prompt: str = (
            "Du bist ein Gedaechtnissystem. "
            "Deine Aufgabe: Eine bestehende Erinnerung mit neuen Beobachtungen "
            "abgleichen und aktualisieren.\n\n"
            "PRUEFE:\n"
            "1. Widersprechen die neuen Beobachtungen der bestehenden Erinnerung?\n"
            "2. Wenn NEIN: Fasse bestehende Erinnerung und neue Beobachtungen "
            "zu einer aktualisierten Gesamtaussage zusammen.\n"
            "3. Wenn JA: Schreibe eine neue Aussage nur aus den neuen Beobachtungen.\n\n"
            "REGELN:\n"
            "- Behalte ALLE konkreten Namen, Orte, Zahlen\n"
            "- Ein bis drei Saetze\n"
            f"- Dritte Person ('{user_id} mag...')\n"
            "- Kein Kommentar, keine Einleitung\n\n"
            "ANTWORTFORMAT (JSON ohne Backticks):\n"
            '{"zusammenfassung": "...", "widerspruch": true/false}'
        )

        user_prompt: str = (
            f"Thema: {thema}\n\n"
            f"Bestehende Erinnerung:\n\"{alter_text}\"\n\n"
            f"Neue Beobachtungen:\n{kerne_formatiert}"
        )

        node_cfg = get_node_config("cluster_destillation")

        # ── BackgroundWorker (Microservice-Welle Block 2 Phase 4, G5) ──
        # _destillation_update(): Sync Pixie-Pfad via asyncio.to_thread →
        # submit_sync. modus="sprache" (Routing-Beifund). expect_json=False
        # (Brief-DEVIATION von TRUE): der bestehende JSONDecodeError-
        # Fallback nutzt den raw-Text als zusammenfassung — das ist
        # Promotion-Schreiblogik (HARTE GRENZE), die unangetastet bleibt.
        # Daher Worker-Text-Pfad + inline Markdown-Strip + json.loads + try
        # beibehalten.
        response = model_service.background.submit_sync(BackgroundRequest(
            messages          = [{"role": "user", "content": user_prompt}],
            modus             = "sprache",
            system            = system_prompt,
            temperature       = node_cfg.get("temperature", 0.1),
            max_output_tokens = node_cfg.get("max_output_tokens"),
            caller            = "pixie/promotion/cluster_update",
        ))

        raw: str = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Cluster-Promotion: Ungueltiges JSON: {raw[:200]}")
            return {"zusammenfassung": raw, "widerspruch": False}
