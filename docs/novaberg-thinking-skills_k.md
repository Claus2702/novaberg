# Novaberg — Skills (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Skills — Selbst-editierbare Arbeitsanweisungen für wiederkehrende Anliegen (Konzept)
**Stand:** 09. Mai 2026, Chat 81
**Pfad:** novaberg/docs/novaberg-thinking-skills_k.md
**Typ:** Konzept (`_k`)
**Quellen:** Chat 81 (Skill-Konzept entstanden aus dem Self-Learning-Strang nach dem Wetter-Korrektur-Beispiel; klare Positionierung gegen Plugins/Agents und gegen Frames; tragende Disziplinen aus Meisters direkten Antworten)

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

## 3. Skill-Format

### 3.1 Anatomie eines Skills

Ein Skill ist eine Markdown-Datei mit YAML-Front-Matter für strukturelle Metadaten und Fließtext im Hauptteil:

```markdown
---
themen: [wetter, klima, vorhersage, agrarwetter]
aufgabentyp: anliegen_wetter
erstellt: 2026-04-15
zuletzt_geaendert: 2026-05-08
gewicht: 1.0
status: aktiv
---

# Wetter-Anfragen

Wenn nach dem Wetter gefragt wird, beachte folgendes Vorgehen:

**Quelle:** Für Anfragen zum Wohnort des Nutzers (Wolferstadt) und
ländlicher Regionen liefert agrarwetter.org die brauchbarsten Daten —
ergänze daher den Suchbegriff um "agrarwetter" oder den Ort.
Bei Großstädten oder fernen Orten reicht eine allgemeine Wettersuche.

**Ort:** Wenn kein Ort genannt wird, nimm den Wohnort aus den Fakten.
Wenn Termine an dem Tag in einem anderen Ort stattfinden,
prüfe das Wetter dort ebenfalls und berichte beides — der Nutzer
plant gern beide Orte mit.

**Tiefe:** Standard ist kurz — Temperatur, allgemeine Wetterlage,
nötigenfalls Niederschlag. Nur bei explizitem Wunsch ausführlicher.

Wenn der Nutzer mit einer Korrektur reagiert, lerne daraus —
schreib die Anpassung in diesen Skill, statt die alte Logik beizubehalten.
```

### 3.2 Front-Matter-Felder

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `themen` | Liste von Themen-Tags für den Lookup | ja |
| `aufgabentyp` | Anliegen-Frame-Klasse, zu der dieser Skill passt (1:1-Bezug) | ja |
| `erstellt` | Datum der ersten Niederschrift | ja |
| `zuletzt_geaendert` | Datum der letzten Edit | ja |
| `gewicht` | Skill-Vertrauensgewicht (siehe §5.4) | ja |
| `status` | `aktiv`, `entwurf`, `archiviert` | ja |
| `urheber` | `nova` oder `mensch` (für initial handgeschriebene Skills) | optional |
| `anwendungs_zaehler` | Wie oft wurde der Skill bisher angewandt? | optional, automatisch |
| `erfolgs_zaehler` | Davon ohne Negativ-Feedback? | optional, automatisch |

### 3.3 Hauptteil-Konventionen

Der Hauptteil ist **bewusst formlos**. Keine festgelegte Struktur, keine erzwungenen Sektionen, keine Step-Listen. Das hat zwei Gründe:

Erstens: Skills sollen lesbar sein wie Notizen, nicht wie Code. Ein Mensch soll einen Skill von Nova überfliegen und verstehen können, was sie sich überlegt hat. Eine starre Struktur würde diese Lesbarkeit kosten.

Zweitens: Skills sollen flexibel editierbar sein. Wenn Nova in der Reflexion merkt, dass ein zusätzlicher Hinweis nötig ist, soll sie ihn einfach anhängen können — nicht erst eine neue Sektion erfinden müssen, die ins Schema passt.

Die einzigen Konventionen im Hauptteil:

