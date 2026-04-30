# Novaberg — Autonomes Wissen (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Autonomes Wissensverzeichnis — Recherche, Vertiefung, Traeumen
**Stand:** 29. April 2026, Chat 70
**Pfad:** novaberg/docs/novaberg-autonomous-wissen_k.md
**Quellen:** Chat 70 (autoresearch, Claude Code autoDream, SWE-agent, Letta, Sleep-time Compute Paper)

---

## 1. Aufgabe

RechercheAgent, VertiefungsAgent und Traum-Modus produzieren Wissen. Aktuell geht dieses Wissen auf den Shadow-Stack (Delivery, vergaenglich) und ins KZG (Decay, vergaenglich). Das erarbeitete Wissen verschwindet.

Das `autonomous/`-Verzeichnis ist Novas persistenter Wissensspeicher. Jeder Durchlauf erzeugt bis zu zwei Dateien: eine **Wissen-Datei** (das Was) und eine **Bericht-Datei** (das Wie). Beide sind ueber RAG (Embedding + pgvector) fuer den Enricher abrufbar.

---

## 2. Verzeichnisstruktur

### 2.1 Zwei Bereiche, ein Obsidian-Vault

```
obsidian-vault/
  autonomous/          ← Novas Wissen (Pixie schreibt)
    nova/
      INDEX.md
      2026-04-29_meister_blockchain-grundlagen_wissen.md
      2026-04-29_meister_blockchain-grundlagen_bericht.md
      2026-05-01_nova_oekologie-co2_wissen.md
    leon/
      INDEX.md
    renate/
      INDEX.md
  user/                ← Users Dateien (DateienAgent schreibt)
    einkaufsliste.md
    projekt-gartenhaus.md
```

**Ein Unterverzeichnis pro Charakter.** Novas Wissen ist Novas Wissen, Leons Wissen ist Leons. Konsistent mit der Pair-Architektur: KZG-Keys `kzg:{user}:{char}:{id}`, LZG `character_id`-Spalte, Charakter-Hash pro `(user_id, character_id)`.

**Strikte Schreibgrenzen:** Pixie schreibt nur in `autonomous/`. DateienAgent schreibt nur in `user/`. Kein Cross-Write. Trust Boundary auf Dateisystem-Ebene.

**Obsidian ist passiv:** Ein Fenster auf die Dateien, kein Akteur. Nova schreibt Markdown, Obsidian zeigt es an. Der User kann stöbern, Novas Recherchen lesen — Transparenz, keine Black Box.

### 2.2 Namensschema

**`{datum}_{context_user}_{thema-slug}_{typ}.md`**

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `datum` | ISO-Datum der Erstellung | `2026-04-29` |
| `context_user` | Fuer wen recherchiert wurde | `meister`, `nova` (bei Traeumen) |
| `thema-slug` | Thema als URL-tauglicher Slug | `blockchain-grundlagen` |
| `typ` | Art der Datei | `wissen` oder `bericht` |

Der Charakter ist das Verzeichnis, nicht der Dateiname. Flach innerhalb des Charakter-Ordners, sortierbar nach Datum.

### 2.3 INDEX.md — pro Charakter

Inspiriert durch Claude Codes `MEMORY.md`: Ein Index, kein Dump. Pro Eintrag eine Zeile mit Verweis auf die Detail-Datei. Gepflegt durch den Prune-Zyklus (autoDream-Pattern).

```markdown
# Nova — Wissensindex

**Letzte Aktualisierung:** 15. Mai 2026
**Eintraege:** 12

- [Blockchain Grundlagen](2026-04-29_meister_blockchain-grundlagen_wissen.md) — Konsens, Smart Contracts, Skalierung (3 Durchlaeufe)
- [Oekologie CO2-Handel](2026-05-01_nova_oekologie-co2_wissen.md) — Zertifikate, EU-ETS (1 Durchlauf)
- [Zwiebelanbau](2026-05-03_meister_zwiebelanbau_wissen.md) — Sorten, Hochbeet, Schaedlinge (5 Durchlaeufe)
```

---

## 3. Wissen-Datei — das Was

Reines Destillat, kompakt, optimiert fuer RAG-Retrieval. Kein Prozess-Rauschen.

