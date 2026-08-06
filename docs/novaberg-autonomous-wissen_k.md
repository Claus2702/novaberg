# Novaberg — Autonomes Wissen (Konzept)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Autonomes Wissensverzeichnis — Recherche, Vertiefung, Klaerfrage, Traeumen
**Stand:** 4. August 2026 (Erstfassung 29. April 2026, Chat 70)
**Pfad:** novaberg/docs/novaberg-autonomous-wissen_k.md
**Status:** ⬜ **nicht gebaut.** Die Erstfassung ist drei Monate alt und wurde nie umgesetzt; §11 traegt die Ueberarbeitung auf den heutigen Stand.
**Quellen:** Chat 70 (autoresearch, Claude Code autoDream, SWE-agent, Letta, Sleep-time Compute Paper)
**Verwandt:** `novaberg-klaerung_k.md` (woher der Auftrag kommt) · `novaberg-gedankenkette_k.md` (wie er ueber mehrere Zuege traegt) · `novaberg-wissensluecken_k.md` (Themen-Neugier, ein anderer Gegenstand)

> **§11 ist gegenueber §1 bis §10 vorrangig.** Die frueheren Abschnitte beschreiben den Entwurf vom April; wo sie ihm widersprechen, gilt §11. Sie bleiben stehen, weil sie die Begruendungen tragen, die weiterhin gelten.

---

## 1. Aufgabe

RechercheAgent, VertiefungsAgent und Traum-Modus produzieren Wissen. Aktuell geht dieses Wissen auf den Shadow-Stack (Delivery, vergaenglich) und ins KZG (Decay, vergaenglich). Das erarbeitete Wissen verschwindet.

Das `autonomous/`-Verzeichnis ist Novas persistenter Wissensspeicher. Jeder Durchlauf erzeugt bis zu zwei Dateien: eine **Wissen-Datei** (das Was) und eine **Bericht-Datei** (das Wie). Beide sind ueber RAG (Embedding + pgvector) fuer den Enricher abrufbar.

> **Nachgetragen am 04.08.2026:** Es sind **drei** Quellen, nicht zwei — Recherche schoepft aus der Welt, Vertiefung aus dem eigenen Bestand, **die Klaerfrage aus dem Gegenueber**. Siehe §11.3. *(Der Modus hiess hier bis zum 05.08.2026 `nachfragen`; der Name war doppelt vergeben und ist getrennt — §11.3.)*

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

> **Gebaut am 04.08.2026 — in der Fassung von §11, nicht in dieser.** Der Entwurf unten bleibt als Herkunft stehen; wo er §11 widerspricht, gilt §11: `context_user`/`charakter` sind durch das Paar-Tripel ersetzt (§11.2), `salienz FLOAT DEFAULT 0.0` durch `salienz_anfang` ohne Vorgabewert (§11.4), und die drei Gewichtsspalten sind hinzugekommen (§11.6).
>
> **Zusätzlich widerlegt hat das der Bau selbst:** Der `ivfflat`-Index unten ist **nicht angelegt**. Bei kleinen Zeilenzahlen durchsucht `ivfflat` mit `probes=1` eine einzige Zentroid-Liste, und der Recall bricht auf nahezu null ein — belegt in Chat 107 an `lzg_knoten`, wo derselbe Index 0 Treffer lieferte, während der Seq-Scan 118 mit Kosinus 0,67–0,74 fand. Diese Tabelle startet bei null Zeilen. Der Index steht in `db/init.sql` als Kommentar samt Schwelle (~10k Einträge) an seiner Stelle; der Partial Index auf Paar und Typ ist angelegt.

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

---

## 11. Überarbeitung vom 4. August 2026

Die Erstfassung ist drei Monate alt und nie gebaut worden. In der Zwischenzeit hat sich die Umgebung an sechs Stellen so verändert, dass der Entwurf ohne Nacharbeit nicht mehr umsetzbar wäre. Dieser Abschnitt hält fest, was heute gilt.

### 11.1 Der Speicherort liegt außerhalb des Git-Roots

Der Speicher liegt **eine Ebene über dem Repositorium**, als Geschwister von dessen Wurzel:

```
<eltern>/
    novaberg/        ← das Repositorium
    knowledge/       ← der Wissensspeicher     (neu)
```

Im Behälter ist er unter `/knowledge` eingehängt, schreibbar.

**Das ist keine Ablage-Vorliebe, sondern eine Sicherung.** Die Dateien enthalten Recherchen, die aus Gesprächen abgeleitet sind. Läge das Verzeichnis unter `novaberg/`, veröffentlichte jeder Push die gesammelten Inhalte. Außerhalb des Arbeitsbaums kann `git add` sie nicht erfassen — die Grenze ist dann eine Eigenschaft des Dateisystems und keine Regel, an die sich jemand erinnern muss.

