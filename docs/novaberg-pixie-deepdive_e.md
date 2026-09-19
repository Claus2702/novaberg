# Novaberg — Pixie-Agent: VertiefungsAgent (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-pixie-deepdive_k.md`](novaberg-pixie-deepdive_k.md) · Ausarbeitung: [`novaberg-pixie-deepdive_t.md`](novaberg-pixie-deepdive_t.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine Entscheidung mit Urheber.

**Im Text als Setzung geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- Abschnitt D, Kasten vom 06.08.2026: *„Bestätigt …: Die Quelle ist das Web“*; `vertiefung` *„aus dem eigenen Bestand“* gilt für die Auswahl der Grabungsstelle, nicht für das Material.

---

## B. Offen beim Meister

Keine offene Frage dieser Art in diesem Konzept. `novaberg-queue-verfall_k.md` §15 führt eine Absichtsfrage, die diesen Agenten betrifft: ihn bauen oder die Intention `vertiefen` stilllegen. Sie ist dort gezählt, nicht hier.

**Offen ohne Frage an den Meister:**

- `_k`, Kasten vor §1: *„Die Überarbeitung dieses Dokuments auf den Zyklus steht aus.“*
- `_t` §2: *„Die Migration zum eigenständigen Agenten steht aus.“*
- Abschnitt D: *„Nicht baubar, solange `PIX-WARTESCHLANGE-AM-MODELL` steht“*.

---

## C. Diskussion und überholte Fassungen

- `_t` §2, *Trigger* — die Auslösung durch den KZG-Agenten aus einer Intention; laut Kasten vor §1 (`_k`) gilt seit dem 06.08.2026: *„Recherche und Vertiefung werden nicht mehr direkt aus einer Intention ausgelöst“*. Der Text von §2 ist nicht markiert (Befund B2).

---

## D. Aus dem Konzept: der zweite Kasten vor §1

Er stand zwischen Kopf und §1 und ist ein Nachtrag zur Quelle und zur Baubarkeit; der erste Kasten (übergeordnetes Konzept) steht in [`novaberg-pixie-deepdive_k.md`](novaberg-pixie-deepdive_k.md).

> **Bestätigt am 06.08.2026: Die Quelle ist das Web**, wie in §4 beschrieben. `novaberg-autonomous-wissen_k.md` §11.3 führte `vertiefung` als „aus dem eigenen Bestand" — das gilt für die **Auswahl der Grabungsstelle**, nicht für das Material. Dieses Dokument ist vier Monate älter als der Wissensspeicher und kennt ihn nicht; seine Architektur bleibt trotzdem gültig.
>
> **Nicht baubar, solange `PIX-WARTESCHLANGE-AM-MODELL` steht:** Der Agent importiert die Aufrufkette der Recherche, und jeder Hintergrundaufruf läuft gegen eine 300-Sekunden-Grenze bei 35–38 s Grundkosten.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_t` §4, *Dual-Modell-Routing* | *„`SHADOW_MODEL` (aktiv: Gemma 4)“*; laut `novaberg-microservice-modell-queue_k.md` läuft im Hintergrund Qwen 3.6 | `[gelesen 19.09.2026]` |
| **B2** | `_t` §2, *Trigger* | Die Auslösung aus der KZG-Intention ist durch den Kasten vor §1 (`_k`) aufgehoben, der Text aber nicht überarbeitet | `[gelesen 19.09.2026]` |
| **B3** | `_t` §2 gegen `novaberg-queue-verfall_k.md` | Das Konzept führt den Agenten als nicht implementiert; nach `novaberg-queue-verfall_k.md` warten 383 Aufträge `vertiefen` auf genau diesen Bau (die Featureliste nennt zu anderen Zeitpunkten andere Zahlen) | `[gelesen 19.09.2026]` |
| **B4** | `novaberg-queue-verfall_k.md` §15 | Dort steht die Absichtsfrage, ob dieser Agent gebaut oder die Intention stillgelegt wird; dieses Konzept beschreibt ihn weiter als geplant | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** VertiefungsAgent — Konzept (noch nicht implementiert)
**Stand:** 19. April 2026, Chat 57 (Modell-Alignment auf aktiven Connector)
**Pfad:** novaberg/docs/novaberg-pixie-deepdive_k.md
**Quellen:** nova-05-k-b.md (VertiefungsAgent-Abschnitte)
