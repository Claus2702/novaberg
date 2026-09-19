# Novaberg — Der Verfall der Shadow-Queue (Messungen)

**Teil 5 von 5 — Messungen.** Absicht und Kopfblock: [`novaberg-queue-verfall_k.md`](novaberg-queue-verfall_k.md) · Ausarbeitung: [`novaberg-queue-verfall_t.md`](novaberg-queue-verfall_t.md) · Bauplan und Umstellung: [`novaberg-queue-verfall_b.md`](novaberg-queue-verfall_b.md) · Diskussion und Ergänzungen: [`novaberg-queue-verfall_e.md`](novaberg-queue-verfall_e.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## Bisheriger Kopf

Der Stands-Kopf des ungeteilten Konzepts, ungekürzt. Er steht hier, weil er Messwerte trägt (Migration von 1036 Aufträgen, die offene Messung über 30 Tage Betrieb).

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Konzept — Warum ein Auftrag verfällt, wie er verfällt, und wohin die Queue dafür umzieht
**Stand:** 28. August 2026 (`ausloeser_turn_id` in §8 — Scheibe 4 des Lage-Konzepts). Davor: 23. August 2026 — v0.6, **der Fehlversuchspfad loescht nicht mehr hart** (§12.1, §14 markiert); davor 15. August 2026, Chat 141 — v0.5, gebaut, gemessen und die Nähte auditiert (§16)
**Pfad:** novaberg/docs/novaberg-queue-verfall_k.md
**Typ:** Konzept
**Status:** ✅ **Gebaut und gemessen am 15.08.2026.** Tabelle, Repository, Migration (1036 Aufträge), Schreib- und Auswahlpfad, Verfallslauf. §16 trägt die Messwerte. Offen: die Messung über 30 Tage Betrieb
**Verwandt:** `novaberg-autonomous-wissen_k.md` §11.6/§11.7 (**das Schwesterdokument — dort steht der Stapel, hier die Queue**) · `novaberg-memory-synapsen_k.md` §9 (das Vorbild) · `novaberg-kzg-salienz_k.md` §3 (die Aufbaukurve) · `novaberg-pixie.md` (das Modul)

---

## 2. Der Befund am Bestand

**Gemessen am 15.08.2026 um 13:52 UTC** über `shadow_queue:meister`. **Zählvorschrift:** alle Einträge aus `LRANGE 0 -1`, je Eintrag der JSON-Satz; Werkzeug `labor/werkzeug/queue_bestand_messung.py`.

```
Bestand            1036 Aufträge
Aufgabenarten      recherche 608 · vertiefen 383 · nachfragen 45
prioritaet         233 auf exakt 0,0        — davon vertiefen 233
                    18 im Band 0,67378–0,94393
                   785 im Band 0,94393–1,0
                   Median 0,9764 · Minimum 0,0 · Maximum 1,0
thema leer         145                      — vertiefen 141, nachfragen 4
Alter              0 bis 18 Tage, Median 9 — keiner über 30
_retries           43 Aufträge tragen das Feld
Gegenstände        878 verschiedene (aufgabe, thema)-Paare
```

> **Der Bestand wächst, während man ihn misst.** Eine Zählung wenige Stunden zuvor am selben Tag ergab 1032, die hier zitierte 1036. Das ist keine Messungenauigkeit, sondern der Gegenstand des Dokuments: **Es gibt einen Zufluss und keinen Abfluss außer der Ausführung.** Wer eine Zahl von hier zitiert, zitiert einen Zeitpunkt.

Drei Dinge stehen darin, die das Konzept tragen müssen.

**Erstens: Die Verteilung ist zweigipflig, nicht breit.** 785 von 1036 liegen im obersten Band, 233 auf null, dazwischen 18. Es gibt kaum mittlere Werte. **Eine Schwelle trennt hier nicht die schwachen von den starken Aufträgen — sie trennt die belegten von den unbelegten.** Wer erwartet, dass eine Schwelle von 0,3 beim ersten Lauf ein Drittel abräumt, misst die 233 Nullen und hält sie für Rauschen im Sinne von „schwach". Sie sind etwas anderes: Aufträge, deren Salienz nie geschrieben wurde.

**Zweitens: Der Bestand ist jünger als die Frist.** Kein Auftrag ist älter als 18 Tage, die Frist soll 30 sein. **Der erste Verfallslauf wird deshalb außer den 233 Nullen nichts finden** — und das ist kein Fehlschlag, sondern die richtige Vorhersage. Wer sie nicht vorher aufschreibt, hält den Lauf hinterher für wirkungslos.

**Drittens: 383 Aufträge warten auf einen Agenten, den es nicht gibt.** Im Verzeichnis `server/agents/` liegt kein `vertiefen`. Das sind 37 % des Bestands.

### 2.1 Die beiden Befunde sind einer

**Die stillen Nullen und die verwaisten Aufträge sind dieselbe Menge.** Aufgeschlüsselt am 15.08.2026:

```
prioritaet 0,0    233  —  davon vertiefen 233, recherche 0, nachfragen 0
thema leer        145  —  davon vertiefen 141, nachfragen 4
```

**Alle Nullen sind `vertiefen`-Aufträge, ausnahmslos.** Das war aus der Gesamtzahl nicht zu sehen und ändert die Deutung: Die stille Null ist kein Streufehler über alle Aufgabenarten, sondern eine Eigenschaft **eines** Pfades — desselben, der auf einen fehlenden Agenten zeigt und dessen Aufträge in 141 Fällen auch noch ohne Thema ankommen.

> **Drei Befunde, ein Pfad:** `information_teilen` → `vertiefen` erzeugt Aufträge ohne Salienz, oft ohne Thema, für einen Agenten, den es nicht gibt. Wer einen davon einzeln behebt, hat den Pfad nicht behoben. **Der Verfall räumt alle drei zusammen ab — und keiner davon ist damit behoben** (§15).

---

## Aus §12 — Der Lebenszyklus

§12.1 bis §12.5 stehen in [`novaberg-queue-verfall_t.md`](novaberg-queue-verfall_t.md).

### 12.6 Was die Prüfung gestützt hat

**Der Abfluss ist der eigentliche Befund.** Die Altersverteilung des Bestands dünnt zu den alten Tagen hin nicht aus:

```
18 Tage: 57   17 Tage: 54   16 Tage: 26   15 Tage: 74
14 Tage: 113  13 Tage: 151  …   2 Tage: 124   1 Tag: 104   0 Tage: 120
```

**Würde die Queue nennenswert abgearbeitet, müsste diese Verteilung zu den alten Tagen hin ausdünnen. Sie tut es nicht** — 57 Aufträge vom ältesten Tag liegen unberührt. Zusammen mit dem Zuwachs während der Messung heißt das: Der Zufluss übersteigt den Abfluss deutlich, und **der Verfall ist damit der einzige realistische Weg hinaus** für alles, was nicht drankommt.

**Was ungeprüft bleibt:** Die tatsächliche Abflussrate ist aus der Altersverteilung erschlossen, nicht aus dem `hintergrund_log` gezählt. Das trägt die Aussage „klein", nicht eine Zahl.

---

## 16. Gebaut und gemessen — 15.08.2026

*Die Bauberichte aus §16 — Einleitung, „Die Reihenfolge, in der gebaut wurde“, „Was der Bau am Konzept berichtigt hat“, „Fünf Bestandszeugen mussten nachgezogen werden“ und „Was der Audit der Nähte fand“ — stehen in [`novaberg-queue-verfall_b.md`](novaberg-queue-verfall_b.md).*

### Die Migration

| | |
|---|---|
| gelesen / geschrieben | **1036 / 1036**, 0 unlesbar |
| danach aktiv | **803** |
| danach ruhend | **233** — ausnahmslos `vertiefen` |
| je Aufgabenart | recherche 608 (608 aktiv) · vertiefen 383 (150 aktiv) · nachfragen 45 (45 aktiv) |
| `erstellt_am` | 27.07. bis 15.08.2026 |

**Die Vorhersage aus §13 ist exakt eingetroffen:** 233 Deaktivierungen, keine
weiteren. Gegengeprüft wurde außerdem, dass keine Zeile `salienz_decay >
salienz_absolut` trägt, keine aktive Zeile unter der Schwelle liegt und keine
ein fremdes Paar-Tripel hat — je 0 Treffer.

### Der Verfallslauf am echten Bestand

```
vorher    aktiv 803, ruhend 233
Lauf      805 verarbeitet, 0 deaktiviert, kein Fehler
nachher   aktiv 803, ruhend 233
Summe     1036 -> 1036   — nichts gelöscht
```

**0 Deaktivierungen sind das richtige Ergebnis**, nicht ein wirkungsloser
Lauf: Die 233 ruhen bereits, und kein übriger Auftrag ist 30 Tage alt. Die 805
gegenüber 803 sind zwei Zeilen eines Testpaares, die der Lauf global miterfasst
hat — der Verfall filtert nicht auf ein Paar, wie `run_node_decay` auch nicht.

Der Gewinner der Auswahl war der **jüngste** Auftrag (erstellt am selben Tag,
`salienz_decay` 0,9974) — die Rangfolge aus §12.3 im Betrieb.

### Die Kette, am laufenden Server belegt

```
15:46:23  Pixie[llm]: Gewinner — recherche (Prio 1.00, Quelle: shadow_auftrag)
15:46:23  RechercheAgent: Start — Thema aus Queue: 'kosmische Präzision, …'
```

Auswahl aus der Tabelle, Router, Registry, Agent — mit dem richtigen Thema.
Vor der Berichtigung endete es nach der ersten Zeile. Ein Auftrag mit Salienz
0,0 scheitert weiterhin laut, wie gefordert.

**Suite 1399 → 1404 grün** (fünf Zeugen der Verdrahtung).

### Was ungemessen bleibt, ausdrücklich

**Die eigentliche Wirkung — ein Auftrag fällt durch Alter heraus — ist am
Bestand nicht zu beobachten**, weil keiner alt genug ist. Sie ist über gesetzte
Zeitstempel geprüft (29 Tage aktiv, 31 Tage nicht), und das ist ein Zeuge,
keine Messung. Die echte Messung braucht 30 Tage Betrieb.

Ebenso ungemessen: die **Reaktivierung im Betrieb**. Dass sie rechnet, ist
belegt; dass ein wiederkehrender echter Anlass denselben Gegenstand trifft,
nicht.
