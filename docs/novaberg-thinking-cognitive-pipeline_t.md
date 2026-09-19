# Novaberg — Cognitive Pipeline (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-thinking-cognitive-pipeline_k.md`](novaberg-thinking-cognitive-pipeline_k.md) · Bauplan und Umstellung: [`novaberg-thinking-cognitive-pipeline_b.md`](novaberg-thinking-cognitive-pipeline_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-cognitive-pipeline_e.md`](novaberg-thinking-cognitive-pipeline_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

---

## 4. Loop-Schritte im Detail

Zehn Schritte, die der CognitiveGraph in einer Aktivierung durchläuft. Nicht jeder Schritt braucht einen LLM-Call — viele sind deterministische Operationen oder Datenbank-Lookups.

### 4.1 Akutheits-Klassifikation

**Eingabe:** User-Prompt, letzte N Vor-Turns, EI-Output (Modus, Intentionen).

**Operation:** LLM-Call mit Akutheits-Test. Ist das Anliegen akut (siehe Frames-Dokument §4)? Welche Frame-Klassen sind aktiv?

**Ausgabe:** Liste der akuten Frame-Klassen mit Akutheits-Stufe (`latent`, `halb_akut`, `akut`).

**Beispiel:** *"Lege sie bitte an"* nach Vor-Turn-Liste mit Schrauben und Dübeln → akute Klassen: `anliegen_notiz_create`, `objekt_liste`, `ort_baumarkt`. Akutheits-Stufe: `akut` (Imperativ, Bezugspronomen, klares Vorhaben).

**Skip-Bedingung:** Wenn keine Klasse über `latent` hinauskommt, wird der Cognitive Loop nicht aktiviert. Der Turn fließt zu GV-Node ohne Frame-Verarbeitung.

### 4.2 Frame-Aktivierung und Slot-Erhebung

**Eingabe:** Akute Frame-Klassen aus Schritt 1.

**Operation:** Pro akuter Frame-Klasse einen Slot-Erhebungs-LLM-Call. Welche Slots sind aus dem aktuellen Prompt direkt füllbar? Welche aus Vor-Turns? Welche fehlen?

**Ausgabe:** Pro Frame eine Slot-Liste mit Werten und Quellen-Markierung (`prompt`, `vor_turn`, `unbekannt`).

**Beispiel (Anliegen-Frame):**
```
anliegen_notiz_create
  was       = ["Schrauben", "Dübel"]    [vor_turn]
  container = liste                     [vor_turn]
  ort       = unbekannt
  name      = unbekannt
```

**Beispiel (Ort-Frame):**
```
ort_baumarkt
  ort_name  = "Baumarkt"                [prompt]
  stadt     = unbekannt
  spezifisch = unbekannt
```

**Optimierung:** Mehrere Frame-Klassen können in einem Sammel-LLM-Call erhoben werden, wenn sie thematisch verwandt sind. Performance-Frage, in der Implementierung zu klären (siehe Frames-Dokument §12.1).

### 4.3 Frame-Auflöser

**Eingabe:** Frames mit Slot-Lücken aus Schritt 2.

**Operation:** Lücken werden über Wissens-Quellen aufgelöst:

1. **Knowledge Graph:** Gibt es Fakten über die Entität? *"Baumarkt"* in Fakten gefunden → *"Baumarkt Donauwörth"*.
2. **Notizen/Timeline:** Gibt es referenzierte Einträge? *"Liste"* in Notizen gefunden → *"Baumarkt-Liste"*.
3. **Frame-Lager:** Gibt es Konsens-Werte aus früheren Frames? *Zahnarzt*-Frames hatten *wo=Treuchtlingen* in 90% der Fälle.
4. **EI-Output:** Modus und Intentionen geben Hinweise (Diktat-Modus → Notiz; Frage-Modus → Recherche).

Pro aufgelöstem Slot wird die Quelle vermerkt. Slots, die auch nach allen Quellen leer bleiben, werden als `Lücke` markiert mit Kritikalitäts-Bewertung.

**Ausgabe:** Frames mit erweiterten Slot-Belegungen und Quellen-Annotation; Lücken-Liste mit Kritikalität.

