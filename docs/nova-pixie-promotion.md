# Nova — Pixie-Agent: PromotionAgent

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** PromotionAgent — KZG-nach-LZG-Promotion (Zwei-Call-Prozess)
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-pixie-promotion.md
**Quellen:** nova-05-m-a.md, nova-03-t-b.md

---

## 1. Aufgabe

Der PromotionAgent ist der einzige Weg vom Kurzzeitgedächtnis (KZG, Redis) ins Langzeitgedächtnis (LZG, PostgreSQL) und in den Knowledge Graph. Pixie arbeitet die Promotion-Queue ab und führt für jeden Eintrag zwei LLM-Calls durch: Der erste klassifiziert, der zweite extrahiert strukturierte Fakten-Tripel. Python-Nachbearbeitung filtert Müll, löst Entitäten auf und schreibt die Ergebnisse.

**Dateien:** `agents/promotion/agent.py`, `AGENT.md`

---

## 2. Scheduling

| Aspekt | Detail |
|--------|--------|
| **Priorität** | 0.9 (höchste unter allen Pixie-Agenten) |
| **Intervall** | Alle 5 Minuten |
| **Queue** | Promotion-Queue (`queue:{user_id}`) — wird VOLLSTÄNDIG abgearbeitet |
| **LLM-Call** | 1–3 Calls pro Eintrag (CPU-Modell) |
| **context_user** | `user` |

Die Queue wird vollständig abgearbeitet (while-Schleife mit LPOP). KZG-Einträge haben TTL — Verzögerung bedeutet Datenverlust. Die Promotion hat deshalb die höchste Priorität unter allen Pixie-Agenten.

---

## 3. Zwei-Call-Prozess

Ein einzelner Prompt, der gleichzeitig klassifiziert, Entitäten erkennt, Referenzen von Interfaces unterscheidet UND strukturierte Tripel extrahiert, wäre zu komplex für ein 24B-Modell. Zwei spezialisierte Calls sind robuster.

### Call 1 — Klassifikation

**Input:** KZG-Eintrag (Themen, Inhalt, Salienz) mit Speaker prominent an erster Stelle (`>>> SPEAKER: {name} <<<`).

Drei simultane Entscheidungen:

**a) Fakt oder Erinnerung?**
- Fakt → Weiter zu Call 2 (Tripel-Extraktion)
- Erinnerung → Direkt ins LZG als Fließtext (Typ 3, kein Call 2)

**b) Entitäten erkennen:** Welche Entitäten kommen vor? Typ: person, ort, organisation, tier, objekt.

**c) Referenz oder Interface?**
- Referenz: Hat einen Eigennamen, konkret identifizierbar → wird aufgelöst. Beispiele: Anna, Nürnberg, BMW.
- Interface: Gattungsbegriff, kein Eigenname → wird ignoriert. Beispiele: Gehirn, KI, Kaffee, Freunde.

### Call 2 — Fakten-Extraktion

Nur wenn Call 1 mindestens einen Fakt erkannt hat. Input: Erkannte Entitäten aus Call 1 + Originaltext.

Output: Strukturierte Fakten-Tripel (Subjekt → Attribut → Objekt):

```json
[
    {"subjekt": "ICH", "attribut": "HAT_SCHWESTER", "objekt": "Anna"},
    {"subjekt": "Anna", "attribut": "HAT_BESITZ", "objekt_wert": "Birnbaum"}
]
```

---

## 4. Nachbearbeitung — 4 Qualitätsfilter

### O5: Speaker-Auflösung

"ich" im KZG-Eintrag wird auf die konkrete `user_id` aufgelöst. Das LLM liefert manchmal "Nutzer" statt den konkreten Namen — der Nachbearbeitungsschritt prüft und korrigiert.

### O6: Interface-Regel

Zusätzliche Python-Prüfung ob eine als Referenz markierte Entität wirklich einen Eigennamen hat. Wissenschaftliche Begriffe, Fachgebiete, Aktivitäten, Lebensmittel sind IMMER Interfaces. Fängt Fälle ab, die der Prompt nicht erwischt.

### O11: Objekt-Entitäten

Call 2 liefert manchmal `"objekt_id": "neu"` als String statt einer echten ID. Der Nachbearbeitungsschritt setzt solche String-IDs zurück und löst sie per Entitäten-Liste korrekt auf. Verhindert, dass Orte als `objekt_wert` statt als eigene Entität gespeichert werden.

### O12: Tautologie-Filter

`_ist_tautologisch()` erkennt und filtert Fakten, bei denen das Objekt das Attribut wiederholt:
- "Anna HAT_WOHNUNG Wohnung" → Tautologie → gefiltert
- "Anna WOHNT_IN München" → kein Tautologie → durchgelassen

Konservativ: Lieber einen sinnlosen Fakt durchlassen als einen guten filtern.

---

## 5. Entity Resolution

Alle Referenz-Entitäten aus Call 1+2 durchlaufen die Entity Resolution via `EntitaetenRepository`:

- Bekannt → ID zuweisen
- Neu → INSERT mit Embedding
- Mehrdeutig → Rückfrage (aktuell geloggt)

**Edge Invalidation:** Für jeden Fakt: Existiert ein aktiver Fakt mit gleichem Subjekt + Attribut? Gleicher Wert → Bestätigung (`last_touched` aktualisieren). Anderer Wert → Widerspruch → Alten Fakt invalidieren, neuen INSERT.

---

## 6. hash_dirty

Nach erfolgreicher Promotion setzt der Agent das Flag `hash_dirty:{user_id}` in Redis. Der CharakterAgent prüft dieses Flag und destilliert bei Bedarf die Charakter-Profile neu.

---

## 7. Konfiguration

| Parameter | Wert | Pfad | Beschreibung |
|-----------|------|------|-------------|
| `PROMOTION_THRESHOLD` | 0.8 | `memory/kzg.py` | Salienz-Minimum für Eintritt in die Promotion-Queue |
| `PIXIE_PROMOTION_PRIORITAET` | 0.9 | `config.py` | Höchste Pixie-Scheduler-Priorität |
| `PIXIE_PROMOTION_INTERVALL_SEKUNDEN` | 300 (5 min) | `config.py` | Task-Intervall (PeriodicTask) |
| Analyse-Modell | `qwen3-32b-cpu` | — | Reasoning, JSON-Output |
| Sprach-Modell | `mistral-small3.2-cpu` | — | Fließtext, Deutsch (bei Typ-3-Erinnerungen) |

**LLM-Call-Budget pro Eintrag:**

| Schicht | Calls | Bedingung |
|---------|-------|-----------|
| Call 1: Klassifikation | 1 | Immer |
| Call 2: Fakten-Extraktion | 0–1 | Nur wenn Fakt erkannt |
| Entity Resolution | 0–1 | Nur bei Mehrdeutigkeit |
| **Total** | **1–3** | |

---

Verwandte Dokumente:
- KZG-Agent (Promotion-Queue-Quelle): `nova-pixie-kzg.md`
- DecayAgent (Ebbinghaus): `nova-pixie-decay.md`
- CharakterAgent (hash_dirty-Konsument): `nova-pixie-character-hash.md`
- Pixie-Agenten-Übersicht: `nova-pixie.md`
