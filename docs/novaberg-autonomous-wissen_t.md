# Novaberg — Autonomes Wissen (Ausarbeitung)

**Teil 2 von 5 — Ausarbeitung.** Absicht und Kopfblock: [`novaberg-autonomous-wissen_k.md`](novaberg-autonomous-wissen_k.md) · Bauplan und Umstellung: [`novaberg-autonomous-wissen_b.md`](novaberg-autonomous-wissen_b.md) · Diskussion und Ergänzungen: [`novaberg-autonomous-wissen_e.md`](novaberg-autonomous-wissen_e.md) · Messungen: [`novaberg-autonomous-wissen_m.md`](novaberg-autonomous-wissen_m.md). Die Abschnittsnummern sind die des ungeteilten Konzepts; welche Datei einen Abschnitt trägt, sagt die Tabelle *„§ → Datei“* in `_k`.

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

~~Der Charakter ist das Verzeichnis, nicht der Dateiname. Flach innerhalb des Charakter-Ordners, sortierbar nach Datum.~~

→ **Am 22.08.2026 um eine Ebene erweitert: `autonomous/{charakter}/{context_user}/`** (`dateipfad_bauen` in `services/wissensspeicher.py`). Der Charakter bleibt Verzeichnis, der Nutzer wird eines. Das Präfix im Dateinamen bleibt und ist damit redundant — es hält eine Datei zuordenbar, die aus ihrem Verzeichnis herausgereicht wird.

> **Der Anlass ist ein Zugriff, den die flache Ablage nicht zuließ.** Der Speicher sollte dem Dateien-Index als Wurzel dienen, und eine Wurzel trägt `user_id × character_id` (`novaberg-agent-dateien_k.md` §2.2). Am Bestand gemessen lagen in `autonomous/nova/` **1097 Dateien über 17 Kennungen** — 1007 `meister`, dazu `falle` 41, `rasim` 12 und vierzehn weitere. Keine Teilmenge davon war ohne Namensvergleich adressierbar, und ein Verzeichnis ist der einzige Zuschnitt, den ein Index kennt.
>
> **Die Zuordnung stand vorher nur im Dateinamen — als Konvention, die kein Werkzeug erzwingt.** Sie war lesbar und nicht ansprechbar; genau das ist der Unterschied, den der Umzug beseitigt.
>
> **Der Umzug in Zahlen, 22.08.2026:** 1097 Dateien verschoben (1071 mit `git mv`, 26 noch nicht versionierte danach), 0 ohne erkennbare Kennung, 0 belegte Ziele. In der Datenbank 725 Zeilen `autonomous_wissen.dateipfad` nachgezogen; danach **0** Zeilen auf der alten Form, **0** Abweichungen zwischen Pfadverzeichnis und `user_id`, und **725 von 725** Zeilen zeigen auf eine existierende Datei.

### 2.3 INDEX.md — pro Paar

Inspiriert durch Claude Codes `MEMORY.md`: Ein Index, kein Dump. Pro Eintrag eine Zeile mit Verweis auf die Detail-Datei. Gepflegt durch den Prune-Zyklus (autoDream-Pattern).

> **Seit dem 22.08.2026 liegt er neben den Dateien, die er nennt** — also im Paarverzeichnis, nicht eine Ebene darüber. Ein Index je Charakter führte die Einträge aller Nutzer gemischt und konnte damit in keiner Wurzel liegen, ohne fremde Themen mit hineinzureichen. **Beim Aufteilen gemessen:** 391 Verweise, 391 übertragen, jedes Ziel vorhanden, 12 Paare mit eigenem Index (die übrigen fünf Kennungen tragen nur Berichte ohne Wissensdatei).

> `index_aktualisieren` leitet den Ort seither **aus dem Dateipfad ab** statt ihn erneut zusammenzusetzen — sonst können Datei und Index auseinanderlaufen, ohne dass etwas anschlägt.

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
| Shadow-Queue (DelegationsAgent) | Hohe Salienz, Effektivwert oder Emotions-Trigger | "Mehmet hat Finanzierungskrise" `[Herkunft geprüft 19.09.2026: keine realen Personen oder Angaben]` |
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
   Web-Suche (Serper, SearXNG als Rueckfall) → PageFetcher, iterativ, max 3 Runden

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

