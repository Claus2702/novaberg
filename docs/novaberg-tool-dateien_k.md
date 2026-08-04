# Novaberg — Tool: Datei-Operationen (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Datei-Operationen — Intelligentes Lesen und Bearbeiten von Dateien
**Stand:** 29. April 2026, Chat 70
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
