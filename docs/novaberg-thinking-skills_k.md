# Novaberg — Skills (Konzept)

**Absicht:** Nova hält erlerntes Vorgehen für wiederkehrende Anliegen als kleine, selbst geschriebene und selbst gepflegte Markdown-Anweisungen fest — eine je Aufgabentyp, entstanden aus Korrekturen, als Vorschlag statt Befehl und nur für die Nutzung von Werkzeugen, nie für ihre Auswahl; ohne Skills läuft alles weiter.
**Stand:** 9. Mai 2026 (am 19.09.2026 ein Herkunftsvermerk in §9.3 und die Aufteilung in fünf Teile, beides ohne inhaltliche Änderung)
**Umsetzung:** Featureliste *Frames · Skills · Task-Orchestration · Cognitive Pipeline — im Bau als Lage-Konzept* 🟠 · *Skill-System (Epic 10)* ⚫ — der Zustand steht dort, nicht hier
**Teile:** [`novaberg-thinking-skills_t.md`](novaberg-thinking-skills_t.md) · [`novaberg-thinking-skills_b.md`](novaberg-thinking-skills_b.md) · [`novaberg-thinking-skills_e.md`](novaberg-thinking-skills_e.md) · Messungen: keiner
**Entschieden:** 2 · **Offen beim Meister:** 1 (Liste in [`novaberg-thinking-skills_e.md`](novaberg-thinking-skills_e.md))

**§ → Datei.** Die Abschnittsnummern sind die des ungeteilten Konzepts; ein Verweis der Form `novaberg-thinking-skills_k.md §6.1` findet seinen Abschnitt über diese Tabelle. `_k` ist diese Datei, `_t` ist [`novaberg-thinking-skills_t.md`](novaberg-thinking-skills_t.md), `_b` ist [`novaberg-thinking-skills_b.md`](novaberg-thinking-skills_b.md), `_e` ist [`novaberg-thinking-skills_e.md`](novaberg-thinking-skills_e.md). Einen Teil Messungen (`_m`) gibt es nicht: Das Konzept enthält keine Messung.

| § | Datei |
|---|---|
| Verhältnis zu Schwester-Dokumenten (unter dem Kopf) | `_k` |
| 1 | `_k` |
| 2 · 2.1 · 2.2 · 2.3 | `_k` |
| 3 · 3.1 · 3.2 · 3.3 · 3.4 | `_t` |
| 4 · 4.1 · 4.2 · 4.3 | `_t` |
| 5 · 5.1 · 5.2 · 5.3 · 5.4 | `_t` |
| 6 · 6.1 · 6.2 · 6.3 | `_k` |
| 7 · 7.1 · 7.2 · 7.3 | `_k` |
| 8 · 8.1 · 8.2 · 8.3 · 8.4 | `_t` |
| 9 · 9.1 · 9.2 · 9.3 | `_t` |
| 10 | `_e` (Abschnitt D) |
| 11 (Phase B · Phase C) | `_b` |
| 12 · 12.1 · 12.2 · 12.3 · 12.4 · 12.5 · 12.6 | `_e` (Abschnitt D) |
| 13 | `_k` |
| 14 (Verbindliche Dokumente, Verwandte Konzepte, Backlog-Bezüge, Quellen-Inspirationen) | `_k` |
| bisheriger Kopf (Projekt, Dokument, Stand, Pfad, Typ, Quellen) | `_e` (Abschnitt F) |
| bisherige Schlusszeile (*Stand 09.05.2026 …*) | `_e` (Abschnitt F) |
| Entschieden, Offen beim Meister, verworfene Varianten, Befunde der Doku-Sichtung vom 19.09.2026 | `_e` |