- **Markdown-Headlines** für gröbere Unterteilung, wenn der Skill länger wird.
- **Bold-Marker** als visuelle Anker für Schlüsselbegriffe (*Quelle:*, *Ort:*, *Tiefe:*).
- **Beispiele** im Fließtext, wenn das Vorgehen nuanciert ist.
- **Kein** zwingendes "Step-1, Step-2, Step-3" — das LLM komponiert die Sequenz aus dem Beschriebenen.

### 3.4 Größe und Granularität

Skills sollen **kompakt** sein. Eine halbe bis eine ganze Bildschirmseite ist die Faustregel. Wenn ein Skill länger wird, ist das ein Hinweis: möglicherweise vermischt er zwei Aufgaben, die getrennte Skills brauchten — oder er enthält Detail-Wissen, das als Frame-Lager-Eintrag besser aufgehoben wäre.

Anti-Pattern: ein 50-Zeilen-Skill, der jeden möglichen Sonderfall vorwegnimmt. Solche Skills werden vom LLM nicht mehr zuverlässig gelesen, und sie sind im Edit fragil. Pragmatisch: 5–15 Zeilen Hauptteil, plus Front-Matter.

---

## 4. Skill-Speicher

### 4.1 Speicherform

Skills leben als **Dateien im Dateisystem**, nicht als Datenbank-Records. Pfad-Konvention:

```
~/ki-assistent/novaberg/server/skills/
  ├── nova/                      # User-spezifisch (über Pfad)
  │   ├── wetter.md
  │   ├── notiz_baumarkt.md
  │   ├── termin_zahnarzt.md
  │   └── ...
  └── shared/                    # Optional: charakter-übergreifende Skills
      └── ...
```

Begründung: Skills sind Texte, sie wollen versioniert, gelesen, exportiert, manuell editiert werden. Ein Dateisystem-Layout erlaubt das mit Standard-Werkzeugen (Editor, Git, Backup). Eine Datenbank wäre für die wenigen typischen Operationen (Lookup, Read, Write) überspezialisiert.

Indexierung erfolgt über einen **In-Memory-Index**, der beim Server-Start aufgebaut und bei Skill-Edits aktualisiert wird. Skill-Lookup im Cognitive Loop läuft dann ohne File-System-Zugriff in Listenzeit.

### 4.2 Index-Struktur

```python
@dataclass
class SkillIndex:
    pfad: str
    aufgabentyp: str          # 1:1 zu Anliegen-Frame-Klasse
    themen: list[str]          # für Themen-Tag-Lookup
    embedding: np.ndarray      # für semantische Ähnlichkeitssuche
    gewicht: float
    status: str
    front_matter_meta: dict
```

Das Embedding wird aus den Themen-Tags und der ersten Hauptteil-Zeile gebildet — nicht aus dem ganzen Skill-Text, sonst sind die Embeddings dominiert von langen Skills.

### 4.3 Lookup-Mechanik

Wie im Cognitive-Pipeline-Dokument §4.7 beschrieben: themen-basiert mit Embedding-Unterstützung. Konkret:

1. **Aufgabentyp-Match**: Aus dem aufgelösten Anliegen-Frame nehme die Klasse (z.B. `anliegen_wetter`). Suche im Index nach Skills mit identischem `aufgabentyp`. Per **1:1-Invariante** (siehe §6.1) gibt es höchstens einen Treffer.

2. **Wenn Match gefunden**: Skill-Text laden, an den Skill-Executor weiterreichen.

3. **Wenn kein Match gefunden**: Themen-basierter Fallback — durchsuche Skills, deren Themen-Tags mit den Themen aus dem Anliegen-Frame überlappen. Embedding-Distance als Tiebreaker. Mindest-Score-Schwelle, um zufällige Treffer zu vermeiden.

4. **Wenn auch Fallback ohne Treffer**: kein Skill, Default-Vorgehen im Loop (Phase-A-Modus, siehe Pipeline-Dokument §7).

