# Novaberg — Memory-Kern: Synapsen-Modell (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) · Ausarbeitung: [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) · Bauplan und Umstellung: [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) · Messungen: [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Die Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §7.1a, Unterabschnitt *„Woran ‚hergenommen‘ erkannt wird — entschieden am 04.09.2026“* | Verwendung wird über die Embedding-Nähe zwischen Antwort und Erinnerung erkannt, nicht über eine Selbstauskunft des Verfassers — *„Er könnte aber auch fantasieren“*. Die Segmentierung, die derselbe Unterabschnitt zuerst vorsah, ist vor dem Bau widerlegt | 04.09.2026 |
| **E2** | `_b` §11, Absatz *„Beschluss …: selektive manuelle Übernahme, danach alte Tabelle löschen“* | Bestandsdaten des alten Langzeitgedächtnisses werden von Hand ausgewählt übernommen, danach wird die alte Tabelle gelöscht. **Gegenstandslos geworden am 27.07.2026, ausgeführt nie** (Kasten am Kopf von §11) | Konzeptphase, Mai 2026 — der Abschnitt nennt kein Datum |
| **E3** | Abschnitt G unten, K5 und K10; `_b` §13.6, *Die Entscheidungs-Notiz zu P4*, §4 und §5 | Wo der Code von den Festlegungen zu P4 abweicht, gilt der Code, die Festlegung ist überholt — *„Code gilt“* | 19.09.2026 |
| **E4** | Abschnitt G unten, K8 | Ob das Anfangsgewicht neuer Knoten umgerechnet wird, wird erst gemessen — *„Erst messen“* | 19.09.2026 |
| **E5** | Abschnitt G unten, *Abschlussstand* | P4 schließt mit `SYNAPSEN-LIVE-VERIFY` und `KZG-ERSTELLT-AM-PARSE-HÄRTE`, die übrigen fünf Folgeeinträge laufen ohne P4-Bindung — *„Zwei, Rest lösen“* | 19.09.2026 |

