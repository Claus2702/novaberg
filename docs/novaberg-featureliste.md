# Novaberg — Featureliste mit Ampel

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Vollständiges Register aller Features mit Zustandsampel und Beleg
**Stand:** 18. August 2026, ~19:30 UTC (Fortführung: **der Rückweg ins Wissen steht** — gemessen an zwei Läufen, einer ohne Schnitt und begründet. Zuvor ~18:40 UTC: **Stufe 4 ist vollständig** — der Aufrufer steht, und ein echter Turn nennt Fundstelle und Zahl im selben Satz. Zuvor ~17:30 UTC: Stufe 4 zur Hälfte, Stufe 3 **zweikanalig**, weil der Boden von vormittags am heterogenen Korpus fiel; eine Zeile neu für die Planner-Zuordnung)
**Pfad:** novaberg/docs/novaberg-featureliste.md
**Typ:** Register
**Quellen:** die 44 Konzeptdokumente, `novaberg-architecture.md`, die Moduldokumente, `novaberg-roadmap.md`, `novaberg-backlog.md`, `novaberg-bugs.md`, `novaberg-fundliste.md` — gehalten gegen Code und Produktivsystem

---

## Wie diese Liste zu lesen ist

| Ampel | Bedeutung | Woran sie gebunden ist |
|---|---|---|
| ⚫ | **nicht begonnen** | Die Zeile existiert, Code zu ihr nicht |
| 🟠 | **begonnen** | Code existiert und ist benennbar — das Ziel ist noch nicht belegt |
| 🟢 | **fertig** | `ZIEL` erreicht, `TEST` grün, `MESSUNG` gelaufen — **alle drei**, nicht zwei davon |
| 🔴 | **fehlerhaft** | Eine offene Kennung im Defektregister zeigt darauf · **oder** es ist gebaut und gemessen ohne Wirkung · **oder** es erzeugt etwas, das niemand liest |

> **Rot ist nicht ein dunkleres Orange.** Orange heißt *unfertig, und niemand hat sich geirrt*. Rot heißt *fertig geglaubt und im Betrieb falsch*. Wer beides in eine Farbe legt, verliert genau die Menge, die Vertrauen kostet — und das ist die einzige Menge, die man vor der nächsten Messung kennen muss.

**Jede Zeile trägt ihren Beleg**, und der Beleg trägt seine Herkunft:

- `[gemessen]` — eine Zahl aus dem Produktivsystem vom 17.08.2026
- `[Code]` — eine Stelle im Bestand, nachprüfbar mit einem Grep
- `[Doku]` — übernommen aus einem Konzept- oder Moduldokument, **nicht** gegen den Bestand gehalten

> **Eine Zeile mit `[Doku]` ist die schwächste Zeile dieser Liste.** Sie sagt, was jemand über den Zustand geschrieben hat, nicht was der Zustand ist. Drei solcher Zeilen sind bei dieser Erhebung als falsch aufgefallen (§14).

### Die Pflege läuft auf zwei Takten

**Fortführung — bei jeder Arbeit.** Wer ein Konzept schreibt, legt seine Featurezeilen an. Wer an einem Feature zu bauen beginnt, setzt die Ampel auf 🟠. Wer es abschließt, setzt sie auf 🟢. Wer einen Defekt mit Kennung dagegen aufnimmt, setzt sie auf 🔴.

**Neuerhebung — in Abständen.** Die Liste wird gegen den Bestand **neu gemessen**, nicht gegen ihre eigene letzte Fassung. Das ist ein eigener Auftrag und nicht Teil der Fortführung.

> **Beides widerspricht sich nicht, weil die Fortführung den Beleg mitbringt.** Wer eine Ampel setzt, hat ihn in der Hand — den Commit, die Bilanzzeile der Suite, den Messlauf. Eine fortgeführte Zeile ist deshalb **nicht** die schwache Sorte. Schwach werden die Zeilen, die niemand anfasst: Sie behalten ihre Ampel, während sich der Code darunter bewegt, und **genau die prüft die Neuerhebung**.
>
> **Der Anteil der `[Doku]`-Belege ist der Verfallsanzeiger dieser Liste.** Er wächst zwischen zwei Erhebungen und sagt, wann die nächste fällig ist — er ist die einzige Zahl hier, die man nicht bauen muss, um sie zu haben.

**Eine Ampel ohne Beleg gilt nicht als gesetzt.** Wer die Ampel ändert, ersetzt den Beleg mit; sonst steht am Ende eine Farbe, die niemand nachrechnen kann.

Die Feature-Matrix in `novaberg-architecture.md` §6 ist mit dieser Liste abgelöst — sie führte die Synapsen-Tabellen als „Schema angelegt, leer", während 2.390 Knoten und 365.088 Kanten darin stehen.

---

## 1. Die Graphen und die Pipeline

### 1.1 Die Graphen

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **HumanGraph** (Pfad 1 — der Mensch spricht) | 🟢 | `graph/human_graph.py`, 5 Knoten `[Code]` | — |
| **CharacterGraph** (Pfad 2 — die Figur antwortet) | 🟢 | `graph/character_graph.py`, 17 Knoten `[Code]` | — |
| **AgentGraph** (Pfad 3 — Hintergrundarbeit) | 🟢 | `graph/agent_graph.py` `[Code]` | — |
| **PixieGraph** (eigener Graph für Pixie statt AgentGraph) | ⚫ | `create_pixie_state` existiert nicht `[Code]` · `novaberg-pixie-graph-merge_k.md` Phase 0–3 | alles |
| **Kanalzwang im StateGraph** (jedes Feld deklariert) | 🟢 | 74 Zustandsfelder, **0 ohne Vorkommen außerhalb `state.py`** `[gemessen]` | — |
| **Event-Modell** (Consumer statt async-Block) | 🟢 | `services/event_consumer.py`, `services/events.py` `[Code]` | — |
| **Prompt-Eingangsqueue** vor Pfad 1 | 🟢 | `services/prompt_eingang.py`, `prompt_consumer.py` `[Code]` | — |
| **TurnOrchestrator** (Vision Chat 58) | ⚫ | kein Modul `[Code]` | alles |

### 1.2 Die zwanzig Knoten

