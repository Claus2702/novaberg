"""Kandidaten-Sammlung fuer Pixie-Heartbeat.

Zwei Quellen:
  1. Queue-Peek: shadow_queue:{user_id} + queue:{user_id}
  2. Faellige periodische Aufgaben: pixie:schedule:*

Periodische Aufgaben altern: Je laenger eine faellige Aufgabe nicht laeuft,
desto hoeher ihre effektive Prioritaet (siehe _aging_zuschlag). Ohne das
gewinnt eine dauerhaft gefuellte Queue jeden Heartbeat, und Wartungslaeufe
mit niedriger Basis-Prioritaet laufen nie. Queue-Eintraege altern nicht.

Jeder Kandidat traegt beides: `prioritaet` ist der Wert, nach dem der
Scheduler waehlt, `prioritaet_basis` der ungealterte Ausgangswert. Wer nur
den ersten loggt, kann eine Wahl nicht mehr von ihrer Begruendung trennen.
"""

import json
import logging
import time

from config import (
    AKTIVES_PAAR_USER_ID,
    ASSISTANT_USER_ID,
    PIXIE_AGING_MAX_ZUSCHLAG,
    PIXIE_AGING_PRO_STUNDE,
    redis_client,
)

logger = logging.getLogger("ki_server.pixie")


def kandidaten_sammeln() -> list[dict]:
    """Sammelt Kandidaten aus Queue-Peek und faelligen periodischen Aufgaben.

    Rueckgabe: Liste von Kandidaten-Dicts mit:
        - name: str
        - prioritaet: float (effektiv — bei periodischen Aufgaben gealtert)
        - prioritaet_basis: float (ungealtert, fuer die Begruendung im Log)
        - ueberfaellig_s: float | None (None = Queue-Eintrag, altert nicht)
        - quelle: "queue" | "periodisch"
        - daten: dict
        - queue_key: str | None
        - queue_raw: bytes | None (fuer exaktes LREM)
        - schedule_key: str | None
        - themen: str
    """
    kandidaten: list[dict] = []

    # Quelle 1: Queue-Peek
    for user_id in _aktive_user_ids():
        queue_kandidat = _queue_peek(user_id)
        if queue_kandidat:
            kandidaten.append(queue_kandidat)

    # Quelle 2: Faellige periodische Aufgaben
    kandidaten.extend(_periodische_faellig())

    return kandidaten


def _aktive_user_ids() -> list[str]:
    """Gibt die beiden Seiten des konfigurierten Paares zurueck.

    Bis Chat 125 war das jeder Nutzer mit `last_activity` in Redis (TTL 2h).
    Damit bediente Pixie jeden, der zufaellig in den letzten zwei Stunden
    geschrieben hatte — bei einer Messreihe also die Testperson **und** den
    produktiven Nutzer, mit einem einzigen Heartbeat fuer beide.

    Jetzt entscheidet die Konfiguration (`AKTIVES_PAAR_USER_ID`), und der Lauf
    ist damit in sich geschlossen: Was in den Queues anderer Paare liegt,
    bleibt liegen, bis sie an der Reihe sind. Verloren geht dabei nichts — die
    Auftraege stehen in Redis, und die KZG-TTL reicht von sieben bis dreissig
    Tagen.

    **Beide Seiten**, weil das Paar zwei Subjekte hat: Der Mensch traegt seine
    Auftraege unter `queue:{mensch}`, Novas eigene Erkenntnisse liegen unter
    `queue:nova`. Wer nur die Menschenseite bedient, laesst Novas Selbstbild
    stehen.

    Nachbedingung: Ein bis zwei Kennungen, ohne Dubletten, keine leere.
    """
    seiten: list[str] = [AKTIVES_PAAR_USER_ID, ASSISTANT_USER_ID]

    # ── Ausgabe-Verifikation ────────────────────
    aktive: list[str] = []
    for kennung in seiten:
        if kennung and kennung not in aktive:
            aktive.append(kennung)

    if not aktive:
        logger.error(
            "Pixie: kein aktives Paar konfiguriert — AKTIVES_PAAR_USER_ID und "
            "ASSISTANT_USER_ID sind beide leer, kein Queue-Kandidat wird gesammelt"
        )

    return aktive


