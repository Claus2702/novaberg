"""CRUD-Nodes -- Erstellen, Aktualisieren, Loeschen, Anhaengen, Leeren, Umbenennen von Notizen.

Erweitert in Chat 42 (CRUD-Haertung):
- Neue Aktionen: add_content, remove_content, clear_content, rename
- Verifikation nach Schreiboperationen (DB-Read nach Write)
- add_content/remove_content nutzen den bestehenden LLM-Update-Flow
- clear_content ist deterministisch (kein LLM-Call)
"""

import json
import logging

from agents.base import AgentState
from config import NOTIZEN_ZUSAMMENFASSUNG_MAX_WOERTER

logger = logging.getLogger("ki_server.agents.notizen.crud")


def _zusammenfassung_generieren(text: str, max_woerter: int = NOTIZEN_ZUSAMMENFASSUNG_MAX_WOERTER) -> str:
    """Erste N Woerter als Zusammenfassung."""
    woerter = text.split()
    if len(woerter) <= max_woerter:
        return text
    return " ".join(woerter[:max_woerter]) + "..."


def _verifizieren_notiz(notiz_id: int, erwartung: dict) -> bool:
    """Prueft ob die DB-Operation den erwarteten Effekt hatte."""
    from tools.db_manager import db_manager

    eintrag = db_manager.select_one(
        "SELECT id, text, aktiv, status FROM notizen WHERE id = %s",
        (notiz_id,),
    )
    if not eintrag:
        logger.error(f"Verifikation: Notiz ID {notiz_id} nicht gefunden")
        return False

    if "aktiv" in erwartung and eintrag["aktiv"] != erwartung["aktiv"]:
        logger.error(f"Verifikation: Notiz ID {notiz_id} aktiv={eintrag['aktiv']}, erwartet={erwartung['aktiv']}")
        return False

    if "text_nicht_leer" in erwartung and not eintrag.get("text"):
        logger.error(f"Verifikation: Notiz ID {notiz_id} Text ist leer, sollte nicht leer sein")
        return False

    if "text_leer" in erwartung and eintrag.get("text") and eintrag["text"].strip():
        logger.error(f"Verifikation: Notiz ID {notiz_id} Text ist nicht leer, sollte leer sein")
        return False

    return True


def ausfuehren(state: AgentState) -> dict:
    """Fuehrt die CRUD-Operation aus."""
    action = state["parameter"].get("action", "")
    normalisiert = state["parameter"].get("normalisiert", "")
    logger.debug(f"ausfuehren: Einstieg -- action='{action}', normalisiert='{normalisiert}'")
    logger.debug(f"ausfuehren: parameter keys={list(state['parameter'].keys())}")

    if "notiz" in state["parameter"]:
        notiz = state["parameter"]["notiz"]
        logger.debug(f"ausfuehren: notiz -- id={notiz.get('id')}, name='{notiz.get('name', '?')}'")

    if action == "create":
        return _create(state)
    elif action in ("update", "add_content", "remove_content"):
        return _update(state)
    elif action == "delete":
        return _delete(state)
    elif action == "append":
        return _append(state)
    elif action == "clear_content":
        return _clear_content(state)
    elif action == "rename":
        return _rename(state)

    logger.debug(f"ausfuehren: Unbehandelte Aktion '{action}'")
    return {
        "status": "fehler",
        "fehler": f"Unbehandelte Aktion: {action}",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "unbehandelt"}],
    }