| Knoten | Ampel | Beleg | Rest |
|---|---|---|---|
| `perzeption` — Emotion, Arousal, Intent, Dual-Modus | 🟢 | `[Code]` · `novaberg-node-perception.md` | schreibt **keinen** Pipeline-Eintrag |
| `db_zugriff` — CG-Eingang, Personality-Klassen | 🟢 | `[Code]` · Pipeline-Einträge vorhanden `[gemessen]` | — |
| `enricher` — Kontext aus vier Quellen | 🟠 | `[Code]` | Fakten-Enrichment **abgeschaltet** seit Chat 71 (`enricher.py:847`) |
| `ei_calc` — Verlauf, Vektor, Empathie | 🟢 | `[Code]` · `novaberg-node-ei-calc.md` | kein Pipeline-Eintrag |
| `emotionale_gravitation` — reaktivierte Erinnerung | 🟢 | `[Code]` · `novaberg-node-emotionale-gravitation.md` | kein Pipeline-Eintrag; `GRAVITATION-KLEMME-FEHLT` offen |
| `ei_calc_persist` — CG-Ausgang, Zustand schreiben | 🟢 | `[Code]` | — |
| `reducer` — Gegenspieler zum Enricher | 🟠 | Knoten verdrahtet in `character_graph.py:63` `[Code]` | `REDUCER_AKTIV` und `REDUCER_LOG_REMOVED` haben **keinen Leser** `[gemessen]`; strukturierter `memory_context` (Reducer-Umbau) offen |
| `router` — Routing und Delegation | 🟠 | `[Code]` · `novaberg-node-router.md` | kein Pipeline-Eintrag · `ROUTER-MISS-OHNE-ABSCHLUSS`, `ROUTE3` offen · Zweifel-Widerspruch im Prompt ungelöst |
| `planner` — Agentenschleife, Resume | 🟠 | `[Code]` · `novaberg-node-planner.md` | kein Pipeline-Eintrag · `PLANNER-AKTIV-RELIKT` |
| `agent_dispatch` — zentraler Eintritt | 🟢 | `[Code]` · Pipeline-Einträge `[gemessen]` | `DISPATCH-ABSCHLUSS-UNVOLLSTAENDIG` offen |
| `gespraechsvektor` — Landschaft, Strategie, Lücken | 🟢 | `[Code]` · `novaberg-node-gv_k.md` | siehe §5 |
| `haltung` — fünf Verhaltensgrößen | 🟢 | Knoten rechnet, protokolliert, persistiert `[Code]` | Wirkung siehe §5 |
| `verfasser` — der Inhalt vor der Form | 🟢 | `[Code]` · `novaberg-node-verfasser_k.md` **✅ gebaut** | läuft **nicht** auf dem Aufgabenpfad |
| `responder` — die Antwort | 🟢 | `[Code]` · `novaberg-node-responder.md` | kein Pipeline-Eintrag · `RESPONDER-LEERE-ANTWORT-STILL` Ursache offen |
| `thinker` — Faktenprüfung, Websuche | 🟠 | `[Code]` · `novaberg-node-thinker.md` | kein Pipeline-Eintrag — der Thinker ist **nicht beobachtbar** (`B−1` der Sykophanz-Reihe) |
| `thinker_cache` | 🟢 | `[Code]` | kein Pipeline-Eintrag |
| `tribunal` — drei Perspektiven | 🟢 | `[Code]` · `novaberg-node-tribunal.md` | kein Pipeline-Eintrag · `TRIB-PERSON-DRIFT` offen |
| `corrector` — Korrekturschleife | 🟢 | `[Code]` · `novaberg-node-corrector.md` | kein Pipeline-Eintrag |
| `salience` — Salienz als Entscheider | 🔴 | `[Code]`, läuft — aber **gesättigt**: 87 % der `user`- und 99 % der `assistant`-Einträge über 0,90 `[Doku, Fundliste 17.08.]` | rangiert nichts mehr; `KZG-SALIENZ-SKALENBRUCH`, `SALIENZ-JSON-BRICHT-AN-LATEX` offen |
| `dispatcher` — Schreiboperationen verteilen | 🟢 | `[Code]` · `novaberg-node-dispatcher.md` | — |

### 1.3 Querschnitt Pipeline

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Prompt-Schema `[BLOCKNAME]`** auf allen Knoten | 🟢 | `novaberg-pattern-prompt-schema.md` `[Doku]` | — |
| **Entscheidungs-Eintrag je Knoten** (jede Weiche dauerhaft belegt) | 🔴 | **9 von 20 Knoten** schreiben einen Pipeline-Eintrag `[gemessen]` | 11 Knoten ohne, darunter Router, Responder, Thinker, Planner, Perzeption |
| **Pipeline-Log** (Forensik, Spans, JSONB) | 🟢 | **87.913 Zeilen**, 10 Eintragsarten, täglich wachsend `[gemessen]` | `log_prompt`, `log_bemerkung`, `log_token` haben **keinen Aufrufer** `[gemessen]` |
| **Rückfrage-Kette** (Redis-Pending, Resume) | 🔴 | `[Code]` · `novaberg-graph.md` — **`ZUSTIMMUNG-GILT-ALS-ABLEHNUNG` offen seit 18.08.**: Die Ja/Nein-Deutung vergleicht Teilzeichenketten, `gerne` gilt als Nein `[gemessen]` | `RESUME-VERBRAUCHT-DEN-IMPULS` ✅ behoben 14.08. · die Deutung an Wortgrenzen, je Torwächter ein Zeuge |

---

## 2. Emotionale Wahrnehmung (EI)

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Plutchik-Oktagon** (9 Vektoren, Normalisierung) | 🟢 | `ei/berechnung.py`, `novaberg-ei-plutchik.md` `[Code]` | `PERZEPTION-EMOTION-AUSSER-KANON` offen |
| **EI-Plausibilitätsgate** (8 Sektoren) | 🟢 | `[Code]` · `novaberg-node-perception.md` | — |
| **Arousal-basierter Decay** | 🟠 | `[Code]` · `novaberg-ei-plutchik_l.md` | zählt **Turns statt Zeit** — die Gegenbewegung über eine Pause ist Bauteil A der Eigenzeit (§8) |
| **EI-MIKRO** (situative Mikro-Anweisungen) | 🟢 | `responder.py:_ei_mikro_anweisung` `[Code]` | — |
| **Dual-Emotion Phase 1** (User-IDs entkoppelt) | 🟢 | `[Doku]` Chat 57 | — |
| **Dual-Emotion Phase 2** (Nova-Empathie, Konflikt) | 🟠 | `[Code]`, AP1–7 und AP9 gebaut | AP8 Client-Teil `[Doku]` |
| **Dual-Emotion Phase 3** (Ziel-Vektor als dritte Kraft) | 🟠 | `ziele`: **259 Zeilen**, `ZielDecayAgent` läuft `[gemessen]` | `ziel_motivation_anpassen` hat **keinen Aufrufer** `[gemessen]`; der Antrieb wirkt nicht auf die Emotion |
| **Emotionale Gravitation** (Erinnerung zieht) | 🟢 | `ei/gravitation.py` `[Code]` | `EMOTIONALE_GRAVITATION_FAKTOR_SESSION` ohne Leser `[gemessen]` |
| **Wahrnehmungs-Gravitation** (Synapsen P10) | 🟠 | `wahrnehmung_verschieben()` gebaut, live gemessen `[Doku]` | **Wirkung ungemessen** — ob sich je eine Trefferliste ändert, ist offen |
| **Anker-Emotion** (Grundemotion je Charakter) | ⚫ | kein Code `[Code]` | alles |

