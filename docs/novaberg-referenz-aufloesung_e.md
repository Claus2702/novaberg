# Novaberg — Referenz-Auflösung (REF-KASKADE) (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-referenz-aufloesung_k.md`](novaberg-referenz-aufloesung_k.md) · Ausarbeitung: [`novaberg-referenz-aufloesung_t.md`](novaberg-referenz-aufloesung_t.md) · Bauplan und Umstellung: [`novaberg-referenz-aufloesung_b.md`](novaberg-referenz-aufloesung_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Ohne eigenen Teil, weil ohne Inhalt: Messungen. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine gezählt. Das Konzept führt keine Entscheidung als solche.

**Übernommen, nicht gezählt:** `_t` §7.1, *„Lösung = Option (b) …, wortgleich: Der Node, der rechnet, lädt seine Daten selbst.“* — eine früher getroffene Bauentscheidung, auf diesen Node übertragen.

---

## B. Offen beim Meister

Keine. §10 führt sieben offene Entscheidungen, und jede hat eine Messung, ein Audit oder einen Live-Test, der sie beantwortet: *„Keine dieser Fragen wird geraten.“*

---

## C. Offen ohne Frage

Offene Punkte, die das Konzept selbst führt:

- `_k` §1.1: der echte Vokabular-Mismatch — *„ein bewusst offener Fall“*.
- `_t` §6, L0: der Lemmatizer — *„Offene Entscheidung, siehe §10“*.
- `_t` §6, L2a: ob der Entity-Layer pro Turn existiert.
- `_t` §6, L3: der Kasten *BLOCKER* — Messung vor Bau (`_b` §8.1).
- `_t` §6, L5: die Voraussetzung, dass der Loop-Fix live abgenommen ist.

Der Abschnitt §10 des ungeteilten Konzepts folgt unverändert.

## 10. Offene Entscheidungen (vor Baubeginn zu klären)

| # | Frage | Blockiert |
|---|---|---|
| 1 | Ist `nomic-embed-text` für deutsche Semantik brauchbar? | **L3 komplett** |
| 2 | Existiert der Entity-Layer pro Turn? | L2a |
| 3 | Lemmatizer: spaCy (schwach bei Plural) oder `simplemma`/`HanTa`? | L0 |
| 4 | Läuft spaCy unter Python 3.12 im Container? | L0 |
| 5 | `n` = wie viele Turns rückwärts? (Vorschlag: 10, aus dem Schatten-Log kalibrieren) | L1–L4 |
| 6 | Kann die Rückfrage (L5) über den bestehenden Pfad? | L5 — **hängt am Loop-Fix Chat 106** |
| 7 | Wo genau wird das Prompt-Embedding berechnet? | Node-Position |

Fragen 2, 4 und 7 beantwortet Brudis Discovery-Audit. Frage 1 beantwortet die
Embedding-Messung. Fragen 3 und 5 beantwortet der Schatten-Lauf. Frage 6 beantwortet der
Live-Test des Loop-Fixes.

**Keine dieser Fragen wird geraten.**

---

## D. Diskussion und verworfene Varianten

Die verworfenen Varianten stehen an ihrer Stelle, mit Grund:

- `_k` §2 — `maverick-coref-de`; nicht übernommen wegen der Lizenz CC BY-NC-SA 4.0, unvereinbar mit Apache 2.0, und weil es nur eine der Schichten löste.
- `_k` §3 — der naive Kaskaden-Entwurf, in dem jede Schicht unabhängig sucht; verworfen, weil er die Arbeit der billigen Schichten verschenkt.
- `_t` §6, L5 — die Rückfrage einer Maschine (*„Kakao oder ein anderes?“*) gegen die spezifische.
- `_t` §7.3 — der Responder mit `prompt_resolved`; ausgeschlossen, sonst redete Nova dem Nutzer Worte in den Mund.
- `_t` §9 — `coreferee`; nur, wenn L1–L4 nachweislich nicht reichen.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code prüfen oder entscheiden lassen — das ist ein eigener Schritt. B1 und B2 stammen aus der Sichtung, B3 ist beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, bisheriger Kopf; `_b` §8.1, §8.2; `_t` §6, L5 | Seit dem 11.07.2026 kein Nachtrag. Ob die Embedding-Messung (§8.1), das Discovery-Audit (§8.2) und der Loop-Fix erledigt sind, steht nirgends | `[gelesen 19.09.2026]` |
| **B2** | `_t` §6, L3, Kasten *BLOCKER* | Der Blocker trifft nach dem eigenen Wortlaut das ganze semantische Gedächtnis (möglicherweise ein englisch-optimiertes Modell), nicht nur L3 | `[gelesen 19.09.2026]` |
| **B3** | `_t` §6, L3; `_b` §8.1; §10, Frage 1 | `novaberg-embedding-casing-blind_k.md` beantwortet die Frage anders: Ursache war das Casing, keine Sprachschwäche (dort §1); das Modell ist auf `nomic-embed-text-v2-moe` gewechselt (§3), `bge-m3` — hier als Ausweg genannt — ist dort verworfen, und §2.1 dort verlangt, REF-KASKADE neu zu bewerten | `[gelesen 19.09.2026]` |

---

## F. Ergänzungen

### Bisheriger Kopf

Der Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Mehrschichtige Referenz-Auflösung vor dem Retrieval
**Stand:** 11. Juli 2026, Chat 106
**Pfad:** `novaberg/docs/novaberg-referenz-aufloesung_k.md`
**Status:** Konzept. Kein Code. Voraussetzungen offen (siehe §10).
