"""PromotionAgent — KZG -> LZG Promotion mit Zwei-Call-Pattern.

Call 1: Klassifikation (Fakt/Erinnerung) + Entitaeten-Erkennung.
Call 2: Fakten-Extraktion als Tripel (nur bei Fakten).
4 Qualitaetsfilter: Speaker (O5), Interface (O6), Objekt (O11), Tautologie (O12).

Migriert aus: services/shadow_agent/tasks/lzg_promotion.py
Queue wird VOLLSTAENDIG abgearbeitet (KZG hat TTL!).
"""

import json
import logging

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    redis_client, POSTGRES_URL, get_node_config,
    PIXIE_PROMOTION_PRIORITAET, PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
)
from services.llm_provider import get_background_provider
from memory.repositories.entitaeten_repository import EntitaetenRepository
from tools.embedding_manager import embedding_manager
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

    def periodic_task(self) -> PeriodicTask:
        return PeriodicTask(
            name="promotion",
            priority=PIXIE_PROMOTION_PRIORITAET,
            interval=PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
            description="KZG -> LZG Promotion (Zwei-Call, Fakten-Extraktion)",
        )

    def build_graph(self):
        return None

    def invoke(self, state: AgentState) -> AgentState:
        """Arbeitet die Promotion-Queue komplett ab."""
        user_id: str = state["kontext"].get("context_user_id", "meister")
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

        state["ergebnis"] = {"promotet": promotet, "fehler": fehler}
        state["status"] = "abgeschlossen"
        return state

    # ─────────────────────────────────────────
    # Eintrag verarbeiten (aus altem execute())
    # ─────────────────────────────────────────
    def _eintrag_verarbeiten(self, auftrag: dict, user_id: str) -> None:
        """Verarbeitet einen einzelnen Queue-Eintrag."""

        kzg_key:   str   = auftrag.get("key", "")
        themen:    str   = auftrag.get("themen", "")
        salienz:   float = auftrag.get("salienz", 0.0)
        dimension: str   = auftrag.get("dimension", "kontext")

        if not kzg_key:
            logger.warning("Promotion: Kein KZG-Key im Queue-Eintrag — uebersprungen")
            return

        # KZG-Daten aus Redis lesen
        def _hget(field: str, default: str = "") -> str:
            val = redis_client.hget(kzg_key, field)
            if val is None:
                return default
            return val.decode("utf-8") if isinstance(val, bytes) else val

        inhalt:             str   = _hget("inhalt") or themen
        haeufigkeit:        int   = int(float(_hget("haeufigkeit", "1")))
        intentionen:        str   = _hget("intentionen", "[]")
        emotion:            str   = _hget("emotion")
        modus:              str   = _hget("modus")
        arousal:            float = float(_hget("arousal", "0.5"))
        emotions_vektor:    str   = _hget("emotions_vektor")
        sprach_stil:        str   = _hget("sprach_stil")
        beziehungs_dynamik: str   = _hget("beziehungs_dynamik")
        tone:               str   = _hget("tone")

        if not inhalt:
            logger.warning(f"Promotion: KZG-Key '{kzg_key}' nicht mehr vorhanden — uebersprungen")
            return

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
        if klassifikation in ("fakt", "gemischt"):
            call2_ergebnis: dict = self._extrahiere_fakten(
                inhalt=inhalt, entitaeten=entitaeten,
                user_name=user_name, user_id_db=user_id_db,
            )
            call2_ergebnis = self._call2_nachbearbeiten(
                call2_ergebnis, entitaeten, user_name, bekannte,
            )

            extrahierte_fakten: list[dict] = call2_ergebnis.get("fakten", [])
            logger.info(f"Promotion Call 2: {len(extrahierte_fakten)} Fakten extrahiert")

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
                        embed_client=embedding_manager._client,
                        embed_model=embedding_manager._model,
                    )
                except Exception as ex:
                    logger.error(f"Promotion: Fehler bei Fakten-Verarbeitung: {ex}", exc_info=True)

        # ── 3. Erinnerung ins LZG (bei erinnerung/gemischt) ──────
        if klassifikation in ("erinnerung", "gemischt"):
            entitaets_tags: list[str] = [
                e["name"] for e in entitaeten if e.get("ist_referenz", False)
            ]

            embedding: list[float] = embedding_manager.embed(f"{themen} {inhalt}")
            embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"

            db_manager.execute(
                """
                INSERT INTO langzeitgedaechtnis
                    (user_id, dimension, inhalt, gewicht, haeufigkeit,
                     embedding, intentionen, emotion, modus,
                     arousal, emotions_vektor,
                     sprach_stil, beziehungs_dynamik, tone,
                     verstaerkt_am)
                VALUES
                    (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s,
                     %s, %s, %s, NOW())
                """,
                (user_id, dimension, inhalt, min(salienz, 1.0), haeufigkeit,
                 embedding_str, intentionen, emotion, modus,
                 arousal, emotions_vektor,
                 sprach_stil, beziehungs_dynamik, tone),
            )

            redis_client.set(f"hash_dirty:{user_id}", "1")

            logger.info(
                f"Promotion: '{themen}' -> LZG als Erinnerung "
                f"(tags: {entitaets_tags})"
            )

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
        provider = get_background_provider()
        antwort  = provider.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=node_cfg.get("temperature", 0.1),
            max_output_tokens=node_cfg.get("max_output_tokens"),
            caller="pixie/promotion/call1",
        )

        raw: str = antwort.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Promotion Call 1: Ungueltiges JSON: {raw[:200]}")
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
        provider = get_background_provider()
        antwort  = provider.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=node_cfg.get("temperature", 0.1),
            max_output_tokens=node_cfg.get("max_output_tokens"),
            caller="pixie/promotion/call2",
        )

        raw: str = antwort.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Promotion Call 2: Ungueltiges JSON: {raw[:200]}")
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