---

## 3. Gedächtnis

### 3.1 Die Speicher

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Session-Gedächtnis** (Redis, Turn-Formatierung) | 🟠 | 2.893 Redis-Keys `[gemessen]` | Die Session **stirbt nicht** — jeder Impuls verlängert die Frist (Eigenzeit §2, Bauteil C) |
| **Kurzzeitgedächtnis KZG** (Redis + Vektor) | 🟢 | **2.803 `kzg:*`-Keys** `[gemessen]` · `novaberg-mem-kzg.md` | `KZG-SEGMENT-DUPLIKAT`, `KZG-VERDICHTER-KONTEXT-VERLUST` offen |
| **KZG-Magnetfelder** (`entitaet_ids`, `timeline_id`) | 🟢 | `[Code]` · Synapsen P3 | — |
| **Synapsen-Modell** (`lzg_knoten` + `lzg_kanten`) | 🟢 | **2.390 Knoten, 365.088 Kanten** `[gemessen]` | P1–P10 gebaut; Lesepfad-Umstellung `SYNAPSEN-DUAL-LZG` offen |
| **Langzeitgedächtnis alt** (`langzeitgedaechtnis`) | 🟢 | abgelöst und gelöscht (P9) `[gemessen]` — Tabelle existiert nicht mehr | — |
| **Ebbinghaus-Decay + Soft-Delete** | 🟢 | `SynapsenDecayAgent`, 40 Läufe im Log `[gemessen]` | `EBBINGHAUS_DECAY_RATE`, `EBBINGHAUS_MIN_GEWICHT` ohne Leser `[gemessen]` |
| **Halbreaktivierung** (§9.3) | 🟠 | `reactivate_node` gebaut `[Code]` | `HALBREAKTIVIERUNG-LIVE`, `SYNAPSEN-REAKTIV-SCHWELLE` — nie beobachtet |
| **Knowledge Graph — Entitäten** | 🟢 | **726 Entitäten**, 0 ohne Embedding `[gemessen]` | `ENTITAET-EMBED-DREIFACH` offen (einziges `TODO` im Code) |
| **Knowledge Graph — Fakten** (bi-temporal) | 🔴 | **0 Zeilen** `[gemessen]` — Enrichment seit Chat 71 abgeschaltet | `FAKTEN-RAUSCH`, `FAK1`, `D9`, `FAK-LECK` offen; ohne Fakten läuft der ganze Faktenpfad leer |
| **Entity Resolution** | 🟢 | `memory/services/entity_resolution.py` `[Code]` | — |
| **Verbindungstabelle** (Turn ↔ KZG ↔ LZG) | 🟢 | **7.073 Zeilen** `[gemessen]` | Pixie-Turns erzeugen **keine** Brückenzeile (`PIXIE-TURN-ID-LEER`) |
| **Gesprächsarchiv** (`gespraech_archiv`) | 🔴 | **0 Zeilen, kein Writer** `[gemessen]` · `GESPRAECH-ARCHIV-VERWAIST` | Tabelle existiert seit Chat 103 und ist nie gefüllt worden |
| **Chronik** (vollständiges Turn-Log) | ⚫ | Konzept im Backlog, kein Code `[Code]` | alles |

### 3.2 Promotion und Verdichtung

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Zwei-Call-Promotion** (KZG → LZG) | 🟢 | `SynapsenPromotionAgent`, **29.129 Audit-Einträge** `[gemessen]` | `PROMO-DROP1`, `PROMO-FAKT-LEER`, `PROMO-KZG-KEY-ALS-TURN-ID` offen |
| **KZG-Verdichter** | 🟠 | `[Code]` | `KZG-VERDICHTER-KONTEXT-VERLUST` — entkernte Inhalte |
| **Queue-Verfall** (Auftrag verliert seinen Anlass) | 🟢 | 1.036 Aufträge migriert, **6 Verfallsläufe** `[gemessen]` · `novaberg-queue-verfall_k.md` ✅ | Messung über 30 Tage Betrieb offen |
| **KZG-Salienz-Neubau** | 🟠 | Bauteil 1 gebaut und migriert `[Doku]` | **drei von sieben IDs offen**; die Skala ist gesättigt (§1.2) |
| **Assoziatives / aktenbasiertes Retrieval** | ⚫ | kein Code `[Code]` | alles |

---

## 4. Charakter

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Fünf Charakter-Profile + Hash** | 🟢 | **34 Zeilen** in `charakter_hash` `[gemessen]` · `novaberg-pixie-character-hash.md` | `CHAR-HASH-PAAR-VERTAUSCHT` offen — die Figur steht in der `user_id`-Spalte |
| **Sprachadaption (CAT)** | 🟢 | `novaberg-ei-language-adaptation.md` `[Doku]` | `SPRACH-STIL-DEFENSIV-STUMM` offen |
| **Charakter-Räder als Messreihe** | 🟢 | **142 Messungen** in `charakter_rad_messung` `[gemessen]` · beide Räder | `RAD-GESPEICHERT-NICHT-REPRODUZIERBAR`, `RAD-WERT-AUF-SPALTEN-DEFAULT` offen |
| **CharakterIdentitätsAgent** (Saatgut) | 🟢 | `[Code]` · 1 Zeile in `charakter_anweisungen` `[gemessen]` | `CRUD-REACTIVATE-STAMP`, `CHAR-ID4-ORPHAN` offen |
| **Charakter-Resonanz — Bauteil 1a/1b** (Brücke) | 🟢 | `verbindung` **7.073 Zeilen** `[gemessen]` | — |
| **Charakter-Resonanz — Bauteil 2** (Backfill) | ⚫ | optional, nicht gebaut `[Code]` | alles |
| **Charakter-Resonanz — Bauteil 3** (`verhaltensweisen` + Verdichter) | ⚫ | **Tabelle existiert nicht** `[gemessen]` | der ganze Bauteil; die Brücke füllt sich seit Wochen für einen Verbraucher, den es nicht gibt |
| **Charakter-Resonanz — Bauteil 4** (Lesepfad) | 🟠 | CharakterAgent liest `verbindung` `[Code]` — aber **anders als geplant** | liest Turn-Wortlaut statt destillierter Verhaltensweisen |
| **Charakter-Resonanz — Bauteil 5** (Doku) | ⚫ | — | nach 1–4 |
| **Charakterbildungs-Messreihe** (18 Bögen, 540 Turns) | 🟠 | aufgesetzt und zurückgesetzt `[Doku]` | wartet auf die GPU |
| **Profil-Historie** | ⚫ | `PROFIL-HISTORIE-FEHLT` `[Doku]` | alles |