`novaberg-wissensluecken_k.md` §7 nennt dieselbe Bedingung; die Erstfassung dieses Dokuments nannte sie nicht.

**Die Rechte sind eine Bedingung an den Schreiber, keine an die Konfiguration.** Gemessen am 04.08.2026: Der Behälter läuft als `root`; auf dem Wirt erscheinen die erzeugten Dateien unter einer fremden Kennung mit Modus 644, und der Nutzer kann sie **nicht** bearbeiten. Ein Obsidian-Fenster darauf ist aber der halbe Zweck des Speichers.

Die Abhilfe liegt in der Anwendung, nicht im Benutzernamensraum:

| | |
|---|---|
| `umask` beim Schreiben | `000` |
| Dateien | `0666` |
| Verzeichnisse | `0777` |

**Gegenprobe gefahren:** Mit diesen Werten kann der Wirtsnutzer Dateien anhängen und im Verzeichnis neue anlegen, obwohl die Eigentümerkennung fremd bleibt. Ohne sie scheitert beides mit `Keine Berechtigung`.

Der Weg über den Benutzernamensraum — den Behälter unter der Wirtskennung laufen zu lassen — wurde verworfen: Er griffe in den laufenden Dienst ein, um ein Problem zu lösen, das drei Zeilen im Schreibpfad ebenfalls lösen. Und er wäre an die Eigenheiten der Behälterlaufzeit gebunden, die Modusbits sind es nicht.

**Gemessener Ist-Zustand (04.08.2026):** Der Server sieht heute genau zwei Mounts — `novaberg/server → /app` (rw) und `novaberg/db → /app/db` (ro). Ein Wissensverzeichnis ist ohne Compose-Änderung nicht erreichbar.

### 11.2 Das Paar-Schema ist zwingend

Die Tabelle in §7.2 trägt `context_user` und `charakter`. Verbindlich ist das Tripel:

| Spalte | Bedeutung |
|---|---|
| `user_id` | das Subjekt — für wen gearbeitet wurde |
| `character_id` | das Gegenüber |
| `beobachter` | wessen Perspektive der Inhalt trägt |

Dieselbe Partitionierung wie KZG, LZG-Knoten, `ziele` und `charakter_hash`. Ein Speicher ohne sie wäre der einzige Bestand, der die Paar-Trennung nicht mitmacht — und die Trennung ist der Grund, warum Novas Wissen über den einen nicht in ein Gespräch mit dem anderen fällt.

### 11.3 Die Klärfrage ist die dritte Quelle

> **Umbenannt am 05.08.2026.** Dieser Abschnitt hieß „Nachfragen ist die dritte Quelle" und beschrieb seine Rolle unter dem Aufgabennamen `nachfragen`. Der Name war bereits vergeben: `novaberg-pixie-nachfragen_k.md` (27.07.2026) beschreibt unter demselben Namen eine **andere** Rolle — Zuwendung statt Wissen —, und die ist an vier Stellen im Code verdrahtet. Entschieden ist, dass es **zwei Agenten** sind; die Abgrenzungstabelle steht in jenem Dokument §6. Was hier steht, gilt unverändert, aber für den Aufgabennamen **`klaerfrage`**.

~~Der Entwurf kennt `recherche`, `vertiefung` und `traum`. `nachfragen` kommt darin nicht vor — und es kommt in **keinem** Konzept vor.~~ **Widerlegt am 05.08.2026:** Der erste Halbsatz stimmt — der Entwurf kennt die drei. Der zweite ist falsch: `novaberg-pixie-nachfragen_k.md` beschreibt den Aufgabennamen seit dem 27.07.2026, acht Tage vor diesem Abschnitt. Er ist bei der Abfassung nicht gefunden worden, und genau daraus entstand der Widerspruch.

Was richtig bleibt, gilt für `klaerfrage`: Diese Quelle kommt im Entwurf nicht vor. Und der Aufgabenname `nachfragen` existiert seit Monaten als Routing-Ziel, ohne dass je beschrieben wurde, was der Agent tun soll; deshalb ist er nie gebaut worden, und deshalb liegen seine Aufträge unbearbeitet in der Queue.

