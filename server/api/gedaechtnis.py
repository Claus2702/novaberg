"""
Gedächtnis-Introspection — KZG, LZG, Hash, Fakten.
Debug- und Monitoring-Endpunkte.
"""

import dataclasses
import datetime
import json
import logging

import redis as redis_lib
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from config import (
    ASSISTANT_USER_ID,
    EMOTION_SEKTOR_MAP,
    INITIATIVE_RAD_NABE,
    INITIATIVE_RAD_SPANNE,
    RAD_MAX,
    RAD_MIN,
    RAD_NABE,
    REDIS_URL,
    postgres_verbinden,
    redis_client,
)
from memory.kzg import _kzg_prefix
from memory.session import _session_key

logger = logging.getLogger("ki_server.gedaechtnis")
router = APIRouter()


# ─────────────────────────────────────────────
# KZG (Redis)
# ─────────────────────────────────────────────
@router.get("/gedaechtnis/kzg/{user_id}")
def kzg_abrufen(
    user_id: str,
    character_id: str = ASSISTANT_USER_ID,
    beobachter: str | None = None,
):
    """Alle KZG-Einträge eines Gesprächspaares aus Redis.

    Optional per ``beobachter`` (``user``/``assistant``) filterbar.
    """
    try:
        keys:      list = redis_client.keys(_kzg_prefix(user_id, character_id))
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

            if beobachter and eintrag.get("beobachter", "") != beobachter:
                continue

            ttl: int = redis_client.ttl(key)

            eintraege.append({
                "key":            key,
                "themen":         eintrag.get("themen", ""),
                "inhalt":         eintrag.get("inhalt", ""),
                "salienz":        float(eintrag.get("salienz", 0)),
                "haeufigkeit":    int(float(eintrag.get("haeufigkeit", 1))),
                "dimension":      eintrag.get("dimension", ""),
                "gedaechtnistyp": eintrag.get("gedaechtnistyp", ""),
                "beobachter":     eintrag.get("beobachter", ""),
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
def lzg_abrufen(
    user_id: str,
    character_id: str = ASSISTANT_USER_ID,
    beobachter: str | None = None,
):
    """Alle LZG-Einträge eines Gesprächspaares.

    Optional per ``beobachter`` (``user``/``assistant``) filterbar.
    """
    try:
        conn   = postgres_verbinden()
        cursor = conn.cursor()

        if beobachter:
            cursor.execute("""
                SELECT dimension, inhalt, gewicht_decay, haeufigkeit,
                       erstellt_am, verstaerkt_am, beobachter
                FROM lzg_knoten
                WHERE user_id = %s AND character_id = %s
                  AND beobachter = %s AND aktiv = TRUE
                ORDER BY verstaerkt_am DESC
            """, (user_id, character_id, beobachter))
        else:
            cursor.execute("""
                SELECT dimension, inhalt, gewicht_decay, haeufigkeit,
                       erstellt_am, verstaerkt_am, beobachter
                FROM lzg_knoten
                WHERE user_id = %s AND character_id = %s AND aktiv = TRUE
                ORDER BY verstaerkt_am DESC
            """, (user_id, character_id))

        rows = cursor.fetchall()
        conn.close()

        eintraege: list = []
        for dimension, inhalt, gewicht, haeufigkeit, erstellt, verstaerkt, beob in rows:
            eintraege.append({
                "dimension":     dimension,
                "inhalt":        inhalt,
                "gewicht":       gewicht,
                "haeufigkeit":   haeufigkeit,
                "erstellt_am":   erstellt.isoformat() if erstellt else "",
                "verstaerkt_am": verstaerkt.isoformat() if verstaerkt else "",
                "beobachter":    beob or "",
            })

        return {"eintraege": eintraege, "anzahl": len(eintraege)}

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})