Die Themen-basierte Fallback-Suche ist defensiv und wird nur greifen, wenn die 1:1-Invariante (noch) nicht stabil etabliert ist — vermutlich vor allem in der frühen Phase, wenn die Aufgabentyp-Klassifikation noch nicht zuverlässig ist.

---

## 5. Skill-Lifecycle

Skills entstehen, werden angewendet, geändert, und manchmal sterben. Vier Phasen.

### 5.1 Entstehung — fehler-getrieben

Aus Chat 81 als tragende Designentscheidung: **Skills entstehen aus Negativ-Feedback, nicht aus Vor-Audit oder bei jedem Erfolg.**

Konkret: Wenn der Cognitive Loop in Phase A (ohne Skills) ein Anliegen bearbeitet hat, der Nutzer dann negativ reagiert (Korrektur, Frust-Anstieg, expliziter Widerspruch — siehe Pipeline-Dokument §5), markiert der Reflexionspfad das als Skill-Erstellungs-Kandidat. Pixie nimmt im nächsten Reflexionslauf den Vorgang auf, analysiert:

- Welcher Aufgabentyp lag vor?
- Was war das Vorgehen?
- Was hat der Nutzer korrigiert?
- Wäre die Korrektur als Vorgehens-Anweisung formulierbar?

Wenn ja: Pixie schreibt einen Skill-Entwurf. Status `entwurf`. Beim nächsten passenden Anliegen wird der Entwurfs-Skill aktiv getestet — wenn er funktioniert, wird er nach n Anwendungen ohne Negativ-Feedback automatisch auf `aktiv` gesetzt.

**Was nicht zur Skill-Erstellung führt:**

- Erfolgreich bearbeitete Anliegen (kein Lerngrund — *was schon klappt, braucht keinen Skill*).
- Beiläufige Erwähnungen ohne Korrektur (Themen-Tags wachsen, nicht Skills).
- Einmalige Sonderfälle (zu wenig Datenbasis).

Diese Disziplin schützt vor Skill-Inflation — der Skill-Müllhalde, die das System langsam unbedienbar machen würde.

### 5.2 Anwendung — Skill-Executor

Die Anwendung ist im Cognitive-Pipeline-Dokument §4.8 detailliert. Hier die wichtigste Eigenschaft: **Skills sind Vorschläge, keine Befehle.**

Der Skill-Executor-Prompt enthält explizit:

> *Nutze die Anweisung als Leitfaden, wenn sie auf die Situation passt. Wenn die Anweisung in der konkreten Situation keinen Sinn ergibt, weich davon ab.*

Das gibt dem LLM die Freiheit, einen veralteten oder unpassenden Skill zu ignorieren — und gibt uns gleichzeitig ein Lern-Signal: bei systematischer Abweichung von einem Skill ist das ein Reflexionsmarker (*"Skill stimmt nicht mehr mit der Realität überein"*), der Pixie zur Skill-Pflege anregt.

Bei jeder Anwendung wird im Skill-Index `anwendungs_zaehler` inkrementiert. Bei Erfolg ohne Negativ-Feedback auch `erfolgs_zaehler`. Diese beiden Zähler sind Material für die Pflege-Heuristiken in §5.4.

### 5.3 Edit — bei wiederholtem Negativ-Feedback

Wenn ein bestehender Skill aktiv war und das Anliegen trotzdem zu Negativ-Feedback geführt hat, ist der Skill der Verdächtige. Pixie:

1. Liest den existierenden Skill.
2. Liest die konkrete Korrektur des Nutzers.
3. Vergleicht: Was im Skill hat zu falschem Vorgehen geführt? Was im Nutzer-Feedback widerspricht dem Skill?
4. Schreibt eine **Anpassung** des Skills, die die Korrektur einbaut.
5. Speichert die alte Version als Kommentar im Skill-Text oder im Git-Verlauf der Datei.

