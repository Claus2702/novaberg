"""Kandidaten-Sammlung fuer Pixie-Heartbeat.

Drei Quellen:
  1. Shadow-Queue: Tabelle `shadow_auftrag` (PostgreSQL, seit 15.08.2026)
  2. Promotions-Queue: queue:{user_id} (Redis)
  3. Faellige periodische Aufgaben: pixie:schedule:*

Periodische Aufgaben altern: Je laenger eine faellige Aufgabe nicht laeuft,
desto hoeher ihre effektive Prioritaet (siehe _aging_zuschlag). Ohne das
gewinnt eine dauerhaft gefuellte Queue jeden Heartbeat, und Wartungslaeufe
mit niedriger Basis-Prioritaet laufen nie.

**Zwei gegenlaeufige Zeitregeln, und beide sind fuer ihren Gegenstand
richtig.** Eine faellige Wartungsaufgabe wird dringlicher, je laenger sie
aussteht — ihre Prioritaet **steigt** mit der Wartezeit. Ein unerledigter
Auftrag der Shadow-Queue wird es nicht: Seine Salienz **faellt**, weil ein
Vorsatz seinen Anlass verliert (`novaberg-queue-verfall_k.md` §12.3). Die
Folge ist eine langsame Verschiebung zugunsten der Wartungsaufgaben; sie ist
gewollt und hier benannt, damit sie nicht spaeter als Defekt gemeldet wird.
Promotionsauftraege altern in keine Richtung.

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
    POSTGRES_URL,
    redis_client,
)
from memory.repositories.shadow_auftrag_repository import ShadowAuftragRepository

logger = logging.getLogger("ki_server.pixie")


def kandidaten_sammeln() -> list[dict]:
    """Sammelt Kandidaten aus Queue-Peek und faelligen periodischen Aufgaben.

    Rueckgabe: Liste von Kandidaten-Dicts mit:
        - name: str
        - prioritaet: float (effektiv — bei periodischen Aufgaben gealtert)
        - prioritaet_basis: float (ungealtert, fuer die Begruendung im Log)
        - ueberfaellig_s: float | None (None = Queue-Eintrag, altert nicht)
        - quelle: "shadow_auftrag" | "queue" | "periodisch"
        - daten: dict
        - auftrag_id: int | None (Primaerschluessel in shadow_auftrag)
        - queue_key: str | None (nur Promotions-Queue)
        - queue_raw: bytes | None (nur Promotions-Queue, fuer exaktes LREM)
        - schedule_key: str | None
        - themen: str
    """
    kandidaten: list[dict] = []

    # Quelle 1: Queue-Peek — je Queue ein Gewinner, nicht einer ueber beide.
    # Ein zusammengefasster Gewinner waere immer der Gespraechsauftrag und
    # die CPU-Spur bekaeme nie einen Kandidaten zu sehen (siehe _queue_peek).
    for user_id in _aktive_user_ids():
        kandidaten.extend(_queue_peek(user_id))

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


def _queue_peek(user_id: str) -> list[dict]:
    """Peek auf shadow_queue und queue (Promotion) — **je einen** Gewinner.

    **Je Queue einen, nicht einen ueber beide.** Bis zum 09.08.2026 faltete
    diese Funktion beide Listen auf einen einzigen besten Eintrag zusammen.
    Solange ein Scheduler daraus einen Agenten waehlte, war das richtig; mit
    den zwei Spuren wurde es zum Defekt:

    Die Gespraechsauftraege in `shadow_queue` tragen 0,94 bis 1,00, die
    Promotionsauftraege in `queue` ihre Salienz. Der Gesamtsieger war damit
    **immer** ein Gespraechsauftrag — also immer ein Kandidat der LLM-Spur.
    Die CPU-Spur bekam nie einen zu sehen und meldete "Keine Kandidaten
    dieser Spur", waehrend 15 Promotionsauftraege danebenlagen.

    > **Eine Zusammenfassung vor der Aufteilung macht die Aufteilung
    > wirkungslos.** Die Spur wird nach dem Agenten entschieden; wer vorher
    > auf einen Gewinner reduziert, hat die Entscheidung schon getroffen.

    Der Vergleich innerhalb einer Queue bleibt unveraendert, und der
    Scheduler waehlt weiterhin einen Gewinner — nur eben aus den Kandidaten
    **seiner** Spur.

    Nachbedingung: Hoechstens ein Eintrag je Queue, in der Reihenfolge
        shadow_queue, queue. Leere Liste, wenn beide leer sind.
    """
    gewinner: list[dict] = []

    # ── Spur 1: die Shadow-Queue, seit dem 15.08.2026 in PostgreSQL ──
    # Die Auswahl macht der Index, nicht dieser Prozess: `ORDER BY
    # salienz_decay DESC LIMIT 1` statt eines Vollscans ueber die ganze Liste.
    # **Die Rangfolge ist Dringlichkeit** — und weil der Verfall sie ueber die
    # Zeit senkt, gewinnt der juengste Auftrag. Die Redis-Fassung nahm unter
    # Gleichstaenden den aeltesten; das war keine Entscheidung, sondern eine
    # Folge der Einfuegereihenfolge (novaberg-queue-verfall_k.md §12.3).
    auftrag: dict | None = ShadowAuftragRepository.bester_kandidat(
        POSTGRES_URL, user_id, ASSISTANT_USER_ID,
    )
    if auftrag:
        gewinner.append({
            "name": auftrag["aufgabe"] or "unbekannt",
            "prioritaet": auftrag["salienz_decay"],
            # Der Auftrag altert jetzt sehr wohl — aber nach unten. Basis ist
            # der Anker, effektiv die verfallene Praesenz; die Differenz ist
            # im Log ablesbar und sagt, wie lange er schon liegt.
            "prioritaet_basis": auftrag["salienz_absolut"],
            "ueberfaellig_s": None,
            "quelle": "shadow_auftrag",
            "daten": auftrag,
            "auftrag_id": auftrag["id"],
            "queue_key": None,
            "queue_raw": None,
            "schedule_key": None,
            "themen": auftrag["thema"],
        })

    # ── Spur 2: die Promotions-Queue, weiterhin in Redis ──
    # Sie zieht **nicht** mit: Sie traegt keine Salienz-Dynamik, kein
    # Verfallsmodell und keinen Soft-Delete — ein KZG-Key wartet dort auf
    # seine Promotion und ist danach weg.
    promotion_key: str = f"queue:{user_id}"
    bester: dict | None = None
    beste_prio: float = -1.0

    for raw in redis_client.lrange(promotion_key, 0, -1):
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
                # Promotionsauftraege altern nicht: basis == effektiv, und
                # None statt 0.0, weil "altert nicht" etwas anderes ist
                # als "ist gerade eben faellig geworden".
                "prioritaet_basis": prio,
                "ueberfaellig_s": None,
                "quelle": "queue",
                "daten": eintrag,
                "auftrag_id": None,
                "queue_key": promotion_key,
                "queue_raw": raw,
                "schedule_key": None,
                "themen": eintrag.get("themen", ""),
            }

    if bester:
        gewinner.append(bester)

    return gewinner


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
                "auftrag_id": None,
                "daten": daten,
                "queue_key": None,
                "queue_raw": None,
                "schedule_key": key,
                "themen": "",
            })

    return faellige