def _queue_peek(user_id: str) -> dict | None:
    """Peek auf shadow_queue und queue (Promotion) fuer einen User.

    Gibt den Eintrag mit der hoechsten Prioritaet zurueck, ohne ihn zu entfernen.
    """
    bester: dict | None = None
    beste_prio: float = -1.0

    for queue_key in [f"shadow_queue:{user_id}", f"queue:{user_id}"]:
        eintraege = redis_client.lrange(queue_key, 0, -1)

        for raw in eintraege:
            try:
                eintrag = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue

            prio: float = float(eintrag.get("prioritaet", eintrag.get("salienz", 0.0)))

            if prio > beste_prio:
                beste_prio = prio
                bester = {
                    "name": eintrag.get("aufgabe", "unbekannt"),
                    "prioritaet": prio,
                    # Queue-Eintraege altern nicht: basis == effektiv, und
                    # None statt 0.0, weil "altert nicht" etwas anderes ist
                    # als "ist gerade eben faellig geworden".
                    "prioritaet_basis": prio,
                    "ueberfaellig_s": None,
                    "quelle": "queue",
                    "daten": eintrag,
                    "queue_key": queue_key,
                    "queue_raw": raw,
                    "schedule_key": None,
                    "themen": eintrag.get("themen", ""),
                }

    return bester


def _aging_zuschlag(ueberfaellig_s: float, name: str) -> float:
    """Berechnet den Prioritaets-Zuschlag einer wartenden periodischen Aufgabe.

    Zweck: Verhungerungsschutz. Eine Aufgabe mit niedriger Basis-Prioritaet
    kommt sonst nie an die Reihe, solange hoeher priorisierte Kandidaten
    nachlaufen — der Scheduler waehlt allein nach dem Maximum.

    Der Massstab ist die ABSOLUTE Wartezeit, nicht die Zahl verpasster
    Intervalle. Waere er relativ, alterte eine Aufgabe mit Fuenf-Minuten-Takt
    288-mal schneller als eine taegliche und saesse dauerhaft am Deckel.

    Formel: min(MAX_ZUSCHLAG, PRO_STUNDE x ueberfaellig_s / 3600)

    Vorbedingung: ueberfaellig_s >= 0 (der Aufrufer ruft nur fuer faellige).
    Nachbedingung: Rueckgabe in [0.0, PIXIE_AGING_MAX_ZUSCHLAG].
    Fehlerfaelle: negative Wartezeit -> Zuschlag 0.0, laut protokolliert. Die
    Aufgabe bleibt Kandidat, sie altert nur nicht — ein stiller Ausschluss
    waere hier der schlimmere Fehler.
    """
    # ── Eingabe-Validierung ─────────────────────
    if ueberfaellig_s < 0:
        logger.error(
            f"Pixie-Aging: '{name}' meldet Wartezeit {ueberfaellig_s:.1f}s — "
            f"negativ, also noch nicht faellig; kein Zuschlag"
        )
        return 0.0

    # ── Verarbeitung ────────────────────────────
    stunden:  float = ueberfaellig_s / 3600.0
    zuschlag: float = min(PIXIE_AGING_MAX_ZUSCHLAG, PIXIE_AGING_PRO_STUNDE * stunden)

    # ── Ausgabe-Verifikation ────────────────────
    if zuschlag < 0.0 or zuschlag != zuschlag:  # NaN faengt sich selbst nicht ein
        logger.error(
            f"Pixie-Aging: '{name}' ergab unplausiblen Zuschlag {zuschlag} "
            f"(Wartezeit {ueberfaellig_s:.1f}s) — auf 0.0 gesetzt"
        )
        return 0.0

    return zuschlag


def _periodische_faellig() -> list[dict]:
    """Sammelt alle faelligen periodischen Aufgaben aus Redis.

    Redis-Keys: pixie:schedule:{agent_name} -> Hash mit priority, interval, next_run, description
    """
    jetzt: float = time.time()
    faellige: list[dict] = []

    for key in redis_client.scan_iter(match="pixie:schedule:*"):
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        daten = redis_client.hgetall(key)
        if not daten:
            continue

        # Byte-Keys decodieren
        if daten and isinstance(list(daten.keys())[0], bytes):
            daten = {
                k.decode(): v.decode() if isinstance(v, bytes) else v
                for k, v in daten.items()
            }

        next_run: float = float(daten.get("next_run", 0))

        if next_run <= jetzt:
            agent_name: str = key.split(":")[-1]

            basis:          float = float(daten.get("priority", 0.0))
            ueberfaellig_s: float = jetzt - next_run
            zuschlag:       float = _aging_zuschlag(ueberfaellig_s, agent_name)
            effektiv:       float = basis + zuschlag

            if zuschlag > 0.0:
                logger.debug(
                    f"Pixie-Aging: {agent_name} wartet {ueberfaellig_s / 3600.0:.2f}h, "
                    f"Prioritaet {basis:.2f} -> {effektiv:.2f}"
                )

            faellige.append({
                "name": daten.get("description", agent_name),
                "prioritaet": effektiv,
                "prioritaet_basis": basis,
                "ueberfaellig_s": ueberfaellig_s,
                "quelle": "periodisch",
                "daten": daten,
                "queue_key": None,
                "queue_raw": None,
                "schedule_key": key,
                "themen": "",
            })

    return faellige
