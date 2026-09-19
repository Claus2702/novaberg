# Novaberg — Pixie-Graph-Merge (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-pixie-graph-merge_k.md`](novaberg-pixie-graph-merge_k.md) · Ausarbeitung: [`novaberg-pixie-graph-merge_t.md`](novaberg-pixie-graph-merge_t.md) · Bauplan und Umstellung: [`novaberg-pixie-graph-merge_b.md`](novaberg-pixie-graph-merge_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine Entscheidung mit Urheber.

**Im Text als Bauentscheidung geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §2, Kasten *„Abweichung, gebaut …“*: Umgesetzt ist nicht die zweite Instanz auf CPU, sondern der Weg über die vorhandene Event-Infrastruktur in dieselbe Instanz, mit Begründung (*„Warum so“*).

---

## B. Offen beim Meister

Keine offene Frage dieser Art.

**Offen ohne Frage an den Meister** — Punkte, die das Konzept selbst als offen führt:

- Abschnitt D (§6.1 bis §6.5): Session-Vermischung, Salienz-Bias für Pixie-Ergebnisse, Thinker-Tools, gleichzeitiger Pixie- und Chat-Lauf, Queue-Duplikat-Prüfung (zur Hälfte beantwortet am 15.08.2026).
- `_t` §2, Kasten: *„Die Trennung GPU/CPU nach Pfad ist nicht gebaut. … Ob das reicht, ist nicht gemessen.“*

---

## C. Diskussion und verworfene Varianten

Die überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten:

- `_k` §1 — die durchgestrichene Liste der sieben fehlenden Nodes; erledigt, der Impuls durchläuft den vollen CharacterGraph.
- `_t` §2 — die zweite CharacterGraph-Instanz auf CPU; nicht gebaut, ersetzt durch den Weg über den Event-Consumer. Der Abschnitt beschreibt laut Kasten *„weiterhin einen moeglichen Ausbau, keinen erledigten Stand“*.
- Abschnitt D, §6.4 — der Name `llm_lock`; umbenannt am 25.08.2026 in `graph_run_lock`.
- Abschnitt D, §6.5 — die Prüfung gegen *„die letzten N Eintraege“*; ersetzt durch Gleichheit von `aufgabe` + `thema` über einen Index. Der Embedding-Vergleich ist in `novaberg-queue-verfall_k.md` §6.1 als zweiter Schritt ausgeschlossen.

---

## D. Aus dem Konzept: offene Design-Fragen

§6 steht hier ganz, mit seinen zwei Nachtragskästen, weil `_e` die offenen Fragen sammelt.

## 6. Offene Design-Fragen

### 6.1 Session-Vermischung

Pixie-Durchlaeufe erzeugen Session-Turns (Dispatcher schreibt). Diese Turns erscheinen in der Session neben User-Chat-Turns. Brauchen wir ein Flag `turn_source: "pixie"` um sie im Client unterscheidbar zu machen?

### 6.2 Salienz fuer Pixie-Ergebnisse

Der Salienz-Node bewertet die Speicherwuerdigkeit des Pixie-Ergebnisses. Aber Pixie-Recherchen sind per Definition speicherwuerdig (sonst waere nicht recherchiert worden). Braucht der Salienz-Node einen Bias fuer `event_source=character`?

### 6.3 Thinker-Tools bei Pixie

Der Thinker nutzt `timeline_check`, `memory_search`, `web_search`. Bei Recherche-Ergebnissen ist `web_search` im Thinker redundant (Recherche hat schon gesucht). Braucht der Thinker eine reduzierte Tool-Liste fuer Pixie-Durchlaeufe?

### 6.4 Concurrent Pixie + Chat

Was passiert wenn ein User chattet waehrend Pixie gerade einen PixieGraph-Durchlauf macht? Beide schreiben in dieselbe Session. Der Chat-Pfad hat den `graph_run_lock` (GPU). Pixie laeuft auf CPU — kein Lock-Konflikt. Aber Session-Writes koennten sich ueberlappen. Loesung: Dispatcher schreibt atomar (einzelner Redis-Call), Session-Reihenfolge durch Timestamp.

> **Umbenannt am 25.08.2026: `llm_lock` heisst jetzt `graph_run_lock`.** Der Name sagte *Sperre vor dem Sprachmodell* und meinte *ein Graphenlauf zur Zeit*; seit dem Vormittag desselben Tages traegt `services/llm_riegel.py` den echten Modell-Riegel, und die Verwechslung waere teuer geworden.

### 6.5 Queue-Duplikat-Pruefung

RECH-SPIRAL entsteht, weil die Queue keine Themen-Aehnlichkeit prueft. Im PixieGraph wuerde der Thinker die Qualitaet pruefen, aber die Queue-Insertion passiert VOR dem Graph-Durchlauf. Braucht `shadow_queue_push` einen Embedding-Vergleich gegen die letzten N Eintraege?

> **Zur Haelfte beantwortet am 15.08.2026.** `shadow_queue_push` prueft seither auf **Gleichheit** von `aufgabe` + `thema` und verstaerkt den vorhandenen Auftrag, statt einen zweiten anzulegen — die Queue liegt seit dem Umzug als Tabelle `shadow_auftrag` vor, und der Vergleich laeuft ueber einen Index statt ueber „die letzten N Eintraege".
>
> **Der Embedding-Vergleich fehlt weiterhin, und er ist der Teil, der diese Spirale trifft:** Sie entsteht aus *verwandten* Themen, nicht aus identischen. Er braucht eine gemessene Schwelle auf einer benannten Paarung und ist in `novaberg-queue-verfall_k.md` §6.1 ausdruecklich als zweiter Schritt ausgeschlossen.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B3 stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Bisheriger Kopf*, Feld **Status** | *„Konzept“*; `_k` §1 (*„Sieben von sieben erledigt“*) und `_t` §2 (Kasten *„Abweichung, gebaut …“*) führen einen Teil als gebaut, auf abweichendem Weg | `[gelesen 19.09.2026]` |
| **B2** | `_t` §2 (Pixie-Pfad) und §2.4 | Provider `gemma4-cpu` und `qwen3-32b-cpu` auf Port 11435; laut `novaberg-microservice-modell-queue_k.md` sind diese Provider gelöscht | `[gelesen 19.09.2026]` |
| **B3** | `_b` §3, Zeile `services/shadow_delivery.py` | *„Entfaellt“*; der gebaute Weg (`_t` §2, Kasten) benutzt gerade die Shadow-Delivery, die das Event feuert | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Stand:** 8. Mai 2026, Chat 79
**Status:** Konzept
**Abhaengigkeiten:** Event-Modell (Chat 60), CharacterGraph (Pfad 2), Pixie-Heartbeat (Chat 33+)