**Der Bestand widerlegt zusätzlich die Annahme, `klaerfrage` könne die vorhandenen Aufträge übernehmen.** Die 62 `nachfragen`-Aufträge in `shadow_queue:{user_id}` tragen `emotion: freude` bzw. `begeisterung` und **keine Wissenslücke** — das Feld existiert im Auftragsformat nicht. Sie stammen aus dem emotionalen Auslöser und sind für diesen Modus kein Eingang. `klaerfrage` braucht einen eigenen Erzeuger.

> **Der Unterschied zwischen den drei ist die Quelle, nicht der Ablauf.**
>
> | Modus | füllt die Lücke aus |
> |---|---|
> | `recherche` | der **Welt** |
> | `vertiefung` | dem **eigenen Bestand** — *präzisiert am 06.08.2026: der eigene Bestand bestimmt, **wo** gegraben wird; das Material kommt wie bei der Recherche aus dem **Web**. Ein reiner Speicherleser könnte die Bibliothek nicht ergänzen, und der Enricher liest sie bereits.* |
> | `klaerfrage` | dem **Gegenüber** — weil nur er die Antwort hat |

Der Auftrag kommt aus `novaberg-klaerung_k.md`: Es gibt eine Lücke oder eine Abweichung, sie ist notwendig (Tor 1) und bedeutsam genug (Tor 2). Bei den ersten beiden Modi kann Nova die Antwort selbst beschaffen. Beim dritten nicht.

**Die Quelle ist nicht der einzige Unterschied — die Reichweite ist der zweite.** `recherche` und `vertiefung` schöpfen beide aus etwas, das Nova selbst erreichen kann, und sind trotzdem nicht dasselbe Werkzeug:

| | Themenkreis | Nähe zum Ausgangsthema |
|---|---|---|
| `recherche` | **flach und breit** — der Umkreis wird abgesteckt | weiter gefasst |
| `vertiefung` | **eng und tief** — eine Stelle wird ausgegraben | **höhere Embedding-Nähe** |

Daraus folgt für die Bibliothek: Ein Vertiefungsergebnis liegt seinem Ausgangsthema im Vektorraum **näher** als ein Rechercheergebnis — es trifft die vorhandene Wissen-Datei eher als eine neue. Das ist derselbe Vorgang wie das Verstärken in §11.5, nur mit anderem Anlass: Recherche legt an, Vertiefung verstärkt und ergänzt. Eine Schwelle, ab der ein Ergebnis als „dieselbe Datei" gilt, ist damit **nicht** für beide Modi dieselbe Frage — die Schwelle 0.60 ist an Gedächtnisknoten gemessen, nicht an Vertiefungsergebnissen. **Offen, und vor `vertiefung` zu messen.**

**Und hier feuert Stufe 4 ohne Turn.** Die Klärungsfrage hängt sonst an einer Nutzeräußerung, die gerade vorliegt. Bei der Klärfrage liegt keine vor — Nova eröffnet selbst. Das ist der Punkt, an dem sie von reagierend zu **absichtsvoll** wird: Ein Impuls ist heute ein Fund, der einen passenden Moment sucht; eine Klärfrage ist ein Anliegen, das eine Handlung erzeugt.

**Das Interesse entscheidet, ob sie eröffnet.** Dieselben Speichen wie in `novaberg-klaerung_k.md` §2.2: `lenkungsdrang` und `eigensinn` ziehen hin, `zurueckhaltung` und `gespraechsdistanz` davon weg. Bei hoher Distanz eröffnet sie nicht — und die stillen Stufen laufen trotzdem.

**Was dabei entsteht, ist Wissen wie bei den anderen:** was gefragt wurde, was zurückkam, was daraus folgt. Es fällt in dieselbe Bibliothek.

Eine Eröffnung ohne Anlass ist ein Eingriff. Die vorhandene Zustellung hat dafür Cooldown, Burst-Grenze und Verträglichkeitsprüfung und schweigt bei Stress ganz.

> **Entschieden am 04.08.2026: Keine der Sperren wird gebrochen — von keinem Modus.**
>
> **Für `klaerfrage`:** Das Fragen ist Stufe 4 der Klärung, und nur diese Stufe hängt am Charakter. Ein Anliegen, das die Zustellung nicht durchlässt, ist genau der Fall, für den die Stufen 1 bis 3 still, gratis und unbedingt sind — Nova merkt die Lücke, baut nicht darauf, überschreibt nichts, und sagt nichts. Wer das Anliegen die Sperre brechen ließe, hätte die vierte Stufe wieder unbedingt gemacht.
>
> **Für `traum`:** Die Frage stellt sich dort gar nicht. Der Traum ist **reines Hintergrundrauschen** mit niedriger Priorität; er stellt nichts zu, sondern füllt die Bibliothek. Was er findet, erreicht das Gespräch über den Enricher, wenn es passt — nicht über eine Unterbrechung. Ein Cooldown, den niemand berührt, muss nicht gebrochen werden.
>
> **Der gemeinsame Grund:** Die Sperren der Zustellung sind keine Bequemlichkeit, sondern die Zusicherung, dass Nova bei Stress schweigt. Eine Ausnahme „für Bedeutsames" hebt genau die Fälle auf, für die sie gebaut ist — denn unbedeutend ist ohnehin nichts, was bis zur Zustellung kommt.