```markdown
# Blockchain — Grundlagen

**Erstellt:** 29. April 2026
**Letzte Ergaenzung:** 15. Mai 2026
**Recherchiert fuer:** Meister
**Durchlaeufe:** 3
**Modus:** Recherche + Vertiefung

---

## Konsens-Mechanismen
[Destillat Durchlauf 1, aktualisiert Durchlauf 3]

## Smart Contracts
[Destillat Durchlauf 1]

## Skalierungsloesungen
[Ergaenzt: 15. Mai 2026, Durchlauf 2]
```

**Lebendes Dokument:** Bei erneuter Recherche zum selben Thema wird die bestehende Wissen-Datei erweitert (neuer Block via `block_einfuegen`) oder aktualisiert (bestehender Block via `block_ersetzen`). Die Bericht-Datei wird immer neu angelegt (neues Datum).

---

## 4. Bericht-Datei — das Wie

Prozessdokumentation. Was hat Nova getan, wie hat sie gesucht, was hat funktioniert. Nuetzlich fuer:
- Pixie-Lagebeurteilungen ("Zu diesem Thema hab ich schon recherchiert")
- Neugier-System ("Welches Thema verdient erneute Vertiefung?")
- Lernen aus Fehlschlaegen ("Welche Suchstrategien funktionieren nicht?")

```markdown
# Bericht: Blockchain — Grundlagen

**Typ:** Recherche
**Datum:** 29. April 2026
**Dauer:** ~12 Minuten (3 Iterationen)
**Charakter:** Nova
**Recherchiert fuer:** Meister
**Ausloeser:** Session-Frage zu Krypto-Infrastruktur
**Status:** echte_tiefe

## Lagebeurteilung

Vorwissen: Nova wusste "Blockchain = dezentrale Datenbank".
Luecken: Konsens-Mechanismen, Smart Contracts, Skalierung.

## Suchverlauf

| # | Query | Treffer | Relevant | Neue Info |
|---|-------|---------|----------|-----------|
| 1 | "blockchain consensus mechanisms explained" | 4 | 3 | ja |
| 2 | "proof of stake vs proof of work comparison" | 3 | 2 | ja |
| 3 | "smart contract limitations security" | 2 | 1 | teilweise |

## Bewertung

Pruefung 1 (Fakten): bestanden
Pruefung 2 (Vollstaendigkeit): bestanden
Pruefung 3 (User-Mehrwert): bestanden

## Ergebnis-Klassifikation

**echte_tiefe** — Drei Luecken gefuellt.

## Notizen

Query 3 lieferte vor allem Security-Aspekte. Bei Vertiefung:
gezielter nach "smart contract design patterns" suchen.
```

---

## 5. Keep/Discard-Gate und Ergebnis-Klassifikation

### 5.1 Status-Typen

Inspiriert durch Karpathys autoresearch (`keep`/`discard`/`crash`):

| Status | Bedeutung | Wissen-Datei | Bericht-Datei |
|--------|-----------|-------------|---------------|
| `echte_tiefe` | Substanzieller Wissenszuwachs | Ja (neu oder erweitert) | Ja |
| `ergaenzung` | Kleiner Zuwachs, Randinformation | Ja (erweitert) | Ja |
| `wiederholung` | Kein neues Wissen, nur Bekanntes | Nein | Ja |
| `fehlschlag` | Suche ohne brauchbare Ergebnisse | Nein | Ja |

Bei `wiederholung` und `fehlschlag`: Kein nutzloses Wissen, aber der Bericht wird geschrieben. Pixie lernt auch aus Fehlschlaegen.

### 5.2 Gate-Implementierung

Neuer Schritt nach der Destillation, vor dem Stack-Push. Das Analyse-Modell (Qwen) bewertet:

```
Destillat:
[destillierter Text]

Novas Vorwissen zum Thema:
[aus Lagebeurteilung]

Frage: Enthaelt das Destillat substanzielle Information, die ueber
Novas Vorwissen hinausgeht?

Antwort als JSON:
{"status": "echte_tiefe|ergaenzung|wiederholung|fehlschlag",
 "begruendung": "..."}
```

---

## 6. Agentic Iteration — der vollstaendige Arbeitszyklus

### 6.1 Themenfindung

