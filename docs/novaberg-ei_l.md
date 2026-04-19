# 02_L_f — Lesson: Der Blindflug

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Emotionale Intelligenz ohne Sichtbarkeit
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-ei_l.md
**Ursprung:** nova-02-l-f.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 15 (Testlauf "Karrierekrise"), bestätigt Chat 16 (Standard-Routing-Test)
**Betrifft:** API-Response, Session-Annotation, Test-Infrastruktur

---

## 1. Symptom

`emotions_vektor` war bei 200/200 Testlauf-Prompts und 10/10 Standard-Test-Prompts ein leerer String. Die gesamte emotionale Intelligenz — 9 Vektoren, logarithmischer Decay, Arousal-Steuerung — lief intern korrekt, war aber nach außen unsichtbar.

Der Responder wurde korrekt gesteuert (Arousal beeinflusste Antwortlänge, Vektor beeinflusste Ton), aber weder Client noch Test-Runner konnten das verifizieren.

---

## 2. Ursache: Zwei getrennte Lücken

**Lücke 1 — Session-Annotation:** `session_turn_annotate` hatte keinen Parameter `emotions_vektor`. Der Enricher berechnete den Vektor, der Responder nutzte ihn im Prompt, die Salienz schrieb ihn nicht in den Session-Turn. Ein vergessener Parameter bei einer Funktions-Erweiterung.

**Lücke 2 — API-Response:** `GespraechAntwort` hatte nur drei Felder: `antwort`, `modell`, `token_total`. Alle EI- und Routing-Daten (Emotion, Arousal, Vektor, Verlauf, Intent, Momentum, ...) existierten im State, wurden aber am Ausgang verworfen. Der Test-Runner behalf sich mit einem Umweg über den Session-Endpoint — der die Daten auch nicht hatte (wegen Lücke 1).

---

## 3. Lösung

**Lücke 1:** `emotions_vektor` als Parameter an `session_turn_annotate` + Übergabe in `salience.py`.

**Lücke 2:** `GespraechAntwort` um 12 Felder erweitert (emotion, arousal, emotions_vektor, emotions_verlauf, sprach_stil, beziehungs_dynamik, intent, tone, gespraechs_modus, user_intentionen, momentum, needs_web). Synchroner + SSE-Endpoint geben die Daten aus dem State zurück. Test-Runner liest direkt aus der Response.

---

## 4. Generalisierbare Erkenntnis

> **Interne Korrektheit ≠ Sichtbarkeit.** Ein System kann intern perfekt funktionieren und trotzdem für Debugging, Testing und Client-Darstellung blind sein. Die API-Response ist nicht nur für den Endbenutzer — sie ist das Fenster, durch das Test-Infrastruktur und Entwickler das System beobachten.

> **Testen was man nicht sieht ist unmöglich.** Der 200-Prompt-Testlauf (Chat 15) konnte BUG1 entdecken, aber nicht diagnostizieren — weil der Verlauf nicht sichtbar war. Erst mit den 12 Response-Feldern wurde der emotionale Bogen (stress → stabilisierung → hoffnung → zufriedenheit, mit Decay-Gewichten) überprüfbar.

> **Response-Design ist Test-Design.** Wenn die API-Response nur das Minimum enthält, kann der Test-Runner nur das Minimum prüfen. Jedes interne Signal, das für die Qualitätsbewertung relevant ist, muss in der Response stehen — nicht als Luxus, sondern als Grundlage für systematisches Testing.

---

→ BUG1: `novaberg-bugs.md`
→ Emotionale Intelligenz: `04_K`, `04_M_a`
→ Session-Annotation: `memory/session.py`
→ API-Modelle: `api/models.py`
→ Enricher (berechnet Vektor): `01_M_c`
→ Salienz (schreibt Annotation): `01_M_g`
