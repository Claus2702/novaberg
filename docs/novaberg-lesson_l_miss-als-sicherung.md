# Novaberg — Lesson: Der Miss ist manchmal die Sicherung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Gleiche Ursache, gleicher Ein-Zeilen-Fix, konträre Konsequenz
**Stand:** 11. Juli 2026, Chat 105
**Pfad:** novaberg/docs/novaberg-lesson_l_miss-als-sicherung.md
**Auslöser:** Pixie-Router-Audit (Chat 105), `_PERIODISCH_ROUTING`
**Verwandt:** `novaberg-lesson_l_quelle-vor-destillat.md`, Backlog PIXIE-ROUTING-DOPPELREGISTRY, ZIEL-DECAY-FORMEL-KUMULATIV

---

## 1. Der Fall

Der Pixie-Router führt eine handgepflegte Registry neben der automatischen Agent-Discovery: `_PERIODISCH_ROUTING` in `services/pixie/router.py` (Z. 21–28) mappt Schedule-Key-Suffixe auf Agent-Namen. Ein Agent kann vollständig implementiert, per Discovery registriert und korrekt geschedult sein — und trotzdem nie laufen, weil dieser Lookup `None` liefert. Sichtbar nur als `warning`: „Pixie-Router: Kein Agent fuer periodische Aufgabe '…'".

Das Chat-105-Audit fand **zwei** Agenten in genau dieser Lage:

- `synapsen_decay` (P6, Chat 102) — täglicher Knoten-Decay + `pipeline_log`-TTL-Cleanup.
- `ziel_decay` — Motivations-Decay für mittelfristige Ziele.

Gleiche Ursache (fehlender Registry-Eintrag), gleicher denkbarer Fix (eine Dict-Zeile). Der erste wurde gefixt (`1e438e0`). Der zweite wurde **bewusst nicht** gefixt.

---

## 2. Zwei Formeln, zwei Welten

Der Unterschied liegt nicht im Routing — er liegt in dem, was der Fix scharfschalten würde.

| | `synapsen_decay` | `ziel_decay` |
|---|---|---|
| Formel | `gewicht_decay = gewicht_absolut × exp(−rate × tage_seit_verstaerkung)` (`lzg_knoten.py:480-486`) | `motivation_neu = motivation_gespeichert × exp(−rate × tage_seit_erstellt_am)`, **zurückgeschrieben** (`ziel_decay/agent.py:78-98`) |
| Zeitbasis | `verstaerkt_am` — zeitabsolut | `erstellt_am` — ändert sich nie |
| Multiplikand | unveränderliches Anker-Feld `gewicht_absolut` | der **bereits decayte** gespeicherte Wert |
| Charakter | **idempotent** — jeder Lauf überschreibt mit demselben Absolutwert; 60 ausgefallene Läufe ändern am Ergebnis des ersten nichts | **kumulativ** — jeder Lauf multipliziert erneut; regulärer Betrieb ergäbe `exp(−r·Σn)`, quadratischer Exponent |
| Umkehrbarkeit | Soft-Delete; `gewicht_absolut`/`gewicht_roh` unangetastet, `reactivate_node` rechnet aus dem Anker zurück | `aktiv=FALSE` zwar weich, aber `motivation` der Überlebenden **hart überschrieben** — kein Anker-Feld, Originalwert weg; Reaktivierte fallen beim nächsten Lauf erneut (das Gesamtalter wächst nur) |
| Dry-Run (echte Formel, Live-DB) | **0 von 252 Knoten** unter der Schwelle — erster Lauf ein Tagesschritt | **5 von 5 Zielen** wären gefallen — erster Lauf eine Klippe, unwiederbringlich |

Beide Agenten sahen von außen identisch aus: sauber implementiert, EVA-diszipliniert, geschedult, nur nicht geroutet. Erst die Formel-Ebene trennte den harmlosen Fix vom Datenverlust.

---

## 3. Die Versuchung

Nach dem ersten Audit („`synapsen_decay`: Formel zeitabsolut, Rückstand folgenlos, Fix harmlos") lag die Übertragung nahe: derselbe Router, derselbe Miss, dieselbe Zeile — also derselbe Fix, gleich mit erledigen. Der Fix wäre in dreißig Sekunden committet gewesen.

Genau das wäre der Fehler gewesen. Beim nächsten Heartbeat (`ziel_decay` hat **kein** eigenes AKTIV-Flag, nur das globale `PIXIE_AKTIV`) hätte der erste Lauf alle fünf nicht-langfristigen Ziele deaktiviert und die Motivation der Überlebenden mit einem doppelt falschen Wert überschrieben. Novas Ziel-Gravitation (Enricher, GV4) wäre auf einen Schlag leer gewesen — und ab dem zweiten Lauf hätte der Kumulativ-Defekt jeden verbliebenen Wert quadratisch zerrieben.

Der Router-Miss war bei `ziel_decay` nicht der Bug. Er war die **Sicherung**: Er hat zwei Monate lang verhindert, dass ein defekter Mechanismus feuert. Wer die Sicherung tauscht, ohne die Leitung zu prüfen, repariert den Kurzschluss in die Wand.

---

## 4. Die Regel

> **Audit vor Code — auch dann, gerade dann, wenn der vorige Audit „harmlos" sagte. Ein zweiter Fall mit gleicher Ursache ist kein zweiter Fall mit gleicher Konsequenz.**

Konkret:

1. **Pro Fall ein eigenes Audit der Konsequenz-Seite.** Die Ursachen-Seite (Registry-Miss) darf gesammelt werden; was der Fix *scharfschaltet*, wird je Empfänger einzeln geprüft — Formel, Zeitbasis, Multiplikand, Umkehrbarkeit, Gates.
2. **Bevor ein toter Pfad scharfgeschaltet wird, gehört ein Dry-Run dazu — mit der ECHTEN Formel, nicht einer Näherung.** Die SQL-Nachbildung muss dieselbe Zeitbasis, dieselbe Rate und dieselbe Schwelle verwenden wie der Code. Hier trennten die Dry-Runs (0/252 vs. 5/5) Tagesschritt von Klippe, bevor irgendetwas lief.
3. **„Läuft nie" ist ein Zustand mit zwei Lesarten.** Ein nie gelaufener Pfad ist entweder ein vorenthaltenes Feature oder ein verhinderter Schaden. Welche Lesart gilt, entscheidet nicht der Routing-Eintrag, sondern der Code dahinter.

Die Reihenfolge im konkreten Fall: erst ZIEL-DECAY-FORMEL-KUMULATIV fixen (Anker-Feld `motivation_absolut` analog `gewicht_absolut`, Zeitbasis zeitabsolut, idempotent wie `synapsen_decay`) — **dann** die Router-Zeile setzen. Nicht umgekehrt.

---

## 5. Anschluss

Die strukturelle Wurzel — zwei Registries, eine automatisch, eine handgepflegt — bleibt als eigener Posten offen (PIXIE-ROUTING-DOPPELREGISTRY): 5 von 7 Einträgen sind Identitäts-Abbildungen, zwei Agenten wurden vergessen, zwei Keys sind tot. Diese Lesson handelt nicht von der Registry, sondern von der Verlockung, den zweiten Fund mit dem Urteil des ersten zu erledigen.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*