**Verhältnis zu Schwester-Dokumenten:** Dieses Dokument ist das dritte und letzte einer Trilogie. `novaberg-thinking-frames_k.md` etabliert das **Substrat** (Frames als universale kognitive Schablonen). `novaberg-thinking-cognitive-pipeline_k.md` beschreibt die **Mechanik** (Verstehens-Loop zwischen Router und Agent-Dispatch). Dieses Dokument detailliert die **Erfahrungs-Schicht** — Skills als selbst-editierbare Arbeitsanweisungen, die das Vorgehen für wiederkehrende Anliegen festhalten.

---

## 1. Vision

Beim ersten Mal denkt Nova nach, was zu einer Wetter-Anfrage gehört: welcher Ort, welche Quelle, welche Tiefe. Sie kommt zu einem brauchbaren Vorgehen, vielleicht mit kleinen Fehlern. Beim zweiten Mal denkt sie wieder nach. Beim dritten Mal hat der Nutzer sie schon zweimal korrigiert — *agrarwetter.org liefert für meine Region bessere Daten*, *bei Terminen prüf das Wetter auch dort*, *ich mag's kurz*. Diese Korrekturen sollen nicht verloren gehen.

Was sie braucht, ist ein Notizbuch. Ein Ort, an dem sie aufschreibt, **wie** sie Wetter-Anfragen sinnvoll bearbeitet — in eigenen Worten, formlos, jederzeit erweiterbar. Beim vierten Mal liest sie ihre eigene Notiz, bevor sie loslegt. Macht es richtig. Wird besser.

Genau das sind Skills. Sie sind Novabergs **Erfahrungs-Schicht** — die Stelle, an der zufällig durchgeschwommene Lösungen zu wiederholbarem Vorgehen werden. Plugins (NotizenAgent, web_search, TimelineAgent) sind ihre Werkzeuge. Frames sind ihre kognitiven Schablonen. Skills sind die Arbeitsanweisungen, die beides zusammenbringen, in der Sprache, die Nova selbst lesen und schreiben kann.

> **Leitmetapher:** Ein Butler, der jeden Auftrag zum ersten Mal abarbeiten muss, bleibt Hilfskraft. Ein Butler, der seine Erfahrungen aufschreibt — *"Sir trinkt Earl Grey nur am Vormittag, am Nachmittag Darjeeling, nie Beutel"* — wird zum vertrauten Begleiter. Skills sind Novabergs Notizbuch.

**Designziel:** Skills materialisieren erlerntes Vorgehen als Markdown-Dateien mit Themen-Tags. Sie werden im Cognitive Loop bei passenden Anliegen aktiviert und modulieren das Default-Vorgehen. Sie entstehen aus Negativ-Feedback (nicht aus Vor-Audit) und werden von Nova selbst editiert (nicht von Entwicklung).

---

## 2. Was Skills sind und was sie nicht sind

### 2.1 Saubere Drei-Schicht-Trennung

Aus Chat 81 als tragende Architektur-Aussage:

**Plugins/Agents** sind die **Werkzeuge** — Code, gepflegt von Entwicklung, definierte Fähigkeiten. NotizenAgent kann Listen anlegen und Items hinzufügen. TimelineAgent kann Termine speichern und finden. web_search kann Suchanfragen an SearXNG geben. Das sind die Hände.

**Frames** sind die **kognitiven Schablonen** — universale Slot-Strukturen für Objekte, Personen, Orte, Vorgänge, Werkzeuge. Sie strukturieren das Verstehen einer Aussage. Sie sagen, *was an Informationen vorhanden sein muss*, damit etwas sinnvoll bearbeitet werden kann. Das ist das kognitive Substrat.

**Skills** sind die **Arbeitsanweisungen** — editierbare Texte, die Vorgehen für eine Aufgaben-Klasse beschreiben. Sie nutzen Plugins als Werkzeuge und Frames als Slot-Quelle. Sie sind die Routinen, die zwischen Substrat und Hand vermitteln.

Diese Trennung ist nicht akademisch. Sie ist die Bedingung dafür, dass Skills überhaupt selbst editierbar sein können, ohne das System zu kompromittieren — siehe §6.

### 2.2 Was Skills nicht sind

