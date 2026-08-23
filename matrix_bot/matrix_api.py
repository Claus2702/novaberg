"""Die Client-Server-API des Homeservers, so weit der Connector sie braucht.

**Der ganze Unterschied zu einem Bot steht in einer Zeile:** `?user_id=` an
jeder Anfrage. Der Application Service weist sich mit seinem `as_token` aus
und nennt dabei, in wessen Namen er spricht. Der Homeserver prueft nur, ob
die Kennung in seinem Namensraum liegt — und schreibt den Absender ins
Event.

Ohne diesen Parameter waere der Connector ein Bot mit einem Absender, und
die `[Du]`-Kruecke aus dem Telegram-Kanal waere zurueck.
"""

import logging
from typing import Any

import httpx

from config import (
    MATRIX_AS_TOKEN,
    MATRIX_HOMESERVER,
    MATRIX_SERVER_NAME,
)
from formatierung import inhalt_bauen

logger = logging.getLogger("nova.matrix.api")

#: Die Client-Server-API in der Fassung, gegen die gebaut ist.
API: str = "/_matrix/client/v3"


def kennung(localpart: str) -> str:
    """Baut eine vollstaendige Matrix-Kennung aus dem lokalen Teil.

    Vorbedingung: `localpart` ist nicht leer und traegt kein `@` und kein `:`.
    Nachbedingung: `@localpart:servername`.
    Fehlerfaelle: leerer oder bereits vollstaendiger Eingabewert (ValueError).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not localpart or not localpart.strip():
        raise ValueError("kennung: leerer lokaler Teil")
    if localpart.startswith("@") or ":" in localpart:
        raise ValueError(f"kennung: {localpart!r} ist bereits vollstaendig")

    # ── Ausgabe ─────────────────────────────────
    return f"@{localpart.strip()}:{MATRIX_SERVER_NAME}"


class MatrixFehler(RuntimeError):
    """Der Homeserver hat eine Anfrage abgelehnt.

    Traegt den Statuscode und den Fehlercode der Matrix-API, weil die beiden
    zusammen sagen, was zu tun ist: `M_EXCLUSIVE` heisst falscher Namensraum,
    `M_FORBIDDEN` falscher Token, `M_UNKNOWN_TOKEN` gar keiner.
    """

    def __init__(self, status: int, code: str, meldung: str) -> None:
        self.status = status
        self.code = code
        super().__init__(f"[{status}/{code}] {meldung}")


class MatrixClient:
    """Ein Application Service als Client — mit wechselndem Absender."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Vorbedingung: `MATRIX_AS_TOKEN` ist gesetzt.

        Fehlerfaelle: fehlender Token (ValueError) — ohne ihn ist jede
        Anfrage ein 401, und der Grund waere im Log nicht ablesbar.
        """
        if not MATRIX_AS_TOKEN:
            raise ValueError(
                "MatrixClient: MATRIX_AS_TOKEN ist leer — der Connector kann "
                "sich beim Homeserver nicht ausweisen"
            )
        self._client = client

    async def _ruf(
        self, methode: str, pfad: str, *,
        als: str | None = None,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Fuehrt eine Anfrage gegen die Client-Server-API aus.

        Args:
            methode: HTTP-Methode.
            pfad:    Pfad unterhalb von `API`, mit fuehrendem Schraegstrich.
            als:     Vollstaendige Kennung, in deren Namen gesprochen wird.
                     **Das ist der Kern des Ganzen** — ohne sie spricht der
                     Dienstnutzer des AS.
            json:    Rumpf.
            params:  weitere Abfrageparameter.

        Nachbedingung: Der geparste Rumpf der Antwort.
        Fehlerfaelle: jeder Statuscode ab 400 wird zu `MatrixFehler` — laut
        und mit dem Code der Matrix-API, nicht als leeres Ergebnis.
        """
        # ── Verarbeitung ────────────────────────
        abfrage: dict = dict(params or {})
        if als:
            abfrage["user_id"] = als

        antwort = await self._client.request(
            methode,
            f"{MATRIX_HOMESERVER}{API}{pfad}",
            headers={"Authorization": f"Bearer {MATRIX_AS_TOKEN}"},
            params=abfrage,
            json=json,
        )

        # ── Ausgabe-Verifikation ────────────────
        if antwort.status_code >= 400:
            try:
                fehler: dict = antwort.json()
            except Exception:
                fehler = {}
            raise MatrixFehler(
                antwort.status_code,
                fehler.get("errcode", "?"),
                fehler.get("error", antwort.text[:200]),
            )

        return antwort.json() if antwort.content else {}

    # ── Was der Connector wirklich braucht ──────

    async def wer_bin_ich(self, als: str | None = None) -> str:
        """Fragt den Homeserver, als wen er die Anfrage liest.

        **Die Probe, die den Puppeting-Weg belegt.** Sie kostet einen Aufruf
        und beantwortet die Frage, die sonst erst am ersten Event auffaellt:
        ob der Namensraum den gewuenschten Absender deckt.
        """
        antwort = await self._ruf("GET", "/account/whoami", als=als)
        return antwort.get("user_id", "")

    async def raum_anlegen(self, *, als: str, name: str, einladen: list[str]) -> str:
        """Legt einen Raum an und laedt die genannten Kennungen ein.

        Nachbedingung: Die Raum-Kennung. Der Raum ist **unverschluesselt** —
        ein Application Service kann in einem E2EE-Raum nicht ohne
        Geraeteschluessel senden (Konzept §5).
        """
        antwort = await self._ruf("POST", "/createRoom", als=als, json={
            "name": name,
            "preset": "private_chat",
            "invite": einladen,
            "is_direct": False,
        })
        raum: str = antwort.get("room_id", "")
        if not raum:
            raise MatrixFehler(200, "?", "createRoom lieferte keine room_id")
        logger.info("Raum angelegt: %s (%s)", raum, name)
        return raum

    async def beitreten(self, raum: str, *, als: str) -> None:
        """Tritt einem Raum bei — im Namen der genannten Kennung."""
        await self._ruf("POST", f"/rooms/{raum}/join", als=als)
        logger.info("%s ist %s beigetreten", als, raum)

    async def senden(self, raum: str, text: str, *, als: str, txn: str) -> str:
        """Sendet eine Textnachricht — **im Namen von `als`**.

        Der Text geht als Markdown in `body` und, wo er Auszeichnungen
        traegt, zusaetzlich als HTML in `formatted_body`. Ohne das zweite
        Feld zeigt ein Client die Markdown-Zeichen woertlich.

        Vorbedingung: `als` liegt im Namensraum des Application Service,
        sonst lehnt der Homeserver mit `M_EXCLUSIVE` ab.
        Nachbedingung: Die Event-Kennung.

        Args:
            txn: Vorgangskennung. Sie macht das Senden wiederholbar, ohne
                 zu verdoppeln — derselbe Wert liefert dasselbe Event.
        """
        # ── Eingabe-Validierung ─────────────────
        if not text or not text.strip():
            raise ValueError("senden: leerer Text — es gibt nichts zu senden")

        antwort = await self._ruf(
            "PUT", f"/rooms/{raum}/send/m.room.message/{txn}", als=als,
            json=inhalt_bauen(text),
        )
        return antwort.get("event_id", "")

    # ── Das Profil der Figur ────────────────────

    async def profil(self, *, als: str) -> dict[str, str]:
        """Liest Anzeigename und Bild einer Kennung.

        Nachbedingung: Die vorhandenen Felder; fehlende fehlen auch im
        Ergebnis. Ein Profil ohne Bild ist kein Fehler, sondern der Zustand
        vor dem ersten Setzen.
        """
        return await self._ruf("GET", f"/profile/{als}")

    async def anzeigename_setzen(self, name: str, *, als: str) -> None:
        """Setzt den Anzeigenamen.

        Ohne ihn zeigt ein Client den lokalen Teil der Kennung — also die
        Kleinschreibung des Kontonamens, nicht den Namen der Figur.
        """
        if not name or not name.strip():
            raise ValueError("anzeigename_setzen: leerer Name")
        await self._ruf("PUT", f"/profile/{als}/displayname", als=als,
                        json={"displayname": name})
        logger.info("Anzeigename von %s auf %r gesetzt", als, name)

    async def bild_hochladen(self, daten: bytes, *, als: str, name: str) -> str:
        """Legt ein Bild im Medienspeicher ab und liefert seine `mxc:`-Adresse.

        **Der Medienspeicher liegt nicht unter der Client-Server-API**, deshalb
        geht dieser Aufruf an der gemeinsamen Methode vorbei.

        Vorbedingung: `daten` ist ein PNG.
        Nachbedingung: Eine `mxc://`-Adresse, dauerhaft und je Aufruf neu —
        **derselbe Inhalt zweimal hochgeladen ergibt zwei Objekte.** Wer bei
        jedem Start hochlaedt, fuellt den Speicher mit Kopien.
        """
        if not daten:
            raise ValueError("bild_hochladen: leere Daten")

        antwort = await self._client.post(
            f"{MATRIX_HOMESERVER}/_matrix/media/v3/upload",
            headers={
                "Authorization": f"Bearer {MATRIX_AS_TOKEN}",
                "Content-Type": "image/png",
            },
            params={"filename": name, "user_id": als},
            content=daten,
        )
        if antwort.status_code >= 400:
            try:
                fehler: dict = antwort.json()
            except Exception:
                fehler = {}
            raise MatrixFehler(antwort.status_code, fehler.get("errcode", "?"),
                               fehler.get("error", antwort.text[:200]))

        adresse: str = antwort.json().get("content_uri", "")
        if not adresse:
            raise MatrixFehler(200, "?", "upload lieferte keine content_uri")
        logger.info("Bild hochgeladen: %s", adresse)
        return adresse

    async def bild_setzen(self, mxc: str, *, als: str) -> None:
        """Haengt ein bereits hochgeladenes Bild an ein Profil."""
        if not mxc.startswith("mxc://"):
            raise ValueError(f"bild_setzen: {mxc!r} ist keine mxc-Adresse")
        await self._ruf("PUT", f"/profile/{als}/avatar_url", als=als,
                        json={"avatar_url": mxc})
        logger.info("Profilbild von %s gesetzt: %s", als, mxc)

    async def raeume(self, *, als: str) -> list[str]:
        """Liefert die Raeume, in denen die Kennung Mitglied ist."""
        antwort = await self._ruf("GET", "/joined_rooms", als=als)
        return list(antwort.get("joined_rooms", []))