---

## 5. Gesprächsvektor, Lage und Haltung

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **GV1 + GV2** (Farbmischung, Landschaft) | 🟢 | `graph/nodes/gespraechsvektor.py` `[Code]` | `GV-HYPOTHESE-ROHE-AUSGABE`, `GV-PANEL-STRATEGIE-DOPPELT` offen |
| **14 Gesprächslandschaften** | 🟢 | `novaberg-gv-strategie_k.md` `[Doku]` | — |
| **Erreichbarkeit der Landschaften** | 🟠 | alle vierzehn erreichbar gemessen `[Doku]` | **Ablesung fällt in 14 % aus** — kein Code für die Abhilfe |
| **Initiative-Achse** | 🟢 | `ei/initiative.py`, Schwelle gegen Zeugen kalibriert `[Code]` | `initiative_berechnen` in `ei/dreischicht.py` hat **keinen Produktivaufrufer** `[gemessen]` |
| **Kalibrierverfahren** (sechs Klassen, Korridor) | 🟠 | `ei/kalibrierung.py` + `agents/kalibrierung/` als Messwerkzeug `[Code]` | **kein Erwartungskorridor geschrieben, keine Validierungsmenge erhoben** |
| **GV4 — Wissenslücken im Prompt** | 🟢 | `ei/wissensluecken.py`, Lücken werden eingefügt `[Code]` | `WISSENSLUECKEN-FELDER-LEER` offen |
| **Wissenslücken-Speicher** | 🔴 | **785 Zeilen, ausnahmslos `offen`**, 78 in zwei Tagen neu `[gemessen]` | kein Verbraucher; `geschlossen`/`ausgeschlossen` sind Statuswerte **ohne Schreiber**; GV4 rechnet parallel und liest die Tabelle nie |
| **Haltungsraum — Rechnung, Knoten, Protokoll, Stand** | 🟢 | `ei/raum.py`, `graph/nodes/haltung.py`, `memory/haltung.py` `[Code]` | — |
| **Haltungsraum — Prompt-Block** | 🔴 | gebaut am 13.08. (`_sprachstil_block`) `[Code]`, aber **gemessen ohne Bindung**: Streuung 2,68 bei identischer Vorgabe `[Doku, Messung 17.08.]` | die Zahl regiert das Modell nicht; die Struktur, die binden würde, ist die Gedankenkette (§6) |
| **Haltungsraum — Ablösung der alten Längenregel** | 🟢 | die drei Längenzweige sind entfernt (`responder.py:60`) `[Code]` | — |
| **Zuwendungs-Riegel** (erster Leser des Standes) | 🟠 | Riegel 1 gebaut, Schwelle 0,25 `[Doku]` | Riegel 2 **nicht gerechnet** → die stündliche Decke steht |

---

## 6. Denken und Wissen

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Thinker** (Faktenprüfung + Websuche) | 🟠 | `[Code]` | **nicht beobachtbar** — kein Protokoll seiner Weiche |
| **Tribunal** (Drei-Perspektiven-Score) | 🟢 | `[Code]` · `novaberg-node-tribunal.md` | `TRIB-PERSON-DRIFT` offen |
| **Recherche** (SearXNG, Dual-Modell, Destillation) | 🟢 | **1.647 Bibliotheksläufe**, 538 in sieben Tagen `[gemessen]` | `RECHERCHE-OHNE-AUDIT`, `RECHERCHE-RELEVANZ-UNGEPRUEFT`, `RECHERCHE-LEER-GLEICH-AUSFALL`, `RECHERCHE-SALIENZ-KONSTANT` offen |
| **Wissensspeicher / Bibliothek** (`autonomous_wissen`) | 🟠 | **466 Zeilen**, seit 04.08. `[gemessen]` | **drei von vier Modi ohne Erzeuger** — nur `recherche` schreibt; `vertiefung`, `traum`, `nachfragen` sind deklariert und leer |
| **Vertiefung** (aus dem eigenen Bestand) | 🔴 | **171 aktive + 233 verfallene Aufträge** für einen Agenten, den es nicht gibt `[gemessen]` | der ganze Agent; jeder Auftrag verbrennt drei Versuche im Heartbeat-Takt |
| **Klärfrage** (aus dem Gegenüber) | 🟠 | `NachfragenAgent` gebaut `[Code]` | siehe §7 — 56 von 58 Läufen sind Fehler |
| **Traum-Modus** | ⚫ | keine der zehn `TRAUM_*`-Konstanten existiert `[gemessen]` | alles |
| **Erkenntniszyklus** (Nachdenken vor Nachschlagen) | ⚫ | kein Code `[Code]` · `novaberg-thinking-erkenntniszyklus_k.md` | ordnet die Bauteile oben — nicht gebaut |
| **Gedankenkette** (ein Gedanke über mehrere Turns) | ⚫ | kein Code `[Code]` · `novaberg-gedankenkette_k.md` | alles — und sie ist die Struktur, die dem Umfangsregler fehlt |
| **Klärung** (Abweichung und Lücke) | ⚫ | kein Code `[Code]` · `novaberg-klaerung_k.md` | alles |
| **Meinung / Willensstrang** | ⚫ | `novaberg-thinking-opinion_k.md`, Skelett `[Doku]` | die Haltungsseite von `einwand.quelle` hängt daran |
| **Neugier** (Resonanz, Neuheit, Register) | 🟢 | `ei/neugier.py` `[Code]` | `session_aktualitaet` ohne Aufrufer `[gemessen]`; Rückkopplung Lücken→Neugier nicht integriert |
| **Antrieb / Ziele** | 🟠 | **259 Ziele**, `ZielDecayAgent` läuft `[gemessen]` | `ZIELE-AUS-ZERRBILD` offen; keine Wirkung auf die Emotion (§2) |
| **Metakognition Phase 1** (Pipeline-Log) | 🟢 | 87.913 Zeilen `[gemessen]` | Entscheidungs-Eintrag fehlt in 11 Knoten |
| **Metakognition Phase 2** (`pipeline_search`) | ⚫ | Bezeichner existiert nicht `[gemessen]` | alles |
| **Metakognition Phase 3–6** (Vorsätze, Selbstreflexion) | ⚫ | keine Tabelle, kein Agent `[gemessen]` | alles |
| **Frames · Skills · Task-Orchestration · Cognitive Pipeline** | ⚫ | die Kernbezeichner fehlen sämtlich `[gemessen]` | vier Konzepte aus Chat 80/81, kein Code |
| **Referenz-Auflösung** (anaphorische Verweise) | ⚫ | `coreferee`, `HanTa`, `de_core_news_sm` **nicht installiert** `[gemessen]` | `REFERENZ-AUFLOESUNG-VOR-RETRIEVAL` offen |

### 6.1 Sykophanz-Eindämmung