**Beispiel-Auflösung Baumarkt-Liste:**
```
anliegen_notiz_create
  was       = ["Schrauben", "Dübel"]    [vor_turn]
  container = liste                     [vor_turn]
  ort       = "Donauwörth"              [knowledge_graph: Fakt #42]
  name      = "Baumarkt-Liste"          [vor_turn: Aufgreifen aus Smalltalk]
```

### 4.4 Cross-Frame-Validierung

**Eingabe:** Aufgelöste Frames aus Schritt 3.

**Operation:** Konsistenz-Prüfung über Frame-Grenzen (Frames-Dokument §5.3). Beispiele:

- Sprecher-Standort vs. Termin-Ort.
- Termin-Zeit vs. Reise-Zeitraum.
- Anliegen-Ort vs. Werkzeug-Reichweite.

Wird über LLM-Call mit allen aufgelösten Frames als Eingabe ausgeführt. Ergibt eine Konflikt-Liste mit Schwere-Klassifikation (`hart_blockierend`, `frage_wert`, `plausibel`).

**Ausgabe:** Konflikt-Liste; im Erfolgsfall leer.

### 4.5 Plausibilitätsprüfung

**Eingabe:** Aufgelöste Frames mit Slot-Werten.

**Operation:** LLM-Call gegen Weltwissen (Frames-Dokument §6). Sind die Slot-Werte plausibel? Gibt es Anomalien?

**Ausgabe:** Plausibilitäts-Annotationen pro Slot (vier Stufen: `plausibel`, `frage_wert`, `konflikt`, `unmoeglich`).

**Anmerkung:** Cross-Frame-Validierung (4.4) und Plausibilitätsprüfung (4.5) können in einem gemeinsamen LLM-Call zusammengelegt werden — beide prüfen die Frames gegen Welt-Constraints. Trennung im Konzept dient der Klarheit, in der Implementierung möglicherweise ein Schritt.

### 4.6 Behandlung von Konflikten und Lücken

**Eingabe:** Konflikt-Liste (4.4), Plausibilitäts-Annotationen (4.5), Lücken-Liste (4.3).

**Operation:** Entscheidung pro Befund:

- *Hart blockierend* → Loop bricht ab, Antwort wird zur Klärungs-Rückfrage geformt.
- *Frage wert* → Loop läuft weiter, aber Antwort enthält Hinweis-Element.
- *Kritische Lücke* → Loop bricht ab, Rückfrage zur Lücken-Schließung.
- *Unkritische Lücke* → Loop läuft weiter mit Default oder leerem Slot.
- *Plausibel ohne Konflikt* → Loop läuft weiter ohne Hinweis.

Die Schwellwerte sind eine Designfrage (siehe §13). Pragmatisch: Beim ersten Bauen vorsichtig (eher Rückfrage als Default), nach Beobachtung kalibrieren.

**Ausgabe:** Entscheidung *Loop fortsetzen* oder *Klärungs-Rückfrage formen*; bei Fortsetzung: angereicherte Frames + Hinweise für den Responder.

### 4.7 Skill-Lookup

**Eingabe:** Aufgelöste Frames, insbesondere Anliegen-Frame.

**Operation:** Im Skill-Speicher (siehe Skills-Dokument) nach passendem Skill suchen. Lookup über Themen-Tags und Embedding-Ähnlichkeit. Skills sind 1:1 zu Aufgabentypen (Skills-Dokument §X), also höchstens ein Treffer pro Anliegen.

**Ausgabe:** Skill-Datei (Markdown-Text mit Anweisung) oder `kein_skill_gefunden`.

**Phase A (skill-loser Modus):** Schritt 4.7 wird übersprungen oder gibt immer `kein_skill_gefunden` zurück. Der Loop läuft auf Default-Mechanik weiter.

### 4.8 Skill-Executor oder Default-Vorgehen

**Eingabe:** Aufgelöstes Frame-Paket; Skill (falls vorhanden).

**Operation, Skill vorhanden:** LLM-Call mit dem Skill-Text als Anweisungs-Block, dem aufgelösten Frame-Paket als Daten und einer Werkzeug-Liste. Das LLM entscheidet anhand des Skills, welche Werkzeuge in welcher Reihenfolge zu rufen sind, mit welchen Parametern.

