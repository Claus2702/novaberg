# Novaberg — Featureliste mit Ampel

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Vollständiges Register aller Features mit Zustandsampel und Beleg
**Stand:** 21. August 2026, 10:29 UTC
**Verlauf:** [Verlauf des Standes](#verlauf-des-standes) — 33 Eintraege, juengster zuerst
**Pfad:** novaberg/docs/novaberg-featureliste.md
**Typ:** Register
**Quellen:** die 43 Konzeptdokumente, `novaberg-architecture.md`, die Moduldokumente, `novaberg-roadmap.md`, `novaberg-backlog.md`, `novaberg-bugs.md`, `novaberg-fundliste.md` — gehalten gegen Code und Produktivsystem

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
| **AgentGraph** (Pfad 3 — Hintergrundarbeit) | 🔴 | `graph/agent_graph.py` `[Code]` | — · **🔴 seit 20.08.2026** (zuvor 🟢): `AGENTGRAPH-REIZPLATZ-FALSCH` offen |
| **PixieGraph** (eigener Graph für Pixie statt AgentGraph) | ⚫ | `create_pixie_state` existiert nicht `[Code]` · `novaberg-pixie-graph-merge_k.md` Phase 0–3 | alles |
| **Kanalzwang im StateGraph** (jedes Feld deklariert) | 🟢 | 74 Zustandsfelder, **0 ohne Vorkommen außerhalb `state.py`** `[gemessen]` | — |
| **Event-Modell** (Consumer statt async-Block) | 🟢 | `services/event_consumer.py`, `services/events.py` `[Code]` | — |
| **Prompt-Eingangsqueue** vor Pfad 1 | 🟢 | `services/prompt_eingang.py`, `prompt_consumer.py` `[Code]` | — |
| **TurnOrchestrator** (Vision Chat 58) | ⚫ | kein Modul `[Code]` | alles |

### 1.2 Die zwanzig Knoten

| Knoten | Ampel | Beleg | Rest |
|---|---|---|---|
| `perzeption` — Emotion, Arousal, Intent, Dual-Modus | 🔴 | `[Code]` · `novaberg-node-perception.md` | schreibt **keinen** Pipeline-Eintrag · **🔴 seit 20.08.2026** (zuvor 🟢): `PERZEPTIONSFELDER-OHNE-KANON` offen |
| `db_zugriff` — CG-Eingang, Personality-Klassen | 🟢 | `[Code]` · Pipeline-Einträge vorhanden `[gemessen]` | — |
| `enricher` — Kontext aus vier Quellen | 🔴 | `[Code]` | Fakten-Enrichment **abgeschaltet** seit Chat 71 (`enricher.py:847`) · **🔴 seit 20.08.2026** (zuvor 🟠): `ENRICHERPROMPT-LEERE-HUELLE` offen |
| **Query Rewriting** (der Suchschluessel traegt den Gegenstand) | 🟢 | `graph/nodes/enricher.py::_suchtext_bauen`, **10 Zeugen**, Gegenprobe 10 rot bei 7 vorhergesagt · gemessen vor dem Bau gegen 306 Ausarbeitungen: rohe Aeusserung **0/10** ueber der Abrufschwelle, Rewrite auf Frageform **5/10** (Median-Kosinus 0,1865 → 0,4173); Themenwechsel 3/3 unter der Schwelle, fremde Verlaeufe 15/15 ohne Treffer · im Betrieb an einem echten Turn belegt `[gemessen]` | **Am 21.08.2026 fuer alle fuenf Leser gemessen** `[gemessen]`: 39 Sonden aus dem Bestand der Konsumenten selbst, durch ihren echten Lesepfad — rohe Aeusserung **0/39**, Rewrite **37/39**, und das Rewrite deckt sich mit der handaufgeloesten Referenz in **39/39**. NMCP `wissen` teilt den Lesepfad der Bibliothek und ist damit mitgedeckt |
| `ei_calc` — Verlauf, Vektor, Empathie | 🟢 | `[Code]` · `novaberg-node-ei-calc.md` | kein Pipeline-Eintrag |
| `emotionale_gravitation` — reaktivierte Erinnerung | 🟢 | `[Code]` · `novaberg-node-emotionale-gravitation.md` | kein Pipeline-Eintrag; `GRAVITATION-KLEMME-FEHLT` offen |
| `ei_calc_persist` — CG-Ausgang, Zustand schreiben | 🟢 | `[Code]` | — |
| `reducer` — Gegenspieler zum Enricher | 🟠 | Knoten verdrahtet in `character_graph.py:63` `[Code]` | `REDUCER_AKTIV` und `REDUCER_LOG_REMOVED` haben **keinen Leser** `[gemessen]`; strukturierter `memory_context` (Reducer-Umbau) offen |
| `router` — Routing und Delegation | 🔴 | `[Code]` · `novaberg-node-router.md` | kein Pipeline-Eintrag · `ROUTER-MISS-OHNE-ABSCHLUSS`, `ROUTE3` offen · **🔴 seit 20.08.2026** (zuvor 🟠) — der Grund ist zur Hälfte fort: `ROUTERPROMPT-ZWEIFEL-WIDERSPRUCH` **behoben** **geprueft 20.08.2026** (der zweite Satz über den Zweifel kommt im Serverbaum nicht mehr vor), die beiden anderen offen |
| `planner` — Agentenschleife, Resume | 🔴 | `[Code]` · `novaberg-node-planner.md` | kein Pipeline-Eintrag · `PLANNER-AKTIV-RELIKT` · **🔴 seit 20.08.2026** (zuvor 🟠): `RESUME-VERBRAUCHT-IMPULS` offen |
| `agent_dispatch` — zentraler Eintritt | 🟢 | `[Code]` · Pipeline-Einträge `[gemessen]` | `DISPATCH-ABSCHLUSS-UNVOLLSTAENDIG` offen |
| `gespraechsvektor` — Landschaft, Strategie, Lücken | 🟢 | `[Code]` · `novaberg-node-gv_k.md` | siehe §5 |
| `haltung` — fünf Verhaltensgrößen | 🔴 | Knoten rechnet, protokolliert, persistiert `[Code]` | Wirkung siehe §5 · **🔴 seit 20.08.2026** (zuvor 🟢): `UEBERSTEUERUNG-GREIFT-NICHT` offen · `UEBERSTEUERUNG-AB-FUER-DREIERSKALA` **behoben** **geprueft 20.08.2026** — die Schwelle steht auf 0.9 statt 1.0 und ein Zeuge hält die Eichung |
| `verfasser` — der Inhalt vor der Form | 🔴 | `[Code]` · `novaberg-node-verfasser_k.md` **✅ gebaut** | läuft **nicht** auf dem Aufgabenpfad · **🔴 seit 20.08.2026** (zuvor 🟢): `VERFASSER-KOPFBLOCK-FAELLT-AUS`, `VERFASSER-ORDNET-IMPULS-PERSON-B-ZU`, `FRAGEN-ZEILE-OHNE-BEDINGUNG` offen |
| `responder` — die Antwort | 🔴 | `[Code]` · `novaberg-node-responder.md` | kein Pipeline-Eintrag · `RESPONDER-LEERE-ANTWORT-STILL` Ursache offen · **🔴 seit 20.08.2026** (zuvor 🟢): `RESPONDER-ERFINDET-DATUM` und `FALSCHE-BESTAETIGUNG-WIRD-ERINNERUNG` offen — **vier von sechs sind behoben** **geprueft 20.08.2026**: `NUTZERKERN-ERREICHT-RESPONDER-NICHT`, `BEZIEHUNGSPROFILE-UNBESCHRIFTET`, `RESPONDER-ANWEISUNG-DOPPELT`, `FARBTON-ERREICHT-RESPONDER-NICHT` |
| `thinker` — Faktenprüfung, Websuche | 🟠 | `[Code]` · `novaberg-node-thinker.md` | kein Pipeline-Eintrag — der Thinker ist **nicht beobachtbar** (`B−1` der Sykophanz-Reihe) |
| `thinker_cache` | 🟢 | `[Code]` | kein Pipeline-Eintrag |
| `tribunal` — drei Perspektiven | 🔴 | `[Code]` · `novaberg-node-tribunal.md` | kein Pipeline-Eintrag · `TRIB-PERSON-DRIFT` offen · **🔴 seit 20.08.2026** (zuvor 🟢): `TRIBUNAL-ERKENNT-ABBRUCH-OHNE-FOLGE` offen |
| `corrector` — Korrekturschleife | 🟢 | `[Code]` · `novaberg-node-corrector.md` | kein Pipeline-Eintrag |
| `salience` — Salienz als Entscheider | 🔴 | `[Code]`, läuft — aber **gesättigt**: 87 % der `user`- und 99 % der `assistant`-Einträge über 0,90 `[Doku, Fundliste 17.08.]` | rangiert nichts mehr; `KZG-SALIENZ-SKALENBRUCH`, `SALIENZ-JSON-BRICHT-AN-LATEX` offen |
| `dispatcher` — Schreiboperationen verteilen | 🟢 | `[Code]` · `novaberg-node-dispatcher.md` | — |

### 1.3 Querschnitt Pipeline

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Prompt-Schema `[BLOCKNAME]`** auf allen Knoten | 🟢 | `novaberg-pattern-prompt-schema.md` `[Doku]` · `[Code]` — **7 Dateien** unter `prompts/` und `graph/` tragen Blockmarken der Form `[GESPRAECHSVEKTOR]`, `[AUFZEICHNUNGEN]`, `[MASS]`; am Bestand gezaehlt 20.08.2026 `[Erhebung 20.08.2026]` | — |
| **Entscheidungs-Eintrag je Knoten** (jede Weiche dauerhaft belegt) | 🔴 | **9 von 20 Knoten** schreiben einen Pipeline-Eintrag `[gemessen]` | 11 Knoten ohne, darunter Router, Responder, Thinker, Planner, Perzeption |
| **Pipeline-Log** (Forensik, Spans, JSONB) | 🔴 | **87.913 Zeilen**, 10 Eintragsarten, täglich wachsend `[gemessen]` | `log_prompt`, `log_bemerkung`, `log_token` haben **keinen Aufrufer** `[gemessen]` · **🔴 seit 20.08.2026** (zuvor 🟢): `TURNROH-ZEILE-FEHLT`, `HALTUNGSSTAND-OHNE-LOGZEILE` offen |
| **Rückfrage-Kette** (Redis-Pending, Resume) | 🔴 | `[Code]` · `novaberg-graph.md` — **`ZUSTIMMUNG-GILT-ALS-ABLEHNUNG` offen seit 18.08.**: Die Ja/Nein-Deutung vergleicht Teilzeichenketten, `gerne` gilt als Nein `[gemessen]` | `RESUME-VERBRAUCHT-DEN-IMPULS` ✅ behoben 14.08. · die Deutung an Wortgrenzen, je Torwächter ein Zeuge |

---

## 2. Emotionale Wahrnehmung (EI)

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Plutchik-Oktagon** (9 Vektoren, Normalisierung) | 🔴 | `ei/berechnung.py`, `novaberg-ei-plutchik.md` `[Code]` | `PERZEPTION-EMOTION-AUSSER-KANON` offen · **🔴 seit 20.08.2026** (zuvor 🟢): `EMOTIONS-VEKTOREN-DOPPELT` offen |
| **EI-Plausibilitätsgate** (8 Sektoren) | 🔴 | `[Code]` · `novaberg-node-perception.md` | — · **🔴 seit 20.08.2026** (zuvor 🟢): `NEGATIVE-EMOTIONEN-DOPPELT` offen |
| **Arousal-basierter Decay** | 🟠 | `[Code]` · `novaberg-ei-plutchik_l.md` | zählt **Turns statt Zeit** — die Gegenbewegung über eine Pause ist Bauteil A der Eigenzeit (§8) |
| **EI-MIKRO** (situative Mikro-Anweisungen) | 🟢 | `responder.py:_ei_mikro_anweisung` `[Code]` | — |
| **Dual-Emotion Phase 1** (User-IDs entkoppelt) | 🟢 | `[Doku]` Chat 57 · `[Code]` — `memory/kzg.py`, Key-Schema `kzg:{user_id}:{character_id}:{entry_id}`; das Paar definiert das gemeinsame Gespraech `[Erhebung 20.08.2026]` | — |
| **Dual-Emotion Phase 2** (Nova-Empathie, Konflikt) | 🟠 | `[Code]`, AP1–7 und AP9 gebaut | AP8 Client-Teil `[Doku]` |
| **Dual-Emotion Phase 3** (Ziel-Vektor als dritte Kraft) | 🟠 | `ziele`: **259 Zeilen**, `ZielDecayAgent` läuft `[gemessen]` | `ziel_motivation_anpassen` hat **keinen Aufrufer** `[gemessen]`; der Antrieb wirkt nicht auf die Emotion |
| **Emotionale Gravitation** (Erinnerung zieht) | 🔴 | `ei/gravitation.py` `[Code]` | `EMOTIONALE_GRAVITATION_FAKTOR_SESSION` ohne Leser `[gemessen]` · **🔴 seit 20.08.2026** (zuvor 🟢): `GRAVITATION-FAERBT-EIGENE-GEDANKEN`, `ZUG-ZWISCHEN-090-097-ABGESCHALTET` offen |
| **Wahrnehmungs-Gravitation** (Synapsen P10) | 🟠 | `wahrnehmung_verschieben()` gebaut, live gemessen `[Doku]` | **Wirkung ungemessen** — ob sich je eine Trefferliste ändert, ist offen |
| **Anker-Emotion** (Grundemotion je Charakter) | ⚫ | kein Code `[Code]` | alles |

---

## 3. Gedächtnis

### 3.1 Die Speicher

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Session-Gedächtnis** (Redis, Turn-Formatierung) | 🟠 | 2.893 Redis-Keys `[gemessen]` | Die Session **stirbt nicht** — jeder Impuls verlängert die Frist (Eigenzeit §2, Bauteil C) |
| **Kurzzeitgedächtnis KZG** (Redis + Vektor) | 🟢 | **2.665 `kzg:*`-Keys** des Paares `[gemessen 21.08.2026]` · `novaberg-mem-kzg.md` · **Abrufschwelle am 21.08.2026 gemessen und auf 0,72 gesetzt** (vorher 0,40, unter dem Boden des Raums): am Bestand vorher/nachher — 10 unbezogene Fragen 100 → **0** Einträge, 3 anaphorische Rückfragen 30 → **0**, 3 einschlägige 30 → **30** `[gemessen]`, 6 Zeugen, Gegenprobe 5 von 6 rot | `KZG-SEGMENT-DUPLIKAT`, `KZG-VERDICHTER-KONTEXT-VERLUST` offen |
| **KZG-Magnetfelder** (`entitaet_ids`, `timeline_id`) | 🔴 | `[Code]` · Synapsen P3 | — · **🔴 seit 20.08.2026** (zuvor 🟢): `ENTITAETIDS-MIT-DUBLETTEN` offen |
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
| **KZG-Salienz-Neubau** | 🔴 | Bauteil 1 gebaut und migriert `[Doku]` | **drei von sieben IDs offen**; die Skala ist gesättigt (§1.2) · **🔴 seit 20.08.2026** (zuvor 🟠): `KZG-SALIENZ-GESAETTIGT` offen |
| **Assoziatives / aktenbasiertes Retrieval** | ⚫ | kein Code `[Code]` | alles |
| **KZG-Liberalisierung + Cluster-Promotion** | 🔴 | Konzept vom 25.04.2026 traegt *„implementiert und getestet"*; der Pfad ist **seit Chat 98 deaktiviert**, die Konstanten `CLUSTER_MIN_EINTRAEGE`, `CLUSTER_THEMEN_SIMILARITY`, `CLUSTER_LZG_SIMILARITY` stehen weiter in `config.py` und wurden in Chat 107 sogar nachkalibriert. `CLUSTER_PROMOTION` hat **0 Aufrufer** im Baum `[Code]` | gebaut, abgeschaltet, und die Konstanten leben weiter — der Kommentar im Code sagt es selbst: *„Alt-Cluster-Pfad (deaktiviert seit Chat 98), trotzdem mitgezogen"*. Neu aufgenommen bei der Erhebung am 20.08.2026 |

---

## 4. Charakter

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Fünf Charakter-Profile + Hash** | 🔴 | **34 Zeilen** in `charakter_hash` `[gemessen 19.08.2026]` · `novaberg-pixie-character-hash.md` · `[Code]` — `agents/charakter/` mit Destillation und `charakter_hash` | `CHAR-HASH-PAAR-VERTAUSCHT` offen — die Figur steht in der `user_id`-Spalte. **Neu:** `PROFIL-EINMALERHEBUNG` — die Profile werden einmal erhoben, die Räder daraus dreimal; derselbe Prompt streut über drei Läufe 16,5–24,5 %, der gespeicherte Lauf trug 42 % · **🔴 seit 20.08.2026** (zuvor 🟢): `PROFILPROMPT-OHNE-GESCHLECHT`, `KERNHASH-OHNE-PERSPEKTIVTRENNUNG`, `PERSPEKTIVE-OHNE-DATIV` offen · `KERNHASH-LIEST-TURNWORTLAUT` **behoben** **geprueft 20.08.2026** (die Doku ist nachgezogen; dass 40 von 444 Zeilen zwei von zwanzig Bestandstagen decken, ist eine andere Frage) |
| **Sprachadaption (CAT)** | 🔴 | `novaberg-ei-language-adaptation.md` `[Doku]` | `SPRACH-STIL-DEFENSIV-STUMM` offen · **🔴 seit 20.08.2026** (zuvor 🟢): `SPRACHSTIL-ZWEI-VERFAHREN-UNEINIG` offen |
| **Charakter-Räder als Messreihe** | 🔴 | **178 Messungen** in `charakter_rad_messung` `[gemessen 19.08.2026]` · beide Räder · `[Code]` — Tabelle `charakter_rad_messung`, Spiegelung der beiden Raeder eines Paares als SQL-Abfrage | `RAD-GESPEICHERT-NICHT-REPRODUZIERBAR`, `RAD-WERT-AUF-SPALTEN-DEFAULT` offen. **Neu am 19.08. gemessen und in der Fundliste:** 37 % des Zugbudgets liegen auf Speichen ohne Trennschärfe zwischen den Paaren, der Faktor erreicht deshalb über 88 Messungen nur 0,864–1,443 statt 0,5–1,5; und beim Initiative-Rad tragen 5 von 10 Speichen einen gespeicherten Wert, den der Median ihrer Läufe nicht stützt · **🔴 seit 20.08.2026** (zuvor 🟢): `SPEICHENWERT-NICHT-MEDIAN`, `RADSPEICHEN-MESSEN-PROFILTEXT` offen |
| **CharakterIdentitätsAgent** (Saatgut) | 🟢 | `[Code]` · 1 Zeile in `charakter_anweisungen` `[gemessen]` | `CRUD-REACTIVATE-STAMP`, `CHAR-ID4-ORPHAN` offen |
| **Charakter-Resonanz — Bauteil 1a/1b** (Brücke) | 🟢 | `verbindung` **7.073 Zeilen** `[gemessen]` | — |
| **Charakter-Resonanz — Bauteil 2** (Backfill) | ⚫ | optional, nicht gebaut `[Code]` | alles |
| **Charakter-Resonanz — Bauteil 3** (`verhaltensweisen` + Verdichter) | ⚫ | **Tabelle existiert nicht** `[gemessen]` | der ganze Bauteil; die Brücke füllt sich seit Wochen für einen Verbraucher, den es nicht gibt |
| **Charakter-Resonanz — Bauteil 4** (Lesepfad) | 🟠 | CharakterAgent liest `verbindung` `[Code]` — aber **anders als geplant** | liest Turn-Wortlaut statt destillierter Verhaltensweisen |
| **Charakter-Resonanz — Bauteil 5** (Doku) | ⚫ | — · `[Doku]` — der Bauteil ist die Dokumentation selbst; ohne Code kein Codebeleg moeglich | nach 1–4 |
| **Charakterbildungs-Messreihe** (18 Bögen, 540 Turns) | 🟠 | aufgesetzt und zurückgesetzt `[Doku]` | wartet auf die GPU |
| **Profil-Historie** | ⚫ | `PROFIL-HISTORIE-FEHLT` `[Doku]` | alles |

---

## 5. Gesprächsvektor, Lage und Haltung

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **GV1 + GV2** (Farbmischung, Landschaft) | 🔴 | `graph/nodes/gespraechsvektor.py` `[Code]` | `GV-HYPOTHESE-ROHE-AUSGABE`, `GV-PANEL-STRATEGIE-DOPPELT` offen · **🔴 seit 20.08.2026** (zuvor 🟢): `GESPRAECHSVEKTOR-HYPOTHESE-DREIFACH` offen |
| **14 Gesprächslandschaften** | 🟢 | `novaberg-gv-strategie_k.md` `[Doku]` · `[Code]` — `CLUSTER_BESCHREIBUNGEN` in `ei/dreischicht.py`, **14 Eintraege gezaehlt** am 20.08.2026 `[Erhebung 20.08.2026]` | — |
| **Erreichbarkeit der Landschaften** | 🟠 | alle vierzehn erreichbar gemessen `[Doku]` | **Ablesung fällt in 14 % aus** — kein Code für die Abhilfe |
| **Initiative-Achse** | 🔴 | `ei/initiative.py`, Schwelle gegen Zeugen kalibriert `[Code]` | `initiative_berechnen` in `ei/dreischicht.py` hat **keinen Produktivaufrufer** `[gemessen]` · **🔴 seit 20.08.2026** (zuvor 🟢): `INITIATIVE-DOPPELT-BELEGT` offen |
| **Kalibrierverfahren** (sechs Klassen, Korridor) | 🟠 | `ei/kalibrierung.py` + `agents/kalibrierung/` als Messwerkzeug `[Code]` | **kein Erwartungskorridor geschrieben, keine Validierungsmenge erhoben** |
| **GV4 — Wissenslücken im Prompt** | 🟢 | `ei/wissensluecken.py`, Lücken werden eingefügt `[Code]` | `WISSENSLUECKEN-FELDER-LEER` offen |
| **Wissenslücken-Speicher** | 🔴 | **785 Zeilen, ausnahmslos `offen`**, 78 in zwei Tagen neu `[gemessen]` | kein Verbraucher; `geschlossen`/`ausgeschlossen` sind Statuswerte **ohne Schreiber**; GV4 rechnet parallel und liest die Tabelle nie |
| **Haltungsraum — Rechnung, Knoten, Protokoll, Stand** | 🔴 | `ei/raum.py`, `graph/nodes/haltung.py`, `memory/haltung.py` `[Code]` | — · **🔴 seit 20.08.2026** (zuvor 🟢): `HALTUNGSSTAND-OHNE-LOGZEILE` offen |
| **Haltungsraum — Prompt-Block** | 🔴 | gebaut am 13.08. (`_sprachstil_block`) `[Code]`, aber **gemessen ohne Bindung**: Streuung 2,68 bei identischer Vorgabe `[Doku, Messung 17.08.]` · seit 20.08. **drei Einflüsse statt einem** — Raum, halbierte Korridore, Länge der Äußerung bei rein leichten Intentionen `[Code]` | die Zahl regiert das Modell nicht; die Struktur, die binden würde, ist die Gedankenkette (§6). **Die Wirkung der Halbierung im Betrieb ist ungemessen** |
| **Haltungsraum — der zweite Leser (Verfasser)** | 🟡 | Block `[MASS]` mit Menge, Rückfrage und Vorschlag; `umfang`, `fragen`, `draengen` gehen an den Verfasser, `naehe` und `waerme` bleiben beim Responder. 10 Zeugen, Gegenprobe 5/5 `[Code]` | gebaut und bezeugt, **im Betrieb nicht gemessen** — kein echter Turn seit dem Bau |
| **Haltungsraum — Ablösung der alten Längenregel** | 🔴 | die drei Längenzweige sind entfernt (`responder.py:60`) `[Code]` | — · **🔴 seit 20.08.2026** (zuvor 🟢): `UMFANGSREGLER-BINDET-NICHT`, `NEUER-NUTZER-OHNE-UMFANGSVORGABE`, `MENGENANGABE-BINDET-NUR-UNTEN` offen |
| **Zuwendungs-Riegel** (erster Leser des Standes) | 🟠 | Riegel 1 gebaut, Schwelle 0,25 `[Doku]` | Riegel 2 **nicht gerechnet** → die stündliche Decke steht |

---

## 6. Denken und Wissen

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Thinker** (Faktenprüfung + Websuche) | 🟠 | `[Code]` | **nicht beobachtbar** — kein Protokoll seiner Weiche |
| **Tribunal** (Drei-Perspektiven-Score) | 🟢 | `[Code]` · `novaberg-node-tribunal.md` | `TRIB-PERSON-DRIFT` offen |
| **Recherche** (SearXNG, Dual-Modell, Destillation) | 🟢 | **1.647 Bibliotheksläufe**, 538 in sieben Tagen `[gemessen]` | `RECHERCHE-OHNE-AUDIT`, `RECHERCHE-RELEVANZ-UNGEPRUEFT`, `RECHERCHE-LEER-GLEICH-AUSFALL`, `RECHERCHE-SALIENZ-KONSTANT` offen |
| **Wissensspeicher / Bibliothek** (`autonomous_wissen`) | 🔴 | **466 Zeilen**, seit 04.08. `[gemessen]` | **drei von vier Modi ohne Erzeuger** — nur `recherche` schreibt; `vertiefung`, `traum`, `nachfragen` sind deklariert und leer · **🔴 seit 20.08.2026** (zuvor 🟠): `BIBLIOTHEK-FILTERT-ZWEISPALTIG` offen |
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
| `B0` Fallenbatterie (Nulllinie) | 🟠 | beide Hälften gefahren `[Doku]` | — · **🟢 → 🟠 bei der Erhebung am 20.08.2026.** **Die Erhebung am 20.08.2026 fand keinen Zeugen**: kein Test unter `tests/` traegt Fallenbatterie oder Nulllinie im Namen; die naechstliegenden sind `test_einwandsurteil.py` und `test_vorzeichenpruefung.py`, und die gehoeren zu B1 und B4. `[gemessen]` |
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
| **NMCP-Handshake beim Start** | 🔴 | **15 von 15 Diensten eingebunden, 0 verweigert** `[gemessen, 18.08.]` · `[Code]` — `agents/nmcp.py`, `anmelden()` mit vier Ausgaengen | — · **🔴 seit 20.08.2026** (zuvor 🟢): `AUSSCHLUSSRIEGEL-TRIFFT-SACHWORT` offen |
| **Zuschnitt des Zustands auf die Anmeldung** | 🟢 | `agents/nmcp.py` `[Code]` | — |
| **Quotenabgleich** (angemeldet gegen gezählt) | 🟠 | Job im Scheduler, `NMCP_ABGLEICH_INTERVALL` `[Code]` | braucht 30–100 Äußerungen je Dienst — noch kein Urteil |
| **Vierter Ausgang** (`abgelehnt` = Zweifelsfall) | 🟠 | **5 von 15 Diensten** melden ihn an `[gemessen, 18.08.]` · `[Code]` — `agents/nmcp.py` Zeile 489, `if "abgelehnt" not in agent.ausgaenge` | für die zehn Hintergrunddienste ist der Grad „eingeschränkt" eine Aussage **ohne Wirkung** |
| **Selbstauskunft der Dienste** (`beschreibungen()`) | 🔴 | 15 Anmeldungen, **kein Produktivaufrufer** `[gemessen, 18.08.]` · `[Code]` — genau **eine** `def beschreibungen`-Stelle im Baum, gezaehlt am 20.08.2026 `[gemessen]` | `SELBSTAUSKUNFT-OHNE-LESER` |
| **Grenze** (`grenze`-Eigenschaft) | 🔴 | **5 Deklaranten, 0 Leser** `[gemessen]` | Ablageort entscheiden: Brett oder vierter Ausgang |
| **Audit-Pflicht** (`hintergrund_log`) | 🔴 | **6 von 15 Agenten** schreiben; über die gesamte Lebenszeit nur **7 Aufgabenarten** `[gemessen]` | acht Agenten ohne Eintrag, darunter drei periodische; fünf eigene Kopien von `_audit_log` |

### 7.2 Die Agenten des Menschen

| Agent | Ampel | Beleg | Rest |
|---|---|---|---|
| **NotizenAgent** (CRUD, pg_trgm) | 🔴 | 1 Zeile in `notizen` `[gemessen]` | sechs offene Bugs: Container-Wechsel, Kontext-Rekonstruktion, Skill-Manifest, leeres UPDATE-Ziel, Befehl als Titel · **🔴 seit 20.08.2026** (zuvor 🟠): `NOTIZAUFTRAG-GEHT-AN-TIMELINE` offen |
| **TimelineAgent** (bi-temporal, ZeitVektor) | 🔴 | **61 Einträge** `[gemessen]` — aber der **Lesepfad ist instabil**: Nova verneinte einen aktiven Termin `[gemessen, 17.08.]` | eine ausgebliebene Zustellung ist von einer richtigen Auskunft nicht zu unterscheiden · `TIMELINE-LESEPFAD-INSTABIL` offen (Erhebung 20.08.2026) |
| **DirektivenAgent** (HITL-Gate) | 🟢 | **12 Direktiven** `[gemessen]` | teilt die Deutung aus `ZUSTIMMUNG-GILT-ALS-ABLEHNUNG` — **nicht nachgemessen** |
| **CharakterIdentitätsAgent** | 🟢 | siehe §4 · `[Code]` — `agents/charakter_identitaet/` | — |
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
| **Pixie-Plugin — der Nutzer beauftragt Pixie** | ⚫ | Konzept `novaberg-pixie-plugin_k.md` vom 29.04.2026: *„Der User kann keinen Pixie-Auftrag erteilen"* — es gibt keinen Pfad vom Router in die Pixie-Welt. Kein Bezeichner `user_auftrag`/`pixie_auftrag` im Baum `[Code]` | die Pixie-Agenten laufen ausschliesslich periodisch oder Queue-getrieben; die symmetrische Haelfte des Plugin-Systems fehlt. Neu aufgenommen bei der Erhebung am 20.08.2026 |

---

## 8. Pixie — die Eigenzeit

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Heartbeat, zwei Spuren** (LLM + CPU) | 🟢 | zwei Jobs im Scheduler `[Code]` | **ein serieller Platz** je Spur — der Engpass der Reihe 3 |
| **Shadow-Queue in PostgreSQL** | 🔴 | **958 Aufträge** `[gemessen]` | Rückstand: 530 aktive `recherche`, ältester vom 27.07. · **🔴 seit 20.08.2026** (zuvor 🟢): `FEHLVERSUCHSPFAD-LOESCHT-HART`, `ZWEI-FRISTEN-7200-VERSCHIEDEN` offen |
| **Promotions-Queue in Redis** | 🟢 | `[Code]` | `QUEUE-SCHEMA-STALE` offen |
| **Kandidatenwahl + Aging** | 🟢 | `services/pixie/kandidaten.py` `[Code]` | `DISPATCH-SALIENZ-DEFAULT`, `UNREGISTRIERTER-AGENT-GEWINNT` offen |
| **Stapel + Zustellung** (Shadow Delivery) | 🔴 | `services/shadow_delivery.py` `[Code]` | `SHADOW-STACK-THEMA-LEER`, `ZUSTELLUNG-ABBRUCH-UNGEZAEHLT` offen · **🔴 seit 20.08.2026** (zuvor 🟢): `PROMPTAENDERUNG-OHNE-STAPELWIRKUNG` offen · `LAGEBILD-IMPULS-ALS-NUTZEREINGABE` **behoben** **geprueft 20.08.2026** — Salienz und KZG-Verdichtung haben einen eigenen Zweig für die Rolle `agent` |
| **Zustellungsfilter** (0,60 Kosinus) | 🔴 | `_stack_aehnliche_entfernen` `[Code]` | löscht den nächsten Gedanken zum selben Thema mit — die Gedankenkette ist die Abhilfe, sie ist nicht gebaut |
| **Eigenzeit E** (Zeitstempel am Zustand) | 🟢 | `[Doku]` · `[Code]` — `EIGENZEIT_*` in `config.py`, gelesen von `services/pixie/riegel.py` `[Erhebung 20.08.2026]` | — |
| **Eigenzeit F** (Session altert) | 🟢 | `[Doku]` · `[Code]` — `EIGENZEIT_*` in `config.py` `[Erhebung 20.08.2026]` | — |
| **Eigenzeit C** (Pausenfaktor) | 🟠 | gemessen: 48,7 h Pause → Faktor 0,0000 `[Doku, 17.08.]` · **Die Erhebung am 20.08.2026 fand keinen Bezeichner**: weder `PAUSE` noch `pausenfaktor` steht in `config.py` `[gemessen]` | benannte offene Kante: der Fall ohne Bezug |
| **Eigenzeit A** (Emotionsverfall über Zeit) | 🟢 | `[Doku]` · `[Code]` — `EIGENZEIT_*` in `config.py` `[Erhebung 20.08.2026]` | — |
| **Eigenzeit B** (Level im Eintrag) | 🟠 | gebaut `[Doku]` | wartet auf seinen **ersten Eintrag mit Level** |
| **Eigenzeit D** (Rad-Riegel) | 🟠 | Riegel 1 gebaut `[Doku]` | Riegel 2 nicht gerechnet; `RIEGEL-5-7-OHNE-EINTRAG` |
| **Selbstauslösung** (vierter Ausgang zurück in die Queue) | 🟠 | zweimal live gefeuert `[Doku, 16.08.]` · **Die Erhebung am 20.08.2026 fand keinen Bezeichner**: kein `selbstausloesung`/`selbst_ausloes` im Baum `[gemessen]` | Budget: drei je Turn für **alle** Gründe zusammen — vor dem zweiten Aufrufer braucht es getrennte Zähler |
| **Master-Switch `PIXIE_AKTIV`** | 🟢 | env-konfigurierbar `[Code]` | — |

---

## 9. Werkzeuge

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Zeitparser** (Fuzzy, Vektor-Modus, zwei Uhren) | 🟢 | `tools/`-Modul, 47 Tests `[Doku]` · `[Code]` — `utils/zeitparser.py` `[Erhebung 20.08.2026]` | `PARSER-NACKTE-UHRZEIT-FALSCHER-TAG` umgangen, Ursache extern; `ZEIT-EXTRAKTION-UNSCHARF` offen |
| **Web-Infrastruktur** (SearXNG + PageFetcher) | 🟢 | `ki_searxng` läuft seit 4 Tagen `[gemessen]` | — |
| **Auto-Fetch** (Suche → Seitenabruf) | 🟢 | `[Doku]` · `[Code]` — `tools/web/search.py` und `tools/web/fetch.py` `[Erhebung 20.08.2026]` | — |
| **Multi-Channel — Telegram** | 🔴 | `ki_telegram` läuft `[gemessen]` | — · **🔴 seit 20.08.2026** (zuvor 🟢): `TELEGRAM-NAMENSAUFLOESUNG-FAELLT-AUS` offen |
| **Multi-Channel — Matrix + WireGuard** | ⚫ | kein Code `[Code]` | alles |
| **Voice (TTS/STT)** | ⚫ | Vision `[Doku]` | alles |
| **Dateien — Schreibwerkzeug** | 🟢 | `tools/dateien/schreiben.py` `[Code]` | nur schreibend, für Novas eigene Bibliothek |
| **Dateien — Leseschicht** (Karte, Block, Fenster, Fundstelle) | 🔴 | `tools/dateien/operationen.py`, **35 Zeugen** · **erster Produktivaufrufer seit 18.08.2026**: `struktur_analysieren` füllt die Blockkarte des Index · seit 20.08.2026 **drei Ausgänge statt zwei** — erhoben / leer / `StrukturUnklarError` — und die Erkennung macht `markdown-it-py` statt eines Zeilenautomaten; am Bestand gemessen **174 / 0 / 0** · seit 20.08.2026 **alle fünf zugelassenen Formate**: Markdown über `markdown-it-py`, dazu eigene Erkenner für `.rst`, `.org`, `.adoc` und `.txt` als ausdrücklich leere Gliederung; an sechs echten `.rst`-Fremddateien gemessen, 24 Überschriften, 0 nicht erhoben `[gemessen]` | `block_lesen` liefert die Unterstreichung einer RST-Überschrift als erste Inhaltszeile mit (Fundliste 20.08.) · **🔴 seit 20.08.2026** (zuvor 🟢): `SETEXT-UNTERSCHRIFT-IM-BLOCK` offen |
| **Formzwang am Modellaufruf** (`expect_json` erreicht den Anbieter) | 🟢 | `services/llm_provider.py` + beide Worker, **5 Zeugen an zwei Nähten** · Gegenproben 2/2 und 1/1 rot · im Betrieb: Index von 155 auf **160 von 160**, **0 unbrauchbare Modellantworten** gegen 18 zuvor `[gemessen]` | der Anthropic-Weg erzwingt nicht — er meldet es (Werkzeugschema fehlt) |
| **Rückweg — Weg 3, der Verweis** (`wissen_verweis`) | 🟠 | `agents/wissen_rueckweg/` + Einreihpunkt in `agents/recherche/agent.py`, **15 Zeugen** · eigener Zuordnungs-Zettel, `bezug_id` hält die eigene Zeile aus der Kandidatenmenge · **sechster echter Lauf trifft**: Zeile 2022 `haeufigkeit` 1→2, `gewicht_roh` 1,0997, `verstaerkt_am` 09:46:50 — und **0 Dateien** unter `/knowledge` mit jüngerer Änderungszeit `[gemessen]` | die Kandidatenlandschaft bewegt sich zwischen Läufen (Fundliste 19.08.) · `VERWEISWEG-LEHNT-BESTEN-FALL-AB` **behoben** **geprueft 20.08.2026**: der Verweis-Weg hat seit dem 20.08.2026 einen eigenen Zuordnungs-Prompt, der den besten Fall als Bestätigung liest. **🟠 statt 🔴 und nicht 🟢** — die Wirkung des neuen Prompts ist im Betrieb ungemessen |
| **Dateien — Schreibschicht** (chirurgische Schnitte) | 🟢 | `tools/dateien/redaktion.py`, 20 Zeugen `[Code]` | — |
| **Dateien — Versionierung im Dokument** (`[cN>]`/`[dN>]`/`[iN>]`, Paarungsprüfung) | 🟢 | `tools/dateien/versionierung.py`, 20 Zeugen · Kette an echter Wissensdatei gefahren, 0 Befunde `[gemessen]` | — |
| **Dateien — Auftragsform `DATEI: {json}`** | 🟠 | `tools/dateien/hand.py`, 22 Zeugen `[Code]` — **weiterhin kein Aufrufer** | die Verdrahtung |
| **Wissensdatei — adressierbarer Block + Version** | 🟢 | `wissen_text_bauen` erzeugt `## AKTUELL` + `**Version:**` · **14 Dateien produktiv geschrieben** `[gemessen]` | — |
| **Ankertreue des Schreibmodells** | 🟢 | 30/30 zeichengenau und eindeutig, `gemma4-gpu` Median 1,7 s, `qwen36-cpu` 17,9 s `[gemessen]` | — |
| ~~**Dateien-Dienst — Stufe 0** (Einbettung gegen den Korpus prüfen)~~ | — | **entfallen** mit `novaberg-agent-dateien_k.md` v0.10 §3.0a-bis `[Doku]` | Die Schwelle ist keine Konstante mehr, sondern das Quantil `1 − K/N` der mitlaufenden Verteilung — es gibt keine einmalige Vermessung mehr, die vorher stattfinden müsste |
| **Dateien-Dienst — Stufe 1** (`dateien_wurzeln` + Freigabe) | 🟢 | `agents/dateien_wurzeln/`, 48 Zeugen · Tabelle steht, **Zeile 1 aus einem echten Turn**, **Zeile 2 ebenso am 20.08.2026**: `/docs`, Tor meldete 166 Dateien, `verifiziert=True` `[gemessen]` · Kette im Betriebslog von `Router: mgmt=agent/dateien_wurzeln` bis `verifiziert=True` `[gemessen]` | das **Vergessen** aus §2a.3 — es hat ohne Indextabelle keinen Gegenstand |
| **Dateien-Dienst — Stufe 2** (`dateien_index` + Wächter) | 🔴 | `agents/dateien_index/`, **31 Zeugen** (nachgezählt) · Erstlauf **3 Dateien in 16 s**, Blockkarten 50/21/32, zweiter Lauf 0 neu / 3 unverändert · **am 20.08.2026 über 160 Dateien gefahren**: vier Läufe, rund 30 s je Datei; zunächst 155 Zeilen und **5 still verloren**, nach der Fessel am Modellaufruf **160 von 160** und 0 unbrauchbare Antworten · die Bilanz trägt seither `gescheitert` samt Pfaden und rechnet `Kandidaten == indiziert + offen + gescheitert` nach `[gemessen]` | der **Takt** — `periodic_task()` ist None, bis die Änderungsrate gemessen ist · **🔴 seit 20.08.2026** (zuvor 🟢): `VERSCHWUNDEN-DURCH-FILTERWECHSEL`, `ARCHIVDATEI-OHNE-ETIKETT`, `DATEIINDEX-SPALTEN-OHNE-SCHREIBER` offen |
| **Dateien-Dienst — Stufe 3** (Enricher-Quelle, `[AUFZEICHNUNGEN]`) | 🟢 | `agents/dateien_index/aufzeichnungen.py`, seit 18.08. **zweikanalig**, 27 Zeugen · im Betrieb: scharfer Kanal 0,4879 und 0,4718, Fremdthemen 0 Treffer · **am 20.08.2026 an 174 Zeilen nachgemessen, 24 Sonden:** einschlägig Median 0,4293 gegen fremd 0,2519 — der Boden 0,30 **trägt**, elf von zwölf fremden Fragen erzeugen null Zeilen darüber, und der eine abgeschnittene richtige Fall wird vom scharfen Kanal geliefert `[gemessen]` | die **Quantilschwelle** (`AUFZEICHNUNGEN-QUANTIL`) · und der eigentliche Rest ist die **Rangfolge**, nicht die Schwelle (`EMBED-LISTE-DATEIENINDEX`) |
| **Die epistemische Grenze im Prompt** (`[AUFZEICHNUNGEN]` neben `[GEDAECHTNIS]`) | 🔴 | eigener Block, Fundstelle je Eintrag · **im Betrieb**: die Figur nannte in allen drei Punkten ihrer Antwort die Quelldatei, und der gespeicherte Kurzzeit-Eintrag trägt sie mit — 1 von 2908 Einträgen mit Dateipfad, über den Abruf als Gedächtniszeile zurückgeholt `[gemessen]` | ~~eine Absicht, keine Arbeit~~ → **entschieden am 18.08.2026: der Übergang ist gewollt, es wird kein Tor gebaut** (`novaberg-agent-dateien_k.md` §9 Punkt 10). Offen bleibt allein die **Rate**: Wie oft die Herkunft den Übergang überlebt, ist an einem Fall belegt und nicht gemessen · **🔴 seit 20.08.2026** (zuvor 🟢): `FUNDSTELLE-MIT-BEHAELTERPFAD` offen |
| **Zuordnung des Planners** (exakt vor unscharf) | 🔴 | `graph/nodes/planner.py::_manager_zu_target`, 8 Zeugen · Gegenprobe 4 vorhergesagt, 4 gezählt `[gemessen]` | — · **🔴 seit 20.08.2026** (zuvor 🟢): `ZUORDNUNG-NENNT-LISTENPOSITION` offen |
| **Dateien-Dienst — Stufe 4** (Auftragsweg mit Grep) | 🟢 | `agents/dateien/` samt Aufrufer (`plugins/dateien_manager/`, `klassifikation.py`, `agent.py`, `dispatch.py`, `auskunft.py`), 63 Zeugen · **echter Turn 18.08. 18:37 UTC**: scharfer Kanal 1 Treffer, Karte 7 Blöcke ohne Dateizugriff, Nadel 2 Fundstellen, und die Antwort trägt `/files/kzg-salienz.md` **und 0,67379** im selben Satz `[gemessen]` | die **Rückfrage** — der Dienst hat sie im Kanon und benutzt sie nicht; er ändert nichts, also gibt es nichts zu bestätigen |
| **Rückweg ins Wissen** (Gespräch → Wissensdatei, §4b) | 🔴 | `agents/wissen_rueckweg/`, 26 Zeugen · **zwei echte Läufe 18.08.**: einer ohne Schnitt mit Begründung (8 Kandidaten, bester Kosinus 0,3137), einer mit `[i1>]` zwischen Definition und Beleg, Version 1.0 → 1.1, Häufigkeit 1 → 2 `[gemessen]` | **zwei der drei Wege** — das Einprägsame (Schwelle 0,7 roh) und das Zugehörige sind nicht verdrahtet; dazu die Idempotenz: derselbe Fund zweimal eingereiht läuft zweimal, und nur der Aufruf verhindert die Dublette · **🔴 seit 20.08.2026** (zuvor 🟢): `RUECKWEG-OHNE-IDEMPOTENZ` offen |
| **Spur der Antwort** (`graph/antwort_spur.py`) | 🟢 | sechs Schreibstellen auf `state["response"]` laufen über einen Helfer, jede mit alter und neuer Länge im Protokoll · Anbieter-Umschlag mit `done_reason` **vor** jeder Zuweisung · AST-Riegel gegen Umgehung, mit Auslösefall · **10 Zeugen** · zwei echte Turns, Kette lückenlos `[gemessen]` | sie **meldet** den Verlust, sie **verhindert** ihn nicht — der Wiederholversuch bei leerer Antwort ist nicht gebaut |
| **Bibliothek als bestellbarer Dienst** (`wissen`, NMCP-Zettel + Dienst) | 🟢 | **Trefferqualität nachgewiesen** (19.08.2026 nachts): 37 von 40 Fragen finden ihre Ausarbeitung auf Rang 1 (92 %, zuvor 15 %), im Betrieb 3 Treffer bei Kosinus 0,730–0,629 — `plugins/wissen_manager/manager.py` (Zettel), `agents/wissen/` (Dienst), geteilte Abfrage in `AutonomousWissenRepository.suchen`, **26 Zeugen** · **zwei echte Turns 19.08. 12:41 und 12:43 UTC**: beide über den Empfang geroutet (`Match via target 'wissen' → wissen (exakt)`), einer in den **vierten Ausgang** (0 Treffer, Bestand 242, nächste Nähe 0,3084), einer **abgeschlossen** mit 5 Treffern `[gemessen]` | die **Schwelle trennt nicht** (siehe Zeile darunter); der Wortlaut der Datei fehlt — Stufe 2 ist nicht gebaut, und der Dienst sagt es in seiner `grenze` |
| **Retrieval der Bibliothek — ein Vektor je Thema** | 🔴 | **Gebaut, migriert und gemessen am 19.08.2026.** `autonomous_wissen_thema`, je Thema eine Zeile; **2443 Themenvektoren** über 559 Ausarbeitungen. Gegen den gebauten Lesepfad gemessen: **37/40 auf Rang 1** (Kosinus-Median 0,7612) gegen zuvor 6/40 und 0,2821 — der alte Median lag **unter** der damaligen Schwelle, die richtige Antwort wurde also im Regelfall verworfen. Schwelle 0,40 → **0,50** aus den Rohdaten: der höchste Wert, der noch keine richtige Antwort kostet. **Der Inhaltsvektor bleibt** — der Rückweg findet gegen ihn 25/25, gegen Themenvektoren 12/25, Überlappung der Top-8 im Median 1 von 8. Im Betrieb belegt: 3 Treffer bei 0,730–0,629 `[gemessen]` | **🔴 seit 20.08.2026** (zuvor 🟢): `BIBLIOTHEK-FINDET-SICH-SELBST` und `THEMENEMBEDDING-TRAEGT-DESTILLAT` offen · `BIBLIOTHEKSSCHWELLE-SORTIERT-FALSCH` **behoben** **geprueft 20.08.2026** — ~~die Schwelle ist übernommen, nicht gemessen~~ → sie ist am 19.08.2026 an 40 Fragen mit bekannter richtiger Antwort kalibriert, die Reihe steht in `config.py:478-499` |
| **Dateien-Dienst — Stufe 5** (Vertiefung) | ⚫ | `[Doku]` | **zuletzt**, hinter der Gedankenkette |
| **Außenrand der Freigaben** (erzwungen, nicht deklariert) | 🟢 | `agents/dateien_wurzeln/aussenrand.py` · Gegenprobe: Randprüfung ausgehebelt → **5 vorhergesagt, 5 rot** · im Betrieb `/files/../knowledge` → `/knowledge` abgewiesen · **seit 20.08.2026 zweiteilig** (`/files,/docs`), im laufenden Dienst als `['/files', '/docs']` abgelesen `[gemessen]` | — |
| **Rückweg der Rückfrage** (`dismissed`, Unklarheit fragt erneut) | 🟢 | `agents/dateien_wurzeln/resume.py` · Wortgrenzen statt Teilzeichenketten, im Betrieb nachgemessen `[gemessen]` | gilt nur für diesen Dienst; **drei Torwächter des Bestandes haben ihn weiterhin nicht**, und ihre Deutung ist als `ZUSTIMMUNG-GILT-ALS-ABLEHNUNG` offen |
| **Änderungserkennung über den Inhalt** (Hash statt Zeit) | 🟢 | `agents/dateien_index/wandern.py` · am Bestand belegt: gleiche Größe, gleiche `mtime`, anderer Inhalt → **erkannt**; Gegenprobe 2 vorhergesagt, 2 rot `[gemessen]` | — |
| **Verborgenes wird nicht betreten** (führender Punkt) | 🟢 | `agents/dateien_index/wandern.py`, **6 Zeugen** · Verzeichnis einmal mit Grund statt je Datei, verborgene Einzeldatei mit eigenem Grund vor der Endung · Gegenprobe zweifach: 4 vorhergesagt/4 rot und 3 vorhergesagt/3 rot · im Lauf danach `uebergangen 0`, `uebergangene_verzeichnisse 1` (`.obsidian`) `[gemessen]` | — |
| **Bibliothek — drei Kanäle** (`suchtext`, `entitaet_ids`, `timeline_id`, `stichwoerter`) | 🔴 | vier Spalten auf `autonomous_wissen`, DDL gezündet, Schema-Zeuge deckt sie `[gemessen]` | **kein Schreiber** — die Spalten sind die Vorbedingung, nicht die Umsetzung · **🔴 seit 20.08.2026** (zuvor 🟠): `ERSCHLIESSUNG-VERSTUEMMELT-STICHWORT` offen |
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
| **FaktenManager** | 🔴 | `[Code]` — aber **deaktiviert**, Speicher leer `[gemessen]` | Aktivierung erfordert die Lösung von `FAKTEN-RAUSCH` · **🔴 seit 20.08.2026** (zuvor 🔴): `FAKTENPLUGIN-OHNE-KAPPUNG` offen |
| **WissenManager** | 🟠 | `[Code]` | Stufe 2 „den Block lesen, der wirklich gebraucht wird" — **noch nicht gebaut** (`manager.py:9`). **Der Blocker ist seit dem 18.08.2026 weg, nicht die Lücke:** Die Leseschicht steht mit 26 Zeugen und hat zwei Produktivaufrufer — beide für die *freigegebenen Verzeichnisse*. Die Bibliothek öffnet weiterhin keine Datei; `dateipfad` geht nur als Fundstelle in den Text `[gemessen]` |

---

## 11. Client (GTK4)

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **WebSocket-Umbau** (alle Stufen über WS) | 🟢 | abgeschlossen Chat 124 `[Doku]` · `[Code]` — `api/websocket.py` `[Erhebung 20.08.2026]` | `WEBSOCKET-OHNE-KEEPALIVE` ✅ behoben 15.08. |
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
| **Tri-LLM + Connector-System** | 🔴 | `[Doku]` · Block 4 der MS-Welle abgeschlossen | — · **🔴 seit 20.08.2026** (zuvor 🟢): `OVERRIDE-NACH-CONNECTOR-STATT-MODELL` offen |
| **Model-Service-Schicht** (ChatWorker, BackgroundWorker, EmbedWorker) | 🟢 | `services/model_services/` `[Code]` | `SUBMIT-SYNC-BEHAUPTET-WORKER-THREAD` offen — zweimal live zugeschlagen |
| **Microservice-Modell-Queue** (Blöcke 1–5) | 🟢 | abgeschlossen Chat 97 `[Doku]` · `[Code]` — `services/model_services/` mit `worker_base`, `chat_worker`, `background_worker`, `embed_worker`, `registry` `[Erhebung 20.08.2026]` | — |
| **Embedding-Konsolidierung** (ein Pfad) | 🟢 | `[Doku]` · `[Code]` — `embed_text_bauen` in `services/wissensspeicher.py`, **60 Fundstellen** im Baum `[Erhebung 20.08.2026]` | `EMBED-DIMENSIONSCHECK-FEHLT` offen; Einbettungsmodell gegen Fachtexte **ungemessen** |
| **Health-Check** | 🟢 | `api/health.py`, rechnet den NMCP-Befund frisch `[Code]` | — |
| **Admin-API** (Pause/Resume/Flush) | 🟢 | `api/admin.py` `[Code]` | — |
| **Schema in `db/init.sql` + Agenten-`init.sql`** | 🔴 | 22 Tabellen definiert, **0 im Code benutzte Tabelle fehlt** `[gemessen]` | `LZG-MIGRATION-REVIEW-NICHT-IN-INIT`, `IDX-TIMELINE-TYPE-NICHT-IN-INIT` offen · **🔴 seit 20.08.2026** (zuvor 🟢): `LOESCHREGELN-DREIGETEILT` offen |

---

## 13. Prüfung und Werkzeugkette

| Feature | Ampel | Beleg | Rest |
|---|---|---|---|
| **Test-Suite** | 🔴 | 1.617 grün, 0 übersprungen `[Doku, 17.08.]` · `[gemessen]` — `Ran 2039 tests — OK`, 0 uebersprungen, am 20.08.2026 | meldet **gelegentlich rot und reproduziert nicht** — der Testname ist unbekannt · **🔴 seit 20.08.2026** (zuvor 🟠): `ZEUGE-FLACKERT-OHNE-REPRODUKTION` offen |
| **Linter-Nulllinie** (`ruff.toml`) | 🟢 | 2.147 geduldete Treffer `[Doku]` · `[Code]` — `novaberg/ruff.toml`, versioniert `[Erhebung 20.08.2026]` | — |
| **Harte Wand** (`ruff-hart.toml`) | 🟠 | **4 Familien** hart: `LOG`, `F821`, `W`-Auswahl, `N` `[Code]` | elf Familien unbewacht, bis sie leer sind |
| **Charakterisierungs-Netz** | 🟠 | `[Doku]` | — · **🟢 → 🟠 bei der Erhebung am 20.08.2026.** **Die Erhebung am 20.08.2026 fand keinen Zeugen**: unter 143 Testdateien traegt keine `charakterisier`, `netz` oder `golden` im Namen. Das Netz ist im Harness beschrieben und im Bestand nicht auffindbar. `[gemessen]` |
| **Kanalprüfung** (Deklaration gegen Leser) | 🟢 | 74 Felder geprüft, **0 tote Kanäle** `[gemessen]` | — |
| **Konfigurationsprüfung** (Konstante ohne Leser) | ⚫ | kein Werkzeug — **8 tote Konstanten** von Hand gefunden `[gemessen]` | `DATEILOG_AKTIV`, `EBBINGHAUS_DECAY_RATE`, `EBBINGHAUS_MIN_GEWICHT`, `EMOTIONALE_GRAVITATION_FAKTOR_SESSION`, `KZG_VERSTAERKUNG_DIVISOR`, `REDUCER_AKTIV`, `REDUCER_LOG_REMOVED`, `STIL_SESSION_GEWICHT` |
| **Schichtprüfung** (Importwurzel) | ⚫ | kein Werkzeug prueft die Schichtgrenze; am Bestand gezaehlt **39 Importe**, die eine ueberspringen `[gemessen]` · `IMPORTE-UEBERSPRINGEN-SCHICHT` offen | die Regel steht, die Wand fehlt. Neu aufgenommen bei der Erhebung am 20.08.2026 |
| **EVA-Sektionsprüfung** (leere Sektionsmarke) | ⚫ | **20 Sektionsmarken `Ausgabe-Verifikation`** ohne Pruefung darunter `[gemessen]` · `EVA-SEKTION-OHNE-PRUEFUNG` offen | eine Marke, unter der nur ein `return` steht, taeuscht eine Pruefung vor. Neu aufgenommen bei der Erhebung am 20.08.2026 |
| **Default-Prüfung** (Begleitfeld beim Vorgabewert) | ⚫ | **11 numerische Defaults** sehen aus wie Messwerte `[gemessen]` · `DEFAULTS-WIE-MESSWERTE` offen | ohne Begleitfeld ist ein Vorgabewert von einer Messung nicht zu unterscheiden. Neu aufgenommen bei der Erhebung am 20.08.2026 |

---

## 14. Was die Erhebungen nebenbei gefunden haben

### Erhebung vom 20.08.2026 — die zweite

**Der Auslöser war kein Zweifel an der Liste, sondern ein Umbau daneben:** Am selben Tag sind 168 rohe
Funde aus `novaberg-fundliste.md` klassifiziert worden, davon 70 als Defekt mit stabiler Kennung. **Erst
dadurch konnten sie überhaupt eine Ampel setzen** — eine Zeile in der Fundliste konnte das nie.

1. **74 offene Defektkennungen zeigten auf keine einzige Ampel.** 61 davon ließen sich einer Zeile
   zuordnen; **39 Zeilen wechselten die Farbe**, 30 von ihnen von 🟢. Die übrigen 13 Kennungen beschreiben
   Doku, Code-Norm oder Umgebung und sind keine Features — für drei davon ist stattdessen eine neue Zeile
   entstanden (§13).
2. **13 von 14 grünen Zeilen mit reinem `[Doku]`-Beleg nannten keinen einzigen Bezeichner.** Ihre Farbe
   war nicht nachrechenbar. Zwölf sind gegen den Code belegt worden; **zwei blieben ohne Fund und stehen
   jetzt auf 🟠** — die Fallenbatterie `B0` und das Charakterisierungs-Netz. Für beide gilt die genaue
   Aussage: Unter 143 Testdateien trägt keine den Namen; das ist eine Aussage über Namen, nicht über
   Existenz.
3. **Zwei Konstanten der Featureliste existieren im Code nicht unter dem Namen, den die Zeile nennt** —
   *Eigenzeit C (Pausenfaktor)* und *Selbstauslösung*. Beide standen ohne Herkunftsmarke da, und genau das
   war der Grund, warum es niemandem auffiel.
4. **Ein Feature war gebaut, wieder abgeschaltet und trug trotzdem keine Zeile:** die
   KZG-Liberalisierung mit Cluster-Promotion. Der Pfad ist seit Chat 98 tot, die drei Konstanten stehen
   weiter in `config.py` — und wurden in Chat 107 sogar nachkalibriert. Der Kommentar im Code sagt es
   selbst: *„Alt-Cluster-Pfad (deaktiviert seit Chat 98), trotzdem mitgezogen"*.
> **Die Gegenprobe der Erhebung lief in beide Richtungen und ist nachrechenbar.** Von 59 roten Zeilen
> nennen 45 eine offene Kennung; die übrigen 14 stehen aus einem der beiden anderen Gründe rot, die §2
> zulässt — gebaut und ohne Wirkung, oder es liest niemand. Umgekehrt setzen **9 der 76 offenen Kennungen
> bewusst keine Ampel**, weil ihr Gegenstand kein Feature ist: `KOPFZEILENZEIT-ALS-UTC-BESCHRIFTET`,
> `BEANTWORTETE-ABSICHT-STEHT-OFFEN`, `FRISTANGABE-WIDERSPRICHT-SICH`, `REPODOKU-VERWEIST-NACH-INNEN`,
> `CLIPBOARD-BEGRIFF-DOPPELT`, ~~`AGENTINPUT-NIE-EXISTIERT`~~, ~~`RIEGEL1-NACHZUG-UNVOLLSTAENDIG`~~,
> `PIXIE-NACHFRAGEN-FEHLT-IM-INDEX` und `VERSATZ-ZWEI-GROESSEN` betreffen Dokumentation oder Benennung.
> **Am 20.08.2026 nachgezogen:** Von diesen neun sind zwei behoben — es sind noch **sieben von 64**,
> nachdem der Durchgang durch alle 70 Kennungen zwölf davon geschlossen hat.
> **Die Zahl gehört hierher und nicht in eine Fußnote:** Ohne sie ist „keine Ampel" nicht von „übersehen"
> zu unterscheiden.

5. **Zehn Zeilen trugen gar keine Herkunftsmarke** und galten damit nach der eigenen Regel als nicht
   gesetzt. Alle zehn sind belegt oder als unbelegbar benannt.

> **Der Ertrag der Erhebung ist nicht die neue Zahl, sondern ihr Vorzeichen.** Die Liste stand auf 123 🟢
> und 19 🔴; sie steht jetzt auf 90 🟢 und 59 🔴. **Kein einziger Defekt ist heute entstanden** — sie waren
> alle schon da, nur an einer Stelle abgelegt, die keine Ampel setzen konnte.

### Erhebung vom 17.08.2026 — die erste

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

Nachgezaehlt in dieser Datei am 20.08.2026, nicht geschaetzt. Die Klammerwerte sind die der Erstaufstellung vom 17.08.2026.

```
Dokumente im Verzeichnis        154   (154)
davon Konzepte (*_k.md)          43   (44)
Zeilen mit Ampel                218   (194)

  gruen   fertig                 90   (103)
  orange  begonnen               32   (36)
  schwarz nicht begonnen         37   (37)
  rot     fehlerhaft             59   (18)

Belege [gemessen]                93   (72)
Belege [Code]                   118   (95)
Belege [Doku]                    36   (36)
Zeilen ohne Herkunftsmarke        0   (10)
```

Gezählt werden **nur Belege in Ampelzeilen** — die Marken im erklärenden Text zählen nicht mit. Eine Zeile kann mehrere Marken tragen; die Summe der drei Belegzahlen ist deshalb größer als die Zahl der Zeilen. Die Zählvorschrift steht hier, weil eine Zahl ohne sie beim nächsten Nachrechnen danebenliegt:

```
Ampelzeile  = eine Tabellenzeile, deren zweite Spalte genau eine der vier Farben trägt
```

**Die 36 `[Doku]`-Belege sind die Arbeitsliste der nächsten Erhebung** — sie sind die einzigen, die noch niemand gegen den Bestand gehalten hat. Ihr Anteil ist zugleich der Fälligkeitsanzeiger dieser Liste: Er wächst zwischen zwei Erhebungen von selbst.

**128 Zeilen stehen auf orange, schwarz oder rot.** Das ist die Menge der offenen Arbeit — 37 mehr als bei der Erstaufstellung, und der Zuwachs kommt fast vollständig aus den 39 Zeilen, deren Defekt bis heute in der Fundliste lag statt im Defektregister.

**Keine Zeile steht mehr ohne Herkunftsmarke.** Bei der Erstaufstellung waren es zehn; nach der eigenen Regel (§3) galt ihre Ampel damit als nicht gesetzt.

---

## Verlauf des Standes

Die Fortschreibung des Standes, aus der Kopfzeile geloest am 20.08.2026. Der Wortlaut jedes Eintrags ist unveraendert; vorangestellt ist allein sein Datum.

- **21. August 2026, 10:29 UTC** — **Keine Ampel wechselt, und eine Zeile bekommt eine Zahl, die sie vorher nicht hatte:** Die KZG-Abrufschwelle ist gemessen und steht auf 0,72 statt 0,40. Am Bestand vorher/nachher: zehn Fragen zu nie besprochenen Gegenstaenden lieferten 100 Eintraege, jetzt **0**; drei anaphorische Rueckfragen 30, jetzt **0**; drei einschlaegige Fragen 30, jetzt **30**. Die Zeile stand auf 🟢 und bleibt es — **das Bauteil tut jetzt, was die Ampel behauptet.**
- **21. August 2026, 09:43 UTC** — **Keine Ampel wechselt, und eine Zeile verliert ihren Vorbehalt:** Query Rewriting ist am 21.08.2026 fuer alle fuenf Leser des Suchschluessels gemessen, nicht mehr nur fuer die Bibliothek. 39 Sonden aus dem Bestand der Konsumenten selbst, durch ihren echten Lesepfad: rohe Aeusserung **0/39**, Rewrite **37/39**, Deckung mit der handaufgeloesten Referenz **39/39**. Die Zeile stand bereits auf 🟢 und bleibt es — **der Beleg traegt sie jetzt.**
- **20. August 2026, 19:36 UTC** — **Eine Ampel von 🔴 auf 🟠, sechs Zeilen nachgezogen: der Durchgang durch alle 70 Kennungen.** Zwoelf von ihnen sind behoben, keine davon von einem Auftrag, der sie kannte — vier am Responder-Prompt, zwei am Haltungsraum, zwei an der Bibliothek, zwei in der Doku, eine am Etikett des eigenen Gedankens, eine am Router-Prompt. **Nur eine Zeile wechselt die Farbe** (Rueckweg Weg 3, 🔴 -> 🟠: der Defekt ist fort, die Wirkung des neuen Prompts ungemessen); die uebrigen fuenf bleiben rot, weil neben der behobenen Kennung noch eine offene steht. Bestand danach: **91 gruen / 33 orange / 37 schwarz / 58 rot** `[gemessen]`.
- **20. August 2026, ~20:55 UTC** — **Eine Ampel neu auf 🟢: Query Rewriting.** Der Suchschluessel des Gedaechtnisses traegt seit heute den Gegenstand des Gespraechs, auch wenn der Turn ihn nur als Rueckbezug nennt. Gemessen vor dem Bau: rohe Aeusserung **0 von 10** ueber der Abrufschwelle, Rewrite auf Frageform **5 von 10**; Themenwechsel 3/3 sauber, fremde Verlaeufe 15/15 ohne Treffer. Im Betrieb belegt, Suite **2050 gruen**. Der erste echte Turn fand dabei einen Defekt, den zehn gruene Zeugen nicht sehen konnten: geratene Feldnamen in der Attrappe.
- **20. August 2026, ~19:30 UTC** — **Zweite Neuerhebung — 218 Zeilen, und 39 davon haben die Farbe gewechselt.** Anlass war die Klassifikation der Fundliste am selben Tag: 70 rohe Funde wurden zu Defekten mit Kennung, und **erst dadurch konnten sie eine Ampel setzen**. 74 offene Kennungen zeigten auf keine einzige; 61 liessen sich zuordnen. Die Liste steht jetzt auf **90 🟢 / 32 🟠 / 37 ⚫ / 59 🔴** gegen 103/36/37/18 bei der Erstaufstellung. **Kein Defekt ist heute entstanden** — sie lagen an einer Stelle, die keine Ampel setzen konnte. Dazu: fuenf neue Zeilen (darunter ein Feature, das gebaut, abgeschaltet und nie verzeichnet war), zwoelf gruene Zeilen erstmals gegen den Code belegt, zwei auf 🟠 zurueckgestuft, weil kein Zeuge auffindbar war, und **keine Zeile steht mehr ohne Herkunftsmarke** (zuvor zehn).
- **20. August 2026, ~18:45 UTC** — **keine Ampel bewegt, und das ist der Befund** — die Fundliste ist klassifiziert und leer: 168 Punkte, davon 70 als Defekt mit Kennung, 48 ins Backlog, 14 in Moduldokumente, 10 als Regel des Vorgehens, 5 als Nachtrag, 21 als erledigt. **Kein Feature beruehrt** — kein Fund ist umgesetzt, nur einsortiert. Was sich fuer diese Liste aendert, ist die Sichtbarkeit: Ein Defekt mit Kennung kann eine Ampel auf 🔴 setzen, eine Zeile in der Fundliste konnte das nie.
- **20. August 2026, ~17:05 UTC** — **keine Ampel bewegt, und das ist der Befund** — die Arbeit des Nachmittags war Doku: Die `Stand:`-Kopfzeilen von vier Registern trugen ihren eigenen Verlauf in *einer* Zeile (10.512 bis 34.263 Zeichen, zusammen 138 Glieder, alle vier mit unpaariger Klammerbilanz). Sie sind in den Koerper geloest, die laengste Kopfzeile misst jetzt 147 Zeichen. Kein Feature beruehrt: Ein Kopf traegt Felder, der Koerper den Verlauf.
- **20. August 2026, ~15:30 UTC** — **ein Defekt am Selbstbild, gefunden an ihren eigenen Antworten** — Nova sprach über ihre Dienste in der dritten Person („die Fachabteilung"), dreimal in einer Sitzung; der Wortlaut stand in ihrem Prompt, und der Datenteil trug die Instanz mit. Beide Hälften behoben, 5 Zeugen, Gegenprobe 2/2 — **im Betrieb ungemessen** (`NOVA-SPRICHT-VON-FACHABTEILUNG`). Suite **2037 grün**.
- **20. August 2026, ~14:15 UTC** — **die Antwortlänge hat drei Einflüsse statt einem, und die Haltung ihren zweiten Leser** — die Zeichenkorridore sind halbiert, die Länge der Äußerung deckelt sie bei rein leichten Intentionen, und der Verfasser bekommt die drei fachlichen Größen (`umfang`, `fragen`, `draengen`) im neuen Block `[MASS]`. Anlass: 12 Zeichen Gruß, 838 Zeichen Antwort. Durchgerechnet fällt derselbe Gruß auf 72–144, eine kurze Sachfrage nur auf 175–350. Suite **2032 grün**.
- **20. August 2026, ~13:55 UTC** — **dieselbe Ampel, und der Dienst versteht jetzt jedes Format, das er annimmt** — vier Erkenner statt einem, `.txt` ausdrücklich als leere Gliederung registriert statt als Lücke. An sechs echten `.rst`-Dateien aus installierten Paketen gemessen: 24 Überschriften, 0 nicht erhoben. Suite **2014 grün**.
- **20. August 2026, ~13:15 UTC** — **dieselbe Ampel, ein besserer Beleg** — die Gliederung von Markdown macht seit heute `markdown-it-py`; über den Bestand gegengerechnet liefern **174 von 174** Dateien dieselbe Karte wie der abgelöste Zeilenautomat, nachdem zwei von ihm verdeckte Fehlauszeichnungen behoben waren. Suite **2009 grün**.
- **20. August 2026, ~12:30 UTC** — **eine Ampel bleibt grün und bekommt eine Einschränkung, die vorher unsichtbar war** — die Blockkarte der Leseschicht lieferte für eine Datei mit unpaarigem Codezaun **5 von 83 Blöcken** und meldete das als gültiges Ergebnis. Seit heute sind *„nachgesehen, keine Gliederung"* und *„konnte nicht nachsehen"* zwei verschiedene Ausgänge; am Bestand gemessen: 174 Dateien, **173 erhoben, 0 leer, 1 nicht erhoben**. Dabei fiel eine zweite, noch unbetretene Lücke auf: Der Index lässt fünf Textformate zu und versteht eines. Suite **2004 grün**.
- **20. August 2026, ~09:45 UTC** — Fortführung: **eine Ampel müsste auf 🔴, und die Messung sagt auch, warum** — die Bibliothek als Enricher-Quelle trug in **142 beantworteten Nutzerturns zweimal** bei. Der Verdacht auf die Schwelle 0,50 ist gemessen und entlastet: Sie schneidet 9 von 10 richtigen ab, lässt aber 0 von 10 fremden durch, und die Verteilungen überlappen. Die Kontrolle stellt die Diagnose: Dieselbe Ausarbeitung steht auf **Themenhöhe auf Rang 1 (0,7375)** und auf **Inhaltshöhe auf Rang 142 (0,1768)** — die Schwelle ist an der falschen Paarung kalibriert.
- **20. August 2026, ~09:05 UTC** — **keine Ampel bewegt, und das ist der Befund** — ein vollständig gebauter Umbau am Vergleichsgegenstand des Dateienindex (Tabelle, Schreibweg, drei Lesewege, 1456 nachgebettete Vektoren) brachte gegen dieselben 24 Sonden **keine** Verbesserung: Rang 1 unverändert 8/12, Top 3 von 10 auf 9, bester Fremdtreffer von 0,3052 auf 0,4008. Zurückgebaut, Suite 2000 grün. Die Analogie zur Bibliothek trägt nicht: Dort standen mehrere Gegenstände in einem Feld, hier beschreiben Thema und Stichwörter denselben.
- **20. August 2026, ~08:40 UTC** — **beide Hälften des Vormittags-Vorfalls sind zu** — der Lauf sagt jetzt, was er verloren hat: `gescheitert` samt Pfaden neben `fehler`, und die Identität `Kandidaten == indiziert + offen + gescheitert` wird nachgerechnet statt unterstellt. Suite **2000 grün**.
- **20. August 2026, ~08:30 UTC** — **eine Schwelle ist belegt, statt übernommen — und der Fehler daneben ist keine Schwellenfrage** — 24 Sonden gegen 174 Indexzeilen: einschlägig Median 0,4293, fremd 0,2519, Lücke **0,177** gegen 0,038 am 18.08. Der Boden 0,30 trägt; der eine richtige Fall, den er abschneidet, kommt über den scharfen Kanal. Was bleibt, ist die Rangfolge: Ein Ziel **über** dem Boden bleibt hinter drei Nachbarn unsichtbar, weil der Vektor einer Indexzeile aus `thema` plus acht Stichwörtern entsteht — dieselbe Bauart, die die Bibliothek von 15 % auf 92 % gehoben hat, als sie fiel.
- **20. August 2026, ~08:20 UTC** — **eine Ampel neu auf 🟢, und sie repariert die Zahl der vorigen** — die Forderung nach JSON erreicht seit heute den Anbieter statt nur den eigenen Worker. Der Index steht damit auf **160 von 160** statt 155, mit **0 unbrauchbaren Modellantworten** gegen 18 an denselben Dateien zuvor; betroffen waren 31 Aufrufstellen. Dabei fiel eine Zusage, die zwei Behauptungen trug und bei beiden irrte: Der dokumentierte Guard existierte nicht, und die Unverträglichkeit von `think` und `expect_json` ist gegen beide Modelle widerlegt. Suite **1999 grün**.
- **20. August 2026, ~07:20 UTC** — **eine Ampel neu auf 🟢, und der Bestand hinter dem Dateien-Dienst ist über Nacht das Zwölffache** — `docs/` ist freigegeben, lesend eingehängt, und die Figur beantwortet eine Frage aus einem benannten Dokument mit Wert und Fundstelle im selben Satz (*„in der Datei `/docs/novaberg-salienz-berechnung_k.md` wird die Nabe mit dem Wert 0.9 definiert"*). 155 von 160 Dateien stehen mit Vektor im Index; die fehlenden fünf sind **kein Kappungsrest, sondern ein stiller Verlust** und stehen als `INDEXLAUF-VERSCHWEIGT-DATEIFEHLER` offen. Neu gebaut und zweifach gegengeprobt: Ein Verzeichnis mit führendem Punkt wird nicht mehr betreten. Suite **1993 grün**.
- **19. August 2026, ~20:40 UTC** — **zwei Ampeln auf 🟢, und beide tragen jetzt eine Zahl** — die Bibliothek findet: 37 von 40 Fragen nach *einem* Thema treffen ihre Ausarbeitung auf Rang 1 (92 %, zuvor 15 %), im Betrieb 3 Treffer bei Kosinus 0,730–0,629 gegen zuvor 5 Treffer in 32 Stunden. Gebaut ist Konvention 4: `autonomous_wissen_thema` mit 2443 Themenvektoren, beide Schreibwege angeschlossen, Schwelle 0,50 aus den Rohdaten. **Der Inhaltsvektor bleibt** — der Rückweg braucht ihn, gemessen 25/25 gegen 12/25. Ein Defekt dabei gefunden und behoben (`THEMENZEILEN-NUR-IM-INSERT-ZWEIG`), gefunden von der Gegenprobe über die Abweichung 12 vorhergesagt / 9 gezählt.
- **19. August 2026, ~19:10 UTC** — **eine Ampel geht auf 🟡, und eine rote stand am falschen Gegenstand** — die Bibliothek ist bestellbar, aber sie findet nicht: In **8 von 40** Fällen liegt die richtige Antwort auf Rang 1 (20 %), der beste Fehltreffer ist im Median ähnlicher als der richtige. **Das ist keine Schwellenfrage** — bei 0,40 werden gleichzeitig 50 % der richtigen verworfen und 80 % der Fehltreffer durchgelassen, und keine Zahl schafft beides. Ursache ist das Embedding-Ziel: `themen_embedding` trägt das Destillat (Ø 552 Zeichen) statt des Themas (Ø 110). Gegen ein Thema-Embedding sind es 39/40.
- **19. August 2026, ~18:30 UTC** — **keine Ampel bewegt, und das ist der Befund** — die Laufzeit ist von 0.20.7 auf 0.32.14 gehoben, zwölf Minor-Versionen, aber **kein Feature dieser Liste hängt daran**: Suite unverändert `Ran 1965 tests — OK`, ein echter Turn zugestellt, alle fünf Modelle mit unveränderten Digests. Der Kandidat `OLLAMA-VERSION-VIER-MONATE-ALT` ist damit abgearbeitet und **erklärt den Leer-Ausfall nicht** — die Nachmessung hat n=1 bis 5 je Aufrufer gegen n=30 bis 224 der Nulllinie und trägt keine Aussage über Besserung. Ein Vorgabewert kippte dabei: 0.32.14 schaltet Thinking per Default ein (`content=214, thinking=1467` ohne das Feld gegen `content=248, thinking=0` mit `think=false`); der Bestand sendet es unbedingt und ist nicht betroffen.
- **19. August 2026, ~19:45 UTC** — **die Angabe ist CEST und als UTC beschriftet**, der Commit dazu trägt `19:47:52 +0200`, also 17:47 UTC; die Uhrzeit dieser Kette läuft deshalb scheinbar rückwärts: **keine Ampel bewegt, und das ist der Befund** — der Abend ging in eine Untersuchung der Laufzeit statt in einen Bau. Mehrfachvorhersage als Erklärung der verlorenen Token **ausgeschlossen**; dafür ist die Laufzeit zwölf Minor-Versionen alt, und fünf Release-Einträge treffen Renderer und Parser. Die Nulllinie für das Update ist erhoben und wiederholbar.
- **19. August 2026, ~16:30 UTC** — **eine Ampel neu auf 🟢** — die tragende Variable des Antwortpfads hat seit heute eine Spur: sechs Schreibstellen, jede protokolliert, dazu die vollständige Anbieter-Antwort vor jeder Zuweisung. Anlass war ein Turn, der den Menschen nicht erreichte und nicht aufklärbar war.
- **19. August 2026, ~13:00 UTC** — **eine Ampel neu auf 🟢 und eine neue auf 🔴** — die Bibliothek ist seit heute **bestellbar**: Zettel am schwarzen Brett, Dienst dahinter, zwei echte Turns über beide Ausgänge. Das Rot daneben ist der Ertrag des vierten Ausgangs: Er hat in seinem **ersten** Lauf die Zahl geliefert, die zeigt, dass die übernommene Schwelle 0,40 an diesem Korpus falsch herum sortiert.
- **19. August 2026, ~13:20 UTC** — **keine Ampel bewegt, und das ist der Befund** — ein halber Tag Messung an EI-Kette, Kern-Hash und beiden Rädern hat sechs Fundlisten-Einträge, zwei Harness-Regeln und einen Backlog-Eintrag erzeugt und **keine Codezeile**. Drei entworfene Umbauten wurden gemessen und verworfen; im Blindvergleich dreier Prompt-Fassungen gewann der unveränderte Bestand. Beide Bestandszahlen nachgezählt: 178 Rad-Messungen, 34 Hash-Zeilen.
- **19. August 2026, ~11:00 UTC** — **keine Ampel bewegt** — die Rollenmatrix ist eine Aussage über die *Anbindung* der Silos, nicht über ihren Bauzustand; sie steht als vier Backlog-Einträge und als §6a der NMCP-Konvention.
- **19. August 2026, ~09:50 UTC** — **Der Verweis trifft** — sechster Lauf, Zeile verstärkt, keine Datei angefasst; und das Modell nahm **nicht** den nächsten Vektor.
- **19. August 2026, ~09:20 UTC** — **Der Verweis fragt jetzt seine eigene Frage** — eigener Zuordnungs-Zettel, und `shadow_auftrag.bezug_id` (angekündigte DDL) hält die gerade angelegte eigene Zeile aus der Kandidatenmenge; ohne sie hätte jedes Recherche-Ergebnis sich selbst verstärkt.
- **19. August 2026, ~08:15 UTC** — **Der Rückweg hat seinen zweiten Weg** — `wissen_verweis` verstärkt die zugeordnete Zeile, ohne die Datei anzufassen; der Recherche-Agent reiht ein, sobald ein Ergebnis mit Wissen abgelegt ist. **Der dritte Weg ist entfallen** statt gebaut: Seine Schwelle war die der Promotions-Queue.
- **19. August 2026, ~21:40 UTC** — **keine Ampel bewegt, und das ist der Befund** — behoben wurde `ZEUGE-ERWARTUNG-AUS-DER-UHR`, ein Defekt **am Messgerät**, nicht am Produkt: Kein Feature dieser Liste trug seinetwegen eine rote Ampel, weil er keine Funktion falsch machte, sondern die Suite unzuverlässig. Was sich geändert hat, steht deshalb hinter jeder Zeile statt in einer: Die Bilanzzeile, auf die sich jeder Beleg `[Code]` dieser Liste stützt, ist seit heute **10 von 10 Läufen** reproduzierbar statt 3 von 4.
- **19. August 2026, ~19:30 UTC** — **der Rückweg ins Wissen steht** — gemessen an zwei Läufen, einer ohne Schnitt und begründet.
- **19. August 2026, ~18:40 UTC** — **Stufe 4 ist vollständig** — der Aufrufer steht, und ein echter Turn nennt Fundstelle und Zahl im selben Satz.
- **19. August 2026, ~17:30 UTC** — Stufe 4 zur Hälfte, Stufe 3 **zweikanalig**, weil der Boden von vormittags am heterogenen Korpus fiel; eine Zeile neu für die Planner-Zuordnung
