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
| **E6** | Abschnitt G unten, K8 | Das Anfangsgewicht wird **nicht** umgerechnet: Der Einstiegspunkt ist so gewünscht, nach oben bedient die Verstärkung die Skala | 20.09.2026 |
| **E5** | Abschnitt G unten, *Abschlussstand* | P4 schließt mit `SYNAPSEN-LIVE-VERIFY` und `KZG-ERSTELLT-AM-PARSE-HÄRTE`, die übrigen fünf Folgeeinträge laufen ohne P4-Bindung — *„Zwei, Rest lösen“* | 19.09.2026 |
| **E7** | `_t` §7.1a, Vermerk unter der Regel; Abschnitt G unten, K10 | **Ein Embedding-Treffer der Promotion verstärkt nicht — es gilt §7.1a.** Die Frage, vorgelegt am 22.10.2026 (B): *Soll ein Embedding-Treffer in der Promotion einen bestehenden LZG-Knoten weiter verstärken?* Zwei Stellen widersprachen sich: die Regel §7.1a, *„Verstärkt wird ausschließlich, was Nova in ihrer Antwort tatsächlich hergenommen hat“*, und die Festlegung K10, nach der ein Treffer ab Kosinus 0,82 den bestehenden Knoten samt Trigger 2 verstärkt — so ist es gebaut (`agents/synapsen_promotion/agent.py`, Verstärkungspfad). Vorgelegt waren **(a)**, empfohlen: *Es gilt §7.1a — ein Treffer verhindert nur die Dublette und verstärkt nicht*; die Folge: Kommt ein Thema im Gespräch wieder, ohne dass Nova es verwendet, wird es im Langzeitgedächtnis nicht stärker. **(b)**: *K10 gilt.* **Entschieden: (a)** (23.10.2026, 05:41 UTC, Wortlaut der Antwort, die zugleich eine Frage des Faktengedächtnisses beantwortete — [`novaberg-memory-fakten_e.md`](novaberg-memory-fakten_e.md) A Nr. 45: *„Beide wie empfohlen“*). Grund: Ein Treffer ist Nachbarschaft, keine Verwendung — genau die zweite Sperre, die §7.1a im Schreibpfad setzt; gemessen am 04.09.2026 trugen 95,2 % der Verstärkungen über den Treffer `cosine = 1.0000`, waren also Selbsttreffer eines stehengebliebenen KZG-Eintrags (`KZG-EINTRAG-BLEIBT-NACH-PROMOTION`). **K10 ist damit überholt, soweit es die Verstärkung beim Treffer betrifft** — samt Trigger 2 in diesem Pfad. Nicht berührt sind der Vorfilter (nach E3 überholt), die Schwelle 0,82 (nach E3) und der Schutz vor der Dublette. Der Code verstärkt weiter: `LZG-PROMOTION-TREFFER-VERSTAERKT` | 23.10.2026 |