> **Nachtrag 18.08.2026 — der Tabelle fehlen drei von vier Suchkanälen.** Sie trägt allein `themen_embedding`. Der Stand der Technik lässt **lexikalisch, dense und Graph** nebeneinander laufen und verschmilzt über Ränge; `notizen` und `lzg_knoten` führen `suchtext` und `entitaet_ids` im selben System längst. Und der fehlende ist bei dieser Größe der **stärkere**: Lexikalische Suche ist bei kleinen Korpora relativ wertvoller, die Bibliothek trägt 234 Dateien. Vorgeschlagene DDL — vier Spalten, nullable, angekündigt: `entitaet_ids INTEGER[]`, `timeline_id INTEGER`, `stichwoerter TEXT[]`, `suchtext TSVECTOR`. Begründung und Quellen in `novaberg-agent-dateien_k.md` §4.1 und §6.

> **Nachtrag 18.08.2026 — der Zuschnitt der Wissen-Datei hat sich geändert.** `wissen_text_bauen` legt seit dem 18.08. jede neue Datei mit einem **adressierbaren Block** `## AKTUELL` und einer Zeile `**Version:** 1.0` an; bringt ein Destillat eigene `##`-Blöcke mit, rücken sie auf `###` und liegen damit innerhalb von AKTUELL. Der Anlass ist gemessen: **223 von 223** Wissensdateien trugen zuvor keine einzige `##`-Überschrift, während 461 von 462 übrigen Dateien welche hatten — damit hatte jedes blockweise arbeitende Werkzeug auf genau dem Bestand nichts zu adressieren, für den es gebaut ist. `## AKTUELL` bildet mit `## HISTORIE` ein Paar: Jeder sagt, was der andere ist, und der lebende Text bekommt dadurch eine Adresse. **Altbestände bleiben blocklos** und werden nicht rückwirkend umgeschrieben.

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

### 7.3a Der zweite Eingang — die Bibliothek ist bestellbar (19.08.2026)

