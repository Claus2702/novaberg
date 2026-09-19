# Novaberg — Konzept: Fachabteilungs-Agenten (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-agent-fachabteilung_k.md`](novaberg-agent-fachabteilung_k.md) · Ausarbeitung: [`novaberg-agent-fachabteilung_t.md`](novaberg-agent-fachabteilung_t.md) · Bauplan und Umstellung: [`novaberg-agent-fachabteilung_b.md`](novaberg-agent-fachabteilung_b.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_k` §1, Zitat am Kopf | Agenten sind Fachabteilungen, die einen falschen Auftrag nicht ausführen, sondern widersprechen — wörtlich im Abschnitt: *„Wenn die Anweisung kommt: 3 + 4 = 9, dann muss die Fachabteilung sagen: Uhm... sorry, aber das stimmt so nicht!“* | April 2026, Entstehung des Konzepts — der Abschnitt nennt kein Datum |
| **E2** | `_k` §2.3, *„Die Entscheidung …: Architektonische Lösung.“* | Eine strukturelle Intelligenz-Schicht statt Einzelfall-Behebung per Prompt-Tuning; daraus folgt die Pipeline in `_t` §3 | wie E1 |

Den Wortlaut enthält das Konzept nur bei E1; E2 gibt es als Ergebnis wieder.

