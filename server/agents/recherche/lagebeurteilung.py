"""
Lagebeurteilung fuer Pixie-Agenten (Recherche + Vertiefung).

Zwei Phasen:
1. Kontext-Assembly (Python, kein LLM) — aggregiert KZG, LZG, Session, Charakter
2. LLM-Lagebeurteilung (Qwen3-32B) — verdichtet zu kompaktem Kontext-Dokument

Das Ergebnis fliesst als [LAGEBEURTEILUNG]-Block in alle Folgeschritte.
"""

import json
import logging

from config import (
    PIXIE_VERTIEFUNG_LZG_LIMIT,
    PIXIE_VERTIEFUNG_KZG_LIMIT,
)
from memory.kontext import session_kontext_extrahieren
from tools.db_manager import db_manager
from services.llm_provider import pixie_llm_call
from services.model_services import model_service, EmbedRequest
from config import redis_client

logger = logging.getLogger("ki_server.pixie.lagebeurteilung")


# ---------------------------------------------------------------------------
# Phase 1: Kontext-Assembly (deterministisch, kein LLM)
# ---------------------------------------------------------------------------

def kontext_paket_bauen(
    thema: str,
    queue_eintrag: dict,
    user_id: str,
    character_id: str,
    lzg_limit: int = PIXIE_VERTIEFUNG_LZG_LIMIT,
    kzg_limit: int = PIXIE_VERTIEFUNG_KZG_LIMIT,
) -> dict:
    """Baut den vollstaendigen Kontext deterministisch zusammen.

    Aggregiert alle Gedaechtnisschichten ohne LLM-Call.
    """
    # 1. Session-Kontext (existiert: memory/kontext.py)
    session_kontext = session_kontext_extrahieren(user_id)

    # 2. LZG-Vorwissen via Embedding-Suche
    lzg_treffer = _lzg_vorwissen_laden(thema, user_id, lzg_limit)

    # 3. KZG-Eintraege zum Thema
    kzg_eintraege = _kzg_eintraege_laden(thema, user_id, kzg_limit)

    # 4. Charakter-Hash
    charakter_hash = _charakter_laden(user_id, character_id)

    # 5. Beziehungsdynamik
    beziehungs_dynamik = "neutral"
    if isinstance(session_kontext, dict):
        beziehungs_dynamik = session_kontext.get("beziehungs_dynamik", "neutral")

    logger.info(
        f"Kontext-Paket: LZG={len(lzg_treffer)}, KZG={len(kzg_eintraege)}, "
        f"Charakter={'ja' if charakter_hash else 'nein'}"
    )

    return {
        "thema": thema,
        "queue_eintrag": queue_eintrag,
        "session_kontext": session_kontext,
        "lzg_treffer": lzg_treffer,
        "kzg_eintraege": kzg_eintraege,
        "charakter_hash": charakter_hash,
        "beziehungs_dynamik": beziehungs_dynamik,
    }


def _lzg_vorwissen_laden(thema: str, user_id: str, limit: int) -> list[dict]:
    """Laedt LZG-Eintraege via Embedding-Suche."""
    try:
        embed_response = model_service.embed.submit_sync(EmbedRequest(text=thema))
        thema_embedding: list[float] = embed_response.embedding
        logger.debug(
            "Lagebeurteilung: LZG-Vorwissen Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
            len(thema_embedding),
            embed_response.duration_seconds,
        )
        embedding_str: str = "[" + ",".join(str(x) for x in thema_embedding) + "]"

        treffer = db_manager.select(
            """
            SELECT inhalt, dimension, erstellt_am, gewicht
            FROM langzeitgedaechtnis
            WHERE user_id = %s AND aktiv = TRUE
              AND embedding IS NOT NULL
            ORDER BY 1 - (embedding <=> %s::vector) DESC
            LIMIT %s
            """,
            (user_id, embedding_str, limit),
        )
        return treffer
    except Exception as e:
        logger.warning(f"LZG-Vorwissen laden fehlgeschlagen: {e}")
        return []


def _kzg_eintraege_laden(thema: str, user_id: str, limit: int) -> list[dict]:
    """Laedt KZG-Eintraege zum Thema aus Redis."""
    try:
        kzg_keys = redis_client.keys(f"kzg:{user_id}:*")
        eintraege: list[dict] = []
        thema_lower: str = thema.lower()

        for key in kzg_keys:
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            themen_raw = redis_client.hget(key, "themen")
            if themen_raw is None:
                continue
            if isinstance(themen_raw, bytes):
                themen_raw = themen_raw.decode("utf-8")

            if thema_lower in themen_raw.lower():
                inhalt = redis_client.hget(key, "inhalt") or ""
                if isinstance(inhalt, bytes):
                    inhalt = inhalt.decode("utf-8")
                salienz = redis_client.hget(key, "salienz") or "0"
                if isinstance(salienz, bytes):
                    salienz = salienz.decode("utf-8")

                eintraege.append({
                    "themen": themen_raw,
                    "inhalt": inhalt,
                    "salienz": float(salienz),
                })

            if len(eintraege) >= limit:
                break

        return eintraege
    except Exception as e:
        logger.warning(f"KZG-Eintraege laden fehlgeschlagen: {e}")
        return []


