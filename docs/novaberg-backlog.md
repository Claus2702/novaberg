# Novaberg — Backlog (Zukunftskonzepte)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Backlog — Konzipierte, noch nicht implementierte Features
**Stand:** 24. April 2026, Chat 63
**Pfad:** novaberg/docs/novaberg-backlog.md
**Quellen:** nova-08-k.md (Kognitive Anreicherung), nova-10-k-backlog.md (Skill-System), nova-01-t-c-backlog.md (Node-Konfiguration)

---

## 1. Kognitive Anreicherung (Epic 8)

Fuenf experimentell belegte Gedaechtniseffekte, die die Qualitaet der Enkodierung, des Abrufs und der Prioritaetssteuerung verbessern. Alle deterministisch, konfigurierbar und ohne zusaetzliche LLM-Calls — reine Embedding-Arithmetik und SQL.

**Leitprinzip:** "Berechnung in Python, nicht im LLM." Alle hier beschriebenen Effekte sind deterministisch, konfigurierbar und erfordern keine zusaetzlichen LLM-Calls. Reine Embedding-Arithmetik und SQL.

**Voraussetzung:** Telemetrie (TEL1). Ohne Messung ist Tuning Ratespiel. Alle Parameter in diesem Epic erfordern eine Instrumentierung, die zeigt, was passiert wenn man an einem Regler dreht.

### 1.1 Curiosity-Enhanced Memory (CEM)

> **Kognitionswissenschaftlicher Hintergrund:** Gruber, Gelman & Ranganath (2014), *Neuron*. PACE-Framework (Gruber & Ranganath 2019), *Trends in Cognitive Sciences*. Meliss et al. (2024), *Imaging Neuroscience*. Wenn Neugier geweckt wird, aktiviert das Gehirn das dopaminerge Belohnungssystem — VTA und Nucleus Accumbens schuetten Dopamin aus, das die Hippocampus-Aktivitaet verstaerkt. Die Folge: bessere Enkodierung ins Langzeitgedaechtnis. Entscheidend: Neugier verbessert nicht nur das Lernen von interessantem Material, sondern auch das von beilaeufig aufgenommenem, eigentlich irrelevantem Material in zeitlicher Naehe. Das PACE-Framework beschreibt den Mechanismus: Neugier wird durch signifikante Vorhersagefehler ausgeloest, die als Hinweis auf potenziell wertvolle Information bewertet werden. Berlyne (1960) unterschied epistemic curiosity (Wissensluecken) und perceptual curiosity (neue Reize).

Wenn ein KZG-Eintrag thematisch nahe an einer Entitaet mit hoher Resonanz liegt, erhaelt er einen Salienz-Boost:

```
effektive_salienz = basis_salienz + (entitaet_naehe × entitaet.resonanz × CEM_BOOST_FAKTOR)
```

`entitaet_naehe` = Cosine Similarity zwischen KZG-Eintrag-Embedding und naechstliegendem Entitaets-Embedding. Gilt fuer alle Entitaetstypen — ein Eintrag ueber Anna profitiert genauso wie einer ueber Astronomie. Wo: `graph/nodes/salience.py`, Python-Nachbearbeitung nach dem LLM-Call. Kein zusaetzlicher LLM-Call. Config: `CEM_BOOST_FAKTOR = 0.5`.

### 1.2 Testing Effect / Retrieval Practice (TE)

> **Kognitionswissenschaftlicher Hintergrund:** Roediger & Karpicke (2006), *Perspectives on Psychological Science*. Karpicke (2017), *Learning and Memory: A Comprehensive Reference*. Der Akt des Abrufens selbst — ohne Feedback oder erneutes Studium — produziert grosse Effekte auf das Lernen. Retrieval Practice staerkt Erinnerungen staerker als erneutes Lesen. Die Erklaerung: Beim Abruf werden neue semantische Assoziationen aktiviert (elaborative retrieval), die mit dem Zielgedaechtnis verknuepft werden und die Repraesentation anreichern.

Jeder erfolgreiche Abruf eines LZG-Eintrags durch den Enricher verstaerkt diesen Eintrag:

1. Enricher merkt sich abgerufene IDs: `state["lzg_abgerufen"] = [14, 27, 33]`
2. Dispatcher schreibt IDs in Redis: `reinforcement_queue:{user_id}`
3. Pixie fuehrt SQL-Update aus: `SET verstaerkt_am = NOW(), gewicht = gewicht + TE_BOOST`

`TE_BOOST = 0.10` — kleiner als bei expliziter User-Wiederholung (+0.40). Passiver Abruf ist schwaecher als aktives Wiederholen. Kein LLM-Call, reines SQL.

### 1.3 Zeigarnik-Effekt (ZE)

> **Kognitionswissenschaftlicher Hintergrund:** Zeigarnik (1927), *Psychologische Forschung*. Erinnerungen an unterbrochene, unerledigte Aufgaben sind staerker als Erinnerungen an abgeschlossene. Eine angefangene Aufgabe baut eine aufgabenspezifische Spannung auf (Kurt Lewins Feldtheorie: "Quasi-Beduerfnis"), die die kognitive Zugaenglichkeit verbessert. In Zeigarnik's Experimenten konnten Probanden unterbrochene Aufgaben ca. 90% besser erinnern als abgeschlossene. Verwandt: Der Ovsiankina-Effekt (1928) — Probanden neigen dazu, unterbrochene Aufgaben von sich aus wieder aufzunehmen.

Der Zeigarnik-Effekt wird ueber die `arousal`-Dimension auf Entitaeten abgebildet:

1. User erwaehnt Thema → Arousal startet bei 0.6
2. Pixie arbeitet daran → Arousal sinkt um 0.2
3. Pixie liefert Ergebnis per Delivery → Arousal sinkt nochmal
4. **Pfad A:** User greift es auf → Arousal steigt, neuer Zyklus
5. **Pfad B:** User ignoriert es → Arousal faellt weiter → 0.0, Thema ruht

Das "erledigt"-Gefuehl entsteht organisch: die Spannung baut sich ab, weil niemand das Thema nachfragt. Nicht als Salienz-Boost (Speicherung), sondern als Themen-Arousal (Pixies Arbeitspriorisierung).

### 1.4 Von-Restorff-Effekt / Isolationseffekt (VRE)

> **Kognitionswissenschaftlicher Hintergrund:** Von Restorff (1933), *Psychologische Forschung*. Hunt & Lamb (2001), *Journal of Experimental Psychology*. Elhalal, Davelaar & Usher (2014), *Frontiers in Human Neuroscience*. Wenn mehrere homogene Stimuli praesentiert werden, wird der Stimulus, der sich vom Rest unterscheidet, besser erinnert. Erklaerungen: Gestalt (aehnliche Stimuli verschmelzen), Interferenz (Isolation reduziert Interferenz), Aufmerksamkeit (isolierte Items erhalten mehr Aufmerksamkeit). Neuroimaging zeigt Korrelation mit praefrontalem Cortex.

Wenn ein KZG-Eintrag thematisch stark vom bisherigen Gespraechskontext abweicht:

```
kontext_embedding = durchschnitt(letzte_N_session_turn_embeddings)
abweichung = 1.0 - cosine_similarity(neuer_eintrag, kontext_embedding)
if abweichung > VRE_SCHWELLWERT:
    salienz_boost = abweichung × VRE_BOOST_FAKTOR
```

Wo: `graph/nodes/salience.py`, parallel zum CEM-Boost. Kein LLM-Call, reine Embedding-Arithmetik. Config: `VRE_SCHWELLWERT = 0.6`, `VRE_BOOST_FAKTOR = 0.3`.

### 1.5 Memory Reconsolidation (MR, aktiv)

> **Kognitionswissenschaftlicher Hintergrund:** Nader, Schafe & LeDoux (2000), *Nature*. Lee, Nader & Schiller (2017), *Trends in Cognitive Sciences*. Haubrich & Nader (2016), *Current Topics in Behavioral Neurosciences*. Konsolidierte Erinnerungen koennen nach dem Abruf erneut in einen instabilen Zustand uebergehen, in dem sie modifiziert werden koennen, bevor sie rekonsolidiert werden. Neuere Forschung interpretiert Rekonsolidierung als "Updating Consolidation" — ein Mechanismus, durch den aktualisierte Erfahrungen in das Langzeitgedaechtnis integriert werden.

Das bi-temporale Modell existiert bereits (passiv). Was fehlt: der bewusste Trigger "Abruf + Widerspruch im selben Kontext":

