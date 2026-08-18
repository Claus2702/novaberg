# Novaberg — Tool: Datei-Operationen (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Datei-Operationen — Intelligentes Lesen und Bearbeiten von Dateien
**Stand:** 18. August 2026 (Leseschicht, Schreibschicht und Versionierung gebaut); davor 29. April 2026, Chat 70

> **Bauzustand am 18.08.2026.** Die Operationen dieses Konzepts sind nicht mehr Entwurf:
>
> | Modul | Inhalt | Zeugen |
> |---|---|---|
> | `tools/dateien/operationen.py` | `struktur_analysieren`, `block_lesen`, `zeilen_lesen`, `datei_grep`, `metadaten_lesen`, `datei_suchen` | 26 |
> | `tools/dateien/redaktion.py` | `block_ersetzen`, `block_anfuegen`, `block_einfuegen`, `str_ersetzen`, `metadaten_setzen` | 20 |
> | `tools/dateien/versionierung.py` | §3.4 vollständig, dazu `aktuell_lesen` und `paarung_pruefen` | 20 |
> | `tools/dateien/hand.py` | die Auftragsform `DATEI: {json}` | 22 |
>
> **Zwei Abweichungen gegenüber diesem Konzept**, beide begründet: Die Wurzel ist bei jedem Aufruf ein **Pflichtargument** ohne Vorgabewert — ein Lesewerkzeug ohne Zonenangabe ist eine Zone ohne Grenze. Und `str_replace_in_block` heißt `str_ersetzen` mit optionalem `header`, weil der Suchraum bei Dateien ohne Blöcke ohnehin die ganze Datei ist.
>
> **Die Ankertreue ist gemessen, nicht angenommen:** 30 von 30 zeichengenaue, eindeutige Anker an echten Wissensdateien — `gemma4-gpu` mit Median 1,7 s, `qwen36-cpu` mit 17,9 s. **Was fehlt, ist der Aufrufer.**
**Pfad:** novaberg/docs/novaberg-tool-dateien_k.md
**Quellen:** Chat 70 (autoresearch-Analyse, Claude Code Leak, SWE-agent, Aider, Letta)

---

## 1. Aufgabe

> **Die Prämisse dieses Abschnitts gilt nur noch für den Gesprächspfad.** Gemessen am laufenden System am 04.08.2026, 21:02 UTC, Connector `qwen36`: Der GPU-Pfad (`gemma4-gpu`, Gespräch) steht bei **32768**, der CPU- und der Analyse-Pfad (`qwen36-cpu`, Hintergrund) bei **262144** — dem Achtfachen.
>
> Für die Hintergrund-Agenten — Recherche, Vertiefung, Traum, Nachfragen — ist der fraktale Zoom damit **nicht mehr erzwungen**: Eine vollständige Wissen-Datei von wenigen Kilobyte passt mühelos in den Prompt. Er bleibt trotzdem sinnvoll, wo Token Geld und Zeit kosten oder wo ein gezielter Block genauer ist als eine ganze Datei; er ist nur keine Notwendigkeit mehr, sondern eine Wahl.
>
> **Für den Gesprächspfad bleibt der Abschnitt unverändert gültig.** Dort ist die Grenze real, und der Enricher liest gegen dieselben 32768 wie zuvor.
>
> Der Text unten bleibt als Herkunft stehen (`40_DOKU_GRUNDSAETZE`: markieren, nicht löschen).

Novas Kontext hat 32768 Tokens. System-Prompt, Charakter, Session, Gedaechtnis belegen einen erheblichen Teil davon. Grosse Dateien koennen nicht vollstaendig in den Prompt geladen werden. Trotzdem muss Nova bestehende Dateien lesen, verstehen, gezielt durchsuchen und chirurgisch bearbeiten koennen.

`tools/dateien/` stellt dafuer eine Sammlung deterministischer Python-Funktionen bereit. Kein LLM in den Tools — der Agent denkt (LLM), das Tool fuehrt aus (Python). Exakt das Prinzip "Berechnung in Python, nicht im LLM."

---

## 2. Kernprinzip — Fraktaler Zoom (Mandelbrot-Navigation)

Wie bei der Mandelbrotmenge: Jeder Zoom-Schritt zeigt mehr Detail in einem kleineren Bereich. Kein Schritt braucht das Gesamtbild. Das LLM entscheidet nach jedem Schritt, ob es tiefer zoomen muss oder genug Kontext hat.

