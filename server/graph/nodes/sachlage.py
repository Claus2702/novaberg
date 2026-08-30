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

**Der Frame-Aufloeser** (Konzept §4, Scheibe 6, 28.08.2026): Auf dem
rechnenden Weg baut `graph/nodes/sachlage_resolver.py` ein nummeriertes
Angebot aus dem Gedaechtnis-Pool des Turns; nach dem Sachlage-Call haelt
ein eigener, kleiner Call die offenen Eigenschaften der akuten Objekte
dagegen. Eine Eigenschaft, die ein angebotener Eintrag beantwortet, wandert
nach `gedeckt` und traegt in `quellen` ihre Herkunft — sie ist damit kein
Rueckfrage-Gegenstand mehr. Der Sachlage-Prompt selbst bleibt unveraendert.

**Die Plausibilitaetspruefung** (Konzept §4, Scheibe 7, 29.08.2026): Traegt
die Sachlage ein akutes Objekt, prueft ein weiterer kleiner Call
(`graph/nodes/sachlage_plausibility.py`), ob die Aeusserung des Nutzers eine
Behauptung enthaelt, die dem Weltwissen widerspricht — vier Stufen aus
Frames §6.2, im Artefakt stehen nur die drei ueber `plausibel`, und der
Block nennt sie dem Verfasser als Zweifel.

**Der Wissenstraeger** (Konzept §4, Scheibe 8, 29.08.2026): Jede offene
Eigenschaft traegt, wer sie kennen kann — `nutzer`, `welt` oder
`nachschlagen` (im Sachlage-Call, denn *wer kann das wissen* ist Teil des
Verstehens). Nur eine `nutzer`-Eigenschaft ist ein Rueckfrage-Gegenstand;
die anderen sind Antwortstoff fuer den Verfasser (`answer_targets`), und
fuer die erste `nachschlagen`-Eigenschaft ohne Deckung laeuft eine Websuche
(`graph/nodes/sachlage_research.py`). Ohne Traeger gilt `nutzer`.

**Das Gewicht einer Luecke** (Konzept §4, Scheibe 10, 30.08.2026): Jede
offene Eigenschaft traegt neben ihrem Traeger, ob eine Antwort ohne sie
raten muesste — `kritisch` oder `unkritisch`. Der Traeger sagt *wer kann es
wissen*, die Kritikalitaet *was kostet es, wenn niemand es sagt*. Nur eine
kritische Luecke zieht den Rueckfrage-Gegenstand vor (`question_target`
sucht sie in einem ersten Durchgang, bevor die Reihenfolge in `offen`
entscheidet), und nur sie bekommt eine eigene Zeile im Block. Ohne Wert
gilt `unkritisch` — das Verhalten vor der Scheibe.

**Der Sprecher** (Konzept §4, Scheibe 9, 29.08.2026): Jede gedeckte
Eigenschaft eines akuten Objekts traegt, wer sie gesagt hat — `nutzer` oder
`nova` —, denn Deckung kommt von beiden Seiten, und der Gedanke des Nutzers
bleibt seiner. Der Block nennt es dem Verfasser (`speaker_lines`); ohne
Sprecher keine Zeile. Kein Raten: Ist der Sprecher in den juengsten
Beitraegen nicht zu sehen, bleibt die Eigenschaft ohne — an einem latenten
Objekt gibt es keinen Sprecher, weil das Fenster ihn dort nicht deckt
(gemessen 29.08.2026: drei von sieben geraten, zwei davon vertauscht).
"""

import json
import logging
import re
import time
from datetime import datetime, timezone

from config import (
    POSTGRES_URL,
    SACHLAGE_BRUECKE_MIN_KOSINUS,
    SACHLAGE_VERFALL_SEKUNDEN,
    SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS,
    get_node_config,
    redis_client,
)
from graph.nodes.sachlage_plausibility import (
    apply_plausibility,
    assess_plausibility,
    has_acute_object,
)
from graph.nodes.sachlage_research import research_open_property
from graph.nodes.sachlage_resolver import (
    SOURCE_LABELS,
    MemoryHit,
    apply_memory_coverage,
    carry_sources,
    memory_offer,
    open_properties,
    resolve_open_properties,
)
from graph.reiz import reiz_ist_eigener_gedanke, reiz_text
from memory.kurzziel import normalize_object_name, short_goal_track
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

# Scheibe 8: wer eine offene Eigenschaft kennen kann. `nutzer` ist der
# Rueckfall fuer Artefakte ohne Traeger — das Verhalten vor der Scheibe.
TRAEGER_NUTZER:       str = "nutzer"        # nur der Nutzer: Vorhaben, Leute, Wahl
TRAEGER_WELT:         str = "welt"          # allgemeines Wissen, aus dem Kopf
TRAEGER_NACHSCHLAGEN: str = "nachschlagen"  # Weltwissen, aber speziell/aktuell/zahlengenau
TRAEGER_KANON: frozenset[str] = frozenset({TRAEGER_NUTZER, TRAEGER_WELT, TRAEGER_NACHSCHLAGEN})

# Scheibe 10 (30.08.2026): das Gewicht einer Luecke. Der Traeger sagt, WER
# sie schliessen kann; die Kritikalitaet sagt, OB die Antwort ohne sie raten
# muesste. Nur eine kritische Luecke zieht die Rueckfrage vor.
KRITISCH:   str = "kritisch"
UNKRITISCH: str = "unkritisch"
KRITIKALITAET_KANON: frozenset[str] = frozenset({KRITISCH, UNKRITISCH})
ANTWORT_TRAEGER: frozenset[str] = frozenset({TRAEGER_WELT, TRAEGER_NACHSCHLAGEN})

# Scheibe 9: wer eine gedeckte Eigenschaft gesagt hat. Der Gedanke des
# Nutzers bleibt seiner, Novas bleibt ihrer — der Verfasser hoert beides.
SPRECHER_NUTZER: str = "nutzer"
SPRECHER_NOVA:   str = "nova"
SPRECHER_KANON: frozenset[str] = frozenset({SPRECHER_NUTZER, SPRECHER_NOVA})

# Scheibe 3, Nachtrag (29.08.2026 abends): woher der Rueckfrage-Gegenstand
# stammt. Aus der Blase — eine offene Eigenschaft des Nutzers oder das
# Kurzziel zu einem akuten Objekt — oder Novas eigener Zug: das staerkste
# Kurzziel, dessen Sache nicht in der Blase steht. Die Gravitation bleibt;
# der Verfasser erfaehrt nur, wessen Zug es ist.
GEGENSTAND_AUS_BLASE:  str = "blase"
GEGENSTAND_EIGENER_ZUG: str = "eigener_zug"

# Der Leser des [SACHLAGE]-Blocks bestimmt die Namen (29.08.2026 spaet): Der
# Verfasser bekommt einen Auftrag ueber PERSON A und PERSON B — das Modell
# ist der Schauspieler, der Charakter der Auftrag, und nirgends wird es als
# der Charakter angesprochen. Der Gespraechsvektor analysiert in dritter
# Person und kennt Nova und den Nutzer beim Namen. Ein Block, der »Nova«,
# »der Nutzer« und »dein Wissen« in den Verfasser-Prompt traegt, ist ein
# zweites und drittes Namenssystem — die am 13.08.2026 gemessene Fehlerklasse.
LESER_VERFASSER: str = "verfasser"
LESER_GV:        str = "gv"
_NAMEN: dict[str, dict[str, str]] = {
    LESER_VERFASSER: {"nova": "Person A", "nutzer": "Person B", "Nutzer": "Person B"},
    LESER_GV:        {"nova": "Nova",     "nutzer": "der Nutzer", "Nutzer": "Der Nutzer"},
}

# Wie die Bruecke ihr zweites Ende gefunden hat — Begleitfeld, damit der
# Verfasser einen belegten Anlass von einem erschlossenen unterscheidet.
BRIDGE_VIA_TURN_ID:   str = "turn_id"             # Verlaufszeile des Ausloesers
BRIDGE_VIA_EMBEDDING: str = "embedding_rueckfall"  # aehnlichste Zeile des Paares

# Wie viele der juengsten Session-Turns der Prompt sieht. Die Sachlage selbst
# traegt die aeltere Historie — mehr Turns doppeln nur, was die Fortschreibung
# schon haelt.
_TURN_FENSTER: int = 6
# Wie viel von einem Beitrag der Prompt sieht. `[gemessen]` 28.08.2026: Der
# Schnitt stand auf 400; Novas Antworten des Paares waren 183 bis 1557 Zeichen
# lang (6 von 11 ueber 400), und eine Regieanweisung frisst die ersten 100 bis
# 400 davon. Eine offene Eigenschaft blieb drei Turns offen, weil die Antwort,
# die sie deckte, bei Zeichen 384 begann und bei 400 endete. Die Grenze liegt
# jetzt ueber der laengsten gemessenen Antwort; Regieanweisungen fallen vorher.
_BEITRAG_MAX_ZEICHEN: int = 1600
# Regieanweisungen (*…*) tragen Gestik, keine Sache — fuer das Verstehen des
# Gegenstands sind sie Rauschen und kosten die Zeichen, die die Antwort braucht.
_REGIEANWEISUNG: re.Pattern = re.compile(r"\*[^*\n]{1,400}\*")

SACHLAGE_PROMPT: str = """Du analysierst ein laufendes Gespraech. Deine Aufgabe
ist zu verstehen, worum es geht — nicht zu antworten.