Wichtig: Skills werden **angepasst**, nicht ersetzt — die 1:1-Invariante (§6.1) bedeutet, dass es pro Aufgabentyp immer nur einen Skill gibt. Pixie editiert ihn, nicht legt einen neuen an.

Die alte Version sollte irgendwo aufgehoben werden (Kommentar, Git-Log, Backup) — nicht aus Daten-Hoarder-Mentalität, sondern weil bei einer fehlerhaften Anpassung ein Rollback möglich sein muss.

### 5.4 Decay und Tod

Nicht jeder Skill bleibt nützlich. Drei Decay-Mechaniken:

**Niedriges Vertrauensgewicht.** Wenn ein Skill mehrfach hintereinander zu Negativ-Feedback führt (Anwendungs-Zähler hoch, Erfolgs-Zähler niedrig), sinkt sein `gewicht`. Bei Schwelle `gewicht < 0.3` wird er auf Status `entwurf` zurückgesetzt — Pixie soll ihn überarbeiten.

**Lange Inaktivität.** Skills, die 6+ Monate nicht angewandt wurden, werden archiviert (`status=archiviert`). Sie bleiben im Speicher, aber im Lookup nicht mehr berücksichtigt. Wenn das Thema später wieder relevant wird, kann Pixie sie reaktivieren.

**Aktive Außerkraftsetzung.** Wenn der Nutzer explizit sagt *"vergiss diese Wetter-Logik"*, soll Nova den Skill löschen können. Pragmatisch: Pixie setzt den Skill auf Status `archiviert`, das wirkt wie ein Soft-Delete.

Vollständige Löschung passiert nur über manuelles Eingreifen (Datei-Removal). Soft-Delete ist die Norm.

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

## 8. Selbst-Lernen — die Reflexions-Mechanik

Skills entstehen und ändern sich autonom. Die Mechanik dazu ist über zwei Schichten verteilt: synchron im Cognitive Loop (Markierung von Lern-Material) und asynchron im Pixie-Reflexionslauf (Skill-Schreibung).

### 8.1 Synchrone Markierung

Während eines Cognitive-Loop-Durchlaufs werden Reflexionsmarker gesetzt, wenn relevante Ereignisse eintreten:

| Marker | Auslöser | Konsequenz |
|---|---|---|
| `negativ_explizit` | Korrektur-Detektor (Pipeline §5.1) erkennt Widerspruch | Skill-Edit oder -Erstellungs-Kandidat |
| `negativ_implizit` | EI-Frust-Anstieg (Pipeline §5.2) | Skill-Edit-Kandidat (schwächer) |
| `validierungs_konflikt` | Cross-Frame-Konflikt (Pipeline §5.3) | Skill-Kandidat-Notiz für Pixie |
| `skill_abweichung` | Skill war aktiv, LLM hat nicht gefolgt | Skill-Pflege-Kandidat |
| `erfolg_ohne_skill` | Default-Vorgehen erfolgreich, kein Skill vorhanden | Niedrige Notiz für Aggregation |

Marker werden in eine Skill-Reflexions-Queue geschrieben (Redis-Liste oder ähnlich), damit Pixie sie aufnehmen kann.

### 8.2 Asynchrone Skill-Pflege durch Pixie

Im periodischen Reflexionslauf (alle paar Minuten, je nach Last) liest Pixie die Reflexions-Queue und entscheidet pro Marker:

**Bei `negativ_explizit`** mit klarem Korrektur-Material:

- Existiert ein Skill für den Aufgabentyp? → Edit-Pfad: Skill-Anpassung schreiben.
- Existiert keiner? → Neu-Erstellungs-Pfad: Skill-Entwurf schreiben.

**Bei `negativ_implizit` ohne klares Korrektur-Material:**

- Marker akkumulieren. Wenn n ähnliche Marker zum selben Aufgabentyp innerhalb eines Zeitraums auftreten → Skill-Edit (oder -Erstellung).
- Einzelne Frust-Marker werden ignoriert (Rauschen-Schwelle).