### 11.4 Die auslösende Salienz ist die Salienz des Ergebnisses

`salienz FLOAT DEFAULT 0.0` in §7.2 ist genau das Muster, das der Standard verbietet: ein Vorgabewert, der aussieht wie ein Messwert.

Der Wert ist beim Schreiben immer bekannt — er hat den Vorgang ausgelöst. Also:

```sql
salienz_anfang  DOUBLE PRECISION NOT NULL,   -- kein DEFAULT
```

Ein Schreiber ohne Salienz scheitert laut, statt eine Null abzulegen. Dieselbe Bauart wie `F-ZIEL-1`.

**Belegt, dass die Gefahr real ist:** In der Shadow-Queue tragen am 04.08.2026 **49 von 650** Aufträgen Priorität `0.0` — obwohl sie das Hochsalienz-Tor passiert haben. Der Produzent reicht den Wert nicht durch. Auf dem Shadow-Stack ist es eine Stufe schlimmer: `stack_push()` nimmt Salienz gar nicht erst entgegen, das Feld existiert nicht.

### 11.5 Aufräumen wird Fortsetzen

Heute räumt `shadow_delivery.py` unmittelbar nach jeder Zustellung alle Stapel-Einträge ab, deren Embedding dem Gesagten mit Kosinus ≥ 0.60 nahe kommt. Das Log nennt sie `Duplikat`.

> **Die Behauptung dahinter ist falsch.** Kosinus ≥ 0.60 heißt „handelt vom selben Thema". Der Code liest das als „ist schon gesagt". Aus dem ersten folgt das zweite nicht — die gelöschten Einträge sind nicht Duplikate, sondern **der Rest des Themas**, und er war nie ausgesprochen.

An die Stelle tritt:

| | heute | künftig |
|---|---|---|
| Zweiter Gedanke zum Thema | gelöscht | **Verstärkung** des vorhandenen |
| Wiederholungsschutz | „ich habe etwas Ähnliches gesagt" | „das steht schon in der Datei" |
| Thema nach dem Sprechen | verbrannt | offen, mit vermerktem Fortschritt |

Die Entdopplung wird damit eine Eigenschaft des **Wissensstands** statt des Stapels: Was die Bibliothek zum Thema hergibt, gegen das, was noch fehlt — die Differenz ist die nächste Arbeit. Dieselbe Operation wie in `novaberg-klaerung_k.md`, hier auf den eigenen Bestand angewandt.

**Die Schwelle bleibt bei 0.60 — belegt, nicht übernommen.**

Der Wert stand schon im Löschpfad, aber „derselbe Schwellwert, umgekehrtes Vorzeichen" wäre kein Argument: Beim Löschen heißt hoch *vorsichtig*, beim Verstärken heißt hoch *untätig*. Die Zahl musste für die neue Richtung eigens gemessen werden.

**Gemessen am 04.08.2026** über alle Paare aus 1248 aktiven LZG-Knoten dreier Beziehungen — 639.652 Paare innerhalb einer Beziehung gegen 138.476 quer darüber:

| Schwelle | Paare innerhalb | Paare quer | quer absolut | Verhältnis |
|---|---|---|---|---|
| 0.55 | 8,31 % | 1,39 % | 1927 | 6 : 1 |
| **0.60** | **2,70 %** | **0,26 %** | **363** | **10 : 1** |
| 0.65 | 0,67 % | 0,05 % | 72 | 13 : 1 |
| 0.70 | 0,16 % | 0,01 % | 13 | 17 : 1 |

Bei 0.55 verfünffacht sich die Zahl der fremden Paare, bei 0.65 bricht die Ausbeute auf ein Viertel ein. **0.60 ist der Punkt, an dem Ausbeute und Trennschärfe zusammen am besten stehen.**

**Ein früherer Vorschlag von 0.50 ist damit widerlegt.** Er stammte aus 231 Paaren eines einzelnen Stapels in einem engen Themenfeld; diese Stichprobe unterschätzte das Rauschen erheblich — sie sah 0.494 als Obergrenze unverwandter Paare, tatsächlich reichen sie bis 0.793. Bei 0.50 hätten rund 6500 fremde Paare verstärkt statt 363, und ein verschmolzenes Thema ist nicht zurückzunehmen.

