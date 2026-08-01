"""
Eingangs-Queue vor dem HumanGraph — Nachrichten annehmen und zu Bloecken schneiden.

**Warum vor dem HumanGraph und nicht danach.** Die Ereignis-Queue liegt hinter
Pfad 1, und Pfad 1 haelt den `llm_lock`: Eine zweite Nachricht wartet dort, bis
der laufende Durchlauf fertig ist. Ihr Ereignis entsteht erst danach, mit rund
zehn Sekunden Abstand zum ersten. Gemessen am 01.08.2026: 11 bis 13 Sekunden
bei freiem System, 104 Sekunden waehrend eines Charakter-Laufs.

**In der Ereignis-Queue liegt deshalb praktisch nie mehr als ein Nutzer-Reiz** —
sie entstehen nicht waehrend eines Laufs, sondern strikt nacheinander nach ihm.
Eine Zusammenfassung dort kann nicht greifen.

Hier greift sie, weil das Einreihen eine Redis-Operation ist und kein
Modellaufruf: Was waehrend eines Laufs eintrifft, liegt tatsaechlich vor, wenn
der naechste Durchlauf beginnt.

**Der Block wird als Ganzes perzipiert.** Das ist der eigentliche Gewinn: Es
gibt eine Perzeption, eine Salienz und einen Satz Intentionen fuer das, was der
Nutzer gesagt hat — statt mehrerer Messungen, von denen eine gewinnt und die
uebrigen weggeworfen werden.
"""

import json
import logging
import uuid
from dataclasses import dataclass

import redis

logger = logging.getLogger("ki_server.prompt_eingang")


@dataclass
class EingehendeNachricht:
    """Eine Nutzeraeusserung, wie sie am Endpunkt eintrifft.

    Reiner Datencontainer. Die drei Felder stammen aus demselben Vorgang und
    werden zusammen erzeugt, weitergereicht und abgelegt — ohne den
    Zeitstempel ist der Text nicht einzuordnen, ohne die Herkunft nicht
    zuzustellen. Zusammenhaengende Werte gehoeren in eine Klasse, nicht in
    eine Reihe flacher Argumente.

    Attributes:
        prompt: Der Text der Aeusserung. Leer ist unzulaessig und wird beim
            Einreihen abgelehnt.
        empfangen_am: Zeitpunkt des Eintreffens als Unix-Zeit, **vor** jeder
            Verarbeitung genommen. Nicht der Zeitpunkt des Einreihens: Zwischen
            beiden liegt bei belegter GPU bis zu eine Minute.
        client_id: Herkunft der Aeusserung — z.B. "desktop" oder "telegram".
            Leer heisst unbekannt und schliesst niemanden vom Broadcast aus.
    """

    prompt:       str
    empfangen_am: float
    client_id:    str = ""


# ─────────────────────────────────────────────
# Konstanten
# ─────────────────────────────────────────────
# Nachrichten, die hoechstens so weit auseinander eintrafen, gehoeren zu
# demselben Prompt. Gemessen wird der Abstand zum unmittelbaren Vorgaenger,
# nicht zum Beginn des Blocks: Eine Kette aus kurzen Abstaenden ist ein
# zusammenhaengender Gedanke, auch wenn ihr erstes und letztes Glied weit
# auseinanderliegen.
EINGANG_FENSTER: float = 30.0

# Lebensdauer einer unverarbeiteten Eingangs-Queue. Sie ist grosszuegig
# bemessen: Der Verfall ist eine Notbremse gegen verwaiste Schluessel, keine
# Frist fuer den Nutzer.
EINGANG_TTL: int = 3600


def _queue_key(user_id: str, character_id: str) -> str:
    """Schluessel der Eingangs-Queue eines Paares."""
    return f"prompt_queue:{user_id}:{character_id}"


