# Novaberg — KZG-Liberalisierung + Cluster-Promotion (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-kzg-liberalisierung_k.md`](novaberg-kzg-liberalisierung_k.md) · Ausarbeitung: [`novaberg-kzg-liberalisierung_t.md`](novaberg-kzg-liberalisierung_t.md) · Bauplan und Umstellung: [`novaberg-kzg-liberalisierung_b.md`](novaberg-kzg-liberalisierung_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine Entscheidung mit Urheber.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_t` §3.1 bis §3.6, *„Architekturentscheidungen“*: Backpropagation, querschneidende Cluster, LLM als Qualitätsfilter, `KZG-KERN-BLIND` obsolet, `KZG-DEDUP` als Feature, KZG-Salienz als Analogon zum LZG-Gewicht. Es sind Begründungen der Bauart.

---

## B. Offen beim Meister

Keine offene Frage dieser Art.

**Offen ohne Frage an den Meister:** Das Konzept führt keine offenen Punkte.

---

## C. Diskussion und verworfene Varianten

- `_t` §2.2 — der Merge bei Cosine >= 0.85 (der zweite Kern ging verloren); ersetzt durch paralleles Speichern und thematische Verstärkung. Der Node `aehnlichkeit_pruefen` fällt weg.
- `_b` §6 — Themen-Clustering, verworfen (kurze Strings unbrauchbar); Greedy-Zuordnung, verworfen (Informationsverlust).

Abschnitt D (aus dem Konzept verschobene Abschnitte) entfällt; kein Abschnitt des Konzepts steht in dieser Datei.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B3 stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Bisheriger Kopf*, Feld **Stand** (*„implementiert und getestet“*), und `_t` §2.3 | Die Cluster-Promotion ist entfernt (`novaberg-memory-synapsen_b.md` §13, P9), die Featureliste führt den Pfad als deaktiviert; das Konzept ist nicht als überholt markiert | `[gelesen 19.09.2026]` |
| **B2** | `_t` §2.2 und §4 (`KZG_SALIENZ_CAP` 10.0, `KZG_SALIENZ_DAEMPFUNG_EXP` 0.6) | Cap 10 und Exponent 0.6 sind ersetzt, ohne Markierung | `[gelesen 19.09.2026]` |
| **B3** | `_t` §2.1 und §4 (`KZG_SALIENZ_MINIMUM` 0.3) | Das Minimum heißt heute 0.67378, ohne Markierung | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf und Schluss

Der Stands-Kopf und die Schlusszeile des ungeteilten Konzepts, ungekürzt. Sie tragen keinen Messwert und stehen deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept & Implementierung — KZG-Liberalisierung + Cluster-Promotion
**Stand:** 25. April 2026, Chat 64 (implementiert und getestet)
**Pfad:** novaberg/docs/novaberg-kzg-liberalisierung_k.md

*Konzeptdokument erstellt und implementiert in Chat 64.*
