# 11_L_a — Lesson: Namens-Identität — Der mentale Anker des Users

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Namens-Entfremdung durch LLM-Extraktion
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-agent-notes_l.md
**Ursprung:** nova-11-l-a.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 22 (AGT2), vertieft Chat 23
**Betrifft:** Alle Agenten mit Speicher-Operationen (Notizen, Timeline, Fakten, Dateien)

---

## 1. Symptom

User: „Merk dir eine Einkaufsliste Baumarkt: Schrauben, Dübel"
→ LLM extrahiert Name: „Einkauf Baumarkt" (statt „Einkaufsliste Baumarkt")

User: „Lösch die Einkaufsliste"
→ Suche findet nur „Einkaufsliste" (exakter Treffer), nicht „Einkauf Baumarkt"
→ Disambiguierung feuert nicht, obwohl zwei relevante Listen existieren
→ Falsche Liste wird ohne Rückfrage gelöscht

Der User hat zwei Einkaufslisten im Kopf. Nova kennt nur eine — weil sie die andere umbenannt hat.

---

## 2. Ursache: Der Name ist die einzige Brücke

In Novas System gibt es keine visuelle UI, keine Icons, keine Farben. Der User interagiert ausschließlich über Sprache. Der **Name** einer Notiz (oder eines Termins, eines Fakts) ist das einzige Merkmal, das User und System teilen.

```
User-Gehirn                    Nova-DB
─────────────                  ──────────
"Einkaufsliste Baumarkt"  →   "Einkauf Baumarkt"  ← LLM hat umbenannt
                     ↓                    ↓
"Lösch die Einkaufsliste" →   find("Einkaufsliste") → kein Match
```

Wenn das LLM den Namen verändert — und sei es nur durch Kürzen, Umformulieren oder „Optimieren" — bricht die Verbindung. Der Gegenstand ist für den User verloren, obwohl er technisch in der DB existiert.

---

## 3. Das tiefere Problem: Zwei Fehler verstärken sich

**Fehler 1 — Speichern:** LLM verändert den Namen (AGT2).

**Fehler 2 — Suchen:** Suche findet veränderte Namen nicht, weil LIKE bei deutschen Komposita versagt. „Einkaufsliste" ist kein Substring von „Einkauf Baumarkt" (Fugen-S trennt das Kompositum).

**Fehler 3 — Suchlogik:** Die dreistufige Suche (Stichwort → LIKE → Volltext) brach nach dem ersten Treffer ab. Bei destruktiven Aktionen (delete/update) fehlten dadurch potentielle Kandidaten — die Disambiguierung wurde nie erreicht.

Jeder Fehler allein wäre verkraftbar. Zusammen machen sie das System unzuverlässig.

---

## 4. Die Lösung: Zwei Prinzipien

### Prinzip 1: User-Wortlaut ist heilig

Was der User sagt, ist der Name. Das LLM darf klassifizieren (Typ, Themen, Zusammenfassung), aber **nicht umbenennen**.

```python
# RICHTIG: management_target hat Vorrang
target_name = state["parameter"].get("target", "")
name = target_name if target_name else notiz_daten.get("name", "")

# FALSCH: LLM entscheidet den Namen
name = notiz_daten.get("name", "")
```

Analogie zum bestehenden Prinzip „Berechnung in Python, nicht im LLM": Der Name ist ein Fakt, keine Interpretation. Fakten kommen vom User, Interpretationen vom LLM.

### Prinzip 2: Suche muss fehlertoleranter sein als Speicherung

Selbst bei korrekt gespeichertem Namen wird der User beim Abrufen ungenau formulieren. „Einkaufsliste" statt „Einkaufsliste Baumarkt". Die Suche muss diesen Abstand überbrücken.

**Lösung: pg_trgm (Trigram-Similarity)**

PostgreSQL-Extension, die Wörter in Dreiergruppen (Trigramme) zerlegt und den Überlappungsgrad berechnet:

```
"einkaufsliste"  → {ein, ink, nka, kau, auf, ufs, fsl, sli, lis, ist, ste}
"einkauf baumarkt" → {ein, ink, nka, kau, auf, ...bau, aum, uma, mar, ark, rkt}

Shared trigrams: {ein, ink, nka, kau, auf} → similarity ≈ 0.35
```

LIKE hätte hier 0 Treffer geliefert (kein Substring-Match). pg_trgm findet die Verbindung über gemeinsame Buchstabengruppen.

### Prinzip 3: Kumulative Suche bei destruktiven Aktionen

Bei `read` reicht der erste Treffer — der User will etwas sehen, nicht wählen.

Bei `delete`/`update`/`append` müssen ALLE potentiellen Kandidaten gesammelt werden, damit die Disambiguierung greifen kann. Die Suche läuft über alle Stufen, dedupliziert über die Notiz-ID:

```
Stufe 1: Exakter Name-Match (ILIKE)     → schnell, präzise
Stufe 2: Trigram-Similarity (pg_trgm)   → fuzzy, findet Komposita
Stufe 3: Volltext-Suche                 → Fallback
→ Zusammenführen, deduplizieren, dann erst entscheiden
```

---

## 5. Geltungsbereich: Über Notizen hinaus

Das Prinzip gilt für **jeden Agenten**, der etwas unter einem Namen speichert:

| Agent | Betroffenes Feld | Risiko |
|-------|-----------------|--------|
| NotizenAgent | `notizen.name` | LLM kürzt Komposita |
| TimelineAgent | `timeline.title` | „Zahnarzttermin" → „Zahnarzt" |
| FaktenAgent | `fakten.subjekt`, `fakten.wert` | Entity-Normalisierung zerstört Varianten |
| DateiAgent | Dateiname / Indexname | LLM-generierte Dateinamen |

**Empfehlung:** Bei der Migration jedes weiteren Agents (Phase 2) prüfen: Kommt der Name vom User oder vom LLM? Wenn vom LLM → User-Wortlaut vorziehen.

---

## 6. Zusammenfassung

| # | Erkenntnis |
|---|-----------|
| 1 | Der Name ist der einzige Identifikator zwischen User und System. Namens-Veränderung = Identitätsverlust. |
| 2 | LLMs „optimieren" Namen — Kürzen, Umformulieren, Zusammenfassen. Das ist in diesem Kontext destruktiv. |
| 3 | LIKE versagt bei deutschen Komposita (Fugen-S, Wortzerlegung). pg_trgm überbrückt diese Lücke. |
| 4 | Suche bei destruktiven Aktionen muss kumulativ sein — alle Stufen, alle Kandidaten, dann disambiguieren. |
| 5 | Das Prinzip gilt systemweit — nicht nur für Notizen. |

---

> „Der Kontext zwischen dem Bild im Gehirn und dem Namen der Liste darf nicht zerstört werden." — Meister, Chat 23

---

→ AGT2-Fix: Chat 23 (management_target als Name)
→ pg_trgm-Integration: Chat 23
→ Disambiguierungs-Pattern: Chat 22 (Abschnitt 4)
→ Prinzip „Berechnung in Python": `05_L_a`
