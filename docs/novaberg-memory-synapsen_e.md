# Novaberg — Memory-Kern: Synapsen-Modell (Diskussion und Ergänzungen)

**Teil 4 von 5 — Diskussion und Ergänzungen:** Entscheidungen, offene Fragen, verworfene Varianten, Befunde. Absicht und Kopfblock: [`novaberg-memory-synapsen_k.md`](novaberg-memory-synapsen_k.md) · Ausarbeitung: [`novaberg-memory-synapsen_t.md`](novaberg-memory-synapsen_t.md) · Bauplan und Umstellung: [`novaberg-memory-synapsen_b.md`](novaberg-memory-synapsen_b.md) · Messungen: [`novaberg-memory-synapsen_m.md`](novaberg-memory-synapsen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`. Die Abschnitte dieser Datei tragen Buchstaben, damit sie nicht mit den Abschnittsnummern des Konzepts verwechselt werden.

---

## A. Entschieden

Beide Entscheidungen stehen in dem Abschnitt, den sie tragen, und bleiben dort. Hier steht der Verweis.

| | Stelle | Gegenstand | Datum |
|---|---|---|---|
| **E1** | `_t` §7.1a, Unterabschnitt *„Woran ‚hergenommen‘ erkannt wird — entschieden am 04.09.2026“* | Verwendung wird über die Embedding-Nähe zwischen Antwort und Erinnerung erkannt, nicht über eine Selbstauskunft des Verfassers — *„Er könnte aber auch fantasieren“*. Die Segmentierung, die derselbe Unterabschnitt zuerst vorsah, ist vor dem Bau widerlegt | 04.09.2026 |
| **E2** | `_b` §11, Absatz *„Beschluss …: selektive manuelle Übernahme, danach alte Tabelle löschen“* | Bestandsdaten des alten Langzeitgedächtnisses werden von Hand ausgewählt übernommen, danach wird die alte Tabelle gelöscht. **Gegenstandslos geworden am 27.07.2026, ausgeführt nie** (Kasten am Kopf von §11) | Konzeptphase, Mai 2026 — der Abschnitt nennt kein Datum |

Der Wortlaut der Entscheidungen steht in keinem der beiden Abschnitte; beide geben sie als Ergebnis wieder.

**Im Text als entschieden geführt, ohne dass ein Urheber genannt ist — nicht gezählt:**

- `_b` §8.5.5, Absatz *„Zum Ablageort der Tabelle“*: *„Entschieden für `ei/dreischicht.py`“* (02.08.2026, beim Bau von P10).
- `_t` §10.1: *„Die Paar-Spalten sind nullable, und das ist eine Entscheidung.“*
- `_b` §13.1, *Cold-Start akzeptiert*: *„Bewusste Designentscheidung“*.
- `_t` §8.5.3: *„Umgesetzt mit Faktor 0.0“* statt eines Werts aus der Spanne 0.0 bis 0.05.

Die Festlegungen K1 bis K10 für Sprint P4 stehen in einer eigenen Datei, `novaberg-memory-synapsen-p4-entscheidungen_k.md`, und sind hier nicht gezählt.

---

## B. Offen beim Meister

Keine. Das Konzept stellt keine Frage an den Meister.

**Offen ohne Frage an den Meister** — Beobachtungen und Messungen, die das Konzept selbst als offen führt:

- Abschnitt D unten (§7.11): Container-Verhalten bei unterschiedlichen Präzisionen, Themen-Normalisierung, Validierung von `LZG_EMBEDDING_SCHWELLWERT`.
- `_m`, *Aus §8.5* (§8.5.6): ob die Wahrnehmungs-Gravitation die Trefferliste je ändert — *„Das ist die offene Frage von P10“*, entscheidbar erst an der Charakterbildungs-Messreihe.
- `_t` §7.1a: eine echte Nulllinie über nachweislich fremde Knoten fehlt; die Segmentzahl ist neu zu messen, wenn die Antworten länger und mehrteilig werden.
- `_m`, *Bisheriger Kopf*: ob Entitäts- und Zeitschicht greifen, wenn es etwas zu greifen gibt — ebenfalls an der Charakterbildungs-Messreihe.
- `_k` §3.2: das Faktengedächtnis als eigenes Konzeptpapier, *„sobald der LZG-Kern dieses Konzepts steht“*.

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
| **B3** | `_t` §6 | `LZG_KNOTEN_REINFORCEMENT_BOOST = 0.5`; `_t` §4.1 (*Was die Skala … bedeutet*) nennt `= 0.1` je Verstärkung, ebenso `novaberg-memory-synapsen-p4-entscheidungen_k.md` K10 und §4 | `[gelesen 19.09.2026]` |
| **B4** | `_t` §6, `_t` §7.5 (Beispiel 2), Abschnitt D (§7.11) | `LZG_EMBEDDING_SCHWELLWERT = 0.85`; `novaberg-embedding-casing-blind_k.md` führt 0.85 als alten und **0.55** als neuen Wert (p99 = 0.568) | `[gelesen 19.09.2026]` |
| **B5** | `_t` §7.7 (dazu §7.2 Schritt 4, §8.4.2 Feld `kzg_quell_key`; `_b` §13.6) | Der KZG-Eintrag werde nach der Promotion aus Redis gelöscht; `novaberg-embedding-casing-blind_k.md` (Nachtrag 04.09.2026) und `novaberg-kzg-salienz_k.md` (`PROMOTION-ENTFERNT-KZG-NICHT`) sagen, das geschieht nicht | `[gelesen 19.09.2026]` |
| **B6** | `_k` §3.1 | *„parallel zum bestehenden `langzeitgedaechtnis`“*; die Tabelle ist gelöscht (`_b` §11, Kasten am Kopf; `_b` §13, P9) | `[gelesen 19.09.2026]` |
| **B7** | `_t` §7.8 | Der erste LLM-Call (Klassifikation) *„bleibt grundsätzlich erhalten“*; `novaberg-memory-synapsen-p4-entscheidungen_k.md` K1 legt *„Keine LLM-Reifeprüfung im neuen Pixie-Agent“* fest, K3 lässt Call 1 und Call 2 in P4 entfallen | `[gelesen 19.09.2026]` |
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