def _charakter_laden(user_id: str, character_id: str) -> dict:
    """Laedt den Charakter-Hash aus der Datenbank (Paar-Schema)."""
    try:
        rows = db_manager.select(
            """
            SELECT kern_hash, adaptive_hash, intentions_profil,
                   emotions_profil, beziehungsprofil
            FROM charakter_hash
            WHERE user_id = %s AND character_id = %s
            """,
            (user_id, character_id),
        )
        return rows[0] if rows else {}
    except Exception as e:
        logger.warning(f"Charakter laden fehlgeschlagen: {e}")
        return {}


# ---------------------------------------------------------------------------
# Formatierung fuer LLM-Kontext
# ---------------------------------------------------------------------------

def _lzg_formatieren(treffer: list[dict], max_zeichen: int = 200) -> str:
    """Formatiert LZG-Treffer als kompakte Liste fuer den Prompt."""
    if not treffer:
        return "Kein Vorwissen im LZG."
    zeilen: list[str] = []
    for t in treffer[:5]:
        inhalt = str(t.get("inhalt", ""))[:max_zeichen]
        datum = ""
        if t.get("erstellt_am"):
            try:
                datum = t["erstellt_am"].strftime("%d.%m.%Y")
            except AttributeError:
                datum = str(t["erstellt_am"])[:10]
        zeilen.append(f"- {inhalt} (LZG, {datum})")
    return "\n".join(zeilen)


def _kzg_formatieren(eintraege: list[dict], max_zeichen: int = 150) -> str:
    """Formatiert KZG-Eintraege als kompakte Liste fuer den Prompt."""
    if not eintraege:
        return "Keine aktuellen KZG-Eintraege zum Thema."
    zeilen: list[str] = []
    for e in eintraege[:5]:
        inhalt = str(e.get("inhalt", ""))[:max_zeichen]
        zeilen.append(f"- {inhalt} (KZG, aktuell)")
    return "\n".join(zeilen)


def _charakter_formatieren(charakter: dict) -> tuple[str, str]:
    """Extrahiert Expertise und Interessen aus dem Charakter-Hash.

    Returns:
        (expertise_str, interessen_str)
    """
    if not charakter:
        return "unbekannt", "unbekannt"

    # Kern-Hash und Adaptive-Hash enthalten Freitext-Profile
    kern = charakter.get("kern_hash", "")
    adaptiv = charakter.get("adaptive_hash", "")

    expertise = kern[:200] if kern else "unbekannt"
    interessen = adaptiv[:200] if adaptiv else "unbekannt"

    return expertise, interessen


# ---------------------------------------------------------------------------
# Phase 2: LLM-Lagebeurteilung (Qwen3-32B)
# ---------------------------------------------------------------------------

LAGEBEURTEILUNG_PROMPT = """[IDENTITAET]
Du bist das Analyse-Modul von Nova, einem persoenlichen KI-Assistenten.
Deine Aufgabe: Den Wissensstand zu einem Thema zusammenfassen und Luecken identifizieren.

[THEMA]
{thema}

[SESSION_KONTEXT]
Modus: {modus}
Aktuelle Gespraechsthemen: {gespraechsthemen}
Zusammenfassung: {zusammenfassung}

[BEKANNTES_WISSEN_LZG]
{lzg_formatiert}

[BEKANNTES_WISSEN_KZG]
{kzg_formatiert}

[USER_PROFIL]
Expertise: {expertise}
Interessen: {interessen}
Beziehungsdynamik: {beziehungs_dynamik}

[SUCHMODUS]
{suchmodus_beschreibung}

[AUFGABE]
Erstelle eine Lagebeurteilung zu diesem Thema.

[FORMAT]
Antworte ausschliesslich als JSON:
{{
  "vorwissen_zusammenfassung": "Was Nova bereits ueber dieses Thema weiss (2-3 Saetze, deutsch)",
  "wissensluecken": ["Konkrete Luecke 1", "Konkrete Luecke 2"],
  "user_mehrwert": "Was waere fuer diesen User besonders wertvoll? (1 Satz)",
  "ausschluss": ["Thema X nicht suchen (bereits bekannt)", "Grundlagen Y nicht suchen (User ist Experte)"]
}}

[REGELN]
- Nur Luecken benennen, die durch Web-Suche fuellbar sind
- Ausschluss-Liste basiert auf bekanntem Wissen UND User-Expertise
- Wenn kein Vorwissen vorhanden: vorwissen_zusammenfassung = "Kein Vorwissen zu diesem Thema."
- Sprache: Deutsch"""

