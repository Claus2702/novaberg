"""Objekt-Merkmal — der Vektor, an dem ein Dienst die Objekte der Lage erkennt.

**Konzept:** `docs/novaberg-thinking-lage_k.md` §4, Scheibe 12, Teil C. Jeder
Dienst am Empfang kann neben seinem Aushang (Merkmale der Aeusserung) ein
**Objekt-Merkmal** deklarieren (`BaseAgent.objekt_merkmal`): das Objekt, das er
bedient, in der Sprache der Sachlage. Die Naehe zwischen Merkmal und akutem
Objekt wird gerechnet, nicht vom Empfang erraten.

**Dieses Modul haelt nur die eine Seite der Rechnung:** je Dienst den Vektor
seines Merkmals, einmal beim Start eingebettet. Es rechnet keine Naehe und
entscheidet keine Zustellung — der Empfang liest die Vektoren heute nicht.

**Der Embed-Text ist das Merkmal selbst** (`F-EMBED-1`): aus der Deklaration
im Code rekonstruierbar, eine benannte Funktion. Nichts wird persistiert —
der Vektor ist so alt wie der Prozess, und ein geaenderter Wortlaut gilt ab
dem naechsten Start.
"""

import asyncio
import logging
import math
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

logger = logging.getLogger("ki_server.agents.object_feature")

_EMBED_DEADLINE_S: float = 60.0


@dataclass(frozen=True)
class FeatureVector:
    """Der eingebettete Merkmalstext eines Dienstes."""

    service: str
    text: str
    vector: tuple[float, ...]


# Der Bestand dieses Prozesses. Geschrieben nur von `feature_vectors_ensure`,
# gelesen nur ueber `feature_vectors` (Kopie).
_VECTORS: dict[str, FeatureVector] = {}


def build_embed_text(feature: str) -> str:
    """Der Embed-Text eines Objekt-Merkmals — die EINZIGE Formel dafuer.

    Vorbedingung: `feature` ist nicht leer.
    Nachbedingung: Der Merkmalstext ohne Rand-Leerraum und ohne Praefix — genau
        die Form, in der er am 16.09.2026 geeicht wurde (`F-EMBED-1`).
    Fehlerfaelle: Leeres Merkmal ist ein `ValueError`, kein leerer Vektor.
    """
    if not feature or not feature.strip():
        raise ValueError(
            "build_embed_text(object_feature): Merkmal ist leer — kein Embed-Text baubar"
        )
    return feature.strip()


def _vector_defect(vector: list[float]) -> str | None:
    """Warum ein Vektor unbrauchbar ist, oder None.

    Ein Nullvektor und ein nicht endlicher Wert machen jede Kosinus-Naehe
    sinnlos, ohne dass die Rechnung scheitert — sie liefert dann 0.0 oder NaN,
    und beides sieht aus wie "nicht nahe".
    """
    if not vector:
        return "leer"
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in vector):
        return "nicht endlicher oder nicht numerischer Wert"
    if not any(x != 0 for x in vector):
        return "Nullvektor"
    return None


async def _embed_via_worker(text: str) -> list[float]:
    """Der Vektor ueber den Embed-Worker — eigene Funktion, damit Zeugen sie ersetzen.

    Die Frist steht hier und nicht am Worker (`F-FRIST-1`): Der Aufruf laeuft
    im Start des Servers, und `submit` wartet ohne Grenze. 60 s ist die
    Vorgabe der Sync-Bruecke desselben Workers, bemessen an Einbettungen
    unter Last von 20 s und mehr. Eine Ausgabegrenze hat ein Embedding nicht.
    """
    from services.model_services import EmbedRequest, model_service  # lokal: Startreihenfolge

    antwort = await asyncio.wait_for(
        model_service.embed.submit(EmbedRequest(text=text)), timeout=_EMBED_DEADLINE_S,
    )
    return list(antwort.embedding)


