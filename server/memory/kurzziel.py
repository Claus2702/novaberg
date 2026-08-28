"""Das kurzfristige Ziel — der dritte Zielhorizont, aus der Sachlage.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 2 (und
`novaberg-thinking-drive_k.md` §3.3, dort noch als fluechtige GV-Hypothese
beschrieben). Zeigen zwei Lagen derselben Blase auf dasselbe Vorhaben,
entsteht ein `ziel_typ='kurzfristig'` in der bestehenden `ziele`-Tabelle:
Novas Vorsatz, dem Menschen bei genau dieser Sache zu helfen. Es traegt einen
Vektor ueber seinen Zielsatz und laeuft damit ohne weiteren Bau durch die
Gravitation in den `[GEDANKEN]`-Block; es verfaellt in Stunden statt Tagen
(`ZIEL_KURZFRISTIG_DECAY_STUNDEN`, Decay-Agent).

**Dasselbe Vorhaben heisst: dasselbe akute Objekt in zwei gerechneten Lagen.**
Das Konzept nannte das `nutzerziel`; gemessen am 28.08.2026 traegt dieses
Feld das Ziel *der Aeusserung* und wird je Turn neu formuliert — Kosinus
0,40 bis 0,42 zwischen zwei Turns desselben Vorhabens gegen 0,35 beim
Themenwechsel, kein Abstand. Das akute Objekt dagegen schreibt die
Fortschreibung woertlich fort (»Rettich bewaessern« ueber drei Turns), weil
der Prompt sie dazu anhaelt. Es ist der Traeger der Bestaendigkeit, und
deshalb zaehlt die Strecke Objekte — per Namensgleichheit, ohne Schwelle.

**Die Strecke lebt in Redis, je Paar** (`kurzziel:{user}:{character}`): je
akutem Objekt die Zahl der aufeinanderfolgenden Lagen, in denen es stand,
und die id des daraus entstandenen Ziels. Sie wird **von der Herkunft der
Sachlage zurueckgesetzt**: Eine frische oder nach Verfall neu begonnene
Blase beginnt bei eins, auch wenn Redis noch den Stand der alten traegt.

**Genau eines je Objekt.** Solange das Objekt in der Blase steht, entsteht
kein zweites Ziel dazu — die id steht in der Strecke. Faellt es aus der
Blase, beginnt die Zaehlung neu, und ein spaeteres Ziel ist ein anderes.
"""

import json
import logging

import redis

from config import KURZZIEL_MOTIVATION, POSTGRES_URL
from memory.ziele import embed_text_bauen, ziel_paar_bestimmen, ziel_speichern
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.memory.kurzziel")

STRECKE_FUER_ZIEL: int = 2   # so viele Lagen mit demselben akuten Objekt erzeugen das Ziel

# Herkuenfte, die eine neue Blase bedeuten — die Strecke beginnt bei eins.
_NEUE_BLASE: frozenset[str] = frozenset({"frisch", "verfallen_neu"})


def normalize_object_name(name: str) -> str:
    """Der Schluessel eines Objekts in der Strecke — die EINZIGE Formel dafuer.

    Vorbedingung: `name` ist eine Zeichenkette.
    Nachbedingung: Kleinschreibung, Leerraum zusammengezogen; leer bleibt leer.
    """
    return " ".join(str(name or "").lower().split())


def build_short_goal_sentence(objekt_name: str, nutzerziel: str) -> str:
    """Der Zielsatz aus Novas Sicht — deterministisch, kein Modell-Call.

    Vorbedingung: `objekt_name` ist nicht leer.
    Nachbedingung: Ein Satz, der wie die uebrigen Ziele mit »Ich moechte«
        beginnt und das Vorhaben woertlich traegt — der `[GEDANKEN]`-Block
        zeigt Zielsaetze unveraendert, und der Leser soll den Anlass erkennen.
        Das Nutzerziel des Turns, in dem das Ziel entstand, steht dahinter,
        wenn es eines gibt.
    Fehlerfaelle: Leerer Objektname ist ein `ValueError`.
    """
    if not objekt_name or not objekt_name.strip():
        raise ValueError("build_short_goal_sentence: objekt_name ist leer — kein Zielsatz baubar")
    satz: str = f"Ich möchte dem Nutzer bei seinem Vorhaben helfen: {objekt_name.strip()}"
    if nutzerziel and nutzerziel.strip():
        satz += f" — {nutzerziel.strip()}"
    return satz


def _key(user_id: str, character_id: str) -> str:
    return f"kurzziel:{user_id}:{character_id}"


def _embed(text: str) -> list[float]:
    """Der Vektor ueber den Embed-Worker — als eigene Funktion, damit Zeugen
    ihn ersetzen koennen, ohne den Worker zu starten.
    """
    return model_service.embed.submit_sync(EmbedRequest(text=text)).embedding


def _stand_lesen(rc: redis.Redis, user_id: str, character_id: str) -> tuple[dict[str, int], dict[str, str]]:
    """Die Strecke aus Redis: (Objekt -> Laenge, Objekt -> Ziel-id)."""
    roh: dict = rc.hgetall(_key(user_id, character_id)) or {}
    try:
        strecken: dict = json.loads(roh["strecken"]) if roh.get("strecken") else {}
        ziele: dict = json.loads(roh["ziele"]) if roh.get("ziele") else {}
    except (ValueError, TypeError, json.JSONDecodeError) as fehler:
        logger.exception(
            "%s: kurzziel: Strecke unlesbar — beginne bei null", type(fehler).__name__,
        )
        return {}, {}
    return (
        {str(k): int(v) for k, v in strecken.items()},
        {str(k): str(v) for k, v in ziele.items()},
    )