**Zur Einordnung:** Bei 0.82 gibt es in beiden Gruppen **null** Paare. Das ist keine Eigenschaft des Embedding-Raums, sondern `LZG_KNOTEN_MATCH_SCHWELLE` — alles, was so ähnlich war, wurde beim Anlegen bereits verschmolzen. Der Bestand ist an seiner eigenen Identitätsschwelle abgeschnitten.

**Das ist zugleich die Vorbedingung für `novaberg-gedankenkette_k.md`** — dessen §1 nennt genau diese Zeile als Blocker. Solange nach jedem Satz das Umfeld gelöscht wird, ist nichts da, woran eine Kette anknüpfen könnte.

### 11.6 Gewichtung, Sättigung und Verfall nach dem Knoten-Schema

**Zwei Speicher, eine Bauart, zwei Raten.** Das ist vorher zu trennen, sonst wird eine Kurve für beides entworfen und passt für keines:

| | `shadow_stack` (Redis) | `autonomous_wissen` (PostgreSQL) |
|---|---|---|
| Inhalt | ungesagte Gedanken | erarbeitetes Wissen |
| Natur | flüchtig | dauerhaft |
| Verfall | **eigene Rate**, 60 Tage | **die des LZG**, unverändert |

**Das erarbeitete Wissen ist Langzeitgedächtnis in Dateiform.** Es bekommt deshalb keinen eigenen Verfall, sondern `LZG_KNOTEN_DECAY_RATE` — **dieselbe Konstante, nicht nur derselbe Wert.** Wird der Gedächtnisverfall je nachkalibriert, soll das Wissen mitgehen; die beiden auseinanderlaufen zu lassen hieße, dass eine Erinnerung verblasst, während die Datei darüber unverändert oben steht.

Beim Stapel ist es umgekehrt: Er braucht eine **eigene** Konstante, weil ein ungesagter Gedanke schneller erledigt ist als ein recherchiertes Thema. Würde er die Knoten-Rate mitbenutzen, verschöbe eine Kalibrierung des Gedächtnisses unbemerkt den Gedankenhaushalt.

Der Rest dieses Abschnitts beschreibt die Kurve **des Stapels**. Für die Bibliothek gelten dieselben drei Stufen mit den Konstanten von `lzg_knoten`.

**Warum die Bibliothek nach PostgreSQL gehört, nicht in Redis — gemessen am 04.08.2026:** Ein Stapel-Eintrag ist im Mittel 11,9 KiB groß, davon 84 % Embedding als JSON-Text. 10.000 Einträge wären 116 MiB Arbeitsspeicher, 100.000 wären 1,1 GiB — Redis hält alles im RAM. `pgvector` legt denselben Vektor binär mit gut 3 KiB ab und durchsucht ihn über `ivfflat`.

Die Bauart ist die von `lzg_knoten`, in drei Stufen:

```
gewicht_roh      Anfangs-Salienz + Boost je Verstärkung      wächst linear
     ↓  cap · sin(min(roh/cap, 1) · π/2) ^ exp
gewicht_absolut  gedämpft, gesättigt bei cap                 Sättigung
     ↓  · e^(−λ · Tage seit verstaerkt_am)
gewicht_decay    der effektive Wert                          Zeit
     ↓  < min_gewicht
aktiv = FALSE    inaktiv, nicht gelöscht                     reaktivierbar
```

**Die Sinus-Kurve sättigt, statt zu kappen.** Der erste Gedanke zu einem Thema zählt viel, der fünfzigste kaum noch — ein Dauerthema wächst nicht unbegrenzt und hebelt den Verfall nicht aus.

**Die Startwerte, hergeleitet:**

| Größe | Wert | Herleitung |
|---|---|---|
| `cap` | 10.0 | wie `lzg_knoten` |
| `min_gewicht` | 0.1 | wie `lzg_knoten` |
| **Dämpfungs-Exponent** | **1.0** | flacher als die 0.5 der Knoten: ein einzelner Gedanke landet bei 1,56 statt 3,96, die Kurve ist in der unteren Hälfte fast linear |
| **Decay-Rate λ** | **0.0768 / Tag** | `ln(cap / min_gewicht) / 60` — ein gesättigtes Thema fällt nach **60 Tagen** inaktiv. Halbwertszeit 9,0 Tage |
| Reinforcement-Boost | 0.1 | wie `lzg_knoten` |