1. Enricher markiert abgerufene LZG-Eintraege im State
2. Salienz erkennt Widerspruch zu einem abgerufenen Eintrag
3. Promotion invalidiert den alten Eintrag und erzeugt den neuen

Kann in den bestehenden Promotion Call 2 integriert werden (zusaetzliches Feld: `widerspricht_bestehendem: true/false`).

### 1.6 Themen-Modell: Resonanz und Arousal

Zwei neue Spalten auf der Entitaeten-Tabelle:

| Dimension | Steuert | Tempo | Speicher |
|-----------|---------|-------|----------|
| **Salienz** | Wie wichtig ist diese Info fuers Gedaechtnis? | Pro Turn | KZG/LZG-Gewicht |
| **Resonanz** | Wie stark springt das System bei dieser Entitaet an? | Wochen/Monate | `entitaeten.resonanz` |
| **Arousal** | Wie aktiv beschaeftigt sich das System damit? | Stunden/Tage | `entitaeten.arousal` |

Resonanz = Langzeitbedeutung (Anna ist wichtig, Astronomie ist spannend). Arousal = Arbeitsgedaechtnis-Aktivierung (die offene Frage ueber Schwarze Loecher). Gilt fuer alle Entitaetstypen (Personen, Orte, Themen, Organisationen).

> **Kognitionswissenschaftlicher Hintergrund:** Die Unterscheidung zwischen Resonanz und Arousal entspricht der Trennung von semantischer Relevanz und Arbeitsgedaechtnis-Aktivierung in der kognitiven Psychologie. Alan Baddeley's Modell des Arbeitsgedaechtnisses (1974) beschreibt eine zentrale Exekutive, die Items nach Relevanz aktiviert und deaktiviert. Novas Arousal-Dimension bildet diesen Mechanismus ab.

```sql
ALTER TABLE entitaeten
    ADD COLUMN IF NOT EXISTS resonanz FLOAT,
    ADD COLUMN IF NOT EXISTS arousal FLOAT;
```

### 1.7 Traum-Modus

Wenn Pixies Shadow-Queue leer ist und keine Promotion ansteht, geht Pixie nicht in Idle, sondern in den **Traum-Zustand**. Pixie nimmt das Thema mit der hoechsten Arousal und assoziiert frei — qualitativ anders als Recherche (konkreter Trigger) oder Vertiefen (konkreter KZG-Eintrag). Es ist assoziatives Wandern — der kreative Modus, der beim Menschen die besten Ideen produziert.

Serendipity-Slot: Manchmal nimmt Pixie nicht das Top-Arousal-Thema, sondern ein Nebenthema. Pixie waehlt 3 Aufgaben: 2 Slots nach Arousal sortiert (hoechste zuerst), 1 Slot gewuerfelt aus den restlichen (der "Serendipity-Slot"). Verhaeltnis konfigurierbar (`SERENDIPITY_RATIO = 0.33`).

Neuer Pixie-Task: `traeumen` — niedrigste Prioritaet, laeuft nur wenn sonst nichts ansteht (Queue leer, keine Promotion, kein Dirty-Flag). Ergebnisse landen auf dem Shadow-Stack.

### 1.8 Konfigurierbare Parameter

| Parameter | Default | Beschreibung |
|-----------|---------|-------------|
| `CEM_BOOST_FAKTOR` | 0.5 | Salienz-Multiplikator fuer Themen-Affinitaet |
| `TE_BOOST` | 0.10 | Gewichts-Boost pro erfolgreichem Enricher-Abruf |
| `VRE_SCHWELLWERT` | 0.6 | Ab welcher Kontext-Abweichung der Isolationsbonus greift |
| `VRE_BOOST_FAKTOR` | 0.3 | Salienz-Multiplikator fuer Isolation |
| `RESONANZ_INKREMENT` | 0.05 | Resonanz-Steigerung pro thematischem KZG-Eintrag |
| `RESONANZ_DECAY_RATE` | 0.0003 | Verfall der Resonanz (5x langsamer als Ebbinghaus) |
| `AROUSAL_INKREMENT` | 0.2 | Arousal-Steigerung bei Erwaehnung |
| `AROUSAL_DEKREMENT_ARBEIT` | 0.2 | Arousal-Senkung nach Pixie-Bearbeitung |
| `AROUSAL_DEKREMENT_TAG` | 0.1 | Arousal-Senkung pro Tag ohne Kontakt |
| `SERENDIPITY_RATIO` | 0.33 | Anteil zufaelliger Themen in Pixies Queue (1 von 3) |

### 1.9 Implementierungsreihenfolge

```
0. TEL1 — Telemetrie-Infrastruktur (Blocker)
1. DB-Schema: resonanz + arousal auf entitaeten
2. Themen-Entitaeten: Manuelle + automatische Entstehung
3. CEM: Salienz-Boost in salience.py (Embedding-Arithmetik)
4. TE: Enricher-Abruf → reinforcement_queue → Pixie SQL-Update
5. VRE: Isolationsbonus in salience.py (Session-Kontext-Vergleich)
6. ZE: Arousal-Dynamik in Pixie (steigern/senken)
7. MR: Widerspruchs-Trigger in Promotion Call 2
8. Traum-Modus: Neuer Pixie-Task 'traeumen'
9. Themen-Erkennung: Pixie-Task fuer automatische Cluster-Erkennung
```

Schritte 1-5 sind unabhaengig implementierbar. Schritte 6-9 bauen auf dem Themen-Modell (1-2) auf.

### 1.10 Bereits implementiert (Referenz)

| Effekt | Quelle | Nova-Implementierung | Dokument |
|--------|--------|---------------------|----------|
| Ebbinghaus-Vergessenskurve | Ebbinghaus 1885 | Exponentieller Decay, konfigurierbare Rate | novaberg-pixie-decay.md |
| Spacing Effect | Distributed Practice | KZG-Verstaerkung bei Wiederholung | novaberg-mem-kzg.md / novaberg-pixie-kzg.md |
| Emotionale Salienz | Plutchik 1980, Russell 1980 | Arousal (0.0-1.0), 9 Emotions-Vektoren | novaberg-node-perception.md |
| Default Mode Network | Raichle et al. 2001 | Pixie als Hintergrundprozess | novaberg-pixie.md |
| Konsolidierung | McGaugh 1966, Dudai 2004 | KZG→LZG Promotion (Zwei-Call) | novaberg-pixie-promotion.md |
| Memory Reconsolidation (passiv) | Nader et al. 2000 | Bi-temporales Modell | novaberg-mem-knowledge-graph.md |

### 1.11 Quellen

1. Gruber, M.J., Gelman, B.D., & Ranganath, C. (2014). States of curiosity modulate hippocampus-dependent learning via the dopaminergic circuit. *Neuron*, 84(2), 486-496.
2. Gruber, M.J. & Ranganath, C. (2019). How Curiosity Enhances Hippocampus-Dependent Memory: The PACE Framework. *Trends in Cognitive Sciences*, 23(12), 1014-1025.
3. Roediger, H.L., III & Karpicke, J.D. (2006). The Power of Testing Memory. *Perspectives on Psychological Science*, 1(3), 181-210.
4. Karpicke, J.D. (2017). Retrieval-Based Learning: A Decade of Progress. In *Learning and Memory: A Comprehensive Reference* (2nd ed.).
5. Zeigarnik, B. (1927). Das Behalten erledigter und unerledigter Handlungen. *Psychologische Forschung*, 9, 1-85.
6. Von Restorff, H. (1933). Ueber die Wirkung von Bereichsbildungen im Spurenfeld. *Psychologische Forschung*, 18, 299-342.
7. Hunt, R.R. & Lamb, C.A. (2001). What causes the isolation effect? *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 27(6), 1359-1366.
8. Elhalal, A., Davelaar, E.J., & Usher, M. (2014). The role of the frontal cortex in memory: An investigation of the Von Restorff effect. *Frontiers in Human Neuroscience*, 8, 410.
9. Nader, K., Schafe, G.E., & LeDoux, J.E. (2000). Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval. *Nature*, 406, 722-726.
10. Lee, J.L.C., Nader, K., & Schiller, D. (2017). An update on memory reconsolidation updating. *Trends in Cognitive Sciences*, 21(7), 531-545.
11. Haubrich, J. & Nader, K. (2016). Memory Reconsolidation. In *Current Topics in Behavioral Neurosciences*.
12. Meliss, S. et al. (2024). Broad brain networks support curiosity-motivated incidental learning. *Imaging Neuroscience*, MIT Press.

