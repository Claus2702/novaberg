# Novaberg — Backlog (Zukunftskonzepte)

**Projekt:** Novaberg — The Nova Anima Resonance System
**Dokument:** Backlog — Konzipierte, noch nicht implementierte Features
**Stand:** 01. Mai 2026, Chat 72
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

**Implementierungsstand nach Chat 64:**

Der Mechanismus ist seit Chat 64 über die Cluster-Promotion implementiert:

- ✅ Widerspruch-Erkennung: LLM-Kohärenzprüfung in `_cluster_update_kohaerenz()` erkennt `widerspruch: true`
- ✅ Decay bei Widerspruch: `gewicht /= CLUSTER_WIDERSPRUCH_DECAY_FAKTOR` (3.0)
- ✅ Neuer Eintrag: INSERT mit korrigierter Information nach Decay

**Was noch fehlt — der Echtzeit-Trigger:**

Die Cluster-Promotion arbeitet periodisch (alle 5 Minuten). Epic 8 MR braucht einen Echtzeit-Trigger:

1. Enricher markiert abgerufene LZG-Einträge im State (z.B. `abgerufene_lzg_ids`)
2. Salienz erkennt Widerspruch zu einem abgerufenen Eintrag
3. Sofortige LZG-Korrektur im Dispatcher (nicht erst beim nächsten Pixie-Scan)

Der Echtzeit-Trigger könnte `_cluster_update_kohaerenz()` aus dem PromotionAgent wiederverwenden — die Mechanik ist identisch, nur der Auslöser unterscheidet sich.