Zum Vergleich: Die Knoten laufen mit λ = 0.0015 und 462 Tagen Halbwertszeit. Ein Gedankenstapel ist kein Langzeitgedächtnis; die Rate ist hier 51-mal höher.

**Was sich daraus ergibt:**

| `gewicht_roh` | `absolut` (exp 1.0) | inaktiv nach |
|---|---|---|
| 0,5 | 0,78 | 26,8 Tagen |
| 1,0 | 1,56 | 35,8 Tagen |
| 3,0 | 4,54 | 49,7 Tagen |
| 5,0 | 7,07 | 55,5 Tagen |
| 10,0 | 10,00 | 60,0 Tagen |

Ein belangloser Gedanke ist nach knapp vier Wochen still verschwunden, ein bedeutsames Dauerthema hält zwei Monate ab der letzten Berührung. Niemand muss dafür sortieren.

> **Diese Zahlen sind Kalibrierung, keine Festlegung.** Sie sind hergeleitet, nicht gemessen — es gibt heute keinen Bestand, an dem sich die Füllrate beobachten ließe. Nach einigen Wochen Betrieb sind sie gegen die tatsächliche Verteilung zu prüfen. Wer sie später vorfindet, darf sie nicht für ein Messergebnis halten.

**Eigene Konstanten für den Stapel, die der Knoten für die Bibliothek.** Der Stapel bekommt getrennte Werte, sonst verschiebt eine Kalibrierung des Langzeitgedächtnisses unbemerkt den Gedankenhaushalt. Die Bibliothek benutzt `LZG_KNOTEN_DECAY_RATE` ausdrücklich mit — sie ist Langzeitgedächtnis in Dateiform und soll mitgehen, wenn dessen Verfall nachkalibriert wird.

**Die Spalten:**

```sql
salienz_anfang    DOUBLE PRECISION NOT NULL,   -- kein Default (§11.4)
gewicht_roh       DOUBLE PRECISION NOT NULL,
gewicht_absolut   DOUBLE PRECISION NOT NULL,
gewicht_decay     DOUBLE PRECISION NOT NULL,
haeufigkeit       INTEGER          NOT NULL DEFAULT 1,
verstaerkt_am     TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
decay_am          TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
aktiv             BOOLEAN          NOT NULL DEFAULT TRUE
```

**`gewicht_decay` wird materialisiert, nicht bei Abfrage gerechnet.** Ein Stapellauf schreibt Spalte und `decay_am`, die Lesepfade lesen die Spalte — wie bei `run_node_decay`. Das steht hier ausdrücklich, weil dieselbe Aussage an drei Stellen im Bestand falsch dokumentiert ist.

**Gebaut am 04.08.2026** in `db/init.sql`, mit drei Zusicherungen im Schema statt im Code: Das Paar-Tripel trägt — anders als `lzg_knoten` — **keinen Vorgabewert**, weil eine leere Tabelle sich den strengeren Weg leisten kann; `salienz_anfang` ebenfalls nicht; und `dateipfad` ist `UNIQUE`, damit Verstärken (§11.5) von Doppelt-Anlegen unterscheidbar bleibt. Die Zusicherungen sind live geprüft: Ein Schreibversuch ohne einen der vier Werte scheitert an der Datenbank, eine vollständige Zeile gelingt, eine zweite Zeile zum selben Pfad nicht.

**`WIS-3` gebaut am 04.08.2026** — der Schreibpfad am `recherche`-Agenten. Der Pfadwächter prüft zwei Bedingungen: innerhalb der Wurzel **und** außerhalb des Arbeitsbaums, jeweils am aufgelösten Pfad, damit kein `..` daran vorbeiführt. Das Anwendungsverzeichnis leitet er aus der Lage seines eigenen Moduls ab statt aus der Konfiguration — ein Wächter, den eine Umgebungsvariable verschieben kann, bewacht nichts.

> **Ein gescheiterter Durchlauf hinterlässt einen Bericht.** §5.1 sagt das, und der erste Messlauf hat gezeigt, warum es zählt: Eine Recherche scheiterte nach rund fünfzehn Minuten an der Zwischen-Destillation und kehrte zurück, bevor irgendetwas geschrieben war. Ohne den Bericht beginnt die nächste Lagebeurteilung bei null und sucht dasselbe noch einmal. Das Gate wird dabei **übergangen** — ein Modellaufruf über ein leeres Blatt wäre eine Frage ohne Gegenstand.