---

## 2. Skill-System (Epic 10)

Nova lernt im Gespraech, wie sie bestimmte Aufgaben ausfuehren soll. Der User erklaert eine Faehigkeit, Nova abstrahiert daraus einen wiederverwendbaren Skill-Prompt, den sie bei zukuenftigen Auftraegen automatisch anwendet.

**Drei Instruktionsebenen:** Direktive (Verhaltensanweisung, dauerhaft, Ebbinghaus-Decay), Skill (Ausfuehrungsanweisung, persistent, kein Decay) und Auftrag (konkreter Befehl, einmalig, Session). Direktive formt das Wie, Skill definiert das Koennen, Auftrag ist das Was.

**Lebenszyklus:** Erstellen (User erklaert, Salienz erkennt Lehrsequenz, LLM destilliert Skill-Prompt) → Anwenden (Enricher findet Skill ueber Trigger-Match, injiziert in Kontext) → Verfeinern (Update zu bestehendem Skill, versioniert) → Loeschen (Soft-Delete).

**Architektur:** SkillManager als Plugin im Plugin-System (BaseManager, Auto-Discovery). Datenmodell: `skills`-Tabelle mit Name, Trigger-Keywords, Skill-Prompt, Version. Trigger-Matching: aktuell Keyword-basiert, spaeter moeglicherweise Embedding-basiert.

**Offene Fragen:** Skill-Konflikte bei Mehrfach-Match, Qualitaet der Destillation durch 24B-Modell, Meta-Skills (rekursives Lernen).

### Erweiterung: Code-Skills via Claude API (Chat 45)

Neben Prompt-Skills (Typ 1: Ausführungsanweisungen, Prompt-Injection) ein zweiter Skill-Typ:

**Typ 2: Code-Skills** — Nova sammelt Wissen, baut Spezifikation, beauftragt Claude API mit Code-Generierung, testet und registriert als Tool.

Beispiel-Flow:
```
User: "Bau mir einen Skill für meine Hue-Lampe"
Novaberg (lokal, Gemma 4): Sammelt Anforderungen, recherchiert Hue API
Nova: Reichert Spezifikation mit gesammeltem Wissen an
Novaberg → Claude API: "Generiere ein Python-Skript nach dieser Spec"
Claude API → Novaberg: Fertiger Code
Novaberg (lokal): Testet, registriert als Tool
Ab jetzt: "Mach das Licht an" → Nova ruft hue_skill.py auf
```

Nutzt den bestehenden AnthropicProvider. Traffic und Kosten gering (2-3 API-Calls pro Skill, Sonnet 4.6, wenige Cent).

**Voraussetzungen:** ProjektAgent (Wissen ablegen + Spec bauen), Recherche + Vertiefen (Wissen sammeln), Reasoning (Strategie + Ziel formulieren).

**Verbindung aller Epics:** Recherche → Dateien → Vertiefen → Spec → Claude API → Skill. Der ProjektAgent ist das Fundament.

---

## 3. Node-Konfiguration (TEMP1)

Jeder der 10 Nodes im HumanGraph wird ueber `config.py` konfigurierbar: Temperature, Sampling-Parameter, System-Prompt-Templates mit Platzhaltern (`{today}`, `{user_name}`), max_output_tokens. Zwei Nodes ohne LLM-Call (Enricher, Dispatcher) haben Datenzugriffs-Parameter.

**Empfohlene Temperatures:** Perzeption 0.05 (reine Klassifikation), Router 0.05, Salienz 0.05 (niedrigste — Kreativitaet = halluzinierte Fakten), Planner 0.2, Responder 0.7 (hoechste — natuerliche Sprache), Thinker 0.15, Tribunal 0.2, Corrector 0.5.

**Ollama-spezifisch:** repeat_penalty (1.1 fuer Responder), presence_penalty (0.3), top_p (0.9) — direkte Bekaempfung repetitiver Patterns auf Modell-Ebene.

**Pixie-Tasks:** Eigene Config-Struktur (PIXIE_TASK_CONFIG) mit Temperature und max_output_tokens pro Agent.

---

## 4. Entity-First-Retrieval (Epic 16)

Aktuell basiert der Gedaechtnis-Abruf auf Embedding-Suche (Cosine Similarity). Entity-First-Retrieval dreht die Reihenfolge um:

1. **Graph-Query zuerst:** Entitaet im Prompt identifizieren, Knowledge Graph nach verbundenen Fakten abfragen.
2. **Disambiguierung:** Bei mehreren Treffern (z.B. "Anna" als Person vs. Filmtitel) kontextbasiert aufloesen.
3. **Fallback auf Websuche:** Bei 0 Treffern im Graph automatisch Web-Recherche triggern.

Vorteil: strukturiertes Wissen wird bevorzugt, Embedding-Suche ergaenzt bei unscharfen Anfragen. Drei Roadmap-Punkte: 16a (Konzept), 16b (Disambiguierung), 16c (Fallback).

---

## 5. MCP-Architektur (Vision)

Langfristige Vision: Agenten als MCP-Server (Model Context Protocol) in Docker-Containern, Novaberg als MCP-Client. Jeder Agent wird ein eigenstaendiger Service mit definierter Schnittstelle — unabhaengig deploybar, testbar und austauschbar. Das wuerde die Grenze zwischen lokalen Agenten und externen Diensten aufloesen: ein RechercheAgent koennte lokal oder als Remote-Service laufen, mit identischer Schnittstelle.

---

## 6. Voice (TTS/STT)

Der naechste Schritt in der Kommunikationsbandbreite: Spracheingabe (Speech-to-Text) und Sprachausgabe (Text-to-Speech). Voice wuerde die natuerlichste Form der Interaktion ermoeglichen — ein Gespraech statt Texteingabe. Voraussetzung: die emotionale Intelligenz muss in der Sprachausgabe ankommen (Tonlage, Tempo, Pausen entsprechend Arousal und Emotions-Vektor). Konzept steht noch aus.

---

## 7. Offene Epics & Features

### Gesprächsvektor (Epic 9, offen)
| # | Thema | Status |
|---|-------|--------|
| GV3 | Invertierte Perzeption (Ziel → benötigter Modus) | ⬜ |
| GV4 | Wissens-Lücken via Embedding-Nachbarschaft | ⬜ |
| GV5 | Vektor-Typen (explizite Erkennung) | ⬜ Implizit durch Farbtöne abgedeckt |
| GV6 | Pixie-Vorbereitung (Vektor im Hintergrund vorbereiten) | ⬜ Nach VertiefungsAgent v2 |

### Domain-Language-Normalisierung (Epic 15, 4/6)
| # | Thema | Status |
|---|-------|--------|
| 15e | FaktenAgent (Salienz-Pipeline) | ⬜ |
| 15f | DateienAgent (geplant) | ⬜ |

### Pixie-Erweiterung (Epic 5, offen)
| # | Thema | Status |
|---|-------|--------|
| PIX-MIG-6 | VertiefungsAgent | ⚠️ Konzept (novaberg-pixie-deepdive_k.md) |
| PIX-MIG-7 | NachfragenAgent | ⬜ Queue-basiert, emotionale Rückfrage |
| PIX-MIG-8 | AufraeumAgent | ⬜ Duplikate, verwaiste Entitäten |
| PIX-CLEAN | Alter Runner entfernen | ⬜ services/shadow_agent/ + BaseTask |
| PIX-GRAPH | PixieGraph | ⬜ Router → Agent-Dispatch → Agent (CPU) → Salienz → Dispatcher |
| PIX-STATUS | Pixie-Statusleiste | ⬜ Zeigt aktiven Agenten statt nur "idle" |
| PIX-FALLBACK | Queue-Fallback bei Fehler | ⬜ Offset +1 nach Dispatch-Fehler |
| SA2–SA4 | Charakter-basierte Priorisierung | ⬜ Multiplikator auf Queue-Priorität |
| PIX-LLM-ROUTER | LLM-Router für Pixie | ⬜ Ersetzt regelbasierten Router |

