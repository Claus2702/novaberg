# Novaberg — Dual-Emotion Phase 2: Novas Emotionsstrang (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-ei-dual-emotion_k.md`](novaberg-ei-dual-emotion_k.md) · Ausarbeitung: [`novaberg-ei-dual-emotion_t.md`](novaberg-ei-dual-emotion_t.md) · Bauplan und Umstellung: [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine. Das Konzept führt keine Entscheidung.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §4.2, Kasten *„Abgrenzung zum Raumzug“*: *„Wer die α-Tabelle oben fürs Register abschreibt, baut das Gegenteil dessen, was entschieden wurde.“* Die Entscheidung betrifft das Register und steht in `novaberg-gv-strategie_k.md` §3.4, nicht hier.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine offene Frage, die eine Entscheidung verlangt.

**Offen, ohne eine Entscheidung zu verlangen:**

- [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md) §10, Arbeitspaket 8: die Client-Panels (*„Client-Panels offen“*).
- [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md) §11, *Phase 3*, und `_t` §4.3: der Ziel-Vektor als dritte Kraft.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, mit Marke und Grund:

- `_t` §6 — der asynchrone Block; *„Veraltet“*, ersetzt durch das Event-Modell. Ebenso die Arbeitspakete 4 bis 7 in `_b` §10.
- `_b` §11, *TurnOrchestrator (überholt)* — der sternförmige Orchestrator; *„konzeptionell überholt“* durch zwei Graphen mit Event-Queue.
- `_b` §10, Arbeitspaket 6 — eine eigene Salienz(Nova); *„nicht nötig“*.
- `_b` §10, Nachträge *Akkumulationsrefactor + Perzeption-Symmetrie*, Punkt 2 — die einfache Decay-Summierung; ersetzt durch drei Mechanismen der Akkumulation.
- `_t` §6.3 und §7 — der flache State-Key `nova_emotions_vektor`; existiert seit dem Personality-Umbau nicht mehr.
- `_t` §4.2, Kasten — die α-Tabelle als Vorlage für das Register; ausdrücklich abgegrenzt, weil das Vorzeichen sich umkehrt.

---

## D. Aus dem Konzept

Keiner. Das Konzept hat keinen Abschnitt mit offenen Punkten.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder eine Entscheidung einholen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung, B5 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, bisheriger Kopf, Feld **Stand** | Der Kopf nennt den 28.07.2026; [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md) §10 (Nachträge *Akkumulationsrefactor + Perzeption-Symmetrie*, Punkt 2) trägt Änderungen vom 31.08.2026 | `[gelesen 19.09.2026]` |
| **B2** | `_t` §2 (asynchroner Teil des Kreislaufs), [`novaberg-ei-dual-emotion_b.md`](novaberg-ei-dual-emotion_b.md) §8.2 | Beide beschreiben den asynchronen Block, den `_t` §6 als veraltet markiert — ohne eigene Marke | `[gelesen 19.09.2026]` |
| **B3** | `_t` §5 | Nova-Daten liegen in einer eigenen `user_id`-Partition (`ASSISTANT_USER_ID`, *„nova“*); das geltende Paar-Schema (`novaberg-convention-paar-schema.md` §2) setzt `user_id` = der Mensch, `character_id` = die Figur | `[gelesen 19.09.2026]` |
| **B4** | Abschnitt F, bisheriger Kopf, Feld **Typ** | *„Konzept (K)“* statt `_k` | `[gelesen 19.09.2026]` |
| **B5** | `_t` §9, *Status* | Der Block werde aus `nova_emotions_vektor` zusammengebaut; `_t` §6.3 und §7 sagen, ein flacher State-Key dieses Namens existiert seit dem Personality-Umbau nicht mehr | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

Der bisherige Kopf und die bisherige Schlusszeile des ungeteilten Konzepts, ungekürzt. Beide tragen keinen Messwert und stehen deshalb hier.

### Bisheriger Kopf

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Dual-Emotion Phase 2
**Stand:** 28. Juli 2026, Chat 114 (Abgrenzung zum Raumzug in §4.2)
**Pfad:** novaberg/docs/novaberg-ei-dual-emotion_k.md
**Typ:** Konzept (K)
**Voraussetzung:** Phase 1 (User-ID-Entkopplung, Chat 57) ✅
**Grundlage:** novaberg-thinking-drive_k.md §4 (Dual-Emotion-Architektur)

---

### Bisheriger Schluss

*Konzept erstellt 19. April 2026, Chat 58. Aktualisiert Chat 66 (AP9 Doku-Abschluss). Grundlage: novaberg-thinking-drive_k.md §4 (Chat 53), Phase 1 User-ID-Entkopplung (Chat 57), Enricher-Analyse (Chat 58). Akkumulationsrefactor + Perzeption-Symmetrie Chat 61. [EIGENE_EMOTION]-Block im Responder live.*
