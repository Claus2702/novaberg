"""
Post-Processing-Helfer fuer Modell-Worker-Antworten.

Zentralisiert die JSON- und CJK-Workarounds, die bisher als private Funktionen
in `services.llm_provider` lagen (`_clean_json_response`, `_deduplicate_repetition`,
`_repair_truncated_json`) plus die CJK-Erkennung aus `pixie_llm_call`.

Parallel-Pfad-Strategie (Microservice-Welle Block 2, Phase 2):
    Die analogen privaten Helfer in `llm_provider.py` bleiben in dieser Phase
    unveraendert in Co-Existenz. Die alte Welt (provider.chat / pixie_llm_call)
    nutzt weiterhin die privaten Kopien dort, die neue Worker-Welt nutzt die
    oeffentlichen Funktionen hier. Bewusste, dokumentierte, temporaere
    Duplikation. Konsolidierung erfolgt im Block-2-Cleanup, sobald die
    privaten Kopien nach der Konsumenten-Migration ungenutzt sind.

EVA-Prinzip (Developer-Handbook §1, §3):
    `parse_json_strict` propagiert JSONDecodeError bewusst — kein stiller
    Leerwert, kein Fallback. Die Silent-Skip-Lesson
    (`docs/novaberg-lesson_l_silent-skip.md`) verbietet stille Defaults bei
    Pflichtdaten.
"""

from __future__ import annotations

import json
import re


# ─────────────────────────────────────────────────────
# JSON-Bereinigung
# ─────────────────────────────────────────────────────

def clean_json_response(text: str) -> str:
    """Entfernt Markdown-Codeblock-Huellen (```json ... ```) um JSON-Text.

    Vorbedingung: `text` ist ein String (darf leer sein).
    Nachbedingung: Rueckgabe ist getrimmter Text ohne fuehrendes/abschliessendes
    Code-Fence.
    Fehlerfaelle: keine — gibt im Worst Case den getrimmten Originaltext zurueck.
    """

    # ── Verarbeitung ────────────────────────────
    cleaned: str = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    # ── Ausgabe ─────────────────────────────────
    return cleaned.strip()


def deduplicate_repetition(text: str) -> str:
    """Kappt Endlos-Wiederholungen (Gemma4/Qwen-MoE-Bug bei langen JSON-Strings).

    Findet Muster von 8–50 Zeichen, die sich dreifach oder oefter wiederholen,
    und behaelt nur das erste Vorkommen. Verhindert, dass `json.loads` an
    Token-Limit-Repetitionen scheitert.
    Vorbedingung: `text` ist ein String.
    Nachbedingung: Bei erkanntem Repetitions-Muster ist der Text bis zur Stelle
    nach dem ersten Vorkommen gekuerzt; sonst unveraendert.
    """

    # ── Eingabe-Validierung ─────────────────────
    if not text:
        return text

    # ── Verarbeitung ────────────────────────────
    match = re.search(r'(.{8,50}?)\1{2,}', text)
    if match:
        text = text[:match.start() + len(match.group(1))]

    # ── Ausgabe ─────────────────────────────────
    return text


def repair_truncated_json(text: str) -> str:
    """Balanciert Klammern und Quotes bei am Token-Limit abgeschnittenem JSON.

    Schliesst offene Strings, Objekte und Arrays, damit `json.loads` nicht
    an unterminierten Strukturen scheitert. Der Inhalt abgeschnittener
    Strings bleibt unvollstaendig, aber die Struktur wird parsbar.
    Vorbedingung: `text` ist ein String.
    Nachbedingung: Rueckgabe enthaelt eine ausgeglichene Anzahl von `{}`/`[]`
    und eine gerade Anzahl von `"`.
    """

    # ── Eingabe-Validierung ─────────────────────
    text = text.strip()
    if not text:
        return text

    # ── Verarbeitung ────────────────────────────
    if text.count('"') % 2 != 0:
        text = text + '"'

    open_braces:   int = text.count('{') - text.count('}')
    open_brackets: int = text.count('[') - text.count(']')

    if open_braces > 0:
        text = text + '}' * open_braces
    if open_brackets > 0:
        text = text + ']' * open_brackets

    # ── Ausgabe ─────────────────────────────────
    return text


# ─────────────────────────────────────────────────────
# CJK-Erkennung (Qwen-Leakage)
# ─────────────────────────────────────────────────────

# Identisch zur Range in `services.llm_provider._CJK_RANGE`:
# CJK Unified Ideographs (一–鿿) + CJK Unified Ideographs Extension A
# (㐀–䶿). Deckt die haeufigsten Qwen-Leakage-Zeichen ab.
_CJK_RANGE: re.Pattern[str] = re.compile(r'[一-鿿㐀-䶿]')


def contains_cjk(text: str) -> bool:
    """True, wenn der Text chinesische Schriftzeichen enthaelt.

    Qwen-Modelle leaken bei laengeren deutschen Prompts gelegentlich CJK-Tokens.
    Der BackgroundWorker prueft damit, ob ein Retry mit verschaerftem
    Sprach-Hinweis noetig ist.
    """
    return bool(_CJK_RANGE.search(text))


def strip_cjk(text: str) -> str:
    """Entfernt chinesische Schriftzeichen aus dem Text (harter Fallback).

    Wird verwendet, wenn auch ein Retry kein CJK-freies Ergebnis liefert.
    Strukturell schlechter als ein erfolgreicher Retry, aber besser als
    deutsch-chinesisches Misch-Output an die Pipeline durchzureichen.
    """
    return _CJK_RANGE.sub('', text)


# ─────────────────────────────────────────────────────
# JSON-Parsing (strict)
# ─────────────────────────────────────────────────────

def parse_json_strict(text: str) -> dict:
    """Saeubert (clean → dedupe → repair) und parst JSON.

    Wirft JSONDecodeError, wenn auch nach allen Bereinigungs-Schritten kein
    valides JSON entsteht — KEIN stiller Leerwert, KEIN `{}`-Fallback.
    Vorbedingung: `text` ist ein String, der ein JSON-Objekt enthalten soll.
    Nachbedingung: Rueckgabe ist das geparste Dict (oder die Liste — der Typ
    haengt vom Aufrufer ab; gemeint sind hier JSON-Objekte gemaess Worker-
    Konvention).
    Fehlerfaelle: JSONDecodeError propagiert an den Aufrufer (Silent-Skip-
    Lesson, Developer-Handbook §3).
    """

    # ── Verarbeitung ────────────────────────────
    cleaned: str = clean_json_response(text)
    cleaned = deduplicate_repetition(cleaned)
    cleaned = repair_truncated_json(cleaned)

    # ── Ausgabe (mit propagierender Validierung) ─
    return json.loads(cleaned)