| Bauteil | Ampel | Beleg | Rest |
|---|---|---|---|
| `B−1` Thinker protokolliert seine Weiche | ⚫ | kein Pipeline-Eintrag im Thinker `[gemessen]` | alles |
| `B0` Fallenbatterie (Nulllinie) | 🟢 | beide Hälften gefahren `[Doku]` | — |
| `B1` Urteilsfeld vor dem Text | 🔴 | `graph/einwand.py` gebaut `[Code]` — **gemessen 87 % → 87 %** `[Doku]` | wirkt nicht; `quelle="haltung"` ist ein Wert ohne Gegenstück |
| `B4` Vorzeichenprüfung Stufe 1 | 🔴 | gebaut, **85 % blind** `[Doku]` | Stufe 2 ist nicht die Verfeinerung, sondern der Mechanismus |
| `B2`, `B3`, `B5`, `B6`, `B7` | ⚫ | kein Code `[Code]` | alles |
| `B8` Schreibpfad (keine Destillation ohne Marke) | ⚫ | kein Code `[Code]` | alles |
| `B9` Register der Widersprüche | ⚫ | kein Code `[Code]` | alles |

---

## 7. Agenten

### 7.1 Die Anmeldung (NMCP)

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **NMCP-Handshake beim Start** | 🟢 | **15 von 15 Diensten eingebunden, 0 verweigert** `[gemessen, 18.08.]` | — |
| **Zuschnitt des Zustands auf die Anmeldung** | 🟢 | `agents/nmcp.py` `[Code]` | — |
| **Quotenabgleich** (angemeldet gegen gezählt) | 🟠 | Job im Scheduler, `NMCP_ABGLEICH_INTERVALL` `[Code]` | braucht 30–100 Äußerungen je Dienst — noch kein Urteil |
| **Vierter Ausgang** (`abgelehnt` = Zweifelsfall) | 🟠 | **5 von 15 Diensten** melden ihn an `[gemessen, 18.08.]` | für die zehn Hintergrunddienste ist der Grad „eingeschränkt" eine Aussage **ohne Wirkung** |
| **Selbstauskunft der Dienste** (`beschreibungen()`) | 🔴 | 15 Anmeldungen, **kein Produktivaufrufer** `[gemessen, 18.08.]` | `SELBSTAUSKUNFT-OHNE-LESER` |
| **Grenze** (`grenze`-Eigenschaft) | 🔴 | **5 Deklaranten, 0 Leser** `[gemessen]` | Ablageort entscheiden: Brett oder vierter Ausgang |
| **Audit-Pflicht** (`hintergrund_log`) | 🔴 | **6 von 15 Agenten** schreiben; über die gesamte Lebenszeit nur **7 Aufgabenarten** `[gemessen]` | acht Agenten ohne Eintrag, darunter drei periodische; fünf eigene Kopien von `_audit_log` |

### 7.2 Die Agenten des Menschen

| Agent | Ampel | Beleg | Rest |
|---|---|---|---|
| **NotizenAgent** (CRUD, pg_trgm) | 🟠 | 1 Zeile in `notizen` `[gemessen]` | sechs offene Bugs: Container-Wechsel, Kontext-Rekonstruktion, Skill-Manifest, leeres UPDATE-Ziel, Befehl als Titel |
| **TimelineAgent** (bi-temporal, ZeitVektor) | 🔴 | **61 Einträge** `[gemessen]` — aber der **Lesepfad ist instabil**: Nova verneinte einen aktiven Termin `[gemessen, 17.08.]` | eine ausgebliebene Zustellung ist von einer richtigen Auskunft nicht zu unterscheiden |
| **DirektivenAgent** (HITL-Gate) | 🟢 | **12 Direktiven** `[gemessen]` | teilt die Deutung aus `ZUSTIMMUNG-GILT-ALS-ABLEHNUNG` — **nicht nachgemessen** |
| **CharakterIdentitätsAgent** | 🟢 | siehe §4 | — |
| **KZG-Agent** (5-Knoten-Subgraph) | 🟢 | 2.803 Keys `[gemessen]` | `QUEUE-PUSH-OHNE-PRIORITAET` offen |
| **DelegationsAgent** (Halluzinationsventil) | 🟢 | **1.557 Akten / 2.068 Seiten** `[gemessen]` | `DELEG-SEITEN-VALENZ-TOT`, `DELEG-VEKTOR-EINGEFROREN` offen |

### 7.3 Die Agenten der Eigenzeit

| Agent | Ampel | Beleg | Rest |
|---|---|---|---|
| **RechercheAgent** | 🟢 | 538 Läufe in sieben Tagen `[gemessen]` | siehe §6 |
| **NachfragenAgent** | 🔴 | **58 Läufe, 2 erledigt, 56 Fehler**; letzter Lauf **12.08.**, während 45 Aufträge liegen `[gemessen]` | 53× „kein annotierter User-Turn mit Vektor", 3× Worker-/Loop-Fehler |
| **WiedervorlageAgent** (4-Tabellen-Scan) | 🟠 | Zeitplan live registriert `[gemessen]` | **kein einziger Audit-Eintrag** — ob er je gelaufen ist, ist nicht feststellbar |
| **CharakterAgent** (5-Profil-Destillation) | 🟠 | 34 Hash-Zeilen `[gemessen]` | kein Audit-Eintrag; Zombie-Schlüssel greift daneben (§14) |
| **SynapsenPromotionAgent** | 🟢 | 29.129 Audit-Einträge `[gemessen]` | — |
| **SynapsenDecayAgent** | 🟢 | 40 Läufe `[gemessen]` | — |
| **ZielDecayAgent** | 🟢 | 42 Läufe `[gemessen]` | — |
| **WissensluecketAgent** | 🔴 | 785 Zeilen, alle `offen` `[gemessen]` | kein Audit-Eintrag, kein Verbraucher |
| **VertiefungsAgent** | ⚫ | existiert nicht `[gemessen]` | 404 Aufträge warten |
| **Fachabteilungs-Agenten** (Fachspeicher bekommen Agenten) | ⚫ | `FACHSPEICHER-AGENTEN` `[Doku]` | alles |
| **PromotionAgent / DecayAgent (alt)** | 🟢 | abgelöst durch die Synapsen-Agenten `[Code]` | Router-Tabelle nennt sie noch (`promotion`, `decay`, `aufraeumen` — kein Agent dahinter) |

---

