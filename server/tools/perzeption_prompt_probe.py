#!/usr/bin/env python3
"""Prueft, ob das Perzeptions-Modell den `modus` korrekt verteilt.

**Der Befund** `[gemessen 10.09.2026 ueber 1347 Turns]`: Dasselbe Modell vergibt
"kreativ" **161-mal** als `tone` und **92-mal** als `intent` (`creative`) — und
**null-mal** als `modus`. Der Wert ist der einzige, der die Vektorlaenge des
Gespraechsvektors hebt.

**Die Vermutung, die hier geprueft wird:** Es liegt an der Legende. Der Prompt
erklaert `intent`, `arousal`, `emotion` und `beziehungs_dynamik` **Wert fuer
Wert** — `modus` und `sprach_stil` bekommen je einen Satz und keine einzige
Werterklaerung.

**Zwei Arme, dieselben Reize, dasselbe Modell.** Arm A faehrt den Prompt des
Betriebs, Arm B denselben mit einer Wertelegende fuer `modus` und
`sprach_stil`. Der Lauf geht ueber `model_service.chat` — denselben Worker wie
der Betrieb, mit der Temperatur des Knotens (`21_MESSUNG/konfiguration-mitsenden.md`).

**Er faehrt keinen Turn.** Nur die Perzeption, ohne Graph, ohne Schreibpfad —
also ohne Seiteneffekte im Gedaechtnis.

Aufruf (im Server-Container):
    python tools/perzeption_prompt_probe.py <reizdatei> [--mit-legende]
"""

import json
import sys
from collections import Counter

from config import get_node_config
from graph.nodes.perzeption import _build_system_prompt, _wahrnehmung_lesen
from services.model_services import model_service

#: Die Legende fuer `modus`, in genau der Form, die `intent` und
#: `beziehungs_dynamik` im Prompt schon haben. Die Formulierungen sind aus den
#: Konstanten-Kommentaren und dem Konzept gezogen, nicht erfunden.
MODUS_LEGENDE: str = """
  "modus" — waehle genau EINEN:
  "fachgespraech" = Fachbegriffe, praezise Sachfrage unter Kundigen
  "philosophischer_austausch" = Sinn-, Erkenntnis- oder Wertefragen, offener Ausgang
  "alltag" = beilaeufige Beobachtung, Kleines, nichts wird verhandelt
  "arbeitsmodus" = Struktur, Vorgehen, Abarbeiten einer Sache
  "emotional" = das Gefuehl selbst ist der Gegenstand, nicht das Thema
  "spielerisch" = Neckerei, Unsinn, Wettstreit ohne Ernst
  "lernmodus" = will etwas erklaert bekommen, Schritt fuer Schritt
  "kreativ" = etwas soll ENTSTEHEN — erfinden, ausmalen, ein Bild bauen,
              ein Was-waere-wenn durchspielen
  "beratend" = Entscheidung steht an, sucht Abwaegung
  "berichtend" = schildert einen Vorgang, ohne Frage
"""

#: Dieselbe Form fuer `sprach_stil`, der dieselbe Luecke hat.
STIL_LEGENDE: str = """
  "sprach_stil" — waehle genau EINEN:
  "locker" = kurze Saetze, Umgangssprache, Verkuerzungen
  "formell" = vollstaendige Saetze, Hoeflichkeitsform, Distanz in der Wortwahl
  "fachlich" = Fachvokabular, Praezision vor Zugaenglichkeit
  "emotional" = Wortwahl traegt das Gefuehl, Verstaerker, Ausrufe
  "jugendlich" = Slang, Anglizismen, Jugendsprache
  "neutral" = keines der obigen erkennbar
"""


def prompt_bauen(mit_legende: bool) -> str:
    """Baut den System-Prompt beider Arme.

    **Ohne Session-Kontext** — der Knoten haengt im Betrieb die letzten Turns
    an. Fuer den Vergleich der beiden Arme ist das gleichgueltig; fuer einen
    Vergleich mit dem Bestand waere es das nicht.
    """
    prompt: str = _build_system_prompt("10.09.2026, 19:30 Uhr", None, rolle="user")
    if not mit_legende:
        return prompt

    # Die Legende geht dorthin, wo die Dimension beschrieben wird — hinter den
    # einen Satz, den sie heute traegt.
    marke: str = '- "modus": Das Kommunikationsregister, in dem der User spricht'
    if marke not in prompt:
        raise ValueError("Die Ankerzeile der Modus-Beschreibung fehlt im Prompt")
    return prompt.replace(marke, marke + "\n" + MODUS_LEGENDE + STIL_LEGENDE, 1)


