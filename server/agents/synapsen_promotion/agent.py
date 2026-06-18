"""SynapsenPromotionAgent — KZG -> LZG Synapsen-Promotion (Synapsen P4).

Promotet jeden reifen KZG-Eintrag als eigenstaendigen lzg_knoten und bildet
Kanten zu entitaets-, embedding-, themen- oder zeitlich verwandten
Bestandsknoten (assoziatives Netz, Konzept novaberg-memory-synapsen_k.md §7).
Ersetzt den Cluster-Aggregat-Pfad des PromotionAgent, sobald
SYNAPSEN_PROMOTION_AKTIV gesetzt ist.

Bewusste Abweichungen vom alten PromotionAgent (Entscheidungs-Doku
novaberg-memory-synapsen-p4-entscheidungen_k.md):
  - Keine LLM-Calls, keine Fakten-Extraktion, kein FaktenManager (K2). Die
    Magnet-Felder entitaet_ids/timeline_id liegen seit P3 (magnete_aufloesen)
    fertig im KZG-Eintrag.
  - Embedding aus dem inhalt ALLEIN, ohne Themen-Anreicherung (K9). Der alte
    Pfad embeddet "themen inhalt" — hier bewusst nicht.
  - gewicht_roh = KZG-Salienz aus dem Hash-Feld 'salienz' (K8, direkte
    Uebernahme; Skala 0..10, KZG_SALIENZ_CAP). Bewusst frisch aus dem Hash
    gelesen, NICHT aus dem Queue-Auftrag: die Salienz kann zwischen Einreihen
    und Promotion durch thematische Verstaerkung gestiegen sein. Der Auftrag
    traegt nur die Trigger-Salienz beim Einreihen.
  - Hybrid Magnet+Vector-Match (K10): bei Cosine >= LZG_KNOTEN_MATCH_SCHWELLE
    wird der Bestandsknoten verstaerkt (Reinforcement + Trigger 2), sonst ein
    neuer Knoten angelegt (+ Trigger 1).

Jedes Promotion-Event wird in beide Gedaechtnis-Spuren geschrieben (K5):
hintergrund_log (Pixie-Arbeitsgedaechtnis, via _audit_log) und pipeline_log
(Novas Selbstreflexion, via Span + log_db_write).

Der KZG-Hash wird wie im alten Pfad NICHT geloescht — der Queue-Task ist per
lpop konsumiert, der Hash verfaellt ueber seine TTL.
"""

import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ASSISTANT_USER_ID, DEFAULT_USER_ID,
    redis_client, POSTGRES_URL,
    PIXIE_PROMOTION_PRIORITAET, PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
    PIXIE_AKTIV, SYNAPSEN_PROMOTION_AKTIV,
)
from memory import lzg_knoten, lzg_kanten, pipeline_log
from services.model_services import model_service, EmbedRequest
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.synapsen_promotion")

# Forensik-Markierung fuer pipeline_log (K5): quelle = Produzent, node = Stufe.
QUELLE: str = "pixie"
NODE: str = "synapsen_promotion"


class SynapsenPromotionAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "synapsen_promotion"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["synapsen_promotion"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    def periodic_task(self) -> PeriodicTask | None:
        """Feature-Flag-Gate (P4): solange SYNAPSEN_PROMOTION_AKTIV False ist,
        bleibt dieser Agent dormant (None = kein Scheduling) und der alte
        Cluster-Pfad (PromotionAgent) bedient die Queue weiter. Erst beim
        Scharfschalten in Phase D wird der alte Pfad stillgelegt.
        """
        if not SYNAPSEN_PROMOTION_AKTIV:
            return None
        return PeriodicTask(
            name="synapsen_promotion",
            priority=PIXIE_PROMOTION_PRIORITAET,
            interval=PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
            description="KZG -> LZG Synapsen-Promotion (Knoten + Kanten, P4)",
        )

    def build_graph(self):
        # Wie PromotionAgent: dieser Agent ist kein LangGraph-Subgraph, sondern
        # arbeitet die Queue direkt in invoke() ab.
        return None

    # ─────────────────────────────────────────
    # Audit-Log (hintergrund_log — Pixie-Arbeitsgedaechtnis, K5)
    # ─────────────────────────────────────────
    @staticmethod
    def _audit_log(user_id: str, aufgabe: str, status: str, ergebnis: str) -> None:
        """Schreibt einen Audit-Eintrag ins hintergrund_log.

        Failsafe: Bei DB-Fehler nur logger.critical — kein Retry, um
        Endlos-Rekursion bei kaputter Audit-Senke zu vermeiden.
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
        """Arbeitet die Promotion-Queue vollstaendig ab (KZG hat TTL)."""
        # Feature-Flag-Gate (P4): Selbst wenn der Queue-Peek diesen Agenten
        # ueber die umgeleitete lzg_promotion-Route invoked, bleibt er bei
        # ausgeschaltetem Flag wirkungslos — er leert die Queue nicht. Der
        # Flag ist damit der einzige Schalter fuer das gesamte Subsystem.
        if not SYNAPSEN_PROMOTION_AKTIV:
            logger.debug(
                "Synapsen-Promotion: inaktiv (SYNAPSEN_PROMOTION_AKTIV=False) — "
                "Queue nicht geleert"
            )
            state["ergebnis"] = {"promotet": 0, "fehler": 0, "inaktiv": True}
            state["status"] = "abgeschlossen"
            return state

        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID
        queue_key: str = f"queue:{user_id}"
        promotet: int = 0
        fehler: int = 0

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
                logger.error(f"Synapsen-Promotion: Fehler bei Eintrag: {ex}", exc_info=True)
                fehler += 1

        if promotet > 0:
            logger.info(f"Synapsen-Promotion: {promotet} Eintraege promotet, {fehler} Fehler")
        else:
            logger.debug("Synapsen-Promotion: Queue leer — nichts zu tun")

        state["ergebnis"] = {"promotet": promotet, "fehler": fehler}
        state["status"] = "abgeschlossen"
        return state

    # ─────────────────────────────────────────
    # Eintrag verarbeiten (EVA)
    # ─────────────────────────────────────────
    def _eintrag_verarbeiten(self, auftrag: dict, user_id: str) -> None:
        """Promotet einen einzelnen KZG-Eintrag in das Synapsen-Netz."""
        kzg_key: str = auftrag.get("key", "")
        themen_str: str = auftrag.get("themen", "")
        # Trigger-Salienz beim Einreihen — NUR Start-Kontext. Die massgebliche
        # gewicht_roh-Salienz (0..10, K8) wird nach der Validierung frisch aus
        # dem KZG-Hash gelesen (kann durch Verstaerkung gestiegen sein).
        trigger_salienz: float = float(auftrag.get("salienz", 0.0))
        dimension: str = auftrag.get("dimension", "kontext")
        aufgabe: str = f"synapsen_promotion:{kzg_key or '?'}"

        eingabe_zsf: str = f"kzg_key='{kzg_key}', themen='{themen_str}', trigger_salienz={trigger_salienz:.3f}"
        logger.info(f"Synapsen-Promotion: gestartet — {eingabe_zsf}")
        self._audit_log(user_id, aufgabe, "gestartet", eingabe_zsf)
        span_id = pipeline_log.span_start(
            turn_id=kzg_key, node=NODE, quelle=QUELLE,
            inhalt={"phase": "start", "themen": themen_str, "trigger_salienz": trigger_salienz},
        )

        # ── Vorbedingung 1: KZG-Key vorhanden ──────
        if not kzg_key:
            self._fehler(user_id, aufgabe, kzg_key, span_id, "Auftrag ohne KZG-Key — verworfen")
            return

        # ── Vorbedingung 2: KZG-Eintrag existiert noch in Redis ──────
        if not redis_client.exists(kzg_key):
            self._fehler(
                user_id, aufgabe, kzg_key, span_id,
                f"KZG-Key '{kzg_key}' nicht mehr vorhanden (TTL abgelaufen) — verworfen",
            )
            return

        def _hget(field: str, default: str = "") -> str:
            val = redis_client.hget(kzg_key, field)
            if val is None:
                return default
            return val.decode("utf-8") if isinstance(val, bytes) else val

        inhalt: str = _hget("inhalt")

        # ── Vorbedingung 3: Inhalt nicht leer ──────
        if not inhalt:
            self._fehler(
                user_id, aufgabe, kzg_key, span_id,
                f"KZG-Key '{kzg_key}' existiert, aber Feld 'inhalt' ist leer — verworfen",
            )
            return

        # ── KZG-Felder laden (nach Validierung) ──────
        character_id: str = _hget("character_id") or ASSISTANT_USER_ID
        beobachter: str = _hget("beobachter") or "user"
        emotion: str = _hget("emotion")
        arousal: float = float(_hget("arousal", "0.5"))
        modus: str = _hget("modus")
        sprach_stil: str = _hget("sprach_stil")
        beziehungs_dynamik: str = _hget("beziehungs_dynamik")
        tone: str = _hget("tone")
        intentionen: str = _hget("intentionen", "[]")
        gedaechtnistyp: str | None = _hget("gedaechtnistyp") or None
        emotions_vektor: str = _hget("emotions_vektor")

        # Magnet-Felder aus P3 (magnete_aufloesen): kommagetrennte Entitaets-IDs,
        # optionale timeline_id (bei None aus dem Hash ausgelassen).
        entitaet_ids: list[int] = [int(x) for x in _hget("entitaet_ids").split(",") if x.strip()]
        timeline_id_str: str = _hget("timeline_id")
        timeline_id: int | None = int(timeline_id_str) if timeline_id_str.strip() else None

        themen_list: list[str] = sorted({t.strip() for t in themen_str.split(",") if t.strip()})

        # gewicht_roh = KZG-Salienz aus dem Hash (K8). Skala 0..10
        # (KZG_SALIENZ_CAP). Frisch aus dem Hash, nicht aus dem Auftrag — die
        # Salienz kann zwischen Einreihen und Promotion durch thematische
        # Verstaerkung gestiegen sein. knoten_anlegen daempft sie per Sinus auf
        # gewicht_absolut (Cap 10) und setzt gewicht_decay = gewicht_absolut.
        salienz: float = float(_hget("salienz", "0"))

        # kzg_erstellt_am ist ein Unix-Timestamp (Float). knoten_anlegen wandelt
        # ihn per to_timestamp in TIMESTAMPTZ. Fallback: jetzt.
        erstellt_am_raw: str = _hget("erstellt_am")
        try:
            kzg_erstellt_am: float = (
                float(erstellt_am_raw) if erstellt_am_raw else datetime.now(timezone.utc).timestamp()
            )
        except ValueError:
            kzg_erstellt_am = datetime.now(timezone.utc).timestamp()

        logger.info(
            f"Synapsen-Promotion: Paar={user_id}:{character_id}, Beobachter={beobachter}, "
            f"kzg_salienz={salienz:.3f} (0-10), entitaeten={entitaet_ids}, timeline_id={timeline_id}"
        )

        # ── Embedding aus inhalt ALLEIN (K9 — keine Themen-Anreicherung) ──────
        embed_response = model_service.embed.submit_sync(EmbedRequest(text=inhalt))
        embedding: list[float] = embed_response.embedding
        embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"
        pipeline_log.log_berechnung(
            turn_id=kzg_key, node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"embedding_dim": len(embedding), "dauer_s": embed_response.duration_seconds},
        )

        # ── Kandidaten der Paar-Partition mit SQL-Cosine (Match + Kantenbildung) ──
        kandidaten: list[dict] = lzg_knoten.kandidaten_mit_cosine_laden(
            POSTGRES_URL, user_id, character_id, embedding_str,
        )
        match: dict | None = lzg_knoten.match_pruefen(kandidaten)

        if match is not None:
            # ── Reinforcement-Pfad (K10) ──────
            lzg_knoten.knoten_verstaerken(POSTGRES_URL, match["id"])
            kanten_neu: int = lzg_kanten.kanten_neuberechnen_fuer_knoten(POSTGRES_URL, match["id"])
            knoten_id: int = match["id"]
            aktion: str = "reinforcement"
            info: str = f"knoten={knoten_id} cosine={match['cosine']:.4f} kanten_neu={kanten_neu}"
        else:
            # ── Neuanlage-Pfad ──────
            neue_id = lzg_knoten.knoten_anlegen(
                POSTGRES_URL,
                kzg_quell_key=kzg_key, user_id=user_id, character_id=character_id,
                beobachter=beobachter, inhalt=inhalt, embedding_str=embedding_str,
                dimension=dimension, gewicht_roh=salienz, kzg_erstellt_am=kzg_erstellt_am,
                themen=themen_list, gedaechtnistyp=gedaechtnistyp,
                entitaet_ids=entitaet_ids, timeline_id=timeline_id,
                emotion=emotion, arousal=arousal, emotions_vektor=emotions_vektor,
                intentionen=intentionen, modus=modus, sprach_stil=sprach_stil,
                beziehungs_dynamik=beziehungs_dynamik, tone=tone,
            )
            if neue_id is None:
                self._fehler(
                    user_id, aufgabe, kzg_key, span_id,
                    f"knoten_anlegen lieferte None fuer '{kzg_key}' — LZG-Write fehlgeschlagen",
                )
                return
            # Neuen Knoten in Kandidaten-Form zuruecklesen (gewicht_absolut +
            # Timeline-Bezug) und Kanten zu allen Kandidaten bilden (Trigger 1).
            neuer: dict | None = lzg_knoten.knoten_laden(POSTGRES_URL, neue_id)
            paare: int = (
                lzg_kanten.kanten_fuer_neuen_knoten_bilden(POSTGRES_URL, neuer, kandidaten)
                if neuer else 0
            )
            knoten_id = neue_id
            aktion = "neuanlage"
            info = f"knoten={knoten_id} kanten_paare={paare}"

        # ── hash_dirty (Charakter-Hash neu berechnen lassen) ──────
        if PIXIE_AKTIV:
            redis_client.set(f"hash_dirty:{user_id}:{character_id}", "1")

        # ── Ausgabe: beide Gedaechtnis-Spuren (K5) ──────
        ausgabe_zsf: str = f"aktion={aktion}, {info}, gewicht_roh={salienz:.3f}"
        logger.info(f"Synapsen-Promotion: erledigt — {ausgabe_zsf}")
        self._audit_log(user_id, aufgabe, "erledigt", ausgabe_zsf)
        pipeline_log.log_db_write(
            turn_id=kzg_key, node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={
                "aktion": aktion, "knoten_id": knoten_id, "info": info,
                "paar": f"{user_id}:{character_id}", "gewicht_roh": salienz,
            },
        )
        pipeline_log.span_end(
            turn_id=kzg_key, node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"aktion": aktion, "knoten_id": knoten_id},
        )

    def _fehler(self, user_id: str, aufgabe: str, kzg_key: str, span_id, grund: str) -> None:
        """Einheitlicher Fehler-Abschluss: Log, hintergrund_log, pipeline_log, Span-Ende."""
        logger.error(f"Synapsen-Promotion: {grund}")
        self._audit_log(user_id, aufgabe, "fehler", grund)
        pipeline_log.log_fehler(
            turn_id=kzg_key or "?", node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"grund": grund},
        )
        pipeline_log.span_end(
            turn_id=kzg_key or "?", node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"status": "fehler"},
        )
