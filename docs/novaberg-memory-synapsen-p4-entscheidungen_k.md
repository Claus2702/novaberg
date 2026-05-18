# Novaberg — Synapsen P4: Architektur-Entscheidungen

**Dokument:** Konzept-Notiz, K-Punkt-Festlegungen für Synapsen P4
**Status:** Aktiv (Chat 91, vor Implementation)
**Verwandt:** `novaberg-memory-synapsen_k.md` (Haupt-Konzept), `novaberg-pixie-promotion.md` (Live-Doku alter Pfad)

---

## 1. Kontext

Diese Notiz hält die Architektur-Entscheidungen fest, die in Chat 91 nach
Audit 1 (Code-Inventar des alten PromotionAgents) und Audit 2 (Mapping auf
das Synapsen-Schema) als zehn Klärungspunkte (K1–K10) entstanden sind. Die
Klärung erfolgte punkt-für-punkt im Reducer-Stil.

Die Notiz ist Anker für den späteren P4-Sprint und überbrückt die
Microservice-Modell-Queue-Welle, die als Voraussetzung vor P4 läuft.

---

## 2. Reihenfolge der Wellen

1. **Pre-P4-Fix** — `queues.py:72` Schwelle vereinheitlichen
2. **Microservice-Modell-Queue** — eigener Sprint mit Konzept, Audit,
   Implementation (Blocker für P4)
3. **Synapsen P4** — neuer Pixie-Agent `synapsen_promotion` auf dem
   Microservice-Layer
4. **Synapsen P5** — Enricher als Reader
5. **Synapsen P6** — Decay-Job
6. ... weitere Phasen gemäß `novaberg-memory-synapsen_k.md` §13

---

## 3. Die zehn K-Punkte mit Festlegungen

### K1 — Reifeprüfung

**Festlegung:** Salienz ≥ 0.7 für beide Pfade (`neu` und `verstaerkt`).
Keine LLM-Reifeprüfung im neuen Pixie-Agent. Keine Mindest-Alter-Bedingung.
Keine Magnet-Feld-Anwesenheits-Bedingung — dünn vernetzte Knoten werden
akzeptiert, Pipeline-Log liefert spätere Analyse-Möglichkeit.

**Pre-P4-Fix:** `queues.py:72` von `PROMOTION_THRESHOLD` (0.8) auf
`KZG_SALIENZ_HIGH` (0.7) umhängen. Asymmetrie 0.7/0.8 ist Restbefund der
unvollständigen Chat-64-Konsolidierung, nicht Designentscheidung.

### K2 — FaktenManager-Verbleib

**Festlegung:** Pfad D.2 — Tripel-Extraktion entfällt komplett in P4.
Kein Call 1, kein Call 2, kein FaktenManager-Aufruf im neuen Pixie-Agent.
Funktionalitäts-Bruch zwischen P4 und M2.5b wird akzeptiert (keine neuen
Tripel, keine Edge Invalidation, eingefrorener Fakten-Bestand).

Spätere Architektur: FaktenAgent als eigenständige Fachabteilung
(M2.5b), analog zu TimelineAgent. Router-getrieben mit Salienz-Fallback.

### K3 — Call 1 + Call 2 Verbleib

**Festlegung:** Beide entfallen vollständig in P4. Folge aus K2.

### K4 — Qualitätsfilter O5/O11/O12

**Festlegung:** Strukturell aufgelöst. O5 (Speaker-Auflösung) entfällt
ersatzlos — `inhalt` wandert unverändert, Speaker steht in `beobachter`.
O11 (Objekt-Entitäten) obsolet durch P3 (`magnete_aufloesen` mit
`EntityResolutionService.resolve_batch`). O12 (Tautologie) Tripel-spezifisch,
wandert später mit dem FaktenAgent mit.

### K5 — `hintergrund_log` vs. `pipeline_log`