**Skills sind keine Plugins.** Plugins definieren Fähigkeiten, sie haben Code-Schnittstellen, sie werden von Entwicklung gepflegt. Skills definieren Vorgehen mit Plugins, sie sind Text, sie werden von Nova selbst gepflegt.

**Skills sind keine Workflows in einem Workflow-Engine.** Ein Skill ist nicht *"Step 1 → Step 2 → if A then Step 3"* in einer Datenstruktur. Ein Skill ist Fließtext, das LLM interpretiert ihn beim Skill-Executor. Die strukturierte Sequenz entsteht zur Laufzeit, nicht im Skill-Format.

**Skills sind keine Code-Skills (Epic 10 Typ 2).** Im langfristigen Backlog steht Epic 10 mit Typ-2-Code-Skills via Claude API — Python-Skripten, die Nova selbst generiert und als Tools registriert. Das ist eine separate, riskantere Stufe. Die Skills in diesem Dokument sind ausschließlich **Typ-1-Prompt-Skills**: Markdown-Texte, die als zusätzlicher Prompt-Block ins LLM-Material einfließen. Keine Code-Generierung, keine Tool-Registrierung.

**Skills sind keine Frames.** Anweisung-Frames sind die Frame-Klasse, die Skills strukturell beschreibt (siehe Frames-Dokument §3.1). Ein Skill ist die Materialisierung dieses Frames als Textdatei. Frames sind Schablone, Skills sind Inhalt. Sie sind eng verwandt, aber nicht identisch.

### 2.3 Verwandtschaft zu Anthropic-SKILL.md

Eine Beobachtung aus der Diskussion: Anthropic selbst verwendet beim Training ihrer Modelle ein **Skills-Pattern** — Markdown-Dateien (`SKILL.md`) mit prozeduralen Anweisungen, die das Modell vor einer Aufgabe als Mentor-Briefing liest. Im Bestand finden sich solche Skills für PowerPoint-Erstellung, PDF-Verarbeitung, Frontend-Design und mehr.

Novabergs Skills folgen demselben Pattern. Der Unterschied: **Nova ist gleichzeitig Leser, Autor und Editor ihrer eigenen Skills.** Anthropics SKILL.md werden von Menschen geschrieben, Novas Skills entstehen aus ihrer eigenen Praxis. Das macht aus dem statischen Briefing eine selbst-lernende Erfahrungs-Schicht.

---

## 6. Disziplinen

Drei tragende Disziplinen, die ohne explizite Festlegung den Selbst-Edit gefährden würden.

### 6.1 1:1-Invariante — ein Aufgabentyp, ein Skill

Aus Meisters direkter Antwort in Chat 81: *"Skill zu einem Aufgabentyp. Wenn sie sieht, dass der Skill nicht passt, dann den Skill ändern. Sie kann theoretisch keine 2 Skills zu einem Thema haben."*

Diese Invariante ist nicht nur Aufräum-Disziplin, sondern strukturell bedeutsam. Folgen:

- **Lookup ist trivial.** Ein Aufgabentyp-Match liefert höchstens einen Skill. Kein Ranking, kein Voting, kein Konsens-Aggregator nötig.
- **Edits sind unzweideutig.** Pixie ändert *den* Skill, nicht *einen von mehreren*.
- **Skill-Müllhalde ist vermieden.** Skills wachsen in der **Tiefe** (durch Edit), nicht in der **Breite** (durch Duplikate).
- **Konflikt-Auflösung entfällt.** Wenn nur ein Skill existiert, kann er sich nicht selbst widersprechen.

Implementierung: Beim Skill-Erstellung prüft Pixie zuerst, ob ein Skill für den Aufgabentyp bereits existiert. Wenn ja → Edit-Pfad. Wenn nein → Neu-Erstellung.

