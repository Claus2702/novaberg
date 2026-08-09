"""SynapsenPromotionAgent — KZG -> LZG Synapsen-Promotion (Synapsen P4).

Promotet jeden reifen KZG-Eintrag als eigenstaendigen lzg_knoten und bildet
Kanten zu entitaets-, embedding-, themen- oder zeitlich verwandten
Bestandsknoten (assoziatives Netz, Konzept novaberg-memory-synapsen_k.md §7).
Hat den Cluster-Aggregat-Pfad des PromotionAgent abgeloest; jener ist mit
dem Codeschloss P9 aus dem Repositorium entfernt.

Bewusste Abweichungen vom alten PromotionAgent (Entscheidungs-Doku
novaberg-memory-synapsen-p4-entscheidungen_k.md):
  - Keine LLM-Calls, keine Fakten-Extraktion, kein FaktenManager (K2). Die
    Magnet-Felder entitaet_ids/timeline_id liegen seit P3 (magnete_aufloesen)
    fertig im KZG-Eintrag.
  - Embedding aus dem inhalt ALLEIN, ohne Themen-Anreicherung (K9). Der alte
    Pfad embeddet "themen inhalt" — hier bewusst nicht.
  - gewicht_roh = KZG-Salienz aus dem Hash-Feld 'salienz' (K8, direkte
    Uebernahme; Skala 0..1, KZG_SALIENZ_CAP seit Chat 113). Bewusst frisch aus dem Hash
    gelesen, NICHT aus dem Queue-Auftrag: die Salienz kann zwischen Einreihen
    und Promotion durch thematische Verstaerkung gestiegen sein. Der Auftrag
    traegt nur die Trigger-Salienz beim Einreihen.
  - Hybrid Magnet+Vector-Match (K10): bei Cosine >= LZG_KNOTEN_MATCH_SCHWELLE
    wird der Bestandsknoten verstaerkt (Reinforcement + Trigger 2), sonst ein
    neuer Knoten angelegt (+ Trigger 1).

Jedes Promotion-Event wird in beide Gedaechtnis-Spuren geschrieben (K5):
hintergrund_log (Pixie-Arbeitsgedaechtnis, via _audit_log) und pipeline_log
(Novas Selbstreflexion, via Span + log_db_write).

Der KZG-Hash wird wie im alten Pfad NICHT geloescht — er verfaellt ueber seine
TTL. Der Queue-Task wird seit dem 09.08.2026 nicht mehr per `lpop` konsumiert,
sondern per `LMOVE` in eine Arbeitsliste verschoben und erst nach gruenem
Ergebnis daraus entfernt; siehe `invoke`.
"""

import json
import logging
from datetime import datetime, timezone

