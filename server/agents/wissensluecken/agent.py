"""WissensluecketAgent — Themen am Rand von Novas Wissensfeld.

Vier Schritte je Lauf: Saat ziehen, per LLM erweitern, gegen Bestand und
bestehende Luecken filtern, bewerten und ablegen.

Unterscheidet sich von der GV4-Lueckensuche durch die Lebensdauer: GV4 findet,
was im laufenden Turn nebenan liegt, und vergisst es. Was hier entsteht, liegt
in einer Tabelle und traegt den Zug zu einem Thema ueber Tage.

Konzept: docs/novaberg-wissensluecken_k.md
"""

import json
import logging
import random

from agents.base import BaseAgent, AgentState, PeriodicTask
from agents.wissensluecken.berechnung import (
    STATUS_OFFEN,
    ist_dublette,
    neugier_vektor_berechnen,
    neuheit_berechnen,
)
from config import (
    ASSISTANT_USER_ID,
    DEFAULT_USER_ID,
    LUECKEN_KANDIDATEN_JE_LAUF,
    LUECKEN_PRIORITAET,
    LUECKEN_INTERVALL_SEKUNDEN,
    LUECKEN_SAAT_THEMEN,
    LUECKEN_HINWEIS_THEMEN,
    get_node_config,
)
from memory.utils import embedding_zu_pgvector_str
from services.model_services import model_service, BackgroundRequest, EmbedRequest
from tools.db_manager import db_manager

logger = logging.getLogger("ki_server.agents.wissensluecken")


ERWEITERN_PROMPT: str = """Du kennst dieses Wesen an seinen Themen.

[BEKANNTE THEMEN]
{saat}

[BEREITS ERFASST — NICHT ERNEUT NENNEN]
{hinweis}

[AUFGABE]
Nenne {anzahl} Rand- und Unterthemen, die an die bekannten Themen angrenzen,
aber selbst noch nicht darunter sind. Gehe einen Schritt weiter, nicht zehn:
Zu "Kosmologie" gehoeren "Rotverschiebung" und "Inflation", nicht
"Kryptowaehrung".

Ein Randthema liegt daneben (Himmel und Wolken -> Regen, Gartenbewaesserung),
ein Unterthema liegt darunter (Kosmologie -> Dunkle Materie).

Jedes Thema ist ein kurzer Stichpunkt, zwei bis fuenf Woerter, kein Satz.

Antworte AUSSCHLIESSLICH mit einem JSON-Array von Strings:
["Thema eins", "Thema zwei", ...]
"""


class WissensluecketAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "wissensluecken"

    @property
    def faehigkeiten(self) -> list[str]:
        return ["wissensluecken"]

    @property
    def graph_eignung(self) -> list[str]:
        return ["pixie"]

    @property
    def context_user(self) -> str:
        return "user"

    @property
    def identity_user(self) -> str:
        return ASSISTANT_USER_ID

    def periodic_task(self) -> PeriodicTask | None:
        # Prioritaet bewusst gesetzt, nicht per Default. Gemessen 27.07.2026:
        # CharakterAgent mit 0.3 kam erst dran, als das Gespraech verstummte.
        # Ein Agent, der nie laeuft, ist so gut wie keiner.
        return PeriodicTask(
            name="wissensluecken",
            priority=LUECKEN_PRIORITAET,
            interval=LUECKEN_INTERVALL_SEKUNDEN,
            description="Themen am Rand des Wissensfeldes suchen",
        )

    def build_graph(self):
        return None

    # ═══════════════════════════════════════════════════════════
    # Lauf
    # ═══════════════════════════════════════════════════════════

    def invoke(self, state: AgentState) -> AgentState:
        """Sucht Themen am Rand des Wissensfeldes und legt sie ab.

        Vorbedingung: charakter_hash traegt einen kern_hash fuer das Paar.
            Ohne ihn gibt es kein Feld, gegen das Resonanz gemessen werden
            koennte — dann bricht der Lauf laut ab.
        Nachbedingung: state["ergebnis"] nennt angelegte und aufgefrischte
            Zeilen. Jede Zeile traegt resonanz, neuheit und den daraus
            gerechneten neugier_vektor.
        Fehlerfaelle: kein Charakterkern, leere Saat, unlesbare LLM-Antwort —
            jeweils Abbruch mit error-Zeile und status="fehler".
        """

        user_id:      str = state["kontext"].get("user_id", "")      or DEFAULT_USER_ID
        character_id: str = state["kontext"].get("character_id", "") or ASSISTANT_USER_ID

        # ── Eingabe-Validierung: das Charakterfeld ──
        feld_embedding, feld_grund = self._charakterfeld(user_id, character_id)
        if feld_embedding is None:
            return self._abbruch(state, feld_grund)

        # ── Saat ziehen ─────────────────────────────
        saat: list[str] = self._saat_ziehen(user_id, character_id)
        if not saat:
            return self._abbruch(
                state,
                f"Keine bekannten Themen fuer {user_id}:{character_id} — "
                f"nichts zu erweitern.",
            )

        # ── Erweitern ───────────────────────────────
        hinweis: list[str] = self._hinweis_themen(user_id, character_id)
        kandidaten: list[str] = self._erweitern(saat, hinweis)
        if not kandidaten:
            return self._abbruch(state, "LLM lieferte keine brauchbaren Kandidaten.")

        # ── Filtern, bewerten, ablegen ──────────────
        angelegt:      int = 0
        aufgefrischt:  int = 0
        verworfen:     int = 0

        for thema in kandidaten:
            embedding: list[float] = self._embedden(thema)
            if not embedding:
                verworfen += 1
                continue

            vektor_str: str = embedding_zu_pgvector_str(embedding)

            resonanz: float = self._cosine(feld_embedding, embedding)
            neuheit:  float = neuheit_berechnen(
                self._naechster_im_bestand(user_id, character_id, vektor_str)
            )
            zug: float = neugier_vektor_berechnen(max(0.0, resonanz), neuheit)

            treffer = self._naechste_luecke(user_id, character_id, vektor_str)
            if treffer is not None and ist_dublette(treffer["cosine"]):
                # Auffrischen statt verwerfen: Die Neuheit kann seit dem
                # letzten Lauf gesunken sein, weil Nova inzwischen darueber
                # gesprochen hat — genau daran schliesst sich eine Luecke.
                db_manager.execute(
                    """
                    UPDATE wissensluecken
                       SET neuheit = %s, neugier_vektor = %s, resonanz = %s,
                           aktualisiert_am = NOW()
                     WHERE id = %s
                    """,
                    (neuheit, zug, resonanz, treffer["id"]),
                )
                aufgefrischt += 1
                continue

            # xmax = 0 heisst: eingefuegt. Sonst hat der ON-CONFLICT-Zweig
            # gefeuert. Ohne diese Unterscheidung zaehlte der Zaehler Aufrufe
            # statt Wirkungen — dieselbe Klasse wie
            # BATCH-ZAEHLER-ZAEHLEN-AUFRUFE, wo eine Summenzeile Verworfene
            # als Erfolge meldete.
            # execute_returning statt select: select committet NICHT, und die
            # Einfuegung wuerde beim Verbindungsschluss verworfen — lautlos,
            # mit einem Zaehler, der trotzdem Erfolg meldet.
            zeile = db_manager.execute_returning(
                """
                INSERT INTO wissensluecken
                    (user_id, character_id, thema, embedding,
                     resonanz, neuheit, neugier_vektor, herkunft, status)
                VALUES (%s, %s, %s, %s::vector, %s, %s, %s, 'nachbar', %s)
                ON CONFLICT (user_id, character_id, thema) DO UPDATE SET
                    resonanz        = EXCLUDED.resonanz,
                    neuheit         = EXCLUDED.neuheit,
                    neugier_vektor  = EXCLUDED.neugier_vektor,
                    aktualisiert_am = NOW()
                RETURNING (xmax = 0) AS eingefuegt
                """,
                (user_id, character_id, thema, vektor_str,
                 resonanz, neuheit, zug, STATUS_OFFEN),
            )
            if zeile is None:
                # Weder eingefuegt noch aktualisiert — das darf nicht sein.
                logger.error(
                    f"Wissensluecken: Upsert fuer '{thema}' lieferte keine "
                    f"Zeile — weder angelegt noch aufgefrischt"
                )
                verworfen += 1
            elif zeile["eingefuegt"]:
                angelegt += 1
            else:
                aufgefrischt += 1

        # ── Ausgabe-Verifikation ────────────────────
        logger.info(
            f"Wissensluecken: {angelegt} angelegt, {aufgefrischt} aufgefrischt, "
            f"{verworfen} ohne Embedding verworfen "
            f"(Paar={user_id}:{character_id}, Saat={len(saat)}, "
            f"Kandidaten={len(kandidaten)})"
        )

        state["ergebnis"] = {
            "angelegt":     angelegt,
            "aufgefrischt": aufgefrischt,
            "verworfen":    verworfen,
            "kandidaten":   len(kandidaten),
        }
        state["status"] = "abgeschlossen"
        return state

    # ═══════════════════════════════════════════════════════════
    # Bausteine
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _abbruch(state: AgentState, grund: str) -> AgentState:
        """Laut abbrechen — kein stiller Leerlauf."""
        logger.error(f"Wissensluecken: {grund}")
        state["ergebnis"] = {"angelegt": 0, "aufgefrischt": 0, "verworfen": 0}
        state["status"] = "fehler"
        state["fehler"] = grund
        return state

    def _charakterfeld(
        self, user_id: str, character_id: str,
    ) -> tuple[list[float] | None, str]:
        """Embeddet kern_hash plus aktive Charakter-Anweisung.

        Wird NICHT persistiert — der Wert entsteht je Lauf neu und wird
        verworfen. Was bleibt, sind die Luecken.

        ACHTUNG: Kern und Anweisung liegen unter VERSCHIEDENEN Schluesseln.
        Der Kern steht am Paar, die Anweisung nur an user_id — der Tabelle
        charakter_anweisungen fehlt bis heute jedes character_id.

        Nachbedingung: (embedding, "") bei Erfolg, sonst (None, grund). Der
        Grund wird MITGELIEFERT statt vom Aufrufer geraten: Ein fehlender
        Kern und ein gescheitertes Embedding sind verschiedene Lagen, und
        eine Fehlermeldung, die die falsche nennt, schickt den Leser in die
        Irre.
        """

        # ── Eingabe-Validierung ─────────────────────
        zeilen = db_manager.select(
            "SELECT kern_hash FROM charakter_hash "
            "WHERE user_id = %s AND character_id = %s",
            (user_id, character_id),
        )
        kern: str = (zeilen[0]["kern_hash"] or "").strip() if zeilen else ""
        if not kern:
            return None, (
                f"Kein Charakterkern fuer {user_id}:{character_id} — ohne Feld "
                f"keine Resonanz. Erst destillieren lassen."
            )

        anweisungen = db_manager.select(
            "SELECT anweisung FROM charakter_anweisungen "
            "WHERE user_id = %s AND aktiv = TRUE ORDER BY erstellt_am",
            (user_id,),
        )
        teile: list[str] = [kern] + [z["anweisung"] for z in (anweisungen or [])]

        # ── Verarbeitung / Ausgabe ──────────────────
        embedding: list[float] = self._embedden("\n\n".join(teile))
        if not embedding:
            return None, (
                f"Charakterkern vorhanden ({len(kern)} Zeichen), aber sein "
                f"Embedding ist gescheitert — Ursache steht in der Zeile davor. "
                f"Kein Feld, keine Resonanz."
            )
        return embedding, ""

    @staticmethod
    def _embedden(text: str) -> list[float]:
        """Ein Embedding, oder eine leere Liste plus Fehlerzeile."""
        if not text or not text.strip():
            logger.error("Wissensluecken: Embedding fuer leeren Text angefordert")
            return []
        try:
            return model_service.embed.submit_sync(EmbedRequest(text=text)).embedding
        except Exception as fehler:
            logger.error(
                f"Wissensluecken: Embedding fehlgeschlagen fuer "
                f"'{text[:60]}' — {type(fehler).__name__}: {fehler}",
                exc_info=True,
            )
            return []

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        """Cosine-Similarity zweier Vektoren gleicher Laenge."""
        if not a or not b or len(a) != len(b):
            logger.error(
                f"Wissensluecken: Cosine auf unvertraeglichen Vektoren "
                f"({len(a)} vs {len(b)}) — 0.0"
            )
            return 0.0
        punkt: float = sum(x * y for x, y in zip(a, b))
        norm_a: float = sum(x * x for x in a) ** 0.5
        norm_b: float = sum(y * y for y in b) ** 0.5
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return punkt / (norm_a * norm_b)

    @staticmethod
    def _saat_ziehen(user_id: str, character_id: str) -> list[str]:
        """Stichprobe bekannter Themen als Ausgangspunkt.

        Wechselnde Saat: Ohne sie liefe jeder Lauf ueber dieselben Themen und
        das LLM schluege dieselben Nachbarn vor.
        """
        zeilen = db_manager.select(
            "SELECT DISTINCT unnest(themen) AS thema FROM lzg_knoten "
            "WHERE user_id = %s AND character_id = %s AND aktiv = TRUE",
            (user_id, character_id),
        )
        alle: list[str] = [z["thema"] for z in (zeilen or []) if z.get("thema")]
        if len(alle) <= LUECKEN_SAAT_THEMEN:
            return alle
        return random.sample(alle, LUECKEN_SAAT_THEMEN)

    @staticmethod
    def _hinweis_themen(user_id: str, character_id: str) -> list[str]:
        """Kurzer Wink an das LLM, welche Themen schon erfasst sind.

        Nur ein Hinweis — die Garantie gegen Dubletten ist die
        Embedding-Pruefung, nicht diese Liste. Sie darf unvollstaendig sein.
        """
        zeilen = db_manager.select(
            "SELECT thema FROM wissensluecken "
            "WHERE user_id = %s AND character_id = %s "
            "ORDER BY aktualisiert_am DESC LIMIT %s",
            (user_id, character_id, LUECKEN_HINWEIS_THEMEN),
        )
        return [z["thema"] for z in (zeilen or [])]

    @staticmethod
    def _naechster_im_bestand(user_id: str, character_id: str, vektor: str) -> float:
        """Hoechste Aehnlichkeit zu dem, was sie schon weiss."""
        zeilen = db_manager.select(
            "SELECT 1 - (embedding <=> %s::vector) AS cosine FROM lzg_knoten "
            "WHERE user_id = %s AND character_id = %s AND embedding IS NOT NULL "
            "ORDER BY cosine DESC LIMIT 1",
            (vektor, user_id, character_id),
        )
        return float(zeilen[0]["cosine"]) if zeilen else 0.0

    @staticmethod
    def _naechste_luecke(user_id: str, character_id: str, vektor: str) -> dict | None:
        """Naechstliegende bestehende Luecke — unabhaengig vom Status.

        Offen, geschlossen und ausgeschlossen sperren gleichermassen: Was
        einmal erfasst ist, soll nicht ein zweites Mal angelegt werden.
        """
        zeilen = db_manager.select(
            "SELECT id, 1 - (embedding <=> %s::vector) AS cosine "
            "FROM wissensluecken "
            "WHERE user_id = %s AND character_id = %s AND embedding IS NOT NULL "
            "ORDER BY cosine DESC LIMIT 1",
            (vektor, user_id, character_id),
        )
        return zeilen[0] if zeilen else None

    @staticmethod
    def _erweitern(saat: list[str], hinweis: list[str]) -> list[str]:
        """LLM-Aufruf: Rand- und Unterthemen zur Saat.

        Der einzige Schritt, der etwas ENTDECKEN kann. Eine Vektorsuche ueber
        den eigenen Bestand liefert nur, was schon drinsteht.
        """
        node_cfg = get_node_config("wissensluecken")
        prompt: str = ERWEITERN_PROMPT.format(
            saat    = "\n".join(f"- {t}" for t in saat),
            hinweis = "\n".join(f"- {t}" for t in hinweis) or "(noch nichts)",
            anzahl  = LUECKEN_KANDIDATEN_JE_LAUF,
        )

        try:
            antwort = model_service.background.submit_sync(BackgroundRequest(
                messages          = [{"role": "user", "content": prompt}],
                modus             = "analyse",
                temperature       = node_cfg.get("temperature", 0.7),
                max_output_tokens = node_cfg.get("max_output_tokens", 1024),
                caller            = "wissensluecken/erweitern",
            ))
        except Exception as fehler:
            logger.error(
                f"Wissensluecken: Erweitern fehlgeschlagen — "
                f"{type(fehler).__name__}: {fehler}", exc_info=True,
            )
            return []

        roh: str = (antwort.text or "").strip()
        if roh.startswith("```"):
            roh = roh.split("\n", 1)[1] if "\n" in roh else roh[3:]
        if roh.endswith("```"):
            roh = roh[:-3]

        try:
            geparst = json.loads(roh.strip())
        except (json.JSONDecodeError, TypeError) as fehler:
            logger.error(
                f"Wissensluecken: Antwort ist kein JSON "
                f"({type(fehler).__name__}) — Roh: '{roh[:120]}'"
            )
            return []

        if not isinstance(geparst, list):
            logger.error(
                f"Wissensluecken: Antwort ist kein Array, sondern "
                f"{type(geparst).__name__} — verworfen"
            )
            return []

        # ── Ausgabe-Verifikation ────────────────────
        themen: list[str] = [
            t.strip() for t in geparst if isinstance(t, str) and t.strip()
        ]
        if len(themen) < len(geparst):
            logger.warning(
                f"Wissensluecken: {len(geparst) - len(themen)} Kandidaten "
                f"verworfen (leer oder kein String)"
            )
        return themen
