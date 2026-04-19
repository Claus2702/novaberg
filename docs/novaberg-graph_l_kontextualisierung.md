# 11_L_b — Lesson: Strukturierte Kontextualisierung

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Lesson — Prompts beschreiben, nicht verbieten
**Stand:** 12. April 2026, Chat 44 (migriert, Inhalt unverändert)
**Pfad:** novaberg/docs/novaberg-graph_l_kontextualisierung.md
**Ursprung:** nova-11-l-b.md
**Typ:** Lesson (L)
**Entdeckt:** Chat 27 (RESP-TIMELINE1 Analyse)
**Betrifft:** Alle Nodes mit zusammengesetzten Prompts (Responder, Perzeption, Router, Salienz)

---

## 1. Ausgangslage

Chat 23 etablierte das Prinzip **„Weniger Input > stärkerer Prompt"**: Halluzination löst man durch Kontext-Reduktion, nicht durch stärkere Anweisungen. Das war richtig und löste AGT3 — der Responder halluzinierte aus dem memory_context (Notizen-Übersicht), also wurde er entfernt.

Aber das Prinzip wurde zu weit angewandt. Bei Agent-Erfolg wurde dem Responder *alles* genommen: Session-Turns, Gedächtnis-Kontext, Web-Kontext. Als Ersatz kamen vier Imperative:

```
Erfinde KEINE Probleme.
Erfinde KEINE Duplikat-Warnungen.
Erfinde KEINE Konsolidierungs-Vorschläge.
Wenn das Ergebnis sagt 'erstellt', dann wurde es erstellt.
```

Das Ergebnis: Nova wurde zur Meldestelle. Keine Persönlichkeit, keine emotionale Reaktion, und trotzdem Halluzination — weil der Responder die *Transition* nicht verstand. „Zahnarzt — nicht mehr aktiv" wurde als „nicht gefunden" interpretiert, weil der Kontext fehlte, dass der User gerade den Termin abgesagt hat.

---

## 2. Erkenntnis

> **Der Prompt darf Informationen haben. Er muss nur mitteilen, um was für Informationen es sich handelt.**

Das LLM halluziniert nicht, weil es zu viel sieht. Es halluziniert, weil es nicht versteht, was es sieht. Wenn ein Prompt Session-Turns, ein Agent-Ergebnis und eine Anweisung enthält, aber nicht beschrieben ist, was was ist — dann mischt das LLM alles zusammen.

Die Lösung sind nicht Verbote, sondern **Kontext-Beschreibungen**: Jeder Informationsblock wird explizit eingeleitet mit einer Beschreibung seiner Rolle.

---

## 3. Prinzip: Beschreiben statt Verbieten

### Vorher — Imperative

```
═══ AKTIONS-ERGEBNIS ═══
Die folgende Aktion war ERFOLGREICH.
Beschreibe dem Nutzer NUR was passiert ist.
Erfinde KEINE Probleme.
═══════════════════════
```

Vier Verbote, kein Kontext. Das LLM weiß, was es *nicht* tun soll, aber nicht, was die Information *bedeutet*.

### Nachher — Strukturierte Kontextualisierung

```
═══ VERARBEITUNG ═══
Der Benutzer hat eine Anweisung gegeben. Die zuständige Fachabteilung hat
folgende Operation ausgeführt:

{ergebnis_text}

Gib dem Benutzer eine Rückmeldung zu seiner Anweisung und dem Ergebnis
der Fachabteilung. Dein Stil, deine Persönlichkeit und deine emotionale
Reaktion bestimmst du selbst.
═══════════════════════
```

Kein Verbot. Stattdessen: Was ist das? (Operation der Fachabteilung.) Was soll ich damit tun? (Rückmeldung geben.) Wie? (Bestimmst du selbst.)

---

## 4. Muster: Abgegrenzte Informationsblöcke

Das Muster hat sich über mehrere Chats entwickelt:

