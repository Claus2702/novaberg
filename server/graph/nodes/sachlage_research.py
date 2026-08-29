"""Die Recherche zu einer offenen Eigenschaft — Scheibe 8 des Lage-Konzepts.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 8. Eine offene
Eigenschaft mit dem Wissenstraeger `nachschlagen` ist Weltwissen, das
speziell, aktuell oder zahlengenau ist — Nova muss es nicht im Kopf haben,
sie darf nachschlagen. Fuer die **erste** solche Eigenschaft eines akuten
Objekts, die das Gedaechtnis nicht deckt (Scheibe 6 nimmt gedeckte aus
`offen` heraus), laeuft **eine** Websuche je Turn; die Treffer stehen am
Objekt in `recherche`, und der `[SACHLAGE]`-Block gibt sie dem Verfasser.

**Dieselbe Suche wie im Thinker** (`tools/web/search.py`), kein Nachlesen
der Trefferseite — das bleibt dem Thinker. Ein Ausfall der Suche ist laut
und kostet den Turn nicht.
"""

import logging

from config import SACHLAGE_RECHERCHE_MAX_TREFFER
from tools.web.search import web_search_manager

logger = logging.getLogger("ki_server.sachlage.research")

# Der Traeger, der eine Suche verlangt — derselbe Wert wie in `sachlage.py`
# (dort TRAEGER_NACHSCHLAGEN; hier ohne Import, weil `sachlage.py` dieses
# Modul importiert und ein Kreis entstuende).
HOLDER_LOOKUP: str = "nachschlagen"
# Wie viel eines Treffers das Artefakt traegt.
_CONTENT_MAX_CHARS: int = 400
# Ein Treffer muss die Sache nennen: mindestens ein Wort des Objektnamens ab
# dieser Laenge in Titel oder Text. `[gemessen]` 29.08.2026, 07:27 UTC: Die
# Suche zu »Neutronenstern-Rotation Rotationsfrequenz des schnellsten
# bekannten Pulsars« lieferte drei BeamNG-Mod-Seiten (BMW 318) — ohne Filter
# haette der Verfasser sie als Nachschlagewerk bekommen.
_MIN_TERM_CHARS: int = 5


def lookup_target(artifact: dict) -> tuple[dict, str] | None:
    """Das erste akute Objekt mit einer offenen `nachschlagen`-Eigenschaft.

    Vorbedingung: `artifact` ist validiert (`traeger` normalisiert).
    Nachbedingung: (Objekt, Eigenschaft) oder None.
    """
    for objekt in artifact.get("objekte") or []:
        if not isinstance(objekt, dict) or not objekt.get("akut"):
            continue
        traeger: dict = objekt.get("traeger") or {}
        for eigenschaft in objekt.get("offen") or []:
            if traeger.get(str(eigenschaft)) == HOLDER_LOOKUP:
                return objekt, str(eigenschaft)
    return None


def _terms(text: str) -> set[str]:
    """Die Woerter eines Namens ab `_MIN_TERM_CHARS`, kleingeschrieben, ohne Bindestriche."""
    return {
        w for w in "".join(c if c.isalnum() else " " for c in text.lower()).split()
        if len(w) >= _MIN_TERM_CHARS
    }


def relevant_hits(objekt_name: str, treffer: list[dict]) -> list[dict]:
    """Die Treffer, die die Sache nennen — die anderen sind Rauschen der Suche.

    Vorbedingung: `treffer` roh aus der Suche (title, url, content).
    Nachbedingung: Nur Treffer, in deren Titel oder Text ein Wort des
        Objektnamens (ab `_MIN_TERM_CHARS`) vorkommt; hat der Name kein
        solches Wort, bleiben alle. Reihenfolge erhalten.
    """
    woerter: set[str] = _terms(objekt_name)
    if not woerter:
        return list(treffer)
    behalten: list[dict] = []
    for t in treffer:
        if not isinstance(t, dict):
            continue
        text: str = f"{t.get('title', '')} {t.get('content', '')}".lower()
        if any(w in text for w in woerter):
            behalten.append(t)
    return behalten


def research_open_property(artifact: dict) -> dict:
    """Eine Websuche fuer die erste offene Eigenschaft, die Nachschlagen verlangt.

    Vorbedingung: `artifact` ist validiert.
    Nachbedingung: Jedes akute Objekt traegt `recherche` (auch leer); hoechstens
        eines traegt Treffer, unter der gesuchten Eigenschaft, hoechstens
        `SACHLAGE_RECHERCHE_MAX_TREFFER`, jeder mit title, url, content. Die
        Suche steht im Log — mit Anfrage und Trefferzahl.
    Fehlerfaelle: Ein Ausfall der Suche ist eine Warnung, `recherche` bleibt
        leer, der Turn laeuft weiter.
    """
    # ── Eingabe-Validierung ─────────────────────
    for objekt in artifact.get("objekte") or []:
        if isinstance(objekt, dict) and objekt.get("akut"):
            objekt.setdefault("recherche", {})
    ziel: tuple[dict, str] | None = lookup_target(artifact)
    if ziel is None:
        return artifact
    objekt, eigenschaft = ziel

    # ── Verarbeitung ────────────────────────────
    anfrage: str = f"{objekt.get('name', '')} {eigenschaft}".strip()
    try:
        treffer: list[dict] = web_search_manager.suchen(
            anfrage, max_results=SACHLAGE_RECHERCHE_MAX_TREFFER,
        )
    except Exception as fehler:  # noqa: BLE001 — der Turn geht vor
        logger.warning(
            f"Sachlage-Recherche: Suche zu '{anfrage[:60]}' ausgefallen "
            f"({type(fehler).__name__}: {fehler}) — ohne Treffer"
        )
        return artifact
    passend: list[dict] = relevant_hits(str(objekt.get("name", "")), treffer)
    gekuerzt: list[dict] = [
        {
            "title":   str(t.get("title", ""))[:120],
            "url":     str(t.get("url", "")),
            "content": str(t.get("content", ""))[:_CONTENT_MAX_CHARS],
        }
        for t in passend[:SACHLAGE_RECHERCHE_MAX_TREFFER]
        if t.get("content") or t.get("title")
    ]

    # ── Ausgabe-Verifikation ────────────────────
    objekt["recherche"] = {eigenschaft: gekuerzt}
    logger.info(
        f"Sachlage-Recherche: '{anfrage[:60]}' — {len(treffer)} Treffer, "
        f"{len(gekuerzt)} nennen die Sache"
        + (f", erster: {gekuerzt[0]['url']}" if gekuerzt else " (keiner — Rauschen verworfen)")
    )
    return artifact