**Operation, Default-Vorgehen (Phase A):** LLM-Call ohne Skill-Anweisung, nur mit Frame-Paket und Werkzeug-Liste. Das LLM entscheidet aus seinem allgemeinen Wissen — was eine kompetente, aber untrainierte Hilfskraft täte. Wird typischerweise einfache 1-Step-Lösungen produzieren, möglicherweise mit Fehlern bei Sonder­fällen.

**Ausgabe:** Werkzeug-Aufruf-Plan (eine oder mehrere Aufrufe in Sequenz), gegebenenfalls mit konditionalen Verzweigungen.

### 4.9 Werkzeug-Aufruf

**Eingabe:** Werkzeug-Aufruf-Plan.

**Operation:** Aufruf der Plugins/Agents (NotizenAgent, TimelineAgent, FaktenAgent, web_search, …) entsprechend des Plans. Bei Multi-Step-Plänen wird der Output von Schritt N als Input für Schritt N+1 verwendet (Slot-Verkettung, siehe §6).

**Ausgabe:** Werkzeug-Ergebnisse, bei Multi-Step die Sequenz aller Zwischen-Ergebnisse.

### 4.10 Ergebnis-Validierung und Reflexionsmarker

**Eingabe:** Werkzeug-Ergebnisse aus 4.9.

**Operation:** Hat das Werkzeug das Anliegen vollständig erfüllt? Beispiele:

- NotizenAgent gibt `status=fehler` zurück → Anliegen nicht erfüllt.
- web_search liefert keine Treffer → Recherche fehlgeschlagen.
- TimelineAgent legt Termin an, aber die Cross-Frame-Konflikte aus 4.4 wurden nicht aufgelöst → Anliegen ist erfüllt, aber wahrscheinlich nicht so, wie gemeint.

**Ausgabe:** Ergebnis-Block für Responder, mit Markierungen `erfolg`, `teilweise`, `fehler`. Plus ein optionaler Reflexionsmarker, der vom Pixie aufgegriffen wird (siehe §7).

### 4.11 Schema-Reifung und Cache-Hierarchie

Die zehn Loop-Schritte oben sind so beschrieben, als müsste jeder Schritt bei jeder Frame-Aktivierung neu durchlaufen werden. Das wäre teuer und kognitiv falsch — ein Mensch denkt beim zehnten Zahnarzttermin nicht mehr darüber nach, was alles dazugehört. Er weiß es. Genau diese Reifung baut das Frame-Lager über Häufigkeits-Aggregation, Recency- und Korrektur-Gewichtung ab (siehe Frames-Dokument §7.3, §9.2). Die Pipeline nutzt sie über eine **Cache-Hierarchie**, die den LLM-Aufwand stufenweise reduziert.

**Drei Reife-Stufen pro Frame-Klasse:**

**Cold Start** (erste oder zweite Beobachtung). Volle LLM-Kette: Akutheits-Klassifikation, Klassen-Findung, Slot-Inventar (was gehört zu dieser Klasse), Slot-Erhebung (was steht im Prompt), Auflösung der Lücken. Das Lager bekommt einen Erst-Eintrag mit Schema-Skizze. Teuerster Lauf, aber notwendig, um überhaupt Erfahrung aufzubauen.

**Warm** (3 bis ~10 Beobachtungen). Klassen-Findung trifft Lager-Treffer. Slot-Inventar wird per `frame_schema_holen()` aus dem Lager geholt — kein eigener LLM-Call mehr für die Frage *"welche Slots gehören zu dieser Klasse?"*. Nur die Slot-Erhebung *"was steht im aktuellen Prompt?"* läuft am LLM. Defaults werden vorsichtig gehandhabt: Häufigkeit ist noch nicht hoch genug, um sie automatisch in Lücken einzusetzen — eher als Kandidaten-Vorschlag, der vom Auflöser noch geprüft wird.

**Hot** (10+ Beobachtungen, stabile Defaults, wenig Korrekturen). Slot-Inventar fix, Defaults zuverlässig. Auflöser greift Defaults direkt für unbelegte Slots, ohne dass das LLM noch eine Lücken-Strategie entwickeln muss. LLM-Beteiligung minimal — vor allem dort, wo der konkrete Prompt vom Schema abweicht oder neue Slots auftauchen.

**Wirkung über die Loop-Schritte:**

