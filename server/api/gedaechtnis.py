"""
Gedächtnis-Introspection — KZG, LZG, Hash, Fakten.
Debug- und Monitoring-Endpunkte.
"""

import json
import logging

import redis as redis_lib
from fastapi           import APIRouter
from fastapi.responses import JSONResponse

from config import redis_client, REDIS_URL, postgres_verbinden, EMOTION_SEKTOR_MAP

logger = logging.getLogger("ki_server.gedaechtnis")
router = APIRouter()


# ─────────────────────────────────────────────
# KZG (Redis)
# ─────────────────────────────────────────────
@router.get("/gedaechtnis/kzg/{user_id}")
def KzgAbrufen(user_id: str):
    """Alle KZG-Einträge eines Users aus Redis."""
    try:
        keys:      list = redis_client.keys(f"kzg:{user_id}:*")
        eintraege: list = []

        raw_redis = redis_lib.from_url(REDIS_URL, decode_responses=False)

        for key in keys:
            daten: dict = raw_redis.hgetall(key.encode() if isinstance(key, str) else key)

            eintrag: dict = {}
            for k, v in daten.items():
                feld: str = k.decode() if isinstance(k, bytes) else k
                if feld == "embedding":
                    continue
                eintrag[feld] = v.decode() if isinstance(v, bytes) else v

            ttl: int = redis_client.ttl(key)

            eintraege.append({
                "key":            key,
                "themen":         eintrag.get("themen", ""),
                "inhalt":         eintrag.get("inhalt", ""),
                "salienz":        float(eintrag.get("salienz", 0)),
                "haeufigkeit":    int(float(eintrag.get("haeufigkeit", 1))),
                "dimension":      eintrag.get("dimension", ""),
                "gedaechtnistyp": eintrag.get("gedaechtnistyp", ""),
                "ttl_sekunden":   ttl,
            })

        eintraege.sort(key=lambda e: e["salienz"], reverse=True)
        return {"eintraege": eintraege, "anzahl": len(eintraege)}

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})


# ─────────────────────────────────────────────
# LZG (PostgreSQL)
# ─────────────────────────────────────────────
@router.get("/gedaechtnis/lzg/{user_id}")
def LzgAbrufen(user_id: str):
    """Alle LZG-Einträge eines Users."""
    try:
        conn   = postgres_verbinden()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT dimension, inhalt, gewicht, haeufigkeit, erstellt_am, verstaerkt_am
            FROM langzeitgedaechtnis
            WHERE user_id = %s AND aktiv = TRUE
            ORDER BY verstaerkt_am DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        eintraege: list = []
        for dimension, inhalt, gewicht, haeufigkeit, erstellt, verstaerkt in rows:
            eintraege.append({
                "dimension":     dimension,
                "inhalt":        inhalt,
                "gewicht":       gewicht,
                "haeufigkeit":   haeufigkeit,
                "erstellt_am":   erstellt.isoformat() if erstellt else "",
                "verstaerkt_am": verstaerkt.isoformat() if verstaerkt else "",
            })

        return {"eintraege": eintraege, "anzahl": len(eintraege)}

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})


# ─────────────────────────────────────────────
# Charakter-Hash
# ─────────────────────────────────────────────
@router.get("/gedaechtnis/hash/{user_id}")
def HashAbrufen(user_id: str):
    """Charakter-Hash eines Users."""
    try:
        conn   = postgres_verbinden()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT kern_hash, adaptive_hash,
                   intentions_profil, emotions_profil, beziehungsprofil,
                   kern_aktualisiert_am, adaptive_aktualisiert_am
            FROM charakter_hash
            WHERE user_id = %s
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                "kern_hash": "", "adaptive_hash": "",
                "intentions_profil": "", "emotions_profil": "",
                "beziehungsprofil": "",
                "kern_aktualisiert": "", "adaptive_aktualisiert": "",
            }

        return {
            "kern_hash":             row[0] or "",
            "adaptive_hash":         row[1] or "",
            "intentions_profil":     row[2] or "",
            "emotions_profil":       row[3] or "",
            "beziehungsprofil":      row[4] or "",
            "kern_aktualisiert":     row[5].isoformat() if row[5] else "",
            "adaptive_aktualisiert": row[6].isoformat() if row[6] else "",
        }

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})


