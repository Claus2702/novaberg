"""Matrix-Connector fuer Novaberg — ein Kanal mit zwei Absendern.

Drei nebenlaeufige Aufgaben:

1. **Ein HTTP-Dienst**, an den der Homeserver seine Ereignisse schiebt
   (`PUT /_matrix/app/v1/transactions/{txnId}`). Anders als der Telegram-Bot
   fragt dieser Connector nicht — er wird beliefert.
2. **Ein WebSocket-Zuhoerer** an Novaberg, wie beim Telegram-Bot.
3. **Der Aufbau des Raums** beim Start, damit beide Kennungen darin sitzen.

**Warum es diesen Kanal gibt, steht in einer Zeile Code:** `als=`. Der
Connector sendet Novas Antwort im Namen von `@nova` und die Aeusserung eines
anderen Clients im Namen von `@meister` — nicht als `[Du] ...` aus fremdem
Mund. Konzept: `docs/novaberg-matrix-kanal_k.md`.
"""

import asyncio
import json
import logging
import pathlib
import uuid

import httpx
import uvicorn
import websockets
from fastapi import FastAPI, HTTPException, Request

from config import (
    MATRIX_BOT_PORT,
    MATRIX_CHARACTER,
    MATRIX_HS_TOKEN,
    MATRIX_USER_MAP,
    NOVA_API_TIMEOUT,
    NOVA_API_URL,
    NOVA_CHARACTER_ID,
    RAUM_DATEI,
    WS_RECONNECT_DELAY,
)
from matrix_api import MatrixClient, MatrixFehler, kennung

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nova.matrix")

#: Der Client-Name, unter dem dieser Kanal bei Novaberg auftritt. Er
#: entscheidet, welche Aeusserungen zurueckgespiegelt werden: Der
#: Prompt-Consumer schliesst den Absender aus (`exclude_client`), sonst
#: saehe der Raum jede eigene Nachricht zweimal.
CLIENT_ID: str = "matrix"

#: Umgekehrte Zuordnung: Novaberg-Kennung -> lokaler Matrix-Teil.
NOVA_ZU_MATRIX: dict[str, str] = {
    nova_id: localpart for localpart, nova_id in MATRIX_USER_MAP.items()
}

#: Raum je Novaberg-Kennung, zur Laufzeit gefuellt.
RAEUME: dict[str, str] = {}

#: Ereignis-Kennungen, die dieser Connector selbst erzeugt hat.
#:
#: **Ohne sie laeuft der Kanal im Kreis.** Was der Connector im Namen von
#: `@meister` in den Raum stellt, kommt als Transaktion zurueck — und ginge
#: erneut an `POST /chat`. Die Menge ist begrenzt; sie haelt nur, was
#: gerade unterwegs ist.
EIGENE_EVENTS: set[str] = set()
EIGENE_EVENTS_MAX: int = 512

app = FastAPI(title="Novaberg Matrix-Connector")


# ─────────────────────────────────────────────
# Raumzustand
# ─────────────────────────────────────────────
def _raeume_laden() -> dict[str, str]:
    """Liest die bekannten Raeume von der Platte.

    Nachbedingung: Zuordnung Novaberg-Kennung -> Raum-Kennung; leer, wenn
    noch keiner angelegt wurde. Eine unlesbare Datei ist ein leerer Stand
    **mit Fehlerzeile** — nicht ein stiller Neuanfang, denn der wuerde einen
    zweiten Raum anlegen und den Verlauf des ersten zuruecklassen.
    """
    pfad = pathlib.Path(RAUM_DATEI)
    if not pfad.is_file():
        return {}
    try:
        return json.loads(pfad.read_text(encoding="utf-8"))
    except Exception as fehler:
        logger.error(
            "Raumstand %s ist unlesbar (%s) — es wird KEIN neuer Raum "
            "angelegt, damit der bestehende Verlauf nicht verwaist. Datei "
            "pruefen oder von Hand entfernen.", RAUM_DATEI, fehler,
        )
        raise


def _raeume_sichern(raeume: dict[str, str]) -> None:
    """Schreibt den Raumstand auf die Platte."""
    pfad = pathlib.Path(RAUM_DATEI)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(raeume, indent=2), encoding="utf-8")