**Gebaut, nicht geplant.** Bis zum 19.08.2026 war die Bibliothek über **einen** Eingang erreichbar: den Enricher. Sie floss bei jedem Turn bei, und niemand konnte sie **bestellen** — weder der Mensch (*„Was hast du selbst dazu erarbeitet?"*) noch sie selbst. Von den drei Rollen eines Silos (`novaberg-convention-nmcp.md` §6a) trug sie genau eine.

| Rolle | Wer entscheidet | Zustand |
|---|---|---|
| **Quelle** | niemand — sie fließt bei | `WissenManager.enrich_entries`, unverändert |
| **Zettel** | der Empfang, anhand der Äußerung | **neu:** `WissenManager.router_prompt` + `agents/wissen/` |
| **Werkzeug** | das Modell selbst | **offen** (`SILO-OHNE-WERKZEUG`) |

#### Eine Suche, zwei Tiefen

**Beide Eingänge gehen durch dieselbe Abfrage** — `AutonomousWissenRepository.suchen` (§6a.1). Zwei Abfragen über denselben Bestand ergäben zwei Rangfolgen, und die Abweichung fiele erst auf, wenn jemand dieselbe Frage zweimal stellt und zwei Antworten bekommt.

**Was der Eingang wählen darf, ist die Tiefe — nicht die Ordnung.** Schwelle, Typ und Sortierung sind für beide gleich; allein die Obergrenze unterscheidet sich (Quelle 3, Zettel 5). Der Grund für den Unterschied ist die Lage: Der Enricher-Weg drückt seine Treffer ungefragt in *jeden* Turn und muss sparsam sein; beim bestellten Weg hat der Mensch gefragt und wartet.

#### Der vierte Ausgang ist hier der eigentliche Zugewinn

**Die Quelle kann nur beitragen oder schweigen**, und Schweigen ist keine Antwort: *„dazu habe ich nichts"* und *„dazu habe ich nicht nachgesehen"* sehen im Gespräch gleich aus. Der Dienst trennt beides und legt die Zahl dazu — wie viele Ausarbeitungen durchsucht wurden und wie nah die knappste lag.

*Der `[gemessen]`-Kasten zum ersten Lauf des Dienstes (19.08.2026) steht in [`novaberg-autonomous-wissen_m.md`](novaberg-autonomous-wissen_m.md), Abschnitt „Aus §7.3a“.*

#### Die Tiefe bleibt Stufe 1, und der Dienst sagt es

Er liefert **Thema und Zusammenfassung, nicht den Wortlaut** der Ausarbeitung; Stufe 2 (§7.3) ist nicht gebaut. Das steht in seiner `grenze` und in jeder Auskunft, weil ein unbenannter Verzicht sich als Vollständigkeit liest — die gemessene Folge dieser Lücke steht in `novaberg-agent-dateien_k.md` §8.1a.

---

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

**Der Bestand widerlegt zusätzlich die Annahme, `klaerfrage` könne die vorhandenen Aufträge übernehmen.** Die 62 `nachfragen`-Aufträge in ~~`shadow_queue:{user_id}`~~ (heute Tabelle `shadow_auftrag`; am 15.08.2026 waren es 45) tragen `emotion: freude` bzw. `begeisterung` und **keine Wissenslücke** — das Feld existiert im Auftragsformat nicht. Sie stammen aus dem emotionalen Auslöser und sind für diesen Modus kein Eingang. `klaerfrage` braucht einen eigenen Erzeuger.

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

Eine Eröffnung ohne Anlass ist ein Eingriff. Die vorhandene Zustellung hat dafür Burst-Grenze und Verträglichkeitsprüfung und schweigt bei Stress ganz. (Der Cooldown stand hier bis zum 15.08.2026 mit; er ist mit dem Bau von Riegel 2 gefallen — `novaberg-eigenzeit_k.md` §2.5.)

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

> **Seit dem 15.08.2026 sind es drei Speicher, und der dritte hat ein eigenes Dokument.** Die **Shadow-Queue** übernimmt dieselbe Bauart mit einer dritten Rate: `novaberg-queue-verfall_k.md`. Sie kam hier nicht vor, weil dieser Abschnitt vom erarbeiteten Wissen aus gedacht ist, nicht von den Aufträgen. **Zwei Unterschiede sind beim Quervergleich wichtig**, damit niemand die Zahlen von hier dorthin trägt: Die Queue rechnet auf **Cap 1,0** statt 10,0, weil sie Salienz führt — auf der Skala dieses Abschnitts wäre ihre Schwelle 0,3 gleich 3 % und der Verfall liefe still ins Leere. Und sie zieht dafür **nach PostgreSQL** um, während der Stapel in Redis bleibt; der Grund ist die Lesefrequenz, gemessen, und er steht dort in §7.2.

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

*Was am 04.08.2026 dazu gebaut wurde — die Tabelle, der Schreibpfad `WIS-3`, der Bericht beim gescheiterten Durchlauf und was noch nicht gebaut ist —, steht in [`novaberg-autonomous-wissen_b.md`](novaberg-autonomous-wissen_b.md), Abschnitt „Aus §11.6“.*

### 11.7 Wer den Verfall rechnet

`gewicht_decay` wird materialisiert (§11.6), also braucht es einen Lauf, der es tut. **Der Weg dafür existiert und ist erprobt** — es wird kein neuer Mechanismus gebaut.

**Gemessen am 04.08.2026:** Die periodischen Aufgaben liegen als Redis-Hashes unter `pixie:schedule:{name}` mit `interval`, `priority` und `next_run`. Der Tageslauf `synapsen_decay` (Intervall 86400 s, Priorität 0.2) steht mit **14 Läufen** im `hintergrund_log`, `ziel_decay` mit **16**, beide zuletzt am Vorabend. Keine der sechs periodischen Aufgaben war zum Messzeitpunkt überfällig.

> **Ein naheliegender Verdacht ist damit widerlegt.** Man könnte erwarten, dass die niedrig priorisierten Tagesläufe hinter der blockierenden Recherche verhungern — so wie es der Fund vom 27.07.2026 für den CharakterAgenten belegt. Sie tun es nicht. **Der Engpass des einen seriellen Platzes trifft, was oft laufen soll, nicht was selten laufen muss:** Ein Tagesintervall findet auch dann eine Lücke, wenn der Takt über Stunden übersprungen wird.

**Der Verfall wird ein dritter Schritt des vorhandenen Tageslaufs.** `synapsen_decay` tut heute schon zweierlei — Knoten-Decay und `pipeline_log`-TTL-Aufräumen. Ein dritter Schritt darin kostet **keinen zusätzlichen Platz im Heartbeat**, und das ist bei einem einzigen seriellen Platz das ausschlaggebende Argument: Jeder neue periodische Auftrag konkurriert mit den bestehenden um dieselbe Stelle.

Die Alternative — ein eigener Agent `gedanken_decay` — wäre sauberer getrennt und teurer im Takt. Sie bleibt die richtige Wahl, falls der Verfall später eine andere Frequenz braucht als der Knoten-Verfall.

**Der Preis der gewählten Variante ist benannt:** Ein Lauf, der drei Dinge tut, färbt bei einem Fehlschlag im dritten den ganzen Auftrag rot. Dagegen hilft, was die Norm ohnehin verlangt — **je Schritt ein eigener `hintergrund_log`-Eintrag** mit `gestartet` / `erledigt` / `fehler`, keine Sammelmeldung. Erst dann ist im Nachhinein unterscheidbar, ob der Verfall lief und nichts fand, oder ob er gar nicht lief.

*§11.8 (Was offen bleibt) steht in [`novaberg-autonomous-wissen_e.md`](novaberg-autonomous-wissen_e.md), Abschnitt D.*
