"""Task: Charakter-Profile destillieren (Kern, Adaptiv, Intentionen, Emotionen, Beziehung)."""

import logging
import threading
import time

import psycopg2
import redis

from memory.lzg                      import effektives_gewicht_berechnen
from config                          import get_node_config, DEFAULT_USER_ID, ASSISTANT_USER_ID
from services.shadow_agent.base_task import BaseTask
from services.llm_provider           import get_background_provider

logger = logging.getLogger("ki_server.shadow")

# ─────────────────────────────────────────────
# Prompts für die 5 Profile
# ─────────────────────────────────────────────
KERN_HASH_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Erstelle aus den folgenden Langzeitgedächtnis-Einträgen ein kompaktes Persönlichkeitsprofil
des Nutzers in 2-5 Sätzen auf Deutsch.

Fokus: Tiefenwerte, dauerhafte Interessen, Kommunikationsstil, Denkweise.
Das Profil soll zeitlos sein — keine aktuellen Projekte oder Stimmungen.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

ADAPTIVE_HASH_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Erstelle aus den folgenden Kurzzeitgedächtnis-Einträgen ein kompaktes Profil
der AKTUELLEN Verfassung des Nutzers in 2-4 Sätzen auf Deutsch.

Die Einträge sind nach Zeitzone gewichtet:
- [AKUT] = letzte 24 Stunden (höchste Relevanz)
- [PHASE] = letzte 7 Tage (mittlere Relevanz)
- [TREND] = letzte 30 Tage (Hintergrund-Tendenz)

Fokus: Aktuelle Projekte, Stimmung, emotionale Lage, akute Themen.

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

INTENTIONS_PROFIL_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere die folgenden Einträge aus dem Langzeitgedächtnis
und erstelle ein kompaktes Kommunikations-Profil in 3-5 Sätzen auf Deutsch.

Drei Aspekte beschreiben:
- STIL: Wie formuliert der Nutzer? (Satzlänge, Formalität, Slang, Emojis, Zeichensetzung)
- MODUS: In welchem Register denkt er? (Fachgespräch, Philosophie, Alltag, ...)
- INTENTIONEN: Was will er typischerweise? (Fragen, Brainstorming, Feedback, ...)

Beschreibe den Menschen, nicht die Statistik.
Beispiel: "Der Nutzer kommuniziert sachlich-strukturiert mit vollständigen Sätzen.
Er bevorzugt Fachgespräche und philosophischen Austausch, stellt tiefe Fragen.
Sein Stil ist direkt, gelegentlich mit trockenem Humor. Kein Slang, keine Emojis."

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

EMOTIONS_PROFIL_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere die folgenden emotionalen Signale aus dem Langzeitgedächtnis
und erstelle ein kompaktes emotionales Profil in 3-5 Sätzen auf Deutsch.

Zwei Aspekte beschreiben:
- GRUNDTENDENZ: Welche Emotionen dominieren langfristig? Welche Muster gibt es?
- VOLATILITÄT: Wie sprunghaft ist der Nutzer emotional? Schnelle Umschwünge oder stabile Grundstimmung?
  Nutze die Emotions-Vektoren als Hinweis (häufig spirale/absturz = volatil, häufig plateau = stabil).

Beispiel stabil: "Grundlegend zuversichtlich-neugierig mit Begeisterungs-Peaks.
Emotional stabil — bei Belastung baut sich Frustration langsam auf statt zu explodieren."

Beispiel volatil: "Emotional lebhaft mit häufigen Richtungswechseln.
Schnelle Umschwünge zwischen Begeisterung und Frustration. Braucht bei Absturz schnelle Anerkennung."

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""

BEZIEHUNGS_PROFIL_PROMPT: str = """Du bist ein psychologischer Profilierungs-Agent.
Analysiere den folgenden Gesprächsverlauf und erstelle ein kompaktes
Beziehungsprofil in 2-3 Sätzen auf Deutsch.

Fokus: Wie steht der Nutzer zum Assistenten?
- Nähe: Vertraut oder formell? Duzt er, nutzt er Kosenamen, Emojis?
- Hierarchie: Gleichrangig oder direktiv? Gibt er Anweisungen oder diskutiert er?
- Vertrauen: Teilt er persönliche Details oder bleibt er sachlich?
- Ton: Warmherzig, humorvoll, sachlich, nüchtern?

Einträge:
{eintraege}

Antworte NUR mit dem Profil-Text, kein weiterer Kommentar."""


