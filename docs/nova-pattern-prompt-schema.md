# Nova — Pattern: Prompt-Schema [BLOCKNAME]

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Technik — Einheitliches Prompt-Schema für alle Nodes
**Stand:** 17. April 2026, Chat 52 (Code-Alignment)
**Pfad:** novaberg/docs/nova-pattern-prompt-schema.md
**Quellen:** nova-01-t-d.md
**Betrifft:** Alle Nodes mit LLM-Prompts (Perzeption, Router, Responder, Thinker, Tribunal, Salienz, Classify-Nodes)

---

## 1. Prinzip

> **Der Prompt darf Informationen haben. Er muss nur mitteilen, um was für Informationen es sich handelt.**

Ein LLM halluziniert nicht, weil es zu viel sieht, sondern weil es nicht versteht, was es sieht. Wenn verschiedene Informationsarten (Identität, Aufgabe, Kontext, Regeln) ohne Abgrenzung zusammenfließen, mischt das LLM sie. Die Lösung sind nicht Imperative ("Erfinde KEINE..."), sondern **Kontext-Beschreibungen**: Jeder Block wird eingeleitet mit einer Beschreibung seiner Rolle.

→ Lesson: nova-graph_l_kontextualisierung.md

---

## 2. Blockformat

Alle Nodes verwenden dasselbe Format:

```
[BLOCKNAME]
Beschreibung: Was dieser Block enthält und wie er zu verwenden ist.

{Inhalt}
```

**Regeln:**
- Blockname in eckigen Klammern, Großbuchstaben: `[IDENTITÄT]`
- Direkt nach dem Blocknamen: 1–2 Sätze Beschreibung (WAS ist das, WAS soll das LLM damit tun)
- Keine verschachtelten Formate innerhalb eines Blocks (keine `═══`, `---`, `***`)
- Thematisch zusammengehörige Informationen in einem Block
- Blöcke durch eine Leerzeile getrennt

---

## 3. Reihenfolge: Primacy → Recency

LLMs haben zwei starke Aufmerksamkeitszonen: **Anfang** (Primacy) und **Ende** (Recency). Die Mitte wird am schwächsten gewichtet ("Lost in the Middle").

```
OBEN — Primacy (Wer bin ich, was tue ich jetzt):
  [IDENTITÄT]        Wer das LLM ist, Datum, Rolle
                     (Responder seit Chat 45: inkl. nova_kern/adaptiv/intentionen/beziehung
                      — der frühere [CHARAKTER]-Block ist hier konsolidiert)
  [AUFGABE]          Was jetzt zu tun ist (bedingt)

MITTE — Kontext (stabile Hintergrundinformation):
  [KOMMUNIKATION]    Emotionaler Zustand, Stil, Modus (Responder)
  [GESPRAECHSVEKTOR] Landschaftsbeschreibung (Responder, seit Chat 39)
  [KONTEXT]/[AGENTEN]/[GEDAECHTNIS]/[WEB-RECHERCHE] (je nach Node)

UNTEN — Recency (letzte Einprägung vor der Generierung):
  [REGELN]           Verbote, Kürze, Prinzipien
  [DIREKTIVEN]       Absolute Verhaltensregeln vom Nutzer (Responder/Corrector/Tribunal-Jurist, seit Chat 40)
```

**Begründung der Reihenfolge:**
- IDENTITÄT oben: Das LLM muss zuerst wissen, *wer* es ist. Das prägt alles.
- AUFGABE oben: "Was tue ich jetzt" muss vor "Wie verhalte ich mich" kommen.
- CHARAKTER/KOMMUNIKATION in der Mitte: Stabile Informationen, die das LLM als Hintergrund hält.
- REGELN unten: Verbote und Formatregeln direkt vor der Generierung — Recency-Effekt maximiert Befolgung.
- DATENFORMAT ganz unten: Beschreibt das, was unmittelbar danach kommt (die Messages).

---

## 4. Block-Katalog

Nicht jeder Node hat alle Blöcke. Die Tabelle zeigt, welcher Node welche Blöcke nutzt:

| Block | Responder | Perzeption | Router | Salienz | Thinker | Tribunal | Classify |
|-------|-----------|------------|--------|---------|---------|----------|----------|
| IDENTITÄT | ✅ (inkl. Nova-Profile seit Chat 45) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| AUFGABE | ✅ (bedingt) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CHARAKTER | entfallen (Chat 45, in IDENTITÄT konsolidiert) | — | — | — | — | — | — |
| KOMMUNIKATION | ✅ | — | — | — | — | — | — |
| GESPRAECHSVEKTOR | ✅ (seit Chat 39) | — | — | — | — | — | — |
| KONTEXT | ✅ (bedingt) | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| AGENTEN | — | — | ✅ (Plugin-Additions) | — | — | — | — |
| GEDAECHTNIS / WEB-RECHERCHE | ✅ (bei Nicht-Agent-Erfolg) | — | — | — | — | — | — |
| REGELN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DIREKTIVEN | ✅ (seit Chat 40) | — | — | — | — | ✅ (nur Jurist) | — |
| DATENFORMAT | entfallen (Chat 30) | — | — | — | — | — | — |