| Schritt | Cold | Warm | Hot |
|---|---|---|---|
| 4.1 Akutheit | LLM | LLM | LLM (kann nicht gecacht werden) |
| 4.2 Frame-Aktivierung | LLM (volles Inventar) | LLM (kompakter, Inventar aus Lager) | LLM (nur Werte-Erhebung) |
| 4.3 Frame-Auflöser | LLM für Lücken-Strategie | LLM mit Lager-Vorschlägen | Lager-Defaults direkt, LLM nur Kontroll-Lauf |
| 4.4–4.5 Validierung | LLM | LLM | LLM (kann nicht gecacht werden) |
| 4.7 Skill-Lookup | DB-Query | DB-Query | DB-Query |

Akutheits-Klassifikation und Validierung bleiben LLM-Operationen — sie hängen am konkreten Prompt-Inhalt, da gibt es nichts zu cachen. Der Hauptgewinn liegt in den Schritten 4.2 und 4.3, die sich von zwei LLM-Calls (Inventar + Erhebung) auf einen reduzierten LLM-Call plus Lager-Lookup vereinfachen, sobald eine Klasse warm ist.

**Schema-Aktualisierung als Nebenwirkung jeder Aktivierung:**

Nach erfolgreichem Loop-Durchlauf wird der Frame-Eintrag im Lager registriert (`frame_registrieren`). Der aggregierte Schema-Zustand pro Klasse wird dabei automatisch aktualisiert — nicht synchron im Hot Path, sondern asynchron über einen Pixie-Task oder einen Datenbank-Trigger. Damit zahlt jede Aktivierung in das Schema ein, ohne den Loop zu verlangsamen.

**Korrekturen führen zu Schema-Updates:**

Wenn der Nutzer einen Default-Vorschlag korrigiert (Negativ-Feedback §5.1, *"Nicht in Donauwörth, in Treuchtlingen"*), ruft der Reflexionspfad `frame_korrektur_registrieren()` auf. Der korrekte Wert bekommt erhöhtes Gewicht, der falsche reduziertes. Bei stark korrigierten Defaults kann das Schema bei der nächsten Aktivierung bereits den neuen Wert vorschlagen — auch wenn die rohe Häufigkeit noch dagegen spräche. Das macht das Lager schnell-lernend gegen Fehler.

**Was nicht gecacht wird:**

- Die spezifischen Slot-Werte des aktuellen Turns (immer aus dem Prompt zu erheben).
- Cross-Frame-Konflikte (immer prompt-spezifisch).
- Plausibilitätsprüfung (immer prompt-spezifisch).
- Skill-Anwendung (Skill-Text wird als Prompt-Block geliefert, nicht das Ergebnis).

**Cold-Start-Risiko:**

Bei einem ganz neuen Nutzer ist alles cold. Der Loop ist zu Beginn am teuersten und fühlt sich am langsamsten an. Erst nach einigen Wochen Nutzung reift das Lager so weit, dass die häufigen Anliegen warm oder hot werden. Pragmatische Konsequenz: keine Optimierungs-Premiumstrategie für Cold Start — der teure Erst-Lauf ist die Investition, die sich amortisiert.

---

## 5. Negativ-Feedback-Erkennung

Skill-Lernen lebt vom Negativ-Feedback. Wenn das System ohne Skills (Phase A) Fehler macht und der Nutzer reagiert, muss diese Reaktion erkennbar sein, um sie als Lern-Signal zu nutzen. Vier Quellen liefern Negativ-Feedback:

### 5.1 Expliziter Widerspruch des Nutzers im Folge-Turn

Klarste Quelle. *"Nicht in Donauwörth, in Treuchtlingen"*, *"das war falsch"*, *"das hattest du anders gemacht"*. Der Router würde solche Turns heute als neuen Auftrag behandeln. In der neuen Pipeline wird vor der Akutheits-Klassifikation ein **Korrektur-Detektor** geschaltet — ein LLM-Call mit dem aktuellen Turn und dem Vor-Turn (Novas Antwort), der prüft, ob der Nutzer eine Korrektur ausspricht.

