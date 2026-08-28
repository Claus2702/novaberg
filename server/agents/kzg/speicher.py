"""Speicher — Neuer KZG-Eintrag + thematische Verstaerkung verwandter Eintraege.

Schreibt direkt in Redis. Nutzt redis_client aus config.
"""

import json
import logging
import time

import numpy as np

from agents.base import AgentState
from config import (
    KZG_SALIENZ_HIGH,
    KZG_SALIENZ_MID,
    KZG_TTL_HIGH_SEKUNDEN,
    KZG_TTL_LOW_SEKUNDEN,
    KZG_TTL_MID_SEKUNDEN,
    redis_client,
)
from memory.kzg import _kzg_key, salienz_berechnen
from memory.pipeline_log import log_db_write
from services.model_services import EmbedRequest, model_service

logger = logging.getLogger("ki_server.agents.kzg.speicher")


def embed_text_bauen(themen: str, kern: str) -> str:
    """
    Baut den Embed-Text eines KZG-Eintrags — die EINZIGE Formel für das
    embedding-Feld im KZG-Hash (Chat 107). Der Text ist aus den
    persistierten Hash-Feldern themen + inhalt vollständig
    rekonstruierbar; themen kommt in der persistierten, kommagetrennten
    Form herein (", ".join — dieselbe, die im Hash liegt).

    Valenz steht bewusst NICHT mehr im Text (Entscheidung Chat 107):
    Metadaten gehören nicht in den Vektor — bei 81 % "positiv" war es ein
    nahezu konstanter Token, der den Raum verschiebt statt zu schärfen.
    Der Vektor findet den Kandidatenraum; strukturierte Felder entscheiden
    danach exakt.

    E: kern muss nicht-leer sein; themen ist optional und entfällt bei
       leerem Wert sauber aus dem Text.
    V: "Thema: {themen}. Aussage: {kern}".
    A: mit oder ohne Themen-Segment, nie mit leerem Segment.
    """
    if not kern or not kern.strip():
        raise ValueError("embed_text_bauen(kzg): kern ist leer — kein Embed-Text baubar")
    if themen and themen.strip():
        return f"Thema: {themen}. Aussage: {kern}"
    return f"Aussage: {kern}"