```
Level 0: Verzeichnis scannen
          → "3 Dateien zu 'blockchain'" (~20 Tokens)

Level 1: Struktur analysieren
          → "5 Bloecke: ## Konsens (Z.8-35), ## Smart Contracts (Z.36-60), ..."
            (~50 Tokens)

Level 2: Zielblock lesen
          → Inhalt von ## Smart Contracts (~200 Tokens)

Level 2b: Block zu gross → Haeppchenweise lesen
          → Zeilen 0-200 von 412, rest: 212 (~200 Tokens)

Level 3: Innerhalb des Blocks suchen (grep)
          → Zeilen mit "Security" (~30 Tokens)

Edit:     Block erweitern, ersetzen, oder str_replace innerhalb
          → Chirurgischer Eingriff, Rest der Datei unberuehrt
```

Jeder Schritt verbraucht nur so viele Tokens wie noetig, um die naechste Entscheidung zu treffen.

**Referenz:** Claude Codes autoDream-Service arbeitet identisch — "Don't exhaustively read transcripts. Look only for things you already suspect matter." (Quelle: Claude Code Leak-Analyse, github.com/Piebald-AI/claude-code-system-prompts)

---

## 3. Operationen

**Datei:** `tools/dateien/operationen.py`

### 3.1 Navigation (Token-sparsam)

```python
def datei_suchen(verzeichnis: str, muster: str) -> list[str]:
    """Glob-Suche nach Dateien.
    
    Args:
        verzeichnis: Pfad zum Verzeichnis
        muster: Glob-Pattern, z.B. '*blockchain*_wissen.md'
    
    Returns:
        Liste der Dateipfade (sortiert)
    
    Token-Kosten: ~5 pro Treffer (nur Dateinamen)
    """

def struktur_analysieren(pfad: str) -> list[dict]:
    """Erkennt Markdown-Struktur ohne Inhalt zu laden.
    
    Liest die Datei zeilenweise, extrahiert Header (#, ##, ###)
    und deren Zeilenbereiche. Das LLM bekommt eine Karte, nicht den Inhalt.
    
    Returns:
        [{"header": "## Smart Contracts", "ebene": 2,
          "start": 36, "ende": 60, "zeilen": 25}]
    
    Token-Kosten: ~15 pro Block (Header + Zahlen)
    """

def datei_grep(pfad: str, suchbegriff: str,
               regex: bool = False) -> list[tuple[int, str]]:
    """Zeilenweise Suche in einer Datei.
    
    Returns:
        Liste von (Zeilennummer, Zeileninhalt)
    
    Token-Kosten: ~10 pro Treffer
    """
```

### 3.2 Lesen (gezielt)

```python
def datei_lesen(pfad: str) -> str:
    """Liest eine Datei vollstaendig.
    
    Nur fuer kleine Dateien (<DATEI_MAX_VOLLSTAENDIG Zeichen).
    Bei grossen Dateien: struktur_analysieren + block_lesen.
    """

def block_lesen(pfad: str, header: str,
                offset: int = 0, limit: int = 200) -> dict:
    """Liest einen Block haeppchenweise.
    
    Wenn der Block klein genug ist, kommt alles in einem Aufruf.
    Bei grossen Bloecken wird gefenstert gelesen — wie SWE-agents
    Viewer (100 Zeilen pro Turn) oder Claude Codes view_range.
    
    Args:
        pfad: Dateipfad
        header: Exakter Header-Text, z.B. '## Smart Contracts'
        offset: Ab welcher Zeile innerhalb des Blocks (0-basiert)
        limit: Maximale Zeilen pro Aufruf (Default: DATEI_BLOCK_LIMIT)
    
    Returns:
        {"inhalt": "...",
         "block_zeilen": 412,
         "gelesen_von": 0,
         "gelesen_bis": 200,
         "rest": 212}
    
    Das LLM entscheidet nach jedem Haeppchen: weiterlesen,
    grep, editieren, oder abbrechen.
    """

def zeilen_lesen(pfad: str, von: int, bis: int) -> dict:
    """Liest einen Zeilenbereich (Fallback ohne Markdown-Struktur).
    
    Fuer Dateien ohne Header oder fuer strukturlose User-Dateien.
    
    Args:
        von: Startzeile (1-basiert)
        bis: Endzeile (inklusiv)
    
    Returns:
        {"inhalt": "...",
         "datei_zeilen": 1847,
         "gelesen_von": 1,
         "gelesen_bis": 200,
         "rest": 1647}
    """

def metadaten_lesen(pfad: str) -> dict[str, str]:
    """Liest den Metadaten-Header einer Datei.
    
    Erkennt Zeilen mit '**Feld:** Wert' am Dateianfang.
    
    Returns:
        {"Erstellt": "29. April 2026", "Durchlaeufe": "2"}
    """
```