| Quelle | Wann | Beispiel |
|--------|------|---------|
| Shadow-Queue (DelegationsAgent) | Hohe Salienz, Effektivwert oder Emotions-Trigger | "Mehmet hat Finanzierungskrise" |
| Shadow-Queue (KZG-Agent) | information_teilen + Salienz >= 0.7, oder Verstaerkung >= 3 | "Blockchain wurde 3x erwaehnt" |
| User-Auftrag (Router) | User sagt "Recherchiere das fuer mich" | "Zwiebelanbau umfassend" |
| Neugier (Traum-Modus) | Queue leer, Resonanz-Feld-Scan, Serendipity | Assoziative Querverbindung |
| Bericht-Dateien | Traum-Modus scannt nach `ergaenzung`/`fehlschlag` | "Letzte Vertiefung war oberflaechlich" |

### 6.2 Pipeline

```
0. KONTEXT AUFBAUEN [Python, deterministisch]
   Session-Kontext + LZG-Treffer + KZG + Charakter-Hash
   + autonomous/{charakter}/ nach bestehendem Wissen scannen
   + Wenn Wissen-Datei existiert: struktur_analysieren,
     relevante Bloecke lesen → Vorwissen zusammenstellen

1. LAGEBEURTEILUNG [Qwen, Analyse]
   Was weiss Nova schon? Wo sind Luecken?
   Bei Vertiefung: Wo hat Nova nur Oberflaeche?

2. PLANUNG [Qwen, Analyse]
   Recherche-Ziel (1 Satz), 2-4 Queries, Erfolgskriterien

3. SUCHE + FETCH [Python, deterministisch]
   SearXNG → PageFetcher, iterativ, max 3 Runden

4. BEWERTUNG [Qwen, Analyse]
   3 Pruefungen (Fakten, Vollstaendigkeit, User-Mehrwert)
   + Pruefung 4 bei Vertiefung (Tiefe)
   Luecken noch offen? → Zurueck zu Schritt 2

5. DESTILLATION [Gemma4, Sprache]
   Fliesstext, Charakter-treu, nur das Neue

6. KEEP/DISCARD-GATE [Qwen, Analyse]
   Status: echte_tiefe | ergaenzung | wiederholung | fehlschlag
```

### 6.3 Speicherung nach dem Gate — Datei + Pipeline-Feedback

Das Destillat geht nicht nur in die Datei und auf den Stack. Es wird
**zurueck durch Novas eigene Pipeline geschickt** — emotional bewertet,
mit Salienz versehen, und nach den normalen Regeln ins KZG oder LZG
eingestellt. Die Dateien sind keine Ausnahme vom Gedaechtnissystem.

```
Keep/Discard-Gate → Status

Bei echte_tiefe / ergaenzung:
  │
  ├── 1. DATEI: Wissen-Datei schreiben/erweitern (tools/dateien/)
  │              Bericht-Datei schreiben (immer neu)
  │              INDEX.md aktualisieren
  │
  ├── 2. METADATEN: autonomous_wissen-Tabelle aktualisieren
  │                  (Themen, Zusammenfassung, Pfad, Salienz, Status)
  │
  ├── 3. STACK: Stack-Push (Delivery an User)
  │
  └── 4. PIPELINE-FEEDBACK: Destillat zurueck durch die Pipeline
         Der Trigger bestimmt, WESSEN Gedaechtnis und WESSEN Salienz:

         User-Auftrag oder User-Queue:
           → user_id: meister, beobachter: user
           → Salienz aus dem User-Turn / Queue-Eintrag
           → Geht in MEISTERS KZG/LZG
           (Der User hat danach gefragt — es ist ihm wichtig)

         Nova autonom oder Traum:
           → user_id: nova, beobachter: assistant
           → Novas eigene emotionale Bewertung
           → Geht in NOVAS KZG/LZG
           (Nova hat es selbst erforscht — ihr Charakter entscheidet)

         In beiden Faellen:
             Perzeption → EI-Calc → Salienz
                 │
                 ├── Salienz ≥ 0.7 → KZG 30 Tage + Promotion-Queue → LZG
                 │   LZG-Gewicht 0.80 → haelt ~3 Jahre (Decay-Rate 0.0015)
                 │   Bei Verstaerkung (erneute Vertiefung) → Gewicht steigt
                 │
                 ├── Salienz 0.3-0.7 → KZG mit kuerzerer TTL
                 │
                 └── Salienz < 0.3 → Nichts

         Die Datei in autonomous/nova/ ist in beiden Faellen dieselbe —
         die Bibliothek ist charakter-gebunden. Aber das Gedaechtnis
         ist getrennt: Meister erinnert sich an Zwiebelanbau (sein Auftrag),
         Nova erinnert sich an Oekologie (ihre Neugier).

Bei wiederholung / fehlschlag:
  ├── Bericht-Datei schreiben
  ├── Metadaten aktualisieren (Status: wiederholung/fehlschlag)
  └── Kein Stack-Push, kein Pipeline-Feedback
```

