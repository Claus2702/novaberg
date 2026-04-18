# Novaberg — Backlog (Zukunftskonzepte)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Backlog — Konzipierte, noch nicht implementierte Features
**Stand:** 18. April 2026, Chat 54
**Pfad:** novaberg/docs/nova-backlog.md
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
| Ebbinghaus-Vergessenskurve | Ebbinghaus 1885 | Exponentieller Decay, konfigurierbare Rate | nova-pixie-decay.md |
| Spacing Effect | Distributed Practice | KZG-Verstaerkung bei Wiederholung | nova-mem-kzg.md / nova-pixie-kzg.md |
| Emotionale Salienz | Plutchik 1980, Russell 1980 | Arousal (0.0-1.0), 9 Emotions-Vektoren | nova-node-perception.md |
| Default Mode Network | Raichle et al. 2001 | Pixie als Hintergrundprozess | nova-pixie.md |
| Konsolidierung | McGaugh 1966, Dudai 2004 | KZG→LZG Promotion (Zwei-Call) | nova-pixie-promotion.md |
| Memory Reconsolidation (passiv) | Nader et al. 2000 | Bi-temporales Modell | nova-mem-knowledge-graph.md |

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
Nova (lokal, Gemma 4): Sammelt Anforderungen, recherchiert Hue API
Nova: Reichert Spezifikation mit gesammeltem Wissen an
Nova → Claude API: "Generiere ein Python-Skript nach dieser Spec"
Claude API → Nova: Fertiger Code
Nova (lokal): Testet, registriert als Tool
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

Langfristige Vision: Agenten als MCP-Server (Model Context Protocol) in Docker-Containern, Nova als MCP-Client. Jeder Agent wird ein eigenstaendiger Service mit definierter Schnittstelle — unabhaengig deploybar, testbar und austauschbar. Das wuerde die Grenze zwischen lokalen Agenten und externen Diensten aufloesen: ein RechercheAgent koennte lokal oder als Remote-Service laufen, mit identischer Schnittstelle.

---

## 6. Voice (TTS/STT)

Der naechste Schritt in der Kommunikationsbandbreite: Spracheingabe (Speech-to-Text) und Sprachausgabe (Text-to-Speech). Voice wuerde die natuerlichste Form der Interaktion ermoeglichen — ein Gespraech statt Texteingabe. Voraussetzung: die emotionale Intelligenz muss in der Sprachausgabe ankommen (Tonlage, Tempo, Pausen entsprechend Arousal und Emotions-Vektor). Konzept steht noch aus.

---

## 7. Offene Epics & Features

### RESP-CHAR1 — Base-Charakter-Prompt ✅ Chat 45
nova_kern und nova_beziehung in [IDENTITAET] konsolidiert. [CHARAKTER]-Block entfernt. Destillation für user_id="nova" auf eigene Prompts umgestellt ("Nova ist..." statt "Der Nutzer ist..."). Nova-Charakter bleibt dünn bis Traum-Modus eigenes Material liefert.

### Prompt-Segregation (Chat 46-47, abgeschlossen)
| # | Thema | Status |
|---|-------|--------|
| SEG-1 | Infrastruktur (Loader, PROMPTS, Verzeichnisse) | ✅ Chat 46 |
| SEG-2 | JSON-Nodes (Perzeption, Router, Salienz, Tribunal) | ✅ Chat 46 |
| SEG-3 | Gemma4-Overrides (7 Dateien) | ✅ Chat 46 |
| SEG-4 | Responder + Thinker + Corrector + GV | ✅ Chat 47 |
| SEG-5 | KZG-Verdichtung + Classify-Nodes (4x) | ✅ Chat 47 |

### CLASSIFY-REJECTED — Selbstprüfung in Classify-Nodes ✅ Chat 48
action: "rejected" als neue gültige Aktion. Classify prüft ZUERST ob der Prompt überhaupt ein Auftrag ist (vs. Kompliment, Redewendung, rhetorische Bemerkung). Löste ROUTE-CHAR1 und den "Zeit fürs Bett"-Fall. Implementiert in 16 Dateien: 4 Task-Textdateien + 4 klassifikation.py + 4 agent.py + 4 dispatch.py. Dispatch gibt AgentResult mit status="rejected" zurück — der Responder ignoriert es automatisch, der Planner beendet seine Schleife.

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
| PIX-MIG-6 | VertiefungsAgent | ⚠️ Konzept (nova-pixie-deepdive_k.md) |
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
| CLIENT-RENDER | QWebEngineView Chat-Rendering | ⬜ Markdown + Emojis |
| Oktagon-Radar | Hexagon → 8 Sektoren | ⬜ Brudi-Prompt erstellt |
| Konfig-Panel | Schieberegler | ⬜ |
| Timeline/Schatten-Panel | — | ⬜ |

### Kommunikation
| # | Thema | Status |
|---|-------|--------|
| Überakkommodation | CAT empirisch testen | ⬜ |
| PENDING-RELEVANZ | Router prüft nicht ob Prompt Antwort auf Rückfrage | ⬜ Chat 43 |
| KORR1 | Korrektur-Erkennung bei fehlgeschlagenen Aktionen | ⬜ Chat 43 (niedrig) |
| CLASSIFY-CONFIRM | Classify erkennt Bestätigung/Erinnerung nicht als rejected | ✅ Chat 49 |
| ROUTE-MISS1 | Router erkennt Timeline-Update-Auftrag mit Kontext-Bezug nicht | ⬜ Chat 48 |
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

**Konzept-Dokument:** `nova-agent-fachabteilung_k.md` (Chat 49)

**Aufwand:** Mehrere Sessions. Pilot-Agent: Charakter (aktueller Fokus). Rollout danach auf die anderen drei.