### Client & Visualisierung
| # | Thema | Status |
|---|-------|--------|
| CLIENT-RENDER | GTK4 + WebKitGTK Chat-Rendering (Markdown + Emojis nativ) | ✅ Chat 56 |
| Oktagon-Radar | 8-Sektor-Radar im Emotions-Panel (Cairo, 2× nebeneinander) | ✅ Chat 56 |
| Konfig-Panel | Schieberegler für Config-Parameter | ⬜ |
| Restliche Panels | Fakten, Pixie-Monitor, PostgreSQL, Redis, Logs | ⬜ |
| Emotionen (Turns) | Turn-reaktives Emotions-Panel (SSE-Event-basiert) | ⬜ |

### Kommunikation
| # | Thema | Status |
|---|-------|--------|
| Überakkommodation | CAT empirisch testen | ⬜ |
| PENDING-RELEVANZ | Router prüft nicht ob Prompt Antwort auf Rückfrage | ⬜ Chat 43 |
| KORR1 | Korrektur-Erkennung bei fehlgeschlagenen Aktionen | ⬜ Chat 43 (niedrig) |
| ROUTE-MISS1 | Router erkennt kontextabhängige Aufträge nicht | ⬜ Chat 48, strukturell adressiert durch Enricher-vor-Router (Chat 59, implementiert). Offen für Validierung. |
| 5i | Zeitparser: Fränkisch + Norddeutsch | ⬜ |

### Infrastruktur
| # | Thema | Status |
|---|-------|--------|
| TEL1 | Telemetrie (Metriken + Dashboard) | ⬜ Blocker für Feintuning |
| TOK1 | Token-Budget-Management | ⬜ |
| LLM1b | LLM-Abstraktion verfeinern (3-Schichten) | ⬜ |
| E2 | Fakten-Konfidenzwert bei Widersprüchen | ⬜ |
| E3 | Kontextnormalisierung (Negationen, temporäre Zustände) | ⬜ |
| E4/E5 | LZG-Verdichtung durch Pixie | ⬜ |
| D9 | Burst-Deduplizierung (KZG-Klebrigkeit) | ⬜ |
| TEST1 | Testumgebung vervollständigen | ⚠️ Phase 0+4 fehlen |

### DateienAgent / ProjektAgent (Chat 45)

Aufspaltung des DateienAgenten in zwei Agenten mit unterschiedlichen Abstraktionsebenen:

**DateienAgent** — niedrige Ebene, CRUD für Dateien:
- Datei erstellen, lesen, suchen, aktualisieren, löschen
- Embedding-basierte Suche über Dateiinhalte
- Flach, keine Struktur-Annahmen

**ProjektAgent** — hohe Ebene, orchestriert Dateien:
- Projekt anlegen = Ordner + Meta-Datei (`_meta.md` mit Ziel, Status, Kontext)
- Dateien einem Projekt zuordnen
- Projektstatus verwalten (aktiv, pausiert, abgeschlossen)
- Projekt-Kontext als Block für Responder oder Claude API bereitstellen
- Automatisch Recherche-Ergebnisse dem richtigen Projekt zuordnen

ProjektAgent nutzt DateienAgent als Infrastruktur (Separation of Concerns). ProjektAgent ist das Fundament für Skill-Generierung, Recherche-Ablage und autonome Problemlösung.

---

### Fachabteilungs-Agenten (Epic, Chat 49)

**Vision:** Agenten sind keine CRUD-Masken mit LLM-Wrapper, sondern **Fachabteilungen mit Intelligenz**. Sie prüfen Input gegen den Bestand, erkennen Widersprüche, verweigern Unsinn, fragen differenziert zurück, und validieren ihre Ausgaben semantisch bevor sie zurückmelden.

**Leitmetapher:** "Wenn die Anweisung kommt: 3 + 4 = 9, dann muss die Fachabteilung sagen: Uhm... sorry, aber das stimmt so nicht!"

**Neue generische Agent-Pipeline:**
```
Input-Validation → Semantik-Check → HITL-Gate → CRUD → Output-Validation → Antwort
```

Zwei neue Nodes pro Agent:
- **Semantik-Check (Input):** Prüft Kompatibilität der gewünschten Operation mit aktuellen Daten. Klassifiziert: Widerspruch, Ergänzung, Redundanz, identisch. Formuliert differenzierte Rückfrage.
- **Output-Validation:** Prüft nach CRUD, ob das Ergebnis semantisch Sinn macht (z. B. abfängt CRUD-DESTILL-SUBTRAKT — "Nicht mehr das kleine Mädchen sein" als Anweisung → unsinnig → zurück zum Classify).

**Differenzierte Rückfrage-Typen** (statt einfachem Ja/Nein):
- Widerspruch: "Das neue X passt nicht zum aktuellen Y. Soll ich Y deaktivieren?"
- Ergänzung: "Ich bin dann X und Y, passt das?"
- Redundanz: "Das habe ich im Kern schon. Zusammenführen?"

**Beseitigt strukturell:**
- CRUD-REACTIVATE-COEXIST (Semantik-Check fängt Widersprüche ab)
- CRUD-DESTILL-SUBTRAKT (Output-Validation erkennt unsinnige Destillation)
- Vermutlich ähnliche Fälle in DirektivenAgent, NotizenAgent, TimelineAgent

**Betrifft:** CharakterIdentitaetAgent, DirektivenAgent, NotizenAgent, TimelineAgent (gemeinsame Infrastruktur in `agents/crud_validation.py`)

**Voraussetzung:** ✅ RESUME-REJECT gelöst (Chat 50). Phase 0 abgeschlossen — Resume-Node mit Strategy-Hook implementiert.

**Inspiration:** OpenClaw, Agentic Workflows (2026-Standard für Agent-Design). Eine Aufgabe erhalten, Input normalisieren, prüfen/validieren, gegen DB verarbeiten, Ausgabe semantisch validieren, Antwort zurückgeben — gerne mit mehreren Rücksprachen.

**Konzept-Dokument:** `novaberg-agent-fachabteilung_k.md` (Chat 49)

**Aufwand:** Mehrere Sessions. Pilot-Agent: Charakter (aktueller Fokus). Rollout danach auf die anderen drei.

---

## Epic: Client-Dashboard (GTK4 / PyGObject)

**Motivation:** Debugging, Kalibrierung und Einregelung des Dual-Emotion-Systems (Chat 53) erfordern visuelles Echtzeit-Feedback. Log-Grep ist kein Werkzeug für die Feinabstimmung von 8-dimensionalen Emotionsvektoren. Ohne Dashboard ist die Dual-Emotion-Architektur Blindflug.

**Architektur:** GTK4 Desktop-App (PyGObject) als Parent-Fenster mit Child-Panel-Fenstern. Emojis nativ (System-Fonts). FastAPI liefert Daten über REST (statisch) und WebSocket (Live-Streams). Kein Qt, kein Browser, kein Electron.

**Technologie-Entscheidung (Chat 55):** PySide6/Qt verworfen nach Emoji-Rendering-Bug (Qt-Chromium findet System-Emoji-Fonts nicht auf Linux). GTK4 ist das native GNOME/Fedora-Toolkit — vorinstalliert, keine Dependencies, Emojis nativ validiert.

**Panels (12 Typen, Chat 55 designed):**

| Panel | Kategorie | Datenquelle | Status |
|-------|-----------|-------------|--------|
| Emotionen (Aktuell) | on_demand | `GET /gedaechtnis/emotionen/{user_id}` | ✅ Chat 56 |
| Emotionen (Turns) | turn_reactive | SSE answer-Event (emotions_vektor) | ⬜ |
| Session-Turns | on_demand | `GET /session/kontext/{user_id}` | ✅ Chat 56 |
| KZG | on_demand | `GET /gedaechtnis/kzg/{user_id}` | ✅ Chat 56 |
| LZG | on_demand | `GET /gedaechtnis/lzg/{user_id}` | ✅ Chat 56 |
| Charakter | on_demand | `GET /gedaechtnis/hash/{user_id}` | ✅ Chat 56 |
| Fakten | on_demand | `GET /fakten/{user_id}` | ⬜ |
| System | on_demand | `GET /health` | ✅ Chat 56 |
| Pixie-Monitor | on_demand | `GET /debug/pixie/status` (neu) | ⬜ |
| PostgreSQL | query | `POST /debug/query/postgres` (neu) | ⬜ |
| Redis | query | `POST /debug/query/redis` (neu) | ⬜ |
| Docker-Logs | log_stream | `WS /debug/logs` (neu) | ⬜ |

**Voraussetzung für:** Dual-Emotion-Architektur (Chat 53), Antrieb/Gravitation (Chat 53), TR6 (_farbe_charakter). Ohne visuelles Feedback können die Schwellwerte nicht empirisch kalibriert werden.

