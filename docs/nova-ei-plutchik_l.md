# 02_L_g — Lesson: Arousal-basierter Decay

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Warum positions-basierter Decay nicht ausreicht
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/nova-ei-plutchik_l.md
**Ursprung:** nova-02-l-g.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 16 (Standard-Routing-Test, EI-Analyse)
**Betrifft:** Emotions-Verlauf, Enricher, config.py

---

## 1. Symptom

Im Standard-Routing-Test fiel der Stress einer Kündigung (Arousal 0.8) nach 5 sachlichen Turns aus dem Emotions-Verlauf — genauso schnell wie ein kleiner Ärger (Arousal 0.2). Ein Mensch, dem gerade gekündigt wurde und der dann Termine regelt, ist nicht emotional neutral — er funktioniert. Das System behandelte beide gleich.

---

## 2. Ursache: Positions-basierter Decay

Der ursprüngliche Decay kannte nur die *Position* eines Turns, nicht seine *Intensität*:
```
decay = 1.0 / (1.0 + 0.8 × log₁₀(1 + position))
```

Turn 5 hat immer Gewicht 0.62 — egal ob die Emotion ein Todesfall oder ein Regenschauer war. Der Arousal-Wert existierte im System (Perzeption berechnet ihn korrekt), wurde aber im Decay nicht genutzt.

---

## 3. Lösung: Arousal moduliert den Decay-Faktor
```
effective_decay = DECAY_FACTOR × (1.0 - arousal × PERSISTENCE)
decay = 1.0 / (1.0 + effective_decay × log₁₀(1 + position))
```

Hoher Arousal → niedrigerer effective_decay → langsamerer Verfall. Der Config-Wert `EI_AROUSAL_PERSISTENCE` (Default: 0.6) steuert die Stärke des Effekts.

Gleichzeitig wurde das Fenster von 15 auf 100 Turns erweitert (gesamte Session). Der arousal-basierte Decay regelt organisch, was davon noch Gewicht hat. Kleine Emotionen verschwinden nach wenigen Turns. Große halten die gesamte Session durch — wie ein Grundrauschen, das auch durch sachliche Turns hindurch spürbar bleibt.

---

## 4. Differenzierte Fenster

Nicht alles profitiert von einem großen Fenster:

| Berechnung | Fenster | Begründung |
|-----------|---------|------------|
| Emotions-Verlauf | 100 (Session) | Grundstimmung, Decay regelt Gewicht |
| Emotions-Vektor | 8 | Richtungswechsel, muss reaktiv sein |
| Sprachstil | 5 | Aktuelle Formulierung, ändert sich schnell |

---

## 5. Generalisierbare Erkenntnis

> **Decay ohne Intensität ist wie Vergessen ohne Bedeutung.** Ein Mensch vergisst einen Regenschauer schneller als einen Todesfall — nicht weil mehr Zeit vergangen ist, sondern weil der Regenschauer weniger Bedeutung hatte. Jedes Vergessens-Modell, das nur die Zeit berücksichtigt (Position im Verlauf), verfehlt diese fundamentale Asymmetrie.

> **Arousal ist das Äquivalent zur neurochemischen Intensität.** Dopamin, Cortisol, Adrenalin — sie alle modulieren, wie tief ein Ereignis encodiert wird und wie langsam es verblasst. `EI_AROUSAL_PERSISTENCE` ist Novas Version davon. Kein Neurotransmitter, aber die gleiche Wirkung: Starke Erlebnisse hallen nach.

> **Funktionieren ist nicht Vergessen.** Fünf sachliche Turns nach einer Kündigung bedeuten nicht, dass die Kündigung verdaut ist. Der Mensch funktioniert — Einkaufsliste, Termine, Alltag — aber die Grundstimmung bleibt. Das System muss das abbilden: Warmer Ton bei der Einkaufsliste, nicht robotische Sachlichkeit.

---

→ Ebbinghaus-Decay: `02_T_a`
→ Enricher (berechnet Verlauf): `01_M_c`
→ Emotionale Intelligenz: `04_K`, `04_M_a`
→ Config: `EI_AROUSAL_PERSISTENCE`, `EMOTION_MAX_TURNS`, `EMOTION_VEKTOR_TURNS`, `STIL_ANALYSE_TURNS`
→ Lesson Blindflug: `02_L_f`
