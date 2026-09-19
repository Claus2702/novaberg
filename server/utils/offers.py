"""Das Angebot: Bot Nova an, eine Sache einzutragen oder festzuhalten?

**Warum es das gibt.** Der `[LAGE]`-Block des Empfangs macht eine Zustimmung
zum Auftrag — *"Gerne"* nach einem Angebot heisst eintragen. Was fehlte, war
das Angebot selbst: Es wurde nirgends festgehalten, und damit galt **jede**
Zustimmung als Auftrag. `[gemessen 17.09.2026, Betrieb]` In zwei Dialogen
fragte Nova nach einer Nebensache (Gleis, Dauer), das folgende *"Gerne"*
schrieb trotzdem den Termin — 2 von 2.

**Was hier entsteht.** Nach jedem Turn wird die fertige Antwort auf Angebote
abgesucht. Findet sich eins, liegt es mit den akuten Objekten des Turns und
den Diensten, an deren Zettel sie stehen, als **offener Punkt** in Redis.
Der Empfang liest ihn im naechsten Turn: Ohne offenen Punkt ist eine
Zustimmung keine Zustimmung zu einem Auftrag, sondern Gespraech.

**Die Grenze dieser Pruefung.** Sie liest Wortlaut, kein Verstehen: Die Muster
sind an den Formen geeicht, in denen Nova anbietet (*"Soll ich ... eintragen?"*).
Ein Angebot in einer Form, die hier nicht steht, wird nicht gefunden — dann
faellt die Kette auf *kein Auftrag* zurueck, also auf die vorsichtige Seite.
Dasselbe Verfahren wie bei der Speicherbehauptung (`utils/storage_claims.py`),
und dieselbe Grenze.
"""

import json
import logging
import re
import time
from dataclasses import dataclass

logger = logging.getLogger("ki_server.offers")

# Die Verben, um die es geht: eine Sache in einen Dienst schreiben.
_WRITE_VERB = (
    r"(?:eintrage|eintragen|eintrag|notiere|notieren|festhalte|festhalten|"
    r"anlege|anlegen|aufschreibe|aufschreiben|merke|merken|speichere|speichern|"
    r"vormerke|vormerken|setze|setzen|hinzufuege|hinzufuegen|hinzufüge|hinzufügen)"
)

