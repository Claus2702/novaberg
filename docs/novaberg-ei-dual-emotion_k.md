# Novaberg — Dual-Emotion Phase 2: Novas Emotionsstrang

**Absicht:** Nova hat je Turn einen eigenen Emotionsstrang in denselben acht Plutchik-Dimensionen wie der Nutzer: Er entsteht aus ihrem vorherigen Zustand mit Abklingen und aus asymmetrischer Empathie zum Nutzer, wird getrennt vom Nutzer gespeichert und färbt ihre Antwort, ohne sie zu diktieren.
**Stand:** 31. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Dual-Emotion Phase 1* 🟢 · *Dual-Emotion Phase 2* 🟠 · *Dual-Emotion Phase 3* 🟠 · *TurnOrchestrator* ⚫ — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-ei-dual-emotion_t.md`](novaberg-ei-dual-emotion_t.md) · [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md) · [`novaberg-ei-dual-emotion_e.md`](novaberg-ei-dual-emotion_e.md) · Messungen (`_m`): keiner
**Entschieden:** 0 · **Offen beim Meister:** 0 (Liste in [`novaberg-ei-dual-emotion_e.md`](novaberg-ei-dual-emotion_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-ei-dual-emotion_k.md §4.2` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-ei-dual-emotion_t.md`](novaberg-ei-dual-emotion_t.md), `_b` ist [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md), `_e` ist [`novaberg-ei-dual-emotion_e.md`](novaberg-ei-dual-emotion_e.md).

| § | Datei |
|---|---|
| Titelzeile, Kopfblock, Tabelle | `_k` |
| 1 | `_k` |
| 2 | `_t` |
| 3 · 3.1 · 3.2 · 3.3 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 · 4.4 | `_t` |
| 5 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 · 6.4 · 6.5 · 6.6 | `_t` |
| 7 | `_t` |
| 8 · 8.1 · 8.2 · 8.3 | `_b` |
| 9 | `_t` |
| 10 (mit den Nachträgen *Akkumulationsrefactor + Perzeption-Symmetrie*) · 11 (mit *Phase 3*, *TurnOrchestrator*) | `_b` |
| 12 | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Voraussetzung, Grundlage) | `_e` |
| bisherige Schlusszeile (*Konzept erstellt …*) | `_e` |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Motivation

Nova hat heute keine eigenen Emotionen pro Turn. Sie hat eine destillierte emotionale Grundstimmung (`nova_emotions` — die fünfte IDENTITAET-Schicht seit Chat 52), aber das ist ein strategisches Langzeit-Profil aus der Pixie-Destillation. Pro Turn ist Nova emotional blind — sie spiegelt den User, hat aber kein eigenes Momentum.

Phase 2 gibt Nova einen eigenen Emotionsstrang mit denselben 8 Plutchik-Dimensionen wie der User. Jede Antwort, die Nova gibt, wird analysiert — Emotion, Arousal, Modus, Intent. Diese Daten fließen ins Gedächtnis unter `ASSISTANT_USER_ID` und werden im nächsten Turn geladen, um Novas emotionalen Zustand zu berechnen.

**Kernprinzip:** Der Eingangspfad für den User ist der Ausgangspfad für Nova. Dieselben Nodes, dieselben Funktionen, andere Eingabedaten.

---

> **Hinweis zur Aufteilung (19.09.2026):** §2 bis §7 und §9 stehen in [`novaberg-ei-dual-emotion_t.md`](novaberg-ei-dual-emotion_t.md), §8, §10 und §11 in [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md).

---

## 12. Prinzipien

> **"Der Eingangspfad für den User ist der Ausgangspfad für Nova."** — Dieselben Nodes, dieselben Funktionen, andere Eingabedaten.

> **"Berechnung in Python, nicht im LLM."** — EI-Calc ist reine Vektorarithmetik. Kein LLM-Call für die Emotions-Berechnung.

> **"Daten vollständig transportieren, Formatierung am Konsumenten."** — Der State trägt User-Daten und Nova-Daten parallel, getrennt gespeichert nach `user_id`.

> **"Speichern ist billig, Vergessen ist intelligent."** — Novas KZG speichert ihre Aussagen. Was irrelevant ist, verfällt über Decay.

---