{vorige_sektion}
{wiederaufnahme_sektion}
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
                 genannt hat"],
      "traeger": {{"erste Eigenschaft aus offen": "nutzer|welt|nachschlagen",
                   "zweite Eigenschaft aus offen": "nutzer|welt|nachschlagen"}},
      "kritikalitaet": {{"erste Eigenschaft aus offen": "kritisch|unkritisch",
                         "zweite Eigenschaft aus offen": "kritisch|unkritisch"}},
      "sprecher": {{"erste Eigenschaft aus gedeckt": "nutzer|nova",
                    "zweite Eigenschaft aus gedeckt": "nutzer|nova"}}}}
  ]}}

Regeln:
- Ein Objekt ist "akut": true nur, wenn es Gegenstand eines konkreten
  Vorhabens oder Sachverhalts ist — zeitliche Naehe, besitzanzeigende oder
  bestimmte Bezuege, Verben des Vorhabens. Eine beilaeufige Bemerkung ist
  latent: "akut": false, und dann bleibt "offen" LEER. Wer auf jede
  Bemerkung mit Eigenschaftsfragen reagiert, wird unertraeglich.
- "offen" nennt nur Eigenschaften, die fuer das Vorhaben wirklich fehlen —
  nach Wichtigkeit geordnet, hoechstens fuenf.
- "traeger" sagt je offener Eigenschaft, wer sie kennen kann: "nutzer" —
  nur der Nutzer (sein Vorhaben, seine Leute, seine Wahl, sein Erleben);
  "welt" — allgemeines Wissen, aus dem Kopf zu beantworten; "nachschlagen"
  — Weltwissen, aber speziell, aktuell oder zahlengenau. JEDE Eigenschaft
  aus "offen" bekommt genau einen Traeger — auch eine fortgefuehrte, deren
  Eintrag in der bisherigen Sachlage noch keinen hatte.
- "kritikalitaet" sagt je offener Eigenschaft, ob eine Antwort ohne sie
  raten muesste: "kritisch" — ohne diese Angabe traegt jede Antwort einen
  geratenen Kern, die Sache selbst bleibt unbestimmt; "unkritisch" — die
  Antwort steht auch ohne sie, die Angabe macht sie nur genauer. Die Probe
  ist die Antwort, nicht die Neugier: Laesst sich der Satz sinnvoll
  formulieren, ist die Luecke unkritisch. Meist ist hoechstens eine
  Eigenschaft kritisch; JEDE Eigenschaft aus "offen" bekommt genau einen
  Wert — auch eine fortgefuehrte.
- Fuehre die vorige Sachlage FORT: Was der neue Turn deckt, wandert von
  "offen" nach "gedeckt". Was nicht mehr Gegenstand ist, faellt weg.
- Deckung kommt von beiden Seiten: Auch was Nova in den juengsten Beitraegen
  bereits beantwortet hat, deckt die Eigenschaft. Offen bleibt nur, was
  weder der Nutzer noch Nova genannt hat.