**Priorität:** Mittel — der periodische Pfad deckt 90% der Fälle ab. Der Echtzeit-Trigger verbessert die Reaktionszeit bei offensichtlichen Korrekturen ("Anna wohnt jetzt in München" direkt nach LZG-Abruf "Anna wohnt in Nürnberg").

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
7. MR: Echtzeit-Trigger in Enricher/Salienz (Mechanismus via Cluster-Promotion bereits implementiert, Chat 64)
8. Traum-Modus: Neuer Pixie-Task 'traeumen'
9. Themen-Erkennung: Pixie-Task fuer automatische Cluster-Erkennung
```

Schritte 1-5 sind unabhaengig implementierbar. Schritte 6-9 bauen auf dem Themen-Modell (1-2) auf.

### 1.10 Bereits implementiert (Referenz)

| Effekt | Quelle | Nova-Implementierung | Dokument |
|--------|--------|---------------------|----------|
| Ebbinghaus-Vergessenskurve | Ebbinghaus 1885 | Exponentieller Decay, konfigurierbare Rate | novaberg-pixie-decay.md |
| Spacing Effect | Distributed Practice | KZG thematische Verstärkung (Salienz-Boost + TTL-Auffrischung, Chat 64) | novaberg-mem-kzg.md |
| Emotionale Salienz | Plutchik 1980, Russell 1980 | Arousal (0.0-1.0), 9 Emotions-Vektoren | novaberg-node-perception.md |
| Default Mode Network | Raichle et al. 2001 | Pixie als Hintergrundprozess | novaberg-pixie.md |
| Konsolidierung | McGaugh 1966, Dudai 2004 | KZG→LZG Promotion: Einzelpromotion (Zwei-Call) + Cluster-Promotion (4-Phasen, Chat 64) | novaberg-pixie-promotion.md |
| Memory Reconsolidation (teilw. aktiv) | Nader et al. 2000 | Cluster-Promotion: Widerspruch-Erkennung + Decay + Neueintrag (Chat 64). Echtzeit-Trigger noch offen. | novaberg-pixie-promotion.md, novaberg-mem-knowledge-graph.md |

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
| GV3 | Invertierte Perzeption (Ziel → benötigter Modus) — Dreischicht-Prompt-Integration | ✅ Chat 72 |
| GV4 | Wissens-Lücken via Embedding-Nachbarschaft | 🔧 Chat 71 (Kern: LZG + KZG) |
| GV4b | Agenten als Wissensquellen (Timeline, Notizen, Fakten, Dateien) | ⬜ Epic unten |
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

### Charakter-Hash: Fehlende Zeitstempel (Chat 71)

Die Tabelle `charakter_hash` hat nur `kern_aktualisiert_am` und `adaptive_aktualisiert_am`.
Drei Profile haben keinen eigenen Zeitstempel — man kann nicht sehen wann sie
zuletzt destilliert wurden:

| Profil | Spalte existiert | Zeitstempel |
|--------|:---:|:---:|
| kern_hash | ✅ | kern_aktualisiert_am |
| adaptive_hash | ✅ | adaptive_aktualisiert_am |
| beziehungsprofil | ❌ | fehlt |
| intentions_profil | ❌ | fehlt |
| emotions_profil | ❌ | fehlt |

Fix:

1. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beziehung_aktualisiert_am TIMESTAMPTZ;
2. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS intentionen_aktualisiert_am TIMESTAMPTZ;
3. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS emotionen_aktualisiert_am TIMESTAMPTZ;
4. CharakterAgent: Beim Schreiben den jeweiligen Zeitstempel setzen
5. Charakter-Panel: Alle 5 Zeitstempel anzeigen

Priorität: Niedrig — aber wichtig für Debugging (Chat 71 hat gezeigt dass ein
veraltetes Beziehungsprofil die gesamte Antwortqualität ruiniert).

---

### Charakter-Hash schema-konform um `beobachter` erweitern (Chat 71)

Konzept: `novaberg-paar-schema_k.md`. Heute mischt der Hash-Eintrag
`(nova, meister)` zwei Sichten — Nova-aus-User-Sicht (Beobachter `user`) und
Nova-aus-Selbstsicht (Beobachter `assistant`) — in einem Datensatz. Dadurch
überschreibt jede Destillation die jeweils andere Sicht.

Fix:

1. ALTER TABLE charakter_hash ADD COLUMN IF NOT EXISTS beobachter TEXT NOT NULL DEFAULT 'user';
2. Primärschlüssel umstellen: `(user_id, character_id)` → `(user_id, character_id, beobachter)`.
3. CharakterAgent-Loop erweitern: Statt zwei Paaren jetzt vier Tripel — `(meister, nova, user)`, `(meister, nova, assistant)`, `(nova, meister, user)`, `(nova, meister, assistant)`.
4. Destillations-Funktionen filtern KZG/LZG zusätzlich nach `beobachter`.
5. Enricher entscheidet per Kontext, welchen Hash er liest.
6. Cluster-Promotion-Guard für Nova ([promotion/agent.py:575-577](novaberg/server/agents/promotion/agent.py#L575-L577)) entschärfen, sobald genug Nova-KZG-Material da ist (sonst läuft die Promotion auf 0 Einträgen).

Priorität: Mittel. Erst sinnvoll, wenn der Sofort-Fix aus Chat 71
(`nova_gedaechtnis.py`) ein paar Tage Material gesammelt hat. Vorher fehlt
die Datengrundlage für die Beobachter-Trennung.

---

### Altdaten-Migration: `kzg:nova:nova:*` → `kzg:nova:meister:*` (Chat 71)

Konzept: `novaberg-paar-schema_k.md`, Abschnitt 4.2. In Redis liegen aktuell
19 KZG-Einträge unter `kzg:nova:nova:*` aus der Zeit vor dem Chat-71-Fix.
Sie werden vom CharakterAgent zufällig mitgelesen (Wildcard `kzg:nova:*`),
gehören aber semantisch unter `kzg:nova:meister:*` mit `beobachter=assistant`.

Fix:

1. Tool-Skript schreiben (analog `tools/migrate_kzg_keys.py`): Iteriere alle Keys mit Pattern `kzg:nova:nova:*`.
2. Pro Eintrag den Redis-Hash auslesen, mit `beobachter=assistant` neuen Key `kzg:nova:meister:{id}` schreiben, alte TTL übernehmen, alten Key löschen.
3. Anschließend `hash_dirty:nova:meister` setzen, damit der CharakterAgent das migrierte Material direkt einliest.
4. Sicherheitscheck: Vor der Migration zählen, nach der Migration zählen, in einem Log dokumentieren.

Priorität: Niedrig. Solange der Sofort-Fix neue Einträge sauber unter
`kzg:nova:meister:*` ablegt, schadet das Altmaterial nicht — es führt nur
zu einer leichten Mischung in der Destillation. Wenn die Beobachter-
Erweiterung (siehe oben) kommt, müssen die Altdaten ohnehin migriert werden.

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
| Ziele & Antrieb | turn_reactive | `GET /drive/goals` | ✅ Chat 69 |
| Gravitationsgraph | turn_reactive | `GET /drive/gravity_map` | ✅ Chat 69 |

**Voraussetzung für:** Dual-Emotion-Architektur (Chat 53), Antrieb/Gravitation (Chat 53), TR6 (_farbe_charakter). Ohne visuelles Feedback können die Schwellwerte nicht empirisch kalibriert werden.

**Löst:** CLIENT-RENDER (Backlog), Log-Debugging-Workflow

**Status Chat 56:** Phase 1 weitgehend abgeschlossen — Chat (WebKitGTK + SSE + WebSocket), Panel-Infrastruktur (PanelBase, ChildWindow, Registry, UNIQUE-Enforcement), 6 Panels funktional (System, Emotionen mit Radar, KZG, LZG, Session, Charakter). Offen: Fakten, Pixie-Monitor, PostgreSQL-Query, Redis-Query, Docker-Logs, Emotionen (Turns).

**Status Chat 62:** Perspektive-Selector eingebaut — `GespraechsPerspektive`-Dataclass + `PERSPEKTIVEN`-Liste als Single Source. Dropdown im Hauptfenster: "Meister — Gespraech mit Nova" / "Nova — Gespraech mit Meister". Alle sechs aktiven Panels auf `_get_api_params()` umgestellt, sodass sie die aktuelle Perspektive konsumieren statt hartkodierter User-IDs. Emotionen-Panel zeigt Dual-Emotion je Perspektive — verschiedene Radare fuer Meister und Nova. Die Dataclass-Liste ist erweiterbar fuer weitere User/Charakter-Paare (`james`, `tarzan`, weitere User).

**Status Chat 69:** Zwei neue Panels: Ziele & Antrieb (GoalsPanel, turn_reactive, 3 Ebenen) + Gravitationsgraph (GravityMapPanel, turn_reactive, 900×650, Cairo Force-Directed). 8 von 14 Panels funktional. Embedding-Persistenz in der Pipeline. Themen-Pipeline geschlossen.

---

## Epic: Dual-Emotion (Chats 53, 57–58)

**Vision:** Nova hat einen eigenen Emotionsstrang mit denselben 8 Plutchik-Dimensionen wie der User. Jede Antwort wird analysiert — Emotion, Arousal, Modus, Intent. Die Daten fließen unter `ASSISTANT_USER_ID` ins Gedächtnis und werden im nächsten Turn geladen.

**Leitprinzip:** "Der Eingangspfad für den User ist der Ausgangspfad für Nova."

**Drei Phasen:**

| Phase | Ziel | Status |
|-------|------|--------|
| Phase 1 | User-IDs entkoppeln — frei wählbar aus Config | ✅ Chat 57 |
| Phase 2 | Zweiter Emotionsstrang + Enricher-Split + Graph-Neuordnung | 🔧 AP1–7 ✅, AP8 teilw. (Server ✅, Client offen), AP9 ✅ |
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
| 8 | API + Client (GespraechAntwort + Dual-Radar) | 🔧 API ✅, Responder [EIGENE_EMOTION] ✅, Client-Panels offen |
| 9 | Dokumentation | ✅ Chat 66 |

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

**Status Chat 68:** WS-SINGLE behoben. `ClientConnection`-Dataclass mit `client_id`/`character_id`-Filterung. User-Message-Broadcast (server-seitige Filterung, kein Client-Filter nötig). Desktop ↔ Telegram bidirektional getestet. 12 Dateien.

---

## Epic: Chat 62 — Folgearbeiten aus dem Paar-Schema

Vier Arbeitspakete, die durch die KZG/LZG-Umstellung auf das Paar-Schema und durch beobachtete Gespraechsverlaeufe sichtbar wurden. Zwei Bugs, ein Bug-Risiko, ein Feature.

### KZG-DEDUP — Deduplizierung semantisch aehnlicher Eintraege ✅ Gelöst Chat 64

Bei semantisch aehnlichen Turns erzeugt die Salienz mehrere KZG-Eintraege statt zu verstaerken, weil der Themen-Vergleich leicht unterschiedliche Tags extrahiert ("Name Lumi" vs. "Namensgebung Lumi" vs. "neuer Mitbewohner"). In Chat 62 beobachtet: Ein Gespraech ueber Lumi erzeugte 8 Eintraege statt 1–2.

**Auflösung Chat 64:** Re-framed als Feature im Rahmen der KZG-Liberalisierung. Verschiedene Facetten desselben Themas werden im KZG bewusst als eigenständige Einträge behalten — die Cluster-Promotion sammelt sie ein und destilliert sie zu einem kohärenten LZG-Eintrag.

### CHAR-HASH-FILTER — beobachter-Filter bei Hash-Destillation (Bug-Risiko, niedrig)

Durch das Paar-Schema fliessen jetzt auch `beobachter="assistant"`-Eintraege in die Charakter-Hash-Destillation ein — `agents/charakter/agent.py` und `charakter_hash.py` lesen ueber das Prefix `kzg:{user_id}:*`, ohne nach Beobachter zu filtern. Novas eigene Beobachtungen sollten nicht Meisters adaptives Profil formen.

**Loesungsansatz:** `beobachter="user"`-Filter bei der Hash-Destillation fuer den User-Hash; spiegelsymmetrisch `beobachter="assistant"` fuer den Nova-Hash.

**Prio:** Niedrig — bisher keine beobachtete Profil-Verzerrung, aber strukturell riskant bei laengeren Paar-Historien.

### KZG-KERN-BLIND — Verstaerkung ignoriert neuen Kern-Inhalt ✅ Gelöst Chat 64

Bei KZG-Verstaerkung wurde der Zaehler erhoeht und Scores/Emotionen aktualisiert, aber der inhaltliche `inhalt`/Kern blieb auf dem Text des ersten Turns. Folge-Turns, die den Moment erst bedeutsam machen (z.B. der Name "Lumi" nach mehreren Turns ueber die neue Pflanze), gingen inhaltlich verloren.

**Auflösung Chat 64:** Obsolet durch Architekturwechsel — keine Merge-Verstärkung mehr. Jeder KZG-Eintrag behält seinen originalen Kern. Die thematische Verstärkung boosted nur Metadaten (Salienz, Häufigkeit, TTL). Die Cluster-Promotion destilliert alle Kerne bei der Zusammenführung ins LZG.

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

## Epic: Retrieval-Gate — Kontextverifikation nach dem Enricher (Chat 67)

**Vision:** Der Enricher lädt alle verfügbaren Daten (Session, KZG, LZG, Knowledge Graph, Charakter-Hash). Heute fließt alles ungefiltert in den State — der Responder bekommt Roleplay-Fakten, Negationen, Duplikate, LZG-Response-Blobs und irrelevante Einträge. Das Retrieval-Gate ist ein Verifikationsschritt an der Verarbeitungsgrenze zwischen Laden und Konsumieren.

**Leitprinzip:** "Weniger Input > stärkerer Prompt." — Kein Prompt kompensiert verrauschten Kontext. Verifikation gehört an jede Trust Boundary im Datenfluss, nicht nur am Ausgang (Tribunal).

**Architekturmuster:** Verifikation an Verarbeitungsgrenzen. Dasselbe Prinzip wie das Tribunal (Ausgangsverifikation), angewandt auf den Eingang. Zwei-Stufen-Retrieval nach dem Re-Ranking-Muster: Stufe 1 (Enricher) lädt breit, Stufe 2 (Gate) filtert scharf.

**Position im Graph:**

Perzeption → Enricher → ▶ Retrieval-Gate ◀ → EI-Calc → Router → ...

Eigener Node zwischen Enricher und EI-Calc. Liest aus dem State, schreibt gefilterten Kontext zurück.

**Drei Filtermechanismen (alle deterministisch, kein LLM-Call):**

| Mechanismus | Methode | Adressiert |
|-------------|---------|-----------|
| Relevanz-Score | Cosine-Similarity jedes Eintrags gegen User-Prompt-Embedding. Unter Schwelle → entfernen. | Irrelevante Einträge, Roleplay-Fakten, veraltete Themen |
| Deduplizierung | Embedding-Ähnlichkeit zwischen den geladenen Einträgen selbst. Über Schwelle → den mit höherem Gewicht behalten. | ENRICHER-DUP, redundante Fakten |
| Top-K pro Quelle | Maximal N Einträge pro Quelle (KZG, LZG, Knowledge Graph). | Kontext-Dominanz durch eine einzelne Quelle, Token-Budget-Überschreitung |

**Erwartete Wirkung:**

- Sauberer `memory_context` für Responder → bessere Antwortqualität
- ENRICHER-DUP gelöst (strukturell, nicht per Prompt)
- Token-Budget im Responder-Prompt entlastet
- Indirekt: Thinker-Web-Suche weniger anfällig für `num_ctx`-Überlauf (weniger Basis-Kontext = mehr Raum für Web-Ergebnisse)

**Konfiguration (Config-Muster):**

- `RETRIEVAL_GATE_RELEVANZ_SCHWELLE` — Cosine-Similarity-Minimum gegen User-Prompt
- `RETRIEVAL_GATE_DEDUP_SCHWELLE` — Cosine-Similarity-Maximum zwischen Einträgen
- `RETRIEVAL_GATE_TOP_K_KZG` — Max Einträge aus KZG
- `RETRIEVAL_GATE_TOP_K_LZG` — Max Einträge aus LZG
- `RETRIEVAL_GATE_TOP_K_FAKTEN` — Max Einträge aus Knowledge Graph

**Laufzeit:** Sub-100ms, reine Embedding-Arithmetik + Sortierung. Kein GPU-Bedarf (Embeddings liegen bereits vor).

**Voraussetzung:** Die Embeddings der geladenen Einträge müssen im State verfügbar sein. KZG-Einträge haben Embeddings (Redis-Vektoren). LZG und Knowledge Graph müssten ihre Embeddings mittransportieren — zu prüfen.

**Priorität:** Mittel — adressiert Kontextqualität, ENRICHER-DUP und Token-Budget. Wird wichtiger mit wachsendem Gedächtnis.

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

## Epic: Matrix-Kanal + WireGuard-Zugang (Chat 68)

**Vision:** Nova als vollwertiger Chat-Partner über das Matrix-Protokoll, erreichbar von überall per WireGuard-VPN. Im Gegensatz zu Telegram kann Matrix über den Application-Service-Mechanismus *beide* Seiten steuern — User-Nachrichten und Bot-Nachrichten. Damit entfällt die `[Du]`-Krücke: Desktop-Eingaben erscheinen im Matrix-Client als echte User-Nachrichten, Novas Antworten als echte Nova-Nachrichten.

**Leitprinzip:** "Der Kanal ist dumm. Absichtlich." — Gilt weiterhin. Matrix ist ein dritter Renderer neben Desktop (GTK4) und Telegram. Markdown bleibt das kanonische Format.

**Architektur:**

1. **Matrix-Homeserver** — Synapse oder Dendrite, lokal auf der Novaberg-Maschine. Kein Cloud-Dienst, kein föderierter Zugang (optional später).
2. **Zwei Accounts** — `@meister:novaberg.local` (User) + `@nova:novaberg.local` (Charakter) in einem gemeinsamen Room.
3. **Application Service (AS)** — Novaberg registriert sich als AS beim Homeserver. Kann als beide Accounts schreiben. Empfängt Room-Events per Callback.
4. **Novaberg-Integration** — Analog zum Telegram-Bot: fire-and-forget POST /chat + WebSocket-Listener. Aber zusätzlich: User-Nachrichten von anderen Clients werden als `@meister` in den Room geschrieben (nicht als Bot-Nachricht).
5. **WireGuard-VPN** — Server auf der Novaberg-Maschine, Client auf dem Handy (e/OS, F-Droid). Kein offener Port, kein externer Server. Voller Zugriff auf lokales Netz (Matrix, REST-API, Panels, Docker).
6. **Matrix-Client** — Element oder FluffyChat auf e/OS (F-Droid). Verbindet sich über VPN-Tunnel auf den lokalen Homeserver.

**Vorteil gegenüber Telegram:**

| Aspekt | Telegram | Matrix |
|--------|----------|--------|
| User-Nachrichten einspeisen | ❌ Nur Bot-Messages | ✅ AS kann als beliebiger User schreiben |
| Datenhaltung | Telegram-Cloud | Lokal (Homeserver auf eigener Maschine) |
| Erreichbarkeit unterwegs | Internet (Telegram-API) | WireGuard-VPN (kein offener Port) |
| Client-Verfügbarkeit | Telegram-App | Element/FluffyChat (F-Droid) |
| Protokoll | Proprietär | Offen (Matrix-Spezifikation) |

**Bestandteile:**

| # | Arbeitspaket | Beschreibung |
|---|-------------|-------------|
| 1 | WireGuard-Server | Installation + Konfiguration auf der Novaberg-Maschine (Nobara/Fedora) |
| 2 | WireGuard-Client | Konfiguration auf e/OS Handy, Verbindungstest |
| 3 | Matrix-Homeserver | Synapse oder Dendrite als Docker-Service im Compose-Stack |
| 4 | Account-Setup | Zwei Accounts anlegen, Room erstellen, Berechtigungen |
| 5 | Application Service | AS-Registrierung, Event-Callback, Nachrichtensteuerung als beide User |
| 6 | Novaberg-Connector | `matrix_bot/bot.py` analog zu `telegram_bot/bot.py` — POST /chat + WebSocket-Listener + user_message-Einspeisung als `@meister` |
| 7 | Client-Test | Element auf e/OS über VPN, bidirektionaler Nachrichtentest |

**Priorität:** Niedrig — Telegram funktioniert, Matrix ist Kür. Aber architektonisch sauber und privacy-konform.

**Voraussetzung:** WS-SINGLE Fix (Chat 68, ✅), ClientConnection mit client_id/character_id-Filterung (Chat 68, ✅).

---

## Epic: GV4b — Agenten als Wissensquellen (Chat 71)

### Kontext

GV4 (Chat 71, Kern) durchsucht LZG und KZG nach Wissenslücken — semantisch nahe,
aber unbesprochene Konzepte. Die Relevanz wird über 6 Systeme berechnet: Gedächtnis,
Aktualität, Drive (Ziel-Gravitation), Neugier (6 EI-Säulen, sin^0.5), Register-
Kompatibilität und Charakter-Filter. Die Formel ist validiert (58-Testfälle-Matrix).

Was fehlt: Agenten-Domänen als Quellen. Timeline-Einträge, Notizen, Fakten und
autonome Wissens-Dateien enthalten Wissen, das Nova für Wissenslücken nutzen kann.
Die Agenten müssen sich selbst als Quelle anmelden und ihre eigenen Config-Werte
bereitstellen.

### Architektur: BaseAgent-Erweiterung

Neue Attribute in `server/agents/base.py` (`BaseAgent`):

| Attribut | Typ | Default | Beschreibung |
|----------|-----|---------|-------------|
| `neugier_quelle` | `bool` | `False` | Kann dieser Agent Wissenslücken liefern? |
| `neugier_config` | `dict` | `{}` | Agent-spezifische GV4-Parameter |

Neue Methode in `BaseAgent`:

```python
def neugier_suchen(
    self,
    turn_embedding: list[float],
    user_id: str,
    character_id: str,
    limit: int = 10,
) -> list[dict]:
    """Durchsucht die Domäne nach Wissenslücken.

    Returns: [{konzept, similarity, gewicht, gap_arousal, quelle, quellen_faktor}]
    """
    return []