def einen_reiz(reiz: str, system_prompt: str) -> dict:
    """Fragt das Modell einmal und gibt die interessierenden Werte.

    **Am Worker vorbei, aber nicht an seiner Konfiguration.** `submit_sync`
    setzt eine laufende Queue voraus, die es nur im Serverprozess gibt (der
    Riegel meldet das sauber). Der Provider dahinter ist derselbe — Modell,
    Kontextfenster und Zugang kommen aus der Registry des Betriebs, nicht aus
    einer Kopie (`21_MESSUNG/konfiguration-mitsenden.md`).
    """
    node_cfg = get_node_config("perzeption")
    backend = model_service.chat._backend          # noqa: SLF001 — Messwerkzeug
    antwort = backend.chat(
        messages          = [{"role": "user", "content": reiz}],
        system            = system_prompt,
        temperature       = node_cfg.get("temperature", 0.05),
        expect_json       = True,
        max_output_tokens = node_cfg.get("max_output_tokens"),
        caller            = "perzeption_probe",
    )
    # **Der Provider parst nicht — das tut sonst der Worker.** `content` traegt
    # den JSON-Body; ein unlesbarer faellt hier auf und wird gezaehlt, statt
    # still zu einem Leerwert zu werden.
    roh: dict = json.loads(antwort.content)

    # **Was der Zug daraus macht** — derselbe Leser wie im Knoten. Ohne ihn
    # zeigt die Probe die Rohantwort und nicht, was im Zustand landet.
    gezogen = _wahrnehmung_lesen(roh)
    return {
        "gezogen_modus":   gezogen.modus,
        "gezogen_tone":    gezogen.tone,
        "gezogen_intent":  gezogen.intent,
        "gezogen_stil":    gezogen.sprach_stil,
        "modus":   (roh.get("psychologisch") or {}).get("modus", ""),
        "stil":    (roh.get("psychologisch") or {}).get("sprach_stil", ""),
        "dynamik": (roh.get("psychologisch") or {}).get("beziehungs_dynamik", ""),
        "intent":  (roh.get("rational") or {}).get("intent", ""),
        "tone":    (roh.get("rational") or {}).get("tone", ""),
    }


if __name__ == "__main__":
    pfad:        str  = sys.argv[1]
    mit_legende: bool = "--mit-legende" in sys.argv

    zeilen: list[tuple[str, str]] = []
    for roh in open(pfad, encoding="utf-8"):
        if not roh.strip() or "|" not in roh:
            continue
        etikett, reiz = roh.rstrip("\n").split("|", 1)
        zeilen.append((etikett, reiz))

    system_prompt: str = prompt_bauen(mit_legende)
    arm: str = "MIT Legende" if mit_legende else "OHNE Legende (Betrieb)"
    print(f"# Arm: {arm}  ·  {len(zeilen)} Reize  ·  "
          f"Prompt {len(system_prompt)} Zeichen", flush=True)

    treffer = 0
    werte_alle: list[dict] = []
    modi:   Counter = Counter()
    stile:  Counter = Counter()
    for etikett, reiz in zeilen:
        try:
            werte = einen_reiz(reiz, system_prompt)
        except Exception as fehler:            # noqa: BLE001 — die Probe soll durchlaufen
            print(json.dumps({"etikett": etikett, "fehler": str(fehler)[:80]}), flush=True)
            continue
        werte["etikett"] = etikett
        werte["treffer"] = werte["modus"] == etikett
        treffer += werte["treffer"]
        werte_alle.append(werte)
        modi[werte["modus"]] += 1
        stile[werte["stil"]] += 1
        print(json.dumps(werte, ensure_ascii=False), flush=True)

    n = len(zeilen)
    print(f"\n# Treffer modus == etikett: {treffer} von {n} ({100*treffer/n:.1f} %)")
    print(f"# Modi vergeben:  {dict(modi.most_common())}")
    print(f"# Stile vergeben: {dict(stile.most_common())}")
    print(f"# 'kreativ' als modus: {modi.get('kreativ', 0)}")

    # **Was der Zug gerettet hat.** Ein Wert, der roh ausserhalb stand und
    # gezogen im Kanon landet, ist die Wirkung; einer, der in beiden Spalten
    # gleich bleibt, ist ein echter Ausreisser.
    from graph.nodes.perzeption import _FELDER_KANON
    gerettet = ausser_roh = 0
    for w in werte_alle:
        for feld, roh_key, gez_key in (("modus", "modus", "gezogen_modus"),
                                       ("tone", "tone", "gezogen_tone"),
                                       ("intent", "intent", "gezogen_intent"),
                                       ("sprach_stil", "stil", "gezogen_stil")):
            roh_wert, gez_wert = w.get(roh_key, ""), w.get(gez_key, "")
            if roh_wert and roh_wert not in _FELDER_KANON[feld]:
                ausser_roh += 1
                gerettet += gez_wert in _FELDER_KANON[feld]
    print(f"# Rohwerte ausserhalb ihres Kanons: {ausser_roh}  ·  davon vom Zug gerettet: {gerettet}")