Wenn ja: Der vorige Turn wird als *"falsch ausgeführt"* markiert, der aktuelle Turn wird als *"korrigierende Anweisung"* in den Cognitive Loop gegeben. Beim Loop-Ende wird der Reflexionsmarker mit *"Korrektur erfolgt, Vor-Turn war Fehler-Quelle"* gesetzt — Pixie nimmt das auf und löst Skill-Erstellung oder Skill-Edit aus.

### 5.2 EI-gemeldeter Frust-Anstieg nach Antwort

Subtilere Quelle. Der Nutzer korrigiert nicht explizit, aber die emotionale Pipeline meldet im Folge-Turn einen Frust-Anstieg. Beispiel: Nova legt die Notiz im falschen Container an, der Nutzer schreibt *"naja…"* mit erkennbarer Resignation.

EI-Calc liefert solche Signale heute schon (Modus, Arousal, Beziehungsdynamik). Eine Schwellwert-Heuristik *"Arousal-Anstieg um X bei negativer Valenz"* könnte als Trigger dienen, ohne neuen LLM-Call.

### 5.3 Validierungs-Konflikt während des Loops

Wenn die Cross-Frame-Validierung (4.4) oder Plausibilitätsprüfung (4.5) einen Konflikt erkennen, der sich während des Loops nicht auflösen lässt, ist das ein internes Negativ-Feedback. Der Loop hat etwas geliefert, aber nicht ohne Bauchgefühl. Reflexionsmarker setzen — Pixie kann sich später überlegen, ob ein Skill helfen würde.

### 5.4 Pixie-Reflexion entdeckt Fehler-Cluster

Späteste Quelle, dafür mit großer Reichweite. Pixie scannt periodisch die Reflexionsmarker und Negativ-Feedback-Spuren. Wenn ein Muster sichtbar wird (*"in den letzten zehn Wetter-Anfragen war fünf Mal eine Ortskorrektur nötig"*), wird das zum Skill-Edit-Trigger — auch ohne explizite Einzel-Markierung.

### 5.5 Klassifikation der Feedback-Stärke

Nicht jedes Feedback ist gleich gewichtig. Vorläufige Hierarchie:

| Stärke | Quelle | Wirkung |
|---|---|---|
| Hoch | Expliziter Widerspruch (5.1) | Skill-Erstellung oder -Edit unmittelbar |
| Mittel | EI-Frust + Korrektur in Folge-Turn | Skill-Edit-Kandidat |
| Mittel | Internes Validierungs-Konflikt (5.3) | Skill-Kandidat-Notiz für Pixie |
| Niedrig | EI-Frust ohne Korrektur (5.2) | Marker für Pixie-Aggregation |
| Aggregat | Pixie-Cluster (5.4) | Skill-Edit oder -Erstellung |

Diese Klassifikation ist eine **Designfrage**, die in der Implementierung nachjustiert wird. Skills sollen nicht durch jede emotionale Schwankung umgeschrieben werden.

---

## 6. Frame-Komposition — Multi-Step-Workflows

Schritt 4.8 (Skill-Executor oder Default-Vorgehen) kann mehrstufige Werkzeug-Pläne erzeugen. Damit ist die Architektur tragend für genuin agentic Workflows.

### 6.1 Slot-Verkettung über Steps

Im Wetter-mit-Termin-Beispiel:

```
Step 1: web_search(wetter, ort=user_location)
        → ergebnis_lokal = "21°C, sonnig"

Step 2: timeline_check(tag=heute)
        → termine_heute = [{ort: "Hamburg", zeit: "14:00"}]

Step 3 (konditional, wenn termine_heute hat einen Ort ≠ user_location):
        web_search(wetter, ort=termin_ort)
        → ergebnis_termin = "14°C, Regen"

Step 4: synthese aus ergebnis_lokal und (falls vorhanden) ergebnis_termin
```

Der Output von Step 2 wird zum Slot-Input für Step 3 — Slot-Verkettung. Genau dieselbe Operation wie der Frame-Auflöser innerhalb eines Frames (Slot-Lücke aus Vor-Wissen füllen), nur mit "vorheriger Step-Output" als zusätzlicher Quelle.

### 6.2 Konditionale Verzweigung

Step 3 oben ist konditional. *Wenn* die Termin-Liste einen anderen Ort enthält, *dann* lauf Step 3, sonst überspring. Diese Verzweigungs-Logik kommt aus dem Skill (oder im skill-losen Phase-A-Modus aus dem allgemeinen LLM-Verständnis der Aufgabe).

