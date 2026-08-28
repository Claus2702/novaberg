"""Sachlage — das fortgeschriebene Verstehen des Gespraechs.

**Konzept:** `docs/novaberg-thinking-lage_k.md` — die erste Scheibe der
Verstehens-Schicht. Je Turn ein strukturiertes Verstaendnis: worum es geht,
was der Nutzer vermutlich erreichen will, wie er es angeht, welche
Referenzobjekte im Raum stehen und welche ihrer typischen Eigenschaften noch
offen sind.

**Warum der Name nicht `lage` lautet:** `F-LAGE-1..3` besetzen den Begriff
fuer die emotionale Turn-Lage (Achsen, Sektor, Landschaft). Die Sachlage ist
ihre kognitive Schwester — *was* gesagt wird, nicht *wie* — und traegt
deshalb einen eigenen Namen.

**Fortgeschrieben, nicht je Turn frisch** (Konzept §3a): Die vorige Sachlage
ist Eingang des Calls, der neue Turn aktualisiert sie. Sie lebt in Redis
unter dem Paar und verfaellt nach `SACHLAGE_VERFALL_SEKUNDEN` — dieselbe
Ueberlegung wie beim Raum (`ei/raum.py::raum_neutralisieren`): Wer nach
Stunden zurueckkommt, ist nicht mehr in der alten Blase. Anders als der Raum
wird sie nicht gezogen, sondern verworfen: Ein halb verblasstes Verstaendnis
gibt es nicht — entweder die Blase traegt noch, oder das Gespraech beginnt
eine neue.

**Jeder Rueckkehrpfad traegt seine Herkunft** (`22_STILLE_FEHLER` §5): Das
Artefakt sagt in `herkunft`, ob es frisch erhoben, fortgeschrieben, nach
Verfall neu begonnen, auf einem Impuls-Turn unveraendert uebernommen oder
nach einem Ausfall des Calls uebernommen wurde. Ohne dieses Feld waere eine
nicht gerechnete Sachlage von einer gerechneten nicht zu unterscheiden.

**Das Gedaechtnis und die Bruecke** (Konzept §4, Scheibe 4, 28.08.2026):
Jeder gerechnete Turn legt seine Sachlage als Faktum in `sachlage_verlauf`
ab (`memory/sachlage_history.py`; verfaellt nicht, `F-VERFALL-1`). Auf einem
Impuls-Turn baut der Knoten daraus die **Bruecke**: die Verlaufszeile des
Turns, aus dem der Gedanke entstand — hart ueber die `ausloeser_turn_id`
des Ereignisses, sonst ueber die aehnlichste Zeile des Paares, und dann
**als Rueckfall markiert**. Der Verfasser bekommt beide Blasen als
`[SACHLAGE-BRUECKE]` und baut den Uebergang, statt unvermittelt
einzuwerfen. Ohne beide Enden gibt es keine Bruecke und keinen Block.
"""

import json
import logging
import time

from config import (
    POSTGRES_URL,
    SACHLAGE_BRUECKE_MIN_KOSINUS,
    SACHLAGE_VERFALL_SEKUNDEN,
    get_node_config,
    redis_client,
)
from graph.reiz import reiz_ist_eigener_gedanke, reiz_text
from memory.kurzziel import short_goal_track
from memory.pipeline_log import log_berechnung
from memory.sachlage_history import (
    build_embed_text,
    history_nearest,
    history_read_turn,
    history_write,
)
from services.model_services import EmbedRequest, model_service
from services.model_services.types import ChatRequest
from services.pixie.stack import build_impulse_embed_text

logger = logging.getLogger("ki_server.sachlage")