**Was damit noch nicht gebaut ist:** Die Kurve selbst. Die Spalten stehen, aber niemand schreibt sie — `gewicht_roh`, `gewicht_absolut` und `gewicht_decay` bekommen ihre Werte erst mit `WIS-3` (Schreibpfad) und `WIS-5` (Verfall). Eine vorhandene Spalte ist keine gerechnete Größe.

### 11.7 Wer den Verfall rechnet

`gewicht_decay` wird materialisiert (§11.6), also braucht es einen Lauf, der es tut. **Der Weg dafür existiert und ist erprobt** — es wird kein neuer Mechanismus gebaut.

**Gemessen am 04.08.2026:** Die periodischen Aufgaben liegen als Redis-Hashes unter `pixie:schedule:{name}` mit `interval`, `priority` und `next_run`. Der Tageslauf `synapsen_decay` (Intervall 86400 s, Priorität 0.2) steht mit **14 Läufen** im `hintergrund_log`, `ziel_decay` mit **16**, beide zuletzt am Vorabend. Keine der sechs periodischen Aufgaben war zum Messzeitpunkt überfällig.

> **Ein naheliegender Verdacht ist damit widerlegt.** Man könnte erwarten, dass die niedrig priorisierten Tagesläufe hinter der blockierenden Recherche verhungern — so wie es der Fund vom 27.07.2026 für den CharakterAgenten belegt. Sie tun es nicht. **Der Engpass des einen seriellen Platzes trifft, was oft laufen soll, nicht was selten laufen muss:** Ein Tagesintervall findet auch dann eine Lücke, wenn der Takt über Stunden übersprungen wird.

**Der Verfall wird ein dritter Schritt des vorhandenen Tageslaufs.** `synapsen_decay` tut heute schon zweierlei — Knoten-Decay und `pipeline_log`-TTL-Aufräumen. Ein dritter Schritt darin kostet **keinen zusätzlichen Platz im Heartbeat**, und das ist bei einem einzigen seriellen Platz das ausschlaggebende Argument: Jeder neue periodische Auftrag konkurriert mit den bestehenden um dieselbe Stelle.

Die Alternative — ein eigener Agent `gedanken_decay` — wäre sauberer getrennt und teurer im Takt. Sie bleibt die richtige Wahl, falls der Verfall später eine andere Frequenz braucht als der Knoten-Verfall.

**Der Preis der gewählten Variante ist benannt:** Ein Lauf, der drei Dinge tut, färbt bei einem Fehlschlag im dritten den ganzen Auftrag rot. Dagegen hilft, was die Norm ohnehin verlangt — **je Schritt ein eigener `hintergrund_log`-Eintrag** mit `gestartet` / `erledigt` / `fehler`, keine Sammelmeldung. Erst dann ist im Nachhinein unterscheidbar, ob der Verfall lief und nichts fand, oder ob er gar nicht lief.

### 11.8 Was offen bleibt

**Sind Priorität und Salienz zwei Größen oder eine?** Die Shadow-Queue schreibt `prioritaet`, der Dispatcher liest `salienz` — zwei Funde vom 27.07.2026 beschreiben das als Defekt. Bevor eine zweistufige Sortierung „erst Priorität, dann Bedeutung" in eine Tabellendefinition eingeht, muss feststehen, ob sich die beiden überhaupt unterscheiden. Sollen sie es: **Priorität = wie dringend, Salienz = wie bedeutsam.**

**Woran wird eine Verstärkung erkannt?** Vorschlag: an derselben Embedding-Nähe von 0.60, die heute löscht. Das ist eine Entscheidung, keine Ableitung.

~~**Darf ein bedeutsames Anliegen den Zustellungs-Cooldown brechen?**~~ **Entschieden am 04.08.2026: nein, von keinem Modus.** Begründung in §11.3.

**Braucht der Verfall später eine eigene Frequenz?** Dann wird aus dem dritten Schritt ein eigener Agent (§11.7).

**Braucht der Stapel zusätzlich eine harte Obergrenze?** Mit dem Verfall greift sie im Normalbetrieb nie. Als Netz gegen einen Fehler im Produzenten wäre sie trotzdem sinnvoll — die Größenordnung folgt aus §11.6, nicht aus einer runden Zahl.

---


---

## Versionshistorie