def nachricht_einreihen(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    nachricht:    EingehendeNachricht,
) -> str:
    """Legt eine eingetroffene Nutzeraeusserung in die Eingangs-Queue.

    Der Aufrufer ist der Anfragepfad. Er rechnet nicht und ruft kein Modell —
    er nimmt an, stempelt und reiht ein. Alles Weitere geschieht im Consumer
    — der Anfragepfad wartet auf kein Ergebnis, das im Hintergrund entsteht,
    sonst entstuende ein Wartezustand ohne Zeitschranke.

    Vorbedingung: `prompt` ist nicht leer. Eine leere Aeusserung hat nichts,
        was zusammengefasst oder beantwortet werden koennte.
    Nachbedingung: Die Queue ist um genau einen Eintrag laenger, und der
        Eintrag traegt eine eigene Kennung.
    Fehlerfaelle: Leerer Prompt — `logger.error`, keine Einreihung, leere
        Kennung zurueck.

    Args:
        redis_client: Redis-Verbindung.
        user_id: Kennung des Nutzers.
        character_id: Kennung des Gegenuebers.
        nachricht: Die eingetroffene Aeusserung mit Text, Empfangszeit und
            Herkunft.

    Returns:
        Die Kennung der Nachricht, oder eine leere Zeichenkette bei
        verletzter Vorbedingung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not nachricht.prompt or not nachricht.prompt.strip():
        logger.error(
            f"Prompt-Eingang: leere Aeusserung abgelehnt "
            f"({user_id}:{character_id}, "
            f"client={nachricht.client_id or 'unbekannt'})"
        )
        return ""

    # ── Verarbeitung ────────────────────────────
    nachrichten_id: str = uuid.uuid4().hex

    eintrag: dict = {
        "nachrichten_id": nachrichten_id,
        "prompt":         nachricht.prompt,
        "empfangen_am":   nachricht.empfangen_am,
        "client_id":      nachricht.client_id,
    }

    key: str = _queue_key(user_id, character_id)
    laenge: int = redis_client.rpush(key, json.dumps(eintrag, ensure_ascii=False))

    if redis_client.ttl(key) < 0:
        redis_client.expire(key, EINGANG_TTL)

    # ── Ausgabe-Verifikation ────────────────────
    if not laenge:
        logger.error(
            f"Prompt-Eingang: rpush meldete Laenge 0 fuer {key} — "
            f"die Nachricht ist nicht eingereiht"
        )
        return ""

    logger.info(
        f"Prompt-Eingang: Nachricht eingereiht "
        f"({len(nachricht.prompt)} Zeichen, "
        f"nachrichten_id={nachrichten_id}, Warteschlange={laenge})"
    )
    return nachrichten_id


def block_schneiden(
    nachrichten: list[dict],
    fenster:     float = EINGANG_FENSTER,
) -> list[dict]:
    """Schneidet die vorderste Gruppe zusammengehoeriger Nachrichten ab.

    Zwei Nachrichten gehoeren zusammen, wenn ihr Abstand **zum unmittelbaren
    Vorgaenger** hoechstens `fenster` betraegt. Die Kette endet bei der ersten
    groesseren Luecke; alles dahinter bleibt fuer den naechsten Durchlauf.

    Reine Funktion ohne Redis-Zugriff — sie ist die eigentliche Regel und
    deshalb einzeln pruefbar.

    Vorbedingung: `nachrichten` ist in Eingangsreihenfolge. Jeder Eintrag
        traegt `empfangen_am` als Zahl; ein Eintrag ohne verwertbaren
        Zeitstempel beendet den Block, statt ihn stillschweigend zu verlaengern.
    Nachbedingung: Das Ergebnis ist ein Praefix der Eingabe und bei nicht
        leerer Eingabe selbst nicht leer.
    Fehlerfaelle: Fehlender oder nicht numerischer Zeitstempel — `logger.error`
        und Schnitt an dieser Stelle.

    Args:
        nachrichten: Die wartenden Eintraege, aeltester zuerst.
        fenster: Groesster zulaessiger Abstand in Sekunden.

    Returns:
        Die vorderste Gruppe. Leere Eingabe ergibt eine leere Liste.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not nachrichten:
        return []

    # ── Verarbeitung ────────────────────────────
    block:   list[dict] = [nachrichten[0]]
    vorher:  float      = _zeitstempel(nachrichten[0])

    if vorher is None:
        # Der erste Eintrag ohne Zeitstempel wird allein verarbeitet: Ohne
        # Bezugspunkt ist jede Zuordnung geraten.
        return block

    for eintrag in nachrichten[1:]:
        jetzt: float | None = _zeitstempel(eintrag)

        if jetzt is None or jetzt - vorher > fenster:
            break

        block.append(eintrag)
        vorher = jetzt

    # ── Ausgabe-Verifikation ────────────────────
    if not block:
        logger.error(
            f"Prompt-Eingang: leerer Block aus {len(nachrichten)} Nachrichten — "
            f"das darf nicht vorkommen, die erste gehoert immer dazu"
        )

    return block