**Wer fragt, dem gehoert die Erinnerung.** Wenn der User einen Auftrag gibt,
geht das Ergebnis in sein Gedaechtnis mit seiner Salienz. Wenn Nova autonom
forscht, geht es in ihr Gedaechtnis mit ihrer emotionalen Bewertung. Die Datei
auf der Festplatte bleibt in beiden Faellen dieselbe — ein Buch im Regal, das
beiden gehoert, aber unterschiedlich erinnert wird.

### 6.4 Auftragsmodus — Mehrstufige Recherche

Wenn der User sagt "Recherchiere Zwiebelanbau umfassend", laeuft nicht ein Durchlauf, sondern mehrere hintereinander:

```
Durchlauf 1: Ueberblick (Sorten, Zeitplanung, Grundlagen)
  → Stack-Push: "Erster Ueberblick steht. Ich mache weiter."

Durchlauf 2: Vertiefung (Hochbeet-Bau, Bodenqualitaet)
  → Wissen-Datei waechst um Bloecke

Durchlauf 3: Vertiefung (Schaedlinge, Begleitpflanzen)

Durchlauf 4: Vertiefung (Ernte, Lagerung)

Durchlauf 5: Konsolidierung (Redundanzen, Querverweise)
  → Stack-Push: "Recherche abgeschlossen. 15 Seiten in Obsidian."
```

Das Ergebnis: Ein wachsendes Dokument, das die Qualitaet eines Essays oder Mini-Buchs erreicht — nicht weil "Buch schreiben" ein Feature ist, sondern weil iterative Wissens-Akkumulation in einer strukturierten Datei genau das produziert.

---

## 7. Bibliothek vs. Gedaechtnis — Zwei-Stufen-Retrieval

### 7.1 Die Unterscheidung

| | Bibliothek (Dateien) | Gedaechtnis (KZG/LZG) |
|---|---|---|
| **Was** | Rohmaterial, vollstaendige Destillate | Verdichtete Erinnerungen |
| **Wo** | Dateisystem (`autonomous/{charakter}/`) | Redis (KZG), PostgreSQL (LZG) |
| **Lifecycle** | Persistent, Soft-Delete moeglich | Decay (Ebbinghaus), Promotion |
| **Zugriff** | Mandelbrot-Navigation, Bloecke lesen | Embedding-Suche, Top-K |
| **Analogie** | Buch im Regal | Aktive Erinnerung |

Die Datei ist der **Speicher**. Das LZG ist das **Gedaechtnis**. Ein Buch im Regal
ist noch da, aber ob man sich aktiv daran erinnert, haengt davon ab, wie stark es
einen beruehrt hat.

### 7.2 Metadaten-Tabelle (PostgreSQL)

Nicht die Dateiinhalte werden in PostgreSQL gespeichert — sondern die **Metadaten**.
Der Enricher prueft zuerst die Metadaten (schnell, SQL), und greift nur bei
Themennaehe oder Zusammenfassungs-Treffer auf die Datei zu (langsam, Mandelbrot).

