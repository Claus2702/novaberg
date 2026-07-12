"""
Fakten-Manager — Speichert deklaratives Wissen (Entitäten + Fakten).
Optional: Nur aktiv wenn Salienz-Agent Fakten extrahiert hat.

Erweitert um:
- Entity Resolution (via M3 Service)
- CRUD auf bi-temporalem Schema (via M2 Repositories)
- Edge Invalidation bei Widersprüchen
- Rückfragen bei mehrdeutigen Entitäten
"""

import logging

import redis

from graph.context_entry import ContextEntry
from plugins.base import BaseManager
from services.model_services import model_service, EmbedRequest
from memory.repositories.entitaeten_repository import EntitaetenRepository
from memory.repositories.fakten_repository import FaktenRepository
from memory.services.entity_resolution import (
    EntityResolutionService,
    ResolvedEntity,
    ResolutionResult,
)

logger = logging.getLogger("ki_server.plugins.fakten")

# Schlüssel die auf Entitäts-Werte hindeuten (Wert = eigene DB-Entität)
_ENTITAETS_SCHLUESSEL: set[str] = {
    "schwester", "bruder", "mutter", "vater", "partner", "freund", "freundin",
    "tochter", "sohn", "nachbar", "onkel", "tante", "oma", "opa",
    "ehemann", "ehefrau", "kollege", "kollegin", "chef",
    "haustier",
    "wohnort", "stadt", "land", "ort", "geburtsort", "heimat", "arbeitsort",
    "planet", "satellit", "kontinent",
}

# Schlüssel → Attribut-Name (Graph-Kanten-Stil)
_ATTRIBUT_MAP: dict[str, str] = {
    "wohnort":    "WOHNT_IN",
    "arbeitsort": "ARBEITET_IN",
    "geburtsort": "GEBOREN_IN",
    "heimat":     "HEIMAT",
    "schwester":  "HAT_SCHWESTER",
    "bruder":     "HAT_BRUDER",
    "mutter":     "HAT_MUTTER",
    "vater":      "HAT_VATER",
    "partner":    "HAT_PARTNER",
    "tochter":    "HAT_TOCHTER",
    "sohn":       "HAT_SOHN",
    "nachbar":    "HAT_NACHBAR",
    "haustier":   "HAT_HAUSTIER",
    "freund":     "HAT_FREUND",
    "freundin":   "HAT_FREUNDIN",
    "ehemann":    "HAT_EHEMANN",
    "ehefrau":    "HAT_EHEFRAU",
    "kollege":    "HAT_KOLLEGE",
    "kollegin":   "HAT_KOLLEGIN",
    "chef":       "HAT_CHEF",
    "name":       "HEISST",
    "beziehung":  "IST",
    "beruf":      "ARBEITET_ALS",
    "hobby":      "HAT_HOBBY",
}

# Schlüssel → Typ der Wert-Entität
_WERT_TYP_MAP: dict[str, str] = {
    "wohnort": "ort", "stadt": "ort", "land": "ort", "ort": "ort",
    "geburtsort": "ort", "heimat": "ort", "arbeitsort": "ort",
    "schwester": "person", "bruder": "person", "mutter": "person",
    "vater": "person", "partner": "person", "nachbar": "person",
    "tochter": "person", "sohn": "person", "freund": "person",
    "freundin": "person", "ehemann": "person", "ehefrau": "person",
    "onkel": "person", "tante": "person", "oma": "person", "opa": "person",
    "kollege": "person", "kollegin": "person", "chef": "person",
    "haustier": "tier",
    "planet": "objekt", "satellit": "objekt", "kontinent": "ort",
}


# ─────────────────────────────────────────
# Hilfsfunktion
# ─────────────────────────────────────────

def _find_id_by_name(
    aufgeloest: list[ResolvedEntity],
    name:       str,
) -> int | None:
    """Sucht eine aufgelöste Entität per Name und gibt die ID zurück."""
    for entity in aufgeloest:
        if entity.name.lower() == name.lower() and entity.bekannte_id is not None:
            return entity.bekannte_id
    return None