Der Wortlaut von E1 und E2 steht in keinem der beiden Abschnitte; beide geben sie als Ergebnis wieder. E3 bis E5 stehen wörtlich am Punkt. E7 steht wörtlich in seiner Zeile und unter K10.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_b` §8.5.5, Absatz *„Zum Ablageort der Tabelle“*: *„Entschieden für `ei/dreischicht.py`“* (02.08.2026, beim Bau von P10).
- `_t` §10.1: *„Die Paar-Spalten sind nullable, und das ist eine Entscheidung.“*
- `_b` §13.1, *Cold-Start akzeptiert*: *„Bewusste Designentscheidung“*.
- `_t` §8.5.3: *„Umgesetzt mit Faktor 0.0“* statt eines Werts aus der Spanne 0.0 bis 0.05.

Die Festlegungen K1 bis K10 für Sprint P4 stehen in Abschnitt G unten, mit dem Messergebnis am Code, und sind hier nicht gezählt; gezählt sind die Entscheidungen des Meisters dazu (E3 bis E5).

---

## B. Offen beim Meister

~~Keine. Das Konzept stellt keine Frage an den Meister.~~ → ~~Eine, offen seit dem 22.10.2026 (am Code geprüft):~~ → Keine. Die eine vom 22.10.2026 ist am 23.10.2026 entschieden (A, E7):

- ~~**§7.1a gegen K10 — verstärkt der Embedding-Treffer der Promotion einen bestehenden Knoten?** `_t` §7.1a sperrt die bloße Nachbarschaft im Schreibpfad: Verstärkt wird nur, was die Antwort hergenommen hat. K10 (Abschnitt G) sieht bei einem Treffer der Promotion (Kosinus ≥ 0,82) die Verstärkung samt Trigger 2 vor, und der Code führt sie aus (`agents/synapsen_promotion/agent.py`, Verstärkungspfad). Gebaut ist die Regel §7.1a nur am Weg der Verwendung (`memory/usage_reinforcement.py`). Bis zur Entscheidung verstärken beide Wege (Vermerke in `_t` §7.1a und unter K10).~~ → **Entschieden am 23.10.2026: (a), es gilt §7.1a** — ein Treffer der Promotion verhindert nur die Dublette und verstärkt nicht (A, E7). Der Code verstärkt weiter; der Defekt trägt die Kennung `LZG-PROMOTION-TREFFER-VERSTAERKT`.

**Offen ohne Frage an den Meister** — Beobachtungen und Messungen, die das Konzept selbst als offen führt:

- Abschnitt D unten (§7.11): Container-Verhalten bei unterschiedlichen Präzisionen, Themen-Normalisierung, Validierung von `LZG_EMBEDDING_SCHWELLWERT`.
- `_m`, *Aus §8.5* (§8.5.6): ob die Wahrnehmungs-Gravitation die Trefferliste je ändert — *„Das ist die offene Frage von P10“*, entscheidbar erst an der Charakterbildungs-Messreihe.
- `_t` §7.1a: eine echte Nulllinie über nachweislich fremde Knoten fehlt; die Segmentzahl ist neu zu messen, wenn die Antworten länger und mehrteilig werden.
- `_m`, *Bisheriger Kopf*: ob Entitäts- und Zeitschicht greifen, wenn es etwas zu greifen gibt — ebenfalls an der Charakterbildungs-Messreihe.
- ~~`_k` §3.2: das Faktengedächtnis als eigenes Konzeptpapier, *„sobald der LZG-Kern dieses Konzepts steht“*.~~ → **Erledigt am 17.10.2026:** [`novaberg-memory-fakten_k.md`](novaberg-memory-fakten_k.md). Die Voraussetzung ist am selben Tag als erfüllt entschieden; die Sequenz im Enricher (`_k` §3.2) ist im Ort überholt.
- ~~Abschnitt G, K8 (E4): ob das Anfangsgewicht neuer Knoten umgerechnet wird — entscheidbar erst nach der Messung der Anfangsgewichte aus der Datenbank.~~ **Gemessen und entschieden am 20.09.2026 (E6), siehe K8.**

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
- Abschnitt G, K10, *Auf Match — Reinforcement-Pfad*, und `_b` §13.6, Notiz §5 — die Verstärkung eines bestehenden Knotens beim Embedding-Treffer der Promotion, samt Trigger 2; überholt am 23.10.2026, weil ein Treffer Nachbarschaft ist und keine Verwendung (E7). Der Code führt sie weiter aus (`LZG-PROMOTION-TREFFER-VERSTAERKT`).
- `_k` §14.2 und §14.3 — bewusst nicht übernommene Modelle der Forschung (ungerichtete Kanten, RDF-Tripel, eigenständige Kantenstärken, Multi-Timescale-Konsolidierung, Edge-Embeddings, STDP), je mit Grund.

---

## D. Aus §7 — Schreibpfad-Sicht

Die übrigen Unterabschnitte von §7 stehen in [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md).

### 7.11 Offene Detail-Punkte zum Schreibpfad

Diese Punkte sind noch nicht festgelegt und werden in den nächsten Konzept-Sessions geklärt oder im Live-Betrieb beobachtet:

- **Container-Verhalten bei unterschiedlichen Präzisionen.** Konzert um 20:00 (Minute) liegt innerhalb eines Urlaubs vom 1.–7. August (Tag oder Zeitraum). Strikte Präzisions-Gleichheit lässt zwischen ihnen keine Timeline-Kante zu — sie verbinden sich nur über Entitäten und Themen. Beobachten, ob das in der Praxis ausreicht; falls nicht, eine Containment-Bedingung als eigenen Auslöser nachrüsten.
- **Themen-Normalisierung.** Bestehender Bug-Cluster zur Themen-Vermischung („Annas Geburtstag" vs. „Geburtstag von Anna" vs. „Geburtstag"). Möglicher LLM-Call vor dem Knoten-Insert. Aktuell zurückgestellt, weil der zweite Promotion-Call entfällt; nachrüsten, wenn das Phänomen in der neuen Topologie sichtbar bleibt.
- **Initialwert `LZG_EMBEDDING_SCHWELLWERT = 0.85` validieren.** Im Live-Betrieb beobachten, wie häufig die Embedding-Schicht greift. Greift sie zu selten, Schwellwert auf 0.80 oder 0.75 absenken. → Der Code setzt `0.55`, seit dem 12.07.2026 kalibriert auf das Embedding-Modell `nomic-embed-text-v2-moe` (am Code geprüft am 22.10.2026, `server/config.py`); *Steht in* `_t` §6, Vermerk unter dem Block.

---

## E. Befunde der Doku-Sichtung vom 19.09.2026

Gefunden, nicht aufgelöst. Auflösen heißt, gegen den Code oder den Meister prüfen — das ist ein eigener Schritt. B1 bis B10 stammen aus der Sichtung, B11 bis B14 sind beim Aufteilen am selben Tag gelesen.

| | Stelle | Was gegen was steht | Herkunft |
|---|---|---|---|
| **B1** | `_m`, *Bisheriger Kopf*, Feld **Stand** (Glied *„davor 2. August 2026“*) | Der Kopf sagt *„P1 bis P9 gebaut, P10 offen“*; `_b` §13 sagt *„Alle zehn Sprints sind gebaut“*, und `_b` §13.12 wie `_t` §8.5 führen P10 als gebaut am 02.08.2026 | `[gelesen 19.09.2026]` |
| **B2** | Abschnitt F unten, bisherige Schlusszeile | Die Zeile nennt als Konzept-Stand eine Sitzung der Konzeptphase und beschreibt die Sprints als künftig; der Kopf trägt den Stand 18.09.2026, `_b` §13 den abgeschlossenen Bau | `[gelesen 19.09.2026]` |
| **B3** | `_t` §6 | `LZG_KNOTEN_REINFORCEMENT_BOOST = 0.5`; `_t` §4.1 (*Was die Skala … bedeutet*) nennt `= 0.1` je Verstärkung, ebenso die Festlegungen zu P4, K10 (Abschnitt G unten) und Notiz §4 (`_b` §13.6) | `[gelesen 19.09.2026]` · → am Code aufgelöst am 22.10.2026: `0.1`; *Steht in* `_t` §6, Vermerk unter dem Block |
| **B4** | `_t` §6, `_t` §7.5 (Beispiel 2), Abschnitt D (§7.11) | `LZG_EMBEDDING_SCHWELLWERT = 0.85`; `novaberg-embedding-casing-blind_k.md` führt 0.85 als alten und **0.55** als neuen Wert (p99 = 0.568) | `[gelesen 19.09.2026]` · → am Code aufgelöst am 22.10.2026: `0.55`; *Steht in* `_t` §6 und §7.5 (Beispiel 2 neu gerechnet), Abschnitt D |
| **B5** | `_t` §7.7 (dazu §7.2 Schritt 4, §8.4.2 Feld `kzg_quell_key`; `_b` §13.6) | Der KZG-Eintrag werde nach der Promotion aus Redis gelöscht; `novaberg-embedding-casing-blind_k.md` (Nachtrag 04.09.2026) und `novaberg-kzg-salienz_k.md` (`PROMOTION-ENTFERNT-KZG-NICHT`) sagen, das geschieht nicht | `[gelesen 19.09.2026]` · → am Code geprüft am 22.10.2026: das Löschen ist nicht gebaut; das Soll bleibt, der Defekt ist `KZG-EINTRAG-BLEIBT-NACH-PROMOTION`; *Steht in* `_t` §7.2, §7.7, §8.4.2 · → gebaut am 23.10.2026 im Code-Tree `2d18b83`, gelöscht wird nach einer Neuanlage; committet als `d11de95`, ~~im Betrieb nicht gemessen~~ → im Betrieb gemessen am 23.10.2026; *Steht in* `_t` §7.2, §7.7 |
| **B6** | `_k` §3.1 | *„parallel zum bestehenden `langzeitgedaechtnis`“*; die Tabelle ist gelöscht (`_b` §11, Kasten am Kopf; `_b` §13, P9) | `[gelesen 19.09.2026]` · → am Code aufgelöst am 22.10.2026, mit den übrigen veralteten Orten der Liste; *Steht in* `_k` §3.1 |
| **B7** | `_t` §7.8 | Der erste LLM-Call (Klassifikation) *„bleibt grundsätzlich erhalten“*; K1 der Festlegungen zu P4 (Abschnitt G unten) legt *„Keine LLM-Reifeprüfung im neuen Pixie-Agent“* fest, K3 lässt Call 1 und Call 2 in P4 entfallen | `[gelesen 19.09.2026]` · → am Code aufgelöst am 22.10.2026: kein LLM-Call; *Steht in* `_t` §7.8 |
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

`[entschieden 19.09.2026]` Die Begründung *„dieselbe Skala 0–10“* gilt seit Chat 113 nicht mehr. Ob umgerechnet wird, wird erst gemessen — der Meister: *„Erst messen“*.

`[gemessen 20.09.2026, laufende DB, nur lesend]` **Der Einstieg liegt bei 3,4 bis 4,0 von 10, nicht unten.** Die 2.413 nie verstärkten Knoten seit dem Skalenumbau (`ae69547`, 28.07.2026) tragen `gewicht_roh` 0,727 bis 1,0 und `gewicht_absolut` 3,376 bis 3,955; die Dämpfung hebt kleine Werte an, weil ihr Exponent unter 1 liegt. Kein Knoten liegt unter der Ruheschwelle 0,1, der kleinste `gewicht_decay` im Bestand ist 3,118, inaktiv sind 0. **Der heutige `gewicht_roh` ist nicht der Anlagewert** — Reinforcement erhöht ihn (Korrelation zu `haeufigkeit` 0,997; alle 1.759 Knoten über 1,0 sind verstärkte). Belege in `labor/2026-09-20_k8-skala/`; dieselbe Aussage steht seit dem 30.08.2026 in `_t` §5.4 (*„Der untere Bereich der Skala gehört dem Verfall, nicht der Anlage“*).

`[entschieden 20.09.2026]` **Es wird nicht umgerechnet; die Festlegung bleibt, nur ihre Begründung wird ersetzt.** Der Meister: *„Die Antwort auf die Frage mit der Synapsen-K8-Skala liegt im Konzept. Das ist alles bereits geplant und ausgearbeitet. Der Einstiegspunkt ist so gewünscht. Die Skala wird nach oben durch Verstärkung bedient.“* Die direkte Übernahme trägt also nicht mehr, weil beide Skalen gleich wären, sondern **weil der untere Bereich dem Verfall gehört**: Ein Knoten betritt die Skala bei 3 bis 4 und wandert nach unten, solange ihn niemand berührt, oder nach oben, wenn er wiederkehrt. Die Haltbarkeitsrechnung in `_t` §5.4 ist damit die Begründung des Einstiegspunkts. Gemessen werden die Anfangsgewichte neuer Knoten aus der Datenbank; danach entscheidet der Meister. Ein eigener Backlog-Eintrag folgt. P4 hängt nicht daran.

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

**Auf Match — Reinforcement-Pfad:** → *überholt am 23.10.2026 (E7, Vermerk unten): Ein Treffer verstärkt nicht.*
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

→ *Steht in* `_t` §7.1a, §7.9.2 und §9.3 (Vermerke vom 22.10.2026, am Code geprüft): Die Verstärkung beim Treffer, die K10 vorsieht und der Code ausführt, widerspricht der Regel §7.1a — ~~offen, nicht entschieden~~ → entschieden am 23.10.2026 für §7.1a (E7, unten). Trigger 2 läuft nur in diesem Pfad, nicht nach einer Verstärkung über die Verwendung (`LZG-KANTEN-NACH-VERWENDUNG-UNVERAENDERT`). → Seit dem Code-Tree `3a5ccab` (24.10.2026, Kennung wird nachgetragen) läuft Trigger 2 nach der Verstärkung über die Verwendung; der Pfad der Promotion ruft ihn seit dem 23.10.2026 nicht mehr (`_t` §7.9.2). Der halbe Wert der Halbreaktivierung hält nur bis zum nächsten Tageslauf (`LZG-HALBREAKTIVIERUNG-HAELT-EINEN-TAG`).

`[entschieden 23.10.2026]` (E7) **Die Verstärkung beim Treffer ist überholt; es gilt §7.1a.** Wortlaut der Antwort auf die Frage vom 22.10.2026, ob ein Embedding-Treffer der Promotion einen bestehenden Knoten weiter verstärkt — (a) *es gilt §7.1a, ein Treffer verhindert nur die Dublette und verstärkt nicht*, empfohlen; (b) *K10 gilt*: *„Beide wie empfohlen“* (23.10.2026, 05:41 UTC; die Antwort galt zwei Fragen). Ein Treffer ab `LZG_KNOTEN_MATCH_SCHWELLE` (0,82) legt weiter keinen neuen Knoten an — das ist der Schutz vor der Dublette, und er bleibt —, aber er ändert `gewicht_roh`, `gewicht_absolut`, `haeufigkeit` und `verstaerkt_am` nicht, und Trigger 2 entfällt in diesem Pfad. Verstärkt wird allein über die Verwendung in der Antwort (`_t` §7.1a). Der Code verstärkt beim Treffer weiter (`agents/synapsen_promotion/agent.py`, Zweig *Reinforcement-Pfad (K10)*); der Defekt trägt die Kennung `LZG-PROMOTION-TREFFER-VERSTAERKT`. Die Halbreaktivierung eines deaktivierten Knotens beim Treffer (`_t` §9.3) war nicht Gegenstand der Frage.

→ **Gebaut am 23.10.2026, im Code-Tree `5342a6a`** (Commit-Tree `2f6a3d1`, committet als `782274c`; ~~im Betrieb nicht gemessen, `LZG-PROMOTION-TREFFER-VERSTAERKT` offen bis dahin~~ → im Betrieb gemessen am 23.10.2026, `LZG-PROMOTION-TREFFER-VERSTAERKT` im Archiv): Der Zweig *Reinforcement-Pfad (K10)* heißt im Code *Dubletten-Pfad*, Aktion `dublette` — kein `knoten_verstaerken`, kein Trigger 2, kein neuer Knoten. Die Halbreaktivierung ist unverändert. Gelöscht wird der KZG-Hash nur nach der Neuanlage (Code-Tree `2d18b83`, `_t` §7.7); nach einer Dublette oder Halbreaktivierung bleibt er bis zur TTL.

### Abschlussstand

`[entschieden 19.09.2026]` **P4 ist gebaut.** Abgeschlossen ist P4, sobald `SYNAPSEN-LIVE-VERIFY` (die Abnahme der Entitäts- und Timeline-Kanten, gemessen aus der Datenbank) und `KZG-ERSTELLT-AM-PARSE-HÄRTE` (zum Mitbauen in P4 vorgesehen, Notiz §7 in `_b`) geschlossen sind. Die übrigen fünf Folgeeinträge — `TRIGGER-2-RECACHE-KONZEPT-LÜCKE`, `REFAC-MAGNETE-AUDIT`, `EMOTIONS-VEKTOR-LEER`, M2.5b (FaktenAgent) und `DOKU-DRIFT-WELLE-PROMOTION` — laufen ohne P4-Bindung weiter. Der Meister: *„Zwei, Rest lösen“*. Der Zustand der Einträge steht im Backlog (`novaberg-backlog-gedaechtnis.md`, `novaberg-backlog-bauart.md`).

`[gemessen 19.09.2026]` **P4 ist abgeschlossen: Beide Bedingungen sind geschlossen.** `SYNAPSEN-LIVE-VERIFY` ist aus der Datenbank abgenommen: Entität 1.831 von 1.831, Timeline 4.137 von 4.137 verpflichteten Paaren tragen ihre Kante. `KZG-ERSTELLT-AM-PARSE-HÄRTE` ist gebaut: Ein unlesbarer Anlagezeitpunkt wird verworfen statt erfunden. Die Belege stehen an beiden Einträgen im Backlog.
