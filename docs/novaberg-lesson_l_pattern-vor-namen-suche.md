# Novaberg — Lesson: Pattern-Suche vor Namen-Suche

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Architektur-Audits müssen das Aufruf-Pattern suchen, nicht nur den Wrapper-Namen
**Stand:** 20. Mai 2026, Chat 92
**Pfad:** novaberg/docs/novaberg-lesson_l_pattern-vor-namen-suche.md
**Kategorie:** Architektur — Audit-Disziplin bei Migrationen
**Schwester-Lessons:** `novaberg-lesson_l_async-bruecken.md`, `novaberg-lesson_l_loop-binding.md` (beide aus demselben Block-1-Sprint)
**Konzept-Bezug:** `novaberg-microservice-modell-queue_k.md`
**Handbuch-Bezug:** `DEVELOPER_HANDBOOK.md` §1 EVA-Disziplin

---

## 1. Der Vorfall

Block 1 der Microservice-Welle begann mit einer Inventur. Phase 1 sollte alle Stellen im Codebase finden, die ein Embedding erzeugen, damit die Migration auf den zentralen EmbedWorker keine Stelle übersieht. Brudi lieferte eine saubere Tabelle: 24 Aufruf-Stellen, getrennt nach den zwei bekannten Wrapper-Funktionen `embedding_create` (16 Aufrufer) und `embedding_manager.embed` (8 Aufrufer). Die Inventur galt als vollständig. Auf ihrer Basis wurde der gesamte Sprint geplant — acht Migrations-Gruppen G1 bis G6, plus Cleanup.

Sie war nicht vollständig.

In G4 fiel der erste übersehene Aufruf auf: `services/pixie/stack.py:38` erzeugte ein Embedding direkt über `embed_client.embed(model=..., input=...)["embeddings"][0]` — ohne den Umweg über eine der zwei Wrapper-Funktionen. Brudi entdeckte ihn nur, weil er beim RechercheAgent-Audit den `stack_push`-Aufrufer-Pfad mitverfolgte. Die Stelle wanderte als ungeplanter Sprint G7 nach.

In G7 fiel der zweite auf: `services/shadow_delivery.py:165`, ebenfalls direkter `embed_client.embed`-Call. Diesmal nicht in einem Legacy-Pfad, sondern im Live-Code — importiert von `main.py` und `api/chat.py`, also auf jedem Server-Start aktiv. G8 wurde nötig.

Zwei übersehene Stellen, zwei ungeplante Zusatz-Sprints. Der Sprint, der mit G6 enden sollte, endete mit G8.

## 2. Die Ursache

Die Audit-Lücke war kein Brudi-Fehler. Brudi hatte exakt das gesucht, was im Phase-1-Prompt stand — die zwei Wrapper-Funktionsnamen:

```bash
grep -rn "embedding_create\|embedding_manager" novaberg/server/
```

Die Lücke war im Audit-Plan. Phase 1 folgte der unausgesprochenen Annahme: „Embedding-Calls laufen immer über die Wrapper-Funktion." Diese Annahme war falsch. Zwei Stellen im Codebase benutzten die darunterliegende Ollama-API direkt — `embed_client.embed(...)` — ohne den Wrapper. Wer das Pattern direkt benutzte, fiel durch das namens-basierte Raster.

Warum gab es überhaupt Direkt-Aufrufe? Keine böse Absicht. `stack_push` und `shadow_delivery._gespraechs_embedding` waren historisch gewachsen, vermutlich aus einer Zeit, in der die Wrapper-Funktion noch nicht existierte oder nicht praktisch erreichbar war. Solche Umgehungen entstehen ständig: aus Performance-Optimierungen, aus Inline-Tests, aus Refactor-Etappen, in denen eine Stelle nicht mit-migriert wurde. Sie sind nicht falsch — aber sie umgehen die Abstraktion, und genau deshalb übersieht sie ein namens-basiertes Audit.

Der entscheidende Punkt: Beide übersehenen Stellen trugen denselben Silent-Skip-Bug — bei Embedding-Fehler wurde ein leerer Vektor `[]` zurückgegeben statt eine Exception zu werfen. Hätte die Migration sie nicht gefunden, wären sie nach Abschluss von Block 1 als unsichtbare Defekte im Code geblieben — in der Annahme, „alle Embedding-Pfade laufen jetzt sauber über den Worker." Das wäre eine falsche Gewissheit gewesen.