**Löst:** CLIENT-RENDER (Backlog), Log-Debugging-Workflow

**Status Chat 56:** Phase 1 weitgehend abgeschlossen — Chat (WebKitGTK + SSE + WebSocket), Panel-Infrastruktur (PanelBase, ChildWindow, Registry, UNIQUE-Enforcement), 6 Panels funktional (System, Emotionen mit Radar, KZG, LZG, Session, Charakter). Offen: Fakten, Pixie-Monitor, PostgreSQL-Query, Redis-Query, Docker-Logs, Emotionen (Turns).

**Status Chat 62:** Perspektive-Selector eingebaut — `GespraechsPerspektive`-Dataclass + `PERSPEKTIVEN`-Liste als Single Source. Dropdown im Hauptfenster: "Meister — Gespraech mit Nova" / "Nova — Gespraech mit Meister". Alle sechs aktiven Panels auf `_get_api_params()` umgestellt, sodass sie die aktuelle Perspektive konsumieren statt hartkodierter User-IDs. Emotionen-Panel zeigt Dual-Emotion je Perspektive — verschiedene Radare fuer Meister und Nova. Die Dataclass-Liste ist erweiterbar fuer weitere User/Charakter-Paare (`james`, `tarzan`, weitere User).

---

## Epic: Dual-Emotion (Chats 53, 57–58)

**Vision:** Nova hat einen eigenen Emotionsstrang mit denselben 8 Plutchik-Dimensionen wie der User. Jede Antwort wird analysiert — Emotion, Arousal, Modus, Intent. Die Daten fließen unter `ASSISTANT_USER_ID` ins Gedächtnis und werden im nächsten Turn geladen.

**Leitprinzip:** "Der Eingangspfad für den User ist der Ausgangspfad für Nova."

**Drei Phasen:**

| Phase | Ziel | Status |
|-------|------|--------|
| Phase 1 | User-IDs entkoppeln — frei wählbar aus Config | ✅ Chat 57 |
| Phase 2 | Zweiter Emotionsstrang + Enricher-Split + Graph-Neuordnung | 🔧 AP1–3+7 ✅, AP4+8 teilw., AP5+6+9 offen |
| Phase 3 | Ziel-Vektor (Antrieb) als dritte Kraft auf Novas Emotion | ⬜ |

**Konzept-Dokumente:** `novaberg-thinking-drive_k.md` §4 (Chat 53), `novaberg-ei-dual-emotion_k.md` (Chat 58)

**Arbeitspakete Phase 2:**

| AP | Paket | Status |
|----|-------|--------|
| 1 | EI-Extraktion (Enricher → ei/berechnung.py) | ✅ Chat 58 |
| 2 | EI-Calc-Node (graph/nodes/ei_calc.py) | ✅ Chat 59 |
| 3 | Nova-Emotion Berechnung (Decay + Empathie) | ✅ Chat 59 |
| 4 | Perzeption(Nova) + EI-Calc(Nova) im async-Block | ✅ Chat 60 — Event-Modell ersetzt den async-Pfad |
| 5 | Router(Nova) + Commitment-Erkennung | ✅ Chat 60 — Router im CharacterGraph |
| 6 | Salienz(Nova) — eigener Salienz-Prompt | ✅ Chat 60 — Salienz im CharacterGraph |
| 7 | Asynchroner Block orchestrieren | ✅ Chat 60 — Event-Consumer ersetzt async-Block |
| 8 | API + Client (GespraechAntwort + Dual-Radar) | 🔧 API ✅, Client-Panels offen |
| 9 | Dokumentation | 🔧 Konzeptdokument + 12 Node-Dokumente aktualisiert |

**Chat 61 Nachtrag:**
- Perzeption(Nova) läuft nun symmetrisch nach Nova's finaler Antwort (analog zu Perzeption(User) in Pfad 1). Siehe Roadmap Chat 61.
- EI-Calc hat einen sauberen Rollen-Split bekommen (`ei_calc_rolle: "user" | "character"`). Trennung von User- und Nova-Emotion-Berechnung ist damit architektonisch abgeschlossen.

---

## Epic: Emotionale Gravitation (Chat 61)

**Vision:** Gespeicherte emotional aufgeladene Erinnerungen wirken als Attraktoren auf Novas aktuellen Emotionsstrom. Still, passiv, bis ein thematisch verwandtes Gespräch sie reaktiviert.

**Konzept:** `novaberg-thinking-drive_k.md` Kapitel 5.7 — drei Zeithorizonte (Session/KZG/LZG), Formel `gravitation = similarity × gewicht × zeit_dekay × quellen_faktor`.

**Mechanik:** Bei jedem Turn in Pfad 2 (Nova-EI-Calc):
1. Embedding des aktuellen Themas berechnen (liegt bereits vor)
2. Top-K Einträge aus Session + KZG + LZG mit Emotion-Aufladung retrieven
3. Ähnlichkeits-basierte Gravitations-Berechnung je Eintrag
4. Einträge über Schwelle (EMOTIONALE_GRAVITATIONS_SCHWELLE) fügen ihren Emotions-Vektor zu Novas Vektor hinzu
5. Hard-Cap auf EMOTIONALE_GRAVITATION_MAX_PRO_TURN (default 2) um keine Gefühls-Explosion auszulösen

**Config-Parameter (neu):**
- `EMOTIONALE_GRAVITATIONS_SCHWELLE: float = 0.5`
- `EMOTIONALE_GRAVITATION_ZEIT_HALBWERT: int = 180` (Tage)
- `EMOTIONALE_GRAVITATION_MAX_PRO_TURN: int = 2`
- `EMOTIONALE_GRAVITATION_FAKTOR_SESSION: float = 1.0`
- `EMOTIONALE_GRAVITATION_FAKTOR_KZG: float = 0.8`
- `EMOTIONALE_GRAVITATION_FAKTOR_LZG: float = 0.5`

**Wissenschaftliche Basis:** Bower (1981) Mood-Congruent Memory, Collins & Loftus (1975) Spreading Activation, Tulving (1983) Episodic Memory.

**Status:** Konzeptionell vollständig. Code-Implementation offen.

**Priorität:** Mittel — schön zu haben, erhöht emotionale Tiefe deutlich, aber nicht blockierend.

---

## Epic: Client urllib3-Retry-Fix (Chat 61)

**Problem:** Wenn der Server lange braucht (z.B. 55 Sekunden bei GPU-Druck), sendet urllib3 (unter requests) automatisch einen Retry. Der Server bekommt den Prompt zweimal, schreibt zwei identische User-Turns in die Session. Symptom wurde in Chat 61 beobachtet.

**Fix:** In `client/ui/stream_handler.py` HTTPAdapter mit `max_retries=0` konfigurieren, damit keine automatischen Retries stattfinden. Timeouts auf Client-Ebene explizit behandeln.

**Priorität:** Niedrig-Mittel — tritt nur bei langsamen Server-Responses auf. Mit schneller GPU und normaler Session-Größe kein Problem. Verhindert aber Daten-Inkonsistenzen bei Edge-Cases.

---

## Epic: Session-Limit für Responder-Prompt (Chat 61)

**Problem:** Der Responder-Node packt aktuell alle Session-Turns (seit Session-Beginn) in den System-Prompt. Bei 18+ Turns mit reichhaltigen Emotions-Metadaten wird der Kontext schnell groß (~7000-14000 Tokens für einen Turn). In Kombination mit KZG + Charakter-Hash + Regeln kann das Gemma4's Kontext-Fenster (32768) deutlich beanspruchen.

**Fix:** Session-Fenster einziehen — z.B. nur die letzten 12 Turns in den Prompt packen. Die älteren Turns bleiben in Redis für Nova's Gedächtnis, fließen aber nicht mehr in den aktuellen LLM-Call.

**Zu beachten:** 
- KZG-Verdichtung und Charakter-Hash ersetzen bereits den älteren Kontext konzeptionell
- Der Cut-off sollte aber die aktuelle Gesprächs-Episode vollständig enthalten (Session-Cluster-Grenzen beachten, nicht mitten in einem thematischen Block abschneiden)

**Priorität:** Mittel — performance- und kontextrelevant. Wird dringender, je längere Gespräche geführt werden.

---

## Epic: Graph-Neuordnung (Chat 58–59) — ✅ Chat 59

