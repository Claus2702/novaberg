# 01_L_a — Lesson: Kontextuelle Kontamination

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Bewertungsverfälschung in Multi-Agent-Systemen
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-graph_l.md
**Ursprung:** nova-01-l-a.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 3 (14.–15. März 2026)
**Betrifft:** Tribunal (`01_M_i`), Salienz (`01_M_g`), Corrector (`01_M_j`)

---

## 1. Symptom

Drei unabhängige Fehler, die alle dieselbe Ursache hatten:

**Tribunal — False Positives:**
Der Jurist warnte bei jeder Terminerwähnung wegen „Datenschutz", obwohl die Daten vom Nutzer selbst stammten. Der Psychologe warnte bei sachlichen Wissensfragen wegen „fehlender Empathie". Ergebnis: 3 Korrektur-Runden statt 0, Antwortzeit >60 Sekunden statt ~20.

**Salienz — Emotionen verwässert:**
„Ich bin total überfordert mit der Arbeit, alles wird zu viel!" erhielt Salienz 0.40 statt der erwarteten 0.70+. Stress-Signale wurden nicht erkannt und landeten nicht im Kurzzeitgedächtnis.

**Corrector — Themen-Drift:**
Korrigierte Antworten drifteten in Richtung „TÜV-Stress", obwohl der aktuelle Prompt nichts mit dem TÜV zu tun hatte. Der Stress-Kontext kam aus dem Adaptive-Hash, nicht aus dem Prompt.

---

## 2. Ursache: Alles im selben Topf

Alle drei Agenten erhielten als Input eine Mischung aus primären und sekundären Daten — ohne Trennung. Ein LLM kann nicht „nicht beachten". Es integriert alles, was es sieht.

**Tribunal erhielt:**
```
BENUTZERANFRAGE: Was steht morgen an?
VERFÜGBARER KONTEXT: [Charakter: User ist gestresst wegen TÜV] [Timeline: Peters Geburtstag]
ANTWORT: Morgen ist Peters Geburtstag.
```

Der Jurist bewertete „Persönliche Informationen ohne Kontext" → Warnung. Der Psychologe bewertete „User ist gestresst, Antwort ignoriert das" → Warnung. Beides False Positives — der Kontext *erklärt* die Antwort, ist aber nicht das *Problem*.

**Salienz erhielt:**
```
User: Ich bin total überfordert mit der Arbeit!
Assistent: [200 Wörter beruhigende, sachliche Antwort mit Tipps]
```

Der Agent mittelte über den gesamten Turn. Die lange, ruhige Antwort verwässerte den Stress des Users.

**Corrector erhielt:**
```
TRIBUNAL-FEEDBACK: [Psychologe] User ist gestresst wegen TÜV
ANTWORT: [sachliche Information über Termine]
```

Der Corrector überarbeitete die Antwort in Richtung TÜV-Stress — ein Thema aus dem Hash, nicht aus dem Prompt.

---

## 3. Warum wir es nicht vorhergesehen haben

Die intuitive Annahme war: Mehr Kontext = bessere Bewertung. Das stimmt für den Responder (der generiert, nicht bewertet). Für bewertende Agenten gilt das Gegenteil: Mehr Kontext = mehr Verfälschung.

Das Problem trat nicht in einfachen Tests auf — nur bei Nutzern mit reichem Gedächtnis (Charakter-Hash, Timeline, KZG-Einträge). Je mehr das System über den Nutzer wusste, desto schlechter wurden die Bewertungen.

---

## 4. Die Analogie: Das Apotheker-Prinzip

Wenn jemand ein Tütchen mit kontrollierten Substanzen übergibt, ist die Bewertung fundamental verschieden je nach Kontext:

- **Apotheker mit Rezept im Laden:** Legal, korrekt, erwünscht.
- **Person nachts im Park:** Verdächtig, vermutlich illegal.

Der Kontext (Apotheke vs. Park) verändert die Bewertung des gleichen Vorgangs. Aber der Kontext selbst ist nicht das Bewertungsobjekt — der Vorgang ist es.

Übertragen auf Nova: Die Agenten müssen den Kontext **kennen** (um korrekt zu bewerten), aber sie dürfen ihn nicht **bewerten** (das verfälscht das Ergebnis).

---

## 5. Die Lösung: Lagebild / Bewertungsobjekt

Jeder bewertende Agent erhält seinen Input in zwei klar getrennten Blöcken:

```
═══ LAGEBILD (nicht Teil der Bewertung) ═══
- Intent und gewünschter Ton (aus Router/Perzeption)
- Persönlicher Kontext des Nutzers (aus KZG/LZG)
- Charakter-Hash (Kern + Adaptiv)
- Timeline-Einträge

═══ BEWERTUNGSOBJEKT (nur diesen Teil bewerten) ═══
- Benutzeranfrage (der aktuelle Prompt)
- Antwort des Assistenten (die zu bewertende Ausgabe)
```

