"""
GV4: Themen als Lueckenkandidaten — die Luecke beim Nutzer.

**Warum Themen und nicht Saetze** (`F-GV-2`, 12.09.2026). Die Lueckensuche gab
bis dahin ganze Gedaechtnissaetze in den Prompt, und `[gemessen]` 56 von 83 davon
waren Vermerke ueber Novas eigene Aeusserungen (*„Nova hat gefragt, ob …"*). Ein
Satz traegt seinen Sprecher: Gegen den Charakterkern lagen Nova-Saetze bei
0,44–0,53, Nutzer-Saetze bei 0,13–0,24. **Ein Thema traegt ihn nicht** —
dieselbe Messung auf den Themen derselben Knoten: Median 0,209 gegen 0,200.

**Was eine Luecke beim Nutzer hier heisst, ist eine Annaeherung:** ein Thema aus
Novas Bestand nahe am Turn, das in keinem Eintrag mit `beobachter = 'user'` des
Paares als Thema steht. Das ist das Fehlen eines Belegs, dass er es kennt — kein
Nachweis, dass er es nicht kennt.

Dieses Modul traegt drei Dinge: die Zerlegung der Themenfelder, den
Themenbestand des Nutzers (je Paar zwischengehalten) und die Einbettung der
Themen im Stapel (je Text zwischengehalten).
"""

import logging
import math
import threading
import time
from collections import OrderedDict
from collections.abc import Iterable

from config import GV_GEWICHT_VERTEILUNG_TTL_S, redis_client
from services.model_services import EmbedBatchRequest, model_service
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.ei.gap_topics")

#: Ab welchem Anteil bekannter Wortstaemme ein Thema als vom Nutzer beruehrt gilt.
#: Zwei von drei: *„Neutronenstern Kruste"* ist beruehrt, wenn der Nutzer
#: *„Neutronensterne"* und *„Krustenbeben"* als Themen hatte. Kein Messwert — eine
#: Setzung, deren Wirkung im Nachher-Lauf gelesen wird.
TOUCHED_SHARE: float = 2 / 3

#: Laenge des Wortstamms. Sieben Zeichen fassen deutsche Flexion
#: (*Neutronenstern/-sterne*) und trennen noch Komposita mit gleichem Anfang
#: nicht zuverlaessig — eine grobe, benannte Naeherung.
STEM_LENGTH: int = 7

#: Hoechstzahl zwischengehaltener Themen-Vektoren. Ein Vektor sind 768 Zahlen;
#: 5000 davon sind rund 30 MB im Prozess.
EMBED_CACHE_SIZE: int = 5000

_KZG_PAGE: int = 1000

_user_cache: dict[tuple[str, str], tuple[float, "UserTopics"]] = {}
_user_lock = threading.Lock()
_embed_cache: "OrderedDict[str, list[float]]" = OrderedDict()
_embed_lock = threading.Lock()


class UserTopics:
    """Was der Nutzer als Thema beruehrt hat: die Themen selbst und ihr Wortschatz."""

    def __init__(self, topics: set[str], stems: set[str]) -> None:
        """Legt Themen und Wortstaemme ab.

        Vorbedingung: beides Mengen kleingeschriebener Zeichenketten.
        Nachbedingung: unveraendert abgelegt.
        """
        self.topics = topics
        self.stems = stems


