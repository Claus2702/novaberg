"""
Task: KZG-Einträge ins Langzeitgedächtnis überführen.

Neuer Flow (M7):
1. Call 1: Klassifikation (Fakt/Erinnerung) + Entitäten-Erkennung
2. Call 2: Fakten-Extraktion als Tripel (nur bei Fakten)
3. Dispatch: Fakten → FaktenManager, Erinnerungen → LZG (nie überschrieben)
"""

import json
import logging
import threading

import psycopg2
import redis

from config                          import get_node_config
from services.shadow_agent.base_task import BaseTask
from services.llm_provider           import get_background_provider
from memory.repositories.entitaeten_repository import EntitaetenRepository

logger = logging.getLogger("ki_server.shadow")


class LzgPromotionTask(BaseTask):
    """KZG-Einträge ins Langzeitgedächtnis überführen."""

    TASK_NAME    = "lzg_promotion"
    BESCHREIBUNG = "KZG-Einträge ins Langzeitgedächtnis überführen"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = True
    PRIORITAET   = 60
    INTENTIONEN  = []

    def execute(
        self,
        auftrag:        dict,
        redis_client:   redis.Redis,
        embed_client,
        embed_model:    str,
        postgres_url:   str,
        user_id:        str,
        shutdown_event: threading.Event | None = None,
    ) -> dict | None:

        kzg_key:   str   = auftrag.get("key", "")
        themen:    str   = auftrag.get("themen", "")
        salienz:   float = auftrag.get("salienz", 0.0)
        dimension: str   = auftrag.get("dimension", "kontext")

        if not kzg_key:
            logger.warning("Promotion: Kein KZG-Key im Queue-Eintrag — übersprungen")
            return None

        inhalt:          str   = redis_client.hget(kzg_key, "inhalt") or themen
        haeufigkeit:     int   = int(float(redis_client.hget(kzg_key, "haeufigkeit") or "1"))
        intentionen:     str   = redis_client.hget(kzg_key, "intentionen") or "[]"
        emotion:         str   = redis_client.hget(kzg_key, "emotion") or ""
        modus:           str   = redis_client.hget(kzg_key, "modus") or ""
        arousal:         float = float(redis_client.hget(kzg_key, "arousal") or "0.5")
        emotions_vektor:    str = redis_client.hget(kzg_key, "emotions_vektor") or ""
        sprach_stil:        str = redis_client.hget(kzg_key, "sprach_stil") or ""
        beziehungs_dynamik: str = redis_client.hget(kzg_key, "beziehungs_dynamik") or ""
        tone:               str = redis_client.hget(kzg_key, "tone") or ""
        character_id:       str = redis_client.hget(kzg_key, "character_id") or ""

        if not inhalt:
            logger.warning(f"Promotion: KZG-Key '{kzg_key}' nicht mehr vorhanden — übersprungen")
            return None

        # ── 0. Bekannte Entitäten laden ──────
        bekannte: list[dict] = EntitaetenRepository.find_by_user(postgres_url, user_id)

        # User-Entität finden
        user_name:  str       = user_id  # Fallback
        user_id_db: int | None = None
        for bek in bekannte:
            if bek.get("typ") == "user" or (bek.get("name") or "").lower() == user_id.lower():
                user_name  = bek["name"]
                user_id_db = bek["id"]
                break

        # ── 1. Call 1: Klassifikation + Entitäten ──────
        if shutdown_event and shutdown_event.is_set():
            return None

        call1_ergebnis: dict = self._klassifiziere(
            themen=themen,
            inhalt=inhalt,
            bekannte_entitaeten=bekannte,
        )

        call1_ergebnis = self._call1_nachbearbeiten(
            call1_ergebnis, user_name, user_id_db, bekannte
        )

        klassifikation: str        = call1_ergebnis.get("klassifikation", "erinnerung")
        entitaeten:     list[dict] = call1_ergebnis.get("entitaeten", [])

        logger.info(
            f"Promotion Call 1: '{themen}' → {klassifikation}, "
            f"{len(entitaeten)} Entitäten"
        )

        # ── 2. Call 2: Fakten-Extraktion (nur bei fakt/gemischt) ──────
        if klassifikation in ("fakt", "gemischt"):
            if shutdown_event and shutdown_event.is_set():
                return None

            call2_ergebnis: dict = self._extrahiere_fakten(
                inhalt=inhalt,
                entitaeten=entitaeten,
                user_name=user_name,
                user_id_db=user_id_db,
            )

            call2_ergebnis = self._call2_nachbearbeiten(
                call2_ergebnis, entitaeten, user_name, bekannte
            )

            extrahierte_fakten: list[dict] = call2_ergebnis.get("fakten", [])

            logger.info(
                f"Promotion Call 2: {len(extrahierte_fakten)} Fakten extrahiert"
            )

            # Fakten über den FaktenManager verarbeiten
            if extrahierte_fakten:
                try:
                    from plugins.fakten_manager.manager import FaktenManager

                    fakten_manager = FaktenManager()
                    fakten_manager.fakten_verarbeiten(
                        aktion="create",
                        entitaeten=entitaeten,
                        fakten=extrahierte_fakten,
                        user_id=user_id,
                        postgres_url=postgres_url,
                        redis_client=redis_client,
                        embed_client=embed_client,
                        embed_model=embed_model,
                    )
                except Exception as ex:
                    logger.error(f"Promotion: Fehler bei Fakten-Verarbeitung: {ex}", exc_info=True)

        # ── 3. Erinnerung ins LZG (bei erinnerung/gemischt) ──────
        if klassifikation in ("erinnerung", "gemischt"):
            if shutdown_event and shutdown_event.is_set():
                return None

            entitaets_tags: list[str] = [
                e["name"] for e in entitaeten
                if e.get("ist_referenz", False)
            ]

            # Embedding erzeugen
            embed_response = embed_client.embeddings(
                model=embed_model,
                prompt=f"{themen} {inhalt}",
            )
            embedding:     list[float] = embed_response["embedding"]
            embedding_str: str         = "[" + ",".join(str(x) for x in embedding) + "]"

            # INSERT ins LZG — NIE UPDATE, NIE überschreiben
            conn   = psycopg2.connect(postgres_url)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO langzeitgedaechtnis
                    (user_id, dimension, inhalt, gewicht, haeufigkeit,
                     embedding, intentionen, emotion, modus,
                     arousal, emotions_vektor,
                     sprach_stil, beziehungs_dynamik, tone,
                     verstaerkt_am)
                VALUES
                    (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s, %s,
                     %s, %s, %s, NOW())
            """, (user_id, dimension, inhalt, min(salienz, 1.0), haeufigkeit,
                  embedding_str, intentionen, emotion, modus,
                  arousal, emotions_vektor,
                  sprach_stil, beziehungs_dynamik, tone))

            conn.commit()
            conn.close()

            # Charakter-Hash muss neu destilliert werden
            redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")

            logger.info(
                f"Promotion: '{themen}' → LZG als Erinnerung "
                f"(tags: {entitaets_tags})"
            )

        return None

    # ─────────────────────────────────────────
    # Call 1: Klassifikation + Entitäten
    # ─────────────────────────────────────────
    @staticmethod
    def _klassifiziere(
        themen:              str,
        inhalt:              str,
        bekannte_entitaeten: list[dict],
    ) -> dict:
        """
        Call 1: Klassifikation + Entitäten-Erkennung.

        Returns:
            dict mit klassifikation und entitaeten
        """
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
            bekannte_str: str = "Keine bekannten Entitäten"

        system_prompt: str = (
            "Du bist ein Wissensanalyst. Deine EINZIGE Aufgabe: "
            "Klassifiziere die Aussage und erkenne Entitäten.\n\n"
            "KLASSIFIKATION:\n"
            "- \"fakt\" = enthält überprüfbare, dauerhafte Informationen "
            "über Personen, Orte, Beziehungen, Eigenschaften, Vorlieben, Abneigungen\n"
            "- \"erinnerung\" = Erlebnis, Emotion, Meinung, temporärer Zustand "
            "(heute müde, gerade erkältet, bin sauer)\n"
            "- \"gemischt\" = enthält beides\n\n"
            "TEMPORÄRE ZUSTÄNDE sind IMMER \"erinnerung\". "
            "Signalwörter: heute, gerade, momentan, jetzt, im Moment.\n"
            "Vorlieben und Abneigungen (mag Kaffee, hasst Fisch) sind FAKTEN "
            "auch wenn das Objekt ein Interface ist.\n"
            "Emotionale Ausrufe ohne konkrete dauerhafte Informationen "
            "sind IMMER \"erinnerung\".\n\n"
            "SPEAKER: \"Ich\" = User (immer erste Entität, immer Referenz)\n\n"
            "ENTITÄTEN-TYPEN:\n"
            "- REFERENZ: Konkret, identifizierbar, hat einen EIGENNAMEN. "
            "Beispiele: Anna (Person), Nürnberg (Stadt), BMW (Firma), "
            "Der Goldene Drache (Restaurant), Max (Hund). "
            "→ Eine Referenz ist etwas, das man auf ein Namensschild schreiben könnte.\n"
            "- INTERFACE: Allgemein, kein Eigenname, ein Gattungsbegriff oder Konzept. "
            "Beispiele: Gehirn, Künstliche Intelligenz, Lernalgorithmen, Wohnung, "
            "Freunde, Kollegen, ein Restaurant, der Asiate, Kaffee, Fisch, "
            "Sushi, Astronomie, Physik, Wissenschaft, Forschung, Spazierengehen. "
            "→ Wenn man es nicht auf ein Namensschild schreiben würde, ist es ein Interface.\n\n"
            "WICHTIG: Wissenschaftliche Begriffe, Fachgebiete, abstrakte Konzepte, "
            "Organe, Aktivitäten und Lebensmittel sind IMMER Interfaces. "
            "Nur Eigennamen sind Referenzen.\n\n"
            "Extrahiere KEINE Fakten. Nur Klassifikation und Entitäten.\n"
            "Antworte in JSON ohne Markdown-Backticks."
        )

        user_prompt: str = (
            f"THEMEN: {themen}\n"
            f"INHALT: {inhalt}\n"
            f"BEKANNTE ENTITÄTEN: {bekannte_str}\n\n"
            "Format:\n"
            "{\"klassifikation\": \"fakt|erinnerung|gemischt\", "
            "\"entitaeten\": [{\"name\": \"\", \"typ\": \"person|ort|organisation|objekt\", "
            "\"ist_referenz\": true, \"bekannte_id\": null}]}"
        )

        node_cfg = get_node_config("lzg_promotion")
        provider = get_background_provider()
        antwort  = provider.chat(
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            system=system_prompt,
            temperature=node_cfg.get("temperature", 0.1),
            max_output_tokens=node_cfg.get("max_output_tokens"),
            caller="pixie/promotion/call1",
        )

        raw: str = antwort.content.strip()

        # Markdown-Backticks entfernen falls vorhanden
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            ergebnis: dict = json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Promotion Call 1: Ungültiges JSON: {raw[:200]}")
            ergebnis = {
                "klassifikation": "erinnerung",
                "entitaeten": [],
            }

        return ergebnis

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
        """
        Call 2: Fakten-Extraktion als Tripel.
        Wird nur aufgerufen wenn Call 1 fakt/gemischt liefert.

        Returns:
            dict mit fakten-Liste
        """
        ent_str: str = "\n".join(
            f"- {e['name']} (ID:{e.get('bekannte_id', 'neu')}, "
            f"{'Referenz' if e.get('ist_referenz') else 'Interface'}, {e.get('typ', '')})"
            for e in entitaeten
        )

        system_prompt: str = (
            "Du bist ein Fakten-Extraktor. Du bekommst einen Text und "
            "eine Liste aufgelöster Entitäten. Extrahiere alle Fakten als Tripel.\n\n"
            "REGELN:\n"
            "1. Subjekt ist IMMER eine Referenz-Entität aus der Liste\n"
            "2. Objekt ist entweder eine Referenz-Entität (Typ 1) oder "
            "ein Interface-Wert als String (Typ 2)\n"
            "3. Bei Referenz-Objekten: objekt_id setzen, objekt_wert=null\n"
            "4. Bei Interface-Objekten: objekt_id=null, objekt_wert=String\n"
            "5. Attribut in SCREAMING_SNAKE_CASE "
            "(WOHNORT, HAT_SCHWESTER, MAG_NICHT, ARBEITET_ALS)\n"
            "6. Fakt-Text muss eigenständig und kontextfrei sein\n"
            "7. Jeden Fakt genau EINMAL — keine Duplikate\n"
            "8. Negationen: \"mag keinen Fisch\" = MAG_NICHT, ist_negation=true\n"
            "9. temporal: \"permanent\" (Schwester sein), "
            "\"aktuell\" (wohnt in), \"vergangen\" (hat gewohnt in)\n"
            "10. Beziehungen vom User aus formulieren: "
            "\"Claus HAT_SCHWESTER Anna\" nicht \"Anna IST_SCHWESTER\"\n"
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
            f"AUFGELÖSTE ENTITÄTEN:\n{ent_str}\n\n"
            "Format:\n"
            "{\"fakten\": [{\"subjekt\": \"\", \"subjekt_id\": null, "
            "\"attribut\": \"SCREAMING_SNAKE_CASE\", \"objekt\": \"\", "
            "\"objekt_id\": null, \"objekt_wert\": null, "
            "\"fakt_text\": \"\", \"ist_negation\": false, "
            "\"temporal\": \"permanent|aktuell|vergangen\"}]}"
        )

        node_cfg = get_node_config("lzg_promotion")
        provider = get_background_provider()
        antwort  = provider.chat(
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            system=system_prompt,
            temperature=node_cfg.get("temperature", 0.1),
            max_output_tokens=node_cfg.get("max_output_tokens"),
            caller="pixie/promotion/call2",
        )

        raw: str = antwort.content.strip()

        # Markdown-Backticks entfernen
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            ergebnis: dict = json.loads(raw)
        except json.JSONDecodeError:
            logger.error(f"Promotion Call 2: Ungültiges JSON: {raw[:200]}")
            ergebnis = {"fakten": []}

        return ergebnis

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
        """
        Nachbearbeitung von Call 1:
        1. User als erste Entität einfügen falls fehlend
        2. "Ich" durch User-Namen ersetzen
        3. bekannte_id nachschlagen falls Name matcht aber ID fehlt
        """
        entitaeten: list[dict] = ergebnis.get("entitaeten", [])

        # User als erste Entität sicherstellen
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

        # bekannte_id nachschlagen, Warnung bei Alias-Resten
        for ent in entitaeten:
            ent_name: str = (ent.get("name") or "").lower()

            if ent_name in ("nutzer", "der nutzer", "user", "der user"):
                logger.warning(
                    f"Promotion: LLM liefert '{ent.get('name')}' statt User-Name. "
                    f"O5-Speaker-Fix greift möglicherweise nicht."
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
        """
        Nachbearbeitung von Call 2:
        1. "Ich" im fakt_text ersetzen
        2. objekt_wert setzen bei Interface-Objekten
        3. subjekt_id/objekt_id aus Entitäten-Liste nachschlagen
        4. Finaler Plausibilitäts-Check gegen DB-Entitäten
        5. Leere, ungültige und tautologische Fakten filtern
        """
        fakten: list[dict] = ergebnis.get("fakten", [])

        # User-Entität aus Entitäten-Liste finden (für ID)
        user_ent_id: int | None = None
        for ent in entitaeten:
            if (ent.get("name") or "").lower() == user_name.lower():
                user_ent_id = ent.get("bekannte_id")
                break

        for fakt in fakten:
            # Warnung bei Alias-Resten im Subjekt
            subjekt_name: str = fakt.get("subjekt") or ""
            if subjekt_name.lower() in ("nutzer", "der nutzer", "user", "der user"):
                logger.warning(
                    f"Promotion: LLM liefert '{subjekt_name}' statt User-Name. "
                    f"O5-Speaker-Fix greift möglicherweise nicht."
                )

            # "Ich" im fakt_text ersetzen (valides LLM-Muster)
            fakt_text: str = fakt.get("fakt_text") or ""
            if fakt_text.startswith("Ich "):
                fakt_text = user_name + fakt_text[3:]
            fakt_text = fakt_text.replace(" ich ", f" {user_name} ")
            fakt["fakt_text"] = fakt_text

            # subjekt_id: nicht-numerische Werte zurücksetzen
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

            # LLM hat "neu" oder einen nicht-numerischen Wert als ID geliefert → zurücksetzen
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
                # Nicht in Entitäten gefunden → Interface-Wert
                if not matched and objekt_name:
                    fakt["objekt_wert"] = objekt_name

        # Finaler Check: objekt_wert gegen bekannte DB-Entitäten abgleichen
        if bekannte_entitaeten:
            for fakt in fakten:
                if fakt.get("objekt_wert") and not fakt.get("objekt_id"):
                    obj_name: str = fakt["objekt_wert"]
                    for bek in bekannte_entitaeten:
                        if (bek.get("name") or "").lower() == obj_name.lower() and bek.get("id"):
                            logger.info(
                                f"Promotion: objekt_wert '{obj_name}' "
                                f"→ objekt_id {bek['id']} korrigiert"
                            )
                            fakt["objekt_id"] = bek["id"]
                            fakt["objekt_wert"] = None
                            break

        # Tautologische Fakten loggen + filtern
        def _ist_tautologisch(f: dict) -> bool:
            attribut: str = (f.get("attribut") or "").lower().replace("_", " ").replace("hat ", "")
            objekt: str = (f.get("objekt_wert") or f.get("objekt") or "").lower()
            if not attribut or not objekt:
                return False
            return objekt in attribut or attribut in objekt

        for f in fakten:
            if _ist_tautologisch(f):
                logger.info(f"Promotion: Tautologischer Fakt gefiltert: {f.get('fakt_text', '')}")

        # Ungültige + tautologische Fakten filtern
        fakten = [
            f for f in fakten
            if f.get("subjekt") and f.get("attribut") and f.get("fakt_text")
            and (f.get("objekt_id") is not None or f.get("objekt_wert") is not None)
            and not _ist_tautologisch(f)
        ]

        ergebnis["fakten"] = fakten
        return ergebnis