def _zeitstempel(eintrag: dict) -> float | None:
    """Liest `empfangen_am` und meldet einen unbrauchbaren Wert laut.

    Vorbedingung: Keine.
    Nachbedingung: Eine Zahl oder None. None heisst "nicht verwertbar" und ist
        von einer echten 0.0 zu unterscheiden.
    Fehlerfaelle: Fehlender oder nicht numerischer Wert — `logger.error`.

    Returns:
        Der Zeitstempel oder None.
    """
    # ── Eingabe-Validierung ─────────────────────
    wert = eintrag.get("empfangen_am")

    if not isinstance(wert, (int, float)) or isinstance(wert, bool):
        logger.error(
            f"Prompt-Eingang: Nachricht ohne verwertbaren Zeitstempel "
            f"(nachrichten_id={eintrag.get('nachrichten_id', '?')}, "
            f"empfangen_am={wert!r}) — sie wird nicht zusammengefasst"
        )
        return None

    # ── Ausgabe-Verifikation ────────────────────
    return float(wert)


def naechster_block(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    fenster:      float = EINGANG_FENSTER,
) -> list[dict]:
    """Nimmt die vorderste Gruppe aus der Eingangs-Queue.

    Gelesen wird ohne zu entnehmen; entnommen wird erst, wenn der Schnitt
    feststeht. So liegt kein Eintrag in einem Moment nirgends — ein
    Zuruecklegen nach einem `lpop` haette genau dieses Fenster.

    **Es wird nicht gewartet.** Der Consumer nimmt, was da ist; was danach
    eintrifft, gehoert zum naechsten Durchlauf. Ein Ruhefenster waere eine
    Wartezeit auf jeder Antwort, und der Loop ist fuer alle Paare gemeinsam.

    Vorbedingung: Keine.
    Nachbedingung: Die Queue ist um genau so viele Eintraege kuerzer, wie
        zurueckgegeben werden.
    Fehlerfaelle: Unlesbarer JSON-Eintrag — `logger.error`, der Eintrag wird
        entfernt und nicht zurueckgegeben; die uebrigen bleiben unberuehrt.

    Args:
        redis_client: Redis-Verbindung.
        user_id: Kennung des Nutzers.
        character_id: Kennung des Gegenuebers.
        fenster: Groesster zulaessiger Abstand in Sekunden.

    Returns:
        Die Eintraege des Blocks, aeltester zuerst. Leer, wenn nichts wartet.
    """
    # ── Eingabe-Validierung ─────────────────────
    key: str = _queue_key(user_id, character_id)
    rohe: list = redis_client.lrange(key, 0, -1)

    if not rohe:
        return []

    # ── Verarbeitung ────────────────────────────
    nachrichten: list[dict] = []
    defekte:     int        = 0

    for roh in rohe:
        try:
            nachrichten.append(json.loads(roh))
        except (json.JSONDecodeError, TypeError):
            defekte += 1
            logger.exception(
                f"Prompt-Eingang: unlesbarer Eintrag in {key} — er wird "
                f"entfernt, die uebrigen bleiben"
            )
            nachrichten.append({})

    block: list[dict] = block_schneiden(nachrichten, fenster)

    for _ in range(len(block)):
        redis_client.lpop(key)

    gueltige: list[dict] = [e for e in block if e]

    # ── Ausgabe-Verifikation ────────────────────
    if defekte and not gueltige:
        logger.error(
            f"Prompt-Eingang: Block aus {len(block)} Eintraegen enthielt nur "
            f"unlesbare — nichts zu verarbeiten"
        )
        return []

    logger.info(
        f"Prompt-Eingang: Block mit {len(gueltige)} Nachricht(en) genommen "
        f"({user_id}:{character_id}, {len(rohe) - len(block)} bleiben)"
    )
    return gueltige