def split_topics(raw: object) -> list[str]:
    """Die Themen eines Eintrags als Liste — gleich, ob sie als Liste oder als Zeichenkette kommen.

    Vorbedingung: keine. Das LZG fuehrt `themen` als Array, das KZG als durch
        Komma getrennte Zeichenkette; `None` und Leeres sind zulaessig.
    Nachbedingung: getrimmte, nicht leere Themen in Eingabereihenfolge, ohne
        Wiederholung (Gross-/Kleinschreibung gilt als gleich).
    Fehlerfaelle: Ein anderer Typ als Liste, Zeichenkette oder None ergibt eine
        leere Liste und einen Fehler im Log.

    Args:
        raw: der Feldinhalt.

    Returns:
        Die Themen.
    """
    # ── Eingabe-Validierung ─────────────────────
    if raw is None:
        return []
    if isinstance(raw, str):
        teile: Iterable = raw.split(",")
    elif isinstance(raw, (list, tuple)):
        teile = raw
    else:
        logger.error(
            "split_topics: Themenfeld vom Typ %s — erwartet Liste oder Text", type(raw).__name__,
        )
        return []

    # ── Verarbeitung ────────────────────────────
    ergebnis: list[str] = []
    gesehen: set[str] = set()
    for teil in teile:
        if not isinstance(teil, str):
            continue
        thema = teil.strip()
        if thema and thema.lower() not in gesehen:
            gesehen.add(thema.lower())
            ergebnis.append(thema)

    # ── Ausgabe-Verifikation ────────────────────
    if any(not t for t in ergebnis):
        raise ValueError("split_topics: leeres Thema im Ergebnis")
    return ergebnis


def topic_stems(topic: str) -> set[str]:
    """Die Wortstaemme eines Themas: Woerter ueber drei Zeichen, klein, auf `STEM_LENGTH` gekuerzt.

    Vorbedingung: keine.
    Nachbedingung: eine Menge, leer bei einem Thema ohne ausreichend lange Woerter.
    """
    return {
        w.lower()[:STEM_LENGTH]
        for w in topic.replace("-", " ").replace("/", " ").split()
        if len(w) > 3
    }


def touched_by_user(topic: str, user_topics: UserTopics) -> bool:
    """Sagt, ob der Nutzer dieses Thema beruehrt hat.

    Vorbedingung: `topic` ist nicht leer.
    Nachbedingung: True, wenn das Thema woertlich (ohne Gross-/Kleinschreibung)
        unter den Nutzerthemen steht oder mindestens `TOUCHED_SHARE` seiner
        Wortstaemme im Wortschatz des Nutzers vorkommen. Ein Thema ohne
        verwertbare Woerter gilt nur bei woertlichem Treffer als beruehrt.

    Args:
        topic: das Thema.
        user_topics: der Themenbestand des Nutzers.

    Returns:
        Ob das Thema als beruehrt gilt.
    """
    if topic.strip().lower() in user_topics.topics:
        return True
    staemme = topic_stems(topic)
    if not staemme:
        return False
    return len(staemme & user_topics.stems) / len(staemme) >= TOUCHED_SHARE


def _load_user_topics(user_id: str, character_id: str) -> UserTopics:
    """Liest die Themen aller Nutzer-Eintraege des Paares aus LZG und KZG.

    Vorbedingung: Paar vollstaendig (prueft der Aufrufer).
    Nachbedingung: Themen klein und getrimmt, Wortstaemme dazu.
    Fehlerfaelle: Datenbank- und Redis-Fehler laufen durch.
    """
    themen: set[str] = set()
    for zeile in db_manager.select(
        "SELECT themen FROM lzg_knoten "
        "WHERE user_id = %s AND character_id = %s AND beobachter = 'user'",
        (user_id, character_id),
    ):
        themen.update(t.lower() for t in split_topics(zeile.get("themen")))

    abfrage: str = f"@user_id:{{{user_id}}} @character_id:{{{character_id}}} @beobachter:{{user}}"
    offset: int = 0
    while True:
        ergebnis = redis_client.execute_command(
            "FT.SEARCH", "idx:kzg", abfrage,
            "RETURN", "1", "themen",
            "LIMIT", str(offset), str(_KZG_PAGE),
            "DIALECT", "2",
        )
        gesamt: int = int(ergebnis[0])
        treffer: list = ergebnis[1:]
        for i in range(1, len(treffer), 2):
            felder = treffer[i]
            roh = dict(zip(felder[::2], felder[1::2], strict=True)).get("themen")
            themen.update(t.lower() for t in split_topics(roh))
        offset += _KZG_PAGE
        if offset >= gesamt:
            break

    staemme: set[str] = set()
    for thema in themen:
        staemme |= topic_stems(thema)
    return UserTopics(themen, staemme)