- "sprecher" sagt je gedeckter Eigenschaft eines AKUTEN Objekts, wer sie
  genannt hat: "nutzer" oder "nova" — auch fuer eine fortgefuehrte
  Eigenschaft, deren Eintrag in der bisherigen Sachlage noch keinen hatte.
  Was Nova in den juengsten Beitraegen gesagt hat, traegt "nova"; was der
  Nutzer gesagt hat, "nutzer". Ist in den juengsten Beitraegen und der
  bisherigen Sachlage NICHT zu sehen, wer es gesagt hat, laesst du die
  Eigenschaft in "sprecher" weg — ein geratener Sprecher ist schlimmer als
  keiner. Ein latentes Objekt traegt kein "sprecher".
- "thema" und "gegenstand" benennen die Sache selbst. Wechselt der Turn
  die Sache, nennen beide die neue Sache (etwa "Neutronensterne" / "Warum
  Neutronensterne ohne Fusion leuchten"), und die alte faellt aus der
  Sachlage. Das Gespraech ueber die Sache — ein Themenwechsel, eine
  Rueckkehr, dass der Nutzer fragt — ist nie der Gegenstand.
- Ein Objekt, das schon in der bisherigen Sachlage steht, behaelt seinen
  "name" WOERTLICH — auch wenn der neue Turn es anders nennt. Ein neues
  Objekt bekommt nur dann einen eigenen Eintrag, wenn es eine andere Sache
  ist, nicht eine Facette derselben.
- Antworte NUR mit dem JSON."""

_VORIGE_SEKTION: str = """Die bisherige Sachlage des Gespraechs:
{vorige}

Der neue Turn setzt dieses Verstaendnis fort."""

# Scheibe 5: die fruehere Blase, die der Turn vermutlich wieder aufnimmt.
_WIEDERAUFNAHME_SEKTION: str = """
Eine fruehere Sachlage dieses Gespraechs zu einer aehnlichen Sache (Thema
"{thema}", {alter}):
{objekte}

Kehrt der neue Turn zu dieser Sache zurueck, fuehre SIE fort: Ihr Objekt
behaelt seinen "name" woertlich, was dort "gedeckt" ist, bleibt gedeckt.
Was der Turn sonst noch nennt, bleibt ein eigenes Objekt. Geht es um etwas
anderes, lass sie unbeachtet.
"""


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
        objekt["traeger"] = _normalize_holders(objekt)
        objekt["kritikalitaet"] = _normalize_criticality(objekt)
        objekt["sprecher"] = _normalize_speakers(objekt)
    return parsed


def _normalize_holders(objekt: dict) -> dict[str, str]:
    """Scheibe 8: die Wissenstraeger der offenen Eigenschaften, gegen den Kanon gehalten.

    Vorbedingung: `objekt` ist ein Objekt des Parses.
    Nachbedingung: Ein dict Eigenschaft → Traeger aus TRAEGER_KANON, nur fuer
        Eigenschaften, die in `offen` stehen; ein fehlender Traeger bleibt
        fehlend — der Leser behandelt ihn wie `nutzer` (das Verhalten vor
        der Scheibe). Unbekannte Werte und fremde Schluessel fallen laut.
    """
    roh: object = objekt.get("traeger")
    if roh is None:
        return {}
    if not isinstance(roh, dict):
        logger.warning(
            f"Sachlage: 'traeger' an '{objekt.get('name')}' ist "
            f"{type(roh).__name__} statt dict — verworfen"
        )
        return {}
    offen: dict[str, str] = {_holder_key(o): str(o) for o in objekt.get("offen") or []}
    traeger: dict[str, str] = {}
    for eigenschaft, wert in roh.items():
        wert_norm: str = str(wert).strip().lower()
        schluessel: str = _holder_key(eigenschaft)
        if wert_norm not in TRAEGER_KANON:
            logger.warning(
                f"Sachlage: Traeger {wert!r} an '{eigenschaft}' ({objekt.get('name')}) "
                f"steht nicht im Kanon {TRAEGER_KANON} — verworfen"
            )
            continue
        if schluessel not in offen:
            logger.info(
                f"Sachlage: Traeger an '{eigenschaft}' ({objekt.get('name')}) — "
                f"die Eigenschaft steht nicht in offen, verworfen"
            )
            continue
        traeger[offen[schluessel]] = wert_norm
    return traeger


def _normalize_criticality(objekt: dict) -> dict[str, str]:
    """Scheibe 10: das Gewicht der offenen Eigenschaften, gegen den Kanon gehalten.

    Gebaut wie `_normalize_holders`, und aus demselben Grund: Ein Wert, den
    das Modell vergibt, ist erst ein Wert, wenn er im Kanon steht — sonst ist
    ein Tippfehler von einer Aussage nicht zu unterscheiden.

    Vorbedingung: `objekt` ist ein Objekt des Parses.
    Nachbedingung: Ein dict Eigenschaft → Wert aus KRITIKALITAET_KANON, nur
        fuer Eigenschaften, die in `offen` stehen. Ein fehlender Eintrag
        bleibt fehlend — der Leser behandelt ihn wie `unkritisch`, also wie
        das Verhalten vor der Scheibe. Unbekannte Werte fallen laut.
    """
    roh: object = objekt.get("kritikalitaet")
    if roh is None:
        return {}
    if not isinstance(roh, dict):
        logger.warning(
            f"Sachlage: 'kritikalitaet' an '{objekt.get('name')}' ist "
            f"{type(roh).__name__} statt dict — verworfen"
        )
        return {}
    offen: dict[str, str] = {_holder_key(o): str(o) for o in objekt.get("offen") or []}
    gewichte: dict[str, str] = {}
    for eigenschaft, wert in roh.items():
        wert_norm: str = str(wert).strip().lower()
        schluessel: str = _holder_key(eigenschaft)
        if wert_norm not in KRITIKALITAET_KANON:
            logger.warning(
                f"Sachlage: Kritikalitaet {wert!r} an '{eigenschaft}' "
                f"({objekt.get('name')}) steht nicht im Kanon "
                f"{KRITIKALITAET_KANON} — verworfen"
            )
            continue
        if schluessel not in offen:
            logger.info(
                f"Sachlage: Kritikalitaet an '{eigenschaft}' ({objekt.get('name')}) — "
                f"die Eigenschaft steht nicht in offen, verworfen"
            )
            continue
        gewichte[offen[schluessel]] = wert_norm
    return gewichte


def carry_criticality(artifact: dict, previous: dict | None) -> dict:
    """Scheibe 10: fehlende Gewichte aus der vorigen Blase erben.

    Dieselbe Lehre wie `carry_holders`: Der Fortfuehrungsfall ist der, in dem
    das Modell ein neues Feld weglaesst, weil die vorige Blase es nicht trug.

    Vorbedingung: `artifact` validiert; `previous` ein Artefakt oder None.
    Nachbedingung: `kritikalitaet` jedes akuten Objekts umfasst die geerbten
        Eintraege; vorhandene bleiben unberuehrt.
    """
    if not previous:
        return artifact
    vorige: dict[str, dict] = {
        _holder_key(o.get("name", "")): {
            _holder_key(k): v for k, v in (o.get("kritikalitaet") or {}).items()
        }
        for o in previous.get("objekte") or [] if isinstance(o, dict)
    }
    for objekt in artifact.get("objekte") or []:
        if not objekt.get("akut"):
            continue
        geerbt: dict = vorige.get(_holder_key(objekt.get("name", "")), {})
        if not geerbt:
            continue
        gewichte: dict = objekt.setdefault("kritikalitaet", {})
        for eigenschaft in objekt.get("offen") or []:
            schluessel: str = _holder_key(eigenschaft)
            if str(eigenschaft) not in gewichte and schluessel in geerbt:
                gewichte[str(eigenschaft)] = geerbt[schluessel]
    return artifact


def carry_holders(artifact: dict, previous: dict | None) -> dict:
    """Scheibe 8: fehlende Traeger aus der vorigen Blase erben.

    `[gemessen]` 29.08.2026: Ohne Vorgaenger gab das Modell 90 von 90 offenen
    Eigenschaften einen Traeger; bei der Fortschreibung einer Blase, deren
    Objekte noch keinen trugen, liess es das Feld ganz weg. Eine Eigenschaft,
    die schon in der vorigen Blase offen war und dort einen Traeger hatte,
    behaelt ihn; nur was auch dort keinen hatte, bleibt ohne (= `nutzer`).

    Vorbedingung: `artifact` validiert; `previous` ein Artefakt oder None.
    Nachbedingung: `traeger` jedes akuten Objekts umfasst die geerbten
        Eintraege; vorhandene bleiben unberuehrt.
    """
    if not previous:
        return artifact
    vorige: dict[str, dict] = {
        _holder_key(o.get("name", "")): {
            _holder_key(k): v for k, v in (o.get("traeger") or {}).items()
        }
        for o in previous.get("objekte") or [] if isinstance(o, dict)
    }
    for objekt in artifact.get("objekte") or []:
        if not objekt.get("akut"):
            continue
        geerbt: dict = vorige.get(_holder_key(objekt.get("name", "")), {})
        if not geerbt:
            continue
        traeger: dict = objekt.setdefault("traeger", {})
        for eigenschaft in objekt.get("offen") or []:
            schluessel: str = _holder_key(eigenschaft)
            if str(eigenschaft) not in traeger and schluessel in geerbt:
                traeger[str(eigenschaft)] = geerbt[schluessel]
    return artifact


def _normalize_speakers(objekt: dict) -> dict[str, str]:
    """Scheibe 9: die Sprecher der gedeckten Eigenschaften, gegen den Kanon gehalten.

    Vorbedingung: `objekt` ist ein Objekt des Parses.
    Nachbedingung: Ein dict Eigenschaft → Sprecher aus SPRECHER_KANON, nur
        fuer Eigenschaften, die in `gedeckt` stehen, nur an akuten Objekten;
        ein fehlender Sprecher bleibt fehlend — der Block schreibt dann keine
        Zeile (das Verhalten vor der Scheibe). Unbekannte Werte, fremde
        Schluessel und Sprecher an latenten Objekten fallen laut.
    """
    roh: object = objekt.get("sprecher")
    if roh is None:
        return {}
    if not isinstance(roh, dict):
        logger.warning(
            f"Sachlage: 'sprecher' an '{objekt.get('name')}' ist "
            f"{type(roh).__name__} statt dict — verworfen"
        )
        return {}
    # Nur akute Objekte: Das Fenster deckt die Herkunft einer alten Deckung
    # nicht, und das Modell raet dann (`[gemessen]` 29.08.2026: 3 von 7 am
    # latenten Objekt falsch, 2 davon vertauscht). Wie die Smalltalk-Schranke.
    if not objekt.get("akut") and roh:
        logger.info(
            f"Sachlage: latentes Objekt '{objekt.get('name')}' trug Sprecher — "
            f"geleert (nur akute Objekte tragen einen)"
        )
        return {}
    gedeckt_roh: object = objekt.get("gedeckt")
    gedeckt: dict[str, str] = (
        {_holder_key(e): str(e) for e in gedeckt_roh} if isinstance(gedeckt_roh, dict) else {}
    )
    sprecher: dict[str, str] = {}
    for eigenschaft, wert in roh.items():
        wert_norm: str = str(wert).strip().lower()
        schluessel: str = _holder_key(eigenschaft)
        if wert_norm not in SPRECHER_KANON:
            logger.warning(
                f"Sachlage: Sprecher {wert!r} an '{eigenschaft}' ({objekt.get('name')}) "
                f"steht nicht im Kanon {SPRECHER_KANON} — verworfen"
            )
            continue
        if schluessel not in gedeckt:
            logger.info(
                f"Sachlage: Sprecher an '{eigenschaft}' ({objekt.get('name')}) — "
                f"die Eigenschaft steht nicht in gedeckt, verworfen"
            )
            continue
        sprecher[gedeckt[schluessel]] = wert_norm
    return sprecher


def carry_speakers(artifact: dict, previous: dict | None) -> dict:
    """Scheibe 9: fehlende Sprecher aus der vorigen Blase erben.

    Dieselbe Lehre wie `carry_holders` — der Fortfuehrungsfall zaehlt:
    Ein Modell, das eine Blase ohne das Feld fortschreibt, laesst das Feld
    weg. Eine Eigenschaft, die in der vorigen Blase gedeckt war und dort
    einen Sprecher hatte, behaelt ihn; nur was auch dort keinen hatte,
    bleibt ohne.

    Vorbedingung: `artifact` validiert; `previous` ein Artefakt oder None.
    Nachbedingung: `sprecher` jedes akuten Objekts umfasst die geerbten
        Eintraege; vorhandene bleiben unberuehrt; ein latentes Objekt erbt
        nichts — sonst ueberlebt ein einmal geratener Wert jede Folgeblase.
    """
    if not previous:
        return artifact
    vorige: dict[str, dict] = {
        _holder_key(o.get("name", "")): {
            _holder_key(k): v for k, v in (o.get("sprecher") or {}).items()
        }
        for o in previous.get("objekte") or [] if isinstance(o, dict)
    }
    for objekt in artifact.get("objekte") or []:
        if not objekt.get("akut"):
            continue
        geerbt: dict = vorige.get(_holder_key(objekt.get("name", "")), {})
        if not geerbt:
            continue
        sprecher: dict = objekt.setdefault("sprecher", {})
        gedeckt: object = objekt.get("gedeckt")
        for eigenschaft in (gedeckt if isinstance(gedeckt, dict) else {}):
            schluessel: str = _holder_key(eigenschaft)
            if str(eigenschaft) not in sprecher and schluessel in geerbt:
                sprecher[str(eigenschaft)] = geerbt[schluessel]
    return artifact


def _holder_key(text: object) -> str:
    """Der Vergleichsschluessel einer Eigenschaft: Kleinschreibung, ein Leerzeichen."""
    return " ".join(str(text).lower().split())


def _render_history(session_turns: list[dict]) -> str:
    """Die juengsten Turns als Verlaufszeilen fuer den Prompt.

    Vorbedingung: Turns mit `rolle` und `inhalt`, wie `session_turns_retrieve`
        sie liefert.
    Nachbedingung: Eine Zeile je Beitrag (`Nutzer:` / `Nova:`), ohne
        Regieanweisungen, Zeilenumbrueche zu Leerzeichen gefaltet, hoechstens
        `_BEITRAG_MAX_ZEICHEN` lang — Novas Antworten kommen damit ganz an,
        und die Deckungsregel des Prompts hat etwas zu lesen.
    Fehlerfaelle: Ein Beitrag, der nach dem Entfernen der Regieanweisung leer
        ist, erzeugt keine Zeile; ohne Zeilen steht der Platzhalter.
    """
    zeilen: list[str] = []
    for turn in session_turns[-_TURN_FENSTER:]:
        sprecher: str = "Nutzer" if turn.get("rolle") == "user" else "Nova"
        inhalt: str = _REGIEANWEISUNG.sub(" ", turn.get("inhalt") or "")
        inhalt = " ".join(inhalt.split())
        if inhalt:
            zeilen.append(f"{sprecher}: {inhalt[:_BEITRAG_MAX_ZEICHEN]}")
    return "\n".join(zeilen) if zeilen else "(noch keine Beitraege)"


def _age_label(erstellt_am: str) -> str:
    """»vor 12 min« / »vor 2 h« / »vor 3 Tagen« aus einem ISO-Zeitstempel; leer, wenn unlesbar."""
    try:
        damals = datetime.fromisoformat(str(erstellt_am))
    except (TypeError, ValueError):
        return ""
    if damals.tzinfo is None:
        damals = damals.replace(tzinfo=timezone.utc)
    sekunden: float = max(0.0, (datetime.now(timezone.utc) - damals).total_seconds())
    if sekunden < 3600:
        return f"vor {int(sekunden // 60)} min"
    if sekunden < 86400:
        return f"vor {sekunden / 3600:.0f} h"
    return f"vor {int(sekunden // 86400)} Tagen"


def _derive(
    vorige:        dict | None,
    session_turns: list[dict],
    aeusserung:    str,
    wiederaufnahme: dict | None = None,
    bestand:        list[MemoryHit] | None = None,
) -> dict | None:
    """Der LLM-Call — erzwungenes JSON, validiert gegen die Pflichtstruktur.

    Vorbedingung: `aeusserung` ist nicht leer; `wiederaufnahme` ist eine
        Verlaufszeile (`history_nearest`) oder None; `bestand` das Angebot
        des Aufloesers (`memory_offer`) oder None.
    Nachbedingung: Das validierte Artefakt oder None bei Ausfall. Mit
        Angebot und offenen Eigenschaften ist der Aufloeser-Call gelaufen,
        seine Ansprueche sind gegen das Angebot gehalten und die Quellen der
        vorigen Blase fortgeschrieben.
    Fehlerfaelle: Ausnahmen des Workers werden gefangen und laut gemeldet —
        der Turn laeuft weiter, der Aufrufer markiert den Rueckkehrpfad.
    """
    # Was der Prompt von der vorigen Blase sieht: die Sache, nicht die
    # Buchfuehrung des letzten Laufs — auch nicht die Quellen der Objekte
    # (die erbt das neue Artefakt in `carry_sources`).
    vorige_rein: dict | None = (
        {k: (
            [{ok: ov for ok, ov in o.items() if ok != "quellen"} for o in v]
            if k == "objekte" else v
        ) for k, v in vorige.items()
         if k not in ("wiederaufnahme", "herkunft", "alter_sekunden")}
        if vorige else None
    )
    angebot: list[MemoryHit] = list(bestand or [])
    vorige_sektion: str = (
        _VORIGE_SEKTION.format(vorige=json.dumps(vorige_rein, ensure_ascii=False))
        if vorige_rein else "Es gibt noch keine Sachlage — dies ist der Anfang."
    )
    wiederaufnahme_sektion: str = (
        _WIEDERAUFNAHME_SEKTION.format(
            thema   = str(wiederaufnahme.get("thema", "")),
            alter   = _age_label(str(wiederaufnahme.get("erstellt_am", ""))) or "frueher",
            objekte = json.dumps(wiederaufnahme.get("objekte", []), ensure_ascii=False),
        )
        if wiederaufnahme else ""
    )
    prompt: str = SACHLAGE_PROMPT.format(
        vorige_sektion         = vorige_sektion,
        wiederaufnahme_sektion = wiederaufnahme_sektion,
        verlauf                = _render_history(session_turns),
        aeusserung             = aeusserung.strip()[:1200],
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
    artefakt: dict | None = _validate_artifact(response.parsed)
    if artefakt is None:
        return None
    # Scheibe 6: das Urteil, ob das Angebot eine offene Eigenschaft deckt,
    # faellt ein eigener, kleiner Call — nur offene Eigenschaften gegen das
    # Angebot. `[gemessen]` 28.08.2026: im Sachlage-Call selbst traf es 1/5.
    offen: list[tuple[str, list[str]]] = open_properties(artefakt)
    claims: dict = (
        resolve_open_properties(offen, angebot) if angebot and offen else {}
    )
    artefakt = carry_sources(apply_memory_coverage(artefakt, angebot, claims, vorige), vorige)
    artefakt = carry_holders(artefakt, vorige)
    artefakt = carry_criticality(artefakt, vorige)
    artefakt = carry_speakers(artefakt, vorige)
    # Scheibe 7: Behauptet der Nutzer ueber die akute Sache etwas, das die
    # Welt nicht hergibt? Ein eigener Call, nur bei akutem Objekt — die Lage
    # sagt dass und warum, die Form bleibt Sache von Haltung und Vehikel.
    befunde: dict = (
        assess_plausibility(aeusserung, artefakt) if has_acute_object(artefakt) else {}
    )
    artefakt = apply_plausibility(artefakt, befunde)
    # Scheibe 8: die erste offene Eigenschaft, die Nachschlagen verlangt und
    # die das Gedaechtnis nicht deckt — eine Websuche je Turn.
    return research_open_property(artefakt)


def _resume_lookup(state: dict, vorige: dict | None) -> dict | None:
    """Scheibe 5: die fruehere Blase des Paares, zu der der Turn vermutlich zurueckkehrt.

    Vorbedingung: `state` traegt das Paar; das Prompt-Embedding des Enrichers
        liegt in `state["prompt_embedding"]` — fehlt es, wird der Reiz hier
        eingebettet.
    Nachbedingung: Die naechste Verlaufszeile eines **anderen** Themas ueber
        `SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS`, samt `kosinus` — oder None.
    Fehlerfaelle: Ohne Vektor (Embed-Worker aus) keine Suche, mit Warnung —
        der Turn laeuft ohne Wiederaufnahme weiter; das Repository meldet
        DB-Fehler selbst und liefert None.
    """
    vektor: list[float] | None = state.get("prompt_embedding") or None
    if not vektor:
        try:
            vektor = model_service.embed.submit_sync(
                EmbedRequest(text=reiz_text(state)[:1200])
            ).embedding
        except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
            logger.warning(
                f"Wiederaufnahme: kein Vektor fuer den Reiz ({type(fehler).__name__}: "
                f"{fehler}) — Turn laeuft ohne Suche nach einer frueheren Blase"
            )
            return None
    return history_nearest(
        POSTGRES_URL,
        state.get("user_id", ""), state.get("character_id", ""),
        embedding    = vektor,
        min_kosinus  = SACHLAGE_WIEDERAUFNAHME_MIN_KOSINUS,
        ausser_thema = str(vorige.get("thema") or "") or None if vorige else None,
    )


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
        f"Person As Gedanke entstand frueher. {anlass}",
        f"Damals ging es um: {damals.get('gegenstand', '')} ({damals.get('thema', '')})",
        f"Was Person B damals wollte: {damals.get('nutzerziel', '')}",
    ]
    if aktuell.get("gegenstand"):
        zeilen.append(f"Jetzt geht es um: {aktuell.get('gegenstand', '')}")
    else:
        zeilen.append("Jetzt: Das Gespraech hat gerade keinen Gegenstand — eine Pause.")
    zeilen.append(
        "Baue den Uebergang hoerbar: Person A sagt, woran sie anknuepft, bevor "
        "sie den Gedanken einbringt — der Anschluss steht im Inhalt."
    )
    return "\n".join(zeilen)


def _reader_names(leser: str, aufrufer: str) -> dict[str, str]:
    """Die Personennamen fuer den Leser eines Blocks — oder ein lauter Fehler.

    Vorbedingung: `leser` ist LESER_VERFASSER oder LESER_GV.
    Nachbedingung: das Namens-Dict; ein unbekannter Leser ist ein ValueError,
        kein Rueckfall — ein Block im falschen Namenssystem saehe richtig aus.
    """
    if leser not in _NAMEN:
        meldung: str = f"{aufrufer}: unbekannter Leser {leser!r}"
        raise ValueError(meldung)
    return _NAMEN[leser]


def critical_gap_lines(objekt: dict, namen: dict[str, str]) -> list[str]:
    """Scheibe 10: die Zeile des Blocks, die die tragende Luecke benennt.

    Eine Luecke kommt hier nur durch, wenn beides gilt: Sie ist `kritisch`
    (ohne sie muesste die Antwort raten) **und** ihr Traeger ist der Nutzer.
    Was die Welt weiss, ist Antwortstoff und keine Frage — eine kritische
    Weltwissens-Luecke macht daraus keine Rueckfrage, sondern hoechstens eine
    Suche (Scheibe 8).

    Rein. Vorbedingung: `objekt` ist ein Objekt des Artefakts, `namen` die
        Leser-Namen des Blocks.
    Nachbedingung: Hoechstens eine Zeile; leer, wenn keine tragende Luecke
        beim Nutzer liegt.
    """
    kritische: list[str] = [
        str(e) for e in (objekt.get("offen") or [])
        if (objekt.get("kritikalitaet") or {}).get(str(e), UNKRITISCH) == KRITISCH
        and (objekt.get("traeger") or {}).get(str(e), TRAEGER_NUTZER) == TRAEGER_NUTZER
    ][:2]
    if not kritische:
        return []
    return [
        f"Ohne {', '.join(kritische)} muesste {namen['nova']} bei "
        f"{objekt.get('name')} raten — das ist zuerst zu klaeren"
    ]


def sachlage_block(sachlage: dict, leser: str = LESER_GV) -> str:
    """Der [SACHLAGE]-Block fuer Verfasser und Gespraechsvektor.

    Vorbedingung: `sachlage` traegt die Pflichtfelder; `leser` ist
        LESER_VERFASSER oder LESER_GV — ein anderer Wert ist ein Fehler, kein
        Rueckfall (ein Block im falschen Namenssystem saehe richtig aus).
    Nachbedingung: Ein Block, der mit `[SACHLAGE]` beginnt; offene
        Eigenschaften stehen nur bei akuten Objekten; die Personen heissen
        beim Verfasser Person A und Person B, beim Gespraechsvektor Nova und
        der Nutzer — nie »du«.
    """
    n: dict[str, str] = _reader_names(leser, "sachlage_block")
    zeilen: list[str] = [
        "[SACHLAGE]",
        f"Worum es geht: {sachlage.get('gegenstand', '')}",
        f"Was {n['nutzer']} vermutlich will: {sachlage.get('nutzerziel', '')}",
        f"Wie er es angeht: {sachlage.get('ausdrucksweise', '')}",
    ]
    for objekt in sachlage.get("objekte", []):
        if not objekt.get("akut"):
            continue
        if objekt.get("offen"):
            offen: str = ", ".join(str(o) for o in objekt["offen"][:5])
            zeilen.append(
                f"Im Raum steht: {objekt.get('name')} — dazu noch offen: {offen}"
            )
        # Scheibe 6: was das Gedaechtnis deckt, ist Wissen fuer den Verfasser,
        # nicht Fragestoff — mit der Herkunft, damit Nova sagen kann, woher.
        gedeckt: dict = objekt.get("gedeckt") or {}
        quellen: dict = objekt.get("quellen") or {}
        for eigenschaft, quelle in list(quellen.items())[:3]:
            label: str = SOURCE_LABELS.get(
                str(quelle.get("quelle", "")), "aus dem Gedaechtnis",
            )
            zeilen.append(
                f"Dazu weiss {n['nova']} schon ({label}): {eigenschaft} — "
                f"{str(gedeckt.get(eigenschaft, ''))[:200]}"
            )
        # Scheibe 9: wer eine gedeckte Eigenschaft gesagt hat.
        zeilen.extend(speaker_lines(objekt, leser))
        # Scheibe 7: ein Zweifel am Gesagten — Stufe, Behauptung, Grund. Ob und
        # wie Nova ihn ausspricht, entscheiden Haltung und Vehikel.
        for befund in (objekt.get("plausibilitaet") or [])[:3]:
            zeilen.append(
                f"Zweifel ({befund.get('stufe', '')}): {befund.get('behauptung', '')} — "
                f"{befund.get('grund', '')}"
            )
        # Scheibe 10: Die Luecke, ohne die jede Antwort raten muesste. Sie steht
        # VOR dem Antwortstoff, weil sie die Antwort traegt und nicht schmueckt.
        zeilen.extend(critical_gap_lines(objekt, n))
        # Scheibe 8: Was die Welt weiss, beantwortet Nova — kein Fragestoff.
        traeger: dict = objekt.get("traeger") or {}
        antworten: list[str] = [
            str(e) for e in (objekt.get("offen") or [])
            if traeger.get(str(e), TRAEGER_NUTZER) in ANTWORT_TRAEGER
        ][:3]
        if antworten:
            zeilen.append(
                f"{n['Nutzer']} will zu {objekt.get('name')} wissen: "
                f"{', '.join(antworten)} — "
                f"{n['nova']} beantwortet es aus ihrem Wissen, statt danach zu fragen"
            )
        for eigenschaft, treffer in list((objekt.get("recherche") or {}).items())[:1]:
            for fund in treffer[:2]:
                zeilen.append(
                    f"Nachgeschlagen zu {objekt.get('name')} — {eigenschaft}: "
                    f"{str(fund.get('content', ''))[:240]} ({fund.get('url', '')})"
                )
    fruehere: dict | None = sachlage.get("wiederaufnahme")
    if fruehere:
        alter: str = _age_label(str(fruehere.get("erstellt_am", "")))
        zeilen.append(
            f"{n['Nutzer']} kommt auf {fruehere.get('thema', '')} zurueck"
            f"{f' (zuletzt {alter})' if alter else ''}"
        )
    return "\n".join(zeilen)


def speaker_lines(objekt: dict, leser: str = LESER_GV) -> list[str]:
    """Scheibe 9: die Zeilen des Blocks, die sagen, wer was gesagt hat.

    Der Gedanke des Nutzers bleibt seiner, Novas bleibt ihrer — der Verfasser
    hoert beides und nimmt den fremden als fremden auf. Eine Deckung aus dem
    Gedaechtnis traegt ihre Quelle statt eines Sprechers (Scheibe 6); ohne
    Sprecher (alte Artefakte) keine Zeile — das Verhalten vor der Scheibe.

    Vorbedingung: `objekt` ist ein akutes Objekt des Artefakts; `leser` wie
        bei `sachlage_block`.
    Nachbedingung: Hoechstens drei Zeilen, in der Reihenfolge von `gedeckt`,
        nur fuer Eigenschaften mit Sprecher und ohne Quelle, in den Namen
        des Lesers.
    """
    n: dict[str, str] = _reader_names(leser, "speaker_lines")
    gedeckt: dict = objekt.get("gedeckt") or {}
    quellen: dict = objekt.get("quellen") or {}
    sprecher: dict = objekt.get("sprecher") or {}
    genannt: list[str] = [
        str(e) for e in gedeckt if str(e) in sprecher and str(e) not in quellen
    ][:3]
    zeilen: list[str] = []
    for eigenschaft in genannt:
        wer: str = (
            f"{n['Nutzer']} hat" if sprecher[eigenschaft] == SPRECHER_NUTZER
            else f"{n['nova']} hat schon"
        )
        zeilen.append(
            f"{wer} zu {objekt.get('name')} gesagt: {eigenschaft} — "
            f"{str(gedeckt.get(eigenschaft, ''))[:200]}"
        )
    return zeilen


# Der Zielsatz des kurzfristigen Ziels traegt das Vorhaben woertlich hinter
# diesem Praefix (`memory/kurzziel.py::build_short_goal_sentence`).
_KURZZIEL_PRAEFIX: str = "Ich möchte dem Nutzer bei seinem Vorhaben helfen: "


def question_target_origin(
    sachlage: dict, aktivierte_ziele: list[dict] | None = None,
) -> tuple[str, str] | None:
    """Scheibe 3: der Gegenstand der Rueckfrage — und woher er stammt.

    `[gemessen]` 29.08.2026, 20 Betriebsturns: 17 von 20 Gegenstaenden kamen
    aus dem Kurzziel, und in den ersten zwei Turns nach einem Themenwechsel
    war das das alte — die Gravitation zieht Nova dorthin, und das ist
    gewollt. Falsch war nur die Form: Die Rueckfrage-Zeile gab Novas Zug als
    Frage an den Nutzer zu *seiner* Sache aus. Deshalb traegt der Gegenstand
    seine Herkunft: `blase` (eine offene Eigenschaft des Nutzers oder ein
    Kurzziel zu einem akuten Objekt der Blase) oder `eigener_zug` (ein
    Kurzziel, dessen Sache nicht in der Blase steht).

    Rein. Vorbedingung: wie `question_target`.
    Nachbedingung: (Gegenstand, Herkunft) mit Herkunft aus
        {GEGENSTAND_AUS_BLASE, GEGENSTAND_EIGENER_ZUG}, oder None.
    """
    akute: set[str] = set()
    for objekt in sachlage.get("objekte") or []:
        if not objekt.get("akut"):
            continue
        akute.add(normalize_object_name(str(objekt.get("name", ""))))
        # Scheibe 8: Nur eine Eigenschaft, die der Nutzer kennt, ist eine
        # Frage an ihn. Was die Welt weiss, ist Antwortstoff (`answer_targets`).
        traeger: dict = objekt.get("traeger") or {}
        gewichte: dict = objekt.get("kritikalitaet") or {}
        # Scheibe 10: Zwei Durchgaenge, und der erste sucht die kritische
        # Luecke. `offen` ist nach Wichtigkeit geordnet, aber Wichtigkeit ist
        # nicht dasselbe wie *ohne sie muss die Antwort raten* — genau diese
        # Unterscheidung fehlte, solange die erste Nutzer-Eigenschaft gewann.
        for nur_kritische in (True, False):
            for eigenschaft in objekt.get("offen") or []:
                if traeger.get(str(eigenschaft), TRAEGER_NUTZER) != TRAEGER_NUTZER:
                    continue
                ist_kritisch: bool = (
                    gewichte.get(str(eigenschaft), UNKRITISCH) == KRITISCH
                )
                if nur_kritische and not ist_kritisch:
                    continue
                return (
                    f"{objekt.get('name', '')} — was dazu noch offen ist: "
                    f"{eigenschaft}",
                    GEGENSTAND_AUS_BLASE,
                )
    for ziel in aktivierte_ziele or []:
        if ziel.get("ziel_typ") == "kurzfristig":
            satz: str = str(ziel.get("zielsatz", ""))
            vorhaben: str = satz.split(_KURZZIEL_PRAEFIX, 1)[-1].split(" — ", 1)[0].strip()
            if vorhaben:
                herkunft: str = (
                    GEGENSTAND_AUS_BLASE if normalize_object_name(vorhaben) in akute
                    else GEGENSTAND_EIGENER_ZUG
                )
                return f"wie es mit {vorhaben} weitergeht", herkunft
    return None


def question_target(sachlage: dict, aktivierte_ziele: list[dict] | None = None) -> str | None:
    """Scheibe 3: der Gegenstand, den die Rueckfrage des Verfassers bekommt.

    Die Reihenfolge ist die des Konzepts (`novaberg-thinking-lage_k.md` §4,
    Scheibe 3): die wichtigste offene Eigenschaft eines akuten Objekts —
    `offen` ist im Prompt nach Wichtigkeit geordnet, also die erste —, sonst
    der naechste Schritt zum beruehrten Ziel, und das ist das kurzfristige
    (es entstand aus derselben Blase). Novas eigene mittel- und
    langfristigen Ziele sind kein Gegenstand fuer eine Frage an den Nutzer.

    Rein: kein Modell, kein Zustand. **Die Haltung bleibt der Regler** —
    ob aus dem Gegenstand eine Frage wird, entscheidet die Rueckfrage-Zeile
    (`ei/haltungssprache.py::_rueckfragenzeile`), nicht diese Funktion.

    Vorbedingung: `sachlage` ist ein Artefakt (auch leer); `aktivierte_ziele`
        die Dicts aus dem Zustand oder None.
    Nachbedingung: Ein Satzstueck (»Geburtstag — was dazu noch offen ist:
        wer« / »wie es mit Umlaufzeitberechnung weitergeht«) oder None.
    Fehlerfaelle: keine — ein fehlender Gegenstand ist ein regulaerer Fall.
    Seit dem 29.08.2026 abends ein Blick auf `question_target_origin`, das
    zusaetzlich die Herkunft kennt.
    """
    quelle: tuple[str, str] | None = question_target_origin(sachlage, aktivierte_ziele)
    return quelle[0] if quelle else None


def answer_targets(sachlage: dict) -> list[tuple[str, str, str]]:
    """Scheibe 8: die offenen Eigenschaften, die Nova beantworten soll.

    Rein. Eine offene Eigenschaft mit Traeger `welt` oder `nachschlagen`
    ist Antwortstoff fuer den Verfasser, keine Frage an den Nutzer — und sie
    steht nur in `offen`, solange das Gedaechtnis sie nicht deckt (Scheibe 6
    nimmt gedeckte heraus).

    Vorbedingung: `sachlage` ist ein Artefakt (auch leer).
    Nachbedingung: Tripel (Objektname, Eigenschaft, Traeger) in der Reihenfolge
        von `offen`, nur akute Objekte; leer erlaubt.
    """
    ziele: list[tuple[str, str, str]] = []
    for objekt in sachlage.get("objekte") or []:
        if not objekt.get("akut"):
            continue
        traeger: dict = objekt.get("traeger") or {}
        for eigenschaft in objekt.get("offen") or []:
            wer: str = traeger.get(str(eigenschaft), TRAEGER_NUTZER)
            if wer in ANTWORT_TRAEGER:
                ziele.append((str(objekt.get("name", "")), str(eigenschaft), wer))
    return ziele


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
        # Scheibe 5: Kehrt der Turn zu einer frueheren Blase zurueck, bekommt
        # der Call sie mit — sonst beginnt die Sache bei null.
        fruehere: dict | None = _resume_lookup(state, vorige)
        if fruehere:
            logger.info(
                f"Wiederaufnahme: fruehere Blase '{str(fruehere.get('thema', ''))[:40]}' "
                f"(turn={fruehere.get('turn_id')}, "
                f"kosinus={float(fruehere.get('kosinus', 0.0)):.2f})"
            )
        # Scheibe 6: das Angebot aus dem Gedaechtnis-Pool des Turns — was
        # davon eine offene Eigenschaft deckt, entscheidet der Call, gehalten
        # gegen das Angebot.
        erhoben: dict | None = _derive(
            vorige, state.get("session_turns") or [], reiz_text(state),
            wiederaufnahme=fruehere,
            bestand=memory_offer(state, vorige),
        )
        if erhoben is not None:
            erhoben["herkunft"] = (
                HERKUNFT_VERFALLEN_NEU if verfallen
                else HERKUNFT_FORTGESCHRIEBEN if vorige
                else HERKUNFT_FRISCH
            )
            erhoben["wiederaufnahme"] = (
                {k: fruehere.get(k) for k in ("turn_id", "thema", "kosinus", "erstellt_am")}
                if fruehere else None
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