async def _raum_sicherstellen(client: MatrixClient, nova_id: str) -> str:
    """Findet den Raum dieses Paares oder legt ihn an.

    Vorbedingung: `nova_id` steht in `MATRIX_USER_MAP`.
    Nachbedingung: Eine Raum-Kennung, in der **beide** Kennungen Mitglied
    sind — die des Menschen und die der Figur.

    **Der Raum wird von der Figur angelegt und der Mensch eingeladen**, nicht
    umgekehrt: Der Raum gehoert zum Kanal, nicht zur Sitzung eines Geraets.
    Ein Beitritt wird ausdruecklich ausgefuehrt und nicht der Einladung
    ueberlassen — eine offene Einladung ist kein Mitglied, und in einen Raum,
    den niemand betreten hat, kann auch niemand sprechen.
    """
    if nova_id in RAEUME:
        return RAEUME[nova_id]

    mensch: str = kennung(NOVA_ZU_MATRIX[nova_id])
    figur: str = kennung(MATRIX_CHARACTER)

    raum: str = await client.raum_anlegen(
        als=figur, name=f"Nova & {NOVA_ZU_MATRIX[nova_id]}", einladen=[mensch],
    )
    # Der Mensch tritt sofort bei — der AS darf das fuer ihn tun.
    await client.beitreten(raum, als=mensch)

    RAEUME[nova_id] = raum
    _raeume_sichern(RAEUME)
    return raum


# ─────────────────────────────────────────────
# Matrix -> Novaberg
# ─────────────────────────────────────────────
@app.put("/_matrix/app/v1/transactions/{txn_id}")
async def transaktion(txn_id: str, request: Request) -> dict:
    """Nimmt eine Ereignis-Lieferung des Homeservers entgegen.

    Vorbedingung: Der `hs_token` steht im Authorization-Header. **Eine
    Anfrage ohne ihn ist keine vom Homeserver** und wird mit 403 abgewiesen —
    der Dienst haengt in einem Netz, in dem auch anderes lauft.
    Nachbedingung: `{}` und Statuscode 200. Der Homeserver wiederholt eine
    Transaktion, die nicht mit 200 beantwortet wurde.

    **Quittiert wird auch, was uebergangen wird.** Ein Ereignis, das dieser
    Connector nicht braucht, ist kein Fehlschlag der Lieferung; wer es mit
    einem Fehler beantwortet, bekommt es fuer immer wieder.
    """
    # ── Eingabe-Validierung ─────────────────────
    kopf: str = request.headers.get("Authorization", "")
    if not MATRIX_HS_TOKEN or kopf != f"Bearer {MATRIX_HS_TOKEN}":
        logger.error("Transaktion %s ohne gueltigen hs_token — abgewiesen", txn_id)
        raise HTTPException(status_code=403, detail={"errcode": "M_FORBIDDEN"})

    rumpf: dict = await request.json()
    ereignisse: list[dict] = rumpf.get("events", [])

    # ── Verarbeitung ────────────────────────────
    for ereignis in ereignisse:
        try:
            await _ereignis_behandeln(ereignis)
        except Exception as fehler:
            # Ein einzelnes Ereignis darf die Lieferung nicht scheitern
            # lassen — sonst wiederholt der Homeserver den ganzen Stapel.
            logger.error(
                "Ereignis %s uebersprungen: %s",
                ereignis.get("event_id", "?"), fehler, exc_info=True,
            )

    return {}