**Erläuterung:**
- CHARAKTER und KOMMUNIKATION sind Responder-spezifisch (nur er formt die Persönlichkeit)
- AUFGABE ist bei allen Nodes vorhanden — enthält die JSON-Struktur/Feld-Definitionen (Perzeption, Router, Salienz, Classify) oder die Prüfungsschritte (Thinker, Tribunal)
- KONTEXT enthält Session-Turns (Perzeption, Router, Classify), Gedächtnis/Web (Responder, Thinker) oder Anmerkungen (Tribunal). Bei Salienz nicht im System-Prompt, sondern in der User-Message ([LAGEBILD]/[BEWERTUNGSOBJEKT])
- DATENFORMAT existiert nicht mehr beim Responder (seit Chat 30). Der [GESPRAECHSVERLAUF]-Block in der User-Message beschreibt sich selbst. Session-Turns werden als Textblock mit Turn-Headern gesendet, nicht als separate JSON-Messages

> **Hinweis (Chat 36):** Die Tabelle wurde geprüft — AUFGABE-Spalte für Perzeption und Router ist korrekt. Beide Nodes haben einen [AUFGABE]-Block der das JSON-Antwortformat definiert.

---

## 5. Node-spezifische AUFGABE-Blöcke

### Responder

Drei Varianten, nur eine erscheint:

**Agent-Erfolg:**
```
[AUFGABE]
Der Benutzer hat eine Anweisung gegeben. Die zustaendige Fachabteilung hat
folgende Operation ausgefuehrt:

{ergebnis_text}

Gib dem Benutzer eine Rueckmeldung zu seiner Anweisung und dem Ergebnis.
Dein Stil und deine emotionale Reaktion bestimmst du selbst.
```

**Pflicht-Rückfrage:**
```
[AUFGABE]
Ein Agent benoetigt eine Rueckmeldung vom Benutzer. Stelle die folgende
Frage — formuliere sie in deinem Stil, veraendere den Inhalt nicht:

{rueckfrage_text}
```

**Normaler Chat:** Block AUFGABE entfällt.

### Perzeption

```
[AUFGABE]
Analysiere den folgenden Prompt und liefere ein JSON-Objekt
mit drei Ebenen: rational, emotional, psychologisch.

Antwortformat:
{
    "rational": {
        "intent": "smalltalk|knowledge|personal|task|creative|meta",
        "tone": "empathisch|sachlich|kreativ|direkt",
        "thema": "Kurzbeschreibung des Themas in 2-5 Worten"
    },
    "emotional": {
        "emotion": "begeisterung|...|neutral",
        "arousal": 0.0-1.0
    },
    "psychologisch": {
        "modus": "fachgespraech|...|berichtend",
        "sprach_stil": "locker|formell|fachlich|emotional|jugendlich|neutral",
        "beziehungs_dynamik": "vertrauen|distanz|angriff|hilfesuchend|dankbar|neutral"
    }
}

Rationale Ebene — intent: smalltalk, knowledge, personal, task, creative, meta
Emotionale Ebene — emotion: 16+1 Kategorien, genau EINE waehlen
Emotionale Ebene — arousal: 0.0-1.0 Energie-Intensitaet
Psychologische Ebene: modus, sprach_stil, beziehungs_dynamik
```

### Router

```
[AUFGABE]
Entscheide anhand des Prompts und der Analyse, welche Ressourcen
benoetigt werden. Liefere ein JSON-Objekt:

{
    "needs_memory": true/false,
    "needs_web": true/false,
    "needs_timeline": true/false,
    "timeline_query": null | {
        "type": "range|search",
        "from": "YYYY-MM-DD HH:MM" | null,
        "to": "YYYY-MM-DD HH:MM" | null,
        "keyword": "Suchbegriff" | null,
        "direction": "forward|backward|both" | null,
        "limit": 1-10 | null,
        "date": "YYYY-MM-DD" | null,
        "title": "Beschreibung" | null
    },
    "momentum": "low|mid|high",
    "management_action": "",
    "management_target": "",
    "management_target_typ": ""
}

Feld-Regeln: needs_memory (personal/emotional), needs_web (aktuelle Fakten),
needs_timeline (zeitgebundene Information — Satzform irrelevant)
Timeline-Query: range (Zeitraum) oder search (Keyword)
Momentum: low (Abschluss), mid (normal), high (Engagement)
```