Der Wortlaut von E1 und E2 steht in keinem der beiden Abschnitte; beide geben sie als Ergebnis wieder. E3 bis E5 stehen wörtlich am Punkt.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_b` §8.5.5, Absatz *„Zum Ablageort der Tabelle“*: *„Entschieden für `ei/dreischicht.py`“* (02.08.2026, beim Bau von P10).
- `_t` §10.1: *„Die Paar-Spalten sind nullable, und das ist eine Entscheidung.“*
- `_b` §13.1, *Cold-Start akzeptiert*: *„Bewusste Designentscheidung“*.
- `_t` §8.5.3: *„Umgesetzt mit Faktor 0.0“* statt eines Werts aus der Spanne 0.0 bis 0.05.

Die Festlegungen K1 bis K10 für Sprint P4 stehen in Abschnitt G unten, mit dem Messergebnis am Code, und sind hier nicht gezählt; gezählt sind die Entscheidungen des Meisters dazu (E3 bis E5).

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage an den Meister.

**Offen ohne Frage an den Meister** — Beobachtungen und Messungen, die das Konzept selbst als offen führt:

- Abschnitt D unten (§7.11): Container-Verhalten bei unterschiedlichen Präzisionen, Themen-Normalisierung, Validierung von `LZG_EMBEDDING_SCHWELLWERT`.
- `_m`, *Aus §8.5* (§8.5.6): ob die Wahrnehmungs-Gravitation die Trefferliste je ändert — *„Das ist die offene Frage von P10“*, entscheidbar erst an der Charakterbildungs-Messreihe.
- `_t` §7.1a: eine echte Nulllinie über nachweislich fremde Knoten fehlt; die Segmentzahl ist neu zu messen, wenn die Antworten länger und mehrteilig werden.
- `_m`, *Bisheriger Kopf*: ob Entitäts- und Zeitschicht greifen, wenn es etwas zu greifen gibt — ebenfalls an der Charakterbildungs-Messreihe.
- `_k` §3.2: das Faktengedächtnis als eigenes Konzeptpapier, *„sobald der LZG-Kern dieses Konzepts steht“*.
- Abschnitt G, K8 (E4): ob das Anfangsgewicht neuer Knoten umgerechnet wird — entscheidbar erst nach der Messung der Anfangsgewichte aus der Datenbank.

---

## C. Diskussion und verworfene Varianten

Die verworfenen und überholten Fassungen stehen an ihrer Stelle, durchgestrichen oder mit Kasten, und mit Grund:

- `_k` §2 / `_t` §7.1 — der Co-Aktivierungs-Boost im Lesepfad; entfällt, weil Lesen nichts verstärken darf (selbstverstärkendes Verwachsen).
- `_t` §4.1 — der Vektor-Index `ivfflat` auf `lzg_knoten.embedding`; entfernt am 12.07.2026 (Recall-Kollaps bei kleinem Bestand).
- `_t` §7.1a — die Selbstauskunft des Verfassers als Erkennungskriterium; verworfen, weil nicht nachprüfbar (E1).
- `_t` §7.1a — die Segmentierung der Antwort; widerlegt am 04.09.2026 vor dem Bau (25 von 25 Antworten ein Segment).
- `_t` §7.8 — der zweite LLM-Call der alten Promotion (Destillation); entfällt, weil nichts mehr verdichtet wird.
- `_t` §8.5 — *„Bis dahin sucht der Enricher mit dem rohen Anfrage-Embedding“*; überholt durch den Bau von P10 am 02.08.2026.
- `_t` §8.5.2 — der CharacterGraph habe den Cluster des aktuellen Turns; widerlegt am 02.08.2026, der Rückfall auf den Vorturn ist der einzige Pfad.
- `_t` §8.5.3 — der Dateizeiger auf `salienz.task.txt`; korrigiert am 02.08.2026.
- `_t` §10.2 — *„Elf Werte“* und *„Lesen wird nicht geloggt“*; überholt am 04.09.2026.
- `_b` §11 — die selektive Migration; gegenstandslos seit dem 27.07.2026 (E2).
- `_b` §12.3, *TE* — der Pfad *Enricher schreibt abgerufene IDs, Pixie verstärkt*; existiert nicht mehr (04.09.2026).
- `_b` §13.12, Abnahme-Test 3 — der HumanGraph-Rückfall; nicht erfüllbar, geprüft im CharacterGraph.
- `_k` §14.2 und §14.3 — bewusst nicht übernommene Modelle der Forschung (ungerichtete Kanten, RDF-Tripel, eigenständige Kantenstärken, Multi-Timescale-Konsolidierung, Edge-Embeddings, STDP), je mit Grund.

---

## D. Aus §7 — Schreibpfad-Sicht

Die übrigen Unterabschnitte von §7 stehen in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md).

### 7.11 Offene Detail-Punkte zum Schreibpfad

Diese Punkte sind noch nicht festgelegt und werden in den nächsten Konzept-Sessions geklärt oder im Live-Betrieb beobachtet:

- **Container-Verhalten bei unterschiedlichen Präzisionen.** Konzert um 20:00 (Minute) liegt innerhalb eines Urlaubs vom 1.–7. August (Tag oder Zeitraum). Strikte Präzisions-Gleichheit lässt zwischen ihnen keine Timeline-Kante zu — sie verbinden sich nur über Entitäten und Themen. Beobachten, ob das in der Praxis ausreicht; falls nicht, eine Containment-Bedingung als eigenen Auslöser nachrüsten.
- **Themen-Normalisierung.** Bestehender Bug-Cluster zur Themen-Vermischung („Annas Geburtstag" vs. „Geburtstag von Anna" vs. „Geburtstag"). Möglicher LLM-Call vor dem Knoten-Insert. Aktuell zurückgestellt, weil der zweite Promotion-Call entfällt; nachrüsten, wenn das Phänomen in der neuen Topologie sichtbar bleibt.
- **Initialwert `LZG_EMBEDDING_SCHWELLWERT = 0.85` validieren.** Im Live-Betrieb beobachten, wie häufig die Embedding-Schicht greift. Greift sie zu selten, Schwellwert auf 0.80 oder 0.75 absenken.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B10 stammen aus der Sichtung, B11 bis B14 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_m`, *Bisheriger Kopf*, Feld **Stand** (Glied *„davor 2. August 2026“*) | Der Kopf sagt *„P1 bis P9 gebaut, P10 offen“*; `_b` §13 sagt *„Alle zehn Sprints sind gebaut“*, und `_b` §13.12 wie `_t` §8.5 führen P10 als gebaut am 02.08.2026 | `[gelesen 19.09.2026]` |
| **B2** | Abschnitt F unten, bisherige Schlusszeile | Die Zeile nennt als Konzept-Stand eine Sitzung der Konzeptphase und beschreibt die Sprints als künftig; der Kopf trägt den Stand 18.09.2026, `_b` §13 den abgeschlossenen Bau | `[gelesen 19.09.2026]` |
| **B3** | `_t` §6 | `LZG_KNOTEN_REINFORCEMENT_BOOST = 0.5`; `_t` §4.1 (*Was die Skala … bedeutet*) nennt `= 0.1` je Verstärkung, ebenso die Festlegungen zu P4, K10 (Abschnitt G unten) und Notiz §4 (`_b` §13.6) | `[gelesen 19.09.2026]` |
| **B4** | `_t` §6, `_t` §7.5 (Beispiel 2), Abschnitt D (§7.11) | `LZG_EMBEDDING_SCHWELLWERT = 0.85`; `novaberg-embedding-casing-blind_k.md` führt 0.85 als alten und **0.55** als neuen Wert (p99 = 0.568) | `[gelesen 19.09.2026]` |
| **B5** | `_t` §7.7 (dazu §7.2 Schritt 4, §8.4.2 Feld `kzg_quell_key`; `_b` §13.6) | Der KZG-Eintrag werde nach der Promotion aus Redis gelöscht; `novaberg-embedding-casing-blind_k.md` (Nachtrag 04.09.2026) und `novaberg-kzg-salienz_k.md` (`PROMOTION-ENTFERNT-KZG-NICHT`) sagen, das geschieht nicht | `[gelesen 19.09.2026]` |
| **B6** | `_k` §3.1 | *„parallel zum bestehenden `langzeitgedaechtnis`“*; die Tabelle ist gelöscht (`_b` §11, Kasten am Kopf; `_b` §13, P9) | `[gelesen 19.09.2026]` |
| **B7** | `_t` §7.8 | Der erste LLM-Call (Klassifikation) *„bleibt grundsätzlich erhalten“*; K1 der Festlegungen zu P4 (Abschnitt G unten) legt *„Keine LLM-Reifeprüfung im neuen Pixie-Agent“* fest, K3 lässt Call 1 und Call 2 in P4 entfallen | `[gelesen 19.09.2026]` |
| **B8** | `_k` §15 | `novaberg-pixie-promotion.md` und `novaberg-mem-lzg.md` *„wird durch den Umbau abgelöst“*, `novaberg-kzg-liberalisierung_k.md` als *„heutige Cluster-Promotion“*; der Umbau ist abgeschlossen und die Cluster-Promotion entfernt (`_b` §13, P9) | `[gelesen 19.09.2026]` |
| **B9** | `_t` §10.5, *Wachstums-Schätzung* | *„der GIN-Index auf `inhalt` ist die größte Einzelposition“*; `_t` §10.1 (Absatz *Nachgezogen am 04.09.2026*) sagt, dieser Index ist nicht gebaut | `[gelesen 19.09.2026]` |
| **B10** | `_k` §1 | *„Novas Langzeitgedächtnis ist heute eine Aggregat-Schicht …“* im Präsens; der Umbau ist seit dem 02.08.2026 abgeschlossen (`_b` §13) — die Vision liest sich, als gelte der alte Zustand | `[gelesen 19.09.2026]` |
| **B11** | `_t` §4.2, §7.8, §7.9.2; `_b` §8.5.5 · `_t` §7.1, §8 · `_t` §8.4.2, §8.5.4 | Verweise mit der Nummerierung eines früheren Entwurfs: *„Punkt 9 (Implementierungs-Phasen)“* — die Phasen stehen in §13, §9 ist die Decay-Logik; *„Punkt 4 (Lesepfad)“* — der Lesepfad ist §8; *„Punkt 6 im offenen Teil“* für das Gesprächs- und Node-Log — das Pipeline-Log ist §10 | `[gelesen 19.09.2026]` |
| **B12** | `_b` §13.6, *Abgrenzung* | *„vollständig aus Redis gelöscht (Konzept 2.5)“*; §2.5 ist *Gläsernheit als Architekturziel*, die Löschung steht in `_t` §7.7 | `[gelesen 19.09.2026]` |
| **B13** | `_b` §13.7 gegen `_t` §8.2.1 | `CLUSTER_ENRICHER_SPRUENGE` *„aus `config.py`“* (§13.7) gegen *„in `ei/dreischicht.py`“* (§8.2.1) | `[gelesen 19.09.2026]` |
| **B14** | `_b` §13.8, Abnahme-Tests 2 und 4 | Die Tests rechnen mit Decay-Rate 0.02 und `LZG_KNOTEN_MIN_GEWICHT = 0.5`; `_t` §6 führt 0.0015 und 0.1, das Beispiel in `_t` §9.3 rechnet mit 0.10 | `[gelesen 19.09.2026]` |


