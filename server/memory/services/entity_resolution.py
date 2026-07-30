"""
Entity Resolution Service — löst Entitätsnamen zu DB-Einträgen auf.
Shared Service für alle Manager (Fakten, Timeline, Notizen).

Drei Quellen in Reihenfolge:
1. Agent-State (bereits aufgelöste Entitäten aus vorherigem Turn)
2. Datenbank (Name-Match + Embedding-Similarity)
3. Rückfrage (nur wenn 1 und 2 nicht reichen)
"""

import json
import logging
from dataclasses import dataclass, field

import redis

from memory.repositories.entitaeten_repository import EntitaetenRepository
from services.model_services import model_service, EmbedRequest

logger = logging.getLogger("ki_server.memory.services.entity_resolution")

AGENT_STATE_TTL: int = 3600  # 1 Stunde


# ══════════════════════════════════════════════
# Datentypen
# ══════════════════════════════════════════════

@dataclass
class ResolvedEntity:
    """Ergebnis einer Entity Resolution."""
    name:             str
    typ:              str = "sonstiges"
    bekannte_id:      int | None = None
    ist_referenz:     bool = True
    ist_neu:          bool = False
    kandidaten:       list[dict] = field(default_factory=list)
    braucht_klärung:  bool = False
    klärungsfrage:    str = ""


@dataclass
class ResolutionResult:
    """Gesamtergebnis einer Batch-Resolution."""
    aufgeloest:        list[ResolvedEntity] = field(default_factory=list)
    braucht_klärung:   bool = False
    klärungsfragen:    list[str] = field(default_factory=list)


# ══════════════════════════════════════════════
# Service
# ══════════════════════════════════════════════