**Beschluss:** Enricher vor Router verschieben. Der Router sieht dadurch die volle Session, KZG, LZG, Charakter-Hash und EI-Ergebnisse — statt nur 5 Turns aus eigenem Redis-Read.

**Neuer synchroner Graph (implementiert Chat 59):**
```
Perzeption → Enricher(laden) → EI-Calc → Router → [Planner → Agent] →
GV-Node → Responder → Thinker → Tribunal → [Corrector]
```

**Löst:** ROUTE-MISS1 (strukturell — Router erkennt "Ja, bitte!" nach "Soll ich einen Termin anlegen?"). Offen für Validierung.

**Status:** ✅ Implementiert in Chat 59 zusammen mit Dual-Emotion AP2. Conditional Edge `_after_enricher` → `_after_router`. Salienz und Dispatcher zugleich aus dem sync-Graph entfernt (siehe Dual-Emotion AP7).

---

## Epic: Session-Trennung (User × Charakter) (Chat 54, 59)

**Vision:** Jede Gesprächskombination (User × Charakter) bekommt eine eigene Session-Partition. `session:meister:nova`, `session:meister:james`, `session:meister:tarzan`.

**Motivation:** Aktuell landen alle Charakter-Daten in `session:meister`. Multi-Character ist nicht trennbar. Durch die Turn-Annotation (Chat 59) ist das Problem sichtbarer geworden: Novas Emotionen landen in Meisters Session, unabhängig vom Charakter.

**Betroffene Stellen (Chat 54):**
1. Session-Keys in Redis (`session:{user_id}` → `session:{user_id}:{character_id}`)
2. `ASSISTANT_USER_ID` in config.py (hartkodiert → parametrisiert pro Turn)
3. `ASSISTANT_NAME` in config.py (Konstante → pro Turn aus Character-Definition)
4. Pending Agents in Redis (Character-Dimension nötig)

**Zusätzlich betroffen (Chat 59):**
5. `session_assistant_turn_annotate()` — annotiert in User-Session, muss Character-aware sein
6. Enricher — lädt Session-Turns, KZG, LZG, Hash pro Character
7. Nachbearbeitung — Nova-Pfad muss Character-ID durchreichen

**Priorität:** Direkt nach Dual-Emotion Phase 2. Wird für Debugging, Tests mit eigenen Charakteren und Multi-Character-Betrieb gebraucht.

**Status:** ✅ Implementiert in Chat 60. 23 Dateien, 56 Stellen. Session-Key `session:{user_id}:{character_id}:turns`.

---

## Vision: TurnOrchestrator (Chat 58)

**Idee:** Den linearen Graph durch einen sternförmigen Orchestrator ersetzen. Ein TurnOrchestrator entscheidet regelbasiert, welcher Node als nächstes läuft ("Waren wir schon bei Perception? Nein? Dann Perception."). Der asynchrone Nova-Pfad wäre dann kein Sonderfall, sondern eine weitere Sequenz in derselben State-Machine.

**Vorteil:** Flexiblere Pfade, weniger Conditional Edges, Nova-Pfad als natürlicher Teil statt Sonderlogik.

**Status:** Diskutiert, als Zukunfts-Epic festgehalten. Großer Umbau — berührt human_graph.py, alle Conditional Edges, Node-Wrapper-Factory, Builder. Nicht Teil von Phase 2.

**Update Chat 60:** Das Event-Modell löst das TurnOrchestrator-Problem auf eine andere Art — statt eines sternförmigen Orchestrators gibt es zwei separate Graphen, verbunden durch eine Event-Queue. Der TurnOrchestrator als separates Epic ist damit konzeptionell überholt.

---

## Epic: Client WebSocket-Umbau (Chat 60)

**Vision:** Der GTK4-Client empfängt Charakter-Antworten per WebSocket (`typ: "character_response"`) statt aus dem SSE-"answer"-Event. Der SSE-Stream zeigt nur noch die Pfad-1-Stages.

**Motivation:** chat.py ist fire-and-forget (Chat 60). Die Antwort kommt vom Event-Consumer per WebSocket. Der Client muss den neuen Message-Typ rendern.

**Betroffene Stellen:**
1. `client/ui/chat_view.py` (oder äquivalent) — WebSocket-Handler für `character_response`
2. SSE-Handler — kein `answer`-Event mehr, nur `processing`
3. Nachrichten-Rendering — Antworten asynchron anzeigen

**Status:** Offen. Server-Seite fertig (Chat 60).

---

## Epic: Chat 62 — Folgearbeiten aus dem Paar-Schema

Vier Arbeitspakete, die durch die KZG/LZG-Umstellung auf das Paar-Schema und durch beobachtete Gespraechsverlaeufe sichtbar wurden. Zwei Bugs, ein Bug-Risiko, ein Feature.

### KZG-DEDUP — Deduplizierung semantisch aehnlicher Eintraege (Feature, mittel)

Bei semantisch aehnlichen Turns erzeugt die Salienz mehrere KZG-Eintraege statt zu verstaerken, weil der Themen-Vergleich leicht unterschiedliche Tags extrahiert ("Name Lumi" vs. "Namensgebung Lumi" vs. "neuer Mitbewohner"). In Chat 62 beobachtet: Ein Gespraech ueber Lumi erzeugte 8 Eintraege statt 1–2. Der Cosine-Schwellwert (0.85) greift erst ab einer bestimmten Formulierungs-Naehe, der Themen-Tag-Match davor nicht.

**Loesungsansatz:** Zweite Deduplizierungs-Stufe vor dem Schreiben — Embedding-Aehnlichkeit gegen die letzten N Eintraege der Paar-Partition pruefen, bei Treffer Verstaerkung statt Neuanlage. Priorisierung nach Herkunft (assistant vs. user) und Salienz; nur der wichtigste Eintrag ueberlebt.

**Prio:** Mittel — reduziert KZG-Rauschen, verbessert Promotion-Qualitaet.

### CHAR-HASH-FILTER — beobachter-Filter bei Hash-Destillation (Bug-Risiko, niedrig)

Durch das Paar-Schema fliessen jetzt auch `beobachter="assistant"`-Eintraege in die Charakter-Hash-Destillation ein — `agents/charakter/agent.py` und `charakter_hash.py` lesen ueber das Prefix `kzg:{user_id}:*`, ohne nach Beobachter zu filtern. Novas eigene Beobachtungen sollten nicht Meisters adaptives Profil formen.

**Loesungsansatz:** `beobachter="user"`-Filter bei der Hash-Destillation fuer den User-Hash; spiegelsymmetrisch `beobachter="assistant"` fuer den Nova-Hash.

**Prio:** Niedrig — bisher keine beobachtete Profil-Verzerrung, aber strukturell riskant bei laengeren Paar-Historien.

### KZG-KERN-BLIND — Verstaerkung ignoriert neuen Kern-Inhalt (Bug, mittel)

Bei KZG-Verstaerkung wird der Zaehler erhoeht und Scores/Emotionen aktualisiert, aber der inhaltliche `inhalt`/Kern bleibt auf dem Text des ersten Turns. Folge-Turns, die den Moment erst bedeutsam machen (z.B. der Name "Lumi" nach mehreren Turns ueber die neue Pflanze), gehen inhaltlich verloren. Der Promotion-Call liest dann den ersten, oft weniger pointierten Kern — und ins LZG wandert die fruehe Form statt der reifen.

**Loesungsansatz:** Kern-Neudestillation bei Verstaerkung — LLM-Call mit altem Kern + neuem Turn als Input, neuer Kern als Output. Kostet einen zusaetzlichen CPU-LLM-Call pro Verstaerkung; begrenzbar auf Schwellwert (z.B. nur ab `haeufigkeit >= 2`).

**Prio:** Mittel — bricht die Promotion-Qualitaet bei Themen, die sich ueber mehrere Turns entwickeln.

### ROUTE-CHAR-NOTIZ — CharacterGraph-Router dispatched Konversation an NotizenAgent (Bug, niedrig)

Der Router im CharacterGraph erkennt Konversation faelschlich als Notizen-Task ("Lumi Geschlecht" → NotizenAgent-Dispatch → Fehler). Der Classify im NotizenAgent rejected korrekt mit "kein Notiz-Auftrag", aber der Umweg kostet einen LLM-Call und erzeugt eine Fehlermeldung im Gespraechsvektor. Verwandt mit ROUTE-MISS1 (dort False Negative, hier False Positive).