def load_user_topics(user_id: str, character_id: str) -> UserTopics:
    """Der Themenbestand des Nutzers fuer ein Paar, zwischengehalten.

    Die Frist ist `GV_GEWICHT_VERTEILUNG_TTL_S` — dieselbe wie die der Gewichtsverteilung.

    Vorbedingung: `user_id` und `character_id` sind gesetzt.
    Nachbedingung: ein `UserTopics`; leer zulaessig bei einem Paar ohne Nutzer-Eintraege.
    Fehlerfaelle: `ValueError` bei unvollstaendigem Paar; Speicherfehler laufen durch.

    Args:
        user_id: der Mensch des Paares.
        character_id: die Figur des Paares.

    Returns:
        Themen und Wortstaemme.

    Raises:
        ValueError: bei unvollstaendigem Paar.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        raise ValueError(
            f"load_user_topics: Paar unvollstaendig "
            f"(user_id={user_id!r}, character_id={character_id!r})"
        )

    # ── Verarbeitung ────────────────────────────
    schluessel = (user_id, character_id)
    jetzt = time.monotonic()
    with _user_lock:
        eintrag = _user_cache.get(schluessel)
        if eintrag and jetzt - eintrag[0] < GV_GEWICHT_VERTEILUNG_TTL_S:
            return eintrag[1]
    bestand = _load_user_topics(user_id, character_id)

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(bestand.topics, set) or not isinstance(bestand.stems, set):
        raise TypeError("load_user_topics: Bestand ohne Mengen")
    with _user_lock:
        _user_cache[schluessel] = (jetzt, bestand)
    logger.info(
        "Nutzerthemen %s/%s geladen: %d Themen, %d Wortstaemme",
        user_id, character_id, len(bestand.topics), len(bestand.stems),
    )
    return bestand


def embed_topics(topics: list[str]) -> dict[str, list[float]]:
    """Vektoren fuer Themen — aus dem Zwischenspeicher, der Rest in einem Stapelaufruf.

    Vorbedingung: `topics` enthaelt nur nicht leere Zeichenketten; leer zulaessig.
    Nachbedingung: ein Vektor je Thema, alle gleich lang und endlich. Neue
        Vektoren liegen danach im Zwischenspeicher; der aelteste faellt heraus,
        wenn `EMBED_CACHE_SIZE` ueberschritten ist.
    Fehlerfaelle: Ein Fehler des Modellaufrufs laeuft durch — der Aufrufer
        entscheidet, was ein Turn ohne Themenvektoren tut.

    Args:
        topics: die Themen.

    Returns:
        Thema → Vektor.

    Raises:
        ValueError: bei leerem Thema oder einem Vektor ungleicher Laenge.
    """
    # ── Eingabe-Validierung ─────────────────────
    if any(not isinstance(t, str) or not t.strip() for t in topics):
        raise ValueError("embed_topics: leeres oder ungueltiges Thema")

    # ── Verarbeitung ────────────────────────────
    ergebnis: dict[str, list[float]] = {}
    fehlend: list[str] = []
    with _embed_lock:
        for thema in topics:
            if thema in _embed_cache:
                _embed_cache.move_to_end(thema)
                ergebnis[thema] = _embed_cache[thema]
            elif thema not in fehlend:
                fehlend.append(thema)
    if fehlend:
        antwort = model_service.embed.submit_sync(EmbedBatchRequest(texts=fehlend))
        with _embed_lock:
            for thema, vektor in zip(fehlend, antwort.embeddings, strict=True):
                ergebnis[thema] = vektor
                _embed_cache[thema] = vektor
                _embed_cache.move_to_end(thema)
            while len(_embed_cache) > EMBED_CACHE_SIZE:
                _embed_cache.popitem(last=False)

    # ── Ausgabe-Verifikation ────────────────────
    laengen = {len(v) for v in ergebnis.values()}
    if len(laengen) > 1 or any(not math.isfinite(x) for v in ergebnis.values() for x in v[:4]):
        raise ValueError(
            f"embed_topics: Vektoren ungleicher Laenge oder nicht endlich ({sorted(laengen)})"
        )
    if fehlend:
        logger.info(
            "Themenvektoren: %d aus dem Zwischenspeicher, %d neu eingebettet",
            len(topics) - len(fehlend), len(fehlend),
        )
    return ergebnis