**Bei `validierungs_konflikt`:**

- Notiz zum Aufgabentyp anlegen (interne Pixie-Notiz, nicht User-sichtbar). Bei Wiederholung → Skill-Kandidat.

**Bei `skill_abweichung`:**

- Wenn das LLM systematisch (n Mal) von einem Skill abweicht, prüfen: Skill veraltet? Falsch formuliert? Pixie liest den Skill, vergleicht mit den abweichenden Vorgehen, schreibt Anpassung.

**Bei `erfolg_ohne_skill`:**

- Niedrige Aggregation. Wenn n erfolgreiche Anwendungen desselben Aufgabentyps ohne Skill auftreten, könnte ein Skill helfen — aber nur, wenn auch *Variation* zwischen den Vorgehen sichtbar ist (das Default-Vorgehen ist nicht immer ideal). Schwacher Trigger, niedrige Priorität.

### 8.3 Skill-Entwurf-LLM-Call

Pixie schreibt Skill-Entwürfe und -Edits über LLM-Calls. Der Prompt enthält:

- Den Aufgabentyp und das Anliegen-Frame-Schema.
- Das Vor-Vorgehen, das zu Negativ-Feedback geführt hat.
- Die Korrektur-Aussage des Nutzers (wenn vorhanden).
- Den existierenden Skill-Text (bei Edit).
- Die Skill-Format-Konvention (Front-Matter, Hauptteil-Stil).

Der LLM-Output ist die neue Skill-Datei. Pixie validiert das Format (gültiges Front-Matter, Aufgabentyp-Konsistenz), schreibt die Datei, aktualisiert den Index.

### 8.4 Audit-Trail

Skill-Edits sollen nachvollziehbar bleiben. Zwei Mechaniken:

- **Datei-Versionierung über Git.** Wenn das `~/ki-assistent/novaberg/server/skills/`-Verzeichnis als Git-Repo geführt wird, ist jeder Edit ein Commit mit Auto-Message (*"Skill wetter.md angepasst aus Reflexion vom 2026-05-09"*).
- **In-File-Kommentare.** Pixie kann am Ende des Skill-Texts einen kurzen Kommentar anhängen: *"<!-- Geändert 2026-05-09 nach Korrektur 'nicht in Donauwörth, in Treuchtlingen' -->"*. Das ist redundant mit Git, aber nützlich für menschliche Leser.

Beide zusammen: belastbarer Audit-Trail ohne separate Datenbank.

---

## 9. Beispiel-Skills

Drei Skills als Lehrbeispiele, in der Größe, die wir anstreben.

### 9.1 Wetter-Anfragen

```markdown
---
themen: [wetter, klima, vorhersage, agrarwetter]
aufgabentyp: anliegen_wetter
erstellt: 2026-04-15
zuletzt_geaendert: 2026-05-08
gewicht: 1.0
status: aktiv
urheber: nova
anwendungs_zaehler: 23
erfolgs_zaehler: 21
---

# Wetter-Anfragen

Wenn nach dem Wetter gefragt wird, beachte folgendes Vorgehen:

**Quelle:** Für Anfragen zum Wohnort des Nutzers (Wolferstadt) und
ländlicher Regionen liefert agrarwetter.org die brauchbarsten Daten —
ergänze daher den Suchbegriff um "agrarwetter" oder den Ort.
Bei Großstädten oder fernen Orten reicht eine allgemeine Wettersuche.

**Ort:** Wenn kein Ort genannt wird, nimm den Wohnort aus den Fakten.
Wenn Termine an dem Tag in einem anderen Ort stattfinden,
prüfe das Wetter dort ebenfalls und berichte beides — der Nutzer
plant gern beide Orte mit.

**Tiefe:** Standard ist kurz — Temperatur, allgemeine Wetterlage,
nötigenfalls Niederschlag. Nur bei explizitem Wunsch ausführlicher.

<!-- Geändert 2026-05-08: Termine-an-anderem-Ort-Logik ergänzt nach
     Korrektur 'ich bin doch in Hamburg' -->
```