## 8. Pixie — die Eigenzeit

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Heartbeat, zwei Spuren** (LLM + CPU) | 🟢 | zwei Jobs im Scheduler `[Code]` | **ein serieller Platz** je Spur — der Engpass der Reihe 3 |
| **Shadow-Queue in PostgreSQL** | 🟢 | **958 Aufträge** `[gemessen]` | Rückstand: 530 aktive `recherche`, ältester vom 27.07. |
| **Promotions-Queue in Redis** | 🟢 | `[Code]` | `QUEUE-SCHEMA-STALE` offen |
| **Kandidatenwahl + Aging** | 🟢 | `services/pixie/kandidaten.py` `[Code]` | `DISPATCH-SALIENZ-DEFAULT`, `UNREGISTRIERTER-AGENT-GEWINNT` offen |
| **Stapel + Zustellung** (Shadow Delivery) | 🟢 | `services/shadow_delivery.py` `[Code]` | `SHADOW-STACK-THEMA-LEER`, `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` offen |
| **Zustellungsfilter** (0,60 Kosinus) | 🔴 | `_stack_aehnliche_entfernen` `[Code]` | löscht den nächsten Gedanken zum selben Thema mit — die Gedankenkette ist die Abhilfe, sie ist nicht gebaut |
| **Eigenzeit E** (Zeitstempel am Zustand) | 🟢 | `[Doku]` | — |
| **Eigenzeit F** (Session altert) | 🟢 | `[Doku]` | — |
| **Eigenzeit C** (Pausenfaktor) | 🟠 | gemessen: 48,7 h Pause → Faktor 0,0000 `[Doku, 17.08.]` | benannte offene Kante: der Fall ohne Bezug |
| **Eigenzeit A** (Emotionsverfall über Zeit) | 🟢 | `[Doku]` | — |
| **Eigenzeit B** (Level im Eintrag) | 🟠 | gebaut `[Doku]` | wartet auf seinen **ersten Eintrag mit Level** |
| **Eigenzeit D** (Rad-Riegel) | 🟠 | Riegel 1 gebaut `[Doku]` | Riegel 2 nicht gerechnet; `RIEGEL-5-7-OHNE-EINTRAG` |
| **Selbstauslösung** (vierter Ausgang zurück in die Queue) | 🟠 | zweimal live gefeuert `[Doku, 16.08.]` | Budget: drei je Turn für **alle** Gründe zusammen — vor dem zweiten Aufrufer braucht es getrennte Zähler |
| **Master-Switch `PIXIE_AKTIV`** | 🟢 | env-konfigurierbar `[Code]` | — |

---

