# Novaberg — Lesson: Lokale Bindung vor Nutzung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — `UnboundLocalError` beim Einfügen von Argumenten an bestehende Call-Sites
**Stand:** 11. Juli 2026, Chat 104
**Pfad:** novaberg/docs/novaberg-lesson_l_lokale-bindung-vor-nutzung.md
**Auslöser:** Paar-Verkabelung des `pipeline_log` (Chat 104), Node `enricher`
**Verwandt:** `novaberg-lesson_l_pattern-vor-namen-suche.md`, `novaberg-lesson_l_code-vor-doku.md`

---

## 1. Der Fund

Bei der Chat-104-Serie bekamen alle `pipeline_log`-Schreib-Call-Sites zwei neue
Keyword-Argumente (`user_id=…`, `character_id=…`). Sieben Dateien, 36 Call-Sites,
jede einzeln durch Import-Smoke-Test gegangen, jede committet, alles grün.

Der erste echte Turn danach starb sofort nach `ei_calc`:

```
[ERROR] ki_server.event_consumer: Graph-Fehler —
cannot access local variable 'character_id' where it is not associated with a value
```

`UnboundLocalError` in `_enrich_character` (enricher.py). Ursache:

| Zeile | Code |
|-------|------|
| 385 | `span_id = span_start(…, character_id=character_id)` ← **Nutzung** |
| 400 | `character_id: str = state.get("character_id", "")` ← **Bindung** |

Weil `character_id` weiter unten *lokal zugewiesen* wird, ist der Name für die
gesamte Funktion lokal — an Zeile 385 aber noch nicht gebunden. Python wirft
`UnboundLocalError`, nicht `NameError`. Der CharacterGraph starb bei **jedem**
Durchlauf; der HumanGraph (`_enrich_human`, Bindung auf Z. 222, vor allen
Call-Sites) lief unauffällig weiter.

---

## 2. Warum es durchrutschte

**Die Asymmetrie war die Falle.** Von den sieben verkabelten Dateien hatten fünf
das Paar strukturell unkritisch:

| Datei | Herkunft von `character_id` | Reihenfolge-Risiko |
|---|---|---|
| `db_zugriff`, `ei_calc_persist` | `state.get()` **am Node-Kopf** | keins — Bindung vor allem |
| `kzg`, `kzg/speicher` | **Funktions-Argument** | keins — immer gebunden |
| `synapsen_promotion` | lokale Auflösung mitten in der Funktion | **geprüft** — Halb-Paar-Zonen bewusst behandelt |
| `enricher` | lokale Zuweisung mitten in der Funktion | **nicht geprüft** ← der Fehler |

Bei `synapsen_promotion` wurde die Reihenfolge explizit auditiert („liegt der Call
vor oder nach der Auflösung?"), weil die Auflösung sichtbar an einer Closure
(`_hget`) hing — die Abhängigkeit *sah aus wie* ein Problem. Beim `enricher` wirkte
`character_id = state.get("character_id", "")` wie eine triviale Zeile ohne
Abhängigkeit und wurde nicht auf ihre **Position** geprüft. Das Audit lieferte die
Zeilennummer der Bindung (400) *und* die der Call-Sites (u.a. 390) — der Vergleich
wurde schlicht nicht gezogen.

**Die Ironie:** Die harmlos aussehende Variante war die gefährliche. Die
offensichtlich komplizierte wurde geprüft und war sicher.

---

## 3. Warum die Tests es nicht fingen

- **Import-Smoke** (`python -c "import graph.nodes.enricher"`) — grün. Ein
  `UnboundLocalError` entsteht zur **Laufzeit**, beim Betreten des Zweigs, nicht
  beim Import.
- **`compile()` / Syntax-Check** — grün. Es ist kein Syntaxfehler; der Code ist
  wohlgeformt.
- **Linter** hätten es gemeldet (`pyflakes`: *local variable referenced before
  assignment*) — laufen aber nicht in der Kette.
- **Guard-Smoke** des Dispatchers — grün, aber am falschen Node.

Gefunden hat es **der erste echte Turn**. Nichts anderes hätte es gefunden.

---

## 4. Die Lehre

> **Wer eine lokal gebundene Variable an einer bestehenden Call-Site einfügt, prüft
> ihre Bindungs-Position — immer, nicht nur wenn die Bindung kompliziert aussieht.**

Konkret, als Checkliste beim Einfügen von Argumenten in bestehenden Code:

1. **Woher kommt der Wert?**
   - Funktions-Argument → immer gebunden, sicher.
   - Lokale Zuweisung → **Zeilennummer der Bindung gegen die Zeilennummer *jeder*
     Call-Site halten.** Nicht nur gegen die erste.
2. **Liegt eine Call-Site vor der Bindung?** Dann eine von zwei Antworten:
   - **Bindung hochziehen**, wenn sie an nichts hängt (`state.get(…)` hängt nur an
     `state` → frei nach oben ziehbar). Der saubere Fix: eine Quelle, ein Wert.
   - **Konstante/Fallback einsetzen**, wenn die Bindung an vorgelagertem Code hängt
     (Closure, Vorbedingungs-Checks) und nicht hochziehbar ist.
3. **Nie ein Halb-Paar schreiben.** `user_id` gesetzt, `character_id` NULL ist
   schlimmer als beides NULL — es fällt bei `WHERE user_id=… AND character_id=…`
   durchs Raster, statt sauber als „herrenlos" erkennbar zu sein.

**Und für die Abnahme:** Import-Smoke ist die Untergrenze, nicht der Beweis. Bei
Änderungen an Node-internen Bindungen ist **ein echter Turn** das einzige
belastbare Gate. Genau deshalb steht die Live-Abnahme am Ende jedes Sprints — sie
hat hier funktioniert, sofort und eindeutig.

---

## 5. Der Fix

Die Bindung wurde nach oben gezogen, neben `turn_id_log`/`quelle_log`, vor den
ersten `span_start`. Sie hing an nichts außer `state`. Alle Call-Sites tragen jetzt
die echte lokale ID, konsistent — kein Konstanten-Workaround, kein Sonderfall.

Commit: `6e1b950` — *fix(enricher): character_id binding before span_start*.

---

## 6. Anschluss

Ein pattern-basierter Grep über alle Call-Sites bestätigte hinterher die
Vollständigkeit der Verkabelung (36 verkabelt, 1 bewusst NULL, 0 übersehen) — aber
**Vollständigkeit ist nicht Korrektheit**. Der Grep hätte die falsche Reihenfolge nie
gesehen; er zählt Argumente, nicht ihre Gültigkeit. Zwei verschiedene Fragen, zwei
verschiedene Prüfungen:

- *Ist überall etwas eingefügt?* → Grep (`pattern-vor-namen-suche`).
- *Ist das Eingefügte an dieser Stelle gültig?* → Reihenfolge-Audit + echter Turn.

Nebenbefund derselben Prüfung: Auch der Grep brauchte einen zweiten Anlauf. Der
erste (naiver String-Match `user_id=`) meldete 36 Fehlalarme, weil die Codebase die
Argumente ausgerichtet schreibt (`user_id      = user_id`). Erst
`\buser_id\s*=` traf. Auch das ist `pattern-vor-namen-suche` — im Kleinen.