def speichern(state: AgentState) -> dict:
    """Speichert neuen KZG-Eintrag und verstärkt thematisch verwandte Einträge.

    Jeder Eintrag wird als eigenständiger Eintrag mit seinem scharfen Kern
    abgelegt. Danach werden alle Einträge mit thematischem Overlap verstärkt
    (Salienz-Boost + TTL-Auffrischung + Häufigkeitszähler).

    Die Verstärkung berührt nur Metadaten, nie den Inhalt. Jeder Kern bleibt
    exakt wie er beim Verdichten erzeugt wurde.
    """
    salienz_obj:  dict = state["parameter"].get("salienz_obj", {})
    kern:         str  = state["parameter"].get("kern", "")
    user_id:      str  = state["kontext"].get("user_id", "")
    character_id: str  = state["kontext"].get("character_id", "")
    beobachter:   str  = state["kontext"].get("beobachter", "user")
    turn_id:      str  = state["kontext"].get("turn_id", "")

    # Magnete aus dem magnete_aufloesen-Node (Synapsen P3).
    entitaet_ids: list[int]  = state["parameter"].get("entitaet_ids", []) or []
    timeline_id:  int | None = state["parameter"].get("timeline_id")

    salienz: float = salienz_obj.get("salienz", 0.0)

    # Ohne Kern gibt es nichts abzulegen. Der Verdichter bricht bei leerem
    # Bewertungsobjekt ab und liefert einen leeren Kern; ohne diesen Riegel
    # wuerde `embed_text_bauen` eine ValueError werfen, die den gesamten
    # KZG-Dispatch fuer alle uebrigen Segmente mitreisst.
    if not kern.strip():
        logger.error(
            f"KZG-Speicher: Kern leer — kein Eintrag angelegt "
            f"(paar={user_id}:{character_id}, beobachter={beobachter}, "
            f"turn_id={turn_id}, themen={salienz_obj.get('themen', [])})"
        )
        return {
            "parameter": {
                **state["parameter"],
                "speicher_status":       "leer",
                "kzg_key":               "",
                "verstaerkt_verwandt":   0,
                "verstaerkte_eintraege": [],
            },
            "schritte": state["schritte"] + [
                {"node": "speichern", "ergebnis": "leer"}
            ],
        }

    # Kommagetrennt wie im Hash persistiert (_neu_anlegen) — der Embed-Text
    # muss aus den gespeicherten Feldern rekonstruierbar sein (Chat 107).
    themen:     str = ", ".join(salienz_obj.get("themen", []))
    embed_text: str = embed_text_bauen(themen, kern)

    request = EmbedRequest(text=embed_text)
    embed_response = model_service.embed.submit_sync(request)
    embedding: list[float] = embed_response.embedding
    logger.debug(
        "KZG-Speicher: Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
        len(embedding),
        embed_response.duration_seconds,
    )

    ergebnis: dict = _neu_anlegen(
        redis_client, user_id, character_id, beobachter,
        salienz_obj, kern, embedding, salienz,
        entitaet_ids = entitaet_ids,
        timeline_id  = timeline_id,
        turn_id      = turn_id,
    )

    neue_themen: set[str] = set(
        t.strip().lower() for t in salienz_obj.get("themen", []) if t.strip()
    )
    verstaerkte_eintraege: list[dict] = []

    if neue_themen:
        verstaerkte_eintraege = _thematisch_verstaerken(
            user_id, character_id, ergebnis.get("key", ""), neue_themen,
        )

    return {
        "parameter": {
            **state["parameter"],
            "embedding":           embedding,
            "speicher_status":     ergebnis["status"],
            "kzg_key":             ergebnis.get("key", ""),
            "kzg_themen_str":      ergebnis.get("themen_str", ""),
            "kzg_dimension":       ergebnis.get("dimension", ""),
            "neue_salienz":        ergebnis.get("salienz", 0.0),
            "neue_haeufigkeit":    1,
            "verstaerkt_verwandt": len(verstaerkte_eintraege),
            "verstaerkte_eintraege": verstaerkte_eintraege,
        },
        "schritte": state["schritte"] + [
            {"node": "speichern", "ergebnis": ergebnis["status"],
             "verstaerkt_verwandt": len(verstaerkte_eintraege)}
        ],
    }