### 3.3 Schreiben (chirurgisch)

```python
def datei_schreiben(pfad: str, inhalt: str) -> bool:
    """Schreibt eine Datei vollstaendig (Neuanlage oder Ueberschreiben)."""

def block_ersetzen(pfad: str, header: str, neuer_inhalt: str) -> bool:
    """Ersetzt den gesamten Inhalt eines Blocks.
    Header bleibt, Text darunter wird ersetzt, Rest der Datei unberuehrt."""

def block_anfuegen(pfad: str, header: str, zusatz: str) -> bool:
    """Haengt Text an einen bestehenden Block an."""

def block_einfuegen(pfad: str, vor_header: str | None,
                     neuer_header: str, inhalt: str) -> bool:
    """Fuegt einen komplett neuen Block ein.
    vor_header=None bedeutet: am Ende der Datei."""

def str_replace_in_block(pfad: str, header: str,
                          old_str: str, new_str: str) -> dict:
    """Ersetzt Text innerhalb eines Blocks (feinkoernig).
    
    Prueft auf Eindeutigkeit innerhalb des Blocks. Wenn old_str
    nicht eindeutig: Fehlermeldung zurueck ans LLM mit Hinweis,
    mehr Kontext (Zeilen davor/danach) mitzugeben.
    
    Das LLM versucht es erneut mit laengerem old_str, bis der
    Text eindeutig ist. Dasselbe Pattern wie bei SWE-agent und
    Aider (Search/Replace-Bloecke).
    
    Returns:
        {"erfolg": True} oder
        {"erfolg": False, "grund": "nicht_eindeutig", "anzahl": 2,
         "hinweis": "Text kommt 2x vor. Mehr Kontext mitgeben."}
    """

def metadaten_aktualisieren(pfad: str, feld: str, wert: str) -> bool:
    """Aktualisiert ein Metadaten-Feld im Header."""
```

---

## 3.4 Versionierung im Dokument (Entwurf, 17.08.2026)

**Ein Wissenstext, der über Monate wächst, ist ein Verlauf und kein Zustand.** Ein `str_replace_in_block` ist endgültig: Was überschrieben wird, ist weg. Die Vorbilder aus §7 brauchen dafür nichts, weil sie in einem Repositorium arbeiten — hier gibt es keins.

### 3.4.1 Drei Marken, und die Pfeilrichtung sagt, wo man ist

| Marke | Vorgang | Was unten steht |
|---|---|---|
| `[cN>]` | **Change** — der Absatz wurde geändert | der Absatz **davor** |
| `[dN>]` | **Delete** — der Absatz wurde entfernt | der **entfernte** Absatz |
| `[iN>]` | **Insert** — der Absatz kam hinzu | **nichts** — es gab kein Davor |

**Der Pfeil zeigt im Text nach rechts und in der Anmerkung nach links.** `[c1>]` verweist nach unten, `[<c1_…]` verweist zurück. Die Richtung ist damit an der Marke selbst ablesbar, ohne die Stelle zu kennen.

```
[<Typ><Nummer>_<Version>_<Datum>]
```

**Ohne Leerzeichen innerhalb der Marke** — eine Marke, die an einem Leerzeichen zerfällt, ist nicht mehr sicher zu finden, wenn ein Textwerkzeug Zeilen umbricht.

### 3.4.2 Wie es aussieht

```markdown
Hier steht der Absatz davor.
[d2>]
Hier steht der Absatz danach.


## Änderungen

[<d2_2.3_2026-08-17]
[c1>]Der Text wurde schon geändert.

[<c1_2.2_2026-08-16]
Der Text wurde neu angelegt.
```

**Zu lesen ist das so:** An der Stelle von `[d2>]` stand ein Absatz, der in Version 2.3 entfernt wurde. Sein Wortlaut steht unten — und er trug seinerseits schon eine Marke, weil er in Version 2.2 geändert worden war. Deren Vorgänger steht darunter.

### 3.4.3 Die vier Regeln, die den Verlauf rekonstruierbar machen

**Erstens: Archiveinträge sind gewöhnlicher Text und dürfen Marken tragen.** Genau daraus entsteht die Kette. Ein Absatz, der geändert und später gelöscht wurde, hat beide Vorgänge — der Löscheintrag enthält die Änderungsmarke, und die führt eine Stufe tiefer.

**Zweitens: Die Position sagt, ob eine Fassung lebt.** Steht `[c1>]` im laufenden Text, ist c1 die geltende Fassung. Steht dieselbe Marke **innerhalb** eines Archiveintrags, gehört sie zu einer abgelösten Fassung. Es braucht dafür kein zusätzliches Feld — die Marke steht dort, wo ihr Text steht.