---

## F. Bisheriger Schluss

Die Schlusszeile des ungeteilten Konzepts, ungekürzt. Sie trägt keinen Messwert und steht deshalb hier.

*Konzept-Stand Chat 88. Alle Architektur-Punkte ausgearbeitet — Schreibpfad, Lesepfad, Decay-Logik, Pipeline-Log, Migration, Bug- und Backlog-Reset, Kanten-als-Cache-Architektur, wissenschaftliche Einordnung sowie Implementierungs-Phasen (Stufe 1, zehn Sprints P1–P10). Charakter-Hash-Destillation gehört zu Pixie und ist außerhalb des LZG-Kerns. Brudi-Prompts pro Sprint (Stufe 2) entstehen just in time vor Sprint-Start. Faktengedächtnis als eigenes Konzeptpapier kommt nach Fertigstellung des LZG-Kerns.*

---

## G. Die Festlegungen zu P4

**Umgezogen am 19.09.2026.** Dieser Abschnitt und der Abschnitt *„Die Entscheidungs-Notiz zu P4“* unter §13.6 in [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) tragen die frühere Konzept-Notiz `novaberg-memory-synapsen-p4-entscheidungen_k.md` wortgleich; die Notiz ist am 19.09.2026 hierher gezogen, ihre eigene Datei entfällt. Chronik, Fundliste und Archive nennen weiter den alten Dateinamen. Die Nummern 1 bis 9 sind die der Notiz, nicht die des Konzepts: §1 und §3 stehen hier, §2 und §4 bis §8 in `_b`, die verwandten Dokumente aus §9 in `_k` §15.