class CharakterHashTask(BaseTask):
    """Charakter-Profile destillieren (Kern, Adaptiv, Intentionen, Emotionen, Beziehung)."""

    TASK_NAME    = "charakter_hash"
    BESCHREIBUNG = "Charakter-Profile destillieren (Kern, Adaptiv, Intentionen, Emotionen, Beziehung)"
    BRAUCHT_LLM  = True
    BRAUCHT_DB   = True
    PRIORITAET   = 70
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

        ergebnis: dict = {
            "kern": "", "adaptiv": "",
            "intentions_profil": "", "emotions_profil": "", "beziehungsprofil": "",
        }

        # Paar-Schema (Chat 66): character_id aus user_id ableiten
        character_id: str = ASSISTANT_USER_ID if user_id == DEFAULT_USER_ID else DEFAULT_USER_ID

        # ── Kern-Hash aus LZG ────────────────────
        try:
            conn   = psycopg2.connect(postgres_url)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT dimension, inhalt, gewicht, haeufigkeit, verstaerkt_am
                FROM langzeitgedaechtnis
                WHERE user_id = %s AND aktiv = TRUE
                ORDER BY gewicht DESC, haeufigkeit DESC
                LIMIT 20
            """, (user_id,))

            lzg_rows = cursor.fetchall()
            conn.close()

            if lzg_rows:
                if shutdown_event and shutdown_event.is_set():
                    logger.info("Pixie-Task charakter_hash: Shutdown — breche ab")
                    return None

                eintraege: str = "\n".join(
                    f"[{dim}] (Gewicht: {effektives_gewicht_berechnen(gew, va):.2f}, Häufigkeit: {hfk}): {inh}"
                    for dim, inh, gew, hfk, va in lzg_rows
                )

                node_cfg = get_node_config("charakter_hash")
                provider = get_background_provider()
                antwort  = provider.chat(
                    messages = [{"role": "user", "content": KERN_HASH_PROMPT.format(eintraege=eintraege)}],
                    temperature       = node_cfg.get("temperature", 0.2),
                    max_output_tokens = node_cfg.get("max_output_tokens"),
                    caller            = "pixie/hash",
                )

                ergebnis["kern"] = antwort.content.strip()
                logger.info(f"Kern-Hash destilliert: '{ergebnis['kern'][:80]}...'")
            else:
                logger.info(f"Kern-Hash: Keine LZG-Einträge für user '{user_id}'")

        except Exception as fehler:
            logger.error(f"Kern-Hash Destillation fehlgeschlagen: {fehler}")

        # ── Adaptive-Hash aus KZG ────────────────
        try:
            kzg_keys: list = redis_client.keys(f"kzg:{user_id}:*")

            if kzg_keys:
                jetzt:           float      = time.time()
                zonen_eintraege: list[str]  = []

                for key in kzg_keys:
                    themen:   str   = redis_client.hget(key, "themen") or ""
                    inhalt:   str   = redis_client.hget(key, "inhalt") or ""
                    salienz:  float = float(redis_client.hget(key, "salienz") or "0")
                    erstellt: float = float(redis_client.hget(key, "erstellt_am") or "0")

                    if not themen:
                        continue

                    alter_sekunden: float = jetzt - erstellt
                    alter_tage:     float = alter_sekunden / 86400

                    if alter_tage <= 1:
                        zone:    str   = "AKUT"
                        gewicht: float = 1.0
                    elif alter_tage <= 7:
                        zone    = "PHASE"
                        gewicht = 0.8 - (0.6 * (alter_tage - 1) / 6)
                    elif alter_tage <= 30:
                        zone    = "TREND"
                        gewicht = 0.2 * (2.718 ** (-0.1 * (alter_tage - 7)))
                    else:
                        continue

                    effektive_salienz: float = salienz * gewicht

                    zonen_eintraege.append(
                        f"[{zone}] (Salienz: {effektive_salienz:.2f}) {themen}: {inhalt}"
                    )

                if zonen_eintraege:
                    if shutdown_event and shutdown_event.is_set():
                        logger.info("Pixie-Task charakter_hash: Shutdown — breche ab")
                        return None

                    eintraege: str = "\n".join(zonen_eintraege)

                    node_cfg = get_node_config("charakter_hash")
                    provider = get_background_provider()
                    antwort  = provider.chat(
                        messages = [{"role": "user", "content": ADAPTIVE_HASH_PROMPT.format(eintraege=eintraege)}],
                        temperature       = node_cfg.get("temperature", 0.2),
                        max_output_tokens = node_cfg.get("max_output_tokens"),
                        caller            = "pixie/hash",
                    )

                    ergebnis["adaptiv"] = antwort.content.strip()
                    logger.info(f"Adaptive-Hash destilliert: '{ergebnis['adaptiv'][:80]}...'")
                else:
                    logger.info(f"Adaptive-Hash: Keine relevanten KZG-Einträge für user '{user_id}'")
            else:
                logger.info(f"Adaptive-Hash: Keine KZG-Einträge für user '{user_id}'")

        except Exception as fehler:
            logger.error(f"Adaptive-Hash Destillation fehlgeschlagen: {fehler}")

        # ── Intentions-Profil aus LZG ────────────
        try:
            conn   = psycopg2.connect(postgres_url)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT intentionen, emotion, modus, sprach_stil, tone,
                       dimension, inhalt
                FROM langzeitgedaechtnis
                WHERE user_id = %s AND aktiv = TRUE
                  AND (intentionen != '[]' OR emotion != '' OR sprach_stil != '')
                ORDER BY gewicht DESC
                LIMIT 20
            """, (user_id,))

            intention_rows = cursor.fetchall()
            conn.close()

            if intention_rows:
                if shutdown_event and shutdown_event.is_set():
                    logger.info("Pixie-Task charakter_hash: Shutdown — breche ab")
                    return None

                eintraege: str = "\n".join(
                    f"[{dim}] Intentionen: {intent}, Emotion: {emo}, "
                    f"Modus: {mod}, Stil: {stil}, Tone: {tn} — {inh}"
                    for intent, emo, mod, stil, tn, dim, inh in intention_rows
                )

                node_cfg = get_node_config("charakter_hash")
                provider = get_background_provider()
                antwort  = provider.chat(
                    messages = [{"role": "user", "content": INTENTIONS_PROFIL_PROMPT.format(eintraege=eintraege)}],
                    temperature       = node_cfg.get("temperature", 0.2),
                    max_output_tokens = node_cfg.get("max_output_tokens"),
                    caller            = "pixie/hash",
                )

                ergebnis["intentions_profil"] = antwort.content.strip()
                logger.info(f"Intentions-Profil destilliert: '{ergebnis['intentions_profil'][:80]}...'")

        except Exception as fehler:
            logger.error(f"Intentions-Profil Destillation fehlgeschlagen: {fehler}")

        # ── Emotions-Profil aus LZG ──────────────
        try:
            conn   = psycopg2.connect(postgres_url)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT emotion, arousal, emotions_vektor,
                       dimension, inhalt, gewicht, verstaerkt_am
                FROM langzeitgedaechtnis
                WHERE user_id = %s AND aktiv = TRUE AND emotion != ''
                ORDER BY gewicht DESC
                LIMIT 20
            """, (user_id,))

            emotion_rows = cursor.fetchall()
            conn.close()

            if emotion_rows:
                if shutdown_event and shutdown_event.is_set():
                    logger.info("Pixie-Task charakter_hash: Shutdown — breche ab")
                    return None

                eintraege: str = "\n".join(
                    f"[{dim}] Emotion: {emo}, Arousal: {ar:.2f}, "
                    f"Vektor: {vek or 'keiner'} "
                    f"(Gewicht: {effektives_gewicht_berechnen(gew, va):.2f}): {inh}"
                    for emo, ar, vek, dim, inh, gew, va in emotion_rows
                )

                node_cfg = get_node_config("charakter_hash")
                provider = get_background_provider()
                antwort  = provider.chat(
                    messages = [{"role": "user", "content": EMOTIONS_PROFIL_PROMPT.format(eintraege=eintraege)}],
                    temperature       = node_cfg.get("temperature", 0.2),
                    max_output_tokens = node_cfg.get("max_output_tokens"),
                    caller            = "pixie/hash",
                )

                ergebnis["emotions_profil"] = antwort.content.strip()
                logger.info(f"Emotions-Profil destilliert: '{ergebnis['emotions_profil'][:80]}...'")

        except Exception as fehler:
            logger.error(f"Emotions-Profil Destillation fehlgeschlagen: {fehler}")

        # ── Beziehungsprofil aus KZG ─────────────
        try:
            kzg_keys: list = redis_client.keys(f"kzg:{user_id}:*")
            beziehungs_eintraege: list[str] = []

            for key in kzg_keys[:20]:
                inhalt:             str = redis_client.hget(key, "inhalt") or ""
                modus:              str = redis_client.hget(key, "modus") or ""
                emotion_kzg:        str = redis_client.hget(key, "emotion") or ""
                beziehungs_dynamik: str = redis_client.hget(key, "beziehungs_dynamik") or ""
                tone_kzg:           str = redis_client.hget(key, "tone") or ""

                if inhalt:
                    beziehungs_eintraege.append(
                        f"[Modus: {modus}, Emotion: {emotion_kzg}, "
                        f"Dynamik: {beziehungs_dynamik}, Tone: {tone_kzg}] {inhalt}"
                    )

            if beziehungs_eintraege:
                if shutdown_event and shutdown_event.is_set():
                    logger.info("Pixie-Task charakter_hash: Shutdown — breche ab")
                    return None

                eintraege: str = "\n".join(beziehungs_eintraege)

                node_cfg = get_node_config("charakter_hash")
                provider = get_background_provider()
                antwort  = provider.chat(
                    messages = [{"role": "user", "content": BEZIEHUNGS_PROFIL_PROMPT.format(eintraege=eintraege)}],
                    temperature       = node_cfg.get("temperature", 0.2),
                    max_output_tokens = node_cfg.get("max_output_tokens"),
                    caller            = "pixie/hash",
                )

                ergebnis["beziehungsprofil"] = antwort.content.strip()
                logger.info(f"Beziehungsprofil destilliert: '{ergebnis['beziehungsprofil'][:80]}...'")

        except Exception as fehler:
            logger.error(f"Beziehungsprofil Destillation fehlgeschlagen: {fehler}")

        # ── In PostgreSQL speichern ──────────────
        hat_aenderungen: bool = any(v for v in ergebnis.values())

        if hat_aenderungen:
            try:
                conn   = psycopg2.connect(postgres_url)
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO charakter_hash
                        (user_id, character_id, kern_hash, adaptive_hash, intentions_profil,
                         emotions_profil, beziehungsprofil,
                         kern_aktualisiert_am, adaptive_aktualisiert_am)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
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
                            ELSE charakter_hash.adaptive_aktualisiert_am END
                """, (
                    user_id, character_id,
                    ergebnis["kern"], ergebnis["adaptiv"],
                    ergebnis["intentions_profil"], ergebnis["emotions_profil"],
                    ergebnis["beziehungsprofil"],
                    ergebnis["kern"], ergebnis["kern"],
                    ergebnis["adaptiv"], ergebnis["adaptiv"],
                    ergebnis["intentions_profil"], ergebnis["intentions_profil"],
                    ergebnis["emotions_profil"], ergebnis["emotions_profil"],
                    ergebnis["beziehungsprofil"], ergebnis["beziehungsprofil"],
                    ergebnis["kern"],
                    ergebnis["adaptiv"],
                ))

                conn.commit()
                conn.close()

                redis_client.delete(f"hash_dirty:{user_id}:{character_id}")
                logger.info(f"Charakter-Hash gespeichert fuer Paar '{user_id}/{character_id}' (5 Profile)")

            except Exception as fehler:
                logger.error(f"Charakter-Hash Speicherung fehlgeschlagen: {fehler}")

        return None