```sql
CREATE TABLE autonomous_wissen (
    id SERIAL PRIMARY KEY,
    dateipfad TEXT NOT NULL,
    thema TEXT NOT NULL,
    zusammenfassung TEXT NOT NULL,       -- Kurze Beschreibung des Inhalts
    themen_embedding VECTOR(768),       -- Embedding der Zusammenfassung
    typ TEXT NOT NULL,                   -- 'wissen' oder 'bericht'
    modus TEXT NOT NULL,                 -- 'recherche', 'vertiefung', 'traum'
    context_user TEXT NOT NULL,
    charakter TEXT NOT NULL DEFAULT 'nova',
    status TEXT,                         -- 'echte_tiefe', 'ergaenzung', etc.
    salienz FLOAT DEFAULT 0.0,          -- Emotionale Bewertung aus Pipeline
    haeufigkeit INT DEFAULT 1,          -- Wie oft zum Thema recherchiert
    aktiv BOOLEAN DEFAULT TRUE,         -- Soft-Delete (wie LZG)
    erstellt_am TIMESTAMPTZ DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_autonomous_themen_embedding
    ON autonomous_wissen USING ivfflat (themen_embedding vector_cosine_ops)
    WITH (lists = 20);

CREATE INDEX idx_autonomous_aktiv
    ON autonomous_wissen (charakter, aktiv)
    WHERE aktiv = TRUE;
```

**Kein Volltext-Inhalt in der DB.** Der Inhalt lebt in den Dateien. Die DB speichert:
Wo liegt die Datei, worum geht es (Zusammenfassung + Embedding), wie wichtig ist es
(Salienz), wie oft wurde es bearbeitet (Haeufigkeit), und ist es noch relevant (aktiv).

### 7.3 Zwei-Stufen-Retrieval im Enricher

```
Stufe 1: Metadaten-Check (schnell, SQL)
    SELECT dateipfad, thema, zusammenfassung, salienz
    FROM autonomous_wissen
    WHERE charakter = %s AND aktiv = TRUE
      AND themen_embedding <=> %s < 0.4    -- Cosine-Naehe
    ORDER BY themen_embedding <=> %s
    LIMIT 5

    → "Zu diesem Thema gibt es 2 Wissen-Dateien"
    → Zusammenfassungen reichen oft schon als Kontext

Stufe 2: Datei lesen (nur bei Bedarf, Mandelbrot)
    Wenn die Zusammenfassung nicht reicht und die Salienz hoch ist:
    → struktur_analysieren(dateipfad)
    → block_lesen(relevanter_block)
    → Detailliertes Wissen als Kontext fuer den Responder

    Trigger fuer Stufe 2:
    - User fragt explizit nach Details
    - Salienz >= 0.7 (Nova erinnert sich aktiv → tieferer Zugriff)
    - Vertiefungsauftrag zu diesem Thema
```

Das LZG steuert die Gewichtung: Wenn Nova im LZG einen aktiven Eintrag zu
"Blockchain" hat (hohes effektives Gewicht), dann werden Datei-Treffer zu
Blockchain hoeher priorisiert. **Das Gedaechtnis steuert, wie wichtig der
Bibliotheksinhalt genommen wird.**

### 7.4 Soft-Delete statt Loeschung

Dateien werden nie geloescht. Metadaten-Eintraege werden auf `aktiv = FALSE`
gesetzt wenn:
- Die Salienz unter einen Schwellwert faellt und keine Verstaerkung kommt
- Der Prune-Zyklus feststellt, dass das Thema nicht mehr relevant ist
- Der User explizit sagt "Das Thema interessiert mich nicht mehr"

Inaktive Eintraege sind fuer den Enricher unsichtbar (Partial Index auf
`aktiv = TRUE`). Aber die Dateien bleiben auf der Festplatte — durchsuchbar
via `datei_suchen()` und `datei_grep()`, wenn Nova gezielt danach sucht.

Reaktivierung: Wenn Nova erneut zum Thema recherchiert oder der User
danach fragt, wird `aktiv = TRUE` gesetzt und die Salienz zurueckgesetzt.

### 7.5 Retrieval-Filter nach Konsument

| Konsument | Metadaten-Filter | Datei-Zugriff |
|-----------|-----------------|---------------|
| Enricher (Chat) | `typ=wissen`, `aktiv=TRUE`, Themennaehe | Stufe 2 nur bei hoher Salienz |
| Pixie-Lagebeurteilung | `typ=bericht`, Themennaehe | Immer (braucht das Wie) |
| Traum-Modus | `status IN (ergaenzung, fehlschlag)` | Ja (sucht Vertiefungskandidaten) |
| GV4-Wissensluecken | `typ=wissen`, Embedding-Nachbarschaft | Nein (Zusammenfassung reicht) |

