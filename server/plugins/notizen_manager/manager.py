"""
Notizen-Manager — Snippets: Einkaufslisten, ToDos, Merkzettel, Entwürfe.
Erstes echtes Plugin: Zeigt das volle Potenzial des Plugin-Systems.

Das LLM versteht den Inhalt, die DB speichert nur Text.
"Streich die Milch von der Einkaufsliste" → LLM erzeugt neue Version → UPDATE.

Erweitert um:
- Stichwort-basierte Suche + semantische Zusammenfassung + Themenliste
- Volltextsuche über Stichwort und Zusammenfassung
- Entity Resolution für referenzierte Entitäten
- Wiedervorlage für inaktive Notizen
- Soft-Delete statt Löschung
"""

import json
import logging
from dataclasses import dataclass

import psycopg2
import redis

from config import get_node_config
from graph.context_entry import ContextEntry
from memory.repositories.notizen_repository import NotizenRepository
from plugins.base import BaseManager
from services.model_services import ChatRequest, model_service

logger = logging.getLogger("ki_server.plugins.notizen")

# Aktionen, die unveraendert an den M6-Pfad gehen. Als Menge, weil die
# Zugehoerigkeit gefragt wird und nicht die Reihenfolge.
_M6_AKTIONEN: frozenset[str] = frozenset({"create", "append", "query"})


@dataclass(frozen=True)
class Zugang:
    """Die drei Verbindungswerte, die jeder Schreibpfad braucht.

    Zusammen uebergeben, weil sie zusammen gehoeren — ohne sie trugen die
    Unterfunktionen sechs Parameter und rissen die Argumentgrenze
    (`novaberg-lesson_l_klassen-statt-flache-keys.md`).
    """

    user_id:      str
    postgres_url: str
    redis_client: redis.Redis


# ─────────────────────────────────────────
# Hilfsfunktion
# ─────────────────────────────────────────

def _zusammenfassung_generieren(text: str, max_woerter: int = 20) -> str:
    """
    Generiert eine kurze Zusammenfassung des Notiz-Textes.
    Einfache Heuristik: erste N Wörter.
    Kann später durch LLM-Call ersetzt werden.
    """
    woerter: list[str] = text.split()
    if len(woerter) <= max_woerter:
        return text
    return " ".join(woerter[:max_woerter]) + "..."


