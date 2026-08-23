"""Prompt-Lade-System — Default, Modell, Connector.

Laedt statische Prompt-Bloecke aus Textdateien. Einmal beim Start, danach
im RAM.

**Drei Ebenen, und die Reihenfolge ist die Aussage.** Ein spaeter geladener
Block ueberschreibt einen frueheren:

  1. `prompts/default/` — was ohne Ansehen des Modells gilt
  2. `prompts/{modell}/` — was an dem Modell haengt, das antwortet
  3. `prompts/{connector}/` — was an dieser Zusammenstellung haengt

**Warum die mittlere Ebene seit dem 23.08.2026 existiert.** Bis dahin gab
es nur Default und Connector, und das war fuer Gespraechs-Bloecke die
falsche Groesse: Zwei der drei Connectoren fahren im Gespraech **dasselbe**
GPU-Modell (`gemma4` und `qwen36` beide `gemma4-gpu`). Sieben fuer Gemma4
gebaute Bloecke lagen deshalb unter dem aktiven Connector `qwen36` still,
waehrend Gemma4 antwortete — im Betriebslog als *"Keine Overrides fuer
Connector 'qwen36'"* nachlesbar.

**Der Connector bleibt die letzte Ebene, weil er der engere Schluessel
ist.** Zwei Connectoren teilen sich ein Modell, aber kein Modell teilt sich
einen Connector; wer ausdruecklich nach Zusammenstellung schluesselt, meint
mehr als das Modell und soll es behalten. Fuer Hintergrund-Bloecke ist das
die richtige Ebene — dort unterscheiden sich die Connectoren wirklich
(`cpu_model` ist bei `gemma4` und `qwen36` verschieden).
"""

import logging
import os

logger = logging.getLogger("ki_server.prompts")


def _bloecke_lesen(verzeichnis: str) -> dict[str, str]:
    """Liest alle `.txt` eines Verzeichnisses als Bloecke.

    Vorbedingung: keine — ein fehlendes Verzeichnis ist kein Fehler,
    sondern die Auskunft, dass es fuer diese Ebene nichts gibt.
    Nachbedingung: Abbildung Blockname → Text, leer wenn nichts da ist.
    Der Blockname ist der Dateiname ohne Endung (`router.rules`).
    """
    if not os.path.isdir(verzeichnis):
        return {}

    bloecke: dict[str, str] = {}
    for datei in sorted(os.listdir(verzeichnis)):
        if not datei.endswith(".txt"):
            continue
        with open(os.path.join(verzeichnis, datei), encoding="utf-8") as f:
            bloecke[datei[:-4]] = f.read().strip()
    return bloecke


def prompt_laden(
    connector: str, prompt_dir: str = "", modell: str = "",
) -> dict[str, str]:
    """Laedt alle Prompt-Bloecke fuer Modell und Connector.

    Vorbedingung: `connector` ist der Name der aktiven Zusammenstellung;
    `modell` ist das **konfigurierte GPU-Modell** des Connectors (leer
    heisst: keine Modellebene). `prompt_dir` steht fuer Zeugen offen.

    **Der Aufrufer reicht `OLLAMA_MODEL`, und das ist nicht in jedem Fall
    das Modell, das antwortet.** Welches der Chat-Worker fuehrt, entscheidet
    `MODEL_WORKER_BACKENDS["chat"]`; steht dort ein anderer Rueckhalt, ist
    die Modellebene nach dem GPU-Modell geschluesselt, waehrend ein anderes
    Modell spricht. Heute deckungsgleich (`ollama_gpu`, im Betriebslog
    belegt). Bis zu diesem Umbau war der Fall folgenlos, weil die
    Modellebene nie etwas lud — **die Reichweite ist neu**, und der Fund
    steht in `novaberg-fundliste.md`.
    Nachbedingung: Abbildung `{"node.block": "text"}`. Die drei Ebenen sind
    in der Reihenfolge default → Modell → Connector angewandt; jede spaetere
    ueberschreibt.

    **Fehlt `prompts/default/`, ist das ein Fehler und kein Leerfall** — es
    gibt dann keinen einzigen Block, und jeder Knoten liefe in einen
    KeyError statt in eine Meldung.
    """
    # ── Eingabe-Validierung ─────────────────────
    if not prompt_dir:
        prompt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

    default_path: str = os.path.join(prompt_dir, "default")
    if not os.path.isdir(default_path):
        logger.error(f"Prompt-Verzeichnis nicht gefunden: {default_path}")
        return {}

    # ── Verarbeitung ────────────────────────────
    prompts: dict[str, str] = _bloecke_lesen(default_path)
    logger.info(f"Prompts: {len(prompts)} Default-Bloecke geladen")

    for ebene, schluessel in (("Modell", modell), ("Connector", connector)):
        if not schluessel:
            continue
        bloecke: dict[str, str] = _bloecke_lesen(os.path.join(prompt_dir, schluessel))
        prompts.update(bloecke)
        if bloecke:
            logger.info(
                f"Prompts: {len(bloecke)} Override(s) ueber {ebene} "
                f"'{schluessel}': {sorted(bloecke)}",
            )
        else:
            logger.info(f"Prompts: Keine Overrides ueber {ebene} '{schluessel}'")

    # ── Ausgabe-Verifikation ────────────────────
    if not prompts:
        logger.error(
            "Prompts: kein einziger Block geladen — jeder Knoten, der einen "
            "erwartet, laeuft in einen KeyError",
        )

    return prompts