---

## 8. Prune-Zyklus (autoDream-Pattern)

Periodisch (z.B. naechtlich) konsolidiert Pixie die INDEX.md und prueft Wissen-Dateien:

1. **Orient:** `INDEX.md` lesen, Verzeichnis scannen
2. **Gather:** Bericht-Dateien scannen — welche Themen hatten `wiederholung`? Welche Wissen-Dateien haben Widersprueche?
3. **Consolidate:** Redundanzen in Wissen-Dateien mergen, veraltete Fakten aktualisieren
4. **Prune:** INDEX.md aktualisieren, unter Zeilengrenze halten

Referenz: Claude Codes autoDream haelt MEMORY.md unter 200 Zeilen. "It's an index, not a dump — link to memory files with one-line descriptions." (Quelle: github.com/Piebald-AI/claude-code-system-prompts, agent-prompt-dream-memory-consolidation.md)

Theoretische Grundlage: "Sleep-time Compute" Paper (UC Berkeley / Letta-Team, arXiv:2504.13171). Modelle die in Leerlaufzeiten vorberechnen brauchen bei gleicher Genauigkeit 5x weniger Test-Time-Compute.

---

## 9. Implementierungsreihenfolge

| Phase | Umfang | Abhaengigkeit |
|-------|--------|-------------|
| **Phase 1** | `tools/dateien/operationen.py` | Keine |
| **Phase 2** | `autonomous_wissen`-Tabelle + Embedding-Funktionen | Phase 1 |
| **Phase 3** | RechercheAgent: Keep/Discard-Gate, Datei-Schreiben, Embedding | Phase 1+2 |
| **Phase 4** | VertiefungsAgent: Mandelbrot-Navigation, Block-Ergaenzung | Phase 1+2+3 |
| **Phase 5** | Traum-Modus: Assoziatives Verknuepfen, NEVER-STOP-Loop | Phase 1+2, Epic 8 |
| **Phase 6** | Enricher: Sechste RAG-Quelle | Phase 2 |
| **Phase 7** | Prune-Zyklus (INDEX.md, Konsolidierung) | Phase 3+ |
| **Phase 8** | Auftragsmodus (mehrstufige User-Auftraege) | Phase 3, Pixie-Plugin-Architektur |

---

## 10. Referenzen und Quellen

| Quelle | Relevanz | Fundort |
|--------|----------|---------|
| **autoresearch** (Karpathy, 2026) | Keep/Discard/Crash-Status, Experiment-Log, NEVER-STOP-Loop | github.com/karpathy/autoresearch |
| **Claude Code autoDream** | 4-Phasen-Zyklus (Orient/Gather/Consolidate/Prune), INDEX unter 200 Zeilen | github.com/Piebald-AI/claude-code-system-prompts |
| **Sleep-time Compute** (UC Berkeley / Letta) | Idle-Time-Vorberechnung spart 5x Test-Time-Compute, 18% Genauigkeitsgewinn | arXiv:2504.13171 |
| **Letta/MemGPT** | Paradigma "LLM verwaltet eigenes Gedaechtnis", Core/Archival Memory | github.com/letta-ai/letta |
| **dream-skill** (Community-Reimplementierung) | Open-Source-Nachbau von autoDream mit Stop-Hook | github.com/grandamenium/dream-skill |
| **Claude Code autoDream Guide** | Praxisbericht, 913 Sessions in 9 Minuten konsolidiert | claudefa.st/blog/guide/mechanics/auto-dream |
| **zenvanriel AutoDream Guide** | Detaillierte Analyse der 4 Phasen | zenvanriel.com/ai-engineer-blog/claude-code-autodream-memory-consolidation-guide/ |

---

Verwandte Dokumente:
- Datei-Operationen: `novaberg-tool-dateien_k.md`
- Pixie-Plugin-Architektur: `novaberg-pixie-plugin_k.md`
- RechercheAgent: `novaberg-pixie-research.md`
- VertiefungsAgent: `novaberg-pixie-deepdive_k.md`
- Neugier / Traum-Modus: `novaberg-thinking-curiosity_k.md`
- Drive-System: `novaberg-thinking-drive_k.md`
- Web-Infrastruktur: `novaberg-tool-web.md`