async def _ereignis_behandeln(ereignis: dict) -> None:
    """Leitet eine Textnachricht des Menschen an Novaberg weiter.

    Uebergangen wird, was nicht hierher gehoert, und **jedes Uebergehen hat
    einen Grund im Log**: eigene Echos, andere Ereignistypen, unbekannte
    Absender.
    """
    typ: str = ereignis.get("type", "")
    if typ != "m.room.message":
        return

    event_id: str = ereignis.get("event_id", "")
    if event_id in EIGENE_EVENTS:
        # Was dieser Connector selbst gesendet hat, kommt hier zurueck.
        EIGENE_EVENTS.discard(event_id)
        logger.debug("Eigenes Echo %s uebergangen", event_id)
        return

    absender: str = ereignis.get("sender", "")
    localpart: str = absender.split(":", 1)[0].lstrip("@")

    if localpart == MATRIX_CHARACTER:
        return

    nova_id: str | None = MATRIX_USER_MAP.get(localpart)
    if nova_id is None:
        logger.warning("Unbekannte Matrix-Kennung: %s", absender)
        return

    inhalt: dict = ereignis.get("content", {})
    if inhalt.get("msgtype") != "m.text":
        logger.info("Nachricht von %s ist kein Text (%s) — uebergangen",
                    absender, inhalt.get("msgtype"))
        return

    text: str = inhalt.get("body", "")
    if not text.strip():
        return

    # Der Raum dieser Nachricht wird gemerkt: Er ist der, in dem geantwortet
    # wird, auch wenn der Stand auf der Platte einen anderen nennt.
    raum: str = ereignis.get("room_id", "")
    if raum and RAEUME.get(nova_id) != raum:
        RAEUME[nova_id] = raum
        _raeume_sichern(RAEUME)

    logger.info("[%s] Eingehend: %s", nova_id, text[:80])
    await _an_novaberg(nova_id, text)


async def _an_novaberg(nova_id: str, text: str) -> None:
    """Reicht die Aeusserung an `POST /chat` weiter — ohne auf Antwort zu warten.

    Die Antwort kommt ueber den WebSocket, nicht aus dieser Anfrage. Das ist
    dieselbe Bauart wie beim Telegram-Bot und derselbe Grund: Der Turn dauert
    laenger als jede vernuenftige HTTP-Frist.
    """
    try:
        async with httpx.AsyncClient(timeout=NOVA_API_TIMEOUT) as client:
            antwort = await client.post(
                f"{NOVA_API_URL}/chat",
                json={"prompt": text, "user_id": nova_id, "client_id": CLIENT_ID},
            )
            antwort.raise_for_status()
            logger.info("[%s] POST /chat angenommen", nova_id)
    except Exception as fehler:
        logger.error("[%s] POST /chat fehlgeschlagen: %s", nova_id, fehler)
        await _in_raum(nova_id, "Ich bin gerade nicht erreichbar.",
                       localpart=MATRIX_CHARACTER)


# ─────────────────────────────────────────────
# Novaberg -> Matrix
# ─────────────────────────────────────────────
async def _in_raum(nova_id: str, text: str, *, localpart: str) -> None:
    """Stellt einen Text in den Raum — im Namen der genannten Kennung.

    **Hier steht der Unterschied zum Telegram-Kanal.** `localpart` entscheidet,
    wer im Verlauf als Absender steht: die Figur bei ihrer Antwort, der Mensch
    bei einer Aeusserung, die er an einem anderen Client gemacht hat.
    """
    raum: str | None = RAEUME.get(nova_id)
    if not raum:
        logger.error("[%s] Kein Raum bekannt — Nachricht faellt aus", nova_id)
        return

    txn: str = uuid.uuid4().hex
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            client = MatrixClient(http)
            event_id: str = await client.senden(
                raum, text, als=kennung(localpart), txn=txn,
            )
        # Merken, damit das Echo der Transaktion nicht erneut eingespeist wird.
        EIGENE_EVENTS.add(event_id)
        if len(EIGENE_EVENTS) > EIGENE_EVENTS_MAX:
            EIGENE_EVENTS.pop()
        logger.info("[%s] Gesendet als @%s: %s", nova_id, localpart, text[:60])
    except MatrixFehler as fehler:
        logger.error("[%s] Senden als @%s scheiterte: %s", nova_id, localpart, fehler)