| Chat | Node | Block | Beschreibung |
|------|------|-------|-------------|
| 23 | Perzeption/Router | `═══ GESPRÄCHSVERLAUF ═══` | „Analysiere NUR den aktuellen Prompt. Der Verlauf hilft bei Pronomen-Auflösung." |
| 24 | Responder | `═══ HINTERGRUND: GEDÄCHTNIS ═══` | „Nutze sie NUR wenn der aktuelle Prompt darauf Bezug nimmt." |
| 24 | Responder | `═══ HINTERGRUND: WEB-RECHERCHE ═══` | Analog zum Gedächtnis-Block. |
| 25 | Responder | `═══ AKTUELLER PROMPT ═══` | Trennt Session-Turns vom aktuellen User-Input. |
| 26 | Classify-Node | Session-Block | „NUR FUER RUECKBEZUEGE" im Header. |
| **27** | **Responder** | **`═══ VERARBEITUNG ═══`** | **„Die Fachabteilung hat folgende Operation ausgeführt."** |

Das durchgängige Muster: `═══ BLOCKNAME ═══` + Beschreibung der Rolle + Inhalt + `═══════════════════════`.

---

## 5. Warum Imperative versagen

Imperative versuchen, das LLM von *außen* zu kontrollieren: „Tu X nicht." Das funktioniert bei klaren, isolierten Fällen. Es versagt, wenn das LLM den *Kontext* falsch einordnet — denn dann kommt es gar nicht erst in die Situation, das Verbot anzuwenden.

Beispiel: „Erfinde KEINE Probleme" setzt voraus, dass das LLM *weiß*, dass es ein Problem erfindet. Aber wenn „nicht mehr aktiv" als Zustandsbeschreibung statt als Handlungsergebnis interpretiert wird, erfindet das LLM aus seiner Sicht kein Problem — es *beschreibt* eines.

**Kontext-Beschreibung** löst das an der Wurzel: Das LLM ordnet die Information *vor* der Generierung richtig ein. Es muss nicht kontrolliert werden, weil es die Situation versteht.

---

## 6. Evolution des Prompt-Designs

```
Chat 1–22:  Flacher Prompt → alles in einem Block → Halluzination
Chat 23:    Weniger Input → Kontext-Reduktion → Halluzination weg, aber Persönlichkeit weg
Chat 24:    Abgegrenzte Blöcke → Bereiche markiert → Kontamination reduziert
Chat 27:    Strukturierte Kontextualisierung → Blöcke beschrieben → LLM versteht Kontext
```

Jede Stufe war nötig, um die nächste zu verstehen. Ohne den AGT3-Kontext-Schnitt (Chat 23) hätten wir nicht erkannt, dass das Problem nicht die *Menge* der Information ist, sondern ihre *Einordnung*.

---

## 7. Anwendung auf andere Nodes

Das Prinzip gilt überall, wo ein Prompt mehrere Informationsquellen zusammenführt:

- **Salienz:** Fakten-Extraktion + Session-Kontext + User-Prompt. Aktuell: Regeln im Fließtext. Besser: Abgegrenzte Blöcke mit Rollenbeschreibung.
- **Thinker:** Web-Ergebnisse + Memory + User-Prompt. Aktuell: Alles in einem System-Prompt. Besser: „Das sind Suchergebnisse. Das ist Novas Wissen. Das hat der User gefragt."
- **Tribunal:** Antwort-Entwurf + Regeln + Kontext. Aktuell: Perspektiven-Prompts. Potenziell: Klarere Trennung zwischen Bewertungskriterien und zu bewertendem Material.

---

→ Kontext-Abgrenzung im Responder: `01_M_e`, Abschnitt 3.4
→ Kontext-Schnitt bei Agent-Erfolg (Vorgänger): `01_M_e`, Abschnitt 3.5
→ Lesson AGT3 (Halluzination durch Kontext): Chat 23 Protokoll
→ Lesson „Weniger Input > stärkerer Prompt": Chat 23, Abschnitt 6
