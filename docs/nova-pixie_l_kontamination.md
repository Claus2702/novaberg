# 05_L_b — Lesson: Session-Kontamination durch Delivery

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned — Session-Kontamination durch Shadow Delivery
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-pixie_l_kontamination.md
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

Das ist ein Spezialfall des generellen Kontaminations-Prinzips aus `01_L_a`: Bewertende (oder generierende) Agenten verfälschen ihr Ergebnis, wenn sie kontextfremde Information sehen — auch wenn sie angewiesen werden, diese zu ignorieren.

---

→ Pixie-Konzept: `05_K`
→ Queue, Stack & Delivery: `05_T_a`
→ Enricher (filtert Shadow-Turns): `01_M_c`
→ Lesson: Kontextuelle Kontamination: `01_L_a`