def absender_fuer(typ: str, mensch: str) -> str | None:
    """Entscheidet, wer eine Novaberg-Meldung im Raum sagt.

    **Das ist die eine Entscheidung, wegen der es diesen Kanal gibt**, und sie
    steht als eigene Funktion, damit ein Zeuge sie treffen kann. Inline in der
    Empfangsschleife waere sie nur ueber den ganzen WebSocket pruefbar — und
    ein Zeuge, der stattdessen den Sendeweg direkt aufruft, prueft die Wahl
    gar nicht. Genau so ist es beim Bau am 23.08.2026 passiert: Die Gegenprobe
    baute das `[Du]`-Praefix zurueck und **kein Test wurde rot**.

    Args:
        typ:    der `typ` der WebSocket-Meldung.
        mensch: lokaler Matrix-Teil des Menschen dieses Paares.

    Returns:
        Der lokale Teil der sendenden Kennung — oder `None`, wenn diese
        Meldung nicht in den Raum gehoert.
    """
    if typ in ("character_response", "shadow_delivery"):
        return MATRIX_CHARACTER
    if typ == "user_message":
        # Die Aeusserung stammt von einem anderen Client desselben Menschen.
        # Sie gehoert ihm, nicht der Figur — im Telegram-Kanal stand hier
        # `[Du] ...` aus Novas Mund, weil ein Bot nur sich selbst sagen kann.
        return mensch
    return None


async def websocket_zuhoerer(nova_id: str) -> None:
    """Haelt die Verbindung zu Novaberg und verteilt, was kommt.

    Drei Typen tragen, und **die Unterscheidung ist der Zweck dieses Kanals**:

    | Typ | Absender im Raum |
    |---|---|
    | `character_response` | die Figur |
    | `shadow_delivery` | die Figur |
    | `user_message` | **der Mensch** — hier stand im Telegram-Kanal `[Du] ...` |
    """
    ws_basis: str = NOVA_API_URL.replace("http://", "ws://").replace("https://", "wss://")
    url: str = (f"{ws_basis}/ws/{nova_id}"
                f"?client_id={CLIENT_ID}&character_id={NOVA_CHARACTER_ID}")
    mensch: str = NOVA_ZU_MATRIX[nova_id]

    while True:
        try:
            logger.info("[%s] WebSocket zu %s ...", nova_id, url)
            async with websockets.connect(url, ping_interval=30, ping_timeout=10) as ws:
                logger.info("[%s] WebSocket verbunden", nova_id)

                async for roh in ws:
                    try:
                        daten: dict = json.loads(roh)
                    except json.JSONDecodeError:
                        logger.warning("[%s] Ungueltiges JSON", nova_id)
                        continue

                    typ: str = daten.get("typ", "")
                    text: str = daten.get("nachricht", "")

                    localpart: str | None = absender_fuer(typ, mensch)
                    if localpart and text:
                        await _in_raum(nova_id, text, localpart=localpart)
                    elif localpart is None and typ not in (
                        "character_stage", "verbindung", "echo",
                    ):
                        logger.debug("[%s] Unbekannter Typ: %s", nova_id, typ)

        except Exception as fehler:
            logger.warning("[%s] WebSocket-Fehler: %s", nova_id, fehler)

        await asyncio.sleep(WS_RECONNECT_DELAY)


# ─────────────────────────────────────────────
# Start
# ─────────────────────────────────────────────
@app.on_event("startup")
async def starten() -> None:
    """Baut den Raum auf und startet je Mensch einen WebSocket-Zuhoerer.

    **Der Puppeting-Weg wird beim Start geprueft, nicht beim ersten Turn.**
    Ein `whoami` im Namen des Menschen kostet einen Aufruf und beantwortet
    die Frage, die sonst erst auffiele, wenn eine Nachricht ausbleibt.
    """
    RAEUME.update(_raeume_laden())

    async with httpx.AsyncClient(timeout=30.0) as http:
        client = MatrixClient(http)

        for localpart, nova_id in MATRIX_USER_MAP.items():
            wer: str = await client.wer_bin_ich(als=kennung(localpart))
            if wer != kennung(localpart):
                logger.error(
                    "Puppeting fuer %s liefert %r — der Namensraum des "
                    "Application Service deckt diese Kennung nicht",
                    kennung(localpart), wer,
                )
                continue
            logger.info("Puppeting geprueft: %s", wer)

            await _raum_sicherstellen(client, nova_id)
            asyncio.create_task(websocket_zuhoerer(nova_id))

    logger.info("Matrix-Connector bereit. Raeume: %s", RAEUME)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=MATRIX_BOT_PORT)