**Was bedeutet "Aufgabentyp"?** Im Front-Matter der Skill-Datei steht `aufgabentyp: anliegen_wetter` als 1:1-Bezug zu einer Anliegen-Frame-Klasse aus dem Frame-Lager. Wenn das Frame-Lager weniger oder mehr Klassen unterscheidet, als für Skills sinnvoll wäre, kommt es zu Inkonsistenzen — diese Klassen-Granularität ist eine offene Designfrage (siehe §10).

### 6.2 Modulation, nicht Werkzeug-Auswahl

Aus Meisters Antwort in Chat 81: *"Sie kann den Begriff in der Suche ergänzen, der Treffer wäre dann weiter oben."*

Die Folgerung als Disziplin: **Skills geben dem LLM Hinweise zur Werkzeug-*Nutzung*, nicht zur Werkzeug-*Auswahl*.** Sie beeinflussen das *wie*, nicht das *womit*.

Konkrete Konsequenzen:

- Ein Skill schreibt **nicht**: *"Nutze URL https://agrarwetter.org direkt, web_fetch da hin."*
- Ein Skill schreibt **wohl**: *"Ergänze den Suchbegriff um 'agrarwetter', dann liegt der relevante Treffer weiter oben."*

Effekt: Das Werkzeug bleibt `web_search` mit SearXNG als Suchgateway. Der Skill ändert nur den Query-String. SearXNG behält die Whitelisting- und Sicherheits-Hoheit, kein Skill kann sie umgehen.

**Verallgemeinert:** Skills modulieren **innerhalb** der Werkzeug-Schicht. Sie wählen nicht zwischen Werkzeugen, sie wählen nicht zwischen Plugins, sie verändern keine Plugin-Schnittstellen. Sie sind Erfahrungs-Hinweise zur Anwendung dessen, was das System ohnehin kann.

Das schützt die Architektur: Plugins bleiben das alleinige Tor zu externen Wirkungen. Wenn ein Skill plötzlich Werkzeug-Auswahl-Anweisungen enthielte, wäre er ein Sicherheitsrisiko. Diese Disziplin ist **non-negotiable**.

### 6.3 Skills sind Vorschläge, nicht Befehle

Bereits unter §5.2 erwähnt, hier als Disziplin festgehalten. Der Skill-Executor-Prompt erlaubt explizit Abweichung. Das ist nicht Schwäche, sondern Schutz — gegen Skills, die im konkreten Fall nicht passen.

Außerdem ist es Lern-Mechanik: Wenn das LLM systematisch von einem Skill abweicht, ist das diagnostisches Material. Der Skill ist möglicherweise veraltet, schlecht formuliert oder in der falschen Klasse.

---

## 7. Verhältnis zu Frames und Cognitive Pipeline

### 7.1 Frame liefert, Skill verlangt

Aus Frames-Dokument §8 als zentrale Pipeline-Trennung: **Frames liefern die Slots — Skills verlangen sie.**

Konkret: Der Skill-Executor (Pipeline §4.8) bekommt das aufgelöste Frame-Paket als Eingabe und nutzt die Slot-Werte als Material für sein Vorgehen. Der Skill geht davon aus, dass die Slots da sind — er füllt sie nicht selbst.

Beispiel Wetter-Skill: Slots `ort`, `zeit`, `tiefe` kommen aus dem Anliegen-Frame. Der Skill-Text setzt voraus, dass `ort` aus dem Frame-Auflöser stammt (Wohnort als Default, falls leer). Er verlangt keine Slot-Erhebung selbst.

Wenn ein Slot fehlt, der für die Skill-Anwendung kritisch wäre, ist das ein Frame-Problem (kritische Lücke, Pipeline §4.6), kein Skill-Problem. Der Skill kann darauf verweisen (*"Ohne ort-Slot kann ich keine sinnvolle Suche absetzen — Rückfrage stellen"*), aber die Auflösung selbst gehört in den Frame-Auflöser.

### 7.2 Skill nutzt Frame-Lager-Reife

Wenn ein Frame-Lager-Eintrag etablierte Defaults hat (Frames §7.3, Pipeline §4.11), kann der Skill darauf bauen. *"Nimm den Wohnort aus den Fakten"* funktioniert nur, wenn der Wohnort als Fakt etabliert ist. Bei Cold-Start ohne Wohnort-Fakt fällt der Skill auf eine Rückfrage zurück.