### 9.2 Notizen-Listen-Verwaltung

```markdown
---
themen: [notiz, liste, einkaufsliste, todo, baumarkt]
aufgabentyp: anliegen_notiz_listen_management
erstellt: 2026-04-22
zuletzt_geaendert: 2026-04-22
gewicht: 1.0
status: aktiv
urheber: nova
anwendungs_zaehler: 17
erfolgs_zaehler: 17
---

# Listen-Verwaltung

Wenn der Nutzer Items auf eine Liste setzen möchte, nutze NotizenAgent
mit Container-Typ "liste".

**Bezugs-Auflösung:** Wenn der Nutzer mit Pronomen oder Bezugswörtern
auf eine Liste verweist (*"setze das auf die Liste"*, *"die Liste"*,
*"sie"*), prüfe den Vor-Turn-Kontext: über welche Liste wurde zuletzt
gesprochen? Wenn unklar, frag nach.

**Container-Wechsel:** Wenn aus einer Notiz eine Liste werden soll,
verwende `add_content` mit Container-Typ-Wechsel — verweigere das nicht
mit der Begründung "ist eine Notiz und keine Liste". Das ist legitim.

**Mehrere Items:** Bei mehreren Items in einem Turn (*"Schrauben, Dübel,
Muttern"*) leg sie als einzelne Items in der Liste an, nicht als
Klammer-Text in einem Item.
```

### 9.3 Termin-Anlage Zahnarzt

```markdown
---
themen: [termin, zahnarzt, zahnreinigung, treuchtlingen]
aufgabentyp: anliegen_termin_zahnarzt
erstellt: 2026-03-10
zuletzt_geaendert: 2026-04-30
gewicht: 1.0
status: aktiv
urheber: nova
anwendungs_zaehler: 8
erfolgs_zaehler: 8
---

# Zahnarzt-Termin

Wenn ein Zahnarzt-Termin angelegt werden soll, vervollständige die Slots
über Vor-Wissen und frag nur, was wirklich offen ist.

**Ort:** Default ist Treuchtlingen (Praxis Müller) — der Nutzer geht
seit 2024 dorthin. Nur fragen, wenn ein neuer Ort genannt wurde.

**Anlass:** Bei Routine-Terminen ist meist Zahnreinigung gemeint.
Wenn der Nutzer Schmerzen oder konkretes Anliegen erwähnt, nimm das.

**Bestätigung:** Bei Default-Annahmen (Ort, Anlass) im Antwort-Text
kurz erwähnen, damit der Nutzer korrigieren kann, falls anders gemeint.

<!-- Erstellt 2026-03-10 nach drei aufeinanderfolgenden Zahnarzt-Anlagen
     mit identischen Slots -->
```

---

## 10. Risiken

**Skill-Inflation.** Trotz 1:1-Invariante könnten zu viele Aufgabentypen entstehen, jeder mit eigenem Skill. Gegenmaßnahme: Aufgabentyp-Granularität durch Frame-Klassen kontrolliert (siehe §6.1). Wenn das Frame-Lager weniger Klassen unterscheidet als nötig, wachsen Skills auch nicht.

**Skill-Drift.** Pixie könnte Skills schreiben, die im Sprachstil oder Detailgrad inkonsistent sind. Gegenmaßnahme: Skill-Format-Konvention im Pixie-Schreib-Prompt mitgeben, plus periodische Audits durch Mensch oder Pixie selbst.

**Skill-Spam in Phase C.** Pixie schreibt zu viele Entwurfs-Skills, die nie aktiv werden. Gegenmaßnahme: Erstellungs-Schwelle (z.B. nur bei `negativ_explizit` mit klarem Material; bei `negativ_implizit` erst nach n Akkumulationen).