In der Implementierung: Skill-Text enthält Anweisungen wie *"Wenn an dem Tag ein Termin in einem anderen Ort vorliegt, prüfe dort auch das Wetter"*. Der Skill-Executor übersetzt das in den Werkzeug-Aufruf-Plan.

### 6.3 Mehrere Frames im Loop

Ein einzelner Turn kann mehrere Anliegen-Frames enthalten. *"Lege die Liste an und plan einen Termin für nächste Woche"* — zwei Anliegen, beide akut. Der Cognitive Loop handhabt das durch parallele oder sequentielle Frame-Bearbeitung:

- *Parallel*: beide Anliegen unabhängig, beide Skills parallel, beide Werkzeug-Aufrufe parallel.
- *Sequentiell*: ein Anliegen hängt vom Ergebnis des anderen ab, dann muss der Loop sequenziell laufen.

Die Entscheidung trifft das LLM bei der Frame-Erhebung (Schritt 4.2). Wenn die Anliegen-Frames Slot-Verbindungen zeigen, läuft sequenziell; sonst parallel.

---

> **§7 steht nicht in dieser Datei.** Phase A, der Loop ohne Skills, trägt eine Setzung zur Absicht und steht in [`novaberg-thinking-cognitive-pipeline_k.md`](novaberg-thinking-cognitive-pipeline_k.md).

## 8. Phase B: Loop mit Skills

Wenn Skills existieren, modifizieren sie den Loop, aber sie ersetzen keinen Schritt. Die Mechanik:

### 8.1 Skills modulieren, sie umgehen nicht

Aus Chat 81 als tragende Architektur-Aussage: Skills geben dem LLM Hinweise zur **Werkzeug-Nutzung**, nicht zur **Werkzeug-Auswahl**. Sie beeinflussen das *wie*, nicht das *womit*. Ein Skill schreibt nicht *"nutze URL X"*, sondern *"erweitere die Suche um Begriff Y"*. Das Werkzeug bleibt `web_search`, der Skill modifiziert nur den Query-String.

Diese Disziplin verhindert, dass Skills die Werkzeug-Schicht aushebeln. Plugins/Agents bleiben das alleinige Tor zu externen Wirkungen, Skills sind die Erfahrungs-Schicht darüber.

### 8.2 Skill-Wirkung im Skill-Executor

Im Schritt 4.8 (Skill-Executor) wird der Skill-Text als zusätzlicher Prompt-Block ins LLM-Eingangs-Material gegeben:

```
[ANWEISUNG]
{skill_text}

[FRAMES]
{aufgeloeste_frames}

[WERKZEUGE]
{verfuegbare_werkzeuge}

Du sollst das Anliegen aus den Frames bearbeiten.
Nutze die Anweisung als Leitfaden, wenn sie auf die Situation passt.
Wenn die Anweisung in der konkreten Situation keinen Sinn ergibt, weich davon ab.
```

Der letzte Satz ist wichtig: Skills sind keine Befehle, sondern Vorschläge. Das LLM darf abweichen, wenn die Situation es erfordert. Bei systematischer Abweichung von einem Skill ist das selbst wieder ein Reflexionsmarker — möglicherweise stimmt der Skill nicht mehr mit der Realität überein.

### 8.3 Skill-Pflege als Reflexions-Konsequenz

Bei Negativ-Feedback wird im Pixie-Reflexionslauf geprüft, ob ein Skill betroffen ist:

- *Skill war beteiligt und das Vorgehen führte zu Negativ-Feedback*: Skill-Edit-Kandidat. Pixie liest den Skill, vergleicht mit dem konkreten Fehler, schreibt eine angepasste Version.
- *Skill war nicht beteiligt, aber der Fall wäre ein typisches Skill-Thema*: Skill-Erstellungs-Kandidat. Pixie schreibt einen ersten Skill-Entwurf.
- *Skill war beteiligt und das Vorgehen führte zu Erfolg*: Skill-Verstärkung (im Skill-Lager: Häufigkeit hoch, Anwendungs-Erfolg vermerkt).

Detail-Mechanik der Skill-Pflege liegt im Skills-Dokument.

---