def _create(state: AgentState) -> dict:
    """Neue Notiz anlegen -- LLM extrahiert Name, Typ, Text, Themen."""
    from config import POSTGRES_URL, get_node_config
    from memory.repositories.notizen_repository import NotizenRepository
    from services.model_services import model_service, ChatRequest

    user_id = state["kontext"].get("user_id", "")
    prompt = state["aufgabe"]
    normalisiert = state["parameter"].get("normalisiert", "")
    logger.debug(f"_create: Einstieg -- user_id='{user_id}', prompt='{prompt[:80]}...', normalisiert='{normalisiert}'")

    if normalisiert:
        user_content = (
            f"NORMALISIERTE ANWEISUNG:\n{normalisiert}\n\n"
            f"ORIGINAL-PROMPT DES NUTZERS:\n{prompt}"
        )
    else:
        user_content = prompt

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
    # _create() laeuft im NotizenAgent (sync invoke), aufgerufen entweder
    # aus dem CharacterGraph via agent_dispatch_node oder aus
    # services/pixie/dispatch.py — beide Pfade nutzen asyncio.to_thread.
    # Kein Event-Loop im aufrufenden Thread → submit_sync.
    chat_request = ChatRequest(
        messages          = [{"role": "user", "content": user_content}],
        system            = (
            "Extrahiere aus dem folgenden Text eine Notiz. "
            "Antworte NUR mit JSON: "
            '{"name": "Kurzname", "typ": "einkauf|todo|merkliste|notiz|entwurf|idee", '
            '"text": "Vollstaendiger Inhalt", '
            '"themen": ["thema1", "thema2"]}\n\n'
            "Wenn eine NORMALISIERTE ANWEISUNG vorhanden ist, nutze sie als primaere Quelle:\n"
            "- Der Name steht nach dem Apostroph in der Anweisung\n"
            "- Der Inhalt steht nach 'mit Inhalt:' oder ist das genannte Element\n"
            "- Der Typ steht in Klammern am Ende\n\n"
            "Wenn KEINE normalisierte Anweisung vorhanden ist, extrahiere aus dem Original-Prompt.\n\n"
            "WICHTIG fuer 'text': Der Inhalt ist das WAS gespeichert werden soll, "
            "NICHT die Anweisung des Users. "
            "'Setz Kuemmel auf die Einkaufsliste' -> text = 'Kuemmel', NICHT 'Setz Kuemmel auf die Einkaufsliste'.\n"
            "'Notiere dir: Durch diese hohle Gasse wird er kommen' -> text = 'Durch diese hohle Gasse wird er kommen'.\n\n"
            "WICHTIG fuer 'name': Verwende den EXAKTEN Wortlaut des Users oder der Anweisung. "
            "Kuerze nicht, optimiere nicht, interpretiere nicht."
        ),
        temperature       = get_node_config("planner").get("temperature", 0.2),
        expect_json       = True,
        max_output_tokens = get_node_config("planner").get("max_output_tokens"),
        caller            = "agent/notizen/create",
    )

    try:
        response = model_service.chat.submit_sync(chat_request)
        notiz_daten = response.parsed
    except (json.JSONDecodeError, KeyError) as fehler:
        logger.warning(f"NotizenAgent: JSON-Fehler bei create -- {fehler}")
        return {
            "status": "fehler",
            "fehler": f"Konnte Notiz-Daten nicht extrahieren: {fehler}",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "json_fehler"}],
        }

    target_name = state["parameter"].get("target", "")
    name = target_name if target_name else notiz_daten.get("name", "")
    text = notiz_daten.get("text", "")
    typ = notiz_daten.get("typ", "notiz")
    themen = notiz_daten.get("themen", [])

    if not name or not text:
        return {
            "status": "fehler",
            "fehler": "Name oder Text fehlt in der LLM-Antwort",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "unvollstaendig"}],
        }

    # Duplikat-Pruefung
    if not state["parameter"].get("skip_duplikat_check"):
        existing = NotizenRepository.find_by_stichwort(POSTGRES_URL, user_id, name)
        if existing:
            return {
                "status": "rueckfrage",
                "rueckfrage": (
                    f"Es gibt bereits eine Notiz '{name}'. "
                    f"Soll ich sie aktualisieren oder eine neue anlegen?"
                ),
                "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "duplikat"}],
            }

    zusammenfassung = _zusammenfassung_generieren(text)

    notiz_id = NotizenRepository.insert(
        postgres_url=POSTGRES_URL,
        user_id=user_id,
        name=name,
        typ=typ,
        text=text,
        zusammenfassung=zusammenfassung,
        themen=themen if themen else None,
    )

    verifiziert = _verifizieren_notiz(notiz_id, {"aktiv": True, "text_nicht_leer": True}) if notiz_id else False

    logger.info(f"NotizenAgent: Notiz '{name}' angelegt (ID {notiz_id}), verifiziert={verifiziert}")

    return {
        "ergebnis": f"Notiz '{name}' erstellt:\n{text}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "erstellt", "notiz_id": notiz_id, "verifiziert": verifiziert}],
    }


