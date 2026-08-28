"""Shadow Agent — Shared Utilities.

Die **Shadow-Queue** liegt seit dem 15.08.2026 in PostgreSQL
(`novaberg-queue-verfall_k.md`), die **Promotions-Queue** weiterhin in Redis.
Beide Schreibpfade stehen hier nebeneinander; der Unterschied ist gewollt und
in §7.2 des Konzepts begruendet.
"""

import json
import logging

import psycopg2
import redis

from config import (
    ASSISTANT_USER_ID,
    MESSREIHE_OHNE_AUFTRAGSARTEN,
    PIXIE_AKTIV,
    POSTGRES_URL,
)

logger = logging.getLogger("ki_server.shadow")


# ─────────────────────────────────────────────
# Queue befüllen (wird vom Hauptgraph aufgerufen)
# ─────────────────────────────────────────────
def shadow_queue_push(
    redis_client: redis.Redis,
    user_id:      str,
    aufgabe:      str,
    thema:        str,
    prioritaet:   float,
    kontext:      str = "",
    intentionen:  list = None,
    emotion:      str  = "",
    modus:        str  = "",
    arousal:      float | None = None,
    bezug_id:     int | None = None,
    ausloeser_turn_id: str | None = None,
) -> None:
    """Legt einen Auftrag in die Shadow-Queue.

    `ausloeser_turn_id` ist der Turn, aus dem der Auftrag entstand — das
    erste Glied der Sachlage-Bruecke (`novaberg-thinking-lage_k.md` §4,
    Scheibe 4). `None` heisst unbekannt, nie eine leere Zeichenkette.

    **`prioritaet` ist Pflicht und hatte bis zum 15.08.2026 den Vorgabewert
    0.0.** Der Wert traegt die Ausloese-Salienz des Turns; eine 0.0 ist ein
    gueltiger Salienzwert, unterschreitet aber jede Schwelle und sortiert den
    Auftrag an das Ende jeder Rangfolge — lautlos. Von zwei Aufrufern uebergab
    ihn genau einer, und der Aufruf des anderen sah dabei vollstaendig aus.
    Gemessen ueber 1036 Auftraege: 233 trugen 0.0, alle davon `vertiefen`.
    Deshalb kein Vorgabewert: Wer die Salienz nicht hat, soll hier scheitern
    und nicht spaeter eine Zahl vorfinden, die wie eine Messung aussieht
    (`KANDIDATEN-PRIORITAET-STILLE-NULL`).

    Waehrend eines Messreihen-Laufs werden die Auftragsarten aus
    `MESSREIHE_OHNE_AUFTRAGSARTEN` **gar nicht erst eingereiht**. Der Grund
    steht dort: Eine Messreihe muss abschliessen, und ein Bogen ist erst zu
    Ende, wenn die Queues leer sind — mit sechzig Recherche-Auftraegen darin
    kommt die Destillation nie an die Reihe, und ohne Destillation misst die
    Reihe nicht, was sie messen soll.

    **Unterdrueckt heisst protokolliert, nicht verschwiegen.** Eine leere
    Queue ohne Spur waere von einer Queue, die nie befuellt wurde, nicht zu
    unterscheiden — und genau diese Verwechslung kostet spaeter die
    Erklaerung, warum eine Persona kein recherchiertes Wissen traegt.
    """
    if not PIXIE_AKTIV:
        logger.debug("shadow_agent.utils: shadow_queue_push uebersprungen (PIXIE_AKTIV=False)")
        return

    if aufgabe in MESSREIHE_OHNE_AUFTRAGSARTEN:
        logger.info(
            f"Shadow-Queue: '{aufgabe}' fuer '{user_id}' NICHT eingereiht "
            f"(Messreihen-Modus) — {thema[:60]}"
        )
        return

    # **Der Import steht hier und nicht am Modulkopf**, weil er sonst einen
    # Zyklus schliesst: `memory/__init__` laedt `memory.kzg`, und die holt sich
    # `shadow_queue_push` aus genau diesem Modul. Ein lokaler Import bricht
    # ihn auf; dieselbe Bauart benutzt `pixie/dispatch.py` fuer die Registry.
    from memory.repositories.shadow_auftrag_repository import (
        ShadowAuftrag,
        ShadowAuftragRepository,
    )

    # Die Queue liegt seit dem 15.08.2026 in PostgreSQL statt als Redis-Liste
    # (`novaberg-queue-verfall_k.md` §7). Der Parameter `redis_client` bleibt
    # in der Signatur, weil er die Schwester `promotion_queue_push` bedient und
    # jede Aufrufstelle beide Wege kennt; hier wird er nicht mehr gebraucht.
    #
    # **Derselbe Gegenstand erzeugt keine zweite Zeile mehr**, sondern
    # verstaerkt die vorhandene — und weckt sie, wenn sie ruht (§6.1). Das
    # Repository entscheidet das; hier steht nur der Auftrag.
    auftrag = ShadowAuftrag(
        user_id      = user_id,
        character_id = ASSISTANT_USER_ID,
        beobachter   = "user",
        aufgabe      = aufgabe,
        thema        = thema,
        salienz      = prioritaet,
        kontext      = kontext,
        intentionen  = intentionen or [],
        emotion      = emotion,
        modus        = modus,
        arousal      = arousal,
        bezug_id     = bezug_id,
        ausloeser_turn_id = ausloeser_turn_id or None,
    )

    try:
        _auftrag_id, vorgang = ShadowAuftragRepository.einreihen(POSTGRES_URL, auftrag)
    except (psycopg2.Error, ValueError):
        # **Kein stiller Verlust.** Ein Auftrag, der hier verlorengeht, ist ein
        # Gedanke, den niemand je aufgreift — und niemand wuerde ihn vermissen,
        # weil er nie existiert hat. Deshalb laut und mit dem Gegenstand.
        logger.exception(
            "Shadow-Queue: '%s' fuer '%s' konnte nicht eingereiht werden — %s",
            aufgabe, user_id, thema[:60],
        )
        return

    logger.info(
        "Shadow-Queue: '%s' fuer '%s' %s — %s",
        aufgabe, user_id, vorgang, thema[:60] or "<ohne Thema>",
    )