**Festlegung:** Beide Tabellen bleiben, funktional verschieden:
- `hintergrund_log` = Pixies operatives Arbeitsgedächtnis
  (Deduplizierung, was wurde erledigt)
- `pipeline_log` = Novas Selbstreflexionsschicht
  (Span-Forensik, Metakognitions-Substrat)

Neuer Pixie-Agent schreibt in **beide**. EVA-Vorbedingungs-Fehler:
`hintergrund_log` mit `status='fehler'`, `pipeline_log` mit
`art='bemerkung'`. Erfolgreiche Promotionen analog mit kompletter Span.

**Architektur-Grundannahme:** Nova ist Pixie. Pixies Verarbeitung ist
Teil von Novas Pipeline.

### K6 — Prompt-Segregation

**Festlegung:** Obsolet in P4. Folge aus K3 — keine LLM-Calls, keine
Prompts auszulagern. Bleibt offen für M2.5b (FaktenAgent).

### K7 — Caller-Tags

**Festlegung:** P4 hat keine Caller-Tags, weil keine LLM-Calls.
Konvention für später (alle LLM-aufrufenden Agenten ab M2.5b):
`pipeline_log`-Span-Korrelation als alleinige Forensik-Quelle,
keine zusätzlichen Caller-Tags.

### K8 — Initiale `gewicht_roh`-Berechnung

**Festlegung:** `lzg_knoten.gewicht_roh = KZG-Eintrag.salienz` (direkte
Übernahme, keine Skalierung). Begründung: Salienz im KZG ist 0–10-Skala
(`KZG_SALIENZ_CAP = 10.0`, sin^0.6-gedämpft) — dieselbe Skala wie
`gewicht_roh` im LZG. Nahtlose Übernahme.

Anschluss-Felder:
- `gewicht_absolut = 10 × sin^0.5(min(gewicht_roh / 10, 1) × π/2)`
  (§5.4 Schritt 5)
- `gewicht_decay = gewicht_absolut` (initial identisch, divergiert mit
  P6 Decay-Job)

**Migration alter Daten (P9, §11.2):** `gewicht_roh = 2.0` als
neutraler Setz-Wert, weil Bestandsdaten ihre ursprüngliche Salienz
verloren haben.

### K9 — Embedding-Quelle

**Festlegung:** Re-Embed `inhalt` allein (Pfad B). Keine
Themen-Anreicherung. Begründung: Schicht-Orthogonalität wahren — Themen
gehen über die Themen-Schicht in die Kanten-Bildung ein, Embedding
über die Embedding-Schicht. Pfad C (`inhalt + themen`) würde die
Schicht-Trennung sabotieren.

Pre-Voraussetzung Microservice-Modell-Queue ist Blocker für P4 —
Re-Embed-Aufrufe laufen über die Queue, nicht direkt.

