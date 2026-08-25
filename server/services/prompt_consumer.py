"""
Prompt-Consumer — nimmt Bloecke aus der Eingangs-Queue und faehrt Pfad 1.

**Was hier gewonnen wird.** Der HumanGraph-Lauf steckte bisher im
Anfragepfad: Der POST blockierte, bis Perzeption und Salienz durch waren — bei
belegter GPU bis zu 104 Sekunden (gemessen am 01.08.2026). Jetzt nimmt der
Endpunkt nur an und bestaetigt; hier laeuft, was Zeit braucht.

**Und der Block wird als Ganzes perzipiert.** Mehrere Aeusserungen, die
innerhalb des Fensters eintrafen, sind ein Prompt — mit **einer** Perzeption,
**einer** Salienz und **einem** Satz Intentionen fuer das, was der Nutzer
tatsaechlich gesagt hat. Vorher wurde je Aeusserung gemessen und beim
Zusammenfassen alles bis auf eine Messung verworfen.

Die Stufen von Pfad 1 gehen als `character_stage` ueber den WebSocket. Der
SSE-Kanal traegt sie nicht mehr — er endet mit der Bestaetigung.
"""

import asyncio
import json
import logging
import time
import uuid

from api.websocket import broadcast_threadsafe
from config import ASSISTANT_USER_ID, llm_lock, redis_client, shutdown_event
from services.events import event_erzeugen, event_wartet
from services.prompt_eingang import (
    block_zu_prompt,
    naechster_block,
    turn_beenden,
    turn_beginnen,
)
from services.shadow_delivery import shadow_burst_reset
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.prompt_consumer")

# Sekunden zwischen zwei Blicken in die Eingangs-Queues. Es wird **nicht**
# gewartet, ob noch etwas nachkommt: Der Block ist, was beim Hinsehen da liegt.
POLL_INTERVAL: float = 1.0

# Beschriftung der Pfad-1-Stufen fuer die Anzeige. Dieselben Schluessel wie
# `NODE_LABELS` in `api/chat.py`, wo sie fuer den SSE-Kanal standen.
STUFEN_LABELS: dict[str, str] = {
    "perzeption": "Perzeption — Wahrnehmung",
    "enricher":   "Enricher — Kontext laden",
    "ei_calc":    "EI-Calc — Emotionale Intelligenz",
    "salience":   "Salienz — Bewertung",
    "dispatcher": "Dispatcher — Speichern",
}