## 9. Werkzeuge

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Zeitparser** (Fuzzy, Vektor-Modus, zwei Uhren) | 🟢 | `tools/`-Modul, 47 Tests `[Doku]` | `PARSER-NACKTE-UHRZEIT-FALSCHER-TAG` umgangen, Ursache extern; `ZEIT-EXTRAKTION-UNSCHARF` offen |
| **Web-Infrastruktur** (SearXNG + PageFetcher) | 🟢 | `ki_searxng` läuft seit 4 Tagen `[gemessen]` | — |
| **Auto-Fetch** (Suche → Seitenabruf) | 🟢 | `[Doku]` | — |
| **Multi-Channel — Telegram** | 🟢 | `ki_telegram` läuft `[gemessen]` | — |
| **Multi-Channel — Matrix + WireGuard** | ⚫ | kein Code `[Code]` | alles |
| **Voice (TTS/STT)** | ⚫ | Vision `[Doku]` | alles |
| **Dateien — Schreibwerkzeug** | 🟢 | `tools/dateien/schreiben.py` `[Code]` | nur schreibend, für Novas eigene Bibliothek |
| **Dateien — Leseschicht** (Karte, Block, Fenster, Fundstelle) | 🟢 | `tools/dateien/operationen.py`, 26 Zeugen · **erster Produktivaufrufer seit 18.08.2026**: `struktur_analysieren` füllt die Blockkarte des Index `[gemessen]` | — |
| **Dateien — Schreibschicht** (chirurgische Schnitte) | 🟢 | `tools/dateien/redaktion.py`, 20 Zeugen `[Code]` | — |
| **Dateien — Versionierung im Dokument** (`[cN>]`/`[dN>]`/`[iN>]`, Paarungsprüfung) | 🟢 | `tools/dateien/versionierung.py`, 20 Zeugen · Kette an echter Wissensdatei gefahren, 0 Befunde `[gemessen]` | — |
| **Dateien — Auftragsform `DATEI: {json}`** | 🟠 | `tools/dateien/hand.py`, 22 Zeugen `[Code]` — **weiterhin kein Aufrufer** | die Verdrahtung |
| **Wissensdatei — adressierbarer Block + Version** | 🟢 | `wissen_text_bauen` erzeugt `## AKTUELL` + `**Version:**` · **14 Dateien produktiv geschrieben** `[gemessen]` | — |
| **Ankertreue des Schreibmodells** | 🟢 | 30/30 zeichengenau und eindeutig, `gemma4-gpu` Median 1,7 s, `qwen36-cpu` 17,9 s `[gemessen]` | — |
| ~~**Dateien-Dienst — Stufe 0** (Einbettung gegen den Korpus prüfen)~~ | — | **entfallen** mit `novaberg-agent-dateien_k.md` v0.10 §3.0a-bis `[Doku]` | Die Schwelle ist keine Konstante mehr, sondern das Quantil `1 − K/N` der mitlaufenden Verteilung — es gibt keine einmalige Vermessung mehr, die vorher stattfinden müsste |
| **Dateien-Dienst — Stufe 1** (`dateien_wurzeln` + Freigabe) | 🟢 | `agents/dateien_wurzeln/`, 48 Zeugen · Tabelle steht, **Zeile 1 aus einem echten Turn** · Kette im Betriebslog von `Router: mgmt=agent/dateien_wurzeln` bis `verifiziert=True` `[gemessen]` | das **Vergessen** aus §2a.3 — es hat ohne Indextabelle keinen Gegenstand |
| **Dateien-Dienst — Stufe 2** (`dateien_index` + Wächter) | 🟢 | `agents/dateien_index/`, 18 Zeugen · Erstlauf **3 Dateien in 16 s**, Blockkarten 50/21/32, zweiter Lauf 0 neu / 3 unverändert `[gemessen]` | der **Takt** — `periodic_task()` ist None, bis die Änderungsrate gemessen ist |
| **Dateien-Dienst — Stufe 3** (Enricher-Quelle, `[AUFZEICHNUNGEN]`) | 🟢 | `agents/dateien_index/aufzeichnungen.py`, seit 18.08. **zweikanalig**, 27 Zeugen · im Betrieb: scharfer Kanal 0,4879 und 0,4718, Fremdthemen 0 Treffer · zwei Treffer unter dem Boden (0,1901 / 0,2148) fand **nur** der scharfe Kanal `[gemessen]` | die **Quantilschwelle** (`AUFZEICHNUNGEN-QUANTIL`) und der Boden, der bei heterogenem Korpus **widerlegt** ist |
| **Die epistemische Grenze im Prompt** (`[AUFZEICHNUNGEN]` neben `[GEDAECHTNIS]`) | 🟢 | eigener Block, Fundstelle je Eintrag · **im Betrieb**: die Figur nannte in allen drei Punkten ihrer Antwort die Quelldatei, und der gespeicherte Kurzzeit-Eintrag trägt sie mit — 1 von 2908 Einträgen mit Dateipfad, über den Abruf als Gedächtniszeile zurückgeholt `[gemessen]` | ~~eine Absicht, keine Arbeit~~ → **entschieden am 18.08.2026: der Übergang ist gewollt, es wird kein Tor gebaut** (`novaberg-agent-dateien_k.md` §9 Punkt 10). Offen bleibt allein die **Rate**: Wie oft die Herkunft den Übergang überlebt, ist an einem Fall belegt und nicht gemessen |
| **Zuordnung des Planners** (exakt vor unscharf) | 🟢 | `graph/nodes/planner.py::_manager_zu_target`, 8 Zeugen · Gegenprobe 4 vorhergesagt, 4 gezählt `[gemessen]` | — |
| **Dateien-Dienst — Stufe 4** (Auftragsweg mit Grep) | 🟢 | `agents/dateien/` samt Aufrufer (`plugins/dateien_manager/`, `klassifikation.py`, `agent.py`, `dispatch.py`, `auskunft.py`), 63 Zeugen · **echter Turn 18.08. 18:37 UTC**: scharfer Kanal 1 Treffer, Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen, und die Antwort trägt `/files/kzg-salienz.md` **und 0,67379** im selben Satz `[gemessen]` | die **Rückfrage** — der Dienst hat sie im Kanon und benutzt sie nicht; er ändert nichts, also gibt es nichts zu bestätigen |
| **Rückweg ins Wissen** (Gespräch → Wissensdatei, §4b) | 🟢 | `agents/wissen_rueckweg/`, 26 Zeugen · **zwei echte Läufe 18.08.**: einer ohne Schnitt mit Begründung (8 Kandidaten, bester Kosinus 0,3137), einer mit `[i1>]` zwischen Definition und Beleg, Version 1.0 → 1.1, Häufigkeit 1 → 2 `[gemessen]` | **zwei der drei Wege** — das Einprägsame (Schwelle 0,7 roh) und das Zugehörige sind nicht verdrahtet; dazu die Idempotenz: derselbe Fund zweimal eingereiht läuft zweimal, und nur der Aufruf verhindert die Dublette |
| **Dateien-Dienst — Stufe 5** (Vertiefung) | ⚫ | `[Doku]` | **zuletzt**, hinter der Gedankenkette |
| **Außenrand der Freigaben** (erzwungen, nicht deklariert) | 🟢 | `agents/dateien_wurzeln/aussenrand.py` · Gegenprobe: Randprüfung ausgehebelt → **5 vorhergesagt, 5 rot** · im Betrieb `/files/../knowledge` → `/knowledge` abgewiesen `[gemessen]` | — |
| **Rückweg der Rückfrage** (`dismissed`, Unklarheit fragt erneut) | 🟢 | `agents/dateien_wurzeln/resume.py` · Wortgrenzen statt Teilzeichenketten, im Betrieb nachgemessen `[gemessen]` | gilt nur für diesen Dienst; **drei Torwächter des Bestandes haben ihn weiterhin nicht**, und ihre Deutung ist als `ZUSTIMMUNG-GILT-ALS-ABLEHNUNG` offen |
| **Änderungserkennung über den Inhalt** (Hash statt Zeit) | 🟢 | `agents/dateien_index/wandern.py` · am Bestand belegt: gleiche Größe, gleiche `mtime`, anderer Inhalt → **erkannt**; Gegenprobe 2 vorhergesagt, 2 rot `[gemessen]` | — |
| **Bibliothek — drei Kanäle** (`suchtext`, `entitaet_ids`, `timeline_id`, `stichwoerter`) | 🟠 | vier Spalten auf `autonomous_wissen`, DDL gezündet, Schema-Zeuge deckt sie `[gemessen]` | **kein Schreiber** — die Spalten sind die Vorbedingung, nicht die Umsetzung |
| **`zuletzt_gelernt_hash`** (§5.2a — der Wiedereröffner) | ⚫ | Spalte steht in `dateien_index`, **niemand schreibt sie** `[Code]` — 18.08.2026 nachgeprüft, Stufe 3 hat sie nicht mitgebracht: Sie gehört zum **frühen Tor** (§3.0d) und nicht zum Enricher-Weg |
| **Verb-Mapping lernen** (nutzereigene Sprache) | 🔴 | `verb_mapping_lernen` **ohne Aufrufer**, `verb_mappings` **0 Zeilen** `[gemessen]` | Schreibpfad steht seit Chat 42 und wurde nie verdrahtet |
| **Hermes-Substrat** (Ausführungsschicht) | ⚫ | kein Code, keine Anbindungsspezifikation `[Code]` | sieben Messfragen M0–M6 unbeantwortet |
| **Skill-System** (Epic 10) | ⚫ | kein Code `[Code]` | alles |

---

## 10. Plugin-System

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **BaseManager + Auto-Discovery** | 🟢 | `plugins/base.py` `[Code]` | — |
| **PendingWrite** (Austauschformat) | 🟢 | `[Code]` | `PENDING-AGENT-INS-PAYLOAD` offen |
| **KzgManager** | 🟢 | `[Code]` | — |
| **NotizenManager** | 🟢 | `[Code]` | — |
| **TimelineManager** | 🟠 | `[Code]` | trägt einen ausdrücklichen Loud-Failure-Stub (`manager.py:243`) |
| **DirektivenManager** | 🟢 | `[Code]` | — |
| **CharakterIdentitaetManager** | 🟢 | `[Code]` | — |
| **FaktenManager** | 🔴 | `[Code]` — aber **deaktiviert**, Speicher leer `[gemessen]` | Aktivierung erfordert die Lösung von `FAKTEN-RAUSCH` |
| **WissenManager** | 🟠 | `[Code]` | Stufe 2 „den Block lesen, der wirklich gebraucht wird" — **noch nicht gebaut** (`manager.py:9`) |

---