```

Jeder Agent implementiert `neugier_suchen()` mit seiner eigenen DB-Query
(pgvector, RediSearch, Textsuche) und liefert Kandidaten mit seinem eigenen
`quellen_faktor` aus `neugier_config`.

### Agent-Registrierung (Opt-in)

| Agent | `neugier_quelle` | `quellen_faktor` | `gap_arousal_base` | Voraussetzung |
|-------|:-:|:-:|:-:|---|
| TimelineAgent | `True` | 0.7 | 0.3 | **Embedding-Nachrüstung** (s.u.) |
| NotizenAgent | `True` | 0.5 | 0.2 | **Embedding-Nachrüstung** (s.u.) |
| FaktenAgent | `True` | 0.6 | 0.3 | Fakten-Tabelle hat bereits `embedding VECTOR(768)` — sofort möglich |
| DateienAgent | `True` | 0.5 | 0.2 | `autonomous_wissen`-Tabelle (Phase 3, Pixie-Infrastruktur) |
| CharakterAgent | `False` | — | — | Keine Wissensdomäne |
| DelegationsAgent | `False` | — | — | Keine Wissensdomäne |
| RechercheAgent | `False` | — | — | Produziert Wissen, liefert es nicht |
| PromotionAgent | `False` | — | — | Infrastruktur, keine Domäne |
| DecayAgent | `False` | — | — | Infrastruktur, keine Domäne |
| WiedervorlageAgent | `False` | — | — | Trigger, keine Domäne |
| KZG-Agent | `False` | — | — | KZG ist Kern-Quelle, kein Agent-Opt-in |

### Embedding-Nachrüstung (Voraussetzung)

Zwei Tabellen haben aktuell **kein** `embedding`-Feld:

**1. Timeline:**

```sql
ALTER TABLE timeline ADD COLUMN IF NOT EXISTS embedding VECTOR(768);
CREATE INDEX IF NOT EXISTS idx_timeline_embedding
    ON timeline USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