def _thematisch_verstaerken(
    user_id:       str,
    character_id:  str,
    eigener_key:   str,
    neue_themen:   set[str],
) -> list[dict]:
    """Verstärkt thematisch verwandte KZG-Einträge in der Paar-Partition.

    Verstärkungsschema (KZG):
    - haeufigkeit += 1
    - salienz = salienz_berechnen(salienz_eingang, neue_haeufigkeit) — neu
      gerechnet aus den beiden gespeicherten Eingaben, nicht fortgeschrieben
    - TTL auf den höheren Wert aus (verbleibend, neu berechnet aus neuer Salienz)

    Die eingehende Salienz des auslösenden Eintrags geht NICHT mehr in den
    Zuwachs ein: Was einen Eintrag stärker macht, ist die Tatsache der
    Wiederholung, nicht die Bewertung dessen, was sie ausgelöst hat.

    Nicht angerührt: inhalt, embedding, emotion, modus, arousal.
    Der scharfe Kern jedes Eintrags bleibt exakt erhalten.

    Returns:
        Liste der verstärkten Einträge als Dicts mit key, salienz, themen.
        Jeder Eintrag, dessen neu gerechnete Salienz KZG_SALIENZ_HIGH erreicht,
        wird in queues_befuellen zur Promotion eingereiht.
    """
    prefix: str = f"kzg:{user_id}:{character_id}:"
    keys: list = redis_client.keys(f"{prefix}*")
    verstaerkte: list[dict] = []

    for key in keys:
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        if key == eigener_key:
            continue

        try:
            existing_themen_raw: str | None = redis_client.hget(key, "themen")
            if not existing_themen_raw:
                continue

            existing_themen: set[str] = set(
                t.strip().lower() for t in existing_themen_raw.split(",") if t.strip()
            )

            overlap: set[str] = neue_themen & existing_themen
            if not overlap:
                continue

            # Der Eingangswert ist unveraenderlich; verstaerkt wird der Zaehler.
            # Die Salienz entsteht daraus neu — sie wird nicht fortgeschrieben
            # (novaberg-convention-abgeleitete-werte.md).
            eingang_roh: str | None = redis_client.hget(key, "salienz_eingang")
            if eingang_roh is None:
                logger.error(
                    f"KZG-Verstaerkung: {key} traegt kein salienz_eingang — Eintrag "
                    f"stammt aus der Zeit vor dem Skalenumbau und ist nicht "
                    f"nachrechenbar; uebersprungen"
                )
                continue

            alte_salienz:     float = float(redis_client.hget(key, "salienz") or "0.0")
            alte_haeufigkeit: int   = int(float(redis_client.hget(key, "haeufigkeit") or "1"))

            neue_haeufigkeit: int   = alte_haeufigkeit + 1
            neue_salienz:     float = salienz_berechnen(
                float(eingang_roh), neue_haeufigkeit,
            )

            redis_client.hset(key, mapping={
                "salienz":     str(neue_salienz),
                "haeufigkeit": str(neue_haeufigkeit),
            })

            if neue_salienz >= KZG_SALIENZ_HIGH:
                neuer_ttl: int = KZG_TTL_HIGH_SEKUNDEN
            elif neue_salienz >= KZG_SALIENZ_MID:
                neuer_ttl: int = KZG_TTL_MID_SEKUNDEN
            else:
                neuer_ttl: int = KZG_TTL_LOW_SEKUNDEN

            verbleibend: int = redis_client.ttl(key)
            if verbleibend < 0:
                verbleibend = 0
            effektiver_ttl: int = max(verbleibend, neuer_ttl)
            redis_client.expire(key, effektiver_ttl)

            verstaerkte.append({
                "key":     key,
                "salienz": neue_salienz,
                "themen":  existing_themen_raw,
            })

            logger.info(
                f"KZG Verstärkung: {key} — "
                f"salienz {alte_salienz:.4f} → {neue_salienz:.4f} "
                f"(Eingang {float(eingang_roh):.2f}), "
                f"häufigkeit {alte_haeufigkeit} → {neue_haeufigkeit}, "
                f"TTL {effektiver_ttl}s, "
                f"overlap={overlap}"
            )

        except Exception as ex:
            logger.warning(f"KZG Verstärkung: Fehler bei {key}: {ex}")

    if verstaerkte:
        logger.info(
            f"KZG Verstärkung: {len(verstaerkte)} verwandte Einträge verstärkt "
            f"für {user_id}:{character_id}"
        )

    return verstaerkte