from agents.base import BaseAgent, AgentState, PeriodicTask
from config import (
    ASSISTANT_USER_ID, DEFAULT_USER_ID,
    redis_client, POSTGRES_URL,
    PIXIE_PROMOTION_PRIORITAET, PIXIE_PROMOTION_INTERVALL_SEKUNDEN,
    PIXIE_AKTIV, MAX_PROMOTION_RUECKSTELLUNGEN,
)
from memory import lzg_knoten, lzg_kanten, pipeline_log
from memory.repositories.verbindung_repository import VerbindungRepository
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
        """Der einzige Promotions-Weg — ohne Schalter.

        Bis P9 stand hier ein Gate auf SYNAPSEN_PROMOTION_AKTIV, das diesen
        Agenten dormant hielt, solange der alte Cluster-Pfad die Queue
        bediente. Beides ist mit dem Codeschloss entfallen: Der alte Pfad ist
        geloescht, und ein Schalter, dessen Aus-Stellung keinen Ersatz mehr
        hat, schaltet die Promotion nicht um, sondern ab.
        """
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
        """Arbeitet die Promotion-Queue vollstaendig ab (KZG hat TTL).

        **Der Auftrag wird nicht entnommen, sondern verschoben.** `lpop` nahm
        ihn aus der Liste, bevor die Arbeit begann; scheiterte sie, war die
        Zeile weg — und nichts reihte sie je wieder ein, weil der Erzeuger nur
        bei einem neuen Turn schreibt. Der KZG-Hash ueberlebte seine sieben
        bis dreissig Tage und wurde nie promotet. **Jeder voruebergehende
        Fehler kostete so dauerhaft einen Gedaechtniskandidaten**, und die
        Zaehlung sagte es nicht (siehe die Meldung am Ende).

        Deshalb zwei Listen und ein `LMOVE`, das beides in einem Schritt tut:

            queue:{paar}            wartend
            queue:{paar}:arbeit     in Arbeit — genau ein Eintrag, solange
                                    die Verarbeitung laeuft

        Grün heisst `LREM` aus der Arbeitsliste. Rot heisst: der Eintrag
        **bleibt dort liegen** und ist damit sichtbar statt verschwunden.

        **Warum ein gefuelltes `:arbeit` beim Start eindeutig ist.** Der
        Pixie-Heartbeat ist EIN Job mit `max_instances=1` und `coalesce=True`
        (`main.py`), und dieser Agent ist ueber `graph_eignung` nur ueber ihn
        erreichbar. Wer hier laeuft, laeuft allein — es kann also kein zweiter
        gerade an diesen Eintraegen arbeiten. Ein gefuelltes `:arbeit` ist
        damit **immer** der Rest eines abgebrochenen Laufs und wird
        zurueckgelegt, nicht abgewartet. Das ersetzt jede Zeitheuristik.

        > Diese Eindeutigkeit haengt daran, dass **niemand den Agenten von
        > ausserhalb des Serverprozesses aufruft.** Ein Standalone-Skript, das
        > ihn direkt baut, laeuft neben dem Heartbeat und macht `:arbeit`
        > mehrdeutig — und es scheitert ohnehin, weil die ModelWorker nur im
        > Server-Loop laufen.

        Nachbedingung: `queue:{paar}` ist leer. In `:arbeit` steht genau das,
            was in diesem Lauf gescheitert ist — beim naechsten Lauf wird es
            zurueckgelegt und erneut versucht.
        """

        user_id: str = state["kontext"].get("user_id", "") or DEFAULT_USER_ID
        queue_key: str = f"queue:{user_id}"
        arbeit_key: str = f"{queue_key}:arbeit"
        promotet: int = 0
        fehler: int = 0

        gescheitert_key: str = f"{queue_key}:gescheitert"
        versuche_key: str = f"{queue_key}:versuche"

        # ── Souveraenitaetspruefung ─────────────────
        # Vom Ende der Arbeitsliste nach vorn in die Warteschlange: Damit
        # behalten die Reste ihre urspruengliche Reihenfolge und stehen vor
        # dem, was inzwischen dazugekommen ist — sie sind ja aelter.
        #
        # Der Zaehler steht bewusst NICHT in der Nutzlast. Er dort
        # hochzuzaehlen hiesse entnehmen, aendern, neu schreiben — und ein
        # Absturz zwischen den Schritten verloere genau den Eintrag, den
        # diese Mechanik retten soll. Als eigener Hash bleibt jede
        # Verschiebung ein atomares LMOVE; ein Absturz kostet dann
        # schlimmstenfalls einen falsch gezaehlten Versuch.
        #
        # `lindex` vor dem `lmove` ist hier gefahrlos, weil der Souveraen
        # allein laeuft: Zwischen Blick und Griff kann sich die Liste nicht
        # bewegen.
        zurueckgelegt: int = 0
        endgueltig: int = 0
        while (roh := redis_client.lindex(arbeit_key, -1)) is not None:
            try:
                text = roh.decode("utf-8") if isinstance(roh, bytes) else roh
                kzg_key: str = json.loads(text).get("key", "")
            except (json.JSONDecodeError, TypeError, AttributeError):
                # Ein unlesbarer Eintrag kann nie gruen werden. Er wandert
                # sofort auf den Fehlerstapel statt zweimal zu kreisen.
                kzg_key = ""

            versuch: int = redis_client.hincrby(versuche_key, kzg_key or "<unlesbar>", 1)

            if not kzg_key or versuch > MAX_PROMOTION_RUECKSTELLUNGEN:
                redis_client.lmove(arbeit_key, gescheitert_key, "RIGHT", "RIGHT")
                redis_client.hdel(versuche_key, kzg_key or "<unlesbar>")
                endgueltig += 1
            else:
                redis_client.lmove(arbeit_key, queue_key, "RIGHT", "LEFT")
                zurueckgelegt += 1

        if zurueckgelegt or endgueltig:
            logger.warning(
                f"Synapsen-Promotion: Reste eines abgebrochenen Laufs in "
                f"'{arbeit_key}' — {zurueckgelegt} zurueckgelegt, {endgueltig} "
                f"nach {MAX_PROMOTION_RUECKSTELLUNGEN} Versuchen auf den "
                f"Fehlerstapel '{gescheitert_key}'"
            )

        # ── Verarbeitung ────────────────────────────
        while True:
            roh = redis_client.lmove(queue_key, arbeit_key, "LEFT", "RIGHT")
            if not roh:
                break
            try:
                text: str = roh.decode("utf-8") if isinstance(roh, bytes) else roh
                auftrag: dict = json.loads(text)
                self._eintrag_verarbeiten(auftrag, user_id)
                promotet += 1
                redis_client.lrem(arbeit_key, 1, roh)
                # Der Zaehler gehoert zum Auftrag, nicht zum Schluessel: Ein
                # Eintrag, der nach zwei Fehlversuchen durchlaeuft, startet
                # beim naechsten Mal wieder bei null.
                redis_client.hdel(versuche_key, auftrag.get("key", ""))
            except Exception as ex:
                # Kein lrem: Der Eintrag bleibt in der Arbeitsliste. Das ist
                # der ganze Unterschied zu vorher — er ist danach auffindbar
                # und wird beim naechsten Lauf zurueckgelegt.
                logger.error(f"Synapsen-Promotion: Fehler bei Eintrag: {ex}", exc_info=True)
                fehler += 1

        # ── Ausgabe-Verifikation ────────────────────
        # Die alte Fassung meldete "Queue leer — nichts zu tun" auf debug,
        # sobald `promotet == 0` war — auch dann, wenn JEDER Eintrag
        # gescheitert war. Ein Lauf, der fuenf Gedaechtniskandidaten verliert,
        # sah aus wie ein Lauf ohne Arbeit, und die Zahl, die beides
        # unterscheidet, stand in derselben Funktion.
        if promotet or fehler or zurueckgelegt:
            logger.info(
                f"Synapsen-Promotion: {promotet} promotet, {fehler} gescheitert "
                f"(liegen in '{arbeit_key}'), {zurueckgelegt} zurueckgelegt"
            )
        else:
            logger.debug("Synapsen-Promotion: Queue leer — nichts zu tun")

        state["ergebnis"] = {
            "promotet": promotet, "fehler": fehler,
            "zurueckgelegt": zurueckgelegt, "endgueltig": endgueltig,
        }
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
            user_id=user_id, character_id=ASSISTANT_USER_ID,
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

        # gewicht_roh = KZG-Salienz aus dem Hash (K8). Skala 0..1
        # (KZG_SALIENZ_CAP seit Chat 113). Frisch aus dem Hash, nicht aus dem
        # Auftrag — die Salienz kann zwischen Einreihen und Promotion durch
        # thematische Verstaerkung gestiegen sein. knoten_anlegen daempft sie
        # per Sinus auf gewicht_absolut (Cap 10) und setzt
        # gewicht_decay = gewicht_absolut. Dass roh > CAP auftreten kann, ist
        # damit ausgeschlossen (KZG-GEWICHT-ABSOLUT-CEILING).
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
        embed_response = model_service.embed.submit_sync(
            EmbedRequest(text=lzg_knoten.embed_text_bauen(inhalt))
        )
        embedding: list[float] = embed_response.embedding
        embedding_str: str = "[" + ",".join(str(x) for x in embedding) + "]"
        pipeline_log.log_berechnung(
            turn_id=kzg_key, node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"embedding_dim": len(embedding), "dauer_s": embed_response.duration_seconds},
            user_id=user_id, character_id=character_id,
        )

        # ── Kandidaten der Paar-Partition mit SQL-Cosine (Match + Kantenbildung) ──
        # include_inactive=True: deaktivierte Knoten muessen als Match sichtbar
        # sein, damit die Halbreaktivierung (§9.3) sie wecken kann statt eine
        # Dublette neu anzulegen.
        kandidaten: list[dict] = lzg_knoten.kandidaten_mit_cosine_laden(
            POSTGRES_URL, user_id, character_id, embedding_str,
            include_inactive=True,
        )
        match: dict | None = lzg_knoten.match_pruefen(kandidaten)

        if match is not None and match["aktiv"] is False:
            # ── Halbreaktivierungs-Pfad (§9.3) ──────
            # Deaktivierter Knoten wird geweckt (halber gewicht_decay, aktiv=TRUE).
            # KEINE Kanten-Neuberechnung: gewicht_absolut bleibt unveraendert,
            # also kein Trigger 2 (§7.9.2) — die Kanten bleiben voll wirksam (§9.5).
            knoten_id: int = match["id"]
            reaktiv = lzg_knoten.reactivate_node(POSTGRES_URL, knoten_id)
            aktion: str = "halbreaktivierung"
            if reaktiv is not None:
                info: str = (
                    f"knoten={knoten_id} cosine={match['cosine']:.4f} "
                    f"decay {reaktiv['decay_alt']:.3f} -> {reaktiv['decay_neu']:.3f}"
                )
                pipeline_log.log_berechnung(
                    turn_id=kzg_key, node=NODE, quelle=QUELLE, span_id=span_id,
                    inhalt={"aktion": aktion, **reaktiv,
                            "paar": f"{user_id}:{character_id}"},
                    user_id=user_id, character_id=character_id,
                )
            else:
                # reactivate_node scheiterte (nicht gefunden / bereits aktiv /
                # DB-Fehler) — fail-loud im Log, kein Abbruch des Promotion-Laufs.
                info: str = f"knoten={knoten_id} cosine={match['cosine']:.4f} reaktivierung_fehlgeschlagen"
                logger.warning(
                    "Halbreaktivierung fehlgeschlagen: knoten=%s paar=%s/%s",
                    knoten_id, user_id, character_id,
                )
        elif match is not None:
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

        # ── verbindung: lzg_id nachtragen (§11.2) ──────
        # Hinter allen drei Pfaden, weil in allen dreien derselbe Umzug
        # stattfindet: Halbreaktivierung, Reinforcement und Neuanlage geben den
        # Knoten an, in den dieser KZG-Eintrag gewandert ist. Ein Schreibpunkt
        # statt drei.
        self._verbindung_lzg_id_nachtragen(kzg_key, knoten_id, user_id, character_id)

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
            user_id=user_id, character_id=character_id,
        )
        pipeline_log.span_end(
            turn_id=kzg_key, node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"aktion": aktion, "knoten_id": knoten_id},
            user_id=user_id, character_id=character_id,
        )

    def _verbindung_lzg_id_nachtragen(
        self,
        kzg_key:      str,
        knoten_id:    int,
        user_id:      str,
        character_id: str,
    ) -> int:
        """Verdrahtet die Bruecken-Zeilen dieses KZG-Keys auf den LZG-Knoten.

        §11.2: Der KZG-Key ist TTL-fluechtig. Ohne diesen Nachtrag zeigt die
        `verbindung`-Zeile ins Leere, sobald er verfaellt — und der Weg vom
        erinnerungswuerdigen Knoten zurueck zum Rohturn ist zu.

        Vorbedingung: kzg_key und knoten_id liegen vor; beim Aufruf hinter den
        drei Promotions-Pfaden ist das immer der Fall.
        Nachbedingung: alle Zeilen mit dieser kzg_id tragen die knoten_id.
        Fehlerfaelle: fehlende Eingabe (error, 0), Datenbankfehler (error mit
        Forensik, 0). Die Methode wirft nicht — ein fehlgeschlagener Nachtrag
        darf den Promotions-Lauf nicht reissen, muss aber laut sein.
        """
        # ── Eingabe-Validierung ─────────────────────
        if not kzg_key or not knoten_id:
            logger.error(
                f"Synapsen-Promotion: verbindung-Nachtrag uebersprungen — "
                f"kzg_key='{kzg_key}', knoten_id={knoten_id}"
            )
            return 0

        # ── Verarbeitung ────────────────────────────
        # Eigenes try/except: die Fehlerbehandlung des Promotions-Laufs fasst
        # den Nachtrag nicht an.
        try:
            ergebnis: dict[str, int] = VerbindungRepository.lzg_id_nachtragen(
                postgres_url = POSTGRES_URL,
                kzg_id       = kzg_key,
                lzg_id       = knoten_id,
            )
        except Exception as ex:
            logger.error(
                f"Synapsen-Promotion: verbindung-Nachtrag fehlgeschlagen — "
                f"kzg_key={kzg_key}, knoten_id={knoten_id}, paar={user_id}:{character_id}, "
                f"fehler={ex}",
                exc_info=True,
            )
            return 0

        # ── Ausgabe-Verifikation ────────────────────
        gefunden:  int = ergebnis["gefunden"]
        geaendert: int = ergebnis["geaendert"]

        if gefunden == 0:
            # Kein Defekt: KZG-Eintraege ohne turn_id (Pixie-Laeufe) und alle
            # vor dem Bau der Tabelle erzeugten haben keine Bruecken-Zeile.
            logger.info(
                f"Synapsen-Promotion: verbindung-Nachtrag ohne Treffer — "
                f"kzg_key={kzg_key}, knoten_id={knoten_id}, keine Bruecken-Zeile vorhanden"
            )
        else:
            logger.info(
                f"Synapsen-Promotion: verbindung nachgetragen — knoten_id={knoten_id}, "
                f"kzg_key={kzg_key}, {geaendert} von {gefunden} Zeilen geschrieben"
            )

        return geaendert

    def _fehler(self, user_id: str, aufgabe: str, kzg_key: str, span_id, grund: str) -> None:
        """Einheitlicher Fehler-Abschluss: Log, hintergrund_log, pipeline_log, Span-Ende."""
        logger.error(f"Synapsen-Promotion: {grund}")
        self._audit_log(user_id, aufgabe, "fehler", grund)
        pipeline_log.log_fehler(
            turn_id=kzg_key or "?", node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"grund": grund},
            user_id=user_id, character_id=ASSISTANT_USER_ID,
        )
        pipeline_log.span_end(
            turn_id=kzg_key or "?", node=NODE, quelle=QUELLE, span_id=span_id,
            inhalt={"status": "fehler"},
            user_id=user_id, character_id=ASSISTANT_USER_ID,
        )
