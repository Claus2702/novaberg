# 01_L_b — Lesson: Thinker-Suchbegriff-Verzerrung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson Learned — Thinker-Suchbegriff aus Antwort statt aus Frage
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-node-thinker_l.md
**Ursprung:** nova-01-l-b.md
**Typ:** Lesson (L)
**Entdeckt in:** Chat 12 (25. März 2026)

---

## 1. Was passierte?

Nach der Integration von SearXNG (Web 7d) konnte der Thinker erstmals Web-Suchen durchführen, um die Antwort des Responders zu verifizieren. Beim Test mit der Frage „Wer ist aktuell Bundeskanzler von Deutschland?" lieferte der Responder die korrekte Antwort: „Friedrich Merz".

Der Thinker sollte diese Antwort verifizieren — und machte sie kaputt.

## 2. Diagnose

Der Thinker-Prompt instruierte: „Formuliere den Suchbegriff kurz und präzise." Ohne weitere Einschränkung nahm das LLM den prominentesten Namen aus der Antwort als Suchbegriff: `web_search(Olaf Scholz Bundeskanzler)` — weil Olaf Scholz als Vorgänger erwähnt wurde.

Die Web-Ergebnisse bestätigten: Olaf Scholz war bis Mai 2025 Bundeskanzler. Der Thinker interpretierte das als „kein aktueller Bundeskanzler" und ersetzte die korrekte Antwort durch eine falsche: „Aktuell gibt es keinen Bundeskanzler."

**Kernproblem:** Der Thinker nutzte die zu prüfende Antwort als Quelle für den Suchbegriff. Das ist ein Zirkelschluss: Wenn die Antwort falsch ist, sucht man nach dem falschen Begriff und bestätigt den Fehler — oder verschlimmert ihn.

## 3. Lösung

Neue Regel im `THINKER_SYSTEM_PROMPT`, Abschnitt `WEB-SUCHE:`:

```
Formuliere den Suchbegriff basierend auf der FRAGE DES NUTZERS,
nicht auf der Antwort des Assistenten. Wenn der Nutzer fragt
"Wer ist Bundeskanzler?", suche nach "aktueller Bundeskanzler
Deutschland 2026" — nicht nach einem Namen aus der Antwort.
Die Antwort könnte falsch sein, deshalb prüfst du ja.
```

**Nach dem Fix:** `web_search(aktueller Bundeskanzler Deutschland 2026)` → korrekte Ergebnisse → Antwort bestätigt.

## 4. Erkenntnis

**Verifikation darf nie die zu prüfende Quelle als Suchgrundlage verwenden.** Das gilt für jedes System mit Faktenprüfung — nicht nur für Web-Suche. Ein Faktenprüfer, der die Behauptung als Sucheingabe nimmt, findet nur Bestätigung oder verzerrte Ergebnisse. Die Prüfung muss immer von der ursprünglichen Frage ausgehen.

Das ist analog zu einem Wissenschaftler, der seine Hypothese nicht anhand der eigenen Daten bestätigt, sondern unabhängige Quellen konsultiert — formuliert aus der Fragestellung, nicht aus der Antwort.

---

→ Thinker-Node: `01_M_f`
→ Web-Service: `services/web_search.py`
→ Lesson Kontextuelle Kontamination: `01_L_a` (verwandtes Problem in anderem Kontext)