def _neu_anlegen(
    rc,
    user_id:      str,
    character_id: str,
    beobachter:   str,
    salienz_obj:  dict,
    kern:         str,
    embedding:    list[float],
    salienz:      float,
    entitaet_ids: list[int] | None = None,
    timeline_id:  int | None       = None,
    turn_id:      str              = "",
) -> dict:
    """Legt einen neuen KZG-Eintrag an.

    Magnet-Felder (Synapsen P3):
      entitaet_ids: kommagetrennter String im RediSearch-TagField. Leere
                    Liste -> leerer String "" (RediSearch tolerant).
      timeline_id:  Integer im RediSearch-NumericField. None -> Feld wird
                    aus dem mapping= ausgelassen, damit der Index-Update
                    nicht bricht.

    Pipeline-Log: nach erfolgreichem hset wird ein log_db_write-Eintrag
    erzeugt (EVA-konform: Forensik nach Verarbeitung).

    Der Parameter `salienz` ist die BEWERTUNG des Modells — der unveraenderliche
    Eingang. Die Salienz, gegen die alle Tore pruefen, wird daraus abgeleitet
    (novaberg-kzg-salienz_k.md §3). Beide werden gespeichert: der Eingang, weil
    ohne ihn nichts nachrechenbar ist, das Ergebnis fuer die Leser.
    """
    salienz_eingang: float = salienz
    salienz_wert:    float = salienz_berechnen(salienz_eingang, 1)

    embedding_bytes: bytes = np.array(embedding, dtype=np.float32).tobytes()
    timestamp:       float = time.time()

    key:        str = _kzg_key(user_id, character_id, str(int(timestamp * 1000)))
    themen_str: str = ", ".join(salienz_obj.get("themen", []))
    dimension:  str = salienz_obj.get("dimension", "kontext")

    entitaet_ids_str: str = ",".join(str(eid) for eid in (entitaet_ids or []))

    mapping: dict = {
        "user_id":            user_id,
        "character_id":       character_id,
        "beobachter":         beobachter,
        "themen":             themen_str,
        "inhalt":             kern,
        "salienz":            str(salienz_wert),
        "salienz_eingang":    str(salienz_eingang),
        # Herkunft des Eingangswerts: Ein neu angelegter Eintrag traegt die
        # echte Modellbewertung. Der migrierte Bestand traegt teils
        # "geschaetzt" — ein Default darf nie aussehen wie ein echter Wert
        # (novaberg-kzg-salienz_k.md §10).
        "salienz_eingang_herkunft": "gemessen",
        "haeufigkeit":        str(1),
        "gedaechtnistyp":     salienz_obj.get("gedaechtnistyp", "kurz"),
        "dimension":          dimension,
        "intentionen":        json.dumps(salienz_obj.get("intentionen", [])),
        "emotion":            salienz_obj.get("emotion", "neutral"),
        "modus":              salienz_obj.get("modus", ""),
        "arousal":            str(salienz_obj.get("arousal", 0.5)),
        "emotions_vektor":    salienz_obj.get("emotions_vektor", ""),
        "sprach_stil":        salienz_obj.get("sprach_stil", "neutral"),
        "beziehungs_dynamik": salienz_obj.get("beziehungs_dynamik", "neutral"),
        "tone":               salienz_obj.get("tone", "sachlich"),
        "erstellt_am":        str(timestamp),
        "entitaet_ids":       entitaet_ids_str,
        # Der Turn, aus dem der Eintrag entstand. Bis zum 28.08.2026 stand
        # er nur im Pipeline-Log, nicht im Hash: 0 von 300 Eintraegen trugen
        # ihn, und die Promotion las ihn mit `_hget("turn_id")` ins Leere —
        # der Rueckweg-Auftrag bekam nie einen Turnbezug (Sachlage-Bruecke,
        # erstes Glied). Leer heisst unbekannt; nichts wird erfunden.
        "turn_id":            turn_id,
        "embedding":          embedding_bytes,
    }
    if timeline_id is not None:
        mapping["timeline_id"] = str(timeline_id)

    rc.hset(key, mapping=mapping)

    # Die TTL-Stufen stehen auf derselben gekruemmten Skala wie die Tore. Ein
    # roher Wert gegen ein gekruemmtes Tor waeren zwei Skalen nebeneinander.
    if salienz_wert >= KZG_SALIENZ_HIGH:
        ttl: int = KZG_TTL_HIGH_SEKUNDEN
    elif salienz_wert >= KZG_SALIENZ_MID:
        ttl: int = KZG_TTL_MID_SEKUNDEN
    else:
        ttl: int = KZG_TTL_LOW_SEKUNDEN
    rc.expire(key, ttl)

    logger.info(
        f"KZG: Neuer Eintrag — salienz={salienz_wert:.4f} "
        f"(Eingang {salienz_eingang:.2f}), themen={themen_str}, "
        f"entitaet_ids={entitaet_ids or []}, timeline_id={timeline_id}, TTL={ttl}s"
    )

    # Pipeline-Log: schreibender DB-Zugriff (Synapsen §10.2).
    log_db_write(
        turn_id = turn_id or "kzg-unbekannt",
        node    = "kzg_speicher",
        quelle  = user_id,
        inhalt  = {
            "tabelle":      "kzg",
            "operation":    "insert",
            "kzg_key":      key,
            "entitaet_ids": entitaet_ids or [],
            "timeline_id":  timeline_id,
            "themen":       themen_str,
            "dimension":       dimension,
            "salienz":         salienz_wert,
            "salienz_eingang": salienz_eingang,
            "ttl":             ttl,
        },
        user_id      = user_id,
        character_id = character_id,
    )

    return {
        "status": "neu",
        "key": key,
        "themen_str": themen_str,
        "dimension": dimension,
        # Die abgeleitete Salienz wandert mit: Der Aufrufer legt sie als
        # `neue_salienz` in den State, und agents/kzg/queues.py entscheidet
        # damit ueber die Promotion. Stuende dort der rohe Modellwert, pruefte
        # er gegen ein Tor auf der gekruemmten Skala und traefe es nie.
        "salienz": salienz_wert,
    }