# Suchmodus-Beschreibungen
SUCHMODUS_RECHERCHE = (
    "RECHERCHE (breit): Verschaffe einen Ueberblick ueber verschiedene Facetten des Themas. "
    "Suche neue Perspektiven, aktuelle Entwicklungen, Querverbindungen. "
    "Niveau: angepasst an die Expertise des Users — keine Grundlagen fuer Experten, "
    "keine Fachtiefe fuer Laien."
)

SUCHMODUS_VERTIEFUNG = (
    "VERTIEFUNG (tief): Nova hat bereits Vorwissen zu diesem Thema (siehe oben). "
    "Identifiziere SPEZIFISCHE Wissensluecken auf Detail-Ebene. "
    "Wo hat Nova nur Oberflaeche? Wo fehlen Mechanismen, Zusammenhaenge, Gegenargumente? "
    "Nicht breit suchen — tief bohren."
)


def lagebeurteilung_erstellen(
    kontext_paket: dict,
    suchmodus: str = "recherche",
) -> dict:
    """Erstellt die Lagebeurteilung per LLM-Call (Qwen3-32B).

    Args:
        kontext_paket: Ergebnis von kontext_paket_bauen()
        suchmodus: "recherche" (breit) oder "vertiefung" (tief)

    Returns:
        Dict mit vorwissen_zusammenfassung, wissensluecken,
        user_mehrwert, ausschluss. Bei Fehler: Minimal-Dict.
    """
    session = kontext_paket["session_kontext"]
    expertise, interessen = _charakter_formatieren(kontext_paket["charakter_hash"])

    # Session-Kontext sicher extrahieren
    if isinstance(session, dict):
        modus = session.get("modus", "unbekannt")
        themen = session.get("themen", [])
        zusammenfassung = session.get("zusammenfassung", "Keine Zusammenfassung verfuegbar.")
    else:
        modus = "unbekannt"
        themen = []
        zusammenfassung = "Keine Zusammenfassung verfuegbar."

    if isinstance(themen, list):
        themen = ", ".join(themen)

    suchmodus_beschreibung = (
        SUCHMODUS_VERTIEFUNG if suchmodus == "vertiefung" else SUCHMODUS_RECHERCHE
    )

    prompt = LAGEBEURTEILUNG_PROMPT.format(
        thema=kontext_paket["thema"],
        modus=modus,
        gespraechsthemen=themen,
        zusammenfassung=zusammenfassung,
        lzg_formatiert=_lzg_formatieren(kontext_paket["lzg_treffer"]),
        kzg_formatiert=_kzg_formatieren(kontext_paket["kzg_eintraege"]),
        expertise=expertise,
        interessen=interessen,
        beziehungs_dynamik=kontext_paket["beziehungs_dynamik"],
        suchmodus_beschreibung=suchmodus_beschreibung,
    )

    antwort = pixie_llm_call(
        prompt=prompt,
        modus="analyse",
        temperatur=0.1,
        json_output=True,
        caller="lagebeurteilung",
    )

    # JSON parsen
    try:
        lage = json.loads(antwort)
    except json.JSONDecodeError:
        logger.error("Lagebeurteilung: JSON-Parse fehlgeschlagen, Fallback")
        lage = {
            "vorwissen_zusammenfassung": "Kein Vorwissen zu diesem Thema.",
            "wissensluecken": [kontext_paket["thema"]],
            "user_mehrwert": f"Informationen zu {kontext_paket['thema']}",
            "ausschluss": [],
        }

    # Pflichtfelder sicherstellen
    lage.setdefault("vorwissen_zusammenfassung", "Kein Vorwissen zu diesem Thema.")
    lage.setdefault("wissensluecken", [kontext_paket["thema"]])
    lage.setdefault("user_mehrwert", f"Informationen zu {kontext_paket['thema']}")
    lage.setdefault("ausschluss", [])

    logger.info(
        f"Lagebeurteilung [{suchmodus}]: "
        f"{len(lage['wissensluecken'])} Luecken, "
        f"{len(lage['ausschluss'])} Ausschluesse"
    )

    return lage