def _update(state: AgentState) -> dict:
    """Notiz aktualisieren -- LLM erzeugt neue Version.

    Wird auch fuer add_content und remove_content verwendet.
    """
    from config import POSTGRES_URL, get_node_config
    from memory.repositories.notizen_repository import NotizenRepository
    from services.model_services import model_service, ChatRequest

    notiz = state["parameter"].get("notiz", {})
    notiz_id = notiz.get("id")
    aktueller_text = notiz.get("text", "")
    notiz_name = notiz.get("name", "")
    prompt = state["aufgabe"]
    action = state["parameter"].get("action", "update")
    normalisiert = state["parameter"].get("normalisiert", "")

    if not notiz_id:
        return {
            "status": "fehler",
            "fehler": "Keine Notiz-ID vorhanden",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
        }

    if normalisiert:
        aenderungswunsch = (
            f"NORMALISIERTE ANWEISUNG: {normalisiert}\n"
            f"ORIGINAL-PROMPT: {prompt}"
        )
    else:
        aenderungswunsch = prompt

    # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
    # _update() laeuft im NotizenAgent (sync invoke), aufgerufen entweder
    # aus dem CharacterGraph via agent_dispatch_node oder aus
    # services/pixie/dispatch.py — beide Pfade nutzen asyncio.to_thread.
    # Kein Event-Loop im aufrufenden Thread → submit_sync. expect_json
    # bleibt False — die Antwort ist der neue Notiz-Fliesstext.
    chat_request = ChatRequest(
        messages          = [{
            "role": "user",
            "content": (
                f"AKTUELLER INHALT DER NOTIZ:\n{aktueller_text}\n\n"
                f"ÄNDERUNGSWUNSCH DES NUTZERS:\n{aenderungswunsch}\n\n"
                f"NEUER VOLLSTÄNDIGER NOTIZ-TEXT:"
            ),
        }],
        system            = (
            "Du bearbeitest eine Notiz. Der Nutzer gibt dir den AKTUELLEN Inhalt "
            "und einen ÄNDERUNGSWUNSCH in natürlicher Sprache.\n\n"
            "Deine Aufgabe:\n"
            "1. Verstehe WAS der Nutzer aendern will (hinzufuegen, entfernen, umformulieren)\n"
            "2. Wende die Aenderung auf den aktuellen Inhalt an\n"
            "3. Antworte NUR mit dem VOLLSTAENDIGEN neuen Notiz-Text\n\n"
            "WICHTIG: Der Aenderungswunsch ist eine ANWEISUNG, nicht der neue Inhalt. "
            "'Setz Erdbeeren drauf' bedeutet: Erdbeeren zur bestehenden Liste HINZUFUEGEN. "
            "'Streich die Milch' bedeutet: Milch aus der bestehenden Liste ENTFERNEN.\n"
            "Gib NIEMALS den Aenderungswunsch woertlich als Notiz-Text zurueck.\n\n"
            "Keine Erklaerungen, kein Markdown -- nur der reine Inhalt."
        ),
        temperature       = get_node_config("planner").get("temperature", 0.2),
        max_output_tokens = get_node_config("planner").get("max_output_tokens"),
        caller            = f"agent/notizen/{action}",
    )
    response = model_service.chat.submit_sync(chat_request)

    neuer_text = response.text.strip()
    zusammenfassung = _zusammenfassung_generieren(neuer_text)

    NotizenRepository.update(
        postgres_url=POSTGRES_URL,
        notiz_id=notiz_id,
        text=neuer_text,
        zusammenfassung=zusammenfassung,
    )

    verifiziert = _verifizieren_notiz(notiz_id, {"aktiv": True, "text_nicht_leer": True})

    logger.info(f"NotizenAgent: Notiz '{notiz_name}' (ID {notiz_id}) {action}, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Notiz '{notiz_name}' aktualisiert:\n{neuer_text}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": action, "verifiziert": verifiziert}],
    }