# Die Formen, in denen ein Angebot steht. Alle haben zwei Teile: Nova nimmt die
# Handlung auf sich (ich), und sie fragt oder stellt es frei.
_OFFER_FORMS: tuple[re.Pattern[str], ...] = (
    re.compile(rf"\bsoll\s+ich\b.*\b{_WRITE_VERB}\b", re.I),
    re.compile(rf"\bmoechtest\s+du,?\s+dass\s+ich\b.*\b{_WRITE_VERB}\b", re.I),
    re.compile(rf"\bmöchtest\s+du,?\s+dass\s+ich\b.*\b{_WRITE_VERB}\b", re.I),
    re.compile(rf"\bwillst\s+du,?\s+dass\s+ich\b.*\b{_WRITE_VERB}\b", re.I),
    re.compile(rf"\bdarf\s+ich\b.*\b{_WRITE_VERB}\b", re.I),
    re.compile(rf"\bich\s+kann\s+(?:es\s+|das\s+|dir\s+|ihn\s+|sie\s+)?.*\b{_WRITE_VERB}\b", re.I),
    re.compile(rf"\bwenn\s+du\s+(?:magst|willst|moechtest|möchtest)\b.*\b{_WRITE_VERB}\b", re.I),
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_MARKUP = re.compile(r"[*_`#>]+")


@dataclass(frozen=True)
class Offer:
    """Ein Angebot Novas, das auf eine Antwort des Menschen wartet.

    Attributes:
        sentence: Der Satz, in dem das Angebot steht — der Beleg.
        objects: Die Namen der akuten Objekte des Turns, auf die es sich
            bezieht. Leer heisst: Ein Angebot stand da, aber die Lage nannte
            keine Sache — dann traegt es keinen Gegenstand.
        details: Dieselben Objekte mit `name`, `klasse` und `gedeckt`. **Sie
            reisen mit, weil die Lage weiterzieht:** `[gemessen 17.09.2026,
            Betrieb]` Zwei Turns nach dem Angebot war die angebotene Sache
            nicht mehr akut — mit den Namen allein haette der Dienst weder
            Tag noch Uhrzeit bekommen.
        services: Die Dienste, an deren Zettel diese Objekte stehen.
        turn_id: Der Turn, in dem das Angebot fiel.
        time: Sekunden seit der Epoche, gesetzt beim Ablegen.
    """

    sentence: str
    objects: tuple[str, ...]
    services: tuple[str, ...]
    turn_id: str
    time: float
    details: tuple[dict, ...] = ()


def _plain(text: str) -> str:
    """Nimmt Markdown-Auszeichnung heraus, damit die Muster am Wort greifen."""
    return _MARKUP.sub("", text)


def find_offers(text: str) -> list[str]:
    """Findet die Saetze einer Antwort, in denen Nova anbietet, etwas zu schreiben.

    Vorbedingung: `text` ist die fertige Antwort. Ein anderer Typ wird laut
    gemeldet und ergibt eine leere Liste — eine Pruefung haelt den Antwortpfad
    nicht an.

    Nachbedingung: hoechstens ein Befund je Satz, in der Reihenfolge der
    Antwort. Leere Liste heisst: keine der bekannten Angebotsformen. **Sie
    heisst nicht, dass der Text kein Angebot enthaelt.**
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(text, str):
        logger.error("Angebot: text ist %s statt str — keine Pruefung", type(text).__name__)
        return []
    if not text.strip():
        return []

    # ── Verarbeitung ────────────────────────────
    treffer: list[str] = []
    for satz in _SENTENCE_SPLIT.split(_plain(text)):
        satz = satz.strip()
        if satz and any(form.search(satz) for form in _OFFER_FORMS):
            treffer.append(satz)

    # ── Ausgabe-Verifikation ────────────────────
    if any(not isinstance(s, str) or not s for s in treffer):
        logger.error("Angebot: leerer Satz im Befund — verworfen")
        return [s for s in treffer if isinstance(s, str) and s]
    return treffer


def offer_key(user_id: str, character_id: str) -> str:
    """Der Redis-Schluessel des offenen Angebots — je Paar, nicht je Mensch.

    Anders als `pending_agent:{user_id}` traegt er die Figur: Zwei Figuren
    desselben Menschen bieten unabhaengig voneinander an.
    """
    return f"angebot:{user_id}:{character_id}"


def offer_store(redis_client: object, user_id: str, character_id: str,
                offer: Offer, ttl_seconds: float) -> bool:
    """Legt das Angebot als offenen Punkt ab und gibt zurueck, ob es ankam.

    Vorbedingung: `offer` traegt einen Satz; `ttl_seconds` ist positiv.
    Nachbedingung: Der Schluessel des Paares traegt das Angebot und verfaellt
    nach `ttl_seconds`. Bei einem Fehler des Speichers: `False` und eine
    Fehlerzeile — der Turn laeuft weiter, der naechste gilt dann als ohne
    Angebot (die vorsichtige Seite).
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(offer, Offer) or not offer.sentence:
        logger.error("Angebot: kein gueltiges Angebot zum Ablegen")
        return False
    if not user_id or not character_id:
        logger.error("Angebot: Paar unvollstaendig (user=%r, character=%r)", user_id, character_id)
        return False
    if ttl_seconds <= 0:
        logger.error("Angebot: Verfallszeit %r ist nicht positiv", ttl_seconds)
        return False

    # ── Verarbeitung ────────────────────────────
    nutzlast = {
        "satz":     offer.sentence[:400],
        "objekte":  list(offer.objects),
        "sachen":   [dict(d) for d in offer.details],
        "dienste":  list(offer.services),
        "turn_id":  offer.turn_id,
        "zeit":     offer.time,
    }
    try:
        redis_client.setex(offer_key(user_id, character_id), int(ttl_seconds),
                           json.dumps(nutzlast, ensure_ascii=False))
    except Exception as fehler:  # noqa: BLE001 — der Antwortpfad haelt nicht an
        logger.error("Angebot: konnte nicht abgelegt werden (%s: %s)", type(fehler).__name__, fehler)
        return False

    # ── Ausgabe-Verifikation ────────────────────
    logger.info(
        "Angebot abgelegt: %s — Objekte %s, Dienste %s, %.0f s gueltig",
        nutzlast["satz"][:80], nutzlast["objekte"], nutzlast["dienste"], ttl_seconds,
    )
    return True


def offer_load(redis_client: object, user_id: str, character_id: str) -> Offer | None:
    """Liest das offene Angebot des Paares, oder `None`.

    Nachbedingung: `None` heisst **kein offenes Angebot** — auch dann, wenn der
    Speicher nicht antwortet oder Unlesbares traegt. Beides wird laut gemeldet;
    die Kette faellt damit auf *keine Zustimmung ist ein Auftrag* zurueck.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        return None

    # ── Verarbeitung ────────────────────────────
    try:
        roh = redis_client.get(offer_key(user_id, character_id))
    except Exception as fehler:  # noqa: BLE001
        logger.error("Angebot: nicht lesbar (%s: %s)", type(fehler).__name__, fehler)
        return None
    if not roh:
        return None
    try:
        daten = json.loads(roh if isinstance(roh, str) else roh.decode("utf-8"))
    except (ValueError, AttributeError, UnicodeDecodeError) as fehler:
        logger.error("Angebot: unlesbar abgelegt (%s) — gilt als keines", fehler)
        return None
    if not isinstance(daten, dict) or not daten.get("satz"):
        logger.error("Angebot: Eintrag ohne Satz — gilt als keines")
        return None

    # ── Ausgabe ─────────────────────────────────
    return Offer(
        sentence = str(daten.get("satz", "")),
        objects  = tuple(str(o) for o in daten.get("objekte", []) if o),
        details  = tuple(d for d in daten.get("sachen", []) if isinstance(d, dict)),
        services = tuple(str(d) for d in daten.get("dienste", []) if d),
        turn_id  = str(daten.get("turn_id", "")),
        time     = float(daten.get("zeit", 0.0)),
    )


def offer_clear(redis_client: object, user_id: str, character_id: str, grund: str) -> None:
    """Nimmt den offenen Punkt weg — beantwortet, ausgefuehrt oder ueberholt.

    Nachbedingung: Der Schluessel ist fort, und der Grund steht im Log. Ein
    stilles Loeschen waere von *"es gab nie eins"* nicht zu unterscheiden.
    """
    try:
        entfernt = redis_client.delete(offer_key(user_id, character_id))
    except Exception as fehler:  # noqa: BLE001
        logger.error("Angebot: konnte nicht entfernt werden (%s: %s)", type(fehler).__name__, fehler)
        return
    if entfernt:
        logger.info("Angebot entfernt (%s) — Paar %s:%s", grund, user_id, character_id)


def offer_matches(offer: Offer | None, object_names: list[str]) -> bool:
    """Steht ein Angebot offen, auf das sich eine Zustimmung beziehen kann?

    Vorbedingung: `object_names` sind die Namen der akuten Objekte dieses Turns
        — sie dienen nur der Meldung, nicht der Entscheidung.
    Nachbedingung: `True`, sobald ein Angebot offen ist. **Die Lage entscheidet
        nicht mit:** `[gemessen 17.09.2026, Betrieb]` Zwei Turns nach dem
        Angebot war die angebotene Sache nicht mehr akut, und ein Abgleich
        gegen die Lage liess die Zustimmung ins Leere laufen. Der Gegenstand
        kommt aus dem Angebot selbst (`details`), nicht aus der Lage.
        Kein Angebot: immer `False`.
    """
    if offer is None:
        return False
    if offer.objects and object_names:
        bekannt = {n.strip().casefold() for n in object_names if isinstance(n, str)}
        if not any(o.strip().casefold() in bekannt for o in offer.objects):
            logger.info(
                "Angebot: die angebotene Sache %s ist nicht mehr in der Lage %s — "
                "der Gegenstand kommt aus dem Angebot",
                list(offer.objects), list(object_names)[:3],
            )
    return True


# Die Woerter, mit denen ein Mensch zustimmt, ohne etwas anderes zu sagen.
# Geeicht an den Zustimmungen der Messreihen vom 17.09.2026.
_CONSENT_WORDS: frozenset[str] = frozenset({
    "ja", "jo", "jep", "jawohl", "gern", "gerne", "bitte", "klar", "ok", "okay",
    "sicher", "unbedingt", "natuerlich", "natürlich", "mach", "das", "tu", "es",
    "mache", "machs", "immer", "her", "damit", "danke", "super", "prima", "doch",
})
_WORD = re.compile(r"[a-zA-ZaeoeueAEOEUEäöüÄÖÜß]+")


def is_bare_consent(text: str) -> bool:
    """Sagt die Aeusserung nichts weiter als "ja"?

    Vorbedingung: `text` ist der Reiz dieses Turns.
    Nachbedingung: `True` nur, wenn **jedes** Wort ein Zustimmungswort ist und
    hoechstens vier Woerter dastehen — *"Gerne"*, *"Ja, bitte"*, *"Mach das"*.
    Alles, was eine eigene Sache nennt (*"Ja, trag den Zahnarzt ein"*), ist
    keine blanke Zustimmung: Ein solcher Auftrag traegt seinen Gegenstand
    selbst und darf nicht an einem fehlenden Angebot scheitern.

    **Was diese Pruefung nicht kann:** eine Zustimmung erkennen, die nicht aus
    diesen Woertern besteht (*"Na dann los"*). Sie faellt dann auf `False` —
    und die Kette entscheidet wie bisher.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    woerter = [w.casefold() for w in _WORD.findall(text)]
    if not woerter or len(woerter) > 4:
        return False
    # Ein "Danke" allein ist nach einem Angebot im Deutschen oft die hoefliche
    # Ablehnung (zweite Kontrolle, 18.09.2026) — es zaehlt nur, wenn ein
    # anderes Zustimmungswort daneben steht ("Ja, danke").
    if all(w == "danke" for w in woerter):
        return False
    return all(w in _CONSENT_WORDS for w in woerter)


# Die Wortformen, mit denen ein Mensch einen eigenen Schreibauftrag stellt.
# Geeicht an den Aushaengen von Timeline und Notizen und an den Messreihen vom
# 13. bis 17.09.2026 — es sind die Imperative, die dort als Auftrag gelten.
_REQUEST_FORMS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:trag|träg|traeg)\w*\b.*\bein\b", re.I),
    re.compile(r"\b(?:schreib|notier|merk|vermerk|speicher|setz|streich|loesch|lösch|entfern)\w*\b", re.I),
    re.compile(r"\berinner\w*\s+mich\b", re.I),
    re.compile(r"\bverschieb\w*\b", re.I),
    re.compile(r"\bleg\w*\b.*\b(?:an|liste)\b", re.I),
)