Diese Verbindung muss im Skill-Text **nicht** explizit gemacht werden — sie passiert automatisch, weil Skills auf aufgelösten Frames arbeiten und der Auflöser das Lager bereits konsultiert hat.

### 7.3 Phase A funktioniert ohne Skills

Wichtige Konsequenz aus Pipeline-Dokument §7: Der Cognitive Loop muss zwingend ohne Skills funktionieren. **Das macht Skills zur Verfeinerungs-Schicht, nicht zur Grundlage.**

Effekt: Skills sind nicht-essentiell. Wenn der Skill-Speicher leer ist, läuft alles weiter — nur eben weniger personalisiert. Das gibt Sicherheit gegen Skill-Speicher-Korruption, gegen versehentliches Löschen, gegen Migrations-Probleme. Skills sind eine **additive** Schicht.

---

## 13. Designprinzipien

**Skills sind Erfahrungs-Schicht, nicht Grundlage.** Phase A funktioniert ohne Skills. Skills sind Verfeinerung.

**Ein Aufgabentyp, ein Skill.** 1:1-Invariante. Skills wachsen in Tiefe, nicht in Breite.

**Skills modulieren, sie umgehen nicht.** Werkzeug-Auswahl bleibt im System, Skills beeinflussen nur die Werkzeug-Nutzung.

**Skills sind Vorschläge, nicht Befehle.** LLM darf abweichen. Abweichung ist Lern-Signal.

**Skill-Erstellung ist fehler-getrieben.** Negativ-Feedback ist die Quelle, nicht Vor-Audit oder jeder Erfolg.

**Skills sind selbst-editierbar.** Nova liest, schreibt, ändert ihre eigenen Skills. Mensch greift nur ein, wenn es schiefgeht.

**Skills sind Text, nicht Code.** Markdown mit Front-Matter. Kein YAML-Workflow, keine Decision-Trees, keine Step-Listen.

**Skills sind klein.** Halbe bis ganze Bildschirmseite. Lange Skills werden vom LLM nicht zuverlässig gelesen.

**User-Feedback ist die Korrektur-Quelle.** Schlechte Skills werden in der Praxis sichtbar und führen zu Negativ-Feedback, das den nächsten Edit-Trigger auslöst. Selbst-korrigierende Schleife.

---

## 14. Verweise

### Verbindliche Dokumente

- `novaberg-thinking-frames_k.md` — Frames als kognitives Substrat, Anweisung-Frame als Skill-Vorgänger
- `novaberg-thinking-cognitive-pipeline_k.md` — Skill-Lookup, Skill-Executor, Phasen-Plan B und C
- `novaberg-architecture.md` — Gesamtarchitektur
- `novaberg-pixie.md` — Pixie-Reflexionsläufe, Heartbeat-Mechanik

### Verwandte Konzepte

- `novaberg-metakognition_k.md` — Aktionen-Queue, Vorsätze als Skill-Verwandtschaft
- `novaberg-thinking-curiosity_k.md` — Neugier-Triggers, mit denen Skill-Pflege verwandt ist
- `novaberg-pattern-domain-language.md` — Vokabular für Themen-Tag-Definition

### Backlog-Bezüge

- Epic 10 (Skill-System) im Backlog — dieses Konzept materialisiert Typ-1 (Prompt-Skills). Typ 2 (Code-Skills via Claude API) bleibt im Backlog, separate spätere Stufe.

### Quellen-Inspirationen

- Anthropic SKILL.md-Pattern (Mentor-Briefing als Markdown), siehe `/mnt/skills/public/*/SKILL.md` als Beispiele bei Claude-Sessions.
- Programming-Practice: README-driven development, wo das README das Vorgehen formuliert, das dann implementiert wird. Skills sind die Laufzeit-Variante davon.
