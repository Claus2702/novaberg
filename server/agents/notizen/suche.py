"""Such-Node -- Gewichtete Multi-Feld-Suche mit pg_trgm und Score-Gap.

Sucht Notizen ueber name, text und themen-Array mit konfigurierbaren
Gewichtungen je nach target_typ (titel/inhalt/thema).
"""

import json
import logging

from agents.base import AgentState
from config import (
    NOTIZEN_SUCHE_LIMIT,
    NOTIZEN_SUCHE_MIN_SCORE,
    NOTIZEN_SUCHE_MIN_SIMILARITY,
)

logger = logging.getLogger("ki_server.agents.notizen.suche")

# Gewichtungen fuer Multi-Feld-Suche je nach Target-Typ
SUCH_GEWICHTE = {
    "titel":  {"name": 2.0, "text": 1.0, "themen": 1.0},
    "inhalt": {"name": 1.0, "text": 2.0, "themen": 0.5},
    "thema":  {"name": 1.0, "text": 1.0, "themen": 2.0},
}


def suchen(state: AgentState) -> dict:
    """Sucht die betroffene Notiz in der Datenbank."""
    from config import POSTGRES_URL
    from memory.repositories.notizen_repository import NotizenRepository

    target = state["parameter"].get("target", "")
    user_id = state["kontext"].get("user_id", "")
    action = state["parameter"].get("action", "")
    logger.debug(f"suchen: Einstieg -- action='{action}', target='{target}', user_id='{user_id}'")

    # READ ohne Target: Alle aktiven Notizen auflisten
    if action == "read" and not target:
        logger.debug("suchen: READ ohne Target -- lade alle Notizen")
        notizen = NotizenRepository.find_by_user(POSTGRES_URL, user_id)
        logger.debug(f"suchen: find_by_user -- {len(notizen)} Treffer")
        if not notizen:
            logger.debug("suchen: Return -- status='abgeschlossen', keine Notizen")
            return {
                "ergebnis": "Du hast aktuell keine Notizen.",
                "status": "abgeschlossen",
                "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "keine_notizen"}],
            }
        for n in notizen:
            logger.debug(
                f"suchen: Treffer -- id={n['id']}, name='{n['name']}', typ='{n.get('typ', '?')}'"
            )
        # Kompakte Uebersicht fuer den Responder
        zeilen = []
        for n in notizen:
            zeile = f"- {n['name']} ({n['typ']})"
            zf = n.get("zusammenfassung")
            if zf:
                zeile += f": {zf}"
            zeilen.append(zeile)
        logger.debug(
            f"suchen: Return -- status='abgeschlossen', {len(notizen)} Notizen aufgelistet"
        )
        return {
            "ergebnis": "Deine Notizen:\n" + "\n".join(zeilen),
            "status": "abgeschlossen",
            "schritte": state["schritte"]
            + [{"node": "suchen", "ergebnis": f"{len(notizen)} Notizen"}],
        }

    # Gewichtete Multi-Feld-Suche mit pg_trgm
    # Gewichtung haengt vom target_typ ab (titel/inhalt/thema)
    from tools.db_manager import db_manager

    target_typ = state["parameter"].get("target_typ", "titel")
    gewichte = SUCH_GEWICHTE.get(target_typ, SUCH_GEWICHTE["titel"])
    logger.debug(f"suchen: Gewichtete Suche -- target_typ='{target_typ}', gewichte={gewichte}")

    such_query = (
        "SELECT id, name, typ, text, zusammenfassung, themen, status, "
        "  created_at, updated_at, "
        "  ("
        "    COALESCE(similarity(LOWER(name), LOWER(%s)), 0) * %s + "
        "    COALESCE(similarity(LOWER(COALESCE(text, '')), LOWER(%s)), 0) * %s + "
        "    COALESCE("
        "      (SELECT MAX(similarity(LOWER(t), LOWER(%s))) FROM unnest(themen) AS t),"
        "      0"
        "    ) * %s"
        "  ) AS score "
        "FROM notizen "
        "WHERE user_id = %s AND aktiv = TRUE "
        "AND ("
        "  similarity(LOWER(name), LOWER(%s)) > %s "
        "  OR similarity(LOWER(COALESCE(text, '')), LOWER(%s)) > %s "
        "  OR EXISTS ("
        "    SELECT 1 FROM unnest(themen) t WHERE similarity(LOWER(t), LOWER(%s)) > %s"
        "  )"
        ") "
        "ORDER BY score DESC "
        f"LIMIT {NOTIZEN_SUCHE_LIMIT}"
    )
    such_params = (
        target, gewichte["name"],
        target, gewichte["text"],
        target, gewichte["themen"],
        user_id,
        target, NOTIZEN_SUCHE_MIN_SIMILARITY,
        target, NOTIZEN_SUCHE_MIN_SIMILARITY,
        target, NOTIZEN_SUCHE_MIN_SIMILARITY,
    )

    treffer = db_manager.select(such_query, such_params)
    # Mindest-Score filtern
    treffer = [t for t in treffer if t.get("score", 0) >= NOTIZEN_SUCHE_MIN_SCORE]
    logger.debug(
        f"suchen: Gewichtete Suche -- {len(treffer)} Treffer (score >= {NOTIZEN_SUCHE_MIN_SCORE})"
    )

    # Fallback: Exakter Name-Match wenn gewichtete Suche nichts findet
    if not treffer:
        logger.debug(f"suchen: Fallback -- find_by_stichwort(target='{target}')")
        treffer = NotizenRepository.find_by_stichwort(POSTGRES_URL, user_id, target)
        logger.debug(f"suchen: Fallback -- {len(treffer)} Treffer")

    # Fallback: Volltext
    if not treffer:
        logger.debug(f"suchen: Fallback -- find_by_volltext(target='{target}')")
        treffer = NotizenRepository.find_by_volltext(POSTGRES_URL, user_id, target)
        logger.debug(f"suchen: Fallback -- {len(treffer)} Treffer")

    for t in treffer:
        logger.debug(
            f"suchen: Treffer -- id={t['id']}, name='{t['name']}', score={t.get('score', '?')}"
        )

    if not treffer:
        if action == "read":
            logger.debug("suchen: Return -- status='abgeschlossen', nicht gefunden (read)")
            return {
                "status": "abgeschlossen",
                "ergebnis": f"Keine Notiz mit '{target}' gefunden.",
                "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden"}],
            }

        if action in ("add_content", "remove_content"):
            logger.info(f"suchen: '{target}' nicht gefunden bei {action} -- Rueckfrage ob anlegen")
            return {
                "status": "rueckfrage",
                "rueckfrage": json.dumps({
                    "typ": "nicht_gefunden",
                    "agent": "notizen",
                    "aktion": action,
                    "target": target,
                    "original_aufgabe": state["aufgabe"],
                }, ensure_ascii=False),
                "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden_rueckfrage"}],
            }

        logger.debug("suchen: Return -- status='fehler', nicht gefunden")
        return {
            "status": "fehler",
            "fehler": f"Keine Notiz mit '{target}' gefunden.",
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "nicht_gefunden"}],
        }

    # Score-Gap-Pruefung: Klaren Gewinner erkennen, Rauschen abschneiden
    if len(treffer) >= 2 and all("score" in t for t in treffer):
        scores = [t["score"] for t in treffer]
        avg = sum(scores) / len(scores)

        # Finde die natuerliche Trennlinie:
        # Gehe die sortierte Liste durch, suche den ersten Gap >= avg.
        # Alles oberhalb der Trennlinie ist die Gewinner-Gruppe.
        trennlinie = len(treffer)  # Default: alle behalten
        for i in range(len(scores) - 1):
            gap = scores[i] - scores[i + 1]
            if gap >= avg:
                trennlinie = i + 1
                break

        if trennlinie < len(treffer):
            abgeschnitten = treffer[trennlinie:]
            treffer = treffer[:trennlinie]

            # Die Verworfenen gehoeren in dieselbe Zeile wie die Behaltenen.
            # Ohne sie ist eine zu scharfe Trennlinie von einer knappen
            # Trefferlage nicht zu unterscheiden — beide Male steht dort nur,
            # wie viele uebrig blieben.
            verworfen: str = (
                f"{len(abgeschnitten)} verworfen "
                f"(scores={[f'{t["score"]:.2f}' for t in abgeschnitten[:3]]}"
                f"{', ...' if len(abgeschnitten) > 3 else ''})"
            )

            if len(treffer) == 1:
                logger.info(
                    f"suchen: Score-Gap -- Klarer Gewinner: '{treffer[0]['name']}' "
                    f"(score={scores[0]:.2f}, gap={scores[0] - scores[1]:.2f}, avg={avg:.2f}) "
                    f"-- {verworfen}"
                )
            else:
                logger.info(
                    f"suchen: Score-Gap -- {len(treffer)} Kandidaten in Gewinner-Gruppe "
                    f"(scores={[f'{s:.2f}' for s in scores[:trennlinie]]}, avg={avg:.2f}) "
                    f"-- {verworfen} -- Disambiguierung"
                )

    if len(treffer) > 1 and action in ("update", "delete", "append"):
        kandidaten = [
            {
                "id": n["id"],
                "name": n["name"],
                "zusammenfassung": n.get("zusammenfassung", ""),
                "erstellt": str(n.get("created_at", "")),
            }
            for n in treffer
        ]
        logger.debug(
            f"suchen: Return -- status='rueckfrage', {len(kandidaten)} Kandidaten zur "
            "Disambiguierung"
        )
        return {
            "status": "rueckfrage",
            "rueckfrage": json.dumps({
                "typ": "disambiguierung",
                "agent": "notizen",
                "aktion": action,
                "kandidaten": kandidaten,
            }, ensure_ascii=False),
            "schritte": state["schritte"] + [{"node": "suchen", "ergebnis": "mehrdeutig", "anzahl": len(treffer)}],
        }

    # Bei read mit Treffer: direkt Inhalt zurueckgeben
    if action == "read":
        notiz = treffer[0]
        logger.debug(f"suchen: Return -- status='abgeschlossen', read notiz_id={notiz['id']}")
        return {
            "ergebnis": f"[{notiz['name']} ({notiz['typ']})]\n{notiz['text']}",
            "status": "abgeschlossen",
            "schritte": state["schritte"]
            + [{"node": "suchen", "ergebnis": f"gefunden: {notiz['name']}"}],
        }

    notiz = treffer[0]
    logger.debug(
        f"suchen: Return -- status='laufend', notiz_id={notiz['id']}, name='{notiz['name']}'"
    )
    return {
        "parameter": {**state["parameter"], "notiz": notiz},
        "status": "laufend",
        "schritte": state["schritte"]
        + [{"node": "suchen", "ergebnis": f"gefunden: {notiz['name']}"}],
    }
