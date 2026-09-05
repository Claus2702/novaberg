#!/usr/bin/env python3
"""Haelt die konfigurierten OpenRouter-Preise gegen den lebenden Endpunkt.

Der Endpunkt fuer `deepseek/deepseek-v4-flash-0731` trug am 05.09.2026 einen
Rabatt von 64,3 % (`pricing.discount: 0.643`). **Die Schnittstelle nennt die
Hoehe des Rabatts, nie sein Ende.** Ein Preis, der still auf Listenniveau
zurueckginge, faende sich in der Rechnung und sonst nirgends — dieses Werkzeug
macht daraus eine Protokollzeile und einen Rueckgabewert.

Es bewacht ausserdem, was ein Anbieterwechsel ausser dem Preis aendern wuerde:
das Kontextfenster, die Quantisierung und ob `response_format` ueberhaupt
gefuehrt wird. Vier von 29 Anbietern hinter dieser Modell-ID fuehren es nicht,
und ohne es ist `expect_json` wieder eine Bitte statt einer Fessel.

AUFRUF
    python -m tools.openrouter_price_watch
    python -m tools.openrouter_price_watch --json

Rueckgabewert 0 heisst: Endpunkt und Konfiguration stimmen ueberein. Alles
andere ist ein Befund — damit das Werkzeug aus einem Zeitplan laufen kann,
ohne dass jemand seine Ausgabe liest.
"""

from __future__ import annotations

import json
import logging
import sys

import httpx

from config import (
    OPENROUTER_GEFUEHRTE_PARAMETER,
    OPENROUTER_MODEL,
    OPENROUTER_NUM_CTX,
    OPENROUTER_PRICE_INPUT_PER_M,
    OPENROUTER_PRICE_OUTPUT_PER_M,
    OPENROUTER_PROVIDER,
    OPENROUTER_QUANTISIERUNG,
)

logger = logging.getLogger("ki_server.tools.price_watch")

#: Wo die Endpunktliste liegt. Braucht keinen Schluessel.
ENDPOINT_URL: str = "https://openrouter.ai/api/v1/models/{model}/endpoints"

#: Wie weit ein Preis abweichen darf, bevor er als geaendert gilt. Die Preise
#: stehen je Token mit zehn Nachkommastellen; ein exakter Vergleich meldete
#: einen Befund auf einen Rundungsunterschied. Ein Hunderttausendstel Dollar
#: je Million liegt weit unter jedem echten Preisschritt und weit ueber dem
#: Rauschen.
TOLERANCE_PER_M: float = 0.00001


def fetch_endpoints(client: httpx.Client, model: str) -> list[dict]:
    """Liefert alle Endpunkte, die zu einer Modell-ID angeboten werden.

    Vorbedingung: `model` ist eine dem Zugang bekannte Modell-ID.
    Nachbedingung: die Endpunktliste, nie `None`.
    Fehlerfaelle: `ValueError` ohne Modell-ID, `RuntimeError` bei einer Antwort
    ausserhalb 2xx, `TypeError` bei einem Rumpf ohne Endpunktliste — **eine
    leere Liste hiesse *keine Anbieter*, und das ist eine andere Aussage als
    *der Aufruf ist gescheitert*.**
    """
    # ── Eingabe-Validierung ─────────────────────
    if not model:
        raise ValueError("fetch_endpoints ohne Modell-ID")

    # ── Verarbeitung ────────────────────────────
    antwort = client.get(ENDPOINT_URL.format(model=model))
    if antwort.status_code >= 400:
        raise RuntimeError(
            f"Endpunktliste nicht abrufbar: HTTP {antwort.status_code} "
            f"— {antwort.text[:400]}"
        )
    rumpf = antwort.json()

    # ── Ausgabe-Verifikation ────────────────────
    if not isinstance(rumpf, dict) or "data" not in rumpf:
        raise TypeError(f"unerwartete Rumpfform: {str(rumpf)[:400]}")
    endpunkte = (rumpf["data"] or {}).get("endpoints")
    if not isinstance(endpunkte, list):
        raise TypeError(f"keine Endpunktliste im Rumpf: {str(rumpf)[:400]}")
    return endpunkte