## 3. Die strukturelle Lösung

Der Verifikations-Grep in G8 wurde um das **Aufruf-Pattern** erweitert, nicht nur den Wrapper-Namen:

```bash
# Phase-1-Suche (Namen-basiert, unvollständig):
grep -rn "embedding_create\|embedding_manager" novaberg/server/

# G8-Suche (Pattern-basiert, vollständig):
grep -rn "embed_client\.embed\|\.embed(model=\|\.embed(input=" novaberg/server/ \
  | grep -v "model_services"
```

Die zweite Suche hätte beide übersehenen Stellen schon in Phase 1 gefunden. Nach Abschluss von Block 1 lieferte sie null Treffer im Anwendungscode — der EmbedWorker ist die einzige Stelle, die das Ollama-Embedding-Pattern direkt benutzt.

## 4. Das Prinzip

### Pattern-Suche vor Namen-Suche bei Architektur-Audits

Ein Audit, das die zu migrierende Schicht nur über Funktions- und Klassennamen erfasst, übersieht alle Stellen, die diese Schicht umgehen. Wer eine Abstraktions-Schicht (Wrapper, Manager, Service) ablösen will, muss nach zwei Dingen suchen:

1. **dem Namen der Wrapper-Schicht** — `embedding_create`, `embedding_manager.embed`
2. **dem darunterliegenden API-Aufruf-Pattern** — `embed_client.embed(...)`, `.embed(model=`, `.embed(input=`

Die erste Suche findet die ordentlichen Konsumenten. Die zweite findet die, die die Abstraktion umgehen. Beide zusammen ergeben das vollständige Bild. Der zweite Schritt kostet drei Minuten; fehlt er, kostet die Lücke Tage — im Block-1-Fall zwei ungeplante Sprints.

Das Prinzip gilt nicht nur für Embedding. Jede künftige Modell-Schicht-Migration (Block 2 für LLM-Calls, Block 5 für `num_ctx`) muss in Phase 1 explizit pattern-basiert auditieren. Wer `provider.chat()` ablöst, sucht auch nach `ollama_client.chat(`, `client.generate(` und dem Roh-HTTP-Pattern. Wer eine Datenbank-Schicht ablöst, sucht nach dem direkten `cursor.execute(` neben dem ORM-Methodennamen.

## 5. Die Konsequenz

**Erstens:** Die Audit-Disziplin im Entwicklerhandbuch wird ergänzt. Wer eine Migration plant, prüft die zu ersetzende Schicht zweifach — Wrapper-Namen und Aufruf-Pattern. Der zweite Grep gehört in jeden Phase-1-Audit-Prompt.

**Zweitens:** Block 2 und Block 5 der Microservice-Welle werden ihre Inventur pattern-basiert beginnen. Der Phase-1-Prompt für die LLM-Konsolidierung enthält von vornherein die Suche nach dem darunterliegenden Provider-Aufruf-Pattern, nicht nur nach den Wrapper-Funktionsnamen.

**Drittens:** Diese Lesson dient als Archiv. Wer in einem Jahr fragt, warum die Audit-Greps zwei Suchmuster verwenden, liest hier nach. Die zweite Suche wirkt redundant, bis man sich an die zwei ungeplanten Sprints erinnert, die sie verhindert hätte.

## 6. Der Preis

Zwei ungeplante Sprint-Phasen (G7 und G8). Beide klein, beide sauber durchziehbar, aber beide vermeidbar, wenn Phase 1 von Anfang an pattern-basiert gesucht hätte. Der eigentliche Preis liegt im Risiko, das beinahe realisiert worden wäre: Hätte Brudi die beiden Direkt-Aufrufe nicht durch sorgfältiges Mitverfolgen der Aufrufer-Pfade gefunden, wären sie als Silent-Skip-Defekte im Code geblieben — und die Gewissheit „Block 1 hat alle Embedding-Pfade konsolidiert" wäre falsch gewesen. Eine falsche Gewissheit über eine abgeschlossene Migration ist teurer als eine bekannte offene Stelle, weil niemand mehr danach sucht.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_async-bruecken.md`, `novaberg-lesson_l_loop-binding.md`
→ Konzept-Dokument: `novaberg-microservice-modell-queue_k.md`
→ Handbuch-Bezug: `DEVELOPER_HANDBOOK.md` §1 EVA-Disziplin
