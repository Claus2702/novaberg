# Novaberg — NachfragenAgent: die einfühlsame Rückfrage (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-pixie-nachfragen_k.md`](novaberg-pixie-nachfragen_k.md) · Ausarbeitung: [`novaberg-pixie-nachfragen_t.md`](novaberg-pixie-nachfragen_t.md) · Bauplan und Umstellung: [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md) · Diskussion und Ergänzungen: [`novaberg-pixie-nachfragen_e.md`](novaberg-pixie-nachfragen_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 5. Ein Befund nebenbei

Ein Queue-Auftrag für einen nicht registrierten Agenten **gewinnt** den Heartbeat und blockiert ihn für drei Durchläufe. Der fehlende Agent ist Roadmap und kein Defekt; die Verdrängung ist einer. Ein Auftrag für einen unbekannten Agenten sollte gar nicht erst gewinnen, sondern beim Einreihen oder spätestens bei der Auswahl aussortiert werden.

Steht in `novaberg-fundliste.md`, 27.07.2026.

**Nachtrag, gemessen am 05.08.2026 — der Defekt ist latent, nicht aktiv.** In einem Beobachtungsfenster von rund 2,25 Stunden gewann **kein einziger** agentenloser Auftrag; 19 Gewinner verteilten sich auf 11× `recherche`, 6× `synapsen_promotion`, 1× `wissensluecken`, 1× `wiedervorlage`, und die Meldung „nicht in Registry" fiel keinmal. Der Grund ist die Auswahl in `services/pixie/kandidaten.py`: Sie nimmt den **ersten** Eintrag mit echt größerer Priorität, und der älteste Eintrag bei Priorität 1,0 ist eine `recherche`. Die 390 Recherche-Aufträge verdrängen die 260 agentenlosen.

**Der Befund bleibt gültig und wird durch die Messung schärfer:** Er feuert wieder, sobald die Recherche-Aufträge vor ihnen abfließen. Was den Heartbeat heute blockiert, ist ein anderes: 249 von 270 Auslösungen fielen im selben Fenster mit `maximum number of running instances reached (1)` aus, weil eine laufende Recherche den einzigen Slot fünf Minuten hält.

---

## Aus §9 — Gebaut und gemessen, 05.08.2026

Was gebaut ist, die beiden Gegenproben und die Änderung am Auslöser stehen in [`novaberg-pixie-nachfragen_b.md`](novaberg-pixie-nachfragen_b.md), §9.

### Was der Reiz geworden ist

Wörtlich aus dem Messlauf, bei `einbruch` und Arousal 0,75:

> Die Stimmung kippt gerade ins Negative. Schwere liegt ueber dem Gespraech. Der Nutzer sucht Halt. Es ging zuletzt um: …

Drei Sätze aus dem Farbton, dann der Anlass. **Er beschreibt und adressiert niemanden** — die Form, die §7 verlangt. Ein Test hält das fest: Der Reiz enthält kein Fragezeichen und keine Anrede.

### Die Messung, in zwei Hälften

| | Ergebnis |
|---|---|
| **Kein Druck**, echter Auftrag vom 30.07. gegen die laufende Session | Vektor `eskalation`, **kein** Stapel-Eintrag (37 → 37), Status `abgeschlossen`; beide Audit-Zeilen in `hintergrund_log` nachgewiesen |
| **Druck**, eigenes Paar in derselben Anlage | Vektor `einbruch`, **ein** Eintrag (0 → 1), `aufgabe='nachfragen'`, Embedding 768 Dimensionen; danach aufgeräumt |
| **Zustellung** | `nachfragen` kommt bei allen vier negativen Emotionen durch, `recherche` bei keiner; bei `stress` schweigt auch `nachfragen` |

**Die erste Hälfte ist der wertvollere Beleg.** Sie ist die Entscheidung aus §8.1 im Betrieb: ein sechs Tage alter Auftrag, dessen Anlass vorbei ist, hinterlässt nichts als eine Audit-Zeile mit Grund.

**Was ungemessen bleibt, ausdrücklich:** Die Druck-Hälfte lief gegen ein eigens angelegtes Paar mit gesetzten Turn-Werten, nicht gegen einen echten Gesprächsverlauf. Ein echter Absturz lässt sich nicht bestellen, und ihn in der Produktivsession zu setzen hieße, falsche Gefühlshistorie zu schreiben. Damit ist der Weg vom Turn zum Vektor **nicht** mitgemessen — nur der Weg vom Vektor zum Stapel-Eintrag.