class EntityResolutionService:
    """
    Löst Entitätsnamen zu Datenbankeinträgen auf.
    Shared Service für alle Manager.

    Drei Quellen in Reihenfolge:
    1. Agent-State (bereits aufgelöste Entitäten aus vorherigem Turn)
    2. Datenbank (Name-Match + Embedding-Similarity)
    3. Rückfrage (nur wenn 1 und 2 nicht reichen)
    """

    @staticmethod
    def resolve_batch(
        entitaeten:     list[dict],
        postgres_url:   str,
        user_id:        str,
        redis_client:   "redis.Redis",
        turn_id:        str | None = None,
    ) -> ResolutionResult:
        """
        Löst eine Liste von Entitäten auf (aus Call 1 der Promotion).

        Ablauf pro Entität:
        1. ist_referenz=False → überspringen, direkt übernehmen
        2. bekannte_id gesetzt → direkt übernehmen
        3. Agent-State prüfen → bereits aufgelöst? → übernehmen
        4. DB: find_by_name (exakter Match, case-insensitive)
           - 0 Treffer → Embedding-Fallback oder neue Entität
           - 1 Treffer → aufgelöst
           - N Treffer → Disambiguierung nötig
        5. Bei Disambiguierung → Klärungsfrage formulieren
        """
        result = ResolutionResult()

        for ent in entitaeten:
            name:         str        = ent.get("name", "").strip()
            typ:          str        = ent.get("typ", "sonstiges")
            ist_referenz: bool       = ent.get("ist_referenz", True)
            bekannte_id:  int | None = ent.get("bekannte_id")

            if not name:
                continue

            # ── 0. "ICH" → User-Entität auflösen ──────
            if name.upper() == "ICH":
                user_entity: list[dict] = EntitaetenRepository.find_by_type(
                    postgres_url, user_id, "user"
                )
                if user_entity:
                    result.aufgeloest.append(ResolvedEntity(
                        name=name, typ="user",
                        bekannte_id=user_entity[0]["id"]
                    ))
                    logger.info(
                        f"Entity Resolution: 'ICH' → User-Entität "
                        f"'{user_entity[0].get('name', '')}' (ID {user_entity[0]['id']})"
                    )
                    continue
                else:
                    logger.warning("Entity Resolution: 'ICH' → keine User-Entität gefunden")

            # ── 1. Interface → überspringen ──────
            if not ist_referenz:
                result.aufgeloest.append(ResolvedEntity(
                    name=name, typ=typ, ist_referenz=False
                ))
                logger.debug(f"Entity Resolution: '{name}' → Interface, übersprungen")
                continue

            # ── 2. Bereits bekannt (Call 1 hat ID geliefert) ──────
            if bekannte_id is not None:
                result.aufgeloest.append(ResolvedEntity(
                    name=name, typ=typ, bekannte_id=bekannte_id
                ))
                logger.info(f"Entity Resolution: '{name}' → bekannte ID {bekannte_id}")
                continue

            # ── 3. Agent-State prüfen ──────
            cached: dict | None = EntityResolutionService._check_agent_state(
                redis_client, user_id, turn_id, name
            )
            if cached:
                result.aufgeloest.append(ResolvedEntity(
                    name=name, typ=typ,
                    bekannte_id=cached.get("id")
                ))
                logger.info(
                    f"Entity Resolution: '{name}' aus Agent-State"
                    f" (Turn {turn_id})"
                )
                continue

            # ── 4. DB: Name-Match ──────
            treffer: list[dict] = EntityResolutionService._search_by_name(
                postgres_url, user_id, name
            )

            if len(treffer) == 1:
                result.aufgeloest.append(ResolvedEntity(
                    name=name, typ=typ,
                    bekannte_id=treffer[0]["id"]
                ))
                logger.info(f"Entity Resolution: '{name}' → gefunden (ID {treffer[0]['id']})")
                continue

            if len(treffer) == 0:
                # ── 5. Fallback: Embedding-Similarity ──────
                # Block 1 Cleanup-Sprint: Embedding-Fallback läuft jetzt
                # immer (Worker steht zentral), Feature-Flag entkernt.
                ähnliche: list[dict] = EntityResolutionService._search_by_embedding(
                    postgres_url, user_id, name,
                )
                logger.info(
                    f"Entity Resolution: '{name}'"
                    f" → Embedding-Suche ({len(ähnliche)} Treffer)"
                )

                if len(ähnliche) == 1:
                    result.aufgeloest.append(ResolvedEntity(
                        name=name, typ=typ,
                        bekannte_id=ähnliche[0]["id"]
                    ))
                    continue
                elif len(ähnliche) > 1:
                    treffer = ähnliche
                    # Weiter zur Disambiguierung unten
                else:
                    result.aufgeloest.append(ResolvedEntity(
                        name=name, typ=typ, ist_neu=True
                    ))
                    logger.info(f"Entity Resolution: '{name}' → neue Entität")
                    continue

            # ── 6. Disambiguierung (N Treffer) ──────
            frage: str = EntityResolutionService._build_klärungsfrage(
                name, treffer
            )
            result.aufgeloest.append(ResolvedEntity(
                name=name, typ=typ,
                kandidaten=treffer,
                braucht_klärung=True,
                klärungsfrage=frage
            ))
            result.braucht_klärung = True
            result.klärungsfragen.append(frage)
            logger.info(
                f"Entity Resolution: '{name}'"
                f" → {len(treffer)} Kandidaten, Klärung nötig"
            )

        return result

    @staticmethod
    def resolve_single(
        name:           str,
        typ:            str,
        postgres_url:   str,
        user_id:        str,
        redis_client:   "redis.Redis",
        turn_id:        str | None = None,
    ) -> ResolvedEntity:
        """Löst eine einzelne Entität auf. Convenience-Wrapper um resolve_batch."""
        batch_result: ResolutionResult = EntityResolutionService.resolve_batch(
            entitaeten=[{"name": name, "typ": typ, "ist_referenz": True}],
            postgres_url=postgres_url,
            user_id=user_id,
            redis_client=redis_client,
            turn_id=turn_id,
        )
        if batch_result.aufgeloest:
            return batch_result.aufgeloest[0]
        return ResolvedEntity(name=name, typ=typ, ist_neu=True)

    # ──────────────────────────────────────────
    # Interne Helfer
    # ──────────────────────────────────────────

    @staticmethod
    def _check_agent_state(
        redis_client:  "redis.Redis",
        user_id:       str,
        turn_id:       str | None,
        name:          str,
    ) -> dict | None:
        """
        Prüft ob die Entität bereits im Agent-State aufgelöst wurde.
        Sucht in ALLEN offenen Agent-States des Users.
        """
        try:
            pattern: str = f"agent_state:{user_id}:*"
            keys: list = redis_client.keys(pattern)

            for key in keys:
                raw: bytes | None = redis_client.get(key)
                if not raw:
                    continue
                state: dict = json.loads(raw)
                aufgeloest: dict = state.get("aufgeloeste_entitaeten", {})

                for ent_name, ent_data in aufgeloest.items():
                    if ent_name.lower() == name.lower():
                        return ent_data

        except Exception as fehler:
            logger.warning(f"Agent-State-Lookup fehlgeschlagen: {fehler}")

        return None

    @staticmethod
    def _search_by_name(
        postgres_url:  str,
        user_id:       str,
        name:          str,
    ) -> list[dict]:
        """
        Sucht Entitäten per Name in der DB (case-insensitive, nur aktive).
        Nutzt EntitaetenRepository.find_by_name().
        """
        try:
            return EntitaetenRepository.find_by_name(postgres_url, user_id, name)
        except Exception as fehler:
            logger.exception(f"DB-Namenssuche fehlgeschlagen: {fehler}")
            return []

    @staticmethod
    def _name_ist_plausibel(such_name: str, treffer_name: str) -> bool:
        """
        Prüft ob zwei Namen plausibel zusammenpassen.

        Akzeptiert:
        - Exakter Match (case-insensitive)
        - Teilstring: "Anna" in "Anna-Maria"
        - Gleicher Anfangsbuchstabe + ähnliche Länge (±3)

        Verwirft:
        - Komplett verschiedene Namen: "Anna" ≠ "Max"
        """
        s: str = such_name.lower().strip()
        t: str = treffer_name.lower().strip()

        if s == t:
            return True
        if s in t or t in s:
            return True
        if s and t and s[0] == t[0] and abs(len(s) - len(t)) <= 3:
            return True

        return False

    @staticmethod
    def _search_by_embedding(
        postgres_url:   str,
        user_id:        str,
        name:           str,
        # Kalibriert auf nomic-embed-text-v2-moe (Chat 107), vorher 0.80 —
        # synchron zum find_similar-Default. ⚠ Wachposten: Suchpfad embeddet
        # nur den Namen (ENTITAET-EMBED-DREIFACH), kurze Texte nicht gemessen
        # — begruendeter Startwert, nach dem Re-Embedding messen.
        threshold:      float = 0.70,
    ) -> list[dict]:
        """
        Sucht ähnliche Entitäten per Embedding-Similarity.
        Nur als Fallback wenn find_by_name nichts liefert.
        Filtert Treffer zusätzlich per Name-Plausibilität.
        """
        try:
            # TODO ENTITAET-EMBED-DREIFACH: Der Suchpfad embeddet nur den
            # Namen, vergleicht aber gegen Vektoren aus
            # EntitaetenRepository.embed_text_bauen(name, zusammenfassung).
            # Bewusst NICHT auf die Bauer-Funktion umgestellt (Chat 107) —
            # eine Aenderung hier veraendert das Suchverhalten und gehoert
            # gemessen, nicht nebenbei gemacht.
            request = EmbedRequest(text=name)
            embed_response = model_service.embed.submit_sync(request)
            embedding: list[float] = embed_response.embedding
            logger.debug(
                "Entity-Resolution: Similarity-Suche Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )
            treffer: list[dict] = EntitaetenRepository.find_similar(
                postgres_url, user_id, embedding, threshold=threshold
            )

            # Embedding-Treffer filtern: Name muss plausibel sein
            gefiltert: list[dict] = []
            for t in treffer:
                if EntityResolutionService._name_ist_plausibel(name, t.get("name", "")):
                    gefiltert.append(t)
                else:
                    logger.info(
                        f"Entity Resolution: '{name}' → Embedding-Treffer "
                        f"'{t.get('name', '')}' verworfen (Name nicht plausibel)"
                    )

            return gefiltert
        except Exception as fehler:
            logger.warning(f"Embedding-Suche fehlgeschlagen: {fehler}")
            return []

    @staticmethod
    def _build_klärungsfrage(
        name:        str,
        kandidaten:  list[dict],
    ) -> str:
        """
        Formuliert eine natürliche Klärungsfrage.
        Nutzt die Zusammenfassung der Entitäten zur Unterscheidung.
        """
        if len(kandidaten) == 2:
            beschreibungen: list[str] = []
            for k in kandidaten:
                zusammenfassung: str = k.get("zusammenfassung", "") or ""
                if zusammenfassung:
                    beschreibungen.append(f"{k['name']} ({zusammenfassung})")
                else:
                    beschreibungen.append(f"{k['name']} (ID:{k['id']})")

            return (
                f"Ich kenne zwei Personen namens {name}: "
                f"{beschreibungen[0]} und {beschreibungen[1]}. "
                f"Welche meinst du?"
            )

        return (
            f"Ich kenne {len(kandidaten)} Einträge zu '{name}'. "
            f"Kannst du genauer beschreiben, wen oder was du meinst?"
        )

    # ──────────────────────────────────────────
    # Entität anlegen + State aktualisieren
    # ──────────────────────────────────────────

    @staticmethod
    def create_new_entity(
        postgres_url:    str,
        user_id:         str,
        name:            str,
        typ:             str = "sonstiges",
        zusammenfassung: str | None = None,
    ) -> int:
        """
        Legt eine neue Entität in der DB an.
        Erzeugt ein Embedding für Name + Zusammenfassung.

        Block 1 Cleanup-Sprint: Embedding läuft jetzt immer (Worker steht
        zentral), Feature-Flag entkernt.
        """
        embedding: list[float] | None = None

        try:
            embed_text: str = EntitaetenRepository.embed_text_bauen(name, zusammenfassung)
            request = EmbedRequest(text=embed_text)
            embed_response = model_service.embed.submit_sync(request)
            embedding = embed_response.embedding
            logger.debug(
                "Entity-Resolution: Neue Entität Embedding via EmbedWorker (Dim: %d, Dauer: %.3fs)",
                len(embedding),
                embed_response.duration_seconds,
            )
        except Exception as fehler:
            logger.warning(f"Embedding-Erzeugung fehlgeschlagen: {fehler}")

        entitaet_id: int = EntitaetenRepository.insert(
            postgres_url=postgres_url,
            user_id=user_id,
            name=name,
            typ=typ,
            zusammenfassung=zusammenfassung,
            embedding=embedding,
        )

        logger.info(
            f"Entity Resolution: '{name}'"
            f" → neue Entität wird angelegt (ID {entitaet_id})"
        )
        return entitaet_id

    @staticmethod
    def update_agent_state(
        redis_client:  "redis.Redis",
        user_id:       str,
        turn_id:       str,
        resolved:      list[ResolvedEntity],
    ) -> None:
        """
        Speichert aufgelöste Entitäten im Agent-State.
        Key: agent_state:{user_id}:{turn_id}
        TTL: 3600 Sekunden.
        """
        key: str = f"agent_state:{user_id}:{turn_id}"

        # Bestehenden State laden oder neuen anlegen
        try:
            raw: bytes | None = redis_client.get(key)
            state: dict = json.loads(raw) if raw else {}
        except Exception:
            state = {}

        aufgeloest: dict = state.get("aufgeloeste_entitaeten", {})

        for ent in resolved:
            if ent.bekannte_id is not None:
                aufgeloest[ent.name] = {
                    "id":   ent.bekannte_id,
                    "name": ent.name,
                    "typ":  ent.typ,
                }

        state["aufgeloeste_entitaeten"] = aufgeloest

        try:
            redis_client.set(key, json.dumps(state), ex=AGENT_STATE_TTL)
            logger.debug(
                f"Agent-State aktualisiert: {key}"
                f" ({len(aufgeloest)} Entitäten)"
            )
        except Exception as fehler:
            logger.warning(f"Agent-State-Update fehlgeschlagen: {fehler}")