**Im Text als Setzung geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_k` §1, Kasten vom 20.08.2026: *„Die Metapher ist an Entwickler gerichtet, nicht an die Figur“*; seither sagen die Blöcke, dass Nova es selbst war (`NOVA-SPRICHT-VON-FACHABTEILUNG`).
- Abschnitt D, §8.1 bis §8.3: je eine *Tendenz*, ausdrücklich nicht entschieden (*„bei der tatsächlichen Umsetzung zu klären“*).

---

## B. Offen beim Meister

- Abschnitt D, §8.4 — *„Was passiert bei wiederholtem Scheitern der Output-Validation?“* Der Abschnitt nennt es selbst *„eine UX-Entscheidung“*: aufgeben, oder den Nutzer bitten, es anders zu formulieren. Das ist eine Frage nach der Absicht, nicht nach der Umsetzung.

**Offen ohne Frage an den Meister** — Punkte, die das Konzept selbst als offen führt:

- Abschnitt D, §8.1 (ein Node oder zwei), §8.2 (wie viel Fachwissen in den Prompt), §8.3 (Resume-Flow für differenzierte Rückfragen), §8.5 (empirische Validierung über ein Test-Set aus Live-Konversationen).
- `_b` §7.1, Schritt 1, und §6: `RESUME-REJECT` ist Voraussetzung, nicht Teil des Epics.

---

## C. Diskussion und verworfene Varianten

- `_k` §2.3 — die Einzelfall-Behebung per Prompt-Tuning (wie bei `CLASSIFY-CONFIRM`); verworfen, weil sie nicht skaliert: *„jeder neue Agent, jede neue Aktion bringt neue Fälle“* (E2).
- Abschnitt D, §8.1 — ein kombinierter Node für Semantik-Check und Output-Validation; billiger, aber weniger klar. Tendenz: getrennt, nicht entschieden.
- `_k` §1, Kasten vom 20.08.2026 — der Begriff *Fachabteilung* in Novas Prompt; dort entfernt, weil Nova als Botin über eine dritte Stelle sprach.

---

## D. Aus dem Konzept: offene Fragen für die Umsetzung

§8 steht hier ganz, weil `_e` die offenen Fragen sammelt.

## 8. Offene Fragen für die Umsetzung

Diese Fragen werden bei der tatsächlichen Umsetzung zu klären sein, nicht jetzt:

### 8.1 Sollen Semantik-Check und Output-Validation ein einzelner Node sein?

Zwei getrennte Nodes sind sauberer (Separation of Concerns), aber kosten zwei LLM-Calls. Ein kombinierter Node wäre billiger, aber weniger klar strukturiert. Tendenz: getrennt, weil Kosten lokal unkritisch.

### 8.2 Wie viel Fachwissen kommt in den Semantik-Check-Prompt?

Der Charakter-Agent weiß, wie Charakter-Beschreibungen aussehen. Wie wird dieses Wissen in den Prompt eingebettet? Als Beispiel-Tabelle? Als Regeln? Als destilliertes Fachsprache-Dokument? Tendenz: aufbauend auf dem bestehenden Domain-Language-Konzept aus Epic 15.

### 8.3 Wie wird der Resume-Flow für differenzierte Rückfragen designed?

Wenn die Rückfrage "Soll ich X deaktivieren?" lautet, wie interpretiert der Agent "Ja" (= ja, deaktiviere X) versus "Nein" (= nein, lass X aktiv, aber mach den Rest der Aktion)? Braucht es strukturierte Antwort-Interpretation? Tendenz: Ja, als Teil des RESUME-REJECT-Fix.

### 8.4 Was passiert bei wiederholtem Scheitern der Output-Validation?

Wenn der Classify wiederholt unsinnige Destillationen produziert, soll der Agent aufgeben? Dem User sagen "Ich verstehe dich nicht, formuliere es anders"? Das ist eine UX-Entscheidung.

### 8.5 Wie wird das Epic empirisch validiert?

Nach dem Umbau müssen die in Chat 48/49 dokumentierten Bugs verschwinden. Ein Test-Set aus den Live-Konversationen dient als Regressions-Baseline. Jeder der dort dokumentierten Fälle muss durch das neue System korrekt behandelt werden.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder die Entscheidung prüfen — das ist ein eigener Schritt. B1 bis B5 stammen aus der Sichtung.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | Abschnitt F, *Bisheriger Kopf* (Feld **Stand**) gegen *Bisheriger Schluss* | Der Kopf nennt als Stand eine andere Sitzung als der Schluss als Entstehung des Konzepts | `[gelesen 19.09.2026]` |
| **B2** | `_b` §10, Schritt 1 | *„Dieses Konzept lesen lassen. Im nächsten Chat …“* ist veraltet; der Schritt ist seit dem Stand des Konzepts nicht nachgeführt | `[gelesen 19.09.2026]` |
| **B3** | `_b` §7.4 | *„Repo-Vorbereitung und Codeberg-Push“*; veröffentlicht wird auf GitHub | `[gelesen 19.09.2026]` |
| **B4** | Abschnitt F, *Bisheriger Kopf*, Feld **Status** | *„Konzept — nicht implementiert“*; ob das noch gilt, ist unklar. Die Featureliste führt *Fachabteilungs-Agenten* ⚫ und daneben *Scheibe 12 F — die Fachabteilung prueft den Bestand* 🟠 | `[gelesen 19.09.2026]` |
| **B5** | `_k` §1 gegen `novaberg-pixie-plugin_k.md` §5 | *Fachabteilung* heißt hier die Bauart eines mitdenkenden CRUD-Agenten; in `novaberg-pixie-plugin_k.md` §5 heißen die Pixie-Plugins *„Fachabteilungen“* (gründliche, zeitintensive Aufträge) und die User-Plugins *„Sachbearbeiter“* — derselbe Begriff, anders belegt | `[gelesen 19.09.2026]` |

---

## F. Bisheriger Kopf und Schluss

Der Stands-Kopf und die Schlusszeile des ungeteilten Konzepts, ungekürzt. Sie tragen keinen Messwert und stehen deshalb hier.

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Fachabteilungs-Agenten (Konzept/Vision)
**Stand:** 19. April 2026, Chat 56
**Pfad:** novaberg/docs/novaberg-agent-fachabteilung_k.md
**Status:** Konzept — nicht implementiert, Pilot: CharakterIdentitaetAgent

*Erstellt in Chat 49 als Konzept-Papier. Basis: Live-Test-Beobachtungen in Chat 48/49, Design-Diskussion mit Meister. Inspiration: OpenClaw, Agentic Workflows, Anthropic's Agent Architecture.*