**Bekannter Schwachpunkt:** Entkernte KZG-Inhalte ("Der Nutzer
bestätigt das.") werden auch im LZG entkernt sein. Lösung außerhalb
P4-Scope: KZG-Verdichter-Prompt-Refinement plus späteres
Chronik-Konzept.

### K10 — Match-Mechanik und Counter-Trigger

**Festlegung:** Hybrid Magnet + Vector (Pfad B, Onyx-Analogon):

1. **Vor-Filter** über Magnet-Felder: Knoten desselben
   `user_id+character_id` mit mindestens einer Magnet-Übereinstimmung
   (geteilte `entitaet_ids`, `themen`-Overlap, oder Timeline-Distanz
   unter Toleranz). GIN-Index-Lookups, schnell.
2. **Vector-Reranking** über den Kandidaten-Pool: Cosine berechnen,
   höchsten Treffer auswählen.
3. **Schwellwert:** `LZG_KNOTEN_MATCH_SCHWELLE = 0.85`.

**Auf Match — Reinforcement-Pfad:**
- `gewicht_roh += LZG_KNOTEN_REINFORCEMENT_BOOST` (= 0.1)
- `gewicht_absolut` neu berechnen via Sinus-Dämpfung
- `haeufigkeit += 1`
- `verstaerkt_am = NOW()`
- Trigger 2: alle Kanten von/zu diesem Knoten neu berechnen

**Kein Match — Anlage-Pfad:**
- Neuer `lzg_knoten` mit `gewicht_roh = salienz`, `haeufigkeit = 1`
- Kanten gegen alle bestehenden Knoten berechnen (vier Schichten)

**Hinweis:** Aktivierung ist Schreibpfad-Logik (Konzept §7.1, §7.9.2,
§7.1 „Lesepfad löst keine Aktivierung aus"). Lesepfad bleibt passiv.

---

## 4. Neue Konstanten in `config.py`

```python
# Synapsen P4 — Match-Erkennung
LZG_KNOTEN_MATCH_SCHWELLE = 0.85  # Cosine-Schwelle für Knoten-Reinforcement

# Synapsen P4 — Reinforcement
LZG_KNOTEN_REINFORCEMENT_BOOST = 0.1  # Additiver Boost auf gewicht_roh

# Feature-Flag
SYNAPSEN_PROMOTION_AKTIV = False  # auf True nach Microservice-Welle + P4-Test
```

Plus die in §6 ohnehin vorgesehenen Schicht-Faktoren, Tiefe-Faktoren,
`LZG_PIPELINE_LOG_VORHALTUNG_TAGE = 365` etc. — sofern noch nicht in
`config.py`.

---

## 5. Neuer Pixie-Agent — Architektur-Eckpunkte

**Vermutliche Pfad-Lokation:** `novaberg/server/agents/synapsen_promotion/`
mit `agent.py` und `AGENT.md`. Endgültiger Pfad bei Sprint-Planung.

**Kein:**
- Kein LLM-Call (kein Call 1, kein Call 2, kein FaktenManager-Aufruf)
- Keine Cluster-Logik, keine Aggregation
- Keine Caller-Tags

**Ja:**
- KZG-Queue lesen wie heute (`redis_client.lpop`)
- EVA-Vorbedingungs-Checks (drei wie heute + ggf. neue für Schema-Härte)
- Match-Erkennung (Hybrid Magnet + Vector)
- Anlage- oder Reinforcement-Pfad
- Kanten-Berechnung (vier Schichten, Sinus-Geometrie)
- Schreibziele: `lzg_knoten`, `lzg_kanten`, `hintergrund_log`,
  `pipeline_log`
- Trigger 2 (Re-Cache) bei Reinforcement
- Embed-Aufruf über Microservice-Queue

**Stilllegung alter Pfad:** `PromotionAgent` (alt) bleibt im Repository
hinter `SYNAPSEN_PROMOTION_AKTIV=True`, vollständige Entfernung in P9.

---

## 6. Backlog-Einträge aus dieser Welle

Folgende Punkte aus den K-Klärungen sind nicht P4-Scope und gehören in
`novaberg-backlog.md`:

- **MICROSERVICE-MODELL-QUEUE** — Konzept und Implementation der
  FIFO-Queue für Modell-Aufrufe (Nomic, Gemma4, künftige Modelle).
  **Blocker für P4.** Microservice-Architektur, threadsafe,
  Vorbereitung auf sternförmigen Orchestrator-Graph.

- **KONZEPT-CHRONIK** — Vollständiges Turn-Log als episodisches
  Nachschlagewerk, dauerhaft, `turn_id`-indiziert. Eigenes Konzeptpapier
  nach P4-P9. Stichworte: episodisches Gedächtnis (Tulving), Lookup-
  Mechanismus für Knoten-Kontextualisierung. Bezugspunkte:
  `novaberg-mem-session.md` für Turn-Struktur, `turn_id`-Konvention aus
  Chat 88.

- **KZG-VERDICHTER-KONTEXT-VERLUST** — Verdichter produziert entkernte
  Einträge wie „Der Nutzer bestätigt das." Sollte gar nicht erst
  entstehen. Prompt-Refinement-Sprint. Verbunden mit Chronik:
  Verdichter-Fix reduziert das Problem, Chronik bietet
  Sicherheitsnetz.

- **KONFIG-PIXIE-AKTIV-HARDCODED** — `PIXIE_AKTIV = False` ist
  hartcodiert in `config.py:129`, alle anderen Pixie-Konstanten sind
  env-konfigurierbar. Anpassen für Pixie-Reaktivierung nach P4.

- **PROMO-QUEUE-SCHWELLE-ASYMMETRIE** — Durch Pre-P4-Fix erledigt;
  Doku-Drift in `novaberg-pixie-promotion.md` und
  `novaberg-pixie.md` (beide nennen noch 0.8) nachziehen.

- **DOKU-DRIFT-WELLE-PROMOTION** — Sammlung der sieben Drift-Punkte
  aus Audit 1: Methoden-Namen, Schwellen 0.75 vs. 0.85,
  Modell-Trennung Doku vs. Code, Prompt-Lokation, `hash_dirty`
  paar-spezifisch, O6 nur LLM-Prompt-Regel, Entitäts-Typ `tier`.
  Erfolgt in Welle nach P9 (alter Code wird ohnehin gelöscht).

---

## 7. Beifang-Punkte (im Backlog, nicht P4-blockierend)

- **`emotions_vektor`-Befüllung** — Spalte ist NOT NULL DEFAULT '', wird
  aber im KZG vom Salience-Node leer gelassen. Eigener
  Salience-Sprint später.

- **`kzg_erstellt_am` Parse-Härte** — neue Spalte NOT NULL, alter Code
  fing Parse-Fehler ab. Vorbedingungs-Check im neuen Agent.

- **`gedaechtnistyp` neu befüllt statt NULL** — Lese-Pfad muss in P5
  darauf vorbereitet sein.

- **Trigger 2 Re-Cache-Konzept-Lücke** — Was ist „echte Aktivierung"
  im 1:1-Umzug? Konzept-Klärung in eigener Welle, Trigger 2 ist
  faktisch P6+.

- **`fakten`-Tabelle-Konsistenz und Entity-Merge** — Explizit außerhalb
  P4-Scope, eigenes Faktengedächtnis-Konzept (Konzept §3.2).

- **Konzept §4.1 vs. `init.sql` FK-Drift bei `timeline_id`** —
  Funktional gleichwertig, Doku-Sync.

- **`magnete_aufloesen` ohne Audit-Trail** — Backlog
  REFAC-MAGNETE-AUDIT, separater Sprint.

---

## 8. Pfad zur Sprint-Planung

Nach Microservice-Welle:

1. **Audit-Refresh** — Code-Stand prüfen (es können bis dahin Wochen
   vergangen sein), Schema-Stand, Migrationsstand
2. **Sprint-Schneidung** — Welle-Phasen (Schema → Helfer → Schreibpfad
   → Kanten) oder Code-Pfade (Anlage → Reinforcement → Trigger-2).
   Tendenz: Welle-Phasen, weil robuster.
3. **Brudi-Sprints** — sequentiell, mit Audit-Vorbau pro Sprint nach
   Reducer-Vorbild
4. **Inbetriebnahme** — `SYNAPSEN_PROMOTION_AKTIV=True` schrittweise,
   Pipeline-Log-Beobachtung, dann Pixie-Reaktivierung

---

## 9. Verwandte Dokumente

- `novaberg-memory-synapsen_k.md` — Haupt-Konzept Synapsen-Modell
- `novaberg-pixie-promotion.md` — Live-Doku alter PromotionAgent
- `novaberg-mem-kzg.md` — KZG-Architektur, Salienz-Skala
- `novaberg-mem-lzg.md` — LZG-Architektur (alt)
- `novaberg-backlog.md` — Backlog, M2.5b FaktenAgent
- Audit 1 + Audit 2 Ausgaben (Chat 91)