**Kollision mit Default-Vorgehen.** Skill und Default-Vorgehen könnten unterschiedlich sein, ohne dass das LLM merkt, wann welches besser passt. Gegenmaßnahme: Vorschlags-Charakter des Skills (§6.3), plus Reflexionsmarker bei systematischer Abweichung.

**Falsch geschriebene Skills.** Pixie schreibt einen Skill mit Logik-Fehler oder Halluzination. Gegenmaßnahme: User-Feedback als Korrektur-Quelle — bei nächster Anwendung wird der Fehler durch Negativ-Feedback sichtbar, Pixie korrigiert. Plus: Status `entwurf` für die ersten n Anwendungen, bei Erfolg auf `aktiv` setzen.

**Pixie-Reflexionslauf belastet System.** Skill-Schreibung ist LLM-Call. Gegenmaßnahme: niedriges Frequenz-Setting für die Reflexions-Schleife, Aggregation mehrerer Marker zu einem Schreib-Vorgang.

**Datei-System-Korruption.** Skills sind Dateien — was, wenn Pixie eine Datei zerschießt? Gegenmaßnahme: Git-Versionierung des Skill-Verzeichnisses (5.4), plus optionaler Read-Only-Modus für hartcodierte Skills (Mensch-geschriebene als read-only markiert).

---

## 11. Phasen-Plan

Skills sind durch den Cognitive-Pipeline-Phasen-Plan abgedeckt — Phase B und Phase C dort sind die Skill-Phasen.

### Phase B (aus Cognitive-Pipeline §11) — Skill-Speicher und -Anwendung

**Ziel hier:** Skill-Speicher anlegen, manuell geschriebene Skills für die häufigen Aufgabentypen, Skill-Lookup im Cognitive Loop aktiv.

**Skills-spezifische Schritte:**

1. Skill-Verzeichnis-Struktur anlegen (`~/ki-assistent/novaberg/server/skills/`).
2. Skill-Format-Validator schreiben (Front-Matter-Check, Aufgabentyp-Existenz).
3. Skill-Index-Aufbau beim Server-Start.
4. Drei bis fünf manuelle Skills für häufige Aufgabentypen schreiben (Wetter, Notiz-Listen, Termin-Anlage).
5. Skill-Lookup im Pipeline-Schritt 4.7 aktivieren.
6. Skill-Executor-Prompt im Schritt 4.8 mit Skill-Text-Block.
7. Live-Beobachtung: Welche Skills werden befolgt, welche umgangen?

**Erfolgskriterium:** Drei manuelle Skills sind aktiv, nachweislich in mindestens 80% der passenden Fälle befolgt, ohne Werkzeug-Schicht-Verletzungen.

### Phase C (aus Cognitive-Pipeline §11) — Selbst-lernende Skills

**Ziel hier:** Pixie schreibt und ändert Skills autonom auf Basis von Negativ-Feedback.

**Skills-spezifische Schritte:**

1. Reflexions-Queue schreiben (Redis-Liste `skill_reflektion:{user_id}`).
2. Pipeline-Marker-Schreibung in den entsprechenden Schritten (4.6, 5.1–5.4).
3. Pixie-Task `skill_pflege` schreiben — periodisch die Queue lesen, pro Marker entscheiden.
4. Skill-Schreib-LLM-Call mit Format-Konvention.
5. Skill-Edit-LLM-Call analog.
6. Status-Übergänge implementieren (`entwurf` → `aktiv` nach n erfolgreichen Anwendungen).
7. Decay-Mechanik (`gewicht`-Reduktion bei wiederholtem Negativ-Feedback).
8. Git-Versionierung des Skill-Verzeichnisses einrichten.

**Erfolgskriterium:** Nova schreibt eigenständig mindestens drei Skills aus Praxis-Beobachtung, davon mindestens zwei stabil (kein Re-Edit nach erster Anwendung).

---

