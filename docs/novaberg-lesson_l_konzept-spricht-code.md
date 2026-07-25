# Novaberg — Lesson: Ein Konzept, das in Code-Sprache spricht, wird für einen Befund gehalten

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Konzeptsätze mit Code-Ankern sind von Audit-Ergebnissen nicht zu unterscheiden
**Stand:** 25. Juli 2026, Chat 108
**Pfad:** novaberg/docs/novaberg-lesson_l_konzept-spricht-code.md
**Typ:** Lesson (L)
**Auslöser:** `novaberg-charakter-resonanz_k.md` — zwei Konzeptaussagen, die wie Befunde gelesen wurden (Chat 104 und 108)
**Betrifft:** alle `_k`-Konzeptdokumente, Sprint-Vorbereitung, Brudi-Prompt-Schreiben
**Verwandt:** `novaberg-lesson_l_code-vor-doku.md`, `novaberg-lesson_l_schema-struktur-nicht-bedeutung.md`, `novaberg-lesson_l_pattern-vor-namen-suche.md`

---

## 1. Situation

Zwei Aussagen in `novaberg-charakter-resonanz_k.md` nannten Funktionsnamen, State-Keys und eine Aufrufreihenfolge — und waren Annahmen.

**§3 — die Graph-Reihenfolge.** Das Konzept schrieb: „Graph-Reihenfolge `ei_calc → thinker → responder → reducer`; der Reducer schreibt nach dem Responder." Falsch. Der Reducer läuft an Position 4, **vor** dem Responder, und sieht `state["response"]` nie; einen Key `final_response` gibt es nicht. Chat 104 musste den Schreibpunkt mitten im Sprint verschieben.

**§5 — der Schreibort der `verbindung`-Zeile.** Das Konzept schrieb: „Die `verbindung`-Zeile entsteht am KZG-Boost-Punkt (`_thematisch_verstaerken` / `kzg_store`-inline)." Der Chat-103-Audit hatte die **Orte** belegt — der Satz „hier entsteht die Zeile" war Brudis **Empfehlung** im selben Bericht und wurde als Befund übernommen.

**Die Kosten in Chat 108:** Die Vokabel „Boost-Punkt" wurde ungeprüft weitergereicht, als wäre sie belegt, und hätte beinahe eine Fehlkonstruktion getragen. Erst die Frage des Meisters — „Ich verstehe nicht, was ein KZG-Boost-Punkt ist" — hat sie aufgedeckt.

---

## 2. Erkenntnis

Ein Konzeptdokument spricht in der Sprache des Codes. Seine Sätze sehen aus wie Audit-Ergebnisse — und sind von echten Befunden nicht zu unterscheiden, auch nicht für den, der sie geschrieben hat.

Die Lücke ist unsichtbar, weil die ungeprüften Sätze klingen wie die geprüften. Das Konzept machte es an **einer** Stelle richtig (§6: „✅ Chat-103-Audit bestätigt") — und genau diese eine Markierung machte die anderen scheinbar überflüssig. Wer ein Häkchen sieht, liest den Rest als selbstverständlich mitbestätigt.

---

## 3. Prinzip

> **Jede Aussage in einem Konzeptdokument, die einen Funktionsnamen, State-Key, eine Spalte oder eine Aufrufreihenfolge nennt, braucht einen Herkunftsvermerk. Ohne Vermerk ist sie eine Annahme — auch wenn sie stimmt.**

Ein einzelnes bestätigtes Häkchen im Dokument ersetzt die Vermerke an den übrigen Stellen nicht. Es tarnt sie.

---

## 4. Konsequenz (umgesetzt Chat 108)

Jede solche Aussage trägt einen der drei Vermerke: **auditiert (Chat N)**, **Annahme** oder **überholt (Chat N)**. Ohne Vermerk gilt sie als Annahme. Die Regel steht seit Chat 108 im Kopf von `novaberg-charakter-resonanz_k.md` und gilt für alle `_k`-Dokumente.

Zwei Nachbarregeln aus derselben Sitzung:

- **Widerlegtes wird an seiner Stelle markiert**, nicht nur weiter unten korrigiert. §3 trug die falsche Graph-Reihenfolge vier Chats lang weiter, während §5 sie bereits richtigstellte. Wer oben liest und unten nicht ankommt, liest die widerlegte Fassung.
- **Zählungen tragen ihr Messdatum, Zeitstempel nicht.** Eine Zahl ist am Tag nach der Messung falsch; ein Stichtag bleibt wahr.

---

## 5. Verwandtschaft

- `novaberg-lesson_l_code-vor-doku.md` — Live-Code schlägt Doku und Erinnerung. Hier schlägt der Audit die plausible Konzept-Lesung: derselbe Vorrang, eine Ebene höher.
- `novaberg-lesson_l_schema-struktur-nicht-bedeutung.md` — eine Struktur belegt nicht, was sie bedeutet.
- `novaberg-lesson_l_pattern-vor-namen-suche.md` — nach Muster suchen, nicht nach dem Namen, den man erwartet.
- Geschwister-Lesson aus derselben Sitzung: `novaberg-lesson_l_ableitung-als-messung.md` — dort geht es um erschlossene **Werte**, hier um erschlossene **Code-Aussagen**.

---

*Diese Lesson ist Archiv. Wenn Aspekte zu ergänzen sind, wird eine neue Lesson geschrieben, nicht diese hier überarbeitet. Lessons = Gegenwart-mit-Datum, nicht Gegenwart-evolvierend.*

→ Konzeptdokument: `novaberg-charakter-resonanz_k.md` (Kopf: Herkunftsvermerk, §3 und §5: die beiden überholten Aussagen)