**Hinweis:** Der Router liefert kein `agent_name`-Feld. Agenten-Delegation geschieht über den `[AGENTEN]`-Block (Plugin-Prompt-Additions, seit Chat 26) und den Pending-Resume-Mechanismus. Der Router erkennt lediglich `management_action` + `management_target` — die Zuordnung zum konkreten Agenten macht der Planner.

### Thinker

```
[AUFGABE]
Pruefe die folgende Antwort auf faktische Korrektheit.
Wenn du Fehler findest, korrigiere sie. Wenn alles stimmt, bestaetigen.
```

### Tribunal (pro Perspektive)

```
[AUFGABE]
Bewerte die folgende Antwort aus der Perspektive eines {perspektive}.
Antworte mit: ok, warnung, oder ablehnung. Begruende kurz.
```

### Classify-Node

```
[AUFGABE]
Analysiere den folgenden Prompt und bestimme die Aktion.
{klassifikations_regeln}
```

---

## 6. Implementierungsstand

| Node | Status | Chat |
|------|--------|------|
| Responder | ✅ Fertig (Chat 27, DATENFORMAT entfallen Chat 30) | Chat 27/30 |
| Perzeption | ✅ Fertig | Chat 28 |
| Router | ✅ Fertig | Chat 28 |
| Salienz | ✅ Fertig (Dim 6+7+8 entfernt, kern → KZG-Agent) | Chat 29 |
| Thinker | ✅ Fertig | Chat 28 |
| Tribunal | ✅ Fertig (+ Template-Funktion, Duplikation reduziert) | Chat 28 |
| Classify-Nodes | ✅ Fertig (Notizen + Timeline) | Chat 28 |

Alle Nodes implementiert. Das Schema ist durchgängig.

---

## 7. Evolution des Prompt-Designs

```
Chat 1–22:   Flacher Prompt, alles in einem Block
Chat 23:     Kontext-Reduktion ("Weniger Input > stärkerer Prompt")
Chat 24:     Abgegrenzte Blöcke (═══ HINTERGRUND ═══)
Chat 25:     JSON-Transport für Session-Turns (PROMPT2-Fix)
Chat 26:     Kontext-Schutz im Classify-Node
Chat 27:     Strukturierte Kontextualisierung — einheitliches [BLOCKNAME]-Schema
             Primacy/Recency-Reihenfolge, Beschreibungen statt Imperative
Chat 28:     Rollout auf alle Nodes komplett. Umlaute→ASCII, {{→{, ═══ eliminiert.
             Salienz fokussiert (Dim 7+8 entfernt). Tribunal Template-Funktion.
Chat 29:     KZG-Agent übernimmt Session-Turn-Annotation + kern-Erzeugung.
             Salienz auf 8 Dimensionen fokussiert (reine Bewertung).
Chat 30:     [DATENFORMAT] beim Responder entfallen. Session-Turns als Textblock
             in User-Message ([GESPRAECHSVERLAUF]) statt separate JSON-Messages.
             Enricher reicht Turn-Dicts vollständig durch (nova-graph_l_datentransport.md).
Chat 39:     [GESPRAECHSVEKTOR]-Block im Responder (GV-Node liefert Landschaftsbeschreibung).
Chat 40:     [DIREKTIVEN]-Block in Responder/Corrector/Tribunal-Jurist (Arbeitsvertrag-Framing).
Chat 45:     RESP-CHAR1 — [CHARAKTER]-Block entfällt, Nova-Profile (kern/adaptiv/intentionen/
             beziehung) in [IDENTITÄT] konsolidiert. User-Hash über [GEDAECHTNIS].
Chat 46:     Prompt-Segregation — alle statischen Blöcke aus Python-Code in
             prompts/default/*.txt extrahiert. Connector-Overrides (gemma4) in
             prompts/gemma4/. PROMPTS-Dictionary in config.py. 0 hardcoded Prompts.
Chat 47:     Segregation-Rollout auf verbleibende Nodes (Responder, Thinker, Corrector,
             GV, KZG-Verdichtung, 4× Classify) — Corrector nutzt weiterhin ═══-Marker
             für [LAGEBILD]/[BEWERTUNGSOBJEKT], nur Direktiven-Block ist [BLOCKNAME].
```

Jede Stufe löste ein konkretes Problem und war Voraussetzung für die nächste.

---

→ Lesson Strukturierte Kontextualisierung: nova-graph_l_kontextualisierung.md
→ Responder-Modul: nova-node-responder.md
→ Node-Konfiguration: nova-backlog.md §3
→ Perzeption: nova-node-perception.md
→ Router: nova-node-router.md
→ Salienz: nova-pixie.md