**Drittens: Die Version in der Marke ist die, in der die Änderung geschah** — nicht die des archivierten Textes. `[<c1_2.2_…]` heißt: In Version 2.2 wurde geändert, und darunter steht, was vorher galt. Ohne diese Festlegung ist bei jeder Rekonstruktion offen, ob eine Zahl den Zustand vorher oder nachher benennt.

**Viertens: Der jüngste Eintrag steht oben.** Wer wissen will, was zuletzt geschah, liest die erste Zeile des Blocks und nicht die letzte.

> **Damit ist der Verlauf umkehrbar, und das war der Zweck.** Eine frühere Fassung entsteht, indem man von der laufenden Fassung rückwärts über die Versionen geht: `d` wieder einsetzen, `c` durch den Vorgänger ersetzen, `i` entfernen. Jeder Schritt ist eindeutig, weil jede Marke genau einen Eintrag hat.

### 3.4.4 Insert trägt keinen Rumpf — und bekommt trotzdem einen Eintrag

**Bei `[iN>]` gibt es nichts zu archivieren.** Die Marke ist die ganze Aussage: *dieser Absatz kam in Version X hinzu.* Rückgängig gemacht wird ein Insert, indem man den markierten Absatz entfernt — dafür genügt der Anker.

**Der Eintrag unten bleibt trotzdem stehen, mit leerem Rumpf.** Der Grund ist nicht Symmetrie, sondern die Prüfbarkeit aus §3.4.5: Sobald ein Marken-Typ ohne Eintrag zulässig wäre, ließe sich ein fehlender Eintrag nicht mehr von einem erlaubten Fall unterscheiden — und die Invariante, die den einzigen Detektor dieses Bereichs trägt, wäre keine mehr.

### 3.4.5 Die Paarung ist maschinell prüfbar — und das ist der Grund für dieses Format

**Jede Marke `[xN>]` hat genau einen Eintrag `[<xN_…]`, und jeder Eintrag genau eine Marke.** Das ist eine Invariante über eine einzelne Datei, ohne Kontext und ohne Modell prüfbar:

| Befund | Bedeutung |
|---|---|
| Marke ohne Eintrag | die Auslagerung ist verlorengegangen |
| Eintrag ohne Marke | der Text wurde ersetzt, ohne die Marke mitzunehmen |
| Nummer zweimal im Text | der Zähler ist gerissen |
| Version nicht fortlaufend | ein Eintrag fehlt oder wurde von Hand geändert |

> **Das wiegt schwerer als die Lesbarkeit.** Eine Markierung in Prosa kann man vergessen, und **niemand merkt es** — auf dem Inhalt einer Wissensdatei steht kein Zeuge. Eine Markenpaarung kann man ebenfalls vergessen, aber **ein Script sieht es sofort.** Damit bekommt ein Bereich, der bisher gar keinen Detektor hatte, den ersten.

### 3.4.6 Warum die Auslagerung nichts kostet

**Der Anker bleibt beim Leser, der Rumpf geht ans Ende.** Wo Widerlegtes im Fließtext markiert wird, wächst der Text genau dort, wo gelesen wird; ein Absatz mit drei Korrekturschichten ist beim vierten Lesen nicht mehr die Aussage, sondern ihre Geschichte.

> **Und die Blockstruktur zahlt sich hier ein zweites Mal aus.** Weil der Zugriff über `struktur_analysieren` und `block_lesen` läuft, ist der Änderungsblock ein Block wie jeder andere — **er wird schlicht nie geladen**, solange niemand nach der Geschichte fragt. Die Auslagerung kostet damit Platte, nicht Kontext. Bei einem Format, das die ganze Datei liest, wäre dasselbe Schema ein Nachteil.

### 3.4.7 Was noch zu entscheiden ist

- **Ab wann ist eine Änderung eine Version?** Ein berichtigter Tippfehler soll keine Marke bekommen, eine geänderte Aussage schon. Die Grenze ist ein Urteil und gehört in die Anweisung, nicht in den Code.
- **Wie zählt die Version?** Die Beispiele zeigen `2.2`, `2.3` — ob die zweite Stelle je Änderung steigt und wann die erste, ist nicht gesetzt.
- **Wird der Änderungsblock je beschnitten?** Er wächst monoton. Solange er ein eigener Block ist, kostet er keinen Kontext; eine Obergrenze wäre denkbar und ist nicht gesetzt.
- **Gilt das Format auch für fremde Dateien?** Nein — in freigegebenen Wurzeln wird nicht geschrieben. Es gilt ausschließlich in ihrer eigenen Zone.