## 12. Offene Punkte

### 12.1 Aufgabentyp-Granularität

Wenn das Frame-Lager `anliegen_wetter` als eine Klasse führt, gibt es einen Wetter-Skill. Aber: möglicherweise wären Subklassen sinnvoller — `anliegen_wetter_lokal` vs. `anliegen_wetter_termine_einbeziehend`. Aktuell offen, ob Skills ein eigenes Granularitäts-Schema brauchen oder ob die Frame-Lager-Klassen reichen.

Pragmatisch: zunächst Frame-Lager-Klassen 1:1 nutzen. Wenn sich zeigt, dass mehrere Skills denselben Aufgabentyp betreffen würden, ist das ein Hinweis, dass die Klasse zu grob ist — entweder Frame-Lager-Klasse splitten oder Skill-Subklassen einführen.

### 12.2 Skill-Verstärkung bei Erfolg

Heute: Skills entstehen aus Negativ-Feedback, werden bei Negativ-Feedback geändert. Kein Mechanismus, der Skills *verstärkt*, wenn sie erfolgreich sind.

Alternative: bei jedem `erfolgs_zaehler++` das `gewicht` leicht erhöhen (z.B. 0.01). Damit driften erfolgreiche Skills im Gewicht nach oben, und beim Lookup kann Gewicht als Tiebreaker dienen, wenn Themen-Tag-Treffer mehrdeutig sind. Implementierung trivial, Wirkung unklar — offen.

### 12.3 Skill-Sharing zwischen Charakteren

Wenn ein Nutzer mehrere Charaktere hat (Nova, anderer), sollen Skills geteilt werden? Ein "Liste-Verwaltung"-Skill ist wahrscheinlich charakter-unabhängig — er beschreibt Plugin-Nutzung, nicht Persönlichkeit. Ein "Wetter-Anfragen"-Skill mit Wohnort-Default ist nutzer-spezifisch, aber charakter-unabhängig.

Schema-Vorschlag (§4.1) sah einen `shared/` -Ordner vor. Implementierung der Sharing-Logik offen — vermutlich nicht in Phase B/C, sondern später.

### 12.4 Mensch-geschriebene Skills

Phase B startet mit drei bis fünf manuell geschriebenen Skills. Sind die ungesetzlich für Pixie? Pragmatisch: Front-Matter-Feld `urheber: mensch` plus `darf_pixie_aendern: false` als Schutz. Pixie liest, befolgt, aber editiert nicht. Bei Negativ-Feedback markiert Pixie das als Hinweis für menschliches Edit, schreibt aber nicht selbst.

Alternative: keine Sonderbehandlung, Pixie editiert auch Mensch-Skills. Risiko: Mensch-Intent geht verloren. Noch zu entscheiden.

### 12.5 Skill-Embeddings — was indexieren?

Aus §4.2: Embedding aus Themen-Tags und erster Hauptteil-Zeile. Alternative: ganzer Hauptteil. Kompromiss: erste 500 Zeichen.

Performance-Frage in der Implementierung. Pragmatisch: kurze Embeddings reichen für Themen-Lookup, lange Embeddings für Detail-Match. Hot-Path braucht keine Detail-Match, also kurz.

### 12.6 Decay-Schwellwerte

Wann ist ein Skill "lange inaktiv"? 6 Monate ist eine Zahl aus der Hüfte. Pragmatisch: konservativ kalibrieren (eher länger), bei Bedarf nachjustieren.

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

---

*Stand 09.05.2026 — Chat 81. Skills als selbst-editierbare Markdown-Dateien für wiederkehrende Anliegen. 1:1-Invariante (Aufgabentyp ↔ Skill). Modulation statt Werkzeug-Auswahl. Fehler-getrieben entstehend, autonom editiert durch Pixie, Vorschlags-Charakter im Executor. Phase A funktioniert ohne Skills — sie sind die Verfeinerung, nicht die Grundlage.*