def block_zu_prompt(block: list[dict]) -> str:
    """Fuegt die Texte eines Blocks zu einem Prompt zusammen.

    Die Reihenfolge ist die des Eintreffens. Getrennt wird mit einem
    Zeilenumbruch — nicht mit einem Trennzeichen, das im Prompt wie eine
    Anweisung aussehen koennte.

    Vorbedingung: `block` enthaelt Eintraege mit `prompt`. Pruefung erfolgt
        beim Aufrufer (`naechster_block` gibt nur gueltige Eintraege zurueck).
    Nachbedingung: Eine Zeichenkette; leer nur bei leerem Block.
    Fehlerfaelle: Keine.

    Returns:
        Der zusammengefuegte Text.
    """
    # ── Eingabe-Validierung ─────────────────────
    # Keine: siehe Vorbedingung.

    # ── Verarbeitung ────────────────────────────
    texte: list[str] = [e.get("prompt", "") for e in block]

    # ── Ausgabe-Verifikation ────────────────────
    return "\n".join(t for t in texte if t)


# Lebensdauer des Turn-Markers. Er ist eine Notbremse, keine Frist: Faellt ein
# Durchlauf so aus, dass niemand ihn loescht, gibt der Verfall die Eingabe
# wieder frei. Grosszuegig ueber der laengsten beobachteten Turn-Dauer (rund
# drei Minuten), damit er nie einen laufenden Turn ueberholt.
TURN_MARKER_TTL: int = 600


def _turn_key(user_id: str, character_id: str) -> str:
    """Schluessel des Turn-Markers eines Paares."""
    return f"turn_laeuft:{user_id}:{character_id}"


def turn_beginnen(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
    turn_id:      str,
) -> bool:
    """Meldet einen Turn als begonnen — oder scheitert, weil schon einer laeuft.

    **Der Marker umspannt den ganzen Turn**, nicht nur Pfad 1. Der `llm_lock`
    kann das nicht: Er wird zwischen Pfad 1 und dem CharacterGraph kurz frei,
    und in diesen Spalt geriet am 01.08.2026 ein zweiter Durchlauf — dessen
    Modellaufruf lief danach in einen Timeout und der Turn blieb ohne
    Perzeption.

    Gesetzt wird mit `NX`: Das Setzen und die Pruefung sind **eine** Operation,
    und Redis fuehrt sie atomar aus. Zwei Loops koennen sich deshalb nicht
    gegenseitig ueberholen.

    Geloescht wird von dem, der den Turn beendet — das ist der Event-Consumer
    nach dem CharacterGraph, nicht der Prompt-Consumer nach Pfad 1.

    Vorbedingung: `turn_id` ist nicht leer. Ein Marker ohne Kennung waere im
        Log nicht zuzuordnen.
    Nachbedingung: Bei `True` traegt der Schluessel die Kennung und einen
        Verfall; bei `False` ist nichts veraendert.
    Fehlerfaelle: Leere Kennung — `logger.error`, kein Marker, `False`.

    Returns:
        True, wenn dieser Aufrufer den Turn begonnen hat.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not turn_id:
        logger.error(
            f"Prompt-Eingang: turn_beginnen ohne turn_id "
            f"({user_id}:{character_id}) — kein Marker gesetzt"
        )
        return False

    # ── Verarbeitung ────────────────────────────
    gesetzt: bool = bool(redis_client.set(
        _turn_key(user_id, character_id), turn_id, nx=True, ex=TURN_MARKER_TTL,
    ))

    # ── Ausgabe-Verifikation ────────────────────
    if not gesetzt:
        logger.debug(
            f"Prompt-Eingang: Turn laeuft bereits ({user_id}:{character_id}) — "
            f"die Aeusserungen bleiben in der Queue"
        )

    return gesetzt


def turn_beenden(
    redis_client: redis.Redis,
    user_id:      str,
    character_id: str,
) -> None:
    """Gibt die Eingabe wieder frei — der Turn ist vollstaendig durch.

    Idempotent: Ein zweiter Aufruf ist folgenlos. Das ist Absicht, denn nicht
    jeder Durchlauf des Event-Consumers hat einen Marker gesetzt bekommen —
    ein eigener Impuls entsteht ohne Eingangs-Queue.

    Vorbedingung: Keine.
    Nachbedingung: Der Schluessel existiert nicht mehr.
    Fehlerfaelle: Keine.
    """
    # ── Eingabe-Validierung ─────────────────────
    key: str = _turn_key(user_id, character_id)

    # ── Verarbeitung ────────────────────────────
    entfernt: int = redis_client.delete(key)

    # ── Ausgabe-Verifikation ────────────────────
    if entfernt:
        logger.info(
            f"Prompt-Eingang: Turn beendet ({user_id}:{character_id}) — "
            f"die Eingabe ist wieder frei"
        )