**Loesungsansatz:** Router-Prompt haerten — kurze Zwei-Wort-Phrasen ohne Verb und ohne Objekt-Marker nicht als Notiz-Auftrag klassifizieren. Alternativ: Router bekommt die letzten Turns als Kontext und pruefend ob das Thema gerade im Gespraech ist.

**Prio:** Niedrig — kosmetisch und Performance, kein Datenverlust.

---

## Epic: KZG-Liberalisierung + LZG-Destillation (Chat 63)

**Vision:** Speichern ist günstig, Vergessen ist intelligent. Die KZG-Eintrittsschwelle wird gesenkt, die Deduplizierung im KZG aufgeweicht, und die Intelligenz wird an den LZG-Übergang delegiert — wo thematisch verwandte KZG-Einträge zu einer Synthese destilliert werden.

**Leitprinzip:** Im KZG bleiben präzise Einzelaussagen. Im LZG verschwimmen Details zu einer Essenz — wie beim Menschen, der sich nach Wochen nicht mehr an den exakten Wortlaut erinnert, aber an die Kernaussage.

### Änderung 1 — Salienz-Schwelle senken

Aktuell: `< 0.5` wird ignoriert, `0.5–0.7` KZG kurz (TTL 7 Tage), `≥ 0.7` KZG lang (TTL 30 Tage).

Neu: `< 0.3` wird ignoriert, `0.3–0.5` KZG kurz (TTL 7 Tage), `0.5–0.7` KZG mittel (TTL 14 Tage), `≥ 0.7` KZG lang (TTL 30 Tage) + Promotion-Queue.

**Begründung:** Der Bereich 0.3–0.5 enthält informative Aussagen ("Ich mag Schnittlauch"), die heute komplett verloren gehen. Wenn sie nicht innerhalb von 7 Tagen verstärkt werden, verschwinden sie — dann waren sie nicht wichtig. Wenn doch, steigen sie auf.

**Betroffene Dateien:** `config.py` (Schwellwerte), `graph/nodes/salience.py` (Bereichsgrenzen), `agents/kzg/speicher.py` (TTL-Zuweisung).

### Änderung 2 — KZG-Deduplizierung aufweichen

Aktuell: Cosine-Schwellwert 0.85 + Themen-Tag-Match → bei Treffer Verstärkung statt Neuanlage.

Neu: Im KZG keine aggressive Deduplizierung mehr. Einzelaussagen als separate Einträge behalten. Verstärkung nur bei sehr hoher Ähnlichkeit (≥ 0.95) oder exaktem Themen-Match.

**Begründung:** Das KZG bildet die nahe Vergangenheit ab. Hier zählt Präzision — "Schnittlauch ist toll!" und "Minze ist toll!" sind zwei verschiedene Aussagen mit unterschiedlichem Informationsgehalt. Beide sollen abrufbar sein. Die Zusammenführung passiert erst beim LZG-Übergang.

**Zusammenspiel mit KZG-DEDUP (Chat 62):** Der Bug KZG-DEDUP (8 Einträge statt 1 bei einem Gespräch über Lumi) wird damit neu gerahmt. Die 8 Einträge waren kein Bug — sie waren verschiedene Facetten desselben Themas. Die Lösung liegt nicht in aggressiverer KZG-Deduplizierung, sondern in intelligenter LZG-Destillation.

### Änderung 3 — LZG-Destillation bei Promotion

Aktuell: Einzelne KZG-Einträge werden 1:1 ins LZG promoviert (Pixie Promotion Call 2).

Neu: Bei der Promotion sammelt Pixie alle thematisch verwandten KZG-Einträge der Paar-Partition ein (Embedding-Ähnlichkeit ≥ 0.75 zum Promotion-Kandidaten), destilliert sie in einem LLM-Call zu einer großen Zusammenfassung und schreibt diese als einen LZG-Eintrag.

**Beispiel:**

- KZG-Eintrag 1: "Schnittlauch ist toll!"
- KZG-Eintrag 2: "Minze ist toll!"
- KZG-Eintrag 3: "Hat frische Kräuter für den Balkon gekauft"
- → LZG-Destillat: "Mag frische Kräuter, besonders Schnittlauch und Minze. Hat Kräuter für den Balkon."

**Mechanik:**

1. Promotion-Trigger wie bisher (TTL 30 Tage, `gedaechtnistyp=lang`, Verstärkung)
2. Vor dem Schreiben: Embedding-Suche im KZG nach verwandten Einträgen (gleiche Paar-Partition, Cosine ≥ 0.75)
3. LLM-Call (CPU-Modell): "Fasse folgende Beobachtungen zu einer Gesamtaussage zusammen: [alle Kerne]"
4. Ein LZG-Eintrag mit dem Destillat, Themen-Union aus allen Quell-Einträgen
5. Quell-KZG-Einträge werden als `promoviert` markiert (kein erneutes Triggern)

**Betroffene Dateien:** `agents/pixie/promotion.py` (Destillations-Logik), `agents/kzg/aehnlichkeit.py` (Cluster-Suche), neuer Prompt in `prompts/default/pixie.promotion_destillation.txt`.

**Priorität:** Mittel-Hoch — verbessert LZG-Qualität deutlich, löst KZG-DEDUP konzeptionell.

---

## Epic: Embedding-Gravitationsgraph — Turn-Dashboard (Chat 63)

**Vision:** Ein visuelles Dashboard, das den letzten Turn als Embedding-Graphen zeigt. Novas Interessen, Ziele und Neugier-Punkte sind Gravitationszentren im 2D-Raum. Der User-Input und Novas Gesprächsvektor-Schritte wandern als Punkte durch diesen Raum. Kantenlängen zeigen Embedding-Distanz. Je näher ein Thema an einem Gravitationspunkt liegt, desto heißer wird es — sichtbar durch Farbverlauf von Grün (weit weg) nach Rot (nah, hohe Gravitation).

**Leitprinzip:** "Ich will sehen, wie der Turn ins Gedächtnis von Nova passt, wo wir thematisch sind."

### Elemente im Graphen

**Gravitationszentren (statisch pro Session):**

- Novas Interessen (aus Charakter-Hash `interessen_profil`)
- Novas Ziele (aus `thinking-drive` / Ziel-Embeddings)
- Novas Neugier-Themen (aus KZG/LZG mit hoher Resonanz)
- Jedes Zentrum hat ein sichtbares **Gravitationsfeld** — einen radialen Farbverlauf um den Kern:
  - Äußerer Rand ("Ereignishorizont"): Grün, halbtransparent. Markiert die Embedding-Distanz, ab der Gravitation beginnt zu wirken (= `EMOTIONALE_GRAVITATIONS_SCHWELLE`)
  - Übergangszone: Grün → Gelb → Orange, zunehmende Opazität
  - Kernzone: Rot, intensiv. Hier ist die Gravitation maximal — ein Thema, das hier landet, beeinflusst Novas Themenwahl und Emotion stark
- Kreisgröße des Kerns proportional zur Resonanz/Motivation
- Der Farbverlauf macht sichtbar: Wenn ein Turn-Punkt (User oder Nova) den Ereignishorizont berührt, beginnt die Verfärbung. Je tiefer er eintaucht, desto stärker der Gravitationseinfluss auf Themenwahl und Emotionsstrom
- Bei Themen OHNE Gravitationseinfluss (weit weg von allen Zentren): keine Verfärbung, neutraler Raum

**Turn-Punkte (dynamisch pro Turn):**

- User-Aussage: Embedding des User-Inputs
- Nova-Aussage: Embedding der Nova-Antwort
- GV-Schritte: 0 bis 2–3 Zwischenschritte des Gesprächsvektors, sichtbar als Pfad

**Verbindungen:**

- Kanten zwischen Turn-Punkten und Gravitationszentren
- Kantenlänge = Embedding-Distanz (kurz = nah = heiß)
- Pfeil von User-Aussage über GV-Schritte zu Nova-Aussage zeigt den Gesprächsvektor

### Geladenes Gedächtnis als Orientierungspunkte

Das Entscheidende: Der Graph muss zeigen, was der Enricher für diesen Turn geladen hat. Die geladenen KZG- und LZG-Einträge sind die thematische Nachbarschaft — sie erklären, warum Nova so reagiert wie sie reagiert. Ohne sie fehlt dem Graphen der Kontext.

**Session-Turns (letzte N):**

- Kleine Punkte entlang eines Pfades, der den bisherigen Gesprächsverlauf zeigt
- Zeigen, wo das Gespräch herkommt — der Weg zum aktuellen Turn
- Visuell dezent (kleiner als Turn-Punkte, kein Plutchik-Stern, einfache Kreise)