```

- TimelineAgent muss bei `create`, `update`, `reschedule` das Embedding aus
  `title + ' ' + COALESCE(details, '')` erzeugen.
- Einmalige Migration: Alle bestehenden Einträge embedden
  (`embedding_create(title + details, embed_client, EMBED_MODEL)`).
- `neugier_suchen()` Query: pgvector `ORDER BY embedding <=> %s LIMIT 10`
  mit Zeitfenster-Filter `WHERE event_time >= NOW() AND event_time <= NOW() + INTERVAL '{zeitfenster_h} hours'`
  (aus `neugier_config["zeitfenster_h"]`, Default 72).

**2. Notizen:**

```sql
ALTER TABLE notizen ADD COLUMN IF NOT EXISTS embedding VECTOR(768);
CREATE INDEX IF NOT EXISTS idx_notizen_embedding
    ON notizen USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
```

- NotizenAgent muss bei `create`, `update` das Embedding aus
  `titel + ' ' + COALESCE(inhalt, '')` erzeugen.
- Einmalige Migration analog zu Timeline.
- `neugier_suchen()` Query: pgvector `ORDER BY embedding <=> %s LIMIT 10`.

**3. Fakten:** Hat bereits `embedding VECTOR(768)` — kein ALTER TABLE nötig.
  FaktenAgent kann `neugier_suchen()` sofort implementieren.
  Die Entity-Hop-ILIKE-Suche im GV-Node bleibt parallel bestehen —
  sie findet Named Entities, die pgvector-Suche findet semantische Nachbarschaft.

**4. Dateien:** `autonomous_wissen`-Tabelle hat bereits `themen_embedding VECTOR(768)`
  im Konzept (`novaberg-autonomous-wissen_k.md`). Wird mit Phase 3 (Pixie-Infrastruktur)
  angelegt. DateienAgent implementiert `neugier_suchen()` sobald die Tabelle existiert.

### Integration in `_wissensluecken_finden()`

Nach den Kern-Quellen (LZG + KZG) iteriert der GV-Node über die Agent-Registry:

```python
from agents import AgentRegistry