# ─────────────────────────────────────────────
# Charakter-Hash
# ─────────────────────────────────────────────
@dataclasses.dataclass(frozen=True)
class RadSpalten:
    """Die vier Spalten, in denen ein Charakter-Rad in der Datenbank liegt.

    Sie gehoeren zusammen und werden nie einzeln gebraucht: Der Wert ohne
    seine Herkunft ist nicht einzuordnen, das Speichen-JSON ohne den Wert
    nicht nachrechenbar. Als vier lose Parameter waeren sie zudem
    vertauschbar — ``quelle`` und ``rad_roh`` sind beide Text.
    """

    rad_roh: str | None
    wert: float | None
    quelle: str | None
    erhoben_am: datetime.datetime | None


@dataclasses.dataclass(frozen=True)
class RadGrenzen:
    """Nabe und Grenzen eines Rades — seine Bauart, nicht sein Inhalt.

    Sie haengen am Rad-Typ, nicht an der Zeile: Jede Zeile des
    Zuwendungs-Rades hat dieselbe Nabe. Deshalb stehen sie getrennt von
    ``RadSpalten``.
    """

    nabe: float
    minimum: float
    maximum: float


# Die Bauart je Rad, einmal aus der Konfiguration gelesen. Das
# Initiative-Rad traegt eine symmetrische Spanne um seine Nabe, das
# Zuwendungs-Rad zwei verschiedene — deshalb beide Grenzen einzeln und
# nicht eine Spanne.
_GRENZEN_ZUWENDUNG = RadGrenzen(nabe=RAD_NABE, minimum=RAD_MIN, maximum=RAD_MAX)
_GRENZEN_INITIATIVE = RadGrenzen(
    nabe=INITIATIVE_RAD_NABE,
    minimum=-INITIATIVE_RAD_SPANNE,
    maximum=INITIATIVE_RAD_SPANNE,
)


def _rad_aufbereiten(
    bezeichnung: str, spalten: RadSpalten, grenzen: RadGrenzen,
) -> dict:
    """Baut den Anzeige-Block eines Charakter-Rades aus seinen vier Spalten.

    Das Rad liegt in der Datenbank als TEXT. Es wird **hier** geparst, nicht
    beim Leser: Ein JSON-Feld, das ungeparst weitergereicht wird, sieht am
    Ziel wie ein Wert aus und rechnet still falsch — genau so lief M1 zwei
    Monate als Konstante (``KALIBRIER-INTENTIONEN-UNGEPARST``).

    ``lesbar`` trennt drei Faelle, die ein leeres Rad sonst zusammenwerfen:
    die Zeile fehlt, das JSON ist kaputt, oder alle Speichen stehen echt auf
    0.0. Nur der dritte ist ein Messergebnis.

    **Nabe, Minimum und Maximum reisen mit.** Sie sind serverseitige
    Konstanten und ueber die Umgebung einstellbar; eine Kopie im Anzeiger
    waere eine zweite Quelle derselben Groesse und liefe beim naechsten
    Verstellen still auseinander. Der Anzeiger braucht sie, um den Abstand
    des Werts von der Nabe als Anteil der jeweiligen Spanne zu zeichnen —
    die beiden Spannen sind nicht symmetrisch.

    Args:
        bezeichnung: Name des Rades fuer die Logausgabe.
        spalten:     Die vier Datenbankspalten des Rades.
        grenzen:     Nabe und Grenzen seiner Bauart.

    Returns:
        Dict mit ``wert``, ``quelle``, ``erhoben_am``, ``rad``, ``lesbar``
        sowie ``nabe``, ``minimum`` und ``maximum``.
    """

    def block(rad_inhalt: dict, lesbar: bool) -> dict:
        """Setzt die Antwort zusammen — eine Form, vier Ausgaenge."""
        return {
            "wert":       float(spalten.wert) if spalten.wert is not None else None,
            "quelle":     spalten.quelle or "",
            "erhoben_am": spalten.erhoben_am.isoformat() if spalten.erhoben_am else "",
            "rad":        rad_inhalt,
            "lesbar":     lesbar,
            "nabe":       float(grenzen.nabe),
            "minimum":    float(grenzen.minimum),
            "maximum":    float(grenzen.maximum),
        }

    # ── Eingabe ──────────────────────────────────────────────────────
    if not spalten.rad_roh:
        logger.warning(f"Charakter-Rad '{bezeichnung}': Spalte leer")
        return block({}, lesbar=False)

    # ── Verarbeitung ─────────────────────────────────────────────────
    try:
        rad: dict = json.loads(spalten.rad_roh)
    except (ValueError, TypeError) as fehler:
        logger.exception(
            f"{type(fehler).__name__}: Charakter-Rad '{bezeichnung}': "
            f"JSON nicht lesbar — Rohwert: {spalten.rad_roh[:120]!r}"
        )
        return block({}, lesbar=False)

    # ── Ausgabe ──────────────────────────────────────────────────────
    if not isinstance(rad, dict) or "hoch" not in rad or "runter" not in rad:
        logger.error(
            f"Charakter-Rad '{bezeichnung}': geparst, aber ohne die Seiten "
            f"'hoch'/'runter' — Typ {type(rad).__name__}, "
            f"Schluessel {list(rad)[:8] if isinstance(rad, dict) else '—'}"
        )
        return block({}, lesbar=False)

    logger.debug(
        f"Charakter-Rad '{bezeichnung}': {len(rad['hoch'])} hoch, "
        f"{len(rad['runter'])} runter, quelle={spalten.quelle}, "
        f"wert={spalten.wert}, Nabe {grenzen.nabe} "
        f"in [{grenzen.minimum}, {grenzen.maximum}]"
    )
    return block(rad, lesbar=True)


