# Novaberg — Der Verfall der Shadow-Queue

**Absicht:** Ein Auftrag der Shadow-Queue verliert mit der Zeit an Dringlichkeit, ruht nach 30 Tagen ohne neuen Anlass, statt gelöscht zu werden, und kehrt bei einem neuen Anlass zum selben Gegenstand mit halber Dringlichkeit zurück; nur ein abgearbeiteter Auftrag verschwindet ganz.
**Stand:** 28. August 2026 (am 19.09.2026 in fünf Teile aufgeteilt, ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Queue-Verfall* 🟢 — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-queue-verfall_t.md`](novaberg-queue-verfall_t.md) · [`novaberg-queue-verfall_b.md`](novaberg-queue-verfall_b.md) · [`novaberg-queue-verfall_e.md`](novaberg-queue-verfall_e.md) · [`novaberg-queue-verfall_m.md`](novaberg-queue-verfall_m.md)
**Entschieden:** 10 · **Offen beim Meister:** 2 (Liste in [`novaberg-queue-verfall_e.md`](novaberg-queue-verfall_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-queue-verfall_k.md §12` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-queue-verfall_t.md`](novaberg-queue-verfall_t.md), `_b` ist [`novaberg-queue-verfall_b.md`](novaberg-queue-verfall_b.md), `_e` ist [`novaberg-queue-verfall_e.md`](novaberg-queue-verfall_e.md), `_m` ist [`novaberg-queue-verfall_m.md`](novaberg-queue-verfall_m.md).

| § | Datei |
|---|---|
| 1 | `_k` |
| 2 · 2.1 | `_m` |
| 3 · 3.1 · 3.2 | `_t` |
| 4 | `_t` |
| 5 | `_t` |
| 6 · 6.1 · 6.2 | `_t` |
| 7 · 7.1 · 7.2 · 7.3 | `_t` |
| 8 | `_t` |
| 9 | `_t` |
| 10 | `_b` |
| 11 | `_t` |
| 12 · 12.1 · 12.2 · 12.3 · 12.4 · 12.5 | `_t` |
| 12.6 | `_m` |
| 13 | `_b` |
| 14 | `_k` |
| 15 | `_e` (Abschnitt D) |
| 16 | `_b`: Einleitung, *Die Reihenfolge, in der gebaut wurde*, *Was der Bau am Konzept berichtigt hat*, *Fünf Bestandszeugen mussten nachgezogen werden*, *Was der Audit der Nähte fand*; `_m`: *Die Migration*, *Der Verfallslauf am echten Bestand*, *Die Kette, am laufenden Server belegt*, *Was ungemessen bleibt, ausdrücklich* |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Status, Verwandt) | `_m` |
| Versionshistorie | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

---

## 1. Warum dieses Dokument — und warum es kein zweites ist

**Die Shadow-Queue wächst und schrumpft nie.** Am 15.08.2026 liegen 1036 Aufträge darin, der älteste 18 Tage alt. Es gibt keinen Weg hinaus außer der Ausführung und dem Verwerfen nach drei Fehlversuchen. Ein Auftrag, den niemand je ausführt, bleibt für immer.

> **Nachgemessen am 23.08.2026: 590 Aufträge, 343 aktiv und 247 stillgelegt.** Der Bestand schrumpft — er sieht nur nicht danach aus, weil ein abgearbeiteter Auftrag gelöscht wird und keine Zeile hinterlässt, an der man ihn zählen könnte. Am 23.08.2026 zwischen 15:20 und 20:25 UTC gemessen: 653 → 597 Zeilen bei unveränderten 247 Stillgelegten, also rund elf abgearbeitete je Stunde.

> **Es gibt auch keine Obergrenze — entgegen dem, was das Moduldokument sagte.** `novaberg-pixie.md` §3 führte *„Max 20 Eintraege pro User"* als Eigenschaft der Shadow-Queue. Geprüft am 15.08.2026: Im Schreibpfad (`shadow_queue_push`) steht kein `LTRIM`, keine Längenprüfung, keine Konstante dieser Art; im ganzen Modul gibt es keinen Begrenzer. Der Bestand von 1036 ist der Beleg. **Die Zahl war eine Absicht, die als Zustand geschrieben stand** — und solange jemand sie glaubte, gab es keinen Anlass, nach einem Verfall zu fragen.

> **Ein Auftrag ist ein Vorsatz, kein Sachverhalt.** Ein Sachverhalt bleibt wahr, wenn man ihn liegen lässt. Ein Vorsatz verliert seinen Anlass — die Lage, aus der er entstand, ist nach zwei Wochen eine andere. Was der Verfall entfernt, ist deshalb nicht Speicherplatz, sondern **die Behauptung, dieser Vorsatz gelte noch**.

### Was es zu diesem Gegenstand schon gibt

**`novaberg-autonomous-wissen_k.md` §11.6 beschreibt dieselbe Bauart für zwei andere Speicher** — den Stapel und die Bibliothek. Dort steht die dreistufige Kurve, das Soft-Delete über `aktiv`, die Spaltenliste und die Entscheidung, wer den Verfall rechnet (§11.7).

**Dieses Dokument ist deshalb keine Neuerfindung, sondern die Übertragung auf einen dritten Speicher.** Wo §11.6 trägt, wird verwiesen statt wiederholt. Was hier neu ist, ist dreierlei: die Queue kam in §11.6 nicht vor, sie liegt auf einer anderen Skala, und sie muss dafür umziehen.

**Die Abgrenzung, damit die beiden nicht auseinanderlaufen:**

| Speicher | Dokument | Inhalt | Verfall |
|---|---|---|---|
| `shadow_queue` | **hier** | Aufträge — was getan werden soll | eigene Rate, 30 Tage |
| `shadow_stack` | `autonomous-wissen_k.md` §11.6 | ungesagte Gedanken | eigene Rate, 60 Tage |
| `autonomous_wissen` | `autonomous-wissen_k.md` §11.6 | erarbeitetes Wissen | die des LZG |
| `lzg_knoten` | `memory-synapsen_k.md` §9 | Erinnerung | 0,0015/Tag |

**Drei Speicher, eine Bauart, drei Raten.** Die Bauart wird geteilt, weil sie sich bewährt hat. Die Raten nicht, weil ein unerledigter Auftrag schneller gegenstandslos wird als ein Gedanke, und ein Gedanke schneller als eine Erinnerung.

---

## 14. Was nicht enthalten ist

- **Der Stapel zieht nicht um.** Er bleibt in Redis, mit den Konstanten aus `novaberg-autonomous-wissen_k.md` §11.6. Der Grund steht in §7.2 und ist gemessen, nicht vermutet.
- **Wiederkehrende Aufgaben bleiben, wie sie sind.** Sie dürfen über 1,0 steigen und immer gewinnen; das ist gewollt. Ihr Aging (`_aging_zuschlag`) ist ein anderer Mechanismus mit einem anderen Zweck — Verhungerungsschutz statt Verfall — und wird von hier nicht berührt.
- ~~**Der Retry-Pfad bleibt, wie er ist.** Nach `_RETRY_GRENZE` = 3 Fehlversuchen wird ein Auftrag **hart** verworfen.~~ → **Am 23.08.2026 geändert.** Das Argument *ein Ausführungsfehler ist kein Verfall* war formal richtig und hat gegen die Messung nicht gehalten: Über die 582 aktiven `recherche`-Einträge stieg die mittlere `salienz_roh` monoton mit der Versuchszahl — **der Verfall entfernte weich, was niemanden interessiert, der Fehlversuch hart, was am meisten interessiert.** Seither legt auch dieser Weg still, mit eigenem `grund`.

  > **Die Zahl selbst ist inzwischen nicht mehr reproduzierbar** (nachgemessen 23.08.2026: 213 Aufträge bei null Versuchen, 3 bei einem, keiner darüber). Sie hat die Entscheidung getragen, und die Entscheidung steht — aber wer sie nachprüfen will, findet die Kurve heute nicht mehr.

  **Was bleibt:** Die **Auswahl** zieht weiter den Salienzstärksten zuerst, und der scheitert deshalb zuerst. Das ist eine eigene Absicht und nicht der Rest dieses Zuges.
- **Kein Verhungerungsschutz für Queue-Aufträge.** Was die periodischen Aufgaben über `_aging_zuschlag` bekommen, bekommt die Queue ausdrücklich **nicht**: Ein Vorsatz wird nicht dringlicher, weil er lange liegt (§12.3). Ein Aging-Zuschlag auf `salienz_decay` würde den Verfall teilweise aufheben und ist deshalb nicht nur unnötig, sondern gegenläufig.
- **Keine Mengengrenze und kein Jahresablauf** (§12.5). Wächst der Bestand über das Erträgliche, wird `QUEUE_DECAY_RATE` verstärkt.
- **Die Umbenennung von `prioritaet`** geschieht im Umzug, weil die Spalten dort ohnehin neu entstehen — nicht als eigener Zug (§3.1).
- **Keine Ähnlichkeitsprüfung bei der Dublettenerkennung.** Gleiches `aufgabe` und `thema`, mehr nicht (§6.1).