# Die Herkunfts-Marken des Artefakts. Begleitfeld im Sinn von
# `22_STILLE_FEHLER` §3: Jeder Weg, auf dem eine Sachlage im State landet,
# hat genau eine.
HERKUNFT_FRISCH:         str = "frisch"            # kein Vorgaenger, erhoben
HERKUNFT_FORTGESCHRIEBEN: str = "fortgeschrieben"  # Vorgaenger + Turn, erhoben
HERKUNFT_VERFALLEN_NEU:  str = "verfallen_neu"     # Vorgaenger zu alt, frisch erhoben
HERKUNFT_IMPULS:         str = "impuls_uebernommen"  # Novas Impuls, kein Call
HERKUNFT_AUSFALL:        str = "ausfall_uebernommen"  # Call/Parse rot, Vorgaenger steht

# Pflichtfelder des Artefakts — die Ausgabe-Verifikation haelt den Parse
# dagegen, bevor er in den State darf.
_PFLICHTFELDER: tuple[str, ...] = (
    "thema", "gegenstand", "nutzerziel", "ausdrucksweise", "objekte",
)

# Wie die Bruecke ihr zweites Ende gefunden hat — Begleitfeld, damit der
# Verfasser einen belegten Anlass von einem erschlossenen unterscheidet.
BRIDGE_VIA_TURN_ID:   str = "turn_id"             # Verlaufszeile des Ausloesers
BRIDGE_VIA_EMBEDDING: str = "embedding_rueckfall"  # aehnlichste Zeile des Paares

# Wie viele der juengsten Session-Turns der Prompt sieht. Die Sachlage selbst
# traegt die aeltere Historie — mehr Turns doppeln nur, was die Fortschreibung
# schon haelt.
_TURN_FENSTER: int = 6

SACHLAGE_PROMPT: str = """Du analysierst ein laufendes Gespraech. Deine Aufgabe
ist zu verstehen, worum es geht — nicht zu antworten.

{vorige_sektion}

Die juengsten Beitraege:
{verlauf}

Die neue Aeusserung des Nutzers:
{aeusserung}

Erstelle die aktualisierte Sachlage als JSON mit genau diesen Feldern:

{{"thema": "der Name der Sache, ein bis drei Worte",
  "gegenstand": "worum es im Gespraech gerade geht, ein Satz",
  "nutzerziel": "was der Nutzer mit seiner Aeusserung vermutlich erreichen
                 will — das Gesagte muss nicht der Grund sein; schliesse aus
                 Zeichen und Mustern, formuliere als Vermutung",
  "ausdrucksweise": "wie er es angeht: erzaehlend, pruefend, beilaeufig,
                     draengend, begeistert, ...",
  "objekte": [
    {{"name": "das referenzierte Ding, Vorhaben oder Ereignis",
      "klasse": "objekt|person|ort|vorgang|anliegen",
      "akut": true,
      "gedeckt": {{"eigenschaft": "was dazu schon gesagt wurde"}},
      "offen": ["typische Eigenschaften dieser Sache, die noch niemand
                 genannt hat"]}}
  ]}}

Regeln:
- Ein Objekt ist "akut": true nur, wenn es Gegenstand eines konkreten
  Vorhabens oder Sachverhalts ist — zeitliche Naehe, besitzanzeigende oder
  bestimmte Bezuege, Verben des Vorhabens. Eine beilaeufige Bemerkung ist
  latent: "akut": false, und dann bleibt "offen" LEER. Wer auf jede
  Bemerkung mit Eigenschaftsfragen reagiert, wird unertraeglich.
- "offen" nennt nur Eigenschaften, die fuer das Vorhaben wirklich fehlen —
  nach Wichtigkeit geordnet, hoechstens fuenf.
- Fuehre die vorige Sachlage FORT: Was der neue Turn deckt, wandert von
  "offen" nach "gedeckt". Was nicht mehr Gegenstand ist, faellt weg.
- Ein Objekt, das schon in der bisherigen Sachlage steht, behaelt seinen
  "name" WOERTLICH — auch wenn der neue Turn es anders nennt. Ein neues
  Objekt bekommt nur dann einen eigenen Eintrag, wenn es eine andere Sache
  ist, nicht eine Facette derselben.
- Antworte NUR mit dem JSON."""