- **v0.5 — 05.08.2026:** §11.3 heißt **Die Klärfrage ist die dritte Quelle** — der Modus hieß hier `nachfragen`, und der Name war bereits vergeben. `novaberg-pixie-nachfragen_k.md` (27.07.2026) beschreibt unter demselben Namen eine andere Rolle, Zuwendung statt Wissen, verdrahtet an vier Stellen im Code. **Widerlegt** ist damit der Satz dieses Abschnitts, `nachfragen` komme „in keinem Konzept vor" — es kam in einem vor, acht Tage älteren, das bei der Abfassung nicht gefunden wurde. Entschieden ist die Trennung in **zwei Agenten**; die Abgrenzung steht in jenem Dokument §6, hier bleibt alles inhaltlich gültig unter dem Namen `klaerfrage`. Zusätzlich am Bestand belegt: Die 62 vorhandenen `nachfragen`-Aufträge tragen `freude`/`begeisterung` und keine Wissenslücke — dieser Modus kann sie nicht übernehmen und braucht einen eigenen Erzeuger, der auf `KLA-K1`/`KLA-K2` wartet.
- **v0.4 — 04.08.2026:** `WIS-3` gebaut, am `recherche`-Agenten. §11.3 um die **Reichweite** erweitert: Quelle ist nicht der einzige Unterschied zwischen `recherche` und `vertiefung` — Recherche steckt einen flachen, breiten Umkreis ab, Vertiefung gräbt an einer Stelle und liegt ihrem Ausgangsthema im Vektorraum **näher**. Daraus folgt, dass die Schwelle, ab der ein Ergebnis „dieselbe Datei" trifft, für die beiden Modi nicht dieselbe Frage ist; die 0.60 aus §11.5 ist an Gedächtnisknoten gemessen, nicht an Vertiefungsergebnissen. §11.6 hält fest, was der Bau ergänzt hat: Ein **gescheiterter Durchlauf hinterlässt einen Bericht**, und das Gate wird dabei übergangen.
- **v0.3 — 04.08.2026:** `WIS-2` gebaut. §7.2 trägt eine Marke: Die Tabelle steht in der Fassung von §11, und der dort genannte `ivfflat`-Index ist **nicht** angelegt — bei kleinen Zeilenzahlen bricht sein Recall auf nahezu null ein, belegt in Chat 107 an `lzg_knoten`. §11.6 hält fest, was gebaut ist und was nicht: Die Spalten stehen, die Kurve rechnet niemand, bis `WIS-3` und `WIS-5` da sind. Drei Zusicherungen liegen im Schema statt im Code — Paar-Tripel und `salienz_anfang` ohne Vorgabewert, `dateipfad UNIQUE` —, alle drei live geprüft.
- **v0.2 — 04.08.2026:** §11 ergänzt — die Überarbeitung auf den heutigen Stand, nachdem die Erstfassung drei Monate ungebaut lag. Sechs Punkte: der Speicherort liegt **außerhalb des Git-Roots** (die Erstfassung nannte die Repo-Grenze nicht, obwohl die Dateien aus Gesprächen abgeleitete Inhalte tragen); das **Paar-Schema** ersetzt `context_user`/`charakter`; **`nachfragen` ist die dritte Quelle** und bekommt hier zum ersten Mal überhaupt eine Aufgabenbeschreibung — es existierte seit Monaten als Routing-Ziel ohne Konzept, weshalb der Agent nie gebaut wurde; die auslösende **Salienz ohne Vorgabewert**; das **Aufräumen wird Fortsetzen**, weil Embedding-Nähe „vom selben Thema" heißt und nicht „schon gesagt" — mit der Schwelle 0.60 an **778.128 Paaren** aus 1248 LZG-Knoten belegt (Trefferverhältnis 10 : 1) und einem Zwischenvorschlag von 0.50 widerlegt, der aus einer zu kleinen Stichprobe stammte; und **Gewichtung, Sättigung und Verfall nach dem Knoten-Schema** mit hergeleiteten Startwerten (Dämpfungs-Exponent 1.0, λ = 0.0768 für 60 Tage); ; die Bibliothek erbt den Verfall des LZG **samt Konstante**, nur der Stapel bekommt eine eigene Rate; und **wer den Verfall rechnet** — ein dritter Schritt im vorhandenen Tageslauf `synapsen_decay` statt eines neuen Agenten, weil jeder periodische Auftrag um denselben einen seriellen Platz konkurriert. Dabei widerlegt: die Vermutung, niedrig priorisierte Tagesläufe verhungerten hinter der blockierenden Recherche — 14 und 16 Läufe im Audit-Protokoll belegen das Gegenteil. Die §§1–10 bleiben stehen und tragen ihre Begründungen; §11 hat Vorrang, wo sie widersprechen.
- **v0.1 — 29.04.2026:** Erstfassung. Verzeichnisstruktur, Wissen- und Bericht-Datei, Keep/Discard-Gate, agentische Iteration, Metadaten-Tabelle und Zwei-Stufen-Retrieval, Prune-Zyklus, Implementierungsreihenfolge.
