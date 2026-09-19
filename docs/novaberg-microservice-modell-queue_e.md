# Novaberg — Microservice-Modell-Queue (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-microservice-modell-queue_k.md`](novaberg-microservice-modell-queue_k.md) · Ausarbeitung: [`novaberg-microservice-modell-queue_t.md`](novaberg-microservice-modell-queue_t.md) · Bauplan und Umstellung: [`novaberg-microservice-modell-queue_b.md`](novaberg-microservice-modell-queue_b.md) · Messungen: [`novaberg-microservice-modell-queue_m.md`](novaberg-microservice-modell-queue_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden. Einen Abschnitt D gibt es hier nicht, weil kein Abschnitt des Konzepts hierher gewandert ist.

---

## A. Entschieden

Die Entscheidungen stehen in den Abschnitten, die sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_b` §8, Punkt 1 *Connector-Switch*; `_b`, *Bisheriger Schluss* | Aktivierung über die Umgebung, nicht über den Code-Default: *„Der `config.py`-Default bleibt bewusst `gemma4` — er ist der Fallback-Anker für den Standard-Betrieb ohne Env, nicht der aktive Schalter.“* | Mai 2026 — der Abschnitt nennt kein Datum |
| **E2** | `_b`, *Bisheriger Schluss* | *„Neuer BackgroundWorker-Submit-Timeout-Default 300 s (Variante B: Worker-Instanz-Default per Konstruktor, pro Call überschreibbar — Chat/Embed behalten 60 s)“* | Mai 2026 — die Zeile nennt kein Datum |
| **E3** | `_b` §8, Punkt 4; `_b`, *Bisheriger Schluss* | Die alten CPU-Modelle werden gelöscht, zuletzt und erst nach verifiziertem Background-Pfad — *„Alte CPU-Modelle nach verifiziertem Background-Pfad gelöscht (~105 GB frei)“* | Mai 2026 — der Abschnitt nennt kein Datum |

Der Wortlaut der Entscheidungen steht in keinem der Abschnitte; alle drei geben sie als Ergebnis wieder.

**Im Text als Wahl geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_b` §7: die Reihenfolge der Blöcke, Block 5 vor Block 4, mit Begründung je Schritt.
- `_t` §5: *„`background` ersetzt zwei alte Modelle“*; *„Pixie nutzt nachts keine GPU.“*
- `_m` §9a: `F-FRIST-1` registriert — der Vorgabewert wird nach der langsamsten Aufgabe bemessen, die ihn erbt.
- `_m` §9b: der Worker meldet wirkungslose Parameter und entfernt sie nicht.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage an den Meister.

**Offen ohne Frage an den Meister** — was das Konzept selbst als offen führt:

- `_b` §6.5: *„die einzelnen Call-Site-Overrides (kurze Klassifikation `num_ctx=4096` etc.) sind ein separater Folgeschritt“*.
- `_t` §5: *„Mittelfristig fallen die zwei Variablen zusammen“*; der Pixie-Output-Queue-Pfad *„im Backlog“*.
- `_b` §9: was nicht Sache der MS-Welle ist und offen bleibt (`TRIB-PERSON-DRIFT`, `PROMO-FAKT-LEER`, `KZG-DEDUP`, `CHAR-HASH-FILTER`, `ENRICHER-DUP`).
- `_m` §9a: 61 Aufrufstellen erben die Frist des Vorgabewerts — *„oder die langsame Aufgabe nennt ihre eigene Frist“*.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_t` §4.2 — der Konkurrenz-Schutz aus dem Worker-Pattern ohne Locks (durchgestrichen); der Kasten darunter nennt den Defekt und seine Behebung am 25.08.2026.
- `_b` §6.1 — *„keine Locks, keine Race Conditions“* (durchgestrichen, widerlegt am 25.08.2026).
- `_k` §2, Punkt 1 — *„Konkurrenz-Schutz gibt es weder beim einen noch beim anderen“*, mit Marke *„Seit dem 25.08.2026 gibt es ihn“*.
- `_t` §4.5 — Microservices als eigene Prozesse; gebaut wird die Architektur in einem Prozess, die Schnittstelle bleibt dafür vorbereitet.
- `_t` §5 — zwei CPU-Modelle für Sprache und Analyse (*„eine Notlösung, die wir loswerden“*); Pixie nachts auf der GPU (*„obsolet“*).
- `_b` §7 — Rückbau-Strategie: der neue Pfad zuerst parallel zum alten.
- `_m` §9b — beim Fernzugang ist ein Modellname *„eine Ausschreibung, keine Wahl“*; §3.5 bekommt zwei Ergänzungen, und §3.2 gilt beim Fernzugang nur mit Anbieter, Quantisierung und Absage an den Rückfall.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung, B5 bis B7 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Bisheriger Kopf*, Feld **Status** | *„Block 4 (Qwen 3.6) als letzter Schritt der MS-Welle“* steht als ausstehend; `_b`, *Bisheriger Schluss*: *„MS-Welle vollständig abgeschlossen (Block 1–5)“* | `[gelesen 19.09.2026]` |
| **B2** | `_t` §4.3 | *„Drei Modell-Instanzen, jeweils auf eigenem Port“*; genannt werden zwei Ports (11434 und 11435) | `[gelesen 19.09.2026]` |
| **B3** | `_b` §8 | Im Futur geschrieben (*„Nach Abschluss aller fünf Blöcke“*), obwohl nach dem bisherigen Schluss erledigt | `[gelesen 19.09.2026]` |
| **B4** | `_k` §10 | *„`novaberg-backlog.md` — Sprint-Tracking der fünf Blöcke“*; das Backlog trägt seine Einträge heute in den Gegenstandsdateien, der Verweis ist veraltet | `[gelesen 19.09.2026]` |
| **B5** | `_b` §8, Punkt 4, gegen `_b`, *Bisheriger Schluss* | *„zusammen ~52 GB Plattenplatz frei“* gegen *„~105 GB frei“* — die Abweichung ist nicht erklärt | `[gelesen 19.09.2026]` |
| **B6** | `_m` §9b, zweiter Absatz nach der Tabelle | *„die Embedding-Pfade, die nach §4.2 ausdruecklich nicht Teil der Backend-Wahl sind“*; `_t` §4.2 (Worker und Queue) sagt nichts über eine Backend-Wahl | `[gelesen 19.09.2026]` |
| **B7** | `_k` §2, Punkt 1 | Die Marke *„Seit dem 25.08.2026 gibt es ihn“* steht mitten im Absatz; der Satz dahinter (*„treffen sie sich am gleichen HTTP-Client ohne Koordination“*) steht weiter im Präsens des alten Zustands | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — In-Process-Microservice-Architektur für die Modell-Schicht
**Stand:** 5. September 2026, 17:41 UTC (§9b — der erste Rueckhalt ausserhalb der eigenen Maschine; die Zusage aus §1 gegen den Baum gemessen). Davor 23. Mai 2026
**Pfad:** novaberg/docs/novaberg-microservice-modell-queue_k.md
**Vorgänger-Konzepte:** Audit 4 aus Chat 91 (fünf strukturelle Defizite), Pixie-Graph-Merge (Chat 79), Connector-Architektur (`config.py`)
**Status:** Block 1 (Embedding) abgeschlossen Chat 92, Block 2 (LLM-Konsolidierung) + Block 3 (think pro Call) abgeschlossen Chat 93/94, Block 5 (num_ctx pro Call) abgeschlossen Chat 96 — Block 4 (Qwen 3.6) als letzter Schritt der MS-Welle