_VORIGE_SEKTION: str = """Die bisherige Sachlage des Gespraechs:
{vorige}

Der neue Turn setzt dieses Verstaendnis fort."""


def _redis_key(user_id: str, character_id: str) -> str:
    """Der Ablageort der Sachlage — paar-skopiert wie `nova_state`."""
    return f"sachlage:{user_id}:{character_id}"


def sachlage_load(user_id: str, character_id: str) -> tuple[dict | None, bool]:
    """Laedt die vorige Sachlage des Paares aus Redis.

    Vorbedingung: `user_id` und `character_id` sind nicht leer.
    Nachbedingung: (Sachlage oder None, verfallen). `verfallen` ist True,
        wenn eine Sachlage vorlag, aber aelter als die Frist war — der
        Aufrufer beginnt dann frisch und benennt es.
    Fehlerfaelle: Unlesbares JSON oder unlesbarer Zeitstempel sind Defekte,
        werden laut gemeldet und wie „keine Sachlage" behandelt — ein
        kaputter Vorgaenger darf die Erhebung nicht verhindern.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not user_id or not character_id:
        logger.error("sachlage_load: leeres Paar — keine Sachlage geladen")
        return None, False

    roh: dict = redis_client.hgetall(_redis_key(user_id, character_id)) or {}
    if not roh.get("json"):
        return None, False

    # ── Verarbeitung ────────────────────────────
    try:
        vorige: dict = json.loads(roh["json"])
        alter: float = time.time() - float(roh.get("turn_zeit", "0"))
    except (ValueError, TypeError, json.JSONDecodeError) as fehler:
        logger.exception(
            "%s: sachlage_load: Bestand unlesbar — beginne frisch",
            type(fehler).__name__,
        )
        return None, False

    if alter > SACHLAGE_VERFALL_SEKUNDEN:
        logger.info(
            "Sachlage verfallen (%.0f s alt, Frist %.0f s) — die Blase "
            "traegt nicht mehr, das Gespraech beginnt eine neue",
            alter, SACHLAGE_VERFALL_SEKUNDEN,
        )
        return None, True

    # ── Ausgabe ─────────────────────────────────
    return vorige, False


def _sachlage_store(user_id: str, character_id: str, sachlage: dict) -> None:
    """Persistiert die Sachlage samt Zeitstempel fuer den naechsten Turn."""
    try:
        redis_client.hset(_redis_key(user_id, character_id), mapping={
            "json":      json.dumps(sachlage, ensure_ascii=False),
            "turn_zeit": str(time.time()),
        })
    except Exception as fehler:  # Forensik darf den Turn nicht killen
        logger.warning(
            f"Sachlage nicht gespeichert ({type(fehler).__name__}: {fehler}) "
            f"— der naechste Turn beginnt ohne Vorgaenger"
        )


def _validate_artifact(parsed: object) -> dict | None:
    """Haelt den Parse gegen die Pflichtstruktur.

    Vorbedingung: `parsed` ist das Ergebnis eines expect_json-Calls.
    Nachbedingung: Das validierte Artefakt oder None — nie ein halbes.
    Fehlerfaelle: Jede Abweichung wird laut benannt; der Aufrufer entscheidet
        ueber den Rueckkehrpfad und markiert ihn.
    """
    if not isinstance(parsed, dict):
        logger.error(
            f"Sachlage: Parse ist {type(parsed).__name__} statt dict — verworfen"
        )
        return None
    fehlend: list[str] = [f for f in _PFLICHTFELDER if f not in parsed]
    if fehlend:
        logger.error(f"Sachlage: Pflichtfelder fehlen: {fehlend} — verworfen")
        return None
    if not isinstance(parsed["objekte"], list):
        logger.error("Sachlage: 'objekte' ist keine Liste — verworfen")
        return None
    for objekt in parsed["objekte"]:
        if not isinstance(objekt, dict) or "name" not in objekt:
            logger.error(f"Sachlage: Objekt ohne Namen: {objekt!r} — verworfen")
            return None
        # Die Smalltalk-Schranke (Konzept §3, Festlegung 2): Ein latentes
        # Objekt traegt keine offenen Eigenschaften — sonst erzeugt jede
        # Beilaeufigkeit Fragestoff.
        if not objekt.get("akut") and objekt.get("offen"):
            logger.info(
                f"Sachlage: latentes Objekt '{objekt.get('name')}' trug "
                f"offene Eigenschaften — geleert (Smalltalk-Schranke)"
            )
            objekt["offen"] = []
    return parsed


def _render_history(session_turns: list[dict]) -> str:
    """Die juengsten Turns als Verlaufszeilen fuer den Prompt."""
    zeilen: list[str] = []
    for turn in session_turns[-_TURN_FENSTER:]:
        sprecher: str = "Nutzer" if turn.get("rolle") == "user" else "Nova"
        inhalt: str = (turn.get("inhalt") or "").strip()
        if inhalt:
            zeilen.append(f"{sprecher}: {inhalt[:400]}")
    return "\n".join(zeilen) if zeilen else "(noch keine Beitraege)"


def _derive(
    vorige:        dict | None,
    session_turns: list[dict],
    aeusserung:    str,
) -> dict | None:
    """Der LLM-Call — erzwungenes JSON, validiert gegen die Pflichtstruktur.

    Vorbedingung: `aeusserung` ist nicht leer.
    Nachbedingung: Das validierte Artefakt oder None bei Ausfall.
    Fehlerfaelle: Ausnahmen des Workers werden gefangen und laut gemeldet —
        der Turn laeuft weiter, der Aufrufer markiert den Rueckkehrpfad.
    """
    vorige_sektion: str = (
        _VORIGE_SEKTION.format(vorige=json.dumps(vorige, ensure_ascii=False))
        if vorige else "Es gibt noch keine Sachlage — dies ist der Anfang."
    )
    prompt: str = SACHLAGE_PROMPT.format(
        vorige_sektion = vorige_sektion,
        verlauf        = _render_history(session_turns),
        aeusserung     = aeusserung.strip()[:1200],
    )
    node_cfg: dict = get_node_config("sachlage")
    try:
        response = model_service.chat.submit_sync(ChatRequest(
            messages          = [{"role": "user", "content": prompt}],
            temperature       = node_cfg.get("temperature", 0.1),
            max_output_tokens = node_cfg.get("max_output_tokens", 768),
            expect_json       = True,
            caller            = "sachlage",
        ), timeout=node_cfg.get("timeout_s", 60.0))
    except Exception as fehler:
        logger.error(
            f"Sachlage-Call ausgefallen ({type(fehler).__name__}: {fehler})"
        )
        return None
    return _validate_artifact(response.parsed)


def _persist_history(
    user_id:      str,
    character_id: str,
    turn_id:      str,
    sachlage:     dict,
) -> None:
    """Legt die gerechnete Sachlage als Faktum in `sachlage_verlauf` ab.

    Vorbedingung: `sachlage` ist validiert und traegt `herkunft`.
    Nachbedingung: Eine Zeile, mit Vektor ueber den Gegenstand-Satz — oder
        ohne Vektor, wenn der Embed-Worker ausfaellt; das Faktum steht
        trotzdem.
    Fehlerfaelle: Nichts hier wirft. Ein Ausfall ist laut (Repository) und
        kostet den Turn nicht.
    """
    embedding: list[float] | None
    try:
        antwort = model_service.embed.submit_sync(
            EmbedRequest(text=build_embed_text(str(sachlage.get("gegenstand", ""))))
        )
        embedding = antwort.embedding
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.warning(
            f"Sachlage-Verlauf: Embedding ausgefallen ({type(fehler).__name__}: "
            f"{fehler}) — Zeile ohne Vektor"
        )
        embedding = None
    history_write(
        POSTGRES_URL, turn_id=turn_id, user_id=user_id,
        character_id=character_id, sachlage=sachlage, embedding=embedding,
    )


def _track_short_goal(
    user_id:      str,
    character_id: str,
    turn_id:      str,
    sachlage:     dict,
) -> None:
    """Die Zielverfolgung, mit eigener Protokollzeile.

    Vorbedingung: `sachlage` ist gerechnet und traegt `herkunft`.
    Nachbedingung: Die Strecke in Redis ist fortgeschrieben; eine
        `berechnung`-Zeile `node='kurzziel'` traegt Strecke, Kosinus und
        Ziel-id — auch wenn kein Ziel entstand.
    Fehlerfaelle: Nichts hier wirft; die Verfolgung meldet selbst.
    """
    try:
        ergebnis: dict = short_goal_track(
            redis_client, user_id, character_id, sachlage, str(sachlage.get("herkunft", "")),
        )
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.error(
            f"Kurzziel: Verfolgung ausgefallen ({type(fehler).__name__}: {fehler})"
        )
        return
    try:
        log_berechnung(
            turn_id=turn_id, node="kurzziel", quelle="character_graph",
            inhalt=ergebnis, user_id=user_id, character_id=character_id,
        )
    except Exception as fehler:  # noqa: BLE001 — Forensik darf den Turn nicht killen
        logger.warning(f"Kurzziel-Protokoll nicht geschrieben ({type(fehler).__name__})")


def _impulse_embedding(state: dict) -> list[float] | None:
    """Rechnet das Embedding des Impulses nach — aus derselben Formel wie
    der Stapel (`build_impulse_embed_text`), damit die Suche den Vektor
    trifft, den `stack_push` abgelegt hat.

    Nachbedingung: Der Vektor, oder None ohne Thema und Gedanke oder bei
        Ausfall des Workers — beides laut.
    """
    payload: dict = state.get("event_payload") or {}
    thema:  str = str(payload.get("prompt_thema", "") or "")
    inhalt: str = str(payload.get("eigener_gedanke", "") or "")
    if not thema and not inhalt:
        logger.info("Sachlage-Bruecke: Impuls ohne Thema und Gedanke — kein Rueckfall")
        return None
    try:
        return model_service.embed.submit_sync(
            EmbedRequest(text=build_impulse_embed_text(thema, inhalt))
        ).embedding
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.warning(
            f"Sachlage-Bruecke: Impuls-Embedding ausgefallen "
            f"({type(fehler).__name__}: {fehler}) — kein Rueckfall"
        )
        return None


def sachlage_bridge_build(state: dict, aktuell: dict) -> dict:
    """Die Bruecke eines Impuls-Turns zu seinem Anlass.

    Vorbedingung: `state` ist ein Impuls-Turn (`reiz_ist_eigener_gedanke`).
    Nachbedingung: Ein Dict mit `damals` (Verlaufszeile des Ausloesers),
        `aktuell`, `ausloeser_turn_id` und `weg` — oder `{}`, wenn es kein
        zweites Ende gibt. **Der Weg steht immer dabei:** harte `turn_id`
        oder Embedding-Rueckfall mit `kosinus`.
    Fehlerfaelle: Eine `turn_id` ins Leere (Ausloeser vor dem Bau der
        Tabelle) faellt auf die Suche zurueck; alles andere ist ein leeres
        Dict mit Meldung.
    """
    # ── Eingabe-Validierung ─────────────────────
    payload: dict = state.get("event_payload") or {}
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")
    ausloeser: str | None = payload.get("ausloeser_turn_id") or None

    # ── Verarbeitung ────────────────────────────
    if ausloeser:
        zeile: dict | None = history_read_turn(POSTGRES_URL, ausloeser)
        if zeile is not None:
            return {
                "weg": BRIDGE_VIA_TURN_ID, "ausloeser_turn_id": ausloeser,
                "damals": zeile, "aktuell": aktuell,
            }
        logger.info(
            f"Sachlage-Bruecke: keine Verlaufszeile fuer Ausloeser turn={ausloeser} "
            f"— Rueckfall auf die Vektorsuche"
        )

    embedding: list[float] | None = _impulse_embedding(state)
    if embedding is None:
        return {}
    treffer: dict | None = history_nearest(
        POSTGRES_URL, user_id, character_id, embedding, SACHLAGE_BRUECKE_MIN_KOSINUS,
    )
    if treffer is None:
        logger.info("Sachlage-Bruecke: kein zweites Ende — keine Bruecke")
        return {}

    # ── Ausgabe ─────────────────────────────────
    return {
        "weg": BRIDGE_VIA_EMBEDDING, "ausloeser_turn_id": treffer["turn_id"],
        "kosinus": treffer["kosinus"], "damals": treffer, "aktuell": aktuell,
    }


def sachlage_bridge_block(bruecke: dict) -> str:
    """Der [SACHLAGE-BRUECKE]-Block fuer den Verfasser: beide Blasen und der
    Auftrag, den Uebergang hoerbar zu bauen.

    Vorbedingung: `bruecke` traegt `damals`.
    Nachbedingung: Ein Block, der mit `[SACHLAGE-BRUECKE]` beginnt und den
        Anlass als belegt oder als vermutet benennt.
    """
    damals:  dict = bruecke.get("damals") or {}
    aktuell: dict = bruecke.get("aktuell") or {}
    if bruecke.get("weg") == BRIDGE_VIA_EMBEDDING:
        anlass: str = (
            f"Der Anlass ist erschlossen, nicht belegt — vermutlich dieses "
            f"fruehere Gespraech (Aehnlichkeit {float(bruecke.get('kosinus', 0.0)):.2f})."
        )
    else:
        anlass = "Der Anlass ist belegt: das Gespraech, aus dem der Gedanke entstand."
    zeilen: list[str] = [
        "[SACHLAGE-BRUECKE]",
        f"Dein Gedanke entstand frueher. {anlass}",
        f"Damals ging es um: {damals.get('gegenstand', '')} ({damals.get('thema', '')})",
        f"Was der Nutzer damals wollte: {damals.get('nutzerziel', '')}",
    ]
    if aktuell.get("gegenstand"):
        zeilen.append(f"Jetzt geht es um: {aktuell.get('gegenstand', '')}")
    else:
        zeilen.append("Jetzt: Das Gespraech hat gerade keinen Gegenstand — eine Pause.")
    zeilen.append(
        "Baue den Uebergang hoerbar: Sag, woran du anknuepfst, bevor du den "
        "Gedanken einbringst — wirf ihn nicht unvermittelt ein."
    )
    return "\n".join(zeilen)


def sachlage_block(sachlage: dict) -> str:
    """Der [SACHLAGE]-Block fuer Verfasser und Gespraechsvektor.

    Vorbedingung: `sachlage` traegt die Pflichtfelder.
    Nachbedingung: Ein Block, der mit `[SACHLAGE]` beginnt; offene
        Eigenschaften stehen nur bei akuten Objekten.
    """
    zeilen: list[str] = [
        "[SACHLAGE]",
        f"Worum es geht: {sachlage.get('gegenstand', '')}",
        f"Was der Nutzer vermutlich will: {sachlage.get('nutzerziel', '')}",
        f"Wie er es angeht: {sachlage.get('ausdrucksweise', '')}",
    ]
    for objekt in sachlage.get("objekte", []):
        if objekt.get("akut") and objekt.get("offen"):
            offen: str = ", ".join(str(o) for o in objekt["offen"][:5])
            zeilen.append(
                f"Im Raum steht: {objekt.get('name')} — dazu noch offen: {offen}"
            )
    return "\n".join(zeilen)


def sachlage_assess(state: dict) -> dict:
    """Der Knoten: laedt, schreibt fort, protokolliert.

    Vorbedingung: `state` traegt `user_id`, `character_id`, `turn_id`.
    Nachbedingung: `state["sachlage"]` ist ein dict mit `herkunft` — auf
        jedem Weg, auch bei Ausfall (F-LOG-3: der Rueckkehrpfad setzt das
        Protokollfeld).
    Fehlerfaelle: Ein Ausfall des Calls uebernimmt den Vorgaenger und
        markiert das; ohne Vorgaenger steht ein leeres Artefakt mit Marke.
    """
    # ── Eingabe-Validierung ─────────────────────
    user_id:      str = state.get("user_id", "")
    character_id: str = state.get("character_id", "")
    vorige, verfallen = sachlage_load(user_id, character_id)
    impuls: bool = reiz_ist_eigener_gedanke(state)

    # Die Groessen der Weiche, BEVOR sie entscheidet (F-LOG-3): Welcher der
    # fuenf Wege gleich genommen wird, haengt an genau diesen dreien.
    logger.info(
        f"Sachlage Eingang: vorgaenger={'ja' if vorige else 'nein'}, "
        f"verfallen={verfallen}, impuls={impuls}, "
        f"reiz={len(reiz_text(state))} Zeichen"
    )

    # ── Verarbeitung ────────────────────────────
    if impuls:
        # Novas eigener Impuls sagt nichts Neues ueber das Nutzerziel.
        # Die Blase bleibt, wie sie ist — und dass sie nicht gerechnet
        # wurde, steht in der Marke.
        sachlage: dict = dict(vorige or {})
        sachlage["herkunft"] = HERKUNFT_IMPULS
        bruecke: dict = sachlage_bridge_build(state, sachlage)
    else:
        bruecke = {}
        erhoben: dict | None = _derive(
            vorige, state.get("session_turns") or [], reiz_text(state),
        )
        if erhoben is not None:
            erhoben["herkunft"] = (
                HERKUNFT_VERFALLEN_NEU if verfallen
                else HERKUNFT_FORTGESCHRIEBEN if vorige
                else HERKUNFT_FRISCH
            )
            sachlage = erhoben
            _sachlage_store(user_id, character_id, sachlage)
            # Das Faktum: nur gerechnete Artefakte, keine uebernommenen.
            _persist_history(
                user_id, character_id, state.get("turn_id", ""), sachlage,
            )
            # Scheibe 2: Zeigt die Blase zum zweiten Mal auf dasselbe
            # Nutzerziel, entsteht das kurzfristige Ziel (memory/kurzziel.py).
            _track_short_goal(user_id, character_id, state.get("turn_id", ""), sachlage)
        else:
            sachlage = dict(vorige or {})
            sachlage["herkunft"] = HERKUNFT_AUSFALL

    # ── Ausgabe-Verifikation ────────────────────
    if "herkunft" not in sachlage:
        raise ValueError("Sachlage ohne Herkunft — ein Weg wurde nicht markiert")
    try:
        log_berechnung(
            turn_id      = state.get("turn_id", ""),
            node         = "sachlage",
            quelle       = "character_graph",
            inhalt       = sachlage,
            user_id      = user_id,
            character_id = character_id,
        )
    except Exception as fehler:
        logger.warning(
            f"Sachlage-Protokoll nicht geschrieben ({type(fehler).__name__}: "
            f"{fehler}) — der Turn laeuft weiter, die Reihe hat eine Luecke"
        )
    state["sachlage"] = sachlage
    state["sachlage_bruecke"] = bruecke
    if bruecke:
        logger.info(
            f"Sachlage-Bruecke [{bruecke['weg']}]: Ausloeser turn="
            f"{bruecke['ausloeser_turn_id']}, damals='{str(bruecke['damals'].get('thema', ''))[:40]}'"
        )
    logger.info(
        f"Sachlage [{sachlage['herkunft']}]: "
        f"Gegenstand='{str(sachlage.get('gegenstand', ''))[:80]}', "
        f"{len(sachlage.get('objekte', []))} Objekte"
    )
    return state