def _hash_leer() -> dict:
    """Antwort fuer ein Gespraechspaar ohne Zeile in ``charakter_hash``.

    ``lesbar: False`` bei beiden Raedern ist hier die Aussage: Es gibt keine
    Erhebung. Ein Rad voller Nullen waere an dieser Stelle eine Behauptung.
    """
    leeres_rad: dict = {
        "wert": None, "quelle": "", "erhoben_am": "", "rad": {}, "lesbar": False,
    }
    zuwendung: dict = dict(leeres_rad, **dataclasses.asdict(_GRENZEN_ZUWENDUNG))
    initiative: dict = dict(leeres_rad, **dataclasses.asdict(_GRENZEN_INITIATIVE))
    return {
        "kern_hash": "", "adaptive_hash": "",
        "intentions_profil": "", "emotions_profil": "",
        "beziehungsprofil": "",
        "kern_aktualisiert": "", "adaptive_aktualisiert": "",
        "intentions_aktualisiert": "", "emotions_aktualisiert": "",
        "beziehung_aktualisiert": "",
        "zuwendung":  zuwendung,
        "initiative": initiative,
    }


@router.get("/gedaechtnis/hash/{user_id}")
def hash_abrufen(user_id: str, character_id: str = ASSISTANT_USER_ID):
    """Charakter-Hash eines Users fuer ein bestimmtes Gespraechspaar.

    Seit dem Paar-Schema (Chat 62) wird nach ``user_id`` + ``character_id``
    gefiltert. Die Zeile traegt neben den fuenf Profilen die **zwei
    Charakter-Raeder** des Subjekts gegenueber seinem Gegenueber: die
    Zuwendung (zwoelf Speichen, ``novaberg-salienz-berechnung_k.md`` §5) und
    den Initiative-Versatz (zehn Speichen, ``novaberg-gv-initiative_k.md``
    §6). Beide werden hier mitgeliefert, samt Herkunft — ohne die ist ein
    Wert von 0.9 bzw. 0.00 nicht von einem Ausfall zu unterscheiden.
    """
    try:
        conn   = postgres_verbinden()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT kern_hash, adaptive_hash,
                   intentions_profil, emotions_profil, beziehungsprofil,
                   kern_aktualisiert_am, adaptive_aktualisiert_am,
                   intentions_aktualisiert_am, emotions_aktualisiert_am,
                   beziehung_aktualisiert_am,
                   nutzer_gewichtung, nutzer_gewichtung_quelle,
                   nutzer_gewichtung_rad, nutzer_gewichtung_am,
                   initiative_versatz, initiative_versatz_quelle,
                   initiative_versatz_rad, initiative_versatz_am
            FROM charakter_hash
            WHERE user_id = %s AND character_id = %s
        """, (user_id, character_id))

        row = cursor.fetchone()
        conn.close()

        if not row:
            logger.info(
                f"hash_abrufen: keine Zeile fuer {user_id}/{character_id}"
            )
            return _hash_leer()

        return {
            "kern_hash":                row[0] or "",
            "adaptive_hash":            row[1] or "",
            "intentions_profil":        row[2] or "",
            "emotions_profil":          row[3] or "",
            "beziehungsprofil":         row[4] or "",
            "kern_aktualisiert":        row[5].isoformat() if row[5] else "",
            "adaptive_aktualisiert":    row[6].isoformat() if row[6] else "",
            "intentions_aktualisiert":  row[7].isoformat() if row[7] else "",
            "emotions_aktualisiert":    row[8].isoformat() if row[8] else "",
            "beziehung_aktualisiert":   row[9].isoformat() if row[9] else "",
            "zuwendung": _rad_aufbereiten(
                f"zuwendung {user_id}->{character_id}",
                RadSpalten(row[12], row[10], row[11], row[13]),
                _GRENZEN_ZUWENDUNG,
            ),
            "initiative": _rad_aufbereiten(
                f"initiative {user_id}->{character_id}",
                RadSpalten(row[16], row[14], row[15], row[17]),
                _GRENZEN_INITIATIVE,
            ),
        }

    except Exception as fehler:
        return JSONResponse(status_code=500, content={"fehler": str(fehler)})


# ─────────────────────────────────────────────
# Fakten
# ─────────────────────────────────────────────
@router.get("/fakten/{user_id}")
def fakten_abrufen(user_id: str):
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
            for (
                attribut,
                objekt_wert,
                objekt_id,
                fakt_text,
                t_valid,
                t_invalid,
                last_touched,
            ) in cursor.fetchall():
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
def emotionen_abrufen(
    user_id: str,
    character_id: str = ASSISTANT_USER_ID,
    beobachter: str | None = None,
):
    """Emotions-Radar-Daten: Aggregierte Arousal-Werte pro Emotion für Session und KZG.

    ``beobachter`` filtert bei Session die Turn-Rolle (user/assistant) und
    bei KZG das ``beobachter``-Feld des Eintrags.
    """

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

    # Rolle, nach der die Session-Turns gefiltert werden (user / assistant / alle).
    turn_rolle: str | None = beobachter

    try:
        # --- Session-Turns ---
        session_turns: list = []
        try:
            raw_turns: list = redis_client.lrange(
                _session_key(user_id, character_id, "turns"), 0, -1
            )
            for raw in raw_turns:
                turn: dict = json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
                rolle: str = turn.get("rolle", "")
                if turn_rolle and rolle != turn_rolle:
                    continue
                # Ohne Filter: nur user-Turns (bisheriges Verhalten als Default).
                if not turn_rolle and rolle != "user":
                    continue
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
            keys: list = redis_client.keys(_kzg_prefix(user_id, character_id))
            for key in keys:
                daten: dict = raw_redis.hgetall(key.encode() if isinstance(key, str) else key)

                if beobachter:
                    beob_raw = daten.get(b"beobachter", b"")
                    beob: str = beob_raw.decode() if isinstance(beob_raw, bytes) else beob_raw
                    if beob != beobachter:
                        continue

                emotion_raw = daten.get(b"emotion", b"neutral")
                emotion: str = (
                    emotion_raw.decode() if isinstance(emotion_raw, bytes) else emotion_raw
                )
                arousal_raw = daten.get(b"arousal", b"0")
                arousal: float = float(
                    arousal_raw.decode() if isinstance(arousal_raw, bytes) else arousal_raw
                )
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