def carries_own_request(text: str) -> bool:
    """Traegt die Aeusserung einen eigenen Schreibauftrag?

    Vorbedingung: `text` ist der Reiz dieses Turns.
    Nachbedingung: `True`, wenn eine der bekannten Auftragsformen darin steht
    (*"Trag mir ... ein"*, *"Schreib ... auf"*, *"Erinnere mich ..."*). Damit
    unterscheidet der Empfang eine **Antwort auf seine Rueckfrage** von einem
    **neuen Auftrag**: `[gemessen 17.09.2026, Betrieb]` Eine offene Rueckfrage
    der Notizen verschluckte den Auftrag *"Trag mir den Zahnarzt am Donnerstag
    um 15 Uhr ein"* und meldete `abgeschlossen`, ohne etwas zu schreiben.

    **Was diese Pruefung nicht kann:** einen Auftrag in einer Form erkennen, die
    nicht in der Liste steht. Dann bleibt es beim Verhalten von vorher — die
    Aeusserung gilt als Antwort auf die Rueckfrage.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    return any(form.search(text) for form in _REQUEST_FORMS)


# Die Woerter, mit denen ein Mensch ein Angebot ablehnt, ohne etwas anderes zu
# sagen. Geeicht an den Ablehnungen der Messreihen vom 17.09.2026.
_REFUSAL_WORDS: frozenset[str] = frozenset({
    "nein", "ne", "nee", "noe", "nö", "danke", "lass", "mal", "nicht", "noetig", "nötig",
    "lieber", "brauchst", "du", "schon", "gut", "passt", "kein", "bedarf", "nope",
})
_REFUSAL_OPENERS: frozenset[str] = frozenset({"nein", "ne", "nee", "noe", "nö", "nope", "lass", "lieber", "nicht", "kein"})


def is_bare_refusal(text: str) -> bool:
    """Sagt die Aeusserung nichts weiter als "nein"?

    Vorbedingung: `text` ist der Reiz dieses Turns.
    Nachbedingung: `True` nur, wenn hoechstens fuenf Woerter dastehen, **jedes**
    ein Ablehnungswort ist und das erste die Ablehnung traegt — *"Nein"*,
    *"Nein danke"*, *"Lass mal"*, *"Nicht noetig"*, *"Lieber nicht"*. Ein
    Satz, der zugleich etwas anderes sagt (*"Nein, trag lieber den Zahnarzt
    ein"*), ist keine blanke Ablehnung.

    **Was diese Pruefung nicht kann:** eine Ablehnung in anderen Worten
    erkennen (*"Das merke ich mir selbst"*). Dann bleibt das Objekt ohne
    Vermerk — Nova koennte wieder anbieten, das ist die aufdringliche Seite.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    woerter = [w.casefold() for w in _WORD.findall(text)]
    if not woerter or len(woerter) > 5 or woerter[0] not in _REFUSAL_OPENERS:
        return False
    return all(w in _REFUSAL_WORDS for w in woerter)


# Wie Nova die Handlung je Dienst nennt — im Wortlaut, den `find_offers` erkennt.
_OFFER_VERBS: dict[str, str] = {"timeline": "eintragen", "notizen": "notieren"}


def _writing_services(entry: dict) -> list[str]:
    """Die schreibenden Dienste eines Urteilseintrags, der naechste zuerst.

    Vorbedingung: keine; ein unlesbarer Naehewert zaehlt als 0.
    Nachbedingung: nur Dienste aus `_OFFER_VERBS`, absteigend nach Naehe, bei
        Gleichstand nach Name. **Nicht die Reihenfolge von `empfaenger`** —
        die ist nach Name (`object_nearness.judge`). `[gemessen 18.09.2026,
        Betrieb]` 4 von 4 Terminen standen an Notizen und Timeline, die
        Timeline naeher — angeboten wurde 4 von 4 Mal "notieren".
    Fehlerfaelle: keine.
    """
    naehe: dict = entry.get("naehe") if isinstance(entry.get("naehe"), dict) else {}

    def wert(dienst: str) -> float:
        try:
            return float(naehe.get(dienst, 0.0))
        except (TypeError, ValueError):
            return 0.0

    dienste: list[str] = [str(d) for d in (entry.get("empfaenger") or []) if str(d) in _OFFER_VERBS]
    return sorted(dict.fromkeys(dienste), key=lambda d: (-wert(d), d))


@dataclass(frozen=True)
class OfferCandidate:
    """Eine Sache, die Nova anbieten koennte — und warum oder warum nicht.

    Attributes:
        name: Name des akuten Objekts; leer, wenn es keinen Kandidaten gibt.
        service: Der Dienst, an dessen Zettel es steht.
        verb: Wie die Handlung heisst ("eintragen", "notieren").
        reason: Der Ausgang der Weiche — `anbieten`, oder warum nicht.
    """

    name: str
    service: str
    verb: str
    reason: str


def _service_acted(result: object) -> bool:
    """Hat dieser Dienst im Turn gehandelt oder gefragt?

    Vorbedingung: keine; `result` ist ein AgentResult oder ein dict.
    Nachbedingung: False genau dann, wenn kein Status gesetzt ist oder der
        Dienst ablehnte, weil die Aeusserung **kein Auftrag an ihn** war
        (`Korrektur.kein_auftrag`). Jeder andere Ausgang — abgeschlossen,
        Rueckfrage, Fehler, Ablehnung in der Sache — zaehlt als gehandelt.
        `[gelesen 19.09.2026]` Vorher zaehlte jede Ablehnung: Seit die
        Notizen-Vorpruefung Bedarfsaussagen ablehnt, bot Nova auf sie nie an.
    Fehlerfaelle: keine.
    """
    ist_dict: bool = isinstance(result, dict)
    status = getattr(result, "status", None) or (result.get("status") if ist_dict else None)
    if not status:
        return False
    if status != "abgelehnt":
        return True
    korrektur = getattr(result, "korrektur", None) or (result.get("korrektur") if ist_dict else None)
    kein_auftrag = getattr(korrektur, "kein_auftrag", None)
    if kein_auftrag is None and isinstance(korrektur, dict):
        kein_auftrag = korrektur.get("kein_auftrag")
    return kein_auftrag is not True


def offer_candidate(
    sachlage:          object,
    verdict:           object,
    agent_results:     list,
    management_action: str,
) -> OfferCandidate:
    """Welche Sache kaeme fuer ein Angebot in Frage — vor Pflicht und Ablehnung?

    Vorbedingung: keine.
    Nachbedingung: der erste akute Gegenstand, den die gerechnete Naehe an den
        Zettel eines schreibenden Dienstes (Timeline, Notizen) stellt — sonst
        ein Kandidat ohne Namen mit dem Grund. **Kein Angebot**, wenn in diesem
        Turn schon ein Dienst gehandelt oder gefragt hat (`_service_acted` —
        eine Ablehnung als Nicht-Auftrag zaehlt nicht) oder ein Auftrag
        laeuft — es sei denn, jeder gefragte Dienst lehnte ihn als
        Nicht-Auftrag ab: Anbieten ist fuer das, worum niemand gebeten hat.
    """
    ergebnisse: list = list(agent_results or [])
    # Ein Auftrag, den jeder gefragte Dienst als Nicht-Auftrag abgelehnt hat,
    # laeuft nicht: Der Router stellte zu, aber niemand hat gebeten.
    nur_kein_auftrag: bool = bool(ergebnisse) and not any(_service_acted(r) for r in ergebnisse)
    if management_action and not nur_kein_auftrag:
        return OfferCandidate("", "", "", "auftrag_laeuft")
    if any(_service_acted(r) for r in ergebnisse):
        return OfferCandidate("", "", "", "dienst_lief")
    if not isinstance(sachlage, dict) or not isinstance(verdict, dict) or verdict.get("ergebnis") != "gerechnet":
        return OfferCandidate("", "", "", "keine_naehe")
    empfaenger: dict[str, list[str]] = {
        str(o.get("name") or ""): _writing_services(o)
        for o in verdict.get("objekte") or [] if isinstance(o, dict)
    }
    for objekt in sachlage.get("objekte") or []:
        if not isinstance(objekt, dict) or objekt.get("akut") is not True:
            continue
        name = str(objekt.get("name") or "").strip()
        for dienst in empfaenger.get(name, []):
            return OfferCandidate(name, dienst, _OFFER_VERBS[dienst], "anbieten")
    return OfferCandidate("", "", "", "keine_sache_am_zettel")


@dataclass(frozen=True)
class OfferBinding:
    """Woran ein erkanntes Angebot gebunden wird — und warum.

    Attributes:
        objects: Die Namen der angebotenen Sachen; leer, wenn keine eindeutig ist.
        services: Die schreibenden Dienste dieser Sachen.
        details: Dieselben Sachen mit `name`, `klasse` und `gedeckt`.
        reason: `angeboten` (der Verfasser bot genau diese Sache an),
            `einzige_sache` (Nova bot von sich aus an, und nur eine akute Sache
            steht am Zettel eines schreibenden Dienstes) oder `mehrdeutig`.
    """

    objects: tuple[str, ...]
    services: tuple[str, ...]
    details: tuple[dict, ...]
    reason: str


def offer_binding(sachlage: object, verdict: object, offered: object) -> OfferBinding:
    """Bindet ein Angebot in Novas Antwort an die Sache, der es gilt.

    Vorbedingung: keine.
    Nachbedingung: Hat der Verfasser in diesem Turn eine Sache angeboten
        (`offered` = {"name", "dienst"}), gilt das Angebot genau ihr. Sonst
        gilt es der einzigen akuten Sache am Zettel eines schreibenden
        Dienstes. **Gibt es keine oder mehrere, traegt es keinen Gegenstand**
        — ein "Gerne" wird dann nicht von selbst zum Auftrag.
        `[gemessen 18.09.2026, zweite Kontrolle]` 2 von 4 echten Angeboten
        galten einer Nebensache, abgelegt wurden sie mit **allen** akuten
        Objekten; der Router nahm deren ersten Dienst.
    Fehlerfaelle: keine; unlesbare Eingaben zaehlen als leer.
    """
    objekte: list[dict] = [
        o for o in ((sachlage or {}).get("objekte") or [] if isinstance(sachlage, dict) else [])
        if isinstance(o, dict) and o.get("akut") is True and str(o.get("name") or "").strip()
    ]
    empfaenger: dict[str, list[str]] = {
        str(o.get("name") or ""): _writing_services(o)
        for o in ((verdict or {}).get("objekte") or [] if isinstance(verdict, dict) else [])
        if isinstance(o, dict)
    }
    name: str = str(offered.get("name") or "").strip() if isinstance(offered, dict) else ""
    if name:
        dienste: list[str] = [str(offered.get("dienst") or "")]
        gewaehlt: list[dict] = [o for o in objekte if str(o.get("name")).strip() == name]
        grund: str = "angeboten"
    else:
        gewaehlt = [o for o in objekte if empfaenger.get(str(o.get("name")).strip())]
        if len(gewaehlt) != 1:
            return OfferBinding((), (), (), "mehrdeutig")
        dienste = empfaenger[str(gewaehlt[0].get("name")).strip()]
        grund = "einzige_sache"
    details: tuple[dict, ...] = tuple(
        {"name": str(o.get("name")).strip(), "klasse": o.get("klasse"),
         "gedeckt": dict(o.get("gedeckt") or {})}
        for o in gewaehlt
    )
    namen: tuple[str, ...] = (name,) if name else tuple(d["name"] for d in details)
    # Der naechste Dienst zuerst (`_writing_services`): Der Router stellt dem
    # ersten zu.
    return OfferBinding(namen, tuple(dict.fromkeys(dienste)), details, grund)
