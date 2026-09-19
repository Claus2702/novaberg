# Novaberg — Skills (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-thinking-skills_k.md`](novaberg-thinking-skills_k.md) · Bauplan und Umstellung: [`novaberg-thinking-skills_b.md`](novaberg-thinking-skills_b.md) · Diskussion und Ergänzungen: [`novaberg-thinking-skills_e.md`](novaberg-thinking-skills_e.md) · Messungen: keiner. Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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
seit 2024 dorthin. Nur fragen, wenn ein neuer Ort genannt wurde. `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]`

**Anlass:** Bei Routine-Terminen ist meist Zahnreinigung gemeint.
Wenn der Nutzer Schmerzen oder konkretes Anliegen erwähnt, nimm das.

**Bestätigung:** Bei Default-Annahmen (Ort, Anlass) im Antwort-Text
kurz erwähnen, damit der Nutzer korrigieren kann, falls anders gemeint.

<!-- Erstellt 2026-03-10 nach drei aufeinanderfolgenden Zahnarzt-Anlagen
     mit identischen Slots -->
```