**KZG-Einträge (vom Enricher geladen):**

- Mittlere Punkte mit Themen-Label
- Diese sind die nahen Erinnerungen — kurze Embedding-Vektoren, die der Enricher für relevant befunden hat
- Farblich abgesetzt (z.B. halbtransparent), um sie von den aktiven Turn-Punkten zu unterscheiden
- Ihre Position im Embedding-Raum zeigt, WARUM der Turn in die Nähe bestimmter Gravitationszentren fällt

**LZG-Einträge (vom Enricher geladen):**

- Wie KZG, aber visuell anders markiert (z.B. gestrichelter Rand)
- Langzeiterinnerungen sind destillierter, breiter — ihre Position zeigt die tiefere thematische Verankerung

**Neugier, Ziele, Interessen aus dem State:**

- Alles, was im ConversationState steht und als Orientierung dient, muss im Graphen sichtbar sein
- Die Gravitationszentren sind nicht abstrakt — sie werden aus den konkreten Daten im State befüllt: `interessen_profil`, `ziele`, `neugier_themen`
- Nur so kann man die Position von User- und Charakter-Aussagen einordnen: relativ zu dem, was Nova gerade "weiß" und "will"

**Prinzip:** Der Graph bildet das Gesamtbild eines Turns ab — nicht nur was gesagt wurde, sondern was geladen wurde, was in der Nähe liegt, und in welchem Gravitationsfeld das alles stattfindet. Jeder Punkt im Graphen hat eine Bedeutung als Orientierung, wo wir uns thematisch befinden.

### Emotions-Visualisierung: Plutchik-Mikrosterne

Jeder Turn-Punkt (User-Aussage, GV-Schritte, Nova-Aussage) wird nicht als einfacher Kreis dargestellt, sondern als kleiner 8-zackiger Plutchik-Stern. Die 8 Achsen entsprechen den 8 Plutchik-Dimensionen (Freude, Vertrauen, Angst, Überraschung, Trauer, Ekel, Wut, Antizipation). Die Achsenlänge zeigt die Intensität der jeweiligen Emotion.

**Effekt:** Man sieht auf einen Blick:

- User-Stern zeigt z.B. dominante Freude (eine Zacke lang)
- Nova Schritt 1: Stern kippt zu Neugier (andere Zacke wächst)
- Nova Schritt 2: Stern kippt zu Vertrauen
- Die Sterne wandern durch den Gravitationsraum UND verändern dabei ihre Form

**Größe:** Nicht zu klein (Emotionen müssen lesbar sein), nicht zu massiv (Gravitationsraum muss dominieren). Ca. 40–60px Durchmesser im Rendering.

### Technische Überlegungen

**2D-Projektion:** UMAP oder t-SNE auf die hochdimensionalen Embeddings. Pro Turn neu berechnen (nur die Turn-Punkte ändern sich, Gravitationszentren bleiben stabil innerhalb einer Session).

**Rendering:** Cairo-Canvas im GTK4-Client oder WebKit-Widget. Live-Update nach jedem Turn.

**Datenquellen:**

- Embedding des User-Inputs: liegt nach Perzeption vor
- Embedding der Nova-Antwort: liegt nach Perzeption(Nova) vor
- GV-Schritte: aus `gv_vektor` im State (0–3 Schritte mit Themen)
- Emotionen: aus `ei_calc` (User) und `nova_emotions_vektor` (Nova)
- Gravitationszentren: Charakter-Hash-Profile + Ziel-Embeddings (zu cachen)
- Geladene KZG-Einträge: aus `kzg_eintraege` im State (vom Enricher befüllt)
- Geladene LZG-Einträge: aus `lzg_eintraege` im State (vom Enricher befüllt)
- Session-Turns: aus `session_turns` im State (letzte N Turns mit Embeddings)
- Neugier/Ziele/Interessen: aus Charakter-Hash-Feldern im State + KZG/LZG-Einträge mit hoher Resonanz als Neugier-Gravitationszentren

**Offene Fragen:**

1. UMAP-Stabilität: Ändert sich die 2D-Projektion der Gravitationszentren bei jedem Turn, verliert man die räumliche Orientierung. Lösung: Gravitationszentren einmal projizieren und fixieren, nur Turn-Punkte relativ einbetten.
2. Performance: UMAP auf ~30–50 Embeddings pro Turn (Gravitationszentren + Turn-Punkte + geladene KZG/LZG + Session-Turns) sollte <200ms sein. Zu verifizieren.
3. Skalierung: Bei vielen Gravitationszentren (>15) wird der Graph unübersichtlich. Top-K nach Relevanz filtern?
4. Überlappende Gravitationsfelder: Wenn zwei Zentren nahe beieinander liegen, überlappen ihre Ereignishorizonte. Rendering: additive Blending (überlappende Zonen werden intensiver) oder dominanter-Attraktor-Regel (stärkstes Feld gewinnt)?
5. Ereignishorizont-Radius: Direkt aus `EMOTIONALE_GRAVITATIONS_SCHWELLE` ableiten — der Radius im 2D-Raum entspricht der Cosine-Distanz, ab der Gravitation greift. Muss nach der UMAP-Projektion kalibriert werden.

**Priorität:** Niedrig-Mittel — Forschungs-Dashboard, kein produktionskritisches Feature. Aber enormer Wert für das Verständnis und die Kalibrierung von Gravitation, Gesprächsvektor und Dual-Emotion.

**Voraussetzungen:** Emotionale Gravitation (Epic Backlog) sollte zumindest konzeptionell stehen, damit die Gravitationszentren echte Daten haben. GV-Node sollte Schritte als separate Embeddings liefern.

---

## 8. Offene Bugs

Vollständige Bug-Dokumentation → `novaberg-bugs.md`

Kurzübersicht aktiver Bugs:

| Bug | Prio | Kurzbeschreibung |
|-----|------|-----------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| ROUTE-MISS1 | ⬜ | Router erkennt kontextabhängige Aufträge nicht (strukturell adressiert durch Enricher-vor-Router, Chat 59, offen für Validierung) |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| CRUD-DESTILL-SUBTRAKT | ⚠️ | Subtraktive Änderungen als Anweisung gespeichert |
| CRUD-REACTIVATE-STAMP | ⚠️ | Reactivate setzt deaktiviert_am nicht auf NULL |
| EMOTE-LOCK | ⬜ | Emote-Inflation bei langem Charakter-Register |
| TOPOS-LOCK | ⬜ | Bildervorrat wird mechanisch zykeliert |
| urllib3-RETRY | ⬜ | Client-urllib3 macht automatischen Retry bei langer Response, erzeugt Doppel-Turns |
| PATH1-LATENZ | ⬜ | Pfad-1 kann bei GPU-Druck auf 55+ Sekunden gehen (Einmal-Event beobachtet) |
| KZG-KERN-BLIND | ⬜ | KZG-Verstaerkung aktualisiert Scores, aber nicht den Kern (Chat 62) |
| ROUTE-CHAR-NOTIZ | ⬜ | CharacterGraph-Router dispatched Konversation an NotizenAgent (Chat 62) |
| ENRICHER-DUP | 👁 | Fakten werden mehrfach in den Enricher-Kontext injiziert (Chat 62, Beobachtung) |

Details, Ursachen und Lösungsansätze → `novaberg-bugs.md`

---

*Aktualisiert Chat 61: Perzeption-Symmetrie ✅, EI-Calc Rollen-Split ✅, Akkumulations-Refactor mit Historien-Gewicht + sin^0.5-Glättung ✅, perzeption_assistant Client-Label ✅. Konzeptionell: Emotionale Gravitation (Kapitel 5.7 in thinking-drive), Paper-Portfolio (novaberg-papers.md mit 29 Titeln, 9 angereichert). Neue Epics: Emotionale Gravitation implementieren, Client urllib3-Retry-Fix, Session-Limit für Responder-Prompt. Neue Bugs: urllib3-RETRY, PATH1-LATENZ.*

*Aktualisiert Chat 63: Zwei neue Epics — KZG-Liberalisierung + LZG-Destillation (Schwelle senken, Deduplizierung aufweichen, Destillation bei Promotion), Embedding-Gravitationsgraph (Turn-Dashboard mit Plutchik-Mikrosternen, geladenem Gedächtnis als Orientierungspunkte).*