Zusätzlich im System-Prompt jedes Agenten:
- Explizite Anweisung: „Bewerte AUSSCHLIESSLICH das Bewertungsobjekt"
- Perspektivspezifische Negativbeispiele (Jurist: „Persönliche Daten vom Nutzer sind kein Datenschutzproblem")
- Kalibrierung: „Im Zweifel: vote ok"

**Für die Salienz:** Bewertungsobjekt (User-Eingabe) steht am Ende des Prompts — nutzt den Recency Bias. Die Assistenten-Antwort steht oben im Lagebild: kontextgebend, aber nicht dominant.

---

## 6. Ergebnis

| Szenario | Vorher | Nachher |
|----------|--------|---------|
| Terminabfrage „Was steht morgen an?" | 3 Runden, ~15 LLM-Calls, >60s | 1 Runde, ~7 Calls, ~20s |
| Sachliche Wissensfrage | Psychologe warnt „fehlende Empathie" | Psychologe: ok |
| Persönliche Daten in Antwort | Jurist warnt „Datenschutz" | Jurist: ok |
| „Total überfordert mit der Arbeit!" | Salienz 0.40 | Salienz **0.70** |
| Charakter-Hash nach Korrektur | „Nutzer ist gestresst wegen TÜV" | „Begeisterung für Küche, Astronomie und KI" |

---

## 7. Vier generalisierbare Gesetze

### Das Kontaminations-Gesetz

> In einem Multi-Agent-System verfälscht jede Information, die ein bewertender Agent sieht aber nicht bewerten soll, zwangsläufig sein Ergebnis.

Das LLM kann nicht „nicht beachten". Es integriert alles. Die einzige Lösung ist strukturelle Trennung mit expliziter Anweisung.

### Das Lagebild-Prinzip

> Kontext erklärt. Kontext rechtfertigt. Kontext ist nicht das Bewertungsobjekt.

Jeder bewertende Agent braucht den Kontext — aber als klar markierten Hintergrund, nicht als Teil des zu bewertenden Inputs.

### Das Mittlungs-Problem

> Ein LLM, das einen kurzen emotionalen Input UND eine lange sachliche Antwort bewertet, mittelt über beides.

Die Lösung: Das Bewertungsobjekt zuletzt platzieren (Recency Bias nutzen) und explizit anweisen, nur diesen Teil zu bewerten.

### Das Drift-Problem

> Sekundäre Informationen im Charakter-Hash oder Adaptive-Hash können über den Corrector in die Antwort „einwandern", obwohl sie nichts mit dem aktuellen Prompt zu tun haben.

Die Lösung: Auch der Corrector braucht die Lagebild/Bewertungsobjekt-Trennung — nicht nur das Tribunal.

---

## 8. Betroffene Nodes und ihre Anpassung

| Node | Anpassung |
|------|-----------|
| **Tribunal** (alle 3 Agenten) | Lagebild/Bewertungsobjekt-Trennung. Perspektivspezifische Negativbeispiele. „Im Zweifel: ok". |
| **Salienz** | User-Eingabe als Bewertungsobjekt am Ende. Assistenten-Antwort als Lagebild oben. Explizite Schwellwerte für Emotionen. |
| **Corrector** | Lagebild/Bewertungsobjekt-Trennung. Explizite Anweisung: „Korrektur bezieht sich nur auf das Bewertungsobjekt." |
| **Router** | Nicht betroffen — sieht nur den reinen User-Prompt. |
| **Enricher** | Nicht betroffen — kein LLM-Aufruf, nur Datenzugriff. |
| **Responder** | Nicht betroffen — SOLL alles sehen. Generierung, nicht Bewertung. |

---

## 9. Generalisierbarkeit

Dieses Pattern betrifft **jedes** Multi-Agent-System mit geteiltem State, bei dem spezialisierte Agenten Bewertungen vornehmen. Es ist unabhängig vom LLM-Modell, der Sprache und dem Anwendungsfall. Die Trennung muss architektonisch erzwungen werden — sie entsteht nicht von selbst.

---

## 10. Offene Fragen

- **Granularität:** Wie viel Lagebild braucht ein Agent? Zu viel → Token-Verschwendung. Zu wenig → Agent versteht die Situation nicht.
- **Differenzierung:** Sollte das Lagebild pro Agent unterschiedlich sein? Der Jurist braucht andere Hintergründe als der Psychologe.
- **Erkennung:** Wie erkennt man neue Kontaminationsfälle systematisch? Aktuell durch manuelle Tests. Telemetrie (TEL1) könnte helfen — unerwartete Korrektur-Raten als Indikator.

---

*Diese Lesson dokumentiert eine fundamentale Architektur-Erkenntnis. Die Trennung von Lagebild und Bewertungsobjekt ist kein optionales Feature — sie ist eine strukturelle Notwendigkeit für jedes Multi-Agent-System mit geteiltem Gedächtnis.*