for agent in AgentRegistry.get_all():
    if agent.neugier_quelle:
        agent_kandidaten = agent.neugier_suchen(
            turn_embedding, user_id, character_id
        )
        alle_kandidaten.extend(agent_kandidaten)
```

Die Relevanz-Berechnung liest den `quellen_faktor` aus dem Kandidaten-Dict
(statt aus der zentralen Config-Variable). Kern-Quellen (LZG, KZG) setzen
weiterhin den Default `GV_QUELLEN_FAKTOR`.

```python
# Statt:
basis = k["similarity"] * k["gewicht"] * GV_QUELLEN_FAKTOR
# Jetzt:
basis = k["similarity"] * k["gewicht"] * k.get("quellen_faktor", GV_QUELLEN_FAKTOR)
```

### Reihenfolge

| Schritt | Was | Abhängigkeit |
|---------|-----|-------------|
| 1 | `BaseAgent` um `neugier_quelle`, `neugier_config`, `neugier_suchen()` erweitern | — |
| 2 | `_wissensluecken_finden()` um Agent-Registry-Loop ergänzen | Schritt 1 |
| 3 | FaktenAgent: `neugier_suchen()` implementieren | Schritt 1 (sofort, Embedding existiert) |
| 4 | Timeline: Embedding nachrüsten (ALTER TABLE + Migration + Agent-Writes) | — |
| 5 | TimelineAgent: `neugier_suchen()` implementieren | Schritt 1 + 4 |
| 6 | Notizen: Embedding nachrüsten (ALTER TABLE + Migration + Agent-Writes) | — |
| 7 | NotizenAgent: `neugier_suchen()` implementieren | Schritt 1 + 6 |
| 8 | DateienAgent: `neugier_suchen()` implementieren | Phase 3 (autonomous_wissen) |

Schritte 1–3 könnten unmittelbar nach GV4-Kern-Validierung erfolgen.
Schritte 4–7 sind unabhängig voneinander und parallelisierbar.
Schritt 8 wartet auf die Pixie-Infrastruktur (Phase 3).

### Designprinzipien

> **"Jeder Agent kennt seine Domäne."** Der GV-Node fragt nicht die Timeline-Tabelle
> direkt ab — der TimelineAgent weiß, wie seine Daten liegen und welche Filter
> (Zeitfenster, aktiv-Flag) gelten. Das ist "Separation of Concerns über Nodes"
> konsequent auf Agenten-Ebene angewendet.

> **"Die Neugier gehört Nova, die Daten gehören dem Agenten."** Der GV-Node berechnet
> die Relevanz (Neugier, Register, Charakter). Der Agent liefert die Rohdaten
> (Kandidaten mit Similarity, Gewicht, Arousal). Keine Vermischung.

> **"Config beim Agenten, nicht in der Zentrale."** Jeder Agent bringt seinen eigenen
> `quellen_faktor` und `gap_arousal_base` mit. Das vermeidet eine zentrale
> Faktor-Tabelle, die bei jedem neuen Agenten wachsen müsste.

### Priorität

Mittel. Der GV4-Kern (LZG + KZG) deckt den Hauptanwendungsfall ab. Die
Agent-Quellen erweitern die Reichweite, sind aber nicht blockierend.
FaktenAgent als erste Agent-Quelle (Embedding existiert) ist Quick Win.

---

## Epic: Chat 72 — Folgearbeiten aus Dreischicht-Integration

### Reducer-Node — Gegenspieler zum Enricher (Hoch, Chat 71/72)

Der Reducer fasst ältere Session-Turns zusammen, statt alle 11+ Turns wörtlich an den Responder durchzureichen. Pendant zum Enricher: wo der Enricher anreichert, dünnt der Reducer aus.

**Motivation:** Echo-Bug (Chat 72) zeigt, dass Nova ab ~11 Turns die User-Nachricht wörtlich wiederholt. Vermutete Ursache: Kontext-Sättigung durch Session-Turns + KZG/LZG-Rauschen + Charakter-Hash + GV-Vorschlag. Konzipiert in Chat 71, durch Echo-Bug in Chat 72 priorisiert.

**Funktion:**

- Ältere Turns (>N) destillieren statt durchreichen
- Pro Responder-Call ein fokussiertes Konzentrat aus dem State bauen, statt vollen `memory_context`
- Reduktionsstufen je nach Turn-Alter (jüngste vollständig, mittlere zusammengefasst, alte als Themen-Tag)

**Architektur-Anschluss:** Reducer läuft im CharacterGraph zwischen Enricher und Responder. Konsumiert Session + KZG/LZG-Treffer und schreibt `responder_context` in den State. Auch GV-Vorschlag und Charakter-Hash gehen durch den Reducer, damit der Responder ein konsistentes Konzentrat bekommt.

**Priorität:** Hoch — direkt blockierender Bug bei langen Sessions.

---

### GV-Panel: Dreischicht-Felder visualisieren (Hoch, Chat 72)

`gv_detail` enthält seit Chat 72 die volle Entscheidungskette: Achsen, Sektor, Cluster, Repertoire, Charakter-Gewichtung, Sprünge, Absicht, Strategie, Vehikel. Das GV-Panel soll diese Felder detailliert anzeigen — die komplette Entscheidungskette von EI-State bis Antwort-Strategie sichtbar machen.

**Was zu sehen sein soll:**

- 6 Achsen (Werte + Visualisierung)
- Aktiver Sektor (1 von 64) mit Cluster-Zuordnung (1 von 13)
- Repertoire (Strategien × Absichten × Vehikel) mit Charakter-Gewichtung
- Gewählte Absicht / Strategie / Vehikel als Endergebnis
- Sprünge zwischen Sektoren über die letzten Turns

**Priorität:** Hoch — ohne Sichtbarkeit ist die neue Architektur nicht debugbar oder kalibrierbar.

---

### Modus-Kalibrierung: spielerisch vs. emotional (Niedrig, Chat 72)

Perzeption klassifiziert 😍-Katzen-Chat als `gespraechs_modus="emotional"` statt `"spielerisch"`. Folge: Tiefe-Achse 0.70 statt 0.40, was die Sektor-Berechnung in der Dreischicht verschiebt.

**Lösungsansatz:** Modus-Beispiele im Perzeption-LLM-Call schärfen. Spielerisch (Tier-Niedlichkeit, Quatschen, leichte Themen) klar von emotional (Beziehungsthemen, Sorgen, Tiefe) abgrenzen.

**Priorität:** Niedrig — kosmetische Verschiebung der Sektor-Verteilung, keine Funktion gebrochen.

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
| ROUTE-CHAR-NOTIZ | ✅ (beobachten) | CharacterGraph-Router dispatched Konversation an NotizenAgent (Chat 62) |
| ENRICHER-DUP | 👁 | Fakten werden mehrfach in den Enricher-Kontext injiziert (Chat 62, Beobachtung) |
| RESP-DEAD | ⬜ | Tote Standardphrase statt Nova-Ton bei fehlgeschlagenen Agent-Dispatches |
| PIXIE-GHOST | ⬜ | Pixie-Delivery fließt nicht durch EI/Session/Router — Nova hört sich selbst nicht |

Details, Ursachen und Lösungsansätze → `novaberg-bugs.md`

---

*Aktualisiert Chat 61: Perzeption-Symmetrie ✅, EI-Calc Rollen-Split ✅, Akkumulations-Refactor mit Historien-Gewicht + sin^0.5-Glättung ✅, perzeption_assistant Client-Label ✅. Konzeptionell: Emotionale Gravitation (Kapitel 5.7 in thinking-drive), Paper-Portfolio (novaberg-papers.md mit 29 Titeln, 9 angereichert). Neue Epics: Emotionale Gravitation implementieren, Client urllib3-Retry-Fix, Session-Limit für Responder-Prompt. Neue Bugs: urllib3-RETRY, PATH1-LATENZ.*

*Aktualisiert Chat 63: Zwei neue Epics — KZG-Liberalisierung + LZG-Destillation (Schwelle senken, Deduplizierung aufweichen, Destillation bei Promotion), Embedding-Gravitationsgraph (Turn-Dashboard mit Plutchik-Mikrosternen, geladenem Gedächtnis als Orientierungspunkte).*

*Aktualisiert Chat 68: WS-SINGLE behoben (ClientConnection-Dataclass, broadcast()/broadcast_threadsafe() mit character_id/exclude_client). User-Message-Broadcast: Desktop ↔ Telegram bidirektional sichtbar (server-seitige Filterung). 12 Dateien.*

*Aktualisiert Chat 69: Goals-Panel ✅ + Gravitationsgraph-Panel ✅ (2 neue Panels). Embedding-Persistenz in Session-Turns. Themen-Pipeline (`prompt_thema` → Dispatcher → Session) geschlossen. `thema`-Spalte in `ziele`-Tabelle. GRAVITATIONS_SCHWELLE kalibriert (0.3 → 0.75). Dashboard-Epic: 8/14 Panels.*

*Aktualisiert Chat 72: GV3 (Dreischicht-Prompt-Integration) ✅ — implementiert in Chat 72. GV-Panel Redis-Persistierung ✅ (war bei Chat-72-Start bereits erledigt). Drei neue Folgearbeiten: Reducer-Node (Hoch, gegen Echo-Bug bei langen Sessions), GV-Panel Dreischicht-Felder visualisieren (Hoch, Sichtbarkeit der neuen Architektur), Modus-Kalibrierung spielerisch vs. emotional (Niedrig, Perzeption-Prompt).*

*Aktualisiert Chat 71: GV3 + GV4 in Implementierung (🔧). GV4b als neues Epic: Agenten als Wissensquellen mit BaseAgent-Erweiterung (neugier_quelle, neugier_config, neugier_suchen()). Embedding-Nachrüstung für Timeline + Notizen. FaktenAgent als Quick Win (Embedding existiert). 6-Systeme-Relevanzformel validiert (58-Testfälle-Matrix, sin^0.5 Neugier-Normalisierung, Register-Kompatibilität, Session-Decay).*