Unter jedem Punkt steht das Messergebnis vom 19.09.2026 am Code (`server/`, gelesen, kein Lauf gegen den Dienst): **trägt**, **abweichend** oder **fehlt**, mit Fundstelle. Von 16 geprüften Punkten der Notiz tragen 11, 4 weichen ab, 1 fehlt; die Konstanten und die Lesart der Queue stehen bei §4 und §5 in `_b`.

Der Kopf der Notiz, ungekürzt:

**Dokument:** Konzept-Notiz, K-Punkt-Festlegungen für Synapsen P4
**Status:** Aktiv (Chat 91, vor Implementation)
**Verwandt:** `novaberg-memory-synapsen_k.md` (Haupt-Konzept), `novaberg-pixie-promotion.md` (Live-Doku alter Pfad)

### 1. Kontext

Diese Notiz hält die Architektur-Entscheidungen fest, die in Chat 91 nach
Audit 1 (Code-Inventar des alten PromotionAgents) und Audit 2 (Mapping auf
das Synapsen-Schema) als zehn Klärungspunkte (K1–K10) entstanden sind. Die
Klärung erfolgte punkt-für-punkt im Reducer-Stil.

Die Notiz ist Anker für den späteren P4-Sprint und überbrückt die
Microservice-Modell-Queue-Welle, die als Voraussetzung vor P4 läuft.

### 3. Die zehn K-Punkte mit Festlegungen

#### K1 — Reifeprüfung

**Festlegung:** Salienz ≥ 0.7 für beide Pfade (`neu` und `verstaerkt`).
Keine LLM-Reifeprüfung im neuen Pixie-Agent. Keine Mindest-Alter-Bedingung.
Keine Magnet-Feld-Anwesenheits-Bedingung — dünn vernetzte Knoten werden
akzeptiert, Pipeline-Log liefert spätere Analyse-Möglichkeit.

**Pre-P4-Fix:** `queues.py:72` von `PROMOTION_THRESHOLD` (0.8) auf
`KZG_SALIENZ_HIGH` (0.7) umhängen. Asymmetrie 0.7/0.8 ist Restbefund der
unvollständigen Chat-64-Konsolidierung, nicht Designentscheidung.