# ─────────────────────────────────────────────
# Promotions-Queue befüllen (idempotent je KZG-Key)
# ─────────────────────────────────────────────
def promotion_queue_push(
    redis_client: redis.Redis,
    user_id:      str,
    key:          str,
    salienz:      float,
    themen:       str = "",
    dimension:    str = "",
) -> bool:
    """Reiht einen KZG-Key zur LZG-Promotion ein — nur, wenn er nicht schon liegt.

    Bis Chat 111 schrieben drei Stellen ohne jede Pruefung; derselbe Key konnte
    mehrfach in der Queue stehen. Eine Dublette kann nachweislich nichts
    beitragen: Der SynapsenPromotionAgent liest die Salienz **frisch aus dem
    Hash** statt aus dem Auftrag (agents/synapsen_promotion/agent.py:236-240),
    der erste Auftrag holt einen gestiegenen Wert also ohnehin ab.

    Vorbedingung: user_id und key sind nicht leer.
    Nachbedingung: In `queue:{user_id}` liegt genau ein lzg_promotion-Auftrag
        fuer diesen Key. Rueckgabe True, wenn dieser Aufruf ihn angelegt hat.
    Fehlerfaelle: leere Pflichtfelder — laut abgelehnt, kein Push. Ein
        unlesbarer Fremdeintrag in der Queue blockiert die Pruefung nicht,
        wird aber benannt.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not key:
        logger.error(
            f"promotion_queue_push: Pflichtfeld leer — user_id='{user_id}', "
            f"key='{key}' — nicht eingereiht"
        )
        return False

    if not PIXIE_AKTIV:
        logger.debug("shadow_agent.utils: promotion_queue_push uebersprungen (PIXIE_AKTIV=False)")
        return False

    # ── Verarbeitung: liegt der Key schon? ──────
    queue_key: str = f"queue:{user_id}"

    for roh in redis_client.lrange(queue_key, 0, -1):
        try:
            vorhanden: dict = json.loads(roh)
        except (json.JSONDecodeError, TypeError) as fehler:
            # Kein stiller Uebersprung: Ein unlesbarer Eintrag gehoert
            # benannt. Er darf die Pruefung aber nicht abbrechen, sonst
            # blockiert ein fremder Datensatz jede Promotion.
            logger.warning(
                f"promotion_queue_push: unlesbarer Queue-Eintrag in {queue_key} "
                f"({type(fehler).__name__}) — bei der Dublettenpruefung uebergangen"
            )
            continue

        if vorhanden.get("aufgabe") == "lzg_promotion" and vorhanden.get("key") == key:
            logger.debug(
                f"Promotions-Queue: '{key}' liegt bereits — nicht erneut eingereiht"
            )
            return False

    redis_client.rpush(queue_key, json.dumps({
        "aufgabe":   "lzg_promotion",
        "user_id":   user_id,
        "key":       key,
        "salienz":   salienz,
        "themen":    themen,
        "dimension": dimension,
    }))

    # ── Ausgabe ─────────────────────────────────
    logger.info(f"Promotions-Queue: '{key}' eingereiht (salienz={salienz:.2f})")
    return True