# ─────────────────────────────────────────────
# Fakten
# ─────────────────────────────────────────────
@router.get("/fakten/{user_id}")
def FaktenAbrufen(user_id: str):
    """Alle Entitäten mit ihren Fakten (M2-Schema)."""
    try:
        conn   = postgres_verbinden()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT e.id, e.name, e.typ, e.zusammenfassung
            FROM entitaeten e
            WHERE e.user_id = %s AND e.aktiv = TRUE
            ORDER BY e.name
        """, (user_id,))

        entitaeten: list = []
        for eid, name, typ, zusammenfassung in cursor.fetchall():
            cursor.execute("""
                SELECT attribut, objekt_wert, objekt_id, fakt_text,
                       t_valid, t_invalid, last_touched
                FROM fakten
                WHERE subjekt_id = %s AND user_id = %s AND aktiv = TRUE
                ORDER BY attribut
            """, (eid, user_id))

            relationen: list = []
            for attribut, objekt_wert, objekt_id, fakt_text, t_valid, t_invalid, last_touched in cursor.fetchall():
                relationen.append({
                    "attribut":     attribut,
                    "objekt_wert":  objekt_wert or "",
                    "objekt_id":    objekt_id,
                    "fakt_text":    fakt_text or "",
                    "t_valid":      t_valid.isoformat() if t_valid else "",
                    "t_invalid":    t_invalid.isoformat() if t_invalid else None,
                    "last_touched": last_touched.isoformat() if last_touched else "",
                })

            entitaeten.append({
                "id":              eid,
                "name":            name,
                "typ":             typ,
                "zusammenfassung": zusammenfassung or "",
                "fakten":          relationen,
            })

        conn.close()
        return {"entitaeten": entitaeten, "anzahl": len(entitaeten)}

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})


# ─────────────────────────────────────────────
# Emotionen (Radar-Daten)
# ─────────────────────────────────────────────
@router.get("/gedaechtnis/emotionen/{user_id}")
def EmotionenAbrufen(user_id: str):
    """Emotions-Radar-Daten: Aggregierte Arousal-Werte pro Emotion für Session und KZG."""

    def emotionen_aggregieren(eintraege: list) -> dict:
        """Berechnet Durchschnitts-Arousal pro Einzelemotion.

        Gibt nur Emotionen zurück, die in EMOTION_SEKTOR_MAP bekannt sind.
        Der Client aggregiert dann per Sektor (max).
        """
        summen: dict[str, float] = {}
        zaehler: dict[str, int] = {}
        for e in eintraege:
            emotion: str = e.get("emotion", "neutral")
            if emotion not in EMOTION_SEKTOR_MAP:
                continue
            arousal: float = e.get("arousal", 0.0)
            summen[emotion] = summen.get(emotion, 0.0) + arousal
            zaehler[emotion] = zaehler.get(emotion, 0) + 1

        return {em: round(summen[em] / zaehler[em], 2) for em in summen}

    try:
        # --- Session-Turns ---
        session_turns: list = []
        try:
            raw_turns: list = redis_client.lrange(f"session:{user_id}:turns", 0, -1)
            for raw in raw_turns:
                turn: dict = json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
                if turn.get("rolle") == "user":
                    emotion: str = turn.get("emotion", "neutral")
                    arousal_raw = turn.get("arousal", 0)
                    arousal: float = float(arousal_raw) if arousal_raw else 0.0
                    session_turns.append({"emotion": emotion, "arousal": arousal})
        except Exception as e:
            logger.warning(f"Session-Turns lesen fehlgeschlagen: {e}")

        # --- KZG-Einträge ---
        kzg_eintraege: list = []
        try:
            raw_redis = redis_lib.from_url(REDIS_URL, decode_responses=False)
            keys: list = redis_client.keys(f"kzg:{user_id}:*")
            for key in keys:
                daten: dict = raw_redis.hgetall(key.encode() if isinstance(key, str) else key)
                emotion_raw = daten.get(b"emotion", b"neutral")
                emotion: str = emotion_raw.decode() if isinstance(emotion_raw, bytes) else emotion_raw
                arousal_raw = daten.get(b"arousal", b"0")
                arousal: float = float(arousal_raw.decode() if isinstance(arousal_raw, bytes) else arousal_raw)
                kzg_eintraege.append({"emotion": emotion, "arousal": arousal})
        except Exception as e:
            logger.warning(f"KZG-Emotionen lesen fehlgeschlagen: {e}")

        return {
            "session": emotionen_aggregieren(session_turns),
            "kzg": emotionen_aggregieren(kzg_eintraege),
            "session_turns": len(session_turns),
            "kzg_eintraege": len(kzg_eintraege),
        }

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})