`[gemessen am Code 19.09.2026]` **trägt.** Beide Pfade — neuer und verstärkter Eintrag — prüfen gegen `KZG_SALIENZ_HIGH`; eine Alters- oder Magnet-Prüfung gibt es im Agenten nicht. Der Wert heißt heute `0.88078`, der gedämpfte Gegenwert zu roh 0.7 nach dem Umbau der Salienz-Skala. Fundstelle: `server/agents/kzg/queues.py` `queues_befuellen`; `server/config.py` `KZG_SALIENZ_HIGH`.

`[gemessen am Code 19.09.2026]` **Pre-P4-Fix: trägt.** Beide Einreihungen prüfen gegen `KZG_SALIENZ_HIGH`; `PROMOTION_THRESHOLD = 0.8` steht noch, kommentiert als *„Legacy, nicht mehr verwendet“*. Fundstelle: `server/agents/kzg/queues.py` `queues_befuellen`; `server/memory/kzg.py` `PROMOTION_THRESHOLD`.

#### K2 — FaktenManager-Verbleib

**Festlegung:** Pfad D.2 — Tripel-Extraktion entfällt komplett in P4.
Kein Call 1, kein Call 2, kein FaktenManager-Aufruf im neuen Pixie-Agent.
Funktionalitäts-Bruch zwischen P4 und M2.5b wird akzeptiert (keine neuen
Tripel, keine Edge Invalidation, eingefrorener Fakten-Bestand).

Spätere Architektur: FaktenAgent als eigenständige Fachabteilung
(M2.5b), analog zu TimelineAgent. Router-getrieben mit Salienz-Fallback.

`[gemessen am Code 19.09.2026]` **trägt.** Der Agent ruft weder eine Tripel-Extraktion noch den FaktenManager auf. Einen FaktenAgent (M2.5b) gibt es im Code nicht (Suche `FaktenAgent|fakten_agent` in `server/`: ein Treffer in einem Kommentar in `server/graph/nodes/gespraechsvektor.py`, kein Agent). Fundstelle: `server/agents/synapsen_promotion/agent.py` `SynapsenPromotionAgent`.

#### K3 — Call 1 + Call 2 Verbleib

**Festlegung:** Beide entfallen vollständig in P4. Folge aus K2.

`[gemessen am Code 19.09.2026]` **trägt.** Kein Aufruf eines Sprachmodells; `lastart` ist `"cpu"`. Fundstelle: `server/agents/synapsen_promotion/agent.py` `SynapsenPromotionAgent.lastart`.

#### K4 — Qualitätsfilter O5/O11/O12

**Festlegung:** Strukturell aufgelöst. O5 (Speaker-Auflösung) entfällt
ersatzlos — `inhalt` wandert unverändert, Speaker steht in `beobachter`.
O11 (Objekt-Entitäten) obsolet durch P3 (`magnete_aufloesen` mit
`EntityResolutionService.resolve_batch`). O12 (Tautologie) Tripel-spezifisch,
wandert später mit dem FaktenAgent mit.

`[gemessen am Code 19.09.2026]` **trägt.** `beobachter` kommt aus dem Hash des KZG-Eintrags; die Magnete löst `magnete_aufloesen` über `EntityResolutionService.resolve_batch` auf; eine Tautologie-Prüfung gibt es im Agenten nicht (Suche `tautolog` in `server/`: kein Treffer). Fundstelle: `server/agents/synapsen_promotion/agent.py` `_eintrag_verarbeiten`; `server/agents/kzg/magnete.py` `magnete_aufloesen`.

#### K5 — `hintergrund_log` vs. `pipeline_log`

**Festlegung:** Beide Tabellen bleiben, funktional verschieden:
- `hintergrund_log` = Pixies operatives Arbeitsgedächtnis
  (Deduplizierung, was wurde erledigt)
- `pipeline_log` = Novas Selbstreflexionsschicht
  (Span-Forensik, Metakognitions-Substrat)

Neuer Pixie-Agent schreibt in **beide**. EVA-Vorbedingungs-Fehler:
`hintergrund_log` mit `status='fehler'`, `pipeline_log` mit
`art='bemerkung'`. Erfolgreiche Promotionen analog mit kompletter Span.

**Architektur-Grundannahme:** Nova ist Pixie. Pixies Verarbeitung ist
Teil von Novas Pipeline.

