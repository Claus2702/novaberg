# Novaberg — Pixie-Plugin-Architektur (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-pixie-plugin_k.md`](novaberg-pixie-plugin_k.md) · Ausarbeitung: [`novaberg-pixie-plugin_t.md`](novaberg-pixie-plugin_t.md) · Bauplan und Umstellung: [`novaberg-pixie-plugin_b.md`](novaberg-pixie-plugin_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Keine. Das Konzept führt keine Entscheidung als solche.

---

## B. Offen beim Meister

Keine offene Frage dieser Art.

**Offen ohne Frage an den Meister:** Das Konzept führt keine offenen Punkte als solche. `_b` §6.2, Schritt 5, stellt den VertiefungsAgenten und weitere Pixie-Plugins auf *„Spaeter“*.

---

## C. Diskussion, verworfene Varianten und Nachträge

- `_t` §3.2, Kommentar im Codebeispiel: *„seit 15.08.2026: Zeile in shadow_auftrag, und prioritaet ist Pflicht“* — der einzige Nachtrag, an seiner Stelle.
- Verworfene Varianten führt das Konzept nicht.

Abschnitt D (aus dem Konzept verschobene Abschnitte) entfällt; kein Abschnitt des Konzepts steht in dieser Datei.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B4 stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Bisheriger Kopf* | Der Kopf hat kein Feld für den Stand der Umsetzung; der Sache nach ist das Konzept offen (Featureliste ⚫) | `[gelesen 19.09.2026]` |
| **B2** | `_t` §3.1 und §3.2, Felder `themen` und `context_user` | Beide sind veraltet: Laut `novaberg-queue-verfall_k.md` gab es `themen` im Auftrag nie, und für den Nutzer gilt jetzt das Paar-Schema | `[gelesen 19.09.2026]` |
| **B3** | `_t` §4.2 (*„Die Recherche liegt in Obsidian bereit“*) und `_k` §2 (Antwort als *„Stack-Push“*) | Obsidian und Stack-Push als Ziel sind vom Stand April 2026 | `[gelesen 19.09.2026]` |
| **B4** | `_k` §5 gegen `novaberg-agent-fachabteilung_k.md` §1 | Pixie-Plugins heißen hier *„Fachabteilungen“*; dort ist *Fachabteilung* die Bauart eines mitdenkenden CRUD-Agenten — derselbe Begriff, anders belegt | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er trägt keinen Messwert und steht deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Pixie-Plugin-Architektur — User-Auftraege an Pixie-Agenten
**Stand:** 29. April 2026, Chat 70
**Pfad:** novaberg/docs/novaberg-pixie-plugin_k.md
**Quellen:** Chat 70 (Architektur-Diskussion)
