# 05_L_b — Lesson: Session-Kontamination durch Delivery

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned — Session-Kontamination durch Shadow Delivery
**Stand:** 24. August 2026 (§5 bestritten — die Ausblendung kostet den Anlass; gewählt ist wieder eine Markierung, siehe dort); davor 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-pixie_l_kontamination.md
**Ursprung:** nova-05-l-b.md
**Typ:** Lesson (L)
**Entdeckt in:** Chat 7

---

## 1. Was passierte?

Nova begann im regulären Chat Sätze zu verwenden wie „Hey! Ich hab gerade über Quantencomputing nachgedacht..." — obwohl der Nutzer etwas völlig anderes gefragt hatte. Nova imitierte ihre eigenen Shadow-Delivery-Impulse.

## 2. Ursache

Shadow-Delivery-Turns wurden als reguläre Assistant-Turns in der Session gespeichert. Der Enricher destillierte diese Turns und reichte sie an den Responder weiter. Das LLM sah die Shadow-Impulse als Beispiele für gute Antworten und kopierte Stil und Muster.

**Kontaminationskette:**
```
Pixie → Shadow Delivery → WebSocket → Session-Turn (rolle: "assistant")
    → Enricher destilliert → Responder sieht den Turn → imitiert das Pattern
```

## 3. Lösungsweg (drei Iterationen)

| Iteration | Ansatz | Ergebnis |
|-----------|--------|----------|
| 1 | `[Nova-Impuls]`-Prefix vor Delivery-Turns | LLM kopierte den Prefix, eckige Klammern tauchten in Antworten auf |
| 2 | Destillierte Turns mit „(Nova hatte einen eigenen Gedanken zum Thema: X)" | Besser, aber LLM übernahm trotzdem das „Gedanken zum Thema"-Pattern |
| 3 | `continue` im Enricher — Shadow-Turns komplett ausblenden | Kontamination verschwunden |

## 4. Finale Lösung

Der Enricher erkennt Shadow-Impuls-Turns und überspringt sie bei der Destillation. Das LLM sieht sie nie. Was das LLM nicht sieht, kann es nicht kopieren.

## 5. Erkenntnis

**Das LLM kann nichts kopieren, was es nicht sieht.** Das klingt trivial, aber die Implikation ist tiefgreifend: In einem System, in dem ein LLM seine eigenen früheren Outputs als Kontext bekommt, verstärkt sich jeder Stilfehler exponentiell. Die einzige sichere Lösung ist nicht Markierung, nicht Anweisung, sondern Ausblendung.

> **Der letzte Satz ist am 24.08.2026 bestritten, und zwar durch die Kosten der Ausblendung.** Sie hat einen Preis, den diese Lesson nicht kannte: Wird der Impuls ausgeblendet, fehlt der **Anlass** für alles, was danach kommt — Nova schrieb einen Vorschlag, den sie selbst gemacht hatte, dem Nutzer zu (`novaberg-bugs.md` → `IMPULS-FAELLT-AUS-DEM-VERLAUF`). Gewählt ist deshalb wieder eine **Markierung**, also Iteration 2, die hier als gescheitert steht.
>
> **Zwei Unterschiede zu Iteration 2, und beide sind Hypothesen, keine Messungen.** Damals stand die Annotation **im Text des Turns** — *„(Nova hatte einen eigenen Gedanken zum Thema: X)"* —, also an einer Stelle, die das Modell als Teil der Äußerung liest. Heute steht sie in der **Sprecherzeile**, in demselben Feld wie `USER:` und `NOVA:`, das ein Modell bereits als Rahmen und nicht als nachzuahmenden Inhalt behandelt. Und der Filter, dessen Wirkung Iteration 3 zugeschrieben wird, **hat seit Chat 110 nie gefeuert** — die Kontamination verschwand also aus einem Grund, den niemand nachgemessen hat.
>
> **Was es entscheidet:** Taucht `(von sich aus)` in Novas eigenen Antworten auf, war diese Lesson im Recht und die Markierung fällt wieder. Bis dahin ist sie **bestritten, nicht widerlegt** — und die Beweislast liegt bei der neuen Lösung.

Das ist ein Spezialfall des generellen Kontaminations-Prinzips aus `01_L_a`: Bewertende (oder generierende) Agenten verfälschen ihr Ergebnis, wenn sie kontextfremde Information sehen — auch wenn sie angewiesen werden, diese zu ignorieren.

---

→ Pixie-Konzept: `05_K`
→ Queue, Stack & Delivery: `05_T_a`
→ Enricher (filtert Shadow-Turns): `01_M_c`
→ Lesson: Kontextuelle Kontamination: `01_L_a`