`[gemessen am Code 19.09.2026]` **abweichend.** Der Agent schreibt in beide Tabellen. Fehler gehen aber als `art='fehler'` ins `pipeline_log`, über `log_fehler`, nicht als `art='bemerkung'`. Fundstelle: `server/agents/synapsen_promotion/agent.py` `_fehler`, `_audit_log` → `server/memory/background_audit.py` `write_audit`; `server/memory/pipeline_log.py` `log_fehler`.

`[entschieden 19.09.2026]` Der Code gilt, die Festlegung ist überholt. Der Meister: *„Code gilt“*.

#### K6 — Prompt-Segregation

**Festlegung:** Obsolet in P4. Folge aus K3 — keine LLM-Calls, keine
Prompts auszulagern. Bleibt offen für M2.5b (FaktenAgent).

`[gemessen am Code 19.09.2026]` **trägt.** Der Agent enthält keine Prompts (Suche `prompt` in `server/agents/synapsen_promotion/agent.py`: kein Treffer).

#### K7 — Caller-Tags

**Festlegung:** P4 hat keine Caller-Tags, weil keine LLM-Calls.
Konvention für später (alle LLM-aufrufenden Agenten ab M2.5b):
`pipeline_log`-Span-Korrelation als alleinige Forensik-Quelle,
keine zusätzlichen Caller-Tags.

`[gemessen am Code 19.09.2026]` **trägt.** Der Agent setzt keine Caller-Tags (Suche `caller` in `server/agents/synapsen_promotion/agent.py`: kein Treffer).

#### K8 — Initiale `gewicht_roh`-Berechnung

**Festlegung:** `lzg_knoten.gewicht_roh = KZG-Eintrag.salienz` (direkte
Übernahme, keine Skalierung). Begründung: Salienz im KZG ist 0–10-Skala
(`KZG_SALIENZ_CAP = 10.0`, sin^0.6-gedämpft) — dieselbe Skala wie
`gewicht_roh` im LZG. Nahtlose Übernahme.

Anschluss-Felder:
- `gewicht_absolut = 10 × sin^0.5(min(gewicht_roh / 10, 1) × π/2)`
  (§5.4 Schritt 5)
- `gewicht_decay = gewicht_absolut` (initial identisch, divergiert mit
  P6 Decay-Job)

**Migration alter Daten (P9, §11.2):** `gewicht_roh = 2.0` als
neutraler Setz-Wert, weil Bestandsdaten ihre ursprüngliche Salienz
verloren haben.

`[gemessen am Code 19.09.2026]` **abweichend.** Die Übernahme ist direkt, `gewicht_absolut` und `gewicht_decay` stehen wie festgelegt. Die Begründung trägt nicht mehr: `KZG_SALIENZ_CAP` ist seit Chat 113 `1.0`, `LZG_KNOTEN_GEWICHT_CAP` ist `10.0` — ein neuer Knoten bekommt `gewicht_roh` im Bereich 0 bis 1 auf einer Kurve, die bis 10 reicht. Die Logzeile im Agenten schreibt weiter `(0-10)`. Fundstelle: `server/agents/synapsen_promotion/agent.py` `_eintrag_verarbeiten` (Kommentar K8, Logzeile `kzg_salienz=… (0-10)`); `server/memory/lzg_knoten.py` `knoten_anlegen`, `gewicht_absolut_berechnen`; `server/config.py` `KZG_SALIENZ_CAP`, `LZG_KNOTEN_GEWICHT_CAP`, `LZG_KNOTEN_DAEMPFUNG_EXP`.

`[entschieden 19.09.2026]` Die Begründung *„dieselbe Skala 0–10“* gilt seit Chat 113 nicht mehr. Ob umgerechnet wird, wird erst gemessen — der Meister: *„Erst messen“*. Gemessen werden die Anfangsgewichte neuer Knoten aus der Datenbank; danach entscheidet der Meister. Ein eigener Backlog-Eintrag folgt. P4 hängt nicht daran.

#### K9 — Embedding-Quelle

**Festlegung:** Re-Embed `inhalt` allein (Pfad B). Keine
Themen-Anreicherung. Begründung: Schicht-Orthogonalität wahren — Themen
gehen über die Themen-Schicht in die Kanten-Bildung ein, Embedding
über die Embedding-Schicht. Pfad C (`inhalt + themen`) würde die
Schicht-Trennung sabotieren.

Pre-Voraussetzung Microservice-Modell-Queue ist Blocker für P4 —
Re-Embed-Aufrufe laufen über die Queue, nicht direkt.

