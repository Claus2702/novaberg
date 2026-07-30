# Novaberg — Lesson: Ein Log darf nur behaupten, was es weiß

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Wer eine Wirkung loggt, die er nicht beobachten kann, baut einen Zeugen, der gegen ihn aussagt
**Stand:** 11. Juli 2026, Chat 106
**Pfad:** novaberg/docs/novaberg-lesson_l_log-behauptet-was-es-weiss.md
**Auslöser:** THINKER-SELFTRIGGER-KANALLOS — das Log behauptete das Gegenteil der Wahrheit
**Verwandt:** `novaberg-lesson_l_default-wie-fehlschlag.md`, `novaberg-lesson_l_silent-skip.md`, `novaberg-lesson_l_code-vor-doku.md`, `novaberg-lesson_l_ollama-think-content-split.md` (Nachtrag), `novaberg-lesson_l_fehlschlag-als-absicht.md`

---

## 1. Der Fall

Der Thinker loggte auf seinem Doppel-Fehlschlag-Pfad:

```
Thinker: Doppel-Fehlschlag — Self-Trigger fuer Klaerung gesetzt
```

Er wusste nur, dass er **in den State geschrieben** hatte. Ob es ankommt, weiß nur der Empfänger — und der Wert kam nie an: `self_trigger` und `self_trigger_payload` waren nicht als Channel deklariert und wurden an der ersten Node-Grenze (Thinker → Tribunal) still verworfen. Live bewiesen 11.7.2026, 18:35:22:

```
KANAL-TEST/Thinker: self_trigger im State gesetzt — vorhanden=True,  wert=True
KANAL-TEST (Tribunal):                              vorhanden=False, wert=None
```

Eine Millisekunde. Eine Node-Grenze. Wert weg. Nicht `False` — **nicht vorhanden**.

Der Bug war der schlimmste der drei Chat-106-Bugs, gerade WEIL er der leiseste war. Kraft 1 war *still* kaputt (kein Signal). Der Rückfrage-Loop war *laut* kaputt (Crash am Recursion-Limit). Dieser hier war **falsch beglaubigt**: Wer den Pfad debuggt, sieht „gesetzt" und sucht den Fehler woanders. Ein Wachposten (THINKER-DOPPELFEHLSCHLAG-LIVE) beobachtete wochenlang einen Pfad, der laut Log funktioniert. Und eine Lesson (`novaberg-lesson_l_ollama-think-content-split.md`) wurde in gutem Glauben über einen Mechanismus geschrieben, der nie funktioniert hat — **das lügende Log erzeugte ein Dokument, das die Lüge beglaubigt und archiviert.**

---

## 2. Die Regel

> **Ein Log darf nur behaupten, was es weiß. Wer eine Wirkung loggt, die er nicht beobachten kann, baut einen Zeugen, der gegen ihn aussagt.**

Der Thinker weiß: „ich habe in den State geschrieben". Er weiß NICHT: „der Folge-Durchlauf wird laufen". Das ehrliche Log lautet deshalb seit `090ac07`:

```
Thinker: Doppel-Fehlschlag — Self-Trigger im State gesetzt (self_trigger=True)
         — Auslieferung haengt am Event-Consumer
```

Das gilt auch für `node_annotations` und jede andere forensische Spur: Sie sind Zeugen. Ein Zeuge, der Wirkungen bekundet, die er nicht gesehen hat, vergiftet jede spätere Untersuchung.

---

## 3. Die Wurzel darunter: die Funktion, die das Wissen vorenthält

> **Ein Log kann nur so ehrlich sein wie die Funktion, die es aufruft.**

Der Audit über lügende Logs (Chat 106, 9 Funde: 2 HOCH, 5 MITTEL, 2 NIEDRIG) fand die eigentliche Wurzel **nicht auf der Log-Liste**: `broadcast()` (`api/websocket.py`) verschluckt jeden Send-Fehler intern und wirft nie. Das ist keine Log-Lüge — das ist eine **Funktion, die es unmöglich macht, die Wahrheit zu loggen.** Jeder Aufrufer, der „gesendet" schreibt (Event-Consumer, Shadow-Delivery), lügt nicht aus Nachlässigkeit — er lügt, weil er es nicht besser wissen *kann*.

> **Der Fix sitzt nie im Log. Er sitzt in der Rückgabe.**

Zwei wiederkehrende Klassen aus dem Audit, beide mit derselben Form („der Aufrufer kann nicht wissen, ob es geklappt hat"):

1. **`broadcast()`-Aufrufer**, die Rückkehr als Zustellung deuten — im schlimmsten Fall mit Folgeschaden: `SHADOW-DELIVERY-DATENVERLUST` löscht den Stack-Eintrag nach dem unverifizierten „Erfolg", mit dem Kommentar *„erst NACH erfolgreichem Senden"* — er beschreibt eine Prüfung, die es nicht gibt. Bei Totalausfall loggt die Zeile *„gesendet … 0 Clients"* — **das Log widerlegt sich selbst in derselben Zeile.**
2. **Batch-Zähler**, die exception-freie Durchläufe zählen, während die Arbeitsfunktion per stillem `return` verwerfen darf (`WIEDERVORLAGE-SNOOZE-OHNE-WIRKUNG`, `BATCH-ZAEHLER-ZAEHLEN-AUFRUFE`). Die Zahl, auf die man beim Debuggen schaut, lügt.

---

## 4. Die Anwendung (drei Regeln, umgesetzt in `090ac07`)

1. **Der Sender loggt seinen Write, nicht die Wirkung** — „im State gesetzt, Auslieferung hängt am Empfänger".
2. **Der Empfänger loggt jede Ankunft, nicht nur den Erfolgsfall** — sonst ist ein toter Kanal von „kein Trigger nötig" nicht unterscheidbar (`Event-Consumer: Self-Trigger im Result — vorhanden=…, wert=…`).
3. **Deckel greifen laut** — der `MAX_SELF_TRIGGERS`-Verwurf wird mit Zählerstand und Paar geloggt. Ein Deckel darf bewusst greifen, aber nicht heimlich.

Der Positivbefund gehört dazu: Die CRUD-Agenten verifizieren sich selbst (`RETURNING id` + `_verifizieren`), die model_services-Schicht propagiert Fehler über Futures. **Das Muster ist eingegrenzt, nicht flächendeckend** — es sitzt in den Zustell- und Batch-Pfaden, dort, wo etwas hinausgeht und niemand zurückschaut.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_stichprobe-trifft-den-pfad.md`, `novaberg-lesson_l_fehlschlag-als-absicht.md`, `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`
→ Modul-Dokumente: `novaberg-node-thinker.md` §3.5, `novaberg-convention-event-model.md` §7
→ Bug-Einträge: THINKER-SELFTRIGGER-KANALLOS (✅), BROADCAST-VERSCHLUCKT-FEHLER, SHADOW-DELIVERY-DATENVERLUST, WIEDERVORLAGE-SNOOZE-OHNE-WIRKUNG, BATCH-ZAEHLER-ZAEHLEN-AUFRUFE (novaberg-bugs.md, Chat 106)
