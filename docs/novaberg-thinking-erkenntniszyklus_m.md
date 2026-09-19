# Novaberg — Der Erkenntniszyklus: wie aus Sammeln Verstehen wird (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-thinking-erkenntniszyklus_k.md`](novaberg-thinking-erkenntniszyklus_k.md) · Ausarbeitung: [`novaberg-thinking-erkenntniszyklus_t.md`](novaberg-thinking-erkenntniszyklus_t.md) · Bauplan und Umstellung: [`novaberg-thinking-erkenntniszyklus_b.md`](novaberg-thinking-erkenntniszyklus_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-erkenntniszyklus_e.md`](novaberg-thinking-erkenntniszyklus_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 11. Die tragende Vorfrage — vor dem Bau zu beantworten

Der Zyklus setzt vor jede Recherche einen Denkaufruf. Bei 35 bis 38 Sekunden je Aufruf und **92 % übersprungenen Heartbeats** ist das zunächst zusätzliche Last. Sie rechnet sich nur, wenn Schritt 5 genug wegschneidet.

> **Welcher Anteil der 606 vorhandenen `recherche`- und `vertiefen`-Aufträge fiele an Schritt 5 weg, weil Nova das Thema bereits abgedeckt hat?**

Das ist **ohne neuen Lauf und ohne Modellaufruf** zu beantworten: die Themen-Einbettungen der Queue gegen Bibliothek und Langzeitgedächtnis, Trefferquote über der Schwelle. Die Zahl entscheidet, ob der Zyklus ein Sparmechanismus ist oder ein Aufschlag.

### ✅ Gemessen am 09.08.2026 — der Zyklus spart

614 Altaufträge, 518 davon mit Thema. Jedes Thema eingebettet und gegen beide Bestände gehalten. **Keine Schwelle gesetzt, sondern die Kurve berichtet** — die Schwelle ist der strittige Knopf, und ein Werkzeug, das sie setzt, entscheidet die Frage, die es messen soll.

| Schwelle | gesamt | `recherche` | `vertiefen` |
|---|---|---|---|
| 0,50 | 94,6 % | 96,2 % | 91,3 % |
| 0,55 | 88,0 % | 92,2 % | 79,8 % |
| **0,60** | **77,4 %** | 84,1 % | 64,2 % |
| 0,65 | 61,4 % | 69,9 % | 44,5 % |
| 0,70 | 41,5 % | 49,9 % | 24,9 % |
| 0,75 | 15,6 % | 19,4 % | 8,1 % |

Verteilung von `max_sim`: min 0,359 · p25 0,614 · **Median 0,681** · p75 0,730 · max 0,841.

**Die Antwort ist robust gegen die Schwellenwahl.** Selbst bei einer strengen 0,70 fällt gut ein Drittel weg, bei der Bibliotheksschwelle 0,60 mehr als drei Viertel. Der Denkaufruf vor der Recherche ist damit **kein Aufschlag, sondern eine Einsparung** — er ersetzt in der Mehrzahl der Fälle einen Netzlauf durch einen Blick in den eigenen Bestand.

**Die Aufteilung nach Auftragsart trägt mehr als die Gesamtzahl.** `recherche` ist an jeder Schwelle deutlich besser abgedeckt als `vertiefen` — bei 0,60 sind es 84,1 % gegen 64,2 %. Das passt zur Bauart beider: Die breite Recherche trifft Themen, zu denen ohnehin schon etwas liegt; die fokussierte Vertiefung zielt auf Lücken. **Ein Gesamtwert allein hätte den Unterschied verdeckt.**

### Woher die Abdeckung kommt — nicht von dort, wo der Zyklus sie vermutet

**Der nächste Treffer stammt in 86 % der Fälle aus dem Langzeitgedächtnis, nicht aus der Bibliothek.** Der Bibliotheks-Median liegt bei 0,563, der des Gedächtnisses bei 0,689.

Der erste Rohwert lautete 2,1 % für die Bibliothek und war zu einem Teil ein **Messgerätfehler**: Die Spalte `themen_embedding` bildet die lange `zusammenfassung` ab, ein Queue-Thema ist eine kurze Phrase. Die Kontrolle Thema-gegen-Thema (n=100, die 145 Bibliotheksthemen frisch eingebettet) hebt den Bibliotheksanteil von 2,1 % auf 14 % und den Median von 0,505 auf 0,563 — **das Register erklärt einen Teil des Abstands, aber nicht den Abstand.** Auch fair verglichen liegt die Bibliothek 0,126 unter dem Gedächtnis.

> **Für den Zyklus heißt das: Schritt 3 liest vor allem das Langzeitgedächtnis.** Die Bibliothek ist mit 168 Einträgen und 145 Themen kein kleiner Bestand mehr — sie wuchs seit dem 06.08. von 24 auf 168 —, sie ist als Deckungsquelle für kommende Themen aber zweitrangig. Wer die Vorprüfung des Kaltstarts (§7) nur gegen die Bibliothek baut, misst am falschen Bestand.

---