class FaktenManager(BaseManager):

    @property
    def ziel(self) -> str:
        return "fakten"

    @property
    def immer_aktiv(self) -> bool:
        return False

    # ─────────────────────────────────────────
    # Prompt-Erweiterungen
    # ─────────────────────────────────────────
    @property
    def router_intents(self) -> list[str]:
        return ["fakten_management"]

    @property
    def router_prompt(self) -> str:
        return """
FAKTEN-ERKENNUNG:
Wenn der User explizit Fakten korrigieren, löschen oder abfragen möchte, setze:
  intent = "fakten_management"
  management_action = "update|delete|read"
  management_target = "Name der Entität oder des Fakts"

Trigger-Phrasen: "das stimmt nicht", "korrigiere", "vergiss das",
"was weißt du über", "was hast du dir gemerkt über"
"""

    # ─────────────────────────────────────────
    # Enricher-Hook
    # ─────────────────────────────────────────
    def enrich_entries(self, state: dict, postgres_url: str) -> list[ContextEntry]:
        """Liefert Fakten als strukturierte ContextEntry-Liste.

        Pro Entitaet mit mindestens einem Fakt wird ein Entry erzeugt;
        die Fakt-Zeilen der Entitaet werden als zusammengehoeriger Block
        in `inhalt` mit Newlines verkettet (gleiche Einrueckung wie zuvor:
        zwei Leerzeichen pro Fakt-Zeile).

        Mapping pro Entitaets-Block:
          quelle  = "plugin_fakt"
          subtyp  = ent["typ"] (Entity-Typ: person, ort, ...)
          inhalt  = mehrzeiliger String, pro Fakt eine Zeile
                    "  {attribut} = {wert} (seit {t_valid})"
          gewicht = 1.0
          meta    = {
              "praefix":        "Fakten/{name} ({typ})",
              "name":           Entitaets-Name,
              "typ":            Entitaets-Typ,
              "fakten_anzahl":  Anzahl der Fakt-Zeilen im Block,
          }

        Hinweis: Der FaktenManager liefert aktuell zwar Entries, der
        Enricher hat den Aufruf jedoch seit Chat 71 per `continue`
        deaktiviert (Rausch-Eintraege). Aktivierung erfordert Entfernung
        der Sperre in graph/nodes/enricher.py.
        """
        user_id: str = state.get("user_id", "")
        if not user_id:
            return []

        entries: list[ContextEntry] = []

        try:
            entitaeten: list[dict] = EntitaetenRepository.find_by_user(
                postgres_url, user_id
            )

            logger.info(
                f"FaktenManager.enrich_entries: entitaeten={len(entitaeten)}"
            )

            for ent in entitaeten:
                fakten: list[dict] = FaktenRepository.find_by_subjekt(
                    postgres_url, ent["id"]
                )
                if not fakten:
                    continue

                fakt_zeilen: list[str] = []
                for fakt in fakten:
                    t_valid: str = str(fakt.get("t_valid") or "unbekannt")
                    fakt_zeilen.append(
                        f"  {fakt['attribut']} = "
                        f"{fakt.get('objekt_wert') or fakt.get('fakt_text', '')} "
                        f"(seit {t_valid})"
                    )

                inhalt: str           = "\n".join(fakt_zeilen)
                name:   str           = ent["name"]
                typ:    str           = ent["typ"]
                fakten_anzahl: int    = len(fakt_zeilen)

                logger.info(
                    f"FaktenManager.enrich_entries: name={name}, "
                    f"fakten={fakten_anzahl}"
                )

                entry: ContextEntry = {
                    "quelle":  "plugin_fakt",
                    "subtyp":  typ,
                    "inhalt":  inhalt,
                    "gewicht": 1.0,
                    "meta": {
                        "praefix":       f"Fakten/{name} ({typ})",
                        "name":          name,
                        "typ":           typ,
                        "fakten_anzahl": fakten_anzahl,
                    },
                }
                entries.append(entry)
                logger.debug(
                    f"Fakt-Entry: name={name}, typ={typ}, fakten={fakten_anzahl}"
                )

        except Exception as fehler:
            logger.warning(f"FaktenManager enrich_entries (neu) fehlgeschlagen: {fehler}")

        logger.info(
            f"FaktenManager.enrich_entries: {len(entries)} Eintraege geliefert"
        )
        return entries

    # ─────────────────────────────────────────
    # Salienz → M2 Transformation
    # ─────────────────────────────────────────
    def _salienz_facts_transformieren(
        self,
        facts: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """
        Transformiert Salienz-Rohfakten (subjekt/schluessel/wert/typ)
        in M2-Format (entitaeten + fakten) für fakten_verarbeiten().

        Salienz liefert ein agnostisches Format — die Fachabteilung baut
        sich daraus das Datenpaket, das sie braucht.
        """
        entitaeten_map: dict[str, str] = {}   # name → typ (dedupliziert)
        fakten_liste:   list[dict]     = []

        for f in facts:
            subjekt:    str = f.get("subjekt", "").strip()
            schluessel: str = f.get("schluessel", "").strip()
            wert:       str = f.get("wert", "").strip()
            typ:        str = f.get("typ", "sonstiges")

            if not subjekt or not schluessel or not wert:
                continue

            # ── Subjekt → Entität ──────
            if subjekt not in entitaeten_map:
                subj_typ: str = "user" if subjekt == "ICH" else typ
                entitaeten_map[subjekt] = subj_typ

            # ── Attribut normalisieren ──────
            attribut: str = _ATTRIBUT_MAP.get(
                schluessel.lower(), schluessel.upper()
            )

            # ── Wert: Entität oder Skalar? ──────
            schluessel_lower: str  = schluessel.lower()
            ist_entitaet:     bool = schluessel_lower in _ENTITAETS_SCHLUESSEL

            if ist_entitaet:
                wert_typ: str = _WERT_TYP_MAP.get(schluessel_lower, "sonstiges")

                if wert not in entitaeten_map:
                    entitaeten_map[wert] = wert_typ

                fakten_liste.append({
                    "subjekt":     subjekt,
                    "attribut":    attribut,
                    "objekt":      wert,
                    "objekt_wert": None,
                    "fakt_text":   f"{subjekt} {attribut} {wert}",
                })
            else:
                fakten_liste.append({
                    "subjekt":     subjekt,
                    "attribut":    attribut,
                    "objekt":      None,
                    "objekt_wert": wert,
                    "fakt_text":   f"{subjekt} {attribut} {wert}",
                })

        entitaeten: list[dict] = [
            {"name": name, "typ": typ}
            for name, typ in entitaeten_map.items()
        ]

        logger.info(
            f"FaktenManager: Salienz→M2 — "
            f"{len(entitaeten)} Entitäten, {len(fakten_liste)} Fakten"
        )

        return entitaeten, fakten_liste

    # ─────────────────────────────────────────
    # Ausführung
    # ─────────────────────────────────────────
    def execute(
        self,
        writes:        list[dict],
        user_id:       str,
        redis_client:  redis.Redis,
        postgres_url:  str,
    ) -> int:
        """
        Verarbeitet pending_writes für Fakten.
        Unterstützt altes Format (facts aus Salienz) und neues M2-Format.
        """
        verarbeitet: int = 0

        for write in writes:
            aktion: str  = write.get("aktion", "")
            daten:  dict = write.get("daten", {})

            # ── Neuer M2-Pfad: entitaeten + fakten vorhanden ──────
            if "entitaeten" in daten and "fakten" in daten:
                ergebnis: dict = self.fakten_verarbeiten(
                    aktion=aktion,
                    entitaeten=daten["entitaeten"],
                    fakten=daten["fakten"],
                    user_id=user_id,
                    postgres_url=postgres_url,
                    redis_client=redis_client,
                    turn_id=daten.get("turn_id"),
                )
                if ergebnis.get("erfolg"):
                    verarbeitet += 1
                logger.info(
                    f"FaktenManager M2: {ergebnis.get('aktion', '')} "
                    f"— {ergebnis.get('details', '')}"
                )
                continue

            # ── Salienz-Rohfakten → M2 transformieren ──────
            if "facts" in daten:
                entitaeten, fakten = self._salienz_facts_transformieren(
                    daten["facts"]
                )

                if entitaeten and fakten:
                    ergebnis = self.fakten_verarbeiten(
                        aktion       = aktion,
                        entitaeten   = entitaeten,
                        fakten       = fakten,
                        user_id      = user_id,
                        postgres_url = postgres_url,
                        redis_client = redis_client,
                    )

                    if ergebnis.get("erfolg"):
                        verarbeitet += 1

                    logger.info(
                        f"FaktenManager Salienz→M2: {ergebnis.get('aktion', '')} "
                        f"— {ergebnis.get('details', '')}"
                    )
                else:
                    logger.warning(
                        f"FaktenManager: Salienz-Facts konnten nicht "
                        f"transformiert werden — {len(daten['facts'])} Rohfakten"
                    )

                continue

            # ── Query-Aktion ──────
            if aktion == "query":
                self.fakten_abfragen(
                    entitaet_name=daten.get("entitaet", ""),
                    attribut=daten.get("attribut"),
                    postgres_url=postgres_url,
                    user_id=user_id,
                    redis_client=redis_client,
                    turn_id=daten.get("turn_id"),
                )
                verarbeitet += 1
                continue

            # ── Delete-Aktion (Invalidierung) ──────
            if aktion == "delete":
                fakt_id: int | None = daten.get("fakt_id")
                if fakt_id:
                    FaktenRepository.invalidate(postgres_url, fakt_id)
                    logger.info(f"FaktenManager: Fakt {fakt_id} invalidiert")
                    verarbeitet += 1
                continue

            # Alte Salienz-Daten ohne M2-Struktur → ignorieren
            # (altes Schema existiert nicht mehr)

        return verarbeitet

    # ─────────────────────────────────────────
    # M2: Fakten verarbeiten (create/update)
    # ─────────────────────────────────────────
    def fakten_verarbeiten(
        self,
        aktion:         str,
        entitaeten:     list[dict],
        fakten:         list[dict],
        user_id:        str,
        postgres_url:   str,
        redis_client:   "redis.Redis",
        turn_id:        str | None = None,
    ) -> dict:
        """
        Verarbeitet Fakten aus der Promotion-Klassifikation.

        Returns:
            dict mit erfolg, aktion, details, braucht_klärung, klärungsfrage, agent_state
        """
        # ── 1. Entity Resolution ──────
        resolution: ResolutionResult = EntityResolutionService.resolve_batch(
            entitaeten=entitaeten,
            postgres_url=postgres_url,
            user_id=user_id,
            redis_client=redis_client,
            turn_id=turn_id,
        )

        # Bei Klärungsbedarf → Rückfrage, kein CRUD
        if resolution.braucht_klärung:
            return {
                "erfolg": False,
                "aktion": "klärung",
                "details": "",
                "braucht_klärung": True,
                "klärungsfrage": " ".join(resolution.klärungsfragen),
                "agent_state": {
                    "aktiver_agent": "fakten",
                    "aktion": aktion,
                    "aufgeloeste_entitaeten": {
                        e.name: {"id": e.bekannte_id, "name": e.name, "typ": e.typ}
                        for e in resolution.aufgeloest
                        if e.bekannte_id is not None
                    },
                    "kandidaten": {
                        e.name: e.kandidaten
                        for e in resolution.aufgeloest
                        if e.braucht_klärung
                    },
                    "fakten": fakten,
                },
            }

        # ── 2. Neue Entitäten anlegen ──────
        for entity in resolution.aufgeloest:
            if entity.ist_neu and entity.ist_referenz:
                neue_id: int = EntityResolutionService.create_new_entity(
                    postgres_url=postgres_url,
                    user_id=user_id,
                    name=entity.name,
                    typ=entity.typ,
                )
                entity.bekannte_id = neue_id
                entity.ist_neu = False

        # ── 3. Agent-State aktualisieren ──────
        if turn_id:
            EntityResolutionService.update_agent_state(
                redis_client=redis_client,
                user_id=user_id,
                turn_id=turn_id,
                resolved=resolution.aufgeloest,
            )

        # ── 4. Fakten verarbeiten ──────
        ergebnisse: list[str] = []

        for fakt in fakten:
            subjekt_name: str       = fakt.get("subjekt", "")
            attribut:     str       = fakt.get("attribut", "")
            objekt_name:  str       = fakt.get("objekt", "")
            objekt_wert:  str | None = fakt.get("objekt_wert")
            fakt_text:    str       = fakt.get("fakt_text", "")

            # Subjekt-ID auflösen
            subjekt_id: int | None = _find_id_by_name(
                resolution.aufgeloest, subjekt_name
            )
            if subjekt_id is None:
                logger.warning(
                    f"FaktenManager: Subjekt '{subjekt_name}' nicht aufgelöst"
                )
                continue

            # Objekt-ID auflösen (nur bei Entitäts-Referenz)
            objekt_id: int | None = None
            if objekt_name and not objekt_wert:
                objekt_id = _find_id_by_name(
                    resolution.aufgeloest, objekt_name
                )
                if objekt_id is None:
                    # Objekt nicht aufgelöst → als Wert behandeln
                    objekt_wert = objekt_name

            # ── Edge Invalidation Check ──────
            existing: dict | None = FaktenRepository.find_aktiv(
                postgres_url, subjekt_id, attribut
            )

            if existing:
                alter_wert: str = (
                    existing.get("objekt_wert")
                    or str(existing.get("objekt_id", ""))
                )
                neuer_wert: str = objekt_wert or str(objekt_id or "")

                if alter_wert != neuer_wert:
                    # Widerspruch → alten Fakt invalidieren
                    FaktenRepository.invalidate(postgres_url, existing["id"])
                    logger.info(
                        f"FaktenManager: Fakt invalidiert (id={existing['id']}, "
                        f"'{attribut}': '{alter_wert}' → '{neuer_wert}')"
                    )
                    ergebnisse.append(f"{attribut} aktualisiert: {fakt_text}")
                else:
                    # Gleicher Wert → nur last_touched wurde aktualisiert (via find_aktiv)
                    logger.info(
                        f"FaktenManager: Fakt bestätigt (id={existing['id']})"
                    )
                    ergebnisse.append(f"{attribut} bestätigt")
                    continue  # Kein neuer INSERT nötig

            else:
                ergebnisse.append(f"Neuer Fakt: {fakt_text}")

            # ── Embedding erzeugen ──────
            embedding: list[float] | None = None
            if fakt_text:
                try:
                    request = EmbedRequest(text=FaktenRepository.embed_text_bauen(fakt_text))
                    embed_response = model_service.embed.submit_sync(request)
                    embedding = embed_response.embedding
                    logger.debug(
                        "FaktenManager: Fakt Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                        len(embedding),
                        embed_response.duration_seconds,
                    )
                except Exception as fehler:
                    logger.warning(f"Fakt-Embedding fehlgeschlagen: {fehler}")

            # ── INSERT neuer Fakt ──────
            FaktenRepository.insert(
                postgres_url=postgres_url,
                user_id=user_id,
                subjekt_id=subjekt_id,
                attribut=attribut,
                fakt_text=fakt_text,
                objekt_id=objekt_id,
                objekt_wert=objekt_wert,
                embedding=embedding,
            )

        return {
            "erfolg": True,
            "aktion": aktion,
            "details": "; ".join(ergebnisse),
            "braucht_klärung": False,
            "klärungsfrage": "",
            "agent_state": None,
        }

    # ─────────────────────────────────────────
    # M2: Fakten abfragen (SELECT)
    # ─────────────────────────────────────────
    def fakten_abfragen(
        self,
        entitaet_name:  str,
        attribut:       str | None,
        postgres_url:   str,
        user_id:        str,
        redis_client:   "redis.Redis",
        turn_id:        str | None = None,
    ) -> dict:
        """
        Fragt Fakten zu einer Entität ab.

        Returns:
            dict mit erfolg, fakten, braucht_klärung, klärungsfrage
        """
        resolved: ResolvedEntity = EntityResolutionService.resolve_single(
            name=entitaet_name, typ="sonstiges",
            postgres_url=postgres_url, user_id=user_id,
            redis_client=redis_client, turn_id=turn_id,
        )

        if resolved.braucht_klärung:
            return {
                "erfolg": False,
                "fakten": [],
                "braucht_klärung": True,
                "klärungsfrage": resolved.klärungsfrage,
            }

        if resolved.bekannte_id is None:
            return {
                "erfolg": False,
                "fakten": [],
                "braucht_klärung": False,
                "klärungsfrage": "",
            }

        if attribut:
            fakt: dict | None = FaktenRepository.find_aktiv(
                postgres_url, resolved.bekannte_id, attribut
            )
            gefundene_fakten: list[dict] = [fakt] if fakt else []
        else:
            gefundene_fakten = FaktenRepository.find_by_subjekt(
                postgres_url, resolved.bekannte_id
            )

        return {
            "erfolg": True,
            "fakten": gefundene_fakten,
            "braucht_klärung": False,
            "klärungsfrage": "",
        }

    # ─────────────────────────────────────────
    # M2: Fakten-Historie abfragen
    # ─────────────────────────────────────────
    def fakten_historie(
        self,
        entitaet_name:  str,
        attribut:       str,
        postgres_url:   str,
        user_id:        str,
        redis_client:   "redis.Redis",
        turn_id:        str | None = None,
    ) -> dict:
        """
        Fragt die Historie eines Fakts ab (aktive + inaktive).
        "Wo hat Michael früher gewohnt?"

        Returns:
            dict mit erfolg, historie, braucht_klärung, klärungsfrage
        """
        resolved: ResolvedEntity = EntityResolutionService.resolve_single(
            name=entitaet_name, typ="sonstiges",
            postgres_url=postgres_url, user_id=user_id,
            redis_client=redis_client, turn_id=turn_id,
        )

        if resolved.braucht_klärung:
            return {
                "erfolg": False,
                "historie": [],
                "braucht_klärung": True,
                "klärungsfrage": resolved.klärungsfrage,
            }

        if resolved.bekannte_id is None:
            return {
                "erfolg": False,
                "historie": [],
                "braucht_klärung": False,
                "klärungsfrage": "",
            }

        historie: list[dict] = FaktenRepository.find_historie(
            postgres_url, resolved.bekannte_id, attribut
        )

        return {
            "erfolg": True,
            "historie": historie,
            "braucht_klärung": False,
            "klärungsfrage": "",
        }