def _delete(state: AgentState) -> dict:
    """Notiz archivieren (Soft-Delete)."""
    from tools.db_manager import db_manager

    notiz = state["parameter"].get("notiz", {})
    notiz_id = notiz.get("id")
    notiz_name = notiz.get("name", "")

    if not notiz_id:
        return {
            "status": "fehler",
            "fehler": "Keine Notiz-ID vorhanden",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
        }

    db_manager.execute(
        "UPDATE notizen SET aktiv = FALSE, status = 'archiviert', updated_at = NOW() WHERE id = %s",
        (notiz_id,)
    )

    verifiziert = _verifizieren_notiz(notiz_id, {"aktiv": False})

    logger.info(f"NotizenAgent: Notiz '{notiz_name}' (ID {notiz_id}) archiviert, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Notiz '{notiz_name}' geloescht",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "archiviert", "verifiziert": verifiziert}],
    }


def _append(state: AgentState) -> dict:
    """Text an bestehende Notiz anhaengen."""
    from config import POSTGRES_URL
    from memory.repositories.notizen_repository import NotizenRepository

    notiz = state["parameter"].get("notiz", {})
    notiz_id = notiz.get("id")
    notiz_name = notiz.get("name", "")
    aktueller_text = notiz.get("text", "")
    prompt = state["aufgabe"]

    if not notiz_id:
        return {
            "status": "fehler",
            "fehler": "Keine Notiz-ID vorhanden",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
        }

    kombiniert = aktueller_text + "\n" + prompt
    zusammenfassung = _zusammenfassung_generieren(kombiniert)

    NotizenRepository.update(
        postgres_url=POSTGRES_URL,
        notiz_id=notiz_id,
        text=kombiniert,
        zusammenfassung=zusammenfassung,
    )

    verifiziert = _verifizieren_notiz(notiz_id, {"aktiv": True, "text_nicht_leer": True})

    logger.info(f"NotizenAgent: Notiz '{notiz_name}' (ID {notiz_id}) ergaenzt, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Text an '{notiz_name}' angehaengt:\n{kombiniert}",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "angehaengt", "verifiziert": verifiziert}],
    }


def _clear_content(state: AgentState) -> dict:
    """Alle Inhalte einer Notiz leeren (deterministisch, kein LLM-Call).

    Die Notiz bleibt bestehen, nur text und zusammenfassung werden geleert.
    """
    from config import POSTGRES_URL
    from memory.repositories.notizen_repository import NotizenRepository

    notiz = state["parameter"].get("notiz", {})
    notiz_id = notiz.get("id")
    notiz_name = notiz.get("name", "")

    if not notiz_id:
        return {
            "status": "fehler",
            "fehler": "Keine Notiz-ID vorhanden",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
        }

    NotizenRepository.update(
        postgres_url=POSTGRES_URL,
        notiz_id=notiz_id,
        text="",
        zusammenfassung="(leer)",
    )

    verifiziert = _verifizieren_notiz(notiz_id, {"aktiv": True, "text_leer": True})

    logger.info(f"NotizenAgent: Notiz '{notiz_name}' (ID {notiz_id}) geleert, verifiziert={verifiziert}")

    return {
        "ergebnis": f"Notiz '{notiz_name}' geleert.",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "geleert", "verifiziert": verifiziert}],
    }


def _rename(state: AgentState) -> dict:
    """Notiz umbenennen."""
    from tools.db_manager import db_manager

    notiz = state["parameter"].get("notiz", {})
    notiz_id = notiz.get("id")
    alter_name = notiz.get("name", "")
    neuer_name = state["parameter"].get("target", "")

    if not notiz_id:
        return {
            "status": "fehler",
            "fehler": "Keine Notiz-ID vorhanden",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "keine_id"}],
        }

    if not neuer_name:
        return {
            "status": "fehler",
            "fehler": "Kein neuer Name angegeben",
            "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "kein_name"}],
        }

    db_manager.execute(
        "UPDATE notizen SET name = %s, updated_at = NOW() WHERE id = %s",
        (neuer_name, notiz_id),
    )

    logger.info(f"NotizenAgent: Notiz '{alter_name}' → '{neuer_name}' (ID {notiz_id})")

    return {
        "ergebnis": f"Notiz umbenannt: '{alter_name}' → '{neuer_name}'",
        "status": "abgeschlossen",
        "schritte": state["schritte"] + [{"node": "ausfuehren", "ergebnis": "umbenannt"}],
    }