async def feature_vectors_ensure(
    agents: dict,
    embed: Callable[[str], Awaitable[list[float]]] | None = None,
) -> dict[str, FeatureVector]:
    """Bettet das Objekt-Merkmal jedes Dienstes am Empfang ein, der eins deklariert.

    Vorbedingung: `agents` bildet Namen auf Dienste ab (`AgentRegistry.alle()`);
        der Embed-Worker laeuft, falls `embed` nicht ersetzt ist.
    Nachbedingung: Der Bestand dieses Prozesses traegt fuer jeden Dienst mit
        Zustellart `empfang` und nicht leerem Merkmal genau einen gueltigen
        Vektor; alle Vektoren haben dieselbe Dimension. Zurueck kommt eine Kopie.
    Fehlerfaelle: Ein Einbettungsfehler oder ein unbrauchbarer Vektor fehlt
        diesem einen Dienst — `logger.error` mit Namen und Grund, der Start
        laeuft weiter. Ein Vektor abweichender Dimension wird verworfen, laut.
        Ein zuvor gehaltener Vektor desselben Dienstes wird dabei entfernt:
        Ein alter Vektor zu einem neuen Wortlaut waere eine stille Luege.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not isinstance(agents, dict):
        raise TypeError(
            f"feature_vectors_ensure: agents ist {type(agents).__name__}, erwartet dict"
        )
    einbetten = embed or _embed_via_worker

    # ── Verarbeitung ────────────────────────────
    empfang = {n: a for n, a in sorted(agents.items()) if a.zustellart == "empfang"}
    ohne: list[str] = []
    dimension: int | None = None
    for name, agent in empfang.items():
        # Die Deklaration ist Code eines Dienstes: Wirft sie oder ist sie kein
        # Text, fehlt diesem Dienst der Vektor — wie bei der Anmeldung darf ein
        # fehlerhaft angemeldeter Dienst den Start nicht verhindern.
        try:
            merkmal = agent.objekt_merkmal
        except Exception:  # noqa: BLE001 — fremder Code, der Start laeuft weiter
            logger.exception(
                "Objekt-Merkmal: Deklaration von Dienst '%s' wirft — kein Vektor", name,
            )
            _VECTORS.pop(name, None)
            continue
        if not isinstance(merkmal, str):
            logger.error(
                "Objekt-Merkmal: Dienst '%s' deklariert %s statt Text — kein Vektor",
                name, type(merkmal).__name__,
            )
            _VECTORS.pop(name, None)
            continue
        if not merkmal.strip():
            ohne.append(name)
            _VECTORS.pop(name, None)
            continue
        text = build_embed_text(merkmal)
        try:
            vektor = await einbetten(text)
        except Exception:  # noqa: BLE001 — ein Dienst ohne Vektor darf den Start nicht verhindern
            logger.exception(
                "Objekt-Merkmal: Einbettung fuer Dienst '%s' gescheitert — kein Vektor", name,
            )
            _VECTORS.pop(name, None)
            continue
        mangel = _vector_defect(vektor)
        if mangel is None and dimension is not None and len(vektor) != dimension:
            mangel = f"Dimension {len(vektor)} statt {dimension}"
        if mangel is not None:
            logger.error(
                "Objekt-Merkmal: Vektor fuer Dienst '%s' unbrauchbar (%s) — kein Vektor",
                name, mangel,
            )
            _VECTORS.pop(name, None)
            continue
        dimension = len(vektor)
        _VECTORS[name] = FeatureVector(
            service=name, text=text, vector=tuple(float(x) for x in vektor),
        )

    # ── Ausgabe-Verifikation ────────────────────
    ergebnis = feature_vectors()
    dimensionen = {len(v.vector) for v in ergebnis.values()}
    if len(dimensionen) > 1:
        logger.error("Objekt-Merkmal: gemischte Dimensionen %s im Bestand", sorted(dimensionen))
    logger.info(
        "Objekt-Merkmal: %d von %d Diensten am Empfang mit Vektor %s (Dimension %s); "
        "ohne Merkmal: %s",
        len(ergebnis), len(empfang), sorted(ergebnis), dimension, ohne,
    )
    return ergebnis


def feature_vectors() -> dict[str, FeatureVector]:
    """Die Merkmalsvektoren dieses Prozesses, als Kopie.

    Nachbedingung: leer, solange `feature_vectors_ensure` nicht lief — der
    Leser unterscheidet "kein Dienst hat ein Merkmal" nicht von "noch nicht
    eingebettet" und muss es auch nicht: In beiden Faellen gibt es nichts zu
    rechnen.
    """
    return dict(_VECTORS)