---

## Epic: Client-Dashboard (PySide6 + QWebEngineView)

**Motivation:** Debugging, Kalibrierung und Einregelung des Dual-Emotion-Systems (Chat 53) erfordern visuelles Echtzeit-Feedback. Log-Grep ist kein Werkzeug für die Feinabstimmung von 8-dimensionalen Emotionsvektoren. Ohne Dashboard ist die Dual-Emotion-Architektur Blindflug.

**Architektur:** PySide6 Desktop-Shell als Parent-Formular mit dockbaren Child-Panels. Jedes Panel rendert über QWebEngineView (Chromium) — Markdown, Emojis, Charts nativ. FastAPI liefert Daten über REST (statisch) und WebSocket (Live-Streams). Kein Browser, kein Electron.

**Panels (geplant):**

| Panel | Datenquelle | Zweck |
|-------|-------------|-------|
| Chat | Bestehende Chat-API | Markdown + Emoji korrekt gerendert (löst CLIENT-RENDER) |
| EI-Dashboard | `GespraechAntwort` pro Turn | 8 Plutchik-Dimensionen, Arousal, Vektor — visuell pro Turn |
| Session-Turns | Session-Daten aus Redis | Rohe Turn-Daten mit Annotationen, Emotion, Kern |
| Charakter-Viewer | `charakter_hash` + Anweisungen | Kern, Adaptiv, Beziehung, Emotions-Profil, Intentionen |
| Pixie-Monitor | Redis Pixie-Queue/Status | Aktuelle Tätigkeit, Queue, letzte Ergebnisse |
| Live-Logs | WebSocket, Python-Logging-Events | Filterbar nach Node/Level, kein docker-compose-logs mehr |

**Voraussetzung für:** Dual-Emotion-Architektur (Chat 53), Antrieb/Gravitation (Chat 53), TR6 (_farbe_charakter). Ohne visuelles Feedback können die Schwellwerte nicht empirisch kalibriert werden.

**Löst:** CLIENT-RENDER (Backlog), Log-Debugging-Workflow

**Aufwand:** Mehrere Sessions. Phase 1: Chat + Live-Logs + EI-Dashboard. Phase 2: Charakter + Pixie + Session-Turns.

---

## 8. Offene Bugs

| Bug | Status | Beschreibung |
|-----|--------|-------------|
| HALL2 | ⚠️ | KZG-Klebrigkeit — wiederholte Mitteilung bereits kommunizierter Inhalte |
| TAG-LEAK3 | ⬜ | `[emotionaler_ausdruck]` leckt in Antwort |
| FAK-LECK | ⬜ | Charakter-Anweisungen als User-Fakten extrahiert |
| BUTLER1 | ⬜ | Eigeninitiative und Pseudo-Angebote |
| SIEZ2 | ⬜ | Sie/Du-Inkonsistenz bei formeller Persona |
| LEAK3 | ⬜ | Salienz-Score leckt in Antwort |
| RECH2 | ⚠️ | 3/3 Iterationen "luecken", Max-Iter fängt ab |
| THER1 | ⚠️ | RLHF-Therapeut-Muster |
| PLANNER-WARN | ⬜ | Doppel-Read bei Resume (harmlos, WARNING → DEBUG) |
| OLLAMA-THINK | ⚠️ | Ollama #15260: `think=false` + `format="json"` = Format ignoriert (Gemma4). Workaround: kein format, Prompt+Cleanup. |
| ROUTE-MISS1 | ⬜ | Router erkennt "Kannst Du das mit in den Termin schreiben?" nicht als Timeline-Update |
| HALL2-Update | ✅ | ~~Halluzinierte Bestätigung + stiller Datenverlust~~ — Gefixt Chat 54 |
| SEARX1 | ⚠️ | SearXNG Engines timen aus, keine Web-Suche möglich |
| RESP-CRUD-GENERIC | ℹ️ | Möglicherweise entschärft durch task_block (Chat 54), weiter beobachten |
| EMOTE-LOCK | ⬜ | Emote-Inflation — Nova eröffnet fast jede Antwort mit `*kichere boshaft*` (register-abhängig) |
| TOPOS-LOCK | ⬜ | Nova zykelt mechanisch durch 8 Alters-Bilder statt auf User-Details einzugehen (register-abhängig) |
| RESUME-REJECT | ✅ | ~~Pflicht-Rückfrage führt Aktion trotz "Nein" aus~~ — Gefixt Chat 50 |
| HALL2-Reject | ✅ | ~~Responder halluziniert Bestätigung bei abgelehnten Agent-Aktionen~~ — Gefixt Chat 54 |
| CRUD-DESTILL-SUBTRAKT | ⚠️ | Subtraktive Änderungen ("Sei nicht mehr X") werden als Anweisung gespeichert statt in den Charakter integriert |
| CRUD-REACTIVATE-STAMP | ⚠️ | Reactivate setzt `deaktiviert_am` nicht auf NULL zurück (Invarianzverletzung) |
| CRUD-REACTIVATE-COEXIST | ℹ️ | Reactivate deaktiviert nicht den aktuellen Charakter — abgedeckt durch Fachabteilungs-Epic |
| CHAR-ID4-ORPHAN | ⬜ | Bi-temporale Invariante verletzt (ID 4: aktiv=f ohne deaktiviert_am) |
| TIMELINE-SEARCH1 | ⬜ | Timeline-Agent findet irrelevanten alten Termin, keine Disambiguierung |

Details → nova-bugs.md

---

*Aktualisiert Chat 54: HALL2-Update + HALL2-Reject gefixt, TIMELINE-SEARCH1 neu, RESP-CRUD-GENERIC möglicherweise entschärft.*