class NotizenManager(BaseManager):

    @property
    def ziel(self) -> str:
        return "notizen"

    @property
    def immer_aktiv(self) -> bool:
        return False

    # ─────────────────────────────────────────
    # Prompt-Erweiterungen
    # ─────────────────────────────────────────
    @property
    def router_intents(self) -> list[str]:
        return ["notizen_management"]

    @property
    def router_prompt(self) -> str:
        return """
NOTIZEN-ERKENNUNG:
Setze management_action = "agent" wenn:
1. Der User eine Notiz, Liste, Einkaufsliste, ToDo oder Merkzettel
   verwalten moechte (erstellen, bearbeiten, loeschen, abfragen)
2. ODER der Gespraechsverlauf eine aktive Notiz/Liste enthaelt
   und der aktuelle Prompt eine AENDERUNG an dieser Notiz ausdrueckt
   (z.B. "Wir brauchen auch Erdbeeren" = Ergaenzung,
    "Streich die Milch" = Loeschung).
   Blosse Erwaehnung eines Themas, das zufaellig auch in einer
   Notiz steht, ist KEIN Dispatch.

Bei Erkennung:
  management_action = "agent"
  management_target = "notizen"
  management_target_typ = ""

BEISPIELE (alle → management_action = "agent"):
- "Schreib auf: Milch, Eier, Butter"
- "Was steht auf meiner Einkaufsliste?"
- "Streich die Milch von der Liste"
- "Merk dir, dass ich morgen Mehl brauche"
"""

    @property
    def salienz_prompt(self) -> str:
        return """
NOTIZ-ERKENNUNG:
Wenn der User eine Aufzählung, Liste oder strukturierte Sammlung nennt,
die als Notiz festgehalten werden sollte, extrahiere:
"snippet": {
    "name": "Kurzer Name der Notiz",
    "typ": "einkauf|todo|merkliste|notiz|entwurf|idee",
    "text": "Der vollständige Inhalt"
}
Falls keine Notiz erkennbar: "snippet": null
"""

    # ─────────────────────────────────────────
    # Enricher-Hook
    # ─────────────────────────────────────────
    def enrich_entries(self, state: dict, postgres_url: str) -> list[ContextEntry]:
        """Liefert Notizen-Kontext als strukturierte ContextEntry-Liste.

        Zwei Zweige:
          - Gezielt (intent == "notizen_management" und management_target gesetzt):
              Eine Notiz wird per Stichwort, Volltext oder direktem SQL-Fallback
              gesucht und als ein Entry mit subtyp="management" geliefert.
          - Proaktiv (sonst):
              Alle aktiven Notizen des Nutzers werden geladen; pro Notiz
              ein Entry mit subtyp="proaktiv".

        Mapping pro Entry:
          quelle  = "plugin_notiz"
          subtyp  = "management" | "proaktiv"
          inhalt  = (gezielt) Volltext der Notiz; (proaktiv) "{name}" + optional
                    ": {zusammenfassung}" + optional " (Themen: {themen_str})"
          gewicht = 1.0
          meta    = {
              "praefix": "Notiz/{name} ({typ})" | "Notiz",
              "name":             Notiz-Name,
              "typ":              Notiz-Typ (gezielt) — fehlt im proaktiven Pfad,
              "zusammenfassung":  Kurzfassung (proaktiv),
              "themen":           Themen-String (proaktiv, nur wenn nicht leer),
          }
        """
        user_id: str = state.get("user_id", "")
        if not user_id:
            return []

        external = state.get("external")
        intent:            str               = external.emotion.intent if external else ""
        management_target: str               = state.get("management_target", "")
        entries:           list[ContextEntry] = []

        logger.info(
            f"NotizenManager.enrich_entries: intent={intent}, target={management_target}"
        )

        # Gezielt eine Notiz laden (für Management-Intents)
        if intent == "notizen_management" and management_target:
            row: dict | None = None
            quelle_branch:   str = ""

            try:
                treffer: list[dict] = NotizenRepository.find_by_stichwort(
                    postgres_url, user_id, management_target
                )
                if treffer:
                    row = treffer[0]
                    quelle_branch = "stichwort"
                else:
                    # Fallback: Volltextsuche
                    treffer = NotizenRepository.find_by_volltext(
                        postgres_url, user_id, management_target
                    )
                    if treffer:
                        row = treffer[0]
                        quelle_branch = "volltext"

            except Exception as fehler:
                logger.warning(f"Notizen-Enricher (gezielt) fehlgeschlagen: {fehler}")

            # Alter Fallback: direkte DB-Abfrage
            if row is None:
                try:
                    conn = psycopg2.connect(postgres_url)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT name, typ, text FROM notizen
                        WHERE user_id = %s AND LOWER(name) ILIKE LOWER(%s)
                          AND status = 'aktiv'
                        ORDER BY updated_at DESC
                        LIMIT 1
                    """, (user_id, f"%{management_target}%"))
                    raw = cursor.fetchone()
                    conn.close()
                    if raw:
                        row = {"name": raw[0], "typ": raw[1], "text": raw[2]}
                        quelle_branch = "sql_fallback"
                except Exception as fehler:
                    logger.exception(
                        f"{type(fehler).__name__}: Notizen-Enricher Fallback fehlgeschlagen"
                    )

            if row:
                name:   str = row["name"]
                typ:    str = row["typ"]
                inhalt: str = row["text"]
                entry: ContextEntry = {
                    "quelle":  "plugin_notiz",
                    "subtyp":  "management",
                    "inhalt":  inhalt,
                    "gewicht": 1.0,
                    "meta": {
                        "praefix": f"Notiz/{name} ({typ})",
                        "name":    name,
                        "typ":     typ,
                    },
                }
                entries.append(entry)
                logger.info(
                    f"NotizenManager.enrich_entries: gezielt ({quelle_branch}) — 1 Treffer"
                )
                logger.debug(
                    f"Notiz-Entry: subtyp=management, name={name}, "
                    f"inhalt-snippet={inhalt[:60]}"
                )
            else:
                logger.info("NotizenManager.enrich_entries: gezielt — kein Treffer")

            logger.info(
                f"NotizenManager.enrich_entries: {len(entries)} Eintraege geliefert"
            )
            return entries

        # Proaktiv: alle aktiven Notizen (nur Stichwort + Zusammenfassung)
        try:
            notizen: list[dict] = NotizenRepository.find_by_user(
                postgres_url, user_id
            )

            logger.info(
                f"NotizenManager.enrich_entries: proaktiv — {len(notizen)} Notiz(en)"
            )

            for n in notizen:
                name:            str       = n["name"]
                zusammenfassung: str       = n.get("zusammenfassung") or ""
                themen:          list[str] = n.get("themen") or []
                themen_str:      str       = ", ".join(themen) if themen else ""

                inhalt: str = name
                if zusammenfassung:
                    inhalt += f": {zusammenfassung}"
                if themen_str:
                    inhalt += f" (Themen: {themen_str})"

                meta: dict = {
                    "praefix":         "Notiz",
                    "name":            name,
                    "zusammenfassung": zusammenfassung,
                }
                if themen_str:
                    meta["themen"] = themen_str

                entry: ContextEntry = {
                    "quelle":  "plugin_notiz",
                    "subtyp":  "proaktiv",
                    "inhalt":  inhalt,
                    "gewicht": 1.0,
                    "meta":    meta,
                }
                entries.append(entry)
                logger.debug(
                    f"Notiz-Entry: subtyp=proaktiv, name={name}, "
                    f"inhalt-snippet={inhalt[:60]}"
                )

        except Exception as fehler:
            logger.warning(f"Notizen-Enricher (proaktiv) fehlgeschlagen: {fehler}")

        logger.info(
            f"NotizenManager.enrich_entries: {len(entries)} Eintraege geliefert"
        )
        return entries

    # ─────────────────────────────────────────
    # Planner-Hook
    # ─────────────────────────────────────────
    def plan(
        self,
        state:        dict,
        postgres_url: str
    ) -> dict:
        """
        Plant Notiz-Operationen.
        Bei update: LLM erzeugt die neue Version, pending_write wird angelegt.
        Bei create: Daten aus dem State extrahieren.
        """
        action:  str = state.get("management_action", "")
        target:  str = state.get("management_target", "")
        user_id: str = state.get("user_id", "")
        prompt:  str = state.get("user_prompt", "")

        pending:    list = []
        result:     str  = ""
        detail:     str  = ""

        if action == "create":
            # LLM extrahiert Name, Typ und Inhalt
            # ── LLM-Call via ChatWorker (Microservice-Welle Block 2 Phase 4, G3) ──
            # plan() laeuft im CharacterGraph-planner-Node, der seinerseits
            # in event_consumer.py via asyncio.to_thread(_graph_streamen, ...)
            # laeuft. Kein Event-Loop im aufrufenden Thread → submit_sync.
            chat_request = ChatRequest(
                messages          = [{"role": "user", "content": prompt}],
                system            = (
                    "Extrahiere aus dem folgenden Text eine Notiz. "
                    "Antworte NUR mit JSON: "
                    '{"name": "Kurzname", "typ": "einkauf|todo|merkliste|notiz|entwurf|idee", '
                    '"text": "Vollständiger Inhalt", '
                    '"themen": ["thema1", "thema2"]}'
                ),
                temperature       = get_node_config("planner").get("temperature", 0.2),
                expect_json       = True,
                max_output_tokens = get_node_config("planner").get("max_output_tokens"),
                caller            = "planner/notizen",
            )

            try:
                response = model_service.chat.submit_sync(chat_request)
                notiz: dict = response.parsed
                pending.append({
                    "ziel":         "notizen",
                    "aktion":       "create",
                    "daten":        notiz,
                    "beschreibung": f"Notiz erstellen: {notiz.get('name', '')}",
                })
                result = f"Notiz '{notiz.get('name', '')}' wird erstellt"
                detail = notiz.get("text", "")
            except (json.JSONDecodeError, KeyError) as fehler:
                logger.warning(f"Notizen-Planner: JSON-Fehler bei create — {fehler}")

        elif action == "update":
            # Bestehende Notiz aus memory_context
            kontext: str = state.get("memory_context", "")

            if not kontext:
                result = f"Notiz '{target}' nicht gefunden"
            else:
                # LLM erzeugt die aktualisierte Version
                # ── LLM-Call via ChatWorker (G3) — gleicher Kontext wie create-Pfad
                # oben (CharacterGraph-planner-Node, sync to_thread). expect_json
                # bleibt False — die Antwort ist der neue Notiz-Fliesstext.
                chat_request = ChatRequest(
                    messages          = [
                        {"role": "user", "content": (
                            f"Aktuelle Notiz:\n{kontext}\n\n"
                            f"Änderungswunsch: {prompt}\n\n"
                            f"Neuer Notiz-Inhalt:"
                        )},
                    ],
                    system            = (
                        "Du bearbeitest eine Notiz. Führe die gewünschte Änderung durch. "
                        "Antworte NUR mit dem neuen, vollständigen Notiz-Text. "
                        "Keine Erklärungen, kein Markdown — nur der reine Inhalt."
                    ),
                    temperature       = get_node_config("planner").get("temperature", 0.2),
                    max_output_tokens = get_node_config("planner").get("max_output_tokens"),
                    caller            = "planner/notizen",
                )
                response = model_service.chat.submit_sync(chat_request)

                neuer_text: str = response.text.strip()
                pending.append({
                    "ziel":         "notizen",
                    "aktion":       "update",
                    "daten":        {"target": target, "text": neuer_text},
                    "beschreibung": f"Notiz aktualisieren: {target}",
                })
                result = f"Notiz '{target}' wird aktualisiert"
                detail = neuer_text

        elif action == "append":
            pending.append({
                "ziel":         "notizen",
                "aktion":       "append",
                "daten":        {"name": target, "text": prompt},
                "beschreibung": f"Notiz erweitern: {target}",
            })
            result = f"Notiz '{target}' wird ergänzt"

        elif action == "delete":
            pending.append({
                "ziel":         "notizen",
                "aktion":       "delete",
                "daten":        {"target": target},
                "beschreibung": f"Notiz löschen: {target}",
            })
            result = f"Notiz '{target}' wird gelöscht"

        elif action == "read":
            result = "Notiz-Daten geladen"
            detail = state.get("memory_context", "")

        return {
            "pending_writes":    pending,
            "management_result": result,
            "management_detail": detail,
        }

    # ─────────────────────────────────────────
    # Ausführung
    # ─────────────────────────────────────────
    def _m6_ausfuehren(self, aktion: str, daten: dict, zugang: Zugang) -> int:
        """Fuehrt einen Auftrag ueber den M6-Pfad aus (Repository).

        Vorbedingung: `aktion` ist eine der M6-Aktionen oder "update".
        Nachbedingung: 1, wenn der Pfad Erfolg meldet, sonst 0. Das Ergebnis
        steht in jedem Fall im Log — auch ein Fehlschlag ist eine Auskunft.
        Fehlerfaelle: Keine eigenen; `notiz_verarbeiten` meldet seine selbst,
        und eine Ausnahme faengt der Aufrufer je Auftrag.

        Returns:
            1 bei Erfolg, sonst 0.
        """
        # ── Verarbeitung ────────────────────────────
        ergebnis: dict = self.notiz_verarbeiten(
            aktion       = aktion,
            daten        = daten,
            user_id      = zugang.user_id,
            postgres_url = zugang.postgres_url,
            redis_client = zugang.redis_client,
            turn_id      = daten.get("turn_id"),
        )

        # ── Ausgabe-Verifikation ────────────────────
        logger.info(
            f"NotizenManager M6: {ergebnis.get('aktion', '')} "
            f"— {ergebnis.get('details', '')}"
        )
        return 1 if ergebnis.get("erfolg") else 0

    def _update_ausfuehren(self, daten: dict, zugang: Zugang) -> int:
        """Aktualisiert eine Notiz — ueber M6 mit `notiz_id`, sonst per target.

        **Gepinnte Asymmetrie:** Der M6-Zweig zaehlt nur bei gemeldetem Erfolg,
        der alte Zweig unbedingt — `_aktualisieren` gibt nichts zurueck, es gibt
        dort nichts zu pruefen. `verarbeitet` bedeutet damit je Pfad etwas
        anderes. `tests/test_notizen_execute.py` haelt das fest; es
        gleichzuziehen ist eine Entscheidung und kein Nebeneffekt.

        Vorbedingung: `daten` traegt `notiz_id` oder `target` und `text`.
        Nachbedingung: 1 oder 0 nach der obigen Regel.
        Fehlerfaelle: Faengt der Aufrufer je Auftrag.

        Returns:
            1 oder 0.
        """
        # ── Verarbeitung ────────────────────────────
        if "notiz_id" in daten:
            return self._m6_ausfuehren("update", daten, zugang)

        # ── Ausgabe ─────────────────────────────────
        self._aktualisieren(zugang.postgres_url, zugang.user_id, daten)
        return 1

    def _delete_ausfuehren(self, daten: dict, zugang: Zugang) -> int:
        """Loescht eine Notiz — per Repository mit `notiz_id`, sonst per target.

        Vorbedingung: `daten` traegt `notiz_id` oder `target`.
        Nachbedingung: 1 — beide Zweige zaehlen, die Zaehlung stand schon
        vorher hinter der Weiche.
        Fehlerfaelle: Faengt der Aufrufer je Auftrag.

        Returns:
            1.
        """
        # ── Verarbeitung ────────────────────────────
        if "notiz_id" in daten:
            NotizenRepository.invalidate(zugang.postgres_url, daten["notiz_id"])
            logger.info(f"NotizenManager: Notiz {daten['notiz_id']} invalidiert")
        else:
            self._loeschen(zugang.postgres_url, zugang.user_id, daten)

        # ── Ausgabe ─────────────────────────────────
        return 1

    def _auftrag_ausfuehren(self, write: dict, zugang: Zugang) -> int:
        """Waehlt den Pfad fuer einen einzelnen Schreibauftrag.

        **Gepinntes Verhalten:** Eine unbekannte Aktion faellt stillschweigend
        durch — keine Zaehlung, keine Log-Zeile. Das ist der stille Uebersprung,
        den der Standard verbietet, und er wird hier nicht beiläufig behoben:
        Ein Test sichert die Stille, damit ihre Beseitigung eine Entscheidung
        ist. Der Fund gehoert in die Fundliste.

        Vorbedingung: `write` traegt `aktion` und `daten`.
        Nachbedingung: Die Zahl der verarbeiteten Auftraege dieses Satzes.
        Fehlerfaelle: Keine eigenen — der Aufrufer faengt je Auftrag.

        Returns:
            1 oder 0.
        """
        # ── Eingabe-Validierung ─────────────────────
        aktion: str  = write.get("aktion", "")
        daten:  dict = write.get("daten", {})

        # ── Verarbeitung ────────────────────────────
        if aktion in _M6_AKTIONEN:
            return self._m6_ausfuehren(aktion, daten, zugang)
        if aktion == "update":
            return self._update_ausfuehren(daten, zugang)
        if aktion == "delete":
            return self._delete_ausfuehren(daten, zugang)

        # ── Ausgabe ─────────────────────────────────
        return 0

    def execute(
        self,
        writes:        list[dict],
        user_id:       str,
        redis_client:  redis.Redis,
        postgres_url:  str,
    ) -> int:
        """Fuehrt Notiz-CRUD aus.

        Unterstuetzt den alten Pfad (direkte SQL) und den neuen M6-Pfad
        (Repository). Die Signatur ist durch `BaseManager` festgelegt.

        **Der `try` steht in der Schleife, nicht darum.** Ein gescheiterter
        Auftrag darf die folgenden nicht mitnehmen.

        Vorbedingung: `writes` ist eine Liste von Auftraegen, auch eine leere.
        Nachbedingung: Zahl der verarbeiteten Auftraege.
        Fehlerfaelle: Ein Auftrag, der wirft, wird mit Ausnahmetyp und Aktion
        gemeldet und zaehlt nicht; die uebrigen laufen weiter.

        Returns:
            Anzahl verarbeiteter Writes.
        """
        # ── Eingabe-Validierung ─────────────────────
        zugang = Zugang(
            user_id      = user_id,
            postgres_url = postgres_url,
            redis_client = redis_client,
        )

        # ── Verarbeitung ────────────────────────────
        verarbeitet: int = 0
        for write in writes:
            try:
                verarbeitet += self._auftrag_ausfuehren(write, zugang)
            except Exception as fehler:
                logger.exception(
                    f"{type(fehler).__name__}: Notizen-Manager: "
                    f"{write.get('aktion', '')} fehlgeschlagen"
                )

        # ── Ausgabe ─────────────────────────────────
        return verarbeitet

    # ─────────────────────────────────────────
    # M6: Notiz verarbeiten
    # ─────────────────────────────────────────
    def notiz_verarbeiten(
        self,
        aktion:         str,
        daten:          dict,
        user_id:        str,
        postgres_url:   str,
        redis_client:   "redis.Redis",
        turn_id:        str | None = None,
    ) -> dict:
        """
        Verarbeitet Notiz-Aktionen (create, update, delete, query, append).

        Returns:
            dict mit erfolg, aktion, details, braucht_klärung, klärungsfrage, agent_state
        """
        if aktion == "create":
            return self._notiz_create(daten, user_id, postgres_url)

        elif aktion == "append":
            return self._notiz_append(daten, user_id, postgres_url)

        elif aktion == "update":
            return self._notiz_update(daten, postgres_url)

        elif aktion == "query":
            result: dict = self.notiz_suchen(daten, user_id, postgres_url)
            return {
                "erfolg": result["erfolg"],
                "aktion": "query",
                "details": result["details"],
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        return {
            "erfolg": False,
            "aktion": aktion,
            "details": f"Unbekannte Aktion: {aktion}",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────
    def _notiz_create(
        self,
        daten:        dict,
        user_id:      str,
        postgres_url: str,
    ) -> dict:
        """Neue Notiz anlegen."""
        name:   str        = daten.get("name", "")
        text:   str        = daten.get("text", "")
        typ:    str        = daten.get("typ", "notiz")
        themen: list[str]  = daten.get("themen", [])

        # Vollständigkeits-Check
        fehlend: list[str] = []
        if not name:
            fehlend.append("Stichwort/Name der Notiz")
        if not text:
            fehlend.append("Inhalt der Notiz")

        if fehlend:
            return {
                "erfolg": False,
                "aktion": "klärung",
                "details": "",
                "braucht_klärung": True,
                "klärungsfrage": f"Mir fehlt noch: {', '.join(fehlend)}",
                "agent_state": {
                    "aktiver_agent": "notizen",
                    "aktion": "create",
                    "vorhandene_daten": daten,
                    "fehlt": fehlend,
                },
            }

        zusammenfassung: str = _zusammenfassung_generieren(text)

        # Prüfen ob Notiz mit gleichem Namen schon existiert
        existing: list[dict] = NotizenRepository.find_by_stichwort(
            postgres_url, user_id, name
        )
        if existing:
            return {
                "erfolg": False,
                "aktion": "klärung",
                "details": "",
                "braucht_klärung": True,
                "klärungsfrage": (
                    f"Es gibt bereits eine Notiz '{name}'. "
                    f"Soll ich sie aktualisieren oder eine neue anlegen?"
                ),
                "agent_state": {
                    "aktiver_agent": "notizen",
                    "aktion": "create",
                    "vorhandene_daten": daten,
                    "bestehende_notiz_id": existing[0]["id"],
                },
            }

        notiz_id: int = NotizenRepository.insert(
            postgres_url=postgres_url,
            user_id=user_id,
            name=name,
            typ=typ,
            text=text,
            zusammenfassung=zusammenfassung,
            themen=themen if themen else None,
        )

        logger.info(f"NotizenManager: Notiz '{name}' angelegt (ID {notiz_id})")

        return {
            "erfolg": True,
            "aktion": "create",
            "details": f"Notiz '{name}' angelegt",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # APPEND
    # ─────────────────────────────────────────
    def _notiz_append(
        self,
        daten:        dict,
        user_id:      str,
        postgres_url: str,
    ) -> dict:
        """Text an bestehende Notiz anhängen."""
        name:       str = daten.get("name", "")
        neuer_text: str = daten.get("text", "")

        if not name or not neuer_text:
            return {
                "erfolg": False,
                "aktion": "klärung",
                "details": "",
                "braucht_klärung": True,
                "klärungsfrage": "Welche Notiz, und was soll ich hinzufügen?",
                "agent_state": {
                    "aktiver_agent": "notizen",
                    "aktion": "append",
                },
            }

        treffer: list[dict] = NotizenRepository.find_by_stichwort(
            postgres_url, user_id, name
        )

        if len(treffer) == 0:
            return {
                "erfolg": False,
                "aktion": "append",
                "details": f"Keine Notiz mit dem Stichwort '{name}' gefunden",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        if len(treffer) > 1:
            optionen: str = ", ".join(f"'{t['name']}'" for t in treffer)
            return {
                "erfolg": False,
                "aktion": "klärung",
                "details": "",
                "braucht_klärung": True,
                "klärungsfrage": f"Ich habe mehrere Notizen: {optionen}. Welche meinst du?",
                "agent_state": {
                    "aktiver_agent": "notizen",
                    "aktion": "append",
                    "kandidaten": [
                        {"id": t["id"], "name": t["name"]}
                        for t in treffer
                    ],
                    "neuer_text": neuer_text,
                },
            }

        bestehende_notiz: dict = treffer[0]
        aktualisierter_text: str = bestehende_notiz["text"] + "\n" + neuer_text

        NotizenRepository.update(
            postgres_url=postgres_url,
            notiz_id=bestehende_notiz["id"],
            text=aktualisierter_text,
            zusammenfassung=_zusammenfassung_generieren(aktualisierter_text),
        )

        logger.info(f"NotizenManager: Notiz '{name}' ergänzt")

        return {
            "erfolg": True,
            "aktion": "append",
            "details": f"Notiz '{name}' ergänzt",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────
    def _notiz_update(
        self,
        daten:        dict,
        postgres_url: str,
    ) -> dict:
        """Notiz aktualisieren per ID."""
        notiz_id: int | None = daten.get("notiz_id")
        if not notiz_id:
            return {
                "erfolg": False,
                "aktion": "update",
                "details": "Keine Notiz-ID angegeben",
                "braucht_klärung": False,
                "klärungsfrage": "",
                "agent_state": None,
            }

        text: str | None = daten.get("text")
        zusammenfassung: str | None = None
        if text:
            zusammenfassung = _zusammenfassung_generieren(text)

        NotizenRepository.update(
            postgres_url=postgres_url,
            notiz_id=notiz_id,
            name=daten.get("name"),
            text=text,
            zusammenfassung=zusammenfassung,
            themen=daten.get("themen"),
            entitaet_ids=daten.get("entitaet_ids"),
            faellig_am=daten.get("faellig_am"),
        )

        logger.info(f"NotizenManager: Notiz {notiz_id} aktualisiert")

        return {
            "erfolg": True,
            "aktion": "update",
            "details": "Notiz aktualisiert",
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # Suche
    # ─────────────────────────────────────────
    def notiz_suchen(
        self,
        daten:        dict,
        user_id:      str,
        postgres_url: str,
    ) -> dict:
        """
        Sucht Notizen per Stichwort, Volltext oder Thema.

        Returns:
            dict mit erfolg, notizen, details
        """
        name:        str | None = daten.get("name")
        suchbegriff: str | None = daten.get("suchbegriff")
        thema:       str | None = daten.get("thema")

        treffer: list[dict] = []

        if name:
            treffer = NotizenRepository.find_by_stichwort(
                postgres_url, user_id, name
            )
        elif suchbegriff:
            treffer = NotizenRepository.find_by_volltext(
                postgres_url, user_id, suchbegriff
            )
        elif thema:
            treffer = NotizenRepository.find_by_thema(
                postgres_url, user_id, thema
            )

        return {
            "erfolg": len(treffer) > 0,
            "notizen": treffer,
            "details": (
                f"{len(treffer)} Notiz(en) gefunden"
                if treffer
                else "Keine Notizen gefunden"
            ),
        }

    # ─────────────────────────────────────────
    # Private CRUD-Methoden (alter Pfad)
    # ─────────────────────────────────────────
    def _aktualisieren(self, postgres_url: str, user_id: str, daten: dict) -> None:
        """Bestehende Notiz aktualisieren (alter Pfad, target-basiert)."""
        target: str = daten.get("target", "")
        text:   str = daten.get("text", "")

        if not target or not text:
            return

        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notizen
            SET text = %s, updated_at = NOW()
            WHERE user_id = %s AND LOWER(name) ILIKE LOWER(%s) AND status = 'aktiv'
        """, (text, user_id, f"%{target}%"))

        conn.commit()
        conn.close()
        logger.info(f"Notizen-Manager: Aktualisiert — '{target}'")

    def _loeschen(self, postgres_url: str, user_id: str, daten: dict) -> None:
        """Notiz als archiviert markieren (alter Pfad, target-basiert)."""
        target: str = daten.get("target", "")
        if not target:
            return

        conn   = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notizen
            SET status = 'archiviert', updated_at = NOW()
            WHERE user_id = %s AND LOWER(name) ILIKE LOWER(%s) AND status = 'aktiv'
        """, (user_id, f"%{target}%"))

        conn.commit()
        conn.close()
        logger.info(f"Notizen-Manager: Archiviert — '{target}'")
