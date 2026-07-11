# Novaberg — Lesson: Die Stichprobe ist repräsentativ für den Pfad, den sie trifft

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Terminierende Live-Turns beweisen nichts über Pfade, die sie nicht betreten haben
**Stand:** 11. Juli 2026, Chat 106
**Pfad:** novaberg/docs/novaberg-lesson_l_stichprobe-trifft-den-pfad.md
**Auslöser:** AGENT-RUECKFRAGE-LOOP — dreimal an einem Tag traf die Stichprobe den Pfad daneben
**Verwandt:** `novaberg-lesson_l_log-behauptet-was-es-weiss.md`, `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`, `novaberg-lesson_l_quelle-vor-destillat.md`

---

## 1. Der Fall — dreimal an einem Tag

**Chat 101:** Fünf Live-Turns terminierten sauber über den `bereits_gelaufen`-Guard → „Loop existiert nicht, nicht reproduzierbar." Der Loop saß im **Resume-Pfad**, und den hat die Stichprobe nie betreten — alle fünf Turns liefen über den Agent-Pfad, wo der Guard greift. Chat 103 reproduzierte den Loop. Beide hatten recht: Der Guard war nie kaputt — **er wurde nur nie gefragt.**

**Chat 106, spiegelverkehrt:** Nach dem Fix liefen neun Live-Turns sauber durch. **Und bewiesen nichts.** Alle neun waren `status=abgeschlossen`, alle neun nahmen den Agent-Pfad; die neue Guard-Zeile (`Planner: Resume — …`) stand in keinem einzigen Log.

> Beinahe wäre derselbe Denkfehler passiert wie in Chat 101 — nur spiegelverkehrt.
> Chat 101: „Neun Turns terminieren → Loop existiert nicht."
> Chat 106: „Neun Turns terminieren → Loop ist gefixt."
> Beide Male: Die Stichprobe traf den Pfad daneben.

Der Loop braucht zwingend eine **Rückfrage** — ohne Rückfrage kein Pending-Key, ohne Pending-Key kein Resume-Pfad. Erst die gezielte Provokation (Notiz-Duplikat → Rückfrage → **Gegenfrage** statt Wahl) betrat den Pfad und lieferte den Beweis (11.7. 18:14:01, fünf Millisekunden, ein Durchlauf — vorher 60 Iterationen in 230 ms).

**Drittes Mal, am selben Abend:** Beim Self-Trigger-Kanalbeweis traf der erste erzwungene Turn den **Erfolgspfad** (`Nachfass-Iteration 1/2` → `Antwort korrigiert`) — der Doppel-Fehlschlag war nie eingetreten. Die Messung war korrekt, aber sie traf den Pfad daneben. Erst der zweite Anlauf (deterministisch erzwungener Zweig) lieferte den Kanal-Beweis.

---

## 2. Die Regel

> **Wo Vollständigkeit billig ist (grep, `count(*)`), ist sie Pflicht — eine Stichprobe wäre dort Faulheit, die sich gründlich anfühlt. Wo sie teuer ist (Live-Turns), prüft man den PFAD, nicht die MENGE. Und die Pfadliste kommt aus dem Code, nicht aus dem Gefühl.**

Praktisch heißt das:

1. **Vor dem Live-Test die Pfadliste aufstellen** — welche Zweige hat die Funktion, welcher trägt den Verdacht? (Der Planner hat vier Pfade; der Verdacht saß in genau einem.)
2. **Den Zieltest so bauen, dass er den Verdachts-Pfad zwingend betritt** — notfalls provozieren (Gegenfrage statt Wahl) oder deterministisch erzwingen (temporäres Force-Flag, danach rückstandsfrei entfernen).
3. **Am Log verifizieren, dass der Pfad wirklich betreten wurde** — die neue Guard-Zeile muss im Log STEHEN, nicht nur der Turn terminieren. N saubere Durchläufe ohne die Zeile sind kein Beweis, sie sind N Treffer auf dem falschen Pfad.

---

## 3. Warum sich der Fehler so gut tarnt

Terminierende Turns fühlen sich wie Evidenz an — sie sind echte, live gemessene Daten. Genau das macht sie gefährlicher als eine ehrlich eingestandene Vermutung: Die Stichprobe IST repräsentativ — aber nur für die Verteilung der Pfade im Alltagsbetrieb, nicht für den seltenen Pfad, in dem der Bug wohnt. Ein Bug im 2-%-Pfad übersteht beliebig viele 98-%-Stichproben.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Schwester-Lessons: `novaberg-lesson_l_log-behauptet-was-es-weiss.md`, `novaberg-lesson_l_analyse-ersetzt-keine-messung.md`
→ Modul-Dokument: `novaberg-node-planner.md` §3.1
→ Bug-Eintrag: AGENT-RUECKFRAGE-LOOP (✅ Chat 106, novaberg-bugs.md)