def pick_provider(endpoints: list[dict], provider: str, quantization: str) -> dict:
    """Liefert den Endpunkt, auf den die Konfiguration zeigt.

    Vorbedingung: `endpoints` stammt aus `fetch_endpoints`.
    Nachbedingung: genau ein Endpunkt.
    Fehlerfaelle: `ValueError` ohne Anbieternamen; `RuntimeError`, wenn der
    Anbieter fehlt oder mehrdeutig ist.

    **Der fehlende Anbieter ist der interessante Fall.** Mit abgeschaltetem
    Rueckfall antwortet der Server dann gar nicht mehr; dieses Werkzeug sagt
    warum, bevor jemand einen Stacktrace liest.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not provider:
        raise ValueError("pick_provider ohne Anbieternamen")

    # ── Verarbeitung ────────────────────────────
    treffer = [
        e for e in endpoints
        if (e.get("tag") or "").split("/")[0] == provider
        and (not quantization or e.get("quantization") == quantization)
    ]

    # ── Ausgabe-Verifikation ────────────────────
    if not treffer:
        vorhanden = sorted({(e.get("tag") or "?") for e in endpoints})
        raise RuntimeError(
            f"Anbieter {provider!r} (Quantisierung {quantization!r}) fuehrt "
            f"{OPENROUTER_MODEL!r} nicht mehr — angeboten: {vorhanden}"
        )
    if len(treffer) > 1:
        raise RuntimeError(
            f"Anbieter {provider!r} fuehrt {len(treffer)} Endpunkte — die "
            f"Konfiguration sagt nicht welchen: {[t.get('tag') for t in treffer]}"
        )
    return treffer[0]


def compare(endpoint: dict) -> list[str]:
    """Nennt jeden Unterschied zwischen Endpunkt und Konfiguration.

    Vorbedingung: `endpoint` ist ein Eintrag der Endpunktliste.
    Nachbedingung: eine Zeile je Unterschied, leer bei Gleichstand.
    Fehlerfaelle: keine — ein fehlendes Feld wird ein Befund, keine Ausnahme.
    Ein Waechter, der am Fehlen seiner Eingabe stirbt, meldet nichts.
    """
    # ── Eingabe-Validierung ─────────────────────
    preise: dict = endpoint.get("pricing") or {}
    befunde: list[str] = []

    # ── Verarbeitung ────────────────────────────
    for name, schluessel, konfiguriert in (
        ("Eingangspreis", "prompt",     OPENROUTER_PRICE_INPUT_PER_M),
        ("Ausgangspreis", "completion", OPENROUTER_PRICE_OUTPUT_PER_M),
    ):
        roh = preise.get(schluessel)
        if roh is None:
            befunde.append(f"{name} fehlt am Endpunkt")
            continue
        lebend = float(roh) * 1_000_000
        if abs(lebend - konfiguriert) > TOLERANCE_PER_M:
            if konfiguriert:
                richtung = "gestiegen" if lebend > konfiguriert else "gesunken"
                befunde.append(
                    f"{name} {richtung}: konfiguriert ${konfiguriert:.5f}/M, "
                    f"lebend ${lebend:.5f}/M — Faktor {lebend / konfiguriert:.2f}"
                )
            else:
                befunde.append(f"{name} ist ${lebend:.5f}/M, konfiguriert 0")

    if not preise.get("discount"):
        befunde.append("der Rabatt ist fort — der Endpunkt weist keinen mehr aus")

    fenster = endpoint.get("context_length")
    if fenster != OPENROUTER_NUM_CTX:
        befunde.append(
            f"Kontextfenster geaendert: konfiguriert {OPENROUTER_NUM_CTX:,}, "
            f"lebend {fenster:,}"
        )

    quantisierung = endpoint.get("quantization")
    if OPENROUTER_QUANTISIERUNG and quantisierung != OPENROUTER_QUANTISIERUNG:
        befunde.append(
            f"Quantisierung geaendert: konfiguriert {OPENROUTER_QUANTISIERUNG!r}, "
            f"lebend {quantisierung!r}"
        )

    angeboten = set(endpoint.get("supported_parameters") or [])
    fehlend = sorted(OPENROUTER_GEFUEHRTE_PARAMETER - angeboten)
    if fehlend:
        befunde.append(
            f"der Anbieter fuehrt {fehlend} nicht mehr — "
            f"OPENROUTER_GEFUEHRTE_PARAMETER ist veraltet"
        )

    # Keine Ausgabe-Verifikation, und das ist Absicht: Die Befundliste **ist**
    # das Ergebnis der Pruefung. Eine Marke ueber einem nackten `return` sieht
    # beim Lesen aus wie eine Verifikation und ist keine (`11_EVA` §4).
    return befunde


def main() -> int:
    """Fuehrt die Pruefung aus und liefert den Rueckgabewert.

    Vorbedingung: die OpenRouter-Konstanten sind gesetzt; der Endpunkt ist
    ueber das Netz erreichbar. Ein Schluessel wird **nicht** gebraucht.
    Nachbedingung: 0 bei Gleichstand, 1 bei mindestens einem Befund; die
    Befunde stehen als Warnungen im Protokoll, mit `--json` auf der Ausgabe.
    Fehlerfaelle: die Ausnahmen von `fetch_endpoints` und `pick_provider` —
    sie brechen absichtlich durch, weil ein Waechter, der seinen Gegenstand
    nicht findet, nicht *„keine Befunde"* melden darf.
    """
    # ── Eingabe-Validierung & Verarbeitung ──────
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with httpx.Client(timeout=30.0) as client:
        endpunkte = fetch_endpoints(client, OPENROUTER_MODEL)
        endpunkt = pick_provider(
            endpunkte, OPENROUTER_PROVIDER, OPENROUTER_QUANTISIERUNG,
        )
    befunde = compare(endpunkt)
    preise = endpunkt.get("pricing") or {}

    # ── Ausgabe-Verifikation ────────────────────
    if "--json" in sys.argv:
        print(json.dumps({
            "model":        OPENROUTER_MODEL,
            "provider":     endpunkt.get("tag"),
            "input_per_m":  float(preise.get("prompt", 0)) * 1_000_000,
            "output_per_m": float(preise.get("completion", 0)) * 1_000_000,
            "discount":     preise.get("discount"),
            "findings":     befunde,
        }, indent=1))
        return 1 if befunde else 0

    logger.info(
        "%s ueber %s — $%.5f ein / $%.5f aus je Million, Rabatt %s",
        OPENROUTER_MODEL, endpunkt.get("tag"),
        float(preise.get("prompt", 0)) * 1_000_000,
        float(preise.get("completion", 0)) * 1_000_000,
        f"{float(preise['discount']) * 100:.1f} %" if preise.get("discount") else "keiner",
    )
    for befund in befunde:
        logger.warning("  BEFUND: %s", befund)
    logger.info("%d Befund(e)", len(befunde))
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