def _ziel_anlegen(user_id: str, character_id: str, objekt_name: str, sachlage: dict) -> int | None:
    """Schreibt das kurzfristige Ziel — mit Vektor, wenn der Worker ihn liefert."""
    subjekt, gegenueber = ziel_paar_bestimmen(user_id, character_id)
    zielsatz: str = build_short_goal_sentence(objekt_name, str(sachlage.get("nutzerziel", "") or ""))
    try:
        ziel_embedding: list[float] | None = _embed(embed_text_bauen(zielsatz))
    except Exception as fehler:  # noqa: BLE001 — das Ziel steht auch ohne Vektor
        logger.warning(
            f"kurzziel: Zielsatz-Embedding ausgefallen ({type(fehler).__name__}) "
            f"— Ziel ohne Vektor, die Gravitation findet es nicht"
        )
        ziel_embedding = None
    return ziel_speichern(
        postgres_url = POSTGRES_URL,
        user_id      = subjekt,
        character_id = gegenueber,
        ziel_typ     = "kurzfristig",
        zielsatz     = zielsatz,
        motivation   = KURZZIEL_MOTIVATION,
        emotion      = "",
        arousal      = 0.5,
        thema        = str(sachlage.get("thema", "") or "")[:100],
        embedding    = ziel_embedding,
    )


def short_goal_track(
    rc:           redis.Redis,
    user_id:      str,
    character_id: str,
    sachlage:     dict,
    herkunft:     str,
) -> dict:
    """Verfolgt die akuten Objekte ueber die Lagen und erzeugt kurzfristige Ziele.

    Vorbedingung: `sachlage` ist das gerechnete Artefakt dieses Turns (nicht
        ein uebernommenes), `herkunft` seine Marke.
    Nachbedingung: Ein Dict `{strecken, neu, ziele}` — `strecken` je akutem
        Objekt seine Laenge, `neu` die in diesem Aufruf angelegten Ziel-ids,
        `ziele` alle ids der Strecke. In Redis der Stand fuer den naechsten
        Turn; Objekte, die nicht mehr akut sind, fallen aus der Strecke.
    Fehlerfaelle: Ohne akutes Objekt wird nichts verfolgt und die Strecke
        geleert (`info`). Ein gescheiterter Ziel-Schreiber hinterlaesst keine
        id — beim naechsten Turn wird es erneut versucht.
    """
    # ── Eingabe-Validierung ─────────────────────
    leer: dict = {"strecken": {}, "neu": [], "ziele": {}}
    if not user_id or not character_id:
        logger.error("kurzziel: leeres Paar (%r/%r) — keine Verfolgung", user_id, character_id)
        return leer
    akute: dict[str, str] = {}
    for objekt in sachlage.get("objekte", []) or []:
        if isinstance(objekt, dict) and objekt.get("akut"):
            schluessel: str = normalize_object_name(objekt.get("name", ""))
            if schluessel:
                akute[schluessel] = str(objekt.get("name", "")).strip()

    # ── Verarbeitung ────────────────────────────
    strecken, ziele = _stand_lesen(rc, user_id, character_id)
    if herkunft in _NEUE_BLASE:
        # Eine neue Blase: Was Redis traegt, gehoert zur alten.
        strecken, ziele = {}, {}
    neue_strecken: dict[str, int] = {k: strecken.get(k, 0) + 1 for k in akute}
    neue_ziele: dict[str, str] = {k: v for k, v in ziele.items() if k in akute}
    neu: list[int] = []
    for schluessel, laenge in neue_strecken.items():
        if laenge >= STRECKE_FUER_ZIEL and not neue_ziele.get(schluessel):
            ziel_id = _ziel_anlegen(user_id, character_id, akute[schluessel], sachlage)
            if ziel_id is not None:
                neue_ziele[schluessel] = str(ziel_id)
                neu.append(int(ziel_id))
                logger.info(
                    f"Kurzziel: angelegt (id={ziel_id}, Strecke {laenge}) — "
                    f"Vorhaben '{akute[schluessel][:60]}'"
                )
            else:
                logger.error(
                    f"Kurzziel: Schreiber lieferte keine id fuer '{akute[schluessel][:60]}' "
                    f"— kein Ziel, naechster Turn versucht es erneut"
                )

    try:
        rc.hset(_key(user_id, character_id), mapping={
            "strecken": json.dumps(neue_strecken, ensure_ascii=False),
            "ziele":    json.dumps(neue_ziele, ensure_ascii=False),
        })
    except redis.RedisError as fehler:
        logger.warning(
            f"kurzziel: Strecke nicht gespeichert ({type(fehler).__name__}: {fehler}) "
            f"— der naechste Turn beginnt bei eins"
        )

    # ── Ausgabe ─────────────────────────────────
    if not akute:
        logger.info("Kurzziel: kein akutes Objekt — Strecke geleert")
    else:
        logger.info(
            "Kurzziel: Strecken %s, Ziele %s",
            {akute[k]: v for k, v in neue_strecken.items()},
            {akute[k]: v for k, v in neue_ziele.items()} or "—",
        )
    return {
        "strecken": {akute[k]: v for k, v in neue_strecken.items()},
        "neu": neu,
        "ziele": {akute[k]: int(v) for k, v in neue_ziele.items() if v.isdigit()},
    }