def _audit_log(user_id: str, status: str, ergebnis: str) -> None:
    """Schreibt einen `hintergrund_log`-Eintrag (Audit-Pflicht).

    Failsafe: Bei einem Datenbankfehler nur `logger.critical`, kein
    Wiederholungsversuch — sonst droht Endlos-Rekursion bei kaputter
    Audit-Senke. Muster wie `ziel_decay`.
    """
    try:
        db_manager.execute(
            """
            INSERT INTO hintergrund_log
                (user_id, aufgabe, status, ergebnis, verarbeitet_am)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (user_id, "prompt_block", status, ergebnis),
        )
    except Exception as fehler:
        logger.critical(
            f"hintergrund_log-INSERT fehlgeschlagen: {fehler} "
            f"(verlorener Audit-Eintrag: prompt_block/{status}/{ergebnis[:100]})",
            exc_info=True,
        )


def _stufe_senden(
    user_id:      str,
    character_id: str,
    node_name:    str,
    detail:       str,
    loop:         asyncio.AbstractEventLoop,
) -> None:
    """Meldet eine Pfad-1-Stufe an die Clients.

    Derselbe Nachrichtentyp wie die Stufen des CharacterGraph — der Client
    unterscheidet sie nicht, und er muss es auch nicht: Fuer ihn ist es eine
    Verarbeitung.
    """
    nutzlast: str = json.dumps({
        "typ":    "character_stage",
        "node":   node_name,
        "label":  STUFEN_LABELS.get(node_name, node_name),
        "detail": detail,
    }, ensure_ascii=False)

    broadcast_threadsafe(user_id, nutzlast, loop, character_id=character_id)


def _pfad1_fahren(
    conversation_graph: object,
    zustand: dict,
    kopf:    tuple[str, str],
    loop:    asyncio.AbstractEventLoop,
) -> tuple[dict, str]:
    """Faehrt den HumanGraph und meldet jede Stufe an die Clients.

    Laeuft in einem eigenen Thread (`asyncio.to_thread`) — der Graph ist
    blockierend, und der Loop bedient alle Nutzer.

    Vorbedingung: `zustand` ist ein frischer Pfad-1-State.
    Nachbedingung: Der zuletzt erreichte Zustand und der Ausfalltext. Der
        Ausfalltext ist leer, wenn der Graph durchgelaufen ist.
    Fehlerfaelle: Ein Abbruch im Graphen wird zum Ausfalltext, nicht zur
        Ausnahme — das Ereignis muss danach trotzdem entstehen, sonst ist die
        Nutzeraeusserung verloren (novaberg-bugs.md -> PFAD1-TIMEOUT-TURNVERLUST).

    Returns:
        Der letzte Zustand und der Ausfalltext.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id, character_id = kopf

    # ── Verarbeitung ────────────────────────────
    from api.chat import _Pfad1Abbruch, _stage_detail, _stream_oder_abbruch

    letzter:  dict = zustand
    ausfall:  str  = ""

    for chunk in _stream_oder_abbruch(conversation_graph, zustand):
        if isinstance(chunk, _Pfad1Abbruch):
            ausfall = chunk.text
            logger.error(
                f"Prompt-Consumer: Pfad 1 abgebrochen ({chunk.text}) — das "
                f"Ereignis wird trotzdem erzeugt, damit der Turn nicht "
                f"verlorengeht (turn_id={zustand.get('turn_id', '?')})"
            )
            _stufe_senden(
                user_id, character_id, "perzeption",
                "Wahrnehmung unvollständig — die Antwort folgt trotzdem.", loop,
            )
            break

        # LangGraph liefert nach Subgraph-Return manchmal Listen statt Dicts.
        if not isinstance(chunk, dict):
            logger.debug(
                f"Prompt-Consumer: Nicht-Dict-Chunk uebersprungen "
                f"(Typ: {type(chunk).__name__})"
            )
            continue

        for node_name, node_state in chunk.items():
            _stufe_senden(
                user_id, character_id, node_name,
                _stage_detail(node_name, node_state), loop,
            )
            letzter = node_state

    # ── Ausgabe-Verifikation ────────────────────
    if letzter is zustand and not ausfall:
        logger.error(
            f"Prompt-Consumer: Pfad 1 lieferte keinen einzigen Knoten-Zustand "
            f"und meldete keinen Abbruch ({user_id}:{character_id}) — der "
            f"Eingangs-Zustand wird weitergereicht"
        )

    return letzter, ausfall


async def _block_verarbeiten(
    block:        list[dict],
    kopf:         tuple[str, str],
    turn_id:      str,
    human_graph:  object,
    conversation_graph: object,
) -> None:
    """Macht aus einem Block einen Pfad-1-Durchlauf und ein Ereignis.

    Vorbedingung: `block` ist nicht leer und enthaelt gueltige Eintraege.
        **Der Turn-Marker ist gesetzt** — er ist die Bedingung dafuer, dass der
        Block ueberhaupt genommen werden durfte, und er bleibt bis der
        CharacterGraph durch ist.
    Nachbedingung: Genau ein Ereignis in der Ereignis-Queue, und ein
        Audit-Eintrag mit `erledigt` oder `fehler`.
    Fehlerfaelle: Jede Ausnahme wird gefangen, auditiert und gemeldet — ein
        Fehlschlag kostet den Block, nicht den Loop
        Ein Fehlschlag kostet den Block, nicht den Loop.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id, character_id = kopf

    if not block:
        logger.error(f"Prompt-Consumer: leerer Block fuer {user_id}:{character_id}")
        return

    from api.chat import _ereignis_nutzlast

    prompt:       str  = block_zu_prompt(block)
    empfangen_am: float = block[0].get("empfangen_am", time.time())
    kennungen:    list[str] = [e.get("nachrichten_id", "") for e in block]

    _audit_log(
        user_id, "gestartet",
        f"{len(block)} Nachricht(en), {len(prompt)} Zeichen, turn_id={turn_id}",
    )

    # ── Verarbeitung ────────────────────────────
    try:
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        redis_client.set(f"last_activity:{user_id}", str(time.time()), ex=7200)
        shadow_burst_reset(redis_client, user_id)

        zustand: dict = human_graph.create_state(
            user_prompt  = prompt,
            user_id      = user_id,
            character_id = character_id,
            turn_id      = turn_id,
        )

        # **Kein `with llm_lock` hier.** Ein `threading.Lock` blockierend im
        # Event-Loop zu nehmen legt den gesamten Loop still — auch den
        # Event-Consumer, dessen `await` den Riegel freigeben wuerde. Genau so
        # entstand am 01.08.2026 ein Deadlock: Der Loop stand, und mit ihm
        # jede Logzeile. Der Riegel wird vom Waechter erworben, bevor er die
        # Queue anfasst, und im `finally` des Loops freigegeben.
        letzter, ausfall = await asyncio.to_thread(
            _pfad1_fahren, conversation_graph, zustand, kopf, loop,
        )

        nutzlast: dict = _ereignis_nutzlast(
            turn_id, empfangen_am, prompt, letzter, ausfall,
        )
        # Die Kennungen aller Aeusserungen, die dieser Turn beantwortet. Der
        # Client hat je Aeusserung eine Bestaetigung bekommen und haelt sie
        # offen, bis eine Antwort sie nennt.
        nutzlast["nachrichten_ids"] = kennungen

        event_erzeugen(
            redis_client = redis_client,
            user_id      = user_id,
            character_id = character_id,
            source       = "user",
            typ          = "message",
            payload      = nutzlast,
        )

        _nutzer_nachricht_verteilen(block, prompt, kopf, loop)

        redis_client.set(
            f"momentum:{user_id}", letzter.get("momentum", "mid"), ex=300,
        )

    except Exception as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Prompt-Consumer: Block gescheitert "
            f"({user_id}:{character_id}, turn_id={turn_id}) — die "
            f"Nutzeraeusserung ist verloren"
        )
        _audit_log(user_id, "fehler", f"{type(fehler).__name__}: {fehler}")
        # Ohne Ereignis kommt kein Event-Consumer vorbei, der den Marker
        # loeschen koennte — der Turn endet hier.
        turn_beenden(redis_client, user_id, character_id)
        return

    # ── Ausgabe-Verifikation ────────────────────
    _audit_log(
        user_id, "erledigt",
        f"Ereignis erzeugt, turn_id={turn_id}, "
        f"{len(kennungen)} Nachricht(en) beantwortet",
    )


def _nutzer_nachricht_verteilen(
    block:  list[dict],
    prompt: str,
    kopf:   tuple[str, str],
    loop:   asyncio.AbstractEventLoop,
) -> None:
    """Zeigt die Aeusserung auf den **anderen** Clients desselben Nutzers.

    Ausgeschlossen wird die Herkunft des Blocks — aber nur, wenn alle
    Aeusserungen von demselben Client kamen. Kamen sie von verschiedenen, gibt
    es keinen gemeinsamen Absender, den man ausschliessen koennte; dann sehen
    alle den Block.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id, character_id = kopf
    herkuenfte: set[str] = {e.get("client_id", "") for e in block}

    # ── Verarbeitung ────────────────────────────
    absender: str = herkuenfte.pop() if len(herkuenfte) == 1 else ""

    try:
        broadcast_threadsafe(
            user_id      = user_id,
            nachricht    = json.dumps({
                "typ":          "user_message",
                "nachricht":    prompt,
                "user_id":      user_id,
                "character_id": character_id,
            }, ensure_ascii=False),
            loop           = loop,
            character_id   = character_id,
            exclude_client = absender,
        )
    except Exception as fehler:
        # Ein misslungener Broadcast kostet eine Anzeige, nicht den Turn.
        logger.warning(
            f"Prompt-Consumer: User-Message-Broadcast fehlgeschlagen: {fehler}",
            exc_info=True,
        )


def _darf_nehmen(user_id: str, character_id: str, turn_id: str) -> bool:
    """Der Waechter — entscheidet, ob jetzt eingespeist werden darf.

    Zwei Bedingungen, und sie sagen **nicht** dasselbe:

    * **Der Turn-Marker** sagt, dass gerade nichts laeuft. Er umspannt den
      ganzen Turn — Pfad 1 und CharacterGraph. Der Riegel um das Sprachmodell
      reicht dafuer nicht: Er wird zwischen beiden Haelften kurz frei, und in
      diesen Spalt geriet am 01.08.2026 ein zweiter Durchlauf, dessen
      Modellaufruf danach in eine Zeitueberschreitung lief.
    * **Die Ereignis-Queue** sagt, ob noch etwas *kommt*. Ein eigener Impuls
      loescht den Marker am Ende seines Durchlaufs — auch dann, wenn das
      Nutzer-Ereignis dahinter noch wartet. Dann steht der Marker frei und ein
      unfertiger Turn trotzdem aus.

    Gesetzt wird zuerst, geprueft danach: Ein Blick vor dem Setzen waere eine
    Momentaufnahme, die bis zum Setzen veraltet sein kann. Faellt die zweite
    Bedingung, wird der Marker sofort zurueckgegeben.

    Vorbedingung: `turn_id` ist nicht leer.
    Nachbedingung: Bei `True` sind **Riegel und Marker** erworben und gehoeren
        dem Aufrufer — er gibt beide zurueck. Bei `False` ist nichts veraendert.
    Fehlerfaelle: Keine — beide Ausgaenge sind Aussagen.

    Returns:
        Ob eingespeist werden darf.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Keine: `turn_beginnen` lehnt eine leere Kennung selbst ab und meldet.

    # ── Verarbeitung ────────────────────────────
    # Der Riegel zuerst, **nicht blockierend**. Er deckt ab, was der Marker
    # nicht kennt: den Pixie- und den Recherche-Pfad, die dasselbe Modell
    # benutzen. Ein blockierendes Warten waere hier toedlich — es liefe im
    # Event-Loop und legte den ganzen Dienst still.
    if not llm_lock.acquire(blocking=False):
        logger.debug(
            f"Prompt-Consumer: Riegel belegt ({user_id}:{character_id}) — "
            f"es wird nichts genommen"
        )
        return False

    if not turn_beginnen(redis_client, user_id, character_id, turn_id):
        llm_lock.release()
        return False

    if event_wartet(redis_client, user_id, character_id):
        logger.debug(
            f"Prompt-Consumer: ein Ereignis wartet noch auf seinen Durchlauf "
            f"({user_id}:{character_id}) — es wird nichts genommen"
        )
        turn_beenden(redis_client, user_id, character_id)
        llm_lock.release()
        return False

    # ── Ausgabe-Verifikation ────────────────────
    return True


async def prompt_consumer_loop(
    human_graph:        object,
    conversation_graph: object,
) -> None:
    """Endlos-Loop: nimmt Bloecke aus den Eingangs-Queues und faehrt Pfad 1.

    **Es wird nicht gewartet.** Der Block ist, was beim Hinsehen in der Queue
    liegt; was danach eintrifft, gehoert zum naechsten Durchlauf. Ein
    Ruhefenster waere eine Wartezeit auf jeder Antwort — und der Loop ist fuer
    alle Nutzer gemeinsam — ein langsamer Vorgang darf keinen schnellen aufhalten.

    Args:
        human_graph: HumanGraph-Instanz, fuer `create_state`.
        conversation_graph: Der kompilierte Pfad-1-Graph.
    """
    logger.info("Prompt-Consumer gestartet.")

    while True:
        try:
            await asyncio.sleep(POLL_INTERVAL)

            if shutdown_event.is_set():
                logger.info("Prompt-Consumer: Shutdown erkannt — beende Loop")
                break

            schluessel: list = redis_client.keys("prompt_queue:*")

            if not schluessel:
                continue

            for key in schluessel:
                key_str: str = key if isinstance(key, str) else key.decode()
                teile: list[str] = key_str.split(":")

                if len(teile) != 3:
                    logger.error(
                        f"Prompt-Consumer: unerwarteter Schluessel '{key_str}' — "
                        f"drei Teile erwartet, {len(teile)} gefunden"
                    )
                    continue

                _, user_id, character_id = teile
                character_id = character_id or ASSISTANT_USER_ID

                turn_id: str = uuid.uuid4().hex

                if not _darf_nehmen(user_id, character_id, turn_id):
                    continue

                # Ab hier gehoert der Riegel diesem Durchlauf. Er wird in
                # **jedem** Ausgang zurueckgegeben — ein gehaltener Riegel
                # legte jeden weiteren Modellaufruf still.
                try:
                    block: list[dict] = naechster_block(
                        redis_client, user_id, character_id,
                    )

                    if not block:
                        # Nichts zu tun — der Marker darf nicht stehenbleiben,
                        # sonst blockiert ein leerer Takt die naechste
                        # Aeusserung.
                        turn_beenden(redis_client, user_id, character_id)
                        continue

                    await _block_verarbeiten(
                        block, (user_id, character_id), turn_id,
                        human_graph, conversation_graph,
                    )
                finally:
                    llm_lock.release()

        except asyncio.CancelledError:
            logger.info("Prompt-Consumer beendet.")
            break

        except Exception as fehler:
            logger.exception(
                f"{type(fehler).__name__}: Prompt-Consumer: unerwarteter Fehler"
            )
            await asyncio.sleep(POLL_INTERVAL)