**Bekannter Schwachpunkt:** Entkernte KZG-Inhalte ("Der Nutzer
bestätigt das.") werden auch im LZG entkernt sein. Lösung außerhalb
P4-Scope: KZG-Verdichter-Prompt-Refinement plus späteres
Chronik-Konzept.

`[gemessen am Code 19.09.2026]` **trägt.** `embed_text_bauen` gibt `inhalt` unverändert zurück; der Aufruf läuft über die Modell-Queue (`model_service.embed.submit_sync`). Fundstelle: `server/memory/lzg_knoten.py` `embed_text_bauen`; `server/agents/synapsen_promotion/agent.py` `_eintrag_verarbeiten`; `server/services/model_services/`.

#### K10 — Match-Mechanik und Counter-Trigger

**Festlegung:** Hybrid Magnet + Vector (Pfad B, Onyx-Analogon):

1. **Vor-Filter** über Magnet-Felder: Knoten desselben
   `user_id+character_id` mit mindestens einer Magnet-Übereinstimmung
   (geteilte `entitaet_ids`, `themen`-Overlap, oder Timeline-Distanz
   unter Toleranz). GIN-Index-Lookups, schnell.
2. **Vector-Reranking** über den Kandidaten-Pool: Cosine berechnen,
   höchsten Treffer auswählen.
3. **Schwellwert:** `LZG_KNOTEN_MATCH_SCHWELLE = 0.85`.

**Auf Match — Reinforcement-Pfad:**
- `gewicht_roh += LZG_KNOTEN_REINFORCEMENT_BOOST` (= 0.1)
- `gewicht_absolut` neu berechnen via Sinus-Dämpfung
- `haeufigkeit += 1`
- `verstaerkt_am = NOW()`
- Trigger 2: alle Kanten von/zu diesem Knoten neu berechnen

**Kein Match — Anlage-Pfad:**
- Neuer `lzg_knoten` mit `gewicht_roh = salienz`, `haeufigkeit = 1`
- Kanten gegen alle bestehenden Knoten berechnen (vier Schichten)

**Hinweis:** Aktivierung ist Schreibpfad-Logik (Konzept §7.1, §7.9.2,
§7.1 „Lesepfad löst keine Aktivierung aus"). Lesepfad bleibt passiv.

`[gemessen am Code 19.09.2026]` **abweichend.** Einen Magnet-Vorfilter gibt es nicht: Geladen wird die ganze Partition des Paars, der Docstring begründet das als spätere Optimierung. Die Schwelle ist `0.82`, nicht `0.85` (Notiz §4 in [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) §13.6). Dazu kommt ein dritter Pfad, die Halbreaktivierung deaktivierter Knoten (`_t` §9.3). Reinforcement, Trigger 2 und Anlage stehen wie festgelegt. Fundstelle: `server/memory/lzg_knoten.py` `kandidaten_mit_cosine_laden` (Docstring *„Hinweis: K10 …“*), `match_pruefen`, `knoten_verstaerken`, `reactivate_node`; `server/memory/lzg_kanten.py` `kanten_neuberechnen_fuer_knoten`, `kanten_fuer_neuen_knoten_bilden`.

`[entschieden 19.09.2026]` Der Code gilt, die Festlegung ist überholt — für den Vorfilter, die Schwelle und die Halbreaktivierung. Der Meister: *„Code gilt“*.

### Abschlussstand

`[entschieden 19.09.2026]` **P4 ist gebaut.** Abgeschlossen ist P4, sobald `SYNAPSEN-LIVE-VERIFY` (die Abnahme der Entitäts- und Timeline-Kanten, gemessen aus der Datenbank) und `KZG-ERSTELLT-AM-PARSE-HÄRTE` (zum Mitbauen in P4 vorgesehen, Notiz §7 in `_b`) geschlossen sind. Die übrigen fünf Folgeeinträge — `TRIGGER-2-RECACHE-KONZEPT-LÜCKE`, `REFAC-MAGNETE-AUDIT`, `EMOTIONS-VEKTOR-LEER`, M2.5b (FaktenAgent) und `DOKU-DRIFT-WELLE-PROMOTION` — laufen ohne P4-Bindung weiter. Der Meister: *„Zwei, Rest lösen“*. Der Zustand der Einträge steht im Backlog (`novaberg-backlog-gedaechtnis.md`, `novaberg-backlog-bauart.md`).
