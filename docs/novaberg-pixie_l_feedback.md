# 05_L_a — Lesson: Feedback-Loop Pixie

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned — Pixie Feedback-Loop
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-pixie_l_feedback.md
**Ursprung:** nova-05-l-a.md
**Typ:** Lesson (L)
**Entdeckt in:** Chat 9 (O9, O9a, O9b)

---

## 1. Was passierte?

Nova recherchierte ein Thema → schrieb die Erkenntnis in ihr eigenes KZG (`kzg:nova:*`) → die hohe Salienz triggerte einen neuen Shadow-Queue-Eintrag → Pixie recherchierte erneut → schrieb wieder ins KZG → endlos. Die Queue `queue:nova` wuchs auf 18+ Einträge und blockierte die Promotion-Queue des Nutzers.

## 2. Ursache

Drei fehlende Schutzmechanismen:

1. **Kein User-Guard:** `kzg_store()` behandelte `user_id="nova"` identisch zu `user_id="meister"` — inklusive Shadow-Queue-Push.
2. **Kein Cooldown:** `nova_gedaechtnis` konnte in jedem Zyklus feuern, auch wenn der letzte Eintrag erst Sekunden alt war.
3. **Kein Queue-Limit:** Die Queue wuchs unbegrenzt.

## 3. Lösung (O9, O9a, O9b)

| Fix | Was | Wo |
|-----|-----|-----|
| **O9b** — Nova-Guard | `user_id == "nova"` → kein Shadow-Queue-Push | `memory/kzg.py` |
| **O9a** — Cooldown | Redis-Cooldown von 600 Sekunden für `nova_gedaechtnis` | `services/shadow_agent/tasks/nova_gedaechtnis.py` |
| **O9** — Queue-Limit | Maximal 20 Einträge pro User, Überschuss per `ltrim` | `memory/kzg.py` |

## 4. Erkenntnis

In einem System mit autonomer Hintergrundverarbeitung ist Selbstverstärkung das gefährlichste Failure-Mode. Wenn ein Agent seine eigenen Outputs als Input empfängt, entsteht ein Feedback-Loop — nicht durch einen Bug, sondern durch korrekte Anwendung der Regeln. Der Guard muss architektonisch erzwungen werden, nicht durch Prompt-Anweisungen.

**Faustregel:** Jeder autonome Prozess, der in denselben Speicher schreibt, aus dem er liest, braucht einen expliziten Self-Feed-Guard.

---

→ Pixie-Konzept: `05_K`
→ KZG (Guard-Implementierung): `02_M_b`
→ Pixie-Tasks: `05_M_a`, Abschnitt 2.8