---

## 4. Zoom-Stufen auf einen Blick

| Stufe | Werkzeug | Token-Kosten | Wann |
|-------|----------|-------------|------|
| **Karte** | `struktur_analysieren()` | ~15/Block | Immer zuerst |
| **Block** | `block_lesen(header)` | ~200/Aufruf | Zielblock identifiziert |
| **Fenster** | `block_lesen(header, offset, limit)` | ~200/Haeppchen | Block > 200 Zeilen |
| **Fallback** | `zeilen_lesen(von, bis)` | ~200/Haeppchen | Kein Markdown |
| **Nadel** | `datei_grep(suchbegriff)` | ~10/Treffer | Gezielte Pattern-Suche |

---

## 5. Positionierung als Shared Tool

```
tools/
  web/                  ← Web-Infrastruktur (SearXNG, PageFetcher)
    search.py
    fetch.py
  dateien/              ← Datei-Infrastruktur (NEU)
    __init__.py
    operationen.py      ← Alle Funktionen aus Abschnitt 3
```

Konsumenten:

| Konsument | Nutzung |
|-----------|---------|
| RechercheAgent (Pixie) | Wissen-/Bericht-Dateien schreiben und erweitern |
| VertiefungsAgent (Pixie) | Bestehende Wissen-Dateien lesen und ergaenzen |
| Traum-Modus (Pixie) | Assoziativ verknuepfen, konsolidieren |
| DateienAgent (User) | CRUD fuer User-Dateien (zukuenftig) |
| ProjektAgent (User) | Ordner + Meta-Dateien (zukuenftig) |

> **Architektur-Entscheidung:** Datei-Operationen sind allgemeine Tools (`tools/dateien/`), keine Pixie-Infrastruktur. Identisches Prinzip wie bei Web-Tools (Chat 34).

---

## 6. Konfiguration

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `DATEI_BLOCK_LIMIT` | `200` | Max Zeilen pro Lesevorgang |
| `DATEI_MAX_VOLLSTAENDIG` | `2000` | Max Zeichen fuer `datei_lesen` |

---

## 7. Referenzen und Quellen

| Quelle | Relevanz | Fundort |
|--------|----------|---------|
| **SWE-agent** (Princeton/Stanford, NeurIPS 2024) | `str_replace_editor` mit `view_range`, empirisch validiert | github.com/SWE-agent/SWE-agent |
| **Claude Code** (Leak 2026-03-31) | `FileEditTool`, `FileReadTool`, 40+ Agent-Tools | github.com/Piebald-AI/claude-code-system-prompts |
| **Aider** (Paul Gauthier) | 5 Edit-Formate, Leaderboard, Architect-Mode | aider.chat/docs/more/edit-formats.html |
| **OpenAI Codex CLI** | `apply_patch.py`, GPT-4.1 auf Patch-Format trainiert | Prompt Cookbook (April 2025) |
| **Fabian Hertwig** | Umfassender Vergleich aller Edit-Ansaetze | fabianhertwig.com/blog/coding-assistants-file-edits/ |
| **Letta/MemGPT** (UC Berkeley) | `core_memory_replace/append` — Paradigma "LLM verwaltet eigenes Gedaechtnis" | github.com/letta-ai/letta, docs.letta.com |

### Erkenntnisse aus den Quellen

- **SWE-agent:** "Das effektivste Edit-Tool ist str_replace. Bei Nicht-Eindeutigkeit: range-Parameter oder mehr Kontext."
- **Aider:** "whole ist einfach aber teuer, diff ist effizient aber fehleranfällig. Verschiedene LLMs brauchen verschiedene Formate."
- **SWE-agent Deep Dive:** "Nicht die menschliche Shell wiederverwenden. cat, sed, grep -rn sind schlechte Agent-Tools. Agent-gerechte Befehle mit begrenztem, strukturiertem Output bauen."
- **Augment Code:** "Fuer SWE-bench waren Embedding-Tools nicht der Engpass — grep und find reichten."
- **Novas fuenfter Weg:** Block-basierte Navigation mit Markdown-Headings als natuerliche Grenzen ist semantisch eindeutiger als Code-Zeilen. `str_replace_in_block` begrenzt den Suchraum auf einen Block und reduziert Eindeutigkeitsprobleme massiv.

---

Verwandte Dokumente:
- Autonomes Wissen: `novaberg-autonomous-wissen_k.md`
- Pixie-Plugin-Architektur: `novaberg-pixie-plugin_k.md`
- Web-Infrastruktur: `novaberg-tool-web.md`