## 11. Client (GTK4)

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **WebSocket-Umbau** (alle Stufen über WS) | 🟢 | abgeschlossen Chat 124 `[Doku]` | `WEBSOCKET-OHNE-KEEPALIVE` ✅ behoben 15.08. |
| **Chat-Ansicht + Stream-Handler** | 🟢 | `client/ui/` `[Code]` | `CLIENT-STUFEN-OHNE-TURN-KENNUNG` offen |
| **Emotions-Panel** (Radar) | 🟢 | `panels/emotions_panel.py` `[Code]` | Dual-Radar (beide Seiten) `[Doku]` offen |
| **Charakter-Panel** (5 Profile) | 🟢 | `panels/character_panel.py` `[Code]` | — |
| **GV-Panel** | 🟠 | `panels/gv_panel.py` `[Code]` | Dreischicht-Felder visualisieren offen |
| **KZG-/LZG-/Session-/Ziele-Panel** | 🟢 | vier Panels `[Code]` | — |
| **Gravitationskarte** | 🟢 | `panels/gravity_map_panel.py` `[Code]` | Turn-Dashboard mit Mikrosternen `[Doku]` offen |
| **System-Panel + StatusBar** | 🟢 | `[Code]` | `LOG-TUERKLINGEL` (Warn-/Fehlerlampen) offen |
| **Offene Frage sichtbar machen** | ⚫ | `CLIENT-OFFENE-FRAGE-UNSICHTBAR` `[Doku]` | alles |
| **Projektseite** | ⚫ | `PROJEKTSEITE-NACHZIEHEN` `[Doku]` | alles |

---

## 12. Infrastruktur und Modellschicht

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Docker-Verbund** (5 Dienste) | 🟢 | alle fünf Container up `[gemessen]` | — |
| **Tri-LLM + Connector-System** | 🟢 | `[Doku]` · Block 4 der MS-Welle abgeschlossen | — |
| **Model-Service-Schicht** (ChatWorker, BackgroundWorker, EmbedWorker) | 🟢 | `services/model_services/` `[Code]` | `SUBMIT-SYNC-BEHAUPTET-WORKER-THREAD` offen — zweimal live zugeschlagen |
| **Microservice-Modell-Queue** (Blöcke 1–5) | 🟢 | abgeschlossen Chat 97 `[Doku]` | — |
| **Embedding-Konsolidierung** (ein Pfad) | 🟢 | `[Doku]` | `EMBED-DIMENSIONSCHECK-FEHLT` offen; Einbettungsmodell gegen Fachtexte **ungemessen** |
| **Health-Check** | 🟢 | `api/health.py`, rechnet den NMCP-Befund frisch `[Code]` | — |
| **Admin-API** (Pause/Resume/Flush) | 🟢 | `api/admin.py` `[Code]` | — |
| **Schema in `db/init.sql` + Agenten-`init.sql`** | 🟢 | 22 Tabellen definiert, **0 im Code benutzte Tabelle fehlt** `[gemessen]` | `LZG-MIGRATION-REVIEW-NICHT-IN-INIT`, `IDX-TIMELINE-TYPE-NICHT-IN-INIT` offen |

---

## 13. Prüfung und Werkzeugkette

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Test-Suite** | 🟠 | 1.617 grün, 0 übersprungen `[Doku, 17.08.]` | meldet **gelegentlich rot und reproduziert nicht** — der Testname ist unbekannt |
| **Linter-Nulllinie** (`ruff.toml`) | 🟢 | 2.147 geduldete Treffer `[Doku]` | — |
| **Harte Wand** (`ruff-hart.toml`) | 🟠 | **4 Familien** hart: `LOG`, `F821`, `W`-Auswahl, `N` `[Code]` | elf Familien unbewacht, bis sie leer sind |
| **Charakterisierungs-Netz** | 🟢 | `[Doku]` | — |
| **Kanalprüfung** (Deklaration gegen Leser) | 🟢 | 74 Felder geprüft, **0 tote Kanäle** `[gemessen]` | — |
| **Konfigurationsprüfung** (Konstante ohne Leser) | ⚫ | kein Werkzeug — **8 tote Konstanten** von Hand gefunden `[gemessen]` | `DATEILOG_AKTIV`, `EBBINGHAUS_DECAY_RATE`, `EBBINGHAUS_MIN_GEWICHT`, `EMOTIONALE_GRAVITATION_FAKTOR_SESSION`, `KZG_VERSTAERKUNG_DIVISOR`, `REDUCER_AKTIV`, `REDUCER_LOG_REMOVED`, `STIL_SESSION_GEWICHT` |

---

## 14. Was diese Erhebung nebenbei gefunden hat

Vier Befunde, die in keinem Register standen — gefunden beim Halten dieser Liste gegen den Bestand:

1. **Der Zombie-Schlüssel greift daneben.** Der Start löscht `pixie:schedule:{agent.name}`, angelegt wird unter `{task.name}`. Genau ein Dienst hat verschiedene Namen — `charakter` gegen `charakter_hash` —, und sein Zeitplan liegt live unter `pixie:schedule:charakter_hash`. Meldet er einmal keine periodische Aufgabe mehr, bleibt der Kandidat stehen.
2. **Acht Konfigurationskonstanten ohne jeden Leser** (§13).
3. **Der NachfragenAgent scheitert in 56 von 58 Läufen** und schweigt seit dem 12.08., während 45 Aufträge auf ihn warten (§7.3).
4. **Drei Pipeline-Logger ohne Aufrufer** — `log_prompt`, `log_bemerkung`, `log_token` (§1.3).

**Drei Statuszeilen im Bestand sind durch diese Erhebung widerlegt:**

| Dokument | sagt | ist |
|---|---|---|
| `novaberg-haltungsraum_k.md` | „es fehlen der Prompt-Block (§3)" | der Block steht seit dem 13.08. |
| `novaberg-eigenzeit_k.md` | „D fehlt" | Riegel 1 von D steht seit dem 15.08. — die eigene Versionshistorie derselben Datei sagt es |
| `novaberg-architecture.md` §6 | „Synapsen-Tabellen: Schema angelegt, leer" | 2.390 Knoten, 365.088 Kanten |

---

## 15. Die Zahlen dieser Erhebung

Nachgezaehlt in dieser Datei, nicht geschaetzt:

```
Dokumente im Verzeichnis        154
davon Konzepte (*_k.md)          44   alle geprueft
Zeilen mit Ampel                194

  gruen   fertig                103
  orange  begonnen               36
  schwarz nicht begonnen         37
  rot     fehlerhaft             18

Belege [gemessen]                72
Belege [Code]                    95
Belege [Doku]                    36
```

Gezählt werden **nur Belege in Ampelzeilen** — die Marken im erklärenden Text zählen nicht mit. Die Zählvorschrift steht hier, weil eine Zahl ohne sie beim nächsten Nachrechnen um fünf danebenliegt:

```
Ampelzeile  = eine Tabellenzeile, deren zweite Spalte genau eine der vier Farben trägt
```

**Die 36 `[Doku]`-Belege sind die Arbeitsliste der nächsten Erhebung** — sie sind die einzigen, die noch niemand gegen den Bestand gehalten hat. Ihr Anteil ist zugleich der Fälligkeitsanzeiger dieser Liste: Er wächst zwischen zwei Erhebungen von selbst.

**91 Zeilen stehen auf orange, schwarz oder rot.** Das ist die Menge der offenen Arbeit, und sie ist damit erstmals abzaehlbar.
